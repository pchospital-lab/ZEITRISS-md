#!/usr/bin/env python3
"""
tests/mmo_sim/drive_r3_g5_evidence_2026_11_04.py -- ZR-BETREIBER-
GASTERSCHAFFUNG-20261104-R3, G5 (WORKER-G5-EVIDENCE.md): erweitert
`drive_r2_f5_evidence_2026_11_04.py` 1:1 in Struktur/Helfern/Disziplin um
vier Beweisfamilien T1-T4 fuer G1-G4 (echter Launcher-FIFO-Betreiberweg,
Plan-vs-Stop-Rennen mit G2-Bedienzweig, hostloser Gast ueber Anbieter-
Autoritaet, Stop derselben Erschaffung vor+nach Annahme).

Disziplin (UNVERAENDERT aus R2-F5): echte neue OS-Prozesse
(`subprocess.run`/`subprocess.Popen([sys.executable, "-B", "-c", ...])`),
echte `store.publish_current_save`/`table_admission`-Slots, Monkeypatch NUR
an der Prozessabbruch-Grenze, byteidentische Save-Roundtrips, Vorher-/
Nachher-Inventar statt Fake-Leer-Records, MANIFEST mit {path,sha256,bytes}
je Datei + {argv,cwd,utc_start,utc_end,exit,stdout_path,stderr_path} je
Subprozess.

Methodik-Hinweis T1 (ehrlich dokumentiert, kein stiller Kompromiss): der
ECHTE `scripts/mmo_sim.py`-Einstiegspunkt baut seine `gm_transport_factory`
IMMER gegen eine echte Netzwerk-SL-Anbindung (`adapters.factories.
default_gm_transport_factory` -> `GmOwuiTransport` -> `sl_client.SLSession`,
die OHNE `OPENWEBUI_API_KEY` sofort — vor jedem Socket — mit `RuntimeError`
abbricht); es gibt KEINEN CLI-Schalter, der hier einen Test-Doppel injiziert.
Da KEIN NETZ eine harte Vorgabe ist, deckt T1 zwei Schichten GETRENNT ab:
 (a) T1a -- ein echter `subprocess.run([... , "scripts/mmo_sim.py", ...])`
     mit den woertlichen G1-Flags (`--operator-control-fifo`/
     `--guest-terminal`/`--run-dir`/`--states-dir`) ueber die echte
     argparse-/`main()`-Flaeche: beweist Flag-Parsing, echte FIFO-Anlage
     (`stat.S_ISFIFO`), echten `tisch-anbieten`-Dispatch unter der
     geteilten `run_dir`.
 (b) T1b -- derselbe echte G1-Code (`scripts.mmo_sim._fifo_control_line_
     source`/`_fifo_input_fn`/`_fifo_print_fn`, importiert, NICHT
     nachgebaut) in einem echten NEUEN Interpreter-Prozess, der
     `TuiSession` GENAUSO verdrahtet wie `scripts/mmo_sim.py:main()`, aber
     mit einem Fake NUR an der GM-Transport-Grenze (identische Erlaubnis
     wie jeder bestehende Treiber/Test dieser Suite, z.B. `_FakeTableGm`/
     `StopAfterResponseGmTransport`) -- das echte `/stop` wird dabei
     TATSAECHLICH ueber die reale Kontroll-FIFO zugestellt (der Fake
     schreibt NUR das Steuerwort in die echte Pipe und wartet kontrolliert
     auf die durable Bestaetigung, KEIN Zufallstiming, KEIN direkter
     `table_admission`-Aufruf aus dem Fake selbst).

Export: fuer jede Familie werden die realen Ergebniswurzeln VOR der
Tempverzeichnis-Bereinigung nach `run/r3/results/<familie>/` kopiert;
bewusst NICHT entstandene Kategorien werden als Vorher-/Nachher-Inventar in
`inventory.json` dokumentiert, NIE als leerer Fake-Record. `run/r3/results/
MANIFEST.json` bindet je kopierte Datei {path, sha256, bytes} und je echtem
Subprozesslauf {argv, cwd, utc_start, utc_end, exit, stdout_path,
stderr_path}.

Pure Python, nur `assert`, echter Exitcode, kein pytest."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402
from _section_completion_resume_fixtures import (  # noqa: E402
    COMPLETION_MARKER, ScriptedDriver, ScriptedGmTransport, debrief_with_marker,
    harvest_extractor, seed_persona_state,
)

import mmo_sim.core.admission as admission  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
import mmo_sim.core.table_admission as table_admission  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss import creation_service as creation_grants  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_TODAY = "2026-11-04"
_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
_RESULTS_ROOT = Path("/home/altair/zr-betreiber-gast-20261103/run/r3/results")

_MANIFEST: dict = {"files": [], "runs": []}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _utc(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))


def _export_file(szene: str, src: Path, rel: str) -> None:
    dest = _RESULTS_ROOT / szene / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    _MANIFEST["files"].append({
        "path": str(dest.relative_to(_RESULTS_ROOT)),
        "sha256": _sha256(dest),
        "bytes": dest.stat().st_size,
    })


def _export_tree(szene: str, src_root: Path, rel_root: str) -> None:
    if not src_root.exists():
        return
    for p in sorted(src_root.rglob("*")):
        if p.is_file():
            rel = str(Path(rel_root) / p.relative_to(src_root))
            _export_file(szene, p, rel)


def _write_export_json(szene: str, rel: str, data: object) -> None:
    dest = _RESULTS_ROOT / szene / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    _MANIFEST["files"].append({
        "path": str(dest.relative_to(_RESULTS_ROOT)),
        "sha256": _sha256(dest),
        "bytes": dest.stat().st_size,
    })


def _clean_env() -> dict:
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    # KEIN NETZ (Hartes Verbot): die echte GM-Factory bricht ohne
    # OPENWEBUI_API_KEY sofort (VOR jedem Socket) ab -- dieselbe Garantie
    # wird hier explizit erzwungen, unabhaengig von der Elternumgebung.
    env.pop("OPENWEBUI_API_KEY", None)
    env.pop("MMO_SIM_PERSONA_CLI", None)
    env.pop("MMO_SIM_PERSONA_API_BASE_URL", None)
    return env


def _fill_script(template: str, **kwargs) -> str:
    """Ersetzt `@@name@@`-Platzhalter durch `repr(value)` -- vermeidet
    Kollisionen zwischen `str.format()`-Platzhaltern und literalen
    geschweiften Klammern (dict/json-Literale) in den Subprozess-Skripten."""
    out = template
    for key, value in kwargs.items():
        out = out.replace(f"@@{key}@@", repr(value))
    return out


def _run_real_subprocess(szene: str, label: str, argv: list[str], **kw) -> subprocess.CompletedProcess:
    cwd = kw.pop("cwd", None)
    timeout = kw.pop("timeout", 60)
    utc_start = _utc(time.time())
    result = subprocess.run(argv, capture_output=True, text=True, cwd=cwd, timeout=timeout, **kw)
    utc_end = _utc(time.time())
    out_dir = _RESULTS_ROOT / szene
    out_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = out_dir / f"{label}.stdout.txt"
    stderr_path = out_dir / f"{label}.stderr.txt"
    stdout_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")
    for p in (stdout_path, stderr_path):
        _MANIFEST["files"].append({
            "path": str(p.relative_to(_RESULTS_ROOT)), "sha256": _sha256(p), "bytes": p.stat().st_size,
        })
    _MANIFEST["runs"].append({
        "szene": szene, "label": label, "argv": argv, "cwd": str(cwd) if cwd else None,
        "utc_start": utc_start, "utc_end": utc_end, "exit": result.returncode,
        "stdout_path": str(stdout_path.relative_to(_RESULTS_ROOT)),
        "stderr_path": str(stderr_path.relative_to(_RESULTS_ROOT)),
    })
    return result


def _record_background_run(
    szene: str, label: str, argv: list[str], cwd, utc_start: str, utc_end: str,
    exit_code: int, stdout_text: str, stderr_text: str,
) -> None:
    """Wie `_run_real_subprocess`, aber fuer einen bereits via `Popen`
    (konkurrierend zur FIFO-Interaktion des Treibers) gelaufenen echten
    Subprozess -- derselbe Manifest-/Export-Vertrag (stdout/stderr als
    eigene Dateien, Laufmetadaten in `_MANIFEST['runs']`), nur dass argv/
    cwd/Exit/Ausgaben vom Aufrufer statt von `subprocess.run` selbst kommen."""
    out_dir = _RESULTS_ROOT / szene
    out_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = out_dir / f"{label}.stdout.txt"
    stderr_path = out_dir / f"{label}.stderr.txt"
    stdout_path.write_text(stdout_text, encoding="utf-8")
    stderr_path.write_text(stderr_text, encoding="utf-8")
    for p in (stdout_path, stderr_path):
        _MANIFEST["files"].append({
            "path": str(p.relative_to(_RESULTS_ROOT)), "sha256": _sha256(p), "bytes": p.stat().st_size,
        })
    _MANIFEST["runs"].append({
        "szene": szene, "label": label, "argv": argv, "cwd": str(cwd) if cwd else None,
        "utc_start": utc_start, "utc_end": utc_end, "exit": exit_code,
        "stdout_path": str(stdout_path.relative_to(_RESULTS_ROOT)),
        "stderr_path": str(stderr_path.relative_to(_RESULTS_ROOT)),
    })


def _drain_lines(f, settle: float = 0.4, overall_timeout: float = 20.0) -> list[str]:
    """Liest alle gerade verfuegbaren Zeilen aus einer echten FIFO, bis
    `settle` Sekunden lang nichts Neues mehr ankommt (oder EOF/Timeout) --
    robuster als eine feste Anzahl `readline()`-Aufrufe, weil ein einzelner
    mehrzeiliger `print_fn`-Aufruf (z.B. ein kompletter Debrief-Block) ueber
    mehrere Zeilen im selben FIFO-Puffer ankommt."""
    import select
    lines: list[str] = []
    deadline = time.time() + overall_timeout
    last_data_at = None
    while time.time() < deadline:
        ready, _, _ = select.select([f], [], [], 0.1)
        if ready:
            line = f.readline()
            if line == "":
                break
            lines.append(line)
            last_data_at = time.time()
        elif last_data_at is not None and time.time() - last_data_at > settle:
            break
    return lines


# ───────────────────────── Familie T1 ─────────────────────────
# G1 (GUEST-OPERATOR.md B1), G5/O1-O3/O6 (Betreiber OHNE Figur, Gast MIT
# echter persoenlicher Datei; Stop gewinnt VOR Planannahme ueber den
# ECHTEN Launcher/FIFO-Bedienweg).

_T1_ROUND_SCRIPT = r"""
import os, sys, time, json
from pathlib import Path
sys.path.insert(0, @@repo_root@@)
sys.path.insert(0, @@fixtures_dir@@)

import scripts.mmo_sim as launcher  # echter G1-Code, nicht nachgebaut
import mmo_sim.core.admission as admission
import mmo_sim.core.table_admission as table_admission
import mmo_sim.core.store as store
from mmo_sim.domain.zeitriss import catalog, onboarding
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator
from mmo_sim.ui.tui import TuiSession
from _full_v7_fixture import full_v7_save

run_dir = Path(@@run_dir@@)
states_dir = Path(@@states_dir@@)
schema_path = Path(@@schema_path@@)
ctrl_fifo = Path(@@ctrl_fifo@@)
in_fifo = Path(@@in_fifo@@)
out_fifo = Path(@@out_fifo@@)
guest_onboarding = Path(@@guest_onboarding@@)
guest_catalog = Path(@@guest_catalog@@)
op_onboarding = Path(@@op_onboarding@@)
op_catalog = Path(@@op_catalog@@)

launcher._ensure_fifo(ctrl_fifo)
launcher._ensure_fifo(in_fifo)
launcher._ensure_fifo(out_fifo)


