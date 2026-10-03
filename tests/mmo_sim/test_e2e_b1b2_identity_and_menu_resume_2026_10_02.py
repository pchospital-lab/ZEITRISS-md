#!/usr/bin/env python3
"""
tests/mmo_sim/test_e2e_b1b2_identity_and_menu_resume_2026_10_02.py --
E2E-Nacharbeit (End-Critic-Verdikt BLOCKED_SCOPED_WITH_CONFIRMED_PARTIAL_FIXES,
2026-10-02, `02_B1B2_NACHZUG.md` §A-§D): dauerhafte Repo-Tests fuer die drei
verbleibenden Faelle an der Abschluss-/Identitaets-/Publikationsnahtstelle
(`ui/tui.py:_finish_new_character_creation`, `domain/zeitriss/
community_creation.py:_publication_reconcile_additional`), adaptiert aus den
Lieferproben (`reproduction/evidence/general_b1b2_end_to_end.py` und der
Menue-Variante `general_b1b2_end_to_end_menu_v2.py`), PLUS der bereits
zweimal offen gebliebene Human-B1-Katalog-I/O-Fall (Critic-Auflage der
R0/R1-Runden, adaptiert aus `general_r2_release_boundary_probes.py`):

  E2E-A (B2-CURRENT) -- `_finish_new_character_creation` darf einen bereits
    fortgeschrittenen Current NICHT auf einen archivgleichen, aber
    veralteten Stand zuruecksetzen, nur weil ein neuer (fehlerhafter)
    SL-Output zufaellig dieselben Bytes wie das Archiv liefert.
  E2E-B (B2-OWNER) -- bekannte FREMDE Eigentuemerschaft (Mensch UND Persona)
    haelt UNABHAENGIG von Save-Inhaltsgleichheit.
  E2E-C (B1-MENUE) -- eine bereits angenommene, aber nach einem Katalog-/
    Figursave-I/O-Fehler noch nicht vollstaendig persistierte Zusatzfigur-
    Erschaffung ist in einer FRISCH GESTARTETEN TUI ueber die neue
    'fortsetzen:<persona-id>'-Auswahl fortsetzbar -- 0 zusaetzliche
    Menschenfiguren, 0 zusaetzliche Einladungsentscheidungen.
  Human-B1-Katalog-I/O (`catalog.register`/`catalog.store_figure_save`,
    jeweils EIN echter `OSError`) -- derselbe Vorgang wird im naechsten
    Menue-Reentry OHNE zweiten SL-Turn fertiggestellt.
  E2E-C-Grenzfall (R-E2E-2 SOLLTE-1, 2026-10-02, 02_B1B2_NACHZUG.md §C) --
    eine NEUE, UNABHAENGIGE Einladung an DIESELBE Persona (waehrend eine
    AELTERE, noch unpersistierte Zusatzfigur-Erschaffung derselben Persona
    offen ist) wird frisch entschieden; eine Ablehnung dieser neuen
    Gelegenheit loescht/ueberschreibt den aelteren angenommenen, noch
    offenen Vorgang NICHT -- er bleibt unveraendert ueber 'fortsetzen:'
    spaeter fertigstellbar. Adaptiert aus der End-Critic-eigenen Probe
    `critic/evidence/critic_probe_independent_invite_reject_preserves_pending.py`
    (dort nur Einmalbeleg, hier als dauerhafter `run_all.py`-Schutz).

Alle Tests nutzen den ECHTEN `TuiSession.run()`-Menue-/Dispatchweg (keine
privaten Helper-Abkuerzungen) inkl. frischem Session-Neustart, wo die
Lieferprobe das vorsieht. Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import copy
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

from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.community_creation import (  # noqa: E402
    advance_additional_persona_creation,
    find_resumable_additional_creation,
    _additional_onboarding_key,
)
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


def _v7_block(char_id: str, name: str, **extra) -> str:
    body = {"v": 7, "characters": [{"char_id": char_id, "name": name, "callsign": name.upper(), "level": 1, **extra}]}
    return "```json\n" + json.dumps(body) + "\n```"


def _give_existing_figure(states_dir, run_dir, catalog_dir, onboarding_dir, participant_id, char_id, name):
    ps_store = PersonaStateStore(schema_path=_SCHEMA)
    ps_store.save_state(participant_id, {
        "v": 2, "persona_key": participant_id, "real_name": name,
        "archetype": "E2E-NACHARBEIT", "play_style": "E2E-NACHARBEIT", "charwunsch": "E2E-NACHARBEIT",
        "plays_char": {"save_file": "NOCH_NICHT_ERSCHAFFEN", "character_id": "NOCH_NICHT_ERSCHAFFEN",
                        "name": "NOCH_NICHT_ERSCHAFFEN", "callsign": "NOCH_NICHT_ERSCHAFFEN"},
        "rounds_played": 1,
    }, states_dir=states_dir)
    save = {"v": 7, "save_id": f"fixture-{char_id}", "characters": [
        {"char_id": char_id, "id": char_id, "name": name, "callsign": name.upper(), "level": 7},
    ]}
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, participant_id, char_id, save)
    catalog.register(catalog_dir, catalog.CatalogEntry(participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id))
    catalog.store_figure_save(catalog_dir, participant_id, char_id, save)
    core_store.publish_current_save(run_dir, participant_id, save, ps_store, states_dir)
    catalog.bind_for_section(catalog_dir, participant_id, char_id, has_open_section=False)
    return save


def _setup(root: Path):
    states, run, onb, cat = root / "states", root / "run", root / "onboarding", root / "catalog"
    run.mkdir(parents=True, exist_ok=True)
    write_test_profile(run)
    _give_existing_figure(states, run, cat, onb, "flo_human", "human-old", "flo_human")
    _give_existing_figure(states, run, cat, onb, "medic", "medic-old", "medic")
    return states, run, onb, cat


def _current(paths, who):
    states, run, onb, cat = paths
    return core_store.load_current_save_or_raise(run, who, PersonaStateStore(schema_path=_SCHEMA), states)


class _GM:
    def __init__(self, replies, calls, chat):
        self.replies = list(replies)
        self.calls = calls
        self.chat = chat

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append({"chat": self.chat, "idx": idx, "text": text})
        if not self.replies:
            raise AssertionError("GM fixture depleted")
        return {"content": self.replies.pop(0), "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": self.chat}


class _Driver:
    def __init__(self, decisions):
        self.decisions = decisions
        self.invites = []
        self.creation = 0

    def decide(self, ctx):
        dc = ctx.get("decision_contract")
        if dc:
            decision = self.decisions[len(self.invites)]
            self.invites.append(copy.deepcopy(ctx))
            return ParticipantDecision(text=json.dumps(dict(dc, decision=decision)), origin_source="E2E_TEST", meta={"usage": {}})
        self.creation += 1
        return ParticipantDecision(text="Bereit.", origin_source="E2E_TEST", meta={"usage": {}})


def _sess(paths, factory, driver, answers, prints, who="flo_human"):
    states, run, onb, cat = paths
    answers = iter(answers)

    def read(prompt=""):
        try:
            return next(answers)
        except StopIteration:
            raise EOFError()

    return TuiSession(
        onb, cat, who, input_fn=read, print_fn=prints.append, run_dir=run, states_dir=states,
        schema_path=_SCHEMA, gm_transport_factory=factory, persona_driver_factory=lambda p: driver,
    )


def test_e2e_a_stale_current_archive_does_not_regress_progressed_current():
    """E2E-A (B2-CURRENT). Reale Menuefolge: `n -> neu` erschafft
    `human-new-1` (Level 1). Ein spaeterer, echter Fortschritt (Level 4/
    Wallet/Inventarmarker) wird ueber die Current-Publikationsautoritaet
    geschrieben; der Katalogsave bleibt (produktbedingt getrennt) beim
    Level-1-Stand. Ein bewusst weiterer `n -> neu` liefert (SL-Fehlverhalten)
    dieselbe ID mit GENAU dem alten archivierten Inhalt -- Current darf NICHT
    auf Level 1 zurueckfallen."""
    with tempfile.TemporaryDirectory() as td:
        paths = _setup(Path(td))
        states, run, onb, cat = paths
        calls, prints = [], []
        driver = _Driver(["reject"])

        factory1 = lambda chat: _GM([_v7_block("human-new-1", "Fresh")], calls, chat)
        _sess(paths, factory1, driver, ["n", "neu", "", "x"], prints).run()

        archived = copy.deepcopy(catalog.load_figure_save(cat, "flo_human", "human-new-1"))
        progressed = copy.deepcopy(_current(paths, "flo_human"))
        progressed["characters"][0].update(level=4, wallet={"credits": 4711}, inventory=["KEEP_CURRENT_NOT_CATALOG"])
        core_store.publish_current_save(run, "flo_human", progressed, PersonaStateStore(schema_path=_SCHEMA), states)
        assert catalog.load_figure_save(cat, "flo_human", "human-new-1") == archived

        factory2 = lambda chat: _GM(["```json\n" + json.dumps(archived) + "\n```"], calls, chat)
        _sess(paths, factory2, driver, ["n", "neu", "", "x"], prints).run()

        after_current = _current(paths, "flo_human")
        after_archive = catalog.load_figure_save(cat, "flo_human", "human-new-1")
        assert after_current == progressed, f"Current darf nicht zurueckfallen: {after_current}"
        assert after_archive == archived, "Archiv bleibt unveraendert (kein Write bei HOLD)"
        assert len(calls) == 2, "zwei echte, distincte SL-Requests (kein Replay)"


def test_e2e_b_foreign_equal_bytes_human_holds_ownership():
    """E2E-B (B2-OWNER), Mensch. `flo_human` erhaelt im echten `n -> neu`-
    Menue `medic-old` mit IDENTISCHEM Fremdinhalt -- bekannte Fremd-
    Eigentuemerschaft (medic) haelt, UNABHAENGIG von der Byte-Gleichheit."""
    with tempfile.TemporaryDirectory() as td:
        paths = _setup(Path(td))
        states, run, onb, cat = paths
        calls, prints = [], []
        foreign = copy.deepcopy(catalog.load_figure_save(cat, "medic", "medic-old"))
        factory = lambda chat: _GM(["```json\n" + json.dumps(foreign) + "\n```"], calls, chat)
        _sess(paths, factory, _Driver(["reject"]), ["n", "neu", "", "x"], prints).run()

        after = _current(paths, "flo_human")
        ids = [e.chrononaut_id for e in catalog.list_for_participant(cat, "flo_human")]
        assert "medic-old" not in ids, f"fremde ID darf NICHT im eigenen Katalog landen: {ids}"
        assert after["characters"][0]["char_id"] != "medic-old", "Current darf NICHT die fremde Figur uebernehmen"
        assert catalog.load_figure_save(cat, "medic", "medic-old") == foreign, "Fremdarchiv bleibt unveraendert"


def test_e2e_b_foreign_equal_bytes_persona_holds_ownership():
    """E2E-B (B2-OWNER), Persona. `medic` erhaelt ueber `advance_additional_
    persona_creation` IDENTISCHE Bytes von `human-old` -- dieselbe
    Eigentuemergrenze gilt am Persona-Zusatzfigur-Pfad (keine
    Sonderloesung nur fuer die Human-Probe)."""
    with tempfile.TemporaryDirectory() as td:
        paths = _setup(Path(td))
        states, run, onb, cat = paths
        foreign = copy.deepcopy(catalog.load_figure_save(cat, "flo_human", "human-old"))
        calls = []
        factory = lambda chat: _GM(["```json\n" + json.dumps(foreign) + "\n```"], calls, chat)
        result = advance_additional_persona_creation(
            run_dir=run, states_dir=states, schema_path=_SCHEMA, onboarding_dir=onb, catalog_dir=cat,
            community_id="community-flo_human", generation=2, persona_key="medic",
            gm_transport_factory=factory, persona_driver_factory=lambda p: _Driver(["accept"]),
        )
        assert result.status == "blocked", f"erwartetes HOLD, erhalten: {result}"
        ids = [e.chrononaut_id for e in catalog.list_for_participant(cat, "medic")]
        assert "human-old" not in ids, f"fremde ID darf NICHT im eigenen Katalog landen: {ids}"
        after = _current(paths, "medic")
        assert after["characters"][0]["char_id"] != "human-old"
        assert catalog.load_figure_save(cat, "flo_human", "human-old") == foreign, "Fremdarchiv bleibt unveraendert"


def test_e2e_c_persona_menu_resume_completes_without_new_human_figure_or_invite():
    """E2E-C (B1-MENUE). Nach einem echten Figursave-I/O-Fehler (NACH
    erfolgreichem `catalog.register`) ist `medic`s angenommene, aber noch
    nicht persistierte Zusatzfigur in einer FRISCH GESTARTETEN TUI ueber
    `fortsetzen:medic` fortsetzbar -- 0 zusaetzliche Menschenfiguren, 0
    zusaetzliche Einladungsentscheidungen, kein neuer SL-Turn, Save wird
    nachgetragen."""
    with tempfile.TemporaryDirectory() as td:
        paths = _setup(Path(td))
        states, run, onb, cat = paths
        calls, prints = [], []
        human_no = [0]
        driver = _Driver(["accept"])

        def factory(chat):
            if "__additional_gen" in chat:
                cid = "medic-new-1"
            else:
                human_no[0] += 1
                cid = f"human-new-{human_no[0]}"
            return _GM([_v7_block(cid, "Fresh")], calls, chat)

        orig_write_text = Path.write_text
        fired = []

        def failing_write(p, *a, **kw):
            if p == cat / "figures/medic__medic-new-1.json.tmp" and not fired:
                fired.append(str(p))
                raise OSError("E2E menu persona figure-save one-shot fault")
            return orig_write_text(p, *a, **kw)

        exc = None
        with patch.object(Path, "write_text", failing_write):
            try:
                _sess(paths, factory, driver, ["n", "neu", "medic", "x"], prints).run()
            except OSError as e:
                exc = e
        assert exc is not None and len(fired) == 1 and len(driver.invites) == 1 and len(calls) == 2

        before_human_ids = [e.chrononaut_id for e in catalog.list_for_participant(cat, "flo_human")]
        before_invites = len(driver.invites)
        before_gm_calls = len(calls)
        assert catalog.load_figure_save(cat, "medic", "medic-new-1") is None, "Testannahme: noch kein Save"

        # Frische TUI, NEUE Fortsetzen-Auswahl statt 'neu'+'medic'.
        _sess(paths, factory, driver, ["n", "fortsetzen:medic", "x"], prints).run()

        after_human_ids = [e.chrononaut_id for e in catalog.list_for_participant(cat, "flo_human")]
        after_persona_save = catalog.load_figure_save(cat, "medic", "medic-new-1")
        assert after_human_ids == before_human_ids, f"keine zusaetzliche Menschenfigur erwartet: {after_human_ids}"
        assert len(driver.invites) == before_invites, "keine zusaetzliche Einladungsentscheidung erwartet"
        assert len(calls) == before_gm_calls, "kein neuer SL-Turn erwartet (reiner Katalog-Nachtrag)"
        assert after_persona_save is not None, "Persona-Save haette nachgetragen werden muessen"
        assert catalog.active_chrononaut_id(cat, "medic") == "medic-new-1"


def test_e2e_c_independent_second_invite_reject_preserves_older_pending_creation():
    """E2E-C-Grenzfall (R-E2E-2 SOLLTE-1, 2026-10-02, 02_B1B2_NACHZUG.md §C,
    adaptiert aus `critic/evidence/critic_probe_independent_invite_reject_
    preserves_pending.py`): eine AELTERE, bereits angenommene, aber nach
    einem Figursave-I/O-Fehler noch unpersistierte Zusatzfigur-Erschaffung
    von `medic` darf NICHT durch eine SPAETERE, UNABHAENGIGE zweite
    Einladung an DIESELBE Persona beschaedigt/ueberschrieben werden, wenn
    diese zweite Einladung abgelehnt wird. Die zweite Einladung muss echt
    neu entschieden werden (kein Consent-Autofill der alten Zusage), und
    ihre Ablehnung darf den aelteren, noch offenen Vorgang weder loeschen
    noch veraendern -- er bleibt ueber 'fortsetzen:' spaeter unveraendert
    fertigstellbar (Schutz vor einem automatischen, stillen
    'Reject raeumt alles auf'-Verhalten)."""
    with tempfile.TemporaryDirectory() as td:
        paths = _setup(Path(td))
        states, run, onb, cat = paths
        calls, prints = [], []
        human_no = [0]
        driver = _Driver(["accept", "reject"])

        def factory(chat):
            if "__additional_gen" in chat:
                cid = "medic-new-1"
            else:
                human_no[0] += 1
                cid = f"human-new-{human_no[0]}"
            return _GM([_v7_block(cid, "Fresh")], calls, chat)

        orig_write_text = Path.write_text
        fired = []

        def failing_write(p, *a, **kw):
            if p == cat / "figures/medic__medic-new-1.json.tmp" and not fired:
                fired.append(str(p))
                raise OSError("E2E-2 one-shot persona figure-save fault")
            return orig_write_text(p, *a, **kw)

        # Session 1: accept + fault -> older pending creation exists
        # (registered, not yet saved, dialog already completed).
        exc1 = None
        with patch.object(Path, "write_text", failing_write):
            try:
                _sess(paths, factory, driver, ["n", "neu", "medic", "x"], prints).run()
            except OSError as e:
                exc1 = e
        assert exc1 is not None and len(fired) == 1

        pending_before = find_resumable_additional_creation(onb)
        assert len(pending_before) == 1 and pending_before[0]["persona_key"] == "medic"
        gen_before = pending_before[0]["generation"]
        final_save_before = onboarding.peek(onb, _additional_onboarding_key("medic", gen_before)).final_save
        medic_ids_before = [e.chrononaut_id for e in catalog.list_for_participant(cat, "medic")]
        human_ids_before = [e.chrononaut_id for e in catalog.list_for_participant(cat, "flo_human")]
        invites_before = len(driver.invites)
        calls_before = len(calls)
        assert catalog.load_figure_save(cat, "medic", "medic-new-1") is None

        # Session 2: a SECOND, INDEPENDENT force_new human figure re-invites
        # medic; medic REJECTS this unrelated new offer (no fault active).
        _sess(paths, factory, driver, ["n", "neu", "medic", "x"], prints).run()

        pending_after = find_resumable_additional_creation(onb)
        assert len(pending_after) == 1 and pending_after[0]["persona_key"] == "medic"
        gen_after = pending_after[0]["generation"]
        final_save_after = onboarding.peek(onb, _additional_onboarding_key("medic", gen_after)).final_save
        medic_ids_after = [e.chrononaut_id for e in catalog.list_for_participant(cat, "medic")]
        human_ids_after = [e.chrononaut_id for e in catalog.list_for_participant(cat, "flo_human")]

        assert gen_after == gen_before, "die aeltere, offene Generation darf sich nicht veraendern"
        assert final_save_after == final_save_before, "die bereits erhaltenen Savebytes duerfen unveraendert bleiben"
        assert medic_ids_after == medic_ids_before, "keine Katalogaenderung durch die Ablehnung"
        assert catalog.load_figure_save(cat, "medic", "medic-new-1") is None, (
            "Ablehnung der NEUEN Einladung darf den aelteren Vorgang NICHT fuellen/abschliessen"
        )
        assert len(driver.invites) == invites_before + 1, "die zweite Einladung muss echt neu entschieden werden"
        assert len(calls) == calls_before + 1, "genau EIN neuer SL-Turn (nur human-new-2), kein neuer medic-Turn"
        assert len(human_ids_after) == len(human_ids_before) + 1, "die zweite, unabhaengige Menschenfigur entsteht bewusst"

        # Session 3: the older pending creation must still be resumable
        # afterwards via the real 'fortsetzen:' menu path, unharmed.
        _sess(paths, factory, driver, ["n", "fortsetzen:medic", "x"], prints).run()
        medic_save_final = catalog.load_figure_save(cat, "medic", "medic-new-1")
        assert medic_save_final == final_save_before, "Fortsetzen muss dieselben, aelteren Savebytes liefern"
        assert catalog.active_chrononaut_id(cat, "medic") == "medic-new-1"


def test_e2e_human_b1_catalog_register_io_fault_resumes_same_attempt():
    """Twice-deferred Critic-Auflage (R0 §7, R1 §8.4): Human-B1-Katalog-I/O
    -- ein echter `OSError` bei `catalog.register` (VOR jedem Figursave)
    darf beim naechsten Menue-Reentry (`n -> neu`) KEINEN zweiten SL-Turn
    ausloesen; derselbe Vorgang wird fertiggestellt."""
    with tempfile.TemporaryDirectory() as td:
        paths = _setup(Path(td))
        states, run, onb, cat = paths
        prints = []
        turns = []
        seq = [0]

        class _SeqGM:
            def turn(self, idx, text, output_limit_tokens=None):
                seq[0] += 1
                cid = f"human-r2-new-{seq[0]}"
                turns.append({"idx": idx, "id": cid})
                return {"content": _v7_block(cid, "Fresh"), "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "e2e-r2"}

        factory = lambda chat: _SeqGM()
        orig_write_text = Path.write_text
        faults = []

        def selective_write(path, *a, **kw):
            target = cat / "catalog__flo_human.json.tmp"
            if path == target and not faults:
                faults.append(str(path))
                raise OSError("E2E_R2 one-shot real catalog register I/O boundary")
            return orig_write_text(path, *a, **kw)

        exc = None
        with patch.object(Path, "write_text", selective_write):
            try:
                _sess(paths, factory, _Driver(["reject"]), ["n", "neu", "", "x"], prints).run()
            except OSError as e:
                exc = e
        assert exc is not None and len(faults) == 1 and len(turns) == 1

        _sess(paths, factory, _Driver(["reject"]), ["n", "neu", "", "x"], prints).run()
        ids = [e.chrononaut_id for e in catalog.list_for_participant(cat, "flo_human")]
        first_save = catalog.load_figure_save(cat, "flo_human", "human-r2-new-1")
        assert len(turns) == 1, f"kein zweiter SL-Turn erwartet: {turns}"
        assert first_save is not None, "Figur haette fertiggestellt werden muessen"
        assert "human-r2-new-2" not in ids, f"keine zweite Figur erwartet: {ids}"


def test_e2e_human_b1_catalog_figure_save_io_fault_resumes_same_attempt():
    """Twice-deferred Critic-Auflage (Variante): echter `OSError` bei
    `catalog.store_figure_save` (NACH bereits erfolgreichem `register`) --
    derselbe Reentry-Vertrag gilt fuer die zweite Schreibstelle."""
    with tempfile.TemporaryDirectory() as td:
        paths = _setup(Path(td))
        states, run, onb, cat = paths
        prints = []
        turns = []
        seq = [0]

        class _SeqGM:
            def turn(self, idx, text, output_limit_tokens=None):
                seq[0] += 1
                cid = f"human-r2-new-{seq[0]}"
                turns.append({"idx": idx, "id": cid})
                return {"content": _v7_block(cid, "Fresh"), "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "e2e-r2"}

        factory = lambda chat: _SeqGM()
        orig_write_text = Path.write_text
        faults = []

        def selective_write(path, *a, **kw):
            target = cat / "figures/flo_human__human-r2-new-1.json.tmp"
            if path == target and not faults:
                faults.append(str(path))
                raise OSError("E2E_R2 one-shot real catalog figure-save I/O boundary")
            return orig_write_text(path, *a, **kw)

        exc = None
        with patch.object(Path, "write_text", selective_write):
            try:
                _sess(paths, factory, _Driver(["reject"]), ["n", "neu", "", "x"], prints).run()
            except OSError as e:
                exc = e
        assert exc is not None and len(faults) == 1 and len(turns) == 1

        _sess(paths, factory, _Driver(["reject"]), ["n", "neu", "", "x"], prints).run()
        ids = [e.chrononaut_id for e in catalog.list_for_participant(cat, "flo_human")]
        first_save = catalog.load_figure_save(cat, "flo_human", "human-r2-new-1")
        assert len(turns) == 1, f"kein zweiter SL-Turn erwartet: {turns}"
        assert first_save is not None, "Figursave haette nachgetragen werden muessen"
        assert "human-r2-new-2" not in ids, f"keine zweite Figur erwartet: {ids}"


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
