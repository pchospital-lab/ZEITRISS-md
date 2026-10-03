#!/usr/bin/env python3
"""
tests/mmo_sim/test_h05_stop_lifecycle_2026_09_29.py — H05 Stop-Lebenszyklus
(Auftragspaket `zeitriss-p2-headless-h02-abnahme-h05-auftrag-2026-09-29-r1`,
02_AUFTRAG_H05.md): spaetere Stopgrenzen, passive Beobachterenden und
Controllerunterbrechung ueber die bereits abgenommenen H02-Bausteine (Lobby-/
Tischbildung, G0-G4, Phase-1-Ernte/Phase-2-Reflexion, request_ledger) hinweg.

P0 (Erhalt) ist das UNVERAENDERTE `test_h02_vollreise_profiles_2026_09_28.py`
selbst -- hier NICHT dupliziert, nur importiert und fuer die Fixture-/
Sequenz-/Validator-Wiederverwendung referenziert (`h02journey`). Diese Datei
implementiert ausschliesslich P1-P5:

- P1 GM-Stop (API + Hybrid-Fake-CLI+API-SL): natuerliche Lobby-/Tischbildung,
  G0/G1-Import, Empfaengerbarriere VOR einer angefragten NICHT-finalen
  GM-Antwort (G2), zwei separate `lab stop`.
- P2 Reflexions-Stop (API + Hybrid): echte vollstaendige G4-Antwort,
  natuerliche Phase-1-Ernte, Barriere an der ersten von zwei
  Pflichtreflexionen, zwei separate `lab stop`, nur diese eine Antwort
  freigegeben.
- P3 Observerende: ein eigener API-Controller haelt einen belegten
  in-flight-Request; zwei unabhaengige `lab attach --follow`-Prozesse (einer
  stdin-EOF ueber eigene Pipe, einer SIGINT), Controller bleibt Owner.
- P4 Controllersignale: API-Controller echtes SIGINT, Hybrid-Controller
  echtes SIGTERM, jeweils nach unabhaengig bestaetigtem Versand vor
  Antwortausgabe.
- P5 harte Unterbrechung: eigener API-Controller, Request bestaetigt/Antwort
  zurueckgehalten, SIGKILL nur auf diese PID, dann expliziter `lab resume`.

Nur `scripts/mmo_sim.py lab start/resume/status/stop/attach` als echte neue
Python-Subprozesse; Persona-/GM-Empfaenger sind ausschliesslich eigene
`127.0.0.1:0`-Loopback-Server bzw. eine selbst erzeugte ausfuehrbare
Fake-CLI-Datei -- keine realen Anbieter/Keys. Barrieren halten den
tatsaechlich empfangenen Request VOR Antwortausgabe zurueck (kein Sleep als
Beweis). Wiederverwendet werden AUSSCHLIESSLICH bereits abgenommene H02-
Bausteine (`_h02_vollreise_support.py` als `sup`, die H02-Testdatei selbst
als `h02journey` -- beide UNVERAENDERT, nur importiert) plus die neuen,
testlokalen H05-Barrierehelfer (`_h05_stop_support.py` als `h05sup`)."""
from __future__ import annotations

import copy
import datetime
import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import _h02_vollreise_support as sup  # noqa: E402
import _h05_stop_support as h05sup  # noqa: E402
import test_h02_vollreise_profiles_2026_09_28 as h02journey  # noqa: E402
from mmo_sim.core import lobby_service  # noqa: E402
from mmo_sim.core import request_ledger  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.lab import runner as lab_runner  # noqa: E402

_MMO_SIM = sup.MMO_SIM
TABLE_ID = "lobby-sniper-tech"
SECTION_ID = "lobby-sniper-tech-section"


def _bootstrap_table_prereqs(root: Path, community_participant_id: str):
    """Gemeinsame Vorbereitung fuer P1-P5 (N2-Nachzug, 02_AUFTRAG_
    NACHWEISABSCHLUSS.md N2): GROSSE bestaetigte Community ueber die
    vorhandenen H02-Bootstrap-/Onboarding-/Registryhelfer -- alle sechs
    unterscheidbaren KI-Personas (`sup.SIX_PERSONAS`, Default von
    `bootstrap_six_persona_community`, vorher explizit auf nur
    `("sniper","tech")` eingeschraenkt) PLUS eine echte synthetische
    Human-Teilnehmeridentitaet mit eigener Figur/`record_refs`
    (`register_human_participant`+`onboard_human_figure`, identischer
    Produktweg wie in H02s eigenen N-HUMAN-/Vollreise-Faellen). NUR
    sniper+tech sind ueber `--personas sniper,tech` die freiwillige
    Modellselektion/Zweiertisch -- die vier restlichen Personas und der
    Mensch bleiben Bystander: bootstrapped/ready, aber nie am Tisch. Ihr
    Schutz "vor+nach" wird NICHT hier erzwungen, sondern durch die
    vollstaendigen `protected_authority_hashes["persona_states"]`-Vergleiche
    (hasht den GESAMTEN `states_dir`, s. `_assert_protected_unchanged`) an
    jedem Phasenpunkt in den P1-P5-Faellen selbst. Rueckgabe: (schema_path,
    states_dir, run_dir, onboarding_dir, guard_dir, offer_id,
    human_participant_id)."""
    guard_dir = sup.write_loopback_guard(root / "guard")
    community_id = f"community-{community_participant_id}"
    schema_path, states_dir, run_dir, onboarding_dir, _catalog = sup.bootstrap_six_persona_community(
        root, community_id,
    )
    for pk in sup.SIX_PERSONAS:
        sup.make_ready(onboarding_dir, states_dir, run_dir, pk)
    registry_dir = root / "participants"
    human = sup.register_human_participant(registry_dir, f"H05-Operator-Mensch-{community_participant_id}")
    human = sup.onboard_human_figure(registry_dir, human.participant_id, onboarding_dir, states_dir, run_dir)
    write_test_profile(run_dir, max_usd=5.0)
    status_before = lab_runner.read_status(run_dir)
    assert status_before is not None and status_before.provider_free is True, (
        f"provider_free muss VOR Start bereits True sein: {status_before}"
    )
    offer_id = h02journey._offer_id_for_first_window(community_participant_id)
    return schema_path, states_dir, run_dir, onboarding_dir, guard_dir, offer_id, human.participant_id


def _controller_env(
    *, tmp_root: Path, guard_dir: Path, extra: dict, require_schema_dependency: bool = True,
) -> dict:
    """Baut das isolierte Kind-Env fuer einen DIREKT (nicht ueber
    `h02journey._run_lab`, das blockierend `communicate()` aufruft) gestarteten
    langlebigen Controller-`Popen` -- dieselbe jsonschema-Sichtbarkeitskopie
    (Hashbeleg, keine Installation) und dasselbe Guard-/HOME-/TMP-Muster wie
    `_run_lab`, nur ohne den blockierenden Aufruf."""
    schema_dependency_dir = None
    if require_schema_dependency:
        schema_dependency_dir, manifest = sup.copy_dependency_visibility(tmp_root / "schema-dependency-visibility")
        env_probe = sup.minimal_lab_env(extra, tmp_root=tmp_root, guard_dir=guard_dir, schema_dependency_dir=schema_dependency_dir)
        proof = sup.probe_schema_dependency(env_probe)
        assert proof.get("available") is True and proof.get("functional_validate_ok") is True, (
            f"H05: benoetigte jsonschema-Dependency im echten Controller-Kind-Env nicht nachweisbar: {proof} "
            f"(manifest={manifest})"
        )
    return sup.minimal_lab_env(extra, tmp_root=tmp_root, guard_dir=guard_dir, schema_dependency_dir=schema_dependency_dir)


def _utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _start_controller(args: list[str], *, env: dict) -> subprocess.Popen:
    """N3-Nachzug: der reale, langlebige Controller-`Popen` wird bisher NIE
    journalisiert (nur die kurzlebigen `stop`/`resume`-Aufrufe ueber
    `h02journey._run_lab`+`_log_invocation`) -- argv/cwd/env/started_utc
    werden hier direkt am `Popen`-Objekt als eigene Attribute abgelegt
    (analog `_run_lab`s `_h02_pid`/`_h02_started_utc`-Muster), damit
    `_log_controller_invocation` sie NACH Prozessende in die permanente
    `case`-Evidenzablage schreiben kann, BEVOR das umgebende
    `tempfile.TemporaryDirectory` geraeumt wird."""
    argv = [sys.executable, str(_MMO_SIM), "lab", *args]
    started_utc = _utc_now_iso()
    proc = subprocess.Popen(
        argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env,
        cwd=str(_REPO_ROOT),
    )
    proc._h05_argv = argv  # type: ignore[attr-defined]
    proc._h05_cwd = str(_REPO_ROOT)  # type: ignore[attr-defined]
    proc._h05_env_min = dict(env)  # type: ignore[attr-defined]
    proc._h05_started_utc = started_utc  # type: ignore[attr-defined]
    return proc


def _finish_controller(proc: subprocess.Popen, *, timeout: int = 20) -> tuple[str, str, bool]:
    """Rueckgabe jetzt `(out, err, timed_out)` (N3): ein durch Timeout
    erzwungener `kill()` ist laut Auftrag KEIN fachlicher Erfolg -- der
    Aufrufer muss das unterscheiden statt es zu verschlucken."""
    timed_out = False
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        proc.kill()
        out, err = proc.communicate(timeout=10)
    proc._h05_ended_utc = _utc_now_iso()  # type: ignore[attr-defined]
    return out, err, timed_out


def _log_controller_invocation(
    case: Path, name: str, proc: subprocess.Popen, out: str, err: str, *, timeout: int, timed_out: bool = False,
) -> None:
    """N3: vollstaendiger Controller-Prozessbeleg -- echte PID/argv/cwd/
    Interpreter/min-Env/UTC-Start-Ende/Exit/Timeout -- PLUS die tatsaechlichen
    stdout/stderr-Rohbytes VOLLSTAENDIG (kein 2000-Zeichen-Tail, kein aus
    Prosa rekonstruierter Text), in die permanente `case`-Evidenzablage
    geschrieben (nicht `root`/`td` -- das wird beim Testende geraeumt)."""
    sup.append_jsonl(case / "invocations.json", {
        "name": name, "argv": getattr(proc, "_h05_argv", None), "cwd": getattr(proc, "_h05_cwd", None),
        "pid": proc.pid, "interpreter": sys.executable, "env_min": getattr(proc, "_h05_env_min", {}),
        "started_utc": getattr(proc, "_h05_started_utc", None), "ended_utc": getattr(proc, "_h05_ended_utc", None),
        "returncode": proc.returncode, "timeout_seconds": timeout, "timed_out_and_killed": timed_out,
    })
    (case / f"stdout.{name}.txt").write_text(out, encoding="utf-8")
    (case / f"stderr.{name}.txt").write_text(err, encoding="utf-8")


def _log_signal_event(case: Path, name: str, *, pid: int, sig: "signal.Signals", note: str = "") -> dict:
    """N3: 'eigenes Signal-/Stopereignis' als EIGENSTAENDIGER Beleg, getrennt
    von der reinen Prozess-Invocation -- vorher wurde z.B. `wall_ts_signal_
    sent = time.time()` berechnet und NIE gespeichert (totes Zwischenergebnis,
    kein Beleg). Persistiert VOR jedem Cleanup in `case/signal-events.json`."""
    event = {
        "name": name, "pid": pid, "signal": sig.name, "signum": int(sig),
        "sent_wall_ts": time.time(), "sent_monotonic": time.monotonic(), "note": note,
    }
    sup.append_jsonl(case / "signal-events.json", event)
    return event


def _standard_start_args(root: Path, community_participant_id: str, profile: str) -> list[str]:
    return [
        "start", "--data-dir", str(root), "--community", community_participant_id, "--profile", profile,
        "--personas", "sniper,tech", "--max-requests", "40", "--max-seconds", "120",
        "--max-usd", "5", "--max-idle-windows", "1", "--max-wall-seconds", "90",
    ]


def _ledger_records_snapshot(run_dir: Path) -> list[dict]:
    return copy.deepcopy(request_ledger._all_records(run_dir))


_ALWAYS_PROTECTED_KEYS = (
    "persona_states", "current_saves_and_versions", "completion", "tables", "locks.json", "reflections.jsonl",
)