class StopViaRealControlFifoGm:
    # G1-Beleg (Fake NUR an der GM-Transport-Grenze, wie
    # StopAfterResponseGmTransport/_FakeTableGm anderswo in dieser Suite):
    # liefert die EINE gescriptete Antwort normal, schreibt danach "/stop"
    # in die ECHTE Kontroll-FIFO (derselbe Zustellweg, den ein Betreiber
    # ueber --operator-control-fifo benutzen wuerde) und wartet kontrolliert
    # (kein Zufallstiming) auf die durable Bestaetigung, BEVOR es
    # zurueckkehrt -- ein zweiter GM-Turn waere ein Testversagen (Stop
    # haette vor der Planannahme gewinnen muessen).
    def __init__(self, first_content, run_dir, ctrl_fifo):
        self._first_content = first_content
        self.calls = 0
        self._run_dir = run_dir
        self._ctrl_fifo = ctrl_fifo
        self.table_id = None

    def turn(self, turn_idx, user_text, **kw):
        self.calls += 1
        if self.calls > 1:
            raise AssertionError(
                "StopViaRealControlFifoGm: kein zweiter GM-Turn erwartet -- der Stop ueber die "
                "echte Kontroll-FIFO haette vor der Planannahme gewinnen muessen."
            )
        content = self._first_content
        fd = os.open(str(self._ctrl_fifo), os.O_WRONLY)
        with os.fdopen(fd, "w") as f:
            f.write("/stop\n")
        deadline = time.time() + 20
        while time.time() < deadline:
            stopped, _reason = admission.read_table_stop(self._run_dir, self.table_id)
            if stopped:
                break
            time.sleep(0.02)
        else:
            raise AssertionError("T1: Stop wurde nicht rechtzeitig durabel ueber die Kontroll-FIFO.")
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": f"c{turn_idx}"}


_gm_holder = {}


def _gm_factory(table_id):
    gm = StopViaRealControlFifoGm("SL-Antwort auf Anker.", run_dir, ctrl_fifo)
    gm.table_id = table_id
    _gm_holder["gm"] = gm
    return gm


guest_session = TuiSession(
    onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id="guest1",
    input_fn=launcher._fifo_input_fn(in_fifo), print_fn=launcher._fifo_print_fn(out_fifo),
    run_dir=run_dir, host_capable=False,
)
operator_session = TuiSession(
    onboarding_dir=op_onboarding, catalog_dir=op_catalog, participant_id="operator1",
    run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
    gm_transport_factory=_gm_factory, host_capable=True,
)
# G1: EXAKT der Aufruf-Vertrag von TuiSession(input_fn=..., print_fn=...)/
# register_guest_terminal/operator_control_line_source -- echte
# Konstruktorparameter, kein Testshim.
operator_session.operator_control_line_source = launcher._fifo_control_line_source(ctrl_fifo)

operator_session._cmd_table_offer(["mesaT1"])
guest_session._cmd_table_request_join(["mesaT1"])
operator_session._cmd_table_accept(["mesaT1", "guest1"])
operator_session.register_guest_terminal("guest1", guest_session)

operator_session._cmd_table_start(["mesaT1"])

# Fortsetzbarkeit nach dem echten Abbruch: Betreiber bietet einen zweiten
# Tisch an (fuer den T1-Nachweis "neue Tischsuche/-anfrage ueber den
# normalen Produktweg" in einem SPAETEREN frischen Prozess).
operator_session._cmd_table_offer(["mesaT1-retry"])

print(json.dumps({
    "gm_calls": _gm_holder["gm"].calls,
    "table_id": _gm_holder["gm"].table_id,
}))
"""

_T1_FRESH_READER_SCRIPT = r"""
import json, sys
from pathlib import Path
sys.path.insert(0, @@repo_root@@)
sys.path.insert(0, @@fixtures_dir@@)

import mmo_sim.core.table_admission as table_admission
from mmo_sim.ui.tui import TuiSession

run_dir = Path(@@run_dir@@)
guest_onboarding = Path(@@guest_onboarding@@)
guest_catalog = Path(@@guest_catalog@@)

# Echter neuer Prozess, rein dateibasiert -- KEINE Objektreferenz auf die
# alte guest_session. host_capable=False (Gast), run_dir geteilt (neue
# Tischsuche/-anfrage ueber dieselbe Anbieterwurzel).
fresh = TuiSession(
    onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id="guest1",
    run_dir=run_dir, host_capable=False,
)
resolved = fresh._resolve_member("guest1")
assert resolved is not None, "T1d: frischer Leser haette die eigene Figur finden muessen."
resolved_save, resolved_char = resolved

open_tables = sorted(r["table_key"] for r in table_admission.list_open_tables(run_dir))
request_join_ok = True
try:
    before = table_admission.load_record(run_dir, "mesaT1-retry")
    fresh._cmd_table_request_join(["mesaT1-retry"])
    after = table_admission.load_record(run_dir, "mesaT1-retry")
    request_join_ok = "guest1" in after.get("requests", []) and "guest1" not in (before or {}).get("requests", [])
except Exception:
    request_join_ok = False

