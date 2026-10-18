#!/usr/bin/env python3
"""
tests/mmo_sim/test_f_process_evidence_2026_10_18.py -- F-PROCESS-EVIDENCE
(ZR-N2-LIVEBUNDLE-FRESH-20261018-R1).

Testet die ECHTE, bis zum Bundle-Eintritt vollstaendige Aufrufkette -- nicht
nur isolierte Adapter -- jeweils mit Fake-TRANSPORT (geldfrei, kein Netz,
keine Inferenz), aber ueber die echten Caller:

1. Langsame Persona-CLI -> echter Timeout (`subprocess.TimeoutExpired` im
   echten `_RealProcessRunner`, kein in-Prozess-Fake) mit durablem
   `finish_error` durch den normalen Caller
   (`domain.zeitriss.community_creation._persona_get_reply_factory`'s
   `_get_reply`, EXAKT der Pfad, den `advance_community_creation` benutzt).
2. Unbekannter Ausgang -> kalter OS-Reentry (echter zweiter Prozess, ANDERE
   PID) mit gebundener HOLD-Sperre -- `core.request_ledger.begin()`s
   bestehendes `OpenReservationExistsError` fuer dieselbe Operations-
   identitaet, hier ueber ZWEI echte OS-Prozesse statt nur in-Prozess belegt.
3. Echte langsame SL-Korrekturkette (volle Schleife, nicht nur zwei
   Personaaufrufe): `core.save_correction.pursue_single_figure_correction`
   mit einem GM-Transport, der JEDEN Turn real (Wall-Clock) verzoegert --
   voller Mehr-Versuch-Korrekturpfad, nicht abgekuerzt.
4. Vollstaendig gemessener Outer-Drain: Wall-Clock-Messung um den echten
   `subprocess.run`-Aufruf (derselbe Fake-CLI-Prozess wie (1)) herum.

Jeder Fakeprozess besitzt seine EIGENE PID/Prozessgruppe (echte
`subprocess.run`/`os.fork`-Grenzen) -- KEIN `pgrep`/`pkill`, KEIN Toeten
fremder Prozesse. Dispatch-/Record-Zahlen werden ueber die bereits vom
Produkt selbst geschriebenen Requestdatensaetze (`run/requests/*.json`)
UND das eigene `dispatch_log.jsonl` des Fake-CLI-Fixtures geprueft -- ein
`sent`-Record allein beweist keinen physischen Dispatch, deshalb wird hier
IMMER zusaetzlich das vom (echten, eigenen PID tragenden) Kindprozess
selbst geschriebene Dispatch-Protokoll gegengelesen."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.adapters.base import ProviderUnavailableError  # noqa: E402
from mmo_sim.adapters.persona_claude_code import ClaudeCodeConfig, PersonaClaudeCodeDriver  # noqa: E402
from mmo_sim.core import request_ledger  # noqa: E402
from mmo_sim.core import save_correction  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.community_bootstrap import bootstrap_community  # noqa: E402
from mmo_sim.domain.zeitriss.community_creation import _persona_get_reply_factory  # noqa: E402

import contextlib  # noqa: E402


@contextlib.contextmanager
def _restore_home():
    """Die Fake-CLI-Fixtur bindet ihre Kontrolldateien an `$HOME` (s.
    `_make_driver`) -- das MUSS nach jedem Test wiederhergestellt werden,
    sonst erbt ein von DIESEM Testprozess gestarteter echter Subprozess
    (z.B. Test 2s `--child`-Reinvocation) ein geloeschtes temporaeres
    `HOME` und scheitert bereits am Modulimport (site-packages/venv-
    Aufloesung haengt am echten `HOME`)."""
    original = os.environ.get("HOME")
    try:
        yield
    finally:
        if original is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = original


_FAKE_CLI = _HERE / "_f_process_evidence_fake_cli.py"
SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
PK = "f_process_evidence_persona"


def _make_driver(root: Path, *, process_timeout_seconds: int, sleep_seconds: float, dispatch_log: Path):
    """Kontrolldateien liegen unter `$HOME` (hier auf `root/home` gebunden,
    `os.environ["HOME"]` entsprechend gesetzt) statt `cwd` -- der echte
    Adapter setzt `cwd` NUR fuer den eigentlichen Decide-Call (`isolated_
    workdir`), NICHT fuer die vorgelagerten `--version`/`--help`-Aufrufe in
    `check_isolation()` (dort bleibt `cwd=None`). `HOME` ist dagegen bei
    ALLEN drei echten Aufrufen identisch durchgereicht (Teil der minimalen
    `_CHILD_ENV_ALLOWLIST` UND -- fuer die env-lose Version/Help-Aufrufe --
    ueber volle Env-Vererbung, `env=None`)."""
    workdir = root / "persona_workdir"
    workdir.mkdir(parents=True, exist_ok=True)
    home = root / "home"
    home.mkdir(parents=True, exist_ok=True)
    os.environ["HOME"] = str(home)
    config = ClaudeCodeConfig(
        binary=sys.executable, isolated_workdir=str(workdir),
        extra_isolation_flags=["--permission-mode=plan", "--safe-mode"],
        process_timeout_seconds=process_timeout_seconds,
    )
    driver = PersonaClaudeCodeDriver(config, PK)
    if sleep_seconds:
        (home / "sleep_seconds.txt").write_text(str(sleep_seconds), encoding="utf-8")
    else:
        (home / "sleep_seconds.txt").unlink(missing_ok=True)
    return driver, home / "dispatch_log.jsonl"


class _PrefixedRunner:
    """Reicht `[sys.executable, FAKE_CLI_PATH, *argv[1:]]` an den ECHTEN
    `_RealProcessRunner` weiter -- `argv[0]` ist `config.binary`
    (`sys.executable`), die eigentliche Fake-CLI-Datei wird als FESTES
    zweites Argument vorangestellt. Delegiert 1:1 an den echten Runner
    (gleicher `subprocess.run`, gleicher Timeout) -- KEIN In-Prozess-Fake,
    nur eine Argv-Praefix-Bruecke, damit `sys.executable` die Fake-CLI-
    Datei statt sich selbst interaktiv startet."""

    def __init__(self, inner):
        self._inner = inner

    def run(self, argv, stdin="", env=None, cwd=None):
        real_argv = [argv[0], str(_FAKE_CLI), *argv[1:]]
        return self._inner.run(real_argv, stdin=stdin, env=env, cwd=cwd)


def _wrap_with_fake_cli(driver: PersonaClaudeCodeDriver) -> None:
    from mmo_sim.adapters.persona_claude_code import _RealProcessRunner
    driver._runner = _PrefixedRunner(_RealProcessRunner(timeout=driver.config.process_timeout_seconds))


def test_slow_persona_cli_real_subprocess_timeout_is_durable_finish_error():
    """(1) Ein ECHTER, eigenstaendiger OS-Prozess (eigene PID) schlaeft
    laenger als `process_timeout_seconds` -- der ECHTE `_RealProcessRunner`
    wirft `subprocess.TimeoutExpired`, `PersonaClaudeCodeDriver.decide()`
    bildet das auf `ProviderUnavailableError` ab, der NORMALE Caller
    (`_persona_get_reply_factory`'s `_get_reply`) faengt das in seinem
    bestehenden `except Exception`-Zweig und schreibt EINEN durablen
    `request_ledger.finish_error`-Record -- kein stilles Verschlucken,
    kein zweiter automatischer Versand fuer denselben Request."""
    with tempfile.TemporaryDirectory() as td, _restore_home():
        root = Path(td)
        run_dir, onboarding_dir, states_dir = root / "run", root / "onboarding", root / "states"
        ps_store = PersonaStateStore(schema_path=SCHEMA)
        draft = {
            "real_name": "F-Process-Evidence", "archetype": "SYNTHETIC_ARCH", "play_style": "SYNTHETIC_STYLE",
            "charwunsch": "SYNTHETIC_WISH",
            "plays_char": {
                "save_file": "NOCH_NICHT_ERSCHAFFEN", "character_id": "NOCH_NICHT_ERSCHAFFEN",
                "name": "NOCH_NICHT_ERSCHAFFEN", "callsign": "NOCH_NICHT_ERSCHAFFEN",
            },
        }
        bootstrap_community(run_dir / "community", "f-pe-community", 1, {PK: draft}, ps_store, states_dir, "2026-10-18")
        write_test_profile(run_dir, max_turns=10, max_usd=10)
        onboarding.start_or_resume(onboarding_dir, PK)

        driver, dispatch_log = _make_driver(root, process_timeout_seconds=1, sleep_seconds=4.0, dispatch_log=None)
        _wrap_with_fake_cli(driver)

        reply_fn = _persona_get_reply_factory(
            run_dir=run_dir, persona_driver=driver, community_id="f-pe-community", generation=1,
            persona_key=PK, draft_state=draft, onboarding_dir=onboarding_dir, print_fn=lambda *_a: None,
        )

        t0 = time.monotonic()
        result = reply_fn(0, "Welchen Rufnamen waehlst du?")
        elapsed = time.monotonic() - t0
        assert result.kind == "error", result
        assert 1.0 <= elapsed < 3.5, f"Timeout muss real nahe 1s greifen (Sleep war 4s), gemessen: {elapsed:.2f}s"

        requests = [json.loads(p.read_text()) for p in sorted((run_dir / "requests").glob("*.json"))]
        assert len(requests) == 1 and requests[0]["state"] == "accounted", requests
        assert requests[0].get("error") and "timed out" in requests[0]["error"].lower(), requests[0]
        assert requests[0]["result_text"] is None, "ein durabler finish_error darf KEINEN Erfolgstext tragen."

        # Record-/Dispatch-Zahlen: ein `sent`->`error`-Record allein beweist
        # keinen physischen Dispatch -- das eigenstaendig vom Kindprozess
        # geschriebene Dispatch-Protokoll (EIGENE PID, kein pgrep) belegt
        # den tatsaechlichen Versand zusaetzlich.
        dispatch_rows = [json.loads(l) for l in dispatch_log.read_text().splitlines() if l.strip()]
        kinds = [r["kind"] for r in dispatch_rows]
        assert kinds.count("version") == 1 and kinds.count("help") == 1 and kinds.count("decide_start") == 1, kinds
        assert "decide_end" not in kinds, "der Kindprozess wurde VOM TIMEOUT abgebrochen, bevor er antworten konnte."
        pids = {r["pid"] for r in dispatch_rows}
        assert os.getpid() not in pids, "jeder Fake-CLI-Aufruf hat seine EIGENE PID, nicht die des Elternprozesses."
        assert len(pids) == 3, f"drei eigenstaendige Prozesse (--version/--help/decide), je eigene PID: {pids}"


def test_unknown_outcome_cold_os_reentry_binds_hold_no_blind_resend():
    """(2) Prozess 1 reserviert real (`request_ledger.begin`, state=sent)
    und stirbt DANACH hart (`os._exit`, KEIN finish_received/finish_error --
    der 'unbekannte Ausgang': Ledger weiss nicht, ob der Versand je
    ankam). Prozess 2 ist ein ECHTER, FRISCHER OS-Prozess (andere PID,
    `subprocess.run` dieses Moduls mit `--child`) -- `request_ledger.
    begin()` fuer DIESELBE Operationsidentitaet MUSS `OpenReservationExists
    Error` werfen (gebundene HOLD-Sperre), KEIN zweiter Versand fuer
    denselben Slot."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        write_test_profile(run_dir, max_turns=10, max_usd=10)
        identity_kwargs = dict(
            role="gm_turn", content="SYNTHETIC unbeantworteter Request (unbekannter Ausgang).",
            reserved_usd=0.01, table_id="f-pe-table", section_id="f-pe-section", turn_idx=1, participant="f_pe_pk",
        )

        p1 = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--child", "begin-and-crash", str(run_dir)],
            capture_output=True, text=True, timeout=30,
        )
        assert p1.returncode == 93, (p1.returncode, p1.stdout, p1.stderr)
        parent_row = json.loads(p1.stdout.strip().splitlines()[-1])
        parent_pid = parent_row["pid"]

        requests = [json.loads(p.read_text()) for p in sorted((run_dir / "requests").glob("*.json"))]
        assert len(requests) == 1 and requests[0]["state"] == "sent", (
            f"Prozess 1 muss state=sent OHNE finish_received/finish_error hinterlassen -- {requests}"
        )

        p2 = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--child", "reenter-same-identity", str(run_dir)],
            capture_output=True, text=True, timeout=30,
        )
        assert p2.returncode == 0, (p2.returncode, p2.stdout, p2.stderr)
        child_row = json.loads(p2.stdout.strip().splitlines()[-1])
        assert child_row["pid"] != parent_pid, "Prozess 2 muss eine ECHTE, ANDERE PID als Prozess 1 haben."
        assert child_row["bound_hold"] is True and child_row["error_type"] == "OpenReservationExistsError", child_row

        requests_after = [json.loads(p.read_text()) for p in sorted((run_dir / "requests").glob("*.json"))]
        assert len(requests_after) == 1, (
            f"KEIN zweiter Requestdatensatz -- der kalte Reentry darf nicht blind erneut versenden: {requests_after}"
        )


