#!/usr/bin/env python3
"""
tests/mmo_sim/test_stage4_capability_gate_2026_11_02.py — ZR-FIGURENREISE-
TISCH-20261102-R1, Teilpaket B (design.md §2, Briefing stage4-capability-
gate.md).

Beweist das explizite HOST/GUEST-Capability-Gate:
1. Providerfreiheit: der komplette Gast-Pfad (Tischsuche/-ansicht,
   Beitritt anfragen/zurueckziehen, eigene Figur waehlen/export/import)
   laeuft durch, OHNE je eine Spy-Factory (wirft SOFORT bei Aufruf) zu
   triggern.
2. Jede Gast-verbotene Hostaktion wirft `GuestCapabilityError` (NICHT die
   rohe Spy-Exception) -- der Gate-Punkt selbst verhindert den
   Factory-Aufruf, fängt ihn nicht erst ab.
3. `host_capable=True` (Default) bleibt bytegleich zum bisherigen
   Hostverhalten (keine Regression fuer bestehende Aufrufer).

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs."""
from __future__ import annotations

import json
import sys
import tempfile
import traceback
from pathlib import Path
from types import SimpleNamespace

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.core import table_admission  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import GuestCapabilityError, TuiSession, render_boot_menu  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


class _SpyFactory:
    """Wirft SOFORT bei Aufruf (Konstruktion/Aufruf des Treibers), NIE erst
    beim Benutzen des Ergebnisses -- der staerkste Nachweis, dass ein
    Gast-Pfad die Factory NIE erreicht (design.md §2 'Nachweis
    Providerfreiheit')."""

    def __init__(self, label: str):
        self.label = label
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        raise AssertionError(
            f"Spy-Factory '{self.label}' wurde aufgerufen -- der Gast-Pfad hat eine "
            "Host-Factory-Instanziierungsstelle erreicht (Teilpaket B Gate-Bruch)."
        )


def _scripted_input(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


def _register_own_figure(onboarding_dir: Path, catalog_dir: Path, participant_id: str) -> str:
    """Legt fuer `participant_id` eine ABGESCHLOSSENE eigene Figur im
    Katalog an -- derselbe Produktweg wie `onboarding.complete_with_save`
    + `catalog.register`, OHNE je eine SL/Persona-Factory zu beruehren
    (reine Katalog-/Onboarding-Schreiblogik)."""
    char_id = f"CHR-{participant_id.upper()}"
    save = full_v7_save(char_id, name=participant_id, save_id=f"fixture-{participant_id}-001")
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
    ))
    return char_id


def _make_ready_persona(onboarding_dir: Path, states_dir: Path, run_dir: Path, persona_key: str) -> str:
    """Dieselbe Produktwegfolge wie
    `test_ux1_persona_factory_guard.py:_make_ready` -- eine Persona
    braucht eine ECHTE abgeschlossene+publizierte Figur, bevor
    `_resume_bound_table`/`_cmd_local_round` ueberhaupt bis zur
    Persona-Factory-Aufrufstelle vordringen."""
    char_id = f"CHR-{persona_key.upper()}"
    save = full_v7_save(char_id, name=persona_key, save_id=f"fixture-{persona_key}-001")
    ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
    onboarding.start_or_resume(onboarding_dir, persona_key)
    onboarding.complete_with_save(onboarding_dir, persona_key, save, ZeitrissHarvestValidator(), char_id)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, persona_key, char_id, save)
    core_store.publish_current_save(run_dir, persona_key, save, ps_store, states_dir)
    return char_id


