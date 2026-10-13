#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_r5_round_journey_group_sizes_2026_10_06.py — W20/F04
(ZEITRISS Terminal UX-1, R5-Wiederanlauf): die beiden geforderten
Gruppenkonstellationen -- FUeNF MENSCHEN bzw. ZWEI MENSCHEN + DREI
FREIWILLIGE KI -- spielen WIRKLICH mindestens den fuer die jeweilige
Behauptung noetigen Abschnitt (echter Turn/Abschluss, nicht bloss
Zusammenstellung einer Teilnehmerliste), VERBUNDEN mit Fachpunkt 1 (eine der
Personen kommt ueber eine 'neu:'-Registrierung UND echte Erschaffung WAEHREND
derselben Rundenplanung hinzu) -- kein reiner Nachbau des bereits bestehenden
`test_ux1_g01_five_humans_full_flow_2026_10_05.py`/`test_a24_local_two_
humans_2026_10_01.py`, sondern deren Verbindung mit der Erschaffungsreise.

Wiederverwendet die bereits in `test_ux1_r5_round_journey_new_person_
recipients_2026_10_06.py` etablierten Fake-/Antwortgeber-Bausteine (EIN GM
fuer Erschaffung UND Spiel, content-gebunden) -- kein neuer Fake-Mechanismus.

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs."""
from __future__ import annotations

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
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

import _a24_local_support as sup  # noqa: E402
import test_ux1_g03_same_authority_resume_2026_10_05 as g03  # noqa: E402
import test_ux1_r5_round_journey_new_person_recipients_2026_10_06 as journey  # noqa: E402


def test_five_humans_three_existing_two_new_real_segment_no_autoplayer():
    """FUeNF MENSCHEN (0 KI): drei bereits bestehende Figuren + ZWEI NEUE
    Personen aus EINER Setupzeile (Fachpunkt 1 <-> Fachpunkt 2 verbunden) --
    jeder der fuenf Zuege kommt aus einer eigenen, unterscheidbaren
    Antwortgeber-Entscheidung dieses Transkripts, kein Autoplayer."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        registry_dir = root / "registry"
        onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
        states_dir, run_dir = root / "states", root / "run"
        write_test_profile(run_dir)

        existing_names = ["Anke", "Bela", "Cem"]
        existing_chars = [("CHR-W20G-A", "Anke", "ANKEOPS"), ("CHR-W20G-B", "Bela", "BELAOPS"),
                           ("CHR-W20G-C", "Cem", "CEMOPS")]
        leader = sup.register_human(registry_dir, existing_names[0])
        leader_id = leader.participant_id
        others_existing = [sup.register_human(registry_dir, n) for n in existing_names[1:]]
        for pid, c in zip([leader_id] + [p.participant_id for p in others_existing], existing_chars):
            sup.onboard_human_figure(registry_dir, pid, onboarding_dir, states_dir, run_dir, *c)

        creation_gms: dict = {}
        table_box: dict = {}
        printed: list[str] = []
        state = {"prompts": [], "creation_answers": 0}

        # Die sichtbare Auswahlzeile fuer bereits bestehende Menschen nutzt
        # NUMMERN aus genau der Liste, die das Produkt selbst zeigt
        # (`_local_round_list_humans`) -- nicht hartkodiert, da die
        # tatsaechliche Sortierung von den zur Laufzeit zufaelligen
        # Registry-IDs abhaengt.
        probe = TuiSession(onboarding_dir, catalog_dir, leader_id, run_dir=run_dir)
        known = probe._local_round_list_humans()
        others_ids = [pid for pid, _name in known if pid != leader_id]
        assert len(others_ids) == 2, others_ids
        select_line = ",".join(str(i + 1) for i in range(len(others_ids))) + ",neu:Dora,neu:Elia"

        # W26-Haertung (BRIEF-W26.md §1): `moves` ist die UNVERAeNDERLICHE
        # erwartete Zugliste, gegen die unten geprueft wird -- die Eingabe-
        # queue bekommt eine EIGENE Kopie (`list(moves)`). Vorher teilten
        # sich `moves`/`queues["moves"]` dasselbe mutable Listenobjekt;
        # `_resp()` leerte es per `.pop(0)`, wodurch `moves` am Testende
        # bereits leer war und die spaeteren `for text in moves`-Assertions
        # (unten) vakant durchliefen (0 Iterationen = immer "bestanden",
        # ohne je einen Zug wirklich zu pruefen).
        moves = [
            "Leader-Zug 1 (Anker).",
            "Bestehender-Gast-1-Erstzug.",
            "Bestehender-Gast-2-Erstzug.",
            "Neuer-Gast-A-Erstzug.",
            "Neuer-Gast-B-Erstzug.",
        ]
        queues = {"moves": list(moves)}

        def _resp(prompt: str = "") -> str:
            state["prompts"].append(prompt)
            if "Allein mit KI-Mitspielern" in prompt:
                return "2"
            if "Weitere Menschen an diesem Geraet" in prompt:
                return select_line
            if "bestaetigen? [j/n]" in prompt or "uebernehmen? [j/n]" in prompt:
                return "j"
            if prompt == "Auswahl: ":
                return "1"
            if prompt == "Deine Antwort: ":
                state["creation_answers"] += 1
                return f"Standardausruestung #{state['creation_answers']}."
            if "KI-Mitspieler (Nummer/Name" in prompt:
                return ""
            if prompt.startswith("Leader dieser Runde"):
                return ""
            if "Mit dieser Startwahl fortfahren?" in prompt:
                return "j"
            if "beitreten? [j/n]" in prompt:
                return "j"
            if prompt.endswith("Deine Aktion: ") or "] Deine Aktion: " in prompt:
                if queues["moves"]:
                    return queues["moves"].pop(0)
                raise EOFError()
            raise AssertionError(f"W20: unerwarteter Prompt ohne Antwortregel: {prompt!r}")

        session = TuiSession(
            onboarding_dir, catalog_dir, leader_id,
            input_fn=_resp,
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=sup.SCHEMA,
            gm_transport_factory=journey._journey_gm_factory(creation_gms, table_box),
        )
        try:
            session._cmd_local_round_setup()
        except EndOfInput:
            pass
        out = "\n".join(printed)

        assert "Zusammenfassung (5 Spieler einschliesslich Leader)" in out, out[-1500:]
        assert out.count("Neu registriert:") == 2, out[-2000:]
        assert out.count("Erschaffung abgeschlossen.") == 2, out[-2000:]
        assert len(creation_gms) == 2, creation_gms
        for gm in creation_gms.values():
            assert gm.calls == 2, f"echter Zweiturn-Dialog je neuer Person erwartet: {gm.calls}"

        gm = table_box["gm"]
        for text in moves:
            assert any(text in c for c in gm.calls), f"Zugzeile nicht beim SL angekommen (Autoplayer-Verdacht): {text!r}"
        # Kein sechster/zusaetzlicher Call mit identischem Text (keine
        # verdoppelte Verarbeitung derselben Eingabe).
        for text in moves:
            matching = [c for c in gm.calls if text in c]
            assert len(matching) == 1, f"'{text}' sollte genau einmal beim SL ankommen, beobachtet={len(matching)}"
        # W26-Haertung: nach Testende muss die Eingabequeue konkret
        # VOLLSTAeNDIG geleert sein -- sonst waeren weniger echte Zuege
        # verarbeitet worden, als die Testabsicht (5 unterscheidbare Zuege)
        # verlangt, selbst wenn die obigen Pruefungen gegen `moves` bereits
        # bestehen wuerden.
        assert queues["moves"] == [], f"Eingabequeue nicht vollstaendig konsumiert: {queues['moves']}"


