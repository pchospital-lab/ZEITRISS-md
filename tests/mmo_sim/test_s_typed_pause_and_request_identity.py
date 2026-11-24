#!/usr/bin/env python3
"""
tests/mmo_sim/test_s_typed_pause_and_request_identity.py — ZR-N2-
STABILISIERUNG-WEITERLAUF-20261017-R1 Nacharbeit (ABNAHME.json Vorstart-
gruppe `typed_pause_and_request_identity`: "Dauerhafte Reparatur/
Originalbindung, keine Doppeluebernahme oder Neuversendung unbekannter
Requests"). S1-S3 selbst sind unveraendert (01_AUFTRAG.md) -- diese Datei
liefert den bisher fehlenden gezielten, asserting Gate-Test fuer genau
diese EINE Vorstartgruppe.

Faehrt den ECHTEN Produktpfad `core.creation_service.run_admitted_creation_
dialog` (gemeinsamer Kern des fortsetzbaren SL-Erschaffungsdialogs, von
Mensch UND Persona genutzt, s. dessen Moduldocstring) direkt an -- keine
Mocks/Patches AUF diesem Pfad selbst, nur Fakes an der aeussersten
Transport-/Antwortgrenze (GM-Transport, Antwortgeber). Admission-Gate,
Requestledger (`core/request_ledger.py`) und Onboarding-Checkpoint laufen
echt.

A - Ein am Admission-Gate pausierter Vorgang liefert ein TYPISIERTES
    `CreationDialogOutcome(status="paused", ...)` -- kein stiller Erfolg
    (`status="completed"`), kein unbehandelter Abbruch (Exception), kein
    Modellaufruf VOR der Pause. Gegenprobe: dieselbe Funktion liefert fuer
    einen echten erfolgreichen Durchlauf ein unterscheidbares
    `status="completed"` -- "paused" ist kein Catch-all, der jeden Ausgang
    verdeckt.
B - Ein bereits VOR dem Transportaufruf committeter, aber nie
    abgeschlossener Requestdatensatz (`state=sent`, exakt der S1-Befund:
    "beweist weder physischen Dispatch noch eine leere Modellantwort") wird
    bei einem kalten JSON-Reentry fuer DIESELBE Operationsidentitaet NICHT
    als abgeschlossen/adoptierbar behandelt und NICHT automatisch durch
    einen zweiten Versand ersetzt. REC-1-Nachzug (04_REQUEST_RECOVERY.md
    §2A/§3, ZR-UPDATE-RESUME-REPARATUR 2026-11-23): `run_admitted_creation_
    dialog` prueft diesen Fall jetzt VOR `request_ledger.begin()`
    (`request_ledger.find_open_orphan`, dieselbe Pruefung, die `begin()`
    sonst intern per `OpenReservationExistsError` durchsetzt) und liefert
    ein TYPISIERTES `CreationDialogOutcome(status="paused", reason=
    "open_orphan_unresolved_sent_without_result")` statt eines unbehandelten
    Abbruchs -- 04 §3: "typisierte Pause-/Stop-/HOLD-Ausgaenge statt
    pauschales except Exception". `begin()`s eigene Pruefung bleibt
    unveraendert als letzte Verteidigungslinie bestehen. Der GM-Transport
    wird dabei NIE erreicht, es entsteht KEIN zweiter Requestdatensatz.
C - Ein bereits durabel EMPFANGENER (`accounted`) Request fuer eine
    Operationsidentitaet bleibt bei einem kalten JSON-Reentry UNTER SEINER
    URSPRUENGLICHEN Record-ID gebunden (Originalbindung) und wird NICHT ein
    zweites Mal versendet -- der GM-Transport wird fuer GENAU DIESEN Turn
    nie ein zweites Mal aufgerufen, ein erneuter Nachschlag
    (`find_durable_result`) liefert weiterhin DIESELBE Record-ID (keine
    Neu-Adoption unter einer anderen Identitaet).

Ausschliesslich echte Produktprimitiven (`request_ledger.begin`/
`finish_received`, `onboarding.start_or_resume`, `admission.write_test_
profile`) plus Fakes an der aeussersten Transport-/Antwortgrenze. Kein
echter Modellaufruf, kein Netzwerk. Pure Python, nur `assert`, echter
Exitcode."""
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

from _full_v7_fixture import full_v7_block_text  # noqa: E402

from mmo_sim.core import request_ledger as ledger  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.creation_service import (  # noqa: E402
    CreationDialogOutcome, ReplyResult, run_admitted_creation_dialog,
)
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402

PARTICIPANT = "typed_pause_participant"


class _GM:
    """Zeichnet jeden tatsaechlichen Transportaufruf auf -- das
    Pruefkriterium in jedem Testfall ist, OB/WIE OFT dieser Fake je
    erreicht wird, nicht nur sein Rueckgabewert. `output_limit_tokens`
    (wie jeder echte GM-Transport, s. `core.creation_service.
    run_admitted_creation_dialog`s `gm_output_limit`) macht
    `output_bound_known=True` fuer `read_admission_block` -- ohne dieses
    Feld wuerde ein konfiguriertes `max_usd` JEDE Anfrage ablehnen (Q07),
    unabhaengig vom hier getesteten Verhalten."""

    output_limit_tokens = 50

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls: list[int] = []

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append(idx)
        if not self.replies:
            raise AssertionError(f"GM-Transport ohne gescriptete Antwort fuer turn_idx={idx} aufgerufen")
        return {"content": self.replies.pop(0), "usage": {}}


def _unreached_get_reply(turn_idx: int, sl_text: str) -> ReplyResult:
    raise AssertionError(
        f"get_reply() darf bei einer VOR Erhalt einer SL-Antwort pausierten/gesperrten "
        f"Operation nicht erreicht werden (turn_idx={turn_idx})"
    )


# ===========================================================================
# A -- typisiertes paused-Outcome statt stillem Erfolg/Abbruch
# ===========================================================================

