#!/usr/bin/env python3
"""
tests/mmo_sim/test_n2r5_driftfix_creation_core_identity_2026_10_20.py —
N2R5-DRIFTFIX (ZR-N2R-ANSCHLUSS-20261019-R4, worker/BRIEF-driftfix-rerun.md).

Reproduziert die reale p04-Konstellation aus `worker/live1/LIVE-REPORT.md`
(echter Live-Lauf: ein schema-ungueltiger GM-Erschaffungsentwurf --
`economy/wallets/<id>` als blanke Zahl statt Objekt PLUS ein unerwartetes
Zusatzfeld, analog `pp_max` -- wurde bei `attempts_used=1` terminal als
`unjustified_semantic_drift` gehalten, OBWOHL `MAX_ADDITIONAL_REQUESTS=3`
(domain/zeitriss/save_correction.py:26) noch 2 weitere Versuche erlaubt
haette. Wurzel: `core/creation_service.py`s `_attempt_correction` uebergibt
den GM-EIGENEN ersten Entwurf als `original` -- jede Flavor-Neuformulierung
zwischen zwei Erschaffungsentwuerfen (Hintergrundtext, Herkunft, ...) wurde
Blatt-fuer-Blatt als Drift gewertet.

Fix (s. FIX.diff): `core.creation_service._attempt_correction` setzt jetzt
`restrict_drift_to_core_identity=True` -- NUR dieser Aufrufer, NIE
`pursue_group_save_correction` oder ein direkter Testaufruf ohne den
Parameter. Die drei Tests hier beweisen alle drei geforderten Eigenschaften
(Aufgabe 1 der BRIEF): (1) benigne Flavor-Regeneration ist jetzt NICHT mehr
sofort terminal, (2) anhaltend schema-ungueltige Entwuerfe erschoepfen
weiterhin korrekt erst nach 3 Versuchen (`attempt_budget_exhausted`, NICHT
`unjustified_semantic_drift`), (3) ECHTE Identitaets-/Kerninhaltsdrift
(char_id/callsign/name/level/Attribute/Inventar/Wallet-Betrag/Fortschritt)
bleibt WEITERHIN sofort terminal, auch in der Erschaffung -- KEINE
Guard-Schwaechung.

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


def _p04_style_invalid_draft(char_id: str, background: str) -> dict:
    """Exakt die p04-Defektform aus `worker/live1/LIVE-REPORT.md`: Wallet
    als blanke Zahl statt Objekt (`economy/wallets/<id>` type-invalid) PLUS
    ein unerwartetes Zusatzfeld (`pp_max`, analog zum realen Fund
    `characters/0: pp_max was unexpected`)."""
    block = full_v7_save(char_id, name="Insa", callsign="OLTMANNS", history={"background": background}, pp_max=7)
    block["economy"] = {"wallets": {char_id: 100}}  # int statt {"balance": ...}-Objekt -- der reale Fund.
    return block


def _p04_style_valid_block(char_id: str, background: str) -> dict:
    """Dieselbe Figur, SCHEMA-GUELTIG (Wallet korrekt gewrappt, kein
    `pp_max` mehr) -- NUR der Flavor-Text (`history.background`) weicht
    vom vorigen Entwurf ab, exakt die vom Review benannte 'GM regeneriert
    bei Creation naturgemaess anderen Flavor'-Situation."""
    block = full_v7_save(char_id, name="Insa", callsign="OLTMANNS", history={"background": background})
    block["economy"] = {"wallets": {char_id: {"balance": 100}}}
    return block


def _as_json_reply(block: dict) -> str:
    return "```json\n" + json.dumps(block, ensure_ascii=False) + "\n```"


# ---------------------------------------------------------------------------
# (1) Benigne Flavor-Regeneration ist NICHT mehr sofort terminal.
# ---------------------------------------------------------------------------

