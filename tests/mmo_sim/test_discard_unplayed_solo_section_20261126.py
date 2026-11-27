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


def _create_admission_bound_unplayed_solo_table(
    run_dir, states_dir, onboarding_dir, catalog_dir, pid: str, table_key: str,
) -> str:
    """General-Nachzug r6 (ZEITRISS-ALTAIR-DISCARD-RECOVERY-20261127-r6):
    baut ueber den ECHTEN admissionsgebundenen Produktweg
    (`_cmd_table_offer([table_key])` + `_cmd_table_start([table_key])`,
    derselbe Caller wie `evidence/general_discard_r5_caller_probe.py`)
    einen unbenutzten Solo-Tisch, dessen `table_admission`-Record danach
    `state='started'` und `section_id=<table_id>` an einen noch `active`
    Tisch bindet -- diese Bindung ist UNABHAENGIG vom Chrononaut-Lock und
    bleibt auch nach dessen Freigabe bestehen (anders als `card.
    open_section_id`, s. `TuiSession._build_resume_card`-Docstring
    'core.store.locked_table_id'). Eingabequeue ist bereits VOR dem ersten
    Zug erschoepft (`/abbrechen` fuer den Start-Dialog, danach EOF)."""
    printed: list[str] = []
    session, gm_spy = _fresh_session(
        run_dir, states_dir, onboarding_dir, catalog_dir, pid, ["/abbrechen"], printed,
    )
    session._cmd_table_offer([table_key])
    try:
        session._cmd_table_start([table_key])
    except EndOfInput:
        pass
    assert gm_spy.calls == 0, "Admissionsgebundene Tischanlage allein darf keinen GM-Call ausloesen."
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

def _run_child(root: Path, mode: str, result_path: Path, *, table: str | None = None) -> dict:
    import subprocess

    cmd = [sys.executable, str(Path(__file__).resolve()), "--child", "--mode", mode,
           "--root", str(root), "--result", str(result_path)]
    if table is not None:
        cmd += ["--table", table]
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


# --------------------------------------------------------------------------
# General-Nachzug r4 (ZEITRISS-ALTAIR-DISCARD-RECOVERY-20261127-r4): zwei
# geschuetzte Haelte unter echter OS-Zweiprozess-Nachstellung -- R1
# (vorliegender echter Ledger-Request blockiert den terminalen Nachzug-
# Abschluss in `_follow_through_authorized_discard`) und R2 (der
# `closed`-Persist im Store-Resume-Zweig mutiert NIE unter fremd gehaltener
# `_SharedWriterExclusivity`). RED-Gegenprobe: `git stash` NUR auf
# `mmo_sim/ui/tui.py`/`mmo_sim/core/store.py` (die beiden r4-Fixdateien)
# laesst GENAU diese beiden Tests fehlschlagen, alle uebrigen (inkl. der
# r3-Vorgaenger) bleiben gruen -- s. worker/linus-nachzug-r4-report.md.
# --------------------------------------------------------------------------

def test_r4_r1_pending_real_ledger_request_blocks_follow_through_with_protected_halt():
    """R1 (`stopped_recovery_with_pending_real_ledger_request`, General-
    Nachzug r4 N2-R1): echte Schreibunterbrechung GENAU zwischen dem
    atomaren 'stopped'-Commit und `_finalize_genuine_table_abort` (Window
    1, Lock noch gebunden) wie `test_n2_window1_...` -- ABER danach legt
    ein ECHTER, frischer OS-Kindprozess (Mode `writer`, derselbe wie r3s
    `test_r3_cooperating_writer_...`) unter echter
    `_SharedWriterExclusivity` einen dem Tisch zugeordneten Request an
    (state `sent`). Ein danach frischer, dritter OS-Prozess (Mode
    `resume_after_crash`) darf diese vorliegende Arbeit NICHT durch einen
    blinden Nachzug-Abschluss verschlucken.

    RED ohne FIX R1 (`_follow_through_authorized_discard` prueft keine
    vorliegende Arbeit): der dritte Prozess wuerde den Tisch trotz des
    vorliegenden `sent`-Requests blind finalisieren (`status='closed'`,
    Lock freigegeben, Request bleibt verwaist unter einem bereits toten
    Tisch) -- dieser Test schlaegt dann auf `table_status=='active'`
    (tatsaechlich 'closed') und `lock==table_id` (tatsaechlich `None`)
    fehl."""
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
            raise _InjectedCrash("r4/R1: nach echtem stopped-Commit, vor Finalize")

        interrupted = False
        try:
            with patch.object(session, "_finalize_genuine_table_abort", _crash):
                session._cmd_menu_fortsetzen()
        except _InjectedCrash:
            interrupted = True
        assert interrupted, "Crash-Injektion hat nicht gegriffen -- Testaufbau defekt."

        decision_mid = core_admission.read_table_decision(run_dir, table_id)
        assert decision_mid is not None and decision_mid.get("decision") == "stopped", decision_mid
        table_mid = core_store.Table.load(run_dir, table_id)
        assert table_mid.status == "active", table_mid
        lobby_mid = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby_mid.is_locked(char_id) == table_id

        writer_result = _run_child(root, "writer", root / "r4-r1-writer.json", table=table_id)
        assert writer_result["acquired"] is True, writer_result
        assert writer_result["request_state"] == "sent", writer_result

        result_path = root / "r4-r1-resume.json"
        r2 = _run_child(root, "resume_after_crash", result_path)
        assert r2["error"] is None, r2
        assert r2["gm_calls"] == 0, r2
        assert r2["table_ids"] == [table_id], r2

        table_final = core_store.Table.load(run_dir, table_id)
        assert table_final.status == "active", (
            "ein vorliegender echter Request darf den Nachzug-Abschluss NICHT blind "
            "finalisieren.", table_final,
        )
        lobby_final = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby_final.is_locked(char_id) == table_id, (
            "Lock darf bei vorliegender Arbeit NICHT geloest werden."
        )
        decision_final = core_admission.read_table_decision(run_dir, table_id)
        assert decision_final is not None and decision_final.get("decision") == "stopped", decision_final
        records_final = request_ledger.records_for_table(run_dir, table_id)
        assert [r.get("state") for r in records_final] == ["sent"], (
            "der vorliegende Request muss unangetastet bleiben (nicht geloescht/abgerechnet).",
            records_final,
        )


def _child_hold_exclusivity(args) -> None:
    """r4-Nachzug (N2-R2): echter, frischer OS-Kindprozess, der
    `_SharedWriterExclusivity` erwirbt, seine Bereitschaft ueber stdout
    meldet und sie DANACH, bis zum ausdruecklichen `release`-Kommando ueber
    stdin, durchgehend haelt -- derselbe Trick wie `general_discard_r3_
    recovery.py`s `hold`-Kindmodus."""
    from mmo_sim.core.recovery_ops import _SharedWriterExclusivity

    root = Path(args.root)
    run_dir = root / "run"
    with _SharedWriterExclusivity(run_dir):
        print(json.dumps({"acquired": True}), flush=True)
        line = sys.stdin.readline()
        assert line == "release\n", repr(line)
    Path(args.result).write_text(json.dumps({"released": True}), encoding="utf-8")


def test_r4_r2_lockfree_window2_blocked_while_other_os_writer_holds_exclusivity():
    """R2 (`lockfree_window2_while_other_os_writer_holds_exclusivity`,
    General-Nachzug r4 N2-R2): echte Schreibunterbrechung GENAU NACH
    `release_chrononaut` (Lock bereits frei) aber VOR dem `status=
    "closed"`-Persist (Window 2), wie `test_n2_window2_...`. Ein ECHTES,
    frisches OS-Kind haelt waehrenddessen DURCHGEHEND die echte
    `_SharedWriterExclusivity` (Mode `hold`). Ein dritter, frischer
    OS-Prozess (Mode `resume_after_crash`) laeuft waehrend dieser Haltung
    bis zum Store-Resume-Zweig (`create_table_from_offer_log`) durch --
    DARF den `closed`-Persist NICHT gegen die fremd gehaltene Exklusivitaet
    ausfuehren.

    RED ohne FIX R2 (store.py:399-411 persistiert `closed` ungeschuetzt):
    der dritte Prozess wuerde `existing_table.status="closed"` + `persist()`
    OHNE Ruecksicht auf den haltenden Peer schreiben -- die Tisch-Bytes
    aendern sich WAEHREND der Peer die Exklusivitaet haelt. Dieser Test
    schlaegt dann auf `bytes_after == bytes_before` (tatsaechlich
    veraendert) und `table_status=='active'` (tatsaechlich 'closed')
    fehl."""
    import subprocess

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
                raise _InjectedCrash("r4/R2: nach Lock-Freigabe, vor closed-Persist")
            return original_persist(table)

        interrupted = False
        try:
            with patch.object(core_store.Table, "persist", _crash_before_closed_persist):
                session._cmd_menu_fortsetzen()
        except _InjectedCrash:
            interrupted = True
        assert interrupted, "Crash-Injektion hat nicht gegriffen -- Testaufbau defekt."

        decision_mid = core_admission.read_table_decision(run_dir, table_id)
        assert decision_mid is not None and decision_mid.get("decision") == "stopped", decision_mid
        table_mid = core_store.Table.load(run_dir, table_id)
        assert table_mid.status == "active", table_mid
        lobby_mid = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby_mid.is_locked(char_id) is None

        table_path = run_dir / "tables" / f"{table_id}.json"
        bytes_before = table_path.read_bytes()

        hold_result_path = root / "r4-r2-hold.json"
        cmd = [
            sys.executable, str(Path(__file__).resolve()), "--child", "--mode", "hold",
            "--root", str(root), "--result", str(hold_result_path),
        ]
        peer = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            ready = json.loads(peer.stdout.readline())
            assert ready.get("acquired") is True, ready
            assert peer.poll() is None, "Peer darf die Exklusivitaet nicht sofort wieder freigeben."

            result_path = root / "r4-r2-resume.json"
            r2 = _run_child(root, "resume_after_crash", result_path)
            peer_still_holds = peer.poll() is None
            bytes_after = table_path.read_bytes()
        finally:
            _out, stderr = peer.communicate("release\n", timeout=30)
            assert peer.returncode == 0, stderr

        hold_result = json.loads(hold_result_path.read_text(encoding="utf-8"))
        assert hold_result.get("released") is True, hold_result
        assert peer_still_holds, (
            "der Peer musste die Exklusivitaet waehrend des GESAMTEN Resumes gehalten haben "
            "-- sonst belegt dieser Test nicht den Konfliktfall."
        )
        assert bytes_after == bytes_before, (
            "Tisch-Bytes duerfen sich WAEHREND ein fremder Schreiber die Exklusivitaet haelt "
            "NIE aendern."
        )
        assert r2["error"] is None, r2
        assert r2["gm_calls"] == 0, r2
        assert r2["table_ids"] == [table_id], r2

        table_final = core_store.Table.load(run_dir, table_id)
        assert table_final.status == "active", table_final
        lobby_final = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby_final.is_locked(char_id) is None, lobby_final
        decision_final = core_admission.read_table_decision(run_dir, table_id)
        assert decision_final is not None and decision_final.get("decision") == "stopped", decision_final
        assert request_ledger.records_for_table(run_dir, table_id) == []