def test_a_blocked_admission_returns_typed_paused_outcome_no_transport():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        onboarding_dir = root / "onboarding"
        # Budget bereits bei 0 offenen Turns -- das Admission-Gate blockiert
        # den ALLERERSTEN Turn, BEVOR irgendein Transport/Request entsteht.
        write_test_profile(run_dir, max_turns=0)
        onboarding.start_or_resume(onboarding_dir, PARTICIPANT)

        gm = _GM([])
        outcome = run_admitted_creation_dialog(
            run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=PARTICIPANT,
            turn_idx_start=0, initial_outgoing="SYNTHETIC: Ich moechte einen Chrononauten erschaffen.",
            gm_transport=gm, get_reply=_unreached_get_reply, harvest_validator=ZeitrissHarvestValidator(),
            role="creation_dialog",
        )

        assert isinstance(outcome, CreationDialogOutcome), type(outcome)
        assert outcome.status == "paused", (
            f"ein blockiertes Admission-Gate muss ein TYPISIERTES paused-Outcome liefern, "
            f"kein stiller Erfolg -- erhalten: {outcome!r}"
        )
        assert outcome.reason, "paused ohne Grund ist kein belegtes Outcome"
        assert outcome.save_block is None and outcome.chrononaut_id is None, (
            "ein paused-Outcome darf NIE gleichzeitig einen Save/eine Chrononaut-ID tragen "
            "(kein verdeckter Teilabschluss)"
        )
        assert gm.calls == [], "Admission-Gate muss VOR jedem Transportaufruf blockieren"
        assert ledger.open_requests(run_dir) == [], (
            "ein am Admission-Gate blockierter Versuch darf KEINEN Requestdatensatz hinterlassen"
        )


def test_a_paused_outcome_is_distinguishable_from_completed():
    # Gegenprobe: dieselbe Funktion liefert fuer einen ERFOLGREICHEN
    # Durchlauf ein ANDERES status-Feld -- "paused" ist kein Catch-all-
    # Rueckgabewert, der jeden Ausgang verdeckt.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        onboarding_dir = root / "onboarding"
        write_test_profile(run_dir, max_turns=10, max_usd=10.0)
        onboarding.start_or_resume(onboarding_dir, PARTICIPANT)

        gm = _GM([full_v7_block_text("typed-pause-chr-a2", name="TypedPauseA2")])
        outcome = run_admitted_creation_dialog(
            run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=PARTICIPANT,
            turn_idx_start=0, initial_outgoing="SYNTHETIC: Start.",
            gm_transport=gm, get_reply=_unreached_get_reply, harvest_validator=ZeitrissHarvestValidator(),
            role="creation_dialog",
        )
        assert outcome.status == "completed", outcome
        assert outcome.chrononaut_id == "typed-pause-chr-a2"
        assert gm.calls == [0]


# ===========================================================================
# B -- unbekannter `sent`-Record wird NICHT adoptiert/neu versendet
# ===========================================================================

def test_b_cold_reentry_refuses_unknown_sent_record_no_resend():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        onboarding_dir = root / "onboarding"
        write_test_profile(run_dir, max_turns=10, max_usd=10.0)
        onboarding.start_or_resume(onboarding_dir, PARTICIPANT)

        # S1-Befund nachgebaut: `begin()` committet die Reservierung UND
        # markiert state=sent VOR dem eigentlichen Transportaufruf -- ein
        # Absturz GENAU hier (Transport nie abgeschlossen, kein
        # `finish_received`/`finish_error`) hinterlaesst exakt diesen
        # Record: `sent`, kein `result_text`, kein Abschluss.
        stuck_id = ledger.begin(
            run_dir, role="creation_dialog", content="SYNTHETIC: Start.", reserved_usd=0.001,
            table_id=None, section_id=None, turn_idx=0, participant=PARTICIPANT,
        )
        stuck_before = ledger.load_request(run_dir, stuck_id)
        assert stuck_before["state"] == "sent" and stuck_before["result_text"] is None

        gm = _GM([full_v7_block_text("typed-pause-chr-b", name="TypedPauseB")])
        # REC-1-Nachzug: `run_admitted_creation_dialog` liefert jetzt ein
        # TYPISIERTES `CreationDialogOutcome(status="paused", ...)` statt
        # die rohe `OpenReservationExistsError` unbehandelt zu propagieren
        # (04 §3) -- `find_open_orphan` faengt denselben Befund VOR
        # `begin()` ab.
        outcome = run_admitted_creation_dialog(
            run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=PARTICIPANT,
            turn_idx_start=0, initial_outgoing="SYNTHETIC: Start.",
            gm_transport=gm, get_reply=_unreached_get_reply, harvest_validator=ZeitrissHarvestValidator(),
            role="creation_dialog",
        )

        assert outcome.status == "paused", (
            "ein kalter JSON-Reentry fuer dieselbe Operationsidentitaet darf einen unbekannten "
            "state=sent-Record NICHT stillschweigend als abgeschlossen/adoptierbar behandeln -- "
            f"er muss kontrolliert verweigert werden (typisierte Pause statt Exception). outcome={outcome}"
        )
        assert outcome.reason == "open_orphan_unresolved_sent_without_result", outcome.reason
        assert gm.calls == [], (
            "ein unbekannter sent-Record darf NIEMALS automatisch durch einen zweiten echten "
            "Transportaufruf 'ersetzt'/neu versendet werden"
        )

        on_disk = sorted(f.name for f in (run_dir / "requests").glob("*.json"))
        assert on_disk == [f"{stuck_id}.json"], (
            f"es darf KEIN zweiter Requestdatensatz fuer dieselbe Operationsidentitaet entstehen: {on_disk}"
        )
        stuck_after = ledger.load_request(run_dir, stuck_id)
        assert stuck_after == stuck_before, (
            "der urspruengliche, unbekannte Record darf durch den verweigerten Reentry-Versuch "
            "nicht veraendert werden"
        )


# ===========================================================================
# C -- bereits empfangener Request bleibt unter seiner Original-ID gebunden
# ===========================================================================

