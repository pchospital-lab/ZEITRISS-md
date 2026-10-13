#!/usr/bin/env python3
"""
tests/mmo_sim/test_r12_binding_lifecycle_two_process_window_resume.py —
R12-W77: F02-LIFECYCLE-Fix, 01_BINDUNGSERHALT.md §A, CASES.json
L02-WINDOW ("Two real processes").

Reproduziert GENERALREVIEW.md §3 "Eigene echte Zweiprozessprobe" --
Prozess 1 beginnt eine konkrete Figur bei GESCHLOSSENEM synthetischem
Fenster (kein Transport, `window_paused`, das gebundene Dict ist
vorhanden). Prozess 2 (ein ECHTER, separater OS-Prozess via `subprocess`,
NICHT nur ein zweiter Funktionsaufruf im selben Interpreter) oeffnet das
Testfenster und erhaelt ERST die widerspruechliche Antwort, DANN eine
umbenannte Einzelantwort -- die Identitaet (der durabel gebundene
Originalentwurf) MUSS den Prozesswechsel UND den Konflikt ueberleben:
`accepted` darf NICHT eintreten, die umbenannte Antwort bleibt
`unjustified_semantic_drift`-HOLD.

Dies ist eine STRENGERE Variante von
`test_r12_binding_lifecycle_conflict_preserves_binding.py` (dort: ein
Funktionsaufruf, derselbe Interpreterprozess) -- hier mit einer echten
Prozessgrenze dazwischen, exakt wie GENERALREVIEW.md sie zusaetzlich zu
C38s ADV2 (zwei Aufrufe, kein Prozesswechsel) verlangt.

Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _r12_provenance_close_fixture import wallet_as_number  # noqa: E402
from _r12_window_hold_fixture import close_window, open_window  # noqa: E402

import mmo_sim.core.save_correction as save_correction  # noqa: E402
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402

ROLE_CREATION = save_correction_domain.ROLE_CREATION

_PROCESS_2_SCRIPT = r"""
import json, sys
sys.path.insert(0, {repo_root!r})
import mmo_sim.core.save_correction as save_correction
from mmo_sim.domain.zeitriss import save_correction as save_correction_domain
from mmo_sim.core import save_correction as _sc  # noqa: F401


class _ScriptedGm2:
    def __init__(self, contents):
        self._contents = list(contents)
        self.calls = []

    def turn(self, turn_idx, text, **kwargs):
        self.calls.append((turn_idx, text))
        return {{
            "content": self._contents.pop(0), "usage": {{}}, "sources": [], "latency_s": 0.0,
            "chat_id": "fake",
        }}


def _full_v7(char_id, name):
    character = {{
        "id": char_id, "name": name, "callsign": name.upper(), "rank": "Rookie",
        "lvl": 1, "xp": 0, "origin": {{}}, "attr": {{}}, "lp": 10, "lp_max": 10,
        "stress": 0, "has_psi": False, "sys_installed": 0, "talents": [], "equipment": [],
        "implants": [], "history": {{}}, "carry": [], "quarters_stash": [], "vehicles": {{}},
        "reputation": {{}}, "wallet": 0.0, "level_history": {{}},
    }}
    return {{
        "v": 7, "zr": "fixture", "save_id": "fixture-" + char_id,
        "parent_save_id": None, "merge_id": None, "branch_id": "main",
        "campaign": {{
            "episode": 1, "mission": 1, "px": 0, "px_state": "stable", "mode": "mixed",
            "rift_seeds": [], "entry_choice_skipped": False, "episode_start": None, "episode_end": None,
        }},
        "characters": [character], "economy": {{}},
        "logs": {{
            "trace": [], "arena_psi": [], "psi": [], "hud": [], "market": [], "artifact_log": [],
            "notes": [],
            "flags": {{
                "runtime_version": "fixture", "chronopolis_unlocked": False, "imported_saves": [],
                "duplicate_branch_detected": False, "duplicate_character_detected": False,
                "continuity_conflicts": [],
            }},
        }},
        "summaries": {{"summary_last_episode": "", "summary_last_rift": "", "summary_active_arcs": ""}},
        "continuity": {{
            "last_seen": {{"mode": "hq", "episode": 1, "mission": 1, "location": "fixture"}},
            "split": {{}}, "roster_echoes": [], "shared_echoes": [], "convergence_tags": [],
            "npc_roster": [], "active_npc_ids": [],
        }},
        "arc": {{"factions": {{}}, "questions": [], "hooks": []}},
        "ui": {{
            "gm_style": "fixture", "suggest_mode": False, "action_mode": "uncut", "contrast": "fixture",
            "badge_density": "fixture", "output_pace": "fixture", "voice_profile": "fixture",
            "intro_seen": False, "dice": {{"debug_rolls": False}},
        }},
        "arena": {{
            "active": False, "phase": "idle", "queue_state": "idle", "mode": "none", "tier": 0,
            "previous_mode": None, "resume_token": None, "contract_id": None, "streak": 0,
            "pending_rewards": {{"cu": 0, "xp": 0, "arena_rep": 0, "multiplier": 1, "risk": "none"}},
            "banked_rewards": {{"cu": 0, "xp": 0, "arena_rep": 0}},
            "rewarded_runs_this_contract": 0, "first_wins": {{}}, "defeated_types": [],
            "last_reward_episode": None, "wins_player": 0, "wins_opponent": 0, "match_policy": "none",
        }},
    }}


