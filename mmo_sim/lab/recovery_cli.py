#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mmo_sim/lab/recovery_cli.py — CLI-Dispatch fuer die Operator-Recovery-
Faehigkeiten R-P3/R-P5 (ZR-RECOVERY-OFFLINE-20261015-R1,
03_RECOVERY_VERTRAG.md). Aufgerufen NUR ueber `scripts/mmo_sim.py lab
recovery ...` (`mmo_sim.lab.cli.build_parser`/`main` registrieren den
Subparser, s. dort) -- kein eigener Prozesseinstieg, analog zu `lab
start|resume|status|stop|attach`.

`inspect`/`plan-p3`/`plan-p5` sind REIN LESEND. `apply-p3`/`apply-p5` sind
bewusste, einzeln aufgerufene Operatoraktionen -- NUR auf ausdruecklich als
synthetischer Testroot markierten `run_dir`s erlaubt (s. `core.recovery_ops.
_require_synthetic_root`); ein Aufruf auf einem echten LA1/P3/P5-Root
schlaegt kontrolliert fehl (`RecoveryUnsafeRootError`).

R2-BIND-Fix (GENERALREVIEW.md §3, "Die CLI uebergibt ueberhaupt keinen
freigegebenen Plan/Erwartungshash an Apply"): `apply-p3`/`apply-p5`
verlangen jetzt ein PFLICHT-`--plan-file`, das genau die JSON-Ausgabe eines
vorherigen `plan-p3`/`plan-p5`-Aufrufs enthaelt (derselbe Operator liest
diese Datei VOR dem Apply und entscheidet bewusst). Der Inhalt wird
unveraendert als `plan=` an `recovery_ops.apply_p3`/`apply_p5` uebergeben --
deren bestehende Precondition-Pruefung (`audit_key`/`pre_state_sha256`/
`run_binding`/`community_binding`/`generation_binding`) vergleicht ihn
gegen den FRISCH von Platte gelesenen Zustand. Ein blosses Echo des eben
neu berechneten Hashes (R1-Verhalten) ist KEIN Entscheidungsabgleich -- die
Datei muss aus einem ECHTEN vorherigen `plan-*`-Aufruf stammen."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ..core import recovery_ops


class _PlanFileError(RuntimeError):
    """`--plan-file` fehlt, ist nicht lesbar, oder kein JSON-Objekt --
    kontrollierte Ablehnung VOR jedem `recovery_ops.apply_*`-Aufruf (fail-
    closed, analog `recovery_ops.RecoveryError`)."""


def _load_plan_file(path_str: str) -> dict:
    path = Path(path_str)
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise _PlanFileError(f"--plan-file {path_str!r} nicht lesbar ({exc}).") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise _PlanFileError(f"--plan-file {path_str!r} ist kein gueltiges JSON ({exc}).") from exc
    if not isinstance(data, dict):
        raise _PlanFileError(f"--plan-file {path_str!r}: Inhalt ist kein JSON-Objekt.")
    return data


def _add_data_dir_arg(sub: argparse.ArgumentParser) -> None:
    sub.add_argument("--data-dir", required=True, help="dasselbe Datenverzeichnis wie beim TUI-/Lab-Aufruf")


def _add_decision_args(sub: argparse.ArgumentParser) -> None:
    sub.add_argument("--operator-decision", required=True, help="explizite Entscheidung des Betreibers (Pflicht, nichtleer)")
    sub.add_argument("--reason", required=True, help="Begruendung (Pflicht, nichtleer)")
    sub.add_argument("--evidence-ref", required=True, help="Belegreferenz, z.B. Pfad/Ticket-ID (Pflicht, nichtleer)")
    sub.add_argument("--community", default=None, help="optionale Communitybindung (Audittext, keine Rechtequelle)")


def _add_p3_identity_args(sub: argparse.ArgumentParser) -> None:
    sub.add_argument("--table-id", default=None)
    sub.add_argument("--section-id", default=None)
    sub.add_argument("--role", required=True)
    sub.add_argument("--turn-idx", type=int, default=None)
    sub.add_argument("--participant", default=None)
    sub.add_argument("--request-id", required=True)
    sub.add_argument("--generation", type=int, default=None, help="optionale Generationbindung (Audittext)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mmo_sim.py lab recovery", description="Operator-Recovery R-P3/R-P5")
    sub = parser.add_subparsers(dest="recovery_command", required=True)

    p_inspect = sub.add_parser("inspect", help="rein lesend: P3-/P5-Kandidaten + bestehende Audits/Grants")
    _add_data_dir_arg(p_inspect)

    p_plan_p3 = sub.add_parser("plan-p3", help="rein lesend: Plan fuer R-P3 (UNKNOWN_OUTCOME_PROTECTED)")
    _add_data_dir_arg(p_plan_p3)
    _add_p3_identity_args(p_plan_p3)
    p_plan_p3.add_argument("--community", default=None, help="Gemeinschaftskontext für denselben Plan-/Apply-Fall")

    p_apply_p3 = sub.add_parser("apply-p3", help="Apply R-P3 -- additiver Auditdatensatz, NUR auf synthetischen Testroots")
    _add_data_dir_arg(p_apply_p3)
    _add_p3_identity_args(p_apply_p3)
    _add_decision_args(p_apply_p3)
    p_apply_p3.add_argument(
        "--plan-file", required=True,
        help="Pfad zur JSON-Ausgabe eines vorherigen 'plan-p3'-Aufrufs (Pflicht -- bindet Apply an einen "
        "tatsaechlich zuvor freigegebenen Plan, kein blosses Hash-Echo)",
    )

    p_plan_p5 = sub.add_parser("plan-p5", help="rein lesend: Plan fuer R-P5 (gebundene Einmalallowance)")
    _add_data_dir_arg(p_plan_p5)
    p_plan_p5.add_argument("--repair-key", required=True)
    p_plan_p5.add_argument("--community", default=None, help="Gemeinschaftskontext für denselben Plan-/Apply-Fall")
    p_plan_p5.add_argument("--generation", type=int, default=None, help="Generation für denselben Plan-/Apply-Fall")

    p_apply_p5 = sub.add_parser("apply-p5", help="Apply R-P5 -- gebundene Einmalautorisierung, NUR auf synthetischen Testroots")
    _add_data_dir_arg(p_apply_p5)
    p_apply_p5.add_argument("--repair-key", required=True)
    _add_decision_args(p_apply_p5)
    p_apply_p5.add_argument("--generation", type=int, default=None, help="Generation des freigegebenen Plans")
    p_apply_p5.add_argument(
        "--plan-file", required=True,
        help="Pfad zur JSON-Ausgabe eines vorherigen 'plan-p5'-Aufrufs (Pflicht -- bindet Apply an einen "
        "tatsaechlich zuvor freigegebenen Plan, kein blosses Hash-Echo)",
    )

    # R2 (PR #3317-Nachzug 2026-11-23, RECOVERY_REVIEW.md R2): echter-Root-
    # faehiger Orphan-Weg -- ANDERS als p3/p5 NICHT auf synthetische
    # Testroots beschraenkt (kein `_require_synthetic_root`). Der bestellte
    # Bedienweg ist die TUI; dies ist nur die Ergaenzung fuer einen
    # Operator-CLI-Zugriff auf dieselbe Anwendungsschicht.
    p_plan_orphan = sub.add_parser(
        "plan-orphan", help="rein lesend/kostenfrei: alle echten offenen Orphan-Roots dieses Runs klassifizieren",
    )
    _add_data_dir_arg(p_plan_orphan)

    p_apply_orphan = sub.add_parser(
        "apply-orphan",
        help="Apply R2 -- genau einen gebundenen Folgeversuch fuer einen echten UNKNOWN-Orphan autorisieren "
        "(KEIN Modellcall; auch auf echten Roots erlaubt)",
    )
    _add_data_dir_arg(p_apply_orphan)
    p_apply_orphan.add_argument("--request-id", required=True, help="request_id des zu disponierenden Orphan-Roots")
    p_apply_orphan.add_argument("--reason", required=True, help="Begruendung der Dispositon (Pflicht, nichtleer)")
    p_apply_orphan.add_argument(
        "--plan-file", required=True,
        help="Pfad zur JSON-Ausgabe eines vorherigen 'plan-orphan'-Aufrufs (Pflicht -- bindet Apply an einen "
        "tatsaechlich zuvor freigegebenen Plan, kein blosses Hash-Echo)",
    )

    return parser


def _run_dir(args) -> Path:
    return Path(args.data_dir) / "run"


def _print(payload) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str))


