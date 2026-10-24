#!/usr/bin/env python3
"""
tests/mmo_sim/test_p2_candidate_ids_excluded_persona_2026_10_21.py —
Regression fuer FIX-SPEC-P1234.md P2 (ZR-N2R-ANSCHLUSS-20261019-R4
Compact-Anschluss).

BEFUND (vor dem Fix): `core.lobby_flow.run_lobby_window`s Initiative-Zweig
beschraenkt den BEFRAGTEN Scheduler-Pool bereits korrekt auf `ai_personas`,
bildet die Einladungs-/Wunschliste `candidate_ids` (wen eine befragte
Persona als moeglichen Partner angeboten bekommt) aber weiterhin aus ALLEN
freien Mitgliedern -- eine ausgewaehlte Persona kann damit eine
ausgeschlossene/nicht ausgewaehlte freie Persona in `wants` einladen. Deren
Zustimmung wird NIE eingeholt (sie ist nicht im Scheduler-Pool) -- das
Angebot bleibt offen und haelt die ausgewaehlte Gruppe bis zur
Idle-Sicherheitsgrenze fest, OHNE dass die ausgewaehlten Kandidaten
jemals zueinander finden.

FIX: `candidate_ids` nutzt `free_selectable` (bereits auf `ai_personas`
beschraenkt) statt `free`.

Methode: ECHTER Aufrufer `core.catchup.run_catch_up` (derselbe Orchestrator-
Einstieg wie Lab/TUI, s. `test_bl1_subset_starvation_2026_10_21.py::
test_bl1_lab_path_foreign_bound_unplayed_table`) -- kein Direktaufruf von
`lobby_flow.run_lobby_window` an den Fix vorbei.

Reuse (Leitprinzip "Reuse vor Neubau"): Community-Bootstrap/`_TableGM`-
Helfer aus `test_l01_l10_lobby_initiative.py` (wie
`test_bl1_subset_starvation_2026_10_21.py`)."""
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

import test_l01_l10_lobby_initiative as l01  # noqa: E402

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import catchup  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

HUMAN_PK = "sniper"
AI_PERSONAS = ("cqb", "face", "pyro")


class _NeverCalledDriver:
    """Fail-closed-Wache: `pyro` ist in diesem Szenario bewusst NICHT
    ausgewaehlt -- ein Treiberaufruf fuer `pyro` waere selbst der Bug
    (analog `test_bl1_subset_starvation_2026_10_21.py::_NeverCalledDriver`)."""

    def __init__(self, pk: str):
        self.pk = pk

    def decide(self, ctx: dict) -> ParticipantDecision:
        raise AssertionError(f"{self.pk!r} haette in diesem Szenario NIE einen Treiberaufruf bekommen duerfen")


class _GreedyInitiativeDriver:
    """Organischer, aber deterministischer Initiativ-Treiber: nimmt
    Rundeneinladungen an (`decision_contract`) und versucht bei einem
    eigenen Initiativfenster IMMER ZUERST, `decoy` (eine sichtbare, aber
    nicht ausgewaehlte freie Persona) einzuladen, FALLS `decoy` in der
    ihr angebotenen Kandidatenliste (`candidate_ids`, im Kontrakttext
    sichtbar) ueberhaupt auftaucht -- das ist exakt der P2-Befund: eine
    reale KI wuerde eine sichtbare, bekannte freie Mitspielerin genauso
    gern einladen wie die ausgewaehlte Partnerin. Taucht `decoy` NICHT
    (mehr) in der Kandidatenliste auf (P2-Fix wirksam), schlaegt sie
    stattdessen `partner` vor -- kein Zufall, kein offener Ausgang."""

    def __init__(self, pk: str, partner: str | None, decoy: str | None):
        self.pk = pk
        self.partner = partner
        self.decoy = decoy
        self.calls: list[dict] = []

    def decide(self, ctx: dict) -> ParticipantDecision:
        self.calls.append(ctx)
        if "decision_contract" in ctx:
            c = ctx["decision_contract"]
            text = f"ENTSCHEIDUNG offer_id={c['offer_id']} participant_id={self.pk} decision=accept"
            return ParticipantDecision(text=text, origin_source=f"p2:{self.pk}")
        user = ctx.get("user", "")
        if "begrenztes eigenes Lobby-Initiativfenster" in user:
            if self.decoy is not None and f'"{self.decoy}"' in user:
                text = json.dumps({"action": "propose", "wants": [self.decoy]})
            elif self.partner is not None and self.pk < self.partner:
                text = json.dumps({"action": "propose", "wants": [self.partner]})
            else:
                text = json.dumps({"action": "pause"})
            return ParticipantDecision(text=text, origin_source=f"p2:{self.pk}")
        return ParticipantDecision(text="Wir beobachten die Lage.", origin_source=f"p2:{self.pk}")


def _bootstrap(root: Path):
    schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = l01._bootstrap_community(
        root, f"community-{HUMAN_PK}", list(AI_PERSONAS),
    )
    write_test_profile(run_dir)
    l01._make_ready(onboarding_dir, states_dir, run_dir, HUMAN_PK)
    for pk in AI_PERSONAS:
        l01._make_ready(onboarding_dir, states_dir, run_dir, pk)
    all_saves = {pk: l01._load_fixture_save(pk) for pk in (HUMAN_PK,) + AI_PERSONAS}
    gm_registry: dict[str, l01._TableGM] = {}

    def gm_transport_factory(table_id: str | None = None):
        table = core_store.Table.load(run_dir, table_id)
        final_saves = {pk: all_saves[pk] for pk in table.members if pk in all_saves}
        gm = gm_registry.get(table_id)
        if gm is None:
            gm = l01._TableGM(table_id, f"{table_id}-section", final_saves, turns_before_marker=1)
            gm_registry[table_id] = gm
        return gm

    return schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, gm_transport_factory


