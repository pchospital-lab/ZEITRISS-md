#!/usr/bin/env python3
"""
tests/mmo_sim/test_g2_control_field_value_contract.py -- G2-Kontrollfeld-
Wertvertragsnachzug (01_AUFTRAG_G2_KONTROLLFELDER.md, REVIEW-G2-
KONTROLLFELDER.md Section 3/4/5, 2026-09-24): additive In-Repo-
Regressionen fuer den REST-A-Nachzug des gemeinsamen Lesewegs
(`_classify_or_raise` via `load_request()`/`open_requests()`) in
`mmo_sim/core/request_ledger.py`, die dieser Runner (`run_all.py`)
TATSAECHLICH ausfuehrt. Ergaenzt (nicht ersetzt)
`test_g2_read_contract_and_directory_scan.py` (fehlender Schluessel/blosses
state=accounted/Scanfehler) UND die externe Gegenprobe
`regressions/review_g2_control_fields.py` (drei falsch typisierte
Identitaetsfelder + doppeltes state). Malformte Records unten sind
ABSICHTLICHE synthetische Testeingaben, NICHT behauptetes Verhalten des
atomaren Writers (`_atomic_write_json`/`_write_request`).

Abgedeckt, zusaetzlich zu den bereits vorhandenen Faellen:
  (1) PRAESENTE, aber falsch typisierte Werte JENSEITS der drei bereits
      extern geprueften Felder -- insbesondere `bool` an Zahlenfeldern
      (`bool` ist in Python ein Subtyp von `int`: `isinstance(True, int)`
      ist `True`, ein naiver Typcheck wuerde das durchlassen) UND ein
      falscher Typ an einem rein optionalen String-Feld (`table_id`).
  (2) ein widerspruechliches doppeltes Kontrollfeld JENSEITS von `state`
      (`participant`) -- die Ablehnung muss generisch beim Dekodieren
      greifen, nicht nur fuer das eine bereits extern geprüfte Feld.
  (3) Positivkontrolle ueber die VOLLE optionale Nullmatrix (nicht nur
      Identitaetsfelder): ein `reserved`-Zwischenzustand (vor `sent`) UND
      ein echter Human-Driver-Aufruf ohne Tisch-/Turn-/Routenkontext (`ui/
      tui.py`s Gast-Pfad ruft `begin()` ohne `table_id`/`section_id`/
      `turn_idx`, s. `ui/tui.py:806`) bleiben normal lesbar/buchbar.
  (4) eine vollstaendige gueltige Erst-/Folge-/Finish-Sequenz bleibt nach
      dem REST-A-Fix unveraendert nutzbar (kein legitimer begin()/
      finish_received()-Output wird abgewiesen).

Pure Python, nur `assert`, echter Exitcode. Keine Netz-/Modellaufrufe,
keine echten Subprozesse (In-Prozess-Patching genuegt, da keine
Prozessneustart-Semantik geprueft wird)."""
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

from mmo_sim.core import request_ledger  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402

_KW = dict(role="gm_turn", content="SYNTHETIC in-repo G2 value-contract regression", reserved_usd=0.01)


def _init(run_dir: Path) -> None:
    write_test_profile(run_dir, max_turns=20, max_seconds=100, max_usd=1.0)


def _status(run_dir: Path) -> dict:
    return json.loads((run_dir / "lab.status.json").read_text(encoding="utf-8"))


def _record_files(run_dir: Path) -> dict:
    d = run_dir / "requests"
    if not d.is_dir():
        return {}
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(d.glob("*.json"))}


def _assert_blocked_without_mutation(run_dir: Path, before_status: dict, before_records: dict, **begin_kwargs) -> None:
    """Gemeinsame Abnahmegrenze (02_ABNAHME.md): kontrollierter Fehler in
    BEIDEN Lesewegen, keine zweite ID/Reserve, Bestand unveraendert."""
    load_error = None
    try:
        request_ledger.load_request(run_dir, before_records and next(iter(before_records)).removesuffix(".json"))
    except request_ledger.IndeterminateRequestRecordError as exc:
        load_error = exc
    begin_error = None
    try:
        request_ledger.begin(run_dir, **_KW, **begin_kwargs)
    except request_ledger.IndeterminateRequestRecordError as exc:
        begin_error = exc
    assert load_error is not None, "load_request() muss den unklaren Bestandsrecord ablehnen, nicht als gueltig lesen."
    assert begin_error is not None, "begin() muss VOR jeder neuen Reservierung denselben unklaren Bestand ablehnen."
    assert _status(run_dir) == before_status, "Kein zweites Buchen bei unklarem Bestandsrecord."
    assert _record_files(run_dir) == before_records, "Der urspruengliche fehlerhafte Record bleibt unveraendert (kein Auffuellen/Loeschen/Neu-UUID)."


