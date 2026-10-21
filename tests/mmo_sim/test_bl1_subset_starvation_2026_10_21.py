#!/usr/bin/env python3
"""
tests/mmo_sim/test_bl1_subset_starvation_2026_10_21.py — dauerhafte
Repo-Regression fuer BL1-FIX-SPEC.md (CRITIC-REPORT-R3.md BLOCKER BL1,
MAJOR M1/M3).

BL1: ein aktiver, gebundener, NIE gespielter (`sl_log=[]`) rein-KI-Tisch,
dessen Mitglieder NICHT Teil der fuer einen Catch-up-/Vorspiel-Aufruf
ausgewaehlten Menge sind, gewann vor diesem Fix in `lobby_flow.
run_lobby_window`s PRE-STEP (`store.find_bound_active_unplayed_table`, OHNE
`ai_personas`-Filter) JEDES Fenster -- die tatsaechlich ausgewaehlten,
bereiten Kandidaten bekamen NIE eine Initiative-Chance und wurden nach
`idle_safety_cap` faelschlich als `blocked` gemeldet. Fix: `find_bound_
active_unplayed_table` bekommt einen OPTIONALEN `ai_personas`-Filter (Default
`None` = unveraendert), `lobby_flow.run_lobby_window`s PRE-STEP reicht die
aktuelle Auswahl durch (analog STEP 1).

M1: "Vorspielen" (`catchup.run_catch_up`s `max_rounds`) war im gesamten
Produktpfad toter Code -- kein Aufrufer nutzte ihn. Fix: `ui.tui.TuiSession.
_cmd_catch_up_personas(vorspielen=True)` (Menuepunkt [5]) ruft `run_catch_up`
jetzt mit `max_rounds=1`.

M3: der bisherige organische Test (`test_r4_organic_player_flow_2026_10_21.py`)
wahlt bei "Personas spielen lassen" immer ALLE wahlbaren Kandidaten (leere
Eingabe) und sieht BL1 strukturell nie. Dieser Testfall (`test_bl1_tui_...`)
ergaenzt eine ECHTE, kommagetrennte Teilauswahl UEBER DEN ECHTEN TUI-
Produktpfad (`TuiSession._cmd_catch_up_personas`), WAEHREND gleichzeitig ein
nicht ausgewaehlter, gebundener-ungespielter Tisch existiert.

Reuse (Leitprinzip "Reuse vor Neubau"): Community-Bootstrap/Fixture-Saves/
`_TableGM`-Helfer aus `test_l01_l10_lobby_initiative.py` (wie bereits
`test_r2_hauptbefund2_bound_table_recovery.py`/
`test_r4_organic_player_flow_2026_10_21.py`), direkte Store-Level-
Tisch-Konstruktion fuer die BL1-Vorbedingung analog CRITIC-REPORT-R3.md
Repro-Methodik (`critic_r3_repro_b2_stuck_ai_table.py`, dauerhaft als
Regression portiert)."""
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
from mmo_sim.domain.zeitriss.policy import ZeitrissTableSizePolicy  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

HUMAN_PK = "sniper"
AI_PERSONAS = ("tech", "cqb", "face", "medic", "pyro")


class _PairDriver:
    """Deterministischer Entscheider fuer EIN Paar KI-Personas, die sich
    IMMER gegenseitig vorschlagen/annehmen -- kein offener Ausgang, kein
    Zufall (analog `critic_r3_repro_b2_stuck_ai_table.py::_PairDriver`)."""

    def __init__(self, pk: str, partner: str):
        self.pk = pk
        self.partner = partner
        self.calls: list[dict] = []

    def decide(self, ctx: dict) -> ParticipantDecision:
        self.calls.append(ctx)
        if "decision_contract" in ctx:
            c = ctx["decision_contract"]
            text = f"ENTSCHEIDUNG offer_id={c['offer_id']} participant_id={self.pk} decision=accept"
            return ParticipantDecision(text=text, origin_source=f"bl1test:{self.pk}")
        if "begrenztes eigenes Lobby-Initiativfenster" in ctx.get("user", ""):
            if self.pk < self.partner:
                text = json.dumps({"action": "propose", "wants": [self.partner]})
            else:
                text = json.dumps({"action": "pause"})
            return ParticipantDecision(text=text, origin_source=f"bl1test:{self.pk}")
        return ParticipantDecision(text="Wir beobachten die Lage.", origin_source=f"bl1test:{self.pk}")


