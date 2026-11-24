#!/usr/bin/env python3
"""
tests/mmo_sim/test_rec2_orphan_recovery_menu_20261123_r1.py — PR #3317-
Nachzug 2026-11-23, RECOVERY_REVIEW.md R2 ("Es gibt keinen normalen
Recoveryweg fuer echte Roots"). Additiv, pure Python (nur `assert`, echter
Exitcode) -- deckt die neue Anwendungsschicht `core.recovery_ops.
plan_orphan_recovery`/`apply_orphan_recovery`, die gehaertete
`request_ledger.commit_authorized_retry`-Bindungspruefung UND den
ersetzten TUI-Dead-End (`ui.tui.TuiSession._offer_orphan_recovery_menu`)
ab.

Faehrt ECHTE Produktprimitiven (`request_ledger.begin`/`finish_received`,
`recovery_ops.plan_orphan_recovery`/`apply_orphan_recovery`) an -- keine
Mocks AUF diesem Pfad selbst. Fuer den TUI-Menuepfad wird NUR ein minimaler
Duck-Typing-Stand-in fuer `TuiSession` verwendet (`run_dir`/`_print`/
`_readline_with_controls`), da `TuiSession.__init__` eine volle Session
(Lobby/Store/Transport) voraussetzt, die dieser enge Test nicht braucht --
die aufgerufene Methode selbst (`_offer_orphan_recovery_menu`) ist die
ECHTE, unveraenderte Produktmethode, nur `self` ist ein Stand-in."""
from __future__ import annotations

import fcntl
import json
import os
import shutil
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.core import recovery_ops, request_ledger  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402


def _make_run(root: Path, *, run_id: str | None = "REAL-ROOT-RUN") -> Path:
    """Baut einen Run OHNE `RECOVERY_SYNTHETIC_TEST_ROOT`-Marker -- R2 ist
    ausdruecklich der echte-Root-faehige Weg (`apply_orphan_recovery` ruft
    NIE `_require_synthetic_root` auf); anders als `_recovery_ops_r1_
    fixtures.make_synthetic_run` (das den Marker per Default setzt) belegt
    dieser Helper das strukturell."""
    run_dir = root / "run"
    write_test_profile(run_dir)
    if run_id is not None:
        (run_dir / "run_id.json").write_text(json.dumps({"run_id": run_id}), encoding="utf-8")
    return run_dir


def _make_unknown_orphan(run_dir: Path, *, table_id="table-1", section_id="section-1",
                          role="gm_turn", turn_idx=1, participant="alice") -> str:
    """`request_ledger.begin()` und STOPPT dort -- state bleibt `sent`,
    `result_text`/`usage`/`settled_ts`/`error` bleiben `None`: exakt der
    echte unbekannte Ausgang, fuer den R2 gilt."""
    return request_ledger.begin(
        run_dir, role=role, content="SYNTHETIC unbeantworteter R2-Orphan-Request", reserved_usd=0.01,
        table_id=table_id, section_id=section_id, turn_idx=turn_idx, participant=participant,
    )


def _resolve_identity_via_consumed_follower(run_dir: Path, original_id: str, *, result_text: str | None) -> str:
    """Baut den Fall, den `find_durable_result`/`find_answered_without_text`
    tatsaechlich fuer R2 abdecken: das ORIGINAL bleibt offen (`sent`, nie
    `finish_*`), aber die GLEICHE Operationsidentitaet ist bereits ueber
    einen regulaer konsumierten Folger (`dispose_open_orphan`->`authorize_
    bound_retry`->`commit_authorized_retry`->`finish_received`) entweder
    durabel beantwortet (`result_text` gesetzt) oder verloren (`result_
    text=None`) -- GENAU das Szenario, in dem `plan_orphan_recovery` das
    Original NICHT mehr als `unknown` einstufen darf (R2 Punkt 2)."""
    request_ledger.dispose_open_orphan(run_dir, original_id, reason="fixture: identity resolved via follower")
    follower_id = request_ledger.authorize_bound_retry(run_dir, original_id)
    request_ledger.commit_authorized_retry(run_dir, follower_id, content="fixture follower content", reserved_usd=0.01)
    request_ledger.finish_received(run_dir, follower_id, usage={"usd": 0.01}, result_text=result_text)
    return follower_id


