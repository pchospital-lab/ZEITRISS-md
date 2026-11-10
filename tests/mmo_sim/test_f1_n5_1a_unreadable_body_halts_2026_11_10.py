#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n5_1a_unreadable_body_halts_2026_11_10.py —
Delta-Test für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N6 §N6-1a (N6-Nachzug zu
N5-1a).

WP-N6-1a korrigiert zwei Reste am N5-1a-Fix:

1. `APIClient.get_model` (setup.py) akzeptierte JEDEN 200-dict als gültiges
   Modellpreset (`isinstance(data, dict)` allein). Ein HTTP-200-FEHLEROBJEKT
   wie `{"detail": "unexpected shape"}` ist auch ein dict und wurde darum
   unbesehen als vorhandenes Preset zurückgegeben -- `last_model_body_ok`
   blieb fälschlich True. Jetzt verlangt `get_model` einen nicht-leeren
   String `id` (die Markerform eines echten OWUI-Modellpresets, s.
   downstream `preset.get("id", preset_id)`); ein Fehlerobjekt ohne `id`
   liefert jetzt `None` UND `last_model_body_ok is False`.

2. `_detect_install_state` (launcher.py) kollabierte einen erreichbaren, aber
   mehrdeutigen Befund (unlesbarer/formfalscher 200-Körper, Status außerhalb
   200/404) bislang auf "unreachable" -- identisch zum echten health-down-
   Fall. Das öffnete fälschlich den `_confirm_reinstall_unreachable()`-
   Override-Pfad (der für den ECHTEN N2-Bootfall legitim ist: OWUI bootet
   gerade, User kann bewusst "trotzdem fortfahren" wählen) auch für einen
   erreichbaren, aber unklar gelesenen Bestand. Ein unklarer Bestand ist
   WEDER bestätigtes Preset NOCH bestätigte Abwesenheit -- er darf NIE in
   `run_setup`s destroy&recreate laufen, auch nicht über eine zustimmende
   UI. Jetzt liefert der Klassifikator dafür einen eigenen State "unclear",
   den beide echten [1]-Caller (Eingangscheck UND WP1d-Auth-Recheck) als
   REINEN STOPP behandeln -- kein `_confirm_reinstall_unreachable`-Aufruf,
   kein Override möglich. "unreachable" bleibt ausschließlich für den
   echten health-down-Fall (`check_health()` False) reserviert, dort bleibt
   der bewusste Override (N2-Bootfall) unverändert möglich.

Deckt:
  (A) `_detect_install_state` mit echtem `APIClient` (nur `_request`
      gedoubelt): unlesbarer Preset-Körper (HTTP 200, kein JSON) ->
      "unclear", NICHT "fresh"/"installed"/"unreachable".
  (B) Formfalscher Preset-Körper (HTTP 200, JSON-Liste statt Objekt) ->
      "unclear".
  (B2) Falsches Modell-DICTIONARY (HTTP 200, JSON-OBJEKT ohne `id`, z.B.
      `{"detail": "unexpected shape"}`) -> `get_model` liefert None,
      `last_model_body_ok is False`, Klassifikator -> "unclear". Das ist
      der N6-1a-Rest: vorher galt JEDES dict als vorhandenes Preset.
  (C) KB-Antwort ohne passendes `items`-Feld (HTTP 200, JSON-Objekt ohne
      `items`) -> `APIClient.list_knowledge` liefert `last_knowledge_
      body_ok is False` UND `_detect_install_state` -> "unclear",
      NICHT "fresh" (trotz `kb_items == []`).
  (D) Gegenprobe: echte, lesbare Antworten (404 + `{"items": []}`) bleiben
      "fresh" -- bestätigt-frisch bleibt möglich, keine Überreaktion auf
      den Fix.
  (D2) Gegenprobe: ein wohlgeformtes Modellobjekt (`id` + `meta.knowledge`)
      bleibt "installed" -- der neue `id`-Formcheck in `get_model` darf ein
      echtes Preset NICHT fälschlich als formfalsch verwerfen.
  (E) Echter [1]-Eingangscheck-Caller (`action_install`, `_skip_state_
      check=False`): unlesbarer Körper -> State "unclear" hält VOR jeder
      Mutation an -- KEIN `_confirm_reinstall_unreachable`-Aufruf (anders
      als beim echten "unreachable"-Fall gibt es hier gar keinen Confirm,
      nur einen Stopp), `run_setup` NIE erreicht.
  (F) Echter WP1d-Re-Check-Caller (launcher.py, zweiter
      `_detect_install_state()`-Aufruf in `action_install`): derselbe Fix
      greift auch hier -- Eingangscheck ohne Key liefert "fresh"/
      "partial_no_key", Re-Check MIT Key trifft auf denselben unlesbaren
      Körper -> "unclear" hält an, KEIN Confirm, `run_setup` NIE erreicht.
  (G) Gegenprobe zu (E)/(F): selbst eine Konfiguration, die
      `_confirm_reinstall_unreachable` auf True stellen WÜRDE, erreicht
      `run_setup` bei "unclear" trotzdem NICHT -- es gibt dort gar keinen
      Confirm-Durchgriff (anders als beim echten Unreachable-Fall).
  (H) Dedizierte Gegenprobe: ECHTER health-down-Fall (`check_health()`
      False, OWUI wirklich weg) -> "unreachable" -> der bewusste N2-Bootfall-
      Override über `_confirm_reinstall_unreachable(True)` bleibt möglich,
      `run_setup` wird erreicht. Belegt, dass der neue "unclear"-Stopp den
      bestehenden, legitimen Unreachable-Override NICHT kaputt macht.

