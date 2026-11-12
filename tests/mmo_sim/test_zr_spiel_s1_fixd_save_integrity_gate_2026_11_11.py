#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_spiel_s1_fixd_save_integrity_gate_2026_11_11.py —
ZR-SPIEL-S1 Fix D (LINUS-SPEC-FIXD.md, Flo-Entscheidung HART/Option A):
Save-Integritaets-Gate im menschlichen Leader-Eingabepfad (`ui/tui.py:
TuiSession._run_table_round`s innere Klasse `_HumanDriver.decide`).

Belegte Ursache: der live gehostete GM zeigt am Abschnittsende/HQ ein
In-Fiction-Menue mit `!save` als NUMMERIERTER Option. Tippt der Spieler die
Zahl statt woertlich `!save`, erzaehlt der GM einen Deepsave und gibt den
v7-Save-Block aus -- aber `completion_hit` ist False (kein echtes `!save`-
Kommando), die App uebernimmt den Block NICHT, der Abschnitt bleibt offen,
die Runde laeuft mit normalen Zuegen weiter. Der Spieler glaubt gespeichert
zu haben; strukturell ist nichts persistiert.

Fix: sobald im LAUFENDEN, noch nicht geschlossenen Abschnitt bereits ein an
einen AKTUELLEN Tisch-Chrononauten bindbarer v7-Save GEZEIGT wurde (per-Run-
Flag aus den in DIESEM Lauf neu eintreffenden GM-Antworten, NICHT aus
historischem `sl_log`), weist `_HumanDriver.decide` jede normale Folgeaktion
des menschlichen Leaders ab und fragt dieselbe Prompt-Zeile erneut ab -- nur
ein echtes `!save`/`!speichern` oder eine Meta-Steuerzeile kommt vorbei.

