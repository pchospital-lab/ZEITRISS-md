#!/usr/bin/env python3
"""
tests/mmo_sim/run_all.py — portabler Gesamtrunner fuer alle neuen
mmo_sim-Regressionen (04 §"Portablen Gesamtrunner fuer die neuen Tests
bereitstellen").

Fuehrt jede `test_*.py`-Datei in diesem Verzeichnis als eigenen Subprozess
aus (echte Exitcodes, keine gegenseitige Zustandsverschmutzung zwischen
Testdateien) und fasst am Ende zusammen. Exitcode 0 nur, wenn ALLE Dateien
exit=0 liefern.

Aufruf: `python3 tests/mmo_sim/run_all.py`
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    test_files = sorted(p for p in HERE.glob("test_*.py"))
    results: list[tuple[str, int]] = []
    for f in test_files:
        proc = subprocess.run([sys.executable, str(f)], capture_output=True, text=True)
        print(f"=== {f.name} ===")
        print(proc.stdout.strip())
        if proc.returncode != 0:
            print(proc.stderr.strip(), file=sys.stderr)
        results.append((f.name, proc.returncode))
        print()

    print("=== Zusammenfassung ===")
    failed = [name for name, rc in results if rc != 0]
    for name, rc in results:
        status = "OK" if rc == 0 else f"FAIL(exit={rc})"
        print(f"{status:>16}  {name}")
    print(f"\n{len(results) - len(failed)}/{len(results)} Testdateien bestanden.")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
