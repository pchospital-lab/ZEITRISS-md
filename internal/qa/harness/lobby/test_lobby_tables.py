#!/usr/bin/env python3
"""
lobby/test_lobby_tables.py — Offline-Tests fuer den Lobby/Tisch-Durchstich.

Pure Python, nur `assert`, echter Exitcode (0=pass, !=0=fail). Kein Netz, kein
Provider — Testfall 6 verifiziert das aktiv (Quelltext-Scan + Socket-Sperre waehrend
eines echten Section-Laufs).

Aufruf: python3 internal/qa/harness/lobby/test_lobby_tables.py
"""
from __future__ import annotations

import copy
import json
import shutil
import socket
import sys
import tempfile
import traceback
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rooms  # noqa: E402
import section  # noqa: E402
import sl_stub  # noqa: E402

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
STATES_SRC = FIXTURES / "persona_states"
SAVES_SRC = FIXTURES / "saves"
OFFERS_SRC = FIXTURES / "offers"
SL_CANNED_SRC = FIXTURES / "sl_canned"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _chrononaut_ids() -> dict[str, str]:
    data = _load(FIXTURES / "personas.json")
    return {p["persona_key"]: p["chrononaut_id"] for p in data["personas"]}


def _initial_saves(keys: list[str]) -> dict[str, dict]:
    return {pk: _load(SAVES_SRC / f"{pk}.json") for pk in keys}


def _offer_events(name: str) -> list[dict]:
    return _load(OFFERS_SRC / f"{name}.json")["events"]


class TmpEnv:
    """Frischer, isolierter run_dir + eine Kopie der Persona-State-Fixtures (damit
    Tests NIE die committeten Fixtures unter fixtures/persona_states/ mutieren)."""

    def __enter__(self):
        self._td = tempfile.TemporaryDirectory()
        root = Path(self._td.name)
        self.run_dir = root / "run"
        self.states_dir = root / "states"
        shutil.copytree(STATES_SRC, self.states_dir)
        self.lobby = rooms.Lobby(self.run_dir)
        return self

    def __exit__(self, *exc):
        self._td.cleanup()


CANON = ["cqb", "sniper", "face", "pyro", "tech"]
LOBBY8 = CANON + ["medic", "scout", "ghost"]


# ── Testfall 1: Kapazitaeten (Lobby 8, Tische 1/2/5, 0/6 unzulaessig) ───────────

def test_1_table_capacity():
    cids = _chrononaut_ids()
    with TmpEnv() as env:
        for pk in LOBBY8:
            env.lobby.join(pk)
        assert sorted(env.lobby.members()) == sorted(LOBBY8), "Lobby=8 muss alle 8 aufnehmen"
        assert len(env.lobby.members()) == 8

        t1, d1 = rooms.create_table_from_offer_log(
            env.lobby, "t1", _offer_events("table1_solo"), cids)
        assert t1 is not None and t1.members == ["face"], "Tisch-Groesse 1 muss zulaessig sein"
        for pk in t1.members:
            env.lobby.release_chrononaut(t1.chrononaut_ids[pk], t1.table_id)  # Kapazitaetstest, kein Lock-Test (s. Testfall 5)

        t2, d2 = rooms.create_table_from_offer_log(
            env.lobby, "t2", _offer_events("table2_pair"), cids)
        assert t2 is not None and sorted(t2.members) == ["sniper", "tech"], "Tisch-Groesse 2 muss zulaessig sein"
        for pk in t2.members:
            env.lobby.release_chrononaut(t2.chrononaut_ids[pk], t2.table_id)

        t5, d5 = rooms.create_table_from_offer_log(
            env.lobby, "t5", _offer_events("table5_full"), cids)
        assert t5 is not None and len(t5.members) == 5, "Tisch-Groesse 5 muss zulaessig sein"

        members_before = env.lobby.members()
        t0, d0 = rooms.create_table_from_offer_log(
            env.lobby, "t0", _offer_events("table0_empty"), cids)
        assert t0 is None, "Tisch-Groesse 0 (keine vollstaendige Offer) muss abgelehnt werden"
        assert env.lobby.members() == members_before, "Ablehnung darf Mitgliedschaften nicht aendern"
        assert not (env.run_dir / "tables" / "t0.json").exists(), "kein Tisch-Artefakt bei Ablehnung"

        t6, d6 = rooms.create_table_from_offer_log(
            env.lobby, "t6", _offer_events("table6_oversubscribed"), cids)
        assert t6 is None, "Tisch-Groesse 6 muss hart abgelehnt werden"
        assert not (env.run_dir / "tables" / "t6.json").exists()

        # 6. Beitritt NACH Tisch-Erstellung (Tisch t5 ist bereits voll):
        before_members = list(t5.members)
        before_cids = dict(t5.chrononaut_ids)
        ok = t5.join_more("medic", cids["medic"])
        assert ok is False, "6. Beitritt an vollem Tisch muss abgelehnt werden"
        assert t5.members == before_members, "6. Beitritt darf Mitgliedschaften nicht aendern"
        assert t5.chrononaut_ids == before_cids, "6. Beitritt darf keine Saves/Zuordnung aendern"
        reloaded = rooms.Table.load(env.run_dir, "t5")
        assert reloaded.members == before_members, "abgelehnter 6. Beitritt darf nicht persistiert werden"
        assert "medic" not in reloaded.members, "kein Ersatz-Tisch/-Spieler bei Ablehnung"


# ── Testfall 2: Kanaltrennung, Sichtfilter, Leader-only-Send ────────────────────

def test_2_channels_and_visibility():
    cids = _chrononaut_ids()
    with TmpEnv() as env:
        for pk in CANON:
            env.lobby.join(pk)

        tA, _ = rooms.create_table_from_offer_log(env.lobby, "tA", _offer_events("table2_pair"), cids)
        tB, _ = rooms.create_table_from_offer_log(env.lobby, "tB", _offer_events("table1_solo"), cids)
        assert tA is not None and tB is not None

        stub_a = sl_stub.SLStub(SL_CANNED_SRC / "table2_pair.json")
        result = section.run_section(
            env.lobby, tA, stub_a, "section-2-vis",
            _initial_saves(["sniper", "tech"]), env.states_dir)
        assert result.completion.success

        view_leader = rooms.persona_view(tA, "sniper")
        view_guest = rooms.persona_view(tA, "tech")
        assert view_leader["sl_log"] == view_guest["sl_log"], \
            "identischer voller SL-Text fuer alle Mitglieder"
        assert "operator_meta" not in view_leader, "Sichtfilter darf operator_meta nicht durchreichen"
        assert "chrononaut_ids" not in view_leader, "Sichtfilter darf keine internen Zuordnungsdaten zeigen"

        try:
            rooms.persona_view(tB, "sniper")
            raise AssertionError("Fremd-Tisch-Einblick haette abgelehnt werden muessen")
        except rooms.VisibilityError:
            pass

        op = rooms.operator_view(tA)
        assert "operator_meta" in op and "offer_log" in op["operator_meta"], \
            "Operator-Belegansicht muss Offer-Log-Rohdaten enthalten"
        assert op["operator_meta"] is not view_leader.get("operator_meta"), "getrennte Objekte"

        try:
            rooms.submit_to_sl(tA, "tech", stub_a, 99, "ich schreibe trotzdem")
            raise AssertionError("Nicht-Leader-Send haette abgelehnt werden muessen")
        except rooms.LeaderOnlySendError:
            pass


# ── Testfall 3: Gruppe/Leader aus Offers/Consents, Dissens != Konsens ───────────

def test_3_dissent_no_artificial_consensus():
    cids = _chrononaut_ids()
    events = _offer_events("dissent_log")

    only_dissent = [e for e in events if e.get("id", e.get("offer_id")) == "off-1"]
    d_partial = rooms.derive_group_and_leader(only_dissent)
    assert d_partial.leader is None and d_partial.members == [], \
        "reiner Dissens darf KEINE Gruppe/keinen Leader ergeben (kein kuenstlicher Konsens)"
    assert d_partial.dissenters.get("ghost") is not None, "ghosts Widerspruch muss protokolliert sein"

    d_full = rooms.derive_group_and_leader(events)
    assert d_full.leader == "medic", "Leader muss aus der ERSTEN vollstaendig angenommenen Offer folgen (off-2)"
    assert sorted(d_full.members) == ["medic", "scout"], "Gruppe = leader + tatsaechlich zustimmende Personas"
    assert "ghost" not in d_full.members, "Dissenter darf NIE Teil der Gruppe werden"
    assert d_full.dissenters.get("ghost") is not None, "Dissens bleibt auch nach spaeterer Offer dokumentiert"

    with TmpEnv() as env:
        for pk in ["medic", "scout", "ghost"]:
            env.lobby.join(pk)
        t_none, _ = rooms.create_table_from_offer_log(env.lobby, "t-dissent-only", only_dissent, cids)
        assert t_none is None, "Tisch-Erstellung aus reinem Dissens-Log muss scheitern"

        t_ok, _ = rooms.create_table_from_offer_log(env.lobby, "t-recovered", events, cids)
        assert t_ok is not None and "ghost" not in t_ok.members
        assert sorted(t_ok.members) == ["medic", "scout"]


# ── Testfall 4: Lobby->Tisch->Abschluss->Save/State, Idempotenz, Negativfaelle ──

