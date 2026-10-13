#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_label_authority.py — R1 (Korrekturzyklus 1, C-M1,
UX14), ZEITRISS Terminal UX-1.

Vorher: `_HumanDriver._purpose_label()` (mmo_sim/ui/tui.py) und die
Payload-Wahl am Zugende entschieden ausschliesslich ueber den
Pro-Prozess-Zaehler `self._turn`, der bei JEDEM Prozessneustart wieder bei
0 beginnt. Die Runtime (`core/runtime.py:SectionRuntime`) rekonstruiert die
tatsaechliche "hat schon importiert"-Autoritaet dagegen aus dem
PERSISTIERTEN `table.sl_log` (`_guests_imported`). Nach einem Neustart
einer laufenden Runde zeigte ein bereits frueher importierter Gast
faelschlich "Erstbeitrag -> SL (mit deinem Save)", obwohl sein Beitrag
real nur noch Tischabsprache wird (`poll_guests_and_consolidate` liest
`save_payload` nie aus, schreibt nie in `sl_log`).

Dieser Test simuliert einen echten Prozessneustart ueber ZWEI unabhaengige
`TuiSession`-Objekte, die sich ausschliesslich das Dateisystem (`run_dir`)
teilen -- exakt wie im Critic-Repro (`critic/out/CRITIQUE.md`, M1).

Erhaltungsprobe: der echte Erstfall (Prozess 1, keine Vorgeschichte)
bleibt "Erstbeitrag -> SL" UND landet nachweislich im `sl_log`.

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs."""
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

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.ui.tui import TuiSession, EndOfInput  # noqa: E402
import _a24_local_support as sup  # noqa: E402


class _FakeGm:
    """Liefert nie einen Completion-Marker -- die Sektion bleibt 'offen'
    (laufende Runde), damit nach dem simulierten Neustart der
    Poll-/Tischabsprache-Pfad real erreicht wird."""

    def __init__(self):
        self.calls: list[tuple[int, str]] = []

    def turn(self, turn_idx, text, **kw):
        self.calls.append((turn_idx, text))
        return {"content": f"SL-Antwort #{turn_idx} (kein Abschluss-Marker hier)."}


def _scripted(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


def _build_table(run_dir: Path, states_dir: Path, onboarding_dir: Path, catalog_dir: Path):
    registry_dir = run_dir.parent / "registry"
    leader = sup.register_human(registry_dir, "Leader")
    guest = sup.register_human(registry_dir, "Guest")
    leader_id, guest_id = leader.participant_id, guest.participant_id
    sup.onboard_human_figure(
        registry_dir, leader_id, onboarding_dir, states_dir, run_dir, "CHR-LEAD", "Lea", "LEADOPS",
    )
    sup.onboard_human_figure(
        registry_dir, guest_id, onboarding_dir, states_dir, run_dir, "CHR-GUEST", "Gus", "GUESTOPS",
    )
    return leader_id, guest_id


def test_first_import_label_matches_real_sl_log_transport():
    """Erhaltungsprobe: der echte Erstfall (keine Vorgeschichte) bleibt
    korrekt 'Erstbeitrag -> SL' UND landet nachweislich im sl_log."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = d / "run", d / "states", d / "onboarding", d / "catalog"
        write_test_profile(run_dir)
        leader_id, guest_id = _build_table(run_dir, states_dir, onboarding_dir, catalog_dir)

        printed: list[str] = []
        gm = _FakeGm()
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=leader_id,
            input_fn=_scripted([
                "j",
                "Leader-Zug 1 (Anker).",
                "Gast-Erstbeitrag (Import).",
            ]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=sup.SCHEMA,
            gm_transport_factory=lambda: gm,
            persona_driver_factory=None,
        )
        try:
            session._cmd_local_round([guest_id])
        except EndOfInput:
            pass

        labels = [p for p in printed if p.startswith("Empfaenger:")]
        assert any("Erstbeitrag" in lbl for lbl in labels), labels

        table_file = run_dir / "tables" / f"local-{leader_id}-{guest_id}.json"
        assert table_file.exists()
        data = json.loads(table_file.read_text(encoding="utf-8"))
        guest_sl_entries = [e for e in data.get("sl_log", []) if e.get("origin_persona_key") == guest_id]
        assert guest_sl_entries, "Gast-Erstimport muss im sl_log landen (Erhaltungsprobe)"
        assert any(e.get("save_payload") is not None for e in guest_sl_entries), guest_sl_entries


