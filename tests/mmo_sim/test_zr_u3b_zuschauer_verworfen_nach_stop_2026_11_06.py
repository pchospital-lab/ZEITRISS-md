#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_u3b_zuschauer_verworfen_nach_stop_2026_11_06.py
-- ZR-VOLLENDUNG-OHNE-LAN-NACHZUG-20261106-R3, U3b (01_NACHZUG.md §U3b,
02_ABNAHME.md §C: "Nach der Anzeigeaenderung genau diesen betroffenen Fall
eng durch den normalen Betreiber-Kontrollweg pruefen").

Dauerhafter Regressionswaechter fuer die R3-Anzeigegrenze in
`TuiSession._print_spectator_view` (mmo_sim/ui/tui.py:5395): nach einem
kontrollierten Stop darf ein spaet eingetroffener SL-Eintrag (verworfene
Spaetantwort) NICHT mehr als normaler oeffentlicher Spielinhalt im
Zuschauer-Feed erscheinen, sondern NUR als klar markierte Verwurf-Zeile.
Der gemeinsame atomare Entscheid-Slot (`core.admission.read_table_decision`,
geschrieben via `try_commit_table_decision`, O_CREAT|O_EXCL) ist die Wahrheit.

Dieser Fall war vor R3 nicht automatisiert abgedeckt (Vera-Befund 11): die
Stop-Mechanik-Tests pruefen Save-Erhalt/kein-zweiter-Call, aber keiner ruft
`_print_spectator_view` nach einem "stopped"-Entscheid auf und prueft die
NEUE Anzeige. Ohne diesen Waechter faellt eine kuenftige Regression an genau
dieser Stelle durch `bash scripts/smoke.sh` nicht auf.

Asserts:
1. Negativkontrolle (kein Vakuum): OHNE Stop-Entscheid erscheint der rohe
   SL-Verlauf (die Spaetantwort) im Zuschauer-Feed als '[Zuschauer][SL] ...'
   -- der Test wuerde also ohne den Fix auch wirklich etwas sehen.
2. Positivfall: MIT "stopped"-Entscheid erscheint NUR die Verwurf-Zeile
   ('verworfen -- nach Stop eingetroffen') und der rohe Spaetantwort-Inhalt
   taucht im gesamten Zuschauer-Protokoll NICHT mehr auf.
3. Die vier Zustaende werden nicht vermischt: im verworfenen Fall wird kein
   '[Zuschauer][SL] '-Eintrag mehr gedruckt.
"""
from __future__ import annotations

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

from mmo_sim.core import admission as core_admission  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_TABLE_ID = "t-u3b-verwurf"
_SECRET_LATE = (
    "SL-Spaetantwort auf Anker B1b -- verspaetet eingetroffen, NICHT adoptiert; "
    "darf im Zuschauer-Feed nach Stop nicht als Spielinhalt erscheinen."
)


def _make_run_with_table(tmp_root: Path) -> Path:
    """Minimaler echter Lauf: ein Tisch mit genau EINER (spaet eingetroffenen)
    SL-Zeile, ueber die reale `core_store.Table`-Persistenz geschrieben."""
    run_dir = tmp_root / "run"
    (run_dir / "tables").mkdir(parents=True, exist_ok=True)
    table = core_store.Table(
        table_id=_TABLE_ID,
        leader="persona:gm_nova",
        members=["persona:gm_nova"],
        chrononaut_ids={"persona:gm_nova": "chrono-nova"},
        run_dir=run_dir,
        sl_log=[{"turn_idx": 1, "content": _SECRET_LATE}],
        status="closed",
    )
    table.persist()
    return run_dir


def _spectator_lines(run_dir: Path) -> list[str]:
    """Ruft den ECHTEN `_print_spectator_view` auf und faengt die Ausgabe --
    minimal konstruierte Session (kein voller Bootstrap noetig: die Methode
    braucht nur `run_dir` + `_print`), gegen die reale Methode am Produkt."""
    sess = TuiSession.__new__(TuiSession)
    sess.run_dir = run_dir
    captured: list[str] = []
    sess._print = lambda text="": captured.append(str(text))  # type: ignore[method-assign]
    sess._print_spectator_view(_TABLE_ID)
    return captured


def test_u3b_ohne_stop_zeigt_rohen_verlauf():
    """Negativkontrolle: ohne Stop-Entscheid ist die Spaetantwort normal sichtbar."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _make_run_with_table(Path(td))
        lines = _spectator_lines(run_dir)
        joined = "\n".join(lines)
        assert any(line.startswith("[Zuschauer][SL] ") for line in lines), (
            "Negativkontrolle gescheitert: ohne Stop-Entscheid erscheint keine "
            "'[Zuschauer][SL] '-Zeile -- der Test waere vakuos.\n" + joined
        )
        assert _SECRET_LATE in joined, (
            "Negativkontrolle gescheitert: der rohe SL-Inhalt fehlt ohne Stop.\n" + joined
        )
        assert "verworfen -- nach Stop eingetroffen" not in joined, (
            "Ohne Stop-Entscheid darf KEINE Verwurf-Zeile erscheinen.\n" + joined
        )


def test_u3b_nach_stop_zeigt_nur_verwurfzeile():
    """Positivfall: nach 'stopped'-Entscheid nur die Verwurf-Zeile, kein roher Inhalt."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = _make_run_with_table(Path(td))
        won, record = core_admission.try_commit_table_decision(
            run_dir, _TABLE_ID, "stopped", reason="test-u3b-regressionswaechter"
        )
        assert won and record.get("decision") == "stopped", (
            "Vorbedingung gescheitert: 'stopped'-Entscheid nicht sauber geschrieben: "
            f"won={won} record={record}"
        )
        readback = core_admission.read_table_decision(run_dir, _TABLE_ID)
        assert isinstance(readback, dict) and readback.get("decision") == "stopped", (
            "Vorbedingung gescheitert: Entscheid-Slot liest 'stopped' nicht zurueck: "
            f"{readback}"
        )

        lines = _spectator_lines(run_dir)
        joined = "\n".join(lines)
        assert "verworfen -- nach Stop eingetroffen" in joined, (
            "R3-U3b gebrochen: nach Stop fehlt die Verwurf-Markierung im "
            "Zuschauer-Feed.\n" + joined
        )
        assert _SECRET_LATE not in joined, (
            "R3-U3b gebrochen: die verworfene SL-Spaetantwort leakt nach Stop "
            "WEITERHIN als Spielinhalt in den Zuschauer-Feed.\n" + joined
        )
        assert not any(line.startswith("[Zuschauer][SL] ") for line in lines), (
            "R3-U3b gebrochen: nach Stop wird weiterhin eine rohe '[Zuschauer][SL] '-"
            "Zeile gedruckt -- die vier Endzustaende werden vermischt.\n" + joined
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
