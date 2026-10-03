#!/usr/bin/env python3
"""
tests/mmo_sim/test_a27_neutral_core.py — A27 (04_ABNAHME_UND_TESTPLAN.md).

"Neutraler Teilnehmer-/Anwendungsdatensatz-Hook; ZEITRISS-Adapter setzt
v7/Char-ID/Fuenfer-/Publikationsregeln durch. Neutraler Dummyfall ohne
Char-ID scheitert nicht an generischer Spielklassenpflicht; kein Abschalten
der ZEITRISS-Validierung."

Beweist PLAN-CRITIC.md A1 direkt am Code: `mmo_sim.core.store` wird HIER mit
einer neutralen Dummy-Policy (kein v7, kein char_id) betrieben und ein
Abschluss ohne jede Char-ID gelingt — UND separat, dass die ECHTE
ZEITRISS-Policy einen fehlenden/falschen char_id weiterhin hart ablehnt
(keine globale Abschaltung der Domaenenvalidierung).

Pure Python, nur `assert`, echter Exitcode. Kein Netz, keine Modellaufrufe.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss.policy import (  # noqa: E402
    NullHarvestValidator,
    ZeitrissHarvestValidator,
    ZeitrissTableSizePolicy,
)


class _DummySchemaEnv:
    """Neutrales Schema OHNE Char-ID/v7-Konzept — nur `v` (int) und
    `persona_key` (str) sind Pflichtfelder. Beweist, dass PersonaStateStore
    selbst kein ZEITRISS-Schema kennt (A2/A6)."""

    def __enter__(self):
        self._td = tempfile.TemporaryDirectory()
        root = Path(self._td.name)
        self.schema_path = root / "dummy-state.schema.json"
        self.schema_path.write_text(
            '{"type":"object","required":["v","persona_key"],'
            '"properties":{"v":{"const":2}}}',
            encoding="utf-8",
        )
        self.states_dir = root / "states"
        self.states_dir.mkdir()
        self.run_dir = root / "run"
        return self

    def __exit__(self, *exc):
        self._td.cleanup()


def test_neutral_dummy_without_char_id_succeeds():
    """A27 Kernfall: ein Tisch mit einem Dummy-Teilnehmer OHNE jede Char-ID
    schliesst unter der neutralen `NullHarvestValidator`-Policy erfolgreich ab
    — der Kern selbst erzwingt keine 'ein Chrononaut = ein JSON'-Regel."""
    with _DummySchemaEnv() as env:
        ps_store = PersonaStateStore(schema_path=env.schema_path, default_states_dir=None)
        # Dummy-Persona-State: KEIN "plays_char"/"character_id"-Feld ueberhaupt vorhanden.
        ps_store.save_state("dummy_p1", {"v": 2, "persona_key": "dummy_p1", "rounds_played": 0},
                             states_dir=env.states_dir)

        lobby = store.Lobby(env.run_dir, table_size_policy=ZeitrissTableSizePolicy(min_size=1, max_size=5))
        lobby.join("dummy_p1")
        # chrononaut_id = "" (leer) -- explizit KEINE Char-ID, um den Dummyfall zu markieren.
        table, derivation = store.create_table_from_offer_log(
            lobby, "t-dummy",
            offer_log_events=[
                {"type": "offer", "id": "o1", "from": "dummy_p1", "wants": []},
            ],
            chrononaut_ids={"dummy_p1": ""},
        )
        assert table is not None, f"Tisch mit neutralem Dummy-Teilnehmer haette entstehen muessen: {derivation}"

        # Save-Block ohne "v":7, ohne "characters" -- ein generischer Anwendungsdatensatz.
        dummy_block = {"kind": "dummy-record", "note": "kein ZEITRISS-Save"}
        result = store.complete_section(
            lobby, table, "dummy-section",
            harvested_saves={"dummy_p1": dummy_block},
            states_dir=env.states_dir,
            today="2026-09-22",
            harvest_validator=NullHarvestValidator(),
            persona_state_store=ps_store,
        )
        assert result.success, f"Neutraler Dummyfall haette an KEINER generischen Spielklassenpflicht scheitern duerfen: {result.reason}"
        assert not result.missing


def test_zeitriss_policy_still_rejects_missing_char_id():
    """Gegenprobe (A27 zweiter Halbsatz): die ECHTE ZEITRISS-Policy
    (`ZeitrissHarvestValidator`) lehnt denselben Dummy-Block weiterhin hart
    ab -- die Domaenenvalidierung ist NICHT global abgeschaltet, nur nicht
    mehr im Kern hart verdrahtet."""
    with _DummySchemaEnv() as env:
        validator = ZeitrissHarvestValidator()
        # Kein "v":7, keine "characters" -- muss abgelehnt werden.
        assert validator.validate_block({"kind": "dummy-record"}, "chrono-1") is False
        # Falsche char_id trotz gueltigem v7-Block -- muss abgelehnt werden.
        v7_block = {"v": 7, "characters": [{"char_id": "other-id"}]}
        assert validator.validate_block(v7_block, "chrono-1") is False
        # Korrekte char_id -- muss akzeptiert werden.
        v7_ok = {"v": 7, "characters": [{"char_id": "chrono-1"}]}
        assert validator.validate_block(v7_ok, "chrono-1") is True


def main() -> int:
    tests = [test_neutral_dummy_without_char_id_succeeds, test_zeitriss_policy_still_rejects_missing_char_id]
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
    total = len(tests)
    print(f"\n{total - failed}/{total} Tests bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
