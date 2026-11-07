#!/usr/bin/env python3
"""
tests/mmo_sim/test_r4_u5_zweigast_figurfrei_strukturell_2026_11_07.py --
ZR-VOLLENDUNG-OHNE-LAN-NACHZUG-20261107-R4 (U5, 01_NACHZUG.md U5 + der
U2-"Fertig,wenn"-Normalweg). Analog zum Muster von `test_r4_u2_gast_
erschaffung_menu_2026_11_07.py` (in-process, echte `TuiSession`-Objekte,
EIN kontrollierter Fake-GM-Call am vorhandenen Modellrand -- hier VIER,
weil GENAU vier reale GM-Rufe auf diesem Normalweg anfallen, s. `drive_u5_
zweigast_figurfrei_2026_11_07.py`-Modul-Docstring), damit CI den figurfreien
Zweigast-Weg STRUKTURELL gruen haelt, OHNE den teuren echten Subprozess-/
Helferprozess-Beleg zu wiederholen.

Prueft am echten `TuiSession`/`core.runtime.run_full_section`-Dispatch
(`register_guest_terminal`-Verdrahtung, bytegleich zum echten
`scripts/mmo_sim.py`, nur ohne eigene Betriebssystem-Threads/FIFOs -- der
synchrone In-Process-Aufruf ersetzt NUR den Transportweg, nicht die
Produktlogik):

1. Figurfreier Betreiber wird NICHT Leader -- der erste angenommene Gast
   (`guest_tokens[0]`, s. `ui/tui.py:_cmd_table_start`) wird spielender
   Leader.
2. Der echte Import-[charaktere]->[2]-Weg (`_cmd_menu_charaktere`/
   `_cmd_import`) erzeugt eine echte, registrierte Figur.
3. Beide persoenlichen Abschlusskarten dispatchen real (Export-Handler
   lief -- echte Exportdatei auf Platte) UND zeigen das NEUE Label
   "Zurueck zum Hauptmenue" woertlich.

Zusaetzlich (negative Assertion, R4 U5 Briefing): eine ungueltige
Kartennummer loest KEINE fremde Aktion aus, und ein Markertext INNERHALB
eines zitierten Fence-Blocks (`core.completion_marker.completion_marker_
matches`) gilt NICHT als echter Abschluss (Top-Level-Marker-Grammatik).

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs.
Null echte GM-/Persona-Modellcalls."""
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

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.completion_marker import completion_marker_matches  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"

BETREIBER_ID = "betreiber_u5_struct"
GAST_A_ID = "gast_a_u5_struct"
GAST_B_ID = "gast_b_u5_struct"
CHAR_A = "chrono-u5-struct-gast-a"
CHAR_B = "chrono-u5-struct-gast-b"
TABLE_KEY = "mesaU5structZweigast"
TABLE_ID = f"local-{GAST_A_ID}-{GAST_B_ID}"


class _ScriptedGm:
    """Liefert vorgegebene Antworten der Reihe nach -- derselbe
    Musteraufbau wie `tests/mmo_sim/_r4_gm_double.py`s `_R4GmDoubleTransport`,
    hier ohne Datei-/Env-Umweg (reines In-Process-Double)."""

    def __init__(self, responses: list[str]):
        self._responses = list(responses)
        self.calls = 0

    def turn(self, turn_idx: int, user_text: str, **kw) -> dict:
        self.calls += 1
        content = self._responses.pop(0) if self._responses else ""
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": f"u5struct-{self.calls}"}


def _scripted_input(values):
    q = list(values)

    def input_fn(prompt: str = "") -> str:
        if q:
            return q.pop(0)
        raise EOFError()

    return input_fn