def test_host_capable_defaults_true_for_every_existing_caller():
    """design.md §2: 'Default so, dass JEDER bestehende Aufrufer
    bytegleich/kompatibel bleibt' -- kein `host_capable`-Keyword, keine
    Gastgrenze, `_require_host` ist ein No-op."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
        )
        assert session._host_capable is True
        session._require_host("irgendeine Hostaktion")  # darf NICHT werfen


def test_render_boot_menu_shows_gastmodus_line_only_when_not_host_capable():
    host_text = render_boot_menu(None)
    assert "Gastmodus" not in host_text
    guest_text = render_boot_menu(None, host_capable=False)
    assert "Gastmodus" in guest_text
    assert "nur eigene Figur verwalten" in guest_text


def test_table_admission_guest_flow_needs_zero_host_factories():
    """design.md §2 Nachweis Providerfreiheit, Tischsuche/-ansicht +
    Beitritt anfragen/zurueckziehen: `table_admission.py` importiert gar
    keine Factory -- Host anbieten, Gast anfragen/zurueckziehen/roster
    ansehen laufen vollstaendig OHNE jede GM-/Persona-Anbindung durch."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        table_admission.offer_table(run_dir, host_id="host1", table_key="tisch-a")
        view1 = table_admission.roster(run_dir, "tisch-a")
        assert view1["state"] == table_admission.STATE_OPEN
        table_admission.request_join(run_dir, table_key="tisch-a", guest_id="guest1")
        view2 = table_admission.roster(run_dir, "tisch-a")
        assert "guest1" in view2["requests"]
        table_admission.withdraw_request(run_dir, table_key="tisch-a", guest_id="guest1")
        view3 = table_admission.roster(run_dir, "tisch-a")
        assert "guest1" not in view3["requests"]


def test_guest_export_import_and_figure_switch_without_spy_trigger():
    """design.md §2 Nachweis Providerfreiheit: Export/Import/Eigene-Figur-
    waehlen laufen im Gastmodus durch, OHNE die Spy-GM-/Persona-Factory
    je zu triggern (inkl. `_apply_pending_compat_load`s Defense-in-depth,
    da `_cmd_export` ueber `_resolve_active_save` dorthin verzweigt)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write_test_profile(d / "run")
        char_id = _register_own_figure(d / "onboarding", d / "catalog", "guest1")
        spy_gm = _SpyFactory("gm_transport_factory")
        spy_persona = _SpyFactory("persona_driver_factory")
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="guest1",
            input_fn=_scripted_input(["1"]),  # Index 1 = die einzige bestehende Figur
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=spy_gm, persona_driver_factory=spy_persona,
            host_capable=False,
        )
        # Eigene Figur waehlen (bestehende Figur, NICHT 'neu') -- Gast
        # DARF das (design.md §2 Gast-Faehigkeitsgrenze).
        session._cmd_new_or_switch_character()
        assert spy_gm.calls == 0 and spy_persona.calls == 0

        # Export -- Gast DARF das.
        session._cmd_export()
        assert any("Vollstaendiger Save" in p for p in printed), printed
        assert spy_gm.calls == 0 and spy_persona.calls == 0

        # Import -- Gast DARF das (eigene Figur re-importieren).
        export_path = d / "exports" / "guest1.json"
        assert export_path.is_file(), "Export-Datei fehlt -- Testvoraussetzung"
        raw_text = export_path.read_text(encoding="utf-8")
        session2 = TuiSession(
            onboarding_dir=d / "onboarding2", catalog_dir=d / "catalog2", participant_id="guest1",
            input_fn=_scripted_input([raw_text, "ENDE"]),
            print_fn=printed.append,
            run_dir=d / "run2", states_dir=d / "states2", schema_path=_SCHEMA_PATH,
            gm_transport_factory=spy_gm, persona_driver_factory=spy_persona,
            host_capable=False,
        )
        session2._cmd_import()
        assert spy_gm.calls == 0 and spy_persona.calls == 0
        assert not any("Traceback" in p for p in printed), printed


def test_guest_switching_to_existing_figure_does_not_raise():
    """Teil des Gast-Pfads oben isoliert: `_cmd_new_or_switch_character`
    MUSS fuer eine BESTEHENDE Figur ohne Ausnahme zurueckkehren (nur der
    'neu'-Host-Pfad ist gegatet, s. `test_guest_new_character_creation_
    raises_guest_boundary` unten)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        _register_own_figure(d / "onboarding", d / "catalog", "guest1")
        spy_gm = _SpyFactory("gm")
        spy_persona = _SpyFactory("persona")
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="guest1",
            input_fn=_scripted_input(["1"]),  # Index 1 = die einzige bestehende Figur
            print_fn=printed.append,
            gm_transport_factory=spy_gm, persona_driver_factory=spy_persona,
            host_capable=False,
        )
        session._cmd_new_or_switch_character()
        assert spy_gm.calls == 0 and spy_persona.calls == 0
        assert not any(isinstance(p, GuestCapabilityError) for p in printed)


