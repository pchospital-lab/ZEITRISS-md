#!/usr/bin/env python3
"""
tests/mmo_sim/_f_process_evidence_fake_cli.py -- F-PROCESS-EVIDENCE
(ZR-N2-LIVEBUNDLE-FRESH-20261018-R1) Fixturehelfer, KEIN Testmodul selbst
(kein `test_`-Praefix, von `run_all.py` nicht aufgerufen).

Ein ECHTES, ausfuehrbares Python-Skript (eigene OS-PID/Prozessgruppe bei
jedem `subprocess`-Aufruf -- `mmo_sim.adapters.persona_claude_code._Real
ProcessRunner` startet es unveraendert wie die echte `claude`-Binary).
Ersetzt NUR die aeusserste Prozessgrenze (dieselbe Stelle, die `adapters.
fakes.FakeCLIProcess` in-process ersetzt) -- der Adaptercode selbst
(`PersonaClaudeCodeDriver.check_isolation`/`.decide()`) laeuft unveraendert
real darueber. KEIN `pgrep`/`pkill`: jeder Aufruf wird ausschliesslich ueber
seine EIGENE, vom Elternprozess (`subprocess.run`) zurueckgegebene PID
identifiziert und protokolliert -- niemals ueber einen Prozessnamen-Scan.

Steuerung ueber `HOME`-Kontrolldateien, NICHT ueber ein eigenes Env (der
echte Adapter (`_CHILD_ENV_ALLOWLIST`) reicht dem Kindprozess ABSICHTLICH
nur eine minimale Env-Allowlist durch -- Testparameter duerfen diese
Produktgrenze nicht umgehen, `HOME` ist Teil dieser Allowlist und bereits
Bestandteil JEDES echten Aufrufs). `cwd` wird vom Adapter NUR beim
eigentlichen Decide-Call gesetzt (`isolated_workdir`), NICHT bei --version/
--help -- `HOME` bleibt dagegen bei ALLEN drei Aufrufen identisch, deshalb
die gemeinsame Ablagebasis statt `cwd`:
  $HOME/dispatch_log.jsonl    IMMER angelegt: ein Record pro Aufruf
                              (--version/--help/decide), je mit EIGENER PID.
  $HOME/sleep_seconds.txt     Optional: vor der Hauptantwort real so lange
                              schlafen (misst einen echten, langsamen Prozess).
  $HOME/result_text.txt       Optional: Text fuer das JSON-`result`-Feld.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path


def _record(log_path: Path, kind: str, **extra) -> None:
    row = {"kind": kind, "pid": os.getpid(), "pgid": os.getpgrp(), "wall_ts": time.time(), "argv": sys.argv[1:]}
    row.update(extra)
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    base = Path(os.environ["HOME"])
    log_path = base / "dispatch_log.jsonl"
    argv = sys.argv[1:]
    if "--version" in argv:
        _record(log_path, "version")
        print("fake-claude 0.0.0-f-process-evidence")
        return 0
    if "--help" in argv:
        _record(log_path, "help")
        print(
            "Usage: fake-claude [options]\n"
            "  --permission-mode <mode>  restrict tool execution (plan|manual|acceptEdits|auto|bypassPermissions|dontAsk)\n"
            "  --safe-mode  skip hooks, MCP servers, settings, plugins\n"
        )
        return 0

    stdin_text = sys.stdin.read()
    _record(log_path, "decide_start", stdin_len=len(stdin_text))
    sleep_file = base / "sleep_seconds.txt"
    if sleep_file.is_file():
        time.sleep(float(sleep_file.read_text().strip()))
    result_file = base / "result_text.txt"
    result_text = result_file.read_text() if result_file.is_file() else "SYNTHETIC: Entscheidung getroffen."
    payload = {
        "type": "result", "subtype": "success", "is_error": False,
        "result": result_text, "usage": {"input_tokens": 5, "output_tokens": 5},
    }
    _record(log_path, "decide_end", result_len=len(result_text))
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
