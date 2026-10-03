#!/usr/bin/env python3
"""
tests/mmo_sim/test_n1_n7_persona_additional_figure_2026_10_02.py — N1-N7
(lokale Auftragsfaelle, KEINE A24/G6-IDs, P/04 "Team und Nachweise"):
Gate B des Terminal-Bestand/Neustart-Auftrags 2026-10-02 -- eine bekannte,
bereits spielende Persona erschafft auf ausdrueckliche Einladung einen
ZUSAETZLICHEN eigenen Chrononauten fuer einen gemeinsamen Level-1-
Frischstart (02_PERSONA_NEUER_CHRONONAUT.md).

Deckt den NEUEN Kandidaten (`domain/zeitriss/community_creation.py:
advance_additional_persona_creation`/`_publication_reconcile_additional`,
`ui/tui.py:_invite_persona_fresh_start`, verdrahtet aus `_cmd_new_or_
switch_character`):
  N1 - bekannter Mitspieler, frischer gemeinsamer Start (voller Terminalweg,
       BEIDE Persona-Providerprofile an echten Adaptergrenzen: Fake-CLI via
       `mmo_sim.adapters.fakes.FakeCLIProcess` + `PersonaClaudeCodeDriver`,
       loopback-HTTP via `mmo_sim.adapters.fakes.FakeHTTPServer` +
       `PersonaApiDriver` -- GM-Seite bleibt das bereits an anderer Stelle
       (H02/A24) an ihrer eigenen echten Adaptergrenze geprüfte `GmOwuiTransport`-
       Protokoll, hier als markiertes Fake-Double wie in `test_p2_community_
       creation.py` etabliert).
  N2 - keine Pflichtangleichung (Ablehnung UND bewusste Pause mitten im
       Erschaffungsdialog).
  N3 - A->B->A und Restart (letzter Stand von A bleibt erhalten; Reentry
       auf B ohne zweiten Modellaufruf).
  N4 - aktive Bindung/Konflikt (offene Tischbindung der alten Figur
       verhindert die Aktivierung der neuen Figur ohne Umgehungswrite).
  N5 - Abbruch/Antwort/Publikation (Transportfehler/Reentry nach Teilschritt
       ohne doppelten Request/doppelte Figur).
  N6 - Empfaengerkontext VOR der Adapterserialisierung (`ctx`-Dict, NICHT
       die tatsaechlichen STDIN-/HTTP-Bytes eines echten Adapters -- diese
       pruefen Gegenprobe 3/`test_r2_r6_fresh_start_durable_identity_
       2026_10_02.py:test_r6_...`): kein automatisches Uebernehmen alter
       Autoritaet/Wallet/Geheimnisse; fremde Sentinels fehlen (r2-Nacharbeit
       2026-10-02, 01_UNABHAENGIGE_REVIEW.md §5: vorherige Bezeichnung
       "Wire-Bytes" war fuer DIESEN Test wahrheitswidrig).
  N7 - vorhandene lokale Bedienintegration (aus dem realen `[n]`-Menuepfad
       erreichbar, kein neuer A24-Capture-/G6-Abnahmeumlauf).

Nutzt AUSSCHLIESSLICH markierte Fake-Doubles an der aeussersten Grenze
(analog `test_p2_community_creation.py`/`test_i1_i2_i3_worker_matrix.py`) --
der komplette Produktionsweg (`ui/tui.py` -> `domain/zeitriss/community_
creation.py` -> `core/creation_service.py` -> `core/admission.py`/
`core/request_ledger.py`/`core/store.py`/`domain/zeitriss/catalog.py`)
laeuft echt. Kein echter Modellcall, kein LAN. Pure Python, nur `assert`,
echter Exitcode."""
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

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.adapters.fakes import FakeCLIProcess, FakeHTTPServer  # noqa: E402
from mmo_sim.adapters.persona_api import PersonaApiConfig, PersonaApiDriver  # noqa: E402
from mmo_sim.adapters.persona_claude_code import ClaudeCodeConfig, PersonaClaudeCodeDriver  # noqa: E402
from mmo_sim.core import request_ledger  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.community_creation import (  # noqa: E402
    advance_additional_persona_creation,
    _additional_onboarding_key,
)
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
_CLI_HELP_TEXT = (
    "Usage: fake-claude [options]\n"
    "  --synthetic-safe  restrict tools/MCP/hooks/settings for tests\n"
)


# ---------------------------------------------------------------------------
# Gemeinsame Helfer (neue Testinfrastruktur, keine Produktdatei; reine
# Wiederverwendung vorhandener Produktfunktionen fuer Setup/Bootstrap --
# s. `test_p2_community_creation.py:_bootstrap`/`_draft_personas`-Vorbild).
# ---------------------------------------------------------------------------

def _new_env(root: Path):
    schema_path = _SCHEMA
    states_dir = root / "states"
    run_dir = root / "run"
    onboarding_dir = root / "onboarding"
    catalog_dir = root / "catalog"
    states_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    return schema_path, states_dir, run_dir, onboarding_dir, catalog_dir


def _v7_block(char_id: str, name: str = "Nova", level: int = 1) -> str:
    return (
        "```json\n"
        f'{{"v": 7, "characters": [{{"char_id": "{char_id}", "name": "{name}", '
        f'"callsign": "{name.upper()}", "level": {level}}}]}}\n'
        "```"
    )


def _old_fixture_save(char_id: str, name: str) -> dict:
    """Vollstaendiger ALTER Save mit erkennbaren, eindeutig NUR dieser alten
    Figur zugehoerigen Geheimnissen/Wallet (N6: diese duerfen NICHT
    automatisch in die neue Zusatzfigur-Erschaffung uebernommen werden)."""
    return {
        "v": 7, "save_id": f"fixture-{char_id}-old-001",
        "_fixture_note": "SIMULIERT/FIXTURE (N1-N7-Testfixture, ALTE Figur).",
        "characters": [{
            "char_id": char_id, "id": char_id, "name": name, "callsign": name.upper(),
            "level": 7,
            "wallet": {"credits": 9001},
            "inventory": ["ALT_GEHEIMES_ARTEFAKT_SENTINEL_" + char_id.upper()],
            "in_world_secret": "ALT_FIGURENGEHEIMNIS_SENTINEL_" + char_id.upper(),
        }],
    }


