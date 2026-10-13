#!/usr/bin/env python3
"""
tests/mmo_sim/_full_v7_fixture.py — gemeinsamer Testhelper (R12-Savegate,
02_TEAM_UND_QUELLRAHMEN.md "Testfixtures versus Schutzassertionen"):
erzeugt einen MINIMAL-ABER-VOLLSTAENDIGEN, gegen BEIDE unveraenderten v7-
Schemas (`systems/gameflow/saveGame.v7.schema.json` UND `saveGame.v7.
export.schema.json`) gueltigen Save-Block.

FIXTURE_ONLY (kein neues Exportformat, keine Produktlogik): die alten
winzigen Test-Fakes (z.B. `{"v": 7, "characters": [{"char_id": ..., "name":
..., "callsign": ..., "level": 1}]}`) besassen weder die Root-Pflichtfelder
(`campaign`/`economy`/`logs`/`summaries`/`continuity`/`arc`/`ui`/`arena`)
noch die vollen Pflichtfelder je Figur des strikten Export-Schemas. Sie
wurden von der milden Vorgaenger-Pruefung (`ZeitrissHarvestValidator.
validate_block`, NUR v7/Ein-Figur/char_id) akzeptiert, scheitern aber zu
Recht an der R12-Vollschema-Pruefung (`save_validation.validate_structure`,
jetzt Teil von `validate_block`) -- vorhergesehen und gewollt (s. 02_TEAM-
Dokument, nicht abzuschalten). Dieser Helfer liefert TESTS, die einen
tatsaechlich schemagueltigen Block brauchen, EINE gemeinsame Quelle statt
N unabhaengiger Ad-hoc-Reparaturen.

Reiner Testcode, keine Produktabhaengigkeit hierauf (Produktcode kennt
diese Datei nicht)."""
from __future__ import annotations

import json


def full_v7_save(
    char_id: str,
    name: str = "Flo",
    callsign: str | None = None,
    level: int = 1,
    wallet: float = 0.0,
    save_id: str | None = None,
    campaign_mode: str = "mixed",
    **character_overrides,
) -> dict:
    """Vollstaendiger, gegen BEIDE v7-Schemas gueltiger Personal-Save-Block
    mit GENAU EINER Figur. `character_overrides` werden in den EINEN
    Figureneintrag gemergt (z.B. `has_psi=True` zusammen mit den dafuer
    vom Export-Schema zusaetzlich verlangten `psi_heat`/`pp`/
    `psi_abilities`-Overrides)."""
    callsign = callsign or name.upper()
    character = {
        "id": char_id, "name": name, "callsign": callsign, "rank": "Rookie",
        "lvl": level, "xp": 0, "origin": {}, "attr": {}, "lp": 10, "lp_max": 10,
        "stress": 0, "has_psi": False, "sys_installed": 0, "talents": [], "equipment": [],
        "implants": [], "history": {}, "carry": [], "quarters_stash": [], "vehicles": {},
        "reputation": {}, "wallet": wallet, "level_history": {},
    }
    character.update(character_overrides)
    return {
        "v": 7, "zr": "fixture", "save_id": save_id or f"fixture-{char_id}",
        "parent_save_id": None, "merge_id": None, "branch_id": "main",
        "campaign": {
            "episode": 1, "mission": 1, "px": 0, "px_state": "stable", "mode": campaign_mode,
            "rift_seeds": [], "entry_choice_skipped": False, "episode_start": None, "episode_end": None,
        },
        "characters": [character],
        "economy": {},
        "logs": {
            "trace": [], "arena_psi": [], "psi": [], "hud": [], "market": [], "artifact_log": [],
            "notes": [],
            "flags": {
                "runtime_version": "fixture", "chronopolis_unlocked": False, "imported_saves": [],
                "duplicate_branch_detected": False, "duplicate_character_detected": False,
                "continuity_conflicts": [],
            },
        },
        "summaries": {"summary_last_episode": "", "summary_last_rift": "", "summary_active_arcs": ""},
        "continuity": {
            "last_seen": {"mode": "hq", "episode": 1, "mission": 1, "location": "fixture"},
            "split": {}, "roster_echoes": [], "shared_echoes": [], "convergence_tags": [],
            "npc_roster": [], "active_npc_ids": [],
        },
        "arc": {"factions": {}, "questions": [], "hooks": []},
        "ui": {
            "gm_style": "fixture", "suggest_mode": False, "action_mode": "uncut", "contrast": "fixture",
            "badge_density": "fixture", "output_pace": "fixture", "voice_profile": "fixture",
            "intro_seen": False, "dice": {"debug_rolls": False},
        },
        "arena": {
            "active": False, "phase": "idle", "queue_state": "idle", "mode": "none", "tier": 0,
            "previous_mode": None, "resume_token": None, "contract_id": None, "streak": 0,
            "pending_rewards": {"cu": 0, "xp": 0, "arena_rep": 0, "multiplier": 1, "risk": "none"},
            "banked_rewards": {"cu": 0, "xp": 0, "arena_rep": 0},
            "rewarded_runs_this_contract": 0, "first_wins": {}, "defeated_types": [],
            "last_reward_episode": None, "wins_player": 0, "wins_opponent": 0, "match_policy": "none",
        },
    }


