#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n4_route_check_gate_2026_11_10.py — Delta-Test für
ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N4 §N4-1 P4 (A5).

Vorher hing die positive Fertigmeldung von `ensure_litellm_autowire` an
Connection + Preset-Rewire + dem AGGREGIERTEN `/api/models`-Listing
(`_wait_for_owui_model_visible`). Der Connection-Helfer selbst setzt dabei
`model_ids`-Pins (`_ensure_owui_litellm_connection`) -- das Listing kann
dadurch "verbunden" zeigen, OHNE dass die Route tatsächlich trägt (die Pins
filtern nur die Anzeige, sie beweisen keine Erreichbarkeit).

Deckt:
  (A) `_verify_owui_connection_route`: HTTP 200 + lesbarer models-Körper ->
      `True` (bestätigt erreichbar).
  (B) `_verify_owui_connection_route`: lesbarer Fehlerstatus (HTTPError) ->
      `False` (bestätigt negativ), NICHT None.
  (C) `_verify_owui_connection_route`: Netzwerkfehler (kein lesbares
      Ergebnis) -> `None` (nicht prüfbar), NICHT False.
  (D) `ensure_litellm_autowire`: Connection+Rewire OK, aggregiertes Listing
      (`visible`) zeigt "sichtbar", ABER der nichtgenerative Routecheck
      liefert `False` -> `auto_wired=False`, KEINE Fertigmeldung ("Pin/
      aggregierte Sichtbarkeit allein genügt nicht").
  (E) Positivkontrolle: Connection+Rewire OK UND Routecheck `True` ->
      `auto_wired=True`, Fertigmeldung "live verkabelt".
  (F) Negativkontrolle: Routecheck nicht erreichbar (`None`) -> weder
      "live verkabelt" noch ein falsches "nicht verbunden" -- eine eigene
      "nicht prüfbar"-Aussage.

Double-Grenze (A4, offen gelegt): für (A)-(C) ist `urllib.request.urlopen`
gedoubelt (kein echter Netzwerk-Call). Für (D)-(F) sind
`_ensure_owui_litellm_connection`, `_rewire_preset_base_model`,
`_wait_for_owui_model_visible`, `_auto_load_owui_env`, `_read_env_file`
vollständig gedoubelt (gleiche Double-Grenze wie der bestehende
`autowired_visibility`-Test); NUR `_verify_owui_connection_route` bleibt
ungemockt in (D)-(F) nicht der Fall -- es wird gezielt (A)-(C)-artig über
`urllib.request.urlopen` gesteuert, damit der real geprüfte Gate-Code in
`ensure_litellm_autowire` unverändert läuft. Kein Docker/Netzwerk-Call.

Pure Python, nur `assert`, echter Exitcode, kein Docker/Netzwerk."""
from __future__ import annotations

import importlib.util
import io
import json
import traceback
import unittest.mock as mock
import urllib.error
from contextlib import redirect_stdout
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_SETUP_PY = _REPO_ROOT / "scripts" / "setup.py"

_spec = importlib.util.spec_from_file_location(
    "f1_n4_route_check_gate_setup_under_test", _SETUP_PY,
)
setup_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(setup_mod)


class _FakeResp:
    def __init__(self, body: bytes, status: int = 200):
        self._body = body
        self.status = status

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


# ── (A)-(C) _verify_owui_connection_route ───────────────────────────────

def test_route_check_true_on_readable_200():
    def _ok(req, timeout=15):
        return _FakeResp(json.dumps({"data": [{"id": "proj-sonnet"}]}).encode(), status=200)

    with mock.patch("urllib.request.urlopen", side_effect=_ok):
        result = setup_mod._verify_owui_connection_route(
            "http://127.0.0.1:8080", "owui-key", "http://litellm:4000/v1", "sk-litellm-test",
        )
    assert result is True, result


def test_route_check_false_on_readable_http_error():
    def _http_error(req, timeout=15):
        raise urllib.error.HTTPError(
            "http://127.0.0.1:8080/openai/verify", 400, "bad", {}, io.BytesIO(b'{"detail":"nope"}'),
        )

    with mock.patch("urllib.request.urlopen", side_effect=_http_error):
        result = setup_mod._verify_owui_connection_route(
            "http://127.0.0.1:8080", "owui-key", "http://litellm:4000/v1", "sk-litellm-test",
        )
    assert result is False, (
        f"ein lesbarer Fehlerstatus ist eine bestaetigte negative Antwort (False), war {result!r}"
    )


def test_route_check_none_on_network_error():
    def _network_error(req, timeout=15):
        raise urllib.error.URLError("connection refused")

    with mock.patch("urllib.request.urlopen", side_effect=_network_error):
        result = setup_mod._verify_owui_connection_route(
            "http://127.0.0.1:8080", "owui-key", "http://litellm:4000/v1", "sk-litellm-test",
        )
    assert result is None, (
        f"ein Netzwerkfehler ist nicht pruefbar (None), keine bestaetigte Abwesenheit (False), war {result!r}"
    )


# ── (D)-(F) ensure_litellm_autowire-Gate ────────────────────────────────

def _base_mocks(*, ok_conn=True, ok_rewire=True, visible=True):
    return [
        mock.patch.object(setup_mod, "_read_env_file", return_value={"LITELLM_MASTER_KEY": "sk-litellm-test"}),
        mock.patch.object(setup_mod, "_auto_load_owui_env", return_value=False),
        mock.patch.object(setup_mod, "_litellm_routing_model_id", return_value="proj-sonnet"),
        mock.patch.object(setup_mod, "_ensure_owui_litellm_connection", return_value=(ok_conn, "conn-msg")),
        mock.patch.object(setup_mod, "_wait_for_owui_model_visible", return_value=visible),
        mock.patch.object(setup_mod, "_rewire_preset_base_model", return_value=(ok_rewire, "rewire-msg")),
    ]


def _run_with_env_key(cfg, *, verify_side_effect):
    import os
    saved = dict(os.environ)
    os.environ["OPENWEBUI_API_KEY"] = "owui-test-key"
    os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
    try:
        mocks = _base_mocks(ok_conn=True, ok_rewire=True, visible=True)
        with mocks[0], mocks[1], mocks[2], mocks[3], mocks[4], mocks[5], \
             mock.patch("urllib.request.urlopen", side_effect=verify_side_effect):
            buf = io.StringIO()
            with redirect_stdout(buf):
                result = setup_mod.ensure_litellm_autowire(Path("/tmp/repo-fake"), cfg)
            return result, buf.getvalue()
    finally:
        os.environ.clear()
        os.environ.update(saved)


_CFG = {"project": "Proj", "variants": {"default": {"preset_id": "p1", "cache": True}}}


def test_aggregated_visibility_alone_is_not_enough_when_route_check_fails():
    """(D), Kern von A5: `visible=True` (aggregiertes Listing) reicht NICHT,
    wenn der nichtgenerative Routecheck bestaetigt scheitert."""
    def _http_error(req, timeout=15):
        raise urllib.error.HTTPError(
            "http://127.0.0.1:8080/openai/verify", 400, "bad", {}, io.BytesIO(b'{"detail":"nope"}'),
        )

    result, out = _run_with_env_key(_CFG, verify_side_effect=_http_error)
    assert result is False, (
        "aggregiertes Listing 'sichtbar' + fehlgeschlagener Routecheck duerfen NICHT auto_wired=True ergeben"
    )
    assert "Cache ist live verkabelt" not in out, out


def test_positive_control_route_check_confirmed_reports_live_wired():
    """(E) Positivkontrolle: echter (simuliert lesbarer) Routecheck-Erfolg
    -> Fertigmeldung."""
    def _ok(req, timeout=15):
        return _FakeResp(json.dumps({"data": [{"id": "proj-sonnet"}]}).encode(), status=200)

    result, out = _run_with_env_key(_CFG, verify_side_effect=_ok)
    assert result is True, out
    assert "Cache ist live verkabelt" in out, out


def test_negative_control_route_unreachable_is_neither_wired_nor_falsely_disconnected():
    """(F) Negativkontrolle: Route nicht erreichbar -> 'nicht pruefbar',
    KEIN falsches 'verbunden' UND KEIN falsches bestaetigtes 'nicht
    verbunden'-Wording (das waere eine zu starke Behauptung fuer einen
    reinen Netzwerkfehler)."""
    def _network_error(req, timeout=15):
        raise urllib.error.URLError("connection refused")

    result, out = _run_with_env_key(_CFG, verify_side_effect=_network_error)
    assert result is False, "nicht pruefbar darf NIE als auto_wired=True gelten"
    assert "Cache ist live verkabelt" not in out, out
    assert "nicht prüfbar" in out.lower() or "unklar" in out.lower(), (
        f"ein reiner Netzwerkfehler sollte als 'nicht pruefbar' gemeldet werden, nicht stillschweigend: {out}"
    )


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
