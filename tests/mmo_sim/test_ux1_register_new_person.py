#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_register_new_person.py — UX07 (ZEITRISS Terminal
UX-1, 02 §D.2): "Zweite NEUE menschliche Person bekommt im Terminal ihre
eigene Figur" -- das war die zentrale, im Auftrag benannte offene Luecke
(`[n]`/`[i]` haengen an der beim Prozessstart aufgelösten `participant_id`,
MENUE_ENTSCHEIDUNG.md U02).

Beweist den neuen Weg: 'registrieren' -> neue Person ueber die VORHANDENE
`ParticipantRegistry` -> bewusste Fokusuebernahme (`_local_round_handoff`,
bestehender Vertrag) -> Erschaffung UNTER GENAU dieser neuen ID -> Rueckkehr
zur urspruenglichen Identitaet, OHNE CLI-Neustart/`--participant`-Handarbeit.

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs."""
from __future__ import annotations

import json
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import upgrade_narrow_save  # noqa: E402

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import catalog  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
_FIXTURE_SAVE = json.loads(
    (_REPO_ROOT / "internal" / "qa" / "harness" / "lobby" / "fixtures" / "saves" / "sniper.json").read_text(encoding="utf-8")
)
# W63-Fix (R12-Restreparatur, 02_TESTVERTRAG.md "Bestehende unbekannte
# Source-Rohfixtures unveraendert lassen"): die Rohfixture `tech.json`
# selbst bleibt unangetastet (schmaler Legacy-Block, `_fixture_note`-Root-
# Key) -- als simuliertes SL-Erschaffungsergebnis durchlaeuft sie aber den
# echten `run_admitted_creation_dialog`-Harvestweg (BEIDE v7-Schemas,
# `additionalProperties:false`). `upgrade_narrow_save` (`_full_v7_fixture.py`,
# bereits etablierter Weg, s. `test_ux1_persona_factory_guard.py`) hebt sie
# auf einen vollen gueltigen Block, erhaelt dabei char_id/id="CHR-TECH-001",
# name="Kaede", callsign="TECH" unveraendert -- keine Identitaets-/Zaehl-
# aenderung, nur das Format.
_FIXTURE_SAVE_2 = upgrade_narrow_save(json.loads(
    (_REPO_ROOT / "internal" / "qa" / "harness" / "lobby" / "fixtures" / "saves" / "tech.json").read_text(encoding="utf-8")
))


def _scripted_input(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


class _FakeCreationGm:
    def __init__(self, save_block: dict):
        self._save_block = save_block
        self.calls: list[tuple[int, str]] = []

    def turn(self, idx, text):
        self.calls.append((idx, text))
        if len(self.calls) == 1:
            return {"content": "Wie beginnt deine Zeitreise?"}
        return {"content": "```json\n" + json.dumps(self._save_block) + "\n```"}


def test_new_person_gets_own_figure_under_exactly_her_own_id():
    """UX07 Kernnachweis: Registrierung + Import ueber 'registrieren' legt
    eine Figur unter der NEUEN Teilnehmer-ID ab -- NICHT unter der
    urspruenglichen `self.participant_id` des aufrufenden Menschen."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write_test_profile(d / "run")
        printed: list[str] = []
        gm = _FakeCreationGm(_FIXTURE_SAVE_2)
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="original-human",
            input_fn=_scripted_input([
                "Zweite Spielerin",     # Name der neuen Person
                "j",                    # Fokusuebernahme bestaetigen (_local_round_handoff)
                "n",                    # fuer die neue Person: Figur erschaffen
                "Ich beginne meine eigene Reise.",
            ]),
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: gm,
        )
        assert session.participant_id == "original-human"
        session._cmd_register_new_person()

        # Fokus ist nach Abschluss wieder bei der URSPRUENGLICHEN Identitaet.
        assert session.participant_id == "original-human"
        assert any("Fokus uebernommen" in p for p in printed), printed
        assert any("Fokus zurueck bei 'original-human'" in p for p in printed), printed

        # Die neue Person hat ihre EIGENE registrierte ID bekommen (nicht
        # 'original-human') -- aus der Registry lesbar.
        from mmo_sim.registry.participants import ParticipantRegistry
        registry = ParticipantRegistry(session._local_round_registry_dir())
        humans = session._local_round_list_humans()
        new_ids = [pid for pid, name in humans if name == "Zweite Spielerin"]
        assert len(new_ids) == 1, humans
        new_pid = new_ids[0]
        assert new_pid != "original-human"

        # Katalog: die neu erschaffene Figur gehoert der NEUEN ID, nicht
        # der urspruenglichen aufrufenden Person (kein Ownership-Leck).
        new_entries = catalog.list_for_participant(d / "catalog", new_pid)
        original_entries = catalog.list_for_participant(d / "catalog", "original-human")
        assert len(new_entries) == 1, new_entries
        assert len(original_entries) == 0, original_entries
        from mmo_sim.domain.zeitriss import saves as zeitriss_saves
        assert new_entries[0].chrononaut_id == zeitriss_saves.block_char_id(_FIXTURE_SAVE_2)


def test_registration_without_focus_confirmation_keeps_focus_and_stays_registered():
    """UX07: wird die Fokusuebernahme ABGELEHNT (kein 'j'), bleibt die
    Person registriert (keine verlorene Arbeit), aber OHNE eigene Figur --
    kein stiller Fokuswechsel ohne Bestaetigung."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="original-human",
            input_fn=_scripted_input(["Dritte Person", "n"]),  # 'n' = Fokus NICHT uebernehmen
            print_fn=printed.append,
        )
        session._cmd_register_new_person()
        assert session.participant_id == "original-human"
        assert any("noch nicht aktiv uebernommen" in p for p in printed), printed
        humans = session._local_round_list_humans()
        assert any(name == "Dritte Person" for _pid, name in humans), humans


def test_empty_name_aborts_without_any_write():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="original-human",
            input_fn=_scripted_input([""]),
            print_fn=printed.append,
        )
        session._cmd_register_new_person()
        assert any("kein Name eingegeben" in p for p in printed), printed
        assert session._local_round_list_humans() == []


def test_focus_guard_restores_participant_id_even_on_eof():
    """`_ParticipantFocusGuard` muss den urspruenglichen Fokus auch bei
    einem Abbruch (EOF) INNERHALB des Fokus-Blocks zuverlaessig
    restaurieren (kein hinterlassener falscher Fokus)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        from mmo_sim.registry.participants import ParticipantRegistry
        registry = ParticipantRegistry(d / "registry")
        new_p = registry.register_participant(kind="human", display_name="Jemand")
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="original-human",
            input_fn=lambda prompt="": (_ for _ in ()).throw(EOFError()), print_fn=lambda *_a: None,
        )
        try:
            with session._ParticipantFocusGuard(session, new_p.participant_id):
                assert session.participant_id == new_p.participant_id
                raise EOFError()
        except EOFError:
            pass
        assert session.participant_id == "original-human"


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
