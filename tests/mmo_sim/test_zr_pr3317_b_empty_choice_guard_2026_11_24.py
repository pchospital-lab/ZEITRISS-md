#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_pr3317_b_empty_choice_guard_2026_11_24.py -- ZR-PR3317-
NACHZUG-20261124 Aufgabe B (02_NACHZUG.md Abschnitt B, REVIEW.md Abschnitt 4):
dauerhafter Regressionstest fuer den Leerwert-/Whitespace-Fix in
`TuiSession._cmd_new_or_switch_character()`.

Altprobe (REVIEW.md Abschnitt 4, quellbestaetigt auf `main`): bei bereits
vorhandenen Figuren faellt ein blosses Enter (Leerstring) ODER reiner
Whitespace NACH `choice.strip()` mangels Treffer in BEIDEN Pruefzweigen
(`fortsetzen:`-Praefix, 'Nummer/Name ungleich neu/n/new') bis zu
`force_new = True` durch und loest darueber `onboarding.bind_attempt()` samt
nachfolgendem (potenziell kostenpflichtigem) Erschaffungsdialog aus, OHNE dass
der Mensch 'neu' gewaehlt hat.

Diese Datei treibt GENAU den echten Caller (`TuiSession._cmd_new_or_switch_
character`), keine Kopie/Nachbildung der Auswahllogik. Test-Doubles nur an
den aeussersten Grenzen (Eingabe/Druck/GM-Transport/`onboarding.bind_attempt`
als Sentinel), echter Produktweg darunter (`onboarding`/`catalog`/`core.store`).
Isolierte temporaere Daten (`tmp_path`), NIE Live-Originale. Kein Netzwerk,
kein echter Modellaufruf, kein Live-Spielzug.

Deckt (B.1) Leerstring UND reiner Whitespace bei vorhandenen Figuren: kein
`force_new`, kein `onboarding.bind_attempt`-Aufruf, kein Request/Transport,
kein zusaetzlicher Onboarding-/Figuren-/Savewrite -- der Mensch wird erneut
gefuehrt (Hinweistext + `return`, derselbe Rueckweg wie bei einer ungueltigen
Auswahl). (B.2) Gegenfaelle bleiben unveraendert: bestehende Figur per Nummer
-> `_switch_active_figure`; explizit 'neu' -> force_new-Pfad (Host-Gate)
erreicht; '/zurueck'/'/abbrechen' -> reguläre Steuerung; 'fortsetzen:<id>' ->
Resume-Pfad. (B.3) Erstaufruf ohne vorhandene Figur (`entries` leer) bleibt
von diesem Guard unberuehrt (der Guard liegt innerhalb des `if entries:`-
Zweigs) und erreicht weiterhin die reguläre Erst-Erschaffung.