def test_already_imported_guest_label_honest_after_restart_no_fake_sl_promise():
    """R1 (C-M1): nach einem simulierten Prozessneustart behauptet das
    Label fuer einen bereits frueher importierten Gast NICHT mehr
    'Erstbeitrag -> SL' -- sein Zweitbeitrag landet nachweislich nur noch
    als Tischabsprache, nie im sl_log."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = d / "run", d / "states", d / "onboarding", d / "catalog"
        write_test_profile(run_dir)
        leader_id, guest_id = _build_table(run_dir, states_dir, onboarding_dir, catalog_dir)

        # --- "Prozess 1": Leader-Anker + Gast-Erstimport.
        printed_1: list[str] = []
        gm1 = _FakeGm()
        session1 = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=leader_id,
            input_fn=_scripted([
                "j",
                "Leader-Zug 1 (Anker).",
                "Gast-Erstbeitrag (Import).",
            ]),
            print_fn=printed_1.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=sup.SCHEMA,
            gm_transport_factory=lambda: gm1,
            persona_driver_factory=None,
        )
        try:
            session1._cmd_local_round([guest_id])
        except EndOfInput:
            pass

        sl_log_count_after_p1 = len(
            json.loads((run_dir / "tables" / f"local-{leader_id}-{guest_id}.json").read_text(encoding="utf-8"))
            .get("sl_log", [])
        )

        # --- "Prozess 2": NEUE, unabhaengige TuiSession, derselbe run_dir
        # (simulierter Neustart). Der Gast bestaetigt den Beitritt erneut
        # (echte erneute Eingabe) und gibt einen ZWEITEN Beitrag ab.
        printed_2: list[str] = []
        gm2 = _FakeGm()
        session2 = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=leader_id,
            input_fn=_scripted([
                "j",
                "Leader-Zug 2 (nach Neustart).",
                "Gast-Zweitbeitrag (nach Neustart, muss Tischabsprache sein).",
            ]),
            print_fn=printed_2.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=sup.SCHEMA,
            gm_transport_factory=lambda: gm2,
            persona_driver_factory=None,
        )
        try:
            session2._cmd_local_round([guest_id])
        except EndOfInput:
            pass

        label_lines = [p for p in printed_2 if p.startswith("Empfaenger:")]
        assert label_lines, printed_2
        # Kernassertion R1: KEIN Label in Prozess 2 darf dem Gast noch
        # "Erstbeitrag...SL" versprechen -- er hat bereits in Prozess 1
        # importiert, sein Beitrag wird nachweislich nur Tischabsprache.
        assert not any("Erstbeitrag" in lbl for lbl in label_lines), (
            f"Label luegt nach Neustart: {label_lines}"
        )
        assert any("Tischabsprache" in lbl for lbl in label_lines), label_lines

        table_file = run_dir / "tables" / f"local-{leader_id}-{guest_id}.json"
        data = json.loads(table_file.read_text(encoding="utf-8"))
        sl_log_after_p2 = data.get("sl_log", [])
        # Kernassertion R1 (Transportziel): der Gast-Zweitbeitrag darf NICHT
        # als zusaetzlicher sl_log-Eintrag des Gasts auftauchen -- die
        # Zusage im Label muss zum tatsaechlichen Transportziel passen.
        new_guest_sl_entries = [
            e for e in sl_log_after_p2[sl_log_count_after_p1:] if e.get("origin_persona_key") == guest_id
        ]
        assert not new_guest_sl_entries, (
            f"Gast-Zweitbeitrag landete faelschlich im sl_log: {new_guest_sl_entries}"
        )
        guest_table_messages = [m for m in data.get("table_messages", []) if m.get("from") == guest_id]
        assert any("Zweitbeitrag" in m.get("text", "") for m in guest_table_messages), data.get("table_messages")


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
