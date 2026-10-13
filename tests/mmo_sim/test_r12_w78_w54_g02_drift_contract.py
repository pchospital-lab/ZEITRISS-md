#!/usr/bin/env python3
"""
tests/mmo_sim/test_r12_w78_w54_g02_drift_contract.py — R12-Savegate,
W78-Testvertragsabschluss (GENERALREVIEW.md §Die W54-G02B-Kollision).

W77 fuehrte eine Driftpruefung in `core/save_correction.py` ein: eine
Korrekturantwort, deren Inhalt UEBER die tatsaechlich gemeldeten
Schemafehlerpfade des zuvor gebundenen Entwurfs hinaus abweicht (z.B. ein
geaenderter `level`), gilt als `unjustified_semantic_drift` und wird NICHT
uebernommen — der Dialog pausiert (`paused`), unabhaengig davon, ob die
Antwort selbst schemagueltig ist. Eine reine Formatkorrektur (derselbe
Wert, nur die vom Validator tatsaechlich bemaengelte Struktur repariert)
bleibt dagegen annehmbar (s. die angepasste Fixture in
`test_w54_g02_duplicate_save_id_ambiguity_2026_10_08.py::
test_w54g02b_conflicting_correction_answer_is_never_silently_adopted`).

Dieser Vertrag sichert BEIDE Seiten unabhaengig von jener Datei mit EIGENEN
Figuren/IDs (keine geteilten Fixtures) ueber den echten
`run_admitted_creation_dialog` (kein Stub, kein Mock des Produktpfads):

  test_w78_drift_negative_level_change_after_conflict_is_paused_not_adopted
      — der ALTE Level1->Konflikt3/4->Level9-Ablauf (vor W77 stillschweigend
      `completed`/`adopted`) haelt jetzt an: `paused`/
      `unjustified_semantic_drift`, kein Save, kein `adopted`-Block,
      `attempts_used==2`, drei Transporte, der gebundene Level1 bleibt
      unveraendert, alle drei Requests sind terminal `accounted`.
  test_w78_drift_positive_value_preserving_wallet_fix_is_adopted
      — dieselbe Reise, aber die eindeutige Korrekturantwort ist eine
      wertgleiche Formatkorrektur (Level1, `economy.wallets[cid].balance
      == 500`): `completed`/`adopted` nach denselben drei Transporten/zwei
      Korrekturslots, Ergebnisblock == genau diese Antwort, beide
      unveraenderten v7-Schemas bestehen. Die ersten widersprechenden
      Antworten (conflict_a/conflict_b) werden in BEIDEN Faellen nie
      uebernommen (kein first-wins).

Pure Python, nur `assert`, echter Exitcode — gleiches Muster wie die
Nachbartests. Kein Netz, kein Livecall."""
from __future__ import annotations

import json
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

from _full_v7_fixture import full_v7_save  # noqa: E402 (Fixturehelper, FIXTURE_ONLY)

import mmo_sim.core.request_ledger as request_ledger  # noqa: E402
import mmo_sim.core.save_correction as save_correction  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.creation_service import run_admitted_creation_dialog  # noqa: E402
import mmo_sim.domain.zeitriss.onboarding as onboarding  # noqa: E402
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402
from mmo_sim.domain.zeitriss import save_validation  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402


def fenced(block: dict) -> str:
    return "```json\n" + json.dumps(block) + "\n```"


def _no_persona_poll(*_a, **_k):
    raise AssertionError("W78-Drift-Contract: kein Personapoll im menschlichen Erschaffungsdialog erwartet.")