def test_n2r5_benign_flavor_regeneration_accepted_not_terminal_drift():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, onboarding_dir = root / "run", root / "onboarding"
        write_test_profile(run_dir)
        participant_id = "p04_n2r5"
        char_id = "CHR-DRIFT-001"
        onboarding.start_or_resume(onboarding_dir, participant_id)

        draft1 = _p04_style_invalid_draft(char_id, background="Tochter eines Fischers, Nordseeufer.")
        corrected_valid = _p04_style_valid_block(
            char_id, background="Aufgewachsen an der Waterkant, lernte frueh das Flicken von Netzen.",
        )
        gm = _ScriptedGm([_as_json_reply(draft1), _as_json_reply(corrected_valid)])

        outcome = run_admitted_creation_dialog(
            run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=participant_id,
            turn_idx_start=0, initial_outgoing="Erschaffung starten.",
            gm_transport=gm, get_reply=_never_called_get_reply,
            harvest_validator=ZeitrissHarvestValidator(), role="creation_dialog",
        )
        assert outcome.status == "completed", (
            f"VOR dem Fix haette die reine Flavor-Abweichung (history.background) bereits bei "
            f"attempts_used=1 terminal unjustified_semantic_drift ausgeloest -- jetzt erwartet: "
            f"completed. outcome={outcome}"
        )
        assert outcome.save_block == corrected_valid
        assert len(gm.calls) == 2, f"genau 1 Initialturn + 1 Korrekturturn, kein Post-Terminal-Send -- {gm.calls}"

        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)
        record = save_correction.load_record(run_dir, repair_key)
        assert record is not None and record["attempts_used"] == 1 and record["state"] == "adopted", record


# ---------------------------------------------------------------------------
# (2) Anhaltend schema-ungueltig (trotz wechselndem Flavor) erschoepft
#     weiterhin korrekt erst nach 3 Versuchen -- NICHT vorzeitig als Drift.
# ---------------------------------------------------------------------------

def test_n2r5_persistent_schema_invalid_with_varying_flavor_exhausts_budget_not_drift():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, onboarding_dir = root / "run", root / "onboarding"
        write_test_profile(run_dir)
        participant_id = "p04_n2r5_exhaust"
        char_id = "CHR-DRIFT-002"
        onboarding.start_or_resume(onboarding_dir, participant_id)

        # 1 Initialentwurf + 3 Korrekturversuche, JEDER mit ANDEREM Flavor-
        # Text (benigne Regeneration) UND JEDER weiterhin schema-ungueltig
        # (Wallet bleibt eine blanke Zahl) -- vor dem Fix waere dies bereits
        # beim ERSTEN Korrekturversuch unjustified_semantic_drift gewesen.
        texts = [
            "Tochter eines Fischers, Nordseeufer.",
            "Aufgewachsen an der Waterkant.",
            "Kind einer Lotsenfamilie, Elbmuendung.",
            "Spaete Jugend auf einem Schlepper verbracht.",
        ]
        gm = _ScriptedGm([_as_json_reply(_p04_style_invalid_draft(char_id, background=t)) for t in texts])

        outcome = run_admitted_creation_dialog(
            run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=participant_id,
            turn_idx_start=0, initial_outgoing="Erschaffung starten.",
            gm_transport=gm, get_reply=_never_called_get_reply,
            harvest_validator=ZeitrissHarvestValidator(), role="creation_dialog",
        )
        # TEST-DELTA (N2R5-BESTEFFORT, Flo-Design, ZR-N2R-ANSCHLUSS-20261020-
        # FINALRUN3): VOR diesem Fix haelt ein voll ausgeschoepftes
        # Korrekturbudget (reiner Schema-Imperfekt, KEINE Drift) terminal
        # mit `status="paused"`. Flo woertlich: 'beim 4. Mal -- passend
        # ODER NICHT -- muss es TROTZDEM WEITERLAUFEN; den Rest korrigiert
        # der GM automatisch beim Laden' -- `core.creation_service.
        # run_admitted_creation_dialog` finalisiert die Figur jetzt mit dem
        # letzten (weiterhin schema-ungueltigen) Kandidaten best-effort
        # (`onboarding.complete_with_save_best_effort`, EHRLICH markiert
        # ueber `final_save_best_effort=True`, NIE als perfekt behauptet)
        # und laeuft weiter. Die eigentliche Testabsicht bleibt bestehen:
        # das Budget wird voll ausgeschoepft (3 Korrekturversuche, NICHT
        # bereits bei attempts_used=1 durch den wechselnden Flavor-Text),
        # NUR der terminale Endzustand aendert sich von HOLD auf
        # best-effort-completed.
        assert outcome.status == "completed" and outcome.reason == "attempt_budget_exhausted_best_effort", (
            f"Budget wird voll ausgeschoepft (3 Korrekturversuche), DANN best-effort-Abschluss "
            f"(NICHT mehr HOLD, N2R5-BESTEFFORT) -- outcome={outcome}"
        )
        assert len(gm.calls) == 4, f"genau 1 Initialturn + 3 Korrekturversuche, dann best-effort-Abschluss -- {gm.calls}"

        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)
        record = save_correction.load_record(run_dir, repair_key)
        # Die interne Korrektur-Buchhaltung (`core.save_correction`) bleibt
        # UNVERAENDERT terminal `hold`/`attempt_budget_exhausted` -- NUR der
        # Aufrufer (`creation_service`) uebersetzt dies jetzt in einen
        # best-effort-Abschluss statt eines Dialog-HOLD (s.o.).
        assert record["attempts_used"] == 3 and record["state"] == "hold"
        assert record.get("last_reason") == "attempt_budget_exhausted"

        state = onboarding.peek(onboarding_dir, participant_id)
        assert state is not None and state.status == "completed", state
        assert state.final_save_best_effort is True, "muss EHRLICH als best-effort/imperfekt markiert sein."


