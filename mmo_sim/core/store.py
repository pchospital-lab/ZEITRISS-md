#!/usr/bin/env python3
"""
mmo_sim/core/store.py — neutraler, serialisierter Publikations-Store.

Extrahiert aus `internal/qa/harness/lobby/rooms.py` (P1, 1326 Zeilen). Enthaelt
die Lobby-/Tisch-/Leader-only-Send-/Completion-Idempotenz-Mechanik UNVERAENDERT
in ihrem Ablauf (Guards, `__plan`/`__final`-Journal, `run_id`-Bindung,
Current-Save-Versionierung).

Auflage A1 (PLAN-CRITIC.md, BLOCKER): dieser Kern kennt WEDER `TABLE_MAX_SIZE=5`
NOCH v7-/char-id-Validierung als Modulkonstanten oder harte Checks. Beides ist
hier als injiziertes Policy-Objekt modelliert (`TableSizePolicy`,
`HarvestValidator`) — die konkreten ZEITRISS-Instanzen liefert
`domain/zeitriss/policy.py`. Ein neutraler Dummyfall ohne Char-ID darf hier
NICHT an einer generischen Spielklassenpflicht scheitern (A27).

Auflage A2 (BLOCKER): kein `__file__`-relativer Schema-/Fixture-Pfad-Patch mehr
— Persona-State-Zugriff laeuft ausschliesslich ueber eine vom Aufrufer
uebergebene `PersonaStateStore`-Instanz (siehe `core/persona_state.py`), deren
Schema-Pfad explizit konfiguriert wurde.

Auflage A5: `complete_section` hat KEIN Default fuer `today` mehr — ein
implizites, stehengelassenes Testdatum darf nie unbemerkt greifen.
"""
from __future__ import annotations

import hashlib
import json
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from .persona_state import PersonaStateStore

# K1/K1-Nachzug: additives Current-Save-Ref-Feld im Persona-State — traegt EIN
# JSON-OBJEKT {"run_id": <str>, "seq": <int>} (nicht eine bare Sequenznummer):
# die Sequenznummer referenziert current_saves/<pk>__versions/<seq>.json, die
# run_id bindet diese Referenz zusaetzlich an den Speicherbereich (run_dir).
_CURRENT_SAVE_REF_FIELD = "current_save_version"

_SECTION_ID_RE = re.compile(r"^[A-Za-z0-9_-]+\Z")


# ── Policy-Protokolle (A1) — Domaene injiziert Implementierung ─────────────────


class TableSizePolicy(Protocol):
    min_size: int
    max_size: int

    def validate_size(self, size: int) -> bool: ...


class HarvestValidator(Protocol):
    """Domaenenregel fuer die Save-Ernte. `core/store.py` kennt weder "v7" noch
    "char_id" — nur diese zwei Methoden."""

    def validate_block(self, block: dict, expected_id: str) -> bool: ...

    def validate_identity(self, state: dict, persona_key: str, expected_id: str) -> bool: ...


def _safe_component(value: str) -> str:
    return value.replace("/", "_")


# ── Chrononaut-Locks: gemeinsamer, dateibasierter Speicher ──────────────────


def _locks_path(run_dir: str | Path) -> Path:
    return Path(run_dir) / "locks.json"


def _read_locks(run_dir: str | Path) -> dict:
    p = _locks_path(run_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _write_locks(run_dir: str | Path, data: dict) -> None:
    _locks_path(run_dir).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ── Speicherbereichs-Identitaet: stabile run_id pro run_dir ─────────────────


def _run_id_path(run_dir: str | Path) -> Path:
    return Path(run_dir) / "run_id.json"


def _run_id(run_dir: str | Path) -> str:
    run_dir = Path(run_dir)
    p = _run_id_path(run_dir)
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = None
        if isinstance(data, dict):
            rid = data.get("run_id")
            if isinstance(rid, str) and rid:
                return rid
    rid = uuid.uuid4().hex
    run_dir.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"run_id": rid}, ensure_ascii=False, indent=2), encoding="utf-8")
    return rid


# ── Gruppen-/Leader-Ableitung aus Offer-/Consent-Log ────────────────────────


@dataclass
class GroupDerivation:
    leader: str | None
    members: list[str]
    dissenters: dict[str, str]
    source_offer_id: str | None
    reason: str


def derive_group_and_leader(offer_log_events: list[dict]) -> GroupDerivation:
    offers: dict[str, dict] = {}
    order: list[str] = []
    dissenters: dict[str, str] = {}

    for ev in offer_log_events:
        if ev.get("type") == "offer":
            oid = ev["id"]
            offers[oid] = {
                "from": ev["from"],
                "wants": set(ev.get("wants") or []),
                "accepted": set(),
                "declined": set(),
            }
            order.append(oid)
        elif ev.get("type") == "consent":
            oid = ev.get("offer_id")
            if oid not in offers:
                continue
            frm = ev["from"]
            if ev.get("accept"):
                offers[oid]["accepted"].add(frm)
            else:
                offers[oid]["declined"].add(frm)
                dissenters[frm] = ev.get("reason", "(kein Grund angegeben)")

    for oid in order:
        o = offers[oid]
        complete = o["wants"].issubset(o["accepted"]) and o["declined"].isdisjoint(o["wants"])
        if complete:
            members = sorted({o["from"]} | o["wants"])
            return GroupDerivation(
                leader=o["from"], members=members, dissenters=dict(dissenters),
                source_offer_id=oid, reason=f"erste vollstaendig angenommene Offer '{oid}'",
            )

    return GroupDerivation(
        leader=None, members=[], dissenters=dict(dissenters),
        source_offer_id=None, reason="keine vollstaendig angenommene Offer im Log",
    )


