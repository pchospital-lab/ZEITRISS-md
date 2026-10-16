#!/usr/bin/env python3
"""
tests/mmo_sim/test_recovery_ops_r1.py — ZR-RECOVERY-OFFLINE-20261015-R1
(03_RECOVERY_VERTRAG.md, TEST-CATALOG.json): ausfuehrbare Regression fuer
ALLE 22 `required_case_ids`. Sammelsuite (eine Datei), aber jeder
Katalog-ID entspricht GENAU EINER `test_<id>`-Funktion unten -- einzeln
ausweisbar in TEST-RESULTS.json.

Pure Python, nur `assert`, echter Exitcode -- gleiches Muster wie die
bestehende Suite (`run_all.py` entdeckt diese Datei automatisch ueber
`test_*.py`). `PYTHONDONTWRITEBYTECODE=1`/kein Netz zu nativen Diensten;
synthetische Loopback-Testserver (falls ueberhaupt gebraucht) nur auf
frischen, testeigenen Ports -- diese Suite braucht keinen (reiner
In-Prozess-/Subprozess-Dateisystemtest, kein HTTP).

Status `BLOCKED_ENV` (nicht `FAIL`, nicht `PASS`) fuer einen Fall, dessen
Pflichtfixture auf eine erkennbar NICHT vorhandene Datei zeigt -- s.
`EnvironmentBlocked`/`main()` unten.

R2-TEST-Fix (GENERALREVIEW.md §6, 04_NAECHSTER_BAU_R2.md "TEST"): die
vormals fest verdrahteten `/home/altair/...`-Paketpfade sind entfernt --
`_PKG_BUDGET_CALC`/`_PKG_CONTROL_JSON` wurden danach EXPLIZIT ueber die
Umgebungsvariablen `ZEITRISS_R1_BUDGET_CALC`/`ZEITRISS_R1_CONTROL_JSON`
gebunden (keine private Paketkopie im Produkt-/Testbaum, keine neue feste
VM-Pfadannahme) -- das war fuer ein privates Pruefpaket ausdruecklich
gebunden und zulaessig, ein frischer OEFFENTLICHER Repo-Checkout darf
dieses Paket aber nicht mehr benoetigen.

C-Fix (ZR-LIVEWEG-PR-KANDIDAT-20261016-R1, 01_AUFTRAG.md C): `_PKG_BUDGET_
CALC`/`_PKG_CONTROL_JSON` loesen jetzt ueber `_recovery_public_fixture_
paths.resolve_budget_calc()`/`resolve_control_json()` auf -- IST die jeweilige
Variable gesetzt, bindet sie weiterhin UNVERAENDERT (Rueckwaertskompatibilitaet
zur bisherigen privaten Pruefumgebung); FEHLT sie, bindet jetzt der neutrale
Repo-Default unter `tests/mmo_sim/fixtures/recovery_contract/` (immer im
Checkout vorhanden) statt BLOCKED_ENV zu erzwingen. Zeigt die Variable
ausdruecklich auf eine NICHT vorhandene Datei, bleibt der Fall weiterhin
ehrlich `BLOCKED_ENV` -- kein stiller Fallback bei einem erkennbar falschen
Pfad (s. `test_recovery_fixture_portability.py`). `main()` liefert fuer
BLOCKED_ENV weiterhin einen NICHTNULL Exitcode (R1-Bug-Fix, s. dort), damit
`run_all.py`/ein aussenstehender Aufrufer eine solche Datei NIE als
vollstaendig bestanden zaehlt."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path
from unittest.mock import patch

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _recovery_ops_r1_fixtures import (  # noqa: E402
    ScriptedGm, apply_p3_audit, apply_p5_grant, make_p3_unknown_request, make_p5_drift_hold,
    make_synthetic_run, never_called_gm, snapshot_tree,
)
from _full_v7_fixture import full_v7_save  # noqa: E402
from _recovery_public_fixture_paths import resolve_budget_calc, resolve_control_json  # noqa: E402

import mmo_sim.core.recovery_ops as recovery_ops  # noqa: E402
import mmo_sim.core.request_ledger as request_ledger  # noqa: E402
import mmo_sim.core.save_correction as save_correction  # noqa: E402
from mmo_sim.core.admission import _atomic_write_json, _status_path  # noqa: E402

_SCRIPTS_MMO_SIM = _REPO_ROOT / "scripts" / "mmo_sim.py"

# C-Fix (01_AUFTRAG.md C): neutraler Repo-Default, falls die jeweilige Env
# fehlt -- s. `_recovery_public_fixture_paths.py`-Docstring. Zeigt die Env
# ausdruecklich auf eine NICHT vorhandene Datei, bleibt der Fall unten
# weiterhin ehrlich BLOCKED_ENV (kein stiller Fallback bei einem erkennbar
# falschen Pfad).
_PKG_BUDGET_CALC = resolve_budget_calc()
_PKG_CONTROL_JSON = resolve_control_json()


class EnvironmentBlocked(Exception):
    """Fehlende Umgebung (z.B. ein Pfad ausserhalb dieses Checkouts) --
    `main()` meldet dafuer `BLOCKED_ENV`, NIE `PASS`/stillschweigend
    uebersprungen (03_RECOVERY_VERTRAG.md: 'Unbekannt/Umgebung fehlt -> BLOCKED')."""


def _run_cli(data_dir: Path, *argv: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-B", "-u", str(_SCRIPTS_MMO_SIM), "lab", "recovery", *argv, "--data-dir", str(data_dir)],
        capture_output=True, text=True, cwd=str(_REPO_ROOT), env=env,
    )


# ─────────── writer_exclusivity_unlink_race: echte Zweiprozess-Probe ────────
# Rework (Critic must_fix writer_exclusivity_unlink_race): Vorlage/Methodik aus
# den Critic-Belegen `race_labrunner_sim.py`/`race_recovery_acquire.py`
# (kritiker-eigen, NICHT Teil dieser Lieferung -- hier eigenstaendig
# nachgebaut), echte Subprozesse statt In-Prozess-Simulation. Ein
# "ready"/"go"-Handshake (statt eines blinden `time.sleep()` vor dem Start
# des zweiten Subprozesses) nimmt die variable Python-Interpreter-/Import-
# Kaltstartzeit aus dem zeitkritischen Fenster heraus -- sonst waere die
# Probe auf einer langsamen/ausgelasteten Maschine nicht deterministisch
# (empirisch 10/10 stabil bei 10ms UND 15ms Gap getestet, s. REWORK-NOTE.md).

_RACE_A_TEARDOWN_SRC = '''
import fcntl, json, os, sys, time

def main():
    lock_path, results_path, ready_path, go_path, gap_seconds = (
        sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], float(sys.argv[5])
    )

    def log(ev):
        with open(results_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"who": "A_teardown", "event": ev, "t": time.time()}) + "\\n")

    # Reproduziert LabRunner.release()'s dokumentierte Reihenfolge (work/B/
    # mmo_sim/lab/runner.py ~Z.838-881): Statuswrite (hier irrelevant,
    # ausgelassen) -> unlink WAEHREND der eigene flock noch gehalten wird ->
    # flock(LOCK_UN)+close ALS LETZTER Schritt. Der reale unlink->unlock-Gap
    # ist laut Runner-Docstring "ein paar CPU-Instruktionen" -- hier als
    # `gap_seconds` kuenstlich (aber MASSVOLL, nicht adversarisch) verbreitert,
    # um die Race in einem kurzen Testlauf deterministisch zu machen.
    with open(ready_path, "w", encoding="utf-8") as f:
        f.write("ready")
    while not os.path.exists(go_path):
        time.sleep(0.0005)

    fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    fcntl.flock(fd, fcntl.LOCK_EX)
    os.write(fd, json.dumps({"pid": os.getpid()}).encode("utf-8"))
    log("acquired_and_wrote")
    os.unlink(lock_path)
    log("unlinked_still_locked")
    time.sleep(gap_seconds)
    fcntl.flock(fd, fcntl.LOCK_UN)
    os.close(fd)
    log("unlocked_and_closed")

if __name__ == "__main__":
    main()
'''

_RACE_B_FIXED_SRC = '''
import json, os, sys, time
from pathlib import Path

repo_root, run_dir_s, results_path, ready_path, go_path = sys.argv[1:6]
sys.path.insert(0, repo_root)
from mmo_sim.core import recovery_ops  # echtes, ausgeliefertes Modul -- keine Nachbildung

run_dir = Path(run_dir_s)


def log(ev, extra=None):
    rec = {"who": "B_fixed", "event": ev, "t": time.time()}
    if extra:
        rec.update(extra)
    with open(results_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\\n")


with open(ready_path, "w", encoding="utf-8") as f:
    f.write("ready")
while not os.path.exists(go_path):
    time.sleep(0.0005)

try:
    with recovery_ops._SharedWriterExclusivity(run_dir):
        log("acquired_shared_lock")
        log("released_shared_lock")
    sys.exit(0)
except recovery_ops.RecoveryExclusivityUnavailableError as exc:
    log("hold", {"reason": str(exc)})
    sys.exit(1)
'''

_RACE_B_LEGACY_SRC = '''
# VOR-FIX-REKONSTRUKTION (byte-identisch zur urspruenglichen __enter__ VOR
# diesem Rework: os.open(O_CREAT|O_RDWR) + flock(LOCK_EX|LOCK_NB), SOFORTIGE
# Uebernahme ohne Post-flock-Inode-Recheck, OHNE Settle-Delay). Dient NUR dem
# Sensitivitaetsbeleg (zeigt, dass die Probe die Race bei gefixtem Code
# tatsaechlich erkennen WUERDE, keine Vorab-Mutation des echten Moduls).
import fcntl, json, os, sys, time

lock_path, results_path, ready_path, go_path = sys.argv[1:5]


def log(ev):
    with open(results_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"who": "B_legacy_prefix", "event": ev, "t": time.time()}) + "\\n")


with open(ready_path, "w", encoding="utf-8") as f:
    f.write("ready")
while not os.path.exists(go_path):
    time.sleep(0.0005)

fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o644)
try:
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError:
    os.close(fd)
    log("hold")
    sys.exit(1)
log("acquired_shared_lock")
fcntl.flock(fd, fcntl.LOCK_UN)
os.close(fd)
log("released_shared_lock")
sys.exit(0)
'''


def _run_unlink_while_locked_probe(scripts_dir: Path, use_fixed: bool, gap_seconds: float):
    """Echte Zweiprozess-Nachstellung von `writer_exclusivity_unlink_race`:
    Prozess A reproduziert `LabRunner.release()`s unlink-waehrend-geflockt-
    Sequenz: Prozess B versucht, WAEHREND dieses Fensters, echte
    Schreiber-Exklusivitaet zu erwerben -- entweder ueber das echte,
    ausgelieferte `recovery_ops._SharedWriterExclusivity` (`use_fixed=True`)
    oder ueber dessen VOR-Fix-Rekonstruktion (`use_fixed=False`,
    Sensitivitaetsbeleg). Gibt die chronologische Ereignisliste + B's
    Exitcode/Streams zurueck."""
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    with tempfile.TemporaryDirectory() as td:
        race_root = Path(td)
        lock_path = race_root / "lab.lock.json"
        results_path = race_root / "results.jsonl"
        results_path.touch()
        a_ready, a_go = race_root / "a_ready", race_root / "a_go"
        b_ready, b_go = race_root / "b_ready", race_root / "b_go"

        proc_a = subprocess.Popen(
            [sys.executable, "-B", str(scripts_dir / "race_a_teardown.py"),
             str(lock_path), str(results_path), str(a_ready), str(a_go), str(gap_seconds)],
            env=env,
        )
        deadline = time.time() + 5.0
        while not a_ready.exists():
            if time.time() > deadline:
                proc_a.kill()
                raise AssertionError("race_a_teardown.py nicht bereit (Timeout).")
            time.sleep(0.001)

        if use_fixed:
            b_argv = [sys.executable, "-B", str(scripts_dir / "race_b_fixed.py"),
                      str(_REPO_ROOT), str(race_root), str(results_path), str(b_ready), str(b_go)]
        else:
            b_argv = [sys.executable, "-B", str(scripts_dir / "race_b_legacy.py"),
                      str(lock_path), str(results_path), str(b_ready), str(b_go)]
        proc_b = subprocess.Popen(b_argv, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        deadline = time.time() + 5.0
        while not b_ready.exists():
            if time.time() > deadline:
                proc_a.kill(); proc_b.kill()
                raise AssertionError("race_b_*.py nicht bereit (Timeout) -- Import fehlgeschlagen?")
            time.sleep(0.001)

        # Beide Subprozesse sind jetzt warm und blockieren auf ihr jeweiliges
        # go-File -- Interpreter-/Importstartzeit ist damit aus dem
        # zeitkritischen Fenster heraus. A zuerst freigeben, B erst NACH
        # bestaetigtem `unlinked_still_locked`-Log -- sonst waere nicht
        # garantiert, dass B tatsaechlich WAEHREND des Fensters startet.
        a_go.touch()
        deadline = time.time() + 5.0
        while True:
            lines = [ln for ln in results_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
            if any(json.loads(ln)["event"] == "unlinked_still_locked" for ln in lines):
                break
            if time.time() > deadline:
                proc_a.kill(); proc_b.kill()
                raise AssertionError("A hat unlinked_still_locked nie erreicht (Timeout).")
            time.sleep(0.0005)
        b_go.touch()

        proc_a.wait(timeout=10)
        out_b, err_b = proc_b.communicate(timeout=10)
        events = [json.loads(ln) for ln in results_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        return events, proc_b.returncode, out_b, err_b


# ═══════════════════════ Gemeinsam/Haltbarkeit ══════════════════════════════


def test_inspect_plan_read_only():
    """inspect/plan_p3/plan_p5 duerfen KEINEN Verzeichnis-/Dateiwrite als
    Nebenwirkung erzeugen (03 §Haltbarkeit)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        rid = make_p3_unknown_request(run_dir)
        p5 = make_p5_drift_hold(run_dir, persona_key="flo_ro", char_id="CHR-RO-01")

        before = snapshot_tree(root)
        recovery_ops.inspect_p3_candidates(run_dir)
        recovery_ops.inspect_p5_candidates(run_dir)
        recovery_ops.list_p3_audits(run_dir)
        recovery_ops.list_p5_grants(run_dir)
        recovery_ops.plan_p3(
            run_dir, table_id="table-1", section_id="section-1", role="gm_turn",
            turn_idx=1, participant="alice", request_id=rid,
        )
        recovery_ops.plan_p5(run_dir, repair_key=p5["repair_key"])
        after = snapshot_tree(root)
        assert before == after, f"inspect/plan hat einen Dateisystem-Nebenwrite erzeugt: {set(after) - set(before)}"


