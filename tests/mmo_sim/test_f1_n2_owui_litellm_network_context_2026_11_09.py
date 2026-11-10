#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n2_owui_litellm_network_context_2026_11_09.py —
Delta-Test für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N2 WP-N2-1b (P1b, "der
harte Punkt") — F1-N2-Nachzug nach realem Erreichbarkeits-Beweis.

Vorher setzte `scripts/setup.py:_ensure_owui_litellm_connection` die
OWUI->LiteLLM-Connection-URL hart auf `http://127.0.0.1:<port>/v1`. Aus einem
gebridgten OWUI-Container heraus ist `127.0.0.1` der Container selbst, NICHT
der Host. Der erste N2-Fix (`host.docker.internal` + `--add-host`) wurde in
einem isolierten Docker-Probelauf (2026-11-09) als auf nativer Linux-Engine
UNERREICHBAR belegt: LiteLLM wird per `docker-compose.litellm.yml` BEWUSST
loopback-only (`127.0.0.1:<port>:<port>`) published, die DNAT-Bindung matcht
nur `127.0.0.1` des Hosts, nicht die Bridge-Gateway-IP der Pakete aus dem
Container. Der kleinste funktionierende Anschluss, der die loopback-only-
Sicherheitsentscheidung NICHT aufweicht und KEINEN Port nach außen öffnet,
ist das gemeinsame Docker-Netz: OWUI wird an das Netz des LiteLLM-Containers
gehängt und erreicht ihn über den Container-NAMEN auf dem internen Port.

Deckt:
  (A) `setup.py:_owui_litellm_target_host(project)` wählt den LiteLLM-
      Container-Namen (`litellm-<slug>`), wenn der `open-webui`-Container
      gebridgt läuft (NetworkMode != host), `127.0.0.1` bei NetworkMode=host
      und bewahrt den `127.0.0.1`-Default, wenn der Netzwerkkontext nicht
      ermittelbar ist (bewusste Fremdkonfig NICHT überschreiben). Reiner
      Getter OHNE Seiteneffekt.
  (B) `setup.py:_ensure_owui_on_litellm_network(project)` hängt OWUI
      idempotent an das Netz des LiteLLM-Containers (success + "already
      exists" => True; Container/Netz nicht ermittelbar => False).
  (C) `_ensure_owui_litellm_connection` bindet OWUI bei gebridgtem Kontext
      ans Netz, baut `target_url` aus dem Container-Namen, und lehnt sichtbar
      ab (ok=False), wenn die Netz-Anbindung nicht herstellbar ist -- KEIN
      stiller Erfolg mit falscher Loopback-URL.
  (D) `launcher.py:_start_openwebui()` behält `--add-host
      host.docker.internal:host-gateway` (harmlos, Docker-Desktop-kompatibel;
      der eigentliche Linux-Anschluss läuft über das gemeinsame Netz).

Double-Grenze (A4, offen gelegt): `subprocess.run` ist vollständig gedoubelt
(kein echter Docker-/Netzwerk-Aufruf); in (C) sind `_owui_container_network_
mode`, `_ensure_owui_on_litellm_network` und `_owui_litellm_target_host`
gemockt bzw. `urllib.request.urlopen` gedoubelt. Der echte Erreichbarkeits-
beweis aus dem OWUI-Container läuft über Mains reale Nutzerreise (N2-4), nicht
hier.

Pure Python, nur `assert`, echter Exitcode, kein Docker/Netzwerk."""
from __future__ import annotations

import importlib.util
import traceback
import types
import unittest.mock as mock
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_SETUP_PY = _REPO_ROOT / "scripts" / "setup.py"
_LAUNCHER_PY = _REPO_ROOT / "scripts" / "launcher.py"

_setup_spec = importlib.util.spec_from_file_location(
    "f1_n2_owui_litellm_network_context_setup_under_test", _SETUP_PY,
)
setup_mod = importlib.util.module_from_spec(_setup_spec)
_setup_spec.loader.exec_module(setup_mod)

_launcher_spec = importlib.util.spec_from_file_location(
    "f1_n2_owui_litellm_network_context_launcher_under_test", _LAUNCHER_PY,
)
launcher_mod = importlib.util.module_from_spec(_launcher_spec)
_launcher_spec.loader.exec_module(launcher_mod)

_EXPECTED = f"litellm-{setup_mod._docker_slug('proj')}"


def _fake_result(returncode=0, stdout="", stderr=""):
    return types.SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def test_target_host_is_litellm_container_name_for_bridged_container():
    """Gebridgt (NetworkMode != host) -> LiteLLM-Container-NAME, nicht
    127.0.0.1 und nicht host.docker.internal (empirisch unerreichbar)."""
    def _run(cmd, **kw):
        assert cmd[:2] == ["docker", "inspect"], cmd
        return _fake_result(stdout="bridge\n")

    with mock.patch.object(setup_mod.subprocess, "run", side_effect=_run):
        host = setup_mod._owui_litellm_target_host("proj")
    assert host == _EXPECTED, host
    assert "host.docker.internal" not in host, host


def test_target_host_stays_loopback_for_host_network_mode():
    """Bewusste Fremdkonfig (OWUI laeuft explizit mit --network=host) darf
    NICHT ueberschrieben werden."""
    def _run(cmd, **kw):
        return _fake_result(stdout="host\n")

    with mock.patch.object(setup_mod.subprocess, "run", side_effect=_run):
        host = setup_mod._owui_litellm_target_host("proj")
    assert host == "127.0.0.1", host


def test_target_host_stays_loopback_when_network_mode_not_determinable():
    """Kein Docker / Container fehlt / docker inspect schlaegt fehl ->
    bisherige Annahme NICHT aendern (kein generatives Raten)."""
    def _run(cmd, **kw):
        return _fake_result(returncode=1, stderr="Error: No such object: open-webui")

    with mock.patch.object(setup_mod.subprocess, "run", side_effect=_run):
        host = setup_mod._owui_litellm_target_host("proj")
    assert host == "127.0.0.1", host

    with mock.patch.object(setup_mod.subprocess, "run", side_effect=Exception("docker fehlt")):
        host = setup_mod._owui_litellm_target_host("proj")
    assert host == "127.0.0.1", host


def test_ensure_owui_on_litellm_network_connects_and_is_idempotent():
    """docker inspect liefert das Netz des LiteLLM-Containers; OWUI wird dran
    gehaengt. Ein bereits verbundenes OWUI ("already exists") gilt als
    Erfolg; ein fehlender LiteLLM-Container als Fehler (kein stiller OK)."""
    # Erfolg: inspect -> Netzname, connect -> rc 0
    def _run_ok(cmd, **kw):
        if cmd[:2] == ["docker", "inspect"]:
            assert cmd[-1] == _EXPECTED, cmd
            return _fake_result(stdout=f"{_EXPECTED}_default\n")
        if cmd[:3] == ["docker", "network", "connect"]:
            assert cmd[-1] == "open-webui", cmd
            assert cmd[-2] == f"{_EXPECTED}_default", cmd
            return _fake_result(returncode=0)
        raise AssertionError(cmd)

    with mock.patch.object(setup_mod.subprocess, "run", side_effect=_run_ok):
        ok, detail = setup_mod._ensure_owui_on_litellm_network("proj")
    assert ok is True, detail

    # Idempotent: connect meldet "already exists" -> trotzdem True
    def _run_already(cmd, **kw):
        if cmd[:2] == ["docker", "inspect"]:
            return _fake_result(stdout=f"{_EXPECTED}_default\n")
        return _fake_result(returncode=1, stderr="Error response from daemon: endpoint with name open-webui already exists in network foo")

    with mock.patch.object(setup_mod.subprocess, "run", side_effect=_run_already):
        ok, detail = setup_mod._ensure_owui_on_litellm_network("proj")
    assert ok is True, detail

    # LiteLLM-Container fehlt -> False (sichtbar, kein stiller Erfolg)
    def _run_missing(cmd, **kw):
        if cmd[:2] == ["docker", "inspect"]:
            return _fake_result(returncode=1, stderr="No such object")
        raise AssertionError("connect darf bei fehlendem Container nicht versucht werden")

    with mock.patch.object(setup_mod.subprocess, "run", side_effect=_run_missing):
        ok, detail = setup_mod._ensure_owui_on_litellm_network("proj")
    assert ok is False, detail


def test_start_openwebui_keeps_host_gateway_add_host_flag():
    """`docker run`-Argv fuer den neu erstellten OWUI-Container behaelt
    `--add-host host.docker.internal:host-gateway` (harmlos/No-Op auf Linux,
    Docker-Desktop-kompatibel; der Linux-Anschluss laeuft ueber das
    gemeinsame Netz, s. _ensure_owui_on_litellm_network)."""
    calls = []

    def _run(cmd, **kw):
        calls.append(cmd)
        if cmd[:4] == ["docker", "ps", "-a", "--format"]:
            return _fake_result(stdout="")  # kein bestehender Container
        return _fake_result(returncode=0)

    with mock.patch.object(launcher_mod, "_cmd_available", return_value=True), \
         mock.patch.object(launcher_mod.subprocess, "run", side_effect=_run), \
         mock.patch.object(launcher_mod, "_openwebui_ok", return_value=(True, "ok")), \
         mock.patch("time.sleep"):
        launcher_mod._start_openwebui()

    run_calls = [c for c in calls if c[:2] == ["docker", "run"]]
    assert len(run_calls) == 1, calls
    argv = run_calls[0]
    assert "--add-host" in argv, argv
    idx = argv.index("--add-host")
    assert argv[idx + 1] == "host.docker.internal:host-gateway", argv


def test_connection_uses_container_name_and_binds_network_for_bridged():
    """Gebridgter Kontext: _ensure_owui_litellm_connection haengt OWUI ans
    Netz UND baut target_url aus dem Container-Namen (nicht 127.0.0.1)."""
    net_calls = []

    class _FakeResp:
        def __init__(self, status, payload):
            self.status = status
            self._payload = payload

        def read(self):
            import json
            return json.dumps(self._payload).encode()

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def _fake_urlopen(req, timeout=15):
        if req.get_method() == "GET":
            return _FakeResp(200, {"OPENAI_API_BASE_URLS": [], "OPENAI_API_KEYS": [], "OPENAI_API_CONFIGS": {}})
        return _FakeResp(200, {})

    def _fake_net(project):
        net_calls.append(project)
        return True, f"open-webui an Netz {_EXPECTED}_default angehängt"

    with mock.patch.object(setup_mod, "_owui_container_network_mode", return_value="bridge"), \
         mock.patch.object(setup_mod, "_ensure_owui_on_litellm_network", side_effect=_fake_net), \
         mock.patch.object(setup_mod, "_owui_litellm_target_host", return_value=_EXPECTED), \
         mock.patch.object(setup_mod, "_litellm_routing_model_id", return_value="proj-sonnet"), \
         mock.patch("urllib.request.urlopen", side_effect=_fake_urlopen):
        ok, msg = setup_mod._ensure_owui_litellm_connection(
            "http://127.0.0.1:8080", "owui-key", "litellm-master-key", "proj", 4000,
        )
    assert ok is True, msg
    assert net_calls == ["proj"], net_calls
    assert f"{_EXPECTED}:4000" in msg, msg
    assert "127.0.0.1:4000" not in msg, msg


def test_connection_refuses_when_network_not_bindable():
    """Netz-Anbindung scheitert (LiteLLM-Container/Netz nicht ermittelbar) ->
    sichtbare Ablehnung (ok=False), KEIN Fallback auf eine falsche
    Loopback-URL und KEIN OWUI-Call."""
    def _fail_net(project):
        return False, "LiteLLM-Container litellm-proj nicht gefunden"

    def _must_not_call(req, timeout=15):
        raise AssertionError("urlopen darf bei nicht herstellbarer Netz-Anbindung nicht laufen")

    with mock.patch.object(setup_mod, "_owui_container_network_mode", return_value="bridge"), \
         mock.patch.object(setup_mod, "_ensure_owui_on_litellm_network", side_effect=_fail_net), \
         mock.patch("urllib.request.urlopen", side_effect=_must_not_call):
        ok, msg = setup_mod._ensure_owui_litellm_connection(
            "http://127.0.0.1:8080", "owui-key", "litellm-master-key", "proj", 4000,
        )
    assert ok is False, msg
    assert "nicht herstellbar" in msg, msg


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
