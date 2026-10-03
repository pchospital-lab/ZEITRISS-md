#!/usr/bin/env python3
"""
tests/mmo_sim/test_r1_persona_b1_b2_rework_2026_10_02.py — R1-Nacharbeit
(Persona-Zusatzfigur-Nahtstelle, GO_MIT_AUFLAGEN-Nachlese 2026-10-02):
dauerhafte Repo-Tests fuer die beiden MUSS-Blocker, die der End-Critic am
PERSONA-Aequivalent des bereits gefixten menschlichen Mehrfigurenpfads
(`ui/tui.py:_finish_new_character_creation`) fand — adaptiert aus den
Critic-eigenen Proben (`critic/evidence/scripts/critic_probe_persona_
b1_equivalent.py`/`critic_probe_persona_b2_equivalent.py`, dort nur
Einmalbelege, hier als dauerhafter `run_all.py`-Schutz):

  R1-B1 — `domain/zeitriss/community_creation.py:advance_additional_
          persona_creation` haelt eine in Arbeit befindliche Zusatzfigur-
          Generation stabil (`_additional_creation_pending_key` +
          `onboarding.bind_attempt`/`resolve_attempt`), wenn ein
          gewoehnlicher `catalog.store_figure_save`-I/O-Fehler NACH
          bereits erfolgreichem `catalog.register` auftritt: ein Reentry
          mit einer (wie beim echten Aufrufer `ui/tui.py:
          _invite_persona_fresh_start`) NEU aus der (bereits um 1
          gewachsenen) Kataloganzahl abgeleiteten `generation` nimmt
          DENSELBEN Vorgang wieder auf, OHNE zweiten Modellaufruf und OHNE
          die erste, teilregistrierte Figur fuer immer als Katalogleiche
          zurueckzulassen.
  R1-B2 — `_publication_reconcile_additional` haelt (HOLD) VOR jeder
          ueberschreibenden Publikation, wenn eine abgeschlossene
          Zusatzfigur-Antwort eine BEREITS (bei irgendeinem Teilnehmer)
          real gespeicherte `chrononaut_id` mit ABWEICHENDEM Inhalt
          liefert -- `publish_current_save` lief vorher bedingungslos und
          konnte den aktiven Current mit Fremdinhalt ueberschreiben,
          waehrend das eigene Figur-Save-Archiv unter derselben ID den
          ALTEN Stand behielt (Archiv/Current-Diskrepanz).

Pure Python, nur `assert`, echter Exitcode -- kein echter Modellcall, kein
LAN. Reine Produktfunktionen (`advance_additional_persona_creation`,
`catalog`, `core.store`), keine Mocks am Produktcode selbst (nur an
`pathlib.Path.write_text`, um einen gewoehnlichen I/O-Fehler an genau
EINER Datei zu simulieren, analog den bestehenden Gegenproben/Testfixturen
in diesem Repo, z.B. `tests/mmo_sim/test_n1_n7_...py:test_n5_...`)."""
from __future__ import annotations

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
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.community_creation import advance_additional_persona_creation  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


def _v7_block(char_id: str, name: str) -> str:
    return (
        "```json\n"
        f'{{"v": 7, "characters": [{{"char_id": "{char_id}", "name": "{name}", '
        f'"callsign": "{name.upper()}", "level": 1}}]}}\n'
        "```"
    )


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


