#!/usr/bin/env python3
"""
tests/mmo_sim/test_r2_f1_f2_f3_tabledienst_2026_11_02.py — ZR-FIGURENREISE-
TISCH-NACHZUG-20261102-R2, enger Nachzug F1/F2/F3 (02_NACHZUG.md,
review/independent-r1-review.md).

Deckt:
F1 — frühe Gastgrenze VOR Lock/Tisch-Persist (direktes `_cmd_local_round`,
     wie der `l`-Alias/Fortsetzen-Sologastfallback es erreicht) + neuer
     Such-/Listenbefehl `tisch-suchen` (kein table_key vorher nötig) +
     schmaler In-Process-Gastdienst (eigene private Katalog-/Onboarding-
     Wurzel, NUR run_dir mit dem Host geteilt, für Admission-Operationen).
F2 — `table_admission.bind_section`/`close_table`: die tatsächlich
     gestartete Abschnittskennung wird zurückgebunden; nach echtem
     Abschluss schließt die Admission mit; Leave bei offenem Abschnitt
     erklärt den sicheren Pause-/Abschlussweg.
F3 — `_cmd_table_start` treibt eine eigene bestätigte Hostpersona ALS
     Persona (nicht als Mensch); `tisch-anfragen-persona` ist HOST-ONLY
     und weist eine fremde/unbekannte Persona-ID VOR jeder Mutation ab.

Fakes nur am GM-Transportrand (`_FakeTableGm`, Muster aus
`test_stage5_tui_wiring_2026_11_02.py`) -- Produktpersistenz läuft echt.

Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import json
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402
from _section_completion_resume_fixtures import debrief_with_marker  # noqa: E402

from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core import table_admission  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.community_bootstrap import bootstrap_community  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, GuestCapabilityError, TuiSession  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


class _SpyFactory:
    """Wirft SOFORT bei Aufruf -- Nachweis Providerfreiheit (design.md §2,
    identisches Muster zu `test_stage4_capability_gate_2026_11_02.py`)."""

    def __init__(self, label: str):
        self.label = label
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        raise AssertionError(f"Spy-Factory '{self.label}' wurde aufgerufen (Gate-Bruch).")


class _FakeTableGm:
    """Zwei SL-Antworten ohne Abschluss-Marker, danach (Zug 3+) der volle
    Debrief MIT Marker -- derselbe Rhythmus wie in `test_stage5_tui_
    wiring_2026_11_02.py._FakeTableGm`."""

    def __init__(self, debrief_text: str):
        self._debrief = debrief_text
        self.calls = 0

    def turn(self, turn_idx, text, **kw):
        self.calls += 1
        if self.calls < 3:
            return {"content": f"SL-Antwort #{self.calls} (kein Abschluss)."}
        return {"content": self._debrief}


def _smart_input():
    counter = {"n": 0}

    def _fn(prompt: str = "") -> str:
        if "[j/n]" in prompt:
            return "j"
        if "Wahl [a/k]" in prompt:
            return "a"
        counter["n"] += 1
        return f"Zug {counter['n']}."
    return _fn


def _register_own_figure(
    onboarding_dir: Path, catalog_dir: Path, participant_id: str, char_id: str, level: int = 1,
    *, run_dir: Path | None = None, states_dir: Path | None = None,
) -> dict:
    save = full_v7_save(char_id, name=participant_id, save_id=f"fixture-{participant_id}-001", level=level)
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
    ))
    if run_dir is not None and states_dir is not None:
        ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
        onboarding.ensure_participant_persona_state(ps_store, states_dir, participant_id, char_id, save)
        core_store.publish_current_save(run_dir, participant_id, save, ps_store, states_dir)
    return save


def _bootstrap_own_persona(run_dir: Path, states_dir: Path, host_id: str, persona_key: str) -> None:
    """Legt `persona_key` als EIGENE bestaetigte Hostpersona von `host_id`
    an -- genau der Bestand, den `TuiSession._known_ai_overview()` liest
    (`community-<host_id>`, `bootstrap_community`-Produktfunktion, Muster
    `_a24_local_support.bootstrap_six_persona_community`)."""
    ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
    community_dir = run_dir / "community"
    drafts = {
        persona_key: {
            "real_name": persona_key, "archetype": "Test-Archetyp",
            "play_style": "SIMULIERT/DEMO", "charwunsch": "SIMULIERT/DEMO (R2-F3-Testfixture).",
            "plays_char": {
                "save_file": "NOCH_NICHT_ERSCHAFFEN", "character_id": "NOCH_NICHT_ERSCHAFFEN",
                "name": "NOCH_NICHT_ERSCHAFFEN", "callsign": "NOCH_NICHT_ERSCHAFFEN",
            },
        },
    }
    result = bootstrap_community(community_dir, f"community-{host_id}", 1, drafts, ps_store, states_dir, today="2026-11-02")
    assert persona_key in result.personas_written, result.reason


# ── F1: fruehe Gastgrenze ───────────────────────────────────────────────────


def test_f1_guest_direct_local_round_blocked_before_any_lock_or_table_write():
    """Der direkte `l`-Alias/Fortsetzen-Sologastfallback ruft
    `_cmd_local_round` unmittelbar auf -- fuer `host_capable=False` MUSS
    das VOR jedem `core_store.create_table_from_offer_log`-Aufruf (der
    Figuren sperrt + einen Tisch persistiert, `store.py` ~362-421)
    abgewiesen werden. Vorher/Nachher-Bytes: `locks.json` bleibt {}, kein
    `tables/*.json` entsteht."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir = d / "run"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        states_dir = d / "states"
        write_test_profile(run_dir, max_turns=200)
        _register_own_figure(
            onboarding_dir, catalog_dir, "guest1", "CHR-GUEST1", level=1,
            run_dir=run_dir, states_dir=states_dir,
        )
        # Vorher: kein Lock, kein Tisch.
        lobby_before = core_store.Lobby(run_dir, table_size_policy=__import__(
            "mmo_sim.domain.zeitriss.policy", fromlist=["ZeitrissTableSizePolicy"]
        ).ZeitrissTableSizePolicy())
        assert lobby_before.is_locked("CHR-GUEST1") is None
        tables_dir = run_dir / "tables"
        before_tables = sorted(tables_dir.glob("*.json")) if tables_dir.exists() else []
        assert before_tables == []

        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="guest1",
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=_SpyFactory("guest_gm"), persona_driver_factory=_SpyFactory("guest_persona"),
            host_capable=False,
        )
        try:
            session._cmd_local_round([])
            raise AssertionError("_cmd_local_round haette GuestCapabilityError werfen muessen (F1).")
        except GuestCapabilityError:
            pass

        # Nachher: unveraendert -- kein Lock, kein Tisch, 0 Providercalls.
        lobby_after = core_store.Lobby(run_dir, table_size_policy=lobby_before.table_size_policy)
        assert lobby_after.is_locked("CHR-GUEST1") is None
        after_tables = sorted(tables_dir.glob("*.json")) if tables_dir.exists() else []
        assert after_tables == [], f"Gast-Aufruf haette KEINEN Tisch persistieren duerfen: {after_tables}"


