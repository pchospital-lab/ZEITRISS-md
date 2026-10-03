#!/usr/bin/env python3
"""
tests/mmo_sim/test_r2_r6_fresh_start_durable_identity_2026_10_02.py — r2-Nacharbeit
(Terminal-Bestand/Neustart-Auftrag 2026-10-02, 02_NACHARBEITSAUFTRAG.md,
03_NACHWEISE_UND_TEAM.md R2-R6-Matrix) als dauerhafte Regressionstests fuer
`onboarding.bind_attempt`/`resolve_attempt` (`ui/tui.py:_cmd_new_or_switch_
character`/`_invite_persona_fresh_start`):

R2 - zweimal bewusst "neu" fuer DENSELBEN Menschen ueber den echten Menueweg:
     zwei unterschiedliche char_ids, bereits erspielter Fortschritt der
     ERSTEN neuen Figur bleibt in ihrem EIGENEN Save vollstaendig erhalten,
     A->B->A zeigt den letzten Stand (01_UNABHAENGIGE_REVIEW.md §3 BLOCKER
     "human_fresh_reset").
R3 - wiederholte echte Gelegenheiten an dieselbe Persona: reject->accept UND
     accept->reject, je GENAU EIN echter `driver.decide()`-Aufruf pro
     Gelegenheit, keine Ersatzpersona/Pflichtangleichung.
R4 - "audit_loss_reuses_accept"-BLOCKER (01_UNABHAENGIGE_REVIEW.md §4): nur
     der best-effort Auditlog-Append schlaegt fehl -> keine Kollision/kein
     Alt-Accept; UND ein operativer Bind-Fehler (Vorgangsidentitaet selbst
     nicht schreibbar) -> HOLD vor jedem Modellaufruf, kein Zaehler-/
     UUID-Ueberspringen.
R5 - Menue-Resume-Kontinuitaet: ein Prozess bricht NACH der empfangenen
     SL-Antwort, aber VOR dem lokalen Onboarding-Checkpoint ab -- eine
     fortsetzende TuiSession uebernimmt denselben Auftrag+dieselbe
     Generation und findet die bereits durabel abgerechnete Antwort wieder
     (kein zweiter Request fuer denselben bereits beantworteten Schritt).
R6 - Bestandsschutz an der ECHTEN Wire-Grenze (PersonaClaudeCodeDriver +
     FakeCLIProcess, wie N1/Gegenprobe 3): altes Wallet/Inventar/Geheimnis
     MEHRERER vorheriger eigener Generationen UND einer fremden Persona
     erscheinen in den tatsaechlichen STDIN-Bytes einer weiteren
     Zusatzerschaffung NICHT; alle Altfiguren bleiben unveraendert lesbar.

Nutzt AUSSCHLIESSLICH markierte Fake-Doubles an der aeussersten Grenze (wie
`test_n1_n7_persona_additional_figure_2026_10_02.py`) -- der komplette
Produktionsweg (`ui/tui.py` -> `domain/zeitriss/community_creation.py` ->
`core/creation_service.py` -> `core/admission.py`/`core/request_ledger.py`/
`core/store.py`/`domain/zeitriss/catalog.py`/`domain/zeitriss/onboarding.py`)
laeuft echt. Kein echter Modellcall, kein LAN. Pure Python, nur `assert`,
echter Exitcode."""
from __future__ import annotations

import json
import sys
import tempfile
import traceback
from pathlib import Path
from unittest.mock import patch

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.adapters.fakes import FakeCLIProcess  # noqa: E402
from mmo_sim.adapters.persona_claude_code import ClaudeCodeConfig, PersonaClaudeCodeDriver  # noqa: E402
from mmo_sim.core import lobby_service  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.community_creation import advance_additional_persona_creation  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
_CLI_HELP_TEXT = (
    "Usage: fake-claude [options]\n"
    "  --synthetic-safe  restrict tools/MCP/hooks/settings for tests\n"
)


def _new_env(root: Path):
    states_dir = root / "states"
    run_dir = root / "run"
    onboarding_dir = root / "onboarding"
    catalog_dir = root / "catalog"
    states_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    return states_dir, run_dir, onboarding_dir, catalog_dir