Testet am ECHTEN Verzweigungsort: ein Fake-GM-Transport (`gm_transport_
factory`) am Produktionspfad `_cmd_local_round`/`_cmd_menu_fortsetzen` ->
`_run_table_round` -> `_HumanDriver.decide` (derselbe Call-Pfad wie
`test_ux1_control_contract.py`/`test_ux1_g03_same_authority_resume_2026_10_
05.py`), KEIN isolierter Nachbau der Gate-Logik. Kein Netzwerk-/echter
Modellaufruf -- die Fakes liefern synthetischen, gegen beide v7-Schemas
gueltigen Text (`full_v7_save`).

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs."""
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
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _full_v7_fixture import full_v7_save, upgrade_narrow_save  # noqa: E402

from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
_FIX = _REPO_ROOT / "internal" / "qa" / "harness" / "lobby" / "fixtures" / "saves"

_CHAR_ID = "CHR-SNIPER-001"
_GATE_CORE_LINE = "der Stand wurde noch NICHT uebernommen"


def _queued_input(values: list[str]):
    q = list(values)

    def _fn(prompt: str = "") -> str:
        if not q:
            raise EOFError()
        return q.pop(0)
    return _fn


def _save_block_text(save_id: str, level: int = 2) -> str:
    """Ein synthetischer, gegen BEIDE v7-Schemas gueltiger Save-Block
    (`full_v7_save`) fuer GENAU den Chrononauten, den der Leader spielt --
    dieselbe `char_id`-Bindung, die `domain.zeitriss.saves.
    harvest_from_debrief`/`table.chrononaut_id_to_persona()` am echten
    Verzweigungsort auswerten (LINUS-SPEC-FIXD.md PFLICHT-Praezision 3)."""
    block = full_v7_save(_CHAR_ID, name="Yael", callsign="SNIPER", level=level, save_id=save_id)
    return "```json\n" + json.dumps(block, ensure_ascii=False) + "\n```"


def _group_closing_text(leader_save_id: str, guest_save_id: str, leader_level: int = 3) -> str:
    """R1+R2-Nachzug (02_ENGER_NACHZUG.md R2): ein echter Gruppenabschluss
    (mehr als ein Tischmitglied) braucht bindbare eigene v7-Saves fuer
    JEDES Mitglied im Debrief, sonst fordert `core/save_correction.py`
    einen zusaetzlichen, hier nicht gewollten Korrekturzug fuer die
    fehlende Figur an -- derselbe Mehrfiguren-Debrief-Aufbau wie
    `test_linus_n123_2026_11_06.py:_debrief_text`."""
    leader_block = full_v7_save(_CHAR_ID, name="Yael", callsign="SNIPER", level=leader_level, save_id=leader_save_id)
    guest_block = full_v7_save("CHR-TECH-001", name="Kaede", callsign="TECH", save_id=guest_save_id)
    parts = ["Abschnitt beendet."]
    for blk in (leader_block, guest_block):
        parts.append("```json\n" + json.dumps(blk, ensure_ascii=False) + "\n```")
    return "\n".join(parts)


class _ScriptedTableGm:
    """Gescriptetes GM-Fake am echten Transport-Verzweigungsort (`gm.
    turn(idx, text)` -> `{"content": ...}`, wie `_TechDriver`/`_OpenTableGM`
    in `test_ux1_g03_same_authority_resume_2026_10_05.py`). Wirft, wenn MEHR
    Zuege ankommen als gescriptet -- das ist der direkte Doppelcall-/
    Fehlfire-Beleg: ein abgewiesener Gate-Versuch darf NIEMALS einen
    GM-/Modellaufruf verbrauchen (LINUS-SPEC-FIXD.md Soll-Verhalten)."""

    def __init__(self, contents: list[str]):
        self._contents = list(contents)
        self.calls: list[str] = []

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append(text)
        if not self._contents:
            raise AssertionError(
                f"_ScriptedTableGm: unerwarteter {len(self.calls)}. GM-Call (Skript erschoepft) "
                f"mit text={text!r} -- ein abgewiesener Gate-Versuch darf KEINEN GM-Call ausloesen."
            )
        content = self._contents.pop(0)
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "table"}


def _env(root: Path):
    states_dir, run_dir = root / "states", root / "run"
    onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
    states_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    return states_dir, run_dir, onboarding_dir, catalog_dir


def _make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, persona_key: str) -> dict:
    """Stellt eine real erschaffene/publizierte Figur bereit, ohne den
    Erschaffungsdialog durchzuspielen -- derselbe Helfer-Zweck wie
    `test_ux1_g03_same_authority_resume_2026_10_05.py:_make_ready` (Reuse,
    hier inline, um keinen Cross-Test-Importpfad fuer EINE Hilfsfunktion
    aufzuspannen)."""
    save = upgrade_narrow_save(json.loads((_FIX / f"{persona_key}.json").read_text(encoding="utf-8")))
    ps_store = PersonaStateStore(schema_path=_SCHEMA)
    chrono_id = save["characters"][0]["id"]
    onboarding.start_or_resume(onboarding_dir, persona_key)
    onboarding.complete_with_save(onboarding_dir, persona_key, save, ZeitrissHarvestValidator(), chrono_id)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, persona_key, chrono_id, save)
    core_store.publish_current_save(run_dir, persona_key, save, ps_store, states_dir)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=persona_key, chrononaut_id=chrono_id, persona_key=persona_key,
    ))
    catalog.bind_for_section(catalog_dir, persona_key, chrono_id, has_open_section=False)
    return save


def _assert_calls(calls: list[str], expected_texts: list[str]) -> None:
    """Vergleicht `gm.calls` gegen die rohen Leader-Eingaben, TOLERANT
    gegenueber dem bestehenden, fixbunabhaengigen Anker-Mechanismus (D3/A7,
    `_HumanDriver.__init__`-Docstring): der ERSTE Zug eines frischen
    `_HumanDriver` (`self._turn == 1` nach Inkrement) haengt den aktuell
    publizierten Save des Leaders als `save_payload` an, der GM-Transport
    bettet ihn dem ausgehenden Text als zusaetzlichen JSON-Block an -- das
    ist bestehendes, von Fix D UNBERUEHRTES Verhalten (`core/runtime.py`s
    Wire-Einbettung), kein Teil der hier getesteten Gate-Logik. Geprueft
    wird daher per `startswith` auf die rohe Eingabe, NICHT auf exakte
    Gleichheit."""
    assert len(calls) == len(expected_texts), (calls, expected_texts)
    for actual, expected in zip(calls, expected_texts):
        assert actual == expected or actual.startswith(expected + "\n"), (actual, expected)


def _solo_session(root: Path, participant_id: str, input_fn, printed: list, gm) -> TuiSession:
    states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
    return TuiSession(
        onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=participant_id,
        input_fn=input_fn, print_fn=printed.append,
        run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
        gm_transport_factory=lambda *_a, **_kw: gm,
    )


def test_a_bindable_save_shown_gates_next_normal_action_no_further_gm_call():
    """(a) GM-Antwort mit bindbarem v7-Save-Block auf eine NORMALE Aktion
    -> die naechste normale Aktion wird abgewiesen, die Kernzeile erscheint,
    KEIN weiterer GM-Zug (das gescriptete Fake wirft sonst selbst)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
        write_test_profile(run_dir)
        _make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, "sniper")

        gm = _ScriptedTableGm([_save_block_text("fixture-a-001")])
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="sniper",
            input_fn=_queued_input([
                "Ich beobachte den Raum.",
                "Ich gehe einfach weiter (sollte abgelehnt werden).",
            ]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda *_a, **_kw: gm,
        )
        try:
            session._cmd_local_round()
        except EndOfInput:
            pass  # Eingabequeue am Gate erschoepft -- erwartet (kein Absturz).

        _assert_calls(gm.calls, ["Ich beobachte den Raum."])
        assert any(_GATE_CORE_LINE in p for p in printed), printed
        assert any("!save" in p and "!speichern" in p for p in printed), printed
        assert not any("Abschnitt abgeschlossen" in p for p in printed), printed


