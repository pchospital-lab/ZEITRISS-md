#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_g03_same_authority_resume_2026_10_05.py — G03
(ZEITRISS Terminal UX-1, Korrekturzyklus 2, Wiederanlauf W6): "Fortsetzen"-
Karte UND Dispatch an dieselbe Autoritaet binden.

Deckt:
- P03 (General-Befund 'P03_STALE_RESUME_SUMMARY'): ein neuerer autoritativer
  Current (NEW_CURRENT_ONLY, Level 7) erscheint auf der Karte korrekt, NICHT
  der alte Onboarding-Finalsave (OldFigure). `open_section_id` traegt die
  tatsaechliche Tisch-/Lock-ID, nicht den Platzhaltertext "aktiv".
- P04 (General-Befund 'P04_OPEN_CREATION_NOT_OFFERED'): eine real begonnene,
  noch offene Erschaffung liefert eine Karte (nicht `None`) und wird als
  solche erkannt/behandelt (kein automatischer Spielstart ohne Figur).
- UX12: ein bekannter, aber GERADE nicht lesbarer Current stoppt
  `_cmd_menu_fortsetzen` sicher -- kein stiller Rueckfall, keine getarnte
  neue Runde.
- P09 (General-Befund 'P09_MAIN_RESUME_TWO_PERSON_SECTION'): ein real
  aufgebauter Zweipersonentisch (Mensch-Leader + KI-Gast), nach Leader- UND
  Gastbeitrag pausiert, wird in einem ECHTEN, separaten OS-Prozess (nicht nur
  einem zweiten TuiSession-Objekt) tatsaechlich fortgesetzt -- derselbe
  Tisch (keine neue Solo-Tisch-ID), KEINE neue Einladungs-/Consent-
  Anfrage/Doppelcall an den bereits aufgenommenen Gast, der naechste
  Spielzug ist real erreichbar.

Pure Python, nur `assert` (ausser Teil 4, der echte Subprozesse startet),
synthetische Daten/Temp-Dirs, kein Netzwerk-/externer Providercall."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _full_v7_fixture import full_v7_save, upgrade_narrow_save  # noqa: E402

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import (  # noqa: E402
    COMPLETION_MARKER, ZeitrissHarvestValidator, ZeitrissTableSizePolicy,
)
from mmo_sim.ui.tui import EndOfInput, TuiSession, render_boot_menu  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
_FIX = _REPO_ROOT / "internal" / "qa" / "harness" / "lobby" / "fixtures" / "saves"


def _queued_input(values):
    q = list(values)

    def input_fn(prompt: str = "") -> str:
        if q:
            return q.pop(0)
        raise EOFError()

    return input_fn


def _old_onboarding_save(char_id: str = "chrono-old-001") -> dict:
    return full_v7_save(char_id, name="OldFigure", level=3, save_id="fixture-old-onboarding-001")


def _new_current_save(char_id: str = "chrono-old-001") -> dict:
    # Dieselbe char_id wie der Onboarding-Finalsave -- derselbe Chrononaut,
    # bloss ein SPAETERER, bereits veroeffentlichter Stand (ein gespielter
    # Abschnitt nach dem Onboarding-Abschluss).
    return full_v7_save(char_id, name="NEW_CURRENT_ONLY", level=7, save_id="fixture-new-current-only-001")


def _env(root: Path):
    states_dir, run_dir = root / "states", root / "run"
    onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
    states_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    return _SCHEMA, states_dir, run_dir, onboarding_dir, catalog_dir


def _session(participant_id, onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
             input_fn=None, gm_transport_factory=None, persona_driver_factory=None, printed=None):
    printed = printed if printed is not None else []
    return TuiSession(
        onboarding_dir, catalog_dir, participant_id,
        input_fn=input_fn or (lambda prompt="": (_ for _ in ()).throw(EOFError())),
        print_fn=printed.append,
        run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
        gm_transport_factory=gm_transport_factory,
        persona_driver_factory=persona_driver_factory,
    ), printed


