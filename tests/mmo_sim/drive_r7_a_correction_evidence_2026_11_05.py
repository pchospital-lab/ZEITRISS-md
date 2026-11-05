#!/usr/bin/env python3
"""
tests/mmo_sim/drive_r7_a_correction_evidence_2026_11_05.py -- ZR-BETREIBER-
GASTERSCHAFFUNG-20261105-R7, Familie `a_correction` (G4/A, 01_NACHZUG.md §2,
02_NACHWEISE_UND_RUECKGABE.md §1 "G4/bestehendes A-correction",
04_ABGABE_UND_QUELLEN.md §2): schliesst den von GUEST-PUBLICATION.md §3.2
benannten Nachweisrest des R6-Belegs `drive_r6_a_correction_evidence_
2026_11_05.py` -- dort entfernte die "spaet gueltige" zweite Antwort den
gebundenen Walletbetrag 500 ERSATZLOS (frischer `full_v7_save(...)` mit
`economy={}`) und waere DESHALB bereits ohne den neuen R6-Fix-A-Stopcheck
am bestehenden Drift-HOLD (`core/save_correction.py:1464-1476`) gescheitert
-- kein vollstaendiger Beleg des verlangten "sonst annehmbaren" inneren
Korrekturfalls.

Dieser Treiber repariert GENAU das: die zweite Antwort traegt denselben
Walletbetrag 500 in der SCHEMAGUELTIGEN Form `/economy/wallets/<char_id>/
balance` (statt der im ersten -- weiterhin bewusst ungueltigen -- Entwurf
verwendeten blossen Zahl `/economy/wallets/<char_id>` == 500). Das ist GENAU
der in `domain/zeitriss/save_correction.py:266-291` (`_is_allowed_amount_
wrap`) UND im SAVEGATE-Vertrag (`01_AUFTRAG_SAVEGATE.md §A: "Wallet Zahl
100 -> Objekt mit balance 100 erlaubt"`) als wertgleich/driftfrei anerkannte
Zahl->Objekt-Wrap: beide v7-Schemas (`systems/gameflow/saveGame.v7.schema.
json`/`.export.schema.json`) verlangen fuer `economy.wallets.<id>` ein
Objekt mit PFLICHT-`balance` (number) -- eine blosse Zahl ist dort TYPE-
UNGUELTIG (das macht den ersten Entwurf ungueltig), `{"balance": 500}` ist
voll schema-gueltig UND behaelt den Betrag 500 unveraendert (kein `economy=
{}`-Verlust). Der Kandidat ist damit tatsaechlich "sonst annehmbar" (schema-
UND driftzulaessig) -- GENAU der vom Order verlangte enge Anschluss.

Derselbe bereits beauftragte Uebergang (R6-Fix A, `core/save_correction.py:
pursue_single_figure_correction`, zweiter `stop_check`-Recheck NACH
`record_correction_received`/`archive_raw_response` und VOR `mark_adopted`,
s. `GUEST-PUBLICATION.md §2.1`) wird UNVERAENDERT erneut belegt: echter
offener Korrekturrequest, dauerhafter adressierter Stop derselben erwarteten
Generation, die jetzt tatsaechlich sonst-annehmbare Antwort wird `correction_
received` verbucht, aber NICHT adoptiert -- `CorrectionOutcome(status=
'stopped')`, aeusserer Dialog ebenfalls `stopped`.

Zusaetzlich (04_ABGABE_UND_QUELLEN.md §2, Linus-Briefing Treiber 2): das
deklarierte Roharchiv (`core/save_compatibility.py:archive_raw_response`,
append-only unter `run_dir/save_corrections_raw/<repair_key-safe>.json`,
VOR dem Stopcheck aufgerufen, s. Moduldocstring dort und `save_correction.py:
1310-1329`) wird HIER tatsaechlich als eigener Manifest-Eintrag exportiert
(ECHTE neue Bytes/SHA256 dieses Laufs -- NICHT die alten, historisch
deklarierten R6-Werte, die zu einem ANDEREN Lauf mit anderen Zeitstempeln
gehoeren und nie wieder erreichbar sind). Ein "Versuchclaim" (`onboarding.
record_attempt_claim`/`attempt-claim__<key>.json`, s. `onboarding.py:434-
469`) wird NUR beim ERFOLGREICHEN Erschaffungs-/Importfinish nach `mark_
adopted` geschrieben (`ui/tui.py:6623-6644`) -- da dieser Lauf (wie der
R6-Vorlauf) terminal `stopped` endet UND NIE adoptiert, kann hier KEIN
echter Versuchclaim existieren; seine Abwesenheit wird explizit geprueft
und erfasst (KEIN kuenstlich erzeugter Claim).

ECHTER Launcher-Subprozess, GM-Anbieter NUR als FIX5-Grenzinjektion, NIE
Live-Modell.

Pure Python, nur `assert`, echter Exitcode, kein pytest."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import subprocess  # noqa: E402

import drive_r4_evidence_2026_11_04 as r4  # noqa: E402
import _r6_evidence_helpers as r6  # noqa: E402

import mmo_sim.core.admission as admission  # noqa: E402
import mmo_sim.core.save_correction as sc  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import catalog  # noqa: E402
from mmo_sim.domain.zeitriss import creation_service as creation_grants  # noqa: E402
from mmo_sim.domain.zeitriss import save_correction as save_correction_domain  # noqa: E402
from mmo_sim.domain.zeitriss import save_compatibility as save_compatibility_domain  # noqa: E402
from mmo_sim.domain.zeitriss.save_correction import creation_repair_key  # noqa: E402
from _full_v7_fixture import full_v7_save  # noqa: E402

_OUT_DIR = Path(os.environ.get(
    "R7_OUT_DIR",
    "/home/altair/zr-betreiber-gast-20261105/r7/run/evidence/r7-runs/a_correction",
))
_RUN_ID = "a_correction_late_schema_and_drift_valid_wallet_wrap_answer_after_won_stop_no_adoption"


def run() -> None:
    mf = r6.Manifest(_OUT_DIR)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data = root / "op_data"
        run_dir = root / "run"
        states_dir = root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        in_fifo = fifo_dir / "guest_in.fifo"
        out_fifo = fifo_dir / "guest_out.fifo"
        calls_log = root / "gm_calls.jsonl"
        cfg_path = root / "gmdouble_cfg.json"
        signal_path = root / "stop_signal.json"

        write_test_profile(run_dir, max_turns=200)
        char_id = "CHR-R7A-CORRECTION-GAST"
        participant_id = "guest1"
        wallet_amount = 500

        # Erster Entwurf: WEITERHIN bewusst schema-UNGUELTIG -- `economy.
        # wallets.<char_id>` ist nach BEIDEN v7-Schemas
        # (`systems/gameflow/saveGame.v7.schema.json`/`.export.schema.json`
        # `properties.economy.properties.wallets.additionalProperties`) ein
        # OBJEKT mit Pflichtfeld `balance` (number) -- eine blosse Zahl ist
        # dort type-ungueltig. Das triggert dieselbe interne Korrekturstrecke
        # wie der R6-Vorlauf.
        invalid_block = full_v7_save(char_id, name="GastR7ACorrection", save_id="fixture-r7a-correction-001")
        invalid_block["economy"] = {"wallets": {char_id: wallet_amount}}
        invalid_content = "```json\n" + json.dumps(invalid_block, ensure_ascii=False) + "\n```"

        # Zweiter Entwurf (die "spaet gueltige" Antwort): derselbe Betrag
        # 500 in der SCHEMAGUELTIGEN, wertgleichen Wrap-Form -- `economy`
        # ist NICHT leer, der Betrag bleibt nachweislich unveraendert
        # (`domain/zeitriss/save_correction.py:_is_allowed_amount_wrap`:
        # GENAU EIN neuer Unterpfad `.../balance`, derselbe Zahlenwert,
        # KEIN zusaetzlicher Geschwisterschluessel -> driftfrei, KEINE
        # semantische Drift). Sonst identisch zum ersten Entwurf (dieselbe
        # char_id, keine Identitaets-/Levelaenderung).
        valid_block = full_v7_save(char_id, name="GastR7ACorrection", save_id="fixture-r7a-correction-002")
        valid_block["economy"] = {"wallets": {char_id: {"balance": wallet_amount}}}
        assert valid_block["economy"] != {}, "R7/a_correction: der reparierte Kandidat darf KEINE leere economy haben."
        valid_content = "```json\n" + json.dumps(valid_block, ensure_ascii=False) + "\n```"

        # ── Statischer Vorabbeleg der tatsaechlichen Schema-/Drift-
        # zulaessigkeit MIT DEN VOM PRODUKT SELBST GENUTZTEN
        # Pruefoberflaechen (01_NACHZUG.md §2: "mit den vorhandenen
        # Pruefoberflaechen im selben Beleg nachvollziehbar machen") --
        # EXAKT dieselbe Funktionsfolge wie `core/save_correction.py:
        # pursue_single_figure_correction` (1440-1468): CU-only
        # Wallet-Projektion (hier No-op, kein "cu"-Feld) -> `evaluate()`
        # fuer Fehlerpfade des Ausgangsentwurfs -> `evaluate()` fuer die
        # Annahmefaehigkeit des reparierten Kandidaten -> `detect_
        # unjustified_drift(..., restrict_to_core_identity=True)` (dieselbe
        # Einschraenkung wie am echten Erschaffungsdialog-Aufrufer,
        # `core/creation_service.py:437`). Dies laeuft VOR dem echten
        # Launcher-Prozess und ERSETZT KEINE Produktentscheidung -- der
        # echte Launcher-Lauf unten durchlaeuft DENSELBEN Code erneut, der
        # Stopcheck gewinnt dort VOR dieser Pruefung (GUEST-PUBLICATION.md
        # §2.1), diese statische Vorabpruefung belegt nur, dass der
        # Kandidat OHNE den Stop tatsaechlich angenommen worden waere.
        invalid_projection = save_compatibility_domain.project_wallets_in_block(
            invalid_block, rules=save_compatibility_domain.CU_ONLY_RULES,
        ).canonical_candidate
        valid_projection = save_compatibility_domain.project_wallets_in_block(
            valid_block, rules=save_compatibility_domain.CU_ONLY_RULES,
        ).canonical_candidate
        base_acceptance_static = save_correction_domain.evaluate(invalid_projection, char_id)
        error_paths_static = {e.path for e in base_acceptance_static.structure.errors}
        assert any(p.endswith(f"/economy/wallets/{char_id}") for p in error_paths_static), (
            f"R7/a_correction: der Ausgangsentwurf muss GENAU den Wallet-Pfad als Fehler melden "
            f"(Vorbedingung fuer den erlaubten Zahl->Objekt-Wrap): {error_paths_static}"
        )
        new_acceptance_static = save_correction_domain.evaluate(valid_projection, char_id)
        assert new_acceptance_static.accepted, (
            f"R7/a_correction: der reparierte Kandidat muss gegen BEIDE v7-Schemas tatsaechlich "
            f"annehmbar sein (Vorbedingung 'sonst annehmbarer Kandidat'): "
            f"{[e.path for e in new_acceptance_static.structure.errors] if not new_acceptance_static.accepted else None}"
        )
        drift_static = save_correction_domain.detect_unjustified_drift(
            invalid_projection, valid_projection, error_paths_static, restrict_to_core_identity=True,
        )
        assert drift_static == [], (
            f"R7/a_correction: der reparierte Kandidat darf KEINE unerwuenschte Drift gegenueber dem "
            f"Ausgangsentwurf aufweisen (wertgleicher Zahl->Objekt-Wrap ist explizit erlaubt): {drift_static}"
        )

        r4._write_gm_double_config(
            cfg_path, responses=[invalid_content, valid_content], calls_log=calls_log,
            stop={
                "after_call": 2, "kind": "creation", "signal_file": str(signal_path),
                "run_dir": str(run_dir), "operator_id": "operator1", "guest_id": participant_id, "generation": 1,
            },
        )
        env = r4._gm_double_env(cfg_path)
        argv = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"{participant_id}:{in_fifo}:{out_fifo}",
        ]
        utc_start = r6.utc(time.time())
        proc = subprocess.Popen(
            argv, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f, out_f = r4._open_guest_fifo_pair(in_fifo, out_fifo)
        r4._drain(out_f, settle=0.6, overall=10.0)

        r4._send_guest(in_f, "gast-erschaffung-anfragen operator1")
        r4._drain(out_f, settle=0.6, overall=10.0)
        r4._send_op(proc, f"gast-erschaffung-annehmen {participant_id}")
        time.sleep(0.6)
        grant_before = creation_grants.grant_status(run_dir, participant_id)
        assert grant_before["status"] == "approved" and grant_before["generation"] == 1, grant_before

        repair_key = creation_repair_key(participant_id, char_id)

        # Kein Attempt-Claim-/Finish-Koerper kann VOR diesem Punkt existieren
        # (`record_attempt_claim` laeuft nur NACH erfolgreicher Adoption,
        # `ui/tui.py:6623-6644`) -- "Vorher"-Abwesenheitsbeleg.
        guest_onboarding_dir = op_data / "guests" / participant_id / "onboarding"
        attempt_claim_files_before = (
            sorted(guest_onboarding_dir.glob("attempt-claim__*.json"))
            if guest_onboarding_dir.is_dir() else []
        )
        assert attempt_claim_files_before == [], (
            f"R7/a_correction: VORHER darf kein Versuchclaim existieren: {attempt_claim_files_before}"
        )

        r4._send_guest(in_f, "gast-erschaffung-dialog operator1")
        invalid_lines = r4._wait_for_marker(out_f, "[SL]", overall=15.0)
        assert any("SL korrigiert Format" in l or "Versuch 1/" in l for l in
                   r4._drain(out_f, settle=0.6, overall=8.0) + invalid_lines), (
            "R7/a_correction: die ungueltige Erstantwort muss die Korrekturstrecke sichtbar "
            f"anstossen: {invalid_lines}"
        )

        r4._wait_for_path(signal_path, overall=15.0)
        utc_stop_sent = r6.utc(time.time())

        record_before = sc.load_record(run_dir, repair_key)
        assert record_before is not None and record_before.get("state") == sc.STATE_CORRECTION_PENDING, (
            f"R7/a_correction: 'vorher' muss den offenen Korrektur-Request (correction_pending) "
            f"zeigen: {record_before}"
        )
        bound_wallet_before = record_before.get("bound_block", {}).get("economy", {}).get("wallets", {}).get(char_id)
        assert bound_wallet_before == wallet_amount, (
            f"R7/a_correction: der gebundene Ausgangsentwurf muss den Walletbetrag {wallet_amount} "
            f"(ungueltige Zahlform) tragen: {bound_wallet_before}"
        )

        r4._send_op(proc, f"gast-erschaffung-stop {participant_id}")

        terminal_marker = (
            "ein adressierter Betreiber-Stop hat den gemeinsamen Entscheid waehrend der "
            "Save-Korrektur gewonnen"
        )
        terminal_lines = r4._wait_for_marker(out_f, terminal_marker, overall=15.0)
        joined_terminal = "".join(terminal_lines)
        assert (
            "dieser Weg ist terminal, kein weiterer Korrektur-Request, keine Annahme/Publikation"
            in joined_terminal
        ), joined_terminal
        assert "Deine Antwort" not in joined_terminal, terminal_lines

        tail_after_terminal = r4._drain(out_f, settle=0.8, overall=5.0)
        assert "Deine Antwort" not in "".join(tail_after_terminal), tail_after_terminal

        record_after = sc.load_record(run_dir, repair_key)
        assert record_after is not None and record_after.get("state") == sc.STATE_CORRECTION_RECEIVED, (
            f"R7/a_correction: 'nachher' muss die empfangene, aber NICHT adoptierte Korrekturantwort "
            f"zeigen (state=correction_received, NIE adopted): {record_after}"
        )
        assert record_after.get("attempts_used") == record_before.get("attempts_used"), (
            "R7/a_correction: derselbe Versuchs-Slot (attempts_used) -- kein zweiter Versand nach Stop."
        )

        decision_id = creation_grants._creation_decision_id("operator1", participant_id, 1)
        decision = admission.read_table_decision(run_dir, decision_id)
        assert decision is not None and decision.get("decision") == "stopped", decision

        gm_calls = [json.loads(l) for l in calls_log.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(gm_calls) == 2, (
            f"R7/a_correction: genau 2 GM-Calls erwartet (Initialturn ungueltig + 1 Korrektur-Request, "
            f"danach Stop -- KEIN dritter Request trotz schema-/driftgueltiger Antwort): {gm_calls}"
        )

        requests_dir = run_dir / "requests"
        all_requests = [
            json.loads(p.read_text(encoding="utf-8")) for p in sorted(requests_dir.glob("*.json"))
        ] if requests_dir.is_dir() else []
        assert len(all_requests) == 2, (
            f"R7/a_correction: genau 2 Requests im Ledger erwartet: {all_requests}"
        )
        assert all(r.get("state") == "accounted" and not r.get("error") for r in all_requests), (
            f"R7/a_correction: beide Requests muessen ehrlich 'accounted' ohne Fehler verbucht sein: "
            f"{all_requests}"
        )
        # Die Anbieterantwort selbst (der schema-/driftgueltige zweite
        # Entwurf) liegt im Request-`result_text` vor -- KEINE fehlende
        # Anbieterantwort (GUEST-PUBLICATION.md §3.3).
        correction_request = next(
            (r for r in all_requests if r.get("role") == sc.ROLE_CREATION and r.get("turn_idx") == 1), None,
        )
        assert correction_request is not None and valid_content in (correction_request.get("result_text") or ""), (
            f"R7/a_correction: der Korrektur-Request muss die VOLLSTAENDIGE spaet-gueltige Antwort als "
            f"result_text binden: {correction_request}"
        )

        current_path = run_dir / "current_saves" / f"{participant_id}.json"
        assert not current_path.exists(), "R7/a_correction: kein Current-Write nach Stop."
        guest_catalog_dir = op_data / "guests" / participant_id / "catalog"
        assert catalog.list_for_participant(guest_catalog_dir, participant_id) == [], (
            "R7/a_correction: keine Katalogfigur nach Stop (die spaet gueltige Antwort wurde NICHT "
            "adoptiert/publiziert, trotz tatsaechlicher Schema-/Driftzulaessigkeit)."
        )

        # ── Roharchiv (04_ABGABE_UND_QUELLEN.md §2): `archive_raw_response`
        # laeuft UNBEDINGT NACH `record_correction_received`, VOR dem
        # Stopcheck (save_correction.py:1310-1329) -- die Rohantwort dieses
        # EINEN Korrektur-Requests muss daher real archiviert vorliegen.
        raw_archive_path = run_dir / "save_corrections_raw" / f"{repair_key.replace('/', '_')}.json"
        assert raw_archive_path.exists(), (
            f"R7/a_correction: das Roharchiv muss nach dem archivierten Korrektur-Request real "
            f"existieren: {raw_archive_path}"
        )
        raw_archive_entries = json.loads(raw_archive_path.read_text(encoding="utf-8"))
        assert isinstance(raw_archive_entries, list) and len(raw_archive_entries) == 1, (
            f"R7/a_correction: GENAU EIN Roharchiv-Eintrag erwartet (ein einziger Korrektur-Request "
            f"vor Stop): {raw_archive_entries}"
        )
        assert raw_archive_entries[0].get("raw_text") == valid_content, (
            f"R7/a_correction: der Roharchiv-Eintrag muss die VOLLSTAENDIGE spaet-gueltige Rohantwort "
            f"tragen: {raw_archive_entries[0]}"
        )
        raw_archive_sha256_real = r6.sha256_of(raw_archive_path)
        raw_archive_bytes_real = raw_archive_path.stat().st_size

        # ── Versuchclaim: terminal 'stopped' ohne Adoption -> real NICHT
        # existent (ehrlich erfasste Abwesenheit, KEIN kuenstlicher Claim).
        attempt_claim_files_after = (
            sorted(guest_onboarding_dir.glob("attempt-claim__*.json"))
            if guest_onboarding_dir.is_dir() else []
        )
        assert attempt_claim_files_after == [], (
            f"R7/a_correction: NACH dem terminalen Stop (keine Adoption) darf KEIN Versuchclaim "
            f"existieren: {attempt_claim_files_after}"
        )

        r4._send_op(proc, "beenden")
        stdout_text, stderr_text = proc.communicate(timeout=30)
        utc_end = r6.utc(time.time())
        in_f.close()
        out_f.close()
        assert proc.returncode == 0, f"R7/a_correction: Launcher-Lauf ist unerwartet gescheitert: {stderr_text}"

        r6.write_process_result(
            _OUT_DIR, "launcher", argv=argv, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
            stdout_text=stdout_text, stderr_text=stderr_text,
        )
        mf.record_process_files(
            "launcher", aussage="a_correction_full_launcher_transcript", run_id=_RUN_ID,
            teilnehmer_figur=participant_id, tisch_abschnitt="creation-operator1-guest1-gen1",
        )
        mf.export_tree(
            run_dir, "run", aussage="a_correction_run_dir_after_stop", run_id=_RUN_ID,
            teilnehmer_figur=participant_id, tisch_abschnitt="creation-operator1-guest1-gen1",
        )
        mf.export_file(
            calls_log, "gm_calls.jsonl", aussage="a_correction_gm_double_calls_log", run_id=_RUN_ID,
            teilnehmer_figur=participant_id,
        )
        mf.export_file(
            raw_archive_path, "save_corrections_raw_real_export.json",
            aussage="a_correction_raw_archive_real_export_echte_neue_bytes_dieses_laufs", run_id=_RUN_ID,
            teilnehmer_figur=f"{participant_id}/{char_id}",
        )
        mf.write_json_body(
            "invalid_draft_full_body.json", invalid_block,
            aussage="a_correction_original_invalid_draft_full_body", run_id=_RUN_ID,
            teilnehmer_figur=f"{participant_id}/{char_id}",
        )
        mf.write_json_body(
            "valid_wallet_wrap_candidate_full_body.json", valid_block,
            aussage="a_correction_repaired_schema_and_drift_valid_wallet_wrap_candidate_full_body",
            run_id=_RUN_ID, teilnehmer_figur=f"{participant_id}/{char_id}",
        )
        mf.write_json_body(
            "save_correction_record_before.json", record_before,
            aussage="a_correction_repair_record_before_late_valid_wallet_wrap_answer", run_id=_RUN_ID,
            teilnehmer_figur=f"{participant_id}/{char_id}",
        )
        mf.write_json_body(
            "save_correction_record_after.json", record_after,
            aussage="a_correction_repair_record_after_stop_no_adoption", run_id=_RUN_ID,
            teilnehmer_figur=f"{participant_id}/{char_id}",
        )
        mf.write_json_body(
            "correction_request_with_provider_answer.json", correction_request,
            aussage="a_correction_correction_request_settlement_with_full_provider_result_text",
            run_id=_RUN_ID, teilnehmer_figur=f"{participant_id}/{char_id}",
        )
        mf.write_json_body(
            "io_transcript.json", {
                "invalid_lines": invalid_lines, "terminal_lines": terminal_lines,
                "tail_after_terminal": tail_after_terminal,
            }, aussage="a_correction_dialog_io_transcript", run_id=_RUN_ID, teilnehmer_figur=participant_id,
        )
        mf.write_json_body(
            "static_schema_and_drift_proof.json", {
                "error_paths_ausgangsentwurf": sorted(error_paths_static),
                "kandidat_angenommen": new_acceptance_static.accepted,
                "kandidat_fehlerpfade": [e.path for e in new_acceptance_static.structure.errors],
                "drift_gefunden": drift_static,
                "hinweis": (
                    "berechnet VOR dem Launcher-Prozess mit denselben Pruefoberflaechen wie "
                    "core/save_correction.py:pursue_single_figure_correction (1440-1468): "
                    "save_compatibility_domain.project_wallets_in_block(CU_ONLY_RULES) -> "
                    "save_correction_domain.evaluate() -> detect_unjustified_drift("
                    "restrict_to_core_identity=True, wie core/creation_service.py:437). Belegt, "
                    "dass der reparierte Kandidat OHNE den Stop tatsaechlich angenommen worden "
                    "waere (schema- UND driftzulaessig) -- ersetzt keine Produktentscheidung, "
                    "der echte Launcher-Lauf unten durchlaeuft denselben Code erneut."
                ),
            }, aussage="a_correction_static_schema_and_drift_proof_same_product_surfaces", run_id=_RUN_ID,
            teilnehmer_figur=f"{participant_id}/{char_id}",
        )
        mf.write_json_body(
            "attempt_claim_absence.json", {
                "before": [str(p) for p in attempt_claim_files_before],
                "after": [str(p) for p in attempt_claim_files_after],
                "reason": (
                    "record_attempt_claim laeuft nur NACH erfolgreicher Adoption/Finish "
                    "(ui/tui.py:6623-6644); dieser Lauf endet terminal 'stopped' ohne Adoption -- "
                    "KEIN Versuchclaim real existent, ehrlich als Abwesenheit erfasst, nicht "
                    "kuenstlich erzeugt."
                ),
            }, aussage="a_correction_attempt_claim_honest_absence", run_id=_RUN_ID,
            teilnehmer_figur=f"{participant_id}/{char_id}",
        )
        mf.write_manifest()
        mf.write_summary({
            "familie": "a_correction", "aussage": (
                "G4/A (01_NACHZUG.md §2, GUEST-PUBLICATION.md §3.2 enger Anschluss): die zweite "
                "Korrekturantwort traegt denselben Walletbetrag 500 jetzt in der SCHEMAGUELTIGEN, "
                "wertgleichen Zahl->Objekt-Wrap-Form (/economy/wallets/<id>/balance statt blosser "
                "Zahl) -- tatsaechlich schema- UND driftzulaessig (domain/zeitriss/save_correction.py:"
                "_is_allowed_amount_wrap), economy NICHT leer. Trotzdem KEINE Adoption: der R6-Fix-A-"
                "Stopcheck (core/save_correction.py:pursue_single_figure_correction, NACH record_"
                "correction_received/archive_raw_response, VOR mark_adopted) greift VOR der Annahme -- "
                "CorrectionOutcome(status='stopped'), record_after.state=correction_received, "
                "KEINE Adoption/Publikation. Roharchiv real exportiert (neue Bytes dieses Laufs); "
                "Versuchclaim real NICHT existent (ehrliche Abwesenheit, terminal ohne Adoption)."
            ),
            "echter_neuer_os_prozess": True,
            "gm_anbieter_ist_grenzinjektion": "FIX5 MMO_SIM_GM_TRANSPORT_DOUBLE, NIE Live-Modell",
            "produktcode_fundstellen": [
                "mmo_sim/core/save_correction.py:1310-1348 (record_correction_received, archive_raw_response, "
                "R6-Fix-A zweiter stop_check, VOR mark_adopted)",
                "mmo_sim/core/save_compatibility.py:72-92 (archive_raw_response, append-only unter "
                "run_dir/save_corrections_raw/<repair_key-safe>.json)",
                "mmo_sim/domain/zeitriss/save_correction.py:40-46,266-291 (_WALLET_AMOUNT_PATH_RE, "
                "_is_allowed_amount_wrap: wertgleicher Zahl->Objekt-Wrap bleibt driftfrei)",
                "mmo_sim/domain/zeitriss/save_correction.py:401-520 (detect_unjustified_drift, "
                "F-WALLET-LOSS-Verengung)",
                "mmo_sim/core/save_correction.py:1464-1476 (Drift-HOLD vor mark_adopted, waere ohne "
                "den Wrap getroffen worden)",
                "systems/gameflow/saveGame.v7.schema.json + .export.schema.json: "
                "properties.economy.properties.wallets.additionalProperties (Objekt, Pflichtfeld balance)",
                "mmo_sim/domain/zeitriss/onboarding.py:434-469 (record_attempt_claim/attempt_claim_matches, "
                "NUR nach Adoption -- hier belegt NICHT erreicht)",
            ],
            "repair_key": repair_key,
            "utc_stop_sent": utc_stop_sent,
            "gm_call_count": len(gm_calls),
            "wallet_amount": wallet_amount,
            "record_state_before": record_before.get("state"),
            "record_state_after": record_after.get("state"),
            "attempts_used_unchanged": record_after.get("attempts_used") == record_before.get("attempts_used"),
            "decision": decision,
            "current_write": current_path.exists(),
            "catalog_entries": len(catalog.list_for_participant(guest_catalog_dir, participant_id)),
            "raw_archive": {
                "path_real": str(raw_archive_path), "sha256_real": raw_archive_sha256_real,
                "bytes_real": raw_archive_bytes_real,
                "hinweis": (
                    "ECHTE neue Bytes/SHA256 DIESES Laufs -- unterscheiden sich erwartbar von den "
                    "historisch (nie bytegleich gefundenen) R6-deklarierten Werten d3267b9e...2723B, "
                    "da jeder Lauf eigene Zeitstempel/Requestbindung traegt."
                ),
            },
            "attempt_claim_real_absent": True,
            "assertions_bestanden": [
                "ungueltiger Erstentwurf (economy.wallets.<id>==Zahl, type-ungueltig) triggert Korrekturstrecke",
                "Double blockiert im ersten Korrektur-Request, signalisiert per Datei",
                "record_before.state == correction_pending, bound_block traegt Walletbetrag 500 (Zahlform)",
                "echter Stopbefehl waehrend offenem Request gewonnen (decision=stopped)",
                "Double liefert DANACH eine SCHEMA- UND DRIFTGUELTIGE Wrap-Antwort (Betrag wertgleich)",
                "record_after.state == correction_received (NIE adopted)",
                "gleicher attempts_used vor/nach (kein zweiter Versand)",
                "genau 2 GM-Calls, genau 2 Requests, beide accounted ohne Fehler",
                "Request result_text enthaelt die VOLLE Anbieterantwort (keine fehlende Antwort)",
                "Roharchiv real exportiert (ein Eintrag, volle Rohantwort)",
                "Versuchclaim real NICHT existent (ehrlich erfasste Abwesenheit, terminal ohne Adoption)",
                "terminal-Meldung erschienen, NIE 'Deine Antwort'",
                "kein Current-Write, keine Katalogfigur",
            ],
        })


def main() -> int:
    try:
        run()
    except AssertionError as e:
        print(f"FAIL a_correction: {e}")
        return 1
    except Exception:
        traceback.print_exc()
        return 1
    print("OK a_correction")
    return 0


if __name__ == "__main__":
    sys.exit(main())
