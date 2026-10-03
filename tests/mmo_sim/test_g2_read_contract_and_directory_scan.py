#!/usr/bin/env python3
"""
tests/mmo_sim/test_g2_read_contract_and_directory_scan.py — G2
Lesevertragsnachzug (01_AUFTRAG_G2_LESEVERTRAG.md §A/§B/§C, REVIEW-G2.md
§3/§4, 2026-09-24): additive In-Repo-Regressionen fuer den gemeinsamen
Leseweg (`_classify_or_raise`, `load_request`, `open_requests`) in
`mmo_sim/core/request_ledger.py`, die dieser Runner (`run_all.py`)
TATSAECHLICH ausfuehrt -- die externen Gegenproben
(`regressions/review_g2_record_boundaries.py`,
`regressions/runtime_controls.py`) bleiben zusaetzlich bestehen, ersetzen
diese Lieferung aber nicht (02_ABNAHME.md).

Abgedeckt:
  (1) syntaktisch gueltiger JSON-Record, dem ein Pflichtschluessel
      (`participant`) fehlt -- muss wie ein Lese-/Parsefehler behandelt
      werden, NICHT wie ein Aufrufer mit bewusst gesetztem `None`.
  (2) ein blosses `{"state": "accounted"}`-Objekt -- kein Identitaets-/
      Buchungsnachweis, keine gueltige abgeschlossene Operation.
  (3) ein Verzeichnislesefehler am TATSAECHLICH von `open_requests()`
      verwendeten Primitive (`os.scandir`, oeffentliche stdlib-API --
      NICHT das private/versionsfragile `pathlib.Path._scandir`, s.
      `adapted-tests/`-Begruendung im Worker-Report) -- darf nicht wie ein
      leerer Erstlauf wirken.
  (4) ein initial fehlendes oder tatsaechlich leeres Requestverzeichnis
      bleibt der erlaubte Positivfall (`[]`).
  (5) ein NUR voruebergehender Scanfehler erzeugt kein Dauerverbot -- nach
      Wiederherstellung werden bereits vorhandene gueltige Datensaetze
      wieder normal gelesen UND neue, wirklich unabhaengige Operationen
      normal gebucht.
  (6) ein atomarer Kernfall (Schreibfehler zwischen den beiden
      `begin()`-Schreibschritten reserved->sent) hinterlaesst den zuletzt
      gueltigen Datensatz unveraendert -- ergaenzend zur bereits
      bestehenden vollen 18-Szenarien-Matrix in
      `test_i2_request_ledger_restart_and_write_failure.py` und der
      externen `review_g2_record_boundaries.py:test_06`.
  (+) Positivkontrolle: bereits von Aufrufern unterstuetzte, bewusst
      gesetzte `None`-Werte in optionalen Identitaetsfeldern bleiben
      gueltig (Auftrag §A: "fehlender KEY != bewusstes null").

Pure Python, nur `assert`, echter Exitcode. Keine Netz-/Modellaufrufe,
keine echten Subprozesse (im Gegensatz zur externen Reviewprobe genuegt
hier In-Prozess-Patching, da keine Prozessneustart-Semantik geprueft wird
-- die ist bereits in `test_i2_request_ledger_restart_and_write_failure.py`
abgedeckt)."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import traceback
from pathlib import Path
from unittest.mock import patch

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.core import request_ledger  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402

_KW = dict(role="gm_turn", content="SYNTHETIC in-repo G2 regression", reserved_usd=0.01)


def _init(run_dir: Path) -> None:
    write_test_profile(run_dir, max_turns=20, max_seconds=100, max_usd=1.0)


def _status(run_dir: Path) -> dict:
    return json.loads((run_dir / "lab.status.json").read_text(encoding="utf-8"))


def _record_files(run_dir: Path) -> dict:
    d = run_dir / "requests"
    if not d.is_dir():
        return {}
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(d.glob("*.json"))}


def test_g2_missing_operation_identity_key_blocks_second_reservation():
    """(1) Fall 02 (REVIEW-G2.md §3): ein sonst vollstaendiger Record verliert
    genau den `participant`-Schluessel (nicht nur seinen Wert). `begin()`
    fuer dieselbe logische Operation darf das NICHT als abwesend/fertig
    lesen und ein zweites Mal reservieren."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        _init(run_dir)
        rid = request_ledger.begin(
            run_dir, **_KW, table_id="table-1", section_id="section-1", turn_idx=1, participant="alice",
        )
        record_path = run_dir / "requests" / f"{rid}.json"
        data = json.loads(record_path.read_text(encoding="utf-8"))
        assert data.get("participant") == "alice"
        del data["participant"]
        record_path.write_text(json.dumps(data), encoding="utf-8")

        before_status = _status(run_dir)
        before_records = _record_files(run_dir)

        raised = None
        try:
            request_ledger.begin(
                run_dir, **_KW, table_id="table-1", section_id="section-1", turn_idx=1, participant="alice",
            )
        except request_ledger.IndeterminateRequestRecordError as exc:
            raised = exc
        assert raised is not None, (
            "Ein Record ohne 'participant'-Schluessel darf die bereits reservierte "
            "Operation nicht unsichtbar machen und eine zweite Reservierung zulassen."
        )
        assert _status(run_dir) == before_status, "Kein zweites Buchen bei unklarem Bestandsrecord."
        assert _record_files(run_dir) == before_records, "Keine neue Requestdatei bei unklarem Bestandsrecord."

        # Auch der reine Lesepfad (End-Critic-/Debug-Sicht) propagiert denselben Fehler.
        try:
            request_ledger.open_requests(run_dir)
            raised_via_open = False
        except request_ledger.IndeterminateRequestRecordError:
            raised_via_open = True
        assert raised_via_open, "open_requests() muss denselben unklaren Record propagieren, nicht ueberspringen."