class ChrononautLockedError(RuntimeError):
    pass


class TableSizeError(ValueError):
    pass


class LeaderOnlySendError(PermissionError):
    pass


class VisibilityError(PermissionError):
    pass


class TableClosedError(PermissionError):
    pass


class TablePendingError(TableClosedError):
    pass


# ── Lobby ────────────────────────────────────────────────────────────────────


class Lobby:
    """Persistente Lobby-Mitgliedschaft (JSON-Datei), kein Dauerprozess.

    `table_size_policy` (A1) bestimmt die zulaessige Tischgroesse — die Lobby
    selbst kennt keine Zahl."""

    def __init__(self, run_dir: str | Path, table_size_policy: TableSizePolicy):
        self.run_dir = Path(run_dir)
        self.table_size_policy = table_size_policy
        self.run_dir.mkdir(parents=True, exist_ok=True)
        (self.run_dir / "tables").mkdir(exist_ok=True)
        (self.run_dir / "completion").mkdir(exist_ok=True)
        (self.run_dir / "current_saves").mkdir(exist_ok=True)
        self.run_id = _run_id(self.run_dir)
        self._path = self.run_dir / "lobby.json"
        self._messages_path = self.run_dir / "lobby_messages.json"
        if not self._path.exists():
            self._write({"members": []})
        if not self._locks_path().exists():
            _write_locks(self.run_dir, {})
        if not self._messages_path.exists():
            self._write_messages([])

    def _locks_path(self) -> Path:
        return _locks_path(self.run_dir)

    def _read(self) -> dict:
        return json.loads(self._path.read_text(encoding="utf-8"))

    def _write(self, data: dict) -> None:
        self._path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_messages(self) -> list[dict]:
        return json.loads(self._messages_path.read_text(encoding="utf-8"))["messages"]

    def _write_messages(self, data: list[dict]) -> None:
        self._messages_path.write_text(
            json.dumps({"messages": data}, ensure_ascii=False, indent=2), encoding="utf-8")

    def join(self, persona_key: str) -> None:
        data = self._read()
        if persona_key not in data["members"]:
            data["members"].append(persona_key)
            self._write(data)

    def members(self) -> list[str]:
        return list(self._read()["members"])

    def post_lobby_message(self, persona_key: str, text: str) -> dict:
        if persona_key not in self.members():
            raise VisibilityError(f"'{persona_key}' ist kein Lobby-Mitglied — kein Sende-Recht im Lobby-Kanal.")
        record = {"from": persona_key, "text": text}
        msgs = self._read_messages()
        msgs.append(record)
        self._write_messages(msgs)
        return record

    def lobby_messages(self, persona_key: str) -> list[dict]:
        if persona_key not in self.members():
            raise VisibilityError(f"'{persona_key}' ist kein Lobby-Mitglied — kein Lese-Recht im Lobby-Kanal.")
        return list(self._read_messages())

    def lock_chrononaut(self, chrononaut_id: str, table_id: str) -> None:
        locks = _read_locks(self.run_dir)
        held_by = locks.get(chrononaut_id)
        if held_by is not None and held_by != table_id:
            raise ChrononautLockedError(
                f"Chrononaut {chrononaut_id} ist bereits an Tisch {held_by} aktiv "
                f"(gleichzeitiger Fortschritt an zwei Tischen ist untersagt)."
            )
        locks[chrononaut_id] = table_id
        _write_locks(self.run_dir, locks)

    def release_chrononaut(self, chrononaut_id: str, expected_table_id: str) -> None:
        locks = _read_locks(self.run_dir)
        if locks.get(chrononaut_id) == expected_table_id:
            del locks[chrononaut_id]
            _write_locks(self.run_dir, locks)

    def is_locked(self, chrononaut_id: str) -> str | None:
        return _read_locks(self.run_dir).get(chrononaut_id)


# ── Table ────────────────────────────────────────────────────────────────────