def test_4_lifecycle_completion_and_negatives():
    cids = _chrononaut_ids()

    # Erfolgspfad + Doppel-Abschluss
    with TmpEnv() as env:
        for pk in ["sniper", "tech"]:
            env.lobby.join(pk)
        table, _ = rooms.create_table_from_offer_log(env.lobby, "t-ok", _offer_events("table2_pair"), cids)
        stub = sl_stub.SLStub(SL_CANNED_SRC / "table2_pair.json")
        res = section.run_section(
            env.lobby, table, stub, "section-4-ok",
            _initial_saves(["sniper", "tech"]), env.states_dir)
        assert res.completion.success and not res.completion.already_completed and res.completion.written

        sniper_state = json.loads((env.states_dir / "sniper.json").read_text())
        tech_state = json.loads((env.states_dir / "tech.json").read_text())
        assert sniper_state["rounds_played"] == 1
        assert tech_state["rounds_played"] == 1

        # R3 legt zusaetzlich ein `<section_id>__plan.json`-Journal an (Teilschreib-
        # Idempotenz, s. rooms.complete_section) UND C1/Auflage 1 einen
        # `<section_id>__final.json`-Finalisierungsmarker (resumierbare
        # Finalisierung, s. rooms.complete_section); beide sind keine
        # Mitglieder-Guards und werden hier bewusst ausgeklammert, damit die
        # Guard-Zaehlung unveraendert "genau eine Datei pro Mitglied" bedeutet.
        guard_files = sorted(p.name for p in (env.run_dir / "completion").glob("*section-4-ok*")
                              if not p.name.endswith("__plan.json")
                              and not p.name.endswith("__final.json"))
        assert len(guard_files) == 2, f"pro Mitglied genau eine Guard-Datei erwartet, war: {guard_files}"
        mtimes_before = {p: p.stat().st_mtime_ns for p in (env.run_dir / "completion").glob("*")}

        # Doppel-Abschluss: identische Ernte erneut auswerten
        again = rooms.complete_section(env.lobby, table, "section-4-ok", res.harvested, env.states_dir)
        assert again.already_completed is True and again.written is False, \
            "Doppel-Abschluss darf keinen zweiten Write ausloesen"
        mtimes_after = {p: p.stat().st_mtime_ns for p in (env.run_dir / "completion").glob("*")}
        assert mtimes_before == mtimes_after, "Guard-Dateien duerfen beim Doppel-Abschluss nicht neu geschrieben werden"
        sniper_state_2 = json.loads((env.states_dir / "sniper.json").read_text())
        assert sniper_state_2["rounds_played"] == 1, "persona_state darf beim Doppel-Abschluss nicht doppelt fortschreiben"

        assert table.leader in [m for m in table.members], "Leader bleibt Mitglied nach Abschluss"

    # Initial-Import allein ist KEIN Abschluss
    with TmpEnv() as env:
        for pk in ["sniper", "tech"]:
            env.lobby.join(pk)
        table, _ = rooms.create_table_from_offer_log(env.lobby, "t-setup-only", _offer_events("table2_pair"), cids)
        stub = sl_stub.SLStub(SL_CANNED_SRC / "table2_pair.json")
        rooms.submit_to_sl(table, table.leader, stub, 0, "Anker-Save (nur Setup, kein Debrief)")
        rooms.submit_to_sl(table, table.leader, stub, 1, "Gast-Save (nur Setup, kein Debrief)")
        assert list((env.run_dir / "completion").glob("*")) == [], \
            "Initial-Import (Setup) allein darf keine Completion-Guard-Datei erzeugen"

    # Fehlender Save verhindert falschen Erfolg
    with TmpEnv() as env:
        for pk in ["sniper", "tech"]:
            env.lobby.join(pk)
        table, _ = rooms.create_table_from_offer_log(env.lobby, "t-missing", _offer_events("table2_pair"), cids)
        stub = sl_stub.SLStub(SL_CANNED_SRC / "table2_missing_save.json")
        res = section.run_section(
            env.lobby, table, stub, "section-4-missing",
            _initial_saves(["sniper", "tech"]), env.states_dir)
        assert res.completion.success is False, "fehlender Save darf NICHT als Erfolg gewertet werden"
        assert "tech" in res.completion.missing
        assert list((env.run_dir / "completion").glob("*")) == [], "kein Guard-Write bei unvollstaendiger Ernte"
        tech_state = json.loads((env.states_dir / "tech.json").read_text())
        assert tech_state["rounds_played"] == 0, "persona_state darf bei fehlendem Save nicht fortgeschrieben werden"

    # Falsch zugeordneter Save verhindert falschen Erfolg
    with TmpEnv() as env:
        for pk in ["sniper", "tech"]:
            env.lobby.join(pk)
        table, _ = rooms.create_table_from_offer_log(env.lobby, "t-wrong", _offer_events("table2_pair"), cids)
        stub = sl_stub.SLStub(SL_CANNED_SRC / "table2_wrong_char_id.json")
        res = section.run_section(
            env.lobby, table, stub, "section-4-wrong",
            _initial_saves(["sniper", "tech"]), env.states_dir)
        assert res.completion.success is False, "falsch zugeordneter Save darf NICHT als Erfolg gewertet werden"
        assert "tech" in res.completion.missing
        assert list((env.run_dir / "completion").glob("*")) == []

    # complete_section() DIREKT mit falscher char_id unter gueltigem pk-Key
    # (umgeht section.py's Vorfilter, deckt den cid!=chrononaut_ids[pk]-Ast in
    # rooms.complete_section selbst ab statt nur den missing-Pfad ueber section.py)
    with TmpEnv() as env:
        for pk in ["sniper", "tech"]:
            env.lobby.join(pk)
        table, _ = rooms.create_table_from_offer_log(env.lobby, "t-direct-wrong-cid", _offer_events("table2_pair"), cids)
        harvested = _initial_saves(["sniper", "tech"])
        harvested["tech"] = _load(SAVES_SRC / "sniper.json")  # gueltiger v7-Block, aber falsche char_id fuer "tech"
        res = rooms.complete_section(env.lobby, table, "section-4-direct-wrong-cid", harvested, env.states_dir)
        assert res.success is False, "falsche char_id unter gueltigem pk-Key darf NICHT als Erfolg gewertet werden"
        assert "tech" in res.missing, "der cid!=chrononaut_ids[pk]-Ast muss 'tech' als missing melden"
        assert list((env.run_dir / "completion").glob("*")) == [], "kein Guard-Write bei falscher char_id"
        tech_state = json.loads((env.states_dir / "tech.json").read_text())
        assert tech_state["rounds_played"] == 0, "persona_state darf bei falscher char_id nicht fortgeschrieben werden"


# ── Testfall 5: Chrononaut-Lock (kein gleichzeitiger Fortschritt an 2 Tischen) ──

def test_5_chrononaut_lock():
    cids = _chrononaut_ids()
    with TmpEnv() as env:
        for pk in LOBBY8:
            env.lobby.join(pk)

        t5, _ = rooms.create_table_from_offer_log(env.lobby, "t5-lock", _offer_events("table5_full"), cids)
        assert t5 is not None

        blocked, derivation = rooms.create_table_from_offer_log(
            env.lobby, "t2-blocked", _offer_events("table2_pair"), cids)
        assert blocked is None, "sniper/tech sind ueber t5-lock bereits an einem Tisch aktiv"
        assert derivation.leader == "sniper", "Ableitung selbst findet die Gruppe, der Lock blockiert erst danach"
        assert not (env.run_dir / "tables" / "t2-blocked.json").exists()

        stub = sl_stub.SLStub(SL_CANNED_SRC / "table5_full.json")
        res = section.run_section(
            env.lobby, t5, stub, "section-5-lock",
            _initial_saves(CANON), env.states_dir)
        assert res.completion.success, "Voraussetzung: t5 muss abschliessen, um Locks freizugeben"

        t2_after, _ = rooms.create_table_from_offer_log(env.lobby, "t2-after", _offer_events("table2_pair"), cids)
        assert t2_after is not None, "nach Abschluss/Rueckkehr in Lobby muss der Lock freigegeben sein"


# ── Testfall 6: Kein echter Provider ────────────────────────────────────────────

FORBIDDEN_SOURCE_SIGNS = [
    "OWUIChat(", "sl_client.SLSession(", "OPENWEBUI_URL", "requests.get(",
    "requests.post(", "urllib.request", "http.client", "socket.create_connection(",
]


def test_6_no_real_provider():
    for mod_file in ["rooms.py", "sl_stub.py", "section.py"]:
        src = (HERE / mod_file).read_text(encoding="utf-8")
        for sign in FORBIDDEN_SOURCE_SIGNS:
            assert sign not in src, f"{mod_file} enthaelt verbotenes Provider-Signal: {sign}"

    cids = _chrononaut_ids()

    def _blocked_socket(*a, **kw):
        raise AssertionError("kein Netzwerk-Socket erwartet waehrend eines Stub-Laufs")

    real_socket = socket.socket
    socket.socket = _blocked_socket
    try:
        with TmpEnv() as env:
            for pk in ["cqb", "sniper"]:
                env.lobby.join(pk)
            table, _ = rooms.create_table_from_offer_log(env.lobby, "t-offline", _offer_events("table2_pair"), cids)
            # table2_pair-Offer erzeugt sniper+tech; wir nutzen hier bewusst nur
            # sniper/tech als Lobby-Mitglieder, cqb bleibt ungenutzt (Kapazitaets-Test).
        with TmpEnv() as env:
            for pk in ["sniper", "tech"]:
                env.lobby.join(pk)
            table, _ = rooms.create_table_from_offer_log(env.lobby, "t-offline2", _offer_events("table2_pair"), cids)
            stub = sl_stub.SLStub(SL_CANNED_SRC / "table2_pair.json")
            res = section.run_section(
                env.lobby, table, stub, "section-6-offline",
                _initial_saves(["sniper", "tech"]), env.states_dir)
            assert res.completion.success, "Stub-Lauf muss ohne jeden Socket-Zugriff vollstaendig durchlaufen"
    finally:
        socket.socket = real_socket

    r1 = sl_stub.SLStub(SL_CANNED_SRC / "table2_missing_save.json").turn(0, "x")
    r2 = sl_stub.SLStub(SL_CANNED_SRC / "table2_missing_save.json").turn(0, "x")
    assert r1["content"] == r2["content"], \
        "zwei unabhaengige Stub-Instanzen auf derselben Fixture muessen denselben ersten Turn liefern (rein fixture-getrieben, kein versteckter State)"
    exhausted = sl_stub.SLStub(SL_CANNED_SRC / "table1_solo.json")
    exhausted.turn(0, "a")
    exhausted.turn(1, "b")
    try:
        exhausted.turn(2, "c")
        raise AssertionError("SLStub haette bei Erschoepfung werfen muessen")
    except sl_stub.SLStubExhausted:
        pass


