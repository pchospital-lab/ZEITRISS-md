#!/usr/bin/env python3
"""
tests/mmo_sim/test_section_completion_resume_two_process_crash.py —
R12-AUTORECOVERY/AR2: CASES.json AR03 (Prozessabbruch -- echter Prozess-
wechsel, kein Mock-Return) UND AR12/M1 (BASE/FIX-Diskriminierung mit
IDENTISCHEN Fixtures, jetzt portabel ohne harte Sibling-Pfad-Annahme).

AR2-Korrektur (01_ABSCHLUSSVERTRAG.md Teil A, GENERALREVIEW.md,
PRE-LEDGER-CRASH-OBSERVATIONS.json): der bisher hier als "positiver
Nach-Ledger-Crash" bezeichnete Zweiprozesslauf (`process1`/`process2`) ist
tatsaechlich ein VOR-Ledger-Crash -- `process1` beendet sich hart INNERHALB
von `store.submit_to_sl` (die Rohantwort ist bereits durabel im `sl_log`),
aber NOCH VOR `request_ledger.finish_received`: der zugehoerige GM-Request
bleibt dauerhaft `state=sent`, nie `accounted`. Unter dem FIX muss `process2`
das jetzt als KONTROLLIERTEN HOLD sehen (keine Ernte/Reflexion/Finalisierung,
kein Refund, keine neue Anfrage) -- NICHT mehr als erfolgreiche automatische
Recovery (das war genau der AR04/AR05-Bruch, s. CONTRACT-OBSERVATIONS.json
Fall `request_sent`).

Ein EIGENER, echter POSITIVER Nach-Ledger-Crash wird zusaetzlich ueber
`process3`/`process4` abgedeckt: `process3` beendet sich hart ERST NACHDEM
`request_ledger.finish_received` durabel auf `state=accounted` (inkl.
`result_text`) uebergegangen ist -- NOCH VOR `marker_hit(...)`/Plan-Pinnung.
Unter dem FIX muss `process4` das jetzt als normale automatische Recovery
sehen (null neue GM-/Spielzug-Anfragen, Pflichtreflexion, finaler Abschluss).

M1-Korrektur (FINDINGS.json, m1_clean_checkout.std{out,err}): die beiden
FIX-Prozessphasen (oben) laufen IMMER in jedem normalen Checkout. Der
zusaetzliche historische BASE/FIX-Vergleich (AR12) ist NUR noch optional,
ueber eine EXPLIZITE Env-Variable (`AR2_HISTORICAL_BASE_ROOT`) aktivierbar --
kein fester `../base-source/candidate`-Pfad mehr als CI-Voraussetzung. Nicht
gesetzt => dieser eine historische Teiltest wird sichtbar als SKIP markiert
(NICHT als PASS gezaehlt, Script-RC bleibt davon unberuehrt). Gesetzt, aber
der Pfad fehlt/ist kein gueltiger candidate-Baum => Fehler (kein stilles
SKIP) -- echte, gebundene Originalbytes oder gar nichts.

Pure Python, nur `assert`, echter Exitcode, kein pytest."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_FIX_REPO_ROOT = _HERE.parents[1]

# M1 (AR2 Teil D): KEIN fester Sibling-Pfad mehr -- nur noch ein expliziter,
# optionaler Opt-in. Siehe `_resolve_historical_base_root()`.
_BASE_ROOT_ENV = "AR2_HISTORICAL_BASE_ROOT"

_PROCESS_SCRIPT = r"""
import json, os, sys
from pathlib import Path
sys.path.insert(0, {repo_root!r})
sys.path.insert(0, {fixtures_dir!r})

import mmo_sim.core.store as store
import mmo_sim.core.request_ledger as request_ledger
from mmo_sim.adapters.base import ParticipantDecision
from mmo_sim.core.admission import write_test_profile
from mmo_sim.core.controller import TableController
from mmo_sim.core.runtime import SectionRuntime
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy
from mmo_sim.core.persona_state import PersonaStateStore
from _full_v7_fixture import full_v7_save

