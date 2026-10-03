#!/usr/bin/env python3
"""
tests/mmo_sim/test_p2_community_creation.py — P2 Community-Erstgeneration
bis zur spielbereiten Persona (02_ABNAHME.md, P2-Community-Block
2026-09-25).

Deckt die Abnahme-Matrix (semantisch, s. 02_ABNAHME.md):
  - Einmalige neue Community: >5 geplante Personas, gepinnter Plan.
  - Eigene reguläre Erschaffung: ≥2 individuelle Persona↔SL-Dialoge,
    darunter eine echte mehrstufige Erschaffung, Antworten erreichen den
    jeweiligen echten Empfänger (dediziertes GM-Fake pro Persona-Chat-ID).
  - Fehler/Abbruch vor Save: Ablehnung/Budget-Stop/Transportfehler/
    ungültiger Save — andere Mitglieder bleiben unberührt, keine fingierte
    Spielfähigkeit.
  - Teilgeneration + Neustart: unterbrochene zweite Persona, frische
    PersonaStateStore/Aufruf übernimmt denselben gepinnten Plan, fertiger
    Save bleibt erhalten, keine doppelte Reservierung/kein doppelter
    Request für denselben offenen Schritt (request_ledger-Identität).
  - Endgültiger Reentry: kein erneuter Modellaufruf nach Fertigstellung.
  - Wirklicher Tischanschluss: fertige Persona nimmt über den bestehenden
    `_cmd_local_round`-Einladungsweg teil (Consent, Current kommt an);
    Ablehnung bleibt Ablehnung.
  - Lokale Menschen/andere Communities bleiben unverändert.

Nutzt AUSSCHLIESSLICH markierte Fake-Doubles an der äußersten Grenze (GM-/
Persona-Treiber-Fakes, analog `_GM` in `test_i1_i2_i3_worker_matrix.py`) —
der komplette Produktionsweg (`ui/tui.py:_cmd_community` →
`domain/zeitriss/community_creation.py` → `core/creation_service.py` →
`core/admission.py`/`core/request_ledger.py`/`core/store.py`) läuft echt.
Kein echter Modellcall. Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import request_ledger  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import read_admission_block, write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.community_bootstrap import bootstrap_community  # noqa: E402
from mmo_sim.domain.zeitriss.community_creation import (  # noqa: E402
    advance_community_creation,
    advance_one_persona_creation,
)
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


class _GM:
    """Ein eigenes GM-Fake PRO Persona-Chat-ID -- prüft, dass Antworten den
    jeweiligen echten Empfänger erreichen (keine Vermischung zwischen
    Personas)."""

    def __init__(self, scripted_replies: list[str]):
        self.scripted = list(scripted_replies)
        self.calls: list[str] = []

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append(text)
        content = self.scripted.pop(0) if self.scripted else "Die Erschaffung laeuft weiter."
        return {"content": content, "usage": {"prompt_tokens": 5, "completion_tokens": 5}, "sources": [], "latency_s": 0.0, "chat_id": "creation"}


class _FailingGM:
    def turn(self, idx, text, output_limit_tokens=None):
        raise RuntimeError("simulierter Transportfehler (Netzwerk)")


class _FakePersonaDriver:
    """`accept`/`reject` steuert, wie eine Einladungs-/Leaderentscheidung
    (`context['decision_contract']` gesetzt, s. `adapters/base.
    decision_contract_instruction`) beantwortet wird -- dieselbe strukturell
    validierbare Kontrollform wie ein echter Adapter (`interpret_decision_
    contract`), kein Freitext-Rateversuch. Normale Erschaffungs-Turns
    (kein `decision_contract`) nutzen die gescripteten `answers`."""

    def __init__(self, persona_key: str, answers: list[str], invite_decision: str = "accept"):
        self.persona_key = persona_key
        self.config = None
        self.answers = list(answers)
        self.invite_decision = invite_decision
        self.calls: list[dict] = []

    def decide(self, context: dict) -> ParticipantDecision:
        self.calls.append(context)
        contract = context.get("decision_contract")
        if contract:
            import json as _json
            text = _json.dumps({
                "offer_id": contract["offer_id"], "participant_id": contract["participant_id"],
                "decision": self.invite_decision,
            })
            return ParticipantDecision(text=text, origin_source="fake:community_creation", meta={"usage": {"prompt_tokens": 3, "completion_tokens": 3}})
        if not self.answers:
            raise RuntimeError(f"_FakePersonaDriver[{self.persona_key}]: keine weiteren Antworten gescriptet.")
        text = self.answers.pop(0)
        return ParticipantDecision(text=text, origin_source="fake:community_creation", meta={"usage": {"prompt_tokens": 3, "completion_tokens": 3}})


def _v7_block(char_id: str, name: str = "Nova", level: int = 1) -> str:
    return (
        "```json\n"
        f'{{"v": 7, "characters": [{{"char_id": "{char_id}", "name": "{name}", '
        f'"callsign": "{name.upper()}", "level": {level}}}]}}\n'
        "```"
    )


def _scripted_then_eof_input(*answers: str):
    """C4-Testanpassung (P2-Community-Ergebnisuebergabe 2026-09-25,
    01_AUFTRAG §3 C4, 02_ABNAHME 'TUI/Tests': 'Neue legitime Menueeingaben
    sind erlaubt'): `TuiSession._cmd_community()` stellt jetzt bei einer
    NEUEN, Live-konfigurierten Community GENAU EINE bewusste Demo-/Produktiv-
    Entscheidungsfrage (s. `mmo_sim/ui/tui.py:_cmd_community`) -- die bisher
    hier verwendete `input_fn`, die JEDE Eingabe sofort mit `EOFError`
    quittierte, ist damit kein reiner No-Interaction-Stub mehr. Liefert die
    uebergebenen `answers` der Reihe nach aus, danach `EOFError` wie zuvor
    (bewusst kein unbegrenzter Stub -- ein UNERWARTETER zusaetzlicher
    `_readline()`-Aufruf soll weiterhin sofort auffallen, nicht still eine
    leere Zeile liefern)."""
    queue = list(answers)

    def _input(prompt: str = "") -> str:
        if queue:
            return queue.pop(0)
        raise EOFError()

    return _input


def _new_env(root: Path):
    schema_path = _SCHEMA
    states_dir = root / "states"
    run_dir = root / "run"
    onboarding_dir = root / "onboarding"
    catalog_dir = root / "catalog"
    states_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    return schema_path, states_dir, run_dir, onboarding_dir, catalog_dir


def _bootstrap(root: Path, community_id: str, personas: dict[str, dict]):
    schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
    ps_store = PersonaStateStore(schema_path=schema_path)
    community_dir = run_dir / "community"
    result = bootstrap_community(community_dir, community_id, 1, personas, ps_store, states_dir, today="2026-09-25")
    return schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, result


def _draft_personas(keys: list[str]) -> dict[str, dict]:
    archetypes = ["Nahkampf", "Scharfschuetze", "Verhandler", "Technik", "Sanitaeter", "Aufklaerung"]
    return {
        pk: {
            "real_name": pk,
            "archetype": f"SIMULIERT: {archetypes[i % len(archetypes)]}",
            "play_style": "SIMULIERT: eigenstaendig",
            "charwunsch": "SIMULIERT/DEMO -- kein Erschaffungsdialog durchlaufen.",
            "plays_char": {
                "save_file": "NOCH_NICHT_ERSCHAFFEN", "character_id": "NOCH_NICHT_ERSCHAFFEN",
                "name": "NOCH_NICHT_ERSCHAFFEN", "callsign": "NOCH_NICHT_ERSCHAFFEN",
            },
        }
        for i, pk in enumerate(keys)
    }


# ── Einmalige neue Community: >5 geplante Personas, gepinnter Plan ─────────

def test_new_community_plans_more_than_five_distinct_personas():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = [f"persona{i}" for i in range(7)]
        _, _, _, _, _, result = _bootstrap(root, "community-x", _draft_personas(keys))
        assert not result.already_completed
        assert len(result.personas_written) == 7, "Community-Bootstrap muss >5 Personas planen koennen"
        assert set(result.personas_written) == set(keys)
        plan_path = root / "run" / "community" / "bootstrap__plan.json"
        assert plan_path.is_file(), "Plan muss dauerhaft gepinnt sein"


# ── Eigene reguläre Erschaffung: ≥2 individuelle Persona↔SL-Dialoge ────────

def test_two_personas_get_independent_multi_step_creation_dialogs_real_receiver():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["cqb", "sniper"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, result = _bootstrap(
            root, "community-y", _draft_personas(keys),
        )
        write_test_profile(run_dir)

        gm_scripts = {
            # cqb: ECHTE mehrstufige Erschaffung -- zwei SL-Fragen, Save erst
            # nach der zweiten Antwort.
            "cqb": ["Welche Waffengattung bevorzugst du?", "Wie soll dein Rufname lauten?", _v7_block("chrono-cqb", "Cee")],
            # sniper: einstufig (Save direkt nach der ersten Antwort).
            "sniper": ["Wie soll dein Rufname lauten?", _v7_block("chrono-sniper", "Ess")],
        }
        persona_answers = {
            "cqb": ["Nahkampf mit Kurzwaffen.", "Krag."],
            "sniper": ["Vesper."],
        }
        gm_instances: dict[str, _GM] = {}

        def gm_factory(chat_id: str):
            pk = chat_id.split("onboarding-", 1)[1]
            gm = _GM(gm_scripts[pk])
            gm_instances[pk] = gm
            return gm

        def persona_factory(pk: str):
            return _FakePersonaDriver(pk, persona_answers[pk])

        outcomes = advance_community_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-y", generation=1, planned_persona_keys=list(result.personas_written),
            gm_transport_factory=gm_factory, persona_driver_factory=persona_factory,
        )
        by_key = {o.persona_key: o for o in outcomes}
        assert by_key["cqb"].status == "completed" and by_key["cqb"].chrononaut_id == "chrono-cqb"
        assert by_key["sniper"].status == "completed" and by_key["sniper"].chrononaut_id == "chrono-sniper"
        # Echte mehrstufige Erschaffung: cqb bekam GENAU 3 SL-Turns (zwei
        # Fragen + Save-Turn, jede Antwort einzeln versendet), sniper GENAU 2
        # (eine Frage + Save-Turn) -- unterschiedliche Dialoglaengen pro
        # Persona, kein synchronisierter Gleichschritt.
        assert len(gm_instances["cqb"].calls) == 3, "cqb-Erschaffung muss echte mehrstufige Frage/Antwort sein"
        assert len(gm_instances["sniper"].calls) == 2

        # Antworten erreichen den jeweiligen echten Empfaenger, keine Vermischung:
        assert "Krag" not in gm_instances["sniper"].calls[-1]
        assert gm_instances["cqb"].calls[-1] == "Krag."

        # Spielbereit: Current-Save + Katalog + Persona-State fuer BEIDE veroeffentlicht.
        ps_store = PersonaStateStore(schema_path=schema_path)
        for pk, cid in (("cqb", "chrono-cqb"), ("sniper", "chrono-sniper")):
            current = core_store.load_current_save_or_raise(run_dir, pk, ps_store, states_dir=states_dir)
            assert current is not None and current["characters"][0]["char_id"] == cid
            entries = catalog.list_for_participant(catalog_dir, pk)
            assert any(e.chrononaut_id == cid for e in entries)
            assert catalog.active_chrononaut_id(catalog_dir, pk) == cid
            state = ps_store.load_state(pk, states_dir=states_dir)
            assert state["plays_char"]["character_id"] == cid, "Bootstrap-Entwurf muss durch echten Chrononauten ersetzt sein"
            assert state["rounds_played"] == 0, "Erschaffung ist keine gespielte Runde (kein kuenstlicher Zuwachs)"


# ── Fehler/Abbruch vor Save: andere Mitglieder bleiben unberuehrt ──────────

def test_persona_transport_failure_keeps_others_unaffected_no_fake_readiness():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["broken", "healthy"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, result = _bootstrap(
            root, "community-z", _draft_personas(keys),
        )
        write_test_profile(run_dir)

        def gm_factory(chat_id: str):
            pk = chat_id.split("onboarding-", 1)[1]
            if pk == "broken":
                return _FailingGM()
            return _GM([_v7_block("chrono-healthy", "Healthy")])

        def persona_factory(pk: str):
            return _FakePersonaDriver(pk, ["irrelevant"])

        outcomes = advance_community_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-z", generation=1, planned_persona_keys=list(result.personas_written),
            gm_transport_factory=gm_factory, persona_driver_factory=persona_factory,
        )
        by_key = {o.persona_key: o for o in outcomes}
        assert by_key["broken"].status == "error"
        assert by_key["healthy"].status == "completed"
        # broken bleibt OFFEN/fortsetzbar, KEINE fingierte Spielfaehigkeit:
        broken_state = onboarding.peek(onboarding_dir, "broken")
        assert broken_state.status == "in_progress"
        assert broken_state.final_save is None
        ps_store = PersonaStateStore(schema_path=schema_path)
        assert core_store.load_current_save_or_raise(run_dir, "broken", ps_store, states_dir=states_dir) is None
        # healthy bleibt UNBEEINFLUSST vollstaendig fertig:
        assert core_store.load_current_save_or_raise(run_dir, "healthy", ps_store, states_dir=states_dir) is not None


def test_persona_rejects_dialog_leaves_progress_open_others_unaffected():
    """Eine Persona, die im Erschaffungsdialog abweichend/verweigernd
    antwortet (kein Save), bleibt offen -- kein Zwang, keine Fake-Fertigstellung."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["reluctant"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, result = _bootstrap(
            root, "community-r", _draft_personas(keys),
        )
        write_test_profile(root / "run")

        def gm_factory(chat_id: str):
            return _GM(["Welche Ausruestung waehlst du?"] * 3)  # nie ein v7-Block -> nie fertig

        def persona_factory(pk: str):
            return _FakePersonaDriver(pk, ["Ich bin mir noch unsicher."])  # nur EINE Antwort gescriptet

        outcome = advance_one_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-r", generation=1, persona_key="reluctant",
            gm_transport_factory=gm_factory, persona_driver_factory=persona_factory,
        )
        # Zweite Runde hat keine gescriptete Antwort mehr -> Treiber wirft ->
        # Dialog bleibt kontrolliert offen (kein Absturz, keine Fake-Figur).
        assert outcome.status == "error"
        state = onboarding.peek(onboarding_dir, "reluctant")
        assert state.status == "in_progress"
        assert len(state.steps) == 1, "die EINE tatsaechlich gegebene Antwort bleibt persistiert"