def test_c_durable_result_keeps_original_record_id_no_second_transport():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        onboarding_dir = root / "onboarding"
        write_test_profile(run_dir, max_turns=10, max_usd=10.0)
        onboarding.start_or_resume(onboarding_dir, PARTICIPANT)

        sl_text_0 = "SYNTHETIC: Wie soll dein Rufname lauten?"
        # Turn 0 wurde bereits real gesendet UND durabel empfangen
        # (`accounted`) -- der lokale Onboarding-Checkpoint fuer GENAU
        # DIESEN Schritt ist (simulierter Absturz) noch nicht geschrieben.
        # Ein Folgeprozess kennt den Text deshalb nur ueber den bereits
        # dauerhaften Ledger-Datensatz (C2-Pfad).
        original_id = ledger.begin(
            run_dir, role="creation_dialog", content="SYNTHETIC: Start.", reserved_usd=0.001,
            table_id=None, section_id=None, turn_idx=0, participant=PARTICIPANT,
        )
        ledger.finish_received(run_dir, original_id, usage={}, seconds=1.0, result_text=sl_text_0)
        accounted = ledger.load_request(run_dir, original_id)
        assert accounted["state"] == "accounted" and accounted["result_text"] == sl_text_0

        gm = _GM([full_v7_block_text("typed-pause-chr-c", name="TypedPauseC")])

        def get_reply(turn_idx, sl_text):
            # Der Antwortgeber reagiert auf den WIEDERVERWENDETEN Turn-0-
            # Text -- `turn_idx` selbst ruckt erst NACH dieser Antwort (in
            # `onboarding.record_step`) auf 1 vor.
            assert turn_idx == 0 and sl_text == sl_text_0, (turn_idx, sl_text)
            return ReplyResult(kind="answer", text="SYNTHETIC: Phoenix.")

        outcome = run_admitted_creation_dialog(
            run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=PARTICIPANT,
            turn_idx_start=0, initial_outgoing="SYNTHETIC: Start.",
            gm_transport=gm, get_reply=get_reply, harvest_validator=ZeitrissHarvestValidator(),
            role="creation_dialog",
        )

        assert gm.calls == [1], (
            "Turn 0 wurde bereits durabel empfangen -- der kalte Reentry darf ihn NICHT ein "
            "zweites Mal real versenden; nur der echte NEUE Turn 1 ist ein zusaetzlicher "
            f"Transportaufruf. Tatsaechliche Calls: {gm.calls}"
        )
        assert outcome.status == "completed" and outcome.chrononaut_id == "typed-pause-chr-c", outcome

        # Originalbindung: GENAU EIN Requestdatensatz fuer turn_idx=0, seine
        # ID bleibt UNVERAENDERT `original_id` -- kein zweiter, abweichender
        # Treffer fuer dieselbe Operationsidentitaet.
        records_turn0 = [
            json.loads(p.read_text(encoding="utf-8"))
            for p in sorted((run_dir / "requests").glob("*.json"))
        ]
        records_turn0 = [r for r in records_turn0 if r.get("turn_idx") == 0]
        assert len(records_turn0) == 1 and records_turn0[0]["id"] == original_id, (
            f"Turn 0 darf keinen ZWEITEN Requestdatensatz erhalten -- seine Record-ID bleibt "
            f"dauerhaft an den urspruenglichen begin()-Aufruf gebunden: {records_turn0}"
        )

        # (c) Ein bereits erledigter Request wird nicht erneut adoptiert:
        # ein weiterer kalter Nachschlag fuer GENAU DIESE Operations-
        # identitaet liefert weiterhin DENSELBEN Record -- keine neue ID,
        # keine zweite Adoption unter einer anderen Identitaet.
        re_lookup = ledger.find_durable_result(
            run_dir, table_id=None, section_id=None, role="creation_dialog",
            turn_idx=0, participant=PARTICIPANT,
        )
        assert re_lookup is not None and re_lookup["id"] == original_id, re_lookup


# ===========================================================================
# D -- REC-2: additive Unknown-Disposition + EIN crashfest gebundener Retry
# ===========================================================================

def _make_stuck_orphan(run_dir):
    return ledger.begin(
        run_dir, role="creation_dialog", content="SYNTHETIC: alter Versuch.", reserved_usd=0.001,
        table_id=None, section_id=None, turn_idx=0, participant=PARTICIPANT,
    )


