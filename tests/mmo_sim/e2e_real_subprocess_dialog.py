#!/usr/bin/env python3
"""
tests/mmo_sim/e2e_real_subprocess_dialog.py — echter durchgaengiger
Offline-Prozess-Beleg gegen den TATSAECHLICHEN `scripts/mmo_sim.py`-
Einstiegspunkt (WEGKARTE §3, P2-Vertragsabschluss).

Unterschied zu `e2e_offline_player_dialog.py` (bleibt unveraendert, deckt den
In-Prozess-`TuiSession`-Pfad ab): DIESES Skript startet fuer JEDEN
Teilnehmer + JEDEN "neuen Prozess"-Schritt einen ECHTEN, EIGENSTAENDIGEN
Python-Subprozess (`subprocess.run([sys.executable, 'scripts/mmo_sim.py', ...])`)
-- keine In-Prozess-`TuiSession`-Instanz, keine direkte State-/Katalog-/
Consent-Vorbereitung NEBEN der UI. Jeder Teilnehmer (Leader UND Gast)
uebernimmt seinen Save ueber sein EIGENES, echtes Menue ('i'), exakt wie im
Produkt. Testdoubles sitzen AUSSCHLIESSLICH an der aeusseren Prozess-/HTTP-
Grenze: ein "smarter" Loopback-HTTP-Server fuer die SL (prueft die
tatsaechlich empfangenen v7-Save-IDs beider Mitglieder, BEVOR er den
Abschluss-Marker sendet -- kein bedingungsloser N-ter-Call-Erfolg) und ein
zweiter Loopback-HTTP-Server fuer die eingeladene KI-Persona (liefert
normalen Modelltext -- KEINE `save_payload`-Fake-Bindung; die Bindung des
Gast-Saves an den Wire erfolgt ausschliesslich ueber die Runtime, D3).

Deckt: Import (beide Teilnehmer, je eigener Prozess) -> Einladung + echte
Zusage (Persona-Gast ueber HTTP) -> mehrere Szenen mit Reaktion auf
empfangene SL-Infos -> gueltiger Abschluss + KI-Pflichtreflexion -> Export
-> ECHTER NEUER Python-Prozess (nicht dieselbe TuiSession) mit derselben
Gruppe -> neuer Abschnitt OHNE `TableClosedError` (D5). Zusaetzlich ein
separater negativer Kontrollfall (eigener temp-Store): eine abgelehnte/
nicht erreichbare Persona-Einladung erzeugt KEINE Tischmitgliedschaft."""
from __future__ import annotations

import json
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

from mmo_sim.core import store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER  # noqa: E402

FIX = _REPO_ROOT / "internal" / "qa" / "harness" / "lobby" / "fixtures" / "saves"
LOG: list[str] = []


def log(msg: str) -> None:
    print(msg)
    LOG.append(msg)


class _SmartGmHandler(BaseHTTPRequestHandler):
    """Simuliert die OWUI-`/api/chat/completions`-Antwortform, die
    `internal/qa/harness/owui_client.OWUIChat` erwartet. Prueft VOR jedem
    Abschluss-Angebot, ob die v7-Save-IDs BEIDER erwarteter Mitglieder
    tatsaechlich schon in einer der bisherigen Nachrichten angekommen sind
    (kein bedingungsloser Call-Zaehler-Erfolg, WEGKARTE §3)."""

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
        n = len(self.server.calls)  # type: ignore[attr-defined]
        if n >= self.server.complete_after and self.server.expected_char_ids.issubset(  # type: ignore[attr-defined]
            self.server.seen_char_ids  # type: ignore[attr-defined]
        ):
            debrief = "\n".join(
                f"```json\n{json.dumps(b, ensure_ascii=False)}\n```" for b in self.server.final_saves.values()  # type: ignore[attr-defined]
            )
            content = (
                f"{debrief}\n{COMPLETION_MARKER} table_id={self.server.table_id} "  # type: ignore[attr-defined]
                f"section_id={self.server.section_id}"  # type: ignore[attr-defined]
            )
        else:
            content = f"Szene {n}: Ihr steht bereit und beobachtet die Umgebung. Was tut ihr?"
        payload = {"choices": [{"message": {"content": content}}], "usage": {}, "sources": []}
        data = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class SmartGmServer(HTTPServer):
    """Echter Loopback-HTTP-Server (127.0.0.1), ersetzt NUR die aeussere
    HTTP-Grenze von `owui_client.OWUIChat` -- der komplette Adapter-/
    Runtime-/TUI-Code laeuft real durch einen echten Subprozess."""

    def __init__(self, final_saves: dict[str, dict], table_id: str, section_id: str, complete_after: int):
        super().__init__(("127.0.0.1", 0), _SmartGmHandler)
        self.calls: list[dict] = []
        self.seen_char_ids: set[str] = set()
        self.expected_char_ids = {zeitriss_saves.block_char_id(b) for b in final_saves.values()}
        self.final_saves = final_saves
        self.table_id = table_id
        self.section_id = section_id
        self.complete_after = complete_after
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


