#!/usr/bin/env python3
"""
tests/mmo_sim/test_linus_n123_2026_11_06.py -- ZR-VOLLENDUNG-R3-NACHZUG
(GENERAL-REVIEW.md N1/N2/N3, Linus-Briefing linus-n123.md). Gezielte Belege
fuer die drei Befunde, isolierte QA-Daten (tmpdir), deterministischer Rand,
0 bezahlte Modellaufrufe (nur In-Process-Doubles am GM-/Persona-Transportrand,
ehrlich gekennzeichnet). Pure Python, nur `assert`, echter Exitcode (Muster
aus test_r3_f1_guest_table_service.py / test_zr_betreiber_r2_f3a_abbruch_
lifecycle_2026_11_04.py)."""
from __future__ import annotations

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
from _zr_betreiber_fixtures_2026_11_03 import (  # noqa: E402
    SCHEMA_PATH, AcceptLeadDriver, bootstrap_own_persona, register_own_figure,
)

from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core import table_admission  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

_SCHEMA_PATH = SCHEMA_PATH


def _register_host_figure(onboarding_dir, catalog_dir, run_dir, states_dir, participant_id, char_id):
    from mmo_sim.core.persona_state import PersonaStateStore
    save = full_v7_save(char_id, name=participant_id, save_id=f"fixture-{participant_id}-001", level=1)
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
    ))
    ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, participant_id, char_id, save)
    core_store.publish_current_save(run_dir, participant_id, save, ps_store, states_dir)
    return save


def _register_private_figure(onboarding_dir, catalog_dir, participant_id, char_id):
    save = full_v7_save(char_id, name=participant_id, save_id=f"fixture-{participant_id}-001", level=1)
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
    ))
    return save


class _DivergingInput:
    """N1-Testdouble: liefert bei einem '[j/n]'-Prompt bewusst eine ANDERE
    Antwort als bei einem normalen Spielzug-Prompt -- so laesst sich an der
    tatsaechlich ausgewerteten Entscheidung erkennen, WESSEN input_fn fuer
    den Consent-Prompt konsumiert wurde (kein stiller 'beide Seiten sagen
    ohnehin j'-Fall wie bei den aelteren `_counting_input`-Helpern)."""

    def __init__(self, label: str, jn_answer: str):
        self.label = label
        self.jn_answer = jn_answer
        self.calls_total = 0
        self.calls_jn = 0
        self.calls_turn = 0

    def __call__(self, prompt: str = "") -> str:
        self.calls_total += 1
        if "[j/n]" in prompt:
            self.calls_jn += 1
            return self.jn_answer
        # R4 U3 (01_NACHZUG.md U3 Punkt 3): die jetzt echt bedienbare
        # Abschlusskarte liest nach echtem Abschnittsabschluss eine
        # zusaetzliche Auswahl -- neutral "Zurueck zum Hauptmenue", statt
        # sie wie einen normalen Spielzug zu beantworten.
        if prompt.startswith("Auswahl (Nummer, leer/zurueck = Hauptmenue)"):
            return ""
        self.calls_turn += 1
        return f"{self.label}-Zug {self.calls_turn}."


class _FakeTableGm:
    """Modellrand-Double (EHRLICH gekennzeichnet): liefert N unterscheidbare
    Zwischenantworten, danach einen Debrief mit Abschluss-Marker -- gleiches
    Muster wie test_r3_f1_guest_table_service.py:_FakeTableGm."""

    def __init__(self, debrief_text: str, non_completion_rounds: int = 3):
        self._debrief = debrief_text
        self._non_completion_rounds = non_completion_rounds
        self.calls = 0

    def turn(self, turn_idx, text, **kw):
        self.calls += 1
        if self.calls <= self._non_completion_rounds:
            return {"content": f"SL-Antwort #{self.calls}"}
        return {"content": self._debrief}


def _debrief_text(saves_by_char_id: dict) -> str:
    import json

    from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER
    parts = ["Abschnitt beendet."]
    for blk in saves_by_char_id.values():
        parts.append(f"```json\n{json.dumps(blk)}\n```")
    parts.append(COMPLETION_MARKER)
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# N1 -- Mehrgast-Consent/Fokus am richtigen Kanal
# ---------------------------------------------------------------------------