# --------------------------------------------------------------------------
# P03: dieselbe Autoritaet fuer Karte wie Start -- neuerer Current statt
# altem Onboarding-Finalsave; echte Tisch-/Lock-ID statt Literal "aktiv".
# --------------------------------------------------------------------------

def test_p03_resume_card_shows_newer_authoritative_current_not_stale_onboarding():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
        ps_store = PersonaStateStore(schema_path=schema_path)
        pid = "sniper"
        old_save = _old_onboarding_save()
        chrono_id = old_save["characters"][0]["id"]
        onboarding.start_or_resume(onboarding_dir, pid)
        onboarding.complete_with_save(onboarding_dir, pid, old_save, ZeitrissHarvestValidator(), chrono_id)
        onboarding.ensure_participant_persona_state(ps_store, states_dir, pid, chrono_id, old_save)
        # Ein SPAETER veroeffentlichter neuerer Current (z.B. nach einem
        # gespielten Abschnitt) -- die Karte MUSS diesen zeigen, nicht mehr
        # den alten Onboarding-Finalsave.
        new_save = _new_current_save()
        core_store.publish_current_save(run_dir, pid, new_save, ps_store, states_dir)

        session, _printed = _session(pid, onboarding_dir, catalog_dir, run_dir, states_dir, schema_path)
        card = session._build_resume_card()
        assert card is not None
        assert card.last_valid_save_summary == "NEW_CURRENT_ONLY (Level 7)", card
        assert "OldFigure" not in (card.last_valid_save_summary or ""), card
        assert card.authority_unresolved is False, card


def test_p03_open_section_id_is_real_table_id_not_literal_aktiv():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
        ps_store = PersonaStateStore(schema_path=schema_path)
        pid = "sniper"
        save = _new_current_save()
        chrono_id = save["characters"][0]["id"]
        onboarding.start_or_resume(onboarding_dir, pid)
        onboarding.complete_with_save(onboarding_dir, pid, save, ZeitrissHarvestValidator(), chrono_id)
        onboarding.ensure_participant_persona_state(ps_store, states_dir, pid, chrono_id, save)
        core_store.publish_current_save(run_dir, pid, save, ps_store, states_dir)
        # `catalog.last_selected` ist die reale Quelle fuer `_build_resume_
        # card`s `chrononaut_id` -- `bind_for_section` ist derselbe Weg, den
        # `_cmd_new_or_switch_character` nach echter Erschaffung nutzt.
        from mmo_sim.domain.zeitriss import catalog
        catalog.register(catalog_dir, catalog.CatalogEntry(
            participant_id=pid, chrononaut_id=chrono_id, persona_key=pid,
        ))
        catalog.bind_for_section(catalog_dir, pid, chrono_id, has_open_section=False)
        # Realer Lock (wie ihn `create_table_from_offer_log` setzt) -- eine
        # reine Lesefunktion (`core.store.locked_table_id`) muss ihn jetzt
        # korrekt zeigen.
        lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        lobby.lock_chrononaut(chrono_id, "local-sniper-tech")

        session, _printed = _session(pid, onboarding_dir, catalog_dir, run_dir, states_dir, schema_path)
        card = session._build_resume_card()
        assert card is not None
        assert card.open_section_id == "local-sniper-tech", card
        text = render_boot_menu(card)
        assert "local-sniper-tech" in text, text
        assert "(Abschnitt local-sniper-tech unterbrochen)" in text, text


# --------------------------------------------------------------------------
# P04: offene Erschaffung liefert eine Karte (nicht None), wird unterscheid-
# bar erkannt -- kein automatischer Spielstart ohne Figur.
# --------------------------------------------------------------------------