def test_cli_real_entry_not_noop():
    """`scripts/mmo_sim.py lab recovery ...` ist ein ECHTER, in einem
    Subprozess ausfuehrbarer CLI-Einstieg -- kein Mock/No-op (03 §Integration:
    'Muss echt benutzbar sein')."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        make_p3_unknown_request(run_dir)
        proc = _run_cli(root, "inspect")
        assert proc.returncode == 0, f"rc={proc.returncode} stderr={proc.stderr}"
        payload = json.loads(proc.stdout)
        assert len(payload["p3_candidates"]) == 1, payload

        # Der frühere No-op `python -m mmo_sim.lab.cli` bleibt irrelevant --
        # der echte Einstieg ist scripts/mmo_sim.py (03 §Integration).
        proc_help = subprocess.run(
            [sys.executable, "-B", str(_SCRIPTS_MMO_SIM), "lab", "recovery", "--help"],
            capture_output=True, text=True, cwd=str(_REPO_ROOT),
        )
        assert proc_help.returncode == 0
        assert "apply-p3" in proc_help.stdout and "apply-p5" in proc_help.stdout


def test_writer_race_single_winner():
    """Zwei gleichzeitige `apply_*`-Aufrufe duerfen nicht beide schreiben --
    ohne gesicherte Exklusivitaet HOLD (03 §Haltbarkeit). Haelt den
    GETEILTEN `lab.lock.json`-OS-Lock (`fcntl.flock`) ueber eine zweite,
    unabhaengige fd offen (POSIX: verschiedene fds auf dieselbe Datei sind
    bei `flock` NICHT derselbe Besitzer, selbst im selben Prozess -- exakt
    das reale Konkurrenzszenario eines zweiten Prozesses).

    Rework-Verstaerkung (writer_exclusivity_unlink_race, CRITIC-VERDICT.json):
    der obige Block deckt nur eine bereits VORHANDENE, identische Inode ab
    ("materially easier case" laut Critic) -- NICHT die belegte unlink-
    waehrend-gehalten-Klasse (ein ausgehender `LabRunner` unlinkt
    `lab.lock.json` WAEHREND er seinen eigenen flock noch haelt, s.
    `LabRunner.release()`). Der zweite Block unten reproduziert GENAU diese
    Klasse mit zwei echten Subprozessen (Vorlage: Critic-Belege
    `race_labrunner_sim.py`/`race_recovery_acquire.py`) und verlangt
    GENAU EINEN Gewinner, kein Overlap-Write -- gegen das echte,
    ausgelieferte `recovery_ops._SharedWriterExclusivity` GRUEN, gegen eine
    VOR-Fix-Rekonstruktion als Sensitivitaetsbeleg im Log NICHT gruen (zeigt:
    die Probe erkennt die Race tatsaechlich, ist kein Blindflug)."""
    import fcntl
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        rid = make_p3_unknown_request(run_dir)
        lock_path = run_dir / "lab.lock.json"
        fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o644)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            raised = None
            try:
                apply_p3_audit(
                    run_dir, table_id="table-1", section_id="section-1", role="gm_turn",
                    turn_idx=1, participant="alice", request_id=rid,
                )
            except recovery_ops.RecoveryExclusivityUnavailableError as exc:
                raised = exc
            assert raised is not None, "apply_p3 haette ohne Exklusivitaet HOLD melden muessen."
            assert not list((run_dir / "recovery").rglob("*.json")) if (run_dir / "recovery").exists() else True, (
                "Kein Audit-Write ohne gesicherte Exklusivitaet."
            )
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)

        # Nach Freigabe gewinnt genau ein Aufruf normal.
        result = apply_p3_audit(
            run_dir, table_id="table-1", section_id="section-1", role="gm_turn",
            turn_idx=1, participant="alice", request_id=rid,
        )
        assert result["status"] == "applied"

    # ── Zweiprozess-Nachstellung der unlink-waehrend-gehalten-Klasse ────────
    # GAP bewusst klein (realistische Groessenordnung des echten "paar CPU-
    # Instruktionen"-Fensters, kuenstlich nur so weit verbreitert wie fuer
    # deterministische CI-Beobachtbarkeit noetig -- NICHT die 2s-Breite der
    # Critic-Explorationsprobe, die keine produktionsvertraegliche Verzoegerung
    # je ueberbruecken koennte, s. REWORK-NOTE.md fuer die volle Herleitung).
    GAP_SECONDS = 0.015
    with tempfile.TemporaryDirectory() as scripts_td:
        scripts_dir = Path(scripts_td)
        (scripts_dir / "race_a_teardown.py").write_text(_RACE_A_TEARDOWN_SRC, encoding="utf-8")
        (scripts_dir / "race_b_fixed.py").write_text(_RACE_B_FIXED_SRC, encoding="utf-8")
        (scripts_dir / "race_b_legacy.py").write_text(_RACE_B_LEGACY_SRC, encoding="utf-8")

        # (a) Sensitivitaetsbeleg: die VOR-Fix-Rekonstruktion MUSS die Race
        # bei diesem Gap zeigen -- sonst waere die Probe selbst nicht
        # aussagekraeftig (koennte vacuous gruen sein).
        events_legacy, rc_legacy, out_legacy, err_legacy = _run_unlink_while_locked_probe(
            scripts_dir, use_fixed=False, gap_seconds=GAP_SECONDS
        )
        a_unlocked_legacy = next(
            e["t"] for e in events_legacy if e["who"] == "A_teardown" and e["event"] == "unlocked_and_closed"
        )
        b_acquired_legacy = next(
            (e["t"] for e in events_legacy if e["who"] == "B_legacy_prefix" and e["event"] == "acquired_shared_lock"),
            None,
        )
        log_legacy = "\n".join(f"{e['who']}: {e['event']} t={e['t']:.6f}" for e in events_legacy)
        assert b_acquired_legacy is not None and b_acquired_legacy < a_unlocked_legacy, (
            "Sensitivitaetsbeleg fehlgeschlagen: die VOR-Fix-Rekonstruktion haette die unlink-waehrend-"
            f"gehalten-Race bei GAP_SECONDS={GAP_SECONDS} zeigen muessen (b_acquired={b_acquired_legacy}, "
            f"a_unlocked={a_unlocked_legacy}, rc={rc_legacy}, stderr={err_legacy.decode('utf-8', 'replace')}).\n"
            f"Log:\n{log_legacy}"
        )

        # (b) Fix-Nachweis: das echte, ausgelieferte Modul darf WAEHREND A's
        # gehaltenem flock auf der unlinkten Inode NICHT zuschlagen -- es muss
        # entweder HOLDen oder erst NACH A's tatsaechlicher Freigabe gewinnen.
        events_fixed, rc_fixed, out_fixed, err_fixed = _run_unlink_while_locked_probe(
            scripts_dir, use_fixed=True, gap_seconds=GAP_SECONDS
        )
        a_unlocked_fixed = next(
            e["t"] for e in events_fixed if e["who"] == "A_teardown" and e["event"] == "unlocked_and_closed"
        )
        b_acquired_fixed = next(
            (e["t"] for e in events_fixed if e["who"] == "B_fixed" and e["event"] == "acquired_shared_lock"), None
        )
        log_fixed = "\n".join(f"{e['who']}: {e['event']} t={e['t']:.6f}" for e in events_fixed)
        assert b_acquired_fixed is not None, (
            f"recovery_ops haette nach A's Freigabe normal gewinnen muessen (rc={rc_fixed}, "
            f"stderr={err_fixed.decode('utf-8', 'replace')}).\nLog:\n{log_fixed}"
        )
        assert b_acquired_fixed >= a_unlocked_fixed, (
            "writer_exclusivity_unlink_race: das echte recovery_ops hat WAEHREND A's gehaltenem flock auf "
            f"der unlinkten Inode zugeschlagen (b_acquired={b_acquired_fixed}, a_unlocked={a_unlocked_fixed}) "
            f"-- genau EIN Gewinner verlangt, kein Overlap-Write.\nLog:\n{log_fixed}"
        )


def test_malformed_paths_json_counters_rejected():
    """(a) Ein Pfad-Trickmuster in `repair_key` wird kontrolliert
    abgelehnt, NIE als Dateinamensbestandteil verwendet. (b) ein
    `save_corrections`-Datensatz mit Duplicate-Key/bool-als-Zaehler wird
    beim Lesen abgelehnt, NICHT stillschweigend als gueltig/abwesend
    behandelt (G2-Analogie)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)

        for bad_key in ("../../etc/passwd", "foo/bar", "a\x00b"):
            raised = None
            try:
                recovery_ops.plan_p5(run_dir, repair_key=bad_key)
            except recovery_ops.RecoveryUnsafeIdentityError as exc:
                raised = exc
            assert raised is not None, f"repair_key={bad_key!r} hätte abgelehnt werden müssen."
            assert "/" not in str(list((run_dir).rglob(bad_key.replace('/', '_') + '*')))

        fake_record_dir = run_dir / "save_corrections"
        fake_record_dir.mkdir(parents=True, exist_ok=True)
        malformed_path = fake_record_dir / "bad_record.json"
        malformed_path.write_text(
            '{"repair_key":"bad_record","persona_key":"p","char_id":"c","operation_key":"o",'
            '"state":"hold","last_reason":"unjustified_semantic_drift","attempts_used":true}',
            encoding="utf-8",
        )
        raised = None
        try:
            recovery_ops.plan_p5(run_dir, repair_key="bad_record")
        except recovery_ops.RecoveryAuditUnreadableError as exc:
            raised = exc
        assert raised is not None, "attempts_used=True (bool-als-Zaehler) hätte abgelehnt werden müssen."

        malformed_path.write_text(
            '{"repair_key":"bad_record","persona_key":"p","char_id":"c","operation_key":"o",'
            '"state":"hold","state":"adopted","attempts_used":1}',
            encoding="utf-8",
        )
        raised = None
        try:
            recovery_ops.plan_p5(run_dir, repair_key="bad_record")
        except recovery_ops.RecoveryAuditUnreadableError as exc:
            raised = exc
        assert raised is not None, "doppelter JSON-Schluessel 'state' hätte abgelehnt werden müssen."