# ── Testfall 7: R7-Nachrichtenkanaele (Lobby/Tisch/Leader-SL-Dialog) ────────────

def test_7_message_channels():
    cids = _chrononaut_ids()
    with TmpEnv() as env:
        for pk in ["sniper", "tech", "cqb"]:
            env.lobby.join(pk)

        # Oeffentlicher Lobby-Kanal: nur Lobby-Mitglieder duerfen posten/lesen.
        env.lobby.post_lobby_message("sniper", "Wer will einen Zweiertisch bilden?")
        msgs = env.lobby.lobby_messages("tech")
        assert [m["from"] for m in msgs] == ["sniper"], "Lobby-Mitglied muss die Lobby-Nachricht lesen koennen"
        try:
            env.lobby.post_lobby_message("ghost", "ich bin nicht in der Lobby")
            raise AssertionError("Nicht-Lobby-Mitglied durfte im Lobby-Kanal senden")
        except rooms.VisibilityError:
            pass
        try:
            env.lobby.lobby_messages("ghost")
            raise AssertionError("Nicht-Lobby-Mitglied durfte den Lobby-Kanal lesen")
        except rooms.VisibilityError:
            pass

        # Privater Tisch-Absprachekanal: nur Tisch-Mitglieder duerfen posten/lesen.
        table, _ = rooms.create_table_from_offer_log(env.lobby, "t-msg", _offer_events("table2_pair"), cids)
        rooms.post_table_message(table, "sniper", "Ich uebernehme den HQ-Import.")
        rooms.post_table_message(table, "tech", "Bin bereit, importiere gleich.")
        view = rooms.persona_view(table, "tech")
        assert [m["from"] for m in view["table_messages"]] == ["sniper", "tech"], \
            "Tisch-Mitglied muss den vollstaendigen Absprachekanal lesen koennen"
        try:
            rooms.post_table_message(table, "cqb", "ich bin nicht an diesem Tisch")
            raise AssertionError("Fremdes Mitglied durfte im Tisch-Absprachekanal senden")
        except rooms.VisibilityError:
            pass
        try:
            rooms.persona_view(table, "cqb")
            raise AssertionError("Fremdes Mitglied durfte den Tisch-Absprachekanal lesen")
        except rooms.VisibilityError:
            pass

        # Leader/SL-Dialog: submit_to_sl (via run_section) persistiert die
        # gesendete Leader-Nachricht UND die SL-Antwort, inkl. Herkunftsbeleg
        # (welche Persona, welche Fixture) und GETRENNTER Save-Payload
        # (Auflage 6 — kein controller-formulierter Text getarnt als
        # Persona-Entscheidung, kein eingebetteter Save-JSON-Blob im Text).
        stub = sl_stub.SLStub(SL_CANNED_SRC / "table2_pair.json")
        result = section.run_section(
            env.lobby, table, stub, "section-7-msg",
            _initial_saves(["sniper", "tech"]), env.states_dir)
        assert result.completion.success

        reloaded = rooms.Table.load(env.run_dir, "t-msg")
        anchor_entry, guest_entry, debrief_entry = reloaded.sl_log[0], reloaded.sl_log[1], reloaded.sl_log[2]
        assert anchor_entry["origin_persona_key"] == "sniper", "Anker-Turn muss den Leader als Herkunft ausweisen"
        assert anchor_entry["origin_source"], "Anker-Turn muss einen Herkunfts-/Quellenbeleg tragen"
        assert anchor_entry["save_payload"] == _initial_saves(["sniper"])["sniper"], \
            "dynamischer Save-Inhalt muss als GETRENNTE Payload transportiert werden"
        # NB-A/R7 (Test 01 der externen Re-Review): der Save MUSS den tatsaechlichen
        # SL-Empfaenger (den Wire-Text an sl_stub.turn) erreichen, sonst empfaengt der
        # SL-Adapter nie einen Save. Das pauschale Wire-Verbot ("kein Save-Marker im
        # Leader-Text") war der FALSCHE Invariant (technische Serialisierung der
        # freigegebenen Nachricht + Save ist ausdruecklich erlaubt, keine erfundene
        # Persona-Entscheidung) -- richtig ist: Save im Wire-Text vorhanden UND
        # Herkunft/Entscheidung bleiben GETRENNT ueber origin_*/save_payload
        # nachvollziehbar (beide zusaetzlich geprueft, nicht ersetzt).
        assert rooms.save_lib.extract_all_saves(stub.calls[0]["user_text"]) == [anchor_entry["save_payload"]], \
            "Anker-Turn muss den Save tatsaechlich im an den SL-Empfaenger gesendeten Text tragen"
        assert anchor_entry["origin_persona_key"] and anchor_entry["save_payload"] is not None, \
            "Herkunft (origin_persona_key) und Save-Payload bleiben getrennt vom Wire-Text nachvollziehbar"
        assert guest_entry["origin_persona_key"] == "tech", "Gast-Turn muss den Gast als Herkunft ausweisen"
        assert guest_entry["save_payload"] == _initial_saves(["tech"])["tech"]
        assert rooms.save_lib.extract_all_saves(stub.calls[1]["user_text"]) == [guest_entry["save_payload"]], \
            "Gast-Turn muss den Save tatsaechlich im an den SL-Empfaenger gesendeten Text tragen"
        assert debrief_entry["origin_persona_key"] == "sniper"

        # Sichtfilter bleibt auch nach dem Abschluss aktiv: operator_meta/Locks/
        # Dissens sind nicht Teil der Persona-Sicht.
        member_view = rooms.persona_view(reloaded, "tech")
        assert "operator_meta" not in member_view and "chrononaut_ids" not in member_view


# ── Testfall 8: R5-Zusatzpersona (medic) durch den vollen Offline-Lifecycle ─────

def test_8_medic_extra_persona_full_lifecycle():
    cids = _chrononaut_ids()
    with TmpEnv() as env:
        for pk in LOBBY8:
            env.lobby.join(pk)

        table, _ = rooms.create_table_from_offer_log(
            env.lobby, "t-medic-solo", _offer_events("medic_solo"), cids)
        assert table is not None and table.members == ["medic"], \
            "medic (R5-Zusatzpersona jenseits der historischen fuenf) muss einen Solo-Tisch bilden koennen"

        stub = sl_stub.SLStub(SL_CANNED_SRC / "medic_solo.json")
        res = section.run_section(
            env.lobby, table, stub, "section-8-medic",
            _initial_saves(["medic"]), env.states_dir)
        assert res.completion.success, "medic muss den vollen Offline-Lifecycle (Solo-Abschnitt) abschliessen koennen"

        medic_state = json.loads((env.states_dir / "medic.json").read_text())
        assert medic_state["rounds_played"] == 1
        assert medic_state["persona_key"] == "medic", "Schema-Pattern (statt Enum) darf medic als persona_key nicht ablehnen"

        current_save = rooms.load_current_save(env.run_dir, "medic")
        assert current_save is not None and current_save["characters"][0]["char_id"] == cids["medic"]

        assert "medic" in env.lobby.members(), "medic muss nach Abschluss (weiterhin) Lobby-Mitglied sein"


# ── Testfall 9: NB-A/R7 — Save erreicht den tatsaechlichen SL-Empfaenger ────────

def test_9_nb_a_receiver_save_reaches_sl():
    """NB-A/R7 (Test 01 der externen Re-Review): der initiale v7-Save MUSS im
    tatsaechlich an den SL-Stub gesendeten Wire-Text stehen (nicht nur im
    getrennt gefuehrten sl_log), sonst empfaengt ein echter SL-Adapter nie
    einen Save."""
    cids = _chrononaut_ids()
    with TmpEnv() as env:
        for pk in ["sniper", "tech"]:
            env.lobby.join(pk)
        table, _ = rooms.create_table_from_offer_log(env.lobby, "t-nb-a", _offer_events("table2_pair"), cids)
        stub = sl_stub.SLStub(SL_CANNED_SRC / "table2_pair.json")
        saves = _initial_saves(["sniper", "tech"])
        res = section.run_section(env.lobby, table, stub, "section-nb-a", saves, env.states_dir)
        assert res.completion.success
        received = [rooms.save_lib.extract_all_saves(c["user_text"]) for c in stub.calls[:2]]
        assert received == [[saves["sniper"]], [saves["tech"]]], \
            "Anker-/Gast-Turn muessen den jeweiligen v7-Save im tatsaechlichen SL-Empfangstext tragen"


# ── Testfall 10: NB-B/R2 — Abschluss-Marker: Qualifier + json-Strip (Auflage 5) ─

