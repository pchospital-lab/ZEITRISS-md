#!/usr/bin/env python3
"""
tests/mmo_sim/test_r2_hauptbefund2_bound_table_recovery.py — neue dauerhafte
Repo-Regression fuer den R2-Nachzug "Hauptbefund 2" (END-CRITIC.md §4.4,
REVIEW-LOBBY-TISCHWIEDERAUFNAHME.md §4/§5, MAIN-DATENWEGENTSCHEIDUNG-
TISCHWIEDERAUFNAHME.md).

Original+Derivat+Diff (WORKER-REPORT.md-Konvention dieses Repos): dieselbe
I/O-Naht-/GM-Fehlerinjektionstechnik wie die externe Review-Kernprobe
(`tests-review/review_lobby_bound_table_recovery.py` im Lieferpaket, NICHT
Teil dieses Repos) UND wie die bereits bestehende `test_p2_lobby_
application_boundaries.py:test_r2_resolution_write_failure_...` (isolierter
Einzelfehler) -- DERIVAT hier lebt DAUERHAFT im Repo, importiert bestehende
Fixtures aus `test_l01_l10_lobby_initiative.py` (kein zweiter Bootstrap-
Baustein), relauncht sich selbst als eigenstaendigen Subprozess (`--child`,
echte, von Prozess 1 verschiedene Betriebssystem-PID) und ist ueber den
Dateinamen `test_*.py` automatisch in `run_all.py` eingebunden.

Deckt (semantisch angepasst fuer echtes Resume, Entscheidung B,
MAIN-QUELLENENTSCHEIDUNG-RESUME.md, TESTKORREKTUR.md -- die fruehere
Fassung dieser Regression verlangte bei gesunden B1/B2-Quellen noch
`active`/`gm_calls==0` als DAUERZUSTAND; das war der von der Review
korrigierte Zwischenstand, reine Diagnose ist bei gesunden eindeutigen
Quellen KEINE gleichwertige Endloesung mehr):
- B1 (`compound-log-failure`): Offer-, Antwort- UND Resolution-Append
  scheitern in DERSELBEN Runde an DERSELBEN Datei (Audit schluckt zwei
  davon, Resolution propagiert sichtbar) -- der Tisch entsteht `active`,
  bleibt in Prozess 1 ungespielt, das Offer-Log bleibt LEER.
- B2 (`gm-init-failure`): Offer/Antwort/Resolution (`table_bound`) werden
  ALLE erfolgreich geschrieben, nur die GM-Factory wirft einmal -- kein
  Spielstart in Prozess 1, aber die Resolution entfernt das Angebot
  bereits aus der offenen Menge (`reconstruct_pending_offer_events`).
  In BEIDEN Faellen darf ein frischer Folgeprozess NICHT das generische
  "niemand frei" melden (der urspruengliche Fund) -- er muss den `active`,
  gebundenen, ungespielten Tisch ueber `core.store.find_bound_active_
  unplayed_table` erkennen UND ihn jetzt tatsaechlich ueber den
  vorhandenen Spielstart-Pfad (`ui/tui.py:_play_bound_table` ->
  `app_service.run_play_session`) zu Ende spielen: derselbe `table_id`,
  mindestens 3 gescriptete GM-Turns, Tisch danach `closed`, Chrononaut-
  Locks normal freigegeben, veroeffentlichte Currents fuer beide
  Mitglieder, erhaltener Leaderkontext -- OHNE neue Initiativ-/
  Consent-Requests an 'sniper'/'tech' (B1 zieht dabei zusaetzlich die
  fehlende Resolution idempotent nach). Ein DANACH genuin neu
  gestartetes Fenster, in dem beide pausieren, erzeugt weiterhin KEINEN
  zweiten Tisch und KEINEN GM-Aufruf (jetzt aber MIT je einem echten
  Initiativ-Request, weil die Mitglieder nach dem Abschluss wieder frei
  sind) -- das bereits bestehende Verhalten "geschlossener Tisch bleibt
  geschlossen, spaetere neue Runde moeglich" deckt die separate
  `test_hauptbefund2_closed_table_two_full_rounds_...`-Regression weiter
  ab.
- Positive Kontrolle: der bereits bestehende, isolierte Einzelfehlerfall
  (NUR die Resolution scheitert, Offer/Antwort sind durabel) bleibt vom
  neuen Fund UNBERUEHRT -- er erreicht den neuen Zweig gar nicht
  (`confirmed_derivation` wird bereits aus dem weiterhin vollstaendigen
  Offer-Log abgeleitet) und loest weiterhin ueber den bestehenden
  `create_table_from_offer_log`-Resume-Zweig real bis zum Abschluss auf.
- "Geschlossener Tisch bleibt geschlossen, spaetere neue Runde moeglich":
  ein Direkttest von `core.store.find_bound_active_unplayed_table` belegt,
  dass ein bereits GESCHLOSSENER Tisch (auch bei einer widerspruechlichen
  verbliebenen Lock-Eintragung) NIEMALS als wiederaufnehmbar erkannt wird,
  plus ein echter Real-Restart-Zweirunden-Beleg (Runde 1 schliesst
  regulaer, Runde 2 -- neuer Prozess, Mitglieder wieder frei -- legt real
  einen zweiten, unabhaengigen Tisch an)."""
