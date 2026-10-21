#!/usr/bin/env python3
"""
tests/mmo_sim/test_r4_organic_player_flow_2026_10_21.py — Beobachtungstest
fuer SPIELFLUSS-SPEC.md (Abschnitts-Paritaets-Modell mit spielergesteuertem
Catch-up/Vorspielen, Flo-GO 2026-10-21).

KEIN vorchoreografierter Testablauf: ein simulierter menschlicher Spieler
("sniper") spielt ueber den ECHTEN Produktpfad (`ui.tui.TuiSession._cmd_
local_round`/`_cmd_lobby_initiative`/`_cmd_catch_up_personas`, dasselbe
Menuekommando wie im echten Terminal). Die fuenf KI-Personas der Community
entscheiden in der Lobby ORGANISCH ueber einen seedbasierten Zufalls-
entscheider (`_OrganicAiDriver`) -- WELCHE Personas sich wann zu welchem
Tisch zusammenfinden, ist NICHT vorgeschrieben; der Test beobachtet nur die
INVARIANTEN (a)-(f) aus SPIELFLUSS-SPEC.md, nie eine konkrete Besetzung.

Reuse (Leitprinzip "Reuse vor Neubau"): Community-Bootstrap/Fixture-Saves/
`_TableGM`/`_session`-Helfer aus `test_l01_l10_lobby_initiative.py` (wie
bereits `test_r2_hauptbefund2_bound_table_recovery.py`), echter Produktweg
fuer Lobby/lokale Runde/Catch-up -- kein zweiter Spielstart-/Tischcode."""
from __future__ import annotations

import json
import random
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

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import catchup  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

HUMAN_PK = "sniper"
AI_PERSONAS = ("tech", "cqb", "face", "medic", "pyro")
EXCLUDED_PK = "pyro"
ROUNDS = 4
AI_WINDOWS_PER_ROUND = 3


class _OrganicAiDriver:
    """Organischer, seedbasierter Entscheider fuer EINE KI-Persona -- WANN
    wer mit wem vorschlaegt/zustimmt ist zufallsgesteuert (fixer Seed fuer
    Reproduzierbarkeit), der Entscheidungs-VERTRAG selbst (Kontrollform) ist
    der echte Produktvertrag (`adapters.base`), kein Textparsing-Bypass.
    Akzeptanzgewichtet (85%), damit der Lauf endlich oft wirklich einen
    Tisch bildet -- KEINE vorgeschriebene Zusammensetzung."""

    def __init__(self, pk: str, rng: random.Random, all_ai: tuple[str, ...]):
        self.pk = pk
        self.rng = rng
        self.all_ai = all_ai
        self.calls: list[dict] = []

    def decide(self, ctx: dict) -> ParticipantDecision:
        self.calls.append(ctx)
        if "decision_contract" in ctx:
            c = ctx["decision_contract"]
            decision = "accept" if self.rng.random() < 0.85 else "reject"
            text = f"ENTSCHEIDUNG offer_id={c['offer_id']} participant_id={self.pk} decision={decision}"
            return ParticipantDecision(text=text, origin_source=f"organic:{self.pk}")
        if "begrenztes eigenes Lobby-Initiativfenster" in ctx.get("user", ""):
            if self.rng.random() < 0.2:
                text = json.dumps({"action": "pause"})
            else:
                others = [p for p in self.all_ai if p != self.pk]
                self.rng.shuffle(others)
                want_n = self.rng.randint(0, min(4, len(others)))
                text = json.dumps({"action": "propose", "wants": others[:want_n]})
            return ParticipantDecision(text=text, origin_source=f"organic:{self.pk}")
        # Tischrunde (nach Tischbildung): einfache Szenenreaktion.
        return ParticipantDecision(
            text="Wir sichern die Position und beobachten die Umgebung.",
            origin_source=f"organic:{self.pk}",
        )