def test_figurfreier_betreiber_zweigast_normalweg_strukturell():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        write_test_profile(run_dir, max_turns=200)

        # ── Zwei getrennte GM-Transport-Instanzen aus EINER Factory, exakt
        # wie der echte Produktweg (`_cmd_gast_erschaffung_dialog`s
        # `authority.gm_transport_factory(onboarding_chat_id)` UND
        # `_run_table_round`s `self.gm_transport_factory(table.table_id)`
        # sind ZWEI getrennte Aufrufe) -- der ERSTE liefert GENAU den einen
        # Erschaffungs-Block, der ZWEITE die drei Rundentexte.
        creation_block_b = full_v7_save(CHAR_B, name="GastB", save_id="fixture-u5-struct-gast-b-001")
        creation_response = "```json\n" + json.dumps(creation_block_b, ensure_ascii=False) + "\n```"
        debrief_block_a = full_v7_save(CHAR_A, name="GastA", save_id="fixture-u5-struct-gast-a-002", level=2)
        debrief_block_b = full_v7_save(CHAR_B, name="GastB", save_id="fixture-u5-struct-gast-b-002", level=2)
        debrief_text = (
            "Abschnitt beendet.\n"
            "```json\n" + json.dumps(debrief_block_a) + "\n```\n"
            "```json\n" + json.dumps(debrief_block_b) + "\n```\n"
            + COMPLETION_MARKER
        )
        _factory_calls = {"n": 0}

        def gm_transport_factory(*_args, **_kw):
            _factory_calls["n"] += 1
            if _factory_calls["n"] == 1:
                return _ScriptedGm([creation_response])
            return _ScriptedGm([
                "SL-Antwort auf den Leader-Anker.", "SL-Antwort auf den Gast-B-Erstbeitrag.", debrief_text,
            ])

        operator_printed: list[str] = []
        operator = TuiSession(
            onboarding_dir=root / "op_onboarding", catalog_dir=root / "op_catalog",
            participant_id=BETREIBER_ID, print_fn=operator_printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=gm_transport_factory, host_capable=True,
        )

        gast_a_printed: list[str] = []
        gast_a = TuiSession(
            onboarding_dir=root / "gast_a_onboarding", catalog_dir=root / "gast_a_catalog",
            participant_id=GAST_A_ID, print_fn=gast_a_printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            host_capable=False,
        )
        gast_b_printed: list[str] = []
        gast_b = TuiSession(
            onboarding_dir=root / "gast_b_onboarding", catalog_dir=root / "gast_b_catalog",
            participant_id=GAST_B_ID, print_fn=gast_b_printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            host_capable=False,
        )
        # Bytegleiche Verdrahtung zu `scripts/mmo_sim.py`s `--guest-terminal`-
        # Schleife (register_guest_terminal) -- NUR ohne eigene Threads/FIFOs;
        # derselbe `_HumanDriver.decide()`-Routingmechanismus (`io = outer.
        # _table_guest_terminals.get(pid, outer)`) wird dadurch real geuebt.
        operator.register_guest_terminal(GAST_A_ID, gast_a)
        operator.register_guest_terminal(GAST_B_ID, gast_b)

        # ═══ (2) Gast A: ECHTER Import ueber [charaktere] -> [2]. ═══
        import_block_a = full_v7_save(CHAR_A, name="GastA", save_id="fixture-u5-struct-gast-a-001")
        gast_a._input = _scripted_input(["2", json.dumps(import_block_a), "ENDE", "j"])
        gast_a._cmd_menu_charaktere()
        gast_a_out = "\n".join(gast_a_printed)
        assert f"action=register_new char_id={CHAR_A}" in gast_a_out, gast_a_out
        resolved_a = gast_a._resolve_member(GAST_A_ID)
        assert resolved_a is not None and resolved_a[1] == CHAR_A, resolved_a

        # ═══ Gast B: ECHTE genehmigte Erschaffung ueber [charaktere] ->
        # [4] (Anfrage) -> Betreiber [4]->[1]->[1] (Annahme) -> Gast [5]
        # (Dialogabschluss, GENAU EIN GM-Call). ═══
        gast_b._input = _scripted_input(["4", BETREIBER_ID])
        gast_b._cmd_menu_charaktere()
        assert "Erschaffungsanfrage an Betreiber" in "\n".join(gast_b_printed), gast_b_printed

        operator._input = _scripted_input(["4", "1", "1"])
        operator._cmd_menu_charaktere()
        op_out = "\n".join(operator_printed)
        assert f"[1] {GAST_B_ID}" in op_out, op_out
        assert f"Gast '{GAST_B_ID}' freigegeben" in op_out, op_out

        gast_b_printed.clear()
        gast_b._input = _scripted_input(["5"])
        gast_b._cmd_menu_charaktere()
        gast_b_out = "\n".join(gast_b_printed)
        assert "Erschaffung abgeschlossen" in gast_b_out, gast_b_out
        resolved_b = gast_b._resolve_member(GAST_B_ID)
        assert resolved_b is not None and resolved_b[1] == CHAR_B, resolved_b

        # ═══ Tisch: anbieten/anfragen/annehmen (Gast A ZUERST -> Leader). ═══
        operator._cmd_table_offer([TABLE_KEY])
        gast_a._cmd_table_request_join([TABLE_KEY])
        gast_b._cmd_table_request_join([TABLE_KEY])
        operator_printed.clear()
        operator._cmd_table_accept([TABLE_KEY, GAST_A_ID])
        operator._cmd_table_accept([TABLE_KEY, GAST_B_ID])
        assert f"'{GAST_A_ID}' an Tisch '{TABLE_KEY}' aufgenommen" in "\n".join(operator_printed)
        assert f"'{GAST_B_ID}' an Tisch '{TABLE_KEY}' aufgenommen" in "\n".join(operator_printed)

        # ═══ Rundenscript: Gast A (Leader) Anker + Debriefzug + Notiz +
        # Karte; Gast B (Nicht-Leader) Konsens + Erstbeitrag + Notiz + Karte;
        # Betreiber (figurfrei) nur die eigene Tisch-Abschlusskarte. ═══
        gast_a._input = _scripted_input([
            "Ich sichte knapp die Lage am Tisch.",
            "Ich schliesse den Abschnitt ab.",
            "Abschlussnotiz Leader (Gast A): Reise erfolgreich.",
            "1",
        ])
        gast_b._input = _scripted_input([
            "j",
            "Ich pruefe meine Ausruestung und melde mich.",
            "Abschlussnotiz Gast B: Erschaffung und erster Einsatz gelungen.",
            "1",
        ])
        operator._input = _scripted_input(["3"])
        operator_printed.clear()
        gast_a_printed.clear()
        gast_b_printed.clear()
        operator._cmd_table_start([TABLE_KEY])

        op_out2 = "\n".join(operator_printed)
        gast_a_out2 = "\n".join(gast_a_printed)
        gast_b_out2 = "\n".join(gast_b_printed)

        # ═══ Assertion 1: figurfreier Betreiber wird NICHT Leader. ═══
        assert f"Gruppe eingeladen: leader={GAST_A_ID}" in op_out2, op_out2
        table = core_store.Table.load(run_dir, TABLE_ID)
        assert table.leader == GAST_A_ID, table.leader
        assert BETREIBER_ID not in table.members, table.members
        assert sorted(table.members) == [GAST_A_ID, GAST_B_ID], table.members

        final_path = run_dir / "completion" / f"{TABLE_ID}-section__final.json"
        assert final_path.exists(), "U5-struct: regulaerer Abschluss haette __final.json schreiben muessen."

        # ═══ Assertion 3: beide Abschlusskarten dispatchen real -- echte
        # Exportdatei UND das NEUE Label woertlich. ═══
        assert f"Abschlusskarte fuer '{GAST_A_ID}'" in gast_a_out2, gast_a_out2
        assert ") Zurueck zum Hauptmenue" in gast_a_out2, gast_a_out2
        export_a_path = gast_a.exports_dir / f"{GAST_A_ID}.json"
        assert export_a_path.exists(), "U5-struct: Gast As Abschlusskarten-Export-Handler lief nicht real."

        assert f"Abschlusskarte fuer '{GAST_B_ID}'" in gast_b_out2, gast_b_out2
        assert ") Zurueck zum Hauptmenue" in gast_b_out2, gast_b_out2
        export_b_path = gast_b.exports_dir / f"{GAST_B_ID}.json"
        assert export_b_path.exists(), "U5-struct: Gast Bs Abschlusskarten-Export-Handler lief nicht real."

        assert f"Tisch-Abschlusskarte (Betreiber, figurfrei) fuer '{TABLE_ID}'" in op_out2, op_out2

        # ═══ Beide Reloads lvl > start (1 -> 2). ═══
        from mmo_sim.domain.zeitriss import onboarding
        priv_a = onboarding.peek(gast_a.onboarding_dir, GAST_A_ID)
        assert priv_a is not None and priv_a.final_save["characters"][0]["lvl"] == 2, priv_a
        priv_b = onboarding.peek(gast_b.onboarding_dir, GAST_B_ID)
        assert priv_b is not None and priv_b.final_save["characters"][0]["lvl"] == 2, priv_b