def test_persona_pause_control_contract_halts_without_further_requests_progress_retained():
    """C4 (P2-Community-Ergebnisuebergabe 2026-09-25, MAIN-DATENWEGENTSCHEIDUNG.md
    §4, 11 §8 'koennen auch ablehnen, pausieren oder andere Ziele waehlen'):
    der echte Entscheider (Persona-Driver) signalisiert eine bewusste Pause
    NUR ueber die exakte strukturelle Kontrollzeile (`adapters.base.
    interpret_creation_pause_control`) -- kein Transportfehler, keine
    erschoepfte Fake-Antwortliste. Ergebnis: `status='paused'`, Fortschritt
    (die bereits empfangene SL-Frage) bleibt persistiert, KEIN weiterer
    Modellaufruf fuer diese Persona in diesem Versuch."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["pausing"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, result = _bootstrap(
            root, "community-pause", _draft_personas(keys),
        )
        write_test_profile(root / "run")

        def gm_factory(chat_id: str):
            return _GM(["Welche Ausruestung waehlst du?"])

        def persona_factory(pk: str):
            return _FakePersonaDriver(pk, ["STEUERUNG erschaffung_pause"])

        outcome = advance_one_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-pause", generation=1, persona_key="pausing",
            gm_transport_factory=gm_factory, persona_driver_factory=persona_factory,
        )
        assert outcome.status == "paused", outcome
        state = onboarding.peek(onboarding_dir, "pausing")
        assert state.status == "in_progress"
        assert state.pending_step is not None and state.pending_step.get("sl_reply") == "Welche Ausruestung waehlst du?", (
            "die bereits empfangene SL-Frage muss trotz Pause erhalten bleiben"
        )
        assert core_store.load_current_save_or_raise(run_dir, "pausing", PersonaStateStore(schema_path=schema_path), states_dir=states_dir) is None


def test_persona_mentioning_pause_word_in_normal_answer_is_not_treated_as_pause():
    """C4: eine gewoehnliche inhaltliche Antwort, die das Wort 'Pause'
    ERWAEHNT (aber NICHT die exakte Kontrollzeile ist), bleibt eine
    gewoehnliche Figurenantwort -- KEINE Keyword-/Negationswortliste, kein
    Fehldeuten als Steuerung (02_ABNAHME 'Eigener Kontext/Pause')."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["talkative"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, result = _bootstrap(
            root, "community-talk", _draft_personas(keys),
        )
        write_test_profile(root / "run")

        def gm_factory(chat_id: str):
            return _GM(["Welche Ausruestung waehlst du?", _v7_block("chrono-talkative", "talkative")])

        def persona_factory(pk: str):
            return _FakePersonaDriver(pk, ["Mein Chrononaut braucht eine kurze Gefechtspause, dann waehlt er einen Karabiner."])

        outcome = advance_one_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-talk", generation=1, persona_key="talkative",
            gm_transport_factory=gm_factory, persona_driver_factory=persona_factory,
        )
        assert outcome.status == "completed", outcome
        assert core_store.load_current_save_or_raise(
            run_dir, "talkative", PersonaStateStore(schema_path=schema_path), states_dir=states_dir,
        ) is not None


