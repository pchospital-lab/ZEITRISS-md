#!/usr/bin/env python3
"""
tests/mmo_sim/test_terminal_command_note_2026_10_22.py —
R4-MEHRSPIELER (ZR-N2R-ANSCHLUSS-20261019-R4): der Persona-Systemkontext
(`ui/tui.py:TuiSession._own_system_context`) stellt jedem Zug eine kleine,
fixe Terminal-Kommando-Notiz voran, damit die zustandslos pro Zug spawnende
Persona weiss, dass sie am HQ-Abschnittsende `!save`/`!speichern` als
ALLEINIGE Nachricht senden muss (Client-UX, KEIN Spielleitungs-/Weltwissen).
`!bogen` (reiner Ingame-Ansichtsbefehl, kein App-Trigger) gehoert bewusst
NICHT hinein.

Pure Python, nur `assert`, echter Exitcode (Konvention wie
`test_m1_runtime_section.py`)."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.ui.tui import TuiSession, _TERMINAL_COMMAND_NOTE  # noqa: E402

_DUMMY_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)


def _session_with_state(root: Path, persona_key: str) -> TuiSession:
    states_dir = root / "states"
    run_dir = root / "run"
    onboarding_dir = root / "onboarding"
    catalog_dir = root / "catalog"
    for d in (states_dir, run_dir, onboarding_dir, catalog_dir):
        d.mkdir(parents=True, exist_ok=True)
    schema_path = root / "schema.json"
    schema_path.write_text(_DUMMY_SCHEMA, encoding="utf-8")
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    ps_store.save_state(persona_key, {
        "v": 2, "persona_key": persona_key, "rounds_played": 0,
        "plays_char": {"character_id": "CHR-NOTE-01", "name": "Test"},
    }, states_dir=states_dir)
    return TuiSession(
        onboarding_dir, catalog_dir, persona_key,
        run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
    )


def test_persona_system_context_leads_with_terminal_command_note():
    with tempfile.TemporaryDirectory() as td:
        pk = "p_note"
        session = _session_with_state(Path(td), pk)
        ctx = session._own_system_context(pk)
        # Bewusst ANGEHAENGT (nicht vorangestellt): der Kontext beginnt weiter mit
        # der render_for_prompt-Kopfzeile und endet mit der Notiz -- so bleibt die
        # bestehende Kontextstruktur (Header vorn, Current-JSON per raw_decode
        # lesbar) fuer alle Leser unveraendert.
        assert ctx.endswith(_TERMINAL_COMMAND_NOTE), (
            "der Persona-Systemkontext muss mit der fixen Terminal-Kommando-Notiz ENDEN "
            f"(jeder Zug), endete aber mit: {ctx[-80:]!r}"
        )
        assert not ctx.startswith(_TERMINAL_COMMAND_NOTE), (
            "die Notiz wird ANGEHAENGT, nicht vorangestellt (Kontext beginnt mit der "
            "render_for_prompt-Kopfzeile)."
        )
        # Kerninhalt: genau das App-Kommando, HQ-gebunden, alleinige Nachricht.
        assert "!save" in ctx and "!speichern" in ctx, "die Notiz muss !save/!speichern nennen."
        assert "HQ" in ctx, "die Notiz muss die HQ-Bindung nennen."
        assert "ALLEINIGE" in ctx or "alleinige" in ctx.lower(), (
            "die Notiz muss 'alleinige Nachricht' verlangen (blankes Kommando, kein Fliesstext)."
        )
        # `!bogen` ist reiner Ingame-Ansichtsbefehl -> NICHT in der Client-Notiz.
        assert "!bogen" not in ctx, (
            "`!bogen` ist kein App-/Client-Kommando (reine Ingame-Ansicht) und darf NICHT "
            "in der Terminal-Bedienungsnotiz stehen."
        )
        # Der eigene State/Render steht VOR der angehaengten Notiz (Notiz ist Suffix, kein Ersatz).
        assert len(ctx) > len(_TERMINAL_COMMAND_NOTE), "der eigene State muss zusaetzlich zur Notiz vorhanden sein."


def test_note_constant_is_minimal_save_only():
    # Schutzassertion gegen Scope-Kriechen: die Notiz nennt NUR das Save-Kommando,
    # keine weiteren erfundenen Client-Kommandos.
    for forbidden in ("!bogen", "!hilfe", "!help", "!menu", "!menue"):
        assert forbidden not in _TERMINAL_COMMAND_NOTE, (
            f"die Terminal-Notiz soll minimal bleiben (nur !save/!speichern), fand {forbidden!r}."
        )
    assert "!save" in _TERMINAL_COMMAND_NOTE and "!speichern" in _TERMINAL_COMMAND_NOTE


def main() -> int:
    tests = [
        test_persona_system_context_leads_with_terminal_command_note,
        test_note_constant_is_minimal_save_only,
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
            import traceback
            failed += 1
            print(f"ERROR {t.__name__}:")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} Tests bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