print(json.dumps({
    "resolved_char_id": resolved_char, "resolved_save": resolved_save,
    "found_open_tables": open_tables, "request_join_ok": request_join_ok,
}))
"""


def _t1_cli_literal_smoke(root: Path) -> None:
    """T1a: der WOERTLICHE `scripts/mmo_sim.py`-Einstiegspunkt (echte
    argparse-Flaeche, echter `main()`) mit den G1-Flags -- beweist
    Flag-Parsing, echte FIFO-Anlage (`_ensure_fifo`, `stat.S_ISFIFO`) und
    echten `tisch-anbieten`-Dispatch unter der geteilten `run_dir`. KEIN
    Rundenstart hier (0 `gm_transport_factory`-Aufrufe, 0 Netz -- s.
    Moduldocstring)."""
    szene = "t1"
    cli_root = root / "cli_smoke"
    op_data = cli_root / "operator_data"
    shared_run = cli_root / "run"
    shared_states = cli_root / "states"
    fifo_dir = cli_root / "fifos"
    ctrl_fifo = fifo_dir / "ctrl.fifo"
    in_fifo = fifo_dir / "guest_in.fifo"
    out_fifo = fifo_dir / "guest_out.fifo"

    result = _run_real_subprocess(
        szene, "t1a_cli_literal_smoke",
        [
            sys.executable, "-B", str(_REPO_ROOT / "scripts" / "mmo_sim.py"),
            "--participant", "opcli1", "--data-dir", str(op_data),
            "--run-dir", str(shared_run), "--states-dir", str(shared_states),
            "--operator-control-fifo", str(ctrl_fifo),
            "--guest-terminal", f"guestcli1:{in_fifo}:{out_fifo}",
        ],
        cwd=str(_REPO_ROOT), input="tisch-anbieten mesaCliSmoke\nx\n", env=_clean_env(),
    )
    assert result.returncode == 0, f"T1a: echter CLI-Lauf ist unerwartet fehlgeschlagen: {result.stderr}"
    assert "Tisch 'mesaCliSmoke' offen" in result.stdout, result.stdout
    for p in (ctrl_fifo, in_fifo, out_fifo):
        assert p.exists() and stat.S_ISFIFO(p.stat().st_mode), (
            f"T1a: '{p}' haette von '_ensure_fifo' als echte Named Pipe angelegt werden muessen."
        )
    record = table_admission.load_record(shared_run, "mesaCliSmoke")
    assert record is not None and record["host_id"] == "opcli1", record
    _write_export_json(szene, "t1a_cli_literal_smoke.json", {
        "argv_tail": ["--operator-control-fifo", "--guest-terminal", "--run-dir", "--states-dir"],
        "fifos_real_namedpipes": {str(p.name): stat.S_ISFIFO(p.stat().st_mode) for p in (ctrl_fifo, in_fifo, out_fifo)},
        "table_admission_record": record,
        "notes": [
            "T1a beweist NUR die argparse-/main()-Flaeche + echte FIFO-Anlage + 'tisch-anbieten' "
            "ueber den geteilten run_dir -- 0 gm_transport_factory-Aufrufe (kein Rundenstart), "
            "also 0 Netzkontakt (s. Moduldocstring 'Methodik-Hinweis T1').",
        ],
    })


def run_family_t1() -> None:
    szene = "t1"
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)

        # (a) CLI-literale Flaeche.
        _t1_cli_literal_smoke(root)

        # (b) G1-FIFO-Rundenweg + echtes Stop-vor-Planannahme-Rennen.
        shared_run = root / "run"
        shared_states = root / "states"
        shared_states.mkdir(parents=True)
        write_test_profile(shared_run, max_turns=200)

        guest_onboarding = root / "guest_onboarding"
        guest_catalog = root / "guest_catalog"
        op_onboarding = root / "op_onboarding"
        op_catalog = root / "op_catalog"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        ctrl_fifo = fifo_dir / "ctrl.fifo"
        in_fifo = fifo_dir / "guest_in.fifo"
        out_fifo = fifo_dir / "guest_out.fifo"

        # Echte persoenliche Gastdatei (Produktaufrufe, KEIN Fake-Dict):
        # Betreiber OHNE eigene Figur, Gast MIT echter persoenlicher Datei.
        start_save = full_v7_save("chrono-t1-guest", name="GastT1", save_id="fixture-t1-guest-001")
        onboarding.start_or_resume(guest_onboarding, "guest1")
        onboarding.complete_with_save(guest_onboarding, "guest1", start_save, ZeitrissHarvestValidator(), "chrono-t1-guest")
        catalog.register(guest_catalog, catalog.CatalogEntry(
            participant_id="guest1", chrononaut_id="chrono-t1-guest", persona_key="guest1",
        ))
        catalog.store_figure_save(guest_catalog, "guest1", "chrono-t1-guest", start_save)

        script = _fill_script(_T1_ROUND_SCRIPT,
            repo_root=str(_REPO_ROOT), fixtures_dir=str(_HERE),
            run_dir=str(shared_run), states_dir=str(shared_states), schema_path=str(_SCHEMA_PATH),
            ctrl_fifo=str(ctrl_fifo), in_fifo=str(in_fifo), out_fifo=str(out_fifo),
            guest_onboarding=str(guest_onboarding), guest_catalog=str(guest_catalog),
            op_onboarding=str(op_onboarding), op_catalog=str(op_catalog),
        )
        clean_env = _clean_env()
        utc_start = _utc(time.time())
        proc = subprocess.Popen(
            [sys.executable, "-B", "-c", script], cwd=str(_REPO_ROOT), env=clean_env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            # Kontrollierte Barriere (kein Zufallstiming): die FIFOs werden
            # vom Subprozess selbst angelegt (`launcher._ensure_fifo`) --
            # auf die reale Dateianlage warten, BEVOR geoeffnet wird.
            _deadline = time.time() + 20
            while time.time() < _deadline and not (in_fifo.exists() and out_fifo.exists()):
                time.sleep(0.02)
            assert in_fifo.exists() and out_fifo.exists(), "T1b: Gast-FIFOs wurden nicht rechtzeitig angelegt."
            # Echte Gastantwort ueber die ECHTE Gast-FIFO (derselbe
            # Zustellweg wie --guest-terminal): der Gast sieht zuerst die
            # Anfrage-Quittung, dann die Zweck-Zeile, antwortet EINMAL
            # (Anker-Zug, echte persoenliche Figur wird vom Produkt am
            # ersten Zug angehaengt). Der admission-Gate-Check vor JEDEM
            # weiteren Zug (`core.runtime._check_gate`) laeuft VOR dem
            # naechsten Prompt -- gewinnt der Stop (hier garantiert, s.
            # `StopViaRealControlFifoGm`), wird der Gast KEIN zweites Mal
            # mehr befragt; die echte SL-Antwort erscheint dadurch NICHT
            # auf dem Gastbildschirm, sondern im OEFFENTLICHEN Betreiber-
            # Zuschauerverlauf (s. unten, operator stdout).
            out_fd = os.open(str(out_fifo), os.O_RDONLY)
            out_f = os.fdopen(out_fd, "r")
            in_fd = os.open(str(in_fifo), os.O_WRONLY)
            in_f = os.fdopen(in_fd, "w")
            seen: list[str] = []
            seen.append(out_f.readline())  # Anfrage-Quittung
            seen.append(out_f.readline())  # Zweck-Zeile vor dem Prompt
            in_f.write("Ich erkunde die Gegend.\n")
            in_f.flush()
            stdout_text, stderr_text = proc.communicate(timeout=30)
        finally:
            try:
                in_f.close()
            except Exception:
                pass
            try:
                out_f.close()
            except Exception:
                pass
        utc_end = _utc(time.time())
        _record_background_run(
            szene, "t1b_fifo_round_stop_race", [sys.executable, "-B", "-c", "<siehe t1b_fifo_round_stop_race.script.py>"],
            str(_REPO_ROOT), utc_start, utc_end, proc.returncode, stdout_text, stderr_text,
        )
        _write_export_json(szene, "t1b_fifo_round_stop_race.script.py", script)
        assert proc.returncode == 0, f"T1b: FIFO-Rundenprozess ist unerwartet fehlgeschlagen: {stderr_text}"
        payload = json.loads(stdout_text.strip().splitlines()[-1])
        assert payload["gm_calls"] == 1, (
            f"T1b: genau EIN GM-Turn (Anker) erwartet, Stop haette den zweiten verhindern muessen: {payload}"
        )
        table_id = payload["table_id"]
        assert table_id == "local-guest1", table_id
        # Oeffentlicher Verlauf (Zuschauersicht, vom Betreiber-Prozess nach
        # dem Abbruch automatisch gedruckt): die echte SL-Antwort erscheint
        # hier, NICHT auf dem Gastbildschirm (s. Kommentar oben -- der
        # Gate-Check vor Zug 2 hat den Gast nie wieder befragt).
        assert "[Zuschauer][SL] SL-Antwort auf Anker." in stdout_text, stdout_text
        assert any("Anfrage an Tisch 'mesaT1' gestellt" in line for line in seen), seen

        # (c) Produktbelege nach dem echten Abbruch.
        stopped, stop_reason = admission.read_table_stop(shared_run, table_id)
        assert stopped is True and "stop" in stop_reason.lower() or "/stop" in stop_reason, (stopped, stop_reason)
        decision = admission.read_table_decision(shared_run, table_id)
        assert decision is not None and decision.get("decision") == "stopped", decision
        record = table_admission.load_record(shared_run, "mesaT1")
        assert record is not None and record["state"] == table_admission.STATE_CLOSED, record
        section = store.Table.load(shared_run, table_id)
        assert section.status == "closed", f"T1: KEIN aktiver Core-Tisch als abgeschlossener Nutzerabbruch erwartet: {section.status}"
        # `app_service.run_play_session`/`_run_table_round` reichen
        # `f"{table.table_id}-section"` (NICHT `table.table_id` selbst) als
        # `section_id` an `store.complete_section` durch -- das ist der
        # Schluessel, unter dem `__plan.json`/`__final.json` abgelegt werden.
        completion_section_id = f"{table_id}-section"
        plan_path = shared_run / "completion" / f"{completion_section_id}__plan.json"
        final_path = shared_run / "completion" / f"{completion_section_id}__final.json"
        assert not plan_path.exists(), "T1: kein __plan.json -- die Planannahme hat den Stop verloren."
        assert not final_path.exists(), "T1: kein __final.json."

        # Byte-Identitaet: die bereits bei Annahme hostseitig uebernommene
        # persoenliche Gastfigur bleibt vom Abbruch unberuehrt.
        guest_current_path = shared_run / "current_saves" / "guest1.json"
        assert guest_current_path.exists(), "guest1 haette bei Annahme hostseitig uebernommen werden muessen."
        sha_guest_current = _sha256(guest_current_path)
        guest_figure_path = guest_catalog / "figures" / "guest1__chrono-t1-guest.json"
        assert guest_figure_path.exists(), guest_figure_path
        sha_guest_private = _sha256(guest_figure_path)

        # Figurenbindung freigegeben (02 §C-Lifecycle): chrono-t1-guest ist
        # NICHT mehr an den toten Tisch gebunden.
        active_binding = store.chrononaut_active_binding(shared_run, "chrono-t1-guest")
        assert active_binding is False, f"T1: Figurenbindung haette am sicheren Ende freigegeben werden muessen: {active_binding}"

        # Enge Probe (G5/O6, "offener Personaaufruf ueber denselben
        # Mechanismus"): derselbe table_id-adressierte Admission-Gate-Check
        # (`core.runtime._check_gate` -> `read_admission_block`), den JEDER
        # Treiber durchlaeuft (Mensch UND Persona, s. `core/runtime.py:
        # act()` -- `_check_gate` laeuft UNBEDINGT nach dem is_human-Zweig),
        # blockt denselben Tisch auch mit persona-typischen Parametern
        # (dollar_billed=False, eigene Route) -- derselbe durable Stop,
        # keine zweite Autoritaet fuer Personas.
        persona_blocked, persona_reason = admission.read_admission_block(
            shared_run, reserved_usd=0.01, output_bound_known=True, route="persona-route",
            dollar_billed=False, table_id=table_id,
        )
        assert persona_blocked is True, (
            f"T1: derselbe Stop haette auch einen offenen Personaaufruf (enge Probe) blocken muessen: {persona_reason}"
        )

        # (d) Fortsetzbarkeit: NEUER Prozess liest die unveraenderte private
        # Figur ueber den Produktleser und erreicht eine NEUE Tischsuche/
        # -anfrage (mesaT1-retry, vom Betreiber nach dem Abbruch angeboten).
        fresh_script = _fill_script(_T1_FRESH_READER_SCRIPT,
            repo_root=str(_REPO_ROOT), fixtures_dir=str(_HERE),
            run_dir=str(shared_run), guest_onboarding=str(guest_onboarding), guest_catalog=str(guest_catalog),
        )
        fresh = _run_real_subprocess(
            szene, "t1d_fresh_process_rejoin", [sys.executable, "-B", "-c", fresh_script],
            cwd=str(_REPO_ROOT), env=clean_env,
        )
        assert fresh.returncode == 0, f"T1d: frischer Leseprozess ist unerwartet fehlgeschlagen: {fresh.stderr}"
        fresh_payload = json.loads(fresh.stdout.strip().splitlines()[-1])
        assert fresh_payload["resolved_char_id"] == "chrono-t1-guest", fresh_payload
        assert fresh_payload["resolved_save"]["save_id"] == "fixture-t1-guest-001", fresh_payload
        # mesaT1 ist nach dem echten Abbruch 'closed' (kein offenes Angebot
        # mehr) -- NUR mesaT1-retry ist jetzt sichtbar offen.
        assert fresh_payload["found_open_tables"] == ["mesaT1-retry"], fresh_payload
        assert fresh_payload["request_join_ok"] is True, fresh_payload

        after_guest_current_sha = _sha256(guest_current_path)
        after_guest_private_sha = _sha256(guest_figure_path)
        assert after_guest_current_sha == sha_guest_current, "T1: hostseitiger Gast-Current wurde trotz Stop veraendert."
        assert after_guest_private_sha == sha_guest_private, "T1: private Gastfigur wurde trotz Stop veraendert."

        # (e) Export VOR Tempverzeichnis-Bereinigung.
        _export_tree(szene, shared_run, "run")
        _export_tree(szene, shared_states, "states")
        _export_tree(szene, guest_onboarding, "guest_onboarding")
        _export_tree(szene, guest_catalog, "guest_catalog")
        _export_tree(szene, op_onboarding, "op_onboarding")
        _export_tree(szene, op_catalog, "op_catalog")
        _write_export_json(szene, "t1b_io_transcript.json", {"guest_out_seen": seen})
        _write_export_json(szene, "inventory.json", {
            "before": {
                "guest_current_sha256": sha_guest_current, "guest_private_sha256": sha_guest_private,
                "plan_exists": False, "final_exists": False,
            },
            "after": {
                "guest_current_sha256": after_guest_current_sha, "guest_private_sha256": after_guest_private_sha,
                "plan_exists": plan_path.exists(), "final_exists": final_path.exists(),
                "chrononaut_active_binding": active_binding,
            },
            "notes": [
                "kein __plan.json/__final.json -- der echte Kontroll-FIFO-Stop hat den gemeinsamen "
                "atomaren Entscheid-Slot VOR dem Debrief/Markeraustausch gewonnen (nur EIN GM-Turn, "
                "der Anker, lief ueberhaupt); bewusst keine leeren Fake-Records.",
                "T1a (CLI-literal) und T1b (FIFO-Rundenweg+Stop-Rennen) sind GETRENNTE echte "
                "Subprozess-Nachweise, s. Moduldocstring 'Methodik-Hinweis T1' fuer die Begruendung "
                "(KEIN NETZ verbietet einen vollen Rundenlauf ueber den woertlichen, unveraenderten "
                "scripts/mmo_sim.py-Einstiegspunkt, dessen gm_transport_factory IMMER echtes Netz "
                "braucht).",
            ],
        })


# ───────────────────────── Familie T2 ─────────────────────────
# G2 (/abbrechen ehrt plan_committed), G5/O4 (Plan gewinnt; Teilpublikation,
# Stop, menschliche Abschlussnotiz) -- integrativ ueber den ECHTEN
# TUI-/table_admission-Betreiberweg (register_guest_terminal/
# operator_table_key), NICHT nur den rohen `core.runtime.SectionRuntime`-
# Aufruf (das deckt bereits die bestehende, UNVERAENDERTE R2-F5-Szene O4).
#
# GEFUNDENER PRODUKTDEFEKT (nicht selbst gefixt, s. Report): ein echter
# Prozessneustart, der einen table_admission-/register_guest_terminal-
# admittierten Gast-Leader (KEIN lokal via ParticipantRegistry
# registrierter Mensch) fortsetzen will, schlaegt in
# `TuiSession._resume_bound_table` fehl -- `_is_persona_member(leader_id)`
# kennt NUR `self.participant_id` (die resuemierende Session selbst) UND
# die lokale `ParticipantRegistry` (A24, geteiltes Geraet), NICHT aber
# `register_guest_terminal`/table_admission-Gaeste. Der Leader wird
# faelschlich als KI-Persona eingestuft ("Fortsetzen nicht moeglich:
# KI-Leader 'guest1' erfordert eine konfigurierte Persona-Anbindung"),
# obwohl er ein echter Mensch mit echter persoenlicher Figur ist. Dieser
# Treiber dokumentiert den echten Fehlertext (Prozess 2 unten) und WEICHT
# fuer den "echter neuer Prozess fuehrt die Pflicht-Reflexion/Finalisierung
# zu Ende"-Nachweis bewusst auf denselben CORE-Layer-Mechanismus aus, den
# die bestehende, UNVERAENDERTE R2-F5-Szene O4 bereits akzeptiert hat
# (`core.runtime.SectionRuntime` + `ReflectionOnlyDriver`, KEIN TUI-Resume).

_T2_PROCESS1_HARDEXIT_SCRIPT = r"""
import os, sys, time, json
from pathlib import Path
sys.path.insert(0, @@repo_root@@)
sys.path.insert(0, @@fixtures_dir@@)

import mmo_sim.core.runtime as runtime_mod
import mmo_sim.core.table_admission as table_admission
from mmo_sim.domain.zeitriss import catalog, onboarding
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator
from mmo_sim.ui.tui import TuiSession
from _full_v7_fixture import full_v7_save

run_dir = Path(@@run_dir@@)
states_dir = Path(@@states_dir@@)
schema_path = Path(@@schema_path@@)
in_fifo = Path(@@in_fifo@@)
out_fifo = Path(@@out_fifo@@)
guest_onboarding = Path(@@guest_onboarding@@)
guest_catalog = Path(@@guest_catalog@@)
op_onboarding = Path(@@op_onboarding@@)
op_catalog = Path(@@op_catalog@@)
table_key = @@table_key@@


def _hard_exit_before_reflection(*_a, **_kw):
    # Dieselbe Technik wie die bestehenden StopAfterResponseGmTransport/
    # _hard_kill_after_durable_persist-Fixtures (R2-F5 O4): ein
    # Klassen-Monkeypatch GENAU an der Prozessabbruch-Grenze -- Phase 1
    # (store.complete_section: Plan-Pin + Primaersave) ist zu diesem
    # Zeitpunkt bereits real abgeschlossen; kein veraenderter Produktpfad.
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(94)


runtime_mod.SectionRuntime._collect_reflections = _hard_exit_before_reflection


class ScriptedGm:
    def __init__(self, contents):
        self._c = list(contents)
        self.calls = 0

    def turn(self, turn_idx, user_text, **kw):
        self.calls += 1
        content = self._c.pop(0) if self._c else ""
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": f"c{turn_idx}"}


if not in_fifo.exists():
    os.mkfifo(in_fifo)
if not out_fifo.exists():
    os.mkfifo(out_fifo)

_in_state = {"f": None}
_out_state = {"f": None}