def _snapshot(run_dir: Path) -> dict:
    """Byte-Snapshot aller Dateien unter `run_dir` -- fuer den
    Abbruch/Zurueck-bytegleich-Nachweis (R2 Punkt 7)."""
    out = {}
    for p in sorted(run_dir.rglob("*")):
        if p.is_file():
            out[str(p.relative_to(run_dir))] = p.read_bytes()
    return out


class _FakeTuiSession:
    """Minimaler Duck-Typing-Stand-in fuer `TuiSession` -- NUR die drei
    Attribute/Methoden, die `_offer_orphan_recovery_menu` tatsaechlich
    benutzt. Wirft, wenn mehr Prompts gestellt werden als Antworten
    gecannt wurden (Beleg gegen eine unerwartete zusaetzliche Nachfrage,
    z.B. fuer einen bereits durablen Treffer)."""

    def __init__(self, run_dir: Path, answers: list[tuple[str, str | None]]):
        self.run_dir = run_dir
        self._answers = list(answers)
        self.printed: list[str] = []

    def _print(self, text: str) -> None:
        self.printed.append(text)

    def _readline_with_controls(self, prompt: str, *, context: str):
        if not self._answers:
            raise AssertionError(
                "FakeTuiSession: unerwarteter zusaetzlicher Prompt -- keine weiteren Antworten gecannt "
                f"(prompt={prompt!r})."
            )
        return self._answers.pop(0)


# ─────────────────────────── plan_orphan_recovery ───────────────────────────


def test_plan_orphan_recovery_is_read_only_and_cheap():
    """`plan_orphan_recovery` schreibt NICHTS -- vor/nach dem Aufruf ist
    der Run byte-identisch (R2 Punkt 1: kostenfrei)."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _make_run(Path(td))
        rid = _make_unknown_orphan(run_dir)
        before = _snapshot(run_dir)
        plan = recovery_ops.plan_orphan_recovery(run_dir)
        after = _snapshot(run_dir)
        assert after == before, "plan_orphan_recovery darf keine Datei veraendern (rein lesend/kostenfrei)."
        orphans = plan["orphans"]
        assert len(orphans) == 1 and orphans[0]["request_id"] == rid
        assert orphans[0]["classification"] == "unknown"
        assert orphans[0]["action"] == recovery_ops.ORPHAN_ACTION


def test_durable_result_is_preferred_over_retry_and_apply_rejects_it():
    """R2 Punkt 2 ('Originalresultate vorrangig aufloesen'): das Original
    bleibt offen (`sent`), aber dieselbe Operationsidentitaet ist bereits
    ueber einen regulaer konsumierten Folger durabel beantwortet -- das
    Original wird dadurch als `durable_result` klassifiziert, NICHT als
    `unknown`. `apply_orphan_recovery` lehnt einen Versuch darauf
    kontrolliert ab (kein Retry fuer ein bereits vorliegendes Ergebnis)."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _make_run(Path(td))
        rid = _make_unknown_orphan(run_dir)
        _resolve_identity_via_consumed_follower(run_dir, rid, result_text="echte Antwort")

        plan = recovery_ops.plan_orphan_recovery(run_dir)
        orphans = plan["orphans"]
        assert len(orphans) == 1, f"erwartet genau das offene Original, erhalten: {orphans!r}"
        assert orphans[0]["classification"] == "durable_result"
        assert orphans[0]["request_id"] == rid

        raised = None
        try:
            recovery_ops.apply_orphan_recovery(
                run_dir, request_id=rid, reason="sollte abgelehnt werden",
                plan={"action": recovery_ops.ORPHAN_ACTION, "request_id": rid},
            )
        except recovery_ops.RecoveryPreconditionChangedError as exc:
            raised = exc
        assert raised is not None, (
            "ein durabel beantworteter Orphan darf NICHT ueber apply_orphan_recovery neu versucht werden."
        )


