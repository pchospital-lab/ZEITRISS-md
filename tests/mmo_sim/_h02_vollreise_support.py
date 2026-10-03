#!/usr/bin/env python3
"""
tests/mmo_sim/_h02_vollreise_support.py — gemeinsame Helper/Fixtures fuer
`test_h02_vollreise_profiles_2026_09_28.py` (H02-Vollreise-Auftrag,
2026-09-28). Neues Testartefakt, keine Produktdatei.

Baut NUR Testinfrastruktur (Loopback-Receiver, Fake-CLI, Evidenzordner,
Community-/Human-Bootstrap ueber vorhandene Produktfunktionen). Kein
Testhelper hier erzeugt Angebot/Tisch/Abschnitt/Consent/Save direkt in
Produktdateien -- das macht ausschliesslich der echte Produktweg
(`scripts/mmo_sim.py lab ...` als echter Subprozess).

`H02_EVIDENCE_DIR` ist eine NEUE, dokumentierte Testausgabevariable (kein
Produktflag): fehlt sie, legt `_evidence_root()` einen eigenen temporaeren
Ordner an, damit dieser Test weiterhin ohne externe Vorbereitung ueber
`run_all.py` lauffaehig bleibt."""
from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.community_bootstrap import bootstrap_community  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.registry.participants import ApplicationRecordRef, ParticipantRegistry  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
_FIX = _REPO_ROOT / "internal" / "qa" / "harness" / "lobby" / "fixtures" / "saves"
SIX_PERSONAS = ("sniper", "tech", "cqb", "face", "medic", "pyro")
MMO_SIM = _REPO_ROOT / "scripts" / "mmo_sim.py"
GUARD_DIR = Path(__file__).resolve().parents[2] / "internal" / "qa" / "harness"  # placeholder, unused directly


# --------------------------------------------------------------------------
# Evidenzordner (02_ABNAHME.md §E Beleglayout)
# --------------------------------------------------------------------------

def evidence_root() -> Path:
    """`H02_EVIDENCE_DIR` (neue Testausgabevariable, dokumentiert in
    02_ABNAHME_UND_AUFRUFE.md §D) -- ohne Angabe: eigener Temp-Ordner, damit
    `run_all.py` diesen Test ohne externe Vorbereitung findet/ausfuehrt."""
    raw = os.environ.get("H02_EVIDENCE_DIR")
    if raw:
        root = Path(raw)
    else:
        root = Path(tempfile.mkdtemp(prefix="h02_vollreise_evidence_"))
    root.mkdir(parents=True, exist_ok=True)
    return root


class CaseDirCollisionError(FileExistsError):
    """C3 (01_REVIEW_H02.md §5, 02_AUFTRAG_RESTPFLICHTEN.md 'Exklusive neue
    Ausgabeziele'): eine zweite Reservierung DESSELBEN Fallnamens ist ein
    kontrollierter Fehler, kein stiller Reuse -- alte Belegbytes duerfen
    dadurch nicht vermischt/ueberschrieben werden."""


def case_dir(name: str) -> Path:
    """Reserviert `name` exklusiv unter `evidence_root()`. R6-Nachzug
    (Review H02 2026-09-28 §5, WORKER-AUFTRAG.md C3): vorher `exist_ok=True`
    -- ein zweiter Aufruf mit demselben `name` wurde still akzeptiert und
    haette bereits vorhandene Belege mit einem neuen Lauf vermischen koennen
    (Review-Befund: 'zweiter Aufruf akzeptiert, statt Kollisionstop'). Jetzt
    `exist_ok=False`: die erste Reservierung legt `name`/`before`/`after`
    frisch an, jede weitere Reservierung DESSELBEN Namens wirft
    `CaseDirCollisionError`, OHNE die bereits vorhandenen Dateien der ersten
    Reservierung anzufassen (der fehlgeschlagene `mkdir`-Aufruf selbst
    schreibt nichts). Ein bewusst DERSELBE Testfall (z.B. API-Start gefolgt
    von API-Resume im selben `test_a_...`) reserviert weiterhin nur EINMAL
    und reicht danach das bereits zurueckgegebene `Path`-Handle weiter --
    kein zweiter `case_dir()`-Aufruf noetig/erlaubt fuer diesen Fall."""
    d = evidence_root() / name
    try:
        d.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise CaseDirCollisionError(
            f"case_dir({name!r}): bereits reserviert unter {d} -- kein Reuse, "
            "alte Belegbytes bleiben unveraendert"
        ) from exc
    (d / "before").mkdir()
    (d / "after").mkdir()
    return d


def sha256_of(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hash_tree(root: Path) -> dict:
    """Flaches Pfad->SHA256-Inventar (fuer before/after-Belege)."""
    out: dict[str, str] = {}
    if not root.exists():
        return out
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out[str(p.relative_to(root))] = sha256_of(p)
    return out


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")


def append_jsonl(path: Path, record: dict) -> None:
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


# --------------------------------------------------------------------------
# Community-/Human-Bootstrap (nur vorhandene Produktfunktionen)
# --------------------------------------------------------------------------

_PERSONA_ARCHETYPES = {
    "sniper": "Praeziser Einzelgaenger", "tech": "Analytischer Planer", "cqb": "Aggro-Draufgaenger",
    "face": "Sozialer Vermittler", "medic": "Vorsichtiger Absicherer", "pyro": "Chaotischer Improvisierer",
}
_PERSONA_PLAY_STYLES = {
    "sniper": "Distanz+Geduld", "tech": "Systematisch+Risikoarm", "cqb": "Nahkampf+Tempo",
    "face": "Diplomatie+Deeskalation", "medic": "Support+Ueberleben", "pyro": "Flaechenwirkung+Risiko",
}


def bootstrap_six_persona_community(root: Path, community_id: str, persona_keys=SIX_PERSONAS):
    """Analog `test_l01_l10_lobby_initiative._bootstrap_community`, aber mit
    eigenem Modulnamen hier (kein Import-Koppeln an die L-Testdatei fuer die
    Bootstrap-Funktion selbst -- diese Datei ist die eigene H02-Support-
    Fixture). Nutzt ausschliesslich `bootstrap_community` (Produktfunktion).

    R2-Nachzug (Review H02 2026-09-28 §3, WORKER-AUFTRAG.md B): `archetype`/
    `play_style` waren zuvor fuer JEDE Persona identisch `"SIMULIERT"` --
    das verhinderte, eigene/fremde Profiltexte im gerenderten eigenen
    Kontext (`persona_state.render_for_prompt`) ueberhaupt unterscheidbar zu
    pruefen. Jetzt je Persona ein eigener, fest zugeordneter Wert (s.
    `_PERSONA_ARCHETYPES`/`_PERSONA_PLAY_STYLES`) -- reine Testfixturedaten,
    keine Produktaenderung; Personas ausserhalb dieser Map (sollte nicht
    vorkommen, `SIX_PERSONAS` deckt alle bekannten Keys ab) fallen auf den
    alten `"SIMULIERT"`-Wert zurueck."""
    states_dir = root / "states"
    run_dir = root / "run"
    onboarding_dir = root / "onboarding"
    catalog_dir = root / "catalog"
    states_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    ps_store = PersonaStateStore(schema_path=_SCHEMA)
    community_dir = run_dir / "community"
    drafts = {
        pk: {
            "real_name": pk,
            "archetype": _PERSONA_ARCHETYPES.get(pk, "SIMULIERT"),
            "play_style": _PERSONA_PLAY_STYLES.get(pk, "SIMULIERT"),
            "charwunsch": "SIMULIERT/DEMO -- kein Erschaffungsdialog (H02-Vollreise-Testfixture).",
            "plays_char": {
                "save_file": "NOCH_NICHT_ERSCHAFFEN", "character_id": "NOCH_NICHT_ERSCHAFFEN",
                "name": "NOCH_NICHT_ERSCHAFFEN", "callsign": "NOCH_NICHT_ERSCHAFFEN",
            },
        }
        for pk in persona_keys
    }
    bootstrap_community(community_dir, community_id, 1, drafts, ps_store, states_dir, today="2026-09-28")
    return _SCHEMA, states_dir, run_dir, onboarding_dir, catalog_dir


def make_ready(onboarding_dir: Path, states_dir: Path, run_dir: Path, persona_key: str) -> str:
    """Identisch zu `test_l01_l10_lobby_initiative._make_ready` (Produktweg:
    `onboarding` + `core.store.publish_current_save`) -- eigene Kopie hier,
    damit diese Supportdatei self-contained bleibt (kein Cross-Test-Import
    fuer eine so zentrale Fixturefunktion)."""
    save = json.loads((_FIX / f"{persona_key}.json").read_text(encoding="utf-8"))
    chrono_id = save["characters"][0]["char_id"]
    ps_store = PersonaStateStore(schema_path=_SCHEMA)
    onboarding.start_or_resume(onboarding_dir, persona_key)
    onboarding.complete_with_save(onboarding_dir, persona_key, save, ZeitrissHarvestValidator(), chrono_id)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, persona_key, chrono_id, save)
    core_store.publish_current_save(run_dir, persona_key, save, ps_store, states_dir)
    return chrono_id


