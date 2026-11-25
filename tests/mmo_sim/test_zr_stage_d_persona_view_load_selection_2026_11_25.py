#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_stage_d_persona_view_load_selection_2026_11_25.py —
Stage D (Linus-Integratorauftrag, 02_ANSCHLUSS.md §2, REVIEW.md §6):

Im bestehenden Charaktere-Untermenue (`TuiSession._cmd_menu_charaktere`)
macht ein neuer, additiver Auswahlschritt (`_select_managed_persona_or_
self`) eine bereits BERECHTIGT VERWALTETE Persona aus dem eigenen
bestaetigten Bestand (`_known_ai_overview()`, dieselbe Lesequelle wie
`_cmd_community`/die KI-Auswahl in `_local_round_select_ai`) fuer die
vorhandenen Aktionen [6] "Bogen ansehen" (`_cmd_show_bogen`) und [7]
"Laden/Kontext aufbauen" (`_cmd_load_context_checkpoint`) erreichbar --
beide binden bisher NUR `self.participant_id`.

Deckt ab:
- genau die gewaehlte berechtigte Persona wird angezeigt/geladen;
- zwei unterschiedliche persoenliche Saves werden NICHT vertauscht;
- reine Ansicht ohne Writes/Modell-Calls (auch ohne Modellanbindung
  nutzbar -- GM-/Persona-Factories werfen SOFORT bei Aufruf, s.
  `test_stage4_capability_gate_2026_11_02.py:_SpyFactory`);
- Rueckkehr/Leerwert/unerlaubte/fremde Auswahl bleibt folgenlos;
- echter zielgebundener Kontext-Checkpoint OHNE Tischstart;
- vorhandene eigene [6]/[7]-Wege (ohne Bestand, bytegleich) bleiben intakt;
- `self.participant_id`/`last_participant.json`/Registrierung/Kampagne
  bleiben unveraendert.

Reuse (Leitprinzip "Reuse vor Neubau"): Bootstrap-Fixtures aus
`_a24_local_support.py` (`bootstrap_six_persona_community`, `make_ready`)
und `test_stage4_capability_gate_2026_11_02.py` (`_make_ready_persona`,
`_SCHEMA_PATH`, `_SpyFactory`) -- importiert als Module, kein zweiter
Bootstrap-Code. Pure `unittest.TestCase`, ISOLIERTE `tempfile`-Daten,
NIEMALS die Live-Produktionswurzel."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import _a24_local_support as sup  # noqa: E402
import test_stage4_capability_gate_2026_11_02 as stage4  # noqa: E402

from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402