def test_completion_card_invalid_choice_triggers_no_handler():
    """Negative Assertion (U5 Briefing): eine ungueltige Kartennummer loest
    KEINEN der echten Handler aus -- `_dispatch_completion_card_choice`
    (tui.py:8614ff) wiederholt die Abfrage, bis eine gueltige Nummer/'/
    zurueck' kommt; hier wird nach einer ungueltigen Zahl sofort '/zurueck'
    nachgereicht, damit der Test terminiert, OHNE dass die gespionten
    Handler je aufgerufen wurden."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=root / "onboarding", catalog_dir=root / "catalog",
            participant_id="probe_u5", print_fn=printed.append, host_capable=False,
        )
        called: list[str] = []
        actions = [
            ("Export des eigenen Standes (echter Export)", lambda: called.append("export")),
            ("Zurueck zum Hauptmenue", lambda: called.append("zurueck")),
        ]
        session._input = _scripted_input(["99", "/zurueck"])
        session._dispatch_completion_card_choice(session, actions)
        assert called == [], f"U5-struct: ungueltige Kartennummer durfte KEINEN Handler ausloesen: {called}"
        assert "Unbekannte Auswahl" in "\n".join(printed), printed


def test_completion_marker_inside_fenced_block_is_not_a_real_completion():
    """Negative Assertion (U5 Briefing "ein neuer Filtertext/Markertext darf
    keinen falschen Erfolg behaupten"): `COMPLETION_MARKER` als Teil eines
    ZITIERTEN Beispiels INNERHALB eines Fence-Blocks darf NICHT als echter
    Abschluss gelten -- nur eine TOP-LEVEL-Zeile mit GENAU diesem Marker
    (optional mit passenden table_id=/section_id=-Qualifiern) zaehlt
    (`core.completion_marker.completion_marker_matches`)."""
    table_id, section_id = "local-probe-a-probe-b", "local-probe-a-probe-b-section"
    fenced_decoy = (
        "Hier ein Beispiel, wie ein Abschluss aussehen koennte:\n"
        "```\n" + COMPLETION_MARKER + "\n```\n"
        "Das war nur ein zitiertes Beispiel, kein echter Abschluss."
    )
    assert completion_marker_matches(fenced_decoy, COMPLETION_MARKER, table_id, section_id) is False, fenced_decoy

    real_completion = "Abschnitt fertig.\n" + COMPLETION_MARKER
    assert completion_marker_matches(real_completion, COMPLETION_MARKER, table_id, section_id) is True

    wrong_qualifier = f"{COMPLETION_MARKER} table_id=ein-anderer-tisch"
    assert completion_marker_matches(wrong_qualifier, COMPLETION_MARKER, table_id, section_id) is False, wrong_qualifier


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
