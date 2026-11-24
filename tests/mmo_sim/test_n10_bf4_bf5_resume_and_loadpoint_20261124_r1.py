#!/usr/bin/env python3
"""
tests/mmo_sim/test_n10_bf4_bf5_resume_and_loadpoint_20261124_r1.py — N10
(BF-4 + BF-5, reviews/BUDGET_FLOW_REVIEW.md).

BF-4 ("ein Fenster pro [5] ist noch kein gezieltes Resume"):
- `_cmd_catch_up_personas` akzeptiert jetzt ZUSAETZLICH zu den bisherigen
  Persona-Keys kommagetrennte 1-basierte Nummern (gemischt moeglich) --
  bestehende Key-Eingaben bleiben unveraendert gueltig.
- Ein neuer, von Catch-up/Vorspielen UNTERSCHEIDBARER Weg ("Diesen offenen
  Abschnitt fortsetzen", [6] im Spielen-Untermenue) setzt eine bereits
  real gebundene Tisch-/Sectionbindung ueber die BESTEHENDE
  `_resolve_bound_table_for_resume`/`_resume_bound_table`-Autoritaet fort
  -- NIE ueber `catchup.run_catch_up` -- und beruehrt dabei NIE eine
  unbeteiligte "freie ungewaehlte" Persona (kein Driver-/Request-/Lock-
  Kontakt).

BF-5 ("LOAD-1 verbessert die Anzeige, liefert aber noch keinen Ladepunkt"):
- Der Kompatibilitaets-Hinweis in `render_boot_menu` nennt "Export" nicht
  mehr als Reparaturweg (Export nutzt `_resolve_active_save` NICHT, s.
  `_cmd_export`).
- Ein neuer, bewusster Ladepunkt im Charakter-Untermenue ([7]) baut ueber
  den bereits bestehenden `_resolve_active_save(apply_compat_load=True)`-
  Weg Kontext fuer die aktuelle Figur auf, zeigt einen real offenen
  Kompatibilitaetsfall ehrlich an und STOPPT danach (kein neuer Abschnitt/
  keine Einladung/kein Missionsfortschritt). Reine Bogen-Anzeige
  (`_cmd_show_bogen`) bleibt davon unberuehrt/kostenfrei.

Reuse (Leitprinzip "Reuse vor Neubau"): Bootstrap-/Treiber-/Fixture-Code
aus `test_p1_vorspielen_closed_table_2026_10_21.py`,
`test_r3_f2_resume_admission_reconcile.py` und
`test_stage4_capability_gate_2026_11_02.py` -- importiert als Module,
kein zweiter Bootstrap-Code. Pure `unittest.TestCase` (Pflicht-Smoke lief
ueber `python -m unittest ... -v`)."""
from __future__ import annotations

import contextlib
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _full_v7_fixture import full_v7_save  # noqa: E402
from _section_completion_resume_fixtures import debrief_with_marker  # noqa: E402

import test_l01_l10_lobby_initiative as l01  # noqa: E402
import test_p1_vorspielen_closed_table_2026_10_21 as p1  # noqa: E402
import test_r3_f2_resume_admission_reconcile as r3f2  # noqa: E402
import test_stage4_capability_gate_2026_11_02 as stage4  # noqa: E402

import mmo_sim.core.save_compatibility as save_compat_core  # noqa: E402
import mmo_sim.core.save_correction as sc  # noqa: E402
from mmo_sim.core import catchup  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core import table_admission  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, ResumeCard, TuiSession, render_boot_menu  # noqa: E402


@contextlib.contextmanager
def _inject_one_shot_version_read_error(version_path: Path):
    """L1-Gegenfall-Helfer (dasselbe Injektionsmuster wie
    `test_i4_current_readpaths.py:_inject_version_read_error`, hier lokal
    dupliziert statt importiert -- Linus-TUI darf dieses fremde Testmodul
    nicht anfassen/importieren): genau EIN gewoehnlicher `OSError` beim
    Lesen der TATSAECHLICH vorhandenen, referenzierten Versionsdatei; die
    Datei selbst bleibt auf der Platte unveraendert."""
    original = Path.read_text
    hit = [0]

    def _fail(path, *a, **kw):
        if path == version_path and hit[0] == 0:
            hit[0] += 1
            raise OSError("INJECT ordinary one-shot version read failure")
        return original(path, *a, **kw)

    with patch.object(Path, "read_text", _fail):
        yield hit