def _give_existing_figure(
    schema_path: Path, states_dir: Path, run_dir: Path, catalog_dir: Path, onboarding_dir: Path,
    participant_id: str, char_id: str, name: str, *,
    archetype: str = "SIMULIERT: etablierter Archetyp",
    play_style: str = "SIMULIERT: eigenstaendig, vorsichtig",
    charwunsch: str = "SIMULIERT/DEMO (N1-N7-Testfixture, bereits erspielt).",
) -> dict:
    """Stattet `participant_id` (Mensch ODER Persona -- `onboarding`/
    `catalog`/`core.store` sind teilnehmerunabhaengig) mit einer bereits
    VOLLSTAENDIG aktiven, aelteren Figur aus -- derselbe Produktweg wie
    `_cmd_new_or_switch_character`/`advance_one_persona_creation`
    (Onboarding -> Katalogregistrierung -> eigene Figursavebytes ->
    Persona-State-Identitaet -> Current-Publikation -> aktive Bindung).
    Das ETABLIERTE Profil (archetype/play_style/charwunsch) wird VOR der
    Identitaetsangleichung gesetzt, damit es (wie bei einer real bereits
    spielenden Persona) NICHT der technische Bootstrap-Platzhalter ist."""
    states_dir = Path(states_dir)
    states_dir.mkdir(parents=True, exist_ok=True)
    ps_store = PersonaStateStore(schema_path=schema_path)
    ps_store.save_state(participant_id, {
        "v": 2, "persona_key": participant_id, "real_name": name,
        "archetype": archetype, "play_style": play_style, "charwunsch": charwunsch,
        "plays_char": {
            "save_file": "NOCH_NICHT_ERSCHAFFEN", "character_id": "NOCH_NICHT_ERSCHAFFEN",
            "name": "NOCH_NICHT_ERSCHAFFEN", "callsign": "NOCH_NICHT_ERSCHAFFEN",
        },
        "rounds_played": 4,
    }, states_dir=states_dir)
    save = _old_fixture_save(char_id, name)
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
    """Ein eigenes GM-Fake PRO Chat-ID -- prueft, dass Antworten den
    jeweiligen echten Empfaenger erreichen (keine Vermischung zwischen
    menschlicher Erschaffung/Persona-Zusatzerschaffung/Tischspiel)."""

    def __init__(self, scripted_replies: list[str]):
        self.scripted = list(scripted_replies)
        self.calls: list[str] = []

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append(text)
        content = self.scripted.pop(0) if self.scripted else "Die Lage entwickelt sich weiter."
        return {"content": content, "usage": {"prompt_tokens": 5, "completion_tokens": 5}, "sources": [], "latency_s": 0.0, "chat_id": "n1n7"}


