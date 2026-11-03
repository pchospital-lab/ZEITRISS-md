#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_betreiber_o2_stop_waehrend_offenem_call_2026_11_03.py
-- ZR-BETREIBER-GASTERSCHAFFUNG-20261103-R1, O2 (design.md §1d/§1e/§6, echte
TUI-Verdrahtung `ui/tui.py:_OperatorControlScope` um `_run_table_round` ->
`app_service.run_play_session`).

Modellrand-Double (02_ABNAHME §1, EHRLICH gekennzeichnet): `_SlowDebriefGm`
ist ein BLOCKIERENDER In-Process-GM-Transport mit GESTEUERT VERSPAETETER
Antwort (`time.sleep`) -- waehrend dieser 'offene Call' laeuft, injiziert
dieser Test ueber `TuiSession.operator_control_line_source` (die injizierbare
Kontrollzeilen-Quelle aus `_OperatorControlScope`) eine '/stop'-Zeile, OHNE
jedes echte TTY. Identitaet ist VOR dem Call gebunden (§1e, bereits
bestehender Main-Code + die O1/O2-Ergaenzung in `_cmd_local_round`, die
`operator_table_key` fuer den Betreiberpfad synthetisch anlegt).

Beweis: der Stop wird WAEHREND des offenen Calls gesetzt (die Fake-Quelle
liefert '/stop' SOFORT, die GM-Antwort kommt erst nach `_GM_DELAY_S`
Sekunden zurueck) -- NACH Rueckkehr des Calls blockt das bestehende
Runtime-Gate (`core/runtime.py:_check_gate` -> `read_admission_block(
table_id=...)`) an der naechsten Grenze VOR jedem Save: `outcome.completion.
success` ist `False`, KEIN `current_saves/<persona>.json` entsteht."""
from __future__ import annotations

import sys
import tempfile
import threading
import time
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _zr_betreiber_fixtures_2026_11_03 import (  # noqa: E402
    SCHEMA_PATH, AcceptLeadDriver, bootstrap_own_persona, register_own_figure,
)

import mmo_sim.core.admission as admission  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

_GM_DELAY_S = 0.3


class _SlowDebriefGm:
    """Blockierendes Transportdouble mit gesteuert verspaeteter Antwort
    (02_ABNAHME §1, EHRLICH als Double gekennzeichnet) -- schlaeft
    `_GM_DELAY_S` Sekunden, BEVOR es antwortet, damit der Kontroll-Thread
    waehrend dieser Zeit real '/stop' einspeisen kann."""

    def __init__(self):
        self.calls = 0

    def turn(self, turn_idx: int, user_text: str) -> dict:
        self.calls += 1
        time.sleep(_GM_DELAY_S)
        return {
            "content": "Szene 1: Die Heldin zoegert einen Moment zu lange.",
            "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "o2-fake",
        }


def _once_stop_then_idle_source(sent: list[str]):
    """Injizierbare Kontrollzeilen-Quelle (s. `TuiSession.
    operator_control_line_source`-Docstring): wartet ERST `_GM_DELAY_S/3`
    Sekunden (`stop_event.wait`, KEIN Busy-Poll) -- damit der Hauptthread
    sicher schon INNERHALB des blockierenden `_SlowDebriefGm.turn`-Sleeps
    steckt, wenn '/stop' injiziert wird (sonst wuerde die bereits VOR dem
    GM-Versand liegende Gate-Pruefung -- `core/runtime.py:1036`, "zwischen
    Persona-Request und GM-Request" -- den Call gar nicht erst starten
    lassen, und dieser Test bewiese KEINE Nebenlaeufigkeit WAEHREND des
    offenen Calls). Danach GENAU EINMAL '/stop', anschliessend idle bis
    das `stop_event` gesetzt ist (Rundenende)."""
    state = {"sent": False}

    def _source(stop_event: threading.Event) -> str | None:
        if not state["sent"]:
            if stop_event.wait(_GM_DELAY_S / 3):
                return None
            state["sent"] = True
            sent.append("/stop")
            return "/stop"
        stop_event.wait(_GM_DELAY_S * 4)
        return None
    return _source


def test_o2_stop_waehrend_offenem_call_blockt_an_naechster_grenze():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
        write_test_profile(run_dir, max_turns=200)

        operator_id = "betreiber_o2"
        persona_key = "gm_sentinel"
        persona_char_id = "CHR-O2-SENTINEL"

        bootstrap_own_persona(run_dir, states_dir, operator_id, persona_key)
        register_own_figure(
            onboarding_dir, catalog_dir, persona_key, persona_char_id, run_dir=run_dir, states_dir=states_dir,
        )
        # `register_own_figure` publiziert bereits die STARTfassung unter
        # `current_saves/<persona>.json` (Voraussetzung, damit die Persona
        # ueberhaupt als Leader auflösbar ist) -- der eigentliche Beweis
        # ist daher NICHT "Datei fehlt", sondern "Datei bleibt bytegleich"
        # (kein neuer Harvest-Write durch die geblockte Runde).
        import hashlib
        persona_save_path = run_dir / "current_saves" / f"{persona_key}.json"
        assert persona_save_path.exists(), "Startfassung haette aus der Fixture existieren muessen."
        sha_before = hashlib.sha256(persona_save_path.read_bytes()).hexdigest()

        driver = AcceptLeadDriver(persona_key, play_replies=["Wir beobachten die Lage."])
        gm = _SlowDebriefGm()
        sent: list[str] = []

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=operator_id,
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=SCHEMA_PATH,
            gm_transport_factory=lambda: gm,
            persona_driver_factory=lambda pk: driver,
            host_capable=True,
        )
        session.operator_control_line_source = _once_stop_then_idle_source(sent)

        t0 = time.monotonic()
        try:
            # allow_operator_mode=True bildet exakt den frei getippten
            # 'l operator ...'-Dispatch (tui.py run(): choice=='l') nach.
            section_id = session._cmd_local_round(
                ["operator", f"lead:persona:{persona_key}"], allow_operator_mode=True,
            )
        except EndOfInput:
            raise AssertionError(f"unerwartete EndOfInput. printed={printed}")
        elapsed = time.monotonic() - t0

        assert sent == ["/stop"], "die injizierte Kontrollzeile muss real konsumiert worden sein."
        assert elapsed >= _GM_DELAY_S, (
            f"der GM-Call muss tatsaechlich blockiert haben (elapsed={elapsed:.3f}s) -- "
            "sonst beweist dieser Test keine Nebenlaeufigkeit WAEHREND des offenen Calls."
        )
        assert section_id is not None, f"der Tisch selbst entsteht trotzdem (Store-Ebene, vor dem Call). printed={printed}"

        stop_lines = [p for p in printed if "Betreiber-Stop gesetzt" in p]
        assert stop_lines, f"der Kontroll-Thread haette die Stop-Bestaetigung drucken muessen. printed={printed}"

        from mmo_sim.core import store as core_store
        table = core_store.Table.load(run_dir, section_id)
        stopped, reason = admission.read_table_stop(run_dir, table.table_id)
        assert stopped is True, "der tischadressierte Stop muss real auf Platte liegen."

        # Gate/Guard blockt an der naechsten Grenze, VOR jedem Save: KEIN
        # neuer Primaersave-Write fuer die Persona -- die Startfassung
        # bleibt bytegleich.
        sha_after = hashlib.sha256(persona_save_path.read_bytes()).hexdigest()
        assert sha_after == sha_before, (
            f"O2: der waehrend des offenen Calls gesetzte Stop haette JEDEN Save an der "
            f"naechsten Grenze blocken muessen (Datei wurde veraendert). printed={printed}"
        )
        blocked_lines = [p for p in printed if "nicht abgeschlossen" in p and "Admission-Gate blockiert" in p]
        assert blocked_lines, f"das Admission-Gate haette den Abschluss sichtbar blocken muessen. printed={printed}"
        plan_path = run_dir / "completion" / f"{table.table_id}-section__plan.json"
        assert not plan_path.exists(), "kein Plan-Pin darf bei einem waehrend des Calls gesetzten Stop entstehen."


def test_o2_default_line_source_kein_busyspin_bei_eof_stdin():
    """Regression (Abschluss-Critic-Befund 1): bei geschlossenem/nicht-
    interaktivem stdin (headless/Service/CI/Docker ohne TTY) meldet
    `select` EOF DAUERHAFT als lesebereit und `readline()` liefert sofort
    `''` -- ohne Backoff drehte `_OperatorControlScope._loop` ueber
    `continue` einen CPU-Kern auf 100%. Der Fix unterscheidet echtes EOF
    (`''`) vom bloss-keine-Eingabe-Fall und federt es mit
    `stop_event.wait(0.2)` ab.

    Beweis gegen den AUSGELIEFERTEN Code (keine Abschrift): ein einzelner
    Aufruf von `_default_line_source` mit echtem EOF-stdin liefert `None`
    UND kostet den vollen Backoff (~0.2s) -- VOR dem Fix kam er in ~0s
    zurueck, was die Heisslauf-Schleife verursachte."""
    import os
    from mmo_sim.ui.tui import _OperatorControlScope

    r_fd, w_fd = os.pipe()
    os.close(w_fd)  # Schreibseite zu -> Leseseite ist dauerhaft EOF
    r_file = os.fdopen(r_fd, "r")
    saved_stdin = sys.stdin
    sys.stdin = r_file
    try:
        stop_event = threading.Event()  # NICHT gesetzt -> voller Backoff erwartet
        t0 = time.monotonic()
        result = _OperatorControlScope._default_line_source(stop_event)
        elapsed = time.monotonic() - t0
    finally:
        sys.stdin = saved_stdin
        r_file.close()

    assert result is None, f"EOF-stdin muss None liefern, nicht {result!r}"
    assert elapsed >= 0.15, (
        f"kein Backoff bei EOF-stdin -> Busy-Spin-Risiko (elapsed={elapsed:.4f}s, "
        "erwartet >= ~0.2s)"
    )


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
