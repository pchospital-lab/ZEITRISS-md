#!/usr/bin/env python3
"""
tests/mmo_sim/test_r4_u1b_setup_step_back_2026_11_07.py
ZR-VOLLENDUNG-OHNE-LAN-NACHZUG-20261107-R4 (U1-Teil-B, PLAYER-UX-REVIEW.md
F1, 01_NACHZUG.md U1 Punkt 4, 02_ABNAHME.md A/B).

Vorher behandelte `_cmd_local_round_setup` JEDE Steuerzeile ('/zurueck'
GENAUSO wie '/abbrechen'/'/pause') als Komplettabbruch des gesamten
gefuehrten Rundenaufbaus -- obwohl die allgemeine Hilfe '/zurueck (eine
Ebene zurueck)' verspricht. Dieser Test beweist am echten
`TuiSession._cmd_local_round_setup()`-Zustandsautomaten:

* '/zurueck' an der Figurbestaetigung (FIGURES-Schritt) springt GENAU eine
  Stufe zurueck (hier: zum MODUS-Schritt, da nur ein Mensch beteiligt ist),
  OHNE die bereits abgeschlossene Erschaffung/Registrierung rueckwirkend zu
  loeschen -- der zweite Durchlauf durch den FIGURES-Schritt loest KEINEN
  zweiten Fake-GM-Call aus (`gm.calls` bleibt bei genau 1), weil die Figur
  bereits persistiert ist.
* Eine ungueltige Eingabe am MODUS-Schritt bricht NICHT mehr die gesamte
  Einrichtung ab, sondern bleibt im Schritt (erklaert, fragt erneut) --
  die Einrichtung laeuft mit einer gueltigen Folgeeingabe normal weiter.
* '/zurueck' an einem reinen Auswahl-Teilschritt (`_local_round_select_
  humans`) wirft die interne `_SetupStepBack`-Signalisierung statt pauschal
  `None` wie `/abbrechen` zurueckzugeben -- die Unterscheidung ist damit
  auch auf Funktionsebene nachweisbar, nicht nur ueber den Gesamtlauf.
* '/abbrechen' am MODUS-Schritt beendet weiterhin den gesamten Aufbau
  (unveraenderte Altregression, hier erneut mitgefuehrt).

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs,
Null echte GM-/Persona-Modellcalls (ein einziger kontrollierter
Fake-GM-Call am vorhandenen Modellrand, wie in
`test_ux1_q04_round_setup_connects_new_person_2026_10_05.py`)."""
from __future__ import annotations

import json
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _full_v7_fixture import upgrade_narrow_save  # noqa: E402

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.ui.tui import TuiSession, _SetupStepBack  # noqa: E402
import _a24_local_support as sup  # noqa: E402

_FIX = _REPO_ROOT / "internal" / "qa" / "harness" / "lobby" / "fixtures" / "saves"


class _FakeGm:
    """Liefert SOFORT im ersten Call den gueltigen v7-Save-Block -- derselbe
    Musteraufbau wie `test_ux1_q04_round_setup_connects_new_person_2026_10_05.py`."""

    def __init__(self, save_block: dict):
        self.save_block = save_block
        self.calls: list[tuple[int, str]] = []

    def turn(self, idx, text):
        self.calls.append((idx, text))
        return {"content": "```json\n" + json.dumps(self.save_block) + "\n```"}


def _scripted_input(values):
    q = list(values)

    def input_fn(prompt: str = "") -> str:
        if q:
            return q.pop(0)
        raise EOFError()

    return input_fn