from __future__ import annotations

import argparse
import json
import os
import sys
import subprocess
import tempfile
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
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissTableSizePolicy  # noqa: E402


class _ChildDriver:
    """Markiertes Testdouble fuer den relaunchten Kind-Prozess -- entscheidet
    NUR anhand des tatsaechlichen Kontrollvertrags (Kontexttext), analog
    `test_p2_lobby_application_boundaries.py:_ChildDriver`. `mode='pause'`
    laesst BEIDE pausieren (kein neues Angebot); sonst schlaegt 'sniper'
    'tech' vor, 'tech' akzeptiert real."""

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
        return ParticipantDecision(text=text, origin_source=f"repo-regression-hauptbefund2:{self.pk}")


def _child_main(args: argparse.Namespace) -> None:
    """Laeuft NUR im relaunchten Subprozess (`--child`) -- echte, andere
    Betriebssystem-PID als der aufrufende Testprozess."""
    root = Path(args.root)
    schema_path, states_dir, run_dir = l01._SCHEMA, root / "states", root / "run"
    onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"

    drivers = {pk: _ChildDriver(pk, args.mode) for pk in ("sniper", "tech")}
    gms: list = []
    hits: list[dict] = []

    def gm_transport_factory(tid: str):
        if args.mode == "gm-init-failure" and not hits:
            hits.append({"seam": "real gm factory construction", "error": "RuntimeError"})
            raise RuntimeError("SYNTHETIC GM constructor temporarily unavailable")
        saves = {pk: json.loads((l01._FIX / f"{pk}.json").read_text(encoding="utf-8")) for pk in ("sniper", "tech")}
        for pk, s in saves.items():
            s["save_id"] = f"repo-regression-hauptbefund2-{tid}-{pk}"
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
            if args.mode == "compound-log-failure":
                hits.append({"seam": "real invitation_log append", "number": len(hits) + 1})
                raise OSError("SYNTHETIC persistent I/O failure on invitation log")
            if (
                args.mode == "resolution-write-error" and not hits
                and json.loads(text).get("type") == "resolution"
            ):
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

    # R2-Nachzug (echtes Resume): Leaderkontext-/Currents-Beleg fuer die
    # semantisch angepassten B1/B2-Assertions -- dieselbe Autoritaet wie die
    # externe `review_lobby_resume_phases.py:snapshot`/`check_closed`.
    ps_store = PersonaStateStore(schema_path=schema_path)
    current_ids: dict[str, str | None] = {}
    for pk in ("sniper", "tech"):
        try:
            current = core_store.load_current_save_or_raise(run_dir, pk, ps_store, states_dir)
        except core_store.CurrentSaveUnavailableError:
            current = None
        current_ids[pk] = current.get("save_id") if current else None

    row = {
        "pid": os.getpid(),
        "printed": printed,
        "errors": errors,
        "hits": hits,
        "calls": {pk: len([c for c in d.calls if c["kind"] in ("initiative", "consent")]) for pk, d in drivers.items()},
        "table_notes": {
            pk: [c["context"].get("user") for c in d.calls if c["kind"] == "table"]
            for pk, d in drivers.items()
        },
        "gm_calls": sum(len(g.calls) for g in gms),
        "tables": [read(p, {}) for p in sorted((run_dir / "tables").glob("*.json"))],
        "locks": read(run_dir / "locks.json", {}),
        "current_ids": current_ids,
        "offer_log_present": invitation_log_path.exists() and bool(invitation_log_path.read_text(encoding="utf-8").strip()),
    }
    Path(args.result).write_text(json.dumps(row, indent=2, ensure_ascii=False), encoding="utf-8")


