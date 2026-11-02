#!/usr/bin/env python3
"""
tests/mmo_sim/test_table_admission_2026_11_02.py — ZR-FIGURENREISE-TISCH-
20261102-R1, Teilpaket A: `mmo_sim/core/table_admission.py`, der host-
autoritative Pre-Start-Tisch-Dienst (design.md §1, §5 Tests).

Abdeckung (Briefing stage3-table-admission.md):
  - host-only Transitionen (`accept_request`/`reject_request`/
    `remove_member`/`start_table`) werfen `HostAuthorityError` für
    Nicht-Host -- geprüft gegen den persistierten Record, nicht gegen den
    Parameter allein.
  - roster/requests dedup (mehrfache `request_join`, mehrfache `offer_table`
    für denselben Host sind idempotent).
  - leave/remove-Semantik: der Host ist NICHT entfernbar, weder über
    `remove_member` noch über `leave_table`.
  - Restart-Fit: ein frischer `load_record`-Aufruf (neuer "Prozess") sieht
    exakt den zuletzt persistierten Stand, kein 0-Reset.
  - atomarer Write: `table_admission/<table_key>.json` existiert nach jeder
    Mutation vollständig lesbar (kein halbgeschriebenes Dokument).

Pure Python, nur `assert`, echter Exitcode -- gleiches Muster wie die
bestehende Suite (kein pytest-Fixture-Zwang, s. `test_w48_save_correction_
2026_10_07.py`)."""
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

import mmo_sim.core.table_admission as table_admission  # noqa: E402


def test_offer_table_idempotent_same_host():
    with tempfile.TemporaryDirectory() as d:
        r1 = table_admission.offer_table(d, host_id="host1", table_key="t1")
        assert r1["state"] == "open" and r1["roster"] == ["host1"] and r1["requests"] == []
        r2 = table_admission.offer_table(d, host_id="host1", table_key="t1")
        assert r2 == r1, "zweiter offer_table-Aufruf desselben Hosts muss unveraendert (idempotent) sein."


def test_offer_table_foreign_host_raises_host_authority_error():
    with tempfile.TemporaryDirectory() as d:
        table_admission.offer_table(d, host_id="host1", table_key="t1")
        try:
            table_admission.offer_table(d, host_id="intruder", table_key="t1")
            raise AssertionError("offer_table mit fremdem host_id auf bestehenden Tisch muss werfen.")
        except table_admission.HostAuthorityError:
            pass


def test_request_join_dedup_and_noop_when_already_roster():
    with tempfile.TemporaryDirectory() as d:
        table_admission.offer_table(d, host_id="host1", table_key="t1")
        table_admission.request_join(d, table_key="t1", guest_id="g1")
        table_admission.request_join(d, table_key="t1", guest_id="g1")
        record = table_admission.load_record(d, "t1")
        assert record["requests"] == ["g1"], "mehrfache request_join fuer denselben Gast darf nicht duplizieren."

        table_admission.accept_request(d, table_key="t1", host_id="host1", guest_id="g1")
        record = table_admission.load_record(d, "t1")
        assert record["roster"] == ["host1", "g1"] and record["requests"] == []

        # no-op: bereits Mitglied, keine neue Anfrage
        record_after = table_admission.request_join(d, table_key="t1", guest_id="g1")
        assert record_after["requests"] == [] and record_after["roster"] == ["host1", "g1"]


def test_accept_request_requires_real_host_not_parameter_belief():
    """Host-Pruefung MUSS gegen den persistierten Record laufen -- ein
    Aufrufer, der behauptet host_id='g1' zu sein (obwohl der Record
    weiterhin 'host1' als Host traegt), darf NICHT durchkommen."""
    with tempfile.TemporaryDirectory() as d:
        table_admission.offer_table(d, host_id="host1", table_key="t1")
        table_admission.request_join(d, table_key="t1", guest_id="g1")
        try:
            table_admission.accept_request(d, table_key="t1", host_id="g1", guest_id="g1")
            raise AssertionError("accept_request von Nicht-Host muss HostAuthorityError werfen.")
        except table_admission.HostAuthorityError:
            pass
        # Record bleibt dabei unveraendert -- kein versehentlicher Teilschreib.
        record = table_admission.load_record(d, "t1")
        assert record["requests"] == ["g1"] and record["roster"] == ["host1"]