def test_guest_new_character_creation_raises_guest_boundary_no_spy():
    """design.md §2: der allererste Erschaffungsweg (keine Figur vorhanden,
    SL-Dialog) IST ein Host-Pfad -- Gast bekommt `GuestCapabilityError`,
    die Spy-GM-Factory wird NIE aufgerufen."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        spy_gm = _SpyFactory("gm")
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="guest1",
            run_dir=d / "run",
            gm_transport_factory=spy_gm,
            host_capable=False,
        )
        try:
            session._cmd_new_or_switch_character()
            raise AssertionError("GuestCapabilityError erwartet, aber keine Ausnahme geworfen.")
        except GuestCapabilityError as e:
            assert "Gastmodus" in str(e)
        assert spy_gm.calls == 0


def test_guest_new_character_creation_explicit_neu_raises_guest_boundary():
    """Dieselbe Grenze, aber ueber den 'neu'-Zweig MIT bereits vorhandener
    Figur (die zweite der beiden Zusammenflussstellen vor dem Gate)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        _register_own_figure(d / "onboarding", d / "catalog", "guest1")
        spy_gm = _SpyFactory("gm")
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="guest1",
            input_fn=_scripted_input(["neu"]),
            run_dir=d / "run",
            gm_transport_factory=spy_gm,
            host_capable=False,
        )
        try:
            session._cmd_new_or_switch_character()
            raise AssertionError("GuestCapabilityError erwartet, aber keine Ausnahme geworfen.")
        except GuestCapabilityError:
            pass
        assert spy_gm.calls == 0


def test_guest_local_round_setup_raises_guest_boundary_before_any_prompt():
    """`_cmd_local_round_setup` (Solo-mit-KI/Anbieten) ist Methodeneintritt-
    gegatet -- 0 Prompts, 0 Calls fuer Gast."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="guest1",
            input_fn=_scripted_input([]),  # darf NIE gelesen werden
            host_capable=False,
        )
        try:
            session._cmd_local_round_setup()
            raise AssertionError("GuestCapabilityError erwartet.")
        except GuestCapabilityError:
            pass


def test_guest_invite_persona_fresh_start_raises_guest_boundary_no_spy():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        spy_persona = _SpyFactory("persona")
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="guest1",
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: object(), persona_driver_factory=spy_persona,
            host_capable=False,
        )
        try:
            session._invite_persona_fresh_start()
            raise AssertionError("GuestCapabilityError erwartet.")
        except GuestCapabilityError:
            pass
        assert spy_persona.calls == 0


def test_guest_local_round_lead_persona_token_raises_guest_boundary_no_spy():
    """'l lead:persona:<id>' -- KI-Leader einladen IST eine Hostaktion."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write_test_profile(d / "run")
        _register_own_figure(d / "onboarding", d / "catalog", "guest1")
        _make_ready_persona(d / "onboarding", d / "states", d / "run", "some_ai")
        spy_persona = _SpyFactory("persona")
        spy_gm = _SpyFactory("gm")
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="guest1",
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=spy_gm, persona_driver_factory=spy_persona,
            host_capable=False,
        )
        try:
            session._cmd_local_round(["lead:persona:some_ai"])
            raise AssertionError("GuestCapabilityError erwartet.")
        except GuestCapabilityError:
            pass
        assert spy_gm.calls == 0 and spy_persona.calls == 0


