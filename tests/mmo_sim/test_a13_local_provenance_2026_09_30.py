#!/usr/bin/env python3
"""
tests/mmo_sim/test_a13_local_provenance_2026_09_30.py — A13 (02_AUFTRAG_A13.md,
04_ROLLEN_UND_MAIN.md, 03_GATES_UND_AUFRUFE.md §7, 2026-09-30): lokaler
Operator-Quellenbericht ueber den neuen fruehen `report`-Dispatcherzweig.

Pure Python, nur `assert`, echter Exitcode (wie alle Dateien in diesem
Ordner, s. `run_all.py`).

Testlage (P13-1..6, s. 03_GATES_UND_AUFRUFE.md):
  - Hauptnachweis ist der ECHTE `scripts/mmo_sim.py report`-Prozess
    (Subprozess, kein reiner Parser-Unit-Test) -- `_run_report()` unten.
  - STANDARD includes fresh existing A23 API + Hybrid journeys, then separate
    zero-inference reports on their durable snapshots. The older two-person
    store-built REPORTFIXTURE remains only for deterministic parser/error tests;
    it is not described as a real A23 journey. No external package is required.
  - OPTIONAL `--fixture-package <P>`: zusaetzlich werden die ZWEI echten,
    bereits ausgefuehrten synthetischen A23-Endablagen aus
    REPORT-FIXTURES.json (API + Hybrid) als uebernommene Regressions-
    eingaben gegen den echten Reportprozess geprueft (in eine exklusive
    Testkopie kopiert -- das Paket selbst bleibt unveraendert). Diese
    zwei echten Reisen sind reale, bereits abgeschlossene A23-Laeufe,
    KEINE hier neu gespielte Karriere -- s. PROVENIENZ.json/A13_SOURCE_MAP.json.
  - Zusaetzliche handgeschriebene deterministische Belegfixtures
    (`_HANDWRITTEN_...`-Konstanten unten) sind ausdruecklich als
    REPORTFIXTURE gekennzeichnet, keine gespielte Karriere.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _a13_report_support import build_real_minimal_section_data_dir  # noqa: E402
from mmo_sim.reports.report import (  # noqa: E402
    A13SourceError, ProvenanceExcerpt, build_source_report, extract_provenance_excerpts,
)

MMO_SIM = _REPO_ROOT / "scripts" / "mmo_sim.py"


# ----------------------------------------------------------------------------
# Hauptnachweis: echter `scripts/mmo_sim.py report`-Prozess (frischer
# Subprozess, kein reiner In-Process-Funktionsaufruf).
# ----------------------------------------------------------------------------

def _run_report(args: list[str], timeout: float = 60) -> subprocess.CompletedProcess:
    from _a13_report_support import run_recorded_report
    return run_recorded_report(args, _REPO_ROOT, timeout)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_hashes(root: Path) -> dict[str, str]:
    out = {}
    if not root.exists():
        return out
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out[str(p.relative_to(root))] = _sha256_file(p)
    return out


def _count_files(root: Path) -> int:
    return sum(1 for p in root.rglob("*") if p.is_file()) if root.exists() else 0


# ----------------------------------------------------------------------------
# P13-1: Dispatcher/keine Inferenz -- `report --help` und echter Start als
# frischer scripts-Prozess; Pflichtarg-/ID-Fehler VOR jeder Teilnehmer-/
# Lab-/Adapterkonstruktion (0 Treffer).
# ----------------------------------------------------------------------------

def test_p13_1_help_and_missing_required_args_touch_nothing():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td) / "data-not-yet-existing"
        proc = _run_report(["--help"])
        assert proc.returncode == 0, proc.stderr
        assert "--data-dir" in proc.stdout and "--table" in proc.stdout and "--section" in proc.stdout
        assert not data_dir.exists(), "report --help darf keine Datendatei/kein Datenverzeichnis anlegen"

        proc2 = _run_report([])
        assert proc2.returncode == 2, proc2.stderr
        assert "required" in proc2.stderr or "erforderlich" in proc2.stderr.lower() or "arguments are required" in proc2.stderr
        # Die reale Vorher-/Nachher-Pruefung des Repo-internen Default-
        # Datenverzeichnisses (keine tote `... or True`-Heuristik mehr,
        # R3 02_AUFTRAG_REST_A13.md) steht unten in
        # `test_p13_1_no_participant_or_lab_construction_on_help`.


def test_p13_1_no_participant_or_lab_construction_on_help():
    """Reale Vorher-/Nachher-Pruefung (statt Heuristik): der bestehende TUI-
    Default-Datenordner darf durch `report --help`/fehlende Pflichtargumente
    nicht veraendert werden -- der neue Zweig liegt VOR jeder
    Teilnehmerausloesung/TUI-/Lab-Konstruktion (02_AUFTRAG_A13.md)."""
    default_data_dir = _REPO_ROOT / "internal" / "mmo_sim_data"
    before = _tree_hashes(default_data_dir)
    _run_report(["--help"])
    _run_report([])
    _run_report(["--data-dir", "/nonexistent-a13-probe", "--table", "x"])  # weitere fehlende Pflichtargumente
    after = _tree_hashes(default_data_dir)
    assert before == after, "report-Dispatch hat den TUI-Default-Datenordner beruehrt"


# ----------------------------------------------------------------------------
# P13-2/P13-6: STANDARD -- echter Reportprozess gegen einen echten, minimalen
# (Testsupport-gebauten) Datenordner. Fixture-Aufbau (Spielaufrufe) und
# Reportaufrufe (NULL neue Requests) werden getrennt geprueft.
# ----------------------------------------------------------------------------

def test_p13_2_real_minimal_section_report_end_to_end_and_no_new_requests():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "a13root"
        root.mkdir()
        info = build_real_minimal_section_data_dir(root)  # Fixture-Aufbau (echte Produktfunktionen), GETRENNT gezaehlt
        run_dir = info["run_dir"]
        requests_before = sorted((run_dir / "requests").glob("*.json"))
        assert len(requests_before) == 2, "Testsupport muss genau 2 echte Requestdatensaetze erzeugt haben"
        source_before = _tree_hashes(run_dir)

        out_dir = Path(td) / "out"
        proc = _run_report([
            "--data-dir", str(run_dir), "--table", info["table_id"], "--section", info["section_id"],
            "--output-dir", str(out_dir), "--include-persona-feedback",
        ])
        assert proc.returncode == 0, proc.stderr
        # PARTIAL statt COMPLETE: GM-Modell-/Prompt-/Regelmetadaten werden in
        # dieser Datenkopie nie aufgezeichnet (ehrliche Luecke, R1).
        assert "PARTIAL" in proc.stdout

        # NULL-Request-Reportaufruf: exakt dieselben Requestdateien wie vorher,
        # keine neue Datei, kein Byte im Quellordner veraendert.
        requests_after = sorted((run_dir / "requests").glob("*.json"))
        assert requests_before == requests_after
        source_after = _tree_hashes(run_dir)
        assert source_before == source_after, "Reportlauf hat Quellbytes veraendert -- verboten (nur Ausgabewrite)"

        for name in ("report.json", "report.md", "issue-drafts.md", "source-index.json", "SHA256SUMS"):
            assert (out_dir / name).is_file(), f"{name} fehlt im Ausgabeordner"

        report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
        # R1 (02_AUFTRAG_REST_A13.md): GM-Modell-/Prompt-/Regelmetadaten
        # werden in dieser Datenkopie nie aufgezeichnet -- das ist eine
        # ehrliche Luecke, kein pauschales COMPLETE mehr.
        assert report["status"] == "PARTIAL"
        assert any("GM-Modell" in r for r in report["partial_reasons"])
        assert report["table"]["table_id"] == info["table_id"]
        assert report["sl_log"]["turns"] == 2
        assert report["sl_log"]["events_jsonl_present_but_unused"] is False, "events.jsonl darf in dieser Kopie fehlen -- table.sl_log ist Quelle"
        assert len(report["requests"]) == 2
        assert {r["participant"] for r in report["requests"]} == {"tech"}
        for pk in info["members"]:
            guard = report["completion"]["guards"][pk]
            assert guard["section_end_save_sha256_matches_guard"] is True
            # R1: historisches Vor-/Nachsavepaar tatsaechlich geladen (aus
            # expected_prev_ref/Guard, nicht aus aktuellem Current) und als
            # technisches Quellenpaar verknuepft (kein Kauf-/Erfolgsbeweis).
            assert guard["section_start_save"] is not None
            assert guard["section_start_save_source"]["sha256"]
            pair = guard["technical_source_pair"]
            assert pair["before"] == guard["section_start_save_source"]
            assert pair["after"] == guard["section_end_save_source"]
            assert "Kauf" in pair["disclaimer"]
        assert report["completion"]["final"]["section_id"] == info["section_id"]
        # --include-persona-feedback: NUR eigene passende Abschnittsreflexionen, kein Fremdinhalt.
        refl_by_pk = {r["persona_key"]: r for r in report["reflections"]}
        assert set(refl_by_pk) == set(info["members"])
        for pk, row in refl_by_pk.items():
            assert row["section_id"] == info["section_id"]
            # R2 (02_AUFTRAG_REST_A13.md §Eingangsroot): eigenes Abschnitts-
            # feedback ist PRIVAT und traegt eine auflösbare eigene Quelle
            # (Pfad/Zeile/Offsets/Hash), kein leeres `private:false`.
            assert row["private"] is True
            src = row["source"]
            assert src["path"] == "reflections.jsonl"
            refl_text = (run_dir / "reflections.jsonl").read_text(encoding="utf-8")
            refl_line = refl_text.splitlines()[src["line"] - 1]
            assert hashlib.sha256(refl_line.encode("utf-8")).hexdigest() == src["sha256"]
            assert refl_text[src["char_offset_start"]:src["char_offset_end"]] == refl_line

        excerpt_categories = {ex["category"] for ex in report["provenance_excerpts"]}
        assert "ausruestung" in excerpt_categories, "REPORTFIXTURE-Turn0 enthaelt eine Ausruestungs-Erwaehnung"
        for ex in report["provenance_excerpts"]:
            src_path = run_dir / ex["source_path"]
            assert src_path.is_file()
            assert _sha256_file(src_path) == ex["source_sha256"]
            start, end = ex["char_offset_start"], ex["char_offset_end"]
            table_data = json.loads((run_dir / "tables" / f"{info['table_id']}.json").read_text(encoding="utf-8"))
            pointer_parts = ex["pointer"].strip("/").split("/")
            turn_idx = int(pointer_parts[1])
            raw_content = table_data["sl_log"][turn_idx]["content"]
            assert raw_content[start:end] == ex["excerpt"], "Pointer/Offsets muessen exakt auf das unveraenderte Fragment zeigen"

        titles = [d["title"] for d in report["issue_drafts"]]
        assert any("ausruestung" in t for t in titles)
        assert all("privat" not in d["body"].lower() for d in report["issue_drafts"])


def test_p13_2_default_excludes_private_reflections():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "a13root"
        root.mkdir()
        info = build_real_minimal_section_data_dir(root)
        out_dir = Path(td) / "out"
        proc = _run_report([
            "--data-dir", str(info["run_dir"]), "--table", info["table_id"], "--section", info["section_id"],
            "--output-dir", str(out_dir),
        ])
        assert proc.returncode == 0, proc.stderr
        report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
        assert report["scope"]["include_persona_feedback"] is False
        assert report["reflections"] == [], "ohne --include-persona-feedback duerfen keine Reflexionen exportiert werden"


def test_p13_6_repeat_report_is_deterministic_and_leaves_no_new_game_state():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "a13root"
        root.mkdir()
        info = build_real_minimal_section_data_dir(root)
        run_dir = info["run_dir"]
        before_all = _tree_hashes(run_dir)

        out1 = Path(td) / "out1"
        out2 = Path(td) / "out2"
        proc1 = _run_report(["--data-dir", str(run_dir), "--table", info["table_id"], "--section", info["section_id"], "--output-dir", str(out1)])
        proc2 = _run_report(["--data-dir", str(run_dir), "--table", info["table_id"], "--section", info["section_id"], "--output-dir", str(out2)])
        assert proc1.returncode == 0 and proc2.returncode == 0

        after_all = _tree_hashes(run_dir)
        assert before_all == after_all, "zwei Reportlaeufe duerfen keine neue Spielrunde/Request/Saveversion erzeugen"

        r1 = json.loads((out1 / "report.json").read_text(encoding="utf-8"))
        r2 = json.loads((out2 / "report.json").read_text(encoding="utf-8"))
        r1.pop("generated_at_utc"); r2.pop("generated_at_utc")
        assert r1 == r2, "zwei Berichte auf denselben Input muessen denselben fachlichen Inhalt liefern (abzueglich Berichtszeit)"


def test_p13_6_corrupted_required_source_is_not_a_healthy_empty_report():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "a13root"
        root.mkdir()
        info = build_real_minimal_section_data_dir(root)
        table_path = info["run_dir"] / "tables" / f"{info['table_id']}.json"
        table_path.write_text("{not valid json", encoding="utf-8")
        out_dir = Path(td) / "out"
        proc = _run_report(["--data-dir", str(info["run_dir"]), "--table", info["table_id"], "--section", info["section_id"], "--output-dir", str(out_dir)])
        assert proc.returncode != 0, "eine kaputte Pflichtquelle darf NICHT wie ein gesunder Nullbericht durchgehen"
        assert not out_dir.exists(), "bei unlesbarer Pflichtquelle darf kein Ausgabeordner entstehen"


# ----------------------------------------------------------------------------
# P13-3: Quellen/Erwerb/Feedback -- unveraenderte Fragmente mit auflösbaren
# Pointer/Hash/Offsets; falsche Bindung wird sichtbar (kein stilles Uebernehmen).
# ----------------------------------------------------------------------------

def test_p13_3_extract_provenance_excerpts_still_unchanged_pure_function():
    """Bestehende Funktion (`report.py`, unveraendert) bleibt die EINZIGE
    Stichwortlogik -- A13 ruft sie nur auf und reichert das Ergebnis mit
    Pointer/Hash an (kein zweiter Erkennungsweg)."""
    events = [{
        "event_id": "e1", "event_type": "sl_turn", "actor": "leader",
        "payload": {"turn_idx": 0, "table_id": "t1", "section_id": "s1", "origin_persona_key": "sniper",
                    "content": "Der Boss blockt den Ausgang."},
        "ts": "t0",
    }]
    excerpts = extract_provenance_excerpts(events)
    assert len(excerpts) == 1 and excerpts[0].category == "boss"
    assert isinstance(excerpts[0], ProvenanceExcerpt)
    assert excerpts[0].source_path is None, "die unveraenderte Basisfunktion liefert KEINE Pointer-Anreicherung von sich aus"


def test_p13_3_mismatched_completion_plan_table_binding_is_a_hold_not_silent_success():
    """REPORTFIXTURE (handgeschrieben): ein `__plan.json`, dessen `table_id`
    NICHT zum angefragten Tisch passt, muss als Bindungsfehler sichtbar
    werden (03 §Grenzweg), NICHT still als Erfolg durchgehen."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "a13root"
        root.mkdir()
        info = build_real_minimal_section_data_dir(root)
        plan_path = info["run_dir"] / "completion" / f"{info['section_id']}__plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["table_id"] = "ein-anderer-tisch"
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        try:
            build_source_report(str(info["run_dir"]), info["table_id"], info["section_id"])
            assert False, "falsche Plan-table_id-Bindung haette einen A13SourceError ausloesen muessen"
        except A13SourceError as exc:
            assert "Bindungsfehler" in str(exc)


