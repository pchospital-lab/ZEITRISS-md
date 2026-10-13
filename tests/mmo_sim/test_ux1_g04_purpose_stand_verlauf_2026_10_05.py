#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_g04_purpose_stand_verlauf_2026_10_05.py — G04
(ZEITRISS Terminal UX-1, Korrekturzyklus 2, Wiederanlauf W9): Eingabezweck
an den menschlichen UI-Adapter durchreichen, `/stand` an die tatsaechlich
eingebende Person binden, `/verlauf` vollstaendig statt still gekuerzt.

Deckt General-Befund G04/P05 und die zugehoerigen Mussfaelle:
- UX14 (vierter Textzweck): die freiwillige Abschlussnotiz (`_collect_
  reflections`/`human_note`) laeuft ueber DENSELBEN `_HumanDriver.decide()`
  wie ein echter Spielzug -- vorher zeigte sie faelschlich "Empfaenger:
  Spielleitung (SL)" (P05). Jetzt zeigt sie die tatsaechlich zutreffende
  lokale Beschriftung; Payloadbeleg: die Notiz landet NIE im `sl_log`/in
  `table_messages`, NUR in `reflections.jsonl` (`kind=human_note`).
- UX15: leere Notiz blockiert den Abschluss nicht (kein `human_note`-Eintrag,
  aber `reflections_ok` bleibt wahr); Hilfe ('?') waehrend der Notizabfrage
  verbraucht keinen Reflexionsturn (genau EIN Archiveintrag trotz Hilfeabruf,
  kein zusaetzlicher Modellaufruf).
- UX20: `/stand` an einem geteilten Terminal zeigt den Stand der GERADE
  EINGEBENDEN Person (Leader ODER Gast), nicht pauschal den aeusseren
  Sessionteilnehmer; `/verlauf` macht die VOLLE erhaltene Historie ueber
  sichtbare Seitennavigation zugaenglich statt still nur die letzten 10
  Eintraege zu zeigen (die an das Modell gehende `history` bleibt dabei
  in jedem Fall vollstaendig/ungekuerzt -- nur die ANZEIGE blaettert).

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
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import catalog  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402
import _a24_local_support as sup  # noqa: E402


