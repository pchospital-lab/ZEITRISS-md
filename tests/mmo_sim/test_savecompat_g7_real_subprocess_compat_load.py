#!/usr/bin/env python3
"""
tests/mmo_sim/test_savecompat_g7_real_subprocess_compat_load.py —
ZR-SK-FINALISIERUNG-20261016-R1, Pflichtgruppe `new_process_compat_load_
and_play` (02_SAVEVERTRAG.md §D), ECHTER OS-Prozesswechsel.

Ergaenzt (ersetzt NICHT) `test_savecompat_new_process_compat_load_and_
play.py`: jene Datei beweist `core.save_compatibility.attempt_compat_load`
isoliert (direkter Funktionsaufruf, EIN Prozess) -- review/INTAKE.md
kritisiert zu Recht, dass damit kein echter OS-Prozesswechsel und kein
Aufruf ueber den normalen Spielerweg belegt ist. Diese Datei schliesst
genau diese Luecke, ueber den REALEN Consumer-Pfad:

  Prozess 1 (`--child create_and_exhaust`): echte SL-Erschaffung
  (`TuiSession._cmd_new_or_switch_character` -> `core.creation_service.
  run_admitted_creation_dialog`), danach eine echte erste Solo-Spielrunde
  (`TuiSession._cmd_local_round()` -> `core.app_service.run_play_session`
  -> `core.runtime.SectionRuntime.run_full_section`), deren Debrief-Wallet
  fuer die eigene Figur durchgehend ein bloss-zahliger (schema-ungueltiger)
  Wert bleibt -- weder die enge CU-only-Projektion des LAUFENDEN
  Korrekturzyklus (`core.save_correction.pursue_group_save_correction`)
  noch drei echte zusaetzliche SL-Ausgaben beheben das (bewusst: nur
  `currency`-Entfernung, kein Zahl->balance-Wrap, s. dessen eigener
  R12-SAVECOMPAT-Kommentar) -- ECHTES, wiederholtes Scheitern ueber alle
  drei Zusatzversuche, danach `_write_compat_export_on_exhaustion`
  (additive R-SCF-A-Verdrahtung) schreibt den Kompatibilitaetsumschlag.
  Prozess 1 endet (eigene PID, echter `sys.exit`).

  Prozess 2 (`--child resume_and_play`, ZWEITER echter `python3`-
  Subprozess, ANDERE PID): `TuiSession._cmd_local_round()` erneut --
  `_resolve_member` -> `_resolve_active_save` findet KEINEN kanonischen
  Current (Abschnitt nie erfolgreich geerntet) und greift additiv
  `_apply_pending_compat_load` (R-SCF-A) auf: findet den in Prozess 1
  geschriebenen Umschlag, repariert ihn OFFLINE (deterministische Wallet-
  Projektion, KEIN Modellaufruf -- ehrlich als Offline-Ersatz fuer die
  KI-SL benannt, s. `_offline_repair`-Docstring in `ui/tui.py`) VOR jeder
  abhaengigen Spielaktion, uebernimmt ihn atomar in den kanonischen Store
  -- und spielt danach eine ECHTE, GUELTIGE Spielrunde zu Ende (mindestens
  eine normale Spielaktion ueber Runtime/CLI, kein blosser Store-Readback).

Beide Kindprozesse sind `python3 <diese Datei> --child ... --base ...`
(subprocess.run, echte PIDs, echte Exitcodes) -- analog zum bereits
etablierten Muster in `test_i4_active_authority_subprocess.py`. Pure
Python, nur `assert`, echter Exitcode. Providerfrei (synthetisches
GM-Double, kein externer Modellaufruf, kein HTTP, keine Live-Modelle)."""
from __future__ import annotations

import argparse
import json
import os
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

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
PARTICIPANT_ID = "scfa_g7_participant"
CHAR_ID = "CHR-SCFA7-G7"
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
    block = full_v7_save(CHAR_ID, name="Rhea", callsign="RHEAOPS")
    block["economy"] = {"wallets": {}}
    return block


def _broken_block() -> dict:
    """Ein strukturell gueltiger v7-Block MIT bloss-zahligem Wallet fuer
    die EIGENE Figur -- schema-ungueltig (s. `test_savecompat_wallet_live_
    fixture_and_seed.py: numeric_wallet_rejected_by_strict_schema_
    directly`), aber von der engen CU-only-Projektion des laufenden
    Korrekturzyklus NICHT reparierbar."""
    block = full_v7_save(CHAR_ID, name="Rhea", callsign="RHEAOPS")
    block["economy"] = {"wallets": {CHAR_ID: 240}}
    return block