def _read_fifo_line(prompt=""):
    if _in_state["f"] is None:
        _in_state["f"] = open(in_fifo, "r", encoding="utf-8")
    line = _in_state["f"].readline()
    if line == "":
        raise EOFError("Gast-FIFO geschlossen (EOF).")
    return line.rstrip("\n")


def _write_fifo_line(text):
    if _out_state["f"] is None:
        fd = os.open(str(out_fifo), os.O_RDWR)
        _out_state["f"] = os.fdopen(fd, "w", encoding="utf-8")
    _out_state["f"].write(text + "\n")
    _out_state["f"].flush()


guest_session = TuiSession(
    onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id="guest1",
    input_fn=_read_fifo_line, print_fn=_write_fifo_line,
    run_dir=run_dir, host_capable=False,
)

debrief_save = full_v7_save("chrono-t2-guest", name="GastT2", save_id="fixture-t2-guest-002", level=2)
debrief_text = (
    "Abschnitt beendet.\n```json\n" + json.dumps(debrief_save) + "\n```\nSECTION-ABSCHLUSS-BESTAETIGT"
)
gm = ScriptedGm(["SL-Antwort auf Anker.", debrief_text])

operator_session = TuiSession(
    onboarding_dir=op_onboarding, catalog_dir=op_catalog, participant_id="operator1",
    run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
    gm_transport_factory=lambda: gm, host_capable=True,
)

operator_session._cmd_table_offer([table_key])
guest_session._cmd_table_request_join([table_key])
operator_session._cmd_table_accept([table_key, "guest1"])
operator_session.register_guest_terminal("guest1", guest_session)

operator_session._cmd_table_start([table_key])
print(json.dumps({"unexpected_normal_return": True, "gm_calls": gm.calls}))
"""

_T2_PROCESS2_RESUME_ATTEMPT_SCRIPT = r"""
import json, sys
from pathlib import Path
sys.path.insert(0, @@repo_root@@)
sys.path.insert(0, @@fixtures_dir@@)

from mmo_sim.ui.tui import TuiSession

run_dir = Path(@@run_dir@@)
states_dir = Path(@@states_dir@@)
schema_path = Path(@@schema_path@@)
op_onboarding = Path(@@op_onboarding@@)
op_catalog = Path(@@op_catalog@@)
table_key = @@table_key@@


class ExplodingGmTransport:
    def turn(self, *a, **kw):
        raise AssertionError("kein GM-Turn erwartet (dieser Prozess testet nur den Resume-Versuch).")


# Echter NEUER Prozess, KEINE Objektreferenz auf Prozess 1 -- versucht den
# NORMALEN Produktweg (erneutes 'tisch-start' auf denselben table_key, der
# bestehende Reconcile-/Resume-Zweig in `_cmd_table_start`).
fresh_operator = TuiSession(
    onboarding_dir=op_onboarding, catalog_dir=op_catalog, participant_id="operator1",
    run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
    gm_transport_factory=lambda: ExplodingGmTransport(), host_capable=True,
)
printed = []
fresh_operator._print = printed.append
fresh_operator._cmd_table_start([table_key])
print(json.dumps({"printed": printed}))
"""

_T2_PROCESS_G2_STANDALONE_SCRIPT = r"""
import os, sys, json
from pathlib import Path
sys.path.insert(0, @@repo_root@@)
sys.path.insert(0, @@fixtures_dir@@)

from mmo_sim.domain.zeitriss import catalog, onboarding
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator
from mmo_sim.ui.tui import TuiSession
from _full_v7_fixture import full_v7_save

run_dir = Path(@@run_dir@@)
states_dir = Path(@@states_dir@@)
schema_path = Path(@@schema_path@@)
in_fifo = Path(@@in_fifo@@)
out_fifo = Path(@@out_fifo@@)
guest_onboarding = Path(@@guest_onboarding@@)
guest_catalog = Path(@@guest_catalog@@)
op_onboarding = Path(@@op_onboarding@@)
op_catalog = Path(@@op_catalog@@)
table_key = @@table_key@@

if not in_fifo.exists():
    os.mkfifo(in_fifo)
if not out_fifo.exists():
    os.mkfifo(out_fifo)
_in_state = {"f": None}
_out_state = {"f": None}


def _read_fifo_line(prompt=""):
    if _in_state["f"] is None:
        _in_state["f"] = open(in_fifo, "r", encoding="utf-8")
    line = _in_state["f"].readline()
    if line == "":
        raise EOFError("Gast-FIFO geschlossen (EOF).")
    return line.rstrip("\n")


def _write_fifo_line(text):
    if _out_state["f"] is None:
        fd = os.open(str(out_fifo), os.O_RDWR)
        _out_state["f"] = os.fdopen(fd, "w", encoding="utf-8")
    _out_state["f"].write(text + "\n")
    _out_state["f"].flush()


start_save = full_v7_save("chrono-t2g2-guest", name="GastT2G2", save_id="fixture-t2g2-guest-001")
onboarding.start_or_resume(guest_onboarding, "guest2")
onboarding.complete_with_save(guest_onboarding, "guest2", start_save, ZeitrissHarvestValidator(), "chrono-t2g2-guest")
catalog.register(guest_catalog, catalog.CatalogEntry(
    participant_id="guest2", chrononaut_id="chrono-t2g2-guest", persona_key="guest2",
))
catalog.store_figure_save(guest_catalog, "guest2", "chrono-t2g2-guest", start_save)

guest_session = TuiSession(
    onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id="guest2",
    input_fn=_read_fifo_line, print_fn=_write_fifo_line,
    run_dir=run_dir, host_capable=False,
)


class ScriptedGm:
    def __init__(self, contents):
        self._c = list(contents)
        self.calls = 0

    def turn(self, turn_idx, user_text, **kw):
        self.calls += 1
        content = self._c.pop(0) if self._c else ""
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": f"c{turn_idx}"}


debrief_save = full_v7_save("chrono-t2g2-guest", name="GastT2G2", save_id="fixture-t2g2-guest-002", level=2)
debrief_text = (
    "Abschnitt beendet.\n```json\n" + json.dumps(debrief_save) + "\n```\nSECTION-ABSCHLUSS-BESTAETIGT"
)
gm = ScriptedGm(["SL-Antwort auf Anker.", debrief_text])
operator_session = TuiSession(
    onboarding_dir=op_onboarding, catalog_dir=op_catalog, participant_id="operator2",
    run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
    gm_transport_factory=lambda: gm, host_capable=True,
)
operator_session._cmd_table_offer([table_key])
guest_session._cmd_table_request_join([table_key])
operator_session._cmd_table_accept([table_key, "guest2"])
operator_session.register_guest_terminal("guest2", guest_session)
operator_session._cmd_table_start([table_key])
print(json.dumps({"gm_calls": gm.calls}))
"""

_T2_PROCESS_CORE_REAL_FINISH_SCRIPT = r"""
import json, sys
from pathlib import Path
sys.path.insert(0, @@repo_root@@)
sys.path.insert(0, @@fixtures_dir@@)

from _section_completion_resume_fixtures import COMPLETION_MARKER, ReflectionOnlyDriver
import mmo_sim.core.store as store
from mmo_sim.core.controller import TableController
from mmo_sim.core.runtime import SectionRuntime
from mmo_sim.core.persona_state import PersonaStateStore
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy

run_dir = Path(@@run_dir@@)
states_dir = Path(@@states_dir@@)
schema_path = Path(@@schema_path@@)
table_id = @@table_id@@
section_id = @@section_id@@
leader_key = @@leader_key@@


class ExplodingGmTransport:
    def __init__(self):
        self.calls = 0

    def turn(self, *a, **kw):
        self.calls += 1
        raise AssertionError("ExplodingGmTransport: kein neuer GM-Turn nach Plan-Pin/Resume erwartet.")


lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
table = store.Table.load(run_dir, table_id)
ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
gm = ExplodingGmTransport()
leader_refl = ReflectionOnlyDriver(
    "Alles ist gut gelaufen, Debrief abgeschlossen (echte Notiz).", origin_source="fake:leader-reflect-recovery",
)
controller = TableController(leader_key=leader_key, drivers={leader_key: leader_refl})
runtime = SectionRuntime(
    lobby=lobby, table=table, gm_transport=gm, marker=COMPLETION_MARKER,
    harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
    harvest_extractor=lambda text, cid_to_pk: {},
)
outcome = runtime.run_full_section(
    controller, section_id,
    contexts_by_persona={leader_key: {"user": f"ctx-{leader_key}"}},
    states_dir=states_dir, today=@@today@@, ts="2026-11-04T10:10:00",
)
print(json.dumps({
    "success": outcome.completion.success, "reason": outcome.completion.reason,
    "members_completed": outcome.completion.members_completed,
    "gm_calls": gm.calls, "leader_reflection_calls": leader_refl.calls,
}))
"""

_T2_PROCESS_IDEMPOTENT_RETRY_SCRIPT = r"""
import json, sys
from pathlib import Path
sys.path.insert(0, @@repo_root@@)
sys.path.insert(0, @@fixtures_dir@@)

import mmo_sim.core.store as store
from mmo_sim.core.persona_state import PersonaStateStore
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy

run_dir = Path(@@run_dir@@)
states_dir = Path(@@states_dir@@)
schema_path = Path(@@schema_path@@)
table_id = @@table_id@@
section_id = @@section_id@@

lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
table = store.Table.load(run_dir, table_id)
ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
result1 = store.complete_section(
    lobby, table, section_id, {}, states_dir, @@today@@, ZeitrissHarvestValidator(), ps_store,
)
result2 = store.finalize_section_after_reflection(lobby, table, section_id)
print(json.dumps({
    "complete_section_already_completed": result1.already_completed, "complete_section_written": result1.written,
    "finalize_already_completed": result2.already_completed, "finalize_written": result2.written,
}))
"""


def run_family_t2() -> None:
    szene = "t2"
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        shared_run = root / "run"
        shared_states = root / "states"
        shared_states.mkdir(parents=True)
        write_test_profile(shared_run, max_turns=200)

        guest_onboarding = root / "guest_onboarding"
        guest_catalog = root / "guest_catalog"
        op_onboarding = root / "op_onboarding"
        op_catalog = root / "op_catalog"
        in_fifo = root / "guest_in.fifo"
        out_fifo = root / "guest_out.fifo"

        start_save = full_v7_save("chrono-t2-guest", name="GastT2", save_id="fixture-t2-guest-001")
        onboarding.start_or_resume(guest_onboarding, "guest1")
        onboarding.complete_with_save(guest_onboarding, "guest1", start_save, ZeitrissHarvestValidator(), "chrono-t2-guest")
        catalog.register(guest_catalog, catalog.CatalogEntry(
            participant_id="guest1", chrononaut_id="chrono-t2-guest", persona_key="guest1",
        ))
        catalog.store_figure_save(guest_catalog, "guest1", "chrono-t2-guest", start_save)

        common = dict(
            repo_root=str(_REPO_ROOT), fixtures_dir=str(_HERE),
            run_dir=str(shared_run), states_dir=str(shared_states), schema_path=str(_SCHEMA_PATH),
            in_fifo=str(in_fifo), out_fifo=str(out_fifo),
            guest_onboarding=str(guest_onboarding), guest_catalog=str(guest_catalog),
            op_onboarding=str(op_onboarding), op_catalog=str(op_catalog),
            table_key="mesaT2",
        )
        clean_env = _clean_env()

        # ── Prozess 1: echter Spielzug bis Plan-Pin+Primaersave (Phase 1),
        # dann os._exit NACH Plan-Pin/Primaersave, VOR Reflexion (Phase 2).
        script1 = _fill_script(_T2_PROCESS1_HARDEXIT_SCRIPT, **common)
        utc_start = _utc(time.time())
        proc1 = subprocess.Popen(
            [sys.executable, "-B", "-c", script1], cwd=str(_REPO_ROOT), env=clean_env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        deadline = time.time() + 20
        while time.time() < deadline and not (in_fifo.exists() and out_fifo.exists()):
            time.sleep(0.02)
        assert in_fifo.exists() and out_fifo.exists(), "T2: Gast-FIFOs (Prozess 1) nicht rechtzeitig angelegt."
        out_fd = os.open(str(out_fifo), os.O_RDONLY)
        out_f = os.fdopen(out_fd, "r")
        in_fd = os.open(str(in_fifo), os.O_WRONLY)
        in_f = os.fdopen(in_fd, "w")
        batch1 = _drain_lines(out_f)
        in_f.write("Ich erkunde die Gegend.\n")
        in_f.flush()
        batch2 = _drain_lines(out_f)
        in_f.write("Ich gehe weiter.\n")
        in_f.flush()
        stdout1, stderr1 = proc1.communicate(timeout=30)
        in_f.close()
        out_f.close()
        utc_end = _utc(time.time())
        _record_background_run(
            szene, "t2_proc1_plan_pin_primary_save_hard_exit",
            [sys.executable, "-B", "-c", "<siehe t2_proc1_plan_pin_primary_save_hard_exit.script.py>"],
            str(_REPO_ROOT), utc_start, utc_end, proc1.returncode, stdout1, stderr1,
        )
        _write_export_json(szene, "t2_proc1_plan_pin_primary_save_hard_exit.script.py", script1)
        assert proc1.returncode == 94, (
            f"T2: Prozess 1 muss ueber os._exit(94) enden (NACH Plan-Pin/Primaersave, VOR Reflexion) -- "
            f"rc={proc1.returncode} stderr={stderr1!r}"
        )
        assert batch1 and "chrono-t2-guest" in "".join(batch1), batch1
        assert batch2 and any("SL-Antwort auf Anker" in l for l in batch2), batch2

        completion_section_id = "mesaT2-g2-placeholder"  # ueberschrieben unten
        plan_path = shared_run / "completion" / "local-guest1-section__plan.json"
        final_path = shared_run / "completion" / "local-guest1-section__final.json"
        guest_save_path = shared_run / "current_saves" / "guest1.json"
        assert plan_path.exists(), "T2: Prozess 1 haette den Plan real pinnen muessen (Phase 1)."
        assert guest_save_path.exists(), "T2: Prozess 1 haette den Primaersave real schreiben muessen."
        assert not final_path.exists(), "T2: Phase 2 (__final.json) darf von Prozess 1 NICHT erreicht worden sein."
        sha_guest_phase1 = _sha256(guest_save_path)
        decision = admission.read_table_decision(shared_run, "local-guest1")
        assert decision is not None and decision.get("decision") == "plan_committed", decision
        before_inventory = {
            "plan_exists": True, "final_exists": False, "guest_save_sha256": sha_guest_phase1,
            "decision": decision.get("decision"),
        }

        # ── Prozess 2 (frisch): ECHTER Resume-Versuch ueber den normalen
        # Produktweg ('tisch-start' erneut) -- deckt den gefundenen
        # Produktdefekt auf (s. Moduldocstring/Kommentar oben): der Leader
        # 'guest1' (table_admission-Gast, kein lokal registrierter Mensch)
        # wird in `_resume_bound_table` faelschlich als KI-Persona
        # eingestuft. NICHT selbst gefixt -- echter Fehlertext als Beleg.
        script2 = _fill_script(_T2_PROCESS2_RESUME_ATTEMPT_SCRIPT, **common)
        proc2 = _run_real_subprocess(
            szene, "t2_proc2_real_resume_attempt_hits_known_defect",
            [sys.executable, "-B", "-c", script2], cwd=str(_REPO_ROOT), env=clean_env,
        )
        _write_export_json(szene, "t2_proc2_real_resume_attempt_hits_known_defect.script.py", script2)
        assert proc2.returncode == 0, f"T2: Prozess 2 (Resume-Versuch) ist unerwartet abgestuerzt: {proc2.stderr}"
        payload2 = json.loads(proc2.stdout.strip().splitlines()[-1])
        resume_blocked_text = " ".join(payload2["printed"])
        assert "KI-Leader 'guest1' erfordert eine konfigurierte Persona-Anbindung" in resume_blocked_text, payload2
        assert not final_path.exists(), "T2: der blockierte Resume-Versuch darf NICHTS finalisiert haben."
        assert _sha256(guest_save_path) == sha_guest_phase1, "T2: der blockierte Resume-Versuch darf den Save NICHT veraendert haben."

        # ── G2-Standaloneszene (echter zweiter Tisch 'mesaT2-g2', EIN
        # durchgehender Prozess, KEIN Resume noetig): '/abbrechen' an der
        # freiwilligen Abschlussnotiz NACH Planannahme trifft auf einen
        # bereits 'plan_committed' gewonnenen Entscheid -- der G2-Fix darf
        # dafuer WEDER finalisieren NOCH 'verworfen' melden.
        common_g2 = dict(common)
        common_g2["table_key"] = "mesaT2-g2"
        script_g2 = _fill_script(_T2_PROCESS_G2_STANDALONE_SCRIPT, **common_g2)
        utc_start_g2 = _utc(time.time())
        proc_g2 = subprocess.Popen(
            [sys.executable, "-B", "-c", script_g2], cwd=str(_REPO_ROOT), env=clean_env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        deadline = time.time() + 20
        while time.time() < deadline and not (in_fifo.exists() and out_fifo.exists()):
            time.sleep(0.02)
        out_fd_g2 = os.open(str(out_fifo), os.O_RDONLY)
        out_f_g2 = os.fdopen(out_fd_g2, "r")
        in_fd_g2 = os.open(str(in_fifo), os.O_WRONLY)
        in_f_g2 = os.fdopen(in_fd_g2, "w")
        batch_a = _drain_lines(out_f_g2)
        in_f_g2.write("Ich erkunde die Gegend.\n")
        in_f_g2.flush()
        batch_b = _drain_lines(out_f_g2)
        in_f_g2.write("Ich gehe weiter.\n")
        in_f_g2.flush()
        batch_c = _drain_lines(out_f_g2)  # Reflexions-Zweckzeile
        in_f_g2.write("/abbrechen\n")
        in_f_g2.flush()
        batch_d = _drain_lines(out_f_g2)  # G2-Meldung (plan_committed-Zweig)
        stdout_g2, stderr_g2 = proc_g2.communicate(timeout=30)
        in_f_g2.close()
        out_f_g2.close()
        utc_end_g2 = _utc(time.time())
        _record_background_run(
            szene, "t2_procG2_abbrechen_at_plan_committed",
            [sys.executable, "-B", "-c", "<siehe t2_procG2_abbrechen_at_plan_committed.script.py>"],
            str(_REPO_ROOT), utc_start_g2, utc_end_g2, proc_g2.returncode, stdout_g2, stderr_g2,
        )
        _write_export_json(szene, "t2_procG2_abbrechen_at_plan_committed.script.py", script_g2)
        assert proc_g2.returncode == 0, f"T2: G2-Standaloneszene ist unerwartet gescheitert: {stderr_g2}"
        payload_g2 = json.loads(stdout_g2.strip().splitlines()[-1])
        assert payload_g2["gm_calls"] == 2, payload_g2
        joined_d = "".join(batch_d)
        assert "Spielstand uebernommen" in joined_d and "KEIN Verwurf" in joined_d, batch_d
        g2_final_path = shared_run / "completion" / "local-guest2-section__final.json"
        assert not g2_final_path.exists(), (
            "T2 (G2): '/abbrechen' am plan_committed-Zweig haette NICHT vorzeitig finalisieren duerfen."
        )
        assert "Fortschritt bereits angenommen" in stdout_g2, stdout_g2

        # ── Echter neuer Prozess fuehrt den DURCH PROZESS 1 angenommenen
        # Vorgang ('mesaT2'/local-guest1) tatsaechlich zu Ende --
        # CORE-Layer (derselbe Mechanismus wie die bestehende R2-F5-Szene
        # O4), weil der TUI-Resume fuer diesen Leader-Typ den oben
        # dokumentierten Defekt hat.
        script_finish = _fill_script(
            _T2_PROCESS_CORE_REAL_FINISH_SCRIPT,
            repo_root=str(_REPO_ROOT), fixtures_dir=str(_HERE), run_dir=str(shared_run),
            states_dir=str(shared_states), schema_path=str(_SCHEMA_PATH),
            table_id="local-guest1", section_id="local-guest1-section", leader_key="guest1", today=_TODAY,
        )
        proc_finish = _run_real_subprocess(
            szene, "t2_proc3_core_layer_real_finish_after_defect_workaround",
            [sys.executable, "-B", "-c", script_finish], cwd=str(_REPO_ROOT), env=clean_env,
        )
        _write_export_json(szene, "t2_proc3_core_layer_real_finish_after_defect_workaround.script.py", script_finish)
        assert proc_finish.returncode == 0, f"T2: echter Finish-Prozess ist unerwartet gescheitert: {proc_finish.stderr}"
        payload_finish = json.loads(proc_finish.stdout.strip().splitlines()[-1])
        assert payload_finish["success"] is True, payload_finish
        assert payload_finish["gm_calls"] == 0, "T2: Resume darf KEINEN neuen GM-Turn ausloesen -- " + repr(payload_finish)
        assert payload_finish["leader_reflection_calls"] == 1, payload_finish
        assert final_path.exists(), "T2: der echte Finish-Prozess haette __final.json real schreiben muessen."
        sha_final_1 = _sha256(final_path)
        sha_guest_after_finish = _sha256(guest_save_path)
        assert sha_guest_after_finish == sha_guest_phase1, "T2: der echte Reflexionsabschluss darf den bereits geernteten Save NICHT veraendern (Doppel-Harvest)."

        # ── Idempotenter Retry (echter neuer Prozess, direkte
        # store.complete_section/finalize_section_after_reflection-Aufrufe,
        # analog R2-F5 O4 Prozess 3).
        script_retry = _fill_script(
            _T2_PROCESS_IDEMPOTENT_RETRY_SCRIPT,
            repo_root=str(_REPO_ROOT), fixtures_dir=str(_HERE), run_dir=str(shared_run),
            states_dir=str(shared_states), schema_path=str(_SCHEMA_PATH),
            table_id="local-guest1", section_id="local-guest1-section", today=_TODAY,
        )
        proc_retry = _run_real_subprocess(
            szene, "t2_proc4_idempotent_retry_no_double_effect",
            [sys.executable, "-B", "-c", script_retry], cwd=str(_REPO_ROOT), env=clean_env,
        )
        assert proc_retry.returncode == 0, f"T2: idempotenter Retry-Prozess ist unerwartet gescheitert: {proc_retry.stderr}"
        payload_retry = json.loads(proc_retry.stdout.strip().splitlines()[-1])
        assert payload_retry["complete_section_already_completed"] is True and payload_retry["complete_section_written"] is False
        assert payload_retry["finalize_already_completed"] is True and payload_retry["finalize_written"] is False
        assert _sha256(final_path) == sha_final_1, "T2: idempotenter Retry hat __final.json erneut geschrieben."
        assert _sha256(guest_save_path) == sha_guest_after_finish, "T2: idempotenter Retry hat den Gast-Save veraendert."

        # ── Export VOR Tempverzeichnis-Bereinigung.
        _export_tree(szene, shared_run, "run")
        _export_tree(szene, shared_states, "states")
        _export_tree(szene, guest_onboarding, "guest_onboarding")
        _export_tree(szene, guest_catalog, "guest_catalog")
        _export_tree(szene, op_onboarding, "op_onboarding")
        _export_tree(szene, op_catalog, "op_catalog")
        after_inventory = {
            "plan_exists": plan_path.exists(), "final_exists": final_path.exists(),
            "final_sha256": sha_final_1, "guest_save_sha256": sha_guest_after_finish,
        }
        _write_export_json(szene, "inventory.json", {
            "before": before_inventory, "after": after_inventory,
            "found_product_defect": {
                "where": "mmo_sim/ui/tui.py:TuiSession._resume_bound_table (->_is_persona_member)",
                "what": (
                    "Ein echter Prozessneustart, der einen table_admission-/register_guest_terminal-"
                    "admittierten Gast-Leader (echter Mensch, KEINE KI-Persona, KEIN lokal via "
                    "ParticipantRegistry registrierter Mensch) fortsetzen will, wird faelschlich als "
                    "'KI-Leader ... erfordert persona_driver_factory' abgelehnt -- echter Fehlertext "
                    "in t2_proc2_real_resume_attempt_hits_known_defect.stdout.txt."
                ),
                "not_fixed": "Produktcode wurde NICHT geaendert (hartes Verbot) -- s. Report fuer Details.",
            },
            "notes": [
                "Prozess 1 endet real ueber os._exit(94) (Klassen-Monkeypatch auf "
                "SectionRuntime._collect_reflections, dieselbe Technik wie R2-F5 O4) -- NACH Plan-Pin/"
                "Primaersave, VOR jeder Reflexion/Finalisierung.",
                "Prozess 2 versucht den NORMALEN Produktweg (erneutes 'tisch-start') und deckt dabei "
                "den oben dokumentierten Defekt auf -- 0 Writes, kein Finalrecord, Save unveraendert.",
                "Die G2-Standaloneszene (eigener Tisch 'mesaT2-g2', eigener Gast 'guest2', EIN "
                "durchgehender Prozess) demonstriert den G2-Fix unabhaengig vom Resume-Defekt: "
                "'/abbrechen' an der freiwilligen Notiz NACH Planannahme loest WEDER Finalisierung "
                "NOCH 'verworfen' aus.",
                "Der echte Abschluss des durch Prozess 1 angenommenen Vorgangs ('mesaT2'/local-guest1) "
                "laeuft ueber denselben CORE-Layer-Mechanismus (SectionRuntime+ReflectionOnlyDriver) "
                "wie die bestehende R2-F5-Szene O4 -- bewusste Ausweichung um den dokumentierten "
                "TUI-Resume-Defekt, KEIN Produktfix.",
            ],
        })



# ───────────────────────── Familie T3 ─────────────────────────
# G3 (Erschaffung ueber Anbieter-Autoritaet), G5/O5/O6 (hostloser Gast;
# Freigabe, mehrschrittige Erschaffung, persoenliche Mitnahme).
#
# Abgrenzung zur bestehenden, UNVERAENDERTEN R2-F4-Szene
# (test_zr_betreiber_r2_f4_gast_erschaffung_produktweg_2026_11_04.py): die
# dort getestete Gastsession hat IMMER ihre EIGENE `gm_transport_factory`
# (Rueckwaertskompatibler Zweig von `_creation_authority`, s. dessen
# Docstring). Dieser Treiber deckt GENAU den NEUEN G3-Zweig: ein
# HOSTLOSER Gast (`host_capable=False`, `gm_transport_factory=None`,
# STRUKTURELL unerreichbar) wird ueber `register_guest_terminal` an einen
# ANBIETER angeschlossen -- Erschaffungsanfrage/-entscheid/-dialog laufen
# unter DESSEN `run_dir`/`gm_transport_factory` (`_creation_authority`),
# der Gast-Dialog-Scratch/Abschluss bleibt bei `self.onboarding_dir`
# (eigene private Wurzel).

_T3_FRESH_READER_SCRIPT = r"""
import json, sys
from pathlib import Path
sys.path.insert(0, @@repo_root@@)
sys.path.insert(0, @@fixtures_dir@@)