def _run_child(root: Path, mode: str, result_path: Path, limit: int = 2) -> dict:
    """ECHTER, EIGENSTAENDIGER Python-Subprozess (`subprocess.run`) -- die
    zurueckgegebene PID ist von jedem weiteren Aufruf verschieden (L08-
    Muster, `test_p2_lobby_application_boundaries.py:_run_child`)."""
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


_DIAGNOSIS_TOKENS = ("resolution", "wiederaufnahme", "fortsetz", "ungeklaert", "ausstehend")


def _asserts_concrete_pending_diagnosis(printed: list[str], tid: str) -> bool:
    joined = "\n".join(printed).lower()
    return tid.lower() in joined and any(tok in joined for tok in _DIAGNOSIS_TOKENS)


def test_hauptbefund2_b1_compound_log_failure_real_resume_across_repeated_calls():
    """B1 (MAIN-QUELLENENTSCHEIDUNG-RESUME.md Zustand (a), TESTKORREKTUR.md):
    Offer-, Antwort- UND Resolution-Append scheitern in Prozess 1 an
    DERSELBEN Datei (3 Treffer, Offer-Log bleibt LEER). Tisch entsteht
    `active`, kein GM-Call. Prozess 2 (Stoerung entfernt, echte neue PID)
    MUSS den Tisch jetzt tatsaechlich ueber den vorhandenen Spielstart-Pfad
    zu Ende spielen: derselbe `table_id`, mindestens 3 echte GM-Turns,
    Tisch danach `closed`, Locks normal freigegeben, veroeffentlichte
    Currents fuer beide Mitglieder, erhaltener Leaderkontext, die fehlende
    Resolution wird idempotent nachgezogen -- OHNE neuen Request an
    'sniper'/'tech'. Prozess 3 (danach genuin neues Fenster, beide
    pausieren) legt KEINEN zweiten Tisch an und ruft die GM-Factory NICHT
    -- jetzt aber MIT je einem echten Initiativ-Request, weil beide nach
    dem Abschluss wieder frei sind."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _seed(root)

        r1 = _run_child(root, "compound-log-failure", root / "r1.json")
        assert len(r1["hits"]) == 3, r1["hits"]
        assert not r1["errors"], r1["errors"]
        assert not r1["offer_log_present"], "Offer-Log muss nach dem gemeinsamen Ausfall leer bleiben"
        assert len(r1["tables"]) == 1 and r1["tables"][0]["status"] == "active"
        assert r1["gm_calls"] == 0
        tid = r1["tables"][0]["table_id"]

        r2 = _run_child(root, "pause", root / "r2.json")
        assert len(r2["tables"]) == 1 and r2["tables"][0]["table_id"] == tid, (
            f"Resume muss denselben Tisch fortsetzen, kein zweiter Tisch: {r2['tables']}"
        )
        assert r2["tables"][0]["status"] == "closed", "gesunde eindeutige Wiederaufnahme muss tatsaechlich abschliessen"
        assert r2["gm_calls"] >= 3, "mindestens die gescripteten GM-Turns muessen real stattfinden"
        assert r2["tables"][0]["leader"] == "sniper", "Leaderkontext (der urspruenglich abgeleitete Leader) bleibt erhalten"
        assert r2["calls"]["sniper"] == 0 and r2["calls"]["tech"] == 0, (
            f"Resume darf keine neuen Initiativ-/Consent-Requests stellen: {r2['calls']}"
        )
        assert not r2["locks"], "normaler Lock-Release nach gueltigem Abschluss erwartet"
        assert all(v is not None for v in r2["current_ids"].values()), (
            f"veroeffentlichte Currents fuer beide Mitglieder erwartet: {r2['current_ids']}"
        )
        leader_notes = r2["table_notes"]["sniper"]
        assert leader_notes and "Leader" in leader_notes[0], (
            f"der urspruengliche Leader muss seinen Leaderkontext beim Resume erhalten: {leader_notes}"
        )
        assert '"outcome": "table_bound"' in Path(root / "run" / "invitation_decisions.jsonl").read_text(encoding="utf-8"), (
            "B1 muss die fehlende Resolution idempotent nachziehen"
        )

        r3 = _run_child(root, "pause", root / "r3.json")
        assert len(r3["tables"]) == 1 and r3["tables"][0]["table_id"] == tid, (
            f"ein genuin neues Pausenfenster darf keinen zweiten Tisch anlegen: {r3['tables']}"
        )
        assert r3["gm_calls"] == 0, "kein Spielstart aus einem reinen Pausenfenster"
        assert r3["calls"]["sniper"] == 1 and r3["calls"]["tech"] == 1, (
            f"nach dem Abschluss sind beide wieder frei und muessen real neu gefragt werden: {r3['calls']}"
        )


def test_hauptbefund2_b2_gm_init_failure_real_resume_across_repeated_calls():
    """B2 (MAIN-QUELLENENTSCHEIDUNG-RESUME.md Zustand (a)): Offer/Antwort/
    Resolution (`table_bound`) werden in Prozess 1 ALLE erfolgreich
    geschrieben, nur die GM-Factory wirft EINMAL. Prozess 2 (Factory wieder
    gesund) muss den bereits gebundenen, aktiven, ungespielten Tisch trotz
    `reconstruct_pending_offer_events`s Verwurf (Resolution bereits
    vorhanden) real zu Ende spielen (KEINE zweite Resolution -- B2 hat sie
    bereits). Prozess 3 (genuin neues Pausenfenster) legt keinen zweiten
    Tisch an."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _seed(root)

        r1 = _run_child(root, "gm-init-failure", root / "r1.json")
        assert r1["hits"] == [{"seam": "real gm factory construction", "error": "RuntimeError"}]
        assert not r1["errors"], r1["errors"]
        r1_log = Path(root / "run" / "invitation_decisions.jsonl").read_text(encoding="utf-8")
        assert '"outcome": "table_bound"' in r1_log
        assert r1_log.count('"outcome": "table_bound"') == 1
        assert len(r1["tables"]) == 1 and r1["tables"][0]["status"] == "active"
        assert r1["gm_calls"] == 0
        tid = r1["tables"][0]["table_id"]

        r2 = _run_child(root, "pause", root / "r2.json")
        assert len(r2["tables"]) == 1 and r2["tables"][0]["table_id"] == tid
        assert r2["tables"][0]["status"] == "closed"
        assert r2["gm_calls"] >= 3
        assert r2["tables"][0]["leader"] == "sniper"
        assert r2["calls"]["sniper"] == 0 and r2["calls"]["tech"] == 0
        assert not r2["locks"], "normaler Lock-Release nach gueltigem Abschluss erwartet"
        assert all(v is not None for v in r2["current_ids"].values())
        r2_log = Path(root / "run" / "invitation_decisions.jsonl").read_text(encoding="utf-8")
        assert r2_log.count('"outcome": "table_bound"') == 1, (
            "B2 hat seine Resolution bereits -- kein zweiter Resolution-Eintrag beim Resume erwartet"
        )

        r3 = _run_child(root, "pause", root / "r3.json")
        assert len(r3["tables"]) == 1 and r3["tables"][0]["table_id"] == tid
        assert r3["gm_calls"] == 0
        assert r3["calls"]["sniper"] == 1 and r3["calls"]["tech"] == 1


