#!/usr/bin/env python3
"""
tests/mmo_sim/test_k1_k4_lobby_kontinuitaet.py — neue dauerhafte
Repo-Regressionen fuer den Lobby-Kontinuitaetsnachzug (K1-K4,
01_AUFTRAG_LOBBY_KONTINUITAET.md §3, MAIN-DATENWEGENTSCHEIDUNG.md
Zustandstabelle, REVIEW-LOBBY.md §3-6).

Ergaenzt (nicht ersetzt) `test_l01_l10_lobby_initiative.py` -- Fixtures/
Helfer werden von dort importiert (keine zweite Kopie derselben Bootstrap-/
Ready-/Session-Bausteine). Deckt:

K1 test_k1_*: neues b-Fenster nach reiner Pause -- ECHTER Subprozess-Neustart
    (andere PID), beide Personas werden im NEUEN Fenster tatsaechlich ERNEUT
    (real ueber Loopback-HTTP, kein Ledger-Replay) gefragt.
K2 test_k2_*: neues b-Fenster nach vollstaendigem Tischabschluss -- ECHTER
    Subprozess-Neustart, keine Wiederverwendung des alten Angebots/Consents,
    kein zweiter Tisch; UND das abgeschlossene Angebot ist im Offer-Log
    tatsaechlich an seine reale Tisch-ID gebunden (Resolution-Eintrag).
K1/K2 test_k1_k2_unit_*: schneller Einheitstest direkt auf den neuen
    `lobby_service`-Bausteinen (`resolve_window_id`/`reconstruct_pending_
    offer_events`/`append_offer_resolution`) -- belegt den Kernmechanismus
    ohne Prozess-Overhead.
K3 test_k3_*: Leader-Nominierung (Self-Leader bleibt Default, ABER ein
    anderer Kandidat kann als Leader vorgeschlagen werden UND muss selbst
    zustimmen) -- positiver Fall (Tisch mit nominiertem Leader) und
    negativer Fall (Ablehnung -> kein Tisch, keine stille Ersatzentscheidung).
K4 test_k4_*: `settle_received`-Gate -- ein `received`-Datensatz OHNE
    bekannte Originaldauer wird NICHT freigegeben (kontrolliert offen, kein
    Modellaufruf); mit bekannter Dauer (`accounted`) bleibt die Antwort ein
    positiver Fall.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import test_l01_l10_lobby_initiative as l01  # noqa: E402

from mmo_sim.core import lobby_service  # noqa: E402
from mmo_sim.core import request_ledger  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER, ZeitrissTableSizePolicy  # noqa: E402


def _persona_http_server(responses):
    return l01._persona_http_server(responses)


def _run_lobby_subprocess(root: Path, stdin_text: str, env_extra: dict, limit: int):
    """ECHTER, EIGENSTAENDIGER Python-Subprozess (`subprocess.Popen`) --
    `Popen.pid` liefert die tatsaechliche, von einem vorherigen Aufruf
    verschiedene Betriebssystem-PID (analog `test_l08_real_restart_...`)."""
    env = dict(os.environ)
    env.update(env_extra)
    env["MMO_SIM_LOBBY_INITIATIVE_LIMIT"] = str(limit)
    cmd = [sys.executable, str(_REPO_ROOT / "scripts" / "mmo_sim.py"),
           "--data-dir", str(root), "--participant", "op"]
    proc = subprocess.Popen(
        cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, env=env, cwd=str(root),
    )
    pid = proc.pid
    stdout, stderr = proc.communicate(input=stdin_text, timeout=30)
    return pid, proc.returncode, stdout, stderr


def test_k1_new_window_after_pause_real_subprocess_restart_both_asked_again():
    """K1 (01_AUFTRAG §3 A, MAIN-Zustandstabelle "Neues b-Fenster nach
    Pause"): Prozess 1 -- beide Personas pausieren ihr Initiativfenster
    (kein Angebot entsteht). Prozess 2 ist ein ECHTER neuer Subprozess
    (andere PID) -- BEIDE Personas werden im NEUEN Fenster tatsaechlich
    ERNEUT (real ueber Loopback-HTTP) gefragt, kein stilles Ledger-Replay
    der alten Pausen (der urspruengliche Bug, REVIEW-LOBBY.md §3, Probe 02)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["sniper", "tech"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = l01._bootstrap_community(
            root, "community-op", keys,
        )
        write_test_profile(run_dir)
        for pk in keys:
            l01._make_ready(onboarding_dir, states_dir, run_dir, pk)

        with _persona_http_server([
            (200, {"choices": [{"message": {"content": json.dumps({"action": "pause"})}}]}),
            (200, {"choices": [{"message": {"content": json.dumps({"action": "pause"})}}]}),
        ]) as srv1:
            env1 = {
                "MMO_SIM_PERSONA_API_BASE_URL": srv1.base_url, "MMO_SIM_PERSONA_API_KEY": "SYNTH",
                "MMO_SIM_PERSONA_API_MODEL": "synthetic-e2e",
                "OPENWEBUI_URL": "http://127.0.0.1:1", "OPENWEBUI_API_KEY": "unused",
            }
            pid1, rc1, out1, err1 = _run_lobby_subprocess(root, "b\nx\n", env1, limit=2)
            assert rc1 == 0, err1
            assert len(srv1.calls) == 2, f"beide Personas haetten real gefragt werden muessen: {srv1.calls}"
        assert not lobby_service.read_offer_log(run_dir), "kein Angebot erwartet -- beide pausieren"

        with _persona_http_server([
            (200, {"choices": [{"message": {"content": json.dumps({"action": "pause"})}}]}),
            (200, {"choices": [{"message": {"content": json.dumps({"action": "pause"})}}]}),
        ]) as srv2:
            env2 = {
                "MMO_SIM_PERSONA_API_BASE_URL": srv2.base_url, "MMO_SIM_PERSONA_API_KEY": "SYNTH",
                "MMO_SIM_PERSONA_API_MODEL": "synthetic-e2e",
                "OPENWEBUI_URL": "http://127.0.0.1:1", "OPENWEBUI_API_KEY": "unused",
            }
            pid2, rc2, out2, err2 = _run_lobby_subprocess(root, "b\nx\n", env2, limit=2)
            assert rc2 == 0, err2
            assert pid2 != pid1, "Prozess 2 muss ein ECHTER neuer Prozess sein (andere PID)"
            assert len(srv2.calls) == 2, (
                f"Explizites naechstes Fenster: beide Personas haetten ERNEUT real gefragt werden "
                f"muessen (kein Replay der alten Pausen aus Prozess 1): {srv2.calls}"
            )

        records = [json.loads(p.read_text(encoding="utf-8")) for p in (run_dir / "requests").glob("*.json")]
        section_ids = sorted({r.get("section_id") for r in records})
        assert len(section_ids) == 2, (
            f"Prozess 1 und Prozess 2 haetten ZWEI verschiedene Fenster-IDs verwenden muessen "
            f"(stabiler Cursor statt volatiler Laenge): {section_ids}"
        )


def test_k2_new_window_after_completed_table_binds_resolution_no_stale_reuse():
    """K1/K2 (01_AUFTRAG §3 A, MAIN-Zustandstabelle "Neues b-Fenster nach
    Abschluss"): Prozess 1 schliesst einen echten Tisch ab (echter
    Subprozess + Loopback-Wire fuer beide Rollen). Prozess 2 (ECHTER neuer
    Subprozess) -- beide pausieren dieses NEUE Fenster; KEIN zweiter Tisch,
    KEINE Wiederverwendung des alten propose/accept. Zusaetzlich: das
    abgeschlossene Angebot traegt im Offer-Log einen Resolution-Eintrag
    (`outcome=table_bound`), der es an seine TATSAECHLICHE Tisch-ID bindet
    (01_AUFTRAG §3 A: "bestaetigtes Angebot mit tatsaechlicher Tisch-/
    Section-ID verknuepfen")."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["sniper", "tech"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = l01._bootstrap_community(
            root, "community-op", keys,
        )
        write_test_profile(run_dir)
        for pk in keys:
            l01._make_ready(onboarding_dir, states_dir, run_dir, pk)

        table_id, section_id = "lobby-sniper-tech", "lobby-sniper-tech-section"
        final_saves = {pk: json.loads((l01._FIX / f"{pk}.json").read_text(encoding="utf-8")) for pk in keys}
        debrief = "\n".join(f"```json\n{json.dumps(b, ensure_ascii=False)}\n```" for b in final_saves.values())

        with _persona_http_server([
            (200, {"choices": [{"message": {"content": json.dumps({"action": "propose", "wants": ["tech"]})}}]}),
            (200, {"choices": [{"message": {
                # R1.2-Nachzug (REVIEW-LOBBY.md §3.2): offer_id traegt jetzt
                # die window_id -- `lobby_service.offer_id_for` ist die EINE
                # Stelle, die Produkt UND Test uebereinstimmend nutzen.
                "content": (
                    f"ENTSCHEIDUNG offer_id={lobby_service.offer_id_for('lobby-community-op-0', 'sniper', 0)} "
                    "participant_id=tech decision=accept"
                ),
            }}]}),
            (200, {"choices": [{"message": {"content": "Wir sichern das Gebiet."}}]}),
            (200, {"choices": [{"message": {"content": "Ich bin bereit."}}]}),
            (200, {"choices": [{"message": {"content": "Ich nehme mit, dass wir gut zusammengespielt haben."}}]}),
            (200, {"choices": [{"message": {"content": "Ich nehme mit, dass ich gut gedeckt war."}}]}),
        ]) as persona_srv, _persona_http_server([
            (200, {"choices": [{"message": {"content": "Ihr steht bereit. Was tut ihr?"}}]}),
            (200, {"choices": [{"message": {
                "content": f"{debrief}\n{COMPLETION_MARKER} table_id={table_id} section_id={section_id}",
            }}]}),
        ]) as gm_srv:
            env1 = {
                "MMO_SIM_PERSONA_API_BASE_URL": persona_srv.base_url, "MMO_SIM_PERSONA_API_KEY": "SYNTH",
                "MMO_SIM_PERSONA_API_MODEL": "synthetic-e2e",
                "OPENWEBUI_URL": gm_srv.base_url, "OPENWEBUI_API_KEY": "SYNTH",
            }
            pid1, rc1, out1, err1 = _run_lobby_subprocess(root, "b\nx\n", env1, limit=2)
            assert rc1 == 0, err1
            assert "Lobby-Tisch abgeschlossen" in out1, out1

        table = core_store.Table.load(run_dir, table_id)
        assert table.status == "closed"

        resolutions = [r for r in lobby_service.read_offer_log(run_dir) if r.get("type") == "resolution"]
        assert resolutions and resolutions[0]["outcome"] == "table_bound", resolutions
        assert resolutions[0]["table_id"] == table.table_id, (
            "abgeschlossenes Angebot muss an seine TATSAECHLICHE Tisch-ID gebunden sein"
        )

        with _persona_http_server([
            (200, {"choices": [{"message": {"content": json.dumps({"action": "pause"})}}]}),
            (200, {"choices": [{"message": {"content": json.dumps({"action": "pause"})}}]}),
        ]) as srv2:
            env2 = {
                "MMO_SIM_PERSONA_API_BASE_URL": srv2.base_url, "MMO_SIM_PERSONA_API_KEY": "SYNTH",
                "MMO_SIM_PERSONA_API_MODEL": "synthetic-e2e",
                "OPENWEBUI_URL": "http://127.0.0.1:1", "OPENWEBUI_API_KEY": "unused",
            }
            pid2, rc2, out2, err2 = _run_lobby_subprocess(root, "b\nx\n", env2, limit=2)
            assert rc2 == 0, err2
            assert pid2 != pid1, "Prozess 2 muss ein ECHTER neuer Prozess sein (andere PID)"
            assert len(srv2.calls) == 2, (
                f"NEUES Fenster nach Abschluss: beide Personas haetten ERNEUT real gefragt werden "
                f"muessen (kein Default aus altem Consent): {srv2.calls}"
            )
            assert "schlaegt eine Runde vor" not in out2, out2

        assert sorted(p.name for p in (run_dir / "tables").glob("*.json")) == [f"{table_id}.json"], (
            "kein zweiter Tisch/keine __2-Generation erwartet"
        )


def test_k1_k2_unit_window_and_resolution_mechanics():
    """K1/K2 Einheitstest (kein Subprozess-Overhead) direkt auf den neuen
    `lobby_service`-Bausteinen: (a) `_next_window_id`/`resolve_window_id`
    liefern einen stabilen, monoton fortlaufenden Cursor je Community; (b)
    ein noch OFFENES (nicht resolvedes) Angebot liefert seine urspruengliche
    `window_id` unveraendert zurueck (Fensterkontinuitaet); (c) ein RESOLVEDES
    Angebot (Resolution-Eintrag) wird von `reconstruct_pending_offer_events`
    NICHT mehr als offen zurueckgegeben, selbst wenn sein Konsens
    vollstaendig war."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        write_test_profile(run_dir)

        # (a) genuin neue Fenster -- stabiler, monoton fortlaufender Cursor.
        w0 = lobby_service.resolve_window_id(run_dir, "community-x", [])
        assert w0 == "lobby-community-x-0"
        w1 = lobby_service.resolve_window_id(run_dir, "community-x", [])
        assert w1 == "lobby-community-x-1", "jeder Aufruf OHNE offenes Angebot muss eine NEUE ID ziehen"
        # andere Community hat ihren EIGENEN Cursor.
        wy0 = lobby_service.resolve_window_id(run_dir, "community-y", [])
        assert wy0 == "lobby-community-y-0"

        # (b) ein offenes Angebot bindet seine urspruengliche window_id.
        lobby_service.append_offer_log_record(run_dir, {
            "type": "offer", "offer_id": "lobby-offer-sniper-0", "ts": "t0",
            "from": "sniper", "wants": ["tech"], "window_id": w1,
        })
        reconstructed = lobby_service.reconstruct_pending_offer_events(run_dir, offer_id_prefix="lobby-offer-")
        assert len(reconstructed) == 1 and reconstructed[0]["window_id"] == w1
        w_continued = lobby_service.resolve_window_id(run_dir, "community-x", reconstructed)
        assert w_continued == w1, "ein noch offenes Angebot muss seine urspruengliche Fenster-ID behalten"

        # (c) nach Resolution ist das Angebot verbraucht -- nicht mehr offen,
        # selbst wenn sein Konsens (hier absichtlich NICHT geloggt) fehlt.
        lobby_service.append_offer_resolution(run_dir, "lobby-offer-sniper-0", outcome="no_table")
        reconstructed_after = lobby_service.reconstruct_pending_offer_events(
            run_dir, offer_id_prefix="lobby-offer-",
        )
        assert reconstructed_after == [], "resolvedes Angebot darf nicht erneut als offen erscheinen"
        w_after_resolution = lobby_service.resolve_window_id(run_dir, "community-x", reconstructed_after)
        assert w_after_resolution not in (w0, w1), "nach Resolution muss ein GENUIN NEUES Fenster gezogen werden"


def test_k3_leader_nomination_accepted_creates_table_with_nominee_as_leader():
    """K3 (01_AUFTRAG §3 B, MAIN-Zustandsentscheidung: "Self-Leader bleibt
    zulaessig, aber nicht die einzige Rolle; ein anderer Leader muss selbst
    zustimmen"): sniper schlaegt vor, DASS TECH Leader wird (nicht sniper
    selbst). tech nimmt sowohl Mitgliedschaft ALS AUCH Leaderrolle an
    (strukturelles accept auf die entsprechend formulierte Einladung) --
    der entstandene Tisch fuehrt tech als Leader, sniper als Mitglied
    (kein automatischer Self-Leader trotz eigener Initiative)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["sniper", "tech"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = l01._bootstrap_community(
            root, "community-op", keys,
        )
        write_test_profile(run_dir)
        for pk in keys:
            l01._make_ready(onboarding_dir, states_dir, run_dir, pk)

        table_id, section_id = "lobby-sniper-tech", "lobby-sniper-tech-section"
        final_saves = {pk: json.loads((l01._FIX / f"{pk}.json").read_text(encoding="utf-8")) for pk in keys}
        gm = l01._TableGM(table_id, section_id, final_saves, turns_before_marker=3)
        sniper_driver = l01._ScriptedDriver("sniper", [
            json.dumps({"action": "propose", "wants": ["tech"], "leader": "tech"}),
            "Ich trete bei und lasse tech fuehren.",
            "Ich nehme mit, dass die Runde gut lief.",
        ])
        tech_driver = l01._ScriptedDriver("tech", [
            # R1.2-Nachzug (REVIEW-LOBBY.md §3.2): offer_id traegt jetzt die
            # window_id -- `lobby_service.offer_id_for` ist die EINE Stelle,
            # die Produkt UND Test uebereinstimmend nutzen.
            f"ENTSCHEIDUNG offer_id={lobby_service.offer_id_for('lobby-community-op-0', 'sniper', 0)} "
            "participant_id=tech decision=accept explanation=Ich uebernehme die Leaderrolle.",
            "Wir bewegen uns vorsichtig weiter.",
            "Ende der Runde, bleibt aufmerksam.",
            "Ich nehme mit, dass ich gut gefuehrt habe.",
        ])
        drivers = {"sniper": sniper_driver, "tech": tech_driver}
        printed: list[str] = []
        session = l01._session(
            "op", onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
            gm_transport_factory=lambda *_a, **_kw: gm,
            persona_driver_factory=lambda pk: drivers[pk],
            printed=printed,
        )
        session._cmd_lobby_initiative()
        out = "\n".join(printed)
        assert "Lobby-Tisch abgeschlossen" in out, out

        table = core_store.Table.load(run_dir, table_id)
        assert table.status == "closed" and set(table.members) == {"sniper", "tech"}
        assert table.leader == "tech", (
            f"nominierter, zustimmender Leader (tech) haette Leader werden muessen: {table.leader!r}"
        )
        offers = [r for r in lobby_service.read_offer_log(run_dir) if r.get("type") == "offer"]
        assert offers and offers[0].get("leader") == "tech" and offers[0].get("proposed_by") == "sniper", offers


def test_k3_leader_nomination_rejected_no_table_no_silent_self_leader():
    """K3 Gegenprobe (02_ABNAHME "Ungueltiges/fehlendes/fremdgebundenes
    Ereignis -> keine Tabelle"): sniper nominiert tech als Leader, tech
    LEHNT AB -- kein Tisch entsteht (weder mit tech noch mit sniper als
    stillem Ersatz-Leader), keine heimliche Verkleinerung/Umdeutung des
    Angebots."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["sniper", "tech"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = l01._bootstrap_community(
            root, "community-op", keys,
        )
        write_test_profile(run_dir)
        for pk in keys:
            l01._make_ready(onboarding_dir, states_dir, run_dir, pk)

        sniper_driver = l01._ScriptedDriver("sniper", [
            json.dumps({"action": "propose", "wants": ["tech"], "leader": "tech"}),
        ])
        tech_driver = l01._ScriptedDriver("tech", [
            f"ENTSCHEIDUNG offer_id={lobby_service.offer_id_for('lobby-community-op-0', 'sniper', 0)} "
            "participant_id=tech decision=reject explanation=Ich will jetzt nicht fuehren.",
        ])
        drivers = {"sniper": sniper_driver, "tech": tech_driver}
        printed: list[str] = []
        session = l01._session(
            "op", onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
            gm_transport_factory=lambda *_a, **_kw: (_ for _ in ()).throw(AssertionError("kein GM-Call erwartet")),
            persona_driver_factory=lambda pk: drivers[pk],
            printed=printed,
        )
        session._cmd_lobby_initiative()
        out = "\n".join(printed)
        assert "ohne bestaetigten Tisch" in out, out
        assert not list((run_dir / "tables").glob("*.json")), "kein Tisch (auch kein Self-Leader-Ersatz) erwartet"
        assert core_store._read_locks(run_dir) == {}


def test_k4_settle_received_gate_blocks_unaccounted_result_and_allows_accounted():
    """K4 (01_AUFTRAG §3 A, REVIEW-LOBBY.md §6): ein `received`-Datensatz
    OHNE bekannte Originaldauer (`settle_received` bleibt `received`) wird
    von `request_admitted_decision` NICHT freigegeben -- kontrolliert offen
    (`block_reason` gesetzt, KEIN Treiberaufruf). Ein zweiter Datensatz MIT
    bekannter Dauer settled normal nach `accounted` und wird als Entscheidung
    freigegeben (positiver Fall bleibt unveraendert)."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        write_test_profile(run_dir)

        # Unaccounted: simuliert einen Datensatz eines AELTEREN Schreibers
        # (vor dem A1-Fix, s. `request_ledger.settle_received`-Docstring),
        # der `received_seconds` nie kannte -- 02_ABNAHME Fall 05 erzeugt
        # dies ueber eine echte Altversion (`reference/legacy-duration-
        # snapshot`); hier direkt am persistierten Record simuliert (kein
        # produktiver Schreibpfad noetig, `received_seconds` faellt in
        # `finish_received` bereits VOR einem etwaigen `add_seconds`-Fehler
        # in denselben ersten Write).
        rid_unaccounted = request_ledger.begin(
            run_dir, role="lobby_initiative", participant="sniper", content="c1",
            reserved_usd=.01, table_id=None, section_id="lobby-community-op-0", turn_idx=0,
        )
        record_path = run_dir / "requests" / f"{rid_unaccounted}.json"
        stale = json.loads(record_path.read_text(encoding="utf-8"))
        stale.update({
            "state": "received", "usage": {"usd": .05}, "settled_ts": 1.0, "usd_reconciled": True,
            "result_text": '{"action":"propose","wants":["tech"]}',
        })
        record_path.write_text(json.dumps(stale, indent=2), encoding="utf-8")
        record = request_ledger.load_request(run_dir, rid_unaccounted)
        assert record["state"] == "received" and "received_seconds" not in record, record

        raising_driver = l01._RaisingDriver("sniper")
        decision, reason = lobby_service.request_admitted_decision(
            run_dir, raising_driver, {"system": "s", "user": "u"},
            role="lobby_initiative", participant="sniper", section_id="lobby-community-op-0", turn_idx=0,
        )
        assert decision is None and reason, "ungeklaerte Wirkung darf NICHT als Entscheidung freigegeben werden"

        # Accounted: normaler Schreiber, bekannte Dauer -- bleibt positiv.
        rid_accounted = request_ledger.begin(
            run_dir, role="lobby_initiative", participant="tech", content="c2",
            reserved_usd=.01, table_id=None, section_id="lobby-community-op-0", turn_idx=0,
        )
        request_ledger.finish_received(
            run_dir, rid_accounted, usage={"usd": .01}, seconds=1,
            result_text='{"action":"pause"}',
        )
        record2 = request_ledger.load_request(run_dir, rid_accounted)
        assert record2["state"] == "accounted", record2

        decision2, reason2 = lobby_service.request_admitted_decision(
            run_dir, l01._RaisingDriver("tech"), {"system": "s", "user": "u"},
            role="lobby_initiative", participant="tech", section_id="lobby-community-op-0", turn_idx=0,
        )
        assert reason2 is None and decision2.text == '{"action":"pause"}', (decision2, reason2)


if __name__ == "__main__":
    import traceback

    tests = [
        test_k1_new_window_after_pause_real_subprocess_restart_both_asked_again,
        test_k2_new_window_after_completed_table_binds_resolution_no_stale_reuse,
        test_k1_k2_unit_window_and_resolution_mechanics,
        test_k3_leader_nomination_accepted_creates_table_with_nominee_as_leader,
        test_k3_leader_nomination_rejected_no_table_no_silent_self_leader,
        test_k4_settle_received_gate_blocks_unaccounted_result_and_allows_accounted,
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