def test_real_slow_sl_correction_full_loop_is_measured():
    """(3) Echte langsame SL-Korrekturkette: `pursue_single_figure_
    correction` durchlaeuft den VOLLEN Mehr-Versuch-Korrekturpfad (1
    Erstversand + 2 Korrekturversuche, jeder Turn real wall-clock-verzoegert
    ueber einen echten `time.sleep()` im GM-Transport-Double) -- nicht nur
    zwei isolierte Personaaufrufe. Die gemessene Gesamtzeit MUSS die Summe
    der realen Verzoegerungen widerspiegeln (kein beschleunigter/
    uebersprungener Fake-Transport)."""
    char_id = "CHR-F-PE-SLOW-01"
    invalid_block = full_v7_save(char_id, name="Flo", callsign="PE1")
    invalid_block["economy"] = {"wallets": {char_id: 500}}  # schema-ungueltig: blanke Zahl statt Objekt.
    invalid_1 = "```json\n" + json.dumps(invalid_block) + "\n```"
    invalid_2 = invalid_1  # dieselbe Form, zweiter Korrekturversuch bleibt ebenfalls ungueltig.
    valid_block = full_v7_save(char_id, name="Flo", callsign="PE1")
    valid_block["economy"] = {"wallets": {char_id: {"balance": 500}}}  # wertgleicher, gueltig geformter Rename.
    valid = "```json\n" + json.dumps(valid_block) + "\n```"

    delays = [0.3, 0.3, 0.3]

    class _SlowGm:
        output_limit_tokens = 4000

        def __init__(self):
            self.calls: list[float] = []

        def turn(self, turn_idx, user_text, output_limit_tokens=None):
            start = time.monotonic()
            time.sleep(delays[len(self.calls)])
            self.calls.append(time.monotonic() - start)
            content = [invalid_1, invalid_2, valid][len(self.calls) - 1]
            return {"content": content, "usage": {}}

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        write_test_profile(run_dir, max_turns=10, max_usd=10)
        gm = _SlowGm()
        t0 = time.monotonic()
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id="flo_pe_slow", expected_chrononaut_id=char_id,
            candidate_block=None, gm_transport=gm, role=save_correction.ROLE_CREATION,
        )
        elapsed = time.monotonic() - t0
        assert len(gm.calls) == 3, f"voller Mehr-Versuch-Korrekturpfad erwartet, bekommen: {gm.calls}"
        assert outcome.status == "accepted", outcome
        assert elapsed >= sum(delays) * 0.9, (
            f"gemessene Gesamtzeit ({elapsed:.2f}s) muss die reale Summe der SL-Verzoegerungen "
            f"({sum(delays):.2f}s) widerspiegeln -- kein uebersprungener Fake-Transport."
        )

        requests = [json.loads(p.read_text()) for p in sorted((run_dir / "requests").glob("*.json"))]
        assert len(requests) == 3 and all(r["state"] == "accounted" for r in requests[:2] + requests[2:]), requests


