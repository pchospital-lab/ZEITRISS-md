#!/usr/bin/env python3
"""
tests/mmo_sim/test_n2f_a_f1_f2_wallet_key_rename_fix_2026_10_17.py —
N2F-A (ZR-N2-ANSCHLUSS-LIVE-20261017-R1), F1/F2: Regression fuer den engen
wertgleichen Geschwister-Key-Rename in
`mmo_sim/domain/zeitriss/save_correction.py:detect_unjustified_drift`
(`_is_allowed_required_key_rename`).

Gegenstueck zum urspruenglichen Bug-Reprotest (General-Reviewpaket,
`.../evidence/test_n2a_r_p01_wallet_wrap_drift_repro.py`, sha256
a3128a1a9e2d2b25fbb7cc31d1bd81fcc86b01e8abcafb11839b718e6fa503d6): jener
Reprotest demonstrierte den Live-Stall (amount->balance-Umbenennung wird
faelschlich als Drift erkannt, `run_admitted_creation_dialog` haengt
terminal bei `status=paused, reason=unjustified_semantic_drift`, OBWOHL
Versuch 2 schema-gueltig ist). Dieselben drei Szenarien werden hier GEGEN
DEN GEFIXTEN CODE erneut gefahren, mit INVERTIERTEN Erwartungen (Dialog
schliesst jetzt ab, Drift ist jetzt leer) -- das belegt die Behebung ueber
den ECHTEN Produktpfad (`core.creation_service.run_admitted_creation_dialog`
-> `core.save_correction` -> `domain.zeitriss.save_correction`), nicht nur
isoliert gegen die Domainfunktion.

Zusaetzlich: die vollstaendige Negativfall-Matrix (01_AUFTRAG.md §A) direkt
gegen den echten gepinnten v7-Validator (`jsonschema`/`referencing`,
requirements-ci.txt) -- 100->1000, Name-/Fortschritts-/Alias-Aenderung,
unbegruendete Zusatzschluessel und boolesche Scheinzahlen bleiben Drift;
NUR `amount`<->`balance`<->`credits`<->`value` (byte-gleicher Wert, am
tatsaechlich gemeldeten Fehlerpfad) wird akzeptiert.

Pure Python, nur `assert`, echter Exitcode -- gleiches Muster wie die
bestehende Suite (`test_w48_save_correction_2026_10_07.py`,
`test_n2a_r_p01_wallet_wrap_drift_repro.py`)."""
from __future__ import annotations

import copy
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

import mmo_sim.core.save_correction as save_correction  # noqa: E402
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.creation_service import ReplyResult, run_admitted_creation_dialog  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402

CHAR_ID = "CHR-DRIFT-7W71"


def _wallet_number(char_id: str) -> dict:
    block = full_v7_save(char_id, name="Yara Ostrova", callsign="DRIFT")
    block["economy"] = {"wallets": {char_id: 100}}
    return block


def _wallet_amount(char_id: str) -> dict:
    block = full_v7_save(char_id, name="Yara Ostrova", callsign="DRIFT")
    block["economy"] = {"wallets": {char_id: {"amount": 100}}}
    return block


def _wallet_balance(char_id: str, value: object = 100) -> dict:
    block = full_v7_save(char_id, name="Yara Ostrova", callsign="DRIFT")
    block["economy"] = {"wallets": {char_id: {"balance": value}}}
    return block


def _never_called_get_reply(turn_idx: int, sl_text: str) -> ReplyResult:
    raise AssertionError("get_reply darf hier nie aufgerufen werden -- die SL liefert den Save direkt.")


