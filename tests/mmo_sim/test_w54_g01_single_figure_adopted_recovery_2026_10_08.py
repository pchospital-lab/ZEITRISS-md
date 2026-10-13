#!/usr/bin/env python3
"""
tests/mmo_sim/test_w54_g01_single_figure_adopted_recovery_2026_10_08.py --
R12-Savegate, W54-Slice, G01 (FINDINGS.json/01_ENTSCHEIDUNG_UND_REPARATUR.md
§W54 G01, SC03/SC09/SC13/SC14).

Befund (General, GENERALREVIEW.md §3, eigene Zwei-Prozess-Gegenprobe):
`pursue_single_figure_correction` persistierte beim Einzelfigurpfad
`mark_adopted(run_dir, repair_key)` OHNE `adopted_block` (anders als der
bereits W53-reparierte Gruppenpfad). Crasht der Aufrufer GENAU zwischen
diesem `mark_adopted` und dem terminalen zweiten `onboarding.
complete_with_save`-Aufruf, fand ein Neustart den Datensatz bereits
`state=="adopted"` vor und gab den dabei vom AUFRUFER erneut uebergebenen
`candidate_block` zurueck -- das ist IMMER der alte, bereits abgelehnte
Entwurf (die tatsaechlich akzeptierte Antwort wurde nie lokal durabel
gemacht). Der Caller versuchte dessen Uebernahme und endete in einem
ValueError -- blockierte Wiederaufnahme, `final_save` blieb dauerhaft
`None`, obwohl der gueltige Text bereits real empfangen worden war.

W54-Fix (NUR `mmo_sim/core/save_correction.py`):
  1. `mark_adopted(..., adopted_block=new_candidate)` persistiert die
     adoptierten Blockbytes ATOMAR zusammen mit `state="adopted"`
     (identisches Muster zum W53-Fix im Gruppenpfad).
  2. Der `STATE_ADOPTED`-Zweig liefert NIE mehr den Caller-`candidate_
     block`, sondern den durabel persistierten `adopted_block` -- NACH
     voller Re-Pruefung gegen BEIDE v7-Schemas (`save_correction_domain.
     evaluate`). Fehlt `adopted_block` oder besteht er die Re-Pruefung
     nicht, kontrolliertes HOLD statt eine Vermutung ueber den
     Rueckgabewert.

Abdeckung:
  W54-G01-A -- Echter End-to-End-Crash-/Restart-Durchlauf UEBER den
               Produktweg (`core.creation_service.run_admitted_creation_
               dialog`, identisches Reproduktionsmuster zu `refs/
               probe_savegate.py` modes 'crash'+'restart'): Restart MUSS
               den durabel adoptierten, gueltigen Save GENAU EINMAL
               uebernehmen -- 0 neue Transportaufrufe, `attempts_used`
               unveraendert, kein neuer Ledgerdatensatz, `accepted` wird
               NIE mit dem alten ungueltigen Entwurf zurueckgegeben.
  W54-G01-B -- Fehlender `adopted_block` in einem (simulierten) Altrecord
               vor diesem Fix -> kontrolliertes HOLD, kein Raten.
  W54-G01-C -- `adopted_block` vorhanden, besteht aber die Re-Pruefung
               gegen die v7-Schemas nicht mehr (korrupter/inkonsistenter
               Dauerbeleg) -> kontrolliertes HOLD, kein Raten.

Pure Python, nur `assert`, echter Exitcode -- gleiches Muster wie
`test_w53_save_correction_adopted_replay_2026_10_08.py`. Kein Netz, kein
Livecall -- ausschliesslich kontrollierte, lokal geskriptete
Fake-SL-Antworten."""
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
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402