def test_outer_drain_is_fully_measured_with_real_subprocess_pid():
    """(4) Outer-Drain: Wall-Clock-Messung um denselben echten Fake-CLI-
    Subprozess (1) herum, diesmal OHNE Timeout (Sleep < Grenze) -- belegt,
    dass der Elternprozess tatsaechlich bis zum vollstaendigen Drain des
    Kindprozesses (stdout/stderr/Exit) wartet und das real misst, nicht nur
    den Start. `dispatch_log` zeigt die EIGENE PID des Kindprozesses."""
    with tempfile.TemporaryDirectory() as td, _restore_home():
        root = Path(td)
        driver, dispatch_log = _make_driver(root, process_timeout_seconds=10, sleep_seconds=0.5, dispatch_log=None)
        _wrap_with_fake_cli(driver)

        t0 = time.monotonic()
        decision = driver.decide({"system": "", "user": "SYNTHETIC: triff eine Entscheidung."})
        elapsed = time.monotonic() - t0
        assert decision.text, decision
        assert elapsed >= 0.5 * 0.9, f"Outer-Drain muss die reale 0.5s-Verzoegerung des Kindprozesses abwarten: {elapsed:.2f}s"

        dispatch_rows = [json.loads(l) for l in dispatch_log.read_text().splitlines() if l.strip()]
        decide_rows = [r for r in dispatch_rows if r["kind"] in ("decide_start", "decide_end")]
        assert len(decide_rows) == 2 and decide_rows[0]["pid"] == decide_rows[1]["pid"] != os.getpid(), dispatch_rows