def _assert_protected_unchanged(
    before: dict, after: dict, *, except_keys: "frozenset[str]" = frozenset(), context: str = "",
) -> None:
    """N1: vergleicht `protected_authority_hashes` (aus `h02journey.
    _authority_state_snapshot`, UNVERAENDERT wiederverwendet) Schluessel fuer
    Schluessel -- `persona_states` ist ein Hash des GESAMTEN `states_dir`
    (alle sechs KI-Personas + die synthetische Human-Figur aus N2, nicht nur
    sniper/tech), `current_saves_and_versions`/`completion`/`tables` je ein
    Hash des vollstaendigen jeweiligen Verzeichnisses unter `run_dir`.
    `except_keys` benennt NUR die laut fester Falltabelle (02_AUFTRAG_H05.md,
    Spalte 'Erlaubt') fuer DIESEN Fall ausdruecklich erlaubten Aenderungen
    (z.B. P1s SL-Append in `tables`, P2s erhaltene Reflexion in
    `persona_states`/`reflections.jsonl`) -- alle uebrigen Schluessel MUESSEN
    bytegleich bleiben. Als PERMANENTE Assertion aufgerufen, nicht nur zur
    Belegablage."""
    before_hashes = before["protected_authority_hashes"]
    after_hashes = after["protected_authority_hashes"]
    # Die P2-Ausnahme erlaubt nur die eine empfangene eigene Reflexion,
    # nicht beliebige Aenderungen am gesamten states/-Verzeichnis.
    if "persona_states" in except_keys:
        required = [r for r in after["reflections"] if r.get("kind") == "ai_required_reflection"]
        assert len(required) == 1 and required[0]["persona_key"] == "sniper", context
        reflection = required[0]
        assert before_hashes["persona_states"].keys() == after_hashes["persona_states"].keys(), context
        for name, digest in before_hashes["persona_states"].items():
            if name != "sniper.json":
                assert after_hashes["persona_states"][name] == digest, f"{context}: fremder State {name} geaendert"
        for pk, old in before["persona_states"].items():
            new = after["persona_states"][pk]
            if pk != "sniper":
                assert new == old, f"{context}: fremde Persona {pk} geaendert"
                continue
            permitted = {"last_reflection", "pending_reflections"}
            assert {k:v for k,v in new.items() if k not in permitted} == {k:v for k,v in old.items() if k not in permitted}, context
            assert new["last_reflection"] == reflection["text"], context
            pending = list(old.get("pending_reflections") or [])
            expected = {k: reflection[k] for k in ("section_id", "text", "ts")}
            assert new["pending_reflections"] == pending + [expected], context
    for key in _ALWAYS_PROTECTED_KEYS:
        if key in except_keys:
            continue
        assert after_hashes.get(key) == before_hashes.get(key), (
            f"{context}: geschuetzter Autoritaetsbereich {key!r} haette unveraendert bleiben muessen "
            f"(before={before_hashes.get(key)!r} after={after_hashes.get(key)!r})"
        )


def _assert_gm_append(before: dict, after: dict, receipt: dict) -> None:
    """Nur der eine, wirklich empfangene G2-Ausgang darf den Tisch erweitern."""
    assert {k:v for k,v in before.items() if k != "sl_log"} == {k:v for k,v in after.items() if k != "sl_log"}
    assert after["sl_log"][:-1] == before["sl_log"] and len(after["sl_log"]) == len(before["sl_log"]) + 1
    assert receipt["egress_state"] == "written" and receipt["egress_status"] == 200
    entry = after["sl_log"][-1]
    assert entry["content"] == receipt["egress_body"]["choices"][0]["message"]["content"]
    assert entry["leader_message"] == receipt["body"]["messages"][-1]["content"]
    assert entry["turn_idx"] == len(before["sl_log"]) and entry["origin_persona_key"] == "tech"
    assert entry["save_payload"] is None


# ---------------------------------------------------------------------------
# P1 -- GM-Stop (API): Empfaengerbarriere VOR der G2-Antwort (nicht-final).
# ---------------------------------------------------------------------------

def test_p1_gm_stop_api():
    case = sup.case_dir("P1_gm_stop_api")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        community_participant_id = "h05p1api"
        schema_path, states_dir, run_dir, onboarding_dir, guard_dir, offer_id, human_pid = _bootstrap_table_prereqs(
            root, community_participant_id,
        )
        sup.write_json(case / "human-participant.json", {"human_participant_id": human_pid})
        seq = h02journey._persona_response_sequence_for_full_journey(offer_id)
        gm_texts = h02journey._gm_response_texts(TABLE_ID, SECTION_ID)
        persona_validators_full = h02journey._persona_validators_for_full_journey(offer_id, TABLE_ID, SECTION_ID)
        gm_validators_full = h02journey._gm_validators_for_full_journey(seq)

        persona_receipts_path = case / "persona-receipts.jsonl"
        gm_receipts_path = case / "gm-receipts.jsonl"

        persona_validators = {0: sup.make_persona_input_validator("sniper", None, expected_current=sup.load_fixture_save("sniper"))}
        for i in range(4):
            persona_validators[i + 1] = persona_validators_full[i]

        GmHandler, block_event, release_event, gm_receipts, gm_validation_failures = h05sup.make_stalling_handler(
            pre_block_bodies=[
                {"choices": [{"message": {"content": gm_texts[0]}}], "usage": {}},
                {"choices": [{"message": {"content": gm_texts[1]}}], "usage": {}},
            ],
            block_response_body={"choices": [{"message": {"content": gm_texts[2]}}], "usage": {}},
            validators={0: gm_validators_full[0], 1: gm_validators_full[1], 2: gm_validators_full[2]},
            wait_timeout=30.0, label="p1-gm-api",
        journal_path=case / 'p1-gm-api-wire-events.jsonl', )
        gm_srv, gm_thread, gm_base_url = h05sup.start_http_server(GmHandler)
        proc = None
        try:
            with sup.recording_http_server(
                [(200, {"choices": [{"message": {"content": h02journey._leader_nomination_proposal()}}]})]
                + [(200, {"choices": [{"message": {"content": seq[i]}}], "usage": {}}) for i in range(4)],
                receipts_path=persona_receipts_path, label="p1-persona-api", validators=persona_validators,
            ) as persona_srv:
                env = _controller_env(
                    tmp_root=root / "kidtmp_controller", guard_dir=guard_dir,
                    extra={
                        "MMO_SIM_PERSONA_API_BASE_URL": persona_srv.base_url,
                        "MMO_SIM_PERSONA_API_KEY": "SYNTH-H05-NOT-A-REAL-KEY",
                        "MMO_SIM_PERSONA_API_MODEL": "synthetic-h05-persona",
                        "OPENWEBUI_URL": gm_base_url, "OPENWEBUI_API_KEY": "SYNTH-H05-NOT-A-REAL-KEY",
                        "MMO_SIM_GM_OUTPUT_LIMIT_TOKENS": "4096",
                        "MMO_SIM_LOBBY_INITIATIVE_LIMIT": "8",
                    },
                )
                start_args = _standard_start_args(root, community_participant_id, "api")
                proc = _start_controller(start_args, env=env)

                assert block_event.wait(timeout=20), "G2-Anfrage haette real am Handler ankommen muessen"
                assert gm_validation_failures == [], f"P1: GM-Empfaenger meldet Inputvalidierungsfehler: {gm_validation_failures}"
                assert persona_srv.validation_failures == [], (
                    f"P1: Persona-Empfaenger meldet Inputvalidierungsfehler: {persona_srv.validation_failures}"
                )

                state_before_stop = h02journey._authority_state_snapshot(run_dir, states_dir, schema_path)
                p1_table_before = json.loads((run_dir / "tables" / f"{TABLE_ID}.json").read_text())
                ledger_before_stop = _ledger_records_snapshot(run_dir)
                sup.write_json(case / "state-1-before-stop.json", state_before_stop)
                sup.write_json(case / "ledger-1-before-stop.json", ledger_before_stop)
                assert state_before_stop["tables"].get(f"{TABLE_ID}.json", {}).get("status") is None or \
                    state_before_stop["tables"][f"{TABLE_ID}.json"]["status"] == "active", state_before_stop["tables"]

                stop1_args = ["stop", "--data-dir", str(root), "--reason", "H05-P1-gm-stop"]
                stop2_args = ["stop", "--data-dir", str(root), "--reason", "H05-P1-gm-stop-repeat"]
                p_stop1 = h02journey._run_lab(stop1_args, tmp_root=root / "kidtmp_stop1", guard_dir=guard_dir)
                h02journey._log_invocation(case, "stop_1", stop1_args, {}, p_stop1)
                assert p_stop1.returncode == 0, p_stop1.stderr
                assert "Stop angefordert" in p_stop1.stdout, p_stop1.stdout
                p_stop2 = h02journey._run_lab(stop2_args, tmp_root=root / "kidtmp_stop2", guard_dir=guard_dir)
                h02journey._log_invocation(case, "stop_2", stop2_args, {}, p_stop2)
                assert p_stop2.returncode == 0, p_stop2.stderr

                state_barrier_held = h02journey._authority_state_snapshot(run_dir, states_dir, schema_path)
                sup.write_json(case / "state-2-barrier-held.json", state_barrier_held)
                assert state_barrier_held["lab_stop_file_exists"] is True
                assert state_barrier_held["turns_used"] == state_before_stop["turns_used"], (
                    "P1: turns_used haette sich WAEHREND gehaltener Barriere nicht aendern duerfen"
                )
                assert state_barrier_held["currents"] == state_before_stop["currents"]
                assert state_barrier_held["persona_states"] == state_before_stop["persona_states"]
                assert state_barrier_held["reflections_count"] == 0
                _assert_protected_unchanged(
                    state_before_stop, state_barrier_held, context="P1-API barrier-held vs before-stop",
                )

                release_event.set()
                out, err, timed_out = _finish_controller(proc)
                _log_controller_invocation(case, "controller_start", proc, out, err, timeout=20, timed_out=timed_out)
        finally:
            h05sup.stop_http_server(gm_srv, gm_thread)

        assert proc.returncode == 0, out + err
        assert "Lobby-Tisch abgeschlossen" not in out, out
        state_after_release = h02journey._authority_state_snapshot(run_dir, states_dir, schema_path)
        ledger_after_release = _ledger_records_snapshot(run_dir)
        sup.write_json(case / "state-3-after-release.json", state_after_release)
        sup.write_json(case / "ledger-3-after-release.json", ledger_after_release)
        _assert_protected_unchanged(
            state_before_stop, state_after_release, except_keys=frozenset({"tables"}),
            context="P1-API after-release vs before-stop",
        )

        # `begin()` committet SOFORT (state=sent), bevor der Transport laeuft
        # (Case 05) -- die blockierte G2-GM-Antwort war deshalb bereits VOR
        # der Barriere als eigener (state=sent) Datensatz in `ledger_before_stop`
        # enthalten. Erlaubt ist NUR ihr Uebergang sent->accounted, KEIN
        # zusaetzlicher (neuer) Requestdatensatz jeglicher Rolle.
        accounted_before = [r for r in ledger_before_stop if r.get("state") == "accounted"]
        accounted_after = [r for r in ledger_after_release if r.get("state") == "accounted"]
        assert len(ledger_after_release) == len(ledger_before_stop), (
            f"P1: kein Folgerequest jeglicher Rolle erwartet (Gesamtzahl Requestdatensaetze darf sich durch "
            f"Freigabe nicht aendern): vorher={len(ledger_before_stop)} nachher={len(ledger_after_release)}"
        )
        assert len(accounted_before) == len(ledger_before_stop) - 1, (
            f"P1: vor Freigabe muss GENAU der eine G2-GM-Datensatz noch nicht 'accounted' sein (state=sent, "
            f"in-flight): accounted_before={len(accounted_before)} total_before={len(ledger_before_stop)}"
        )
        assert len(accounted_after) == len(ledger_after_release), (
            f"P1: NACH Freigabe muessen ALLE (weiterhin gleich vielen) Requestdatensaetze 'accounted' sein "
            f"(die eine G2-Antwort wurde einmal verbucht, sonst nichts Neues): accounted_after={len(accounted_after)} "
            f"total_after={len(ledger_after_release)}"
        )
        assert state_after_release["reflections_count"] == 0, "P1: keine Reflexion an einer blockierten GM-Antwort erlaubt"
        table = core_store.Table.load(run_dir, TABLE_ID)
        _assert_gm_append(p1_table_before, json.loads((run_dir / "tables" / f"{TABLE_ID}.json").read_text()), gm_receipts[2])
        assert table.status == "active", f"P1: Tisch/Abschnitt muessen offen bleiben: {table.status}"
        assert len(table.sl_log) == 3, f"P1: G0,G1,G2 = 3 sl_log-Eintraege erwartet (die eine G2-Antwort verbucht): {len(table.sl_log)}"
        assert state_after_release["currents"] == state_before_stop["currents"], (
            "P1: kein erfundener Abschluss/zusaetzlicher Current -- Currents muessen vs. vor-Stop unveraendert bleiben"
        )
        assert gm_receipts[2]["egress_sent_monotonic"] > gm_receipts[2]["received_monotonic"], (
            "P1: Ausgang der G2-Antwort muss zeitlich NACH ihrem Empfang liegen (Barriere hielt sie tatsaechlich zurueck)"
        )
        sup.write_json(case / "gm-independent-receipts.json", gm_receipts)

        sup.write_json(case / "result.json", {
            "status": "PASS", "controller_returncode": proc.returncode,
            "ledger_before": len(ledger_before_stop), "ledger_after": len(ledger_after_release),
            "table_status": table.status, "sl_log_len": len(table.sl_log),
        })