def test_lost_without_text_is_not_a_retry_candidate():
    """Dasselbe Szenario, aber der konsumierte Folger hat `result_text=
    None` (`find_answered_without_text`-Treffer) -- bleibt ebenfalls KEIN
    `unknown`-Kandidat, kein Retry fuer eine bereits abgeschlossene
    Operation."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _make_run(Path(td))
        rid = _make_unknown_orphan(run_dir)
        _resolve_identity_via_consumed_follower(run_dir, rid, result_text=None)

        plan = recovery_ops.plan_orphan_recovery(run_dir)
        orphans = plan["orphans"]
        assert len(orphans) == 1, f"erwartet genau das offene Original, erhalten: {orphans!r}"
        assert orphans[0]["classification"] == "lost_without_text"


# ─────────────────────── apply_orphan_recovery Gegenfaelle ──────────────────


def test_apply_without_plan_is_rejected():
    """R2 Punkt 4/5 (CONTROL.json `core_plan_clarification`, analog
    `apply_p3`/`apply_p5`): `plan=None` appliziert NICHT stillschweigend
    neu geplant."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _make_run(Path(td))
        rid = _make_unknown_orphan(run_dir)
        raised = None
        try:
            recovery_ops.apply_orphan_recovery(run_dir, request_id=rid, reason="x", plan=None)
        except recovery_ops.RecoveryPlanRequiredError as exc:
            raised = exc
        assert raised is not None


def test_apply_rejects_changed_pre_state():
    """Gegenfall 'geaenderter Vorzustand': ein VOR der Zustandsaenderung
    gezogener Plan wird NACH einer Veraenderung des Originalrecords (hier:
    zwischenzeitliches `finish_received`) kontrolliert abgelehnt."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _make_run(Path(td))
        rid = _make_unknown_orphan(run_dir)
        plan = recovery_ops.plan_orphan_recovery(run_dir)
        stale_item = next(o for o in plan["orphans"] if o["request_id"] == rid)

        request_ledger.finish_received(run_dir, rid, usage={"usd": 0.01}, result_text="inzwischen doch beantwortet")

        raised = None
        try:
            recovery_ops.apply_orphan_recovery(run_dir, request_id=rid, reason="x", plan=stale_item)
        except recovery_ops.RecoveryPreconditionChangedError as exc:
            raised = exc
        assert raised is not None, "ein veralteter Plan (Vorzustand geaendert) haette abgelehnt werden muessen."


def test_apply_rejects_foreign_run_binding():
    """Gegenfall 'fremder Run': ein auf Run A gezogener Plan darf NICHT auf
    einem byte-identisch kopierten Run B (andere `run_id.json`) appliziert
    werden."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_a = _make_run(root / "a", run_id="RUN-A")
        rid = _make_unknown_orphan(run_a)
        plan = recovery_ops.plan_orphan_recovery(run_a)
        item = next(o for o in plan["orphans"] if o["request_id"] == rid)

        run_b = root / "b" / "run"
        shutil.copytree(run_a, run_b)
        (run_b / "run_id.json").write_text(json.dumps({"run_id": "RUN-B"}), encoding="utf-8")

        raised = None
        try:
            recovery_ops.apply_orphan_recovery(run_b, request_id=rid, reason="x", plan=item)
        except recovery_ops.RecoveryPreconditionChangedError as exc:
            raised = exc
        assert raised is not None, "ein Plan von Run A durfte NICHT auf Run B appliziert werden (Bindungsfehler)."


