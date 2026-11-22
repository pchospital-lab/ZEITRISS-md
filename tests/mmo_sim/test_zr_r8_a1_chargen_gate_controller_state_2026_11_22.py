#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_r8_a1_chargen_gate_controller_state_2026_11_22.py —
ZR-R8-A1 (2026-11-22, ALTAIR-ZR-R8-CHARGEN-GRUPPENABSCHLUSS-FIX §A Teil 1):
deterministischer Controller-Zustandsgate ("kein freier HQ-Zug ohne
gueltigen Erstsave") am ECHTEN Admission-/Uebergangscaller
`ui/tui.py:_resolve_member` (verwendet von `_cmd_local_round`/
`_cmd_lobby_initiative`/Tischbeitritt — KEIN zweiter Code, KEIN Textfilter
auf GM-Freitext).

Rechercheergebnis (dokumentiert hier, damit die Lokalisierung nachvollziehbar
bleibt): im gesamten `mmo_sim`-Paket existiert KEIN Code-Pfad, der
mechanisches Spielgeschehen (Rundenbeitritt, Abschnitts-/HQ-Runtime, Shop,
Mission, XP) ohne `onboarding.status == 'completed'` + `final_save is not
None` zulaesst — die im nativen Befund beobachteten 'Erkunden/Schnell-HQ/
Auto-HQ'-Optionen sind AUSSCHLIESSLICH vom GM generierter Erzaehltext
innerhalb des bestehenden Erschaffungsdialogs (`core/creation_service.py`),
kein Code-Menuepunkt (0 Treffer fuer diese Strings in `mmo_sim/**/*.py`).
`_resolve_member` pruefte das bereits implizit (`final_save is None`); diese
Suite macht den Gate EXPLIZIT benannt (`onboarding.is_regular_creation_save_
committed`), direkt am echten Caller unabhaengig regressionsgesichert, und
beweist zusaetzlich, dass der Inhalt der aufgezeichneten SL-Antworten
('GM bietet freies HQ an') auf das Praedikat KEINEN Einfluss hat (reine
Statuspruefung, kein Parsen von Freitext).

Pure Python, nur `assert`, echter Exitcode. Kein Modellaufruf -- Onboarding-
Zustand wird direkt ueber `domain/zeitriss/onboarding.py` geschrieben."""
from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


def _new_env(root: Path):
    states_dir = root / "states"
    run_dir = root / "run"
    onboarding_dir = root / "onboarding"
    catalog_dir = root / "catalog"
    states_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    return _SCHEMA, states_dir, run_dir, onboarding_dir, catalog_dir


def _session(onboarding_dir, catalog_dir, run_dir, states_dir, schema_path, participant_id="flo_human") -> TuiSession:
    return TuiSession(
        onboarding_dir, catalog_dir, participant_id,
        input_fn=lambda prompt="": (_ for _ in ()).throw(EOFError()),
        print_fn=lambda s: None,
        run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
    )


def test_no_regular_erstsave_blocks_hq_admission_at_real_caller_c1():
    """C1 (02_REGRESSION_UND_ABNAHME.md): Bogen frei (mehrere SL-/Antwort-
    Turns bereits aufgezeichnet, inkl. einem SL-Turn, der woertlich freies
    HQ/Erkunden anbietet UND sogar das erzaehlerische 'Chargen-Save-Gate
    passiert' behauptet), aber KEIN Erstsave committet -- der echte
    Caller `_resolve_member` (verwendet von `_cmd_local_round`/
    `_cmd_lobby_initiative` fuer JEDEN Rundenbeitritt) darf KEINEN
    Uebergang in freien HQ-Spielzug liefern."""
    with tempfile.TemporaryDirectory() as td:
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(Path(td))
        pid = "flo_human"
        onboarding.start_or_resume(onboarding_dir, pid)
        # Bogen "frei"/bestaetigt, aber bewusst noch KEIN `!save` -- exakt
        # der native Befund (Dronov-aehnlich): die SL bietet freies HQ an
        # UND behauptet narrativ ein bereits passiertes Gate. Der Inhalt
        # dieser Zeilen ist fuer den Gate IRRELEVANT (reine Statuspruefung,
        # kein Textparsing) -- s. zweiter Test unten, der das direkt belegt.
        onboarding.record_step(
            onboarding_dir, pid,
            "Chargen-Sequenz abgeschlossen. Bogen: Name, Attribute, Ausruestung vollstaendig.",
            "Danke, mein Bogen ist fertig.",
        )
        onboarding.record_step(
            onboarding_dir, pid,
            "Chargen-Save-Gate passiert. Du stehst vor dem HQ: [1] Erkunden [2] Schnell-HQ "
            "[3] Auto-HQ, oder gib '!save' ein.",
            "Ich erkunde das HQ.",
        )
        state = onboarding.peek(onboarding_dir, pid)
        assert state is not None and state.status == "in_progress" and state.final_save is None, (
            "Vorbedingung C1: Bogen laeuft, KEIN Erstsave -- sonst waere der Test gegenstandslos."
        )

        session = _session(onboarding_dir, catalog_dir, run_dir, states_dir, schema_path, pid)
        result = session._resolve_member(pid)
        assert result is None, (
            f"kein Erstsave committet -- `_resolve_member` (echter Admission-/Uebergangscaller "
            f"fuer Rundenbeitritt/HQ-Spielzug) darf KEINEN freien HQ-Zug freigeben, lieferte "
            f"aber: {result}"
        )

        # Charakterkorrektur/Save-Recovery bleiben erhalten: weitere
        # Erschaffungsschritte (z.B. eine Korrekturrunde) duerfen den
        # Erschaffungsauftrag normal fortsetzen, OHNE dass dieser Gate das
        # blockiert -- der Gate wirkt NUR am Uebergang in die Spielphase.
        onboarding.record_step(
            onboarding_dir, pid, "Welche Ausruestung waehlst du stattdessen?", "Leichte Ruestung, Pistole.",
        )
        assert onboarding.peek(onboarding_dir, pid).status == "in_progress", (
            "Charakterkorrektur/Fortsetzung des Erschaffungsdialogs muss unabhaengig vom "
            "HQ-Admission-Gate weiter moeglich bleiben."
        )
        assert session._resolve_member(pid) is None, (
            "weiterhin kein Erstsave committet -- Gate muss nach einer weiteren Korrekturrunde "
            "unveraendert ablehnen."
        )


def test_regular_erstsave_commit_unlocks_same_caller():
    """Gegenstueck: SOBALD ein gueltiger regulaerer Erstsave committet ist
    (`onboarding.complete_with_save`, derselbe Weg wie am Ende eines echten
    Erschaffungsdialogs), liefert GENAU DERSELBE Caller (`_resolve_member`)
    einen echten Treffer -- der Gate blockiert NICHT dauerhaft, nur bis zum
    regulaeren Abschluss."""
    with tempfile.TemporaryDirectory() as td:
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(Path(td))
        pid = "flo_human"
        char_id = "chrono-zr-r8-a1"
        onboarding.start_or_resume(onboarding_dir, pid)
        save = full_v7_save(char_id, name="A1-Fixture", level=1, save_id="SAVE-ZR-R8-A1")
        onboarding.complete_with_save(onboarding_dir, pid, save, ZeitrissHarvestValidator(), char_id)

        session = _session(onboarding_dir, catalog_dir, run_dir, states_dir, schema_path, pid)
        result = session._resolve_member(pid)
        assert result is not None, "ein committeter regulaerer Erstsave muss den echten Caller freigeben."
        active_save, resolved_char_id = result
        assert resolved_char_id == char_id
        assert active_save.get("characters", [{}])[0].get("id") == char_id


def test_predicate_is_pure_status_check_text_content_irrelevant():
    """Direkter Unit-Beleg fuer `onboarding.is_regular_creation_save_
    committed`: identischer `OnboardingState` mit UNTERSCHIEDLICHEN
    `steps`-Inhalten (einmal neutral, einmal mit woertlichem 'Gate
    passiert'-Erzaehltext) liefert IDENTISCHES Praedikatsergebnis -- der
    Gate liest/bewertet den Text nicht."""
    import dataclasses

    base = onboarding.OnboardingState(participant_id="x", status="in_progress")
    neutral = dataclasses.replace(base, steps=[{"sl": "Welche Attribute waehlst du?", "answer": "Stark."}])
    narrated_gate = dataclasses.replace(base, steps=[{
        "sl": "Chargen-Save-Gate passiert. Freies HQ steht offen.", "answer": "Ich gehe ins HQ.",
    }])
    assert onboarding.is_regular_creation_save_committed(neutral) is False
    assert onboarding.is_regular_creation_save_committed(narrated_gate) is False
    assert onboarding.is_regular_creation_save_committed(neutral) == onboarding.is_regular_creation_save_committed(
        narrated_gate
    ), "GM-Freitext in `steps` darf das Praedikat nicht unterschiedlich ausfallen lassen."

    completed = dataclasses.replace(narrated_gate, status="completed", final_save={"v": 7})
    assert onboarding.is_regular_creation_save_committed(completed) is True
    assert onboarding.is_regular_creation_save_committed(None) is False


def main() -> int:
    tests = [
        test_no_regular_erstsave_blocks_hq_admission_at_real_caller_c1,
        test_regular_erstsave_commit_unlocks_same_caller,
        test_predicate_is_pure_status_check_text_content_irrelevant,
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
