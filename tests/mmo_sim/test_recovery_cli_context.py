#!/usr/bin/env python3
"""
tests/mmo_sim/test_recovery_cli_context.py — ZR-SPIELTEST-INTEGRATION-
20261015-R1: portable Regression fuer den integrierten
`mmo_sim/lab/recovery_cli.py`-Seed (R2-BIND-Fix, GENERALREVIEW.md §3:
"Die CLI uebergibt ueberhaupt keinen freigegebenen Plan/Erwartungshash an
Apply" / "`--community` bei Apply, jedoch nicht beim entsprechenden Plan").

Deckt genau die vier echten CLI-Subprozess-Roundtrips ab, die GENERALREVIEW
§3 als Erstprobe auf dem Seed beschreibt (P3/P5, je ohne und mit
Gemeinschaftskontext), PLUS einen Negativfall (Community-Mismatch zwischen
Plan und Apply bleibt kontrolliert abgelehnt -- Core-Pruefung wird durch
den Seed NICHT entfernt) sowie einen `--plan-file`-Robustheitsfall.

Pure Python, nur `assert`, echter Exitcode -- gleiches Muster wie
`test_recovery_ops_r1.py`/`test_recovery_ops_r2.py` (von `run_all.py`
automatisch ueber `test_*.py` entdeckt). Echte `scripts/mmo_sim.py lab
recovery ...`-Subprozessaufrufe (derselbe oeffentliche Produkt-CLI-Pfad wie
im Produkt), NUR gegen frische, selbst angelegte synthetische
`RECOVERY_SYNTHETIC_TEST_ROOT`-Testroots -- kein echter LA1-Root, kein
Netz, keine Modellinferenz.

Portable Env-Bindung: `_REPO_ROOT`/`_SCRIPTS_MMO_SIM` werden ausschliesslich
relativ zu `__file__` aufgeloest (kein fest verdrahteter `/home/...`-Pfad).
Fehlt die fuer diese Suite notwendige Pflichtfixture (das Produkt-CLI-
Einstiegsskript `scripts/mmo_sim.py` oder das gemeinsame Fixturemodul
`_recovery_ops_r1_fixtures.py`, z.B. bei einem unvollstaendigen Checkout),
bleibt JEDER betroffene Fall ehrlich `BLOCKED_ENV` (nicht `PASS`,
analog `test_recovery_ops_r1.py`'s `EnvironmentBlocked`); `main()` liefert
dafuer einen NICHTNULL Exitcode."""
from __future__ import annotations

import json
import os
import subprocess
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

_SCRIPTS_MMO_SIM = _REPO_ROOT / "scripts" / "mmo_sim.py"


class EnvironmentBlocked(Exception):
    """Fehlende Pflichtfixture (Produkt-CLI-Skript oder Fixturemodul) --
    `main()` meldet dafuer `BLOCKED_ENV`, NIE `PASS`. Kein fest
    verdrahteter `/home/...`-Ersatzpfad; alle Pfade sind relativ zu
    `__file__`/`_REPO_ROOT`."""


def _require_fixture_module():
    if not _SCRIPTS_MMO_SIM.is_file():
        raise EnvironmentBlocked(
            f"Produkt-CLI-Einstiegsskript nicht gefunden unter {_SCRIPTS_MMO_SIM} "
            "(portabel relativ zu __file__ aufgeloest) -- unvollstaendiges Checkout."
        )
    try:
        import _recovery_ops_r1_fixtures  # noqa: F401
    except ImportError as exc:
        raise EnvironmentBlocked(
            f"Gemeinsames Fixturemodul '_recovery_ops_r1_fixtures' nicht importierbar ({exc})."
        ) from exc


_require_fixture_module()

from _recovery_ops_r1_fixtures import (  # noqa: E402
    make_p3_unknown_request, make_p5_drift_hold, make_synthetic_run,
)


def _run_cli(data_dir: Path, *argv: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-B", "-u", str(_SCRIPTS_MMO_SIM), "lab", "recovery", *argv, "--data-dir", str(data_dir)],
        capture_output=True, text=True, cwd=str(_REPO_ROOT), env=env, timeout=30,
    )


