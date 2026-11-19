#!/usr/bin/env python3
"""
tests/mmo_sim/test_r4_01_cloud_gm_output_limit_2026_11_18.py — R4-01
Regression (ZR-ALTAIR-UPDATER-SPIELTEST-NACHZUG-20261118-r4,
01_GENERAL_REVIEW.md R4-01, 02_NACHZUG_AUFTRAG.md Block A).

Vorher loeste `mmo_sim/adapters/factories.py:default_gm_transport_factory`
den Output-Bound NUR aus `MMO_SIM_GM_OUTPUT_LIMIT_TOKENS` ODER dem lokalen
Profil (`_gm_provider == "local"`) auf. Fuer die normale Remote-/Cloud-
Route (`_gm_provider` 'legacy'/'cloud') OHNE gesetzte Env-Variable blieb
`gm_output_limit_tokens=None` -- `admission.py:664ff` blockte dann JEDEN
dollar_billed-Call, unabhaengig vom tatsaechlichen Verbrauch (eine reine
Konfig-Durchreichluecke, kein zu kleines Budget). Der Fix leitet die
wirksame Grenze aus der TATSAECHLICH ausgewaehlten `setup.json` ab
(`params.max_tokens` der Variante, deren `preset_id` dem live aufgeloesten
`sl_model` entspricht) -- `_resolve_cloud_gm_output_limit_tokens` in
factories.py.

Drei Gegenfaelle aus 01_GENERAL_REVIEW.md R4-01 / 02_NACHZUG_AUFTRAG.md
Block A, jeweils am REALEN Factory-Aufrufer:
  (a) fehlende/ungueltige wirksame Konfiguration -> blockt VOR jedem
      Transportbau (zwei Teste: Datei fehlt ganz; Datei da, Wert ungueltig).
  (b) explizite `MMO_SIM_GM_OUTPUT_LIMIT_TOKENS` -> behaelt Vorrang vor
      einer tatsaechlich abweichenden setup.json-Grenze.
  (c) lokales Profil (`_gm_provider == "local"`) -> bleibt bei seinem
      eigenen (kleineren) Startwert, KEINE Durchmischung mit der neuen
      Cloud-Ableitung, selbst wenn setup.json einen groesseren Wert traegt.
Zusaetzlich: die abgeleitete Grenze bindet an die PASSENDE Variante (nicht
blind an `default_variant`), wenn mehrere Varianten existieren.

Double-Grenzen: `mmo_sim.adapters.gm_owui.GmOwuiTransport` wird fuer die
Cloud-Faelle durch ein Fake ersetzt (reine Kwargs-Aufzeichnung, kein HTTP).
Der lokale Gegenfall (c) nutzt denselben echten HTTP-Double-Aufbau wie
`test_f1_gm_route_threading_2026_11_09.py::test_persisted_local_profile_
chains_route_resolution...` (`urllib.request.urlopen` gepatcht), damit
`_gm_provider` ECHT 'local' wird (kein Fake-Resolver dieser Datei selbst).

Pure Python, nur `assert`, echter Exitcode -- lauffaehig per `pytest`
(Modulimport ist unconditional, keine Delegating-`load_tests`-Bruecke)
UND als eigenstaendiges Skript."""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import traceback
import urllib.parse
from pathlib import Path
from unittest import mock

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.adapters.factories import default_gm_transport_factory  # noqa: E402
import mmo_sim.adapters.gm_owui as gm_owui_mod  # noqa: E402

_ENV_KEYS_TO_CLEAR = (
    "MMO_SIM_GM_OUTPUT_LIMIT_TOKENS", "MMO_SIM_GM_TRANSPORT_DOUBLE",
    "OPENWEBUI_API_KEY", "OPENWEBUI_URL",
)


class _FakeTransport:
    """Zeichnet nur die Konstruktor-Kwargs auf -- kein `sl_client`-Import,
    kein HTTP (identische Double-Technik zu test_f1_gm_route_threading)."""

    def __init__(self, sl_client_path, run_dir, table_id=None, sl_model=None,
                 kb_id=None, gm_output_limit_tokens=None, **kw):
        self.sl_model = sl_model
        self.kb_id = kb_id
        self.gm_output_limit_tokens = gm_output_limit_tokens


def _isolated_dirs():
    return (
        Path(tempfile.mkdtemp(prefix="r4-01-repo-")),
        Path(tempfile.mkdtemp(prefix="r4-01-data-")),
        Path(tempfile.mkdtemp(prefix="r4-01-home-")),
    )


def _cleanup(*dirs):
    for d in dirs:
        shutil.rmtree(d, ignore_errors=True)