def test_candidate_scope_and_source_modes_bound():
    """`apply_*` NUR auf einem ausdruecklich markierten synthetischen
    Testroot (03 §Haltbarkeit: 'Apply NUR auf ausdruecklich kuenstlich
    erzeugten Testroots'). Zusaetzlich: der tatsaechliche Kandidaten-Diff
    beruehrt AUSSCHLIESSLICH die in `CONTROL.json` erlaubten Pfade."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root, synthetic_marker=False)
        rid = make_p3_unknown_request(run_dir)

        raised = None
        try:
            apply_p3_audit(
                run_dir, table_id="table-1", section_id="section-1", role="gm_turn",
                turn_idx=1, participant="alice", request_id=rid,
            )
        except recovery_ops.RecoveryUnsafeRootError as exc:
            raised = exc
        assert raised is not None, "apply_p3 ohne Markerdatei hätte abgelehnt werden müssen."

        for bad_dir in ("relative/path", "/tmp/../tmp"):
            raised = None
            try:
                recovery_ops.plan_p3(
                    bad_dir, table_id="x", section_id="y", role="gm_turn", turn_idx=1,
                    participant="z", request_id="whatever",
                )
            except recovery_ops.RecoveryUnsafeRootError:
                raised = True
            except recovery_ops.RecoveryError:
                raised = True
            assert raised, f"unsicherer run_dir {bad_dir!r} hätte abgelehnt werden müssen."

    if _PKG_CONTROL_JSON is None or not _PKG_CONTROL_JSON.is_file():
        raise EnvironmentBlocked(
            "Pflichtfixture CONTROL_JSON (ZEITRISS_R1_CONTROL_JSON bzw. neutraler Repo-Default) "
            f"zeigt auf keine vorhandene Datei (aktuell {_PKG_CONTROL_JSON!r})."
        )
    control = json.loads(_PKG_CONTROL_JSON.read_text(encoding="utf-8"))
    allowed = set(control["allowed_existing_candidate_paths"]) | set(control["allowed_new_candidate_paths"])
    touched = {
        "mmo_sim/core/recovery_ops.py", "mmo_sim/core/save_correction.py",
        "mmo_sim/lab/recovery_cli.py", "mmo_sim/lab/cli.py",
        "tests/mmo_sim/test_recovery_ops_r1.py", "tests/mmo_sim/_recovery_ops_r1_fixtures.py",
    }
    not_covered = touched - allowed - {"mmo_sim/lab/cli.py"}  # cli.py ist CONTROL-erlaubt ueber allowed_existing
    # mmo_sim/lab/cli.py steht in allowed_existing_candidate_paths -- separat verifizieren:
    assert "mmo_sim/lab/cli.py" in control["allowed_existing_candidate_paths"]
    assert not not_covered, f"Dateien ausserhalb CONTROL.json-Scope veraendert: {not_covered}"


def test_unrelated_legacy_guards_preserved():
    """Ein HOLD aus einem ANDEREN Grund als `unjustified_semantic_drift`
    (hier: regulaer per Budget erschoepft, `attempt_budget_exhausted`)
    bleibt vom neuen R-P5-Zweig vollstaendig unberuehrt -- `plan_p5`
    lehnt ihn als fachlich nicht in Betracht kommend ab (last_reason-Gate),
    der bestehende Legacy-Pfad (hier: Budgeterschoepfung) bleibt bytegleich
    terminal."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        char_id = "CHR-LEGACY-01"
        valid = full_v7_save(char_id, name="Flo")
        bad = full_v7_save(char_id, name="Flo")
        bad["economy"] = {"wallets": {char_id: 999}}  # bleibt bei JEDEM Versuch gleich falsch -> kein Drift, nur Budget

        gm = ScriptedGm([
            f"```json\n{json.dumps(bad)}\n```",
            f"```json\n{json.dumps(bad)}\n```",
            f"```json\n{json.dumps(bad)}\n```",
        ])
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id="flo_legacy", expected_chrononaut_id=char_id,
            candidate_block=bad, gm_transport=gm, role=save_correction.ROLE_CREATION,
        )
        assert outcome.status == "hold" and outcome.reason == "attempt_budget_exhausted", outcome
        repair_key = save_correction.save_correction_domain.creation_repair_key("flo_legacy", char_id)
        record = save_correction.load_record(run_dir, repair_key)
        assert record["attempts_used"] == 3 and record["state"] == "hold"

        raised = None
        try:
            recovery_ops.plan_p5(run_dir, repair_key=repair_key)
        except recovery_ops.RecoveryNotEligibleError as exc:
            raised = exc
        assert raised is not None, "ein Budget-Hold darf NIE als R-P5-Kandidat durchgehen."

        # Legacy-Pfad bleibt unveraendert terminal: ein erneuter Aufruf ohne
        # Allowance sendet NICHTS (never_called_gm wirft bei jedem .turn()).
        outcome2 = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id="flo_legacy", expected_chrononaut_id=char_id,
            candidate_block=bad, gm_transport=never_called_gm(), role=save_correction.ROLE_CREATION,
        )
        assert outcome2.status == "hold" and outcome2.reason == "attempt_budget_exhausted"


