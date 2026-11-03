#!/usr/bin/env python3
"""
tests/mmo_sim/test_r2_f5_foreign_registration_conflict_2026_11_02.py —
ZR-FIGURENREISE-TISCH-NACHZUG-20261102-R2, enger Nachzug F5 §2
(02_NACHZUG.md, review/independent-r1-review.md F5).

Deckt den konkret benannten R1-Fehler: `_cmd_import` baute `known_char_ids`
NUR aus dem Katalog des IMPORTIERENDEN Teilnehmers (`tui.py` ~2819) -- eine
char_id, die bereits bei einem ANDEREN Teilnehmer registriert ist, lief
dadurch als `register_new` durch `resolve_import` (eigene Save-/
Registrierungs-/Bindungswrites, OBWOHL die Figur schon fremd zugeordnet
ist, AUCH OHNE aktiven Tischlock -- 02_NACHZUG §F5/independent-r1-review.md
F5). Der Fix nutzt die bereits VORHANDENE Cross-Teilnehmer-Lesefunktion
`catalog.find_registration` EINMALIG, VOR jedem Write (`tui.py` kurz vor
`import_export.resolve_import`).

1. test_f5_foreign_registration_rejected_before_any_write — der
   fehlerhafte R1-Fall (zwei Teilnehmer, GEMEINSAMER `catalog_dir` --
   realistisch fuer ein geteiltes lokales Install, s. `_cmd_table_leave`/
   `test_stage5...`-Pattern): Teilnehmer B importiert eine char_id, die
   bereits Teilnehmer A zugeordnet ist -- geparkt, 0 Writes unter B.
2. test_f5_genuinely_new_char_id_still_registers_normally — Regressions-
   Gegenprobe: eine WIRKLICH neue char_id bleibt eine neue Figur (derselbe
   gemeinsame `catalog_dir`, kein Fremdtreffer).

Pure Python, nur `assert`, echter Exitcode."""
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

from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402


def _register_own_figure(onboarding_dir: Path, catalog_dir: Path, participant_id: str, char_id: str, level: int = 1) -> dict:
    save = full_v7_save(char_id, name=participant_id, save_id=f"fixture-{participant_id}-001", level=level)
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
    ))
    return save


def _run_import(session: TuiSession, raw_text: str) -> None:
    """Treibt `TuiSession._cmd_import()` mit vorab bereitgestelltem
    Mehrzeilentext -- derselbe Eingabevertrag wie am echten Terminal
    (Muster `test_stage5_tui_wiring_2026_11_02.py::_run_import`)."""
    lines = iter(raw_text.splitlines() + ["ENDE"])
    base_input = session._input

    def _fn(prompt: str = "") -> str:
        try:
            return next(lines)
        except StopIteration:
            return base_input(prompt)
    session._input = _fn
    session._cmd_import()
    session._input = base_input


def test_f5_foreign_registration_rejected_before_any_write():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"

        # Teilnehmer A registriert (und besitzt damit) CHR-SHARED.
        _register_own_figure(onboarding_dir, catalog_dir, "alice", "CHR-SHARED", level=1)
        alice_catalog_before = (catalog_dir / "catalog__alice.json").read_text(encoding="utf-8")

        # Teilnehmer B (GLEICHER catalog_dir -- geteiltes lokales Install)
        # versucht, EXAKT dieselbe char_id unter der EIGENEN ID zu
        # importieren.
        foreign_save = full_v7_save("CHR-SHARED", name="bob", save_id="fixture-bob-attempt-001", level=5)
        import json as _json
        raw_text = _json.dumps(foreign_save, ensure_ascii=False)

        bob_session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="bob",
            input_fn=lambda p="": "n", print_fn=lambda *_a, **_kw: None, host_capable=False,
        )
        printed: list[str] = []
        bob_session._print = printed.append
        _run_import(bob_session, raw_text)

        assert any("Fremdzuordnungs-Konflikt" in p for p in printed), printed
        assert any("'alice'" in p for p in printed), printed

        # 0 Writes unter Bob: kein Katalogeintrag, kein Onboarding-Stand.
        bob_catalog_path = catalog_dir / "catalog__bob.json"
        assert not bob_catalog_path.exists(), "Bob haette KEINEN Katalogeintrag bekommen duerfen (Fremdzuordnung)."
        bob_state = onboarding.peek(onboarding_dir, "bob")
        assert bob_state is None or bob_state.final_save is None, "Bob haette KEINEN Onboarding-Stand bekommen duerfen."

        # Alice bleibt komplett unberuehrt (Nichtbeteiligten-Beleg).
        alice_catalog_after = (catalog_dir / "catalog__alice.json").read_text(encoding="utf-8")
        assert alice_catalog_after == alice_catalog_before, "Alice's Katalog haette unveraendert bleiben muessen."


def test_f5_genuinely_new_char_id_still_registers_normally():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        _register_own_figure(onboarding_dir, catalog_dir, "alice", "CHR-SHARED", level=1)

        import json as _json
        new_save = full_v7_save("CHR-BOB-OWN", name="bob", save_id="fixture-bob-own-001", level=1)
        raw_text = _json.dumps(new_save, ensure_ascii=False)

        bob_session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="bob",
            input_fn=lambda p="": "j", print_fn=lambda *_a, **_kw: None, host_capable=False,
        )
        printed: list[str] = []
        bob_session._print = printed.append
        _run_import(bob_session, raw_text)

        assert any("Uebernahme abgeschlossen" in p for p in printed), printed
        entries = catalog.list_for_participant(catalog_dir, "bob")
        assert any(e.chrononaut_id == "CHR-BOB-OWN" for e in entries), entries


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
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