def load_fixture_save(persona_key: str) -> dict:
    return json.loads((_FIX / f"{persona_key}.json").read_text(encoding="utf-8"))


def own_figure_marker(persona_key: str) -> str:
    """C2-Nachzug (02_AUFTRAG_C_ABSCHLUSS.md C2, 01_REVIEW_H02.md §3): die
    woertliche Kopfzeile aus `persona_state.render_for_prompt`
    (`f'[BISHERIGER STAND — {{real_name}} spielt {{name}} "{{callsign}}", ...]'`)
    fuer GENAU die eigene Figur dieser Persona -- Sollwert stammt aus der
    unabhaengigen Fixture-Autoritaet (`load_fixture_save`, dieselbe Quelle,
    die `make_ready`/`bootstrap_six_persona_community` bereits zur
    Onboarding-/Publikationszeit verwendet haben), NICHT aus dem zu
    pruefenden Input selbst. Ersetzt den bisherigen zu schwachen
    `f'{{pk}} spielt'`-Marker (akzeptierte jede beliebige/fremde Figur nach
    dem Wort 'spielt', Review-Probe 'Leaderfigur')."""
    char = load_fixture_save(persona_key)["characters"][0]
    return f'{persona_key} spielt {char["name"]} "{char["callsign"]}"'


def own_current_json_marker(current: dict) -> str:
    """C2-Nachzug: der woertliche, vollstaendige JSON-Text, den
    `ui/tui.py:_own_system_context` fuer den eigenen Current anhaengt
    (`json.dumps(current, ensure_ascii=False, sort_keys=True)`, identischer
    Aufruf hier reproduziert -- kein neues Serialisierungsformat)."""
    return json.dumps(current, ensure_ascii=False, sort_keys=True)


_CURRENT_LABEL = "Eigener aktueller Spielstand (Current, vollstaendig): "


def own_current_full_marker(current: dict) -> str:
    """Oeffentlicher Wrapper um `_CURRENT_LABEL` + `own_current_json_marker`
    -- der vollstaendige woertliche Text, den `ui/tui.py:_own_system_context`
    fuer den eigenen Current anhaengt (fuer Fake-CLI-`expect_all`-Listen; die
    HTTP-Seite prueft denselben Text ueber `make_persona_input_validator`s
    `expected_current`-Parameter)."""
    return _CURRENT_LABEL + own_current_json_marker(current)


def register_human_participant(registry_dir: Path, display_name: str = "H02-Operator-Mensch"):
    """A01/H09: echte menschliche Teilnehmeridentitaet ueber
    `ParticipantRegistry.register_participant(kind="human", ...)` -- die
    zurueckgegebene ID wird verwendet, kein erfundener fester Wert."""
    registry = ParticipantRegistry(registry_dir)
    participant = registry.register_participant(kind="human", display_name=display_name)
    return participant


def onboard_human_figure(registry_dir: Path, persona_key: str, onboarding_dir: Path, states_dir: Path, run_dir: Path):
    """A01: stattet die unter `persona_key` registrierte menschliche
    Teilnehmeridentitaet (`persona_key` MUSS die von
    `register_human_participant()` zurueckgegebene `participant_id` sein,
    kein erfundener fester Produkt-ID-Wert) mit einer eigenen, eindeutig
    anderen v7-Save-Figur aus -- ueber denselben Onboarding-/Publish-
    Produktweg wie jede KI-Persona (`synthetic_human_save()`), und verbindet
    Registry-Seite und Figur explizit via `add_record_ref()`, damit die
    Registry-Identitaet die Figur auch sichtbar referenziert."""
    registry = ParticipantRegistry(registry_dir)
    save = synthetic_human_save()
    chrono_id = save["characters"][0]["char_id"]
    ps_store = PersonaStateStore(schema_path=_SCHEMA)
    onboarding.start_or_resume(onboarding_dir, persona_key)
    onboarding.complete_with_save(onboarding_dir, persona_key, save, ZeitrissHarvestValidator(), chrono_id)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, persona_key, chrono_id, save)
    core_store.publish_current_save(run_dir, persona_key, save, ps_store, states_dir)
    registry.add_record_ref(persona_key, ApplicationRecordRef(
        record_id=chrono_id, schema="zeitriss-v7", version="7", owner_participant_id=persona_key,
    ))
    return registry.load_participant(persona_key)


# --------------------------------------------------------------------------
# Aufzeichnender Loopback-HTTP-Server (Persona UND GM -- beide erfuellen
# denselben {choices:[{message:{content}}], usage} Response-Vertrag, s.
# `owui_client.OWUIChat.say`/`persona_api.PersonaApiDriver.decide`).
# --------------------------------------------------------------------------

def recording_http_server(
    responses: list[tuple[int, dict]], receipts_path: Path | None = None, label: str = "srv",
    validators: "dict[int, object] | None" = None,
):
    """Wie `test_l01_l10_lobby_initiative._persona_http_server`, aber
    zusaetzlich: volle Methode/Pfad/Header/Body je Call in `.received`
    gesammelt UND (falls `receipts_path` gesetzt) sofort als JSONL-Receipt
    persistiert -- fuer die geforderten `persona-receipts.jsonl`/
    `gm-receipts.jsonl`-Belege (02_ABNAHME.md §E).

    R3-Nachzug (Review H02 2026-09-28 §4, 07_HYBRID_API_SL_ERHALT.md §3):
    `validators` bildet Call-Index -> `Callable[[dict], str | None]` ab. Der
    Validator laeuft VOR der gescripteten Antwort gegen den tatsaechlich
    empfangenen Body; liefert er einen Fehlertext, wird NICHT die
    gescriptete Erfolgsantwort gesendet, sondern eine erkennbare
    Ablehnung (HTTP599, eigener `H02_INPUT_VALIDATION_FAILED`-Payload) --
    ein Double, das seinen Input nicht prueft, darf laut Review kein
    Entscheidungs-/Transportnachweis sein. Fehlschlaege landen zusaetzlich
    in `.validation_failures` (vom Aufrufer explizit auf Leere zu pruefen).

    C1-Nachzug (01_REVIEW_H02.md §3, 02_AUFTRAG_RESTPFLICHTEN.md C1): vorher
    enthielt der persistierte Receipt NUR den Eingang (Body/Hash) -- der
    Review-Befund 'Alle 36 positiven Transportbelege enthalten bislang
    Eingaenge, keinen Responsebody/stdout' galt genau fuer diese Funktion.
    Jetzt wird Status/Payload ZUERST bestimmt (Validierung + Scriptantwort),
    dann der TATSAECHLICH ueber `wfile.write` ausgegebene Response-Body
    (Bytes, Hash, Status) in DENSELBEN Receipt-Record aufgenommen, BEVOR er
    persistiert wird -- kein Nachschreiben, kein getrennter zweiter
    Schreiber. `send_ok`/`send_error` unterscheiden die zum Senden
    bestimmten Bytes von den tatsaechlich erfolgreich geschriebenen (ein
    Schreibfehler waere sonst unsichtbar geblieben)."""
    validators = validators or {}

    class _Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            return

        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0) or 0)
            raw = self.rfile.read(length) if length else b""
            received_wall_ts = time.time()
            received_monotonic = time.monotonic()
            try:
                body = json.loads(raw.decode("utf-8")) if raw else {}
            except json.JSONDecodeError:
                body = {"_raw_undecoded": raw.decode("utf-8", errors="replace")}
            idx = len(self.server.received)  # type: ignore[attr-defined]
            validator = self.server.validators.get(idx)  # type: ignore[attr-defined]
            validation_error = validator(body) if validator is not None else None
            if validation_error is not None:
                self.server.validation_failures.append(  # type: ignore[attr-defined]
                    {"seq": idx, "label": label, "error": validation_error}
                )
                status, payload = 599, {"error": f"H02_INPUT_VALIDATION_FAILED: {validation_error}"}
            else:
                status, payload = self.server.next_response()  # type: ignore[attr-defined]
            data = json.dumps(payload).encode("utf-8")
            send_error = None
            try:
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                send_ok = True
            except OSError as exc:  # echter Sendefehler -- ehrlich unterscheiden
                send_ok = False
                send_error = repr(exc)
            responded_wall_ts = time.time()
            responded_monotonic = time.monotonic()
            record = {
                "seq": idx, "label": label, "method": "POST", "path": self.path,
                "authorization_present": bool(self.headers.get("Authorization")),
                "body": body,
                "body_sha256": hashlib.sha256(raw).hexdigest(),
                "body_bytes_len": len(raw),
                "validation_error": validation_error,
                "received_wall_ts": received_wall_ts, "received_monotonic": received_monotonic,
                # C1: tatsaechlich ausgegebene Antwort -- nicht die gescriptete
                # Absicht, sondern das real ueber wfile geschriebene Ergebnis.
                "response_status": status, "response_body": payload,
                "response_bytes_intended_len": len(data),
                "response_sha256": hashlib.sha256(data).hexdigest(),
                "send_ok": send_ok, "send_error": send_error,
                "responded_wall_ts": responded_wall_ts, "responded_monotonic": responded_monotonic,
            }
            self.server.received.append(record)  # type: ignore[attr-defined]
            if self.server.receipts_path is not None:  # type: ignore[attr-defined]
                append_jsonl(self.server.receipts_path, record)  # type: ignore[attr-defined]
            self.server.calls.append(1)  # type: ignore[attr-defined]

    class _Srv(HTTPServer):
        def __init__(self):
            super().__init__(("127.0.0.1", 0), _Handler)
            self.calls: list[int] = []
            self.received: list[dict] = []
            self.receipts_path = receipts_path
            self.validators = validators
            self.validation_failures: list[dict] = []
            self._responses = list(responses)
            self._thread = threading.Thread(target=self.serve_forever, daemon=True)

        def next_response(self):
            return self._responses.pop(0) if self._responses else (500, {"error": f"{label}: keine weitere gescriptete Antwort"})

        @property
        def base_url(self):
            host, port = self.server_address
            return f"http://{host}:{port}"

        def __enter__(self):
            self._thread.start()
            return self

        def __exit__(self, *exc):
            self.shutdown()
            self.server_close()

    return _Srv()