def test_apply_rejects_when_writer_busy():
    """Gegenfall 'Writer belegt': ein anderswo gehaltener `lab.lock.json`-
    `flock` liefert kontrolliertes `RecoveryExclusivityUnavailableError`,
    NIE einen ungesicherten Write. Nach Freigabe funktioniert derselbe
    Aufruf normal."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _make_run(Path(td))
        rid = _make_unknown_orphan(run_dir)
        plan = recovery_ops.plan_orphan_recovery(run_dir)
        item = next(o for o in plan["orphans"] if o["request_id"] == rid)

        lock_path = run_dir / "lab.lock.json"
        lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o644)
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            raised = None
            try:
                recovery_ops.apply_orphan_recovery(run_dir, request_id=rid, reason="x", plan=item)
            except recovery_ops.RecoveryExclusivityUnavailableError as exc:
                raised = exc
            assert raised is not None, "ein belegter Lab-Lock haette apply_orphan_recovery blockieren muessen."
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)

        result = recovery_ops.apply_orphan_recovery(run_dir, request_id=rid, reason="x", plan=item)
        assert result["status"] == "applied", "nach Freigabe des Locks muss derselbe Aufruf normal funktionieren."


def test_apply_on_real_root_authorizes_bound_retry_no_modelcall_then_regular_caller_consumes():
    """R2 Punkt 6 ('Apply selbst macht KEINEN Modellcall'): `apply_orphan_
    recovery` nimmt strukturell KEINEN Transport-/GM-Parameter entgegen und
    autorisiert GENAU EINEN gebundenen Folgeversuch; der TATSAECHLICHE
    Versand passiert erst am 'regulaeren Caller', hier direkt ueber
    `request_ledger.commit_authorized_retry` nachgestellt (demselben
    Aufruf, den `runtime.SectionRuntime._admitted_decision`/`submit`
    bereits fuer genau diesen Fall verwenden, s. test_rec1_recovery_
    wiring_20261123_r1.py). Laeuft ausdruecklich auf einem Root OHNE
    `RECOVERY_SYNTHETIC_TEST_ROOT`-Marker (echter-Root-Weg)."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _make_run(Path(td))
        assert not (run_dir / recovery_ops.SYNTHETIC_ROOT_MARKER).exists(), (
            "dieser Test belegt ausdruecklich den ECHTEN (nicht synthetisch markierten) Root-Weg."
        )
        rid = _make_unknown_orphan(run_dir)
        plan = recovery_ops.plan_orphan_recovery(run_dir)
        item = next(o for o in plan["orphans"] if o["request_id"] == rid)

        result = recovery_ops.apply_orphan_recovery(
            run_dir, request_id=rid, reason="echter unbekannter Ausgang, Flo entscheidet", plan=item,
        )
        assert result["status"] == "applied"
        granted_id = result["granted_request_id"]
        follower = request_ledger.load_request(run_dir, granted_id)
        assert follower["state"] == "reserved"
        assert follower["recovery_of"] == rid

        original = request_ledger.load_request(run_dir, rid)
        assert original["state"] == "sent", "das Original bleibt bytegleich Unknown (kein sent->accounted-Shortcut)."

        # Idempotenz: ein zweiter identischer Apply-Aufruf liefert denselben Folger, kein zweiter.
        result2 = recovery_ops.apply_orphan_recovery(
            run_dir, request_id=rid, reason="echter unbekannter Ausgang, Flo entscheidet", plan=item,
        )
        assert result2["granted_request_id"] == granted_id

        # Regulaerer Caller konsumiert GENAU diesen Folger -- KEIN Modellcall in apply_orphan_recovery selbst.
        request_ledger.commit_authorized_retry(run_dir, granted_id, content="tatsaechlich jetzt gesendeter Kontext", reserved_usd=0.02)
        request_ledger.finish_received(run_dir, granted_id, usage={"usd": 0.02}, result_text="echte Antwort")
        assert request_ledger.load_request(run_dir, granted_id)["state"] == "accounted"


# ───────────────── commit_authorized_retry Original-/Grantbindung ───────────