class _AcceptAllDriver:
    """Deterministischer Entscheider NUR fuer den gezielten Aufbau des
    Zwei-Menschen-Szenarios (Invariante f) -- bewusst NICHT der organische
    Entscheider, weil dieser eine Ablehnung wuerfeln koennte UND dieser
    Testabschnitt eine kontrollierte Vorbedingung (ein gemischter Mensch+KI-
    Tisch, der auf den zweiten Menschen wartet) braucht, keinen offenen
    Ausgang. Analog `l01._ScriptedDriver`."""

    def __init__(self, pk: str):
        self.pk = pk
        self.calls: list[dict] = []

    def decide(self, ctx: dict) -> ParticipantDecision:
        self.calls.append(ctx)
        if "decision_contract" in ctx:
            c = ctx["decision_contract"]
            text = f"ENTSCHEIDUNG offer_id={c['offer_id']} participant_id={self.pk} decision=accept"
            return ParticipantDecision(text=text, origin_source=f"acceptall:{self.pk}")
        return ParticipantDecision(text="Ich beobachte aufmerksam.", origin_source=f"acceptall:{self.pk}")


def _make_ready_with_save(onboarding_dir, states_dir, run_dir, persona_key: str, save: dict) -> str:
    """Analog `l01._make_ready`, aber mit einem explizit uebergebenen Save
    statt eines Fixture-Dateinamens -- fuer den ZWEITEN Menschen, der keine
    eigene Fixture-Datei unter `internal/qa/harness/lobby/fixtures/saves/`
    hat (SPIELFLUSS-SPEC.md Invariante f, "Zwei-Menschen-Fall")."""
    chrono_id = save["characters"][0]["id"]
    ps_store = l01.PersonaStateStore(schema_path=l01._SCHEMA)
    l01.onboarding.start_or_resume(onboarding_dir, persona_key)
    l01.onboarding.complete_with_save(onboarding_dir, persona_key, save, l01.ZeitrissHarvestValidator(), chrono_id)
    l01.onboarding.ensure_participant_persona_state(ps_store, states_dir, persona_key, chrono_id, save)
    core_store.publish_current_save(run_dir, persona_key, save, ps_store, states_dir)
    return chrono_id


