#!/usr/bin/env python3
"""
tests/mmo_sim/_r5_t1d_fresh_process_resume.py -- Kind-Skript fuer
`drive_r5_t1d_evidence_2026_11_05.py` (ZR-BETREIBER-GASTERSCHAFFUNG-
20261105-R5, Phase `t1t2`, Teilauftrag T1d-Nachbau).

Wird NIEMALS importiert -- ausschliesslich als eigenstaendiges Argument an
`subprocess.run([sys.executable, __file__, ...])` aus dem Treiber uebergeben
(ECHTER, frisch gestarteter OS-Interpreter-Subprozess, kein In-Process-
Funktionsaufruf, kein `-c`-String). Laedt den vom Treiber (Phase A, darf
In-Process sein) persistierten `run_dir` eines Tisches zurueck, bei dem eine
Gruppen-Korrekturrunde NEU eroeffnet (`_group_rounds/<tisch>__<section>.
open.json` persistiert), der Versand transportseitig fehlgeschlagen
(`finish_error` -> `state=accounted`, `error` gesetzt) UND der Prozess GENAU
DANACH, aber VOR `mark_hold`/`_clear_open_round`, hart abgebrochen ist
(Phase A im Treiber) -- der Marker UND der Korrekturdatensatz des
betroffenen Mitglieds blieben dadurch unveraendert offen liegen.

Dieses Kind-Skript ruft NICHT direkt `save_correction.pursue_group_save_
correction` auf (das haette die belegte Luecke aus 01-PRODUCT-REVIEW.md
NICHT geschlossen, s. `test_r4_duo_open_group_correction_resume_2026_10_28.
py`-Moduldocstring) -- es konstruiert stattdessen GENAU denselben normalen
Aufrufer wie `ui/tui.py`/`core/lobby_flow.py`: `core.app_service.
run_play_session` (Zeile s. Aufruf unten). `run_full_section` prueft VOR
jedem neuen Spielzug `save_correction.has_open_group_round(...)` (`core/
runtime.py:1153`) und dispatcht bei Treffer OHNE neuen GM-/Persona-Turn
direkt in den Resume-/Korrekturzweig (`finalize("", resume_section_id=...)`
-> `store.complete_section` -> `save_correction.pursue_group_save_
correction`) -- exakt der Pfad, den dieses Skript aus einem WIRKLICH neuen
Interpreter heraus erreichen muss.

Der vorangegangene Transportfehler (`accounted` MIT `error`, s.o.) macht
diese Rundenidentitaet fuer `find_durable_result`/`find_answered_without_
text` unsichtbar (identische Ausgangslage zu `test_r12_window_resume_
boundary_group.py:test_g_...`) -- die Runde wird deshalb terminal
(`unresolved_prior_round_outcome`-HOLD), OHNE einen zweiten Transport-/
GM-Call: der `_ExplodingGm`-Transport unten wirft eine `AssertionError`,
FALLS er doch erreicht wuerde (Testversagen, kein stiller Fallback) -- die
`controller`-Treiber ("sollte nie aufgerufen werden") ebenso.

Druckt GENAU EIN JSON-Objekt als letzte stdout-Zeile (vom Treiber ueber
`last_json`-Muster geparst) -- Pure Python, nur `assert`, echter
Prozess-Exitcode (0 = Resume-Erwartung erfuellt, != 0 = Traceback in
stderr)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _section_completion_resume_fixtures import ReflectionOnlyDriver  # noqa: E402

import mmo_sim.core.request_ledger as ledger  # noqa: E402
import mmo_sim.core.save_correction as sc  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.core import app_service  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import save_correction as domain  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER, ZeitrissHarvestValidator  # noqa: E402

ROLE_GROUP = domain.ROLE_GROUP


class _ExplodingGm:
    """KEIN Transport-Call erwartet -- die vorangegangene Runde ist (wegen
    des terminalen `accounted`+`error`-Requestdatensatzes, s. Moduldocstring)
    `unresolved_prior_round_outcome`, nicht neu versendbar."""

    def __init__(self):
        self.calls = []

    def turn(self, turn_idx, text, **kwargs):
        self.calls.append((turn_idx, text))
        raise AssertionError(
            "FRESH-PROCESS-RESUME: kein zweiter Transport-/GM-Call erwartet -- "
            "die Runde muss ueber den vorangegangenen terminalen Requestdatensatz "
            "direkt HOLD werden."
        )


def main() -> int:
    run_dir = Path(sys.argv[1])
    states_dir = Path(sys.argv[2])
    schema_path = Path(sys.argv[3])
    table_id = sys.argv[4]
    section_id = sys.argv[5]
    today = sys.argv[6]
    ts = sys.argv[7]
    guest_char_id = sys.argv[8]

    assert run_dir.is_dir(), f"run_dir fehlt im frischen Prozess: {run_dir}"
    assert schema_path.is_file(), f"schema_path fehlt im frischen Prozess: {schema_path}"

    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    lobby = store.Lobby(run_dir, table_size_policy=_table_size_policy())
    table2 = store.Table.load(run_dir, table_id)

    group_repair_key = domain.group_repair_key(table_id, section_id, guest_char_id)
    open_round_path = sc._open_round_path(run_dir, table_id, section_id)
    member_before = sc.load_record(run_dir, group_repair_key)
    group_records_before = len([r for r in ledger._all_records(run_dir) if r.get("role") == ROLE_GROUP])

    gm2 = _ExplodingGm()
    controller2 = TableController(leader_key="leader_pk", drivers={
        "leader_pk": ReflectionOnlyDriver("sollte nie aufgerufen werden", "fake:leader-noop"),
        "guest_pk": ReflectionOnlyDriver("sollte nie aufgerufen werden", "fake:guest-noop"),
    })
    contexts_by_persona = {"leader_pk": {"user": "ctx-leader_pk"}, "guest_pk": {"user": "ctx-guest_pk"}}

    # === DER NORMALE RECOVERY-AUFRUFER (derselbe Weg wie `ui/tui.py`/
    # `core/lobby_flow.py`), hier aus einem WIRKLICH neuen Interpreter-
    # Subprozess heraus aufgerufen -- NICHT `save_correction.pursue_group_
    # save_correction` direkt. ===
    outcome2 = app_service.run_play_session(
        lobby, table2, gm2, controller2, section_id, contexts_by_persona,
        states_dir, today, ts, COMPLETION_MARKER, ZeitrissHarvestValidator(),
        ps_store, zeitriss_saves.harvest_from_debrief, max_turns=5,
    )

    member_after = sc.load_record(run_dir, group_repair_key)
    group_records_after = len([r for r in ledger._all_records(run_dir) if r.get("role") == ROLE_GROUP])

    result = {
        "pid": __import__("os").getpid(),
        "executable": sys.executable,
        "completion_success": outcome2.completion.success,
        "completion_missing": outcome2.completion.missing,
        "completion_reason": outcome2.completion.reason,
        "gm_calls": len(gm2.calls),
        "open_round_marker_present_after": open_round_path.exists(),
        "member_state_before": member_before.get("state") if member_before else None,
        "member_state_after": member_after.get("state") if member_after else None,
        "member_reason_after": member_after.get("last_reason") if member_after else None,
        "group_records_before": group_records_before,
        "group_records_after": group_records_after,
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0


def _table_size_policy():
    from mmo_sim.domain.zeitriss.policy import ZeitrissTableSizePolicy
    return ZeitrissTableSizePolicy()


if __name__ == "__main__":
    try:
        rc = main()
    except AssertionError as exc:
        print(json.dumps({"error": "AssertionError", "detail": str(exc)}))
        rc = 1
    except Exception:
        import traceback
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
