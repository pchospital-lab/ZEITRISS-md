#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_register_existing_person.py — R6 (Korrekturzyklus
1, T-Befund 3, UX02/UX07), ZEITRISS Terminal UX-1.

Vorher erzeugte ein erneutes 'registrieren' mit demselben Anzeigenamen
(z.B. nach Ctrl-C + Neustart, `tester/out/BEDIENPROBE.md` Aufgabe 7)
stillschweigend eine ZWEITE, komplett neue Teilnehmer-ID unter demselben
Namen -- es gab keinen sichtbaren Weg zurueck zur eigenen, zuvor
registrierten (noch figurlosen) Person, ohne eine technische ID zu
kennen.

Dieser Test beweist: `registrieren` mit einem bereits bekannten
Anzeigenamen erkennt die bestehende Person (reine Lesefunktion
`ParticipantRegistry.find_by_display_name`, s. `worker/SCOPE-MAP-2.md`)
und bietet "als bestehende Person fortsetzen" an -- bei Bestaetigung
entsteht KEINE zweite ID, die Fokusuebernahme laeuft auf der BEREITS
BEKANNTEN ID.

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs."""
from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.ui.tui import TuiSession  # noqa: E402
from mmo_sim.registry.participants import ParticipantRegistry  # noqa: E402


def _scripted_input(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


def test_find_by_display_name_pure_read_returns_existing_match():
    """Erhaltungsprobe fuer die neue Lesefunktion selbst (keine Autoritaets-
    /Ownership-Aenderung, kein Write)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        registry = ParticipantRegistry(d / "registry")
        assert registry.find_by_display_name("Testperson7") == []
        created = registry.register_participant(kind="human", display_name="Testperson7")
        matches = registry.find_by_display_name("Testperson7")
        assert len(matches) == 1, matches
        assert matches[0].participant_id == created.participant_id
        # Case-insensitiv/getrimmt, aber kein Teilstring-Treffer.
        assert len(registry.find_by_display_name("  testperson7  ")) == 1
        assert registry.find_by_display_name("Testperson") == []


def test_re_register_same_name_after_simulated_restart_offers_existing_no_duplicate():
    """R6 Kernassertion: zwei unabhaengige `TuiSession`-'Prozesse' (echter
    simulierter Neustart ueber denselben `registry_dir`) -- der zweite
    Lauf registriert 'Testperson7' erneut, bestaetigt die Fortsetzung als
    bestehende Person -- es entsteht KEINE zweite ID."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        registry_dir = d / "registry"

        # "Prozess 1": Erstregistrierung.
        printed_1: list[str] = []
        session1 = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="original-human",
            input_fn=_scripted_input(["Testperson7", "n"]),  # Name, Fokus NICHT uebernehmen
            print_fn=printed_1.append,
        )
        session1._cmd_register_new_person()
        humans_after_1 = session1._local_round_list_humans()
        first_ids = [pid for pid, name in humans_after_1 if name == "Testperson7"]
        assert len(first_ids) == 1, humans_after_1
        first_pid = first_ids[0]

        # "Prozess 2" (simulierter Neustart, NEUE TuiSession, derselbe
        # registry_dir): erneutes 'registrieren' mit demselben Namen.
        printed_2: list[str] = []
        session2 = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="original-human",
            input_fn=_scripted_input([
                "Testperson7",  # derselbe Name
                "j",            # "als bestehende Person fortsetzen?" -> ja
                "n",            # Fokusuebernahme NICHT bestaetigen (haelt den Test einfach)
            ]),
            print_fn=printed_2.append,
        )
        session2._cmd_register_new_person()

        assert any("Bereits bekannt" in p for p in printed_2), printed_2
        assert any("Fortsetzung als bestehende Person" in p for p in printed_2), printed_2
        assert not any("Neu registriert" in p for p in printed_2), printed_2

        humans_after_2 = session2._local_round_list_humans()
        testperson7_ids = {pid for pid, name in humans_after_2 if name == "Testperson7"}
        # Kernassertion: GENAU EINE ID fuer 'Testperson7', keine stille Dublette.
        assert testperson7_ids == {first_pid}, humans_after_2


def test_re_register_same_name_declining_existing_still_creates_second_registration():
    """Erhaltungsprobe: lehnt der Nutzer die Fortsetzung als bestehende
    Person ausdruecklich ab ('n'), bleibt die bewusste Neu-Registrierung
    (wie vorher) moeglich -- keine erzwungene Zusammenfuehrung."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        session1 = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="original-human",
            input_fn=_scripted_input(["Mehrfachname", "n"]),
            print_fn=lambda *_a: None,
        )
        session1._cmd_register_new_person()

        printed_2: list[str] = []
        session2 = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="original-human",
            input_fn=_scripted_input(["Mehrfachname", "n", "n"]),  # Name, NICHT fortsetzen, NICHT Fokus
            print_fn=printed_2.append,
        )
        session2._cmd_register_new_person()
        assert any("Neu registriert" in p for p in printed_2), printed_2

        humans = session2._local_round_list_humans()
        ids = {pid for pid, name in humans if name == "Mehrfachname"}
        assert len(ids) == 2, humans


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