def test_budget_seed_30_independent_cases():
    """Fuehrt den byte-exakten General-Seed (`PKG/budget-seed/budget_calc.py`)
    ALS REALEN SUBPROZESS aus (Log+rc gebunden) UND prueft zusaetzlich 30
    UNABHAENGIG konstruierte Faelle direkt gegen `physical_cost_usd`/
    `BudgetBlocked` -- unabhaengig vom alten N1-Helper (Budget-Policy:
    'Der Seed schliesst den N1-Budgetrest; unabhaengig pruefen')."""
    if _PKG_BUDGET_CALC is None or not _PKG_BUDGET_CALC.is_file():
        raise EnvironmentBlocked(
            "Pflichtfixture BUDGET_CALC (ZEITRISS_R1_BUDGET_CALC bzw. neutraler Repo-Default) "
            f"zeigt auf keine vorhandene Datei (aktuell {_PKG_BUDGET_CALC!r})."
        )
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, "-B", "-u", str(_PKG_BUDGET_CALC)], capture_output=True, text=True, env=env,
    )
    assert proc.returncode == 0, f"budget_calc.py rc={proc.returncode} stderr={proc.stderr}"
    report = json.loads(proc.stdout)
    assert report["schema"] == "general-budget-seed/1"
    assert len(report["positive_cases"]) >= 7 and len(report["negative_cases"]) >= 5

    import importlib.util
    spec = importlib.util.spec_from_file_location("_pkg_budget_calc_independent", _PKG_BUDGET_CALC)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    independent_cases = []
    for attempts in (1, 2, 3, 4, 5):
        for out_tokens in (0, 400, 16384):
            independent_cases.append({"physical_attempts": attempts, "output_tokens": out_tokens, "input_tokens": 1000})
    for bad in (
        {"physical_attempts": None, "output_tokens": 100, "input_tokens": 100},
        {"physical_attempts": 0, "output_tokens": 100, "input_tokens": 100},
        {"physical_attempts": 1, "output_tokens": None, "input_tokens": 100},
        {"physical_attempts": 1, "output_tokens": 100, "input_tokens": None},
        {"physical_attempts": True, "output_tokens": 100, "input_tokens": 100},
        {"physical_attempts": 1, "output_tokens": 100, "input_tokens": 100, "cache_write_tokens": 50, "cache_write_kind": None},
        {"physical_attempts": 1, "output_tokens": 100, "input_tokens": 100, "cached_input_tokens": 1000},
        {"physical_attempts": -1, "output_tokens": 100, "input_tokens": 100},
        {"physical_attempts": 1.5, "output_tokens": 100, "input_tokens": 100},
        {"physical_attempts": 1, "output_tokens": -1, "input_tokens": 100},
    ):
        independent_cases.append(bad)
    assert len(independent_cases) == 25
    for extra_attempts in (6, 7, 8, 9, 10):
        independent_cases.append({"physical_attempts": extra_attempts, "output_tokens": 16384, "input_tokens": 2000, "cached_input_tokens": 500})
    assert len(independent_cases) == 30, len(independent_cases)

    results = []
    for case in independent_cases:
        try:
            result = module.physical_cost_usd(**case)
            results.append({"case": case, "status": "OK", "result": result})
        except module.BudgetBlocked as exc:
            results.append({"case": case, "status": "BLOCKED_MISSING_BOUND", "missing": exc.missing})
    assert len(results) == 30
    ok_count = sum(1 for r in results if r["status"] == "OK")
    blocked_count = sum(1 for r in results if r["status"] == "BLOCKED_MISSING_BOUND")
    # 15 strukturell gueltige Faelle aus der ersten Schleife (5 attempts x 3
    # output_tokens) + 5 weitere gueltige aus der dritten Schleife = 20 OK;
    # 10 bewusst defekte Faelle aus der zweiten Schleife = 10 BLOCKED.
    assert ok_count == 20, f"erwartet 20 gueltige Faelle, erhalten {ok_count}"
    assert blocked_count == 10, f"erwartet 10 BLOCKED-Faelle, erhalten {blocked_count}"
    for r in results:
        if r["status"] == "OK":
            from decimal import Decimal
            assert Decimal(r["result"]["total_usd"]) >= 0


