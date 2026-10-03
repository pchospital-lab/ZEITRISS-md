#!/usr/bin/env python3
"""
tests/mmo_sim/test_p2_lobby_application_boundaries.py — dauerhafte Repo-
Regressionen fuer den Lobby-Anwendungsabschluss (R1.1/R1.2/R2/R3.1/R3.2,
REVIEW-LOBBY-ANWENDUNG.md §3-5, MAIN-DATENWEGENTSCHEIDUNG.md Zustandstabelle).

Original+Derivat+Diff (WORKER-REPORT.md): dieselbe I/O-Naht/Fehlerinjektions-
Technik wie die externe Review-Kernprobe (`tests-review/review_lobby_
application_boundaries.py` im Lieferpaket, NICHT Teil dieses Repos) --
DERIVAT hier lebt DAUERHAFT im Repo, importiert bestehende Fixtures aus
`test_l01_l10_lobby_initiative.py` (kein zweiter Bootstrap-Baustein) und ist
in `run_all.py` eingebunden (Dateiname `test_*.py`). Ergaenzt (nicht
ersetzt) `test_l01_l10_lobby_initiative.py`/`test_k1_k4_lobby_kontinuitaet.py`.

R1.1/R2 brauchen eine ECHTE Unterbrechung an einer konkreten I/O-Naht NACH
einer bereits empfangenen Entscheidung -- dieses Modul relauncht sich dafuer
selbst als eigenstaendigen Python-Subprozess (`--child`, echte, von Prozess 1
verschiedene Betriebssystem-PID, analog `test_l08_real_restart_process_
resumes_open_offer_without_duplicate_offer`/`test_k1_new_window_after_
pause_real_subprocess_restart_...`). Die Injektion wird NUR intern im
relaunchten Kind-Interpreter angewendet (`Path.open`-Patch NACH Prozessstart)
-- der Produktweg selbst (`ui/tui.py`, `core/lobby_service.py`) bleibt
unveraendert, kein Fault-Injection-Flag im Produkt."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest.mock import patch

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import test_l01_l10_lobby_initiative as l01  # noqa: E402

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import lobby_service  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402

ACTIVITY = "HQ-Recherche: REPO_REGRESSION_AGREED_ACTIVITY_512"


def _persona_http_server(responses):
    return l01._persona_http_server(responses)


class _ChildDriver:
    """Markiertes Testdouble fuer den relaunchten Kind-Prozess -- entscheidet
    NUR anhand des tatsaechlichen Kontrollvertrags (Kontexttext), keine
    Vorwegnahme. `self.calls` traegt `kind` ('initiative'/'consent'/'table'),
    damit die Zaehlung der echten Lobby-Requests (nicht der spaeteren
    Tischspielzuege) eindeutig bleibt."""

    def __init__(self, pk: str, mode: str):
        self.pk = pk
        self.mode = mode
        self.config = None
        self.calls: list[dict] = []

    def decide(self, ctx: dict) -> ParticipantDecision:
        if "decision_contract" in ctx:
            kind = "consent"
            c = ctx["decision_contract"]
            text = f"ENTSCHEIDUNG offer_id={c['offer_id']} participant_id={self.pk} decision=accept"
        elif "begrenztes eigenes Lobby-Initiativfenster" in ctx.get("user", ""):
            kind = "initiative"
            if self.mode == "pause" or self.pk != "sniper":
                text = json.dumps({"action": "pause"})
            else:
                text = json.dumps({"action": "propose", "wants": ["tech"]})
        else:
            kind = "table"
            text = "SYNTHETIC: Wir beobachten und entscheiden am Tisch."
        self.calls.append({"kind": kind, "context": ctx})
        return ParticipantDecision(text=text, origin_source=f"repo-regression:{self.pk}")


def _child_main(args: argparse.Namespace) -> None:
    """Laeuft NUR im relaunchten Subprozess (`--child`) -- echte, andere
    Betriebssystem-PID als der aufrufende Testprozess. `root` ist bereits
    ueber `_bootstrap_community`/`_make_ready` (Prozess 1) vorbereitet."""
    root = Path(args.root)
    schema_path, states_dir, run_dir = l01._SCHEMA, root / "states", root / "run"
    onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"

    drivers = {pk: _ChildDriver(pk, args.mode) for pk in ("sniper", "tech")}
    gms: list = []

    def gm_transport_factory(tid: str):
        # Real `_TableGM`-Testdouble (wie die Review-Kernprobe) -- ein
        # tatsaechlich entstandener Tisch (mode='journey'/'pause' NACH
        # Wiederaufnahme) muss real bis zum Abschluss gespielt werden
        # koennen, kein pauschales "kein GM-Call erwartet".
        saves = {pk: json.loads((l01._FIX / f"{pk}.json").read_text(encoding="utf-8")) for pk in ("sniper", "tech")}
        for pk, s in saves.items():
            s["save_id"] = f"repo-regression-{tid}-{pk}"
        gm = l01._TableGM(tid, f"{tid}-section", saves, turns_before_marker=3)
        gms.append(gm)
        return gm

    printed: list[str] = []
    session = l01._session(
        "op", onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
        gm_transport_factory=gm_transport_factory,
        persona_driver_factory=lambda pk: drivers[pk],
        printed=printed,
    )

    hits: list[dict] = []
    orig_append = session._append_invitation_log

    def append(rec: dict) -> None:
        if args.mode == "interrupt-offer" and rec.get("type") == "offer" and not hits:
            hits.append({"seam": "before_offer_event_application"})
            raise OSError("SYNTHETIC local interruption after received decision")
        return orig_append(rec)

    session._append_invitation_log = append

    invitation_log_path = run_dir / "invitation_decisions.jsonl"
    orig_open = Path.open

    class _WriteProxy:
        def __init__(self, fh):
            self._fh = fh

        def __enter__(self):
            self._fh.__enter__()
            return self

        def __exit__(self, *exc):
            return self._fh.__exit__(*exc)

        def __getattr__(self, name):
            return getattr(self._fh, name)

        def write(self, text):
            if args.mode == "resolution-write-error" and not hits and json.loads(text).get("type") == "resolution":
                hits.append({"seam": "real invitation_log append", "type": "resolution"})
                raise OSError("SYNTHETIC resolution write failure")
            return self._fh.write(text)

    def patched_open(p, *a, **kw):
        fh = orig_open(p, *a, **kw)
        mode = a[0] if a else kw.get("mode", "r")
        if p == invitation_log_path and "a" in mode:
            return _WriteProxy(fh)
        return fh

    errors: list[dict] = []
    with patch.object(Path, "open", patched_open):
        try:
            session._cmd_lobby_initiative()
        except Exception as e:  # ECHTER Prozessabbruch bleibt sichtbar, kein Verschlucken hier.
            errors.append({"type": type(e).__name__, "message": str(e)})

    def read(p: Path, default):
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default

    row = {
        "pid": os.getpid(),
        "printed": printed,
        "errors": errors,
        "hits": hits,
        # Nur echte LOBBY-Requests zaehlen (initiative/consent) -- spaetere
        # Tischspielzuege sind eine andere Zaehlung (`gm_calls`).
        "calls": {pk: len([c for c in d.calls if c["kind"] in ("initiative", "consent")]) for pk, d in drivers.items()},
        "gm_calls": sum(len(g.calls) for g in gms),
        "tables": [read(p, {}) for p in sorted((run_dir / "tables").glob("*.json"))],
        "records": [read(p, {}) for p in sorted((run_dir / "requests").glob("*.json"))],
    }
    Path(args.result).write_text(json.dumps(row, indent=2, ensure_ascii=False), encoding="utf-8")


def _run_child(root: Path, mode: str, result_path: Path, limit: int = 2) -> dict:
    """ECHTER, EIGENSTAENDIGER Python-Subprozess (`subprocess.run`, nicht
    dieselbe `TuiSession`-Instanz) -- die zurueckgegebene PID ist von jedem
    weiteren Aufruf verschieden (L08-Muster)."""
    cmd = [
        sys.executable, str(Path(__file__).resolve()), "--child",
        "--root", str(root), "--mode", mode, "--result", str(result_path),
    ]
    env = os.environ.copy()
    env["MMO_SIM_LOBBY_INITIATIVE_LIMIT"] = str(limit)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    cp = subprocess.run(cmd, cwd=str(root), env=env, capture_output=True, text=True, timeout=60)
    if cp.returncode != 0:
        raise RuntimeError(f"child(mode={mode!r}) exit={cp.returncode}: {cp.stderr[-2000:]}")
    return json.loads(result_path.read_text(encoding="utf-8"))


def _seed(root: Path) -> None:
    schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = l01._bootstrap_community(
        root, "community-op", ["sniper", "tech"],
    )
    write_test_profile(run_dir)
    for pk in ("sniper", "tech"):
        l01._make_ready(onboarding_dir, states_dir, run_dir, pk)


def test_r11_first_proposal_survives_interrupted_offer_log_write_real_restart_positive_repeat():
    """R1.1 (REVIEW-LOBBY-ANWENDUNG.md §3.1, MAIN-DATENWEGENTSCHEIDUNG.md A):
    Prozess 1 (echter Subprozess) laesst 'sniper' seine erste Initiative
    real beantworten ('propose') -- der Offer-Logeintrag dafuer wird durch
    eine synthetische Unterbrechung VERHINDERT, NACHDEM die Entscheidung
    bereits durabel im Ledger accounted ist (kein Tisch, kein Angebot im
    Log). Prozess 2 (ECHTER neuer Subprozess, andere PID) fuehrt DIESELBE
    Requestidentitaet fort: 'sniper' wird NICHT erneut real befragt
    (`calls['sniper'] == 0`), das noch fehlende Angebot wird jetzt real
    geschrieben, 'tech' konsentiert real, ein Tisch entsteht. Positive
    Wiederholung: Prozess 3 (echter dritter Subprozess) startet ein GENUIN
    NEUES Fenster (beide erneut real pausiert) -- der Fix haelt die
    normalen Fensterfaelle NICHT versehentlich fest."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _seed(root)

        r1 = _run_child(root, "interrupt-offer", root / "r1.json")
        assert r1["hits"] == [{"seam": "before_offer_event_application"}]
        assert r1["errors"], "die synthetische Unterbrechung muss den Kind-Prozess sichtbar unterbrechen"
        assert len(r1["records"]) == 1 and r1["records"][0]["state"] == "accounted"
        assert not r1["tables"]
        assert not lobby_service.read_offer_log(root / "run"), "kein Angebot vor der Unterbrechung geloggt"

        r2 = _run_child(root, "journey", root / "r2.json")
        assert r2["pid"] != r1["pid"], "Prozess 2 muss eine ECHTE andere Betriebssystem-PID haben"
        assert r2["calls"]["sniper"] == 0, (
            f"'sniper' haette seine bereits accountede erste Initiative NICHT erneut real beantworten "
            f"duerfen: {r2['calls']}"
        )
        assert r2["calls"]["tech"] == 1, "'tech' antwortet real auf das jetzt geschriebene Angebot"
        assert len(r2["tables"]) == 1 and r2["tables"][0]["status"] == "closed"

        r3 = _run_child(root, "pause", root / "r3.json")
        assert r3["pid"] not in (r1["pid"], r2["pid"])
        assert r3["calls"]["sniper"] == 1 and r3["calls"]["tech"] == 1, (
            f"ein GENUIN NEUES Fenster (nach Abschluss) haette BEIDE real erneut fragen muessen: "
            f"{r3['calls']}"
        )


