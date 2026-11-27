#!/usr/bin/env python3
"""
tests/mmo_sim/test_discard_unplayed_solo_section_20261126.py --
ZR-DISCARD-UNPLAYED-SOLO-20261126 (Linus-Fix, PR3321-Stage-5-Nachzug).

Problem (enge Produktluecke, gegen Main #3321 verifiziert): ein eigener,
tatsaechlich unbenutzter Solo-Abschnitt (kein Zug, keine SL-Antwort) hielt
die Figurenbindung dauerhaft fest -- `/abbrechen` existiert an dieser
Stelle noch nicht (der Rundenaufruf hat noch nicht begonnen), `/pause`
pausiert nur. Die Figur konnte dadurch NIE an einem neuen Tisch
teilnehmen (unbedingte Lock-Gate in `store.create_table_from_offer_log`).

Fix: `TuiSession._cmd_menu_fortsetzen` (tui.py:2947) bietet im bestehenden
Resume-Zweig (`card.chrononaut_id is not None and card.open_section_id is
not None`), VOR jedem Modell-/Persona-/Reflexionscall, fuer einen
beweisbar-unbenutzten EIGENEN Solo-Abschnitt (`TuiSession.
_discard_unplayed_solo_eligible`) zusaetzlich die ausdrueckliche,
zweifach bestaetigte Wahl "Ungespielten Abschnitt verwerfen" an. Nutzt
intern denselben atomaren Entscheid-Slot (`core.admission.
try_commit_table_decision(..., "stopped")`) und denselben bestehenden
Helper (`_finalize_genuine_table_abort`, `operator_table_key=None`) wie
der produktive Betreiber-/Gast-Abbruchpfad (`_cmd_table_... /abbrechen`).

RED-Nachweis (Ausgangsstand ohne Fixbytes): `git stash` auf diesem Branch
entfernt GENAU den Fix (tui.py/store.py/request_ledger.py); dieser Test
schlaegt dann mit `AttributeError: 'TuiSession' object has no attribute
'_discard_unplayed_solo_eligible'` fehl (kein Verwurfsweg vorhanden) --
exakt der im Problemabschnitt beschriebene Zustand (Abschnitt bleibt
`active`/gelockt). Siehe worker/discard-fix-report.md fuer den
tatsaechlichen RED-Lauf-Output.

Jeder Fake-Transport (`_ExplodingGm`) wirft SOFORT bei `.turn()` --
Beweis fuer '0 Modell-/Transportcalls' in jedem Testfall, der den Fix
selbst durchlaeuft (kein Testfall hier ruft je tatsaechlich einen GM-Turn
aus). Isolierte temp `run_dir` je Test (`tempfile.TemporaryDirectory`).

Pure Python, nur `assert`, echter Exitcode, `unittest`-entdeckbar."""
from __future__ import annotations

import json
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.core import admission as core_admission  # noqa: E402
from mmo_sim.core import request_ledger  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


class _ExplodingGm:
    """Explodierender Fake-Transport: JEDER `.turn()`-Aufruf ist ein
    Testfehler -- der Beweis fuer '0 Modell-/Transportcalls'."""

    def __init__(self):
        self.calls = 0

    def turn(self, *a, **kw):
        self.calls += 1
        raise AssertionError("GM-Transport wurde aufgerufen -- 0 Calls erwartet (Discard-unplayed-solo-section).")


def _eof_input(prompt: str = "") -> str:
    raise EOFError()


def _queued_input(values):
    q = list(values)

    def _fn(prompt: str = "") -> str:
        if q:
            return q.pop(0)
        raise EOFError()

    return _fn


def _make_env(root: Path):
    run_dir, states_dir = root / "run", root / "states"
    onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
    run_dir.mkdir(parents=True, exist_ok=True)
    states_dir.mkdir(parents=True, exist_ok=True)
    write_test_profile(run_dir, max_turns=200)
    return run_dir, states_dir, onboarding_dir, catalog_dir


def _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid: str, char_id: str) -> dict:
    save = full_v7_save(char_id, name=pid, save_id=f"fixture-{pid}-001", level=1)
    ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
    onboarding.start_or_resume(onboarding_dir, pid)
    onboarding.complete_with_save(onboarding_dir, pid, save, ZeitrissHarvestValidator(), char_id)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, pid, char_id, save)
    core_store.publish_current_save(run_dir, pid, save, ps_store, states_dir)
    catalog.register(catalog_dir, catalog.CatalogEntry(participant_id=pid, chrononaut_id=char_id, persona_key=pid))
    catalog.bind_for_section(catalog_dir, pid, char_id, has_open_section=False)
    return save


