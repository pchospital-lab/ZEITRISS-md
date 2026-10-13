#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_r11_testroot_classification.py — R11/W38 (ZEITRISS
Terminal UX-1, Reparatur R10-F01, BRIEF-W38.md): belegt die DREI
dokumentierten Teilfaelle der bisher offenen Testroot-Klassifikationsklasse
am ECHTEN `manual_offline_harness.py`-Subprozess (nicht an einer
Testdoppel-Nachbildung), PLUS die bestehende Erhaltung (FRESH_EMPTY,
EXISTING_CONSISTENT, C17-F01, R9-Missing-Marker-HOLD, Szenario-Flag
unberuehrt).

Zustandsmatrix (vollstaendig, s. auch `report/CHECKPOINT-W38.md`):

  FRESH_EMPTY         -- kein Marker UND kein begonnener Produktbestand
                         (JETZT: generische Pruefung aller Dateien unter
                         `--data-dir` ausserhalb `logs/`, s. R10P01) ->
                         rc 0, Erstvorbereitung (Profil+Marker+3 Personas).
  EXISTING_CONSISTENT -- gueltiger Marker + aufloesbarer Leader + ALLE DREI
                         KI-Personas "complete" + (JETZT: R10P02) Community-
                         Bootstrap-Transaktion `already_completed is True`
                         + offene Testfreigabe -> rc 0, KEIN Write, nur
                         echter Client-Start.
  SETUP_HOLD          -- jede andere Kombination, insbesondere:
    R10P01 (NEU): Marker fehlt, aber `run/requests/<id>.json` (echte
      Request-Reservierung via `request_ledger.begin()`) ist bereits
      vorhanden -- vorher UEBERSEHEN, Root galt faelschlich als
      FRESH_EMPTY.
    R10P02 (NEU): gueltiger Marker + alle drei Personas "complete", aber
      die Community-Bootstrap-Transaktion selbst (`bootstrap__final.json`)
      ist (noch) nicht abgeschlossen -- vorher als EXISTING_CONSISTENT
      durchgerutscht, echter Client-Start statt HOLD.
    R10P03 (NEU): ein Persona-State-Lesefehler (`states/<pk>.json` mit
      falschem JSON-Typ) wurde bisher NICHT gefangen -- ungefangener
      Traceback statt eines kontrollierten `"inconsistent"` -> SETUP_HOLD
      rc 3.
    (bestehend) C17-F01: Profil (`lab.status.json`) ohne Marker.
    (bestehend) R9: Marker fehlt auf einem sonst bereits fortgeschriebenen
      Bestand (Registry-Teilnehmer).

