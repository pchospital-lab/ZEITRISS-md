#!/usr/bin/env python3
"""
tests/mmo_sim/_population_backup_fixtures.py — gemeinsamer Testhelper fuer
ZR-POPULATION-BACKUP-RESTORE-20261101-R1. Baut eine kleine, aber ECHTE
Population (spielender Tisch, unbeteiligte Persona mit Memory, inaktive
Figur mit eigenem Katalogsave, zweiter OFFENER Tisch, Registry-/Prefs-
Datensaetze) ueber die echten Produktschreibwege (`store`, `persona_state`,
`catalog`, `ParticipantRegistry`, `onboarding_prefs`) -- NUR GM/Persona-
Treiber sind Fakes (Transportrand). Reiner Testcode, keine
Produktabhaengigkeit hierauf."""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _full_v7_fixture import full_v7_save  # noqa: E402
from _section_completion_resume_fixtures import (  # noqa: E402
    COMPLETION_MARKER, ScriptedDriver, ScriptedGmTransport, debrief_with_marker, harvest_extractor,
)

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import population_backup, store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.core.runtime import SectionRuntime  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy  # noqa: E402
from mmo_sim.registry.participants import ParticipantRegistry  # noqa: E402
from mmo_sim.ui import onboarding_prefs  # noqa: E402

PRODUCER_ANCHOR = "tests/mmo_sim/_population_backup_fixtures.py"

_DUMMY_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)

BYSTANDER_PK = "bystander_pk"
INACTIVE_CHRONONAUT_ID = "chrono-inactive"
LEADER_PK = "leader_pk"
GUEST_PK = "guest_pk"
OTHER_PK = "other_pk"
FAKE_TOKEN_SENTINEL = "FAKE-NOT-REAL-TOKEN-xyz"


@dataclass
class Fixture:
    root: Path
    roots: population_backup.PopulationRoots
    ps_store: PersonaStateStore
    lobby: object
    table: object
    run_id: str
    table_id: str
    section_id: str
    open_table_id: str


def make_roots(root: Path) -> population_backup.PopulationRoots:
    return population_backup.PopulationRoots(
        onboarding_dir=root / "onboarding", catalog_dir=root / "catalog",
        run_dir=root / "run", states_dir=root / "states",
        registry_dir=root / "registry", prefs_root=root,
    )


def backup_root_for(fx: "Fixture") -> Path:
    return fx.root / "population_backups"