def full_v7_block_text(char_id: str, name: str = "Flo", **kwargs) -> str:
    """Wie `full_v7_save`, aber als fenced-JSON-SL-Antworttext (fuer Tests,
    die wie `saves.extract_all_saves` einen Rohtext parsen)."""
    return "```json\n" + json.dumps(full_v7_save(char_id, name=name, **kwargs)) + "\n```"


def upgrade_narrow_save(narrow: dict) -> dict:
    """W45 FIXTURE_ONLY (R12-Savegate, 02_TEAM_UND_QUELLRAHMEN.md
    "Testfixtures versus Schutzassertionen"): hebt einen alten, vor der
    R12-Vollschema-Annahmegrenze geschriebenen schmalen Legacy-Save-Block
    (nur `v`/`save_id`/GENAU EINE Figur mit `id`(/`char_id`)/`name`/
    `callsign`[/`level`,`lvl`,`wallet`,...]) auf einen vollen, gegen BEIDE
    unveraenderten v7-Schemas gueltigen Block (`full_v7_save`) -- erhaelt
    dabei JEDEN vorhandenen Identitaets-/Fortschrittswert (char_id/id,
    name, callsign, Level, Wallet, etwaige bewusste Testdefekte als
    zusaetzliche Figur-Overrides) unveraendert.

    Liefert IMMER GENAU EINE Figur mit `id` (kein `char_id`-Schluessel):
    das strikte Export-Schema hat `additionalProperties: false` auf
    Figurenebene und kennt nur `id`, keinen zusaetzlichen `char_id`-
    Schluessel (s. `_ia1_v7_fixture.make_v7_fixture`, bereits W47-
    abgenommene kanonische Referenz, ebenfalls nur `id`). Aufrufer, die
    bisher `save["characters"][0]["char_id"]` gelesen haben, lesen ab W45
    `["id"]` -- derselbe Wert, nur der schon immer redundante Zweitschluessel
    entfaellt. Root-Schluessel ausserhalb der erlaubten Exportmenge (z.B.
    `_fixture_note`) werden NICHT uebernommen (`additionalProperties: false`
    gilt auch auf Root-Ebene) -- sie waren reine Testannotation, nie ein
    gepruefter Wert.

    Reiner Testcode, keine Produktabhaengigkeit hierauf."""
    char = dict(narrow["characters"][0])
    char_id = char.pop("char_id", None) or char["id"]
    char.pop("id", None)
    name = char.pop("name", "Flo")
    callsign = char.pop("callsign", None)
    level = char.pop("level", char.pop("lvl", 1))
    wallet = char.pop("wallet", 0.0)
    save_id = narrow.get("save_id")
    campaign_mode = narrow.get("campaign", {}).get("mode", "mixed") if isinstance(narrow.get("campaign"), dict) else "mixed"
    return full_v7_save(
        char_id, name=name, callsign=callsign, level=level, wallet=wallet,
        save_id=save_id, campaign_mode=campaign_mode, **char,
    )