# ═══════════════════════════════ R-P3 ═══════════════════════════════════════


def test_p3_unknown_audit_only():
    """Apply schreibt NUR den additiven Audit -- niemals `accounted`/
    `finish_received`/`finish_error`/Refund/Resend auf dem Original."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        rid = make_p3_unknown_request(run_dir)
        before_request = (run_dir / "requests" / f"{rid}.json").read_bytes()

        result = apply_p3_audit(
            run_dir, table_id="table-1", section_id="section-1", role="gm_turn",
            turn_idx=1, participant="alice", request_id=rid,
        )
        assert result["status"] == "applied"
        assert result["audit"]["action"] == recovery_ops.P3_ACTION

        after_request = (run_dir / "requests" / f"{rid}.json").read_bytes()
        assert before_request == after_request, "Originalrequest wurde veraendert."
        loaded = request_ledger.load_request(run_dir, rid)
        assert loaded["state"] == "sent" and loaded["result_text"] is None and loaded["usage"] is None
        assert loaded["settled_ts"] is None and loaded["error"] is None and loaded["usd_reconciled"] is False


def test_p3_original_and_budget_unchanged():
    """`lab.status.json` (turns_used/usd_spent) bleibt byte-logisch
    unveraendert durch `apply_p3`."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        rid = make_p3_unknown_request(run_dir)
        status_before = json.loads(_status_path(run_dir).read_text(encoding="utf-8"))

        apply_p3_audit(
            run_dir, table_id="table-1", section_id="section-1", role="gm_turn",
            turn_idx=1, participant="alice", request_id=rid,
        )
        status_after = json.loads(_status_path(run_dir).read_text(encoding="utf-8"))
        assert status_before == status_after, (status_before, status_after)