# ---------------------------------------------------------------------------
# P1 -- GM-Stop (Hybrid-Fake-CLI+API-SL): identische GM-Barriere wie P1-API,
# Persona-Transport ueber echte `PersonaClaudeCodeDriver` + eigene
# ausfuehrbare Fake-CLI (unblockiert -- P1 blockiert die SL/GM-Seite, nicht
# die Persona-Seite).
# ---------------------------------------------------------------------------

_SL_LOG_LEN_BY_SEQ_IDX_0_3 = {0: None, 1: 0, 2: 1, 3: 2}  # seq[0]=Consent (kein sl_log-Feld), seq[1..3]=G0/G1/G2.


def test_p1_gm_stop_hybrid():
    case = sup.case_dir("P1_gm_stop_hybrid")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        community_participant_id = "h05p1hybrid"
        schema_path, states_dir, run_dir, onboarding_dir, guard_dir, offer_id, human_pid = _bootstrap_table_prereqs(
            root, community_participant_id,
        )
        sup.write_json(case / "human-participant.json", {"human_participant_id": human_pid})
        seq = h02journey._persona_response_sequence_for_full_journey(offer_id)
        gm_texts = h02journey._gm_response_texts(TABLE_ID, SECTION_ID)
        gm_validators_full = h02journey._gm_validators_for_full_journey(seq)

        cli_capture = case / "cli-receipts.jsonl"
        queue = [{
            "result": h02journey._leader_nomination_proposal(),
            "expect_all": [sup.own_figure_marker("sniper"), sup.own_current_full_marker(sup.load_fixture_save("sniper"))],
        }]
        for i in range(4):
            pk = h02journey._SEQ_PK[i]
            expect_all = [sup.own_figure_marker(pk), sup.own_current_full_marker(sup.load_fixture_save(pk))]
            if i == 0:
                expect_all = expect_all + [f"offer_id={offer_id}"]
            queue.append({
                "result": seq[i], "expect_all": expect_all,
                "expect_sl_log_len": _SL_LOG_LEN_BY_SEQ_IDX_0_3[i],
            })
        fake_cli = sup.write_queued_fake_cli(root, capture_path=cli_capture, queue=queue)
        isolated_workdir = root / "cli_workdir"
        isolated_workdir.mkdir(parents=True, exist_ok=True)

        GmHandler, block_event, release_event, gm_receipts, gm_validation_failures = h05sup.make_stalling_handler(
            pre_block_bodies=[
                {"choices": [{"message": {"content": gm_texts[0]}}], "usage": {}},
                {"choices": [{"message": {"content": gm_texts[1]}}], "usage": {}},
            ],
            block_response_body={"choices": [{"message": {"content": gm_texts[2]}}], "usage": {}},
            validators={0: gm_validators_full[0], 1: gm_validators_full[1], 2: gm_validators_full[2]},
            wait_timeout=30.0, label="p1-gm-hybrid",
        journal_path=case / 'p1-gm-hybrid-wire-events.jsonl', )
        gm_srv, gm_thread, gm_base_url = h05sup.start_http_server(GmHandler)
        proc = None
        try:
            env = _controller_env(
                tmp_root=root / "kidtmp_controller", guard_dir=guard_dir,
                extra={
                    "OPENWEBUI_URL": gm_base_url, "OPENWEBUI_API_KEY": "SYNTH-H05-NOT-A-REAL-KEY",
                    "MMO_SIM_GM_OUTPUT_LIMIT_TOKENS": "4096",
                    "MMO_SIM_LOBBY_INITIATIVE_LIMIT": "8",
                    "MMO_SIM_PERSONA_CLI": str(fake_cli),
                    "MMO_SIM_PERSONA_ISOLATED_WORKDIR": str(isolated_workdir),
                    "MMO_SIM_PERSONA_ISOLATION_FLAGS": "--permission-mode=plan,--safe-mode",
                },
            )
            start_args = _standard_start_args(root, community_participant_id, "hybrid")
            proc = _start_controller(start_args, env=env)

            assert block_event.wait(timeout=20), "G2-Anfrage haette real am Handler ankommen muessen"
            assert gm_validation_failures == [], f"P1-Hybrid: GM-Empfaenger meldet Inputvalidierungsfehler: {gm_validation_failures}"
            assert (cli_capture.parent / f"{cli_capture.stem}.validation-failures.jsonl").exists() is False, (
                "P1-Hybrid: Fake-CLI meldet Inputvalidierungsfehler"
            )

            state_before_stop = h02journey._authority_state_snapshot(run_dir, states_dir, schema_path)
            p1_table_before = json.loads((run_dir / "tables" / f"{TABLE_ID}.json").read_text())
            ledger_before_stop = _ledger_records_snapshot(run_dir)
            sup.write_json(case / "state-1-before-stop.json", state_before_stop)

            stop1_args = ["stop", "--data-dir", str(root), "--reason", "H05-P1-hybrid-gm-stop"]
            stop2_args = ["stop", "--data-dir", str(root), "--reason", "H05-P1-hybrid-gm-stop-repeat"]
            p_stop1 = h02journey._run_lab(stop1_args, tmp_root=root / "kidtmp_stop1", guard_dir=guard_dir)
            h02journey._log_invocation(case, "stop_1", stop1_args, {}, p_stop1)
            assert p_stop1.returncode == 0, p_stop1.stderr
            p_stop2 = h02journey._run_lab(stop2_args, tmp_root=root / "kidtmp_stop2", guard_dir=guard_dir)
            h02journey._log_invocation(case, "stop_2", stop2_args, {}, p_stop2)
            assert p_stop2.returncode == 0, p_stop2.stderr

            state_barrier_held = h02journey._authority_state_snapshot(run_dir, states_dir, schema_path)
            sup.write_json(case / "state-2-barrier-held.json", state_barrier_held)
            assert state_barrier_held["lab_stop_file_exists"] is True
            assert state_barrier_held["turns_used"] == state_before_stop["turns_used"]
            assert state_barrier_held["currents"] == state_before_stop["currents"]
            assert state_barrier_held["reflections_count"] == 0
            _assert_protected_unchanged(
                state_before_stop, state_barrier_held, context="P1-Hybrid barrier-held vs before-stop",
            )

            release_event.set()
            out, err, timed_out = _finish_controller(proc)
            _log_controller_invocation(case, "controller_start", proc, out, err, timeout=20, timed_out=timed_out)
        finally:
            h05sup.stop_http_server(gm_srv, gm_thread)

        assert proc.returncode == 0, out + err
        assert "Lobby-Tisch abgeschlossen" not in out, out
        state_after_release = h02journey._authority_state_snapshot(run_dir, states_dir, schema_path)
        ledger_after_release = _ledger_records_snapshot(run_dir)
        sup.write_json(case / "state-3-after-release.json", state_after_release)
        _assert_protected_unchanged(
            state_before_stop, state_after_release, except_keys=frozenset({"tables"}),
            context="P1-Hybrid after-release vs before-stop",
        )

        accounted_before = [r for r in ledger_before_stop if r.get("state") == "accounted"]
        accounted_after = [r for r in ledger_after_release if r.get("state") == "accounted"]
        assert len(ledger_after_release) == len(ledger_before_stop), (
            f"P1-Hybrid: kein Folgerequest erwartet: vorher={len(ledger_before_stop)} nachher={len(ledger_after_release)}"
        )
        assert len(accounted_before) == len(ledger_before_stop) - 1
        assert len(accounted_after) == len(ledger_after_release)
        assert state_after_release["reflections_count"] == 0
        table = core_store.Table.load(run_dir, TABLE_ID)
        _assert_gm_append(p1_table_before, json.loads((run_dir / "tables" / f"{TABLE_ID}.json").read_text()), gm_receipts[2])
        assert table.status == "active", f"P1-Hybrid: Tisch/Abschnitt muessen offen bleiben: {table.status}"
        assert len(table.sl_log) == 3, f"P1-Hybrid: G0,G1,G2 erwartet: {len(table.sl_log)}"
        assert state_after_release["currents"] == state_before_stop["currents"]
        assert gm_receipts[2]["egress_sent_monotonic"] > gm_receipts[2]["received_monotonic"]
        sup.write_json(case / "gm-independent-receipts.json", gm_receipts)

        sup.write_json(case / "result.json", {
            "status": "PASS", "controller_returncode": proc.returncode,
            "table_status": table.status, "sl_log_len": len(table.sl_log),
        })


# ---------------------------------------------------------------------------
# P2 -- Reflexions-Stop (API): echte vollstaendige G4-Antwort, natuerliche
# Phase-1-Ernte, Barriere an der ERSTEN von zwei Pflichtreflexionen (sniper,
# seq[8]) -- danach nur diese eine Antwort freigeben.
# ---------------------------------------------------------------------------

