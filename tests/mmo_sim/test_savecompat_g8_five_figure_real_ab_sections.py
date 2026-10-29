#!/usr/bin/env python3
"""
tests/mmo_sim/test_savecompat_g8_five_figure_real_ab_sections.py —
ZR-SK-FINALISIERUNG-20261016-R1, Pflichtgruppe `creation_and_five_figure_
ab` (02_SAVEVERTRAG.md §E).

Ergaenzt (ersetzt NICHT) `test_savecompat_creation_and_five_figure_ab.py`:
jene Datei bearbeitet EINE feste Figur, archiviert vorgegebene Antworten
direkt und ruft den Core-Loader direkt auf (review/INTAKE.md: "beweist
nicht fuenf Figuren mit zwei gespielten Abschnitten"). Diese Datei liefert
genau das, ueber den REALEN Consumer-Pfad:

  1. FUENF verschiedene, echte Erschaffungen (`TuiSession._cmd_new_or_
     switch_character` -> `core.creation_service.run_admitted_creation_
     dialog`, EIN eigener SL-Dialog je Figur, fuenf unterscheidbare
     `char_id`s -- keine Einfiguren-Funktion als Fuenfer ausgewiesen).
  2. Abschnitt A: ein echter Fuenfer-Tisch (`core.store.create_table_
     from_offer_log`, `ZeitrissTableSizePolicy.max_size == 5`), eine echte
     Spielrunde (`core.app_service.run_play_session` -- derselbe Call-Pfad
     wie `TuiSession._cmd_local_round`/`lab.runner.LabRunner.run_section`,
     A4) mit FUeNF unterscheidbaren Entscheidungen/Konsequenzen (je Figur
     ein eigener Spielzugtext + ein eigener Wallet-/Ausruestungsdelta im
     Debrief).
  3. Echter A-Export: jedes Abschnitt-A-Endresultat wird ueber die reale
     Exportfunktion (`domain.zeitriss.import_export.export_save_text`)
     als eigenstaendige Datei geschrieben UND ueber die reale, strukturelle
     Importpruefung (`preview_import`/`resolve_import`) zurueckgelesen
     (byte-identischer Roundtrip, `action == "noop_identical"`) -- KEINE
     bloss interne Zustandskontinuitaet, ein echter Dateiartefakt.
  4. Abschnitt B: EIGENER, generationserhoehter Tisch derselben fuenf
     Figuren (`create_table_from_offer_log`s bestehende "neuer Abschnitt
     nach Abschluss"-Ableitung, `<table_id>__2`), erneut FUeNF eigene
     Entscheidungen/Konsequenzen -- JEDE Konsequenz baut nachweislich auf
     dem gerade zurueckgelesenen A-Export auf (gleicher `char_id`, A-Delta
     bleibt erhalten, B fuegt ein EIGENES zusaetzliches Delta hinzu).

Kein Modellaufruf (synthetisches GM-/Personadouble), kein Netz. Pure
Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import app_service, store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import import_export, onboarding, saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import (  # noqa: E402
    COMPLETION_MARKER, ZeitrissHarvestValidator, ZeitrissTableSizePolicy,
)
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"

CHAR_SPECS = [
    ("p_anke", "CHR-SCFA8-ANKE", "Anke", "ANKEOPS"),
    ("p_bela", "CHR-SCFA8-BELA", "Bela", "BELAOPS"),
    ("p_cem", "CHR-SCFA8-CEM", "Cem", "CEMOPS"),
    ("p_dora", "CHR-SCFA8-DORA", "Dora", "DORAOPS"),
    ("p_elia", "CHR-SCFA8-ELIA", "Elia", "ELIAOPS"),
]
LEADER_ID = CHAR_SPECS[0][0]
GUEST_IDS = [c[0] for c in CHAR_SPECS[1:]]
PID_TO_CHAR = {pid: char_id for pid, char_id, _n, _c in CHAR_SPECS}

SECTION_A_DECISIONS = {
    "p_anke": ("Ich uebernehme die Spitze und sichere den Zugang.", 30),
    "p_bela": ("Ich hacke das Kodexterminal fuer zusaetzliche Daten.", 15),
    "p_cem": ("Ich decke den Rueckzug mit schwerem Geraet.", 45),
    "p_dora": ("Ich verhandle mit der ansaessigen Fraktion.", 10),
    "p_elia": ("Ich improvisiere eine Ablenkung mit Sprengstoff.", 60),
}
SECTION_B_DECISIONS = {
    "p_anke": ("Ich fuehre den zweiten Trupp durch den Nordtunnel.", 20),
    "p_bela": ("Ich knacke die zweite Sicherheitsschicht.", 25),
    "p_cem": ("Ich haelt die Stellung gegen den Gegenangriff.", 35),
    "p_dora": ("Ich schliesse einen zweiten Handel ab.", 5),
    "p_elia": ("Ich zuendet die zweite, groessere Ablenkung.", 50),
}


def _scripted_input(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


class _CreationGm:
    def __init__(self, save_block: dict):
        self.calls = 0
        self._save_block = save_block

    def turn(self, idx, text):
        self.calls += 1
        if self.calls == 1:
            return {"content": "Wie beginnt deine Zeitreise?"}
        return {"content": "```json\n" + json.dumps(self._save_block) + "\n```"}


def _create_real_figure(base: Path, pid: str, char_id: str, name: str, callsign: str) -> dict:
    """Treibt eine ECHTE SL-Erschaffung ueber den realen Produktweg
    (`TuiSession._cmd_new_or_switch_character` -> `core.creation_service.
    run_admitted_creation_dialog` -> `core.save_correction.pursue_single_
    figure_correction`, DIESELBE Stelle, in die R-SCF-A `archive_raw_
    response` additiv verdrahtet hat) -- KEINE direkte Save-Injektion."""
    save_block = full_v7_save(char_id, name=name, callsign=callsign, wallet=0.0)
    gm = _CreationGm(save_block)
    session = TuiSession(
        base / "onboarding", base / "catalog", pid,
        input_fn=_scripted_input(["n", f"Ich erwache als {name} inmitten eines Risses.", "x"]),
        print_fn=lambda *_a: None,
        run_dir=base / "run", states_dir=base / "states", schema_path=_SCHEMA,
        gm_transport_factory=lambda: gm,
    )
    rc = session.run()
    assert rc == 0, f"Erschaffung fuer {pid} brach unerwartet ab"
    state = onboarding.peek(base / "onboarding", pid)
    assert state is not None and state.status == "completed", f"Erschaffung fuer {pid} nicht abgeschlossen: {state}"
    assert zeitriss_saves.block_char_id(state.final_save) == char_id
    return state.final_save


class _ScriptedDriver:
    def __init__(self, text: str):
        self._text = text
        self.calls = 0

    def decide(self, ctx: dict) -> ParticipantDecision:
        self.calls += 1
        return ParticipantDecision(text=self._text, origin_source="fake:g8", decision=None)


class _FivePersonaGm:
    """Nachbau der bereits etablierten, real bewiesenen `_SmartGmHandler`-
    Logik (`test_ux1_g01_five_humans_full_flow_2026_10_05.py`), hier
    IN-PROCESS statt als HTTP-Loopback (A4: `run_play_session` ruft
    `gm_transport.turn` direkt, kein Netz noetig): akkumuliert gesehene
    `char_id`s aus jedem tatsaechlich gesendeten Turntext; liefert den
    vollen Fuenfer-Debrief + Abschlussmarker ERST, sobald alle fuenf
    erwarteten Figuren tatsaechlich angekommen sind."""
    def __init__(self, expected_char_ids: set[str], end_saves: dict[str, dict], table_id: str, section_id: str):
        self.calls = 0
        self.seen: set[str] = set()
        self.expected = set(expected_char_ids)
        self.end_saves = end_saves
        self.table_id = table_id
        self.section_id = section_id
        self.output_limit_tokens = 8000

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls += 1
        for blk in zeitriss_saves.extract_all_saves(text):
            cid = zeitriss_saves.block_char_id(blk)
            if cid:
                self.seen.add(cid)
        if self.expected.issubset(self.seen):
            body = "\n".join(
                f"```json\n{json.dumps(b, ensure_ascii=False)}\n```" for b in self.end_saves.values()
            )
            content = f"{body}\n{COMPLETION_MARKER} table_id={self.table_id} section_id={self.section_id}"
        else:
            content = f"Szene {self.calls}: Ihr steht bereit. Was tut ihr als naechstes?"
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "g8-fake"}


def _play_section(
    lobby, table, states_dir, section_id: str, decisions: dict[str, tuple[str, int]], end_saves: dict[str, dict],
    chrononaut_ids: dict[str, str], ps_store: PersonaStateStore, import_payloads: dict[str, dict],
):
    contexts = {
        pid: {"user": decisions[pid][0], "import_save_payload": import_payloads[pid]}
        for pid in [LEADER_ID] + GUEST_IDS
    }
    expected_char_ids = set(chrononaut_ids.values())
    gm = _FivePersonaGm(expected_char_ids, end_saves, table.table_id, section_id)
    drivers = {pid: _ScriptedDriver(decisions[pid][0]) for pid in [LEADER_ID] + GUEST_IDS}
    controller = TableController(table.leader, drivers)
    outcome = app_service.run_play_session(
        lobby, table, gm, controller, section_id, contexts, states_dir, "2026-10-16",
        "2026-10-16T00:00:00", COMPLETION_MARKER, ZeitrissHarvestValidator(), ps_store,
        zeitriss_saves.harvest_from_debrief, max_turns=20,
    )
    return outcome, gm


def _build_section_delta(base_block: dict, char_id: str, wallet_delta: int, tag: str, item_label: str) -> dict:
    """Baut einen NEUEN, gueltigen v7-Endstand aus `base_block` (deepcopy --
    niemals Aliasing) mit einem EIGENEN, unterscheidbaren Delta (Wallet-
    zuwachs + ein neuer Inventareintrag) -- die Konsequenz der jeweiligen
    Entscheidung dieser Figur in diesem Abschnitt."""
    end = copy.deepcopy(base_block)
    char = end["characters"][0]
    char["wallet"] = (char.get("wallet") or 0) + wallet_delta
    char.setdefault("carry", [])
    char["carry"] = list(char["carry"]) + [item_label]
    end["save_id"] = f"{base_block.get('save_id', 'save')}-{tag}"
    assert zeitriss_saves.block_char_id(end) == char_id
    return end


def test_g8_five_real_creations_two_real_ab_sections_with_real_export_roundtrip():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        run_dir, states_dir = base / "run", base / "states"
        (run_dir).mkdir(parents=True, exist_ok=True)
        write_test_profile(run_dir)
        ps_store = PersonaStateStore(schema_path=_SCHEMA)

        # ── 1) FUENF echte, unterscheidbare Erschaffungen ──────────────────
        creation_saves = {
            pid: _create_real_figure(base, pid, char_id, name, callsign)
            for pid, char_id, name, callsign in CHAR_SPECS
        }
        chrononaut_ids = {pid: zeitriss_saves.block_char_id(b) for pid, b in creation_saves.items()}
        assert len(set(chrononaut_ids.values())) == 5, "fuenf unterscheidbare Figuren erwartet"

        # ── 2) Abschnitt A: echter Fuenfer-Tisch, fuenf Entscheidungen ─────
        lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        for pid in [LEADER_ID] + GUEST_IDS:
            lobby.join(pid)
        table_id = f"g8-table-{LEADER_ID}"
        offer_events = [{"type": "offer", "id": "o-a", "from": LEADER_ID, "wants": GUEST_IDS}]
        offer_events += [{"type": "consent", "offer_id": "o-a", "from": pid, "accept": True} for pid in GUEST_IDS]
        table_a, derivation_a = core_store.create_table_from_offer_log(lobby, table_id, offer_events, chrononaut_ids)
        assert table_a is not None, derivation_a
        assert set(table_a.members) == set(chrononaut_ids), table_a.members
        assert len(table_a.members) == 5

        a_end_saves = {
            pid: _build_section_delta(creation_saves[pid], chrononaut_ids[pid], delta, "A", f"A-Beute-{pid}")
            for pid, (_text, delta) in SECTION_A_DECISIONS.items()
        }
        outcome_a, gm_a = _play_section(
            lobby, table_a, states_dir, f"{table_id}-section", SECTION_A_DECISIONS, a_end_saves,
            chrononaut_ids, ps_store, creation_saves,
        )
        assert outcome_a.completion.success, outcome_a.completion.reason
        assert gm_a.calls == 5, f"erwartet 1 Leader-Anker + 4 Gast-Importe = 5 echte SL-Calls, beobachtet={gm_a.calls}"
        for pid in [LEADER_ID] + GUEST_IDS:
            published = core_store.load_current_save(run_dir, pid, ps_store, states_dir=states_dir)
            assert published == a_end_saves[pid], f"'{pid}': Abschnitt-A-Endstand nicht korrekt veroeffentlicht"

        # ── 3) Echter A-Export + Re-Import-Pruefung (Rundtrip-Beleg) ───────
        # G8_EVIDENCE_DIR (optional, analog A24_EVIDENCE_DIR/H02_EVIDENCE_DIR
        # in bereits bestehenden Suiten-Konventionen): OHNE Angabe bleibt
        # dies ein eigener Temp-Ordner -- `run_all.py` findet/fuehrt diesen
        # Test damit OHNE externe Vorbereitung in JEDEM Checkout aus (kein
        # hartcodierter privater Pfad im Produktkandidaten).
        import os as _os
        _evidence_root = Path(_os.environ.get("G8_EVIDENCE_DIR") or tempfile.mkdtemp(prefix="g8_evidence_"))
        exports_dir = _evidence_root / "exports" / "A"
        exports_dir.mkdir(parents=True, exist_ok=True)
        reimported = {}
        for pid in [LEADER_ID] + GUEST_IDS:
            export_text = import_export.export_save_text(a_end_saves[pid])
            export_path = exports_dir / f"{pid}.json"
            export_path.write_text(export_text, encoding="utf-8")
            read_back_text = export_path.read_text(encoding="utf-8")
            preview = import_export.preview_import(read_back_text)
            assert preview.single_char_ok and preview.char_id == chrononaut_ids[pid], preview
            incoming = json.loads(read_back_text)
            decision = import_export.resolve_import(
                incoming, known_char_ids={chrononaut_ids[pid]}, existing_block_for_char_id=a_end_saves[pid],
                active_binding=False, open_completion_order=False,
            )
            assert decision.action == "noop_identical", (
                f"'{pid}': A-Export muss byte-identisch re-importierbar sein, beobachtet={decision.action}"
            )
            reimported[pid] = incoming

        # ── 4) Abschnitt B: EIGENER, generationserhoehter Tisch, baut auf dem
        #       gerade zurueckgelesenen A-Export auf ────────────────────────
        offer_events_b = [{"type": "offer", "id": "o-b", "from": LEADER_ID, "wants": GUEST_IDS}]
        offer_events_b += [{"type": "consent", "offer_id": "o-b", "from": pid, "accept": True} for pid in GUEST_IDS]
        table_b, derivation_b = core_store.create_table_from_offer_log(lobby, table_id, offer_events_b, chrononaut_ids)
        assert table_b is not None, derivation_b
        assert table_b.table_id == f"{table_id}__2", (
            f"Abschnitt B muss der bestehenden Generationslogik folgen (neuer Abschnitt nach Abschluss), "
            f"beobachtet={table_b.table_id}"
        )

        b_end_saves = {
            pid: _build_section_delta(reimported[pid], chrononaut_ids[pid], delta, "B", f"B-Beute-{pid}")
            for pid, (_text, delta) in SECTION_B_DECISIONS.items()
        }
        outcome_b, gm_b = _play_section(
            lobby, table_b, states_dir, f"{table_b.table_id}-section", SECTION_B_DECISIONS, b_end_saves,
            chrononaut_ids, ps_store, reimported,
        )
        assert outcome_b.completion.success, outcome_b.completion.reason
        assert gm_b.calls == 5, f"erwartet 5 echte SL-Calls fuer Abschnitt B, beobachtet={gm_b.calls}"

        for pid in [LEADER_ID] + GUEST_IDS:
            published_b = core_store.load_current_save(run_dir, pid, ps_store, states_dir=states_dir)
            assert published_b == b_end_saves[pid], f"'{pid}': Abschnitt-B-Endstand nicht korrekt veroeffentlicht"
            a_wallet = a_end_saves[pid]["characters"][0]["wallet"]
            b_wallet = published_b["characters"][0]["wallet"]
            assert b_wallet > a_wallet, (
                f"'{pid}': B muss auf dem A-Delta AUFBAUEN (kumulativ), nicht es ersetzen -- "
                f"A={a_wallet} B={b_wallet}"
            )
            carry = published_b["characters"][0]["carry"]
            assert f"A-Beute-{pid}" in carry and f"B-Beute-{pid}" in carry, (
                f"'{pid}': B-Endstand muss sowohl das A- als auch das B-Beuteitem tragen (echte Kontinuitaet "
                f"ueber den re-importierten A-Export), beobachtet={carry}"
            )

        (exports_dir.parent / "B").mkdir(parents=True, exist_ok=True)
        for pid in [LEADER_ID] + GUEST_IDS:
            (exports_dir.parent / "B" / f"{pid}.json").write_text(
                import_export.export_save_text(b_end_saves[pid]), encoding="utf-8",
            )


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