class _ScriptedGm:
    """Liefert der Reihe nach vorgegebene Antworten; jeder Aufruf ohne
    verbleibende Antwort ist ein Produktfehler (verbotener Zweitversand)."""

    def __init__(self, contents: list[str]):
        self._contents = list(contents)
        self.calls: list[tuple[int, str]] = []

    def turn(self, turn_idx, text, **kwargs):
        self.calls.append((turn_idx, text))
        if not self._contents:
            raise AssertionError(
                f"W54-G01: unerwarteter zusaetzlicher Transport-Call (turn_idx={turn_idx})."
            )
        return {"content": self._contents.pop(0), "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}


def fenced(block: dict) -> str:
    return "```json\n" + json.dumps(block) + "\n```"


def _no_persona_poll(*_a, **_k):
    raise AssertionError("W54-G01: kein Personapoll im menschlichen Erschaffungsdialog erwartet.")


# ---------------------------------------------------------------------------
# W54-G01-A -- echter Crash-/Restart-Durchlauf ueber den Produktweg.
# ---------------------------------------------------------------------------

def test_w54g01a_restart_after_adopted_before_onboarding_write_recovers_durable_valid_block():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, onboarding_dir = root / "run", root / "onboarding"
        write_test_profile(run_dir)
        who = "testspieler_w54g01a"
        cid = "CHR-W54-G01A-01"

        invalid = full_v7_save(cid, name="Flo")
        invalid["economy"] = {"wallets": {cid: 500}}  # Zahl statt Objekt -- schema-ungueltig
        valid = full_v7_save(cid, name="Flo")
        valid["economy"] = {"wallets": {cid: {"balance": 500}}}

        onboarding.start_or_resume(onboarding_dir, who)
        gm_run1 = _ScriptedGm([fenced(invalid), fenced(valid)])

        old_complete = onboarding.complete_with_save

        def _stop_on_valid(on_dir, pid, block, *a, **k):
            # Simulierter Prozessabsturz GENAU NACH `mark_adopted` (im
            # Produktcode bereits durchlaufen) UND VOR diesem terminalen
            # `onboarding.complete_with_save`-Aufruf -- identisches
            # Crashfenster zu `refs/probe_savegate.py` mode 'crash'.
            if block == valid:
                raise OSError("W54G01_SIMULATED_CRASH_AFTER_ADOPTED_BEFORE_ONBOARDING_WRITE")
            return old_complete(on_dir, pid, block, *a, **k)

        onboarding.complete_with_save = _stop_on_valid
        raised = None
        try:
            try:
                run_admitted_creation_dialog(
                    run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=who,
                    turn_idx_start=0, initial_outgoing="Erschaffung starten.", gm_transport=gm_run1,
                    get_reply=_no_persona_poll, harvest_validator=ZeitrissHarvestValidator(),
                    print_fn=lambda _s: None,
                )
            except Exception as exc:  # noqa: BLE001 (bewusst breit -- Crash-Reproduktion)
                raised = exc
        finally:
            onboarding.complete_with_save = old_complete

        assert isinstance(raised, OSError) and "W54G01_SIMULATED_CRASH" in str(raised), raised
        assert len(gm_run1.calls) == 2, "genau 2 reale Transport-Calls (Erstantwort + 1 Korrektur) im Crash-Lauf."

        repair_key = save_correction_domain.creation_repair_key(who, cid)
        record_before = save_correction.load_record(run_dir, repair_key)
        assert record_before["state"] == "adopted"
        assert record_before.get("adopted_block") == valid, (
            "W54-Fix 1: der adoptierte Block MUSS atomar mit state=adopted persistiert sein."
        )
        assert record_before["attempts_used"] == 1

        state_before = onboarding.peek(onboarding_dir, who)
        assert state_before.status == "in_progress" and state_before.final_save is None, (
            "der Crash geschah VOR dem terminalen Onboarding-Write -- final_save bleibt (noch) None."
        )
        ledger_before = request_ledger._all_records(run_dir)
        assert len(ledger_before) == 2

        # "Neustart": frischer Lauf, KEINE weiteren SL-Antworten verfuegbar
        # -- ein (verbotener) Zweitversand wuerde sofort AssertionError
        # auswerfen (identisches Muster zu `refs/probe_savegate.py` mode
        # 'restart', `Gm([])`).
        gm_run2 = _ScriptedGm([])
        outcome = run_admitted_creation_dialog(
            run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=who,
            turn_idx_start=0, initial_outgoing="Erschaffung starten.", gm_transport=gm_run2,
            get_reply=_no_persona_poll, harvest_validator=ZeitrissHarvestValidator(),
            print_fn=lambda _s: None,
        )

        assert len(gm_run2.calls) == 0, "SC09/G01: 0 neue Transportaufrufe bei der Wiederaufnahme."
        assert outcome.status == "completed", outcome
        assert outcome.save_block == valid, (
            "G01-Fix: der Restart MUSS den durabel adoptierten GUELTIGEN Block uebernehmen, "
            "NIE den alten ungueltigen Entwurf (der bisherige Bug)."
        )
        assert outcome.chrononaut_id == cid

        state_after = onboarding.peek(onboarding_dir, who)
        assert state_after.status == "completed" and state_after.final_save == valid, (
            "der gueltige Save MUSS nach Wiederaufnahme GENAU EINMAL dauerhaft uebernommen werden."
        )

        record_after = save_correction.load_record(run_dir, repair_key)
        assert record_after["attempts_used"] == 1, (
            f"SC13: Versuchszaehler darf durch die Wiederherstellung NICHT steigen -- {record_after['attempts_used']}"
        )
        assert record_after["state"] == "adopted"

        ledger_after = request_ledger._all_records(run_dir)
        assert len(ledger_after) == 2, f"kein neuer Ledgerdatensatz durch den Restart -- {ledger_after}"
        assert ledger_after == ledger_before

        # Der Korrekturdatensatz selbst bleibt unabhaengig vom (bereits
        # "completed") Onboarding-Zustand idempotent: ein direkter
        # erneuter Aufruf von `pursue_single_figure_correction` mit dem
        # alten ungueltigen Entwurf liefert weiterhin denselben durabel
        # adoptierten gueltigen Block, 0 neue Transportaufrufe, kein
        # erneutes Hochzaehlen.
        gm_run3 = _ScriptedGm([])
        again = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=who, expected_chrononaut_id=cid,
            candidate_block=invalid, gm_transport=gm_run3,
        )
        assert len(gm_run3.calls) == 0
        assert again.status == "accepted" and again.block == valid
        record_again = save_correction.load_record(run_dir, repair_key)
        assert record_again["attempts_used"] == 1 and record_again["state"] == "adopted"