class _ScriptedGm:
    def __init__(self, contents: list[str]):
        self._contents = list(contents)
        self.calls: list[tuple[int, str]] = []

    def turn(self, turn_idx: int, user_text: str) -> dict:
        self.calls.append((turn_idx, user_text))
        if not self._contents:
            raise AssertionError(
                f"_ScriptedGm: unerwarteter zusaetzlicher Transport-Call (turn_idx={turn_idx}) -- "
                "keine weiteren gescripteten Antworten (Beleg gegen einen dritten automatischen Versand)."
            )
        return {"content": self._contents.pop(0), "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}


def test_fixed_wallet_wrap_key_rename_no_longer_hangs_real_product_path():
    """GEGENSTUECK zu `test_hang_wallet_wrap_key_rename_is_misclassified_as_drift`
    (Reprotest, pre-fix): derselbe Scriptablauf (Zahl -> {"amount":100} ->
    {"balance":100}) ueber den ECHTEN Produktpfad
    (`run_admitted_creation_dialog`) schliesst jetzt ab (`status=completed`),
    OHNE einen vierten/zusaetzlichen SL-Call (weiterhin genau 3: 1
    Erstantwort + 2 Korrekturen), MIT byte-identischem Walletbetrag."""
    root = Path(tempfile.mkdtemp(prefix="n2f_a_f1_fix_"))
    run_dir, onboarding_dir = root / "run", root / "onboarding"
    write_test_profile(run_dir)
    participant_id = "p01_latch"
    onboarding.start_or_resume(onboarding_dir, participant_id)

    number_block = _wallet_number(CHAR_ID)
    amount_block = _wallet_amount(CHAR_ID)
    balance_block = _wallet_balance(CHAR_ID)

    assert save_correction_domain.evaluate(amount_block, CHAR_ID).accepted is False
    assert save_correction_domain.evaluate(balance_block, CHAR_ID).accepted is True

    gm = _ScriptedGm([
        "```json\n" + json.dumps(number_block) + "\n```",
        "```json\n" + json.dumps(amount_block) + "\n```",
        "```json\n" + json.dumps(balance_block) + "\n```",
    ])
    outcome = run_admitted_creation_dialog(
        run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=participant_id,
        turn_idx_start=0, initial_outgoing="Erschaffung starten.",
        gm_transport=gm, get_reply=_never_called_get_reply,
        harvest_validator=ZeitrissHarvestValidator(), role="creation_dialog",
    )

    assert outcome.status == "completed", f"Erwarteter Abschluss (completed), bekommen: {outcome}"
    assert len(gm.calls) == 3, f"1 Erstantwort + genau 2 Korrekturversuche erwartet, bekommen: {gm.calls}"
    assert outcome.save_block["economy"]["wallets"][CHAR_ID] == {"balance": 100}, outcome.save_block["economy"]

    state = onboarding.peek(onboarding_dir, participant_id)
    assert state.status == "completed", "Onboarding muss nach dem gueltigen Rename als abgeschlossen gelten."

    repair_key = save_correction_domain.creation_repair_key(participant_id, CHAR_ID)
    record = save_correction.load_record(run_dir, repair_key)
    assert record["state"] == "adopted", record


def test_root_cause_isolated_drift_check_is_now_empty():
    """GEGENSTUECK zu `test_root_cause_isolated_drift_check` (Reprotest,
    pre-fix): amount->balance (byte-gleicher Wert, am echten gemeldeten
    Fehlerpfad) ist jetzt KEINE Drift mehr; die bereits vorher korrekte
    Erstverwrappung (number->amount) bleibt unveraendert driftfrei."""
    amount_block = _wallet_amount(CHAR_ID)
    balance_block = _wallet_balance(CHAR_ID)
    number_block = _wallet_number(CHAR_ID)

    acc_amount = save_correction_domain.evaluate(amount_block, CHAR_ID)
    error_paths_amount = {e.path for e in acc_amount.structure.errors}
    assert error_paths_amount == {"/economy/wallets/" + CHAR_ID}, error_paths_amount

    acc_number = save_correction_domain.evaluate(number_block, CHAR_ID)
    error_paths_number = {e.path for e in acc_number.structure.errors}
    drift_first_wrap = save_correction_domain.detect_unjustified_drift(
        number_block, amount_block, error_paths_number,
    )
    assert drift_first_wrap == [], drift_first_wrap

    drift_rename = save_correction_domain.detect_unjustified_drift(
        amount_block, balance_block, error_paths_amount,
    )
    assert drift_rename == [], f"F1-Fix erwartet: Umbenennung ist KEINE Drift mehr, bekommen: {drift_rename}"


def test_wallet_negative_matrix_against_real_validator():
    """01_AUFTRAG.md §A Negativfaelle, direkt gegen den echten gepinnten
    v7-Validator ausgewertet (error_paths aus `evaluate(...)`, nicht
    hartkodiert) -- KEIN Blanket "schema-gueltig -> annehmen"."""

    def error_paths_of(block: dict) -> set[str]:
        return {e.path for e in save_correction_domain.evaluate(block, CHAR_ID).structure.errors}

    # Positiv: amount:100 -> balance:100 UND der alte Zahl->Objekt-Wrap bleiben erlaubt.
    for before, after in (
        (_wallet_amount(CHAR_ID), _wallet_balance(CHAR_ID)),
        (_wallet_number(CHAR_ID), _wallet_balance(CHAR_ID)),
    ):
        drift = save_correction_domain.detect_unjustified_drift(before, after, error_paths_of(before))
        assert drift == [], ("erwartete Annahme (wertgleiche Strukturkorrektur)", before, after, drift)

    # Negativ 1: Betrag geaendert (100 -> 1000) bleibt Drift, trotz Rename.
    for before in (_wallet_amount(CHAR_ID), _wallet_number(CHAR_ID)):
        after = _wallet_balance(CHAR_ID, value=1000)
        drift = save_correction_domain.detect_unjustified_drift(before, after, error_paths_of(before))
        assert drift, ("erwartete Ablehnung (Betragsaenderung)", before, after)

    # Negativ 2: Namensaenderung bleibt Drift, auch neben einer gueltigen Walletkorrektur.
    before = _wallet_amount(CHAR_ID)
    after = _wallet_balance(CHAR_ID)
    after["characters"][0]["name"] = "UNAUTHORIZED NAME CHANGE"
    drift = save_correction_domain.detect_unjustified_drift(before, after, error_paths_of(before))
    assert "/characters/0/name" in {row[0] for row in drift}, drift

    # Negativ 3: Fortschrittsaenderung (Level) bleibt Drift.
    before = _wallet_amount(CHAR_ID)
    after = _wallet_balance(CHAR_ID)
    after["characters"][0]["lvl"] = 99
    drift = save_correction_domain.detect_unjustified_drift(before, after, error_paths_of(before))
    assert "/characters/0/lvl" in {row[0] for row in drift}, drift

    # Negativ 4: boolesche Scheinzahl (True == 1 numerisch) bleibt Drift, nicht "wertgleich".
    before = _wallet_amount(CHAR_ID)
    before["economy"]["wallets"][CHAR_ID] = {"amount": 1}
    after = _wallet_balance(CHAR_ID, value=True)
    drift = save_correction_domain.detect_unjustified_drift(before, after, error_paths_of(before))
    assert drift, ("erwartete Ablehnung (boolesche Scheinzahl)", before, after)

    # Negativ 5: Alias ausserhalb von _AMOUNT_WRAP_KEYS (z.B. 'funds') bleibt Drift.
    before = _wallet_amount(CHAR_ID)
    after = copy.deepcopy(before)
    after["economy"]["wallets"][CHAR_ID] = {"funds": 100}
    drift = save_correction_domain.detect_unjustified_drift(before, after, error_paths_of(before))
    assert drift, ("erwartete Ablehnung (unbekannter Alias)", before, after)

    # Negativ 6: unbegruendeter Zusatzschluessel neben dem Rename bleibt Drift.
    before = _wallet_amount(CHAR_ID)
    after = copy.deepcopy(before)
    after["economy"]["wallets"][CHAR_ID] = {"balance": 100, "extra_sneaky": "x"}
    drift = save_correction_domain.detect_unjustified_drift(before, after, error_paths_of(before))
    assert drift, ("erwartete Ablehnung (unbegruendeter Zusatzschluessel)", before, after)

    # Negativ 7: Callsign-Alias-Aenderung bleibt Drift (keine Freigabe aller Nachkommen).
    before = _wallet_amount(CHAR_ID)
    after = _wallet_balance(CHAR_ID)
    after["characters"][0]["callsign"] = "NEWALIAS"
    drift = save_correction_domain.detect_unjustified_drift(before, after, error_paths_of(before))
    assert "/characters/0/callsign" in {row[0] for row in drift}, drift


def _run(name: str, fn) -> bool:
    try:
        fn()
    except AssertionError as e:
        print(f"FAIL {name}: {e}")
        traceback.print_exc()
        return False
    except Exception as e:  # pragma: no cover
        print(f"ERROR {name}: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False
    print(f"PASS {name}")
    return True


if __name__ == "__main__":
    tests = [
        ("test_fixed_wallet_wrap_key_rename_no_longer_hangs_real_product_path",
         test_fixed_wallet_wrap_key_rename_no_longer_hangs_real_product_path),
        ("test_root_cause_isolated_drift_check_is_now_empty", test_root_cause_isolated_drift_check_is_now_empty),
        ("test_wallet_negative_matrix_against_real_validator", test_wallet_negative_matrix_against_real_validator),
    ]
    ok_all = [(_run(name, fn)) for name, fn in tests]
    sys.exit(0 if all(ok_all) else 1)
