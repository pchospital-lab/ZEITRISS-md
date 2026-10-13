#!/usr/bin/env python3
"""
tests/mmo_sim/test_a04_shared_app_service.py — A4 (PLAN-CRITIC.md WICHTIG):
konkreter neuer Introspektions-/Spy-Test, der belegt, dass `scripts/mmo_sim.
py`/`mmo_sim/ui/tui.py` (TUI) UND `mmo_sim/lab/runner.py` (Lab) DENSELBEN
`core.app_service.run_play_session`-Call-Pfad durchlaufen -- nicht bloss
strukturell aehnlichen, aber separaten Code (REVIEW-P2.md §I1: "TUI und Lab
muessen nachweisbar genau diesen Service verwenden").

Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_block_text, full_v7_save  # noqa: E402

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import app_service, store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding, saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import (  # noqa: E402
    COMPLETION_MARKER, ZeitrissHarvestValidator, ZeitrissTableSizePolicy,
)
from mmo_sim.lab.runner import LabBudget, LabRunner  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_DUMMY_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)


class _MarkerGm:
    """Liefert den Abschluss-Marker SOFORT auf den ersten Turn -- der
    Zweck dieses Tests ist der BEWEIS des gemeinsamen Call-Pfads, nicht ein
    vollstaendiger Spieldurchlauf (der wird separat in
    test_p2_offline_player_journey.py gefuehrt).

    W50 NEW_FLOW_SEQUENCE (Savegate-Harvest, 02_TEAM_UND_QUELLRAHMEN.md
    "Testfixtures versus Schutzassertionen"): die SL-Antwort muss seit dem
    Savegate-Umbau (`core.runtime.run_full_section.finalize`) einen echten,
    vollschema-gueltigen v7-Save-Block fuer die abgeschlossene Figur
    ENTHALTEN, sonst gilt die Ernte als unvollstaendig und
    `save_correction.pursue_group_save_correction` fragt bis zu drei
    zusaetzliche Male bei der SL nach -- der alte bloße-Marker-Fake loeste
    das (ungewollt) aus und liess `gm.calls`/`gm_b.calls` auf 4 statt 1
    laufen, obwohl dieser Test ausschliesslich den gemeinsamen Call-Pfad
    beweisen soll, nicht die Korrekturschleife. `save_text` liefert optional
    genau diesen Block (fenced JSON, VOR dem Marker, also ausserhalb des
    Marker-Fence -- `core.completion_marker.top_level_lines` zaehlt die
    Markerzeile weiterhin unveraendert)."""

    def __init__(self, save_text: str = ""):
        self.calls = 0
        # E1/E2 (MAIN-ENTSCHEIDUNG I2-Nachzug GM-Weg): konfigurierte
        # Ausgabegrenze nachgebildet -- ohne dieses Attribut wuerde das jetzt
        # korrekt durchgesetzte Q07-Prinzip (kein erkennbares Limit + hartes
        # `max_usd` -> ablehnen) diese reine Call-Path-Spy-Fixture blockieren.
        self.output_limit_tokens = 2000
        self._save_text = save_text

    def turn(self, turn_idx: int, user_text: str, output_limit_tokens: float | None = None) -> dict:
        self.calls += 1
        content = f"{self._save_text}\n{COMPLETION_MARKER}" if self._save_text else COMPLETION_MARKER
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}


class _OneShotDriver:
    def __init__(self):
        self.calls = 0

    def decide(self, context: dict) -> ParticipantDecision:
        self.calls += 1
        return ParticipantDecision(text="Meine Aktion.", origin_source="fake:a04")


def _setup_env(root: Path, participant_id: str):
    schema_path = root / "schema.json"
    schema_path.write_text(_DUMMY_SCHEMA, encoding="utf-8")
    states_dir = root / "states"
    states_dir.mkdir()
    run_dir = root / "run"
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    ps_store.save_state(participant_id, {
        "v": 2, "persona_key": participant_id, "rounds_played": 0,
        "plays_char": {"character_id": "chrono-a04"},
    }, states_dir=states_dir)
    return schema_path, states_dir, run_dir, ps_store


def test_lab_and_tui_call_the_same_run_play_session():
    calls = []
    original = app_service.run_play_session

    def spy(*args, **kwargs):
        calls.append((args, kwargs))
        return original(*args, **kwargs)

    with patch("mmo_sim.core.app_service.run_play_session", spy):
        # ── (a) Lab-Pfad ────────────────────────────────────────────────
        with tempfile.TemporaryDirectory() as td_a:
            root_a = Path(td_a)
            schema_path, states_dir, run_dir, ps_store = _setup_env(root_a, "lab_pk")
            lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
            lobby.join("lab_pk")
            table, _ = store.create_table_from_offer_log(
                lobby, "t-lab", [{"type": "offer", "id": "o1", "from": "lab_pk", "wants": []}],
                {"lab_pk": "chrono-a04"},
            )
            assert table is not None
            gm = _MarkerGm(save_text=full_v7_block_text("chrono-a04", name="Test"))
            driver = _OneShotDriver()
            controller = TableController("lab_pk", {"lab_pk": driver})
            lab = LabRunner(run_dir, LabBudget(max_turns=100, max_seconds=1000, max_usd=10.0))
            lab.start()
            lab.run_section(
                lobby, table, gm, controller, "sec-lab",
                {"lab_pk": {"user": "Anfang"}}, states_dir, "2026-09-22", "T",
                COMPLETION_MARKER, ZeitrissHarvestValidator(), ps_store,
                zeitriss_saves.harvest_from_debrief,
            )
            lab.release()
        assert len(calls) == 1, "Lab-Pfad haette run_play_session GENAU EINMAL aufrufen muessen"
        # W50 NEW_FLOW_SEQUENCE (Pflicht-Reflexion, Plan §1 Punkt 6 /
        # PLAN-CRITIC-DURCHSTICH.md, core.runtime._collect_reflections):
        # der zweite `decide()`-Aufruf ist die fuer KI-Personas VORGESEHENE
        # (Pflicht-)Reflexion NACH dem Abschluss-Marker, kein zweiter
        # Spielzug -- derselbe Call-Pfad-Beweis bleibt unberuehrt, da auch
        # die Reflexion ausschliesslich ueber `controller.collect_decision`
        # desselben Treibers laeuft.
        assert driver.calls == 2
        assert gm.calls == 1

        # ── (b) TUI-Pfad (`l`, lokale Runde) ────────────────────────────
        with tempfile.TemporaryDirectory() as td_b:
            root_b = Path(td_b)
            schema_path, states_dir, run_dir, ps_store = _setup_env(root_b, "p_tui")
            onboarding_dir = root_b / "onboarding"
            catalog_dir = root_b / "catalog"
            save_block = full_v7_save("chrono-a04", name="Test")
            onboarding.start_or_resume(onboarding_dir, "p_tui")
            onboarding.complete_with_save(
                onboarding_dir, "p_tui", save_block, ZeitrissHarvestValidator(), "chrono-a04",
            )
            gm_b = _MarkerGm(save_text=full_v7_block_text("chrono-a04", name="Test"))
            scripted = iter(["Meine Aktion."])

            def _input_fn(prompt=""):
                try:
                    return next(scripted)
                except StopIteration:
                    raise EOFError()

            # I2/A1 (MAIN-ENTSCHEIDUNG A1, fail-closed): ohne explizite
            # Autorisierung (providerfreies Testprofil ODER Betreiber-Live-/
            # Budgetfreigabe) blockiert das Admission-Gate jetzt JEDE
            # Entscheidung, auch die des menschlichen Leaders selbst
            # (`act()` gated ALLE Rollen). Test-Setup, nicht Typ-Sniffing.
            write_test_profile(run_dir)
            session = TuiSession(
                onboarding_dir, catalog_dir, "p_tui",
                input_fn=_input_fn,
                print_fn=lambda *a, **k: None,
                run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
                gm_transport_factory=lambda: gm_b,
            )
            session._cmd_local_round()
        assert len(calls) == 2, "TUI-Pfad haette run_play_session GENAU EINMAL zusaetzlich aufrufen muessen"
        assert gm_b.calls == 1

    # Beide Aufrufe liefen ueber DIESELBE gepatchte Funktion -- der Spy
    # selbst IST der Beweis, dass es kein zweiter, unabhaengiger Codepfad ist.
    assert calls[0][0] != calls[1][0], "unterschiedliche Tische/Runs -- kein Test-Artefakt durch Wiederverwendung"


def main() -> int:
    import traceback
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