def test_b_real_save_command_at_the_gate_passes_through_to_completion():
    """(b) am Gate `!save` -> laeuft durch (completion/Ingest-Pfad erreicht).
    Ablauf: normale Aktion zeigt den unsavten Save (Gate aktiv) -> eine
    weitere normale Aktion wird ABGEWIESEN (echt 'am Gate') -> `!save`
    kommt vorbei und loest den echten zweiten GM-Call + Abschluss aus."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
        write_test_profile(run_dir)
        _make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, "sniper")

        gm = _ScriptedTableGm([
            _save_block_text("fixture-b-001"),
            _save_block_text("fixture-b-002", level=3),
        ])
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="sniper",
            input_fn=_queued_input([
                "Ich beobachte den Raum.",
                "Ich gehe einfach weiter (sollte abgelehnt werden).",
                "!save",
                "",  # Pflicht-Abschlussnotiz des Leaders -- leer = ueberspringen.
            ]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda *_a, **_kw: gm,
        )
        try:
            session._cmd_local_round()
        except EndOfInput:
            pass  # nach Abschluss endet die Runde regulaer (naechster Abschnitt waere neu).

        _assert_calls(gm.calls, ["Ich beobachte den Raum.", "!save"])
        assert any(_GATE_CORE_LINE in p for p in printed), (
            "die abgewiesene Zwischenaktion muss die Gate-Kernzeile gezeigt haben", printed
        )
        assert any("Abschnitt abgeschlossen" in p for p in printed), printed


def test_c_gm_response_without_save_block_does_not_gate_next_action():
    """(c) GM-Antwort OHNE Save-Block -> die normale Folgeaktion laeuft
    NORMAL durch (kein Gate, echter zweiter GM-Call)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
        write_test_profile(run_dir)
        _make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, "sniper")

        gm = _ScriptedTableGm([
            "Nichts Besonderes passiert, die Szene laeuft weiter.",
            "Ihr setzt eure Erkundung fort.",
        ])
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="sniper",
            input_fn=_queued_input([
                "Ich beobachte den Raum.",
                "Ich gehe einfach weiter.",
            ]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda *_a, **_kw: gm,
        )
        try:
            session._cmd_local_round()
        except EndOfInput:
            pass  # Eingabequeue nach dem zweiten echten Zug erschoepft -- erwartet.

        _assert_calls(gm.calls, ["Ich beobachte den Raum.", "Ich gehe einfach weiter."])
        assert not any(_GATE_CORE_LINE in p for p in printed), printed


