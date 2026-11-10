#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_gm_route_threading_2026_11_09.py — Delta-Test für
F1-3 (03_F1_AUFTRAG.md §F1-3: "gespeicherte Werte müssen bei den
tatsächlich verwendeten GM-/Persona-Factories ankommen").

Vorher reichte `mmo_sim/adapters/factories.py:default_gm_transport_factory`
NIE ein `sl_model`/`kb_id` an `GmOwuiTransport` durch (obwohl dessen
Konstruktor beide Parameter bereits akzeptierte) — und
`scripts/mmo_sim.py:main()` ermittelte diese Werte gar nicht erst. Jede
frische `setup.py`-Installation legt aber eine NEUE Knowledge-Base mit
neuer ID an; ohne diesen Fix griffe das Terminalspiel immer auf die in
`agent_mp/sl_client.py` hartkodierte KB-ID einer alten Installation zurück.

Deckt drei getrennte Stellen:
  (A) `factories.default_gm_transport_factory(..., sl_model=, kb_id=)`
      reicht beide Werte tatsächlich an den konstruierten Transport durch.
  (B) `scripts/mmo_sim.py:_resolve_active_gm_route()` ermittelt Preset-ID
      (aus `setup.json`) und KB-ID (live über den vorhandenen
      `setup.APIClient`) korrekt. F1-N2 WP-N2-2a (NACHTRAG): fehlende/
      unlesbare Konfiguration (kein `setup.json`, keine Preset-ID) liefert
      NICHT MEHR `(None, None)` ("fail-soft, stiller Fallback auf die
      sl_client.py-Altdefaults"), sondern `(None, GM_ROUTE_KB_UNVERIFIED)`
      -- produktive GM-Nutzung ohne verlässlich bestimmte eigene Modell-/
      KB-Werte lehnt sichtbar ab statt auf eine fremde historische KB
      auszuweichen. Programmstart/lokales Menü bleiben unberührt.
  (C) F1-N1 WP5a/PF3.GM (NACHTRAG): ein fehlgeschlagener KB-Read TROTZ
      vorhandenem Key liefert den Sentinel `GM_ROUTE_KB_UNVERIFIED` statt
      stillem `None` — vorher war das vom "kein Key"-Fall nicht
      unterscheidbar, und `GmOwuiTransport`/`sl_client.py` fiel auf die
      hartkodierte HISTORISCHE KB_ID zurück, als wäre das ein gültiger
      "bewusst keine KB"-Zustand. F1-N2 WP-N2-2a: HTTP 501 ist davon KEINE
      Ausnahme mehr (vorher bewusst `(sl_model, None)`, weil die schlanken
      E2E-Fake-Server den Endpunkt nicht implementierten) -- die Fakes
      bekommen stattdessen ein minimales `do_GET` oder laufen über
      `MMO_SIM_GM_TRANSPORT_DOUBLE`. Das Wiring in `main()` baut bei diesem
      Sentinel keine Live-Factory mehr, sondern
      `_blocked_gm_transport_factory()`, die erst beim tatsächlichen
      produktiven Zugriff sichtbar ablehnt.

Double-Grenzen (A4, offen gelegt):
  (A) `mmo_sim.adapters.gm_owui.GmOwuiTransport` wird durch ein Fake
      ersetzt, das nur die übergebenen Konstruktor-Kwargs aufzeichnet —
      kein echter `sl_client`-Import, kein HTTP, keine OWUI-Verbindung.
  (B) `setup` (scripts/setup.py) wird durch ein Fake-Modul in `sys.modules`
      ersetzt (eigenes `APIClient`, eigenes `_auto_load_owui_env`) — keine
      echte Netzwerk-/OWUI-Anbindung, reine Entscheidungslogik-Prüfung.

Pure Python, nur `assert`, echter Exitcode, temporäre Verzeichnisse."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import traceback
import types
from pathlib import Path
from unittest import mock

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.adapters.factories import default_gm_transport_factory  # noqa: E402
import mmo_sim.adapters.gm_owui as gm_owui_mod  # noqa: E402


def test_factory_forwards_sl_model_and_kb_id_to_transport():
    captured: dict = {}

    class _FakeTransport:
        def __init__(self, sl_client_path, run_dir, table_id=None,
                     sl_model=None, kb_id=None, **kw):
            captured["sl_model"] = sl_model
            captured["kb_id"] = kb_id
            captured["table_id"] = table_id

    real_transport = gm_owui_mod.GmOwuiTransport
    gm_owui_mod.GmOwuiTransport = _FakeTransport
    tmp = Path(tempfile.mkdtemp(prefix="f1-gm-route-"))
    try:
        factory = default_gm_transport_factory(
            tmp, _REPO_ROOT, sl_model="zeitriss-v426-uncut", kb_id="kb-fresh-123",
        )
        factory("table-1")
        assert captured["sl_model"] == "zeitriss-v426-uncut", captured
        assert captured["kb_id"] == "kb-fresh-123", captured
        assert captured["table_id"] == "table-1", captured
    finally:
        gm_owui_mod.GmOwuiTransport = real_transport
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_factory_without_sl_model_kb_id_keeps_old_default_none_behavior():
    """Regressionsschutz: ohne die neuen Kwargs (jeder bestehende Aufrufer,
    z.B. `mmo_sim/lab/cli.py`) bleiben beide Werte `None` -- `GmOwuiTransport`
    faellt dann weiterhin auf die `sl_client.py`-Altdefaults zurueck."""
    captured: dict = {"called": False}

    class _FakeTransport:
        def __init__(self, sl_client_path, run_dir, table_id=None,
                     sl_model=None, kb_id=None, **kw):
            captured["called"] = True
            captured["sl_model"] = sl_model
            captured["kb_id"] = kb_id

    real_transport = gm_owui_mod.GmOwuiTransport
    gm_owui_mod.GmOwuiTransport = _FakeTransport
    tmp = Path(tempfile.mkdtemp(prefix="f1-gm-route-"))
    try:
        factory = default_gm_transport_factory(tmp, _REPO_ROOT)  # alte 2-Arg-Form
        factory("table-1")
        assert captured["called"]
        assert captured["sl_model"] is None
        assert captured["kb_id"] is None
    finally:
        gm_owui_mod.GmOwuiTransport = real_transport
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def _load_mmo_sim_entrypoint():
    """Laedt `scripts/mmo_sim.py` per explizitem Dateipfad (identische
    Technik wie `scripts/mmo_sim_launcher_hook.py:launch()`) -- ein
    plattes `import mmo_sim` wuerde an das Paket `mmo_sim/` binden, nicht an
    den Shim, s. dessen eigener Kollisions-Docstring."""
    spec = importlib.util.spec_from_file_location(
        "f1_mmo_sim_entrypoint_under_test", _REPO_ROOT / "scripts" / "mmo_sim.py",
    )
    module = importlib.util.module_from_spec(spec)
    # F1-Critic-Fix: scripts/mmo_sim.py ruft beim Laden seinen venv-Bootstrap
    # (`ensure_running_in_project_venv`) auf -- ohne diesen Mock feuert der ein
    # echtes `os.execv`/`pip install` mitten im Test (per strace belegt), was
    # den Testprozess still neu startet (doppelte "OK"-Zeilen) und auf einem
    # frischen CI-Runner ohne `.venv` einen unentdeckten Netzwerkaufruf
    # ausloest. `sys.prefix` auf das erwartete `.venv` zeigen lassen ->
    # `already_in_venv()` == True -> Bootstrap ist No-Op (identische Technik
    # wie test_f1_venv_bootstrap_2026_11_09.py).
    with mock.patch.object(sys, "prefix", str(_REPO_ROOT / ".venv")):
        spec.loader.exec_module(module)
    return module


def _install_fake_setup_module(get_result):
    """Installiert ein Fake-`setup`-Modul. `get_result` ist ein `(code, data)`-
    Tupel wie `APIClient.get` es liefert -- `_resolve_active_gm_route` ist
    seit der F1-N1-WP5a-Verfeinerung status-bewusst (unterscheidet 200 /
    501 / sonstige Codes), statt `get_model` (das jeden Nicht-200 zu None
    kollabiert) zu verwenden."""
    fake_setup = types.ModuleType("setup")
    fake_setup._auto_load_owui_env_calls = []

    def _auto_load_owui_env():
        fake_setup._auto_load_owui_env_calls.append(True)

    class _FakeAPIClient:
        def __init__(self, url, key):
            self.url = url
            self.key = key

        def get(self, path, **kw):
            return get_result

    fake_setup._auto_load_owui_env = _auto_load_owui_env
    fake_setup.APIClient = _FakeAPIClient
    sys.modules["setup"] = fake_setup
    return fake_setup


def test_resolve_active_gm_route_no_setup_json_is_fail_soft_for_local_menu_but_unverified_for_gm():
    """F1-N2 WP-N2-2a: fehlendes `setup.json` ist weiterhin fail-soft fuer
    den Programmstart (die Funktion crasht nicht, `main()` blockiert
    nicht) -- ABER `kb_id` ist jetzt der Sentinel `GM_ROUTE_KB_UNVERIFIED`
    statt stillem `None`, damit produktive GM-Nutzung (`.turn()`) NICHT auf
    die hartkodierten `sl_client.py`-Altdefaults (fremde historische KB)
    zurueckfaellt. Lokales Menue/Figurenverwaltung bleiben unberuehrt, weil
    `default_gm_transport_factory` erst bei tatsaechlichem Transportbau
    wirft (s. test_gm_transport_factory_blocks_productive_use_when_kb_
    unverified)."""
    module = _load_mmo_sim_entrypoint()
    tmp = Path(tempfile.mkdtemp(prefix="f1-resolve-route-"))
    try:
        sl_model, kb_id = module._resolve_active_gm_route(tmp)
        assert sl_model is None, sl_model
        assert kb_id == module.GM_ROUTE_KB_UNVERIFIED, (
            f"fehlendes setup.json haette den Sentinel liefern muessen (nicht stilles None), war {kb_id!r}"
        )
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_resolve_active_gm_route_without_owui_key_returns_only_sl_model():
    module = _load_mmo_sim_entrypoint()
    tmp = Path(tempfile.mkdtemp(prefix="f1-resolve-route-"))
    saved_setup = sys.modules.get("setup")
    saved_env = module.os.environ.pop("OPENWEBUI_API_KEY", None)
    try:
        (tmp / "setup.json").write_text(json.dumps({
            "default_variant": "sonnet",
            "variants": {"sonnet": {"preset_id": "zeitriss-v426-uncut"}},
        }), encoding="utf-8")
        _install_fake_setup_module(get_result=(200, {}))
        sl_model, kb_id = module._resolve_active_gm_route(tmp)
        assert sl_model == "zeitriss-v426-uncut", sl_model
        assert kb_id is None, kb_id
    finally:
        if saved_setup is not None:
            sys.modules["setup"] = saved_setup
        else:
            sys.modules.pop("setup", None)
        if saved_env is not None:
            module.os.environ["OPENWEBUI_API_KEY"] = saved_env
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_resolve_active_gm_route_invalid_auth_is_visibly_rejected():
    """F1-N1 WP5a (PF3.GM): ein (simuliert) abgelaufener/falscher OWUI-Key
    fuehrt zu HTTP 401 (von `APIClient.get` intern abgefangen, kein raise)
    -- `_resolve_active_gm_
    route` darf dabei NICHT crashen, UND darf NICHT mehr still `(sl_model,
    None)` zurueckgeben (das sah wie "Route korrekt, aber bewusst ohne KB"
    aus und liess `GmOwuiTransport`/`sl_client.py` auf die hartkodierte
    HISTORISCHE KB_ID einer alten Installation zurueckfallen -- ein
    fehlgeschlagener Read wurde so faelschlich als Erfolg behandelt).
    Stattdessen muss der unterscheidbare Sentinel `GM_ROUTE_KB_UNVERIFIED`
    zurueckkommen, den `default_gm_transport_factory` (mmo_sim/adapters/
    factories.py) in eine sichtbar ablehnende Factory statt eines Live-
    Transports uebersetzt (s. test_gm_transport_factory_blocks_productive_
    use_when_kb_unverified unten)."""
    module = _load_mmo_sim_entrypoint()
    tmp = Path(tempfile.mkdtemp(prefix="f1-resolve-route-auth-"))
    saved_setup = sys.modules.get("setup")
    saved_env = dict(module.os.environ)
    try:
        (tmp / "setup.json").write_text(json.dumps({
            "default_variant": "sonnet",
            "variants": {"sonnet": {"preset_id": "zeitriss-v426-uncut"}},
        }), encoding="utf-8")
        module.os.environ["OPENWEBUI_API_KEY"] = "invalid-expired-key-not-a-secret"
        module.os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"

        fake_setup = types.ModuleType("setup")

        def _auto_load_owui_env():
            pass

        class _UnauthorizedAPIClient:
            def __init__(self, url, key):
                pass

            def get(self, path, **kw):
                # APIClient faengt HTTP 401 INTERN ab und gibt (code, body)
                # zurueck, OHNE zu werfen -- der realistische Auth-Fehlerweg.
                return 401, {"detail": "invalid API key"}

        fake_setup._auto_load_owui_env = _auto_load_owui_env
        fake_setup.APIClient = _UnauthorizedAPIClient
        sys.modules["setup"] = fake_setup

        sl_model, kb_id = module._resolve_active_gm_route(tmp)
        assert sl_model == "zeitriss-v426-uncut", sl_model
        assert kb_id == module.GM_ROUTE_KB_UNVERIFIED, (
            f"ein fehlgeschlagener Auth-Read haette den Sentinel liefern muessen, war {kb_id!r}"
        )
    finally:
        if saved_setup is not None:
            sys.modules["setup"] = saved_setup
        else:
            sys.modules.pop("setup", None)
        module.os.environ.clear()
        module.os.environ.update(saved_env)
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_resolve_active_gm_route_preset_without_kb_link_is_unverified():
    """F1-N1 WP5a (PF3.GM, Main-Verfeinerung): Preset lesbar (HTTP 200), aber
    OHNE gueltige KB-Verknuepfung -> `GM_ROUTE_KB_UNVERIFIED`, NICHT mehr still
    `None`. VORHER fiel dieser Fall ueber `kb_id or KB_ID` in `sl_client.py`
    auf die hartkodierte historische KB einer alten Installation; der Auftrag
    verlangt ausdruecklich, dass auch ein "fehlender KB-Link" nicht auf die
    fremde historische KB ausweicht. Dieser Fall ist von den E2E-Fakes NICHT
    erreichbar (die liefern 501 fuer `GET /api/v1/models/model`, also VOR einem
    Preset) -- er kann daher sicher sentinel werden."""
    module = _load_mmo_sim_entrypoint()
    tmp = Path(tempfile.mkdtemp(prefix="f1-resolve-route-nokb-"))
    saved_setup = sys.modules.get("setup")
    saved_env = dict(module.os.environ)
    try:
        (tmp / "setup.json").write_text(json.dumps({
            "default_variant": "sonnet",
            "variants": {"sonnet": {"preset_id": "zeitriss-v426-uncut"}},
        }), encoding="utf-8")
        module.os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
        module.os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
        fake_preset_no_kb = {"meta": {"knowledge": []}}
        _install_fake_setup_module(get_result=(200, fake_preset_no_kb))
        sl_model, kb_id = module._resolve_active_gm_route(tmp)
        assert sl_model == "zeitriss-v426-uncut", sl_model
        assert kb_id == module.GM_ROUTE_KB_UNVERIFIED, kb_id
    finally:
        if saved_setup is not None:
            sys.modules["setup"] = saved_setup
        else:
            sys.modules.pop("setup", None)
        module.os.environ.clear()
        module.os.environ.update(saved_env)
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_resolve_active_gm_route_no_key_at_all_stays_plain_none():
    """Gegenprobe (WP5a): der echte 'Key fehlt ganz'-Fall bleibt
    UNVERAENDERT plain `None` (nicht der Sentinel) -- dieser Pfad bleibt
    bewusst fail-closed in `sl_client.SLSession.__init__`, unberuehrt von
    diesem Fix."""
    module = _load_mmo_sim_entrypoint()
    tmp = Path(tempfile.mkdtemp(prefix="f1-resolve-route-nokey-"))
    saved_setup = sys.modules.get("setup")
    saved_env = module.os.environ.pop("OPENWEBUI_API_KEY", None)
    try:
        (tmp / "setup.json").write_text(json.dumps({
            "default_variant": "sonnet",
            "variants": {"sonnet": {"preset_id": "zeitriss-v426-uncut"}},
        }), encoding="utf-8")
        _install_fake_setup_module(get_result=(200, {}))
        sl_model, kb_id = module._resolve_active_gm_route(tmp)
        assert sl_model == "zeitriss-v426-uncut", sl_model
        assert kb_id is None, f"kein-Key-Fall haette plain None bleiben muessen, war {kb_id!r}"
    finally:
        if saved_setup is not None:
            sys.modules["setup"] = saved_setup
        else:
            sys.modules.pop("setup", None)
        if saved_env is not None:
            module.os.environ["OPENWEBUI_API_KEY"] = saved_env
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_gm_transport_factory_blocks_productive_use_when_kb_unverified():
    """F1-N1 WP5a: `default_gm_transport_factory(..., kb_id=GM_ROUTE_KB_
    UNVERIFIED)` darf KEINEN Live-`GmOwuiTransport` mit dem Sentinel als
    `kb_id` bauen -- stattdessen wirft die Factory bei TATSAECHLICHEM
    Aufruf (erster `.turn()`-Transportbau) sichtbar ab. Programmstart
    selbst (die Factory-KONSTRUKTION, nicht der Aufruf) bleibt unberuehrt."""
    from mmo_sim.adapters.factories import GM_ROUTE_KB_UNVERIFIED
    saved_double = os.environ.pop("MMO_SIM_GM_TRANSPORT_DOUBLE", None)
    tmp = Path(tempfile.mkdtemp(prefix="f1-gm-route-blocked-"))
    try:
        factory = default_gm_transport_factory(
            tmp, _REPO_ROOT, sl_model="f1n1test-sonnet", kb_id=GM_ROUTE_KB_UNVERIFIED,
        )
        raised = False
        try:
            factory("table-1")
        except RuntimeError as exc:
            raised = True
            msg = str(exc)
            assert "GM-Route nicht verlaesslich aufgeloest" in msg, msg
        assert raised, "Factory haette bei Aufruf mit unverifiziertem kb_id werfen muessen"
    finally:
        if saved_double is not None:
            os.environ["MMO_SIM_GM_TRANSPORT_DOUBLE"] = saved_double
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_gm_transport_double_seam_takes_priority_over_unverified_block():
    """Regressionstest (gefunden beim F1-N1-WP6-Vollauf, s. Report): eine
    FRÜHERE Fassung dieses Fixes ersetzte die GESAMTE Factory im Wiring
    von `scripts/mmo_sim.py:main()`, sobald `kb_id == GM_ROUTE_KB_
    UNVERIFIED` war -- das umging den bestehenden `MMO_SIM_GM_TRANSPORT_
    DOUBLE`-Test-Seam komplett (Double wurde nie konsultiert), weil der
    Seam-Check NUR innerhalb der `default_gm_transport_factory`-Closure
    lebt. Mehrere bestehende Tests (u.a. test_a24_local_two_humans,
    test_k1_k4_lobby_kontinuitaet), die den Double-Seam nutzen, scheiterten
    dadurch mit 'missing actual operations', weil ihr GM-Double nie lief.
    Fix: der Unverified-Check liegt jetzt INNERHALB der Closure, NACH dem
    Double-Check -- ein gesetzter Double hat weiterhin Vorrang, auch wenn
    `kb_id` der Sentinel ist."""
    from mmo_sim.adapters.factories import GM_ROUTE_KB_UNVERIFIED

    double_calls: list = []

    def _fake_double_transport(table_id: str):
        double_calls.append(table_id)
        return "double-transport-result"

    import types
    double_module = types.ModuleType("f1_n1_gm_double_regression_module")
    double_module.fake_transport = _fake_double_transport
    sys.modules["f1_n1_gm_double_regression_module"] = double_module

    saved_double = os.environ.get("MMO_SIM_GM_TRANSPORT_DOUBLE")
    tmp = Path(tempfile.mkdtemp(prefix="f1-gm-route-double-priority-"))
    try:
        os.environ["MMO_SIM_GM_TRANSPORT_DOUBLE"] = "f1_n1_gm_double_regression_module:fake_transport"
        factory = default_gm_transport_factory(
            tmp, _REPO_ROOT, sl_model="f1n1test-sonnet", kb_id=GM_ROUTE_KB_UNVERIFIED,
        )
        result = factory("table-1")
        assert result == "double-transport-result", (
            f"Double haette trotz GM_ROUTE_KB_UNVERIFIED laufen muessen, war: {result!r}"
        )
        assert double_calls == ["table-1"], double_calls
    finally:
        if saved_double is None:
            os.environ.pop("MMO_SIM_GM_TRANSPORT_DOUBLE", None)
        else:
            os.environ["MMO_SIM_GM_TRANSPORT_DOUBLE"] = saved_double
        sys.modules.pop("f1_n1_gm_double_regression_module", None)
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_resolve_active_gm_route_with_owui_key_resolves_live_kb_id():
    module = _load_mmo_sim_entrypoint()
    tmp = Path(tempfile.mkdtemp(prefix="f1-resolve-route-"))
    saved_setup = sys.modules.get("setup")
    saved_env = dict(module.os.environ)
    try:
        (tmp / "setup.json").write_text(json.dumps({
            "default_variant": "sonnet",
            "variants": {"sonnet": {"preset_id": "zeitriss-v426-uncut"}},
        }), encoding="utf-8")
        module.os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
        module.os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
        fake_preset = {"meta": {"knowledge": [{"id": "kb-fresh-456", "name": "x"}]}}
        _install_fake_setup_module(get_result=(200, fake_preset))
        sl_model, kb_id = module._resolve_active_gm_route(tmp)
        assert sl_model == "zeitriss-v426-uncut", sl_model
        assert kb_id == "kb-fresh-456", kb_id
    finally:
        if saved_setup is not None:
            sys.modules["setup"] = saved_setup
        else:
            sys.modules.pop("setup", None)
        module.os.environ.clear()
        module.os.environ.update(saved_env)
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def _resolve_with_get_result(get_result):
    """Hilfs-Setup fuer die statuscode-bezogenen Faelle: setup.json + Key da,
    Fake-`APIClient.get` liefert `get_result`. Gibt (sl_model, kb_id) zurueck
    und raeumt Modul/Env auf."""
    module = _load_mmo_sim_entrypoint()
    tmp = Path(tempfile.mkdtemp(prefix="f1-resolve-route-code-"))
    saved_setup = sys.modules.get("setup")
    saved_env = dict(module.os.environ)
    try:
        (tmp / "setup.json").write_text(json.dumps({
            "default_variant": "sonnet",
            "variants": {"sonnet": {"preset_id": "zeitriss-v426-uncut"}},
        }), encoding="utf-8")
        module.os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
        module.os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
        _install_fake_setup_module(get_result=get_result)
        return module, module._resolve_active_gm_route(tmp)
    finally:
        if saved_setup is not None:
            sys.modules["setup"] = saved_setup
        else:
            sys.modules.pop("setup", None)
        module.os.environ.clear()
        module.os.environ.update(saved_env)
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_resolve_active_gm_route_501_models_endpoint_not_implemented_is_unverified():
    """F1-N2 WP-N2-2a: der vorherige 501-Carve-out ist ENTFERNT. HTTP 501
    (`GET /api/v1/models/model` nicht implementiert) muss wie jeder andere
    Nicht-200-Code behandelt werden -- ein HTTP-Status identifiziert keinen
    Testprozess. Die betroffenen schlanken E2E-Fake-Server (N2-2b) bekommen
    stattdessen ein minimales `do_GET` fuer diesen Endpunkt oder laufen ueber
    `MMO_SIM_GM_TRANSPORT_DOUBLE`."""
    module, (sl_model, kb_id) = _resolve_with_get_result((501, b""))
    assert sl_model == "zeitriss-v426-uncut", sl_model
    assert kb_id == module.GM_ROUTE_KB_UNVERIFIED, (
        f"501 haette wie jeder andere Nicht-200-Code den Sentinel liefern muessen, war {kb_id!r}"
    )


def test_resolve_active_gm_route_404_preset_missing_is_unverified():
    """Server erreichbar, Preset aber nicht vorhanden (404) -> sichtbar
    ablehnen, NICHT still auf die historische KB (PF3.GM, voll geschlossen)."""
    module, (sl_model, kb_id) = _resolve_with_get_result((404, {"detail": "not found"}))
    assert sl_model == "zeitriss-v426-uncut", sl_model
    assert kb_id == module.GM_ROUTE_KB_UNVERIFIED, kb_id


def test_resolve_active_gm_route_connection_error_is_unverified():
    """Unerreichbarer Dienst (APIClient._request liefert code 0 bei URLError/
    OSError) trotz vorhandenem Key -> Sentinel, nicht stille historische KB."""
    module, (sl_model, kb_id) = _resolve_with_get_result((0, b"connection refused"))
    assert sl_model == "zeitriss-v426-uncut", sl_model
    assert kb_id == module.GM_ROUTE_KB_UNVERIFIED, kb_id


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
