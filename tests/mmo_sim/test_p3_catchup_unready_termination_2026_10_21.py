#!/usr/bin/env python3
"""
tests/mmo_sim/test_p3_catchup_unready_termination_2026_10_21.py —
Regression fuer FIX-SPEC-P1234.md P3 (ZR-N2R-ANSCHLUSS-20261019-R4
Compact-Anschluss).

BEFUND (vor dem Fix): im Lab (`mmo_sim/lab/cli.py` Hauptloop) ist
`round_target = max(counts der selected) + 1`, `current_table_members=
set()`. `core.catchup.run_catch_up` bildet `base_candidates = (selected &
ready_keys) - current_table`. Sind ALLE ausgewaehlten Mitglieder UNbereit
(z.B. Community bestaetigt, aber nie onboardet/kein Save veroeffentlicht),
ist `candidates` leer -> Rueckgabe `windows_run=0, stopped=False,
blocked=[]`, Note "bereits Paritaet". Der Lab-Loop wertete das als
abgeschlossene Runde, machte KEINE Requests (kein Verbrauch -> `should_
stop()` bleibt False) und begann SOFORT die naechste Runde -- ein
unbeschraenkter Null-Arbeits-/CPU-Loop OHNE Wall-Cap, mit faelschlich als
"abgeschlossen" gemeldeten unbereiten Teilnehmern.

FIX: `CatchUpReport.unready` (neu) benennt ehrlich, wer nicht spielbereit
ist; `lab/cli.py` terminiert geordnet, sobald `windows_run == 0 and not
report.candidates` (NULL ausfuehrbare Arbeit), statt die naechste Runde
sofort zu beginnen.

Methode: ECHTER CLI-Subprozess (`scripts/mmo_sim.py lab start ...`,
GESCHLOSSENES stdin, analog `test_h01_h07_headless_lab_cli.py`) -- der
kritische Teil des Befunds (der Lab-HAUPTLOOP selbst) wird NICHT durch
einen Direktaufruf von `catchup.run_catch_up` an der eigentlichen
Schleifenlogik vorbei ersetzt. Ein externer `subprocess`-Timeout dient NUR
als Sicherheitsnetz des TESTHARNESS (keine Wall-Cap-"Loesung" im Produkt
selbst -- die lehnt FIX-SPEC-P1234.md ausdruecklich ab; ohne Fix haengt der
Lauf ohne JEDE eigene Obergrenze, s. unten).

Reuse (Leitprinzip "Reuse vor Neubau"): `_bootstrap_community`/`_make_ready`
aus `test_l01_l10_lobby_initiative.py`, `_run_lab`-Subprozesshelfer-Pattern
aus `test_h01_h07_headless_lab_cli.py` (kein zweiter CLI-Aufrufweg)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_HERE))
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import test_l01_l10_lobby_initiative as l01  # noqa: E402

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import catchup  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.lab import runner as lab_runner  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_MMO_SIM = _REPO_ROOT / "scripts" / "mmo_sim.py"

# Sicherheitsnetz des TESTHARNESS (nicht die Produktloesung, s. Moduldocstring):
# ohne Fix haengt der Lauf unbeschraenkt -- ein externer Subprozess-Timeout
# verhindert, dass ein roter Lauf diesen Testprozess selbst blockiert.
_HANG_GUARD_SECONDS = 20


def _run_lab(args: list[str], env_extra: dict | None = None, timeout: int = _HANG_GUARD_SECONDS):
    import os
    env = dict(os.environ)
    env.update(env_extra or {})
    return subprocess.run(
        [sys.executable, str(_MMO_SIM), "lab", *args],
        stdin=subprocess.DEVNULL, capture_output=True, text=True, env=env, timeout=timeout,
    )


def test_p3_lab_loop_terminates_without_infinite_null_work_when_all_selected_unready():
    """P3 (Kern): eine bestaetigte Community mit AUSSCHLIESSLICH UNbereiten
    Mitgliedern (nie onboardet, kein Save) -- `--personas` waehlt genau
    diese Menge. VORHER: endlose Null-Arbeits-Runden (kein `lab.stop`
    gesetzt, Prozess muss per Timeout gewaltsam beendet werden). NACHHER:
    GENAU EINE geordnete Rueckkehr, `lab.stop` gesetzt, ehrlicher Grund mit
    den unbereiten Teilnehmern, kein einziger Modell-/HTTP-Call (es gibt
    keinen Persona-Server in diesem Test -- ein fehlerhafter Pfad, der
    trotzdem einen Request versucht, wuerde mit einem Verbindungsfehler
    sichtbar auffallen, nicht leise durchlaufen)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["cqb", "face"]
        # NUR Community-Bootstrap (bestaetigte Mitgliedschaft) -- bewusst
        # KEIN `_make_ready` fuer irgendeine der beiden Personas: beide
        # bleiben unbereit (kein Onboarding, kein veroeffentlichter Save).
        _schema, _states, run_dir, _onboarding, _catalog = l01._bootstrap_community(
            root, "community-p3allunready", keys,
        )

        try:
            proc = _run_lab([
                "start", "--data-dir", str(root), "--community", "p3allunready", "--profile", "api",
                "--max-requests", "20", "--max-seconds", "60", "--max-usd", "5.0",
                "--max-idle-windows", "3", "--personas", "cqb,face",
            ], env_extra={
                "MMO_SIM_PERSONA_API_BASE_URL": "http://127.0.0.1:1",
                "MMO_SIM_PERSONA_API_KEY": "SYNTH-UNUSED", "MMO_SIM_PERSONA_API_MODEL": "synthetic-p3",
            })
        except subprocess.TimeoutExpired as exc:
            raise AssertionError(
                f"P3 (vor dem Fix): der Lab-Loop ist NICHT innerhalb von {_HANG_GUARD_SECONDS}s "
                "geordnet zurueckgekehrt -- unbeschraenkter Null-Arbeits-Loop (kein Verbrauch, "
                f"keine eigene Terminierung). stdout bisher: {exc.stdout!r}"
            ) from exc

        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "nichts ausfuehrbar" in proc.stdout or "ohne ausfuehrbare Arbeit" in proc.stdout, (
            f"keine ehrliche 'nichts ausfuehrbar'-Meldung im Lab-Output gefunden:\n{proc.stdout}"
        )
        assert "cqb" in proc.stdout and "face" in proc.stdout, (
            f"die unbereiten Teilnehmer sollten namentlich im Output auftauchen:\n{proc.stdout}"
        )
        assert "abgeschlossen fuer ['cqb', 'face']" not in proc.stdout, (
            f"P3 (vor dem Fix): falsches DONE -- unbereite Teilnehmer wurden als 'abgeschlossen' "
            f"gemeldet:\n{proc.stdout}"
        )
        assert (run_dir / "lab.stop").exists(), "geordneter Stop haette lab.stop setzen muessen"
        status = lab_runner.read_status(run_dir)
        assert status is not None and status.turns_used == 0, (
            f"es sollte NULL echte Requests gegeben haben (keine Kandidaten je spielbereit): {status}"
        )