def test_10_nb_b_marker_qualifiers_and_json_stripping():
    """NB-B/R2 (Tests 02+03 der externen Re-Review, Auflage 5): ein Marker
    INNERHALB eines importierten json-Blocks zaehlt nicht (muss erst
    gestrippt werden); ein Marker mit FREMDEN table_id/section_id-Qualifiern
    zaehlt ebenfalls nicht. Zusaetzlich: alle 6 fixtures/sl_canned/*.json
    (inkl. der 2 Negativ-Fixtures) tragen einen fuer die aktuelle Session
    gueltigen Marker und scheitern (falls sie scheitern) am RICHTIGEN Grund,
    nie am Marker-Gate."""
    cids = _chrononaut_ids()

    quoted_text = (
        'Kein neuer Abschnitt.\n```json\n'
        + json.dumps({"note": "Historisches Beispiel: " + section.COMPLETION_MARKER})
        + '\n```'
    )
    assert section._completion_marker_matches(quoted_text, "any-table", "any-section") is False, \
        "Marker als String-Wert INNERHALB eines json-Blocks darf nicht zaehlen"

    foreign_text = section.COMPLETION_MARKER + " table_id=other-table section_id=other-section"
    assert section._completion_marker_matches(foreign_text, "pair", "expected-section") is False, \
        "Marker mit fremden Qualifiern darf fuer die aktuelle Session nicht gelten"

    bare_text = "Gut gemacht, Team.\n" + section.COMPLETION_MARKER
    assert section._completion_marker_matches(bare_text, "pair", "expected-section") is True, \
        "blanker Marker (eigenstaendige Zeile) muss fuer die aktuelle Session gelten"

    matching_text = section.COMPLETION_MARKER + " table_id=pair section_id=expected-section"
    assert section._completion_marker_matches(matching_text, "pair", "expected-section") is True, \
        "Marker mit ZUTREFFENDEN Qualifiern muss gelten"

    fixture_cases = [
        ("table1_solo", "table1_solo", ["face"], True),
        ("table2_pair", "table2_pair", ["sniper", "tech"], True),
        ("table2_missing_save", "table2_pair", ["sniper", "tech"], False),
        ("table2_wrong_char_id", "table2_pair", ["sniper", "tech"], False),
        ("table5_full", "table5_full", CANON, True),
        ("medic_solo", "medic_solo", ["medic"], True),
    ]
    for sl_name, offer_name, members, expect_success in fixture_cases:
        with TmpEnv() as env:
            for pk in LOBBY8:
                env.lobby.join(pk)
            table, _ = rooms.create_table_from_offer_log(
                env.lobby, f"t-marker-{sl_name}", _offer_events(offer_name), cids)
            assert table is not None, f"{sl_name}: Tisch-Setup fehlgeschlagen"
            stub = sl_stub.SLStub(SL_CANNED_SRC / f"{sl_name}.json")
            res = section.run_section(
                env.lobby, table, stub, f"section-marker-{sl_name}",
                _initial_saves(members), env.states_dir)
            assert res.completion.success is expect_success, f"{sl_name}: {res.completion.reason}"
            assert "Marker" not in res.completion.reason, \
                f"{sl_name} darf nicht am Marker-Gate scheitern: {res.completion.reason}"


# ── Testfall 11: NB-C/R1+R3 — Finalize-Recovery + torn current-save ────────────

def test_11_nb_c_finalize_recovery_and_torn_current_save():
    """NB-C/R1+R3 (Tests 04+05 der externen Re-Review):
    - Finalize-Recovery: crasht die Finalisierung NACH der Schreibschleife
      (Lock-Freigabe), aber VOR dem `__final`-Marker, muss ein Retry die
      Finalisierung nachholen (Locks frei, status=closed, __final vorhanden)
      — OHNE bereits geschriebene Mitglieder ein zweites Mal fortzuschreiben.
    - Torn current-save: reisst der DIREKTE `current_saves/<pk>.json`-Schreib-
      vorgang waehrend eines ZWEITEN Abschlusses ab, bleibt der zuletzt
      gueltige (versionierte) Save ueber `load_current_save` weiterhin lesbar.
    """
    cids = _chrononaut_ids()

    with TmpEnv() as env:
        for pk in ["sniper", "tech"]:
            env.lobby.join(pk)
        table, _ = rooms.create_table_from_offer_log(env.lobby, "t-nb-c-crash", _offer_events("table2_pair"), cids)
        saves = _initial_saves(["sniper", "tech"])
        with patch.object(env.lobby, "release_chrononaut",
                           side_effect=OSError("SIMULATED crash before final marker")):
            try:
                rooms.complete_section(env.lobby, table, "section-nb-c-crash", saves, env.states_dir)
                raise AssertionError("erwarteter OSError wurde nicht geworfen")
            except OSError:
                pass
        assert list((env.run_dir / "completion").glob("*__final.json")) == [], \
            "vor der nachgeholten Finalisierung darf noch kein __final-Marker existieren"
        before_rounds = json.loads((env.states_dir / "sniper.json").read_text())["rounds_played"]

        lobby2 = rooms.Lobby(env.run_dir)
        table2 = rooms.Table.load(env.run_dir, table.table_id)
        retry = rooms.complete_section(lobby2, table2, "section-nb-c-crash", saves, env.states_dir)
        assert retry.success
        disk = rooms.Table.load(env.run_dir, table.table_id)
        assert disk.status == "closed"
        assert all(lobby2.is_locked(table2.chrononaut_ids[pk]) is None for pk in table2.members)
        after_rounds = json.loads((env.states_dir / "sniper.json").read_text())["rounds_played"]
        assert after_rounds == before_rounds, "Retry darf bereits geschriebene Mitglieder nicht doppelt fortschreiben"

    with TmpEnv() as env:
        for pk in ["sniper", "tech"]:
            env.lobby.join(pk)
        a, _ = rooms.create_table_from_offer_log(env.lobby, "t-nb-c-first", _offer_events("table2_pair"), cids)
        stub = sl_stub.SLStub(SL_CANNED_SRC / "table2_pair.json")
        done = section.run_section(
            env.lobby, a, stub, "section-nb-c-first", _initial_saves(["sniper", "tech"]), env.states_dir)
        assert done.completion.success
        old = rooms.load_current_save(env.run_dir, "sniper")
        assert old is not None

        b, _ = rooms.create_table_from_offer_log(env.lobby, "t-nb-c-second", _offer_events("table2_pair"), cids)
        next_saves = copy.deepcopy(done.harvested)
        next_saves["sniper"]["save_id"] = "SYNTHETIC-NB-C-NEXT-SNIPER"
        target = env.run_dir / "current_saves" / "sniper.json"
        real_write_text = Path.write_text

        def torn_write(self_path, data, *a, **kw):
            if self_path == target:
                real_write_text(self_path, '{"v":', *a, **kw)
                raise OSError("SIMULATED partial filesystem write")
            return real_write_text(self_path, data, *a, **kw)

        with patch.object(Path, "write_text", new=torn_write):
            try:
                rooms.complete_section(env.lobby, b, "section-nb-c-second", next_saves, env.states_dir)
                raise AssertionError("erwarteter OSError wurde nicht geworfen")
            except OSError:
                pass
        loaded = rooms.load_current_save(env.run_dir, "sniper")
        assert loaded == old, "nach einem abgerissenen Direktschreiben muss der letzte gueltige Save lesbar bleiben"


# ── Testfall 12: NB-D/R4+R6 — stale Handle, closed/consent-join, Absprache ─────

def test_12_nb_d_stale_handle_closed_paths_and_consent_join():
    """NB-D/R4+R6 (Tests 06+07+08 der externen Re-Review, Auflage 3):
    - Ein VOR Abschluss geladenes ("stale") Table-Handle darf einen inzwischen
      persistiert geschlossenen Tisch weder per submit_to_sl weiterbespielen
      noch per complete_section erneut abschliessen (persistierter, nicht der
      veraltete in-memory Status ist massgeblich).
    - Ein bereits geschlossener Tisch nimmt keinen `join_more`-Beitritt an.
    - Ein aktiver Tisch ohne legitimierenden Konsens-/Offer-Beleg nimmt
      ebenso keinen `join_more`-Beitritt an (Nachbeitritt in diesem Slice
      generell nicht unterstuetzt, D3).
    - `post_table_message` lehnt Versand an einen geschlossenen Tisch ab
      (Auflage 3).
    """
    cids = _chrononaut_ids()
    with TmpEnv() as env:
        for pk in LOBBY8:
            env.lobby.join(pk)
        old, _ = rooms.create_table_from_offer_log(env.lobby, "t-nb-d-old", _offer_events("table2_pair"), cids)
        stale = rooms.Table.load(env.run_dir, "t-nb-d-old")
        stub = sl_stub.SLStub(SL_CANNED_SRC / "table2_pair.json")
        done = section.run_section(
            env.lobby, old, stub, "section-nb-d-old", _initial_saves(["sniper", "tech"]), env.states_dir)
        assert done.completion.success

        new, _ = rooms.create_table_from_offer_log(env.lobby, "t-nb-d-new", _offer_events("table2_pair"), cids)
        assert new is not None, "nach Abschluss/Rueckkehr muessen die Locks fuer einen neuen Tisch frei sein"

        fresh_stub = sl_stub.SLStub(SL_CANNED_SRC / "table2_pair.json")
        try:
            rooms.submit_to_sl(stale, stale.leader, fresh_stub, 0, "veraltetes Handle darf nicht senden")
            raise AssertionError("stale-Handle-Versand haette abgelehnt werden muessen")
        except rooms.TableClosedError:
            pass

        stale_result = rooms.complete_section(env.lobby, stale, "section-nb-d-stale", done.harvested, env.states_dir)
        assert stale_result.success is False, "stale-Handle-Abschluss haette abgelehnt werden muessen"

        loaded_closed = rooms.Table.load(env.run_dir, old.table_id)
        admitted_closed = loaded_closed.join_more("medic", cids["medic"])
        assert admitted_closed is False
        assert "medic" not in rooms.Table.load(env.run_dir, old.table_id).members

        active, _ = rooms.create_table_from_offer_log(env.lobby, "t-nb-d-active", _offer_events("medic_solo"), cids)
        admitted_active = active.join_more("scout", cids["scout"])
        assert admitted_active is False
        assert "scout" not in rooms.Table.load(env.run_dir, active.table_id).members

        try:
            rooms.post_table_message(
                rooms.Table.load(env.run_dir, old.table_id), "sniper", "darf nicht mehr gesendet werden")
            raise AssertionError("post_table_message an geschlossenen Tisch haette abgelehnt werden muessen")
        except rooms.TableClosedError:
            pass


# ── Testfall 13: NB-B/Konsistenz-Nachzug — Negations-/Zitat-Marker + cross-table __final ──