def _run_cloud_factory(repo_root, data_dir, tmp_home, sl_model="r4-01-preset", kb_id="r4-01-kb"):
    """Baut+ruft die echte Factory gegen einen isolierten `repo_root`/`$HOME`
    (kein Lesen des echten Hosts) mit dem Transport-Double ersetzt."""
    real_transport = gm_owui_mod.GmOwuiTransport
    gm_owui_mod.GmOwuiTransport = _FakeTransport
    try:
        with mock.patch.object(Path, "home", return_value=tmp_home):
            factory = default_gm_transport_factory(data_dir, repo_root, sl_model=sl_model, kb_id=kb_id)
            return factory("r4-01-table")
    finally:
        gm_owui_mod.GmOwuiTransport = real_transport


def test_cloud_route_missing_setup_json_blocks_before_send():
    """Gegenfall (a1): fehlt `setup.json` am `repo_root` ganz, darf die
    Remote-/Cloud-Route NICHT mit `gm_output_limit_tokens=None` (=
    'unbegrenzt') weiterlaufen -- die Factory haelt SELBST sichtbar
    (RuntimeError), BEVOR ueberhaupt ein `GmOwuiTransport` konstruiert
    wird."""
    repo_root, data_dir, tmp_home = _isolated_dirs()
    saved_env = {k: os.environ.pop(k, None) for k in _ENV_KEYS_TO_CLEAR}
    try:
        raised = False
        try:
            _run_cloud_factory(repo_root, data_dir, tmp_home)
        except RuntimeError as exc:
            raised = True
            msg = str(exc)
            assert "setup.json" in msg, msg
            assert "keine wirksame GM-Ausgabegrenze ableitbar" in msg, msg
        assert raised, "fehlendes setup.json haette die Cloud-Route blockieren muessen"
    finally:
        for k, v in saved_env.items():
            if v is not None:
                os.environ[k] = v
        _cleanup(repo_root, data_dir, tmp_home)


def test_cloud_route_invalid_max_tokens_blocks_before_send():
    """Gegenfall (a2): `setup.json` vorhanden, aber `params.max_tokens` ist
    keine gueltige positive endliche Ganzzahl (hier `0`) -- muss GENAUSO
    sichtbar halten wie eine fehlende Datei, kein stiller Fallback auf
    unbegrenzt und kein hart codierter Ersatzwert."""
    repo_root, data_dir, tmp_home = _isolated_dirs()
    saved_env = {k: os.environ.pop(k, None) for k in _ENV_KEYS_TO_CLEAR}
    try:
        (repo_root / "setup.json").write_text(json.dumps({
            "default_variant": "sonnet",
            "variants": {"sonnet": {"preset_id": "r4-01-preset"}},
            "params": {"max_tokens": 0},
        }), encoding="utf-8")
        raised = False
        try:
            _run_cloud_factory(repo_root, data_dir, tmp_home)
        except RuntimeError as exc:
            raised = True
            assert "params.max_tokens" in str(exc), str(exc)
        assert raised, "params.max_tokens=0 haette die Cloud-Route blockieren muessen"
    finally:
        for k, v in saved_env.items():
            if v is not None:
                os.environ[k] = v
        _cleanup(repo_root, data_dir, tmp_home)


def test_cloud_route_derives_bound_from_matching_setup_variant():
    """Hauptfall R4-01: KEINE Env-Grenze gesetzt, Provider ist die Remote-/
    Cloud-Route ('legacy', kein lokales Profil persistiert) -- die Factory
    leitet die wirksame Grenze aus `setup.json params.max_tokens` ab UND
    bindet an die Variante, deren `preset_id` dem live aufgeloesten
    `sl_model` entspricht (hier bewusst NICHT `default_variant`, um
    blindes Binden an die erste/Default-Variante auszuschliessen). Derselbe
    Wert erreicht den konstruierten Transport (`gm_output_limit_tokens`-
    Kwarg) -- genau das Attribut, das `creation_service.py:164` als
    `gm_transport.output_limit_tokens` fuer Reservierung/Gate/Request
    liest."""
    repo_root, data_dir, tmp_home = _isolated_dirs()
    saved_env = {k: os.environ.pop(k, None) for k in _ENV_KEYS_TO_CLEAR}
    try:
        (repo_root / "setup.json").write_text(json.dumps({
            "default_variant": "sonnet",
            "variants": {
                "sonnet": {"preset_id": "r4-01-preset-sonnet"},
                "deepseek": {"preset_id": "r4-01-preset-deepseek"},
            },
            "params": {"max_tokens": 64000},
        }), encoding="utf-8")
        transport = _run_cloud_factory(
            repo_root, data_dir, tmp_home,
            sl_model="r4-01-preset-deepseek", kb_id="r4-01-kb",
        )
        assert transport.gm_output_limit_tokens == 64000.0, transport.gm_output_limit_tokens
    finally:
        for k, v in saved_env.items():
            if v is not None:
                os.environ[k] = v
        _cleanup(repo_root, data_dir, tmp_home)