# ----------------------------------------------------------------------------
# R1-Nacharbeit (02_AUFTRAG_REST_A13.md, 2026-09-30): die am Eingang mit
# `tools/review_a13_sources.py --fixture-package` belegten roten Befunde
# werden hier als semantische Assertions auf REPORTFIXTUREs reproduziert --
# kein Nulltreffer/Importfehler/Timeout als Erkennung.
# ----------------------------------------------------------------------------

def test_p13_2_end_save_hash_mismatch_is_a_hold_not_a_hidden_false_field():
    """REPORTFIXTURE: publiziertes Endsave im Datenroot mutiert, Guard-Hash
    bleibt unveraendert -- muss jetzt ein Hold sein (vorher: rc0/COMPLETE
    mit `section_end_save_sha256_matches_guard: false` versteckt)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "a13root"
        root.mkdir()
        info = build_real_minimal_section_data_dir(root)
        guard_path = info["run_dir"] / "completion" / f"{info['chrononaut_ids']['sniper']}__{info['section_id']}.json"
        guard = json.loads(guard_path.read_text(encoding="utf-8"))
        save_path = info["run_dir"] / guard["save_path"]
        save_data = json.loads(save_path.read_text(encoding="utf-8"))
        save_data["_review_only"] = "HASH_MISMATCH"
        save_path.write_text(json.dumps(save_data), encoding="utf-8")
        try:
            build_source_report(str(info["run_dir"]), info["table_id"], info["section_id"])
            assert False, "Endsave-Hashwiderspruch haette einen A13SourceError ausloesen muessen"
        except A13SourceError as exc:
            assert "sniper" in str(exc) and "save_sha256" in str(exc)


def test_p13_2_guard_wrong_own_persona_key_is_a_hold():
    """REPORTFIXTURE: Guard-Datei fuer 'sniper' traegt selbst
    `persona_key='medic'` -- Dateiname/Ordnung ersetzt nicht die eigenen
    Felder des Guards (02_AUFTRAG_REST_A13.md §R1)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "a13root"
        root.mkdir()
        info = build_real_minimal_section_data_dir(root)
        guard_path = info["run_dir"] / "completion" / f"{info['chrononaut_ids']['sniper']}__{info['section_id']}.json"
        guard = json.loads(guard_path.read_text(encoding="utf-8"))
        guard["persona_key"] = "medic"
        guard_path.write_text(json.dumps(guard), encoding="utf-8")
        try:
            build_source_report(str(info["run_dir"]), info["table_id"], info["section_id"])
            assert False, "abweichendes Guard-persona_key haette einen A13SourceError ausloesen muessen"
        except A13SourceError as exc:
            assert "persona_key" in str(exc)