# ---------------------------------------------------------------------------
# W54-G01-B -- fehlender `adopted_block` (Altrecord vor diesem Fix) ->
# kontrolliertes HOLD statt Raten.
# ---------------------------------------------------------------------------

def test_w54g01b_adopted_without_durable_block_is_a_controlled_hold_not_a_guess():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        write_test_profile(run_dir)
        who = "testspieler_w54g01b"
        cid = "CHR-W54-G01B-01"
        repair_key = save_correction_domain.creation_repair_key(who, cid)

        save_correction.load_or_init_record(
            run_dir, repair_key, persona_key=who, char_id=cid,
            operation_key=save_correction_domain.ROLE_CREATION,
        )
        save_correction.begin_attempt(run_dir, repair_key)
        # Simuliert einen Datensatz, wie er VOR diesem W54-Fix entstanden
        # waere: state=adopted OHNE adopted_block.
        save_correction.mark_adopted(run_dir, repair_key)
        before = save_correction.load_record(run_dir, repair_key)
        assert before["state"] == "adopted" and before.get("adopted_block") is None

        stale_candidate = full_v7_save(cid, name="Flo")
        stale_candidate["economy"] = {"wallets": {cid: 999}}  # irrelevant -- darf NICHT uebernommen werden

        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=who, expected_chrononaut_id=cid,
            candidate_block=stale_candidate, gm_transport=_ScriptedGm([]),
        )
        assert outcome.status == "hold" and outcome.reason == "adopted_without_durable_block", outcome
        assert outcome.block is None, "kein Raten -- der alte Caller-Kandidat darf NIE als Save gelten."

        after = save_correction.load_record(run_dir, repair_key)
        assert after["state"] == "hold" and after["last_reason"] == "adopted_without_durable_block"


# ---------------------------------------------------------------------------
# W54-G01-C -- `adopted_block` vorhanden, besteht aber die volle Re-Pruefung
# gegen BEIDE v7-Schemas nicht mehr -> kontrolliertes HOLD statt Raten.
# ---------------------------------------------------------------------------

def test_w54g01c_adopted_durable_block_failing_revalidation_is_a_controlled_hold():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        write_test_profile(run_dir)
        who = "testspieler_w54g01c"
        cid = "CHR-W54-G01C-01"
        repair_key = save_correction_domain.creation_repair_key(who, cid)

        save_correction.load_or_init_record(
            run_dir, repair_key, persona_key=who, char_id=cid,
            operation_key=save_correction_domain.ROLE_CREATION,
        )
        save_correction.begin_attempt(run_dir, repair_key)
        corrupted_durable = full_v7_save(cid, name="Flo")
        corrupted_durable["economy"] = {"wallets": {cid: 500}}  # inkonsistent: schema-ungueltig
        save_correction.mark_adopted(run_dir, repair_key, adopted_block=corrupted_durable)

        # `candidate_block` muss hier selbst schema-ungueltig sein, damit
        # der Aufruf ueberhaupt den `STATE_ADOPTED`-Zweig erreicht (ein fuer
        # sich allein bereits gueltiger `candidate_block` wuerde den
        # vorgelagerten Fruehausstieg `if acceptance.accepted: ...` treffen
        # -- irrelevant fuer diesen Re-Pruefungsfall).
        stale_invalid = full_v7_save(cid, name="Flo")
        stale_invalid["economy"] = {"wallets": {cid: 999}}
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=who, expected_chrononaut_id=cid,
            candidate_block=stale_invalid, gm_transport=_ScriptedGm([]),
        )
        assert outcome.status == "hold" and outcome.reason == "adopted_durable_block_failed_revalidation", outcome
        assert outcome.block is None

        after = save_correction.load_record(run_dir, repair_key)
        assert after["state"] == "hold" and after["last_reason"] == "adopted_durable_block_failed_revalidation"


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