def test_d_regression_open_section_resume_still_gates_first_action():
    """(d) KORRIGIERT (02_ENGER_NACHZUG.md R1, LINUS-SPEC-N1.md): der
    FRUEHERE Test d baute hier einen UNGESICHERTEN Save auf (`status !=
    closed`, kein `!save`) und forderte faelschlich, dass die normale
    Folgeaktion NACH Resume durchlaeuft -- das war der Fehlfire selbst
    (Flos berechtigte Sorge betraf bereits GESPEICHERTE/geschlossene
    Vorgeschichte, nicht einen weiterhin offenen, unerledigten Abschnitt).
    Section-autoritativ heisst: ein offener Abschnitt mit einem NOCH NICHT
    uebernommenen Eigen-Save bleibt auch nach Prozessneustart/Resume
    gegattet -- unabhaengig davon, ob der Save-Block "historisch" (vor
    diesem Prozess) oder "neu" (in diesem Prozess) gezeigt wurde.

    Prozess 1 (echter `_cmd_local_round`-Lauf): eine normale Aktion zeigt
    einen unsavten bindbaren Save, dann pausiert die Eingabequeue (kein
    `!save`) -- der Tisch bleibt offen, `sl_log` traegt genau diesen
    Save-Eintrag, `current_save` bleibt der urspruengliche Fixture-Stand
    (NICHT der gezeigte Block).
    Prozess 2 (NEUE `TuiSession`, DIESELBEN Verzeichnisse, `_cmd_menu_
    fortsetzen` -> `_resume_bound_table` -> frischer `_run_table_round`-
    Aufruf): die ERSTE Aktion nach dem Resume wird WEITERHIN abgewiesen
    (section-autoritativ gegen den persistierten `current_save` geprueft,
    NICHT gegen eine Pro-Lauf-Baseline) -- kein weiterer GM-Call fuer den
    abgewiesenen Versuch; erst `!save` schliesst danach wirklich ab."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
        write_test_profile(run_dir)
        _make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, "sniper")

        gm1 = _ScriptedTableGm([_save_block_text("fixture-d-001")])
        printed1: list[str] = []
        session1 = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="sniper",
            input_fn=_queued_input(["Ich beobachte den Raum."]),
            print_fn=printed1.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda *_a, **_kw: gm1,
        )
        try:
            session1._cmd_local_round()
        except EndOfInput:
            pass  # kontrollierte Pause (Eingabequeue erschoepft) -- Abschnitt bleibt offen.

        tables_before = list((run_dir / "tables").glob("*.json"))
        assert len(tables_before) == 1, tables_before
        table_before = json.loads(tables_before[0].read_text(encoding="utf-8"))
        assert table_before["status"] != "closed", table_before
        assert len(table_before["sl_log"]) == 1, table_before["sl_log"]

        # Prozess 2: NEUE TuiSession (frische Closures in
        # `_run_table_round`), DIESELBEN Verzeichnisse -- derselbe
        # Resume-Pfad wie `test_ux1_g03_same_authority_resume_2026_10_05.py`.
        # Der erste Zug wird ABGEWIESEN (kein GM-Call); erst '!save' kommt
        # durch und schliesst den Abschnitt wirklich ab.
        gm2 = _ScriptedTableGm([_save_block_text("fixture-d-002", level=3)])
        printed2: list[str] = []
        session2 = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="sniper",
            input_fn=_queued_input([
                "Normale Folgeaktion, erste nach dem Resume (sollte abgewiesen werden).",
                "!save",
                "",  # Pflicht-Abschlussnotiz des Leaders -- leer = ueberspringen.
            ]),
            print_fn=printed2.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda *_a, **_kw: gm2,
        )
        try:
            session2._cmd_menu_fortsetzen()
        except EndOfInput:
            pass  # nach Abschluss endet die Runde regulaer.

        _assert_calls(gm2.calls, ["!save"])
        assert any(_GATE_CORE_LINE in p for p in printed2), (
            "Regression (Fehlfire): die erste Aktion nach Resume haette weiterhin "
            f"gegattet werden muessen (offener, un-ingesteter Eigen-Save): {printed2}"
        )
        assert any("Abschnitt abgeschlossen" in p for p in printed2), printed2


def test_d2_real_save_then_new_section_with_old_save_recap_does_not_gate():
    """(d2) POSITIVFALL (02_ENGER_NACHZUG.md R1, "wirklich abgeschlossener
    Vorgang und danach neuer Abschnitt/Save-Load mit erneut sichtbarem
    altem Save bleiben normal spielbar"): ersetzt NICHT den offenen Fall
    oben, deckt die Gegenseite ab.

    Prozess 1: normale Aktion zeigt einen Save, `!save` uebernimmt ihn
    WIRKLICH (`current_save.save_id` wird dieser Block) -- der Tisch wird
    geschlossen.
    Prozess 2: EIN NEUER Abschnitt (fresh `_cmd_local_round()`, da der
    vorige Tisch geschlossen ist, erzeugt `create_table_from_offer_log`
    automatisch eine neue Generation) -- der SL rekapituliert dabei
    denselben, bereits uebernommenen Save-Block erneut (gleiche `save_id`
    wie der aktuelle `current_save`) -- die ZWEITE normale Aktion darf NICHT
    gegattet werden (echter zweiter GM-Call, kein abgewiesener Versuch)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
        write_test_profile(run_dir)
        _make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, "sniper")

        gm1 = _ScriptedTableGm([_save_block_text("fixture-d2-closed-001")])
        printed1: list[str] = []
        session1 = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="sniper",
            input_fn=_queued_input(["!save", ""]),
            print_fn=printed1.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda *_a, **_kw: gm1,
        )
        try:
            session1._cmd_local_round()
        except EndOfInput:
            pass  # nach Abschluss endet die Runde regulaer.
        assert any("Abschnitt abgeschlossen" in p for p in printed1), printed1

        # Dieselbe Autoritaet, die auch das Gate selbst zum Ingest-Abgleich
        # liest (`outer._resolve_active_save` -> `core_store.load_current_
        # save_or_raise`) -- NICHT der separate `current_saves/<pk>.json`-
        # "direct"-Pfad aus `publish_current_save` (anderer Schreibweg, hier
        # nicht die massgebliche Leseautoritaet nach einem echten Ingest).
        ps_store = PersonaStateStore(schema_path=_SCHEMA)
        current_after_close = core_store.load_current_save(run_dir, "sniper", ps_store, states_dir=states_dir)
        assert current_after_close is not None and current_after_close.get("save_id") == "fixture-d2-closed-001", (
            current_after_close
        )

        # Prozess 2: NEUER Abschnitt (derselbe Teilnehmer, dieselben
        # Verzeichnisse). Der SL rekapituliert den bereits uebernommenen
        # Save (gleiche save_id) als normale Zwischenantwort -- das darf
        # die ZWEITE normale Aktion NICHT gegattet werden.
        gm2 = _ScriptedTableGm([
            _save_block_text("fixture-d2-closed-001"),
            "Normale Folgeaktion laeuft durch, kein Gate.",
        ])
        printed2: list[str] = []
        session2 = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="sniper",
            input_fn=_queued_input([
                "Ich beginne den neuen Abschnitt (der SL rekapituliert den alten Save).",
                "Normale Folgeaktion, sollte NICHT abgewiesen werden.",
            ]),
            print_fn=printed2.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda *_a, **_kw: gm2,
        )
        try:
            session2._cmd_local_round()
        except EndOfInput:
            pass  # Eingabequeue nach dem zweiten echten Zug erschoepft -- erwartet.

        _assert_calls(gm2.calls, [
            "Ich beginne den neuen Abschnitt (der SL rekapituliert den alten Save).",
            "Normale Folgeaktion, sollte NICHT abgewiesen werden.",
        ])
        assert not any(_GATE_CORE_LINE in p for p in printed2), (
            f"ein bereits uebernommener (save_id-gleicher) rekapitulierter Save darf das Gate "
            f"NICHT erneut armieren: {printed2}"
        )