_PUBLIC_TABLE_VIEW_MARKER = "[OEFFENTLICHE_TISCHSICHT]\n"


def decode_public_table_view(wire_text: str) -> dict | None:
    """B1 (02_AUFTRAG_BELEGSCHLUSS.md, 07_HYBRID_API_SL_VOLLSTAENDIG.md §4):
    dekodiert den woertlichen `[OEFFENTLICHE_TISCHSICHT]`-JSON-Block aus dem
    TATSAECHLICH gesendeten Persona-Wire (HTTP-`user`-Feld bzw. CLI-STDIN-
    `[USER]`-Abschnitt). `adapters.base.render_public_wire_text` haengt
    diesen Block IMMER als LETZTEN Teil an (nach `user`/`own_context`), s.
    dortiger Quellcode -- der Rest des Strings ab dem Marker ist deshalb
    exakt der von `json.dumps(table_view, ..., sort_keys=True)` erzeugte
    Text und laesst sich direkt zurueckparsen (kein Heuristik-Trimmen).
    Liefert `None`, wenn der Marker fehlt (z.B. Preflight-/Isolationstexte
    ohne `table_view`) -- das ist fuer die Aufrufer selbst ein Befund, kein
    stiller Fallback auf eine andere Quelle."""
    idx = wire_text.rfind(_PUBLIC_TABLE_VIEW_MARKER)
    if idx == -1:
        return None
    raw = wire_text[idx + len(_PUBLIC_TABLE_VIEW_MARKER):]
    return json.loads(raw)


def make_persona_input_validator(
    expected_pk: str, expected_sl_log_len: "int | None",
    *, expected_table_id: "str | None" = None, expected_offer_id: "str | None" = None,
    expected_current: "dict | None" = None,
):
    """B2 (G09, 02_AUFTRAG_BELEGSCHLUSS.md): echter `recording_http_server`-
    Validator (laeuft VOR der gescripteten Antwort, s. dortiges `do_POST`)
    -- prueft am TATSAECHLICH empfangenen Request-Body die eigene Persona
    (woertliche `render_for_prompt`-Kopfzeile `"{pk} spielt"`) UND, wenn
    `expected_sl_log_len` gesetzt ist, die tatsaechliche oeffentliche
    SL-Praefixlaenge aus dem dekodierten `[OEFFENTLICHE_TISCHSICHT]`-Block
    im `user`-Feld. Die Persona-Kopfzeile wird -- wie bei `_identify_persona`
    im Testfile -- ueber `system+user` gemeinsam gesucht: bei normalen
    Turns steht sie im `system`-Feld, bei Reflexionen ist `system` bewusst
    der generische `PRIVATE_REFLECTION_SENTINEL` und die Kopfzeile steckt
    stattdessen im `own_context`-Teil des `user`-Felds (s. `core/runtime.py:
    _collect_reflections`). Liefert bei Abweichung einen Fehlertext (der
    Server antwortet dann mit HTTP599 statt der gescripteten Erfolgsantwort,
    s. `recording_http_server`) -- kein reines Positions-/Listen-Pop. Die
    VOLLSTAENDIGE Zeichen-fuer-Zeichen-Pruefung des Praefixinhalts bleibt
    bewusst der permanenten Nachher-Assertion vorbehalten (getrennte
    Zustaendigkeit B1 vs. B2, 07_HYBRID_API_SL_VOLLSTAENDIG.md §3).

    C2-Nachzug (01_REVIEW_H02.md §4 Probe 1/2, 02_AUFTRAG_RESTPFLICHTEN.md
    C2): vorher pruefte diese Funktion nur Persona+Praefixlaenge -- der
    Review belegte zwei konkret erfolgreiche Fehlkontexte, die dadurch
    durchrutschten ('HTTP-Zustimmung ohne Angebot/Current/Phase, nur "tech
    spielt": HTTP200 Erfolg'; 'HTTP-Leaderimport mit falschem Tisch,
    fehlendem Current und leerem Praefix: HTTP200 Erfolg'). Beide zusaetzlich
    gepruefte Felder sind TATSAECHLICH im Wire transportiert (kein
    erfundenes Produktfeld): `expected_table_id` gegen den dekodierten
    `table_view["table_id"]` (`core/store.py:persona_view`); `expected_
    offer_id` gegen den woertlich eingebetteten `offer_id=<id>`/`"offer_id":
    "<id>"`-Text aus `adapters/base.py:decision_contract_instruction`, der
    JEDER Angebots-/Zustimmungsanfrage laut `lobby_flow.py:503-511` als Teil
    des `user`-Felds mitgegeben wird (Konsensbeweis fuer die Zustimmungsphase
    -- kein 'Current' im engeren Save-Sinn, aber dieselbe im Review verlangte
    Phasen-/Angebotsbindung: eine Zustimmung ohne die passende offer_id im
    Wire IST der fehlende Phasenbezug).

    C2-Nachzug r1 (01_REVIEW_H02.md §3 'Figur, vollstaendiger Current und
    vollstaendiger Phasenkontext fehlen', 02_AUFTRAG_C_ABSCHLUSS.md C2):
    zwei WEITERE Pruefungen, beide vor JEDER der 13 Personaantworten aktiv
    (nicht nur bei den Tischentscheidungen):
    1) Die Kopfzeile muss die EIGENE FIGUR tragen (`own_figure_marker`,
       woertlich Name+Callsign aus der unabhaengigen Fixture-Autoritaet),
       nicht nur `"{{pk}} spielt"` -- schliesst die Review-Probe 'echte
       Character-ID/Name durch fremde Figur ersetzt, tech-Marker erhalten:
       HTTP200 Erfolg'.
    2) Ist `expected_current` gesetzt, muss der vollstaendige, woertlich
       identisch serialisierte Current-JSON-Block (`own_current_json_marker`,
       derselbe `json.dumps(..., sort_keys=True)`-Aufruf wie
       `ui/tui.py:_own_system_context`) im system+user-Text stehen --
       schliesst die zwei NEUEN C2-Abweichungen 'Current bei Consent/Import
       entfernt'. `expected_current` stammt aus der Fixture- bzw.
       Publikations-Autoritaet (Aufrufer uebergibt sie), NICHT aus dem
       Input selbst."""
    def _validate(body: dict) -> "str | None":
        messages = body.get("messages") or []
        system_text = messages[0].get("content", "") if messages else ""
        user_text = messages[1].get("content", "") if len(messages) > 1 else ""
        haystack = f"{system_text}\n{user_text}"
        figure_marker = own_figure_marker(expected_pk)
        if figure_marker not in haystack:
            return f"erwartete Figur-Kopfzeile {figure_marker!r} fehlt in system+user: {haystack[:200]!r}"
        if expected_current is not None:
            current_marker = _CURRENT_LABEL + own_current_json_marker(expected_current)
            if current_marker not in haystack:
                return (
                    f"erwarteter vollstaendiger Current fuer {expected_pk!r} fehlt in system+user "
                    f"(gesucht: {current_marker[:160]!r}...)"
                )
        if expected_offer_id is not None:
            offer_marker_json = json.dumps(expected_offer_id)
            offer_marker_text = f"offer_id={expected_offer_id}"
            if offer_marker_json not in user_text and offer_marker_text not in user_text:
                return (
                    f"erwartete offer_id {expected_offer_id!r} fehlt woertlich im user-Feld "
                    f"(weder {offer_marker_json!r} noch {offer_marker_text!r} gefunden)"
                )
        if expected_sl_log_len is not None:
            table_view = decode_public_table_view(user_text)
            if table_view is None:
                return "kein [OEFFENTLICHE_TISCHSICHT]-Block im user-Feld gefunden"
            if expected_table_id is not None and table_view.get("table_id") != expected_table_id:
                return f"table_id {table_view.get('table_id')!r} != erwartet {expected_table_id!r}"
            actual_len = len(table_view.get("sl_log") or [])
            if actual_len != expected_sl_log_len:
                return f"sl_log-Laenge {actual_len} != erwartet {expected_sl_log_len}"
        return None
    return _validate