Bestandsaufbau/-korruption nutzt ausschliesslich die bestehenden
`_a24_local_support`-Helfer UND die echte `mmo_sim.core.request_ledger`-
Produktfunktion (`begin()`) -- dieselben echten Produktwege wie der
Harness/das Produkt selbst, kein Fake an dieser Grenze. Pure Python, nur
`assert`, echter Exitcode, synthetische Temp-Dirs, Testspieler A/B,
Testfigur A01/B01 (hier nicht benoetigt -- reine Setup-/Klassifikations-
pruefung ohne Spielzuege)."""
from __future__ import annotations

import json
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

from mmo_sim.core import request_ledger  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402

import _a24_local_support as sup  # noqa: E402

HARNESS = _HERE / "manual_offline_harness.py"
AI_PERSONAS = ("sniper", "tech", "medic")
_LEADER_ID_RE = re.compile(r"Deine Teilnehmer-ID: (p[0-9a-f]+)")


def _run_harness(data_dir: Path, stdin_text: str, *, extra_args=(), timeout: int = 60) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "-B", str(HARNESS), "--data-dir", str(data_dir), *extra_args]
    return subprocess.run(cmd, input=stdin_text, cwd=str(_REPO_ROOT), capture_output=True, text=True, timeout=timeout)


def _snapshot(data_dir: Path) -> dict:
    """Voller Hashvergleich UEBER die gesamte relevante Produktdateimenge
    (states/onboarding/catalog/registry/run), NICHT nur ein `save_id`-
    String. `logs/` bewusst ausgeschlossen (reine Harness-Bookkeeping-
    Ablage, keine Spielberechtigung) -- identisches Muster zu
    `test_ux1_r9_setup_hold_classification_2026_10_06.py:_snapshot`."""
    merged = {}
    for name in ("states", "onboarding", "catalog", "registry", "run"):
        for relpath, digest in sup.hash_tree(data_dir / name).items():
            merged[f"{name}/{relpath}"] = digest
    return merged


def _fresh_setup_via_real_harness(data_dir: Path) -> str:
    """Baut einen vollstaendigen FRESH_EMPTY-Bestand ueber den ECHTEN
    Harness-Subprozess (Profil+Marker+3 tischbereite Personas+offene
    Community-Bootstrap-Transaktion) -- liefert `leader_id`."""
    p = _run_harness(data_dir, "")
    assert p.returncode == 0, f"FRESH_EMPTY-Vorlauf fehlgeschlagen: rc={p.returncode}\n{p.stderr[-2000:]}"
    leader_match = _LEADER_ID_RE.search(p.stdout)
    assert leader_match, p.stdout[:500]
    return leader_match.group(1)


# --------------------------------------------------------------------------
# R10P01 -- echte Requestreste zaehlen jetzt als begonnener Bestand
# --------------------------------------------------------------------------

def test_r10p01_reserved_request_alone_is_setup_hold_bytegleich():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        run_dir = data_dir / "run"
        marker_path = data_dir / "harness_participant.json"
        registry_dir = data_dir / "registry"

        # Echte Reservierung ueber den echten Produktweg (`request_ledger.
        # begin()` -- braucht eine bereits bestehende Admission-Autoritaet,
        # s. `core.admission.record_turn_usage(require_authority=True)`).
        # `lab.status.json` wird DANACH wieder entfernt -- isoliert genau
        # den dokumentierten R10P01-Fall: NUR `run/requests/<id>.json`
        # bleibt als Spur eines begonnenen Bestands, kein Profil, kein
        # Marker, keine Registry, keine Personas.
        write_test_profile(run_dir)
        request_id = request_ledger.begin(
            run_dir, role="gm", content="synthetischer Testinhalt",
            reserved_usd=0.01, table_id="local-test", section_id="sec-1",
            turn_idx=0, participant="leader-sim",
        )
        request_path = run_dir / "requests" / f"{request_id}.json"
        assert request_path.is_file(), "request_ledger.begin() muss den Requestdatensatz real anlegen"
        (run_dir / "lab.status.json").unlink()
        assert not (run_dir / "lab.status.json").exists()
        assert not marker_path.exists()
        assert not registry_dir.exists() or not any(registry_dir.glob("participant__*.json"))

        before_request = request_path.read_bytes()
        before_snapshot = _snapshot(data_dir)

        p = _run_harness(data_dir, "")
        assert p.returncode == 3, (
            "ein Root mit nur einer echten reservierten Requestdatei muss SETUP_HOLD "
            f"ausloesen, nicht FRESH_EMPTY: rc={p.returncode}\nstdout={p.stdout[-1000:]}\n"
            f"stderr={p.stderr[-1000:]}"
        )
        assert "SETUP-HOLD" in p.stderr, p.stderr[-1000:]
        assert "begonnenen Produktbestand" in p.stderr, p.stderr[-1000:]

        after_request = request_path.read_bytes()
        assert after_request == before_request, (
            "R10P01-Regression: die reservierte Requestdatei wurde durch den SETUP_HOLD-"
            "Abbruch veraendert (kein Refund/Retry/Ledger-Fix erlaubt)"
        )
        assert _snapshot(data_dir) == before_snapshot, (
            "SETUP_HOLD darf bei einem reinen Request-Rest keine Produktdaten veraendern"
        )
        assert not marker_path.exists(), "kein impliziter Erstvorbereitungs-Shortcut (kein neuer Marker)"
        assert not registry_dir.exists() or not any(registry_dir.glob("participant__*.json")), (
            "kein Profil/keine Gruppe/kein neuer Leader bei einem reinen Request-Rest"
        )
        assert not (run_dir / "lab.status.json").exists(), (
            "SETUP_HOLD darf das entfernte Profil nicht automatisch wiederherstellen"
        )


# --------------------------------------------------------------------------
# R10P02 -- fehlender Community-Abschluss ist jetzt SETUP_HOLD statt EXISTING
# --------------------------------------------------------------------------

def test_r10p02_missing_community_final_marker_is_setup_hold_bytegleich():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        run_dir = data_dir / "run"

        leader_id = _fresh_setup_via_real_harness(data_dir)
        final_path = run_dir / "community" / "bootstrap__final.json"
        assert final_path.is_file(), "FRESH_EMPTY muss die Community-Bootstrap-Transaktion abschliessen"

        # Explizite Testmutation: NUR den Abschlussmarker entfernen -- kein
        # Core-/Store-Write, keine echte Spielhandlung. Die drei Personas
        # (States/Onboarding/Current) bleiben dabei unberuehrt und lesen
        # sich weiterhin als "complete".
        final_path.unlink()
        before = _snapshot(data_dir)

        p = _run_harness(data_dir, "")
        assert p.returncode == 3, (
            "fehlender Community-Abschlussmarker bei sonst vollstaendigem Bestand muss "
            f"SETUP_HOLD ausloesen, nicht EXISTING_CONSISTENT: rc={p.returncode}\n"
            f"stdout={p.stdout[-1000:]}\nstderr={p.stderr[-1000:]}"
        )
        assert "SETUP-HOLD" in p.stderr, p.stderr[-1000:]
        assert "Community-Bootstrap" in p.stderr, p.stderr[-1000:]
        assert f"community-{leader_id}" in p.stderr, p.stderr[-1000:]

        after = _snapshot(data_dir)
        assert after == before, (
            "R10P02-Regression: SETUP_HOLD hat trotz fehlendem Abschlussmarker Produktdaten "
            f"veraendert. Nur in 'after': {set(after) - set(before)}, nur in 'before': "
            f"{set(before) - set(after)}, geaenderte Hashes: "
            f"{[k for k in before if k in after and before[k] != after[k]]}"
        )
        assert not final_path.is_file(), "SETUP_HOLD darf den Abschlussmarker nicht automatisch nachbootstrappen"


# --------------------------------------------------------------------------
# R10P03 -- defekter Persona-State wird jetzt kontrolliert gehalten statt
# mit Traceback abzustuerzen
# --------------------------------------------------------------------------

def test_r10p03_malformed_persona_state_is_setup_hold_no_traceback():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        run_dir = data_dir / "run"
        states_dir = data_dir / "states"

        _fresh_setup_via_real_harness(data_dir)
        tech_state_path = states_dir / "tech.json"
        assert tech_state_path.is_file()
        tech_state_before_corruption = tech_state_path.read_bytes()

        # Explizite Testmutation: `states/tech.json` auf einen strukturell
        # falschen, aber syntaktisch gueltigen JSON-Typ setzen (eine Liste
        # statt eines Objekts) -- genau der dokumentierte R10P03-Fall.
        tech_state_path.write_text("[]", encoding="utf-8")
        before = _snapshot(data_dir)
        logs_dir = data_dir / "logs"
        run_logs_dirs_before = {p.name for p in logs_dir.iterdir() if p.is_dir()}

        p = _run_harness(data_dir, "")
        assert p.returncode == 3, (
            f"defekter Persona-State muss kontrolliert SETUP_HOLD ausloesen: rc={p.returncode}\n"
            f"stdout={p.stdout[-1000:]}\nstderr={p.stderr[-1000:]}"
        )
        assert "SETUP-HOLD" in p.stderr, p.stderr[-1000:]
        assert "Traceback" not in p.stderr, (
            f"R10P03-Regression: ein ungefangener Fehler propagierte bis zum Traceback:\n{p.stderr}"
        )
        assert "tech" in p.stderr, p.stderr[-1000:]

        after = _snapshot(data_dir)
        assert after == before, (
            "SETUP_HOLD darf den defekten Persona-State nicht reparieren/veraendern"
        )
        assert tech_state_path.read_bytes() == b"[]", (
            "kein automatisches Reparieren/Ueberschreiben des defekten Persona-States"
        )

        # Kein Clientstart: `main()` legt die exklusive Lauf-Logablage
        # dieses Prozesses bereits VOR der Klassifikation an
        # (`_next_exclusive_run_logs_dir`), ABER der SETUP-HOLD-Banner
        # selbst (nur `stderr`) nennt diesen Pfad nicht -- `stdout` bleibt
        # bei SETUP_HOLD komplett leer (der Erfolgsbanner mit dem
        # Logordner-Pfad wird erst NACH der Klassifikation gedruckt).
        # Stattdessen: der NEU entstandene `logs/run-NNNN/`-Ordner (Diff
        # gegen den Vorlauf) muss leer sein -- die vier Callbeleg-Dateien
        # werden ausschliesslich NACH einem tatsaechlichen
        # `subprocess.run(scripts/mmo_sim.py)` geschrieben, der bei
        # SETUP_HOLD nie erreicht wird.
        assert p.stdout == "", f"SETUP_HOLD darf keinen Erfolgsbanner drucken: {p.stdout[:500]!r}"
        run_logs_dirs_after = {p2.name for p2 in logs_dir.iterdir() if p2.is_dir()}
        new_run_logs_dirs = sorted(run_logs_dirs_after - run_logs_dirs_before)
        assert len(new_run_logs_dirs) == 1, (
            f"genau EIN neuer exklusiver Lauf-Logordner erwartet: before={run_logs_dirs_before}, "
            f"after={run_logs_dirs_after}"
        )
        run_logs_dir = logs_dir / new_run_logs_dirs[0]
        assert list(run_logs_dir.iterdir()) == [], (
            f"R10P03: SETUP_HOLD darf keine Callbeleg-Dateien schreiben (kein Clientstart): "
            f"{list(run_logs_dir.iterdir())}"
        )
        # states_dir unveraendert ausser der bewussten Testmutation selbst:
        assert tech_state_path.read_bytes() != tech_state_before_corruption


# --------------------------------------------------------------------------
# Erhaltung -- bestehendes R9/R10/C17-F01-Verhalten bleibt unveraendert
# --------------------------------------------------------------------------

def test_preserved_fresh_empty_root_prepares_full_bestand():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        p = _run_harness(data_dir, "")
        assert p.returncode == 0, f"FRESH_EMPTY-Lauf fehlgeschlagen: rc={p.returncode}\n{p.stderr[-2000:]}"

        marker_path = data_dir / "harness_participant.json"
        assert marker_path.is_file(), "FRESH_EMPTY muss den Marker neu anlegen"
        status_path = data_dir / "run" / "lab.status.json"
        assert status_path.is_file(), "write_test_profile() muss nach FRESH_EMPTY gelaufen sein"
        final_path = data_dir / "run" / "community" / "bootstrap__final.json"
        assert final_path.is_file(), "FRESH_EMPTY muss die Community-Bootstrap-Transaktion abschliessen"
        final_data = json.loads(final_path.read_text(encoding="utf-8"))
        assert sorted(final_data.get("personas") or []) == sorted(AI_PERSONAS)


def test_preserved_existing_consistent_restart_keeps_full_bestand_untouched():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        _fresh_setup_via_real_harness(data_dir)
        marker_path = data_dir / "harness_participant.json"
        before_marker = marker_path.read_text(encoding="utf-8")
        before = _snapshot(data_dir)

        p = _run_harness(data_dir, "")
        assert p.returncode == 0, (
            f"passiver EXISTING_CONSISTENT-Neustart fehlgeschlagen: rc={p.returncode}\n{p.stderr[-2000:]}"
        )
        assert marker_path.read_text(encoding="utf-8") == before_marker, (
            "ein passiver Neustart mit gueltigem Marker/vollstaendigem Bestand darf keinen "
            "neuen Leader registrieren"
        )
        after = _snapshot(data_dir)
        assert after == before, (
            "EXISTING_CONSISTENT darf bei einem bereits vollstaendigen Bestand KEINEN "
            f"prep-Write ausloesen. Geaenderte Hashes: "
            f"{[k for k in before if k in after and before[k] != after[k]]}"
        )


def test_preserved_c17f01_profile_without_marker_is_setup_hold():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        run_dir = data_dir / "run"
        write_test_profile(run_dir)
        before = _snapshot(data_dir)

        p = _run_harness(data_dir, "")
        assert p.returncode == 3, (
            f"C17-F01: ein vorhandenes Profil ohne Marker muss SETUP_HOLD bleiben: rc={p.returncode}\n"
            f"{p.stderr[-1000:]}"
        )
        assert "SETUP-HOLD" in p.stderr, p.stderr[-1000:]
        assert _snapshot(data_dir) == before, "C17-F01 darf keine Produktdaten veraendern"
        assert not (data_dir / "harness_participant.json").exists()


def test_preserved_r9_missing_marker_on_registered_leader_is_setup_hold():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        registry_dir = data_dir / "registry"
        sup.register_human(registry_dir, "Testspieler A")
        before = _snapshot(data_dir)

        p = _run_harness(data_dir, "")
        assert p.returncode == 3, (
            f"R9: fehlender Marker auf einem bereits registrierten Leader muss SETUP_HOLD "
            f"bleiben: rc={p.returncode}\n{p.stderr[-1000:]}"
        )
        assert "SETUP-HOLD" in p.stderr, p.stderr[-1000:]
        assert _snapshot(data_dir) == before, "R9: darf keine Produktdaten veraendern"
        assert not (data_dir / "harness_participant.json").exists()


def test_preserved_reject_scenario_argument_unaffected_by_classification_fix():
    """Kurzer Beleg, dass das `--scenario reject`-Argumentparsing UND die
    FRESH_EMPTY-Vorbereitung von den drei R10-F01-Fixes unberuehrt bleiben
    (Klassifikation ist Scenario-unabhaengig) -- KEIN voller Gruppen-
    Spielzug (teuer, bereits an anderer Stelle, z.B. A24/G6, tief
    abgedeckt), nur der Start bis zum echten Client mit leerem stdin."""
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        p = _run_harness(data_dir, "", extra_args=("--scenario", "reject", "--reject-persona-key", "tech"))
        assert p.returncode == 0, f"reject-Szenario-Start fehlgeschlagen: rc={p.returncode}\n{p.stderr[-2000:]}"
        marker_path = data_dir / "harness_participant.json"
        assert marker_path.is_file(), "FRESH_EMPTY muss auch mit --scenario reject vollstaendig vorbereiten"
        final_path = data_dir / "run" / "community" / "bootstrap__final.json"
        assert final_path.is_file()


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
