#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_w28_r7b_export_admission_privacy_gaps_2026_10_06.py —
W28 (ZEITRISS Terminal UX-1, R7 Phase B): drei eng begrenzte Testluecken aus
den vier ORIGINAL-Faellen UX16/UX17/UX19/UX20 (`reference/previous-order/
ORIGINAL-CASES.json`), NACH Zuordnung der bereits bestehenden Belege
(s. `worker/W28/checkpoints/cp1-mapping-and-gaps.md`). Alle drei Luecken
sind reine Testluecken, KEIN Core-/Domain-/Adapter-Defekt -- jeweils real
ueber `TuiSession._cmd_export`/`_cmd_community`/`_cmd_local_round` belegt
(kein Mock der Domaenenfunktionen).

1. UX16: der echte persoenliche JSON-Export (`_cmd_export`) laesst ein
   erlaubtes v7-Extensionfeld UNGEFILTERT durch, enthaelt aber NIE eine
   echte private Notiz (ueber den echten Notizpfad erzeugt) -- kein
   Notes-/Key-/Frameworkhuelle-Leck.
2. UX19: das Admission-Gate blockiert JEDE externe Anfrage auch dann, wenn
   die [d/p]-Herkunftsfrage ausdruecklich mit 'p' (produktiv) beantwortet
   wird -- bisher war nur die geschlossene Gate-Variante mit 'd' belegt.
3. UX20: zwei eigene synthetische Menschen mit je einer echten privaten
   Notiz (eigener Marker) -- keine Notiz von A erscheint im Export, in der
   eigenen `/stand`-Karte oder im Tisch-Payload von B, und umgekehrt.

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

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, COMPLETION_MARKER  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


def _scripted(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


class _OneShotCompletingGm:
    """Identischer Baustein wie
    `test_ux1_g04_purpose_stand_verlauf_2026_10_05.py::_OneShotCompletingGm`
    (kein neuer Fake-Mechanismus): liefert beim ERSTEN Aufruf sofort den
    Abschluss-Marker + Save-Block -- genau EIN echter Spielzug, danach
    `finalize()`/`_collect_reflections()` (die echte freiwillige
    Notizabfrage)."""

    def __init__(self, char_id: str, save_block: dict):
        self._char_id = char_id
        self._save_block = save_block
        self.calls = 0

    def turn(self, turn_idx, text, **kw):
        self.calls += 1
        content = (
            f"Abschnitt beendet.\n```json\n{json.dumps(self._save_block)}\n```\n"
            f"{COMPLETION_MARKER}"
        )
        return {"content": content}


def _onboard_solo(onboarding_dir: Path, participant_id: str, save_block: dict, char_id: str) -> None:
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save_block, ZeitrissHarvestValidator(), char_id)


def _reflections(run_dir: Path) -> list[dict]:
    path = run_dir / "reflections.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


# ---------------------------------------------------------------------------
# UX16: Exportinhalt-Reinheit -- v7-Extensionfeld bleibt, private Notiz nie.
# ---------------------------------------------------------------------------