def test_cloud_route_without_resolved_preset_does_not_derive_bound():
    """R4-01b-Gegenfall (Kontrollpunkt Y-N3,
    tests/mmo_sim/test_h02_vollreise_profiles_2026_09_28.py::test_y_n3_missing_
    gm_output_bound_blocks_under_hard_budget): der synthetische Lab-/Testpfad
    (`mmo_sim/lab/cli.py:489`) baut diese Factory OHNE `sl_model`. Dann gibt
    es keine gewaehlte Cloud-Konfiguration -- die Factory darf KEINEN Bound
    aus einer vorhandenen `setup.json` ableiten (auch nicht blind aus
    `default_variant`/Top-Level-`params`), sondern muss `gm_output_limit_
    tokens=None` lassen, damit `admission.py` den fehlenden GM-Outputbound
    weiterhin fail-closed blockt ("Kein durchsetzbares Ausgabe-/Gesamtlimit
    ...", 0 GM-Receipts). Vor der r4-Korrektur fiel der Resolver hier blind
    auf `default_variant` zurueck und lieferte 64000 -> defeatete den
    Kontrollpunkt (CI-Rot an genau diesem H02-Test)."""
    repo_root, data_dir, tmp_home = _isolated_dirs()
    saved_env = {k: os.environ.pop(k, None) for k in _ENV_KEYS_TO_CLEAR}
    try:
        (repo_root / "setup.json").write_text(json.dumps({
            "default_variant": "sonnet",
            "variants": {"sonnet": {"preset_id": "r4-01-preset"}},
            "params": {"max_tokens": 64000},
        }), encoding="utf-8")
        transport = _run_cloud_factory(
            repo_root, data_dir, tmp_home, sl_model=None, kb_id="r4-01-kb",
        )
        assert transport.gm_output_limit_tokens is None, (
            f"ohne aufgeloestes Cloud-Preset haette KEIN Bound abgeleitet werden "
            f"duerfen (Kontrollpunkt Y-N3 muss fail-closed bleiben), war "
            f"{transport.gm_output_limit_tokens!r}."
        )
    finally:
        for k, v in saved_env.items():
            if v is not None:
                os.environ[k] = v
        _cleanup(repo_root, data_dir, tmp_home)


def test_explicit_env_override_still_wins_over_setup_json():
    """Gegenfall (b): eine vorhandene EXPLIZITE `MMO_SIM_GM_OUTPUT_LIMIT_
    TOKENS` behaelt weiterhin Vorrang vor der aus `setup.json` abgeleiteten
    Grenze (02_NACHZUG_AUFTRAG.md Block A: "Ausdruecklich gueltige Grenzen
    ... bewahren") -- jetzt bewiesen gegen eine tatsaechlich *abweichende*
    setup.json-Grenze (vorher war setup.json fuer die Cloud-Route nie
    relevant, der Vorrang war gegen keinen echten Konkurrenzwert
    getestet)."""
    repo_root, data_dir, tmp_home = _isolated_dirs()
    saved_env = {k: os.environ.pop(k, None) for k in _ENV_KEYS_TO_CLEAR}
    try:
        (repo_root / "setup.json").write_text(json.dumps({
            "default_variant": "sonnet",
            "variants": {"sonnet": {"preset_id": "r4-01-preset"}},
            "params": {"max_tokens": 64000},
        }), encoding="utf-8")
        os.environ["MMO_SIM_GM_OUTPUT_LIMIT_TOKENS"] = "12345"
        transport = _run_cloud_factory(repo_root, data_dir, tmp_home, sl_model="r4-01-preset")
        assert transport.gm_output_limit_tokens == 12345.0, transport.gm_output_limit_tokens
    finally:
        for k, v in saved_env.items():
            if v is not None:
                os.environ[k] = v
        _cleanup(repo_root, data_dir, tmp_home)


class _ChainFakeResponse:
    """Minimale `urllib.request.urlopen`-Antwort (identische Form zu den
    Doubles in test_f1_gm_route_threading_2026_11_09.py)."""

    def __init__(self, status: int, body: bytes):
        self.status = status
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        return False