class TestBf4NumberedSelection(unittest.TestCase):
    """BF-4 Umsetzungsform Punkt 1: nummerierte Auswahl ZUSAETZLICH zu
    Persona-Keys -- beide Formen (auch gemischt) waehlen dieselben
    Kandidaten; eine ausserhalb der Nummerierung liegende Zahl wird wie
    ein unbekannter Key fail-closed abgelehnt."""

    def test_mixed_number_and_key_input_selects_same_candidates_as_keys(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, gm_transport_factory = p1._bootstrap(root)
            offer_id = "invite-sniper-cqb-face-n10"
            drivers = {
                "cqb": p1._GroupGuestDriver("cqb", offer_id, partner="face"),
                "face": p1._GroupGuestDriver("face", offer_id, partner="cqb"),
                "tech": p1._NeverCalledDriver("tech"),
                "medic": p1._NeverCalledDriver("medic"),
                "pyro": p1._NeverCalledDriver("pyro"),
            }

            def persona_driver_factory(pk):
                return drivers[pk]

            printed: list[str] = []

            def human_responder(prompt: str = "") -> str:
                if prompt.startswith("Welche jetzt spielen lassen?"):
                    # sortierte Kandidaten fuer Vorspielen ohne aktiven Tisch:
                    # ["cqb","face","medic","pyro","tech"] -- "1" == cqb (Nummer),
                    # "face" bleibt der bisherige Key -- BEIDE Formen gemischt.
                    return "1,face"
                raise AssertionError(f"unerwarteter Prompt ohne Antwortregel: {prompt!r}")

            session = TuiSession(
                onboarding_dir, catalog_dir, p1.HUMAN_PK,
                input_fn=human_responder, print_fn=printed.append,
                run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
                gm_transport_factory=gm_transport_factory,
                persona_driver_factory=persona_driver_factory,
            )

            session._cmd_catch_up_personas(vorspielen=True)  # Menuepunkt [5].

            out = "\n".join(printed)
            self.assertIn("1) cqb", out, out)  # Nummer sichtbar in der Kandidatenzeile.
            self.assertTrue(
                len(drivers["cqb"].calls) >= 2 and len(drivers["face"].calls) >= 2,
                "cqb/face haetten real befragt werden muessen (Invite + Zug), egal ob per Nummer "
                f"oder Key gewaehlt: {drivers['cqb'].calls!r} / {drivers['face'].calls!r}",
            )
            counts_after = core_store.sections_played_by_participant(run_dir)
            self.assertEqual(counts_after.get("cqb"), 1)
            self.assertEqual(counts_after.get("face"), 1)
            # tech/medic/pyro: "1,face" waehlt NUR cqb+face -- jeder weitere
            # Call auf _NeverCalledDriver.decide() haette bereits geworfen.

    def test_number_out_of_range_rejected_fail_closed_like_unknown_key(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, gm_transport_factory = p1._bootstrap(root)
            drivers = {pk: p1._NeverCalledDriver(pk) for pk in p1.AI_PERSONAS}

            def persona_driver_factory(pk):
                return drivers[pk]

            printed: list[str] = []

            def human_responder(prompt: str = "") -> str:
                if prompt.startswith("Welche jetzt spielen lassen?"):
                    return "9"  # ausserhalb 1..5 -- kein wahlbarer Kandidat.
                raise AssertionError(f"unerwarteter Prompt ohne Antwortregel: {prompt!r}")

            session = TuiSession(
                onboarding_dir, catalog_dir, p1.HUMAN_PK,
                input_fn=human_responder, print_fn=printed.append,
                run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
                gm_transport_factory=gm_transport_factory,
                persona_driver_factory=persona_driver_factory,
            )

            session._cmd_catch_up_personas(vorspielen=True)  # Menuepunkt [5].

            out = "\n".join(printed)
            self.assertIn("kein Fenster gestartet", out, out)
            self.assertEqual(core_store.sections_played_by_participant(run_dir), {})
            # Jeder _NeverCalledDriver haette bei einem faelschlich gestarteten
            # Fenster bereits in .decide() geworfen -- der Testlauf selbst waere
            # dann mit AssertionError abgebrochen, nicht hier angekommen.


class TestBf4SpielenMenuResumeEntry(unittest.TestCase):
    """BF-4 Umsetzungsform Punkt 2 (Wiring): [6] erscheint NUR mit real
    gebundener offener Section (dieselbe Bedingung wie
    `_cmd_resume_or_continue`) und dispatcht dann auf
    `_cmd_resume_open_section` -- kollidiert mit keinem der festen
    [1]-[5]."""

    def test_entry_6_hidden_and_inert_without_open_section(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            calls: list[str] = []
            session = TuiSession(
                onboarding_dir=root / "onboarding", catalog_dir=root / "catalog",
                participant_id="host1", input_fn=lambda prompt="": "/zurueck",
                host_capable=True,
            )
            session._cmd_resume_open_section = lambda: calls.append("called")
            session._build_resume_card = lambda: None
            printed: list[str] = []
            session._print = printed.append

            session._cmd_menu_spielen()

            out = "\n".join(printed)
            self.assertNotIn("[6]", out, out)
            self.assertEqual(calls, [])

    def test_entry_6_shown_and_dispatches_with_open_section(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            calls: list[str] = []
            session = TuiSession(
                onboarding_dir=root / "onboarding", catalog_dir=root / "catalog",
                participant_id="host1", input_fn=lambda prompt="": "6",
                host_capable=True,
            )
            session._cmd_resume_open_section = lambda: calls.append("called")
            session._build_resume_card = lambda: ResumeCard(
                community_id=None, participant_id="host1", chrononaut_id="CHR-HOST1",
                last_valid_save_summary="Stand", open_section_id="mesa-n10",
            )
            printed: list[str] = []
            session._print = printed.append

            session._cmd_menu_spielen()

            out = "\n".join(printed)
            self.assertIn("[6] Diesen offenen Abschnitt fortsetzen", out, out)
            self.assertEqual(calls, ["called"])


class TestBf4ResumeOpenSectionSemantics(unittest.TestCase):
    """BF-4 Abnahme: zweiter bewusster Schritt haelt dieselbe Zielbindung,
    bereits gebundene Mitglieder bekommen keine neue Catch-up-Zielrunde
    (`catchup.run_catch_up` darf GAR NICHT aufgerufen werden), eine freie
    ungewaehlte Persona bekommt weder Driverkonstruktion noch Lock."""

    def test_second_step_resumes_same_binding_without_catchup_or_foreign_persona_touch(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            run_dir, states_dir = d / "run", d / "states"
            onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
            write_test_profile(run_dir, max_turns=200)
            r3f2._register_own_figure(
                onboarding_dir, catalog_dir, "host1", "CHR-HOST1", level=1,
                run_dir=run_dir, states_dir=states_dir,
            )
            r3f2._register_own_figure(
                onboarding_dir, catalog_dir, "guest1", "CHR-GUEST1", level=1,
                run_dir=run_dir, states_dir=states_dir,
            )
            r3f2._register_human_identity(onboarding_dir, "guest1")
            # Freie, UNBETEILIGTE Persona ("ungewaehlte Persona" der Abnahme) --
            # darf durch den gezielten Resume-Weg NIE angefasst werden.
            stage4._make_ready_persona(onboarding_dir, states_dir, run_dir, "tech")

            host_p1 = r3f2._fresh_host_session(
                onboarding_dir, catalog_dir, run_dir, states_dir,
                input_fn=r3f2._pausing_after_consent_input(),
                gm_transport_factory=lambda: r3f2._NeverClosingGm(),
            )
            guest_session = TuiSession(
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="guest1",
                run_dir=run_dir, host_capable=False,
            )
            host_p1._cmd_table_offer(["mesaN10"])
            guest_session._cmd_table_request_join(["mesaN10"])
            host_p1._cmd_table_accept(["mesaN10", "guest1"])
            try:
                host_p1._cmd_table_start(["mesaN10"])
                self.fail("Tischstart haette per /pause mit EndOfInput enden muessen.")
            except EndOfInput:
                pass

            record_paused = table_admission.load_record(run_dir, "mesaN10")
            bound_section_id = record_paused.get("section_id")
            self.assertTrue(bound_section_id, "section_id haette trotz Pause gebunden sein muessen.")
            section_paused = core_store.Table.load(run_dir, bound_section_id)
            self.assertNotEqual(section_paused.status, "closed", "Testvoraussetzung: Section muss real offen sein.")
            self.assertNotIn("CHR-TECH", core_store._read_locks(run_dir), "tech durfte vor dem Resume keinen Lock haben.")
            tables_dir = run_dir / "tables"
            before_table_files = sorted(p.name for p in tables_dir.glob("*.json"))
            self.assertEqual(before_table_files, [f"{bound_section_id}.json"])

            orig_run_catch_up = catchup.run_catch_up

            def _guard_run_catch_up(*_a, **_k):
                raise AssertionError(
                    "BF-4: 'Diesen offenen Abschnitt fortsetzen' darf run_catch_up NIE aufrufen "
                    "(keine neue Catch-up-Zielrunde fuer bereits gebundene Mitglieder)."
                )

            catchup.run_catch_up = _guard_run_catch_up
            try:
                debrief_host = full_v7_save("CHR-HOST1", name="host1", save_id="fixture-host1-n10-002", level=1)
                debrief_guest = full_v7_save("CHR-GUEST1", name="guest1", save_id="fixture-guest1-n10-002", level=1)
                debrief_text = debrief_with_marker({"CHR-HOST1": debrief_host, "CHR-GUEST1": debrief_guest})
                fake_gm = r3f2._FakeTableGm(debrief_text)
                # Zweiter bewusster Prozess/Schritt -- derselbe Produktweg wie
                # ein echter Neustart (frischer Interpreter, gemeinsame Platte).
                host_p2 = r3f2._fresh_host_session(
                    onboarding_dir, catalog_dir, run_dir, states_dir,
                    input_fn=r3f2._smart_input(), gm_transport_factory=lambda: fake_gm,
                )
                host_p2._cmd_resume_open_section()
            finally:
                catchup.run_catch_up = orig_run_catch_up

            section_resumed = core_store.Table.load(run_dir, bound_section_id)
            self.assertEqual(section_resumed.status, "closed", "der gezielte Resume-Weg haette den Abschnitt abschliessen muessen.")
            record_resumed = table_admission.load_record(run_dir, "mesaN10")
            self.assertEqual(record_resumed["state"], table_admission.STATE_CLOSED)
            self.assertEqual(
                record_resumed["section_id"], bound_section_id,
                "Zielbindung haette beim zweiten bewussten Schritt gleich bleiben muessen.",
            )
            self.assertNotIn(
                "CHR-TECH", core_store._read_locks(run_dir),
                "die freie ungewaehlte Persona 'tech' haette NIE einen Lock bekommen duerfen.",
            )
            after_table_files = sorted(p.name for p in tables_dir.glob("*.json"))
            self.assertEqual(
                after_table_files, before_table_files,
                "kein neuer Tisch/keine Request-Datei fuer 'tech' oder sonst wen erwartet.",
            )

            # Dritter Schritt: keine offene Bindung mehr -> keine Aktion, kein
            # Input/GM-Zugriff noetig (SpyFactory wirft sofort bei Aufruf).
            host_p3 = r3f2._fresh_host_session(
                onboarding_dir, catalog_dir, run_dir, states_dir,
                input_fn=r3f2._SpyFactory("sollte nie Input brauchen"),
                gm_transport_factory=r3f2._SpyFactory("host_gm_p3"),
            )
            printed: list[str] = []
            host_p3._print = printed.append
            host_p3._cmd_resume_open_section()
            self.assertTrue(any("keine Aktion" in p for p in printed), printed)


def _register_ki_persona(
    onboarding_dir: Path, catalog_dir: Path, run_dir: Path, states_dir: Path,
    participant_id: str, char_id: str, display_name: str,
) -> None:
    """L2-Testhelfer: dasselbe Produktweg-Muster wie `r3f2._register_own_
    figure`, aber mit FREI WAEHLBAREM Figurennamen (`r3f2._register_own_
    figure` haengt `name` fest an `participant_id`) -- damit die Abnahme
    beweisen kann, dass die neue nummerierte Auswahl den VERSTAENDLICHEN
    Figurennamen zeigt, NICHT den internen `pk` (BUDGET_FLOW_REVIEW.md
    R2-BF-4 "Kandidatenanzeige zeigt interne pk statt Figurennamen")."""
    save = full_v7_save(char_id, name=display_name, save_id=f"fixture-{participant_id}-001")
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
    ))
    catalog.bind_for_section(catalog_dir, participant_id, char_id, has_open_section=False)
    ps_store = PersonaStateStore(schema_path=stage4._SCHEMA_PATH)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, participant_id, char_id, save)
    core_store.publish_current_save(run_dir, participant_id, save, ps_store, states_dir)


def _bootstrap_bound_ki_table_alpha_beta_free_third(d: Path):
    """L2-Rosterabgleich-Gegenfall-Testhelfer (BUDGET_FLOW_REVIEW.md
    "Verbleibender konkreter Fehler"): Reuse derselben bereits bewiesenen
    Aufbauschritte wie `test_operator_outside_table_selects_open_ki_
    table_by_number_with_readable_names` (echter offener Zwei-Personas-
    KI-Tisch kitech='Techniker-Theta' Leader / kicqb='Scharfschuetze-Rho'
    Gast, PLUS freie dritte Persona 'kifree'='Freilaeuferin-Null') --
    EIN Bootstrap statt einer zweiten Variante fuer die beiden neuen
    Gegenfall-Tests (ausgeschlossener gebundener Partner / positiver
    vollstaendig erlaubter Gegenfall)."""
    run_dir, states_dir = d / "run", d / "states"
    onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
    write_test_profile(run_dir, max_turns=200)
    l01._bootstrap_community(d, "community-coordinator", ["kitech", "kicqb", "kifree"])
    _register_ki_persona(
        onboarding_dir, catalog_dir, run_dir, states_dir, "kitech", "CHR-KITECH", "Techniker-Theta",
    )
    _register_ki_persona(
        onboarding_dir, catalog_dir, run_dir, states_dir, "kicqb", "CHR-KICQB", "Scharfschuetze-Rho",
    )
    _register_ki_persona(
        onboarding_dir, catalog_dir, run_dir, states_dir, "kifree", "CHR-KIFREE", "Freilaeuferin-Null",
    )
    ki_leader = TuiSession(
        onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="kitech",
        input_fn=r3f2._pausing_after_consent_input(), print_fn=lambda *_a, **_kw: None,
        run_dir=run_dir, states_dir=states_dir, schema_path=stage4._SCHEMA_PATH,
        gm_transport_factory=lambda: r3f2._NeverClosingGm(),
        persona_driver_factory=r3f2._SpyFactory("ki_leader_persona"),
        host_capable=True,
    )
    ki_guest = TuiSession(
        onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="kicqb",
        run_dir=run_dir, states_dir=states_dir, host_capable=False,
    )
    ki_leader._cmd_table_offer(["mesaKI"])
    ki_guest._cmd_table_request_join(["mesaKI"])
    ki_leader._cmd_table_accept(["mesaKI", "kicqb"])
    try:
        ki_leader._cmd_table_start(["mesaKI"])
        raise AssertionError("Tischstart haette per /pause mit EndOfInput enden muessen.")
    except EndOfInput:
        pass
    record_paused = table_admission.load_record(run_dir, "mesaKI")
    bound_section_id = record_paused.get("section_id")
    assert bound_section_id, "section_id haette trotz Pause gebunden sein muessen."
    return run_dir, states_dir, onboarding_dir, catalog_dir, bound_section_id


class TestL2OpenKiTableResumeSelection(unittest.TestCase):
    """L2 (BUDGET_FLOW_REVIEW.md R2-BF-4, 02_RESTAUFTRAG.md §L L2) Abnahme:
    ein Operator OHNE eigenen offenen Lock sieht/waehlt einen offenen KI-
    Vorspieltisch (zwei Personas, KEIN Mensch am Tisch) ueber eine
    nummerierte Auswahl mit verstaendlichen Figurennamen; eine daneben
    freie, ungewaehlte Persona bleibt unberuehrt."""

    def test_operator_outside_table_selects_open_ki_table_by_number_with_readable_names(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            run_dir, states_dir = d / "run", d / "states"
            onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
            write_test_profile(run_dir, max_turns=200)

            # Community-Bootstrap des OPERATORS ("coordinator") -- dieselbe
            # bereits bestehende Kandidatenquelle wie Catch-up/Vorspielen
            # ([3]/[5], `catchup.ready_persona_keys`), NICHT ein neuer
            # ungefilterter Lobby-/Tischweg.
            l01._bootstrap_community(d, "community-coordinator", ["kitech", "kicqb", "kifree"])
            _register_ki_persona(
                onboarding_dir, catalog_dir, run_dir, states_dir, "kitech", "CHR-KITECH", "Techniker-Theta",
            )
            _register_ki_persona(
                onboarding_dir, catalog_dir, run_dir, states_dir, "kicqb", "CHR-KICQB", "Scharfschuetze-Rho",
            )
            # Freie, UNBETEILIGTE Persona in DERSELBEN Community -- darf
            # durch die gezielte Auswahl NIE angefasst werden (kein Driver/
            # Request/Lock).
            _register_ki_persona(
                onboarding_dir, catalog_dir, run_dir, states_dir, "kifree", "CHR-KIFREE", "Freilaeuferin-Null",
            )

            # Ein echter, offener KI-Tisch: BEIDE Mitglieder bleiben
            # unregistrierte Nicht-Menschen (kein `_register_human_
            # identity`) -- aus Sicht JEDER dritten Session sind beide
            # strukturell Personas (`_is_persona_member`).
            ki_leader = TuiSession(
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="kitech",
                input_fn=r3f2._pausing_after_consent_input(), print_fn=lambda *_a, **_kw: None,
                run_dir=run_dir, states_dir=states_dir, schema_path=stage4._SCHEMA_PATH,
                gm_transport_factory=lambda: r3f2._NeverClosingGm(),
                persona_driver_factory=r3f2._SpyFactory("ki_leader_persona"),
                host_capable=True,
            )
            ki_guest = TuiSession(
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="kicqb",
                run_dir=run_dir, states_dir=states_dir, host_capable=False,
            )
            ki_leader._cmd_table_offer(["mesaKI"])
            ki_guest._cmd_table_request_join(["mesaKI"])
            ki_leader._cmd_table_accept(["mesaKI", "kicqb"])
            try:
                ki_leader._cmd_table_start(["mesaKI"])
                self.fail("Tischstart haette per /pause mit EndOfInput enden muessen.")
            except EndOfInput:
                pass

            record_paused = table_admission.load_record(run_dir, "mesaKI")
            bound_section_id = record_paused.get("section_id")
            self.assertTrue(bound_section_id, "section_id haette trotz Pause gebunden sein muessen.")
            section_paused = core_store.Table.load(run_dir, bound_section_id)
            self.assertNotEqual(section_paused.status, "closed", "Testvoraussetzung: Section muss real offen sein.")
            self.assertNotIn(
                "CHR-KIFREE", core_store._read_locks(run_dir),
                "die freie ungewaehlte Persona 'kifree' haette VOR der Auswahl keinen Lock haben duerfen.",
            )

            # DER Operator: kein eigener Chrononaut/Save/Lock, NUR die
            # Community-Zustaendigkeit fuer kitech/kicqb/kifree.
            coordinator = TuiSession(
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="coordinator",
                input_fn=lambda prompt="": "1", print_fn=lambda *_a, **_kw: None,
                run_dir=run_dir, states_dir=states_dir, schema_path=stage4._SCHEMA_PATH,
                persona_driver_factory=r3f2._SpyFactory("coordinator_should_never_drive_personas_in_this_check"),
                host_capable=True,
            )

            # Zuerst NUR die lesende Kandidatenermittlung pruefen (ohne
            # irgendeinen Spielzug auszuloesen).
            candidates = coordinator._open_ki_table_resume_candidates()
            self.assertEqual(len(candidates), 1, candidates)
            only = candidates[0]
            self.assertEqual(only.open_section_id, bound_section_id)
            self.assertEqual(set(only.member_pks), {"kitech", "kicqb"})
            names_joined = ", ".join(only.member_names)
            self.assertIn("Techniker-Theta", names_joined, only.member_names)
            self.assertIn("Scharfschuetze-Rho", names_joined, only.member_names)
            self.assertNotIn("kitech", only.member_names, "Anzeige darf nicht den rohen pk tragen.")
            self.assertNotIn("kicqb", only.member_names, "Anzeige darf nicht den rohen pk tragen.")
            self.assertNotIn("kifree", only.member_pks)

            printed: list[str] = []
            coordinator._print = printed.append
            # Dispatch isoliert pruefen (dieselbe Schichtung wie
            # `TestBf4SpielenMenuResumeEntry`): `_resume_bound_table` selbst
            # ist bereits durch `TestBf4ResumeOpenSectionSemantics`/die
            # bestehende P1-Suite voll abgedeckt -- hier zaehlt NUR, dass
            # GENAU die gewaehlte, real existierende Tischbindung dorthin
            # gereicht wird.
            resumed: list = []
            coordinator._resume_bound_table = lambda table: resumed.append(table)

            coordinator._cmd_resume_open_section()

            out = "\n".join(printed)
            self.assertIn("Techniker-Theta", out, out)
            self.assertIn("Scharfschuetze-Rho", out, out)
            self.assertNotIn("Freilaeuferin-Null", out, out)
            self.assertEqual(len(resumed), 1, out)
            self.assertEqual(resumed[0].table_id, bound_section_id)
            self.assertEqual(resumed[0].table_id, section_paused.table_id)
            self.assertNotIn(
                "CHR-KIFREE", core_store._read_locks(run_dir),
                "die freie ungewaehlte Persona 'kifree' haette durch die Auswahl NIE einen Lock bekommen duerfen.",
            )

    def test_own_card_still_takes_priority_over_ki_candidates(self):
        """Die eigene Kartenfortsetzung bleibt die ERSTE Autoritaet (01
        Block F) -- mit eigenem offenen Lock wird NIE die KI-Kandidaten-
        liste gezeigt, selbst wenn zusaetzlich ein KI-Tisch offen ist."""
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            run_dir, states_dir = d / "run", d / "states"
            onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
            write_test_profile(run_dir, max_turns=200)
            r3f2._register_own_figure(
                onboarding_dir, catalog_dir, "host1", "CHR-HOST1", level=1,
                run_dir=run_dir, states_dir=states_dir,
            )
            r3f2._register_own_figure(
                onboarding_dir, catalog_dir, "guest1", "CHR-GUEST1", level=1,
                run_dir=run_dir, states_dir=states_dir,
            )
            r3f2._register_human_identity(onboarding_dir, "guest1")

            host_p1 = r3f2._fresh_host_session(
                onboarding_dir, catalog_dir, run_dir, states_dir,
                input_fn=r3f2._pausing_after_consent_input(),
                gm_transport_factory=lambda: r3f2._NeverClosingGm(),
            )
            guest_session = TuiSession(
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="guest1",
                run_dir=run_dir, states_dir=states_dir, host_capable=False,
            )
            host_p1._cmd_table_offer(["mesaOwn"])
            guest_session._cmd_table_request_join(["mesaOwn"])
            host_p1._cmd_table_accept(["mesaOwn", "guest1"])
            try:
                host_p1._cmd_table_start(["mesaOwn"])
                self.fail("Tischstart haette per /pause mit EndOfInput enden muessen.")
            except EndOfInput:
                pass
            own_bound_section_id = table_admission.load_record(run_dir, "mesaOwn").get("section_id")
            self.assertTrue(own_bound_section_id, "section_id haette trotz Pause gebunden sein muessen.")

            candidates_calls: list[str] = ["sentinel"]
            host_p2 = r3f2._fresh_host_session(
                onboarding_dir, catalog_dir, run_dir, states_dir,
                input_fn=r3f2._SpyFactory("sollte bei eigener Karte nie fuer die KI-Auswahl gebraucht werden"),
                gm_transport_factory=lambda: r3f2._NeverClosingGm(),
            )

            def _guard_candidates():
                candidates_calls.append("called")
                return []

            host_p2._open_ki_table_resume_candidates = _guard_candidates
            resumed: list = []
            host_p2._resume_bound_table = lambda table: resumed.append(table)

            host_p2._cmd_resume_open_section()

            self.assertEqual(candidates_calls, ["sentinel"], "KI-Kandidatenermittlung haette NICHT aufgerufen werden duerfen.")
            self.assertEqual(len(resumed), 1)
            self.assertEqual(resumed[0].table_id, own_bound_section_id)

    def test_bound_excluded_partner_blocks_resume_before_any_driver_build(self):
        """L2-Nachzug-Gegenfall (BUDGET_FLOW_REVIEW.md "Verbleibender
        konkreter Fehler"): Beta (kicqb) ist am SELBEN offenen Tisch
        gebunden wie der erlaubte Alpha (kitech), aber ausdruecklich
        ausgeschlossen (`_excluded_personas`). Die Auswahl darf NICHT
        trotzdem vollstaendig getrieben werden: `persona_driver_factory`
        darf fuer KEIN Mitglied dieses Tisches aufgerufen werden (kein
        Driver/Request fuer Beta, keine partielle Alpha-only-
        Ersatzfortsetzung), und der tatsaechliche Rundendispatch
        (`_run_table_round`, real erst NACH dem Driverbau in
        `_resume_bound_table` erreichbar) darf nie erreicht werden. Die
        freie dritte Persona 'kifree' bleibt unberuehrt."""
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            run_dir, states_dir, onboarding_dir, catalog_dir, bound_section_id = (
                _bootstrap_bound_ki_table_alpha_beta_free_third(d)
            )

            coordinator = TuiSession(
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="coordinator",
                input_fn=lambda prompt="": "1", print_fn=lambda *_a, **_kw: None,
                run_dir=run_dir, states_dir=states_dir, schema_path=stage4._SCHEMA_PATH,
                # Spy-Factory statt echtem Treiber: wirft bei JEDEM Aufruf --
                # beweist "kein Driver fuer irgendein Mitglied", nicht nur
                # "kein Driver fuer Beta" (keine partielle Ersatzfortsetzung).
                persona_driver_factory=r3f2._SpyFactory(
                    "L2-Fix-Gegenfall: ausgeschlossener gebundener Partner darf NIE einen Driver "
                    "bekommen -- diese Spy-Factory haette fuer KEIN Mitglied aufgerufen werden duerfen."
                ),
                host_capable=True,
            )
            # Beta ("kicqb") ist ausdruecklich ausgeschlossen -- dieselbe
            # bestehende Ausschlussmenge wie Catch-up/Vorspielen ([3]/[5]).
            coordinator._excluded_personas.add("kicqb")

            round_calls: list = []
            coordinator._run_table_round = lambda *a, **kw: round_calls.append((a, kw))

            printed: list[str] = []
            coordinator._print = printed.append

            coordinator._cmd_resume_open_section()

            out = "\n".join(printed)
            self.assertIn("kicqb", out, out)
            self.assertIn("ausgeschlossen", out, out)
            self.assertEqual(
                round_calls, [],
                f"Rundendispatch (nach Driverbau) haette fuer den ausgeschlossenen gebundenen "
                f"Partner NIE erreicht werden duerfen:\n{out}",
            )
            self.assertNotIn(
                "CHR-KIFREE", core_store._read_locks(run_dir),
                "die freie ungewaehlte Persona 'kifree' haette durch den Gegenfall NIE einen Lock "
                "bekommen duerfen.",
            )
            # Kein stiller Teil-Resume: der Tisch bleibt unveraendert aktiv
            # und ungetrieben, GENAU wie vor der Auswahl.
            still_active = core_store.Table.load(run_dir, bound_section_id)
            self.assertEqual(still_active.status, "active", still_active.status)
            self.assertEqual(still_active.sl_log, [], still_active.sl_log)

    def test_fully_allowed_bound_table_still_builds_both_drivers(self):
        """Positiver Gegenfall zur selben Kante (BUDGET_FLOW_REVIEW.md
        "Kleinster nötiger Nachzug"): OHNE Ausschluss bleibt derselbe
        vollstaendig sichtbare + erlaubte Tisch (Alpha+Beta beide erlaubt)
        unveraendert fortsetzbar -- BEIDE Driver werden real gebaut, und
        der Rundendispatch wird tatsaechlich erreicht (kein Ueberreagieren
        des L2-Fixes auf den erlaubten Fall). Die freie dritte Persona
        bleibt auch hier unberuehrt."""
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            run_dir, states_dir, onboarding_dir, catalog_dir, bound_section_id = (
                _bootstrap_bound_ki_table_alpha_beta_free_third(d)
            )

            driver_calls: list[str] = []

            def counting_persona_driver_factory(pk: str):
                driver_calls.append(pk)
                return object()

            coordinator = TuiSession(
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="coordinator",
                input_fn=lambda prompt="": "1", print_fn=lambda *_a, **_kw: None,
                run_dir=run_dir, states_dir=states_dir, schema_path=stage4._SCHEMA_PATH,
                gm_transport_factory=lambda: r3f2._NeverClosingGm(),
                persona_driver_factory=counting_persona_driver_factory,
                host_capable=True,
            )
            # Kein Ausschluss -- dieselbe Besetzung bleibt vollstaendig erlaubt.

            round_calls: list = []
            coordinator._run_table_round = lambda *a, **kw: round_calls.append((a, kw))

            printed: list[str] = []
            coordinator._print = printed.append

            coordinator._cmd_resume_open_section()

            out = "\n".join(printed)
            self.assertEqual(
                set(driver_calls), {"kitech", "kicqb"},
                f"beide erlaubten Mitglieder haetten real einen Driver bekommen muessen:\n{out}",
            )
            self.assertEqual(
                len(round_calls), 1,
                f"Rundendispatch haette fuer die vollstaendig erlaubte Besetzung real erreicht "
                f"werden sollen:\n{out}",
            )
            self.assertNotIn(
                "CHR-KIFREE", core_store._read_locks(run_dir),
                "die freie ungewaehlte Persona 'kifree' darf auch im positiven Gegenfall nie "
                "beruehrt werden.",
            )


class TestBf5LoadContextCheckpoint(unittest.TestCase):
    """BF-5 Abnahme: der neue Ladepunkt baut Kontext aus dem persoenlichen
    Current (derselbe bestehende `apply_compat_load=True`-Weg wie jeder
    echte Spielstart) und STOPPT danach -- kein Modellaufruf, kein neuer
    Abschnitt. Ein offener Kompatibilitaetsfall erscheint ueber GENAU
    diesen benannten Weg, waehrend die reine Bogen-Anzeige unberuehrt/
    kostenfrei bleibt (kein getarnter SL-Fresh-Load-PASS)."""

    def test_builds_context_and_halts_without_model_call_or_new_section(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
            run_dir, states_dir = d / "run", d / "states"
            stage4._make_ready_persona(onboarding_dir, states_dir, run_dir, "solo1")

            printed: list[str] = []
            session = TuiSession(
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="solo1",
                print_fn=printed.append,
                run_dir=run_dir, states_dir=states_dir, schema_path=stage4._SCHEMA_PATH,
                gm_transport_factory=stage4._SpyFactory("gm"),
                persona_driver_factory=stage4._SpyFactory("persona"),
            )

            session._cmd_load_context_checkpoint()

            out = "\n".join(printed)
            self.assertIn("Kontext fuer 'solo1' aus dem persoenlichen Current aufgebaut", out, out)
            self.assertIn("Halt vor dem ersten Spielzug", out, out)
            self.assertNotIn("PASS", out, out)
            self.assertFalse(list((run_dir / "tables").glob("*.json")), "kein neuer Abschnitt erwartet.")
            self.assertEqual(core_store.sections_played_by_participant(run_dir).get("solo1", 0), 0)

            # L1-Nachzug (RECOVERY_REVIEW/BUDGET_FLOW_REVIEW R2-BF-5): der
            # frueher geschlossene Befund war, dass die Meldung ALLEIN kein
            # Beweis fuer tatsaechlich aufgebauten Kontext ist -- jetzt MUSS
            # der gebundene Kontext selbst beobachtbar sein, mit identifizierbarem
            # eigenem Save-Inhalt/Owner (nicht nur der Erfolgstext).
            checkpoint = session._loaded_context_checkpoint
            self.assertIsNotNone(
                checkpoint, "der Ladepunkt haette den aufgebauten Kontext an die Sitzung binden muessen.",
            )
            self.assertEqual(checkpoint["persona_key"], "solo1")
            self.assertEqual(checkpoint["save"]["save_id"], "fixture-solo1-001")
            self.assertIn(
                "fixture-solo1-001", checkpoint["context"],
                f"der gebundene Kontext muss den EIGENEN Save-Inhalt (Save-ID) enthalten:\n{checkpoint['context']}",
            )

    def test_pending_compat_case_surfaces_via_named_path_not_via_bogen_read(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
            run_dir, states_dir = d / "run", d / "states"
            char_id = stage4._make_ready_persona(onboarding_dir, states_dir, run_dir, "guest1")

            # Ein noch NICHT adoptierter, neuerer Kompatibilitaetsumschlag --
            # derselbe Produktweg wie `core.save_correction.
            # _write_compat_export_on_exhaustion` (02_SAVEVERTRAG.md §D).
            newer_save = full_v7_save(char_id, name="guest1", save_id="fixture-guest1-n10-compat-002")
            save_compat_core.build_and_write_compat_export(
                run_dir, repair_key=f"repair-{char_id}", char_id=char_id, participant_id="guest1",
                operation_key=sc.ROLE_CREATION, table_id=None, section_id=None,
                best_view=newer_save, last_valid=None, created_ts=time.time(),
            )

            printed: list[str] = []
            session = TuiSession(
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="guest1",
                print_fn=printed.append,
                run_dir=run_dir, states_dir=states_dir, schema_path=stage4._SCHEMA_PATH,
                host_capable=False,
            )

            session._cmd_show_bogen()
            out_bogen = "\n".join(printed)
            self.assertNotIn(
                "Kompatibilitaetsladeweg", out_bogen,
                "die reine Bogen-Anzeige darf den Kompatibilitaets-Ladeweg NICHT ausloesen -- "
                f"sonst waere ein Bogen-Read als getarnter Fresh-Load-PASS wirksam:\n{out_bogen}",
            )

            printed.clear()
            session._cmd_load_context_checkpoint()
            out_checkpoint = "\n".join(printed)
            self.assertIn(
                "Kompatibilitaetsladeweg", out_checkpoint,
                f"der offene Kompatibilitaetsfall haette ueber den benannten Ladepunkt erscheinen "
                f"muessen:\n{out_checkpoint}",
            )
            self.assertIn("Halt vor dem ersten Spielzug", out_checkpoint, out_checkpoint)
            self.assertNotIn("PASS", out_checkpoint, out_checkpoint)

            # L1-Nachzug: der gebundene Kontext muss den ADOPTIERTEN
            # Kompatstand verwenden (nicht den alten Factory-Stand VOR der
            # Reparatur) -- derselbe bereits oben aufgeloeste Stand wird
            # konsistent weiterverwendet, kein zweiter, womoeglich erneut
            # reparierender Resolvercall.
            checkpoint = session._loaded_context_checkpoint
            self.assertIsNotNone(checkpoint)
            self.assertEqual(
                checkpoint["save"]["save_id"], "fixture-guest1-n10-compat-002",
                "der gebundene Kontext haette den ADOPTIERTEN Kompatstand binden muessen.",
            )
            self.assertIn(
                "fixture-guest1-n10-compat-002", checkpoint["context"],
                f"der adoptierte Save-Inhalt muss im gebundenen Kontext sichtbar sein:\n{checkpoint['context']}",
            )

    def test_compat_case_does_not_reconstruct_gm_transport_a_second_time(self):
        """L1-Nachzug (BUDGET_FLOW_REVIEW R2-BF-5 "NICHT bloss einen zweiten
        Resolvercall ... hinzufuegen"): `_apply_pending_compat_load`
        konstruiert bei konfigurierter SL/Host-Faehigkeit einen echten
        `gm_transport` UNBEDINGT vor seinem eigenen (intern idempotenten)
        `attempt_compat_load`-Aufruf (tui.py `_apply_pending_compat_load`,
        s. Docstring "Im Gastmodus bleibt gm_transport=None"). Ein naiver
        Fix, der `_own_system_context` einfach OHNE den bereits aufgeloesten
        Stand aufruft, wuerde intern ein ZWEITES Mal `_resolve_active_save`
        (und damit `_apply_pending_compat_load`) ausloesen und so die
        Factory ein zweites Mal aufrufen -- genau das verhindert die
        Wiederverwendung des bereits aufgeloesten `(final_save, unresolved)`
        ueber `_own_system_context(..., resolved_active_save=...)`."""
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
            run_dir, states_dir = d / "run", d / "states"
            char_id = stage4._make_ready_persona(onboarding_dir, states_dir, run_dir, "guest2")

            newer_save = full_v7_save(char_id, name="guest2", save_id="fixture-guest2-n10-compat-003")
            save_compat_core.build_and_write_compat_export(
                run_dir, repair_key=f"repair-{char_id}", char_id=char_id, participant_id="guest2",
                operation_key=sc.ROLE_CREATION, table_id=None, section_id=None,
                best_view=newer_save, last_valid=None, created_ts=time.time(),
            )

            class _CountingGmFactory:
                def __init__(self):
                    self.calls = 0

                def __call__(self, *args, **kwargs):
                    self.calls += 1
                    return object()

            gm_factory = _CountingGmFactory()
            printed: list[str] = []
            session = TuiSession(
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="guest2",
                print_fn=printed.append,
                run_dir=run_dir, states_dir=states_dir, schema_path=stage4._SCHEMA_PATH,
                host_capable=True, gm_transport_factory=gm_factory,
            )

            session._cmd_load_context_checkpoint()

            self.assertEqual(
                gm_factory.calls, 1,
                "die GM-Transport-Factory haette GENAU EINMAL (im eigentlichen "
                "Kompatladeweg) aufgerufen werden duerfen, nicht ein zweites Mal "
                "durch einen zusaetzlichen Resolvercall im Kontextaufbau.",
            )
            checkpoint = session._loaded_context_checkpoint
            self.assertIsNotNone(checkpoint)
            self.assertEqual(checkpoint["save"]["save_id"], "fixture-guest2-n10-compat-003")

    def test_known_unreadable_current_halts_without_binding_checkpoint(self):
        """L1-Abnahme-Gegenfall "bekannter unlesbarer Current": ein BEKANNTER,
        bereits veroeffentlichter Current kann gerade nicht gelesen werden
        (`store.CurrentSaveUnavailableError`) -- kontrollierter Stopp, KEIN
        Ersatzstand, KEIN gebundener Kontext (kein Vortaeuschen eines
        erfolgreichen Aufbaus)."""
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
            run_dir, states_dir = d / "run", d / "states"
            stage4._make_ready_persona(onboarding_dir, states_dir, run_dir, "solo3")

            ps_store = PersonaStateStore(schema_path=stage4._SCHEMA_PATH)
            version_path = core_store._current_save_version_path(
                run_dir, "solo3", ps_store, states_dir,
            )
            self.assertIsNotNone(version_path, "Testvoraussetzung: Current-Ref muss real aufloesbar sein.")

            printed: list[str] = []
            session = TuiSession(
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="solo3",
                print_fn=printed.append,
                run_dir=run_dir, states_dir=states_dir, schema_path=stage4._SCHEMA_PATH,
            )

            with _inject_one_shot_version_read_error(version_path) as hit:
                session._cmd_load_context_checkpoint()
            self.assertEqual(hit[0], 1, "Injektion muss tatsaechlich feuern.")

            out = "\n".join(printed)
            self.assertTrue(
                any("nicht moeglich" in p or "nicht lesbar" in p for p in printed), out,
            )
            self.assertIsNone(
                session._loaded_context_checkpoint,
                "ein bekannter, gerade nicht lesbarer Current darf NIE einen Kontext/Ersatzstand binden.",
            )

    def test_foreign_owner_never_leaks_into_another_personas_checkpoint(self):
        """L1-Abnahme-Gegenfall "falscher Owner": der fuer Figur A gebundene
        Kontext darf NIE den Save-Inhalt einer anderen Figur B zeigen --
        `_own_system_context`/`_resolve_active_save` bleiben strikt je
        `persona_key` geltungsbereichsbeschraenkt."""
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
            run_dir, states_dir = d / "run", d / "states"
            stage4._make_ready_persona(onboarding_dir, states_dir, run_dir, "ownera")
            stage4._make_ready_persona(onboarding_dir, states_dir, run_dir, "ownerb")

            session_a = TuiSession(
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="ownera",
                print_fn=lambda _s: None,
                run_dir=run_dir, states_dir=states_dir, schema_path=stage4._SCHEMA_PATH,
            )
            session_a._cmd_load_context_checkpoint()
            checkpoint_a = session_a._loaded_context_checkpoint
            self.assertIsNotNone(checkpoint_a)
            self.assertEqual(checkpoint_a["save"]["save_id"], "fixture-ownera-001")
            self.assertIn("fixture-ownera-001", checkpoint_a["context"])
            self.assertNotIn(
                "fixture-ownerb-001", checkpoint_a["context"],
                f"ownerAs Kontext darf ownerBs Save-Inhalt NICHT enthalten:\n{checkpoint_a['context']}",
            )

            session_b = TuiSession(
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="ownerb",
                print_fn=lambda _s: None,
                run_dir=run_dir, states_dir=states_dir, schema_path=stage4._SCHEMA_PATH,
            )
            session_b._cmd_load_context_checkpoint()
            checkpoint_b = session_b._loaded_context_checkpoint
            self.assertIsNotNone(checkpoint_b)
            self.assertEqual(checkpoint_b["save"]["save_id"], "fixture-ownerb-001")
            self.assertNotIn(
                "fixture-ownera-001", checkpoint_b["context"],
                f"ownerBs Kontext darf ownerAs Save-Inhalt NICHT enthalten:\n{checkpoint_b['context']}",
            )


class TestBf5CharaktereMenuLoadCheckpointEntry(unittest.TestCase):
    """BF-5 Umsetzungsform Punkt 2 (Wiring): [7] erscheint fest (kollidiert
    nicht mit den bedingten [4]/[5]) und dispatcht auf
    `_cmd_load_context_checkpoint`; [1]/[2]/[3]/[6] bleiben unveraendert."""

    def test_entry_7_shown_and_dispatches(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            calls: list[str] = []
            session = TuiSession(
                onboarding_dir=root / "onboarding", catalog_dir=root / "catalog",
                participant_id="host1", input_fn=lambda prompt="": "7",
                host_capable=True,
            )
            session._cmd_load_context_checkpoint = lambda: calls.append("called")
            printed: list[str] = []
            session._print = printed.append

            session._cmd_menu_charaktere()

            out = "\n".join(printed)
            self.assertIn("[7] Laden/Kontext aufbauen (Halt vor erstem Zug)", out, out)
            self.assertIn("[1] Auswaehlen/neu erstellen", out, out)
            self.assertIn("[2] Importieren", out, out)
            self.assertIn("[3] Exportieren/ansehen", out, out)
            self.assertIn("[6] Bogen anzeigen", out, out)
            self.assertEqual(calls, ["called"])


class TestBf5CorrectedWegweiser(unittest.TestCase):
    """BF-5 Umsetzungsform Punkt 1: der Kompatibilitaets-Hinweis in
    `render_boot_menu` nennt "Export" nicht mehr (kein erreichbarer
    Reparaturweg, s. `_cmd_export`)."""

    def test_pending_compat_hint_no_longer_mentions_export(self):
        card = ResumeCard(
            community_id=None, participant_id="guest1", chrononaut_id="CHR-GUEST1",
            last_valid_save_summary="Stand", open_section_id=None, pending_compat_load=True,
        )
        text = render_boot_menu(card, host_capable=True)
        self.assertNotIn("Export", text, text)
        self.assertIn("Laden/Kontext aufbauen", text, text)


if __name__ == "__main__":
    unittest.main()
