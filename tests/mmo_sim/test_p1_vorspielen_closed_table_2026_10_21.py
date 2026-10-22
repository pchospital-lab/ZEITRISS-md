#!/usr/bin/env python3
"""
tests/mmo_sim/test_p1_vorspielen_closed_table_2026_10_21.py — Regression fuer
FIX-SPEC-P1234.md P1 (ZR-N2R-ANSCHLUSS-20261019-R4 Compact-Anschluss).

BEFUND (vor dem Fix): `ui.tui.TuiSession._cmd_catch_up_personas` zog fuer
BEIDE Absichten (Catch-up UND Vorspielen) dieselbe Menge
`core.store.current_or_recent_table_members` ab. Dieser Helfer liefert bei
einem gerade freien Spieler (Normalfall direkt NACH einem abgeschlossenen
gemeinsamen Abschnitt) die Mitglieder des zuletzt GESCHLOSSENEN Tisches.
Fuer Vorspielen (Menuepunkt [5]) wurden die Mitspieler eines bereits
abgeschlossenen Gruppenabschnitts (cqb/face) dadurch faelschlich aus dem
waehlbaren Pool entfernt -- Flos ausdruecklich gewuenschter Fall "ich
pausiere, lasse cqb/face ihren naechsten eigenen Abschnitt vorspielen" war
damit ueber [5] unerreichbar.

FIX: `core.store.current_active_table_members` (NEU, nur AKTIV gebundene
Mitglieder, kein Closed-Fallback) wird fuer Vorspielen abgezogen;
Catch-up behaelt `current_or_recent_table_members` unveraendert.

Methode: ECHTER Produktpfad (`TuiSession._cmd_local_round` fuer den
gemeinsamen Abschnitt, `TuiSession._cmd_catch_up_personas(vorspielen=True)`
fuer die Pruefung) -- kein Direktzugriff auf interne Helfer.

Reuse (Leitprinzip "Reuse vor Neubau"): Community-Bootstrap/`_TableGM`/
`_ScriptedDriver`/`_NeverCalledDriver`-Analogon aus
`test_bl1_subset_starvation_2026_10_21.py` und `test_l01_l10_lobby_
initiative.py` -- kein zweiter Bootstrap-Code."""
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
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

HUMAN_PK = "sniper"
AI_PERSONAS = ("tech", "cqb", "face", "medic", "pyro")


class _NeverCalledDriver:
    """Fail-closed-Wache: eine nicht eingeladene/nicht betroffene Persona
    darf in diesem Szenario NIE einen Treiberaufruf bekommen (analog
    `test_bl1_subset_starvation_2026_10_21.py::_NeverCalledDriver`)."""

    def __init__(self, pk: str):
        self.pk = pk

    def decide(self, ctx: dict) -> ParticipantDecision:
        raise AssertionError(f"{self.pk!r} haette in diesem Szenario NIE einen Treiberaufruf bekommen duerfen")


class _GroupGuestDriver:
    """Deterministischer Gast-Treiber: nimmt die Rundeneinladung an
    (`decision_contract`), schlaegt sich im spaeteren Lobby-Initiativfenster
    (Catch-up/Vorspielen) deterministisch mit `partner` zusammen (analog
    `test_bl1_subset_starvation_2026_10_21.py::_PairDriver`) -- kein
    Zufall, kein offener Ausgang."""

    def __init__(self, pk: str, offer_id: str, partner: str | None = None):
        self.pk = pk
        self.offer_id = offer_id
        self.partner = partner
        self.calls: list[dict] = []

    def decide(self, ctx: dict) -> ParticipantDecision:
        self.calls.append(ctx)
        if "decision_contract" in ctx:
            c = ctx["decision_contract"]
            text = f"ENTSCHEIDUNG offer_id={c['offer_id']} participant_id={self.pk} decision=accept"
            return ParticipantDecision(text=text, origin_source=f"p1test:{self.pk}")
        if "begrenztes eigenes Lobby-Initiativfenster" in ctx.get("user", ""):
            if self.partner is not None and self.pk < self.partner:
                text = json.dumps({"action": "propose", "wants": [self.partner]})
            else:
                text = json.dumps({"action": "pause"})
            return ParticipantDecision(text=text, origin_source=f"p1test:{self.pk}")
        return ParticipantDecision(text="Wir beobachten die Lage.", origin_source=f"p1test:{self.pk}")


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