def run_process(data_dir: Path, participant: str, stdin_text: str, env_extra: dict) -> subprocess.CompletedProcess:
    """Ein ECHTER, EIGENSTAENDIGER Python-Subprozess -- kein In-Prozess-
    `TuiSession`-Aufruf. `env_extra` wird an die GEERBTE Umgebung angehaengt
    (nicht ersetzt), wie es die Produktadapter selbst tun (B2-Konsistenz)."""
    import os
    env = dict(os.environ)
    env.update(env_extra)
    cmd = [sys.executable, str(_REPO_ROOT / "scripts" / "mmo_sim.py"),
           "--data-dir", str(data_dir), "--participant", participant]
    return subprocess.run(cmd, input=stdin_text, capture_output=True, text=True, env=env, cwd=str(data_dir), timeout=30)


def positive_scenario() -> None:
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        write_test_profile(data_dir / "run")
        sniper_save = json.loads((FIX / "sniper.json").read_text())
        tech_save = json.loads((FIX / "tech.json").read_text())
        table_id, section_id = "local-sniper-tech", "local-sniper-tech-section"

        with SmartGmServer({"sniper": sniper_save, "tech": tech_save}, table_id, section_id, complete_after=4) as gm_srv, \
             _persona_server([
                 # I1-Fix (MAIN-ENTSCHEIDUNG I1-Kontrollform): Zusage muss der
                 # vollstaendig validierbaren Kontrollform entsprechen
                 # (offer_id/participant_id gebunden, deterministisch aus
                 # Leader+Gaesten abgeleitet -- s. `_cmd_local_round`).
                 (200, {"choices": [{"message": {
                     "content": "ENTSCHEIDUNG offer_id=invite-sniper-tech participant_id=tech "
                                "decision=accept explanation=Ich bin dabei.",
                 }}]}),
                 (200, {"choices": [{"message": {"content": "Ich sichere die Umgebung."}}]}),
                 (200, {"choices": [{"message": {"content": "Ich beobachte weiter, alles ruhig."}}]}),
                 (200, {"choices": [{"message": {"content": "Bin zufrieden mit dem Verlauf."}}]}),
             ]) as persona_srv:
            env = {
                "OPENWEBUI_URL": gm_srv.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC_E2E_KEY",
                "MMO_SIM_PERSONA_API_BASE_URL": persona_srv.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTHETIC_E2E_KEY", "MMO_SIM_PERSONA_API_MODEL": "synthetic-e2e",
            }
            # ── Schritt 1a: Gast 'tech' uebernimmt SEINEN EIGENEN Save
            # ueber SEIN EIGENES echtes Menue (eigener Subprozess) --
            # keine Vorbereitung NEBEN der UI. ────────────────────────────
            log("=== Schritt 1a: 'tech' importiert (echter Subprozess) ===")
            tech_stdin = "i\n" + json.dumps(tech_save) + "\nENDE\nx\n"
            p_tech = run_process(data_dir, "tech", tech_stdin, env)
            assert p_tech.returncode == 0, f"tech-Import-Prozess fehlgeschlagen: {p_tech.stderr}"
            assert "Uebernahme abgeschlossen" in p_tech.stdout, p_tech.stdout
            log(f"  tech-Import Exit={p_tech.returncode}")

            # ── Schritt 1b+3+4+5: Leader 'sniper' importiert, ladet 'tech'
            # (Persona) ein, spielt mehrere Szenen, schliesst ab. ─────────
            log("=== Schritt 1b+3+4+5: 'sniper' importiert + ladet Persona ein + spielt ab (echter Subprozess) ===")
            sniper_stdin = (
                "i\n" + json.dumps(sniper_save) + "\nENDE\n"
                "l persona:tech\n"
                "Wir betreten den Sektor vorsichtig.\n"
                "Wir folgen der Spur weiter.\n"
                "Notiz: zufriedene Runde.\n"
                "x\n"
            )
            p_sniper = run_process(data_dir, "sniper", sniper_stdin, env)
            assert p_sniper.returncode == 0, f"sniper-Prozess fehlgeschlagen: {p_sniper.stderr}"
            log(p_sniper.stdout)
            assert "Uebernahme abgeschlossen" in p_sniper.stdout, "sniper-Import lief nicht real durch"
            assert "Gruppe eingeladen" in p_sniper.stdout and "tech" in p_sniper.stdout, (
                "Persona-Einladung wurde nicht real aufgeloest"
            )
            assert "Abschnitt abgeschlossen:" in p_sniper.stdout, (
                f"Abschnitt wurde nicht real abgeschlossen: {p_sniper.stdout[-800:]}"
            )
            assert len(gm_srv.calls) >= 4, f"Fake-GM haette mehrfach real befragt werden muessen: {len(gm_srv.calls)}"
            assert gm_srv.expected_char_ids.issubset(gm_srv.seen_char_ids), (
                "Fake-GM hat den Abschluss-Marker gesendet, OHNE zuvor beide Save-IDs empfangen zu haben"
            )
            assert len(persona_srv.calls) >= 3, (
                f"Persona-Gast haette mehrfach real ueber HTTP befragt werden muessen: {len(persona_srv.calls)}"
            )
            # A28/D3: die Persona-Antworten (Server-Seite) liefern NUR
            # normalen Modelltext ueber `choices[0].message.content` -- kein
            # `save_payload`-Feld im Antwortformat. Die tatsaechliche
            # Save-Bindung fuer den Gast-Importturn geschieht ausschliesslich
            # in der Runtime (`core/runtime.py:act`, ueber
            # `import_save_payload` aus dem Kontext, s. D3/Test 04) --
            # `PersonaApiDriver` selbst hat strukturell KEINE Moeglichkeit,
            # einen `save_payload` an die Antwort zu haengen (kein Feld im
            # Adaptercode, s. `adapters/persona_api.py`).

            table = store.Table.load(data_dir / "run", table_id)
            assert table.status == "closed" and set(table.members) == {"sniper", "tech"}, (
                f"Tisch nach Abschluss inkonsistent: status={table.status} members={table.members}"
            )
            reflections = [
                json.loads(line) for line in (data_dir / "run" / "reflections.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            assert any(r.get("persona_key") == "tech" and r.get("kind") == "ai_required_reflection" for r in reflections), (
                "KI-Pflichtreflexion fuer 'tech' fehlt im Archiv"
            )
            log(f"  Tisch geschlossen, Mitglieder={table.members}, Fake-GM-Calls={len(gm_srv.calls)}, Persona-Calls={len(persona_srv.calls)}")

            # ── Schritt 6: Export (echter Subprozess, 'e'). ────────────────
            log("=== Schritt 6: Export (echter Subprozess) ===")
            p_export = run_process(data_dir, "sniper", "e\nx\n", env)
            assert p_export.returncode == 0, p_export.stderr
            export_path = data_dir / "exports" / "sniper.json"
            assert export_path.is_file(), "Export-Datei fehlt"
            log(f"  Export geschrieben: {export_path}")

            # ── Schritt 7: TATSAECHLICH NEUER Python-Prozess -- neuer
            # Abschnitt derselben Gruppe, KEIN TableClosedError (D5). ──────
            log("=== Schritt 7: neuer Abschnitt, ECHTER NEUER Prozess ===")
            gm_srv.complete_after = 10 ** 9  # in diesem Schritt keine Vollendung noetig, nur Sendefaehigkeit pruefen.
            calls_before = len(gm_srv.calls)
            # R03-Restintegrationsfix (WEGKARTE §5): ein am selben Geraet
            # mitspielender Mensch (Token ohne 'persona:'-Praefix) bestaetigt
            # jetzt selbst explizit VOR Tischaufnahme -- 'Ja' beantwortet
            # diese Bestaetigung.
            p_resume = run_process(data_dir, "sniper", "l tech\nJa\nWir spielen als Gruppe weiter.\nx\n", env)
            assert p_resume.returncode == 0, f"Resume-Prozess fehlgeschlagen: {p_resume.stderr}"
            assert "TableClosedError" not in p_resume.stdout and "TableClosedError" not in p_resume.stderr, (
                "Neuer Abschnitt derselben Gruppe hat den geschlossenen Tisch wiederzubeleben versucht"
            )
            assert len(gm_srv.calls) > calls_before, "Neuer Abschnitt haette mindestens einen echten GM-Turn ausloesen muessen"
            log(f"  Neuer Abschnitt ohne TableClosedError, GM-Calls jetzt={len(gm_srv.calls)}")


def negative_scenario() -> None:
    """K5-Negativfall (WEGKARTE §3): eine Persona-Einladung, die am Prozess-/
    HTTP-Rand real fehlschlaegt (hier: Server antwortet immer mit 500 --
    entspricht einer nicht erreichbaren/ablehnenden Persona), erzeugt KEINE
    Tischmitgliedschaft."""
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        write_test_profile(data_dir / "run")
        sniper_save = json.loads((FIX / "sniper.json").read_text())
        tech_save = json.loads((FIX / "tech.json").read_text())
        table_id = "local-sniper-tech"
        with SmartGmServer({"sniper": sniper_save}, table_id, f"{table_id}-section", complete_after=999) as gm_srv, \
             _persona_server([(500, {"error": "SYNTHETIC_REJECTION"})]) as persona_srv:
            env = {
                "OPENWEBUI_URL": gm_srv.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC_E2E_KEY",
                "MMO_SIM_PERSONA_API_BASE_URL": persona_srv.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTHETIC_E2E_KEY", "MMO_SIM_PERSONA_API_MODEL": "synthetic-e2e",
            }
            p_tech = run_process(data_dir, "tech", "i\n" + json.dumps(tech_save) + "\nENDE\nx\n", env)
            assert p_tech.returncode == 0, p_tech.stderr
            sniper_stdin = "i\n" + json.dumps(sniper_save) + "\nENDE\nl persona:tech\nIch warte ab.\nx\n"
            p_sniper = run_process(data_dir, "sniper", sniper_stdin, env)
            assert p_sniper.returncode == 0, f"sniper-Prozess fehlgeschlagen: {p_sniper.stderr}"
            assert "nicht zustande gekommen" in p_sniper.stdout, (
                f"Ablehnung/Fehlschlag der Persona-Einladung wurde nicht ehrlich gemeldet: {p_sniper.stdout[-500:]}"
            )
            # W1-B2-Fix (Main-Nacharbeit): eine fehlgeschlagene/abgelehnte
            # Persona-Einladung erzeugt WEDER eine Mitgliedschaft NOCH einen
            # stillen Solo-Tisch -- die Runde bricht kontrolliert ab.
            table_file = data_dir / "run" / "tables" / f"{table_id}.json"
            assert not table_file.exists(), (
                f"Abgelehnte/fehlgeschlagene Persona-Einladung hat trotzdem einen (Solo-)Tisch erzeugt: {table_file}"
            )
            log("=== Negativfall: Ablehnung/Fehlschlag erzeugt keine Mitgliedschaft und keinen Tisch ===")


def http200_refusal_scenario() -> None:
    """D2/A4 (WEGKARTE §8, Test 03, REVIEW-P2V.md §10 Abdeckungsluecke
    'HTTP 500 statt normaler Nein-Antwort'): eine ECHT ZUGESTELLTE (HTTP
    200) Ablehnung ueber den vollen Subprozess-/UI-Pfad -- kein
    Transportfehler wie in `negative_scenario`. Eine erfolgreich
    zugestellte Antwort ist KEINE Zusage; 'tech' darf trotz HTTP 200 nicht
    Mitglied werden."""
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        write_test_profile(data_dir / "run")
        sniper_save = json.loads((FIX / "sniper.json").read_text())
        tech_save = json.loads((FIX / "tech.json").read_text())
        table_id = "local-sniper-tech"
        with SmartGmServer({"sniper": sniper_save}, table_id, f"{table_id}-section", complete_after=999) as gm_srv, \
             _persona_server([(200, {"choices": [{"message": {"content": "Nein. Ich lehne die Einladung ab."}}]})]) as persona_srv:
            env = {
                "OPENWEBUI_URL": gm_srv.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC_E2E_KEY",
                "MMO_SIM_PERSONA_API_BASE_URL": persona_srv.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTHETIC_E2E_KEY", "MMO_SIM_PERSONA_API_MODEL": "synthetic-e2e",
            }
            p_tech = run_process(data_dir, "tech", "i\n" + json.dumps(tech_save) + "\nENDE\nx\n", env)
            assert p_tech.returncode == 0, p_tech.stderr
            sniper_stdin = "i\n" + json.dumps(sniper_save) + "\nENDE\nl persona:tech\nIch warte ab.\nx\n"
            p_sniper = run_process(data_dir, "sniper", sniper_stdin, env)
            assert p_sniper.returncode == 0, f"sniper-Prozess fehlgeschlagen: {p_sniper.stderr}"
            assert persona_srv.calls, "Persona-Server haette real per HTTP 200 angesprochen werden muessen"
            assert "nicht angenommen" in p_sniper.stdout, (
                f"Eine echt zugestellte (HTTP 200) Ablehnung wurde nicht als Nicht-Zusage erkannt: {p_sniper.stdout[-500:]}"
            )
            # W1-B2-Fix (Main-Nacharbeit, End-Critic BLOCKER 2): eine echt
            # zugestellte (HTTP 200) Ablehnung darf WEDER eine Mitgliedschaft
            # NOCH einen stillen Solo-Tisch erzeugen -- die angefragte Runde
            # bricht kontrolliert ab, kein Tisch entsteht (vorher: solo
            # `local-sniper-tech`). Assertionsziel unveraendert (Ablehnung
            # erzeugt keine Mitgliedschaft), nur staerker: gar kein Tisch.
            table_file = data_dir / "run" / "tables" / f"{table_id}.json"
            assert not table_file.exists(), (
                f"HTTP-200-Ablehnung hat trotzdem einen (Solo-)Tisch erzeugt: {table_file}"
            )
            assert "nicht zustande gekommen" in p_sniper.stdout, (
                f"Abbruchhinweis fehlt -- stiller Soloweiterlauf statt Abbruch? {p_sniper.stdout[-400:]}"
            )
            log("=== HTTP-200-Ablehnung (echte Zustellung, keine Zusage): kein Tisch, Runde kontrolliert abgebrochen ===")


def default_identity_scenario() -> None:
    """A8/D1/V02 (WEGKARTE §8, REVIEW-P2V.md §10 Abdeckungsluecke 'feste
    alte Persona-Keys statt normaler erzeugter ID'): ein ECHTER Subprozess
    OHNE `--participant`-Alias -- der reguläre Ersteinstieg (frischer
    Datenordner, `identity.new_participant_id()`-generierte ID) muss den
    Import erfolgreich abschliessen (kein `jsonschema.ValidationError` durch
    einen schema-inkonformen Bindestrich-Key)."""
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        sniper_save = json.loads((FIX / "sniper.json").read_text())
        cmd = [sys.executable, str(_REPO_ROOT / "scripts" / "mmo_sim.py"), "--data-dir", str(data_dir)]
        p = subprocess.run(
            cmd, input="i\n" + json.dumps(sniper_save) + "\nENDE\nx\n",
            capture_output=True, text=True, cwd=str(data_dir), timeout=20,
        )
        assert p.returncode == 0, f"Default-Identitaets-Import fehlgeschlagen: {p.stderr}"
        assert "Uebernahme abgeschlossen" in p.stdout, p.stdout
        marker = json.loads((data_dir / "last_participant.json").read_text(encoding="utf-8"))
        pid = marker["participant_id"]
        assert not pid.startswith("participant-"), f"erwartet schema-konforme ID, bekam {pid!r}"
        state_files = list((data_dir / "states").glob("*.json"))
        assert state_files, "kein Persona-State fuer die default-generierte ID geschrieben"
        log(f"=== Default-Identitaet ohne --participant: pid={pid} state_files={[f.name for f in state_files]} ===")


def _persona_server(responses: list[tuple[int, dict]]):
    from mmo_sim.adapters.fakes import FakeHTTPServer
    return FakeHTTPServer(responses)


def main() -> int:
    default_identity_scenario()
    http200_refusal_scenario()
    positive_scenario()
    negative_scenario()
    log("=== ECHTER PROZESS-E2E VOLLSTAENDIG DURCHLAUFEN: PASS ===")
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except AssertionError as e:
        print(f"FAIL: {e}")
        rc = 1
    except Exception:
        import traceback
        traceback.print_exc()
        rc = 1
    # E2E-Hygiene (WEGKARTE §0/§4, Review-Auflage): das Log NICHT mehr in
    # den getrackten Quellbaum schreiben (s. e2e_offline_player_dialog.py).
    import os
    log_dir = Path(os.environ.get("MMO_SIM_E2E_LOG_DIR", tempfile.gettempdir()))
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / "e2e_real_subprocess_dialog.log").write_text(
        "\n".join(LOG) + f"\n\nEXIT={rc}\n", encoding="utf-8",
    )
    sys.exit(rc)
