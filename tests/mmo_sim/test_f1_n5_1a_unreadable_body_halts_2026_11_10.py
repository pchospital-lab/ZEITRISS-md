#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n5_1a_unreadable_body_halts_2026_11_10.py —
Delta-Test für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N5 §N5-1a (N4-A4-Rest).

Vorher las `_detect_install_state` (launcher.py) die von `APIClient`
gesetzten `last_model_body_ok`/`last_knowledge_body_ok`-Flags NIRGENDS --
ein HTTP-200-Körper, den `APIClient` nicht als Objekt lesen konnte (None/
nicht-dict/Liste statt Objekt), wurde über `get_model`/`list_knowledge` zu
None/[] -- identisch zu einer ECHTEN bestätigten Abwesenheit (HTTP 404 /
leere KB-Liste). Der Klassifikator sah nur den Status (200), nicht die
Körperform, und konnte deshalb trotz unlesbarem/formfalschem Körper
"fresh" liefern -- `action_install` hätte `run_setup` (destroy & recreate)
OHNE jeden Confirm-Prompt erreicht, weil "fresh" (anders als "partial"/
"unreachable") keinen Gate-Schritt hat. Derselbe Klassifikator läuft
unverändert vor `run_setup` beim WP1d-Re-Check erneut (launcher.py
1032-1084) -- dieselbe Lücke war an BEIDEN echten Callern erreichbar.

Zusätzlich validierte `APIClient.list_knowledge` nur `isinstance(data, dict)`
als "gültiger Körper" -- eine KB-Antwort ohne passendes `items`-Feld (anderes
Schema/Fehlerobjekt) wurde über `data.get("items", [])` stumm als bestätigt
leer ausgegeben.

Deckt:
  (A) `_detect_install_state` mit echtem `APIClient` (nur `_request`
      gedoubelt): unlesbarer Preset-Körper (HTTP 200, kein JSON) ->
      "unreachable", NICHT "fresh"/"installed".
  (B) Formfalscher Preset-Körper (HTTP 200, JSON-Liste statt Objekt) ->
      "unreachable".
  (C) KB-Antwort ohne passendes `items`-Feld (HTTP 200, JSON-Objekt ohne
      `items`) -> `APIClient.list_knowledge` liefert `last_knowledge_
      body_ok is False` UND `_detect_install_state` -> "unreachable",
      NICHT "fresh" (trotz `kb_items == []`).
  (D) Gegenprobe: echte, lesbare Antworten (404 + `{"items": []}`) bleiben
      "fresh" -- bestätigt-frisch bleibt möglich, keine Überreaktion auf
      den Fix.
  (E) Echter [1]-Eingangscheck-Caller (`action_install`, `_skip_state_
      check=False`): unlesbarer Körper -> State "unreachable" hält VOR
      jeder Mutation an (`_confirm_reinstall_unreachable`, Default-Ablehnung
      -> `run_setup` NIE erreicht).
  (F) Echter WP1d-Re-Check-Caller (launcher.py 1032-1084, zweiter
      `_detect_install_state()`-Aufruf in `action_install`): derselbe Fix
      greift auch hier -- Eingangscheck ohne Key liefert "fresh"/
      "partial_no_key", Re-Check MIT Key trifft auf denselben unlesbaren
      Körper -> "unreachable" hält an, `run_setup` NIE erreicht.
  (G) Gegenprobe zu (E)/(F): EXPLIZIT bestätigte Ablehnung des Unreachable-
      Confirms -- `run_setup` wird nicht aufgerufen (kein stiller Default).

Double-Grenze (A4, offen gelegt): für (A)-(D) ist NUR `APIClient._request`
gedoubelt (kein echter Netzwerk-Call) -- `APIClient` selbst, `get_model`,
`list_knowledge` und `_detect_install_state` laufen ECHT (Klassifikator
NICHT wegmockt). `load_cfg`/`_default_preset_id`/`_ensure_owui_env`/
`_openwebui_url`/`REPO` sind gedoubelt bzw. laufen gegen ein echtes
temporäres Verzeichnis (kein Netzwerk). Für (E)-(G) sind zusätzlich
`_docker_ok`/`_openwebui_ok`/`_openrouter_key_status`/
`setup_module._update_env_file_preserving`/`setup_module._read_env_file`/
`_prompt`/`_pause`/`_confirm_reinstall_unreachable`/`setup_module.run_setup`/
`setup_module.ensure_litellm_autowire`/`_litellm_ok` gedoubelt (gleiche
Double-Grenze wie der bestehende `ambiguous_halts_before_mutation`-Test) --
`_detect_install_state` selbst bleibt auch hier ECHT. Kein Docker/
Netzwerk-Call.

