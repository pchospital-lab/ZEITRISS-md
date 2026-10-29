#!/usr/bin/env python3
"""
tests/mmo_sim/test_w43_save_validation_acceptance_gate_2026_10_07.py — R12-
Savegate, W43-Slice: Zieltests fuer `domain/zeitriss/save_validation.py`
(volle lokale v7-Validierung) UND den einheitlichen Annahmepunkt, der sie
in die ECHTEN Produktpfade einhaengt (`ZeitrissHarvestValidator.
validate_block` in `domain/zeitriss/policy.py`, `import_export.
preview_import`).

Abdeckung (01_AUFTRAG_SAVEGATE.md §A/§B, SCOPE.json CASES.json):
  SC01 -- A/C-Originale streng ablehnen, A-Reexport/B positive Kontrollen.
  SC02 -- Unveraenderte lokale Schemas, richtiger Draft, lokale Refs,
          kein stiller Rueckfall bei fehlendem Validator.
  SC03 -- Erschaffung vor Publication (Annahmepunkt in `onboarding.
          complete_with_save` via `run_admitted_creation_dialog`).
  SC05 -- Inhalts-/Identitaetswahrung (kein Write/keine Heuristik durch
          den Validator selbst).
  SC06 -- Doppelte/falsche/fehlende Figuren.
  SC11 -- Fuenf (hier: zwei, Mechanismus ist generisch pro Mitglied) vor
          Harvest gueltig -- EIN ungueltiges Mitglied haelt die GESAMTE
          neue Harvestfreigabe zurueck.
  SC15 -- Terminalsteuerung im Savezustand (kein Absturz, kein
          "gespeichert" bei ungueltigem Draft).
  SC16 -- Drittanbieter-JSON/Import: ungueltiger Import wird VOR Write
          gesperrt.
  SC17 -- Privacy der Fehlerdaten (kein roher Python-Traceback).
  SC19 -- Bestand/Fixtures ehrlich (LIVE2-Regressionsfixtures unveraendert
          kopiert, keine Schutzassertion geschwaecht).

Pure Python, nur `assert`, echter Exitcode -- gleiches Muster wie die
bestehende Suite (kein pytest-Fixture-Zwang)."""
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
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save, full_v7_block_text  # noqa: E402 (Fixturehelper, FIXTURE_ONLY)

import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.creation_service import ReplyResult, run_admitted_creation_dialog  # noqa: E402
from mmo_sim.core.events import EventLog  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.core.runtime import SectionRuntime  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding, save_validation as sv, saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss import import_export  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy  # noqa: E402

COMPLETION_MARKER = "SECTION-ABSCHLUSS-BESTAETIGT"
_FIXTURES = _HERE / "fixtures" / "ux1" / "savegate"
_DUMMY_PERSONA_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)


def _load_fixture(name: str) -> dict:
    return json.loads((_FIXTURES / name).read_text(encoding="utf-8"))


def _wallet_as_number(char_id: str) -> dict:
    """Mild-pass (v7/Ein-Figur/char_id stimmen), aber strukturell
    schema-ungueltig: `economy.wallets.<id>` ist eine blanke Zahl statt
    `{"balance": ...}`-Objekt -- exakt das LIVE2-A-Original-Muster."""
    block = full_v7_save(char_id, name="Flo")
    block["economy"] = {"wallets": {char_id: 500}}
    return block


# ---------------------------------------------------------------------------
# SC02 -- Unveraenderte lokale Schemas, richtiger Draft, lokale Refs.
# ---------------------------------------------------------------------------

