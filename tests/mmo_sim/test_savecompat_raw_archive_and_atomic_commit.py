#!/usr/bin/env python3
"""
tests/mmo_sim/test_savecompat_raw_archive_and_atomic_commit.py —
ZR-SAVECOMPAT-TERMINAL-20261016-R1, TEST-CATALOG-Gruppe
`raw_archive_and_atomic_commit` (02_SAVEVERTRAG.md §C,
`core/save_compatibility.py` Abschnitt A).

Deckt: JEDE rohe SL-Antwort (auch unvollstaendige/abgeschnittene) wird
append-only unter `save_corrections_raw/<repair_key>.json` gesichert --
unabhaengig davon, ob sie spaeter akzeptiert/verworfen wird; ein
vorhandener Eintrag wird NIE veraendert/entfernt; der Archivstand ist nach
jedem Schreibzugriff von einem FRISCHEN Lesezugriff (simulierter
Neustart/neuer Prozess) GENAUSO lesbar wie zuvor geschrieben (Atomaritaet
-- `core.admission._atomic_write_json`, kein halbgeschriebenes Fragment)."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import mmo_sim.core.save_compatibility as save_compat_core  # noqa: E402

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    if not cond:
        print("FAIL", name)


if __name__ == "__main__":
    REPAIR_KEY = "creation::participant-raw-01::chrono-raw-01"

    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td)

        # ── 0) Leeres Archiv vor dem ersten Schreibzugriff ──────────────────────
        check("empty_archive_before_any_write", save_compat_core.read_raw_archive(run_dir, REPAIR_KEY) == [])

        # ── 1) Drei Antworten nacheinander archivieren, davon eine "abgeschnitten"
        entries_in = [
            {"attempt_no": 1, "request_id": "req-1", "raw_text": '```json\n{"v":7,...}\n```'},
            {"attempt_no": 2, "request_id": "req-2", "raw_text": '```json\n{"v":7, "TRUNCATED'},  # abgeschnitten
            {"attempt_no": 3, "request_id": "req-3", "raw_text": '```json\n{"v":7,"economy":{}}\n```'},
        ]
        paths = []
        for e in entries_in:
            p = save_compat_core.archive_raw_response(
                run_dir, repair_key=REPAIR_KEY, char_id="chrono-raw-01", section_id=None,
                table_id=None, attempt_no=e["attempt_no"], request_id=e["request_id"], raw_text=e["raw_text"],
            )
            paths.append(p)

        check("all_three_writes_target_same_file", len(set(paths)) == 1)

        # ── 2) Neustart-Simulation: frischer `read_raw_archive`-Aufruf (neuer
        #      "Prozess" auf DENSELBEN run_dir) sieht ALLE drei, in Reihenfolge,
        #      byte-/feldgenau, einschliesslich der abgeschnittenen Antwort ─────
        reloaded = save_compat_core.read_raw_archive(run_dir, REPAIR_KEY)
        check("append_only_all_three_present_after_restart", len(reloaded) == 3)
        check(
            "append_only_order_preserved",
            [e["attempt_no"] for e in reloaded] == [1, 2, 3],
        )
        check(
            "truncated_response_archived_unmodified",
            reloaded[1]["raw_text"] == entries_in[1]["raw_text"],
        )
        for idx, e in enumerate(entries_in):
            check(f"entry_{idx}_has_run_figure_section_request_binding", all(
                k in reloaded[idx] for k in ("repair_key", "char_id", "section_id", "table_id", "attempt_no", "request_id", "archived_ts")
            ))
            check(f"entry_{idx}_repair_key_matches", reloaded[idx]["repair_key"] == REPAIR_KEY)

        # ── 3) Negativ: ein vierter Append darf die ersten drei NICHT verändern
        #      (kein "letzter gewinnt", kein Ueberschreiben) ─────────────────────
        before_first_three = json.loads((run_dir / "save_corrections_raw" / f"{REPAIR_KEY.replace('/', '_')}.json").read_text())
        save_compat_core.archive_raw_response(
            run_dir, repair_key=REPAIR_KEY, char_id="chrono-raw-01", section_id=None,
            table_id=None, attempt_no=4, request_id="req-4", raw_text="vierte Antwort",
        )
        after_fourth = save_compat_core.read_raw_archive(run_dir, REPAIR_KEY)
        check("fourth_append_does_not_mutate_earlier_entries", after_fourth[:3] == before_first_three)
        check("fourth_append_adds_exactly_one_new_entry", len(after_fourth) == 4 and after_fourth[3]["attempt_no"] == 4)

        # ── 4) Ein ANDERER repair_key bleibt vollstaendig getrennt (kein
        #      Vermischen verschiedener Figuren/Operationen im selben Archiv) ───
        other_key = "creation::participant-raw-02::chrono-raw-02"
        check("different_repair_key_starts_empty", save_compat_core.read_raw_archive(run_dir, other_key) == [])
        save_compat_core.archive_raw_response(
            run_dir, repair_key=other_key, char_id="chrono-raw-02", section_id=None,
            table_id=None, attempt_no=1, request_id="other-req-1", raw_text="andere Figur",
        )
        check("original_key_archive_unaffected_by_other_key_write", save_compat_core.read_raw_archive(run_dir, REPAIR_KEY) == after_fourth)

    print()
    passed = sum(1 for _, ok in results if ok)
    print(f"{passed}/{len(results)} passed")
    for name, ok in results:
        print(("OK  " if ok else "FAIL"), name)
    sys.exit(0 if passed == len(results) else 1)