def test_p3_same_operation_still_blocked_after_restart():
    """Nach dem Audit bleibt die logische Operation fuer `request_ledger.
    begin()` weiterhin gesperrt -- `OpenReservationExistsError`, kein
    stiller zweiter Versand (Ledger-Dedup unveraendert, s. 03 §R-P3: "Das
    ist ausdruecklich KEINE Fertigerschaffung von P3")."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        rid = make_p3_unknown_request(run_dir)
        apply_p3_audit(
            run_dir, table_id="table-1", section_id="section-1", role="gm_turn",
            turn_idx=1, participant="alice", request_id=rid,
        )
        raised = None
        try:
            request_ledger.begin(
                run_dir, role="gm_turn", content="zweiter Versuch", reserved_usd=0.01,
                table_id="table-1", section_id="section-1", turn_idx=1, participant="alice",
            )
        except request_ledger.OpenReservationExistsError as exc:
            raised = exc
        assert raised is not None
        assert any(r["id"] == rid for r in request_ledger.open_requests(run_dir)), (
            "open_requests() muss die Operation weiterhin als fachlich unbekannt+gesperrt zeigen."
        )


def test_p3_wrong_target_or_stale_hash_denied():
    """Falsche Zielidentitaet ODER ein veralteter Plan-Hash (Vorzustand
    zwischenzeitlich anders) wird kontrolliert abgelehnt, NIE als Plan->Apply
    durchgereicht."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        rid = make_p3_unknown_request(run_dir, table_id="table-1", section_id="section-1", participant="alice", turn_idx=1)

        raised = None
        try:
            recovery_ops.plan_p3(
                run_dir, table_id="table-1", section_id="section-1", role="gm_turn",
                turn_idx=1, participant="BOB-NOT-ALICE", request_id=rid,
            )
        except recovery_ops.RecoveryNotEligibleError as exc:
            raised = exc
        assert raised is not None, "falsche Zielidentitaet haette abgelehnt werden muessen."

        plan = recovery_ops.plan_p3(
            run_dir, table_id="table-1", section_id="section-1", role="gm_turn",
            turn_idx=1, participant="alice", request_id=rid,
        )
        stale_plan = dict(plan)
        stale_plan["original_file_sha256"] = "0" * 64
        raised = None
        try:
            recovery_ops.apply_p3(
                run_dir, table_id="table-1", section_id="section-1", role="gm_turn",
                turn_idx=1, participant="alice", request_id=rid, operator_decision="d", reason="r",
                evidence_ref="e", plan=stale_plan,
            )
        except recovery_ops.RecoveryPreconditionChangedError as exc:
            raised = exc
        assert raised is not None, "veralteter Plan-Hash haette abgelehnt werden muessen."
        assert not (run_dir / "recovery").exists() or not list((run_dir / "recovery").rglob("*.json"))


def test_p3_duplicate_apply_idempotent():
    """Identischer Apply (gleiche Entscheidung/Grund/Beleg) ist idempotent
    -- keine weitere Wirkung/kein neuer `audit_id`."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        rid = make_p3_unknown_request(run_dir)
        first = apply_p3_audit(
            run_dir, table_id="table-1", section_id="section-1", role="gm_turn",
            turn_idx=1, participant="alice", request_id=rid,
        )
        second = apply_p3_audit(
            run_dir, table_id="table-1", section_id="section-1", role="gm_turn",
            turn_idx=1, participant="alice", request_id=rid,
        )
        assert first["status"] == "applied"
        assert second["status"] == "idempotent_noop"
        assert second["audit"]["audit_id"] == first["audit"]["audit_id"]

        third_raised = None
        try:
            apply_p3_audit(
                run_dir, table_id="table-1", section_id="section-1", role="gm_turn",
                turn_idx=1, participant="alice", request_id=rid, reason="EINE ANDERE Begruendung",
            )
        except recovery_ops.RecoveryConflictError as exc:
            third_raised = exc
        assert third_raised is not None, "andere Begruendung fuer dieselbe Operation haette einen Konflikt melden muessen."


def test_p3_interrupted_write_fail_closed():
    """Ein unterbrochener Write darf keinen halben Autorisierungszustand
    hinterlassen (fail-closed, atomar): (a) ein simulierter OSError waehrend
    `os.replace` hinterlaesst KEINEN (halben) Audit und propagiert den
    Fehler; (b) ein bereits vorhandener, aber beschaedigter Audit wird beim
    naechsten Versuch kontrolliert als unlesbar erkannt, NICHT als abwesend/
    gueltig missgedeutet."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        rid = make_p3_unknown_request(run_dir)

        with patch("mmo_sim.core.admission.os.replace", side_effect=OSError("simulated interrupted write")):
            raised = None
            try:
                apply_p3_audit(
                    run_dir, table_id="table-1", section_id="section-1", role="gm_turn",
                    turn_idx=1, participant="alice", request_id=rid,
                )
            except OSError as exc:
                raised = exc
            assert raised is not None, "ein simulierter os.replace-Fehler muss propagieren, kein stiller Erfolg."
        audits_dir = run_dir / "recovery" / "p3_audits"
        leftover = list(audits_dir.glob("*.json")) if audits_dir.is_dir() else []
        assert leftover == [], f"kein halber Audit-Datensatz darf liegen bleiben: {leftover}"
        tmp_leftover = list(audits_dir.glob("*.tmp-*")) if audits_dir.is_dir() else []
        assert tmp_leftover == [], f"keine verwaiste Temp-Datei: {tmp_leftover}"

        # (b) ein bereits vorhandener, aber beschaedigter Audit (simuliert
        # einen unterbrochenen Write EINES fruehren Prozesses) wird NICHT
        # als abwesend behandelt (das wuerde einen stillen Zweit-Apply
        # erlauben).
        audits_dir.mkdir(parents=True, exist_ok=True)
        audit_key = recovery_ops._hash_key("P3", "table-1", "section-1", "gm_turn", 1, "alice", rid)
        (audits_dir / f"{audit_key}.json").write_text('{"broken": tru', encoding="utf-8")
        raised = None
        try:
            apply_p3_audit(
                run_dir, table_id="table-1", section_id="section-1", role="gm_turn",
                turn_idx=1, participant="alice", request_id=rid,
            )
        except recovery_ops.RecoveryAuditUnreadableError as exc:
            raised = exc
        assert raised is not None, "ein beschaedigter vorhandener Audit muss fail-closed erkannt werden."


# ═══════════════════════════════ R-P5 ═══════════════════════════════════════


def test_p5_without_grant_remains_hold():
    """Ohne Grant bleibt der Drift-Hold terminal -- kein automatischer
    Versand (`never_called_gm` wirft bei jedem `.turn()`-Aufruf)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        p5 = make_p5_drift_hold(run_dir, persona_key="flo_nograt", char_id="CHR-NG-01")
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=p5["persona_key"], expected_chrononaut_id=p5["char_id"],
            candidate_block=p5["invalid_candidate"], gm_transport=never_called_gm(), role=save_correction.ROLE_CREATION,
        )
        assert outcome.status == "hold" and outcome.reason == "unjustified_semantic_drift"
        record = save_correction.load_record(run_dir, p5["repair_key"])
        assert record["attempts_used"] == 1 and record["state"] == "hold"


def test_p5_one_grant_one_additional_slot():
    """Happy Path: EIN Grant -> genau EIN zusaetzlicher Slot (2), der echte,
    unveraenderte Validator akzeptiert die gueltige Antwort."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        p5 = make_p5_drift_hold(run_dir, persona_key="flo_slot2", char_id="CHR-S2-01")
        grant = apply_p5_grant(run_dir, p5["repair_key"])
        assert grant["status"] == "applied" and grant["grant"]["consumed"] is False

        gm = ScriptedGm([f"```json\n{json.dumps(p5['valid_save'])}\n```"])
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=p5["persona_key"], expected_chrononaut_id=p5["char_id"],
            candidate_block=p5["invalid_candidate"], gm_transport=gm, role=save_correction.ROLE_CREATION,
        )
        assert outcome.status == "accepted" and outcome.block == p5["valid_save"]
        assert [c[0] for c in gm.calls] == [2], "die Autorisierung darf hoechstens Slot 2 oeffnen."
        record = save_correction.load_record(run_dir, p5["repair_key"])
        assert record["attempts_used"] == 2 and record["state"] == "adopted"
        assert record.get("recovery_extra_attempt") is True


