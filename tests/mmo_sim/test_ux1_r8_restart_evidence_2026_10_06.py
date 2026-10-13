#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_r8_restart_evidence_2026_10_06.py — R7/W32
(ZEITRISS Terminal UX-1, Reparatur R8, BRIEF-W32.md): belegt F01/F02 am
ECHTEN `manual_offline_harness.py`-Subprozess (nicht an einer
Testdoppel-Nachbildung).

Befund (GENERALREVIEW-R7.md §3/§4, `evidence/runs/probe_harness_restart/
observation.json`): der Harness rief bislang bei JEDEM Start unbedingt
`sup.make_ready` fuer sniper/tech/medic auf -- ein ECHT ueber
`core.store.publish_current_save` fortgeschrittener KI-`Current` wurde
dabei bei einem passiven Neustart desselben `--data-dir` wieder auf die
Anfangsfixtur zurueckgesetzt, waehrend der normale `scripts/mmo_sim.py`-
Start ihn erhaelt. Ausserdem schrieben die vier `logs/*.jsonl` am
Prozessende unbedingt per `write_text` neu -- ein Folgeprozess (auch ein
Null-Call-Neustart) vernichtete die vorigen Callbelege.

Fix (`manual_offline_harness.py`, s. dortige R7/W32-Docstring-Notiz):
Erst-/Resume-Trennung ueber den bestehenden `harness_participant.json`-
Marker + reine Lesefunktion `_ai_persona_state()` (komplett/absent/
inconsistent); exklusive Pro-Prozess-Logablage `logs/run-NNNN/`.

Drei Szenarien:

  test_f01_positive_progressed_ai_save_survives_restart_and_normal_start:
  frische Erstvorbereitung macht alle drei KI-Personas tischbereit; ein
  ECHT publizierter fortgeschrittener `medic`-Save bleibt sowohl nach
  einem normalen Produktstart (Positivkontrolle) ALS AUCH nach einem
  zweiten, leeren Harness-Neustart exakt erhalten.

  test_f01_hold_on_incomplete_contradictory_ai_bestand: ein kuenstlich
  unvollstaendiger/widersprechender KI-Bestand (Current-Save + Onboarding-
  Abschluss vorhanden, zugehoeriger Persona-State fehlt) fuehrt zu einem
  klaren Setup-HOLD (rc=3, "SETUP-HOLD" auf stderr) statt stillem
  Neuanlegen/Reparieren.

  test_f02_previous_calllogs_survive_and_null_call_restart_is_evidenced:
  die Callbelege von Prozess 1 bleiben nach einem Null-Call-Neustart
  (Prozess 2) bytegleich erhalten; der Null-Call-Lauf selbst ist
  eigenstaendig (eigener Ordner, eigene -- hier leere -- Datei) belegt.

