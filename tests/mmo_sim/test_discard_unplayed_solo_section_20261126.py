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
from unittest.mock import patch

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
from mmo_sim.domain.zeitriss.save_correction import group_repair_key  # noqa: E402
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


class _InjectedCrash(RuntimeError):
    """Nachzug N2 (General-Befund, 2026-11-27): simuliert eine echte
    Schreibunterbrechung GENAU an einer benannten Stelle im realen
    `_cmd_menu_fortsetzen`/`_finalize_genuine_table_abort`-Ablauf (dasselbe
    Muster wie `general_discard_probe.py`s `InjectedCrash`), NICHT ueber
    einen direkten Mutator-Aufruf wie `test_crash_between_stopped_commit_
    and_finalize_resumes_safely`."""


def _child_resume_after_crash(args) -> None:
    """Nachzug N2: ECHTER, frischer OS-Prozess (kein In-Process-Fake) ruft
    GENAU den realen Caller `_cmd_menu_fortsetzen()` nach einer zuvor im
    Elternprozess injizierten Schreibunterbrechung auf -- fuer Window 1
    (Lock noch gebunden) UND Window 2 (Lock bereits frei) identisch, der
    Unterschied liegt ausschliesslich im Zustand auf Platte."""
    root = Path(args.root)
    run_dir, states_dir, onboarding_dir, catalog_dir = (
        root / "run", root / "states", root / "onboarding", root / "catalog",
    )
    pid = "owner1"
    printed: list[str] = []
    gm_spy = _ExplodingGm()
    session = TuiSession(
        onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=pid,
        input_fn=_eof_input, print_fn=printed.append,
        run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
        gm_transport_factory=lambda *a, **kw: gm_spy, host_capable=True,
    )
    error = None
    try:
        session._cmd_menu_fortsetzen()
    except (EndOfInput, Exception) as e:
        error = type(e).__name__
    row = {
        "printed": printed, "gm_calls": gm_spy.calls, "error": error,
        "table_ids": sorted(p.stem for p in (run_dir / "tables").glob("*.json")),
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


# --------------------------------------------------------------------------
# Nachzug-Regressionen (General-Befunde N1/N2/N3, 2026-11-27, PR #3322
# MERGE NO-GO -> Nachzug). RED-Beleg je Fall direkt im Docstring/Kommentar;
# zusaetzlich unabhaengig belegt ueber `general_discard_probe.py` (8/8 PASS
# erst MIT diesen drei Fixes, 7 FAIL ohne sie, s. worker/linus-nachzug-
# report.md).
# --------------------------------------------------------------------------


def test_n1_fresh_recheck_blocks_discard_when_request_begins_during_confirmation():
    """N1 (General-Befund N1): der bestehende TOCTOU-Fresh-Reload-Re-Check
    in `_discard_unplayed_solo_section` prueft NUR `sl_log`/`table_messages`
    erneut. Ein waehrend der zwei unbegrenzten Bestaetigungsprompts
    konkurrierend ueber `request_ledger.begin` angelegter Request (z.B. ein
    paralleler Join-/Preis-Check) veraendert `sl_log` NICHT -- blieb daher
    unsichtbar. Patcht `session._input` so, dass GENAU beim zweiten
    Callback (Antwort auf die Bestaetigungsfrage) ZUERST ein echter
    Request-Datensatz entsteht und DANN 'j' geliefert wird -- derselbe
    Trick wie `general_discard_probe.py`s `request_during_confirmation`-
    Fixture.

    RED ohne FIX N1: der schmale Re-Check sieht `sl_log == []` weiterhin,
    committet 'stopped' und finalisiert -- dieser Test schlaegt dann auf
    `table_status == 'active'` (tatsaechlich 'closed') und `decision is
    None` (tatsaechlich 'stopped') fehl; der injizierte Request bliebe
    zusaetzlich verwaist an einem geschlossenen Tisch reserviert."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = _make_env(root)
        pid, char_id = "owner1", "CHR-OWNER1"
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid, char_id)
        table_id = _create_unplayed_solo_table(run_dir, states_dir, onboarding_dir, catalog_dir, pid)
        save_before = _current_save_bytes(run_dir, pid)

        printed: list[str] = []
        session, gm_spy = _fresh_session(run_dir, states_dir, onboarding_dir, catalog_dir, pid, [], printed)
        calls = 0
        injected_request_id = None

        def _concurrent_input(prompt: str = "") -> str:
            nonlocal calls, injected_request_id
            calls += 1
            if calls == 1:
                return "2"
            if calls == 2:
                injected_request_id = request_ledger.begin(
                    run_dir, role="gm", content="konkurrierende Anfrage (N1-Nachzug-Probe).",
                    reserved_usd=0.0, table_id=table_id, section_id=f"{table_id}-section",
                    turn_idx=0, participant=pid, dollar_billed=False,
                )
                return "j"
            raise EOFError()

        session._input = _concurrent_input
        session._cmd_menu_fortsetzen()

        out = "\n".join(printed)
        assert "nicht moeglich" in out, out
        assert "wirklich verworfen" not in out, out
        assert injected_request_id is not None, "Testaufbau defekt -- Request wurde nie injiziert."

        table_data = json.loads((run_dir / "tables" / f"{table_id}.json").read_text(encoding="utf-8"))
        assert table_data["status"] == "active", table_data
        assert core_admission.read_table_decision(run_dir, table_id) is None
        lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby.is_locked(char_id) == table_id
        assert gm_spy.calls == 0
        assert _current_save_bytes(run_dir, pid) == save_before
        records = request_ledger.records_for_table(run_dir, table_id)
        assert len(records) == 1 and records[0]["id"] == injected_request_id, records


def test_n2_window1_stopped_decision_terminal_after_crash_before_finalize():
    """N2 Window 1 (General-Befund N2): echte Schreibunterbrechung GENAU
    zwischen dem atomaren 'stopped'-Commit und `_finalize_genuine_table_
    abort`, ausgeloest DURCH den realen `_cmd_menu_fortsetzen()`-Aufruf
    (Eingaben '2'/'j', nicht per direktem Mutator-Aufruf wie `test_crash_
    between_stopped_commit_and_finalize_resumes_safely`) -- derselbe Trick
    wie `general_discard_probe.py`s `after_decision_before_finalize`-Fall.
    Danach ein ECHTER, frischer OS-Kindprozess (`subprocess`, kein In-
    Process-Fake) mit normalem 'fortsetzen' (Lock noch gebunden, Window 1).

    RED ohne FIX N2/Window1: `_cmd_menu_fortsetzen` liest den Entscheid-
    Slot im Bound-Zweig nie -- der Kindprozess wuerde den noch-`active`
    Tisch klassisch resumen (`_resume_bound_table`, GM-Call) statt den
    laengst gefallenen 'stopped'-Entscheid idempotent nachzufuehren. Dieser
    Test schlaegt dann auf `gm_calls == 0` (tatsaechlich 1) und
    `table_status == 'closed'` (tatsaechlich weiterhin 'active') fehl."""
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

        def _crash(*a, **kw):
            raise _InjectedCrash("nach echtem stopped-Commit, vor Finalize")

        interrupted = False
        try:
            with patch.object(session, "_finalize_genuine_table_abort", _crash):
                session._cmd_menu_fortsetzen()
        except _InjectedCrash:
            interrupted = True
        assert interrupted, "Crash-Injektion hat nicht gegriffen -- Testaufbau defekt."

        decision = core_admission.read_table_decision(run_dir, table_id)
        assert decision is not None and decision.get("decision") == "stopped", decision
        table_mid = core_store.Table.load(run_dir, table_id)
        assert table_mid.status == "active", table_mid
        lobby_mid = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby_mid.is_locked(char_id) == table_id

        result_path = root / "n2w1-result.json"
        r2 = _run_child(root, "resume_after_crash", result_path)
        assert r2["error"] is None, r2
        assert r2["gm_calls"] == 0, r2
        assert r2["table_ids"] == [table_id], (
            "kein Doppelstart -- keine neue Tischanlage waehrend der idempotenten Nachfuehrung.", r2,
        )

        table_final = json.loads((run_dir / "tables" / f"{table_id}.json").read_text(encoding="utf-8"))
        assert table_final["status"] == "closed", table_final
        lobby_final = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby_final.is_locked(char_id) is None
        assert request_ledger.records_for_table(run_dir, table_id) == []


def test_n2_window2_stopped_decision_terminal_after_crash_after_release_before_persist():
    """N2 Window 2 (General-Befund N2): echte Schreibunterbrechung GENAU
    NACH `release_chrononaut` (Lock bereits frei) aber VOR dem `status=
    "closed"`-Persist in `_finalize_genuine_table_abort` -- Patch auf
    `core_store.Table.persist` (nur fuer GENAU diesen Tisch/Status, jeder
    andere Persist-Aufruf laeuft unveraendert durch), derselbe Trick wie
    `general_discard_probe.py`s `after_release_before_table_persist`-Fall.
    Danach ein ECHTER, frischer OS-Kindprozess mit normalem 'fortsetzen'
    (Lock bereits frei, Window 2 -> Solo-Fallback -> `_cmd_local_round([])`
    -> `create_table_from_offer_log`-Resume-Branch).

    Zusaetzlich (Produktweg-Nachweis gegen den General-Einwand, die
    bisherige Probe eroeffne nur 'eine weitere Solo-Generation' ohne den
    alten Tisch sauber ruhen zu lassen): ein DRITTER, ebenfalls frischer
    Aufruf bindet danach ERFOLGREICH eine NEUE Generation an dieselbe
    Figur -- GENAU eine neue aktive Tischanlage, der alte Tisch bleibt
    endgueltig `closed`, kein Doppelstart.

    RED ohne FIX N2/Window2: der Store-Resume-Branch gibt den noch-`active`
    Tisch unveraendert als Resume zurueck -- `_cmd_local_round([])` wuerde
    den laengst entschiedenen Tisch wiederbeleben/fortfuehren statt ihn
    terminal zu schliessen. Dieser Test schlaegt dann auf `table_ids ==
    [table_id]` (tatsaechlich weiterhin genau `[table_id]`, ABER
    `table_status` bliebe 'active' statt 'closed', s. Zwischen-Assert) und
    auf dem Folge-Resume-Check fehl."""
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
        original_persist = core_store.Table.persist

        def _crash_before_closed_persist(table):
            if table.table_id == table_id and table.status == "closed":
                raise _InjectedCrash("nach Lock-Freigabe, vor closed-Persist")
            return original_persist(table)

        interrupted = False
        try:
            with patch.object(core_store.Table, "persist", _crash_before_closed_persist):
                session._cmd_menu_fortsetzen()
        except _InjectedCrash:
            interrupted = True
        assert interrupted, "Crash-Injektion hat nicht gegriffen -- Testaufbau defekt."

        decision = core_admission.read_table_decision(run_dir, table_id)
        assert decision is not None and decision.get("decision") == "stopped", decision
        table_mid = core_store.Table.load(run_dir, table_id)
        assert table_mid.status == "active", (
            "Crash muss GENAU vor dem closed-Persist greifen -- Status auf Platte bleibt active.",
            table_mid,
        )
        lobby_mid = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby_mid.is_locked(char_id) is None, (
            "release_chrononaut laeuft VOR dem closed-Persist -- Lock muss hier bereits frei sein."
        )

        result_path = root / "n2w2-result.json"
        r2 = _run_child(root, "resume_after_crash", result_path)
        assert r2["error"] is None, r2
        assert r2["gm_calls"] == 0, r2
        assert r2["table_ids"] == [table_id], (
            "kein Doppelstart -- keine neue Generation (__2) darf fuer den laengst entschiedenen "
            "Tisch angelegt werden.", r2,
        )

        table_final = json.loads((run_dir / "tables" / f"{table_id}.json").read_text(encoding="utf-8"))
        assert table_final["status"] == "closed", table_final
        assert request_ledger.records_for_table(run_dir, table_id) == []

        # Produktweg-Nachweis: ein dritter, ebenfalls frischer Resume-
        # Versuch bindet danach erfolgreich eine NEUE Generation -- die
        # Tischanlage selbst ist (wie in `_create_unplayed_solo_table`)
        # bereits VOR jedem Eingabe-/GM-Request abgeschlossen; `_eof_input`
        # liefert fuer den tatsaechlichen ERSTEN Spielzug der neuen Runde
        # danach erwartungsgemaess 'EndOfInput' (derselbe Fall wie
        # `test_discard_then_allows_new_round_with_same_figure`s zweite
        # Session) -- das ist KEIN Fix-Defekt, nur eine erschoepfte
        # Eingabequeue fuer einen hier gar nicht beabsichtigten echten Zug.
        result_path2 = root / "n2w2-result-newgen.json"
        r3 = _run_child(root, "resume_after_crash", result_path2)
        assert r3["error"] in (None, "EndOfInput"), r3
        assert r3["gm_calls"] == 0, r3
        new_tables = [tid for tid in r3["table_ids"] if tid != table_id]
        assert len(new_tables) == 1, (
            "GENAU eine neue Generation erwartet -- kein Doppelstart des alten Tisches.", r3,
        )
        new_table_data = json.loads((run_dir / "tables" / f"{new_tables[0]}.json").read_text(encoding="utf-8"))
        assert new_table_data["status"] == "active" and new_table_data["members"] == [pid], new_table_data
        lobby_new = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby_new.is_locked(char_id) == new_tables[0]


def _write_n3_artifact(run_dir: Path, table_id: str, kind: str) -> Path:
    repair = group_repair_key(table_id, f"{table_id}-section", "CHR-OWNER1")
    if kind == "broken_plan":
        p, text = run_dir / "completion" / f"{table_id}-section__plan.json", "{broken"
    elif kind == "broken_final":
        p, text = run_dir / "completion" / f"{table_id}-section__final.json", "{broken"
    elif kind == "wrong_type_raw_archive":
        p, text = run_dir / "save_corrections_raw" / f"{repair}.json", "{}"
    else:
        p, text = run_dir / "save_corrections" / f"{repair}.json", "null"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _assert_n3_halt_not_discard_or_resume(kind: str) -> None:
    """N3 (General-Befund N3): je EIN zielgebundenes Artefakt des eigenen
    Abschnitts (`broken_plan`/`broken_final`/`wrong_type_raw_archive`/
    `null_repair_record`) existiert, ist aber unklar (Parsefehler, falscher
    Wurzeltyp, `null` statt `dict`) -- muss zu einem verstaendlichen HALT
    fuehren: KEIN Verwurf (sonst wuerde ein moeglicherweise benutzter
    Abschnitt unwiderruflich entwertet), aber auch KEIN automatisches
    Resume/Modellcall (sonst waere 'unklar' leise als 'abwesend'
    behandelt worden) -- derselbe Trick wie `general_discard_probe.py`s
    gleichnamiger Fixture-Fall.

    RED ohne FIX N3: die tolerante Default-Behandlung der bestehenden
    Reader (`_open_completion_order_for_table`/`_table_has_final` skippen
    kaputtes JSON via `continue`, `read_raw_archive` liefert `[]` fuer
    falschen Wurzeltyp, `load_record` liefert `None` fuer `null`) macht
    `_discard_unplayed_solo_eligible` HIER faelschlich `True` -- der
    Offer-Flow wuerde die Prompts '2'/'j' konsumieren und tatsaechlich
    verwerfen. Dieser Test schlaegt dann auf `table_status == 'active'`
    (tatsaechlich 'closed') und `decision is None` (tatsaechlich
    'stopped') fehl."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = _make_env(root)
        pid, char_id = "owner1", "CHR-OWNER1"
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid, char_id)
        table_id = _create_unplayed_solo_table(run_dir, states_dir, onboarding_dir, catalog_dir, pid)
        artifact_path = _write_n3_artifact(run_dir, table_id, kind)

        printed: list[str] = []
        session, gm_spy = _fresh_session(
            run_dir, states_dir, onboarding_dir, catalog_dir, pid, ["2", "j"], printed,
        )
        try:
            session._cmd_menu_fortsetzen()
        except EndOfInput:
            pass

        out = "\n".join(printed)
        assert "nicht eindeutig lesbar" in out, out
        assert "wirklich verworfen" not in out, out

        table_data = json.loads((run_dir / "tables" / f"{table_id}.json").read_text(encoding="utf-8"))
        assert table_data["status"] == "active", (table_data, artifact_path)
        assert core_admission.read_table_decision(run_dir, table_id) is None
        lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby.is_locked(char_id) == table_id
        assert gm_spy.calls == 0, "kein Modell-/Transportcall bei unklarem Zustand erwartet."


def test_n3_broken_plan_json_blocks_with_halt_not_discard_or_resume():
    _assert_n3_halt_not_discard_or_resume("broken_plan")


def test_n3_broken_final_json_blocks_with_halt_not_discard_or_resume():
    _assert_n3_halt_not_discard_or_resume("broken_final")


def test_n3_wrong_type_raw_archive_blocks_with_halt_not_discard_or_resume():
    _assert_n3_halt_not_discard_or_resume("wrong_type_raw_archive")


def test_n3_null_repair_record_blocks_with_halt_not_discard_or_resume():
    _assert_n3_halt_not_discard_or_resume("null_repair_record")


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
        ap.add_argument("--mode", required=True, choices=["setup", "discard", "resume_after_crash"])
        ap.add_argument("--root", required=True)
        ap.add_argument("--result", required=True)
        ns = ap.parse_args()
        if ns.mode == "setup":
            _child_setup(ns)
        elif ns.mode == "discard":
            _child_discard(ns)
        else:
            _child_resume_after_crash(ns)
        sys.exit(0)
    raise SystemExit(main())