import mmo_sim.core.table_admission as table_admission
from mmo_sim.ui.tui import TuiSession

run_dir = Path(@@run_dir@@)
guest_onboarding = Path(@@guest_onboarding@@)
guest_catalog = Path(@@guest_catalog@@)


class _SpyFactory:
    def __call__(self, *a, **k):
        raise AssertionError("Spy-Factory aufgerufen -- der hostlose Gast darf STRUKTURELL keine "
                              "eigene Provider-/Modellanbindung besitzen.")


# Echter neuer Prozess, rein dateibasiert, KEINE Objektreferenz auf die
# alte guest_session -- NUR die private Gastwurzel + die geteilte
# Anbieter-run_dir (fuer eine echte Tischanfrage).
fresh = TuiSession(
    onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id="guest1",
    run_dir=run_dir, host_capable=False,
)
resolved = fresh._resolve_member("guest1")
assert resolved is not None, "T3: frischer Leser haette die eigene Figur finden muessen."
resolved_save, resolved_char = resolved

record_before = table_admission.load_record(run_dir, "mesaT3")
fresh._cmd_table_request_join(["mesaT3"])
record_after = table_admission.load_record(run_dir, "mesaT3")
request_join_ok = "guest1" in record_after.get("requests", []) and "guest1" not in (record_before or {}).get("requests", [])

print(json.dumps({
    "resolved_char_id": resolved_char, "resolved_save": resolved_save, "request_join_ok": request_join_ok,
}))
"""


class _ProviderCreationGm:
    """Anbieter-GM-Double (Fake NUR am GM-Transportrand, provider-seitig --
    G3 verlangt ausdruecklich, dass ein Gast-GM NICHT existiert, der
    Anbieter-GM aber Fragen stellt). Mehrschrittig: zwei echte Fragen,
    dann der fertige v7-Save."""

    def __init__(self, questions: list[str], final_block: dict):
        self._questions = list(questions)
        self._final_block = final_block
        self.calls = 0

    def turn(self, turn_idx: int, user_text: str, **kw) -> dict:
        self.calls += 1
        if self._questions:
            content = self._questions.pop(0)
        else:
            content = "```json\n" + json.dumps(self._final_block, ensure_ascii=False) + "\n```"
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": f"t3-{turn_idx}"}


def run_family_t3() -> None:
    szene = "t3"
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        shared_run = root / "run"
        shared_states = root / "states"
        shared_states.mkdir(parents=True)
        write_test_profile(shared_run, max_turns=200)

        guest_onboarding = root / "guest_onboarding"
        guest_catalog = root / "guest_catalog"
        provider_onboarding = root / "provider_onboarding"
        provider_catalog = root / "provider_catalog"

        char_id = "CHR-T3-GAST"
        final_block = full_v7_save(char_id, name="GastT3", save_id="fixture-t3-guest-001")
        gm = _ProviderCreationGm(
            ["Wie nennt sich dein Chrononaut?", "Was ist ihr prägender Ursprung?"], final_block,
        )
        provider_gm_calls_answers: list[str] = []

        def _provider_gm_factory():
            return gm

        provider_session = TuiSession(
            onboarding_dir=provider_onboarding, catalog_dir=provider_catalog, participant_id="operator1",
            run_dir=shared_run, states_dir=shared_states, schema_path=_SCHEMA_PATH,
            gm_transport_factory=_provider_gm_factory, host_capable=True,
        )
        guest_answers = ["Elena", "Eine verlorene Chronoflotte."]
        guest_printed: list[str] = []

        def _guest_input(prompt: str = "") -> str:
            provider_gm_calls_answers.append(prompt)
            return guest_answers.pop(0)

        # Hostloser Gast: host_capable=False, gm_transport_factory NICHT
        # gesetzt (strukturell unerreichbar, s. T3-Assert unten) -- geteilte
        # Anbieter-run_dir/states_dir/schema_path (fuer die echte spaetere
        # Veroeffentlichung), eigene private onboarding_dir/catalog_dir.
        guest_session = TuiSession(
            onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id="guest1",
            input_fn=_guest_input, print_fn=guest_printed.append,
            run_dir=shared_run, states_dir=shared_states, schema_path=_SCHEMA_PATH,
            host_capable=False,
        )
        assert guest_session.gm_transport_factory is None, (
            "T3: der hostlose Gast darf STRUKTURELL keine eigene gm_transport_factory besitzen."
        )
        assert guest_session.persona_driver_factory is None

        # §3 Negativfall (a): fehlende Freigabe -- 0 GM-Aufrufe, 0 Writes.
        guest_session._cmd_gast_erschaffung_dialog(["operator1"])
        assert any("kein gueltiger Betreiber-Grant" in p for p in guest_printed), guest_printed
        assert gm.calls == 0, "T3: vor jeder Freigabe darf der Anbieter-GM NICHT erreicht werden."
        guest_printed.clear()

        # G3: register_guest_terminal verdrahtet BEIDE Richtungen (Tisch-
        # UND Erschaffungs-Autoritaet) -- derselbe Aufruf wie F1.
        provider_session.register_guest_terminal("guest1", guest_session)

        # §3 Negativfall (b): fremder Betreiber kann eine fremde Anfrage
        # nicht entscheiden -- 0 Writes, kein Grant.
        guest_session._cmd_gast_erschaffung_anfragen(["operator1"])
        try:
            creation_grants.decide_creation_request(
                shared_run, operator_id="mallory", guest_id="guest1", approve=True,
            )
            raise AssertionError("T3: decide_creation_request haette bei fremdem Betreiber ablehnen muessen.")
        except creation_grants.CreationGrantError:
            pass
        record_after_foreign = creation_grants.grant_status(shared_run, "guest1")
        assert record_after_foreign["status"] == "requested", record_after_foreign

        # G3/F4 §1: ECHTE Betreiberentscheidung -- bindet Gast + Generation 1.
        provider_session._cmd_gast_erschaffung_annehmen(["guest1"])
        record = creation_grants.grant_status(shared_run, "guest1")
        assert record["status"] == "approved" and record["generation"] == 1, record

        # G3/O5: mehrschrittiger echter Dialog -- Anbieter-GM stellt ZWEI
        # echte Fragen, der Gast antwortet UEBER SEIN EIGENES Terminal
        # (eigener input_fn), ERST danach wird die fertige Fassung
        # angenommen.
        guest_session._cmd_gast_erschaffung_dialog(["operator1"])
        assert gm.calls == 3, f"T3: zwei Fragen + ein finaler Save erwartet, calls={gm.calls}"
        assert len(provider_gm_calls_answers) == 2, provider_gm_calls_answers

        onboarding_key = creation_grants.guest_onboarding_key("guest1", 1)
        state = onboarding.peek(guest_onboarding, onboarding_key)
        assert state is not None and state.status == "completed", state
        assert state.final_save == final_block, "persoenlicher Save muss real ueber complete_with_save gelandet sein."

        # G3/O5: persoenlicher Gastsave + Registrierung + aktive Fassung +
        # Current -- unter den Gast-EIGENEN Katalog-/Onboarding-Wurzeln,
        # aber der GETEILTEN Anbieter-run_dir/states_dir.
        entries = catalog.list_for_participant(guest_catalog, "guest1")
        assert any(e.chrononaut_id == char_id for e in entries), entries
        assert catalog.load_figure_save(guest_catalog, "guest1", char_id) == final_block
        current_save_path = shared_run / "current_saves" / "guest1.json"
        assert current_save_path.exists(), "T3: Current-Save haette real veroeffentlicht werden muessen."
        ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
        published = store.load_current_save_or_raise(shared_run, "guest1", ps_store, states_dir=shared_states)
        assert published == final_block, published

        # Aufrufspur: Anbieterausfuehrung (gm.calls>0) + fehlende
        # Gastprovider-Nutzung (guest_session.gm_transport_factory IST und
        # BLEIBT None -- strukturell unerreichbar, nicht nur ungenutzt).
        assert gm.calls == 3
        assert guest_session.gm_transport_factory is None

        # Fortsetzbarkeit: Betreiber bietet einen Tisch an, damit der
        # FRISCHE Prozess unten eine echte Tischanfrage erreichen kann.
        provider_session._cmd_table_offer(["mesaT3"])

        # Export VOR der Subprozess-Lektuere (Bytes vorher sichern).
        sha_guest_current_before = _sha256(current_save_path)
        sha_guest_figure_before = _sha256(guest_catalog / "figures" / f"guest1__{char_id}.json")

        fresh_script = _fill_script(
            _T3_FRESH_READER_SCRIPT, repo_root=str(_REPO_ROOT), fixtures_dir=str(_HERE),
            run_dir=str(shared_run), guest_onboarding=str(guest_onboarding), guest_catalog=str(guest_catalog),
        )
        fresh = _run_real_subprocess(
            szene, "t3_fresh_process_resolve_member_and_table_request",
            [sys.executable, "-B", "-c", fresh_script], cwd=str(_REPO_ROOT), env=_clean_env(),
        )
        assert fresh.returncode == 0, f"T3: frischer Leseprozess ist unerwartet fehlgeschlagen: {fresh.stderr}"
        fresh_payload = json.loads(fresh.stdout.strip().splitlines()[-1])
        assert fresh_payload["resolved_char_id"] == char_id, fresh_payload
        assert fresh_payload["resolved_save"] == final_block, fresh_payload
        assert fresh_payload["request_join_ok"] is True, fresh_payload

        sha_guest_current_after = _sha256(current_save_path)
        sha_guest_figure_after = _sha256(guest_catalog / "figures" / f"guest1__{char_id}.json")
        assert sha_guest_current_after == sha_guest_current_before, "T3: Current-Save wurde durch Lektuere veraendert."
        assert sha_guest_figure_after == sha_guest_figure_before, "T3: private Gastfigur wurde durch Lektuere veraendert."

        # Export VOR Tempverzeichnis-Bereinigung.
        _export_tree(szene, shared_run, "run")
        _export_tree(szene, shared_states, "states")
        _export_tree(szene, guest_onboarding, "guest_onboarding")
        _export_tree(szene, guest_catalog, "guest_catalog")
        _export_tree(szene, provider_onboarding, "provider_onboarding")
        _export_tree(szene, provider_catalog, "provider_catalog")
        _write_export_json(szene, "inventory.json", {
            "before": {"guest_current_sha256": None, "guest_figure_sha256": None, "grant_status": None},
            "after": {
                "guest_current_sha256": sha_guest_current_after, "guest_figure_sha256": sha_guest_figure_after,
                "grant_status": creation_grants.grant_status(shared_run, "guest1"),
            },
            "notes": [
                "Vor der Freigabe/Anfrage existierte weder ein Grant-Record noch ein persoenlicher "
                "Gastsave (echtes Vorher = vollstaendig fehlend) -- bewusst kein Fake-Leer-Record.",
                "guest_session.gm_transport_factory/persona_driver_factory bleiben UEBER DEN GESAMTEN "
                "Lauf None (strukturell, nicht nur ungenutzt) -- die einzige SL-Anbindung ist die "
                "ANBIETER-Autoritaet (_creation_authority/register_guest_terminal, G3).",
            ],
        })



# ───────────────────────── Familie T4 ─────────────────────────
# G4 (B3a/B3b), G5/O2/O5/O6 -- dieselbe freigegebene Gast-Erschaffung VOR
# UND NACH Annahme stoppen (Anschluss aus T3: derselbe register_guest_
# terminal/_creation_authority-Mechanismus).

_T4A_FRESH_RETRY_AFTER_ABANDON_SCRIPT = r"""
import json, sys
from pathlib import Path
sys.path.insert(0, @@repo_root@@)
sys.path.insert(0, @@fixtures_dir@@)

