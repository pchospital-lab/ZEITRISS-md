#!/usr/bin/env python3
"""
tests/mmo_sim/test_n2r5_besteffort_continue_2026_10_20.py —
N2R5-BESTEFFORT (Flo-Design, ZR-N2R-ANSCHLUSS-20261020-FINALRUN3,
worker/BRIEF-finalrun3-besteffort.md Aufgabe 1+3).

Flo woertlich: die Save-Korrektur wird bis zu 3x nachkontrolliert; beim
4. Mal -- passend ODER NICHT -- muss es TROTZDEM WEITERLAUFEN; den Rest
korrigiert der GM automatisch beim Laden (Speicherstand ist oft nicht ganz
korrekt, das ist ok). `core.save_correction.pursue_single_figure_
correction`s `attempt_budget_exhausted`-HOLD (reiner Schema-Imperfekt,
3 Korrekturversuche erschoepft, KEINE Drift) ist deshalb ab sofort KEIN
terminaler Dialog-HOLD mehr -- `core.creation_service.
run_admitted_creation_dialog` finalisiert die Figur statt dessen best-
effort mit dem letzten Kandidaten (`onboarding.complete_with_save_best_
effort`, EHRLICH markiert ueber `final_save_best_effort=True`, NIE als
perfekt behauptet).

ABGRENZUNG (A_R2, bewusst UNVERAENDERT): `unjustified_semantic_drift` (der
GM hat Identitaet/Kerninhalt umgeschrieben, NICHT nur das Format korrigiert)
bleibt terminal `status="paused"` -- dieser Fix greift NUR fuer den reinen
Budget-Erschoepfungs-Pfad, NIEMALS fuer Drift. Zwei Tests hier beweisen
beide Haelften der Abgrenzung an derselben Produktionsschnittstelle
(`run_admitted_creation_dialog`).

`status="completed"` (statt `status="paused"`) ist genau das Signal, das
`driver.integrated.py`s `_TERMINAL_CREATION_HOLD_REASONS`-Klassifikation
(nur `status="paused"`-Outcomes mit einem terminalen `reason` loesen
`checkpoint["status"] = "HOLD"` aus) NICHT mehr erreicht -- die Erschaffung
laeuft fuer den Treiber normal weiter, ohne eigene Treiberaenderung noetig.

Pure Python, nur `assert`, echter Exitcode -- gleiches Muster wie die
bestehende Suite (kein pytest-Fixture-Zwang, s. `test_w48_save_correction_
2026_10_07.py`, dessen Helfer hier wiederverwendet werden)."""
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
    """Identisches Muster zu `test_w48_save_correction_2026_10_07.py`s
    `_ScriptedGm`: liefert der Reihe nach vorgegebene Antworten, wirft bei
    jedem Call ohne vorgegebene Antwort mehr (Beleg gegen Doppelversand)."""

    def __init__(self, contents: list[str]):
        self._contents = list(contents)
        self.calls: list[tuple[int, str]] = []

    def turn(self, turn_idx: int, user_text: str) -> dict:
        self.calls.append((turn_idx, user_text))
        if not self._contents:
            raise AssertionError(
                f"_ScriptedGm: unerwarteter zusaetzlicher Transport-Call (turn_idx={turn_idx}) -- "
                "keine weiteren gecannten Antworten."
            )
        return {"content": self._contents.pop(0), "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}


def _as_json_reply(block: dict) -> str:
    return "```json\n" + json.dumps(block, ensure_ascii=False) + "\n```"


# ---------------------------------------------------------------------------
# (1) attempt_budget_exhausted -> best-effort completed, NICHT HOLD.
# ---------------------------------------------------------------------------

def test_n2r5_besteffort_attempt_budget_exhausted_completes_not_hold():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, onboarding_dir = root / "run", root / "onboarding"
        write_test_profile(run_dir)
        participant_id = "p_besteffort"
        char_id = "CHR-BESTEFFORT-001"
        onboarding.start_or_resume(onboarding_dir, participant_id)

        # Persistent schema-ungueltig (Wallet bleibt eine blanke Zahl statt
        # Objekt) UND IDENTISCH bei jedem Versuch -- kein Korrekturfortschritt
        # moeglich, KEIN Flavor-Wechsel (also auch keine Drift-Frage), das
        # Budget (1 Initial + 3 Korrekturversuche) erschoepft sich
        # deterministisch.
        invalid_block = full_v7_save(char_id, name="Rook", callsign="ROOK")
        invalid_block["economy"] = {"wallets": {char_id: 100}}  # int statt {"balance": ...}-Objekt.
        gm = _ScriptedGm([_as_json_reply(invalid_block)] * 4)

        outcome = run_admitted_creation_dialog(
            run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=participant_id,
            turn_idx_start=0, initial_outgoing="Erschaffung starten.",
            gm_transport=gm, get_reply=_never_called_get_reply,
            harvest_validator=ZeitrissHarvestValidator(), role="creation_dialog",
        )

        # Kernbehauptung 1: best-effort COMPLETED, NICHT paused/HOLD.
        assert outcome.status == "completed", (
            f"N2R5-BESTEFFORT: ein erschoepftes Korrekturbudget (reiner Schema-Imperfekt, KEINE "
            f"Drift) darf NICHT mehr terminal HOLDen -- outcome={outcome}"
        )
        assert outcome.reason == "attempt_budget_exhausted_best_effort", outcome.reason
        assert outcome.save_block == invalid_block, "best-effort-Save ist der letzte (unveraenderte) Kandidat."
        assert outcome.chrononaut_id == char_id
        assert len(gm.calls) == 4, f"genau 1 Initialturn + 3 Korrekturversuche, dann best-effort-Abschluss -- {gm.calls}"

        # Kernbehauptung 2: EHRLICH als best-effort markiert, kein Fake-DONE.
        state = onboarding.peek(onboarding_dir, participant_id)
        assert state is not None and state.status == "completed", state
        assert state.final_save == invalid_block
        assert state.final_save_best_effort is True, (
            "muss EHRLICH als best-effort/imperfekt markiert sein -- kein stillschweigend perfekter Abschluss."
        )

        # Kernbehauptung 3 (driver.integrated.py-Klassifikation, s. Moduldoc-
        # string): `status="completed"` ist KEIN `status="paused"` -- die
        # `_TERMINAL_CREATION_HOLD_REASONS`-Pruefung dort greift NUR fuer
        # `status="paused"`-Outcomes, dieser Outcome loest also KEIN
        # `checkpoint["status"]="HOLD"` aus. Die interne Korrekturbuchhaltung
        # (`core.save_correction`) bleibt dabei UNVERAENDERT terminal `hold`/
        # `attempt_budget_exhausted` -- nur dieser Aufrufer-Outcome aendert
        # sich (s. `onboarding.complete_with_save_best_effort`-Docstring).
        assert outcome.status != "paused"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)
        record = save_correction.load_record(run_dir, repair_key)
        assert record["attempts_used"] == 3 and record["state"] == "hold"
        assert record.get("last_reason") == "attempt_budget_exhausted"