def test_ux16_export_keeps_v7_extension_field_but_excludes_real_private_note():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = d / "run", d / "states", d / "onboarding", d / "catalog"
        exports_dir = d / "exports"
        write_test_profile(run_dir)
        participant_id = "testspieler_a"
        char_id = "testfigur-a01"
        # W50 FIXTURE_ONLY (R12-Savegate, 02_TEAM_UND_QUELLRAHMEN.md
        # "Testfixtures versus Schutzassertionen", derselbe Helfer-Umbau wie
        # bereits W45 fuer UX20 in dieser Datei): die alte winzige Fixture
        # mit einem FREI ERFUNDENEN Root-Schluessel (`_mod_extension_field`
        # direkt auf Blockebene) wird von der jetzt durchgesetzten
        # R12-Vollschema-Pruefung (`save_validation.validate_structure`,
        # BEIDE v7-Schemas) abgelehnt -- das strikte Exportschema hat
        # `additionalProperties: false` auf Root-UND-Figurebene (bestaetigt
        # per `validate_structure`-Probe). Das echte, bewusst offene
        # Erweiterungsfeld des Vertrags ist `characters[].history`
        # (`additionalProperties: true`, zusammen mit `.prestige`/
        # `logs.flags`/`research.projects[]` die EINZIGEN schema-definierten
        # Freiformstellen) -- das erfuellt den Testzweck ("ein ERLAUBTES
        # v7-Extensionfeld bleibt ungefiltert im Export erhalten") sogar
        # praeziser als die alte freie Rootplatzierung, die nie gegen ein
        # Schema geprueft war. Negativwert/Markerstring unveraendert.
        save_block = full_v7_save(
            char_id, name="Testfigur A01", level=3, save_id="ux16-export-purity-001",
            history={"_mod_extension_field": "ARTIFICIAL-EXT-MARKER-7788"},
        )
        _onboard_solo(onboarding_dir, participant_id, save_block, char_id)
        ps_store = PersonaStateStore(schema_path=_SCHEMA)
        onboarding.ensure_participant_persona_state(ps_store, states_dir, participant_id, char_id, save_block)
        core_store.publish_current_save(run_dir, participant_id, save_block, ps_store, states_dir)

        # Echte private Notiz ueber den echten Notizpfad (ein voller
        # Abschnittsabschluss ueber `_cmd_local_round`, keine direkt
        # geschriebene reflections.jsonl-Zeile).
        printed_round: list[str] = []
        gm = _OneShotCompletingGm(char_id, save_block)
        round_session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=participant_id,
            input_fn=_scripted([
                "Testspieler-A-Zug 1 (Anker, loest Abschluss aus).",
                "ARTIFICIAL-PRIVATE-NOTE-MARKER-9911",
            ]),
            print_fn=printed_round.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda: gm, persona_driver_factory=None,
        )
        try:
            round_session._cmd_local_round([])
        except EndOfInput:
            pass
        human_notes = [r for r in _reflections(run_dir) if r.get("kind") == "human_note"]
        assert len(human_notes) == 1 and human_notes[0]["text"] == "ARTIFICIAL-PRIVATE-NOTE-MARKER-9911", human_notes

        # Jetzt der echte persoenliche Export an den eigenen UI-Prompts.
        printed_export: list[str] = []
        export_session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=participant_id,
            print_fn=printed_export.append, exports_dir=exports_dir,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
        )
        export_session._cmd_export()

        export_path = exports_dir / f"{participant_id.replace('/', '_')}.json"
        assert export_path.is_file(), printed_export
        exported_text = export_path.read_text(encoding="utf-8")
        exported_block = json.loads(exported_text)

        # Gleicher Char-/Versionsbezug: vollstaendiger, unveraenderter Block
        # (der tatsaechlich publizierte Current, nicht nur der Onboarding-
        # Entwurf -- derselbe Stand, der auch der echte Spielzug oben nutzte).
        assert exported_block == save_block, exported_block
        # W50 FIXTURE_ONLY: `full_v7_save` liefert `id` statt des alten
        # redundanten `char_id`-Zweitschluessels (s. Helfer-Docstring,
        # bereits W47-abgenommene kanonische Form).
        assert exported_block["characters"][0]["id"] == char_id

        # v7-Extensionfeld bleibt UNGEFILTERT erhalten -- jetzt am echten
        # schema-definierten Freiformpunkt `characters[].history` (s.
        # FIXTURE_ONLY-Begruendung oben).
        assert exported_block["characters"][0]["history"].get("_mod_extension_field") == (
            "ARTIFICIAL-EXT-MARKER-7788"
        ), exported_block

        # Keine Notes/Keys/Frameworkhuelle: der Marker der echten privaten
        # Notiz darf WEDER in der Exportdatei NOCH in der Druckausgabe
        # auftauchen -- weder "reflections" noch "human_note" als Spur.
        combined = exported_text + "\n".join(printed_export)
        assert "ARTIFICIAL-PRIVATE-NOTE-MARKER-9911" not in combined, combined
        assert "reflections" not in combined, combined
        assert "human_note" not in combined, combined


