#!/usr/bin/env python3
"""
tests/mmo_sim/test_stage5_tui_wiring_2026_11_02.py — ZR-FIGURENREISE-TISCH-
20261102-R1, Stage 5 (TUI-Wiring, design.md §4, Briefing stage5-tui-
wiring.md).

Deckt:
1. Gate-Nachweis im Gast-Flow: JEDE Tisch-Lifecycle-Hostaktion
   (`tisch-anbieten`/`tisch-annehmen`/`tisch-ablehnen`/`tisch-entfernen`/
   `tisch-start`) wirft `GuestCapabilityError` fuer `host_capable=False`,
   OHNE `table_admission` je zu mutieren; die Gast-Kommandos
   (`tisch-anfragen`/`tisch-zurueckziehen`/`tisch-verlassen`/`tisch-status`)
   bleiben fuer denselben Gast ungegatet.
2. Voller A->B->A-Durchlauf (J1-J3/J5): Host bietet an -> Gast fragt an ->
   Host nimmt an -> `tisch-start` -> UNVERAENDERTER Spielpfad
   (`core_store.create_table_from_offer_log` + `app_service.
   run_play_session`, hier via `_cmd_local_round`) -> geschlossener
   Abschnitt (`table.status == "closed"`) -> Gast verlaesst den Tisch
   -> Export der aktualisierten Figur aus Wurzel B -> Re-Import nach
   Wurzel A (`resolve_import`s `adopt_incoming`, UNVERAENDERT) uebernimmt
   den fortgeschrittenen Stand (hoeheres `lvl`), nicht den alten.

Fakes NUR am GM-Transportrand (`_FakeTableGm`, Muster
`_section_completion_resume_fixtures.ScriptedGmTransport`/
`test_ux1_label_authority._FakeGm`) -- Produktpersistenz (table_admission/
store/import_export/catalog/onboarding) laeuft ECHT.

Pure Python, nur `assert`, echter Exitcode (gleiches Muster wie
`test_stage4_capability_gate_2026_11_02.py`)."""
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

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.core import table_admission  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, import_export, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import GuestCapabilityError, TuiSession  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


class _SpyFactory:
    """Wirft SOFORT bei Aufruf -- identisches Muster zu
    `test_stage4_capability_gate_2026_11_02.py._SpyFactory` (Nachweis
    Providerfreiheit, design.md §2)."""

    def __init__(self, label: str):
        self.label = label
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        raise AssertionError(f"Spy-Factory '{self.label}' wurde aufgerufen (Gate-Bruch).")


class _FakeTableGm:
    """Liefert die ersten beiden SL-Antworten OHNE Abschluss-Marker (Anker-
    Zug des Hosts, Erstbeitrag des Gasts), danach (Zug 3+, idempotent fuer
    etwaige weitere Aufrufe) den vollen Debrief MIT Marker + je einem
    gueltigen v7-Save-Block fuer Host UND Gast -- derselbe minimale
    Drei-Zug-Rhythmus wie `_population_backup_fixtures.play_section_to_
    success` (Anker -> Gast-Import -> Debrief), hier real ueber
    `TuiSession._cmd_local_round`/`_HumanDriver` getrieben statt per
    `ScriptedDriver`."""

    def __init__(self, debrief_text: str):
        self._debrief = debrief_text
        self.calls = 0

    def turn(self, turn_idx, text, **kw):
        self.calls += 1
        if self.calls < 3:
            return {"content": f"SL-Antwort #{self.calls} (kein Abschluss hier)."}
        return {"content": self._debrief}


def _smart_input():
    """Promptbewusste Eingabefunktion (robust gegen die genaue Reihenfolge
    von Terminaluebergaben/Pflicht-Reflexionen, die von interner
    Rundenmechanik abhaengt, s. `_HumanDriver`/`_local_round_handoff`):
    jede '[j/n]'-Rueckfrage (Beitritt/Terminaluebergabe/Importbestaetigung)
    bekommt 'j', eine Importkonfliktwahl 'Wahl [a/k]' bekommt 'a'
    (`adopt_incoming`, design.md §3 J5), jeder normale Spielzug-/
    Reflexionsprompt ('Deine Aktion:') bekommt einen generischen, durch-
    nummerierten Text (Inhalt ist fuer die Produktlogik irrelevant)."""
    counter = {"n": 0}

    def _fn(prompt: str = "") -> str:
        if "[j/n]" in prompt:
            return "j"
        if "Wahl [a/k]" in prompt:
            return "a"
        counter["n"] += 1
        return f"Zug {counter['n']}."
    return _fn