def test_sc02_schemas_loaded_byte_identical_and_never_mutated():
    tolerant_path = _REPO_ROOT / "systems" / "gameflow" / "saveGame.v7.schema.json"
    export_path = _REPO_ROOT / "systems" / "gameflow" / "saveGame.v7.export.schema.json"
    before_tolerant = tolerant_path.read_bytes()
    before_export = export_path.read_bytes()

    assert sv._TOLERANT_SCHEMA == json.loads(before_tolerant)
    assert sv._EXPORT_SCHEMA == json.loads(before_export)
    assert sv._TOLERANT_SCHEMA["$schema"] == "http://json-schema.org/draft-07/schema#"
    assert type(sv._TOLERANT_VALIDATOR).__name__ == "Draft7Validator"
    assert type(sv._EXPORT_VALIDATOR).__name__ == "Draft7Validator"

    # Ein voller Validierungslauf darf die Schemadateien NICHT veraendern.
    sv.validate_structure(full_v7_save("CHR-SC02-01"))
    assert tolerant_path.read_bytes() == before_tolerant
    assert export_path.read_bytes() == before_export


def test_sc02_unresolvable_ref_fails_closed_no_network():
    """Lokale Registry ohne `retrieve`-Callback -- ein nicht registrierter
    Verweis scheitert kontrolliert statt einen Netzabruf zu versuchen."""
    from referencing.exceptions import Unresolvable
    try:
        sv._REGISTRY.resolver().lookup("https://example.invalid/not-registered.json")
        raised = False
    except Unresolvable:
        raised = True
    assert raised, "ein nicht lokal gebundener Verweis muss kontrolliert scheitern, kein Netzfetch"


# ---------------------------------------------------------------------------
# SC01 -- A/C-Originale streng ablehnen, A-Reexport/B positive Kontrollen.
# ---------------------------------------------------------------------------

def test_sc01_a_original_rejected_reexport_and_b_accepted_c_rejected():
    a_original = _load_fixture("sc01_testspieler_a_original_invalid.json")
    a_reexport = _load_fixture("sc01_testspieler_a_reexport_valid.json")
    b_valid = _load_fixture("sc01_testspieler_b_valid.json")
    c_invalid = _load_fixture("sc01_testspieler_c_invalid.json")

    cid_a = zeitriss_saves.block_char_id(a_original)
    assert sv.validate_save_block(a_original, cid_a).accepted is False, (
        "A-Original (Wallet als blanke Zahl) muss trotz milder v7/Ein-Figur/char_id-Pruefung "
        "am Vollschemafehler scheitern (SC01: milder Harvest uebersteuert den Schemafehler nicht)."
    )
    assert sv.validate_save_block(a_reexport, zeitriss_saves.block_char_id(a_reexport)).accepted is True
    assert sv.validate_save_block(b_valid, zeitriss_saves.block_char_id(b_valid)).accepted is True
    assert sv.validate_save_block(c_invalid, zeitriss_saves.block_char_id(c_invalid)).accepted is False

    # Dieselbe Erkenntnis muss am REALEN Produktgate ankommen, nicht nur am
    # internen Validator -- `ZeitrissHarvestValidator` ist der einzige
    # Aufrufpunkt, den `onboarding.complete_with_save`/`core.store.
    # complete_section` tatsaechlich benutzen.
    gate = ZeitrissHarvestValidator()
    assert gate.validate_block(a_original, cid_a) is False
    assert gate.validate_block(a_reexport, zeitriss_saves.block_char_id(a_reexport)) is True


# ---------------------------------------------------------------------------
# SC05 -- Inhalts-/Identitaetswahrung: Validator schreibt nichts, rät nichts.
# ---------------------------------------------------------------------------

def test_sc05_validator_never_mutates_block_and_reports_exact_paths():
    c_invalid = _load_fixture("sc01_testspieler_c_invalid.json")
    before = copy.deepcopy(c_invalid)
    result = sv.validate_save_block(c_invalid, zeitriss_saves.block_char_id(c_invalid))
    assert c_invalid == before, "save_validation darf den uebergebenen Block NIE veraendern."
    assert result.accepted is False

    paths = {e.path for e in result.structure.errors}
    assert any(p.startswith("/campaign/mode") for p in paths), (
        "campaign.mode='core' muss als eigener Fehlerpfad erscheinen -- KEINE lokale "
        "Enumheuristik, die 'core' z.B. stillschweigend auf 'mixed' umschreibt."
    )
    assert any("/economy/wallets/" in p for p in paths), (
        "Wallet-als-Zahl muss als eigener Fehlerpfad erscheinen, kein stiller Objekt-Wrap."
    )
    mode_errors = [e for e in result.structure.errors if e.path.startswith("/campaign/mode")]
    assert any(e.expected == ["mixed", "preserve", "trigger"] for e in mode_errors), (
        "der erwartete Enumwertebereich muss mit ausgegeben werden (SL bekommt die Schema-Enums)."
    )