Pure Python, nur `assert`, echter Exitcode (ueber `main()`/`pytest`-kompatibel,
da nur Funktionen `test_*` ohne Fixtures)."""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.community_creation import (  # noqa: E402
    advance_additional_persona_creation,
    find_resumable_additional_creation,
)
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


# ---------------------------------------------------------------------------
# Gemeinsame Helfer (reine Wiederverwendung des echten Produktwegs fuer das
# Setup -- Vorbild `test_n1_n7_persona_additional_figure_2026_10_02.py:
# _new_env`/`_give_existing_figure`).
# ---------------------------------------------------------------------------

def _new_env(root: Path):
    schema_path = _SCHEMA
    states_dir = root / "states"
    run_dir = root / "run"
    onboarding_dir = root / "onboarding"
    catalog_dir = root / "catalog"
    states_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    write_test_profile(run_dir)
    return schema_path, states_dir, run_dir, onboarding_dir, catalog_dir


def _give_existing_figure(
    schema_path: Path, states_dir: Path, run_dir: Path, catalog_dir: Path, onboarding_dir: Path,
    participant_id: str, char_id: str, name: str,
) -> dict:
    """Stattet `participant_id` mit einer bereits VOLLSTAENDIG aktiven Figur
    aus -- derselbe Produktweg wie eine echte abgeschlossene Erschaffung
    (Onboarding -> Katalogregistrierung -> eigene Figursavebytes -> Current-
    Publikation -> aktive Bindung), analog `test_n1_n7_...:_give_existing_
    figure` (hier ohne Persona-State-Profilfelder, die fuer diesen Guard-Test
    nicht relevant sind)."""
    save = full_v7_save(char_id, name=name, level=7, save_id=f"fixture-{char_id}")
    ps_store = PersonaStateStore(schema_path=schema_path)
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, participant_id, char_id, save)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
    ))
    catalog.store_figure_save(catalog_dir, participant_id, char_id, save)
    from mmo_sim.core import store as core_store
    core_store.publish_current_save(run_dir, participant_id, save, ps_store, states_dir)
    catalog.bind_for_section(catalog_dir, participant_id, char_id, has_open_section=False)
    return save


def _one_shot_input(line: str):
    """Liefert `line` GENAU EINMAL, danach EOF -- dieselbe Erwartung wie ein
    Mensch, der an genau diesem Prompt Enter drueckt und die Session dann
    (hier: Testende) verlaesst."""
    state = {"used": False}

    def _fn(prompt: str = "") -> str:
        if state["used"]:
            raise EOFError()
        state["used"] = True
        return line
    return _fn


def _poisoned_bind_attempt(*_a, **_kw):
    raise AssertionError(
        "onboarding.bind_attempt() DARF bei Leerwert/Whitespace NICHT aufgerufen "
        "werden -- genau das war der Bug (force_new faellt faelschlich durch)."
    )


def _poisoned_gm_transport_factory(*_a, **_kw):
    raise AssertionError(
        "gm_transport_factory DARF bei Leerwert/Whitespace NICHT aufgerufen werden "
        "-- kein Request/Transport ohne bewusste Auswahl/'neu'."
    )


def _poisoned_persona_driver_factory(*_a, **_kw):
    raise AssertionError("persona_driver_factory DARF bei Leerwert/Whitespace NICHT aufgerufen werden.")


# ===========================================================================
# B.1 -- Leerstring/Whitespace bei vorhandenen Figuren: kein force_new
# ===========================================================================

def _assert_empty_choice_guard(raw_choice: str, label: str) -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, "p1", "chrono-old", "Old")

        before_entries = {e.chrononaut_id for e in catalog.list_for_participant(catalog_dir, "p1")}
        before_active = catalog.active_chrononaut_id(catalog_dir, "p1")
        before_onboarding = onboarding.peek(onboarding_dir, "p1")
        assert before_onboarding is not None and before_onboarding.status == "completed"
        before_attempt_files = sorted(onboarding_dir.glob("attempt__*"))

        original_bind_attempt = onboarding.bind_attempt
        onboarding.bind_attempt = _poisoned_bind_attempt
        try:
            printed: list[str] = []
            session = TuiSession(
                onboarding_dir, catalog_dir, "p1",
                input_fn=_one_shot_input(raw_choice), print_fn=printed.append,
                run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
                gm_transport_factory=_poisoned_gm_transport_factory,
                persona_driver_factory=_poisoned_persona_driver_factory,
            )
            result = session._cmd_new_or_switch_character()
        finally:
            onboarding.bind_attempt = original_bind_attempt

        assert result in (None, False), f"[{label}] Rueckgabe muss falsy bleiben (kein '/zurueck'), war: {result!r}"

        # Kein neuer/zusaetzlicher Katalog-/Aktivwechsel-/Onboardingwrite.
        after_entries = {e.chrononaut_id for e in catalog.list_for_participant(catalog_dir, "p1")}
        assert after_entries == before_entries == {"chrono-old"}, (label, after_entries)
        assert catalog.active_chrononaut_id(catalog_dir, "p1") == before_active == "chrono-old", label
        after_onboarding = onboarding.peek(onboarding_dir, "p1")
        assert after_onboarding is not None and after_onboarding.status == "completed"
        assert after_onboarding.final_save == before_onboarding.final_save, (
            f"[{label}] die bestehende Erschaffungs-/Onboardingidentitaet von 'p1' darf unveraendert bleiben"
        )
        after_attempt_files = sorted(onboarding_dir.glob("attempt__*"))
        assert after_attempt_files == before_attempt_files == [], (
            f"[{label}] KEINE `bind_attempt`-Ledgerdatei (human-fresh-create::p1) darf entstehen"
        )

        # Nutzer wird erneut gefuehrt (Hinweistext statt stillem Fallback).
        assert any("Keine Eingabe erkannt" in p for p in printed), (label, printed)


def test_b1_empty_string_choice_at_existing_figures_no_force_new():
    _assert_empty_choice_guard("", "leerstring")


def test_b1_whitespace_only_choice_at_existing_figures_no_force_new():
    _assert_empty_choice_guard("   ", "whitespace")


def test_b1_tab_and_newline_whitespace_choice_at_existing_figures_no_force_new():
    _assert_empty_choice_guard("\t\t", "tab-whitespace")


# ===========================================================================
# B.2 -- Gegenfaelle bleiben unveraendert intakt
# ===========================================================================

def test_b2_existing_figure_by_number_still_switches_active_figure():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, "p1", "chrono-a", "A")
        _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, "p1", "chrono-b", "B")
        # Nach der zweiten `_give_existing_figure` ist 'chrono-b' aktiv --
        # Auswahl der Nummer 1 ('chrono-a', erste Katalogposition) muss real
        # zurueckwechseln.
        assert catalog.active_chrononaut_id(catalog_dir, "p1") == "chrono-b"

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir, catalog_dir, "p1",
            input_fn=_one_shot_input("1"), print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=_poisoned_gm_transport_factory,
        )
        session._cmd_new_or_switch_character()

        assert catalog.active_chrononaut_id(catalog_dir, "p1") == "chrono-a", (
            "Nummernauswahl einer bestehenden Figur muss weiterhin ueber "
            "_switch_active_figure den Aktivwechsel ausloesen"
        )


def test_b2_explicit_neu_still_reaches_force_new_host_gate():
    """'neu' (explizit) MUSS weiterhin force_new=True erreichen -- hier ohne
    konfigurierten `run_dir`/`gm_transport_factory`-Dialogaufbau, damit der
    tatsaechliche Host-Gate-Hinweistext (Zeile ~3771 ff.) als eindeutiger
    Beleg dient, dass der force_new-Pfad (NACH erfolgreichem `bind_attempt`)
    erreicht wurde -- waere der neue Guard zu weit gefasst, wuerde 'neu'
    bereits VORHER mit dem Leerwert-Hinweistext abgefangen."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, "p1", "chrono-old", "Old")

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir, catalog_dir, "p1",
            input_fn=_one_shot_input("neu"), print_fn=printed.append,
            run_dir=None, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=None,
        )
        session._cmd_new_or_switch_character()

        assert not any("Keine Eingabe erkannt" in p for p in printed), printed
        assert any("konfigurierte SL-Anbindung" in p for p in printed), (
            "'neu' muss weiterhin force_new=True + bind_attempt erreichen und am "
            "Host-Gate (fehlender run_dir/gm_transport_factory) sichtbar anstehen", printed,
        )
        # bind_attempt-Ledger wurde fuer den echten 'neu'-Pfad angelegt.
        assert any(onboarding_dir.glob("attempt__*")), "echtes 'neu' muss (anders als Leerwert) eine bind_attempt-Datei anlegen"