def test_p2_reflection_stop_api():
    case = sup.case_dir("P2_reflection_stop_api")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        community_participant_id = "h05p2api"
        schema_path, states_dir, run_dir, onboarding_dir, guard_dir, offer_id, human_pid = _bootstrap_table_prereqs(
            root, community_participant_id,
        )
        sup.write_json(case / "human-participant.json", {"human_participant_id": human_pid})
        seq = h02journey._persona_response_sequence_for_full_journey(offer_id)
        gm_texts = h02journey._gm_response_texts(TABLE_ID, SECTION_ID)
        persona_validators_full = h02journey._persona_validators_for_full_journey(offer_id, TABLE_ID, SECTION_ID)
        gm_validators_full = h02journey._gm_validators_for_full_journey(seq)

        gm_receipts_path = case / "gm-receipts.jsonl"
        persona_validators = {0: sup.make_persona_input_validator("sniper", None, expected_current=sup.load_fixture_save("sniper"))}
        for i in range(8):
            persona_validators[i + 1] = persona_validators_full[i]
        persona_validators[9] = persona_validators_full[8]  # sniper Reflexion (die blockierte, freigegebene Antwort)

        PersonaHandler, block_event, release_event, persona_receipts, persona_validation_failures = h05sup.make_stalling_handler(
            pre_block_bodies=(
                [{"choices": [{"message": {"content": h02journey._leader_nomination_proposal()}}]}]
                + [{"choices": [{"message": {"content": seq[i]}}], "usage": {}} for i in range(8)]
            ),
            block_response_body={"choices": [{"message": {"content": seq[8]}}], "usage": {}},
            validators=persona_validators, wait_timeout=30.0, label="p2-persona-api",
        journal_path=case / 'p2-persona-api-wire-events.jsonl', )
        persona_srv, persona_thread, persona_base_url = h05sup.start_http_server(PersonaHandler)
        proc = None
        try:
            with sup.recording_http_server(
                [(200, {"choices": [{"message": {"content": t}}], "usage": {}}) for t in gm_texts],
                receipts_path=gm_receipts_path, label="p2-gm-api",
                validators=gm_validators_full,
            ) as gm_srv:
                env = _controller_env(
                    tmp_root=root / "kidtmp_controller", guard_dir=guard_dir,
                    extra={
                        "MMO_SIM_PERSONA_API_BASE_URL": persona_base_url,
                        "MMO_SIM_PERSONA_API_KEY": "SYNTH-H05-NOT-A-REAL-KEY",
                        "MMO_SIM_PERSONA_API_MODEL": "synthetic-h05-persona",
                        "OPENWEBUI_URL": gm_srv.base_url, "OPENWEBUI_API_KEY": "SYNTH-H05-NOT-A-REAL-KEY",
                        "MMO_SIM_GM_OUTPUT_LIMIT_TOKENS": "4096",
                        "MMO_SIM_LOBBY_INITIATIVE_LIMIT": "8",
                    },
                )
                start_args = _standard_start_args(root, community_participant_id, "api")
                proc = _start_controller(start_args, env=env)

                assert block_event.wait(timeout=30), "sniper-Reflexion haette real am Handler ankommen muessen"
                assert persona_validation_failures == [], f"P2: Persona-Empfaenger meldet Inputvalidierungsfehler: {persona_validation_failures}"
                assert gm_srv.validation_failures == [], f"P2: GM-Empfaenger meldet Inputvalidierungsfehler: {gm_srv.validation_failures}"
                assert len(gm_srv.received) == 5, f"P2: G0-G4 = 5 echte GM-Requests vor der Reflexionsbarriere erwartet: {len(gm_srv.received)}"

                state_before_stop = h02journey._authority_state_snapshot(run_dir, states_dir, schema_path)
                ledger_before_stop = _ledger_records_snapshot(run_dir)
                sup.write_json(case / "state-1-before-stop.json", state_before_stop)
                sup.write_json(case / "ledger-1-before-stop.json", ledger_before_stop)
                # Natuerliche Phase-1-Ernte bereits erfolgt: neue Currents mit
                # unterscheidbarem G4-Endmarker, Tisch noch NICHT geschlossen.
                for pk in ("sniper", "tech"):
                    assert state_before_stop["currents"][pk].get("_h02_end_marker") == f"H02-VOLLREISE-ENDSAVE-{pk}-{TABLE_ID}-{SECTION_ID}", (
                        f"P2: Phase-1-Ernte haette den Current von {pk} bereits vor der Reflexionsbarriere publiziert haben muessen: "
                        f"{state_before_stop['currents'][pk]}"
                    )
                assert state_before_stop["tables"][f"{TABLE_ID}.json"]["status"] == "active"
                assert state_before_stop["reflections_count"] == 0

                stop1_args = ["stop", "--data-dir", str(root), "--reason", "H05-P2-reflection-stop"]
                stop2_args = ["stop", "--data-dir", str(root), "--reason", "H05-P2-reflection-stop-repeat"]
                p_stop1 = h02journey._run_lab(stop1_args, tmp_root=root / "kidtmp_stop1", guard_dir=guard_dir)
                h02journey._log_invocation(case, "stop_1", stop1_args, {}, p_stop1)
                assert p_stop1.returncode == 0, p_stop1.stderr
                p_stop2 = h02journey._run_lab(stop2_args, tmp_root=root / "kidtmp_stop2", guard_dir=guard_dir)
                h02journey._log_invocation(case, "stop_2", stop2_args, {}, p_stop2)
                assert p_stop2.returncode == 0, p_stop2.stderr

                state_barrier_held = h02journey._authority_state_snapshot(run_dir, states_dir, schema_path)
                sup.write_json(case / "state-2-barrier-held.json", state_barrier_held)
                assert state_barrier_held["lab_stop_file_exists"] is True
                assert state_barrier_held["reflections_count"] == 0, "P2: waehrend gehaltener Barriere noch KEINE Reflexion committet"
                assert state_barrier_held["currents"] == state_before_stop["currents"], "P2: Phase-1-Ernte darf durch Stop nicht zurueckgenommen werden"
                assert state_barrier_held["tables"][f"{TABLE_ID}.json"]["status"] == "active"
                _assert_protected_unchanged(
                    state_before_stop, state_barrier_held, context="P2-API barrier-held vs before-stop",
                )

                release_event.set()
                out, err, timed_out = _finish_controller(proc)
                _log_controller_invocation(case, "controller_start", proc, out, err, timeout=20, timed_out=timed_out)
        finally:
            h05sup.stop_http_server(persona_srv, persona_thread)

        assert proc.returncode == 0, out + err
        assert "Lobby-Tisch abgeschlossen" not in out, out
        state_after_release = h02journey._authority_state_snapshot(run_dir, states_dir, schema_path)
        ledger_after_release = _ledger_records_snapshot(run_dir)
        sup.write_json(case / "state-3-after-release.json", state_after_release)
        sup.write_json(case / "ledger-3-after-release.json", ledger_after_release)
        _assert_protected_unchanged(
            state_before_stop, state_after_release, except_keys=frozenset({"persona_states", "reflections.jsonl"}),
            context="P2-API after-release vs before-stop",
        )

        # Erlaubt: genau die eine sniper-Reflexion + ihr Ledgerabschluss. Das
        # Archiv (`reflections.jsonl`) traegt zusaetzlich ehrliche
        # `pending_recovery`-Eintraege fuer tech (dessen Reflexion NIE einen
        # Request erreichte -- das Admission-Gate blockierte sie bereits VOR
        # jedem Transportaufruf, s. `runtime.py:_admitted_decision`) und fuer
        # den abschliessenden Gate-Check -- das ist der bereits im
        # Produktcode vorgesehene, ehrliche "offener Zustand statt
        # Verschlucken"-Pfad (`_collect_reflections`-Docstring), kein H05-Befund.
        required_entries = [r for r in state_after_release["reflections"] if r.get("kind") == "ai_required_reflection"]
        pending_recovery_entries = [r for r in state_after_release["reflections"] if r.get("status") == "pending_recovery"]
        assert len(required_entries) == 1, (
            f"P2: genau EINE erhaltene/committete Reflexion erwartet (sniper), kein zweiter Persona-/GM-Request: "
            f"{state_after_release['reflections']}"
        )
        assert required_entries[0]["persona_key"] == "sniper"
        assert required_entries[0]["text"] == seq[8]
        assert len(pending_recovery_entries) >= 1 and all(
            "H05-P2-reflection-stop" in (e.get("error") or "") for e in pending_recovery_entries
        ), (
            f"P2: verbleibende offene Reflexion(en)/Gate-Check muessen ehrlich als pending_recovery mit dem "
            f"wahren Stopgrund archiviert sein, keine Erfindung/Verschlucken: {pending_recovery_entries}"
        )
        assert state_after_release["persona_states"]["sniper"].get("last_reflection") == seq[8], (
            "P2: die erhaltene sniper-Reflexion muss lokal im Persona-State stehen"
        )
        assert "last_reflection" not in state_after_release["persona_states"]["tech"] or \
            state_after_release["persona_states"]["tech"].get("last_reflection") != seq[9], (
            "P2: tech darf NICHT reflektiert haben (zweite Pflichtreflexion muss ausbleiben)"
        )
        # Verboten: keine finale Schliessung/Lockfreigabe/zweite Runde.
        table = core_store.Table.load(run_dir, TABLE_ID)
        assert table.status == "active", f"P2: Tisch darf NICHT final geschlossen sein: {table.status}"
        locks = core_store._read_locks(run_dir)
        assert locks != {}, "P2: Locks duerfen bei ausstehender zweiter Pflichtreflexion NICHT geloest sein"
        assert not core_store._completion_final_path(run_dir, SECTION_ID).exists(), (
            "P2: kein __final-Marker (echter Storepfad completion/{section_id}__final.json) trotz Stop "
            "waehrend Reflexion erlaubt"
        )
        assert len(gm_srv.received) == 5, "P2: kein zusaetzlicher GM-Request nach der Reflexionsbarriere"
        accounted_before = [r for r in ledger_before_stop if r.get("state") == "accounted"]
        accounted_after = [r for r in ledger_after_release if r.get("state") == "accounted"]
        assert len(ledger_after_release) == len(ledger_before_stop), (
            f"P2: kein Folgerequest (auch keine zweite Reflexion) erwartet: vorher={len(ledger_before_stop)} "
            f"nachher={len(ledger_after_release)}"
        )
        assert len(accounted_before) == len(ledger_before_stop) - 1
        assert len(accounted_after) == len(ledger_after_release)
        assert persona_receipts[9]["egress_sent_monotonic"] > persona_receipts[9]["received_monotonic"], (
            "P2: Ausgang der sniper-Reflexion muss zeitlich NACH ihrem Empfang liegen"
        )
        sup.write_json(case / "persona-independent-receipts.json", persona_receipts)
        sup.write_json(case / "result.json", {
            "status": "PASS", "controller_returncode": proc.returncode,
            "reflections_count": state_after_release["reflections_count"], "table_status": table.status,
        })


# ---------------------------------------------------------------------------
# P2 -- Reflexions-Stop (Hybrid-Fake-CLI+API-SL): identische Semantik wie
# P2-API, Persona-/Reflexionstransport ueber eine eigene blockierende
# Fake-CLI (Prozessgrenze -- dateibasierte Freigabe statt `threading.Event`).
# ---------------------------------------------------------------------------

_SL_LOG_LEN_BY_SEQ_IDX_FULL = {0: None}
for _offset, _length in enumerate(h02journey._TABLE_DECISION_PREFIX_LENGTHS):
    _SL_LOG_LEN_BY_SEQ_IDX_FULL[_offset + 1] = _length


