#!/usr/bin/env python3
"""
tests/mmo_sim/test_r4_u1_numbered_menu_2026_11_07.py
ZR-VOLLENDUNG-OHNE-LAN-NACHZUG-20261107-R4 (U1, GENERAL-REVIEW F1).

Der General wies R3 zurueck, weil das Hauptmenue zwar Optionen zeigte, aber
KEINE Nummernauswahl bediente ("gedruckte Nummern, die keine Aktionen
ausloesen"). Dieser Test beweist am echten `TuiSession.run()`-Loop:

* Eine ALLEINSTEHENDE Nummer waehlt den n-ten sichtbaren Hauptmenueeintrag
  und loest GENAU dieselbe reale Aktion aus wie sein Wortalias
  (`boot_menu_entries` ist die eine geordnete Quelle fuer Anzeige UND
  Dispatch -- kein zweiter Pfad, keine Nummer ohne Handler).
* Eine inzwischen ungueltige Nummer erklaert sich ehrlich und zeigt das
  Menue erneut, ohne eine fremde Aktion auszuloesen.

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs.
Kein Netz, kein Modellaufruf, kein Produktzustandsschreiben ausserhalb der
Temp-Dirs."""
from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.ui.tui import TuiSession, boot_menu_entries  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


def _scripted_input(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


def _run(lines: list[str]) -> list[str]:
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(lines), print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
        )
        rc = session.run()
        assert rc == 0, (rc, printed)
        return printed


def test_entries_order_host_no_resume_is_stable():
    """Die sichtbare Nummerierung haengt an `boot_menu_entries`. Host ohne
    Stand: [1 spielen, 2 charaktere, 3 tisch, 4 registrieren, 5 einstellungen,
    6 beenden]."""
    keys = [k for k, _ in boot_menu_entries(has_resume=False, host_capable=True)]
    assert keys == ["spielen", "charaktere", "tisch", "registrieren", "einstellungen", "beenden"], keys
    # Gast: identische Reihenfolge (spielen bleibt sichtbar, aber als nicht
    # verfuegbar markiert -- die Nummer bleibt rollengerecht belegt).
    gkeys = [k for k, _ in boot_menu_entries(has_resume=False, host_capable=False)]
    assert gkeys == keys, gkeys


def test_number_5_triggers_same_action_as_word_einstellungen():
    """Nummer 5 (Einstellungen) loest dieselbe echte Aktion aus wie das Wort
    'einstellungen' -- beide Wege drucken den realen `_cmd_settings`-Kopf."""
    by_number = _run(["5", "beenden"])
    by_word = _run(["einstellungen", "beenden"])
    assert any("Teilnehmer-ID: p1" in p for p in by_number), by_number
    assert any("Teilnehmer-ID: p1" in p for p in by_word), by_word


def test_number_2_reaches_charaktere_menu():
    """Nummer 2 (Charaktere) erreicht wirklich das Charaktere-Untermenue --
    dieselbe Methode wie das Wort 'charaktere'."""
    by_number = _run(["2", "beenden"])
    by_word = _run(["charaktere", "beenden"])
    # Das Charaktere-Untermenue nennt sich selbst; der exakte Kopf ist fuer
    # beide Wege identisch, daher vergleichen wir die Mengen der Zeilen, die
    # nach dem Hauptmenue vor 'beenden' kamen, auf gemeinsame Charaktere-Marke.
    joined_n = "\n".join(by_number)
    joined_w = "\n".join(by_word)
    assert "harakter" in joined_n, by_number
    # Beide Wege erzeugen dieselbe Charaktere-Ausgabe (Nummer == Wort).
    assert ("harakter" in joined_w) and (joined_n.count("harakter") == joined_w.count("harakter")), (joined_n, joined_w)


def test_number_6_beenden_quits():
    """Nummer 6 (Beenden) beendet sauber (rc 0, kein weiterer Prompt)."""
    printed = _run(["6"])
    # Kein 'Unbekannte Auswahl' -- die Nummer wurde als Beenden erkannt.
    assert not any("Unbekannte Auswahl" in p for p in printed), printed


def test_invalid_number_explains_and_does_not_dispatch_foreign_action():
    """Eine zu grosse Nummer erklaert sich ehrlich und loest KEINE fremde
    Aktion aus; danach beendet 'beenden' reglaer."""
    printed = _run(["99", "beenden"])
    assert any("Ungueltige Nummer: 99" in p for p in printed), printed
    # Keine Einstellungen-/Charaktere-Nebenwirkung durch die Fehlzahl.
    assert not any("Teilnehmer-ID: p1" in p for p in printed), printed


def main() -> int:
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
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