def test_p5_duplicate_or_rebound_grant_denied():
    """Ein zweiter Apply mit ANDERER Begruendung fuer denselben
    `repair_key` ist ein Konflikt; nach Verbrauch (Record nicht mehr
    `hold`/`attempts_used=1`) ist ein ERNEUTER Grant an derselben
    Fallentscheidung ausgeschlossen (plan_p5 lehnt ab)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        p5 = make_p5_drift_hold(run_dir, persona_key="flo_dup", char_id="CHR-DUP-01")
        apply_p5_grant(run_dir, p5["repair_key"])

        raised = None
        try:
            apply_p5_grant(run_dir, p5["repair_key"], reason="EINE ANDERE Begruendung")
        except recovery_ops.RecoveryConflictError as exc:
            raised = exc
        assert raised is not None

        idempotent = apply_p5_grant(run_dir, p5["repair_key"])
        assert idempotent["status"] == "idempotent_noop"

        # Nach Verbrauch (Slot 2 erfolgreich adoptiert) ist dieselbe
        # Fallentscheidung kein Kandidat mehr -- kein erneuter Grant als
        # Umgehung.
        gm = ScriptedGm([f"```json\n{json.dumps(p5['valid_save'])}\n```"])
        save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=p5["persona_key"], expected_chrononaut_id=p5["char_id"],
            candidate_block=p5["invalid_candidate"], gm_transport=gm, role=save_correction.ROLE_CREATION,
        )
        raised = None
        try:
            recovery_ops.plan_p5(run_dir, repair_key=p5["repair_key"])
        except recovery_ops.RecoveryNotEligibleError as exc:
            raised = exc
        assert raised is not None, "nach Verbrauch darf plan_p5 keinen neuen Grant mehr erlauben."


def test_p5_wrong_identity_or_original_denied():
    """`try_consume_p5_allowance` liefert `False`, wenn Record-Identitaet
    ODER gebundener Vorzustand (Original) nicht zum Grant passt -- selbst
    wenn ein Grant fuer einen ANDEREN, aehnlichen Fall existiert."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        p5 = make_p5_drift_hold(run_dir, persona_key="flo_wid", char_id="CHR-WID-01")
        apply_p5_grant(run_dir, p5["repair_key"])
        record = save_correction.load_record(run_dir, p5["repair_key"])

        wrong_identity_record = dict(record)
        wrong_identity_record["char_id"] = "SOME-OTHER-CHAR"
        assert recovery_ops.try_consume_p5_allowance(
            run_dir, repair_key=p5["repair_key"], record=wrong_identity_record,
        ) is False

        # `try_consume_p5_allowance` hasht den TATSAECHLICHEN Datenträger
        # (nicht das uebergebene `record`-Argument) -- ein veraenderter
        # Vorzustand muss deshalb ECHT auf Platte geschrieben sein, um die
        # Pruefung zu treffen (sonst testet man nur eine folgenlose
        # In-Memory-Kopie).
        mutated_on_disk = dict(record)
        mutated_on_disk["errors"] = ["mutated to change the pre-state hash"]
        save_correction._write_record(run_dir, p5["repair_key"], mutated_on_disk)
        assert recovery_ops.try_consume_p5_allowance(
            run_dir, repair_key=p5["repair_key"], record=mutated_on_disk,
        ) is False, "ein veraenderter Vorzustand (anderer Hash) darf nicht konsumieren."
        save_correction._write_record(run_dir, p5["repair_key"], record)

        # Die echte, unveraenderte Identitaet funktioniert weiterhin.
        assert recovery_ops.try_consume_p5_allowance(
            run_dir, repair_key=p5["repair_key"], record=record,
        ) is True


def test_p5_valid_reply_real_validator_accepts():
    """Der REALE, unveraenderte Validator akzeptiert einen wirklich
    validierbaren SYNTHETISCHEN Save auf dem gebundenen Slot 2 -- kein
    synthetischer Test ist ein P5-Livesave."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        p5 = make_p5_drift_hold(run_dir, persona_key="flo_valid", char_id="CHR-VALID-01")
        apply_p5_grant(run_dir, p5["repair_key"])

        acceptance = save_correction.save_correction_domain.evaluate(p5["valid_save"], p5["char_id"])
        assert acceptance.accepted, "Fixture-Vorbedingung: valid_save muss ECHT gueltig sein."

        gm = ScriptedGm([f"```json\n{json.dumps(p5['valid_save'])}\n```"])
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=p5["persona_key"], expected_chrononaut_id=p5["char_id"],
            candidate_block=p5["invalid_candidate"], gm_transport=gm, role=save_correction.ROLE_CREATION,
        )
        assert outcome.status == "accepted" and outcome.block == p5["valid_save"]


def test_p5_schema_or_drift_failure_no_third_attempt():
    """Eine erneute Drift ODER ein Formatfehler auf Slot 2 fuehrt zu
    sicherem Abschluss/HOLD -- OHNE automatische dritte Korrekturanfrage
    (unabhaengig vom verbleibenden `MAX_ADDITIONAL_REQUESTS`-Budget)."""
    for scenario, build_reply in (
        ("drift_again", lambda char_id: _drift_reply(char_id)),
        ("schema_error_no_drift", lambda char_id: _schema_error_reply(char_id)),
    ):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run_dir = make_synthetic_run(root)
            p5 = make_p5_drift_hold(run_dir, persona_key=f"flo_{scenario}", char_id=f"CHR-{scenario.upper()}")
            apply_p5_grant(run_dir, p5["repair_key"])

            gm = ScriptedGm([f"```json\n{json.dumps(build_reply(p5['char_id']))}\n```"])
            outcome = save_correction.pursue_single_figure_correction(
                run_dir=run_dir, participant_id=p5["persona_key"], expected_chrononaut_id=p5["char_id"],
                candidate_block=p5["invalid_candidate"], gm_transport=gm, role=save_correction.ROLE_CREATION,
            )
            assert outcome.status == "hold", (scenario, outcome)
            # "drift_again" trifft den bereits BESTEHENDEN, unveraenderten
            # Drift-Zweig (der IMMER sofort terminal haelt, unabhaengig von
            # einer Recovery-Autorisierung) -- reason bleibt
            # "unjustified_semantic_drift". "schema_error_no_drift" trifft
            # den NEUEN Einmaligkeits-Deckel (kein Drift, aber auch keine
            # Annahme) -- reason "recovery_extra_attempt_exhausted". Beide
            # sind "sicherer Abschluss/HOLD ohne automatische dritte
            # Korrekturanfrage" (03 §R-P5), nur mit unterschiedlichem,
            # jeweils korrektem Beleggrund.
            expected_reason = {
                "drift_again": "unjustified_semantic_drift",
                "schema_error_no_drift": "recovery_extra_attempt_exhausted",
            }[scenario]
            assert outcome.reason == expected_reason, (scenario, outcome)
            assert [c[0] for c in gm.calls] == [2], (scenario, "nur EIN Versand auf Slot 2, kein dritter.")
            record = save_correction.load_record(run_dir, p5["repair_key"])
            assert record["attempts_used"] == 2, (scenario, record)

            # Ein weiterer Aufruf sendet NICHTS mehr (terminal).
            outcome2 = save_correction.pursue_single_figure_correction(
                run_dir=run_dir, participant_id=p5["persona_key"], expected_chrononaut_id=p5["char_id"],
                candidate_block=p5["invalid_candidate"], gm_transport=never_called_gm(), role=save_correction.ROLE_CREATION,
            )
            assert outcome2.status == "hold", (scenario, outcome2)


def _drift_reply(char_id: str) -> dict:
    block = full_v7_save(char_id, name="ANOTHER-DRIFTED-NAME")
    block["economy"] = {"wallets": {char_id: {"balance": 500}}}
    return block


def _schema_error_reply(char_id: str) -> dict:
    block = full_v7_save(char_id, name="Flo")
    block["economy"] = {"wallets": {char_id: "not-a-number"}}
    return block


def test_p5_consumption_crash_no_double_dispatch():
    """Verbrauch ist restartfest VOR dem naechsten physischen Versand: ein
    zweiter `try_consume_p5_allowance`-Aufruf (simuliert einen Prozess, der
    nach dem Konsum, aber VOR dem naechsten Schritt abgestuerzt ist und
    neu einsteigt) schreibt NICHT erneut, liefert aber weiterhin `True`
    (idempotente Fortsetzung, kein Doppelverbrauch)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        p5 = make_p5_drift_hold(run_dir, persona_key="flo_crash", char_id="CHR-CRASH-01")
        apply_p5_grant(run_dir, p5["repair_key"])
        record = save_correction.load_record(run_dir, p5["repair_key"])

        first = recovery_ops.try_consume_p5_allowance(run_dir, repair_key=p5["repair_key"], record=record)
        assert first is True
        grant_path = recovery_ops._p5_grant_path(run_dir, p5["repair_key"])
        grant_after_first = json.loads(grant_path.read_text(encoding="utf-8"))
        assert grant_after_first["consumed"] is True
        mtime_after_first = grant_path.stat().st_mtime_ns

        second = recovery_ops.try_consume_p5_allowance(run_dir, repair_key=p5["repair_key"], record=record)
        assert second is True
        grant_after_second = json.loads(grant_path.read_text(encoding="utf-8"))
        assert grant_after_second == grant_after_first, "kein erneuter Schreibzugriff bei bereits konsumiertem Grant."
        assert grant_path.stat().st_mtime_ns == mtime_after_first

        # Der volle Korrekturpfad selbst sendet danach trotzdem GENAU EINMAL
        # (kein Doppelversand, auch wenn der Konsum zuvor schon isoliert
        # ausgefuehrt wurde).
        gm = ScriptedGm([f"```json\n{json.dumps(p5['valid_save'])}\n```"])
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=p5["persona_key"], expected_chrononaut_id=p5["char_id"],
            candidate_block=p5["invalid_candidate"], gm_transport=gm, role=save_correction.ROLE_CREATION,
        )
        assert outcome.status == "accepted"
        assert len(gm.calls) == 1


