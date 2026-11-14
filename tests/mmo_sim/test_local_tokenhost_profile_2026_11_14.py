#!/usr/bin/env python3
"""tests/mmo_sim/test_local_tokenhost_profile_2026_11_14.py — ZR-LOCAL-TOKENHOST-L1,
Offline-Abnahme O1 (Auswahl, Persistenz, Wiederaufnahme).

Belegt gegen die echten Produktfunktionen des Worktrees:
  - `scripts/local_model_profile.py` (neuer Daten-/Validierungsresolver)
  - `scripts/setup.py:_read_env_file` / `_update_env_file_preserving`
    (bestehender erhaltender Schreibhelfer, wiederverwendet statt verdoppelt)
  - `scripts/setup.py:resolve_model_provider` / `_home_env_path`
  - `scripts/launcher.py:resolve_model_provider_choice` / `action_rekeys`

IO ausschliesslich an Grenzen kontrolliert: private Tempdateien statt
`~/.openwebui_env`, `getpass.getpass`/`_prompt` monkeygepatcht. Die echte
Nutzerdatei wird in KEINEM Testfall geoeffnet -- `Path.home` wird nur fuer
den einen End-to-End-Test auf ein Tempverzeichnis umgelenkt, alle anderen
Tests uebergeben einen expliziten `env_path`.

unittest.TestCase, `python3 -m unittest discover` faehig; kein Netzwerk-/
Docker-/Modellzugriff."""
from __future__ import annotations

import importlib.util
import shutil
import stat
import sys
import tempfile
import unittest
import unittest.mock as mock
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
_SETUP_PY = _SCRIPTS_DIR / "setup.py"
_LAUNCHER_PY = _SCRIPTS_DIR / "launcher.py"
_LOCAL_PROFILE_PY = _SCRIPTS_DIR / "local_model_profile.py"

if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # dataclasses-Introspektion braucht den Modulnamen im Registry
    spec.loader.exec_module(mod)
    return mod


lmp = _load("o1_local_model_profile_under_test", _LOCAL_PROFILE_PY)
setup_mod = _load("o1_setup_under_test", _SETUP_PY)
launcher_mod = _load("o1_launcher_under_test", _LAUNCHER_PY)

FAKE_BASE_URL = "http://127.0.0.1:18001/v1"
FAKE_MODEL = "nemotron-3-super"
FAKE_TOKEN = "test-local-token-not-secret"  # noqa: S105 -- erkennbar unecht, s. 04