def _create_unplayed_solo_table(run_dir, states_dir, onboarding_dir, catalog_dir, pid: str) -> str:
    """Baut ueber den ECHTEN Produktweg (`_cmd_local_round([])`) einen
    unbenutzten Solo-Tisch: die Eingabequeue ist bereits VOR dem ersten
    Zug erschoepft (EOF) -- `create_table_from_offer_log` laeuft bereits
    VOR jedem Eingabe-/GM-Request, der Tisch bleibt mit `sl_log=[]`
    zurueck. Liefert die tatsaechliche `table_id` (empirisch bestaetigt:
    `local-<pid>`, s. `store.py:create_table_from_offer_log`-Formel)."""
    spy = _ExplodingGm()
    session = TuiSession(
        onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=pid,
        input_fn=_eof_input, print_fn=lambda *_a: None,
        run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
        gm_transport_factory=lambda *a, **kw: spy, host_capable=True,
    )
    try:
        session._cmd_local_round([])
    except EndOfInput:
        pass
    assert spy.calls == 0, "Tischanlage allein darf keinen GM-Call ausloesen."
    tables = list((run_dir / "tables").glob("*.json"))
    assert len(tables) == 1, tables
    data = json.loads(tables[0].read_text(encoding="utf-8"))
    assert data["status"] == "active" and data["sl_log"] == [] and data["members"] == [pid], data
    return tables[0].stem


def _fresh_session(run_dir, states_dir, onboarding_dir, catalog_dir, pid, input_values, printed, gm_spy=None):
    gm_spy = gm_spy if gm_spy is not None else _ExplodingGm()
    return TuiSession(
        onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=pid,
        input_fn=_queued_input(input_values), print_fn=printed.append,
        run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
        gm_transport_factory=lambda *a, **kw: gm_spy, host_capable=True,
    ), gm_spy


def _current_save_bytes(run_dir: Path, pid: str) -> bytes:
    p = run_dir / "current_saves" / f"{pid}.json"
    return p.read_bytes() if p.exists() else b""


# --------------------------------------------------------------------------
# Proof 1/2: normaler Terminalweg VOR dem ersten Zug, ausdrueckliche
# Bestaetigung verwirft + gibt NUR die eigene Figur frei.
# --------------------------------------------------------------------------

def test_explicit_double_confirmation_discards_and_releases_only_own_binding():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = _make_env(root)
        pid, char_id = "owner1", "CHR-OWNER1"
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid, char_id)
        table_id = _create_unplayed_solo_table(run_dir, states_dir, onboarding_dir, catalog_dir, pid)

        save_before = _current_save_bytes(run_dir, pid)
        printed: list[str] = []
        session, gm_spy = _fresh_session(
            run_dir, states_dir, onboarding_dir, catalog_dir, pid, ["2", "j"], printed,
        )
        session._cmd_menu_fortsetzen()

        out = "\n".join(printed)
        assert "wirklich verworfen" in out and "ENDGUELTIG" in out, out
        assert "bleibt unveraendert erhalten" in out, out

        table_data = json.loads((run_dir / "tables" / f"{table_id}.json").read_text(encoding="utf-8"))
        assert table_data["status"] == "closed", table_data

        decision = core_admission.read_table_decision(run_dir, table_id)
        assert decision is not None and decision.get("decision") == "stopped", decision

        lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby.is_locked(char_id) is None, "eigene Figurenbindung haette freigegeben werden muessen."

        assert gm_spy.calls == 0, "0 Modell-/Transportcalls erwartet."
        assert request_ledger.records_for_table(run_dir, table_id) == [], (
            "0 neue Request-Reservierungen erwartet."
        )
        assert _current_save_bytes(run_dir, pid) == save_before, (
            "persoenliche Persistenz (Current) haette unveraendert bleiben muessen -- kein Save/Ernte."
        )


# --------------------------------------------------------------------------
# Proof: Ablehnung/Zurueck an JEDER Stelle ⇒ KEIN Verwurf.
# --------------------------------------------------------------------------

