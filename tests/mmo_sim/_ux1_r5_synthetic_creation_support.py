#!/usr/bin/env python3
"""
tests/mmo_sim/_ux1_r5_synthetic_creation_support.py — W19/F03 (ZEITRISS
Terminal UX-1, R5): gemeinsamer Fake-SL-Baustein fuer eine ENDLICHE
synthetische Erschaffung bis zu einem gueltigen v7-Save UEBER DEN ECHTEN
Erschaffungsvertrag (`ui/tui.py:_cmd_new_or_switch_character` ->
`core/creation_service.run_admitted_creation_dialog`), NICHT durch direktes
Speichern/Save-Injektion.

Neues Testartefakt, keine Produktdatei. Erweitert das VORHANDENE
`SmartGmServer`-Muster (`e2e_real_subprocess_dialog.py`: ein echter
Loopback-HTTP-Server an der aeusseren GM-/SL-Transportgrenze, inhaltsgebunden
statt blind call-zaehlend) um GENAU EINEN zusaetzlichen, ebenfalls
inhaltsgebundenen Zweig: eine Erschaffungsanfrage wird an ihrer -- in
`ui/tui.py` hartkodierten, unveraenderten -- Eroeffnungszeile erkannt
(`CREATION_SIGNATURE` in der ERSTEN Nachricht des Chats), beantwortet erst
mit EINER SL-Frage, danach (ab dem naechsten Austausch IM SELBEN Chat) mit
einem gueltigen, strukturell schema-konformen v7-Save -- endlich, keine
Endlosschleife. Jede andere Anfrage faellt unveraendert an dieselbe
Spiel-/Abschlusslogik wie `SmartGmServer` (Debrief-Embedding +
Abschlussmarker, `domain.zeitriss.saves`/`policy.COMPLETION_MARKER`).

Restart-Sicherheit (Pause/Prozessende -> neuer, separater Prozess):
JEDE Entscheidung (Erschaffungsfrage vs. -save, Spielzug vs. Abschluss)
wird ausschliesslich aus dem im Request-Body enthaltenen Nachrichtenverlauf
abgeleitet (`len(messages)`, eingebettete v7-Bloecke in den `user`-Nachrichten)
-- NIE aus einem lokalen, prozessgebundenen Call-Zaehler. `GmOwuiTransport`
rekonstruiert bei einem neuen Prozess ueber `agent_mp/sl_client.py:SLSession.
from_history()` denselben Chat (gleiche `chat_id`, voller Verlauf) aus der
lokal persistierten `sl_history.jsonl` -- ein frischer `CreationCapableSmartGmServer`
(neue Instanz, leerer Prozessspeicher) trifft dadurch GENAU DIESELBE
Entscheidung wie der Server, der den Chat begonnen hat.

R7/W27 (Generalbefund R6P01, BRIEF-W27.md): ein FREIER Harness
(`manual_offline_harness.py`) kennt beim Start nur die eigene `leader_id`
-- ob/wen T spaeter ueber 'l <id> ...' einlaedt, ist zu diesem Zeitpunkt
unbekannt. Ein beim Start fest gesetzter `table_id`/`section_id` (Solo-
Formel) adressiert nach einer Einladung (2+3, `ui/tui.py:4197`: `local-
<leader>-<sortierte invited_ids>`) oder nach einer zweiten Runde
(`core/store.py:create_table_from_offer_log`: generationsweise
hochgezaehlte Kennung `<table_id>__2`, ...) den FALSCHEN Tisch --
`completion_marker_matches` lehnt den Marker am echten Tisch zu Recht ab
(empirisch belegt in `evidence/own/marker_probe.py` der R6-Generalreview).
`CreationCapableSmartGmServer` unterstuetzt deshalb zusaetzlich einen
DYNAMISCHEN Modus (`table_id=None, section_id=None` + `leader_id`/
`run_dir`): `resolve_own_open_table_id()` liest AUSSCHLIESSLICH den
eigenen, bereits von PRODUKTIONSCODE persistierten Zustand unter
`run_dir/tables/*.json` (derselbe Pfad wie `core/store.py:Table.persist`,
`run_dir` == `data_dir/"run"` wie `scripts/mmo_sim.py` ihn an die TUI
uebergibt) -- kein Raten, kein 'neuestes Tischfile', bei Mehrdeutigkeit
klarer Fehler statt Annahme (s. Funktionsdocstring unten). Bestehende
Aufrufer mit FESTEN `table_id`/`section_id` (R5/R6-Journey-Tests, die
ihre Gast-Tokens selbst waehlen und den `table_id` deshalb legitim
testseitig vorausberechnen duerfen, s. `_a24_local_support.
compute_table_id`) bleiben vollstaendig unveraendert -- der dynamische
Modus ist eine reine Erweiterung, kein Ersatz."""
from __future__ import annotations

