#!/usr/bin/env python3
"""Lint: Verifiziert Debrief-Trace-Ausgaben (Markt, Foreshadow, Offline, Flags)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import textwrap
from pathlib import Path

try:
    from scripts.lib_repo import repo_root, get_logger
except ImportError:  # pragma: no cover - fallback
    from pathlib import Path as _Path
    import sys as _sys

    _root = _Path(__file__).resolve().parents[1]
    _sys.path.insert(0, str(_root))
    from scripts.lib_repo import repo_root, get_logger  # type: ignore

log = get_logger("lint_debrief_trace")

NODE_SCRIPT = textwrap.dedent(
    r"""
    const rt = require('./runtime.js');
    const { version: ZR_VERSION = '4.2.3' } = require('./package.json');
    const { state, log_market_purchase, ForeshadowHint, offline_audit, debrief } = rt;

    const captured = [];
    const originalLog = console.log;
    console.log = (...args) => { captured.push(args.map((entry) => String(entry)).join(' ')); };

    state.location = 'HQ';
    state.phase = 'core';
    state.campaign = {
      episode: 3,
      mission: 5,
      mode: 'preserve',
      paradoxon_index: 2,
      missions_since_px: 1,
      objective: 'QA Mission'
    };
    state.character = {
      id: 'qa-agentin',
      lvl: 4,
      rank: 'Operator I',
      stress: 0,
      psi_heat: 0,
      cooldowns: {},
      attributes: { SYS_max: 2, SYS_used: 2 }
    };
    state.economy = { credits: 1500 };

    log_market_purchase('Null-Grav-Tether', 450, {
      timestamp: '2025-06-13T11:00:00.000Z',
      px_clause: 'Px -1',
      note: 'QA Einkauf'
    });
    ForeshadowHint('Boss Gate Szenario', 'Boss');

    offline_audit('jammer', {
      device: 'comlink',
      jammed: true,
      range_m: 1500,
      relays: 0,
      scene_index: 3,
      scene_total: 12,
      episode: 3,
      mission: 5
    });

    state.logs.flags.runtime_version = ZR_VERSION;
    state.logs.flags.compliance_shown_today = true;
    state.logs.flags.chronopolis_warn_seen = true;
    state.logs.flags.offline_help_count = 3;
    state.logs.flags.offline_help_last = '2025-06-13T12:00:00.000Z';

    const output = debrief({
      temp: 2,
      cu_reward: 450,
      stabilized: true,
      level_before: 3,
      level_after: 4
    });

    console.log = originalLog;
    originalLog(JSON.stringify({ debrief: output, captured }));
    """
)


class LintError(RuntimeError):
    """Custom lint error for control flow."""


def run_node(root: Path) -> dict[str, object]:
    """Execute the Node helper and return the parsed payload."""
    proc = subprocess.run(
        ["node", "-e", NODE_SCRIPT],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        log.error("Node-Lauf fehlgeschlagen (code %s)", proc.returncode)
        for line in proc.stderr.splitlines():
            log.error("stderr: %s", line)
        raise LintError("Node-Script nicht erfolgreich")

    stdout = proc.stdout.strip()
    if not stdout:
        raise LintError("Node-Script lieferte keine Ausgabe")

    try:
        payload = json.loads(stdout.splitlines()[-1])
    except json.JSONDecodeError as exc:
        log.error("JSON-Parsing fehlgeschlagen: %s", exc)
        raise LintError("Node-Script gab kein valides JSON zurück") from exc

    if not isinstance(payload, dict):
        raise LintError("Node-Payload hat unerwartetes Format")
    return payload


def require(pattern: str, text: str, message: str, failures: list[str]) -> None:
    """Check ``pattern`` against ``text`` and collect failures."""
    import re

    if re.search(pattern, text, re.S):
        log.info("[ OK ] %s", message)
    else:
        log.error("[FAIL] %s", message)
        failures.append(message)


def lint(root: Path) -> int:
    payload = run_node(root)
    package = json.loads((root / "package.json").read_text(encoding="utf-8"))
    runtime_version = package.get("version", "4.2.3")
    debrief_text = str(payload.get("debrief", ""))
    if not debrief_text:
        log.error("Debrief-Text fehlt in der Node-Antwort")
        return 1

    failures: list[str] = []
    require(r"Chronopolis-Trace \(\d+×\): .*Null-Grav-Tether.*450 CU", debrief_text, "Chronopolis-Trace nennt Einkauf & Kosten", failures)
    require(r"Chronopolis-Trace \(\d+×\): .*2025-06-13T11:00:00.000Z", debrief_text, "Chronopolis-Trace enthält Timestamp", failures)
    require(r"Foreshadow-Log \(\d+×\): .*Boss Gate", debrief_text, "Foreshadow-Log referenziert Mission 5 Hinweis", failures)
    require(r"Offline-Protokoll \(\d+×\): .*jammer.*Jammer aktiv.*Reichweite 1500m", debrief_text, "Offline-Protokoll meldet Jammer-Trace", failures)
    require(
        rf"Runtime-Flags: .*Runtime {re.escape(runtime_version)}",
        debrief_text,
        "Runtime-Flags führen Runtime-Version",
        failures,
    )
    require(r"Runtime-Flags: .*Compliance gezeigt", debrief_text, "Runtime-Flags zeigen Compliance-Status", failures)
    require(r"Runtime-Flags: .*Chronopolis-Warnung quittiert", debrief_text, "Runtime-Flags spiegeln Chronopolis-Warnung", failures)
    require(r"Runtime-Flags: .*Offline-Hilfe 3×", debrief_text, "Runtime-Flags zählen Offline-Hilfe", failures)
    require(r"Runtime-Flags: .*2025-06-13T12:00:00.000Z", debrief_text, "Runtime-Flags enthalten letzten Offline-Zeitstempel", failures)

    if failures:
        log.error("Debrief-Trace-Lint fehlgeschlagen (%s Checks)", len(failures))
        return 1

    log.info("Debrief-Trace-Lint abgeschlossen")
    return 0


def main() -> int:
    root = repo_root(Path(__file__))
    try:
        return lint(root)
    except LintError as exc:
        log.error(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
