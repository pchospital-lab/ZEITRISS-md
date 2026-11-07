#!/usr/bin/env python3
"""
tests/mmo_sim/drive_r6_c_gaststop_anzeige_evidence_2026_11_07.py -- ZR-
VOLLENDUNG-OHNE-LAN-NACHZUG-20261107-R6, 02_ABNAHME.md §C "vorhandener
offener Stop, jetzt mit zutreffender Gastanzeige" (= GENERAL-REVIEW.md §4
G-R6-03, 01_NACHZUG.md Arbeitsblock3).

ECHTER Real-Subprozess-Treiber (Betreiber figurfrei + EIN echter Gast-FIFO-
Kanal) auf dem R6-korrigierten Code. Fuehrt GENAU denselben engen C-Fall wie
`drive_r5_c_stop_offener_call_evidence_2026_11_07.py` weiter (dessen
akzeptierter Stop-/Save-/Retrykern -- dauerhafte Stopentscheidung, keine
gueltige spaete Antwort, kein Plan/Final im verworfenen Abschnitt, erhaltener
Originalsave, abgeschlossener neuer Retry -- wird NICHT neu aufgerollt, nur
WIEDERVERWENDET), schliesst aber GENAU die vorher offene Luecke:

  G-R6-03 (vorher): `_run_table_round`s Stop-Block druckte den endgueltigen
  Verwurf NUR auf den Betreiberkanal (`self._print`). Ein betroffener Gast
  MIT eigenem registriertem Terminal (`io is not self`) bekam diese Meldung
  NIE -- er blieb unverstanden am Aktionsprompt/Zeitgedanken stehen und sprang
  im Original direkt in die naechste Retry-Eingabe, ohne je zu erfahren, dass
  der Abschnitt bereits vorbei ist.

  R6-FIX (jetzt): dieselbe `stop_message` (Reuse, kein neuer Wortlaut) wird
  JETZT zusaetzlich an jeden betroffenen Gastkanal ausgegeben (`drivers.
  items()` + `is_human_driver`-Filter, derselbe Filter wie die bestehende
  Erfolgskarte). Dieser Treiber belegt das ECHT am Subprozess:

  1. Der betroffene Gast (guest_c1, eigener registrierter FIFO-Kanal) sieht
     JETZT auf SEINEM EIGENEN Kanal dieselbe verstaendliche Meldung
     ("gestoppt/nicht abgeschlossen", "ENDGUELTIG, kein Fortsetzen moeglich",
     eigener vorheriger Stand bleibt erhalten/freigegeben, zulaessiger
     naechster Schritt) -- NICHT nur der Betreiber-/Zuschauerkanal.
  2. Sein tatsaechlicher Menue-/Kontrollweg ist ECHT erreichbar: direkt nach
     der Stop-Anzeige bedient er auf SEINEM Kanal real '/stand' (zeigt seinen
     EIGENEN, unveraenderten Stand -- kein neuer Fortschritt aus dem
     verworfenen Abschnitt) und 'tisch' (echtes Tisch-Untermenue, keine
     zurueckbleibende Scheinaktion/Wartephase).
  3. Betreiber/Zuschauer bleiben unveraendert korrekt (R5-Kern); die spaete
     Antwort wird weiterhin NICHT als gueltiges Spiel/Erfolg veroeffentlicht.
  4. Datengegenprobe (R5-Kern, wiederverwendet): alter gueltiger Save
     unveraendert, kein Plan/Final/Adoption im verworfenen Abschnitt, 0
     weitere Calls in diesem Abschnitt. Ein echter neuer zulaessiger Retry
     (NEUER Tisch, nicht Fortsetzen des verworfenen) schliesst danach echt ab.

GM NUR als Grenzinjektion (`MMO_SIM_GM_TRANSPORT_DOUBLE`/`_r4_gm_double`),
NIE Live-Modell. Pure Python, nur `assert`, echter Exitcode, kein pytest.

§D Evidenz-Disziplin: vollstaendige originale stdout/stderr ab Prozessstart,
reale Prozessdaten (`*.procmeta.json`), tatsaechliche Sendeereignisse
gekoppelt an den zuvor beobachteten Prompt (`sends.jsonl`). `MERGED_
PROTOKOLL.md` ist zusaetzlich und ausdruecklich als ABGELEITET markiert, mit
dem wirklichen Codeanker als erster Zeile."""
from __future__ import annotations

import json
import os
import select
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

import drive_r4_evidence_2026_11_04 as r4  # noqa: E402
import _r6_evidence_helpers as r6  # noqa: E402

from _full_v7_fixture import full_v7_save  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER  # noqa: E402
import mmo_sim.core.admission as admission  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402

_OUT_ROOT = Path(os.environ.get("ZR_R6_EVIDENCE_DIR", str(_REPO_ROOT / "tmp" / "r6_evidence" / "C")))

_STOP_MESSAGE_MARKERS = (
    "ENDGUELTIG, kein Fortsetzen moeglich",
    "Betroffene eigene Figurenbindung freigegeben",
    "erneute Tischsuche/-anfrage ueber den normalen Produktweg moeglich",
)


def _git_codeanchor() -> str:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=str(_REPO_ROOT), capture_output=True, text=True, timeout=15,
    ).stdout.strip()
    diffstat = subprocess.run(
        ["git", "diff", "--stat", "mmo_sim/ui/tui.py"], cwd=str(_REPO_ROOT), capture_output=True, text=True, timeout=15,
    ).stdout.strip()
    return f"CODEANKER: HEAD={head} + uncommitteter Linus-Diff -- git diff --stat mmo_sim/ui/tui.py: {diffstat!r}"