def test_p13_2_final_wrong_section_id_is_a_hold():
    """REPORTFIXTURE: `__final.json` traegt selbst eine andere `section_id`
    als der Dateiname/die angefragte Section -- muss ein Hold sein (vorher
    nur `table_id` geprueft)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "a13root"
        root.mkdir()
        info = build_real_minimal_section_data_dir(root)
        final_path = info["run_dir"] / "completion" / f"{info['section_id']}__final.json"
        final = json.loads(final_path.read_text(encoding="utf-8"))
        final["section_id"] = "REPORTFIXTURE-andere-section"
        final_path.write_text(json.dumps(final), encoding="utf-8")
        try:
            build_source_report(str(info["run_dir"]), info["table_id"], info["section_id"])
            assert False, "abweichende Final-section_id haette einen A13SourceError ausloesen muessen"
        except A13SourceError as exc:
            assert "widerspruechliche Bindung" in str(exc)


def test_p13_2_missing_historical_prior_version_is_partial_not_silent_current_fallback():
    """REPORTFIXTURE: die per `expected_prev_ref` referenzierte historische
    Vorversion wird entfernt -- der Bericht darf NICHT auf den aktuellen
    Current zurueckfallen, sondern muss das Quellenpaar als ausdruecklich
    unvollstaendig ausweisen (PARTIAL mit konkretem Grund)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "a13root"
        root.mkdir()
        info = build_real_minimal_section_data_dir(root)
        prev_path = info["run_dir"] / "current_saves" / "sniper__versions" / "0001.json"
        assert prev_path.is_file(), "Testannahme: erste historische Version muss existieren"
        prev_path.unlink()
        report = build_source_report(str(info["run_dir"]), info["table_id"], info["section_id"])
        assert report["status"] == "PARTIAL"
        assert any("historische Vorversion" in r and "sniper" in r for r in report["partial_reasons"])
        assert report["completion"]["guards"]["sniper"].get("section_start_save") is None
        assert "technical_source_pair" not in report["completion"]["guards"]["sniper"]
        # tech ist unberuehrt -- weiterhin ein vollstaendiges Quellenpaar.
        assert report["completion"]["guards"]["tech"].get("section_start_save") is not None