def _synthetic_stub_path(run_dir: Path, name: str, members: list[str], debrief_text: str) -> Path:
    """Baut eine synthetische SLStub-Fixture (SIMULIERT, kein echter Provider):
    ein Import-Turn je Mitglied, danach der zu prüfende Debrief-Text."""
    path = run_dir / f"{name}.json"
    path.write_text(json.dumps({
        "_fixture_note": "SIMULIERT/Konsistenz-Nachzug-Test, kein echter Playtest",
        "turns": [{"content": "Import bestaetigt."} for _ in members] + [{"content": debrief_text}],
    }, ensure_ascii=False))
    return path


def test_13_nb_b_negation_quote_marker_and_cross_table_final():
    """NB-B (Konsistenzplan Frage 1, Test 02/03 der externen Re-Review): ein
    verneinter ("NICHT " + Marker) oder zitierter ("> " + Marker) Token auf
    eigener Zeile ist KEIN Zeilenbeginn-Ereignis -> kein Abschluss, auch wenn
    ein gueltiger table_id=/section_id=-Qualifier direkt danach folgt. Deckt
    zusaetzlich (NB-B/NB-C, Test 07) ab, dass ein fremder Tisch mit
    IDENTISCHER section_id niemals den Abschluss eines anderen Tisches erbt
    (`__final`-Inhalt fuehrt table_id, Kollision -> success=False)."""
    cids = _chrononaut_ids()

    # Direkte Marker-Pruefung: Negation/Zitat auf eigener Zeile, mit ansonsten
    # GUELTIGEM Qualifier direkt im Anschluss -> muss trotzdem scheitern.
    negated = "NICHT " + section.COMPLETION_MARKER + " table_id=neg-table section_id=neg-section"
    assert section._completion_marker_matches(negated, "neg-table", "neg-section") is False, \
        "ein verneinter Marker (auch mit passenden Qualifiern) darf nicht als Abschluss zaehlen"

    quoted = "Historisches Zitat:\n> " + section.COMPLETION_MARKER + " table_id=q-table section_id=q-section"
    assert section._completion_marker_matches(quoted, "q-table", "q-section") is False, \
        "ein zitierter Marker (auch mit passenden Qualifiern) darf nicht als Abschluss zaehlen"

    # Ein FRUEHERES ungueltiges Vorkommen darf ein SPAETERES gueltiges nicht
    # verdecken (Plan-Critic-Auflage 5: alle Vorkommen pruefen).
    mixed = "NICHT " + section.COMPLETION_MARKER + "\nGut gemacht.\n" + section.COMPLETION_MARKER
    assert section._completion_marker_matches(mixed, "any-table", "any-section") is True, \
        "ein spaeteres GUELTIGES Vorkommen muss trotz frueherem ungueltigen Vorkommen zaehlen"

    # End-to-end via run_section: negierter Marker darf keinen Abschluss/Rundenfortschritt ausloesen.
    with TmpEnv() as env:
        for pk in ["sniper", "tech"]:
            env.lobby.join(pk)
        table, _ = rooms.create_table_from_offer_log(env.lobby, "t-nb-b-negation", _offer_events("table2_pair"), cids)
        text = ("NICHT " + section.COMPLETION_MARKER + f" table_id={table.table_id} section_id=section-13-negation\n"
                + "Kein neuer Abschnitt abgeschlossen, nur Einstiegsdaten.")
        stub = sl_stub.SLStub(_synthetic_stub_path(env.run_dir, "negation-fixture", table.members, text))
        res = section.run_section(env.lobby, table, stub, "section-13-negation", _initial_saves(table.members), env.states_dir)
        assert res.completion.success is False, "verneinter Marker darf run_section nicht abschliessen lassen"
        sniper_state = json.loads((env.states_dir / "sniper.json").read_text())
        assert sniper_state["rounds_played"] == 0, "kein Rundenfortschritt bei verneintem Marker"

    # Cross-table __final: Tisch A schliesst ab, Tisch B (andere Mitglieder,
    # gleiche section_id) darf den Abschluss von A nicht erben.
    with TmpEnv() as env:
        for pk in LOBBY8:
            env.lobby.join(pk)
        a, _ = rooms.create_table_from_offer_log(env.lobby, "t-nb-final-a", _offer_events("table2_pair"), cids)
        stub_a = sl_stub.SLStub(SL_CANNED_SRC / "table2_pair.json")
        done_a = section.run_section(env.lobby, a, stub_a, "shared-section-id", _initial_saves(["sniper", "tech"]), env.states_dir)
        assert done_a.completion.success

        b, _ = rooms.create_table_from_offer_log(env.lobby, "t-nb-final-b", _offer_events("medic_solo"), cids)
        stub_b = sl_stub.SLStub(SL_CANNED_SRC / "medic_solo.json")
        done_b = section.run_section(env.lobby, b, stub_b, "shared-section-id", _initial_saves(["medic"]), env.states_dir)
        assert done_b.completion.success is False, "Tisch B darf den Abschluss von Tisch A (gleiche section_id) nicht erben"
        assert done_b.completion.already_completed is False, "Kollision ist kein already_completed fuer Tisch B"
        medic_state = json.loads((env.states_dir / "medic.json").read_text())
        assert medic_state["rounds_played"] == 0, "medic darf durch die Kollision nicht fortgeschrieben werden"
        assert rooms.load_current_save(env.run_dir, "medic") is None, "medic darf keinen Save durch die Kollision erhalten"
        assert rooms.Table.load(env.run_dir, "t-nb-final-b").status == "active", \
            "Tisch B bleibt nach der Kollisionsablehnung aktiv (kein falscher Abschluss)"


# ── Testfall 14: NB-C/Konsistenz-Nachzug — closed-vor-final-Recovery, torn Save+State-Paar, Ernte-Pinning ──

def test_14_nb_c_recovery_torn_state_pair_and_harvest_pinning():
    """NB-C (Konsistenzplan Fragen 3/4, Test 04/05/08 der externen Re-Review):
    - Crasht die Finalisierung GENAU beim `__final`-Write, bleibt der Tisch
      auf der Platte AKTIV (nicht closed) und ohne `__final` -- ein Retry muss
      Locks/Finalisierung nachholen (`__final` UND `status=closed` danach),
      ohne bereits geschriebene Mitglieder erneut fortzuschreiben.
    - Reisst der DIREKTE Save-Schreibvorgang eines NOCH NICHT geschriebenen
      Mitglieds ab, bleiben SOWOHL der aktuelle Save ALS AUCH der
      persona_state fuer dieses Mitglied auf dem alten Stand (kein "alter
      Save + bereits fortgeschriebener State").
    - Ein Retry mit ABWEICHENDER Ernte nutzt die BEI DER ERSTEN Validierung
      gepinnte Ernte weiter, nicht das neue (abweichende) Argument.
    """
    cids = _chrononaut_ids()

    # closed-vor-final-Recovery
    with TmpEnv() as env:
        for pk in ["sniper", "tech"]:
            env.lobby.join(pk)
        table, _ = rooms.create_table_from_offer_log(env.lobby, "t-nb-c-recovery", _offer_events("table2_pair"), cids)
        saves = _initial_saves(["sniper", "tech"])
        final_path = rooms._completion_final_path(env.run_dir, "section-14-recovery")
        real_write_text = Path.write_text

        def fail_final(self_path, data, *a, **kw):
            if self_path == final_path:
                raise OSError("SIMULATED crash exactly at __final write")
            return real_write_text(self_path, data, *a, **kw)

        with patch.object(Path, "write_text", new=fail_final):
            try:
                rooms.complete_section(env.lobby, table, "section-14-recovery", saves, env.states_dir)
                raise AssertionError("erwarteter OSError wurde nicht geworfen")
            except OSError:
                pass

        before = rooms.Table.load(env.run_dir, table.table_id)
        assert before.status == "active", "vor der nachgeholten Finalisierung bleibt der Tisch aktiv (nicht closed)"
        assert not final_path.exists(), "vor der nachgeholten Finalisierung darf __final noch nicht existieren"
        assert all(env.lobby.is_locked(table.chrononaut_ids[pk]) is None for pk in table.members), \
            "Locks sind bereits vor __final freigegeben (Reihenfolge: Locks -> __final -> closed)"

        lobby2 = rooms.Lobby(env.run_dir)
        retry = rooms.complete_section(lobby2, before, "section-14-recovery", saves, env.states_dir)
        assert retry.success
        after = rooms.Table.load(env.run_dir, table.table_id)
        assert after.status == "closed" and final_path.exists(), "Retry muss __final UND status=closed nachholen"

    # torn Save+State-Paar (beide bleiben alt)
    with TmpEnv() as env:
        for pk in ["sniper", "tech"]:
            env.lobby.join(pk)
        a, _ = rooms.create_table_from_offer_log(env.lobby, "t-nb-c-pair-first", _offer_events("table2_pair"), cids)
        stub = sl_stub.SLStub(SL_CANNED_SRC / "table2_pair.json")
        done = section.run_section(env.lobby, a, stub, "section-14-pair-first", _initial_saves(["sniper", "tech"]), env.states_dir)
        assert done.completion.success
        old_save = rooms.load_current_save(env.run_dir, "sniper")
        old_state = json.loads((env.states_dir / "sniper.json").read_text())

        b, _ = rooms.create_table_from_offer_log(env.lobby, "t-nb-c-pair-second", _offer_events("table2_pair"), cids)
        next_saves = copy.deepcopy(done.harvested)
        next_saves["sniper"]["save_id"] = "SYNTHETIC-NB-C-PAIR-SNIPER"
        target = env.run_dir / "current_saves" / "sniper.json"
        real_write_text = Path.write_text

        def torn_write(self_path, data, *a, **kw):
            if self_path == target:
                real_write_text(self_path, '{"v":', *a, **kw)
                raise OSError("SIMULATED torn direct save write")
            return real_write_text(self_path, data, *a, **kw)

        with patch.object(Path, "write_text", new=torn_write):
            try:
                rooms.complete_section(env.lobby, b, "section-14-pair-second", next_saves, env.states_dir)
                raise AssertionError("erwarteter OSError wurde nicht geworfen")
            except OSError:
                pass

        current_save = rooms.load_current_save(env.run_dir, "sniper")
        current_state = json.loads((env.states_dir / "sniper.json").read_text())
        assert current_save == old_save, "Save muss nach abgerissenem Direktschreiben beim letzten gueltigen Stand bleiben"
        assert current_state == old_state, \
            "persona_state darf bei abgerissenem Save-Commit NICHT fortgeschrieben werden (Save+State bleiben als Paar alt)"

    # harvest-drift-Pinning: Retry mit abweichender Ernte darf nicht mischen
    with TmpEnv() as env:
        for pk in ["sniper", "tech"]:
            env.lobby.join(pk)
        table, _ = rooms.create_table_from_offer_log(env.lobby, "t-nb-c-drift", _offer_events("table2_pair"), cids)
        initial = copy.deepcopy(_initial_saves(["sniper", "tech"]))
        real_save_state = rooms.ps.save_state

        def stop_at_tech(pk, *a, **kw):
            if pk == "tech":
                raise OSError("SIMULATED crash after sniper guard, before tech state")
            return real_save_state(pk, *a, **kw)

        with patch.object(rooms.ps, "save_state", new=stop_at_tech):
            try:
                rooms.complete_section(env.lobby, table, "section-14-drift", initial, env.states_dir)
                raise AssertionError("erwarteter OSError wurde nicht geworfen")
            except OSError:
                pass

        changed = copy.deepcopy(initial)
        changed["sniper"]["save_id"] = "RETRY-DRIFT-SNIPER"
        changed["tech"]["save_id"] = "RETRY-DRIFT-TECH"
        retry = rooms.complete_section(rooms.Lobby(env.run_dir), rooms.Table.load(env.run_dir, table.table_id),
                                        "section-14-drift", changed, env.states_dir)
        current = {pk: rooms.load_current_save(env.run_dir, pk) for pk in table.members}
        assert not retry.success or current == initial, \
            "Retry mit abweichender Ernte darf die urspruenglich gepinnte Ernte nicht mischen"