Double-Grenze (A4, offen gelegt): für (A)-(D2) ist NUR `APIClient._request`
gedoubelt (kein echter Netzwerk-Call) -- `APIClient` selbst, `get_model`,
`list_knowledge` und `_detect_install_state` laufen ECHT (Klassifikator
NICHT wegmockt). `load_cfg`/`_default_preset_id`/`_ensure_owui_env`/
`_openwebui_url`/`REPO` sind gedoubelt bzw. laufen gegen ein echtes
temporäres Verzeichnis (kein Netzwerk). Für (E)-(H) sind zusätzlich
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
    "f1_n6_1a_unreadable_body_halts_launcher_under_test", _LAUNCHER_PY,
)
launcher_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(launcher_mod)

setup_mod = launcher_mod.setup_module

_CFG = {"project": "Proj", "kb_name": "Proj Wissensspeicher"}


def _make_client(*, model_status=200, model_body=b"{}",
                  kb_status=200, kb_body=b'{"items": []}', healthy=True):
    """Echter APIClient, NUR `_request` gedoubelt -- `get_model`/
    `list_knowledge`/die `last_*_status`/`last_*_body_ok`-Flags laufen
    ECHT gegen den hier gesteuerten (Status, Körper)."""
    client = setup_mod.APIClient("http://127.0.0.1:8080", "fake-key")

    def _req(method, path, **kw):
        if path == "/api/config":
            return (200, b"{}") if healthy else (0, b"connection refused")
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


# ── (A)-(D2) echter APIClient + echter Klassifikator ────────────────────

def test_unreadable_200_model_body_is_unclear_not_fresh():
    client = _make_client(model_status=200, model_body=b"not json at all")
    assert client.get_model("p1") is None  # Vorbedingung: unlesbar -> None
    with tempfile.TemporaryDirectory() as tmp:
        state = _run_detect(client, tmp_repo=Path(tmp))
    assert state == "unclear", (
        f"HTTP 200 mit unlesbarem Preset-Koerper ist erreichbar+mehrdeutig -- "
        f"KEIN echter health-down-Fall -- war {state!r}"
    )


def test_malformed_200_model_body_is_unclear_not_fresh():
    """Formfalsch: lesbares JSON, aber eine Liste statt eines Objekts."""
    client = _make_client(model_status=200, model_body=b"[]")
    assert client.get_model("p1") is None
    assert client.last_model_body_ok is False
    with tempfile.TemporaryDirectory() as tmp:
        state = _run_detect(client, tmp_repo=Path(tmp))
    assert state == "unclear", (
        f"HTTP 200 mit formfalschem (Listen-statt-Objekt) Preset-Koerper ist "
        f"erreichbar+mehrdeutig -- war {state!r}"
    )


