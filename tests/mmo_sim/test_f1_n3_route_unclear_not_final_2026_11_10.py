#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n3_route_unclear_not_final_2026_11_10.py —
Delta-Test für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N3 §N3-1d.

Vorher lieferte `_wait_for_owui_model_visible` nur `bool` -- ein Timeout
OHNE jede lesbare Antwort (OWUI während der ganzen Prüfung nicht erreichbar)
sah identisch aus wie ein Timeout MIT lesbaren Antworten, in denen das
Modell nur einfach nie auftauchte. `ensure_litellm_autowire`s
Abschlusslage konnte diese beiden Fälle damit nicht trennen: "konfiguriert,
aber (sicher) nicht sichtbar" und "konfiguriert, Sichtbarkeits-Check selbst
unklar" druckten dieselbe Meldung -- keine ehrliche Trennung von
"tatsächlich verbunden" / "noch offen/nicht prüfbar" / "nicht sichtbar".

Deckt:
  (A) `_wait_for_owui_model_visible`: JEDER Versuch wirft (Netzwerkfehler)
      -> liefert `None` (unklar), NICHT `False` (bestätigte Abwesenheit).
  (B) `_wait_for_owui_model_visible`: mindestens EINE lesbare Antwort, Modell
      aber nie drin -> liefert `False` (bestätigt, nicht nur "unklar").
  (C) `ensure_litellm_autowire`: Connection+Rewire OK, Sichtbarkeits-Check
      liefert `None` -> `auto_wired=False` (KEINE Fertigmeldung "live
      verkabelt"/"verbunden"), UND die gedruckte Meldung unterscheidet sich
      von der "konfiguriert, aber nicht sichtbar"-Meldung (eigene,
      "unklar/nicht prüfbar"-Formulierung statt einer falschen negativen
      Bestätigung).

Double-Grenze (A4, offen gelegt): für (A)/(B) wird `urllib.request.urlopen`
gedoubelt (kein echter Netzwerk-Call). Für (C) sind
`_ensure_owui_litellm_connection`, `_rewire_preset_base_model`,
`_wait_for_owui_model_visible`, `_auto_load_owui_env`, `_read_env_file`
vollständig gedoubelt (gleiche Double-Grenze wie der bestehende
`autowired_visibility`-Test). Kein Docker/Netzwerk-Call.

Pure Python, nur `assert`, echter Exitcode, kein Docker/Netzwerk."""
from __future__ import annotations

import importlib.util
import io
import traceback
import unittest.mock as mock
import urllib.error
from contextlib import redirect_stdout
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_SETUP_PY = _REPO_ROOT / "scripts" / "setup.py"

_spec = importlib.util.spec_from_file_location(
    "f1_n3_route_unclear_not_final_setup_under_test", _SETUP_PY,
)
setup_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(setup_mod)


def test_wait_for_visible_returns_none_when_every_attempt_errors():
    def _always_fails(req, timeout=5):
        raise urllib.error.URLError("connection refused")

    with mock.patch("urllib.request.urlopen", side_effect=_always_fails):
        result = setup_mod._wait_for_owui_model_visible(
            "http://127.0.0.1:8080", "owui-key", "proj-sonnet", max_wait_s=0.3,
        )
    assert result is None, (
        f"jeder Versuch ist fehlgeschlagen -- das ist unklar/nicht pruefbar "
        f"(None), keine bestaetigte Abwesenheit (False); war {result!r}"
    )


def test_wait_for_visible_returns_false_when_responses_readable_but_model_absent():
    class _FakeResp:
        def __init__(self, payload):
            import json
            self._body = json.dumps(payload).encode()

        def read(self):
            return self._body

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def _ok_but_empty(req, timeout=5):
        return _FakeResp({"data": [{"id": "some-other-model"}]})

    with mock.patch("urllib.request.urlopen", side_effect=_ok_but_empty):
        result = setup_mod._wait_for_owui_model_visible(
            "http://127.0.0.1:8080", "owui-key", "proj-sonnet", max_wait_s=0.3,
        )
    assert result is False, (
        f"lesbare Antworten kamen, das Modell war nur nie drin -- das ist eine "
        f"bestaetigte negative Aussage (False), nicht None; war {result!r}"
    )


def _base_mocks(*, ok_conn=True, ok_rewire=True, visible, route_check=None):
    # WP-N4-1 P4: die Fertigmeldung gated jetzt am nichtgenerativen
    # `route_check` (eigene Route), NICHT mehr am aggregierten
    # Sichtbarkeits-Listing (`visible`, hier weiterhin vorhanden -- nur
    # noch Zusatz-Info). Ohne diesen zusaetzlichen Double wuerde
    # `ensure_litellm_autowire` einen echten Netzwerk-Call zu
    # `_verify_owui_connection_route` ausloesen.
    return [
        mock.patch.object(setup_mod, "_read_env_file", return_value={"LITELLM_MASTER_KEY": "sk-litellm-test"}),
        mock.patch.object(setup_mod, "_auto_load_owui_env", return_value=False),
        mock.patch.object(setup_mod, "_litellm_routing_model_id", return_value="proj-sonnet"),
        mock.patch.object(setup_mod, "_ensure_owui_litellm_connection", return_value=(ok_conn, "conn-msg")),
        mock.patch.object(setup_mod, "_wait_for_owui_model_visible", return_value=visible),
        mock.patch.object(setup_mod, "_rewire_preset_base_model", return_value=(ok_rewire, "rewire-msg")),
        mock.patch.object(setup_mod, "_verify_owui_connection_route", return_value=route_check),
    ]


def _run_with_env_key(cfg):
    import os
    saved = dict(os.environ)
    os.environ["OPENWEBUI_API_KEY"] = "owui-test-key"
    os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            result = setup_mod.ensure_litellm_autowire(Path("/tmp/repo-fake"), cfg)
        return result, buf.getvalue()
    finally:
        os.environ.clear()
        os.environ.update(saved)


_CFG = {"project": "Proj", "variants": {"default": {"preset_id": "p1", "cache": True}}}


def test_route_check_unclear_is_not_reported_as_live_wired():
    # WP-N4-1 P4: `route_check=None` (nicht nur `visible=None`) ist jetzt
    # das massgebliche unklare Signal.
    mocks = _base_mocks(ok_conn=True, ok_rewire=True, visible=None, route_check=None)
    with mocks[0], mocks[1], mocks[2], mocks[3], mocks[4], mocks[5], mocks[6]:
        result, out = _run_with_env_key(_CFG)
    assert result is False, (
        "ein unklarer Routecheck (None) darf NIE als auto_wired=True gelten"
    )
    assert "Cache ist live verkabelt" not in out, out
    assert "verbunden" not in out.lower() or "nicht prüfbar" in out.lower() or "unklar" in out.lower(), (
        "keine Fertigmeldung 'verbunden' ohne den unklar/nicht-pruefbar-Hinweis"
    )


def test_route_check_unclear_message_differs_from_confirmed_failed():
    """Die beiden Zwischenstaende muessen UNTERSCHIEDLICHE Meldungen
    drucken -- sonst waere 'unklar' und 'bestaetigt fehlgeschlagen' fuer
    den Nutzer (und fuer die Diagnose) nicht unterscheidbar. WP-N4-1 P4:
    jetzt am `route_check`-Tri-State (nicht mehr `visible`) gemessen --
    `visible` ist seit P4 nur noch Zusatz-Info, kein Gate."""
    mocks_unclear = _base_mocks(ok_conn=True, ok_rewire=True, visible=None, route_check=None)
    with mocks_unclear[0], mocks_unclear[1], mocks_unclear[2], mocks_unclear[3], \
         mocks_unclear[4], mocks_unclear[5], mocks_unclear[6]:
        _, out_unclear = _run_with_env_key(_CFG)

    mocks_false = _base_mocks(ok_conn=True, ok_rewire=True, visible=True, route_check=False)
    with mocks_false[0], mocks_false[1], mocks_false[2], mocks_false[3], \
         mocks_false[4], mocks_false[5], mocks_false[6]:
        _, out_false = _run_with_env_key(_CFG)

    assert out_unclear != out_false, "unklar und bestaetigt-fehlgeschlagen drucken identischen Text"
    assert "nicht prüfbar" in out_unclear or "unklar" in out_unclear, out_unclear
    assert "Routecheck zur eigenen Verbindung ist bestätigt fehlgeschlagen" in out_false, out_false


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