def test_p2_reflection_stop_hybrid():
    case = sup.case_dir("P2_reflection_stop_hybrid")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        community_participant_id = "h05p2hybrid"
        schema_path, states_dir, run_dir, onboarding_dir, guard_dir, offer_id, human_pid = _bootstrap_table_prereqs(
            root, community_participant_id,
        )
        sup.write_json(case / "human-participant.json", {"human_participant_id": human_pid})
        seq = h02journey._persona_response_sequence_for_full_journey(offer_id)
        gm_texts = h02journey._gm_response_texts(TABLE_ID, SECTION_ID)
        gm_validators_full = h02journey._gm_validators_for_full_journey(seq)

        cli_capture = case / "cli-receipts.jsonl"
        queue = [{
            "result": h02journey._leader_nomination_proposal(),
            "expect_phase_marker": "begrenztes eigenes Lobby-Initiativfenster",
            "expect_all": [sup.own_figure_marker("sniper"), sup.own_current_full_marker(sup.load_fixture_save("sniper"))],
        }]
        for i in range(9):  # seq[0..8]: consent,G0,G1,G2,poll,G3,poll,G4,sniper-Reflexion
            pk = h02journey._SEQ_PK[i]
            expect_all = [sup.own_figure_marker(pk), sup.own_current_full_marker(sup.load_fixture_save(pk))]
            if i == 0:
                expect_all = expect_all + [f"offer_id={offer_id}"]
            queue.append({
                "result": seq[i], "expect_all": expect_all,
                "expect_sl_log_len": (None if i == 0 else h02journey._TABLE_DECISION_PREFIX_LENGTHS[i - 1]),
                "expect_table_id": TABLE_ID,
                "expect_gm_journal": str(case / "gm-receipts.jsonl"),
                "expect_phase_marker": (
                    "schlaegt eine gemeinsame Runde" if i == 0 else
                    "Private Reflexion" if i == 8 else
                    "Du fuehrst diesen Tisch als Leader." if pk == "tech" else "Ich trete dem Tisch bei."
                ),
            })
        fake_cli, block_marker_path, release_marker_path, cli_egress_path = h05sup.write_stalling_fake_cli(
            root, capture_path=cli_capture, queue=queue, block_at_index=9, wait_timeout=30.0,
        )
        isolated_workdir = root / "cli_workdir"
        isolated_workdir.mkdir(parents=True, exist_ok=True)

        gm_receipts_path = case / "gm-receipts.jsonl"
        proc = None
        try:
            with sup.recording_http_server(
                [(200, {"choices": [{"message": {"content": t}}], "usage": {}}) for t in gm_texts],
                receipts_path=gm_receipts_path, label="p2-gm-hybrid", validators=gm_validators_full,
            ) as gm_srv:
                env = _controller_env(
                    tmp_root=root / "kidtmp_controller", guard_dir=guard_dir,
                    extra={
                        "OPENWEBUI_URL": gm_srv.base_url, "OPENWEBUI_API_KEY": "SYNTH-H05-NOT-A-REAL-KEY",
                        "MMO_SIM_GM_OUTPUT_LIMIT_TOKENS": "4096",
                        "MMO_SIM_LOBBY_INITIATIVE_LIMIT": "8",
                        "MMO_SIM_PERSONA_CLI": str(fake_cli),
                        "MMO_SIM_PERSONA_ISOLATED_WORKDIR": str(isolated_workdir),
                        "MMO_SIM_PERSONA_ISOLATION_FLAGS": "--permission-mode=plan,--safe-mode",
                    },
                )
                start_args = _standard_start_args(root, community_participant_id, "hybrid")
                proc = _start_controller(start_args, env=env)

                assert h05sup.wait_for_marker(block_marker_path, timeout=30), (
                    "P2-Hybrid: sniper-Reflexion haette die blockierende Fake-CLI real erreichen muessen"
                )
                assert not (case / "cli-receipts.validation-failures.jsonl").exists() and not (
                    root / f"{cli_capture.stem}.validation-failures.jsonl"
                ).exists(), "P2-Hybrid: Fake-CLI meldet Inputvalidierungsfehler"
                assert gm_srv.validation_failures == [], f"P2-Hybrid: GM-Empfaenger meldet Inputvalidierungsfehler: {gm_srv.validation_failures}"
                assert len(gm_srv.received) == 5, f"P2-Hybrid: G0-G4 = 5 echte GM-Requests erwartet: {len(gm_srv.received)}"

                state_before_stop = h02journey._authority_state_snapshot(run_dir, states_dir, schema_path)
                ledger_before_stop = _ledger_records_snapshot(run_dir)
                sup.write_json(case / "state-1-before-stop.json", state_before_stop)
                for pk in ("sniper", "tech"):
                    assert state_before_stop["currents"][pk].get("_h02_end_marker") == f"H02-VOLLREISE-ENDSAVE-{pk}-{TABLE_ID}-{SECTION_ID}"
                assert state_before_stop["tables"][f"{TABLE_ID}.json"]["status"] == "active"
                assert state_before_stop["reflections_count"] == 0

                stop1_args = ["stop", "--data-dir", str(root), "--reason", "H05-P2-hybrid-reflection-stop"]
                stop2_args = ["stop", "--data-dir", str(root), "--reason", "H05-P2-hybrid-reflection-stop-repeat"]
                p_stop1 = h02journey._run_lab(stop1_args, tmp_root=root / "kidtmp_stop1", guard_dir=guard_dir)
                h02journey._log_invocation(case, "stop_1", stop1_args, {}, p_stop1)
                assert p_stop1.returncode == 0, p_stop1.stderr
                p_stop2 = h02journey._run_lab(stop2_args, tmp_root=root / "kidtmp_stop2", guard_dir=guard_dir)
                h02journey._log_invocation(case, "stop_2", stop2_args, {}, p_stop2)
                assert p_stop2.returncode == 0, p_stop2.stderr

                state_barrier_held = h02journey._authority_state_snapshot(run_dir, states_dir, schema_path)
                sup.write_json(case / "state-2-barrier-held.json", state_barrier_held)
                assert state_barrier_held["lab_stop_file_exists"] is True
                assert state_barrier_held["reflections_count"] == 0
                assert state_barrier_held["currents"] == state_before_stop["currents"]
                assert state_barrier_held["tables"][f"{TABLE_ID}.json"]["status"] == "active"
                _assert_protected_unchanged(
                    state_before_stop, state_barrier_held, context="P2-Hybrid barrier-held vs before-stop",
                )

                h05sup.release_marker(release_marker_path)
                out, err, timed_out = _finish_controller(proc)
                _log_controller_invocation(case, "controller_start", proc, out, err, timeout=20, timed_out=timed_out)
        finally:
            pass

        assert proc.returncode == 0, out + err
        assert "Lobby-Tisch abgeschlossen" not in out, out
        state_after_release = h02journey._authority_state_snapshot(run_dir, states_dir, schema_path)
        ledger_after_release = _ledger_records_snapshot(run_dir)
        sup.write_json(case / "state-3-after-release.json", state_after_release)
        _assert_protected_unchanged(
            state_before_stop, state_after_release, except_keys=frozenset({"persona_states", "reflections.jsonl"}),
            context="P2-Hybrid after-release vs before-stop",
        )

        required_entries = [r for r in state_after_release["reflections"] if r.get("kind") == "ai_required_reflection"]
        pending_recovery_entries = [r for r in state_after_release["reflections"] if r.get("status") == "pending_recovery"]
        assert len(required_entries) == 1, f"P2-Hybrid: genau EINE erhaltene Reflexion erwartet: {state_after_release['reflections']}"
        assert required_entries[0]["persona_key"] == "sniper"
        assert required_entries[0]["text"] == seq[8]
        assert len(pending_recovery_entries) >= 1 and all(
            "H05-P2-hybrid-reflection-stop" in (e.get("error") or "") for e in pending_recovery_entries
        ), pending_recovery_entries
        table = core_store.Table.load(run_dir, TABLE_ID)
        assert table.status == "active", f"P2-Hybrid: Tisch darf NICHT final geschlossen sein: {table.status}"
        locks = core_store._read_locks(run_dir)
        assert locks != {}, "P2-Hybrid: Locks duerfen NICHT geloest sein"
        assert not core_store._completion_final_path(run_dir, SECTION_ID).exists(), (
            "P2-Hybrid: kein __final-Marker (echter Storepfad) erlaubt"
        )
        assert len(gm_srv.received) == 5, "P2-Hybrid: kein zusaetzlicher GM-Request nach der Reflexionsbarriere"
        accounted_before = [r for r in ledger_before_stop if r.get("state") == "accounted"]
        accounted_after = [r for r in ledger_after_release if r.get("state") == "accounted"]
        assert len(ledger_after_release) == len(ledger_before_stop)
        assert len(accounted_before) == len(ledger_before_stop) - 1
        assert len(accounted_after) == len(ledger_after_release)

        cli_receipts = sup.read_jsonl(cli_capture)
        sup.write_json(case / "cli-independent-receipts.json", cli_receipts)
        assert len(cli_receipts) == 10, f"P2-Hybrid: genau 10 echte Fake-CLI-Aufrufe erwartet (Initiative+9 Sequenzitems): {len(cli_receipts)}"
        # N3: die vollstaendige EGRESS-Seite der blockierenden Fake-CLI (Hash/
        # Bytelaenge/Status/Zeit des tatsaechlich nach Freigabe emittierten
        # stdout) -- vorher NUR die Eingangsseite (`cli_receipts`) gesichert.
        cli_egress = sup.read_jsonl(cli_egress_path) if cli_egress_path.exists() else []
        sup.write_json(case / "cli-egress-receipts.json", cli_egress)
        assert len(cli_egress) == 10, (
            f"P2-Hybrid: genau 10 tatsaechlich emittierte Fake-CLI-Ausgaenge (Egress) erwartet, "
            f"symmetrisch zu den 10 Eingaengen: {len(cli_egress)}"
        )
        for idx, row in enumerate(cli_egress):
            raw = __import__("base64").b64decode(row["egress_stdout_b64"])
            assert row["egress_status"] == "exit_0_success" and row["write_state"] == "written"
            assert row["egress_stdout_sha256"] == __import__("hashlib").sha256(raw).hexdigest()
            assert row["egress_stdout_bytes_len"] == len(raw) and raw.endswith(b"\n")
            assert json.loads(raw)["result"] == ([h02journey._leader_nomination_proposal()] + seq[:9])[idx]
            assert row["egress_stderr_b64"] == ""
        assert cli_egress[-1]["release_observed_wall_ts"] >= json.loads(release_marker_path.read_text())["released_wall_ts"]
        sup.write_json(case / "result.json", {
            "status": "PASS", "controller_returncode": proc.returncode, "table_status": table.status,
        })


# ---------------------------------------------------------------------------
# P3 -- Observerende: ein eigener API-Controller haelt einen belegten
# in-flight-Request; zwei unabhaengige `lab attach --follow`-Prozesse --
# einer bekommt nach der ersten beobachteten Ausgabe stdin-EOF ueber eine
# eigene Pipe (NICHT `--max-updates`), der andere gezielt SIGINT. Jeder
# Observer beendet NUR sich selbst; der Controller bleibt derselbe lebende
# Owner, Stopmarker/Verbrauch/Autoritaeten unveraendert waehrend der
# Barriere; danach wird der Controller regulaer (Freigabe) beendet.
# ---------------------------------------------------------------------------

def test_p3_observer_end():
    case = sup.case_dir("P3_observer_end")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        community_participant_id = "h05p3api"
        schema_path, states_dir, run_dir, onboarding_dir, guard_dir, offer_id, human_pid = _bootstrap_table_prereqs(
            root, community_participant_id,
        )
        sup.write_json(case / "human-participant.json", {"human_participant_id": human_pid})
        PersonaHandler, block_event, release_event, persona_receipts, persona_validation_failures = h05sup.make_stalling_handler(
            pre_block_bodies=[],
            block_response_body={"choices": [{"message": {"content": '{"action": "pause"}'}}]},
            validators={0: sup.make_persona_input_validator("sniper", None, expected_current=sup.load_fixture_save("sniper"))},
            wait_timeout=60.0, label="p3-persona-api",
        journal_path=case / 'p3-persona-api-wire-events.jsonl', )
        persona_srv, persona_thread, persona_base_url = h05sup.start_http_server(PersonaHandler)
        observer_a = observer_b = proc = None
        out = err = ""
        try:
            env = _controller_env(
                tmp_root=root / "kidtmp_controller", guard_dir=guard_dir,
                extra={
                    "MMO_SIM_PERSONA_API_BASE_URL": persona_base_url,
                    "MMO_SIM_PERSONA_API_KEY": "SYNTH-H05-NOT-A-REAL-KEY",
                    "MMO_SIM_PERSONA_API_MODEL": "synthetic-h05-persona",
                    "MMO_SIM_LOBBY_INITIATIVE_LIMIT": "1",
                },
            )
            start_args = _standard_start_args(root, community_participant_id, "api")
            proc = _start_controller(start_args, env=env)
            controller_pid = proc.pid

            assert block_event.wait(timeout=20), "P3: die eine Initiative-Anfrage haette real am Handler ankommen muessen"
            assert persona_validation_failures == [], persona_validation_failures

            snapshot_before_observers = h02journey._authority_hash_snapshot(run_dir)
            # N1-Nachzug (01_REVIEW_H05.md N3-Kritik): `_authority_hash_snapshot`
            # deckt NUR `run_dir` ab, NICHT `states_dir` (Persona-States liegen
            # DORT) -- die vollstaendige `_authority_state_snapshot` (inkl.
            # `protected_authority_hashes["persona_states"]` = hash_tree ueber
            # den GESAMTEN `states_dir`, also auch alle Bystander/Human aus N2)
            # schliesst diese Luecke zusaetzlich.
            full_state_before_observers = h02journey._authority_state_snapshot(run_dir, states_dir, schema_path)
            status_before_observers = lab_runner.read_status(run_dir)
            assert status_before_observers is not None and status_before_observers.running is True
            assert status_before_observers.pid == controller_pid

            observer_env = sup.minimal_lab_env({}, tmp_root=root / "kidtmp_observer_eof", guard_dir=guard_dir)
            attach_args = ["attach", "--data-dir", str(root), "--follow", "--interval-seconds", "0.1"]

            # Observer A: eigene Pipe, EOF NACH der ersten beobachteten Ausgabe.
            observer_a = subprocess.Popen(
                [sys.executable, str(_MMO_SIM), "lab", *attach_args],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                env=observer_env, cwd=str(_REPO_ROOT),
            )
            first_line_a = observer_a.stdout.readline()
            assert first_line_a, "P3: Observer A haette mindestens eine Ausgabezeile liefern muessen, bevor EOF gesendet wird"
            observer_a.stdin.close()  # echtes stdin-EOF ueber die eigene Pipe -- kein --max-updates.
            try:
                observer_a_rc = observer_a.wait(timeout=8)
                observer_a_out = observer_a.stdout.read()
                observer_a_err = observer_a.stderr.read()
                observer_a_timed_out = False
            except subprocess.TimeoutExpired:
                observer_a_timed_out = True
                observer_a.kill()
                observer_a_rc = observer_a.wait(timeout=10)
                observer_a_out = observer_a.stdout.read()
                observer_a_err = observer_a.stderr.read()
            sup.append_jsonl(case / "invocations.json", {
                "name": "attach_observer_a_stdin_eof", "argv": attach_args, "pid": observer_a.pid,
                "returncode": observer_a_rc, "timed_out_and_killed": observer_a_timed_out,
            })
            (case / "stdout.attach_observer_a.txt").write_text(first_line_a + observer_a_out, encoding="utf-8")
            (case / "stderr.attach_observer_a.txt").write_text(observer_a_err, encoding="utf-8")

            # Observer B: eigener zweiter, unabhaengiger Prozess -- SIGINT statt
            # EOF. Eigene OFFENE Pipe (NICHT DEVNULL, NICHT geschlossen): seit
            # dem H05-P3-Fix oben reagiert `--follow` auf ein tatsaechliches
            # stdin-EOF (DEVNULL liest sofort als EOF) -- Observer B soll
            # gezielt NUR den SIGINT-Pfad pruefen, ohne durch ein zufaelliges
            # EOF ueberlagert zu werden (der Schreibende Zweitendpunkt der
            # Pipe bleibt im Testprozess bewusst offen).
            observer_b = subprocess.Popen(
                [sys.executable, str(_MMO_SIM), "lab", *attach_args],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                env=observer_env, cwd=str(_REPO_ROOT),
            )
            first_line_b = observer_b.stdout.readline()
            assert first_line_b, "P3: Observer B haette mindestens eine Ausgabezeile liefern muessen, bevor SIGINT gesendet wird"
            observer_b.send_signal(signal.SIGINT)
            _log_signal_event(case, "observer_b_sigint", pid=observer_b.pid, sig=signal.SIGINT, note="P3 Observerende")
            try:
                observer_b_rc = observer_b.wait(timeout=8)
                observer_b_out = observer_b.stdout.read()
                observer_b_err = observer_b.stderr.read()
                observer_b_timed_out = False
            except subprocess.TimeoutExpired:
                observer_b_timed_out = True
                observer_b.kill()
                observer_b_rc = observer_b.wait(timeout=10)
                observer_b_out = observer_b.stdout.read()
                observer_b_err = observer_b.stderr.read()
            sup.append_jsonl(case / "invocations.json", {
                "name": "attach_observer_b_sigint", "argv": attach_args, "pid": observer_b.pid,
                "returncode": observer_b_rc, "timed_out_and_killed": observer_b_timed_out,
            })
            (case / "stdout.attach_observer_b.txt").write_text(first_line_b + observer_b_out, encoding="utf-8")
            (case / "stderr.attach_observer_b.txt").write_text(observer_b_err, encoding="utf-8")

            # Controller bleibt waehrend BEIDER Observerenden derselbe lebende
            # Owner -- keine Autoritaetsmutation durch reines Beobachten.
            snapshot_after_observers = h02journey._authority_hash_snapshot(run_dir)
            full_state_after_observers = h02journey._authority_state_snapshot(run_dir, states_dir, schema_path)
            status_after_observers = lab_runner.read_status(run_dir)
            sup.write_json(case / "authority-hash-before-observers.json", snapshot_before_observers)
            sup.write_json(case / "authority-hash-after-observers.json", snapshot_after_observers)
            sup.write_json(case / "state-before-observers.json", full_state_before_observers)
            sup.write_json(case / "state-after-observers.json", full_state_after_observers)
            assert snapshot_after_observers == snapshot_before_observers, (
                "P3: passive Attach-Observer duerfen keine Autoritaetsbytes veraendern"
            )
            _assert_protected_unchanged(
                full_state_before_observers, full_state_after_observers,
                context="P3 nach beiden Observerenden vs vorher (inkl. states_dir/Bystander)",
            )
            assert status_after_observers is not None and status_after_observers.running is True and (
                status_after_observers.pid == controller_pid
            ), f"P3: Controller muss waehrend/nach beiden Observerenden derselbe lebende Owner bleiben: {status_after_observers}"
            assert proc.poll() is None, "P3: Controller-Prozess darf durch die Observer NICHT beendet worden sein"

            assert observer_a_timed_out is False and observer_a_rc == 0, (
                f"P3: Observer A (stdin-EOF) haette sich SELBST sauber beenden muessen (rc=0), ohne "
                f"--max-updates und ohne SIGINT -- tatsaechlich rc={observer_a_rc} "
                f"timed_out_and_killed={observer_a_timed_out}. Ausgabe: {observer_a_out!r} / {observer_a_err!r}"
            )
            assert observer_b_timed_out is False and observer_b_rc == 0, (
                f"P3: Observer B (SIGINT) rc={observer_b_rc} timed_out_and_killed={observer_b_timed_out}: "
                f"{observer_b_out!r} / {observer_b_err!r}"
            )
            assert "Ctrl-C" in observer_b_out, f"P3: Observer B haette die vorhandene Ctrl-C-Abschlussmeldung zeigen muessen: {observer_b_out!r}"
        finally:
            # Unbedingt zuerst den Controller regulaer beenden (Barriere
            # freigeben + kontrolliert warten/notfalls kill), BEVOR das
            # `tempfile.TemporaryDirectory`-Verzeichnis geraeumt wird -- sonst
            # kann ein bei einem fehlgeschlagenen Assert noch laufender
            # Controller mit dem Aufraeumen um dieselben Dateien konkurrieren
            # (kein fachlicher H05-Befund, reine Testhygiene).
            release_event.set()
            for p in (observer_a, observer_b):
                if p is not None and p.poll() is None:
                    p.kill()
                if p is not None and p.stdin is not None and not p.stdin.closed:
                    p.stdin.close()
            if proc is not None:
                out, err, timed_out = _finish_controller(proc)
                _log_controller_invocation(case, "controller_start", proc, out, err, timeout=20, timed_out=timed_out)
            h05sup.stop_http_server(persona_srv, persona_thread)

        assert proc.returncode == 0, out + err
        sup.write_json(case / "result.json", {
            "status": "PASS", "controller_returncode": proc.returncode,
            "observer_a_rc": observer_a_rc, "observer_b_rc": observer_b_rc,
        })


