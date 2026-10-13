#!/usr/bin/env python3
"""
tests/mmo_sim/test_w54_g03_error_redaction_2026_10_08.py -- R12-Savegate,
W54-Slice, G03 (FINDINGS.json/01_ENTSCHEIDUNG_UND_REPARATUR.md §W54 G03,
SC15/SC17).

Befund (General, GENERALREVIEW.md §5, eigene Gegenprobe): nach einer
ungueltigen ersten SL-Antwort wirft die Fake-Korrekturanfrage
`RuntimeError('SYNTHETIC_SECRET_GENERAL_CORRECTION_ONLY')`. Der echte
Dienst blieb zwar korrekt `paused`/`in_progress` OHNE Saveuebernahme,
druckte aber `Grund: transport_error:SYNTHETIC_SECRET_GENERAL_CORRECTION_
ONLY.` roh ins Terminal. Quelle: `core.save_correction.send_correction_
turn` baut `transport_error:{exc}`; `core.creation_service` reichte
`correction.reason` roh an `print_fn` weiter -- derselbe rohe Text erreicht
unredigiert auch den Gruppenpfad (`core.runtime._group_correction_status_
emit`'s `self._status_fn(... payload.get('reason') ...)`).

W54-Fix (`domain/zeitriss/save_correction.py` NEU: `public_hold_reason`;
`core/save_correction.py` NEU: Re-Export; `core/creation_service.py` +
`core/runtime.py`): NUR eine feste, oeffentliche Kategorie erreicht
`print_fn`/`self._status_fn` -- NIE der rohe Text hinter einem Praefix
(kann `str(exc)` einer Fremdantwort/Transportausnahme sein). Der volle
Rohgrund bleibt NUR im geschuetzten Korrekturdatensatz (`save_corrections/
<repair_key>.json`s `last_reason`-Feld) erhalten. Ein tatsaechlich
VERSUCHTER, aber unklar beantworteter Korrekturversuch bleibt wahrheitsgemaess
als 'versucht/HOLD' erkennbar -- NIE als 'kein Modellaufruf' (01_
AUFTRAG_SAVEGATE.md §E).

Abdeckung:
  W54-G03-A -- `public_hold_reason` klassifiziert bekannte Praefixe
               (`transport_error:`, `unclear_sent_in_flight:`,
               `admission_blocked:`, `altformat_unresolved_*`) OHNE
               jemals den Rohtext durchzulassen; bereits sichere Gruende
               bleiben unveraendert; Unbekanntes/Fehlendes wird NIE roh
               durchgelassen.
  W54-G03-B -- Echter End-to-End-Durchlauf ueber den Produktweg
               (`run_admitted_creation_dialog`, identisches
               Reproduktionsmuster zu `refs/probe_savegate.py` mode
               'error_redaction'): der synthetische Transport-Fehlermarker
               erreicht NIE eine `print_fn`-Zeile; der geschuetzte
               Korrekturdatensatz behaelt den vollen Rohgrund; der
               Fehlversuch bleibt als tatsaechlich VERSUCHT erkennbar
               (kein 'kein Modellaufruf').
  W54-G03-C -- Gruppenpfad (`core.runtime._group_correction_status_emit`):
               derselbe synthetische Marker erreicht NIE `self._status_fn`.

Pure Python, nur `assert`, echter Exitcode. Kein Netz, kein Livecall."""
from __future__ import annotations

import json
import sys
import tempfile
import traceback
import types
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402 (Fixturehelper, FIXTURE_ONLY)

import mmo_sim.core.runtime as runtime  # noqa: E402
import mmo_sim.core.save_correction as save_correction  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.creation_service import run_admitted_creation_dialog  # noqa: E402
import mmo_sim.domain.zeitriss.onboarding as onboarding  # noqa: E402
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402

_MARKER = "SYNTHETIC_SECRET_W54_G03_CORRECTION_ONLY"


def fenced(block: dict) -> str:
    return "```json\n" + json.dumps(block) + "\n```"


def _no_persona_poll(*_a, **_k):
    raise AssertionError("W54-G03: kein Personapoll im menschlichen Erschaffungsdialog erwartet.")


# ---------------------------------------------------------------------------
# W54-G03-A -- `public_hold_reason` Klassifikationsvertrag (Unit-Ebene).
# ---------------------------------------------------------------------------

def test_w54g03a_public_hold_reason_never_leaks_raw_text():
    raw = f"transport_error:RuntimeError('{_MARKER}')"
    category = save_correction.public_hold_reason(raw)
    assert _MARKER not in category, category
    assert category == "transport_error_after_attempt"
    # Re-Export core<->domain liefert dieselbe Kategorie.
    assert save_correction_domain.public_hold_reason(raw) == category

    assert save_correction.public_hold_reason(f"unclear_sent_in_flight:{_MARKER}") == "unclear_prior_attempt_in_flight"
    assert _MARKER not in save_correction.public_hold_reason(f"unclear_sent_in_flight:{_MARKER}")
    assert save_correction.public_hold_reason(f"admission_blocked:{_MARKER}") == "budget_or_admission_hold"
    assert save_correction.public_hold_reason(f"altformat_unresolved_received_seconds") == "unresolved_prior_result_hold"

    # Bereits sichere Gruende (keine Fremddaten) bleiben unveraendert.
    assert save_correction.public_hold_reason("attempt_budget_exhausted") == "attempt_budget_exhausted"
    assert save_correction.public_hold_reason("unjustified_semantic_drift") == "unjustified_semantic_drift"

    # Unbekannt/fehlend wird NIE roh durchgelassen.
    assert save_correction.public_hold_reason(_MARKER) == "unclear_hold"
    assert save_correction.public_hold_reason(None) == "unclear"
    assert save_correction.public_hold_reason("") == "unclear"


