#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n1_preserving_env_writer_2026_11_09.py — Delta-Test
für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N1 WP1b (PF1.2/PF1.3).

Vorher bauten `launcher.py:action_rekeys` (`~/.openwebui_env`) UND
`setup.py:run_install_litellm` (LiteLLM-`.env`) ihre jeweilige Datei aus
nur 3–4 bekannten Feldern komplett NEU — jede andere Zeile (Kommentare,
unbekannte/fremde Felder, von einem anderen Tool gesetzte Variablen) ging
dabei verloren. Fix: EIN gemeinsamer Helfer
`setup.py:_update_env_file_preserving(path, updates, *, remove=...)`,
genutzt von drei Aufrufern (`launcher.py:action_install`, `action_rekeys`,
`setup.py:run_install_litellm`).

Deckt den Helfer direkt (A) und Aufrufer 2 (`action_rekeys`, B) ab.
Aufrufer 1 (`action_install`) und 3 (`run_install_litellm`) sind bereits
durch `test_f1_n1_cache_probe_optin_2026_11_09.py` (liest/schreibt die
echte LiteLLM-`.env` über den Helfer end-to-end) belegt.

Keine Secrets in den Assertions selbst sichtbar gemacht über das, was der
Helfer ohnehin schreibt — Testwerte sind erkennbar unecht ('fake'/'test').

Pure Python, nur `assert`, echter Exitcode, temporäre Verzeichnisse,
kein Docker/Netzwerk."""
from __future__ import annotations

import importlib.util
import stat
import sys
import tempfile
import traceback
import unittest.mock as mock
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_SETUP_PY = _REPO_ROOT / "scripts" / "setup.py"
_LAUNCHER_PY = _REPO_ROOT / "scripts" / "launcher.py"

_spec = importlib.util.spec_from_file_location(
    "f1_n1_preserving_env_writer_setup_under_test", _SETUP_PY,
)
setup_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(setup_mod)


def test_creates_new_file_with_given_fields():
    tmp = Path(tempfile.mkdtemp(prefix="f1-n1-preserving-env-"))
    target = tmp / ".fresh_env"
    try:
        ok = setup_mod._update_env_file_preserving(target, {"A": "1", "B": "2"})
        assert ok is True
        content = target.read_text(encoding="utf-8")
        assert "A=1" in content and "B=2" in content, content
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_preserves_unknown_fields_and_comments_on_update():
    tmp = Path(tempfile.mkdtemp(prefix="f1-n1-preserving-env-"))
    target = tmp / ".env"
    try:
        target.write_text(
            "# ein Kommentar, der erhalten bleiben soll\n"
            "KNOWN_FIELD=alt\n"
            "UNKNOWN_CUSTOM_VAR=bleib-unberuehrt\n"
            "export SOME_OTHER=wert\n",
            encoding="utf-8",
        )
        ok = setup_mod._update_env_file_preserving(target, {"KNOWN_FIELD": "neu"})
        assert ok is True
        content = target.read_text(encoding="utf-8")
        assert "# ein Kommentar, der erhalten bleiben soll" in content, content
        assert "KNOWN_FIELD=neu" in content, content
        assert "KNOWN_FIELD=alt" not in content, content
        assert "UNKNOWN_CUSTOM_VAR=bleib-unberuehrt" in content, (
            f"unbekanntes Feld haette erhalten bleiben muessen:\n{content}"
        )
        assert "export SOME_OTHER=wert" in content, content
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_remove_set_strips_named_keys_only():
    tmp = Path(tempfile.mkdtemp(prefix="f1-n1-preserving-env-"))
    target = tmp / ".env"
    try:
        target.write_text("KEEP=1\nDROP_ME=2\n", encoding="utf-8")
        ok = setup_mod._update_env_file_preserving(target, {}, remove={"DROP_ME"})
        assert ok is True
        content = target.read_text(encoding="utf-8")
        assert "KEEP=1" in content, content
        assert "DROP_ME" not in content, content
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_chmod_600_applied():
    tmp = Path(tempfile.mkdtemp(prefix="f1-n1-preserving-env-"))
    target = tmp / ".env"
    try:
        setup_mod._update_env_file_preserving(target, {"X": "y"})
        mode = stat.S_IMODE(target.stat().st_mode)
        assert mode == 0o600, f"erwartet chmod 600, war {oct(mode)}"
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_write_failure_returns_false_not_exception():
    tmp = Path(tempfile.mkdtemp(prefix="f1-n1-preserving-env-"))
    target = tmp / ".env"
    try:
        with mock.patch.object(type(target), "write_text", side_effect=OSError("disk full (simuliert)")):
            ok = setup_mod._update_env_file_preserving(target, {"X": "y"})
        assert ok is False, "ein Schreibfehler haette False liefern sollen, kein stiller Erfolg"
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_action_rekeys_uses_shared_helper_and_preserves_unrelated_field():
    """Aufrufer 2: `launcher.py:action_rekeys` nutzt denselben Helfer statt
    des alten 3-Zeilen-Neubaus -- ein unbekanntes Feld in `~/.openwebui_env`
    (hier simuliert ueber eine Tempdatei via `Path.home`-Mock) bleibt
    erhalten."""
    _lspec = importlib.util.spec_from_file_location(
        "f1_n1_preserving_env_writer_launcher_under_test", _LAUNCHER_PY,
    )
    launcher_mod = importlib.util.module_from_spec(_lspec)
    _lspec.loader.exec_module(launcher_mod)

    tmp_home = Path(tempfile.mkdtemp(prefix="f1-n1-preserving-env-home-"))
    home_env = tmp_home / ".openwebui_env"
    home_env.write_text(
        "# bestehende Datei\nOPENWEBUI_URL=http://old:8080\nOPENWEBUI_API_KEY=old-key\n"
        "UNKNOWN_FIELD=bleib-unberuehrt\n",
        encoding="utf-8",
    )
    try:
        with mock.patch.object(launcher_mod.Path, "home", return_value=tmp_home), \
             mock.patch.object(launcher_mod, "_prompt", side_effect=[
                 "http://localhost:8080",  # OpenWebUI-URL (Enter-Default haette alten Wert behalten)
             ]), \
             mock.patch("getpass.getpass", side_effect=[
                 "new-owui-key",   # OpenWebUI-API-Key
                 "",               # OpenRouter-Key: leer lassen
             ]), \
             mock.patch.object(launcher_mod, "_pause"):
            launcher_mod.action_rekeys()
        content = home_env.read_text(encoding="utf-8")
        assert "# bestehende Datei" in content, content
        assert "UNKNOWN_FIELD=bleib-unberuehrt" in content, (
            f"action_rekeys haette ein unbekanntes Feld erhalten muessen:\n{content}"
        )
        assert "OPENWEBUI_API_KEY=new-owui-key" in content, content
    finally:
        import shutil
        shutil.rmtree(tmp_home, ignore_errors=True)


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