class _NeverCalledDriver:
    """Fail-closed-Wache: ein Treiberaufruf fuer eine NICHT ausgewaehlte/
    fremde Persona ist selbst der Bug (BL1 wuerde solche Personas NIE
    befragen muessen, weil sie entweder gebunden/fremd oder nicht ausgewaehlt
    sind -- jeder Aufruf hier waere ein eigenstaendiger neuer Fehler)."""

    def __init__(self, pk: str):
        self.pk = pk

    def decide(self, ctx: dict) -> ParticipantDecision:
        raise AssertionError(
            f"{self.pk!r} haette in diesem Szenario NIE einen Treiberaufruf bekommen duerfen"
        )


def _bootstrap(root: Path, label: str):
    # `ready_persona_keys` leitet die Community-ID intern selbst wieder aus
    # `session.participant_id` ab (`f"community-{participant_id}"`) -- `label`
    # dient hier NUR der Lesbarkeit beim Debuggen (eigenes Tempdir je Test,
    # keine Kollisionsgefahr), darf aber NICHT in die tatsaechliche Community-ID
    # einfliessen, sonst findet `ready_persona_keys` die Community nicht.
    schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = l01._bootstrap_community(
        root, f"community-{HUMAN_PK}", list(AI_PERSONAS),
    )
    write_test_profile(run_dir)
    l01._make_ready(onboarding_dir, states_dir, run_dir, HUMAN_PK)
    chrono_ids = {}
    for pk in AI_PERSONAS:
        chrono_ids[pk] = l01._make_ready(onboarding_dir, states_dir, run_dir, pk)
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

    return schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, chrono_ids, gm_transport_factory


def _construct_foreign_stuck_table(run_dir: Path, chrono_ids: dict[str, str]) -> str:
    """Konstruiert die BL1-Vorbedingung direkt auf Store-Ebene: `medic` und
    `tech` sind an EINEN gemeinsamen Tisch gebunden, aktiv, NIE gespielt
    (`sl_log=[]`) -- realistisch der Zustand, den Hintergrund-Lobby-
    Initiative erzeugen kann, wenn Tischanlage gelingt, die sofortige
    Mitglieder-Aufloesung aber (z.B. transient) scheitert."""
    stuck_table_id = "lobby-medic-tech"
    (run_dir / "tables").mkdir(parents=True, exist_ok=True)
    offer_log = [
        {"type": "offer", "id": "offer-tech-1", "from": "tech", "wants": ["medic"]},
        {"type": "consent", "offer_id": "offer-tech-1", "from": "medic", "accept": True},
    ]
    stuck_table = core_store.Table(
        table_id=stuck_table_id, leader="tech", members=["medic", "tech"],
        chrononaut_ids={"medic": chrono_ids["medic"], "tech": chrono_ids["tech"]},
        run_dir=run_dir, sl_log=[], status="active",
        operator_meta={
            "offer_log": offer_log, "derivation_reason": "bl1-regression-fixture",
            "source_offer_id": "offer-tech-1", "dissenters": {},
        },
    )
    stuck_table.persist()
    lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    lobby.lock_chrononaut(chrono_ids["medic"], stuck_table_id)
    lobby.lock_chrononaut(chrono_ids["tech"], stuck_table_id)
    return stuck_table_id