class _FailingGM:
    def __init__(self, fail_on_call_index: int = 0):
        self.fail_on_call_index = fail_on_call_index
        self.calls = 0

    def turn(self, idx, text, output_limit_tokens=None):
        hit = self.calls
        self.calls += 1
        if hit == self.fail_on_call_index:
            raise RuntimeError("simulierter Transportfehler (Netzwerk)")
        return {"content": "Die Lage entwickelt sich weiter.", "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "n1n7"}


class _FakePersonaDriver:
    """Leichtgewichtiges Fake AN DERSELBEN Protokollgrenze (`ParticipantDriver.
    decide(ctx) -> ParticipantDecision`) wie ein echter Adapter -- etabliertes
    Muster aus `test_p2_community_creation.py:_FakePersonaDriver`. Fuer N2-N7
    (gezielte Semantikpruefungen, keine erneute Adaptergrenzenbeweisfuehrung --
    die leistet N1 bereits mit den ECHTEN Adaptern). `invite_decision` steuert
    JEDE Anfrage mit `decision_contract` (Einladung ODER Zusatzfigur-Einladung);
    `answers` bedient normale Erschaffungs-Turns."""

    def __init__(self, persona_key: str, answers: list[str] | None = None, invite_decision: str = "accept"):
        self.persona_key = persona_key
        self.config = None
        self.answers = list(answers or [])
        self.invite_decision = invite_decision
        self.calls: list[dict] = []

    def decide(self, context: dict) -> ParticipantDecision:
        self.calls.append(context)
        contract = context.get("decision_contract")
        if contract:
            text = json.dumps({
                "offer_id": contract["offer_id"], "participant_id": contract["participant_id"],
                "decision": self.invite_decision,
            })
            return ParticipantDecision(text=text, origin_source="fake:n1n7", meta={"usage": {"prompt_tokens": 3, "completion_tokens": 3}})
        if not self.answers:
            raise RuntimeError(f"_FakePersonaDriver[{self.persona_key}]: keine weiteren Antworten gescriptet.")
        text = self.answers.pop(0)
        return ParticipantDecision(text=text, origin_source="fake:n1n7", meta={"usage": {"prompt_tokens": 3, "completion_tokens": 3}})


def _invite_offer_id(leader_id: str, persona_key: str, generation: int = 2) -> str:
    """Repliziert `TuiSession._invite_persona_fresh_start`s `offer_id`-Formel
    (r2-Nacharbeit 2026-10-02, 01_UNABHAENGIGE_REVIEW.md §4 BLOCKER
    "audit_loss_reuses_accept"): der zaehlende Bestandteil ist jetzt die
    ueber `onboarding.bind_attempt` VOR dem ersten Modellaufruf dauerhaft
    gebundene Generation der Einladungsgelegenheit -- GETRENNT vom
    best-effort Offer-Log (`lobby_service.append_offer_log_record`, dort
    `OSError` bewusst verschluckt). `generation` default `2`: in allen
    hiesigen Tests hat die eingeladene Persona vor DIESER EINEN
    gescripteten Einladung genau EINE bestehende Figur (`len(entries) +
    1 == 2` ist gleichzeitig der `seed_generation`-Startwert fuer die
    allererste Gelegenheit dieser (Leader, Persona)-Paarung)."""
    return f"fresh-start-invite-{persona_key}-{leader_id}-{generation}"


def _accept_contract_json(offer_id: str, persona_key: str) -> str:
    return json.dumps({"offer_id": offer_id, "participant_id": persona_key, "decision": "accept"})


def _reject_contract_json(offer_id: str, persona_key: str) -> str:
    return json.dumps({"offer_id": offer_id, "participant_id": persona_key, "decision": "reject"})


# ===========================================================================
# N1 — bekannter Mitspieler, frischer gemeinsamer Start (voller Terminalweg)
# ===========================================================================

def test_n1_fresh_start_cli_profile_full_journey():
    """Persona-Seite ueber den ECHTEN `claude_code_local`-Adapter
    (`PersonaClaudeCodeDriver`) gegen eine reale Fake-CLI-Prozessgrenze
    (`adapters.fakes.FakeCLIProcess`, ersetzt NUR `subprocess.run`/`Popen`)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        write_test_profile(run_dir)
        workdir = root / "persona_workdir"
        workdir.mkdir(parents=True, exist_ok=True)

        leader_id = "flo_human"
        _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, leader_id, "chrono-flo-old", "FloOld")
        old_medic_save = _give_existing_figure(
            schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, "medic", "chrono-medic-old", "MedicOld",
        )
        old_medic_hash_before = catalog.load_figure_save(catalog_dir, "medic", "chrono-medic-old")
        assert old_medic_hash_before == old_medic_save

        additional_key = _additional_onboarding_key("medic", 2)
        offer_id = _invite_offer_id(leader_id, "medic")
        accept_text = _accept_contract_json(offer_id, "medic")

        cli = FakeCLIProcess([
            (0, "fake-claude 1.0.0", ""),                 # invite driver: --version
            (0, _CLI_HELP_TEXT, ""),                      # invite driver: --help
            (0, json.dumps({"result": accept_text, "usage": {}, "is_error": False}), ""),  # invite decide()
            (0, "fake-claude 1.0.0", ""),                 # creation driver: --version
            (0, _CLI_HELP_TEXT, ""),                      # creation driver: --help
            (0, json.dumps({"result": "Phoenix.", "usage": {}, "is_error": False}), ""),  # creation answer
        ])

        def persona_factory(pk: str):
            assert pk == "medic"
            cfg = ClaudeCodeConfig(binary="fake-claude", isolated_workdir=str(workdir), extra_isolation_flags=["--synthetic-safe"])
            return PersonaClaudeCodeDriver(cfg, pk, process_runner=cli)

        def gm_factory(chat_id: str):
            if chat_id == f"onboarding-{leader_id}":
                return _GM([_v7_block("chrono-flo-fresh", "Flo2")])
            if chat_id == f"onboarding-{additional_key}":
                return _GM(["Wie soll dein Rufname lauten?", _v7_block("chrono-medic-fresh", "MedicFresh")])
            return _GM(["Die Runde beginnt."])

        printed: list[str] = []
        queued_inputs = ["neu", "medic"]

        def input_fn(prompt: str = "") -> str:
            if queued_inputs:
                return queued_inputs.pop(0)
            raise EOFError()

        session = TuiSession(
            onboarding_dir, catalog_dir, leader_id,
            input_fn=input_fn, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=gm_factory, persona_driver_factory=persona_factory,
        )
        session._cmd_new_or_switch_character()

        _assert_n1_outcome(
            run_dir, states_dir, catalog_dir, onboarding_dir, schema_path,
            leader_id, old_medic_save, printed,
        )

        # N1-Zusatznachweis "reguläre Tischaufnahme/öffentlicher Spielturn":
        # beide NEUEN Figuren nehmen ueber den unveraenderten `_cmd_local_
        # round`-Einladungsweg regulaer an einem Tisch teil.
        _assert_table_join_with_fresh_figures(
            run_dir, catalog_dir, onboarding_dir, states_dir, schema_path, leader_id, "medic",
        )


def test_n1_fresh_start_api_profile_full_journey():
    """Persona-Seite ueber den ECHTEN `openai_compatible`-Adapter
    (`PersonaApiDriver`) gegen eine reale loopback-HTTP-Doublegrenze
    (`adapters.fakes.FakeHTTPServer`, 127.0.0.1, kein LAN)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        write_test_profile(run_dir)

        leader_id = "flo_human"
        _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, leader_id, "chrono-flo-old", "FloOld")
        old_medic_save = _give_existing_figure(
            schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, "medic", "chrono-medic-old", "MedicOld",
        )

        additional_key = _additional_onboarding_key("medic", 2)
        offer_id = _invite_offer_id(leader_id, "medic")
        accept_text = _accept_contract_json(offer_id, "medic")

        with FakeHTTPServer([
            (200, {"choices": [{"message": {"content": accept_text}}], "usage": {}}),
            (200, {"choices": [{"message": {"content": "Phoenix."}}], "usage": {}}),
        ]) as server:
            def persona_factory(pk: str):
                assert pk == "medic"
                cfg = PersonaApiConfig(base_url=server.base_url, api_key="test-key", model="test-model")
                return PersonaApiDriver(cfg, pk)

            def gm_factory(chat_id: str):
                if chat_id == f"onboarding-{leader_id}":
                    return _GM([_v7_block("chrono-flo-fresh", "Flo2")])
                if chat_id == f"onboarding-{additional_key}":
                    return _GM(["Wie soll dein Rufname lauten?", _v7_block("chrono-medic-fresh", "MedicFresh")])
                return _GM(["Die Runde beginnt."])

            printed: list[str] = []
            queued_inputs = ["neu", "medic"]

            def input_fn(prompt: str = "") -> str:
                if queued_inputs:
                    return queued_inputs.pop(0)
                raise EOFError()

            session = TuiSession(
                onboarding_dir, catalog_dir, leader_id,
                input_fn=input_fn, print_fn=printed.append,
                run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
                gm_transport_factory=gm_factory, persona_driver_factory=persona_factory,
            )
            session._cmd_new_or_switch_character()

            assert len(server.calls) == 2, "beide Modellturns (Einladung + Zusatzfigur-Antwort) muessen die echte HTTP-Grenze erreichen"

        _assert_n1_outcome(
            run_dir, states_dir, catalog_dir, onboarding_dir, schema_path,
            leader_id, old_medic_save, printed,
        )