@dataclass
class Table:
    table_id: str
    leader: str
    members: list[str]
    chrononaut_ids: dict[str, str]
    run_dir: Path
    sl_log: list[dict] = field(default_factory=list)
    table_messages: list[dict] = field(default_factory=list)
    operator_meta: dict = field(default_factory=dict)
    status: str = "active"

    @property
    def _path(self) -> Path:
        return self.run_dir / "tables" / f"{self.table_id}.json"

    def persist(self) -> None:
        payload = {
            "table_id": self.table_id,
            "leader": self.leader,
            "members": self.members,
            "chrononaut_ids": self.chrononaut_ids,
            "sl_log": self.sl_log,
            "table_messages": self.table_messages,
            "operator_meta": self.operator_meta,
            "status": self.status,
        }
        self._path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, run_dir: str | Path, table_id: str) -> "Table":
        run_dir = Path(run_dir)
        data = json.loads((run_dir / "tables" / f"{table_id}.json").read_text(encoding="utf-8"))
        return cls(
            table_id=data["table_id"], leader=data["leader"], members=data["members"],
            chrononaut_ids=data["chrononaut_ids"], run_dir=run_dir,
            sl_log=data.get("sl_log", []), table_messages=data.get("table_messages", []),
            operator_meta=data.get("operator_meta", {}), status=data.get("status", "active"),
        )

    def chrononaut_id_to_persona(self) -> dict[str, str]:
        return {cid: pk for pk, cid in self.chrononaut_ids.items()}

    def join_more(self, persona_key: str, chrononaut_id: str, table_size_policy: TableSizePolicy) -> bool:
        """Nachtraeglicher Beitrittsversuch — in diesem Slice AUSDRUECKLICH
        NICHT unterstuetzt (kein legitimierender Konsens-/Offer-Beleg fuer
        einen ueber die urspruengliche Offer hinausgehenden Beitritt).
        Mutiert nie, liefert immer `False`."""
        persisted = Table.load(self.run_dir, self.table_id)
        if persisted.status == "closed":
            return False
        if len(self.members) >= table_size_policy.max_size:
            return False
        if persona_key in self.members:
            return False
        locks = _read_locks(self.run_dir)
        held_by = locks.get(chrononaut_id)
        if held_by is not None and held_by != self.table_id:
            return False
        return False


def create_table_from_offer_log(
    lobby: Lobby, table_id: str, offer_log_events: list[dict],
    chrononaut_ids: dict[str, str],
) -> tuple[Table | None, GroupDerivation]:
    """Leitet Gruppe/Leader aus dem Offer-Log ab und erzeugt bei Erfolg einen
    Tisch. Tischgroesse wird gegen `lobby.table_size_policy` geprueft (A1) —
    diese Funktion kennt keine feste Zahl.

    F5/K12/A6 (WEGKARTE §6): existiert unter `table_id` bereits ein OFFENER
    Tisch, ist das eine RESUME-Situation (derselbe Aufrufer -- z.B.
    `ui/tui.py`s lokale Runde -- fragt erneut an, z.B. nach einem Neustart),
    kein Fehlerfall. Der persistierte Tisch wird geladen und zurueckgegeben
    (samt seinem tatsaechlichen `sl_log`/Status), NICHT `None` -- vorher
    lieferte dieser Zweig `None` UND faelschlich die Erfolgs-`reason` der
    (fuer den erneuten Aufruf irrelevanten) Ableitung, was Aufrufer dazu
    brachte, eine gueltige Wiederaufnahme als gescheiterten Neuversuch zu
    melden (beobachtet in `results/new-final/observations.json` Test 09).

    D5/A6 (WEGKARTE §6 BLOCKER, PLAN-CRITIC-ABSCHLUSS.md HINWEIS, Test 05):
    ist der bereits existierende Tisch unter `table_id` hingegen
    GESCHLOSSEN (Abschnitt erfolgreich abgeschlossen), ist das KEIN Resume,
    sondern derselbe Aufrufer will einen NEUEN Abschnitt derselben Gruppe
    beginnen -- kein Wiederbeleben des geschlossenen Tisches
    (`TableClosedError`), sondern ein NEUER Tisch unter einer generations-
    weise hochgezaehlten Kennung (`<table_id>__2`, `__3`, ...). "Resume
    eines offenen Abschnitts" und "neuer Abschnitt nach Abschluss" bleiben
    damit an EINER Stelle klar getrennt (statt den Bug nur eine Ebene hoeher
    zu verschieben). Der Aufrufer MUSS die tatsaechlich zurueckgegebene
    `table.table_id` (nicht das urspruenglich angefragte `table_id`) fuer
    Folgeoperationen (z.B. `section_id`) verwenden.

    Eine WIRKLICH gescheiterte Ableitung (keine vollstaendig angenommene
    Offer) bleibt weiterhin `None` mit der Ableitungs-`reason`."""
    base_table_id = table_id
    generation = 1
    while True:
        candidate_id = base_table_id if generation == 1 else f"{base_table_id}__{generation}"
        candidate_path = lobby.run_dir / "tables" / f"{candidate_id}.json"
        if not candidate_path.exists():
            table_id = candidate_id
            break
        existing_table = Table.load(lobby.run_dir, candidate_id)
        if existing_table.status != "closed" and not _table_has_final(lobby.run_dir, candidate_id):
            return existing_table, GroupDerivation(
                leader=existing_table.leader, members=list(existing_table.members),
                dissenters={}, source_offer_id=None,
                reason=f"table_id {candidate_id!r} existiert bereits (offen) — Wiederaufnahme (kein Neuanlegen).",
            )
        generation += 1
    derivation = derive_group_and_leader(offer_log_events)
    if derivation.leader is None or not derivation.members:
        return None, derivation
    size = len(derivation.members)
    if not lobby.table_size_policy.validate_size(size):
        return None, derivation

    for pk in derivation.members:
        cid = chrononaut_ids.get(pk)
        held_by = lobby.is_locked(cid) if cid else None
        if held_by is not None:
            return None, derivation
        if cid is not None and _member_bound_by_open_order(lobby.run_dir, cid):
            return None, derivation

    table = Table(
        table_id=table_id, leader=derivation.leader, members=list(derivation.members),
        chrononaut_ids={pk: chrononaut_ids[pk] for pk in derivation.members},
        run_dir=lobby.run_dir,
        operator_meta={
            "offer_log": offer_log_events,
            "derivation_reason": derivation.reason,
            "source_offer_id": derivation.source_offer_id,
            "dissenters": derivation.dissenters,
        },
    )
    for pk in derivation.members:
        lobby.lock_chrononaut(table.chrononaut_ids[pk], table_id)
    table.persist()
    return table, derivation


