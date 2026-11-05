#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_betreiber_o3_stop_vor_planpin_2026_11_03.py --
ZR-BETREIBER-GASTERSCHAFFUNG-20261103-R1, O3 (design.md §1c/§6).

Beweist die durable O3-Grenze IN `store.complete_section` selbst (NICHT im
Runtime-Gate -- die Guard-Reihenfolge, s. `core/store.py` kurz vor dem
Plan-Pin bei `complete_section`, laesst `read_table_stop` GENAU vor dem
`plan_path.write_text`-Call laufen):

1. Ein tischadressierter Betreiber-Stop (`table_admission.request_table_
   stop`, VOR dem Plan-Pin gesetzt) verweigert den ERSTMALIGEN Abschluss
   (`complete_section` -> `success=False`), KEIN `__plan.json` wird
   geschrieben.
2. Die bereits vorhandene "Gast-Startdatei" (hier: ein vor dem Versuch
   bestehender `current_saves/<pk>.json`, Stellvertreter fuer "der Gast
   behaelt exakt seine akzeptierte Startfassung") bleibt BYTEGLEICH --
   sha256 vorher == sha256 nachher.
3. Eine spaete, erneut eintreffende Antwort UND ein "frischer Prozess"
   (hier: eine komplett NEU von der Platte geladene `Table`-Instanz, da der
   gesamte Zustand ohnehin ausschliesslich auf Platte lebt -- derselbe
   Durabilitaetsnachweis wie in den bestehenden R12-Fixtures) revitalisieren
   den Abschnitt NICHT -- der Stop-Marker liegt weiterhin auf Platte.
4. Der Korrekturpfad (`save_correction.py`s drei Direktaufrufer, Zeilen
   1951/2103/2318 laut Code-Map A-codemap.md F2) ruft LETZTLICH exakt
   dieselbe `complete_section`-Funktion mit `best_effort=True` -- derselbe
   Guard (er sitzt VOR der `best_effort`-Verzweigung, s. store.py) greift
   daher identisch. Dieser Test uebt `complete_section(..., best_effort=
   True)` direkt (NICHT das gesamte `save_correction`-Modul, das haette
   einen eigenen GM-/Request-Ledger-Loop gebraucht) -- das ist der exakt
   geteilte Codepfad, den ALLE drei Korrektur-Call-Sites durchlaufen.

Pure Python, nur `assert`, echter Exitcode. Modellrand: KEIN Call hier --
`complete_section` wird direkt mit bereits "geernteten" Saves aufgerufen,
kein Transport/keine Persona involviert (reine Store-/Admission-Ebene)."""
from __future__ import annotations

import hashlib
import json
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

from _full_v7_fixture import full_v7_save  # noqa: E402
from _section_completion_resume_fixtures import build_two_member_table, make_env  # noqa: E402

import mmo_sim.core.store as store  # noqa: E402
import mmo_sim.core.table_admission as table_admission  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402

_TODAY = "2026-11-03"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_o3_stop_vor_planpin_blockt_ersten_abschluss_kein_plan_write():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        env = make_env(root)
        lobby, table, ps_store = build_two_member_table(env, table_id="o3-tisch")

        # "Gast-Startdatei" (Stellvertreter): eine bereits bestehende
        # current-Save-Fassung des Gasts, BEVOR irgendein Abschlussversuch
        # laeuft -- die darf von einem geblockten Versuch nicht beruehrt
        # werden.
        current_saves_dir = env.run_dir / "current_saves"
        current_saves_dir.mkdir(parents=True, exist_ok=True)
        guest_start_path = current_saves_dir / "guest_pk.json"
        guest_start_path.write_text(json.dumps({"startfassung": True, "pk": "guest_pk"}), encoding="utf-8")
        sha_before = _sha256(guest_start_path)

        # Betreiber-Stop VOR jedem Abschlussversuch binden+setzen (O6-
        # Autoritaet: offer_table -> bind_section -> request_table_stop).
        table_admission.offer_table(env.run_dir, host_id="leader_pk", table_key="o3-key")
        table_admission.bind_section(
            env.run_dir, table_key="o3-key", host_id="leader_pk", section_id=table.table_id,
        )
        table_admission.request_table_stop(
            env.run_dir, table_key="o3-key", operator_id="leader_pk", table_id=table.table_id,
            reason="O3-Test: Stop vor Plan-Pin.",
        )

        harvested = {
            "leader_pk": full_v7_save("chrono-leader", name="Testfigur"),
            "guest_pk": full_v7_save("chrono-guest", name="Testfigur"),
        }
        section_id = table.table_id
        result = store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, _TODAY,
            ZeitrissHarvestValidator(), ps_store,
        )
        assert result.success is False, result
        assert result.written is False, result
        assert "Betreiber-Stop" in result.reason, result.reason

        plan_path = env.run_dir / "completion" / f"{section_id}__plan.json"
        assert not plan_path.exists(), "O3: kein __plan.json darf bei aktivem Stop entstehen."
        assert _sha256(guest_start_path) == sha_before, "Gast-Startdatei wurde trotz Stop veraendert."

        # (3) Spaete Antwort + "frischer Prozess": NEUE Table-Instanz von
        # der Platte, derselbe (bereits auf Platte liegende) Stop-Marker.
        fresh_table = store.Table.load(env.run_dir, table.table_id)
        result2 = store.complete_section(
            lobby, fresh_table, section_id, harvested, env.states_dir, _TODAY,
            ZeitrissHarvestValidator(), ps_store,
        )
        assert result2.success is False, result2
        assert "Betreiber-Stop" in result2.reason, result2.reason
        assert not plan_path.exists(), "frischer Prozess darf den Stop nicht umgehen."
        assert _sha256(guest_start_path) == sha_before

        # (4) Korrekturpfad-Aequivalent: derselbe Guard, best_effort=True --
        # exakt der Codepfad, den save_correction.py an allen drei
        # Direktaufrufstellen durchlaeuft (A-codemap.md F2).
        result3 = store.complete_section(
            lobby, fresh_table, section_id, harvested, env.states_dir, _TODAY,
            ZeitrissHarvestValidator(), ps_store, best_effort=True,
        )
        assert result3.success is False, result3
        assert "Betreiber-Stop" in result3.reason, result3.reason
        assert not plan_path.exists(), "best_effort=True darf den Stop nicht umgehen."


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