def _register_own_figure(
    onboarding_dir: Path, catalog_dir: Path, participant_id: str, char_id: str, level: int = 1,
    *, run_dir: Path | None = None, states_dir: Path | None = None,
) -> dict:
    """Legt fuer `participant_id` eine ABGESCHLOSSENE eigene Figur im
    Katalog an -- derselbe Produktweg wie `test_stage4_capability_gate_
    2026_11_02.py._register_own_figure`. Mit `run_dir`/`states_dir`
    (additiv, fuer den HOST an Wurzel B gebraucht) ZUSAETZLICH echter
    Persona-State + Current-Publikation (`onboarding.ensure_participant_
    persona_state` + `core_store.publish_current_save`) -- dieselben zwei
    Schritte, die `TuiSession._cmd_import` fuer den GAST automatisch
    ausfuehrt (tui.py:3131-3140); OHNE eine persistierte Persona-State
    lehnt `store._validate_harvest` JEDES Mitglied bei Abschnittsabschluss
    als 'missing' ab (`persona_state_store.load_state` -> `FileNotFoundError`)."""
    save = full_v7_save(char_id, name=participant_id, save_id=f"fixture-{participant_id}-001", level=level)
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
    ))
    if run_dir is not None and states_dir is not None:
        from mmo_sim.core import store as core_store
        from mmo_sim.core.persona_state import PersonaStateStore
        ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
        onboarding.ensure_participant_persona_state(ps_store, states_dir, participant_id, char_id, save)
        core_store.publish_current_save(run_dir, participant_id, save, ps_store, states_dir)
    return save


# ── 1. Gate-Nachweis im Gast-Flow ──────────────────────────────────────────


def test_guest_host_only_table_commands_raise_without_mutating_admission():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir = d / "run"
        table_admission.offer_table(run_dir, host_id="host1", table_key="t1")
        table_admission.request_join(run_dir, table_key="t1", guest_id="guest1")
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="guest1",
            run_dir=run_dir, host_capable=False,
        )
        for method, args in (
            (session._cmd_table_offer, ["t1"]),
            (session._cmd_table_accept, ["t1", "guest1"]),
            (session._cmd_table_reject, ["t1", "guest1"]),
            (session._cmd_table_remove, ["t1", "guest1"]),
            (session._cmd_table_start, ["t1"]),
        ):
            try:
                method(args)
                raise AssertionError(f"{method.__name__} haette GuestCapabilityError werfen muessen.")
            except GuestCapabilityError:
                pass
        # Admission-Record unveraendert: keine Mutation durch die
        # abgelehnten Gastversuche (Gate greift VOR jedem table_admission-
        # Aufruf, Methodeneintritt).
        record = table_admission.load_record(run_dir, "t1")
        assert record["state"] == table_admission.STATE_OPEN
        assert record["roster"] == ["host1"] and record["requests"] == ["guest1"]


def test_guest_table_commands_work_without_host_capability():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir = d / "run"
        table_admission.offer_table(run_dir, host_id="host1", table_key="t1")
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="guest1",
            run_dir=run_dir, host_capable=False,
        )
        printed: list[str] = []
        session._print = printed.append
        session._cmd_table_status(["t1"])
        session._cmd_table_request_join(["t1"])
        record = table_admission.load_record(run_dir, "t1")
        assert "guest1" in record["requests"]
        session._cmd_table_withdraw(["t1"])
        record = table_admission.load_record(run_dir, "t1")
        assert "guest1" not in record["requests"]
        session._cmd_table_request_join(["t1"])
        table_admission.accept_request(run_dir, table_key="t1", host_id="host1", guest_id="guest1")
        session._cmd_table_leave(["t1"])
        record = table_admission.load_record(run_dir, "t1")
        assert "guest1" not in record["roster"]
        assert not any("Gastmodus" in p or "GuestCapabilityError" in p for p in printed), printed


def test_render_boot_menu_table_status_lines_additive_default_none():
    """`render_boot_menu`s neues `table_status_lines`-Keyword bleibt fuer
    JEDEN bestehenden Aufrufer (nur `resume`) bytegleich (Default `None`)."""
    from mmo_sim.ui.tui import render_boot_menu
    assert "Eigene Tische" not in render_boot_menu(None)
    assert "Eigene Tische" in render_boot_menu(None, table_status_lines=["  Tisch 't1' (Host, state=open): ..."])


