#!/usr/bin/env python3
"""
tests/mmo_sim/drive_r5_t1d_evidence_2026_11_05.py -- ZR-BETREIBER-
GASTERSCHAFFUNG-20261105-R5, Phase `t1t2`, T1d-Nachbau (briefing/t1d.md):
der fehlende Nachweis, der ALLE DREI Dimensionen zugleich traegt, die kein
bestehender Einzeltest zusammen zeigt:

  (1) ein offener, abgebrochener Gruppen-Korrekturstand
      (`_group_rounds/<tisch>__<section>.open.json` offen, Mitglieds-
      Korrekturdatensatz NICHT terminalisiert) -- wie `test_r12_window_
      resume_boundary_group.py` herstellt,
  (2) erreicht + terminalisiert ueber den NORMALEN Recovery-Aufrufer
      `core.app_service.run_play_session` (derselbe Weg wie `ui/tui.py`/
      `core/lobby_flow.py`), NICHT ueber einen isolierten `pursue_group_
      save_correction`-Aufruf -- wie `test_r4_duo_open_group_correction_
      resume_2026_10_28.py` fordert,
  (3) in einem WIRKLICH neu gestarteten OS-Prozess (`subprocess.run([sys.
      executable, ...])`, echter Prozess-Exitcode), NICHT nur ein zweiter
      Funktionsaufruf im selben Interpreter -- wie `test_r12_binding_
      lifecycle_two_process_window_resume.py`/`e2e_real_subprocess_dialog.
      py` zeigen.

PHASE A (dieses Skript, darf In-Process sein, s. Briefing): baut Lobby +
Zweiermitglieds-Tisch, seedet eine fehlende/schema-ungueltige Gastfigur
(`guest_pk`), eroeffnet ueber `save_correction.pursue_group_save_correction`
GENAU EINE Gruppenkorrekturrunde fuer das fehlende Mitglied -- der
Transport wirft synthetisch einen rohen Transportfehler (`TimeoutError`,
identisches Muster zu `test_r12_window_resume_boundary_group.py`), DANACH
(aber VOR `mark_hold`/`_clear_open_round`) injiziert ein monkeypatchter
`sc.mark_hold` einen harten `SystemExit(73)` -- der `_open_round`-Marker
UND der Mitglieds-Korrekturdatensatz bleiben dadurch unveraendert OFFEN
liegen (`state=correction_pending`), GENAU EIN Gruppen-Ledger-Datensatz
(`accounted` MIT `error`) ist persistiert.

PHASE B (`_r5_t1d_fresh_process_resume.py`, ECHTER Subprozess): startet
einen WIRKLICH neuen `sys.executable`-Prozess gegen DENSELBEN persistierten
`run_dir`, der `app_service.run_play_session` normal aufruft. `run_full_
section` erkennt den offenen Marker VOR jedem neuen Spielzug (`core/
runtime.py:1153`, `save_correction.has_open_group_round`) und dispatcht
direkt in den Resume-/Korrekturzweig -- der bereits terminale (`accounted`+
`error`) Requestdatensatz derselben Rundenidentitaet macht die Runde fuer
`find_durable_result`/`find_answered_without_text` unsichtbar (identische
Ausgangslage zu `test_r12_window_resume_boundary_group.py:test_g_...`):
KEIN zweiter Transport-/GM-Call, das Mitglied wird terminal `state=hold`/
`last_reason=unresolved_prior_round_outcome`, der Marker wird geloescht --
GENAU EIN Gruppen-Ledger-Datensatz bleibt bestehen (kein zweiter).

Exportiert alle Pflicht-Belege (Vorher-/Nachher-Koerper je `{path, sha256,
bytes}`, Kind-stdout/stderr, vollstaendige `run_dir`-Schnappschuesse,
MANIFEST) nach `t1d/evidence/` (feste Lieferzieladresse, s. briefing/
t1d.md). Pure Python, nur `assert`, echter Treiber-Exitcode."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402
from _r12_provenance_close_fixture import wallet_as_number  # noqa: E402

import mmo_sim.core.request_ledger as ledger  # noqa: E402
import mmo_sim.core.save_correction as sc  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import save_correction as domain  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy  # noqa: E402

ROLE_GROUP = domain.ROLE_GROUP
_RESULTS_ROOT = Path("/home/altair/zr-betreiber-gast-20261105/r5/t1t2/t1d/evidence")
_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)
_MANIFEST: list[dict] = []


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _export_file(src: Path, relname: str) -> dict:
    dst = _RESULTS_ROOT / relname
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    record = {"path": relname, "sha256": _sha256(dst), "bytes": dst.stat().st_size}
    _MANIFEST.append(record)
    return record


def _export_text(relname: str, text: str) -> dict:
    dst = _RESULTS_ROOT / relname
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")
    record = {"path": relname, "sha256": _sha256(dst), "bytes": dst.stat().st_size}
    _MANIFEST.append(record)
    return record


def _export_json(relname: str, data) -> dict:
    return _export_text(relname, json.dumps(data, ensure_ascii=False, indent=2, default=str))


def _export_tree(root: Path, rel_prefix: str) -> None:
    if not root.is_dir():
        return
    for p in sorted(root.rglob("*")):
        if p.is_file():
            rel = p.relative_to(root)
            _export_file(p, f"{rel_prefix}/{rel.as_posix()}")


def _seed(ps_store: PersonaStateStore, states_dir: Path, pk: str, char_id: str) -> None:
    ps_store.save_state(pk, {
        "v": 2, "persona_key": pk, "rounds_played": 0,
        "plays_char": {"character_id": char_id, "name": "Test"},
    }, states_dir=states_dir)


def main() -> int:
    _RESULTS_ROOT.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="r5_t1d_") as td:
        root = Path(td)
        run_dir = root / "run"
        states_dir = root / "states"
        schema_path = root / "schema.json"
        table_id = "t-r5-t1d-freshresume"
        section_id = "section-r5-t1d"
        today = "2026-11-05"
        ts = "2026-11-05T09:00:00"
        leader_char_id = "chrono-r5t1d-leader"
        guest_char_id = "chrono-r5t1d-guest"
        cid_to_pk = {leader_char_id: "leader_pk", guest_char_id: "guest_pk"}

        # ── Phase A, Teil 1: normaler Tischaufbau (darf In-Process sein). ──
        write_test_profile(run_dir)
        states_dir.mkdir(parents=True, exist_ok=True)
        schema_path.write_text(_SCHEMA, encoding="utf-8")
        ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
        _seed(ps_store, states_dir, "leader_pk", leader_char_id)
        _seed(ps_store, states_dir, "guest_pk", guest_char_id)

        lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        lobby.join("leader_pk")
        lobby.join("guest_pk")
        table, derivation = store.create_table_from_offer_log(
            lobby, table_id,
            offer_log_events=[
                {"type": "offer", "id": "o1", "from": "leader_pk", "wants": ["guest_pk"]},
                {"type": "consent", "offer_id": "o1", "from": "guest_pk", "accept": True},
            ],
            chrononaut_ids={"leader_pk": leader_char_id, "guest_pk": guest_char_id},
        )
        assert table is not None, f"PHASE A: Tisch haette entstehen muessen: {derivation}"

        guest_invalid = wallet_as_number(guest_char_id, name="Guest")
        leader_valid = full_v7_save(leader_char_id, name="Leader")
        harvested = {"leader_pk": leader_valid, "guest_pk": guest_invalid}
        harvest_completion = store.complete_section(
            lobby, table, section_id, harvested, states_dir, today, ZeitrissHarvestValidator(), ps_store,
        )
        assert not harvest_completion.success and harvest_completion.missing == ["guest_pk"], (
            f"PHASE A: Setup-Erwartung (nur 'guest_pk' fehlt) nicht erfuellt: {harvest_completion}"
        )

        group_repair_key = domain.group_repair_key(table.table_id, section_id, guest_char_id)
        open_round_path = sc._open_round_path(run_dir, table.table_id, section_id)

        # ── Phase A, Teil 2: offener, abgebrochener Gruppen-Korrekturstand
        # (identisches Muster zu `test_r12_window_resume_boundary_group.py`/
        # `test_r4_duo_open_group_correction_resume_2026_10_28.py` Variante
        # c): ein roher Transportfehler wird `accounted`+`error` verbucht,
        # DANACH crasht der injizierte `mark_hold` HART, VOR `_clear_open_
        # round` -- Marker UND Mitgliedsdatensatz bleiben offen liegen. ──
        class _TransportFailsGm:
            def __init__(self):
                self.calls = []

            def turn(self, turn_idx, text, **kwargs):
                self.calls.append(turn_idx)
                raise TimeoutError("SYNTHETIC_R5_T1D_TRANSPORT_FAILURE")

        def _crash(*_a, **_kw):
            raise SystemExit(73)

        original_mark_hold = sc.mark_hold
        sc.mark_hold = _crash
        try:
            gm1 = _TransportFailsGm()
            try:
                sc.pursue_group_save_correction(
                    lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
                    harvest_completion=harvest_completion, states_dir=states_dir, today=today,
                    harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
                    gm_transport=gm1, cid_to_pk=cid_to_pk, harvest_extractor=None,
                )
                raise AssertionError("PHASE A: Absturzpunkt (injizierter mark_hold-Crash) nicht erreicht.")
            except SystemExit as exc:
                assert exc.code == 73, f"PHASE A: unerwarteter Exitcode des injizierten Crashs: {exc.code}"
        finally:
            sc.mark_hold = original_mark_hold

        assert open_round_path.exists(), (
            "PHASE A Pflicht-Beleg (1): der offene Gruppenkorrekturmarker muss nach dem injizierten "
            "Crash erhalten bleiben."
        )
        member_before = sc.load_record(run_dir, group_repair_key)
        assert member_before is not None and member_before["state"] == "correction_pending", (
            f"PHASE A: Mitglieds-Korrekturdatensatz nicht im erwarteten offenen Zustand: {member_before}"
        )
        group_records_before = len([r for r in ledger._all_records(run_dir) if r.get("role") == ROLE_GROUP])
        assert group_records_before == 1, (
            f"PHASE A: erwartet GENAU EIN Gruppen-Ledger-Datensatz nach dem Setup: {group_records_before}"
        )

        # ── Pflicht-Beleg: Zwischenkoerper VOR Recovery sichern. ──
        before_marker = _export_file(open_round_path, "before/group_round_open_marker.json")
        before_member = _export_file(sc._record_path(run_dir, group_repair_key), "before/member_correction_record.json")
        _export_tree(run_dir, "before/run_dir_snapshot")
        _export_tree(states_dir, "before/states_dir_snapshot")

        # ── PHASE B: echter frischer OS-Subprozess, normaler Aufrufer. ──
        child_script = _HERE / "_r5_t1d_fresh_process_resume.py"
        assert child_script.is_file(), f"Kind-Skript fehlt: {child_script}"
        argv = [
            sys.executable, str(child_script), str(run_dir), str(states_dir), str(schema_path),
            table.table_id, section_id, today, ts, guest_char_id,
        ]
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=60)
        _export_text("child_stdout.txt", proc.stdout)
        _export_text("child_stderr.txt", proc.stderr)

        assert proc.returncode == 0, (
            f"PHASE B Pflicht-Beleg (2): echter Subprozess-Aufruf ist unerwartet fehlgeschlagen "
            f"(rc={proc.returncode}) -- stderr:\n{proc.stderr}"
        )
        lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
        assert lines, f"PHASE B: keine stdout-Zeile vom Kindprozess -- stderr:\n{proc.stderr}"
        payload = json.loads(lines[-1])
        assert "error" not in payload, f"PHASE B: Kindprozess meldete einen Fehler: {payload}"

        assert payload["gm_calls"] == 0, (
            f"PHASE B Pflicht-Beleg (5): KEIN zweiter Transport-/GM-Call erwartet: {payload}"
        )
        assert payload["completion_success"] is False, payload
        assert payload["open_round_marker_present_after"] is False, (
            f"PHASE B Pflicht-Beleg (4): der `_open_round`-Marker muss nach Recovery geloescht sein: {payload}"
        )
        assert payload["member_state_before"] == "correction_pending", payload
        assert payload["member_state_after"] == "hold", (
            f"PHASE B Pflicht-Beleg (3): Mitgliedsdatensatz muss terminalisiert sein (hold): {payload}"
        )
        assert payload["member_reason_after"] == "unresolved_prior_round_outcome", payload
        assert payload["group_records_before"] == 1 and payload["group_records_after"] == 1, (
            f"PHASE B Pflicht-Beleg (5): weiterhin GENAU EIN Gruppen-Ledger-Datensatz, kein zweiter: {payload}"
        )

        assert not open_round_path.exists(), (
            "PHASE B: der Marker haette nach Recovery (vom frischen Subprozess) geloescht sein muessen "
            "(auch aus Sicht des Elternprozesses, derselbe `run_dir`)."
        )
        after_member_path = sc._record_path(run_dir, group_repair_key)
        after_member = _export_file(after_member_path, "after/member_correction_record.json")
        _export_tree(run_dir, "after/run_dir_snapshot")

        assert before_member["sha256"] != after_member["sha256"], (
            "PHASE B Pflicht-Beleg (3): Vorher-Hash und Nachher-Hash des Mitglieds-Korrekturdatensatzes "
            "duerfen NICHT identisch sein (offen -> terminal)."
        )

        summary = {
            "classification": "produced",
            "dimensions": {
                "1_open_abandoned_group_round": {
                    "evidence": "before/group_round_open_marker.json + before/member_correction_record.json",
                    "member_state_before": member_before["state"],
                    "group_records_before": group_records_before,
                },
                "2_normal_caller_run_play_session": {
                    "caller": "mmo_sim.core.app_service.run_play_session",
                    "call_site": "tests/mmo_sim/_r5_t1d_fresh_process_resume.py (siehe run_play_session(...)-Aufruf)",
                    "dispatch_path": "mmo_sim/core/runtime.py:1153 has_open_group_round -> finalize(resume_section_id) "
                                     "-> store.complete_section -> save_correction.pursue_group_save_correction",
                },
                "3_real_fresh_os_subprocess": {
                    "argv": argv,
                    "returncode": proc.returncode,
                    "child_pid": payload.get("pid"),
                    "child_executable": payload.get("executable"),
                },
            },
            "run_dir": str(run_dir), "table_id": table.table_id, "section_id": section_id,
            "before_group_round_marker": before_marker,
            "before_member_record": before_member,
            "after_member_record": after_member,
            "child_payload": payload,
            "note_on_run_scoped_hashes": (
                "run_dir liegt in einem tempfile.TemporaryDirectory je Treiberlauf -- die hier "
                "gedruckten sha256-Werte sind GENAU fuer DIESEN eingefrorenen Lauf gueltig "
                "(eingebettete table_id/section_id/run_id sind fix, aber Pfade/Zeitstempel in den "
                "kopierten run_dir-Schnappschuessen koennen je Lauf variieren); MANIFEST.json ist "
                "fuer die tatsaechlich unter t1d/evidence/ abgelegten Dateien massgeblich, nicht ein "
                "fixer Prosa-Hash in diesem Text."
            ),
        }
        _export_json("SUMMARY.json", summary)

    (_RESULTS_ROOT / "MANIFEST.json").write_text(
        json.dumps(_MANIFEST, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    print("=== R5-T1D FRESH-PROCESS-RESUME (run_play_session, echter Subprozess): PASS ===")
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except AssertionError as e:
        print(f"FAIL: {e}")
        rc = 1
    except Exception:
        import traceback
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