def test_persona_explicit_resume_after_pause_gets_new_decision_not_old_replay():
    """R4 (Community-Recovery 2026-09-25, REVIEW-COMMUNITY-RECOVERY.md §6):
    eine bereits durabel abgerechnete Pause-Kontrollzeile ist KEIN
    wiederverwendbarer Antworttext -- sonst bleibt eine Persona nach der
    ersten Pause fuer immer haengen, selbst bei einem ausdruecklich
    veranlassten zweiten `advance_one_persona_creation`-Aufruf. Die
    bereits empfangene GM-Frage wird dabei NICHT erneut angefragt (lokaler
    Checkpoint bleibt wirksam), aber die Persona erhaelt GENAU EINEN neuen
    Entscheidungsversuch -- kein Keywordveto, keine automatische Aufhebung
    der urspruenglichen Pause, keine Autonomieschleife (nur EIN neuer
    Versuch pro ausdruecklichem Aufruf)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["resuming"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, result = _bootstrap(
            root, "community-resume", _draft_personas(keys),
        )
        write_test_profile(root / "run", max_turns=100)

        gm = _GM(["Welche Ausruestung waehlst du?", _v7_block("chrono-resuming", "resuming")])

        def gm_factory(chat_id: str):
            return gm

        first_driver = _FakePersonaDriver("resuming", ["STEUERUNG erschaffung_pause"])
        outcome1 = advance_one_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-resume", generation=1, persona_key="resuming",
            gm_transport_factory=gm_factory, persona_driver_factory=lambda pk: first_driver,
        )
        assert outcome1.status == "paused", outcome1
        assert len(gm.calls) == 1, "GM-Frage darf beim ersten Versuch genau einmal gestellt werden"

        second_driver = _FakePersonaDriver("resuming", ["Ich waehle leichte Ruestung."])
        outcome2 = advance_one_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-resume", generation=1, persona_key="resuming",
            gm_transport_factory=gm_factory, persona_driver_factory=lambda pk: second_driver,
        )
        assert outcome2.status == "completed", (
            f"eine ausdruecklich veranlasste Fortsetzung muss eine NEUE Personaentscheidung "
            f"erhalten, keine ewige Wiederholung der alten Pause: {outcome2}"
        )
        assert len(second_driver.calls) == 1, "genau EIN neuer Entscheidungsversuch, keine Autonomieschleife"
        assert len(gm.calls) == 2, (
            "die bereits empfangene GM-Frage darf beim Resume NICHT erneut angefragt werden -- "
            "nur der abschliessende Save-Turn ist ein echter neuer GM-Call"
        )
        assert core_store.load_current_save_or_raise(
            run_dir, "resuming", PersonaStateStore(schema_path=schema_path), states_dir=states_dir,
        ) is not None


def test_budget_stop_blocks_remaining_personas_without_further_requests():
    """02_ABNAHME 'Fehler/Abbruch vor Save': Budget-Stop haelt NUR die noch
    offenen Personas an, bereits fertige bleiben unberuehrt."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["first", "second"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, result = _bootstrap(
            root, "community-b", _draft_personas(keys),
        )
        # Exakt genug Budget fuer die 3 Requests (2x GM + 1x Persona) der
        # ersten Persona (einstufige Erschaffung), keinen Request mehr danach.
        write_test_profile(run_dir, max_turns=3)

        def gm_factory(chat_id: str):
            pk = chat_id.split("onboarding-", 1)[1]
            return _GM(["Frage?", _v7_block(f"chrono-{pk}", pk)])

        def persona_factory(pk: str):
            return _FakePersonaDriver(pk, ["Antwort."])

        outcomes = advance_community_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-b", generation=1, planned_persona_keys=["first", "second"],
            gm_transport_factory=gm_factory, persona_driver_factory=persona_factory,
        )
        by_key = {o.persona_key: o for o in outcomes}
        assert by_key["first"].status == "completed"
        assert by_key["second"].status == "blocked"
        second_state = onboarding.peek(onboarding_dir, "second")
        assert second_state is None or second_state.status != "completed"