def test_g2_bare_accounted_label_is_not_a_valid_terminal_record():
    """(2) Fall 03 (REVIEW-G2.md §3): `{"state": "accounted"}` traegt keinerlei
    Identitaets-/Buchungsnachweis -- kein gueltiger abgeschlossener Record,
    auch wenn `state` fuer sich genommen bekannt/gueltig ist."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        _init(run_dir)
        rid = request_ledger.begin(
            run_dir, **_KW, table_id="table-2", section_id="section-2", turn_idx=1, participant="bob",
        )
        record_path = run_dir / "requests" / f"{rid}.json"
        record_path.write_text(json.dumps({"state": "accounted"}), encoding="utf-8")

        before_status = _status(run_dir)
        before_records = _record_files(run_dir)

        raised = None
        try:
            request_ledger.begin(
                run_dir, **_KW, table_id="table-2", section_id="section-2", turn_idx=1, participant="bob",
            )
        except request_ledger.IndeterminateRequestRecordError as exc:
            raised = exc
        assert raised is not None, (
            "Ein blosses 'state=accounted'-Etikett ohne weitere Recorddaten beweist keine "
            "abgeschlossene Operation und darf nicht als Freigabe fuer eine zweite Reservierung dienen."
        )
        assert _status(run_dir) == before_status
        assert _record_files(run_dir) == before_records


def test_g2_unreadable_requests_directory_blocks_instead_of_empty_scan():
    """(3) Fall 04 (REVIEW-G2.md §4): `open_requests()` ruft seit dem G2-Fix
    `os.scandir(d)` direkt auf (oeffentliche stdlib-API statt des
    error-schluckenden `Path.glob`). Ein injizierter `PermissionError`
    GENAU an diesem Primitive muss propagieren -- kein leerer Scan, keine
    zweite Reservierung."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        _init(run_dir)
        rid = request_ledger.begin(
            run_dir, **_KW, table_id="table-3", section_id="section-3", turn_idx=1, participant="carol",
        )
        target_dir = run_dir / "requests"
        before_status = _status(run_dir)
        before_records = _record_files(run_dir)

        original_scandir = os.scandir
        fired = {"n": 0}

        def _patched_scandir(path="."):
            if fired["n"] == 0 and Path(path) == target_dir:
                fired["n"] += 1
                raise PermissionError(13, "INJECT G2 in-repo regression: enumeration denied", str(path))
            return original_scandir(path)

        raised = None
        with patch("os.scandir", _patched_scandir):
            try:
                request_ledger.begin(
                    run_dir, **_KW, table_id="table-3", section_id="section-3", turn_idx=1, participant="carol",
                )
            except request_ledger.IndeterminateRequestRecordError as exc:
                raised = exc

        assert fired["n"] == 1, "Injektion muss das echte Enumerationsprimitive genau einmal treffen."
        assert raised is not None, (
            "Ein nicht vollstaendig lesbares bestehendes Requestverzeichnis darf nicht wie ein "
            "leerer Erstlauf wirken und eine zweite Reservierung zulassen."
        )
        assert _status(run_dir) == before_status, "Budget/Turns duerfen bei fehlgeschlagenem Scan unveraendert bleiben."
        assert _record_files(run_dir) == before_records, "Der urspruengliche Record bleibt unveraendert lesbar."
        assert rid in next(iter(before_records)), "Sanity: der Ausgangsrecord existiert unter seiner eigenen id."