def test_p04_open_creation_yields_card_not_none_and_honest_dispatch():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
        pid = "freshling"
        # Real begonnene, noch NICHT abgeschlossene Erschaffung (Status
        # bleibt "in_progress" -- kein `complete_with_save`).
        onboarding.start_or_resume(onboarding_dir, pid)

        session, printed = _session(pid, onboarding_dir, catalog_dir, run_dir, states_dir, schema_path)
        card = session._build_resume_card()
        assert card is not None, "P04: offene Erschaffung darf keine leere Karte liefern"
        assert card.pending_creation is True, card
        assert card.chrononaut_id is None and card.community_id is None, card
        assert card.authority_unresolved is False, card

        session._cmd_menu_fortsetzen()
        out = "\n".join(printed)
        assert "Erschaffung" in out and "noch offen" in out, out
        assert "kein Stand" not in out, "P04: darf nicht mehr als 'kein Stand' gemeldet werden"
        assert "Lokale Runde erfordert" not in out, "kein automatischer Spielstart ohne Figur"


# --------------------------------------------------------------------------
# UX12: bekannter, aber gerade nicht lesbarer Current -- sicherer Stopp,
# kein stiller Rueckfall, keine getarnte neue Runde.
# --------------------------------------------------------------------------

def test_ux12_unresolved_known_current_stops_safely_no_fallback():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
        ps_store = PersonaStateStore(schema_path=schema_path)
        pid = "sniper"
        old_save = _old_onboarding_save()
        chrono_id = old_save["characters"][0]["id"]
        onboarding.start_or_resume(onboarding_dir, pid)
        onboarding.complete_with_save(onboarding_dir, pid, old_save, ZeitrissHarvestValidator(), chrono_id)
        onboarding.ensure_participant_persona_state(ps_store, states_dir, pid, chrono_id, old_save)
        new_save = _new_current_save()
        core_store.publish_current_save(run_dir, pid, new_save, ps_store, states_dir)
        # Bekannter Current -- die referenzierte Versionsdatei wird jetzt
        # ECHT entfernt (kein Mock): ein real fehlendes Blatt derselben
        # Referenzkette, kein erfundener Fehler.
        state = ps_store.load_state(pid, states_dir=states_dir)
        ref = state["current_save_version"]
        version_path = run_dir / "current_saves" / f"{pid}__versions" / f"{int(ref['seq']):04d}.json"
        assert version_path.exists()
        version_path.unlink()

        session, printed = _session(pid, onboarding_dir, catalog_dir, run_dir, states_dir, schema_path)
        card = session._build_resume_card()
        assert card is not None
        assert card.authority_unresolved is True, card
        assert "OldFigure" not in (card.last_valid_save_summary or ""), (
            "UX12: kein stiller Rueckfall auf den alten Onboarding-Stand", card
        )

        session._cmd_menu_fortsetzen()
        out = "\n".join(printed)
        assert "nicht lesbar" in out, out
        assert "kein Reparaturwrite" in out, out
        assert "OldFigure" not in out, out
        # Kein stiller Weiterlauf in den Solo-/Gruppenspielstart.
        assert "Lokale Runde erfordert" not in out, out
        assert "Gruppe eingeladen" not in out, out


# --------------------------------------------------------------------------
# P09: echter OS-Neustart-Beleg -- zwei getrennte reale Prozesse.
# --------------------------------------------------------------------------

class _TechDriver:
    """KI-Gast 'tech': nimmt GENAU EINE Einladung an (Kontrollform-Vertrag).
    `forbid_invite=True` (Prozess 2) laesst einen ERNEUTEN Einladungs-
    Request (decision_contract im Kontext) fehlschlagen -- ein echter
    Doppelcall-Beleg, kein blosses Nichtbeobachten."""

    def __init__(self, forbid_invite: bool = False):
        self.forbid_invite = forbid_invite
        self.calls: list[dict] = []

    def decide(self, ctx: dict) -> ParticipantDecision:
        self.calls.append(ctx)
        if "decision_contract" in ctx:
            if self.forbid_invite:
                raise AssertionError("P09: verbotener erneuter Einladungs-/Consent-Request an 'tech' beim Resume")
            dc = ctx["decision_contract"]
            text = f"ENTSCHEIDUNG offer_id={dc['offer_id']} participant_id={dc['participant_id']} decision=accept"
        else:
            text = "SYNTHETIC: Wir beobachten und helfen am Tisch."
        return ParticipantDecision(text=text, origin_source="g03-p09-test:tech")