def _plan_then_apply(data_dir, run_dir, kind, ids, *, plan_context, apply_context, expect_apply_rc=0):
    """Ein echter Plan->Apply-Roundtrip ueber den oeffentlichen Produkt-CLI-
    Pfad (`scripts/mmo_sim.py lab recovery ...`): `plan-<kind>` ist rein
    lesend (keine Dateiaenderung unter `run_dir`), `apply-<kind>` konsumiert
    GENAU die zuvor geschriebene Plandatei (Pflicht-`--plan-file`, R2-BIND-
    Fix) -- kein Hash-Echo."""
    before = {
        str(p.relative_to(run_dir)): p.stat().st_mtime_ns
        for p in run_dir.rglob("*") if p.is_file()
    }
    plan = _run_cli(data_dir, "plan-" + kind, *ids, *plan_context)
    assert plan.returncode == 0, f"plan-{kind} {plan_context}: rc={plan.returncode} stderr={plan.stderr!r}"
    after = {
        str(p.relative_to(run_dir)): p.stat().st_mtime_ns
        for p in run_dir.rglob("*") if p.is_file()
    }
    assert before == after, f"plan-{kind} hat run_dir veraendert (muss rein lesend bleiben): {before} != {after}"

    plan_path = data_dir / f"plan-{kind}-{'-'.join(apply_context) or 'none'}.json"
    plan_path.write_text(plan.stdout, encoding="utf-8")

    apply = _run_cli(
        data_dir, "apply-" + kind, *ids, *apply_context,
        "--plan-file", str(plan_path),
        "--operator-decision", "explicit-test-decision", "--reason", "SYNTHETIC cli-context roundtrip",
        "--evidence-ref", "SYNTHETIC-cli-context-case",
    )
    assert apply.returncode == expect_apply_rc, (
        f"apply-{kind} {apply_context}: erwartet rc={expect_apply_rc}, erhalten rc={apply.returncode} "
        f"stdout={apply.stdout!r} stderr={apply.stderr!r}"
    )
    return plan, apply


# ═══════════════════════════════ P3 ═══════════════════════════════════════


def test_cli_context_p3_plan_apply_without_community():
    """Normaler P3-Plan/Apply-Ablauf OHNE Gemeinschaftskontext ueber die
    echte CLI: rc=0, der persistierte Audit traegt `community_binding=None`."""
    with tempfile.TemporaryDirectory(prefix="CLI-CTX-P3-NOCOMM-") as td:
        data_dir = Path(td)
        run_dir = make_synthetic_run(data_dir)
        rid = make_p3_unknown_request(run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1, participant="alice")
        ids = ["--table-id", "table-1", "--section-id", "section-1", "--role", "gm_turn", "--turn-idx", "1", "--participant", "alice", "--request-id", rid]

        _, apply = _plan_then_apply(data_dir, run_dir, "p3", ids, plan_context=[], apply_context=[])
        audit = json.loads(apply.stdout)
        assert audit["status"] == "applied"
        assert audit["audit"]["community_binding"] is None


def test_cli_context_p3_plan_apply_with_community():
    """Normaler P3-Plan/Apply-Ablauf MIT identischer Gemeinschaftsbindung auf
    Plan UND Apply -- genau die Luecke, die der integrierte Seed schliesst
    (`plan-p3` bot vorher KEIN `--community`, GENERALREVIEW.md §3)."""
    with tempfile.TemporaryDirectory(prefix="CLI-CTX-P3-COMM-") as td:
        data_dir = Path(td)
        run_dir = make_synthetic_run(data_dir)
        rid = make_p3_unknown_request(run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1, participant="bob")
        ids = ["--table-id", "table-1", "--section-id", "section-1", "--role", "gm_turn", "--turn-idx", "1", "--participant", "bob", "--request-id", rid]
        community = ["--community", "SYNTHETIC-COMMUNITY-A"]

        _, apply = _plan_then_apply(data_dir, run_dir, "p3", ids, plan_context=community, apply_context=community)
        audit = json.loads(apply.stdout)
        assert audit["status"] == "applied"
        assert audit["audit"]["community_binding"] == "SYNTHETIC-COMMUNITY-A"


def test_cli_context_p3_apply_community_mismatch_rejected():
    """Core-Pruefung bleibt erhalten: ein OHNE Kontext erstellter Plan passt
    NICHT zu einem Apply MIT (abweichendem) Kontext -- kontrollierter
    Abbruch (rc=3, `RecoveryPreconditionChangedError`), kein stilles
    Durchwinken. Der Seed reicht Kontextargumente nur weiter, er entfernt
    keine bestehende Bindungspruefung."""
    with tempfile.TemporaryDirectory(prefix="CLI-CTX-P3-MISMATCH-") as td:
        data_dir = Path(td)
        run_dir = make_synthetic_run(data_dir)
        rid = make_p3_unknown_request(run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1, participant="carol")
        ids = ["--table-id", "table-1", "--section-id", "section-1", "--role", "gm_turn", "--turn-idx", "1", "--participant", "carol", "--request-id", rid]

        _plan_then_apply(
            data_dir, run_dir, "p3", ids,
            plan_context=[], apply_context=["--community", "SYNTHETIC-COMMUNITY-B"], expect_apply_rc=3,
        )


# ═══════════════════════════════ P5 ═══════════════════════════════════════


def test_cli_context_p5_plan_apply_without_community():
    """Normaler P5-Plan/Apply-Ablauf OHNE Gemeinschaftskontext/Generation --
    die bestehende Fixture liefert `generation=None` (kein Korrekturdatensatz
    hat bisher je eine Generation gesetzt bekommen), passend zum Default."""
    with tempfile.TemporaryDirectory(prefix="CLI-CTX-P5-NOCOMM-") as td:
        data_dir = Path(td)
        run_dir = make_synthetic_run(data_dir)
        p5 = make_p5_drift_hold(run_dir, persona_key="flo_p5_nocomm", char_id="CHR-P5-NOCOMM")
        ids = ["--repair-key", p5["repair_key"]]

        _, apply = _plan_then_apply(data_dir, run_dir, "p5", ids, plan_context=[], apply_context=[])
        result = json.loads(apply.stdout)
        assert result["status"] == "applied"
        assert result["grant"]["community_binding"] is None
        assert result["grant"]["generation_binding"] is None