def test_g2_boolean_values_at_numeric_identity_fields_are_rejected():
    """(1a) `bool` ist ein Subtyp von `int` -- `turn_idx=True`/
    `reserved_usd=True` duerfen NICHT als gueltiger Zaehler/Betrag
    durchgehen, obwohl ein naiver `isinstance(v, int)`-Check das erlauben
    wuerde. Deckt beide betroffenen Feldklassen ab (strikt-int ohne bool:
    `turn_idx`; Zahl-ohne-bool: `reserved_usd`)."""
    for field, bad_value in (("turn_idx", True), ("reserved_usd", False)):
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "run"
            _init(run_dir)
            rid = request_ledger.begin(
                run_dir, **_KW, table_id="table-bool", section_id="section-bool", turn_idx=1, participant="alice",
            )
            record_path = run_dir / "requests" / f"{rid}.json"
            data = json.loads(record_path.read_text(encoding="utf-8"))
            assert isinstance(data[field], (int, float)) and not isinstance(data[field], bool), (
                f"Vorbedingung: begin() schreibt {field!r} als echte Zahl, nicht als bool."
            )
            data[field] = bad_value
            record_path.write_text(json.dumps(data), encoding="utf-8")

            before_status = _status(run_dir)
            before_records = _record_files(run_dir)
            _assert_blocked_without_mutation(
                run_dir, before_status, before_records,
                table_id="table-bool", section_id="section-bool", turn_idx=1, participant="alice",
            )


def test_g2_wrong_type_optional_string_field_is_rejected():
    """(1b) `table_id` ist ein optionales STRING-Feld -- ein praesenter,
    aber nicht-string, nicht-None Wert (hier: Liste) ist unzulaessig, auch
    wenn `table_id` grundsaetzlich `None` sein darf."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        _init(run_dir)
        rid = request_ledger.begin(
            run_dir, **_KW, table_id="table-str", section_id="section-str", turn_idx=1, participant="bob",
        )
        record_path = run_dir / "requests" / f"{rid}.json"
        data = json.loads(record_path.read_text(encoding="utf-8"))
        data["table_id"] = ["table-str"]
        record_path.write_text(json.dumps(data), encoding="utf-8")

        before_status = _status(run_dir)
        before_records = _record_files(run_dir)
        _assert_blocked_without_mutation(
            run_dir, before_status, before_records,
            table_id="table-str", section_id="section-str", turn_idx=1, participant="bob",
        )


def test_g2_conflicting_duplicate_participant_key_blocks_without_mutation():
    """(2) Die Doppelkeypruefung ist nicht auf `state` beschraenkt: ein
    zweites, widersprechendes `participant` im selben JSON-Objekt muss
    ebenso beim Dekodieren als nicht eindeutig einordenbar abgelehnt
    werden -- sonst wuerde `_operation_identity()` den STILLEN LETZTEN Wert
    (Standard-`json.loads`-Semantik) fuer die Doppelreservierungspruefung
    verwenden."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        _init(run_dir)
        rid = request_ledger.begin(
            run_dir, **_KW, table_id="table-dup", section_id="section-dup", turn_idx=1, participant="carol",
        )
        record_path = run_dir / "requests" / f"{rid}.json"
        raw = record_path.read_text(encoding="utf-8")
        assert json.loads(raw)["participant"] == "carol"
        malformed = raw.rstrip()[:-1] + ', "participant": "mallory"}'
        record_path.write_text(malformed, encoding="utf-8")

        before_status = _status(run_dir)
        before_records = _record_files(run_dir)
        _assert_blocked_without_mutation(
            run_dir, before_status, before_records,
            table_id="table-dup", section_id="section-dup", turn_idx=1, participant="carol",
        )
        # Auch fuer den ANDEREN (widersprechenden) Teilnehmerwert darf keine
        # neue Reservierung entstehen -- der Record ist insgesamt nicht
        # eindeutig einordenbar, nicht nur fuer eine der beiden Identitaeten.
        begin_error_other = None
        try:
            request_ledger.begin(
                run_dir, **_KW, table_id="table-dup", section_id="section-dup", turn_idx=1, participant="mallory",
            )
        except request_ledger.IndeterminateRequestRecordError as exc:
            begin_error_other = exc
        assert begin_error_other is not None
        assert _status(run_dir) == before_status
        assert _record_files(run_dir) == before_records