Pure Python, nur `assert`, echter Exitcode, kein Docker/Netzwerk."""
from __future__ import annotations

import importlib.util
import os
import tempfile
import traceback
import unittest.mock as mock
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_LAUNCHER_PY = _REPO_ROOT / "scripts" / "launcher.py"

_spec = importlib.util.spec_from_file_location(
    "f1_n5_1a_unreadable_body_halts_launcher_under_test", _LAUNCHER_PY,
)
launcher_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(launcher_mod)

setup_mod = launcher_mod.setup_module

_CFG = {"project": "Proj", "kb_name": "Proj Wissensspeicher"}


def _make_client(*, model_status=200, model_body=b"{}",
                  kb_status=200, kb_body=b'{"items": []}'):
    """Echter APIClient, NUR `_request` gedoubelt -- `get_model`/
    `list_knowledge`/die `last_*_status`/`last_*_body_ok`-Flags laufen
    ECHT gegen den hier gesteuerten (Status, Körper)."""
    client = setup_mod.APIClient("http://127.0.0.1:8080", "fake-key")

    def _req(method, path, **kw):
        if path == "/api/config":
            return 200, b"{}"
        if "/models/model" in path:
            return model_status, model_body
        if "/knowledge/" in path:
            return kb_status, kb_body
        return 200, b"{}"

    client._request = _req
    return client


def _run_detect(client, *, tmp_repo):
    with mock.patch.object(launcher_mod, "REPO", tmp_repo), \
         mock.patch.object(launcher_mod, "load_cfg", return_value=_CFG), \
         mock.patch.object(launcher_mod, "_default_preset_id", return_value="p1"), \
         mock.patch.object(launcher_mod, "_ensure_owui_env", return_value=True), \
         mock.patch.object(launcher_mod, "_openwebui_url", return_value="http://127.0.0.1:8080"), \
         mock.patch.object(setup_mod, "APIClient", return_value=client):
        saved = dict(os.environ)
        os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
        try:
            return launcher_mod._detect_install_state()
        finally:
            os.environ.clear()
            os.environ.update(saved)


# ── (A)-(D) echter APIClient + echter Klassifikator ─────────────────────

def test_unreadable_200_model_body_is_unreachable_not_fresh():
    client = _make_client(model_status=200, model_body=b"not json at all")
    assert client.get_model("p1") is None  # Vorbedingung: unlesbar -> None
    with tempfile.TemporaryDirectory() as tmp:
        state = _run_detect(client, tmp_repo=Path(tmp))
    assert state == "unreachable", (
        f"HTTP 200 mit unlesbarem Preset-Koerper ist KEIN bestaetigtes 'Preset "
        f"fehlt' -- war {state!r}"
    )


def test_malformed_200_model_body_is_unreachable_not_fresh():
    """Formfalsch: lesbares JSON, aber eine Liste statt eines Objekts."""
    client = _make_client(model_status=200, model_body=b"[]")
    assert client.get_model("p1") is None
    assert client.last_model_body_ok is False
    with tempfile.TemporaryDirectory() as tmp:
        state = _run_detect(client, tmp_repo=Path(tmp))
    assert state == "unreachable", (
        f"HTTP 200 mit formfalschem (Listen-statt-Objekt) Preset-Koerper ist KEIN "
        f"bestaetigtes 'Preset fehlt' -- war {state!r}"
    )


def test_kb_body_without_items_field_is_unreachable_not_fresh():
    """KB-Antwort HTTP 200, JSON-Objekt, aber OHNE passendes `items`-Feld --
    `list_knowledge` darf das nicht stumm als [] (bestaetigt leer) ausgeben."""
    client = _make_client(
        model_status=404, model_body=b'{"detail":"not found"}',
        kb_status=200, kb_body=b'{"detail": "unexpected shape"}',
    )
    kb_result = client.list_knowledge()
    assert kb_result == []
    assert client.last_knowledge_body_ok is False, (
        "ein 200-Koerper ohne passendes 'items'-Feld ist formfalsch, KEIN "
        "bestaetigt leeres Ergebnis"
    )
    with tempfile.TemporaryDirectory() as tmp:
        state = _run_detect(client, tmp_repo=Path(tmp))
    assert state == "unreachable", (
        f"eine KB-Antwort ohne 'items'-Feld darf NICHT als bestaetigt 'keine KB "
        f"da' durchlaufen -- war {state!r}"
    )


def test_confirmed_fresh_with_readable_bodies_stays_fresh():
    """Gegenprobe (D): echte 404 (Preset fehlt) + lesbares {'items': []}
    (keine KB da) bleibt 'fresh' -- bestaetigt-frisch bleibt moeglich."""
    client = _make_client(
        model_status=404, model_body=b'{"detail":"not found"}',
        kb_status=200, kb_body=b'{"items": []}',
    )
    with tempfile.TemporaryDirectory() as tmp:
        state = _run_detect(client, tmp_repo=Path(tmp))
    assert state == "fresh", f"echter Erstinstall (lesbar bestaetigt) sollte 'fresh' bleiben, war {state!r}"


# ── (E)-(G) echte [1]-Caller halten vor Mutation an ─────────────────────

def _run_action_install(*, ensure_owui_env_effect, client, confirm_unreachable_result):
    saved_env = dict(os.environ)
    os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
    os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
    os.environ["OPENROUTER_API_KEY"] = "sk-or-test-fake"
    try:
        with mock.patch.object(launcher_mod, "load_cfg", return_value=_CFG), \
             mock.patch.object(launcher_mod, "_default_preset_id", return_value="p1"), \
             mock.patch.object(launcher_mod, "_openwebui_url", return_value="http://127.0.0.1:8080"), \
             mock.patch.object(setup_mod, "APIClient", return_value=client), \
             mock.patch.object(launcher_mod, "_ensure_owui_env", side_effect=ensure_owui_env_effect), \
             mock.patch.object(launcher_mod, "_docker_ok", return_value=(True, "ok")), \
             mock.patch.object(launcher_mod, "_openwebui_ok", return_value=(True, "ok")), \
             mock.patch.object(launcher_mod, "_openrouter_key_status", return_value=(True, "ok")), \
             mock.patch.object(setup_mod, "_update_env_file_preserving", return_value=True), \
             mock.patch.object(setup_mod, "_read_env_file",
                                return_value={"LITELLM_MASTER_KEY": "sk-litellm-test-fake"}), \
             mock.patch.object(launcher_mod, "_confirm_reinstall_unreachable",
                                return_value=confirm_unreachable_result) as confirm_mock, \
             mock.patch.object(setup_mod, "run_setup") as run_setup_mock, \
             mock.patch.object(setup_mod, "ensure_litellm_autowire") as autowire_mock, \
             mock.patch.object(launcher_mod, "_prompt", return_value=""), \
             mock.patch.object(launcher_mod, "_pause"), \
             mock.patch.object(launcher_mod, "_litellm_ok", return_value=(True, "ok")):
            launcher_mod.action_install()
        return confirm_mock, run_setup_mock, autowire_mock
    finally:
        os.environ.clear()
        os.environ.update(saved_env)


def test_entry_check_unreachable_halts_before_confirm_and_mutation():
    """(E)+(G): der ECHTE Eingangscheck-Caller trifft direkt (Key schon
    gesetzt) auf den unlesbaren Koerper -> 'unreachable' -> Confirm wird
    gefragt, Default-Ablehnung -> KEIN run_setup."""
    client = _make_client(model_status=200, model_body=b"not json at all")
    confirm_mock, run_setup_mock, _autowire_mock = _run_action_install(
        ensure_owui_env_effect=[True, True, True],  # Key liegt bereits vor
        client=client,
        confirm_unreachable_result=False,  # explizite Ablehnung
    )
    assert confirm_mock.call_count >= 1, (
        "ein unlesbarer Koerper muss den expliziten Unreachable-Confirm erreichen "
        "(statt stumm 'fresh' zu sein und den Confirm ganz zu umgehen)"
    )
    assert run_setup_mock.call_count == 0, (
        "unklarer/unlesbarer Bestand darf NIE ungefragt in run_setup's destroy&recreate laufen"
    )


def test_recheck_unreachable_halts_before_confirm_and_mutation():
    """(F)+(G): Eingangscheck OHNE Key (-> 'fresh', faellt durch), WP1d-
    Re-Check MIT Key trifft auf denselben unlesbaren Koerper -> 'unreachable'
    -> Confirm wird gefragt, Default-Ablehnung -> KEIN run_setup. Deckt den
    ZWEITEN echten Caller (launcher.py 1032-1084) ab."""
    client = _make_client(model_status=200, model_body=b"not json at all")
    # Aufrufreihenfolge: (1) Eingangsklassifikation -> kein Key -> 'fresh';
    # (2) action_install's eigener Browser-Key-Block -- Key liegt schon vor;
    # (3) WP1d-Re-Check-Klassifikation -- jetzt mit Key, live Check.
    confirm_mock, run_setup_mock, _autowire_mock = _run_action_install(
        ensure_owui_env_effect=[False, True, True],
        client=client,
        confirm_unreachable_result=False,  # explizite Ablehnung
    )
    assert confirm_mock.call_count >= 1, (
        "der WP1d-Re-Check muss denselben unlesbaren Koerper erreichen und den "
        "Unreachable-Confirm ausloesen"
    )
    assert run_setup_mock.call_count == 0, (
        "der Re-Check-Caller darf NIE ungefragt in run_setup's destroy&recreate laufen"
    )


def test_recheck_unreachable_confirmed_override_still_reaches_run_setup():
    """Gegenprobe zu (G): eine EXPLIZITE Bestaetigung am Unreachable-Confirm
    bleibt ein bewusster Override -- der Fix haelt nur VOR unklarer Mutation
    an, er verbietet eine gewollte Fortsetzung nicht."""
    client = _make_client(model_status=200, model_body=b"not json at all")
    confirm_mock, run_setup_mock, _autowire_mock = _run_action_install(
        ensure_owui_env_effect=[False, True, True],
        client=client,
        confirm_unreachable_result=True,  # explizite Bestaetigung
    )
    assert confirm_mock.call_count >= 1
    assert run_setup_mock.call_count == 1, (
        "eine explizit bestaetigte Fortsetzung trotz 'unreachable' muss weiterhin moeglich sein"
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