# ---------------------------------------------------------------------------
# (3) ECHTE Identitaets-/Kerninhaltsdrift bleibt WEITERHIN sofort terminal,
#     auch in der Erschaffung -- KEINE Guard-Schwaechung.
# ---------------------------------------------------------------------------

def test_n2r5_core_identity_drift_still_terminal_immediately_in_creation():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, onboarding_dir = root / "run", root / "onboarding"
        write_test_profile(run_dir)
        participant_id = "p04_n2r5_identity"
        char_id = "CHR-DRIFT-003"
        onboarding.start_or_resume(onboarding_dir, participant_id)

        draft1 = _p04_style_invalid_draft(char_id, background="Tochter eines Fischers, Nordseeufer.")
        # Schema wird korrigiert (Wallet jetzt Objekt, pp_max weg), ABER der
        # Wallet-BETRAG wird dabei stillschweigend von 100 auf 9000 geaendert
        # -- genau die Kategorie ("Wallet-Betrag"), die laut BRIEF AUCH in
        # der Erschaffung terminal bleiben MUSS.
        corrected_with_identity_drift = _p04_style_valid_block(
            char_id, background="Tochter eines Fischers, Nordseeufer.",  # Flavor UNVERAENDERT diesmal
        )
        corrected_with_identity_drift["economy"]["wallets"][char_id]["balance"] = 9000
        gm = _ScriptedGm([_as_json_reply(draft1), _as_json_reply(corrected_with_identity_drift)])

        outcome = run_admitted_creation_dialog(
            run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=participant_id,
            turn_idx_start=0, initial_outgoing="Erschaffung starten.",
            gm_transport=gm, get_reply=_never_called_get_reply,
            harvest_validator=ZeitrissHarvestValidator(), role="creation_dialog",
        )
        assert outcome.status == "paused" and outcome.reason == "unjustified_semantic_drift", (
            f"Eine echte Wallet-BETRAGS-Aenderung (100 -> 9000) MUSS auch in der Erschaffung sofort "
            f"terminal bleiben, OHNE die restlichen 2 Korrekturversuche zu verbrauchen -- der Fix darf "
            f"NUR benigne Flavor-Abweichung tolerieren, NIE Identitaets-/Kerninhaltsdrift. outcome={outcome}"
        )
        assert len(gm.calls) == 2, f"KEIN weiterer Versand nach terminalem Drift-HOLD -- {gm.calls}"

        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)
        record = save_correction.load_record(run_dir, repair_key)
        assert record["attempts_used"] == 1 and record["state"] == "hold", (
            "terminal bereits bei attempts_used=1, NICHT erst nach Erschoepfung des 3er-Budgets."
        )
        assert record.get("last_reason") == "unjustified_semantic_drift"


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