def test_commit_authorized_retry_rejects_record_without_matching_disposition():
    """R2 Punkt d (RECOVERY_REVIEW.md R2 Z.60-62): `commit_authorized_
    retry` verlangt jetzt zusaetzlich eine tatsaechlich passende
    Disposition (nicht mehr nur ein truthy `recovery_of`+`state=reserved`)
    -- ein von Hand konstruierter Record mit `recovery_of` auf ein
    Original, FUER DAS ES NIE eine `dispose_open_orphan`-Disposition gab,
    wird abgelehnt."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _make_run(Path(td))
        rid = _make_unknown_orphan(run_dir)
        forged_id = "forged-follower-id"
        forged_record = dict(request_ledger.load_request(run_dir, rid))
        forged_record.update({"id": forged_id, "state": "reserved", "recovery_of": rid, "recovery_reason": "forged"})
        request_ledger._write_request(run_dir, forged_id, forged_record)

        raised = None
        try:
            request_ledger.commit_authorized_retry(run_dir, forged_id, content="x", reserved_usd=0.01)
        except ValueError as exc:
            raised = exc
        assert raised is not None, (
            "FIX: commit_authorized_retry haette einen Folger ohne passende Disposition ablehnen muessen."
        )


def test_commit_authorized_retry_rejects_mismatched_granted_id():
    """Eine Disposition existiert, ihr `granted_request_id` zeigt aber auf
    einen ANDEREN Folger als den tatsaechlich committeten -- kontrollierte
    Ablehnung statt Buchung auf einem fremden Folger."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _make_run(Path(td))
        rid = _make_unknown_orphan(run_dir)
        request_ledger.dispose_open_orphan(run_dir, rid, reason="x")
        real_follower = request_ledger.authorize_bound_retry(run_dir, rid)

        forged_id = "forged-second-follower"
        forged_record = dict(request_ledger.load_request(run_dir, real_follower))
        forged_record["id"] = forged_id
        request_ledger._write_request(run_dir, forged_id, forged_record)

        raised = None
        try:
            request_ledger.commit_authorized_retry(run_dir, forged_id, content="x", reserved_usd=0.01)
        except ValueError as exc:
            raised = exc
        assert raised is not None, (
            "FIX: commit_authorized_retry haette einen Folger abgelehnt, dessen id nicht granted_request_id entspricht."
        )


def test_commit_authorized_retry_rejects_stale_original_binding():
    """Das Original hat sich seit der Disposition veraendert (hier:
    zwischenzeitlich doch durabel beantwortet) -- `commit_authorized_
    retry` lehnt die Buchung auf dem Folger kontrolliert ab
    (`StaleDispositionError`), auch wenn der Folger selbst unveraendert
    `reserved` ist."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _make_run(Path(td))
        rid = _make_unknown_orphan(run_dir)
        request_ledger.dispose_open_orphan(run_dir, rid, reason="x")
        follower = request_ledger.authorize_bound_retry(run_dir, rid)

        original = dict(request_ledger.load_request(run_dir, rid))
        original["state"] = "received"
        original["result_text"] = "nachtraeglich doch da"
        request_ledger._write_request(run_dir, rid, original)

        raised = None
        try:
            request_ledger.commit_authorized_retry(run_dir, follower, content="x", reserved_usd=0.01)
        except request_ledger.StaleDispositionError as exc:
            raised = exc
        assert raised is not None, (
            "FIX: commit_authorized_retry haette eine veraltete Original-/Grantbindung ablehnen muessen."
        )


# ───────────────────────────── TUI-Menuepfad (R2 c) ──────────────────────────


def test_tui_menu_cancel_is_a_no_op_byte_identical():
    """R2 Punkt 7 ('Abbruch/Zurueck bleiben wirkungslos'): waehlt ein
    Nutzer `/zurueck` fuer den einzigen echten UNKNOWN-Orphan, bleibt der
    Run BYTEGLEICH -- kein Write, keine Autorisierung."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _make_run(Path(td))
        _make_unknown_orphan(run_dir)
        before = _snapshot(run_dir)
        fake = _FakeTuiSession(run_dir, answers=[("", "zurueck")])
        TuiSession._offer_orphan_recovery_menu(fake)
        after = _snapshot(run_dir)
        assert after == before, "Abbruch/Zurueck im Orphan-Recovery-Menue darf den Run NICHT veraendern."