def test_invalid_save_block_rejected_no_fingierte_spielfaehigkeit():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["baddata"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, result = _bootstrap(
            root, "community-bad", _draft_personas(keys),
        )
        write_test_profile(run_dir)

        def gm_factory(chat_id: str):
            # Ein "Save", der keine gueltige char_id traegt (z.B. fehlendes
            # 'characters'-Array-Element) -> `block_char_id` liefert None,
            # Dialog bleibt offen statt Dummy-Uebernahme.
            return _GM(["```json\n{\"v\": 7, \"characters\": []}\n```", "Frage 2?"])

        def persona_factory(pk: str):
            return _FakePersonaDriver(pk, ["Antwort."] * 3)

        outcome = advance_one_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-bad", generation=1, persona_key="baddata",
            gm_transport_factory=gm_factory, persona_driver_factory=persona_factory,
        )
        assert outcome.status != "completed"
        assert onboarding.peek(onboarding_dir, "baddata").status == "in_progress"


# ── Teilgeneration + Neustart: gepinnter Plan/Journal, kein Duplikat ───────

def test_partial_generation_then_restart_resumes_same_journal_no_duplicate_requests():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["done_one", "resumed_two"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, result = _bootstrap(
            root, "community-restart", _draft_personas(keys),
        )
        write_test_profile(run_dir)

        gm_calls_round1 = []

        def gm_factory_round1(chat_id: str):
            pk = chat_id.split("onboarding-", 1)[1]
            if pk == "done_one":
                gm = _GM([_v7_block("chrono-done", "Done")])
            else:
                gm = _GM(["Erste Frage an resumed_two?"])  # kein Save -> bleibt offen
            gm_calls_round1.append((pk, gm))
            return gm

        def persona_factory_round1(pk: str):
            return _FakePersonaDriver(pk, ["Antwort Runde 1."])

        outcomes1 = advance_community_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-restart", generation=1, planned_persona_keys=["done_one", "resumed_two"],
            gm_transport_factory=gm_factory_round1, persona_driver_factory=persona_factory_round1,
        )
        by_key1 = {o.persona_key: o for o in outcomes1}
        assert by_key1["done_one"].status == "completed"
        # resumed_two: GM stellte eine Frage, Persona antwortete -> Dialog
        # laeuft (kein Save-Treffer bisher) -> naechste GM-Antwortliste ist
        # leer -> "Die Erschaffung laeuft weiter." OHNE Save -> get_reply
        # erneut aufgerufen -> Treiber hat keine zweite Antwort -> "error"
        # (bewusst offen gehalten fuer den Restart-Beleg unten).
        resumed_before = onboarding.peek(onboarding_dir, "resumed_two")
        assert resumed_before.status == "in_progress"
        steps_before = len(resumed_before.steps)
        assert steps_before >= 1

        # "Echter Neustart": frische PersonaStateStore-Instanz + frischer
        # Aufruf (derselbe gepinnte Plan/Onboarding-Journal von Platte).
        def gm_factory_round2(chat_id: str):
            pk = chat_id.split("onboarding-", 1)[1]
            assert pk == "resumed_two", "done_one ist bereits fertig -- KEIN zweiter Modellaufruf noetig"
            return _GM([_v7_block("chrono-resumed", "Resumed")])

        def persona_factory_round2(pk: str):
            return _FakePersonaDriver(pk, ["Antwort Runde 2."])

        outcomes2 = advance_community_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-restart", generation=1, planned_persona_keys=["done_one", "resumed_two"],
            gm_transport_factory=gm_factory_round2, persona_driver_factory=persona_factory_round2,
        )
        by_key2 = {o.persona_key: o for o in outcomes2}
        # done_one: bereits `completed` -> sofortiger No-op, KEIN Modellaufruf.
        assert by_key2["done_one"].status == "already_ready"
        assert by_key2["resumed_two"].status == "completed"
        assert by_key2["resumed_two"].chrononaut_id == "chrono-resumed"

        # Fortschritt aus Runde 1 blieb erhalten (kein Duplikat, kein Reset):
        resumed_after = onboarding.peek(onboarding_dir, "resumed_two")
        assert resumed_after.steps[0] == resumed_before.steps[0]

        # Kein doppelter Request fuer denselben (bereits abgeschlossenen)
        # logischen Schritt: `done_one`s GM-Turn 0 (role=community_creation_gm,
        # participant=done_one, turn_idx=0) existiert genau EINMAL im Ledger.
        gm_turn0_records = [
            r for r in request_ledger.open_requests(run_dir) + _all_accounted(run_dir)
            if r.get("participant") == "done_one" and r.get("role") == "community_creation_gm" and r.get("turn_idx") == 0
        ]
        assert len(gm_turn0_records) == 1, "keine zweite Reservierung/kein zweiter Request fuer denselben abgeschlossenen Schritt"