COMPLETION_MARKER = "SECTION-ABSCHLUSS-BESTAETIGT"
run_dir = Path({run_dir!r})
states_dir = Path({states_dir!r})
schema_path = Path({schema_path!r})
role = {role!r}
table_id = {table_id!r}
section_id = {section_id!r}

leader_save = full_v7_save("chrono-ar03", name="Testfigur")
debrief = "Abschnitt beendet.\n```json\n" + json.dumps(leader_save) + "\n```\n" + COMPLETION_MARKER


def harvest_extractor(debrief_text, cid_to_pk):
    from mmo_sim.domain.zeitriss import saves as zeitriss_saves
    out = {{}}
    for blk in zeitriss_saves.extract_all_saves(debrief_text):
        cid = zeitriss_saves.block_char_id(blk)
        pk = cid_to_pk.get(cid) if cid else None
        if pk is not None and zeitriss_saves.single_character_count(blk) == 1 and pk not in out:
            out[pk] = blk
    return out


def _seed_first_process():
    schema_path.write_text(
        '{{"type":"object","required":["v","persona_key","rounds_played"],'
        '"properties":{{"v":{{"const":2}}}}}}',
        encoding="utf-8",
    )
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    ps_store.save_state("leader_pk", {{
        "v": 2, "persona_key": "leader_pk", "rounds_played": 0,
        "plays_char": {{"character_id": "chrono-ar03", "name": "Testfigur"}},
    }}, states_dir=states_dir)

    lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    lobby.join("leader_pk")
    table, derivation = store.create_table_from_offer_log(
        lobby, table_id,
        offer_log_events=[{{"type": "offer", "id": "o1", "from": "leader_pk", "wants": []}}],
        chrononaut_ids={{"leader_pk": "chrono-ar03"}},
    )
    assert table is not None, derivation
    write_test_profile(run_dir)
    return lobby, table, ps_store


class _OneShotGm:
    def turn(self, turn_idx, user_text, **kwargs):
        return {{"content": debrief, "usage": {{}}, "sources": [], "latency_s": 0.0, "chat_id": "chat-0"}}


class _OneShotDriver:
    def decide(self, context):
        return ParticipantDecision(text="Anker-Text.", save_payload=leader_save, origin_source="fake:leader")


class _ExplodingGm:
    def __init__(self):
        self.calls = 0

    def turn(self, turn_idx, user_text, **kwargs):
        self.calls += 1
        raise AssertionError("BUG: ein neuer GM-Turn wurde nach einem Auto-Recovery-Kandidaten ausgeloest.")


class _ExplodingDriverExceptReflection:
    def __init__(self):
        self.non_reflection_calls = 0
        self.reflection_calls = 0

    def decide(self, context):
        if context.get("system") == "PRIVATE_REFLECTION_SENTINEL":
            self.reflection_calls += 1
            return ParticipantDecision(text="Reflexion nach Recovery.", origin_source="fake:leader-reflect")
        self.non_reflection_calls += 1
        raise AssertionError("BUG: eine neue Spielzug-Entscheidung wurde nach Prozessabbruch angefragt.")