def test_b2_n_and_new_aliases_also_still_reach_force_new_host_gate():
    for alias in ("n", "new", "NEU"):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
            _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, "p1", "chrono-old", "Old")
            printed: list[str] = []
            session = TuiSession(
                onboarding_dir, catalog_dir, "p1",
                input_fn=_one_shot_input(alias), print_fn=printed.append,
                run_dir=None, states_dir=states_dir, schema_path=schema_path,
                gm_transport_factory=None,
            )
            session._cmd_new_or_switch_character()
            assert any("konfigurierte SL-Anbindung" in p for p in printed), (alias, printed)


def test_b2_zurueck_and_abbrechen_controls_unaffected_by_guard():
    import tempfile
    for control_token, expected_return in (("/zurueck", True), ("/abbrechen", False)):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
            _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, "p1", "chrono-old", "Old")
            printed: list[str] = []
            session = TuiSession(
                onboarding_dir, catalog_dir, "p1",
                input_fn=_one_shot_input(control_token), print_fn=printed.append,
                run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
                gm_transport_factory=_poisoned_gm_transport_factory,
            )
            result = session._cmd_new_or_switch_character()
            assert result is expected_return, (control_token, result)
            assert not any("Keine Eingabe erkannt" in p for p in printed), (control_token, printed)
            assert catalog.active_chrononaut_id(catalog_dir, "p1") == "chrono-old"