def _child_begin_and_crash(run_dir: Path) -> None:
    write_test_profile(run_dir, max_turns=10, max_usd=10)
    request_ledger.begin(
        run_dir, role="gm_turn", content="SYNTHETIC unbeantworteter Request (unbekannter Ausgang).",
        reserved_usd=0.01, table_id="f-pe-table", section_id="f-pe-section", turn_idx=1, participant="f_pe_pk",
    )
    print(json.dumps({"pid": os.getpid()}))
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(93)  # haerter Absturz NACH state=sent, VOR jedem finish_*-Aufruf -- der 'unbekannte Ausgang'.


def _child_reenter_same_identity(run_dir: Path) -> None:
    error_type = None
    bound_hold = False
    try:
        request_ledger.begin(
            run_dir, role="gm_turn", content="SYNTHETIC zweiter Versand-Versuch (muss abgelehnt werden).",
            reserved_usd=0.01, table_id="f-pe-table", section_id="f-pe-section", turn_idx=1, participant="f_pe_pk",
        )
    except request_ledger.OpenReservationExistsError as exc:
        error_type = type(exc).__name__
        bound_hold = True
    print(json.dumps({"pid": os.getpid(), "bound_hold": bound_hold, "error_type": error_type}))


def _run(name: str, fn) -> bool:
    try:
        fn()
    except Exception as e:  # noqa: BLE001
        print(f"FAIL {name}: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False
    print(f"PASS {name}")
    return True


if __name__ == "__main__":
    if "--child" in sys.argv:
        idx = sys.argv.index("--child")
        mode, run_dir_arg = sys.argv[idx + 1], Path(sys.argv[idx + 2])
        if mode == "begin-and-crash":
            _child_begin_and_crash(run_dir_arg)
        elif mode == "reenter-same-identity":
            _child_reenter_same_identity(run_dir_arg)
        else:
            raise SystemExit(f"unknown --child mode {mode!r}")
        sys.exit(0)

    tests = [
        ("test_slow_persona_cli_real_subprocess_timeout_is_durable_finish_error",
         test_slow_persona_cli_real_subprocess_timeout_is_durable_finish_error),
        ("test_unknown_outcome_cold_os_reentry_binds_hold_no_blind_resend",
         test_unknown_outcome_cold_os_reentry_binds_hold_no_blind_resend),
        ("test_real_slow_sl_correction_full_loop_is_measured",
         test_real_slow_sl_correction_full_loop_is_measured),
        ("test_outer_drain_is_fully_measured_with_real_subprocess_pid",
         test_outer_drain_is_fully_measured_with_real_subprocess_pid),
    ]
    results = [_run(name, fn) for name, fn in tests]
    print(f"\n{sum(results)}/{len(results)} passed")
    sys.exit(0 if all(results) else 1)
