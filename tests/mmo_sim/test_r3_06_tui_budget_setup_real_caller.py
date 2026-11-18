#!/usr/bin/env python3
"""
tests/mmo_sim/test_r3_06_tui_budget_setup_real_caller.py — R3-06
(ZR-ALTAIR-UPDATER-SPIELTEST-NACHZUG-20261118-r3): treibt den ECHTEN
Aufrufer `mmo_sim.ui.tui.TuiSession._cmd_new_or_switch_character()` an --
nicht nur `core.admission.grant_operator_budget` direkt. Vorher musste ein
Betreiber `lab.status.json` von Hand anlegen, bevor der allererste
Erschaffungsdialog (und damit der erste echte, kostenpflichtige Zug)
ueberhaupt moeglich war (General-Befund R3-06, r2-Spieltestbeleg). Beweist:
ein Host OHNE jede vorhandene `lab.status.json` erreicht ueber den
normalen Menuweg ('neue Erschaffung') jetzt einen bedienbaren, in der
Oberflaeche sichtbaren Dialog, der eine begrenzte Betreiberfreigabe
herstellt UND danach den echten SL-Dialog tatsaechlich erreicht (kein
Handedit, kein Deaktivieren des Gates, keine automatische unbegrenzte
Freigabe).

Pure Python, nur `assert`, echter Exitcode. Einziges aeusserstes Fake: der
GM-Transport (Netzwerkrand) -- Admission/Onboarding/Catalog laufen echt."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_block_text  # noqa: E402

from mmo_sim.core.admission import _status_path  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


class _GM:
    """Aeusserstes GM-Transport-Fake (Muster: test_local_tokenhost_
    creation_2026_11_14.py:_GM) -- liefert sofort einen vollstaendigen
    v7-Save-Block, der Dialog schliesst im ersten Turn ab."""

    def __init__(self, reply_text: str):
        self.reply_text = reply_text
        self.is_dollar_billed = True
        self.output_limit_tokens = 4096
        self.base_url = None
        self.calls = 0

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls += 1
        return {
            "content": self.reply_text, "usage": {"prompt_tokens": 12, "completion_tokens": 8},
            "sources": [], "latency_s": 0.01, "chat_id": "r3-06-test",
        }


def _scripted_input(answers):
    it = iter(answers)

    def read(prompt=""):
        try:
            return next(it)
        except StopIteration:
            raise EOFError()

    return read


def _new_env(root: Path):
    states_dir, run_dir = root / "states", root / "run"
    onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
    for d in (states_dir, run_dir, onboarding_dir, catalog_dir):
        d.mkdir(parents=True, exist_ok=True)
    return states_dir, run_dir, onboarding_dir, catalog_dir


def test_host_without_any_lab_status_json_reaches_real_creation_dialog_after_setup():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(base)
        assert not _status_path(run_dir).exists(), "Vorbedingung: wirklich kein Handedit vorhanden"

        gm = _GM(full_v7_block_text("nova-1", name="Nova", level=1))
        shown: list[str] = []
        session = TuiSession(
            onboarding_dir, catalog_dir, "p1",
            input_fn=_scripted_input(["j", "", "", ""]),  # Setup: ja, dann 3x Default-Vorschlag
            print_fn=shown.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda: gm,
        )
        session._cmd_new_or_switch_character()

        assert gm.calls >= 1, (
            "R3-01-artiger Befund fuer R3-06: der echte SL-Dialog wurde NIE erreicht -- "
            "Admission-Gate hat trotz normaler Betreiberfreigabe weiter blockiert."
        )
        assert not any("blockiert" in s for s in shown), shown
        assert _status_path(run_dir).exists(), "Betreiberfreigabe muss normal (ueber die TUI) entstanden sein"
        data = json.loads(_status_path(run_dir).read_text(encoding="utf-8"))
        assert data.get("provider_free") is not True, (
            "eine echte Betreiberfreigabe darf NIE als provider_free (Testdouble) markiert sein"
        )
        assert isinstance(data.get("max_turns"), int) and data["max_turns"] > 0
        assert any("Freigabe eingerichtet" in s for s in shown), shown


def test_declining_the_setup_offer_leaves_the_gate_blocked_and_no_file_written():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(base)
        gm = _GM(full_v7_block_text("nova-2", name="Nova", level=1))
        shown: list[str] = []
        session = TuiSession(
            onboarding_dir, catalog_dir, "p1",
            input_fn=_scripted_input(["n"]),  # Setup ausdruecklich ablehnen
            print_fn=shown.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda: gm,
        )
        session._cmd_new_or_switch_character()

        assert gm.calls == 0, "kein Modellaufruf ohne Freigabe"
        assert not _status_path(run_dir).exists(), "kein heimliches Anlegen ohne Zustimmung"
        assert any("blockiert" in s for s in shown), shown


def test_offer_is_not_shown_again_once_a_real_authorization_already_exists():
    """R3-06-Abnahme: nur der ECHTE Erstfall (gar keine `lab.status.json`)
    bietet den Setup-Dialog an -- eine bereits bestehende, nur erschoepfte
    Grenze darf NICHT ueber diese Stelle heimlich hochgesetzt werden (das
    ist R3-07s getrennte Zustaendigkeit)."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(base)
        from mmo_sim.core.admission import grant_operator_budget
        grant_operator_budget(run_dir, max_turns=0, max_seconds=1.0, max_usd=0.0)  # bereits erschoepft

        gm = _GM(full_v7_block_text("nova-3", name="Nova", level=1))
        shown: list[str] = []
        session = TuiSession(
            onboarding_dir, catalog_dir, "p1",
            input_fn=_scripted_input([]),  # keine Prompts erwartet
            print_fn=shown.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda: gm,
        )
        session._cmd_new_or_switch_character()
        assert gm.calls == 0
        assert any("blockiert" in s for s in shown), shown
        assert not any("Freigabe eingerichtet" in s for s in shown), shown


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
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
            import traceback
            print(f"ERROR {t.__name__}:")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} Tests bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
