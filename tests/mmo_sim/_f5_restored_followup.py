#!/usr/bin/env python3
"""
tests/mmo_sim/_f5_restored_followup.py -- Hilfsprozess fuer den F5-Nachweis
(ZR-POPULATION-BACKUP-RESTORE-NACHZUG-20261101-R1, 02_NACHZUG.md:39-47).

Startet in einem ECHTEN frischen OS-Prozess auf den RESTAURIERTEN Roots und
fuehrt eine NORMALE spielwirksame Folgeaktion ueber die regulaere
Spiel-/Speicher-/Abschlusslogik aus (`core.runtime.SectionRuntime.
run_full_section` -- dieselbe Engine, die die beiden Produktioncaller
`ui/tui.py:_run_table_round` und `core/lobby_flow.py:play_bound_table`
verwenden). KEIN Low-Level `xp=999`+`publish_current_save`-Write.

Nur GM-/Persona-Treiber sind Fakes (Transportrand, laut 02_NACHZUG.md
ausdruecklich erlaubt). Das verwendete Schema ist das REGULAERE PRODUKTSCHEMA
(Argument `schema_path`, i.d.R. `internal/qa/fixtures/persona-state.schema.json`),
NICHT das Schema aus dem (entfernten, unerreichbaren) alten Populationsroot.

Aufruf: `python3 _f5_restored_followup.py <restored_root> <schema_path>`
Gibt bei Erfolg eine JSON-Zeile mit dem Ergebnis aus und endet mit Exit 0."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
for _p in (str(_REPO_ROOT), str(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from _full_v7_fixture import full_v7_save  # noqa: E402
from _section_completion_resume_fixtures import (  # noqa: E402
    COMPLETION_MARKER, ScriptedDriver, ScriptedGmTransport, debrief_with_marker, harvest_extractor,
)

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import population_backup, store  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.core.runtime import SectionRuntime  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy  # noqa: E402

LEADER_PK = "leader_pk"
GUEST_PK = "guest_pk"


def play_fresh_section(root: Path, schema_path: Path, table_id: str = "t-restored-followup") -> dict:
    roots = population_backup.PopulationRoots(
        onboarding_dir=root / "onboarding", catalog_dir=root / "catalog",
        run_dir=root / "run", states_dir=root / "states",
        registry_dir=root / "registry", prefs_root=root,
    )
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    lobby = store.Lobby(roots.run_dir, table_size_policy=ZeitrissTableSizePolicy())
    table, derivation = store.create_table_from_offer_log(
        lobby, table_id,
        offer_log_events=[
            {"type": "offer", "id": "of1", "from": LEADER_PK, "wants": [GUEST_PK]},
            {"type": "consent", "offer_id": "of1", "from": GUEST_PK, "accept": True},
        ],
        chrononaut_ids={LEADER_PK: "chrono-leader", GUEST_PK: "chrono-guest"},
    )
    if table is None:
        raise RuntimeError(f"Neuer Tisch auf restauriertem Root nicht erzeugbar: {derivation}")
    section_id = f"{table_id}-section"
    leader_save = full_v7_save("chrono-leader", name="Testfigur")
    guest_save = full_v7_save("chrono-guest", name="Testfigur")
    debrief = debrief_with_marker({"chrono-leader": leader_save, "chrono-guest": guest_save})
    gm = ScriptedGmTransport(["SL-Anker.", "SL-Gast.", debrief])
    leader_driver = ScriptedDriver([
        ParticipantDecision(text="Anker-Text.", save_payload=leader_save, origin_source="fake:leader"),
        ParticipantDecision(text="Debrief-Anfrage.", origin_source="fake:leader-debrief"),
        ParticipantDecision(text="Reflexion Leader.", origin_source="fake:leader-reflect"),
    ])
    guest_driver = ScriptedDriver([
        ParticipantDecision(text="Gast-Import.", save_payload=guest_save, origin_source="fake:guest"),
        ParticipantDecision(text="Reflexion Gast.", origin_source="fake:guest-reflect"),
    ])
    controller = TableController(
        leader_key=LEADER_PK, drivers={LEADER_PK: leader_driver, GUEST_PK: guest_driver},
    )
    runtime = SectionRuntime(
        lobby=lobby, table=table, gm_transport=gm, marker=COMPLETION_MARKER,
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        harvest_extractor=harvest_extractor,
    )
    outcome = runtime.run_full_section(
        controller, section_id,
        contexts_by_persona={LEADER_PK: {"user": "ctx-leader"}, GUEST_PK: {"user": "ctx-guest"}},
        states_dir=roots.states_dir, today="2026-11-02", ts="2026-11-02T00:00:00",
    )
    final_path = roots.run_dir / "completion" / f"{section_id}__final.json"
    leader_state = ps_store.load_state(LEADER_PK, states_dir=roots.states_dir)
    return {
        "completion_success": bool(outcome.completion.success),
        "section_id": section_id,
        "final_marker_present": final_path.is_file(),
        "leader_rounds_played": leader_state.get("rounds_played"),
    }


def main(argv: list[str]) -> int:
    root = Path(argv[1])
    schema_path = Path(argv[2])
    result = play_fresh_section(root, schema_path)
    print(json.dumps(result))
    return 0 if result["completion_success"] and result["final_marker_present"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