def test_r5_window1_bound_with_received_request_blocks_with_protected_halt():
    """r5-Nachzug (General-Nachzug r5, ZEITRISS-ALTAIR-DISCARD-RECOVERY-
    20261127-r5, Fall `bound_window1_with_received`): wie `test_r4_r1_
    pending_real_ledger_request_blocks_follow_through_with_protected_halt`,
    aber der vorliegende Requestdatensatz erreicht echten `state=received`
    (nicht `sent`). VOR dem r5-Fix pruefte `_follow_through_authorized_
    discard` nur die hartcodierte Teilmenge `state in ("reserved", "sent")`
    -- `received` fehlte komplett, obwohl `finish_received()` seinen
    durablen Checkpoint bereits im ERSTEN Write schreibt (die nachgelagerte
    Buchung kann danach abbrechen, der Datensatz bleibt ehrlich bei
    `received` haengen; die bloosse Moeglichkeit, spaeter `settle_received`
    aufzurufen, ist KEIN Beleg fuer Abschluss).

    RED ohne FIX r5 (hartcodierte Teilmenge ohne `received`): der dritte
    Prozess wuerde den Tisch trotz des vorliegenden `received`-Requests
    blind finalisieren (`status='closed'`, Lock freigegeben) -- dieser Test
    schlaegt dann auf `table_status=='active'` (tatsaechlich 'closed') und
    `lock==table_id` (tatsaechlich `None`) fehl."""
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
            raise _InjectedCrash("r5/Window1-received: nach echtem stopped-Commit, vor Finalize")

        interrupted = False
        try:
            with patch.object(session, "_finalize_genuine_table_abort", _crash):
                session._cmd_menu_fortsetzen()
        except _InjectedCrash:
            interrupted = True
        assert interrupted, "Crash-Injektion hat nicht gegriffen -- Testaufbau defekt."

        decision_mid = core_admission.read_table_decision(run_dir, table_id)
        assert decision_mid is not None and decision_mid.get("decision") == "stopped", decision_mid
        table_mid = core_store.Table.load(run_dir, table_id)
        assert table_mid.status == "active", table_mid
        lobby_mid = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby_mid.is_locked(char_id) == table_id

        writer_result = _run_child(root, "writer_received", root / "r5-w1-writer.json", table=table_id)
        assert writer_result["acquired"] is True, writer_result
        assert writer_result["request_state"] == "received", writer_result
        assert writer_result["durable_result_present"] is True, writer_result

        result_path = root / "r5-w1-resume.json"
        r2 = _run_child(root, "resume_after_crash", result_path)
        assert r2["error"] is None, r2
        assert r2["gm_calls"] == 0, r2
        assert r2["table_ids"] == [table_id], r2

        table_final = core_store.Table.load(run_dir, table_id)
        assert table_final.status == "active", (
            "ein vorliegender echter 'received'-Request darf den Nachzug-Abschluss NICHT "
            "blind finalisieren.", table_final,
        )
        lobby_final = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby_final.is_locked(char_id) == table_id, (
            "Lock darf bei vorliegender Arbeit NICHT geloest werden."
        )
        decision_final = core_admission.read_table_decision(run_dir, table_id)
        assert decision_final is not None and decision_final.get("decision") == "stopped", decision_final
        records_final = request_ledger.records_for_table(run_dir, table_id)
        assert [r.get("state") for r in records_final] == ["received"], (
            "der vorliegende Request muss unangetastet bleiben (nicht geloescht/abgerechnet).",
            records_final,
        )


def test_r5_window1_bound_with_unclear_artifact_blocks_with_protected_halt():
    """r5-Nachzug (General-Nachzug r5): wie `test_r5_window1_bound_with_
    received_request_...`, aber statt eines offenen Requests wird NACH dem
    echten 'stopped'-Commit (Crash vor Finalize, Lock noch gebunden) ein
    zielgebundenes Artefakt (hier: kaputtes `__plan.json`) angelegt -- der
    gemeinsame Helfer (`core.recovery_ops.discard_recovery_blocking_
    reason`) MUSS auch diesen Fall VOR jedem Finalize erkennen, nicht nur
    offene Requests. Vorher deckte kein Test die Kombination 'Entscheid
    bereits stopped, Resume-Fenster noch offen, Artefakt wird GENAU in
    diesem Fenster unklar' ab (die bestehenden N3/r3-Artefakttests pruefen
    nur VOR dem 'stopped'-Commit, waehrend der Bestaetigungs-Prompts)."""
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
            raise _InjectedCrash("r5/Window1-unclear: nach echtem stopped-Commit, vor Finalize")

        interrupted = False
        try:
            with patch.object(session, "_finalize_genuine_table_abort", _crash):
                session._cmd_menu_fortsetzen()
        except _InjectedCrash:
            interrupted = True
        assert interrupted, "Crash-Injektion hat nicht gegriffen -- Testaufbau defekt."

        decision_mid = core_admission.read_table_decision(run_dir, table_id)
        assert decision_mid is not None and decision_mid.get("decision") == "stopped", decision_mid

        _write_n3_artifact(run_dir, table_id, "broken_plan")

        result_path = root / "r5-w1-unclear-resume.json"
        r2 = _run_child(root, "resume_after_crash", result_path)
        assert r2["error"] is None, r2
        assert r2["gm_calls"] == 0, r2
        assert r2["table_ids"] == [table_id], r2

        table_final = core_store.Table.load(run_dir, table_id)
        assert table_final.status == "active", (
            "ein unklares zielgebundenes Artefakt darf den Nachzug-Abschluss NICHT blind "
            "finalisieren.", table_final,
        )
        lobby_final = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby_final.is_locked(char_id) == table_id, (
            "Lock darf bei unklarem Artefakt NICHT geloest werden."
        )
        decision_final = core_admission.read_table_decision(run_dir, table_id)
        assert decision_final is not None and decision_final.get("decision") == "stopped", decision_final


def _assert_r5_window2_lockfree_with_open_request_blocks_closed_persist(mode: str, expected_state: str) -> None:
    """r5-Nachzug (General-Nachzug r5): gemeinsamer Koerper fuer
    `lockfree_window2_with_sent`/`lockfree_window2_with_received` --
    dieselbe echte Crash-Injektion (Lock bereits frei, 'closed'-Persist
    noch offen) wie `test_r4_r2_lockfree_window2_blocked_while_other_os_
    writer_holds_exclusivity`, aber statt eines Peers, der die Exklusivitaet
    haelt, legt ein ECHTER, frischer OS-Kindprozess (Mode `writer`/`writer_
    received`) einen dem Tisch zugeordneten Request an. Der anschliessende
    Resume (dritter frischer OS-Prozess, `_cmd_menu_fortsetzen` ->
    kein gebundenes Lock mehr -> Solo-Fallback `_cmd_local_round([])` ->
    `core.store.create_table_from_offer_log`, Window 2) darf diesen nicht
    blind uebersehen.

    RED ohne FIX r5 (Window2 prueft GAR KEINE Open-Request-/Unklarheits-
    Lage vor dem `closed`-Persist): der dritte Prozess wuerde
    `status='closed'` persistieren und eine NEUE Generation (`__2`)
    anlegen -- dieser Test schlaegt dann auf `table_status=='active'`
    (tatsaechlich 'closed') und `table_ids==[table_id]` (tatsaechlich
    inkl. einer zweiten Generation) fehl."""
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
                raise _InjectedCrash(f"r5/Window2-{mode}: nach Lock-Freigabe, vor closed-Persist")
            return original_persist(table)

        interrupted = False
        try:
            with patch.object(core_store.Table, "persist", _crash_before_closed_persist):
                session._cmd_menu_fortsetzen()
        except _InjectedCrash:
            interrupted = True
        assert interrupted, "Crash-Injektion hat nicht gegriffen -- Testaufbau defekt."

        decision_mid = core_admission.read_table_decision(run_dir, table_id)
        assert decision_mid is not None and decision_mid.get("decision") == "stopped", decision_mid
        table_mid = core_store.Table.load(run_dir, table_id)
        assert table_mid.status == "active", table_mid
        lobby_mid = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby_mid.is_locked(char_id) is None

        writer_result = _run_child(root, mode, root / f"r5-w2-{mode}-writer.json", table=table_id)
        assert writer_result["acquired"] is True, writer_result
        assert writer_result["request_state"] == expected_state, writer_result

        result_path = root / f"r5-w2-{mode}-resume.json"
        r2 = _run_child(root, "resume_after_crash", result_path)
        assert r2["error"] is None, r2
        assert r2["gm_calls"] == 0, r2
        assert r2["table_ids"] == [table_id], r2

        table_final = core_store.Table.load(run_dir, table_id)
        assert table_final.status == "active", (
            f"ein vorliegender echter '{expected_state}'-Request darf den Store-Resume-Pfad "
            "(create_table_from_offer_log) NICHT blind 'closed' persistieren lassen.",
            table_final,
        )
        lobby_final = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby_final.is_locked(char_id) is None, (
            "Lock war in diesem Fenster bereits frei -- ein geschuetzter Halt darf ihn NICHT "
            "rekonstruieren."
        )
        decision_final = core_admission.read_table_decision(run_dir, table_id)
        assert decision_final is not None and decision_final.get("decision") == "stopped", decision_final
        records_final = request_ledger.records_for_table(run_dir, table_id)
        assert [r.get("state") for r in records_final] == [expected_state], (
            "der vorliegende Request muss unangetastet bleiben (nicht geloescht/abgerechnet).",
            records_final,
        )