def _all_accounted(run_dir: Path) -> list[dict]:
    import json
    d = run_dir / "requests"
    if not d.is_dir():
        return []
    return [json.loads(p.read_text(encoding="utf-8")) for p in d.glob("*.json")]


# ── Endgueltiger Reentry: kein erneuter Modellaufruf nach Fertigstellung ───

def test_final_reentry_after_full_completion_makes_zero_new_requests():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["ready_one"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, result = _bootstrap(
            root, "community-reentry", _draft_personas(keys),
        )
        write_test_profile(run_dir)

        call_counter = {"n": 0}

        def gm_factory(chat_id: str):
            call_counter["n"] += 1
            return _GM([_v7_block("chrono-ready", "Ready")])

        def persona_factory(pk: str):
            return _FakePersonaDriver(pk, ["Antwort."])

        outcome1 = advance_one_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-reentry", generation=1, persona_key="ready_one",
            gm_transport_factory=gm_factory, persona_driver_factory=persona_factory,
        )
        assert outcome1.status == "completed"
        assert call_counter["n"] == 1

        def gm_factory_should_not_be_called(chat_id: str):
            raise AssertionError("Reentry nach fertiger Generation darf keinen neuen SL-Dialog starten")

        outcome2 = advance_one_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-reentry", generation=1, persona_key="ready_one",
            gm_transport_factory=gm_factory_should_not_be_called, persona_driver_factory=persona_factory,
        )
        assert outcome2.status == "already_ready"
        assert call_counter["n"] == 1, "kein zusaetzlicher Modellaufruf bei Reentry"


# ── Wirklicher Tischanschluss: bestehender Einladungsweg, Consent, Ablehnung bleibt Ablehnung ──

