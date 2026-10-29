#!/usr/bin/env python3
"""
tests/mmo_sim/test_recovery_ops_r2.py — ZR-RECOVERY-OFFLINE-R2-20261015-R1
(TEST-CATALOG.json `r2_cases`): ausfuehrbare Regression fuer die 18 NEUEN
R2-Achsen (BIND/PATH_LEASE/GATE/TEST), zusaetzlich zu den 22 in
`test_recovery_ops_r1.py` erhaltenen Achsen. Jeder Katalog-ID entspricht
GENAU EINER `test_<id>`-Funktion unten -- einzeln ausweisbar in
TEST-RESULTS.json.

Pure Python, nur `assert`, echter Exitcode. Status `BLOCKED_ENV` fuer
fehlende Umgebung; `ContractGapBlocked` (eigene, NICHT umgebungsbedingte
Kategorie) fuer eine ehrlich ungeloeste Vertragsluecke, die dieser Kandidat
NICHT behebt (s. `test_r2_shared_writer_protocol`/`IMPLEMENTATION.md`) --
beides zaehlt in `main()` gegen `rc=0`, NIE als PASS."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _recovery_ops_r2_fixtures import (  # noqa: E402
    ScriptedGm, apply_p3_audit, apply_p5_grant, make_fifo, make_p3_unknown_request,
    make_p5_drift_hold, make_synthetic_run, never_called_gm, run_actual_writer_proof,
    set_budget_exhausted, set_wall_deadline, write_run_id,
)

import mmo_sim.core.recovery_ops as recovery_ops  # noqa: E402
import mmo_sim.core.request_ledger as request_ledger  # noqa: E402
import mmo_sim.core.save_correction as save_correction  # noqa: E402
from mmo_sim.lab.runner import LabBudget, LabRunner, request_stop  # noqa: E402

_SCRIPTS_MMO_SIM = _REPO_ROOT / "scripts" / "mmo_sim.py"


class EnvironmentBlocked(Exception):
    """Fehlende Umgebung -- `main()` meldet dafuer `BLOCKED_ENV`, NIE `PASS`."""


class ContractGapBlocked(Exception):
    """Eine ehrlich NICHT geschlossene Vertragsluecke (keine Umgebungs-,
    sondern eine Produktfrage) -- `main()` meldet dafuer `BLOCKED` (separat
    von `BLOCKED_ENV`), NIE `PASS`. S. `test_r2_shared_writer_protocol`."""


def _run_cli(data_dir: Path, *argv: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-B", "-u", str(_SCRIPTS_MMO_SIM), "lab", "recovery", *argv, "--data-dir", str(data_dir)],
        capture_output=True, text=True, cwd=str(_REPO_ROOT), env=env,
    )


# ═══════════════════════════════ BIND ═══════════════════════════════════════


def test_r2_plan_run_root_identity():
    """Ein auf Root/Run A, Community A/Generation 1 erstellter P3-Plan darf
    NICHT mit identischen Requestbytes auf Root/Run B, Community B/
    Generation 2 appliziert werden (GENERALREVIEW.md §3 Originalbeleg)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_a = make_synthetic_run(root / "a")
        write_run_id(run_a, "RUN-A")
        rid = make_p3_unknown_request(run_a, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1, participant="alice")
        plan = recovery_ops.plan_p3(
            run_a, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
            participant="alice", request_id=rid, community_binding="COMM-A", generation_binding=1,
        )

        # Root B: byte-identische Requestdatei (versehentlich kopierte Quelle).
        run_b = make_synthetic_run(root / "b")
        write_run_id(run_b, "RUN-B")
        import shutil
        shutil.copytree(run_a, run_b, dirs_exist_ok=True)
        write_run_id(run_b, "RUN-B")  # nach dem Copytree erneut sicherstellen

        raised = None
        try:
            recovery_ops.apply_p3(
                run_b, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
                participant="alice", request_id=rid, operator_decision="x", reason="y", evidence_ref="z",
                community_binding="COMM-B", generation_binding=2, plan=plan,
            )
        except recovery_ops.RecoveryPreconditionChangedError as exc:
            raised = exc
        assert raised is not None, "ein Plan von Root A/Community A/Gen 1 durfte NICHT auf Root B/Community B/Gen 2 appliziert werden."


