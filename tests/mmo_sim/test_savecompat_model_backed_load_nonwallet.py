#!/usr/bin/env python3
"""
tests/mmo_sim/test_savecompat_model_backed_load_nonwallet.py —
ZR-SCF-HYBRID-DURCHSTICH-20261017-R1, Pflichtgruppe `model_backed_load_
nonwallet` (02_KONKRETER_DURCHSTICH.md §A).

Ergaenzt (ersetzt NICHT) `test_savecompat_g7_real_subprocess_compat_load.py`
(jene Datei deckt NUR den Wallet-Fall ab, dort bewusst OFFLINE repariert,
s. deren Docstring). Diese Datei belegt die in Fix A NEU gebaute Bruecke
(`core.compat_load_service.build_compat_repair_fn`): eine NICHT-Wallet-
Strukturabweichung (typfalsches `lvl`, ein String statt einer Ganzzahl)
erreicht ueber den normalen Produktladeweg TATSAECHLICH die konfigurierte
SL (`gm_transport.turn()`), NICHT nur die lokale Wallet-Projektion.

`test_nonwallet_lvl_repair_real_new_process_and_followup_action` ist die in
SD-A.md verlangte Pflichtprobe:
  - konkrete NICHT-Wallet-Abweichung (`characters[0].lvl == "2"`, String),
  - bereitgestellte korrigierende SL-Antwort (kuenstlich NUR als letzte
    Provider-I/O am Prozessrand -- `_CompatRepairThenPlayGm.turn()` im
    ZWEITEN echten `python3`-Subprozess, exakt wie G7s `_OneShotValidPlayGm`),
  - normaler Produktladeweg (`TuiSession._cmd_local_round()` ->
    `_resolve_active_save()` -> `_apply_pending_compat_load()`) in einem
    ECHTEN NEUEN OS-Prozess (zweiter `subprocess.run`, andere PID),
  - tatsaechlich gezaehlter SL-Aufruf (`request_ledger`-Datensatz mit
    `role="save_compat_load_repair"`, `state="accounted"`),
  - gueltige Annahme (`current_save_after_resume` traegt den reparierten,
    jetzt schema-gueltigen Block),
  - echte Folgeaktion (EIN weiterer echter, gueltiger Spielturn NACH der
    Uebernahme -- derselbe Beleg wie G7s `play_gm_calls`).

`test_valid_save_direct_load_needs_no_sl_repair_zero_calls` ist die
geforderte Positivprobe (gueltiger Save, KEINE SL-Reparatur noetig) und
`test_unknown_outcome_blocks_without_second_physical_call` die geforderte
Probe fuer einen unbekannten Antwortausgang OHNE Zweitversand -- beide
direkt gegen `core.compat_load_service`/`core.save_compatibility`
(providerfrei, EIN zaehlendes Fake-Transportobjekt NUR am Provider-Rand
dieses Unit-Tests, KEIN Produktionscallback). `test_wallet_only_repair_
stays_local_no_sl_call` belegt zusaetzlich, dass die bestehende, wertgleiche
Wallet-Projektion (02.B) weiterhin VOR jedem Modellaufruf versucht wird --
G7/G8 selbst bleiben unveraendert (s. `worker/TEST-RESULTS.json`, separat
ausgefuehrt, 159/159 gruen inkl. G7/G8)."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.core import compat_load_service  # noqa: E402
from mmo_sim.core import request_ledger  # noqa: E402
from mmo_sim.core import save_compatibility as save_compat_core  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss import save_compatibility as save_compatibility_domain  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
PARTICIPANT_ID = "scfhybrid_nonwallet_participant"
CHAR_ID = "CHR-SCFHY-NW1"
TABLE_ID = f"local-{PARTICIPANT_ID}"
SECTION_ID = f"{TABLE_ID}-section"

_pa = argparse.ArgumentParser(add_help=False)
_pa.add_argument("--child", choices=["create_and_exhaust", "resume_and_play"])
_pa.add_argument("--base", type=Path)
_ARGS, _REMAINING = _pa.parse_known_args()


def _scripted_input(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


def _valid_save() -> dict:
    block = full_v7_save(CHAR_ID, name="Nyx", callsign="NYXOPS")
    block["economy"] = {"wallets": {}}
    return block


def _nonwallet_broken_block() -> dict:
    """Ein strukturell gueltiger v7-Block MIT typfalschem `lvl` (String
    statt Ganzzahl) fuer die EIGENE Figur -- das Wallet selbst bleibt ein
    bereits gueltiges leeres Objekt (`{}`), die wertgleiche Wallet-
    Projektion (02.B) kann diesen Fehler also NICHT beheben (sie kennt nur
    `economy.wallets.*`-Eintraege). Genau die in SD-A.md geforderte
    'konkrete NICHT-Wallet-Abweichung (z.B. typfalsches lvl)'."""
    block = full_v7_save(CHAR_ID, name="Nyx", callsign="NYXOPS")
    block["characters"][0]["lvl"] = "2"
    block["economy"] = {"wallets": {}}
    return block


def _nonwallet_broken_debrief_text() -> str:
    return (
        f"```json\n{json.dumps(_nonwallet_broken_block())}\n```\n"
        f"{COMPLETION_MARKER} table_id={TABLE_ID} section_id={SECTION_ID}"
    )


class _CreationGm:
    def __init__(self, save_block: dict):
        self.calls: list[tuple[int, str]] = []
        self._save_block = save_block

    def turn(self, idx, text):
        self.calls.append((idx, text))
        if len(self.calls) == 1:
            return {"content": "Wie beginnt deine Zeitreise?"}
        return {"content": "```json\n" + json.dumps(self._save_block) + "\n```"}


class _AlwaysBrokenLvlGm:
    """Analog G7s `_AlwaysBrokenWalletGm`, aber mit einer NICHT-Wallet-
    Abweichung: liefert bei JEDEM Aufruf (natuerlicher Abschlussturn UND
    alle drei Gruppen-Korrekturzusatzversuche) denselben typfalschen
    `lvl`-Block -- echtes, wiederholtes Scheitern des LAUFENDEN
    `save_correction`-Zyklus (der reagiert generisch auf jeden Schema-
    fehler, nicht nur Wallet-Fehler), danach schreibt die bereits
    bestehende `_write_compat_export_on_exhaustion`-Verdrahtung den
    Kompatibilitaetsumschlag -- derselbe Mechanismus wie G7, nur mit einer
    anderen konkreten Abweichung."""
    def __init__(self):
        self.calls: list[str] = []
        self.output_limit_tokens = 4000

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append(text)
        if len(self.calls) == 1:
            content = _nonwallet_broken_debrief_text()
        else:
            content = f"```json\n{json.dumps(_nonwallet_broken_block())}\n```"
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "nonwallet-fake"}


class _CompatRepairThenPlayGm:
    """Prozess 2: der ERSTE Aufruf trifft `core.compat_load_service`s
    SL-gestuetzte Reparaturbruecke (Fix A) -- erkennbar am unveraenderten
    `save_correction.build_correction_message`-Header "TECHNISCHE
    SPEICHERKORREKTUR" -- und liefert die bereitgestellte KORRIGIERENDE
    SL-Antwort (lvl jetzt echte Ganzzahl). JEDER WEITERE Aufruf ist der
    normale, nachfolgende echte Spielzug (G7-Muster `_OneShotValidPlayGm`).
    Kuenstliche Provider-I/O NUR an diesem Prozessrand -- kein
    Produktionscallback, kein Testdouble im Ladepfad selbst."""
    def __init__(self):
        self.calls: list[str] = []
        self.output_limit_tokens = 4000

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append(text)
        if len(self.calls) == 1 and "TECHNISCHE SPEICHERKORREKTUR" in text:
            fixed = full_v7_save(CHAR_ID, name="Nyx", callsign="NYXOPS", save_id="nonwallet-sl-repaired")
            fixed["economy"] = {"wallets": {}}
            content = "```json\n" + json.dumps(fixed) + "\n```"
        else:
            end = full_v7_save(CHAR_ID, name="Nyx", callsign="NYXOPS", save_id="nonwallet-after-process-switch")
            end["economy"] = {"wallets": {}}
            body = f"```json\n{json.dumps(end)}\n```"
            content = f"{body}\n{COMPLETION_MARKER} table_id={TABLE_ID} section_id={SECTION_ID}"
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "nonwallet-fake-2"}


def _session(base: Path, inputs: list[str], gm, shown: list) -> TuiSession:
    return TuiSession(
        base / "onboarding", base / "catalog", PARTICIPANT_ID, input_fn=_scripted_input(inputs),
        print_fn=shown.append, run_dir=base / "run", states_dir=base / "states", schema_path=_SCHEMA,
        gm_transport_factory=(lambda: gm) if gm is not None else None,
    )


def _child_create_and_exhaust(base: Path) -> dict:
    write_test_profile(base / "run")
    shown: list = []
    creation_gm = _CreationGm(_valid_save())
    session = _session(base, ["n", "Ich lande mitten im Rift.", "x"], creation_gm, shown)
    rc_creation = session.run()
    onboarding_state = onboarding.peek(base / "onboarding", PARTICIPANT_ID)

    shown2: list = []
    play_gm = _AlwaysBrokenLvlGm()
    session2 = TuiSession(
        base / "onboarding", base / "catalog", PARTICIPANT_ID,
        input_fn=_scripted_input(["Ich beginne die Erkundung des Suedfluegels.", "", "", "", ""]),
        print_fn=shown2.append, run_dir=base / "run", states_dir=base / "states", schema_path=_SCHEMA,
        gm_transport_factory=lambda: play_gm,
    )
    try:
        session2._cmd_local_round()
    except EndOfInput:
        pass

    base_dir = base / "run" / "save_compat"
    envelopes = []
    if base_dir.is_dir():
        for repair_dir in sorted(base_dir.iterdir()):
            versions = sorted((p for p in repair_dir.glob("*.json") if p.stem.isdigit()), key=lambda p: int(p.stem))
            if versions:
                envelopes.append(json.loads(versions[-1].read_text(encoding="utf-8")))

    current = core_store.load_current_save(
        base / "run", PARTICIPANT_ID, PersonaStateStore(schema_path=_SCHEMA), states_dir=base / "states",
    )
    return {
        "pid": os.getpid(), "rc_creation": rc_creation,
        "onboarding_status": onboarding_state.status if onboarding_state else None,
        "creation_gm_calls": len(creation_gm.calls),
        "play_gm_calls": len(play_gm.calls),
        "shown_play": shown2,
        "compat_envelopes": envelopes,
        "current_save_before_process_end": current,
    }


def _child_resume_and_play(base: Path) -> dict:
    shown: list = []
    play_gm = _CompatRepairThenPlayGm()
    session = TuiSession(
        base / "onboarding", base / "catalog", PARTICIPANT_ID,
        input_fn=_scripted_input(["Ich setze die Erkundung fort.", "", "", "", ""]),
        print_fn=shown.append, run_dir=base / "run", states_dir=base / "states", schema_path=_SCHEMA,
        gm_transport_factory=lambda: play_gm,
    )
    try:
        session._cmd_local_round()
    except EndOfInput:
        pass
    current = core_store.load_current_save(
        base / "run", PARTICIPANT_ID, PersonaStateStore(schema_path=_SCHEMA), states_dir=base / "states",
    )
    table = None
    try:
        table = core_store.Table.load(base / "run", TABLE_ID).status
    except (FileNotFoundError, ValueError, KeyError):
        pass
    ledger_records = request_ledger._all_records(base / "run")
    compat_repair_records = [r for r in ledger_records if r.get("role") == compat_load_service.ROLE_COMPAT_LOAD]
    return {
        "pid": os.getpid(), "shown": shown, "play_gm_calls": len(play_gm.calls),
        "play_gm_call_texts_head": [t[:40] for t in play_gm.calls],
        "current_save_after_resume": current, "table_status_after_resume": table,
        "compat_repair_ledger_records": compat_repair_records,
    }


def _child() -> None:
    base = _ARGS.base
    if _ARGS.child == "create_and_exhaust":
        rec = _child_create_and_exhaust(base)
    else:
        rec = _child_resume_and_play(base)
    print(json.dumps(rec, ensure_ascii=False))


def _run_subprocess(mode: str, base: Path, timeout: int = 60) -> dict:
    cmd = [sys.executable, str(Path(__file__).resolve()), "--child", mode, "--base", str(base)]
    env = {k: v for k, v in os.environ.items() if not any(x in k.upper() for x in ("TOKEN", "SECRET", "API_KEY"))}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    p = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=str(base), timeout=timeout)
    if p.returncode:
        raise RuntimeError(f"Kindprozess {mode!r} fehlgeschlagen (exit={p.returncode}): {p.stdout[-3000:]}\n{p.stderr[-3000:]}")
    return json.loads(p.stdout.strip().splitlines()[-1])


def test_nonwallet_lvl_repair_real_new_process_and_followup_action():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        (base / "run").mkdir(parents=True, exist_ok=True)

        r1 = _run_subprocess("create_and_exhaust", base)
        r2 = _run_subprocess("resume_and_play", base)

        assert r1["pid"] != r2["pid"], "Prozess 1 und Prozess 2 muessen ECHT verschiedene PIDs sein"
        assert r1["onboarding_status"] == "completed", r1
        assert r1["creation_gm_calls"] == 2
        assert r1["play_gm_calls"] == 4, (
            f"natuerlicher Abschlussturn + GENAU drei zusaetzliche Korrekturversuche erwartet, "
            f"beobachtet={r1['play_gm_calls']}"
        )
        assert len(r1["compat_envelopes"]) == 1, r1["compat_envelopes"]
        envelope = r1["compat_envelopes"][0]
        assert envelope["participant_id"] == PARTICIPANT_ID
        assert envelope["char_id"] == CHAR_ID
        assert envelope["canonical_import_eligible"] is False
        # die konkrete NICHT-Wallet-Abweichung muss im gesicherten Umschlag
        # tatsaechlich vorliegen (String statt Ganzzahl) -- sonst waere
        # dies versehentlich doch der schon durch G7 abgedeckte Wallet-Fall.
        best_or_last = envelope.get("best_view") or envelope.get("last_valid")
        assert isinstance(best_or_last["characters"][0]["lvl"], str), envelope

        # Prozess 2: GENAU ZWEI echte SL-Aufrufe -- (1) die neue SL-
        # gestuetzte Kompat-Reparaturbruecke (Fix A), (2) der normale
        # Folgespielzug NACH Uebernahme. Die Wallet-Projektion allein
        # haette den typfalschen `lvl` NICHT beheben koennen (02.B betrifft
        # ausschliesslich `economy.wallets.*`) -- ein `play_gm_calls == 1`
        # wie bei G7 waere hier also ein Fehlbeleg (lokale Reparatur ohne
        # echten Modellaufruf).
        assert r2["play_gm_calls"] == 2, (
            f"ein echter SL-Aufruf fuer die Kompat-Reparatur PLUS ein echter Folgespielzug erwartet, "
            f"beobachtet={r2['play_gm_calls']} ({r2['play_gm_call_texts_head']})"
        )
        assert "TECHNISCHE SPEICHERKORREKTUR" in r2["play_gm_call_texts_head"][0], r2["play_gm_call_texts_head"]
        assert "TECHNISCHE SPEICHERKORREKTUR" not in r2["play_gm_call_texts_head"][1], r2["play_gm_call_texts_head"]

        # tatsaechlich gezaehlter SL-Aufruf: EIN `request_ledger`-Datensatz
        # mit der dedizierten Rolle `save_compat_load_repair`, erfolgreich
        # abgerechnet (NICHT nur reserviert/gesendet).
        repair_records = r2["compat_repair_ledger_records"]
        assert len(repair_records) == 1, repair_records
        assert repair_records[0]["state"] == "accounted", repair_records
        assert repair_records[0]["error"] is None, repair_records
        assert repair_records[0]["participant"] == PARTICIPANT_ID, repair_records

        assert any(
            "Kompatibilitaetsladeweg" in p and "repariert und uebernommen" in p for p in r2["shown"]
        ), r2["shown"]
        assert r2["current_save_after_resume"] is not None
        assert r2["current_save_after_resume"]["save_id"] == "nonwallet-after-process-switch", r2
        assert r2["current_save_after_resume"]["characters"][0]["lvl"] == 1, (
            "nach echter SL-Reparatur UND echtem Folgespielzug muss lvl wieder eine gueltige Ganzzahl sein", r2
        )
        assert r2["table_status_after_resume"] == "closed", r2


def test_valid_save_direct_load_needs_no_sl_repair_zero_calls():
    """Positivprobe (SD-A.md): ein gueltiger Save braucht KEINE SL-
    Reparatur -- `attempt_compat_load` akzeptiert ihn direkt, `repair_fn`
    wird dabei UEBERHAUPT NICHT aufgerufen (kein Modellaufruf, keine
    Kosten)."""
    calls: list = []

    class _CountingGm:
        output_limit_tokens = 4000

        def turn(self, idx, text, output_limit_tokens=None):
            calls.append(text)
            raise AssertionError("repair_fn haette fuer einen bereits gueltigen Save NIE aufgerufen werden duerfen")

    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        run_dir.mkdir(parents=True)
        write_test_profile(run_dir)
        repair_key = "nonwallet-positive-probe"
        valid_block = _valid_save()
        envelope = save_compatibility_domain.build_compat_envelope(
            envelope_version=1, repair_key=repair_key, char_id=CHAR_ID, participant_id=PARTICIPANT_ID,
            operation_key="group", table_id=TABLE_ID, section_id=SECTION_ID, raw_responses=[],
            best_view=valid_block, last_valid=valid_block, created_ts=time.time(),
        )
        repair_fn = compat_load_service.build_compat_repair_fn(
            run_dir, repair_key=repair_key, char_id=CHAR_ID, participant_id=PARTICIPANT_ID,
            gm_transport=_CountingGm(), table_id=TABLE_ID, section_id=SECTION_ID,
        )
        outcome = save_compat_core.attempt_compat_load(
            run_dir, repair_key=repair_key, char_id=CHAR_ID, participant_id=PARTICIPANT_ID,
            states_dir=Path(td) / "states", schema_path=_SCHEMA, envelope=envelope, repair_fn=repair_fn,
        )
        assert outcome.status == "adopted", outcome
        assert len(calls) == 0, "gueltiger Save durfte keinen SL-Aufruf ausloesen"


def test_unknown_outcome_blocks_without_second_physical_call():
    """SD-A.md: 'kein stilles Resend bei unbekanntem Ausgang'. Simuliert
    einen bereits (nach einem fruehenn Crash) ERFOLGREICH abgerechneten,
    aber textlosen Request fuer GENAU die Operationsidentitaet, die die
    naechste Reparaturrunde verwenden wuerde (`role=save_compat_load_
    repair`, `turn_idx=1`, `participant=PARTICIPANT_ID`). `build_compat_
    repair_fn` darf dafuer KEINEN zweiten physischen Request absenden."""
    calls: list = []

    class _CountingGm:
        output_limit_tokens = 4000

        def turn(self, idx, text, output_limit_tokens=None):
            calls.append(text)
            return {"content": "sollte nie erreicht werden", "usage": {}}

    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        run_dir.mkdir(parents=True)
        write_test_profile(run_dir)
        repair_key = "nonwallet-unknown-outcome-probe"
        # Simuliert einen Datensatz, der bereits gesendet+abgerechnet wurde,
        # dessen Antworttext aber (Altformat/Verlust) nicht vorliegt --
        # exakt die von `request_ledger.find_answered_without_text`
        # erkannte Lage.
        request_id = request_ledger.begin(
            run_dir, role=compat_load_service.ROLE_COMPAT_LOAD, content="irrelevant", reserved_usd=0.01,
            turn_idx=1, participant=PARTICIPANT_ID, table_id=TABLE_ID, section_id=SECTION_ID,
        )
        request_ledger.finish_received(run_dir, request_id, usage={}, seconds=0.1, result_text=None)

        repair_fn = compat_load_service.build_compat_repair_fn(
            run_dir, repair_key=repair_key, char_id=CHAR_ID, participant_id=PARTICIPANT_ID,
            gm_transport=_CountingGm(), table_id=TABLE_ID, section_id=SECTION_ID,
        )
        result = repair_fn(_nonwallet_broken_block(), ["[binding:compat_load_open_issue] lvl ist kein int."])
        assert result is None, result
        assert len(calls) == 0, "ein unklarer Ausgang darf KEINEN zweiten physischen SL-Request ausloesen"


def test_wallet_only_repair_stays_local_no_sl_call():
    """G7/G8-Regressionsgrenze aus diesem Fix: eine REINE Wallet-Abweichung
    bleibt weiterhin lokal/wertgleich repariert (02.B), OHNE die neue
    SL-Bruecke je zu erreichen -- 'eindeutige wertgleiche Projektion bleibt
    lokal zulaessig, ohne unnoetige Modellkosten' (02_KONKRETER_DURCHSTICH.md
    §A)."""
    calls: list = []

    class _CountingGm:
        output_limit_tokens = 4000

        def turn(self, idx, text, output_limit_tokens=None):
            calls.append(text)
            raise AssertionError("eine reine Wallet-Abweichung haette lokal geloest werden muessen")

    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        run_dir.mkdir(parents=True)
        write_test_profile(run_dir)
        block = _valid_save()
        block["economy"] = {"wallets": {CHAR_ID: 240}}  # bloss-zahliges Wallet -- 02.B-Projektionsfall.
        repair_fn = compat_load_service.build_compat_repair_fn(
            run_dir, repair_key="nonwallet-wallet-priority-probe", char_id=CHAR_ID, participant_id=PARTICIPANT_ID,
            gm_transport=_CountingGm(), table_id=TABLE_ID, section_id=SECTION_ID,
        )
        repaired = repair_fn(block, ["[tolerant]/economy/wallets/" + CHAR_ID + ": is not of type 'object'"])
        assert repaired is not None
        assert repaired["economy"]["wallets"][CHAR_ID] == {"balance": 240}, repaired
        assert len(calls) == 0, "Wallet-Projektion darf keinen SL-Aufruf ausloesen"


if _ARGS.child:
    _child()
    raise SystemExit(0)


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