def _broken_debrief_text() -> str:
    return (
        f"```json\n{json.dumps(_broken_block())}\n```\n"
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


class _AlwaysBrokenWalletGm:
    """Liefert bei JEDEM Aufruf (natuerlicher Abschlussturn UND alle drei
    Gruppen-Korrekturzusatzversuche) denselben schema-ungueltigen Save-
    Block -- echtes, wiederholtes Scheitern, kein Mock des Korrektur-
    zyklus. NUR der ALLERERSTE (natuerliche) Turn traegt den Abschluss-
    marker (der ist es, der `store.complete_section`/die Marker-Pruefung
    im normalen Spielloop ueberhaupt erst ausloest); die drei Zusatz-
    Korrekturantworten gehen ueber `core.save_correction.send_correction_
    turn`, der NIE auf den Marker prueft (nur `harvest_extractor` auf den
    Blockinhalt) -- ein wiederholter Marker darin wuerde nur das sl_log
    unnoetig mit zusaetzlichen (fuer eine spaetere Resume-Erkennung
    irrelevanten) Markertreffern fuellen."""
    def __init__(self):
        self.calls: list[str] = []
        self.output_limit_tokens = 4000

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append(text)
        if len(self.calls) == 1:
            content = _broken_debrief_text()
        else:
            content = f"```json\n{json.dumps(_broken_block())}\n```"
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "g7-fake"}


class _OneShotValidPlayGm:
    """Prozess 2: EINE normale Spielaktion, die diesmal ein gueltiges
    Wallet liefert (die Figur, deren Kompatibilitaetsstand gerade erst
    repariert/uebernommen wurde, spielt tatsaechlich weiter)."""
    def __init__(self):
        self.calls: list[str] = []
        self.output_limit_tokens = 4000

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append(text)
        end = full_v7_save(CHAR_ID, name="Rhea", callsign="RHEAOPS", save_id="g7-after-real-process-switch")
        end["economy"] = {"wallets": {}}
        body = f"```json\n{json.dumps(end)}\n```"
        content = f"{body}\n{COMPLETION_MARKER} table_id={TABLE_ID} section_id={SECTION_ID}"
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "g7-fake-2"}


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
    play_gm = _AlwaysBrokenWalletGm()
    session2 = TuiSession(
        base / "onboarding", base / "catalog", PARTICIPANT_ID,
        input_fn=_scripted_input(["Ich beginne die Erkundung des Nordfluegels.", "", "", "", ""]),
        print_fn=shown2.append, run_dir=base / "run", states_dir=base / "states", schema_path=_SCHEMA,
        gm_transport_factory=lambda: play_gm,
    )
    try:
        session2._cmd_local_round()
    except EndOfInput:
        pass

    from mmo_sim.core import save_compatibility as save_compat_core
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
        "shown_creation": shown, "shown_play": shown2,
        "compat_envelopes": envelopes,
        "current_save_before_process_end": current,
    }


def _child_resume_and_play(base: Path) -> dict:
    shown: list = []
    play_gm = _OneShotValidPlayGm()
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
    return {
        "pid": os.getpid(), "shown": shown, "play_gm_calls": len(play_gm.calls),
        "current_save_after_resume": current, "table_status_after_resume": table,
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


def test_g7_real_two_process_compat_load_and_play():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        (base / "run").mkdir(parents=True, exist_ok=True)

        r1 = _run_subprocess("create_and_exhaust", base)
        r2 = _run_subprocess("resume_and_play", base)

        assert r1["pid"] != r2["pid"], "Prozess 1 und Prozess 2 muessen ECHT verschiedene PIDs sein"
        assert r1["onboarding_status"] == "completed", r1
        assert r1["creation_gm_calls"] == 2, "echte Erschaffung: Frage + gueltige Antwort"
        assert r1["play_gm_calls"] == 4, (
            f"natuerlicher Abschlussturn + GENAU drei zusaetzliche Korrekturversuche erwartet, "
            f"beobachtet={r1['play_gm_calls']}"
        )
        # Die Erschaffung selbst veroeffentlicht bereits einen kanonischen
        # Current (`_finish_new_character_creation`) -- der spaeter
        # gescheiterte ERSTE Abschnitt aendert diesen (noch gueltigen,
        # aelteren) Stand NICHT; der neue Kompatibilitaetsstand liegt
        # SEPARAT daneben (02.D: "Kompatibilitaetsexport und letzter valider
        # Stand bleiben erhalten").
        assert r1["current_save_before_process_end"]["save_id"] == "fixture-CHR-SCFA7-G7", r1
        assert len(r1["compat_envelopes"]) == 1, r1["compat_envelopes"]
        envelope = r1["compat_envelopes"][0]
        assert envelope["participant_id"] == PARTICIPANT_ID
        assert envelope["char_id"] == CHAR_ID
        assert envelope["canonical_import_eligible"] is False
        assert any("Runde 3" in p for p in r1["shown_play"]), r1["shown_play"]
        assert any("Abschnitt nicht abgeschlossen" in p and "kann fortgesetzt werden" in p for p in r1["shown_play"]), \
            r1["shown_play"]

        assert r2["play_gm_calls"] == 1, (
            f"NACH erfolgreicher Kompat-Uebernahme genuegt EIN echter, gueltiger Spielturn -- "
            f"beobachtet={r2['play_gm_calls']}"
        )
        assert any("Kompatibilitaetsladeweg" in p and "repariert und uebernommen" in p for p in r2["shown"]), r2["shown"]
        assert r2["current_save_after_resume"] is not None, "nach Prozess 2 muss ein kanonischer Current lesbar sein"
        assert r2["current_save_after_resume"]["save_id"] == "g7-after-real-process-switch", r2
        assert r2["current_save_after_resume"]["economy"]["wallets"] == {}, r2["current_save_after_resume"]
        assert r2["table_status_after_resume"] == "closed", r2


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