def _assert_n1_outcome(run_dir, states_dir, catalog_dir, onboarding_dir, schema_path, leader_id, old_medic_save, printed):
    ps_store = PersonaStateStore(schema_path=schema_path)

    # Neue Char-IDs fuer BEIDE (Mensch UND Persona) -- alte Figuren bleiben
    # unveraendert registriert und unveraendert in ihren eigenen Savebytes.
    medic_entries = {e.chrononaut_id for e in catalog.list_for_participant(catalog_dir, "medic")}
    assert medic_entries == {"chrono-medic-old", "chrono-medic-fresh"}, medic_entries
    assert catalog.load_figure_save(catalog_dir, "medic", "chrono-medic-old") == old_medic_save, (
        "alte Figur/Save darf durch die Zusatzfigur-Erschaffung NICHT veraendert werden"
    )
    flo_entries = {e.chrononaut_id for e in catalog.list_for_participant(catalog_dir, leader_id)}
    assert flo_entries == {"chrono-flo-old", "chrono-flo-fresh"}, flo_entries

    # Beide NEUEN Figuren sind jetzt die aktiven/tischbereiten Figuren.
    assert catalog.active_chrononaut_id(catalog_dir, "medic") == "chrono-medic-fresh"
    assert catalog.active_chrononaut_id(catalog_dir, leader_id) == "chrono-flo-fresh"
    medic_current = core_store.load_current_save_or_raise(run_dir, "medic", ps_store, states_dir=states_dir)
    assert medic_current["characters"][0]["char_id"] == "chrono-medic-fresh"
    flo_current = core_store.load_current_save_or_raise(run_dir, leader_id, ps_store, states_dir=states_dir)
    assert flo_current["characters"][0]["char_id"] == "chrono-flo-fresh"

    # KEIN level=1-Patch an einem alten Save, KEINE Uebernahme alter
    # Wallet-/Inventar-/Save-Refs (02 'Level'): die neue Figur ist ein
    # komplett EIGENER, von der KI-SL gelieferter Block ohne Wallet/
    # Inventar der alten Figur.
    assert "wallet" not in medic_current["characters"][0]
    assert "inventory" not in medic_current["characters"][0]
    assert medic_current["characters"][0].get("level", 1) == 1

    # Gleiche Personen-/Community-ID (die Persona bleibt "medic", keine
    # neue Identitaet/neue Community), neue technische Auftragsidentitaet
    # (eigene Onboarding-Scratchdatei, getrennt vom alten, laengst
    # abgeschlossenen Auftrag).
    assert onboarding.peek(onboarding_dir, "medic").final_save["characters"][0]["char_id"] == "chrono-medic-old", (
        "die ALTE Onboarding-Auftragsidentitaet von 'medic' bleibt unangetastet"
    )
    additional_state = onboarding.peek(onboarding_dir, _additional_onboarding_key("medic", 2))
    assert additional_state is not None and additional_state.status == "completed"
    assert additional_state.final_save["characters"][0]["char_id"] == "chrono-medic-fresh"

    assert any("Zusatzfigur erschaffen" in line or "tischbereit" in line for line in printed)


def _assert_table_join_with_fresh_figures(run_dir, catalog_dir, onboarding_dir, states_dir, schema_path, leader_id, persona_key):
    class _TableGM:
        def turn(self, idx, text, output_limit_tokens=None):
            return {"content": "Die Runde beginnt.", "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "table"}

    session = TuiSession(
        onboarding_dir, catalog_dir, leader_id,
        input_fn=lambda prompt="": (_ for _ in ()).throw(EOFError()),
        print_fn=lambda s: None,
        run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
        gm_transport_factory=lambda *_a, **_kw: _TableGM(),
        persona_driver_factory=lambda pk: _FakePersonaDriver(pk, invite_decision="accept"),
    )
    try:
        session._cmd_local_round([f"persona:{persona_key}"])
    except EndOfInput:
        pass  # Menschlicher Spielzug bricht erwartungsgemaess per EOF ab (A11/A16).

    table = core_store.Table.load(run_dir, f"local-{leader_id}-{persona_key}")
    assert persona_key in table.members
    assert table.chrononaut_id_to_persona()["chrono-medic-fresh"] == persona_key, (
        "der Tisch muss mit der NEUEN (nicht der alten) Figur entstanden sein"
    )
    assert table.chrononaut_id_to_persona()["chrono-flo-fresh"] == leader_id


# ===========================================================================
# N2 — keine Pflichtangleichung (Ablehnung UND bewusste Pause)
# ===========================================================================

def test_n2_persona_rejects_invite_keeps_old_figure_no_new_request():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        write_test_profile(run_dir)
        leader_id = "flo_human"
        _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, leader_id, "chrono-flo-old", "FloOld")
        old_save = _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, "medic", "chrono-medic-old", "MedicOld")
        before_hash = catalog.load_figure_save(catalog_dir, "medic", "chrono-medic-old")
        before_entries = {e.chrononaut_id for e in catalog.list_for_participant(catalog_dir, "medic")}

        def gm_factory_should_not_be_called(chat_id: str):
            raise AssertionError("Ablehnung der Einladung darf KEINEN Erschaffungsdialog starten")

        printed: list[str] = []
        queued = ["neu", "medic"]

        def input_fn(prompt: str = "") -> str:
            if queued:
                return queued.pop(0)
            raise EOFError()

        session = TuiSession(
            onboarding_dir, catalog_dir, leader_id,
            input_fn=input_fn, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=lambda chat_id: (
                _GM([_v7_block("chrono-flo-fresh2", "Flo3")]) if chat_id == f"onboarding-{leader_id}"
                else gm_factory_should_not_be_called(chat_id)
            ),
            persona_driver_factory=lambda pk: _FakePersonaDriver(pk, invite_decision="reject"),
        )
        session._cmd_new_or_switch_character()

        # Keine neue Figur, Katalog/Savebytes der alten Figur unveraendert.
        assert catalog.load_figure_save(catalog_dir, "medic", "chrono-medic-old") == before_hash == old_save
        assert {e.chrononaut_id for e in catalog.list_for_participant(catalog_dir, "medic")} == before_entries
        assert catalog.active_chrononaut_id(catalog_dir, "medic") == "chrono-medic-old"
        assert any("nicht angenommen" in line for line in printed)

        # Kein verdeckter Ersatz durch eine andere Persona / keine
        # automatische Vollgruppenbildung: der onboarding-Scratch der
        # Zusatzfigur wurde nie angelegt.
        from mmo_sim.domain.zeitriss.community_creation import _additional_onboarding_key as _key
        assert onboarding.peek(onboarding_dir, _key("medic", 2)) is None


