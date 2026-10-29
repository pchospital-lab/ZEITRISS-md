#!/usr/bin/env python3
"""
tests/mmo_sim/_recovery_ops_r1_fixtures.py — gemeinsamer Testhelper fuer
`test_recovery_ops_r1.py` (ZR-RECOVERY-OFFLINE-20261015-R1). FIXTURE_ONLY,
reiner Testcode -- Produktcode kennt diese Datei nicht.

Baut synthetische `run_dir`s (inkl. der `RECOVERY_SYNTHETIC_TEST_ROOT`-
Markerdatei, die `core.recovery_ops._require_synthetic_root` fuer JEDEN
`apply_*`-Aufruf verlangt) und einen skriptierten GM-Transport, analog dem
bereits bestehenden Muster in `test_w48_save_correction_2026_10_07.py`s
`_ScriptedGm`."""
from __future__ import annotations

import json
from pathlib import Path

from mmo_sim.core.admission import write_test_profile
from mmo_sim.core import recovery_ops, request_ledger, save_correction

_HERE = Path(__file__).resolve().parent
import sys  # noqa: E402

if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
from _full_v7_fixture import full_v7_save  # noqa: E402 (Fixturehelper, FIXTURE_ONLY)


class ScriptedGm:
    """Liefert der Reihe nach vorgegebene Antworten; zaehlt Aufrufe. Wirft,
    wenn mehr Aufrufe erfolgen als Antworten vorgegeben wurden -- der
    primaere Beleg gegen jeden unerwarteten zusaetzlichen (Doppel-/Dritt-)
    Transport-Call in den R-P5-Faellen."""

    def __init__(self, contents: list[str]):
        self._contents = list(contents)
        self.calls: list[tuple[int, str]] = []

    def turn(self, turn_idx: int, user_text: str) -> dict:
        self.calls.append((turn_idx, user_text))
        if not self._contents:
            raise AssertionError(
                f"ScriptedGm: unerwarteter zusaetzlicher Transport-Call (turn_idx={turn_idx}) -- "
                "keine weiteren gecannten Antworten (Beleg gegen Doppel-/Drittversand)."
            )
        return {"content": self._contents.pop(0), "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}


def never_called_gm() -> ScriptedGm:
    return ScriptedGm([])


def _as_json_block(block: dict) -> str:
    return "```json\n" + json.dumps(block) + "\n```"


def make_synthetic_run(root: Path, *, synthetic_marker: bool = True, run_id: str | None = "SYNTHETIC-RUN") -> Path:
    """Baut `root/run` mit einem providerfreien Testprofil (kein Netz, keine
    echten Kosten, s. `write_test_profile`). `synthetic_marker=True` (Default)
    legt zusaetzlich `RECOVERY_SYNTHETIC_TEST_ROOT` an -- OHNE diese Datei
    lehnt jeder `apply_*`-Aufruf kontrolliert ab (s.
    `candidate_scope_and_source_modes_bound`-Testfaelle, die bewusst
    `synthetic_marker=False` verwenden).

    R2-N1-Fix (`p3_missing_run_id`, transparente Treiberanpassung): ein
    echter Recovery-`run_dir` traegt VOR jedem Recovery-Aufruf bereits eine
    von `core.store._run_id` geschriebene `run_id.json` -- dieselbe
    Voraussetzung wird jetzt standardmaessig auch hier hergestellt
    (Default `run_id='SYNTHETIC-RUN'`, analog `write_test_profile`), weil
    `apply_p3`/`apply_p5` eine fehlende/ungueltige Run-Identitaet jetzt
    fail-closed ablehnen (s. `recovery_ops.RecoveryMissingRunIdentityError`)
    statt mit `run_id:null` zu applizieren. `run_id=None` baut bewusst OHNE
    `run_id.json` -- fuer den eigenen `p3_missing_run_id`-Testfall, der
    genau diese Ablehnung nachweist."""
    run_dir = root / "run"
    write_test_profile(run_dir)
    if synthetic_marker:
        (run_dir / recovery_ops.SYNTHETIC_ROOT_MARKER).write_text("test\n", encoding="utf-8")
    if run_id is not None:
        (run_dir / "run_id.json").write_text(json.dumps({"run_id": run_id}), encoding="utf-8")
    return run_dir


def make_p3_unknown_request(run_dir: Path, *, table_id="table-1", section_id="section-1",
                             role="gm_turn", turn_idx=1, participant="alice") -> str:
    """`request_ledger.begin()` und STOPPT dort -- state bleibt `sent`,
    `result_text`/`usage`/`settled_ts`/`error` bleiben `None`: exakt der
    unbekannte Ausgang, fuer den R-P3 ausdruecklich gilt (kein
    `finish_received`/`finish_error`, s. `03_RECOVERY_VERTRAG.md §R-P3`)."""
    return request_ledger.begin(
        run_dir, role=role, content="SYNTHETIC unbeantworteter R-P3-Request", reserved_usd=0.01,
        table_id=table_id, section_id=section_id, turn_idx=turn_idx, participant=participant,
    )


def make_p5_drift_hold(run_dir: Path, *, persona_key="flo_p5", char_id="CHR-P5-01") -> dict:
    """Treibt EINEN echten `pursue_single_figure_correction`-Durchlauf bis
    zu einem terminalen Drift-Hold bei `attempts_used=1` (03 §R-P5s exakte
    Fallklasse): `candidate_block` ist ein schemaungueltiger Entwurf (Wallet
    als blanke Zahl statt Objekt -- derselbe Fehlerpfad wie `test_w48_
    save_correction_2026_10_07.py:_wallet_as_number`); die EINZIGE
    skriptierte SL-Antwort behebt den Schemafehler, AENDERT aber zusaetzlich
    `name` (ein nicht gemeldeter Fehlerpfad) -- `detect_unjustified_drift`
    erkennt das als unerwuenschte Drift, `pursue_single_figure_correction`
    haelt terminal (`mark_hold(reason='unjustified_semantic_drift')`), OHNE
    weiteren automatischen Versand.

    Liefert `repair_key`, den gueltigen Vergleichs-Save (`valid_save`, vom
    REALEN unveraenderten Validator akzeptierbar) und den urspruenglichen
    schemaungueltigen Entwurf (`invalid_candidate`).

    F-WALLET-LOSS (ZR-N2-LIVEBUNDLE-FRESH-20261018-R1): `valid_save` trug
    frueher KEIN Wallet (`economy={}` per `full_v7_save`-Default) --
    unbeabsichtigt derselbe Walletbetrag-verschwindet-ersatzlos-Fall, den
    der F-WALLET-LOSS-Fix jetzt korrekt als Drift ablehnt (dieses Fixture
    testet P5-Grant-/Recovery-Mechanik, nicht Wallet-Inhalt -- der
    Walletbetrag muss deshalb wertgleich WEITERGEFUEHRT werden, nicht
    verschwinden). `valid_save` erhaelt jetzt denselben Betrag (500) im
    gueltigen `{"balance": 500}`-Objekt -- byte-identischer Wert, nur
    gueltig geformt, exakt wie `drifted`s Wallet (nur ohne den zusaetzlich
    gedrifteten Namen)."""
    invalid_candidate = full_v7_save(char_id, name="Flo")
    invalid_candidate["economy"] = {"wallets": {char_id: 500}}
    drifted = full_v7_save(char_id, name="DRIFTED-NAME")
    drifted["economy"] = {"wallets": {char_id: {"balance": 500}}}
    valid_save = full_v7_save(char_id, name="Flo")
    valid_save["economy"] = {"wallets": {char_id: {"balance": 500}}}

    gm = ScriptedGm([_as_json_block(drifted)])
    outcome = save_correction.pursue_single_figure_correction(
        run_dir=run_dir, participant_id=persona_key, expected_chrononaut_id=char_id,
        candidate_block=invalid_candidate, gm_transport=gm, role=save_correction.ROLE_CREATION,
    )
    repair_key = save_correction.save_correction_domain.creation_repair_key(persona_key, char_id)
    record = save_correction.load_record(run_dir, repair_key)
    if outcome.status != "hold" or outcome.reason != "unjustified_semantic_drift":
        raise AssertionError(f"Fixture-Vorbedingung verletzt: outcome={outcome}")
    if record.get("attempts_used") != 1:
        raise AssertionError(f"Fixture-Vorbedingung verletzt: attempts_used={record.get('attempts_used')!r}")
    return {
        "repair_key": repair_key, "persona_key": persona_key, "char_id": char_id,
        "valid_save": valid_save, "invalid_candidate": invalid_candidate, "drifted_reply": drifted,
        "record": record,
    }


def apply_p5_grant(run_dir: Path, repair_key: str, *, operator_decision="grant-one-extra",
                    reason="flo explicitly authorizes one additional synthetic attempt",
                    evidence_ref="test-evidence") -> dict:
    """R2-N1-Fix (`core_plan_clarification`): `apply_p5` verlangt jetzt einen
    vom Aufrufer gelieferten vorherigen `plan_p5`-Plan (`plan=None` wird
    fail-closed abgelehnt, s. `recovery_ops.RecoveryPlanRequiredError`) --
    dieser Testtreiber wird transparent an die neue Signatur angepasst
    (plant zuerst, appliziert danach mit `plan=`), ohne die eigentliche vom
    jeweiligen Test geprüfte Produktentscheidung zu beeinflussen."""
    plan = recovery_ops.plan_p5(run_dir, repair_key=repair_key)
    return recovery_ops.apply_p5(
        run_dir, repair_key=repair_key, operator_decision=operator_decision, reason=reason,
        evidence_ref=evidence_ref, plan=plan,
    )


def apply_p3_audit(run_dir: Path, *, table_id, section_id, role, turn_idx, participant, request_id,
                    operator_decision="classify-unknown", reason="lost reply after outage",
                    evidence_ref="test-evidence") -> dict:
    """R2-N1-Fix (`core_plan_clarification`): analog `apply_p5_grant` --
    plant zuerst ueber `plan_p3`, appliziert dann mit `plan=`."""
    plan = recovery_ops.plan_p3(
        run_dir, table_id=table_id, section_id=section_id, role=role, turn_idx=turn_idx,
        participant=participant, request_id=request_id,
    )
    return recovery_ops.apply_p3(
        run_dir, table_id=table_id, section_id=section_id, role=role, turn_idx=turn_idx,
        participant=participant, request_id=request_id, operator_decision=operator_decision,
        reason=reason, evidence_ref=evidence_ref, plan=plan,
    )


def snapshot_tree(root: Path) -> dict:
    """Pfad -> (Grösse, mtime_ns) fuer JEDE Datei unter `root` -- fuer den
    `inspect_plan_read_only`-Nachweis 'kein Verzeichnis-/Datei-Nebenwrite'."""
    out = {}
    if not root.exists():
        return out
    for p in sorted(root.rglob("*")):
        if p.is_file():
            st = p.stat()
            out[str(p.relative_to(root))] = (st.st_size, st.st_mtime_ns)
    return out
