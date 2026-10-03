#!/usr/bin/env python3
"""
tests/mmo_sim/test_r2d_lobby_resume_belegkette_guard.py — neue dauerhafte
Repo-Regression fuer die zwei Belegketten-Relationen aus MAIN-QUELLENENT-
SCHEIDUNG-BELEGKETTE.md (extern: `tests-review/review_resume_consistency.py`
im Lieferpaket, NICHT Teil dieses Repos):

- R1: eine gesamte Resolutionmenge fuer dieselbe Angebots-Kennung darf keinen
  widerspruechlichen Eintrag verdecken, nur weil AUCH ein passender Eintrag
  existiert (frueher: `offer_resolution_exists` liefert True beim ersten
  Treffer -- `[passend, widersprueclich]` haelt NICHT an).
- R2: der Mitgliedervergleich allein beweist keine vollstaendige Figuren-/
  Lockbindung -- ein fehlender `Table.chrononaut_ids`-Eintrag ODER ein
  fehlender Mitgliedslock darf keine Personaentscheidung mehr erreichen.

Reuse (kein zweiter Bootstrap-Baustein, `MAIN-QUELLENENTSCHEIDUNG-
BELEGKETTE.md` "Prozess-Haertung"): dieselbe Subprozess-/Child-/Fixture-
Technik wie `test_r2c_lobby_resume_zuordnung_guard.py` -- `_seed`,
`_run_child`, `_own_decision_calls` und der Child-Entry-Point (`--child`)
werden von dort importiert und unveraendert wiederverwendet, keine zweite
Kopie. Kein `run_play_session`-Rettungscallback -- alle Faelle laufen ueber
den tatsaechlichen, unveraenderten Spielstart-Pfad
(`ui/tui.py:_play_bound_table` -> `app_service.run_play_session`);
Assertions pruefen echte Diskzustaende (Tabellenstatus/Locks/Currents/Log/
States als vollstaendiger Byte-Hash), nicht bloss Log-/Helfererfolg.

Ueber den Dateinamen `test_*.py` automatisch in `run_all.py` eingebunden."""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import test_r2c_lobby_resume_zuordnung_guard as r2c  # noqa: E402


def _protected_snapshot(root: Path) -> dict[str, str]:
    """Byte-genauer Fingerabdruck aller geschuetzten Belege (Tische, Locks,
    Angebots-/Resolutionlog, veroeffentlichte Currents, States) -- der
    Konsistenz-Guard darf beim Hold KEINE davon veraendern, auch nicht
    zusaetzlich zur bewusst gesetzten Testkorruption."""
    paths = [root / "run" / "locks.json", root / "run" / "invitation_decisions.jsonl"]
    for d in (root / "run" / "tables", root / "run" / "current_saves", root / "states"):
        if d.exists():
            paths.extend(p for p in d.rglob("*") if p.is_file())
    return {
        p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in paths if p.exists()
    }