def test_two_humans_three_ai_real_consent_and_real_turn_one_new_person():
    """ZWEI MENSCHEN + DREI FREIWILLIGE KI: Leader (bestehend) + eine WAEHREND
    der Planung neu registrierte zweite Person (Fachpunkt 1) + drei KI-
    Personas, die ECHT ueber den Entscheidungsvertrag (`decision_contract`)
    zustimmen und danach real mitspielen (kein KI-Ersatzleader, keine
    automatische Zusage)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        registry_dir = root / "registry"
        onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
        states_dir, run_dir = root / "states", root / "run"
        write_test_profile(run_dir)

        leader = sup.register_human(registry_dir, "LeaderAI")
        leader_id = leader.participant_id
        sup.onboard_human_figure(registry_dir, leader_id, onboarding_dir, states_dir, run_dir, "CHR-W20AI-L", "LA", "LAOPS")
        for pk in ("sniper", "tech", "medic"):
            g03._make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, pk)

        class _AcceptAndPlayDriver:
            """Nimmt GENAU EINE Einladung ECHT an (`decision_contract`-
            Vertrag, derselbe wie `test_ux1_g03_...::_TechDriver`), danach
            ein real unterscheidbarer Spielzug je Aufruf."""

            def __init__(self, pid: str):
                self.pid = pid
                self.calls: list[dict] = []
                self.invite_calls = 0
                self.play_calls = 0

            def decide(self, ctx: dict) -> ParticipantDecision:
                self.calls.append(ctx)
                if "decision_contract" in ctx:
                    self.invite_calls += 1
                    dc = ctx["decision_contract"]
                    text = (
                        f"ENTSCHEIDUNG offer_id={dc['offer_id']} participant_id={dc['participant_id']} "
                        "decision=accept explanation=Ich bin dabei."
                    )
                    return ParticipantDecision(text=text, origin_source=f"w20-ai:{self.pid}")
                if ctx.get("system") == "PRIVATE_REFLECTION_SENTINEL":
                    return ParticipantDecision(text="", origin_source=f"w20-ai:{self.pid}")
                self.play_calls += 1
                return ParticipantDecision(
                    text=f"SYNTHETISCH ({self.pid}, Zug {self.play_calls}): Wir sichern den Bereich.",
                    origin_source=f"w20-ai:{self.pid}",
                )

        ai_drivers = {pk: _AcceptAndPlayDriver(pk) for pk in ("sniper", "tech", "medic")}

        creation_gms: dict = {}
        table_box: dict = {}
        printed: list[str] = []
        state = {"prompts": [], "creation_answers": 0}
        # W26-Haertung (BRIEF-W26.md §1, s. Kommentar im ersten Testfall oben):
        # `moves` bleibt die unveraenderliche erwartete Zugliste, die Queue
        # bekommt eine eigene Kopie.
        moves = [
            "Leader-Zug 1 (Anker, 2+3-KI-Fall).",
            "Neuer-Zweitmensch-Erstzug.",
            "Leader-Zug 2 (nach Erstimport).",
        ]
        queues = {"moves": list(moves)}

        def _resp(prompt: str = "") -> str:
            state["prompts"].append(prompt)
            if "Allein mit KI-Mitspielern" in prompt:
                return "2"
            if "Weitere Menschen an diesem Geraet" in prompt:
                return "neu:Zweit"
            if "bestaetigen? [j/n]" in prompt or "uebernehmen? [j/n]" in prompt:
                return "j"
            if prompt == "Auswahl: ":
                return "1"
            if prompt == "Deine Antwort: ":
                state["creation_answers"] += 1
                return f"Standardausruestung #{state['creation_answers']}."
            if "KI-Mitspieler (Nummer/Name" in prompt:
                return "sniper tech medic"
            if prompt.startswith("Leader dieser Runde"):
                return ""
            if "Mit dieser Startwahl fortfahren?" in prompt:
                return "j"
            if "beitreten? [j/n]" in prompt:
                return "j"
            if prompt.endswith("Deine Aktion: ") or "] Deine Aktion: " in prompt:
                if queues["moves"]:
                    return queues["moves"].pop(0)
                raise EOFError()
            raise AssertionError(f"W20: unerwarteter Prompt ohne Antwortregel: {prompt!r}")

        session = TuiSession(
            onboarding_dir, catalog_dir, leader_id,
            input_fn=_resp,
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=sup.SCHEMA,
            gm_transport_factory=journey._journey_gm_factory(creation_gms, table_box),
            persona_driver_factory=lambda pk: ai_drivers[pk],
        )
        try:
            session._cmd_local_round_setup()
        except EndOfInput:
            pass
        out = "\n".join(printed)

        assert "Zusammenfassung (5 Spieler einschliesslich Leader)" in out, out[-1500:]
        assert out.count("Neu registriert:") == 1, out[-1500:]
        assert out.count("Erschaffung abgeschlossen.") == 1, out[-1500:]
        assert "Gruppe eingeladen" in out, out[-1500:]
        for pk in ("sniper", "tech", "medic"):
            assert pk in out.split("Gruppe eingeladen", 1)[1][:400], out

        # Echter Konsens: jede KI hat GENAU EINMAL den Entscheidungsvertrag
        # ECHT beantwortet (kein automatisches Accept, keine Doppelanfrage).
        for pk, drv in ai_drivers.items():
            assert drv.invite_calls == 1, f"'{pk}': genau EIN echter Einladungs-/Consent-Request erwartet, beobachtet={drv.invite_calls}"
            assert drv.play_calls >= 1, f"'{pk}': mindestens EIN echter Spielzug erwartet (kein reiner Beitritt ohne Zug)"

        offer_log = sup.read_jsonl(run_dir / "invitation_decisions.jsonl")
        consent_from = {e.get("from") for e in offer_log if e.get("type") == "response" and e.get("decision") == "accept"}
        assert {"sniper", "tech", "medic"}.issubset(consent_from), f"Consent-Log fuer alle drei KI unvollstaendig: {offer_log}"

        gm = table_box["gm"]
        for text in moves:
            assert any(text in c for c in gm.calls), f"Zugzeile nicht beim SL angekommen: {text!r}"
        # Mindestens ein echter KI-Spielzug kam ebenfalls beim SL an (nicht
        # nur deren Einladungsantwort).
        ai_play_texts = [c for c in gm.calls if "SYNTHETISCH (" in c]
        assert len(ai_play_texts) >= 1, f"kein echter KI-Spielzug beim SL angekommen: {gm.calls}"
        # W26-Haertung: Eingabequeue muss nach Testende konkret
        # vollstaendig geleert sein (alle 3 Zuege wirklich verarbeitet).
        assert queues["moves"] == [], f"Eingabequeue nicht vollstaendig konsumiert: {queues['moves']}"


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
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