# ── 2. Voller A->B->A-Durchlauf ────────────────────────────────────────────


def test_full_a_to_b_to_a_table_journey():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)

        # --- Wurzel A: Gastinstall, KEIN Hoststack. Eigene Figur anlegen
        # + exportieren (design.md §0).
        onboarding_A, catalog_A, exports_A = d / "A" / "onboarding", d / "A" / "catalog", d / "A" / "exports"
        _register_own_figure(onboarding_A, catalog_A, "guest1", "CHR-GUEST1", level=1)
        guest_session_A = TuiSession(
            onboarding_dir=onboarding_A, catalog_dir=catalog_A, participant_id="guest1",
            exports_dir=exports_A, print_fn=lambda *_a, **_kw: None, host_capable=False,
        )
        guest_session_A._cmd_export()
        export_path_A = exports_A / "guest1.json"
        assert export_path_A.is_file(), "Export aus Wurzel A fehlt -- Testvoraussetzung"
        raw_text_from_A = export_path_A.read_text(encoding="utf-8")

        # --- Wurzel B: Hostinstall, voller Stack. Eigene Hostfigur anlegen.
        run_dir_B, states_dir_B = d / "B" / "run", d / "B" / "states"
        onboarding_B, catalog_B, exports_B = d / "B" / "onboarding", d / "B" / "catalog", d / "B" / "exports"
        # Kein `max_usd`: der providerfreie Testprofil-Treiber (`_FakeTableGm`)
        # legt kein durchsetzbares Ausgabe-/Gesamtlimit offen -- ein hartes
        # `max_usd` wuerde die Admission-Gate (I2 Q07, A1) jede Anfrage
        # ablehnen lassen, weil keine Obergrenze ermittelbar ist. `max_turns`
        # alleine bleibt eine ausreichende, durchsetzbare Obergrenze.
        write_test_profile(run_dir_B, max_turns=200)
        host_save = _register_own_figure(
            onboarding_B, catalog_B, "host1", "CHR-HOST1", level=1,
            run_dir=run_dir_B, states_dir=states_dir_B,
        )

        debrief_host_block = full_v7_save("CHR-HOST1", name="host1", save_id="fixture-host1-002", level=1)
        debrief_guest_block = full_v7_save("CHR-GUEST1", name="guest1", save_id="fixture-guest1-002", level=2)
        from _section_completion_resume_fixtures import debrief_with_marker
        debrief_text = debrief_with_marker({"CHR-HOST1": debrief_host_block, "CHR-GUEST1": debrief_guest_block})
        fake_gm = _FakeTableGm(debrief_text)
        spy_persona = _SpyFactory("persona_driver_factory")

        host_session_B = TuiSession(
            onboarding_dir=onboarding_B, catalog_dir=catalog_B, participant_id="host1",
            input_fn=_smart_input(), print_fn=lambda *_a, **_kw: None,
            run_dir=run_dir_B, states_dir=states_dir_B, schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: fake_gm, persona_driver_factory=spy_persona,
            exports_dir=exports_B, host_capable=True,
        )
        guest_at_B_session = TuiSession(
            onboarding_dir=onboarding_B, catalog_dir=catalog_B, participant_id="guest1",
            input_fn=_smart_input(), print_fn=lambda *_a, **_kw: None,
            run_dir=run_dir_B, states_dir=states_dir_B, schema_path=_SCHEMA_PATH,
            gm_transport_factory=_SpyFactory("guest_gm"), persona_driver_factory=_SpyFactory("guest_persona"),
            exports_dir=exports_B, host_capable=False,
        )

        # J1: Host bietet an -> Gast fragt an -> Host nimmt an.
        host_session_B._cmd_table_offer(["mesa1"])
        guest_at_B_session._cmd_table_request_join(["mesa1"])
        host_session_B._cmd_table_accept(["mesa1", "guest1"])
        record = table_admission.load_record(run_dir_B, "mesa1")
        assert record["roster"] == ["host1", "guest1"] and record["requests"] == []

        # J4/Fremdimport (Teilpaket C, UNVERAENDERT): Gast importiert die
        # in Wurzel A exportierte Figur nach Wurzel B unter der eigenen ID.
        _run_import(guest_at_B_session, raw_text_from_A)
        imported_state = onboarding.peek(onboarding_B, "guest1")
        assert imported_state is not None and imported_state.final_save is not None

        # J1/J2: Host startet den Tisch -> UNVERAENDERTER Spielpfad ->
        # geschlossener Abschnitt.
        # R2-Nachzug (F2 §1, independent-r1-review.md F2 Abs. 1): die
        # Admission-Idempotenz ist jetzt bis zum echten Spielstart/-
        # abschluss GEBUNDEN (`table_admission.bind_section`/
        # `close_table`, s. `tui.py:_cmd_table_start`) -- der Fake-GM
        # debrieft hier bereits INNERHALB dieses einen Aufrufs (Zug 3),
        # der Admission-Record schliesst deshalb SOFORT mit (vorher R1:
        # blieb faelschlich `state="started"`, obwohl der echte Store-
        # Tisch schon `status="closed"` war -- genau die in F2 benannte
        # Luecke).
        host_session_B._cmd_table_start(["mesa1"])
        started_record = table_admission.load_record(run_dir_B, "mesa1")
        assert started_record["state"] == table_admission.STATE_CLOSED
        assert started_record["section_id"] == "local-host1-guest1"
        assert started_record["roster"] == ["host1", "guest1"]
        assert fake_gm.calls >= 3, "GM-Transport haette bis zum Debrief-Marker durchlaufen muessen"

        table_file = run_dir_B / "tables" / "local-host1-guest1.json"
        assert table_file.is_file(), "Spieltisch-Datei (bestehender Spielpfad) fehlt"
        table_data = json.loads(table_file.read_text(encoding="utf-8"))
        assert table_data.get("status") == "closed", f"Abschnitt nicht geschlossen: {table_data.get('status')!r}"
        assert spy_persona.calls == 0, "Persona-Factory darf im reinen Human-Host-Gast-Strang nie aufgerufen werden"

        # J3: Gast verlaesst den Tisch nach geschlossenem Abschnitt.
        guest_at_B_session._cmd_table_leave(["mesa1"])
        left_record = table_admission.load_record(run_dir_B, "mesa1")
        assert left_record["roster"] == ["host1"], "Gast haette sich selbst aus dem roster entfernen muessen"

        # J5/J6: Export der AKTUALISIERTEN Figur aus Wurzel B.
        guest_at_B_session._cmd_export()
        export_path_B = exports_B / "guest1.json"
        assert export_path_B.is_file(), "Export der aktualisierten Figur aus Wurzel B fehlt"
        exported_block_B = json.loads(export_path_B.read_text(encoding="utf-8"))
        assert exported_block_B["characters"][0]["lvl"] == 2, (
            "Export aus Wurzel B haette den fortgeschrittenen Stand (lvl=2) tragen muessen, "
            f"nicht den alten: {exported_block_B['characters'][0].get('lvl')!r}"
        )
        raw_text_from_B = export_path_B.read_text(encoding="utf-8")

        # J5: Re-Import nach Wurzel A -- `resolve_import`s `adopt_incoming`
        # (UNVERAENDERT) ersetzt NUR die vorige aktive Gastkopie.
        guest_session_A2 = TuiSession(
            onboarding_dir=onboarding_A, catalog_dir=catalog_A, participant_id="guest1",
            input_fn=_smart_input(), print_fn=lambda *_a, **_kw: None, host_capable=False,
        )
        _run_import(guest_session_A2, raw_text_from_B)
        final_state_A = onboarding.peek(onboarding_A, "guest1")
        assert final_state_A is not None and final_state_A.final_save is not None
        assert final_state_A.final_save["characters"][0]["lvl"] == 2, (
            "Re-Import nach Wurzel A haette den fortgeschrittenen Stand (lvl=2) uebernehmen "
            f"muessen (adopt_incoming), nicht den alten: {final_state_A.final_save['characters'][0].get('lvl')!r}"
        )


def _run_import(session: TuiSession, raw_text: str) -> None:
    """Treibt `TuiSession._cmd_import()` mit vorab bereitgestelltem
    Mehrzeilentext (Export-JSON + 'ENDE') -- derselbe Eingabevertrag wie am
    echten Terminal (`_cmd_import` liest Zeile fuer Zeile bis 'ENDE'). Die
    `_smart_input`-Funktion der uebergebenen Session beantwortet danach
    JEDE Rueckfrage (Konfliktwahl/Bestaetigung) promptbewusst."""
    lines = iter(raw_text.splitlines() + ["ENDE"])
    base_input = session._input

    def _fn(prompt: str = "") -> str:
        try:
            return next(lines)
        except StopIteration:
            return base_input(prompt)
    session._input = _fn
    session._cmd_import()
    session._input = base_input


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
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