def test_r2_strict_run_json():
    """Fehlende `run_id.json` bleibt `run_id=None` (kein Fehler); eine
    VORHANDENE, aber doppelschluesselige/nichtstring-`run_id` wird
    kontrolliert gesperrt (`RecoveryAuditUnreadableError`), kein
    `None`-Fallback."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        # R2-N1-Fix (transparente Treiberanpassung): `make_synthetic_run`
        # schreibt seit `p3_missing_run_id` standardmaessig eine run_id.json
        # (reale run_dirs haben immer eine) -- dieser Test prueft explizit
        # den Abwesenheitsfall, daher hier bewusst `run_id=None`.
        run_dir = make_synthetic_run(root, run_id=None)
        binding = recovery_ops._run_binding(run_dir)
        assert binding == {"run_dir": str(run_dir), "run_id": None}

        (run_dir / "run_id.json").write_text('{"run_id": "A", "run_id": "B"}', encoding="utf-8")
        raised = None
        try:
            recovery_ops._run_binding(run_dir)
        except recovery_ops.RecoveryAuditUnreadableError as exc:
            raised = exc
        assert raised is not None, "doppelter 'run_id'-Schluessel haette abgelehnt werden muessen."

        (run_dir / "run_id.json").write_text('{"run_id": 123}', encoding="utf-8")
        raised = None
        try:
            recovery_ops._run_binding(run_dir)
        except recovery_ops.RecoveryAuditUnreadableError as exc:
            raised = exc
        assert raised is not None, "nicht-string 'run_id' haette abgelehnt werden muessen."

        (run_dir / "run_id.json").write_text('{"run_id": "RUN-OK"}', encoding="utf-8")
        assert recovery_ops._run_binding(run_dir) == {"run_dir": str(run_dir), "run_id": "RUN-OK"}


def test_r2_cli_expected_plan():
    """Der reale CLI-Einstieg verlangt `--plan-file` (Pflicht); ein
    veralteter/fremder Plan wird abgelehnt (rc=3), ein frischer, tatsaechlich
    vorher geplanter wird akzeptiert (rc=0)."""
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        run_dir = make_synthetic_run(data_dir)
        rid = make_p3_unknown_request(run_dir)

        p_missing = _run_cli(
            data_dir, "apply-p3", "--table-id", "table-1", "--section-id", "section-1", "--role", "gm_turn",
            "--turn-idx", "1", "--participant", "alice", "--request-id", rid,
            "--operator-decision", "classify", "--reason", "r", "--evidence-ref", "e",
        )
        assert p_missing.returncode != 0, "apply-p3 ohne --plan-file haette (argparse) ablehnen muessen."

        p_plan = _run_cli(
            data_dir, "plan-p3", "--table-id", "table-1", "--section-id", "section-1", "--role", "gm_turn",
            "--turn-idx", "1", "--participant", "alice", "--request-id", rid,
        )
        assert p_plan.returncode == 0, p_plan.stderr
        plan_path = data_dir / "plan.json"
        plan_path.write_text(p_plan.stdout, encoding="utf-8")

        tampered_path = data_dir / "tampered.json"
        tampered = json.loads(p_plan.stdout)
        tampered["original_file_sha256"] = "0" * 64
        tampered_path.write_text(json.dumps(tampered), encoding="utf-8")
        p_tampered = _run_cli(
            data_dir, "apply-p3", "--table-id", "table-1", "--section-id", "section-1", "--role", "gm_turn",
            "--turn-idx", "1", "--participant", "alice", "--request-id", rid,
            "--operator-decision", "classify", "--reason", "r", "--evidence-ref", "e", "--plan-file", str(tampered_path),
        )
        assert p_tampered.returncode == 3, p_tampered.stdout

        p_apply = _run_cli(
            data_dir, "apply-p3", "--table-id", "table-1", "--section-id", "section-1", "--role", "gm_turn",
            "--turn-idx", "1", "--participant", "alice", "--request-id", rid,
            "--operator-decision", "classify", "--reason", "r", "--evidence-ref", "e", "--plan-file", str(plan_path),
        )
        assert p_apply.returncode == 0, p_apply.stderr
        assert json.loads(p_apply.stdout)["status"] == "applied"


def test_r2_audit_idempotence_binding():
    """Identische gebundene Felder -> No-op; ANDERE Community/Generation fuer
    DENSELBEN audit_key -> kontrollierter Konflikt (GENERALREVIEW.md §3:
    'Ein vorhandener P3-Audit meldet bei veraenderter Community/Generation
    idempotent_noop' -- jetzt widerlegt)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        rid = make_p3_unknown_request(run_dir)
        first = apply_p3_audit(
            run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
            participant="alice", request_id=rid,
        )
        assert first["status"] == "applied"

        # R2-N1-Fix (`core_plan_clarification`, transparente Treiberanpassung):
        # `apply_p3` verlangt jetzt einen vom Aufrufer gelieferten
        # vorherigen `plan_p3`-Plan -- dieser Test prueft Idempotenz/Konflikt
        # NACH dem Apply, nicht die Planpflicht selbst; ein frischer Plan
        # wird deshalb jeweils unmittelbar davor geplant.
        replan = recovery_ops.plan_p3(
            run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
            participant="alice", request_id=rid,
        )
        identical = recovery_ops.apply_p3(
            run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
            participant="alice", request_id=rid, operator_decision="classify-unknown",
            reason="lost reply after outage", evidence_ref="test-evidence", plan=replan,
        )
        assert identical["status"] == "idempotent_noop"

        raised = None
        try:
            replan2 = recovery_ops.plan_p3(
                run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
                participant="alice", request_id=rid, community_binding="COMM-NEW", generation_binding=7,
            )
            recovery_ops.apply_p3(
                run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
                participant="alice", request_id=rid, operator_decision="classify-unknown",
                reason="lost reply after outage", evidence_ref="test-evidence",
                community_binding="COMM-NEW", generation_binding=7, plan=replan2,
            )
        except recovery_ops.RecoveryConflictError as exc:
            raised = exc
        assert raised is not None, "veraenderte Community/Generation fuer denselben audit_key haette NICHT idempotent_noop sein duerfen."


def test_r2_grant_strict_fields():
    """Ein fremder/falsch beschrifteter Grant (`action` != P5_ACTION), ein
    Grant ohne `operator_decision`, und `allowance=True` werden JEDE vor
    Verbrauch abgelehnt (`try_consume_p5_allowance` -> `False`), kein
    synthetischer Transport, kein Doppelverbrauch."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        for scenario in ("bool_allowance", "wrong_action", "no_operator_decision", "missing_reason"):
            char_id = f"CHR-{scenario.upper()}"
            p5 = make_p5_drift_hold(run_dir, persona_key=f"flo_{scenario}", char_id=char_id)
            granted = apply_p5_grant(run_dir, p5["repair_key"])
            grant_path = recovery_ops._p5_grant_path(run_dir, p5["repair_key"])
            grant = json.loads(grant_path.read_text(encoding="utf-8"))
            if scenario == "bool_allowance":
                grant["allowance"] = True
            elif scenario == "wrong_action":
                grant["action"] = "UNRELATED_ACTION"
            elif scenario == "no_operator_decision":
                grant.pop("operator_decision")
            elif scenario == "missing_reason":
                grant["reason"] = "   "
            grant_path.write_text(json.dumps(grant), encoding="utf-8")

            record = save_correction.load_record(run_dir, p5["repair_key"])
            ok = recovery_ops.try_consume_p5_allowance(run_dir, repair_key=p5["repair_key"], record=record)
            assert ok is False, f"{scenario}: try_consume_p5_allowance haette False liefern muessen."
            after = json.loads(grant_path.read_text(encoding="utf-8"))
            assert after.get("consumed") is not True, f"{scenario}: Grant durfte NICHT als consumed markiert werden."
            gm = ScriptedGm([])
            outcome = save_correction.pursue_single_figure_correction(
                run_dir=run_dir, participant_id=p5["persona_key"], expected_chrononaut_id=p5["char_id"],
                candidate_block=p5["invalid_candidate"], gm_transport=gm, role=save_correction.ROLE_CREATION,
            )
            assert outcome.status == "hold" and len(gm.calls) == 0, f"{scenario}: kein synthetischer Transport erlaubt."
        assert granted["status"] == "applied"


def test_r2_grant_context_at_consumption():
    """Aendert sich die Run-Identitaet NACH dem Grant (vor Verbrauch), wird
    der echte Korrekturpfad auf dem (jetzt fremden) Kontext abgelehnt, KEIN
    synthetischer Transport; auf einem unveraenderten Kontext bleibt der
    Grant weiterhin gueltig verbrauchbar."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        write_run_id(run_dir, "RUN-A")
        p5 = make_p5_drift_hold(run_dir, persona_key="flo_runchange", char_id="CHR-RUNCHANGE")
        apply_p5_grant(run_dir, p5["repair_key"])
        write_run_id(run_dir, "RUN-B")

        gm = ScriptedGm([])
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=p5["persona_key"], expected_chrononaut_id=p5["char_id"],
            candidate_block=p5["invalid_candidate"], gm_transport=gm, role=save_correction.ROLE_CREATION,
        )
        assert outcome.status == "hold" and len(gm.calls) == 0, "ein Run-Identitaetswechsel nach dem Grant darf keinen Transport mehr ausloesen."

        write_run_id(run_dir, "RUN-A")
        gm2 = ScriptedGm([f"```json\n{json.dumps(p5['valid_save'])}\n```"])
        outcome2 = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=p5["persona_key"], expected_chrononaut_id=p5["char_id"],
            candidate_block=p5["invalid_candidate"], gm_transport=gm2, role=save_correction.ROLE_CREATION,
        )
        assert outcome2.status == "accepted" and len(gm2.calls) == 1, "auf unveraendertem Kontext bleibt der Grant gueltig verbrauchbar."


