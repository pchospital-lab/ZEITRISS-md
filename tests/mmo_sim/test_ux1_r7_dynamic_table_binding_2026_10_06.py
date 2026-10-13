#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_r7_dynamic_table_binding_2026_10_06.py — W27 (ZEITRISS
Terminal UX-1, R7 Phase A): dauerhafte Testdatei fuer den Generalbefund
R6P01 ("freier Harness konfiguriert Solo-Marker, tatsaechliche TUI bindet
Gruppentisch") UND dessen Behebung (BRIEF-W27.md).

R6P01 (wiederholt, mit eigener Lesung bestaetigt): `manual_offline_harness.py`
setzte `table_id`/`section_id` FEST (Solo-Formel) BEVOR T im Hauptmenue
ueberhaupt Gaeste einlaedt. Die echte TUI bindet bei Gaesten einen ANDEREN
Namensraum (`ui/tui.py:_cmd_local_round`, `local-<leader>[-<sortierte
invited_ids>]`) bzw. nach einer zweiten Runde eine generationsweise
hochgezaehlte Kennung (`core/store.py:create_table_from_offer_log`,
`<table_id>__2`, ...). Ein GM-Double mit falschen Qualifiern kann
`core.completion_marker.completion_marker_matches` nie erfuellen -- der
Abschnitt bleibt am echten Tisch offen.

Fix (`_ux1_r5_synthetic_creation_support.py`, R7/W27): `CreationCapableSmartGmServer`
unterstuetzt jetzt einen DYNAMISCHEN Modus (`table_id=None, section_id=None`
+ `leader_id`/`run_dir`) -- `resolve_own_open_table_id()` liest AUSSCHLIESSLICH
den bereits vom echten Produktionscode persistierten Zustand unter
`run_dir/tables/*.json` (derselbe Pfad wie `core/store.py:Table.persist`).
Kein Raten, keine feste Solo-Annahme.

Drei Szenarien, ECHTE eigenstaendige Subprozesse (kein In-Prozess-
`TuiSession`-Aufruf), Muster wie `test_ux1_r6_synthetic_two_plus_three_
journey_2026_10_06.py`:

  test_r6p01_negative_fixed_solo_marker_rejected_then_positive_dynamic_
  binding_closes_real_group_table: Prozess 1 verwendet (bewusst, zur
  Reproduktion) den ALTEN, FESTEN Solo-`table_id`/`section_id` gegen einen
  TATSAECHLICHEN Gruppentisch (Leader + 1 eingeladene KI) -- Negativbeleg:
  trotz eines echten, inhaltlich vollstaendigen Zugs bleibt der Tisch
  `status=active`, KEIN `COMPLETION_MARKER`/`Abschnitt abgeschlossen:` in
  der Ausgabe (`completion_marker_matches` lehnt die falschen Qualifier am
  echten Tisch ab). Prozess 2 (ECHTER SEPARATER Subprozess, DIESELBE
  Datenroot, dieselbe noch offene Runde) verwendet den NEUEN dynamischen
  Modus -- Positivbeleg: derselbe Tisch erreicht echtes `closed`, inkl.
  gueltigem Save/Lockzustand UND einem Debrief-Block, der zu BEIDEN
  tatsaechlichen Mitgliedern passt (nicht nur kosmetisch die Markerzeile).

  test_solo_dynamic_binding_closes_real_section: derselbe dynamische Modus
  OHNE jede Einladung (Solo) -- die Ableitung darf den Solo-Fall nicht
  verschlechtern.

  test_second_round_after_close_dynamic_binding_resolves_new_generation:
  NACH einem echten Abschluss (Tisch `status=closed`) startet eine ZWEITE
  Runde mit derselben Gruppe -- `create_table_from_offer_log` liefert dafuer
  eine generationsweise hochgezaehlte Kennung (`<table_id>__2`). Der
  dynamische GM-Double muss bei JEDEM Abschlussversuch FRISCH ableiten und
  darf den geschlossenen Runde-1-Tisch NICHT mehr als Kandidat sehen --
  sonst waere `resolve_own_open_table_id` zweideutig (0 oder 2 Treffer,
  beide ein Fehler, kein Raten).

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs,
ECHTE eigenstaendige Subprozesse."""
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

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER  # noqa: E402

from _ux1_r5_synthetic_creation_support import (  # noqa: E402
    CreationCapableSmartGmServer,
    resolve_own_open_table_id,
    NoOwnTableYetError,
    AmbiguousOwnTableError,
)
from _ux1_r6_persona_loopback_support import PersonaLoopbackServer  # noqa: E402
import _a24_local_support as sup  # noqa: E402

_LEADER_MOVE_1 = "Leader-Zug-1-W27 (R6P01-Nachweis, falscher fester Marker)."
_LEADER_MOVE_2 = "Leader-Zug-2-W27 (dynamische Ableitung, echter Abschluss)."
_NOTE_LEADER = "Notiz-W27-Leader: Runde war in Ordnung (lokal, nicht fuer die SL)."
_SOLO_MOVE_1 = "Solo-Zug-1-W27 (dynamische Ableitung, Solo-Fall)."
_SOLO_NOTE = "Notiz-W27-Solo: alles plangemaess (lokal, nicht fuer die SL)."
_ROUND2_MOVE = "Leader-Zug-R2-W27 (zweite Runde, generationsgebumpter Tisch)."
_ROUND2_NOTE = "Notiz-W27-R2: zweite Runde ebenfalls in Ordnung (lokal)."
_AI_GUEST = "medic"


def _setup_common(root: Path) -> dict:
    registry_dir = root / "registry"
    onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
    states_dir, run_dir = root / "states", root / "run"
    write_test_profile(run_dir)
    return {
        "registry_dir": registry_dir, "onboarding_dir": onboarding_dir, "catalog_dir": catalog_dir,
        "states_dir": states_dir, "run_dir": run_dir,
    }


def test_r6p01_negative_fixed_solo_marker_rejected_then_positive_dynamic_binding_closes_real_group_table():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        d = _setup_common(root)
        registry_dir, onboarding_dir = d["registry_dir"], d["onboarding_dir"]
        states_dir, run_dir = d["states_dir"], d["run_dir"]

        leader = sup.register_human(registry_dir, "LeaderW27")
        leader_id = leader.participant_id
        sup.onboard_human_figure(
            registry_dir, leader_id, onboarding_dir, states_dir, run_dir,
            "CHR-W27-LEAD", "LeadW27", "LEADOPS",
        )
        sup.make_ready(onboarding_dir, states_dir, run_dir, _AI_GUEST)

        guest_tokens = [f"persona:{_AI_GUEST}"]
        # NUR fuer die Testassertion (das Testdesign darf das wissen) --
        # NICHT an den GM-Double gegeben, s. Moduldocstring.
        expected_table_id = sup.compute_table_id(leader_id, [_AI_GUEST])
        expected_section_id = f"{expected_table_id}-section"

        # -----------------------------------------------------------------
        # Prozess 1: R6P01-NEGATIV -- GM-Double mit dem ALTEN, FESTEN
        # Solo-table_id/section_id (genau das Muster des unbehobenen
        # `manual_offline_harness.py`) gegen den tatsaechlichen Gruppentisch.
        # -----------------------------------------------------------------
        wrong_table_id = f"local-{leader_id}"
        wrong_section_id = f"{wrong_table_id}-section"
        assert wrong_table_id != expected_table_id, "Testaufbau ungueltig: Solo- und Gruppen-ID duerfen nicht zufaellig gleich sein."

        with CreationCapableSmartGmServer(
            table_id=wrong_table_id, section_id=wrong_section_id, complete_after=1,
        ) as gm1, PersonaLoopbackServer() as persona1:
            env1 = {
                "OPENWEBUI_URL": gm1.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC_W27_KEY",
                "MMO_SIM_PERSONA_API_BASE_URL": persona1.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTHETIC_W27_KEY", "MMO_SIM_PERSONA_API_MODEL": "synthetic-w27",
            }
            stdin1 = (
                "l " + " ".join(guest_tokens) + "\n"
                + "j\n"
                + _LEADER_MOVE_1 + "\n"
            )
            p1 = sup.run_process(root, leader_id, stdin1, env1, timeout=40)
            assert p1.returncode == 0, f"Prozess 1 fehlgeschlagen: rc={p1.returncode}\n{p1.stderr}"
            out1 = p1.stdout

            assert "Gruppe eingeladen" in out1, out1[-1500:]
            decisions = {c["participant_id"]: c["decision"] for c in persona1.decision_calls}
            assert decisions.get(_AI_GUEST) == "accept", f"echte accept-Entscheidung erwartet: {decisions}"

            table1 = core_store.Table.load(run_dir, expected_table_id)
            assert set(table1.members) == {leader_id, _AI_GUEST}, table1.members
            assert table1.table_id == expected_table_id, (
                f"Testdesign-Annahme ungueltig -- echter table_id {table1.table_id!r} "
                f"weicht von der unabhaengig berechneten Erwartung {expected_table_id!r} ab."
            )

            # -- R6P01 NEGATIV (Kernbeleg): der GM-Double hat einen echten
            # v7-Block gesehen (Leaderanker) UND `complete_after=1` erreicht,
            # sendet also tatsaechlich eine COMPLETION_MARKER-Zeile -- aber
            # mit den FALSCHEN (Solo-)Qualifiern. Der echte Client lehnt sie
            # am Gruppentisch ab: KEIN "Abschnitt abgeschlossen:", Tisch
            # bleibt `active`.
            assert len(gm1.calls) >= 1, "GM-Double muss mindestens einen Spielzug real erhalten haben."
            assert "Abschnitt abgeschlossen:" not in out1, (
                f"R6P01-Negativ verletzt: der falsche feste Solo-Marker darf am echten "
                f"Gruppentisch NICHT zum Abschluss fuehren: {out1[-1500:]}"
            )
            table1_after = core_store.Table.load(run_dir, expected_table_id)
            assert table1_after.status == "active", (
                f"R6P01-Negativ verletzt: Tisch darf bei falschem Marker nicht geschlossen sein: "
                f"{table1_after.status}"
            )

        # -----------------------------------------------------------------
        # Prozess 2: R6P01-POSITIV -- ECHTER SEPARATER Subprozess, DIESELBE
        # Datenroot, DIESELBE noch offene Runde. GM-Double jetzt im
        # DYNAMISCHEN Modus (kein fester table_id/section_id) -- muss den
        # tatsaechlichen Tisch selbst finden.
        # -----------------------------------------------------------------
        with CreationCapableSmartGmServer(
            leader_id=leader_id, run_dir=run_dir, complete_after=1,
        ) as gm2, PersonaLoopbackServer() as persona2:
            env2 = {
                "OPENWEBUI_URL": gm2.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC_W27_KEY_P2",
                "MMO_SIM_PERSONA_API_BASE_URL": persona2.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTHETIC_W27_KEY_P2", "MMO_SIM_PERSONA_API_MODEL": "synthetic-w27-p2",
            }
            # Kein zweites 'j' hier (empirisch bestaetigt, Debug-Lauf
            # W27): eine bereits reale, noch offene Runde mit UNVERAENDERTER
            # Besetzung fragt beim erneuten 'l <dieselben Tokens>' keine
            # zweite Startbestaetigung mehr ab (nur eine NEUE Besetzung
            # verlangt 'j') -- ein zusaetzliches 'j' hier wuerde als
            # Spielzugtext fehlinterpretiert und die restliche Eingabe um
            # eine Zeile verschieben.
            stdin2 = (
                "l " + " ".join(guest_tokens) + "\n"
                + _LEADER_MOVE_2 + "\n"
                + _NOTE_LEADER + "\n"
            )
            p2 = sup.run_process(root, leader_id, stdin2, env2, timeout=40)
            assert p2.returncode == 0, f"Prozess 2 fehlgeschlagen: rc={p2.returncode}\n{p2.stderr}"
            out2 = p2.stdout

            assert "Gruppe eingeladen" in out2, (
                f"Prozess 2 muss die zuvor noch offene Runde real ueber denselben Einladungsweg "
                f"wiedererkennen: {out2[-1000:]}"
            )

            # -- R6P01 POSITIV (Kernbeleg): derselbe Weg (dynamische
            # Ableitung statt fester Qualifier) bindet jetzt den
            # TATSAECHLICHEN Tisch -- echtes closed.
            assert COMPLETION_MARKER in out2, out2[-1500:]
            assert "Abschnitt abgeschlossen:" in out2, out2[-1500:]
            table2 = core_store.Table.load(run_dir, expected_table_id)
            assert table2.status == "closed", table2.status
            assert set(table2.members) == {leader_id, _AI_GUEST}, (
                f"Mitgliedschaft darf sich beim Abschluss NICHT aendern: {table2.members}"
            )

            # Unabhaengige Gegenprobe: `resolve_own_open_table_id` findet
            # NACH dem Abschluss keinen offenen Tisch mehr (der jetzt
            # geschlossene faellt aus den Kandidaten).
            try:
                resolve_own_open_table_id(run_dir, leader_id)
                raise AssertionError("nach dem Abschluss darf kein offener eigener Tisch mehr gefunden werden")
            except NoOwnTableYetError:
                pass

            # -- Debrief-Mitglieder-Check: die ECHTE lokale Notiz des
            # Leaders landet unter der korrekten `section_id`, NICHT im
            # sl_log (02 §F, wie im 2+3-Journey-Test etabliert).
            reflections = sup.read_jsonl(run_dir / "reflections.jsonl")
            human_notes = {
                r["persona_key"]: r.get("text") for r in reflections
                if r.get("kind") == "human_note" and r.get("section_id") == expected_section_id
            }
            assert human_notes.get(leader_id) == _NOTE_LEADER, human_notes
            ai_reflections = {
                r["persona_key"] for r in reflections
                if r.get("kind") == "ai_required_reflection" and r.get("section_id") == expected_section_id
            }
            assert ai_reflections == {_AI_GUEST}, (
                f"Pflicht-KI-Reflexion muss real ueber den Persona-Loopback abgegeben worden sein "
                f"(sonst waere der Tisch oben gar nicht closed): {ai_reflections}"
            )
            table_data = (run_dir / "tables" / f"{expected_table_id}.json").read_text(encoding="utf-8")
            assert _NOTE_LEADER not in table_data, "lokale Notiz darf NIE am Tisch/SL landen"

            # -- Idempotenz (Brief-Pflicht): der Guest hatte bereits in
            # Prozess 1 real zugesagt. Der Neustart (Prozess 2) ruft 'l'
            # erneut auf derselben, noch offenen Runde auf -- ob dabei ein
            # zweiter HTTP-Entscheidungsrequest fuer DIESELBE Operation
            # gestellt wird, haengt an `round_section_id` (NEU pro
            # `_cmd_local_round`-Aufruf, s. `ui/tui.py` Kommentar
            # "End-Critic-Nacharbeit"). Harter Beleg hier: KEINE zweite
            # abweichende Entscheidung fuer denselben participant_id (kein
            # Flip accept->reject durch einen zweiten, widerspruechlichen
            # Request) -- falls ein zweiter Request gestellt wurde, bleibt
            # er inhaltlich IDENTISCH (weiterhin "accept").
            decisions2 = {c["participant_id"]: c["decision"] for c in persona2.decision_calls}
            if _AI_GUEST in decisions2:
                assert decisions2[_AI_GUEST] == "accept", (
                    f"ein erneuter Request fuer dieselbe, bereits zugesagte Einladung darf keine "
                    f"widersprechende Entscheidung erzeugen: {decisions2}"
                )


def test_solo_dynamic_binding_closes_real_section():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        d = _setup_common(root)
        registry_dir, onboarding_dir = d["registry_dir"], d["onboarding_dir"]
        states_dir, run_dir = d["states_dir"], d["run_dir"]

        leader = sup.register_human(registry_dir, "SoloW27")
        leader_id = leader.participant_id
        sup.onboard_human_figure(
            registry_dir, leader_id, onboarding_dir, states_dir, run_dir,
            "CHR-W27-SOLO", "SoloW27", "SOLOOPS",
        )
        expected_table_id = sup.compute_table_id(leader_id, [])
        assert expected_table_id == f"local-{leader_id}"

        with CreationCapableSmartGmServer(
            leader_id=leader_id, run_dir=run_dir, complete_after=1,
        ) as gm, PersonaLoopbackServer() as persona:
            env = {
                "OPENWEBUI_URL": gm.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC_W27_SOLO_KEY",
                "MMO_SIM_PERSONA_API_BASE_URL": persona.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTHETIC_W27_SOLO_KEY", "MMO_SIM_PERSONA_API_MODEL": "synthetic-w27-solo",
            }
            stdin = "l\n" + _SOLO_MOVE_1 + "\n" + _SOLO_NOTE + "\n"
            p = sup.run_process(root, leader_id, stdin, env, timeout=40)
            assert p.returncode == 0, f"Prozess fehlgeschlagen: rc={p.returncode}\n{p.stderr}"
            out = p.stdout

            assert COMPLETION_MARKER in out, out[-1500:]
            assert "Abschnitt abgeschlossen:" in out, out[-1500:]
            table = core_store.Table.load(run_dir, expected_table_id)
            assert table.status == "closed", table.status
            assert set(table.members) == {leader_id}, table.members


def test_second_round_after_close_dynamic_binding_resolves_new_generation():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        d = _setup_common(root)
        registry_dir, onboarding_dir = d["registry_dir"], d["onboarding_dir"]
        states_dir, run_dir = d["states_dir"], d["run_dir"]

        leader = sup.register_human(registry_dir, "RoundTwoW27")
        leader_id = leader.participant_id
        sup.onboard_human_figure(
            registry_dir, leader_id, onboarding_dir, states_dir, run_dir,
            "CHR-W27-R2", "RoundTwoW27", "R2OPS",
        )
        expected_table_id_r1 = sup.compute_table_id(leader_id, [])
        expected_table_id_r2 = f"{expected_table_id_r1}__2"

        # Runde 1: dynamische Ableitung, echter Abschluss (Vorbedingung
        # fuer die generationsweise Hochzaehlung in Runde 2).
        with CreationCapableSmartGmServer(
            leader_id=leader_id, run_dir=run_dir, complete_after=1,
        ) as gm1, PersonaLoopbackServer() as persona1:
            env1 = {
                "OPENWEBUI_URL": gm1.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC_W27_R2_KEY1",
                "MMO_SIM_PERSONA_API_BASE_URL": persona1.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTHETIC_W27_R2_KEY1", "MMO_SIM_PERSONA_API_MODEL": "synthetic-w27-r2a",
            }
            stdin1 = "l\n" + _LEADER_MOVE_1 + "\n" + _NOTE_LEADER + "\n"
            p1 = sup.run_process(root, leader_id, stdin1, env1, timeout=40)
            assert p1.returncode == 0, f"Runde 1 fehlgeschlagen: rc={p1.returncode}\n{p1.stderr}"
            assert "Abschnitt abgeschlossen:" in p1.stdout, f"Runde 1 muss real abschliessen: {p1.stdout[-1500:]}"
            table_r1 = core_store.Table.load(run_dir, expected_table_id_r1)
            assert table_r1.status == "closed", table_r1.status

        # Vor Runde 2: `resolve_own_open_table_id` findet (noch) keinen
        # offenen Tisch -- der Runde-1-Tisch ist geschlossen, Runde 2 hat
        # noch keinen eigenen angelegt.
        try:
            resolve_own_open_table_id(run_dir, leader_id)
            raise AssertionError("vor Runde 2 darf kein offener Tisch gefunden werden")
        except NoOwnTableYetError:
            pass

        # Runde 2: neue Einladung DERSELBEN (leeren) Gruppe nach Abschluss
        # -> `create_table_from_offer_log` liefert die generationsweise
        # hochgezaehlte Kennung `<table_id>__2` (core/store.py:343-392).
        # Der dynamische GM-Double muss DIESEN neuen Tisch finden, NICHT
        # den geschlossenen Runde-1-Tisch.
        with CreationCapableSmartGmServer(
            leader_id=leader_id, run_dir=run_dir, complete_after=1,
        ) as gm2, PersonaLoopbackServer() as persona2:
            env2 = {
                "OPENWEBUI_URL": gm2.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC_W27_R2_KEY2",
                "MMO_SIM_PERSONA_API_BASE_URL": persona2.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTHETIC_W27_R2_KEY2", "MMO_SIM_PERSONA_API_MODEL": "synthetic-w27-r2b",
            }
            stdin2 = "l\n" + _ROUND2_MOVE + "\n" + _ROUND2_NOTE + "\n"
            p2 = sup.run_process(root, leader_id, stdin2, env2, timeout=40)
            assert p2.returncode == 0, f"Runde 2 fehlgeschlagen: rc={p2.returncode}\n{p2.stderr}"
            out2 = p2.stdout
            assert "Abschnitt abgeschlossen:" in out2, out2[-1500:]
            table_r2 = core_store.Table.load(run_dir, expected_table_id_r2)
            assert table_r2.status == "closed", table_r2.status
            # Runde-1-Tisch bleibt unangetastet geschlossen (kein
            # faelschliches Wiedereroeffnen/Ueberschreiben).
            table_r1_final = core_store.Table.load(run_dir, expected_table_id_r1)
            assert table_r1_final.status == "closed", table_r1_final.status

            reflections = sup.read_jsonl(run_dir / "reflections.jsonl")
            note_r2 = {
                r.get("text") for r in reflections
                if r.get("kind") == "human_note" and r.get("section_id") == f"{expected_table_id_r2}-section"
            }
            assert _ROUND2_NOTE in note_r2, note_r2


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