def test_p13_2_corrupt_request_json_is_named_not_silently_dropped():
    """REPORTFIXTURE: eine zum Abschnitt gehoerende Requestdatei wird mit
    kaputtem JSON ueberschrieben -- muss als PARTIAL-Grund benannt werden,
    nicht kommentarlos aus der Trefferliste verschwinden."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "a13root"
        root.mkdir()
        info = build_real_minimal_section_data_dir(root)
        run_dir = info["run_dir"]
        target = next(
            p for p in sorted((run_dir / "requests").glob("*.json"))
            if json.loads(p.read_text(encoding="utf-8")).get("section_id") == info["section_id"]
        )
        target.write_bytes(b"{A13_INVALID_JSON")
        report = build_source_report(str(run_dir), info["table_id"], info["section_id"])
        assert report["status"] == "PARTIAL"
        assert len(report["requests"]) == 1, "die kaputte Datei darf nicht als gueltiger Record erscheinen"
        assert any(target.name in r and "nicht auswertbar" in r for r in report["partial_reasons"])


def test_p13_2_events_jsonl_corruption_is_named_not_generic_unused_note():
    """REPORTFIXTURE: ein vorhandenes `events.jsonl` mit einer kaputten
    Zeile muss konkret als beschaedigt ausgewiesen werden -- table.sl_log
    bleibt trotzdem die einzige Turnquelle (keine Doppelzaehlung)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "a13root"
        root.mkdir()
        info = build_real_minimal_section_data_dir(root)
        (info["run_dir"] / "events.jsonl").write_text("{A13_INVALID_EVENT_JSON\n", encoding="utf-8")
        report = build_source_report(str(info["run_dir"]), info["table_id"], info["section_id"])
        assert report["sl_log"]["turns"] == 2, "events.jsonl darf keine zusaetzlichen/doppelten Turns beisteuern"
        assert any("beschaedigt" in r and "events.jsonl" in r for r in report["partial_reasons"])


