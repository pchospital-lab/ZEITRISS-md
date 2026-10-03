#!/usr/bin/env python3
"""
tests/mmo_sim/_a13_report_support.py — gemeinsame Helper fuer
`test_a13_local_provenance_2026_09_30.py` (A13-Quellenbericht-Auftrag,
2026-09-30). Neues Testartefakt, keine Produktdatei.

`build_real_minimal_section_data_dir()` baut einen ECHTEN, minimalen
Zwei-Personen-Ein-Abschnitt-Datenordner NUR durch Aufrufe bereits
vorhandener, unveraenderter Produktfunktionen (`core.store.Table`/
`Lobby`/`complete_section`/`finalize_section_after_reflection`,
`core.request_ledger.begin`/`finish_received`, `core.persona_state.
PersonaStateStore`, `domain.zeitriss.saves.harvest_from_debrief`,
`domain.zeitriss.policy.ZeitrissHarvestValidator`/`COMPLETION_MARKER`,
`lab.runner.LabRunner`, sowie `bootstrap_six_persona_community`/
`make_ready` aus `_h02_vollreise_support.py`) -- KEINE zweite Spiel-/
Buchungslogik, nur Orchestrierung + literale Testtexte (wie jede
Fixture). `events.jsonl` bleibt bewusst ABWESEND (wie in den echten A23-
API-/Hybrid-Endablagen aus REPORT-FIXTURES.json) -- Quelle fuer den
Bericht ist `table.sl_log`.

Diese Datei erzeugt selbst NIE einen `report`-Prozess -- das macht
ausschliesslich der echte Produktweg (`scripts/mmo_sim.py report ...`
als Subprozess) im Testfile."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _h02_vollreise_support import bootstrap_six_persona_community, make_ready  # noqa: E402
from mmo_sim.core.store import (  # noqa: E402
    Lobby, Table, complete_section, finalize_section_after_reflection,
)
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.core.request_ledger import begin, finish_received  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER, ZeitrissTableSizePolicy, ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.domain.zeitriss.saves import harvest_from_debrief  # noqa: E402
from mmo_sim.lab.runner import LabBudget, LabRunner  # noqa: E402

TABLE_ID = "a13-lobby-sniper-tech"
SECTION_ID = "a13-lobby-sniper-tech-section"
MEMBERS = ("sniper", "tech")

# REPORTFIXTURE (handgeschrieben, keine gespielte Karriere): literale
# SL-Turntexte, analog wie jede bestehende Testdatei (z.B.
# `test_m4_lab_reports.py`) Eventtexte literal als Python-Strings haelt.
_TURN0_LEADER_MESSAGE = "Wir pruefen gemeinsam die Ausruestung im HQ, bevor wir starten."
_TURN0_GM_CONTENT = (
    "Ihr sichtet eure Waffen und die restliche Ausruestung -- alles einsatzbereit. "
    "[A13-REPORTFIXTURE-turn0]"
)
_TURN1_LEADER_MESSAGE = "Wir schliessen den Abschnitt kontrolliert ab."


def _debrief_text(sniper_cid: str, tech_cid: str) -> str:
    sniper_final = {
        "v": 7, "save_id": "a13-reportfixture-sniper-final-001",
        "_fixture_note": "SIMULIERT/FIXTURE (A13-Quellenbericht-Testsupport, KEINE gespielte Karriere)",
        "characters": [{"char_id": sniper_cid, "id": sniper_cid, "name": "Yael", "callsign": "SNIPER"}],
    }
    tech_final = {
        "v": 7, "save_id": "a13-reportfixture-tech-final-001",
        "_fixture_note": "SIMULIERT/FIXTURE (A13-Quellenbericht-Testsupport, KEINE gespielte Karriere)",
        "characters": [{"char_id": tech_cid, "id": tech_cid, "name": "Kaede", "callsign": "TECH"}],
    }
    return (
        f"```json\n{json.dumps(sniper_final, ensure_ascii=False)}\n```\n"
        f"```json\n{json.dumps(tech_final, ensure_ascii=False)}\n```\n"
        f"{COMPLETION_MARKER} table_id={TABLE_ID} section_id={SECTION_ID}"
    )


def build_real_minimal_section_data_dir(root: Path) -> dict:
    """Baut unter `root` (vom Aufrufer bereitgestelltes, LEERES exklusives
    Testverzeichnis) einen echten, vollstaendig abgeschlossenen
    Zwei-Personen-Ein-Abschnitt-Datenordner (`root/run`). Liefert ein
    dict mit `run_dir`/`table_id`/`section_id`/`members`/`chrononaut_ids`
    fuer den Aufrufer. Rein additive Testinfrastruktur, kein Produktcode."""
    schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = bootstrap_six_persona_community(
        root, "a13-community", persona_keys=MEMBERS,
    )
    sniper_cid = make_ready(onboarding_dir, states_dir, run_dir, "sniper")
    tech_cid = make_ready(onboarding_dir, states_dir, run_dir, "tech")
    chrononaut_ids = {"sniper": sniper_cid, "tech": tech_cid}

    lobby = Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    table = Table(
        table_id=TABLE_ID, leader="tech", members=list(MEMBERS),
        chrononaut_ids=chrononaut_ids, run_dir=run_dir,
    )
    debrief_text = _debrief_text(sniper_cid, tech_cid)
    table.sl_log.append({
        "turn_idx": 0, "leader_message": _TURN0_LEADER_MESSAGE, "origin_persona_key": "tech",
        "origin_source": "persona_api:synthetic", "save_payload": None, "content": _TURN0_GM_CONTENT,
    })
    table.sl_log.append({
        "turn_idx": 1, "leader_message": _TURN1_LEADER_MESSAGE, "origin_persona_key": "tech",
        "origin_source": "persona_api:synthetic", "save_payload": None, "content": debrief_text,
    })
    table.persist()

    cid_to_pk = {sniper_cid: "sniper", tech_cid: "tech"}
    harvested = harvest_from_debrief(debrief_text, cid_to_pk)
    ps_store = PersonaStateStore(schema_path=schema_path)
    result = complete_section(
        lobby, table, SECTION_ID, harvested, states_dir, "2026-09-30",
        ZeitrissHarvestValidator(), ps_store,
    )
    if not result.success:
        raise RuntimeError(f"A13-Testsupport: complete_section fehlgeschlagen: {result.reason}")

    reflections_path = run_dir / "reflections.jsonl"
    reflection_texts = {
        "sniper": "Ich bin zufrieden, dass die Ausruestungspruefung gruendlich war.",
        "tech": "Die Absprache am Tisch hat gut funktioniert.",
    }
    with reflections_path.open("a", encoding="utf-8") as fh:
        for pk in MEMBERS:
            entry = {
                "persona_key": pk, "section_id": SECTION_ID, "ts": "2026-09-30T00:00:00+00:00",
                "text": reflection_texts[pk], "origin_source": "persona_api:synthetic",
                "kind": "ai_reflection_received",
            }
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

    result2 = finalize_section_after_reflection(lobby, table, SECTION_ID)
    if not result2.success:
        raise RuntimeError(f"A13-Testsupport: finalize_section_after_reflection fehlgeschlagen: {result2.reason}")

    runner = LabRunner(run_dir, LabBudget(max_turns=10, max_seconds=1000, max_usd=10.0), pid=os.getpid())
    runner.start()
    try:
        rid0 = begin(
            run_dir, role="gm", content=_TURN0_LEADER_MESSAGE, reserved_usd=0.001,
            route="http://127.0.0.1:0", table_id=TABLE_ID, section_id=SECTION_ID,
            turn_idx=0, participant="tech", dollar_billed=True,
        )
        finish_received(run_dir, rid0, usage={"prompt_tokens": 12, "completion_tokens": 6}, seconds=0.01,
                         result_text=_TURN0_GM_CONTENT)
        rid1 = begin(
            run_dir, role="gm", content=_TURN1_LEADER_MESSAGE, reserved_usd=0.001,
            route="http://127.0.0.1:0", table_id=TABLE_ID, section_id=SECTION_ID,
            turn_idx=1, participant="tech", dollar_billed=True,
        )
        finish_received(run_dir, rid1, usage={"prompt_tokens": 30, "completion_tokens": 18}, seconds=0.02,
                         result_text=debrief_text)
    finally:
        runner.release()

    return {
        "run_dir": run_dir, "table_id": TABLE_ID, "section_id": SECTION_ID,
        "members": list(MEMBERS), "chrononaut_ids": chrononaut_ids,
    }

# Persistent, explicitly separated fixture-game and report-only evidence.
# No external package is needed by the ordinary run_all path.
def report_evidence_root() -> Path:
    import tempfile
    parent = os.environ.get("H02_EVIDENCE_DIR")
    if parent:
        base = Path(parent) / "a13-permanent"
        base.mkdir(parents=True, exist_ok=True)
        return base
    global _A13_STANDALONE_EVIDENCE
    if "_A13_STANDALONE_EVIDENCE" not in globals():
        _A13_STANDALONE_EVIDENCE = Path(tempfile.mkdtemp(prefix="a13-evidence-"))
    return _A13_STANDALONE_EVIDENCE


def _a13_capture_tree(source: Path, target: Path) -> dict:
    """Read plain files without traversing any link; preserve bytes before cleanup."""
    import hashlib
    target.mkdir(parents=True, exist_ok=False)
    result = {}
    if not source.is_dir() or source.is_symlink():
        return result
    for directory, dirs, files in os.walk(source, followlinks=False):
        base = Path(directory)
        dirs[:] = sorted(d for d in dirs if not (base/d).is_symlink())
        for name in sorted(files):
            path = base/name
            rel = path.relative_to(source).as_posix()
            if path.is_symlink():
                result[rel] = {"symlink": os.readlink(path)}
                continue
            data = path.read_bytes(); dst = target/rel; dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data); result[rel] = hashlib.sha256(data).hexdigest()
    (target/"A13-CAPTURE-HASHES.json").write_text(json.dumps(result, indent=2)+"\n")
    return result


def run_recorded_report(args: list[str], repo_root: Path, timeout: float = 60):
    """Real dispatcher under read-only constructor/network observations, no models.

    The test wrapper patches only forbidden constructors/transports and records their
    hits. It does not replace report.main or its return/exception behavior.
    """
    import datetime, hashlib, subprocess, tempfile, time
    case = Path(tempfile.mkdtemp(prefix="report-", dir=report_evidence_root()))
    log = case/"observer.json"; wrapper = case/"wrapper.py"
    wrapper.write_text('''import sys,pathlib,json,runpy,socket,os
sys.path.insert(0,%r)
from mmo_sim.ui.tui import TuiSession
from mmo_sim.lab.runner import LabRunner
from mmo_sim.core.events import EventLog
from mmo_sim.core import identity,request_ledger
from mmo_sim.adapters import factories
hits=[]
def deny(label):
 def call(*a,**kw):
  hits.append(label);raise RuntimeError('UNEXPECTED_REPORT_SIDE_EFFECT '+label)
 return call
for cls in (TuiSession,LabRunner,EventLog):cls.__init__=deny(cls.__name__)
identity.new_participant_id=deny('participant-allocation')
request_ledger._requests_dir=deny('request-directory-writer')
for name in ('default_gm_transport_factory','default_persona_driver_factory'):
 setattr(factories,name,deny(name))
socket.socket.connect=deny('socket.connect');socket.socket.connect_ex=deny('socket.connect_ex');socket.getaddrinfo=deny('socket.getaddrinfo')
try:
 sys.argv=sys.argv[1:];runpy.run_path(sys.argv[0],run_name='__main__')
finally:
 pathlib.Path(%r).write_text(json.dumps({'pid':os.getpid(),'forbidden_calls':hits})+'\\n')
''' % (str(repo_root), str(log)))
    def option(key):
        return Path(args[args.index(key)+1]) if key in args and args.index(key)+1 < len(args) else None
    source = option("--data-dir"); output = option("--output-dir")
    before = _a13_capture_tree(source, case/"source-before") if source else None
    argv = [sys.executable,"-B",str(wrapper),str(repo_root/"scripts/mmo_sim.py"),"report",*args]
    start = datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic()
    p = subprocess.Popen(argv,cwd=repo_root,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    timed_out=False
    try:stdout,stderr=p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out=True;p.kill();stdout,stderr=p.communicate()
    (case/"stdout.bin").write_bytes(stdout);(case/"stderr.bin").write_bytes(stderr)
    after = _a13_capture_tree(source,case/"source-after") if source else None
    if p.returncode == 0 and output and output.is_dir() and not output.is_symlink():
        _a13_capture_tree(output,case/"output")
    observer=json.loads(log.read_text()) if log.exists() else None
    meta={"argv":argv,"dispatcher_argv":[str(repo_root/"scripts/mmo_sim.py"),"report",*args],
          "cwd":str(repo_root),"pid":p.pid,"started_utc":start,"elapsed_seconds":time.monotonic()-t,
          "returncode":p.returncode,"timeout":timed_out,"source_unchanged":before==after,
          "stdout_sha256":hashlib.sha256(stdout).hexdigest(),"stderr_sha256":hashlib.sha256(stderr).hexdigest(),
          "observer":observer,"wrapper_sha256":hashlib.sha256(wrapper.read_bytes()).hexdigest(),
          "classification":"fresh report process; fixture-game work is separate"}
    (case/"execution.json").write_text(json.dumps(meta,indent=2)+"\n")
    assert not timed_out, "A13_REPORT_TIMEOUT"
    assert before==after, "A13_REPORT_CHANGED_INPUT"
    assert observer is not None and observer["pid"]==p.pid and not observer["forbidden_calls"], "A13_REPORT_SIDE_EFFECT"
    result=subprocess.CompletedProcess(argv,p.returncode,stdout.decode(),stderr.decode())
    result.a13_case=case
    return result


def generate_existing_a23_journey_inputs() -> list[dict]:
    """Invoke unchanged A23 V3/V4; they use real TUI/Lab/API/Fake-CLI pathways.

    Only synthetic loopback fixtures. These ARE fresh game-fixture calls, not
    zero-request reports. Restore evidence environment before report execution.
    """
    import tempfile
    import test_a23_bounded_vorlauf_2026_09_30 as a23
    destination=Path(tempfile.mkdtemp(prefix="fixture-games-",dir=report_evidence_root()))
    old=os.environ.get("H02_EVIDENCE_DIR")
    try:
        os.environ["H02_EVIDENCE_DIR"]=str(destination)
        a23.test_v3_api_profile_real_tui_to_lab_to_persona_journey()
        a23.test_v4_hybrid_profile_real_tui_to_lab_to_fake_cli_journey()
    finally:
        if old is None:os.environ.pop("H02_EVIDENCE_DIR",None)
        else:os.environ["H02_EVIDENCE_DIR"]=old
    result=[]
    for profile in ("api","hybrid"):
        case=destination/f"A23_{profile}_complete_journey"
        run_dir=case/"tui/after-ui/run"
        assert run_dir.is_dir(),f"Actual A23 snapshot not found: {run_dir}"
        result.append({"profile":profile,"run_dir":run_dir,"case":case,
                       "table_id":"lobby-sniper-tech","section_id":"lobby-sniper-tech-section"})
    return result