def _run_second_process():
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    table = store.Table.load(run_dir, table_id)

    gm2 = _ExplodingGm()
    driver2 = _ExplodingDriverExceptReflection()
    controller2 = TableController(leader_key="leader_pk", drivers={{"leader_pk": driver2}})
    runtime2 = SectionRuntime(
        lobby=lobby, table=table, gm_transport=gm2, marker=COMPLETION_MARKER,
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        harvest_extractor=harvest_extractor,
    )
    bug_triggered = False
    outcome = None
    try:
        outcome = runtime2.run_full_section(
            controller2, section_id,
            contexts_by_persona={{"leader_pk": {{"user": "ctx"}}}},
            states_dir=states_dir, today="2026-10-12", ts="2026-10-12T10:05:00",
        )
    except AssertionError:
        bug_triggered = True
    print(json.dumps({{
        "bug_triggered": bug_triggered,
        "gm_calls": gm2.calls,
        "non_reflection_calls": driver2.non_reflection_calls,
        "reflection_calls": driver2.reflection_calls,
        "success": (outcome.completion.success if outcome is not None else None),
        "reason": (outcome.completion.reason if outcome is not None else None),
        "members_completed": (outcome.completion.members_completed if outcome is not None else None),
    }}))


if role == "process1":
    # AR2/Vor-Ledger-Fenster: haertester Absturz DIREKT nach dem durablen
    # sl_log-Persist, aber VOR request_ledger.finish_received -- der
    # zugehoerige GM-Request bleibt dauerhaft 'sent'.
    lobby, table, ps_store = _seed_first_process()
    _original_submit_to_sl = store.submit_to_sl

    def _hard_kill_after_durable_persist(*args, **kwargs):
        result = _original_submit_to_sl(*args, **kwargs)
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(90)

    store.submit_to_sl = _hard_kill_after_durable_persist
    controller = TableController(leader_key="leader_pk", drivers={{"leader_pk": _OneShotDriver()}})
    runtime = SectionRuntime(
        lobby=lobby, table=table, gm_transport=_OneShotGm(), marker=COMPLETION_MARKER,
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        harvest_extractor=harvest_extractor,
    )
    runtime.run_full_section(
        controller, section_id,
        contexts_by_persona={{"leader_pk": {{"user": "ctx"}}}},
        states_dir=states_dir, today="2026-10-12", ts="2026-10-12T10:00:00",
    )
    print(json.dumps({{"unexpected_normal_return": True}}))

elif role == "process2":
    _run_second_process()

elif role == "process3":
    # AR2/echter Nach-Ledger-Crash: der Absturz erfolgt ERST NACHDEM
    # request_ledger.finish_received durabel auf state=accounted (inkl.
    # result_text) uebergegangen ist -- NOCH VOR marker_hit(...)/Plan.
    lobby, table, ps_store = _seed_first_process()
    _original_finish_received = request_ledger.finish_received

    def _hard_kill_after_ledger_accounted(run_dir_arg, request_id, **kwargs):
        # NUR der GM-Turn-Request ist das hier gesuchte Fenster -- der
        # vorgelagerte persona_decision-Request (Anker-Entscheidung, laeuft
        # VOR dem eigentlichen GM-Turn durch denselben Requestweg) muss ganz
        # normal durchlaufen, sonst stuerbe der Prozess bereits VOR dem
        # GM-Turn selbst ab (falsches Fenster).
        _original_finish_received(run_dir_arg, request_id, **kwargs)
        record = request_ledger.load_request(run_dir_arg, request_id)
        if record is not None and record.get("role") == "gm_turn":
            sys.stdout.flush()
            sys.stderr.flush()
            os._exit(91)

    request_ledger.finish_received = _hard_kill_after_ledger_accounted
    controller = TableController(leader_key="leader_pk", drivers={{"leader_pk": _OneShotDriver()}})
    runtime = SectionRuntime(
        lobby=lobby, table=table, gm_transport=_OneShotGm(), marker=COMPLETION_MARKER,
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        harvest_extractor=harvest_extractor,
    )
    runtime.run_full_section(
        controller, section_id,
        contexts_by_persona={{"leader_pk": {{"user": "ctx"}}}},
        states_dir=states_dir, today="2026-10-12", ts="2026-10-12T10:00:00",
    )
    print(json.dumps({{"unexpected_normal_return": True}}))

elif role == "process4":
    _run_second_process()
