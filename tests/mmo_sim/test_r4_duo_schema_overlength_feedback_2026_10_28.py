#!/usr/bin/env python3
"""
tests/mmo_sim/test_r4_duo_schema_overlength_feedback_2026_10_28.py
-- ZR-N2R-ANSCHLUSS-20261019-R4, Reparatur 1: der an die SL gegebene
Korrektur-/Feedbackweg muss bei einem UEBERLANGEN Array (maxItems) Pfad,
Regel, erlaubte Grenze und tatsaechliche Laenge transportieren -- VOR dem
evtl. auf `MAX_MESSAGE_LENGTH` gekuerzten rohen jsonschema-Text.

Hintergrund (02-FRESH-MAIN-AUFTRAG.md): Die zwei realen Duo-B-Antworten
(Requests 17203d19... / 11e1e2b8...) enthielten je Figur SIEBEN
`continuity.shared_echoes` und ELF `continuity.npc_roster`; beide v7-Schemas
erlauben hoechstens sechs. `save_validation._classify` kuerzte den langen
Fehlertext (grosse Instanz-Repr) auf 500 Zeichen, BEVOR die entscheidende
"zu lang"-/Grenzangabe erschien -- die strukturierte Fehlerart und der
Sollwert existierten, erreichten die SL aber nicht brauchbar. Der
Schemahinweis nannte fuer ein Array nur "Liste", ohne die Obergrenze.

Diese Tests belegen die kleinste echte Produktaenderung:
  - `feedback_items` fuehrt jeden Strukturfehler mit `regel=.../erlaubt=.../
    ist=...` an, VOR dem (ggf. gekuerzten) Originaltext.
  - Bei echter Ueberlaenge (grosse Eintraege, Originaltext > 500 Zeichen und
    damit real gekuerzt) bleiben Grenze (6) und Ist (7/11) trotzdem lesbar.
  - Der schema-abgeleitete Zielhinweis nennt die Obergrenze ("hoechstens 6
    Eintraege").
  - Das Schema wird NICHT gelockert: ein auf sechs reduzierter, sonst
    gueltiger Block hat KEINEN maxItems-Fehler mehr und wird angenommen;
    Spielfakten werden nicht still abgeschnitten (der volle Originaltext
    bleibt angehaengt).

Pure Python, nur `assert`, echter Exitcode -- gleiches Muster wie die
bestehende Suite (kein pytest-Fixture-Zwang)."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.domain.zeitriss import save_correction as sc  # noqa: E402
from mmo_sim.domain.zeitriss import save_validation as sv  # noqa: E402

from _full_v7_fixture import full_v7_save  # noqa: E402

EXPECTED = "CHR-DUOB-OVERLEN-001"
SE_PATH = "/continuity/shared_echoes"
NR_PATH = "/continuity/npc_roster"


def _overlong_block(se_count: int = 7, nr_count: int = 11, big: bool = True) -> dict:
    """Sonst gueltiger v7-Save mit GENAU der realen Ueberlaenge: `se_count`
    schema-gueltige shared_echoes (Pflichtfeld `tag`) und `nr_count`
    npc_roster-Objekte. Mit `big=True` sind die Eintraege gross genug, dass
    die rohe Instanz-Repr die 500-Zeichen-Grenze ueberschreitet und real
    gekuerzt wird -- so wird die Truncation-Survival echt geprueft."""
    block = full_v7_save(EXPECTED, name="Duo B Overlength")
    filler = ("x" * 120) if big else "x"
    block.setdefault("continuity", {})
    block["continuity"]["shared_echoes"] = [
        {"tag": f"echo-{i}", "scope": "shared", "text": f"{filler}-{i}"} for i in range(se_count)
    ]
    block["continuity"]["npc_roster"] = [
        {"id": f"NPC-{i:03d}", "name": f"Nebenfigur {filler} {i}"} for i in range(nr_count)
    ]
    return block


def _array_feedback_lines(acc: sv.AcceptanceResult, path: str) -> list[str]:
    """Nur die Feedbackzeilen des ARRAY-Knotens selbst (z.B.
    '/continuity/shared_echoes'), nicht die der Einzelelemente
    ('/continuity/shared_echoes/0')."""
    prefix_tol = f"[tolerant]{path}:"
    prefix_exp = f"[export]{path}:"
    return [it for it in acc.feedback_items if it.startswith(prefix_tol) or it.startswith(prefix_exp)]


def test_r1a_overlength_feedback_carries_path_rule_limit_and_actual() -> None:
    block = _overlong_block(7, 11)
    acc = sv.validate_save_block(block, EXPECTED)
    assert not acc.accepted, "7 shared_echoes / 11 npc_roster muessen abgelehnt werden (maxItems 6)."

    se_lines = _array_feedback_lines(acc, SE_PATH)
    nr_lines = _array_feedback_lines(acc, NR_PATH)
    assert se_lines, f"Kein Array-Feedback fuer {SE_PATH}: {acc.feedback_items}"
    assert nr_lines, f"Kein Array-Feedback fuer {NR_PATH}: {acc.feedback_items}"

    for line in se_lines:
        head = line.split(" -- ", 1)[0]  # der strukturierte Teil VOR dem Rohtext
        assert "regel=maxItems" in head, head
        assert "erlaubt=6" in head, head
        assert "ist=7" in head, head
    for line in nr_lines:
        head = line.split(" -- ", 1)[0]
        assert "regel=maxItems" in head, head
        assert "erlaubt=6" in head, head
        assert "ist=11" in head, head


def test_r1b_limit_and_actual_survive_real_truncation() -> None:
    """Die Instanz-Repr ist hier real > MAX_MESSAGE_LENGTH und wird gekuerzt
    -- die entscheidenden Fakten stehen trotzdem lesbar davor."""
    block = _overlong_block(7, 11, big=True)
    acc = sv.validate_save_block(block, EXPECTED)
    se_lines = _array_feedback_lines(acc, SE_PATH)
    assert se_lines
    truncated_seen = False
    for line in se_lines:
        head, _, raw = line.partition(" -- ")
        # Fakten stehen VOR dem Rohtext, unabhaengig von dessen Kuerzung.
        assert head.index("erlaubt=6") >= 0 and head.index("ist=7") >= 0
        if "…(gekuerzt)" in raw:
            truncated_seen = True
    assert truncated_seen, "Die grosse Instanz-Repr sollte real gekuerzt worden sein (Truncation-Survival-Fall)."


def test_r1c_schema_target_hint_names_the_upper_bound() -> None:
    block = _overlong_block(7, 11)
    acc = sv.validate_save_block(block, EXPECTED)
    msg = sc.build_correction_message(
        persona_key="p02_breach", char_id=EXPECTED,
        operation_label=f"group:lobby-p01_latch-p02_breach__2-section",
        acceptance=acc, original_block=block, attempt_no=1,
    )
    # Zielform-Abschnitt nennt die Obergrenze fuer beide Arrays.
    hint_lines = [l for l in msg.splitlines() if l.startswith("- ") and "erwartet" in l]
    se_hint = [l for l in hint_lines if SE_PATH in l]
    nr_hint = [l for l in hint_lines if NR_PATH in l]
    assert any("hoechstens 6" in l for l in se_hint), f"shared_echoes-Obergrenze fehlt im Zielhinweis: {se_hint}"
    assert any("hoechstens 6" in l for l in nr_hint), f"npc_roster-Obergrenze fehlt im Zielhinweis: {nr_hint}"


def test_r1d_reduced_to_six_has_no_maxitems_error_schema_not_loosened() -> None:
    """Gegenprobe: genau sechs gueltige Eintraege sind kein maxItems-Fehler
    mehr -- das Schema wird NICHT fuer PASS gelockert, nur korrekt gemeldet."""
    ok_block = _overlong_block(6, 6, big=False)
    acc_ok = sv.validate_save_block(ok_block, EXPECTED)
    maxitems_on_arrays = [
        e for e in acc_ok.structure.errors
        if e.check == "maxItems" and e.path in (SE_PATH, NR_PATH)
    ]
    assert not maxitems_on_arrays, f"Sechs Eintraege duerfen keinen maxItems-Fehler ausloesen: {maxitems_on_arrays}"
    assert acc_ok.accepted, f"Der auf 6/6 reduzierte, sonst gueltige Block muss angenommen werden: {acc_ok.feedback_items}"

    # Sieben bleibt ein echter Fehler (kein heimliches Abschneiden auf PASS).
    seven = _overlong_block(7, 6, big=False)
    acc_seven = sv.validate_save_block(seven, EXPECTED)
    assert not acc_seven.accepted
    assert any(e.check == "maxItems" and e.path == SE_PATH and e.actual == 7 for e in acc_seven.structure.errors)


def test_r1e_no_raw_python_detail_leaks() -> None:
    block = _overlong_block(7, 11)
    joined = "\n".join(sv.validate_save_block(block, EXPECTED).feedback_items)
    for forbidden in ("Traceback", 'File "', "Exception:", "jsonschema.exceptions"):
        assert forbidden not in joined, f"Rohes Python-Detail im Feedback: {forbidden!r}"


def main() -> int:
    tests = [
        test_r1a_overlength_feedback_carries_path_rule_limit_and_actual,
        test_r1b_limit_and_actual_survive_real_truncation,
        test_r1c_schema_target_hint_names_the_upper_bound,
        test_r1d_reduced_to_six_has_no_maxitems_error_schema_not_loosened,
        test_r1e_no_raw_python_detail_leaks,
    ]
    for test in tests:
        test()
        print(f"ok  {test.__name__}")
    print(f"\nall {len(tests)} R4 duo schema-overlength feedback tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