def test_reject_request_host_only():
    with tempfile.TemporaryDirectory() as d:
        table_admission.offer_table(d, host_id="host1", table_key="t1")
        table_admission.request_join(d, table_key="t1", guest_id="g1")
        try:
            table_admission.reject_request(d, table_key="t1", host_id="g1", guest_id="g1")
            raise AssertionError("reject_request von Nicht-Host muss HostAuthorityError werfen.")
        except table_admission.HostAuthorityError:
            pass
        table_admission.reject_request(d, table_key="t1", host_id="host1", guest_id="g1")
        record = table_admission.load_record(d, "t1")
        assert record["requests"] == [] and record["roster"] == ["host1"]
        # idempotent no-op fuer eine bereits abgelehnte/nicht vorhandene Anfrage
        record2 = table_admission.reject_request(d, table_key="t1", host_id="host1", guest_id="g1")
        assert record2["requests"] == []


def test_remove_member_host_only_and_host_not_removable():
    with tempfile.TemporaryDirectory() as d:
        table_admission.offer_table(d, host_id="host1", table_key="t1")
        table_admission.request_join(d, table_key="t1", guest_id="g1")
        table_admission.accept_request(d, table_key="t1", host_id="host1", guest_id="g1")

        try:
            table_admission.remove_member(d, table_key="t1", host_id="g1", guest_id="g1")
            raise AssertionError("remove_member von Nicht-Host muss HostAuthorityError werfen.")
        except table_admission.HostAuthorityError:
            pass

        try:
            table_admission.remove_member(d, table_key="t1", host_id="host1", guest_id="host1")
            raise AssertionError("remove_member darf den Host selbst NICHT entfernen koennen.")
        except table_admission.TableAdmissionError:
            pass

        table_admission.remove_member(d, table_key="t1", host_id="host1", guest_id="g1")
        record = table_admission.load_record(d, "t1")
        assert record["roster"] == ["host1"]
        # no-op: bereits entfernt
        record2 = table_admission.remove_member(d, table_key="t1", host_id="host1", guest_id="g1")
        assert record2["roster"] == ["host1"]


def test_leave_table_self_removal_and_host_cannot_leave():
    with tempfile.TemporaryDirectory() as d:
        table_admission.offer_table(d, host_id="host1", table_key="t1")
        table_admission.request_join(d, table_key="t1", guest_id="g1")
        table_admission.accept_request(d, table_key="t1", host_id="host1", guest_id="g1")

        table_admission.leave_table(d, table_key="t1", guest_id="g1")
        record = table_admission.load_record(d, "t1")
        assert record["roster"] == ["host1"]

        try:
            table_admission.leave_table(d, table_key="t1", guest_id="host1")
            raise AssertionError("Host darf sich NICHT ueber leave_table entfernen koennen.")
        except table_admission.TableAdmissionError:
            pass
        record_after = table_admission.load_record(d, "t1")
        assert record_after["roster"] == ["host1"], "Host muss nach fehlgeschlagenem leave_table weiter im roster sein."


def test_withdraw_request_removes_own_pending_request():
    with tempfile.TemporaryDirectory() as d:
        table_admission.offer_table(d, host_id="host1", table_key="t1")
        table_admission.request_join(d, table_key="t1", guest_id="g1")
        table_admission.withdraw_request(d, table_key="t1", guest_id="g1")
        record = table_admission.load_record(d, "t1")
        assert record["requests"] == []
        # no-op, wenn keine Anfrage (mehr) vorliegt
        record2 = table_admission.withdraw_request(d, table_key="t1", guest_id="g1")
        assert record2["requests"] == []


def test_start_table_host_only_freezes_roster_idempotent():
    with tempfile.TemporaryDirectory() as d:
        table_admission.offer_table(d, host_id="host1", table_key="t1")
        table_admission.request_join(d, table_key="t1", guest_id="g1")
        table_admission.accept_request(d, table_key="t1", host_id="host1", guest_id="g1")

        try:
            table_admission.start_table(d, table_key="t1", host_id="g1")
            raise AssertionError("start_table von Nicht-Host muss HostAuthorityError werfen.")
        except table_admission.HostAuthorityError:
            pass

        started = table_admission.start_table(d, table_key="t1", host_id="host1")
        assert started["state"] == "started" and started["roster"] == ["host1", "g1"]

        # idempotent -- zweiter Start-Aufruf desselben Hosts unveraendert
        started2 = table_admission.start_table(d, table_key="t1", host_id="host1")
        assert started2 == started

        # roster/requests sind eingefroren: aktiv oeffnende Mutationen nach
        # start lehnen ab (`_require_open`).
        for fn, kwargs in (
            (table_admission.request_join, dict(table_key="t1", guest_id="g2")),
            (table_admission.accept_request, dict(table_key="t1", host_id="host1", guest_id="g2")),
        ):
            try:
                fn(d, **kwargs)
                raise AssertionError(f"{fn.__name__} darf nach start_table nicht mehr zulaessig sein.")
            except table_admission.TableAdmissionError:
                pass

        # reject_request ist idempotent no-op-sicher: `requests` ist nach
        # dem Freeze bereits leer, ein Nicht-Mitglied bleibt weiterhin
        # abwesend, ohne dass der Record veraendert wird.
        after = table_admission.reject_request(d, table_key="t1", host_id="host1", guest_id="g2")
        assert after["requests"] == [] and after["roster"] == ["host1", "g1"]


