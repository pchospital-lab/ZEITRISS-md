#!/usr/bin/env python3
"""
tests/mmo_sim/drive_r2_f5_evidence_2026_11_04.py -- ZR-BETREIBER-
GASTERSCHAFFUNG-20261103-R2, F5 (GENERAL-REVIEW.md §F5 /
02_NACHWEISE_UND_RUECKGABE.md §1/§2): echte Frischprozess-Belege + exportierte
Ergebnisbytes fuer O3/O4, die R1 fehlten (dort: eine Fake-Startdatei
`{"startfassung":true,"pk":"guest_pk"}` + eine Same-Interpreter-`Table.load`
als "frischer Prozess" bei O3; zwei `complete_section`-Aufrufe im selben
Prozess bei O4, `__final.json` wurde NIE erreicht).

Szene O3 (echte Startfassung + echter neuer OS-Prozess, kein Plan):
  Der Parent-Prozess baut einen echten Zweier-Tisch (`build_two_member_table`)
  und veroeffentlicht die Gast-Startfassung ECHT ueber
  `store.publish_current_save` (ein realer `full_v7_save`-Block, KEIN
  Fake-Dict). Ein Betreiber-Stop wird VOR jedem Abschlussversuch gebunden+
  gesetzt (`table_admission.offer_table`/`bind_section`/`request_table_stop`
  -- derselbe atomare Entscheid-Slot wie F2). Danach laedt ein ECHTER NEUER
  OS-Prozess (`subprocess.run([sys.executable, "-c", ...])`, eigene
  argv/exit/stdout/stderr) den Tisch frisch von der Platte und ruft
  `store.complete_section` auf: der Betreiber-Stop gewinnt den Entscheid,
  `complete_section` bricht ab (KEIN `__plan.json`), die Gast-Startfassung
  bleibt sha256-byteidentisch vor/nach dem Versuch.

Szene O4 (Plan-Pin+Primaersave in Prozess 1, Finalabschluss NUR ueber den
echten Produktweg in Prozess 2, idempotenter Retry in Prozess 3):
  Drei echte, unabhaengige OS-Prozesse (`subprocess.run`), jeder baut seine
  Python-Objektsicht NUR aus der Platte neu (kein geteilter
  Interpreterzustand):
    Prozess 1 spielt einen echten Abschnitt (Leader-Anker, Gast-Import,
    Debrief mit Marker) ueber `core.runtime.SectionRuntime.run_full_section`
    (`ScriptedDriver`/`ScriptedGmTransport`) bis `store.complete_section`
    PHASE 1 real erfolgreich ist (Plan gepinnt, Primaersaves fuer
    leader_pk/guest_pk geschrieben) -- und endet DANACH hart (`os._exit`),
    indem NUR `SectionRuntime._collect_reflections` (die Pflicht-KI-
    Reflexion, Vorbedingung von `finalize_section_after_reflection`) auf der
    Instanz durch einen Hard-Exit ersetzt wird (dieselbe Technik wie die
    bestehenden `StopAfterResponseGmTransport`/`_hard_kill_after_durable_
    persist`-Fixtures: ein Monkeypatch GENAU an der Prozessabbruch-Grenze,
    kein veraenderter Produktpfad). Kein Rollback, kein Lock-Release, kein
    `__final.json`.
    Prozess 2 ist ein KOMPLETT FRISCHER Prozess: baut Lobby/Table NUR aus der
    Platte, ruft erneut `run_full_section` mit einem UNVERAENDERTEN
    `SectionRuntime` (kein Monkeypatch mehr) -- die bestehende Produktlogik
    (`run_full_section`s `open_completion_order_for_table`-Check, A1/D5)
    erkennt den offenen Plan-Auftrag selbst und nimmt den Resume-Zweig:
    `complete_section` (idempotenter Resume, kein neuer Harvest) ->
    `_collect_reflections` (ECHTE Pflicht-Reflexion, hier mit
    `ReflectionOnlyDriver` bedient) -> `finalize_section_after_reflection`
    (schreibt `__final.json`, loest Locks, schliesst den Tisch). KEIN
    GM-Aufruf, KEINE neue Spielzug-Entscheidung
    (`ExplodingGmTransport`/`ReflectionOnlyDriver` werfen bei jedem anderen
    Aufruf).
    Prozess 3 ist ein dritter frischer Prozess: ruft `store.complete_section`
    und `store.finalize_section_after_reflection` fuer denselben Abschnitt
    ERNEUT auf (derselbe Code, den jeder Retry/jede doppelte Zustellung
    durchlaeuft) -- beide liefern `already_completed=True, written=False`;
    Primaersaves/`__final.json` bleiben byteidentisch.

Export: fuer jede Szene werden die realen Ergebniswurzeln (Saves/
current_saves/Versions/Plan/Guards/Final/lab.decide/lab.stop/Admission-
Record/persona States/oeffentliche Spectator-Sicht, soweit fuer die Szene
zutreffend) VOR der Tempverzeichnis-Bereinigung nach
`run/r2/results/<szene>/` kopiert; bewusst NICHT entstandene Kategorien
(z. B. kein `__plan.json`/`__final.json` bei O3, kein Gast-Erschaffungs-
Grant/persoenlicher Gastsave in O3/O4 -- das ist ausserhalb dieser Szenen,
F4 ist bereits eigenstaendig abgenommen) werden als konkretes Vorher-/
Nachher-Inventar in `run/r2/results/<szene>/inventory.json` dokumentiert,
NIE als leerer Fake-Record angelegt. `run/r2/results/MANIFEST.json` bindet
je kopierte Datei `{path, sha256, bytes}` und je echtem Subprozesslauf
`{argv, cwd, utc_start, utc_end, exit, stdout_path, stderr_path}`.

Pure Python, nur `assert`, echter Exitcode, kein pytest."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
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
from _section_completion_resume_fixtures import build_two_member_table, make_env, seed_persona_state  # noqa: E402

import mmo_sim.core.admission as admission  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
import mmo_sim.core.table_admission as table_admission  # noqa: E402

_TODAY = "2026-11-04"
_RESULTS_ROOT = Path("/home/altair/zr-betreiber-gast-20261103/run/r2/results")

_MANIFEST: dict = {"files": [], "runs": []}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _utc(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))


def _export_file(szene: str, src: Path, rel: str) -> None:
    """Kopiert `src` nach `run/r2/results/<szene>/<rel>` (Bytes unveraendert)
    und traegt `{path, sha256, bytes}` in `_MANIFEST['files']` ein (`path`
    relativ zu `run/r2/results/`)."""
    dest = _RESULTS_ROOT / szene / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    _MANIFEST["files"].append({
        "path": str(dest.relative_to(_RESULTS_ROOT)),
        "sha256": _sha256(dest),
        "bytes": dest.stat().st_size,
    })


def _export_tree(szene: str, src_root: Path, rel_root: str) -> None:
    """Exportiert ALLE Dateien unter `src_root` (rekursiv) nach
    `<szene>/<rel_root>/...` -- real vorhandene Ergebniswurzeln (Saves,
    current_saves/Versions, completion/Plan/Final, lab.decide.table.*,
    lab.stop.table.*, table_admission/*, persona States, ...), je nachdem,
    was fuer DIESE Szene tatsaechlich entstanden ist."""
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


def _run_real_subprocess(szene: str, label: str, argv: list[str], **kw) -> subprocess.CompletedProcess:
    """Fuehrt `argv` als ECHTEN neuen OS-Prozess aus (`subprocess.run`),
    exportiert stdout/stderr als eigene Dateien und bindet den Lauf
    (`argv`/`cwd`/`utc_start`/`utc_end`/`exit`/stdout_path/stderr_path) in
    `_MANIFEST['runs']`."""
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


# ───────────────────────── Szene O3 ─────────────────────────

_O3_SUBPROCESS_SCRIPT = r"""
import json, sys
from pathlib import Path
sys.path.insert(0, {repo_root!r})
sys.path.insert(0, {fixtures_dir!r})

import mmo_sim.core.store as store
from mmo_sim.core.persona_state import PersonaStateStore
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy
from _full_v7_fixture import full_v7_save

run_dir = Path({run_dir!r})
states_dir = Path({states_dir!r})
schema_path = Path({schema_path!r})
table_id = {table_id!r}
section_id = {section_id!r}

ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
# Echter Frischprozess-Reload -- NUR von der Platte, kein geteilter Zustand.
table = store.Table.load(run_dir, table_id)

harvested = {{
    "leader_pk": full_v7_save("chrono-leader", name="Testfigur"),
    "guest_pk": full_v7_save("chrono-guest", name="Testfigur"),
}}
result = store.complete_section(
    lobby, table, section_id, harvested, states_dir, {today!r},
    ZeitrissHarvestValidator(), ps_store,
)
print(json.dumps({{"success": result.success, "written": result.written, "reason": result.reason}}))
"""


def run_scene_o3() -> None:
    szene = "o3"
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        env = make_env(root)
        lobby, table, ps_store = build_two_member_table(env, table_id="f5-o3-tisch")
        section_id = table.table_id

        # (1) Echte Startfassung -- ein realer full_v7_save, veroeffentlicht
        # ueber den echten Produktweg (`publish_current_save`), KEIN Fake-Dict.
        guest_start_block = full_v7_save("chrono-f5o3-start", name="GastStartfassungF5O3")
        store.publish_current_save(env.run_dir, "guest_pk", guest_start_block, ps_store, env.states_dir)
        guest_save_path = env.run_dir / "current_saves" / "guest_pk.json"
        assert guest_save_path.exists(), "publish_current_save haette die Gast-Startfassung real schreiben muessen."
        sha_before = _sha256(guest_save_path)

        # Auflage 3 (Critic-Vera, 02_NACHWEISE §1/§2): expliziter Isolations-
        # beleg -- eine UNBETEILIGTE Figur UND ein weiterer, unbeteiligter
        # Tischdatensatz im SELBEN run_dir muessen durch den tischadressierten
        # O3-Stop/Abbruch BYTE-IDENTISCH bleiben (Stop/Entscheid sind pro
        # table_id/table_key benannt -- keine Cross-Table-Interferenz).
        seed_persona_state(ps_store, env.states_dir, "bystander_pk", "chrono-f5o3-bystander")
        bystander_block = full_v7_save("chrono-f5o3-bystander", name="UnbeteiligteFigurF5O3")
        store.publish_current_save(env.run_dir, "bystander_pk", bystander_block, ps_store, env.states_dir)
        bystander_save_path = env.run_dir / "current_saves" / "bystander_pk.json"
        assert bystander_save_path.exists(), "Bystander-Startfassung haette real geschrieben werden muessen."
        table_admission.offer_table(env.run_dir, host_id="bystander_host", table_key="f5-o3-bystander-key")
        bystander_record_path = env.run_dir / "table_admission" / "f5-o3-bystander-key.json"
        assert bystander_record_path.exists(), "Bystander-Tischdatensatz haette existieren muessen."
        bystander_save_sha_before = _sha256(bystander_save_path)
        bystander_record_sha_before = _sha256(bystander_record_path)

        # Betreiber-Stop VOR jedem Abschlussversuch bindet+setzt (O6-Autoritaet).
        table_admission.offer_table(env.run_dir, host_id="leader_pk", table_key="f5-o3-key")
        table_admission.bind_section(
            env.run_dir, table_key="f5-o3-key", host_id="leader_pk", section_id=table.table_id,
        )
        stop_record = table_admission.request_table_stop(
            env.run_dir, table_key="f5-o3-key", operator_id="leader_pk", table_id=table.table_id,
            reason="F5-O3: Betreiber-Stop VOR jedem Abschlussversuch (echte Frischprozess-Probe).",
        )
        assert stop_record["decision"] == "stopped", stop_record
        stopped, stop_reason = admission.read_table_stop(env.run_dir, table.table_id)
        assert stopped is True and stop_reason, (stopped, stop_reason)
        decision = admission.read_table_decision(env.run_dir, table.table_id)
        assert decision is not None and decision.get("decision") == "stopped", decision

        plan_path = env.run_dir / "completion" / f"{section_id}__plan.json"
        final_path = env.run_dir / "completion" / f"{section_id}__final.json"
        before_inventory = {
            "plan_exists": plan_path.exists(), "final_exists": final_path.exists(),
            "guest_save_sha256": sha_before, "guest_save_bytes": guest_save_path.stat().st_size,
        }

        script = _O3_SUBPROCESS_SCRIPT.format(
            repo_root=str(_REPO_ROOT), fixtures_dir=str(_HERE),
            run_dir=str(env.run_dir), states_dir=str(env.states_dir),
            schema_path=str(root / "schema.json"), table_id=table.table_id, section_id=section_id,
            today=_TODAY,
        )
        clean_env = dict(os.environ)
        clean_env.pop("PYTHONPATH", None)
        result = _run_real_subprocess(
            szene, "proc1_fresh_abort_attempt", [sys.executable, "-B", "-c", script], env=clean_env,
        )
        assert result.returncode == 0, f"echter Frischprozess ist unerwartet abgestuerzt: {result.stderr}"
        payload = json.loads(result.stdout.strip().splitlines()[-1])
        assert payload["success"] is False, payload
        assert "Betreiber-Stop" in payload["reason"], payload["reason"]

        assert not plan_path.exists(), "O3: kein __plan.json darf bei aktivem Stop entstehen (frischer Prozess)."
        sha_after = _sha256(guest_save_path)
        assert sha_after == sha_before, "Gast-Startfassung wurde trotz Betreiber-Stop veraendert."
        bystander_save_sha_after = _sha256(bystander_save_path)
        bystander_record_sha_after = _sha256(bystander_record_path)
        assert bystander_save_sha_after == bystander_save_sha_before, (
            "Isolationsbruch: unbeteiligte Figur wurde durch den O3-Tischstop veraendert."
        )
        assert bystander_record_sha_after == bystander_record_sha_before, (
            "Isolationsbruch: unbeteiligter Tischdatensatz wurde durch den O3-Tischstop veraendert."
        )

        after_inventory = {
            "plan_exists": plan_path.exists(), "final_exists": final_path.exists(),
            "guest_save_sha256": sha_after, "guest_save_bytes": guest_save_path.stat().st_size,
        }

        # (3) Byte-Export VOR Tempverzeichnis-Bereinigung.
        _export_tree(szene, env.run_dir, "run")
        _export_tree(szene, env.states_dir, "states")
        spectator = store.spectator_view(store.Table.load(env.run_dir, table.table_id))
        _write_export_json(szene, "spectator_view.json", spectator)
        _write_export_json(szene, "inventory.json", {
            "before": before_inventory, "after": after_inventory,
            "bystander_isolation": {
                "unbeteiligte_figur": "current_saves/bystander_pk.json",
                "unbeteiligter_tischdatensatz": "table_admission/f5-o3-bystander-key.json",
                "figur_sha256_before": bystander_save_sha_before,
                "figur_sha256_after": bystander_save_sha_after,
                "figur_unveraendert": bystander_save_sha_after == bystander_save_sha_before,
                "tischdatensatz_sha256_before": bystander_record_sha_before,
                "tischdatensatz_sha256_after": bystander_record_sha_after,
                "tischdatensatz_unveraendert": bystander_record_sha_after == bystander_record_sha_before,
            },
            "notes": [
                "Isolationsbeleg (02_NACHWEISE §1/§2): eine unbeteiligte Figur UND ein weiterer "
                "Tischdatensatz im SELBEN run_dir bleiben durch den tischadressierten O3-Stop/Abbruch "
                "byte-identisch (sha256 vorher==nachher) -- Stop/Entscheid sind pro table_id/key benannt.",
                "kein __plan.json/__final.json: der Betreiber-Stop hat den atomaren Entscheid-Slot "
                "gewonnen, complete_section hat PHASE 1 nie erreicht -- bewusst kein Plan/Final, kein "
                "Fake-Record (vorher UND nachher identisch: beide fehlen).",
                "kein Gast-Erschaffungs-Grant/persoenlicher Gastsave (F4) in dieser Szene -- guest_pk ist "
                "ein bestehender Tischgast (build_two_member_table), keine Gast-Erschaffung; F4 ist "
                "eigenstaendig abgenommen (run/r2/worker/F4-report.md).",
            ],
        })


# ───────────────────────── Szene O4 ─────────────────────────

_O4_PROCESS_SCRIPT = r"""
import json, os, sys
from pathlib import Path
sys.path.insert(0, {repo_root!r})
sys.path.insert(0, {fixtures_dir!r})

import mmo_sim.core.store as store
from mmo_sim.adapters.base import ParticipantDecision
from mmo_sim.core.admission import write_test_profile
from mmo_sim.core.controller import TableController
from mmo_sim.core.runtime import SectionRuntime
from mmo_sim.core.persona_state import PersonaStateStore
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy
from _full_v7_fixture import full_v7_save
from _section_completion_resume_fixtures import (
    COMPLETION_MARKER, ReflectionOnlyDriver, ScriptedDriver, ScriptedGmTransport,
    debrief_with_marker, harvest_extractor, seed_persona_state,
)

run_dir = Path({run_dir!r})
states_dir = Path({states_dir!r})
schema_path = Path({schema_path!r})
table_id = {table_id!r}
section_id = {section_id!r}
role = {role!r}


class ExplodingGmTransport:
    # Beweis: nach Plan-Pin/Resume darf KEIN neuer GM-Turn erfolgen.
    def __init__(self):
        self.calls = 0

    def turn(self, turn_idx, user_text, **kwargs):
        self.calls += 1
        raise AssertionError("ExplodingGmTransport: kein neuer GM-Turn nach Plan-Pin/Resume erwartet.")


def _make_ps_store(write_schema):
    if write_schema:
        schema_path.write_text(
            '{{"type":"object","required":["v","persona_key","rounds_played"],'
            '"properties":{{"v":{{"const":2}}}}}}',
            encoding="utf-8",
        )
    return PersonaStateStore(schema_path=schema_path, default_states_dir=None)


if role == "process1":
    ps_store = _make_ps_store(write_schema=True)
    seed_persona_state(ps_store, states_dir, "leader_pk", "chrono-leader")
    seed_persona_state(ps_store, states_dir, "guest_pk", "chrono-guest")
    write_test_profile(run_dir)

    lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    lobby.join("leader_pk")
    lobby.join("guest_pk")
    table, derivation = store.create_table_from_offer_log(
        lobby, table_id,
        offer_log_events=[
            {{"type": "offer", "id": "o1", "from": "leader_pk", "wants": ["guest_pk"]}},
            {{"type": "consent", "offer_id": "o1", "from": "guest_pk", "accept": True}},
        ],
        chrononaut_ids={{"leader_pk": "chrono-leader", "guest_pk": "chrono-guest"}},
    )
    assert table is not None, derivation

    leader_save = full_v7_save("chrono-leader", name="Testfigur")
    guest_save = full_v7_save("chrono-guest", name="Testfigur")
    debrief = debrief_with_marker({{"chrono-leader": leader_save, "chrono-guest": guest_save}})

    gm = ScriptedGmTransport(["SL-Antwort auf Anker.", "SL-Antwort auf Gast-Import.", debrief])
    leader_driver = ScriptedDriver([
        ParticipantDecision(text="Anker-Text.", save_payload=leader_save, origin_source="fake:leader"),
        ParticipantDecision(text="Debrief-Anfrage.", origin_source="fake:leader-debrief"),
        ParticipantDecision(text="Reflexion Leader.", origin_source="fake:leader-reflect"),
    ])
    guest_driver = ScriptedDriver([
        ParticipantDecision(text="Gast-Import.", save_payload=guest_save, origin_source="fake:guest"),
        ParticipantDecision(text="Reflexion Gast.", origin_source="fake:guest-reflect"),
    ])
    controller = TableController(leader_key="leader_pk", drivers={{"leader_pk": leader_driver, "guest_pk": guest_driver}})
    runtime = SectionRuntime(
        lobby=lobby, table=table, gm_transport=gm, marker=COMPLETION_MARKER,
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        harvest_extractor=harvest_extractor,
    )

    def _hard_exit_before_reflection(*a, **kw):
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(94)

    # Monkeypatch NUR der Pflicht-Reflexions-Vorbedingung (Phase 2) -- Phase 1
    # (store.complete_section: Plan-Pin + Primaersave) ist zu diesem Zeitpunkt
    # bereits real abgeschlossen (runtime.py `finalize()`: complete_section ->
    # return_to_lobby -> _collect_reflections -> finalize_section_after_reflection).
    # Dieselbe Monkeypatch-Technik wie die bestehenden
    # StopAfterResponseGmTransport/_hard_kill_after_durable_persist-Fixtures:
    # ein Hard-Exit GENAU an der Prozessabbruch-Grenze, kein veraenderter Produktpfad.
    runtime._collect_reflections = _hard_exit_before_reflection

    runtime.run_full_section(
        controller, section_id,
        contexts_by_persona={{"leader_pk": {{"user": "ctx-leader"}}, "guest_pk": {{"user": "ctx-guest"}}}},
        states_dir=states_dir, today={today!r}, ts="2026-11-04T10:00:00",
    )
    print(json.dumps({{"unexpected_normal_return": True}}))

elif role == "process2":
    ps_store = _make_ps_store(write_schema=False)
    lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    table = store.Table.load(run_dir, table_id)

    gm2 = ExplodingGmTransport()
    leader_refl = ReflectionOnlyDriver(
        "Reflexion Leader nach Prozessabbruch/Recovery.", origin_source="fake:leader-reflect-recovery",
    )
    guest_refl = ReflectionOnlyDriver(
        "Reflexion Gast nach Prozessabbruch/Recovery.", origin_source="fake:guest-reflect-recovery",
    )
    controller2 = TableController(leader_key="leader_pk", drivers={{"leader_pk": leader_refl, "guest_pk": guest_refl}})
    runtime2 = SectionRuntime(
        lobby=lobby, table=table, gm_transport=gm2, marker=COMPLETION_MARKER,
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        harvest_extractor=harvest_extractor,
    )
    outcome = runtime2.run_full_section(
        controller2, section_id,
        contexts_by_persona={{"leader_pk": {{"user": "ctx-leader"}}, "guest_pk": {{"user": "ctx-guest"}}}},
        states_dir=states_dir, today={today!r}, ts="2026-11-04T10:10:00",
    )
    print(json.dumps({{
        "success": outcome.completion.success, "reason": outcome.completion.reason,
        "members_completed": outcome.completion.members_completed,
        "gm_calls": gm2.calls, "leader_reflection_calls": leader_refl.calls,
        "guest_reflection_calls": guest_refl.calls,
    }}))

elif role == "process3":
    ps_store = _make_ps_store(write_schema=False)
    lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    table = store.Table.load(run_dir, table_id)
    result1 = store.complete_section(
        lobby, table, section_id, {{}}, states_dir, {today!r},
        ZeitrissHarvestValidator(), ps_store,
    )
    result2 = store.finalize_section_after_reflection(lobby, table, section_id)
    print(json.dumps({{
        "complete_section_success": result1.success,
        "complete_section_already_completed": result1.already_completed,
        "complete_section_written": result1.written,
        "finalize_success": result2.success,
        "finalize_already_completed": result2.already_completed,
        "finalize_written": result2.written,
    }}))
"""


def run_scene_o4() -> None:
    szene = "o4"
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        states_dir = root / "states"
        states_dir.mkdir(parents=True)
        schema_path = root / "schema.json"
        table_id = "f5-o4-tisch"
        section_id = table_id

        common = dict(
            repo_root=str(_REPO_ROOT), fixtures_dir=str(_HERE),
            run_dir=str(run_dir), states_dir=str(states_dir), schema_path=str(schema_path),
            table_id=table_id, section_id=section_id, today=_TODAY,
        )
        clean_env = dict(os.environ)
        clean_env.pop("PYTHONPATH", None)

        # Prozess 1: echter Spielzug bis Plan-Pin+Primaersave (Phase 1), dann
        # os._exit NACH Plan-Pin/Primaersave, VOR Reflexion/Final (Phase 2).
        script1 = _O4_PROCESS_SCRIPT.format(role="process1", **common)
        proc1 = _run_real_subprocess(
            szene, "proc1_plan_pin_primary_save_hard_exit",
            [sys.executable, "-B", "-c", script1], env=clean_env,
        )
        assert proc1.returncode == 94, (
            f"Prozess 1 muss ueber os._exit(94) enden (NACH Plan-Pin/Primaersave, VOR Reflexion/Final) -- "
            f"rc={proc1.returncode} stderr={proc1.stderr!r}"
        )

        plan_path = run_dir / "completion" / f"{section_id}__plan.json"
        final_path = run_dir / "completion" / f"{section_id}__final.json"
        leader_save_path = run_dir / "current_saves" / "leader_pk.json"
        guest_save_path = run_dir / "current_saves" / "guest_pk.json"
        assert plan_path.exists(), "Prozess 1 haette den Plan real pinnen muessen (Phase 1)."
        assert leader_save_path.exists() and guest_save_path.exists(), (
            "Prozess 1 haette die Primaersaves real schreiben muessen."
        )
        assert not final_path.exists(), "Phase 2 (__final.json) darf von Prozess 1 NICHT erreicht worden sein."
        sha_leader_1 = _sha256(leader_save_path)
        sha_guest_1 = _sha256(guest_save_path)
        before_inventory = {
            "plan_exists": True, "final_exists": False,
            "leader_save_sha256": sha_leader_1, "guest_save_sha256": sha_guest_1,
        }

        # Prozess 2: frischer Prozess, echter Resume-Zweig -- idempotente
        # Phase-1-Ernte + echte Pflicht-Reflexion + echter Finalabschluss.
        script2 = _O4_PROCESS_SCRIPT.format(role="process2", **common)
        proc2 = _run_real_subprocess(
            szene, "proc2_fresh_resume_real_reflection_final",
            [sys.executable, "-B", "-c", script2], env=clean_env,
        )
        assert proc2.returncode == 0, f"Prozess 2 (Resume+Finalabschluss) ist unerwartet gescheitert: {proc2.stderr}"
        payload2 = json.loads(proc2.stdout.strip().splitlines()[-1])
        assert payload2["success"] is True, payload2
        assert set(payload2["members_completed"]) == {"leader_pk", "guest_pk"}, payload2
        assert payload2["gm_calls"] == 0, "Resume darf KEINEN neuen GM-Turn ausloesen -- " + repr(payload2)
        assert payload2["leader_reflection_calls"] == 1 and payload2["guest_reflection_calls"] == 1, (
            "echte Pflicht-Reflexion fuer BEIDE Mitglieder erwartet -- " + repr(payload2)
        )
        assert final_path.exists(), "Prozess 2 haette __final.json ueber den echten Produktweg schreiben muessen."
        assert _sha256(leader_save_path) == sha_leader_1, "Doppel-Harvest: leader_pk-Save beim Resume veraendert."
        assert _sha256(guest_save_path) == sha_guest_1, "Doppel-Harvest: guest_pk-Save beim Resume veraendert."
        sha_final_1 = _sha256(final_path)

        # Prozess 3: dritter frischer Prozess, idempotenter Retry -- KEINE Doppelwirkung.
        script3 = _O4_PROCESS_SCRIPT.format(role="process3", **common)
        proc3 = _run_real_subprocess(
            szene, "proc3_idempotent_retry_no_double_effect",
            [sys.executable, "-B", "-c", script3], env=clean_env,
        )
        assert proc3.returncode == 0, f"Prozess 3 (idempotenter Retry) ist unerwartet gescheitert: {proc3.stderr}"
        payload3 = json.loads(proc3.stdout.strip().splitlines()[-1])
        assert payload3["complete_section_success"] is True and payload3["complete_section_already_completed"] is True
        assert payload3["complete_section_written"] is False
        assert payload3["finalize_success"] is True and payload3["finalize_already_completed"] is True
        assert payload3["finalize_written"] is False
        assert _sha256(leader_save_path) == sha_leader_1
        assert _sha256(guest_save_path) == sha_guest_1
        assert _sha256(final_path) == sha_final_1, "Dritter Retry hat __final.json erneut geschrieben (Doppelwirkung)."

        after_inventory = {
            "plan_exists": plan_path.exists(), "final_exists": final_path.exists(),
            "leader_save_sha256": _sha256(leader_save_path), "guest_save_sha256": _sha256(guest_save_path),
            "final_sha256": sha_final_1,
        }

        _export_tree(szene, run_dir, "run")
        _export_tree(szene, states_dir, "states")
        spectator = store.spectator_view(store.Table.load(run_dir, table_id))
        _write_export_json(szene, "spectator_view.json", spectator)
        _write_export_json(szene, "inventory.json", {
            "before": before_inventory, "after": after_inventory,
            "notes": [
                "kein Admission-/lab.stop-/lab.decide-Record in dieser Szene: O4 testet Plan-Pin + "
                "Prozessabbruch + Resume OHNE Betreiber-Stop (anders als O3) -- bewusst keine Stop-/"
                "Entscheid-Datei, kein Fake-Record.",
                "kein Gast-Erschaffungs-Grant/persoenlicher Gastsave (F4) in dieser Szene -- guest_pk ist "
                "ein bestehender Tischgast, keine Gast-Erschaffung; F4 ist eigenstaendig abgenommen "
                "(run/r2/worker/F4-report.md).",
                "Prozess 3 nutzt bewusst DIREKTE store.complete_section/finalize_section_after_reflection-"
                "Aufrufe (nicht den vollen run_full_section-Weg) fuer den Idempotenz-Beweis -- der Tisch "
                "ist nach Prozess 2 bereits 'closed', derselbe Direktaufruf-Codepfad wie der bereits "
                "abgenommene O4-R1-Idempotenztest (test_zr_betreiber_o4_stop_nach_planpin_2026_11_03.py).",
            ],
        })


def main() -> int:
    if _RESULTS_ROOT.exists():
        shutil.rmtree(_RESULTS_ROOT)
    _RESULTS_ROOT.mkdir(parents=True)

    scenes = [("o3", run_scene_o3), ("o4", run_scene_o4)]
    failed = 0
    for name, fn in scenes:
        try:
            fn()
            print(f"OK   scene_{name}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL scene_{name}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR scene_{name}:")
            traceback.print_exc()

    manifest_path = _RESULTS_ROOT / "MANIFEST.json"
    manifest_path.write_text(json.dumps(_MANIFEST, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{len(scenes) - failed}/{len(scenes)} Szenen bestanden.")
    print(f"MANIFEST: {manifest_path} ({len(_MANIFEST['files'])} Dateien, {len(_MANIFEST['runs'])} Laeufe)")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