def test_d1_dispose_open_orphan_idempotent_and_rejects_stale_vorzustand():
    """REC-2 §2B/§2C: `dispose_open_orphan` ist additiv (Originalrecord
    bytegleich unveraendert), idempotent (zweiter Aufruf auf UNVERAENDERTEM
    Vorzustand liefert dieselbe Disposition, kein zweiter Eintrag) und lehnt
    eine Neuerstellung auf einem INZWISCHEN veraenderten Vorzustand ab
    (`StaleDispositionError`, 04 §2C: 'veraenderte Zielbindung/Vorzustand
    VOR Wirkung ablehnen')."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        write_test_profile(run_dir)
        stuck_id = _make_stuck_orphan(run_dir)
        stuck_before = ledger.load_request(run_dir, stuck_id)

        disp1 = ledger.dispose_open_orphan(run_dir, stuck_id, reason="PID tot, Prozess neu gestartet")
        assert disp1["original_request_id"] == stuck_id
        assert disp1["granted_request_id"] is None
        stuck_after_disp = ledger.load_request(run_dir, stuck_id)
        assert stuck_after_disp == stuck_before, "dispose_open_orphan darf den Originalrecord NICHT schreiben"

        # Idempotent: zweiter Aufruf auf unveraendertem Vorzustand liefert
        # dieselbe Disposition (kein zweiter Eintrag, kein verlorener Grund).
        disp2 = ledger.dispose_open_orphan(run_dir, stuck_id, reason="anderer Grund -- wird ignoriert")
        assert disp2 == disp1, "ein zweiter dispose-Aufruf auf unveraendertem Vorzustand muss No-op sein"

        # Vorzustand aendert sich (z.B. doch noch durabel empfangen) --
        # eine erneute Disposition auf dem jetzt veralteten Befund wird
        # kontrolliert abgelehnt, nicht stillschweigend ueberschrieben.
        ledger.finish_received(run_dir, stuck_id, usage={"usd": 0.001}, seconds=1.0, result_text="spaet gefunden")
        # Disposition selbst bleibt als Beleg bestehen (reiner Lesevorgang,
        # kein Loeschen) -- nur eine NEUE dispose-Anfrage auf dem jetzt
        # widersprechenden Vorzustand wird kontrolliert verweigert.
        raised = None
        try:
            ledger.dispose_open_orphan(run_dir, stuck_id, reason="erneuter Versuch auf veraltetem Stand")
        except ledger.StaleDispositionError as e:
            raised = e
        assert raised is not None, "dispose_open_orphan auf einem veraenderten Vorzustand muss StaleDispositionError werfen"


def test_d2_authorize_bound_retry_is_idempotent_and_survives_simulated_crash():
    """REC-2 §2C: `authorize_bound_retry` liefert bei wiederholtem Aufruf
    IMMER dieselbe neue Request-ID (kein zweiter Nachfolger) UND bleibt
    crashfest, wenn ein simulierter Absturz GENAU zwischen 'neuer Record
    geschrieben' und 'Disposition aktualisiert' nachgebildet wird (derselbe
    deterministische Dateiname wird beim Retry wiedergefunden, kein dritter
    Record)."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        write_test_profile(run_dir)
        stuck_id = _make_stuck_orphan(run_dir)
        ledger.dispose_open_orphan(run_dir, stuck_id, reason="Orphan-Recovery-Test")

        new_id_1 = ledger.authorize_bound_retry(run_dir, stuck_id)
        new_id_2 = ledger.authorize_bound_retry(run_dir, stuck_id)
        assert new_id_1 == new_id_2, "wiederholtes Apply muss dieselbe Request-ID liefern (No-op, 04 §2C)"

        new_records = [
            r for r in (
                json.loads(p.read_text(encoding="utf-8")) for p in (run_dir / "requests").glob("*.json")
            )
            if r.get("recovery_of") == stuck_id
        ]
        assert len(new_records) == 1 and new_records[0]["id"] == new_id_1, (
            f"es darf GENAU EIN gebundener Folgerecord fuer {stuck_id!r} entstehen: {new_records}"
        )
        assert new_records[0]["state"] == "reserved" and new_records[0]["sent_ts"] is None, (
            "ein autorisierter, aber noch nicht vom regulaeren Caller verwendeter Retry "
            "darf NICHT bereits 'sent' sein -- der Versand erfolgt erst ueber den regulaeren "
            "Caller (04 §2D)."
        )

        # Crash-Simulation: die Disposition wird kuenstlich auf ihren
        # Zustand VOR dem Granted-Update zurueckgesetzt (als waere der
        # Prozess NACH dem Record-Write, aber VOR dem Disposition-Update
        # abgestuerzt) -- ein erneuter Aufruf darf dann KEINEN dritten,
        # neuen Record anlegen, sondern muss den bereits vorhandenen
        # deterministischen Record wiederfinden und binden.
        disp_path = run_dir / "recovery_dispositions" / f"{stuck_id}.json"
        disp = json.loads(disp_path.read_text(encoding="utf-8"))
        disp["granted_request_id"] = None
        disp_path.write_text(json.dumps(disp), encoding="utf-8")

        new_id_3 = ledger.authorize_bound_retry(run_dir, stuck_id)
        assert new_id_3 == new_id_1, "nach simuliertem Absturz muss derselbe deterministische Record wiedergefunden werden"
        new_records_after_crash = [
            r for r in (
                json.loads(p.read_text(encoding="utf-8")) for p in (run_dir / "requests").glob("*.json")
            )
            if r.get("recovery_of") == stuck_id
        ]
        assert len(new_records_after_crash) == 1, (
            f"kein dritter Record nach simuliertem Absturz+Retry: {new_records_after_crash}"
        )


def test_d3_authorize_bound_retry_rejects_stale_original():
    """REC-2 §2C: ein Apply auf einer Disposition, deren Originalrecord sich
    seit der Disposition veraendert hat, wird kontrolliert abgelehnt
    (`StaleDispositionError`) statt auf einem ueberholten Vorzustand zu
    binden."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        write_test_profile(run_dir)
        stuck_id = _make_stuck_orphan(run_dir)
        ledger.dispose_open_orphan(run_dir, stuck_id, reason="Orphan-Recovery-Test")

        # Originalrecord aendert sich NACH der Disposition (z.B. spaet
        # gefundenes Ergebnis via anderem Pfad verbucht).
        ledger.finish_received(run_dir, stuck_id, usage={"usd": 0.001}, seconds=1.0, result_text="spaet gefunden")

        raised = None
        try:
            ledger.authorize_bound_retry(run_dir, stuck_id)
        except ledger.StaleDispositionError as e:
            raised = e
        assert raised is not None, "authorize_bound_retry auf einem veraenderten Vorzustand muss ablehnen"


def test_d4_commit_authorized_retry_books_once_no_double_booking():
    """REC-2 §2C: `commit_authorized_retry` bucht die Reservierung GENAU
    EINMAL und transitioniert nach `state="sent"` -- ein zweiter Aufruf
    (z.B. nach einem Absturz zwischen Commit und dem eigentlichen
    Transport-Call, gefolgt von einem Retry desselben regulaeren Callers)
    bucht NICHT doppelt (No-op, da `state != "reserved"` beim zweiten
    Aufruf)."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        write_test_profile(run_dir, max_turns=10, max_usd=10.0)
        stuck_id = _make_stuck_orphan(run_dir)
        ledger.dispose_open_orphan(run_dir, stuck_id, reason="Orphan-Recovery-Test")
        new_id = ledger.authorize_bound_retry(run_dir, stuck_id)

        status_before = json.loads((run_dir / "lab.status.json").read_text())
        ledger.commit_authorized_retry(
            run_dir, new_id, content="SYNTHETIC: tatsaechlicher neuer Versuch.", reserved_usd=0.01,
        )
        status_after_first = json.loads((run_dir / "lab.status.json").read_text())
        assert status_after_first["usd_spent"] - status_before["usd_spent"] >= 0.01 - 1e-9, status_after_first
        record_after_first = ledger.load_request(run_dir, new_id)
        assert record_after_first["state"] == "sent" and record_after_first["sent_ts"] is not None

        # Zweiter Aufruf (simulierter Caller-Retry nach Absturz vor dem
        # eigentlichen Transport-Call) -- KEINE zweite Buchung.
        ledger.commit_authorized_retry(
            run_dir, new_id, content="SYNTHETIC: tatsaechlicher neuer Versuch.", reserved_usd=0.01,
        )
        status_after_second = json.loads((run_dir / "lab.status.json").read_text())
        assert status_after_second["usd_spent"] == status_after_first["usd_spent"], (
            "ein zweiter commit_authorized_retry-Aufruf auf einem bereits 'sent' Record darf "
            f"NICHT erneut buchen: {status_after_first} vs {status_after_second}"
        )