# ---------------------------------------------------------------------------
# P4 -- Controllersignale: API-Controller echtes SIGINT, Hybrid-Controller
# echtes SIGTERM, jeweils NACH unabhaengig bestaetigtem Versand (Barriere
# real erreicht) VOR Antwortausgabe. Tatsaechliche begrenzte Pause,
# wahrheitsgemaesser Grund/Verbrauch/offene IDs -- kein erfundener Erfolg.
# Nur die eigene Kind-PID (`proc.pid`) wird signalisiert.
# ---------------------------------------------------------------------------

def test_p4_controller_sigint_api():
    case = sup.case_dir("P4_controller_sigint_api")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        community_participant_id = "h05p4api"
        schema_path, states_dir, run_dir, onboarding_dir, guard_dir, offer_id, human_pid = _bootstrap_table_prereqs(
            root, community_participant_id,
        )
        sup.write_json(case / "human-participant.json", {"human_participant_id": human_pid})
        PersonaHandler, block_event, release_event, persona_receipts, persona_validation_failures = h05sup.make_stalling_handler(
            pre_block_bodies=[],
            block_response_body={"choices": [{"message": {"content": '{"action": "pause"}'}}]},
            validators={0: sup.make_persona_input_validator("sniper", None, expected_current=sup.load_fixture_save("sniper"))},
            wait_timeout=60.0, label="p4-persona-api",
        journal_path=case / 'p4-persona-api-wire-events.jsonl', )
        persona_srv, persona_thread, persona_base_url = h05sup.start_http_server(PersonaHandler)
        proc = None
        try:
            env = _controller_env(
                tmp_root=root / "kidtmp_controller", guard_dir=guard_dir,
                extra={
                    "MMO_SIM_PERSONA_API_BASE_URL": persona_base_url,
                    "MMO_SIM_PERSONA_API_KEY": "SYNTH-H05-NOT-A-REAL-KEY",
                    "MMO_SIM_PERSONA_API_MODEL": "synthetic-h05-persona",
                    "MMO_SIM_LOBBY_INITIATIVE_LIMIT": "1",
                },
            )
            start_args = _standard_start_args(root, community_participant_id, "api")
            proc = _start_controller(start_args, env=env)
            controller_pid = proc.pid

            assert block_event.wait(timeout=20), (
                "P4: unabhaengig bestaetigter Versand (echter Empfang am Handler) VOR Antwortausgabe erforderlich"
            )
            assert persona_validation_failures == []
            ledger_before_signal = _ledger_records_snapshot(run_dir)
            sent_before = [r for r in ledger_before_signal if r.get("state") == "sent"]
            assert len(sent_before) == 1, f"P4: genau EIN offener (state=sent) Requestdatensatz vor dem Signal erwartet: {ledger_before_signal}"
            state_before_signal = h02journey._authority_state_snapshot(run_dir, states_dir, schema_path)
            sup.write_json(case / "state-before-signal.json", state_before_signal)

            # Nur die eigene, bekannte Kind-PID -- kein pkill/killall. N3: das
            # Signal ist ein EIGENES belegtes Ereignis (vorher wurde `wall_ts_
            # signal_sent` berechnet und NIE gespeichert -- totes Zwischenergebnis).
            os.kill(controller_pid, signal.SIGINT)
            _log_signal_event(case, "p4_api_sigint", pid=controller_pid, sig=signal.SIGINT, note="P4 API-Controller")
            out, err, timed_out = _finish_controller(proc, timeout=20)
            _log_controller_invocation(case, "controller_start", proc, out, err, timeout=20, timed_out=timed_out)
        finally:
            h05sup.stop_http_server(persona_srv, persona_thread)

        assert timed_out is False, (
            f"P4: der Controller haette auf das echte SIGINT rechtzeitig selbst beenden muessen -- ein erzwungenes "
            f"Timeout-`kill()` ist KEIN fachlicher Erfolg: stdout={out!r} stderr={err!r}"
        )
        sup.write_json(case / "result-raw.json", {
            "controller_returncode": proc.returncode, "timed_out_and_killed": timed_out,
        })
        # Tatsaechliche begrenzte Pause: der bestehende KeyboardInterrupt-Pfad
        # (`_run_controller`, unveraendert) liefert exit_code=130 UND ruft
        # `lab.release()` im `finally` -- kein erfundener Erfolg, aber auch
        # kein unkontrollierter Absturz.
        assert proc.returncode == 130, f"P4: erwarteter KeyboardInterrupt-Exitcode 130 nach echtem SIGINT: {proc.returncode}; stderr={err}"
        assert "Lab pausiert (Ctrl-C/SIGTERM)" in out, out
        status_after = lab_runner.read_status(run_dir)
        assert status_after is not None and status_after.running is False, (
            f"P4: lab.release() haette running=False geschrieben haben muessen: {status_after}"
        )
        assert (run_dir / "lab.stop").exists(), "P4: SIGINT-Pfad ruft lab.stop() -- wahrheitsgemaesser Grund erforderlich"
        stop_payload = json.loads((run_dir / "lab.stop").read_text(encoding="utf-8"))
        assert "Ctrl-C" in stop_payload.get("reason", "") or "SIGTERM" in stop_payload.get("reason", ""), stop_payload
        assert not (run_dir / "lab.lock.json").exists(), "P4: SIGINT-Pfad loest den Lock im finally auf"

        # Antwort-/Ledgerzustand nach TATSAECHLICHEM Empfang, nicht aus
        # Sendeabsicht erfunden: die eine unterbrochene Anfrage bleibt
        # unbekannt/offen (state=sent), KEIN finish_received/finish_error
        # (KeyboardInterrupt ist kein `Exception`, `_admitted_decision`s
        # `except Exception` faengt es NICHT -- verifiziert am realen Lauf,
        # nicht nur am Code gelesen).
        ledger_after_signal = _ledger_records_snapshot(run_dir)
        assert len(ledger_after_signal) == len(ledger_before_signal), (
            f"P4: kein Folgerequest/keine Erfindung -- Gesamtzahl Requestdatensaetze unveraendert erwartet: "
            f"vorher={len(ledger_before_signal)} nachher={len(ledger_after_signal)}"
        )
        sent_after = [r for r in ledger_after_signal if r.get("state") == "sent"]
        assert len(sent_after) == 1 and sent_after[0]["id"] == sent_before[0]["id"], (
            f"P4: die unterbrochene Anfrage muss unbekannt/offen (state=sent) bleiben, IDENTISCHE id, kein Reset: "
            f"vorher={sent_before} nachher={sent_after}"
        )
        state_after_signal = h02journey._authority_state_snapshot(run_dir, states_dir, schema_path)
        sup.write_json(case / "state-after-signal.json", state_after_signal)
        _assert_protected_unchanged(
            state_before_signal, state_after_signal, context="P4-API after-SIGINT vs before-signal",
        )
        sup.write_json(case / "ledger-before-signal.json", ledger_before_signal)
        sup.write_json(case / "ledger-after-signal.json", ledger_after_signal)
        sup.write_json(case / "result.json", {
            "status": "PASS", "controller_returncode": proc.returncode,
            "stop_reason": stop_payload.get("reason"), "open_request_id": sent_after[0]["id"],
        })


