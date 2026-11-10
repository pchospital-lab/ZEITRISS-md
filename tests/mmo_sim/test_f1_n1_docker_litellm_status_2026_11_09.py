#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n1_docker_litellm_status_2026_11_09.py — Delta-Test
für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N1 WP1c (PF1.4).

Vorher klassifizierte `scripts/launcher.py:_docker_ok` JEDEN `docker ps`-
Fehlschlag pauschal als "Daemon läuft nicht nicht" — ein fehlendes
Compose-Plugin oder fehlende Docker-Gruppenrechte sahen identisch aus wie
ein gestoppter Daemon, obwohl die nächste Aktion für den Nutzer in jedem
Fall eine andere ist. `_litellm_ok` akzeptierte IRGENDEINEN Container mit
`name=litellm` im Namen — ein fremder Bausatz-Container (z.B.
`litellm-arxion`) ließ den benötigten ZEITRISS-Schritt fälschlich als
erledigt gelten.

Deckt:
  (A) `_docker_ok` unterscheidet 4 Fälle: Engine fehlt, Compose-Plugin
      fehlt, Permission (nicht in docker-Gruppe), sonstiger Daemon-Fehler.
  (B) `_litellm_ok`/`_expected_litellm_container_name` prüfen routegenau
      (`litellm-<project-slug>`), nicht pauschal "irgendein litellm".

Double-Grenze (A4, offen gelegt): `subprocess.run` ist vollständig
gedoubelt (kein echter Docker-Aufruf); `load_cfg`/`setup_module._docker_slug`
laufen echt gegen das reale `setup.json` dieses Repos (reiner Dateiread,
kein Docker/Netzwerk) — das Projekt heißt dort "ZEITRISS", der erwartete
Containername ist also `litellm-zeitriss`.

Pure Python, nur `assert`, echter Exitcode, kein Docker/Netzwerk."""
from __future__ import annotations

import importlib.util
import traceback
import types
import unittest.mock as mock
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_LAUNCHER_PY = _REPO_ROOT / "scripts" / "launcher.py"

_spec = importlib.util.spec_from_file_location(
    "f1_n1_docker_litellm_status_launcher_under_test", _LAUNCHER_PY,
)
launcher_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(launcher_mod)


def _fake_result(returncode=0, stdout="", stderr=""):
    return types.SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def test_docker_ok_engine_missing():
    with mock.patch.object(launcher_mod, "_cmd_available", return_value=False):
        ok, info = launcher_mod._docker_ok()
    assert ok is False
    assert "Engine fehlt" in info, info


def test_docker_ok_compose_plugin_missing():
    def _run(cmd, **kw):
        if cmd[:3] == ["docker", "compose", "version"]:
            return _fake_result(returncode=1, stderr="docker: 'compose' is not a docker command")
        raise AssertionError(f"unerwarteter Aufruf: {cmd}")

    with mock.patch.object(launcher_mod, "_cmd_available", return_value=True), \
         mock.patch.object(launcher_mod.subprocess, "run", side_effect=_run):
        ok, info = launcher_mod._docker_ok()
    assert ok is False
    assert "Compose-Plugin fehlt" in info, info


def test_docker_ok_permission_denied_reports_group_hint():
    def _run(cmd, **kw):
        if cmd[:3] == ["docker", "compose", "version"]:
            return _fake_result(returncode=0)
        if cmd[:2] == ["docker", "ps"]:
            return _fake_result(returncode=1, stderr="permission denied while trying to connect to the Docker daemon socket")
        raise AssertionError(f"unerwarteter Aufruf: {cmd}")

    with mock.patch.object(launcher_mod, "_cmd_available", return_value=True), \
         mock.patch.object(launcher_mod.subprocess, "run", side_effect=_run):
        ok, info = launcher_mod._docker_ok()
    assert ok is False
    assert "Gruppenrechte" in info or "docker-Gruppe" in info or "docker'-Gruppe" in info, info
    assert "Daemon läuft nicht" not in info, "Permission-Fall darf nicht als Daemon-aus-Fall gemeldet werden"


def test_docker_ok_other_ps_failure_is_daemon_down():
    def _run(cmd, **kw):
        if cmd[:3] == ["docker", "compose", "version"]:
            return _fake_result(returncode=0)
        if cmd[:2] == ["docker", "ps"]:
            return _fake_result(returncode=1, stderr="Cannot connect to the Docker daemon at unix:///var/run/docker.sock")
        raise AssertionError(f"unerwarteter Aufruf: {cmd}")

    with mock.patch.object(launcher_mod, "_cmd_available", return_value=True), \
         mock.patch.object(launcher_mod.subprocess, "run", side_effect=_run):
        ok, info = launcher_mod._docker_ok()
    assert ok is False
    assert "Daemon läuft nicht" in info, info


def test_docker_ok_all_green():
    def _run(cmd, **kw):
        return _fake_result(returncode=0)

    with mock.patch.object(launcher_mod, "_cmd_available", return_value=True), \
         mock.patch.object(launcher_mod.subprocess, "run", side_effect=_run):
        ok, info = launcher_mod._docker_ok()
    assert ok is True, info


def test_expected_litellm_container_name_matches_project_slug():
    name = launcher_mod._expected_litellm_container_name()
    assert name == "litellm-zeitriss", f"erwartet litellm-zeitriss (ZEITRISS-Projekt), war {name!r}"


def test_litellm_ok_accepts_matching_container():
    def _run(cmd, **kw):
        return _fake_result(stdout="litellm-zeitriss\n")

    with mock.patch.object(launcher_mod, "_cmd_available", return_value=True), \
         mock.patch.object(launcher_mod.subprocess, "run", side_effect=_run):
        ok, info = launcher_mod._litellm_ok()
    assert ok is True, info
    assert "litellm-zeitriss" in info, info


def test_litellm_ok_rejects_foreign_container_from_other_bausatz():
    """PF1.4: ein fremder Container (anderer Bausatz) darf NICHT als
    erledigt gelten, auch wenn sein Name 'litellm' enthält."""
    def _run(cmd, **kw):
        return _fake_result(stdout="litellm-arxion\n")

    with mock.patch.object(launcher_mod, "_cmd_available", return_value=True), \
         mock.patch.object(launcher_mod.subprocess, "run", side_effect=_run):
        ok, info = launcher_mod._litellm_ok()
    assert ok is False, f"ein fremder litellm-Container haette NICHT als erledigt gelten duerfen: {info}"
    assert "litellm-arxion" in info and "litellm-zeitriss" in info, info


def test_litellm_ok_no_container_at_all():
    def _run(cmd, **kw):
        return _fake_result(stdout="")

    with mock.patch.object(launcher_mod, "_cmd_available", return_value=True), \
         mock.patch.object(launcher_mod.subprocess, "run", side_effect=_run):
        ok, info = launcher_mod._litellm_ok()
    assert ok is False
    assert "kein litellm-Container aktiv" in info, info


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
