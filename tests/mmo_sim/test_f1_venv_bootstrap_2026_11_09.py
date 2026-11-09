#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_venv_bootstrap_2026_11_09.py — Delta-Test für
`scripts/venv_bootstrap.py` (F1, 03_F1_AUFTRAG.md §F1-1: "normaler Nutzer
braucht keinen Git-Checkout und keine manuell aktivierte Dev-venv").

Deckt: (1) Idempotenz — ein zweiter Lauf mit unveränderten
`requirements-ci.txt`-Pins installiert NICHT erneut; geänderte Pins lösen
dagegen genau einen Reinstall aus. (2) `already_in_venv()` kurzschliesst
ohne `os.execv`. (3) Root-Guard bricht VOR jeder venv-Erzeugung ab.

Double-Grenze (A4, offen gelegt): `subprocess.run` wird NUR für den
`pip install`-Netzwerkruf abgefangen und als Erfolg simuliert — dieser Test
beweist also NICHT, dass echte PyPI-Pakete installierbar sind (das hat ein
realer End-to-End-Lauf gegen eine entpackte Kopie belegt, s. Report), sondern
NUR die Entscheidungslogik (wann (re-)installiert wird). Die echte
`python3 -m venv`-Erzeugung läuft UNGEPATCHT (stdlib-lokal, kein Netzwerk).
`os.execv` wird in jedem Teiltest abgefangen (es würde sonst den Testprozess
ersetzen) und als `SystemExit(0)` simuliert.

Alle Tests, die den ERZEUGUNGS-/Install-/Root-Guard-/Fehler-Pfad prüfen,
patchen zusätzlich `_required_deps_available` auf `False` — ohne das würde
das "vorhandene gültige Umgebung wiederverwenden"-Gate (F1,
scripts/venv_bootstrap.py) auf einer Maschine mit bereits installiertem
`jsonschema`/`referencing` sofort No-Op greifen und diese Erzeugungs-Pfade
nie erreichen. Simuliert damit gezielt den blanken Download ohne
vorinstallierte Pakete. Der `already_in_venv()`-Kurzschluss-Test bleibt
unverändert (dieses Gate greift VOR dem Deps-Check ohnehin).

Pure Python, nur `assert`, echter Exitcode, temporäre Verzeichnisse."""
from __future__ import annotations

import importlib.util
import os
import shutil
import sys
import tempfile
import traceback
import unittest.mock as mock
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]

_spec = importlib.util.spec_from_file_location(
    "f1_venv_bootstrap_under_test", _REPO_ROOT / "scripts" / "venv_bootstrap.py",
)
venv_bootstrap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(venv_bootstrap)


def _patched_run_factory(calls: list):
    real_run = venv_bootstrap.subprocess.run

    def _patched(cmd, *a, **kw):
        if len(cmd) >= 3 and cmd[1] == "-m" and cmd[2] == "pip":
            calls.append(list(cmd))

            class _Result:
                returncode = 0
                stdout = ""
                stderr = ""

            return _Result()
        return real_run(cmd, *a, **kw)

    return _patched


def test_create_then_reuse_then_reinstall_on_pin_change():
    tmp = Path(tempfile.mkdtemp(prefix="f1-venv-bootstrap-"))
    real_run = venv_bootstrap.subprocess.run
    real_execv = venv_bootstrap.os.execv
    pip_calls: list = []
    execv_calls: list = []

    def _fake_execv(path, argv):
        execv_calls.append((path, argv))
        raise SystemExit(0)

    try:
        (tmp / "requirements-ci.txt").write_text("jsonschema==4.26.0\n", encoding="utf-8")
        venv_bootstrap.subprocess.run = _patched_run_factory(pip_calls)
        venv_bootstrap.os.execv = _fake_execv

        with mock.patch.object(venv_bootstrap, "_required_deps_available", return_value=False):
            # Lauf 1: venv fehlt noch -> echte (netzwerkfreie) Erzeugung + genau
            # ein simulierter pip-install-Aufruf, dann execv.
            try:
                venv_bootstrap.ensure_running_in_project_venv(tmp)
            except SystemExit:
                pass
            venv_python = venv_bootstrap._venv_python(venv_bootstrap.venv_dir(tmp))
            assert venv_python.exists(), f"venv-Interpreter fehlt: {venv_python}"
            assert len(pip_calls) == 1, f"genau EIN pip-install-Aufruf erwartet, war {len(pip_calls)}"
            assert len(execv_calls) == 1, "os.execv wurde nicht (oder mehrfach) aufgerufen"
            marker = venv_bootstrap.venv_dir(tmp) / venv_bootstrap._SENTINEL_NAME
            assert marker.is_file(), "Sentinel-Datei fehlt nach Erstinstall"
            first_hash = marker.read_text(encoding="utf-8").strip()
            assert first_hash, "Sentinel-Datei ist leer"

            # Lauf 2: UNVERÄNDERTE Pins -> KEIN erneuter pip-install-Aufruf
            # (03_F1_AUFTRAG.md §F1-1: "ein gewöhnlicher späterer Start
            # installiert nicht alles erneut"), aber weiterhin ein execv-Wechsel.
            try:
                venv_bootstrap.ensure_running_in_project_venv(tmp)
            except SystemExit:
                pass
            assert len(pip_calls) == 1, f"zweiter Lauf haette NICHT neu installieren duerfen: {len(pip_calls)}"
            assert len(execv_calls) == 2, "zweiter Lauf haette weiterhin in die venv wechseln muessen"

            # Lauf 3: GEÄNDERTE Pins -> löst genau einen weiteren Reinstall aus,
            # Sentinel-Hash ändert sich entsprechend.
            (tmp / "requirements-ci.txt").write_text(
                "jsonschema==4.26.0\nreferencing==0.37.0\n", encoding="utf-8",
            )
            try:
                venv_bootstrap.ensure_running_in_project_venv(tmp)
            except SystemExit:
                pass
            assert len(pip_calls) == 2, f"geaenderte Pins haetten einen zweiten Install ausloesen muessen: {len(pip_calls)}"
            second_hash = marker.read_text(encoding="utf-8").strip()
            assert second_hash != first_hash, "Sentinel-Hash haette sich nach Pin-Aenderung aendern muessen"
    finally:
        venv_bootstrap.subprocess.run = real_run
        venv_bootstrap.os.execv = real_execv
        shutil.rmtree(tmp, ignore_errors=True)


def test_already_in_venv_short_circuits_without_execv():
    tmp = Path(tempfile.mkdtemp(prefix="f1-venv-bootstrap-already-"))
    real_execv = venv_bootstrap.os.execv
    called = {"execv": False}

    def _fake_execv(*a, **kw):
        called["execv"] = True

    try:
        venv_dir = venv_bootstrap.venv_dir(tmp)
        venv_dir.mkdir(parents=True)
        venv_bootstrap.os.execv = _fake_execv
        with mock.patch.object(sys, "prefix", str(venv_dir)):
            venv_bootstrap.ensure_running_in_project_venv(tmp)
        assert not called["execv"], "already_in_venv() haette os.execv NICHT aufrufen duerfen (No-Op erwartet)"
        assert not (venv_dir / venv_bootstrap._SENTINEL_NAME).exists(), \
            "No-Op-Pfad haette keine Sentinel-Datei anlegen duerfen"
    finally:
        venv_bootstrap.os.execv = real_execv
        shutil.rmtree(tmp, ignore_errors=True)


def test_venv_creation_failure_is_clear_and_fails_closed():
    """A4 (Laufzeit/Abhaengigkeiten-Check): bricht `python3 -m venv` ab
    (z.B. fehlendes `python3-venv`-Paket auf einer Mint-Minimalinstallation,
    hier als Double simuliert), muss der Prozess mit einer klaren Meldung
    und Exit-Code 1 abbrechen -- KEIN stiller Fallback, KEINE als 'fertig'
    markierte halbe venv (keine Sentinel-Datei)."""
    tmp = Path(tempfile.mkdtemp(prefix="f1-venv-bootstrap-create-fail-"))
    real_run = venv_bootstrap.subprocess.run

    def _failing_run(cmd, *a, **kw):
        if len(cmd) >= 2 and cmd[1] == "-m" and len(cmd) >= 3 and cmd[2] == "venv":
            raise venv_bootstrap.subprocess.CalledProcessError(
                1, cmd, output="", stderr="ensurepip is not available -- python3-venv fehlt\n",
            )
        return real_run(cmd, *a, **kw)

    try:
        (tmp / "requirements-ci.txt").write_text("jsonschema==4.26.0\n", encoding="utf-8")
        venv_bootstrap.subprocess.run = _failing_run
        raised = False
        with mock.patch.object(venv_bootstrap, "_required_deps_available", return_value=False):
            try:
                venv_bootstrap.ensure_running_in_project_venv(tmp)
            except SystemExit as exc:
                raised = True
                assert exc.code == 1, f"Exit-Code sollte 1 sein, war {exc.code!r}"
        assert raised, "fehlgeschlagene venv-Erzeugung haette mit SystemExit(1) abbrechen muessen"
        assert not (tmp / ".venv" / venv_bootstrap._SENTINEL_NAME).exists(), \
            "fehlgeschlagene Erzeugung haette KEINE Sentinel-Datei (= 'fertig installiert') hinterlassen duerfen"
    finally:
        venv_bootstrap.subprocess.run = real_run
        shutil.rmtree(tmp, ignore_errors=True)


def test_root_guard_blocks_before_any_venv_creation():
    tmp = Path(tempfile.mkdtemp(prefix="f1-venv-bootstrap-root-"))
    had_geteuid = hasattr(os, "geteuid")
    real_geteuid = os.geteuid if had_geteuid else None
    try:
        os.geteuid = lambda: 0  # Double: root-UID simulieren, kein echter UID-Wechsel
        raised = False
        with mock.patch.object(venv_bootstrap, "_required_deps_available", return_value=False):
            try:
                venv_bootstrap.ensure_running_in_project_venv(tmp)
            except SystemExit as exc:
                raised = True
                assert exc.code == 1, f"root-Abbruch sollte Exit-Code 1 liefern, war {exc.code!r}"
        assert raised, "ein Lauf mit euid=0 haette mit SystemExit(1) abbrechen muessen"
        assert not (tmp / ".venv").exists(), "root-Guard haette VOR jeder venv-Erzeugung greifen muessen"
    finally:
        if had_geteuid:
            os.geteuid = real_geteuid
        else:
            del os.geteuid
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR {t.__name__}:")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} Tests bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