# ---------------------------------------------------------------------------
# W54-G03-B -- Echter End-to-End-Durchlauf, Einzelfigur-Erschaffungsdialog.
# ---------------------------------------------------------------------------

class _FailingCorrectionGm:
    """Erste Antwort (ungueltiger Entwurf) regulaer; JEDER weitere Call
    (die Korrekturanfrage) wirft einen synthetischen Transportfehler --
    identisches Muster zu `refs/probe_savegate.py` mode 'error_redaction'."""

    def __init__(self, first_response: str):
        self._first = first_response
        self.calls: list[tuple[int, str]] = []

    def turn(self, turn_idx, text, **kwargs):
        self.calls.append((turn_idx, text))
        if len(self.calls) == 1:
            return {"content": self._first, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}
        raise RuntimeError(_MARKER)


def test_w54g03b_transport_exception_marker_never_reaches_print_fn():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, onboarding_dir = root / "run", root / "onboarding"
        write_test_profile(run_dir)
        who = "testspieler_w54g03b"
        cid = "CHR-W54-G03B-01"

        invalid = full_v7_save(cid, name="Flo")
        invalid["economy"] = {"wallets": {cid: 500}}  # schema-ungueltig -- loest Korrektur aus

        onboarding.start_or_resume(onboarding_dir, who)
        gm = _FailingCorrectionGm(fenced(invalid))
        printed: list[str] = []

        outcome = run_admitted_creation_dialog(
            run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=who,
            turn_idx_start=0, initial_outgoing="Erschaffung starten.", gm_transport=gm,
            get_reply=_no_persona_poll, harvest_validator=ZeitrissHarvestValidator(),
            print_fn=printed.append,
        )

        assert len(gm.calls) == 2, "Erstantwort + genau 1 versuchter Korrekturcall."
        assert outcome.status == "paused"
        assert "transport_error:" in outcome.reason and _MARKER in outcome.reason, (
            "intern (NICHT fuer die Anzeige) bleibt der volle Rohgrund am Outcome erhalten -- "
            "nur die TERMINALAUSGABE wird redigiert, s. unten."
        )

        joined = "\n".join(printed)
        assert _MARKER not in joined, f"SC15/SC17: der synthetische Marker darf NIE im Terminal erscheinen -- {printed!r}"
        assert "RuntimeError" not in joined, printed
        assert "kein Modellaufruf" not in joined, (
            "SC15/SC17: ein TATSAECHLICH versuchter Korrekturcall darf NIE als 'kein Modellaufruf' "
            f"dargestellt werden -- {printed!r}"
        )
        assert any("transport_error_after_attempt" in line for line in printed), (
            f"die klassifizierte oeffentliche Kategorie MUSS sichtbar sein -- {printed!r}"
        )

        # Geschuetzter Diagnosebeleg (NICHT die Spieleranzeige) behaelt den
        # vollen Rohgrund -- fuer Support/Debugging, s. Modulkommentar.
        repair_key = save_correction_domain.creation_repair_key(who, cid)
        record = save_correction.load_record(run_dir, repair_key)
        assert record["state"] == "hold"
        assert _MARKER in record["last_reason"], (
            "der geschuetzte Korrekturdatensatz darf den vollen Diagnosebeleg weiterhin tragen."
        )

        state = onboarding.peek(onboarding_dir, who)
        assert state.status == "in_progress" and state.final_save is None, (
            "ein Fehlversuch darf NIE einen ungueltigen/unklaren Stand als gespeichert ausweisen."
        )


# ---------------------------------------------------------------------------
# W54-G03-C -- Gruppenpfad-Statuskanal (`core.runtime._group_correction_
# status_emit`).
# ---------------------------------------------------------------------------

def test_w54g03c_group_status_channel_never_leaks_raw_transport_reason():
    printed: list[str] = []
    fake_self = types.SimpleNamespace(_status_fn=printed.append)

    runtime.SectionRuntime._group_correction_status_emit(
        fake_self, "save_correction_hold",
        {"section_id": "s1", "table_id": "t1", "persona_key": "guest_pk", "reason": f"transport_error:{_MARKER}"},
    )

    joined = "\n".join(printed)
    assert _MARKER not in joined, f"SC15/SC17: der Gruppenpfad darf den rohen Transportgrund NIE anzeigen -- {printed!r}"
    assert any("transport_error_after_attempt" in line for line in printed), printed
    assert any("guest_pk" in line for line in printed), "die betroffene Person bleibt weiterhin benannt."


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