def _scripted(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


def _save_block(char_id: str) -> dict:
    return full_v7_save(char_id, name="Journey")


class _OneShotCompletingGm:
    """Liefert beim ERSTEN Aufruf sofort den Abschluss-Marker + Save-Block --
    genau EIN echter Spielzug, danach `finalize()`/`_collect_reflections()`."""

    def __init__(self, char_id: str):
        self._char_id = char_id
        self.calls = 0

    def turn(self, turn_idx, text, **kw):
        self.calls += 1
        content = (
            f"Abschnitt beendet.\n```json\n{json.dumps(_save_block(self._char_id))}\n```\n"
            f"{COMPLETION_MARKER}"
        )
        return {"content": content}


class _NeverCompletingGm:
    """Liefert nie einen Abschluss-Marker -- die Runde bleibt offen, damit
    nach dem Leader-Anker auch der Gast-Erstimport real erreicht wird."""

    def __init__(self):
        self.calls = 0

    def turn(self, turn_idx, text, **kw):
        self.calls += 1
        return {"content": f"SL-Antwort #{turn_idx} (kein Abschluss hier)."}


def _build_solo_leader(run_dir: Path, states_dir: Path, onboarding_dir: Path):
    registry_dir = run_dir.parent / "registry"
    leader = sup.register_human(registry_dir, "Leader")
    leader_id = leader.participant_id
    info = sup.onboard_human_figure(
        registry_dir, leader_id, onboarding_dir, states_dir, run_dir, "CHR-LEAD", "Lea", "LEADOPS",
    )
    return leader_id, info["char_id"]


# --------------------------------------------------------------------------
# UX14/UX15/P05: Empfaenger-/Zweckzeile der freiwilligen lokalen Abschluss-
# notiz (vierter Textzweck), Payload-/Callbeleg (NICHT in sl_log/table).
# --------------------------------------------------------------------------

def test_reflection_purpose_label_is_local_note_not_sl_and_note_stays_local():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir, onboarding_dir = d / "run", d / "states", d / "onboarding"
        catalog_dir = d / "catalog"
        write_test_profile(run_dir)
        leader_id, char_id = _build_solo_leader(run_dir, states_dir, onboarding_dir)

        printed: list[str] = []
        gm = _OneShotCompletingGm(char_id)
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=leader_id,
            input_fn=_scripted([
                "Leader-Zug 1 (Anker, loest Abschluss aus).",
                "Das war ein guter Abschnitt, danke dir.",
            ]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=sup.SCHEMA,
            gm_transport_factory=lambda: gm, persona_driver_factory=None,
        )
        try:
            session._cmd_local_round([])
        except EndOfInput:
            pass

        assert gm.calls == 1, "genau EIN echter Spielzug, danach Abschluss/Reflexion"
        assert any("Abschnitt abgeschlossen" in p for p in printed), printed

        empf_lines = [p for p in printed if p.startswith("Empfaenger:")]
        # Erhaltungsprobe: der ECHTE Spielzug (Leader-Anker) zeigt weiterhin
        # korrekt "Spielleitung (SL)".
        assert any(p == "Empfaenger: Spielleitung (SL)" for p in empf_lines), empf_lines
        # Kernassertion G04/P05: die LETZTE Empfaenger-Zeile (die der
        # Notizabfrage unmittelbar vorausgeht) darf NICHT mehr "Spielleitung"
        # behaupten -- sie muss die tatsaechlich zutreffende lokale
        # Beschriftung zeigen.
        assert empf_lines[-1].startswith("Empfaenger: eigene lokale Notiz"), empf_lines
        # Die korrekte lokale Beschriftung DARF "Spielleitung"/"Tisch" nur im
        # Rahmen von "NICHT an ..." erwaehnen -- sie darf aber nicht mit
        # einer der alten Spielzug-Beschriftungen BEGINNEN (genau das war
        # der Fehler, P05).
        assert not empf_lines[-1].startswith("Empfaenger: Spielleitung")
        assert not empf_lines[-1].startswith("Empfaenger: Tischabsprache")
        assert not empf_lines[-1].startswith("Empfaenger: ueber Leader")

        reflections = [
            json.loads(line)
            for line in (run_dir / "reflections.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        human_notes = [r for r in reflections if r.get("kind") == "human_note"]
        assert len(human_notes) == 1, reflections
        assert human_notes[0]["text"] == "Das war ein guter Abschnitt, danke dir."
        assert human_notes[0]["origin_source"].startswith("human:"), human_notes[0]

        # UX15/Payloadbeleg: die private Notiz erreicht NIE sl_log/Tisch.
        table_file = run_dir / "tables" / f"local-{leader_id}.json"
        data = json.loads(table_file.read_text(encoding="utf-8"))
        sl_text = " ".join(e.get("content", "") for e in data.get("sl_log", []))
        assert "guter Abschnitt, danke" not in sl_text, sl_text
        assert not any("guter Abschnitt" in m.get("text", "") for m in data.get("table_messages", [])), data


def test_empty_reflection_note_does_not_block_section_completion():
    """UX15: leere Notiz ist freiwillig -- blockiert nichts, erzeugt KEINEN
    `human_note`-Archiveintrag, die Sektion schliesst trotzdem final."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir, onboarding_dir = d / "run", d / "states", d / "onboarding"
        catalog_dir = d / "catalog"
        write_test_profile(run_dir)
        leader_id, char_id = _build_solo_leader(run_dir, states_dir, onboarding_dir)

        printed: list[str] = []
        gm = _OneShotCompletingGm(char_id)
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=leader_id,
            input_fn=_scripted(["Leader-Zug 1 (Anker).", ""]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=sup.SCHEMA,
            gm_transport_factory=lambda: gm, persona_driver_factory=None,
        )
        try:
            session._cmd_local_round([])
        except EndOfInput:
            pass

        assert any("Abschnitt abgeschlossen" in p for p in printed), printed
        reflections_path = run_dir / "reflections.jsonl"
        reflections = (
            [json.loads(l) for l in reflections_path.read_text(encoding="utf-8").splitlines() if l.strip()]
            if reflections_path.exists() else []
        )
        assert not any(r.get("kind") == "human_note" for r in reflections), reflections


def test_help_during_reflection_consumes_no_turn_no_duplicate_record():
    """UX15: '?' waehrend der Notizabfrage zeigt Hilfe OHNE die Notiz zu
    verbrauchen/zu duplizieren -- genau EIN `human_note`-Eintrag mit dem
    tatsaechlich zuletzt eingegebenen Text, kein zweiter Modell-/Archivzug."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir, onboarding_dir = d / "run", d / "states", d / "onboarding"
        catalog_dir = d / "catalog"
        write_test_profile(run_dir)
        leader_id, char_id = _build_solo_leader(run_dir, states_dir, onboarding_dir)

        printed: list[str] = []
        gm = _OneShotCompletingGm(char_id)
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=leader_id,
            input_fn=_scripted(["Leader-Zug 1 (Anker).", "?", "Danke, das war hilfreich."]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=sup.SCHEMA,
            gm_transport_factory=lambda: gm, persona_driver_factory=None,
        )
        try:
            session._cmd_local_round([])
        except EndOfInput:
            pass

        assert gm.calls == 1, "Hilfe darf keinen zweiten GM-/Modellaufruf ausloesen"
        assert any("Hilfe (Spielzug)" in p for p in printed), printed

        reflections = [
            json.loads(l)
            for l in (run_dir / "reflections.jsonl").read_text(encoding="utf-8").splitlines()
            if l.strip()
        ]
        human_notes = [r for r in reflections if r.get("kind") == "human_note"]
        assert len(human_notes) == 1, reflections
        assert human_notes[0]["text"] == "Danke, das war hilfreich."


# --------------------------------------------------------------------------
# UX20: `/stand` bindet an die GERADE EINGEBENDE Person (geteiltes Terminal),
# nicht pauschal an den aeusseren Sessionteilnehmer.
# --------------------------------------------------------------------------

def test_stand_during_shared_terminal_binds_to_actually_typing_participant():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = d / "run", d / "states", d / "onboarding", d / "catalog"
        write_test_profile(run_dir)
        registry_dir = run_dir.parent / "registry"
        leader = sup.register_human(registry_dir, "Leader")
        guest = sup.register_human(registry_dir, "Guest")
        leader_id, guest_id = leader.participant_id, guest.participant_id
        leader_info = sup.onboard_human_figure(
            registry_dir, leader_id, onboarding_dir, states_dir, run_dir, "CHR-LEAD", "Lea", "LEADOPS",
        )
        guest_info = sup.onboard_human_figure(
            registry_dir, guest_id, onboarding_dir, states_dir, run_dir, "CHR-GUEST", "Gus", "GUESTOPS",
        )
        # Testaufbau ueber die vorhandene oeffentliche Katalog-API (keine
        # Produktaenderung): `last_selected` muss real gebunden sein, damit
        # die Fortsetzen-Detailzeile (render_boot_menu) ueberhaupt erscheint
        # -- derselbe Weg, den `_cmd_new_or_switch_character` am echten
        # Erschaffungspfad bereits produktiv nutzt (`catalog.bind_for_section`).
        catalog.register(catalog_dir, catalog.CatalogEntry(
            participant_id=leader_id, chrononaut_id=leader_info["char_id"],
            persona_key=leader_id, display_name="Lea",
        ))
        catalog.bind_for_section(catalog_dir, leader_id, leader_info["char_id"], has_open_section=False)
        catalog.register(catalog_dir, catalog.CatalogEntry(
            participant_id=guest_id, chrononaut_id=guest_info["char_id"],
            persona_key=guest_id, display_name="Gus",
        ))
        catalog.bind_for_section(catalog_dir, guest_id, guest_info["char_id"], has_open_section=False)

        printed: list[str] = []
        gm = _NeverCompletingGm()
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=leader_id,
            input_fn=_scripted([
                "j",                          # Gast bestaetigt den Beitritt.
                "/stand",                     # Leader fragt WAEHREND SEINES EIGENEN Zugs.
                "Leader-Zug 1 (Anker).",
                "/stand",                     # Gast fragt WAEHREND SEINES EIGENEN Erstimport-Zugs.
                "Gast-Erstbeitrag (Import).",
            ]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=sup.SCHEMA,
            gm_transport_factory=lambda: gm, persona_driver_factory=None,
        )
        try:
            session._cmd_local_round([guest_id])
        except EndOfInput:
            pass

        stand_lines = [p for p in printed if p.startswith("Fortsetzen:")]
        assert len(stand_lines) == 2, printed
        leader_stand, guest_stand = stand_lines

        def _participant_field(line: str) -> str:
            # "Fortsetzen: {community} · {participant_id} · {chrono} — ...";
            # the shared open-section suffix mentions BOTH ids (same table),
            # so only the dedicated middle field identifies the card owner.
            parts = line.split(" · ")
            assert len(parts) >= 3, line
            return parts[1].strip()

        assert _participant_field(leader_stand) == leader_id, leader_stand
        assert _participant_field(guest_stand) == guest_id, guest_stand
        # Zusatzbeleg: die jeweils EIGENE Figur/Chrononaut erscheint, nicht
        # die der anderen Person.
        assert "CHR-LEAD" in leader_stand and "CHR-GUEST" not in leader_stand, leader_stand
        assert "CHR-GUEST" in guest_stand and "CHR-LEAD" not in guest_stand, guest_stand


# --------------------------------------------------------------------------
# UX20: `/verlauf` macht die VOLLE Historie ueber Seitennavigation
# zugaenglich statt still nur die letzten 10 Eintraege zu zeigen. Direkter
# Test an der tatsaechlichen Produktionsmethode (`_readline_with_controls`,
# derselbe Code, den `_HumanDriver.decide()` real aufruft).
# --------------------------------------------------------------------------

def test_verlauf_pagination_reaches_full_history_not_only_last_ten():
    """Alle drei '/verlauf'-Eingaben landen in EINEM Aufruf (dieselbe
    Prompt-Zeile wird intern wiederholt abgefragt, s. `_readline_with_
    controls`-Docstring) -- `printed` akkumuliert daher alle drei Seiten
    nacheinander. Die Seitenbeleg-/Abschlusszeilen dienen hier als
    eindeutige Trenner, um JEDE Seite exakt (kein Ueberlapp/keine Luecke)
    zu pruefen, statt sich auf eine (nach drei Seiten ohnehin falsche)
    pauschale Abwesenheitspruefung zu verlassen."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted(["/verlauf", "/verlauf", "/verlauf", "echter Zug"]),
            print_fn=(printed := []).append,
        )
        full_history = [f"[SL] Eintrag {i}" for i in range(25)]
        text, control = session._readline_with_controls(
            "Frage: ", context="Spielzug", history=full_history,
        )
        assert control is None and text == "echter Zug"

        # Exakte Volltextgleichheit statt Teilstringsuche: "5 weitere ..."
        # ist sonst ein Teilstring von "15 weitere ..." und faende faelsch-
        # lich dieselbe Zeile wie die erste Seitengrenze.
        page1_marker = "... 15 weitere, aeltere Eintraege -- '/verlauf' erneut fuer mehr."
        page2_marker = "... 5 weitere, aeltere Eintraege -- '/verlauf' erneut fuer mehr."
        page3_marker = "(Anfang des Verlaufs erreicht, 25 Eintraege gesamt.)"
        idx_page1 = next(i for i, p in enumerate(printed) if p == page1_marker)
        idx_page2 = next(i for i, p in enumerate(printed) if p == page2_marker)
        idx_page3 = next(i for i, p in enumerate(printed) if p == page3_marker)
        page1 = printed[:idx_page1]
        page2 = printed[idx_page1 + 1:idx_page2]
        page3 = printed[idx_page2 + 1:idx_page3]
        # Seite 1 (neueste zuerst angefragt): Eintraege 15..24, GENAU 10,
        # keine Kuerzung/Uebersprung.
        assert page1 == [f"[SL] Eintrag {i}" for i in range(15, 25)], page1
        # Seite 2: die NAECHSTEN 10 aelteren, lueckenlos an Seite 1 anschliessend.
        assert page2 == [f"[SL] Eintrag {i}" for i in range(5, 15)], page2
        # Seite 3: der VERBLEIBENDE Rest bis zum echten Anfang (Eintrag 0) --
        # voller Zugriff auf die GESAMTE erhaltene Historie, nicht nur die
        # letzten 10 (vorheriges Verhalten: stilles `history[-10:]`).
        assert page3 == [f"[SL] Eintrag {i}" for i in range(0, 5)], page3


def test_verlauf_without_history_says_so_honestly():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted(["/verlauf", "echter Zug"]),
            print_fn=(printed := []).append,
        )
        text, control = session._readline_with_controls("Frage: ", context="Spielzug", history=[])
        assert control is None and text == "echter Zug"
        assert any("Kein bisheriger Verlauf" in p for p in printed), printed


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