def test_p2_excluded_free_persona_never_becomes_invitation_target():
    """P2 (gezielt) ueber den echten Orchestrator-Einstieg
    (`catchup.run_catch_up`): `cqb`/`face` sind ausgewaehlt (`selected`),
    `pyro` ist frei/spielbereit, aber NICHT ausgewaehlt. VORHER: `cqb`
    lud wiederholt `pyro` ein (sichtbar in `candidate_ids`), das Angebot
    blieb offen (`pyro` nie im Scheduler-Pool befragt) -- `cqb`/`face`
    erreichten ihr Ziel nie, `report.blocked` enthielt beide. NACHHER:
    `pyro` taucht nie in `candidate_ids` auf, `cqb` ladet `face` ein,
    beide erreichen ihr Ziel, `pyro`s Treiber wird NIE aufgerufen."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, gm_transport_factory = _bootstrap(root)

        drivers = {
            "cqb": _GreedyInitiativeDriver("cqb", partner="face", decoy="pyro"),
            "face": _GreedyInitiativeDriver("face", partner="cqb", decoy=None),
            "pyro": _NeverCalledDriver("pyro"),
        }

        def persona_driver_factory(pk: str):
            return drivers[pk]

        printed: list[str] = []

        def no_human_responder(prompt: str = "") -> str:
            raise AssertionError(f"dieser Orchestrator-Pfad sollte nie einen Mensch-Prompt stellen: {prompt!r}")

        session = TuiSession(
            onboarding_dir, catalog_dir, HUMAN_PK,
            input_fn=no_human_responder, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=gm_transport_factory,
            persona_driver_factory=persona_driver_factory,
        )

        selected = {"cqb", "face"}
        report = catchup.run_catch_up(
            session, selected=selected, current_table_members=set(), target=1,
            max_windows=40, idle_safety_cap=3,
        )

        assert not report.blocked, (
            f"P2 (vor dem Fix): 'pyro' blieb sichtbares Einladungsziel fuer 'cqb', das Angebot "
            f"blieb offen -- cqb/face wurden faelschlich blockiert: {report.notes}"
        )
        assert not report.stopped, report.stopped_reason
        assert report.end_counts.get("cqb", 0) >= 1 and report.end_counts.get("face", 0) >= 1, (
            f"cqb/face haetten ihr Ziel (1) erreichen muessen: {report.end_counts}"
        )
        # `pyro` bleibt in seinem Zustand unangetastet -- nie befragt, nie gespielt.
        assert core_store.sections_played_by_participant(run_dir).get("pyro", 0) == 0
        assert len(drivers["cqb"].calls) >= 1 and len(drivers["face"].calls) >= 1


def test_p2_real_rejection_among_selected_personas_still_honored():
    """Gegenprobe (unveraendertes Verhalten): eine echte freiwillige
    Ablehnung EINER AUSGEWAEHLTEN Persona wird weiterhin korrekt als
    Ablehnung behandelt -- kein Auto-Accept, keine erzwungene Zustimmung,
    der P2-Fix aendert NUR die Sichtbarkeit nicht ausgewaehlter freier
    Personas, nicht die Konsenslogik unter ausgewaehlten."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, gm_transport_factory = _bootstrap(root)

        class _ProposeThenRejectDriver:
            def __init__(self, pk: str, partner: str | None, will_reject: bool):
                self.pk = pk
                self.partner = partner
                self.will_reject = will_reject
                self.calls: list[dict] = []

            def decide(self, ctx: dict) -> ParticipantDecision:
                self.calls.append(ctx)
                if "decision_contract" in ctx:
                    c = ctx["decision_contract"]
                    decision = "reject" if self.will_reject else "accept"
                    text = f"ENTSCHEIDUNG offer_id={c['offer_id']} participant_id={self.pk} decision={decision}"
                    return ParticipantDecision(text=text, origin_source=f"p2reject:{self.pk}")
                user = ctx.get("user", "")
                if "begrenztes eigenes Lobby-Initiativfenster" in user:
                    if self.partner is not None and self.pk < self.partner:
                        text = json.dumps({"action": "propose", "wants": [self.partner]})
                    else:
                        text = json.dumps({"action": "pause"})
                    return ParticipantDecision(text=text, origin_source=f"p2reject:{self.pk}")
                return ParticipantDecision(text="Wir beobachten.", origin_source=f"p2reject:{self.pk}")

        drivers = {
            "cqb": _ProposeThenRejectDriver("cqb", partner="face", will_reject=False),
            "face": _ProposeThenRejectDriver("face", partner="cqb", will_reject=True),
            "pyro": _NeverCalledDriver("pyro"),
        }

        def persona_driver_factory(pk: str):
            return drivers[pk]

        printed: list[str] = []

        def no_human_responder(prompt: str = "") -> str:
            raise AssertionError(f"unerwarteter Prompt: {prompt!r}")

        session = TuiSession(
            onboarding_dir, catalog_dir, HUMAN_PK,
            input_fn=no_human_responder, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=gm_transport_factory,
            persona_driver_factory=persona_driver_factory,
        )

        report = catchup.run_catch_up(
            session, selected={"cqb", "face"}, current_table_members=set(), target=1,
            max_windows=10, idle_safety_cap=3,
        )
        assert "face" in report.blocked, (
            f"'face' lehnt ehrlich ab -- sollte blockiert bleiben, NICHT erzwungen beigetreten "
            f"sein: {report.notes}"
        )
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