def test_r2_resolution_write_failure_does_not_spawn_second_table_real_restart_positive_repeat():
    """R2 (REVIEW-LOBBY-ANWENDUNG.md §4, MAIN-DATENWEGENTSCHEIDUNG.md B):
    Prozess 1 (echter Subprozess) schliesst Angebot+Konsens vollstaendig ab
    UND legt den Tisch an -- die anschliessende Resolution-Bindung
    (`append_offer_resolution`) trifft einen ECHTEN `OSError` beim
    tatsaechlichen Log-Append. Prozess 2 (ECHTER neuer Subprozess) darf
    daraus KEINEN zweiten Tisch aus derselben, bereits verbrauchten
    Zustimmung erzeugen -- hoechstens EIN Tisch bleibt bestehen, kein
    zusaetzlicher GM-/Driveraufruf aus der alten Zustimmung. Positive
    Wiederholung: Prozess 3 startet danach ein GENUIN NEUES, gesundes
    Fenster (beide real gefragt) -- der Fix blockiert nicht dauerhaft."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _seed(root)

        r1 = _run_child(root, "resolution-write-error", root / "r1.json")
        assert r1["hits"] == [{"seam": "real invitation_log append", "type": "resolution"}]
        # R2-Fix: der Writefehler wird sichtbar KONTROLLIERT abgefangen
        # (Meldung, kein Spielstart) -- kein Absturz (`errors` bleibt leer),
        # aber auch KEIN stilles Verschlucken, das den Tisch trotzdem spielt.
        assert not r1["errors"], r1["errors"]
        assert "Resolution-Bindung" in "\n".join(r1["printed"]) or "Resolution" in "\n".join(r1["printed"]), r1["printed"]
        assert r1["gm_calls"] == 0, "kein Spielstart aus einer nicht durabel gebundenen Zustimmung erwartet"
        tables_after_r1 = len(r1["tables"])
        assert tables_after_r1 <= 1

        r2 = _run_child(root, "pause", root / "r2.json")
        assert r2["pid"] != r1["pid"]
        assert len(r2["tables"]) <= 1, (
            f"ein fehlgeschlagener Resolution-Write darf beim naechsten Aufruf KEINEN zweiten Tisch "
            f"aus derselben Zustimmung erzeugen: {len(r2['tables'])} Tische"
        )
        if tables_after_r1 == 1 and r1["tables"][0]["status"] == "closed":
            assert r2["calls"]["sniper"] == 0 and r2["calls"]["tech"] == 0, (
                "ein bereits GESCHLOSSENER Tisch darf keinen weiteren echten Request aus der alten "
                f"Zustimmung ausloesen: {r2['calls']}"
            )

        r3 = _run_child(root, "pause", root / "r3.json")
        assert r3["pid"] not in (r1["pid"], r2["pid"])
        assert r3["calls"]["sniper"] == 1 and r3["calls"]["tech"] == 1, (
            f"ein gesundes GENUIN NEUES Fenster nach der Unterbrechung muss weiterhin BEIDE real fragen "
            f"koennen: {r3['calls']}"
        )


def test_r12_new_offer_in_fresh_window_is_not_masked_by_stale_same_pk_turn_resolution():
    """R1.2 (REVIEW-LOBBY-ANWENDUNG.md §3.2, MAIN-DATENWEGENTSCHEIDUNG.md A):
    Fenster 1 schliesst normal ab (Resolution fuer `lobby-offer-<w0>-sniper-0`
    real geschrieben). Fenster 2 (ECHTER neuer Subprozess) erzeugt fuer
    DENSELBEN Vorschlagenden/Turn-Index ('sniper', turn_idx=0) ein NEUES
    Angebot -- `lobby_service.offer_id_for` bindet die window_id ein, die
    beiden offer_ids sind daher NICHT identisch, obwohl `pk`/`turn_idx`
    gleich sind (vorher: `lobby-offer-sniper-0` in BEIDEN Fenstern ->
    Kollision)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _seed(root)

        r1 = _run_child(root, "journey", root / "r1.json")
        assert len(r1["tables"]) == 1 and r1["tables"][0]["status"] == "closed"

        r2 = _run_child(root, "journey", root / "r2.json")
        assert r2["pid"] != r1["pid"]
        assert r2["calls"]["sniper"] == 1 and r2["calls"]["tech"] == 1, (
            "das NEUE Fenster muss beide real (nicht ueber die alte Resolution maskiert) fragen"
        )
        assert len(r2["tables"]) == 2 and all(t["status"] == "closed" for t in r2["tables"])

        offers = [r for r in lobby_service.read_offer_log(root / "run") if r.get("type") == "offer"]
        assert len(offers) == 2
        offer_ids = [o["offer_id"] for o in offers]
        assert len(set(offer_ids)) == 2, f"beide Fenster erzeugten dieselbe offer_id: {offer_ids}"
        assert offers[0]["window_id"] != offers[1]["window_id"]
        expected_0 = lobby_service.offer_id_for(offers[0]["window_id"], "sniper", 0)
        expected_1 = lobby_service.offer_id_for(offers[1]["window_id"], "sniper", 0)
        assert offer_ids == [expected_0, expected_1]


