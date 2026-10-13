#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_q07_resume_open_creation_2026_10_05.py — Q07
(REVIEW.md R03, 05.10.2026, ZEITRISS Terminal UX-1, W12-Nacharbeit).

Negative Altprobe (dokumentiert, nicht erneut ausgefuehrt): vor dieser
Aenderung gab `_cmd_menu_fortsetzen()` bei einer real offenen, bereits
begonnenen Erschaffung (`card.pending_creation is True`, `card.
chrononaut_id is None`) NUR einen Wegweiser-Text aus ("bitte ueber
'[n]'/[charaktere] fortsetzen") -- kein Erschaffungszug folgte, der
Fake-GM-Zaehler blieb 0 (s. REVIEW.md Q07, `evidence/guarded_counterprobes/
Q07_CREATION_CONTINUE_SIGNPOST_ONLY` im Review-Paket).

Positive Regression (dieser Test): Anzeige UND Ausfuehrung nutzen jetzt
denselben Zustandsentscheid (`card.pending_creation`); der Dispatch bindet
TATSAECHLICH an den vorhandenen Verlauf (bereits aufgezeichneter
Zwischenschritt wird als naechste SL-Nachricht wiederverwendet, kein
Neustart) und ein echter Erschaffungszug (realer Fake-GM-Call) folgt --
bis zum Abschluss, wenn die SL-Antwort bereits einen gueltigen v7-Save
enthaelt.

Pure Python, nur `assert`, synthetische Daten/Temp-Dirs, kein Netzwerk-/
externer Providercall."""
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
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _full_v7_fixture import upgrade_narrow_save  # noqa: E402

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_FIX = _REPO_ROOT / "internal" / "qa" / "harness" / "lobby" / "fixtures" / "saves"
_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


def _eof_input(prompt: str = "") -> str:
    raise EOFError()


class _FakeGm:
    """Scriptetes GM-Fake: liefert SOFORT im ersten Call den gueltigen
    v7-Save-Block -- ein einziger echter Erschaffungszug reicht bis zum
    Abschluss (deckt den Fortsetzungsfall ohne zusaetzliche Zwischenfrage,
    der eigentliche Mehrfragen-Dialog ist bereits in `test_m3_tui.py`
    abgedeckt)."""

    def __init__(self, save_block: dict):
        self.save_block = save_block
        self.calls: list[tuple[int, str]] = []

    def turn(self, idx, text):
        self.calls.append((idx, text))
        return {"content": "```json\n" + json.dumps(self.save_block) + "\n```"}


def _env(root: Path):
    states_dir, run_dir = root / "states", root / "run"
    onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
    states_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    return states_dir, run_dir, onboarding_dir, catalog_dir


def test_q07_fortsetzen_actually_continues_existing_open_creation_dialog():
    """Kernassertion: `_cmd_menu_fortsetzen()` bindet die offene Erschaffung
    tatsaechlich an den VORHANDENEN Verlauf (turn_idx/initial_outgoing aus
    dem bereits aufgezeichneten Schritt, kein Neustart) und loest einen
    echten GM-Call aus (Fake-GM-Zaehler > 0 statt 0)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
        pid = "lingerer"
        write_test_profile(run_dir)

        # Real begonnene Erschaffung MIT bereits einem abgeschlossenen
        # Zwischenschritt (nicht ein frischer Start ohne jeden Verlauf) --
        # genau der Zustand, den die alte Signpost-Antwort bisher NICHT
        # tatsaechlich fortsetzte.
        onboarding.start_or_resume(onboarding_dir, pid)
        onboarding.record_step(
            onboarding_dir, pid,
            "Wie beginnt deine Zeitreise?", "Ich erwache in einem Rift.",
        )

        save_block = upgrade_narrow_save(json.loads((_FIX / "sniper.json").read_text(encoding="utf-8")))
        gm = _FakeGm(save_block)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir, catalog_dir, pid,
            input_fn=_eof_input, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda: gm,
        )

        card = session._build_resume_card()
        assert card is not None, "offene Erschaffung darf keine leere Karte liefern (P04)"
        assert card.pending_creation is True, card
        assert card.chrononaut_id is None, card

        session._cmd_menu_fortsetzen()
        out = "\n".join(printed)

        # Q07-Kernbeleg: ein echter Erschaffungszug ist gefolgt, kein
        # reiner Wegweiser-Text mehr.
        assert len(gm.calls) == 1, f"Fake-GM-Zaehler muss > 0 sein (echter Zug), war: {gm.calls}"
        turn_idx, outgoing = gm.calls[0]
        assert turn_idx == 1, (
            "turn_idx muss den bereits vorhandenen Schritt fortsetzen (len(steps)==1), "
            f"nicht neu bei 0 beginnen: {turn_idx}"
        )
        assert outgoing == "Ich erwache in einem Rift.", (
            "die naechste SL-Nachricht muss die VORHANDENE letzte Antwort aus dem Verlauf "
            f"sein (kein Neustart): {outgoing!r}"
        )
        assert "Erschaffung abgeschlossen" in out, out

        state = onboarding.peek(onboarding_dir, pid)
        assert state is not None and state.status == "completed", state
        assert len(state.steps) == 1, "der bereits bestehende Schritt bleibt erhalten, kein Duplikat"


def test_q07_fortsetzen_without_configured_sl_binding_stays_honest_no_fake_progress():
    """Erhaltungsprobe: ohne konfigurierte SL-Anbindung (kein `gm_transport_
    factory`) bleibt der Dispatch ehrlich -- derselbe bestehende Hinweis
    aus `_cmd_new_or_switch_character` ("konfigurierte SL-Anbindung... hier
    nicht konfiguriert"), kein automatischer Spielstart, keine erfundene
    Fortschrittsmeldung."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
        pid = "lingerer2"
        onboarding.start_or_resume(onboarding_dir, pid)

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir, catalog_dir, pid,
            input_fn=_eof_input, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
        )
        card = session._build_resume_card()
        assert card is not None and card.pending_creation is True and card.chrononaut_id is None, card

        session._cmd_menu_fortsetzen()
        out = "\n".join(printed)
        assert "konfigurierte SL-Anbindung" in out, out
        assert "kein Stand" not in out, out
        assert "Lokale Runde erfordert" not in out, out

        state = onboarding.peek(onboarding_dir, pid)
        assert state.status == "in_progress", "kein erfundener Abschluss ohne SL-Anbindung"


def main() -> int:
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
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