# ── Testfall 15: NB-D/Konsistenz-Nachzug — stale Handle darf sl_log nicht loeschen ──

def test_15_nb_d_stale_handle_preserves_sl_log_on_table_message():
    """NB-D (Konsistenzplan Frage 5, Test 06 der externen Re-Review):
    submit_to_sl/post_table_message muessen reload->append->persist auf dem
    PERSISTIERTEN Tisch ausfuehren -- ein sequenziell aelteres, aktives
    ("stale") Table-Handle, das NACH einem submit_to_sl ueber ein frisches
    Handle einen Tisch-Absprache-Post absetzt, darf den bereits persistierten
    sl_log NICHT durch einen veralteten Voll-Snapshot loeschen."""
    cids = _chrononaut_ids()
    with TmpEnv() as env:
        for pk in ["sniper", "tech"]:
            env.lobby.join(pk)
        fresh, _ = rooms.create_table_from_offer_log(env.lobby, "t-nb-d-msg", _offer_events("table2_pair"), cids)
        stale = rooms.Table.load(env.run_dir, "t-nb-d-msg")

        stub = sl_stub.SLStub(SL_CANNED_SRC / "table2_pair.json")
        rooms.submit_to_sl(fresh, fresh.leader, stub, 0, "SIMULIERT: freigegebener Leader-Text")
        before = rooms.Table.load(env.run_dir, "t-nb-d-msg")
        assert len(before.sl_log) == 1

        rooms.post_table_message(stale, "tech", "SIMULIERT: Tischabsprache ueber aelteres Handle")
        after = rooms.Table.load(env.run_dir, "t-nb-d-msg")
        assert after.sl_log == before.sl_log, \
            "ein sequenziell aelteres Handle darf den persistierten sl_log beim Posten nicht loeschen"
        assert [m["from"] for m in after.table_messages] == ["tech"], \
            "die Tischabsprache selbst muss trotzdem persistiert werden"


# ── Testfall 16: K3 — "=false"-Suffix am Marker ist kein positives Ereignis ─────

def test_16_k3_suffix_marker_is_rejected():
    """K3/NB-B (Test 02 der externen K-Re-Review): ein Suffix OHNE trennenden
    Whitespace direkt am Markertoken (`COMPLETION_MARKER + "=false"` als EIN
    Token) darf NICHT als positives Abschluss-Ereignis zaehlen, selbst wenn
    ansonsten gueltige `table_id=`/`section_id=`-Qualifier folgen. Nur
    `tokens[0] == COMPLETION_MARKER` EXAKT ist ein gueltiger Markerbeginn."""
    cids = _chrononaut_ids()
    with TmpEnv() as env:
        for pk in ["sniper", "tech"]:
            env.lobby.join(pk)
        table, _ = rooms.create_table_from_offer_log(env.lobby, "t-k3-suffix", _offer_events("table2_pair"), cids)
        text = (section.COMPLETION_MARKER + f"=false table_id={table.table_id} section_id=section-16-suffix")
        assert section._completion_marker_matches(text, table.table_id, "section-16-suffix") is False, \
            "ein an das Markertoken angehaengtes '=false'-Suffix darf kein positives Ereignis sein"

        stub = sl_stub.SLStub(_synthetic_stub_path(env.run_dir, "k3-suffix-fixture", table.members, text))
        res = section.run_section(env.lobby, table, stub, "section-16-suffix", _initial_saves(table.members), env.states_dir)
        assert res.completion.success is False, "run_section darf bei '=false'-Suffix nicht abschliessen"
        sniper_state = json.loads((env.states_dir / "sniper.json").read_text())
        assert sniper_state["rounds_played"] == 0, "kein Rundenfortschritt bei '=false'-Suffix-Marker"


# ── Testfall 17: K1 — State-Schreibfehler haelt Save UND State gemeinsam alt ────

def test_17_k1_new_save_old_state_stays_consistent_on_state_write_failure():
    """K1/NB-C: schlaegt der State-Publish (`ps.save_state`, der EINZIGE
    Veroeffentlichungs-Flip) fehl, NACHDEM die neue Save-Version bereits
    atomar committet wurde, darf KEIN Leser eine gemischte Generation sehen —
    `load_current_save` UND `rooms.ps.load_state` muessen beide weiterhin die
    VOLLSTAENDIGE alte Generation liefern (kein "neuer Save + alter State")."""
    cids = _chrononaut_ids()
    with TmpEnv() as env:
        for pk in ["sniper", "tech"]:
            env.lobby.join(pk)
        first, _ = rooms.create_table_from_offer_log(env.lobby, "t-k1-first", _offer_events("table2_pair"), cids)
        stub = sl_stub.SLStub(SL_CANNED_SRC / "table2_pair.json")
        done = section.run_section(env.lobby, first, stub, "section-17-first", _initial_saves(["sniper", "tech"]), env.states_dir)
        assert done.completion.success
        before_save = rooms.load_current_save(env.run_dir, "sniper")
        before_state = rooms.ps.load_state("sniper", env.states_dir)

        second, _ = rooms.create_table_from_offer_log(env.lobby, "t-k1-second", _offer_events("table2_pair"), cids)
        next_saves = copy.deepcopy(done.harvested)
        next_saves["sniper"]["save_id"] = "SYNTHETIC-K1-NEXT-SNIPER"
        real_save_state = rooms.ps.save_state

        def fail_sniper_state(pk, *a, **kw):
            if pk == "sniper":
                raise OSError("SIMULATED state publish failure after save-version commit")
            return real_save_state(pk, *a, **kw)

        with patch.object(rooms.ps, "save_state", new=fail_sniper_state):
            try:
                rooms.complete_section(env.lobby, second, "section-17-second", next_saves, env.states_dir)
                raise AssertionError("erwarteter OSError wurde nicht geworfen")
            except OSError:
                pass

        after_save = rooms.load_current_save(env.run_dir, "sniper")
        after_state = rooms.ps.load_state("sniper", env.states_dir)
        assert after_save == before_save, \
            "load_current_save darf nach fehlgeschlagenem State-Publish keine neue Save-Version zeigen"
        assert after_state == before_state, \
            "persona_state darf nach fehlgeschlagenem eigenen Publish nicht fortgeschrieben sein"


# ── Testfall 18: K2 — offener Abschluss-Auftrag blockiert zweiten Abschnitt ─────

def test_18_k2_pending_completion_order_blocks_second_section():
    """K2/NB-C+D (Tests 04/05 der externen K-Re-Review): ein noch OFFENER
    Abschluss-Auftrag (`__plan.json` fuer section A ohne eigenes `__final`)
    bindet den Tisch EXKLUSIV — ein zweiter Abschnitt B am selben Tisch muss
    bereits am allerersten `submit_to_sl`-Aufruf (Leader-Anker) mit einer
    ECHTEN `rooms.TableClosedError`-Unterklasse scheitern (nicht mit einem
    blossen `PermissionError`, sonst faengt das schmale `except
    (TableClosedError, ValueError)` der Oracle-Tests die Ablehnung nicht)."""
    cids = _chrononaut_ids()
    with TmpEnv() as env:
        for pk in ["sniper", "tech"]:
            env.lobby.join(pk)
        table, _ = rooms.create_table_from_offer_log(env.lobby, "t-k2-pending", _offer_events("table2_pair"), cids)
        pending = _initial_saves(["sniper", "tech"])
        real_save_state = rooms.ps.save_state

        def fail_sniper_state(pk, *a, **kw):
            if pk == "sniper":
                raise OSError("SIMULATED pending completion for section-18-pending-A")
            return real_save_state(pk, *a, **kw)

        with patch.object(rooms.ps, "save_state", new=fail_sniper_state):
            try:
                section.run_section(env.lobby, table, sl_stub.SLStub(SL_CANNED_SRC / "table2_pair.json"),
                                     "section-18-pending-A", pending, env.states_dir)
                raise AssertionError("erwarteter OSError wurde nicht geworfen")
            except OSError:
                pass
        assert list((env.run_dir / "completion").glob("*__plan.json")), \
            "ein offener Abschluss-Auftrag (__plan.json ohne __final) muss existieren"
        assert list((env.run_dir / "completion").glob("*__final.json")) == [], \
            "section-18-pending-A darf noch nicht finalisiert sein"

        reloaded = rooms.Table.load(env.run_dir, table.table_id)
        try:
            section.run_section(env.lobby, reloaded, sl_stub.SLStub(SL_CANNED_SRC / "table2_pair.json"),
                                 "section-18-branch-B", _initial_saves(["sniper", "tech"]), env.states_dir)
            raise AssertionError("ein zweiter Abschnitt auf einem Tisch mit offenem Auftrag haette scheitern muessen")
        except rooms.TableClosedError:
            pass
        assert isinstance(rooms.TablePendingError(""), rooms.TableClosedError), \
            "TablePendingError muss eine echte TableClosedError-Unterklasse sein (Auflage 1)"

        # complete_section() DIREKT fuer ein ANDERES section_id auf demselben
        # Tisch muss ebenso hart abgelehnt werden (success=False, kein Write).
        direct = rooms.complete_section(env.lobby, reloaded, "section-18-branch-direct",
                                         _initial_saves(["sniper", "tech"]), env.states_dir)
        assert direct.success is False, \
            "complete_section darf fuer ein anderes section_id auf einem Tisch mit offenem Auftrag nicht erfolgreich sein"