def test_b2_fortsetzen_prefix_still_reaches_resume_path():
    """'fortsetzen:<persona-id>' muss weiterhin den echten Resume-Pfad
    (`_resume_additional_persona_creation` -> `advance_additional_persona_
    creation`) erreichen. Setup: eine Persona hat eine Zusatzfigur-SL-
    Antwort bereits VOLLSTAENDIG erhalten (`completed`), aber die
    Katalogpersistenz ist (hier ueber eine real geworfene, einmalige
    `catalog.register`-Ausnahme, die unveraendert UNGEFANGEN bis zum
    Aufrufer durchreicht) noch offen -- derselbe reale Luecken-/
    Nachtragsfall, den `find_resumable_additional_creation`/'fortsetzen:'
    abdecken (Vorbild `test_e2e_b1b2_identity_and_menu_resume_2026_10_02.py:
    test_e2e_c_...`, dort per `Path.write_text`-Patch statt `catalog.
    register`)."""
    import tempfile
    from unittest.mock import patch

    from _full_v7_fixture import full_v7_block_text
    from mmo_sim.adapters.base import ParticipantDecision

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, "medic", "medic-old", "Medic")

        class _GM:
            def __init__(self, replies: list[str]):
                self.replies = list(replies)
                self.calls: list[str] = []

            def turn(self, idx, text, output_limit_tokens=None):
                self.calls.append(text)
                content = self.replies.pop(0)
                return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "x"}

        class _Driver:
            def __init__(self, answers: list[str]):
                self.answers = list(answers)

            def decide(self, ctx):
                assert not ctx.get("decision_contract"), "kein Einladungsvertrag in diesem Setup erwartet"
                return ParticipantDecision(text=self.answers.pop(0), origin_source="test", meta={"usage": {}})

        gm = _GM(["Wie soll dein Rufname lauten?", full_v7_block_text("medic-new-1", name="MedicFresh", level=1)])

        original_register = catalog.register
        fired = {"n": 0}

        def failing_register(*a, **kw):
            if fired["n"] == 0:
                fired["n"] += 1
                raise OSError("simulierter einmaliger Katalog-Registrierungsfehler (Resume-Setup)")
            return original_register(*a, **kw)

        setup_exc = None
        with patch.object(catalog, "register", failing_register):
            try:
                advance_additional_persona_creation(
                    run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
                    onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
                    community_id="community-medic", generation=2, persona_key="medic",
                    gm_transport_factory=lambda chat_id: gm,
                    persona_driver_factory=lambda pk: _Driver(["Bereit."]),
                )
            except OSError as e:
                setup_exc = e
        assert setup_exc is not None and fired["n"] == 1, "Testannahme: genau EIN realer Registrierungsfehler im Setup"

        resumable = find_resumable_additional_creation(onboarding_dir)
        assert resumable == [{"persona_key": "medic", "generation": 2}], resumable
        assert catalog.load_figure_save(catalog_dir, "medic", "medic-new-1") is None, "Testannahme: Save noch nicht nachgetragen"

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir, catalog_dir, "medic",
            input_fn=_one_shot_input("fortsetzen:medic"), print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=lambda chat_id: gm,
            persona_driver_factory=lambda pk: (_ for _ in ()).throw(AssertionError("kein neuer Persona-Request beim Nachtrag erwartet")),
        )
        session._cmd_new_or_switch_character()

        assert catalog.load_figure_save(catalog_dir, "medic", "medic-new-1") is not None, (
            "'fortsetzen:medic' muss den echten Resume-Pfad erreicht und den Save nachgetragen haben"
        )
        assert any("fortgesetzt" in p for p in printed), printed


# ===========================================================================
# B.3 -- Erstaufruf ohne vorhandene Figur (entries leer) bleibt unberuehrt
# ===========================================================================

def test_b3_first_call_without_existing_entries_unaffected_by_guard():
    """Der neue Guard liegt INNERHALB des `if entries:`-Zweigs -- ein
    Erstaufruf ganz ohne vorhandene Figur darf NICHT denselben Leerwert-
    Hinweistext zeigen und muss weiterhin regulaer bis zum Host-Gate
    (force_new bleibt False) durchfallen."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        assert catalog.list_for_participant(catalog_dir, "p1") == []

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir, catalog_dir, "p1",
            input_fn=_one_shot_input("irrelevant, da entries leer -- Prompt wird nicht gezeigt"),
            print_fn=printed.append,
            run_dir=None, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=None,
        )
        session._cmd_new_or_switch_character()

        assert not any("Keine Eingabe erkannt" in p for p in printed), printed
        assert any("konfigurierte SL-Anbindung" in p for p in printed), printed


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