def _v7_block(char_id: str, name: str, level: int = 1) -> str:
    return (
        "```json\n"
        f'{{"v": 7, "characters": [{{"char_id": "{char_id}", "name": "{name}", '
        f'"callsign": "{name.upper()}", "level": {level}}}]}}\n'
        "```"
    )


def _give_existing_figure(states_dir, run_dir, catalog_dir, onboarding_dir, participant_id, char_id, name):
    ps_store = PersonaStateStore(schema_path=_SCHEMA)
    ps_store.save_state(participant_id, {
        "v": 2, "persona_key": participant_id, "real_name": name,
        "archetype": "R2-R6: etablierter Archetyp", "play_style": "R2-R6", "charwunsch": "R2-R6",
        "plays_char": {
            "save_file": "NOCH_NICHT_ERSCHAFFEN", "character_id": "NOCH_NICHT_ERSCHAFFEN",
            "name": "NOCH_NICHT_ERSCHAFFEN", "callsign": "NOCH_NICHT_ERSCHAFFEN",
        },
        "rounds_played": 2,
    }, states_dir=states_dir)
    save = {"v": 7, "characters": [{
        "char_id": char_id, "id": char_id, "name": name, "callsign": name.upper(), "level": 1,
    }]}
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, participant_id, char_id, save)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
    ))
    catalog.store_figure_save(catalog_dir, participant_id, char_id, save)
    core_store.publish_current_save(run_dir, participant_id, save, ps_store, states_dir)
    catalog.bind_for_section(catalog_dir, participant_id, char_id, has_open_section=False)
    return save


class _GM:
    """Zeichnet die tatsaechlich angefragten `turn_idx`-Werte auf -- das
    Pruefkriterium fuer R5 ist NICHT "wie oft insgesamt", sondern "wird
    EIN BESTIMMTER, bereits durabel beantworteter Turn ein zweites Mal
    angefragt"."""

    def __init__(self, scripted_replies):
        self.scripted = list(scripted_replies)
        self.calls: list[int] = []

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append(idx)
        content = self.scripted.pop(0) if self.scripted else "Die Lage entwickelt sich weiter."
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "r2r6"}


class _Driver:
    """Analog zur General-Review-Gegenprobenfixture: liefert Einladungs-
    entscheidungen gescriptet in Aufrufreihenfolge; normale Erschaffungs-
    turns antworten immer 'Bereit.' (keine weitere SL-Frage gescriptet)."""

    def __init__(self, decisions):
        self.decisions = list(decisions)
        self.invite_calls: list[dict] = []
        self.creation_calls = 0

    def decide(self, ctx: dict) -> ParticipantDecision:
        dc = ctx.get("decision_contract")
        if dc:
            decision = self.decisions[len(self.invite_calls)]
            self.invite_calls.append(dict(ctx))
            return ParticipantDecision(
                text=json.dumps({**dc, "decision": decision}), origin_source="r2r6", meta={"usage": {}},
            )
        self.creation_calls += 1
        return ParticipantDecision(text="Bereit.", origin_source="r2r6", meta={"usage": {}})


def _queued_input(values, default: str | None = None):
    """`default is None`: nach Erschoepfung der Queue wird `EOFError`
    (EndOfInput) ausgeloest -- Standardverhalten fuer die meisten Tests
    hier. `default` gesetzt: liefert diesen Wert fuer JEDE weitere Eingabe
    (z.B. eine feste Antwort auf wiederholte "Deine Antwort:"-Prompts)."""
    q = list(values)

    def input_fn(prompt: str = "") -> str:
        if q:
            return q.pop(0)
        if default is not None:
            return default
        raise EOFError()

    return input_fn


# ===========================================================================
# R2 — zweimal bewusst "neu" fuer denselben Menschen (echter Menueweg)
# ===========================================================================