def test_n2_persona_pauses_mid_creation_dialog_progress_retained_no_second_figure():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        write_test_profile(run_dir)
        leader_id = "flo_human"
        _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, leader_id, "chrono-flo-old", "FloOld")
        _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, "medic", "chrono-medic-old", "MedicOld")

        additional_key = _additional_onboarding_key("medic", 2)

        def gm_factory(chat_id: str):
            if chat_id == f"onboarding-{leader_id}":
                return _GM([_v7_block("chrono-flo-fresh3", "Flo4")])
            if chat_id == f"onboarding-{additional_key}":
                return _GM(["Wie soll dein Rufname lauten?"])  # keine zweite Frage -> Persona pausiert
            raise AssertionError("kein Tischweg in diesem Test erwartet")

        # Persona nimmt die Einladung an, pausiert aber dann WAEHREND des
        # eigentlichen Erschaffungsdialogs (strukturelle Kontrollzeile).
        request_count = {"n": 0}

        def persona_factory(pk: str):
            driver = _FakePersonaDriver(pk, answers=["STEUERUNG erschaffung_pause"], invite_decision="accept")
            orig_decide = driver.decide

            def counted_decide(ctx):
                if not ctx.get("decision_contract"):
                    request_count["n"] += 1
                return orig_decide(ctx)

            driver.decide = counted_decide
            return driver

        printed: list[str] = []
        queued = ["neu", "medic"]

        def input_fn(prompt: str = "") -> str:
            if queued:
                return queued.pop(0)
            raise EOFError()

        session = TuiSession(
            onboarding_dir, catalog_dir, leader_id,
            input_fn=input_fn, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=gm_factory, persona_driver_factory=persona_factory,
        )
        session._cmd_new_or_switch_character()

        assert request_count["n"] == 1, "genau EIN Modellaufruf fuer den pausierten Schritt, kein Doppelrequest"
        state = onboarding.peek(onboarding_dir, additional_key)
        assert state is not None and state.status == "in_progress", "Dialog bleibt offen/fortsetzbar, kein Fehler, kein Fake-Save"
        assert catalog.active_chrononaut_id(catalog_dir, "medic") == "chrono-medic-old", "kein Levelreset, keine neue Figur bei Pause"
        assert {e.chrononaut_id for e in catalog.list_for_participant(catalog_dir, "medic")} == {"chrono-medic-old"}


# ===========================================================================
# N3 — A->B->A und Restart
# ===========================================================================

def test_n3_a_to_b_to_a_then_restart_reactivates_b_without_new_model_call():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        write_test_profile(run_dir)
        ps_store = PersonaStateStore(schema_path=schema_path)
        old_save = _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, "tech", "chrono-tech-A", "TechA")

        # B wird ueber die neue Domaenenfunktion erschaffen (generation=2).
        additional_key = _additional_onboarding_key("tech", 2)

        def gm_factory(chat_id: str):
            assert chat_id == f"onboarding-{additional_key}"
            return _GM([_v7_block("chrono-tech-B", "TechB")])

        def persona_factory(pk: str):
            return _FakePersonaDriver(pk, answers=["Bereit."])

        outcome = advance_additional_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-tester", generation=2, persona_key="tech",
            gm_transport_factory=gm_factory, persona_driver_factory=persona_factory,
        )
        assert outcome.status == "completed" and outcome.chrononaut_id == "chrono-tech-B"
        assert catalog.active_chrononaut_id(catalog_dir, "tech") == "chrono-tech-B"
        # A's wirklich letzter Stand wurde VOR der Aktivierung von B
        # gesichert (Ausgangsfigur-Sync, I4 Luecke 1-Paritaet).
        assert catalog.load_figure_save(catalog_dir, "tech", "chrono-tech-A") == old_save

        # A->B->A: Rueckwahl ueber DIESELBEN generischen, teilnehmer-
        # unabhaengigen Primitiven, die `ui/tui.py:_switch_active_figure`
        # fuer einen Menschen benutzt (nur hier direkt auf `persona_key`
        # angewandt, kein neuer Store).
        b_current = core_store.load_current_save_or_raise(run_dir, "tech", ps_store, states_dir=states_dir)
        catalog.store_figure_save(catalog_dir, "tech", "chrono-tech-B", b_current)
        a_save = catalog.load_figure_save(catalog_dir, "tech", "chrono-tech-A")
        onboarding.ensure_participant_persona_state(ps_store, states_dir, "tech", "chrono-tech-A", a_save)
        core_store.publish_current_save(run_dir, "tech", a_save, ps_store, states_dir)
        catalog.bind_for_section(catalog_dir, "tech", "chrono-tech-A", has_open_section=False)

        a_current_after_restore = core_store.load_current_save_or_raise(run_dir, "tech", ps_store, states_dir=states_dir)
        assert a_current_after_restore == old_save, "A->B->A muss den wirklich letzten Stand von A wiederfinden"
        assert catalog.active_chrononaut_id(catalog_dir, "tech") == "chrono-tech-A"

        # "Restart": ein erneuter Aufruf fuer dieselbe, bereits fertige
        # Zusatzfigur (B) reaktiviert sie OHNE zweiten Modellaufruf (B ist
        # bereits `completed` -- derselbe Reentry-Vertrag wie
        # `advance_one_persona_creation`s `already_ready`).
        def gm_factory_must_not_be_called(chat_id: str):
            raise AssertionError("Restart auf eine bereits fertige Zusatzfigur darf keinen neuen SL-Dialog starten")

        def persona_factory_must_not_be_called(pk: str):
            raise AssertionError("Restart darf keinen neuen Persona-Request ausloesen")

        outcome2 = advance_additional_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-tester", generation=2, persona_key="tech",
            gm_transport_factory=gm_factory_must_not_be_called, persona_driver_factory=persona_factory_must_not_be_called,
        )
        assert outcome2.status == "completed" and outcome2.chrononaut_id == "chrono-tech-B"
        assert catalog.active_chrononaut_id(catalog_dir, "tech") == "chrono-tech-B", "Restart muss B wieder aktivieren"