class _OpenTableGM:
    """Gescriptetes GM-Fake, das NIEMALS den Abschlussmarker liefert
    (`turns_before_marker` absichtlich unerreichbar hoch) -- der Tisch bleibt
    nach jedem Turn `active`, genau das in P03/P04/P09-REVIEW.md P09
    beschriebene 'pausiert, nicht abgeschlossen'."""

    def __init__(self):
        self.calls: list[str] = []

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append(text)
        return {
            "content": "Ihr beobachtet die Lage weiter. Was tut ihr als Naechstes?",
            "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "table",
        }


class _CompletingTableGM:
    """Gescriptetes GM-Fake fuer Prozess 2: liefert SOFORT (nach 1 Turn) den
    Abschlussmarker samt beider finaler Saves -- belegt, dass der TATSAECH-
    LICHE naechste Spielzug nach dem Resume real bis zum Abschluss reicht."""

    def __init__(self, table_id: str, section_id: str, final_saves: dict):
        self.table_id, self.section_id, self.final_saves = table_id, section_id, final_saves
        self.calls: list[str] = []

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append(text)
        debrief = "\n".join(
            f"```json\n{json.dumps(b, ensure_ascii=False)}\n```" for b in self.final_saves.values()
        )
        content = f"{debrief}\n{COMPLETION_MARKER} table_id={self.table_id} section_id={self.section_id}"
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "table"}


def _make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, persona_key: str) -> dict:
    save = upgrade_narrow_save(json.loads((_FIX / f"{persona_key}.json").read_text(encoding="utf-8")))
    ps_store = PersonaStateStore(schema_path=_SCHEMA)
    chrono_id = save["characters"][0]["id"]
    onboarding.start_or_resume(onboarding_dir, persona_key)
    onboarding.complete_with_save(onboarding_dir, persona_key, save, ZeitrissHarvestValidator(), chrono_id)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, persona_key, chrono_id, save)
    core_store.publish_current_save(run_dir, persona_key, save, ps_store, states_dir)
    # Derselbe Weg, den `_cmd_new_or_switch_character` nach echter
    # Erschaffung nutzt -- `_build_resume_card`s `catalog.last_selected`
    # braucht diese Bindung real, kein Produkt-Stub.
    from mmo_sim.domain.zeitriss import catalog
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=persona_key, chrononaut_id=chrono_id, persona_key=persona_key,
    ))
    catalog.bind_for_section(catalog_dir, persona_key, chrono_id, has_open_section=False)
    return save


def _child_setup(args: argparse.Namespace) -> None:
    """Prozess 1 (ECHTER eigenstaendiger Subprozess, eigene OS-PID): baut
    real einen Zweipersonentisch (Mensch-Leader 'sniper' + KI-Gast 'tech')
    auf, laesst Leader UND Gast je mindestens einen echten Beitrag leisten,
    dann (Eingabequeue erschoepft) kontrolliert pausieren -- OHNE
    Abschluss."""
    root = Path(args.root)
    schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _SCHEMA, root / "states", root / "run", root / "onboarding", root / "catalog"
    states_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    _make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, "sniper")
    _make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, "tech")
    write_test_profile(run_dir)

    gm = _OpenTableGM()
    tech_driver = _TechDriver(forbid_invite=False)
    session = TuiSession(
        onboarding_dir, catalog_dir, "sniper",
        input_fn=_queued_input(["Wir ruecken vorsichtig vor."]),
        print_fn=lambda *_a: None,
        run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
        gm_transport_factory=lambda *_a, **_kw: gm,
        persona_driver_factory=lambda pk: tech_driver,
    )
    try:
        session._cmd_local_round(["persona:tech"])
    except EndOfInput:
        pass  # kontrollierte Pause nach erschoepfter Eingabequeue -- erwartet.

    tables = list((run_dir / "tables").glob("*.json"))
    row = {
        "pid_is_real": True,
        "tables": [json.loads(p.read_text(encoding="utf-8")) for p in tables],
        "table_names": sorted(p.stem for p in tables),
        "gm_calls": len(gm.calls),
        "tech_calls": len(tech_driver.calls),
        "invitation_log": (run_dir / "invitation_decisions.jsonl").read_text(encoding="utf-8")
        if (run_dir / "invitation_decisions.jsonl").exists() else "",
        "locks": json.loads((run_dir / "locks.json").read_text(encoding="utf-8")),
    }
    Path(args.result).write_text(json.dumps(row, indent=2, ensure_ascii=False), encoding="utf-8")


