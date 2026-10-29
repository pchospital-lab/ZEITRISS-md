#!/usr/bin/env python3
"""
tests/mmo_sim/test_r4_continuable_table_unit_guards_2026_10_21.py —
R4-Fix1 (02_JETZT_ENTWICKELN.md §1 "Den Ein-Zug-Stillstand beheben",
ABSCHNITT-A-ROOTCAUSE.md §5): Direkttest des neuen Lese-Helfers
`core.store.find_bound_active_continuable_table`.

Belegt die fail-closed-Grenzen EINZELN und -- als Kern des Fixes -- die
KOMPLEMENTARITAET zum bestehenden `find_bound_active_unplayed_table`:
ein bereits BEGONNENER (nicht-leeres sl_log), aktiver, noch nicht
abgeschlossener Tisch liefert bei `...unplayed...` `None` (korrekt: kein
"ungespielter" Tisch mehr), bei `...continuable...` aber GENAU DIESEN Tisch
(damit der begonnene organische Tisch einen WEITEREN regulaeren Zug bekommt,
statt nach einem Zug stillzustehen).

Schnell, deterministisch, ohne Subprozess-Overhead. Gleiches Muster wie
`test_r2_hauptbefund2_bound_table_recovery.py::test_find_bound_active_
unplayed_table_unit_guards`."""
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

import mmo_sim.core.store as core_store  # noqa: E402

_READY = {"sniper": "CHR-SNIPER-001", "tech": "CHR-TECH-001"}


def _write_table(run_dir: Path, table_id: str, status: str, sl_log=None) -> core_store.Table:
    table = core_store.Table(
        table_id=table_id, leader="sniper", members=["sniper", "tech"],
        chrononaut_ids={"sniper": "CHR-SNIPER-001", "tech": "CHR-TECH-001"},
        run_dir=run_dir, status=status, sl_log=sl_log or [],
        operator_meta={"source_offer_id": f"lobby-offer-{table_id}-sniper-0"},
    )
    table.persist()
    return table


def _write_second_table(run_dir: Path, table_id: str, status: str, sl_log=None) -> core_store.Table:
    """Ein von `_write_table` VOELLIG unabhaengiger zweiter Tisch (eigene
    Mitglieder cqb/face statt sniper/tech) -- fuer die R4-FixB1-Multi-Tisch-
    Faelle, die ZWEI GLEICHZEITIG gebundene, unabhaengige Tische brauchen."""
    table = core_store.Table(
        table_id=table_id, leader="cqb", members=["cqb", "face"],
        chrononaut_ids={"cqb": "CHR-CQB-001", "face": "CHR-FACE-001"},
        run_dir=run_dir, status=status, sl_log=sl_log or [],
        operator_meta={"source_offer_id": f"lobby-offer-{table_id}-cqb-0"},
    )
    table.persist()
    return table


_READY_TWO_TABLES = {**_READY, "cqb": "CHR-CQB-001", "face": "CHR-FACE-001"}


def _fresh_run(td: str) -> Path:
    run_dir = Path(td) / "run"
    (run_dir / "tables").mkdir(parents=True)
    (run_dir / "completion").mkdir(parents=True)
    return run_dir


def test_r4_continuable_positive_and_complementary_to_unplayed():
    """KERN: ein aktiver, BEREITS GESPIELTER (sl_log>=1), nicht abgeschlossener
    Tisch -- `...unplayed...` lehnt ab (None), `...continuable...` liefert ihn."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _fresh_run(td)
        table = _write_table(run_dir, "lobby-sniper-tech", status="active", sl_log=[{"turn": 1}])
        bound = {"sniper": table.table_id, "tech": table.table_id}

        # Komplementaritaet: genau der Fall, den `...unplayed...` (korrekt)
        # ablehnt, ist der Fall, den `...continuable...` aufgreift.
        assert core_store.find_bound_active_unplayed_table(run_dir, _READY, bound) is None, (
            "ein bereits gespielter Tisch ist fuer den unplayed-/Recovery-Helfer korrekt None"
        )
        found = core_store.find_bound_active_continuable_table(run_dir, _READY, bound)
        assert found is not None and found.table_id == table.table_id, (
            "Fix1: der begonnene, aktive, nicht abgeschlossene Tisch MUSS fortsetzbar sein"
        )


def test_r4_continuable_empty_sl_log_is_not_continuable():
    """Leeres sl_log = unplayed-/Recovery-Fall, NICHT hier (gibt None)."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _fresh_run(td)
        table = _write_table(run_dir, "lobby-sniper-tech", status="active", sl_log=[])
        bound = {"sniper": table.table_id, "tech": table.table_id}
        assert core_store.find_bound_active_continuable_table(run_dir, _READY, bound) is None