def test_g2_initial_missing_or_empty_requests_directory_stays_allowed():
    """(4) Ein echt leeres/initial fehlendes Requestverzeichnis bleibt der
    erlaubte Positivfall -- Fix B darf KEIN Generalverbot fuer den
    Normalfall einfuehren."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        _init(run_dir)
        # Das requests/-Unterverzeichnis wurde noch nie angelegt.
        assert not (run_dir / "requests").exists()
        assert request_ledger.open_requests(run_dir) == []

        # Ein tatsaechlich existierendes, aber leeres Verzeichnis bleibt ebenfalls erlaubt.
        (run_dir / "requests").mkdir(parents=True, exist_ok=True)
        assert request_ledger.open_requests(run_dir) == []

        # Und der normale Folgeaufruf funktioniert danach unveraendert.
        rid = request_ledger.begin(
            run_dir, **_KW, table_id="table-4", section_id="section-4", turn_idx=1, participant="dave",
        )
        assert any(r["id"] == rid for r in request_ledger.open_requests(run_dir))


def test_g2_transient_scan_error_recovers_after_restoration():
    """(5) Ein NUR voruebergehender Scanfehler ist kein Dauerverbot: nach
    Wiederherstellung liest `open_requests()` den bereits vorhandenen
    offenen Record wieder normal UND eine wirklich unabhaengige neue
    Operation (andere `turn_idx`) wird normal gebucht."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        _init(run_dir)
        rid = request_ledger.begin(
            run_dir, **_KW, table_id="table-5", section_id="section-5", turn_idx=1, participant="erin",
        )
        target_dir = run_dir / "requests"
        original_scandir = os.scandir
        fired = {"n": 0}

        def _patched_scandir(path="."):
            if fired["n"] == 0 and Path(path) == target_dir:
                fired["n"] += 1
                raise PermissionError(13, "INJECT G2 in-repo regression: transient enumeration denial", str(path))
            return original_scandir(path)

        with patch("os.scandir", _patched_scandir):
            try:
                request_ledger.open_requests(run_dir)
                assert False, "Injektion haette hier feuern muessen."
            except request_ledger.IndeterminateRequestRecordError:
                pass
        assert fired["n"] == 1

        # Nach dem `with`-Block ist os.scandir wiederhergestellt -- derselbe
        # bereits vorhandene offene Record muss wieder normal lesbar sein.
        reopened = request_ledger.open_requests(run_dir)
        assert any(r["id"] == rid for r in reopened), "Kein Dauerverbot nach behobenem transientem Fehler."

        # Eine wirklich unabhaengige neue Operation (anderer turn_idx) bucht normal.
        rid2 = request_ledger.begin(
            run_dir, **_KW, table_id="table-5", section_id="section-5", turn_idx=2, participant="erin",
        )
        assert rid2 != rid
        ids_after = {r["id"] for r in request_ledger.open_requests(run_dir)}
        assert {rid, rid2} <= ids_after
        assert _status(run_dir)["turns_used"] == 2