def test_r13_corrupted_per_entry_window_state_fails_closed_no_reask_no_collision():
    """R1.3, Eintragsebene (END-CRITIC.md §4.3 Hauptbefund 1, Nacharbeit):
    Fenster 1 schliesst normal ab (Fenster-Cursordatei traegt danach den
    gueltigen `{"cursor": 1, "pending": None}`-Eintrag). Der TOP-LEVEL bleibt
    ein gueltiges JSON-`dict` (besteht `_read_window_state`s Strukturpruefung
    unveraendert) -- aber der EINZELNE Community-Eintrag wird auf einen
    Skalartyp korrumpiert, der WEDER dem neuen (`dict` mit `cursor`) NOCH dem
    alten (`int`/`float`) unterstuetzten Schema entspricht (eine
    Zeichenkette). Vor der Nacharbeit interpretierte `_window_entry_cursor`
    dies still als `cursor=0` -- Fenster 2 zog danach ERNEUT die bereits
    verbrauchte erste Fenster-ID und erzeugte dieselbe `offer_id` wie das
    laengst geschlossene Fenster 1 (die exakte Kollision, die R1.2 verhindern
    sollte, hier ueber einen anderen Ausloeser). Nach der Nacharbeit muss
    Fenster 2 stattdessen sichtbar KONTROLLIERT sperren: kein Request an
    irgendein Mitglied, kein neues Angebot im Log, keine Kollision."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = l01._bootstrap_community(
            root, "community-op", ["sniper", "tech"],
        )
        write_test_profile(run_dir)
        for pk in ("sniper", "tech"):
            l01._make_ready(onboarding_dir, states_dir, run_dir, pk)

        saves1 = {pk: json.loads((l01._FIX / f"{pk}.json").read_text(encoding="utf-8")) for pk in ("sniper", "tech")}
        gm1 = l01._TableGM("lobby-sniper-tech", "lobby-sniper-tech-section", saves1, turns_before_marker=2)
        drivers1 = {
            "sniper": l01._ScriptedDriver("sniper", [json.dumps({"action": "propose", "wants": ["tech"]})]),
            "tech": l01._ScriptedDriver("tech", [
                f"ENTSCHEIDUNG offer_id={lobby_service.offer_id_for('lobby-community-op-0', 'sniper', 0)} "
                "participant_id=tech decision=accept",
            ]),
        }
        session1 = l01._session(
            "op", onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
            gm_transport_factory=lambda *_a, **_kw: gm1,
            persona_driver_factory=lambda pk: drivers1[pk], printed=[],
        )
        session1._cmd_lobby_initiative()
        offers_after_1 = [r for r in lobby_service.read_offer_log(run_dir) if r.get("type") == "offer"]
        assert len(offers_after_1) == 1, "Fenster 1 muss genau ein Angebot erzeugen"

        window_state_path = run_dir / lobby_service.WINDOW_STATE_FILENAME
        corrupt = {"community-op": "CORRUPTED_UNEXPECTED_TYPE"}
        window_state_path.write_text(json.dumps(corrupt), encoding="utf-8")

        printed2: list[str] = []
        drivers2 = {
            "sniper": l01._ScriptedDriver("sniper", [json.dumps({"action": "propose", "wants": ["tech"]})]),
            "tech": l01._ScriptedDriver("tech", [
                f"ENTSCHEIDUNG offer_id={lobby_service.offer_id_for('lobby-community-op-0', 'sniper', 0)} "
                "participant_id=tech decision=accept",
            ]),
        }
        session2 = l01._session(
            "op", onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
            gm_transport_factory=lambda *_a, **_kw: (_ for _ in ()).throw(
                AssertionError("kein GM-Call erwartet -- Fenster 2 muss vor jedem Request sperren"),
            ),
            persona_driver_factory=lambda pk: drivers2[pk], printed=printed2,
        )
        session2._cmd_lobby_initiative()

        assert drivers2["sniper"].calls == [], (
            "'sniper' haette bei unlesbarem Eintrag NICHT real befragt werden duerfen (Re-Ask-Risiko): "
            f"{drivers2['sniper'].calls}"
        )
        assert drivers2["tech"].calls == [], f"'tech' haette ebenfalls NICHT real befragt werden duerfen: {drivers2['tech'].calls}"
        out2 = "\n".join(printed2)
        assert "nicht zuverlaessig lesbar" in out2 and "kontrolliert gesperrt" in out2, out2

        offers_after_2 = [r for r in lobby_service.read_offer_log(run_dir) if r.get("type") == "offer"]
        assert offers_after_2 == offers_after_1, (
            "ein unlesbarer Eintrag darf KEIN neues Angebot erzeugen (weder ein kollidierendes noch ein "
            f"neues): {offers_after_2}"
        )


def test_r31_full_current_including_inventory_reaches_actual_persona_api_wire_body():
    """R3.1 (REVIEW-LOBBY-ANWENDUNG.md §5.1, MAIN-DATENWEGENTSCHEIDUNG.md C):
    der eigene VOLLSTAENDIGE Current (inkl. Inventar, nicht nur `save_id`)
    erreicht den TATSAECHLICHEN API-Wire-Body des eigenen Initiativschritts
    -- real ueber `PersonaApiDriver` gegen einen echten Loopback-Server."""
    from mmo_sim.adapters.persona_api import PersonaApiConfig, PersonaApiDriver
    from mmo_sim.core.persona_state import PersonaStateStore

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = l01._bootstrap_community(
            root, "community-op", ["sniper", "tech"],
        )
        write_test_profile(run_dir)
        for pk in ("sniper", "tech"):
            l01._make_ready(onboarding_dir, states_dir, run_dir, pk)

        ps = PersonaStateStore(schema_path=schema_path)
        save = json.loads((l01._FIX / "sniper.json").read_text(encoding="utf-8"))
        save["save_id"] = "REPO_REGRESSION_OWN_SAVE_ID_331"
        save["characters"][0]["inventory"] = [{"name": "REPO_REGRESSION_OWN_GEAR_774", "quantity": 1}]
        core_store.publish_current_save(run_dir, "sniper", save, ps, states_dir)

        bodies: list[dict] = []

        class _Handler(BaseHTTPRequestHandler):
            def log_message(self, *_a):
                return

            def do_POST(self):
                length = int(self.headers.get("Content-Length", 0) or 0)
                bodies.append(json.loads(self.rfile.read(length)))
                self.server.calls.append(1)  # type: ignore[attr-defined]
                data = json.dumps(
                    {"choices": [{"message": {"content": json.dumps({"action": "pause"})}}]},
                ).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        server = HTTPServer(("127.0.0.1", 0), _Handler)
        server.calls = []  # type: ignore[attr-defined]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            sniper_driver = PersonaApiDriver(
                PersonaApiConfig(base_url=f"http://127.0.0.1:{server.server_address[1]}", api_key="SYNTH", model="synthetic"),
                "sniper",
            )
            tech_driver = l01._ScriptedDriver("tech", ['{"action": "pause"}'])
            drivers = {"sniper": sniper_driver, "tech": tech_driver}
            printed: list[str] = []
            session = l01._session(
                "op", onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
                gm_transport_factory=lambda *_a, **_kw: (_ for _ in ()).throw(
                    AssertionError("kein GM-Call erwartet"),
                ),
                persona_driver_factory=lambda pk: drivers[pk],
                printed=printed,
            )
            session._cmd_lobby_initiative()
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

        assert len(bodies) == 1, "genau EIN echter HTTP-Request von 'sniper' erwartet"
        wire_text = json.dumps(bodies[0], ensure_ascii=False)
        assert "REPO_REGRESSION_OWN_SAVE_ID_331" in wire_text
        assert "REPO_REGRESSION_OWN_GEAR_774" in wire_text, (
            "eigener Inventarinhalt fehlt im tatsaechlichen API-Wire-Body -- nur save_id genuegt nicht"
        )


def test_r32_agreed_activity_reaches_nominated_leaders_first_real_table_decision_call():
    """R3.2 (REVIEW-LOBBY-ANWENDUNG.md §5.2, MAIN-DATENWEGENTSCHEIDUNG.md C):
    sniper schlaegt tech als Leader mit einem eindeutig markierten
    Aktivitaetswunsch vor; tech nimmt an. tech's ERSTER TATSAECHLICHER
    Tischentscheidungsaufruf (kein Angebots-/Consent-Request mehr, ein
    echter Spielzug-Kontext) enthaelt den vereinbarten Wunsch als
    Teilnehmerkontext -- die Persona formuliert ihre Spielnachricht
    weiterhin selbst (kein Harness-Text als `decide()`-Rueckgabe vorgegeben,
    das Testdouble antwortet frei)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _seed(root)

        table_id, section_id = "lobby-sniper-tech", "lobby-sniper-tech-section"
        final_saves = {pk: json.loads((l01._FIX / f"{pk}.json").read_text(encoding="utf-8")) for pk in ("sniper", "tech")}
        gm = l01._TableGM(table_id, section_id, final_saves, turns_before_marker=3)
        sniper_driver = l01._ScriptedDriver("sniper", [
            json.dumps({"action": "propose", "wants": ["tech"], "leader": "tech", "activity": ACTIVITY}),
            "Ich trete bei und lasse tech fuehren.",
            "Ich nehme mit, dass die Runde gut lief.",
        ])
        tech_driver = l01._ScriptedDriver("tech", [
            f"ENTSCHEIDUNG offer_id={lobby_service.offer_id_for('lobby-community-op-0', 'sniper', 0)} "
            "participant_id=tech decision=accept explanation=Ich uebernehme die Leaderrolle.",
            "Meine tatsaechliche, selbst formulierte Spielentscheidung als Leader.",
            "Ende der Runde, bleibt aufmerksam.",
            "Ich nehme mit, dass ich gut gefuehrt habe.",
        ])
        drivers = {"sniper": sniper_driver, "tech": tech_driver}
        printed: list[str] = []
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = (
            l01._SCHEMA, root / "states", root / "run", root / "onboarding", root / "catalog",
        )
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
        assert table.status == "closed" and table.leader == "tech"

        table_calls = [
            ctx for ctx in tech_driver.calls
            if "decision_contract" not in ctx
            and "begrenztes eigenes Lobby-Initiativfenster" not in ctx.get("user", "")
        ]
        assert table_calls, "kein echter Tischentscheidungsaufruf an 'tech' gefunden"
        first_table_ctx = table_calls[0]
        assert ACTIVITY in json.dumps(first_table_ctx, ensure_ascii=False), (
            "vereinbarter Aktivitaetswunsch fehlt im ERSTEN echten Tischentscheidungsaufruf des "
            f"nominierten Leaders: {first_table_ctx}"
        )
        # Die Persona formuliert ihre Spielnachricht weiterhin selbst -- das
        # Testdouble antwortet mit eigenem Text (der GM erhaelt den Text PLUS
        # den Import-Save-Block auf dem ersten Turn, daher Teilstring-Pruefung
        # ueber alle Turns), keine vom Harness erzwungene Mission/HQ-
        # Ausfuehrung ersetzt diese Antwort.
        assert any(
            "Meine tatsaechliche, selbst formulierte Spielentscheidung als Leader." in call
            for call in gm.calls
        ), gm.calls


if __name__ == "__main__":
    if "--child" in sys.argv:
        ap = argparse.ArgumentParser()
        ap.add_argument("--child", action="store_true")
        ap.add_argument("--root", required=True)
        ap.add_argument("--mode", required=True)
        ap.add_argument("--result", required=True)
        _child_main(ap.parse_args())
        sys.exit(0)

    import traceback

    tests = [
        test_r11_first_proposal_survives_interrupted_offer_log_write_real_restart_positive_repeat,
        test_r2_resolution_write_failure_does_not_spawn_second_table_real_restart_positive_repeat,
        test_r12_new_offer_in_fresh_window_is_not_masked_by_stale_same_pk_turn_resolution,
        test_r13_corrupted_per_entry_window_state_fails_closed_no_reask_no_collision,
        test_r31_full_current_including_inventory_reaches_actual_persona_api_wire_body,
        test_r32_agreed_activity_reaches_nominated_leaders_first_real_table_decision_call,
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