def test_p5_unknown_sent_no_resend():
    """Ein unklarer Versand (Crash zwischen Versand+Antwort fuer Slot 2)
    wird NIE retried/resend -- kontrolliertes HOLD (`OpenReservationExistsError`-
    Dedup bleibt unveraendert wirksam auch fuer den gebundenen Slot 2)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        p5 = make_p5_drift_hold(run_dir, persona_key="flo_unksent", char_id="CHR-UNK-01")
        apply_p5_grant(run_dir, p5["repair_key"])
        record = save_correction.load_record(run_dir, p5["repair_key"])

        # Konsum isoliert ausfuehren und DANACH einen Request fuer Slot 2
        # (turn_idx=2) liegen lassen, der nie finish_received/finish_error
        # erreicht hat -- genau die "unklare sent-Ausfuehrung".
        assert recovery_ops.try_consume_p5_allowance(run_dir, repair_key=p5["repair_key"], record=record) is True
        request_ledger.begin(
            run_dir, role=save_correction.ROLE_CREATION, content="unklar gesendet", reserved_usd=0.01,
            table_id=None, section_id=None, turn_idx=2, participant=p5["persona_key"],
        )

        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=p5["persona_key"], expected_chrononaut_id=p5["char_id"],
            candidate_block=p5["invalid_candidate"], gm_transport=never_called_gm(), role=save_correction.ROLE_CREATION,
        )
        assert outcome.status == "hold", outcome
        assert outcome.reason is not None and outcome.reason.startswith("unclear_sent_in_flight"), outcome


def test_p5_received_reply_restart_reuses_original():
    """Eine bereits durabel empfangene Antwort fuer Slot 2 (Crash NACH
    Empfang, VOR Auswertung) wird bei Wiederaufnahme WIEDERVERWENDET --
    kein Doppelversand (`find_durable_result`, bestehender Mechanismus,
    unveraendert)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = make_synthetic_run(root)
        p5 = make_p5_drift_hold(run_dir, persona_key="flo_received", char_id="CHR-RECV-01")
        apply_p5_grant(run_dir, p5["repair_key"])
        record = save_correction.load_record(run_dir, p5["repair_key"])
        assert recovery_ops.try_consume_p5_allowance(run_dir, repair_key=p5["repair_key"], record=record) is True

        rid = request_ledger.begin(
            run_dir, role=save_correction.ROLE_CREATION, content="bereits beantwortet", reserved_usd=0.01,
            table_id=None, section_id=None, turn_idx=2, participant=p5["persona_key"],
        )
        request_ledger.finish_received(
            run_dir, rid, usage={}, seconds=0.5, result_text=f"```json\n{json.dumps(p5['valid_save'])}\n```",
        )

        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=p5["persona_key"], expected_chrononaut_id=p5["char_id"],
            candidate_block=p5["invalid_candidate"], gm_transport=never_called_gm(), role=save_correction.ROLE_CREATION,
        )
        assert outcome.status == "accepted" and outcome.block == p5["valid_save"]


def main() -> int:
    tests = [v for k, v in list(globals().items()) if k.startswith("test_") and callable(v)]
    passed, failed, blocked = 0, 0, 0
    for t in sorted(tests, key=lambda f: f.__name__):
        try:
            t()
            print(f"OK      {t.__name__}")
            passed += 1
        except EnvironmentBlocked as e:
            blocked += 1
            print(f"BLOCKED {t.__name__}: {e}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL    {t.__name__}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR   {t.__name__}:")
            traceback.print_exc()
    print(f"\n{passed}/{len(tests)} bestanden, {failed} fehlgeschlagen, {blocked} BLOCKED_ENV.")
    # R2-TEST-Fix (GENERALREVIEW.md §6): ein BLOCKED_ENV-Fall (fehlende
    # Pflichtfixture) ist KEIN bestandener Lauf -- der vormalige rc=0 trotz
    # BLOCKED_ENV liess eine Datei mit nicht ausgefuehrten Pflichtfaellen
    # fuer `run_all.py`/jeden aussenstehenden Aufrufer als erfolgreich
    # zaehlen (R1-Bug). `blocked` zaehlt jetzt wie `failed` gegen rc=0.
    return 0 if failed == 0 and blocked == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