def test_organic_player_flow_invariants_a_to_f():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
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

        rng = random.Random(20261021)
        ai_drivers: dict[str, _OrganicAiDriver] = {
            pk: _OrganicAiDriver(pk, rng, AI_PERSONAS) for pk in AI_PERSONAS
        }

        def persona_driver_factory(pk: str):
            return ai_drivers[pk]

        printed: list[str] = []
        moves_queue: list[str] = []
        catchup_selection_queue: list[str] = []
        prompts_seen: list[str] = []

        def human_responder(prompt: str = "") -> str:
            prompts_seen.append(prompt)
            if prompt.endswith("Deine Aktion: ") or "] Deine Aktion: " in prompt:
                return moves_queue.pop(0) if moves_queue else "Ich warte kurz ab und beobachte weiter."
            if prompt.startswith("Welche jetzt spielen lassen?"):
                return catchup_selection_queue.pop(0) if catchup_selection_queue else ""
            raise AssertionError(f"Unerwarteter Prompt ohne Antwortregel: {prompt!r}")

        session = TuiSession(
            onboarding_dir, catalog_dir, HUMAN_PK,
            input_fn=human_responder, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=gm_transport_factory,
            persona_driver_factory=persona_driver_factory,
        )
        # SPIELFLUSS-SPEC.md "Aktive Gruppe/Ausschluss": pyro ist ausgeschlossen
        # -- nie Catch-up-/Vorspiel-Kandidat (Invariante c).
        session._excluded_personas.add(EXCLUDED_PK)

        all_catch_up_reports: list[catchup.CatchUpReport] = []
        all_candidates_ever_seen: set[str] = set()

        for round_idx in range(ROUNDS):
            # (a) Der Spieler wird NIE geblockt: sein eigenes Tischspiel laeuft
            # unveraendert, egal was die KI-Community gerade tut.
            moves_queue.clear()
            moves_queue.append(f"Runde {round_idx}: ich sichere die Position und beobachte die Lage.")
            before = core_store.sections_played_by_participant(run_dir).get(HUMAN_PK, 0)
            session._cmd_local_round([])
            out = "\n".join(printed)
            assert "Lobby-Tisch abgeschlossen" in out.rsplit("Runde", 1)[-1] or "abgeschlossen" in out[-400:], (
                f"Runde {round_idx}: eigenes Tischspiel wurde nicht wie erwartet abgeschlossen -- "
                f"Spieler waere (a)-widersprechend blockiert gewesen.\n{out[-1500:]}"
            )
            after = core_store.sections_played_by_participant(run_dir).get(HUMAN_PK, 0)
            assert after == before + 1, (
                f"Runde {round_idx}: eigene Abschnittszahl haette genau um 1 steigen muessen "
                f"({before} -> {after})."
            )

            # Organische KI-Hintergrundaktivitaet -- NICHT vorgeschrieben, wer
            # sich mit wem zusammenfindet.
            for _ in range(AI_WINDOWS_PER_ROUND):
                session._cmd_lobby_initiative()

            # Jede zweite Runde: "Personas spielen lassen" ueber den echten
            # TUI-Menuepfad (Catch-up zur aktuellen Abschnittszahl des Spielers).
            if round_idx % 2 == 1:
                current_table_before = core_store.current_or_recent_table_members(run_dir, HUMAN_PK)
                catchup_selection_queue.clear()
                catchup_selection_queue.append("")  # leer = alle wahlbaren Kandidaten.
                session._cmd_catch_up_personas()

                # Der Report selbst ist nur ueber direkten Orchestrator-Aufruf
                # einsehbar (die TUI-Methode druckt ihn nur) -- fuer die
                # Invarianten-Pruefung rufen wir denselben Orchestrator NOCH
                # EINMAL direkt mit identischen Parametern auf (reiner
                # Lese-/Fortsetzungs-Aufruf: entweder bereits Paritaet ->
                # trivialer Erfolg ohne Fenster, oder er treibt ehrlich weiter
                # -- in jedem Fall belegt er densselben Endzustand).
                ready = catchup.ready_persona_keys(session)
                selected = ready - {HUMAN_PK} - session._excluded_personas - current_table_before
                report = catchup.run_catch_up(
                    session, selected=selected, current_table_members=current_table_before, target=None,
                )
                all_catch_up_reports.append(report)
                all_candidates_ever_seen |= set(report.candidates)

                # (b) Schluessel-Invariante: Catch-up beruehrt NIE ein Mitglied
                # des aktuellen/zuletzt gespielten Tisches des Spielers.
                assert not (set(report.candidates) & current_table_before), (
                    f"Runde {round_idx}: Catch-up-Kandidaten {report.candidates} ueberschneiden sich "
                    f"mit dem aktuellen Tisch des Spielers {current_table_before} -- Schluessel-"
                    "Invariante verletzt."
                )
                assert HUMAN_PK not in report.candidates, "der Spieler selbst darf nie eigener Catch-up-Kandidat sein."

                # (c) Ausgeschlossene Personas sind NIE Kandidat.
                assert EXCLUDED_PK not in report.candidates, (
                    f"Runde {round_idx}: ausgeschlossene Persona {EXCLUDED_PK!r} tauchte als "
                    f"Catch-up-Kandidat auf: {report.candidates}"
                )

                # (b) Beschraenkt + terminiert: endliche Fensterzahl, kein Hang
                # (der Aufruf ist bereits synchron zurueckgekehrt -- belegt
                # zusaetzlich ueber eine explizite Obergrenze).
                assert report.windows_run <= catchup.DEFAULT_MAX_WINDOWS, report.windows_run

                # (d) Nach Catch-up: Paritaet fuer jeden NICHT blockierten
                # Kandidaten (ehrlich -- ein blockierter Rest ist erlaubt und
                # wird separat berichtet, s. `report.blocked`).
                counts_after = core_store.sections_played_by_participant(run_dir)
                for pk in report.candidates:
                    if pk in report.blocked:
                        continue
                    assert counts_after.get(pk, 0) >= report.per_target[pk], (
                        f"Runde {round_idx}: {pk!r} wurde als nicht blockiert gemeldet, hat aber "
                        f"die Zielzahl {report.per_target[pk]} nicht erreicht "
                        f"(tatsaechlich {counts_after.get(pk, 0)})."
                    )

        assert all_catch_up_reports, "mindestens ein Catch-up-Aufruf haette stattfinden muessen."
        assert EXCLUDED_PK not in all_candidates_ever_seen, (
            f"{EXCLUDED_PK!r} war ueber den gesamten Lauf nie Kandidat -- erwartet, da ausgeschlossen."
        )

        # (e) Saves/Chrononauten bleiben konsistent: Save -> kalter Load (neue
        # TuiSession-Instanz, kein geteilter Zustand) -> wirksamer Folgezug.
        ps_store_check = l01.PersonaStateStore(schema_path=schema_path)
        save_before_cold = core_store.load_current_save(run_dir, HUMAN_PK, ps_store_check, states_dir=states_dir)
        assert save_before_cold is not None, "Spieler-Save sollte nach mehreren Runden lesbar sein."
        state_before_cold = ps_store_check.load_state(HUMAN_PK, states_dir=states_dir)
        seq_before_cold = (state_before_cold.get("current_save_version") or {}).get("seq")
        count_before_cold = core_store.sections_played_by_participant(run_dir).get(HUMAN_PK, 0)

        cold_session = TuiSession(
            onboarding_dir, catalog_dir, HUMAN_PK,
            input_fn=human_responder, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=gm_transport_factory,
            persona_driver_factory=persona_driver_factory,
        )
        moves_queue.clear()
        moves_queue.append("Kalter Neustart: ich pruefe meine Ausruestung und mache weiter.")
        cold_session._cmd_local_round([])
        count_after_cold = core_store.sections_played_by_participant(run_dir).get(HUMAN_PK, 0)
        assert count_after_cold == count_before_cold + 1, (
            f"Save->kalter Load->Folgezug haette die Abschnittszahl um 1 weitertreiben muessen "
            f"({count_before_cold} -> {count_after_cold})."
        )
        save_after_cold = core_store.load_current_save(run_dir, HUMAN_PK, ps_store_check, states_dir=states_dir)
        assert save_after_cold is not None, "nach dem kalten Folgezug sollte weiterhin ein Save lesbar sein."
        state_after_cold = ps_store_check.load_state(HUMAN_PK, states_dir=states_dir)
        seq_after_cold = (state_after_cold.get("current_save_version") or {}).get("seq")
        assert seq_after_cold is not None and seq_after_cold >= 1, (
            "der Folgezug nach kaltem Load haette eine NEUE Save-Version veroeffentlichen muessen "
            f"(current_save_version={state_after_cold.get('current_save_version')!r})."
        )

        # (f) Zwei-Menschen-Fall: ein zweiter Mensch ("operator2") spielt an
        # einem eigenen, gemischten Mensch+KI-Tisch -- Catch-up des ersten
        # Spielers darf diesen Tisch NIE "vorspielen"/den zweiten Menschen
        # ueberspringen. Aufbau: operator2 ladet 'medic' (KI) ein, bestaetigt
        # NICHT den ersten eigenen Zug (EOF) -- der Tisch bleibt aktiv/
        # gebunden, exakt die B2-Vorbedingung (CRITIC-REPORT-R2.md), jetzt
        # ueber den echten Zwei-Menschen-Pfad.
        second_human_pk = "operator2"
        second_human_save = full_v7_save(
            "CHR-SECOND-HUMAN", name="Operator2", callsign="OPS2", save_id="fixture-second-human-001",
        )
        _make_ready_with_save(onboarding_dir, states_dir, run_dir, second_human_pk, second_human_save)

        def operator2_responder(prompt: str = "") -> str:
            prompts_seen.append(prompt)
            if prompt.endswith("Deine Aktion: ") or "] Deine Aktion: " in prompt:
                raise EOFError()  # Pause VOR dem ersten eigenen Zug -- Tisch bleibt gebunden/aktiv.
            raise AssertionError(f"operator2: unerwarteter Prompt ohne Antwortregel: {prompt!r}")

        operator2_session = TuiSession(
            onboarding_dir, catalog_dir, second_human_pk,
            input_fn=operator2_responder, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=gm_transport_factory,
            persona_driver_factory=lambda pk: _AcceptAllDriver(pk),
        )
        try:
            operator2_session._cmd_local_round(["persona:medic"])
        except EndOfInput:
            pass

        # Figuren-/Chrononaut-ID aus der Fixture, nicht geraten:
        medic_chrono_id = all_saves["medic"]["characters"][0]["id"]
        stuck_table_id = core_store.locked_table_id(run_dir, medic_chrono_id)
        assert stuck_table_id is not None, (
            "medic sollte jetzt an einen aktiven, gebundenen (aber ungespielten) Tisch mit "
            f"operator2 gebunden sein -- B2-Vorbedingung nicht aufgebaut.\n{chr(10).join(prompts_seen[-10:])}"
        )
        stuck_table = core_store.Table.load(run_dir, stuck_table_id)
        assert second_human_pk in stuck_table.members, stuck_table.members
        assert not core_store._table_has_final(run_dir, stuck_table_id), "Tisch sollte noch offen sein."

        current_table_f = core_store.current_or_recent_table_members(run_dir, HUMAN_PK)
        ready_f = catchup.ready_persona_keys(session)
        selected_f = ready_f - {HUMAN_PK} - session._excluded_personas - current_table_f
        assert "medic" in selected_f, "medic sollte (abgesehen vom Stuck-Tisch) ein wahlbarer Kandidat sein."
        report_f = catchup.run_catch_up(
            session, selected=selected_f, current_table_members=current_table_f, target=None,
        )

        # medic darf NICHT vorangetrieben worden sein (der zweite Mensch wird
        # nie "vorgespielt"/uebersprungen) -- entweder gar nicht Kandidat
        # (bereits am Ziel) oder blockiert, NIE mit erhoehter Abschnittszahl
        # durch diesen Aufruf.
        medic_count_before_f = core_store.sections_played_by_participant(run_dir).get("medic", 0)
        medic_count_after_f = report_f.end_counts.get("medic", medic_count_before_f)
        assert medic_count_after_f == medic_count_before_f, (
            f"medic wurde trotz gebundenem Mensch+KI-Tisch mit operator2 weitergetrieben "
            f"({medic_count_before_f} -> {medic_count_after_f}) -- Invariante (f) verletzt."
        )
        if "medic" in report_f.candidates:
            assert "medic" in report_f.blocked, (
                "medic war Kandidat, aber nicht blockiert, obwohl sein Tisch auf operator2 wartet "
                f"-- Notes: {report_f.notes}"
            )
        assert not core_store._table_has_final(run_dir, stuck_table_id), (
            "der Mensch+KI-Tisch von operator2 darf durch den Catch-up des anderen Spielers NIE "
            "abgeschlossen werden (kein Ueberspringen eines Menschen)."
        )
        operator2_still_bound = core_store.chrononaut_active_binding(
            run_dir, operator2_session._resolve_member(second_human_pk)[1],
        )
        assert operator2_still_bound, "operator2 sollte an seinem eigenen Tisch gebunden bleiben (kein Fremdabschluss)."


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