def test_f1_tisch_suchen_lists_open_table_for_unrelated_new_guest():
    """F1 §1: ein brandneuer Gast, der NOCH NIE angefragt hat und den
    `table_key` nicht kennt, sieht den offenen Tisch ueber `tisch-suchen`
    -- reine Lesefunktion, 0 Writes."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir = d / "run"
        table_admission.offer_table(run_dir, host_id="host1", table_key="mesa1")
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="brandnew_guest",
            run_dir=run_dir, host_capable=False,
        )
        printed: list[str] = []
        session._print = printed.append
        session._cmd_table_search([])
        assert any("mesa1" in p for p in printed), printed
        assert any("host1" in p for p in printed), printed
        # 0 Writes: Record unveraendert.
        record = table_admission.load_record(run_dir, "mesa1")
        assert record["roster"] == ["host1"] and record["requests"] == []


def test_f1_narrow_guest_connector_private_catalog_never_touches_host_catalog():
    """F1 §2: der schmale In-Process-Gastdienst teilt NUR `run_dir`
    (table_admission) mit dem Host -- die eigene Katalog-/Onboarding-
    Wurzel bleibt PRIVAT. Beweis: nach Suche/Anfrage/Status/Ruecknahme
    existiert UNTER DEM HOST-`run_dir` kein Katalog-/Onboarding-Ordner
    (der Gast hat nie dorthin geschrieben), und die eigene private Wurzel
    bleibt komplett getrennt vom Host-Datenbaum."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        host_run_dir = d / "host_run"
        table_admission.offer_table(host_run_dir, host_id="host1", table_key="mesa1")

        guest_private_root = d / "guest_private"
        guest_onboarding = guest_private_root / "onboarding"
        guest_catalog = guest_private_root / "catalog"
        # Schmaler Connector: eigene private Wurzel fuer Onboarding/Katalog,
        # `run_dir` zeigt EXPLIZIT auf den fremden Host-Tischdienst -- genau
        # "ein schmaler, ausdruecklich lokaler In-Process-Anschluss" (F1 §2).
        guest_session = TuiSession(
            onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id="guest1",
            run_dir=host_run_dir, host_capable=False,
        )
        printed: list[str] = []
        guest_session._print = printed.append
        guest_session._cmd_table_search([])
        guest_session._cmd_table_request_join(["mesa1"])
        guest_session._cmd_table_status(["mesa1"])
        guest_session._cmd_table_withdraw(["mesa1"])

        # Der Host-run_dir hat NUR `table_admission/` bekommen -- kein
        # Katalog-/Onboarding-Unterordner wurde dort je angelegt.
        assert not (host_run_dir / "catalog").exists()
        assert not (host_run_dir / "onboarding").exists()
        assert (host_run_dir / "table_admission").is_dir()
        # Die eigene private Wurzel wurde fuer diese reinen Admission-
        # Operationen (noch) gar nicht beschrieben (kein Katalogeintrag
        # noetig, um anzufragen/zu suchen/zurueckzuziehen).
        assert not guest_catalog.exists() or list(guest_catalog.glob("*.json")) == []