def _cmd_inspect(args) -> int:
    run_dir = _run_dir(args)
    _print({
        "p3_candidates": recovery_ops.inspect_p3_candidates(run_dir),
        "p3_audits": recovery_ops.list_p3_audits(run_dir),
        "p5_candidates": recovery_ops.inspect_p5_candidates(run_dir),
        "p5_grants": recovery_ops.list_p5_grants(run_dir),
        # R2: dieselbe kostenfreie Uebersicht wie `plan-orphan`, zusaetzlich
        # hier in der gemeinsamen Inspect-Ansicht (rein lesend).
        "orphan_recovery": recovery_ops.plan_orphan_recovery(run_dir).get("orphans", []),
    })
    return 0


def _cmd_plan_p3(args) -> int:
    plan = recovery_ops.plan_p3(
        _run_dir(args), table_id=args.table_id, section_id=args.section_id, role=args.role,
        turn_idx=args.turn_idx, participant=args.participant, request_id=args.request_id,
        community_binding=args.community, generation_binding=args.generation,
    )
    _print(plan)
    return 0


def _cmd_apply_p3(args) -> int:
    plan = _load_plan_file(args.plan_file)
    result = recovery_ops.apply_p3(
        _run_dir(args), table_id=args.table_id, section_id=args.section_id, role=args.role,
        turn_idx=args.turn_idx, participant=args.participant, request_id=args.request_id,
        operator_decision=args.operator_decision, reason=args.reason, evidence_ref=args.evidence_ref,
        community_binding=args.community, generation_binding=args.generation, plan=plan,
    )
    _print(result)
    return 0


