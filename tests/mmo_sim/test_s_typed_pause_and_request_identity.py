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
    einen zweiten Versand ersetzt -- `request_ledger.begin()` verweigert
    kontrolliert (`OpenReservationExistsError`), der GM-Transport wird dabei
    NIE erreicht, es entsteht KEIN zweiter Requestdatensatz.
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
        raised = None
        try:
            run_admitted_creation_dialog(
                run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=PARTICIPANT,
                turn_idx_start=0, initial_outgoing="SYNTHETIC: Start.",
                gm_transport=gm, get_reply=_unreached_get_reply, harvest_validator=ZeitrissHarvestValidator(),
                role="creation_dialog",
            )
        except ledger.OpenReservationExistsError as e:
            raised = e

        assert raised is not None, (
            "ein kalter JSON-Reentry fuer dieselbe Operationsidentitaet darf einen unbekannten "
            "state=sent-Record NICHT stillschweigend als abgeschlossen/adoptierbar behandeln -- "
            "er muss kontrolliert verweigert werden (OpenReservationExistsError)."
        )
        assert stuck_id in str(raised), raised
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


def main() -> int:
    tests = [
        test_a_blocked_admission_returns_typed_paused_outcome_no_transport,
        test_a_paused_outcome_is_distinguishable_from_completed,
        test_b_cold_reentry_refuses_unknown_sent_record_no_resend,
        test_c_durable_result_keeps_original_record_id_no_second_transport,
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