def test_p3_catchup_report_unready_field_mixed_selection():
    """P3 (Ehrlichkeit, gemischte Auswahl): direkter Aufruf desselben
    Orchestrators, den `lab/cli.py` pro Runde nutzt (`catchup.run_catch_up`,
    identische Aufrufsignatur `target=<Rundenziel>, current_table_members=
    set()`) -- `tech` ist spielbereit und ausgewaehlt, `cqb`/`face` sind
    ausgewaehlt, aber NIE onboardet (unbereit). `report.unready` MUSS genau
    `['cqb', 'face']` benennen, `tech` darf NICHT als unready erscheinen
    und muss sein Ziel erreichen; `report.blocked` darf `tech` nicht
    enthalten."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        # `ready_persona_keys` leitet die Community-ID intern aus
        # `session.participant_id` ab (`f"community-{participant_id}"`,
        # analog `test_bl1_subset_starvation_2026_10_21.py::_bootstrap`) --
        # ein eigener Trigger-Teilnehmer (hier nicht Teil der Auswahl)
        # bindet den Bootstrap an einen von `keys` UNABHAENGIGEN Namen.
        TRIGGER_PK = "p3mixed_trigger"
        keys = ["cqb", "face", "tech"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = l01._bootstrap_community(
            root, f"community-{TRIGGER_PK}", keys,
        )
        write_test_profile(run_dir)
        l01._make_ready(onboarding_dir, states_dir, run_dir, "tech")
        # cqb/face bleiben bewusst UNbereit (kein `_make_ready`).

        save = l01._load_fixture_save("tech")
        gm_registry: dict[str, l01._TableGM] = {}

        def gm_transport_factory(table_id: str | None = None):
            table = core_store.Table.load(run_dir, table_id)
            final_saves = {pk: save for pk in table.members if pk == "tech"}
            gm = gm_registry.get(table_id)
            if gm is None:
                gm = l01._TableGM(table_id, f"{table_id}-section", final_saves, turns_before_marker=1)
                gm_registry[table_id] = gm
            return gm

        class _SoloProposeDriver:
            """`tech` ist der einzige spielbereite Kandidat -- schlaegt in
            seinem Initiativfenster einen Solo-Tisch vor (`wants=[]`,
            `leader=self`), analog einer einzelnen freien Figur ohne
            Partner (Reuse-Vertrag identisch zu `_cmd_local_round([])`)."""

            def __init__(self):
                self.calls: list[dict] = []

            def decide(self, ctx: dict) -> ParticipantDecision:
                self.calls.append(ctx)
                user = ctx.get("user", "")
                if "begrenztes eigenes Lobby-Initiativfenster" in user:
                    return ParticipantDecision(
                        text=json.dumps({"action": "propose", "wants": []}),
                        origin_source="p3:tech",
                    )
                return ParticipantDecision(text="Ich beobachte die Lage.", origin_source="p3:tech")

        tech_driver = _SoloProposeDriver()

        def persona_driver_factory(pk: str):
            assert pk == "tech", f"{pk!r} ist unbereit und sollte NIE befragt werden (unready)."
            return tech_driver

        printed: list[str] = []

        def no_human_responder(prompt: str = "") -> str:
            raise AssertionError(f"unerwarteter Prompt: {prompt!r}")

        session = TuiSession(
            onboarding_dir, catalog_dir, TRIGGER_PK,
            input_fn=no_human_responder, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=gm_transport_factory,
            persona_driver_factory=persona_driver_factory,
        )

        counts = core_store.sections_played_by_participant(run_dir)
        round_target = max((counts.get(pk, 0) for pk in keys), default=0) + 1
        report = catchup.run_catch_up(
            session, selected=set(keys), current_table_members=set(),
            target=round_target, max_windows=20, idle_safety_cap=5,
        )

        assert report.unready == ["cqb", "face"], report.unready
        assert "tech" not in report.unready, report.unready
        assert "tech" not in report.blocked, (
            f"'tech' ist spielbereit und sollte sein Ziel erreichen, nicht blockiert sein: "
            f"{report.notes}"
        )
        assert core_store.sections_played_by_participant(run_dir).get("tech", 0) >= 1, (
            "'tech' haette real vorankommen muessen."
        )
        assert core_store.sections_played_by_participant(run_dir).get("cqb", 0) == 0
        assert core_store.sections_played_by_participant(run_dir).get("face", 0) == 0


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
        except Exception:
            failures += 1
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
    total = len(tests)
    print(f"\n{total - failures}/{total} Tests bestanden.")
    sys.exit(1 if failures else 0)