def test_sc05_number_wallet_rejected_not_silently_wrapped():
    block = _wallet_as_number("CHR-SC05-01")
    before = copy.deepcopy(block)
    result = sv.validate_save_block(block, "CHR-SC05-01")
    assert result.accepted is False
    assert block == before
    assert not isinstance(block["economy"]["wallets"]["CHR-SC05-01"], dict), (
        "Beleg, dass der Validator NICHT selbst 100 -> {'balance': 100} umschreibt."
    )


# ---------------------------------------------------------------------------
# SC06 -- Doppelte/falsche/fehlende Figuren.
# ---------------------------------------------------------------------------

def test_sc06_duplicate_save_id_conflict_not_hidden_by_first_wins():
    block_a = full_v7_save("CHR-SC06-01", name="Flo", save_id="dup-1")
    block_b = full_v7_save("CHR-SC06-01", name="AndereFigur", save_id="dup-1")
    dups = sv.find_duplicate_save_ids([block_a, block_b])
    codes = {d.code for d in dups}
    assert "duplicate_save_id_conflict" in codes
    assert "duplicate_char_id_conflict" in codes


def test_sc06_identical_resend_is_not_a_false_duplicate_conflict():
    """Ein idempotenter Zweitversand DESSELBEN Inhalts (z.B. Recovery nach
    Retry) ist KEIN Konflikt -- nur ABWEICHENDER Inhalt bei gleicher ID
    zaehlt."""
    block = full_v7_save("CHR-SC06-02", name="Flo", save_id="same-1")
    dups = sv.find_duplicate_save_ids([block, copy.deepcopy(block)])
    assert dups == []


def test_sc06_binding_rejects_multi_missing_and_wrong_figure():
    one_char = full_v7_save("CHR-SC06-03", name="Flo")
    two_chars = copy.deepcopy(one_char)
    two_chars["characters"].append(copy.deepcopy(two_chars["characters"][0]))
    two_chars["characters"][1]["id"] = "CHR-SC06-04"

    assert any(e.code == "not_single_character" for e in sv.validate_binding(two_chars, "CHR-SC06-03"))
    assert any(e.code == "char_id_mismatch" for e in sv.validate_binding(one_char, "CHR-SC06-99"))

    empty = copy.deepcopy(one_char)
    empty["characters"] = []
    binding_errors = sv.validate_binding(empty, "CHR-SC06-03")
    assert any(e.code == "not_single_character" for e in binding_errors)
    assert any(e.code == "missing_char_id" for e in binding_errors)


# ---------------------------------------------------------------------------
# SC17 -- Privacy der Fehlerdaten: kein roher Python-Traceback.
# ---------------------------------------------------------------------------

def test_sc17_feedback_items_contain_no_raw_traceback_or_foreign_hints():
    c_invalid = _load_fixture("sc01_testspieler_c_invalid.json")
    result = sv.validate_save_block(c_invalid, zeitriss_saves.block_char_id(c_invalid))
    joined = "\n".join(result.feedback_items)
    for forbidden in ("Traceback", "File \"", "line ", "Exception:", "jsonschema.exceptions"):
        assert forbidden not in joined, f"Fehlerausgabe enthaelt rohes Python-Detail: {forbidden!r}"
    # ≤32 Feedbackpunkte je Pruefung, niemals heimlich als PASS gezaehlt.
    assert len(result.structure.errors) <= sv.MAX_FEEDBACK_ITEMS


def test_sc17_feedback_cap_never_counts_as_pass():
    minimal_fake = {"v": 7, "characters": [{"id": "CHR-SC17-01"}]}
    result = sv.validate_save_block(minimal_fake, "CHR-SC17-01")
    assert result.structure.total_error_count > sv.MAX_FEEDBACK_ITEMS
    assert result.structure.truncated is True
    assert result.structure.valid is False
    assert result.accepted is False