# ═══════════════════════════════ PATH_LEASE ═════════════════════════════════


def test_r2_path_type_matrix():
    """Symlink-Umleitung des `recovery`-Unterpfads, eine FIFO statt einer
    regulaeren Audit-/Grant-Datei, und ein per Symlink ersetztes `lab.lock.json`
    schlagen ALLE kontrolliert fehl -- keine Schreibwirkung ausserhalb des
    freigegebenen Roots."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        inside = root / "inside"
        outside = root / "outside"
        outside.mkdir()
        run_dir = make_synthetic_run(inside)
        rid = make_p3_unknown_request(run_dir)
        (run_dir / "recovery").symlink_to(outside, target_is_directory=True)
        raised = None
        try:
            apply_p3_audit(
                run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
                participant="alice", request_id=rid,
            )
        except recovery_ops.RecoveryError as exc:
            raised = exc
        assert raised is not None, "Symlink-Umleitung des 'recovery'-Unterpfads haette abgelehnt werden muessen."
        escaped = [str(f.relative_to(outside)) for f in outside.rglob("*") if f.is_file()]
        assert not escaped, f"es wurde ausserhalb des Roots geschrieben: {escaped}"

        # FIFO statt regulaerer Datei: _read_strict_json_file darf NICHT
        # blockierend oeffnen, sondern kontrolliert ablehnen.
        root2 = root / "fifo-case"
        run_dir2 = make_synthetic_run(root2)
        recovery_dir = run_dir2 / "recovery" / "p3_audits"
        recovery_dir.mkdir(parents=True)
        fifo_path = recovery_dir / "some_audit_key.json"
        make_fifo(fifo_path)
        raised2 = None
        try:
            recovery_ops._read_strict_json_file(fifo_path)
        except recovery_ops.RecoveryAuditUnreadableError as exc:
            raised2 = exc
        assert raised2 is not None, "eine FIFO statt einer regulaeren Datei haette abgelehnt werden muessen (kein blockierendes Oeffnen)."

        # lab.lock.json als Symlink in ein fremdes Verzeichnis.
        root3 = root / "lock-symlink-case"
        run_dir3 = make_synthetic_run(root3)
        foreign = root / "foreign-lock-target"
        foreign.mkdir()
        foreign_lock = foreign / "lab.lock.json"
        foreign_lock.write_text("", encoding="utf-8")
        (run_dir3 / "lab.lock.json").symlink_to(foreign_lock)
        rid3 = make_p3_unknown_request(run_dir3)
        raised3 = None
        try:
            apply_p3_audit(
                run_dir3, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
                participant="alice", request_id=rid3,
            )
        except recovery_ops.RecoveryError as exc:
            raised3 = exc
        assert raised3 is not None, "ein per Symlink umgeleitetes lab.lock.json haette abgelehnt werden muessen."


def test_r2_path_race_boundary():
    """Ein DRITTER Racer, der die Lock-Datei zwischen `os.open` und dem
    eigenen `flock`-Erwerb unlinkt+neu anlegt, wird per Inode-Nachcheck
    erkannt und der Erwerb kontrolliert neu versucht -- kein Vertrauen auf
    eine veraltete fd (keine Krypto-Zusage gegen den FS-Owner, nur ein
    Zustandsmodell-/Grenzfallschutz)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        rid = make_p3_unknown_request(run_dir)
        from unittest.mock import patch

        real_matches = recovery_ops._SharedWriterExclusivity._fd_still_matches_path
        calls = {"n": 0}

        def flaky_matches(fd, path):
            calls["n"] += 1
            if calls["n"] == 1:
                return False  # simuliert einen dritten Racer: erster Versuch verworfen
            return real_matches(fd, path)

        with patch.object(recovery_ops._SharedWriterExclusivity, "_fd_still_matches_path", side_effect=flaky_matches):
            result = apply_p3_audit(
                run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
                participant="alice", request_id=rid,
            )
        assert result["status"] == "applied"
        assert calls["n"] >= 2, "der Erwerb haette nach dem ersten verworfenen Versuch erneut versucht werden muessen."