def test_p1_vorspielen_sees_members_of_just_closed_table():
    """Flos Ablauf: sniper+cqb+face schliessen einen Gruppenabschnitt ab ->
    sniper pausiert -> ueber [5] (Vorspielen) MUESSEN cqb/face als wahlbare
    Kandidaten erscheinen (sichtbare Prompt-Zeile, nicht nur die interne
    Menge) und GENAU EINEN eigenen naechsten Abschnitt vorspielen."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, gm_transport_factory = _bootstrap(root)

        offer_id = "invite-sniper-cqb-face"
        drivers = {
            "cqb": _GroupGuestDriver("cqb", offer_id, partner="face"),
            "face": _GroupGuestDriver("face", offer_id, partner="cqb"),
            "tech": _NeverCalledDriver("tech"),
            "medic": _NeverCalledDriver("medic"),
            "pyro": _NeverCalledDriver("pyro"),
        }

        def persona_driver_factory(pk: str):
            return drivers[pk]

        printed: list[str] = []
        catchup_selection_queue: list[str] = []

        def human_responder(prompt: str = "") -> str:
            if "Deine Aktion" in prompt:
                return "Wir sichern die Position und beobachten die Umgebung."
            if prompt.startswith("Welche jetzt spielen lassen?"):
                return catchup_selection_queue.pop(0) if catchup_selection_queue else ""
            raise AssertionError(f"unerwarteter Prompt ohne Antwortregel: {prompt!r}")

        session = TuiSession(
            onboarding_dir, catalog_dir, HUMAN_PK,
            input_fn=human_responder, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=gm_transport_factory,
            persona_driver_factory=persona_driver_factory,
        )

        # Gemeinsamer Gruppenabschnitt sniper+cqb+face -- schliesst nach
        # genau einem Zug (`turns_before_marker=1`).
        session._cmd_local_round(["persona:cqb", "persona:face"])
        out_round = "\n".join(printed)
        assert "nicht angenommen" not in out_round, out_round
        counts = core_store.sections_played_by_participant(run_dir)
        assert counts.get(HUMAN_PK, 0) == 1 and counts.get("cqb", 0) == 1 and counts.get("face", 0) == 1, counts
        table_id = f"local-{HUMAN_PK}-cqb-face"
        closed_table = core_store.Table.load(run_dir, table_id)
        assert closed_table.status == "closed", (
            f"Vorbedingung nicht aufgebaut: der gemeinsame Tisch sollte nach dem Abschnitt "
            f"GESCHLOSSEN sein, ist aber status={closed_table.status!r}."
        )

        # sniper ist jetzt frei (Lock laengst freigegeben) -- `current_or_
        # recent_table_members` liefert bei einem frisch geschlossenen Tisch
        # trotzdem dessen Mitglieder (das ist die eigentliche Fehlerquelle):
        recent = core_store.current_or_recent_table_members(run_dir, HUMAN_PK)
        assert recent == {HUMAN_PK, "cqb", "face"}, recent
        # P1-Fix: der NEUE Helfer liefert fuer einen bereits geschlossenen
        # Tisch die leere Menge (kein aktiver Lock mehr vorhanden).
        active = core_store.current_active_table_members(run_dir, HUMAN_PK)
        assert active == set(), (
            f"P1-Fix nicht wirksam: current_active_table_members haette fuer den bereits "
            f"geschlossenen Tisch die leere Menge liefern muessen, lieferte aber {active!r}."
        )

        printed.clear()
        catchup_selection_queue.append("cqb,face")
        session._cmd_catch_up_personas(vorspielen=True)  # Menuepunkt [5].

        out = "\n".join(printed)
        assert "cqb" in out.split("\n")[0] and "face" in out.split("\n")[0], (
            f"P1 (vor dem Fix): cqb/face fehlen in der sichtbaren 'Wahlbare Kandidaten'-Zeile "
            f"fuer Vorspielen, obwohl ihr gemeinsamer Abschnitt mit sniper bereits abgeschlossen "
            f"ist:\n{out}"
        )
        assert len(drivers["cqb"].calls) >= 2 and len(drivers["face"].calls) >= 2, (
            "cqb/face haetten fuer Vorspielen real befragt werden muessen (Invite + Vorspiel-Zug)."
        )
        counts_after = core_store.sections_played_by_participant(run_dir)
        assert counts_after.get("cqb", 0) == 2 and counts_after.get("face", 0) == 2, (
            f"Vorspielen ueber [5] haette cqb/face je +1 Abschnitt bringen muessen "
            f"(vorher 1, nachher {counts_after.get('cqb')}/{counts_after.get('face')})."
        )
        assert "blockiert/kein Fortschritt: (keine)" in out, out


def test_p1_catchup_still_excludes_currently_bound_table_members():
    """Gegenprobe (Schluessel-Invariante erhalten): solange der Mensch
    AKTIV an einem Tisch gebunden ist (noch NICHT geschlossen), erscheinen
    dessen Mitglieder weder bei Catch-up [3] noch bei Vorspielen [5]."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, gm_transport_factory = _bootstrap(root)

        drivers = {
            "cqb": _GroupGuestDriver("cqb", "invite-sniper-cqb"),
            "tech": _NeverCalledDriver("tech"),
            "face": _NeverCalledDriver("face"),
            "medic": _NeverCalledDriver("medic"),
            "pyro": _NeverCalledDriver("pyro"),
        }

        def persona_driver_factory(pk: str):
            return drivers[pk]

        printed: list[str] = []

        def human_responder(prompt: str = "") -> str:
            if "Deine Aktion" in prompt:
                raise EOFError()  # Pause VOR dem ersten eigenen Zug -- Tisch bleibt aktiv/gebunden.
            raise AssertionError(f"unerwarteter Prompt ohne Antwortregel: {prompt!r}")

        session = TuiSession(
            onboarding_dir, catalog_dir, HUMAN_PK,
            input_fn=human_responder, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=gm_transport_factory,
            persona_driver_factory=persona_driver_factory,
        )
        # Nur cqb ist fuer diese Gegenprobe relevant -- die anderen vier
        # KI-Personas sind bewusst ausgeschlossen (Aktive-Gruppe-Feature),
        # damit die Abzugsmenge isoliert geprueft werden kann (ohne dass
        # sie selbst als Kandidaten fuer Vorspielen auftauchen).
        session._excluded_personas.update({"tech", "face", "medic", "pyro"})
        try:
            session._cmd_local_round(["persona:cqb"])
        except EndOfInput:
            pass  # Tisch bleibt aktiv/gebunden, ungespielt (sl_log=[]).

        table_id = f"local-{HUMAN_PK}-cqb"
        bound_table = core_store.Table.load(run_dir, table_id)
        assert bound_table.status == "active" and bound_table.sl_log == [], (
            f"Vorbedingung nicht aufgebaut: Tisch sollte aktiv UND ungespielt sein "
            f"(status={bound_table.status!r}, sl_log={bound_table.sl_log!r})."
        )

        active = core_store.current_active_table_members(run_dir, HUMAN_PK)
        assert active == {HUMAN_PK, "cqb"}, active
        recent = core_store.current_or_recent_table_members(run_dir, HUMAN_PK)
        assert recent == {HUMAN_PK, "cqb"}, recent

        printed.clear()
        session._cmd_catch_up_personas(vorspielen=True)
        out = "\n".join(printed)
        assert "aktuell keine wahlbaren Kandidaten" in out and "cqb" not in out, (
            f"cqb ist aktiv an sniper gebunden (ungespielter Tisch) und darf auch unter "
            f"Vorspielen NIE als Kandidat auftauchen:\n{out}"
        )
        assert len(drivers["cqb"].calls) == 1, (
            "cqb sollte nur die urspruengliche Rundeneinladung bekommen haben, keinen zweiten "
            f"Treiberaufruf durch Vorspielen: {len(drivers['cqb'].calls)}"
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