import hashlib
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _full_v7_fixture import full_v7_save  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER  # noqa: E402
from mmo_sim.domain.zeitriss.save_validation import validate_structure  # noqa: E402


class NoOwnTableYetError(RuntimeError):
    """R7/W27: kein eigener Tisch unter `run_dir/tables/*.json` gefunden --
    der echte Produktionscode persistiert den Tisch VOR dem ersten GM-Call
    dieser Runde (`core/store.py:Table.persist`, vor `ui/tui.py:
    _run_table_round`); dieser Fehler bedeutet, dass die dynamische
    Ableitung zu frueh (vor der echten Tischanlage) aufgerufen wurde --
    kein Fallback/Raten, klarer Stopp."""


class AmbiguousOwnTableError(RuntimeError):
    """R7/W27: mehr als ein eigener, noch nicht geschlossener Tisch
    gefunden -- echte Mehrdeutigkeit (z.B. zwei parallel offene
    Generationen). Kein 'neuestes Tischfile' raten (Brief-Pflicht),
    sondern klarer Fehler/Stopp."""


def resolve_own_open_table_id(run_dir: "str | Path", leader_id: str) -> str:
    """R7/W27 (Generalbefund R6P01): liefert den TATSAECHLICHEN eigenen
    `table_id` -- gelesen AUSSCHLIESSLICH aus dem bereits vom echten
    Produktionscode persistierten Zustand des eigenen `run_dir`
    (`core/store.py:Table.persist`, Pfad `run_dir/tables/<table_id>.json`;
    `run_dir` ist identisch zu `data_dir/"run"`, s. `scripts/mmo_sim.py`).
    Kein Raten, keine feste Solo-Annahme, keine Abkuerzung.

    Kandidat: `leader == leader_id` (der eigene Teilnehmer ist in diesem
    Harness IMMER Leader seines eigenen lokalen Tisches, nie Gast eines
    fremden Leaders -- Solo/2+3/zweite Runde aendern nur den Gaesteteil
    des Namensraums bzw. die Generation, s. `ui/tui.py:_cmd_local_round`
    `table_id = f"local-{leader_id}" [+ "-" + sortierte invited_ids]`,
    `core/store.py:create_table_from_offer_log` generationsweise
    hochgezaehlte Kennung `<table_id>__2`, ... nach Abschluss einer
    vorigen Runde) UND `status != "closed"` UND KEIN zugehoeriges
    `run_dir/completion/<table_id>-section__final.json` (zweite,
    unabhaengige Bestaetigung derselben 'noch offen'-Aussage, Pfadformel
    identisch zu `core/store.py:_completion_final_path`).

    Genau EIN Treffer -> dessen `table_id`. Null Treffer ->
    `NoOwnTableYetError` (zu frueh aufgerufen, vor der echten Tischanlage).
    Mehr als ein Treffer -> `AmbiguousOwnTableError` (kein 'neuestes
    Tischfile'-Raten, sondern klarer Stopp -- Brief-Pflicht)."""
    run_dir = Path(run_dir)
    tables_dir = run_dir / "tables"
    candidates: list[str] = []
    if tables_dir.is_dir():
        for table_path in sorted(tables_dir.glob("*.json")):
            try:
                data = json.loads(table_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            if data.get("leader") != leader_id:
                continue
            if data.get("status") == "closed":
                continue
            table_id = data.get("table_id")
            if not table_id:
                continue
            final_path = run_dir / "completion" / f"{table_id}-section__final.json"
            if final_path.exists():
                continue
            candidates.append(table_id)
    if not candidates:
        raise NoOwnTableYetError(
            f"Kein offener eigener Tisch fuer leader_id={leader_id!r} unter "
            f"{tables_dir} gefunden -- der echte Tisch muss vor der ersten "
            "Abschlussentscheidung real angelegt sein (Produktweg), kein Raten."
        )
    if len(candidates) > 1:
        raise AmbiguousOwnTableError(
            f"Mehrdeutiger eigener Tisch fuer leader_id={leader_id!r}: "
            f"{sorted(candidates)} -- kein erratenes 'neuestes Tischfile', "
            "klarer Stopp statt Annahme."
        )
    return candidates[0]


# Exakte Teilzeichenkette der in `ui/tui.py:_cmd_new_or_switch_character`
# hartkodierten, unveraenderten Erschaffungs-Eroeffnungszeile ("Ich moechte
# einen neuen Chrononauten erschaffen. Fuehre mich Schritt fuer Schritt
# durch die Erschaffung.") -- JEDE frische Erschaffung (erste UND jede
# weitere bewusst neue Zusatzfigur derselben Person) beginnt mit genau
# dieser Zeile, unabhaengig von `onboarding_key`/Generation.
CREATION_SIGNATURE = "Chrononauten erschaffen"

CREATION_QUESTION = (
    "[SYNTHETISCHE SL-ERSCHAFFUNG -- Fake-SL an der Transportgrenze, KEINE echte "
    "Spielleitung/Liveprobe] Welche Grundausstattung und welchen Rufnamen waehlst du "
    "fuer deinen ersten Einsatz als Chrononaut?"
)


def creation_char_id(chat_id: str) -> str:
    """Deterministisch aus der (clientseitig erzeugten, aber je Chat
    stabilen) `chat_id` abgeleitet -- reine Funktion, kein mutabler
    Serverzustand noetig, dieselbe `chat_id` liefert nach einem Neustart
    (Prozessgrenze) wieder DIESELBE char_id (kein Zweit-/Ersatzsave)."""
    digest = hashlib.sha1(chat_id.encode("utf-8")).hexdigest()[:10]
    return f"chrono-synth-{digest}"


def synthetic_creation_save(chat_id: str, callsign: str = "SYN") -> dict:
    """R12 Savegate (B1, 02_TESTVERTRAG.md): beide v7-Schemas muessen VOR
    Annahme passen -- der alte Minimalblock (nur 4 Root-Felder, Root-Key
    `_fixture_note` NICHT im Export-Schema erlaubt, Figur fehlten alle
    uebrigen Export-Pflichtfelder) scheiterte an BEIDEN Schemas, sobald er
    den echten `save_validation.validate_structure`-Vollschemapfad
    erreichte. `full_v7_save` liefert denselben synthetischen Block,
    jetzt vollstaendig schemakonform, mit IDENTISCHER Identitaet
    (char_id/name/callsign/save_id unveraendert). Die bisherige
    `_fixture_note`-Testannotation lebt nur noch hier im Docstring
    (SYNTHETISCH, W19 F03 Fake-SL, GM-/Persona-Transportgrenze, keine
    echte Spielleitung/Liveprobe -- entstanden ueber den echten
    Erschaffungsdialog, kein direktes Speichern/keine Save-Injektion),
    nicht mehr als Root-Key im Save selbst (additionalProperties:false
    am Export-Schema-Root verbietet unbekannte Zusatzschluessel, analog
    `_a24_local_support.end_save_for`/W61).

    Post-Override-Validierung (02_TESTVERTRAG.md 'Positive / negative
    Fixtureeingaenge'): der final zurueckgegebene Block wird HIER, NACH
    jedem Override, gegen BEIDE unveraenderten v7-Schemas geprueft -- ein
    kuenftiger Override, der das Schema wieder verletzt, faellt sofort
    hier auf, nicht erst drei Korrekturversuche spaeter im echten
    Erschaffungsdialog."""
    char_id = creation_char_id(chat_id)
    block = full_v7_save(
        char_id, name="Synthetischer Chrononaut", callsign=callsign,
        save_id=f"synthetic-{char_id}-001",
    )
    report = validate_structure(block)
    assert report.valid, (
        f"synthetic_creation_save({chat_id!r}) ist NICHT gegen beide v7-Schemas "
        f"gueltig (total_error_count={report.total_error_count}): {report.errors}"
    )
    return block


class _CreationCapableHandler(BaseHTTPRequestHandler):
    def log_message(self, *_a):
        return

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b""
        try:
            body = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            body = {}
        messages = body.get("messages") or []
        opening = ""
        if messages and isinstance(messages[0], dict):
            opening = messages[0].get("content") or ""
        if CREATION_SIGNATURE in opening:
            content = self._creation_response(body, messages)
            self.server.creation_calls.append(body)  # type: ignore[attr-defined]
        else:
            content = self._gameplay_response(messages)
            self.server.calls.append(body)  # type: ignore[attr-defined]
        self._respond(content)

    def _creation_response(self, body: dict, messages: list) -> str:
        """Endlich, inhaltsgebunden -- UND mehrfachfaehig fuer DIESELBE
        Person: `ui/tui.py` bindet den Erschaffungs-GM-Transport ueber
        `onboarding-<participant_id>` (NICHT ueber die jeweilige
        Generation) -- eine bewusst NEUE Zusatzerschaffung ('neu') teilt
        sich daher denselben, bereits bestehenden Chat/Verlauf mit jeder
        vorherigen Erschaffung dieser Person. Entscheidend ist deshalb
        NICHT `len(messages)`, sondern der INHALT der JEWEILS LETZTEN
        `user`-Nachricht: eine frische Erschaffung (egal welche Generation)
        sendet als naechste Nachricht IMMER wortgleich dieselbe, in
        `ui/tui.py` hartkodierte Eroeffnungszeile (`CREATION_SIGNATURE`) --
        das bekommt EINE Frage; jede andere letzte Nachricht ist die freie
        Antwort eines Menschen auf diese Frage und bekommt einen gueltigen
        v7-Save. Restart-sicher (volle Historie aus dem Request-Body, kein
        lokaler Zaehler). Die char_id wird zusaetzlich an die Anzahl der
        bisher in diesem Chat gesehenen Eroeffnungszeilen gebunden (1. =
        erste Erschaffung, 2. = erste Zusatzerschaffung, ...) -- dieselbe
        Person bekommt dadurch bei einer bewusst neuen Erschaffung eine
        ECHT ANDERE Figur statt eines Konflikts mit der bereits bestehenden."""
        user_msgs = [m for m in messages if isinstance(m, dict) and m.get("role") == "user"]
        last_text = user_msgs[-1].get("content", "") if user_msgs else ""
        if CREATION_SIGNATURE in last_text:
            return CREATION_QUESTION
        attempt_no = sum(1 for m in user_msgs if CREATION_SIGNATURE in (m.get("content") or ""))
        chat_id = str(body.get("chat_id") or "unknown-chat")
        save_block = synthetic_creation_save(f"{chat_id}#{attempt_no}")
        return (
            "[SYNTHETISCHE SL-ERSCHAFFUNG -- Fake-SL, keine echte Liveprobe] Deine "
            "Erschaffung ist damit abgeschlossen.\n```json\n"
            + json.dumps(save_block, ensure_ascii=False) + "\n```"
        )

    def _gameplay_response(self, messages: list) -> str:
        """UNVERAENDERTES `SmartGmServer`-Prinzip (inhaltsgebundener
        Abschluss, kein blinder Call-Zaehler-Erfolg), aber restart-sicher
        aus dem VOLLEN, im Request-Body mitgelieferten Verlauf abgeleitet
        (nicht aus einem lokalen, pro Prozess zuruecksetzenden Zaehler):
        jede `user`-Nachricht dieses Chats wird auf eingebettete v7-Bloecke
        durchsucht (`core/runtime.py:_embed_json_block`, Leader-Ankerzug);
        sobald mindestens `complete_after` eigene Nutzertextzeilen UND
        mindestens ein echter v7-Block gesehen wurden, wird der Abschluss
        samt echo-gebundenem Debrief gesendet."""
        user_texts = [
            m.get("content", "") for m in messages
            if isinstance(m, dict) and m.get("role") == "user"
        ]
        seen_blocks: dict[str, dict] = {}
        for txt in user_texts:
            for blk in zeitriss_saves.extract_all_saves(txt):
                cid = zeitriss_saves.block_char_id(blk)
                if cid:
                    seen_blocks[cid] = blk
        n = len(user_texts)
        complete_after = self.server.complete_after  # type: ignore[attr-defined]
        if n >= complete_after and seen_blocks:
            debrief = "\n".join(
                f"```json\n{json.dumps(b, ensure_ascii=False)}\n```" for b in seen_blocks.values()
            )
            return (
                f"{debrief}\n{COMPLETION_MARKER} table_id={self.server.table_id} "  # type: ignore[attr-defined]
                f"section_id={self.server.section_id}"  # type: ignore[attr-defined]
            )
        return f"Szene {n}: Ihr steht bereit und beobachtet die Umgebung. Was tut ihr als Naechstes?"

    def _respond(self, content: str) -> None:
        payload = {"choices": [{"message": {"content": content}}], "usage": {}, "sources": []}
        data = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class CreationCapableSmartGmServer(HTTPServer):
    """Echter Loopback-HTTP-Server (127.0.0.1, zufaelliger freier Port) --
    EIN Fake an der GM-/Persona-Transportgrenze fuer den GESAMTEN Prozess
    (Erschaffung UND Spiel), s. Moduldocstring. `.creation_calls` und
    `.calls` sind BEWUSST getrennte Belegeimer (Erschaffung vs. Spiel/
    Bestandsfixtur-Spiellogik), damit ein Testbeleg beide Kategorien nie
    vermischt (Brief-Auflage "Erschaffung-vs-Bestandsfixture im Beleg klar
    trennen").

    Zwei Modi fuer `table_id`/`section_id` (R7/W27, Generalbefund R6P01):
    - FEST (beide als String uebergeben, wie bisher): unveraendertes
      Verhalten -- fuer bereits bestehende, vollstaendig skriptierte Tests,
      die ihre Gast-Tokens selbst waehlen und den `table_id` deshalb
      legitim testseitig vorausberechnen duerfen.
    - DYNAMISCH (`table_id=None, section_id=None` + Pflicht-Keywords
      `leader_id`/`run_dir`): jeder Zugriff auf `.table_id`/`.section_id`
      ruft `resolve_own_open_table_id()` frisch auf -- fuer einen FREIEN
      Harness, der beim Start nicht weiss, wen T spaeter einlaedt (Solo
      UND 2+3 UND zweite Runde funktionieren dadurch alle automatisch,
      ohne dass der Aufrufer irgendeine Gruppenformel selbst nachbauen
      muss)."""

    def __init__(
        self, table_id: str | None = None, section_id: str | None = None,
        complete_after: int = 2, *, leader_id: str | None = None,
        run_dir: "str | Path | None" = None,
    ):
        super().__init__(("127.0.0.1", 0), _CreationCapableHandler)
        if table_id is None or section_id is None:
            if not leader_id or run_dir is None:
                raise ValueError(
                    "Ohne feste table_id/section_id sind leader_id und run_dir "
                    "Pflicht (dynamische Ableitung, R6P01-Fix) -- kein stiller "
                    "Solo-Default."
                )
        self.calls: list[dict] = []
        self.creation_calls: list[dict] = []
        self._fixed_table_id = table_id
        self._fixed_section_id = section_id
        self._leader_id = leader_id
        self._run_dir = Path(run_dir) if run_dir is not None else None
        self.complete_after = complete_after
        self._thread = threading.Thread(target=self.serve_forever, daemon=True)

    @property
    def table_id(self) -> str:
        if self._fixed_table_id is not None:
            return self._fixed_table_id
        return resolve_own_open_table_id(self._run_dir, self._leader_id)

    @property
    def section_id(self) -> str:
        if self._fixed_section_id is not None:
            return self._fixed_section_id
        return f"{self.table_id}-section"

    @property
    def base_url(self) -> str:
        host, port = self.server_address
        return f"http://{host}:{port}"

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self.shutdown()
        self.server_close()