def test_ready_persona_joins_existing_local_round_via_invitation_path_with_consent():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["joiner"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, result = _bootstrap(
            root, "community-join", _draft_personas(keys),
        )
        write_test_profile(run_dir)

        def gm_factory(chat_id: str):
            return _GM([_v7_block("chrono-joiner", "Joiner")])

        def persona_factory(pk: str):
            return _FakePersonaDriver(pk, ["Ich bin bereit."])

        outcome = advance_one_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-join", generation=1, persona_key="joiner",
            gm_transport_factory=gm_factory, persona_driver_factory=persona_factory,
        )
        assert outcome.status == "completed"

        # Leader (Mensch) laedt die fertige Persona ueber den BESTEHENDEN
        # `_cmd_local_round`-Weg ein -- kein neues JSON-Einfuegen, kein neuer
        # Code fuer den Tischanschluss.
        leader_id = "leader_human"
        leader_onboard = onboarding.start_or_resume(onboarding_dir, leader_id)
        leader_save = {"v": 7, "characters": [{"char_id": "chrono-leader", "name": "Leader", "callsign": "LEAD", "level": 1}]}
        from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator
        onboarding.complete_with_save(onboarding_dir, leader_id, leader_save, ZeitrissHarvestValidator(), "chrono-leader")
        catalog.register(catalog_dir, catalog.CatalogEntry(participant_id=leader_id, chrononaut_id="chrono-leader", persona_key=leader_id))
        catalog.store_figure_save(catalog_dir, leader_id, "chrono-leader", leader_save)
        ps_store = PersonaStateStore(schema_path=schema_path)
        onboarding.ensure_participant_persona_state(ps_store, states_dir, leader_id, "chrono-leader", leader_save)
        core_store.publish_current_save(run_dir, leader_id, leader_save, ps_store, states_dir)
        catalog.bind_for_section(catalog_dir, leader_id, "chrono-leader", has_open_section=False)

        table_gm_calls = []

        class _TableGM:
            def turn(self, idx, text, output_limit_tokens=None):
                table_gm_calls.append(text)
                from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER
                return {"content": "Die Runde beginnt.", "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "table"}

        from mmo_sim.ui.tui import EndOfInput

        session = TuiSession(
            onboarding_dir, catalog_dir, leader_id,
            input_fn=lambda prompt="": (_ for _ in ()).throw(EOFError()),
            print_fn=lambda s: None,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=lambda *_a, **_kw: _TableGM(),
            persona_driver_factory=lambda pk: _FakePersonaDriver(pk, ["Ja, ich nehme an."]),
        )
        try:
            session._cmd_local_round(["persona:joiner"])
        except EndOfInput:
            # Consent + Tischanlage sind bereits VOR dem ersten Spielzug
            # abgeschlossen (Table.persist in `create_table_from_offer_log`)
            # -- der eigentliche Spielzug des menschlichen Leaders (nicht
            # Gegenstand dieses Tests) bricht hier erwartungsgemaess per EOF
            # kontrolliert ab, genau wie am echten Terminal (A11/A16).
            pass

        # Consent-Log belegt Angebot + Zusage VOR Tischanlage.
        log_path = run_dir / "invitation_decisions.jsonl"
        assert log_path.is_file()
        import json as _json
        records = [_json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
        offer = [r for r in records if r["type"] == "offer"]
        response = [r for r in records if r["type"] == "response" and r["from"] == "joiner"]
        assert offer and response
        assert response[0]["decision"] == "accept"

        # Der Tisch ist tatsaechlich mit dem Current-Save der Persona entstanden.
        table = core_store.Table.load(run_dir, f"local-{leader_id}-joiner")
        assert "joiner" in table.members
        assert table.chrononaut_id_to_persona()["chrono-joiner"] == "joiner"


def test_ready_persona_rejects_invitation_stays_rejected_no_table():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["shy"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, result = _bootstrap(
            root, "community-shy", _draft_personas(keys),
        )
        write_test_profile(run_dir)

        outcome = advance_one_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-shy", generation=1, persona_key="shy",
            gm_transport_factory=lambda chat_id: _GM([_v7_block("chrono-shy", "Shy")]),
            persona_driver_factory=lambda pk: _FakePersonaDriver(pk, ["Bereit."]),
        )
        assert outcome.status == "completed"

        leader_id = "leader_human_two"
        leader_save = {"v": 7, "characters": [{"char_id": "chrono-leader2", "name": "Leader2", "callsign": "L2", "level": 1}]}
        from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator
        onboarding.start_or_resume(onboarding_dir, leader_id)
        onboarding.complete_with_save(onboarding_dir, leader_id, leader_save, ZeitrissHarvestValidator(), "chrono-leader2")
        catalog.register(catalog_dir, catalog.CatalogEntry(participant_id=leader_id, chrononaut_id="chrono-leader2", persona_key=leader_id))
        catalog.store_figure_save(catalog_dir, leader_id, "chrono-leader2", leader_save)
        ps_store = PersonaStateStore(schema_path=schema_path)
        onboarding.ensure_participant_persona_state(ps_store, states_dir, leader_id, "chrono-leader2", leader_save)
        core_store.publish_current_save(run_dir, leader_id, leader_save, ps_store, states_dir)
        catalog.bind_for_section(catalog_dir, leader_id, "chrono-leader2", has_open_section=False)

        session = TuiSession(
            onboarding_dir, catalog_dir, leader_id,
            input_fn=lambda prompt="": (_ for _ in ()).throw(EOFError()),
            print_fn=lambda s: None,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=lambda *_a, **_kw: _GM(["sollte nie erreicht werden"]),
            persona_driver_factory=lambda pk: _FakePersonaDriver(pk, [], invite_decision="reject"),
        )
        session._cmd_local_round(["persona:shy"])
        assert not (run_dir / "tables" / f"local-{leader_id}-shy.json").exists(), (
            "abgelehnte Persona darf keinen Tisch entstehen lassen"
        )


# ── Lokale Menschen/andere Communities bleiben unveraendert ────────────────

def test_unrelated_human_and_other_community_untouched():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, _r1 = _bootstrap(
            root, "community-main", _draft_personas(["alpha"]),
        )
        write_test_profile(run_dir)

        # Ein Mensch mit eigener Figur, unabhaengig von der Community.
        human_save = {"v": 7, "characters": [{"char_id": "chrono-human", "name": "Mensch", "callsign": "M", "level": 3}]}
        from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator
        onboarding.start_or_resume(onboarding_dir, "human_x")
        onboarding.complete_with_save(onboarding_dir, "human_x", human_save, ZeitrissHarvestValidator(), "chrono-human")
        catalog.register(catalog_dir, catalog.CatalogEntry(participant_id="human_x", chrononaut_id="chrono-human", persona_key="human_x"))
        catalog.store_figure_save(catalog_dir, "human_x", "chrono-human", human_save)
        ps_store = PersonaStateStore(schema_path=schema_path)
        onboarding.ensure_participant_persona_state(ps_store, states_dir, "human_x", "chrono-human", human_save)
        core_store.publish_current_save(run_dir, "human_x", human_save, ps_store, states_dir)
        before_human_current = core_store.load_current_save_or_raise(run_dir, "human_x", ps_store, states_dir=states_dir)

        # Eine ZWEITE, unabhaengige Community im selben run_dir.
        community_dir_2 = run_dir / "community2"
        result2 = bootstrap_community(community_dir_2, "community-other", 1, _draft_personas(["beta"]), ps_store, states_dir, today="2026-09-25")

        advance_one_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-main", generation=1, persona_key="alpha",
            gm_transport_factory=lambda chat_id: _GM([_v7_block("chrono-alpha", "Alpha")]),
            persona_driver_factory=lambda pk: _FakePersonaDriver(pk, ["Bereit."]),
        )

        # Mensch unveraendert:
        after_human_current = core_store.load_current_save_or_raise(run_dir, "human_x", ps_store, states_dir=states_dir)
        assert after_human_current == before_human_current

        # Andere Community (beta) unveraendert -- kein Cross-Talk:
        beta_state = onboarding.peek(onboarding_dir, "beta")
        assert beta_state is None, "unbeteiligte Persona einer anderen Community darf nicht angefasst werden"
        assert core_store.load_current_save_or_raise(run_dir, "beta", ps_store, states_dir=states_dir) is None


# ── UI-/Factory-Verbindung: der reale `c`-Weg (TuiSession._cmd_community) ──

def test_cmd_community_end_to_end_via_real_tui_c_command():
    """Beweist die tatsaechliche Verdrahtung (nicht nur die Domaenenfunktion
    isoliert): `TuiSession._cmd_community()` (derselbe Code, den `run()`
    fuer die reale Auswahl `c` aufruft) fuehrt Bootstrap UND Persona-
    Erschaffung in EINEM Aufruf durch, wenn gm_transport_factory/
    persona_driver_factory konfiguriert sind."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        write_test_profile(run_dir)
        printed: list[str] = []

        def gm_factory(chat_id: str):
            pk = chat_id.split("onboarding-", 1)[1]
            return _GM([_v7_block(f"chrono-{pk}", pk)])

        def persona_factory(pk: str):
            return _FakePersonaDriver(pk, ["Bereit."])

        session = TuiSession(
            onboarding_dir, catalog_dir, "human_caller",
            # C4-Testanpassung (s. `_scripted_then_eof_input` Docstring):
            # 'd' beantwortet die NEUE, bewusste Demo-/Produktiv-Entscheidung
            # (SIMULIERT/DEMO-Uebernahme) -- unveraendert die bisherige
            # Default-Erwartung dieses Tests (8 SIMULIERT/DEMO-Profile).
            input_fn=_scripted_then_eof_input("d"),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=gm_factory, persona_driver_factory=persona_factory,
        )
        session._cmd_community()

        community_id = "community-human_caller"
        plan = (run_dir / "community" / "bootstrap__plan.json")
        assert plan.is_file()
        import json as _json
        planned_keys = list(_json.loads(plan.read_text(encoding="utf-8"))["personas"].keys())
        assert len(planned_keys) == 8, "Default-Startpopulation bleibt 8 (konfigurierbarer technischer Default)"

        ps_store = PersonaStateStore(schema_path=schema_path)
        ready = [pk for pk in planned_keys if core_store.load_current_save_or_raise(run_dir, pk, ps_store, states_dir=states_dir) is not None]
        assert len(ready) == 8, f"ALLE geplanten Personas sollten ueber den realen 'c'-Weg spielbereit werden, war: {ready}"
        assert any("Persona-getriebene Erstgeneration" in line for line in printed)

        # Der aufrufende MENSCH bekommt hier KEINE eigene Stamm-Persona (02 §2).
        assert onboarding.peek(onboarding_dir, "human_caller") is None
        assert core_store.load_current_save_or_raise(run_dir, "human_caller", ps_store, states_dir=states_dir) is None


def test_cmd_community_production_choice_creates_distinct_non_demo_pool():
    """C4 (P2-Community-Ergebnisuebergabe 2026-09-25, 01_AUFTRAG §3 C4,
    02_ABNAHME 'Demo/Produkt'): bei einer NEUEN, Live-konfigurierten
    Community und explizit gewaehltem 'p' entsteht eine GETRENNTE
    produktive Startpopulation -- weder Namen noch `_fixture_note`
    ueberschneiden sich mit `_synthetic_starter_pool`, keine SIMULIERT/
    DEMO-Kennzeichnung. Kein Loeschen/Umetikettieren vorhandener Daten (hier:
    keine gibt es, frische Community)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        write_test_profile(run_dir)
        printed: list[str] = []

        def gm_factory(chat_id: str):
            pk = chat_id.split("onboarding-", 1)[1]
            return _GM([_v7_block(f"chrono-{pk}", pk)])

        def persona_factory(pk: str):
            return _FakePersonaDriver(pk, ["Bereit."])

        session = TuiSession(
            onboarding_dir, catalog_dir, "human_caller_prod",
            input_fn=_scripted_then_eof_input("p"),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=gm_factory, persona_driver_factory=persona_factory,
        )
        session._cmd_community()

        plan = run_dir / "community" / "bootstrap__plan.json"
        import json as _json
        personas = _json.loads(plan.read_text(encoding="utf-8"))["personas"]
        assert len(personas) == 8
        demo_pool_keys = set(session._synthetic_starter_pool("community-human_caller_prod", size=8).keys())
        assert not (set(personas.keys()) & demo_pool_keys), (
            "produktive Neuanlage darf keine Persona-Keys mit dem SIMULIERT/DEMO-Pool teilen"
        )
        for payload in personas.values():
            assert "SIMULIERT" not in payload.get("_fixture_note", ""), (
                "produktive Neuanlage darf nicht als SIMULIERT/DEMO gekennzeichnet sein"
            )
            assert "PRODUKTIV" in payload.get("_fixture_note", "")
        assert any("PRODUKTIVE Neuanlage bewusst gewaehlt" in line for line in printed)
        ps_store = PersonaStateStore(schema_path=schema_path)
        ready = [pk for pk in personas if core_store.load_current_save_or_raise(run_dir, pk, ps_store, states_dir=states_dir) is not None]
        assert len(ready) == 8, f"produktive Startpopulation muss regulaer erschaffbar sein, war: {ready}"


def test_cmd_community_without_model_config_stays_honest_partial_state_like_baseline():
    """Test vs. Produkt (02_ABNAHME): Default `c` OHNE Modellfreigabe macht
    KEINE echte Anfrage und gibt KEINE Dummyfigur als echt aus -- identisch
    zur Bestandsbeobachtung (`observe_community_entry.py`: 8 Entwuerfe, 0
    Current-Saves)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        # KEIN write_test_profile() -- keine lab.status.json, Admission-Gate
        # blockiert fail-closed (wie am echten Terminal ohne Live-Setup).
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir, catalog_dir, "human_caller2",
            # C4-Testanpassung (s. `_scripted_then_eof_input` Docstring): die
            # neue Demo-/Produktiv-Entscheidungsfrage haengt NUR an
            # konfigurierten Factories (hier gesetzt, um zu pruefen, dass sie
            # NICHT aufgerufen werden) -- 'd' beantwortet sie, ohne dass ein
            # Modellaufruf stattfindet (der faellt separat am Admission-Gate).
            input_fn=_scripted_then_eof_input("d"),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=lambda *_a, **_kw: (_ for _ in ()).throw(AssertionError("kein Modellaufruf ohne Freigabe erwartet")),
            persona_driver_factory=lambda pk: (_ for _ in ()).throw(AssertionError("kein Modellaufruf ohne Freigabe erwartet")),
        )
        session._cmd_community()
        ps_store = PersonaStateStore(schema_path=schema_path)
        ready = [
            pk for pk in _json_persona_keys(run_dir)
            if core_store.load_current_save_or_raise(run_dir, pk, ps_store, states_dir=states_dir) is not None
        ]
        assert ready == [], "ohne Admission-Freigabe darf keine Persona als spielbereit gemeldet werden"
        assert any("blocked" in line for line in printed)


def _json_persona_keys(run_dir: Path) -> list[str]:
    import json as _json
    plan = run_dir / "community" / "bootstrap__plan.json"
    if not plan.is_file():
        return []
    return list(_json.loads(plan.read_text(encoding="utf-8"))["personas"].keys())


# ── C4: begrenzter Fortschrittsschritt (`limit`/`MMO_SIM_COMMUNITY_STEP_LIMIT`) ──
# Testabdeckungslücke, End-Critic-Befund 2026-09-25 (i4ck-Review): die
# `limit`-Kapazität selbst war bereits funktional korrekt implementiert,
# aber ohne dauerhaften Regressionstest im Repo.

def test_advance_community_creation_limit_defers_excess_frees_already_completed():
    """C4: `limit` begrenzt NUR tatsaechlich noch offene Personas -- eine
    bereits `completed` Persona bleibt IMMER kostenfrei (`already_ready`,
    kein Modellaufruf, verbraucht das Limit nicht), genau EINE der beiden
    noch offenen Personas wird bis zum Abschluss getrieben, die dritte
    bleibt `deferred` (offen, requestfrei). Ein Folgeaufruf OHNE Limit
    vervollstaendigt exakt die deferred gebliebene Persona, ohne die
    bereits fertigen erneut anzufassen."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["already_done", "gets_driven", "stays_deferred"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, result = _bootstrap(
            root, "community-limit", _draft_personas(keys),
        )
        write_test_profile(run_dir)

        # Runde 0 (kein Limit): nur "already_done" fertigstellen.
        outcome0 = advance_one_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-limit", generation=1, persona_key="already_done",
            gm_transport_factory=lambda: _GM([_v7_block("chrono-already", "Already")]),
            persona_driver_factory=lambda pk: _FakePersonaDriver(pk, ["Antwort."]),
        )
        assert outcome0.status == "completed"

        def gm_factory_limited(chat_id: str):
            pk = chat_id.split("onboarding-", 1)[1]
            assert pk != "already_done", "bereits fertige Persona darf keinen neuen GM-Request ausloesen"
            assert pk != "stays_deferred", "deferred Persona darf in dieser Runde keinen GM-Request bekommen"
            return _GM([_v7_block(f"chrono-{pk}", pk)])

        def persona_factory_limited(pk: str):
            assert pk != "already_done"
            assert pk != "stays_deferred"
            return _FakePersonaDriver(pk, ["Antwort."])

        outcomes1 = advance_community_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-limit", generation=1, planned_persona_keys=keys,
            gm_transport_factory=gm_factory_limited, persona_driver_factory=persona_factory_limited,
            limit=1,
        )
        by_key1 = {o.persona_key: o for o in outcomes1}
        assert by_key1["already_done"].status == "already_ready"
        assert by_key1["gets_driven"].status == "completed"
        assert by_key1["stays_deferred"].status == "deferred"
        assert by_key1["stays_deferred"].chrononaut_id is None

        # Folgeaufruf OHNE Limit: vervollstaendigt exakt die deferred
        # gebliebene Persona, ruehrt die beiden bereits fertigen nicht an.
        def gm_factory_followup(chat_id: str):
            pk = chat_id.split("onboarding-", 1)[1]
            assert pk == "stays_deferred", f"nur die deferred Persona sollte hier angefragt werden, war: {pk}"
            return _GM([_v7_block("chrono-stays-deferred", "StaysDeferred")])

        outcomes2 = advance_community_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-limit", generation=1, planned_persona_keys=keys,
            gm_transport_factory=gm_factory_followup,
            persona_driver_factory=lambda pk: _FakePersonaDriver(pk, ["Antwort."]),
        )
        by_key2 = {o.persona_key: o for o in outcomes2}
        assert by_key2["already_done"].status == "already_ready"
        assert by_key2["gets_driven"].status == "already_ready"
        assert by_key2["stays_deferred"].status == "completed"