def test_r5_window2_lockfree_with_sent_request_blocks_closed_persist():
    """r5-Nachzug (General-Nachzug r5, ZEITRISS-ALTAIR-DISCARD-RECOVERY-
    20261127-r5, Fall `lockfree_window2_with_sent`): s. `_assert_r5_
    window2_lockfree_with_open_request_blocks_closed_persist`-Docstring."""
    _assert_r5_window2_lockfree_with_open_request_blocks_closed_persist("writer", "sent")


def test_r5_window2_lockfree_with_received_request_blocks_closed_persist():
    """r5-Nachzug (General-Nachzug r5): wie `test_r5_window2_lockfree_
    with_sent_request_...`, aber mit einem Request, der echten
    `state=received` erreicht (s. `_child_writer_received`-Docstring fuer
    die durable-Checkpoint-vor-Buchung-Semantik)."""
    _assert_r5_window2_lockfree_with_open_request_blocks_closed_persist("writer_received", "received")


def test_r5_window2_lockfree_with_unclear_artifact_blocks_closed_persist():
    """r5-Nachzug (General-Nachzug r5): wie `test_r5_window2_lockfree_
    with_sent_request_...`, aber statt eines offenen Requests wird NACH
    dem echten Crash (Lock bereits frei, 'closed'-Persist noch offen) ein
    zielgebundenes Artefakt (kaputtes `__final.json`) angelegt --
    `create_table_from_offer_log` (Window 2, store.py) MUSS ueber denselben
    gemeinsamen Helfer auch diesen Fall erkennen, bevor es `closed`
    persistiert. Vorher gab es fuer Window 2 GAR KEINE Unklarheits-
    Bewertung -- dieser Test deckt die zuvor komplett fehlende Pruefung
    ab."""
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
                raise _InjectedCrash("r5/Window2-unclear: nach Lock-Freigabe, vor closed-Persist")
            return original_persist(table)

        interrupted = False
        try:
            with patch.object(core_store.Table, "persist", _crash_before_closed_persist):
                session._cmd_menu_fortsetzen()
        except _InjectedCrash:
            interrupted = True
        assert interrupted, "Crash-Injektion hat nicht gegriffen -- Testaufbau defekt."

        decision_mid = core_admission.read_table_decision(run_dir, table_id)
        assert decision_mid is not None and decision_mid.get("decision") == "stopped", decision_mid
        lobby_mid = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby_mid.is_locked(char_id) is None

        _write_n3_artifact(run_dir, table_id, "broken_final")

        result_path = root / "r5-w2-unclear-resume.json"
        r2 = _run_child(root, "resume_after_crash", result_path)
        assert r2["error"] is None, r2
        assert r2["gm_calls"] == 0, r2
        assert r2["table_ids"] == [table_id], r2

        table_final = core_store.Table.load(run_dir, table_id)
        assert table_final.status == "active", (
            "ein unklares zielgebundenes Artefakt darf den Store-Resume-Pfad "
            "(create_table_from_offer_log) NICHT blind 'closed' persistieren lassen.",
            table_final,
        )
        lobby_final = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby_final.is_locked(char_id) is None
        decision_final = core_admission.read_table_decision(run_dir, table_id)
        assert decision_final is not None and decision_final.get("decision") == "stopped", decision_final


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


# --------------------------------------------------------------------------
# Nachzug r3 (General-Befunde N1/N2/N3 weiterhin offen, 2026-11-27, PR
# #3321 Head 8cf64b7c weiterhin MERGE NO-GO -> Nachzug r3). Vertrag A:
# `_discard_unclear_blocking_reason` jetzt auch am Mutationsrand +
# gemeinsame `_SharedWriterExclusivity` ueber Pruefung+Commit+Finalize.
# Vertrag B: gemeinsamer `_follow_through_authorized_discard`-Helper an
# allen drei echten Wiedereinstiegen. RED-Beleg je Fall direkt im
# Docstring; zusaetzlich unabhaengig belegt ueber `general_discard_r2_
# edges.py` (7/7 PASS erst MIT diesen Fixes, s. worker/linus-nachzug-r3-
# report.md).
# --------------------------------------------------------------------------

def _child_writer(args) -> None:
    """r3-Nachzug (A-Vertrag, N1 erweitert): echter, frischer OS-
    Kindprozess, der versucht, dieselbe `_SharedWriterExclusivity` wie der
    Elternprozess zu erwerben und -- bei Erfolg -- eine echte Request-
    Reservierung vorzunehmen. Derselbe Trick wie `general_discard_r2_
    edges.py`s `writer`-Kindmodus."""
    from mmo_sim.core.recovery_ops import RecoveryExclusivityUnavailableError, _SharedWriterExclusivity

    root = Path(args.root)
    run_dir = root / "run"
    result: dict = {}
    try:
        with _SharedWriterExclusivity(run_dir):
            result["acquired"] = True
            rid = request_ledger.begin(
                run_dir, role="gm", content="r3-Nachzug kooperierender Schreiber (Writer-Fixture).",
                reserved_usd=0.0, table_id=args.table, section_id=f"{args.table}-section",
                turn_idx=0, participant="owner1", dollar_billed=False,
            )
            result["request_state"] = request_ledger.load_request(run_dir, rid)["state"]
    except RecoveryExclusivityUnavailableError:
        result["acquired"] = False
        result["request_state"] = None
    Path(args.result).write_text(json.dumps(result), encoding="utf-8")


def _child_writer_received(args) -> None:
    """r5-Nachzug (General-Nachzug r5, ZEITRISS-ALTAIR-DISCARD-RECOVERY-
    20261127-r5): wie `_child_writer`, aber der Request erreicht echten
    `state=received` (nicht `sent`) -- derselbe Trick wie
    `general_discard_r4_state_matrix.py`s `prepare_received`-Kindmodus:
    `finish_received()` schreibt seinen durablen Checkpoint (inkl.
    `result_text`) bereits im ERSTEN Write; die nachgelagerte Buchung
    (`add_seconds`) wird GENAU danach unterbrochen (injizierter `OSError`),
    der Datensatz bleibt deshalb ehrlich bei `received` haengen, nicht
    `accounted`."""
    from mmo_sim.core.recovery_ops import RecoveryExclusivityUnavailableError, _SharedWriterExclusivity

    root = Path(args.root)
    run_dir = root / "run"
    result: dict = {}
    try:
        with _SharedWriterExclusivity(run_dir):
            result["acquired"] = True
            rid = request_ledger.begin(
                run_dir, role="gm",
                content="r5-Nachzug kooperierender Schreiber (received-Fixture).",
                reserved_usd=0.0, table_id=args.table, section_id=f"{args.table}-section",
                turn_idx=0, participant="owner1", dollar_billed=False,
            )

            def _fail_accounting(*a, **kw):
                raise OSError("injected r5-fixture accounting interruption")

            interrupted = False
            try:
                with patch.object(request_ledger, "add_seconds", _fail_accounting):
                    request_ledger.finish_received(
                        run_dir, rid, usage=None, seconds=0.0,
                        result_text="Isolierte Fixture-Antwort; kein echter Provider.",
                    )
            except OSError:
                interrupted = True
            assert interrupted, "Buchungsunterbrechung hat nicht gegriffen -- Testaufbau defekt."
            record = request_ledger.load_request(run_dir, rid)
            result["request_state"] = record["state"]
            result["durable_result_present"] = isinstance(record.get("result_text"), str)
    except RecoveryExclusivityUnavailableError:
        result["acquired"] = False
        result["request_state"] = None
    Path(args.result).write_text(json.dumps(result), encoding="utf-8")


def _child_follow_through(args) -> None:
    """r3-Nachzug (B-Vertrag, N2): echter, frischer OS-Prozess ruft GENAU
    den jeweiligen echten Wiedereinstiegs-Caller nach einer zuvor im
    Elternprozess injizierten Schreibunterbrechung NACH dem echten
    'stopped'-Commit auf -- 'spielen' (Spielen->[6], `_cmd_menu_spielen`
    -> `_cmd_resume_open_section` -> `_resume_bound_table`) UND
    'local_then_fortsetzen' (oeffentliches 'l', `_cmd_local_round`, danach
    ein Folgeaufruf 'fortsetzen' im SELBEN Prozess) identisch strukturiert,
    nur der Einstiegscaller unterscheidet sich."""
    root = Path(args.root)
    run_dir, states_dir, onboarding_dir, catalog_dir = (
        root / "run", root / "states", root / "onboarding", root / "catalog",
    )
    pid, char_id = "owner1", "CHR-OWNER1"
    printed: list[str] = []
    gm_spy = _ExplodingGm()
    inputs = ["6", "Ich warte im HQ."] if args.mode == "spielen" else []
    session = TuiSession(
        onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=pid,
        input_fn=_queued_input(inputs), print_fn=printed.append,
        run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
        gm_transport_factory=lambda *a, **kw: gm_spy, host_capable=True,
    )
    row: dict = {}
    error = None
    try:
        if args.mode == "spielen":
            session._cmd_menu_spielen()
        else:
            session._cmd_local_round([], allow_operator_mode=True)
            lobby_after_local = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
            row["after_local_status"] = core_store.Table.load(run_dir, args.table).status
            row["after_local_lock"] = lobby_after_local.is_locked(char_id)
            row["after_local_table_ids"] = sorted(p.stem for p in (run_dir / "tables").glob("*.json"))
            row["after_local_gm_calls"] = gm_spy.calls
            row["after_local_request_states"] = [
                r.get("state") for r in request_ledger.records_for_table(run_dir, args.table)
            ]
            session._cmd_menu_fortsetzen()
    except (EndOfInput, Exception) as e:
        error = type(e).__name__
    lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    row.update(
        printed=printed, gm_calls=gm_spy.calls, error=error,
        table_status=core_store.Table.load(run_dir, args.table).status,
        lock=lobby.is_locked(char_id),
        request_states=[r.get("state") for r in request_ledger.records_for_table(run_dir, args.table)],
        table_ids=sorted(p.stem for p in (run_dir / "tables").glob("*.json")),
    )
    Path(args.result).write_text(json.dumps(row), encoding="utf-8")