def test_p4_controller_sigterm_hybrid():
    case = sup.case_dir("P4_controller_sigterm_hybrid")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        community_participant_id = "h05p4hybrid"
        schema_path, states_dir, run_dir, onboarding_dir, guard_dir, offer_id, human_pid = _bootstrap_table_prereqs(
            root, community_participant_id,
        )
        sup.write_json(case / "human-participant.json", {"human_participant_id": human_pid})
        cli_capture = case / "cli-receipts.jsonl"
        queue = [{
            "result": h02journey._leader_nomination_proposal(),
            "expect_all": [sup.own_figure_marker("sniper"), sup.own_current_full_marker(sup.load_fixture_save("sniper"))],
        }]
        fake_cli, block_marker_path, release_marker_path, cli_egress_path = h05sup.write_stalling_fake_cli(
            root, capture_path=cli_capture, queue=queue, block_at_index=0, wait_timeout=60.0,
        )
        isolated_workdir = root / "cli_workdir"
        isolated_workdir.mkdir(parents=True, exist_ok=True)
        fake_cli_child_pid_path = root / "fake_cli_pid.json"
        proc = None
        try:
            # N2-Nachzug (01_REVIEW_H05.md N2-Kritik): `require_schema_
            # dependency=False` war hier ausdruecklich fuer den ECHTEN
            # Hybrid-Lab-Controller-Kindprozess gesetzt -- die Fake-CLI-
            # Ausnahme ("Fake-CLI braucht kein jsonschema") gilt NICHT fuer
            # deren Lab-Controller. Jetzt Default (True, wie alle anderen 7
            # Faelle): jsonschema-Sichtbarkeit wird im echten Controller-Kind
            # erzwungen, eine fehlende Dependency blockiert VOR Fachstart.
            env = _controller_env(
                tmp_root=root / "kidtmp_controller", guard_dir=guard_dir,
                extra={
                    "MMO_SIM_LOBBY_INITIATIVE_LIMIT": "1",
                    "MMO_SIM_PERSONA_CLI": str(fake_cli),
                    "MMO_SIM_PERSONA_ISOLATED_WORKDIR": str(isolated_workdir),
                    "MMO_SIM_PERSONA_ISOLATION_FLAGS": "--permission-mode=plan,--safe-mode",
                },
            )
            start_args = _standard_start_args(root, community_participant_id, "hybrid")
            proc = _start_controller(start_args, env=env)
            controller_pid = proc.pid

            assert h05sup.wait_for_marker(block_marker_path, timeout=20), (
                "P4-Hybrid: unabhaengig bestaetigter Versand (Fake-CLI real erreicht) VOR Antwortausgabe erforderlich"
            )
            block_marker = json.loads(block_marker_path.read_text(encoding="utf-8"))
            fake_cli_pid = block_marker["pid"]
            ledger_before_signal = _ledger_records_snapshot(run_dir)
            state_before_signal = h02journey._authority_state_snapshot(run_dir, states_dir, schema_path)
            sup.write_json(case / "state-before-signal.json", state_before_signal)

            # Nur die eigene, bekannte Kind-PID des Controllers -- kein
            # pkill/killall. Der Fake-CLI-Kindprozess (fake_cli_pid, eine
            # separate, ebenfalls bekannte eigene PID) wird NICHT signalisiert
            # -- er wird beim regulaeren Timeout seiner eigenen Wartelogik
            # oder spaetestens beim Testcleanup beendet (kein Zombie-Leck).
            os.kill(controller_pid, signal.SIGTERM)
            _log_signal_event(case, "p4_hybrid_sigterm", pid=controller_pid, sig=signal.SIGTERM, note="P4 Hybrid-Controller")
            out, err, timed_out = _finish_controller(proc, timeout=20)
            _log_controller_invocation(case, "controller_start", proc, out, err, timeout=20, timed_out=timed_out)
        finally:
            h05sup.release_marker(release_marker_path)
            try:
                block_marker = json.loads(block_marker_path.read_text(encoding="utf-8")) if block_marker_path.exists() else None
                if block_marker is not None:
                    try:
                        os.kill(block_marker["pid"], signal.SIGTERM)
                    except ProcessLookupError:
                        pass
            except Exception:
                pass

        assert timed_out is False, (
            f"P4-Hybrid: der Controller haette auf das echte SIGTERM rechtzeitig selbst beenden muessen -- ein "
            f"erzwungenes Timeout-`kill()` ist KEIN fachlicher Erfolg: stdout={out!r} stderr={err!r}"
        )
        sup.write_json(case / "result-raw.json", {
            "controller_returncode": proc.returncode, "timed_out_and_killed": timed_out,
        })
        # H05-Repro (VOR jedem Produktwrite dokumentiert, s. WORKER-REPORT.md):
        # `_run_controller` installierte KEINEN echten SIGTERM-Handler (nur
        # `except KeyboardInterrupt`) -- ein reales SIGTERM toetete den
        # Controller mit Pythons Default-Aktion (`finally: lab.release()`
        # laeuft NICHT), `lab.status.json.running` blieb stale `True`, kein
        # wahrheitsgemaesser Stopgrund. Nach dem minimalen Fix (lokaler
        # SIGTERM-Handler, der `KeyboardInterrupt` erhebt, mit Wieder-
        # herstellung im `finally`) verhaelt sich SIGTERM symmetrisch zu
        # SIGINT: exit_code=130, `lab.release()` laeuft, wahrheitsgemaesser
        # Grund in `lab.stop`.
        assert proc.returncode == 130, (
            f"P4-Hybrid: erwarteter KeyboardInterrupt-Exitcode 130 nach echtem SIGTERM (symmetrisch zu SIGINT): "
            f"{proc.returncode}; stdout={out!r} stderr={err!r}"
        )
        status_after = lab_runner.read_status(run_dir)
        assert status_after is not None and status_after.running is False, (
            f"P4-Hybrid: lab.release() haette running=False geschrieben haben muessen (echte begrenzte Pause, "
            f"kein stiller Absturz mit stale running=True): {status_after}"
        )
        assert (run_dir / "lab.stop").exists()
        stop_payload = json.loads((run_dir / "lab.stop").read_text(encoding="utf-8"))
        assert not (run_dir / "lab.lock.json").exists(), "P4-Hybrid: SIGTERM-Pfad muss den Lock im finally auflosen"

        ledger_after_signal = _ledger_records_snapshot(run_dir)
        assert len(ledger_after_signal) == len(ledger_before_signal)
        sent_after = [r for r in ledger_after_signal if r.get("state") == "sent"]
        assert len(sent_after) == 1, (
            f"P4-Hybrid: die unterbrochene Fake-CLI-Anfrage muss unbekannt/offen (state=sent) bleiben, kein "
            f"erfundenes finish_received/finish_error: {ledger_after_signal}"
        )
        state_after_signal = h02journey._authority_state_snapshot(run_dir, states_dir, schema_path)
        sup.write_json(case / "state-after-signal.json", state_after_signal)
        _assert_protected_unchanged(
            state_before_signal, state_after_signal, context="P4-Hybrid after-SIGTERM vs before-signal",
        )
        sup.write_json(case / "ledger-before-signal.json", ledger_before_signal)
        sup.write_json(case / "ledger-after-signal.json", ledger_after_signal)
        # N3-Beleg (kein strikter Assert -- Race zwischen `release_marker`
        # und dem direkt anschliessenden SIGTERM auf die Fake-CLI-PID ist
        # gewollt knapp, s. `finally` oben; die fachliche Garantie "kein
        # stiller Erfolg" liefert bereits die obige Ledger-`sent_after`-
        # Assertion, unabhaengig vom Fake-CLI-Egress): der Controller starb
        # per SIGTERM VOR jeder Antwortverarbeitung -- ob die separate
        # Fake-CLI-PID ihrerseits noch einen (dann von niemandem mehr
        # gelesenen) Egress-Eintrag schreiben konnte, wird nur dokumentiert.
        cli_egress = sup.read_jsonl(cli_egress_path) if cli_egress_path.exists() else []
        sup.write_json(case / "cli-egress-receipts.json", cli_egress)
        sup.write_json(case / "result.json", {
            "status": "PASS", "controller_returncode": proc.returncode, "stop_reason": stop_payload.get("reason"),
        })


# ---------------------------------------------------------------------------
# P5 -- harte Unterbrechung: eigener API-Controller, Request am Empfaenger
# bestaetigt, Antwort ZURUECKGEHALTEN (nie freigegeben), gezieltes SIGKILL
# nur auf diese bekannte PID. Danach neuer expliziter `lab resume`-Prozess
# derselben synthetischen Ablage. Die nicht empfangene Antwort bleibt
# unbekannt/offen; kein automatischer zweiter Versand derselben Operation,
# kein Budget-/ID-/Save-Reset, keine erfundene Antwort. Vorhandener,
# eindeutig sicherer Hold: `request_ledger.begin()` lehnt eine zweite
# Reservierung fuer DIESELBE Operationsidentitaet (table_id/section_id/
# role/turn_idx/participant) ab (`OpenReservationExistsError`,
# `request_ledger.py:560-613`); `SectionRuntime._collect_reflections`
# (`runtime.py:315-336`) faengt das bereits vorhandene, geprueft ab (`ok=
# False`, `pending_recovery`-Archiveintrag) -- kein neuer Produktcode.
# ---------------------------------------------------------------------------