def make_gm_leader_text_validator(expected_text: str):
    """B2 (G09): echter GM-Empfaenger-Validator -- prueft, dass der
    tatsaechlich vom Leader entschiedene Text (`expected_text`, derselbe
    Wert, der bereits als gescriptete Persona-Antwort verwendet wurde)
    woertlich in der AKTUELLEN Usernachricht des tatsaechlich empfangenen
    GM-Request-Body steht.

    C2-Nachzug (01_REVIEW_H02.md §4 Probe 3, 02_AUFTRAG_RESTPFLICHTEN.md C2):
    die VORHERIGE Fassung durchsuchte den GESAMTEN serialisierten Body
    (`json.dumps(body)`) -- der Review belegte konkret, dass ein
    Erwartungstext, der NUR in einer AELTEREN Nachricht steht, waehrend die
    aktuelle Usernachricht etwas anderes/falsches traegt, trotzdem als
    Erfolg durchging ('GM-Erwartungstext nur in alter Nachricht, aktuelle
    Usernachricht falsch: HTTP200 Erfolg'). `internal/qa/harness/owui_client.
    py:OWUIChat.say` haengt die aktuell zu sendende Leaderentscheidung als
    LETZTEN Eintrag von `body['messages']` an (`self.history.append({'role':
    'user', 'content': user_text})` unmittelbar vor dem Request) -- diese
    Funktion prueft deshalb NUR NOCH `messages[-1]`, nicht mehr die gesamte
    History/den gesamten Body. Ein `body['messages']` ohne Eintraege ist
    ebenfalls ein Befund (kein leerer Body als impliziter Erfolg).

    C2-Nachzug r1 (01_REVIEW_H02.md §3 'GM aktuelle Usernachricht exakt,
    nicht widerspruechliche Zusaetze durch Substring passieren lassen',
    02_AUFTRAG_C_ABSCHLUSS.md C2): die VORHERIGE Fassung pruefte
    `expected_text not in current_content` (Substring) -- ein Aufrufer
    KONNTE `expected_text` frei in einer laengeren, widersprechenden
    Nachricht einbetten und wuerde trotzdem akzeptiert. `expected_text` MUSS
    jetzt der VOLLSTAENDIGE erwartete aktuelle Text sein (`caller` uebergibt
    bei G0/G1 den TEXT INKLUSIVE des angehaengten erlaubten Save-JSON-Blocks,
    s. `_gm_wire_texts_with_embedded_saves` im Testfile) -- Vergleich ist
    jetzt EXAKTE Gleichheit (`==`), keine Teilstring-Pruefung mehr."""
    def _validate(body: dict) -> "str | None":
        messages = body.get("messages") or []
        if not messages:
            return "GM-Request-Body ohne messages[] -- keine aktuelle Usernachricht auswertbar"
        current = messages[-1]
        current_content = current.get("content", "") if isinstance(current, dict) else ""
        if current_content != expected_text:
            return (
                f"aktuelle GM-Usernachricht (messages[-1], role="
                f"{current.get('role') if isinstance(current, dict) else '?'}) weicht EXAKT vom erwarteten "
                f"vollstaendigen Text ab: erwartet={expected_text!r} ist={current_content!r}"
            )
        return None
    return _validate


def blocked_target_url() -> str:
    """Y-N4: nicht erlaubte Testadresse -- ein nicht-Loopback/nicht
    existentes Ziel, das VOR jedem DNS/Socket-Versuch am Admission-/
    Autoritaetsgate abgelehnt werden muss (fail-closed, kein echter
    externer Request)."""
    return "http://198.51.100.1:9"  # TEST-NET-2 (RFC 5737), nie live geroutet


# --------------------------------------------------------------------------
# Fake-CLI mit sequenzieller Queue (Hybrid-Profil, echte ausfuehrbare Datei)
# --------------------------------------------------------------------------

_QUEUED_FAKE_CLI_TEMPLATE = '''{shebang}
import hashlib
import json
import os
import sys
import time

CAPTURE_PATH = {capture_path!r}
QUEUE_PATH = {queue_path!r}
FAIL_MARKER_PATH = {fail_marker_path!r}
FAIL_LOG_PATH = {fail_log_path!r}
RESPONSE_LOG_PATH = {response_log_path!r}
HELP_VERSION_LOG_PATH = {help_version_log_path!r}

# C1-Nachzug (01_REVIEW_H02.md §3, 02_AUFTRAG_RESTPFLICHTEN.md C1): Help/
# Version-Probes GETRENNT vom Entscheidungsjournal protokolliert (nicht in
# die 13 Entscheidungsaufrufe mitgezaehlt) -- vorher wurden sie gar nicht
# journalisiert.
if "--help" in sys.argv or "--version" in sys.argv:
    _kind = "help" if "--help" in sys.argv else "version"
    _text = (
        "Usage: fake-claude [options]\\n"
        "  --permission-mode <mode>  restrict tool execution (plan|manual|...)\\n"
        "  --safe-mode  skip hooks, MCP servers, settings, plugins"
    ) if _kind == "help" else "fake-claude 0.0.0-h02-vollreise-test"
    if HELP_VERSION_LOG_PATH:
        with open(HELP_VERSION_LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({{
                "kind": _kind, "argv": sys.argv[1:], "pid": os.getpid(), "cwd": os.getcwd(),
                "wall_ts": time.time(), "stdout": _text,
            }}, ensure_ascii=False) + "\\n")
    print(_text)
    sys.exit(0)

stdin_text = sys.stdin.read()
_received_wall_ts = time.time()
with open(CAPTURE_PATH, "a", encoding="utf-8") as fh:
    fh.write(json.dumps(
        {{"argv": sys.argv[1:], "stdin": stdin_text, "cwd": os.getcwd(), "pid": os.getpid(),
          "received_wall_ts": _received_wall_ts}}, ensure_ascii=False,
    ) + "\\n")


def _write_response_journal(rc, stdout_text, stderr_text):
    # C1-Nachzug: die TATSAECHLICH ausgegebene Antwort (nicht die geplante
    # Queue-Intention) -- eigener Receipt neben CAPTURE_PATH (das nur den
    # Eingang protokolliert), mit echtem eigenem PID (`os.getpid()` DIESES
    # Kindprozesses -- Fake-CLI darf ihren eigenen PID angeben, s.
    # 02_AUFTRAG_RESTPFLICHTEN.md C1) und Hash/Zeit der realen Ausgabe.
    #
    # C1-Nachzug r1 (01_REVIEW_H02.md §2 Bytebefund): `print(_stdout)` im
    # Erfolgspfad schreibt TATSAECHLICH `len(stdout_text)+1` Bytes (print()
    # haengt genau EIN LF an) -- die vorherige Fassung hashte/laengte NUR
    # `stdout_text` OHNE dieses LF (223 statt 224 Bytes am realen Beispiel).
    # Jetzt getrennt benannt: `stdout`/`stdout_sha256`/`stdout_chars` bleiben
    # der NORMALISIERTE semantische Text (kein LF, wie bisher lesbar); NEU
    # `stdout_raw_bytes_len`/`stdout_raw_sha256` sind Laenge/Hash der
    # TATSAECHLICH via `print()` geschriebenen Bytes inkl. LF -- NUR im
    # Erfolgspfad (rc=0, `stdout_text` nichtleer) wird ueberhaupt ein LF
    # angehaengt, da die Fehlerpfade NIE `print(_stdout)` aufrufen (dort ist
    # `stdout_text` bewusst "").
    if not RESPONSE_LOG_PATH:
        return
    raw_stdout_bytes = (stdout_text + "\\n").encode("utf-8") if stdout_text else b""
    payload = {{
        "pid": os.getpid(), "argv": sys.argv[1:], "rc": rc,
        "stdout": stdout_text, "stdout_sha256": hashlib.sha256(stdout_text.encode("utf-8")).hexdigest(),
        "stdout_chars": len(stdout_text),
        "stdout_raw_bytes_len": len(raw_stdout_bytes),
        "stdout_raw_sha256": hashlib.sha256(raw_stdout_bytes).hexdigest(),
        "stderr": stderr_text, "responded_wall_ts": time.time(),
    }}
    with open(RESPONSE_LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\\n")


if FAIL_MARKER_PATH and os.path.exists(FAIL_MARKER_PATH):
    _stderr = "simulated CLI failure (H02 Y-N1)"
    print(_stderr, file=sys.stderr)
    _write_response_journal(1, "", _stderr)
    sys.exit(1)

with open(QUEUE_PATH, "r", encoding="utf-8") as fh:
    queue = json.load(fh)
if not queue:
    _stderr = "fake-claude: Antwortqueue erschoepft -- unerwarteter zusaetzlicher Aufruf"
    print(_stderr, file=sys.stderr)
    _write_response_journal(2, "", _stderr)
    sys.exit(2)
item = queue[0]

# R3-Nachzug (Review H02 2026-09-28 §4, 07_HYBRID_API_SL_ERHALT.md §3): VOR
# jeder Antwort den tatsaechlichen Input inhaltlich pruefen (Persona-/Phasen-
# /Offer-/Section-Bezug, eigener Kontext, SL-Praefix) -- ein blindes
# positionsweises Poppen der Queue ist laut Review KEIN Entscheidungs-/
# Transportnachweis. `expect_all`: JEDE dieser Teilzeichenketten MUSS
# woertlich in argv+stdin vorkommen; fehlt eine, wird die Queue NICHT
# konsumiert, sondern ein sichtbarer, diagnostizierbarer Fehler geschrieben.
expect_all = item.get("expect_all") or []
haystack = stdin_text + "\\n" + " ".join(sys.argv[1:])
missing = [needle for needle in expect_all if needle not in haystack]

# R5-Nachzug (H02-Belegschluss B2, 02_AUFTRAG_BELEGSCHLUSS.md, 07_...md §3):
# `expect_all` prueft bisher NUR Persona-/ID-Substrings -- der oeffentliche
# Praefix selbst (wie viele SL-Runden das Double VOR dieser Antwort bereits
# sehen darf) wurde NIE geprueft, ein leeres oder gekuerztes
# `table_view["sl_log"]` waere unbemerkt durchgerutscht (kein Antwort-Poppen
# nach Position/Substring allein). `expect_sl_log_len` (optional, vom
# Aufrufer je Queue-Position mitgegeben) dekodiert denselben
# `[OEFFENTLICHE_TISCHSICHT]`-JSON-Block wie die permanente Testassertion
# und prueft VOR dem Antworten die tatsaechliche Praefixlaenge.
expect_sl_log_len = item.get("expect_sl_log_len")
sl_log_len_error = None
if expect_sl_log_len is not None:
    # WICHTIG: nur `stdin_text` durchsuchen/parsen, NICHT `haystack` -- der
    # `[OEFFENTLICHE_TISCHSICHT]`-JSON-Block ist das LETZTE, was
    # `render_public_wire_text` an den `user`-Teil des STDIN anhaengt
    # (s. `decode_public_table_view`-Docstring); `haystack` haengt danach
    # zusaetzlich noch argv an, was `json.loads` mit "Extra data" abbrechen
    # liesse.
    marker = "[OEFFENTLICHE_TISCHSICHT]\\n"
    marker_idx = stdin_text.rfind(marker)
    if marker_idx == -1:
        sl_log_len_error = "kein [OEFFENTLICHE_TISCHSICHT]-Block im STDIN gefunden"
    else:
        try:
            table_view = json.loads(stdin_text[marker_idx + len(marker):])
            actual_len = len(table_view.get("sl_log") or [])
        except (json.JSONDecodeError, AttributeError) as exc:
            sl_log_len_error = f"table_view nicht dekodierbar: {{exc}}"
        else:
            if actual_len != expect_sl_log_len:
                sl_log_len_error = f"sl_log-Laenge {{actual_len}} != erwartet {{expect_sl_log_len}}"

if missing or sl_log_len_error:
    diag = {{
        "argv": sys.argv[1:], "stdin_len": len(stdin_text), "missing_expected": missing,
        "sl_log_len_error": sl_log_len_error, "queue_position": 0,
    }}
    if FAIL_LOG_PATH:
        with open(FAIL_LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(diag, ensure_ascii=False) + "\\n")
    _stderr = (
        f"fake-claude: unerwarteter Input, fehlende erwartete Teiltexte: {{missing}}; "
        f"sl_log_len_error: {{sl_log_len_error}}"
    )
    print(_stderr, file=sys.stderr)
    _write_response_journal(9, "", _stderr)
    sys.exit(9)

queue.pop(0)
with open(QUEUE_PATH, "w", encoding="utf-8") as fh:
    json.dump(queue, fh)

result_text = item.get("result", "")
rc = int(item.get("rc", 0))
if rc != 0:
    _stderr = item.get("stderr", "simulated CLI failure")
    print(_stderr, file=sys.stderr)
    _write_response_journal(rc, "", _stderr)
    sys.exit(rc)
_stdout = json.dumps({{"type": "result", "subtype": "success", "is_error": False, "result": result_text, "usage": {{}}}})
print(_stdout)
_write_response_journal(0, _stdout, "")
'''


