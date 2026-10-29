#!/usr/bin/env python3
"""
tests/mmo_sim/test_f_s2_closed_control_2026_10_18.py -- F-S2-CLOSED-CONTROL
(ZR-N2-LIVEBUNDLE-FRESH-20261018-R1), konsolidierter Beleg fuer drei bereits
im Produktcode (`core.store.find_bound_active_unplayed_table`) vorhandene,
aber bisher auf mehrere Testdateigenerationen verteilte Eigenschaften -- hier
EXPLIZIT in EINER Datei zusammengefuehrt, mit der im Auftrag verlangten
Korrektur der Zuordnung:

1. POSITIV (muss erhalten bleiben): der echte, bereits bestehende
   ZWEIPROZESSIGE Lobby-Recovery-Fall -- `os._exit` nach dem durabel
   empfangenen Abschluss-Beleg, zweiter Prozess finalisiert OHNE erneuten
   GM-Call (`test_s2_lobby_resume_pre_plan_completion_recovery.py::
   test_s2_positive_recovery_pre_plan_crash_resumes_exactly_once_no_new_
   model_calls`). Wird hier durch ECHTEN Aufruf derselben Funktion erneut
   bestaetigt (Komposition, keine Zweitimplementierung).

2. KORRIGIERTE ZUORDNUNG: ein AKTIVER Tisch OHNE Abschluss-Marker ist NICHT
   finalisiert -- `find_bound_active_unplayed_table` liefert dafuer `None`
   (weiterspielen/neu anfragen bleibt moeglich), aber das bedeutet NICHT
   "dieser Tisch ist bereits erledigt". Die bisherige Testlandschaft prueft
   zwar denselben Fall (`test_s2_negative_real_play_without_marker_stays_
   rejected`), benennt die Unterscheidung aber nirgends explizit am
   `Table.status`-Feld selbst -- das wird hier nachgezogen: `table.status`
   bleibt `"active"` (NICHT `"closed"`), der Tisch ist schlicht noch nicht
   markiert abgeschlossen, keine Finalisierung.

3. Ein tatsaechlich GESCHLOSSENER/finalisierter Tisch (`status="closed"`),
   geprueft ueber denselben NORMALEN Lesepfad wie der Produkt-Einstieg
   (`core.store.find_bound_active_unplayed_table`, von `ui/tui.py:_cmd_
   lobby_initiative` aufgerufen): keine zweite Uebernahme (liefert `None`),
   KEIN neuer Transport-Call ausgeloest (der Helfer selbst tut nie I/O
   jenseits des einen Lesezugriffs), UND kein Ueberschreiben der Tischdatei
   (Bytes/mtime der persistierten `Table`-Datei bleiben nach dem Aufruf
   IDENTISCH -- reiner Lesezugriff, keine Mutation).

WICHTIG (Auftrag: "klar dokumentieren"): der oben unter (1) referenzierte
Test ist ein ZWEISPIELERIGER (sniper/tech) Recovery-Beleg fuer GENAU EINEN
Tischabschluss -- er ist NICHT der fuenfspielerige 2+3-A/B-Liveweg-Beleg
(Hybrid-2-Import+3-Neu, zwei volle Abschnitte A/B). Dieser Liveweg-Beleg
liegt in `worker/proofs/offline_2plus3_dryrun_*` (s. N2L-A-REPORT.md),
NICHT in dieser Datei."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from mmo_sim.core import store as core_store  # noqa: E402

import test_s2_lobby_resume_pre_plan_completion_recovery as s2_mod  # noqa: E402
import test_r2_hauptbefund2_bound_table_recovery as r2_mod  # noqa: E402


def test_f_s2_1_positive_two_process_recovery_is_preserved():
    """Komposition: ruft den bestehenden, echten Zweiprozess-Positivtest
    UNVERAENDERT auf -- jede zukuenftige Regression an diesem Pfad schlaegt
    hier sofort sichtbar mit auf."""
    s2_mod.test_s2_positive_recovery_pre_plan_crash_resumes_exactly_once_no_new_model_calls()


def test_f_s2_2_active_table_without_marker_is_not_finalized():
    """KORRIGIERTE ZUORDNUNG: ein aktiver Tisch ohne Abschluss-Marker bleibt
    `status="active"` -- `find_bound_active_unplayed_table` liefert `None`
    (nicht automatisch wiederaufnehmbar als geernteter Abschluss), aber das
    heisst NICHT, der Tisch sei bereits erledigt/geschlossen. Beide Fakten
    werden hier GEMEINSAM explizit geprueft, nicht nur das `None`-Ergebnis
    allein (das liesse offen, OB der Grund 'schon fertig' oder 'noch aktiv,
    nur kein Marker' ist)."""
    from mmo_sim.core.completion_marker import completion_marker_matches
    from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER

    ready_ids = {"sniper": "CHR-SNIPER-001", "tech": "CHR-TECH-001"}
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        (run_dir / "tables").mkdir(parents=True)
        (run_dir / "completion").mkdir(parents=True)
        table = core_store.Table(
            table_id="lobby-sniper-tech", leader="sniper", members=["sniper", "tech"],
            chrononaut_ids={"sniper": "CHR-SNIPER-001", "tech": "CHR-TECH-001"},
            run_dir=run_dir, status="active",
            sl_log=[{
                "section_id": "lobby-sniper-tech-section",
                "content": "Ihr beratet euch kurz, bevor ihr weiterzieht.",
                "expected_prev_ref_by_member": {"sniper": None, "tech": None},
            }],
        )
        table.persist()
        bound = {"sniper": "lobby-sniper-tech", "tech": "lobby-sniper-tech"}

        found = core_store.find_bound_active_unplayed_table(
            run_dir, ready_ids, bound, marker=COMPLETION_MARKER, marker_matches=completion_marker_matches,
        )
        assert found is None, "kein Marker -> nicht automatisch als geernteter Abschluss wiederaufnehmbar"

        # Die eigentliche, korrigierte Zuordnung: NICHT "schon erledigt".
        reloaded = core_store.Table.load(run_dir, "lobby-sniper-tech")
        assert reloaded.status == "active", (
            f"ein Tisch ohne Marker bleibt aktiv/unfinalisiert, status={reloaded.status!r} waere die "
            "falsche Zuordnung 'schon erledigter Tisch' fuer einen lediglich noch unmarkierten Tisch."
        )
        assert not core_store._table_has_final(run_dir, "lobby-sniper-tech"), (
            "kein __final.json -- strukturell kein finalisierter Abschnitt."
        )


def test_f_s2_3_truly_closed_table_via_normal_entry_point_is_never_retaken():
    """Ein tatsaechlich GESCHLOSSENER Tisch (status='closed'), geprueft
    ueber denselben Lesepfad wie der normale Produkt-Einstieg
    (`ui/tui.py:_cmd_lobby_initiative` -> `core.store.find_bound_active_
    unplayed_table`): keine zweite Uebernahme (`None`), kein Ueberschreiben
    der Tischdatei (Bytes + mtime unveraendert -- reiner Lesezugriff)."""
    ready_ids = {"sniper": "CHR-SNIPER-001", "tech": "CHR-TECH-001"}
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        (run_dir / "tables").mkdir(parents=True)
        (run_dir / "completion").mkdir(parents=True)
        table = r2_mod._write_table(run_dir, "lobby-sniper-tech", status="closed")
        table_path = run_dir / "tables" / f"{table.table_id}.json"
        bytes_before = table_path.read_bytes()
        mtime_before = table_path.stat().st_mtime_ns

        # Widerspruechlich verbliebene Lock-Eintragung (wie nach einem Crash
        # zwischen Lock-Release und Statuswechsel) -- der haertere Fall als
        # "gar kein Lock mehr", belegt zusaetzlich "kein Ueberschreiben".
        bound = {"sniper": table.table_id, "tech": table.table_id}
        found = core_store.find_bound_active_unplayed_table(run_dir, ready_ids, bound)
        assert found is None, "ein bereits geschlossener Tisch darf NIE erneut uebernommen werden."

        bytes_after = table_path.read_bytes()
        mtime_after = table_path.stat().st_mtime_ns
        assert bytes_after == bytes_before, "kein Ueberschreiben der Tischdatei durch den reinen Lesepfad."
        assert mtime_after == mtime_before, "kein Schreibzugriff (mtime unveraendert) auf einen bereits geschlossenen Tisch."

        # Bestaetigt zusaetzlich (Ergaenzung zu r2_mod, keine Dopplung): auch
        # ohne jeden widerspruechlichen Lock liefert derselbe Helfer sofort
        # None, OHNE die Tischdatei ueberhaupt gebunden zu betrachten.
        empty_bound: dict[str, str] = {}
        assert core_store.find_bound_active_unplayed_table(run_dir, ready_ids, empty_bound) is None


def test_f_s2_4_existing_closed_table_two_full_rounds_regression_still_passes():
    """Komposition: der bestehende Positivbeleg fuer "geschlossener Tisch
    bleibt geschlossen, spaetere neue Runde moeglich" (echter Zweiprozess-
    Spielabschluss + danach ein NEUES Fenster) lebt in `test_r2_
    hauptbefund2_bound_table_recovery.py` -- hier referenziert, nicht
    dupliziert, damit eine Regression dort auch hier sichtbar wird."""
    r2_mod.test_hauptbefund2_closed_table_two_full_rounds_real_restart_new_round_possible()


def _run(name: str, fn) -> bool:
    import traceback
    try:
        fn()
    except Exception as e:  # noqa: BLE001
        print(f"FAIL {name}: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False
    print(f"PASS {name}")
    return True


if __name__ == "__main__":
    tests = [
        ("test_f_s2_1_positive_two_process_recovery_is_preserved",
         test_f_s2_1_positive_two_process_recovery_is_preserved),
        ("test_f_s2_2_active_table_without_marker_is_not_finalized",
         test_f_s2_2_active_table_without_marker_is_not_finalized),
        ("test_f_s2_3_truly_closed_table_via_normal_entry_point_is_never_retaken",
         test_f_s2_3_truly_closed_table_via_normal_entry_point_is_never_retaken),
        ("test_f_s2_4_existing_closed_table_two_full_rounds_regression_still_passes",
         test_f_s2_4_existing_closed_table_two_full_rounds_regression_still_passes),
    ]
    results = [_run(name, fn) for name, fn in tests]
    print(f"\n{sum(results)}/{len(results)} passed")
    sys.exit(0 if all(results) else 1)
