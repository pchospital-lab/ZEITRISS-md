#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n2_env_writer_honesty_2026_11_09.py — Delta-Test
für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N2 WP-N2-1e (P1d).

Vorher behandelte `scripts/setup.py:_update_env_file_preserving` einen
Lesefehler einer EXISTIERENDEN Datei wie eine leere Datei ("baue neu") --
fremde Felder/Kommentare gingen dabei unwiderruflich verloren. Ein
chmod(0o600)-Fehlschlag wurde stumm als Erfolg (`return True`) behandelt,
obwohl die Datei dann NICHT mit den erwarteten Rechten geschützt ist.

Deckt:
  (A) Existierende, aber nicht lesbare Datei -> Funktion gibt `False`
      zurück UND lässt die Datei bytegleich unangetastet (kein "baue
      neu"-Überschreiben).
  (B) chmod(0o600) wirft `OSError` -> Funktion gibt `False` zurück, auch
      wenn der Schreibschritt selbst gelungen ist (ehrliche Rechteaussage).
  (C) Gegenprobe: normaler Erfolgsfall (lesbar, Schreiben+chmod klappen)
      bleibt `True`, unbekannte Felder/Kommentare bleiben erhalten.

Double-Grenze (A4, offen gelegt): `Path.read_text`/`Path.chmod` werden
gezielt mit `unittest.mock.patch.object` auf echten temporären Dateien
gedoubelt, um die Fehlerpfade ohne Dateisystem-Berechtigungstricks
(portabel, auch als root) zu erzwingen. Keine Netzwerk-/Docker-Calls."""
from __future__ import annotations

import importlib.util
import tempfile
import traceback
import unittest.mock as mock
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_SETUP_PY = _REPO_ROOT / "scripts" / "setup.py"

_spec = importlib.util.spec_from_file_location(
    "f1_n2_env_writer_honesty_setup_under_test", _SETUP_PY,
)
setup_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(setup_mod)


def test_unreadable_existing_file_is_not_rebuilt_returns_false():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / ".env"
        original = "# Kommentar\nFOO=bar\nOPENWEBUI_API_KEY=old-value\n"
        path.write_text(original, encoding="utf-8")

        with mock.patch.object(Path, "read_text", side_effect=OSError("Permission denied")):
            ok = setup_mod._update_env_file_preserving(path, {"OPENWEBUI_API_KEY": "new-value"})

        assert ok is False, "Lesefehler einer existierenden Datei darf NICHT als Erfolg gelten"
        # bytegleich erhalten -- kein "baue neu"-Überschreiben.
        assert path.read_text(encoding="utf-8") == original, (
            "Datei wurde trotz Lesefehler veraendert -- fremde Felder waeren verloren gegangen"
        )


def test_chmod_failure_returns_false_even_though_write_succeeded():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / ".env"

        with mock.patch.object(Path, "chmod", side_effect=OSError("chmod not permitted")):
            ok = setup_mod._update_env_file_preserving(path, {"OPENWEBUI_API_KEY": "new-value"})

        assert ok is False, "chmod-Fehlschlag darf NICHT stumm als Erfolg (True) gelten"
        # Der Inhalt selbst wurde trotzdem geschrieben -- kein Datenverlust,
        # nur die Rechteaussage ist jetzt ehrlich falsch/offen.
        assert "OPENWEBUI_API_KEY=new-value" in path.read_text(encoding="utf-8")


def test_normal_success_path_preserves_unknown_fields_and_returns_true():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / ".env"
        path.write_text("# Kommentar\nFREMDES_FELD=bleibt\nOPENWEBUI_API_KEY=old\n", encoding="utf-8")

        ok = setup_mod._update_env_file_preserving(path, {"OPENWEBUI_API_KEY": "new-value"})

        assert ok is True
        content = path.read_text(encoding="utf-8")
        assert "FREMDES_FELD=bleibt" in content, "unbekannte Felder muessen erhalten bleiben"
        assert "OPENWEBUI_API_KEY=new-value" in content
        assert "# Kommentar" in content


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