# ----------------------------------------------------------------------------
# P13-4: Schutzgrenze -- genau gewaehlter Tisch, keine Traversal-/Symlink-
# Dereferenzierung, unsichere IDs werden VOR jedem Dateizugriff abgelehnt.
# ----------------------------------------------------------------------------

def test_p13_4_unsafe_table_or_section_id_rejected_via_real_process():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "a13root"
        root.mkdir()
        info = build_real_minimal_section_data_dir(root)
        out_dir = Path(td) / "out"
        proc = _run_report([
            "--data-dir", str(info["run_dir"]), "--table", "../../../etc/passwd",
            "--section", info["section_id"], "--output-dir", str(out_dir),
        ])
        assert proc.returncode != 0
        assert not out_dir.exists()


def test_p13_4_guard_save_path_traversal_is_rejected():
    """REPORTFIXTURE: ein manipulierter Guard mit `save_path` ausserhalb des
    Datenroots darf NICHT dereferenziert werden (02_AUFTRAG_A13.md §1)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "a13root"
        root.mkdir()
        info = build_real_minimal_section_data_dir(root)
        cid = info["chrononaut_ids"]["sniper"]
        guard_path = info["run_dir"] / "completion" / f"{cid}__{info['section_id']}.json"
        guard = json.loads(guard_path.read_text(encoding="utf-8"))
        guard["save_path"] = "../../../../etc/passwd"
        guard_path.write_text(json.dumps(guard), encoding="utf-8")

        proc = _run_report([
            "--data-dir", str(info["run_dir"]), "--table", info["table_id"],
            "--section", info["section_id"], "--output-dir", str(Path(td)/"out"),
        ])
        assert proc.returncode == 3 and not (Path(td)/"out").exists(), proc.stdout + proc.stderr


def test_p13_4_include_persona_feedback_never_leaks_other_section_reflection():
    """Reflexion eines ANDEREN Abschnitts derselben Persona darf NIE als
    Beleg des angefragten Abschnitts auftauchen (02_AUFTRAG_A13.md §3:
    `last_reflection` eines anderen Abschnitts nicht uebernehmen)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "a13root"
        root.mkdir()
        info = build_real_minimal_section_data_dir(root)
        reflections_path = info["run_dir"] / "reflections.jsonl"
        with reflections_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({
                "persona_key": "sniper", "section_id": "ein-ganz-anderer-abschnitt",
                "ts": "2026-09-30T00:00:00+00:00", "text": "GEHÖRT NICHT HIERHER",
                "origin_source": "persona_api:synthetic", "kind": "ai_reflection_received",
            }, ensure_ascii=False) + "\n")
        report = build_source_report(str(info["run_dir"]), info["table_id"], info["section_id"], include_persona_feedback=True)
        texts = [r["text"] for r in report["reflections"]]
        assert not any("GEHÖRT NICHT HIERHER" in t for t in texts)


# ----------------------------------------------------------------------------
# P13-5: Nur Ausgabewrite -- neuer externer Ordner, Kollision/I-O-Fehler
# fuehren nie zu Ueberschreiben/Quellmutation/falschem Vollerfolg.
# ----------------------------------------------------------------------------

def test_p13_5_output_inside_data_dir_or_repo_source_tree_rejected():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "a13root"
        root.mkdir()
        info = build_real_minimal_section_data_dir(root)

        proc_in_data = _run_report([
            "--data-dir", str(info["run_dir"]), "--table", info["table_id"], "--section", info["section_id"],
            "--output-dir", str(info["run_dir"] / "evil-out"),
        ])
        assert proc_in_data.returncode != 0
        assert not (info["run_dir"] / "evil-out").exists()

        evil_repo_out = _REPO_ROOT / "a13-evil-out-2026-09-30-test-probe"
        try:
            proc_in_repo = _run_report([
                "--data-dir", str(info["run_dir"]), "--table", info["table_id"], "--section", info["section_id"],
                "--output-dir", str(evil_repo_out),
            ])
            assert proc_in_repo.returncode != 0
            assert not evil_repo_out.exists()
        finally:
            if evil_repo_out.exists():
                import shutil
                shutil.rmtree(evil_repo_out)


def test_p13_5_output_dir_symlink_escape_into_data_dir_rejected():
    # Regression fuer den End-Critic-Befund vom 2026-09-30 (P13-5): ein
    # --output-dir, das erst UEBER einen Symlink in den geschuetzten
    # Datenbaum fuehrt, darf nicht mehr durchrutschen (Path.absolute() loeste
    # den Symlink nicht auf, Path.resolve() tut es).
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "a13root"
        root.mkdir()
        info = build_real_minimal_section_data_dir(root)
        link_to_data = Path(td) / "link-to-data"
        link_to_data.symlink_to(info["run_dir"], target_is_directory=True)
        escaped_out = link_to_data / "evil-out-via-symlink"

        proc = _run_report([
            "--data-dir", str(info["run_dir"]), "--table", info["table_id"], "--section", info["section_id"],
            "--output-dir", str(escaped_out),
        ])
        assert proc.returncode != 0
        assert not (info["run_dir"] / "evil-out-via-symlink").exists()
        assert not escaped_out.exists()