def test_n1_consent_fuer_registriertes_gastterminal_laeuft_ueber_eigenes_terminal():
    """Ein Gast MIT registriertem eigenem Terminal bestaetigt seinen Beitritt
    ueber SEIN EIGENES Terminal -- NICHT ueber die Host-Tastatur, OHNE
    `_local_round_handoff`. Gegenprobe eingebaut: Host- und Gast-`input_fn`
    antworten bei '[j/n]' BEWUSST unterschiedlich ('n' vs 'j'); haette die
    alte Logik (Consent/Handoff ueber `self`=Host) weiterhin gegriffen, waere
    die Runde entweder an der Handoff-Ablehnung mit `EndOfInput` abgebrochen
    ODER der Gast waere mit 'nicht zugestimmt' abgelehnt worden -- beides
    beobachtbar und verschieden vom tatsaechlich erwarteten Erfolgsfall."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        host_onboarding, host_catalog = d / "host_onboarding", d / "host_catalog"
        guest_onboarding, guest_catalog = d / "guest_onboarding", d / "guest_catalog"
        write_test_profile(run_dir, max_turns=200)
        _register_host_figure(host_onboarding, host_catalog, run_dir, states_dir, "host1", "CHR-N1-HOST")
        _register_private_figure(guest_onboarding, guest_catalog, "guest1", "CHR-N1-GUEST")

        host_in = _DivergingInput("host", jn_answer="n")
        guest_in = _DivergingInput("guest", jn_answer="j")
        host_printed: list[str] = []
        guest_printed: list[str] = []

        debrief_host = full_v7_save("CHR-N1-HOST", name="host1", save_id="fixture-host1-n1-002", level=1)
        debrief_guest = full_v7_save("CHR-N1-GUEST", name="guest1", save_id="fixture-guest1-n1-002", level=1)
        fake_gm = _FakeTableGm(_debrief_text({"CHR-N1-HOST": debrief_host, "CHR-N1-GUEST": debrief_guest}))

        host_session = TuiSession(
            onboarding_dir=host_onboarding, catalog_dir=host_catalog, participant_id="host1",
            input_fn=host_in, print_fn=host_printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: fake_gm, host_capable=True,
        )
        guest_session = TuiSession(
            onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id="guest1",
            input_fn=guest_in, print_fn=guest_printed.append,
            run_dir=run_dir, host_capable=False,
        )

        host_session._cmd_table_offer(["tblN1"])
        guest_session._cmd_table_request_join(["tblN1"])
        host_session._cmd_table_accept(["tblN1", "guest1"])
        host_session.register_guest_terminal("guest1", guest_session)

        host_session._cmd_table_start(["tblN1"])

        record = table_admission.load_record(run_dir, "tblN1")
        section = core_store.Table.load(run_dir, record["section_id"])
        assert section.status == "closed", f"Abschnitt haette abgeschlossen sein sollen: {section.status}"
        assert "guest1" in section.members, (
            f"'guest1' haette ueber den EIGENEN Terminal-Consent beitreten muessen: {section.members}"
        )
        # Der Gast hat selbst geantwortet -- auf seinem eigenen Kanal.
        assert guest_in.calls_jn >= 1, "Gast haette den [j/n]-Consent-Prompt selbst beantworten muessen."
        assert guest_in.calls_turn > 0, "Gast haette auch seinen eigenen Spielzug eingeben muessen."
        # KEINE Terminaluebergabe (`_local_round_handoff`) fuer einen
        # registrierten Gast -- der zugehoerige Text darf NICHT erscheinen.
        assert not any("Eingabeuebergabe" in p for p in host_printed), (
            f"Fuer ein registriertes Gastterminal darf keine Host-Terminaluebergabe stattfinden: {host_printed}"
        )
        # Der Host hat seine (bewusst falsche) [j/n]-Antwort 'n' NIE fuer
        # den Gast-Consent gebraucht -- sonst waere 'guest1' abgelehnt
        # worden bzw. die Runde an der Handoff-Ablehnung abgebrochen.
        assert not any("guest1" in p and "nicht zugestimmt" in p for p in host_printed), host_printed


def test_n1_gegenprobe_geteilter_bildschirm_bleibt_bytegleich():
    """Kein registriertes Gastterminal (klassischer geteilter Bildschirm,
    Status quo, s. `test_a24_local_two_humans_2026_10_01.py` fuer den vollen
    Subprozess-Nachweis): der bestehende `_local_round_handoff`-Weg bleibt
    bytegleich wirksam -- der ZWEITE Mensch bestaetigt ueber DIESELBE
    (geteilte) Eingabequelle wie bisher, `_local_round_handoff` wird real
    aufgerufen (`guest_io is self`-Zweig). `_resolve_member` liest aus
    `self.onboarding_dir` -- fuer den geteilten Bildschirm MUSS der zweite
    Mensch daher (wie im Produkt ueblich) unter DERSELBEN Onboarding-/
    Katalogwurzel wie der Host bekannt sein (kein separates Geraet)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)
        _register_host_figure(onboarding_dir, catalog_dir, run_dir, states_dir, "host1", "CHR-N1B-HOST")
        _register_host_figure(onboarding_dir, catalog_dir, run_dir, states_dir, "human_b", "CHR-N1B-HUMANB")

        # Host selbst + ein ZWEITER Mensch am selben (geteilten) Terminal --
        # bewusst ohne `register_guest_terminal`, derselbe Status-quo-Pfad.
        shared_calls = {"n": 0}

        def shared_input(prompt: str = "") -> str:
            # R4 U3 (01_NACHZUG.md U3 Punkt 3): die jetzt echt bedienbare
            # Abschlusskarte liest nach echtem Abschnittsabschluss eine
            # zusaetzliche Auswahl -- neutral "Zurueck zum Hauptmenue".
            if prompt.startswith("Auswahl (Nummer, leer/zurueck = Hauptmenue)"):
                return ""
            shared_calls["n"] += 1
            if "[j/n]" in prompt:
                return "j"
            return f"geteilt-Zug {shared_calls['n']}."

        printed: list[str] = []
        fake_gm = _FakeTableGm(_debrief_text({
            "CHR-N1B-HOST": full_v7_save("CHR-N1B-HOST", name="host1", save_id="fixture-host1-n1b-002"),
            "CHR-N1B-HUMANB": full_v7_save("CHR-N1B-HUMANB", name="human_b", save_id="fixture-humanb-n1b-002"),
        }), non_completion_rounds=2)

        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="host1",
            input_fn=shared_input, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: fake_gm,
            host_capable=True,
        )
        section_id = session._cmd_local_round(["human_b"], guided=False)
        assert section_id is not None, printed
        table = core_store.Table.load(run_dir, section_id)
        assert table.status == "closed", table.status
        assert set(table.members) == {"host1", "human_b"}, table.members
        # Beide Prompttypen (Terminaluebergabe + Spielzuege) liefen
        # tatsaechlich ueber dieselbe (geteilte) Eingabequelle -- mehr als
        # nur der [j/n]-Consent wurde konsumiert.
        assert shared_calls["n"] > 0, "geteilte Eingabequelle haette fuer Spielzuege genutzt werden muessen."


