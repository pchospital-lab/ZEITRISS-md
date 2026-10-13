#!/usr/bin/env python3
"""
tests/mmo_sim/test_section_completion_resume_ar3_original_request_contract.py
— AR3 (01_ORIGINALREQUEST_VERTRAG.md Teile A-D, FINDINGS.json AR3-F01/F02/F03):
die GENERALREVIEW.md-bestaetigten AR2-Luecken, jetzt als dauerhafte
`assert`-Regression (dieselbe Technik wie die bestehende
`test_section_completion_resume_ar2_contract_binding.py`, hier um die drei
AR3-Funde erweitert, die review-evidence/probe_ar2_bindings.py auf dem
AR2-Kandidaten noch als falsche automatische Erfolge zeigte):

Teil A (AR3-F01): der tatsaechlich gesendete Originalinput
(`sl_log[-1]['leader_message']`) wird jetzt exakt (UTF-8-SHA256 + Zeichen-
laenge) gegen `content_sha256`/`content_chars` des gebundenen Original-
Requestdatensatzes geprueft -- `wrong_input_hash`/`changed_wire_text`/
`wrong_input_length` MUESSEN HOLDen (vorher: `success=True`, 2 neue
Reflexionsrequests, 0 GM-Calls -- GENERALREVIEW.md F01). `control_exact_input`
(echter Unicode-/Whitespace-Text) UND `empty_input_control` (eine echte LEERE
Eingabe fuer den Debrief-Turn) bleiben POSITIVE Kontrollen -- kein
`strip()`/keine Normalisierung, keine Truthiness-Ablehnung einer leeren
Eingabe.

Teil D (AR3-05): ein bekannter, eng gefasster Reader-Fehler des konkret
gebundenen Original-Requestdatensatzes (fehlender Pflichtschluessel ODER ein
falsch typisiertes Kontrollfeld) muss zu einem verstaendlichen kontrollierten
HOLD fuehren, NICHT zu einem ungefangenen Traceback im Normaleinstieg
(`missing_content_sha256`, `corrupt_turn_idx_type`).

Teil C (AR3-F02): `received_not_accounted` reproduziert GENAU die
`add_seconds`-Schreibfehler-Luecke aus GENERALREVIEW.md F02 (derselbe reale
`OSError`-Injektionspunkt wie review-evidence/probe_ar2_bindings.py) -- der
GM-Request bleibt ehrlich bei `state=received` haengen; das MUSS HOLDen
(vorher: `success=True`, 2 neue Reflexionsrequests trotz `received`).

Teil B (AR3-F03): `original_error_with_duplicate`/
`missing_exact_request_with_duplicate` reproduzieren GENAU die
Dedup-Luecke aus GENERALREVIEW.md F03 (ein zweiter, gleich lautender
Erfolgsrecord ersetzt einen fehlerhaften/fehlenden Original-Record) -- beide
MUESSEN HOLDen. `duplicate_received_coexists` ist die dazugehoerige
POSITIVKONTROLLE (AR3-03/02_ANGEBOT.md Teil B): ein legitimer, lediglich
inhaltsgleicher ALTER Record (andere ID, `state=received`) neben einer
eindeutig gebundenen, korrekten Original-ID ist KEIN pauschales
Retry-Verbot -- die automatische Recovery MUSS hier weiterhin greifen.

Pure Python, nur `assert`, echter Exitcode, kein pytest."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _section_completion_resume_fixtures import (  # noqa: E402
    COMPLETION_MARKER, ExplodingDriver, ExplodingGmTransport, ReflectionOnlyDriver,
    ScriptedDriver, StopAfterResponseGmTransport, build_two_member_table, clear_lab_stop,
    debrief_with_marker, harvest_extractor, make_env, save_block,
)

import mmo_sim.core.request_ledger as request_ledger  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.core.runtime import SectionRuntime  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402


def _pause_right_after_marker_response(env, lobby, table, ps_store, section_id: str, debrief_request_text: str):
    """Wie `test_section_completion_resume_ar2_contract_binding.py`s gleich-
    namiger Helfer, hier mit einem vom Aufrufer waehlbaren Debrief-Anfrage-
    Text (AR3 Teil A: eine ECHTE leere Eingabe muss ein normaler, positiver
    Fall bleiben koennen, keine Truthiness-Ablehnung)."""
    leader_save = save_block("chrono-leader")
    guest_save = save_block("chrono-guest")
    debrief = debrief_with_marker({"chrono-leader": leader_save, "chrono-guest": guest_save})
    gm = StopAfterResponseGmTransport(
        ["SL-Antwort Anker.", "SL-Antwort Gast-Import.", debrief], run_dir=env.run_dir,
        reason="AR3-original-request-contract: Pause nach Markerantwort.",
    )
    leader_driver = ScriptedDriver([
        ParticipantDecision(text="Anker: ä/ö/ü, echte Unicode-Eingabe.\n  ", save_payload=leader_save, origin_source="fake:leader"),
        ParticipantDecision(text=debrief_request_text, origin_source="fake:leader-debrief"),
    ])
    guest_driver = ScriptedDriver([
        ParticipantDecision(text="Gast-Import.", save_payload=guest_save, origin_source="fake:guest"),
    ])
    controller = TableController(leader_key="leader_pk", drivers={"leader_pk": leader_driver, "guest_pk": guest_driver})
    runtime = SectionRuntime(
        lobby=lobby, table=table, gm_transport=gm, marker=COMPLETION_MARKER,
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        harvest_extractor=harvest_extractor,
    )
    outcome = runtime.run_full_section(
        controller, section_id,
        contexts_by_persona={"leader_pk": {"user": "ctx"}, "guest_pk": {"user": "ctx"}},
        states_dir=env.states_dir, today="2026-10-13", ts="2026-10-13T07:00:00",
    )
    assert not outcome.completion.success
    assert "Admission-Gate blockiert" in outcome.completion.reason, outcome.completion.reason
    return leader_save, guest_save, debrief


def _gm_request_path_for_turn(run_dir: Path, turn_idx: int) -> Path:
    candidates = [
        p for p in (run_dir / "requests").glob("*.json")
        if (lambda d: d.get("role") == "gm_turn" and d.get("turn_idx") == turn_idx)(
            json.loads(p.read_text(encoding="utf-8"))
        )
    ]
    assert len(candidates) == 1, (turn_idx, candidates)
    return candidates[0]


def _resume_and_assert(env, lobby, table, ps_store, section_id: str, case_name: str, expect_success: bool):
    clear_lab_stop(env.run_dir)
    reloaded = store.Table.load(env.run_dir, table.table_id)
    if expect_success:
        controller2 = TableController(leader_key="leader_pk", drivers={
            "leader_pk": ReflectionOnlyDriver("Reflexion Leader.", "fake:leader-reflect"),
            "guest_pk": ReflectionOnlyDriver("Reflexion Gast.", "fake:guest-reflect"),
        })
    else:
        controller2 = TableController(leader_key="leader_pk", drivers={
            "leader_pk": ExplodingDriver(f"leader-{case_name}"),
            "guest_pk": ExplodingDriver(f"guest-{case_name}"),
        })
    runtime2 = SectionRuntime(
        lobby=lobby, table=reloaded, gm_transport=ExplodingGmTransport(),
        marker=COMPLETION_MARKER, harvest_validator=ZeitrissHarvestValidator(),
        persona_state_store=ps_store, harvest_extractor=harvest_extractor,
    )
    outcome2 = runtime2.run_full_section(
        controller2, section_id,
        contexts_by_persona={"leader_pk": {"user": "ctx"}, "guest_pk": {"user": "ctx"}},
        states_dir=env.states_dir, today="2026-10-13", ts="2026-10-13T07:05:00",
    )
    if expect_success:
        assert outcome2.completion.success, outcome2.completion.reason
        assert set(outcome2.completion.members_completed) == {"leader_pk", "guest_pk"}
    else:
        assert not outcome2.completion.success, (
            f"AR3: Fall {case_name!r} MUSS kontrolliert HOLDen (kein Ernte/Finalisierung) -- "
            f"reason={outcome2.completion.reason!r}"
        )
        assert store.open_completion_order_for_table(env.run_dir, table.table_id) is None, (
            f"Fall {case_name!r}: HOLD darf keinen Completion-Plan pinnen."
        )
    return outcome2


def _case(case_name: str) -> None:
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id=f"t-ar3-{case_name}")
        write_test_profile(env.run_dir)
        section_id = f"section-ar3-{case_name}"

        debrief_text = "" if case_name == "empty_input_control" else "Debrief-Anfrage: ä/ö/ü, Tab\t, Zeilenumbruch.\n  "

        if case_name == "received_not_accounted":
            # AR3-F02 (GENERALREVIEW.md): echte Injektion GENAU am bestehenden
            # `add_seconds`-Schreibpunkt (derselbe Mechanismus wie
            # review-evidence/probe_ar2_bindings.py) -- der GM-Request bleibt
            # ehrlich `state=received` haengen, `finish_received` propagiert
            # den `OSError` ungefangen (G3-Fix, request_ledger.py bleibt
            # dabei vollstaendig UNVERAENDERT, nur eine temporaere Testpatch).
            original_add_seconds = request_ledger.add_seconds

            def _fail_add_seconds(run_dir_arg, rid, seconds):
                # NUR der GM-Turn-Request, der die Markerantwort traegt (der
                # erste `finish_received`-Write hat `result_text` bereits
                # gesetzt, BEVOR `add_seconds` aufgerufen wird) -- die
                # vorgelagerten Anker-/Gast-Import-Turns (gleiche
                # `section_id`, aber keine Markerantwort) muessen ganz
                # normal durchlaufen, sonst stuerzte der Lauf am falschen
                # Fenster ab.
                rec = request_ledger.load_request(run_dir_arg, rid)
                if (
                    rec is not None and rec.get("role") == "gm_turn"
                    and rec.get("section_id") == section_id
                    and COMPLETION_MARKER in (rec.get("result_text") or "")
                ):
                    raise OSError("synthetic write failure before duration accounting (AR3-F02)")
                return original_add_seconds(run_dir_arg, rid, seconds)

            request_ledger.add_seconds = _fail_add_seconds
            try:
                try:
                    _pause_right_after_marker_response(env, lobby, table, ps_store, section_id, debrief_text)
                    raise AssertionError("Testaufbau: OSError-Injektion hat nicht gegriffen.")
                except OSError:
                    pass
            finally:
                request_ledger.add_seconds = original_add_seconds

            table_path = env.run_dir / "tables" / f"{table.table_id}.json"
            table_data = json.loads(table_path.read_text(encoding="utf-8"))
            marker_turn_idx = table_data["sl_log"][-1]["turn_idx"]
            gm_request_path = _gm_request_path_for_turn(env.run_dir, marker_turn_idx)
            req = json.loads(gm_request_path.read_text(encoding="utf-8"))
            assert req["state"] == "received", req
            assert req.get("error") is None
            assert req.get("result_text") == table_data["sl_log"][-1]["content"], (
                "Vorbedingung: der erste finish_received-Write (state=received) bindet "
                "result_text bereits, nur die Dauer-/Kostennachbuchung ist offen."
            )
            # Kein Admission-Gate-Stop in diesem Zweig (der Absturz lag VOR
            # jedem Gate-Check) -- direkt fortsetzen.
            _resume_and_assert(env, lobby, table, ps_store, section_id, case_name, expect_success=False)
            return

        leader_save, guest_save, debrief = _pause_right_after_marker_response(
            env, lobby, table, ps_store, section_id, debrief_text,
        )
        table_path = env.run_dir / "tables" / f"{table.table_id}.json"
        table_data = json.loads(table_path.read_text(encoding="utf-8"))
        assert len(table_data["sl_log"]) == 3, table_data["sl_log"]
        marker_entry = table_data["sl_log"][-1]
        assert marker_entry.get("gm_request_id"), "AR3 Teil B: die Original-ID muss additiv im sl_log-Eintrag stehen."
        marker_turn_idx = marker_entry["turn_idx"]
        gm_request_path = _gm_request_path_for_turn(env.run_dir, marker_turn_idx)
        req = json.loads(gm_request_path.read_text(encoding="utf-8"))
        assert req["id"] == marker_entry["gm_request_id"]
        assert req["state"] == "accounted" and req.get("error") is None
        assert req.get("result_text") == marker_entry["content"]
        exact_hash_before = __import__("hashlib").sha256(marker_entry["leader_message"].encode("utf-8")).hexdigest()
        assert req["content_sha256"] == exact_hash_before
        assert req["content_chars"] == len(marker_entry["leader_message"])

        expect_success = case_name in ("control_exact_input", "empty_input_control", "duplicate_received_coexists")

        if case_name in ("control_exact_input", "empty_input_control"):
            pass
        elif case_name == "wrong_input_hash":
            req["content_sha256"] = "0" * 64
        elif case_name == "changed_wire_text":
            table_data["sl_log"][-1]["leader_message"] += " CHANGED"
        elif case_name == "wrong_input_length":
            req["content_chars"] += 1
        elif case_name == "missing_content_sha256":
            del req["content_sha256"]
        elif case_name == "corrupt_turn_idx_type":
            req["turn_idx"] = str(req["turn_idx"])
        elif case_name == "original_error_with_duplicate":
            dup = copy.deepcopy(req)
            dup["id"] = "1" * 32
            dup["reserved_ts"] = dup["reserved_ts"] + 100
            (gm_request_path.parent / (dup["id"] + ".json")).write_text(
                json.dumps(dup, ensure_ascii=False), encoding="utf-8",
            )
            req["error"] = "synthetic original error (AR3-F03)"
        elif case_name == "missing_exact_request_with_duplicate":
            dup = copy.deepcopy(req)
            dup["id"] = "2" * 32
            dup["reserved_ts"] = dup["reserved_ts"] + 100
            (gm_request_path.parent / (dup["id"] + ".json")).write_text(
                json.dumps(dup, ensure_ascii=False), encoding="utf-8",
            )
            gm_request_path.unlink()
        elif case_name == "duplicate_received_coexists":
            dup = copy.deepcopy(req)
            dup["id"] = "3" * 32
            dup["reserved_ts"] = dup["reserved_ts"] + 100
            dup["state"] = "received"
            (gm_request_path.parent / (dup["id"] + ".json")).write_text(
                json.dumps(dup, ensure_ascii=False), encoding="utf-8",
            )
        else:
            raise AssertionError(f"unbekannter Fall: {case_name}")

        table_path.write_text(json.dumps(table_data, ensure_ascii=False), encoding="utf-8")
        if gm_request_path.exists():
            gm_request_path.write_text(json.dumps(req, ensure_ascii=False), encoding="utf-8")

        _resume_and_assert(env, lobby, table, ps_store, section_id, case_name, expect_success=expect_success)


def main() -> int:
    cases = (
        "control_exact_input", "empty_input_control",
        "wrong_input_hash", "changed_wire_text", "wrong_input_length",
        "missing_content_sha256", "corrupt_turn_idx_type",
        "received_not_accounted",
        "original_error_with_duplicate", "missing_exact_request_with_duplicate",
        "duplicate_received_coexists",
    )
    failed = 0
    for name in cases:
        try:
            _case(name)
            print(f"OK   case_{name}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL case_{name}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR case_{name}:")
            traceback.print_exc()
    total = len(cases)
    print(f"\n{total - failed}/{total} Faelle bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