from mmo_sim.domain.zeitriss import catalog
from mmo_sim.ui.tui import TuiSession

run_dir = Path(@@run_dir@@)
states_dir = Path(@@states_dir@@)
schema_path = Path(@@schema_path@@)
guest_onboarding = Path(@@guest_onboarding@@)
guest_catalog = Path(@@guest_catalog@@)


class _SpyGm:
    def turn(self, *a, **kw):
        raise AssertionError("T4A: kein GM-Aufruf erwartet -- der Grant ist bereits veraltet (abgebrochen).")


printed = []
# Echter neuer Prozess, KEINE Objektreferenz auf die alte Session --
# dieselbe private Gastwurzel, dieselbe geteilte run_dir.
fresh_guest = TuiSession(
    onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id="guest1",
    print_fn=printed.append,
    run_dir=run_dir, states_dir=states_dir, schema_path=schema_path, host_capable=False,
)
fresh_guest._cmd_gast_erschaffung_dialog(["operator1"])
print(json.dumps({
    "printed": printed,
    "catalog_entries": len(catalog.list_for_participant(guest_catalog, "guest1")),
    "current_save_exists": (run_dir / "current_saves" / "guest1.json").exists(),
}))
"""

_T4B_PROCESS1_DIALOG_HARDEXIT_BEFORE_FINISH_SCRIPT = r"""
import os, sys, json
from pathlib import Path
sys.path.insert(0, @@repo_root@@)
sys.path.insert(0, @@fixtures_dir@@)

from mmo_sim.ui.tui import TuiSession

run_dir = Path(@@run_dir@@)
states_dir = Path(@@states_dir@@)
schema_path = Path(@@schema_path@@)
guest_onboarding = Path(@@guest_onboarding@@)
guest_catalog = Path(@@guest_catalog@@)
op_onboarding = Path(@@op_onboarding@@)
op_catalog = Path(@@op_catalog@@)
final_block = @@final_block@@


class _ProviderCreationGm:
    def __init__(self, questions, final_block):
        self._questions = list(questions)
        self._final_block = final_block
        self.calls = 0

    def turn(self, turn_idx, user_text, **kw):
        self.calls += 1
        if self._questions:
            content = self._questions.pop(0)
        else:
            content = "```json\n" + json.dumps(self._final_block, ensure_ascii=False) + "\n```"
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": f"t4b-{turn_idx}"}


def _hard_exit_between_publication_steps(*_a, **_kw):
    # Simulierter Prozessabbruch GENAU ZWISCHEN den beiden Schritten
    # (onboarding.complete_with_save ist bereits real erfolgt --
    # run_admitted_creation_dialog hat intern bereits "completed"
    # geliefert -- NUR die Publikation (catalog/current) fehlt noch).
    # Instanz-Monkeypatch GENAU an dieser Abbruch-Grenze, kein
    # veraenderter Produktpfad (dieselbe Technik wie die Klassen-Monkey-
    # patches in T2/R2-F5 O4, hier auf Instanzebene, weil
    # `_finish_granted_guest_creation` eine gebundene TuiSession-Methode
    # ist).
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(94)


gm = _ProviderCreationGm(["Wie nennt sich dein Chrononaut?", "Was ist ihr Ursprung?"], final_block)
answers = ["Mira", "Ein Forscherteam."]


def _guest_input(prompt=""):
    return answers.pop(0)


guest_session = TuiSession(
    onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id="guest2",
    input_fn=_guest_input, print_fn=lambda *a, **k: None,
    run_dir=run_dir, states_dir=states_dir, schema_path=schema_path, host_capable=False,
)
provider_session = TuiSession(
    onboarding_dir=op_onboarding, catalog_dir=op_catalog, participant_id="operator2",
    run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
    gm_transport_factory=lambda: gm, host_capable=True,
)
provider_session.register_guest_terminal("guest2", guest_session)
guest_session._finish_granted_guest_creation = _hard_exit_between_publication_steps

guest_session._cmd_gast_erschaffung_dialog(["operator2"])
print(json.dumps({"unexpected_normal_return": True, "gm_calls": gm.calls}))
"""

_T4B_PROCESS2_ABBRECHEN_THEN_REAL_FINISH_SCRIPT = r"""
import json, sys
from pathlib import Path
sys.path.insert(0, @@repo_root@@)
sys.path.insert(0, @@fixtures_dir@@)

from mmo_sim.domain.zeitriss import catalog
from mmo_sim.ui.tui import TuiSession

run_dir = Path(@@run_dir@@)
states_dir = Path(@@states_dir@@)
schema_path = Path(@@schema_path@@)
guest_onboarding = Path(@@guest_onboarding@@)
guest_catalog = Path(@@guest_catalog@@)


class _ExplodingGm:
    def __init__(self):
        self.calls = 0

    def turn(self, *a, **kw):
        self.calls += 1
        raise AssertionError("T4B: kein GM-Turn erwartet -- idempotente Fertigstellung braucht keinen neuen Dialog.")


gm = _ExplodingGm()
printed_abbrechen = []
fresh1 = TuiSession(
    onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id="guest2",
    print_fn=printed_abbrechen.append,
    run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
    gm_transport_factory=lambda: gm, host_capable=False,
)
# G4/B3b-Fix: der bisher FALSCHE Menueabbruch darf eine bereits
# ANGENOMMENE (status=='completed') Figur NICHT mehr verwerfen.
fresh1._cmd_gast_erschaffung_abbrechen(["operator2"])

printed_finish = []
fresh2 = TuiSession(
    onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id="guest2",
    print_fn=printed_finish.append,
    run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
    gm_transport_factory=lambda: gm, host_capable=False,
)
# Idempotente Fertigstellung (state.status=='completed' -> _finish_granted_
# guest_creation OHNE neuen GM-Aufruf) -- die Figur bleibt fertigstellbar.
fresh2._cmd_gast_erschaffung_dialog(["operator2"])

print(json.dumps({
    "printed_abbrechen": printed_abbrechen, "printed_finish": printed_finish, "gm_calls": gm.calls,
    "catalog_entries": len(catalog.list_for_participant(guest_catalog, "guest2")),
}))
"""

_T4B_PROCESS3_IDEMPOTENT_RETRY_SCRIPT = r"""
import json, sys
from pathlib import Path
sys.path.insert(0, @@repo_root@@)
sys.path.insert(0, @@fixtures_dir@@)

from mmo_sim.domain.zeitriss import catalog
from mmo_sim.ui.tui import TuiSession

run_dir = Path(@@run_dir@@)
states_dir = Path(@@states_dir@@)
schema_path = Path(@@schema_path@@)
guest_onboarding = Path(@@guest_onboarding@@)
guest_catalog = Path(@@guest_catalog@@)


class _ExplodingGm:
    def turn(self, *a, **kw):
        raise AssertionError("T4B: dritter Retry darf KEINEN neuen GM-Turn ausloesen.")