# ---------------------------------------------------------------------------
# SC03 -- Erschaffung vor Publication (echter Produktpfad).
# ---------------------------------------------------------------------------

class _FakeGm:
    def __init__(self, content: str):
        self._content = content

    def turn(self, turn_idx: int, user_text: str) -> dict:
        return {"content": self._content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}


def _never_called_get_reply(turn_idx: int, sl_text: str) -> ReplyResult:
    raise AssertionError("get_reply sollte hier nie aufgerufen werden -- die SL liefert den Save direkt.")


def test_sc03_invalid_full_save_blocks_completion_no_catalog_write():
    """TEST-DELTA (W48, NEW_FLOW_SEQUENCE; weiter ueberschrieben durch
    N2R5-BESTEFFORT, Flo-Design, ZR-N2R-ANSCHLUSS-20261020-FINALRUN3): vor
    W48 beendete ein strukturell ungueltiger Erstsave die Erschaffung
    SOFORT mit `status="error"`. W48 haengte genau an dieser Annahmegrenze
    die request-/admission-gebundene Korrekturschleife ein (01_AUFTRAG_
    SAVEGATE.md §C) -- `_FakeGm` liefert hier bewusst IMMER denselben
    ungueltigen Block (kein Korrekturfortschritt moeglich), wodurch das
    Budget (max. 3 zusaetzliche Ausgaben) nach drei Korrekturrunden
    erschoepft wird. W48 hielt dann kontrolliert mit `status="paused"`/
    `reason="attempt_budget_exhausted"`.

    N2R5-BESTEFFORT aendert GENAU diesen letzten Schritt: Flo woertlich
    'beim 4. Mal -- passend ODER NICHT -- muss es TROTZDEM WEITERLAUFEN;
    den Rest korrigiert der GM automatisch beim Laden' -- ein reiner
    Schema-Imperfekt (KEINE Drift) ist kein terminaler HOLD mehr, sondern
    wird best-effort finalisiert (`onboarding.complete_with_save_best_
    effort`). Die eigentliche SC03-Schutzabsicht ('KEIN stillschweigend-
    perfekter Abschluss fuer einen nie gueltig gewordenen Entwurf') bleibt
    bestehen, nur das Instrument wechselt von 'kein `completed`' auf
    'EHRLICH als `final_save_best_effort=True` markiertes `completed`' --
    kein Fake-DONE, der Unterschied bleibt maschinenlesbar."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, onboarding_dir = root / "run", root / "onboarding"
        write_test_profile(run_dir)
        participant_id = "flo_sc03"
        onboarding.start_or_resume(onboarding_dir, participant_id)

        invalid_block = _wallet_as_number("CHR-SC03-01")
        gm_text = "```json\n" + json.dumps(invalid_block) + "\n```"
        outcome = run_admitted_creation_dialog(
            run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=participant_id,
            turn_idx_start=0, initial_outgoing="Erschaffung starten.",
            gm_transport=_FakeGm(gm_text), get_reply=_never_called_get_reply,
            harvest_validator=ZeitrissHarvestValidator(), role="creation_dialog",
        )
        assert outcome.status == "completed" and outcome.reason == "attempt_budget_exhausted_best_effort", (
            "ein durchgaengig strukturell ungueltiger Save muss nach Ausschoepfung des W48-"
            f"Korrekturbudgets best-effort abschliessen (N2R5-BESTEFFORT) -- outcome={outcome}"
        )
        state = onboarding.peek(onboarding_dir, participant_id)
        assert state.status == "completed", state
        assert state.final_save_best_effort is True, (
            "muss EHRLICH als best-effort/imperfekt markiert sein -- kein stillschweigend perfekter Abschluss."
        )
        assert state.final_save == invalid_block, "best-effort-Save ist der letzte (unveraenderte) Kandidat."


def test_sc03_valid_full_save_completes_normally_positive_control():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, onboarding_dir = root / "run", root / "onboarding"
        write_test_profile(run_dir)
        participant_id = "flo_sc03b"
        onboarding.start_or_resume(onboarding_dir, participant_id)

        valid_block = full_v7_save("CHR-SC03-02", name="Flo")
        gm_text = "```json\n" + json.dumps(valid_block) + "\n```"
        outcome = run_admitted_creation_dialog(
            run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=participant_id,
            turn_idx_start=0, initial_outgoing="Erschaffung starten.",
            gm_transport=_FakeGm(gm_text), get_reply=_never_called_get_reply,
            harvest_validator=ZeitrissHarvestValidator(), role="creation_dialog",
        )
        assert outcome.status == "completed", f"ein vollstaendig gueltiger Save muss abschliessen -- {outcome}"
        state = onboarding.peek(onboarding_dir, participant_id)
        assert state.status == "completed"
        assert state.final_save == valid_block


# ---------------------------------------------------------------------------
# SC11 -- Fuenf (hier zwei) vor Harvest gueltig.
# ---------------------------------------------------------------------------

def _seed_persona_state(ps_store: PersonaStateStore, states_dir: Path, pk: str, char_id: str) -> None:
    ps_store.save_state(pk, {
        "v": 2, "persona_key": pk, "rounds_played": 0,
        "plays_char": {"character_id": char_id, "name": "Test"},
    }, states_dir=states_dir)


def _run_two_member_section(leader_save: dict, guest_save: dict):
    """Baut einen echten Zweier-Tisch (Lobby/Table/SectionRuntime, exakt
    derselbe Produktweg wie `core/lobby_flow.py`) und spielt EINEN
    Abschnitt bis zum Debrief mit den beiden uebergebenen Saves. Nutzt
    bewusst `mkdtemp()` statt des `TemporaryDirectory`-Kontextmanagers --
    der Aufrufer liest `run_dir`/`states_dir` NACH Rueckkehr dieser
    Funktion weiter (Publikationsnachweis), ein `with`-Block wuerde das
    Verzeichnis bereits beim `return` loeschen."""
    root = Path(tempfile.mkdtemp())
    run_dir, states_dir = root / "run", root / "states"
    states_dir.mkdir(parents=True)
    schema_path = root / "schema.json"
    schema_path.write_text(_DUMMY_PERSONA_SCHEMA, encoding="utf-8")
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    _seed_persona_state(ps_store, states_dir, "leader_pk", "chrono-leader")
    _seed_persona_state(ps_store, states_dir, "guest_pk", "chrono-guest")
    write_test_profile(run_dir)

    lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    lobby.join("leader_pk")
    lobby.join("guest_pk")
    table, derivation = store.create_table_from_offer_log(
        lobby, "t-sc11",
        offer_log_events=[
            {"type": "offer", "id": "o1", "from": "leader_pk", "wants": ["guest_pk"]},
            {"type": "consent", "offer_id": "o1", "from": "guest_pk", "accept": True},
        ],
        chrononaut_ids={"leader_pk": "chrono-leader", "guest_pk": "chrono-guest"},
    )
    assert table is not None, f"Tisch haette entstehen muessen: {derivation}"

    debrief = (
        "Abschnitt beendet.\n"
        f"```json\n{json.dumps(leader_save)}\n```\n"
        f"```json\n{json.dumps(guest_save)}\n```\n"
        f"{COMPLETION_MARKER}"
    )
    from mmo_sim.core.controller import TableController

    class _ScriptedDriver:
        def __init__(self, script):
            self._script = list(script)

        def decide(self, context):
            return self._script.pop(0)

    gm = _FakeGm(content="")
    gm_turns = ["SL-Antwort auf Anker-Turn.", "SL-Antwort auf Gast-Turn.", debrief]

    def _turn(turn_idx, user_text):
        return {"content": gm_turns.pop(0), "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}

    gm.turn = _turn
    leader_driver = _ScriptedDriver([
        ParticipantDecision(text="Anker.", save_payload=leader_save, origin_source="fake:leader"),
        ParticipantDecision(text="Debrief.", origin_source="fake:leader-debrief"),
        ParticipantDecision(text="Reflexion: ok.", origin_source="fake:leader-reflect"),
    ])
    guest_driver = _ScriptedDriver([
        ParticipantDecision(text="Turn.", save_payload=guest_save, origin_source="fake:guest"),
        ParticipantDecision(text="Reflexion: ok.", origin_source="fake:guest-reflect"),
    ])
    controller = TableController(leader_key="leader_pk", drivers={"leader_pk": leader_driver, "guest_pk": guest_driver})
    event_log = EventLog(run_dir)
    runtime = SectionRuntime(
        lobby=lobby, table=table, gm_transport=gm, marker=COMPLETION_MARKER,
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        harvest_extractor=zeitriss_saves.harvest_from_debrief, event_log=event_log,
    )
    outcome = runtime.run_full_section(
        controller, "section-sc11",
        contexts_by_persona={"leader_pk": {"user": "ctx-leader"}, "guest_pk": {"user": "ctx-guest"}},
        states_dir=states_dir, today="2026-10-07", ts="2026-10-07T18:00:00",
    )
    return outcome, run_dir, states_dir, ps_store


def test_sc11_one_invalid_member_blocks_entire_group_harvest():
    leader_save = full_v7_save("chrono-leader", name="Leader")
    guest_save = _wallet_as_number("chrono-guest")  # mild-pass, schema-ungueltig
    outcome, run_dir, states_dir, ps_store = _run_two_member_section(leader_save, guest_save)

    assert outcome.completion.success is False, (
        "EIN ungueltiges Mitglied muss die GESAMTE neue Harvestfreigabe zurueckhalten (SC11)."
    )
    assert "guest_pk" in outcome.completion.missing
    # Beleg, dass NICHT nur das fehlerhafte Mitglied zurueckgehalten wird,
    # sondern wirklich NICHTS publiziert wurde (auch der gueltige Leader nicht).
    assert store.load_current_save(run_dir, "leader_pk", ps_store, states_dir=states_dir) is None
    assert store.load_current_save(run_dir, "guest_pk", ps_store, states_dir=states_dir) is None


def test_sc11_all_valid_members_harvest_succeeds_positive_control():
    leader_save = full_v7_save("chrono-leader", name="Leader")
    guest_save = full_v7_save("chrono-guest", name="Guest")
    outcome, run_dir, states_dir, ps_store = _run_two_member_section(leader_save, guest_save)

    assert outcome.completion.success, outcome.completion.reason
    assert store.load_current_save(run_dir, "leader_pk", ps_store, states_dir=states_dir) == leader_save
    assert store.load_current_save(run_dir, "guest_pk", ps_store, states_dir=states_dir) == guest_save


# ---------------------------------------------------------------------------
# SC16 -- Drittanbieter-JSON/Import: ungueltiger Import wird VOR Write
# gesperrt (keine Katalogschreibung erreicht).
# ---------------------------------------------------------------------------

def test_sc16_import_preview_rejects_schema_invalid_before_any_write():
    invalid_text = json.dumps(_wallet_as_number("CHR-SC16-01"))
    try:
        import_export.preview_import(invalid_text)
        raised = False
    except import_export.MalformedImportError as e:
        raised = True
        msg = str(e)
    assert raised, "ein mild-pass/aber schema-ungueltiger Import muss VOR jedem Write gesperrt werden (SC16)."
    assert "Traceback" not in msg and "File \"" not in msg, "keine rohen Python-Tracebacks in der Importablehnung (SC17)."


def test_sc16_import_preview_accepts_fully_valid_save_positive_control():
    valid_text = json.dumps(full_v7_save("CHR-SC16-02", name="Flo"))
    preview = import_export.preview_import(valid_text)
    assert preview.char_id == "CHR-SC16-02"
    assert preview.single_char_ok is True


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failures = 0
    for fn in tests:
        try:
            fn()
            print(f"OK   {fn.__name__}")
        except Exception:
            failures += 1
            print(f"FAIL {fn.__name__}")
            traceback.print_exc()
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    sys.exit(1 if failures else 0)