def test_choice_one_keeps_default_resume_behavior_no_discard():
    """Waehlt der Spieler [1] Fortsetzen, bleibt das heutige Resume-
    Verhalten bytegleich (`_resume_bound_table` wird aufgerufen) -- hier
    erschoepft die Eingabequeue direkt danach (EOF), der Abschnitt bleibt
    deshalb `active`/gelockt, aber OHNE jeden gefallenen Entscheid."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = _make_env(root)
        pid, char_id = "owner1", "CHR-OWNER1"
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid, char_id)
        table_id = _create_unplayed_solo_table(run_dir, states_dir, onboarding_dir, catalog_dir, pid)

        printed: list[str] = []
        session, gm_spy = _fresh_session(
            run_dir, states_dir, onboarding_dir, catalog_dir, pid, ["1"], printed,
        )
        try:
            session._cmd_menu_fortsetzen()
            raise AssertionError("Resume mit erschoepfter Eingabequeue muss ueber EndOfInput zurueckkehren.")
        except EndOfInput:
            pass

        table_data = json.loads((run_dir / "tables" / f"{table_id}.json").read_text(encoding="utf-8"))
        assert table_data["status"] == "active", table_data
        lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby.is_locked(char_id) == table_id, "Bindung bleibt bei [1] Fortsetzen unveraendert."
        assert core_admission.read_table_decision(run_dir, table_id) is None
        assert gm_spy.calls == 0


def test_rejecting_second_confirmation_keeps_section_bound_no_discard():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = _make_env(root)
        pid, char_id = "owner1", "CHR-OWNER1"
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid, char_id)
        table_id = _create_unplayed_solo_table(run_dir, states_dir, onboarding_dir, catalog_dir, pid)

        printed: list[str] = []
        session, gm_spy = _fresh_session(
            run_dir, states_dir, onboarding_dir, catalog_dir, pid, ["2", "n"], printed,
        )
        session._cmd_menu_fortsetzen()

        out = "\n".join(printed)
        assert "Kein Verwurf" in out, out
        assert "wirklich verworfen" not in out, out

        table_data = json.loads((run_dir / "tables" / f"{table_id}.json").read_text(encoding="utf-8"))
        assert table_data["status"] == "active", table_data
        lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby.is_locked(char_id) == table_id
        assert core_admission.read_table_decision(run_dir, table_id) is None
        assert gm_spy.calls == 0


def test_zurueck_at_first_prompt_cancels_without_resume_or_discard():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = _make_env(root)
        pid, char_id = "owner1", "CHR-OWNER1"
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid, char_id)
        table_id = _create_unplayed_solo_table(run_dir, states_dir, onboarding_dir, catalog_dir, pid)

        printed: list[str] = []
        session, gm_spy = _fresh_session(
            run_dir, states_dir, onboarding_dir, catalog_dir, pid, ["/zurueck"], printed,
        )
        # Kein Exception erwartet -- '/zurueck' am NEUEN Wahlprompt bricht
        # kontrolliert ab (reiner `return`), OHNE `_resume_bound_table`
        # jemals zu erreichen (anders als [1], das die Eingabequeue weiter
        # konsumiert und bei Erschoepfung ueber EndOfInput zurueckkehrt).
        session._cmd_menu_fortsetzen()

        out = "\n".join(printed)
        assert "Abgebrochen" in out, out
        table_data = json.loads((run_dir / "tables" / f"{table_id}.json").read_text(encoding="utf-8"))
        assert table_data["status"] == "active", table_data
        assert core_admission.read_table_decision(run_dir, table_id) is None
        assert gm_spy.calls == 0


# --------------------------------------------------------------------------
# Proof 4: dauerhafter Abbruch -> danach erlaubte neue Gruppenbildung mit
# derselben Figur (Lock ist frei).
# --------------------------------------------------------------------------

def test_discard_then_allows_new_round_with_same_figure():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = _make_env(root)
        pid, char_id = "owner1", "CHR-OWNER1"
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid, char_id)
        table_id = _create_unplayed_solo_table(run_dir, states_dir, onboarding_dir, catalog_dir, pid)

        printed: list[str] = []
        session, _spy = _fresh_session(
            run_dir, states_dir, onboarding_dir, catalog_dir, pid, ["2", "j"], printed,
        )
        session._cmd_menu_fortsetzen()
        lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby.is_locked(char_id) is None

        # Neue Session, neuer Fortsetzen-Aufruf: `card.open_section_id` ist
        # jetzt `None` (kein Lock mehr) -- der normale Solo-Fallback
        # (`_cmd_local_round([])`) greift, OHNE vom alten Lock blockiert zu
        # werden. `create_table_from_offer_log` zaehlt die Generation hoch
        # (`local-owner1__2`), weil `local-owner1` bereits `closed` ist.
        printed2: list[str] = []
        session2, spy2 = _fresh_session(
            run_dir, states_dir, onboarding_dir, catalog_dir, pid, [], printed2,
        )
        try:
            session2._cmd_menu_fortsetzen()
        except EndOfInput:
            pass
        assert spy2.calls == 0

        tables_after = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in (run_dir / "tables").glob("*.json")}
        assert table_id in tables_after and tables_after[table_id]["status"] == "closed"
        new_tables = [tid for tid in tables_after if tid != table_id]
        assert len(new_tables) == 1, tables_after
        assert tables_after[new_tables[0]]["status"] == "active"
        assert tables_after[new_tables[0]]["members"] == [pid]
        lobby2 = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby2.is_locked(char_id) == new_tables[0], (
            "die neue Runde haette dieselbe Figur wieder binden muessen koennen (Lock frei)."
        )


# --------------------------------------------------------------------------
# Proof 5a: idempotenter Retry (zweiter Verwurf = No-op-Erfolg).
# --------------------------------------------------------------------------

def test_idempotent_retry_second_discard_call_is_noop_success():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = _make_env(root)
        pid, char_id = "owner1", "CHR-OWNER1"
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid, char_id)
        table_id = _create_unplayed_solo_table(run_dir, states_dir, onboarding_dir, catalog_dir, pid)

        printed: list[str] = []
        session, gm_spy = _fresh_session(run_dir, states_dir, onboarding_dir, catalog_dir, pid, [], printed)
        table = core_store.Table.load(run_dir, table_id)
        session._discard_unplayed_solo_section(table, char_id)
        assert "wirklich verworfen" in "\n".join(printed)

        printed2: list[str] = []
        session2, gm_spy2 = _fresh_session(run_dir, states_dir, onboarding_dir, catalog_dir, pid, [], printed2)
        table_reloaded = core_store.Table.load(run_dir, table_id)
        session2._discard_unplayed_solo_section(table_reloaded, char_id)
        out2 = "\n".join(printed2)
        assert "wirklich verworfen" in out2, (
            "ein idempotenter Retry auf einen bereits 'stopped' entschiedenen Tisch bleibt ein "
            "No-op-ERFOLG (kein Fehler, keine zweite Entwertung).", out2,
        )

        table_final = json.loads((run_dir / "tables" / f"{table_id}.json").read_text(encoding="utf-8"))
        assert table_final["status"] == "closed"
        lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby.is_locked(char_id) is None
        assert gm_spy.calls == 0 and gm_spy2.calls == 0


# --------------------------------------------------------------------------
# Proof 5b: gezielte Schreibunterbrechung zwischen "stopped"-Commit und
# Finalize -- Wiederaufnahme bleibt sicher, Lock-Exact-Match haelt.
# --------------------------------------------------------------------------

def test_crash_between_stopped_commit_and_finalize_resumes_safely():
    """Simuliert einen Prozessabsturz GENAU zwischen dem atomaren
    'stopped'-Commit und dem nachfolgenden `_finalize_genuine_table_abort`
    (derselbe Slot, den auch `table_admission.request_table_stop` nutzt):
    der Entscheid-Slot wird HIER bereits unabhaengig (ausserhalb der
    Produktmethode) committet -- genau der Zustand, den ein Absturz NACH
    dem Commit, aber VOR dem Finalize, hinterlassen wuerde. Ein frischer
    Aufruf der Produktmethode muss diesen bereits gefallenen Entscheid
    erkennen und sicher idempotent zu Ende finalisieren (Lock-Exact-Match
    bleibt die alleinige Garantie, s. `release_chrononaut`)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = _make_env(root)
        pid, char_id = "owner1", "CHR-OWNER1"
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid, char_id)
        table_id = _create_unplayed_solo_table(run_dir, states_dir, onboarding_dir, catalog_dir, pid)

        # Der Commit allein (ohne Finalize) -- simulierter Crash-Zustand.
        won, decision = core_admission.try_commit_table_decision(
            run_dir, table_id, "stopped", participant_id=pid, chrononaut_id=char_id,
            reason="Simulierter Crash-Zustand: Commit gewonnen, Finalize nie erreicht.",
        )
        assert won is True, decision
        # Zustand VOR dem (nie erreichten) Finalize: Tisch weiterhin
        # `active`, Lock weiterhin gebunden -- genau das erwartete
        # Zwischenbild eines Absturzes direkt nach dem Commit.
        table_mid = core_store.Table.load(run_dir, table_id)
        assert table_mid.status == "active"
        lobby_mid = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby_mid.is_locked(char_id) == table_id

        # Frischer Prozess-/Sessionaufruf finalisiert den bereits gefallenen
        # Entscheid sicher nach.
        printed: list[str] = []
        session, gm_spy = _fresh_session(run_dir, states_dir, onboarding_dir, catalog_dir, pid, [], printed)
        session._discard_unplayed_solo_section(table_mid, char_id)
        assert "wirklich verworfen" in "\n".join(printed)

        table_final = json.loads((run_dir / "tables" / f"{table_id}.json").read_text(encoding="utf-8"))
        assert table_final["status"] == "closed"
        lobby_final = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby_final.is_locked(char_id) is None
        assert gm_spy.calls == 0