def build_fixture(root: Path, *, table_id: str = "t-pop") -> Fixture:
    roots = make_roots(root)
    for d in (roots.onboarding_dir, roots.catalog_dir, roots.states_dir, roots.registry_dir):
        d.mkdir(parents=True, exist_ok=True)
    schema_path = root / "schema.json"
    schema_path.write_text(_DUMMY_SCHEMA, encoding="utf-8")
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)

    def seed(pk: str, cid: str, **extra) -> None:
        # Produktschema-valide Grundform (`internal/qa/fixtures/persona-state.
        # schema.json` verlangt real_name/archetype/play_style/charwunsch +
        # vollstaendiges plays_char) -- damit eine restaurierte Population auch
        # mit dem REGULAEREN Produktschema gelesen/gespielt werden kann
        # (F5-Nachzug), nicht nur mit dem permissiven Test-Dummyschema.
        state = {
            "v": 2, "persona_key": pk, "real_name": f"Echtname {pk}",
            "archetype": "cqb", "play_style": "direkt", "charwunsch": "Testcharakterwunsch",
            "rounds_played": 0,
            "plays_char": {
                "save_file": f"{cid}.json", "character_id": cid,
                "name": f"Figur {cid}", "callsign": cid,
            },
        }
        state.update(extra)
        ps_store.save_state(pk, state, states_dir=roots.states_dir)

    seed(LEADER_PK, "chrono-leader")
    seed(GUEST_PK, "chrono-guest")
    seed(
        BYSTANDER_PK, "chrono-bystander",
        learnings=["Bystander-Erkenntnis: hat diesen Abschnitt nicht gesehen."],
        relationships={"leader_pk": "Kennt ihn nur vom Hoerensagen."},
    )
    seed(OTHER_PK, "chrono-other")

    lobby = store.Lobby(roots.run_dir, table_size_policy=ZeitrissTableSizePolicy())
    for pk in (LEADER_PK, GUEST_PK, BYSTANDER_PK, OTHER_PK):
        lobby.join(pk)

    table, derivation = store.create_table_from_offer_log(
        lobby, table_id,
        offer_log_events=[
            {"type": "offer", "id": "o1", "from": LEADER_PK, "wants": [GUEST_PK]},
            {"type": "consent", "offer_id": "o1", "from": GUEST_PK, "accept": True},
        ],
        chrononaut_ids={LEADER_PK: "chrono-leader", GUEST_PK: "chrono-guest"},
    )
    assert table is not None, f"Tisch haette entstehen muessen: {derivation}"

    open_table_id = "t-open-other"
    open_table, open_derivation = store.create_table_from_offer_log(
        lobby, open_table_id,
        offer_log_events=[{"type": "offer", "id": "o2", "from": OTHER_PK, "wants": []}],
        chrononaut_ids={OTHER_PK: "chrono-other"},
    )
    assert open_table is not None, f"Offener Tisch haette entstehen muessen: {open_derivation}"

    catalog.register(roots.catalog_dir, catalog.CatalogEntry(
        participant_id=LEADER_PK, chrononaut_id="chrono-leader", persona_key=LEADER_PK,
    ))
    catalog.bind_for_section(roots.catalog_dir, LEADER_PK, "chrono-leader", has_open_section=False)
    catalog.register(roots.catalog_dir, catalog.CatalogEntry(
        participant_id=GUEST_PK, chrononaut_id="chrono-guest", persona_key=GUEST_PK,
    ))
    catalog.bind_for_section(roots.catalog_dir, GUEST_PK, "chrono-guest", has_open_section=False)
    # Inaktive Figur: registriert, eigener Katalogsave, NIE aktiv gebunden.
    catalog.register(roots.catalog_dir, catalog.CatalogEntry(
        participant_id=LEADER_PK, chrononaut_id=INACTIVE_CHRONONAUT_ID, persona_key=LEADER_PK,
    ))
    catalog.store_figure_save(
        roots.catalog_dir, LEADER_PK, INACTIVE_CHRONONAUT_ID,
        full_v7_save(INACTIVE_CHRONONAUT_ID, name="Inaktive Figur"),
    )

    # Onboarding-Journal (whole_population-Pflicht): abgeschlossene
    # Erschaffung fuer leader_pk, damit die Rolle 'onboarding' nicht leer ist.
    onboarding.start_or_resume(roots.onboarding_dir, LEADER_PK)
    onboarding.complete_with_save(
        roots.onboarding_dir, LEADER_PK, full_v7_save("chrono-leader", name="Testfigur"),
        ZeitrissHarvestValidator(), "chrono-leader",
    )

    registry = ParticipantRegistry(roots.registry_dir)
    registry.register_participant(kind="human", display_name="Leaderin")
    registry.register_participant(kind="human", display_name="Zaungast")

    onboarding_prefs.mark_tutorial_seen(roots.prefs_root, LEADER_PK)
    (roots.prefs_root / "last_participant.json").write_text(
        json.dumps({"participant_id": LEADER_PK}), encoding="utf-8",
    )

    # Ausschlussfixturen (privacy_and_exclusions): PID-OS-Lock, transiente
    # Tmp-Restdatei, FAKE-Sentinel-Token DIREKT neben den nichtgeheimen
    # Prefs -- beweist Root-/Glob-Scoping statt einer Dateinamen-Blacklist.
    (roots.run_dir / "lab.lock.json").write_text(json.dumps({"pid": 999999}), encoding="utf-8")
    (roots.states_dir / "ghost.json.tmp-424242").write_text("{nicht json, transient}", encoding="utf-8")
    (roots.prefs_root / "session_auth_sentinel.txt").write_text(FAKE_TOKEN_SENTINEL, encoding="utf-8")

    write_test_profile(roots.run_dir)

    return Fixture(
        root=root, roots=roots, ps_store=ps_store, lobby=lobby, table=table,
        run_id=lobby.run_id, table_id=table_id, section_id=f"{table_id}-section",
        open_table_id=open_table_id,
    )


def play_section_to_success(fx: Fixture):
    """Echter Abschluss: Anker (Leader, bindbarer Save), Gast-Import,
    Debrief MIT Marker + beiden v7-Save-Bloecken, danach Pflicht-
    Reflexion je Mitglied -- GENAU der Weg, den `core.runtime.SectionRuntime.
    run_full_section` fuer einen echten Abschluss verlangt (s.
    `_section_completion_resume_fixtures.py`, dort identisch genutzt)."""
    leader_save = full_v7_save("chrono-leader", name="Testfigur")
    guest_save = full_v7_save("chrono-guest", name="Testfigur")
    debrief = debrief_with_marker({"chrono-leader": leader_save, "chrono-guest": guest_save})
    gm = ScriptedGmTransport(["SL-Antwort auf Anker.", "SL-Antwort auf Gast-Import.", debrief])
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
        lobby=fx.lobby, table=fx.table, gm_transport=gm, marker=COMPLETION_MARKER,
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=fx.ps_store,
        harvest_extractor=harvest_extractor,
    )
    outcome = runtime.run_full_section(
        controller, fx.section_id,
        contexts_by_persona={LEADER_PK: {"user": "ctx-leader"}, GUEST_PK: {"user": "ctx-guest"}},
        states_dir=fx.roots.states_dir, today="2026-11-01", ts="2026-11-01T00:00:00",
    )
    return outcome


def run_backup(fx: Fixture, *, created_at_utc: str = "2026-11-01T00:00:00+00:00",
               capture_is_at_completion: bool = True):
    # Modelliert die Sicherung DIREKT beim Abschnittsabschluss (wie der reale
    # Hook): `capture_is_at_completion=True` bindet den Abschlussfingerprint
    # synchron. Retry-/Nachhol-Faelle rufen die Produkt-API mit dem Default
    # (False) bzw. ueber `retry_population_backup`.
    return population_backup.generate_population_backup(
        fx.roots,
        population_backup.GenerationKey(run_id=fx.run_id, table_id=fx.table_id, section_id=fx.section_id),
        backup_root_for(fx), producer_code_anchor=PRODUCER_ANCHOR, created_at_utc=created_at_utc,
        capture_is_at_completion=capture_is_at_completion,
    )