def test_r2_two_deliberate_new_creations_preserve_first_figure_progress():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        write_test_profile(run_dir)
        _give_existing_figure(states_dir, run_dir, catalog_dir, onboarding_dir, "flo_human", "human-old", "Old")

        factory_calls: list[str] = []

        def gm_factory(chat_id: str):
            factory_calls.append(chat_id)
            return _GM([_v7_block(f"human-fresh-{len(factory_calls)}", "Fresh")])

        def make_session(inputs):
            return TuiSession(
                onboarding_dir, catalog_dir, "flo_human",
                input_fn=_queued_input(inputs), print_fn=lambda s: None,
                run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
                gm_transport_factory=gm_factory, persona_driver_factory=lambda pk: _Driver(["reject"]),
            )

        # Erste bewusst neue Erschaffung ("" beantwortet die anschliessende
        # Gate-B-Einladungsfrage mit "nein").
        make_session(["neu", ""])._cmd_new_or_switch_character()
        assert len(factory_calls) == 1, "erste bewusst neue Erschaffung muss GENAU EINEN echten SL-Dialog starten"
        assert {e.chrononaut_id for e in catalog.list_for_participant(catalog_dir, "flo_human")} == {
            "human-old", "human-fresh-1",
        }

        # Realer erspielter Fortschritt der ERSTEN neuen Figur -- ueber die
        # echte Current-Save-Autoritaet publiziert (wie im echten Spiel).
        ps_store = PersonaStateStore(schema_path=_SCHEMA)
        progressed = json.loads(json.dumps(
            core_store.load_current_save_or_raise(run_dir, "flo_human", ps_store, states_dir),
        ))
        progressed["characters"][0]["level"] = 4
        progressed["characters"][0]["wallet"] = {"credits": 123456}
        progressed["characters"][0]["inventory"] = ["R2_PROGRESS_SENTINEL"]
        core_store.publish_current_save(run_dir, "flo_human", progressed, ps_store, states_dir)

        # Zweite, BEWUSST NEUE (nicht fortsetzende) Erschaffung.
        make_session(["neu", ""])._cmd_new_or_switch_character()
        assert len(factory_calls) == 2, (
            "zweite bewusst neue Erschaffung muss einen EIGENEN echten SL-Dialog starten -- NICHT "
            "den laengst abgerechneten Save der ersten Erschaffung aus dem Requestledger "
            "wiederfinden (01_UNABHAENGIGE_REVIEW.md §3 BLOCKER 'human_fresh_reset')."
        )
        assert {e.chrononaut_id for e in catalog.list_for_participant(catalog_dir, "flo_human")} == {
            "human-old", "human-fresh-1", "human-fresh-2",
        }

        # Der erspielte Fortschritt der ERSTEN neuen Figur bleibt in ihrem
        # EIGENEN Save vollstaendig erhalten (kein Level-1-Ueberschreiben).
        preserved = catalog.load_figure_save(catalog_dir, "flo_human", "human-fresh-1")
        assert preserved["characters"][0]["level"] == 4
        assert preserved["characters"][0]["wallet"] == {"credits": 123456}
        assert preserved["characters"][0]["inventory"] == ["R2_PROGRESS_SENTINEL"]

        # Die ZWEITE neue Figur ist jetzt aktiv und startet ehrlich bei Level 1.
        assert catalog.active_chrononaut_id(catalog_dir, "flo_human") == "human-fresh-2"
        current = core_store.load_current_save_or_raise(run_dir, "flo_human", ps_store, states_dir)
        assert current["characters"][0]["char_id"] == "human-fresh-2"
        assert current["characters"][0].get("level", 1) == 1

        # A->B->A (03_NACHWEISE_UND_TEAM.md R2-Zeile): Rueckwahl auf die
        # ERSTE neue Figur zeigt weiterhin ihren letzten (progressed) Stand.
        make_session(["human-fresh-1"])._cmd_new_or_switch_character()
        assert len(factory_calls) == 2, "eine blosse Aktivierung ruft KEINEN neuen SL-Dialog auf"
        a_again = core_store.load_current_save_or_raise(run_dir, "flo_human", ps_store, states_dir)
        assert a_again["characters"][0]["char_id"] == "human-fresh-1"
        assert a_again["characters"][0]["level"] == 4
        assert a_again["characters"][0]["wallet"] == {"credits": 123456}