# ── Testfall 19: P1/K2-Nachzug — offener Auftrag bindet Mitglieder gegen NEUE Tische ──

def test_19_p1_open_completion_order_blocks_new_table_admission():
    """P1/K2-Nachzug (Restkorrektur, boundaries-02/Admission-Matrix): ein
    Mitglied, dessen Chrononaut-Lock im Cleanup bereits freigegeben wurde
    (erste Freigabe in der Schleife erfolgt VOR einer injizierten zweiten),
    aber dessen urspruenglicher Abschluss-Auftrag noch OFFEN ist
    (`__plan.json` ohne eigenes `__final`), darf trotzdem nicht an einem
    NEUEN Tisch aufgenommen werden — `_member_bound_by_open_order` bindet an
    Plan-/Final-Dateiexistenz, NICHT am physischen Lock. Nach gueltigem
    `__final` ist der Auftrag geschlossen; freie Neugruppierung ist wieder
    moeglich."""
    cids = _chrononaut_ids()
    with TmpEnv() as env:
        for pk in ["sniper", "tech"]:
            env.lobby.join(pk)
        table, _ = rooms.create_table_from_offer_log(env.lobby, "t-p1-origin", _offer_events("table2_pair"), cids)
        saves = _initial_saves(["sniper", "tech"])

        real_release = rooms.Lobby.release_chrononaut

        def fail_second(self, cid, owner):
            if cid == table.chrononaut_ids["tech"]:
                raise OSError("SIMULATED crash before second lock release")
            return real_release(self, cid, owner)

        with patch.object(rooms.Lobby, "release_chrononaut", new=fail_second):
            try:
                rooms.complete_section(env.lobby, table, "section-19-origin", saves, env.states_dir)
                raise AssertionError("erwarteter OSError wurde nicht geworfen")
            except OSError:
                pass

        assert env.lobby.is_locked(table.chrononaut_ids["sniper"]) is None, \
            "sniper-Lock muss bereits freigegeben sein (erste Freigabe erfolgt vor der injizierten zweiten)"
        assert list((env.run_dir / "completion").glob("*__final.json")) == [], \
            "vor der nachgeholten Finalisierung darf noch kein __final existieren"

        # sniper ist lock-frei, aber weiterhin am offenen Auftrag gebunden ->
        # Aufnahme an einem NEUEN Tisch muss abgelehnt werden.
        events = [{"type": "offer", "id": "p1-follow", "from": "sniper", "wants": []}]
        follow, _ = rooms.create_table_from_offer_log(env.lobby, "t-p1-follow", events, cids)
        assert follow is None, \
            "ein lock-freies, aber noch am offenen Auftrag gebundenes Mitglied darf keinen neuen Tisch bilden"
        assert not (env.run_dir / "tables" / "t-p1-follow.json").exists()

        # Retry holt die Finalisierung nach.
        lobby2 = rooms.Lobby(env.run_dir)
        table2 = rooms.Table.load(env.run_dir, table.table_id)
        retry = rooms.complete_section(lobby2, table2, "section-19-origin", saves, env.states_dir)
        assert retry.success

        # Nach __final ist der Auftrag geschlossen -> freie Neugruppierung wieder moeglich.
        follow2, _ = rooms.create_table_from_offer_log(env.lobby, "t-p1-follow-2", events, cids)
        assert follow2 is not None and follow2.members == ["sniper"], \
            "nach gueltigem __final muss freie Neugruppierung wieder moeglich sein"


# ── Testfall 20: P2/NB-B,K2-Nachzug — Section-ID-Grammatik + Final-Identitaet ──

def test_20_p2_section_id_grammar_and_final_identity():
    """P2/Auflage 3 (Restkorrektur, boundaries-03): ein `section_id` mit
    unzulaessigen Zeichen (z. B. "/") wird SOWOHL beim direkten
    `complete_section`-Aufruf (umgeht `run_section`) ALS AUCH via
    `run_section` frueh kontrolliert abgelehnt (`success=False`, keine
    Datei). Zusaetzlich prueft der `__final`-Inhalt beim Lesen `table_id`
    UND `section_id` — ein table_id-passender, aber section_id-abweichender
    `__final`-Marker darf NICHT als `already_completed` durchgehen
    (Kollision)."""
    cids = _chrononaut_ids()

    with TmpEnv() as env:
        for pk in ["sniper", "tech"]:
            env.lobby.join(pk)
        table, _ = rooms.create_table_from_offer_log(env.lobby, "t-p2-grammar", _offer_events("table2_pair"), cids)

        direct = rooms.complete_section(
            env.lobby, table, "chapter/one", _initial_saves(["sniper", "tech"]), env.states_dir)
        assert direct.success is False, "'/' im section_id muss auch beim Direktaufruf abgelehnt werden"
        assert list((env.run_dir / "completion").glob("*")) == [], "kein Datei-Write bei Grammatik-Reject"

        stub = sl_stub.SLStub(SL_CANNED_SRC / "table2_pair.json")
        res = section.run_section(
            env.lobby, table, stub, "chapter/one", _initial_saves(["sniper", "tech"]), env.states_dir)
        assert res.completion.success is False, "run_section darf ein unzulaessiges section_id nicht abschliessen lassen"
        assert list((env.run_dir / "completion").glob("*")) == [], \
            "kein Datei-Write bei Grammatik-Reject via run_section"
        sniper_state = json.loads((env.states_dir / "sniper.json").read_text())
        assert sniper_state["rounds_played"] == 0, "kein Rundenfortschritt bei Grammatik-Reject"

    with TmpEnv() as env:
        for pk in ["sniper", "tech"]:
            env.lobby.join(pk)
        table, _ = rooms.create_table_from_offer_log(
            env.lobby, "t-p2-final-identity", _offer_events("table2_pair"), cids)
        stub = sl_stub.SLStub(SL_CANNED_SRC / "table2_pair.json")
        done = section.run_section(
            env.lobby, table, stub, "section-20-real", _initial_saves(["sniper", "tech"]), env.states_dir)
        assert done.completion.success

        final_path = rooms._completion_final_path(env.run_dir, "section-20-real")
        final_data = json.loads(final_path.read_text())
        assert final_data["section_id"] == "section-20-real"
        tampered = dict(final_data)
        tampered["section_id"] = "section-20-other"
        final_path.write_text(json.dumps(tampered))

        reloaded = rooms.Table.load(env.run_dir, table.table_id)
        result = rooms.complete_section(
            env.lobby, reloaded, "section-20-real", _initial_saves(["sniper", "tech"]), env.states_dir)
        assert result.success is False, \
            "table_id-Treffer allein darf ohne passenden section_id nicht already_completed liefern"
        assert result.already_completed is False, "Kollision (section_id-Mismatch) ist kein already_completed"


# ── Testfall 21: P3/K3-Nachzug — gefenschte Steuerzeile (```text```) ist kein Ereignis ──

def test_21_p3_fenced_text_block_marker_is_not_an_event():
    """P3/K3-Nachzug (Restkorrektur, boundaries-04): ein Abschluss-Marker,
    der als Protokollbeispiel INNERHALB eines ```text```-Fence steht (nicht
    nur ```json```), darf nicht als echtes Abschluss-Ereignis zaehlen — die
    Fence-Strip-Erweiterung greift VOR der Marker-Suche, unabhaengig vom
    Info-String."""
    cids = _chrononaut_ids()

    fenced = ("Protokollbeispiel, kein Abschlussereignis:\n```text\n"
              + section.COMPLETION_MARKER + " table_id=any-table section_id=any-section\n```")
    assert section._completion_marker_matches(fenced, "any-table", "any-section") is False, \
        "ein Marker innerhalb eines ```text```-Fence darf nicht zaehlen"

    mixed = fenced + "\n" + section.COMPLETION_MARKER
    assert section._completion_marker_matches(mixed, "any-table", "any-section") is True, \
        "ein gueltiger Marker NACH der Fence muss weiterhin zaehlen"

    with TmpEnv() as env:
        for pk in ["sniper", "tech"]:
            env.lobby.join(pk)
        table, _ = rooms.create_table_from_offer_log(env.lobby, "t-p3-fenced", _offer_events("table2_pair"), cids)
        text = ("Protokollbeispiel, kein Abschlussereignis:\n```text\n"
                + section.COMPLETION_MARKER + f" table_id={table.table_id} section_id=section-21-fenced\n```")
        stub = sl_stub.SLStub(_synthetic_stub_path(env.run_dir, "p3-fenced-fixture", table.members, text))
        res = section.run_section(
            env.lobby, table, stub, "section-21-fenced", _initial_saves(table.members), env.states_dir)
        assert res.completion.success is False, "gefenchte Steuerzeile darf run_section nicht abschliessen lassen"
        sniper_state = json.loads((env.states_dir / "sniper.json").read_text())
        assert sniper_state["rounds_played"] == 0, "kein Rundenfortschritt bei gefenchter Steuerzeile"


