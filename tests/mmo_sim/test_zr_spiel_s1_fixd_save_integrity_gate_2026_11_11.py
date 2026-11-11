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


def test_d_regression_pre_existing_resume_save_block_does_not_gate_first_action():
    """(d) REGRESSION (Flos ausdrueckliche Sorge, LINUS-SPEC-FIXD.md PFLICHT-
    Praezision 1): ein zu BEGINN eines Laufs bereits im `sl_log` vorhandener
    (resume-/vorsektions-) Save-Block, der NICHT in DIESEM Lauf neu vom GM
    kam, gatet NICHT die erste Aktion.

    Prozess 1 (echter `_cmd_local_round`-Lauf): eine normale Aktion zeigt
    einen unsavten bindbaren Save, dann pausiert die Eingabequeue (kein
    `!save`) -- der Tisch bleibt offen, `sl_log` traegt genau diesen
    Save-Eintrag.
    Prozess 2 (NEUE `TuiSession`, DIESELBEN Verzeichnisse, `_cmd_menu_
    fortsetzen` -> `_resume_bound_table` -> frischer `_run_table_round`-
    Aufruf mit frischem Per-Run-Flag/Baseline): die ERSTE Aktion nach dem
    Resume ist eine normale Aktion -- sie darf NICHT gegattet werden, denn
    der bereits vorhandene Save-Eintrag kam NICHT waehrend DIESES Laufs neu
    vom GM (er wird beim Resume nur erneut angezeigt/RE-GEPOSTET)."""
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

        # Prozess 2: NEUE TuiSession (frische Closures/Baseline in
        # `_run_table_round`), DIESELBEN Verzeichnisse -- derselbe
        # Resume-Pfad wie `test_ux1_g03_same_authority_resume_2026_10_05.py`.
        gm2 = _ScriptedTableGm(["Ruhige Reaktion, keine neue Save-Anzeige."])
        printed2: list[str] = []
        session2 = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="sniper",
            input_fn=_queued_input(["Normale Folgeaktion, erste nach dem Resume."]),
            print_fn=printed2.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda *_a, **_kw: gm2,
        )
        try:
            session2._cmd_menu_fortsetzen()
        except EndOfInput:
            pass  # Eingabequeue nach dem echten Folgezug erschoepft -- erwartet.

        try:
            _assert_calls(gm2.calls, ["Normale Folgeaktion, erste nach dem Resume."])
        except AssertionError as e:
            raise AssertionError(
                f"Regression (Fehlfire): die erste Aktion nach Resume wurde gegattet, obwohl der "
                f"vorhandene Save-Block NICHT in diesem Lauf neu vom GM kam: {e}"
            )
        assert not any(_GATE_CORE_LINE in p for p in printed2), printed2

        table_after = json.loads(tables_before[0].read_text(encoding="utf-8"))
        assert len(table_after["sl_log"]) == 2, table_after["sl_log"]


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