def _child_group_writer(args) -> None:
    """r8-Nachzug (ZEITRISS-ALTAIR-DISCARD-RECOVERY-20261127-r8, Fall
    `window1_real_group_rebind_between_precheck_and_writer_acquisition`,
    derselbe Trick wie `evidence/general_discard_r7_fresh_boundary_
    probe.py`s `writer()`-Kindmodus): echter, dritter OS-Prozess, der
    unter der ORIGINALEN `_SharedWriterExclusivity` eine regulaere neue
    Zweipersonen-Gruppe anlegt (`_cmd_local_round(['owner2'])`,
    menschliche Zustimmung 'j', Pause '/abbrechen' VOR jedem Modellcall)
    und die Sicherung danach wieder freigibt -- keine Lock-/Datei-
    Handedits, derselbe Mechanismus wie der echte Produktweg."""
    from mmo_sim.core.recovery_ops import _SharedWriterExclusivity

    root = Path(args.root)
    run_dir, states_dir, onboarding_dir, catalog_dir = (
        root / "run", root / "states", root / "onboarding", root / "catalog",
    )
    printed: list[str] = []
    session, gm_spy = _fresh_session(
        run_dir, states_dir, onboarding_dir, catalog_dir, "owner1", ["j", "/abbrechen"], printed,
    )
    with _SharedWriterExclusivity(run_dir):
        try:
            session._cmd_local_round(["owner2"])
        except EndOfInput:
            pass
        new_table = core_store.Table.load(run_dir, "local-owner1-owner2")
        lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert gm_spy.calls == 0 and new_table.status == "active", new_table
        assert sorted(new_table.members) == ["owner1", "owner2"], new_table
        assert lobby.is_locked("CHR-OWNER1") == new_table.table_id
        assert lobby.is_locked("CHR-OWNER2") == new_table.table_id
    result = {"new_table_id": new_table.table_id, "gm_calls": gm_spy.calls, "printed": printed}
    Path(args.result).write_text(json.dumps(result), encoding="utf-8")


def _child_rebind_tisch_start(args) -> None:
    """r8-Nachzug (ZEITRISS-ALTAIR-DISCARD-RECOVERY-20261127-r8, Fall
    `window1_real_group_rebind_between_precheck_and_writer_acquisition`,
    derselbe wie `evidence/general_discard_r7_fresh_boundary_probe.py`s
    `child()`-Kindmodus): echter, frischer OS-Reader ruft GENAU den
    admissionsgebundenen Reconcile-Caller `_cmd_table_start([table_key])`
    auf (-> `_resume_bound_table` -> `_follow_through_authorized_
    discard`). Der fruehe Lockcheck dort (tui.py ~3404, VOR Exclusivity-
    Erwerb) sieht die Figur frei; GENAU an der echten `_SharedWriter
    Exclusivity.__enter__`-Grenze -- NACH jenem fruehen Read, VOR dem
    tatsaechlichen Erwerb -- spawnt dieser Prozess einen ECHTEN dritten
    OS-Prozess (`_child_group_writer`), der unter der ORIGINALEN
    Sicherung eine regulaere neue Gruppe anlegt und die Sicherung danach
    freigibt. Erst DANACH erwirbt dieser Reader die echte Sicherung und
    faehrt fort -- derselbe TOCTOU-Rand wie im R8-Auftrag, keine Mock der
    eigentlichen Mutation, nur der Erwerbsreihenfolge-Beweis."""
    import subprocess

    from mmo_sim.core.recovery_ops import _SharedWriterExclusivity

    root = Path(args.root)
    run_dir, states_dir, onboarding_dir, catalog_dir = (
        root / "run", root / "states", root / "onboarding", root / "catalog",
    )
    pid, char_id = "owner1", "CHR-OWNER1"
    existing_tables = sorted(p.stem for p in (run_dir / "tables").glob("*.json"))
    assert len(existing_tables) == 1, existing_tables
    table_id = existing_tables[0]
    printed: list[str] = []
    gm_spy = _ExplodingGm()
    session = TuiSession(
        onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=pid,
        input_fn=_eof_input, print_fn=printed.append,
        run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
        gm_transport_factory=lambda *a, **kw: gm_spy, host_capable=True,
    )
    gate_reads: list = []
    boundary: dict = {}
    real_read = core_store.Lobby.is_locked
    real_enter = _SharedWriterExclusivity.__enter__

    def _observe_lock(lobby, lookup_char_id):
        value = real_read(lobby, lookup_char_id)
        gate_reads.append({"char_id": lookup_char_id, "lock": value})
        return value

    def _intervene_before_acquisition(guard):
        assert not boundary, "nur die eine echte Erwerbsgrenze darf hier eingreifen."
        assert gate_reads and gate_reads[-1] == {"char_id": char_id, "lock": None}, gate_reads
        writer_result = root / "r8-group-writer-result.json"
        peer = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--child", "--mode", "group_writer",
             "--root", str(root), "--result", str(writer_result)],
            capture_output=True, text=True, timeout=30,
        )
        assert peer.returncode == 0, peer.stderr
        boundary["writer"] = json.loads(writer_result.read_text(encoding="utf-8"))
        entered = real_enter(guard)
        boundary["reader_real_exclusivity_entered_after_writer"] = True
        boundary["fresh_lock_under_exclusivity"] = real_read(
            core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy()), char_id,
        )
        return entered

    error = None
    try:
        with patch.object(core_store.Lobby, "is_locked", _observe_lock), patch.object(
            _SharedWriterExclusivity, "__enter__", _intervene_before_acquisition,
        ):
            session._cmd_table_start([args.table])
    except (EndOfInput, Exception) as e:
        error = type(e).__name__
    assert boundary.get("reader_real_exclusivity_entered_after_writer"), boundary
    lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    decision = core_admission.read_table_decision(run_dir, table_id)
    row = {
        "printed": printed, "gm_calls": gm_spy.calls, "error": error, "boundary": boundary,
        "table_status": core_store.Table.load(run_dir, table_id).status,
        "lock": lobby.is_locked(char_id),
        "decision": decision.get("decision") if decision else None,
        "request_states": [r.get("state") for r in request_ledger.records_for_table(run_dir, table_id)],
        "table_ids": sorted(p.stem for p in (run_dir / "tables").glob("*.json")),
    }
    Path(args.result).write_text(json.dumps(row), encoding="utf-8")


def _assert_r3_artifact_during_confirmation_blocks_at_mutation_edge(kind: str) -> None:
    """A-Vertrag r3 (N3 am Mutationsrand): dasselbe unklare Artefakt wie
    `_assert_n3_halt_not_discard_or_resume`, aber ERST waehrend des
    ZWEITEN Bestaetigungscallbacks angelegt (nach '2', vor 'j', per
    direktem Patch auf `session._input`) -- der ERSTE Unklar-Check in
    `_cmd_menu_fortsetzen` sieht noch gar kein Artefakt; der Fresh-Reload-
    Re-Check in `_discard_unplayed_solo_section` prueft bisher NUR
    `_discard_unplayed_solo_eligible` (die tolerant-lesenden `has_open_
    completion_plan`/`has_final_record`/`load_record`/`read_raw_archive`-
    Pfade klassifizieren ein kaputtes/falsch typisiertes Artefakt NICHT
    als 'unklar'), NICHT die strenge Unklar-Klassifikation selbst --
    derselbe Trick wie `general_discard_r2_edges.py`s `artifact_during_
    confirmation:<kind>`-Fixture.

    RED ohne FIX A (Unklar-Check am Mutationsrand): der Verwurf liefe
    durch das kaputte/falsch typisierte Artefakt unbemerkt hindurch --
    dieser Test schlaegt dann auf `table_status == 'active'` (tatsaechlich
    'closed') und `decision is None` (tatsaechlich 'stopped') fehl."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = _make_env(root)
        pid, char_id = "owner1", "CHR-OWNER1"
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid, char_id)
        table_id = _create_unplayed_solo_table(run_dir, states_dir, onboarding_dir, catalog_dir, pid)

        printed: list[str] = []
        session, gm_spy = _fresh_session(run_dir, states_dir, onboarding_dir, catalog_dir, pid, [], printed)
        calls = 0

        def _input_during_confirmation(prompt: str = "") -> str:
            nonlocal calls
            calls += 1
            if calls == 1:
                return "2"
            if calls == 2:
                _write_n3_artifact(run_dir, table_id, kind)
                return "j"
            raise EOFError()

        session._input = _input_during_confirmation
        try:
            session._cmd_menu_fortsetzen()
        except EndOfInput:
            pass

        out = "\n".join(printed)
        assert "wirklich verworfen" not in out, out

        table_data = json.loads((run_dir / "tables" / f"{table_id}.json").read_text(encoding="utf-8"))
        assert table_data["status"] == "active", table_data
        assert core_admission.read_table_decision(run_dir, table_id) is None
        lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby.is_locked(char_id) == table_id
        assert gm_spy.calls == 0
        assert request_ledger.records_for_table(run_dir, table_id) == []


def test_r3_artifact_during_confirmation_broken_plan_blocks_at_mutation_edge():
    _assert_r3_artifact_during_confirmation_blocks_at_mutation_edge("broken_plan")


def test_r3_artifact_during_confirmation_broken_final_blocks_at_mutation_edge():
    _assert_r3_artifact_during_confirmation_blocks_at_mutation_edge("broken_final")


def test_r3_artifact_during_confirmation_wrong_type_raw_archive_blocks_at_mutation_edge():
    _assert_r3_artifact_during_confirmation_blocks_at_mutation_edge("wrong_type_raw_archive")


def test_r3_artifact_during_confirmation_null_repair_record_blocks_at_mutation_edge():
    _assert_r3_artifact_during_confirmation_blocks_at_mutation_edge("null_repair_record")


def test_r3_cooperating_writer_after_last_successful_eligibility_read():
    """A-Vertrag r3 (N1 erweitert, gemeinsame Exclusivity): das Fresh-
    Reload-Eligibility-Recheck in `_discard_unplayed_solo_section` UND der
    anschliessende Commit laufen jetzt gemeinsam innerhalb EINER
    `_SharedWriterExclusivity`-Haltung (bereits erworben, BEVOR `fresh`
    geladen wird). Patcht `_discard_unplayed_solo_eligible` so, dass GENAU
    NACH dem zweiten (erfolgreichen) Aufruf -- also dem Fresh-Reload-
    Recheck INNERHALB der bereits gehaltenen Exclusivity -- ein echter,
    frischer OS-Kindprozess versucht, dieselbe Exclusivity zu erwerben und
    eine echte Request-Reservierung vorzunehmen. Derselbe Trick wie
    `general_discard_r2_edges.py`s `cooperating_writer_after_last_
    successful_read`-Fixture.

    Die deterministische Aufrufreihenfolge dieses Tests ergibt immer
    `writer_won=False` (der Elternprozess haelt die Exclusivity zu diesem
    Zeitpunkt bereits) -- RED ohne FIX A (Exclusivity): der Elternprozess
    haelt zu diesem Zeitpunkt noch KEINEN Lock, der Kindprozess erwirbt
    IMMER, der Elternprozess committet TROTZDEM weiter (kein Scope-
    Schutz) -- dieser Test schlaegt dann auf dem exklusiven Entweder-Oder
    (nie beide Seiten gleichzeitig) fehl: `request_states == []` UND
    `table_status == 'closed'` waeren verletzt, waehrend der Kindschreiber
    zusaetzlich faelschlich erfolgreich reserviert haette."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = _make_env(root)
        pid, char_id = "owner1", "CHR-OWNER1"
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid, char_id)
        table_id = _create_unplayed_solo_table(run_dir, states_dir, onboarding_dir, catalog_dir, pid)

        printed: list[str] = []
        session, gm_spy = _fresh_session(
            run_dir, states_dir, onboarding_dir, catalog_dir, pid, ["2", "j"], printed,
        )
        original_eligible = session._discard_unplayed_solo_eligible
        count = 0
        writer_result = None

        def _scheduled_eligible(table, cid):
            nonlocal count, writer_result
            answer = original_eligible(table, cid)
            count += 1
            if count == 2 and answer:
                result_path = root / "writer-result.json"
                writer_result = _run_child(root, "writer", result_path, table=table_id)
            return answer

        session._discard_unplayed_solo_eligible = _scheduled_eligible
        session._cmd_menu_fortsetzen()

        assert writer_result is not None, "Testaufbau defekt -- Scheduling-Hook wurde nie erreicht."
        writer_won = writer_result["acquired"]

        table_data = json.loads((run_dir / "tables" / f"{table_id}.json").read_text(encoding="utf-8"))
        decision = core_admission.read_table_decision(run_dir, table_id)
        lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        records = request_ledger.records_for_table(run_dir, table_id)

        if writer_won:
            assert decision is None, decision
            assert table_data["status"] == "active", table_data
            assert lobby.is_locked(char_id) == table_id
        else:
            assert records == [], records
            assert table_data["status"] == "closed", table_data
            assert lobby.is_locked(char_id) is None
        assert gm_spy.calls == 0