def test_f_shared_screen_guest_poll_does_not_bypass_leader_gate():
    """(f) R2 (02_ENGER_NACHZUG.md R2, LINUS-SPEC-N1.md): echter gemeinsamer
    Tisch (Leader 'sniper' + Gast 'tech'), GETEILTES Terminal (`io=outer`
    fuer BEIDE -- kein `register_guest_terminal`, derselbe Status-quo-Pfad
    wie `test_n1_gegenprobe_geteilter_bildschirm_bleibt_bytegleich` in
    `test_linus_n123_2026_11_06.py`). Ablauf am ECHTEN Verzweigungsort
    (`_cmd_local_round` -> `_run_table_round` -> `_HumanDriver.decide`):

    1) Leader-Anker, 2) Gast-Import -- beide ohne Save-Anzeige.
    3) Ein spaeterer normaler Leader-Zug erzeugt einen bindbaren
       Leader-Save OHNE Abschluss.
    4) Die Runtime pollt danach den Gast (`poll_guests_and_consolidate`);
       der Gast zeigt dabei die neue SL-Antwort auf SEINEM (geteilten)
       Bildschirm und schiebt den GEMEINSAMEN Anzeige-Cursor vor
       (`displayed_sl_count_by_channel[id(outer)]`).
    5) TROTZDEM wird die naechste normale Leader-Aktion ohne weiteren
       GM-/Zugverbrauch abgewiesen -- die fachliche Erkennung ist jetzt
       section-autoritativ (ganzer `sl_log`/Ingest-Abgleich), NICHT mehr
       vom Anzeige-Cursor abhaengig. Echtes `!save` bleibt danach moeglich."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
        write_test_profile(run_dir)
        _make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, "sniper")
        _make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, "tech")

        gm = _ScriptedTableGm([
            "Leader-Anker: ruhige Szene, kein Save.",
            "Gast-Import: ruhige Szene, kein Save.",
            _save_block_text("fixture-r2-001"),  # Leader-Zug 2: bindbarer Save, KEIN Abschluss.
            # '!save'-Zug: echter Gruppenabschluss -- braucht bindbare Saves
            # fuer BEIDE Mitglieder (sonst Korrekturnachforderung fuer 'tech').
            _group_closing_text("fixture-r2-002", "fixture-r2-tech-001", leader_level=3),
        ])
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="sniper",
            input_fn=_queued_input([
                "j",  # 0) 'tech' bestaetigt den Beitritt zur lokalen Runde (geteiltes Terminal).
                "Ich beobachte den Raum.",  # 1) Leader-Anker.
                "Ich sichere die Flanke.",  # 2) Gast-Import.
                "Ich gehe vorsichtig weiter.",  # 3) Leader-Zug zeigt den unsavten Save.
                "Ich bleibe in Deckung.",  # 4) Gast-Poll -- zeigt die neue Antwort, schiebt den Cursor.
                "Ich mache einfach weiter (sollte abgewiesen werden).",  # 5a) abgewiesen.
                "!save",  # 5b) kommt vorbei, echter Abschluss.
                "",  # Leader-Abschlussnotiz -- leer = ueberspringen.
                "",  # Gast-Abschlussnotiz -- leer = ueberspringen.
            ]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda *_a, **_kw: gm,
        )
        try:
            session._cmd_local_round(["tech"])
        except EndOfInput:
            pass  # nach Abschluss endet die Runde regulaer.

        _assert_calls(gm.calls, [
            "Ich beobachte den Raum.",
            "Ich sichere die Flanke.",
            "Ich gehe vorsichtig weiter.",
            "!save",
        ])
        gate_hits = [i for i, p in enumerate(printed) if _GATE_CORE_LINE in p]
        assert gate_hits, (
            "Regression (R2-Fehlfire): die Leader-Aktion nach dem Gast-Poll haette trotz "
            f"vorgeschobenem gemeinsamen Anzeige-Cursor gegattet werden muessen: {printed}"
        )
        # Beweis, dass der Cursor TATSAECHLICH vorgeschoben wurde (der Gast-
        # Poll hat die Save-tragende SL-Antwort bereits auf dem geteilten
        # Bildschirm angezeigt, BEVOR das Gate trotzdem greift) -- genau
        # drei [SL]-Bloecke VOR der Gate-Zeile (Anker/Import/der unsavte
        # Save), je EINMAL angezeigt (kein Doppel-Print am geteilten
        # Cursor); der Abschluss-Debrief selbst zeigt spaeter einen eigenen
        # vierten Block, NACH dem Gate -- unbetroffen von dieser Pruefung.
        sl_markers_before_gate = [
            i for i, p in enumerate(printed) if p.startswith("[SL] ") and i < min(gate_hits)
        ]
        assert len(sl_markers_before_gate) == 3, printed
        assert any("Abschnitt abgeschlossen" in p for p in printed), printed


def test_a1_same_save_id_different_level_still_gates_regression():
    """(A1) 02_ENGER_NACHZUG.md A1, LINUS-SPEC-N2.md: gleiche `save_id`
    beweist KEINE Inhaltsgleichheit/Uebernahme. Ergaenzt (ersetzt NICHT)
    test_d2 (identischer Recap gleicher save_id+Level bleibt frei) -- hier
    ist der gezeigte Block NICHT identisch (gleiche save_id, Level 2 -> 3).

    Prozess 1: echter `!save`-Abschluss, Current = Level 2, save_id X.
    Prozess 2 (neuer Abschnitt, derselbe Tisch wird wegen `status ==
    closed` automatisch neu generiert, s. test_d2): normale Leader-Antwort
    mit GLEICHER save_id X, aber Level 3 -- die naechste normale Aktion
    haelt lokal (KEIN weiterer GM-Call fuer den abgewiesenen Versuch,
    strikte `_assert_calls`-Laengenpruefung), Current bleibt unveraendert
    Level 2. Kontrolliert pausieren (Eingabequeue erschoepft, wie test_d
    Prozess 1).
    Prozess 3 (neue TuiSession, DIESELBEN Verzeichnisse, `_cmd_menu_
    fortsetzen` -> derselbe Resume-Pfad wie test_d): dieselbe Sperre
    greift weiterhin (section-autoritativ, kein Pro-Lauf-Zustand). Echtes
    `!save` kommt danach vorbei und schliesst wirklich ab."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
        write_test_profile(run_dir)
        _make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, "sniper")

        gm1 = _ScriptedTableGm([_save_block_text("fixture-a1-closed-001", level=2)])
        printed1: list[str] = []
        session1 = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="sniper",
            input_fn=_queued_input(["!save", ""]),
            print_fn=printed1.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda *_a, **_kw: gm1,
        )
        try:
            session1._cmd_local_round()
        except EndOfInput:
            pass  # nach Abschluss endet die Runde regulaer.
        assert any("Abschnitt abgeschlossen" in p for p in printed1), printed1

        ps_store = PersonaStateStore(schema_path=_SCHEMA)
        current_after_close = core_store.load_current_save(run_dir, "sniper", ps_store, states_dir=states_dir)
        assert current_after_close is not None and current_after_close.get("save_id") == "fixture-a1-closed-001", (
            current_after_close
        )
        assert current_after_close["characters"][0].get("lvl") == 2, current_after_close

        # Prozess 2: neuer Abschnitt (derselbe Teilnehmer, dieselben
        # Verzeichnisse). Normale Aktion zeigt GLEICHE save_id wie Current,
        # aber Level 3 -- NOCH NICHT uebernommen. Die naechste normale
        # Aktion muss lokal halten, KEIN zweiter GM-Call.
        gm2 = _ScriptedTableGm([_save_block_text("fixture-a1-closed-001", level=3)])
        printed2: list[str] = []
        session2 = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="sniper",
            input_fn=_queued_input([
                "Normale Aktion, SL zeigt gleiche save_id aber verandertes Level.",
                "Normale Folgeaktion (sollte abgewiesen werden).",
            ]),
            print_fn=printed2.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda *_a, **_kw: gm2,
        )
        try:
            session2._cmd_local_round()
        except EndOfInput:
            pass  # kontrollierte Pause (Eingabequeue erschoepft).

        _assert_calls(gm2.calls, ["Normale Aktion, SL zeigt gleiche save_id aber verandertes Level."])
        assert any(_GATE_CORE_LINE in p for p in printed2), (
            "Regression (A1-Fehlfire): gleiche save_id mit geaendertem Level haette das Gate "
            f"armieren muessen: {printed2}"
        )
        current_still_old = core_store.load_current_save(run_dir, "sniper", ps_store, states_dir=states_dir)
        assert current_still_old == current_after_close, (
            "Current darf durch den nur gezeigten (nicht uebernommenen) Block NICHT veraendert "
            f"worden sein: {current_still_old}"
        )

        tables = list((run_dir / "tables").glob("*.json"))
        assert len(tables) >= 1, tables
        open_tables = [json.loads(p.read_text(encoding="utf-8")) for p in tables]
        open_tables = [t for t in open_tables if t.get("status") != "closed"]
        assert len(open_tables) == 1, open_tables

        # Prozess 3: NEUE TuiSession, derselbe Resume-Pfad wie test_d --
        # die Sperre bleibt section-autoritativ erhalten, KEIN Pro-Lauf-
        # Zustand. Erst echtes `!save` kommt vorbei und schliesst ab.
        gm3 = _ScriptedTableGm([_save_block_text("fixture-a1-reopened-002", level=4)])
        printed3: list[str] = []
        session3 = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="sniper",
            input_fn=_queued_input([
                "Normale Folgeaktion nach Resume (sollte weiterhin abgewiesen werden).",
                "!save",
                "",
            ]),
            print_fn=printed3.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda *_a, **_kw: gm3,
        )
        try:
            session3._cmd_menu_fortsetzen()
        except EndOfInput:
            pass  # nach Abschluss endet die Runde regulaer.

        _assert_calls(gm3.calls, ["!save"])
        assert any(_GATE_CORE_LINE in p for p in printed3), (
            "Regression: dieselbe Sperre haette auch nach Fortsetzen (neue TuiSession) "
            f"weiterhin greifen muessen: {printed3}"
        )
        assert any("Abschnitt abgeschlossen" in p for p in printed3), printed3

        current_after_real_save = core_store.load_current_save(run_dir, "sniper", ps_store, states_dir=states_dir)
        assert current_after_real_save is not None and current_after_real_save.get("save_id") == "fixture-a1-reopened-002", (
            "das echte '!save' muss den Current wirklich auf den neu ernteten Block setzen", current_after_real_save
        )