# ===========================================================================
# N4 — aktive Bindung und Konflikt
# ===========================================================================

def test_n4_open_table_binding_on_old_figure_blocks_activation_no_bypass_write():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        write_test_profile(run_dir)
        ps_store = PersonaStateStore(schema_path=schema_path)
        old_save = _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, "sniper", "chrono-sniper-A", "SniperA")

        # Offene Tischbindung der ALTEN Figur -- derselbe reale Lock-
        # Mechanismus (`core.store.Lobby.lock_chrononaut`), den ein echter
        # laufender Tisch verwendet (kein handgeschriebener Sonderzustand).
        from mmo_sim.domain.zeitriss.policy import ZeitrissTableSizePolicy
        lobby = core_store.Lobby(run_dir, ZeitrissTableSizePolicy())
        lobby.lock_chrononaut("chrono-sniper-A", "local-irgendein-tisch")
        assert core_store.chrononaut_active_binding(run_dir, "chrono-sniper-A") is True

        additional_key = _additional_onboarding_key("sniper", 2)

        def gm_factory(chat_id: str):
            assert chat_id == f"onboarding-{additional_key}"
            return _GM([_v7_block("chrono-sniper-B", "SniperB")])

        def persona_factory(pk: str):
            return _FakePersonaDriver(pk, answers=["Bereit."])

        outcome = advance_additional_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-tester", generation=2, persona_key="sniper",
            gm_transport_factory=gm_factory, persona_driver_factory=persona_factory,
        )
        # Die neue Figur wird registriert+gesichert, aber NICHT aktiviert --
        # kein Umgehungswrite der realen Tischsperre, kein KI-Ersatz.
        assert outcome.status == "completed" and outcome.chrononaut_id == "chrono-sniper-B"
        assert "offenen Abschnitt" in outcome.reason
        assert catalog.active_chrononaut_id(catalog_dir, "sniper") == "chrono-sniper-A", (
            "gesperrte aktive Figur bleibt aktiv -- kein Umgehungswrite"
        )
        current = core_store.load_current_save_or_raise(run_dir, "sniper", ps_store, states_dir=states_dir)
        assert current == old_save, "Current bleibt unveraendert die ALTE (gebundene) Figur"
        assert catalog.load_figure_save(catalog_dir, "sniper", "chrono-sniper-B") is not None, "neue Figur bleibt registriert+gesichert"

        # Abgewiesene Aktion erhaelt alten kohaerenten Stand: Freigabe der
        # Sperre + erneuter Aufruf aktiviert B jetzt regulaer (kein
        # Doppelrequest, da bereits `completed`).
        lobby.release_chrononaut("chrono-sniper-A", "local-irgendein-tisch")

        def gm_factory_must_not_be_called(chat_id: str):
            raise AssertionError("Reconcile einer bereits abgeschlossenen Zusatzfigur darf keinen neuen Dialog starten")

        outcome2 = advance_additional_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-tester", generation=2, persona_key="sniper",
            gm_transport_factory=gm_factory_must_not_be_called, persona_driver_factory=lambda pk: (_ for _ in ()).throw(AssertionError("kein Request")),
        )
        assert outcome2.status == "completed"
        assert catalog.active_chrononaut_id(catalog_dir, "sniper") == "chrono-sniper-B"


# ===========================================================================
# N5 — Abbruch/Antwort/Publikation
# ===========================================================================

def test_n5_transport_failure_during_creation_keeps_old_figure_intact_resumable():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        write_test_profile(run_dir)
        ps_store = PersonaStateStore(schema_path=schema_path)
        old_save = _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, "cqb", "chrono-cqb-A", "CqbA")

        outcome1 = advance_additional_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-tester", generation=2, persona_key="cqb",
            gm_transport_factory=lambda chat_id: _FailingGM(fail_on_call_index=0),
            persona_driver_factory=lambda pk: _FakePersonaDriver(pk, answers=["Bereit."]),
        )
        assert outcome1.status == "error"
        # Alte Figur unveraendert, keine zweite Figur, kein Request fuer die
        # Persona ausgeloest (der Fehler lag auf der GM-Seite, VOR jeder
        # Personaanfrage fuer diesen Schritt).
        assert catalog.active_chrononaut_id(catalog_dir, "cqb") == "chrono-cqb-A"
        current = core_store.load_current_save_or_raise(run_dir, "cqb", ps_store, states_dir=states_dir)
        assert current == old_save

        gm_turn0_records_before = [
            r for r in request_ledger.open_requests(run_dir) + _all_accounted(run_dir)
            if r.get("participant") == _additional_onboarding_key("cqb", 2) and r.get("turn_idx") == 0
        ]
        assert len(gm_turn0_records_before) == 1, "GENAU ein Requestledger-Eintrag fuer den fehlgeschlagenen ersten Turn"

        # Reentry (frischer Aufruf, z.B. nach Neuversuch): derselbe offene
        # Auftrag wird fortgesetzt, KEIN zweiter Request fuer denselben
        # bereits versuchten (fehlgeschlagenen) Schritt haengt in der Luft --
        # ein neuer Turn-0-Request wird NICHT erneut reserviert, weil der
        # vorherige als `error` endete, nicht `received`; ein neuer Versuch
        # ist hier bewusst ein NEUER turn_idx=0-Request (GM-Fehler ist kein
        # durabler Treffer) -- geprueft wird ausschliesslich, dass dies
        # weiterhin GENAU EINEN zusaetzlichen Record erzeugt (kein
        # unkontrolliertes Mehrfach-Spawn).
        outcome2 = advance_additional_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-tester", generation=2, persona_key="cqb",
            gm_transport_factory=lambda chat_id: _GM([_v7_block("chrono-cqb-B", "CqbB")]),
            persona_driver_factory=lambda pk: _FakePersonaDriver(pk, answers=["Bereit."]),
        )
        assert outcome2.status == "completed" and outcome2.chrononaut_id == "chrono-cqb-B"
        assert catalog.active_chrononaut_id(catalog_dir, "cqb") == "chrono-cqb-B"


