#!/usr/bin/env python3
"""
tests/mmo_sim/test_auftragsbindung_own_registration_ownership_2026_10_02.py --
Restnachzug "Auftragsbindung" (End-Critic-Verdikt
BLOCKED_SCOPED_WITH_CONFIRMED_E2E_FIXES, 2026-10-02,
`02_RESTNACHZUG_AUFTRAGSBINDUNG.md` §2-§3): eine bereits existierende EIGENE
Figurenregistrierung wird NICHT automatisch dem aktuellen Erschaffungsauftrag
zugerechnet, nur weil derselbe Teilnehmer, gleiche Savebytes oder ein
fehlendes Archiv vorliegen -- nur eine NACHWEISBAR demselben offenen Auftrag
gehoerige Teilregistrierung (`onboarding.attempt_claim_matches`, s.
`mmo_sim/domain/zeitriss/onboarding.py:record_attempt_claim`/
`attempt_claim_matches`) darf idempotent fertiggestellt werden.

  O1-H -- Mensch: ein bewusst NEUER Erschaffungsauftrag (neue, eigene
    Generation) liefert zufaellig exakt ID/Bytes einer bereits VOLLSTAENDIG
    abgeschlossenen (resolvten) eigenen Figur -> HOLD, keine falsche
    Fertigstellung.
  O1-P -- Persona: dieselbe Grenze am Zusatzfigur-Pfad
    (`advance_additional_persona_creation`/`_publication_reconcile_
    additional`).
  O2-H -- Mensch: FEHLENDES eigenes Archiv (Katalogeintrag bleibt, nur die
    Figursave-Datei fehlt) darf den Schutz des real fortgeschrittenen
    Current NICHT umgehen -> HOLD, Current/Wallet/Inventar bleiben erhalten.
  Positivkontrollen (C, "kein Scheinfix"):
    - eine wirklich NEUE, eindeutige ID funktioniert weiterhin normal
      (Mensch UND Persona).
    - ein echter eigener Teilabschluss nach einem Register-/Figursave-I/O-
      Fehler bleibt idempotent fertigstellbar, OHNE zweiten Modellturn
      (Mensch UND Persona) -- der Claim wurde bereits VOR dem Fehler
      geschrieben.
    - der Auftragsbindungs-Claim wird NICHT vorzeitig (vor echter
      Katalogpersistenz) als abgeschlossen behandelt, UND eine fremde/
      andere Generation kann einen bestehenden Claim nicht fuer sich
      beanspruchen ("stehlen").

Alle Tests nutzen den ECHTEN `TuiSession.run()`-Menue-/Dispatchweg bzw. die
echte `advance_additional_persona_creation`-Domainfunktion (keine
Verkuerzung auf private Helfer). Pure Python, nur `assert`, echter
Exitcode."""
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
from mmo_sim.domain.zeitriss.community_creation import advance_additional_persona_creation  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
_HUMAN_FRESH_ATTEMPT_KEY = "human-fresh-create::flo_human"


def _v7_block(char_id: str, name: str, **extra) -> str:
    body = {"v": 7, "characters": [{"char_id": char_id, "name": name, "callsign": name.upper(), "level": 1, **extra}]}
    return "```json\n" + json.dumps(body) + "\n```"