def test_tui_menu_explicit_no_is_a_no_op():
    """Eine explizite 'n'-Antwort autorisiert ebenfalls KEINEN Retry (kein
    Write) -- unterscheidbar von '/zurueck', aber dieselbe Wirkungslosigkeit."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _make_run(Path(td))
        _make_unknown_orphan(run_dir)
        before = _snapshot(run_dir)
        fake = _FakeTuiSession(run_dir, answers=[("n", None)])
        TuiSession._offer_orphan_recovery_menu(fake)
        after = _snapshot(run_dir)
        assert after == before, "Eine explizite 'n'-Antwort darf den Run NICHT veraendern."


def test_tui_menu_yes_authorizes_bound_retry_then_regular_caller_consumes():
    """Eine bewusste 'j'-Antwort autorisiert GENAU EINEN gebundenen Folger
    ueber `recovery_ops.apply_orphan_recovery` (kein Modellcall) -- danach
    erreicht ein regulaerer Caller (hier `commit_authorized_retry`
    nachgestellt) denselben Folger (R2 Punkt 7: 'erreicht Fortsetzen
    denselben regulaeren Caller')."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _make_run(Path(td))
        rid = _make_unknown_orphan(run_dir)
        fake = _FakeTuiSession(run_dir, answers=[("j", None)])
        TuiSession._offer_orphan_recovery_menu(fake)

        original = request_ledger.load_request(run_dir, rid)
        assert original["state"] == "sent", "das Original bleibt Unknown (kein erfundenes Ergebnis)."

        disposition = request_ledger.load_recovery_disposition(run_dir, rid)
        assert disposition is not None and disposition.get("granted_request_id")
        granted_id = disposition["granted_request_id"]
        follower = request_ledger.load_request(run_dir, granted_id)
        assert follower["state"] == "reserved" and follower["recovery_of"] == rid

        request_ledger.commit_authorized_retry(run_dir, granted_id, content="echter Folgeversand", reserved_usd=0.02)
        request_ledger.finish_received(run_dir, granted_id, usage={"usd": 0.02}, result_text="echte Antwort")
        assert request_ledger.load_request(run_dir, granted_id)["state"] == "accounted"


def test_tui_menu_shows_durable_results_without_prompting_for_retry():
    """R2 Punkt 2: liegt bereits ein durables Originalresultat vor, wird
    KEINE Ja/Nein-Wahl angeboten (keine `_readline_with_controls`-Antwort
    wird konsumiert -- `_FakeTuiSession` wirft sonst) -- die Anzeige allein
    reicht."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _make_run(Path(td))
        rid = _make_unknown_orphan(run_dir)
        _resolve_identity_via_consumed_follower(run_dir, rid, result_text="bereits da")
        fake = _FakeTuiSession(run_dir, answers=[])
        TuiSession._offer_orphan_recovery_menu(fake)
        assert any("durabel" in line for line in fake.printed)


def main() -> int:
    tests = [
        test_plan_orphan_recovery_is_read_only_and_cheap,
        test_durable_result_is_preferred_over_retry_and_apply_rejects_it,
        test_lost_without_text_is_not_a_retry_candidate,
        test_apply_without_plan_is_rejected,
        test_apply_rejects_changed_pre_state,
        test_apply_rejects_foreign_run_binding,
        test_apply_rejects_when_writer_busy,
        test_apply_on_real_root_authorizes_bound_retry_no_modelcall_then_regular_caller_consumes,
        test_commit_authorized_retry_rejects_record_without_matching_disposition,
        test_commit_authorized_retry_rejects_mismatched_granted_id,
        test_commit_authorized_retry_rejects_stale_original_binding,
        test_tui_menu_cancel_is_a_no_op_byte_identical,
        test_tui_menu_explicit_no_is_a_no_op,
        test_tui_menu_yes_authorizes_bound_retry_then_regular_caller_consumes,
        test_tui_menu_shows_durable_results_without_prompting_for_retry,
    ]
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