def test_hauptbefund2_ambiguous_authority_multiple_candidates_stays_diagnosis_only():
    """Echte Unklarheitsfaelle bleiben abgedeckt (§C, MAIN-QUELLENENTSCHEIDUNG-
    RESUME.md Zustand (b)): verweisen die gebundenen Mitglieder auf MEHR als
    eine Tisch-ID, bleibt es bei der kontrollierten Diagnosemeldung -- KEIN
    automatischer Spielstart, KEIN Request an eine Persona, KEIN Unlock.
    Direkter Beleg auf Ebene von `_cmd_lobby_initiative` selbst (nicht nur
    am unit-getesteten `find_bound_active_unplayed_table`,
    s. `test_find_bound_active_unplayed_table_unit_guards`) -- die
    Persona-/GM-Factories werfen, wenn sie ueberhaupt aufgerufen wuerden."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = l01._bootstrap_community(
            root, "community-op", ["sniper", "tech"],
        )
        write_test_profile(run_dir)
        chrono_ids = {pk: l01._make_ready(onboarding_dir, states_dir, run_dir, pk) for pk in ("sniper", "tech")}

        lobby = core_store.Lobby(run_dir, ZeitrissTableSizePolicy())
        for pk, tid in (("sniper", "lobby-sniper-tech"), ("tech", "lobby-sniper-tech__2")):
            table = core_store.Table(
                table_id=tid, leader=pk, members=[pk], chrononaut_ids={pk: chrono_ids[pk]},
                run_dir=run_dir, status="active", operator_meta={"offer_log": []},
            )
            table.persist()
            lobby.lock_chrononaut(chrono_ids[pk], tid)

        def _forbidden_driver(pk):
            raise AssertionError(f"kein Persona-Request im ambigen Fall erwartet ({pk})")

        def _forbidden_gm(tid):
            raise AssertionError(f"kein Spielstart im ambigen Fall erwartet ({tid})")

        printed: list[str] = []
        session = l01._session(
            "op", onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
            gm_transport_factory=_forbidden_gm, persona_driver_factory=_forbidden_driver,
            printed=printed,
        )
        session._cmd_lobby_initiative()

        assert _asserts_concrete_pending_diagnosis(printed, "lobby-sniper-tech"), printed
        assert not any("niemand frei" in p.lower() for p in printed)
        locks = json.loads((run_dir / "locks.json").read_text(encoding="utf-8"))
        assert locks == {chrono_ids["sniper"]: "lobby-sniper-tech", chrono_ids["tech"]: "lobby-sniper-tech__2"}, locks
        for tid in ("lobby-sniper-tech", "lobby-sniper-tech__2"):
            data = json.loads((run_dir / "tables" / f"{tid}.json").read_text(encoding="utf-8"))
            assert data["status"] == "active" and not data["sl_log"]


def test_hauptbefund2_positive_control_isolated_resolution_failure_unaffected_by_new_check():
    """Positive Kontrolle: der bereits bestehende ISOLIERTE Einzelfehlerfall
    (NUR die Resolution scheitert, Offer+Antwort bleiben durabel im Log --
    identische Injektionstechnik wie `test_p2_lobby_application_boundaries.
    py:test_r2_resolution_write_failure_...`) erreicht den NEUEN Zweig gar
    nicht (`confirmed_derivation` wird bereits aus dem weiterhin
    vollstaendigen Offer-Log real abgeleitet) und loest weiterhin ueber den
    BESTEHENDEN `create_table_from_offer_log`-Resume-Zweig real bis zum
    Abschluss auf -- der neue Fund darf diesen bereits funktionierenden Pfad
    nicht regredieren."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _seed(root)

        r1 = _run_child(root, "resolution-write-error", root / "r1.json")
        assert r1["hits"] == [{"seam": "real invitation_log append", "type": "resolution"}]
        assert not r1["errors"], r1["errors"]
        assert r1["offer_log_present"], "Offer/Antwort bleiben trotz Resolutionsfehler durabel"
        assert len(r1["tables"]) == 1 and r1["tables"][0]["status"] == "active"
        assert r1["gm_calls"] == 0
        tid = r1["tables"][0]["table_id"]

        r2 = _run_child(root, "pause", root / "r2.json")
        assert len(r2["tables"]) == 1 and r2["tables"][0]["table_id"] == tid
        assert r2["tables"][0]["status"] == "closed", (
            "der bestehende Resume-Zweig (vollstaendiges Offer-Log) muss den Tisch weiterhin real "
            f"bis zum Abschluss fortsetzen: {r2}"
        )
        assert r2["gm_calls"] > 0, "echter Spielstart ueber den bestehenden Resume-Zweig erwartet"
        assert r2["calls"]["sniper"] == 0 and r2["calls"]["tech"] == 0, (
            "kein erneuter echter Lobby-Request fuer eine bereits vollstaendig angenommene Zustimmung"
        )