def _give_existing_figure(states_dir, run_dir, catalog_dir, onboarding_dir, participant_id, char_id, name):
    ps_store = PersonaStateStore(schema_path=_SCHEMA)
    ps_store.save_state(participant_id, {
        "v": 2, "persona_key": participant_id, "real_name": name,
        "archetype": "AUFTRAGSBINDUNG", "play_style": "AUFTRAGSBINDUNG", "charwunsch": "AUFTRAGSBINDUNG",
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

    def decide(self, ctx):
        dc = ctx.get("decision_contract")
        if dc:
            decision = self.decisions[len(self.invites)]
            self.invites.append(copy.deepcopy(ctx))
            return ParticipantDecision(text=json.dumps(dict(dc, decision=decision)), origin_source="AB_TEST", meta={"usage": {}})
        return ParticipantDecision(text="Bereit.", origin_source="AB_TEST", meta={"usage": {}})


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


def test_ab_o1_h_new_attempt_with_existing_own_id_holds_not_as_new_figure():
    """O1-H: gen2 erschafft (echter Menueweg) human-new-1 vollstaendig,
    resolviert. Ein bewusst NEUER Auftrag (gen3) liefert faelschlich exakt
    dieselbe ID/Bytes -- muss HOLD sein, NICHT als neue Figur verbucht."""
    with tempfile.TemporaryDirectory() as td:
        paths = _setup(Path(td))
        states, run, onb, cat = paths
        calls, prints = [], []
        driver = _Driver(["reject"])

        factory1 = lambda chat: _GM([_v7_block("human-new-1", "Fresh")], calls, chat)
        _sess(paths, factory1, driver, ["n", "neu", "", "x"], prints).run()

        own_save = copy.deepcopy(catalog.load_figure_save(cat, "flo_human", "human-new-1"))
        assert own_save == _current(paths, "flo_human")
        ids_before = [e.chrononaut_id for e in catalog.list_for_participant(cat, "flo_human")]
        current_before = _current(paths, "flo_human")
        gen_before = json.loads((onb / f"attempt__{_HUMAN_FRESH_ATTEMPT_KEY}.json").read_text())
        assert gen_before["resolved"] is True

        oldlen = len(prints)
        factory2 = lambda chat: _GM(["```json\n" + json.dumps(own_save) + "\n```"], calls, chat)
        _sess(paths, factory2, driver, ["n", "neu", "", "x"], prints).run()

        ids_after = [e.chrononaut_id for e in catalog.list_for_participant(cat, "flo_human")]
        current_after = _current(paths, "flo_human")
        gen_after = json.loads((onb / f"attempt__{_HUMAN_FRESH_ATTEMPT_KEY}.json").read_text())

        assert ids_after == ids_before, f"keine neue Figur erwartet: {ids_after}"
        assert current_after == current_before, "Current darf unveraendert bleiben"
        assert gen_after["generation"] > gen_before["generation"], "Testannahme: neue Generation wurde gebunden"
        assert gen_after["resolved"] is False, "die NEUE Generation darf NICHT faelschlich resolved werden"
        assert any("angehalten" in s for s in prints[oldlen:]), "sichtbares HOLD erwartet"
        assert not any("tischbereit" in s for s in prints[oldlen:]), "kein falscher Erfolg erwartet"


def test_ab_o1_p_new_attempt_with_existing_own_id_holds_not_as_new_figure():
    """O1-P: medic erschafft (echte Domainfunktion) medic-new-1 vollstaendig,
    resolviert. Eine bewusst NEUE Generation liefert faelschlich exakt
    dieselbe ID/Bytes -- muss HOLD sein."""
    with tempfile.TemporaryDirectory() as td:
        paths = _setup(Path(td))
        states, run, onb, cat = paths

        gm1 = _GM([_v7_block("medic-new-1", "Fresh")], [], "gen2")
        outcome1 = advance_additional_persona_creation(
            run_dir=run, states_dir=states, schema_path=_SCHEMA, onboarding_dir=onb, catalog_dir=cat,
            community_id="community-flo_human", generation=2, persona_key="medic",
            gm_transport_factory=lambda *a, **k: gm1, persona_driver_factory=lambda p: _Driver(["accept"]),
        )
        assert outcome1.status == "completed" and outcome1.chrononaut_id == "medic-new-1"
        own_save = copy.deepcopy(catalog.load_figure_save(cat, "medic", "medic-new-1"))
        ids_before = [e.chrononaut_id for e in catalog.list_for_participant(cat, "medic")]
        current_before = _current(paths, "medic")

        gm2 = _GM(["```json\n" + json.dumps(own_save) + "\n```"], [], "gen3")
        outcome2 = advance_additional_persona_creation(
            run_dir=run, states_dir=states, schema_path=_SCHEMA, onboarding_dir=onb, catalog_dir=cat,
            community_id="community-flo_human", generation=3, persona_key="medic",
            gm_transport_factory=lambda *a, **k: gm2, persona_driver_factory=lambda p: _Driver(["accept"]),
        )

        ids_after = [e.chrononaut_id for e in catalog.list_for_participant(cat, "medic")]
        current_after = _current(paths, "medic")
        assert outcome2.status == "blocked", f"erwartetes HOLD, erhalten: {outcome2}"
        assert ids_after == ids_before, f"keine neue Figur erwartet: {ids_after}"
        assert current_after == current_before, "Current darf unveraendert bleiben"
        assert gm2.calls == [{"chat": "gen3", "idx": 0, "text": gm2.calls[0]["text"]}] or len(gm2.calls) == 1, (
            "genau EIN echter SL-Turn fuer die neue Generation, kein zweiter wegen des HOLD"
        )


def test_ab_o2_h_missing_archive_does_not_authorize_current_reset():
    """O2-H: human-new-1 vollstaendig erschaffen, Current ueber die echte
    Publikationsschnittstelle auf einen fortgeschrittenen Stand gebracht.
    NUR die synthetische Figursave-Datei wird entfernt (Katalogeintrag
    bleibt bestehen) -- ein neuer Auftrag mit alter ID/altem Inhalt darf
    den fortgeschrittenen Current NICHT zuruecksetzen."""
    with tempfile.TemporaryDirectory() as td:
        paths = _setup(Path(td))
        states, run, onb, cat = paths
        calls, prints = [], []
        driver = _Driver(["reject"])

        factory1 = lambda chat: _GM([_v7_block("human-new-1", "Fresh")], calls, chat)
        _sess(paths, factory1, driver, ["n", "neu", "", "x"], prints).run()

        archived = copy.deepcopy(catalog.load_figure_save(cat, "flo_human", "human-new-1"))
        progressed = copy.deepcopy(_current(paths, "flo_human"))
        progressed["characters"][0].update(level=4, wallet={"credits": 86420}, inventory=["KEEP_CURRENT_WITHOUT_ARCHIVE"])
        core_store.publish_current_save(run, "flo_human", progressed, PersonaStateStore(schema_path=_SCHEMA), states)

        figure_file = cat / "figures" / "flo_human__human-new-1.json"
        assert figure_file.is_file()
        figure_file.unlink()
        assert catalog.load_figure_save(cat, "flo_human", "human-new-1") is None
        assert _current(paths, "flo_human") == progressed

        oldlen = len(prints)
        factory2 = lambda chat: _GM(["```json\n" + json.dumps(archived) + "\n```"], calls, chat)
        _sess(paths, factory2, driver, ["n", "neu", "", "x"], prints).run()

        after_current = _current(paths, "flo_human")
        after_archive = catalog.load_figure_save(cat, "flo_human", "human-new-1")
        assert after_current == progressed, "Current (L4/Wallet/Inventar) muss erhalten bleiben"
        assert after_archive is None, "KEINE Neuregistrierungsberechtigung aus dem fehlenden Archiv"
        assert any("angehalten" in s for s in prints[oldlen:]), "sichtbares HOLD erwartet"


def test_ab_o2_p_missing_archive_does_not_authorize_current_reset():
    """O2-P (AB-2 MUSS-1, 2026-10-02, adaptiert aus `critic/evidence/
    critic_probe_missing_archive_persona.py`): dieselbe Grenze wie O2-H, am
    Persona-Zusatzfigur-Pfad. `medic` erschafft medic-new-1 vollstaendig
    (echte `advance_additional_persona_creation`), Current ueber die echte
    Publikationsschnittstelle auf einen fortgeschrittenen Stand gebracht.
    NUR die synthetische Figursave-Datei wird entfernt (Katalogeintrag
    bleibt bestehen) -- ein neuer, eigenstaendiger Zusatzfigur-Auftrag mit
    alter ID/altem Inhalt darf den fortgeschrittenen Current NICHT
    zuruecksetzen. 02 §3 verlangt diese Pruefung ausdruecklich auch fuer
    die Persona-Seite (nicht nur O2-H blind als Nachweis zaehlen)."""
    with tempfile.TemporaryDirectory() as td:
        paths = _setup(Path(td))
        states, run, onb, cat = paths

        gm1 = _GM([_v7_block("medic-new-1", "Fresh")], [], "gen2")
        outcome1 = advance_additional_persona_creation(
            run_dir=run, states_dir=states, schema_path=_SCHEMA, onboarding_dir=onb, catalog_dir=cat,
            community_id="community-flo_human", generation=2, persona_key="medic",
            gm_transport_factory=lambda *a, **k: gm1, persona_driver_factory=lambda p: _Driver(["accept"]),
        )
        assert outcome1.status == "completed" and outcome1.chrononaut_id == "medic-new-1"

        archived = copy.deepcopy(catalog.load_figure_save(cat, "medic", "medic-new-1"))
        progressed = copy.deepcopy(_current(paths, "medic"))
        progressed["characters"][0].update(level=4, wallet={"credits": 86420}, inventory=["KEEP_CURRENT_WITHOUT_ARCHIVE_PERSONA"])
        core_store.publish_current_save(run, "medic", progressed, PersonaStateStore(schema_path=_SCHEMA), states)

        figure_file = cat / "figures" / "medic__medic-new-1.json"
        assert figure_file.is_file()
        figure_file.unlink()
        assert catalog.load_figure_save(cat, "medic", "medic-new-1") is None
        assert _current(paths, "medic") == progressed
        ids_before = [e.chrononaut_id for e in catalog.list_for_participant(cat, "medic")]

        gm2 = _GM(["```json\n" + json.dumps(archived) + "\n```"], [], "gen3")
        outcome2 = advance_additional_persona_creation(
            run_dir=run, states_dir=states, schema_path=_SCHEMA, onboarding_dir=onb, catalog_dir=cat,
            community_id="community-flo_human", generation=3, persona_key="medic",
            gm_transport_factory=lambda *a, **k: gm2, persona_driver_factory=lambda p: _Driver(["accept"]),
        )

        after_current = _current(paths, "medic")
        after_archive = catalog.load_figure_save(cat, "medic", "medic-new-1")
        ids_after = [e.chrononaut_id for e in catalog.list_for_participant(cat, "medic")]
        assert outcome2.status == "blocked", f"erwartetes HOLD, erhalten: {outcome2}"
        assert after_current == progressed, "Current (L4/Wallet/Inventar) muss erhalten bleiben"
        assert after_archive is None, "KEINE Neuregistrierungsberechtigung aus dem fehlenden Archiv"
        assert ids_after == ids_before, f"keine neue Figur erwartet: {ids_after}"
        assert len(gm2.calls) == 1, "genau EIN echter SL-Turn fuer die neue Generation, kein zweiter wegen des HOLD"


def test_ab_positive_genuinely_new_id_still_works_human_and_persona():
    """Positivkontrolle: eine wirklich NEUE, noch nie verwendete ID
    funktioniert weiterhin normal -- fuer Mensch UND Persona (kein
    pauschales HOLD aller bestehenden IDs)."""
    with tempfile.TemporaryDirectory() as td:
        paths = _setup(Path(td))
        states, run, onb, cat = paths
        calls, prints = [], []
        driver = _Driver(["accept"])

        factory = lambda chat: _GM(
            [_v7_block("medic-new-1", "Fresh") if "__additional_gen" in chat else _v7_block("human-new-1", "Fresh")],
            calls, chat,
        )
        _sess(paths, factory, driver, ["n", "neu", "medic", "x"], prints).run()
        assert "human-new-1" in [e.chrononaut_id for e in catalog.list_for_participant(cat, "flo_human")]
        assert "medic-new-1" in [e.chrononaut_id for e in catalog.list_for_participant(cat, "medic")]
        assert not any("angehalten" in s for s in prints), "keine HOLD-Meldung fuer echte neue IDs erwartet"
        assert _current(paths, "flo_human")["characters"][0]["char_id"] == "human-new-1"
        assert _current(paths, "medic")["characters"][0]["char_id"] == "medic-new-1"


def test_ab_positive_partial_resume_completes_without_second_model_turn():
    """Positivkontrolle (C), MENSCHEN-Pfad: ein echter eigener Teilabschluss
    nach einem Register-/Figursave-I/O-Fehler bleibt idempotent
    fertigstellbar, OHNE zweiten Modellturn. Der Auftragsbindungs-Claim
    wurde bereits VOR dem Fehler geschrieben (s. `record_attempt_claim`
    direkt vor dem ersten ueberschreibenden Write). Die PERSONA-Variante
    derselben Garantie steht separat in
    `test_ab_positive_persona_partial_resume_completes_without_second_model_turn`
    (AB-2 SOLLTE-2, 2026-10-02 -- diese Funktion deckt bewusst NUR den
    Menschen-Pfad ab, die vorherige Docstring-Formulierung "fuer Mensch UND
    Persona" war an dieser Stelle unzutreffend und wurde korrigiert)."""
    with tempfile.TemporaryDirectory() as td:
        paths = _setup(Path(td))
        states, run, onb, cat = paths
        calls, prints = [], []
        driver = _Driver(["reject"])

        orig_write_text = Path.write_text
        fired = []

        def failing_write(p, *a, **kw):
            if p == cat / "catalog__flo_human.json.tmp" and not fired:
                fired.append(str(p))
                raise OSError("AB one-shot human catalog register fault")
            return orig_write_text(p, *a, **kw)

        factory = lambda chat: _GM([_v7_block("human-new-1", "Fresh")], calls, chat)
        exc = None
        with patch.object(Path, "write_text", failing_write):
            try:
                _sess(paths, factory, driver, ["n", "neu", "", "x"], prints).run()
            except OSError as e:
                exc = e
        assert exc is not None and len(fired) == 1

        # Claim must already be durably recorded for gen2/human-new-1 even
        # though the register write itself failed right after.
        claim_path = onb / f"attempt-claim__{_HUMAN_FRESH_ATTEMPT_KEY}.json"
        assert claim_path.is_file(), "Claim haette bereits VOR dem fehlgeschlagenen Write geschrieben sein muessen"
        claim = json.loads(claim_path.read_text())
        assert claim["char_id"] == "human-new-1" and claim["generation"] == 2

        _sess(paths, factory, driver, ["n", "neu", "", "x"], prints).run()
        ids = [e.chrononaut_id for e in catalog.list_for_participant(cat, "flo_human")]
        assert ids == ["human-old", "human-new-1"], f"genau eine Figur erwartet, kein Duplikat: {ids}"
        assert len(calls) == 1, "kein zweiter Modellturn fuer den legitimen Resume erwartet"
        assert catalog.load_figure_save(cat, "flo_human", "human-new-1") is not None


def test_ab_positive_persona_partial_resume_completes_without_second_model_turn():
    """Positivkontrolle (C), PERSONA-Pfad (AB-2 SOLLTE-2, 2026-10-02,
    adaptiert aus `critic/evidence/critic_probe_persona_partial_resume.py`):
    dieselbe Idempotenz-Garantie wie der Menschen-Pfad oben, hier ueber die
    echte `advance_additional_persona_creation`-Domainfunktion. Ein echter
    `OSError` bei `catalog.register` (fuer `medic`s Zusatzfigur) wird
    abgefangen; der Auftragsbindungs-Claim ist bereits VOR dem Fehler
    durabel geschrieben. Ein Reentry MIT DERSELBEN Generation muss
    fertigstellen, OHNE einen zweiten echten SL-Turn (gemeinsam gezaehlte
    `calls`-Liste ueber beide Versuche hinweg), ohne Duplikat."""
    with tempfile.TemporaryDirectory() as td:
        paths = _setup(Path(td))
        states, run, onb, cat = paths
        calls = []

        orig_write_text = Path.write_text
        fired = []

        def failing_write(p, *a, **kw):
            if p == cat / "catalog__medic.json.tmp" and not fired:
                fired.append(str(p))
                raise OSError("AB-2 one-shot persona catalog register fault")
            return orig_write_text(p, *a, **kw)

        factory1 = lambda chat: _GM([_v7_block("medic-new-1", "Fresh")], calls, chat)
        exc = None
        with patch.object(Path, "write_text", failing_write):
            try:
                advance_additional_persona_creation(
                    run_dir=run, states_dir=states, schema_path=_SCHEMA, onboarding_dir=onb, catalog_dir=cat,
                    community_id="community-flo_human", generation=2, persona_key="medic",
                    gm_transport_factory=factory1, persona_driver_factory=lambda p: _Driver(["accept"]),
                )
            except OSError as e:
                exc = e
        assert exc is not None and len(fired) == 1

        claim_path = onb / "attempt-claim__medic__additional_pending.json"
        assert claim_path.is_file(), "Claim haette bereits VOR dem fehlgeschlagenen Write geschrieben sein muessen"
        claim = json.loads(claim_path.read_text())
        assert claim["char_id"] == "medic-new-1" and claim["generation"] == 2
        assert catalog.load_figure_save(cat, "medic", "medic-new-1") is None, "Testannahme: Register scheiterte, nichts registriert"

        # Reentry: DIESELBE Generation=2, kein Fault mehr -- factory2 teilt
        # dieselbe `calls`-Liste, ein zweiter echter SL-Turn wuerde sie auf 2
        # wachsen lassen.
        factory2 = lambda chat: _GM([_v7_block("medic-new-1", "Fresh")], calls, chat)
        outcome2 = advance_additional_persona_creation(
            run_dir=run, states_dir=states, schema_path=_SCHEMA, onboarding_dir=onb, catalog_dir=cat,
            community_id="community-flo_human", generation=2, persona_key="medic",
            gm_transport_factory=factory2, persona_driver_factory=lambda p: _Driver(["accept"]),
        )

        ids = [e.chrononaut_id for e in catalog.list_for_participant(cat, "medic")]
        assert outcome2.status in ("completed", "already_ready") and outcome2.chrononaut_id == "medic-new-1", outcome2
        assert ids == ["medic-old", "medic-new-1"], f"genau eine Zusatzfigur erwartet, kein Duplikat: {ids}"
        assert len(calls) == 1, "kein zweiter Modellturn fuer den legitimen Resume erwartet"
        assert catalog.load_figure_save(cat, "medic", "medic-new-1") is not None


def test_ab_positive_claim_not_resolved_too_early_nor_stolen_by_other_attempt():
    """Positivkontrolle (C): der Claim wird NICHT vorzeitig (vor echter
    Katalogpersistenz) resolved, UND eine ANDERE Generation kann einen
    bestehenden Claim nicht fuer sich beanspruchen. Direkter Primitiven-Test
    gegen `onboarding.record_attempt_claim`/`attempt_claim_matches`/
    `bind_attempt`/`resolve_attempt` (dieselbe Mechanik wie in tui.py/
    community_creation.py verdrahtet)."""
    with tempfile.TemporaryDirectory() as td:
        onb = Path(td) / "onboarding"
        key = "probe-claim-key"

        # Erster Claim fuer generation=2, char_id="A".
        onboarding.record_attempt_claim(onb, key, generation=2, char_id="A")
        assert onboarding.attempt_claim_matches(onb, key, generation=2, char_id="A") is True
        # Dieselbe generation, ABWEICHENDE char_id -> kein Match (Diebstahlschutz).
        assert onboarding.attempt_claim_matches(onb, key, generation=2, char_id="B") is False
        # ABWEICHENDE generation, dieselbe char_id -> kein Match (eine SPAETERE,
        # neue Generation darf den ALTEN Claim nicht einfach fuer sich beanspruchen).
        assert onboarding.attempt_claim_matches(onb, key, generation=3, char_id="A") is False
        # Komplett unbekannter Schluessel -> kein Match (kein Claim vorhanden).
        assert onboarding.attempt_claim_matches(onb, key, generation=2, char_id="C") is False

        # bind_attempt (separates Ledger, s. record_attempt_claim-Docstring:
        # GETRENNTE Datei) markiert generation=2 als resolved -- eine NEUE
        # Generation wird gemintet.
        bound = onboarding.bind_attempt(onb, key, seed_generation=2)
        assert bound == 2
        onboarding.resolve_attempt(onb, key, 2)
        bound2 = onboarding.bind_attempt(onb, key, seed_generation=3)
        assert bound2 == 3, "neue Generation nach resolved=True erwartet"
        # Der ALTE Claim (generation=2, "A") gilt fuer die NEUE Generation
        # NICHT als Match -- auch nicht fuer dieselbe char_id "A". Genau das
        # verhindert O1/O2: eine neue, unabhaengige Generation kann einen
        # bestehenden fremden ODER eigenen Claim nicht fuer sich beanspruchen
        # ("stehlen"), nur weil sie zufaellig dieselbe ID produziert.
        assert onboarding.attempt_claim_matches(onb, key, generation=bound2, char_id="A") is False
        # Fuer die NEUE Generation mit einer ANDEREN, echten neuen ID klappt
        # record_attempt_claim normal (keine Blockade fuer legitime neue
        # Ziele) -- DIES ist der reale Ablauf in tui.py/community_creation.py:
        # `record_attempt_claim` wird NUR nach einem bestandenen Match-Check
        # (oder fuer eine brandneue ID ohne vorhandene Registrierung)
        # aufgerufen, NIE fuer eine Kollisions-ID wie "A" unter generation=3
        # (die haette HOLD ausgeloest, s. O1-H/O1-P oben) -- der einzelne,
        # stets aktuelle Claim-Datensatz pro Schluessel ist dafuer bewusst
        # ausreichend (keine Historie noetig, da Katalog/Figursave bereits
        # die dauerhafte Wahrheit tragen; der Claim dient NUR der kurzen
        # "gehoert zu GENAU dieser Generation"-Entscheidung im jeweiligen
        # Moment).
        onboarding.record_attempt_claim(onb, key, generation=bound2, char_id="D")
        assert onboarding.attempt_claim_matches(onb, key, generation=bound2, char_id="D") is True


def _cc1_fault(onb, cat, key, actor, cid):
    """CC-1 (02_CLAIM_CURRENT_NACHZUG.md): dieselbe einmalige synthetische
    Fehlerinjektion wie in der gebundenen End-Critic-Evidenz
    (`general_claim_current_authority.py`) -- fuer den Menschen auf dem
    `resolve_attempt`-Write (markiert die Generation als `resolved`), fuer
    die Persona auf dem abschliessenden Katalogzeiger-Write
    (`bind_for_section`). Beide hinterlassen einen bereits erfolgreich
    registrierten/gespeicherten eigenen Claim, dessen Current-Publikation
    beim naechsten Resume erneut durchlaufen wird."""
    orig = Path.write_text
    fired: list[str] = []

    def fault(p, data, *a, **kw):
        if actor == "human":
            hit = p == onb / f"attempt__{key}.json.tmp" and json.loads(data).get("resolved") is True
        else:
            hit = p == cat / "catalog__medic.json.tmp" and json.loads(data).get("active_chrononaut_id") == cid
        if hit and not fired:
            fired.append(str(p))
            raise OSError("CC-1 synthetic one-shot " + actor + " completion fault")
        return orig(p, data, *a, **kw)

    return fault, fired


def _cc1_case(actor: str, progress: bool) -> dict:
    """CC-1 (02_CLAIM_CURRENT_NACHZUG.md): ein passender eigener, bereits
    geclaimter (`onboarding.attempt_claim_matches`) Erschaffungsauftrag fuer
    `char_id` DARF beim Resume nicht den inzwischen real fortgeschrittenen
    Current derselben Figur (publiziert ueber die echte `core.store.
    publish_current_save`-Autoritaet, UNABHAENGIG von diesem Auftrag) durch
    den alten Erstsave ersetzen -- weder fuer den Menschen
    (`ui/tui.py:_finish_new_character_creation`) noch fuer die Persona
    (`domain/zeitriss/community_creation.py:_publication_reconcile_
    additional`, erreicht ueber die echte Gate-B-Einladung innerhalb der
    menschlichen `neu`-Erschaffung). `progress=True` prueft den Schutz
    (fail-closed HOLD), `progress=False` die Positivkontrolle (echter
    idempotenter Teilabschluss bleibt normal fertigstellbar)."""
    with tempfile.TemporaryDirectory() as td:
        paths = _setup(Path(td))
        states, run, onb, cat = paths
        calls: list = []
        prints: list = []
        driver = _Driver(["accept"])
        who = "flo_human" if actor == "human" else "medic"
        cid = "human-new-1" if actor == "human" else "medic-new-1"
        key = _HUMAN_FRESH_ATTEMPT_KEY if actor == "human" else "medic__additional_pending"

        factory = lambda chat: _GM(
            [_v7_block("medic-new-1" if "__additional_gen" in chat else "human-new-1", "Fresh")], calls, chat,
        )
        fault, fired = _cc1_fault(onb, cat, key, actor, cid)
        caught = None
        with patch.object(Path, "write_text", fault):
            try:
                _sess(paths, factory, driver, ["n", "neu", "" if actor == "human" else "medic", "x"], prints).run()
            except OSError as exc:
                caught = repr(exc)
        assert len(fired) == 1, (actor, fired, caught)

        pending_path = onb / f"attempt__{key}.json"
        pending_before = json.loads(pending_path.read_text())
        assert pending_before["resolved"] is False

        initial = copy.deepcopy(catalog.load_figure_save(cat, who, cid))
        assert initial is not None, "Testannahme: Register/Figursave liefen bereits vor dem injizierten Fehler durch"

        if actor == "human":
            # Bereits katalogisierte, aber INAKTIVE Figur -- ueber den
            # echten oeffentlichen Wechselweg aktiviert, KEIN zweiter
            # SL-Dialog.
            _sess(paths, factory, driver, ["n", cid, "x"], prints).run()
        assert _current(paths, who)["characters"][0]["char_id"] == cid

        before = copy.deepcopy(_current(paths, who))
        if progress:
            before["characters"][0].update(
                level=4, wallet={"credits": 87654}, inventory=["KEEP_PROGRESS_DURING_OPEN_ATTEMPT"],
            )
            # Dieselbe autoritative Store-Operation wie ein real erspielter,
            # von diesem offenen Auftrag UNABHAENGIGER spaeterer Abschnitt.
            core_store.publish_current_save(run, who, before, PersonaStateStore(schema_path=_SCHEMA), states)
        assert _current(paths, who) == before

        before_archive = copy.deepcopy(catalog.load_figure_save(cat, who, cid))
        before_binding = catalog.active_chrononaut_id(cat, who)
        before_ids = [e.chrononaut_id for e in catalog.list_for_participant(cat, who)]
        before_calls = len(calls)
        before_invites = len(driver.invites)

        answers = ["n", "neu", "", "x"] if actor == "human" else ["n", "fortsetzen:medic", "x"]
        _sess(paths, factory, driver, answers, prints).run()

        after = _current(paths, who)
        return {
            "cid": cid,
            "before": before, "after": after, "initial": initial,
            "before_archive": before_archive, "after_archive": catalog.load_figure_save(cat, who, cid),
            "before_binding": before_binding, "after_binding": catalog.active_chrononaut_id(cat, who),
            "before_ids": before_ids, "after_ids": [e.chrononaut_id for e in catalog.list_for_participant(cat, who)],
            "before_calls": before_calls, "after_calls": len(calls),
            "before_invites": before_invites, "after_invites": len(driver.invites),
            "pending_after": json.loads(pending_path.read_text()),
            "prints": prints,
        }


def test_cc1_h_progressed_current_protected_on_claim_resume():
    """CC-1-H: human-new-1 wird real aktiviert, dann (unabhaengig vom noch
    offenen Erstsave-Claim) auf Level 4 fortgeschritten. Der Resume
    desselben, claim-bestaetigten Auftrags darf diesen Fortschritt NICHT
    auf den Level-1-Erstsave zuruecksetzen -- fail-closed HOLD, kein
    zweiter Modellaufruf, kein zweiter Invite."""
    r = _cc1_case("human", True)
    assert r["after_calls"] == r["before_calls"], "kein zweiter Modellaufruf beim Resume erwartet"
    assert r["after_invites"] == r["before_invites"], "kein zweiter Einladungsaufruf beim Resume erwartet"
    assert r["after"] != r["initial"], "Testannahme: Erstsave (L1) und spaeterer Fortschritt (L4) sind verschieden"
    assert r["after"] == r["before"], "der spaeter erspielte Fortschritt darf NICHT auf den Erstsave zurueckfallen"
    assert r["after"]["characters"][0]["level"] == 4
    assert r["after"]["characters"][0]["wallet"] == {"credits": 87654}
    assert r["after"]["characters"][0]["inventory"] == ["KEEP_PROGRESS_DURING_OPEN_ATTEMPT"]
    assert r["after_binding"] == r["cid"]
    assert any("angehalten" in s for s in r["prints"]), "sichtbares HOLD erwartet, kein stilles Ueberschreiben"


def test_cc1_p_progressed_current_protected_on_claim_resume():
    """CC-1-P: dieselbe Garantie wie CC-1-H, am Persona-Zusatzfigur-Pfad
    (`_publication_reconcile_additional`, ueber die echte Gate-B-
    Einladung erreicht; der injizierte Fehler trifft den abschliessenden
    Katalogzeiger-Write, NICHT die Current-Publikation selbst)."""
    r = _cc1_case("persona", True)
    assert r["after_calls"] == r["before_calls"], "kein zweiter Modellaufruf beim Resume erwartet"
    assert r["after_invites"] == r["before_invites"], "kein zweiter Einladungsaufruf beim Resume erwartet"
    assert r["after"] != r["initial"], "Testannahme: Erstsave (L1) und spaeterer Fortschritt (L4) sind verschieden"
    assert r["after"] == r["before"], "der spaeter erspielte Fortschritt darf NICHT auf den Erstsave zurueckfallen"
    assert r["after"]["characters"][0]["level"] == 4
    assert r["after"]["characters"][0]["wallet"] == {"credits": 87654}
    assert r["after"]["characters"][0]["inventory"] == ["KEEP_PROGRESS_DURING_OPEN_ATTEMPT"]
    assert r["after_binding"] == r["cid"]
    assert any("blocked" in s or "angehalten" in s for s in r["prints"]), "sichtbares HOLD erwartet"


def test_cc1_h_unchanged_resume_still_completes_fully():
    """CC-1-H Positivkontrolle: OHNE spaeteren Fortschritt (Current ==
    Erstsave) bleibt der claim-bestaetigte Resume ein echter, vollstaendiger
    Abschluss -- kein maskiertes HOLD, Attempt resolved, Binding korrekt."""
    r = _cc1_case("human", False)
    assert r["after_calls"] == r["before_calls"]
    assert r["after"] == r["before"] == r["initial"]
    assert r["after_archive"] == r["initial"]
    assert r["pending_after"]["resolved"] is True
    assert r["before_ids"] == r["after_ids"]
    assert r["after_binding"] == r["cid"]
    assert not any("angehalten" in s for s in r["prints"]), "kein falsches HOLD fuer den unveraenderten Teilabschluss"


def test_cc1_p_unchanged_resume_still_completes_fully():
    """CC-1-P Positivkontrolle: dieselbe Garantie wie CC-1-H am Persona-
    Pfad."""
    r = _cc1_case("persona", False)
    assert r["after_calls"] == r["before_calls"]
    assert r["after"] == r["before"] == r["initial"]
    assert r["after_archive"] == r["initial"]
    assert r["pending_after"]["resolved"] is True
    assert r["before_ids"] == r["after_ids"]
    assert r["after_binding"] == r["cid"]


def test_cc1_h_archive_protected_through_switch_sync_and_second_resume():
    """G1 (REWORK-BRIEF.md, Nacharbeit 2026-10-03; End-Critic-Gap-Probe
    `critic_gap_probe_archive_staleness.py`): nicht nur der Current (CC-1),
    auch das EIGENE Figuren-Archiv (`catalog.store_figure_save`,
    `ui/tui.py:_finish_new_character_creation`) muss einen claim-
    bestaetigten Resume ueberleben. Ablauf (echter oeffentlicher TUI-Weg):
    (1) derselbe CC1-Fehlerinjektionspfad wie `_cc1_case` hinterlaesst einen
    erfolgreich registrierten/gespeicherten, aber NICHT resolvten Claim
    (`resolve_attempt`-Write schlaegt EINMALIG fehl); (2) die neue Figur
    wird ueber den echten Wechselweg aktiviert; (3) ein echter, von diesem
    Auftrag UNABHAENGIGER spaeterer Fortschritt (Level 4) wird ueber die
    Store-Autoritaet publiziert; (4) ein Wechsel WEG und wieder ZURUECK
    synchronisiert das Archiv ueber den bestehenden, unveraenderten
    `_sync_outgoing_active_figure`-Mechanismus auf Level 4 -- ERST HIER wird
    ein veraltetes Archiv-Ueberschreiben ueberhaupt sichtbar (ohne diesen
    Schritt bliebe das Archiv ohnehin auf Level 1 und ein erneuter Write
    desselben Level-1-Blocks waere nicht beobachtbar); (5) ein ZWEITER
    Resume DERSELBEN noch offenen/unresolvten Generation (reuse von
    `state.final_save`, KEIN neuer GM-Turn) darf das jetzt fortgeschrittene
    Archiv NICHT transient auf den alten Level-1-Erstsave zuruecksetzen --
    Current bleibt UNVERAENDERT geschuetzt (CC-1)."""
    with tempfile.TemporaryDirectory() as td:
        paths = _setup(Path(td))
        states, run, onb, cat = paths
        calls: list = []
        prints: list = []
        driver = _Driver(["accept"])
        who = "flo_human"
        cid = "human-new-1"
        key = _HUMAN_FRESH_ATTEMPT_KEY

        factory = lambda chat: _GM([_v7_block(cid, "Fresh")], calls, chat)
        fault, fired = _cc1_fault(onb, cat, key, "human", cid)
        with patch.object(Path, "write_text", fault):
            try:
                _sess(paths, factory, driver, ["n", "neu", "", "x"], prints).run()
            except OSError:
                pass
        assert len(fired) == 1, fired

        pending_path = onb / f"attempt__{key}.json"
        assert json.loads(pending_path.read_text())["resolved"] is False

        archive_after_first_pass = copy.deepcopy(catalog.load_figure_save(cat, who, cid))
        assert archive_after_first_pass["characters"][0]["level"] == 1

        # Aktivierung ueber den echten Wechselweg (bereits katalogisierte,
        # aber inaktive Figur -- kein zweiter SL-Dialog).
        _sess(paths, factory, driver, ["n", cid, "x"], prints).run()
        assert _current(paths, who)["characters"][0]["char_id"] == cid

        # Echter, von diesem Auftrag UNABHAENGIGER spaeterer Fortschritt.
        progressed = copy.deepcopy(_current(paths, who))
        progressed["characters"][0].update(
            level=4, wallet={"credits": 87654}, inventory=["KEEP_PROGRESS_AFTER_SECOND_RESUME"],
        )
        core_store.publish_current_save(run, who, progressed, PersonaStateStore(schema_path=_SCHEMA), states)

        # Wechsel WEG und wieder ZURUECK -- synchronisiert das Archiv ueber
        # den bestehenden `_sync_outgoing_active_figure`-Weg auf Level 4.
        _sess(paths, factory, driver, ["n", "human-old", "x"], prints).run()
        archive_after_switch_away = copy.deepcopy(catalog.load_figure_save(cat, who, cid))
        assert archive_after_switch_away["characters"][0]["level"] == 4, (
            "Testannahme: switch-away-Sync muss das Archiv auf den echten Fortschritt heben"
        )
        _sess(paths, factory, driver, ["n", cid, "x"], prints).run()

        before_calls = len(calls)
        before_invites = len(driver.invites)

        # ZWEITER Resume derselben noch offenen/unresolvten Generation.
        _sess(paths, factory, driver, ["n", "neu", "", "x"], prints).run()

        after_archive = catalog.load_figure_save(cat, who, cid)
        after_current = _current(paths, who)

        assert len(calls) == before_calls, "Resume nutzt `state.final_save`, kein neuer GM-Turn erwartet"
        assert len(driver.invites) == before_invites, "kein zweiter Einladungsaufruf erwartet"
        assert after_current["characters"][0]["level"] == 4, "Current bleibt (CC-1) geschuetzt"
        assert after_archive["characters"][0]["level"] == 4, "G1: eigenes Archiv darf nicht transient zurueckfallen"
        assert after_archive["characters"][0]["wallet"] == {"credits": 87654}
        assert after_archive["characters"][0]["inventory"] == ["KEEP_PROGRESS_AFTER_SECOND_RESUME"]


def _ia1_case(actor: str, progress: bool) -> dict:
    """IA-1 (BRIEF-IA1.md, archiv-resume-nachzug): eine eigene Figur ist nach
    einem NORMALEN Wegwechsel INAKTIV, ihr EIGENES Archiv aber (ueber den
    bestehenden, unveraenderten `_sync_outgoing_active_figure`-Mechanismus)
    fortgeschritten (Level 4). Der Resume desselben, claim-bestaetigten
    Auftrags DARF diesen Fortschritt NICHT auf den alten Level-1-Erstsave
    zuruecksetzen -- weder fuer den Menschen (`ui/tui.py:_finish_new_
    character_creation`) noch fuer die Persona (`domain/zeitriss/
    community_creation.py:_publication_reconcile_additional`). CC-1 greift
    hier NICHT (eine ANDERE Figur -- `old` -- ist waehrend des Resumes
    aktiv, nicht `cid` selbst); G1 schuetzt nur den Store-Call, nicht den
    Inhalt vor der Aktivierung. `progress=True` prueft den neuen IA-1-Schutz
    (fail-closed HOLD, `resolved=false`, ehrlicher Abschlussstatus),
    `progress=False` die Positivkontrolle (echter idempotenter
    Teilabschluss bleibt normal fertigstellbar, `resolved=true`)."""
    with tempfile.TemporaryDirectory() as td:
        paths = _setup(Path(td))
        states, run, onb, cat = paths
        calls: list = []
        prints: list = []
        driver = _Driver(["accept"])
        who = "flo_human" if actor == "human" else "medic"
        cid = "human-new-1" if actor == "human" else "medic-new-1"
        old = "human-old" if actor == "human" else "medic-old"
        key = _HUMAN_FRESH_ATTEMPT_KEY if actor == "human" else "medic__additional_pending"

        factory = lambda chat: _GM(
            [_v7_block("medic-new-1" if "__additional_gen" in chat else "human-new-1", "Fresh")], calls, chat,
        )
        fault, fired = _cc1_fault(onb, cat, key, actor, cid)
        with patch.object(Path, "write_text", fault):
            try:
                _sess(paths, factory, driver, ["n", "neu", "" if actor == "human" else "medic", "x"], prints).run()
            except OSError:
                pass
        assert len(fired) == 1, (actor, fired)

        pending_path = onb / f"attempt__{key}.json"
        assert json.loads(pending_path.read_text())["resolved"] is False

        initial = copy.deepcopy(catalog.load_figure_save(cat, who, cid))
        assert initial is not None, "Testannahme: Register/Figursave liefen bereits vor dem injizierten Fehler durch"

        if actor == "human":
            # Bereits katalogisierte, aber INAKTIVE Figur -- ueber den
            # echten oeffentlichen Wechselweg aktiviert, KEIN zweiter
            # SL-Dialog.
            _sess(paths, factory, driver, ["n", cid, "x"], prints).run()
        assert _current(paths, who)["characters"][0]["char_id"] == cid

        progressed = copy.deepcopy(_current(paths, who))
        if progress:
            progressed["characters"][0].update(
                level=4, wallet={"credits": 87654}, inventory=["KEEP_INACTIVE_ARCHIVE_PROGRESS"],
            )
            # Dieselbe autoritative Store-Operation wie ein real erspielter,
            # von diesem offenen Auftrag UNABHAENGIGER spaeterer Abschnitt.
            core_store.publish_current_save(run, who, progressed, PersonaStateStore(schema_path=_SCHEMA), states)

        # NORMALER Wegwechsel -- synchronisiert das Archiv ueber den
        # bestehenden, unveraenderten `_sync_outgoing_active_figure`-
        # Mechanismus auf den jetzigen Stand und macht `cid` INAKTIV (eine
        # ANDERE Figur, `old`, wird aktiv). Dieselbe echte TuiSession, auch
        # fuer die Persona (`who=who`, derselbe Mehrfigurenweg).
        _sess(paths, factory, driver, ["n", old, "x"], prints, who=who).run()
        before_current = copy.deepcopy(_current(paths, who))
        before_archive = copy.deepcopy(catalog.load_figure_save(cat, who, cid))
        assert before_current["characters"][0]["char_id"] == old
        assert before_archive == progressed, (
            "Testannahme: switch-away-Sync muss das Archiv auf den echten Fortschritt heben"
        )

        pending_before = json.loads(pending_path.read_text())
        assert pending_before["resolved"] is False
        before_calls = len(calls)
        before_invites = len(driver.invites)
        before_ids = [e.chrononaut_id for e in catalog.list_for_participant(cat, who)]

        # ZWEITER Resume derselben noch offenen/unresolvten Generation,
        # WAEHREND `cid` INAKTIV ist (eine ANDERE Figur ist aktiv -- genau
        # der Fall, den CC-1 NICHT abdeckt).
        answers = ["n", "neu", "", "x"] if actor == "human" else ["n", "fortsetzen:medic", "x"]
        _sess(paths, factory, driver, answers, prints).run()

        after_current = copy.deepcopy(_current(paths, who))
        after_archive = copy.deepcopy(catalog.load_figure_save(cat, who, cid))
        pending_after = json.loads(pending_path.read_text())
        after_calls = len(calls)
        after_invites = len(driver.invites)
        after_ids = [e.chrononaut_id for e in catalog.list_for_participant(cat, who)]

        # Ein weiterer NORMALER Wechsel danach: zeigt, ob ein (im Bugfall
        # transient veraltetes) Archiv den naechsten Sync weiter beschaedigt.
        _sess(paths, factory, driver, ["n", old, "x"], prints, who=who).run()
        _sess(paths, factory, driver, ["n", cid, "x"], prints, who=who).run()
        after_cycle_current = copy.deepcopy(_current(paths, who))
        after_cycle_archive = copy.deepcopy(catalog.load_figure_save(cat, who, cid))

        return {
            "cid": cid, "who": who,
            "initial": initial, "progressed": progressed,
            "before_current": before_current, "before_archive": before_archive,
            "after_current": after_current, "after_archive": after_archive,
            "after_cycle_current": after_cycle_current, "after_cycle_archive": after_cycle_archive,
            "pending_before": pending_before, "pending_after": pending_after,
            "before_calls": before_calls, "after_calls": after_calls,
            "before_invites": before_invites, "after_invites": after_invites,
            "before_ids": before_ids, "after_ids": after_ids,
            "prints": prints,
        }


def test_ia1_h_progressed_archive_protected_on_inactive_resume():
    """IA-1-H: human-new-1 wird nach einem normalen Wegwechsel INAKTIV, ihr
    eigenes Archiv aber (ueber den bestehenden Sync-Mechanismus) auf Level 4
    fortgeschritten. Der Resume desselben, claim-bestaetigten Auftrags DARF
    diesen Fortschritt NICHT auf den Level-1-Erstsave zuruecksetzen --
    fail-closed HOLD, `resolved=false` (ehrlicher Abschlussstatus), kein
    zweiter Modellaufruf, kein zweiter Invite, keine neue Katalogregistrierung."""
    r = _ia1_case("human", True)
    assert r["after_calls"] == r["before_calls"], "kein zweiter Modellaufruf beim Resume erwartet"
    assert r["after_invites"] == r["before_invites"], "kein zweiter Einladungsaufruf beim Resume erwartet"
    assert r["after_ids"] == r["before_ids"], "keine neue Katalogregistrierung erwartet"
    assert r["after_current"] == r["before_current"], "Current (aktuell 'old') bleibt unveraendert"
    assert r["after_current"]["characters"][0]["char_id"] != r["cid"], "cid bleibt INAKTIV, keine Fehlaktivierung"
    assert r["after_archive"] == r["progressed"], "IA-1: eigenes Archiv darf nicht auf den Erstsave zurueckfallen"
    assert r["after_archive"]["characters"][0]["level"] == 4
    assert r["pending_after"]["resolved"] is False, "HOLD darf die Generation NICHT als erledigt markieren"
    assert any("angehalten" in s and "Archiv" in s for s in r["prints"]), "sichtbares IA-1-HOLD erwartet"
    # Ein weiterer normaler Wechsel darf das (bereits korrekte) Archiv NICHT
    # erneut beschaedigen.
    assert r["after_cycle_archive"] == r["progressed"]
    assert r["after_cycle_current"]["characters"][0]["level"] == 4


def test_ia1_p_progressed_archive_protected_on_inactive_resume():
    """IA-1-P: dieselbe Garantie wie IA-1-H, am Persona-Zusatzfigur-Pfad
    (`_publication_reconcile_additional`, ueber die echte Gate-B-Einladung
    erreicht)."""
    r = _ia1_case("persona", True)
    assert r["after_calls"] == r["before_calls"], "kein zweiter Modellaufruf beim Resume erwartet"
    assert r["after_invites"] == r["before_invites"], "kein zweiter Einladungsaufruf beim Resume erwartet"
    assert r["after_ids"] == r["before_ids"], "keine neue Katalogregistrierung erwartet"
    assert r["after_current"] == r["before_current"], "Current (aktuell 'old') bleibt unveraendert"
    assert r["after_current"]["characters"][0]["char_id"] != r["cid"], "cid bleibt INAKTIV, keine Fehlaktivierung"
    assert r["after_archive"] == r["progressed"], "IA-1: eigenes Archiv darf nicht auf den Erstsave zurueckfallen"
    assert r["after_archive"]["characters"][0]["level"] == 4
    assert r["pending_after"]["resolved"] is False, "HOLD darf die Generation NICHT als erledigt markieren"
    assert any("blocked" in s and "Archiv" in s for s in r["prints"]), "sichtbares IA-1-HOLD erwartet"
    assert r["after_cycle_archive"] == r["progressed"]
    assert r["after_cycle_current"]["characters"][0]["level"] == 4


def test_ia1_h_unchanged_resume_still_completes_fully():
    """IA-1-H Positivkontrolle: OHNE spaeteren Fortschritt (Archiv ==
    Erstsave) bleibt der claim-bestaetigte Resume ein echter, vollstaendiger
    Abschluss -- die Figur wird wieder AKTIV, `resolved=true`, kein
    maskiertes HOLD."""
    r = _ia1_case("human", False)
    assert r["after_calls"] == r["before_calls"]
    assert r["after_current"]["characters"][0]["char_id"] == r["cid"], "echter Abschluss aktiviert die Figur wieder"
    assert r["after_current"] == r["initial"] == r["progressed"]
    assert r["after_archive"] == r["initial"]
    assert r["pending_after"]["resolved"] is True
    assert r["before_ids"] == r["after_ids"]
    assert not any("angehalten" in s for s in r["prints"]), "kein falsches HOLD fuer den unveraenderten Teilabschluss"


def test_ia1_p_unchanged_resume_still_completes_fully():
    """IA-1-P Positivkontrolle: dieselbe Garantie wie IA-1-H am Persona-Pfad."""
    r = _ia1_case("persona", False)
    assert r["after_calls"] == r["before_calls"]
    assert r["after_current"]["characters"][0]["char_id"] == r["cid"]
    assert r["after_current"] == r["initial"] == r["progressed"]
    assert r["after_archive"] == r["initial"]
    assert r["pending_after"]["resolved"] is True
    assert r["before_ids"] == r["after_ids"]


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