def test_r4_continuable_closed_table_never_revived():
    """Ein geschlossener Tisch wird NIE wiederbelebt, auch mit sl_log."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _fresh_run(td)
        table = _write_table(run_dir, "lobby-sniper-tech", status="closed", sl_log=[{"turn": 1}])
        bound = {"sniper": table.table_id, "tech": table.table_id}
        assert core_store.find_bound_active_continuable_table(run_dir, _READY, bound) is None


def test_r4_continuable_final_present_is_not_continuable():
    """Ein `__final.json` fuer den Tisch -> abgeschlossen, nicht fortsetzbar."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _fresh_run(td)
        table = _write_table(run_dir, "lobby-sniper-tech", status="active", sl_log=[{"turn": 1}])
        (run_dir / "completion" / f"{table.table_id}-section__final.json").write_text(
            json.dumps({"section_id": f"{table.table_id}-section", "table_id": table.table_id}),
            encoding="utf-8",
        )
        bound = {"sniper": table.table_id, "tech": table.table_id}
        assert core_store.find_bound_active_continuable_table(run_dir, _READY, bound) is None


def test_r4_continuable_open_plan_belongs_to_other_resume_path():
    """Ein offener `__plan.json` (ohne `__final.json`) ist der bestehende
    Finalisierungs-/Ernte-Resume-Pfad, NICHT dieser Mid-Play-Helfer."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _fresh_run(td)
        table = _write_table(run_dir, "lobby-sniper-tech", status="active", sl_log=[{"turn": 1}])
        (run_dir / "completion" / f"{table.table_id}-section__plan.json").write_text(
            json.dumps({"section_id": f"{table.table_id}-section", "table_id": table.table_id}),
            encoding="utf-8",
        )
        bound = {"sniper": table.table_id, "tech": table.table_id}
        assert core_store.find_bound_active_continuable_table(run_dir, _READY, bound) is None


def test_r4_continuable_ambiguous_multiple_tables_stays_none():
    """Gebundene Mitglieder verweisen auf ZWEI Tisch-IDs -- kein Raten."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _fresh_run(td)
        _write_table(run_dir, "lobby-sniper-tech", status="active", sl_log=[{"turn": 1}])
        _write_table(run_dir, "lobby-sniper-tech__2", status="active", sl_log=[{"turn": 1}])
        bound = {"sniper": "lobby-sniper-tech", "tech": "lobby-sniper-tech__2"}
        assert core_store.find_bound_active_continuable_table(run_dir, _READY, bound) is None


def test_r4_continuable_chrononaut_mismatch_stays_none():
    """Konsistenzabgleich: abweichende bereite chrononaut_ids -> kein Treffer."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _fresh_run(td)
        table = _write_table(run_dir, "lobby-sniper-tech", status="active", sl_log=[{"turn": 1}])
        bound = {"sniper": table.table_id, "tech": table.table_id}
        mismatched = {"sniper": "CHR-SNIPER-001", "tech": "CHR-OTHER-999"}
        assert core_store.find_bound_active_continuable_table(run_dir, mismatched, bound) is None


def test_r4_continuable_multi_table_picks_least_advanced():
    """R4-FixB1 (B1-FIX-SPEC.md "Multi-Tisch-Fortsetzung"): ZWEI GLEICHZEITIG
    fortsetzbare, voneinander unabhaengige Tische -- der mit dem KLEINEREN
    `sl_log` (am wenigsten fortgeschritten) wird gewaehlt (faire Round-Robin-
    Progression statt dass ein einziger Tisch immer weiter vorab laeuft)."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _fresh_run(td)
        table_a = _write_table(run_dir, "lobby-sniper-tech", status="active", sl_log=[{"turn": 1}, {"turn": 2}])
        table_b = _write_second_table(run_dir, "lobby-cqb-face", status="active", sl_log=[{"turn": 1}])
        bound = {
            "sniper": table_a.table_id, "tech": table_a.table_id,
            "cqb": table_b.table_id, "face": table_b.table_id,
        }
        found = core_store.find_bound_active_continuable_table(run_dir, _READY_TWO_TABLES, bound)
        assert found is not None and found.table_id == table_b.table_id, (
            f"der weniger fortgeschrittene Tisch (sl_log=1) muss gewinnen, bekam {found}"
        )

        # Tie-Break-Determinismus: gleich lange sl_logs -> kleinere table_id
        # gewinnt (alphabetisch "lobby-cqb-face" < "lobby-sniper-tech").
        table_a_tied = _write_table(run_dir, "lobby-sniper-tech", status="active", sl_log=[{"turn": 1}])
        found_tied = core_store.find_bound_active_continuable_table(run_dir, _READY_TWO_TABLES, bound)
        assert found_tied is not None and found_tied.table_id == table_b.table_id, (
            f"bei Ties muss die kleinere table_id gewinnen, bekam {found_tied}"
        )
        assert len(table_a_tied.sl_log) == len(table_b.sl_log) == 1