class LocalTokenhostProfileTests(unittest.TestCase):
    def setUp(self):
        self._tmp_dirs: list[Path] = []

    def tearDown(self):
        for d in self._tmp_dirs:
            shutil.rmtree(d, ignore_errors=True)

    def _tmp_env_path(self, prefix: str) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix=f"o1-{prefix}-"))
        self._tmp_dirs.append(tmp)
        return tmp / ".fake_openwebui_env"

    # ─── 1. Resolver pur: Validierung/Haltegruende ──────────────────────

    def test_resolve_provider_legacy_cloud_local_hold(self):
        # N1-03: fehlender Schluessel (Datei erwaehnt den Provider nie) ist
        # 'legacy'; ein ausdruecklich LEERER Schluessel (`KEY=`) ist KEIN
        # Legacyzustand mehr, sondern ein sichtbarer HOLD (vorher beide
        # faelschlich gleich behandelt).
        self.assertEqual(lmp.resolve_provider({}), "legacy")
        self.assertEqual(lmp.resolve_provider({"ZEITRISS_MODEL_PROVIDER": ""}), "hold")
        self.assertEqual(lmp.resolve_provider({"ZEITRISS_MODEL_PROVIDER": "cloud"}), "cloud")
        self.assertEqual(lmp.resolve_provider({"ZEITRISS_MODEL_PROVIDER": "LOCAL"}), "local")
        self.assertEqual(lmp.resolve_provider({"ZEITRISS_MODEL_PROVIDER": "weird-value"}), "hold")

    def test_resolve_local_profile_valid_defaults(self):
        env = {
            lmp.ENV_KEY_PROVIDER: "local",
            lmp.ENV_KEY_BASE_URL: FAKE_BASE_URL,
            lmp.ENV_KEY_MODEL: FAKE_MODEL,
            lmp.ENV_KEY_API_KEY: FAKE_TOKEN,
        }
        profile = lmp.resolve_local_profile(env)
        self.assertEqual(profile.base_url, FAKE_BASE_URL)
        self.assertEqual(profile.model, FAKE_MODEL)
        self.assertEqual(profile.api_key, FAKE_TOKEN)
        self.assertIsNone(profile.owui_base_url)
        self.assertEqual(profile.gm_max_tokens, lmp.DEFAULT_GM_MAX_TOKENS)
        self.assertEqual(profile.gm_max_tokens, 4096)
        self.assertEqual(profile.persona_max_tokens, lmp.DEFAULT_PERSONA_MAX_TOKENS)
        self.assertEqual(profile.persona_max_tokens, 400)

    def test_resolve_local_profile_negative_cases_hold_not_raise_generic(self):
        base = {
            lmp.ENV_KEY_BASE_URL: FAKE_BASE_URL,
            lmp.ENV_KEY_MODEL: FAKE_MODEL,
            lmp.ENV_KEY_API_KEY: FAKE_TOKEN,
        }

        def _expect_hold(overrides: dict, note: str):
            env = dict(base)
            env.update(overrides)
            with self.assertRaises(lmp.ProfileHold, msg=note):
                lmp.resolve_local_profile(env)

        _expect_hold({lmp.ENV_KEY_BASE_URL: ""}, "leere URL")
        _expect_hold({lmp.ENV_KEY_BASE_URL: "ftp://127.0.0.1:1/v1"}, "falsches Schema")
        _expect_hold({lmp.ENV_KEY_BASE_URL: "http://user:pw@127.0.0.1:1/v1"}, "eingebettetes Credential")
        _expect_hold({lmp.ENV_KEY_BASE_URL: "http://127.0.0.1:1/v1?token=x"}, "Query-Secret")
        _expect_hold({lmp.ENV_KEY_BASE_URL: "http://127.0.0.1:999999/v1"}, "ungueltiger Port")
        _expect_hold({lmp.ENV_KEY_MODEL: ""}, "leeres Modell")
        _expect_hold({lmp.ENV_KEY_MODEL: "a\r\nb"}, "CRLF im Modell")
        _expect_hold({lmp.ENV_KEY_API_KEY: ""}, "leerer Token")
        _expect_hold({lmp.ENV_KEY_API_KEY: "tok\x00en"}, "NUL im Token")
        _expect_hold({lmp.ENV_KEY_GM_MAX_TOKENS: "0"}, "GM-Limit 0")
        _expect_hold({lmp.ENV_KEY_GM_MAX_TOKENS: "-5"}, "GM-Limit negativ")
        _expect_hold({lmp.ENV_KEY_GM_MAX_TOKENS: "abc"}, "GM-Limit unlesbar")
        _expect_hold({lmp.ENV_KEY_PERSONA_MAX_TOKENS: "0"}, "Persona-Limit 0")
        _expect_hold({lmp.ENV_KEY_OWUI_BASE_URL: "not-a-url"}, "ungueltige OWUI-Basis")

    def test_negative_messages_never_contain_secret_value(self):
        env = {
            lmp.ENV_KEY_BASE_URL: FAKE_BASE_URL,
            lmp.ENV_KEY_MODEL: FAKE_MODEL,
            lmp.ENV_KEY_API_KEY: "",
        }
        with self.assertRaises(lmp.ProfileHold) as ctx:
            lmp.resolve_local_profile(env)
        self.assertNotIn(FAKE_TOKEN, str(ctx.exception))
        self.assertIn("ZEITRISS_LOCAL_API_KEY", str(ctx.exception))

    # ─── 2. Realer Schreib-/Readback-Pfad (setup.py-Helfer, keine Verdopplung) ──

    def test_write_readback_roundtrip_protected_0600_and_values_exact(self):
        env_path = self._tmp_env_path("roundtrip")
        updates = lmp.build_local_profile_updates(
            base_url=FAKE_BASE_URL, model=FAKE_MODEL, api_key=FAKE_TOKEN,
            gm_max_tokens=4096, persona_max_tokens=400,
        )
        ok = setup_mod._update_env_file_preserving(env_path, updates)
        self.assertTrue(ok)
        mode = stat.S_IMODE(env_path.stat().st_mode)
        self.assertEqual(mode, 0o600, f"erwartete 0600, bekam {oct(mode)}")

        # Frischer Reread -- kein In-Memory-Zustand des Schreibvorgangs wird
        # wiederverwendet.
        reread = setup_mod._read_env_file(env_path)
        profile = lmp.resolve_local_profile(reread)
        self.assertEqual(profile.base_url, FAKE_BASE_URL)
        self.assertEqual(profile.model, FAKE_MODEL)
        self.assertEqual(profile.api_key, FAKE_TOKEN)
        self.assertEqual(profile.gm_max_tokens, 4096)
        self.assertEqual(profile.persona_max_tokens, 400)
        self.assertEqual(reread[lmp.ENV_KEY_PROVIDER], "local")

        provider, profile2, reason = setup_mod.resolve_model_provider(env_path)
        self.assertEqual(provider, "local")
        self.assertIsNone(reason)
        # setup_mod importiert sein EIGENES `local_model_profile` (echter
        # sys.path-Import) -- andere Klassenidentitaet als das hier per
        # spec_from_file_location geladene `lmp`, daher Feldvergleich statt
        # Dataclass-`__eq__` (das `other.__class__ is self.__class__` prueft).
        self.assertEqual(profile2.base_url, profile.base_url)
        self.assertEqual(profile2.model, profile.model)
        self.assertEqual(profile2.api_key, profile.api_key)
        self.assertEqual(profile2.gm_max_tokens, profile.gm_max_tokens)
        self.assertEqual(profile2.persona_max_tokens, profile.persona_max_tokens)

    def test_preserves_foreign_fields_comments_and_cloud_values_on_local_write(self):
        env_path = self._tmp_env_path("preserve")
        env_path.parent.mkdir(parents=True, exist_ok=True)
        env_path.write_text(
            "# ein fremder Kommentar\n"
            "OPENWEBUI_URL=http://localhost:8080\n"
            "OPENWEBUI_API_KEY=owui-fake-key-abc\n"
            "OPENROUTER_API_KEY=sk-or-fake-old-key\n"
            "SOME_UNKNOWN_CUSTOM_VAR=bleibt-unberuehrt\n",
            encoding="utf-8",
        )
        updates = lmp.build_local_profile_updates(
            base_url=FAKE_BASE_URL, model=FAKE_MODEL, api_key=FAKE_TOKEN,
        )
        ok = setup_mod._update_env_file_preserving(env_path, updates)
        self.assertTrue(ok)
        content = env_path.read_text(encoding="utf-8")
        self.assertIn("# ein fremder Kommentar", content)
        self.assertIn("SOME_UNKNOWN_CUSTOM_VAR=bleibt-unberuehrt", content)
        self.assertIn("OPENWEBUI_API_KEY=owui-fake-key-abc", content)
        self.assertIn(
            "OPENROUTER_API_KEY=sk-or-fake-old-key", content,
            "OpenRouter-Key muss erhalten bleiben -- Local-Wahl loescht keine "
            "Cloud-Altwerte (02: alte Legacy-Personafelder bleiben erhalten).",
        )
        self.assertIn(FAKE_TOKEN, content)
        self.assertIn("ZEITRISS_LOCAL_API_KEY=", content)

    def test_reuse_enter_keeps_existing_local_profile_via_action_rekeys(self):
        """O1: 'Rekey mit Enter erhaelt die Auswahl' -- echter `action_rekeys`-
        Lauf, zweiter Aufruf mit nur Enter behaelt Token/URL/Modell unveraendert."""
        tmp_home = Path(tempfile.mkdtemp(prefix="o1-rekey-home-"))
        self._tmp_dirs.append(tmp_home)
        stdout_lines: list[str] = []

        def _capture_print(*args, **_kwargs):
            stdout_lines.append(" ".join(str(a) for a in args))

        with mock.patch.object(Path, "home", return_value=tmp_home), \
             mock.patch.object(launcher_mod, "_pause", return_value=None), \
             mock.patch("builtins.print", side_effect=_capture_print):
            prompts_1 = iter([
                "http://localhost:8080",  # OpenWebUI-URL (zuerst, unveraenderte Reihenfolge)
                "local",                  # Modell-Provider
                FAKE_BASE_URL,
                FAKE_MODEL,
                "",
            ])
            with mock.patch.object(launcher_mod, "_prompt", side_effect=lambda *_a, **_k: next(prompts_1)), \
                 mock.patch("getpass.getpass", side_effect=["owui-fake-key", FAKE_TOKEN]):
                launcher_mod.action_rekeys()

            env_path = tmp_home / ".openwebui_env"
            self.assertTrue(env_path.is_file())
            first_body = setup_mod._read_env_file(env_path)
            self.assertEqual(first_body[lmp.ENV_KEY_MODEL], FAKE_MODEL)
            self.assertEqual(first_body[lmp.ENV_KEY_API_KEY], FAKE_TOKEN)

            prompts_2 = iter(["", "", "", "", ""])
            with mock.patch.object(launcher_mod, "_prompt", side_effect=lambda *_a, **_k: next(prompts_2)), \
                 mock.patch("getpass.getpass", side_effect=["", ""]):
                launcher_mod.action_rekeys()

            second_body = setup_mod._read_env_file(env_path)
            self.assertEqual(second_body[lmp.ENV_KEY_MODEL], FAKE_MODEL)
            self.assertEqual(second_body[lmp.ENV_KEY_API_KEY], FAKE_TOKEN)
            self.assertEqual(second_body[lmp.ENV_KEY_PROVIDER], "local")

        joined_stdout = "\n".join(stdout_lines)
        self.assertNotIn(FAKE_TOKEN, joined_stdout, "Token darf nie in Terminalausgabe erscheinen.")

    def test_cloud_to_local_to_cloud_switch_fresh_reread_each_time(self):
        """O1/O6-Unterstuetzung: bewusster Rueckwechsel, jeweils FRISCH von der
        Platte gelesen (kein In-Memory-Rest eines frueheren Aufrufs)."""
        env_path = self._tmp_env_path("switch")
        cloud_updates = {"OPENWEBUI_URL": "http://localhost:8080", "OPENROUTER_API_KEY": "sk-or-fake-cloud"}
        self.assertTrue(setup_mod._update_env_file_preserving(env_path, cloud_updates))
        provider, _p, _r = setup_mod.resolve_model_provider(env_path)
        self.assertEqual(provider, "legacy")

        local_updates = lmp.build_local_profile_updates(base_url=FAKE_BASE_URL, model=FAKE_MODEL, api_key=FAKE_TOKEN)
        self.assertTrue(setup_mod._update_env_file_preserving(env_path, local_updates))
        provider, profile, _r = setup_mod.resolve_model_provider(env_path)
        self.assertEqual(provider, "local")
        self.assertEqual(profile.model, FAKE_MODEL)

        self.assertTrue(setup_mod._update_env_file_preserving(env_path, lmp.cloud_provider_updates()))
        provider, profile, _r = setup_mod.resolve_model_provider(env_path)
        self.assertEqual(provider, "cloud")
        self.assertIsNone(profile)
        reread = setup_mod._read_env_file(env_path)
        self.assertEqual(reread.get("OPENROUTER_API_KEY"), "sk-or-fake-cloud")
        self.assertEqual(
            reread.get(lmp.ENV_KEY_MODEL), FAKE_MODEL,
            "Lokale Felder bleiben in der Datei stehen -- ein spaeterer Rueckwechsel auf "
            "local braucht keine Neueingabe (cloud_provider_updates()-Vertrag).",
        )

        self.assertTrue(setup_mod._update_env_file_preserving(env_path, {lmp.ENV_KEY_PROVIDER: "local"}))
        provider, profile, _r = setup_mod.resolve_model_provider(env_path)
        self.assertEqual(provider, "local")
        self.assertEqual(profile.model, FAKE_MODEL)
        self.assertEqual(profile.api_key, FAKE_TOKEN)

    def test_unreadable_existing_file_not_replaced_write_fails_closed(self):
        env_path = self._tmp_env_path("unreadable")
        env_path.parent.mkdir(parents=True, exist_ok=True)
        env_path.write_text("OPENWEBUI_URL=http://localhost:8080\n", encoding="utf-8")
        env_path.chmod(0o000)
        try:
            ok = setup_mod._update_env_file_preserving(
                env_path,
                lmp.build_local_profile_updates(base_url=FAKE_BASE_URL, model=FAKE_MODEL, api_key=FAKE_TOKEN),
            )
            self.assertFalse(ok, "unlesbare Bestandsdatei darf NICHT neu gebaut werden.")
        finally:
            env_path.chmod(0o600)
        content = env_path.read_text(encoding="utf-8")
        self.assertEqual(content, "OPENWEBUI_URL=http://localhost:8080\n", "Datei muss bytegleich unangetastet bleiben.")

    def test_hold_blocks_launcher_choice_no_silent_cloud_fallback(self):
        env_path = self._tmp_env_path("hold")
        setup_mod._update_env_file_preserving(env_path, {"ZEITRISS_MODEL_PROVIDER": "quantum-local-ish"})
        provider, profile, reason = launcher_mod.resolve_model_provider_choice(env_path)
        self.assertEqual(provider, "hold")
        self.assertIsNone(profile)
        self.assertIsNone(reason)

        env_path2 = self._tmp_env_path("hold-incomplete")
        setup_mod._update_env_file_preserving(
            env_path2, {"ZEITRISS_MODEL_PROVIDER": "local", lmp.ENV_KEY_MODEL: FAKE_MODEL}
        )
        provider2, profile2, reason2 = launcher_mod.resolve_model_provider_choice(env_path2)
        self.assertEqual(provider2, "hold")
        self.assertIsNone(profile2)
        self.assertTrue(reason2 and lmp.ENV_KEY_BASE_URL in reason2)

    def test_cloud_litellm_traps_never_triggered_by_profile_resolution(self):
        """O1-Belegpflicht: Aufrufzaehler fuer Cloud-/LiteLLM-Fallen = 0 -- reine
        Profilaufloesung darf NIE `run_install_litellm`/`ensure_litellm_autowire`/
        `APIClient.test_model` beruehren."""
        calls = {"litellm_install": 0, "litellm_autowire": 0, "test_model": 0}

        def _trap_install(*_a, **_k):
            calls["litellm_install"] += 1
            raise AssertionError("run_install_litellm darf hier nicht aufgerufen werden")

        def _trap_autowire(*_a, **_k):
            calls["litellm_autowire"] += 1
            raise AssertionError("ensure_litellm_autowire darf hier nicht aufgerufen werden")

        def _trap_test_model(self_, *_a, **_k):
            calls["test_model"] += 1
            raise AssertionError("APIClient.test_model darf hier nicht aufgerufen werden")

        env_path = self._tmp_env_path("traps")
        updates = lmp.build_local_profile_updates(base_url=FAKE_BASE_URL, model=FAKE_MODEL, api_key=FAKE_TOKEN)
        with mock.patch.object(setup_mod, "run_install_litellm", _trap_install), \
             mock.patch.object(setup_mod, "ensure_litellm_autowire", _trap_autowire), \
             mock.patch.object(setup_mod.APIClient, "test_model", _trap_test_model):
            self.assertTrue(setup_mod._update_env_file_preserving(env_path, updates))
            provider, profile, reason = setup_mod.resolve_model_provider(env_path)
            self.assertEqual(provider, "local")
            self.assertEqual(profile.model, FAKE_MODEL)

        self.assertEqual(calls, {"litellm_install": 0, "litellm_autowire": 0, "test_model": 0})


if __name__ == "__main__":
    unittest.main()