printed = []
fresh3 = TuiSession(
    onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id="guest2",
    print_fn=printed.append,
    run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
    gm_transport_factory=lambda: _ExplodingGm(), host_capable=False,
)
fresh3._cmd_gast_erschaffung_dialog(["operator2"])
print(json.dumps({
    "printed": printed, "catalog_entries": len(catalog.list_for_participant(guest_catalog, "guest2")),
}))
"""


def run_family_t4() -> None:
    szene = "t4"
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        shared_run = root / "run"
        shared_states = root / "states"
        shared_states.mkdir(parents=True)
        write_test_profile(shared_run, max_turns=200)
        clean_env = _clean_env()

        # ========== T4-A: Stop VOR Annahme (terminaler Entwurf) ==========
        provider_onboarding_a = root / "providerA_onboarding"
        provider_catalog_a = root / "providerA_catalog"
        guestA_onboarding = root / "guestA_onboarding"
        guestA_catalog = root / "guestA_catalog"
        char_id_a = "CHR-T4A-GAST"
        final_block_a = full_v7_save(char_id_a, name="GastT4A", save_id="fixture-t4a-guest-001")
        gm_a = _ProviderCreationGm(
            ["Wie nennt sich dein Chrononaut?", "Was ist ihr prägender Ursprung?"], final_block_a,
        )
        providerA_session = TuiSession(
            onboarding_dir=provider_onboarding_a, catalog_dir=provider_catalog_a, participant_id="operator1",
            run_dir=shared_run, states_dir=shared_states, schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: gm_a, host_capable=True,
        )
        guestA_printed: list[str] = []
        guestA_pending_inputs = ["Elena"]

        def _guestA_input(prompt: str = "") -> str:
            if guestA_pending_inputs:
                return guestA_pending_inputs.pop(0)
            return "/pause"

        guestA_session = TuiSession(
            onboarding_dir=guestA_onboarding, catalog_dir=guestA_catalog, participant_id="guest1",
            input_fn=_guestA_input, print_fn=guestA_printed.append,
            run_dir=shared_run, states_dir=shared_states, schema_path=_SCHEMA_PATH, host_capable=False,
        )
        providerA_session.register_guest_terminal("guest1", guestA_session)

        guestA_session._cmd_gast_erschaffung_anfragen(["operator1"])
        providerA_session._cmd_gast_erschaffung_annehmen(["guest1"])
        onboarding_key_a = creation_grants.guest_onboarding_key("guest1", 1)

        # Mehrschrittiger Dialog, ABER vor der fertigen Figur pausiert (nach
        # Q1/A1, bei Q2 beantwortet der Gast mit '/pause' -- derselbe
        # dokumentierte lokale Verwurf des offenen Schritts, KEIN Save).
        guestA_session._cmd_gast_erschaffung_dialog(["operator1"])
        assert gm_a.calls == 2, f"T4A: zwei Fragen vor der Pause erwartet, calls={gm_a.calls}"
        state_a1 = onboarding.peek(guestA_onboarding, onboarding_key_a)
        assert state_a1 is not None and state_a1.status == "in_progress", state_a1
        assert state_a1.final_save is None, "T4A: terminaler Entwurf OHNE fertige Figur erwartet."
        assert len(state_a1.steps) == 1, state_a1.steps

        # Durabler Abbruch VOR jeder Annahme/Fertigstellung.
        guestA_session._cmd_gast_erschaffung_abbrechen(["operator1"])
        state_a2 = onboarding.peek(guestA_onboarding, onboarding_key_a)
        assert state_a2.status == "abandoned", state_a2

        # Echte spaete Antwort/Korrekturwiederaufnahme am Produktweg darf
        # NICHT publizieren (derselbe Dialogbefehl, bewusst erneut
        # aufgerufen -- EIN direkter Abschlusshelfer nach abandon allein
        # waere KEIN Nachweis, s. Briefing).
        guestA_printed.clear()
        guestA_session._cmd_gast_erschaffung_dialog(["operator1"])
        assert any("kein gueltiger Betreiber-Grant" in p for p in guestA_printed), guestA_printed
        assert gm_a.calls == 2, "T4A: nach dem Abbruch darf KEIN weiterer GM-Turn stattfinden."

        # Frischer Prozess respektiert denselben Abbruch.
        script_a_fresh = _fill_script(
            _T4A_FRESH_RETRY_AFTER_ABANDON_SCRIPT,
            repo_root=str(_REPO_ROOT), fixtures_dir=str(_HERE), run_dir=str(shared_run),
            states_dir=str(shared_states), schema_path=str(_SCHEMA_PATH),
            guest_onboarding=str(guestA_onboarding), guest_catalog=str(guestA_catalog),
        )
        proc_a_fresh = _run_real_subprocess(
            szene, "t4a_fresh_process_retry_respects_abandon",
            [sys.executable, "-B", "-c", script_a_fresh], cwd=str(_REPO_ROOT), env=clean_env,
        )
        assert proc_a_fresh.returncode == 0, f"T4A: frischer Retry-Prozess ist unerwartet gescheitert: {proc_a_fresh.stderr}"
        payload_a_fresh = json.loads(proc_a_fresh.stdout.strip().splitlines()[-1])
        assert any("kein gueltiger Betreiber-Grant" in p for p in payload_a_fresh["printed"]), payload_a_fresh
        assert payload_a_fresh["catalog_entries"] == 0, payload_a_fresh
        assert payload_a_fresh["current_save_exists"] is False, payload_a_fresh

        # ========== T4-B: Stop NACH Annahme (G4/B3b) ==========
        provider_onboarding_b = root / "providerB_onboarding"
        provider_catalog_b = root / "providerB_catalog"
        guestB_onboarding = root / "guestB_onboarding"
        guestB_catalog = root / "guestB_catalog"
        char_id_b = "CHR-T4B-GAST"
        final_block_b = full_v7_save(char_id_b, name="GastT4B", save_id="fixture-t4b-guest-001")

        providerB_setup = TuiSession(
            onboarding_dir=provider_onboarding_b, catalog_dir=provider_catalog_b, participant_id="operator2",
            run_dir=shared_run, states_dir=shared_states, schema_path=_SCHEMA_PATH, host_capable=True,
        )
        guestB_setup = TuiSession(
            onboarding_dir=guestB_onboarding, catalog_dir=guestB_catalog, participant_id="guest2",
            run_dir=shared_run, states_dir=shared_states, schema_path=_SCHEMA_PATH, host_capable=False,
        )
        guestB_setup._cmd_gast_erschaffung_anfragen(["operator2"])
        providerB_setup._cmd_gast_erschaffung_annehmen(["guest2"])
        grant_b_before = creation_grants.grant_status(shared_run, "guest2")
        assert grant_b_before["status"] == "approved" and grant_b_before["generation"] == 1, grant_b_before

        # Prozess 1: echter mehrschrittiger Dialog bis zur ECHTEN
        # Annahme/Fertigstellung des Save-Inhalts (onboarding.complete_
        # with_save real erfolgt), dann os._exit GENAU ZWISCHEN den beiden
        # Publikationsschritten (VOR catalog/current-Veroeffentlichung).
        script_b1 = _fill_script(
            _T4B_PROCESS1_DIALOG_HARDEXIT_BEFORE_FINISH_SCRIPT,
            repo_root=str(_REPO_ROOT), fixtures_dir=str(_HERE), run_dir=str(shared_run),
            states_dir=str(shared_states), schema_path=str(_SCHEMA_PATH),
            guest_onboarding=str(guestB_onboarding), guest_catalog=str(guestB_catalog),
            op_onboarding=str(provider_onboarding_b), op_catalog=str(provider_catalog_b),
            final_block=final_block_b,
        )
        proc_b1 = _run_real_subprocess(
            szene, "t4b_proc1_dialog_completed_hard_exit_before_finish",
            [sys.executable, "-B", "-c", script_b1], cwd=str(_REPO_ROOT), env=clean_env,
        )
        assert proc_b1.returncode == 94, (
            f"T4B: Prozess 1 muss ueber os._exit(94) enden (NACH onboarding.complete_with_save, VOR "
            f"_finish_granted_guest_creation) -- rc={proc_b1.returncode} stderr={proc_b1.stderr!r}"
        )
        onboarding_key_b = creation_grants.guest_onboarding_key("guest2", 1)
        state_b1 = onboarding.peek(guestB_onboarding, onboarding_key_b)
        assert state_b1 is not None and state_b1.status == "completed", state_b1
        assert state_b1.final_save == final_block_b, "T4B: der angenommene Save muss real uebernommen sein (Phase 1)."
        # Teilpublikation: NOCH keine Katalog-/Current-Veroeffentlichung.
        assert catalog.list_for_participant(guestB_catalog, "guest2") == [], "T4B: Phase 2 (Publikation) darf NICHT erreicht worden sein."
        assert not (shared_run / "current_saves" / "guest2.json").exists()
        before_inventory_b = {
            "onboarding_status": state_b1.status, "final_save_present": True,
            "catalog_entries": 0, "current_save_exists": False,
        }

        # Prozess 2 (frisch): G4/B3b -- 'gast-erschaffung-abbrechen' darf
        # die bereits angenommene Figur NICHT mehr verwerfen (idempotent
        # fertigstellen -- EIN direkter Abschlusshelfer nach abandon allein
        # waere KEIN Nachweis, deshalb hier der echte Menuebefehl ZUERST).
        script_b2 = _fill_script(
            _T4B_PROCESS2_ABBRECHEN_THEN_REAL_FINISH_SCRIPT,
            repo_root=str(_REPO_ROOT), fixtures_dir=str(_HERE), run_dir=str(shared_run),
            states_dir=str(shared_states), schema_path=str(_SCHEMA_PATH),
            guest_onboarding=str(guestB_onboarding), guest_catalog=str(guestB_catalog),
        )
        proc_b2 = _run_real_subprocess(
            szene, "t4b_proc2_abbrechen_denied_then_real_finish",
            [sys.executable, "-B", "-c", script_b2], cwd=str(_REPO_ROOT), env=clean_env,
        )
        assert proc_b2.returncode == 0, f"T4B: Prozess 2 ist unerwartet gescheitert: {proc_b2.stderr}"
        payload_b2 = json.loads(proc_b2.stdout.strip().splitlines()[-1])
        assert any("nicht abbrechbar" in p and "bereits angenommen" in p for p in payload_b2["printed_abbrechen"]), payload_b2
        state_b2 = onboarding.peek(guestB_onboarding, onboarding_key_b)
        assert state_b2.status == "completed", "T4B: G4/B3b -- der Abbruchversuch darf die Annahme NICHT verwerfen."
        assert payload_b2["gm_calls"] == 0, "T4B: idempotente Fertigstellung braucht keinen neuen GM-Turn."
        assert payload_b2["catalog_entries"] == 1, payload_b2
        guestB_current_path = shared_run / "current_saves" / "guest2.json"
        assert guestB_current_path.exists(), "T4B: der echte Finish-Prozess haette den Current real veroeffentlichen muessen."
        guestB_figure_path = guestB_catalog / "figures" / f"guest2__{char_id_b}.json"
        assert guestB_figure_path.exists()
        published_b = store.load_current_save_or_raise(
            shared_run, "guest2", PersonaStateStore(schema_path=_SCHEMA_PATH), states_dir=shared_states,
        )
        assert published_b == final_block_b, published_b
        sha_current_b1 = _sha256(guestB_current_path)
        sha_figure_b1 = _sha256(guestB_figure_path)

        # Prozess 3 (frisch): weiterer identischer Retry -- genau EINE
        # Figur, keine Doppelpublikation, byteidentisch.
        script_b3 = _fill_script(
            _T4B_PROCESS3_IDEMPOTENT_RETRY_SCRIPT,
            repo_root=str(_REPO_ROOT), fixtures_dir=str(_HERE), run_dir=str(shared_run),
            states_dir=str(shared_states), schema_path=str(_SCHEMA_PATH),
            guest_onboarding=str(guestB_onboarding), guest_catalog=str(guestB_catalog),
        )
        proc_b3 = _run_real_subprocess(
            szene, "t4b_proc3_identical_retry_no_double_publication",
            [sys.executable, "-B", "-c", script_b3], cwd=str(_REPO_ROOT), env=clean_env,
        )
        assert proc_b3.returncode == 0, f"T4B: Prozess 3 ist unerwartet gescheitert: {proc_b3.stderr}"
        payload_b3 = json.loads(proc_b3.stdout.strip().splitlines()[-1])
        assert payload_b3["catalog_entries"] == 1, "T4B: weiterhin GENAU EINE Figur, kein Ersatz-/Zweiteintrag."
        assert _sha256(guestB_current_path) == sha_current_b1, "T4B: dritter Retry hat den Current erneut geschrieben."
        assert _sha256(guestB_figure_path) == sha_figure_b1, "T4B: dritter Retry hat die Figur erneut geschrieben."

        # ── Export VOR Tempverzeichnis-Bereinigung.
        _export_tree(szene, shared_run, "run")
        _export_tree(szene, shared_states, "states")
        _export_tree(szene, guestA_onboarding, "guestA_onboarding")
        _export_tree(szene, guestA_catalog, "guestA_catalog")
        _export_tree(szene, guestB_onboarding, "guestB_onboarding")
        _export_tree(szene, guestB_catalog, "guestB_catalog")
        _export_tree(szene, provider_onboarding_a, "providerA_onboarding")
        _export_tree(szene, provider_onboarding_b, "providerB_onboarding")
        _write_export_json(szene, "inventory.json", {
            "t4a_before": {"onboarding_status": "in_progress", "final_save_present": False, "steps": 1},
            "t4a_after": {
                "onboarding_status": "abandoned",
                "catalog_entries": payload_a_fresh["catalog_entries"],
                "current_save_exists": payload_a_fresh["current_save_exists"],
            },
            "t4b_before": before_inventory_b,
            "t4b_after": {
                "onboarding_status": state_b2.status, "catalog_entries": payload_b3["catalog_entries"],
                "current_save_sha256": sha_current_b1, "figure_sha256": sha_figure_b1,
            },
            "notes": [
                "T4A: vor Annahme existierte weder Katalogeintrag noch Current-Save (echtes "
                "vollstaendiges Fehlen, kein Fake-Leer-Record) -- bleibt nach dem Abbruch UNVERAENDERT "
                "fehlend (geprueft im frischen Prozess).",
                "T4B Prozess 1 endet real ueber os._exit(94) (Instanz-Monkeypatch auf der gebundenen "
                "Methode `guest_session._finish_granted_guest_creation`, GENAU an der Abbruch-Grenze "
                "zwischen den beiden Publikationsschritten) -- kein veraenderter Produktpfad.",
                "G4/B3b real belegt: 'gast-erschaffung-abbrechen' auf einer bereits angenommenen "
                "(status=='completed') Figur verwirft NICHT mehr, sondern verweist auf die idempotente "
                "Fertigstellung -- die ZWEITE Dialoganfrage (SELBER frischer Prozess) vollzieht genau "
                "diese Fertigstellung real nach, mit 0 neuen GM-Turns.",
            ],
        })



def main() -> int:
    if _RESULTS_ROOT.exists():
        shutil.rmtree(_RESULTS_ROOT)
    _RESULTS_ROOT.mkdir(parents=True)

    scenes = [("t1", run_family_t1), ("t2", run_family_t2), ("t3", run_family_t3), ("t4", run_family_t4)]
    failed = 0
    for name, fn in scenes:
        try:
            fn()
            print(f"OK   familie_{name}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL familie_{name}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR familie_{name}:")
            traceback.print_exc()

    manifest_path = _RESULTS_ROOT / "MANIFEST.json"
    manifest_path.write_text(json.dumps(_MANIFEST, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{len(scenes) - failed}/{len(scenes)} Familien bestanden.")
    print(f"MANIFEST: {manifest_path} ({len(_MANIFEST['files'])} Dateien, {len(_MANIFEST['runs'])} Laeufe)")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