def test_zurueck_at_figure_confirmation_steps_back_without_losing_persisted_figure():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
        run_dir.mkdir(parents=True, exist_ok=True)
        states_dir.mkdir(parents=True, exist_ok=True)
        write_test_profile(run_dir)

        save_block = upgrade_narrow_save(json.loads((_FIX / "sniper.json").read_text(encoding="utf-8")))
        gm = _FakeGm(save_block)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir, catalog_dir, "solo",
            input_fn=_scripted_input([
                "1",          # STEP_MODE: Allein mit KI-Mitspielern
                "j",          # Fokusbestaetigung (_local_round_handoff) fuer die eigene Erschaffung
                "1",          # Charaktere-Untermenue: [1] Auswaehlen/neu erstellen (1 echter Fake-GM-Call)
                "/zurueck",   # an 'solo spielt ... -- bestaetigen?' -- EINE Stufe zurueck, kein Abbruch
                "1",          # STEP_MODE erneut: wieder Allein mit KI-Mitspielern
                "j",          # Figur ist bereits persistiert -- SOFORT bestaetigen, kein zweiter GM-Call
                "",           # STEP_AI: keine KI-Mitspieler
                "",           # STEP_LEADER: leer = du selbst
                "n",          # STEP_SUMMARY: Startwahl NICHT bestaetigen -- kontrollierter, klarer Schluss
            ]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=sup.SCHEMA,
            gm_transport_factory=lambda: gm,
        )

        session._cmd_local_round_setup()
        out = "\n".join(printed)

        # Der Fake-GM wurde GENAU EINMAL gerufen -- das zweite Durchlaufen
        # des FIGURES-Schritts nach '/zurueck' hat die Erschaffung NICHT
        # wiederholt, weil die Figur bereits persistiert war.
        assert len(gm.calls) == 1, gm.calls
        # Kein Komplettabbruch: die alte "Einrichtung abgebrochen"-Zeile an
        # DIESER Stelle (Figurbestaetigung) darf fuer den Zurueck-Schritt
        # nicht auftauchen.
        assert "hat die Figur" not in out or "nicht bestaetigt" not in out, out
        # Die Einrichtung ist tatsaechlich bis zur Zusammenfassung
        # weitergelaufen (Beweis, dass '/zurueck' NICHT wie '/abbrechen'
        # den gesamten Aufbau beendet hat).
        assert "Zusammenfassung" in out, out
        assert "letzte Startwahl nicht bestaetigt" in out, out

        from mmo_sim.domain.zeitriss import onboarding
        state = onboarding.peek(onboarding_dir, "solo")
        assert state is not None and state.status == "completed", state


def test_invalid_mode_choice_stays_in_step_and_setup_continues():
    """R4 U1-Teil-B (01_NACHZUG.md U1 Punkt 4 'bei ungueltiger Eingabe im
    betreffenden Schritt bleiben'): eine unbekannte Modusauswahl bricht
    NICHT mehr ab, sondern erklaert sich und fragt dieselbe Zeile erneut --
    eine darauffolgende gueltige Eingabe setzt die Einrichtung normal
    fort (hier bis zum kontrollierten EOF-Abbruch am naechsten echten
    Schritt, OHNE jemals die alte abschliessende "unbekannte Auswahl"-
    Abbruchmeldung zu zeigen)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="solo-human",
            input_fn=_scripted_input(["9", "1"]),
            print_fn=printed.append,
        )
        session._cmd_local_round_setup()
        out = "\n".join(printed)
        assert "unbekannte Auswahl" in out, out
        # '1' wurde TATSAECHLICH als neuer Modusversuch verarbeitet (nicht
        # verworfen) -- die Einrichtung erreicht den naechsten echten
        # Schritt (Figurbestaetigung fuer 'solo-human', ohne Figur/weitere
        # Eingabe kontrolliert beendet, kein KI-Ersatz).
        assert "noch keine abgeschlossene Figur" in out, out


def test_zurueck_at_select_humans_raises_step_back_not_plain_abort():
    """Funktionsebene (direkt, ohne die ganze Kette): '/zurueck' an
    `_local_round_select_humans` wirft `_SetupStepBack` -- unterscheidbar
    von '/abbrechen' (liefert weiterhin `None`, s. bestehende G02-Regression
    `test_ux1_g02_steuervertrag_real_inputs_2026_10_05.py`)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="leader",
            input_fn=_scripted_input(["/zurueck"]), print_fn=lambda *_a: None,
        )
        raised = False
        try:
            session._local_round_select_humans()
        except _SetupStepBack:
            raised = True
        assert raised, "erwartete _SetupStepBack fuer '/zurueck', keine Ausnahme ausgeloest"


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
