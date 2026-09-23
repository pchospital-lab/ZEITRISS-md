#!/usr/bin/env python3
"""
tests/mmo_sim/test_m2_onboarding_import_catalog.py — A17/A18/A19/A20/A21/A27
(11 §§3-6, 9).

Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import json
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.domain.zeitriss import catalog, import_export, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.registry.participants import ApplicationRecordRef, ParticipantRegistry  # noqa: E402


def _v7_block(char_id: str, level: int = 1) -> dict:
    return {"v": 7, "characters": [{"char_id": char_id, "level": level, "name": "Test"}]}


# ── A17: geführte Einzel-Erschaffung, resumable, kein Dummy vor Save ────────────

def test_a17_onboarding_resumable_no_dummy_before_valid_save():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        s1 = onboarding.start_or_resume(d, "participant-1")
        assert s1.status == "in_progress"
        assert s1.final_save is None

        onboarding.record_step(d, "participant-1", "Wie heisst deine Figur?", "Nova")
        # Simulierter Abbruch VOR erstem Save: erneuter Aufruf setzt fort, kein Duplikat.
        s2 = onboarding.start_or_resume(d, "participant-1")
        assert s2.status == "in_progress"
        assert len(s2.steps) == 1, "Fortsetzen darf den bisherigen Fortschritt nicht verlieren/duplizieren"

        validator = ZeitrissHarvestValidator()
        invalid_block = {"not_v7": True}
        try:
            onboarding.complete_with_save(d, "participant-1", invalid_block, validator, "chrono-nova")
            assert False, "ungueltiger Block haette abgelehnt werden muessen (kein Dummy-v7)"
        except ValueError:
            pass
        still_open = onboarding.start_or_resume(d, "participant-1")
        assert still_open.status == "in_progress", "nach abgelehntem Save bleibt die Erschaffung offen"

        final = onboarding.complete_with_save(d, "participant-1", _v7_block("chrono-nova"), validator, "chrono-nova")
        assert final.status == "completed"
        resumed_after_done = onboarding.start_or_resume(d, "participant-1")
        assert resumed_after_done.status == "completed"


# ── A18: vollstaendiger Export als Text + Roundtrip-Import ──────────────────────

def test_a18_export_then_import_roundtrip_is_stable():
    block = _v7_block("chrono-roundtrip", level=42)
    text = import_export.export_save_text(block)
    preview = import_export.preview_import(text)
    assert preview.char_id == "chrono-roundtrip"
    assert preview.level == 42
    assert preview.single_char_ok


# ── A19: defekter/unvollstaendiger Import wird ohne Write abgelehnt ────────────

def test_a19_malformed_import_rejected_without_write():
    try:
        import_export.preview_import("das ist kein JSON")
        assert False
    except import_export.MalformedImportError:
        pass
    try:
        import_export.preview_import(json.dumps({"v": 7, "characters": [{}, {}]}))  # 2 Figuren -> Vertragsbruch
        assert False, "Sammelbloecke mit mehreren Figuren muessen abgelehnt werden"
    except import_export.MalformedImportError:
        pass


# ── A20: bekannte Char-ID, abweichender Save -> explizite Wahl noetig ──────────

def test_a20_known_char_id_conflict_requires_explicit_choice():
    existing = _v7_block("chrono-known", level=5)
    incoming = _v7_block("chrono-known", level=9)
    identical = import_export.resolve_import(
        existing, known_char_ids={"chrono-known"}, existing_block_for_char_id=existing,
        active_binding=False, open_completion_order=False,
    )
    assert identical.action == "noop_identical"

    unresolved = import_export.resolve_import(
        incoming, known_char_ids={"chrono-known"}, existing_block_for_char_id=existing,
        active_binding=False, open_completion_order=False,
    )
    assert unresolved.action == "parked", "ohne explizite Wahl darf NICHT automatisch gemischt/hochgelevelt werden"

    resolved = import_export.resolve_import(
        incoming, known_char_ids={"chrono-known"}, existing_block_for_char_id=existing,
        active_binding=False, open_completion_order=False, explicit_choice="adopt_incoming",
    )
    assert resolved.action == "adopt_incoming"
    assert resolved.block == incoming

    new_figure = import_export.resolve_import(
        _v7_block("chrono-brandnew"), known_char_ids={"chrono-known"}, existing_block_for_char_id=None,
        active_binding=False, open_completion_order=False,
    )
    assert new_figure.action == "register_new"

    parked_active = import_export.resolve_import(
        incoming, known_char_ids={"chrono-known"}, existing_block_for_char_id=existing,
        active_binding=True, open_completion_order=False,
    )
    assert parked_active.action == "parked"


# ── A21: Katalog — Wechsel nur an sauberer Abschnittsgrenze ─────────────────────

def test_a21_catalog_switch_blocked_during_open_section():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        catalog.register(d, catalog.CatalogEntry("p1", "chrono-a", "p1_persona"))
        catalog.register(d, catalog.CatalogEntry("p1", "chrono-b", "p1_persona"))
        catalog.bind_for_section(d, "p1", "chrono-a", has_open_section=False)
        assert catalog.last_selected(d, "p1") == "chrono-a"

        try:
            catalog.bind_for_section(d, "p1", "chrono-b", has_open_section=True)
            assert False, "Wechsel waehrend offenem Abschnitt haette blockiert werden muessen"
        except catalog.ActiveBindingError:
            pass

        # Nach sauberer Abschnittsgrenze (has_open_section=False) ist der Wechsel erlaubt.
        catalog.bind_for_section(d, "p1", "chrono-b", has_open_section=False)
        assert catalog.last_selected(d, "p1") == "chrono-b"

        entries = catalog.list_for_participant(d, "p1")
        assert {e.chrononaut_id for e in entries} == {"chrono-a", "chrono-b"}


# ── A27 (Registry-Haelfte): neutraler Dummy-Datensatz, kein Char-ID-Wissen ─────

def test_a27_neutral_registry_dummy_record():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        reg = ParticipantRegistry(d)
        p = reg.register_participant(kind="human", display_name="Testperson")
        reg.add_record_ref(p.participant_id, ApplicationRecordRef(
            record_id="dummy-record-1", schema="dummy-v1", version="1",
            owner_participant_id=p.participant_id, source="local",
        ))
        loaded = reg.load_participant(p.participant_id)
        assert len(loaded.record_refs) == 1
        assert loaded.record_refs[0].schema == "dummy-v1"
        # Ein zweiter, ANDERER Datensatz fuer denselben Teilnehmer ist erlaubt
        # (keine "ein Teilnehmer = ein Datensatz"-Regel im neutralen Kern, 11 §9).
        reg.add_record_ref(p.participant_id, ApplicationRecordRef(
            record_id="dummy-record-2", schema="dummy-v1", version="1",
            owner_participant_id=p.participant_id, source="local",
        ))
        assert len(reg.load_participant(p.participant_id).record_refs) == 2


def main() -> int:
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
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