def test_cli_context_p5_plan_apply_with_community_and_generation():
    """Normaler P5-Plan/Apply-Ablauf MIT Gemeinschaftskontext UND Generation.

    `plan_p5` bindet `generation_binding` an das tatsaechlich gespeicherte
    `generation`-Feld des Korrekturdatensatzes (Autoritaet, s.
    `recovery_ops.plan_p5`-Docstring) -- ein vom Operator behauptetes
    `--generation`, das NICHT zu diesem gespeicherten Feld passt, wird
    kontrolliert abgelehnt. Diese Fixture setzt deshalb VOR dem Plan-Aufruf
    bewusst `generation=1` im Korrekturdatensatz (exakt wie
    `review/reproduction/check_cli_roundtrip.py`s `--expect fixed`-
    Gruppenfall), damit `--generation 1` zur Fixture passt."""
    with tempfile.TemporaryDirectory(prefix="CLI-CTX-P5-COMM-") as td:
        data_dir = Path(td)
        run_dir = make_synthetic_run(data_dir)
        p5 = make_p5_drift_hold(run_dir, persona_key="flo_p5_comm", char_id="CHR-P5-COMM")
        record_path = run_dir / "save_corrections" / (p5["repair_key"] + ".json")
        record = json.loads(record_path.read_text(encoding="utf-8"))
        assert record.get("generation") is None, "Fixture-Vorbedingung: Korrekturdatensatz startet ohne Generation."
        record["generation"] = 1
        record_path.write_text(json.dumps(record), encoding="utf-8")

        ids = ["--repair-key", p5["repair_key"]]
        context = ["--community", "SYNTHETIC-COMMUNITY-P5", "--generation", "1"]

        _, apply = _plan_then_apply(data_dir, run_dir, "p5", ids, plan_context=context, apply_context=context)
        result = json.loads(apply.stdout)
        assert result["status"] == "applied"
        assert result["grant"]["community_binding"] == "SYNTHETIC-COMMUNITY-P5"
        assert result["grant"]["generation_binding"] == 1


def test_cli_context_p5_generation_mismatch_rejected():
    """`--generation` widerspricht dem tatsaechlich gespeicherten
    `generation`-Feld -> kontrollierte Ablehnung VOR jeder Wirkung
    (`plan-p5` selbst lehnt bereits ab, rc=3) -- keine stille Uebernahme
    eines unabhaengig behaupteten Bindungsarguments."""
    with tempfile.TemporaryDirectory(prefix="CLI-CTX-P5-GENMISMATCH-") as td:
        data_dir = Path(td)
        run_dir = make_synthetic_run(data_dir)
        p5 = make_p5_drift_hold(run_dir, persona_key="flo_p5_genmismatch", char_id="CHR-P5-GENMM")
        ids = ["--repair-key", p5["repair_key"]]

        plan = _run_cli(data_dir, "plan-p5", *ids, "--generation", "99")
        assert plan.returncode == 3, f"generation=99 gegen gespeichertes generation=None haette abgelehnt werden muessen: {plan.stdout!r} {plan.stderr!r}"


# ═══════════════════════════════ Robustheit ═════════════════════════════════


def test_cli_context_apply_without_plan_file_rejected_by_argparse():
    """`--plan-file` ist Pflicht (R2-BIND-Fix) -- ein Aufruf ohne wird schon
    von argparse abgelehnt (rc!=0), bevor `recovery_ops.apply_p3` ueberhaupt
    erreicht wird."""
    with tempfile.TemporaryDirectory(prefix="CLI-CTX-NOPLANFILE-") as td:
        data_dir = Path(td)
        run_dir = make_synthetic_run(data_dir)
        rid = make_p3_unknown_request(run_dir, table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1, participant="dana")
        proc = _run_cli(
            data_dir, "apply-p3", "--table-id", "table-1", "--section-id", "section-1", "--role", "gm_turn",
            "--turn-idx", "1", "--participant", "dana", "--request-id", rid,
            "--operator-decision", "x", "--reason", "y", "--evidence-ref", "z",
        )
        assert proc.returncode != 0, "apply-p3 ohne --plan-file haette (argparse) ablehnen muessen."


def main() -> int:
    tests = [v for k, v in list(globals().items()) if k.startswith("test_") and callable(v)]
    passed, failed, blocked = 0, 0, 0
    for t in sorted(tests, key=lambda f: f.__name__):
        try:
            t()
            print(f"OK      {t.__name__}")
            passed += 1
        except EnvironmentBlocked as e:
            blocked += 1
            print(f"BLOCKED {t.__name__}: {e}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL    {t.__name__}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR   {t.__name__}:")
            traceback.print_exc()
    print(f"\n{passed}/{len(tests)} bestanden, {failed} fehlgeschlagen, {blocked} BLOCKED_ENV.")
    return 0 if failed == 0 and blocked == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
