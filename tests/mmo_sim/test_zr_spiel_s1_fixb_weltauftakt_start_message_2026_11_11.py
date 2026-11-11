#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_spiel_s1_fixb_weltauftakt_start_message_2026_11_11.py —
ZR-SPIEL-S1 Fix B (LINUS-SPEC.md §Fix B): der frische Erschaffungseinstieg
sendete als ersten Request nur den reinen Erschaffungssatz ("Ich moechte
einen neuen Chrononauten erschaffen...") -- der GM ging direkt in die
Erschaffung, der ausfuehrliche Masterprompt-Sessionstart-Weltauftakt
(Welt/ITI/Nullzeit, Fraktionen, Sprung-Gefuehl) blieb aus.

Fix: `ui/tui.py:_cmd_new_or_switch_character`s `initial_outgoing`-Default
(NUR der `else`-Zweig bei leeren `state.steps`) signalisiert jetzt einen
echten Neustart und fordert den kanonischen Sessionstart-Weltauftakt VOR
der Erschaffung. Der Resume-Zweig (`state.steps[-1]["answer"]`) bleibt
UNVERAENDERT -- eine fortgesetzte Erschaffung wiederholt den Weltauftakt
NICHT.

Testet am echten Verzweigungsort: ein Fake-GM-Transport zeichnet die erste
tatsaechlich an `gm_transport.turn(...)` uebergebene Nachricht auf (derselbe
Aufbau wie `test_ux1_r4_creation_error_redaction_2026_10_05.py::
_MarkerRaisingGm`), KEIN isolierter Nachbau der Stringliteral-Logik. Kein
Netzwerk-/Modellaufruf -- der Fake wirft sofort nach dem Aufzeichnen."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
_OLD_FRESH_MESSAGE = (
    "Ich moechte einen neuen Chrononauten erschaffen. Fuehre mich Schritt fuer Schritt durch die Erschaffung."
)


class _RecordingGm:
    """Zeichnet genau den ersten `turn()`-Aufruf auf und wirft danach sofort
    -- kein echter Modellaufruf, kein zweiter Request noetig."""

    def __init__(self):
        self.calls: list[tuple[int, str]] = []

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append((idx, text))
        raise RuntimeError("_RecordingGm: bewusster Stopp nach Aufzeichnung")


def _env(root: Path):
    states_dir, run_dir = root / "states", root / "run"
    onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
    states_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    return states_dir, run_dir, onboarding_dir, catalog_dir


def _eof_input(prompt: str = "") -> str:
    raise EOFError()


def test_fresh_start_initial_outgoing_carries_weltauftakt_restart_context():
    """frisch (`state.steps == []`): `initial_outgoing` ist NICHT mehr der
    alte reine Erschaffungssatz, sondern traegt den Neustart-/Weltauftakt-
    Kontext (Sessionstart VOR der Erschaffung)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
        write_test_profile(run_dir)
        gm = _RecordingGm()
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="weltauftakt_fresh",
            input_fn=_eof_input, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda: gm,
        )
        session._cmd_new_or_switch_character()

        assert len(gm.calls) == 1, gm.calls
        turn_idx, outgoing = gm.calls[0]
        assert turn_idx == 0, turn_idx
        assert outgoing != _OLD_FRESH_MESSAGE, (
            "Fix B-Regression: initial_outgoing ist noch der alte reine Erschaffungssatz"
        )
        # Minimal-Fix (Flo-Vorgabe): der Erschaffungssatz bleibt erhalten, aber
        # das Stichwort "Einleitung" triggert jetzt den RAG-Zug des
        # spieler-handbuch-Einleitungschunks, und die Reihenfolge ist explizit
        # Einleitung ZUERST, Erschaffung DANACH.
        assert "Einleitung" in outgoing, outgoing
        assert "Weltauftakt" in outgoing, outgoing
        assert "zuerst" in outgoing and "DANACH" in outgoing, outgoing
        assert "neuen Chrononauten erschaffen" in outgoing, outgoing

        state = onboarding.peek(onboarding_dir, "weltauftakt_fresh")
        assert state is not None and state.steps == [], (
            "frischer Einstieg darf vor dem ersten erfolgreichen Zug keine Schritte aufzeichnen"
        )


def test_resume_initial_outgoing_stays_the_existing_last_answer_unchanged():
    """Resume (`state.steps` nicht leer): `initial_outgoing ==
    state.steps[-1]['answer']` -- UNVERAENDERT, der Weltauftakt wird bei
    einer Fortsetzung NICHT wiederholt."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
        write_test_profile(run_dir)
        pid = "weltauftakt_resume"

        onboarding.start_or_resume(onboarding_dir, pid)
        onboarding.record_step(
            onboarding_dir, pid,
            "Wie beginnt deine Zeitreise?", "Ich erwache in einem Rift.",
        )

        gm = _RecordingGm()
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=pid,
            input_fn=_eof_input, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda: gm,
        )
        session._cmd_new_or_switch_character()

        assert len(gm.calls) == 1, gm.calls
        turn_idx, outgoing = gm.calls[0]
        assert turn_idx == 1, (
            f"turn_idx muss den bereits vorhandenen Schritt fortsetzen (len(steps)==1): {turn_idx}"
        )
        assert outgoing == "Ich erwache in einem Rift.", (
            f"Resume-Zweig haette die VORHANDENE letzte Antwort unveraendert weitergeben muessen: {outgoing!r}"
        )