# ---------------------------------------------------------------------------
# UX19: Admission-Gate blockiert auch bei ausdruecklich gewaehltem 'p'
# (produktiv) -- bisher nur fuer 'd' belegt (`test_p2_community_creation.py::
# test_cmd_community_without_model_config_stays_honest_partial_state_like_baseline`).
# ---------------------------------------------------------------------------

def test_ux19_admission_gate_closed_blocks_even_with_explicit_production_choice():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path = _SCHEMA
        states_dir, run_dir = root / "states", root / "run"
        onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
        states_dir.mkdir(parents=True, exist_ok=True)
        run_dir.mkdir(parents=True, exist_ok=True)
        # KEIN write_test_profile() -- keine lab.status.json, Admission-Gate
        # blockiert fail-closed (wie am echten Terminal ohne Live-Setup).
        printed: list[str] = []

        def _queue(answers):
            it = iter(answers)

            def _fn(prompt: str = "") -> str:
                try:
                    return next(it)
                except StopIteration:
                    raise EOFError()
            return _fn

        session = TuiSession(
            onboarding_dir, catalog_dir, "human_caller_prod_closed_gate",
            # 'p': ausdrueckliche PRODUKTIVE Herkunftsentscheidung -- die
            # Factories sind konfiguriert (sonst wuerde die [d/p]-Frage gar
            # nicht gestellt), werfen aber AssertionError, falls sie
            # tatsaechlich fuer einen Modellaufruf erreicht wuerden.
            input_fn=_queue(["p"]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=lambda *_a, **_kw: (_ for _ in ()).throw(
                AssertionError("kein Modellaufruf ohne Admission-Freigabe erwartet (Herkunft 'p')")
            ),
            persona_driver_factory=lambda pk: (_ for _ in ()).throw(
                AssertionError("kein Modellaufruf ohne Admission-Freigabe erwartet (Herkunft 'p')")
            ),
        )
        session._cmd_community()

        # Die produktive Herkunftsentscheidung selbst wurde ausdruecklich
        # verarbeitet (kein stilles Umdeuten auf Demo) ...
        assert any("PRODUKTIVE Neuanlage bewusst gewaehlt" in line for line in printed), printed
        plan = run_dir / "community" / "bootstrap__plan.json"
        assert plan.is_file(), printed
        personas = json.loads(plan.read_text(encoding="utf-8"))["personas"]
        assert len(personas) == 8
        for payload in personas.values():
            assert "SIMULIERT" not in payload.get("_fixture_note", ""), payload
            assert "PRODUKTIV" in payload.get("_fixture_note", ""), payload

        # ... aber die Admission-Gate-geschuetzte Erschaffungsfortsetzung
        # bleibt UNABHAENGIG von der Herkunft blockiert: 0 echte Calls,
        # keine spielbereite Persona, "blocked" sichtbar.
        ps_store = PersonaStateStore(schema_path=schema_path)
        ready = [
            pk for pk in personas
            if core_store.load_current_save_or_raise(run_dir, pk, ps_store, states_dir=states_dir) is not None
        ]
        assert ready == [], "ohne Admission-Freigabe darf auch bei 'p' keine Persona spielbereit werden"
        assert any("blocked" in line for line in printed), printed


# ---------------------------------------------------------------------------
# UX20: zwei eigene synthetische Menschen, zwei eigene private Marker --
# keine Notiz von A im Export/Stand/Tisch-Payload von B, und umgekehrt.
# ---------------------------------------------------------------------------

def test_ux20_two_humans_private_notes_never_cross_into_the_others_export_stand_or_table_payload():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = d / "run", d / "states", d / "onboarding", d / "catalog"
        exports_dir = d / "exports"
        write_test_profile(run_dir)
        ps_store = PersonaStateStore(schema_path=_SCHEMA)

        people = [
            ("testspieler_a", "testfigur-a01", "A-MARKER-NOTE-1234"),
            ("testspieler_b", "testfigur-b01", "B-MARKER-NOTE-5678"),
        ]
        for participant_id, char_id, note_marker in people:
            save_block = full_v7_save(char_id, name=char_id, save_id=f"ux20-{char_id}-001")
            _onboard_solo(onboarding_dir, participant_id, save_block, char_id)
            onboarding.ensure_participant_persona_state(ps_store, states_dir, participant_id, char_id, save_block)
            core_store.publish_current_save(run_dir, participant_id, save_block, ps_store, states_dir)

            printed_round: list[str] = []
            gm = _OneShotCompletingGm(char_id, save_block)
            session = TuiSession(
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=participant_id,
                input_fn=_scripted([
                    f"{participant_id}-Zug 1 (Anker, loest Abschluss aus).",
                    note_marker,
                ]),
                print_fn=printed_round.append,
                run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
                gm_transport_factory=lambda: gm, persona_driver_factory=None,
            )
            try:
                session._cmd_local_round([])
            except EndOfInput:
                pass

        all_reflections = _reflections(run_dir)
        human_notes_by_pk = {
            r["persona_key"]: r["text"] for r in all_reflections if r.get("kind") == "human_note"
        }
        assert human_notes_by_pk.get("testspieler_a") == "A-MARKER-NOTE-1234", human_notes_by_pk
        assert human_notes_by_pk.get("testspieler_b") == "B-MARKER-NOTE-5678", human_notes_by_pk

        other_marker = {"testspieler_a": "B-MARKER-NOTE-5678", "testspieler_b": "A-MARKER-NOTE-1234"}
        for participant_id, char_id, own_marker in people:
            # (1) Export: nie die fremde Notiz, nie die eigene Notiz
            # (Export ist der Save, nicht die Reflexion).
            printed_export: list[str] = []
            export_session = TuiSession(
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=participant_id,
                print_fn=printed_export.append, exports_dir=exports_dir,
                run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            )
            export_session._cmd_export()
            export_path = exports_dir / f"{participant_id.replace('/', '_')}.json"
            exported_text = export_path.read_text(encoding="utf-8")
            combined_export = exported_text + "\n".join(printed_export)
            assert other_marker[participant_id] not in combined_export, combined_export
            assert own_marker not in combined_export, combined_export

            # (2) GM-/Tisch-Payload: der eigene Tisch (`local-<id>.json`)
            # enthaelt nie die fremde Notiz (strukturell sowieso getrennte
            # Tische, aber hier real belegt statt angenommen).
            table_file = run_dir / "tables" / f"local-{participant_id}.json"
            table_data = json.loads(table_file.read_text(encoding="utf-8"))
            table_blob = json.dumps(table_data, ensure_ascii=False)
            assert other_marker[participant_id] not in table_blob, table_blob
            assert own_marker not in table_blob, "private Notiz darf NIE im Tisch-/SL-Payload landen (UX14/UX20)"

            # (3) `/stand` (eigene Fortsetzen-Karte) zeigt nie die fremde
            # Notiz -- `/stand` traegt ueberhaupt keine Reflexionen, real
            # belegt ueber denselben zentralen Leser wie am echten Terminal.
            stand_printed: list[str] = []
            stand_session = TuiSession(
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=participant_id,
                input_fn=_scripted(["/stand", "echter Zug nach /stand (fuer Testabschluss)."]),
                print_fn=stand_printed.append,
                run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            )
            text, control = stand_session._readline_with_controls(
                "Frage: ", context="Spielzug",
            )
            assert control is None and text == "echter Zug nach /stand (fuer Testabschluss)."
            stand_blob = "\n".join(stand_printed)
            assert other_marker[participant_id] not in stand_blob, stand_blob
            assert own_marker not in stand_blob, stand_blob


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