def test_r2_unclear_lease_denied():
    """Ein vorhandenes `lab.lock.json` mit strukturell unklarem Inhalt
    (`{"pid": "invalid"}`) bleibt BLOCKIERT, nicht frei -- eine tatsaechlich
    LEERE Lockdatei (positive Gegenkontrolle, GENERALREVIEW.md §4) bleibt
    weiterhin normaler Erstgebrauch."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        rid = make_p3_unknown_request(run_dir)
        (run_dir / "lab.lock.json").write_text('{"pid": "invalid"}', encoding="utf-8")
        raised = None
        try:
            apply_p3_audit(
                run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
                participant="alice", request_id=rid,
            )
        except recovery_ops.RecoveryExclusivityUnavailableError as exc:
            raised = exc
        assert raised is not None, "ein strukturell unklarer Lock-Inhalt haette NICHT als frei behandelt werden duerfen."

        root2 = root / "empty-lease"
        run_dir2 = make_synthetic_run(root2)
        rid2 = make_p3_unknown_request(run_dir2)
        (run_dir2 / "lab.lock.json").write_text("", encoding="utf-8")
        result = apply_p3_audit(
            run_dir2, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
            participant="alice", request_id=rid2,
        )
        assert result["status"] == "applied", "eine tatsaechlich leere Lockdatei ist KEIN Defekt (positive Gegenkontrolle)."


def test_r2_lock_acquire_error_cleanup():
    """`OSError` (z.B. EIO) aus dem Inode-Nachcheck NACH erfolgreichem
    `flock`-Erwerb hinterlaesst KEIN verlorenes fd/keinen verwaisten Lock --
    ein gesunder Nachfolgeaufruf funktioniert unmittelbar danach."""
    import errno
    import fcntl
    import os as _os
    from unittest.mock import patch

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        rid = make_p3_unknown_request(run_dir)

        with patch.object(
            recovery_ops._SharedWriterExclusivity, "_fd_still_matches_path",
            side_effect=OSError(errno.EIO, "synthetic stat failure"),
        ):
            raised = None
            try:
                apply_p3_audit(
                    run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
                    participant="alice", request_id=rid,
                )
            except recovery_ops.RecoveryExclusivityUnavailableError as exc:
                raised = exc
            assert raised is not None, "ein EIO beim Inode-Nachcheck haette kontrolliert HOLD liefern muessen."

        lock_path = run_dir / "lab.lock.json"
        probe_fd = _os.open(lock_path, _os.O_RDWR)
        try:
            fcntl.flock(probe_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(probe_fd, fcntl.LOCK_UN)
        except BlockingIOError:
            raise AssertionError("Lock ist nach dem EIO-Fehlausgang weiterhin belegt -- verwaister Lock/verlorene fd.")
        finally:
            _os.close(probe_fd)

        result = apply_p3_audit(
            run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
            participant="alice", request_id=rid,
        )
        assert result["status"] == "applied", "ein gesunder Nachfolgeaufruf haette unmittelbar funktionieren muessen."


def test_r2_shared_writer_protocol():
    """R2-N1-Fix (GENERALREVIEW.md §5, `r2_shared_writer_protocol`): ersetzt
    die vorherige KUeNSTLICHE raw-fd/50ms-Erwartung und den unconditional-
    BLOCKED-Stub durch eine ECHTE kausale Writerpruefung (`run_actual_
    writer_proof` in `_recovery_ops_r2_fixtures.py`, transparent adaptiert
    aus General's `probe_actual_writer_handover.py`): zwei ECHTE Prozesse,
    an echten I/O-Grenzen synchron angehalten (kein Mikrosekunden-/
    Zufallssweep), zeigen dass JEDER kritische Write (`lab.status.json`,
    `lab.lock.json`-Unlink) in `LabRunner.release()`/`_release_lock_after_
    failed_start()` von genau einer passenden Autoritaet geschuetzt ist --
    bis zum letzten Write darf kein Nachfolger beginnen (`before_status`/
    `before_unlink` -> Recovery-apply wird verweigert); NACH dem letzten
    Write/Unlink darf ein Nachfolger beginnen, OHNE dass der alte (noch
    offene) fd dessen Lease/Status je veraendert (`after_unlink`/
    `failed_start_after_unlink`). Die Sensitivitaetskontrolle
    (`sensitivity_late_write`, ein ABSICHTLICH FALSCH rekonstruierter
    Referenzablauf mit spaetem Statuswrite NACH Unlink) wird von derselben
    Probe korrekt ALS Nachfolgerueberschreibung erkannt -- reiner
    Sensitivitaetscode, kein Produktbug/-patch.

    Die alte 50ms-/raw-fd-Mitigation (`_UNLINK_RACE_SETTLE_SECONDS` in
    `recovery_ops.py`) bleibt unveraendert bestehen (kein Vertrag, darf
    entfallen) -- diese Funktion verlangt sie NICHT mehr als Beweis; die
    tatsaechlich erforderliche Ausschlusslogik (`_SharedWriterExclusivity`)
    bleibt vollstaendig in Kraft und wird hier real durchlaufen, nicht
    gestubbt. `runner.py`/`recovery_lock.py` wurden dafuer NICHT geaendert
    -- der kausale Nachweis braucht keinen Fix an diesen Dateien (ein
    struktureller Nicht-Ueberlappungs-/fail-closed-Nachweis mit
    unveraendertem Runner ist nach 02_RESTVERTRAG.md zulaessig)."""
    log_dir = Path(tempfile.mkdtemp(prefix="writer-proof-evidence-"))
    results = run_actual_writer_proof(log_dir=log_dir)
    failures = {phase: r for phase, r in results.items() if r["status"] != "PASS"}
    assert not failures, f"writer-proof Phasen fehlgeschlagen: {failures}"
    assert set(results) == {
        "before_status", "before_unlink", "after_unlink", "failed_start_after_unlink", "sensitivity_late_write",
    }
    # Sensitivitaet: der absichtlich FALSCH rekonstruierte Referenzablauf
    # MUSS als Nachfolgerueberschreibung erkannt werden (sonst waere die
    # Probe selbst blind fuer genau den Fehler, den sie zu erkennen behauptet).
    assert "successor_lease_and_status_preserved=False" in results["sensitivity_late_write"]["observation"], (
        "die Sensitivitaetskontrolle haette die Nachfolgerueberschreibung erkennen muessen."
    )
    for phase in ("after_unlink", "failed_start_after_unlink"):
        assert "successor_lease_and_status_preserved=True" in results[phase]["observation"], results[phase]
    for phase in ("before_status", "before_unlink"):
        assert "recovery_denied=True" in results[phase]["observation"], results[phase]


# ═══════════════════════════════ GATE ═══════════════════════════════════════


def test_r2_preexisting_stop_before_consume():
    """Ein bereits VOR dem Verbrauchsversuch gesetzter Stop blockiert den
    P5-Grant-Verbrauch; Grant/Record bleiben UNVERAENDERT, null physische
    Requests (GENERALREVIEW.md §5 Originalbeleg, `probe_p5_gates.py`
    `stop_before_consume`)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        p5 = make_p5_drift_hold(run_dir, persona_key="flo_stop", char_id="CHR-STOP")
        apply_p5_grant(run_dir, p5["repair_key"])
        grant_before = json.loads(recovery_ops._p5_grant_path(run_dir, p5["repair_key"]).read_text(encoding="utf-8"))
        record_before = save_correction.load_record(run_dir, p5["repair_key"])

        request_stop(run_dir, "synthetic review stop")
        gm = ScriptedGm([])
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=p5["persona_key"], expected_chrononaut_id=p5["char_id"],
            candidate_block=p5["invalid_candidate"], gm_transport=gm, role=save_correction.ROLE_CREATION,
        )
        assert outcome.status == "hold" and outcome.reason.startswith("gate_blocked_before_consume:")
        assert len(gm.calls) == 0, "null physische Requests bei bereits gesetztem Stop."
        grant_after = json.loads(recovery_ops._p5_grant_path(run_dir, p5["repair_key"]).read_text(encoding="utf-8"))
        record_after = save_correction.load_record(run_dir, p5["repair_key"])
        assert grant_after == grant_before, "Grant durfte sich nicht veraendern."
        assert record_after["attempts_used"] == record_before["attempts_used"], "attempts_used durfte sich nicht veraendern."