"""


def _resolve_historical_base_root() -> Path | None:
    """M1 (01_ABSCHLUSSVERTRAG.md Teil D): liefert den konfigurierten
    historischen BASE-Baum NUR ueber die explizite Env-Variable
    `AR2_HISTORICAL_BASE_ROOT` -- kein fester `../base-source/candidate`-
    Sibling-Pfad mehr. `None` (Variable nicht gesetzt) ist der normale,
    erlaubte Default -- der Aufrufer meldet dann sichtbar SKIP fuer NUR den
    historischen Diskriminierungstest, zaehlt das aber NICHT als PASS.

    Ist die Variable gesetzt, MUSS sie auf einen echten `candidate`-Baum
    zeigen (hier geprueft ueber `mmo_sim/core/store.py`, dieselbe Datei, die
    dieser Test tatsaechlich importiert) -- ein fehlender/falscher Pfad ist
    dann ein Fehler (`RuntimeError`), NIEMALS ein stilles SKIP (explizit
    konfiguriert, aber falsch == Fehler, nicht uebersprungen)."""
    raw = os.environ.get(_BASE_ROOT_ENV)
    if raw is None or raw.strip() == "":
        return None
    root = Path(raw).resolve()
    marker_file = root / "mmo_sim" / "core" / "store.py"
    if not marker_file.is_file():
        raise RuntimeError(
            f"{_BASE_ROOT_ENV}={raw!r} ist gesetzt, aber unter diesem Pfad liegt kein "
            f"gueltiger candidate-Baum ({marker_file} fehlt) -- explizit konfiguriert, "
            "aber fehlend/falsch ist ein Fehler, kein SKIP (M1)."
        )
    return root


def _run_two_process_scenario(
    repo_root: Path, *, table_id: str, section_id: str, first_role: str, second_role: str, expected_first_rc: int,
) -> dict:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        states_dir = root / "states"
        states_dir.mkdir(parents=True)
        schema_path = root / "schema.json"

        script = _PROCESS_SCRIPT.format(
            repo_root=str(repo_root), fixtures_dir=str(_HERE),
            run_dir=str(run_dir), states_dir=str(states_dir), schema_path=str(schema_path),
            role=first_role, table_id=table_id, section_id=section_id,
        )
        env = dict(os.environ)
        env.pop("PYTHONPATH", None)
        proc1 = subprocess.run([sys.executable, "-B", "-c", script], env=env, capture_output=True, text=True, timeout=60)
        assert proc1.returncode == expected_first_rc, (
            f"Prozess 1 ({first_role}) muss rc{expected_first_rc} liefern -- "
            f"rc={proc1.returncode} stdout={proc1.stdout!r} stderr={proc1.stderr!r}"
        )
        table_path = run_dir / "tables" / f"{table_id}.json"
        assert table_path.exists(), "Rohantwort/Tisch sollten bereits durabel persistiert sein."
        persisted = json.loads(table_path.read_text(encoding="utf-8"))
        assert len(persisted["sl_log"]) == 1 and "SECTION-ABSCHLUSS-BESTAETIGT" in persisted["sl_log"][0]["content"]
        plan_path = run_dir / "completion" / f"{section_id}__plan.json"
        assert not plan_path.exists(), "VOR Prozess 2 darf noch KEIN Completion-Plan existieren (das ist die Luecke)."

        # Dieselbe Anker-Entscheidung laeuft auch ueber einen persistenten
        # Requestdatensatz (role=persona_decision) -- NUR der role=gm_turn
        # Datensatz ist das hier gesuchte Vor-/Nach-Ledger-Fenster.
        request_files = sorted((run_dir / "requests").glob("*.json"))
        gm_request_paths = [
            p for p in request_files if json.loads(p.read_text(encoding="utf-8")).get("role") == "gm_turn"
        ]
        assert len(gm_request_paths) == 1, (request_files, gm_request_paths)
        gm_request_path = gm_request_paths[0]
        gm_request_before = json.loads(gm_request_path.read_text(encoding="utf-8"))

        script2 = _PROCESS_SCRIPT.format(
            repo_root=str(repo_root), fixtures_dir=str(_HERE),
            run_dir=str(run_dir), states_dir=str(states_dir), schema_path=str(schema_path),
            role=second_role, table_id=table_id, section_id=section_id,
        )
        proc2 = subprocess.run([sys.executable, "-B", "-c", script2], env=env, capture_output=True, text=True, timeout=60)
        assert proc2.returncode == 0, (
            f"Prozess 2 ({second_role}) muss rc0 liefern (AssertionError wird selbst abgefangen/berichtet) -- "
            f"rc={proc2.returncode} stdout={proc2.stdout!r} stderr={proc2.stderr!r}"
        )
        payload = json.loads(proc2.stdout.strip().splitlines()[-1])
        gm_request_after = json.loads(gm_request_path.read_text(encoding="utf-8")) if gm_request_path.exists() else None
        return {
            "proc1": proc1, "proc2": proc2, "payload": payload,
            "gm_request_before": gm_request_before, "gm_request_after": gm_request_after,
            "run_dir": run_dir,
        }


def test_ar03_pre_ledger_crash_holds_without_new_turn_or_harvest():
    """AR03/AR04/AR05 (korrigiert, GENERALREVIEW.md): der Absturz liegt VOR
    `request_ledger.finish_received` -- der GM-Request bleibt dauerhaft
    `state=sent`. Unter dem FIX ist das ein kontrollierter HOLD: kein neuer
    GM-Turn, keine neue Spielzug-Entscheidung, KEINE Ernte/Reflexion/
    Finalisierung, kein Refund/Settlement, der Request bleibt unveraendert
    `sent`. Dies ist bewusst die VOR-Ledger-NEGATIVPROBE -- sie darf nicht
    (mehr) als erfolgreiche Recovery bezeichnet/erwartet werden."""
    result = _run_two_process_scenario(
        _FIX_REPO_ROOT, table_id="t-ar03-crash-preledger", section_id="t-ar03-crash-preledger-section",
        first_role="process1", second_role="process2", expected_first_rc=90,
    )
    payload = result["payload"]
    assert payload["bug_triggered"] is False, payload
    assert payload["gm_calls"] == 0, "kein neuer GM-Turn -- " + repr(payload)
    assert payload["non_reflection_calls"] == 0, "keine neue Spielzug-Entscheidung -- " + repr(payload)
    assert payload["reflection_calls"] == 0, "keine Pflichtreflexion vor einem gueltigen Abschluss -- " + repr(payload)
    assert payload["success"] is False, (
        "Vor-Ledger-Fenster (Request bleibt 'sent') MUSS HOLD sein, keine automatische Recovery -- " + repr(payload)
    )
    assert payload["members_completed"] in (None, []), payload

    assert result["gm_request_before"]["state"] == "sent"
    assert result["gm_request_after"] is not None, "Requestdatensatz darf durch den HOLD nicht verschwinden."
    assert result["gm_request_after"]["state"] == "sent", (
        "HOLD darf den haengenden Request NICHT nachtraeglich buchen/veraendern -- "
        f"{result['gm_request_after']!r}"
    )
    assert result["gm_request_after"]["error"] is None, "kein erfundener Fehler/Refund fuer den haengenden Request."
    plan_path = result["run_dir"] / "completion" / "t-ar03-crash-preledger-section__plan.json"
    assert not plan_path.exists(), "HOLD darf keinen Completion-Plan pinnen."


def test_ar03_post_ledger_crash_auto_recovers():
    """AR2 (eigener, echter POSITIVER Nach-Ledger-Crash, 01_ABSCHLUSSVERTRAG.md
    Teil A, zweite Crashgrenze Fall 1): der Absturz liegt NACH einem
    dauerhaft erfolgreichen, fehlerfreien `request_ledger.finish_received`
    (state=accounted, `result_text` gesetzt) -- NOCH VOR Marker-Pruefung/
    Plan-Pinnung. Die normale automatische Recovery MUSS hier funktionieren:
    kein neuer GM-/Spielzug-Call, Pflichtreflexion, erfolgreicher Abschluss."""
    result = _run_two_process_scenario(
        _FIX_REPO_ROOT, table_id="t-ar03-crash-postledger", section_id="t-ar03-crash-postledger-section",
        first_role="process3", second_role="process4", expected_first_rc=91,
    )
    payload = result["payload"]
    assert result["gm_request_before"]["state"] == "accounted"
    assert result["gm_request_before"]["error"] is None
    assert result["gm_request_before"]["result_text"], "Original-Antworttext muss bereits durabel gebunden sein."

    assert payload["bug_triggered"] is False, payload
    assert payload["gm_calls"] == 0, "FIX: kein neuer GM-Turn nach vollstaendigem Ledger-Abschluss -- " + repr(payload)
    assert payload["non_reflection_calls"] == 0, "FIX: keine neue Spielzug-Entscheidung -- " + repr(payload)
    assert payload["reflection_calls"] == 1, "FIX: genau die weiterhin faellige Pflichtreflexion -- " + repr(payload)
    assert payload["success"] is True, payload
    assert payload["members_completed"] == ["leader_pk"], payload


def test_ar12_m1_historical_base_discrimination_explicit_opt_in():
    """M1 (korrigiert): der historische BASE/FIX-Vergleich ist NUR noch ein
    optionaler, explizit konfigurierbarer Zusatztest -- s.
    `_resolve_historical_base_root()`-Docstring. OHNE `AR2_HISTORICAL_BASE_
    ROOT` wird NUR dieser eine historische Teil sichtbar uebersprungen
    (SKIP, kein PASS); die beiden FIX-Pflichttests oben liefen bereits
    regulaer und unabhaengig davon."""
    base_root = _resolve_historical_base_root()
    if base_root is None:
        print(
            f"SKIP test_ar12_m1_historical_base_discrimination_explicit_opt_in: "
            f"{_BASE_ROOT_ENV} nicht gesetzt -- NUR der optionale historische "
            "BASE/FIX-Vergleich wird uebersprungen (kein PASS), die FIX-Pflichttests "
            "liefen bereits regulaer."
        )
        return "skipped"
    result = _run_two_process_scenario(
        base_root, table_id="t-ar03-crash-preledger-base", section_id="t-ar03-crash-preledger-base-section",
        first_role="process1", second_role="process2", expected_first_rc=90,
    )
    payload = result["payload"]
    assert payload["bug_triggered"] is True or payload["gm_calls"] > 0 or payload["non_reflection_calls"] > 0 or payload["success"] is True, (
        "M1: der unveraenderte historische BASE-Baum sollte das urspruengliche AR03-"
        "Fehlverhalten zeigen (faelschliche automatische Ernte eines Vor-Ledger-"
        "Fensters, statt es als HOLD zu behandeln) -- " + repr(payload)
    )
    return "passed"


def main() -> int:
    tests = [
        test_ar03_pre_ledger_crash_holds_without_new_turn_or_harvest,
        test_ar03_post_ledger_crash_auto_recovers,
        test_ar12_m1_historical_base_discrimination_explicit_opt_in,
    ]
    passed = 0
    skipped = 0
    failed = 0
    for t in tests:
        try:
            outcome = t()
            if outcome == "skipped":
                skipped += 1
                print(f"SKIP {t.__name__}")
            else:
                passed += 1
                print(f"OK   {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR {t.__name__}:")
            traceback.print_exc()
    print(f"\n{passed}/{len(tests)} Tests bestanden, {skipped} uebersprungen (SKIP, kein PASS), {failed} fehlgeschlagen.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