def write_queued_fake_cli(
    root: Path, *, capture_path: Path, queue: list[dict], fail_marker_path: Path | None = None,
) -> Path:
    """Baut eine EIGENE ausfuehrbare Fake-CLI-Datei (04_HYBRID_API_SL.md §3):
    `--help`/`--version` liefern markierte Fake-Werte mit den tatsaechlich
    benoetigten Isolations-Hilfeeintraegen; der eigentliche Entscheidungs-
    aufruf liest STDIN vollstaendig, protokolliert argv+stdin+cwd literal in
    `capture_path` (JSONL) und liefert die naechste Antwort aus einer
    Datei-Queue (`queue`, in Aufrufreihenfolge) -- deterministisch fuer den
    vollstaendig sequenziellen Lab-Controller (kein Env-Bypass noetig, da
    `_CHILD_ENV_ALLOWLIST` in `persona_claude_code.py` eigene Testsignal-
    Variablen ohnehin nicht durchreicht, s. dortiger `_write_fake_cli`-
    Docstring im aelteren H08-Test).

    R3-Nachzug: das Shebang bindet jetzt LITERAL auf `sys.executable` (den
    tatsaechlich aufgeloesten Interpreter dieses Testprozesses) statt auf
    `env python3` -- ein `PATH`-abhaengiges `env`-Shebang ist in einer
    absichtlich knappen Allowlist-Umgebung ein unnoetiges Risiko. Jedes
    `queue`-Item darf zusaetzlich `expect_all: list[str]` tragen (vom
    Fake-CLI-Skript selbst VOR dem Popen/Antworten geprueft, s.
    `_QUEUED_FAKE_CLI_TEMPLATE`); Fehlschlaege landen in einer separaten
    `<capture_path>.validation-failures.jsonl`-Datei neben `capture_path`.

    C1-Nachzug (01_REVIEW_H02.md §3): zwei WEITERE eigene Journale neben
    `capture_path` (das nur den Eingang protokolliert) -- `response_log_
    path_for(capture_path)` (die TATSAECHLICH ausgegebene Antwort je
    Entscheidungsaufruf inkl. eigenem PID/Hash/rc/stdout/stderr) und
    `help_version_log_path_for(capture_path)` (Help-/Version-Probes GETRENNT
    vom Entscheidungsjournal, nicht in dessen Zaehlung enthalten)."""
    queue_path = root / f"fake_cli_queue_{capture_path.stem}.json"
    write_json(queue_path, queue)
    fail_log_path = capture_path.parent / f"{capture_path.stem}.validation-failures.jsonl"
    response_log_path = response_log_path_for(capture_path)
    help_version_log_path = help_version_log_path_for(capture_path)
    path = root / f"fake_claude_{capture_path.stem}.py"
    path.write_text(
        _QUEUED_FAKE_CLI_TEMPLATE.format(
            shebang=f"#!{sys.executable}",
            capture_path=str(capture_path),
            queue_path=str(queue_path),
            fail_marker_path=str(fail_marker_path) if fail_marker_path else "",
            fail_log_path=str(fail_log_path),
            response_log_path=str(response_log_path),
            help_version_log_path=str(help_version_log_path),
        ),
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return path


def response_log_path_for(capture_path: Path) -> Path:
    return capture_path.parent / f"{capture_path.stem}.responses.jsonl"


def help_version_log_path_for(capture_path: Path) -> Path:
    return capture_path.parent / f"{capture_path.stem}.help-version.jsonl"


def observed_choice_content(record: dict) -> "str | None":
    """C1-Nachzug (01_REVIEW_H02.md §3 'gm_texts stammen aus der geplanten
    Fixtureliste, nicht einem beobachteten Responsejournal'): liest den
    TATSAECHLICH ueber `wfile.write` ausgegebenen Antworttext aus einem
    `recording_http_server`-Receipt-Record (`record['response_body']`, seit
    dem C1-Nachzug dort im do_POST-Record real erfasst) -- kein Ruecklesen
    der urspruenglichen Scriptliste. Liefert `None`, wenn der Record keinen
    gueltigen `choices[0].message.content` traegt (z.B. eine HTTP599-
    Validierungsablehnung ohne Scriptinhalt)."""
    body = record.get("response_body") or {}
    choices = body.get("choices") or []
    if not choices:
        return None
    return (choices[0].get("message") or {}).get("content")


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def queue_remaining(queue_path: Path) -> list:
    if not queue_path.exists():
        return []
    return json.loads(queue_path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# GM-Debrief-Bloecke (v7-Saves fuer G4)
# --------------------------------------------------------------------------

def debrief_blocks(final_saves: dict[str, dict]) -> str:
    return "\n".join(f"```json\n{json.dumps(b, ensure_ascii=False)}\n```" for b in final_saves.values())


def synthetic_human_save(char_id: str = "CHR-HUMAN-OPS-001", name: str = "Operator", callsign: str = "HUMANOPS") -> dict:
    """A01/H09: eigene vollstaendige, von den sechs KI-Fixtures unterschiedene
    v7-Save-Identitaet fuer den menschlichen Community-Slot -- selbes v7-
    Schema wie die bestehenden Fixtures (`_FIX/*.json`), nur eigener
    char_id/name/callsign (keine Wiederverwendung einer KI-Identitaet)."""
    return {
        "v": 7, "save_id": f"fixture-{char_id.lower()}-initial-001",
        "_fixture_note": "SIMULIERT/FIXTURE (H02-Vollreise, menschlicher Community-Slot)",
        "characters": [{"char_id": char_id, "id": char_id, "name": name, "callsign": callsign}],
    }


# --------------------------------------------------------------------------
# Bereinigtes Kind-Environment + Loopback-Guard (04_HYBRID_API_SL.md §2)
# --------------------------------------------------------------------------

_INHERITED_ENV_ALLOWLIST = ("PATH", "LANG", "LC_ALL", "TERM", "SHELL")

_LOOPBACK_GUARD_SOURCE = '''"""H02-Vollreise-Testguard: verweigert Nicht-Loopback-Python-Socketziele in
diesem UND geerbten Python-Kindprozessen (Loopback-Only, keine OS-Firewall)."""
import ipaddress
import socket
_orig_connect = socket.socket.connect
_orig_connect_ex = socket.socket.connect_ex
_orig_getaddrinfo = socket.getaddrinfo


def _check(host):
    if host in (None, "localhost"):
        return
    try:
        if ipaddress.ip_address(host).is_loopback:
            return
    except ValueError:
        pass
    raise RuntimeError(f"H02_NET_GUARD: Nicht-Loopback-Ziel blockiert ({host!r})")


def connect(self, addr):
    if self.family in (socket.AF_INET, socket.AF_INET6):
        _check(addr[0])
    return _orig_connect(self, addr)


def connect_ex(self, addr):
    if self.family in (socket.AF_INET, socket.AF_INET6):
        _check(addr[0])
    return _orig_connect_ex(self, addr)


def getaddrinfo(host, *a, **kw):
    if host is not None:
        _check(host)
    return _orig_getaddrinfo(host, *a, **kw)


socket.socket.connect = connect
socket.socket.connect_ex = connect_ex
socket.getaddrinfo = getaddrinfo
'''


def write_loopback_guard(dest_dir: Path) -> Path:
    """Schreibt einen eigenen, self-contained `sitecustomize.py`-Guard
    (Inhalt analog `P/reference/guard/sitecustomize.py`, aber literal
    eingebettet -- ein PERMANENTER Repo-Test darf nicht auf den externen,
    nach Auftragsende geraeumten Exchange-Paketpfad verweisen). Rueckgabe:
    Verzeichnis, das der Aufrufer vorne in `PYTHONPATH` einreiht, damit
    Python es beim Interpreterstart automatisch importiert."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    (dest_dir / "sitecustomize.py").write_text(_LOOPBACK_GUARD_SOURCE, encoding="utf-8")
    return dest_dir


def minimal_lab_env(
    extra: dict, *, tmp_root: Path, guard_dir: Path | None = None, schema_dependency_dir: "Path | None" = None,
) -> dict:
    """Baut ein EXPLIZITES minimales Kind-Environment fuer den `lab start/
    resume/status/stop/attach`-Subprozess (04_HYBRID_API_SL.md §2: 'nicht
    unbesehen dict(os.environ) uebernehmen') -- nur eine kleine Allowlist
    (PATH/LANG/...) plus einem FRISCHEN LEEREN eigenen HOME/TMPDIR plus die
    vom Aufrufer uebergebene explizite MMO_SIM_*/OPENWEBUI_*-Konfiguration.
    Keine Dev-Session-/Token-/Proxy-/Provider-/Cloud-/Hookvariablen werden
    geerbt.

    R3-Nachzug (Review H02 2026-09-28 §4, 07_HYBRID_API_SL_ERHALT.md §2):
    `HOME` wurde bisher aus der Testprozess-Umgebung GEERBT statt selbst
    isoliert zu werden (Review-Befund: 'minimal_lab_env uebernimmt HOME aus
    der Umgebung, statt selbst einen frischen leeren Test-HOME zu
    erzwingen') -- Aufrufer-seitig injizierte frische HOME/TMPDIR-Werte
    ersetzten die fehlende Selbstisolation NICHT. Jetzt legt diese Funktion
    IMMER selbst ein frisches leeres `home/`-Unterverzeichnis unter
    `tmp_root` an und setzt `HOME` explizit darauf -- unabhaengig davon, ob
    der Aufrufer bereits eine eigene HOME-Variable in `extra` mitgibt (die,
    falls gesetzt, wie jede andere `extra`-Variable weiterhin Vorrang
    behaelt, s. `env.update(extra)` unten).

    C3-Nachzug r2 (01_REVIEW_H02.md §5, 02_AUFTRAG_RESTABSCHLUSS.md C3):
    optionaler `schema_dependency_dir` -- Default `None`, bestehendes
    Verhalten fuer ALLE bisherigen Aufrufer bleibt bytegleich. Wird ein
    Scratchverzeichnis uebergeben (exklusive Kopie via
    `copy_dependency_visibility`, KEINE Installation), reiht diese Funktion
    es NEBEN `guard_dir` in `PYTHONPATH` ein -- damit die dort sichtbar
    gemachte `jsonschema`-Dependency bis in das wirklich gestartete
    Lab-/Fake-CLI-Kind reicht (Review-Befund: reale Lab-Kinder hatten
    `jsonschema is None`, trotz vorhandener Dependency auf dem Host)."""
    tmp_root.mkdir(parents=True, exist_ok=True)
    home_dir = tmp_root / "home"
    home_dir.mkdir(parents=True, exist_ok=True)
    env = {k: os.environ[k] for k in _INHERITED_ENV_ALLOWLIST if k in os.environ}
    env["HOME"] = str(home_dir)
    env["TMPDIR"] = str(tmp_root)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    pythonpath_parts = [str(p) for p in (guard_dir, schema_dependency_dir) if p is not None]
    if pythonpath_parts:
        env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)
    env.update(extra)
    return env


# --------------------------------------------------------------------------
# C3: echter Kind-Guard-/Dependency-Nachweis (02_AUFTRAG_RESTPFLICHTEN.md
# C3, 01_REVIEW_H02.md §5 'Das minimale Kind-Environment existiert, aber die
# tatsaechliche Guard-/Dependencypruefung der realen Kinder/Fake-CLI ist
# nicht in den Dauertests belegt. Der aeussere Helper-Preflight ist dafuer
# kein Ersatz.').
# --------------------------------------------------------------------------

_CHILD_GUARD_PROOF_SCRIPT = '''
import json
import socket
import sys

report = {"argv_probe": "guard-proof", "checks": {}}

# 0) NEU (C3-Nachzug r1, 01_REVIEW_H02.md §5 "Seine Probe wuerde bei
# fehlendem Hook sogar die externe Adresse mit socket.connect versuchen.
# Das muss vor einem solchen Aufruf rein lokal scheitern. Keine externe
# Verbindung zur Netzsperrenpruefung."): REIN LOKALE Identitaetspruefung,
# ob der Guard-Hook ueberhaupt geladen wurde (Modulpfad + monkeypatchte
# `socket.getaddrinfo`), BEVOR irgendein Verbindungsversuch (Schritt 1/2)
# passiert. Nur wenn dieser lokale Check besteht, folgt der externe Zielort
# (TEST-NET-2, RFC 5737, nie live geroutet) -- fehlt der Hook, wird GAR
# KEIN Verbindungsversuch unternommen, sondern sofort FAIL berichtet.
try:
    import sitecustomize
    import pathlib
    hook_path = str(pathlib.Path(sitecustomize.__file__).resolve())
    hook_identity_ok = socket.getaddrinfo.__module__ == "sitecustomize"
except ImportError:
    hook_path = None
    hook_identity_ok = False
report["checks"]["guard_hook_loaded_locally"] = {
    "ok": hook_identity_ok, "detail": f"sitecustomize={hook_path!r} getaddrinfo.__module__ patched={hook_identity_ok}",
}

if not hook_identity_ok:
    # Kein Hook lokal nachweisbar -- KEIN externer Verbindungsversuch.
    report["checks"]["guard_blocks_nonloopback"] = {
        "ok": False, "detail": "Guard-Hook nicht lokal nachweisbar -- externer Verbindungsversuch UNTERLASSEN (kein Netzversuch ohne Hook)",
    }
else:
    # 1) Guard tatsaechlich im KINDPROZESS geladen (nicht nur im
    # Elternprozess): ein Verbindungsversuch zu einem Nicht-Loopback-Ziel
    # muss die literale H02_NET_GUARD-RuntimeError auswerfen. Faellt der
    # Guard NICHT, scheitert der Versuch stattdessen mit einem anderen
    # Fehler (OSError/Timeout) oder haette (bei erreichbarem Netz) real
    # verbunden -- beides ist hier ein FAIL, kein stiller Erfolg.
    try:
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("198.51.100.1", 9))
        report["checks"]["guard_blocks_nonloopback"] = {"ok": False, "detail": "connect() lief durch (kein Guard-Hit)"}
    except RuntimeError as exc:
        report["checks"]["guard_blocks_nonloopback"] = {
            "ok": "H02_NET_GUARD" in str(exc), "detail": str(exc),
        }
    except OSError as exc:
        report["checks"]["guard_blocks_nonloopback"] = {"ok": False, "detail": f"OSError statt Guard-RuntimeError: {exc!r}"}

# 2) Guard erlaubt weiterhin Loopback (kein Ueberblocken).
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.0)
    try:
        s.connect(("127.0.0.1", 1))
    except ConnectionRefusedError:
        pass  # erwartet: Verbindung wird vom OS abgelehnt (kein Listener), NICHT vom Guard
    except OSError as exc:
        raise AssertionError(f"unerwarteter OSError auf Loopback-Ziel: {exc!r}")
    report["checks"]["guard_allows_loopback"] = {"ok": True, "detail": "kein H02_NET_GUARD auf 127.0.0.1"}
except RuntimeError as exc:
    report["checks"]["guard_allows_loopback"] = {"ok": False, "detail": f"Guard blockierte faelschlich Loopback: {exc!r}"}
except AssertionError as exc:
    report["checks"]["guard_allows_loopback"] = {"ok": False, "detail": str(exc)}

# 3) Dependency-Status ehrlich berichten (jsonschema ist laut Produktcode
# `mmo_sim/core/persona_state.py` OPTIONAL mit Fallback -- kein Hardblock,
# aber der reale Ladezustand in DIESEM Kind-Env wird beobachtet statt
# angenommen).
#
# C3-Nachzug r2 (01_REVIEW_H02.md §5 "prove_child_guard_and_dependency
# meldet bei fehlendem jsonschema weiterhin ok:true"): VORHER meldeten
# BEIDE Zweige (verfuegbar UND ImportError) ok:True -- das verschleierte
# genau den Review-Befund, dass dieses Kind (ohne Dependency-Sichtbarkeit
# im PYTHONPATH) jsonschema tatsaechlich NICHT laden kann. Jetzt EHRLICH:
# ok/available spiegeln den REALEN Ladezustand. Das ist weiterhin KEIN
# Hardblock dieser reinen Beobachtungsfunktion (der optionale
# Produktfallback bleibt unveraendert) -- der strengere Ausfuehrungsvorbehalt
# (BLOCKED vor jedem fachlichen Request) sitzt in `probe_schema_dependency`/
# `prove_child_dependency_fail_closed`, nicht hier.
try:
    import jsonschema  # noqa: F401
except ImportError as exc:
    report["checks"]["jsonschema_dependency"] = {
        "ok": False, "available": False,
        "detail": f"NICHT verfuegbar in diesem Kind-Env (Produktfallback koennte greifen, ist aber hier "
                   f"keine erfuellte Testvoraussetzung): {exc!r}",
    }
else:
    # `jsonschema.__version__` loest bei fehlenden dist-info-Metadaten (z.B.
    # in einer exklusiven Nur-Paketdateien-Scratchkopie ohne *.dist-info,
    # s. `_copy_dependency_visibility`) `importlib.metadata.
    # PackageNotFoundError` aus -- das ist eine `ImportError`-Unterklasse
    # und wuerde, IM SELBEN try-Block wie der `import`, faelschlich als
    # "jsonschema nicht importierbar" verbucht, obwohl das Modul tatsaechlich
    # geladen wurde. Deshalb GETRENNT behandelt: Importerfolg allein
    # entscheidet `available`, ein Fehlschlag NUR beim Versionsstring bleibt
    # rein informativ.
    try:
        version = jsonschema.__version__
    except Exception as exc:  # noqa: BLE001 -- rein informativ, aendert `available` nicht.
        version = f"<version lookup failed: {exc!r}>"
    report["checks"]["jsonschema_dependency"] = {"ok": True, "available": True, "detail": f"verfuegbar: {version}"}

print(json.dumps(report, ensure_ascii=False))
'''


def prove_child_guard_and_dependency(*, tmp_root: Path, guard_dir: Path, timeout: int = 20) -> dict:
    """C3: spawnt einen ECHTEN Python-Kindprozess (kein Parent-Preflight,
    kein Mock) mit GENAU demselben `minimal_lab_env`/`guard_dir`-Aufbau wie
    jeder reale `lab`-Subprozess bzw. die Fake-CLI, und laesst IHN SELBST
    pruefen, ob der Loopback-Guard in seinem eigenen Prozess wirksam ist und
    ob die optionale `jsonschema`-Dependency dort geladen werden kann.
    Liefert `{"pid", "returncode", "stdout", "report", "started_wall_ts",
    "ended_wall_ts"}` -- `pid` ist der ECHTE PID dieses Kindes (`Popen.pid`,
    nicht `os.getpid()` des Elternprozesses)."""
    env = minimal_lab_env({}, tmp_root=tmp_root, guard_dir=guard_dir)
    started = time.time()
    proc = subprocess.Popen(
        [sys.executable, "-c", _CHILD_GUARD_PROOF_SCRIPT],
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env,
    )
    pid = proc.pid
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate(timeout=10)
    ended = time.time()
    try:
        report = json.loads(out.strip().splitlines()[-1]) if out.strip() else {}
    except (json.JSONDecodeError, IndexError):
        report = {}
    return {
        "pid": pid, "returncode": proc.returncode, "stdout": out, "stderr": err,
        "report": report, "started_wall_ts": started, "ended_wall_ts": ended,
    }


_CHILD_DEPENDENCY_FAIL_CLOSED_SCRIPT = '''
import json
import sys

report = {"probe": "dependency-fail-closed"}
try:
    import jsonschema  # noqa: F401
    report["jsonschema_available"] = True
except ImportError:
    report["jsonschema_available"] = False

if not report["jsonschema_available"]:
    # C3-Nachzug (02_AUFTRAG_C_ABSCHLUSS.md C3, 01_REVIEW_H02.md §5): dieser
    # TEST-Vorbehalt ist STRENGER als der optionale Produktfallback in
    # `persona_state.py::PersonaStateStore.validate_state` -- fehlt
    # jsonschema, wird HIER kontrolliert VOR jedem fachlichen
    # Validierungsversuch abgebrochen (BLOCKED), statt `validate_state()`
    # aufzurufen und dessen (produktseitig zulaessigen, hier aber NICHT als
    # erfuellte Testvoraussetzung akzeptierten) Fallback laufen zu lassen.
    # Kein Import/keine Installation -- reine lokale Feststellung.
    report["status"] = "BLOCKED_MISSING_DEPENDENCY"
    report["functional_test_executed"] = False
    print(json.dumps(report, ensure_ascii=False))
    sys.exit(3)

sys.path.insert(0, sys.argv[1])
from mmo_sim.core.persona_state import PersonaStateStore
store = PersonaStateStore(schema_path=sys.argv[2])
state = json.loads(sys.argv[3])
store.validate_state(state)
report["status"] = "OK"
report["functional_test_executed"] = True
print(json.dumps(report, ensure_ascii=False))
'''


def _copy_dependency_visibility(dest_dir: Path) -> "tuple[Path | None, dict]":
    """C3 (05_QUELLEN_UND_PRUEFUNGEN.md 'Ausfuehrungsgrenzen': 'bereits
    vorhandene Dependencydateien nur in einer exklusiven Review-Quellkopie
    als Sichtbarkeit kopiert; Originalpfad/Bytehash unter dependency-
    visibility.json'): kopiert das REAL bereits vorhandene `jsonschema`-
    Package (samt seiner Laufzeit-Abhaengigkeiten `referencing`,
    `rpds_py*`, `attr(s)`, `jsonschema_specifications`, falls vorhanden) aus
    dem tatsaechlichen `site.getusersitepackages()`-Pfad in EIN exklusives
    Scratchverzeichnis (`dest_dir`) -- KEINE Installation, KEINE Aenderung
    von HOME/PATH/globalem Interpreter/Login. Liefert `(dest_dir_oder_None,
    {top_level_name: {"source": str, "sha256_of_init_or_file": str}})` als
    Hashbeleg je kopiertem Top-Level-Namen. `None`, falls das reale
    site-packages-Verzeichnis nicht existiert (dann bleibt die
    Sichtbarkeits-Kopie leer -- der Aufrufer erhaelt dann konsequent
    KEIN sichtbares jsonschema, wie im deny_dependency=True-Fall).

    Host-Nachzug: `site.getusersitepackages()` haengt an der `HOME`-Variable
    DIESES (aufrufenden) Prozesses -- laeuft dieser Testprozess selbst schon
    unter einem isolierten `HOME` (z.B. innerhalb eines kontrollierten
    Wrapperlaufs), liefert `site.getusersitepackages()` einen FALSCHEN,
    ebenfalls isolierten Pfad statt des echten Originalpfads. `H02_REAL_
    USER_SITE_PACKAGES` (optional vom Aufrufer/Wrapper VOR jeder HOME-
    Isolation gesetzt) hat deshalb Vorrang; ohne diese Variable bleibt
    `site.getusersitepackages()` der Fallback (korrekt, wenn dieser
    Testprozess selbst noch mit dem echten HOME laeuft)."""
    import shutil
    import site
    override = os.environ.get("H02_REAL_USER_SITE_PACKAGES")
    real_site = Path(override) if override else Path(site.getusersitepackages())
    if not real_site.is_dir():
        return None, {}
    dest_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict = {}
    for name in ("jsonschema", "jsonschema_specifications", "referencing", "attr", "attrs", "rpds"):
        src = real_site / name
        if not src.exists():
            continue
        dst = dest_dir / name
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
            marker = dst / "__init__.py"
            manifest[name] = {
                "source": str(src),
                "sha256": hashlib.sha256(marker.read_bytes()).hexdigest() if marker.is_file() else None,
            }
        else:
            shutil.copy2(src, dst)
            manifest[name] = {"source": str(src), "sha256": hashlib.sha256(dst.read_bytes()).hexdigest()}
    for entry in real_site.glob("rpds_py*"):
        dst = dest_dir / entry.name
        if entry.is_dir():
            shutil.copytree(entry, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(entry, dst)
        manifest[entry.name] = {"source": str(entry), "sha256": None}
    return dest_dir, manifest


def copy_dependency_visibility(dest_dir: Path) -> "tuple[Path | None, dict]":
    """Oeffentlicher Name fuer `_copy_dependency_visibility` (s. dort fuer
    die vollen Mechanik-/Sicherheitsdetails: exklusive Scratchkopie aus dem
    REALEN `site.getusersitepackages()`, Hashbeleg je Top-Level-Paket, KEINE
    Installation/kein Eingriff in HOME/PATH/globalen Interpreter). C3-Nachzug
    r2 (02_AUFTRAG_RESTABSCHLUSS.md C3): Aufrufer AUSSERHALB dieser Datei
    (`_run_lab`/Testfunktionen), die `jsonschema` bis ins wirklich gestartete
    Lab-Kind sichtbar machen wollen (`minimal_lab_env(..., schema_dependency_dir=...)`),
    nutzen diesen Namen statt des unterstrichenen internen."""
    return _copy_dependency_visibility(dest_dir)


_SCHEMA_DEPENDENCY_PROBE_SCRIPT = '''
import json

report = {}
try:
    import jsonschema
except ImportError as exc:
    report["available"] = False
    report["error"] = repr(exc)
else:
    # Import getrennt von der FUNKTIONALEN Probe (echter validate()-Aufruf,
    # nicht nur der Modulimport) UND getrennt vom Versionsstring: eine
    # exklusive Nur-Paketdateien-Scratchkopie (s. `_copy_dependency_
    # visibility`) hat kein *.dist-info, `jsonschema.__version__` wuerde
    # dort `importlib.metadata.PackageNotFoundError` (eine `ImportError`-
    # Unterklasse) auswerfen -- das darf NICHT als "nicht verfuegbar"
    # gewertet werden, wenn das Modul tatsaechlich geladen UND funktional
    # nutzbar ist.
    report["available"] = True
    try:
        jsonschema.validate(instance={"v": 2}, schema={"type": "object"})
        report["functional_validate_ok"] = True
    except Exception as exc:
        report["functional_validate_ok"] = False
        report["functional_validate_error"] = repr(exc)
    try:
        report["version"] = jsonschema.__version__
    except Exception as exc:
        report["version"] = f"<version lookup failed: {exc!r}>"
print(json.dumps(report))
'''


def probe_schema_dependency(env: dict, timeout: int = 20) -> dict:
    """C3-Nachzug r2 (01_REVIEW_H02.md §5 'Vor dem ersten fachlichen Request
    muss die benoetigte Schema-Dependency im echten Lab-Kind verfuegbar
    sein'): spawnt einen ECHTEN Kindprozess MIT GENAU DEM UEBERGEBENEN `env`
    -- demselben Dict, das der Aufrufer unmittelbar ANSCHLIESSEND fuer den
    fachlichen `lab`-Subprozess verwendet (kein Nachbau mit eigenen Werten,
    keine Kopie mit abweichenden Variablen) -- und laesst IHN SELBST
    feststellen, ob `jsonschema` dort importierbar ist. Reiner Lesevorgang
    (ein `import`-Versuch), keine Installation, keine Aenderung des
    uebergebenen `env`-Dicts."""
    proc = subprocess.run(
        [sys.executable, "-c", _SCHEMA_DEPENDENCY_PROBE_SCRIPT],
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        env=dict(env), timeout=timeout,
    )
    try:
        report = json.loads(proc.stdout.strip().splitlines()[-1]) if proc.stdout.strip() else {}
    except (json.JSONDecodeError, IndexError):
        report = {}
    report["returncode"] = proc.returncode
    report["stderr"] = proc.stderr
    return report


def prove_child_dependency_fail_closed(
    *, tmp_root: Path, repo_root: Path, schema_path: Path, sample_state: dict,
    deny_dependency: bool, timeout: int = 20,
) -> dict:
    """C3-Nachzug (02_AUFTRAG_C_ABSCHLUSS.md C3, 01_REVIEW_H02.md §5): ECHTER
    Kindprozess (kein Parent-Mock), der GENAU DORT, wo die Laufpruefung das
    Persona-State-Schema braucht (`PersonaStateStore.validate_state`), bei
    fehlendem `jsonschema` kontrolliert VOR dem fachlichen Aufruf abbricht
    (`BLOCKED_MISSING_DEPENDENCY`, `functional_test_executed=False`,
    `returncode=3`) statt `ok=True` zu melden.

    BEIDE Faelle verwenden GENAU dasselbe isolierte `minimal_lab_env`-Muster
    (frisches leeres HOME/TMPDIR, knappe Allowlist) wie jeder reale
    `lab`-Subprozess -- WICHTIG: `jsonschema` liegt auf diesem Host
    ausschliesslich im User-Site-Verzeichnis (`site.getusersitepackages()`),
    das an `HOME` gebunden ist. Mit frischem, leerem `HOME` (wie
    `minimal_lab_env` es IMMER erzwingt) ist `jsonschema` deshalb bereits
    OHNE jedes Extra-Flag unsichtbar (eigene Kontrollprobe: `HOME=<leer>
    python3 -c "import jsonschema"` wirft `ModuleNotFoundError`) -- exakt
    der reale Zustand, den JEDER echte Lab-/Fake-CLI-Kindprozess in diesem
    gesamten Testpaket bereits hat. `deny_dependency=True` liefert GENAU
    diesen unveraenderten realen Zustand (keine Praeparation noetig).
    `deny_dependency=False` ist die Gegenprobe: `_copy_dependency_visibility`
    kopiert das REAL vorhandene `jsonschema`-Package (mit Hashbeleg) in EIN
    exklusives Scratchverzeichnis unter `tmp_root` und reiht NUR dieses in
    `PYTHONPATH` ein -- keine Installation, kein Ruecken an HOME/PATH/
    globalem Interpreter. Damit beweist die Gegenprobe wirklich, dass das
    Flag (und nicht ein zufaellig unveraenderter Ambient-Zustand) die
    beobachtete Verfuegbarkeit steuert."""
    tmp_root.mkdir(parents=True, exist_ok=True)
    home_dir = tmp_root / "home"
    home_dir.mkdir(parents=True, exist_ok=True)
    env = {k: os.environ[k] for k in _INHERITED_ENV_ALLOWLIST if k in os.environ}
    env["HOME"] = str(home_dir)
    env["TMPDIR"] = str(tmp_root)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    dependency_visibility = None
    if not deny_dependency:
        vis_dir, manifest = _copy_dependency_visibility(tmp_root / "dependency-visibility")
        dependency_visibility = {"scratch_dir": str(vis_dir) if vis_dir else None, "manifest": manifest}
        if vis_dir is not None and manifest:
            env["PYTHONPATH"] = str(vis_dir)
    argv = [sys.executable, "-c", _CHILD_DEPENDENCY_FAIL_CLOSED_SCRIPT, str(repo_root), str(schema_path), json.dumps(sample_state)]
    started = time.time()
    proc = subprocess.Popen(
        argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env,
    )
    pid = proc.pid
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate(timeout=10)
    ended = time.time()
    try:
        report = json.loads(out.strip().splitlines()[-1]) if out.strip() else {}
    except (json.JSONDecodeError, IndexError):
        report = {}
    return {
        "pid": pid, "returncode": proc.returncode, "stdout": out, "stderr": err,
        "report": report, "started_wall_ts": started, "ended_wall_ts": ended, "deny_dependency": deny_dependency,
        "dependency_visibility": dependency_visibility,
    }