def test_n5_restart_after_full_completion_makes_zero_new_requests():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        write_test_profile(run_dir)
        _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, "face", "chrono-face-A", "FaceA")

        call_counter = {"n": 0}

        def gm_factory(chat_id: str):
            call_counter["n"] += 1
            return _GM([_v7_block("chrono-face-B", "FaceB")])

        outcome1 = advance_additional_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-tester", generation=2, persona_key="face",
            gm_transport_factory=gm_factory, persona_driver_factory=lambda pk: _FakePersonaDriver(pk, answers=["Bereit."]),
        )
        assert outcome1.status == "completed"
        assert call_counter["n"] == 1

        def gm_factory_should_not_be_called(chat_id: str):
            raise AssertionError("Reentry nach vollstaendiger Fertigstellung darf keinen neuen SL-Dialog starten")

        outcome2 = advance_additional_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-tester", generation=2, persona_key="face",
            gm_transport_factory=gm_factory_should_not_be_called,
            persona_driver_factory=lambda pk: (_ for _ in ()).throw(AssertionError("kein Request")),
        )
        assert outcome2.status == "already_ready"
        assert call_counter["n"] == 1, "kein zusaetzlicher Modellaufruf bei Reentry"


def _all_accounted(run_dir: Path) -> list[dict]:
    d = Path(run_dir) / "requests"
    if not d.is_dir():
        return []
    return [json.loads(p.read_text(encoding="utf-8")) for p in d.glob("*.json")]


# ===========================================================================
# N6 — Empfaengerkontext VOR der Adapterserialisierung (ctx-Dict, s.
# Modulkommentar oben -- r2-Nacharbeit: Label korrigiert, war "wire_context")
# ===========================================================================

def test_n6_ctx_dict_excludes_old_wallet_inventory_and_foreign_secrets():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        write_test_profile(run_dir)
        old_save = _give_existing_figure(
            schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, "pyro", "chrono-pyro-A", "PyroA",
            archetype="SIMULIERT: Chaotischer Improvisierer", play_style="SIMULIERT: unberechenbar",
            charwunsch="SIMULIERT: will Dinge explodieren sehen.",
        )
        # Fremde Persona mit eigenem, strikt privatem Sentinel -- darf in
        # KEINEM an 'pyro' gesendeten Wire-Text auftauchen.
        _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, "medic", "chrono-medic-foreign", "MedicForeign")

        captured_driver = _FakePersonaDriver("pyro", answers=["Nachbrenner."])

        def persona_factory(pk: str):
            assert pk == "pyro"
            return captured_driver

        outcome = advance_additional_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-tester", generation=2, persona_key="pyro",
            gm_transport_factory=lambda chat_id: _GM(["Wie soll dein Rufname lauten?", _v7_block("chrono-pyro-B", "PyroB")]),
            persona_driver_factory=persona_factory,
        )
        assert outcome.status == "completed"

        assert len(captured_driver.calls) == 1, "GENAU ein echter Erschaffungs-Turn fuer die Persona (eine Frage, eine Antwort)"
        ctx = captured_driver.calls[0]
        ctx_text = json.dumps(ctx, ensure_ascii=False, sort_keys=True)

        # Eigenes, bereits gepinntes Profil erreicht den Empfaenger.
        assert "Chaotischer Improvisierer" in ctx_text

        # Keine automatisch uebernommene alte Figurenautoritaet/Wallet/
        # Wissensgeheimnisse (02 'Teilnehmergedaechtnis != Figurenwissen').
        assert "9001" not in ctx_text, "altes Wallet darf nicht im ctx-Dict der neuen Erschaffung auftauchen"
        assert "ALT_GEHEIMES_ARTEFAKT_SENTINEL_CHRONO-PYRO-A".lower() not in ctx_text.lower()
        assert "ALT_FIGURENGEHEIMNIS_SENTINEL_CHRONO-PYRO-A".lower() not in ctx_text.lower()

        # Fremde private Sentinels (andere Persona) fehlen vollstaendig.
        assert "ALT_GEHEIMES_ARTEFAKT_SENTINEL_CHRONO-MEDIC-FOREIGN".lower() not in ctx_text.lower()
        assert "ALT_FIGURENGEHEIMNIS_SENTINEL_CHRONO-MEDIC-FOREIGN".lower() not in ctx_text.lower()
        assert "medic" not in ctx_text.lower()

        # System-Text kuendigt ehrlich eine ZUSAETZLICHE (nicht "erste")
        # Erschaffung an (02 'keine erfundene Zustimmung, kein verdeckter
        # Ersatz' -- der Modellprompt selbst darf die Lage nicht verschleiern).
        assert "ZUSAETZLICHEN" in ctx["system"]
        assert "pyro" in ctx["system"]
        # Die Onboarding-Scratchkennung (reine Buchhaltung) landet NICHT im
        # modellfacing Text -- nur die REALE Personakennung.
        assert _additional_onboarding_key("pyro", 2) not in ctx["system"]


# ===========================================================================
# N7 — vorhandene lokale Bedienintegration
# ===========================================================================