def _cmd_plan_p5(args) -> int:
    plan = recovery_ops.plan_p5(
        _run_dir(args), repair_key=args.repair_key,
        community_binding=args.community, generation_binding=args.generation,
    )
    _print(plan)
    return 0


def _cmd_apply_p5(args) -> int:
    plan = _load_plan_file(args.plan_file)
    result = recovery_ops.apply_p5(
        _run_dir(args), repair_key=args.repair_key, operator_decision=args.operator_decision,
        reason=args.reason, evidence_ref=args.evidence_ref, community_binding=args.community,
        generation_binding=args.generation, plan=plan,
    )
    _print(result)
    return 0


def _cmd_plan_orphan(args) -> int:
    _print(recovery_ops.plan_orphan_recovery(_run_dir(args)))
    return 0


def _extract_orphan_plan_item(plan_file_data: dict, request_id: str) -> dict:
    """`--plan-file` ist dieselbe volle Ausgabe wie `plan-orphan` (ein Dict
    mit einem `orphans`-Schluessel) -- extrahiert daraus genau den Treffer
    fuer `request_id`, den `recovery_ops.apply_orphan_recovery` als `plan=`
    erwartet. Fehlt `orphans` (z.B. ein bereits per Hand auf den einzelnen
    Treffer reduziertes File), wird der Inhalt selbst als der Treffer
    behandelt."""
    if "orphans" not in plan_file_data:
        return plan_file_data
    for item in plan_file_data.get("orphans") or []:
        if isinstance(item, dict) and item.get("request_id") == request_id:
            return item
    raise _PlanFileError(
        f"--plan-file enthaelt keinen 'orphans'-Treffer fuer request_id={request_id!r}."
    )


def _cmd_apply_orphan(args) -> int:
    plan_file_data = _load_plan_file(args.plan_file)
    plan = _extract_orphan_plan_item(plan_file_data, args.request_id)
    result = recovery_ops.apply_orphan_recovery(
        _run_dir(args), request_id=args.request_id, reason=args.reason, plan=plan,
    )
    _print(result)
    return 0


def dispatch(args) -> int:
    """Aufgerufen von `mmo_sim.lab.cli.main` fuer `args.command == 'recovery'`
    -- `args.recovery_command` waehlt den konkreten Unterbefehl. Jeder
    `recovery_ops.RecoveryError` wird HIER kontrolliert als Fehlertext auf
    stderr gemeldet (Exit-Code 3, analog `SingletonViolationError`/
    `LabRunnerRestartError` in `lab/cli.py`) -- NIE ein ungefangener
    Traceback fuer eine fachlich erwartbare Ablehnung."""
    handlers = {
        "inspect": _cmd_inspect, "plan-p3": _cmd_plan_p3, "apply-p3": _cmd_apply_p3,
        "plan-p5": _cmd_plan_p5, "apply-p5": _cmd_apply_p5,
        "plan-orphan": _cmd_plan_orphan, "apply-orphan": _cmd_apply_orphan,
    }
    handler = handlers.get(args.recovery_command)
    if handler is None:
        print(f"lab recovery: unbekanntes Unterkommando {args.recovery_command!r}", file=sys.stderr)
        return 2
    try:
        return handler(args)
    except (recovery_ops.RecoveryError, _PlanFileError) as exc:
        print(f"lab recovery {args.recovery_command}: {exc}", file=sys.stderr)
        return 3


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return dispatch(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