# --------------------------------------------------------------------------
# Proof 6: Gegenproben -- KEIN Verwurf in jeder dieser Konstellationen.
# --------------------------------------------------------------------------

def test_gegenprobe_real_work_sl_log_nonempty_blocks_discard():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = _make_env(root)
        pid, char_id = "owner1", "CHR-OWNER1"
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid, char_id)
        table_id = _create_unplayed_solo_table(run_dir, states_dir, onboarding_dir, catalog_dir, pid)

        table_path = run_dir / "tables" / f"{table_id}.json"
        data = json.loads(table_path.read_text(encoding="utf-8"))
        data["sl_log"] = [{"role": "assistant", "content": "echter Spielzug bereits erfolgt."}]
        table_path.write_text(json.dumps(data), encoding="utf-8")

        session, _spy = _fresh_session(run_dir, states_dir, onboarding_dir, catalog_dir, pid, [], [])
        table = core_store.Table.load(run_dir, table_id)
        assert session._discard_unplayed_solo_eligible(table, char_id) is False


def test_gegenprobe_existing_request_record_blocks_discard_despite_empty_sl_log():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = _make_env(root)
        pid, char_id = "owner1", "CHR-OWNER1"
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid, char_id)
        table_id = _create_unplayed_solo_table(run_dir, states_dir, onboarding_dir, catalog_dir, pid)

        request_ledger.begin(
            run_dir, role="gm", content="irrelevant", reserved_usd=0.0,
            table_id=table_id, section_id=f"{table_id}-section", turn_idx=0, participant=pid,
            dollar_billed=False,
        )
        session, _spy = _fresh_session(run_dir, states_dir, onboarding_dir, catalog_dir, pid, [], [])
        table = core_store.Table.load(run_dir, table_id)
        assert session._discard_unplayed_solo_eligible(table, char_id) is False