def test_r2_expired_window_before_consume():
    """Ein bereits abgelaufenes Wall-Clock-Fenster (`wall_deadline`)
    blockiert den P5-Grant-Verbrauch GENAUSO VOR jeder Aenderung, null
    physische Requests."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        p5 = make_p5_drift_hold(run_dir, persona_key="flo_window", char_id="CHR-WINDOW")
        apply_p5_grant(run_dir, p5["repair_key"])
        grant_before = json.loads(recovery_ops._p5_grant_path(run_dir, p5["repair_key"]).read_text(encoding="utf-8"))
        record_before = save_correction.load_record(run_dir, p5["repair_key"])

        set_wall_deadline(run_dir, seconds_from_now=-10.0)
        gm = ScriptedGm([])
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=p5["persona_key"], expected_chrononaut_id=p5["char_id"],
            candidate_block=p5["invalid_candidate"], gm_transport=gm, role=save_correction.ROLE_CREATION,
        )
        assert outcome.status == "hold" and outcome.reason.startswith("gate_blocked_before_consume:")
        assert len(gm.calls) == 0
        grant_after = json.loads(recovery_ops._p5_grant_path(run_dir, p5["repair_key"]).read_text(encoding="utf-8"))
        record_after = save_correction.load_record(run_dir, p5["repair_key"])
        assert grant_after == grant_before
        assert record_after["attempts_used"] == record_before["attempts_used"]


def test_r2_insufficient_budget_before_consume():
    """Ein bekannt unzureichendes Budget (`usd_spent >= max_usd`) blockiert
    den P5-Grant-Verbrauch GENAUSO VOR jeder Aenderung, null physische
    Requests."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        p5 = make_p5_drift_hold(run_dir, persona_key="flo_budget", char_id="CHR-BUDGET")
        apply_p5_grant(run_dir, p5["repair_key"])
        grant_before = json.loads(recovery_ops._p5_grant_path(run_dir, p5["repair_key"]).read_text(encoding="utf-8"))
        record_before = save_correction.load_record(run_dir, p5["repair_key"])

        set_budget_exhausted(run_dir, max_usd=0.01)
        gm = ScriptedGm([])
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=p5["persona_key"], expected_chrononaut_id=p5["char_id"],
            candidate_block=p5["invalid_candidate"], gm_transport=gm, role=save_correction.ROLE_CREATION,
        )
        assert outcome.status == "hold" and outcome.reason.startswith("gate_blocked_before_consume:")
        assert len(gm.calls) == 0
        grant_after = json.loads(recovery_ops._p5_grant_path(run_dir, p5["repair_key"]).read_text(encoding="utf-8"))
        record_after = save_correction.load_record(run_dir, p5["repair_key"])
        assert grant_after == grant_before
        assert record_after["attempts_used"] == record_before["attempts_used"]


def test_r2_crash_dispatch_identity():
    """Restartfeste Kopplung von Verbrauch+Requestidentitaet ueber die
    P5-Grant-Verbrauchsgrenze: ein unklarer Versand (bereits offene
    Reservierung fuer denselben Slot, Crash zwischen Versand+Antwort) bleibt
    gesperrt statt einer dritten Anfrage; ein erneuter Konsumversuch auf
    bereits konsumiertem Grant bleibt idempotent (kein Doppelverbrauch,
    s. auch `test_recovery_ops_r1.py::test_p5_consumption_crash_no_double_
    dispatch`, hier mit zusaetzlichem Ledger-Vorzustand)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        p5 = make_p5_drift_hold(run_dir, persona_key="flo_dispatch", char_id="CHR-DISPATCH")
        apply_p5_grant(run_dir, p5["repair_key"])

        # Teil 1 (restartfester Verbrauch): ein erneuter Konsumversuch AUF
        # UNVERAENDERTEM Vorzustand (ein Prozess, der nach dem Konsum, aber
        # VOR dem naechsten Schritt abgestuerzt ist) bleibt idempotent True,
        # OHNE erneuten Schreibzugriff -- kein Doppelverbrauch.
        record_snapshot = save_correction.load_record(run_dir, p5["repair_key"])
        first = recovery_ops.try_consume_p5_allowance(run_dir, repair_key=p5["repair_key"], record=record_snapshot)
        assert first is True
        grant_after_first = json.loads(recovery_ops._p5_grant_path(run_dir, p5["repair_key"]).read_text(encoding="utf-8"))
        assert grant_after_first["consumed"] is True
        second = recovery_ops.try_consume_p5_allowance(run_dir, repair_key=p5["repair_key"], record=record_snapshot)
        assert second is True, "ein erneuter Konsumversuch auf bereits konsumiertem Grant bleibt idempotent True."
        grant_after_second = json.loads(recovery_ops._p5_grant_path(run_dir, p5["repair_key"]).read_text(encoding="utf-8"))
        assert grant_after_second == grant_after_first, "kein erneuter Schreibzugriff bei bereits konsumiertem Grant."

        # Teil 2 (Crashfenster ueber Verbrauch->Reserve->Send): Slot 2
        # (attempts_used wird nach Konsum zu 2) hat bereits eine offene
        # (unklare) Reservierung im Ledger -- simuliert einen Crash zwischen
        # Versand und Antwort/Fehlerabschluss fuer GENAU diesen Slot. Der
        # reale Korrekturpfad (der den bereits konsumierten Grant ueber
        # `pursue_single_figure_correction` erneut antrifft) darf daraus
        # KEINE dritte/zweite physische Anfrage ableiten -- Unknown-Sent
        # bleibt gesperrt.
        request_ledger.begin(
            run_dir, role=save_correction.ROLE_CREATION, content="SYNTHETIC in-flight",
            reserved_usd=0.01, table_id=None, section_id=None, turn_idx=2, participant=p5["persona_key"],
        )
        gm = ScriptedGm([f"```json\n{json.dumps(p5['valid_save'])}\n```"])
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=p5["persona_key"], expected_chrononaut_id=p5["char_id"],
            candidate_block=p5["invalid_candidate"], gm_transport=gm, role=save_correction.ROLE_CREATION,
        )
        assert outcome.status == "hold" and "unclear_sent_in_flight" in (outcome.reason or ""), outcome
        assert len(gm.calls) == 0, "eine bereits offene Reservierung darf NIE eine dritte/zweite physische Anfrage ausloesen."


# ═══════════════════════════ R2-N1 BIND (neu) ═══════════════════════════════


def test_p3_missing_run_id():
    """R2-N1 (`p3_missing_run_id`, GENERALREVIEW.md §4 BIND): `apply_p3`
    appliziert NICHT mehr bei fehlender/ungueltiger Run-Identitaet mit
    `run_id:null` -- fail-closed (`RecoveryMissingRunIdentityError`), kein
    Audit-Nebenwrite. `plan_p3`/`inspect` melden die Abwesenheit weiterhin
    rein lesend (`run_binding={"run_id": None, ...}`)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root, run_id=None)
        rid = make_p3_unknown_request(run_dir)
        plan = recovery_ops.plan_p3(
            run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
            participant="alice", request_id=rid,
        )
        assert plan["run_binding"] == {"run_dir": str(run_dir), "run_id": None}, "plan_p3 muss die Abwesenheit weiterhin rein lesend melden."
        raised = None
        try:
            recovery_ops.apply_p3(
                run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
                participant="alice", request_id=rid, operator_decision="x", reason="y",
                evidence_ref="z", plan=plan,
            )
        except recovery_ops.RecoveryMissingRunIdentityError as exc:
            raised = exc
        assert raised is not None, "apply_p3 mit fehlender run_id.json haette fail-closed ablehnen muessen."
        assert not (run_dir / "recovery" / "p3_audits").exists(), "kein Audit darf aus einer fehlenden Run-Identitaet entstanden sein."


