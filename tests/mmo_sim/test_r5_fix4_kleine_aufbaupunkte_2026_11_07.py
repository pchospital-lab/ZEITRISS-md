#!/usr/bin/env python3
"""
tests/mmo_sim/test_r5_fix4_kleine_aufbaupunkte_2026_11_07.py -- ZR-
VOLLENDUNG-OHNE-LAN-NACHZUG-20261107-R5 (Arbeitsblock 2 Punkt 3, UX-Review
§"Kleine verbleibende Aufbau-/Dokupunkte"). Deckt die drei Produktpunkte
von FIX 4 ab (Doku-Angleichung hat keinen eigenen Code-Test):

1. Ungueltige Figurbestaetigung (`_local_round_confirm_figure`) darf NICHT
   wie eine Ablehnung den Aufbau verwerfen -- nur eine ECHTE Ablehnung
   ('n') bleibt der bestehende Abbruch-Rueckweg.
2. Beim Zuruecklaufen muss die vorherige Menschen-/KI-Auswahl sichtbar
   wieder angeboten UND bei leerer neuer Eingabe BEHALTEN werden (nicht
   auf den Default zurueckgesetzt); eine bewusst leere Auswahl OHNE
   vorherige Auswahl bedeutet weiterhin 'keine'/'nur du' (unveraendert).
3. Die KI-Uebersicht (`_known_ai_overview`) zeigt jetzt zusaetzlich den
   Figur-/Standstatus jeder Persona -- der technische Platzhalter
   'NOCH_NICHT_ERSCHAFFEN' (von `community_bootstrap`/`_synthetic_
   starter_pool` fuer eine noch nicht erschaffene Persona geschrieben)
   wird dabei NICHT faelschlich als echte Figur angezeigt.

Pure Python, nur `assert`, echter Exitcode, synthetische Temp-Dirs, 0
echte GM-/Modellcalls."""
from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import _a24_local_support as sup  # noqa: E402

from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402


def _scripted_input(values):
    q = list(values)

    def _fn(prompt: str = "") -> str:
        if q:
            return q.pop(0)
        raise EOFError()

    return _fn


def test_invalid_figure_answer_retries_at_same_step_real_reject_still_aborts():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        registry_dir = root / "registry"
        onboarding_dir = root / "onboarding"
        states_dir = root / "states"
        run_dir = root / "run"
        pid = "fix4_mensch_a"
        human = sup.register_human(registry_dir, "Fix4 Mensch A")
        participant_id = human.participant_id
        sup.onboard_human_figure(
            registry_dir, participant_id, onboarding_dir, states_dir, run_dir,
            "CHR-FIX4-A", "Asa", "ASAOPS",
        )
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=root / "catalog",
            participant_id=pid, run_dir=run_dir, states_dir=states_dir,
            schema_path=sup.SCHEMA, print_fn=printed.append, host_capable=True,
        )
        # Ein Tippfehler ('vllt' statt 'j'/'n') ist 'invalid', KEINE
        # Ablehnung -- muss am selben Schritt erklaert+erneut gefragt
        # werden; erst das zweite 'j' bestaetigt wirklich.
        session._input = _scripted_input(["vllt", "j"])
        confirmed = session._local_round_confirm_figure(participant_id)
        assert confirmed is True, "Eine gueltige Zustimmung NACH einer ungueltigen Antwort muss durchgehen."
        out = "\n".join(printed)
        assert "keine erkannte Ja-/Nein-Antwort" in out, out
        assert "Aufbau bleibt erhalten" in out or "kein Abbruch" in out, out

        # Gegenprobe: eine ECHTE Ablehnung ('n') bleibt der bestehende,
        # akzeptierte Abbruch-Rueckweg (unveraendert).
        printed.clear()
        session._input = _scripted_input(["n"])
        confirmed2 = session._local_round_confirm_figure(participant_id)
        assert confirmed2 is False, "Eine echte Ablehnung muss weiterhin False liefern (Abbruch)."
        assert "nicht bestaetigt" in "\n".join(printed)


def test_backward_navigation_shows_and_keeps_previous_human_selection():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        registry_dir = root / "registry"
        onboarding_dir = root / "onboarding"
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=root / "catalog",
            participant_id="fix4_self", run_dir=root / "run", print_fn=printed.append,
            host_capable=True,
        )
        session.states_dir = root / "states"
        human_b = sup.register_human(registry_dir, "Fix4 Mensch B")
        prior_selection = ["fix4_self", human_b.participant_id]

        # Erneuter Eintritt NACH '/zurueck' (current = vorherige Auswahl) --
        # leere neue Eingabe muss sie BEHALTEN, nicht auf 'nur du' zuruecksetzen.
        session._input = _scripted_input([""])
        result = session._local_round_select_humans(current=prior_selection)
        assert result == prior_selection, (result, prior_selection)
        out = "\n".join(printed)
        assert "Aktuelle Auswahl" in out, out
        assert human_b.participant_id in out, out

        # Erster Besuch (current == Default [self.participant_id], KEINE
        # echte vorherige Auswahl) -- leere Eingabe bedeutet weiterhin 'nur
        # du', UNVERAENDERT gegenueber dem bisherigen Verhalten.
        printed.clear()
        session._input = _scripted_input([""])
        first_visit = session._local_round_select_humans(current=["fix4_self"])
        assert first_visit == ["fix4_self"], first_visit
        assert "Aktuelle Auswahl" not in "\n".join(printed)


def test_known_ai_overview_shows_figure_status_and_hides_unfounded_placeholder():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        pid = "fix4_ai_overview_tester"
        community_id = f"community-{pid}"
        env = sup.bootstrap_six_persona_community(root, community_id)
        written = sorted(env["bootstrap"].personas_written)
        assert written

        session = TuiSession(
            onboarding_dir=env["onboarding_dir"], catalog_dir=env["catalog_dir"], participant_id=pid,
            run_dir=env["run_dir"], states_dir=env["states_dir"], schema_path=env["schema"],
        )
        overview = dict(session._known_ai_overview())
        # Jede frisch gebootstrappte Persona hat NUR den technischen
        # Platzhalter 'NOCH_NICHT_ERSCHAFFEN' (bootstrap_community/
        # _synthetic_starter_pool) -- das darf NICHT als echte Figur
        # erscheinen.
        for pk in written:
            assert "noch keine erkennbare Figur/Stand" in overview[pk], (pk, overview[pk])
            assert "NOCH_NICHT_ERSCHAFFEN" not in overview[pk], (pk, overview[pk])

        # Jetzt EINE Persona mit einer echten, abgeschlossenen Figur
        # ausstatten (direkter Store-Write derselben Felder, die der echte
        # Erschaffungsdialog am Ende schreibt) -- deren Label muss die
        # Figur jetzt zeigen.
        bound_pk = written[0]
        ps_store = PersonaStateStore(schema_path=env["schema"])
        state = ps_store.load_state(bound_pk, states_dir=env["states_dir"])
        state["plays_char"] = {
            "save_file": f"{bound_pk}.json", "character_id": "CHR-FIX4-AI-BOUND",
            "name": "Rook", "callsign": "ROOK",
        }
        ps_store.save_state(bound_pk, state, states_dir=env["states_dir"])

        overview_after = dict(session._known_ai_overview())
        assert "Figur: Rook (CHR-FIX4-AI-BOUND)" in overview_after[bound_pk], overview_after[bound_pk]
        other_pk = written[1]
        assert "noch keine erkennbare Figur/Stand" in overview_after[other_pk], overview_after[other_pk]


def main() -> int:
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
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
    raise SystemExit(main())