def test_false_model_dict_without_id_is_unclear_not_installed():
    """WP-N6-1a (der eigentliche N6-Rest): ein HTTP-200-FEHLEROBJEKT ist
    auch ein `dict` -- vorher akzeptierte `get_model` das unbesehen als
    vorhandenes Preset (`isinstance(data, dict)` allein). Ein echtes
    OWUI-Modellpreset TRAEGT ein nicht-leeres `id`-Feld, ein Fehlerobjekt
    wie `{"detail": ...}` nicht."""
    client = _make_client(
        model_status=200, model_body=b'{"detail":"unexpected shape"}',
    )
    assert client.get_model("p1") is None, (
        "ein 200-dict OHNE 'id' ist kein gueltiges Modellpreset -- get_model "
        "muss None liefern, nicht das Fehlerobjekt selbst"
    )
    assert client.last_model_body_ok is False, (
        "last_model_body_ok muss False sein -- sonst gilt ein Fehlerobjekt "
        "als bestaetigt vorhandenes Preset"
    )
    with tempfile.TemporaryDirectory() as tmp:
        state = _run_detect(client, tmp_repo=Path(tmp))
    assert state == "unclear", (
        f"ein falsches Modell-Dictionary darf NICHT als 'installed'/'partial' "
        f"durchlaufen (vorher: has_preset=True trotz Fehlerobjekt) -- war {state!r}"
    )