# ===========================================================================
# R3 — wiederholte echte Gelegenheiten an dieselbe Persona
# ===========================================================================

def test_r3_repeated_real_invite_opportunities_reject_then_accept():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        write_test_profile(run_dir)
        _give_existing_figure(states_dir, run_dir, catalog_dir, onboarding_dir, "flo_human", "human-old", "Old")
        _give_existing_figure(states_dir, run_dir, catalog_dir, onboarding_dir, "medic", "medic-old", "MedicOld")

        driver = _Driver(["reject", "accept"])

        def make_session(inputs):
            return TuiSession(
                onboarding_dir, catalog_dir, "flo_human",
                input_fn=_queued_input(inputs), print_fn=lambda s: None,
                run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
                gm_transport_factory=lambda chat_id: _GM([_v7_block("medic-new-r3", "New")]),
                persona_driver_factory=lambda pk: driver,
            )

        make_session(["medic"])._invite_persona_fresh_start()
        assert len(driver.invite_calls) == 1
        assert catalog.active_chrononaut_id(catalog_dir, "medic") == "medic-old", "Ablehnung erzeugt keine neue Figur"

        make_session(["medic"])._invite_persona_fresh_start()
        assert len(driver.invite_calls) == 2, "zweite, unabhaengige Gelegenheit muss real gefragt werden"
        medic_entries = {e.chrononaut_id for e in catalog.list_for_participant(catalog_dir, "medic")}
        assert len(medic_entries) == 2, "Annahme der zweiten Gelegenheit erzeugt genau EINE neue Figur"
        assert catalog.active_chrononaut_id(catalog_dir, "medic") != "medic-old"


def test_r3_repeated_real_invite_opportunities_accept_then_reject():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        write_test_profile(run_dir)
        _give_existing_figure(states_dir, run_dir, catalog_dir, onboarding_dir, "flo_human", "human-old", "Old")
        _give_existing_figure(states_dir, run_dir, catalog_dir, onboarding_dir, "sniper", "sniper-old", "SniperOld")

        driver = _Driver(["accept", "reject"])

        def make_session(inputs):
            return TuiSession(
                onboarding_dir, catalog_dir, "flo_human",
                input_fn=_queued_input(inputs), print_fn=lambda s: None,
                run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
                gm_transport_factory=lambda chat_id: _GM([_v7_block("sniper-new-r3", "New")]),
                persona_driver_factory=lambda pk: driver,
            )

        make_session(["sniper"])._invite_persona_fresh_start()
        assert len(driver.invite_calls) == 1
        first_entries = {e.chrononaut_id for e in catalog.list_for_participant(catalog_dir, "sniper")}
        assert len(first_entries) == 2, "Annahme erzeugt eine neue Figur"
        active_after_first = catalog.active_chrononaut_id(catalog_dir, "sniper")
        assert active_after_first != "sniper-old"

        make_session(["sniper"])._invite_persona_fresh_start()
        assert len(driver.invite_calls) == 2, (
            "zweite, unabhaengige Gelegenheit muss ERNEUT real gefragt werden -- kein Alt-Accept-Replay"
        )
        second_entries = {e.chrononaut_id for e in catalog.list_for_participant(catalog_dir, "sniper")}
        assert second_entries == first_entries, "Ablehnung der zweiten Gelegenheit erzeugt KEINE weitere Figur"
        assert catalog.active_chrononaut_id(catalog_dir, "sniper") == active_after_first, (
            "Ablehnung aendert die aktive Figur nicht"
        )


# ===========================================================================
# R4 — Audit-Schreibfehler vs. operativer Bind-Fehler
# ===========================================================================