def test_bl1_tui_path_partial_selection_with_foreign_bound_unplayed_table():
    """BL1 (gezielt) + M3 (Testluecke) ueber den ECHTEN TUI-Produktpfad: der
    Spieler waehlt eine ECHTE Teilmenge ('cqb,face') bei 'Personas spielen
    lassen', WAEHREND ein fremder, gebundener-ungespielter KI-Tisch
    (medic+tech) existiert, der NICHT Teil der Auswahl ist. Vor dem Fix:
    0 Treiberaufrufe fuer cqb/face, faelschlich 'blockiert'. Mit Fix: cqb/face
    bekommen Initiative, erreichen ihr Ziel, pyro/medic/tech werden NIE
    befragt (weder ausgewaehlt noch gebunden-irrelevant)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, chrono_ids, gm_transport_factory = (
            _bootstrap(root, "tui")
        )

        drivers = {
            "cqb": _PairDriver("cqb", "face"),
            "face": _PairDriver("face", "cqb"),
            "pyro": _NeverCalledDriver("pyro"),
            "medic": _NeverCalledDriver("medic"),
            "tech": _NeverCalledDriver("tech"),
        }

        def persona_driver_factory(pk: str):
            return drivers[pk]

        printed: list[str] = []
        catchup_selection_queue: list[str] = ["cqb,face"]

        def human_responder(prompt: str = "") -> str:
            if "Deine Aktion" in prompt:
                return "Ich sichere die Position."
            if prompt.startswith("Welche jetzt spielen lassen?"):
                return catchup_selection_queue.pop(0) if catchup_selection_queue else ""
            raise AssertionError(f"unerwarteter Prompt: {prompt!r}")

        session = TuiSession(
            onboarding_dir, catalog_dir, HUMAN_PK,
            input_fn=human_responder, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=gm_transport_factory,
            persona_driver_factory=persona_driver_factory,
        )

        # Baseline: sniper spielt EINEN Abschnitt solo -> eigene Zahl = 1
        # (Catch-up-Ziel fuer cqb/face).
        session._cmd_local_round([])
        assert core_store.sections_played_by_participant(run_dir).get(HUMAN_PK, 0) == 1

        # BL1-Vorbedingung: medic+tech gebunden, aktiv, ungespielt, AUSSERHALB
        # der gleich folgenden Auswahl ('cqb,face').
        stuck_table_id = _construct_foreign_stuck_table(run_dir, chrono_ids)
        assert core_store.find_bound_active_unplayed_table(
            run_dir,
            {pk: chrono_ids[pk] for pk in ("medic", "tech")},
            {"medic": stuck_table_id, "tech": stuck_table_id},
        ) is not None, "Vorbedingung nicht aufgebaut: PRE-STEP sollte den fremden Tisch (ohne Filter) sehen."

        # Echte Teilauswahl ueber den echten Menuepfad.
        session._cmd_catch_up_personas()

        out = "\n".join(printed[-30:])
        assert "blockiert/kein Fortschritt: (keine)" in out, (
            f"cqb/face wurden faelschlich als blockiert gemeldet (BL1 nicht behoben):\n{out}"
        )
        assert len(drivers["cqb"].calls) > 0 and len(drivers["face"].calls) > 0, (
            "cqb/face haben in keinem Fenster eine Initiative-Chance bekommen (BL1: 0 Treiberaufrufe)."
        )
        counts_after = core_store.sections_played_by_participant(run_dir)
        assert counts_after.get("cqb", 0) >= 1 and counts_after.get("face", 0) >= 1, (
            f"cqb/face haetten ihr Catch-up-Ziel (1) erreichen muessen: {counts_after}"
        )
        # Der fremde Tisch bleibt unangetastet -- kein versehentliches
        # Fremdabschliessen/Vorspielen von medic/tech durch diesen Aufruf.
        assert counts_after.get("medic", 0) == 0 and counts_after.get("tech", 0) == 0
        assert not core_store._table_has_final(run_dir, stuck_table_id)


def test_bl1_lab_path_foreign_bound_unplayed_table():
    """BL1 im Lab-Betrieb (headless, `--personas`-Teilauswahl,
    `current_table_members=set()`, explizites `target` -- exakt die
    Aufrufsignatur von `lab/cli.py`s Paritaetsrunde): derselbe fremde,
    gebundene-ungespielte Tisch (medic+tech) darf die fuer den Lab-Lauf
    ausgewaehlten Kandidaten (cqb, face) genauso wenig starven."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, chrono_ids, gm_transport_factory = (
            _bootstrap(root, "lab")
        )

        drivers = {
            "cqb": _PairDriver("cqb", "face"),
            "face": _PairDriver("face", "cqb"),
            "pyro": _NeverCalledDriver("pyro"),
            "medic": _NeverCalledDriver("medic"),
            "tech": _NeverCalledDriver("tech"),
        }

        def persona_driver_factory(pk: str):
            return drivers[pk]

        printed: list[str] = []

        def no_human_responder(prompt: str = "") -> str:
            raise AssertionError(f"Lab-Betrieb sollte nie einen Mensch-Prompt stellen: {prompt!r}")

        session = TuiSession(
            onboarding_dir, catalog_dir, HUMAN_PK,
            input_fn=no_human_responder, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=gm_transport_factory,
            persona_driver_factory=persona_driver_factory,
        )

        stuck_table_id = _construct_foreign_stuck_table(run_dir, chrono_ids)

        selected = {"cqb", "face"}
        report = catchup.run_catch_up(
            session, selected=selected, current_table_members=set(), target=1,
            max_windows=max(50, len(selected) * 20), idle_safety_cap=catchup.DEFAULT_IDLE_SAFETY_CAP,
        )
        assert not report.blocked, f"Lab-Pfad: cqb/face faelschlich blockiert (BL1): {report.notes}"
        assert len(drivers["cqb"].calls) > 0 and len(drivers["face"].calls) > 0
        assert report.end_counts.get("cqb", 0) >= 1 and report.end_counts.get("face", 0) >= 1
        assert not core_store._table_has_final(run_dir, stuck_table_id)