def _wait_for_buffered_substr(reader: "r4._LineReader", marker: str, overall: float = 20.0) -> str:
    """Rework (Specht, 2026-11-07): puffer-basiert auf den tatsaechlichen
    readline-Prompt warten -- der kommt OHNE abschliessenden Newline und
    wird deshalb von `_wait_for_marker`/`pop_line` (zeilenbasiert) NICHT als
    eigene Zeile gefangen, bleibt aber bereits im `reader._buf` liegen,
    sobald er via `cat`-Relay/Kernel-Pipe angekommen ist. Reiner Peek auf
    denselben Puffer (kein Zeilenverbrauch) -- keine Reader-Desync ggue.
    `_wait_for_marker`/`_drain` auf demselben Kanal."""
    deadline = time.time() + overall
    while time.time() < deadline:
        if marker in reader._buf:
            return reader._buf
        ready, _, _ = select.select([reader], [], [], 0.1)
        if ready:
            if not reader.pump():
                raise AssertionError(f"Marker {marker!r} nicht gesehen (EOF); puffer={reader._buf!r}")
    raise AssertionError(f"Marker {marker!r} nicht gesehen (Timeout); puffer={reader._buf!r}")


def _wait_for_buffered_substr_copump(
    reader: "r4._LineReader", marker: str, others: "list[r4._LineReader]", overall: float = 40.0,
) -> str:
    """Rework (Main als Integrator, 2026-11-08): wie `_wait_for_buffered_substr`,
    aber pumpt WAEHREND des Wartens zusaetzlich die `others`-Reader (hier: der
    Host-/Betreiber-stdout-Kanal) leer -- OHNE deren Zeilen zu POPpen (reines
    `pump()` haengt nur an `_buf` an). Grund (reproduzierter Rest-Race ~8%,
    `puffer=''` nach 40s): der eine Betreiberprozess schreibt Gast- UND
    Betreiberausgabe. Wird waehrend eines langen Gast-Prompt-Waits NUR der
    Gastkanal gepumpt, kann die Betreiber-stdout-Pipe (64KB) volllaufen -> das
    Child blockiert beim stdout-Write -> es DRUCKT den erwarteten Gast-Prompt
    nie -> Timeout mit leerem Puffer. Cross-Channel-Pipe-Backpressure, KEIN
    Produktfehler (`tui.py` unveraendert) und KEIN Claim-Deadlock im Spielcode.
    Das Mitpumpen der Host-Pipe loest die Blockade; die Host-Bytes bleiben in
    `host_reader._buf` liegen und werden vom spaeteren `_drain(host_reader)`
    regulaer konsumiert -- keine Reader-Desync, keine verschluckte Zeile."""
    deadline = time.time() + overall
    live_others = list(others)
    while time.time() < deadline:
        if marker in reader._buf:
            return reader._buf
        ready, _, _ = select.select([reader, *live_others], [], [], 0.1)
        for r in ready:
            if r is reader:
                if not reader.pump():
                    raise AssertionError(f"Marker {marker!r} nicht gesehen (EOF); puffer={reader._buf!r}")
            else:
                # Host-/Nebenkanal nur leeren (Backpressure loesen), nicht POPpen.
                if not r.pump():
                    live_others.remove(r)
    raise AssertionError(f"Marker {marker!r} nicht gesehen (Timeout); puffer={reader._buf!r}")