def test_gegenprobe_unreadable_history_file_blocks_discard_unlesbar_ne_leer():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = _make_env(root)
        pid, char_id = "owner1", "CHR-OWNER1"
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid, char_id)
        table_id = _create_unplayed_solo_table(run_dir, states_dir, onboarding_dir, catalog_dir, pid)

        history_dir = run_dir / "gm_sessions" / table_id
        history_dir.mkdir(parents=True, exist_ok=True)
        history_path = history_dir / "sl_history.jsonl"
        history_path.write_text("egal", encoding="utf-8")
        history_path.chmod(0o000)
        try:
            session, _spy = _fresh_session(run_dir, states_dir, onboarding_dir, catalog_dir, pid, [], [])
            table = core_store.Table.load(run_dir, table_id)
            assert session._discard_unplayed_solo_eligible(table, char_id) is False, (
                "unlesbar != leer -- eine vorhandene, aber nicht lesbare SL-Historiendatei muss "
                "sicher stoppen, nicht als abwesend/leer durchgehen."
            )
        finally:
            history_path.chmod(0o644)


def test_gegenprobe_open_completion_plan_blocks_discard():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = _make_env(root)
        pid, char_id = "owner1", "CHR-OWNER1"
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid, char_id)
        table_id = _create_unplayed_solo_table(run_dir, states_dir, onboarding_dir, catalog_dir, pid)

        completion_dir = run_dir / "completion"
        completion_dir.mkdir(parents=True, exist_ok=True)
        plan_path = completion_dir / f"{table_id}-section__plan.json"
        plan_path.write_text(json.dumps({"table_id": table_id, "members": {}}), encoding="utf-8")

        session, _spy = _fresh_session(run_dir, states_dir, onboarding_dir, catalog_dir, pid, [], [])
        table = core_store.Table.load(run_dir, table_id)
        assert session._discard_unplayed_solo_eligible(table, char_id) is False, (
            "ein bereits gewonnener Abschlussplan darf NIE durch 'leer verwerfen' entwertet werden."
        )