def _hold_then_restore_case(corrupt, label: str) -> dict:
    """Gemeinsames Geruest fuer R1/R2-Konflikte: B2-Tisch anlegen (Resolution
    bereits geschrieben, GM-Konstruktion einmalig fehlgeschlagen -- derselbe
    unterbrochene Zustand wie `test_r2c`), EINE begrenzte, wohlgeformte
    widerspruechliche Testeingabe injizieren (Originalbytes separat
    aufbewahrt), Resume-Versuch beobachten (muss VOR jeder Personaentscheidung
    und jedem GM-Turn kontrolliert offen bleiben, geschuetzte Bytes exakt
    unveraendert), Originalbytes wiederherstellen, echten Restore-Resume
    beobachten (muss danach real abschliessen, ohne erneute Zustimmung)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        r2c._seed(root)

        r1 = r2c._run_child(root, "gm-init-failure", root / f"{label}-r1.json")
        assert not r1["errors"], r1["errors"]
        assert len(r1["tables"]) == 1 and r1["tables"][0]["status"] == "active"
        assert r1["gm_calls"] == 0
        assert '"outcome": "table_bound"' in r1["offers"]
        tid = r1["tables"][0]["table_id"]

        table_path = root / "run" / "tables" / f"{tid}.json"
        offers_path = root / "run" / "invitation_decisions.jsonl"
        locks_path = root / "run" / "locks.json"
        original_table_bytes = table_path.read_bytes()
        original_offers_bytes = offers_path.read_bytes()
        original_locks_bytes = locks_path.read_bytes()

        corrupt(table_path, offers_path, locks_path)
        before = _protected_snapshot(root)

        r2 = r2c._run_child(root, "pause", root / f"{label}-r2-conflict.json")
        after = _protected_snapshot(root)

        assert not r2["errors"], "eine konkrete kontrollierte Meldung wird erwartet, keine rohe Ausnahme (z.B. KeyError)"
        assert r2c._own_decision_calls(r2) == 0, "kein Persona-/Consent-Call vor dem Hold"
        assert r2["gm_calls"] == 0, "kein GM-/Spielstart bei widerspruechlichen Belegen"
        assert r2["tables"][0]["status"] == "active", "Tisch bleibt bei widerspruechlichen Belegen aktiv"
        assert before == after, (
            "geschuetzte Bytes (Tables/Locks/Angebotslog/Currents/States) duerfen sich "
            "beim Hold NICHT zusaetzlich veraendern"
        )
        assert any(tid in p for p in r2["printed"]), f"konkrete Tisch-ID in der Meldung erwartet: {r2['printed']}"

        table_path.write_bytes(original_table_bytes)
        offers_path.write_bytes(original_offers_bytes)
        locks_path.write_bytes(original_locks_bytes)

        r3 = r2c._run_child(root, "pause", root / f"{label}-r3-restored.json")
        assert not r3["errors"], r3["errors"]
        assert len(r3["tables"]) == 1 and r3["tables"][0]["table_id"] == tid
        assert r3["tables"][0]["status"] == "closed", "nach Wiederherstellung muss derselbe Tisch real abschliessen"
        assert r3["gm_calls"] >= 3
        assert not r3["locks"]
        assert all(v is not None for v in r3["current_ids"].values())
        assert r2c._own_decision_calls(r3) == 0, "kein erneuter Initiativ-/Consent-Request nach Restore-Resume"
        return {"table_id": tid, "conflict_held_open": True, "restore_resume_completed": True}


def _resolution_row(offers_path: Path, source_offer_id: str) -> dict:
    rows = [json.loads(line) for line in offers_path.read_text(encoding="utf-8").splitlines()]
    return next(dict(r) for r in rows if r.get("type") == "resolution" and r.get("offer_id") == source_offer_id)


def _corrupt_mixed_resolution_set(table_path: Path, offers_path: Path, locks_path: Path) -> None:
    """R1: eine ZUSAETZLICHE, widerspruechliche Resolution (andere table_id)
    NEBEN der weiterhin vorhandenen passenden Resolution derselben Angebots-
    Kennung -- die passende darf den Widerspruch nicht verdecken."""
    obj = json.loads(table_path.read_text(encoding="utf-8"))
    source = obj["operator_meta"]["source_offer_id"]
    match = _resolution_row(offers_path, source)
    wrong = dict(match, table_id="synthetic-contradictory-other-table")
    rows = [json.loads(line) for line in offers_path.read_text(encoding="utf-8").splitlines()]
    rows = [wrong] + rows  # Widerspruch VOR dem passenden Eintrag -- Reihenfolge ist irrelevant.
    offers_path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def _corrupt_missing_chrononaut_entry(table_path: Path, offers_path: Path, locks_path: Path) -> None:
    """R2: `Table.chrononaut_ids['sniper']` fehlt, `Table.members` und die
    Locks bleiben unveraendert -- frueher: eine Personaentscheidung, danach
    roher `KeyError('sniper')` tief in der Harvest-Pruefung."""
    obj = json.loads(table_path.read_text(encoding="utf-8"))
    assert "sniper" in obj["chrononaut_ids"], "Testannahme verletzt: 'sniper' fehlte bereits vor der Korruption"
    del obj["chrononaut_ids"]["sniper"]
    table_path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def _corrupt_missing_member_lock(table_path: Path, offers_path: Path, locks_path: Path) -> None:
    """R2: der einzige Lockeintrag der Sniper-Figur fehlt, Tech bleibt korrekt
    gebunden -- frueher reichte dem Kandidatenfinder die noch gebundene
    Tech-Persona, der ganze Abschnitt lief durch."""
    obj = json.loads(table_path.read_text(encoding="utf-8"))
    cid = obj["chrononaut_ids"]["sniper"]
    locks = json.loads(locks_path.read_text(encoding="utf-8"))
    assert cid in locks, "Testannahme verletzt: Sniper-Lock fehlte bereits vor der Korruption"
    del locks[cid]
    locks_path.write_text(json.dumps(locks, ensure_ascii=False, indent=2), encoding="utf-8")


def test_belegkette_guard_mixed_resolution_set_holds_then_restores():
    """R1 (MAIN-QUELLENENTSCHEIDUNG-BELEGKETTE.md): ein passender Resolution-
    Eintrag darf einen weiteren, widerspruechlichen Eintrag derselben
    Angebots-Kennung nicht verdecken."""
    result = _hold_then_restore_case(_corrupt_mixed_resolution_set, "01-mixed-resolution")
    assert result["conflict_held_open"] and result["restore_resume_completed"]


def test_belegkette_guard_missing_chrononaut_entry_holds_then_restores():
    """R2: ein fehlender `chrononaut_ids`-Eintrag fuer ein weiterhin in
    `members` gelistetes Mitglied muss VOR jeder Personaentscheidung
    kontrolliert offenhalten."""
    result = _hold_then_restore_case(_corrupt_missing_chrononaut_entry, "02-missing-chrononaut")
    assert result["conflict_held_open"] and result["restore_resume_completed"]


def test_belegkette_guard_missing_member_lock_holds_then_restores():
    """R2: ein fehlender Mitgliedslock (bei sonst vollstaendiger
    chrononaut_ids-Zuordnung) muss ebenso VOR jeder Personaentscheidung
    kontrolliert offenhalten -- der Kandidatenfinder allein ist kein
    Vollstaendigkeitsbeweis."""
    result = _hold_then_restore_case(_corrupt_missing_member_lock, "03-missing-lock")
    assert result["conflict_held_open"] and result["restore_resume_completed"]


def test_belegkette_guard_consistent_duplicate_and_foreign_offer_allows_resume():
    """Erhalt (kein Rueckbau): zwei IDENTISCHE passende Resolutionen und ein
    unabhaengiger Fremd-Offer-Eintrag im selben Log duerfen ein gesundes
    Resume NICHT verhindern -- ein pauschales Duplikat-/Fremd-Offer-Verbot
    waere der falsche Nachzug."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        r2c._seed(root)

        r1 = r2c._run_child(root, "gm-init-failure", root / "04-dup-r1.json")
        assert not r1["errors"], r1["errors"]
        assert len(r1["tables"]) == 1 and r1["tables"][0]["status"] == "active"
        tid = r1["tables"][0]["table_id"]

        table_path = root / "run" / "tables" / f"{tid}.json"
        offers_path = root / "run" / "invitation_decisions.jsonl"
        obj = json.loads(table_path.read_text(encoding="utf-8"))
        source = obj["operator_meta"]["source_offer_id"]
        match = _resolution_row(offers_path, source)
        foreign = dict(match, offer_id="synthetic-unrelated-offer", table_id="synthetic-unrelated-table")
        rows = [json.loads(line) for line in offers_path.read_text(encoding="utf-8").splitlines()]
        rows = [foreign] + rows + [dict(match)]
        offers_path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")

        r2 = r2c._run_child(root, "pause", root / "04-dup-r2-resume.json")
        assert not r2["errors"], r2["errors"]
        assert r2["tables"][0]["status"] == "closed", (
            "identische Duplikate + irrelevanter Fremd-Offer-Eintrag duerfen ein gesundes Resume NICHT verhindern"
        )
        assert r2["gm_calls"] >= 3
        assert not r2["locks"]
        assert all(v is not None for v in r2["current_ids"].values())
        assert r2c._own_decision_calls(r2) == 0, "kein neuer Initiativ-/Consent-Request bei konsistenter Wiederaufnahme"


if __name__ == "__main__":
    import traceback

    tests = [
        test_belegkette_guard_consistent_duplicate_and_foreign_offer_allows_resume,
        test_belegkette_guard_mixed_resolution_set_holds_then_restores,
        test_belegkette_guard_missing_chrononaut_entry_holds_then_restores,
        test_belegkette_guard_missing_member_lock_holds_then_restores,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
            passed += 1
        except Exception:
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed}/{len(tests)} Tests bestanden.")
    sys.exit(0 if failed == 0 else 1)