def test_p3_plan_wrong_action():
    """R2-N1 (`p3_plan_wrong_action`): ein sonst vollstaendig gueltiger Plan
    mit FALSCHER `action` wird abgelehnt -- der Plan<->Apply-Abgleich deckt
    jetzt auch die Aktionsentscheidung ab, nicht nur Hash/Bindungen."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        rid = make_p3_unknown_request(run_dir)
        plan = recovery_ops.plan_p3(
            run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
            participant="alice", request_id=rid,
        )
        tampered = dict(plan)
        tampered["action"] = "UNRELATED_ACTION"
        raised = None
        try:
            recovery_ops.apply_p3(
                run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
                participant="alice", request_id=rid, operator_decision="x", reason="y",
                evidence_ref="z", plan=tampered,
            )
        except recovery_ops.RecoveryPreconditionChangedError as exc:
            raised = exc
        assert raised is not None, "ein Plan mit falscher action haette NICHT appliziert werden duerfen."
        assert not (run_dir / "recovery" / "p3_audits").exists(), "kein Audit darf aus einem Plan mit falscher action entstanden sein."


def test_p3_plan_missing():
    """R2-N1 (`p3_plan_missing`, CONTROL.json `core_plan_clarification`):
    JEDER oeffentliche Mutations-Einstieg -- `apply_p3`/`apply_p5`
    eingeschlossen, nicht nur die bereits an `--plan-file` gebundene CLI --
    verlangt einen vom Aufrufer tatsaechlich gelieferten vorherigen Plan.
    `plan=None` appliziert NICHT mehr stillschweigend neu geplant."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        rid = make_p3_unknown_request(run_dir)
        raised_p3 = None
        try:
            recovery_ops.apply_p3(
                run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
                participant="alice", request_id=rid, operator_decision="x", reason="y",
                evidence_ref="z",
            )
        except recovery_ops.RecoveryPlanRequiredError as exc:
            raised_p3 = exc
        assert raised_p3 is not None, "apply_p3 ohne plan (plan=None) haette fail-closed ablehnen muessen."
        assert not (run_dir / "recovery").exists(), "kein Nebenwrite ohne gelieferten Plan."

        p5 = make_p5_drift_hold(run_dir, persona_key="flo_missing_plan", char_id="CHR-MISSING-PLAN")
        raised_p5 = None
        try:
            recovery_ops.apply_p5(
                run_dir, repair_key=p5["repair_key"], operator_decision="x", reason="y", evidence_ref="z",
            )
        except recovery_ops.RecoveryPlanRequiredError as exc:
            raised_p5 = exc
        assert raised_p5 is not None, "apply_p5 ohne plan (plan=None) haette fail-closed ablehnen muessen."
        assert not recovery_ops._p5_grant_path(run_dir, p5["repair_key"]).exists(), "kein Grant-Nebenwrite ohne gelieferten Plan."


def test_p5_consumed_bad_type():
    """R2-N1 (`p5_consumed_bad_type`): ein Grant mit `consumed: "false"`
    (String statt echtem bool) ist in Python truthy -- wird jetzt NICHT
    mehr akzeptiert; `try_consume_p5_allowance` liefert `False`, kein
    synthetischer Transport/Save, der Grant bleibt unveraendert."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        p5 = make_p5_drift_hold(run_dir, persona_key="flo_bad_consumed", char_id="CHR-BAD-CONSUMED")
        apply_p5_grant(run_dir, p5["repair_key"])
        grant_path = recovery_ops._p5_grant_path(run_dir, p5["repair_key"])
        grant = json.loads(grant_path.read_text(encoding="utf-8"))
        grant["consumed"] = "false"
        grant_path.write_text(json.dumps(grant), encoding="utf-8")

        record = save_correction.load_record(run_dir, p5["repair_key"])
        ok = recovery_ops.try_consume_p5_allowance(run_dir, repair_key=p5["repair_key"], record=record)
        assert ok is False, "consumed als String 'false' haette NICHT als konsumierbar akzeptiert werden duerfen."
        after = json.loads(grant_path.read_text(encoding="utf-8"))
        assert after == grant, "der strukturell unklare Grant darf NICHT ueberschrieben worden sein."

        gm = never_called_gm()
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=p5["persona_key"], expected_chrononaut_id=p5["char_id"],
            candidate_block=p5["invalid_candidate"], gm_transport=gm, role=save_correction.ROLE_CREATION,
        )
        assert outcome.status == "hold", outcome
        assert len(gm.calls) == 0, "ein strukturell unklarer Grant-Typ darf NIE einen synthetischen Transport ausloesen."


# ═══════════════════════ R2-N1 PATH/LEASE/CLEANUP (neu) ══════════════════════


def test_p3_marker_symlink():
    """R2-N1 (`p3_marker_symlink`, GENERALREVIEW.md §4 PATH/LEASE): ein
    SYNTHETIC_ROOT_MARKER, der ein Symlink auf eine fremde reguläre Datei
    ist, wird abgelehnt -- kein synthetischer Nachweis ueber einen
    symlinked Marker."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root, synthetic_marker=False)
        foreign_target = root / "foreign-file.txt"
        foreign_target.write_text("kein echter synthetischer Marker\n", encoding="utf-8")
        (run_dir / recovery_ops.SYNTHETIC_ROOT_MARKER).symlink_to(foreign_target)
        rid = make_p3_unknown_request(run_dir)
        plan = recovery_ops.plan_p3(
            run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
            participant="alice", request_id=rid,
        )
        raised = None
        try:
            recovery_ops.apply_p3(
                run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
                participant="alice", request_id=rid, operator_decision="x", reason="y",
                evidence_ref="z", plan=plan,
            )
        except recovery_ops.RecoveryUnsafeRootError as exc:
            raised = exc
        assert raised is not None, "ein symlinked SYNTHETIC_ROOT_MARKER haette abgelehnt werden muessen."
        assert not (run_dir / "recovery" / "p3_audits").exists(), "kein Audit ueber einen symlinked Marker."


def test_p3_requests_symlink():
    """R2-N1 (`p3_requests_symlink`): ein symlinked `requests`-Unterbaum
    wird abgelehnt -- nicht nur das `recovery`-Verzeichnis wird gegen
    Symlink-Umleitung geprueft."""
    import shutil
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        rid = make_p3_unknown_request(run_dir)
        real_requests = run_dir / "requests"
        foreign_requests = root / "foreign-requests"
        shutil.move(str(real_requests), str(foreign_requests))
        real_requests.symlink_to(foreign_requests, target_is_directory=True)
        raised = None
        try:
            recovery_ops.plan_p3(
                run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
                participant="alice", request_id=rid,
            )
        except recovery_ops.RecoveryUnsafeRootError as exc:
            raised = exc
        assert raised is not None, "ein symlinked requests-Unterbaum haette bereits bei plan_p3 abgelehnt werden muessen."
        raised_inspect = None
        try:
            recovery_ops.inspect_p3_candidates(run_dir)
        except recovery_ops.RecoveryUnsafeRootError as exc:
            raised_inspect = exc
        assert raised_inspect is not None, "inspect_p3_candidates haette denselben symlinked requests-Unterbaum ablehnen muessen."