def test_r3_stopped_window1_resume_via_spielen_menu_is_terminal():
    """B-Vertrag r3 (N2, gemeinsamer Helper an echtem Wiedereinstieg):
    echte Schreibunterbrechung GENAU zwischen dem atomaren 'stopped'-
    Commit und `_finalize_genuine_table_abort` (Window 1, Lock noch
    gebunden), wie `test_n2_window1_stopped_decision_terminal_after_
    crash_before_finalize` -- ABER der echte, frische OS-Kindprozess kehrt
    HIER NICHT ueber 'fortsetzen' zurueck, sondern ueber 'Spielen' -> [6]
    (`_cmd_menu_spielen` -> `_cmd_resume_open_section` ->
    `_resume_bound_table`) -- derselbe echte Caller wie `general_discard_
    r2_edges.py`s `stopped_window1_via:spielen`-Fixture.

    RED ohne FIX B: `_resume_bound_table` liest den Entscheid-Slot
    nirgends -- der Kindprozess wuerde den noch-'active' Tisch klassisch
    resumen (echter GM-Call) statt den laengst gefallenen 'stopped'-
    Entscheid idempotent nachzufuehren. Dieser Test schlaegt dann auf
    `gm_calls == 0` (tatsaechlich 1) fehl."""
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
            raise _InjectedCrash("nach echtem stopped-Commit, vor Finalize (r3/spielen)")

        interrupted = False
        try:
            with patch.object(session, "_finalize_genuine_table_abort", _crash):
                session._cmd_menu_fortsetzen()
        except _InjectedCrash:
            interrupted = True
        assert interrupted, "Crash-Injektion hat nicht gegriffen -- Testaufbau defekt."

        decision = core_admission.read_table_decision(run_dir, table_id)
        assert decision is not None and decision.get("decision") == "stopped", decision

        result_path = root / "r3-spielen-result.json"
        r2 = _run_child(root, "spielen", result_path, table=table_id)
        assert r2["error"] is None, r2
        assert r2["gm_calls"] == 0, r2
        assert r2["request_states"] == [], r2
        assert r2["table_status"] == "closed", r2
        assert r2["lock"] is None, r2
        assert r2["table_ids"] == [table_id], r2


def test_r3_stopped_window1_resume_via_public_l_then_fortsetzen_is_terminal():
    """B-Vertrag r3 (N2, gemeinsamer Helper am dritten echten
    Wiedereinstieg): wie oben, aber der Kindprozess kehrt ueber das
    OEFFENTLICHE 'l' zurueck (`_cmd_local_round([], allow_operator_
    mode=True)`), danach -- im selben Prozess -- ein Folgeaufruf
    'fortsetzen'. Der ERSTE Aufruf darf AUSSCHLIESSLICH den alten Verwurf
    idempotent abschliessen (kein Ersatzstart); der anschliessende
    'fortsetzen' darf DANACH legitim eine neue Generation binden --
    derselbe echte Caller wie `general_discard_r2_edges.py`s `stopped_
    window1_via:local_then_fortsetzen`-Fixture.

    RED ohne FIX B: der neue Check in `_cmd_local_round` existiert nicht --
    `create_table_from_offer_log` wuerde den laengst entschiedenen Tisch
    entweder resumen oder einen Ersatztisch anlegen, OHNE ihn terminal
    abzuschliessen. Dieser Test schlaegt dann auf `after_local_status ==
    'closed'` (tatsaechlich weiterhin 'active') fehl."""
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
            raise _InjectedCrash("nach echtem stopped-Commit, vor Finalize (r3/local)")

        interrupted = False
        try:
            with patch.object(session, "_finalize_genuine_table_abort", _crash):
                session._cmd_menu_fortsetzen()
        except _InjectedCrash:
            interrupted = True
        assert interrupted, "Crash-Injektion hat nicht gegriffen -- Testaufbau defekt."

        decision = core_admission.read_table_decision(run_dir, table_id)
        assert decision is not None and decision.get("decision") == "stopped", decision

        result_path = root / "r3-local-result.json"
        r2 = _run_child(root, "local_then_fortsetzen", result_path, table=table_id)

        assert r2.get("after_local_status") == "closed", r2
        assert r2.get("after_local_lock") is None, r2
        assert r2.get("after_local_table_ids") == [table_id], r2
        assert r2.get("after_local_gm_calls") == 0, r2
        assert r2.get("after_local_request_states") == [], r2

        assert r2["error"] in (None, "EndOfInput"), r2
        assert r2["lock"] != table_id, r2
        assert len(r2["table_ids"]) <= 2, r2


# --------------------------------------------------------------------------
# General-Nachzug r6 (ZEITRISS-ALTAIR-DISCARD-RECOVERY-20261127-r6): der
# Lock-Teil von `_discard_candidate_identity_match` war bisher ein Exact-
# Match (`lobby.is_locked(chrononaut_id) == table.table_id`) und diente
# damit GLEICHZEITIG als Identitaets-Scope UND als vollstaendige Recovery-
# Anwendbarkeit. `_cmd_menu_fortsetzen`/`_cmd_menu_spielen`/oeffentliches
# 'l' loesen ihren Resume-Kandidaten alle ueber `core.store.locked_
# table_id` auf (s. `_build_resume_card`-Docstring) -- bei bereits freiem
# Lock faellt dort NIE `_follow_through_authorized_discard` mit freiem
# Lock an, sondern bereits VORHER der (laengst gehaertete) Window2-Store-
# Pfad. `_cmd_table_start`s Reconcile-Zweig (tui.py:7901-7958) laedt den
# gebundenen Tisch dagegen ueber den Admission-Record-`section_id` --
# VOELLIG UNABHAENGIG vom Lock -- und ruft `_resume_bound_table` darauf
# direkt auf. GENAU dieser Caller war die verbleibende Luecke (s.
# `evidence/general_discard_r5_caller_probe.py`, am Head 1edeca6b
# `contract_pass=false`/`fake_gm_calls=1`).
# --------------------------------------------------------------------------

def _child_tisch_start(args) -> None:
    """r6-Nachzug: echter, frischer OS-Prozess ruft GENAU den admissions-
    gebundenen Caller `_cmd_table_start([table_key])` auf -- der einzige
    bestehende Resume-Einstieg, der den gebundenen Abschnitt NICHT ueber
    den Chrononaut-Lock (`core.store.locked_table_id`), sondern ueber den
    `table_admission`-Record-`section_id` findet (tui.py:7901-7907)."""
    root = Path(args.root)
    run_dir, states_dir, onboarding_dir, catalog_dir = (
        root / "run", root / "states", root / "onboarding", root / "catalog",
    )
    pid, char_id = "owner1", "CHR-OWNER1"
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
        session._cmd_table_start([args.table])
    except (EndOfInput, Exception) as e:
        error = type(e).__name__
    lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    row = {
        "printed": printed, "gm_calls": gm_spy.calls, "error": error,
        "lock": lobby.is_locked(char_id),
        "table_ids": sorted(p.stem for p in (run_dir / "tables").glob("*.json")),
    }
    Path(args.result).write_text(json.dumps(row), encoding="utf-8")