def test_r4_continuable_multi_table_skips_closed_foreign():
    """Ein fortsetzbarer Tisch UND ein zweiter, bereits GESCHLOSSENER Tisch
    gleichzeitig gebunden -- nur der gueltige fortsetzbare Tisch wird
    geliefert, der geschlossene wird PRO TISCH uebersprungen (bricht die
    Suche nicht ab)."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _fresh_run(td)
        table_a = _write_table(run_dir, "lobby-sniper-tech", status="active", sl_log=[{"turn": 1}])
        table_b = _write_second_table(run_dir, "lobby-cqb-face", status="closed", sl_log=[{"turn": 1}])
        bound = {
            "sniper": table_a.table_id, "tech": table_a.table_id,
            "cqb": table_b.table_id, "face": table_b.table_id,
        }
        found = core_store.find_bound_active_continuable_table(run_dir, _READY_TWO_TABLES, bound)
        assert found is not None and found.table_id == table_a.table_id, (
            f"der geschlossene Tisch darf die Suche nicht verhindern, bekam {found}"
        )


def test_r4_continuable_ai_personas_filter_excludes_out_of_selection():
    """R4-FixB1-STEP2-SYMMETRIE (Critic-R4-Restluecke): ein fortsetzbarer
    (mid-play, sl_log>=1) Tisch, dessen Mitglieder NICHT vollstaendig in der
    aktuellen Auswahl (`ai_personas`) liegen, darf NICHT zurueckgegeben werden
    -- analog zum ai_personas-Filter in `find_bound_active_unplayed_table`.
    Sonst koennte ein fremder mid-play-Tisch die STEP-2-Fortsetzung der
    tatsaechlich auswaehlbaren Figuren an sich reissen (dasselbe Starvation-
    Muster wie BL1)."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _fresh_run(td)
        table = _write_second_table(run_dir, "lobby-cqb-face", status="active", sl_log=[{"turn": 1}])
        bound = {"cqb": table.table_id, "face": table.table_id}
        # Auswahl deckt die Tischmitglieder NICHT (nur sniper) -> fremder Tisch,
        # MUSS None sein.
        assert core_store.find_bound_active_continuable_table(
            run_dir, _READY_TWO_TABLES, bound, ai_personas=frozenset({"sniper"}),
        ) is None
        # Teil-Ueberlappung (nur cqb in Auswahl, face fehlt) -> ebenfalls None.
        assert core_store.find_bound_active_continuable_table(
            run_dir, _READY_TWO_TABLES, bound, ai_personas=frozenset({"cqb"}),
        ) is None


def test_r4_continuable_ai_personas_none_or_covering_still_found():
    """Gegenprobe zum Filter: ai_personas=None (TUI-Default = alle freien)
    aendert NICHTS; eine Auswahl, die ALLE Tischmitglieder abdeckt, liefert den
    Tisch weiterhin (exact + superset) -- der Filter ist exakt 'alle Mitglieder
    muessen in ai_personas sein', nicht strenger."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _fresh_run(td)
        table = _write_second_table(run_dir, "lobby-cqb-face", status="active", sl_log=[{"turn": 1}])
        bound = {"cqb": table.table_id, "face": table.table_id}
        # Default None -> unveraendert gefunden.
        assert core_store.find_bound_active_continuable_table(run_dir, _READY_TWO_TABLES, bound).table_id == table.table_id
        # Exakte Abdeckung.
        assert core_store.find_bound_active_continuable_table(
            run_dir, _READY_TWO_TABLES, bound, ai_personas=frozenset({"cqb", "face"}),
        ).table_id == table.table_id
        # Superset (Auswahl groesser als Tischmitglieder).
        assert core_store.find_bound_active_continuable_table(
            run_dir, _READY_TWO_TABLES, bound, ai_personas=frozenset({"cqb", "face", "sniper"}),
        ).table_id == table.table_id


if __name__ == "__main__":
    import traceback

    failures = []
    for name, fn in sorted(list(globals().items())):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"OK   {name}")
            except Exception as exc:  # noqa: BLE001
                failures.append(name)
                print(f"FAIL {name}: {exc}")
                traceback.print_exc()
    total = len([n for n in globals() if n.startswith("test_")])
    print(f"\n{total - len(failures)}/{total} Tests bestanden.")
    raise SystemExit(0 if not failures else 1)