def test_r4_audit_log_write_failure_causes_no_collision_or_stale_accept():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        write_test_profile(run_dir)
        _give_existing_figure(states_dir, run_dir, catalog_dir, onboarding_dir, "flo_human", "human-old", "Old")
        _give_existing_figure(states_dir, run_dir, catalog_dir, onboarding_dir, "medic", "medic-old", "MedicOld")

        driver = _Driver(["accept", "reject"])

        def make_session(inputs):
            return TuiSession(
                onboarding_dir, catalog_dir, "flo_human",
                input_fn=_queued_input(inputs), print_fn=lambda s: None,
                run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
                gm_transport_factory=lambda chat_id: _GM([_v7_block("medic-new-r4", "New")]),
                persona_driver_factory=lambda pk: driver,
            )

        orig_open = Path.open
        failures: list[str] = []

        def selective_fail(path, mode="r", *a, **kw):
            if path == run_dir / lobby_service.INVITATION_LOG_FILENAME and "a" in mode:
                failures.append(str(path))
                raise OSError("R4 synthetic audit append failure")
            return orig_open(path, mode, *a, **kw)

        with patch.object(Path, "open", selective_fail):
            make_session(["medic"])._invite_persona_fresh_start()
            after1 = {e.chrononaut_id for e in catalog.list_for_participant(catalog_dir, "medic")}
            make_session(["medic"])._invite_persona_fresh_start()
            after2 = {e.chrononaut_id for e in catalog.list_for_participant(catalog_dir, "medic")}

        assert failures, "Testaufbau muss den Audit-Append tatsaechlich treffen"
        assert len(driver.invite_calls) == 2, (
            "ein best-effort Audit-Schreibfehler darf KEINE Kollision der Einladungsidentitaet "
            "erzeugen -- die zweite Gelegenheit muss trotzdem real gefragt werden "
            "(01_UNABHAENGIGE_REVIEW.md §4 BLOCKER 'audit_loss_reuses_accept')."
        )
        assert len(after1) == 2 and after2 == after1, (
            "erste Gelegenheit (accept) erzeugt eine neue Figur, die zweite (reject) KEINE weitere"
        )


def test_r4_operative_bind_write_failure_holds_before_model_call():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        write_test_profile(run_dir)
        _give_existing_figure(states_dir, run_dir, catalog_dir, onboarding_dir, "flo_human", "human-old", "Old")
        _give_existing_figure(states_dir, run_dir, catalog_dir, onboarding_dir, "medic", "medic-old", "MedicOld")

        driver = _Driver(["accept"])
        printed: list[str] = []

        def gm_factory(chat_id: str):
            raise AssertionError("HOLD-Fall darf NIE einen GM-Transport anfordern")

        session = TuiSession(
            onboarding_dir, catalog_dir, "flo_human",
            input_fn=_queued_input(["medic"]), print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=gm_factory, persona_driver_factory=lambda pk: driver,
        )
        with patch.object(onboarding, "bind_attempt", side_effect=OSError("R4 synthetic operative bind failure")):
            session._invite_persona_fresh_start()

        assert len(driver.invite_calls) == 0, "ein operativer Bind-Fehler muss VOR jedem Modellaufruf halten"
        assert catalog.active_chrononaut_id(catalog_dir, "medic") == "medic-old"
        assert any("HALT" in line for line in printed), printed


# ===========================================================================
# R5 — Menue-Resume-Kontinuitaet
# ===========================================================================