def test_kb_body_without_items_field_is_unclear_not_fresh():
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
    assert state == "unclear", (
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


def test_valid_wellformed_preset_with_kb_link_stays_installed():
    """Gegenprobe (D2): ein wohlgeformtes Modellobjekt (id + meta.knowledge)
    bleibt 'installed' -- der neue id-Formcheck darf ein ECHTES Preset nicht
    faelschlich verwerfen."""
    model_body = (
        b'{"id": "p1", "meta": {"knowledge": [{"id": "kb-1", "name": "Proj Wissensspeicher"}]}}'
    )
    client = _make_client(
        model_status=200, model_body=model_body,
        kb_status=200, kb_body=b'{"items": [{"id": "kb-1", "name": "Proj Wissensspeicher"}]}',
    )
    preset = client.get_model("p1")
    assert preset is not None, "ein wohlgeformtes Modellobjekt mit 'id' muss weiterhin akzeptiert werden"
    assert client.last_model_body_ok is True
    with tempfile.TemporaryDirectory() as tmp:
        state = _run_detect(client, tmp_repo=Path(tmp))
    assert state == "installed", f"Preset+KB-Link sollte 'installed' bleiben, war {state!r}"


# ── (E)-(H) echte [1]-Caller halten vor Mutation an ─────────────────────

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


def test_entry_check_unclear_halts_without_confirm_call():
    """(E): der ECHTE Eingangscheck-Caller trifft direkt (Key schon gesetzt)
    auf den unlesbaren Koerper -> 'unclear' -> REINER STOPP, kein Confirm-
    Aufruf ueberhaupt (anders als beim echten Unreachable-Fall)."""
    client = _make_client(model_status=200, model_body=b"not json at all")
    confirm_mock, run_setup_mock, _autowire_mock = _run_action_install(
        ensure_owui_env_effect=[True, True, True],  # Key liegt bereits vor
        client=client,
        confirm_unreachable_result=False,
    )
    assert confirm_mock.call_count == 0, (
        "ein unklarer (erreichbarer, aber mehrdeutiger) Bestand darf NICHT ueber den "
        "Unreachable-Confirm laufen -- dafuer gibt es gar keinen Confirm, nur einen Stopp"
    )
    assert run_setup_mock.call_count == 0, (
        "unklarer/unlesbarer Bestand darf NIE ungefragt in run_setup's destroy&recreate laufen"
    )


def test_recheck_unclear_halts_without_confirm_call():
    """(F): Eingangscheck OHNE Key (-> 'fresh', faellt durch), WP1d-Re-Check
    MIT Key trifft auf denselben unlesbaren Koerper -> 'unclear' -> REINER
    STOPP, kein Confirm-Aufruf. Deckt den ZWEITEN echten Caller ab."""
    client = _make_client(model_status=200, model_body=b"not json at all")
    # Aufrufreihenfolge: (1) Eingangsklassifikation -> kein Key -> 'fresh';
    # (2) action_install's eigener Browser-Key-Block -- Key liegt schon vor;
    # (3) WP1d-Re-Check-Klassifikation -- jetzt mit Key, live Check.
    confirm_mock, run_setup_mock, _autowire_mock = _run_action_install(
        ensure_owui_env_effect=[False, True, True],
        client=client,
        confirm_unreachable_result=False,
    )
    assert confirm_mock.call_count == 0, (
        "der WP1d-Re-Check muss denselben unlesbaren Koerper erreichen und "
        "dort ANHALTEN, ohne je den Unreachable-Confirm aufzurufen"
    )
    assert run_setup_mock.call_count == 0, (
        "der Re-Check-Caller darf NIE ungefragt in run_setup's destroy&recreate laufen"
    )


def test_recheck_unclear_halts_even_if_confirm_would_have_approved():
    """Gegenprobe (G) zur alten Erwartung: anders als beim echten
    'unreachable'-Fall gibt es bei 'unclear' GAR KEINEN Confirm-Durchgriff --
    selbst wenn `_confirm_reinstall_unreachable` auf True stuende (sie wird
    bei 'unclear' nie aufgerufen), erreicht `run_setup` NIE etwas. Vorher
    (N5-Fassung) war das umgekehrt: eine explizite Bestaetigung erreichte
    bewusst run_setup -- das war fuer den ECHTEN Unreachable-Fall richtig
    (s. test_real_unreachable_confirmed_override_still_reaches_run_setup
    unten), ist fuer den jetzt eingefuehrten 'unclear'-Fall aber FALSCH,
    weil ein unlesbarer Koerper weder bestaetigtes Preset noch bestaetigte
    Abwesenheit ist."""
    client = _make_client(model_status=200, model_body=b"not json at all")
    confirm_mock, run_setup_mock, _autowire_mock = _run_action_install(
        ensure_owui_env_effect=[False, True, True],
        client=client,
        confirm_unreachable_result=True,  # wuerde bestaetigen, WENN gefragt
    )
    assert confirm_mock.call_count == 0, (
        "bei 'unclear' wird der Unreachable-Confirm gar nicht erst aufgerufen"
    )
    assert run_setup_mock.call_count == 0, (
        "ein unklarer Bestand erreicht run_setup NIE -- auch nicht ueber eine "
        "(hypothetisch) zustimmende UI, weil es dafuer keinen Confirm-Pfad gibt"
    )


def test_real_unreachable_confirmed_override_still_reaches_run_setup():
    """(H): ECHTER health-down-Fall (`check_health()` False, OWUI wirklich
    weg) -> 'unreachable' -> der bestehende, bewusste N2-Bootfall-Override
    ueber `_confirm_reinstall_unreachable(True)` bleibt unveraendert
    moeglich. Belegt, dass der neue 'unclear'-Stopp NICHT den legitimen
    Unreachable-Override fuer den echten Boot-Fall kaputt macht."""
    client = _make_client(healthy=False)
    confirm_mock, run_setup_mock, _autowire_mock = _run_action_install(
        ensure_owui_env_effect=[False, True, True],
        client=client,
        confirm_unreachable_result=True,  # explizite Bestaetigung
    )
    assert confirm_mock.call_count >= 1, (
        "ein echter health-down-Fall muss weiterhin den Unreachable-Confirm erreichen"
    )
    assert run_setup_mock.call_count == 1, (
        "eine explizit bestaetigte Fortsetzung trotz echtem 'unreachable' muss "
        "weiterhin moeglich sein (N2-Bootfall)"
    )


def test_real_unreachable_rejected_halts_before_mutation():
    """Gegenprobe zu (H): Ablehnung am echten Unreachable-Confirm haelt
    weiterhin an -- kein stiller Default-Durchgriff."""
    client = _make_client(healthy=False)
    confirm_mock, run_setup_mock, _autowire_mock = _run_action_install(
        ensure_owui_env_effect=[True, True, True],
        client=client,
        confirm_unreachable_result=False,
    )
    assert confirm_mock.call_count >= 1
    assert run_setup_mock.call_count == 0, (
        "eine abgelehnte Bestaetigung bei echtem health-down darf NICHT in "
        "run_setup laufen"
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