# ── F2: Admission <-> echte Abschnittsbindung ──────────────────────────────


def test_f2_section_bound_and_admission_closes_after_real_completion():
    """F2 §1: nach `tisch-start` ist die REAL gestartete Abschnittskennung
    (`table.table_id`) im Admission-Record gebunden; schliesst der echte
    Store-Tisch (Debrief mit Marker), schliesst die Admission mit -- ein
    erneuter `tisch-start` auf DIESELBE `table_key` trifft danach ehrlich
    auf 'geschlossen', statt blind idempotent weiterzulaufen."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)
        _register_own_figure(
            onboarding_dir, catalog_dir, "host1", "CHR-HOST1", level=1,
            run_dir=run_dir, states_dir=states_dir,
        )
        _register_own_figure(
            onboarding_dir, catalog_dir, "guest1", "CHR-GUEST1", level=1,
            run_dir=run_dir, states_dir=states_dir,
        )
        debrief_host = full_v7_save("CHR-HOST1", name="host1", save_id="fixture-host1-002", level=1)
        debrief_guest = full_v7_save("CHR-GUEST1", name="guest1", save_id="fixture-guest1-002", level=1)
        debrief_text = debrief_with_marker({"CHR-HOST1": debrief_host, "CHR-GUEST1": debrief_guest})
        fake_gm = _FakeTableGm(debrief_text)

        host_session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="host1",
            input_fn=_smart_input(), print_fn=lambda *_a, **_kw: None,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: fake_gm, persona_driver_factory=_SpyFactory("host_persona"),
            host_capable=True,
        )
        guest_session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="guest1",
            run_dir=run_dir, host_capable=False,
        )

        host_session._cmd_table_offer(["mesa2"])
        guest_session._cmd_table_request_join(["mesa2"])
        host_session._cmd_table_accept(["mesa2", "guest1"])
        host_session._cmd_table_start(["mesa2"])

        record = table_admission.load_record(run_dir, "mesa2")
        assert record.get("section_id"), "F2: section_id haette gebunden werden muessen."
        section = core_store.Table.load(run_dir, record["section_id"])
        assert section.status == "closed", f"Store-Tisch nicht geschlossen: {section.status!r}"
        assert record["state"] == table_admission.STATE_CLOSED, (
            f"Admission haette nach echtem Abschluss mitschliessen muessen, state={record['state']!r}"
        )

        # Erneuter Start auf DIESELBE table_key: ehrlich 'geschlossen'.
        printed: list[str] = []
        host_session._print = printed.append
        host_session._cmd_table_start(["mesa2"])
        assert any("Tischstart abgelehnt" in p and "geschlossen" in p for p in printed), printed


def test_f2_leave_during_open_section_explains_pause_path():
    """F2 §3: ein Leave WAEHREND der Store-Tisch noch real offen ist
    (Round pausiert vor Debrief) loescht das Roster weiterhin wirksam,
    erklaert aber zusaetzlich den sicheren Pause-/Abschlussweg statt
    bloss 'verlassen' zu melden."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)
        _register_own_figure(
            onboarding_dir, catalog_dir, "host1", "CHR-HOST1", level=1,
            run_dir=run_dir, states_dir=states_dir,
        )
        _register_own_figure(
            onboarding_dir, catalog_dir, "guest1", "CHR-GUEST1", level=1,
            run_dir=run_dir, states_dir=states_dir,
        )

        class _NeverClosingGm:
            def turn(self, turn_idx, text, **kw):
                return {"content": "SL-Antwort (nie fertig)."}

        def _pausing_input():
            # Jeder Spielzug-Prompt wird sofort pausiert ('/pause'); nur die
            # Beitritts-/Importbestaetigungen bekommen 'j'.
            def _fn(prompt: str = "") -> str:
                if "[j/n]" in prompt:
                    return "j"
                return "/pause"
            return _fn

        host_session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="host1",
            input_fn=_pausing_input(), print_fn=lambda *_a, **_kw: None,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: _NeverClosingGm(), persona_driver_factory=_SpyFactory("host_persona"),
            host_capable=True,
        )
        guest_session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="guest1",
            run_dir=run_dir, host_capable=False,
        )
        host_session._cmd_table_offer(["mesa3"])
        guest_session._cmd_table_request_join(["mesa3"])
        host_session._cmd_table_accept(["mesa3", "guest1"])
        try:
            host_session._cmd_table_start(["mesa3"])  # bricht per /pause ab, Section bleibt offen.
        except EndOfInput:
            # Dieselbe kontrollierte Pause, die `run()`s zentraler
            # Dispatch-Loop sonst auffaengt (tui.py `run()`: 'EOF waehrend
            # eines Untermenues') -- dieser Test ruft die Methode direkt,
            # ohne den Dispatch-Loop, und faengt deshalb selbst ab.
            pass

        record = table_admission.load_record(run_dir, "mesa3")
        assert record.get("section_id"), "section_id haette trotz Pause gebunden sein muessen."
        section = core_store.Table.load(run_dir, record["section_id"])
        assert section.status != "closed", "Testvoraussetzung: Section muss real offen bleiben."

        printed: list[str] = []
        guest_session._print = printed.append
        guest_session._cmd_table_leave(["mesa3"])
        left_record = table_admission.load_record(run_dir, "mesa3")
        assert "guest1" not in left_record["roster"], "Leave haette das Roster real aendern muessen."
        assert any("verlassen" in p for p in printed), printed
        assert any("/pause" in p and "OFFEN" in p for p in printed), (
            f"Erwartete Pause-/Abschlusserklaerung fehlt: {printed}"
        )


