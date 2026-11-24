#!/usr/bin/env python3
"""
tests/mmo_sim/test_restnachzug_rk_20261124_r1.py — ergaenzende R4/R5-Abnahme
(RECOVERY_REVIEW.md R4 "drei bestellte Caller verbrauchen keine Freigabe",
R5 "vollstaendige Grantbindung vor Nutzung", PR-#3317-Restnachzug
2026-11-24).

Deckt die engen Gegenfaelle, die in den fuenf bereits bestehenden R/K-
Testdateien (test_rec1/test_rec2/test_recovery_ops_r1/test_n06r/
test_s_typed_pause_and_request_identity) nicht passten, weil sie konkrete
Caller in anderen Modulen (`domain.zeitriss.community_creation`,
`core.save_correction`, `core.compat_load_service`) bzw. die neue R5-
Grantbindung in `core.request_ledger` direkt ansprechen -- eigenstaendige
Datei (analog test_rec1s Docstring: "eigene, kleine Kopie statt
Cross-Test-Import"), kein Mock AUF den geprueften Pfaden, nur Fake-Treiber/
-Transporte an der aeussersten Grenze.

Pure Python, `unittest.TestCase` (Lauf: `python3 -m unittest tests.mmo_sim.
test_restnachzug_rk_20261124_r1 -v`)."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import mmo_sim.core.compat_load_service as compat_load_service  # noqa: E402
import mmo_sim.core.request_ledger as request_ledger  # noqa: E402
import mmo_sim.core.save_correction as save_correction  # noqa: E402
from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.request_ledger import StaleDispositionError  # noqa: E402
from mmo_sim.domain.zeitriss.community_creation import _persona_get_reply_factory  # noqa: E402


class _FakePersonaDriver:
    """Minimaler Fake fuer `_persona_get_reply_factory`s `persona_driver` --
    kein `.config` (duck-typed, behandelt wie ein unbeschraenkter Treiber,
    s. `admission.reservation_for_request`-Docstring)."""

    def __init__(self, decisions):
        self._decisions = list(decisions)
        self.calls = 0

    def decide(self, ctx):
        self.calls += 1
        if not self._decisions:
            raise RuntimeError("_FakePersonaDriver: Skript erschoepft")
        return self._decisions.pop(0)


class _FakeGmTransport:
    def __init__(self, contents):
        self._contents = list(contents)
        self.calls = []
        # Q07 (admission.reservation_for_request/read_admission_block): ein
        # Treiber MIT erkennbarem `.config`-/Limit-Attribut gilt als
        # beschraenkt -- ohne dieses Attribut lehnt das fail-closed-Gate bei
        # hartem `max_usd` JEDE Anfrage ab, BEVOR der Orphan-Dreischritt
        # ueberhaupt erreicht wird. Reiner Testfixture-Bedarf, kein Teil des
        # geprueften Verhaltens.
        self.output_limit_tokens = 400

    def turn(self, turn_idx, text, output_limit_tokens=None):
        self.calls.append({"turn_idx": turn_idx, "text": text})
        content = self._contents.pop(0) if self._contents else "SL-Antwort."
        return {"content": content, "usage": {}}


class _ExplodingGmTransport:
    def __init__(self):
        self.output_limit_tokens = 400

    def turn(self, turn_idx, text, output_limit_tokens=None):
        raise AssertionError("kein Transportversuch fuer ein ungeklaertes Unknown erwartet.")


COMMUNITY_ID = "community-restnachzug"
GENERATION = 1
PERSONA_KEY = "flo-persona"
SECTION_ID = f"gen{GENERATION}"
PERSONA_ROLE = "community_creation_persona"


class _R4Base(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        root = Path(self._td.name)
        self.run_dir = root / "run"
        self.onboarding_dir = root / "onboarding"
        write_test_profile(self.run_dir, max_turns=10, max_usd=10.0)

    def tearDown(self):
        self._td.cleanup()

    def _make_unauthorized_orphan(self, *, role, turn_idx, participant, table_id=None, section_id=SECTION_ID):
        return request_ledger.begin(
            self.run_dir, role=role, content=f"wire-{role}-{turn_idx}", reserved_usd=0.01,
            table_id=table_id, section_id=section_id, turn_idx=turn_idx, participant=participant,
            dollar_billed=True,
        )

    def _make_authorized_follower(self, *, role, turn_idx, participant, table_id=None, section_id=SECTION_ID):
        original_id = request_ledger.begin(
            self.run_dir, role=role, content=f"wire-{role}-{turn_idx}", reserved_usd=0.01,
            table_id=table_id, section_id=section_id, turn_idx=turn_idx, participant=participant,
            dollar_billed=True,
        )
        request_ledger.dispose_open_orphan(self.run_dir, original_id, reason="R4-Restnachzug-Test")
        return request_ledger.authorize_bound_retry(self.run_dir, original_id)


class TestR4CommunityPersonaGetReply(_R4Base):
    """RECOVERY_REVIEW R4: Community-Persona `_get_reply` ging bisher
    direkt in `request_ledger.begin()` -- ein echtes Unknown liess dessen
    eigene Dedup-Pruefung `OpenReservationExistsError` UNBEHANDELT werfen
    (crasht den Aufrufer), ein autorisierter Folger wurde NIE konsumiert."""

    def _factory(self, driver):
        return _persona_get_reply_factory(
            run_dir=self.run_dir, persona_driver=driver, community_id=COMMUNITY_ID,
            generation=GENERATION, persona_key=PERSONA_KEY, draft_state={},
            onboarding_dir=self.onboarding_dir, print_fn=lambda s: None,
        )

    def test_unknown_without_authorization_pauses_zero_model_calls(self):
        self._make_unauthorized_orphan(role=PERSONA_ROLE, turn_idx=0, participant=PERSONA_KEY, table_id=COMMUNITY_ID)
        driver = _FakePersonaDriver([ParticipantDecision(text="sollte nie aufgerufen werden.")])
        get_reply = self._factory(driver)

        result = get_reply(0, "SL-Frage.")

        self.assertEqual(result.kind, "paused")
        self.assertEqual(driver.calls, 0, "R4-FIX: kein Modellaufruf ohne bewusste Recovery-Entscheidung")

    def test_authorized_follower_consumed_exactly_once(self):
        retry_id = self._make_authorized_follower(role=PERSONA_ROLE, turn_idx=0, participant=PERSONA_KEY, table_id=COMMUNITY_ID)
        driver = _FakePersonaDriver([ParticipantDecision(text="Persona-Antwort.", origin_source="fake:persona")])
        get_reply = self._factory(driver)

        result = get_reply(0, "SL-Frage.")

        self.assertEqual(result.kind, "answer")
        self.assertEqual(result.text, "Persona-Antwort.")
        self.assertEqual(driver.calls, 1, "R4-FIX: der autorisierte Folger wurde tatsaechlich real befragt")
        self.assertEqual(request_ledger.load_request(self.run_dir, retry_id)["state"], "accounted")


class TestR4SaveCorrectionSendCorrectionTurn(_R4Base):
    """RECOVERY_REVIEW R4: `save_correction.send_correction_turn` fing den
    `OpenReservationExistsError` bisher pauschal als `unclear_sent_in_flight`
    ab -- sicher kein Zweitversand, aber ein ausdruecklich freigegebener
    Folger wurde NIE verbraucht."""

    def test_unknown_without_authorization_blocked_zero_transport_calls(self):
        self._make_unauthorized_orphan(role="save_correction_single", turn_idx=0, participant=PERSONA_KEY)
        gm = _ExplodingGmTransport()

        outcome = save_correction.send_correction_turn(
            self.run_dir, role="save_correction_single", table_id=None, section_id=SECTION_ID,
            participant=PERSONA_KEY, turn_idx=0, outgoing_text="Korrektur-Text.", gm_transport=gm,
        )

        self.assertTrue(outcome.blocked)
        self.assertTrue(outcome.reason.startswith("unclear_sent_in_flight"), outcome.reason)

    def test_authorized_follower_consumed_exactly_once(self):
        retry_id = self._make_authorized_follower(role="save_correction_single", turn_idx=0, participant=PERSONA_KEY)
        gm = _FakeGmTransport(contents=["SL-Korrekturantwort."])

        outcome = save_correction.send_correction_turn(
            self.run_dir, role="save_correction_single", table_id=None, section_id=SECTION_ID,
            participant=PERSONA_KEY, turn_idx=0, outgoing_text="Korrektur-Text (frisch).", gm_transport=gm,
        )

        self.assertFalse(outcome.blocked, outcome.reason)
        self.assertEqual(outcome.text, "SL-Korrekturantwort.")
        self.assertEqual(len(gm.calls), 1, "R4-FIX: der autorisierte Folger erreicht den Transport genau einmal")
        self.assertEqual(request_ledger.load_request(self.run_dir, retry_id)["state"], "accounted")


class TestR4CompatLoadService(_R4Base):
    """RECOVERY_REVIEW R4: Kompatibilitaets-Load ging bisher direkt in
    `request_ledger.begin()` -- derselbe Fehler fuehrte nur zu `None`
    (kontrolliertes HOLD), der freigegebene Folger wurde ebenfalls nicht
    verwendet."""

    def test_unknown_without_authorization_returns_none_zero_transport_calls(self):
        self._make_unauthorized_orphan(
            role=compat_load_service.ROLE_COMPAT_LOAD, turn_idx=1, participant=PERSONA_KEY,
        )
        gm = _ExplodingGmTransport()

        result = compat_load_service._sl_backed_repair(
            self.run_dir, repair_key="repair-1", char_id="chrono-1", participant_id=PERSONA_KEY,
            gm_transport=gm, table_id=None, section_id=SECTION_ID,
            role=compat_load_service.ROLE_COMPAT_LOAD, max_attempts=3,
            candidate={"id": "chrono-1"}, open_issues=["irgendein Strukturfehler"],
        )

        self.assertIsNone(result, "R4: echtes Unknown bleibt kontrolliertes HOLD (None)")

    def test_authorized_follower_consumed_exactly_once(self):
        retry_id = self._make_authorized_follower(
            role=compat_load_service.ROLE_COMPAT_LOAD, turn_idx=1, participant=PERSONA_KEY,
        )
        gm = _FakeGmTransport(contents=['```json\n{"id": "chrono-1", "fixed": true}\n```'])

        result = compat_load_service._sl_backed_repair(
            self.run_dir, repair_key="repair-1", char_id="chrono-1", participant_id=PERSONA_KEY,
            gm_transport=gm, table_id=None, section_id=SECTION_ID,
            role=compat_load_service.ROLE_COMPAT_LOAD, max_attempts=3,
            candidate={"id": "chrono-1"}, open_issues=["irgendein Strukturfehler"],
        )

        # R4 prueft, dass der autorisierte Folger den Transport ERREICHT und
        # abgerechnet wird -- OB der synthetische Antworttext als gueltiger
        # v7-Save extrahierbar ist, ist eine unabhaengige, hier nicht
        # geprüfte Validierungsfrage (`result` darf deshalb `None` sein).
        self.assertEqual(len(gm.calls), 1, "R4-FIX: der autorisierte Folger erreicht jetzt den Transport")
        self.assertEqual(request_ledger.load_request(self.run_dir, retry_id)["state"], "accounted")


class TestR5GrantBindingDriftBeforeConsumption(unittest.TestCase):
    """RECOVERY_REVIEW R5/§6 ("vollstaendige Grantbindung vor Nutzung"):
    `commit_authorized_retry` prueft jetzt -- unmittelbar VOR Verbrauch --
    zusaetzlich die bei `dispose_open_orphan` gebundene Operationsidentitaet,
    den vollen Original-Dateihash UND die Run-Bindung (`bound_run_id`) gegen
    den aktuellen Stand. Ein truthy `recovery_of` + passendes
    `granted_request_id` alleine darf NICHT mehr genuegen."""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.run_dir = Path(self._td.name) / "run"
        write_test_profile(self.run_dir, max_turns=10, max_usd=10.0)

    def tearDown(self):
        self._td.cleanup()

    def _make_granted_follower(self):
        original_id = request_ledger.begin(
            self.run_dir, role="persona_decision", content="original-wire-text", reserved_usd=0.01,
            table_id="t-r5", section_id="sec-r5", turn_idx=0, participant="vanguard", dollar_billed=True,
        )
        request_ledger.dispose_open_orphan(self.run_dir, original_id, reason="R5-Grantbindung-Test")
        new_id = request_ledger.authorize_bound_retry(self.run_dir, original_id)
        return original_id, new_id

    def test_bound_run_id_drift_after_dispose_rejected(self):
        """Dispose mit einer bereits vorhandenen `run_id.json` (echte
        Bindung, `bound_run_id` gesetzt) -- vor dem Verbrauch wird
        `run_id.json` auf eine ANDERE Run-Identitaet geaendert (z.B. ein
        Restore/eine Kopie desselben Pfades aus einem anderen Lauf).
        `commit_authorized_retry` muss das als Drift erkennen, TYPISIERT
        abbrechen und NICHTS buchen/versenden."""
        (self.run_dir / "run_id.json").write_text('{"run_id": "run-A"}', encoding="utf-8")
        original_id, new_id = self._make_granted_follower()
        disposition = request_ledger.load_recovery_disposition(self.run_dir, original_id)
        self.assertEqual(disposition.get("bound_run_id"), "run-A")

        status_before = request_ledger.load_request(self.run_dir, new_id)
        status_before_usd = self._usd_spent()

        (self.run_dir / "run_id.json").write_text('{"run_id": "run-B-FREMD"}', encoding="utf-8")

        with self.assertRaises(StaleDispositionError):
            request_ledger.commit_authorized_retry(
                self.run_dir, new_id, content="neuer Versand", reserved_usd=0.02,
            )

        status_after = request_ledger.load_request(self.run_dir, new_id)
        self.assertEqual(status_after, status_before, "R5-FIX: kein Schreibzugriff bei Run-Bindungsdrift")
        self.assertEqual(self._usd_spent(), status_before_usd, "R5-FIX: keine Buchung bei Run-Bindungsdrift")

    def test_original_identity_drift_rejected(self):
        """Die bei der Disposition gebundene Operationsidentitaet muss noch
        zum AKTUELLEN Originalrecord passen -- eine (hier synthetisch
        herbeigefuehrte) Abweichung der Original-Identitaetsfelder NACH der
        Disposition wird jetzt erkannt, statt sie zu ignorieren."""
        original_id, new_id = self._make_granted_follower()
        original_record = request_ledger.load_request(self.run_dir, original_id)
        tampered = dict(original_record)
        tampered["participant"] = "FREMDE-IDENTITAET"
        request_ledger._write_request(self.run_dir, original_id, tampered)

        with self.assertRaises(StaleDispositionError):
            request_ledger.commit_authorized_retry(
                self.run_dir, new_id, content="neuer Versand", reserved_usd=0.02,
            )

    def _usd_spent(self):
        import json
        return json.loads((self.run_dir / "lab.status.json").read_text())["usd_spent"]


if __name__ == "__main__":
    unittest.main()
