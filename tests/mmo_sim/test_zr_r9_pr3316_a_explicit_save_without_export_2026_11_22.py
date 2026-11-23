#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_r9_pr3316_a_explicit_save_without_export_2026_11_22.py —
ZR-R9-PR3316-PREMERGE-NACHZUG-20261122, Befund A (01_REVIEW.txt Abschnitt
5, CREATION-REVIEW.md): `core/creation_service.py:run_admitted_creation_
dialog` nutzt das neue Admission-Prädikat (`onboarding.is_regular_
creation_save_committed`) NICHT -- nach Auswahl `1` UND nach einem exakten
`!save`-Kommando liefert die SL weiterhin keinen Save-Export (HQ-Einkaufs-
prosa statt Charakterbogen); der Dialog leitete das bisher unverändert als
gewöhnlichen nächsten Dialogzug an die SL weiter (`get_reply`/GM-Call),
Onboarding blieb `in_progress` -- belegt durch `trace_creation_loop.py`s
`EXPLICIT-SAVE-TRACE.json` im Supportpaket (gegen die gepinnte Head-Kopie,
nicht gegen diesen Nachzug).

Nachzug: der bereits bestehende ausdrückliche `!save`/`!speichern`-
Abschlusswunsch (`domain.zeitriss.policy.is_save_command`, derselbe
Vertrag wie `core.runtime`s `explicit_completion_attempt`) wird jetzt im
tatsächlichen Caller gebunden -- bezieht sich auf `outgoing` (den gerade
gesendeten Text), NICHT auf die Antwort. Liefert die SL darauf KEINEN
extrahierbaren Save-Block, hält der Dialog kontrolliert (`status="paused",
reason="explicit_save_without_export"`), OHNE `record_step`/`turn_idx`
voranzurücken -- NICHT zurück in die freie Story-/Persona-Schleife.
Enthält bewusst KEINE automatische Charakterfertigstellung, KEINE
Zahlenwahl als verstecktes `!save`, KEINEN HQ-Wortfilter, KEINE künstliche
Turngrenze und KEINEN neu erfundenen strukturierten "Bogen fertig"-Zustand
-- ein ganz fehlender Rohblock hat keine Chrononaut-ID, an die eine
Korrekturanfrage (`_attempt_correction`) gebunden werden könnte; die
bestehende G02/SC06-Korrekturbehandlung für MEHRDEUTIGE (aber vorhandene)
Rohblöcke bleibt davon unberührt.

A1 (Admission-Test) und A2 (Prompt-Test) bleiben GENAU das -- dieser Test
ist A1/A2 NICHT: er belegt die TECHNISCHE Abschlussgarantie am echten
Controller-Caller, NICHT native Modellbefolgung (kein echter Modellaufruf,
gescriptetes Fake-SL/-Persona, exakt wie `trace_creation_loop.py`s eigene
Scope-Einschränkung).

Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import mmo_sim.core.creation_service as creation_service  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402


class _ScriptedCreationGm:
    """Wirft bei jedem UEBERZAEHLIGEN Call -- der direkte Beleg, dass nach
    dem Hold kein dritter GM-Turn (die Shopping-Antwort) je gesendet wird."""

    def __init__(self, contents: list[str]):
        self._contents = list(contents)
        self.calls: list[tuple[int, str]] = []

    def turn(self, idx, text, **kwargs):
        self.calls.append((idx, text))
        if not self._contents:
            raise AssertionError(
                f"A-NACHZUG: kein weiterer GM-Call nach explizitem !save ohne Export erwartet "
                f"(turn_idx={idx})."
            )
        content = self._contents.pop(0)
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "creation"}


def test_a_explicit_save_without_export_holds_instead_of_free_loop():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        onboarding_dir = root / "onboarding"
        run_dir.mkdir(parents=True)
        write_test_profile(run_dir)
        onboarding.start_or_resume(onboarding_dir, "dronov_like")

        get_reply_calls: list[tuple[int, str]] = []

        def get_reply(turn_idx: int, sl_text: str) -> creation_service.ReplyResult:
            get_reply_calls.append((turn_idx, sl_text))
            if len(get_reply_calls) > 1:
                raise AssertionError(
                    "A-NACHZUG: get_reply sollte nach dem expliziten !save-Hold nicht erneut "
                    "nach einer weiteren Persona-/Spielerantwort fragen."
                )
            return creation_service.ReplyResult(kind="answer", text="!save")

        # Dronov-aehnlicher Trace (CREATION-REVIEW.md): Turn 0 bietet nach
        # abgeschlossener Chargen HQ an und endet mit der Erwaehnung von
        # `!save`; Turn 1 (die Antwort auf das gesendete `!save`) liefert
        # STATT eines Exports HQ-Einkaufsprosa -- GENAU der belegte Fall.
        gm = _ScriptedCreationGm([
            "Chargen-Sequenz abgeschlossen. [1] Erkunden [2] Schnell-HQ [3] Auto-HQ; !save.",
            "Du erkundest das HQ. Der Shop bietet neue Ausruestung an. Was kaufst du?",
        ])

        outcome = creation_service.run_admitted_creation_dialog(
            run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id="dronov_like",
            turn_idx_start=0, initial_outgoing="Mein Charakterbogen ist fertig.",
            gm_transport=gm, get_reply=get_reply, harvest_validator=ZeitrissHarvestValidator(),
        )

        # DAS ist der eigentliche Beleg: kontrollierter Hold statt
        # Weiterleitung in einen weiteren freien Dialogzug.
        assert outcome.status == "paused", outcome
        assert outcome.reason == "explicit_save_without_export", outcome.reason
        assert len(gm.calls) == 2, (
            f"GENAU zwei GM-Calls (Chargen-Angebot + Antwort auf !save) -- kein dritter "
            f"Shopping-Turn -- {gm.calls}"
        )
        assert len(get_reply_calls) == 1, (
            f"get_reply darf nach dem Hold NICHT erneut nach einer Antwort fragen -- {get_reply_calls}"
        )

        state = onboarding.peek(onboarding_dir, "dronov_like")
        assert state is not None and state.status == "in_progress" and state.final_save is None, state

        # Wiederaufnahme (frischer Aufruf, identische Operationsidentitaet
        # ueber denselben `turn_idx_start`/`initial_outgoing`, exakt wie ein
        # echter Prozessneustart `state.steps[-1]["answer"]` wiederverwendet,
        # s. `ui/tui.py:_cmd_new_or_switch_character`): trifft DIESELBE
        # Entscheidung erneut, OHNE den bereits durabel verbuchten `!save`-
        # Turn erneut an die SL zu senden (`request_ledger`s Idempotenz).
        gm_resume = _ScriptedCreationGm([])  # wirft bei JEDEM Call -- 0 neue Transport-Calls erwartet.

        def get_reply_resume(turn_idx: int, sl_text: str) -> creation_service.ReplyResult:
            raise AssertionError("A-NACHZUG: Wiederaufnahme darf KEINE neue Persona-/Spielerantwort erfragen.")

        outcome_resume = creation_service.run_admitted_creation_dialog(
            run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id="dronov_like",
            turn_idx_start=1, initial_outgoing="!save",
            gm_transport=gm_resume, get_reply=get_reply_resume, harvest_validator=ZeitrissHarvestValidator(),
        )
        assert outcome_resume.status == "paused" and outcome_resume.reason == "explicit_save_without_export", (
            outcome_resume
        )
        assert gm_resume.calls == [], (
            f"Wiederaufnahme muss die bereits durabel verbuchte Antwort wiederverwenden, kein "
            f"zweiter realer Transport-Call -- {gm_resume.calls}"
        )


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
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
