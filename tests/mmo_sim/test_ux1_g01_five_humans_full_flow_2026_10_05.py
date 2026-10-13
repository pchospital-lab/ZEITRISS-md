#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_g01_five_humans_full_flow_2026_10_05.py — UX08
(ZEITRISS Terminal UX-1 Wiederanlauf, 02 §D.5/§Auftrag A24, REVIEW.md §G01/
§G06: "Die selbst berichtete vollstaendige 5-Menschen- ... Mischrunde
fehlt" / "Ein Dummy-Tisch ... ist kein bestandener Mehrpersonentest").

ECHTER durchgaengiger Nachweis fuer FUeNF MENSCHEN (0 KI) an einem
gemeinsamen Terminal: ein echter, eigenstaendiger Subprozess gegen den
tatsaechlichen Einstiegspunkt `scripts/mmo_sim.py`, der gefuehrte Weg `g`
(`_cmd_local_round_setup`) mit vier weiteren bereits registrierten
Menschen, ECHTE Eingabeuebergabe (jeder tatsaechliche Akteurwechsel --
Einrichtung, Beitrittsbestaetigung, Spielzug, Reflexion -- verlangt eine
eigene bewusste Uebernahme, `mmo_sim/ui/tui.py:_local_round_handoff`/
`_HumanDriver.decide`), kein sechster Spieler (eigener, getrennter
Negativfall unten, Policy-Ablehnung VOR jeder Tischanlage), kein
Autoplayer (jeder der fuenf Zuege kommt aus einer eigenen, unterscheidbaren
stdin-Zeile dieses EINEN Transkripts -- nicht aus einer Produktheuristik).

Reihenfolge-Hinweis (wie `_a24_local_support.py`): `core.store.
create_table_from_offer_log` bildet `table.members` als `sorted(leader
UNION Gaeste)` -- NICHT Auswahl-/Tokenreihenfolge; menschliche Registry-IDs
werden zur Laufzeit zufaellig erzeugt. Diese Datei berechnet die
tatsaechliche Akteurreihenfolge daher programmatisch (`sorted_guest_order`/
`sorted_table_members`, wiederverwendet aus `_a24_local_support.py`) und
simuliert damit exakt denselben `current_focus_pid`-Uebergabevertrag wie
das Produkt selbst (`_cmd_local_round_setup`s unbedingte Setup-Uebergabe je
Gast, `_cmd_local_round`s bedingte Beitritts-/Spielzug-/Reflexions-
Uebergabe je tatsaechlichem Akteurwechsel) -- keine hartkodierte Zeilenzahl.

Kein KI-Call (0 Personas angefragt): `OPENWEBUI_URL` zeigt auf einen
eigenen Loopback-HTTP-Server (NUR die SL-Seite, kein Persona-Server
noetig). Pure Python, nur `assert`, echter Exitcode, synthetische
Daten/Temp-Dirs."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER  # noqa: E402

import _a24_local_support as sup  # noqa: E402

MMO_SIM = _REPO_ROOT / "scripts" / "mmo_sim.py"


class _SmartGmHandler(BaseHTTPRequestHandler):
    """Reiner SL-Loopback (keine KI-Persona in diesem Fall noetig, UX08 hat
    0 KI-Mitspieler): liefert den Abschlussmarker ERST, sobald alle fuenf
    erwarteten v7-Save-IDs tatsaechlich in irgendeiner bisherigen
    `user`-Nachricht angekommen sind (Muster aus `e2e_real_subprocess_
    dialog.py:_SmartGmHandler`, hier lokal fuer 5 statt 2 Mitglieder)."""

    def log_message(self, *args):
        return

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b""
        try:
            body = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            body = {}
        self.server.calls.append(body)  # type: ignore[attr-defined]
        messages = body.get("messages") or []
        last_user = messages[-1]["content"] if messages else ""
        for blk in zeitriss_saves.extract_all_saves(last_user):
            cid = zeitriss_saves.block_char_id(blk)
            if cid:
                self.server.seen_char_ids.add(cid)  # type: ignore[attr-defined]
        if self.server.expected_char_ids.issubset(self.server.seen_char_ids):  # type: ignore[attr-defined]
            debrief = "\n".join(
                f"```json\n{json.dumps(b, ensure_ascii=False)}\n```" for b in self.server.final_saves.values()  # type: ignore[attr-defined]
            )
            content = (
                f"{debrief}\n{COMPLETION_MARKER} table_id={self.server.table_id} "  # type: ignore[attr-defined]
                f"section_id={self.server.section_id}"  # type: ignore[attr-defined]
            )
        else:
            content = f"Szene {len(self.server.calls)}: Ihr steht bereit. Was tut ihr?"  # type: ignore[attr-defined]
        payload = {"choices": [{"message": {"content": content}}], "usage": {}, "sources": []}
        data = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class SmartGmServer(HTTPServer):
    def __init__(self, final_saves: dict[str, dict], table_id: str, section_id: str):
        super().__init__(("127.0.0.1", 0), _SmartGmHandler)
        self.calls: list[dict] = []
        self.seen_char_ids: set = set()
        self.expected_char_ids = {zeitriss_saves.block_char_id(b) for b in final_saves.values()}
        self.final_saves = final_saves
        self.table_id = table_id
        self.section_id = section_id
        import threading
        self._thread = threading.Thread(target=self.serve_forever, daemon=True)

    @property
    def base_url(self) -> str:
        host, port = self.server_address
        return f"http://{host}:{port}"

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self.shutdown()
        self.server_close()


def run_process(data_dir: Path, participant: str, stdin_text: str, env_extra: dict, timeout: int = 90) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.update(env_extra)
    cmd = [sys.executable, str(MMO_SIM), "--data-dir", str(data_dir), "--participant", participant]
    return subprocess.run(cmd, input=stdin_text, capture_output=True, text=True, env=env, cwd=str(data_dir), timeout=timeout)


def _focus_emit(lines: list, focus_box: list, actor: str, line: str) -> None:
    """Exakt der Produktvertrag (`_local_round_handoff`/`_HumanDriver.
    decide`, beide pruefen dieselbe `current_focus_pid`-Closure-Variable):
    ein tatsaechlicher Akteurwechsel braucht VORHER eine eigene bewusste
    Uebernahme ('j'), danach kommt die eigentliche Zeile dieses Akteurs."""
    if focus_box[0] != actor:
        lines.append("j")
        focus_box[0] = actor
    lines.append(line)


def _build_five_human_transcript(leader_id: str, guest_ids: list[str], reflections: dict[str, str]) -> tuple[list[str], list[str], list[str]]:
    """Baut das VOLLSTAENDIGE stdin-Transkript fuer den gefuehrten Weg `g`
    mit vier weiteren Menschen (0 KI) -- in genau drei Phasen, die dem
    tatsaechlichen Produktablauf entsprechen (s. Moduldocstring):

    1) Setup (`_cmd_local_round_setup`): Modus, sichtbare Auswahl (die
       Registry-Listung ist selbst pid-sortiert, s. `_local_round_list_
       humans`/`_local_round_select_humans` -- identisch zur Sortierung,
       die `core.store.create_table_from_offer_log` fuer `table.members`
       verwendet, daher entspricht 'alle in Listreihenfolge waehlen'
       GENAU `sorted(guest_ids)`), Figurbestaetigung je Mensch (leader
       zuerst, dann die Gaeste in Auswahlreihenfolge), KEINE KI, Leader=du,
       Startwahl bestaetigen, EINE unbedingte Setup-Uebergabe je Gast.
    2) Beitritt + Spiel (`_cmd_local_round`): Beitrittsbestaetigung je
       Gast-Token (Tokenreihenfolge == Auswahlreihenfolge == `sorted_guest_
       order`), dann Leader-Anker-Zug, dann je Gast genau EIN echter
       Importzug (`act()` ruft `table.members`-Reihenfolge = `sorted_guest_
       order` auf) -- danach sind alle fuenf v7-Saves beim SL angekommen,
       der synthetische GM liefert den Abschlussmarker.
    3) Reflexion (`_collect_reflections`, Reihenfolge = `sorted_table_
       members`, NICHT leader-first): je Mitglied eine freiwillige Notiz
       (leer zulaessig)."""
    guests_sorted = sup.sorted_guest_order(leader_id, guest_ids)
    members_sorted = sup.sorted_table_members(leader_id, guest_ids)

    lines: list[str] = ["g", "2", ",".join(str(i + 1) for i in range(len(guests_sorted)))]
    lines.extend("j" for _ in range(1 + len(guests_sorted)))  # Figurbestaetigung: leader + jeder Gast.
    lines.extend(["", ""])  # KI-Auswahl leer, Leaderwahl leer ("du").
    lines.append("j")  # Startwahl bestaetigen.
    lines.extend("j" for _ in guests_sorted)  # Setup-Uebergabe je Gast, unbedingt.

    focus = [guests_sorted[-1]] if guests_sorted else [leader_id]
    for g in guests_sorted:
        _focus_emit(lines, focus, g, "j")  # Beitrittsbestaetigung (Tokenreihenfolge).

    leader_turn = "Wir sichern gemeinsam den Zugang und beobachten die Lage."
    _focus_emit(lines, focus, leader_id, leader_turn)
    guest_turns = {}
    for idx, g in enumerate(guests_sorted, start=1):
        text = f"Ich uebernehme Position {idx} und melde: alles im Blick."
        guest_turns[g] = text
        _focus_emit(lines, focus, g, text)

    for m in members_sorted:
        _focus_emit(lines, focus, m, reflections.get(m, ""))

    lines.append("x")
    return lines, [leader_turn], [guest_turns[g] for g in guests_sorted]


def test_five_real_humans_shared_terminal_full_flow_real_handoff_no_ai():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        registry_dir = root / "registry"
        onboarding_dir = root / "onboarding"
        states_dir = root / "states"
        run_dir = root / "run"
        catalog_dir = root / "catalog"

        names = ["Anke", "Bela", "Cem", "Dora", "Elia"]
        chars = [("CHR-UX08-A", "Anke", "ANKEOPS"), ("CHR-UX08-B", "Bela", "BELAOPS"),
                 ("CHR-UX08-C", "Cem", "CEMOPS"), ("CHR-UX08-D", "Dora", "DORAOPS"),
                 ("CHR-UX08-E", "Elia", "ELIAOPS")]
        participants = [sup.register_human(registry_dir, n) for n in names]
        pids = [p.participant_id for p in participants]
        onbs = [
            sup.onboard_human_figure(registry_dir, pid, onboarding_dir, states_dir, run_dir, *c)
            for pid, c in zip(pids, chars)
        ]
        write_test_profile(run_dir)

        leader_id = pids[0]
        guest_ids = pids[1:]
        final_saves = {pid: onb["save"] for pid, onb in zip(pids, onbs)}
        expected_char_ids = {zeitriss_saves.block_char_id(b) for b in final_saves.values()}
        assert len(expected_char_ids) == 5, "fuenf unterscheidbare Figuren erwartet"

        table_id = sup.compute_table_id(leader_id, guest_ids)
        section_id = f"{table_id}-section"
        end_saves = sup.end_saves_for(final_saves, "ux08")

        stdin_lines, leader_turns, guest_turn_texts = _build_five_human_transcript(
            leader_id, guest_ids, reflections={leader_id: "Notiz: Tisch stand, alle gemeldet."},
        )
        stdin_text = "\n".join(stdin_lines) + "\n"

        with SmartGmServer(end_saves, table_id, section_id) as gm_srv:
            env = {
                "OPENWEBUI_URL": gm_srv.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC_UX08_KEY",
            }
            env.pop("MMO_SIM_PERSONA_CLI", None)

            proc = run_process(root, leader_id, stdin_text, env, timeout=90)

            assert proc.returncode == 0, (
                f"Fuenf-Menschen-Prozess fehlgeschlagen: rc={proc.returncode}\n"
                f"stdout(tail)={proc.stdout[-2000:]}\nstderr(tail)={proc.stderr[-1500:]}"
            )

            # UX08: echte Eingabeuebergabe -- jede bewusste Uebernahme zeigt
            # Name+ID+Figur, und die reale Beitritts-/Zusammenfassungs-
            # Anzeige erscheint tatsaechlich im Transkript.
            assert "Lokale Runde einrichten" in proc.stdout
            assert "Zusammenfassung (5 Spieler einschliesslich Leader)" in proc.stdout, proc.stdout[-1500:]
            assert f"Leader={leader_id}" in proc.stdout
            for pid in guest_ids:
                assert f"Geteiltes Terminal wird an '{pid}'" in proc.stdout, (
                    f"keine sichtbare Uebergabe an '{pid}' im Transkript gefunden"
                )
            assert "Gruppe eingeladen" in proc.stdout
            assert "Abschnitt abgeschlossen:" in proc.stdout, f"Abschnitt nicht abgeschlossen: {proc.stdout[-2000:]}"

            # Kein Autoplayer: jede der fuenf echten Zugzeilen kam tatsaechlich
            # beim SL an (stdin ist hier eine Pipe, kein PTY -- `input()`
            # echot ueber eine Pipe nicht automatisch nach stdout, s. UX22-
            # Disziplin "Pipe != PTY"; der verbindliche Beleg ist daher der
            # tatsaechlich empfangene GM-Request-Body, nicht stdout). Jede
            # Zeile kam aus GENAU dieser stdin-Zeile, nicht aus einer
            # generischen Heuristik/Produktvorgabe.
            received_texts = [
                (c.get("messages") or [{}])[-1].get("content", "") for c in gm_srv.calls
            ]
            for text in leader_turns + guest_turn_texts:
                assert any(text in rt for rt in received_texts), (
                    f"eigene Zugzeile kam nicht beim SL an: {text!r} (empfangen={received_texts})"
                )

            table = core_store.Table.load(run_dir, table_id)
            assert table.leader == leader_id
            assert set(table.members) == set(pids), f"Mitgliedschaft unvollstaendig/falsch: {table.members}"
            assert len(table.members) == 5, "genau fuenf Mitglieder erwartet, kein sechster Spieler"
            assert table.status == "closed"

            for pid in pids:
                current = json.loads((run_dir / "current_saves" / f"{pid}.json").read_text(encoding="utf-8"))
                assert current == end_saves[pid], f"'{pid}': Endsave nicht vollstaendig/korrekt publiziert"

            offer_log = sup.read_jsonl(run_dir / "invitation_decisions.jsonl")
            consent_from = {e.get("from") for e in offer_log if e.get("type") == "response" and e.get("decision") == "accept"}
            assert set(guest_ids).issubset(consent_from), f"Consent-Log fuer alle vier Gaeste unvollstaendig: {offer_log}"

            assert len(gm_srv.calls) == 5, (
                f"erwartet genau 5 echte SL-Calls (1 Leader-Anker + 4 Gast-Importe, Abschluss bereits "
                f"beim 5. Call) -- beobachtet={len(gm_srv.calls)}"
            )
            assert expected_char_ids.issubset(gm_srv.seen_char_ids)


def test_sixth_human_rejected_no_table_no_gm_call():
    """UX08 (02 §D.5, REVIEW.md §G01 'kein sechster Spieler'): derselbe
    Fuenf-Menschen-Aufbau, aber mit einem FUeNFTEN GAST (sechs Spieler
    gesamt einschliesslich Leader) -- wird von der bestehenden, unveraen-
    derten Tischgroessenpolicy (`ZeitrissTableSizePolicy`, max_size=5) VOR
    jeder Tischanlage kontrolliert abgelehnt. Kein Tisch, kein SL-Call,
    keine stille Restgruppe (dieselbe bereits abgenommene Policy wie
    `test_a24_negative_six_players_rejected`, hier spezifisch fuer FUeNF
    MENSCHEN + einen sechsten statt einer Mensch/KI-Mischung)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        registry_dir = root / "registry"
        onboarding_dir = root / "onboarding"
        states_dir = root / "states"
        run_dir = root / "run"

        names = ["Fin", "Gina", "Hugo", "Ida", "Jon", "Kira"]
        chars = [
            ("CHR-UX08N-A", "Fin", "FINOPS"), ("CHR-UX08N-B", "Gina", "GINAOPS"),
            ("CHR-UX08N-C", "Hugo", "HUGOOPS"), ("CHR-UX08N-D", "Ida", "IDAOPS"),
            ("CHR-UX08N-E", "Jon", "JONOPS"), ("CHR-UX08N-F", "Kira", "KIRAOPS"),
        ]
        participants = [sup.register_human(registry_dir, n) for n in names]
        pids = [p.participant_id for p in participants]
        onbs = [
            sup.onboard_human_figure(registry_dir, pid, onboarding_dir, states_dir, run_dir, *c)
            for pid, c in zip(pids, chars)
        ]
        write_test_profile(run_dir)

        leader_id = pids[0]
        guest_ids = pids[1:]  # fuenf weitere Menschen -- sechs gesamt.
        assert len(guest_ids) == 5

        final_saves = {pid: onb["save"] for pid, onb in zip(pids, onbs)}
        table_id = sup.compute_table_id(leader_id, guest_ids)
        section_id = f"{table_id}-section"

        gm_calls_guard: list = []

        class _MustNotBeCalledHandler(BaseHTTPRequestHandler):
            def log_message(self, *a):
                return

            def do_POST(self):
                length = int(self.headers.get("Content-Length", 0) or 0)
                raw = self.rfile.read(length) if length else b""
                try:
                    body = json.loads(raw.decode("utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    body = {}
                gm_calls_guard.append(body)
                payload = {"choices": [{"message": {"content": "SOLLTE NIE GESENDET WERDEN"}}], "usage": {}}
                data = json.dumps(payload).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        class _GuardServer(HTTPServer):
            def __init__(self):
                super().__init__(("127.0.0.1", 0), _MustNotBeCalledHandler)
                import threading
                self._thread = threading.Thread(target=self.serve_forever, daemon=True)

            @property
            def base_url(self):
                host, port = self.server_address
                return f"http://{host}:{port}"

            def __enter__(self):
                self._thread.start()
                return self

            def __exit__(self, *exc):
                self.shutdown()
                self.server_close()

        with _GuardServer() as gm_srv:
            env = {"OPENWEBUI_URL": gm_srv.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC_UX08N_KEY"}
            env.pop("MMO_SIM_PERSONA_CLI", None)

            guests_sorted = sup.sorted_guest_order(leader_id, guest_ids)
            # Einfacher Tokenweg ('l <id> ...') statt gefuehrtem Weg -- die
            # Policy-Pruefung liegt VOR jeder Mitgliedschafts-/Treiber-
            # anlage, unabhaengig vom Einrichtungsweg (dieselbe Pruefung wie
            # beim gefuehrten `g`-Weg, s. `test_a24_negative_six_players_
            # rejected`, das denselben Tokenweg fuer die Policy-Probe nutzt).
            accepts = "\n".join("j" for _ in guests_sorted)
            stdin_text = f"l {' '.join(guests_sorted)}\n{accepts}\nx\n"

            proc = run_process(root, leader_id, stdin_text, env, timeout=60)

            table_files = list((run_dir / "tables").glob("local-*.json")) if (run_dir / "tables").exists() else []

            assert proc.returncode == 0, f"Prozess-Fehlschlag statt fachlicher Ablehnung: {proc.stderr[-1500:]}"
            assert "Abschnitt abgeschlossen:" not in proc.stdout
            assert not gm_calls_guard, "Sechs-Menschen-Fall hat trotzdem einen SL-Turn ausgeloest -- Tischgrenze umgangen"
            assert not table_files, f"Sechs-Menschen-Fall hat trotzdem einen Tisch angelegt: {[p.name for p in table_files]}"

            size_line = next(
                (ln for ln in proc.stdout.splitlines() if "Lokale Runde konnte nicht gestartet werden" in ln), None,
            )
            assert size_line is not None, f"Ablehnungsmeldung fehlt: {proc.stdout[-800:]}"
            assert "6 Spieler angefragt" in size_line, size_line
            assert "1 bis 5" in size_line, size_line


def main() -> int:
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
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