def test_g2_write_failure_between_reserved_and_sent_preserves_last_valid_record():
    """(6) Atomarer Kernfall: ein Schreibfehler GENAU beim zweiten
    `begin()`-Schreibschritt (reserved -> sent) darf den zuletzt
    vollstaendig veroeffentlichten (`reserved`) Record nicht beschaedigen
    -- ergaenzend zur vollen 18-Szenarien-Matrix in
    `test_i2_request_ledger_restart_and_write_failure.py`/
    `review_g2_record_boundaries.py:test_06`."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        _init(run_dir)
        real_replace = os.replace
        fired = {"n": 0}

        def _faulty_replace(src, dst):
            src_path = Path(src)
            try:
                data = json.loads(src_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return real_replace(src, dst)
            if fired["n"] == 0 and data.get("state") == "sent":
                fired["n"] += 1
                raise OSError("INJECT G2 in-repo regression: reserved->sent replace failure")
            return real_replace(src, dst)

        caught = None
        with patch("os.replace", _faulty_replace):
            try:
                request_ledger.begin(
                    run_dir, **_KW, table_id="table-6", section_id="section-6", turn_idx=1, participant="finn",
                )
            except OSError as exc:
                caught = exc
        assert fired["n"] == 1, "Injektion muss den zweiten Schreibschritt (state=sent) treffen."
        assert caught is not None, "Der Schreibfehler muss ungefangen propagieren."

        records = _record_files(run_dir)
        assert len(records) == 1
        (only_data,) = records.values()
        parsed = json.loads(only_data)
        assert parsed["state"] == "reserved", (
            "Der zuletzt vollstaendig veroeffentlichte Record (reserved) muss unveraendert "
            "lesbar bleiben, wenn der naechste Schreibschritt (sent) scheitert."
        )
        # Der Record ist ausreichend eingeordnet lesbar (Fix A haelt weiterhin).
        assert request_ledger.load_request(run_dir, parsed["id"])["state"] == "reserved"


def test_g2_explicit_null_optional_identity_fields_remain_valid():
    """(+) Positivkontrolle zu Fix A: bereits heute legitime, bewusst
    gesetzte `None`-Werte in optionalen Identitaetsfeldern (`table_id`,
    `section_id`, `turn_idx`, `participant`, `route`) sind KEIN fehlender
    Pflichtschluessel und muessen weiterhin normal lesbar/abschliessbar
    sein (Auftrag §A: 'fehlender KEY != bewusstes null')."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        _init(run_dir)
        rid = request_ledger.begin(
            run_dir, role="persona_decision", content="human driver, no table context", reserved_usd=0.01,
        )
        data = json.loads((run_dir / "requests" / f"{rid}.json").read_text(encoding="utf-8"))
        for optional_key in ("route", "table_id", "section_id", "turn_idx", "participant"):
            assert optional_key in data and data[optional_key] is None, (
                f"Vorbedingung: {optional_key} muss als Schluessel PRAESENT sein mit Wert None."
            )

        # load_request()/open_requests() klassifizieren den Record trotz der
        # None-Werte normal (kein IndeterminateRequestRecordError).
        loaded = request_ledger.load_request(run_dir, rid)
        assert loaded is not None and loaded["state"] == "sent"
        assert any(r["id"] == rid for r in request_ledger.open_requests(run_dir))

        request_ledger.finish_received(run_dir, rid, usage={"usd": 0.01}, seconds=1)
        assert request_ledger.load_request(run_dir, rid)["state"] == "accounted"


def main() -> int:
    tests = [v for k, v in list(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for t in sorted(tests, key=lambda f: f.__name__):
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