def test_r5_menu_resume_recovers_durable_reply_after_local_checkpoint_write_failure():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        write_test_profile(run_dir)
        _give_existing_figure(states_dir, run_dir, catalog_dir, onboarding_dir, "flo_human", "human-old", "Old")

        gm = _GM(["Wie soll dein Rufname lauten?", _v7_block("human-fresh-r5", "Fresh5")])

        def gm_factory(chat_id: str):
            return gm

        session = TuiSession(
            onboarding_dir, catalog_dir, "flo_human",
            input_fn=_queued_input(["neu"], default="Phoenix."), print_fn=lambda s: None,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=gm_factory, persona_driver_factory=lambda pk: _Driver([]),
        )

        orig_record_pending_reply = onboarding.record_pending_reply
        calls = {"n": 0}

        def failing_once(*a, **kw):
            calls["n"] += 1
            if calls["n"] == 1:
                raise OSError("R5 synthetic local checkpoint write failure")
            return orig_record_pending_reply(*a, **kw)

        raised = False
        with patch.object(onboarding, "record_pending_reply", side_effect=failing_once):
            try:
                session._cmd_new_or_switch_character()
            except OSError:
                raised = True
        assert raised, "ein lokaler Checkpoint-Schreibfehler muss ungefangen propagieren (kein stiller Datenverlust)"
        assert gm.calls == [0], "GENAU EIN echter SL-Turn (turn_idx=0) vor dem injizierten Fehler"
        assert {e.chrononaut_id for e in catalog.list_for_participant(catalog_dir, "flo_human")} == {"human-old"}, (
            "der abgebrochene Versuch darf KEINE neue Figur registriert haben"
        )

        # Fortsetzende TuiSession (z.B. nach Prozessneustart) -- DIESELBE
        # Operationsidentitaet (Generation blieb unresolved/offen) findet
        # die bereits durabel abgerechnete SL-Antwort im Requestledger
        # wieder, OHNE Turn 0 ein zweites Mal anzufragen.
        resumed = TuiSession(
            onboarding_dir, catalog_dir, "flo_human",
            input_fn=_queued_input(["neu"], default="Phoenix."), print_fn=lambda s: None,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=gm_factory, persona_driver_factory=lambda pk: _Driver([]),
        )
        resumed._cmd_new_or_switch_character()

        assert gm.calls == [0, 1], (
            "Wiederaufnahme darf den bereits durabel beantworteten Turn 0 NICHT erneut anfragen -- "
            "nur der echte NEUE Turn 1 (Namensantwort -> Save) ist ein zusaetzlicher realer Request."
        )
        entries = {e.chrononaut_id for e in catalog.list_for_participant(catalog_dir, "flo_human")}
        assert entries == {"human-old", "human-fresh-r5"}, entries


# ===========================================================================
# R6 — Bestandsschutz an der echten Wire-Grenze
# ===========================================================================

