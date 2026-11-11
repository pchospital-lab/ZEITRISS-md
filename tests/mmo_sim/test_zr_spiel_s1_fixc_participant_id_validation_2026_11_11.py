#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_spiel_s1_fixc_participant_id_validation_2026_11_11.py —
ZR-SPIEL-S1 Fix C (LINUS-SPEC.md §Fix C): `scripts/mmo_sim.py::_resolve_
participant_id` uebernahm bisher eine explizite `--participant`-ID oder eine
aus `last_participant.json` gelesene ID OHNE Validierung -- eine
schemawidrige ID (z.B. `la1-l-tui-demo`, Bindestrich) lief erst spaet in
`persona_state.save_state`->`validate_state` (`^[a-z][a-z0-9_]*$`) und hatte
bereits Modellaufrufe verbraucht.

Fix: `mmo_sim/core/identity.py` bekommt einen wiederverwendbaren Validator
(`PARTICIPANT_ID_PATTERN`/`is_valid_participant_id`/`validate_participant_id`/
`InvalidParticipantId`) aus demselben Vertrag wie `persona-state.schema.json`
Zeile 25. `_resolve_participant_id` validiert JETZT VOR jeder Marker-/
Verzeichnismutation; `main()` faengt `InvalidParticipantId` und gibt `2`
zurueck -- kein mkdir/Marker-Write, keine stille Ersatz-ID, der Bestand
bleibt erhalten.

Pure Python, nur `assert`, echter Exitcode, kein Netzwerk-/Modellaufruf."""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.core import identity  # noqa: E402

_ENTRY_PATH = _REPO_ROOT / "scripts" / "mmo_sim.py"


def _load_entry():
    spec = importlib.util.spec_from_file_location("mmo_sim_fixc_entrypoint", _ENTRY_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# identity.is_valid_participant_id / validate_participant_id / new_participant_id
# ---------------------------------------------------------------------------

_VALID_IDS = ["p026cc9611cd341ba", "la1_p1", "p" + "a" * 16]
_INVALID_NON_STRING = [None, 123, 1.5, ["la1_p1"], {"id": "la1_p1"}]
_INVALID_STRINGS = ["la1-l-tui-demo", "", "P123", "1abc"]


def test_is_valid_participant_id_accepts_schema_conform_ids():
    for pid in _VALID_IDS:
        assert identity.is_valid_participant_id(pid), pid


def test_is_valid_participant_id_rejects_invalid_strings():
    for pid in _INVALID_STRINGS:
        assert not identity.is_valid_participant_id(pid), pid


def test_is_valid_participant_id_rejects_non_strings():
    for pid in _INVALID_NON_STRING:
        assert not identity.is_valid_participant_id(pid), pid


def test_validate_participant_id_accepts_valid_without_raising():
    for pid in _VALID_IDS:
        identity.validate_participant_id(pid, source="test")


def test_validate_participant_id_raises_invalid_participant_id_with_readable_message():
    for pid in _INVALID_STRINGS:
        try:
            identity.validate_participant_id(pid, source="explizit --participant")
        except identity.InvalidParticipantId as exc:
            msg = str(exc)
            assert repr(pid) in msg, msg
            assert "explizit --participant" in msg, msg
            assert identity.PARTICIPANT_ID_PATTERN in msg, msg
        else:
            raise AssertionError(f"erwartete InvalidParticipantId fuer {pid!r}")


def test_validate_participant_id_raises_for_non_string():
    try:
        identity.validate_participant_id(123, source="gespeicherte last_participant.json")
    except identity.InvalidParticipantId:
        pass
    else:
        raise AssertionError("erwartete InvalidParticipantId fuer einen Nicht-String")


def test_new_participant_id_output_is_always_valid():
    for _ in range(20):
        assert identity.is_valid_participant_id(identity.new_participant_id())


# ---------------------------------------------------------------------------
# scripts/mmo_sim.py::_resolve_participant_id
# ---------------------------------------------------------------------------

def test_resolve_invalid_explicit_id_raises_and_writes_nothing():
    """(a) ungueltige explizite ID -> InvalidParticipantId, KEIN Marker
    geschrieben, data_dir bleibt unveraendert (kein mkdir-Seiteneffekt)."""
    entry = _load_entry()
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td) / "nested" / "data"
        try:
            entry._resolve_participant_id(data_dir, "la1-l-tui-demo")
        except identity.InvalidParticipantId:
            pass
        else:
            raise AssertionError("erwartete InvalidParticipantId fuer ungueltige --participant-ID")
        assert not data_dir.exists(), "data_dir haette NICHT angelegt werden duerfen (kein mkdir vor Validierung)"


def test_resolve_invalid_marker_raises_and_preserves_marker_bytes():
    """(b) ungueltiger vorbereiteter Marker, kein --participant ->
    InvalidParticipantId; der Marker bleibt BYTEGLEICH erhalten, keine neue
    ID wird still erzeugt."""
    entry = _load_entry()
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        data_dir.mkdir(parents=True, exist_ok=True)
        marker = data_dir / "last_participant.json"
        original_bytes = json.dumps({"participant_id": "la1-l-tui-demo"}).encode("utf-8")
        marker.write_bytes(original_bytes)

        try:
            entry._resolve_participant_id(data_dir, None)
        except identity.InvalidParticipantId:
            pass
        else:
            raise AssertionError("erwartete InvalidParticipantId fuer ungueltigen Marker")

        assert marker.read_bytes() == original_bytes, "Marker-Datei haette bytegleich erhalten bleiben muessen"


def test_resolve_valid_explicit_id_updates_marker_and_returns_it():
    """(c) gueltige explizite ID -> Marker aktualisiert, ID zurueckgegeben."""
    entry = _load_entry()
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        result = entry._resolve_participant_id(data_dir, "la1_p1")
        assert result == "la1_p1"
        marker = data_dir / "last_participant.json"
        assert json.loads(marker.read_text(encoding="utf-8"))["participant_id"] == "la1_p1"


def test_resolve_valid_existing_marker_returns_it_unchanged():
    """(d) gueltiger bestehender Marker -> dieselbe ID zurueckgegeben."""
    entry = _load_entry()
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        data_dir.mkdir(parents=True, exist_ok=True)
        marker = data_dir / "last_participant.json"
        marker.write_text(json.dumps({"participant_id": "la1_p1"}), encoding="utf-8")
        result = entry._resolve_participant_id(data_dir, None)
        assert result == "la1_p1"


def test_resolve_no_marker_generates_new_valid_id_and_persists_it():
    """(e) kein Marker -> `new_participant_id()` (immer gueltig) erzeugt +
    gespeichert."""
    entry = _load_entry()
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        result = entry._resolve_participant_id(data_dir, None)
        assert identity.is_valid_participant_id(result), result
        marker = data_dir / "last_participant.json"
        assert json.loads(marker.read_text(encoding="utf-8"))["participant_id"] == result


# ---------------------------------------------------------------------------
# main(): fruehe, verstaendliche Ablehnung VOR jedem Admission-/GM-Aufbau
# ---------------------------------------------------------------------------

def test_main_rejects_invalid_participant_cli_arg_with_exit_2_and_no_marker():
    entry = _load_entry()
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        rc = entry.main(["--data-dir", str(data_dir), "--participant", "la1-l-tui-demo"])
        assert rc == 2, f"main() haette bei ungueltiger --participant-ID mit 2 ablehnen sollen, exit={rc}"
        assert not (data_dir / "last_participant.json").exists(), (
            "Fix C-Regression: main() hat trotz ungueltiger --participant-ID einen Marker geschrieben"
        )
