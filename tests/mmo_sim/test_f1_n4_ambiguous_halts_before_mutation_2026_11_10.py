#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n4_ambiguous_halts_before_mutation_2026_11_10.py —
Delta-Test für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N4 §N4-1 P3 (A4).

Vorher kollabierte `APIClient.get_model`/`list_knowledge` ein HTTP-200 mit
unbrauchbarem/formfalschem Körper auf None/[] -- identisch zu einer
bestätigten leeren/fehlenden Antwort (last_status blieb 200). Zusätzlich
vereinigte `_resolve_orphaned_kb_for_partial` Fehler + Mehrdeutigkeit +
bestätigte Abwesenheit in einem einzigen `None`; die echten [1]-Caller
reichten das ungeprüft an `_confirm_reinstall_after_partial` (Default "j")
weiter -- ein unlesbarer Körper oder mehrere Treffer landeten so in einem
mutierenden Neuaufbau-Pfad, obwohl RETURN behauptete, danach könne nur noch
ein reiner Read folgen.

Deckt:
  (A) `APIClient.list_knowledge`/`get_model`: HTTP 200 + nicht-dict-Körper
      -> `last_*_body_ok is False` (NICHT True wie bei einer echten leeren/
      vorhandenen Antwort).
  (B) `_resolve_orphaned_kb_for_partial`: HTTP-200-mit-unlesbarem-Körper auf
      der KB-Liste -> `("unclear", ...)`, NICHT `("absent", None)`.
  (C) `_resolve_orphaned_kb_for_partial`: zweiter Read (KB-Liste) mit
      Status != 200 (z.B. nach einem Preset-Read, der schon unklar war)
      -> ebenfalls `("unclear", ...)`.
  (D) `_resolve_orphaned_kb_for_partial`: mehrdeutig (>1 gleichnamige KB)
      -> `("unclear", ...)`, NICHT der eindeutige `("kb", ...)`-Fall.
  (E) Echter [1]-Caller (`action_install`, state=='partial', BEIDE Zweige:
      Eingangscheck + WP1d-Re-Check): `kind=="unclear"` -> hält VOR jeder
      Mutation an -- `_confirm_reinstall_after_partial` (Default "j") wird
      NICHT erreicht, `run_setup`/`complete_orphaned_kb_install` laufen
      NICHT.
  (F) Gegenprobe: bestätigt frischer Fall (`kind=="absent"`) bleibt über den
      bisherigen, ausdrücklich bestätigten Confirm-Pfad weiterhin möglich.

Double-Grenze (A4, offen gelegt): fuer (A) ist nur `APIClient._request`
gedoubelt (simuliert HTTP ohne echten Netzwerk-Call); fuer (B)-(D) ein
minimaler Fake-Client (ausschliesslich `check_health`/`get_model`/
`list_knowledge` + die Status-/Body-Attribute); fuer (E)/(F)
`_detect_install_state`, `_docker_ok`, `_openwebui_ok`, `_ensure_owui_env`,
`_openrouter_key_status`, `setup_module._update_env_file_preserving`,
`setup_module.run_setup`, `setup_module.complete_orphaned_kb_install`,
`setup_module.ensure_litellm_autowire`, `_resolve_orphaned_kb_for_partial`,
`_confirm_reinstall_after_partial`, `_prompt`/`_pause` sind vollständig
gedoubelt. Kein Docker/Netzwerk-Call.