def test_r6_lockfree_resume_via_tisch_start_is_terminal():
    """r6-Nachzug (Fall `lockfree_window2_via_real_tisch_start`, derselbe
    wie `general_discard_r5_caller_probe.py`): echte Schreibunterbrechung
    GENAU NACH `release_chrononaut` (Lock bereits frei) aber VOR dem
    `status="closed"`-Persist -- wie `test_n2_window2_stopped_decision_
    terminal_after_crash_after_release_before_persist` -- ABER der Tisch
    ist hier ueber den ECHTEN admissionsgebundenen Weg angelegt
    (`_cmd_table_offer`/`_cmd_table_start`) und der frische OS-Kindprozess
    kehrt HIER ueber `tisch-start` (`_cmd_table_start`) zurueck, NICHT
    ueber 'fortsetzen'/'Spielen'/'l'.

    RED ohne r6-Fix: `_discard_candidate_identity_match`s Exact-Lock-
    Filter liefert bei freiem Lock `False` -> `_follow_through_authorized_
    discard` faellt durch -> `_resume_bound_table` resumt den laengst
    'stopped' entschiedenen Abschnitt klassisch -- dieser Test schlaegt
    dann auf `r2["gm_calls"] == 0` (tatsaechlich 1) fehl."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = _make_env(root)
        pid, char_id = "owner1", "CHR-OWNER1"
        table_key = "fixture-discard-admission"
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid, char_id)
        table_id = _create_admission_bound_unplayed_solo_table(
            run_dir, states_dir, onboarding_dir, catalog_dir, pid, table_key,
        )

        printed: list[str] = []
        session, _spy = _fresh_session(
            run_dir, states_dir, onboarding_dir, catalog_dir, pid, ["2", "j"], printed,
        )
        original_persist = core_store.Table.persist

        def _crash_before_closed_persist(table):
            if table.table_id == table_id and table.status == "closed":
                raise _InjectedCrash("nach Lock-Freigabe, vor closed-Persist (r6/tisch-start)")
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
        assert table_mid.status == "active", table_mid
        lobby_mid = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby_mid.is_locked(char_id) is None, (
            "release_chrononaut laeuft VOR dem closed-Persist -- Lock muss hier bereits frei sein."
        )

        result_path = root / "r6-tisch-start-result.json"
        r2 = _run_child(root, "tisch_start", result_path, table=table_key)
        assert r2["error"] is None, r2
        assert r2["gm_calls"] == 0, r2
        assert r2["table_ids"] == [table_id], (
            "kein Doppelstart/Fake-GM -- der laengst 'stopped' entschiedene Abschnitt wird nur "
            "idempotent nachgefuehrt, kein Ersatzstart.", r2,
        )
        assert r2["lock"] is None, r2

        table_final = json.loads((run_dir / "tables" / f"{table_id}.json").read_text(encoding="utf-8"))
        assert table_final["status"] == "closed", table_final
        assert request_ledger.records_for_table(run_dir, table_id) == []


def _assert_follow_through_discard_lock_state(lock_state: str, *, expect_finalized: bool) -> None:
    """r6-Nachzug, r7-Nachzug (ZEITRISS-ALTAIR-DISCARD-RECOVERY-20261127-r7,
    Fall `stopped_solo_tisch_start_after_real_group_rebind`): direkter
    Vertragsnachweis fuer die jetzt getrennten Bausteine `_discard_
    candidate_hard_identity_match` (reine Identitaet) und die Lock-
    ANWENDBARKEIT, aufgerufen ueber den gemeinsamen Helfer `_follow_
    through_authorized_discard` -- DENSELBEN Helfer, den alle drei echten
    Resume-Caller (zentrales Fortsetzen tui.py:3028, `_resume_bound_table`
    tui.py:3614, oeffentliches 'l' tui.py:9841) teilen. Baut einen eigenen,
    bereits 'stopped' entschiedenen, noch `active` Solo-Tisch (echte
    Schreibunterbrechung VOR Finalize, Lock noch exakt gebunden -- wie
    `test_n2_window1_...`), versetzt den Lock danach GEZIELT ueber die
    ECHTEN `Lobby`-APIs (`release_chrononaut`/`lock_chrononaut`, keine
    rohen Datei-Handedits) in den angeforderten Zustand und ruft den
    Helfer direkt auf:
    - `'exact'`: Lock unveraendert == table_id -- Fall 2, finalisiert.
    - `'free'`: Lock legitim frei (r6-Fix) -- Fall 2, finalisiert.
    - `'foreign'`: Lock zeigt echt auf eine ANDERE table_id (z.B. eine
      inzwischen regulaer neu begonnene Bindung desselben Chrononauten) --
      Fall 3 (r7-Fix): `_follow_through_authorized_discard` gibt JETZT
      `True` zurueck (geschuetzter Halt, der Aufrufer darf nicht weiter
      resumen), ABER finalisiert NICHT -- der alte Tisch bleibt `active`,
      der `stopped`-Entscheid steht, die fremde/neuere Bindung bleibt
      unangetastet. `expect_finalized` unterscheidet deshalb von der
      reinen Rueckgabe: Fall 2 UND Fall 3 liefern beide `True`, nur Fall 2
      finalisiert wirklich.

    RED ohne r6-Fix: `'free'` schlaegt auf `result is True` fehl
    (tatsaechlich `False`). RED ohne r7-Fix: `'foreign'` schlaegt auf
    `result is True` fehl (tatsaechlich `False` -- genau das nackte False,
    das Fall 3 faelschlich wie Fall 1 behandelt und in den normalen Resume
    durchfallen liesse, s. GENERAL-REVIEW)."""
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
            raise _InjectedCrash("nach echtem stopped-Commit, vor Finalize (r6 lock-state matrix)")

        interrupted = False
        try:
            with patch.object(session, "_finalize_genuine_table_abort", _crash):
                session._cmd_menu_fortsetzen()
        except _InjectedCrash:
            interrupted = True
        assert interrupted, "Crash-Injektion hat nicht gegriffen -- Testaufbau defekt."

        decision = core_admission.read_table_decision(run_dir, table_id)
        assert decision is not None and decision.get("decision") == "stopped", decision
        table = core_store.Table.load(run_dir, table_id)
        assert table.status == "active", table
        lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby.is_locked(char_id) == table_id, "Lock muss hier noch exakt gebunden sein (Window1)."

        foreign_table_id = f"{table_id}__foreign-owner"
        if lock_state == "free":
            lobby.release_chrononaut(char_id, table_id)
            assert lobby.is_locked(char_id) is None
        elif lock_state == "foreign":
            lobby.release_chrononaut(char_id, table_id)
            lobby.lock_chrononaut(char_id, foreign_table_id)
            assert lobby.is_locked(char_id) == foreign_table_id
        elif lock_state != "exact":
            raise AssertionError(lock_state)

        printed.clear()
        result = session._follow_through_authorized_discard(table, char_id)
        expect_applicable = expect_finalized or lock_state == "foreign"
        assert result is expect_applicable, (lock_state, result)

        final_table = core_store.Table.load(run_dir, table_id)
        final_lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        if expect_finalized:
            assert final_table.status == "closed", final_table
            assert final_lobby.is_locked(char_id) is None
        else:
            assert final_table.status == "active", (
                "nicht-finalisierter Fall darf den eigenen Tisch NICHT finalisieren.", final_table,
            )
            if lock_state == "foreign":
                assert final_lobby.is_locked(char_id) == foreign_table_id, (
                    "fremde/neuere Bindung darf durch den eigenen Nachzug NICHT aufgeweicht werden."
                )
                decision_after = core_admission.read_table_decision(run_dir, table_id)
                assert decision_after is not None and decision_after.get("decision") == "stopped", (
                    "der stopped-Entscheid darf durch den geschuetzten Halt NICHT zurueckgedreht werden.",
                    decision_after,
                )
                assert printed, "Fall 3 muss eine verstaendliche Bindungsdiagnose ausgeben."
                message = printed[-1]
                assert "andere" in message and "Bindung" in message, message
                for forbidden in ("Recht", "recht", "Retry", "retry", "Storage", "storage", "wiederhol"):
                    assert forbidden not in message, (forbidden, message)


def test_r6_follow_through_discard_still_applies_with_exact_lock_unchanged_behavior():
    _assert_follow_through_discard_lock_state("exact", expect_finalized=True)


def test_r6_follow_through_discard_now_applies_with_legit_free_lock():
    _assert_follow_through_discard_lock_state("free", expect_finalized=True)


def test_r7_follow_through_discard_halts_protected_on_foreign_lock_without_finalize():
    """r7-Nachzug (ersetzt die fruehere r6-Annahme, ein nacktes `False`
    sei bei einer fremden/neueren Bindung bereits vollstaendiger Schutz --
    s. `_assert_follow_through_discard_lock_state`-Docstring und
    GENERAL-REVIEW Zeile 78-80: ein `False` allein ist KEIN Nachweis eines
    terminalen Halts, weil der Aufrufer dann in den normalen Resume
    faellt)."""
    _assert_follow_through_discard_lock_state("foreign", expect_finalized=False)


def test_r7_resume_bound_table_halts_on_real_group_rebind_without_new_request():
    """r7-Nachzug (ZEITRISS-ALTAIR-DISCARD-RECOVERY-20261127-r7, Fall
    `stopped_solo_tisch_start_after_real_group_rebind`, derselbe wie
    `evidence/general_discard_r6_rebind_probe.py`): anders als die
    Lock-State-Matrix oben (die den gemeinsamen Helfer `_follow_through_
    authorized_discard` direkt aufruft) geht dieser Test ueber einen der
    drei tatsaechlichen produktiven Resume-Caller selbst
    (`_resume_bound_table`, tui.py:3643) -- ein gruener Test auf den
    Helfer-Rueckgabewert allein ist KEIN Nachweis des terminalen Halts am
    echten Aufrufer (GENERAL-REVIEW Zeile 78-80).

    Aufbau: echter eigener unbenutzter Solo-Tisch, echte Schreib-
    unterbrechung GENAU NACH `release_chrononaut` (Lock frei) ABER VOR dem
    `status='closed'`-Persist (identisch zu `test_r6_lockfree_resume_via_
    tisch_start_is_terminal`), decision bereits durabel 'stopped'. Danach
    NICHT der alte Tisch, sondern ein ECHTER neuer Zweipersonen-Tisch
    ueber `_cmd_local_round(['owner2'])` mit menschlicher Zustimmung
    ('j') und Pause VOR jedem Modellcall ('/abbrechen') -- keine Lock-
    Handedits, derselbe Mechanismus wie im R7-Briefing Schritt 2. Die
    Figur `CHR-OWNER1` ist danach real an den NEUEN Gruppentisch gebunden
    (Fall 3), der alte Solo-Tisch bleibt im Crash-Zustand.

    Ein frischer `TuiSession` (simuliert den frischen OS-Prozess aus dem
    Briefing) ruft DANACH direkt `_resume_bound_table(alter_tisch)` auf --
    derselbe Einstieg, den die Admission-`tisch-start`-Reconcile
    (`_cmd_table_start`) tatsaechlich erreicht. Erwartet: 0 GM-/Transport-
    Calls, 0 neue Requestdatensaetze fuer den alten Tisch, alter Tisch
    bleibt `active` (NICHT finalisiert), alter `stopped`-Entscheid
    unveraendert, NEUE Bindung/NEUER Tisch bleiben unangetastet, eine
    verstaendliche Bindungsdiagnose ohne Rechte-/Retry-/Storage-Sprache.

    RED ohne r7-Fix: `_resume_bound_table` resumt den alten Abschnitt
    klassisch -- dieser Test schlaegt dann auf `resume_gm.calls == 0`
    fehl (tatsaechlich 1)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = _make_env(root)
        pid, char_id = "owner1", "CHR-OWNER1"
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid, char_id)
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, "owner2", "CHR-OWNER2")
        table_id = _create_unplayed_solo_table(run_dir, states_dir, onboarding_dir, catalog_dir, pid)

        printed: list[str] = []
        session, _spy = _fresh_session(
            run_dir, states_dir, onboarding_dir, catalog_dir, pid, ["2", "j"], printed,
        )
        original_persist = core_store.Table.persist

        def _crash_before_closed_persist(table):
            if table.table_id == table_id and table.status == "closed":
                raise _InjectedCrash("r7: nach Lock-Freigabe, vor closed-Persist (rebind)")
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
        assert core_store.Table.load(run_dir, table_id).status == "active"
        lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby.is_locked(char_id) is None, (
            "release_chrononaut laeuft VOR dem closed-Persist -- Lock muss hier bereits frei sein."
        )

        # Echter neuer Gruppentisch ueber den tatsaechlichen UI-Befehl, mit
        # menschlicher Zustimmung, Pause vor jedem Modellcall ueber
        # '/abbrechen' -- keine Lock-/Datei-Handedits.
        group_printed: list[str] = []
        group_session, group_gm = _fresh_session(
            run_dir, states_dir, onboarding_dir, catalog_dir, pid, ["j", "/abbrechen"], group_printed,
        )
        try:
            group_session._cmd_local_round(["owner2"])
        except EndOfInput:
            pass
        assert group_gm.calls == 0, "Gruppenaufbau allein darf keinen GM-Call ausloesen."
        new_table_id = f"local-{pid}-owner2"
        new_table = core_store.Table.load(run_dir, new_table_id)
        assert new_table.status == "active" and sorted(new_table.members) == [pid, "owner2"], new_table
        lobby_after_rebind = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby_after_rebind.is_locked(char_id) == new_table_id, (
            "Figur muss nach dem echten Gruppenaufbau real an die neue Gruppe gebunden sein."
        )
        rebound_decision = core_admission.read_table_decision(run_dir, table_id)
        assert rebound_decision is not None and rebound_decision.get("decision") == "stopped"
        assert core_store.Table.load(run_dir, table_id).status == "active"

        request_before = request_ledger.records_for_table(run_dir, table_id)
        new_table_bytes_before = (run_dir / "tables" / f"{new_table_id}.json").read_bytes()
        locks_before = (run_dir / "locks.json").read_bytes()

        # Frischer OS-Prozess (hier: frische Session) erreicht den echten
        # produktiven Resume-Einstieg direkt mit dem ALTEN Tisch.
        resume_printed: list[str] = []
        resume_session, resume_gm = _fresh_session(
            run_dir, states_dir, onboarding_dir, catalog_dir, pid, [], resume_printed,
        )
        stale_table = core_store.Table.load(run_dir, table_id)
        resume_session._resume_bound_table(stale_table)

        assert resume_gm.calls == 0, "Fall 3 darf NIE einen GM-/Modellcall ausloesen."
        assert request_ledger.records_for_table(run_dir, table_id) == request_before, (
            "Fall 3 darf keine neue Anfrage fuer den alten Abschnitt anlegen."
        )
        final_old_table = core_store.Table.load(run_dir, table_id)
        assert final_old_table.status == "active", (
            "Fall 3: der alte stopped-Abschnitt darf NICHT finalisiert werden.", final_old_table,
        )
        final_decision = core_admission.read_table_decision(run_dir, table_id)
        assert final_decision is not None and final_decision.get("decision") == "stopped", (
            "der alte stopped-Entscheid darf NICHT zurueckgedreht werden.", final_decision,
        )
        final_lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert final_lobby.is_locked(char_id) == new_table_id, (
            "die neue reale Bindung darf durch den alten Abschnitt NICHT aufgeweicht werden."
        )
        assert (run_dir / "tables" / f"{new_table_id}.json").read_bytes() == new_table_bytes_before, (
            "die neue Gruppe/ihr Tischstand darf unangetastet bleiben."
        )
        assert (run_dir / "locks.json").read_bytes() == locks_before, (
            "bestehende Locks (inkl. neuer Gruppenbindung) duerfen unangetastet bleiben."
        )
        assert resume_printed, "es muss eine verstaendliche Bindungsdiagnose ausgegeben werden."
        message = resume_printed[-1]
        assert "andere" in message and "Bindung" in message, message
        for forbidden in ("Recht", "recht", "Retry", "retry", "Storage", "storage", "wiederhol"):
            assert forbidden not in message, (forbidden, message)