def test_cmd_community_step_limit_env_var_wired_through_real_tui():
    """C4: `MMO_SIM_COMMUNITY_STEP_LIMIT` (Betreiber-/Startkonfiguration,
    `TuiSession._community_step_limit`) wird tatsaechlich bis zu
    `advance_community_creation(limit=...)` durchgereicht -- geprueft ueber
    den echten `_cmd_community()`-Aufruf, nicht nur die Parserfunktion
    isoliert.

    Semantische Korrektur (P2-Community-Ergebnisuebergabe 2026-09-25,
    MAIN-DATENWEGENTSCHEIDUNG.md §4, REVIEW-COMMUNITY-ERGEBNISUEBERGABE.md §3,
    End-Critic-Befund i4ck-Review): die alte Annahme 'ungueltige/nicht-
    positive Werte fallen sicher auf unbegrenztes Verhalten zurueck' war
    genau das verbotene Verhalten -- ein EXPLIZIT gesetzter ungueltiger Wert
    ('abc') darf NICHT ununterscheidbar vom bewusst unkonfigurierten Default
    (unbegrenzt) sein. `_community_step_limit()` liefert dafuer jetzt eine
    kontrollierte Ablehnung (s. `mmo_sim/ui/tui.py`); `_cmd_community()`
    bricht die Erschaffungs-Fortsetzung fuer DIESEN Aufruf dann sichtbar ab,
    OHNE weitere Personas voranzutreiben (kein Vollpool-Fallback). Original
    dieser Testfunktion (vor dieser Korrektur) liegt unter
    `worker/original-tests/test_p2_community_creation.py.original` (Diff
    ueber `git diff`/Reportbeilage)."""
    import os as _os

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        write_test_profile(run_dir)
        printed: list[str] = []

        def gm_factory(chat_id: str):
            pk = chat_id.split("onboarding-", 1)[1]
            return _GM([_v7_block(f"chrono-{pk}", pk)])

        def persona_factory(pk: str):
            return _FakePersonaDriver(pk, ["Bereit."])

        session = TuiSession(
            onboarding_dir, catalog_dir, "human_caller3",
            # C4-Testanpassung (s. `_scripted_then_eof_input` Docstring):
            # genau EINE Antwort fuer die neue Demo-/Produktiv-Entscheidung
            # beim ERSTEN (frischen) `_cmd_community()`-Aufruf unten; beide
            # nachfolgenden Aufrufe fuer DIESELBE Community fragen NICHT
            # erneut (Fortsetzen, kein Doppelfragen).
            input_fn=_scripted_then_eof_input("d"),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=gm_factory, persona_driver_factory=persona_factory,
        )
        prior = _os.environ.get("MMO_SIM_COMMUNITY_STEP_LIMIT")
        try:
            _os.environ["MMO_SIM_COMMUNITY_STEP_LIMIT"] = "2"
            session._cmd_community()
        finally:
            if prior is None:
                _os.environ.pop("MMO_SIM_COMMUNITY_STEP_LIMIT", None)
            else:
                _os.environ["MMO_SIM_COMMUNITY_STEP_LIMIT"] = prior

        planned_keys = _json_persona_keys(run_dir)
        assert len(planned_keys) == 8
        ps_store = PersonaStateStore(schema_path=schema_path)
        ready = [
            pk for pk in planned_keys
            if core_store.load_current_save_or_raise(run_dir, pk, ps_store, states_dir=states_dir) is not None
        ]
        assert len(ready) == 2, f"limit=2 haette genau zwei Personas spielbereit machen duerfen, war: {ready}"
        assert any("Noch offen/wartend" in line and "deferred" not in line for line in printed)

        # C4-Korrektur: ein ungueltiger EXPLIZITER Wert ("abc") wird jetzt
        # kontrolliert ABGELEHNT -- KEIN stiller Vollpool-Fallback mehr. Der
        # bereits erreichte Zwischenstand (2 fertig) bleibt unangetastet,
        # requestfrei (kein einziger neuer GM-/Persona-Call fuer diesen
        # Aufruf).
        requests_before = list((run_dir / "requests").glob("*.json")) if (run_dir / "requests").is_dir() else []
        prior = _os.environ.get("MMO_SIM_COMMUNITY_STEP_LIMIT")
        try:
            _os.environ["MMO_SIM_COMMUNITY_STEP_LIMIT"] = "abc"
            session._cmd_community()
        finally:
            if prior is None:
                _os.environ.pop("MMO_SIM_COMMUNITY_STEP_LIMIT", None)
            else:
                _os.environ["MMO_SIM_COMMUNITY_STEP_LIMIT"] = prior

        ready_after = [
            pk for pk in planned_keys
            if core_store.load_current_save_or_raise(run_dir, pk, ps_store, states_dir=states_dir) is not None
        ]
        assert len(ready_after) == 2, (
            f"ungueltiger expliziter ENV-Wert muss kontrolliert abgelehnt werden (KEIN "
            f"Vollpool-Fallback) -- unveraendert bei den bereits fertigen 2 haette bleiben "
            f"muessen, war: {ready_after}"
        )
        requests_after = list((run_dir / "requests").glob("*.json")) if (run_dir / "requests").is_dir() else []
        assert len(requests_after) == len(requests_before), (
            "ein abgelehntes ungueltiges Limit darf KEINEN einzigen neuen Request "
            "reservieren/senden."
        )
        assert any(
            "Begrenzter Fortschrittsschritt abgelehnt" in line and "abc" in line for line in printed
        ), "die Ablehnung muss sichtbar gemeldet werden (kontrolliert, nicht still)."


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
