#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_w10_figur_prompt_steuervertrag_2026_10_05.py — W10,
C2-bestaetigter MUSS-Blocker (UX04/UX05 Steuervertrag am Figur-Wahl-Prompt
in `_cmd_register_new_person`, `mmo_sim/ui/tui.py`).

Deckt genau die zwei im C2-Urteil benannten Maengel am Prompt "Fuer diese
Person [n] Figur erschaffen oder [i] importieren: " ab:

1. Der Prompt nutzte vorher einen rohen `_readline` -- '/stand', '?'/
   '/hilfe', '/verlauf', '/zurueck', '/abbrechen', '/pause' wurden dort
   NICHT als Steuerzeilen erkannt (verletzt den an 02 §C/7 anderen Stellen
   bereits korrekt umgesetzten Steuervertrag).
2. Beim Re-Fokus einer Person, die BEREITS eine Figur hat (z.B. 'Ben'/
   CHR-BEN), behauptete der Abbruchpfad faelschlich "Person bleibt ohne
   eigene Figur registriert" -- die Meldung muss den tatsaechlichen
   Figurstatus nennen.

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

from mmo_sim.domain.zeitriss import catalog  # noqa: E402
from mmo_sim.registry.participants import ParticipantRegistry  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402


def _scripted_input(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


def _register_ben_with_figure(d: Path) -> str:
    """Legt 'Ben' bereits registriert UND mit einer eigenen Figur an --
    genau der im C2-Urteil benannte Re-Fokus-Fall ('Ben'/CHR-BEN)."""
    registry = ParticipantRegistry(d / "registry")
    ben = registry.register_participant(kind="human", display_name="Ben")
    catalog.register(
        d / "catalog",
        catalog.CatalogEntry(
            participant_id=ben.participant_id,
            chrononaut_id="CHR-BEN",
            persona_key=ben.participant_id,
            display_name="Ben",
        ),
    )
    return ben.participant_id


def test_refocus_person_with_figure_stand_help_and_empty_do_not_claim_no_figure():
    """'/stand', '?' und eine leere Eingabe am Figur-Prompt duerfen bei einer
    Person MIT vorhandener Figur weder einen Abbruch ausloesen noch
    faelschlich 'ohne eigene Figur' behaupten -- Kontexthilfe/Stand werden
    gezeigt (kein Zugverbrauch, Prompt bleibt faktisch bestehen, da
    `_readline_with_controls` intern weiterliest), danach bleibt die Figur
    erhalten und der abschliessende Hinweis nennt das korrekt."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        ben_pid = _register_ben_with_figure(d)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="original-human",
            input_fn=_scripted_input([
                "Ben",          # Name -> findet die bereits registrierte Person
                "j",            # "Als bestehende Person fortsetzen?" bestaetigen
                "j",            # Fokusuebernahme bestaetigen (_local_round_handoff)
                "/stand",       # Steuerzeile am Figur-Prompt -- KEIN Verbrauch/Abbruch
                "?",            # Steuerzeile am Figur-Prompt -- KEIN Verbrauch/Abbruch
                "",             # leere Eingabe -- kein n/i, aber Figur ist vorhanden
            ]),
            print_fn=printed.append,
        )
        session._cmd_register_new_person()

        # Fokus korrekt zurueck, kein Haengenbleiben im fremden Fokus.
        assert session.participant_id == "original-human"

        # '?' wurde als Steuerzeile erkannt (Kontexthilfe gezeigt), nicht als
        # woertliche (ungueltige) Figur-Wahl.
        assert any("Hilfe (Figur erschaffen oder importieren)" in p for p in printed), printed

        # Die FALSCHE Meldung darf an KEINER Stelle erscheinen -- Ben hat
        # bereits eine Figur.
        assert not any("ohne eigene Figur" in p for p in printed), printed

        # Stattdessen die zustandsrichtige Meldung: Figur bleibt erhalten.
        assert any(
            "vorhandene Figur dieser Person bleibt erhalten" in p for p in printed
        ), printed

        # Die Figur selbst ist unangetastet geblieben (keine Loeschung/Aenderung).
        entries = catalog.list_for_participant(d / "catalog", ben_pid)
        assert len(entries) == 1 and entries[0].chrononaut_id == "CHR-BEN", entries


def test_refocus_person_with_figure_abbrechen_and_zurueck_clean_abort_figure_retained():
    """'/abbrechen' und '/zurueck' am Figur-Prompt brechen sauber ab (kein
    Erschaffungs-/Importvorgang gestartet) und benennen korrekt, dass die
    vorhandene Figur erhalten bleibt -- fuer BEIDE Steuerzeilen einzeln."""
    for control_token in ("/abbrechen", "/zurueck"):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            ben_pid = _register_ben_with_figure(d)
            printed: list[str] = []
            session = TuiSession(
                onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="original-human",
                input_fn=_scripted_input(["Ben", "j", "j", control_token]),
                print_fn=printed.append,
            )
            session._cmd_register_new_person()

            assert session.participant_id == "original-human"
            assert not any("ohne eigene Figur" in p for p in printed), (control_token, printed)
            assert any(
                "vorhandene Figur dieser Person bleibt erhalten" in p for p in printed
            ), (control_token, printed)
            assert any("Fokus zurueck bei 'original-human'" in p for p in printed), printed

            entries = catalog.list_for_participant(d / "catalog", ben_pid)
            assert len(entries) == 1 and entries[0].chrononaut_id == "CHR-BEN", entries


def test_truly_new_person_without_figure_keeps_correct_ohne_figur_message():
    """Regressionsschutz: eine WIRKLICH neue Person ohne jede Figur bekommt
    bei leerer Eingabe am Figur-Prompt weiterhin die (dort korrekte)
    bisherige Aussage -- die Zustandsbindung darf diesen Fall nicht
    veraendern."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="original-human",
            input_fn=_scripted_input([
                "Ganz Neue Person",  # echte Neuregistrierung, kein bestehender Treffer
                "j",                 # Fokusuebernahme bestaetigen
                "",                  # kein n/i -- Person hat keine Figur
            ]),
            print_fn=printed.append,
        )
        session._cmd_register_new_person()

        assert session.participant_id == "original-human"
        assert any(
            "Kein Erschaffungs-/Importweg gewaehlt -- Person bleibt ohne eigene Figur registriert." in p
            for p in printed
        ), printed

        humans = session._local_round_list_humans()
        new_ids = [pid for pid, name in humans if name == "Ganz Neue Person"]
        assert len(new_ids) == 1, humans
        assert catalog.list_for_participant(d / "catalog", new_ids[0]) == []


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
