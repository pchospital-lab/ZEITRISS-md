#!/usr/bin/env python3
"""
lobby/rooms.py — Lobby + Tisch-Ebene ueber dem bestehenden Abschnitts-Baustein.

OFFLINE, dateibasiert (JSON unter einem run_dir), kein Dauerprozess, kein Netz, keine
zweite Regelengine. Baut NICHT auf einem Aufruf-Roster (`--players ...`) auf, sondern
leitet Gruppe/Leader aus protokollierten Offer-/Consent-Logs ab (Freeze-Ausnahme 1,
siehe PLAN-P1.md / README.md).

Enthaelt:
  - Gruppen-/Leader-Ableitung aus Offer-/Consent-Logs (Plan-Critic-Auflage 2).
  - Lobby + Table mit Mitgliedschaft, Tisch-Grenze 1-5, Chrononaut-Lock.
  - Leader-only-Send (COORDINATION-MODEL-FROZEN Punkt 3 — NICHT verhandelbar).
  - Sichtfilter: getrennte Operator-/Persona-Ansicht (Plan-Critic-Auflage 3).
  - Nachrichtenkanaele (R7): oeffentlicher Lobby-Kanal, privater Tisch-
    Absprachekanal (nur Mitglieder), Leader/SL-Dialog (submit_to_sl persistiert
    Leader-Nachricht UND SL-Antwort, inkl. Herkunftsbeleg + getrennter
    Save-Payload — siehe section.py).
  - Completion-Idempotenz: Abschnitts-Guard pro (chrononaut, section_id) +
    persistentes Abschluss-Journal (`completion/<section>__plan.json`) fuer den
    Teilschreib-/Crash-Fall + persona_state-Rundenfortschreibung + resumierbare
    Finalisierung (`completion/<section>__final.json` als EINZIGER
    `already_completed`-Nachweis, geprueft gegen `table_id` UND `section_id`,
    NB-C/Auflage 1+4/K2-Nachzug). `section_id` folgt einer strikten Grammatik
    (`[A-Za-z0-9_-]`, frueh in `complete_section` abgelehnt) — kollisionsfrei
    unter der Dateinamen-Normalisierung `_safe_component`.
  - Offener Abschluss-Auftrag bindet Mitglieder auch gegen NEUE Tische
    (`_member_bound_by_open_order`, K2-Nachzug): ein `__plan.json` ohne
    eigenes `__final` bindet seine Chrononaut-IDs exklusiv, unabhaengig vom
    physischen Lock-Zustand — `create_table_from_offer_log` lehnt eine
    Aufnahme fuer ein so gebundenes Mitglied ab (`(None, derivation)`, keine
    Ausnahme). Nach gueltigem `__final` ist der Auftrag geschlossen und bindet
    nicht mehr (freie Neugruppierung bleibt erhalten).
  - Persoenliche Current-Save-Rueckkehr (`current_saves/<pk>.json` +
    versionierte, atomare Ablage `current_saves/<pk>__versions/<seq>.json`,
    NB-C/Auflage 2, K1) — `load_current_save` liest den vom Persona-State
    (Current-Save-Ref, EINZIGER Veroeffentlichungs-Flip) referenzierten Save,
    KEIN "hoechste Version"-Read. Der Current-Save-Ref ist an eine stabile,
    pro `run_dir` erzeugte `run_id` gebunden (`run_dir/run_id.json`,
    K1-Nachzug) — eine Referenz aus einem ANDEREN `run_dir` (selbst bei
    gleicher relativer Sequenznummer) loest nie einen Save in einem fremden
    Speicherbereich auf.
  - Tisch-Identitaet: Chrononaut-Lock ueber `locks.json`, Tisch-Status `closed`
    nach Abschluss, Lock-Freigabe nur durch den Eigentuemer-Tisch, keine
    ueberschreibende Neuanlage bestehender `table_id`. Nachtraeglicher Beitritt
    (`Table.join_more`) ist in diesem Slice AUSDRUECKLICH NICHT unterstuetzt —
    mutiert nie, liefert immer `False` (NB-D/D2+D3). ALLE Mutationswege
    (`submit_to_sl`, `post_table_message`, `complete_section`, `join_more`)
    pruefen den PERSISTIERTEN (nicht den ggf. veralteten in-memory) Tisch-
    status + die Lock-Eigentuemerschaft, bevor sie etwas aendern (NB-D/R4+R6).

Reuse (nicht veraendert): `persona_state.py` (load/update/save_state,
Anti-Stacking-Gate), `agent_mp/saves.py` (v7-Personal-Save-Contract-Pruefung).
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path

_HARNESS_DIR = Path(__file__).resolve().parents[1]
_AGENT_MP_DIR = _HARNESS_DIR / "agent_mp"
for _p in (str(_HARNESS_DIR), str(_AGENT_MP_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import persona_state as ps  # noqa: E402
import saves as save_lib  # noqa: E402

TABLE_MIN_SIZE = 1
TABLE_MAX_SIZE = 5

# K1/K1-Nachzug: additives Current-Save-Ref-Feld im (schema-
# additionalProperties:true) Persona-State — traegt EIN JSON-OBJEKT
# `{"run_id": <str>, "seq": <int>}` (NICHT mehr eine bare Sequenznummer): die
# Sequenznummer referenziert `current_saves/<pk>__versions/<seq>.json`, die
# `run_id` bindet diese Referenz zusaetzlich an den Speicherbereich
# (`run_dir`), in dem sie veroeffentlicht wurde (s. `_run_id`/
# `load_current_save`) — ein zweites `run_dir`, das lokal wieder bei seq=1
# beginnt, kann eine fremde Referenz so nie versehentlich umdeuten. Wird NUR
# im selben Aufruf gesetzt, der auch `ps.save_state` aufruft (der einzige
# Flip, s. `_resume_and_finalize`).
_CURRENT_SAVE_REF_FIELD = "current_save_version"

# ── Adapter-Seam: Schema-Pfad-Fix fuer das wiederverwendete persona_state.py ────
#
# persona_state.py ist FROZEN (wird hier nicht editiert). Sein Default-Schema-Pfad
# ist relativ zum Modul fest verdrahtet auf `<harness>/../personas/persona-state.
# schema.json`. In diesem Worktree liegt die Schema-Datei aber tatsaechlich unter
# `<qa>/fixtures/persona-state.schema.json` (bestaetigt per `git log --all` fuer den
# Commit, der die Datei eingefuehrt hat — kein Artefakt dieses Slices). Ohne diesen
# Fix wirft jeder `persona_state.save_state()`-Aufruf FileNotFoundError, weil die
# Datei am Default-Pfad nie existiert hat. Wir AENDERN NICHT den Modulcode, sondern
# korrigieren zur Laufzeit nur den Datei-Pfad, den das Modul selbst nachschlaegt,
# und leeren den Schema-Cache, falls er vorher (fehlerhaft) befuellt wurde.
_REAL_SCHEMA_PATH = _HARNESS_DIR.parent / "fixtures" / "persona-state.schema.json"
if _REAL_SCHEMA_PATH.exists() and ps._SCHEMA_PATH != _REAL_SCHEMA_PATH:
    ps._SCHEMA_PATH = _REAL_SCHEMA_PATH
    ps._SCHEMA_CACHE = None


# ── Gruppen-/Leader-Ableitung aus Offer-/Consent-Log (Auflage 2) ────────────────
#
# Regel (verbindlich, siehe README.md „Leader-Ableitungsregel"):
#   Scanne die Offer-Events in Log-Reihenfolge. Eine Offer gilt als „vollstaendig
#   angenommen", wenn JEDE in `wants` genannte Persona im Log ein
#   `{"type":"consent","offer_id":<id>,"accept":true}` hat UND KEINE davon ein
#   `accept:false` fuer dieselbe offer_id hat. Die ERSTE so vollstaendige Offer im
#   Log bestimmt Anker/Leader (= ihr `from`) und die Mitgliederliste
#   ({leader} ∪ wants — R6: die EINGELADENE Menge, NICHT zusaetzliche, nicht
#   eingeladene Zustimmer aus `accepted`). Widerspruch/fehlende Zustimmung fuehrt
#   NICHT dazu, dass die widersprechende Persona still aus `wants` herausgefiltert
#   wird — die Offer bleibt insgesamt unvollstaendig; nur eine SPAETERE, tatsaechlich
#   neu konsentierte Offer (ohne die widersprechende Persona in `wants`) kann eine
#   Gruppe bilden. So bleibt der Leader nachvollziehbar aus Persona-Nachrichten
#   ableitbar, nicht aus einer Controller-Wahl.


@dataclass
class GroupDerivation:
    leader: str | None
    members: list[str]
    dissenters: dict[str, str]  # persona_key -> Ablehnungsgrund (aus dem Log)
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
            # R6: Mitglieder = {leader} ∪ wants (die EINGELADENE Menge), nicht
            # {leader} ∪ accepted — nicht eingeladene Zustimmer ("ghost") duerfen
            # eine vollstaendig angenommene Offer nicht um sich selbst erweitern,
            # auch wenn sie zusaetzlich (unaufgefordert) zugestimmt haben.
            members = sorted({o["from"]} | o["wants"])
            return GroupDerivation(
                leader=o["from"], members=members, dissenters=dict(dissenters),
                source_offer_id=oid, reason=f"erste vollstaendig angenommene Offer '{oid}'",
            )

    return GroupDerivation(
        leader=None, members=[], dissenters=dict(dissenters),
        source_offer_id=None, reason="keine vollstaendig angenommene Offer im Log",
    )


# ── Chrononaut-Locks: gemeinsamer, dateibasierter Speicher (Auflage R4) ─────────
#
# `locks.json` liegt direkt unter `run_dir` und wird sowohl von `Lobby` (Tisch-
# erstellung, Abschluss-Freigabe) als auch von `Table.join_more` (nachtraeglicher
# Beitritt) gelesen/geschrieben — beide kennen `run_dir`, keine zusaetzliche
# Kopplung noetig.


def _locks_path(run_dir: str | Path) -> Path:
    return Path(run_dir) / "locks.json"


def _read_locks(run_dir: str | Path) -> dict:
    p = _locks_path(run_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _write_locks(run_dir: str | Path, data: dict) -> None:
    _locks_path(run_dir).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ── Speicherbereichs-Identitaet: stabile run_id pro run_dir (K1-Nachzug/P4) ─────
#
# `run_dir/run_id.json` traegt einen einmalig pro `run_dir` erzeugten, danach
# stabilen Identifier. Erzeugt/gelesen bei `Lobby.__init__` — jede weitere
# `Lobby(run_dir)`-Instanz auf demselben `run_dir` erhaelt dieselbe `run_id`
# (Kontrolle 06: nur `states_dir` wechselt, `run_dir` bleibt gleich -> `run_id`
# bleibt gleich -> Current-Save-Ref bleibt aufloesbar). Ein Aufruf mit einem
# ANDEREN `run_dir` (auch bei rein lokal wiederverwendeter Sequenznummer)
# erhaelt eine ANDERE `run_id` und kann so nie eine fremde Referenz umdeuten.
#
# Auflage 1 (kritisch): die Datei MUSS ein JSON-OBJEKT sein (`{"run_id": ...}`),
# NIE ein bare String/Liste — `review_countertests.py::test_01` scannt ALLE
# `*.json` unter der run_dir-Wurzel per `rglob` und ruft auf jedem geladenen
# Objekt `.get('v')` auf; eine nackte Liste/String wuerde dort mit
# `AttributeError` abbrechen (dieselbe Konvention wie bereits `lobby.json`/
# `lobby_messages.json`, s. `Lobby._read_messages`).


def _run_id_path(run_dir: str | Path) -> Path:
    return Path(run_dir) / "run_id.json"


def _run_id(run_dir: str | Path) -> str:
    """Liest die stabile `run_id` fuer `run_dir`, erzeugt sie bei Bedarf
    einmalig. Reine Dateiexistenz-Pruefung — kein Zwischenspeicher noetig, da
    jede `Lobby.__init__` und jeder `load_current_save`-Aufruf denselben
    stabilen Wert von der Platte liest."""
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


# ── Lobby ────────────────────────────────────────────────────────────────────


class Lobby:
    """Persistente Lobby-Mitgliedschaft (JSON-Datei), kein Dauerprozess."""

    def __init__(self, run_dir: str | Path):
        self.run_dir = Path(run_dir)
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
        # Top-Level-JSON-Objekt (nicht nackte Liste) halten: die harnesseigene
        # Review-Gegenprobe scannt ALLE `*.json` unter der run_dir-Wurzel per
        # `rglob` und ruft auf jedem geladenen Objekt `.get('v')` auf — eine
        # nackte Liste wuerde dort mit AttributeError abbrechen.
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

    # ── Oeffentlicher Lobby-Kanal (R7) — Leser-/Senderfilter: nur Lobby-Mitglieder ──
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

    # ── Chrononaut-Lock: kein gleichzeitiger Fortschritt an zwei Tischen ────────
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
        """Loescht die Sperre NUR, wenn sie tatsaechlich `expected_table_id`
        gehoert (R4c) — ein alter/fremder Tisch darf nie die Sperre eines
        inzwischen aktiven anderen Tisches freigeben."""
        locks = _read_locks(self.run_dir)
        if locks.get(chrononaut_id) == expected_table_id:
            del locks[chrononaut_id]
            _write_locks(self.run_dir, locks)

    def is_locked(self, chrononaut_id: str) -> str | None:
        return _read_locks(self.run_dir).get(chrononaut_id)


class ChrononautLockedError(RuntimeError):
    pass


class TableSizeError(ValueError):
    pass


class LeaderOnlySendError(PermissionError):
    pass


class VisibilityError(PermissionError):
    pass


class TableClosedError(PermissionError):
    """R4b: ein geschlossener (bereits abgeschlossener) Tisch darf weder senden
    noch einen weiteren Abschnitt abschliessen."""


class TablePendingError(TableClosedError):
    """K2/Auflage 1: ein Tisch mit einem noch OFFENEN Abschluss-Auftrag (ein
    `__plan.json` fuer ein ANDERES section_id ohne eigenes `__final`) ist fuer
    jeden weiteren Versand ebenso gesperrt wie ein bereits geschlossener
    Tisch. Echte Unterklasse von `TableClosedError` (nicht nur von
    `PermissionError`), damit das schmale `except (TableClosedError,
    ValueError)` der Oracle-Tests 04/05 diese Ablehnung faengt."""


# ── Table ────────────────────────────────────────────────────────────────────


@dataclass
class Table:
    table_id: str
    leader: str
    members: list[str]
    chrononaut_ids: dict[str, str]  # persona_key -> chrononaut_id
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

    def join_more(self, persona_key: str, chrononaut_id: str) -> bool:
        """Nachtraeglicher Beitrittsversuch (z. B. 6. Beitritt).

        NB-D/D2+D3: Nachbeitritt ist in diesem Slice AUSDRUECKLICH NICHT
        unterstuetzt (README: bewusste, spaetere Erweiterung) — diese Methode
        MUTIERT NIE (kein Ersatz-Tisch/-Spieler, kein Teil-Zustand) und
        liefert IMMER `False`. Die folgenden Pruefungen dienen nur der
        Nachvollziehbarkeit des jeweils zutreffenden Ablehnungsgrunds
        (voll/duplikat/geschlossen/lock-fremd/kein-Konsens-Beleg): selbst wenn
        Groesse/Duplikat/Lock/persistierter Status allesamt unkritisch waeren,
        fehlt in diesem Slice der legitimierende Konsens-/Offer-Beleg fuer
        einen ueber die urspruengliche Offer hinausgehenden Beitritt (D3) — der
        Aufruf bleibt deshalb in JEDEM Fall ein hartes `False` ohne Mutation.

        R4a/D2: der persistierte Tischstatus (Reload via `Table.load`, analog
        `submit_to_sl`) und `chrononaut_id`-Sperren an einem ANDEREN Tisch
        (`run_dir/locks.json`, Signatur unveraendert) werden dabei ebenfalls
        gegen den aktuellen Plattenstand geprueft, nicht nur gegen `self`."""
        persisted = Table.load(self.run_dir, self.table_id)
        if persisted.status == "closed":
            return False
        if len(self.members) >= TABLE_MAX_SIZE:
            return False
        if persona_key in self.members:
            return False
        locks = _read_locks(self.run_dir)
        held_by = locks.get(chrononaut_id)
        if held_by is not None and held_by != self.table_id:
            return False
        # D3: kein legitimierender Konsens-/Offer-Beleg fuer diesen Beitritt
        # in diesem Slice -> auch ohne jede der obigen Ablehnungsursachen
        # bleibt der Beitritt abgelehnt, ohne je etwas zu mutieren.
        return False


def create_table_from_offer_log(
    lobby: Lobby, table_id: str, offer_log_events: list[dict],
    chrononaut_ids: dict[str, str],
) -> tuple[Table | None, GroupDerivation]:
    """Leitet Gruppe/Leader aus dem Offer-Log ab und erzeugt bei Erfolg einen Tisch.

    Lehnt hart ab (gibt `(None, derivation)` zurueck, OHNE irgendetwas zu mutieren)
    wenn: `table_id` bereits existiert (R4d, kein Ueberschreiben von Datei/Verlauf),
    keine vollstaendige Offer, Gruppengroesse 0, Gruppengroesse > 5, ein Mitglied
    bereits per Chrononaut-Lock an einem anderen Tisch aktiv ist, ODER ein
    Mitglied in einem noch OFFENEN Abschluss-Auftrag eines beliebigen Tisches
    gebunden ist (K2-Nachzug/P1: `_member_bound_by_open_order` — die Bindung
    haengt an Plan-/Final-Dateiexistenz, NICHT am physischen Lock, der bereits
    vor `__final` freigegeben wird, s. `_resume_and_finalize`).
    """
    derivation = derive_group_and_leader(offer_log_events)
    if (lobby.run_dir / "tables" / f"{table_id}.json").exists():
        return None, derivation
    if derivation.leader is None or not derivation.members:
        return None, derivation
    size = len(derivation.members)
    if size < TABLE_MIN_SIZE or size > TABLE_MAX_SIZE:
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


# ── Leader-only-Send (COORDINATION-MODEL-FROZEN Punkt 3) ────────────────────────


def _table_has_final(run_dir: str | Path, table_id: str) -> bool:
    """Auflage 1: schliesst das schmale Crash-Fenster zwischen dem NEU
    vorgezogenen `__final`-Write und dem NACHFOLGENDEN `status=closed`-Persist
    (s. `complete_section`) — in diesem Fenster existiert bereits ein
    `__final`-Marker FUER DIESEN TISCH, aber der persistierte `status` ist
    (noch) nicht `closed`. Scannt alle `completion/*__final.json` (i. d. R.
    hoechstens einer pro Tisch, da ein bereits geschlossener Tisch keinen
    zweiten Abschluss-Zweig mehr eroeffnen kann, s. `complete_section` [3])
    nach `table_id`-Uebereinstimmung."""
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
    table: Table, actor_persona_key: str, sl_stub, turn_idx: int, text: str,
    origin_persona_key: str | None = None, origin_source: str | None = None,
    save_payload: dict | None = None,
) -> dict:
    """Transport fuehrt eine vom Leader freigegebene Nachricht aus — schreibt selbst
    nichts inhaltlich Neues. Nur `table.leader` darf ueberhaupt senden.

    R4b/NB-D/D1: ein bereits geschlossener Tisch darf nicht mehr senden — geprueft
    wird der PERSISTIERTE Status (Reload via `Table.load`), NICHT das ggf.
    veraltete in-memory `table.status`: ein vor Abschluss geladenes Table-Handle
    (z. B. aus einer frueheren Aufrufkette) darf einen inzwischen persistiert
    geschlossenen Tisch nicht wiederbeleben (Test 06). Ebenso wird die
    Lock-Eigentuemerschaft aller Mitglieder gegen den persistierten
    `locks.json`-Stand geprueft — ein Tisch, dessen Chrononaut-Sperren
    inzwischen einem ANDEREN Tisch gehoeren, darf nicht mehr senden, selbst wenn
    sein eigener `status` (noch) nicht `closed` waere.
    Auflage 1: zusaetzlich zu `status=="closed"` wird `_table_has_final(...)`
    geprueft — existiert bereits ein `__final`-Marker fuer DIESEN Tisch (auch
    wenn `status` im schmalen Crash-Fenster zwischen `__final`-Write und
    `status=closed`-Persist noch `active` waere), gilt der Tisch als gesperrt.
    K2/Auflage 1: zusaetzlich wird `_open_completion_order_for_table(...)`
    geprueft — bindet ein noch OFFENER Abschluss-Auftrag (`__plan.json` fuer
    ein ANDERES section_id ohne eigenes `__final`) diesen Tisch exklusiv, wird
    `TablePendingError` (echte `TableClosedError`-Unterklasse, faengt sich im
    `except (TableClosedError, ValueError)` der Oracles) geworfen — das ist
    die FRUEHESTE Grenze, an der ein neuer Abschnitt B auf demselben Tisch
    scheitert (Test 04/05 der K-Oracle).
    R7/NB-D: reload -> append -> persist AUF DEM PERSISTIERTEN Tisch — NIE das
    ggf. veraltete in-memory `table` als Voll-Snapshot zurueckschreiben (Test
    06): der neue Eintrag wird an den frisch geladenen `sl_log` angehaengt,
    persistiert, und die Aufrufer-Kopie (`table`) danach auf den neuen Stand
    nachgezogen. Persistiert sowohl die gesendete Leader-Nachricht (`text`)
    als auch die SL-Antwort, zusammen mit einem Herkunftsbeleg
    (`origin_persona_key`/`origin_source` — welche Persona-Entscheidung dies
    simuliert und aus welcher Fixture) und einer optionalen, GETRENNTEN
    strukturierten Save-Payload (`save_payload`), damit dynamischer
    Save-Inhalt nie in den Nachrichtentext hineingerechnet werden muss
    (Auflage 6)."""
    # Leader-Identitaet zuerst pruefen (Original-Test erwartet LeaderOnlySendError
    # fuer einen Nicht-Leader unabhaengig vom Tisch-Status), dann den geschlossenen
    # Zustand — ein bereits abgeschlossener Tisch soll dem LEADER selbst den
    # weiteren Versand verwehren, nicht einem sowieso schon unzulaessigen Akteur.
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
    result = sl_stub.turn(turn_idx, text)

    # NB-D/Reload-Append-Persist: frisch reloaden, NEUEN Eintrag an den
    # PERSISTIERTEN sl_log anhaengen, dann persistieren — nie `table.sl_log`
    # direkt mutieren und `table` selbst zurueckschreiben (das wuerde einen
    # ggf. veralteten Voll-Snapshot ueber den authoritativen Stand schreiben).
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
    # Aufrufer-Kopie auf den neuen authoritativen Stand nachziehen (R7).
    table.sl_log = current.sl_log
    table.table_messages = current.table_messages
    table.status = current.status
    return result


# ── Tisch-Absprachekanal (R7) — nur Mitglieder duerfen posten/lesen ─────────────


def post_table_message(table: Table, persona_key: str, text: str) -> dict:
    """NB-D/Auflage 3: geschlossene Tische nehmen auch im privaten
    Absprachekanal keine neuen Nachrichten mehr an — geprueft wird der
    PERSISTIERTE Status (Reload via `Table.load`), analog zu `submit_to_sl`
    (D1), damit auch hier ein veraltetes Handle einen geschlossenen Tisch
    nicht wiederbeleben kann. Auflage 1: zusaetzlich `_table_has_final(...)`
    (schliesst dasselbe schmale Crash-Fenster wie bei `submit_to_sl`).
    Zusaetzlich (Auflage/Report-Diskrepanz §4): Lock-Eigentuemerschafts-
    Pruefung, konsistent mit `submit_to_sl` — ein Tisch, dessen Chrononaut-
    Sperren inzwischen einem ANDEREN Tisch gehoeren, darf auch im privaten
    Absprachekanal nicht mehr senden.
    R7/NB-D: reload -> append -> persist AUF DEM PERSISTIERTEN Tisch, NIE das
    ggf. veraltete in-memory `table` als Voll-Snapshot zurueckschreiben — der
    neue Eintrag wird an den frisch geladenen `table_messages` angehaengt; die
    Aufrufer-Kopie wird danach nachgezogen (Test 06)."""
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


# ── Sichtfilter: Operator- vs. Persona-Ansicht (Auflage 3) ──────────────────────


def persona_view(table: Table, persona_key: str) -> dict:
    """Was eine Persona an IHREM Tisch sehen darf: identischer voller SL-Text (samt
    Leader-Nachricht + Herkunftsbeleg + Save-Payload) fuer alle Mitglieder, der
    private Tisch-Absprachekanal, die eigene Mitgliederliste, der Leader. KEIN
    operator_meta (Offer-Log-Rohdaten, Dissenter-Gruende, Locks) — das ist
    Operator-/Debug-Beleg, kein geteiltes Spielerwissen. Wirft, wenn persona_key
    nicht Mitglied ist (kein Fremd-Tisch-Einblick, gilt fuer beide Kanaele)."""
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
    """Voller Operator-/Debug-Beleg inkl. Offer-Log, Dissenter-Gruende, Chrononaut-
    Zuordnung. Fuer QA/End-Critic — NICHT an Personas ausliefern."""
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


# ── Completion-Idempotenz + Save/State-Rueckkehr (Konsistenzplan/Auflagen) ──────
#
# round_no/Section-ID-Mapping (siehe README.md fuer die ausfuehrliche Fassung):
#   Der Completion-Guard pro (chrononaut_id, section_id) ist die Schranke INNERHALB
#   der Schreibschleife: hoechstens einmal wird eine Guard-Datei geschrieben UND
#   persona_state.update_state() fuer dasselbe Mitglied aufgerufen. Der VOLLSTAENDIGE
#   Abschluss (`already_completed`, C1/Auflage 1) wird dagegen NICHT an den
#   Guard-Dateien festgemacht, sondern EINZIG am `completion/<section_id>__final.json`
#   -Marker, der erst nach der resumierbaren Finalisierung (Lock-Freigabe +
#   __final + status=closed, s. u.) existiert — s. `complete_section`-Docstring
#   fuer die vollstaendige Reihenfolge. Ein zweiter `complete_section()`-Aufruf mit
#   vorhandenen Guards aber OHNE `__final` gilt deshalb bewusst NICHT als
#   `already_completed`, sondern holt die Finalisierung nach (Retry-Fall, Test 04).
#   round_no fuer persona_state.update_state() ist NICHT die section_id (das waere
#   eine Typverwechslung: section_id ist ein global stabiler Story-Abschnitts-
#   Bezeichner, round_no ist ein persona-lokaler, monoton wachsender Zaehler).
#
#   R3 (Teilschreib-/Crash-Fall) + NB-C/Test08 (Ernte-Pinning): VOR der
#   Schreibschleife wird EINMALIG ein persistenter Abschluss-Auftrag
#   `completion/<section_id>__plan.json = {table_id, members: {persona_key:
#   {round_no, save}}}` geschrieben (existiert er bereits fuer DIESEN Tisch —
#   z. B. nach einem Retry — wird er UNVERAENDERT wiederverwendet, NICHT neu
#   berechnet; gehoert er einem ANDEREN Tisch, ist das eine Kollision, s.
#   `complete_section` [2]). Die volle geerntete Ernte (der v7-Block je
#   Mitglied, nicht nur ein Hash) wird hier PINNED: die Schreibschleife nutzt
#   IMMER `members_plan[pk]["save"]`/`["round_no"]`, NIE das (ggf. bei einem
#   abweichenden Retry-Aufruf andere) Funktionsargument `harvested_saves`
#   (kein Mischen zweier Ernten, Test 08). Die Schreibschleife ueberspringt
#   jedes Mitglied, das bereits eine Guard-Datei hat (kein zweiter
#   Rundenschritt fuer bereits geschriebene Mitglieder). `persona_state`s
#   EIGENES Anti-Stacking-Gate (`round_no <= rounds_played` -> No-op) bleibt
#   eine ZWEITE, unabhaengige Sicherung. Locks werden ERST NACH dem
#   vollstaendigen, konsistenten Schleifendurchlauf freigegeben (nicht pro
#   Mitglied waehrend der Schleife), DANN `__final.json` geschrieben, ERST
#   DANACH `status="closed"` persistiert (Frage 4/Konsistenzplan — NICHT mehr
#   closed-vor-final).


@dataclass
class CompletionResult:
    success: bool
    already_completed: bool
    written: bool
    members_completed: list[str]
    missing: list[str]
    reason: str


def _safe_component(value: str) -> str:
    return value.replace("/", "_")


# P2/NB-B,K2-Nachzug: strikte Section-ID-Grammatik — kollisionsfrei unter der
# obigen `_safe_component`-Normalisierung (die NUR "/" -> "_" ersetzt). Unter
# dieser Grammatik kann keine zulaessige `section_id` mehr auf denselben
# Dateinamen wie eine ANDERE zulaessige `section_id` abbilden (z. B. "chapter/
# one" vs. "chapter_one" — "/" ist schlicht nicht mehr erlaubt).
_SECTION_ID_RE = re.compile(r"^[A-Za-z0-9_-]+\Z")


def _completion_guard_path(run_dir: Path, chrononaut_id: str, section_id: str) -> Path:
    return run_dir / "completion" / f"{_safe_component(chrononaut_id)}__{_safe_component(section_id)}.json"


def _completion_plan_path(run_dir: Path, section_id: str) -> Path:
    return run_dir / "completion" / f"{_safe_component(section_id)}__plan.json"


def _completion_final_path(run_dir: Path, section_id: str) -> Path:
    """C1/Auflage 1+4: der EINZIGE `already_completed`-Nachweis — existiert
    ERST, nachdem Lock-Freigabe UND die volle Schreibschleife durchgelaufen
    sind (s. `complete_section`/`_resume_and_finalize`). Frage 4/Konsistenz-
    plan: `__final` wird VOR `status=closed` geschrieben (nicht mehr danach) —
    der Inhalt bindet `table_id`+`members`, damit ein fremder Tisch mit
    gleicher `section_id` niemals als Erfolg gilt (Test 07). Test-Zaehlfilter
    in `test_lobby_tables.py` muessen diese Datei wie `__plan.json` von der
    Pro-Mitglied-Guard-Zaehlung ausschliessen (Auflage 1)."""
    return run_dir / "completion" / f"{_safe_component(section_id)}__final.json"


def _open_completion_order_for_table(
    run_dir: Path, table_id: str, exclude_section_id: str | None = None,
) -> str | None:
    """K2: findet den `section_id` eines noch OFFENEN Abschluss-Auftrags fuer
    `table_id`, sonst `None`. Ein Auftrag fuer `section_id` gilt als OFFEN,
    wenn `completion/<section_id>__plan.json` existiert, `table_id` darin mit
    `table_id` uebereinstimmt, aber `completion/<section_id>__final.json`
    (noch) NICHT existiert. `exclude_section_id` blendet den gerade selbst
    bearbeiteten Auftrag aus (fuer den eigenen Retry-Pfad in
    `complete_section` [2], der denselben Auftrag legitim wiederaufnimmt)."""
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
    """P1/K2-Nachzug: `True`, wenn `chrononaut_id` Mitglied eines beliebigen
    noch OFFENEN Abschluss-Auftrags ist (`completion/<section>__plan.json`
    OHNE eigenes `completion/<section>__final.json`) — UNABHAENGIG vom
    physischen Lock-Zustand. Loest die Luecke, dass Locks pro Mitglied schon
    VOR `__final` freigegeben werden (s. `_resume_and_finalize` [5]): ein
    Mitglied, dessen Lock im Cleanup bereits fehlt, darf trotzdem nicht an
    einem NEUEN Tisch aufgenommen werden, solange sein urspruenglicher
    Abschluss-Auftrag noch offen ist.

    Auflage 2: die Chrononaut-IDs eines offenen Plans werden ueber
    `Table.load(run_dir, plan_data['table_id']).chrononaut_ids` abgeleitet —
    der referenzierte Tisch bleibt bis zum Final-Write ladbar (wird erst
    NACH `__final` auf `status=closed` umgeschrieben, s.
    `_resume_and_finalize`), daher jederzeit verfuegbar, solange der Auftrag
    offen ist. Iteriert ALLE offenen Plaene (nicht nur die eines bestimmten
    Tisches) — nach gueltigem `__final` ist ein Auftrag geschlossen und
    bindet nicht mehr (freie Neugruppierung bleibt erhalten)."""
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
    """C2/Auflage 2/K1: atomarer Versions-Commit (temp+rename) unter
    `current_saves/<persona_key>__versions/<seq>.json`. Die zurueckgegebene
    Sequenznummer wird dem Persona-State als Current-Save-Ref beigelegt (s.
    `_resume_and_finalize`) — DAS macht diese Version fuer `load_current_save`
    sichtbar, nicht ihre blosse Existenz. Diese Datei ist die fuer
    `save_sha256` im Completion-Guard MASZGEBLICHE Quelle (nicht die
    separate, VOR dem Versions-Commit geschriebene Direktdatei)."""
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
    run_dir: str | Path, persona_key: str, states_dir: str | Path | None = None,
) -> dict | None:
    """K1: liest den zuletzt VEROEFFENTLICHTEN AKTUELLEN Save fuer
    `persona_key` (verbatim geernteter v7-Block), falls vorhanden.

    Gemeinsame Veroeffentlichungsautoritaet: die Persona-State-Datei (atomar
    via `ps.save_state`) ist der EINZIGE Flip. Dieser Lader leitet `states_dir`
    ab (`run_dir.parent/"states"`, TmpEnv-Konvention — alle Oracle-/Test-
    Aufrufer nutzen ausschliesslich diese Konvention; interne Aufrufer koennen
    ihn weiterhin explizit uebergeben), laedt den State und gibt GENAU den
    darin per Current-Save-Ref (`_CURRENT_SAVE_REF_FIELD`) referenzierten
    Save zurueck — KEIN "hoechste Version"-Read. Fehlt der State (Persona hat
    in diesem run_dir noch nie einen Abschnitt abgeschlossen) oder traegt er
    (noch) keine Referenz, ist das Ergebnis `None`. Eine verwaiste (nicht
    referenzierte) Versionsdatei wird nie gelesen — nur ein erfolgreicher
    State-Flip macht eine Version sichtbar.

    K1-Nachzug/P4/Auflage 4: die Referenz ist ein JSON-Objekt
    `{"run_id": ..., "seq": ...}` — sie wird NUR aufgeloest, wenn
    `ref["run_id"] == _run_id(run_dir)` (Speicherbereichs-Bindung). Eine
    Referenz aus einem ANDEREN `run_dir` (selbst bei identischer, rein lokal
    wiederverwendeter Sequenznummer) deutet niemals einen Save in DIESEM
    `run_dir` um — sie loest zu `None` auf."""
    run_dir = Path(run_dir)
    if states_dir is None:
        states_dir = run_dir.parent / "states"
    try:
        state = ps.load_state(persona_key, states_dir=states_dir)
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
) -> tuple[list[str], dict[str, dict]]:
    """R1/Test 09: Erfolg NUR, wenn fuer JEDES Mitglied genau ein
    Ein-Figur-v7-Block (v==7) mit passender char_id vorliegt UND der geladene
    persona_state tatsaechlich zu `pk`/`table.chrononaut_ids[pk]` gehoert.
    Wird sowohl fuer die ERSTE Validierung (gegen das uebergebene Argument)
    als auch — Auflage 4 — fuer die RETRY-Validierung (gegen die gepinnte
    Ernte, s. `_resume_and_finalize`) verwendet, damit beide Pfade exakt
    dieselbe Pruefung durchlaufen."""
    missing: list[str] = []
    identity_states: dict[str, dict] = {}
    for pk in table.members:
        blk = harvest.get(pk)
        if blk is None:
            missing.append(pk)
            continue
        if blk.get("v") != 7:
            missing.append(pk)
            continue
        if save_lib.single_character_count(blk) != 1:
            missing.append(pk)
            continue
        cid = save_lib.block_char_id(blk)
        if cid != table.chrononaut_ids[pk]:
            missing.append(pk)
            continue
        try:
            state = ps.load_state(pk, states_dir=states_dir)
        except FileNotFoundError:
            missing.append(pk)
            continue
        if (state.get("persona_key") != pk
                or state.get("plays_char", {}).get("character_id") != table.chrononaut_ids[pk]):
            missing.append(pk)
            continue
        identity_states[pk] = state
    return missing, identity_states


def _resume_and_finalize(
    lobby: Lobby, table: Table, section_id: str, plan_data: dict,
    states_dir: str | Path, today: str,
    guard_paths: dict[str, Path], final_path: Path,
) -> CompletionResult:
    """Fuehrt die Schreibschleife [4] + resumierbare Finalisierung [5] fuer
    einen (neu gepinnten ODER wiederaufgenommenen) Abschluss-Auftrag aus.
    Gemeinsamer Pfad fuer den ERSTEN Versuch und jeden Retry — beide muessen
    identisch (Guard-Skip, gepinnte Ernte, Reihenfolge) ablaufen (Test 04/08/09).
    """
    run_dir = lobby.run_dir
    members_plan: dict[str, dict] = plan_data.get("members", {})

    # Auflage 4: Schritt-[3]-Validierung ERNEUT, aber gegen die GEPINNTE Ernte
    # (nicht gegen ein evtl. abweichendes Funktionsargument) — kein Mischen
    # (Test 08). Ein first-attempt-Aufruf validiert hier effektiv ein zweites
    # Mal dieselben, gerade selbst gepinnten Daten (billig, aber konsistent).
    pinned_harvest = {pk: entry.get("save") for pk, entry in members_plan.items()}
    missing, identity_states = _validate_harvest(table, pinned_harvest, states_dir)
    if missing:
        return CompletionResult(
            success=False, already_completed=False, written=False,
            members_completed=[], missing=missing,
            reason=f"gepinnter Abschluss-Auftrag fuer {section_id!r} ist inkonsistent/unvollstaendig: {missing}.",
        )

    current_saves_dir = run_dir / "current_saves"
    current_saves_dir.mkdir(exist_ok=True)

    # [4]
    written_any = False
    for pk in table.members:
        cid = table.chrononaut_ids[pk]
        guard_path = guard_paths[pk]
        if guard_path.exists():
            # R3: dieses Mitglied wurde in einem frueheren (abgebrochenen) Versuch
            # bereits vollstaendig geschrieben — kein zweiter Rundenschritt.
            continue

        round_no = members_plan[pk]["round_no"]
        blk = pinned_harvest[pk]

        # K2/Recovery-Guard (Defense-in-Depth): der Auftrag pinnt die zum
        # Pin-Zeitpunkt aktuelle Current-Save-Ref je Mitglied
        # (`expected_prev_ref`, s. `complete_section`). Weicht der JETZT
        # tatsaechlich veroeffentlichte Stand davon ab, OBWOHL dieses Mitglied
        # noch keine eigene Guard-Datei hat, MUSS unterschieden werden: ein
        # frueherer (abgebrochener) Versuch GENAU DIESES Auftrags kann den
        # State-Flip bereits erfolgreich durchgefuehrt haben, bevor NUR der
        # Guard-Write scheiterte (Test 09 der Re-Review) — das ist sicher
        # (derselbe gepinnte Block wurde bereits korrekt veroeffentlicht, nur
        # die Guard-Datei fehlt noch nach). Referenziert der aktuelle Stand
        # dagegen einen ANDEREN Save-Inhalt als den hier gepinnten, hat ein
        # FREMDER, neuerer Abschluss dieses Mitglied fortgeschrieben, seit
        # dieser Auftrag gepinnt wurde — kein Ueberschreiben einer neueren
        # Generation durch ein Journal von gestern.
        expected_prev_ref = members_plan[pk].get("expected_prev_ref")
        actual_prev_ref = identity_states[pk].get(_CURRENT_SAVE_REF_FIELD)
        if expected_prev_ref != actual_prev_ref:
            referenced = load_current_save(run_dir, pk, states_dir=states_dir)
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
            # Der eigene, bereits gepinnte Block wurde schon veroeffentlicht
            # (Save+State-Flip erfolgreich) — nur die Guard-Datei fehlt noch.
            # Kein zweiter Save-/State-Write; Guard direkt anhand des bereits
            # referenzierten (aktuellen) Standes nachholen.
            # K1-Nachzug/P4: `actual_prev_ref` ist an dieser Stelle garantiert
            # ein `{run_id, seq}`-Objekt aus DIESEM `run_dir` — `referenced`
            # (oben, via `load_current_save`) loest nur dann != None auf,
            # wenn die Referenz bereits als gueltiges, an dieses `run_dir`
            # gebundenes Objekt vorlag.
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

        # R1/C2 (Auflage 2, Test 05): geernteten v7-Block VERBATIM als
        # aktuellen Personal-Save ablegen (reines json.dumps, kein
        # Wrapperfeld — Test 01 prueft Dict-Gleichheit). ERST die Direktdatei
        # schreiben (das ist der von Test 05 abgefangene Riss-Punkt), DANACH
        # der atomare Versions-Commit — UND ERST NACH BEIDEN Save-Schreibvor-
        # gaengen `ps.save_state` (Frage 3/Konsistenzplan): reisst der
        # Direkt-Save-Write ab, bleiben Save UND State fuer dieses Mitglied
        # unveraendert (kein "alter Save + bereits fortgeschriebener State").
        direct_path = current_saves_dir / f"{pk}.json"
        direct_path.write_text(json.dumps(blk, ensure_ascii=False, indent=2), encoding="utf-8")
        version_path = _write_current_save_version(current_saves_dir, pk, blk)
        save_sha256 = hashlib.sha256(version_path.read_bytes()).hexdigest()
        new_seq = int(version_path.stem)

        state = ps.update_state(
            identity_states[pk], round_no=round_no,
            kernereignis=f"Abschnitt {section_id} am Tisch {table.table_id} abgeschlossen.",
            now=today, datum=today, mission=section_id,
        )
        # K1/K1-Nachzug: Current-Save-Ref wird IM SELBEN State-Objekt gesetzt,
        # das gleich ueber `ps.save_state` atomar veroeffentlicht wird —
        # Save-Version und State-Fortschritt werden so als EIN Paar sichtbar
        # (der einzige Flip). Die Referenz traegt zusaetzlich die `run_id`
        # dieses Speicherbereichs (P4) — nur ein Ref mit passender `run_id`
        # loest spaeter ueberhaupt einen Save auf (s. `load_current_save`).
        state[_CURRENT_SAVE_REF_FIELD] = {"run_id": _run_id(run_dir), "seq": new_seq}
        ps.save_state(pk, state, states_dir=states_dir)

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

    # [5] R3/R4/C1 (Frage 4/Konsistenzplan): Locks erst NACH dem
    # vollstaendigen, konsistenten Schleifendurchlauf freigeben (nicht pro
    # Mitglied waehrend der Schleife) — DANN erst `__final.json` schreiben —
    # ERST DANACH `status="closed"` persistieren (NEUE Reihenfolge: Locks ->
    # __final -> closed, nicht mehr closed-vor-final). `release_chrononaut`
    # ist selbst idempotent (loescht nur bei Eigentuemer-Match, s. dort) — ein
    # Retry dieses Blocks nach einem Crash GENAU HIER (Test 04) ist deshalb
    # sicher wiederholbar.
    for pk in table.members:
        lobby.release_chrononaut(table.chrononaut_ids[pk], table.table_id)
    final_path.write_text(
        json.dumps({
            "section_id": section_id, "table_id": table.table_id,
            "members": list(table.members),
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    # Auflage 2 (kritisch): den RELOADETEN persistierten Tisch mit
    # `status=closed` persistieren, NIE das `table`-Funktionsargument selbst
    # — sonst Totalverlust von `sl_log`/`table_messages`, falls der Aufrufer
    # sein in-memory-Objekt aus irgendeinem Grund nicht synchron gehalten hat
    # (test_7_message_channels' drei-Turn-sl_log-Assertion nach Abschluss).
    persisted = Table.load(run_dir, table.table_id)
    persisted.status = "closed"
    persisted.persist()
    table.status = "closed"  # Aufrufer-Kopie nachziehen (kein Re-Persist).

    return CompletionResult(
        success=True, already_completed=False, written=written_any,
        members_completed=list(table.members), missing=[],
        reason="Abschnitt vollstaendig abgeschlossen, Saves/States deponiert.",
    )


def complete_section(
    lobby: Lobby, table: Table, section_id: str,
    harvested_saves: dict[str, dict], states_dir: str | Path, today: str = "2026-09-21",
) -> CompletionResult:
    """Wertet eine Save-Ernte (N v7-Bloecke, einer pro Mitglied) fuer `section_id` aus.

    Bleibt die interne, NACHGELAGERTE Persistenz-/Finalisierungsstufe HINTER
    dem bereits validierten Ereignis — `section.run_section` prueft den
    Abschluss-Marker VOR diesem Aufruf; `complete_section` selbst kennt kein
    Marker-Konzept (Direktaufrufe der Gegenproben/Test 09 uebergeben gueltige
    Saves ohne Marker und muessen weiterhin erfolgreich sein).

    Kombinierte Pruef-/Ablaufreihenfolge (Frage 4/Konsistenzplan, C1+D1):
      [1] `__final.json`-Inhalt fuehrt `table_id`+`members` (NB-B/C, Test 07):
          existiert er und `table_id` stimmt mit DIESEM Tisch ueberein ->
          `already_completed` (der EINZIGE Nachweis, NICHT schon bei
          vollstaendigen Mitglieder-Guards). Stimmt `table_id` NICHT ueberein
          (fremder Tisch mit gleicher `section_id`) -> Kollision, harter
          Reject (`success=False`, KEIN Write, KEIN "Erben" eines fremden
          Abschlusses).
      [2] Existiert noch kein `__final`, aber bereits ein Abschluss-Auftrag
          (`__plan.json`, mit `table_id`+gepinnter Ernte) fuer (table,
          section) -> Recovery: fremder `table_id` im Auftrag -> ebenfalls
          Kollision-Reject; eigener `table_id` -> `_resume_and_finalize` holt
          Schreibschleife/Finalisierung nach (Test 04: closed-vor-final wird
          nachgeholt; Test 08: gepinnte Ernte, kein Mischen).
      [3] Weder `__final` noch `__plan` fuer DIESE section: persistierter
          `status=="closed"` (aus einem ANDEREN, bereits abgeschlossenen
          Auftrag desselben Tisches) -> unzulaessiger neuer Zweig, Reject.
          Reload-basierte Lock-Pruefung auf dem PERSISTIERTEN Stand (NB-D/
          R4+R6), analog `submit_to_sl`.
      [4] Erster Versuch: Missing-/Identitaets-/`v==7`-Validierung GEGEN DAS
          ARGUMENT `harvested_saves`; bei Erfolg wird der Abschluss-Auftrag
          EINMALIG gepinnt (`table_id` + je Mitglied `round_no`+voller
          v7-Block + `expected_prev_ref`/K2-Recovery-Guard) und
          `_resume_and_finalize` uebernimmt Schreibschleife + Finalisierung.

    K2/Auflage 1 (zwischen [2] und [3]): ein noch OFFENER Abschluss-Auftrag
    fuer ein ANDERES `section_id` desselben Tisches bindet diesen Tisch
    exklusiv — auch ein DIREKTER `complete_section`-Aufruf (nicht nur
    `submit_to_sl`/`post_table_message`) wird dafuer hart abgelehnt
    (`success=False`, KEIN Write).

    P2/Auflage 3 (vor [1]): `section_id` muss der strikten Grammatik
    `[A-Za-z0-9_-]` genuegen — der Reject sitzt HIER (nicht nur in
    `section.run_section`), damit auch ein DIREKTER `complete_section`-Aufruf
    (der `run_section` umgeht) ein unzulaessiges `section_id` frueh
    kontrolliert ablehnt (`success=False`, KEIN Write, keine Datei).
    """
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

    # [1] P2/Auflage 3(b): `already_completed` NUR bei table_id UND section_id
    # Uebereinstimmung — verhindert, dass ein `__final` unter einem (durch
    # `_safe_component` normalisierten) kollidierenden Dateinamen faelschlich
    # als Abschluss fuer ein ANDERES `section_id` gilt (kein "Erben" von
    # `chapter/one` durch `chapter_one`; unter der neuen Grammatik [oben]
    # physisch nicht mehr erreichbar, bleibt aber als Verteidigungslinie
    # gegen jede sonstige `_safe_component`-Kollision aktiv).
    if final_path.exists():
        try:
            final_data = json.loads(final_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            final_data = {}
        if final_data.get("table_id") == table.table_id and final_data.get("section_id") == section_id:
            # Fokus 4/Fault-Matrix (status_not_closed=0): `__final` ist die
            # EINZIGE Abschluss-Autoritaet — `status=closed` wird idempotent
            # daraus ABGELEITET/nachgezogen, auch in diesem
            # `already_completed`-Kurzschluss (nicht nur beim ERSTEN
            # Finalisierungsdurchlauf in `_resume_and_finalize`). Deckt den
            # Crash-Zeitpunkt "__final bereits geschrieben, status=closed noch
            # nicht persistiert" ab, ohne einen zweiten, widersprechenden
            # Status-Spiegel einzufuehren.
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

    # [2]
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
        return _resume_and_finalize(
            lobby, table, section_id, plan_data, states_dir, today, guard_paths, final_path,
        )

    # [2.5] K2/Auflage 1: ein offener Abschluss-Auftrag fuer ein ANDERES
    # section_id desselben Tisches bindet ihn exklusiv — kein neuer Zweig
    # (auch nicht per Direktaufruf) auf einem Tisch mit unfinalisiertem
    # Auftrag.
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

    # [3] NB-D/R4+R6: PERSISTIERTER (nicht der ggf. veraltete in-memory)
    # Tisch-Status + Lock-Eigentuemerschaft schuetzen den Completion-Pfad
    # genauso wie `submit_to_sl` (s. dort). Ein alter, per ANDERER section_id
    # bereits geschlossener Tisch darf keinen neuen Zweig ohne bestehenden
    # eigenen Auftrag eroeffnen.
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

    # [4] Erster Versuch: Validierung gegen das uebergebene Argument.
    missing, identity_states = _validate_harvest(table, harvested_saves, states_dir)
    if missing:
        return CompletionResult(
            success=False, already_completed=False, written=False,
            members_completed=[], missing=missing,
            reason=f"fehlende/falsch zugeordnete/falsch identifizierte Saves fuer: {missing} — kein Abschluss.",
        )

    # Frage 2/Konsistenzplan: Abschluss-Auftrag EINMALIG vor der
    # Schreibschleife pinnen — `table_id` + je Mitglied `round_no` UND die
    # volle Ernte (der v7-Block selbst, nicht nur ein Hash) — damit ein
    # Retry NIE das (ggf. abweichende) Funktionsargument mischt (Test 08).
    # K2/Recovery-Guard: zusaetzlich die zum Pin-Zeitpunkt aktuelle
    # Current-Save-Ref je Mitglied als `expected_prev_ref` pinnen — ein
    # spaeterer Retry darf diesen Auftrag nur ausfuehren, wenn der dann
    # tatsaechlich veroeffentlichte Stand noch mit dieser erwarteten
    # Vorgaengergeneration uebereinstimmt (s. `_resume_and_finalize`).
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

    return _resume_and_finalize(
        lobby, table, section_id, plan_data, states_dir, today, guard_paths, final_path,
    )


def return_to_lobby(lobby: Lobby, table: Table) -> None:
    """Rueckkehr in die Lobby nach Abschluss: Locks sind bereits in
    complete_section() freigegeben; hier nur sicherstellen, dass alle Mitglieder
    weiterhin als Lobby-Mitglieder gefuehrt werden."""
    for pk in table.members:
        lobby.join(pk)