def test_n7_reachable_via_real_cmd_n_menu_dispatch():
    """Beweist die tatsaechliche Verdrahtung ueber den REALEN `[n]`-
    Menuepfad (`TuiSession._cmd_new_or_switch_character`, derselbe Code, den
    `run()` fuer die reale Tastenauswahl 'n' aufruft) -- kein separater
    A24-Capture-/G6-Abnahmeumlauf, keine neue Menuekarte."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        write_test_profile(run_dir)
        leader_id = "flo_human"
        _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, leader_id, "chrono-flo-old7", "FloOld7")
        _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, "sniper", "chrono-sniper-old7", "SniperOld7")

        additional_key = _additional_onboarding_key("sniper", 2)
        printed: list[str] = []
        queued = ["n", "neu", "Flo5", "sniper"]

        def input_fn(prompt: str = "") -> str:
            if queued:
                return queued.pop(0)
            raise EOFError()

        def gm_factory(chat_id: str):
            if chat_id == f"onboarding-{leader_id}":
                return _GM(["Wie soll dein Rufname lauten?", _v7_block("chrono-flo-fresh7", "Flo5")])
            if chat_id == f"onboarding-{additional_key}":
                return _GM([_v7_block("chrono-sniper-fresh7", "SniperFresh7")])
            raise AssertionError(f"unerwartete chat_id {chat_id!r}")

        session = TuiSession(
            onboarding_dir, catalog_dir, leader_id,
            input_fn=input_fn, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=gm_factory,
            persona_driver_factory=lambda pk: _FakePersonaDriver(pk, invite_decision="accept"),
        )
        # Echter Menueeintritt ueber `run()`s Auswahlschleife -- 'n' loest
        # GENAU `_cmd_new_or_switch_character` aus (s. `run()`-Dispatch).
        try:
            session.run()
        except EndOfInput:
            pass

        assert catalog.active_chrononaut_id(catalog_dir, "sniper") == "chrono-sniper-fresh7", (
            "der Zusatzfigur-Weg muss aus dem echten Boot-Menuedispatch ('n') erreichbar sein"
        )
        assert any("Zusatzfigur erschaffen" in line for line in printed), printed


# ===========================================================================
# N8 — End-Critic-Nacharbeit (END-CRITIC.md 2026-10-02, Finding 1, BLOCKER):
# eine ZWEITE, inhaltlich unabhaengige Einladung derselben Persona wird
# NICHT aus dem Requestledger repliziert, sondern real neu gefragt.
# ===========================================================================

def test_n8_second_independent_invite_to_same_persona_asks_again_not_replayed():
    """Gegenprobe des End-Critics (Gegenprobe 1) als dauerhafter
    Regressionstest nachgebildet: Runde 1 lehnt dieselbe Persona ab, Runde 2
    ist eine SPAETERE, inhaltlich unabhaengige Einladungsgelegenheit an
    DIESELBE Persona (z. B. nach einer weiteren eigenen Zusatzfigur des
    Menschen) und nimmt an. Vor der Nacharbeit war `offer_id`/`section_id`
    eine reine, statische Funktion von `(persona_key, participant_id)` --
    Runde 2 haette dadurch die laengst abgeschlossene Ablehnung aus Runde 1
    ueber `request_ledger.find_durable_result` repliziert bekommen, OHNE
    dass `driver.decide()` fuer Runde 2 je aufgerufen wird (Freiwilligkeits-
    verstoss). Beide Assertions unten waeren mit dem alten statischen Schema
    fehlgeschlagen."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        write_test_profile(run_dir)
        leader_id = "flo_human"
        _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, leader_id, "chrono-flo-old8", "FloOld8")
        _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, "medic", "chrono-medic-old8", "MedicOld8")

        invite_decide_calls = {"n": 0}
        decisions = ["reject", "accept"]
        additional_key2 = _additional_onboarding_key("medic", 2)

        class _CountingInviteDriver:
            def __init__(self, pk):
                self.pk = pk
                self.config = None

            def decide(self, context: dict) -> ParticipantDecision:
                contract = context.get("decision_contract")
                if contract:
                    invite_decide_calls["n"] += 1
                    kind = decisions[invite_decide_calls["n"] - 1]
                    text = json.dumps({
                        "offer_id": contract["offer_id"], "participant_id": contract["participant_id"],
                        "decision": kind,
                    })
                    return ParticipantDecision(text=text, origin_source="fake:n8", meta={"usage": {"prompt_tokens": 2, "completion_tokens": 2}})
                return ParticipantDecision(text="Nova.", origin_source="fake:n8", meta={"usage": {"prompt_tokens": 2, "completion_tokens": 2}})

        def gm_factory(chat_id: str):
            if chat_id == f"onboarding-{additional_key2}":
                return _GM(["Wie soll dein Rufname lauten?", _v7_block("chrono-medic-fresh8", "MedicFresh8")])
            raise AssertionError(f"unerwartete chat_id {chat_id!r} (kein Leaderpfad in diesem Test)")

        printed: list[str] = []

        def make_session(queued_inputs: list[str]) -> TuiSession:
            def input_fn(prompt: str = "") -> str:
                if queued_inputs:
                    return queued_inputs.pop(0)
                raise EOFError()
            return TuiSession(
                onboarding_dir, catalog_dir, leader_id,
                input_fn=input_fn, print_fn=printed.append,
                run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
                gm_transport_factory=gm_factory, persona_driver_factory=lambda pk: _CountingInviteDriver(pk),
            )

        # Runde 1: direkte, isolierte Einladung (ausserhalb des menschlichen
        # force_new-Pfades, um die bereits bekannte, separate Nebenbefund-
        # Replay-Eigenschaft DIESES Pfades hier nicht zu vermischen) -- die
        # Persona lehnt ab.
        make_session(["medic"])._invite_persona_fresh_start()
        assert invite_decide_calls["n"] == 1, "erste Einladung muss real gefragt werden"
        assert catalog.active_chrononaut_id(catalog_dir, "medic") == "chrono-medic-old8"

        # Runde 2: SPAETERE, inhaltlich unabhaengige Einladungsgelegenheit an
        # DIESELBE Persona -- muss real neu gefragt werden, nicht repliziert.
        make_session(["medic"])._invite_persona_fresh_start()

        assert invite_decide_calls["n"] == 2, (
            "zweite, unabhaengige Einladung an dieselbe Persona muss einen EIGENEN "
            "driver.decide()-Aufruf ausloesen -- NICHT die laengst abgeschlossene "
            "Ablehnung aus Runde 1 aus dem Requestledger repliziert bekommen "
            "(END-CRITIC.md 2026-10-02, Finding 1)."
        )
        assert catalog.active_chrononaut_id(catalog_dir, "medic") == "chrono-medic-fresh8", (
            "Persona hat der zweiten, unabhaengigen Einladung zugestimmt und ihre "
            "Zusatzfigur tatsaechlich erschaffen (kein repliziertes Alt-reject)"
        )
        assert any("Zusatzfigur erschaffen" in line for line in printed)


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