def test_gegenprobe_multi_person_or_foreign_owner_blocks_discard():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = _make_env(root)
        pid, char_id = "owner1", "CHR-OWNER1"
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid, char_id)
        table_id = _create_unplayed_solo_table(run_dir, states_dir, onboarding_dir, catalog_dir, pid)

        real_table = core_store.Table.load(run_dir, table_id)
        session, _spy = _fresh_session(run_dir, states_dir, onboarding_dir, catalog_dir, pid, [], [])

        # (e) Mehrperson: ein zusaetzliches Mitglied am selben Tisch.
        multi_member_table = core_store.Table(
            table_id=real_table.table_id, leader=pid, members=[pid, "other_pk"],
            chrononaut_ids={pid: char_id, "other_pk": "CHR-OTHER"},
            run_dir=run_dir, sl_log=[], table_messages=[], operator_meta=dict(real_table.operator_meta),
            status="active",
        )
        assert session._discard_unplayed_solo_eligible(multi_member_table, char_id) is False

        # (e) fremder Owner: Leader ist nicht der Aufrufer.
        foreign_leader_table = core_store.Table(
            table_id=real_table.table_id, leader="other_pk", members=[pid],
            chrononaut_ids={pid: char_id}, run_dir=run_dir, sl_log=[], table_messages=[],
            operator_meta=dict(real_table.operator_meta), status="active",
        )
        assert session._discard_unplayed_solo_eligible(foreign_leader_table, char_id) is False

        # Betreiber-Tisch (operator_meta.operator_id gesetzt) -- selbst bei
        # sonst identischer Form kein Solo-Verwurf.
        operator_meta = dict(real_table.operator_meta)
        operator_meta["operator_id"] = pid
        operator_table = core_store.Table(
            table_id=real_table.table_id, leader=pid, members=[pid],
            chrononaut_ids={pid: char_id}, run_dir=run_dir, sl_log=[], table_messages=[],
            operator_meta=operator_meta, status="active",
        )
        assert session._discard_unplayed_solo_eligible(operator_table, char_id) is False


def test_gegenprobe_lock_pointing_at_different_table_blocks_discard():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = _make_env(root)
        pid, char_id = "owner1", "CHR-OWNER1"
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid, char_id)
        table_id = _create_unplayed_solo_table(run_dir, states_dir, onboarding_dir, catalog_dir, pid)
        real_table = core_store.Table.load(run_dir, table_id)

        # Eine fremde/neue Tisch-ID mit sonst identischer, scheinbar
        # beweisbar-unbenutzter Form -- der tatsaechliche Lock zeigt aber
        # weiterhin auf `table_id` (den echten Tisch), NICHT auf diesen.
        decoy_table = core_store.Table(
            table_id=f"{table_id}__decoy", leader=pid, members=[pid],
            chrononaut_ids={pid: char_id}, run_dir=run_dir, sl_log=[], table_messages=[],
            operator_meta=dict(real_table.operator_meta), status="active",
        )
        session, _spy = _fresh_session(run_dir, states_dir, onboarding_dir, catalog_dir, pid, [], [])
        assert session._discard_unplayed_solo_eligible(decoy_table, char_id) is False, (
            "eine Tisch-ID, auf die der tatsaechliche Lock NICHT zeigt, darf nie als beweisbar-"
            "unbenutzt gelten (kein Pop/Verwurf ohne Exact-Match-Lockbindung)."
        )


# --------------------------------------------------------------------------
# "Frischer Prozess" (echter Subprozess, KEIN In-Process-Fake) kann den
# unbenutzten Solo-Abschnitt weiterhin erkennen und verwerfen.
# --------------------------------------------------------------------------

def _run_child(root: Path, mode: str, result_path: Path) -> dict:
    import subprocess

    cmd = [sys.executable, str(Path(__file__).resolve()), "--child", "--mode", mode,
           "--root", str(root), "--result", str(result_path)]
    cp = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if cp.returncode != 0:
        raise RuntimeError(f"child(mode={mode!r}) exit={cp.returncode}:\n{cp.stderr[-4000:]}")
    return json.loads(result_path.read_text(encoding="utf-8"))