def _ambiguous_text(char_id):
    a = _full_v7(char_id, "Konflikt A")
    b = _full_v7(char_id, "Konflikt B")
    return "```json\n" + json.dumps(a) + "\n```\n```json\n" + json.dumps(b) + "\n```"


run_dir = {run_dir!r}
participant_id, char_id = {participant_id!r}, {char_id!r}
candidate_block = json.loads({candidate_block_json!r})

gm = _ScriptedGm2([
    _ambiguous_text(char_id),
    "```json\n" + json.dumps(_full_v7(char_id, "Changed Testfigur")) + "\n```",
])
outcome = save_correction.pursue_single_figure_correction(
    run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
    candidate_block=candidate_block, gm_transport=gm,
)
print(json.dumps({{"status": outcome.status, "reason": outcome.reason, "calls": len(gm.calls)}}))
"""


def test_two_real_processes_window_pause_then_conflict_then_rename_stays_protected():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        participant_id, char_id = "w77_twoproc", "CHR-77-TWOPROC"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

        original_draft = wallet_as_number(char_id, name="Original Testfigur")

        # Prozess 1 (dieser Interpreter): Fenster geschlossen -- kein
        # Transport, `window_paused`, das gebundene Dict ist vorhanden.
        class _ExplodingGm:
            def __init__(self):
                self.calls = []

            def turn(self, turn_idx, text, **kwargs):
                self.calls.append((turn_idx, text))
                raise AssertionError("kein Transport-Call erwartet -- Fenster ist geschlossen.")

        close_window(run_dir, deadline=1.0)
        gm1 = _ExplodingGm()
        outcome1 = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=original_draft, gm_transport=gm1,
        )
        assert outcome1.status == "hold", outcome1
        assert gm1.calls == [], gm1.calls
        record1 = save_correction.load_record(run_dir, repair_key)
        assert record1["state"] == "window_paused" and record1["bound_block"] == original_draft, record1

        # Fenster oeffnen (naechster Lab-Zyklus) -- dann Prozess 2 als ECHTER
        # separater OS-Prozess starten, der ERST die Konfliktantwort, DANN
        # die umbenannte Antwort erhaelt.
        open_window(run_dir)
        script = _PROCESS_2_SCRIPT.format(
            repo_root=str(_REPO_ROOT), run_dir=str(run_dir), participant_id=participant_id,
            char_id=char_id, candidate_block_json=json.dumps(original_draft),
        )
        env = dict(os.environ)
        env["PYTHONPATH"] = str(_REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
        result = subprocess.run(
            [sys.executable, "-c", script], env=env, capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0, (
            f"Prozess 2 (echter subprocess) muss rc0 liefern -- stdout={result.stdout!r} "
            f"stderr={result.stderr!r}"
        )
        payload = json.loads(result.stdout.strip().splitlines()[-1])
        assert payload["status"] == "hold" and payload["reason"] == "unjustified_semantic_drift", (
            f"R12-W77 L02-WINDOW: die Identitaet MUSS einen echten Prozesswechsel UND einen "
            f"Konflikt ueberleben -- die umbenannte Antwort darf NICHT 'accepted' werden -- {payload}"
        )
        assert payload["calls"] == 2, payload

        record2 = save_correction.load_record(run_dir, repair_key)
        assert record2["state"] == "hold", record2


def _run_all() -> int:
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in fns:
        try:
            fn()
            print(f"OK   {fn.__name__}")
            passed += 1
        except AssertionError:
            print(f"FAIL {fn.__name__}")
            traceback.print_exc()
        except Exception:
            print(f"ERROR {fn.__name__}")
            traceback.print_exc()
    print(f"\n{passed}/{len(fns)} passed")
    return 0 if passed == len(fns) else 1


if __name__ == "__main__":
    raise SystemExit(_run_all())
