#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_betreiber_o5_erschaffung_abandon_guard_2026_11_03.py --
ZR-BETREIBER-GASTERSCHAFFUNG-20261103-R1, O5 (design.md §3/§6).

1. Betreiber-freigegebene Gast-Erschaffung OHNE vorab mitgebrachtes JSON:
   `creation_service.run_admitted_creation_dialog` liefert bei einer SOFORT
   gueltigen SL-Antwort (erster Turn bereits ein schema-gueltiger v7-Block)
   `status == "completed"` UND der persoenliche Save landet real ueber
   `onboarding.complete_with_save` (nicht irgendeinen Nebenweg) -- geprueft
   ueber `onboarding.peek(...)`.final_save.
2. `host_capable` ist in `creation_service.py`/`onboarding.py` STRUKTURELL
   nicht vorhanden -- kein Parameter, kein Attribut, keine Textstelle, die
   als Bypass dienen koennte (grep-belegt, hier als echte Assertion ueber
   `inspect.getsource`, nicht nur behauptet).
3. Durabler Abbruch (O3/O5): nach `onboarding.abandon(...)` wirft ein
   direkter `onboarding.complete_with_save`-Durchgriff (derselbe Aufruf, den
   `creation_service` bei einer gueltigen Antwort normalerweise macht)
   `ValueError` -- der Erschaffungsauftrag bleibt `abandoned`, KEIN
   Wiederbeleben."""
from __future__ import annotations

import inspect
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

from _full_v7_fixture import full_v7_save  # noqa: E402

import mmo_sim.core.creation_service as creation_service  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.creation_service import ReplyResult, run_admitted_creation_dialog  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402


def _never_called_get_reply(turn_idx: int, sl_text: str) -> ReplyResult:
    raise AssertionError("get_reply sollte hier nie aufgerufen werden -- die SL liefert den Save direkt.")


class _OneShotGm:
    """Modellrand-Double: liefert GENAU EINE vorgegebene Antwort, wirft bei
    jedem weiteren Call (Beleg gegen einen unerwarteten zweiten Turn)."""

    def __init__(self, content: str):
        self._content = content
        self.calls = 0

    def turn(self, turn_idx: int, user_text: str) -> dict:
        self.calls += 1
        if self.calls > 1:
            raise AssertionError("_OneShotGm: unerwarteter zweiter Turn.")
        return {"content": self._content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "o5-fake"}


def _as_json_reply(block: dict) -> str:
    import json
    return "```json\n" + json.dumps(block, ensure_ascii=False) + "\n```"


def test_o5_betreiber_freigegebene_erschaffung_ohne_prior_json_persoenlicher_save():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, onboarding_dir = root / "run", root / "onboarding"
        write_test_profile(run_dir)
        participant_id = "gast_o5"
        char_id = "CHR-O5-001"
        onboarding.start_or_resume(onboarding_dir, participant_id)

        block = full_v7_save(char_id, name="Elin")
        gm = _OneShotGm(_as_json_reply(block))

        outcome = run_admitted_creation_dialog(
            run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=participant_id,
            turn_idx_start=0, initial_outgoing="Betreiber hat die Erschaffung freigegeben.",
            gm_transport=gm, get_reply=_never_called_get_reply,
            harvest_validator=ZeitrissHarvestValidator(), role="creation_dialog",
        )
        assert outcome.status == "completed", outcome
        assert outcome.save_block == block, outcome
        assert gm.calls == 1, "kein zweiter Turn noetig -- der erste war bereits gueltig."

        state = onboarding.peek(onboarding_dir, participant_id)
        assert state is not None and state.status == "completed", state
        assert state.final_save == block, "persoenlicher Save muss real ueber complete_with_save gelandet sein."


def test_o5_host_capable_ist_in_creation_core_strukturell_nicht_vorhanden():
    creation_src = inspect.getsource(creation_service)
    onboarding_src = inspect.getsource(onboarding)
    assert "host_capable" not in creation_src, (
        "host_capable darf in creation_service.py nicht als Bypass auftauchen."
    )
    assert "host_capable" not in onboarding_src, (
        "host_capable darf in onboarding.py nicht als Bypass auftauchen."
    )
    sig = inspect.signature(run_admitted_creation_dialog)
    assert "host_capable" not in sig.parameters
    sig2 = inspect.signature(onboarding.complete_with_save)
    assert "host_capable" not in sig2.parameters


def test_o5_nach_abandon_kein_complete_with_save_durchgriff():
    with tempfile.TemporaryDirectory() as td:
        onboarding_dir = Path(td) / "onboarding"
        participant_id = "gast_o5_abandoned"
        char_id = "CHR-O5-002"
        onboarding.start_or_resume(onboarding_dir, participant_id)
        onboarding.abandon(onboarding_dir, participant_id)

        state_before = onboarding.peek(onboarding_dir, participant_id)
        assert state_before is not None and state_before.status == "abandoned", state_before

        block = full_v7_save(char_id, name="Elin")
        try:
            onboarding.complete_with_save(onboarding_dir, participant_id, block, ZeitrissHarvestValidator(), char_id)
            raise AssertionError("complete_with_save haette nach abandon() ValueError werfen muessen.")
        except ValueError as e:
            assert "abandoned" in str(e) or "abgebrochen" in str(e), str(e)

        state_after = onboarding.peek(onboarding_dir, participant_id)
        assert state_after is not None and state_after.status == "abandoned", (
            "ein abgelehnter complete_with_save-Versuch darf den Status nicht veraendern."
        )
        assert state_after.final_save is None, "kein Save darf trotz Ablehnung geschrieben werden."

        # Dasselbe gilt fuer den Best-Effort-Zwilling (derselbe Guard).
        try:
            onboarding.complete_with_save_best_effort(onboarding_dir, participant_id, block)
            raise AssertionError("complete_with_save_best_effort haette nach abandon() ValueError werfen muessen.")
        except ValueError:
            pass


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