def test_local_profile_route_keeps_its_own_bound_not_cloud_setup_json():
    """Gegenfall (c): ein ECHT aktives lokales Profil (`_gm_provider ==
    'local'`, ueber einen persistierten `~/.openwebui_env`-Eintrag, kein
    Fake-Resolver) behaelt seinen eigenen `gm_max_tokens`-Startwert (4096,
    `local_model_profile.DEFAULT_GM_MAX_TOKENS`) -- die neue R4-01-Cloud-
    Ableitung darf NICHT auf den lokalen Zweig durchschlagen, OBWOHL
    `setup.json params.max_tokens` hier bewusst auf einen VIEL groesseren
    Wert (999999) gesetzt ist. Nutzt denselben echten HTTP-Double-Aufbau
    (Preset-Bindung, `/openai/verify`, `/openai/config`) wie der
    bestehende O2-B.B1-Kettentest in test_f1_gm_route_threading_2026_11_09.py."""
    scripts_dir = _REPO_ROOT / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    import local_model_profile as real_lmp
    import setup as real_setup

    repo_root, data_dir, tmp_home = _isolated_dirs()
    saved_env = dict(os.environ)
    saved_setup_mod = sys.modules.get("setup")
    FAKE_OWUI_URL = "http://127.0.0.1:18097"
    FAKE_OWUI_KEY = "owui-fake-key-not-secret-r401"
    FAKE_LOCAL_BASE = "http://127.0.0.1:18098/v1"
    FAKE_LOCAL_MODEL = "nemotron-r4-01-local"
    FAKE_LOCAL_TOKEN = "test-local-token-not-secret-r401"
    FAKE_PRESET = "r4-01-local-preset"
    FAKE_KB = "kb-r4-01-local"
    try:
        for key in _ENV_KEYS_TO_CLEAR:
            os.environ.pop(key, None)
        sys.modules["setup"] = real_setup

        (repo_root / "setup.json").write_text(json.dumps({
            "default_variant": "sonnet",
            "variants": {"sonnet": {"preset_id": FAKE_PRESET}},
            "params": {"max_tokens": 999999},
        }), encoding="utf-8")
        env_path = tmp_home / ".openwebui_env"
        updates = dict(real_lmp.build_local_profile_updates(
            base_url=FAKE_LOCAL_BASE, model=FAKE_LOCAL_MODEL, api_key=FAKE_LOCAL_TOKEN,
        ))
        updates["OPENWEBUI_URL"] = FAKE_OWUI_URL
        updates["OPENWEBUI_API_KEY"] = FAKE_OWUI_KEY
        assert real_setup._update_env_file_preserving(env_path, updates)

        def _router(req, timeout=None, context=None):
            url = req.full_url
            model_url_prefix = f"{FAKE_OWUI_URL}/api/v1/models/model?id={urllib.parse.quote(FAKE_PRESET, safe='')}"
            if url == model_url_prefix:
                body = {
                    "id": FAKE_PRESET, "base_model_id": FAKE_LOCAL_MODEL,
                    "meta": {"knowledge": [{"id": FAKE_KB}]},
                }
                return _ChainFakeResponse(200, json.dumps(body).encode("utf-8"))
            if url == f"{FAKE_OWUI_URL}/openai/verify":
                return _ChainFakeResponse(200, json.dumps({"data": [{"id": FAKE_LOCAL_MODEL}]}).encode("utf-8"))
            if req.get_method() == "GET" and url == f"{FAKE_OWUI_URL}/openai/config":
                body = {
                    "ENABLE_OPENAI_API": True,
                    "OPENAI_API_BASE_URLS": [FAKE_LOCAL_BASE],
                    "OPENAI_API_KEYS": [FAKE_LOCAL_TOKEN],
                    "OPENAI_API_CONFIGS": {
                        "0": {"enable": True, "model_ids": [FAKE_LOCAL_MODEL],
                              "auth_type": "bearer", "prefix_id": ""},
                    },
                }
                return _ChainFakeResponse(200, json.dumps(body).encode("utf-8"))
            raise AssertionError(f"unerwarteter Request im R4-01-Lokal-Gegenfall: {req.get_method()} {url}")

        with mock.patch.object(Path, "home", return_value=tmp_home), \
             mock.patch("urllib.request.urlopen", _router):
            factory = default_gm_transport_factory(
                data_dir, _REPO_ROOT, sl_model=FAKE_PRESET, kb_id=FAKE_KB,
            )
            transport = factory("r4-01-local-table")
            assert transport.is_dollar_billed is False, (
                "lokal bestaetigt gebundene Route muss dollar_billed=False tragen."
            )
            assert transport.output_limit_tokens == 4096, (
                f"lokaler Zweig haette bei seinem eigenen Startwert (4096) bleiben muessen, "
                f"war {transport.output_limit_tokens!r} -- Cloud-setup.json (999999) ist durchgeschlagen."
            )
    finally:
        os.environ.clear()
        os.environ.update(saved_env)
        if saved_setup_mod is not None:
            sys.modules["setup"] = saved_setup_mod
        else:
            sys.modules.pop("setup", None)
        _cleanup(repo_root, data_dir, tmp_home)


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