def test_d5_end_to_end_authorized_retry_consumed_by_real_caller_exactly_once():
    """REC-2 Ende-zu-Ende (04 §2B/§2C/§2D, ECHTER Caller
    `run_admitted_creation_dialog`, nur `_GM` an der aeussersten Grenze
    gedoppelt): ein disponierter + autorisierter Orphan wird vom REGULAEREN
    Caller konsumiert -- GENAU EIN echter GM-Call (fuer den autorisierten
    Folgeversuch), KEIN Pause-Outcome mehr fuer turn_idx=0, der Dialog
    schliesst normal mit `status="completed"` ab. Beweist, dass die REC-1-
    Pause (`test_b_...` oben) nach einer bewussten Recovery-Entscheidung
    NICHT mehr greift, OHNE den `sent→accounted`-Shortcut zu nehmen (der
    autorisierte Record durchlaeuft den reguaeren `commit_authorized_retry`
    -> echter Transport -> `finish_received`-Weg wie jeder normale Turn)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        onboarding_dir = root / "onboarding"
        write_test_profile(run_dir, max_turns=10, max_usd=10.0)
        onboarding.start_or_resume(onboarding_dir, PARTICIPANT)

        stuck_id = ledger.begin(
            run_dir, role="creation_dialog", content="SYNTHETIC: Start.", reserved_usd=0.001,
            table_id=None, section_id=None, turn_idx=0, participant=PARTICIPANT,
        )
        ledger.dispose_open_orphan(run_dir, stuck_id, reason="echte-Root-Testrecovery")
        new_id = ledger.authorize_bound_retry(run_dir, stuck_id)
        assert ledger.load_request(run_dir, new_id)["state"] == "reserved"

        gm = _GM([full_v7_block_text("typed-pause-chr-d5", name="TypedPauseD5")])
        outcome = run_admitted_creation_dialog(
            run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=PARTICIPANT,
            turn_idx_start=0, initial_outgoing="SYNTHETIC: Start.",
            gm_transport=gm, get_reply=_unreached_get_reply, harvest_validator=ZeitrissHarvestValidator(),
            role="creation_dialog",
        )

        assert gm.calls == [0], (
            f"GENAU EIN echter GM-Call fuer den autorisierten Folgeversuch -- calls={gm.calls}"
        )
        assert outcome.status == "completed" and outcome.chrononaut_id == "typed-pause-chr-d5", outcome

        granted_record = ledger.load_request(run_dir, new_id)
        assert granted_record["state"] == "accounted", granted_record
        assert granted_record["result_text"], "der autorisierte Folgeversuch muss real empfangenen Text binden"

        stuck_after = ledger.load_request(run_dir, stuck_id)
        assert stuck_after["state"] == "sent" and stuck_after["result_text"] is None, (
            "der urspruengliche Orphan-Record bleibt als historischer Beleg unveraendert bei "
            f"state='sent' -- KEIN sent->accounted-Shortcut: {stuck_after}"
        )


def test_d6_commit_authorized_retry_crash_between_booking_and_sent_marker_no_double_booking():
    """REC-2 §2C (Vera-BLOCKER 2026-11-23): das kritische Crash-Fenster ist
    NICHT der von `test_d4` abgedeckte 'Record schon sent'-Fall, sondern ein
    Absturz GENAU ZWISCHEN der Budget-Buchung (`record_turn_usage`) und dem
    finalen `state="sent"`-Write -- der Record bleibt dann auf Platte bei
    `state="reserved"`, OBWOHL die Reservierung bereits gebucht wurde. Der
    regulaere Caller (`run_admitted_creation_dialog`) findet ihn erneut
    (immer noch `reserved`, `recovery_of` gesetzt -> kein Pause-Zweig) und
    ruft `commit_authorized_retry` fuer dieselbe deterministische id ein
    zweites Mal auf. Das darf die Reservierung NICHT doppelt buchen
    (Idempotenz ueber eine request-id-gebundene Buchungsmarke in derselben
    atomaren `lab.status.json`-Operation, analog `reconciled_request_ids`)."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        write_test_profile(run_dir, max_turns=10, max_usd=10.0)
        stuck_id = _make_stuck_orphan(run_dir)
        ledger.dispose_open_orphan(run_dir, stuck_id, reason="Orphan-Recovery-Test")
        new_id = ledger.authorize_bound_retry(run_dir, stuck_id)

        status_before = json.loads((run_dir / "lab.status.json").read_text())

        # Absturz simulieren: der ZWEITE `_write_request`-Aufruf innerhalb
        # von `commit_authorized_retry` (der `state="sent"` persistiert)
        # schlaegt fehl -- NACH der Buchung, VOR dem Zustandswechsel.
        real_write_request = ledger._write_request
        calls = {"n": 0}

        def flaky_write_request(rd, rid, data):
            calls["n"] += 1
            if calls["n"] == 2:
                raise RuntimeError("simulierter Absturz vor dem state=sent-Write")
            return real_write_request(rd, rid, data)

        ledger._write_request = flaky_write_request
        try:
            raised = None
            try:
                ledger.commit_authorized_retry(
                    run_dir, new_id, content="SYNTHETIC: tatsaechlicher neuer Versuch.", reserved_usd=0.01,
                )
            except RuntimeError as e:
                raised = e
            assert raised is not None, "Der simulierte Absturz muss propagieren (kein stiller Erfolg)."
        finally:
            ledger._write_request = real_write_request

        status_after_crash = json.loads((run_dir / "lab.status.json").read_text())
        record_after_crash = ledger.load_request(run_dir, new_id)
        # Crash-Zustand getreu: gebucht, aber Record noch 'reserved'.
        assert record_after_crash["state"] == "reserved", record_after_crash
        booked_once = status_after_crash["usd_spent"] - status_before["usd_spent"]
        assert booked_once >= 0.01 - 1e-9, f"erste Buchung fehlt: {status_after_crash}"

        # Re-Entry durch den regulaeren Caller: derselbe deterministische
        # new_id, Record noch 'reserved' -> darf NICHT ein zweites Mal buchen.
        ledger.commit_authorized_retry(
            run_dir, new_id, content="SYNTHETIC: tatsaechlicher neuer Versuch.", reserved_usd=0.01,
        )
        status_after_retry = json.loads((run_dir / "lab.status.json").read_text())
        assert status_after_retry["usd_spent"] == status_after_crash["usd_spent"], (
            "Doppelbuchung im Crash-Fenster (reserved+bereits gebucht): "
            f"{status_after_crash} -> {status_after_retry}"
        )
        assert status_after_retry["turns_used"] == status_after_crash["turns_used"], (
            "turns_used darf im Crash-Fenster-Retry nicht erneut hochzaehlen: "
            f"{status_after_crash} -> {status_after_retry}"
        )
        record_after_retry = ledger.load_request(run_dir, new_id)
        assert record_after_retry["state"] == "sent" and record_after_retry["sent_ts"] is not None, (
            "der Re-Entry muss den Zustandswechsel nachholen (Record wird endlich 'sent'), "
            f"ohne doppelt zu buchen: {record_after_retry}"
        )