# ── F3: Hostpersona-Autoritaet ──────────────────────────────────────────────


def test_f3_table_start_drives_own_confirmed_persona_as_persona():
    """F3 §1: eine EIGENE bestaetigte Hostpersona im Admission-Roster wird
    von `_cmd_table_start` ALS Persona getrieben (persona_driver_factory),
    NICHT als Mensch (kein Beitritts-Ja/Nein-Prompt fuer sie)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)
        _register_own_figure(
            onboarding_dir, catalog_dir, "host1", "CHR-HOST1", level=1,
            run_dir=run_dir, states_dir=states_dir,
        )
        _bootstrap_own_persona(run_dir, states_dir, "host1", "ownpersona1")
        # `_resolve_member`/`_run_table_round` brauchen eine AUFLOESBARE
        # Figur fuer JEDES Mitglied (Leader UND Gast, A7/D1) -- auch eine
        # Persona-Mitgliedschaft ALLEIN (Community-Bootstrap oben) reicht
        # dafuer nicht, sie braucht einen eigenen abgeschlossenen
        # Onboarding-/Katalog-/Current-Eintrag unter DERSELBEN Datenwurzel
        # wie der Host (dieselbe Autoritaet wie bei jedem menschlichen
        # Mitglied, kein zweiter Mechanismus fuer Personas).
        _register_own_figure(
            onboarding_dir, catalog_dir, "ownpersona1", "CHR-PERSONA1", level=1,
            run_dir=run_dir, states_dir=states_dir,
        )

        class _PersonaDriver:
            is_human_driver = False

            def __init__(self):
                self.decide_calls = 0

            def decide(self, context):
                self.decide_calls += 1
                from mmo_sim.adapters.base import ParticipantDecision
                return ParticipantDecision(text="Persona-Zug.", origin_source="persona:test")

        persona_driver = _PersonaDriver()
        persona_calls: list[str] = []

        def _persona_factory(persona_id: str):
            persona_calls.append(persona_id)
            return persona_driver

        debrief_host = full_v7_save("CHR-HOST1", name="host1", save_id="fixture-host1-003", level=1)
        debrief_persona = full_v7_save("CHR-PERSONA1", name="ownpersona1", save_id="fixture-persona1-003", level=1)
        debrief_text = debrief_with_marker({"CHR-HOST1": debrief_host, "CHR-PERSONA1": debrief_persona})
        fake_gm = _FakeTableGm(debrief_text)

        host_session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="host1",
            input_fn=_smart_input(), print_fn=lambda *_a, **_kw: None,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: fake_gm, persona_driver_factory=_persona_factory,
            host_capable=True,
        )
        host_session._cmd_table_offer(["mesa4"])
        # Der Host meldet seine EIGENE Persona ueber die getrennte
        # Anfrageseite an (F3 §1: 'Persona-Anfrage und Hostentscheidung
        # bleiben getrennte Vorgaenge').
        host_session._cmd_table_request_persona(["mesa4", "ownpersona1"])
        host_session._cmd_table_accept(["mesa4", "ownpersona1"])
        host_session._cmd_table_start(["mesa4"])

        assert persona_calls == ["ownpersona1"], f"Persona-Factory haette fuer ownpersona1 aufgerufen werden muessen: {persona_calls}"
        assert persona_driver.decide_calls >= 1, "Persona-Driver haette tatsaechlich treiben sollen."


def test_f3_request_persona_rejects_unknown_persona_without_mutation():
    """F3 §2: eine FREMDE/unbekannte Persona-ID wird VOR jeder
    `table_admission`-Mutation abgewiesen -- 0 Writes."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir = d / "run"
        table_admission.offer_table(run_dir, host_id="host1", table_key="mesa5")
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="host1",
            run_dir=run_dir, host_capable=True,
        )
        printed: list[str] = []
        session._print = printed.append
        session._cmd_table_request_persona(["mesa5", "unknown_foreign_persona"])
        assert any("keine eigene bestaetigte" in p for p in printed), printed
        record = table_admission.load_record(run_dir, "mesa5")
        assert record["requests"] == [], f"Fremde Persona-Anfrage haette NICHT mutieren duerfen: {record}"


def test_f3_request_persona_accepts_own_confirmed_persona():
    """F3 §1 positive Gegenprobe: die eigene bestaetigte Persona darf
    anfragen, der Host entscheidet getrennt."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        table_admission.offer_table(run_dir, host_id="host1", table_key="mesa6")
        _bootstrap_own_persona(run_dir, states_dir, "host1", "ownpersona2")
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="host1",
            run_dir=run_dir, states_dir=states_dir, host_capable=True,
        )
        session._cmd_table_request_persona(["mesa6", "ownpersona2"])
        record = table_admission.load_record(run_dir, "mesa6")
        assert record["requests"] == ["ownpersona2"], record


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
    raise SystemExit(main())