def test_g2_full_optional_null_matrix_remains_valid_including_human_driver_caller():
    """(3) Positivkontrolle ueber die VOLLE optionale Nullmatrix, nicht nur
    Identitaetsfelder: ein `reserved`-Zwischenzustand (sent_ts/settled_ts/
    usage/error alle noch `None`) UND ein echter Human-Driver-Aufruf ohne
    Tisch-/Turn-/Routenkontext (entspricht `ui/tui.py`s Gast-Pfad, der
    `begin()` OHNE `table_id`/`section_id`/`turn_idx` ruft, s. `ui/
    tui.py:806`) bleiben nach dem REST-A-Fix normal lesbar/buchbar -- der
    Wertvertrag darf KEINEN legitimen begin()/finish_received()-Output
    abweisen."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        _init(run_dir)

        # Human-driver-artiger Aufruf: nur role/content/reserved_usd=None,
        # route=None -- kein table_id/section_id/turn_idx (wie ein
        # unqualifizierter Aufrufer ohne Tisch-/Turnkontext).
        rid = request_ledger.begin(run_dir, role="persona_decision", content="human driver turn", reserved_usd=None)
        data = json.loads((run_dir / "requests" / f"{rid}.json").read_text(encoding="utf-8"))
        for optional_key in ("route", "reserved_usd", "output_limit_tokens", "table_id", "section_id", "turn_idx", "participant"):
            assert optional_key in data and data[optional_key] is None
        # Zwischenzustand `reserved` existiert real nur SEHR kurz (begin()
        # schreibt sofort danach `sent`) -- hier direkt simuliert, um den
        # vollen Nullstand (sent_ts/settled_ts/usage/error alle None) am
        # gemeinsamen Leseweg zu pruefen, ohne begin()s internen Ablauf
        # umzubauen.
        reserved_record_path = run_dir / "requests" / "SYNTHETIC-reserved-null-matrix.json"
        reserved_data = dict(data)
        reserved_data["id"] = "SYNTHETIC-reserved-null-matrix"
        reserved_data["state"] = "reserved"
        # `data` stammt vom bereits `sent` Record (begin() schreibt sent_ts
        # beim zweiten Schritt) -- fuer die synthetische reserved-Momentaufnahme
        # explizit auf den echten reserved-Nullstand zuruecksetzen.
        reserved_data["sent_ts"] = None
        assert reserved_data["sent_ts"] is None and reserved_data["settled_ts"] is None
        assert reserved_data["usage"] is None and reserved_data["error"] is None
        reserved_record_path.write_text(json.dumps(reserved_data), encoding="utf-8")
        loaded_reserved = request_ledger.load_request(run_dir, "SYNTHETIC-reserved-null-matrix")
        assert loaded_reserved is not None and loaded_reserved["state"] == "reserved"
        assert any(r["id"] == "SYNTHETIC-reserved-null-matrix" for r in request_ledger.open_requests(run_dir))

        # Der echte begin()-Output selbst bleibt normal lesbar und
        # abschliessbar (kein Refund-/Fehlpfad durch den neuen Wertvertrag).
        loaded = request_ledger.load_request(run_dir, rid)
        assert loaded is not None and loaded["state"] == "sent"
        request_ledger.finish_received(run_dir, rid, usage=None, seconds=0.5)
        final = request_ledger.load_request(run_dir, rid)
        assert final["state"] == "accounted" and final["usd_reconciled"] is True


def test_g2_valid_first_followup_and_finish_sequence_remains_usable():
    """(4) Vollstaendige gueltige Erst-/Folge-/Finish-Sequenz bleibt nach
    dem REST-A-Fix unveraendert nutzbar: Erstturn reserviert+sendet+
    schliesst ab, ein wirklich unabhaengiger Folgeturn (anderer `turn_idx`)
    bucht normal, und der finale Kontostand stimmt -- der Wertvertrag greift
    ausschliesslich bei absichtlich manipulierten Bestandsdateien, nicht bei
    echtem Produktverhalten."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        _init(run_dir)

        rid1 = request_ledger.begin(
            run_dir, **_KW, table_id="table-seq", section_id="section-seq", turn_idx=1, participant="dave",
        )
        first = request_ledger.load_request(run_dir, rid1)
        assert first["state"] == "sent" and first["turn_idx"] == 1 and type(first["turn_idx"]) is int
        request_ledger.finish_received(run_dir, rid1, usage={"usd": 0.01}, seconds=1.5)
        assert request_ledger.load_request(run_dir, rid1)["state"] == "accounted"

        rid2 = request_ledger.begin(
            run_dir, **_KW, table_id="table-seq", section_id="section-seq", turn_idx=2, participant="dave",
        )
        assert rid2 != rid1
        second = request_ledger.load_request(run_dir, rid2)
        assert second["state"] == "sent" and second["turn_idx"] == 2
        request_ledger.finish_error(run_dir, rid2, error=RuntimeError("SYNTHETIC transport failure"), seconds=0.3)
        final_second = request_ledger.load_request(run_dir, rid2)
        assert final_second["state"] == "accounted" and final_second["error"] == "SYNTHETIC transport failure"

        status = _status(run_dir)
        assert status["turns_used"] == 2
        assert abs(status["usd_spent"] - 0.02) < 1e-9

        open_now = request_ledger.open_requests(run_dir)
        assert open_now == [], "Beide abgeschlossenen (accounted) Requests duerfen nicht mehr als offen gelten."


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