# ---------------------------------------------------------------------------
# N2 -- Oeffentlicher SL-Verlauf pro Ausgabekanal
# ---------------------------------------------------------------------------

def test_n2_oeffentlicher_sl_verlauf_pro_kanal_beide_gastkanaele_vollstaendig():
    """Leader (Host, geteilter Bildschirm) + ein registrierter Gast. Beweist,
    dass der Gast die Antwort auf SEINEN EIGENEN ersten Beitrag ('SL-Antwort
    #2') auf seinem eigenen Terminal sieht -- unter dem alten EINEN
    geteilten Zaehler haette der LEADER diesen Eintrag beim Anzeigen seines
    EIGENEN naechsten Zugs 'verbraucht', bevor der Gast ihn je zu sehen
    bekommen haette."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        host_onboarding, host_catalog = d / "host_onboarding", d / "host_catalog"
        guest_onboarding, guest_catalog = d / "guest_onboarding", d / "guest_catalog"
        write_test_profile(run_dir, max_turns=200)
        _register_host_figure(host_onboarding, host_catalog, run_dir, states_dir, "host2", "CHR-N2-HOST")
        _register_private_figure(guest_onboarding, guest_catalog, "guest2", "CHR-N2-GUEST")

        host_in = _DivergingInput("host", jn_answer="j")
        guest_in = _DivergingInput("guest", jn_answer="j")
        host_printed: list[str] = []
        guest_printed: list[str] = []

        debrief_host = full_v7_save("CHR-N2-HOST", name="host2", save_id="fixture-host2-n2-002", level=1)
        debrief_guest = full_v7_save("CHR-N2-GUEST", name="guest2", save_id="fixture-guest2-n2-002", level=1)
        # 3 Zwischenantworten (#1,#2,#3) vor dem Debrief -- genug Raum fuer
        # Leader-Turn1 -> Gast-Erstbeitrag -> Leader-Turn2 -> Gast-Folgezug,
        # damit der Gast bei SEINEM zweiten Aufruf auf #2 UND #3 trifft.
        fake_gm = _FakeTableGm(
            _debrief_text({"CHR-N2-HOST": debrief_host, "CHR-N2-GUEST": debrief_guest}),
            non_completion_rounds=3,
        )

        host_session = TuiSession(
            onboarding_dir=host_onboarding, catalog_dir=host_catalog, participant_id="host2",
            input_fn=host_in, print_fn=host_printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: fake_gm, host_capable=True,
        )
        guest_session = TuiSession(
            onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id="guest2",
            input_fn=guest_in, print_fn=guest_printed.append,
            run_dir=run_dir, host_capable=False,
        )

        host_session._cmd_table_offer(["tblN2"])
        guest_session._cmd_table_request_join(["tblN2"])
        host_session._cmd_table_accept(["tblN2", "guest2"])
        host_session.register_guest_terminal("guest2", guest_session)

        host_session._cmd_table_start(["tblN2"])

        record = table_admission.load_record(run_dir, "tblN2")
        section = core_store.Table.load(run_dir, record["section_id"])
        assert section.status == "closed", f"Abschnitt haette abgeschlossen sein sollen: {section.status}"

        # Die ECHTE Kern-Assertion: der Gast hat die Antwort auf seinen
        # EIGENEN ersten Beitrag ("SL-Antwort #2") auf seinem EIGENEN
        # Terminal gesehen -- nicht nur der Leader.
        assert any("[SL] SL-Antwort #2" in p for p in guest_printed), (
            f"Gast haette die Antwort auf seinen eigenen ersten Beitrag sehen muessen: {guest_printed}"
        )
        # Keine Dopplung am geteilten Bildschirm (Leader-Seite): jeder
        # Eintrag erscheint bei EINEM gemeinsamen Cursor hoechstens einmal
        # pro distinktem [SL]-Text.
        for marker in ("#1", "#2", "#3"):
            text = f"[SL] SL-Antwort {marker}"
            count = sum(1 for p in host_printed if p == text)
            assert count <= 1, f"'{text}' erschien mehrfach am geteilten Host-Bildschirm: {host_printed}"


# ---------------------------------------------------------------------------
# N3 -- Wahrer Stop-/Endstatus (Code-Teil)
# ---------------------------------------------------------------------------

def test_n3_bestaetigter_verwurf_am_run_dispatch_nicht_als_eof_gemeldet():
    """Betreiber-Tisch (Persona-Leader via `lead:persona:`) + ein
    registrierter menschlicher Gast, der am eigenen Spielzug-Prompt
    '/abbrechen' eingibt -> echter, bestaetigter Verwurf (`decided ==
    'stopped'`). Treiber: der ECHTE `run()`-Dispatcher (trifft den obersten
    Fangpunkt, der vorher IMMER 'Eingabe beendet (EOF) ... sicher pausiert'
    druckte) -- NICHT `_cmd_local_round` direkt."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        host_onboarding, host_catalog = d / "host_onboarding", d / "host_catalog"
        guest_onboarding, guest_catalog = d / "guest_onboarding", d / "guest_catalog"
        write_test_profile(run_dir, max_turns=200)

        operator_id = "betreiber_n3"
        persona_key = "gm_n3_sentinel"
        persona_char_id = "CHR-N3-SENTINEL"
        bootstrap_own_persona(run_dir, states_dir, operator_id, persona_key)
        register_own_figure(
            host_onboarding, host_catalog, persona_key, persona_char_id, run_dir=run_dir, states_dir=states_dir,
        )
        # N3 testet NUR den Spielzug-Abbrechen-Pfad, nicht die Admissions-
        # Uebernahme: das direkte 'l operator ...'-Tokenweg ruft
        # `_resolve_member('guest3')` auf der HOST-Session auf, die aus
        # `self.onboarding_dir` liest -- 'guest3' muss also (wie jede
        # Persona) unter der HOST-eigenen Wurzel bekannt sein. Die
        # eigenstaendige `guest_session` (separate Wurzel, s. unten) dient
        # danach ausschliesslich dem `register_guest_terminal`-Ein-/
        # Ausgaberouting, nicht der Figurauflösung.
        _register_host_figure(host_onboarding, host_catalog, run_dir, states_dir, "guest3", "CHR-N3-GUEST")

        leader_driver = AcceptLeadDriver(persona_key, play_replies=["Die Wache beobachtet den Sektor."])
        guest_in = _DivergingInput("guest3", jn_answer="j")
        # Der Gast gibt NACH dem Beitritt genau EINMAL '/abbrechen' am
        # eigenen Spielzug-Prompt ein.
        turn_script = iter(["/abbrechen"])

        def guest_input(prompt: str = "") -> str:
            if "[j/n]" in prompt:
                return "j"
            try:
                return next(turn_script)
            except StopIteration:
                return "/pause"

        host_printed: list[str] = []
        guest_printed: list[str] = []

        # `run()` treibt den ECHTEN Dispatcher -- EINE Auswahlzeile:
        # 'l operator lead:persona:<pk> guest3'. `run()` kehrt bereits beim
        # `EndOfInput`-Fang (bestaetigter Verwurf) zurueck -- es wird KEINE
        # zweite Zeile mehr konsumiert.
        host_lines = iter([f"l operator lead:persona:{persona_key} guest3"])

        def host_input(prompt: str = "") -> str:
            try:
                return next(host_lines)
            except StopIteration:
                raise EOFError

        host_session = TuiSession(
            onboarding_dir=host_onboarding, catalog_dir=host_catalog, participant_id=operator_id,
            input_fn=host_input, print_fn=host_printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: _FakeTableGm("nie erreicht", non_completion_rounds=99),
            persona_driver_factory=lambda pk: leader_driver,
            host_capable=True,
        )
        guest_session = TuiSession(
            onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id="guest3",
            input_fn=guest_input, print_fn=guest_printed.append,
            run_dir=run_dir, host_capable=False,
        )
        host_session.register_guest_terminal("guest3", guest_session)
        # Betreiber-Kontrollthread braucht eine ERKENNBAR ANDERE Quelle als
        # das geteilte Terminal (hier gibt es ohnehin keinen geteilten
        # Terminal-Menschen -- 'guest3' ist registriert) -- idle Quelle, da
        # dieser Test NICHT den separaten '/stop'-Kontrollthread, sondern
        # das '/abbrechen' am Spielzug-Prompt selbst belegt.
        import threading

        def idle_source(stop_event: threading.Event):
            stop_event.wait(5.0)
            return None
        host_session.operator_control_line_source = idle_source

        rc = host_session.run()

        assert rc == 0, rc
        # Die bereits bestehende, akkurate Meldung (Guest-Terminal, s.
        # `_HumanDriver.decide()`s '/abbrechen'-Zweig) bleibt unveraendert.
        assert any("Abschnitt wirklich verworfen" in p for p in guest_printed), guest_printed
        # NEU (N3-Fix): der oberste Fangpunkt in `run()` druckt die
        # zutreffende Verwurf-Meldung -- NICHT mehr die pauschale
        # EOF-/Pause-Meldung fuer diesen Lauf.
        assert any("bestaetigter Verwurf" in p for p in host_printed), host_printed
        assert not any("sicher pausiert" in p for p in host_printed), (
            f"Ein bestaetigter Verwurf darf am obersten Fangpunkt NICHT mehr als "
            f"'sicher pausiert' (EOF/Pause) gemeldet werden: {host_printed}"
        )

        from mmo_sim.core import admission as core_admission
        record = table_admission.load_record(run_dir, f"local-{persona_key}-guest3")
        assert record["state"] == table_admission.STATE_CLOSED, record
        decision = core_admission.read_table_decision(run_dir, record["section_id"])
        assert decision is not None and decision.get("decision") == "stopped", decision


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