def _child_resume(args: argparse.Namespace) -> None:
    """Prozess 2 (ECHTER ANDERER Subprozess, eigene neue OS-PID) -- eine
    VOELLIG NEUE `TuiSession` fuer denselben Teilnehmer 'sniper' ruft
    `_cmd_menu_fortsetzen()`. `tech_driver.forbid_invite=True`: JEDER
    erneute Einladungs-/Consent-Request an 'tech' ist ein Testfehler
    (Doppelcall-Beleg)."""
    root = Path(args.root)
    schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _SCHEMA, root / "states", root / "run", root / "onboarding", root / "catalog"

    before_tables = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in (run_dir / "tables").glob("*.json")}
    assert len(before_tables) == 1, before_tables
    (table_id,) = before_tables.keys()
    section_id = f"{table_id}-section"
    sniper_save = upgrade_narrow_save(json.loads((_FIX / "sniper.json").read_text(encoding="utf-8")))
    tech_save = upgrade_narrow_save(json.loads((_FIX / "tech.json").read_text(encoding="utf-8")))
    sniper_save = {**sniper_save, "save_id": "fixture-sniper-resume-final-001"}
    tech_save = {**tech_save, "save_id": "fixture-tech-resume-final-001"}
    final_saves = {"sniper": sniper_save, "tech": tech_save}

    gm2 = _CompletingTableGM(table_id, section_id, final_saves)
    tech_driver2 = _TechDriver(forbid_invite=True)
    printed: list[str] = []
    session = TuiSession(
        onboarding_dir, catalog_dir, "sniper",
        input_fn=_queued_input(["Wir sichern die Position.", "Ruhig und konzentriert geblieben."]),
        print_fn=printed.append,
        run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
        gm_transport_factory=lambda *_a, **_kw: gm2,
        persona_driver_factory=lambda pk: tech_driver2,
    )
    errors: list[str] = []
    try:
        session._cmd_menu_fortsetzen()
    except EndOfInput:
        pass
    except Exception as e:  # echter unerwarteter Prozessabbruch bleibt sichtbar.
        errors.append(f"{type(e).__name__}: {e}")

    after_tables = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in (run_dir / "tables").glob("*.json")}
    row = {
        "errors": errors,
        "printed": printed,
        "table_id_before": table_id,
        "table_names_after": sorted(after_tables.keys()),
        "status_after": after_tables.get(table_id, {}).get("status"),
        "sl_log_len_after": len(after_tables.get(table_id, {}).get("sl_log", [])),
        "gm2_calls": len(gm2.calls),
        "tech2_invite_calls": sum(1 for c in tech_driver2.calls if "decision_contract" in c),
        "locks_after": json.loads((run_dir / "locks.json").read_text(encoding="utf-8")),
        "invitation_log_after": (run_dir / "invitation_decisions.jsonl").read_text(encoding="utf-8")
        if (run_dir / "invitation_decisions.jsonl").exists() else "",
    }
    Path(args.result).write_text(json.dumps(row, indent=2, ensure_ascii=False), encoding="utf-8")


def _run_child(root: Path, mode: str, result_path: Path) -> dict:
    """ECHTER, EIGENSTAENDIGER Python-Subprozess (eigene OS-PID) -- Muster
    aus `test_r2_hauptbefund2_bound_table_recovery.py:_run_child`."""
    cmd = [sys.executable, str(Path(__file__).resolve()), "--child", "--mode", mode,
           "--root", str(root), "--result", str(result_path)]
    cp = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if cp.returncode != 0:
        raise RuntimeError(f"child(mode={mode!r}) exit={cp.returncode}:\n{cp.stderr[-4000:]}")
    return json.loads(result_path.read_text(encoding="utf-8"))