def test_m1_max_rounds_vorspielen_direct_orchestrator_call():
    """M1: `run_catch_up(max_rounds=1)` direkt -- Personas bereits bei
    Paritaet (target=None waere hier ein No-Op, der M1-Bug) muessen durch
    `max_rounds=1` trotzdem genau EINEN Abschnitt vorspielen. Ein aktueller
    Tischmitspieler (hier simuliert ueber `current_table_members`) wird NIE
    Kandidat, auch nicht unter `max_rounds`."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, chrono_ids, gm_transport_factory = (
            _bootstrap(root, "vorspielen")
        )

        drivers = {
            "cqb": _PairDriver("cqb", "face"),
            "face": _PairDriver("face", "cqb"),
            "medic": _NeverCalledDriver("medic"),
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

        # Schritt 1: cqb/face auf Paritaet (1) bringen -- reiner Setup-Schritt
        # (bewusst `target=1`, nicht Teil der eigentlichen M1-Pruefung).
        setup_report = catchup.run_catch_up(
            session, selected={"cqb", "face"}, current_table_members=set(), target=1,
        )
        assert not setup_report.blocked, setup_report.notes
        counts_mid = core_store.sections_played_by_participant(run_dir)
        assert counts_mid.get("cqb", 0) == 1 and counts_mid.get("face", 0) == 1, counts_mid

        # M1-Praeklusion belegen: bei bereits erreichter Paritaet ist
        # `target=None` (Catch-up) ein No-Op -- GENAU der tote-Code-Befund.
        noop_report = catchup.run_catch_up(
            session, selected={"cqb", "face"}, current_table_members=set(), target=None,
        )
        assert noop_report.candidates == [], (
            f"Setup fehlerhaft: bei Paritaet haette Catch-up (target=None) KEINE Kandidaten haben "
            f"duerfen (das ist exakt die M1-Vorbedingung): {noop_report.candidates}"
        )

        # M1-Fix: `max_rounds=1` treibt TROTZ Paritaet genau einen weiteren
        # Abschnitt je gewaehlter Persona. `medic` ist absichtlich als
        # "aktueller Tischmitspieler" simuliert (`current_table_members`) --
        # selbst wenn er in `selected` stuende, duerfte er NIE Kandidat
        # werden (Schluessel-Invariante gilt unveraendert unter max_rounds).
        vorspielen_report = catchup.run_catch_up(
            session, selected={"cqb", "face", "medic"}, current_table_members={"medic"}, max_rounds=1,
        )
        assert "medic" not in vorspielen_report.candidates, (
            f"Schluessel-Invariante verletzt: aktueller Tischmitspieler 'medic' wurde Vorspiel-"
            f"Kandidat: {vorspielen_report.candidates}"
        )
        assert not vorspielen_report.blocked, vorspielen_report.notes
        counts_after = core_store.sections_played_by_participant(run_dir)
        assert counts_after.get("cqb", 0) == 2 and counts_after.get("face", 0) == 2, (
            f"Vorspielen (max_rounds=1) haette cqb/face je genau +1 Abschnitt bringen muessen "
            f"(vorher {counts_mid}, nachher {counts_after})."
        )
        assert counts_after.get("medic", 0) == 0, "medic (aktueller Tischmitspieler) wurde vorgespielt."


def test_m1_tui_vorspielen_menu_reaches_parity_personas():
    """M1 ueber den echten Menuepfad: [5] 'Personas vorspielen lassen' MUSS
    bei bereits erreichter Paritaet (wo [3] Catch-up nichts getan haette)
    trotzdem einen Abschnitt vorspielen."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, chrono_ids, gm_transport_factory = (
            _bootstrap(root, "tui-vorspielen")
        )

        drivers = {
            "cqb": _PairDriver("cqb", "face"),
            "face": _PairDriver("face", "cqb"),
            "pyro": _NeverCalledDriver("pyro"),
            "medic": _NeverCalledDriver("medic"),
            "tech": _NeverCalledDriver("tech"),
        }

        def persona_driver_factory(pk: str):
            return drivers[pk]

        printed: list[str] = []
        catchup_selection_queue: list[str] = []

        def human_responder(prompt: str = "") -> str:
            if "Deine Aktion" in prompt:
                return "Ich sichere die Position."
            if prompt.startswith("Welche jetzt spielen lassen?"):
                return catchup_selection_queue.pop(0) if catchup_selection_queue else ""
            raise AssertionError(f"unerwarteter Prompt: {prompt!r}")

        session = TuiSession(
            onboarding_dir, catalog_dir, HUMAN_PK,
            input_fn=human_responder, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=gm_transport_factory,
            persona_driver_factory=persona_driver_factory,
        )
        session._excluded_personas.update({"medic", "tech", "pyro"})

        session._cmd_local_round([])  # sniper -> Abschnittszahl 1.
        catchup_selection_queue.append("cqb,face")
        session._cmd_catch_up_personas()  # [3] Catch-up -> cqb/face auf Paritaet (1).
        counts_mid = core_store.sections_played_by_participant(run_dir)
        assert counts_mid.get("cqb", 0) == 1 and counts_mid.get("face", 0) == 1, counts_mid

        printed.clear()
        catchup_selection_queue.append("cqb,face")
        session._cmd_catch_up_personas(vorspielen=True)  # [5] Vorspielen.

        out = "\n".join(printed)
        assert "blockiert/kein Fortschritt: (keine)" in out, out
        counts_after = core_store.sections_played_by_participant(run_dir)
        assert counts_after.get("cqb", 0) == 2 and counts_after.get("face", 0) == 2, (
            f"Vorspielen ueber [5] haette cqb/face je +1 Abschnitt bringen muessen "
            f"(vorher {counts_mid}, nachher {counts_after})."
        )


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
