#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_r06_adapter_pending_completion_restart_2026_10_05.py
— W14/R06 (UX13, CASE-REVIEW.json "Zweiprozess-Tischresume bestaetigt;
pending completion nicht dadurch mitbewiesen"): Pause/Neustart WAEHREND
eines unaufgeloesten `completion_order`-Zustands (`__plan.json` ohne
`__final.json`, `core/store.py:complete_section`/`finalize_section_after_
reflection`) -- nicht nur eines gebundenen, laufenden (noch unabgeschlossenen)
Tisches, den `test_ux1_g03_same_authority_resume_2026_10_05.py::
test_p09_real_os_restart_resumes_same_bound_table_no_doppelcall` bereits
real belegt.

Szenario (zwei ECHTE, getrennte OS-Subprozesse, Muster/Bausteine 1:1 aus
`test_ux1_g03_same_authority_resume_2026_10_05.py` wiederverwendet --
`_make_ready`, `_queued_input`, `_FIX`/`_SCHEMA`, `_run_child`-Subprozess-
Technik -- kein neues Fake, keine neue Engine):

Prozess 1: Mensch-Leader 'sniper' + KI-Gast 'tech' (wie P09). Der GM
schliesst den Abschnitt SOFORT (Completion-Marker) -- `complete_section()`
erntet die Saves erfolgreich (Phase 1, `__plan.json` wird geschrieben),
aber `tech`s PFLICHT-Reflexion schlaegt real fehl (der Persona-Treiber wirft
beim Reflexionsturn, simuliert einen Absturz/Verbindungsabbruch GENAU an
dieser Stelle) -- `finalize()` haelt den Abschnitt deshalb bewusst offen
(`reflections_ok=False`, s. `core/runtime.py:finalize`): KEIN `__final.json`,
Tisch bleibt NICHT `closed`. Das ist der reale "pending Abschluss"-Zustand.

Prozess 2 (neue OS-PID, `_cmd_menu_fortsetzen`): derselbe Tisch wird
fortgesetzt. Kernnachweis:
  (1) KEIN zweiter GM-/SL-Request (`core/runtime.py:run_section` erkennt
      den offenen Abschluss-Auftrag VOR jedem `act()`/Spielzug und springt
      direkt zu `finalize(resume_section_id=...)` -- der GM-Fake in Prozess
      2 wirft, wenn er UEBERHAUPT aufgerufen wird).
  (2) KEINE erneute Einladungs-/Consent-Anfrage an 'tech' (Mitgliedschaft
      bereits real gebunden) -- derselbe Doppelcall-Beleg wie P09
      (`forbid_invite`-Driver wirft bei jedem erneuten `decision_contract`).
  (3) KEINE Doppelpublikation: genau EIN `kind=ai_required_reflection`-
      Archiveintrag fuer 'tech'/diese section_id (nicht zwei), `__final.json`
      entsteht jetzt real, Tisch wird `closed`, Chrononaut-Locks beider
      Mitglieder freigegeben.
  (4) Die Einladungs-/Consent-Logdatei bleibt BYTEGLEICH (kein neuer
      Eintrag durch den Resume selbst)."""
from __future__ import annotations

import argparse
import json
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

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

import test_ux1_g03_same_authority_resume_2026_10_05 as g03  # noqa: E402


class _TechReflectionFailsOnceDriver:
    """KI-Gast 'tech': nimmt die Einladung an (identischer Vertrag wie
    `g03._TechDriver`). Beim PFLICHT-Reflexionsturn (`context['system'] ==
    'PRIVATE_REFLECTION_SENTINEL'`) wirft er GENAU EINMAL (simuliert einen
    echten Absturz/Verbindungsabbruch an dieser Stelle, s. `core/runtime.py:
    _collect_reflections`s `except Exception as exc: ok=False`) -- jeder
    WEITERE Aufruf (Retry nach Resume) liefert eine echte Antwort.
    `forbid_invite=True` laesst einen ERNEUTEN Einladungs-/Consent-Request
    fehlschlagen (Doppelcall-Beleg, identisch zu P09)."""

    def __init__(self, forbid_invite: bool = False, fail_reflection_once: bool = False):
        self.forbid_invite = forbid_invite
        self.fail_reflection_once = fail_reflection_once
        self._reflection_failed_already = False
        self.calls: list[dict] = []
        self.reflection_calls = 0

    def decide(self, ctx: dict) -> ParticipantDecision:
        self.calls.append(ctx)
        if ctx.get("system") == "PRIVATE_REFLECTION_SENTINEL":
            self.reflection_calls += 1
            if self.fail_reflection_once and not self._reflection_failed_already:
                self._reflection_failed_already = True
                raise RuntimeError("SYNTHETIC_RECOVERABLE_REFLECTION_FAILURE (simulierter Absturz)")
            return ParticipantDecision(
                text="Ich habe aus diesem Abschnitt gelernt, aufmerksamer zu sein.",
                origin_source="g03-p09-test:tech",
            )
        if "decision_contract" in ctx:
            if self.forbid_invite:
                raise AssertionError("UX13: verbotener erneuter Einladungs-/Consent-Request an 'tech' beim Resume")
            dc = ctx["decision_contract"]
            text = f"ENTSCHEIDUNG offer_id={dc['offer_id']} participant_id={dc['participant_id']} decision=accept"
            return ParticipantDecision(text=text, origin_source="g03-p09-test:tech")
        return ParticipantDecision(text="SYNTHETIC: Wir beobachten und helfen am Tisch.", origin_source="g03-p09-test:tech")


class _ImmediateCompletingGm:
    """Liefert SOFORT (jeder Aufruf) den Abschlussmarker samt beider
    finaler Saves -- der Leader-Ankerzug loest die Harvest-Phase (Phase 1,
    `__plan.json`) direkt aus, OHNE dass 'tech' je einen Spielzug-Import
    braucht (Tischmitgliedschaft reicht fuer die Pflicht-Reflexionspflicht,
    s. `core/runtime.py:_collect_reflections`: `for pk in self.table.
    members`)."""

    def __init__(self, table_id: str, section_id: str, final_saves: dict):
        self.table_id, self.section_id, self.final_saves = table_id, section_id, final_saves
        self.calls: list[str] = []

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append(text)
        debrief = "\n".join(
            f"```json\n{json.dumps(b, ensure_ascii=False)}\n```" for b in self.final_saves.values()
        )
        content = f"{debrief}\n{COMPLETION_MARKER} table_id={self.table_id} section_id={self.section_id}"
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "table"}


class _NoCallAllowedGm:
    """Prozess 2: ein offener Abschluss-Auftrag darf NIE einen neuen GM-/
    SL-Request ausloesen (`run_section` springt direkt zu `finalize(
    resume_section_id=...)`, VOR jedem `act()`) -- jeder Aufruf hier ist ein
    echter Doppelcall-Beleg, kein blosses Nichtbeobachten."""

    def __init__(self):
        self.calls: list[str] = []

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append(text)
        raise AssertionError(
            f"UX13: verbotener zweiter GM-/SL-Request beim Resume eines pending Abschlusses (text={text!r})"
        )


def _child_setup_pending(args: argparse.Namespace) -> None:
    """Prozess 1 (echter eigenstaendiger Subprozess): Leader+KI-Gast-Tisch,
    Abschluss wird sofort erreicht, aber die Pflicht-Reflexion von 'tech'
    schlaegt real fehl -- Ergebnis ist ein echter 'pending Abschluss'-
    Zustand (`__plan.json` ohne `__final.json`, Tisch bleibt nicht
    `closed`)."""
    root = Path(args.root)
    states_dir, run_dir, onboarding_dir, catalog_dir = root / "states", root / "run", root / "onboarding", root / "catalog"
    states_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    g03._make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, "sniper")
    g03._make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, "tech")
    write_test_profile(root / "run")

    table_id = "local-sniper-tech"
    section_id = f"{table_id}-section"
    sniper_save = g03.upgrade_narrow_save(json.loads((g03._FIX / "sniper.json").read_text(encoding="utf-8")))
    tech_save = g03.upgrade_narrow_save(json.loads((g03._FIX / "tech.json").read_text(encoding="utf-8")))
    sniper_save = {**sniper_save, "save_id": "fixture-sniper-pending-final-001"}
    tech_save = {**tech_save, "save_id": "fixture-tech-pending-final-001"}
    final_saves = {"sniper": sniper_save, "tech": tech_save}

    gm = _ImmediateCompletingGm(table_id, section_id, final_saves)
    tech_driver = _TechReflectionFailsOnceDriver(forbid_invite=False, fail_reflection_once=True)
    printed: list[str] = []
    session = TuiSession(
        onboarding_dir, catalog_dir, "sniper",
        input_fn=g03._queued_input(["Wir ruecken vorsichtig vor.", ""]),  # Zug + eigene (freiwillige) Reflexion.
        print_fn=printed.append,
        run_dir=run_dir, states_dir=states_dir, schema_path=g03._SCHEMA,
        gm_transport_factory=lambda *_a, **_kw: gm,
        persona_driver_factory=lambda pk: tech_driver,
    )
    errors: list[str] = []
    try:
        session._cmd_local_round(["persona:tech"])
    except EndOfInput:
        pass
    except Exception as e:  # echter unerwarteter Prozessabbruch bleibt sichtbar.
        errors.append(f"{type(e).__name__}: {e}")

    tables = list((run_dir / "tables").glob("*.json"))
    completion_dir = run_dir / "completion"
    plan_files = sorted(p.name for p in completion_dir.glob("*__plan.json")) if completion_dir.exists() else []
    final_files = sorted(p.name for p in completion_dir.glob("*__final.json")) if completion_dir.exists() else []
    reflections_path = run_dir / "reflections.jsonl"
    reflections = (
        [json.loads(l) for l in reflections_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        if reflections_path.exists() else []
    )
    row = {
        "errors": errors,
        "printed": printed,
        "table_names": sorted(p.stem for p in tables),
        "tables": [json.loads(p.read_text(encoding="utf-8")) for p in tables],
        "gm_calls": len(gm.calls),
        "tech_reflection_calls": tech_driver.reflection_calls,
        "plan_files": plan_files,
        "final_files": final_files,
        "reflections": reflections,
        "invitation_log": (run_dir / "invitation_decisions.jsonl").read_text(encoding="utf-8")
        if (run_dir / "invitation_decisions.jsonl").exists() else "",
        "locks": json.loads((run_dir / "locks.json").read_text(encoding="utf-8")),
    }
    Path(args.result).write_text(json.dumps(row, indent=2, ensure_ascii=False), encoding="utf-8")


def _child_resume_pending(args: argparse.Namespace) -> None:
    """Prozess 2 (neue OS-PID): derselbe Teilnehmer 'sniper' ruft
    `_cmd_menu_fortsetzen()` -- der GM-Fake wirft bei jedem Aufruf
    (Doppelcall-Beleg), 'tech's Reflexionstreiber wirft bei jedem erneuten
    Einladungs-/Consent-Request, liefert aber diesmal eine echte
    Reflexionsantwort (Retry einer ECHT fehlgeschlagenen, nicht einer
    bereits erfolgreichen Anfrage -- kein Doppelcall-Verstoss)."""
    root = Path(args.root)
    states_dir, run_dir, onboarding_dir, catalog_dir = root / "states", root / "run", root / "onboarding", root / "catalog"

    before_tables = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in (run_dir / "tables").glob("*.json")}
    assert len(before_tables) == 1, before_tables
    (table_id,) = before_tables.keys()

    gm2 = _NoCallAllowedGm()
    tech_driver2 = _TechReflectionFailsOnceDriver(forbid_invite=True, fail_reflection_once=False)
    printed: list[str] = []
    session = TuiSession(
        onboarding_dir, catalog_dir, "sniper",
        # Kein neuer Spielzug erwartet (reiner Abschlussnachzug) -- NUR die
        # eigene freiwillige Reflexion des Leaders wird noch einmal
        # abgefragt (sniper hat sie in Prozess 1 NIE gegeben: dort endete
        # der Lauf mit `reflections_ok=False`, BEVOR der Mensch ueberhaupt
        # an der Reihe war -- s. `_collect_reflections`s `for pk in self.
        # table.members`-Iterationsreihenfolge [leader zuerst]). Eine LEERE
        # Antwort ("") ist die ehrliche freiwillige Nichtangabe, KEIN EOF
        # (ein EOF hier wuerde faelschlich als Fehlschlag/`pending_recovery`
        # gewertet, s. `core/runtime.py:_collect_reflections`s
        # catch-all `except Exception`).
        input_fn=g03._queued_input([""]),
        print_fn=printed.append,
        run_dir=run_dir, states_dir=states_dir, schema_path=g03._SCHEMA,
        gm_transport_factory=lambda *_a, **_kw: gm2,
        persona_driver_factory=lambda pk: tech_driver2,
    )
    errors: list[str] = []
    try:
        session._cmd_menu_fortsetzen()
    except EndOfInput:
        pass
    except Exception as e:
        errors.append(f"{type(e).__name__}: {e}")

    after_tables = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in (run_dir / "tables").glob("*.json")}
    completion_dir = run_dir / "completion"
    plan_files = sorted(p.name for p in completion_dir.glob("*__plan.json")) if completion_dir.exists() else []
    final_files = sorted(p.name for p in completion_dir.glob("*__final.json")) if completion_dir.exists() else []
    reflections_path = run_dir / "reflections.jsonl"
    reflections = (
        [json.loads(l) for l in reflections_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        if reflections_path.exists() else []
    )
    row = {
        "errors": errors,
        "printed": printed,
        "table_names_after": sorted(after_tables.keys()),
        "status_after": after_tables.get(table_id, {}).get("status"),
        "gm2_calls": len(gm2.calls),
        "tech2_invite_calls": sum(1 for c in tech_driver2.calls if "decision_contract" in c),
        "tech2_reflection_calls": tech_driver2.reflection_calls,
        "plan_files": plan_files,
        "final_files": final_files,
        "reflections": reflections,
        "locks_after": json.loads((run_dir / "locks.json").read_text(encoding="utf-8")),
        "invitation_log_after": (run_dir / "invitation_decisions.jsonl").read_text(encoding="utf-8")
        if (run_dir / "invitation_decisions.jsonl").exists() else "",
    }
    Path(args.result).write_text(json.dumps(row, indent=2, ensure_ascii=False), encoding="utf-8")


def _run_child(root: Path, mode: str, result_path: Path) -> dict:
    cmd = [sys.executable, str(Path(__file__).resolve()), "--child", "--mode", mode,
           "--root", str(root), "--result", str(result_path)]
    cp = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if cp.returncode != 0:
        raise RuntimeError(f"child(mode={mode!r}) exit={cp.returncode}:\n{cp.stderr[-4000:]}")
    return json.loads(result_path.read_text(encoding="utf-8"))


def test_ux13_pending_completion_order_real_os_restart_no_doppelcall_no_doppelpublikation():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)

        r1 = _run_child(root, "pending_setup", root / "r1.json")
        assert not r1["errors"], r1["errors"]
        assert r1["table_names"] == ["local-sniper-tech"], r1
        assert r1["gm_calls"] == 1, "genau EIN echter Leader-Ankerzug loest den Abschlussversuch aus"
        # Kernvorbedingung UX13: echter 'pending Abschluss' -- Phase 1
        # (Harvest/`__plan.json`) erfolgreich, Phase 2 (`__final.json`)
        # NICHT erreicht (Reflexion von 'tech' real fehlgeschlagen).
        assert len(r1["plan_files"]) == 1, r1["plan_files"]
        assert r1["final_files"] == [], (
            f"Vorbedingung verletzt: Abschnitt darf nach der fehlgeschlagenen Pflichtreflexion "
            f"NOCH NICHT final abgeschlossen sein: {r1['final_files']}"
        )
        assert r1["tables"][0]["status"] != "closed", r1["tables"][0]
        pending_recovery = [e for e in r1["reflections"] if e.get("status") == "pending_recovery"]
        assert any(e.get("persona_key") == "tech" for e in pending_recovery), r1["reflections"]
        # Die bereits erfolgreich geernteten Saves/der bisherige Spielstand
        # bleiben trotzdem gueltig erhalten (keine verlorenen Bytes) --
        # mindestens ein Lock bleibt bestehen, solange der Abschluss offen ist.
        assert r1["locks"], "Chrononaut-Locks muessen waehrend eines offenen Abschlusses bestehen bleiben"

        r2 = _run_child(root, "pending_resume", root / "r2.json")
        assert not r2["errors"], r2["errors"]
        # (1) kein zweiter GM-/SL-Request.
        assert r2["gm2_calls"] == 0, (
            f"UX13: der Resume eines pending Abschlusses darf KEINEN neuen GM-/SL-Request ausloesen: {r2}"
        )
        # (2) keine erneute Einladungs-/Consent-Anfrage an 'tech'.
        assert r2["tech2_invite_calls"] == 0, (
            f"UX13: kein erneuter Einladungs-/Consent-Request an 'tech' beim Resume erwartet: {r2}"
        )
        # Genau EIN Retry der zuvor echt fehlgeschlagenen Reflexion (kein
        # Doppelcall einer bereits ERFOLGREICHEN Anfrage, s. Docstring).
        assert r2["tech2_reflection_calls"] == 1, r2
        # (3) keine Doppelpublikation: genau EIN `ai_required_reflection`-
        # Archiveintrag fuer 'tech' insgesamt (Prozess 1 schrieb nur
        # `pending_recovery`, NIE `ai_required_reflection`).
        required_reflections_tech = [
            e for e in r2["reflections"]
            if e.get("kind") == "ai_required_reflection" and e.get("persona_key") == "tech"
        ]
        assert len(required_reflections_tech) == 1, r2["reflections"]
        assert len(r2["final_files"]) == 1, (
            f"UX13: der Abschnitt muss nach erfolgreichem Reflexions-Retry real final abgeschlossen werden: {r2}"
        )
        assert r2["status_after"] == "closed", r2
        assert r2["locks_after"] == {}, "normaler Lock-Release nach echtem Abschluss erwartet"
        # (4) keine neue Einladungs-/Consent-Zeile durch den Resume selbst.
        assert r2["invitation_log_after"] == r1["invitation_log"], (
            "UX13: `_cmd_menu_fortsetzen` darf beim Nachzug eines pending Abschlusses keine neue "
            f"Einladungs-/Consent-Zeile anhaengen (Doppelcall/Publikation): {r2['invitation_log_after']!r} "
            f"!= {r1['invitation_log']!r}"
        )


def main() -> int:
    tests = [test_ux13_pending_completion_order_real_os_restart_no_doppelcall_no_doppelpublikation]
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
    if "--child" in sys.argv:
        ap = argparse.ArgumentParser()
        ap.add_argument("--child", action="store_true")
        ap.add_argument("--mode", required=True, choices=["pending_setup", "pending_resume"])
        ap.add_argument("--root", required=True)
        ap.add_argument("--result", required=True)
        ns = ap.parse_args()
        if ns.mode == "pending_setup":
            _child_setup_pending(ns)
        else:
            _child_resume_pending(ns)
        sys.exit(0)
    raise SystemExit(main())