def test_p3_lease_missing_pid():
    """R2-N1 (`p3_lease_missing_pid`): eine nichtleere Lease OHNE eindeutige
    gueltige Besitzer-PID (`{}` oder eine JSON-Liste) ist UNKNOWN/HOLD, NIE
    automatisch frei -- dieselbe konservative Sicht wie `LabRunner.
    _acquire_lock`. Eine tatsaechlich LEERE Lockdatei bleibt gueltig
    (positive Gegenkontrolle)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        rid = make_p3_unknown_request(run_dir)
        plan = recovery_ops.plan_p3(
            run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
            participant="alice", request_id=rid,
        )
        lock_path = run_dir / "lab.lock.json"
        for bad_payload in ('{}', '[]', '[1, 2]', '{"owner": "flo"}'):
            lock_path.write_text(bad_payload, encoding="utf-8")
            raised = None
            try:
                recovery_ops.apply_p3(
                    run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
                    participant="alice", request_id=rid, operator_decision="x", reason="y",
                    evidence_ref="z", plan=plan,
                )
            except recovery_ops.RecoveryExclusivityUnavailableError as exc:
                raised = exc
            assert raised is not None, f"unklare Lease {bad_payload!r} haette NICHT als frei behandelt werden duerfen."
            assert lock_path.read_text(encoding="utf-8") == bad_payload, "die unklare Lease darf nicht veraendert worden sein."
            lock_path.unlink()

        # Positive Gegenkontrolle (GENERALREVIEW.md §4): eine tatsaechlich
        # LEERE Lockdatei ist weiterhin KEIN Defekt -- nur eine NICHTLEERE,
        # aber unzuordenbare Nutzlast wird abgelehnt.
        lock_path.write_text("", encoding="utf-8")
        result = recovery_ops.apply_p3(
            run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
            participant="alice", request_id=rid, operator_decision="x", reason="y",
            evidence_ref="z", plan=plan,
        )
        assert result["status"] == "applied", "eine tatsaechlich LEERE Lockdatei haette weiterhin gueltig sein muessen."


def test_release_unlock_error_closes_owned_fd():
    """R2-N1 (`release_unlock_error_closes_owned_fd`): ein injiziertes
    OSError (EIO) direkt aus `fcntl.flock(..., LOCK_UN)` in
    `_SharedWriterExclusivity.__exit__` schliesst die eigene fd TROTZDEM
    (finally) -- kein Leck, ein gesunder Nachfolger bleibt nicht blockiert.
    Der Primaerfehler aus LOCK_UN wird dabei NICHT verschluckt (kein
    Scheinerfolg); es wird ausschliesslich die EIGENE fd geschlossen."""
    import fcntl
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        ctx = recovery_ops._SharedWriterExclusivity(run_dir)
        ctx.__enter__()
        owned_fd = ctx._fd
        assert owned_fd is not None

        orig_flock = fcntl.flock

        def failing_flock(fd, op):
            if fd == owned_fd and op == fcntl.LOCK_UN:
                raise OSError(5, "synthetic EIO on LOCK_UN")
            return orig_flock(fd, op)

        fcntl.flock = failing_flock
        raised = None
        try:
            try:
                ctx.__exit__(None, None, None)
            except OSError as exc:
                raised = exc
        finally:
            fcntl.flock = orig_flock
        assert raised is not None, "der injizierte LOCK_UN-Fehler haette propagieren muessen (kein Scheinerfolg)."
        assert ctx._fd is None, "die eigene fd-Referenz haette trotz LOCK_UN-Fehler aufgeraeumt werden muessen."
        closed = False
        try:
            os.fstat(owned_fd)
        except OSError:
            closed = True
        assert closed, "die eigene fd haette TROTZ des LOCK_UN-Fehlers geschlossen werden muessen (finally, kein Leck)."

        healthy = recovery_ops._SharedWriterExclusivity(run_dir)
        healthy.__enter__()
        try:
            assert healthy._fd is not None, "ein gesunder Nachfolger haette nach dem aufgeraeumten Fehlerausgang normal erwerben muessen."
        finally:
            healthy.__exit__(None, None, None)


# ═══════════════════════════════ R2-N1 GATE (neu) ════════════════════════════


def test_p5_known_reservation_insufficient():
    """R2-N1 (`p5_known_reservation_insufficient`, GENERALREVIEW.md §4
    GATE): die tatsaechlich beabsichtigte naechste Reservierung (realer
    Korrekturtext, echtes Outputlimit, bestehende `reservation_for_wire_
    text`) wird jetzt VOR jedem Grant-/`attempts_used`-Verbrauch gegen das
    Budget geprueft -- nicht nur die kleinere Default-Pauschale. Gegenprobe:
    ein Restbudget, das fuer die Default-Pauschale reicht, aber NICHT fuer
    den tatsaechlichen Korrekturtext -> HOLD, Grant/Record exakt
    unveraendert, null I/O (kein Transportcall)."""
    from mmo_sim.core.admission import _synthetic_prices, reservation_for_wire_text, write_test_profile

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        p5 = make_p5_drift_hold(run_dir, persona_key="flo_gate", char_id="CHR-GATE-INSUFFICIENT")
        apply_p5_grant(run_dir, p5["repair_key"])
        grant_path = recovery_ops._p5_grant_path(run_dir, p5["repair_key"])
        record_path = save_correction._record_path(run_dir, p5["repair_key"])
        grant_before = grant_path.read_bytes()
        record_before = record_path.read_bytes()

        # Dieselbe Nachricht, die der echte while-Loop fuer GENAU diesen
        # P5-Zusatzversuch bauen wuerde (identischer attempt_no/acceptance/
        # original_block) -- bestimmt die REALE Reservierung.
        record = save_correction.load_record(run_dir, p5["repair_key"])
        pending_block = record.get("bound_block")
        acceptance = save_correction.save_correction_domain.evaluate(pending_block, p5["char_id"])
        message = save_correction.save_correction_domain.build_correction_message(
            persona_key=p5["persona_key"], char_id=p5["char_id"],
            operation_label=f"{save_correction.ROLE_CREATION}:{p5['persona_key']}", acceptance=acceptance,
            original_block=pending_block, attempt_no=record.get("attempts_used", 1) + 1,
            max_attempts=save_correction.MAX_ADDITIONAL_REQUESTS,
        )
        real_reserved = reservation_for_wire_text(message)
        _, price_out = _synthetic_prices()
        assert real_reserved > price_out, (
            "Testvoraussetzung verletzt: der echte Korrekturtext muss teurer reservieren als die "
            "Default-Pauschale, sonst beweist dieser Fall nichts."
        )
        max_usd = (price_out + real_reserved) / 2.0  # genug fuer die Pauschale, zu wenig fuer die echte Reserve
        write_test_profile(run_dir, max_usd=max_usd)

        gm = never_called_gm()
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=p5["persona_key"], expected_chrononaut_id=p5["char_id"],
            candidate_block=p5["invalid_candidate"], gm_transport=gm, role=save_correction.ROLE_CREATION,
        )
        assert outcome.status == "hold" and "gate_blocked_before_consume" in (outcome.reason or ""), outcome
        assert len(gm.calls) == 0, "null physische Requests -- das Gate muss VOR jedem Transport blockieren."
        assert grant_path.read_bytes() == grant_before, "der Grant muss exakt unveraendert bleiben (null I/O)."
        assert record_path.read_bytes() == record_before, "der Record (inkl. attempts_used) muss exakt unveraendert bleiben."


# ═══════════════════════════════ TEST ═══════════════════════════════════════


def test_r2_portable_required_fixtures():
    """C-Fix (ZR-LIVEWEG-PR-KANDIDAT-20261016-R1, 01_AUFTRAG.md C):
    `test_recovery_ops_r1.py` bindet seine beiden Pflichtfixtures jetzt
    ueber `_recovery_public_fixture_paths` -- OHNE `ZEITRISS_R1_BUDGET_CALC`/
    `ZEITRISS_R1_CONTROL_JSON`/`ZEITRISS_R2_PKG_ROOT` (kein privates
    Pruefpaket, kein Exchange-/Chatpaket) resolviert sie den NEUTRALEN
    Repo-Default (`tests/mmo_sim/fixtures/recovery_contract/`) und ALLE
    22 Faelle laufen real durch, rc=0 -- genau der Nachweis, den ein
    frischer oeffentlicher Checkout erbringen muss."""
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    for name in ("ZEITRISS_R1_BUDGET_CALC", "ZEITRISS_R1_CONTROL_JSON", "ZEITRISS_R2_PKG_ROOT"):
        env.pop(name, None)
    proc = subprocess.run(
        [sys.executable, "-B", str(_HERE / "test_recovery_ops_r1.py")],
        capture_output=True, text=True, env=env, cwd=str(_HERE),
    )
    assert proc.returncode == 0, f"rc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}"
    assert "22/22 bestanden, 0 fehlgeschlagen, 0 BLOCKED_ENV." in proc.stdout, proc.stdout


def test_r2_missing_fixture_nonzero():
    """Pflichtfixture-Fehlen wird jetzt ausdruecklich ueber eine auf eine
    NICHT vorhandene Datei zeigende Env simuliert (01_AUFTRAG.md C: 'waehlt
    jetzt ausdruecklich eine nicht vorhandene Datei, statt den legalen
    Repo-Default durch Weglassen einer optionalen Env zu verbieten') -- ein
    blosses Weglassen der Variablen wuerde seit dem C-Fix den GUELTIGEN
    neutralen Default binden und faelschlich PASS liefern, kein BLOCKED_ENV
    mehr. `test_recovery_ops_r1.py` bleibt fuer den erkennbar falschen Pfad
    weiterhin sichtbar BLOCKED_ENV UND liefert einen NICHTNULL Exitcode."""
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.pop("ZEITRISS_R2_PKG_ROOT", None)
    env["ZEITRISS_R1_CONTROL_JSON"] = str(Path(tempfile.mkdtemp()) / "does-not-exist-control.json")
    env.pop("ZEITRISS_R1_BUDGET_CALC", None)
    proc = subprocess.run(
        [sys.executable, "-B", str(_HERE / "test_recovery_ops_r1.py")],
        capture_output=True, text=True, env=env, cwd=str(_HERE),
    )
    assert proc.returncode != 0, (
        f"eine ausdruecklich auf eine fehlende Datei zeigende Pflichtfixture haette einen "
        f"NICHTNULL Exitcode liefern muessen (rc={proc.returncode}).\n{proc.stdout}"
    )
    assert "BLOCKED_ENV" in proc.stdout


def test_r2_all_legacy_and_positive_controls():
    """Alle 22 geerbten logischen Achsen (`test_recovery_ops_r1.py`) bleiben
    auf den R2-Kandidatenbytes bestanden -- echte ScriptedGm-/Validator-
    Pfade, keine Produktaenderung umgeht eine Pflichtpruefung. ZUSAETZLICH
    zum neutralen Default (s. `test_r2_portable_required_fixtures`) bleibt
    auch die explizite Env-Bindung selbst funktionsfaehig (Rueckwaerts-
    kompatibilitaet fuer einen Betreiber mit eigenem Referenzpaket) --
    hier ausdruecklich auf die NEUTRALEN Repo-Fixtures selbst gebunden
    (kein privates Paket noetig, um diesen Zweig zu pruefen)."""
    from _recovery_public_fixture_paths import DEFAULT_BUDGET_CALC, DEFAULT_CONTROL_JSON

    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.pop("ZEITRISS_R2_PKG_ROOT", None)
    env["ZEITRISS_R1_BUDGET_CALC"] = str(DEFAULT_BUDGET_CALC)
    env["ZEITRISS_R1_CONTROL_JSON"] = str(DEFAULT_CONTROL_JSON)
    proc = subprocess.run(
        [sys.executable, "-B", str(_HERE / "test_recovery_ops_r1.py")],
        capture_output=True, text=True, env=env, cwd=str(_HERE),
    )
    assert proc.returncode == 0, f"rc={proc.returncode}\n{proc.stdout}\n{proc.stderr}"
    assert "22/22 bestanden, 0 fehlgeschlagen, 0 BLOCKED_ENV." in proc.stdout, proc.stdout


def main() -> int:
    tests = [v for k, v in list(globals().items()) if k.startswith("test_") and callable(v)]
    passed, failed, blocked_env, blocked = 0, 0, 0, 0
    for t in sorted(tests, key=lambda f: f.__name__):
        try:
            t()
            print(f"OK      {t.__name__}")
            passed += 1
        except EnvironmentBlocked as e:
            blocked_env += 1
            print(f"BLOCKED_ENV {t.__name__}: {e}")
        except ContractGapBlocked as e:
            blocked += 1
            print(f"BLOCKED {t.__name__}: {e}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL    {t.__name__}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR   {t.__name__}:")
            traceback.print_exc()
    print(f"\n{passed}/{len(tests)} bestanden, {failed} fehlgeschlagen, {blocked_env} BLOCKED_ENV, {blocked} BLOCKED.")
    return 0 if failed == 0 and blocked_env == 0 and blocked == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
