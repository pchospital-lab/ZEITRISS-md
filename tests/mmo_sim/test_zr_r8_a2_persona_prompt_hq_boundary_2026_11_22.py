#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_r8_a2_persona_prompt_hq_boundary_2026_11_22.py —
ZR-R8-A2 (2026-11-22, ALTAIR-ZR-R8-CHARGEN-GRUPPENABSCHLUSS-FIX §A Teil 2):
Regelpräzisierung am wirksamen Persona-Systemprompt
(`domain/zeitriss/community_creation.py:advance_one_persona_creation`).

VBR-Beweisgrenze (ausdrücklich benannt, wie im Briefing verlangt): dies ist
ein **Promptinhalt-Beweis**, KEIN Modellverhaltens-Beweis. Der Test belegt
NUR, dass der tatsächlich an die Persona gesendete `ctx['system']`-String
die neue Formulierung enthält (echter Caller, echter Kontext-Dict, über
den real verwendeten `_FakePersonaDriver.decide(context)`-Empfang) — er
belegt NICHT, dass ein echtes Sprachmodell sich daran hält. Kein
Modellaufruf, Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_block_text  # noqa: E402

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss.community_bootstrap import bootstrap_community  # noqa: E402
from mmo_sim.domain.zeitriss.community_creation import advance_one_persona_creation  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


class _GM:
    def __init__(self, scripted_replies):
        self.scripted = list(scripted_replies)
        self.calls = []

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append(text)
        content = self.scripted.pop(0) if self.scripted else "Die Erschaffung laeuft weiter."
        return {"content": content, "usage": {"prompt_tokens": 5, "completion_tokens": 5}, "sources": [], "latency_s": 0.0, "chat_id": "creation"}


class _RecordingPersonaDriver:
    """Fake-Treiber (Testdouble an der aeussersten Grenze, kein Modellaufruf):
    zeichnet JEDEN empfangenen `context`-Dict auf, antwortet mit einer
    neutralen Charakterantwort."""

    def __init__(self, persona_key, answers):
        self.persona_key = persona_key
        self.config = None
        self.answers = list(answers)
        self.received_contexts: list[dict] = []

    def decide(self, context: dict) -> ParticipantDecision:
        self.received_contexts.append(context)
        contract = context.get("decision_contract")
        if contract:
            import json as _json
            text = _json.dumps({
                "offer_id": contract["offer_id"], "participant_id": contract["participant_id"],
                "decision": "accept",
            })
            return ParticipantDecision(text=text, origin_source="fake:a2", meta={"usage": {"prompt_tokens": 3, "completion_tokens": 3}})
        text = self.answers.pop(0) if self.answers else "Bereit."
        return ParticipantDecision(text=text, origin_source="fake:a2", meta={"usage": {"prompt_tokens": 3, "completion_tokens": 3}})


def test_persona_system_prompt_contains_pre_save_hq_boundary_sentence():
    """Promptinhalt-Beleg (KEIN Modellverhaltens-Beweis): der echte Caller
    `advance_one_persona_creation` -> `_persona_get_reply_factory` baut
    `ctx['system']` -- dieser String muss die neue Grenzformulierung
    enthalten: Charakterentscheidungen/Rueckfragen/Korrektur/bewusster
    Abschluss erlaubt, weitere Aktivitaeten folgen erst nach dem
    bewussten Erstsave."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        states_dir = root / "states"
        onboarding_dir = root / "onboarding"
        catalog_dir = root / "catalog"
        run_dir.mkdir(parents=True, exist_ok=True)
        states_dir.mkdir(parents=True, exist_ok=True)
        write_test_profile(run_dir)

        ps_store = PersonaStateStore(schema_path=_SCHEMA)
        community_dir = run_dir / "community"
        persona_key = "flo_a2_fixture"
        draft = {
            "real_name": persona_key, "archetype": "A2-FIXTURE", "play_style": "A2-FIXTURE",
            "charwunsch": "A2-FIXTURE",
            "plays_char": {
                "save_file": "NOCH_NICHT_ERSCHAFFEN", "character_id": "NOCH_NICHT_ERSCHAFFEN",
                "name": "NOCH_NICHT_ERSCHAFFEN", "callsign": "NOCH_NICHT_ERSCHAFFEN",
            },
        }
        bootstrap_community(community_dir, "community-a2", 1, {persona_key: draft}, ps_store, states_dir, today="2026-11-22")

        # Zwei SL-Antworten: eine gewoehnliche Zwischenfrage (damit die
        # Persona ueberhaupt EINMAL befragt wird, statt dass der Dialog
        # schon beim allerersten SL-Turn mit dem Save-Block endet), danach
        # der gueltige v7-Save.
        gm = _GM([
            "Welche Ausruestung waehlst du fuer deinen ersten Einsatz?",
            full_v7_block_text(f"chrono-{persona_key}", persona_key),
        ])
        persona_driver = _RecordingPersonaDriver(persona_key, ["Bereit fuer den ersten Zug."])

        advance_one_persona_creation(
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
            community_id="community-a2", generation=1, persona_key=persona_key,
            gm_transport_factory=lambda *_a: gm, persona_driver_factory=lambda *_a: persona_driver,
        )

        assert persona_driver.received_contexts, "Persona-Treiber wurde nie aufgerufen -- Test gegenstandslos."
        system_prompts = [c["system"] for c in persona_driver.received_contexts if "system" in c]
        assert system_prompts, persona_driver.received_contexts

        expected_fragment = (
            "Du bringst deine Charaktererschaffung zum bewussten Erstsave (`!save`); weitere "
            "Aktivitaeten folgen erst im Spielkontext nach diesem Abschluss."
        )
        assert any(expected_fragment in sp for sp in system_prompts), (
            f"der neue Grenzsatz fehlt im tatsaechlich gesendeten Personaprompt: {system_prompts}"
        )
        # Bestehender, bewahrter Teil des Personaauftrags bleibt unveraendert enthalten.
        assert any("in deiner eigenen Stimme, konsistent zu deinem Profil" in sp for sp in system_prompts)
        # Charakterentscheidungen/Rueckfragen/Korrektur/bewusster Abschluss ausdruecklich erlaubt.
        assert any(
            "Charakterentscheidungen, Rueckfragen, notwendige Korrekturen und die bewusste "
            "Abschlussentscheidung sind Teil dieses Dialogs" in sp
            for sp in system_prompts
        )


def main() -> int:
    try:
        test_persona_system_prompt_contains_pre_save_hq_boundary_sentence()
    except AssertionError as e:
        print(f"FAIL test_persona_system_prompt_contains_pre_save_hq_boundary_sentence: {e}")
        print("\n0/1 Tests bestanden.")
        return 1
    except Exception:
        import traceback
        traceback.print_exc()
        print("\n0/1 Tests bestanden.")
        return 1
    print("OK   test_persona_system_prompt_contains_pre_save_hq_boundary_sentence")
    print("\n1/1 Tests bestanden.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