def test_d7_commit_authorized_retry_crash_then_changed_reservation_no_underbooking():
    """RECOVERY_REVIEW R3 / RECOVERY_LEDGER_WITNESS (PR #3317-Nachzug 2026-11-23),
    K-Nachzug (RECOVERY_REVIEW §5/N08 "geaenderte Versand-/Billingbasis vor
    sent konsistent buchen", 2026-11-24): Gegenstueck zu test_d4/test_d6. Der
    Absturz liegt ZWISCHEN Buchung und `state="sent"` (Record bleibt
    `reserved`, 0.01 bereits gebucht); der REGULAERE Caller berechnet beim
    Re-Entry eine NEUE, HOEHERE Reservierung (0.02).

    Die ALTE Zwischenfassung (vor dem K-Nachzug) fror `reserved_usd` einfach
    auf der alten, niedrigeren Basis (0.01) ein und verliess sich darauf, dass
    `finish_received`s Delta-Mechanik die fehlende Buchung NACHTRAEGLICH
    schliesst, SOBALD eine tatsaechliche Antwort eintrifft -- das deckt genau
    DIESEN Pfad (Antwort kommt noch), aber NICHT den vom Review benannten
    Fall "Ausgang bleibt unbekannt" (Absturz/verlorene Antwort NACH diesem
    `commit_authorized_retry`): dann waere NUR 0.01 dauerhaft gebucht
    geblieben, obwohl 0.02 bereits zulaessig versandt wurde. K-FIX: die
    Differenz zur neuen, hoeheren Basis wird HIER, VOR dem `sent`-Marker,
    idempotent nachgebucht (`lab.status.json` traegt die vollen 0.02 bereits
    NACH diesem Commit, nicht erst nach einer spaeteren Antwort) UND
    `reserved_usd` wird auf die neue Basis (0.02) aktualisiert. test_d6
    (zweimal 0.01) kann diesen Fehler nicht erkennen -- deshalb dieser
    getrennte Fall."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        write_test_profile(run_dir, max_turns=10, max_usd=10.0)
        stuck_id = _make_stuck_orphan(run_dir)  # bucht die urspruenglichen 0.001
        ledger.dispose_open_orphan(run_dir, stuck_id, reason="Orphan-Recovery-Test R3")
        new_id = ledger.authorize_bound_retry(run_dir, stuck_id)
        before = json.loads((run_dir / "lab.status.json").read_text())["usd_spent"]

        real_write = ledger._write_request
        calls = {"n": 0}

        def flaky(rd, rid, data):
            calls["n"] += 1
            if calls["n"] == 2:  # der state="sent"-Write, NACH der Buchung
                raise RuntimeError("SYNTHETIC: Absturz vor state=sent")
            return real_write(rd, rid, data)

        ledger._write_request = flaky
        try:
            raised = None
            try:
                ledger.commit_authorized_retry(run_dir, new_id, content="erster Versuch", reserved_usd=0.01)
            except RuntimeError as e:
                raised = e
            assert raised is not None, "der simulierte Absturz muss propagieren"
        finally:
            ledger._write_request = real_write

        after_crash = json.loads((run_dir / "lab.status.json").read_text())["usd_spent"]
        assert ledger.load_request(run_dir, new_id)["state"] == "reserved"
        assert abs((after_crash - before) - 0.01) < 1e-9, f"erste Buchung 0.01 erwartet, got {after_crash - before}"

        # Re-Entry mit GEAENDERTER hoeherer Reservierung 0.02 -- K-FIX bucht
        # die Differenz (0.01) HIER idempotent nach und aktualisiert
        # reserved_usd auf die neue Basis.
        ledger.commit_authorized_retry(
            run_dir, new_id, content="groesserer Kontext nach Neustart", reserved_usd=0.02,
        )
        rec = ledger.load_request(run_dir, new_id)
        assert rec["state"] == "sent", rec
        assert rec["reserved_usd"] == 0.02, f"K-FIX: reserved_usd auf neue Basis 0.02 aktualisiert, got {rec['reserved_usd']}"
        # K-FIX-Kernnachweis: die volle neue Verpflichtung (0.02) steht
        # bereits HIER, VOR jedem `finish_received`/einer Antwort -- genau
        # das schliesst den vom Review benannten "Ausgang bleibt unbekannt"-
        # Fall (eine verlorene Antwort NACH diesem Commit wuerde sonst nur
        # 0.01 dauerhaft gebucht lassen).
        after_commit = json.loads((run_dir / "lab.status.json").read_text())["usd_spent"]
        assert abs((after_commit - before) - 0.02) < 1e-9, (
            f"K-FIX: volle neue Reserve 0.02 bereits VOR der Antwort gebucht erwartet, "
            f"got {after_commit - before}"
        )
        # AR3/R3 (Vera-Auflage 2026-11-23): NUR die Buchungsbasis (reserved_usd/
        # dollar_billed) friert ein. Die DESKRIPTIVEN Audit-Felder muessen den
        # TATSAECHLICH jetzt physisch gesendeten (hier GEAENDERTEN) Input spiegeln --
        # sonst behauptet der Record einen anderen Inhalt als versendet (stiller Bruch
        # der projektweiten content_sha256-Hashgarantie auf dem Recovery-Pfad).
        import hashlib as _hl
        _sent = "groesserer Kontext nach Neustart"
        assert rec["content_chars"] == len(_sent), (
            f"FIX (Vera-Auflage): content_chars muss den physisch gesendeten frischen "
            f"Text spiegeln (={len(_sent)}), nicht den Alt-Text; got {rec['content_chars']}"
        )
        assert rec["content_sha256"] == _hl.sha256(_sent.encode("utf-8")).hexdigest(), (
            "FIX (Vera-Auflage): content_sha256 muss den physisch gesendeten frischen "
            "Text spiegeln, nicht den eingefrorenen Alt-Text 'erster Versuch'"
        )

        ledger.finish_received(run_dir, new_id, usage={"usd": 0.02}, seconds=1.0, result_text="synthetische Antwort")
        after = json.loads((run_dir / "lab.status.json").read_text())["usd_spent"]
        # child-Beitrag = 0.01 Reserve + 0.01 Delta = 0.02 (nicht 0.01-Unterbuchung).
        assert abs((after - before) - 0.02) < 1e-9, (
            f"FIX: child-Gesamtkosten 0.02 (keine Unterbuchung) erwartet, got {after - before}"
        )
        # wiederholtes Settlement (K-ABNAHME "wiederholtes Settlement verliert/
        # verdoppelt nichts") -- finish_received ist fuer einen bereits
        # `accounted`en Datensatz ein No-op.
        ledger.finish_received(run_dir, new_id, usage={"usd": 0.02}, seconds=1.0, result_text="zweite Antwort?")
        after_repeat = json.loads((run_dir / "lab.status.json").read_text())["usd_spent"]
        assert after_repeat == after, (
            f"wiederholtes finish_received darf nichts erneut buchen: {after} -> {after_repeat}"
        )


def test_k1_commit_authorized_retry_crash_then_billing_class_change_books_new_obligation():
    """RECOVERY_REVIEW §5/N08 ("geaenderte Versand-/Billingbasis vor sent
    konsistent buchen", K-Nachzug 2026-11-24), zweiter bestellter Restfall:
    der VORBEREITETE (erste) Versandversuch war NICHT dollarpflichtig
    (`dollar_billed=False`, bucht 0), der Absturz liegt ZWISCHEN dieser
    (Null-)Buchung und dem `state="sent"`-Write (Record bleibt `reserved`,
    `is_reservation_booked` aber schon True -- dieselbe Buchungsmarke wird
    bereits bei einer 0-Buchung gesetzt). Der REGULAERE Caller berechnet beim
    Re-Entry eine FRISCH dollarpflichtige Route (`dollar_billed=True`,
    reserved_usd=0.02).

    Vor dem K-Fix blieb `dollar_billed` auf dem alten `False` eingefroren --
    `finish_received` ignoriert dann sogar ein tatsaechliches `usage.usd=0.02`
    vollstaendig (`compute_turn_usd` wird fuer `dollar_billed=False` gar nicht
    aufgerufen), die reale kostenpflichtige Route bliebe faelschlich
    kostenfrei verbucht. K-FIX: die volle neue Reserve (0.02, da vorher 0
    gebucht war) wird HIER, VOR dem `sent`-Marker, idempotent nachgebucht UND
    `dollar_billed`/`reserved_usd` werden auf die neue Basis aktualisiert."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        write_test_profile(run_dir, max_turns=10, max_usd=10.0)
        stuck_id = _make_stuck_orphan(run_dir)
        ledger.dispose_open_orphan(run_dir, stuck_id, reason="K-Billingwechsel-Test")
        new_id = ledger.authorize_bound_retry(run_dir, stuck_id)
        before = json.loads((run_dir / "lab.status.json").read_text())["usd_spent"]

        real_write = ledger._write_request
        calls = {"n": 0}

        def flaky(rd, rid, data):
            calls["n"] += 1
            if calls["n"] == 2:  # der state="sent"-Write, NACH der (Null-)Buchung
                raise RuntimeError("SYNTHETIC: Absturz vor state=sent (nicht dollarpflichtiger Erstversuch)")
            return real_write(rd, rid, data)

        ledger._write_request = flaky
        try:
            raised = None
            try:
                ledger.commit_authorized_retry(
                    run_dir, new_id, content="erster Versuch (nicht dollarpflichtig)",
                    reserved_usd=0.01, dollar_billed=False,
                )
            except RuntimeError as e:
                raised = e
            assert raised is not None, "der simulierte Absturz muss propagieren"
        finally:
            ledger._write_request = real_write

        stuck_record = ledger.load_request(run_dir, new_id)
        assert stuck_record["state"] == "reserved", stuck_record
        assert stuck_record["dollar_billed"] is False, stuck_record
        after_first_attempt = json.loads((run_dir / "lab.status.json").read_text())["usd_spent"]
        assert abs(after_first_attempt - before) < 1e-9, (
            f"ein nicht dollarpflichtiger Erstversuch darf NICHTS buchen: {after_first_attempt} vs {before}"
        )

        # Re-Entry mit FRISCH dollarpflichtiger Route (0.02) -- K-FIX bucht
        # die volle neue Reserve nach (vorher war 0 gebucht) und aktualisiert
        # dollar_billed/reserved_usd auf die neue Basis.
        ledger.commit_authorized_retry(
            run_dir, new_id, content="zweiter Versuch (frisch dollarpflichtig)",
            reserved_usd=0.02, dollar_billed=True,
        )
        rec = ledger.load_request(run_dir, new_id)
        assert rec["state"] == "sent", rec
        assert rec["dollar_billed"] is True, f"K-FIX: dollar_billed auf neue Basis True aktualisiert, got {rec}"
        assert rec["reserved_usd"] == 0.02, f"K-FIX: reserved_usd auf neue Basis 0.02 aktualisiert, got {rec}"
        after_commit = json.loads((run_dir / "lab.status.json").read_text())["usd_spent"]
        assert abs((after_commit - before) - 0.02) < 1e-9, (
            f"K-FIX: volle neue Reserve 0.02 bereits VOR der Antwort gebucht erwartet (vorher 0 "
            f"gebucht), got {after_commit - before}"
        )

        # Re-Entry-Idempotenz der Nachbuchung selbst: ein wiederholter Aufruf
        # (z.B. nach einem weiteren Absturz NACH der Nachbuchung) darf die
        # Differenz nicht nochmal buchen.
        ledger.commit_authorized_retry(
            run_dir, new_id, content="zweiter Versuch (frisch dollarpflichtig)",
            reserved_usd=0.02, dollar_billed=True,
        )
        after_second_commit = json.loads((run_dir / "lab.status.json").read_text())["usd_spent"]
        assert after_second_commit == after_commit, (
            f"wiederholter commit_authorized_retry (Record bereits 'sent') darf nicht erneut "
            f"buchen: {after_commit} -> {after_second_commit}"
        )

        ledger.finish_received(run_dir, new_id, usage={"usd": 0.02}, seconds=1.0, result_text="kostenpflichtige Antwort")
        after = json.loads((run_dir / "lab.status.json").read_text())["usd_spent"]
        assert abs((after - before) - 0.02) < 1e-9, (
            f"K-FIX: Gesamtkosten bleiben 0.02 (kein Verlust, keine Verdopplung durch Settlement), "
            f"got {after - before}"
        )


def test_bf1_labstatus_reader_and_writer_preserve_booked_marker():
    """BUDGET_FLOW_REVIEW BF-1 (PR #3317-Nachzug): `record_turn_usage(once_
    request_id=...)` schreibt `booked_reservation_request_ids` ins
    `lab.status.json`. Vor dem Fix fehlte das Feld in der `LabStatus`-Dataclass
    -> `read_status` (`LabStatus(**json)`) warf TypeError, sobald eine
    Retry-Buchung stattgefunden hatte. FIX: Feld ergaenzt (optional,
    rueckwaertskompatibel) UND von `LabRunner._write_status` frisch-von-der-
    Platte erhalten (kein Droppen -> Doppelbuchungsschutz bleibt)."""
    from mmo_sim.core.admission import record_turn_usage
    from mmo_sim.lab.runner import read_status, LabRunner, LabBudget
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        run_dir.mkdir(parents=True)
        write_test_profile(run_dir, max_turns=100, max_usd=10.0)
        record_turn_usage(run_dir, 0.0, 0.01, require_authority=True, once_request_id="rid-xyz")
        st = read_status(run_dir)  # vor dem Fix: TypeError
        assert st is not None and "rid-xyz" in st.booked_reservation_request_ids, st
        # Legacy-Statusdatei OHNE das Feld bleibt lesbar (Rueckwaertskompat):
        raw = json.loads((run_dir / "lab.status.json").read_text())
        raw.pop("booked_reservation_request_ids", None)
        (run_dir / "lab.status.json").write_text(json.dumps(raw))
        assert read_status(run_dir).booked_reservation_request_ids == []
        # Ein LabRunner-eigener Statuswrite darf die Marke NICHT droppen:
        raw["booked_reservation_request_ids"] = ["rid-keep"]
        (run_dir / "lab.status.json").write_text(json.dumps(raw))
        runner = LabRunner(run_dir, LabBudget(max_turns=100, max_seconds=3600.0, max_usd=10.0))
        runner.start()
        try:
            assert "rid-keep" in read_status(run_dir).booked_reservation_request_ids, (
                "FIX: LabRunner._write_status muss die Retry-Buchungsmarke erhalten"
            )
        finally:
            runner.release()


def test_r4_load_recovery_disposition_is_read_only_no_mkdir():
    """RECOVERY_REVIEW R4 (PR #3317-Nachzug): `load_recovery_disposition` ist
    rein lesend und darf das `recovery_dispositions/`-Verzeichnis NICHT anlegen
    -- frueher erzeugte `_recovery_disposition_path` es via `mkdir` schon beim
    blossen Lesezugriff, obwohl er nur `None` lieferte (verletzte die read-only
    Zusage des Inspect/Plan/Zurueck-Wegs)."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        assert not run_dir.exists()
        result = ledger.load_recovery_disposition(run_dir, "nicht-vorhanden")
        assert result is None
        assert not (run_dir / "recovery_dispositions").exists(), (
            "FIX: load_recovery_disposition darf recovery_dispositions/ nicht anlegen"
        )


def main() -> int:
    tests = [
        test_a_blocked_admission_returns_typed_paused_outcome_no_transport,
        test_a_paused_outcome_is_distinguishable_from_completed,
        test_b_cold_reentry_refuses_unknown_sent_record_no_resend,
        test_c_durable_result_keeps_original_record_id_no_second_transport,
        test_d1_dispose_open_orphan_idempotent_and_rejects_stale_vorzustand,
        test_d2_authorize_bound_retry_is_idempotent_and_survives_simulated_crash,
        test_d3_authorize_bound_retry_rejects_stale_original,
        test_d4_commit_authorized_retry_books_once_no_double_booking,
        test_d5_end_to_end_authorized_retry_consumed_by_real_caller_exactly_once,
        test_d6_commit_authorized_retry_crash_between_booking_and_sent_marker_no_double_booking,
        test_d7_commit_authorized_retry_crash_then_changed_reservation_no_underbooking,
        test_bf1_labstatus_reader_and_writer_preserve_booked_marker,
        test_r4_load_recovery_disposition_is_read_only_no_mkdir,
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