def _write_procmeta(
    out_dir: Path, label: str, *, argv: list, cwd: str, pid: int, utc_start: str, utc_end: str, exit_code: int,
) -> Path:
    path = out_dir / f"{label}.procmeta.json"
    path.write_text(
        json.dumps({
            "label": label, "argv": list(argv), "cwd": str(cwd), "pid": int(pid),
            "utc_start": utc_start, "utc_end": utc_end, "exit": exit_code,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


class _SendLog:
    def __init__(self) -> None:
        self.events: list[dict] = []
        self._last_seen: dict[str, str] = {}

    def observed(self, channel: str, text: str) -> None:
        if text:
            self._last_seen[channel] = text

    def record(self, channel: str, line: str) -> None:
        self.events.append({
            "channel": channel, "ts_sent_utc": r6.utc(time.time()), "sent": line,
            "observed_prompt_before_send_tail": self._last_seen.get(channel, "")[-600:],
        })

    def write(self, out_dir: Path, rel: str = "sends.jsonl") -> Path:
        path = out_dir / rel
        path.write_text(
            "\n".join(json.dumps(e, ensure_ascii=False) for e in self.events) + ("\n" if self.events else ""),
            encoding="utf-8",
        )
        return path


def run_scene_c() -> dict:
    out_dir = _OUT_ROOT
    mf = r6.Manifest(out_dir)
    sendlog = _SendLog()
    findings: dict = {}

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data, run_dir, states_dir = root / "op_data", root / "run", root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        ctrl_fifo = fifo_dir / "ctrl.fifo"
        in_fifo, out_fifo = fifo_dir / "guest_in.fifo", fifo_dir / "guest_out.fifo"
        calls_log, cfg_path = root / "gm_calls.jsonl", root / "gmdouble_cfg.json"

        r4.write_test_profile(run_dir, max_turns=200)

        guest_onboarding = op_data / "guests" / "guest_c1" / "onboarding"
        guest_catalog = op_data / "guests" / "guest_c1" / "catalog"
        char_id = "chrono-r6c-guest"
        r4._seed_guest_figure(guest_onboarding, guest_catalog, "guest_c1", char_id, "fixture-r6c-guest-001")
        guest_figure_path = guest_catalog / "figures" / f"guest_c1__{char_id}.json"
        sha_guest_original_before = r4._sha256(guest_figure_path)

        table_id = "local-guest_c1"
        r4._write_gm_double_config(
            cfg_path, responses=["SL-Antwort auf Anker (R6-C, spaete Antwort nach Stop)."],
            calls_log=calls_log,
            stop={
                "after_call": 1, "kind": "table",
                "control_fifo": str(ctrl_fifo), "control_line": "/stop",
                "run_dir": str(run_dir), "table_id": table_id,
            },
        )
        env = r4._gm_double_env(cfg_path)

        argv = [
            sys.executable, "-u", "-B", str(r4._LAUNCHER),
            "--participant", "operator_r6c", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--operator-control-fifo", str(ctrl_fifo),
            "--guest-terminal", f"guest_c1:{in_fifo}:{out_fifo}",
        ]
        utc_start = r6.utc(time.time())
        proc = r4.subprocess.Popen(
            argv, cwd=str(_REPO_ROOT), env=env, stdin=r4.subprocess.PIPE,
            stdout=r4.subprocess.PIPE, stderr=r4.subprocess.PIPE, text=True, bufsize=1,
        )
        host_reader = r4._LineReader(proc.stdout.fileno())
        in_f, out_f = r4._open_guest_fifo_pair(in_fifo, out_fifo)
        r4._wait_for_path(ctrl_fifo)

        host_boot = r4._drain(host_reader, settle=0.6, overall=10.0)
        guest_boot = r4._drain(out_f, settle=0.6, overall=10.0)
        transcript_host: list[str] = list(host_boot)
        transcript_guest: list[str] = list(guest_boot)
        sendlog.observed("host", "".join(host_boot))
        sendlog.observed("guest_c1", "".join(guest_boot))

        def send_op(line: str) -> None:
            sendlog.record("host", line)
            r4._send_op(proc, line)

        def send_guest(line: str) -> None:
            sendlog.record("guest_c1", line)
            r4._send_guest(in_f, line)

        def wait_guest_prompt(marker: str, overall: float = 40.0) -> str:
            # Empirisch (Rework-Diagnose, 2026-11-07, analog zu Treiber A):
            # Claim-/Lock-bedingte Tail-Latenz vor dem Freitext-/Aktion-Read
            # kann unter Systemlast vereinzelt > 20s dauern (kein Deadlock).
            # 40.0 als grosszuegiger, weiterhin aktiv pollender Wait.
            # Rework (Specht, 2026-11-07): vor jedem kontestierten Send erst
            # den tatsaechlichen readline-Prompt puffer-basiert abwarten
            # (s. _wait_for_buffered_substr-Docstring), NICHT nur die
            # vorherige Body-/Markerzeile -- derselbe out_f-Reader, reiner
            # Peek, keine Reader-Desync ggue. _wait_for_marker/_drain.
            # Integrator-Haertung (2026-11-08): pumpt WAEHREND des Waits auch
            # den Host-stdout-Kanal leer (ohne zu POPpen), damit dessen 64KB-
            # Pipe nicht volllaeuft und den EINEN Betreiberprozess beim Write
            # blockiert -> sonst druckt das Child den Gast-Prompt nie
            # (reproduzierter Rest-Race ~8%, puffer='' nach 40s). Host-Bytes
            # bleiben in host_reader._buf fuer den spaeteren _drain(host_reader).
            buf = _wait_for_buffered_substr_copump(out_f, marker, [host_reader], overall=overall)
            sendlog.observed("guest_c1", buf)
            return buf

        def ensure_guest_prompt_seen(prior_text: str, marker: str, overall: float = 40.0) -> None:
            # Rework-Korrektur (Specht, 2026-11-07): wenn der Aufrufer VORHER
            # bereits per `_drain()` (statt `_wait_for_marker`) gewartet hat,
            # kann der gesuchte Prompt -- FALLS er zufaellig MIT Newline
            # ankam -- bereits vollstaendig als "Zeile" KONSUMIERT worden
            # sein (drain poppt kontinuierlich alle fertigen Zeilen, anders
            # als der einmalig zurueckkehrende `_wait_for_marker`). Ein reiner
            # Puffer-Peek (`_wait_for_buffered_substr`) saehe ihn dann NIE
            # mehr -- Dauerhang. Deshalb zuerst pruefen, ob der Prompt schon
            # im bereits GELESENEN Text (`prior_text`) ODER im aktuellen
            # Puffer steckt; nur wenn WEDER noch NICHT, aktiv weiterwarten.
            if marker in prior_text or marker in out_f._buf:
                return
            wait_guest_prompt(marker, overall=overall)

        # ── Normaler Produktweg (identisch zu R5-C/T1): anbieten/anfragen/
        # annehmen/starten.
        send_op("tisch-anbieten mesaC1")
        time.sleep(0.6)
        transcript_host.extend(r4._drain(host_reader, settle=0.3, overall=5.0))
        send_guest("tisch-anfragen mesaC1")
        after_request = r4._drain(out_f, settle=0.6, overall=10.0)
        transcript_guest.extend(after_request)
        sendlog.observed("guest_c1", "".join(after_request))
        assert any("Anfrage an Tisch 'mesaC1' gestellt" in l for l in after_request), after_request
        send_op("tisch-annehmen mesaC1 guest_c1")
        time.sleep(0.6)
        transcript_host.extend(r4._drain(host_reader, settle=0.3, overall=5.0))
        send_op("tisch-start mesaC1")

        anker_prompt = r4._wait_for_marker(out_f, "Empfaenger: Spielleitung (SL)", overall=25.0)
        transcript_guest.extend(anker_prompt)
        sendlog.observed("guest_c1", "".join(anker_prompt))

        # ── Echter Kontroll-FIFO-Stop WAEHREND des offenen GM-Aufrufs,
        # ausgeloest durch GENAU diesen Gastbeitrag (identischer Mechanismus
        # wie R5-C). Rework: der echte "Deine Aktion:"-Readline-Prompt kommt
        # OHNE Newline NACH der o.g. Zweckzeile -- puffer-basiert abwarten,
        # nicht blind direkt nach der Body-Zeile senden.
        wait_guest_prompt("Deine Aktion:")
        send_guest("Ich erkunde die Gegend (R6-C).")
        # R6-Kernbeleg (G-R6-03 Punkt1): JETZT explizit auf die Stop-Meldung
        # AM GASTKANAL warten (nicht nur per settle-Drain) -- dieselbe
        # `stop_message` wie der Betreiberkanal, deterministisch, kein
        # Ratefenster.
        post_answer = r4._wait_for_marker(out_f, "Betreiber-Stop", overall=25.0)
        transcript_guest.extend(post_answer)
        post_answer_joined = "".join(post_answer)
        sendlog.observed("guest_c1", post_answer_joined)
        assert "Unbekannte Auswahl" not in post_answer_joined, (
            f"R6-C/FIX6: Rundenantwort wurde fehlgeleitet: {post_answer}"
        )
        assert "SL-Antwort auf Anker (R6-C, spaete Antwort nach Stop)." not in post_answer_joined, post_answer_joined
        for marker in _STOP_MESSAGE_MARKERS:
            assert marker in post_answer_joined, (
                f"R6-C/G-R6-03 Punkt1: der betroffene GASTKANAL haette die verstaendliche Stop-"
                f"Meldung (Marker {marker!r}) sehen muessen -- vorher ging diese NUR an den "
                f"Betreiberkanal: {post_answer_joined!r}"
            )
        assert "nicht abgeschlossen" in post_answer_joined, post_answer_joined

        block_out = r4._drain(host_reader, settle=1.2, overall=15.0)
        transcript_host.extend(block_out)
        sendlog.observed("host", "".join(block_out))
        block_joined = "".join(block_out)
        assert "Betreiber-Stop gesetzt (/stop)" in block_joined, block_joined
        assert "Admission-Gate blockiert" in block_joined, (
            f"R6-C: Betreiber-Kanal haette die geblockte Entscheidung sichtbar erklaeren muessen: {block_joined}"
        )
        assert "ENDGUELTIG, kein Fortsetzen moeglich" in block_joined, block_joined
        assert (
            "[Zuschauer][verworfen -- nach Stop eingetroffen, nicht Teil des Spiels]" in block_joined
        ), block_joined
        assert "spaeter eingetroffene SL-Antworten sind kein gueltiger Spielinhalt mehr" in block_joined, block_joined
        assert "SL-Antwort auf Anker (R6-C, spaete Antwort nach Stop)." not in block_joined, (
            "R6-C: der Discard-Hinweis darf den verworfenen Inhalt NICHT als Text reproduzieren "
            f"(sonst waere es doch eine Publikation): {block_joined}"
        )
        # Dieselbe stop_message auf BEIDEN Kanaelen -- Reuse, kein zweiter,
        # abweichender Wortlaut (01_NACHZUG.md Arbeitsblock3 "Reuse der
        # bestehenden Outcome-/Claim-/Resumequellen; keine zweite Stop-/
        # Adoptionsautoritaet").
        host_stop_line = next((ln for ln in block_out if "Betreiber-Stop" in ln and "ENDGUELTIG" in ln), None)
        guest_stop_line = next((ln for ln in post_answer if "Betreiber-Stop" in ln and "ENDGUELTIG" in ln), None)
        assert host_stop_line is not None and guest_stop_line is not None, (host_stop_line, guest_stop_line)
        assert host_stop_line == guest_stop_line, (
            "R6-C/G-R6-03: Betreiber- und Gastkanal haetten DIESELBE Stop-Meldung (Reuse, kein "
            f"zweiter Wortlaut) zeigen muessen: host={host_stop_line!r} guest={guest_stop_line!r}"
        )

        full_guest_so_far = "".join(transcript_guest)
        assert "Abschnitt abgeschlossen" not in full_guest_so_far, full_guest_so_far
        assert "Export des eigenen Standes" not in full_guest_so_far, full_guest_so_far

        calls = [json.loads(l) for l in calls_log.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(calls) == 1, f"R6-C: GENAU EIN Call vor/waehrend Stop, 0 danach: {calls}"
        assert calls[0]["content_returned"] == "SL-Antwort auf Anker (R6-C, spaete Antwort nach Stop)."
        assert "Ich erkunde die Gegend (R6-C)." in calls[0]["user_text_excerpt"], calls[0]

        stopped, stop_reason = admission.read_table_stop(run_dir, table_id)
        assert stopped is True, (stopped, stop_reason)
        decision = admission.read_table_decision(run_dir, table_id)
        assert decision is not None and decision.get("decision") == "stopped", decision
        section = core_store.Table.load(run_dir, table_id)
        assert section.status == "closed", section.status
        plan_path = run_dir / "completion" / f"{table_id}-section__plan.json"
        final_path = run_dir / "completion" / f"{table_id}-section__final.json"
        assert not plan_path.exists(), "R6-C: kein __plan.json -- die Planannahme haette den Stop verloren."
        assert not final_path.exists(), "R6-C: kein __final.json."
        guest_current_before_retry = run_dir / "current_saves" / "guest_c1.json"
        sha_guest_current_before_retry = (
            r4._sha256(guest_current_before_retry) if guest_current_before_retry.exists() else None
        )
        after_stop_guest_original_sha = r4._sha256(guest_figure_path)
        assert after_stop_guest_original_sha == sha_guest_original_before, (
            "R6-C: die persoenliche Gast-Originaldatei wurde trotz Stop veraendert."
        )

        # ═══ R6-Kernbeleg (G-R6-03 Punkt2): Menue-/Kontrollweg des Gastes
        # ECHT erreichbar, DIREKT NACH der Stop-Anzeige, OHNE jede
        # zurueckbleibende Scheinaktion/Wartephase -- '/stand' zeigt den
        # EIGENEN, unveraenderten Stand (kein neuer Fortschritt aus dem
        # verworfenen Abschnitt, kein current_saves-Eintrag bisher), 'tisch'
        # zeigt das ECHTE Tisch-Untermenue. ═══
        send_guest("/stand")
        stand_out = r4._drain(out_f, settle=0.6, overall=10.0)
        transcript_guest.extend(stand_out)
        stand_joined = "".join(stand_out)
        sendlog.observed("guest_c1", stand_joined)
        # Reachability-Beleg: '/stand' reagiert SOFORT (kein Timeout/keine
        # Wartephase) und das normale Hauptmenue wird danach korrekt
        # erneut gezeigt -- der Kontrollweg ist real nicht blockiert.
        # `guest_c1` hat VOR jedem Rundenabschluss (R4-Fixture `_seed_guest_
        # figure`, s. Docstring dort) absichtlich noch KEINE Katalog-
        # Bindung fuer eine volle Resume-Karte -- "Figur: noch keine Figur"
        # ist deshalb der ECHTE, unveraenderte Vorzustand (kein Produkt-
        # fehler); die eigentliche Unveraendertheits-Gegenprobe laeuft
        # separat ueber den SHA256 der persoenlichen Originaldatei (s.o./u.).
        assert ("Stand vorhanden" in stand_joined) or ("Kein aktueller Stand vorhanden" in stand_joined), (
            "R6-C/G-R6-03 Punkt2: '/stand' am Gastkanal haette direkt nach der Stop-Anzeige "
            f"real reagieren muessen (Menue-/Kontrollweg erreichbar, keine Wartephase): {stand_joined!r}"
        )
        assert "Hauptmenue:" in stand_joined, (
            "R6-C/G-R6-03 Punkt2: nach '/stand' haette das normale Hauptmenue erneut gezeigt "
            f"werden muessen (Menue-/Kontrollweg real erreichbar): {stand_joined!r}"
        )
        assert "Level 2" not in stand_joined and "lvl=2" not in stand_joined, (
            "R6-C/G-R6-03 Punkt1 Datengegenprobe: KEIN neuer Fortschritt aus dem verworfenen "
            f"Abschnitt darf im eigenen Stand sichtbar sein: {stand_joined!r}"
        )

        send_guest("tisch")
        tisch_out = r4._drain(out_f, settle=0.6, overall=10.0)
        transcript_guest.extend(tisch_out)
        tisch_joined = "".join(tisch_out)
        sendlog.observed("guest_c1", tisch_joined)
        assert "Tisch -- [1] Offene Tische suchen" in tisch_joined, (
            "R6-C/G-R6-03 Punkt2: 'tisch' haette am Gastkanal direkt nach der Stop-Anzeige das "
            f"ECHTE Tisch-Untermenue zeigen muessen (Menue-/Kontrollweg erreichbar): {tisch_joined!r}"
        )
        send_guest("/zurueck")
        r4._drain(out_f, settle=0.4, overall=5.0)

        # ═══════════════════ (2) Tatsaechlicher Retry: NEUER Tisch ════════
        debrief_block = full_v7_save(char_id, name="GuestC1", save_id="fixture-r6c-guest-retry-002", level=2)
        debrief_text = (
            "Abschnitt beendet (R6-C echter Retry nach Stop), Standsicherung anbei.\n"
            "```json\n" + json.dumps(debrief_block) + "\n```\n" + COMPLETION_MARKER
        )
        r4._write_gm_double_config(
            cfg_path,
            responses=["SL-Antwort auf den Retry-Anker (R6-C).", debrief_text],
            calls_log=calls_log, stop=None,
        )

        send_op("tisch-anbieten mesaC1-retry")
        time.sleep(0.6)
        transcript_host.extend(r4._drain(host_reader, settle=0.3, overall=5.0))
        send_guest("tisch-anfragen mesaC1-retry")
        retry_request = r4._drain(out_f, settle=0.6, overall=10.0)
        transcript_guest.extend(retry_request)
        assert any("Anfrage an Tisch 'mesaC1-retry' gestellt" in l for l in retry_request), retry_request
        send_op("tisch-annehmen mesaC1-retry guest_c1")
        time.sleep(0.6)
        transcript_host.extend(r4._drain(host_reader, settle=0.3, overall=5.0))

        import mmo_sim.core.table_admission as table_admission

        send_op("tisch-start mesaC1-retry")
        retry_anker_prompt = r4._wait_for_marker(out_f, "Empfaenger: Spielleitung (SL)", overall=25.0)
        transcript_guest.extend(retry_anker_prompt)

        retry_record = table_admission.load_record(run_dir, "mesaC1-retry")
        retry_table_id = retry_record["section_id"]

        wait_guest_prompt("Deine Aktion:")
        send_guest("Ich sichere die Lage im Retry (R6-C).")
        retry_after_anker = r4._wait_for_marker(out_f, "Empfaenger: Spielleitung (SL)", overall=25.0)
        transcript_guest.extend(retry_after_anker)
        assert "[SL] SL-Antwort auf den Retry-Anker (R6-C)." in "".join(retry_after_anker), "".join(retry_after_anker)

        wait_guest_prompt("Deine Aktion:")
        send_guest("Ich schliesse den Retry-Abschnitt ab (R6-C).")
        retry_closed_guest = r4._wait_for_marker(out_f, "eigene lokale Notiz", overall=25.0)
        transcript_guest.extend(retry_closed_guest)
        # R6-Kernbeleg (bestaetigter Fehlschlagsmodus, ~1/8): der Notiz-
        # Freitext-Prompt ("Deine persoenliche Abschlussnotiz ...") kommt
        # OHNE Newline NACH der "eigene lokale Notiz"-Zweckzeile -- vorher
        # traf der direkt folgende Send intermittierend einen Menue-Prompt
        # ("Unbekannte Auswahl: 'abschlussnotiz'"). Jetzt puffer-basiert den
        # echten Freitext-Prompt abwarten.
        # Integrator-Korrektur (2026-11-08): wie bei der Auswahl-Karte unten
        # `ensure_guest_prompt_seen` statt reinem Peek -- der Notiz-Prompt kann,
        # FALLS er ausnahmsweise MIT Newline ankam, bereits vom vorangehenden
        # `_wait_for_marker("eigene lokale Notiz")` als Zeile konsumiert worden
        # sein; dann saehe ein reiner Puffer-Peek ihn nie (puffer='' nach 40s).
        # Zuerst den bereits gelesenen Text (retry_closed_guest) + Live-Puffer
        # pruefen, nur sonst (co-pumpend) weiterwarten.
        ensure_guest_prompt_seen(
            "".join(retry_closed_guest),
            "Deine persoenliche Abschlussnotiz (leer = ueberspringen):", overall=40.0,
        )
        send_guest("Abschlussnotiz Retry (R6-C).")
        retry_notiz_out = r4._drain(out_f, settle=0.6, overall=10.0)
        transcript_guest.extend(retry_notiz_out)
        retry_notiz_joined = "".join(retry_notiz_out)
        assert "-- Abschlusskarte fuer 'guest_c1' --" in retry_notiz_joined, retry_notiz_joined

        retry_block_out = r4._drain(host_reader, settle=0.8, overall=15.0)
        transcript_host.extend(retry_block_out)
        retry_block_joined = "".join(retry_block_out)
        assert "Abschnitt abgeschlossen:" in retry_block_joined, (
            f"R6-C: der tatsaechliche Retry haette echt abschliessen muessen: {retry_block_joined}"
        )

        # Rework: analoges Risiko zur Notiz-Falle -- die vorangehenden
        # _drain()-Aufrufe fangen den regulaeren Fall ab (settle=0.6s reicht
        # fast immer), aber die Abschlusskarten-Auswahl haengt am selben
        # Claim-Erwerb (_terminal_read_lock) wie in Treiber A, der unter
        # Systemlast laenger als 0.6s dauern kann. `ensure_guest_prompt_seen`
        # prueft ZUERST, ob der Prompt bereits in `retry_notiz_joined` (vom
        # vorangehenden `_drain()` bereits konsumiert) ODER im Live-Puffer
        # steckt -- NUR falls weder/noch, aktiv (bis 40.0s) weiterwarten.
        ensure_guest_prompt_seen(
            retry_notiz_joined, "Auswahl (Nummer, leer/zurueck = Hauptmenue):", overall=40.0,
        )
        send_guest("1")
        retry_guest_after_card = r4._drain(out_f, settle=0.6, overall=10.0)
        transcript_guest.extend(retry_guest_after_card)

        retry_final_path = run_dir / "completion" / f"{retry_table_id}-section__final.json"
        r4._wait_for_path(retry_final_path, overall=20.0)
        operator_card_out = r4._drain(host_reader, settle=0.8, overall=15.0)
        transcript_host.extend(operator_card_out)
        operator_card_joined = "".join(operator_card_out)
        assert "Tisch-Abschlusskarte (Betreiber, figurfrei)" in operator_card_joined, operator_card_joined
        send_op("1")
        operator_card_done = r4._drain(host_reader, settle=0.6, overall=10.0)
        transcript_host.extend(operator_card_done)
        send_op("/zurueck")
        operator_back = r4._drain(host_reader, settle=0.6, overall=10.0)
        transcript_host.extend(operator_back)

        retry_section = core_store.Table.load(run_dir, retry_table_id)
        assert retry_section.status == "closed", retry_section.status
        retry_current_path = run_dir / "current_saves" / "guest_c1.json"
        assert retry_current_path.exists(), "R6-C: Retry haette einen neuen Current-Save fuer guest_c1 schreiben muessen."
        retry_current_block = json.loads(retry_current_path.read_text(encoding="utf-8"))
        assert retry_current_block["characters"][0]["lvl"] == 2, retry_current_block
        sha_guest_current_after_retry = r4._sha256(retry_current_path)
        assert sha_guest_current_after_retry != sha_guest_current_before_retry, (
            "R6-C: der Retry haette einen GENUIN NEUEN Current-Stand schreiben muessen."
        )

        utc_end_cmd = r6.utc(time.time())
        send_op("beenden")
        try:
            stdout_tail, stderr_text = proc.communicate(timeout=30)
        except r4.subprocess.TimeoutExpired:
            proc.kill()
            stdout_tail, stderr_text = proc.communicate()
        utc_end = r6.utc(time.time())
        transcript_host.append(stdout_tail)
        full_host_stdout = "".join(transcript_host)
        assert proc.returncode == 0, f"R6-C: Betreiberprozess gescheitert: {stderr_text}"

        in_f.close()
        all_calls = [json.loads(l) for l in calls_log.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(all_calls) == 3, f"R6-C: 1 (Anker/Stop) + 2 (Retry-Anker, Debrief) = 3 Gesamtcalls: {all_calls}"

        # ── Evidenz.
        r6.write_process_result(
            out_dir, "operator_launcher", argv=argv, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
            stdout_text=full_host_stdout, stderr_text=stderr_text, pid=proc.pid,
        )
        _write_procmeta(
            out_dir, "operator_launcher", argv=argv, cwd=str(_REPO_ROOT), pid=proc.pid,
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
        )
        full_guest_stdout = "".join(transcript_guest)
        guest_argv = ["<fifo-pair>", str(in_fifo), str(out_fifo)]
        r6.write_process_result(
            out_dir, "guest_c1_channel", argv=guest_argv, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=0,
            stdout_text=full_guest_stdout, stderr_text="", pid=-1,
        )
        _write_procmeta(
            out_dir, "guest_c1_channel", argv=guest_argv, cwd=str(_REPO_ROOT), pid=-1,
            utc_start=utc_start, utc_end=utc_end, exit_code=0,
        )
        mf.record_process_files(
            "operator_launcher", aussage="r6c_operator_zuschauer_betreiber_transcript",
            run_id="R6-C-GASTSTOP-ANZEIGE", teilnehmer_figur="operator_r6c", tisch_abschnitt=f"{table_id}/{retry_table_id}",
        )
        mf.record_process_files(
            "guest_c1_channel", aussage="r6c_guest_channel_mit_stop_anzeige_transcript",
            run_id="R6-C-GASTSTOP-ANZEIGE", teilnehmer_figur="guest_c1", tisch_abschnitt=f"{table_id}/{retry_table_id}",
        )
        mf.export_file(calls_log, "gm_calls.jsonl", aussage="r6c_gm_double_calls_vor_und_nach_stop", run_id="R6-C-GASTSTOP-ANZEIGE", teilnehmer_figur="beide")
        mf.export_tree(run_dir, "run", aussage="r6c_run_dir_after_stop_and_retry", run_id="R6-C-GASTSTOP-ANZEIGE", teilnehmer_figur="beide")
        mf.export_file(guest_figure_path, "guest_original_unchanged.json", aussage="r6c_guest_original_unveraendert", run_id="R6-C-GASTSTOP-ANZEIGE", teilnehmer_figur="guest_c1")
        mf.export_file(retry_current_path, "guest_retry_current.json", aussage="r6c_guest_retry_current_neu", run_id="R6-C-GASTSTOP-ANZEIGE", teilnehmer_figur="guest_c1")
        sends_path = sendlog.write(out_dir)
        mf.entries.append({
            "aussage": "r6c_sendeereignisse_gekoppelt_an_beobachteten_prompt", "teilnehmer_figur": "beide",
            "tisch_abschnitt": None, "run_id": "R6-C-GASTSTOP-ANZEIGE",
            "path": str(sends_path.relative_to(out_dir)), "sha256": r6.sha256_of(sends_path),
            "bytes": sends_path.stat().st_size,
        })
        mf.write_json_body(
            "g_r6_03_kernbeleg.json",
            {
                "guest_channel_stop_message": post_answer_joined,
                "host_stop_line": host_stop_line, "guest_stop_line": guest_stop_line,
                "dieselbe_meldung_beide_kanaele": host_stop_line == guest_stop_line,
                "stand_nach_stop_am_gastkanal": stand_joined,
                "tisch_menue_nach_stop_am_gastkanal": tisch_joined,
            },
            aussage="r6c_g_r6_03_kernbeleg", run_id="R6-C-GASTSTOP-ANZEIGE", teilnehmer_figur="guest_c1",
        )
        mf.write_json_body(
            "inventory.json",
            {
                "vor_stop": {"guest_original_sha256": sha_guest_original_before, "plan_exists": False, "final_exists": False},
                "nach_stop": {
                    "guest_original_sha256": after_stop_guest_original_sha,
                    "guest_current_sha256_vor_retry": sha_guest_current_before_retry,
                    "plan_exists": plan_path.exists(), "final_exists": final_path.exists(),
                    "table_status": section.status, "stopped": stopped,
                },
                "nach_retry": {
                    "guest_current_sha256_nach_retry": sha_guest_current_after_retry,
                    "retry_table_status": retry_section.status,
                    "retry_final_exists": retry_final_path.exists(),
                    "retry_current_lvl": retry_current_block["characters"][0]["lvl"],
                },
                "gm_calls_gesamt": len(all_calls),
                "gm_calls_vor_stop": 1, "gm_calls_nach_stop_in_gestoppter_sektion": 0, "gm_calls_im_retry": 2,
            },
            aussage="r6c_inventory_vor_nach_stop_und_retry", run_id="R6-C-GASTSTOP-ANZEIGE", teilnehmer_figur="beide",
        )
        merged_path = out_dir / "MERGED_PROTOKOLL.md"
        merged_path.write_text(
            _git_codeanchor() + "\n\n"
            "ABGELEITETES, zusammengefuegtes Protokoll (R6-C Gaststop-Anzeige/G-R6-03) -- "
            "KEINE Originaldatei, reine Lesehilfe. Die Originale sind operator_launcher.stdout.txt "
            "/ guest_c1_channel.stdout.txt (unveraendert, vollstaendig ab Prozessstart).\n\n"
            "== Betreiber-/Zuschauerkanal ==\n" + full_host_stdout + "\n\n"
            "== Gastkanal (guest_c1, MIT R6-Stop-Anzeige) ==\n" + full_guest_stdout + "\n",
            encoding="utf-8",
        )
        mf.entries.append({
            "aussage": "r6c_abgeleitetes_merged_protokoll", "teilnehmer_figur": "beide",
            "tisch_abschnitt": None, "run_id": "R6-C-GASTSTOP-ANZEIGE",
            "path": str(merged_path.relative_to(out_dir)), "sha256": r6.sha256_of(merged_path),
            "bytes": merged_path.stat().st_size,
        })
        mf.write_manifest()
        mf.write_summary({
            "szene": "R6_C_gaststop_anzeige_g_r6_03",
            "aussage": (
                "Echter offener GM-Call haelt waehrend des Calls an -- '/stop' ueber die echte "
                "Kontroll-FIFO injiziert. JETZT (R6-FIX) sieht der betroffene Gast (eigenes "
                "registriertes FIFO-Terminal) auf SEINEM EIGENEN Kanal dieselbe verstaendliche "
                "Stop-Meldung wie der Betreiber (Reuse, identischer Wortlaut) -- vorher ging diese "
                "NUR an den Betreiberkanal. Direkt danach ist sein Menue-/Kontrollweg ECHT "
                "erreichbar: '/stand' zeigt seinen unveraenderten eigenen Stand (kein neuer "
                "Fortschritt aus dem verworfenen Abschnitt), 'tisch' zeigt das echte Tisch-"
                "Untermenue (keine zurueckbleibende Scheinaktion/Wartephase). Betreiber/Zuschauer "
                "bleiben unveraendert korrekt, die spaete Antwort wird weiterhin NICHT als "
                "gueltiges Spiel/Erfolg veroeffentlicht. Datengegenprobe (R5-Kern): alter Save "
                "unveraendert, kein Plan/Final im verworfenen Abschnitt, 0 weitere Calls. Ein "
                "echter neuer Retry (neuer Tisch) schliesst danach echt ab."
            ),
            "gastkanal_bekommt_stop_meldung": True,
            "dieselbe_meldung_wie_betreiberkanal": host_stop_line == guest_stop_line,
            "gastkanal_stand_nach_stop_zeigt_keinen_neuen_fortschritt": ("Level 2" not in stand_joined),
            "gastkanal_menue_nach_stop_erreichbar": "Tisch -- [1] Offene Tische suchen" in tisch_joined,
            "echter_subprozess_betreiber": True, "echter_gast_fifo_kanal": True,
            "stop_ueber_echte_kontroll_fifo": True, "spaete_antwort_normal_angezeigt_keine_publikation": True,
            "calls_vor_stop": 1, "calls_nach_stop_in_gestoppter_sektion": 0, "calls_im_retry": 2,
            "gestoppte_sektion_plan_final_fehlen": (not plan_path.exists()) and (not final_path.exists()),
            "guest_original_unveraendert": after_stop_guest_original_sha == sha_guest_original_before,
            "retry_echt_abgeschlossen": retry_section.status == "closed",
            "retry_current_neu_und_unterscheidbar": sha_guest_current_after_retry != sha_guest_current_before_retry,
        })

        findings["returncode"] = proc.returncode
        findings["gm_calls_total"] = len(all_calls)
        findings["stopped"] = stopped
        findings["gastkanal_bekommt_stop_meldung"] = True
        findings["gastkanal_menue_erreichbar"] = "Tisch -- [1] Offene Tische suchen" in tisch_joined
        findings["retry_closed"] = retry_section.status == "closed"
        return findings


def main() -> int:
    if _OUT_ROOT.exists():
        import shutil
        shutil.rmtree(_OUT_ROOT)
    _OUT_ROOT.mkdir(parents=True)
    try:
        findings = run_scene_c()
        print(f"OK   R6_C_gaststop_anzeige: {findings}")
        return 0
    except AssertionError as e:
        print(f"FAIL R6_C_gaststop_anzeige: {e}")
        return 1
    except Exception:
        print("ERROR R6_C_gaststop_anzeige:")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