def test_hauptbefund2_closed_table_two_full_rounds_real_restart_new_round_possible():
    """"Geschlossener Tisch bleibt geschlossen, spaetere neue Runde
    moeglich" (Main-Zustandstabelle, Erhalt): Runde 1 (echter Prozess) ist
    ein voellig gesunder Durchlauf und schliesst regulaer. Runde 2 (echter
    neuer Prozess, andere PID) findet BEIDE Mitglieder wieder frei (Locks
    beim Abschluss real geloest) und legt real einen ZWEITEN, unabhaengigen
    Tisch (`__2`-Generation) an -- der neue Hauptbefund-2-Zweig greift hier
    NICHT ein (`bound` ist beim Rundenstart leer)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _seed(root)

        r1 = _run_child(root, "journey", root / "r1.json")
        assert not r1["errors"], r1["errors"]
        assert len(r1["tables"]) == 1 and r1["tables"][0]["status"] == "closed"
        assert r1["gm_calls"] > 0
        tid1 = r1["tables"][0]["table_id"]

        r2 = _run_child(root, "journey", root / "r2.json")
        assert not r2["errors"], r2["errors"]
        assert r2["calls"]["sniper"] == 1 and r2["calls"]["tech"] == 1, (
            f"nach einem regulaeren Abschluss muessen beide Mitglieder in einer NEUEN Runde real erneut "
            f"gefragt werden koennen: {r2['calls']}"
        )
        assert len(r2["tables"]) == 2, f"eine bewusste neue spaetere Runde muss real einen zweiten Tisch anlegen koennen: {r2['tables']}"
        ids = sorted(t["table_id"] for t in r2["tables"])
        assert ids[0] == tid1 and ids[1] == f"{tid1}__2", ids
        assert all(t["status"] == "closed" for t in r2["tables"])


def _write_table(run_dir: Path, table_id: str, status: str, sl_log=None) -> core_store.Table:
    table = core_store.Table(
        table_id=table_id, leader="sniper", members=["sniper", "tech"],
        chrononaut_ids={"sniper": "CHR-SNIPER-001", "tech": "CHR-TECH-001"},
        run_dir=run_dir, status=status, sl_log=sl_log or [],
        operator_meta={"source_offer_id": f"lobby-offer-{table_id}-sniper-0"},
    )
    table.persist()
    return table


def test_find_bound_active_unplayed_table_unit_guards():
    """Direkttest von `core.store.find_bound_active_unplayed_table` (der
    kleine, in diesem Nachzug neu ergaenzte Lese-Helfer) -- schnell,
    deterministisch, ohne Subprozess-Overhead. Belegt ALLE in seinem
    Docstring aufgezaehlten fail-closed-Grenzen einzeln, insbesondere:
    ein bereits GESCHLOSSENER Tisch wird NIEMALS wiederbelebt, auch nicht
    bei einer widerspruechlichen verbliebenen Lock-Eintragung."""
    ready_ids = {"sniper": "CHR-SNIPER-001", "tech": "CHR-TECH-001"}

    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        (run_dir / "tables").mkdir(parents=True)
        (run_dir / "completion").mkdir(parents=True)
        table = _write_table(run_dir, "lobby-sniper-tech", status="active")
        bound = {"sniper": table.table_id, "tech": table.table_id}

        found = core_store.find_bound_active_unplayed_table(run_dir, ready_ids, bound)
        assert found is not None and found.table_id == table.table_id, "positiver Fall muss den Tisch liefern"

    # Geschlossener Tisch + widerspruechlich verbliebene Lock-Eintragung
    # (z.B. Abbruch zwischen Lock-Release und Statuswechsel) darf NIE als
    # wiederaufnehmbar gelten.
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        (run_dir / "tables").mkdir(parents=True)
        (run_dir / "completion").mkdir(parents=True)
        table = _write_table(run_dir, "lobby-sniper-tech", status="closed")
        bound = {"sniper": table.table_id, "tech": table.table_id}
        assert core_store.find_bound_active_unplayed_table(run_dir, ready_ids, bound) is None

    # Uneindeutig: gebundene Mitglieder verweisen auf ZWEI verschiedene
    # Tisch-IDs -- kein Raten, welcher "der" Tisch ist.
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        (run_dir / "tables").mkdir(parents=True)
        (run_dir / "completion").mkdir(parents=True)
        _write_table(run_dir, "lobby-sniper-tech", status="active")
        _write_table(run_dir, "lobby-sniper-tech__2", status="active")
        bound = {"sniper": "lobby-sniper-tech", "tech": "lobby-sniper-tech__2"}
        assert core_store.find_bound_active_unplayed_table(run_dir, ready_ids, bound) is None

    # Konsistenzabgleich: die uebergebenen bereiten chrononaut_ids weichen
    # von `Table.chrononaut_ids` ab -- kein fremder/zufaellig gleichnamiger
    # Tisch wird als Treffer akzeptiert.
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        (run_dir / "tables").mkdir(parents=True)
        (run_dir / "completion").mkdir(parents=True)
        table = _write_table(run_dir, "lobby-sniper-tech", status="active")
        bound = {"sniper": table.table_id, "tech": table.table_id}
        mismatched_ready_ids = {"sniper": "CHR-SNIPER-001", "tech": "CHR-OTHER-999"}
        assert core_store.find_bound_active_unplayed_table(run_dir, mismatched_ready_ids, bound) is None

    # Bereits gespielt (`sl_log` nicht leer) -- kein "ungespielter" Tisch mehr.
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        (run_dir / "tables").mkdir(parents=True)
        (run_dir / "completion").mkdir(parents=True)
        table = _write_table(run_dir, "lobby-sniper-tech", status="active", sl_log=[{"turn": 1}])
        bound = {"sniper": table.table_id, "tech": table.table_id}
        assert core_store.find_bound_active_unplayed_table(run_dir, ready_ids, bound) is None

    # Bereits ein offener Abschnitt (`__plan.json` ohne `__final.json`) --
    # das ist der bestehende, hier NICHT angefasste Resume-Pfad fuer einen
    # BEGONNENEN Abschnitt (`_open_completion_order_for_table`), kein Fall
    # fuer diesen neuen Helfer.
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        (run_dir / "tables").mkdir(parents=True)
        (run_dir / "completion").mkdir(parents=True)
        table = _write_table(run_dir, "lobby-sniper-tech", status="active")
        (run_dir / "completion" / f"{table.table_id}-section__plan.json").write_text(
            json.dumps({"section_id": f"{table.table_id}-section", "table_id": table.table_id}),
            encoding="utf-8",
        )
        bound = {"sniper": table.table_id, "tech": table.table_id}
        assert core_store.find_bound_active_unplayed_table(run_dir, ready_ids, bound) is None


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
        test_hauptbefund2_b1_compound_log_failure_real_resume_across_repeated_calls,
        test_hauptbefund2_b2_gm_init_failure_real_resume_across_repeated_calls,
        test_hauptbefund2_ambiguous_authority_multiple_candidates_stays_diagnosis_only,
        test_hauptbefund2_positive_control_isolated_resolution_failure_unaffected_by_new_check,
        test_hauptbefund2_closed_table_two_full_rounds_real_restart_new_round_possible,
        test_find_bound_active_unplayed_table_unit_guards,
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