def _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, participant_id, char_id, name):
    """Minimaler, bereits vollstaendig aktiver Bestand -- derselbe
    Produktweg wie `tests/mmo_sim/test_n1_n7_...py:_give_existing_figure`,
    hier bewusst schlank gehalten (nur die fuer R1-B1/B2 relevanten
    Felder)."""
    ps_store = PersonaStateStore(schema_path=schema_path)
    ps_store.save_state(participant_id, {
        "v": 2, "persona_key": participant_id, "real_name": name,
        "archetype": "R1-NACHARBEIT", "play_style": "R1-NACHARBEIT", "charwunsch": "R1-NACHARBEIT",
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


class _GM:
    def __init__(self, reply: str):
        self.reply = reply
        self.calls = 0

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls += 1
        return {"content": self.reply, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "r1-persona-rework"}


class _AcceptDriver:
    def decide(self, ctx):
        return ParticipantDecision(text="Bereit.", origin_source="TEST_R1_PERSONA_REWORK", meta={"usage": {}})


def test_r1_b1_persona_additional_creation_survives_figure_save_io_fault():
    """Adaption von `critic_probe_persona_b1_equivalent.py`: ein `OSError`
    in `catalog.store_figure_save`, NACHDEM `catalog.register` fuer die
    neue Zusatzfigur bereits durchgelaufen ist, darf einen Reentry mit der
    (wie beim echten Aufrufer) NEU aus der gewachsenen Kataloganzahl
    abgeleiteten `generation` NICHT zu einem zweiten Modellaufruf/einer
    dritten Figur fuehren -- die erste, teilregistrierte Figur darf NICHT
    fuer immer unvollstaendig/verwaist bleiben."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, "medic", "medic-old", "MedicOld")

        entries_before = catalog.list_for_participant(catalog_dir, "medic")
        generation_attempt1 = len(entries_before) + 1
        assert generation_attempt1 == 2

        orig_write_text = Path.write_text
        fired = []

        def selective_fault(path, *a, **kw):
            if path.name == "medic__medic-fault.json.tmp" and not fired:
                fired.append(str(path))
                raise OSError("R1_B1 store_figure_save boundary")
            return orig_write_text(path, *a, **kw)

        gm1 = _GM(_v7_block("medic-fault", "MedicFault"))
        crashed = None
        with patch.object(Path, "write_text", selective_fault):
            try:
                advance_additional_persona_creation(
                    run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
                    onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
                    community_id="community-r1-test", generation=generation_attempt1, persona_key="medic",
                    gm_transport_factory=lambda *a, **k: gm1,
                    persona_driver_factory=lambda pk: _AcceptDriver(),
                )
            except OSError as e:
                crashed = e
        assert crashed is not None, "erwarteter OSError beim ersten Versuch wurde NICHT geworfen"
        assert fired, "der gezielte Fault wurde nie ausgeloest -- Test misst nichts"

        entries_after_fault = catalog.list_for_participant(catalog_dir, "medic")
        assert any(e.chrononaut_id == "medic-fault" for e in entries_after_fault), (
            "register haette VOR dem Fault bereits durchgelaufen sein muessen"
        )
        assert catalog.load_figure_save(catalog_dir, "medic", "medic-fault") is None, (
            "figure_save haette durch den Fault NICHT persistiert sein duerfen"
        )

        # Reentry: der echte Aufrufer (`ui/tui.py:_invite_persona_fresh_start`,
        # Zeile ~692) leitet eine NEUE Einladungsgelegenheit erneut aus der
        # (jetzt gewachsenen) Kataloganzahl ab -- UNVERAENDERT, s. dortigen
        # Kommentar/Docstring von `_additional_creation_pending_key`.
        generation_retry = len(catalog.list_for_participant(catalog_dir, "medic")) + 1
        assert generation_retry == 3, "Testannahme: Kataloganzahl ist durch register bereits um 1 gewachsen"

        gm2 = _GM(_v7_block("medic-third", "MedicThird"))
        outcome2 = advance_additional_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-r1-test", generation=generation_retry, persona_key="medic",
            gm_transport_factory=lambda *a, **k: gm2,
            persona_driver_factory=lambda pk: _AcceptDriver(),
        )

        assert gm2.calls == 0, "Reentry haette den gestockten Vorgang wiederaufnehmen muessen -- KEIN neuer SL-Turn"
        assert outcome2.status == "completed" and outcome2.chrononaut_id == "medic-fault", (
            f"Reentry haette die ERSTE (gestockte) Figur fertigstellen muessen, nicht eine dritte: {outcome2}"
        )
        final_ids = {e.chrononaut_id for e in catalog.list_for_participant(catalog_dir, "medic")}
        assert final_ids == {"medic-old", "medic-fault"}, f"keine dritte Figur erwartet: {final_ids}"
        assert catalog.load_figure_save(catalog_dir, "medic", "medic-fault") is not None, (
            "medic-fault darf NICHT fuer immer als Katalogleiche (ohne figure_save) zurueckbleiben"
        )


def test_r1_b2_persona_additional_creation_holds_on_rogue_identity_collision():
    """Adaption von `critic_probe_persona_b2_equivalent.py`: eine
    abgeschlossene Zusatzfigur-Antwort mit einer BEREITS (bei derselben
    Persona) real gespeicherten `chrononaut_id`, aber ABWEICHENDEM Inhalt,
    darf NICHT den aktiven Current ueberschreiben -- `_publication_
    reconcile_additional` muss anhalten (HOLD), bevor `publish_current_
    save` laeuft."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        _give_existing_figure(schema_path, states_dir, run_dir, catalog_dir, onboarding_dir, "medic", "medic-old", "MedicOld")
        ps_store = PersonaStateStore(schema_path=schema_path)

        gm1 = _GM(_v7_block("medic-second", "MedicSecond"))
        outcome1 = advance_additional_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-r1-test", generation=2, persona_key="medic",
            gm_transport_factory=lambda *a, **k: gm1,
            persona_driver_factory=lambda pk: _AcceptDriver(),
        )
        assert outcome1.status == "completed" and outcome1.chrononaut_id == "medic-second"

        # Bewusst zurueckwechseln, damit 'medic-second' registriert+gesichert,
        # aber INAKTIV ist (derselbe Zwischenzustand wie bei der Critic-Probe).
        catalog.bind_for_section(catalog_dir, "medic", "medic-old", has_open_section=False)
        core_store.publish_current_save(
            run_dir, "medic", catalog.load_figure_save(catalog_dir, "medic", "medic-old"), ps_store, states_dir,
        )
        original_second_save = catalog.load_figure_save(catalog_dir, "medic", "medic-second")
        assert original_second_save is not None

        # Dritte Gelegenheit: SL-Fehlverhalten/Verwechslung liefert dieselbe
        # char_id 'medic-second' erneut, aber mit ABWEICHENDEM Inhalt.
        colliding_block = (
            "```json\n"
            '{"v": 7, "characters": [{"char_id": "medic-second", "name": "ROGUE", '
            '"callsign": "ROGUE", "level": 9, "wallet": {"credits": 999999}, "inventory": ["COLLISION_MARK"]}]}\n'
            "```"
        )
        gm2 = _GM(colliding_block)
        outcome2 = advance_additional_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-r1-test", generation=3, persona_key="medic",
            gm_transport_factory=lambda *a, **k: gm2,
            persona_driver_factory=lambda pk: _AcceptDriver(),
        )

        assert outcome2.status == "blocked", f"erwartetes HOLD bei Identitaetskollision, erhalten: {outcome2}"
        # Auftragsbindung-Nachzug (2026-10-02): der HOLD-Grund wird jetzt
        # ueber die Claim-/Auftragsbindungspruefung formuliert (s.
        # community_creation.py:_publication_reconcile_additional), nicht
        # mehr ueber einen reinen Inhaltsvergleich -- Wortlaut angepasst,
        # die gepruefte Eigenschaft (kontrollierter HOLD, kein Erfolg) bleibt
        # identisch.
        assert "kontrollierter Konflikt" in (outcome2.reason or ""), outcome2.reason

        archived_after = catalog.load_figure_save(catalog_dir, "medic", "medic-second")
        current_after = core_store.load_current_save_or_raise(run_dir, "medic", ps_store, states_dir)
        assert archived_after == original_second_save, "Archiv darf durch das HOLD NICHT veraendert worden sein"
        assert current_after["characters"][0]["char_id"] == "medic-old", (
            "Current haette unveraendert bei 'medic-old' bleiben muessen, nicht den Rogue-Inhalt uebernehmen"
        )
        assert current_after["characters"][0].get("inventory") != ["COLLISION_MARK"], (
            "Rogue-Inhalt darf NICHT als Current veroeffentlicht worden sein"
        )
        assert catalog.active_chrononaut_id(catalog_dir, "medic") == "medic-old"


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
