#!/usr/bin/env python3
"""Baut einen strict-schema-validen 5er-HQ-Highlevel-Anker (Wallet-SSOT).
Ersetzt die alte Fragment-Fixture (nur id/name/lvl/wallet) durch vollstaendige
Charaktere, ohne fixture_kind-Marker. Selbe Wallet-Betraege + 900+-Band wie zuvor,
damit Economy-Audit-Erwartungen (walletMin 7000 / walletMax 12000) gehalten werden.
"""
import json
from pathlib import Path

REPO = Path("/mnt/agent_share/cloud/repos/ZEITRISS-md-git")
OUT = REPO / "internal/qa/fixtures/savegame_v7_5er_hq_highlevel.json"

# Bestehende Fixture als Basis (Continuity/Logs/Campaign bleiben erhalten)
base = json.loads(OUT.read_text(encoding="utf-8"))

AGENTS = [
    ("AGENT-A", "Astra",  "ECHO",    912, 60400, "Analytik & Spurensicherung",  {"STR": 4, "GES": 7, "INT": 9, "CHA": 5, "TEMP": 6, "SYS": 5}, True),
    ("AGENT-B", "Blitz",  "STORM",   905,  6900, "CQB & Sturmangriff",          {"STR": 9, "GES": 8, "INT": 4, "CHA": 4, "TEMP": 7, "SYS": 3}, False),
    ("AGENT-C", "Cipher", "GHOST",   933,  8100, "Infiltration & Hacking",      {"STR": 4, "GES": 8, "INT": 8, "CHA": 5, "TEMP": 5, "SYS": 9}, False),
    ("AGENT-D", "Dusk",   "VEIL",    918,  7600, "Verdeckte Aufklaerung",       {"STR": 5, "GES": 7, "INT": 6, "CHA": 8, "TEMP": 6, "SYS": 4}, True),
    ("AGENT-E", "Echo",   "RELAY",   901,  7050, "Support & Feldtechnik",       {"STR": 5, "GES": 6, "INT": 7, "CHA": 6, "TEMP": 5, "SYS": 7}, False),
]

def make_char(aid, name, callsign, lvl, wallet, role, attr, has_psi):
    sys_installed = min(attr["SYS"], 6)
    lp_max = 10 + attr["STR"] + attr["TEMP"]  # plausibel, baseline 10 + STR + TEMP
    char = {
        "id": aid,
        "name": name,
        "callsign": callsign,
        "rank": "Operator IX",
        "lvl": lvl,
        "xp": 0,
        "origin": {
            "epoch": "ITI-Nullzeit",
            "hominin": "Homo sapiens sapiens",
            "role": role,
        },
        "attr": attr,
        "lp": lp_max,
        "lp_max": lp_max,
        "stress": 0,
        "has_psi": has_psi,
        "sys_installed": sys_installed,
        "talents": [
            {"name": "Veteranen-Reflex", "tier": "Meister",
             "effect": "+2 auf Initiative und Reaktionsproben."},
            {"name": "Feldroutine", "tier": "Fortgeschritten",
             "effect": "+1 auf rollentypische Proben."},
        ],
        "equipment": [
            {"name": "Standard-Dienstwaffe", "type": "weapon", "tier": 2},
            {"name": "Adaptiv-Panzerung", "type": "armor", "tier": 2},
            {"name": "Feld-Toolkit", "type": "gadget", "tier": 2},
        ],
        "implants": [
            {"name": "Neuro-Sync Mk III", "sys_cost": 1, "effect": "+1 Initiative"},
        ] if sys_installed >= 1 else [],
        "history": {
            "background": f"{name} ({callsign}) - erfahrener ITI-Operator, Rolle: {role}.",
            "milestones": ["Episode 12 abgeschlossen", "HQ-Kernteam"],
        },
        "carry": [
            {"name": "Med-Patch", "type": "consumable", "tier": 2},
            {"name": "Rauchgranate", "type": "consumable", "tier": 1},
        ],
        "quarters_stash": [
            {"name": "Ersatzmagazin", "type": "consumable", "tier": 2},
        ],
        "vehicles": {
            "epoch_vehicle": None,
            "availability": {"ready_every_missions": 4, "next_ready_in": 0},
            "legendary_temporal_ship": None,
        },
        "reputation": {"iti": 80, "fraktionen": {}},
        "wallet": wallet,
        "level_history": {
            "1": {"choice": "+1 Attribut", "detail": "Start", "mission": "MS1"},
        },
    }
    if has_psi:
        char["psi_heat"] = 0
        char["pp"] = 4
        char["psi_abilities"] = [
            {"name": "Praekognitiver Blick", "tier": "Basis",
             "effect": "Einmal pro Szene eine Probe wiederholen."}
        ]
    return char

base["characters"] = [make_char(*a) for a in AGENTS]

# economy.wallets deckungsgleich mit characters[].wallet halten
base["economy"]["wallets"] = {
    aid: {"balance": wallet, "name": name}
    for aid, name, _cs, _lvl, wallet, *_ in AGENTS
}

# arena-Pflichtblock (strict) ergaenzen, falls fehlt
base["arena"] = {
    "active": False,
    "phase": "idle",
    "queue_state": "idle",
    "mode": "none",
    "tier": 0,
    "previous_mode": None,
    "resume_token": None,
    "contract_id": None,
    "streak": 0,
    "pending_rewards": {"cu": 0, "xp": 0, "arena_rep": 0, "multiplier": 1, "risk": "low"},
    "banked_rewards": {"cu": 0, "xp": 0, "arena_rep": 0},
    "rewarded_runs_this_contract": 0,
    "first_wins": {},
    "defeated_types": [],
    "last_reward_episode": None,
    "wins_player": 0,
    "wins_opponent": 0,
    "match_policy": "standard",
}

# logs.flags strict-Pflichtfelder ergaenzen
flags = base["logs"].setdefault("flags", {})
flags.setdefault("imported_saves", [])
flags.setdefault("duplicate_branch_detected", False)
flags.setdefault("duplicate_character_detected", False)
flags.setdefault("continuity_conflicts", [])
flags.setdefault("runtime_version", "4.2.6")
flags.setdefault("chronopolis_unlocked", False)

# ui voice_profile/contrast etc. existieren bereits; sicherstellen
ui = base["ui"]
ui.setdefault("voice_profile", "gm_second_person")

# Fragment-Marker entfernen -> jetzt strict vollstaendig
base.pop("fixture_kind", None)

OUT.write_text(json.dumps(base, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("written:", OUT)
print("chars:", len(base["characters"]),
      "Σwallets:", sum(w["balance"] for w in base["economy"]["wallets"].values()))