def test_r7_window2_create_table_from_offer_log_halts_on_real_group_rebind_without_finalize():
    """r7-Nachzug (ZEITRISS-ALTAIR-DISCARD-RECOVERY-20261127-r7, Befund E
    des unabhaengigen Critics): anders als `test_r7_resume_bound_table_
    halts_on_real_group_rebind_without_new_request` oben (das den
    Window-1-Caller `_resume_bound_table` isoliert) prueft dieser Test
    `store.py::create_table_from_offer_log`s eigenen Window-2-Reuse-Zweig
    ueber dessen tatsaechlichen oeffentlichen Caller: das frei getippte
    'l' (`_cmd_local_round([], allow_operator_mode=True)`). Dessen frueher
    Live-Lock-Check (tui.py:9916-9930) loest NACH einem echten Rebind
    bereits auf den NEUEN Tisch auf -- `_follow_through_authorized_
    discard` sieht fuer den neuen Tisch keinen 'stopped'-Entscheid und
    schuetzt den alten Solo NICHT -- der Aufruf faellt bis zu
    `create_table_from_offer_log(lobby, f"local-{pid}", ...)` durch,
    demselben `table_id` wie der alte Solo-Alias.

    Aufbau identisch zum Test oben: echter eigener unbenutzter Solo-
    Tisch, echte Schreibunterbrechung GENAU NACH `release_chrononaut`
    (Lock frei), ABER VOR dem `status='closed'`-Persist, decision bereits
    durabel 'stopped'. Danach ein ECHTER neuer Zweipersonen-Tisch ueber
    `_cmd_local_round(['owner2'])` (keine Lock-/Datei-Handedits) -- die
    Figur ist danach real an den neuen Gruppentisch gebunden (Fall 3).

    Erwartet: 0 GM-/Transport-Calls, 0 neue Requestdatensaetze fuer den
    alten Tisch, alter Tisch bleibt `active` (NICHT finalisiert), alter
    `stopped`-Entscheid unveraendert, neue Bindung/neuer Tisch/Locks
    bleiben byteidentisch, KEINE faelschliche 'Bindung frei'-Meldung.

    RED ohne diesen Fix: Window 2 prueft nur `decision=='stopped'` +
    `discard_recovery_blocking_reason` (keine Lock-Divergenz-Pruefung) --
    `fresh_existing.status='closed'; fresh_existing.persist()` finalisiert
    den alten Tisch UNBEFUGT und druckt „... wurde dauerhaft verworfen
    (Discard) -- Bindung frei ...", OBWOHL die Figur real an den neuen
    Tisch gebunden ist. Dieser Test schlaegt dann auf
    `final_old_table.status == 'active'` (tatsaechlich 'closed') fehl."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = _make_env(root)
        pid, char_id = "owner1", "CHR-OWNER1"
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid, char_id)
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, "owner2", "CHR-OWNER2")
        table_id = _create_unplayed_solo_table(run_dir, states_dir, onboarding_dir, catalog_dir, pid)

        printed: list[str] = []
        session, _spy = _fresh_session(
            run_dir, states_dir, onboarding_dir, catalog_dir, pid, ["2", "j"], printed,
        )
        original_persist = core_store.Table.persist

        def _crash_before_closed_persist(table):
            if table.table_id == table_id and table.status == "closed":
                raise _InjectedCrash("r7/window2: nach Lock-Freigabe, vor closed-Persist (rebind)")
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
        assert core_store.Table.load(run_dir, table_id).status == "active"
        lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby.is_locked(char_id) is None, (
            "release_chrononaut laeuft VOR dem closed-Persist -- Lock muss hier bereits frei sein."
        )

        # Echter neuer Gruppentisch ueber den tatsaechlichen UI-Befehl, mit
        # menschlicher Zustimmung, Pause vor jedem Modellcall ueber
        # '/abbrechen' -- keine Lock-/Datei-Handedits.
        group_printed: list[str] = []
        group_session, group_gm = _fresh_session(
            run_dir, states_dir, onboarding_dir, catalog_dir, pid, ["j", "/abbrechen"], group_printed,
        )
        try:
            group_session._cmd_local_round(["owner2"])
        except EndOfInput:
            pass
        assert group_gm.calls == 0, "Gruppenaufbau allein darf keinen GM-Call ausloesen."
        new_table_id = f"local-{pid}-owner2"
        new_table = core_store.Table.load(run_dir, new_table_id)
        assert new_table.status == "active" and sorted(new_table.members) == [pid, "owner2"], new_table
        lobby_after_rebind = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby_after_rebind.is_locked(char_id) == new_table_id, (
            "Figur muss nach dem echten Gruppenaufbau real an die neue Gruppe gebunden sein."
        )
        rebound_decision = core_admission.read_table_decision(run_dir, table_id)
        assert rebound_decision is not None and rebound_decision.get("decision") == "stopped"
        assert core_store.Table.load(run_dir, table_id).status == "active"

        request_before = request_ledger.records_for_table(run_dir, table_id)
        new_table_bytes_before = (run_dir / "tables" / f"{new_table_id}.json").read_bytes()
        locks_before = (run_dir / "locks.json").read_bytes()

        # Frischer OS-Prozess (hier: frische Session) erreicht den echten
        # OEFFENTLICHEN 'l'-Dispatch direkt -- fuer den unveraenderten
        # Solo-Alias-Weg (keine guest_tokens) landet das bei
        # `create_table_from_offer_log(lobby, f"local-{pid}", ...)`,
        # demselben `table_id` wie der alte Solo-Tisch.
        resume_printed: list[str] = []
        resume_session, resume_gm = _fresh_session(
            run_dir, states_dir, onboarding_dir, catalog_dir, pid, [], resume_printed,
        )
        try:
            resume_session._cmd_local_round([], allow_operator_mode=True)
        except EndOfInput:
            pass

        assert resume_gm.calls == 0, "Fall 3 (Window 2) darf NIE einen GM-/Modellcall ausloesen."
        assert request_ledger.records_for_table(run_dir, table_id) == request_before, (
            "Fall 3 (Window 2) darf keine neue Anfrage fuer den alten Abschnitt anlegen."
        )
        final_old_table = core_store.Table.load(run_dir, table_id)
        assert final_old_table.status == "active", (
            "Fall 3 (Window 2): der alte stopped-Abschnitt darf NICHT finalisiert werden.", final_old_table,
        )
        final_decision = core_admission.read_table_decision(run_dir, table_id)
        assert final_decision is not None and final_decision.get("decision") == "stopped", (
            "der alte stopped-Entscheid darf NICHT zurueckgedreht werden.", final_decision,
        )
        final_lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert final_lobby.is_locked(char_id) == new_table_id, (
            "die neue reale Bindung darf durch den alten Abschnitt (Window 2) NICHT aufgeweicht werden."
        )
        assert (run_dir / "tables" / f"{new_table_id}.json").read_bytes() == new_table_bytes_before, (
            "die neue Gruppe/ihr Tischstand darf unangetastet bleiben (Window 2)."
        )
        assert (run_dir / "locks.json").read_bytes() == locks_before, (
            "bestehende Locks (inkl. neuer Gruppenbindung) duerfen unangetastet bleiben (Window 2)."
        )
        for emitted in resume_printed:
            assert "Bindung frei" not in emitted, (
                "keine faelschliche 'Bindung frei'-Meldung -- die Figur ist real an die neue "
                "Gruppe gebunden.", emitted,
            )


def test_r8_window1_tisch_start_halts_protected_on_real_group_rebind_at_writer_acquisition_boundary():
    """r8-Nachzug (ZEITRISS-ALTAIR-DISCARD-RECOVERY-20261127-r8, Fall
    `window1_real_group_rebind_between_precheck_and_writer_acquisition`,
    derselbe wie `evidence/general_discard_r7_fresh_boundary_probe.py`):
    anders als `test_r7_resume_bound_table_halts_on_real_group_rebind_
    without_new_request` (dort ist die neue Bindung bereits VOR dem
    Aufruf vollstaendig abgeschlossen -- der fruehe Lockcheck in tui.py
    ~3404 sieht die fremde Bindung schon VOR Exclusivity-Erwerb und haelt
    dort bereits sicher an, UNABHAENGIG vom r8-Fix) prueft dieser Test
    GENAU die Erwerbsgrenze selbst: ein ECHTER zweiter OS-Prozess bindet
    die Figur regulaer an eine neue Gruppe GENAU zwischen jenem fruehen
    Read (sieht noch `None`) und dem tatsaechlichen Erwerb der
    ORIGINALEN `_SharedWriterExclusivity` durch den wartenden Leser --
    derselbe TOCTOU-Rand, den `general_discard_r7_fresh_boundary_
    probe.py` belegt.

    Aufbau wie `test_r6_lockfree_resume_via_tisch_start_is_terminal`:
    echter admissionsgebundener Solo-Tisch (`_cmd_table_offer`+`_cmd_
    table_start`), echte Schreibunterbrechung GENAU NACH `release_
    chrononaut` (Lock frei), ABER VOR dem `status='closed'`-Persist --
    decision bereits durabel 'stopped'. Der frische Leser-OS-Prozess ruft
    danach GENAU den echten admissionsgebundenen Reconcile-Caller
    `_cmd_table_start([table_key])` auf; GENAU an der echten `_Shared
    WriterExclusivity.__enter__`-Grenze spawnt er einen ECHTEN dritten
    OS-Prozess, der unter der ORIGINALEN Sicherung eine regulaere neue
    Zweipersonen-Gruppe anlegt (`_cmd_local_round(['owner2'])`, Konsens
    'j', Pause '/abbrechen' vor jedem Modellcall) und die Sicherung
    danach freigibt -- erst DANACH erwirbt der Leser die echte Sicherung.

    RED ohne r8-Fix: der fruehe Lockcheck (vor Exclusivity-Erwerb) sah
    den Lock noch frei (`None`) und ist die einzige Lockpruefung im
    gesamten Pfad -- innerhalb der Exclusivity wird der Lock NIE erneut
    gelesen. `_finalize_genuine_table_abort` schliesst den alten Tisch
    (`closed`), obwohl die Figur inzwischen real an `local-owner1-
    owner2` gebunden ist -- dieser Test schlaegt dann auf
    `r2['table_status'] == 'active'` fehl (tatsaechlich `'closed'`)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = _make_env(root)
        pid, char_id = "owner1", "CHR-OWNER1"
        table_key = "fixture-discard-admission"
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, pid, char_id)
        _register_owner(run_dir, states_dir, onboarding_dir, catalog_dir, "owner2", "CHR-OWNER2")
        table_id = _create_admission_bound_unplayed_solo_table(
            run_dir, states_dir, onboarding_dir, catalog_dir, pid, table_key,
        )

        printed: list[str] = []
        session, _spy = _fresh_session(
            run_dir, states_dir, onboarding_dir, catalog_dir, pid, ["2", "j"], printed,
        )
        original_persist = core_store.Table.persist

        def _crash_before_closed_persist(table):
            if table.table_id == table_id and table.status == "closed":
                raise _InjectedCrash("r8: nach Lock-Freigabe, vor closed-Persist (tisch-start-Grenze)")
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
        assert table_mid.status == "active", table_mid
        lobby_mid = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby_mid.is_locked(char_id) is None, (
            "release_chrononaut laeuft VOR dem closed-Persist -- Lock muss hier bereits frei sein."
        )
        request_before = [r.get("state") for r in request_ledger.records_for_table(run_dir, table_id)]

        result_path = root / "r8-rebind-tisch-start-result.json"
        r2 = _run_child(root, "rebind_tisch_start", result_path, table=table_key)
        assert r2["error"] is None, r2
        assert r2["gm_calls"] == 0, "Fall 3 darf NIE einen GM-/Modellcall ausloesen."
        boundary = r2["boundary"]
        assert boundary["reader_real_exclusivity_entered_after_writer"], boundary
        new_table_id = boundary["writer"]["new_table_id"]
        assert new_table_id == "local-owner1-owner2", boundary
        assert boundary["fresh_lock_under_exclusivity"] == new_table_id, (
            "die echte Sicherung sah die neue Bindung bereits beim Erwerb -- der Fix muss sie "
            "ERNEUT lesen, nicht den fruehen (jetzt veralteten) Read von davor weiterverwenden.",
            boundary,
        )

        assert r2["table_status"] == "active", (
            "r8-Fix: der alte stopped-Abschnitt darf bei einer echten Rebind-Grenze zwischen "
            "Vorabcheck und Exclusivity-Erwerb NICHT finalisiert werden.", r2,
        )
        assert r2["decision"] == "stopped", (
            "der alte stopped-Entscheid darf NICHT zurueckgedreht werden.", r2,
        )
        assert r2["lock"] == new_table_id, (
            "die neue reale Bindung darf durch den alten Abschnitt NICHT aufgeweicht werden.", r2,
        )
        assert r2["request_states"] == request_before, (
            "Fall 3 darf keine neue Anfrage fuer den alten Abschnitt anlegen.", r2,
        )
        assert r2["table_ids"] == sorted([table_id, new_table_id]), (
            "kein Doppelstart -- genau der alte und der neue Tisch existieren.", r2,
        )
        assert r2["printed"], "es muss eine verstaendliche Bindungsdiagnose ausgegeben werden."
        message = r2["printed"][-1]
        assert "andere" in message and "Bindung" in message, message
        for forbidden in ("Recht", "recht", "Retry", "retry", "Storage", "storage", "wiederhol"):
            assert forbidden not in message, (forbidden, message)


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
        ap.add_argument(
            "--mode", required=True,
            choices=[
                "setup", "discard", "resume_after_crash",
                "spielen", "local_then_fortsetzen", "writer", "writer_received", "hold",
                "tisch_start", "group_writer", "rebind_tisch_start",
            ],
        )
        ap.add_argument("--root", required=True)
        ap.add_argument("--result", required=True)
        ap.add_argument("--table")
        ns = ap.parse_args()
        if ns.mode == "setup":
            _child_setup(ns)
        elif ns.mode == "discard":
            _child_discard(ns)
        elif ns.mode == "resume_after_crash":
            _child_resume_after_crash(ns)
        elif ns.mode == "writer":
            _child_writer(ns)
        elif ns.mode == "writer_received":
            _child_writer_received(ns)
        elif ns.mode == "hold":
            _child_hold_exclusivity(ns)
        elif ns.mode == "tisch_start":
            _child_tisch_start(ns)
        elif ns.mode == "group_writer":
            _child_group_writer(ns)
        elif ns.mode == "rebind_tisch_start":
            _child_rebind_tisch_start(ns)
        else:
            _child_follow_through(ns)
        sys.exit(0)
    raise SystemExit(main())