# ---------------------------------------------------------------------------
# (2) unjustified_semantic_drift bleibt UNVERAENDERT terminal -- dieser Fix
#     greift NIE fuer Drift.
# ---------------------------------------------------------------------------

def test_n2r5_besteffort_unjustified_semantic_drift_still_terminal_not_best_effort():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, onboarding_dir = root / "run", root / "onboarding"
        write_test_profile(run_dir)
        participant_id = "p_besteffort_drift"
        char_id = "CHR-BESTEFFORT-002"
        onboarding.start_or_resume(onboarding_dir, participant_id)

        # Erster Entwurf MUSS schema-ungueltig sein, sonst wird er sofort
        # (ohne Korrekturrunde, ohne Drift-Vergleichsbasis) angenommen --
        # dieselbe p04-Defektform wie `test_n2r5_driftfix_creation_core_
        # identity_2026_10_20.py` (Wallet als blanke Zahl statt Objekt).
        draft1 = full_v7_save(char_id, name="Insa", callsign="OLTMANNS", wallet=100.0)
        draft1["economy"] = {"wallets": {char_id: 100}}  # int statt {"balance": ...}-Objekt.
        # Schema wird korrigiert (Wallet jetzt gueltiges Objekt), ABER der
        # Wallet-BETRAG wird dabei stillschweigend von 100 auf 9000 geaendert
        # -- echte Identitaets-/Kerninhaltsdrift, KEIN Schemafehler.
        corrected_with_drift = full_v7_save(char_id, name="Insa", callsign="OLTMANNS", wallet=9000.0)
        gm = _ScriptedGm([_as_json_reply(draft1), _as_json_reply(corrected_with_drift)])

        outcome = run_admitted_creation_dialog(
            run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=participant_id,
            turn_idx_start=0, initial_outgoing="Erschaffung starten.",
            gm_transport=gm, get_reply=_never_called_get_reply,
            harvest_validator=ZeitrissHarvestValidator(), role="creation_dialog",
        )

        assert outcome.status == "paused" and outcome.reason == "unjustified_semantic_drift", (
            f"A_R2-Integritaet: eine ECHTE Identitaets-/Kerninhaltsdrift (Wallet-Betrag) muss "
            f"WEITERHIN sofort terminal HOLDen -- N2R5-BESTEFFORT darf das NICHT aufweichen. "
            f"outcome={outcome}"
        )
        assert len(gm.calls) == 2, gm.calls

        state = onboarding.peek(onboarding_dir, participant_id)
        assert state is not None and state.status == "in_progress", state
        assert state.final_save is None, state.final_save
        assert state.final_save_best_effort is False, "Drift darf NIE als best-effort durchgereicht werden."


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
