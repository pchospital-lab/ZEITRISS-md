#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_ux10_known_ai_overview_nonempty_2026_10_05.py —
dedizierter UX10-Einzeltest (W8-Rest, s. BRIEF.md "Kleiner Zusatz"):
`_known_ai_overview()` mit einer NICHT-LEEREN Community (bestehende Personas
mit `personas_written`) VOR `_local_round_select_ai()`.

Bestehende UX10-Teilproben (`test_ux1_g02_steuervertrag_real_inputs_2026_10_05.
py:test_help_at_select_ai_prompt_keeps_setup_alive`) laufen OHNE konfigurierten
`run_dir` -- `_known_ai_overview()` liefert dort strukturell IMMER `[]` (leere
Community), der namens-/herkunftssichtbare Listenpfad selbst bleibt dadurch
ungetestet. Dieser Test schliesst genau diese Luecke:

- eine ECHTE, bereits bestaetigte Spielgemeinschaft (`community_bootstrap.
  bootstrap_community`, derselbe Produktweg wie `_cmd_community`) mit
  mehreren Personas existiert VOR dem Aufruf.
- `_known_ai_overview()` liefert fuer jede davon einen lesbaren
  `(persona_key, label)`-Eintrag mit sichtbarer Herkunft ("Herkunft: ..."),
  keine erfundenen/disjunkten Pools (exakt dieselbe Menge wie
  `bootstrap.personas_written`).
- weder `_known_ai_overview()` selbst noch der aufrufende `_local_round_
  select_ai()` (der die Liste VOR der eigentlichen Eingabe anzeigt) loesen
  irgendeinen Persona-/GM-Call aus -- 0 Calls, reines Ansehen (UX03/UX10:
  "Ansehen = 0 Calls").

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs."""
from __future__ import annotations

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

from mmo_sim.ui.tui import TuiSession  # noqa: E402
import _a24_local_support as sup  # noqa: E402


class _CountingPersonaFactory:
    def __init__(self):
        self.calls = 0

    def __call__(self, persona_key: str):
        self.calls += 1
        raise AssertionError(f"UX10: reines Ansehen darf keinen Persona-Call ausloesen ({persona_key!r})")


class _CountingGm:
    def __init__(self):
        self.calls = 0

    def turn(self, *a, **kw):
        self.calls += 1
        raise AssertionError("UX10: reines Ansehen darf keinen GM-Call ausloesen")


def test_known_ai_overview_with_nonempty_community_shows_named_origin_visible_entries_zero_calls():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        pid = "ux10-tester"
        community_id = f"community-{pid}"
        env = sup.bootstrap_six_persona_community(root, community_id)
        written = set(env["bootstrap"].personas_written)
        assert written, "Testvoraussetzung: Community muss real nicht-leer sein"

        persona_factory = _CountingPersonaFactory()
        gm = _CountingGm()
        session = TuiSession(
            onboarding_dir=env["onboarding_dir"], catalog_dir=env["catalog_dir"], participant_id=pid,
            run_dir=env["run_dir"], states_dir=env["states_dir"], schema_path=env["schema"],
            gm_transport_factory=lambda: gm, persona_driver_factory=persona_factory,
        )

        overview = session._known_ai_overview()
        assert overview, "nicht-leere Community muss sichtbare Eintraege liefern (kein leerer Fallback)"
        overview_keys = {pk for pk, _label in overview}
        # Kein Erfinden/Disjunktsein -- exakt dieselbe Menge wie der reale
        # Bootstrap-Bestand, kein Teilauszug, kein Fremdeintrag.
        assert overview_keys == written, (overview_keys, written)
        for pk, label in overview:
            assert pk, "persona_key muss lesbar/nicht leer sein"
            assert "Herkunft:" in label, (pk, label)
        assert persona_factory.calls == 0, "Ansehen allein darf keinen Persona-Call ausloesen (UX10)"
        assert gm.calls == 0, "Ansehen allein darf keinen GM-Call ausloesen (UX03/UX10)"

        # Der eigentliche Aufrufer (`_local_round_select_ai`) zeigt dieselbe
        # Liste VOR der Eingabe -- namens-/herkunftssichtbar, weiterhin 0 Calls.
        printed: list[str] = []
        session._print = printed.append
        session._input = lambda prompt="": ""  # leer = keine Auswahl getroffen
        tokens = session._local_round_select_ai()
        assert tokens is None or tokens == [], tokens
        assert any("Bekannte KI-Mitspieler" in p for p in printed), printed
        for pk in written:
            assert any(pk in p for p in printed), (pk, printed)
        assert any("Herkunft:" in p for p in printed), printed
        assert persona_factory.calls == 0
        assert gm.calls == 0


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
