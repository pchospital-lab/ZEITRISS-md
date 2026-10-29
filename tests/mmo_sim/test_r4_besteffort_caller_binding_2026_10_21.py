#!/usr/bin/env python3
"""
tests/mmo_sim/test_r4_besteffort_caller_binding_2026_10_21.py —
R4-CALLER-BINDUNG (02_JETZT_ENTWICKELN.md §2, ZR-N2R-ANSCHLUSS-20261019-R4).

Ergaenzt `test_n2r5_besteffort_continue_2026_10_20.py` (die Haelfte, die
beweist, dass derselbe Aufrufer nach Budget-Erschoepfung best-effort
weiterlaeuft) um die fehlende Gegenhaelfte: der best-effort gebundene
`bound_block` eines `attempt_budget_exhausted`-HOLD darf NUR an GENAU
DENSELBEN Aufrufer zurueckgegeben werden, der ihn erzeugt hat.

Bug VOR diesem Fix (`core/save_correction.py` Resume-Zweig im
`record["state"] in (HOLD, WINDOW_PAUSED)`-Block): `resumed_block =
record.get("bound_block") if last_reason == "attempt_budget_exhausted"
else None` lieferte den Block AUCH dann, wenn der elif ueber den ERSTEN
Oder-Zweig (`record_identity != caller_identity`) betreten wurde -- also
fuer einen FREMDEN Aufrufer-Kontext. `creation_service.run_admitted_
creation_dialog` (bzw. jeder Best-Effort-Uebernehmer) haette diesen fremd
gebundenen Block dann adoptiert (fremde Caller-Bindung, 02 §2).

Fix: der Block wird nur noch bei `record_identity == caller_identity`
zurueckgegeben. Mismatch endet ohne uebernehmbaren Block (TERMINAL hold),
der passende Resume desselben Callers behaelt Best-Effort unveraendert.

`pursue_single_figure_correction` leitet seinen `repair_key` IMMER aus
`creation_repair_key(participant_id, char_id)` ab (Zeile 682) -- table_id/
section_id/role sind NICHT Teil des Schluessels, aber Teil der feineren
Identitaetspruefung (persona/char/operation/table/section). Genau diese
Luecke -- gleicher Record, abweichender Kontext -- ist das, was der Guard
schuetzt. Der Test betritt denselben Record daher mit abweichendem
table_id/section_id.

Pure Python, nur `assert`, echter Exitcode -- gleiches Muster wie die
bestehende Suite."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402 (Fixturehelper, FIXTURE_ONLY)

import mmo_sim.core.save_correction as save_correction  # noqa: E402
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.creation_service import ReplyResult, run_admitted_creation_dialog  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402


def _never_called_get_reply(turn_idx: int, sl_text: str) -> ReplyResult:
    raise AssertionError("get_reply sollte hier nie aufgerufen werden -- die SL liefert den Save direkt.")


class _ScriptedGm:
    """Liefert vorgegebene Antworten der Reihe nach (Erzeugung des Holds)."""

    def __init__(self, contents: list[str]):
        self._contents = list(contents)
        self.calls: list[tuple[int, str]] = []

    def turn(self, turn_idx: int, user_text: str) -> dict:
        self.calls.append((turn_idx, user_text))
        if not self._contents:
            raise AssertionError(f"_ScriptedGm: unerwarteter Transport-Call (turn_idx={turn_idx}).")
        return {"content": self._contents.pop(0), "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}


class _RaisingGm:
    """Ein Resume auf einem TERMINALEN `attempt_budget_exhausted`-HOLD darf
    NIE einen neuen GM-Versand ausloesen -- jeder `.turn()`-Call ist ein Bug.
    Die Attribute spiegeln die von `save_correction` per `getattr` erfragten
    optionalen Transport-Felder (bleiben hier bewusst `None`)."""

    output_limit_tokens = None
    base_url = None

    def turn(self, turn_idx: int, user_text: str) -> dict:  # noqa: ARG002
        raise AssertionError(
            "Resume auf attempt_budget_exhausted-HOLD darf KEINEN GM-Versand ausloesen."
        )


def _as_json_reply(block: dict) -> str:
    return "```json\n" + json.dumps(block, ensure_ascii=False) + "\n```"


def _produce_attempt_budget_exhausted_hold(run_dir: Path, onboarding_dir: Path, participant_id: str, char_id: str) -> dict:
    """Erzeugt ueber die ECHTE Produktionsschnittstelle (run_admitted_creation_
    dialog) einen `attempt_budget_exhausted`-HOLD-Datensatz mit gebundenem
    `bound_block` -- identischer Aufbau wie
    `test_n2r5_besteffort_continue_2026_10_20.py` (persistent schema-ungueltig,
    identisch bei jedem Versuch, kein Drift). Liefert den gebundenen Block."""
    onboarding.start_or_resume(onboarding_dir, participant_id)
    invalid_block = full_v7_save(char_id, name="Rook", callsign="ROOK")
    invalid_block["economy"] = {"wallets": {char_id: 100}}  # int statt {"balance": ...}-Objekt.
    gm = _ScriptedGm([_as_json_reply(invalid_block)] * 4)
    outcome = run_admitted_creation_dialog(
        run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=participant_id,
        turn_idx_start=0, initial_outgoing="Erschaffung starten.",
        gm_transport=gm, get_reply=_never_called_get_reply,
        harvest_validator=ZeitrissHarvestValidator(), role="creation_dialog",
    )
    assert outcome.reason == "attempt_budget_exhausted_best_effort", outcome
    return invalid_block


# ---------------------------------------------------------------------------
# (1) Passender Resume DESSELBEN Callers behaelt Best-Effort (Regression-
#     Schutz fuer die legitime N2R5-BESTEFFORT-Haelfte).
# ---------------------------------------------------------------------------

def test_r4_same_caller_resume_keeps_besteffort_block():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, onboarding_dir = root / "run", root / "onboarding"
        write_test_profile(run_dir)
        participant_id = "p_match"
        char_id = "CHR-MATCH-001"
        invalid_block = _produce_attempt_budget_exhausted_hold(run_dir, onboarding_dir, participant_id, char_id)

        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)
        record = save_correction.load_record(run_dir, repair_key)
        assert record is not None and record["state"] == "hold", record
        assert record.get("last_reason") == "attempt_budget_exhausted", record
        bound = record.get("bound_block")
        assert bound is not None, "Vorbedingung: der erschoepfte Hold traegt einen gebundenen Best-Effort-Block."

        # Re-Entry mit GENAU der gespeicherten Identitaet (persona/char/
        # operation/table/section). `candidate_block` MUSS schema-ungueltig
        # sein, sonst greift der Sofort-Accept (Zeile 687) VOR dem Resume.
        out = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=invalid_block, gm_transport=_RaisingGm(),
            role=record["operation_key"], table_id=record.get("table_id"), section_id=record.get("section_id"),
        )
        assert out.status == "hold", out
        assert out.reason == "attempt_budget_exhausted", out
        assert out.block == bound, (
            "Passender Resume DESSELBEN Callers muss den Best-Effort-Block unveraendert behalten "
            f"(N2R5-BESTEFFORT) -- block={out.block!r}"
        )


# ---------------------------------------------------------------------------
# (2) FREMDER Aufrufer-Kontext (record_identity != caller_identity) darf
#     KEINEN uebernehmbaren Block erhalten -- der eigentliche R4-Fix.
# ---------------------------------------------------------------------------

def test_r4_foreign_caller_context_gets_no_adoptable_block():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, onboarding_dir = root / "run", root / "onboarding"
        write_test_profile(run_dir)
        participant_id = "p_foreign"
        char_id = "CHR-FOREIGN-001"
        invalid_block = _produce_attempt_budget_exhausted_hold(run_dir, onboarding_dir, participant_id, char_id)

        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)
        record = save_correction.load_record(run_dir, repair_key)
        assert record is not None and record.get("bound_block") is not None, record
        # Vorbedingung: der gespeicherte Kontext ist der Erschaffungskontext
        # (kein table/section). Der Fremdzugriff setzt einen ABWEICHENDEN
        # table/section -- derselbe `creation_repair_key`-Record, aber eine
        # andere feinere Identitaet.
        assert record.get("table_id") != "tbl-fremd", record

        out = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=invalid_block, gm_transport=_RaisingGm(),
            role=record["operation_key"], table_id="tbl-fremd", section_id="sec-fremd",
        )
        assert out.status == "hold", out
        assert out.block is None, (
            "FREMDER Aufrufer-Kontext (record_identity != caller_identity) darf KEINEN "
            f"uebernehmbaren Best-Effort-Block erhalten (02 §2) -- block={out.block!r}"
        )


if __name__ == "__main__":
    failures = []
    for name, fn in sorted(list(globals().items())):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"OK   {name}")
            except AssertionError as exc:
                failures.append(name)
                print(f"FAIL {name}: {exc}")
            except Exception as exc:  # noqa: BLE001 -- echter Exitcode, volle Diagnose
                failures.append(name)
                import traceback
                print(f"ERROR {name}: {exc}")
                traceback.print_exc()
    total = len([n for n in globals() if n.startswith("test_")])
    print(f"\n{total - len(failures)}/{total} Tests bestanden.")
    raise SystemExit(0 if not failures else 1)
