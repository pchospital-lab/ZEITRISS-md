#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n1_persona_api_default_2026_11_09.py — Delta-Test
für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N1 WP5b (PF3.persona).

Vorher brauchte `mmo_sim/adapters/factories.py:default_persona_driver_factory`
IMMER eine explizite `MMO_SIM_PERSONA_CLI`/`MMO_SIM_PERSONA_API_*`-Konfig;
ohne beides warf die Konstruktion "Persona-Anbindung nicht konfiguriert",
auch wenn lokal längst ein LiteLLM-Proxy eingerichtet war (derselbe, den
`setup.py:run_install_litellm` für den GM-Pfad nutzt). Fix: `factory()`
defaultet NUR am TUI-Normalweg (`profile is None` — der bewusst gewählte
Persona-Einladepfad in `mmo_sim/ui/tui.py:_cmd_local_round` ruft genau
diese Factory auf, Solo nie) auf die lokale LiteLLM-Route, wenn weder CLI
noch API-Env gesetzt sind, und persistiert den Default erhaltend nach
`~/.openwebui_env`.

Deckt:
  1. Kein Env, kein lokales LiteLLM → unverändertes Altverhalten (RuntimeError).
  2. Kein Env, LiteLLM lokal eingerichtet → Default wird gesetzt + persistiert.
  3. Explizite `MMO_SIM_PERSONA_CLI`-Wahl → NICHT überschrieben (Vorrang).
  4. Explizite `MMO_SIM_PERSONA_API_BASE_URL`-Wahl → NICHT überschrieben.
  5. Lab-Pfad (`profile="api"`) → Default läuft NICHT (nur TUI-Normalweg).

Double-Grenze (A4, offen gelegt): `setup.py` wird real importiert (kein
Fake-Modul) — `load_config`/`_litellm_routing_model_id` sind reine
Dateireads, kein Docker/Netzwerk. `repo_root` wird über den Test-Seam-
Parameter von `_maybe_default_local_persona_api_env` auf ein Tempverzeichnis
umgelenkt (NICHT das echte `scripts/litellm/.env`/`~/.openwebui_env` — nur
in Test 2/3/4/5 wird zusätzlich `Path.home` gemockt, um die echte Home-Datei
nicht zu berühren).