Pure Python, nur `assert`, echter Exitcode, kein Docker/Netzwerk."""
from __future__ import annotations

import importlib.util
import os
import traceback
import unittest.mock as mock
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_LAUNCHER_PY = _REPO_ROOT / "scripts" / "launcher.py"
_SETUP_PY = _REPO_ROOT / "scripts" / "setup.py"

_lspec = importlib.util.spec_from_file_location(
    "f1_n4_ambiguous_halts_launcher_under_test", _LAUNCHER_PY,
)
launcher_mod = importlib.util.module_from_spec(_lspec)
_lspec.loader.exec_module(launcher_mod)

setup_mod = launcher_mod.setup_module


# ── (A) APIClient-Koerper-Lesbarkeit ────────────────────────────────────

def _client_with_fake_request(body_bytes: bytes, status: int = 200):
    client = setup_mod.APIClient("http://127.0.0.1:8080", "fake-key")
    client._request = lambda method, path, **kw: (status, body_bytes)
    return client


def test_list_knowledge_http_200_non_dict_body_is_not_confirmed_empty():
    client = _client_with_fake_request(b"[]", status=200)  # JSON-Liste statt Objekt
    result = client.list_knowledge()
    assert result == []
    assert client.last_knowledge_status == 200
    assert client.last_knowledge_body_ok is False, (
        "HTTP 200 mit einer JSON-Liste statt eines Objekts ist KEIN bestaetigt "
        "leeres Ergebnis -- last_knowledge_body_ok muss False sein"
    )


def test_list_knowledge_http_200_dict_body_is_confirmed():
    client = _client_with_fake_request(b'{"items": []}', status=200)
    result = client.list_knowledge()
    assert result == []
    assert client.last_knowledge_body_ok is True, "ein echtes leeres {items:[]} ist bestaetigt lesbar"


def test_get_model_http_200_unparseable_body_is_not_confirmed():
    client = _client_with_fake_request(b"not json at all", status=200)
    result = client.get_model("p1")
    assert result is None
    assert client.last_model_status == 200
    assert client.last_model_body_ok is False, (
        "HTTP 200 mit unparsebarem Koerper ist KEINE bestaetigte Auskunft -- "
        "last_model_body_ok muss False sein"
    )


# ── (B)-(D) _resolve_orphaned_kb_for_partial ────────────────────────────

class _FakeClient:
    """Minimaler Double mit genau den Status-/Body-Attributen der echten
    `APIClient` -- steuert gezielt, welchen (Status, Koerper) `get_model`/
    `list_knowledge` 'gesehen' haben, ohne echten HTTP-Call."""

    def __init__(self, *, preset=None, model_status=404, model_body_ok=True,
                 knowledge=None, knowledge_status=200, knowledge_body_ok=True,
                 healthy=True):
        self._preset = preset
        self._model_status = model_status
        self._model_body_ok = model_body_ok
        self._knowledge = knowledge or []
        self._knowledge_status = knowledge_status
        self._knowledge_body_ok = knowledge_body_ok
        self._healthy = healthy
        self.last_model_status = None
        self.last_model_body_ok = None
        self.last_knowledge_status = None
        self.last_knowledge_body_ok = None

    def check_health(self):
        return self._healthy

    def get_model(self, model_id):
        self.last_model_status = self._model_status
        self.last_model_body_ok = self._model_body_ok
        return self._preset

    def list_knowledge(self):
        self.last_knowledge_status = self._knowledge_status
        self.last_knowledge_body_ok = self._knowledge_body_ok
        return self._knowledge


_CFG = {"project": "Proj", "kb_name": "Proj Wissensspeicher"}


def _resolve(client, cfg=_CFG):
    with mock.patch.object(launcher_mod, "_ensure_owui_env", return_value=True), \
         mock.patch.object(launcher_mod, "_openwebui_url", return_value="http://127.0.0.1:8080"), \
         mock.patch.object(launcher_mod, "_default_preset_id", return_value="p1"), \
         mock.patch.object(setup_mod, "APIClient", return_value=client):
        saved = dict(os.environ)
        os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
        try:
            return launcher_mod._resolve_orphaned_kb_for_partial(cfg)
        finally:
            os.environ.clear()
            os.environ.update(saved)


def test_knowledge_list_http_200_unreadable_body_is_unclear_not_absent():
    client = _FakeClient(
        preset=None, model_status=404, model_body_ok=True,
        knowledge=[], knowledge_status=200, knowledge_body_ok=False,
    )
    kind, value = _resolve(client)
    assert kind == "unclear", (
        f"HTTP 200 mit unlesbarem KB-Listen-Koerper ist KEINE bestaetigte Abwesenheit, war {kind!r}"
    )
    assert value, "ein unklarer Befund sollte einen druckbaren Kurzbefund liefern"


def test_knowledge_list_non_200_status_is_unclear():
    client = _FakeClient(
        preset=None, model_status=404, model_body_ok=True,
        knowledge=[], knowledge_status=500, knowledge_body_ok=True,
    )
    kind, _value = _resolve(client)
    assert kind == "unclear", "ein Nicht-200 auf die KB-Liste ist kein bestaetigtes Ergebnis"


def test_model_check_http_200_unreadable_body_is_unclear():
    client = _FakeClient(preset=None, model_status=200, model_body_ok=False)
    kind, _value = _resolve(client)
    assert kind == "unclear", "HTTP 200 mit unlesbarem Preset-Koerper ist weder 'gefunden' noch bestaetigt 404"


def test_ambiguous_multiple_matching_kbs_is_unclear_not_unique_kb():
    client = _FakeClient(
        preset=None, model_status=404, model_body_ok=True,
        knowledge=[
            {"id": "kb-1", "name": "Proj Wissensspeicher"},
            {"id": "kb-2", "name": "Proj Wissensspeicher"},
        ],
    )
    kind, _value = _resolve(client)
    assert kind == "unclear", "mehrere gleichnamige KBs sind mehrdeutig, kein eindeutiger orphaned-KB-Treffer"


def test_confirmed_absent_still_resolves_as_absent():
    """Gegenprobe: eine echte, lesbare 404+leere-KB-Liste-Antwort bleibt
    'absent' (kein falsches 'unclear' fuer den Normalfall)."""
    client = _FakeClient(preset=None, model_status=404, model_body_ok=True, knowledge=[])
    kind, _value = _resolve(client)
    assert kind == "absent", kind


# ── (E)/(F) echter [1]-Caller haelt vor Mutation an ─────────────────────

def _run_action_install_partial(*, resolve_result, first_state="partial", recheck_state="partial"):
    saved_env = dict(os.environ)
    os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
    os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
    os.environ["OPENROUTER_API_KEY"] = "sk-or-test-fake"
    try:
        with mock.patch.object(launcher_mod, "_detect_install_state",
                                side_effect=[first_state, recheck_state]), \
             mock.patch.object(launcher_mod, "_docker_ok", return_value=(True, "ok")), \
             mock.patch.object(launcher_mod, "_openwebui_ok", return_value=(True, "ok")), \
             mock.patch.object(launcher_mod, "_ensure_owui_env", return_value=True), \
             mock.patch.object(launcher_mod, "_openrouter_key_status", return_value=(True, "ok")), \
             mock.patch.object(setup_mod, "_update_env_file_preserving", return_value=True), \
             mock.patch.object(setup_mod, "_read_env_file",
                                return_value={"LITELLM_MASTER_KEY": "sk-litellm-test-fake"}), \
             mock.patch.object(launcher_mod, "_resolve_orphaned_kb_for_partial", return_value=resolve_result), \
             mock.patch.object(launcher_mod, "_confirm_reinstall_after_partial") as confirm_mock, \
             mock.patch.object(setup_mod, "complete_orphaned_kb_install") as complete_mock, \
             mock.patch.object(setup_mod, "run_setup") as run_setup_mock, \
             mock.patch.object(setup_mod, "ensure_litellm_autowire") as autowire_mock, \
             mock.patch.object(launcher_mod, "_prompt", return_value=""), \
             mock.patch.object(launcher_mod, "_pause"), \
             mock.patch.object(launcher_mod, "_litellm_ok", return_value=(True, "ok")):
            launcher_mod.action_install()
        return confirm_mock, complete_mock, run_setup_mock, autowire_mock
    finally:
        os.environ.clear()
        os.environ.update(saved_env)


def test_entry_check_unclear_halts_before_confirm_and_mutation():
    confirm_mock, complete_mock, run_setup_mock, _autowire_mock = _run_action_install_partial(
        resolve_result=("unclear", "mehrdeutig: 2 Treffer"),
        first_state="partial", recheck_state="partial",
    )
    assert confirm_mock.call_count == 0, (
        "unklar/mehrdeutig darf NICHT an den j-vorbelegten _confirm_reinstall_after_partial "
        "weitergereicht werden -- das waere eine vorbelegte Mutation auf Basis eines "
        "ungeklaerten Befunds"
    )
    assert complete_mock.call_count == 0
    assert run_setup_mock.call_count == 0, "unklarer Befund darf NIE in run_setup's destroy&recreate laufen"


def test_recheck_unclear_halts_before_confirm_and_mutation():
    """Derselbe Fix muss auch am WP1d-Re-Check-Caller (launcher.py, zweiter
    [1]-Zweig) greifen -- Eingangscheck 'fresh' (ohne Key), Re-Check (mit
    Key) liefert 'partial' + unklaren Befund."""
    confirm_mock, complete_mock, run_setup_mock, _autowire_mock = _run_action_install_partial(
        resolve_result=("unclear", "KB-Liste: HTTP 200 mit unlesbarem Körper"),
        first_state="fresh", recheck_state="partial",
    )
    assert confirm_mock.call_count == 0
    assert complete_mock.call_count == 0
    assert run_setup_mock.call_count == 0


def test_confirmed_absent_still_reaches_existing_confirm_path():
    """Gegenprobe (F): 'absent' bleibt der bisherige, ausdruecklich
    bestaetigte Confirm-Pfad -- kein Ueberreagieren der P3-Fix auf den
    weiterhin gueltigen Normalfall."""
    confirm_mock, complete_mock, _run_setup_mock, _autowire_mock = _run_action_install_partial(
        resolve_result=("absent", None),
        first_state="partial", recheck_state="partial",
    )
    assert complete_mock.call_count == 0
    assert confirm_mock.call_count >= 1, "bestaetigte Abwesenheit bleibt der richtige, ausdruecklich bestaetigte Weg"


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