def test_p5_hard_interrupt_resume():
    case = sup.case_dir("P5_hard_interrupt_resume")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        community_participant_id = "h05p5api"
        schema_path, states_dir, run_dir, onboarding_dir, guard_dir, offer_id, human_pid = _bootstrap_table_prereqs(
            root, community_participant_id,
        )
        sup.write_json(case / "human-participant.json", {"human_participant_id": human_pid})
        seq = h02journey._persona_response_sequence_for_full_journey(offer_id)
        gm_texts = h02journey._gm_response_texts(TABLE_ID, SECTION_ID)
        persona_validators_full = h02journey._persona_validators_for_full_journey(offer_id, TABLE_ID, SECTION_ID)
        gm_validators_full = h02journey._gm_validators_for_full_journey(seq)

        persona_validators = {0: sup.make_persona_input_validator("sniper", None, expected_current=sup.load_fixture_save("sniper"))}
        for i in range(8):
            persona_validators[i + 1] = persona_validators_full[i]
        persona_validators[9] = persona_validators_full[8]

        # Die Antwort auf die sniper-Reflexion wird NIE freigegeben (P5:
        # "Antwort zurueckgehalten") -- `block_response_body` wird deshalb nie
        # ausgeliefert, `release_event` wird bewusst NIE gesetzt.
        PersonaHandler, block_event, _never_release_event, persona_receipts, persona_validation_failures = h05sup.make_stalling_handler(
            pre_block_bodies=(
                [{"choices": [{"message": {"content": h02journey._leader_nomination_proposal()}}]}]
                + [{"choices": [{"message": {"content": seq[i]}}], "usage": {}} for i in range(8)]
            ),
            block_response_body={"choices": [{"message": {"content": seq[8]}}], "usage": {}},
            # Kurzer `wait_timeout`: der Controller wird gleich per SIGKILL
            # beendet -- die Antwort bleibt fuer IHN unwiderruflich unbekannt/
            # offen (das ist der fachliche Beleg). Dieser Testempfaenger muss
            # aber selbst zeitnah aus `release_event.wait()` zurueckkehren,
            # sonst blockiert `HTTPServer.shutdown()` (wartet auf das Ende der
            # aktuell in `do_POST` laufenden Anfrage) im spaeteren Testcleanup
            # unnoetig lang -- kein fachlicher H05-Bezug, reine Testhygiene.
            validators=persona_validators, wait_timeout=10.0, label="p5-persona-api",
        journal_path=case / 'p5-persona-api-wire-events.jsonl', )
        persona_srv, persona_thread, persona_base_url = h05sup.start_http_server(PersonaHandler)
        gm_receipts_path = case / "gm-receipts.jsonl"
        proc = None
        try:
            with sup.recording_http_server(
                [(200, {"choices": [{"message": {"content": t}}], "usage": {}}) for t in gm_texts],
                receipts_path=gm_receipts_path, label="p5-gm-api", validators=gm_validators_full,
            ) as gm_srv:
                env = _controller_env(
                    tmp_root=root / "kidtmp_controller", guard_dir=guard_dir,
                    extra={
                        "MMO_SIM_PERSONA_API_BASE_URL": persona_base_url,
                        "MMO_SIM_PERSONA_API_KEY": "SYNTH-H05-NOT-A-REAL-KEY",
                        "MMO_SIM_PERSONA_API_MODEL": "synthetic-h05-persona",
                        "OPENWEBUI_URL": gm_srv.base_url, "OPENWEBUI_API_KEY": "SYNTH-H05-NOT-A-REAL-KEY",
                        "MMO_SIM_GM_OUTPUT_LIMIT_TOKENS": "4096",
                        "MMO_SIM_LOBBY_INITIATIVE_LIMIT": "8",
                    },
                )
                start_args = _standard_start_args(root, community_participant_id, "api")
                proc = _start_controller(start_args, env=env)
                controller_pid = proc.pid

                assert block_event.wait(timeout=30), "P5: sniper-Reflexion haette real am Handler ankommen (Request am Empfaenger bestaetigt) muessen"
                assert persona_validation_failures == []
                assert gm_srv.validation_failures == []
                assert len(gm_srv.received) == 5, "P5: echte vollstaendige G0-G4-Reise vor der Reflexionsbarriere erforderlich"

                ledger_before_kill = _ledger_records_snapshot(run_dir)
                sent_before = [r for r in ledger_before_kill if r.get("state") == "sent"]
                assert len(sent_before) == 1, f"P5: genau EIN offener (state=sent) Requestdatensatz (die sniper-Reflexion) vor SIGKILL erwartet: {ledger_before_kill}"
                stuck_identity = (
                    sent_before[0]["table_id"], sent_before[0]["section_id"], sent_before[0]["role"],
                    sent_before[0]["turn_idx"], sent_before[0]["participant"],
                )
                sup.write_json(case / "ledger-before-kill.json", ledger_before_kill)
                state_before_kill = h02journey._authority_state_snapshot(run_dir, states_dir, schema_path)
                sup.write_json(case / "state-before-kill.json", state_before_kill)

                # Gezieltes SIGKILL NUR auf diese eine bekannte, tatsaechlich
                # gestartete Kind-PID -- kein pkill/killall, kein echter Dienst.
                os.kill(controller_pid, signal.SIGKILL)
                _log_signal_event(case, "p5_sigkill", pid=controller_pid, sig=signal.SIGKILL, note="P5 harte Unterbrechung")
                controller_started_utc = getattr(proc, "_h05_started_utc", None)
                controller_argv = getattr(proc, "_h05_argv", None)
                controller_env_min = getattr(proc, "_h05_env_min", {})
                try:
                    kill_rc = proc.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    kill_rc = proc.wait(timeout=10)
                proc._h05_ended_utc = _utc_now_iso()  # type: ignore[attr-defined]
                # N3: SIGKILL ist nicht abfangbar -- `_finish_controller`
                # (das normale `communicate()`) ist hier NICHT nutzbar (kein
                # Timeout-Pfad noetig, `wait()` reicht). Trotzdem MUESSEN die
                # tatsaechlichen Pipe-Rohbytes VOR jedem Cleanup gesichert
                # werden (vorher: gar keine stdout/stderr-Sicherung fuer den
                # haertesten Abbruchfall) -- was der Kernel bis zum Kill
                # gepuffert hat, bleibt auf den Pipes lesbar.
                try:
                    controller_stdout = proc.stdout.read() or ""
                except Exception:
                    controller_stdout = ""
                try:
                    controller_stderr = proc.stderr.read() or ""
                except Exception:
                    controller_stderr = ""
                sup.append_jsonl(case / "invocations.json", {
                    "name": "controller_start", "argv": controller_argv, "cwd": str(_REPO_ROOT),
                    "pid": controller_pid, "interpreter": sys.executable, "env_min": controller_env_min,
                    "started_utc": controller_started_utc, "ended_utc": proc._h05_ended_utc,
                    "returncode": kill_rc, "timeout_seconds": 15, "timed_out_and_killed": False,
                })
                (case / "stdout.controller_start.txt").write_text(controller_stdout, encoding="utf-8")
                (case / "stderr.controller_start.txt").write_text(controller_stderr, encoding="utf-8")
        finally:
            h05sup.stop_http_server(persona_srv, persona_thread)

        assert kill_rc == -signal.SIGKILL, f"P5: Controller muss tatsaechlich per SIGKILL beendet worden sein: rc={kill_rc}"

        # Ehrlich beobachtete, eng begrenzte Unklarheit NACH SIGKILL (KEINE
        # Erfindung eines Erfolgs/einer Antwort): `lab.release()` konnte NICHT
        # laufen (SIGKILL ist nicht abfangbar) -- `running` bleibt stale
        # `True` im zuletzt geschriebenen Status, obwohl der Prozess tot ist.
        status_after_kill = lab_runner.read_status(run_dir)
        sup.write_json(case / "status-after-kill.json", {
            "running": status_after_kill.running if status_after_kill else None,
            "pid": status_after_kill.pid if status_after_kill else None,
            "turns_used": status_after_kill.turns_used if status_after_kill else None,
        })
        assert status_after_kill is not None and status_after_kill.running is True, (
            f"P5: der zuletzt geschriebene Status muss ehrlich stale 'running=True' zeigen (SIGKILL erlaubte keine "
            f"'lab.release()'), NICHT nachtraeglich als 'stopped' erfunden werden: {status_after_kill}"
        )
        ledger_after_kill = _ledger_records_snapshot(run_dir)
        assert ledger_after_kill == ledger_before_kill, (
            "P5: SIGKILL selbst darf am Requestledger NICHTS veraendert haben (kein finish_received/finish_error "
            "konnte laufen -- die Antwort bleibt unbekannt/offen, state=sent unveraendert)"
        )
        state_after_kill = h02journey._authority_state_snapshot(run_dir, states_dir, schema_path)
        sup.write_json(case / "state-after-kill.json", state_after_kill)
        _assert_protected_unchanged(
            state_before_kill, state_after_kill, context="P5 after-SIGKILL vs before-kill",
        )

        # Neuer expliziter `lab resume`-Prozess derselben synthetischen
        # Ablage. N3-Nachzug (01_REVIEW_H05.md N3-Kritik "nach Bind/Close
        # wieder freier Port statt nutzbarer eigener Empfaenger mit
        # Nullzaehler"): VORHER nur `free_loopback_port()` (Bind+Close,
        # garantiert NICHT lauschend) -- das beweist "kein Server da", aber
        # KEINEN Nullzaehler (es gibt schlicht niemanden, der zaehlen
        # koennte). Jetzt: ein ECHTER eigener Loopback-Empfaenger mit
        # Receipt-Liste (`h05sup.make_stalling_handler`, `pre_block_bodies=[]`
        # -- jeder eingehende Call wuerde blockieren/gezaehlt, es soll aber
        # gar keiner ankommen) fuer Persona UND GM; nach Resume wird ihr
        # jeweiliger Nullzaehler (`len(receipts) == 0`) als Beleg gesichert,
        # dann werden beide Empfaenger regulaer gestoppt.
        DeadPersonaHandler, _dp_block_event, _dp_release_event, dead_persona_receipts, _dp_validation_failures = (
            h05sup.make_stalling_handler(
                pre_block_bodies=[], block_response_body={"choices": [{"message": {"content": "H05-P5-UNEXPECTED"}}]},
                wait_timeout=1.0, label="p5-resume-deadcheck-persona",
            journal_path=case / 'p5-resume-deadcheck-persona-wire-events.jsonl', )
        )
        dead_persona_srv, dead_persona_thread, dead_persona_url = h05sup.start_http_server(DeadPersonaHandler)
        DeadGmHandler, _dg_block_event, _dg_release_event, dead_gm_receipts, _dg_validation_failures = (
            h05sup.make_stalling_handler(
                pre_block_bodies=[], block_response_body={"choices": [{"message": {"content": "H05-P5-UNEXPECTED"}}]},
                wait_timeout=1.0, label="p5-resume-deadcheck-gm",
            journal_path=case / 'p5-resume-deadcheck-gm-wire-events.jsonl', )
        )
        dead_gm_srv, dead_gm_thread, dead_gm_url = h05sup.start_http_server(DeadGmHandler)
        resume_env_extra = {
            "MMO_SIM_PERSONA_API_BASE_URL": dead_persona_url,
            "MMO_SIM_PERSONA_API_KEY": "SYNTH-H05-NOT-A-REAL-KEY",
            "MMO_SIM_PERSONA_API_MODEL": "synthetic-h05-persona-resume",
            "OPENWEBUI_URL": dead_gm_url, "OPENWEBUI_API_KEY": "SYNTH-H05-NOT-A-REAL-KEY",
            "MMO_SIM_LOBBY_INITIATIVE_LIMIT": "8",
        }
        resume_args = [
            "resume", "--data-dir", str(root), "--community", community_participant_id, "--profile", "api",
            "--personas", "sniper,tech", "--max-requests", "40", "--max-seconds", "120",
            "--max-usd", "5", "--max-idle-windows", "1", "--max-wall-seconds", "90",
        ]
        try:
            p_resume = h02journey._run_lab(
                resume_args, env_extra=resume_env_extra, tmp_root=root / "kidtmp_resume_run", guard_dir=guard_dir, timeout=60,
            )
        finally:
            h05sup.stop_http_server(dead_persona_srv, dead_persona_thread)
            h05sup.stop_http_server(dead_gm_srv, dead_gm_thread)
        h02journey._log_invocation(case, "resume", resume_args, resume_env_extra, p_resume)
        sup.write_json(case / "resume-stdout.json", {"stdout": p_resume.stdout, "stderr": p_resume.stderr, "rc": p_resume.returncode})
        sup.write_json(case / "dead-receiver-hits-after-resume.json", {
            "persona_receipts": dead_persona_receipts, "gm_receipts": dead_gm_receipts,
        })
        assert dead_persona_receipts == [] and dead_gm_receipts == [], (
            f"P5: nach Resume duerfen die eigenen Nullzaehler-Empfaenger (Persona/GM) KEINE Treffer zeigen -- "
            f"die urspruenglich offene Anfrage darf nicht automatisch ein zweites Mal versendet werden: "
            f"persona={dead_persona_receipts} gm={dead_gm_receipts}"
        )

        assert p_resume.returncode == 0, (
            f"P5: 'lab resume' muss trotz des unbekannten/offenen Requests kontrolliert beenden (sicherer Hold, "
            f"kein Absturz): rc={p_resume.returncode} stdout={p_resume.stdout!r} stderr={p_resume.stderr!r}"
        )
        assert "Lobby-Tisch abgeschlossen" not in p_resume.stdout, p_resume.stdout

        # H05-Repro-Vorabklaerung (dokumentiert VOR dieser Assertion, kein
        # Produktwrite noetig): der real beobachtete `lab resume`-Pfad fuer
        # ein bereits GESPIELTES, per `locks.json` gebundenes Tisch mit
        # offenem Abschluss laeuft NICHT durch `find_bound_active_
        # unplayed_table` (`core/store.py:632-695`, dort EXPLIZIT durch
        # `if table.sl_log: return None` UND `if _open_completion_order_for_
        # table(...): return None` ausgeschlossen -- Docstring: "das ist der
        # bereits bestehende, hier NICHT angefasste Resume-Pfad" -- dieser
        # andere Pfad ist die TUI-only `ui/tui.py:_play_bound_table`, vom
        # headless `lab`-Controller NIEMALS aufgerufen). `lab resume` bindet
        # deshalb bewusst NICHT automatisch an den offenen Tisch: reale
        # Ausgabe "Tisch(e) lobby-sniper-tech bereits gebunden ... kontrolliert
        # offen" (`lobby_flow.py:421-430`), OPEN_WITH_REASON, dann Leerlauf-
        # grenze -- KEIN Absturz, KEIN Doppelversand, KEIN Reset. Das IST der
        # bereits vorhandene, eindeutig sichere Hold: die per SIGKILL
        # unterbrochene Operation wird NICHT erneut angefasst, weil `lab
        # resume` diesen Tisch in diesem Zustand ueberhaupt nicht automatisch
        # wieder betritt -- keine Erfindung, kein neuer Produktcode.
        assert "bereits gebunden" in p_resume.stdout and "kontrolliert offen" in p_resume.stdout, (
            f"P5: erwartete ehrliche 'bereits gebunden/kontrolliert offen'-Meldung fehlt -- "
            f"tatsaechliche Ausgabe: {p_resume.stdout!r}"
        )

        reflections_after_resume = sup.read_jsonl(run_dir / "reflections.jsonl")
        sup.write_json(case / "reflections-after-resume.json", reflections_after_resume)
        assert reflections_after_resume == [], (
            f"P5: 'lab resume' beruehrt den offenen Tisch nicht -- keine neue/erfundene Reflexion, kein "
            f"pending_recovery-Nebenwrite: {reflections_after_resume}"
        )

        # request_ledger: die urspruenglich offene Anfrage bleibt UNVERAENDERT
        # (identische id, weiterhin state=sent) -- KEIN Budget-/ID-/Save-Reset,
        # kein automatischer zweiter Versand DERSELBEN Operation.
        ledger_after_resume = _ledger_records_snapshot(run_dir)
        sup.write_json(case / "ledger-after-resume.json", ledger_after_resume)
        original_record_after_resume = next((r for r in ledger_after_resume if r["id"] == sent_before[0]["id"]), None)
        assert original_record_after_resume is not None and original_record_after_resume["state"] == "sent", (
            f"P5: die urspruengliche offene Anfrage (id={sent_before[0]['id']}) muss unveraendert state=sent bleiben "
            f"(unbekannt/offen), keine erfundene Antwort: {original_record_after_resume}"
        )
        assert original_record_after_resume == sent_before[0], (
            "P5: der urspruengliche Requestdatensatz darf durch resume BYTEGLEICH unveraendert bleiben (kein Reset)"
        )
        duplicate_attempts = [
            r for r in ledger_after_resume
            if (r.get("table_id"), r.get("section_id"), r.get("role"), r.get("turn_idx"), r.get("participant")) == stuck_identity
        ]
        assert len(duplicate_attempts) == 1, (
            f"P5: kein zweiter Reservierungsversand fuer DIESELBE Operationsidentitaet (table_id/section_id/role/"
            f"turn_idx/participant) -- weiterhin genau 1 Datensatz fuer {stuck_identity}: {duplicate_attempts}"
        )

        table = core_store.Table.load(run_dir, TABLE_ID)
        assert table.status == "active", f"P5: Tisch darf NICHT final geschlossen sein (kein erfundener Abschluss): {table.status}"
        locks = core_store._read_locks(run_dir)
        assert locks != {}, "P5: Locks duerfen NICHT geloest sein"
        assert not core_store._completion_final_path(run_dir, SECTION_ID).exists(), (
            "P5: kein __final-Marker (echter Storepfad) nach Resume erlaubt"
        )
        state_after_resume = h02journey._authority_state_snapshot(run_dir, states_dir, schema_path)
        sup.write_json(case / "state-after-resume.json", state_after_resume)
        _assert_protected_unchanged(
            state_before_kill, state_after_resume, context="P5 after-resume vs before-kill",
        )

        sup.write_json(case / "result.json", {
            "status": "PASS", "kill_rc": kill_rc, "resume_returncode": p_resume.returncode,
            "table_status": table.status, "stuck_request_id": sent_before[0]["id"],
        })


if __name__ == "__main__":
    import traceback

    tests = [
        test_p1_gm_stop_api,
        test_p1_gm_stop_hybrid,
        test_p2_reflection_stop_api,
        test_p2_reflection_stop_hybrid,
        test_p3_observer_end,
        test_p4_controller_sigint_api,
        test_p4_controller_sigterm_hybrid,
        test_p5_hard_interrupt_resume,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
            passed += 1
        except Exception:
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed}/{len(tests)} Tests bestanden.")
    sys.exit(0 if failed == 0 else 1)