def _scripted_input(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


def _build_session(root: Path, pid: str, *, input_fn, printed: list[str], completed_personas=("cqb", "face")):
    """Baut EINE isolierte Session mit einem nicht-leeren eigenen Bestand
    (sechs KI-Personas, `_a24_local_support.bootstrap_six_persona_
    community`, derselbe Produktweg wie `_cmd_community`) UND einer echten
    eigenen Figur fuer `pid` selbst (`stage4._make_ready_persona`,
    DIESELBE Fixturefolge wie die bestehenden BF-5-Tests). `completed_
    personas` erhalten zusaetzlich ihre ECHTE, bereits abgeschlossene
    v7-Figur (`_a24_local_support.make_ready`, derselbe Produktweg wie
    eine echte abgeschlossene Erschaffung) -- die restigen Bestandsmit-
    glieder bleiben bewusst bei 'NOCH_NICHT_ERSCHAFFEN' (ungenutzte
    Bystander, reines Bestandsrauschen). GM-/Persona-Factories sind
    `_SpyFactory`-Instanzen -- werfen SOFORT bei Aufruf, der staerkste
    Nachweis fuer 'Ansehen/Auswaehlen = 0 Calls' (UX03/UX10, auch OHNE
    aktive Modellanbindung nutzbar)."""
    community_id = f"community-{pid}"
    env = sup.bootstrap_six_persona_community(root, community_id)
    stage4._make_ready_persona(env["onboarding_dir"], env["states_dir"], env["run_dir"], pid)
    for persona_key in completed_personas:
        sup.make_ready(env["onboarding_dir"], env["states_dir"], env["run_dir"], persona_key)
    session = TuiSession(
        onboarding_dir=env["onboarding_dir"], catalog_dir=env["catalog_dir"], participant_id=pid,
        input_fn=input_fn, print_fn=printed.append,
        run_dir=env["run_dir"], states_dir=env["states_dir"], schema_path=env["schema"],
        gm_transport_factory=stage4._SpyFactory("gm"), persona_driver_factory=stage4._SpyFactory("persona"),
    )
    return session, env


class TestStageDSelectAndViewManagedPersona(unittest.TestCase):
    """Bullet 1/3: genau die gewaehlte berechtigte Persona wird angezeigt
    -- reine Ansicht, 0 Persona-/GM-Calls, auch ohne Modellanbindung."""

    def test_entry_6_selection_shows_exactly_the_chosen_persona_sheet(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            printed: list[str] = []
            session, _env = _build_session(
                root, "selfpid", input_fn=_scripted_input(["6", "1"]), printed=printed,
            )

            overview = session._known_ai_overview()
            self.assertTrue(overview, "Testvoraussetzung: eigener Bestand muss nicht-leer sein.")
            self.assertEqual([pk for pk, _l in overview][0], "cqb", overview)

            session._cmd_menu_charaktere()

            # Der eigentliche Bogen ist der LETZTE `_print`-Aufruf (ein
            # einziger "\n".join(lines)-Block, s. `_cmd_show_bogen`) --
            # die VORGELAGERTE Auswahlliste nennt bewusst auch die eigene
            # Figur ("[0] Eigene Figur (selfpid)") als Orientierung, das
            # ist NICHT der tatsaechlich angezeigte Bogen.
            sheet = printed[-1]
            self.assertIn("Name: Krag", sheet, sheet)
            self.assertIn("Callsign: CQB", sheet, sheet)
            self.assertNotIn("selfpid", sheet, f"der EIGENE Save darf im angezeigten Bogen NICHT erscheinen:\n{sheet}")
            self.assertFalse(
                list((_env["run_dir"] / "tables").glob("*.json")),
                "reine Ansicht darf keinen Tisch/Abschnitt anlegen.",
            )


class TestStageDTwoPersonasNotSwapped(unittest.TestCase):
    """Bullet 2: zwei unterschiedliche persoenliche Saves werden NICHT
    vertauscht -- je Auswahl GENAU der zugehoerige Save, kein Leaken des
    jeweils anderen."""

    def test_two_different_managed_personas_show_distinct_sheets(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            printed: list[str] = []
            session, _env = _build_session(
                root, "selfpid", input_fn=_scripted_input(["6", "1"]), printed=printed,
            )
            session._cmd_menu_charaktere()
            # Der tatsaechlich angezeigte Bogen ist der LETZTE Print (die
            # vorgelagerte Auswahlliste nennt zur Orientierung beide
            # Bestandsmitglieder, das ist NICHT der angezeigte Bogen).
            sheet_cqb = printed[-1]
            self.assertIn("Krag", sheet_cqb, sheet_cqb)
            self.assertNotIn("Elias", sheet_cqb, sheet_cqb)

            printed.clear()
            session._input = _scripted_input(["6", "2"])
            session._cmd_menu_charaktere()
            sheet_face = printed[-1]
            self.assertIn("Elias", sheet_face, sheet_face)
            self.assertIn("Callsign: FACE", sheet_face, sheet_face)
            self.assertNotIn("Krag", sheet_face, sheet_face)


class TestStageDLoadBuildsTargetedCheckpointNoTableStart(unittest.TestCase):
    """Bullet 5 (+ identitaets-/registrierungsfreier Nebeneffekt, Bullet 4
    im 02_ANSCHLUSS.md-Sinn): [7] mit Auswahl baut einen echten,
    zielgebundenen Kontext-Checkpoint fuer die GEWAEHLTE Persona -- ohne
    Tischstart/neuen Abschnitt, ohne Identitaetswechsel der Sitzung."""

    def test_entry_7_selection_binds_checkpoint_to_chosen_persona_without_table_start(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            printed: list[str] = []
            session, env = _build_session(
                root, "selfpid", input_fn=_scripted_input(["7", "1"]), printed=printed,
            )

            session._cmd_menu_charaktere()

            out = "\n".join(printed)
            self.assertIn("Kontext fuer 'cqb' aus dem persoenlichen Current aufgebaut", out, out)
            self.assertIn("Halt vor dem ersten Spielzug", out, out)

            checkpoint = session._loaded_context_checkpoint
            self.assertIsNotNone(checkpoint, "der Ladepunkt haette den Kontext an die Sitzung binden muessen.")
            self.assertEqual(checkpoint["persona_key"], "cqb")
            self.assertEqual(checkpoint["save"]["save_id"], "fixture-cqb-initial-001")
            self.assertIn("Krag", checkpoint["context"], checkpoint["context"])

            # kein neuer Abschnitt/Tisch, weder fuer die Zielpersona noch fuer self.
            self.assertFalse(list((env["run_dir"] / "tables").glob("*.json")), "kein neuer Tisch erwartet.")
            self.assertEqual(core_store.sections_played_by_participant(env["run_dir"]).get("cqb", 0), 0)
            self.assertEqual(core_store.sections_played_by_participant(env["run_dir"]).get("selfpid", 0), 0)

            # Bullet 4 (02_ANSCHLUSS.md §2): KEIN Identitaetswechsel der
            # handelnden Session -- `self.participant_id` bleibt die
            # AEUSSERE Person, obwohl der Kontext fuer 'cqb' gebunden wurde.
            self.assertEqual(session.participant_id, "selfpid")
            self.assertFalse((root / "last_participant.json").exists())


class TestStageDSelectionItselfIsConsequenceFree(unittest.TestCase):
    """Bullet 4 (02_ANSCHLUSS.md §2 'Leere/Zurueck-/ungueltige/fremde
    Auswahl bleibt folgenlos'): Rueckkehr, Leerwert, eine Zahl ausserhalb
    der Liste und nicht-numerischer Text loesen KEINE Aktion aus --
    `_select_managed_persona_or_self()` liefert in jedem Fall `None`, der
    Menuecaller `continue`t zurueck ins Charaktere-Untermenue OHNE
    Bogen-/Ladeaufruf. Da `gm_transport_factory`/`persona_driver_factory`
    beide `_SpyFactory`-Instanzen sind (werfen SOFORT bei Aufruf), beweist
    bereits das fehlerfreie Durchlaufen 0 Persona-/GM-Calls."""

    def _assert_no_action_for(self, second_input: str, *, expect_message: bool):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            printed: list[str] = []
            # Reihenfolge: "6" (Bogen) -> Auswahlschritt bekommt `second_input`
            # -> folgenlos -> `continue` zeigt das Untermenue erneut ->
            # "/zurueck" verlaesst dieses Untermenue kontrolliert.
            session, _env = _build_session(
                root, "selfpid",
                input_fn=_scripted_input(["6", second_input, "/zurueck"]), printed=printed,
            )
            session._cmd_menu_charaktere()
            out = "\n".join(printed)
            self.assertNotIn("Name:", out, f"keine Aktion erwartet, aber Bogen erschien:\n{out}")
            self.assertNotIn("Kontext fuer", out, out)
            self.assertIsNone(session._loaded_context_checkpoint)
            if expect_message:
                self.assertIn("Unbekannte Auswahl", out, out)

    def test_return_control_stays_without_effect(self):
        self._assert_no_action_for("/zurueck", expect_message=False)

    def test_empty_value_stays_without_effect(self):
        self._assert_no_action_for("", expect_message=False)

    def test_out_of_range_number_stays_without_effect(self):
        self._assert_no_action_for("99", expect_message=True)

    def test_non_numeric_text_stays_without_effect(self):
        self._assert_no_action_for("keine-gueltige-id", expect_message=True)


class TestStageDExistingEntriesWithoutBestandStayByteIdentical(unittest.TestCase):
    """Bullet 'vorhandene eigene [6]/[7]-Wege ... bleiben intakt
    (Regressionsschutz)': OHNE eigenen bestaetigten Bestand (der heute
    ueberwiegende Default-Fall, `run_dir=None` oder eine leere Community)
    liefert `_select_managed_persona_or_self()` SOFORT `self.participant_
    id` zurueck, OHNE einen zusaetzlichen Prompt zu lesen -- [6]/[7]
    wirken dann bytegleich auf die eigene Figur wie vor Stage D."""

    def test_entry_6_and_7_without_bestand_act_on_self_with_single_input_each(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
            run_dir, states_dir = root / "run", root / "states"
            stage4._make_ready_persona(onboarding_dir, states_dir, run_dir, "solo1")

            printed: list[str] = []
            session = TuiSession(
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="solo1",
                input_fn=_scripted_input(["6"]), print_fn=printed.append,
                run_dir=run_dir, states_dir=states_dir, schema_path=stage4._SCHEMA_PATH,
                gm_transport_factory=stage4._SpyFactory("gm"), persona_driver_factory=stage4._SpyFactory("persona"),
            )
            self.assertEqual(session._known_ai_overview(), [], "Testvoraussetzung: Bestand muss leer sein.")

            session._cmd_menu_charaktere()
            out = "\n".join(printed)
            self.assertIn("Name:", out, out)
            self.assertIn("solo1", out, out)

            printed.clear()
            session._input = _scripted_input(["7"])
            session._cmd_menu_charaktere()
            out2 = "\n".join(printed)
            self.assertIn("Kontext fuer 'solo1' aus dem persoenlichen Current aufgebaut", out2, out2)
            checkpoint = session._loaded_context_checkpoint
            self.assertIsNotNone(checkpoint)
            self.assertEqual(checkpoint["persona_key"], "solo1")

    def test_entry_7_dispatch_still_matches_prior_no_arg_mock_contract(self):
        """Dieselbe Pruefform wie die bestehende BF-5-Wiring-Regression
        (`test_n10_bf4_bf5_resume_and_loadpoint_20261124_r1.py:
        TestBf5CharaktereMenuLoadCheckpointEntry`): ein Mock OHNE jedes
        Argument muss weiterhin funktionieren, solange kein Bestand
        existiert -- bytegleicher Dispatch, kein neues Pflichtargument
        fuer den haeufigen Default-Fall."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            calls: list[str] = []
            session = TuiSession(
                onboarding_dir=root / "onboarding", catalog_dir=root / "catalog",
                participant_id="host1", input_fn=_scripted_input(["7"]),
            )
            session._cmd_load_context_checkpoint = lambda: calls.append("called")
            printed: list[str] = []
            session._print = printed.append

            session._cmd_menu_charaktere()

            self.assertEqual(calls, ["called"])


class TestStageDExplicitSelfSelectionWithBestand(unittest.TestCase):
    """'0' waehlt explizit die eigene Figur, auch WENN ein eigener Bestand
    existiert -- zeigt/laedt weiterhin die EIGENE Figur, kein versehentlich
    an den Bestand gebundenes Verhalten."""

    def test_choosing_zero_with_nonempty_bestand_still_shows_own_sheet(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            printed: list[str] = []
            session, _env = _build_session(
                root, "selfpid", input_fn=_scripted_input(["6", "0"]), printed=printed,
            )
            session._cmd_menu_charaktere()
            sheet = printed[-1]
            self.assertIn("Name: selfpid", sheet, sheet)
            self.assertNotIn("Krag", sheet, sheet)
            self.assertNotIn("Elias", sheet, sheet)


if __name__ == "__main__":
    unittest.main()