Pure Python, nur `assert`, echter Exitcode, synthetische Temp-Dirs, ECHTE
eigenstaendige Subprozesse von `manual_offline_harness.py`/
`scripts/mmo_sim.py` selbst."""
from __future__ import annotations

import copy
import re
import subprocess
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

from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402

import _a24_local_support as sup  # noqa: E402

HARNESS = _HERE / "manual_offline_harness.py"
_LEADER_ID_RE = re.compile(r"Deine Teilnehmer-ID: (p[0-9a-f]+)")


def _run_harness(data_dir: Path, stdin_text: str, *, extra_args=(), timeout: int = 150) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "-B", str(HARNESS), "--data-dir", str(data_dir), *extra_args]
    return subprocess.run(cmd, input=stdin_text, cwd=str(_REPO_ROOT), capture_output=True, text=True, timeout=timeout)


def test_f01_positive_progressed_ai_save_survives_restart_and_normal_start():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)

        # Prozess 1: frische Erstvorbereitung (noch kein `--data-dir`
        # wiederverwendet) -- Testfigur A01 echt ueber '[n]', die drei
        # KI-Personas werden dabei ueber den normalen Produktweg (R7/W30)
        # tischbereit.
        stdin1 = "n\nNeutrale Testausruestung Testfigur A01.\n"
        p1 = _run_harness(data_dir, stdin1)
        assert p1.returncode == 0, f"Prozess 1 fehlgeschlagen: rc={p1.returncode}\n{p1.stderr[-2000:]}"
        assert "Erschaffung abgeschlossen:" in p1.stdout, p1.stdout[-1500:]
        leader_match = _LEADER_ID_RE.search(p1.stdout)
        assert leader_match, p1.stdout[:500]
        leader_id = leader_match.group(1)

        run_dir = data_dir / "run"
        states_dir = data_dir / "states"
        ps_store = PersonaStateStore(schema_path=sup.SCHEMA)

        # Frische Erstvorbereitung belegt: alle drei KI-Personas haben nach
        # Prozess 1 bereits einen gueltigen Current-Save (Fixture-Stand) --
        # F01-Fix darf die bisherige Erstvorbereitung NICHT verhindern.
        for pk in ("sniper", "tech", "medic"):
            fixture_save = core_store.load_current_save_or_raise(run_dir, pk, ps_store, states_dir=states_dir)
            assert fixture_save is not None, f"frische Erstvorbereitung muss {pk!r} tischbereit machen"

        # Fortgeschrittenen synthetischen Save fuer 'medic' ECHT ueber den
        # bestehenden Store publizieren -- kein direktes Ledger-/Lock-Schreiben.
        old = core_store.load_current_save_or_raise(run_dir, "medic", ps_store, states_dir=states_dir)
        progressed = copy.deepcopy(old)
        progressed["save_id"] = "TEST-UX1-R8-PROGRESSED-MEDIC-SAVE-ONLY"
        progressed["characters"][0]["level"] = 7
        progressed["_r8_progress_marker"] = "PROGRESS_MUST_SURVIVE_RESTART"
        core_store.publish_current_save(run_dir, "medic", progressed, ps_store, states_dir)
        bound = core_store.load_current_save_or_raise(run_dir, "medic", ps_store, states_dir=states_dir)
        assert bound == progressed, "echte Publikation des fortgeschrittenen Saves fehlgeschlagen"

        # Positivkontrolle: der normale, echte Produktstart (kein Harness,
        # keine Loopback-Fakes) erhaelt den fortgeschrittenen Stand exakt.
        normal = subprocess.run(
            [sys.executable, "-B", str(sup.MMO_SIM), "--data-dir", str(data_dir), "--participant", leader_id],
            input="", text=True, capture_output=True, timeout=30, cwd=str(_REPO_ROOT),
        )
        assert normal.returncode == 0, (
            f"normaler Produktstart fehlgeschlagen: rc={normal.returncode}\n{normal.stderr[-2000:]}"
        )
        after_normal = core_store.load_current_save_or_raise(run_dir, "medic", ps_store, states_dir=states_dir)
        assert after_normal == progressed, (
            f"Positivkontrolle verletzt: normaler Produktstart hat den Save veraendert: {after_normal}"
        )

        # Kernbeleg F01: ein zweiter, leerer Harness-Neustart (passiver
        # Neustart desselben --data-dir, KEINE Spielerhandlung) darf den
        # fortgeschrittenen Stand NICHT mehr auf die Fixtur zuruecksetzen.
        p2 = _run_harness(data_dir, "")
        assert p2.returncode == 0, f"Prozess 2 (Neustart) fehlgeschlagen: rc={p2.returncode}\n{p2.stderr[-2000:]}"
        after_restart = core_store.load_current_save_or_raise(run_dir, "medic", ps_store, states_dir=states_dir)
        assert after_restart == progressed, (
            f"F01-Regression: Harness-Neustart hat den fortgeschrittenen KI-Save zurueckgesetzt: {after_restart}"
        )
        assert after_restart.get("save_id") != "fixture-medic-initial-001"

        # sniper/tech wurden nie progressed -- bleiben unberuehrt auf dem
        # unveraenderten Fixture-Stand (kein unbeabsichtigtes Zweit-Publish).
        for pk in ("sniper", "tech"):
            still_fixture = core_store.load_current_save_or_raise(run_dir, pk, ps_store, states_dir=states_dir)
            assert still_fixture["save_id"] == f"fixture-{pk}-initial-001", still_fixture


def test_f01_hold_on_incomplete_contradictory_ai_bestand():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        stdin1 = "n\nNeutrale Testausruestung Testfigur B01.\n"
        p1 = _run_harness(data_dir, stdin1)
        assert p1.returncode == 0, f"Prozess 1 fehlgeschlagen: rc={p1.returncode}\n{p1.stderr[-2000:]}"

        # Kuenstlich widerspruechlichen Bestand fuer 'medic' erzeugen:
        # Current-Save UND Onboarding-Abschluss sind (aus Prozess 1) bereits
        # vorhanden, der zugehoerige Persona-State wird ENTFERNT (simuliert
        # z.B. einen unvollstaendig kopierten/beschaedigten Testroot) --
        # kein Core-/Store-Write, nur Entfernen einer bereits vom normalen
        # Produktweg geschriebenen Testdatei.
        states_dir = data_dir / "states"
        medic_state_path = states_dir / "medic.json"
        assert medic_state_path.is_file(), "Vorbedingung: Persona-State muss nach Prozess 1 existieren"
        medic_state_path.unlink()

        p2 = _run_harness(data_dir, "")
        assert p2.returncode == 3, (
            "ein widerspruechlicher KI-Bestand muss zu einem klaren Setup-HOLD (rc=3) fuehren, "
            f"nicht zu stillem Reparieren/Weiterlaufen: rc={p2.returncode}\n"
            f"stdout={p2.stdout[-1000:]}\nstderr={p2.stderr[-1000:]}"
        )
        assert "SETUP-HOLD" in p2.stderr, p2.stderr[-1000:]
        assert "medic" in p2.stderr, p2.stderr[-1000:]
        # Kein stilles Auffuellen: der fehlende Persona-State wurde NICHT
        # automatisch neu angelegt.
        assert not medic_state_path.is_file()


def test_f02_previous_calllogs_survive_and_null_call_restart_is_evidenced():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        stdin1 = "n\nNeutrale Testausruestung Testfigur A01.\n"
        p1 = _run_harness(data_dir, stdin1)
        assert p1.returncode == 0, f"Prozess 1 fehlgeschlagen: rc={p1.returncode}\n{p1.stderr[-2000:]}"

        run1_dir = data_dir / "logs" / "run-0001"
        creation_log = run1_dir / "gm_creation_calls.jsonl"
        assert creation_log.is_file(), "Prozess 1 muss seine eigenen Callbelege ablegen"
        before_bytes = creation_log.read_bytes()
        assert len(before_bytes.splitlines()) >= 1, "echte Erschaffung muss mindestens einen GM-Call belegen"

        # Null-Call-Neustart: leere Eingabe, KEINE weitere Erschaffung/
        # Einladung -- der GM-Double bekommt in diesem Prozess keinen Call.
        p2 = _run_harness(data_dir, "")
        assert p2.returncode == 0, f"Prozess 2 (Null-Call-Neustart) fehlgeschlagen: rc={p2.returncode}\n{p2.stderr[-2000:]}"

        # F02-Kernbeleg: der Logordner/die Logdatei aus Prozess 1 bleibt
        # BYTEGLEICH -- Prozess 2 hat sie nie wieder geoeffnet.
        assert creation_log.read_bytes() == before_bytes, (
            "F02-Regression: ein Folgeprozess hat die Callbelege eines frueheren Laufs veraendert"
        )

        # Der Null-Call-Lauf ist EIGENSTAENDIG belegt: eigener Ordner, eigene
        # (hier leere, aber vorhandene) Datei -- kein Vermischen mit run-0001,
        # kein leeres write_text ueber die Vergangenheit.
        run2_dir = data_dir / "logs" / "run-0002"
        assert run2_dir != run1_dir
        run2_creation_log = run2_dir / "gm_creation_calls.jsonl"
        assert run2_creation_log.is_file(), "auch ein Null-Call-Lauf muss eine eigene Belegdatei bekommen"
        assert run2_creation_log.read_text(encoding="utf-8") == "", (
            f"Null-Call-Lauf darf keine erfundenen/fremden Zeilen enthalten: {run2_creation_log.read_text()!r}"
        )
        for name in ("gm_gameplay_calls.jsonl", "persona_decision_calls.jsonl", "persona_reflection_calls.jsonl"):
            assert (run1_dir / name).is_file(), name
            assert (run2_dir / name).is_file(), name


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
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
