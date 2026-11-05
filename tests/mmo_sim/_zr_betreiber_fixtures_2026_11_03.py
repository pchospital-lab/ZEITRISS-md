#!/usr/bin/env python3
"""
tests/mmo_sim/_zr_betreiber_fixtures_2026_11_03.py -- gemeinsamer Testhelper
fuer die ZR-BETREIBER-GASTERSCHAFFUNG-20261103-R1 O1/O2-Treiber (Linus,
Stage C). Reiner Testcode, keine Produktabhaengigkeit hierauf -- dieselbe
bereits bewaehrte Aufbaufolge wie `test_r3_f3_host_persona_authority.py`
(`_register_own_figure`/`_bootstrap_own_persona`), hier ausgelagert, damit
O1 UND O2 dieselbe Quelle teilen statt sie zu duplizieren."""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.community_bootstrap import bootstrap_community  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402

SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


def register_own_figure(
    onboarding_dir: Path, catalog_dir: Path, participant_id: str, char_id: str,
    *, run_dir: Path, states_dir: Path, level: int = 1,
) -> dict:
    """Abgeschlossene, publizierte Figur fuer `participant_id` -- identisch
    zu `test_r3_f3_host_persona_authority.py:_register_own_figure`."""
    save = full_v7_save(char_id, name=participant_id, save_id=f"fixture-{participant_id}-001", level=level)
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
    ))
    ps_store = PersonaStateStore(schema_path=SCHEMA_PATH)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, participant_id, char_id, save)
    core_store.publish_current_save(run_dir, participant_id, save, ps_store, states_dir)
    return save


def bootstrap_own_persona(run_dir: Path, states_dir: Path, host_id: str, persona_key: str) -> None:
    """Legt `persona_key` als EIGENE bestaetigte Hostpersona von `host_id`
    an -- Voraussetzung, damit `lead:persona:<id>`/`persona:<id>` die
    Bestandsgrenze (`_known_ai_overview`, F3 §2) passiert. Identisch zu
    `test_r3_f3_host_persona_authority.py:_bootstrap_own_persona`."""
    ps_store = PersonaStateStore(schema_path=SCHEMA_PATH)
    community_dir = run_dir / "community"
    drafts = {
        persona_key: {
            "real_name": persona_key, "archetype": "Test-Archetyp",
            "play_style": "SIMULIERT/DEMO", "charwunsch": "SIMULIERT/DEMO (O1/O2-Testfixture).",
            "plays_char": {
                "save_file": "NOCH_NICHT_ERSCHAFFEN", "character_id": "NOCH_NICHT_ERSCHAFFEN",
                "name": "NOCH_NICHT_ERSCHAFFEN", "callsign": "NOCH_NICHT_ERSCHAFFEN",
            },
        },
    }
    result = bootstrap_community(
        community_dir, f"community-{host_id}", 1, drafts, ps_store, states_dir, today="2026-11-03",
    )
    assert persona_key in result.personas_written, result.reason


class AcceptLeadDriver:
    """In-Process-Persona-Treiber (Modellrand-Double, EHRLICH als solcher
    gekennzeichnet): nimmt JEDE Einladungs-/Leaderentscheidung
    (`decision_contract`) real an, liefert sonst eine gescriptete
    Spielzug-Antwort. `.decide` ist der einzige vom Produktvertrag
    (`adapters.base.ParticipantDriver`) verlangte Einstiegspunkt."""

    def __init__(self, pk: str, play_replies: list[str]):
        self.pk = pk
        self._play_replies = list(play_replies)
        self.calls: list[dict] = []

    def decide(self, ctx: dict) -> ParticipantDecision:
        self.calls.append(ctx)
        if "decision_contract" in ctx:
            return ParticipantDecision(
                text=f"Ja, ich uebernehme ({self.pk}).", decision="accept",
                origin_source=f"fake:lead:{self.pk}",
            )
        if not self._play_replies:
            raise AssertionError(f"AcceptLeadDriver({self.pk}): Spielzug-Skript erschoepft.")
        text = self._play_replies.pop(0)
        return ParticipantDecision(text=text, origin_source=f"fake:lead:{self.pk}")