def test_a2_unadopted_own_block_survives_later_recap_of_old_current():
    """(A2) 02_ENGER_NACHZUG.md A2, LINUS-SPEC-N2.md: ein SPAETERER blosser
    Recap des alten, bereits uebernommenen Current darf einen FRUEHEREN,
    noch nicht uebernommenen Eigenblock NICHT als erledigt behandeln.
    Echter Zweimenschen-Weg (`_cmd_local_round(["tech"])`, geteiltes
    Terminal, wie test_f): Leader-Anker liefert den unuebernommenen
    Eigenblock B; die nachfolgende Gast-Import-Antwort rekapituliert
    EXAKT den alten, bereits uebernommenen Leaderblock A (== Current).
    Die naechste normale Leader-Aktion muss TROTZDEM lokal halten (kein
    normaler GM-Call, Current bleibt A); echtes `!save` bleibt danach
    moeglich und schliesst mit den erforderlichen eigenen Gruppenbloecken
    beider Mitglieder ab."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
        write_test_profile(run_dir)
        save_sniper = _make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, "sniper")
        _make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, "tech")

        ps_store = PersonaStateStore(schema_path=_SCHEMA)
        current_before = core_store.load_current_save(run_dir, "sniper", ps_store, states_dir=states_dir)
        assert current_before == save_sniper, current_before

        a_recap_text = "```json\n" + json.dumps(save_sniper, ensure_ascii=False) + "\n```"
        gm = _ScriptedTableGm([
            _save_block_text("fixture-a2-block-b-001", level=5),  # Leader-Anker: unuebernommener Block B.
            a_recap_text,  # Gast-Import: rekapituliert EXAKT den alten, uebernommenen Current A.
            _group_closing_text("fixture-a2-closing-leader-001", "fixture-a2-closing-tech-001"),  # !save: echter Abschluss.
        ])
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="sniper",
            input_fn=_queued_input([
                "j",  # 0) 'tech' bestaetigt den Beitritt zur lokalen Runde (geteiltes Terminal).
                "Ich beobachte den Raum.",  # 1) Leader-Anker -> zeigt unuebernommenen Block B.
                "Ich sichere die Flanke.",  # 2) Gast-Import -> rekapituliert den alten Current A.
                "Ich mache einfach weiter (sollte abgewiesen werden).",  # 3a) abgewiesen -- B war nie uebernommen.
                "!save",  # 3b) kommt vorbei, echter Gruppenabschluss.
                "",  # Leader-Abschlussnotiz -- leer = ueberspringen.
                "",  # Gast-Abschlussnotiz -- leer = ueberspringen.
            ]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda *_a, **_kw: gm,
        )
        try:
            session._cmd_local_round(["tech"])
        except EndOfInput:
            pass  # nach Abschluss endet die Runde regulaer.

        _assert_calls(gm.calls, [
            "Ich beobachte den Raum.",
            "Ich sichere die Flanke.",
            "!save",
        ])
        assert any(_GATE_CORE_LINE in p for p in printed), (
            "Regression (A2-Fehlfire): der spaetere Recap des alten Current A haette den "
            f"frueheren unuebernommenen Eigenblock B NICHT verdraengen duerfen: {printed}"
        )
        assert any("Abschnitt abgeschlossen" in p for p in printed), printed

        current_after = core_store.load_current_save(run_dir, "sniper", ps_store, states_dir=states_dir)
        assert current_after is not None and current_after.get("save_id") == "fixture-a2-closing-leader-001", (
            "das echte '!save' muss den Current wirklich auf den neu ernteten Gruppenabschluss setzen",
            current_after,
        )


def test_e_meta_control_line_at_the_gate_is_handled_unchanged_no_gate_error():
    """(e) Meta-Steuerzeile (`/pause`) am Gate -> unveraendert behandelt
    (kontrollierte Pause, bestehende `EndOfInput`-Mechanik), kein Gate-
    Fehler/keine Gate-Kernzeile fuer die Steuerzeile selbst."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
        write_test_profile(run_dir)
        _make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, "sniper")

        gm = _ScriptedTableGm([_save_block_text("fixture-e-001")])
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="sniper",
            input_fn=_queued_input([
                "Ich beobachte den Raum.",
                "/pause",
            ]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda *_a, **_kw: gm,
        )
        try:
            session._cmd_local_round()
        except EndOfInput:
            pass  # '/pause' endet den Lauf kontrolliert -- erwartet.

        _assert_calls(gm.calls, ["Ich beobachte den Raum."])
        assert any("Kontrolliert pausiert" in p for p in printed), printed
        assert not any(_GATE_CORE_LINE in p for p in printed), printed


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
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