def _child_setup(args) -> None:
    root = Path(args.root)
    run_dir, states_dir, onboarding_dir, catalog_dir = _make_env(root)
    pid, char_id = "owner1", "CHR-OWNER1"
    _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid, char_id)
    table_id = _create_unplayed_solo_table(run_dir, states_dir, onboarding_dir, catalog_dir, pid)
    Path(args.result).write_text(json.dumps({"table_id": table_id}), encoding="utf-8")


def _child_discard(args) -> None:
    root = Path(args.root)
    run_dir, states_dir, onboarding_dir, catalog_dir = (
        root / "run", root / "states", root / "onboarding", root / "catalog",
    )
    pid = "owner1"
    printed: list[str] = []
    gm_spy = _ExplodingGm()
    session = TuiSession(
        onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=pid,
        input_fn=_queued_input(["2", "j"]), print_fn=printed.append,
        run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
        gm_transport_factory=lambda *a, **kw: gm_spy, host_capable=True,
    )
    session._cmd_menu_fortsetzen()
    row = {
        "printed": printed, "gm_calls": gm_spy.calls,
        "locks_after": json.loads((run_dir / "locks.json").read_text(encoding="utf-8")),
    }
    Path(args.result).write_text(json.dumps(row), encoding="utf-8")


def test_fresh_os_process_can_discover_and_discard_unused_solo_table():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        r1 = _run_child(root, "setup", root / "r1.json")
        table_id = r1["table_id"]

        r2 = _run_child(root, "discard", root / "r2.json")
        assert r2["gm_calls"] == 0, r2
        assert any("wirklich verworfen" in p for p in r2["printed"]), r2["printed"]
        assert r2["locks_after"] == {}, r2

        table_data = json.loads((root / "run" / "tables" / f"{table_id}.json").read_text(encoding="utf-8"))
        assert table_data["status"] == "closed", table_data


# --------------------------------------------------------------------------
# Rework (2026-11-27, TOCTOU/Concurrency-Haertung): zwei Regressionstests
# fuer die beiden in worker/discard-rework-report.md belegten Luecken.
# RED/GRUEN-Beleg via manuellem Revert/Reapply der beiden Rework-Hunks in
# tui.py (NICHT via run_all.py im selben Command) -- s. Report.
# --------------------------------------------------------------------------