def test_r6_real_wire_bytes_exclude_all_prior_generations_and_foreign_secrets():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        write_test_profile(run_dir)
        workdir = root / "persona_workdir"
        workdir.mkdir(parents=True, exist_ok=True)

        def _secret_save(char_id: str, name: str, tag: str, level: int = 7) -> dict:
            return {
                "v": 7, "save_id": f"fixture-{char_id}",
                "characters": [{
                    "char_id": char_id, "id": char_id, "name": name, "callsign": name.upper(), "level": level,
                    "wallet": {"credits": 13579},
                    "inventory": [f"R6_ARTEFAKT_{tag}"],
                    "in_world_secret": f"R6_GEHEIMNIS_{tag}",
                }],
            }

        def _give_secret_figure(participant_id: str, char_id: str, name: str, tag: str):
            ps_store = PersonaStateStore(schema_path=_SCHEMA)
            ps_store.save_state(participant_id, {
                "v": 2, "persona_key": participant_id, "real_name": name,
                "archetype": "R6: eigener Archetyp", "play_style": "R6", "charwunsch": "R6",
                "plays_char": {
                    "save_file": "NOCH_NICHT_ERSCHAFFEN", "character_id": "NOCH_NICHT_ERSCHAFFEN",
                    "name": "NOCH_NICHT_ERSCHAFFEN", "callsign": "NOCH_NICHT_ERSCHAFFEN",
                },
                "rounds_played": 1,
            }, states_dir=states_dir)
            save = _secret_save(char_id, name, tag)
            onboarding.start_or_resume(onboarding_dir, participant_id)
            onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
            onboarding.ensure_participant_persona_state(ps_store, states_dir, participant_id, char_id, save)
            catalog.register(catalog_dir, catalog.CatalogEntry(
                participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
            ))
            catalog.store_figure_save(catalog_dir, participant_id, char_id, save)
            core_store.publish_current_save(run_dir, participant_id, save, ps_store, states_dir)
            catalog.bind_for_section(catalog_dir, participant_id, char_id, has_open_section=False)
            return save

        _give_secret_figure("pyro6", "chrono-pyro6-gen1", "Pyro6Gen1", "PYRO6GEN1")
        # Zweite Figur DERSELBEN Persona, als eigener getrennter Katalog-
        # eintrag -- simuliert eine bereits abgeschlossene VORHERIGE
        # Zusatzerschaffung ueber genau denselben Produktweg (NICHT die
        # aktive Figur, aber real registriert+gesichert).
        onboarding.start_or_resume(onboarding_dir, "pyro6__additional_gen2")
        save_gen2 = _secret_save("chrono-pyro6-gen2", "Pyro6Gen2", "PYRO6GEN2")
        onboarding.complete_with_save(
            onboarding_dir, "pyro6__additional_gen2", save_gen2, ZeitrissHarvestValidator(), "chrono-pyro6-gen2",
        )
        catalog.register(catalog_dir, catalog.CatalogEntry(
            participant_id="pyro6", chrononaut_id="chrono-pyro6-gen2", persona_key="pyro6",
        ))
        catalog.store_figure_save(catalog_dir, "pyro6", "chrono-pyro6-gen2", save_gen2)

        _give_secret_figure("medic6", "chrono-medic6-foreign", "Medic6Foreign", "MEDIC6FOREIGN")

        cli = FakeCLIProcess([
            (0, "fake-claude 1.0.0", ""),
            (0, _CLI_HELP_TEXT, ""),
            (0, json.dumps({"result": "Nachbrenner.", "usage": {}, "is_error": False}), ""),
        ])

        def persona_factory(pk: str):
            assert pk == "pyro6"
            cfg = ClaudeCodeConfig(binary="fake-claude", isolated_workdir=str(workdir), extra_isolation_flags=["--synthetic-safe"])
            return PersonaClaudeCodeDriver(cfg, pk, process_runner=cli)

        def gm_factory(chat_id: str):
            # Eine Zwischenfrage VOR dem Save-Block ist noetig, damit die
            # Persona tatsaechlich EINMAL real ueber die echte Subprozess-
            # grenze antworten muss (sonst liefert die GM-Seite den Save
            # bereits auf Turn 0 und `cli` wird nie fuer einen echten
            # decide()-Aufruf beansprucht, wie bei Gegenprobe 3).
            return _GM(["Wie soll dein Rufname lauten?", _v7_block("chrono-pyro6-gen3", "Pyro6Gen3")])

        outcome = advance_additional_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-r6", generation=3, persona_key="pyro6",
            gm_transport_factory=gm_factory, persona_driver_factory=persona_factory,
        )
        assert outcome.status == "completed" and outcome.chrononaut_id == "chrono-pyro6-gen3"

        real_decide_calls = [c for c in cli.calls if c.argv[:2] == ["fake-claude", "-p"]]
        assert len(real_decide_calls) == 1
        real_stdin = real_decide_calls[0].stdin

        assert "13579" not in real_stdin, "altes Wallet (beider Vorgenerationen) darf nicht auftauchen"
        for tag in ("PYRO6GEN1", "PYRO6GEN2"):
            assert f"R6_ARTEFAKT_{tag}" not in real_stdin
            assert f"R6_GEHEIMNIS_{tag}" not in real_stdin
        assert "R6_ARTEFAKT_MEDIC6FOREIGN" not in real_stdin
        assert "R6_GEHEIMNIS_MEDIC6FOREIGN" not in real_stdin
        assert "medic6" not in real_stdin.lower()

        # Bestand: ALLE Altfiguren (beide eigenen Generationen + fremde
        # Persona) bleiben unveraendert lesbar.
        assert catalog.load_figure_save(catalog_dir, "pyro6", "chrono-pyro6-gen1")["characters"][0]["in_world_secret"] == "R6_GEHEIMNIS_PYRO6GEN1"
        assert catalog.load_figure_save(catalog_dir, "pyro6", "chrono-pyro6-gen2")["characters"][0]["in_world_secret"] == "R6_GEHEIMNIS_PYRO6GEN2"
        assert catalog.load_figure_save(catalog_dir, "medic6", "chrono-medic6-foreign")["characters"][0]["in_world_secret"] == "R6_GEHEIMNIS_MEDIC6FOREIGN"


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