# ── Testfall 22: P4/K1-Nachzug — run-scope-Ref (fremder run_dir deutet Ref nicht um) ──

def test_22_p4_run_scoped_ref_does_not_alias_across_run_dirs():
    """P4/K1-Nachzug (Restkorrektur, boundaries-05): der Current-Save-Ref ist
    an eine pro `run_dir` stabile `run_id` gebunden. Zwei UNABHAENGIGE
    `run_dir`s, die denselben `states_dir` teilen, duerfen sich NIE
    gegenseitig einen Save umdeuten. Zusaetzlich: dieselbe `run_dir` erhaelt
    bei einer erneuten `Lobby(run_dir)`-Instanziierung dieselbe `run_id`
    (Kontrolle 06)."""
    cids = _chrononaut_ids()
    with TmpEnv() as env:
        for pk in ["sniper", "tech"]:
            env.lobby.join(pk)
        first, _ = rooms.create_table_from_offer_log(env.lobby, "t-p4-first", _offer_events("table2_pair"), cids)
        stub = sl_stub.SLStub(SL_CANNED_SRC / "table2_pair.json")
        done = section.run_section(
            env.lobby, first, stub, "section-22-first", _initial_saves(["sniper", "tech"]), env.states_dir)
        assert done.completion.success
        first_run_id = env.lobby.run_id
        first_save = rooms.load_current_save(env.run_dir, "sniper", env.states_dir)
        assert first_save is not None

        second_run_dir = env.run_dir.parent / "second-run"
        second_lobby = rooms.Lobby(second_run_dir)
        assert second_lobby.run_id != first_run_id, "zwei verschiedene run_dirs muessen verschiedene run_id erhalten"

        aliased = rooms.load_current_save(second_run_dir, "sniper", env.states_dir)
        assert aliased is None, "eine Referenz aus einem fremden run_dir darf im neuen run_dir nichts aufloesen"

        again_lobby = rooms.Lobby(env.run_dir)
        assert again_lobby.run_id == first_run_id, "run_id muss fuer denselben run_dir stabil bleiben"
        assert rooms.load_current_save(env.run_dir, "sniper", env.states_dir) == first_save, \
            "eine erneute Lobby-Instanz auf demselben run_dir muss die eigene Referenz weiterhin aufloesen"


# ── Testfaelle 23–29: P3/K3-Nachzug — Fence-Zustandsmaschine (Reviewfaelle 01–07) ──
# Direkte Entsprechung der Orakelfaelle aus `review_r_fences.py` gegen
# `section._completion_marker_matches` (s. PLAN-FENCE.md/PLAN-CRITIC-R.md).
# Rein additiv: bestehende Assertions/Fixtures/Tests bleiben unangetastet.

def test_23_r_fence_01_bare_and_qualified_marker_matches():
    """Reviewfall 01: ein blanker Top-Level-Marker (aktuelle Session) UND ein
    mit passenden `table_id=`/`section_id=`-Qualifiern versehener Top-Level-
    Marker sind je fuer sich gueltige Abschluss-Ereignisse."""
    bare = section.COMPLETION_MARKER
    assert section._completion_marker_matches(bare, "pair", "fence-case") is True, \
        "ein blanker Top-Level-Marker muss fuer die aktuelle Session zaehlen"

    qualified = section.COMPLETION_MARKER + " table_id=pair section_id=fence-case"
    assert section._completion_marker_matches(qualified, "pair", "fence-case") is True, \
        "ein qualifizierter Top-Level-Marker mit passenden Werten muss zaehlen"


def test_24_r_fence_02_closed_backtick_block_hides_marker():
    """Reviewfall 02: ein Marker, der ausschliesslich INNERHALB eines
    geschlossenen ```text```-Fence-Blocks steht, darf nicht zaehlen."""
    text = "```text\n" + section.COMPLETION_MARKER + "\n```"
    assert section._completion_marker_matches(text, "pair", "fence-case") is False, \
        "ein Marker innerhalb eines geschlossenen Fence-Blocks darf nicht zaehlen"


def test_25_r_fence_03_marker_after_closed_block_matches():
    """Reviewfall 03: nach einem vollstaendig geschlossenen Beispiel-Block
    folgt eine echte Top-Level-Markerzeile — der Zustand muss nach dem
    Schliessen sauber zurueckgesetzt sein, damit dieser spaetere Marker
    zaehlt."""
    text = "```text\n" + section.COMPLETION_MARKER + "\n```\n" + section.COMPLETION_MARKER
    assert section._completion_marker_matches(text, "pair", "fence-case") is True, \
        "ein echter Top-Level-Marker nach einem geschlossenen Beispiel-Block muss zaehlen"


def test_26_r_fence_04_open_block_eof_hides_marker():
    """Reviewfall 04 (Restkorrektur ggue. dem alten Regex-Verhalten): ein bis
    Textende OFFENER Fence-Block verschluckt seine Markerzeile vollstaendig —
    kontrollierte Ablehnung ohne Abschluss, kein Marker wird freigelegt."""
    text = "```text\n" + section.COMPLETION_MARKER
    assert section._completion_marker_matches(text, "pair", "fence-case") is False, \
        "ein bis Textende offener Fence-Block darf seinen Marker nicht freigeben"


def test_27_r_fence_05_tilde_fence_hides_marker():
    """Reviewfall 05 (Restkorrektur): `~~~`-Fences werden gleichwertig zu
    Backtick-Fences behandelt — ein darin eingeschlossener Marker zaehlt
    nicht."""
    text = "~~~text\n" + section.COMPLETION_MARKER + "\n~~~"
    assert section._completion_marker_matches(text, "pair", "fence-case") is False, \
        "ein Marker innerhalb eines geschlossenen ~~~-Fence-Blocks darf nicht zaehlen"


def test_28_r_fence_06_nested_shorter_inner_delimiter_does_not_close_outer():
    """Reviewfall 06 (kritischster Fall): ein laengerer aeusserer ````-Fence
    (Lauflaenge 4) bleibt offen, auch wenn eine kuerzere ```-Delimiterzeile
    (Laenge 3) dazwischen vorbeizieht — der kuerzere innere Delimiter
    schliesst den aeusseren Block NICHT, alles bis zum passenden ````-
    Abschluss bleibt In-Block."""
    text = "````text\n```text\n" + section.COMPLETION_MARKER + "\n```\n````"
    assert section._completion_marker_matches(text, "pair", "fence-case") is False, \
        "ein kuerzerer innerer Delimiter darf einen laengeren aeusseren Block nicht schliessen"


def test_29_r_fence_07_inline_backticks_prose_does_not_open_block():
    """Reviewfall 07 (Restkorrektur, Gegenrichtung): eine Prosazeile mit
    Inline-Backticks, die NICHT mit einem Fence-Lauf BEGINNT, ist keine
    Delimiterzeile und oeffnet daher keinen Block — der nachfolgende echte
    Top-Level-Marker muss weiterhin zaehlen, auch wenn spaeter noch ein
    separater, korrekt geschlossener ```json-Beispielblock folgt."""
    text = ("Prosa mit ```inline\n" + section.COMPLETION_MARKER
            + "\n```json\n" + json.dumps({"example": True}) + "\n```")
    assert section._completion_marker_matches(text, "pair", "fence-case") is True, \
        "Inline-Backticks in einer Prosazeile duerfen einen spaeteren echten Marker nicht verdecken"


TESTS = [
    test_1_table_capacity,
    test_2_channels_and_visibility,
    test_3_dissent_no_artificial_consensus,
    test_4_lifecycle_completion_and_negatives,
    test_5_chrononaut_lock,
    test_6_no_real_provider,
    test_7_message_channels,
    test_8_medic_extra_persona_full_lifecycle,
    test_9_nb_a_receiver_save_reaches_sl,
    test_10_nb_b_marker_qualifiers_and_json_stripping,
    test_11_nb_c_finalize_recovery_and_torn_current_save,
    test_12_nb_d_stale_handle_closed_paths_and_consent_join,
    test_13_nb_b_negation_quote_marker_and_cross_table_final,
    test_14_nb_c_recovery_torn_state_pair_and_harvest_pinning,
    test_15_nb_d_stale_handle_preserves_sl_log_on_table_message,
    test_16_k3_suffix_marker_is_rejected,
    test_17_k1_new_save_old_state_stays_consistent_on_state_write_failure,
    test_18_k2_pending_completion_order_blocks_second_section,
    test_19_p1_open_completion_order_blocks_new_table_admission,
    test_20_p2_section_id_grammar_and_final_identity,
    test_21_p3_fenced_text_block_marker_is_not_an_event,
    test_22_p4_run_scoped_ref_does_not_alias_across_run_dirs,
    test_23_r_fence_01_bare_and_qualified_marker_matches,
    test_24_r_fence_02_closed_backtick_block_hides_marker,
    test_25_r_fence_03_marker_after_closed_block_matches,
    test_26_r_fence_04_open_block_eof_hides_marker,
    test_27_r_fence_05_tilde_fence_hides_marker,
    test_28_r_fence_06_nested_shorter_inner_delimiter_does_not_close_outer,
    test_29_r_fence_07_inline_backticks_prose_does_not_open_block,
]


def main() -> int:
    failures = 0
    for t in TESTS:
        name = t.__name__
        try:
            t()
            print(f"OK   {name}")
        except Exception:  # noqa: BLE001 — Testrunner soll alle Faelle sammeln
            failures += 1
            print(f"FAIL {name}")
            traceback.print_exc()
    total = len(TESTS)
    print(f"\n{total - failures}/{total} Tests bestanden.")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