def test_concurrent_lab_writer_during_confirmation_window_is_not_clobbered():
    """TOCTOU-Kernbeweis: zwischen Eligibility-Check und atomarem Commit
    liegen zwei unbegrenzte j/n-Prompts. Patcht `_readline_with_controls`
    so, dass GENAU die Bestaetigungsfrage ('Ungespielten Abschnitt
    verwerfen -- Bestaetigung') als Seiteneffekt ZUERST einen echten
    `sl_log`-Eintrag ueber eine frische `Table.load`->`persist` auf Platte
    schreibt und DANN `('j', None)` liefert -- simuliert einen
    konkurrierenden Lab-Batch-Writer auf demselben Tisch, WAEHREND der
    Mensch noch am zweiten Prompt sitzt. Ohne den Fresh-Reload-Re-Check
    (FIX 2) wuerde der anschliessende `_finalize_genuine_table_abort` den
    VOR den Prompts geladenen Stale-`table` persistieren und den
    konkurrent geschriebenen Fortschritt mit `[]` ueberschreiben (Wholesale-
    Write, kein Merge, s. `store.py:299-310`)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = _make_env(root)
        pid, char_id = "owner1", "CHR-OWNER1"
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid, char_id)
        table_id = _create_unplayed_solo_table(run_dir, states_dir, onboarding_dir, catalog_dir, pid)

        printed: list[str] = []
        session, gm_spy = _fresh_session(
            run_dir, states_dir, onboarding_dir, catalog_dir, pid, ["2"], printed,
        )
        concurrent_entry = {"role": "assistant", "content": "konkurrierender Lab-Schreiber (TOCTOU-Probe)."}
        original_readline = session._readline_with_controls

        def _patched_readline(prompt, *, context, **kwargs):
            if context == "Ungespielten Abschnitt verwerfen -- Bestaetigung":
                concurrent_table = core_store.Table.load(run_dir, table_id)
                concurrent_table.sl_log.append(concurrent_entry)
                concurrent_table.persist()
                return "j", None
            return original_readline(prompt, context=context, **kwargs)

        session._readline_with_controls = _patched_readline
        session._cmd_menu_fortsetzen()

        out = "\n".join(printed)
        assert "nicht moeglich" in out, out
        assert "wirklich verworfen" not in out, (
            "ein waehrend der Bestaetigung konkurrierend bespielter Abschnitt darf NICHT "
            "verworfen werden.", out,
        )

        assert core_admission.read_table_decision(run_dir, table_id) is None, (
            "kein 'stopped'-Entscheid-Slot darf fuer einen zwischenzeitlich bespielten "
            "Abschnitt angelegt werden."
        )
        lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby.is_locked(char_id) == table_id, (
            "die Figurenbindung des Owners bleibt bei sicherem Abbruch gebunden."
        )
        table_on_disk = json.loads((run_dir / "tables" / f"{table_id}.json").read_text(encoding="utf-8"))
        assert table_on_disk["status"] == "active", table_on_disk
        assert table_on_disk["sl_log"] == [concurrent_entry], (
            "der konkurrent geschriebene sl_log-Eintrag muss auf Platte unveraendert erhalten "
            "bleiben, NICHT auf [] zurueckgesetzt werden.", table_on_disk,
        )
        assert gm_spy.calls == 0


def test_lab_guard_blocks_discard_offer_during_active_lab_run():
    """Lab-Guard-Probe: ein lebender fremder Lab-Lock (`lab.lock.json` mit
    der PID eines echten, laufenden Subprozesses -- dasselbe Muster wie
    `test_g05_error_redaction_and_guards.py:
    test_registration_write_blocked_by_foreign_lab_lock`) blockiert den
    Discard-Angebotspfad GENAU wie `_resume_bound_table` (tui.py:3294) --
    OHNE FIX 1 bot `_cmd_menu_fortsetzen` den Verwurf trotz aktivem
    Lab-Lauf weiterhin an (zweiter schreibender Controller unbewacht)."""
    import subprocess
    import time as _time

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = _make_env(root)
        pid, char_id = "owner1", "CHR-OWNER1"
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid, char_id)
        table_id = _create_unplayed_solo_table(run_dir, states_dir, onboarding_dir, catalog_dir, pid)

        save_before = (run_dir / "tables" / f"{table_id}.json").read_bytes()

        foreign = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        try:
            deadline = _time.monotonic() + 5.0
            while foreign.poll() is not None and _time.monotonic() < deadline:
                _time.sleep(0.05)
            assert foreign.poll() is None, "Fremdprozess fuer den Lock-Test ist nicht am Leben"

            (run_dir / "lab.lock.json").write_text(
                json.dumps({"pid": foreign.pid}), encoding="utf-8",
            )

            printed: list[str] = []
            session, gm_spy = _fresh_session(
                run_dir, states_dir, onboarding_dir, catalog_dir, pid, [], printed,
            )
            session._cmd_menu_fortsetzen()

            out = "\n".join(printed)
            assert "aktiver Lab-Lauf" in out and f"pid={foreign.pid}" in out, out
            assert "NICHT gespielt" not in out, (
                "das Discard-Angebot ([1]/[2]-Prompt) darf bei aktivem Lab-Lauf gar nicht erst "
                "erscheinen.", out,
            )
            assert gm_spy.calls == 0

            assert core_admission.read_table_decision(run_dir, table_id) is None
            lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
            assert lobby.is_locked(char_id) == table_id
            save_after = (run_dir / "tables" / f"{table_id}.json").read_bytes()
            assert save_after == save_before, "kein Write am Tisch, solange der Lab-Guard blockiert."
        finally:
            foreign.terminate()
            try:
                foreign.wait(timeout=5)
            except subprocess.TimeoutExpired:
                foreign.kill()
                foreign.wait(timeout=5)


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
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
    if "--child" in sys.argv:
        import argparse

        ap = argparse.ArgumentParser()
        ap.add_argument("--child", action="store_true")
        ap.add_argument("--mode", required=True, choices=["setup", "discard"])
        ap.add_argument("--root", required=True)
        ap.add_argument("--result", required=True)
        ns = ap.parse_args()
        if ns.mode == "setup":
            _child_setup(ns)
        else:
            _child_discard(ns)
        sys.exit(0)
    raise SystemExit(main())