def test_p13_5_existing_output_dir_never_overwritten():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "a13root"
        root.mkdir()
        info = build_real_minimal_section_data_dir(root)
        out_dir = Path(td) / "out"
        out_dir.mkdir()
        sentinel = out_dir / "already-here.txt"
        sentinel.write_text("darf nicht angefasst werden", encoding="utf-8")
        proc = _run_report(["--data-dir", str(info["run_dir"]), "--table", info["table_id"], "--section", info["section_id"], "--output-dir", str(out_dir)])
        assert proc.returncode != 0
        assert sentinel.read_text(encoding="utf-8") == "darf nicht angefasst werden"
        assert not (out_dir / "report.json").exists()


def test_p13_5_sha256sums_matches_written_files():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "a13root"
        root.mkdir()
        info = build_real_minimal_section_data_dir(root)
        out_dir = Path(td) / "out"
        proc = _run_report(["--data-dir", str(info["run_dir"]), "--table", info["table_id"], "--section", info["section_id"], "--output-dir", str(out_dir)])
        assert proc.returncode == 0, proc.stderr
        sums = {}
        for line in (out_dir / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
            digest, name = line.split("  ", 1)
            sums[name] = digest
        for name, digest in sums.items():
            assert _sha256_file(out_dir / name) == digest


# ----------------------------------------------------------------------------
# R2-Nacharbeit (02_AUFTRAG_REST_A13.md §Eingangsroot, 2026-09-30): Route-
# Redaktion, einheitlicher Rootcheck gegen Elternlink-Escape und der
# abschliessende Snapshot-Vergleich gegen Quellaenderungen waehrend der
# Berichterstellung.
# ----------------------------------------------------------------------------

def test_p13_5_request_route_userinfo_and_query_are_redacted():
    """REPORTFIXTURE: eine Requestroute mit Userinfo/Passwort/Querytoken/
    Fragment darf NIEMALS wortgleich in report.json/md/source-index landen
    -- nur Schema+Host+Port+Pfad bleiben uebrig."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "a13root"
        root.mkdir()
        info = build_real_minimal_section_data_dir(root)
        run_dir = info["run_dir"]
        target = next(
            p for p in sorted((run_dir / "requests").glob("*.json"))
            if json.loads(p.read_text(encoding="utf-8")).get("section_id") == info["section_id"]
        )
        data = json.loads(target.read_text(encoding="utf-8"))
        data["route"] = "http://A13_USER:A13_PASSWORD@127.0.0.1:43111/v1?api_key=A13_QUERY_TOKEN#A13_FRAGMENT"
        target.write_text(json.dumps(data), encoding="utf-8")

        out_dir = Path(td) / "out"
        proc = _run_report([
            "--data-dir", str(run_dir), "--table", info["table_id"], "--section", info["section_id"],
            "--output-dir", str(out_dir),
        ])
        assert proc.returncode == 0, proc.stderr
        blob = b"".join(p.read_bytes() for p in out_dir.glob("*") if p.is_file())
        for sentinel in (b"A13_USER", b"A13_PASSWORD", b"A13_QUERY_TOKEN", b"A13_FRAGMENT"):
            assert sentinel not in blob, f"{sentinel!r} darf nicht in der Ausgabe landen"
        report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
        sanitized = next(r["route"] for r in report["requests"] if r["id"] == data["id"])
        assert sanitized == "http://127.0.0.1:43111/v1"


def test_p13_4_tables_parent_symlink_escape_is_rejected_via_real_process():
    """REPORTFIXTURE: `tables/` wird durch einen Verzeichnislink ersetzt,
    der auf einen Ordner AUSSERHALB des Datenroots zeigt -- der belegte
    Rootcheck-Luecke (A13_OUTSIDE_ROOT_SENTINEL) muss abgewiesen werden.
    Finale-Datei-`is_symlink()` alleine genuegt nicht, da der Elternordner
    selbst der Link ist."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "a13root"
        root.mkdir()
        info = build_real_minimal_section_data_dir(root)
        run_dir = info["run_dir"]
        outside = Path(td) / "outside-data-root"
        (run_dir / "tables").rename(outside)
        table_path = outside / f"{info['table_id']}.json"
        table_data = json.loads(table_path.read_text(encoding="utf-8"))
        table_data["sl_log"][0]["content"] = "A13_OUTSIDE_ROOT_SENTINEL Ausruestung"
        table_path.write_text(json.dumps(table_data), encoding="utf-8")
        (run_dir / "tables").symlink_to(outside, target_is_directory=True)

        out_dir = Path(td) / "out"
        proc = _run_report([
            "--data-dir", str(run_dir), "--table", info["table_id"], "--section", info["section_id"],
            "--output-dir", str(out_dir),
        ])
        assert proc.returncode != 0
        assert not out_dir.exists()
        assert "A13_OUTSIDE_ROOT_SENTINEL" not in proc.stdout
        assert "A13_OUTSIDE_ROOT_SENTINEL" not in proc.stderr


def test_p13_5_source_changed_after_read_is_a_snapshot_hold():
    """REPORTFIXTURE: die Pflichtquelle `tables/<id>.json` wird UNMITTELBAR
    NACH ihrem tatsaechlichen Read veraendert (derselbe echte Dispatcher,
    ein dokumentierter Testinjektions-Wrapper) -- der abschliessende Re-
    Read/Hash-Vergleich muss das als Snapshot-Hold erkennen, kein `COMPLETE`
    auf gemischten Staenden."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "a13root"
        root.mkdir()
        info = build_real_minimal_section_data_dir(root)
        run_dir = info["run_dir"]
        target = run_dir / "tables" / f"{info['table_id']}.json"
        out_dir = Path(td) / "out"
        wrapper = Path(td) / "read_change_wrapper.py"
        wrapper.write_text(
            "import pathlib, json, runpy, sys\n"
            f"target = pathlib.Path({str(target)!r}).resolve()\n"
            "original = pathlib.Path.read_bytes\n"
            "done = False\n"
            "def read_bytes(p):\n"
            "    global done\n"
            "    raw = original(p)\n"
            "    if not done and p.resolve() == target:\n"
            "        done = True\n"
            "        d = json.loads(raw)\n"
            "        d['_A13_REVIEW_CHANGED_AFTER_READ'] = True\n"
            "        p.write_bytes((json.dumps(d) + '\\n').encode())\n"
            "    return raw\n"
            "pathlib.Path.read_bytes = read_bytes\n"
            "sys.argv = sys.argv[1:]\n"
            "runpy.run_path(sys.argv[0], run_name='__main__')\n",
            encoding="utf-8",
        )
        proc = subprocess.run(
            [sys.executable, "-B", str(wrapper), str(MMO_SIM), "report",
             "--data-dir", str(run_dir), "--table", info["table_id"], "--section", info["section_id"],
             "--output-dir", str(out_dir)],
            cwd=str(_REPO_ROOT), capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL,
        )
        assert proc.returncode != 0, proc.stdout + proc.stderr
        assert not out_dir.exists()
        assert "_A13_REVIEW_CHANGED_AFTER_READ" in target.read_text(encoding="utf-8")


# ----------------------------------------------------------------------------
# Optionales Regressionsargument (03 §Ausfuehrungskit): die zwei echten,
# bereits ausgefuehrten synthetischen A23-Endablagen aus REPORT-FIXTURES.json.
# Standardaufruf (run_all.py, keine Argumente) braucht dies NICHT -- die
# Standardpfade oben laufen bereits ohne externes Paket.
# ----------------------------------------------------------------------------

def _fixture_package_journeys(package_root: Path) -> list[dict]:
    spec = json.loads((package_root / "REPORT-FIXTURES.json").read_text(encoding="utf-8"))
    out = []
    for key, entry in spec["fixtures"].items():
        out.append({
            "key": key, "source_data_dir": package_root / entry["data_dir"] / "run",
            "table_id": entry["table_id"], "section_id": entry["section_id"],
            "expected_saved_sl_entries": entry["expected_saved_sl_entries"],
            "request_records_in_run": entry["request_records_in_run"],
            "events_jsonl_present": entry["events_jsonl_present"],
        })
    return out


def run_fixture_package_regression(package_root: str) -> int:
    """Nicht Teil von `run_all.py` (braucht ein externes Paket) -- wird
    gezielt von P13-2 (03_GATES_UND_AUFRUFE.md §Ausfuehrungskit) mit
    `--fixture-package <P>` aufgerufen. Kopiert die zwei ECHTEN,
    bereits abgeschlossenen A23-Endablagen (API+Hybrid) in eine exklusive
    Testkopie und prueft den echten Reportprozess dagegen."""
    import shutil

    package_root_path = Path(package_root).resolve()
    journeys = _fixture_package_journeys(package_root_path)
    failed = 0
    with tempfile.TemporaryDirectory() as td:
        for j in journeys:
            data_copy = Path(td) / j["key"] / "data-copy"
            shutil.copytree(j["source_data_dir"], data_copy)
            out_dir = Path(td) / j["key"] / "out"
            proc = _run_report([
                "--data-dir", str(data_copy), "--table", j["table_id"], "--section", j["section_id"],
                "--output-dir", str(out_dir), "--include-persona-feedback",
            ])
            ok = proc.returncode == 0
            print(f"[{j['key']}] returncode={proc.returncode} stderr={proc.stderr.strip()[:200]!r}")
            if not ok:
                failed += 1
                continue
            report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
            ok = ok and report["sl_log"]["turns"] == j["expected_saved_sl_entries"]
            ok = ok and len(report["requests"]) == j["request_records_in_run"] - 4  # abzgl. 4 lobbyweiten Requests ohne table_id
            ok = ok and report["sl_log"]["events_jsonl_present_but_unused"] == j["events_jsonl_present"]
            ok = ok and report["table"]["table_id"] == j["table_id"]
            print(f"[{j['key']}] OK={ok} sl_turns={report['sl_log']['turns']} requests={len(report['requests'])}")
            if not ok:
                failed += 1
    return 0 if failed == 0 else 1



def test_p13_2_standard_uses_actual_a23_api_and_hybrid_journeys():
    from _a13_report_support import generate_existing_a23_journey_inputs, report_evidence_root
    for info in generate_existing_a23_journey_inputs():
        out = report_evidence_root()/("actual-"+info["profile"]+"-report")
        proc = _run_report(["--data-dir",str(info["run_dir"]),"--table",info["table_id"],
                           "--section",info["section_id"],"--output-dir",str(out),"--include-persona-feedback"])
        assert proc.returncode==0,proc.stderr
        r=json.loads((out/"report.json").read_text())
        assert r["sl_log"]["turns"]==5 and len(r["requests"])==14
        assert set(r["table"]["members"])=={"sniper","tech"}
        assert r["status"]=="PARTIAL" and all(x["private"] is True for x in r["reflections"])
        assert len(list((info["case"]/"tui/after-ui/states").glob("*.json")))==7
        for pk,g in r["completion"]["guards"].items():
            for side in ("start","end"):
                ref=g[f"section_{side}_save_source"];raw=(info["run_dir"]/ref["path"]).read_bytes()
                assert hashlib.sha256(raw).hexdigest()==ref["sha256"]
                assert json.loads(raw)==g[f"section_{side}_save"]
                assert json.loads(raw)["characters"][0]["char_id"]==r["table"]["chrononaut_ids"][pk]
        index=json.loads((out/"source-index.json").read_text())
        for ref in index["files"]:
            assert _sha256_file(info["run_dir"]/ref["path"])==ref["sha256"]
        manifest=(out/"SHA256SUMS").read_text().splitlines()
        assert len(manifest)==4
        for line in manifest:assert _sha256_file(out/line[66:])==line[:64]


def test_p13_3_all_existing_character_and_member_bindings_hold():
    # Deliberately damaged copies of a declared REPORTFIXTURE, never played errors.
    for variant in ("guard-char","plan-char","final-members","before-char","after-other","plan-members"):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);info=build_real_minimal_section_data_dir(root/"data");D=info["run_dir"];E=info["section_id"]
            def read(p):return json.loads(p.read_text())
            def write(p,d):p.write_text(json.dumps(d))
            g=D/"completion"/f"{info['chrononaut_ids']['sniper']}__{E}.json"
            plan=D/"completion"/f"{E}__plan.json";final=D/"completion"/f"{E}__final.json"
            other=info["chrononaut_ids"]["tech"]
            if variant=="guard-char":
                d=read(g);d["chrononaut_id"]=other;write(g,d)
            elif variant=="plan-char":
                d=read(plan);d["members"]["sniper"]["save"]["characters"][0].update(char_id=other,id=other);write(plan,d)
            elif variant=="final-members":
                d=read(final);d["members"]=["sniper","medic"];write(final,d)
            elif variant=="before-char":
                p=D/"current_saves/sniper__versions/0001.json";d=read(p);d["characters"][0].update(char_id=other,id=other);write(p,d)
            elif variant=="after-other":
                d=read(g);p=D/"current_saves/tech__versions/0002.json";d["save_path"]=p.relative_to(D).as_posix();d["save_sha256"]=_sha256_file(p);write(g,d)
            else:
                d=read(plan);d["members"]["medic"]=d["members"].pop("tech");write(plan,d)
            proc=_run_report(["--data-dir",str(D),"--table",info["table_id"],"--section",E,"--output-dir",str(root/"out")])
            assert proc.returncode==3 and not (root/"out").exists(),(variant,proc.stdout,proc.stderr)


def test_p13_2_null_metadata_does_not_make_complete_and_missing_end_is_named():
    for variant in ("null-model","missing-end"):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);info=build_real_minimal_section_data_dir(root/"data");D=info["run_dir"];E=info["section_id"]
            if variant=="null-model":
                p=D/"tables"/(info["table_id"]+".json");d=json.loads(p.read_text());d["sl_log"][0]["gm_model"]=None;p.write_text(json.dumps(d))
            else:(D/"current_saves/sniper__versions/0002.json").unlink()
            proc=_run_report(["--data-dir",str(D),"--table",info["table_id"],"--section",E,"--output-dir",str(root/"out")])
            assert proc.returncode==0,proc.stderr
            r=json.loads((root/"out/report.json").read_text());assert r["status"]=="PARTIAL"
            assert any(("GM-Modell" if variant=="null-model" else "Endsave") in x for x in r["partial_reasons"])


def test_p13_3_used_events_source_is_indexed_without_double_counting():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td);info=build_real_minimal_section_data_dir(root/"data");D=info["run_dir"]
        (D/"events.jsonl").write_text(json.dumps({"event_type":"sl_turn","payload":{"table_id":info["table_id"],"section_id":info["section_id"]}})+"\n")
        proc=_run_report(["--data-dir",str(D),"--table",info["table_id"],"--section",info["section_id"],"--output-dir",str(root/"out")])
        assert proc.returncode==0,proc.stderr
        r=json.loads((root/"out/report.json").read_text());idx=json.loads((root/"out/source-index.json").read_text())
        assert r["sl_log"]["turns"]==2
        refs=[x for x in idx["files"] if x["path"]=="events.jsonl"]
        assert len(refs)==1 and refs[0]["sha256"]==_sha256_file(D/"events.jsonl")

def main() -> int:
    import traceback

    argv = sys.argv[1:]
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--fixture-package", default=None, help="Optional: Pfad zum verifizierten A13-Paket (P) fuer die REPORT-FIXTURES.json-Regression (nicht Teil von run_all.py).")
    args, _unknown = ap.parse_known_args(argv)

    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR {t.__name__}:")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} Tests bestanden.")

    if args.fixture_package:
        print("\n=== --fixture-package Regression (REPORT-FIXTURES.json, API+Hybrid) ===")
        rc = run_fixture_package_regression(args.fixture_package)
        if rc != 0:
            failed += 1
        print("OK   fixture_package_regression" if rc == 0 else "FAIL fixture_package_regression")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