# ── Leader-only-Send ─────────────────────────────────────────────────────────


def _table_has_final(run_dir: str | Path, table_id: str) -> bool:
    completion_dir = Path(run_dir) / "completion"
    if not completion_dir.exists():
        return False
    for p in completion_dir.glob("*__final.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if data.get("table_id") == table_id:
            return True
    return False


def submit_to_sl(
    table: Table, actor_persona_key: str, gm_transport, turn_idx: int, text: str,
    origin_persona_key: str | None = None, origin_source: str | None = None,
    save_payload: dict | None = None,
) -> dict:
    """Transport fuehrt eine vom Leader freigegebene Nachricht aus. `gm_transport`
    ist ein beliebiges Objekt mit `.turn(turn_idx, text) -> {content, usage,
    sources, latency_s, chat_id}` (Fake, SLStub, echter Produktionsadapter —
    identischer Vertrag, s. adapters/base.py:GMTransport)."""
    if actor_persona_key != table.leader:
        raise LeaderOnlySendError(
            f"Nur der Leader ({table.leader}) darf an die SL senden, nicht '{actor_persona_key}'."
        )
    persisted = Table.load(table.run_dir, table.table_id)
    if persisted.status == "closed" or _table_has_final(table.run_dir, table.table_id):
        raise TableClosedError(f"Tisch {table.table_id} ist geschlossen — kein weiterer Versand.")
    open_section = _open_completion_order_for_table(table.run_dir, table.table_id)
    if open_section is not None:
        raise TablePendingError(
            f"Tisch {table.table_id} hat einen offenen Abschluss-Auftrag fuer section_id "
            f"{open_section!r} — kein weiterer Versand, bis dieser konsistent finalisiert ist."
        )
    locks = _read_locks(table.run_dir)
    stale_members = [
        pk for pk in table.members
        if locks.get(table.chrononaut_ids[pk]) not in (None, table.table_id)
    ]
    if stale_members:
        raise TableClosedError(
            f"Tisch {table.table_id} besitzt nicht mehr alle Chrononaut-Locks (veraltetes Tisch-Handle): {stale_members}."
        )
    result = gm_transport.turn(turn_idx, text)

    current = Table.load(table.run_dir, table.table_id)
    current.sl_log.append({
        "turn_idx": turn_idx,
        "leader_message": text,
        "origin_persona_key": origin_persona_key if origin_persona_key is not None else actor_persona_key,
        "origin_source": origin_source,
        "save_payload": save_payload,
        "content": result["content"],
    })
    current.persist()
    table.sl_log = current.sl_log
    table.table_messages = current.table_messages
    table.status = current.status
    return result


def post_table_message(table: Table, persona_key: str, text: str) -> dict:
    if persona_key not in table.members:
        raise VisibilityError(f"'{persona_key}' ist nicht Mitglied von Tisch {table.table_id} — kein Sende-Recht.")
    persisted = Table.load(table.run_dir, table.table_id)
    if persisted.status == "closed" or _table_has_final(table.run_dir, table.table_id):
        raise TableClosedError(f"Tisch {table.table_id} ist geschlossen — kein Absprachekanal-Versand mehr.")
    open_section = _open_completion_order_for_table(table.run_dir, table.table_id)
    if open_section is not None:
        raise TablePendingError(
            f"Tisch {table.table_id} hat einen offenen Abschluss-Auftrag fuer section_id "
            f"{open_section!r} — kein Absprachekanal-Versand, bis dieser konsistent finalisiert ist."
        )
    locks = _read_locks(table.run_dir)
    stale_members = [
        pk for pk in table.members
        if locks.get(table.chrononaut_ids[pk]) not in (None, table.table_id)
    ]
    if stale_members:
        raise TableClosedError(
            f"Tisch {table.table_id} besitzt nicht mehr alle Chrononaut-Locks (veraltetes Tisch-Handle): {stale_members}."
        )

    current = Table.load(table.run_dir, table.table_id)
    record = {"from": persona_key, "text": text}
    current.table_messages.append(record)
    current.persist()
    table.sl_log = current.sl_log
    table.table_messages = current.table_messages
    table.status = current.status
    return record


# ── Sichtfilter ──────────────────────────────────────────────────────────────


def persona_view(table: Table, persona_key: str) -> dict:
    if persona_key not in table.members:
        raise VisibilityError(f"'{persona_key}' ist nicht Mitglied von Tisch {table.table_id}.")
    return {
        "table_id": table.table_id,
        "leader": table.leader,
        "members": list(table.members),
        "status": table.status,
        "sl_log": [dict(e) for e in table.sl_log],
        "table_messages": [dict(m) for m in table.table_messages],
    }


def operator_view(table: Table) -> dict:
    return {
        "table_id": table.table_id,
        "leader": table.leader,
        "members": list(table.members),
        "chrononaut_ids": dict(table.chrononaut_ids),
        "status": table.status,
        "sl_log": list(table.sl_log),
        "table_messages": list(table.table_messages),
        "operator_meta": dict(table.operator_meta),
    }


# ── Completion-Idempotenz + Save/State-Rueckkehr ────────────────────────────


@dataclass
class CompletionResult:
    success: bool
    already_completed: bool
    written: bool
    members_completed: list[str]
    missing: list[str]
    reason: str


def _completion_guard_path(run_dir: Path, chrononaut_id: str, section_id: str) -> Path:
    return run_dir / "completion" / f"{_safe_component(chrononaut_id)}__{_safe_component(section_id)}.json"


def _completion_plan_path(run_dir: Path, section_id: str) -> Path:
    return run_dir / "completion" / f"{_safe_component(section_id)}__plan.json"


def _completion_final_path(run_dir: Path, section_id: str) -> Path:
    return run_dir / "completion" / f"{_safe_component(section_id)}__final.json"


def _open_completion_order_for_table(
    run_dir: Path, table_id: str, exclude_section_id: str | None = None,
) -> str | None:
    completion_dir = run_dir / "completion"
    if not completion_dir.exists():
        return None
    for p in completion_dir.glob("*__plan.json"):
        section_id = p.name[: -len("__plan.json")]
        if exclude_section_id is not None and section_id == exclude_section_id:
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if data.get("table_id") != table_id:
            continue
        if not _completion_final_path(run_dir, section_id).exists():
            return section_id
    return None


def _member_bound_by_open_order(run_dir: str | Path, chrononaut_id: str) -> bool:
    run_dir = Path(run_dir)
    completion_dir = run_dir / "completion"
    if not completion_dir.exists():
        return False
    for p in completion_dir.glob("*__plan.json"):
        section_id = p.name[: -len("__plan.json")]
        if _completion_final_path(run_dir, section_id).exists():
            continue
        try:
            plan_data = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        table_id = plan_data.get("table_id")
        if not table_id:
            continue
        try:
            bound_table = Table.load(run_dir, table_id)
        except (OSError, json.JSONDecodeError):
            continue
        if chrononaut_id in bound_table.chrononaut_ids.values():
            return True
    return False


def _current_save_versions_dir(current_saves_dir: Path, persona_key: str) -> Path:
    return current_saves_dir / f"{persona_key}__versions"


def _write_current_save_version(current_saves_dir: Path, persona_key: str, block: dict) -> Path:
    versions_dir = _current_save_versions_dir(current_saves_dir, persona_key)
    versions_dir.mkdir(exist_ok=True)
    existing = [int(p.stem) for p in versions_dir.glob("*.json") if p.stem.isdigit()]
    seq = (max(existing) + 1) if existing else 1
    version_path = versions_dir / f"{seq:04d}.json"
    tmp_path = versions_dir / f".{seq:04d}.json.tmp"
    tmp_path.write_text(json.dumps(block, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(version_path)
    return version_path


def load_current_save(
    run_dir: str | Path, persona_key: str, persona_state_store: PersonaStateStore,
    states_dir: str | Path | None = None,
) -> dict | None:
    """Liest den zuletzt VEROEFFENTLICHTEN AKTUELLEN Save fuer `persona_key`.
    `persona_state_store` (A2/A6) ersetzt den frueheren globalen
    `persona_state`-Modulimport."""
    run_dir = Path(run_dir)
    if states_dir is None:
        states_dir = run_dir.parent / "states"
    try:
        state = persona_state_store.load_state(persona_key, states_dir=states_dir)
    except FileNotFoundError:
        return None
    ref = state.get(_CURRENT_SAVE_REF_FIELD)
    if not isinstance(ref, dict) or ref.get("run_id") != _run_id(run_dir):
        return None
    seq = ref.get("seq")
    if seq is None:
        return None
    version_path = _current_save_versions_dir(run_dir / "current_saves", persona_key) / f"{int(seq):04d}.json"
    try:
        return json.loads(version_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _validate_harvest(
    table: Table, harvest: dict[str, dict], states_dir: str | Path,
    harvest_validator: HarvestValidator, persona_state_store: PersonaStateStore,
) -> tuple[list[str], dict[str, dict]]:
    """A1/A27: alle Domaenenregeln (v7/char-id/Ein-Figur o.ae.) leben
    ausschliesslich in `harvest_validator` — dieser Kern ruft nur die zwei
    generischen Protokoll-Methoden auf."""
    missing: list[str] = []
    identity_states: dict[str, dict] = {}
    for pk in table.members:
        expected_id = table.chrononaut_ids[pk]
        blk = harvest.get(pk)
        if blk is None or not harvest_validator.validate_block(blk, expected_id):
            missing.append(pk)
            continue
        try:
            state = persona_state_store.load_state(pk, states_dir=states_dir)
        except FileNotFoundError:
            missing.append(pk)
            continue
        if not harvest_validator.validate_identity(state, pk, expected_id):
            missing.append(pk)
            continue
        identity_states[pk] = state
    return missing, identity_states


def _resume_and_harvest(
    lobby: Lobby, table: Table, section_id: str, plan_data: dict,
    states_dir: str | Path, today: str,
    guard_paths: dict[str, Path],
    harvest_validator: HarvestValidator, persona_state_store: PersonaStateStore,
) -> CompletionResult:
    """A3/D5 (PLAN-CRITIC-ABSCHLUSS.md BLOCKER, WEGKARTE §6): PHASE 1 der
    Abschluss-Autoritaet -- schreibt/aktualisiert Saves+States je Mitglied
    gemaess dem gepinnten Plan (idempotent ueber die Guard-Dateien: ein
    Retry ueberspringt bereits geschriebene Mitglieder, kein Doppelzaehlen,
    A08 unveraendert). Ruehrt WEDER den `__final`-Marker NOCH den
    Chrononaut-Lock-Release NOCH den Tisch-Status an -- das ist PHASE 2
    (`finalize_section_after_reflection`), die der Aufrufer (`core/runtime.
    py:SectionRuntime.run_full_section`) ERST NACH erfolgreicher Pflicht-
    KI-Reflexion aufruft (Test 10: eine fehlgeschlagene Pflicht-Reflexion
    haelt den Abschnitt offen/wiederaufnehmbar -- bereits geerntete
    Saves/States bleiben dabei gueltig, kein Doppelspiel bei Recovery)."""
    run_dir = lobby.run_dir
    members_plan: dict[str, dict] = plan_data.get("members", {})

    pinned_harvest = {pk: entry.get("save") for pk, entry in members_plan.items()}
    missing, identity_states = _validate_harvest(
        table, pinned_harvest, states_dir, harvest_validator, persona_state_store,
    )
    if missing:
        return CompletionResult(
            success=False, already_completed=False, written=False,
            members_completed=[], missing=missing,
            reason=f"gepinnter Abschluss-Auftrag fuer {section_id!r} ist inkonsistent/unvollstaendig: {missing}.",
        )

    current_saves_dir = run_dir / "current_saves"
    current_saves_dir.mkdir(exist_ok=True)

    written_any = False
    for pk in table.members:
        cid = table.chrononaut_ids[pk]
        guard_path = guard_paths[pk]
        if guard_path.exists():
            continue

        round_no = members_plan[pk]["round_no"]
        blk = pinned_harvest[pk]

        expected_prev_ref = members_plan[pk].get("expected_prev_ref")
        actual_prev_ref = identity_states[pk].get(_CURRENT_SAVE_REF_FIELD)
        if expected_prev_ref != actual_prev_ref:
            referenced = load_current_save(run_dir, pk, persona_state_store, states_dir=states_dir)
            if referenced != blk:
                return CompletionResult(
                    success=False, already_completed=False, written=written_any,
                    members_completed=[], missing=[],
                    reason=(
                        f"Abschluss-Auftrag fuer {section_id!r} erwartet fuer {pk!r} eine andere "
                        f"Vorgaengergeneration als aktuell veroeffentlicht — Recovery abgelehnt "
                        f"(kein Ueberschreiben einer neueren Generation)."
                    ),
                )
            version_path = _current_save_versions_dir(current_saves_dir, pk) / f"{int(actual_prev_ref['seq']):04d}.json"
            save_sha256 = hashlib.sha256(version_path.read_bytes()).hexdigest()
            direct_path = current_saves_dir / f"{pk}.json"
            guard_path.write_text(
                json.dumps({
                    "chrononaut_id": cid, "section_id": section_id, "persona_key": pk,
                    "table_id": table.table_id, "status": "completed",
                    "save_path": str(version_path.relative_to(run_dir)),
                    "current_save_path": str(direct_path.relative_to(run_dir)),
                    "save_sha256": save_sha256,
                }, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            written_any = True
            continue

        direct_path = current_saves_dir / f"{pk}.json"
        direct_path.write_text(json.dumps(blk, ensure_ascii=False, indent=2), encoding="utf-8")
        version_path = _write_current_save_version(current_saves_dir, pk, blk)
        save_sha256 = hashlib.sha256(version_path.read_bytes()).hexdigest()
        new_seq = int(version_path.stem)

        state = persona_state_store.update_state(
            identity_states[pk], round_no=round_no,
            kernereignis=f"Abschnitt {section_id} am Tisch {table.table_id} abgeschlossen.",
            now=today, datum=today, mission=section_id,
        )
        state[_CURRENT_SAVE_REF_FIELD] = {"run_id": _run_id(run_dir), "seq": new_seq}
        persona_state_store.save_state(pk, state, states_dir=states_dir)

        guard_path.write_text(
            json.dumps({
                "chrononaut_id": cid, "section_id": section_id, "persona_key": pk,
                "table_id": table.table_id, "status": "completed",
                "save_path": str(version_path.relative_to(run_dir)),
                "current_save_path": str(direct_path.relative_to(run_dir)),
                "save_sha256": save_sha256,
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        written_any = True

    return CompletionResult(
        success=True, already_completed=False, written=written_any,
        members_completed=list(table.members), missing=[],
        reason="Saves/States vollstaendig geerntet -- Pflicht-Reflexion aussteht vor endgueltigem Abschluss.",
    )


def finalize_section_after_reflection(
    lobby: Lobby, table: Table, section_id: str,
) -> CompletionResult:
    """A3/D5 (PLAN-CRITIC-ABSCHLUSS.md BLOCKER, WEGKARTE §6): PHASE 2 der
    Abschluss-Autoritaet -- wird vom Aufrufer NUR aufgerufen, wenn PHASE 1
    (`_resume_and_harvest`, ueber `complete_section`) erfolgreich war UND
    alle Pflicht-KI-Reflexionen erfolgreich waren
    (`SectionRuntime._collect_reflections` lieferte `True`). Schreibt den
    `__final`-Marker, loest ALLE Chrononaut-Locks UND markiert den Tisch
    `closed` -- exakt das, was `_resume_and_harvest`s Vorgaenger
    (`_resume_and_finalize`) vorher ATOMAR mit der Save-Ernte erledigte.
    Idempotent: existiert der `__final`-Marker bereits, ist ein weiterer
    Aufruf ein No-op-Erfolg (kein doppeltes Lock-Release/Doppel-`closed`)."""
    run_dir = lobby.run_dir
    final_path = _completion_final_path(run_dir, section_id)
    if final_path.exists():
        return CompletionResult(
            success=True, already_completed=True, written=False,
            members_completed=list(table.members), missing=[],
            reason="section_id bereits final abgeschlossen (idempotent) — kein zweiter Write.",
        )
    guard_paths = {
        pk: _completion_guard_path(run_dir, table.chrononaut_ids[pk], section_id)
        for pk in table.members
    }
    missing_guards = [pk for pk, p in guard_paths.items() if not p.exists()]
    if missing_guards:
        raise ValueError(
            f"finalize_section_after_reflection: PHASE 1 (Ernte) fuer section_id {section_id!r} "
            f"ist nicht vollstaendig -- fehlende Guard-Dateien fuer {missing_guards} "
            f"(interner Aufrufer-Fehler, kein Nutzerpfad)."
        )
    for pk in table.members:
        lobby.release_chrononaut(table.chrononaut_ids[pk], table.table_id)
    final_path.write_text(
        json.dumps({
            "section_id": section_id, "table_id": table.table_id,
            "members": list(table.members),
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    persisted = Table.load(run_dir, table.table_id)
    persisted.status = "closed"
    persisted.persist()
    table.status = "closed"

    return CompletionResult(
        success=True, already_completed=False, written=False,
        members_completed=list(table.members), missing=[],
        reason="Abschnitt nach erfolgreicher Pflicht-Reflexion vollstaendig abgeschlossen, Saves/States deponiert.",
    )


def complete_section(
    lobby: Lobby, table: Table, section_id: str,
    harvested_saves: dict[str, dict], states_dir: str | Path, today: str,
    harvest_validator: HarvestValidator, persona_state_store: PersonaStateStore,
) -> CompletionResult:
    """Wertet eine Save-Ernte fuer `section_id` aus. Ablauf/Idempotenz-Logik
    IDENTISCH zu P1 `rooms.complete_section` — Domaenenwissen (v7/char-id) ist
    jedoch komplett in `harvest_validator` ausgelagert (A1).

    A5 (bindend): `today` hat KEINEN Default mehr — jeder Aufrufer MUSS das
    reale Tagesdatum explizit uebergeben."""
    if not _SECTION_ID_RE.match(section_id):
        return CompletionResult(
            success=False, already_completed=False, written=False,
            members_completed=[], missing=[],
            reason=(
                f"section_id {section_id!r} enthaelt unzulaessige Zeichen "
                f"(erlaubt: [A-Za-z0-9_-]) — kein Abschluss."
            ),
        )

    run_dir = lobby.run_dir
    guard_paths = {
        pk: _completion_guard_path(run_dir, table.chrononaut_ids[pk], section_id)
        for pk in table.members
    }
    final_path = _completion_final_path(run_dir, section_id)
    plan_path = _completion_plan_path(run_dir, section_id)

    if final_path.exists():
        try:
            final_data = json.loads(final_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            final_data = {}
        if final_data.get("table_id") == table.table_id and final_data.get("section_id") == section_id:
            persisted = Table.load(run_dir, table.table_id)
            if persisted.status != "closed":
                persisted.status = "closed"
                persisted.persist()
            return CompletionResult(
                success=True, already_completed=True, written=False,
                members_completed=list(final_data.get("members") or table.members), missing=[],
                reason="section_id bereits vollstaendig abgeschlossen (finalisiert) — kein zweiter Write.",
            )
        return CompletionResult(
            success=False, already_completed=False, written=False,
            members_completed=[], missing=[],
            reason=(
                f"section_id {section_id!r} ist bereits von Tisch {final_data.get('table_id')!r} "
                f"abgeschlossen — Kollision, Tisch {table.table_id!r} erbt keinen fremden Abschluss."
            ),
        )

    if plan_path.exists():
        try:
            plan_data = json.loads(plan_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            plan_data = {}
        if plan_data.get("table_id") != table.table_id:
            return CompletionResult(
                success=False, already_completed=False, written=False,
                members_completed=[], missing=[],
                reason=(
                    f"section_id {section_id!r} hat bereits einen Abschluss-Auftrag von Tisch "
                    f"{plan_data.get('table_id')!r} — Kollision, Tisch {table.table_id!r} erbt keinen fremden Auftrag."
                ),
            )
        return _resume_and_harvest(
            lobby, table, section_id, plan_data, states_dir, today, guard_paths,
            harvest_validator, persona_state_store,
        )

    other_open = _open_completion_order_for_table(run_dir, table.table_id, exclude_section_id=section_id)
    if other_open is not None:
        return CompletionResult(
            success=False, already_completed=False, written=False,
            members_completed=[], missing=[],
            reason=(
                f"Tisch {table.table_id} ist an einen offenen Abschluss-Auftrag fuer section_id "
                f"{other_open!r} gebunden — kein weiterer Abschluss, bis dieser konsistent finalisiert ist."
            ),
        )

    persisted = Table.load(run_dir, table.table_id)
    if persisted.status == "closed" or _table_has_final(run_dir, table.table_id):
        return CompletionResult(
            success=False, already_completed=False, written=False,
            members_completed=[], missing=[],
            reason=f"Tisch {table.table_id} ist geschlossen (persistierter Stand) — kein weiterer Abschluss auf altem Tisch.",
        )
    locks = _read_locks(run_dir)
    stale_members = [
        pk for pk in table.members
        if locks.get(table.chrononaut_ids[pk]) not in (None, table.table_id)
    ]
    if stale_members:
        return CompletionResult(
            success=False, already_completed=False, written=False,
            members_completed=[], missing=[],
            reason=f"Tisch {table.table_id} besitzt nicht mehr alle Chrononaut-Locks (veraltetes Tisch-Handle): {stale_members}.",
        )

    missing, identity_states = _validate_harvest(
        table, harvested_saves, states_dir, harvest_validator, persona_state_store,
    )
    if missing:
        return CompletionResult(
            success=False, already_completed=False, written=False,
            members_completed=[], missing=missing,
            reason=f"fehlende/falsch zugeordnete/falsch identifizierte Saves fuer: {missing} — kein Abschluss.",
        )

    plan_data = {
        "table_id": table.table_id,
        "members": {
            pk: {
                "round_no": identity_states[pk].get("rounds_played", 0) + 1,
                "save": harvested_saves[pk],
                "expected_prev_ref": identity_states[pk].get(_CURRENT_SAVE_REF_FIELD),
            }
            for pk in table.members
        },
    }
    plan_path.write_text(json.dumps(plan_data, ensure_ascii=False, indent=2), encoding="utf-8")

    return _resume_and_harvest(
        lobby, table, section_id, plan_data, states_dir, today, guard_paths,
        harvest_validator, persona_state_store,
    )


def return_to_lobby(lobby: Lobby, table: Table) -> None:
    for pk in table.members:
        lobby.join(pk)


# ── K4/D1 (WEGKARTE §6, A1): Current-Publikation ausserhalb eines Abschluss-
# Turns (z.B. beim Import) -- ERWEITERT dieselbe Current-Save-Versionierung,
# die `_resume_and_finalize` fuer erspielte Abschluesse verwendet (kein
# zweiter Publikationsweg, D5-Grenze "erweitern, nicht neu bauen"). ─────────


def publish_current_save(
    run_dir: str | Path, persona_key: str, block: dict,
    persona_state_store: PersonaStateStore, states_dir: str | Path,
) -> None:
    """Veroeffentlicht `block` als NEUE aktuelle Version fuer `persona_key`
    (z.B. eine bestaetigte Import-Uebernahme, `ui/tui.py:_cmd_import`) --
    OHNE Rundenzaehler zu erhoehen (Import ist kein erspielter Abschnitt).
    Setzt voraus, dass fuer `persona_key` bereits ein gueltiger Persona-State
    existiert (s. `domain.zeitriss.onboarding.ensure_participant_persona_state`)."""
    run_dir = Path(run_dir)
    current_saves_dir = run_dir / "current_saves"
    current_saves_dir.mkdir(parents=True, exist_ok=True)
    direct_path = current_saves_dir / f"{persona_key}.json"
    direct_path.write_text(json.dumps(block, ensure_ascii=False, indent=2), encoding="utf-8")
    version_path = _write_current_save_version(current_saves_dir, persona_key, block)
    new_seq = int(version_path.stem)
    state = persona_state_store.load_state(persona_key, states_dir=states_dir)
    state[_CURRENT_SAVE_REF_FIELD] = {"run_id": _run_id(run_dir), "seq": new_seq}
    persona_state_store.save_state(persona_key, state, states_dir=states_dir)


def open_completion_order_for_table(run_dir: str | Path, table_id: str) -> str | None:
    """A1/D5 (WEGKARTE §8, Plan-Critic A1, Test 07): oeffentliche Sicht auf
    `_open_completion_order_for_table` -- liefert die section_id eines
    offenen (`__plan.json` ohne `__final.json`) Abschluss-Auftrags fuer
    `table_id`, sonst `None`. `core/runtime.py:run_full_section` nutzt dies,
    um beim Resume NUR den fehlenden Abschlussschritt (Reflexion/
    Finalisierung) fortzusetzen statt einen neuen Spielzug/GM-Request
    auszuloesen (kein `TablePendingError`)."""
    return _open_completion_order_for_table(Path(run_dir), table_id)


def chrononaut_active_binding(run_dir: str | Path, chrononaut_id: str) -> bool:
    """D1/A1 (K3, PLAN-CRITIC-ABSCHLUSS.md): echte Lock-Pruefung fuer
    Import-Konflikte -- ersetzt das zuvor hart verdrahtete `active_binding=
    False` in `ui/tui.py:_cmd_import`. Sicher auch ohne existierenden
    `run_dir` (noch keine Lobby angelegt) -- `_read_locks` liefert dann `{}`."""
    return _read_locks(Path(run_dir)).get(chrononaut_id) is not None


def chrononaut_open_completion_order(run_dir: str | Path, chrononaut_id: str) -> bool:
    """D1/A1 (K3): echte Pruefung auf einen offenen (noch nicht
    finalisierten) Abschluss-Auftrag, der diese Chrononaut-ID bindet."""
    return _member_bound_by_open_order(run_dir, chrononaut_id)