def test_guest_local_round_persona_guest_token_raises_guest_boundary_no_spy():
    """'l persona:<id>' -- eine Persona ALS MITSPIELER einladen IST eine
    Hostaktion (Host entscheidet die Tischbesetzung)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write_test_profile(d / "run")
        _register_own_figure(d / "onboarding", d / "catalog", "guest1")
        _make_ready_persona(d / "onboarding", d / "states", d / "run", "some_ai")
        spy_persona = _SpyFactory("persona")
        spy_gm = _SpyFactory("gm")
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="guest1",
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=spy_gm, persona_driver_factory=spy_persona,
            host_capable=False,
        )
        try:
            session._cmd_local_round(["persona:some_ai"])
            raise AssertionError("GuestCapabilityError erwartet.")
        except GuestCapabilityError:
            pass
        assert spy_gm.calls == 0 and spy_persona.calls == 0


def test_guest_local_round_plain_solo_raises_guest_boundary_at_gm_defense_in_depth():
    """'l' OHNE Token -- design.md §2 Gast-Faehigkeitsgrenze 'DARF NICHT:
    Solo spielen'. Trifft heute den Defense-in-depth-Gate unmittelbar vor
    `_run_table_round`s GM-Factory-Aufruf (kein Persona-Zweig beteiligt)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write_test_profile(d / "run")
        _register_own_figure(d / "onboarding", d / "catalog", "guest1")
        spy_gm = _SpyFactory("gm")
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="guest1",
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=spy_gm,
            host_capable=False,
        )
        try:
            session._cmd_local_round([])
            raise AssertionError("GuestCapabilityError erwartet.")
        except GuestCapabilityError:
            pass
        assert spy_gm.calls == 0


def test_guest_resume_bound_table_persona_leader_raises_guest_boundary_no_spy():
    """`_resume_bound_table` bleibt fuer Gast GRUNDSAETZLICH erreichbar
    ('spielen nach Annahme') -- aber einen KI-Leader TREIBEN (Defense-in-
    depth vor `persona_driver_factory`) bleibt eine Hostaktion."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        char_id = _make_ready_persona(d / "onboarding", d / "states", d / "run", "ai_leader")
        spy_persona = _SpyFactory("persona")
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="guest1",
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: object(), persona_driver_factory=spy_persona,
            host_capable=False,
        )
        fake_table = SimpleNamespace(
            leader="ai_leader", members=["ai_leader"], chrononaut_ids={"ai_leader": char_id},
            table_id="bound-test-table", sl_log=[],
        )
        try:
            session._resume_bound_table(fake_table)
            raise AssertionError("GuestCapabilityError erwartet.")
        except GuestCapabilityError:
            pass
        assert spy_persona.calls == 0


def test_apply_pending_compat_load_guest_silent_no_spy_when_no_envelope():
    """`_apply_pending_compat_load` ist unbedingt am Boot/Export/Import-Pfad
    erreichbar (`_resolve_active_save` <- `_build_resume_card`) -- der
    Defense-in-depth hier ist bewusst eine STILLE Bedingung statt
    `_require_host` (sonst Absturz bei JEDEM Gastboot). Ohne vorhandenen
    Kompatibilitaetsumschlag (Regelfall) bleibt es ein No-op, 0 Spy-Calls."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        _register_own_figure(d / "onboarding", d / "catalog", "guest1")
        spy_gm = _SpyFactory("gm")
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="guest1",
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=spy_gm,
            host_capable=False,
        )
        card = session._build_resume_card()
        assert card is not None
        assert spy_gm.calls == 0
        assert not any("Traceback" in p for p in printed), printed


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
