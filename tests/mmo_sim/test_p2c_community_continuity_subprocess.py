#!/usr/bin/env python3
"""
tests/mmo_sim/test_p2c_community_continuity_subprocess.py — dauerhafte
Regressionstests fuer den Community-Kontinuitaetsblock (C1/C2/C3,
P2-Community-Kontinuitaet 2026-09-25, MAIN-DATENWEGENTSCHEIDUNG.md §3).

Reale, EIGENSTAENDIGE Python-Subprozesse (echte neue Interpreter-PIDs, keine
In-Prozess-Wiederholung derselben `TuiSession`) treiben `advance_one_persona_
creation` ueber echte Publikations-/Empfangs-/Step-/Ready-Naehte:

C1 (Ready-/Publikationsnähte): ein echter OSError wird ueber
`unittest.mock.patch.object` an je EINER der fuenf realen Publikations-
funktionen (`catalog.register`/`store_figure_save`, `onboarding.ensure_
participant_persona_state`, `store.publish_current_save`, `catalog.
bind_for_section`) injiziert -- ein NEUER Interpreter-Prozess muss danach
OHNE weiteren GM-/Persona-Request wieder tischbereit werden (nicht bloss
`onboarding.completed` behaupten).

C2 (Empfangene Ergebnisse ueberleben lokale Fehler): ein persona_error
(Personaantwort schlaegt fehl, NACHDEM die SL-Frage bereits empfangen
wurde) bzw. ein step_error (`onboarding.record_step` schlaegt fehl, NACHDEM
SL-Frage UND Personaantwort bereits empfangen wurden) darf im naechsten
Prozess NICHT die initiale GM-Anfrage erneut senden.

C3 (Eigener Kontext beim Empfaenger): der reale `PersonaApiDriver` gegen
einen Loopback-Server zeigt, dass der ERSTE HTTP-Request das eigene Profil
UND der ZWEITE HTTP-Request die eigene vorherige Antwort enthaelt --
niemals ein fremdes Profil.

Testdoubles sitzen ausschliesslich an der aeussersten Prozess-/HTTP-/
Fake-Adapter-Grenze (analog `test_p2_community_creation_real_subprocess.py`)
-- kein echter Modell-/Providerlauf."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path
from unittest.mock import patch

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.adapters.fakes import FakeHTTPServer  # noqa: E402
from mmo_sim.adapters.persona_api import PersonaApiConfig, PersonaApiDriver  # noqa: E402
from mmo_sim.core import request_ledger, store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.community_bootstrap import bootstrap_community  # noqa: E402
from mmo_sim.domain.zeitriss.community_creation import (  # noqa: E402
    advance_community_creation,
    advance_one_persona_creation,
)

SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
PS = PersonaStateStore(schema_path=SCHEMA)
QUESTION = "SYNTHETIC_CONTINUITY_Q1: Welche Ausruestung waehlst du?"
ANSWER = "SYNTHETIC_CONTINUITY_A1: Ich waehle einen Karabiner."


def _block(pk: str, stage: str = "created") -> dict:
    return {
        "v": 7, "save_id": f"SYNTHETIC-{stage}-{pk}",
        "characters": [{"char_id": f"chrono-{pk}", "name": f"Synthetic {pk}", "callsign": pk.upper(), "level": 1}],
    }


def _fenced(block: dict) -> str:
    return "```json\n" + json.dumps(block) + "\n```"


def _draft(pk: str) -> dict:
    return {
        "real_name": f"Synthetic {pk}", "archetype": f"ARCHETYPE_{pk}", "play_style": f"STYLE_{pk}",
        "charwunsch": f"OWN_PROFILE_MARKER_{pk}",
        "plays_char": {
            "save_file": "NOCH_NICHT_ERSCHAFFEN", "character_id": "NOCH_NICHT_ERSCHAFFEN",
            "name": "NOCH_NICHT_ERSCHAFFEN", "callsign": "NOCH_NICHT_ERSCHAFFEN",
        },
    }


def _setup(base: Path, keys=("alpha",)) -> None:
    base.mkdir(parents=True, exist_ok=True)
    bootstrap_community(
        base / "run/community", "continuity-community", 1, {pk: _draft(pk) for pk in keys},
        PS, base / "states", "2026-09-25",
    )
    write_test_profile(base / "run", max_turns=100)


def _kwargs(base: Path, pk: str) -> dict:
    return dict(
        run_dir=base / "run", states_dir=base / "states", schema_path=SCHEMA,
        onboarding_dir=base / "onboarding", catalog_dir=base / "catalog",
        community_id="continuity-community", generation=1, persona_key=pk,
    )


def _ready_coherent(base: Path, pk: str) -> bool:
    try:
        current = store.load_current_save_or_raise(base / "run", pk, PS, states_dir=base / "states")
    except store.CurrentSaveUnavailableError:
        return False
    if current is None:
        return False
    char_id = current["characters"][0]["char_id"]
    active = catalog.active_chrononaut_id(base / "catalog", pk)
    persona_state = PS.load_state(pk, states_dir=base / "states")
    entries = catalog.list_for_participant(base / "catalog", pk)
    return (
        active == char_id
        and persona_state["plays_char"]["character_id"] == char_id
        and any(e.chrononaut_id == char_id for e in entries)
    )


def _run_child(base: Path, mode: str, pk: str = "alpha") -> dict:
    """Ein ECHTER, EIGENSTAENDIGER Subprozess (frische PID) ruft
    `advance_one_persona_creation` GENAU EINMAL auf -- `--child` unten ist
    der Selbstaufruf-Einstiegspunkt DIESER Datei, analog `tests-review/
    review_community_continuity.py`."""
    cmd = [
        sys.executable, str(Path(__file__).resolve()), "--child",
        "--base", str(base), "--mode", mode, "--pk", pk,
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=30)
    if proc.returncode:
        raise RuntimeError(f"Kindprozess fehlgeschlagen (exit={proc.returncode}):\n{proc.stderr}\n{proc.stdout}")
    return json.loads(proc.stdout)


# C2 (P2-Community-Ergebnisuebergabe 2026-09-25, MAIN-DATENWEGENTSCHEIDUNG.md
# §3): die NEUE Luecke sitzt NICHT in `record_step`/den fuenf Publikations-
# naehten (bereits oben abgedeckt), sondern GENAU im lokalen Checkpoint-Write
# `record_pending_reply`/`record_pending_answer` SELBST -- ein `OSError`
# WAEHREND `onboarding._write` (nicht die Funktion drumherum) laesst
# `pending_step` unpersistiert, OBWOHL der Requestledger die Antwort bereits
# `accounted` hat (`request_ledger.finish_received(..., result_text=...)`).
# Diese drei Modi treffen `onboarding._write` NUR beim ERSTEN Aufruf, dessen
# `state.pending_step` die jeweilige Zielbedingung erfuellt -- exakt der vom
# End-Critic identifizierte Seam (analog `tests-review/review_community_
# checkpoint_commit.py`, hier als DAUERHAFTER In-Repo-Test statt externer
# Einwegprobe).
_PENDING_WRITE_FAULT_MODES = ("pending_reply_fail", "pending_answer_fail", "pending_reply_save_fail")


def _child_main(base: Path, mode: str, pk: str) -> None:
    if mode == "batch_ledger_internal_fault":
        _child_main_batch_ledger_fault(base)
        return
    calls = {"gm": [], "persona": []}
    faults = []

    class GM:
        output_limit_tokens = 50

        def turn(self, idx, text, output_limit_tokens=None):
            calls["gm"].append({"idx": idx, "text": text})
            if mode == "forbid_calls":
                raise AssertionError("Worker-Test: kein weiterer GM-Call erwartet")
            return {
                "content": _fenced(_block(pk)) if ANSWER in text else QUESTION,
                "usage": {"prompt_tokens": 3, "completion_tokens": 3},
            }

    class Driver:
        config = None

        def decide(self, ctx):
            calls["persona"].append(ctx)
            if mode in ("persona_error", "forbid_calls"):
                raise RuntimeError("SYNTHETIC persona response unavailable")
            return ParticipantDecision(
                text=ANSWER, origin_source="synthetic-worker-test",
                meta={"usage": {"prompt_tokens": 3, "completion_tokens": 3}},
            )

    def _injected(*args, **kwargs):
        faults.append(mode)
        raise OSError(f"SYNTHETIC publication/step failure: {mode}")

    targets = {
        "register_error": (catalog, "register"),
        "figure_error": (catalog, "store_figure_save"),
        "state_error": (onboarding, "ensure_participant_persona_state"),
        "publish_error": (store, "publish_current_save"),
        "bind_error": (catalog, "bind_for_section"),
        "step_error": (onboarding, "record_step"),
    }
    patches = []
    if mode in targets:
        mod, attr = targets[mode]
        patches.append(patch.object(mod, attr, side_effect=_injected))
    elif mode in _PENDING_WRITE_FAULT_MODES:
        original_write = onboarding._write

        def _pending_write_wrapper(path, state):
            pending = state.pending_step or {}
            sl_reply = pending.get("sl_reply")
            persona_answer = pending.get("persona_answer")
            is_target = (
                (mode == "pending_reply_fail" and sl_reply == QUESTION and persona_answer is None)
                or (mode == "pending_answer_fail" and persona_answer == ANSWER)
                or (mode == "pending_reply_save_fail" and sl_reply == _fenced(_block(pk)))
            )
            if not faults and is_target:
                faults.append(mode)
                raise OSError(f"SYNTHETIC checkpoint write failure: {mode}")
            return original_write(path, state)

        patches.append(patch.object(onboarding, "_write", _pending_write_wrapper))
    elif mode == "ledger_internal_fault":
        # C2-Nacharbeit (End-Critic-Befund 1, 2026-09-25, MAIN-DATENWEGENTSCHEIDUNG.md
        # §6 viertes Fenster "vor/nach received/accounted"): trifft NICHT den
        # lokalen Onboarding-Checkpoint-Write (bereits oben abgedeckt), sondern
        # `request_ledger.finish_received()`s EIGENEN zweiten internen Write
        # (Uebergang state=received -> state=accounted, hier ueber `add_seconds`
        # simuliert) -- der Datensatz bleibt danach ehrlich bei `state=received`
        # haengen, OBWOHL `result_text` bereits im ERSTEN Write durabel steht.
        original_add_seconds = request_ledger.add_seconds

        def _faulty_add_seconds(run_dir, request_id, seconds):
            if not faults:
                faults.append(mode)
                raise OSError(f"SYNTHETIC ledger-internal failure: {mode}")
            return original_add_seconds(run_dir, request_id, seconds)

        patches.append(patch.object(request_ledger, "add_seconds", _faulty_add_seconds))
    for p in patches:
        p.start()
    try:
        outcome = advance_one_persona_creation(
            **_kwargs(base, pk), gm_transport_factory=lambda: GM(), persona_driver_factory=lambda pk: Driver(),
        )
        result = {"status": outcome.status, "chrononaut_id": outcome.chrononaut_id, "reason": outcome.reason}
        error = None
    except Exception as e:  # noqa: BLE001 -- Kindprozess meldet jeden Fehler roh an den Elternprozess
        result = None
        error = {"type": type(e).__name__, "text": str(e)}
    finally:
        for p in patches:
            p.stop()
    requests_dir = base / "run" / "requests"
    accounted_result_texts = []
    # C2-Nacharbeit (End-Critic-Befund 1, 2026-09-25): `durable_result_texts`
    # zusaetzlich zu `accounted_result_texts` -- ein Datensatz kann bereits
    # durabel/wiederverwendbar sein (s. `request_ledger.find_durable_result`),
    # OHNE dass sein zweiter interner Write (`state=accounted`) je erfolgreich
    # war (`ledger_internal_fault` oben). `accounted_result_texts` bleibt
    # unveraendert streng auf `state=="accounted"` -- bestehende Tests lesen
    # dieses Feld bereits als Beleg fuer den vollstaendig abgeschlossenen
    # Requestledger-Schritt.
    durable_result_texts = []
    if requests_dir.is_dir():
        for f in sorted(requests_dir.glob("*.json")):
            data = json.loads(f.read_text(encoding="utf-8"))
            if data.get("error") is None and data.get("result_text") is not None:
                if data.get("state") == "accounted":
                    accounted_result_texts.append(data["result_text"])
                if data.get("state") in ("received", "accounted"):
                    durable_result_texts.append(data["result_text"])
    print(json.dumps({
        "outcome": result, "error": error, "calls": calls, "faults": faults,
        "ready_coherent": _ready_coherent(base, pk),
        "accounted_result_texts": accounted_result_texts,
        "durable_result_texts": durable_result_texts,
        "pid": __import__("os").getpid(),
    }))


def _child_main_batch_ledger_fault(base: Path) -> None:
    """C2-Nacharbeit (End-Critic-Befund 1, 2026-09-25): treibt
    `advance_community_creation` (nicht `advance_one_persona_creation`) fuer
    ZWEI Personas -- die erste Persona trifft den `ledger_internal_fault`
    (s. oben) bei ihrem ERSTEN `finish_received()`-Aufruf, die zweite ist
    vollstaendig gesund. Prueft `advance_community_creation`s eigenen,
    dokumentierten Vertrag ('Fehler/Ablehnung/Blockade EINER Persona darf die
    uebrigen Mitglieder NICHT anhalten') auch fuer diesen bislang ungefangenen
    Fehlerpfad, nicht nur fuer die bereits explizit abgefangenen Fehlerarten."""
    calls = {"gm": [], "persona": []}
    faults = []
    original_add_seconds = request_ledger.add_seconds

    def _faulty_add_seconds(run_dir, request_id, seconds):
        if not faults:
            faults.append("batch_ledger_internal_fault")
            raise OSError("SYNTHETIC batch ledger-internal failure: first finish_received() call")
        return original_add_seconds(run_dir, request_id, seconds)

    class GM:
        output_limit_tokens = 50

        def turn(self, idx, text, output_limit_tokens=None):
            calls["gm"].append(text)
            return {
                "content": _fenced(_block("beta_second")) if ANSWER in text else QUESTION,
                "usage": {"prompt_tokens": 3, "completion_tokens": 3},
            }

    class Driver:
        config = None

        def decide(self, ctx):
            calls["persona"].append(ctx)
            return ParticipantDecision(
                text=ANSWER, origin_source="synthetic-worker-test",
                meta={"usage": {"prompt_tokens": 3, "completion_tokens": 3}},
            )

    with patch.object(request_ledger, "add_seconds", _faulty_add_seconds):
        outcomes = advance_community_creation(
            run_dir=base / "run", states_dir=base / "states", schema_path=SCHEMA,
            onboarding_dir=base / "onboarding", catalog_dir=base / "catalog",
            community_id="continuity-community", generation=1,
            planned_persona_keys=["alpha_first", "beta_second"],
            gm_transport_factory=lambda: GM(), persona_driver_factory=lambda pk: Driver(),
            print_fn=lambda s: None,
        )
    print(json.dumps({
        "outcomes": [
            {"persona_key": o.persona_key, "status": o.status, "chrononaut_id": o.chrononaut_id, "reason": o.reason}
            for o in outcomes
        ],
        "calls": calls, "faults": faults,
        "pid": __import__("os").getpid(),
    }))


def test_publication_failure_recovers_without_new_model_call():
    """C1: fuer jede der fuenf realen Publikationsnaehte muss ein NEUER
    Interpreterprozess nach dem Fehler OHNE weiteren GM-/Persona-Request
    wieder eine kohaerente, tischbereite Figur melden."""
    for mode in ("register_error", "figure_error", "state_error", "publish_error", "bind_error"):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            _setup(base)
            first = _run_child(base, mode)
            assert first["faults"] == [mode], f"[{mode}] Injektion muss genau einmal ausgeloest werden: {first}"
            retry = _run_child(base, "forbid_calls")
            assert retry["ready_coherent"], f"[{mode}] Reentry muss tatsaechlich kohaerent tischbereit werden: {retry}"
            assert not retry["calls"]["gm"] and not retry["calls"]["persona"], (
                f"[{mode}] Wiederaufnahme eines bereits erhaltenen validen Saves darf keinen neuen "
                f"Modellaufruf ausloesen: {retry}"
            )


def test_persona_error_after_received_gm_question_does_not_resend_initial_prompt():
    """C2: SL-Frage bereits empfangen, Personaantwort schlaegt fehl -- ein
    NEUER Prozess darf die initiale GM-Anfrage NICHT erneut senden."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        _setup(base)
        first = _run_child(base, "persona_error")
        assert len(first["calls"]["gm"]) == 1 and len(first["calls"]["persona"]) == 1, first
        initial_text = first["calls"]["gm"][0]["text"]
        retry = _run_child(base, "normal")
        repeated = [c for c in retry["calls"]["gm"] if c["text"] == initial_text]
        assert not repeated, f"initiale GM-Anfrage wurde nach Neustart erneut gesendet: {retry}"
        assert retry["ready_coherent"], retry


def test_step_write_failure_after_both_received_does_not_repeat_either_request():
    """C2: SL-Frage UND Personaantwort bereits erhalten, `record_step`
    schlaegt lokal fehl -- ein NEUER Prozess darf WEDER die GM- NOCH die
    Persona-Anfrage wiederholen."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        _setup(base)
        first = _run_child(base, "step_error")
        assert first["faults"] == ["step_error"] and len(first["calls"]["persona"]) == 1, first
        initial_text = first["calls"]["gm"][0]["text"]
        retry = _run_child(base, "normal")
        repeated = [c for c in retry["calls"]["gm"] if c["text"] == initial_text]
        assert not repeated, f"GM-Anfrage wurde nach Step-Write-Fehler erneut gesendet: {retry}"
        assert not retry["calls"]["persona"], f"Persona-Anfrage wurde nach Step-Write-Fehler erneut gesendet: {retry}"
        assert retry["ready_coherent"], retry


def test_pending_reply_checkpoint_failure_does_not_resend_received_gm_question():
    """C2 (P2-Community-Ergebnisuebergabe 2026-09-25, MAIN-DATENWEGENTSCHEIDUNG.md
    §3): die SL-Frage wurde bereits empfangen und im Requestledger dauerhaft
    `accounted` (`request_ledger.finish_received(..., result_text=...)`) --
    ERST DANACH scheitert der lokale `onboarding.record_pending_reply`-Write
    an einem gewoehnlichen `OSError` (nicht Powerloss/fsync). Ein NEUER
    Interpreterprozess darf die bereits abgerechnete GM-Anfrage NICHT
    erneut senden -- er muss sie aus dem Requestledger wiederherstellen und
    direkt bei der Personaantwort fortsetzen."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        _setup(base)
        first = _run_child(base, "pending_reply_fail")
        assert first["faults"] == ["pending_reply_fail"], first
        assert first["error"] is not None and first["error"]["type"] == "OSError", first
        assert len(first["calls"]["gm"]) == 1 and not first["calls"]["persona"], (
            f"Checkpoint-Fehler muss VOR der Personaanfrage auftreten: {first}"
        )
        assert QUESTION in first["accounted_result_texts"], (
            f"die empfangene SL-Frage muss trotz Checkpoint-Fehler bereits durabel im "
            f"Requestledger stehen: {first}"
        )
        initial_text = first["calls"]["gm"][0]["text"]
        retry = _run_child(base, "normal")
        assert retry["pid"] != first["pid"], "Wiederaufnahme muss ein ECHTER neuer Prozess sein"
        # Turn 0 (die bereits empfangene+abgerechnete Frage) darf NICHT erneut
        # angefordert werden -- Turn 1 (der naechste, echte GENUINE neue
        # Schritt, ausgeloest von der jetzt nachgeholten Personaantwort) IST
        # ein legitimer neuer GM-Call, kein Duplikat.
        repeated = [c for c in retry["calls"]["gm"] if c["text"] == initial_text]
        assert not repeated, (
            f"bereits empfangene+abgerechnete SL-Frage darf nach Checkpoint-Fehler NICHT "
            f"erneut angefordert werden: {retry}"
        )
        assert len(retry["calls"]["persona"]) == 1, (
            f"die noch offene Personaantwort muss GENAU EINMAL neu angefordert werden: {retry}"
        )
        assert retry["ready_coherent"], retry


def test_pending_answer_checkpoint_failure_does_not_resend_either_request():
    """C2: SL-Frage UND Personaantwort wurden bereits empfangen und im
    Requestledger dauerhaft `accounted` -- ERST DANACH scheitert der lokale
    `onboarding.record_pending_answer`-Write. Ein NEUER Prozess darf WEDER
    die GM- NOCH die Persona-Anfrage wiederholen."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        _setup(base)
        first = _run_child(base, "pending_answer_fail")
        assert first["faults"] == ["pending_answer_fail"], first
        assert first["error"] is not None and first["error"]["type"] == "OSError", first
        assert len(first["calls"]["gm"]) == 1 and len(first["calls"]["persona"]) == 1, first
        assert QUESTION in first["accounted_result_texts"] and ANSWER in first["accounted_result_texts"], (
            f"beide bereits empfangenen Texte muessen trotz Checkpoint-Fehler durabel im "
            f"Requestledger stehen: {first}"
        )
        initial_text = first["calls"]["gm"][0]["text"]
        retry = _run_child(base, "normal")
        assert retry["pid"] != first["pid"], "Wiederaufnahme muss ein ECHTER neuer Prozess sein"
        # Beide bereits empfangenen Texte (Turn 0 Frage+Antwort) duerfen NICHT
        # erneut angefordert werden -- Turn 1 (die naechste, echte GENUINE
        # neue Frage, hier bereits der Save-Reply) IST ein legitimer neuer
        # GM-Call, kein Duplikat.
        repeated = [c for c in retry["calls"]["gm"] if c["text"] == initial_text]
        assert not repeated, f"SL-Frage darf nicht erneut angefordert werden: {retry}"
        assert not retry["calls"]["persona"], (
            f"bereits empfangene Personaantwort darf nicht erneut angefordert werden: {retry}"
        )
        assert retry["ready_coherent"], retry


def test_pending_reply_checkpoint_failure_on_received_valid_save_does_not_resend():
    """C2: der GM-Reply, der bereits den gueltigen ersten Save enthaelt,
    wurde empfangen und dauerhaft `accounted` -- ERST DANACH scheitert der
    lokale `record_pending_reply`-Write (VOR `complete_with_save`). Ein
    NEUER Prozess darf den bereits erhaltenen Save-Reply NICHT erneut
    anfordern (kein zweiter voller Turn: keine neue GM- UND keine neue
    Persona-Anfrage)."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        _setup(base)
        first = _run_child(base, "pending_reply_save_fail")
        assert first["faults"] == ["pending_reply_save_fail"], first
        assert first["error"] is not None and first["error"]["type"] == "OSError", first
        assert len(first["calls"]["gm"]) == 2 and len(first["calls"]["persona"]) == 1, (
            f"Turn 0 (Frage+Antwort) muss bereits vollstaendig abgeschlossen sein, Turn 1 "
            f"(Save-Reply) muss empfangen, aber nicht mehr checkpointed sein: {first}"
        )
        assert _fenced(_block(pk="alpha")) in first["accounted_result_texts"], (
            f"der bereits empfangene Save-Reply muss durabel im Requestledger stehen: {first}"
        )
        retry = _run_child(base, "forbid_calls")
        assert retry["pid"] != first["pid"], "Wiederaufnahme muss ein ECHTER neuer Prozess sein"
        assert not retry["calls"]["gm"] and not retry["calls"]["persona"], (
            f"der bereits empfangene Save-Reply darf NICHT erneut angefordert werden -- "
            f"vollstaendige requestfreie Wiederherstellung: {retry}"
        )
        assert retry["ready_coherent"], retry


def test_persona_receiver_gets_own_profile_and_own_history_real_http():
    """C3: der reale `PersonaApiDriver` gegen einen Loopback-Server zeigt das
    eigene Profil im ersten Request und die eigene vorherige Antwort im
    zweiten -- kein fremdes Profil (zweite Persona 'beta' dient nur als
    Fremddaten-Sichtgrenzenkontrolle, wird selbst nicht erschaffen)."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        _setup(base, ("alpha", "beta"))
        q2 = "SYNTHETIC_CONTINUITY_Q2: Welchen Rufnamen waehlst du?"
        answer2 = "SYNTHETIC_CONTINUITY_A2: Morgenrot."
        gm_calls: list[str] = []

        class GM:
            output_limit_tokens = 50

            def turn(self, idx, text, output_limit_tokens=None):
                gm_calls.append(text)
                i = len(gm_calls)
                return {
                    "content": [QUESTION, q2, _fenced(_block("alpha"))][i - 1],
                    "usage": {"prompt_tokens": 4, "completion_tokens": 4},
                }

        responses = [
            (200, {"choices": [{"message": {"content": txt}}], "usage": {"prompt_tokens": 4, "completion_tokens": 4}})
            for txt in (ANSWER, answer2)
        ]
        with FakeHTTPServer(responses) as server:
            driver = PersonaApiDriver(PersonaApiConfig(server.base_url, "SYNTHETIC_KEY", "synthetic-worker-test", max_tokens=50), "alpha")
            advance_one_persona_creation(
                **_kwargs(base, "alpha"), gm_transport_factory=lambda: GM(), persona_driver_factory=lambda pk: driver,
            )
            bodies = [json.loads(c["body"]) for c in server.calls]
        texts = [json.dumps(d["messages"], ensure_ascii=False) for d in bodies]
        assert len(bodies) == 2, bodies
        assert "OWN_PROFILE_MARKER_alpha" in texts[0], "eigenes Profil fehlt im ersten Persona-Request"
        assert ANSWER in texts[1], "eigene vorherige Antwort fehlt im zweiten Persona-Request"
        assert all("OWN_PROFILE_MARKER_beta" not in s for s in texts), "fremdes Profil ('beta') ist sichtbar geworden"


def test_finish_received_internal_write_failure_leaves_durable_result_and_retry_converges():
    """C2-Nacharbeit (End-Critic-Befund 1, 2026-09-25, MAIN-DATENWEGENTSCHEIDUNG.md
    §6 viertes Fenster 'vor/nach received/accounted'): ein gewoehnlicher OSError
    GENAU zwischen `finish_received()`s erstem Write (state=received, `result_text`
    bereits gesetzt) und dem zweiten Write (state=accounted, dazwischen `add_seconds`/
    `record_usd_delta`) darf (1) die bereits empfangene SL-Frage nicht verlieren --
    sie bleibt durabel/wiederverwendbar, AUCH OHNE `state=accounted` -- und (2) einen
    NEUEN Wiederaufnahmeversuch fuer dieselbe Persona nicht an einem permanenten
    `OpenReservationExistsError`-Deadlock scheitern lassen (End-Critic-Befund: vor
    dieser Nacharbeit blieb der Datensatz fuer `find_durable_result()` unsichtbar,
    WAEHREND `begin()`s Dedup ihn gleichzeitig als offen sperrte). Ein Direktaufruf
    von `advance_one_persona_creation` (wie hier, kein Batch) propagiert den Fehler
    weiterhin wie jede andere bestehende Checkpoint-Write-Naht in dieser Datei --
    nur der anschliessende NEUE Versuch muss konvergieren, nicht der erste."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        _setup(base)
        first = _run_child(base, "ledger_internal_fault")
        assert first["faults"] == ["ledger_internal_fault"], first
        assert first["error"] is not None and first["error"]["type"] == "OSError", (
            f"ein Direktaufruf von advance_one_persona_creation muss den Fehler weiterhin "
            f"propagieren, kein stilles Verschlucken bei Einzelaufruf: {first}"
        )
        assert len(first["calls"]["gm"]) == 1 and not first["calls"]["persona"], (
            f"der ledger-interne Fehler muss VOR der Personaanfrage auftreten: {first}"
        )
        assert QUESTION in first["durable_result_texts"], (
            f"die empfangene SL-Frage muss trotz haengengebliebenem state=received bereits "
            f"durabel/wiederverwendbar sein: {first}"
        )
        assert QUESTION not in first["accounted_result_texts"], (
            f"der Datensatz darf NICHT faelschlich als 'accounted' erscheinen, wenn der zweite "
            f"interne Write tatsaechlich fehlgeschlagen ist: {first}"
        )
        initial_text = first["calls"]["gm"][0]["text"]
        retry = _run_child(base, "normal")
        assert retry["pid"] != first["pid"], "Wiederaufnahme muss ein ECHTER neuer Prozess sein"
        assert retry["error"] is None, (
            f"Wiederaufnahme darf NICHT an einem permanenten OpenReservationExistsError-"
            f"Deadlock scheitern: {retry}"
        )
        repeated = [c for c in retry["calls"]["gm"] if c["text"] == initial_text]
        assert not repeated, (
            f"bereits empfangene SL-Frage darf nach dem ledger-internen Fehler NICHT erneut "
            f"angefordert werden: {retry}"
        )
        assert retry["outcome"]["status"] == "completed", retry
        assert retry["ready_coherent"], retry


def test_community_batch_isolates_ledger_internal_failure_between_personas():
    """C2-Nacharbeit (End-Critic-Befund 1, 2026-09-25): `advance_community_
    creation`s eigener, oben dokumentierter Modulvertrag ('Fehler/Ablehnung/
    Blockade EINER Persona darf die uebrigen Mitglieder NICHT anhalten') muss
    auch fuer einen unerwarteten `OSError` INNERHALB von `request_ledger.
    finish_received()` gelten, nicht nur fuer die bereits explizit
    abgefangenen Fehlerarten (Transport-/Adapterfehler, Publikationsnaehte)
    -- End-Critic Experiment 2 zeigte vor dieser Nacharbeit, dass eine
    komplett gesunde zweite Persona im selben Batch-Aufruf NIE versucht
    wurde, weil die erste Persona den ganzen Aufruf mit einer ungefangenen
    Ausnahme abbrach."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        _setup(base, ("alpha_first", "beta_second"))
        out = _run_child(base, "batch_ledger_internal_fault")
        assert out["faults"] == ["batch_ledger_internal_fault"], out
        outcomes = {o["persona_key"]: o for o in out["outcomes"]}
        assert set(outcomes) == {"alpha_first", "beta_second"}, (
            f"beide geplanten Personas muessen einen eigenen Outcome erhalten: {out}"
        )
        assert outcomes["alpha_first"]["status"] == "error", outcomes
        assert outcomes["beta_second"]["status"] == "completed", (
            f"eine gesunde zweite Persona muss trotz Fehlschlag der ersten vollstaendig "
            f"abgeschlossen werden -- keine Blockade des gesamten Batches: {outcomes}"
        )


def main() -> int:
    tests = [
        test_publication_failure_recovers_without_new_model_call,
        test_persona_error_after_received_gm_question_does_not_resend_initial_prompt,
        test_step_write_failure_after_both_received_does_not_repeat_either_request,
        test_pending_reply_checkpoint_failure_does_not_resend_received_gm_question,
        test_pending_answer_checkpoint_failure_does_not_resend_either_request,
        test_pending_reply_checkpoint_failure_on_received_valid_save_does_not_resend,
        test_persona_receiver_gets_own_profile_and_own_history_real_http,
        test_finish_received_internal_write_failure_leaves_durable_result_and_retry_converges,
        test_community_batch_isolates_ledger_internal_failure_between_personas,
    ]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR {t.__name__}:")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} Tests bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    if "--child" in sys.argv:
        import argparse
        p = argparse.ArgumentParser()
        p.add_argument("--child", action="store_true")
        p.add_argument("--base", type=Path, required=True)
        p.add_argument("--mode", default="normal")
        p.add_argument("--pk", default="alpha")
        args = p.parse_args()
        _child_main(args.base, args.mode, args.pk)
        raise SystemExit(0)
    raise SystemExit(main())
