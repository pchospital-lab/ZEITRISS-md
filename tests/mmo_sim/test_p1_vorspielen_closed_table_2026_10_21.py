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
            # U3a/R3-Stage2: eigener Notiz-Prompt statt "Deine Aktion:".
            if "Deine persoenliche Abschlussnotiz" in prompt:
                return ""
            if prompt.startswith("Welche jetzt spielen lassen?"):
                return catchup_selection_queue.pop(0) if catchup_selection_queue else ""
            # R4 U3 (01_NACHZUG.md U3 Punkt 3): die jetzt ECHT bedienbare
            # Abschlusskarte liest nach dem echten Abschnittsabschluss
            # unten eine zusaetzliche Auswahl -- dieser Test prueft
            # Vorspielen/Catch-up, nicht die Kartenbedienung, daher hier
            # neutral "Zurueck zum Hauptmenue" (leere Eingabe).
            if prompt.startswith("Auswahl (Nummer, leer/zurueck"):
                return ""
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


def test_flow1_vorspielen_empty_selection_starts_nothing():
    """FLOW-1-Fix (ZR-UPDATE-RESUME-REPARATUR 2026-11-23, 05 §B3, 06 §C6):
    VOR dem Fix waehlte eine leere Eingabe bei [5] (Vorspielen) ALLE
    wahlbaren Kandidaten (`chosen = set(behind)`) -- ein ueberraschender
    Start aller bereiten Personas samt moeglicher B1/B2-gegateter
    Requests, obwohl der Spieler nur "Enter" gedrueckt hat. NACH dem Fix:
    leere Eingabe bei [5] startet explizit NICHTS -- kein Fenster, kein
    Treiberaufruf, keine Abschnittszahl-Aenderung. Catch-up [3] behaelt
    bewusst sein bestehendes "leer = alle"-Verhalten (s.
    test_r4_organic_player_flow_2026_10_21.py, dort NICHT angefasst)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, gm_transport_factory = _bootstrap(root)

        drivers = {
            "cqb": _NeverCalledDriver("cqb"), "face": _NeverCalledDriver("face"),
            "tech": _NeverCalledDriver("tech"), "medic": _NeverCalledDriver("medic"),
            "pyro": _NeverCalledDriver("pyro"),
        }

        def persona_driver_factory(pk: str):
            return drivers[pk]

        printed: list[str] = []

        def human_responder(prompt: str = "") -> str:
            if prompt.startswith("Welche jetzt spielen lassen?"):
                assert "leer/zurueck = nichts ausfuehren" in prompt, (
                    f"Prompt-Hinweistext fuer Vorspielen fehlt/weicht ab: {prompt!r}"
                )
                return ""  # bewusst leer -- muss NICHTS starten.
            raise AssertionError(f"unerwarteter Prompt ohne Antwortregel: {prompt!r}")

        session = TuiSession(
            onboarding_dir, catalog_dir, HUMAN_PK,
            input_fn=human_responder, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=gm_transport_factory,
            persona_driver_factory=persona_driver_factory,
        )
        counts_before = core_store.sections_played_by_participant(run_dir)

        session._cmd_catch_up_personas(vorspielen=True)

        out = "\n".join(printed)
        assert "nichts ausgewaehlt -- kein Fenster gestartet" in out, (
            f"FLOW-1 (vor dem Fix): leere Eingabe haette NICHTS starten sollen:\n{out}"
        )
        # `_NeverCalledDriver.decide()` wirft bei JEDEM Aufruf eine
        # `AssertionError` -- dass dieser Test ueberhaupt hier ankommt,
        # beweist bereits, dass kein Treiber (cqb/face/tech/medic/pyro)
        # befragt wurde.
        counts_after = core_store.sections_played_by_participant(run_dir)
        assert counts_after == counts_before, (
            f"leere Auswahl bei Vorspielen haette KEINE Abschnittszahl aendern duerfen: "
            f"{counts_before} -> {counts_after}"
        )


class _SoloPauseDriver:
    """Deterministischer Solo-Treiber: nimmt an keinem Gruppenangebot teil,
    pausiert in jedem eigenen Lobby-Initiativfenster (`{"action": "pause"}`)
    -- erzwingt `no_consensus`-Fenster ohne Fortschritt, damit das reale
    `idle_safety_cap`/`max_windows`-Verhalten des Orchestrators (nicht nur
    der Gruppenfall) belegt werden kann."""

    def __init__(self, pk: str):
        self.pk = pk
        self.calls: list[dict] = []

    def decide(self, ctx: dict) -> ParticipantDecision:
        self.calls.append(ctx)
        if "begrenztes eigenes Lobby-Initiativfenster" in ctx.get("user", ""):
            return ParticipantDecision(text=json.dumps({"action": "pause"}), origin_source=f"solo:{self.pk}")
        return ParticipantDecision(text="Ich beobachte allein die Lage.", origin_source=f"solo:{self.pk}")


def test_flow1_vorspielen_max_windows_bounds_step_and_resumes():
    """FLOW-1-Fix (05 §B3 'vorhandenes max_windows tatsaechlich setzen,
    z.B. 1 Fenster/Schritt'): ECHTER Produktpfad ueber `TuiSession.
    _cmd_catch_up_personas(vorspielen=True)` (Menuepunkt [5]) -- NICHT nur
    `catchup.run_catch_up` direkt, sondern derselbe Aufruf, den die TUI
    jetzt tatsaechlich mit `max_windows=1` fuettert (vorher gar keine
    `max_windows`-Uebergabe, effektiv der verdeckte Default `catchup.
    DEFAULT_MAX_WINDOWS=200`). Auswahl: cqb/face bilden einen Tisch
    (schliesst in Fenster 1), `tech` ist solo und erreicht NIE einen
    Konsens (`no_consensus` jedes Fenster).

    Separat (nur lesend) gemessen, NICHT Teil dieses Tests: ohne jede
    Fensterbegrenzung braucht genau dieses Szenario fuer EINEN [5]-Druck
    9 echte Lobby-Fenster (1 fuer cqb/face + 8 bis zum alten `idle_safety_
    cap`), s. Report fuer die rohe Messung. Dieser Test beweist die jetzt
    wirksame TUI-Verdrahtung: GENAU EIN Fenster pro Druck auf [5]."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir, gm_transport_factory = _bootstrap(root)

        offer_id = "invite-sniper-cqb-face"
        drivers = {
            "cqb": _GroupGuestDriver("cqb", offer_id, partner="face"),
            "face": _GroupGuestDriver("face", offer_id, partner="cqb"),
            "tech": _SoloPauseDriver("tech"),
            "medic": _NeverCalledDriver("medic"), "pyro": _NeverCalledDriver("pyro"),
        }

        def persona_driver_factory(pk: str):
            return drivers[pk]

        printed: list[str] = []
        catchup_selection_queue: list[str] = []

        def human_responder(prompt: str = "") -> str:
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

        catchup_selection_queue.append("cqb,face,tech")
        session._cmd_catch_up_personas(vorspielen=True)  # Menuepunkt [5], 1. Druck.
        out1 = "\n".join(printed)
        assert "(Fenster: 1," in out1, (
            f"FLOW-1 (vor dem Fix waere hier effektiv der verdeckte Default 200 wirksam "
            f"gewesen -- echt gemessen braucht dieses Szenario ohne Grenze 9 Fenster): "
            f"erwartete 'Fenster: 1' im Abschlussbericht, bekam:\n{out1}"
        )
        counts_mid = core_store.sections_played_by_participant(run_dir)
        assert counts_mid.get("cqb", 0) == 1 and counts_mid.get("face", 0) == 1, (
            f"cqb/face schliessen ihren Tisch bereits in Fenster 1 ab: {counts_mid}"
        )
        assert counts_mid.get("tech", 0) == 0, (
            f"tech findet nie einen Konsens -- muss nach der Fenstergrenze ehrlich offen "
            f"bleiben, nicht erfunden fortgeschritten werden: {counts_mid}"
        )
        assert len(drivers["tech"].calls) == 1, (
            f"tech haette durch die Fenstergrenze nur EINMAL befragt werden duerfen, nicht "
            f"bis zum alten Idle-Sicherheits-Cap (8): {len(drivers['tech'].calls)}"
        )

        # Zweiter bewusster Druck auf [5] -- wieder auf ein Fenster
        # begrenzt, keine automatische Mehrfenster-Fortsetzung.
        printed.clear()
        catchup_selection_queue.append("cqb,face,tech")
        session._cmd_catch_up_personas(vorspielen=True)
        out2 = "\n".join(printed)
        assert "(Fenster: 1," in out2, out2
        assert len(drivers["tech"].calls) == 2, (
            f"der zweite bewusste Schritt darf tech genau EIN weiteres Mal befragen, nicht "
            f"mehrfach automatisch: {len(drivers['tech'].calls)}"
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