Pure Python, nur `assert`, echter Exitcode, kein Docker/Netzwerk."""
from __future__ import annotations

import functools
import importlib.util as _importlib_util_bootstrap
import json
import os
import shutil
import sys
import tempfile
import traceback
import unittest.mock as mock
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_SUPPORT_SCRIPT = _HERE / "_local_tokenhost_support_2026_11_14.py"

# N4-N1/I3.2: Fruehschutz MUSS installiert sein, BEVOR irgendein
# Produktmodul (hier insbesondere `mmo_sim.adapters.factories`) geladen
# wird -- `bootstrap_isolation` ist prozessweit idempotent (EIN
# Audithook, EINE geteilte Allowlist) und patcht `Path.home`/
# `Path.expanduser`/`os.path.expanduser` GLOBAL auf ein privates
# Verzeichnis, BEVOR irgendein Autoload-/Factorypfad unten laufen kann --
# das schuetzt insbesondere die NEGATIVE Factoryprobe (Test 1 unten), die
# frueher `Path.home()` unmaskiert erreichte (02_N4N1_ARBEITSAUFTRAG.md D).
_support_spec = _importlib_util_bootstrap.spec_from_file_location(
    "f1n1_local_tokenhost_support", _SUPPORT_SCRIPT
)
_support_mod = _importlib_util_bootstrap.module_from_spec(_support_spec)
sys.modules["f1n1_local_tokenhost_support"] = _support_mod
_support_spec.loader.exec_module(_support_mod)
EARLY_GUARD = _support_mod.bootstrap_isolation(
    private_home=tempfile.gettempdir(),
    private_root=tempfile.gettempdir(),
    real_home=str(Path.home()),
    repo_root=str(_REPO_ROOT),
)

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.adapters import factories as factories_mod  # noqa: E402


def _isolated_repo_root(tmp_repo_root: Path):
    """I3.2: bindet den vorhandenen `repo_root`-Testseam BEIDER interner
    Autoload-Funktionen auf `tmp_repo_root`, OHNE deren reale
    Entscheidungslogik durch ein Erfolgsdouble zu ersetzen --
    `functools.partial` schliesst ueber der ECHTEN (noch unveraenderten)
    Funktion, nur der Default-Parameter `repo_root` wird vorbelegt. Das
    behebt genau die Luecke, dass `factory()`/`default_persona_driver_
    factory(data_dir=tmp)` diese beiden Funktionen intern OHNE
    `repo_root`-Argument aufruft und sie dadurch (unmaskiert) den echten,
    aus `__file__` ermittelten Repo-Root -- und damit potenziell die
    echte `scripts/litellm/.env`/`~/.openwebui_env` -- erreichen wuerden.
    Liefert ein Patch-Kontextmanager-Paar zum Zuruecksetzen."""
    return mock.patch.multiple(
        factories_mod,
        _maybe_default_local_tokenhost_persona_env=functools.partial(
            factories_mod._maybe_default_local_tokenhost_persona_env, repo_root=tmp_repo_root,
        ),
        _maybe_default_local_persona_api_env=functools.partial(
            factories_mod._maybe_default_local_persona_api_env, repo_root=tmp_repo_root,
        ),
    )


def _make_fake_repo(with_litellm_env: bool, master_key: str = "sk-litellm-test-fake-not-real") -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="f1-n1-persona-default-"))
    (tmp / "setup.json").write_text(json.dumps({
        "project": "f1n1test",
        "default_variant": "sonnet",
        "variants": {"sonnet": {"preset_id": "f1n1test-sonnet"}},
        "litellm": {"port": 4321},
    }), encoding="utf-8")
    lite_dir = tmp / "scripts" / "litellm"
    lite_dir.mkdir(parents=True)
    if with_litellm_env:
        (lite_dir / ".env").write_text(
            f"OPENROUTER_API_KEY=sk-or-fake\nLITELLM_MASTER_KEY={master_key}\n",
            encoding="utf-8",
        )
    # `_maybe_default_local_persona_api_env` does `import setup` after
    # inserting `<repo_root>/scripts` into sys.path -- in production
    # `repo_root` IS the real checkout, so the real `scripts/setup.py` is
    # found there. This test fakes `repo_root` as a tempdir, so the real
    # `scripts/setup.py` (stdlib-only, no project-internal imports) is
    # copied in to keep that lookup working without touching the real repo.
    shutil.copy(_REPO_ROOT / "scripts" / "setup.py", tmp / "scripts" / "setup.py")
    return tmp


def _clear_persona_env():
    saved = {}
    for k in ("MMO_SIM_PERSONA_CLI", "MMO_SIM_PERSONA_API_BASE_URL",
              "MMO_SIM_PERSONA_API_KEY", "MMO_SIM_PERSONA_API_MODEL"):
        saved[k] = os.environ.pop(k, None)
    return saved


def _restore_env(saved: dict):
    for k, v in saved.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


def test_no_default_without_local_litellm_keeps_old_runtime_error():
    """I3.2 negative tatsaechliche Factoryprobe: VORHER erreichte
    `factory("p1")` -> `_maybe_default_local_tokenhost_persona_env()`/
    `_maybe_default_local_persona_api_env()` OHNE jedes `repo_root`-
    Argument -- `data_dir=tmp` ersetzt NICHT den intern aus `__file__`
    ermittelten echten Repo-Root, und ohne diesen Test-Patch hier haette
    dieser Pfad potenziell die ECHTE `scripts/litellm/.env`/
    `~/.openwebui_env` erreicht (02_N4N1_ARBEITSAUFTRAG.md D). Isoliert
    jetzt BEIDE Eingaenge (Home via `bootstrap_isolation`-Baseline +
    hier zusaetzlich explizit gemocktem `Path.home`, Repo-Root via
    `_isolated_repo_root`) UND laesst die reale Entscheidungslogik
    (RuntimeError bei fehlendem lokalem LiteLLM) unveraendert laufen --
    kein Erfolgsdouble fuer die geprueften Funktionen selbst."""
    tmp = _make_fake_repo(with_litellm_env=False)
    saved = _clear_persona_env()
    fake_home = Path(tempfile.mkdtemp(prefix="f1-n1-persona-negative-home-"))
    try:
        with mock.patch.object(factories_mod.Path, "home", return_value=fake_home), \
             _isolated_repo_root(tmp):
            factory = factories_mod.default_persona_driver_factory(tmp)
            raised = False
            try:
                factory("p1")
            except RuntimeError as exc:
                raised = True
                assert "Persona-Anbindung nicht konfiguriert" in str(exc), str(exc)
            assert raised, "ohne lokales LiteLLM UND ohne Env haette die alte Fehlermeldung kommen muessen"
    finally:
        _restore_env(saved)
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(fake_home, ignore_errors=True)


def test_default_applied_and_persisted_when_litellm_locally_configured():
    tmp = _make_fake_repo(with_litellm_env=True, master_key="sk-litellm-abc123")
    saved = _clear_persona_env()
    fake_home_env = Path(tempfile.mkdtemp(prefix="f1-n1-persona-home-")) / ".openwebui_env"
    try:
        with mock.patch.object(factories_mod.Path, "home", return_value=fake_home_env.parent):
            factories_mod._maybe_default_local_persona_api_env(repo_root=tmp)
        assert os.environ.get("MMO_SIM_PERSONA_API_BASE_URL") == "http://127.0.0.1:4321/v1", \
            os.environ.get("MMO_SIM_PERSONA_API_BASE_URL")
        assert os.environ.get("MMO_SIM_PERSONA_API_KEY") == "sk-litellm-abc123"
        assert os.environ.get("MMO_SIM_PERSONA_API_MODEL") == "f1n1test-sonnet"
        assert fake_home_env.is_file(), "Default haette nach ~/.openwebui_env persistiert werden muessen"
        persisted = fake_home_env.read_text(encoding="utf-8")
        assert "MMO_SIM_PERSONA_API_BASE_URL=http://127.0.0.1:4321/v1" in persisted, persisted
        assert "MMO_SIM_PERSONA_API_KEY=sk-litellm-abc123" in persisted, persisted
    finally:
        _restore_env(saved)
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(fake_home_env.parent, ignore_errors=True)


def test_explicit_cli_choice_is_never_overridden():
    """I3.2 explizite CLI-Probe: `repo_root=tmp` ist hier bereits direkt
    gebunden (vorhandener Seam) -- `Path.home` wird zusaetzlich explizit
    auf ein privates Tempverzeichnis gemockt, damit auch ein spaeterer
    Codepfad innerhalb der Funktion nie den echten Home-Wert erreichen
    kann (ALLE Eingaenge privat isolieren, nicht nur die aktuell
    getroffenen Zweige)."""
    tmp = _make_fake_repo(with_litellm_env=True)
    saved = _clear_persona_env()
    os.environ["MMO_SIM_PERSONA_CLI"] = "claude"
    fake_home = Path(tempfile.mkdtemp(prefix="f1-n1-persona-cli-home-"))
    try:
        with mock.patch.object(factories_mod.Path, "home", return_value=fake_home):
            factories_mod._maybe_default_local_persona_api_env(repo_root=tmp)
        assert os.environ.get("MMO_SIM_PERSONA_API_BASE_URL") is None, (
            "eine bewusste CLI-Wahl haette NICHT durch den API-Default ergaenzt/"
            "ueberschrieben werden duerfen"
        )
        assert os.environ.get("MMO_SIM_PERSONA_CLI") == "claude"
    finally:
        _restore_env(saved)
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(fake_home, ignore_errors=True)


def test_explicit_api_choice_is_never_overridden():
    """I3.2 explizite API-Probe: siehe Docstring der CLI-Probe oben --
    `repo_root=tmp` ist bereits direkt gebunden, `Path.home` wird
    zusaetzlich explizit privat isoliert."""
    tmp = _make_fake_repo(with_litellm_env=True)
    saved = _clear_persona_env()
    os.environ["MMO_SIM_PERSONA_API_BASE_URL"] = "https://my-own-provider.example/v1"
    fake_home = Path(tempfile.mkdtemp(prefix="f1-n1-persona-api-home-"))
    try:
        with mock.patch.object(factories_mod.Path, "home", return_value=fake_home):
            factories_mod._maybe_default_local_persona_api_env(repo_root=tmp)
        assert os.environ.get("MMO_SIM_PERSONA_API_BASE_URL") == "https://my-own-provider.example/v1", (
            "eine bewusste, bereits gesetzte API-Base-URL haette Vorrang haben muessen"
        )
    finally:
        _restore_env(saved)
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(fake_home, ignore_errors=True)


def test_lab_profile_path_never_triggers_default():
    """profile="api" (Lab-Headless-Pfad) ruft `_maybe_default_local_persona_
    api_env` NICHT auf -- nur `profile is None` (TUI-Normalweg) tut das.
    Direkter Verhaltenstest ueber die `factory()`-Closure: mit lokal
    eingerichtetem LiteLLM, aber explizit profile='api' und fehlendem
    MMO_SIM_PERSONA_API_BASE_URL, muss weiterhin der alte LabConfigError-
    Pfad greifen (RuntimeError aus Zeile ~55-60 in factories.py), NICHT der
    neue Default.

    I3.2 "jeder weitere Autoloadpfad": `Path.home` wird zusaetzlich
    explizit privat isoliert UND `repo_root` ueber `_isolated_repo_root`
    gebunden -- beide Aufrufe laufen hier wegen `profile="api"` ohnehin
    nie (s. `spy.assert_not_called()`), die Isolation bleibt trotzdem als
    Sicherheitsnetz bestehen, falls sich das je aendert."""
    tmp = _make_fake_repo(with_litellm_env=True)
    saved = _clear_persona_env()
    fake_home = Path(tempfile.mkdtemp(prefix="f1-n1-persona-lab-home-"))
    try:
        with mock.patch.object(factories_mod.Path, "home", return_value=fake_home), \
             _isolated_repo_root(tmp), \
             mock.patch.object(factories_mod, "_maybe_default_local_persona_api_env") as spy:
            factory = factories_mod.default_persona_driver_factory(tmp, profile="api")
            raised = False
            try:
                factory("p1")
            except RuntimeError as exc:
                raised = True
                assert "MMO_SIM_PERSONA_API_BASE_URL" in str(exc), str(exc)
            assert raised, "Lab-Pfad ohne API-Env haette weiterhin RuntimeError werfen muessen"
            spy.assert_not_called()
    finally:
        _restore_env(saved)
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(fake_home, ignore_errors=True)


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