def test_roster_read_only_view_and_unknown_table_key_raises():
    with tempfile.TemporaryDirectory() as d:
        table_admission.offer_table(d, host_id="host1", table_key="t1")
        table_admission.request_join(d, table_key="t1", guest_id="g1")
        view = table_admission.roster(d, "t1")
        assert view["roster"] == ["host1"] and view["requests"] == ["g1"]
        try:
            table_admission.roster(d, "unknown-table")
            raise AssertionError("roster() fuer unbekannten table_key muss TableAdmissionError werfen.")
        except table_admission.TableAdmissionError:
            pass


def test_restart_fit_fresh_load_sees_persisted_state_no_reset():
    """Simuliert einen Neustart: ein frischer `load_record`-Aufruf (kein
    gehaltenes Python-Objekt aus vorherigen Aufrufen) muss exakt den
    zuletzt geschriebenen Stand sehen -- kein 0-Reset von roster/requests/
    attempts-aehnlichen Zaehlern."""
    with tempfile.TemporaryDirectory() as d:
        table_admission.offer_table(d, host_id="host1", table_key="t1")
        table_admission.request_join(d, table_key="t1", guest_id="g1")
        table_admission.request_join(d, table_key="t1", guest_id="g2")
        table_admission.accept_request(d, table_key="t1", host_id="host1", guest_id="g1")

        # "Neustart": komplett frischer Load, unabhaengig von return-Werten oben.
        fresh = table_admission.load_record(d, "t1")
        assert fresh["host_id"] == "host1"
        assert fresh["roster"] == ["host1", "g1"]
        assert fresh["requests"] == ["g2"]
        assert fresh["state"] == "open"
        assert len(fresh["log"]) == 4, "append-only Audit-Log muss alle vier Mutationen enthalten."

        # ein zweiter offer_table-"Resume"-Aufruf darf den bereits bestehenden
        # Record NICHT ueberschreiben/zuruecksetzen.
        resumed = table_admission.offer_table(d, host_id="host1", table_key="t1")
        assert resumed == fresh


def test_atomic_write_leaves_valid_json_and_no_tmp_leftover():
    """Jede Mutation schreibt ueber `admission._atomic_write_json`
    (Temp-Datei + `os.replace`) -- nach einer Mutation existiert GENAU die
    Zieldatei mit vollstaendig parsbarem JSON, keine `.tmp-*`-Artefakte."""
    with tempfile.TemporaryDirectory() as d:
        table_admission.offer_table(d, host_id="host1", table_key="t1")
        table_admission.request_join(d, table_key="t1", guest_id="g1")
        table_admission.accept_request(d, table_key="t1", host_id="host1", guest_id="g1")

        records_dir = Path(d) / "table_admission"
        entries = sorted(p.name for p in records_dir.iterdir())
        assert entries == ["t1.json"], f"keine Temp-/Restartefakte erwartet, gefunden: {entries}"

        on_disk = json.loads((records_dir / "t1.json").read_text(encoding="utf-8"))
        assert on_disk["roster"] == ["host1", "g1"]
        assert on_disk == table_admission.load_record(d, "t1")


def test_table_key_with_slash_is_sanitized_to_safe_filename():
    with tempfile.TemporaryDirectory() as d:
        table_admission.offer_table(d, host_id="host1", table_key="lobby/t1")
        records_dir = Path(d) / "table_admission"
        entries = sorted(p.name for p in records_dir.iterdir())
        assert entries == ["lobby_t1.json"], entries
        record = table_admission.load_record(d, "lobby/t1")
        assert record["table_key"] == "lobby/t1"


def _run_all() -> int:
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in fns:
        try:
            fn()
            print(f"OK   {fn.__name__}")
            passed += 1
        except AssertionError:
            print(f"FAIL {fn.__name__}")
            traceback.print_exc()
        except Exception:
            print(f"ERROR {fn.__name__}")
            traceback.print_exc()
    print(f"\n{passed}/{len(fns)} passed")
    return 0 if passed == len(fns) else 1


if __name__ == "__main__":
    raise SystemExit(_run_all())