def test_p09_real_os_restart_resumes_same_bound_table_no_doppelcall():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)

        r1 = _run_child(root, "setup", root / "r1.json")
        assert not r1["errors"] if "errors" in r1 else True
        assert len(r1["tables"]) == 1, r1["tables"]
        table_name_1 = r1["table_names"][0]
        assert table_name_1 == "local-sniper-tech", (
            f"P09-Vorbedingung: Tisch muss unter local-sniper-tech angelegt sein: {r1['table_names']}"
        )
        assert r1["tables"][0]["status"] == "active", r1["tables"][0]
        assert r1["gm_calls"] >= 1, "Leaderbeitrag muss mindestens einen echten GM-Turn ausgeloest haben"
        assert len(r1["locks"]) == 2, r1["locks"]
        assert '"outcome"' in r1["invitation_log"] or "accept" in r1["invitation_log"], r1["invitation_log"]

        r2 = _run_child(root, "resume", root / "r2.json")
        assert not r2["errors"], r2["errors"]
        # P09-Kernbefund: GENAU derselbe Tisch wird fortgesetzt -- KEIN
        # zweiter/leerer Solo-Tisch ('local-sniper') entsteht.
        assert r2["table_names_after"] == ["local-sniper-tech"], (
            f"P09: `_cmd_menu_fortsetzen` darf keinen neuen/zweiten Tisch anlegen: {r2['table_names_after']}"
        )
        assert r2["table_id_before"] == table_name_1
        # Der tatsaechliche naechste Spielzug ist real erreichbar: der GM
        # in Prozess 2 wurde tatsaechlich aufgerufen UND der Abschnitt
        # konnte real abgeschlossen werden (beide Mitglieder entsperrt).
        assert r2["gm2_calls"] >= 1, "P09: der naechste Spielzug muss nach dem Resume real erreichbar sein"
        assert r2["status_after"] == "closed", r2
        assert r2["locks_after"] == {}, "normaler Lock-Release nach echtem Abschluss erwartet"
        # KEIN Doppelcall: 'tech' wurde in Prozess 2 NICHT erneut um
        # Einladungs-/Consent-Entscheidung gebeten (die Mitgliedschaft war
        # bereits real zugesagt).
        assert r2["tech2_invite_calls"] == 0, (
            f"P09: kein erneuter Einladungs-/Consent-Request an 'tech' beim Resume erwartet: {r2}"
        )
        # KEINE neue Einladungs-/Consent-Zeile im Log durch den Resume selbst
        # (nur die urspruenglichen Zeilen aus Prozess 1 bleiben erhalten).
        log_lines_before = [ln for ln in r1["invitation_log"].splitlines() if ln.strip()]
        log_lines_after = [ln for ln in r2["invitation_log_after"].splitlines() if ln.strip()]
        assert log_lines_after == log_lines_before, (
            "P09: `_cmd_menu_fortsetzen` darf keine neue Einladungs-/Consent-Zeile anhaengen "
            f"(Doppelcall/Publikation): vorher={log_lines_before} nachher={log_lines_after}"
        )


def main() -> int:
    tests = [
        test_p03_resume_card_shows_newer_authoritative_current_not_stale_onboarding,
        test_p03_open_section_id_is_real_table_id_not_literal_aktiv,
        test_p04_open_creation_yields_card_not_none_and_honest_dispatch,
        test_ux12_unresolved_known_current_stops_safely_no_fallback,
        test_p09_real_os_restart_resumes_same_bound_table_no_doppelcall,
    ]
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
        ap = argparse.ArgumentParser()
        ap.add_argument("--child", action="store_true")
        ap.add_argument("--mode", required=True, choices=["setup", "resume"])
        ap.add_argument("--root", required=True)
        ap.add_argument("--result", required=True)
        ns = ap.parse_args()
        if ns.mode == "setup":
            _child_setup(ns)
        else:
            _child_resume(ns)
        sys.exit(0)
    raise SystemExit(main())