class _ScriptedGm:
    def __init__(self, contents: list[str]):
        self._contents = list(contents)
        self.calls: list[tuple[int, str]] = []

    def turn(self, turn_idx, text, **kwargs):
        self.calls.append((turn_idx, text))
        if not self._contents:
            raise AssertionError(
                f"W78-Drift-Contract: unerwarteter zusaetzlicher Transport-Call (turn_idx={turn_idx})."
            )
        return {"content": self._contents.pop(0), "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}


def _run_journey(who: str, cid: str, resolved_answer: dict):
    """Gemeinsamer Ablauf beider Faelle: Erstentwurf mit schema-ungueltiger
    Wallet (Level1) -> mehrdeutige Doppelantwort (Level3/4) -> die vom
    jeweiligen Fall uebergebene eindeutige Antwort. Drei synthetische
    Transporte, ein Ursprung + zwei Korrekturslots -- identisches Muster zu
    G02-B, aber eigene Figuren/IDs statt der geteilten Dateifixture."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, onboarding_dir = root / "run", root / "onboarding"
        write_test_profile(run_dir)

        invalid = full_v7_save(cid, name="Flo", level=1)
        invalid["economy"] = {"wallets": {cid: 500}}  # schema-ungueltig -- loest Korrektur aus
        conflict_a = full_v7_save(cid, name="Flo", level=3)
        conflict_b = full_v7_save(cid, name="Flo", level=4)
        assert conflict_a["save_id"] == conflict_b["save_id"] and conflict_a != conflict_b

        onboarding.start_or_resume(onboarding_dir, who)
        gm = _ScriptedGm([
            fenced(invalid),
            fenced(conflict_a) + "\n" + fenced(conflict_b),
            fenced(resolved_answer),
        ])
        outcome = run_admitted_creation_dialog(
            run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=who,
            turn_idx_start=0, initial_outgoing="Erschaffung starten.", gm_transport=gm,
            get_reply=_no_persona_poll, harvest_validator=ZeitrissHarvestValidator(),
            print_fn=lambda _s: None,
        )
        repair_key = save_correction_domain.creation_repair_key(who, cid)
        record = save_correction.load_record(run_dir, repair_key)
        ledger = request_ledger._all_records(run_dir)
        state = onboarding.peek(onboarding_dir, who)
        return invalid, conflict_a, conflict_b, outcome, record, ledger, state, gm


# ---------------------------------------------------------------------------
# Negativ -- Level1 -> Konflikt3/4 -> Level9 bleibt NACH W77 ein
# unjustified_semantic_drift-HOLD, keine stillschweigende Uebernahme mehr.
# ---------------------------------------------------------------------------

def test_w78_drift_negative_level_change_after_conflict_is_paused_not_adopted():
    who = "testspieler_w78_drift_neg"
    cid = "CHR-W78-DRIFT-NEG-01"
    drifted = full_v7_save(cid, name="Flo", level=9)

    invalid, conflict_a, conflict_b, outcome, record, ledger, state, gm = _run_journey(who, cid, drifted)

    assert len(gm.calls) == 3, "ein Ursprung + zwei Korrekturslots, kein Zusatzcall."
    assert outcome.status == "paused", outcome
    assert outcome.reason == "unjustified_semantic_drift", outcome
    assert outcome.save_block is None, "ein Drift-HOLD darf KEINEN finalen Save liefern."

    assert record["attempts_used"] == 2, "beide Korrekturversuche (mehrdeutig + Drift) zaehlen."
    assert record["state"] == "hold" and record.get("last_reason") == "unjustified_semantic_drift"
    assert "adopted_block" not in record, "kein adopted-Block bei einem Drift-HOLD."
    assert record.get("bound_block") == invalid, "der gebundene Level1-Originalentwurf bleibt unveraendert."

    assert state.status == "in_progress" and state.final_save is None, (
        "ohne Uebernahme bleibt der Onboarding-Zustand offen, kein final_save."
    )
    assert len(ledger) == 3 and all(r.get("state") == "accounted" for r in ledger), (
        f"alle drei Transport-Requests muessen terminal (accounted) sein -- {ledger}"
    )
    assert outcome.save_block not in (conflict_a, conflict_b), (
        "kein first-wins -- die mehrdeutige Doppelantwort darf nie uebernommen werden."
    )


# ---------------------------------------------------------------------------
# Positiv -- dieselbe Reise, aber die eindeutige Antwort ist eine
# wertgleiche Formatkorrektur (Level1, Walletwert 500 nur strukturell
# repariert) -- bleibt annehmbar.
# ---------------------------------------------------------------------------

def test_w78_drift_positive_value_preserving_wallet_fix_is_adopted():
    who = "testspieler_w78_drift_pos"
    cid = "CHR-W78-DRIFT-POS-01"
    corrected = full_v7_save(cid, name="Flo", level=1)
    corrected["economy"] = {"wallets": {cid: {"balance": 500}}}

    invalid, conflict_a, conflict_b, outcome, record, ledger, state, gm = _run_journey(who, cid, corrected)

    assert len(gm.calls) == 3, "ein Ursprung + zwei Korrekturslots, kein Zusatzcall."
    assert outcome.status == "completed", outcome
    assert outcome.save_block == corrected, (
        "Ergebnisblock MUSS genau die gueltige Korrekturantwort sein -- weder conflict_a noch conflict_b."
    )
    assert outcome.save_block["characters"][0]["lvl"] == 1
    assert outcome.save_block["economy"]["wallets"][cid]["balance"] == 500

    assert record["attempts_used"] == 2, "beide Korrekturversuche (mehrdeutig + eindeutig) zaehlen."
    assert record["state"] == "adopted" and record.get("adopted_block") == corrected

    assert state.status == "completed" and state.final_save == corrected

    assert save_validation.validate_structure(invalid).valid is False, (
        "der Ursprungsentwurf bleibt schema-ungueltig (loest die Korrektur ueberhaupt aus)."
    )
    assert save_validation.validate_structure(corrected).valid is True, (
        "die Korrekturantwort MUSS gegen BEIDE unveraenderten v7-Schemas bestehen."
    )
    assert len(ledger) == 3 and all(r.get("state") == "accounted" for r in ledger), (
        f"alle drei Transport-Requests muessen terminal (accounted) sein -- {ledger}"
    )
    assert outcome.save_block not in (conflict_a, conflict_b), (
        "kein first-wins -- die mehrdeutige Doppelantwort darf nie uebernommen werden."
    )


def _run_all() -> int:
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in fns:
        try:
            fn()
            print(f"OK   {fn.__name__}")
            passed += 1
        except AssertionError:
            print(f"FAIL {fn.__name__}")
            traceback.print_exc()
        except Exception:
            print(f"ERROR {fn.__name__}")
            traceback.print_exc()
    print(f"\n{passed}/{len(fns)} passed")
    return 0 if passed == len(fns) else 1


if __name__ == "__main__":
    raise SystemExit(_run_all())
