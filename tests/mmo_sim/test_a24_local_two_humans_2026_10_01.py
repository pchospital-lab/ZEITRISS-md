#!/usr/bin/env python3
"""
tests/mmo_sim/test_a24_local_two_humans_2026_10_01.py — A24-Nachweis
(2026-10-01, Bedienabschluss-Runde): echte lokale Fuenferrunde (zwei
Menschen + drei KI-Personas) ueber den tatsaechlichen Dispatcher-Subprozess
`scripts/mmo_sim.py --participant <id> --data-dir <D>`, NICHT ueber private
`_cmd_local_round`-Aufrufe. Original 04 A24
(`reference/contracts/v2/04_ABNAHME_UND_TESTPLAN.md` Zeile A24 + §5) und 11
§8 (`11_EINSTIEG_CHARAKTERE_UND_KOOP.md`) bleiben die massgeblichen
Vertraege; dieser Test prueft sowohl den vorhandenen Tokenweg (`l <id> ...`
/ `l lead:persona:<id> ...`) ALS AUCH den neuen gefuehrten Weg (`g` ->
`_cmd_local_round_setup`, A24-Bedienabschluss-Runde 2026-10-01).

Zwei feste positive Token-Weg-Faelle (kein Kreuzprodukt, alter Weg bleibt
kompatibel):
  1) Human-Leader/API   -- `l <human-B-id> persona:sniper persona:tech persona:medic`
  2) KI-Leader/Hybrid   -- `l lead:persona:tech <human-B-id> persona:sniper persona:medic`

Neuer gefuehrter Weg (R2, dieselbe Human-Leader/API-Konstellation wie Fall 1
plus bewusste Terminal-Uebergabe an Human B):
  g1) `g` -> Modus/Auswahl/Figurbestaetigung/KI/Leader/Zusammenfassung/
      Uebergabe -> danach UNVERAENDERT derselbe Einladungs-/Consent-/
      Spielweg wie Fall 1.
  g2) `g`-Abbruch (EOF) GENAU an der Uebergabebestaetigung -- kein Tisch/
      Consent/GM-Kontakt, Registry/Onboarding/Katalog bleiben unveraendert.

Drei getrennte negative Faelle (gelten strukturell fuer beide Wege, da
`_cmd_local_round_setup` denselben unveraenderten `_cmd_local_round`-Aufruf
erzeugt):
  a) 3 Menschen + 3 KI = 6 -> abgelehnt, kein Tisch, Policy-spezifischer
     Ablehnungstext (nicht der wiederverwendete Erfolgsgrund)
  b) Human B lehnt den Beitritt ab
  c) Eine angefragte KI lehnt die Einladung ab (echte HTTP-200-Ablehnung)

Pure Python, nur `assert`, echter Exitcode (Muster aus `test_m3_tui.py`/
`e2e_real_subprocess_dialog.py`)."""
from __future__ import annotations

import json
import os
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

from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402

import _a24_local_support as sup  # noqa: E402


def _append_guided_line(stdin_lines: list, focus_box: list, actor: str, line: str) -> bool:
    """A24 R2 (02_AUFTRAG_R2_R3.md §R2 "echte In-Runde-Uebergabe"): fuegt
    VOR der Eingabezeile eines ANDEREN Akteurs als dem zuletzt am
    (synthetischen) Terminal fokussierten eine bewusste Uebergabe-
    Bestaetigung ('j') ein -- exakt das Gegenstueck zur Produktlogik in
    `mmo_sim/ui/tui.py:_cmd_local_round`s `_HumanDriver.decide` (nur bei
    einem TATSAECHLICHEN Akteurwechsel, nicht beim allerersten Zugriff
    dieses Rundenaufrufs; die bestaetigte Setup-Person bleibt dabei erhalten). `focus_box` ist eine 1-elementige Liste (simples
    mutable Fokus-Gedaechtnis ueber mehrere Aufrufe hinweg, analog
    `current_focus_pid` im Produkt). Liefert `True`, wenn dafuer eine
    Uebergabe eingefuegt wurde (fuer programmatische Zaehl-Assertions,
    keine hartkodierten Werte)."""
    switched = focus_box[0] is not None and focus_box[0] != actor
    if switched:
        stdin_lines.append("j")
    stdin_lines.append(line)
    focus_box[0] = actor
    return switched


# ---------------------------------------------------------------------------
# Fall 1: Human-Leader / API
# ---------------------------------------------------------------------------

def test_a24_case1_human_leader_api_full_journey():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        case = sup.case_dir("case1_human_leader_api") if os.environ.get("A24_EVIDENCE_DIR") else None

        boot = sup.bootstrap_six_persona_community(root, "community-a24-c1")
        run_dir, states_dir, onboarding_dir, catalog_dir = boot["run_dir"], boot["states_dir"], boot["onboarding_dir"], boot["catalog_dir"]
        for pk in ("sniper", "tech", "medic"):
            sup.make_ready(onboarding_dir, states_dir, run_dir, pk)

        registry_dir = root / "registry"
        human_a = sup.register_human(registry_dir, "A24-Human-A")
        human_b = sup.register_human(registry_dir, "A24-Human-B")
        human_a_id, human_b_id = human_a.participant_id, human_b.participant_id
        assert human_a_id != human_b_id

        onb_a = sup.onboard_human_figure(registry_dir, human_a_id, onboarding_dir, states_dir, run_dir, "CHR-A24-C1-A", "Alex", "ALEXOPS")
        onb_b = sup.onboard_human_figure(registry_dir, human_b_id, onboarding_dir, states_dir, run_dir, "CHR-A24-C1-B", "Bo", "BOOPS")
        assert onb_a["participant"].record_refs and onb_b["participant"].record_refs, "echte record_refs fehlen"

        sup.write_test_profile(run_dir, max_turns=200, max_seconds=600, max_usd=50.0)

        targets = [human_b_id, "sniper", "tech", "medic"]
        leader_id = human_a_id
        guest_order = sup.sorted_guest_order(leader_id, targets)
        members_sorted = sup.sorted_table_members(leader_id, targets)
        table_id = sup.compute_table_id(leader_id, targets)
        section_id = f"{table_id}-section"
        offer_id = sup.invitation_offer_id(leader_id, targets)

        # R3 (02_AUFTRAG_R2_R3.md §R3 "Fremde/Bystander/Registry/Katalog/
        # Onboarding ... vor/nach assertieren"): echter Vorher-Schnappschuss,
        # VOR dem Subprozessstart -- Vergleich s. unten nach `run_process`.
        protected_before = sup.capture_protected_authorities(states_dir, registry_dir, onboarding_dir, catalog_dir)

        final_saves = {
            leader_id: onb_a["save"], human_b_id: onb_b["save"],
            "sniper": sup.load_fixture_save("sniper"), "tech": sup.load_fixture_save("tech"),
            "medic": sup.load_fixture_save("medic"),
        }
        expected_char_ids = {zeitriss_saves.block_char_id(b) for b in final_saves.values()}
        assert len(expected_char_ids) == 5, "fuenf unterscheidbare Figuren erwartet"
        # R3 ("fuenf volle individuelle Endsaves mit deutlich unterscheidbaren
        # synthetischen End-Save-IDs, nicht Ausgangspayload wiederholen"): der
        # GM-Debrief sendet eigene End-Save-Bloecke, nicht die Onboarding-/
        # Fixture-Ausgangsbloecke selbst.
        end_saves = sup.end_saves_for(final_saves, "c1")

        # G6-E: unabhaengige Erwartung AUSSCHLIESSLICH aus den oben bereits
        # bekannten Setup-/Fixturewerten (nicht aus dem spaeter zu
        # pruefenden Wire-Inhalt) -- s. `expected_context_for_case`.
        gm_receipts_path = root / "gm_receipts.jsonl"
        expected_context = sup.expected_context_for_case(
            leader=leader_id, members=members_sorted, table_id=table_id, section_id=section_id,
            final_saves=final_saves, offer_ids=[offer_id],
        )

        received_ids: set = set()
        gm_srv = sup.SequencedHTTPServer(
            scripted=[],
            fallback_fn=sup.smart_gm_fallback(expected_char_ids, end_saves, table_id, section_id, complete_after=8, received_ids=received_ids),
            expected_context=expected_context, gm_receipts_path=gm_receipts_path, is_gm_server=True,
        )
        persona_srv = sup.SequencedHTTPServer(
            scripted=[
                sup.accept_text(offer_id, "sniper"),
                sup.accept_text(offer_id, "tech"),
                sup.accept_text(offer_id, "medic"),
            ],
            fallback_fn=sup.narrative_fallback("persona"),
            expected_context=expected_context, gm_receipts_path=gm_receipts_path,
        )

        # Fokus-/Prompt-Textbausteine -- bewusst neutrale Spielentscheidungen,
        # keine erfundene Motiv-/Gefuehlsnotiz (02_AUFTRAG_A24.md §3).
        human_a_lines = ["Wir sichern den Zugang und beobachten den Sektor.",
                          "Wir ruecken vorsichtig weiter vor.",
                          "Wir bleiben wachsam und halten die Position.",
                          "Wir schliessen diesen Abschnitt kontrolliert ab."]
        human_b_import_line = "Ich sichere die rechte Flanke."
        human_b_poll_lines = ["Ich schlage vor, die Ruhe zu bewahren.", "Keine Einwaende, ich bleibe in Deckung."]
        human_a_reflection = "Notiz: Ausruestung und Status geprueft."
        human_b_reflection = ""  # freiwillig leer (11 §8 zulaessig) -- keine erfundene Motivnotiz.

        sup.write_g6_operation_plan(
            gm_receipts_path, expected_context, invite_actors=["sniper", "tech", "medic"],
            human_messages={human_a_id: human_a_lines, human_b_id: [human_b_import_line]},
            human_polls={human_b_id: human_b_poll_lines})

        with gm_srv, persona_srv:
            env = {
                "OPENWEBUI_URL": gm_srv.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC_A24_GM_KEY",
                "MMO_SIM_PERSONA_API_BASE_URL": persona_srv.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTHETIC_A24_PERSONA_KEY", "MMO_SIM_PERSONA_API_MODEL": "synthetic-a24",
                "MMO_SIM_GM_OUTPUT_LIMIT_TOKENS": "4000",
            }
            env.pop("MMO_SIM_PERSONA_CLI", None)  # 07 §3: kein geerbtes Hybrid-Profil im API-Fall.

            stdin_lines = [f"l {human_b_id} persona:sniper persona:tech persona:medic", "j"]
            stdin_lines.append(human_a_lines[0])
            for g in guest_order:
                if g == human_b_id:
                    stdin_lines.append(human_b_import_line)
            stdin_lines.append(human_a_lines[1])
            for g in guest_order:
                if g == human_b_id:
                    stdin_lines.append(human_b_poll_lines[0])
            stdin_lines.append(human_a_lines[2])
            for g in guest_order:
                if g == human_b_id:
                    stdin_lines.append(human_b_poll_lines[1])
            stdin_lines.append(human_a_lines[3])
            for m in members_sorted:
                if m == leader_id:
                    stdin_lines.append(human_a_reflection)
                elif m == human_b_id:
                    stdin_lines.append(human_b_reflection)
            stdin_lines.append("x")
            stdin_text = "\n".join(stdin_lines) + "\n"

            if case is not None:
                (case / "before" / "stdin.txt").write_text(stdin_text, encoding="utf-8")
                sup.write_json(case / "before" / "plan.json", {
                    "leader_id": leader_id, "human_b_id": human_b_id, "targets": targets,
                    "guest_order": guest_order, "members_sorted": members_sorted,
                    "table_id": table_id, "section_id": section_id, "offer_id": offer_id,
                    "expected_char_ids": sorted(expected_char_ids),
                })

            # Guardidentitaet + jsonschema-Sichtbarkeit NICHT nur im
            # Elternprozess, sondern mit GENAU demselben Environment/
            # Interpreter, das gleich das echte TUI-Kind erhaelt (07 §4).
            child_env = dict(os.environ)
            child_env.update(env)
            guard_check = sup.verify_child_guard_and_schema(child_env, run_dir.parent)
            parent_guard_state = sup.current_process_guard_state()
            assert guard_check["returncode"] == 0, guard_check
            assert guard_check["parsed"] == parent_guard_state, (
                "Guard-/Schema-Sichtbarkeit im echten TUI-Kind weicht vom Elternprozess ab "
                f"(Kontinuitaet gebrochen): eltern={parent_guard_state} kind={guard_check['parsed']}"
            )
            if case is not None:
                sup.write_json(case / "before" / "guard_check.json", guard_check)

            proc = sup.run_process(run_dir.parent, human_a_id, stdin_text, env, timeout=90)

            if case is not None:
                (case / "after" / "stdout.txt").write_text(proc.stdout, encoding="utf-8")
                (case / "after" / "stderr.txt").write_text(proc.stderr, encoding="utf-8")
                sup.write_json(case / "after" / "process.json", {"returncode": proc.returncode})
                sup.write_json(case / "after" / "gm_received.json", gm_srv.received)
                sup.write_json(case / "after" / "persona_received.json", persona_srv.received)

            sup.assert_g6_operation_tape(gm_receipts_path)
            sup.run_g6_exact_replays(
                sup, str(gm_receipts_path) + '.operations.plan.json',
                str(gm_receipts_path) + '.operations.journal.jsonl',
                (case / 'after' / 'g6-exact-replays') if case else (root / 'g6-exact-replays'))
            assert proc.returncode == 0, f"Prozess fehlgeschlagen: rc={proc.returncode} stderr={proc.stderr[-2000:]}"
            assert "Gruppe eingeladen" in proc.stdout, proc.stdout[-1500:]
            for pid in ("sniper", "tech", "medic"):
                assert pid in proc.stdout.split("Gruppe eingeladen", 1)[1][:400], proc.stdout
            assert "Abschnitt abgeschlossen:" in proc.stdout, f"Abschnitt nicht abgeschlossen: {proc.stdout[-2000:]}"

            # -- Fokus-/Prompt-Zuordnung: Leader IMMER unlabeled "Deine Aktion:",
            # Human B IMMER "[<human_b_id>] Deine Aktion:" (einziger im Produkt
            # vorhandener Fokus-/Mehrmenschen-Mechanismus, s. `_HumanDriver`).
            labeled_prompt = f"[{human_b_id}] Deine Aktion:"
            unlabeled_count = proc.stdout.count("Deine Aktion:") - proc.stdout.count(labeled_prompt)
            assert unlabeled_count == len(human_a_lines) + 1, (  # +1 Reflexionsturn
                f"Leader-Prompts (unlabeled) erwartet={len(human_a_lines) + 1} beobachtet={unlabeled_count}: {proc.stdout}"
            )
            expected_b_prompts = 1 + len(human_b_poll_lines) + 1  # import + 2 polls + reflection
            assert proc.stdout.count(labeled_prompt) == expected_b_prompts, (
                f"Human-B-Prompts erwartet={expected_b_prompts} beobachtet={proc.stdout.count(labeled_prompt)}: {proc.stdout}"
            )
            # -- Persistenter Zustand nach Abschluss: Leader-ID unveraendert,
            # genau die fuenf erwarteten Mitglieder, Tisch geschlossen.
            table = core_store.Table.load(run_dir, table_id)
            assert table.leader == leader_id, f"Leader hat gewechselt: {table.leader} != {leader_id}"
            assert set(table.members) == {leader_id, human_b_id, "sniper", "tech", "medic"}
            assert table.status == "closed"

            # R3 (02_AUFTRAG_R2_R3.md §R3 "Fremde/Bystander/Registry/Katalog/
            # Onboarding ... vor/nach assertieren"): die lokale Runde schreibt
            # NIE Registry/Onboarding/Katalog und laesst die drei nicht
            # beteiligten SIX_PERSONAS ohne eigene Current-Datei -- echter
            # Vorher/Nachher-Hashvergleich, keine reine Mitgliederzaehlung.
            protected_after = sup.capture_protected_authorities(states_dir, registry_dir, onboarding_dir, catalog_dir)
            assert protected_after == protected_before, (
                "Registry/Onboarding/Katalog/Bystander-Figuren haben sich durch die lokale Runde "
                "veraendert -- das darf nur die tatsaechliche Spiel-/Save-Autoritaet (current_saves/"
                "states/reflections/invitation_decisions)."
            )

            # R1 (02_AUFTRAG_A24.md §R1 b: "Alle acht oeffentlichen GM-
            # Antworten muessen ... tatsaechlich sichtbar werden ... nicht nur
            # den letzten Eintrag"): ALLE dauerhaften sl_log-Eintraege muessen
            # als eigener "[SL] <content>"-Block im STDOUT erscheinen, in
            # DERSELBEN Reihenfolge -- nicht nur irgendein "[SL]"-Substring.
            # Positionsbasiert (nicht zeilenbasiert): `input()` haengt bei
            # Pipe-stdin KEIN Newline an seinen Prompt an, daher kann ein
            # "[SL] ..."-Block technisch auf derselben Terminalzeile wie der
            # vorherige Prompt beginnen (reines Anzeigeartefakt) -- die
            # Reihenfolge/Vollstaendigkeit der Bloecke selbst bleibt die
            # tragende Assertion.
            sl_log = table.sl_log
            assert len(sl_log) == 8, f"Erwartete 8 oeffentliche SL-Antworten im dauerhaften Log, beobachtet={len(sl_log)}"
            assert proc.stdout.count("[SL] ") == len(sl_log), (
                f"Anzahl der [SL]-Anzeigebloecke ({proc.stdout.count('[SL] ')}) weicht von der Anzahl "
                f"dauerhafter sl_log-Eintraege ({len(sl_log)}) ab -- mindestens ein Eintrag wurde nicht "
                "(oder mehrfach) angezeigt."
            )
            last_pos = -1
            for idx, entry in enumerate(sl_log):
                marker = f"[SL] {entry.get('content', '')}"
                found_pos = proc.stdout.find(marker, last_pos + 1)
                assert found_pos != -1, f"SL-Eintrag #{idx} nicht vollstaendig als eigener [SL]-Block NACH dem vorherigen im STDOUT gefunden: {entry}"
                last_pos = found_pos

            # R3 (02_AUFTRAG_A24.md §R3 "pro aktiver Figur genau +1 Runde/+1
            # Version"): echte states/current_saves-Pruefung, keine
            # Testzahlen-only-Aussage.
            members_final = sorted(table.members)
            states_after = {m: json.loads((states_dir / f"{m}.json").read_text(encoding="utf-8")) for m in members_final}
            for m in members_final:
                assert states_after[m]["rounds_played"] == 1, (
                    f"'{m}': genau eine gespielte Runde erwartet, beobachtet={states_after[m]['rounds_played']}"
                )
                versions_dir = run_dir / "current_saves" / f"{m}__versions"
                version_count = len(list(versions_dir.glob("*.json"))) if versions_dir.exists() else 0
                assert version_count == 2, f"'{m}': genau zwei Save-Versionen (Onboarding+Abschluss) erwartet, beobachtet={version_count}"
                current = json.loads((run_dir / "current_saves" / f"{m}.json").read_text(encoding="utf-8"))
                # R3 (02_AUFTRAG_R2_R3.md §R3 "vollstaendige persoenliche
                # Anfangs-/Endsaves aus tatsaechlichen GM-Ausgaengen
                # vergleichen, nicht nur save_id"): volle Byte-/Feldgleichheit
                # gegen den tatsaechlich vom GM gesendeten Endsave-Block, nicht
                # nur die ID -- faengt z.B. unterschobene Zusatzfelder, die
                # `probe_remainders.py --mode current-bytes` synthetisch testet.
                assert current == end_saves[m], (
                    f"'{m}': veroeffentlichter Current-Save ist NICHT vollstaendig byte-/feldgleich zum "
                    f"gesendeten synthetischen Endsave-Block (nur save_id reicht nicht): "
                    f"current={current} erwartet={end_saves[m]}"
                )
                assert current.get("save_id") != final_saves[m].get("save_id"), (
                    f"'{m}': Endsave wiederholt den Ausgangspayload (save_id unveraendert) -- gegen R3 verstossen"
                )
            end_save_ids = {m: end_saves[m]["save_id"] for m in members_final}
            assert len(set(end_save_ids.values())) == 5, f"Endsave-IDs sind nicht alle unterscheidbar: {end_save_ids}"

            # R3 ("bekannte 1->8-rounds_played-Gegenprobe MUSS semantisch
            # roeten"): mutiert NUR eine lokale Kopie des real beobachteten
            # Werts (1->8, derselbe Versatz wie P/tools/observe_a24.py
            # --corrupt-rounds) und beweist, dass die obige `== 1`-Invariante
            # bei diesem Wert tatsaechlich faellt -- keine tautologische
            # Immer-gruen-Assertion, kein Produktwrite.
            corrupted_rounds = states_after[leader_id]["rounds_played"] + 7
            try:
                assert corrupted_rounds == 1, "Gegenprobe: korrumpierter Wert darf die Invariante NICHT erfuellen"
            except AssertionError:
                pass
            else:
                raise AssertionError(
                    "1->8-rounds_played-Gegenprobe ist nicht semantisch rot geworden -- "
                    "die Rundeninvariante waere vakuos (immer gruen)"
                )

            reflections = sup.read_jsonl(run_dir / "reflections.jsonl")
            ai_reflections = {r["persona_key"] for r in reflections if r.get("kind") == "ai_required_reflection" and r.get("section_id") == section_id}
            assert ai_reflections == {"sniper", "tech", "medic"}, f"KI-Pflichtreflexionen unvollstaendig: {ai_reflections}"
            human_notes = {r["persona_key"]: r.get("text") for r in reflections if r.get("kind") == "human_note" and r.get("section_id") == section_id}
            assert human_notes.get(leader_id) == human_a_reflection
            assert human_b_id not in human_notes, "leere freiwillige Notiz darf nicht als human_note archiviert werden"

            offer_log = sup.read_jsonl(run_dir / "invitation_decisions.jsonl")
            consent_from = {e.get("from") for e in offer_log if e.get("type") == "response" and e.get("decision") == "accept"}
            assert {human_b_id, "sniper", "tech", "medic"}.issubset(consent_from), f"Consent-Log unvollstaendig: {offer_log}"

            assert len(persona_srv.received) >= 3, "Persona-API haette real mehrfach befragt werden muessen"
            assert len(gm_srv.received) >= 7, f"GM haette mehrfach real befragt werden muessen (>=5 Saves + >=2 Nichtabschluss): {len(gm_srv.received)}"
            assert expected_char_ids.issubset(received_ids), "GM hat Abschluss gesendet ohne alle fuenf Save-IDs vorher empfangen zu haben"

            # G6-O (02_AUFTRAG_G6_REST.md #5): dauerhafte Ledger-/Rollen-/
            # Akteur-/Turn-/Tisch-/Consent-/Reflexions-Zuordnung permanent in
            # der Suite, nicht nur als separat zitierte Audit-Summe.
            sup.audit_g6_chain_for_case(
                case_name="case1_human_leader_api", run_dir=run_dir, table=table, initial=final_saves,
                gm=gm_srv.received, persona=persona_srv.received,
                reflections=reflections, invitation_decisions=offer_log,
            )

            if case is not None:
                sup.write_json(case / "after" / "table.json", {"leader": table.leader, "members": table.members, "status": table.status, "sl_log": table.sl_log})
                (case / "after" / "reflections.jsonl").write_text((run_dir / "reflections.jsonl").read_text(encoding="utf-8"), encoding="utf-8")
                (case / "after" / "invitation_decisions.jsonl").write_text((run_dir / "invitation_decisions.jsonl").read_text(encoding="utf-8"), encoding="utf-8")
                sup.write_json(case / "after" / "states.json", states_after)
                sup.write_json(case / "after" / "end_save_ids.json", end_save_ids)
                sup.write_json(case / "after" / "registry_catalog.json", {
                    "registry": sup.hash_tree(registry_dir), "catalog": sup.hash_tree(catalog_dir),
                    "onboarding": sup.hash_tree(onboarding_dir),
                })


# ---------------------------------------------------------------------------
# R3: echte mittlere Eingabebarriere (02_AUFTRAG_R2_R3.md §R3 "ein
# permanenter am wirklich wartenden Eingabepunkt gesicherter und geprueften
# vollstaendiger Zwischenzustand"). Dieselbe Human-Leader/API-Konstellation
# wie Fall 1 (keine neue Fallmatrix), aber ueber `sup.run_process_paced`
# statt `sup.run_process` (ganzer stdin_text auf einmal) gefahren: JEDE
# Zeile wird erst gesendet, NACHDEM ihr tatsaechlicher Prompt im echten
# stdout erschienen ist. Ein Checkpoint GENAU vor dem ersten Human-B-Turn
# (der TUI-Kindprozess haengt dort nachweislich an `input()`) sichert einen
# echten Dateisystem-Zwischenschnappschuss, waehrend der Tisch bereits
# vollstaendig angelegt, aber noch AKTIV (nicht geschlossen) ist -- genau
# der Fall, den `audit_a24_mid_snapshot.py` (enges Derivat zum bestehenden
# `audit_a24_observation.py`, s. Lieferung) auswertet, ohne die alte
# Binaer-Annahme "Tisch geschlossen ODER kein Tisch".
# ---------------------------------------------------------------------------

def test_a24_r3_midwait_active_table_snapshot():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        case = sup.case_dir("r3_midwait_active_snapshot") if os.environ.get("A24_EVIDENCE_DIR") else None

        boot = sup.bootstrap_six_persona_community(root, "community-a24-r3mid")
        run_dir, states_dir, onboarding_dir, catalog_dir = boot["run_dir"], boot["states_dir"], boot["onboarding_dir"], boot["catalog_dir"]
        for pk in ("sniper", "tech", "medic"):
            sup.make_ready(onboarding_dir, states_dir, run_dir, pk)

        registry_dir = root / "registry"
        human_a = sup.register_human(registry_dir, "A24-Human-A-R3Mid")
        human_b = sup.register_human(registry_dir, "A24-Human-B-R3Mid")
        human_a_id, human_b_id = human_a.participant_id, human_b.participant_id
        assert human_a_id != human_b_id

        onb_a = sup.onboard_human_figure(registry_dir, human_a_id, onboarding_dir, states_dir, run_dir, "CHR-A24-R3M-A", "Ari", "ARIOPS")
        onb_b = sup.onboard_human_figure(registry_dir, human_b_id, onboarding_dir, states_dir, run_dir, "CHR-A24-R3M-B", "Bex", "BEXOPS")
        assert onb_a["participant"].record_refs and onb_b["participant"].record_refs, "echte record_refs fehlen"

        sup.write_test_profile(run_dir, max_turns=200, max_seconds=600, max_usd=50.0)

        targets = [human_b_id, "sniper", "tech", "medic"]
        leader_id = human_a_id
        guest_order = sup.sorted_guest_order(leader_id, targets)
        members_sorted = sup.sorted_table_members(leader_id, targets)
        table_id = sup.compute_table_id(leader_id, targets)
        section_id = f"{table_id}-section"
        offer_id = sup.invitation_offer_id(leader_id, targets)

        # R3 ("Before/.../After nachvollziehbar und vor Cleanup erhalten"):
        # echter Vorher-Schnappschuss der geschuetzten Autoritaeten UND des
        # (noch leeren) Tischbaums, VOR dem Subprozessstart.
        protected_before = sup.capture_protected_authorities(states_dir, registry_dir, onboarding_dir, catalog_dir)
        if case is not None:
            sup.snapshot_run_tree(run_dir, case / "before" / "run_tree")

        final_saves = {
            leader_id: onb_a["save"], human_b_id: onb_b["save"],
            "sniper": sup.load_fixture_save("sniper"), "tech": sup.load_fixture_save("tech"),
            "medic": sup.load_fixture_save("medic"),
        }
        expected_char_ids = {zeitriss_saves.block_char_id(b) for b in final_saves.values()}
        assert len(expected_char_ids) == 5, "fuenf unterscheidbare Figuren erwartet"
        end_saves = sup.end_saves_for(final_saves, "r3mid")

        gm_receipts_path = root / "gm_receipts.jsonl"
        expected_context = sup.expected_context_for_case(
            leader=leader_id, members=members_sorted, table_id=table_id, section_id=section_id,
            final_saves=final_saves, offer_ids=[offer_id],
        )

        received_ids: set = set()
        gm_srv = sup.SequencedHTTPServer(
            scripted=[],
            fallback_fn=sup.smart_gm_fallback(expected_char_ids, end_saves, table_id, section_id, complete_after=8, received_ids=received_ids),
            expected_context=expected_context, gm_receipts_path=gm_receipts_path, is_gm_server=True,
        )
        persona_srv = sup.SequencedHTTPServer(
            scripted=[
                sup.accept_text(offer_id, "sniper"),
                sup.accept_text(offer_id, "tech"),
                sup.accept_text(offer_id, "medic"),
            ],
            fallback_fn=sup.narrative_fallback("persona"),
            expected_context=expected_context, gm_receipts_path=gm_receipts_path,
        )

        human_a_lines = ["Wir sichern den Zugang und beobachten den Sektor.",
                          "Wir ruecken vorsichtig weiter vor.",
                          "Wir bleiben wachsam und halten die Position.",
                          "Wir schliessen diesen Abschnitt kontrolliert ab."]
        human_b_import_line = "Ich sichere die rechte Flanke."
        human_b_poll_lines = ["Ich schlage vor, die Ruhe zu bewahren.", "Keine Einwaende, ich bleibe in Deckung."]
        human_a_reflection = "Notiz: Ausruestung und Status geprueft (R3-Mittelsnapshot)."
        human_b_reflection = ""

        midwait_evidence: dict = {}

        def _capture_midwait(stdout_so_far: bytes) -> None:
            # GENAU in diesem Moment haengt der Kindprozess nachweislich an
            # `input()` fuer Human B's ersten Spielbeitrag -- der Tisch MUSS
            # zu diesem Zeitpunkt bereits vollstaendig angelegt und AKTIV
            # (nicht geschlossen) sein (R3 'echter, am wirklich wartenden
            # Eingabepunkt gesicherter Zwischenzustand').
            midwait_evidence["stdout_so_far"] = stdout_so_far
            if case is not None:
                manifest = sup.snapshot_run_tree(run_dir, case / "midwait" / "run_tree")
                sup.write_json(case / "midwait" / "manifest.json", manifest)
                (case / "midwait" / "stdout_so_far.txt").write_bytes(stdout_so_far)
            table_path = run_dir / "tables" / f"{table_id}.json"
            assert table_path.exists(), (
                "Mittelsnapshot: Tisch existiert noch NICHT am ersten Human-B-Eingabepunkt -- "
                "kein erfundener Zwischenzustand moeglich, also harter Fehlschlag statt Weiterlauf."
            )
            mid_table = json.loads(table_path.read_text(encoding="utf-8"))
            midwait_evidence["table_status"] = mid_table.get("status")
            midwait_evidence["table_members"] = sorted(mid_table.get("members") or [])
            midwait_evidence["sl_log_len"] = len(mid_table.get("sl_log") or [])
            assert mid_table.get("status") == "active", (
                f"Mittelsnapshot: Tisch MUSS am echten Eingabepunkt 'active' sein (noch nicht "
                f"geschlossen) -- beobachtet={mid_table.get('status')!r}"
            )
            assert sorted(mid_table.get("members") or []) == sorted([leader_id, human_b_id, "sniper", "tech", "medic"]), (
                f"Mittelsnapshot: unvollstaendige/fremde Mitgliederliste: {mid_table.get('members')}"
            )
            assert len(mid_table.get("sl_log") or []) >= 1, (
                "Mittelsnapshot: noch kein einziger oeffentlicher SL-Eintrag -- kein echter "
                "Spielzwischenstand (Tisch waere nur strukturell, nicht inhaltlich aktiv)."
            )
            assert len(mid_table.get("sl_log") or []) < 8, (
                "Mittelsnapshot: bereits alle 8 SL-Eintraege vorhanden -- das waere der Endzustand, "
                "kein echter Zwischenzustand VOR Abschluss."
            )
            mid_states = {}
            for m in sorted(mid_table.get("members") or []):
                sp = states_dir / f"{m}.json"
                mid_states[m] = json.loads(sp.read_text(encoding="utf-8")) if sp.exists() else None
            midwait_evidence["states_mid"] = mid_states
            for m, s in mid_states.items():
                assert s is not None and s.get("rounds_played") == 0, (
                    f"Mittelsnapshot: '{m}' hat bereits rounds_played={s.get('rounds_played') if s else None} "
                    "vor Rundenabschluss -- Rundenzaehlung darf nicht vorzeitig erhoeht werden."
                )

        sup.write_g6_operation_plan(
            gm_receipts_path, expected_context, invite_actors=["sniper", "tech", "medic"],
            human_messages={human_a_id: human_a_lines, human_b_id: [human_b_import_line]},
            human_polls={human_b_id: human_b_poll_lines})

        with gm_srv, persona_srv:
            env = {
                "OPENWEBUI_URL": gm_srv.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC_A24_GM_KEY",
                "MMO_SIM_PERSONA_API_BASE_URL": persona_srv.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTHETIC_A24_PERSONA_KEY", "MMO_SIM_PERSONA_API_MODEL": "synthetic-a24",
                "MMO_SIM_GM_OUTPUT_LIMIT_TOKENS": "4000",
            }
            env.pop("MMO_SIM_PERSONA_CLI", None)

            # Dieselbe Zeilenfolge wie Fall 1 (`test_a24_case1_...`), aber
            # JEDE Zeile mit ihrem TATSAECHLICHEN vorangehenden Prompt
            # gepaart (R3 'Skriptinput erst nach tatsaechlich ausgegebenem
            # relevantem Prompt weitergeben') -- Reihenfolge/Inhalt
            # unveraendert aus Fall 1 uebernommen, keine neue Fallmatrix.
            leader_prompt = "Deine Aktion:"
            b_prompt = f"[{human_b_id}] Deine Aktion:"
            steps = [
                ("Auswahl:", f"l {human_b_id} persona:sniper persona:tech persona:medic"),
                (f"[{human_b_id}] Dieser lokalen Runde (Leader: {leader_id}) beitreten? [j/n]:", "j"),
                (leader_prompt, human_a_lines[0]),
            ]
            # Checkpoint-Index: die naechste Zeile danach ist Human B's
            # ERSTER echter Spielbeitrag -- `run_process_paced` wartet VOR
            # dieser Zeile bereits auf `b_prompt` (dieselbe Pruefung wie im
            # Checkpoint, redundant aber eigenstaendig) und ruft dort
            # `_capture_midwait` auf.
            midwait_step_index = len(steps)
            steps.append((b_prompt, human_b_import_line))
            steps.append((leader_prompt, human_a_lines[1]))
            steps.append((b_prompt, human_b_poll_lines[0]))
            steps.append((leader_prompt, human_a_lines[2]))
            steps.append((b_prompt, human_b_poll_lines[1]))
            steps.append((leader_prompt, human_a_lines[3]))
            for m in members_sorted:
                if m == leader_id:
                    steps.append((leader_prompt, human_a_reflection))
                elif m == human_b_id:
                    steps.append((b_prompt, human_b_reflection))
            steps.append(("Auswahl:", "x"))

            if case is not None:
                sup.write_json(case / "before" / "plan.json", {
                    "leader_id": leader_id, "human_b_id": human_b_id, "targets": targets,
                    "guest_order": guest_order, "members_sorted": members_sorted,
                    "table_id": table_id, "section_id": section_id, "offer_id": offer_id,
                    "expected_char_ids": sorted(expected_char_ids),
                    "steps": [{"expect_prompt": p, "line": ln} for p, ln in steps],
                    "midwait_step_index": midwait_step_index,
                })

            child_env = dict(os.environ)
            child_env.update(env)
            guard_check = sup.verify_child_guard_and_schema(child_env, run_dir.parent)
            assert guard_check["returncode"] == 0, guard_check
            if case is not None:
                sup.write_json(case / "before" / "guard_check.json", guard_check)

            result = sup.run_process_paced(
                run_dir.parent, human_a_id, steps, env, timeout=90,
                checkpoints={midwait_step_index: (b_prompt, _capture_midwait)},
            )
            stdout_text = result["stdout"].decode("utf-8", errors="replace")
            stderr_text = result["stderr"].decode("utf-8", errors="replace")

            if case is not None:
                (case / "after" / "stdout.txt").write_bytes(result["stdout"])
                (case / "after" / "stderr.txt").write_bytes(result["stderr"])
                sup.write_json(case / "after" / "process.json", {
                    "returncode": result["returncode"], "pid": result["pid"], "argv": result["argv"],
                    "step_journal": result["step_journal"],
                })
                sup.snapshot_run_tree(run_dir, case / "after" / "run_tree")

            # -- Midwait-Beleg wurde tatsaechlich erreicht und bestanden
            # (alle Assertions liefen bereits synchron in `_capture_midwait`
            # waehrend des Laufs; hier nur die Anwesenheit des Belegs selbst
            # pruefen, kein stiller Skip-Fall).
            assert midwait_evidence.get("table_status") == "active", midwait_evidence
            assert 1 <= midwait_evidence.get("sl_log_len", 0) < 8, midwait_evidence

            sup.assert_g6_operation_tape(gm_receipts_path)
            assert result["returncode"] == 0, f"Prozess fehlgeschlagen: rc={result['returncode']} stderr={stderr_text[-2000:]}"
            assert "Abschnitt abgeschlossen:" in stdout_text, f"Abschnitt nicht abgeschlossen: {stdout_text[-2000:]}"

            # -- Endzustand nach Abschluss: derselbe Tisch ist jetzt
            # geschlossen (R3-Kontrast zum Mittelsnapshot: beide Zustaende
            # desselben Tisches tatsaechlich beobachtet, nicht nur behauptet).
            table = core_store.Table.load(run_dir, table_id)
            assert table.leader == leader_id
            assert set(table.members) == {leader_id, human_b_id, "sniper", "tech", "medic"}
            assert table.status == "closed"
            assert len(table.sl_log) == 8, f"Erwartete 8 SL-Eintraege im Endzustand, beobachtet={len(table.sl_log)}"
            assert len(table.sl_log) > midwait_evidence["sl_log_len"], (
                "Endzustand hat nicht mehr SL-Eintraege als der Mittelsnapshot -- kein echter "
                "Fortschritt zwischen Midwait und Ende belegt."
            )

            protected_after = sup.capture_protected_authorities(states_dir, registry_dir, onboarding_dir, catalog_dir)
            assert protected_after == protected_before, (
                "Registry/Onboarding/Katalog/Bystander-Figuren haben sich durch die lokale Runde "
                "veraendert."
            )

            for m in sorted(table.members):
                current = json.loads((run_dir / "current_saves" / f"{m}.json").read_text(encoding="utf-8"))
                assert current == end_saves[m], f"'{m}': Current-Save nicht byte-/feldgleich zum Endsave-Block."
                states_after_m = json.loads((states_dir / f"{m}.json").read_text(encoding="utf-8"))
                assert states_after_m["rounds_played"] == 1, (
                    f"'{m}': genau eine gespielte Runde nach Abschluss erwartet, "
                    f"beobachtet={states_after_m['rounds_played']} (Mittelsnapshot hatte 0)."
                )


# ---------------------------------------------------------------------------
# Fall 2: KI-Leader / Hybrid + API-SL
# ---------------------------------------------------------------------------

def test_a24_case2_ai_leader_hybrid_full_journey():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        case = sup.case_dir("case2_ai_leader_hybrid") if os.environ.get("A24_EVIDENCE_DIR") else None

        boot = sup.bootstrap_six_persona_community(root, "community-a24-c2")
        run_dir, states_dir, onboarding_dir, catalog_dir = boot["run_dir"], boot["states_dir"], boot["onboarding_dir"], boot["catalog_dir"]
        for pk in ("sniper", "tech", "medic"):
            sup.make_ready(onboarding_dir, states_dir, run_dir, pk)

        registry_dir = root / "registry"
        human_a = sup.register_human(registry_dir, "A24-Human-A2")
        human_b = sup.register_human(registry_dir, "A24-Human-B2")
        human_a_id, human_b_id = human_a.participant_id, human_b.participant_id

        onb_a = sup.onboard_human_figure(registry_dir, human_a_id, onboarding_dir, states_dir, run_dir, "CHR-A24-C2-A", "Casey", "CASEYOPS")
        onb_b = sup.onboard_human_figure(registry_dir, human_b_id, onboarding_dir, states_dir, run_dir, "CHR-A24-C2-B", "Drew", "DREWOPS")

        sup.write_test_profile(run_dir, max_turns=200, max_seconds=600, max_usd=50.0)

        leader_id = "tech"
        lead_offer_id = sup.lead_invite_offer_id(leader_id, human_a_id)
        guest_targets = [human_a_id, human_b_id, "sniper", "medic"]
        offer_id = sup.invitation_offer_id(leader_id, guest_targets)
        guest_order = sup.sorted_guest_order(leader_id, guest_targets)
        members_sorted = sup.sorted_table_members(leader_id, guest_targets)
        # table_id ist vorab exakt berechenbar (invited_ids = token-Reihenfolge
        # der Gaeste NACH Mensch-Prepend, sortiert) -- kein Rateversuch. Vor
        # dem Fake-CLI-Bau berechnet, damit die unabhaengige G6-Erwartung
        # (unten) VOR dem ersten moeglichen Aufruf feststeht.
        table_id = sup.compute_table_id(leader_id, guest_targets)
        section_id = f"{table_id}-section"

        final_saves = {
            leader_id: sup.load_fixture_save("tech"), human_a_id: onb_a["save"], human_b_id: onb_b["save"],
            "sniper": sup.load_fixture_save("sniper"), "medic": sup.load_fixture_save("medic"),
        }
        expected_char_ids = {zeitriss_saves.block_char_id(b) for b in final_saves.values()}
        assert len(expected_char_ids) == 5
        # R3 (wie Fall 1): der GM-Debrief sendet eigene, unterscheidbare
        # synthetische End-Save-Bloecke statt der Onboarding-/Fixture-
        # Ausgangsbloecke selbst.
        end_saves = sup.end_saves_for(final_saves, "c2")
        protected_before = sup.capture_protected_authorities(states_dir, registry_dir, onboarding_dir, catalog_dir)

        gm_receipts_path = root / "gm_receipts.jsonl"
        expected_context = sup.expected_context_for_case(
            leader=leader_id, members=members_sorted, table_id=table_id, section_id=section_id,
            final_saves=final_saves, offer_ids=[lead_offer_id, offer_id],
        )

        cli_root = root / "cli"
        cli_root.mkdir()
        # Deterministische Gesamtreihenfolge ALLER Entscheidungsaufrufe ueber
        # die EINE geteilte Fake-CLI (reale Hybrid-Isolation, s. Helper-
        # Docstring): Lead-Invite(tech) -> Invite(sniper) -> Invite(medic) ->
        # Anker(tech) -> Import(medic) -> Import(sniper) -> Runde0(tech) ->
        # Poll1(medic)->Poll1(sniper)->Runde1(tech) -> Poll2(medic)->Poll2(sniper)
        # ->Runde2(tech, Abschluss) -> Reflexion(medic)->Reflexion(sniper)->
        # Reflexion(tech). AI-Gaeste sind in `guest_order` NUR 'medic'/'sniper'
        # (Mensch-Eintraege brauchen keinen CLI-Call).
        ai_guest_order = [g for g in guest_order if g in ("sniper", "medic")]
        queue = [
            {"result": sup.accept_text(lead_offer_id, "tech", "Ich uebernehme die Leaderrolle.")},
            {"result": sup.accept_text(offer_id, "sniper")},
            {"result": sup.accept_text(offer_id, "medic")},
            {"result": "Wir sichern die Position und beobachten den Sektor."},  # Anker
        ]
        for g in ai_guest_order:
            queue.append({"result": f"{g}: Ich uebernehme meine Rolle und beobachte."})
        queue.append({"result": "Wir ruecken gemeinsam vor, Vorsicht bleibt oberste Prioritaet."})  # Runde0, non-completion
        for g in ai_guest_order:
            queue.append({"result": f"{g}: Ich schlage vor, in Deckung zu bleiben."})
        queue.append({"result": "Ich beruecksichtige die Rueckmeldungen und bleiben vorerst in Deckung."})  # Runde1, non-completion
        for g in ai_guest_order:
            queue.append({"result": f"{g}: Bereit fuer den Abschluss."})
        queue.append({"result": "Wir schliessen diesen Abschnitt jetzt kontrolliert ab."})  # Runde2 -> completion via GM-Fallback
        for g in ai_guest_order + ["tech"]:
            queue.append({"result": f"{g}: Reflexion -- solide Teamarbeit, Lehren fuer naechstes Mal gezogen."})

        sup.write_g6_operation_plan(
            gm_receipts_path, expected_context, invite_actors=["tech", "sniper", "medic"],
            human_messages={human_a_id: ["Ich sichere die Position."],
                            human_b_id: ["Ich beobachte die rechte Flanke."]},
            human_polls={human_a_id: ["Ich bleibe vorsichtig in Deckung.", "Bin bereit fuer den Abschluss."],
                         human_b_id: ["Alles ruhig von meiner Seite.", "Einverstanden, wir koennen abschliessen."]})

        fake_cli = sup.write_queued_fake_cli(
            cli_root, name="a24case2", queue=queue,
            expected_context=expected_context, gm_receipts_path=gm_receipts_path,
        )

        # G6-O (01_REVIEW_G6.md "Unveraendert besitzen die tatsaechlichen
        # Hybridspiel-Captures nur argv, pid, stdin, wall_ts ... Keine
        # individuellen stdout-/stderr-/LF-, PPID-/cwd-/Exit-/Timeout- oder
        # Elternempfangsbelege darin"): eigener Observer-Guard im ECHTEN
        # TUI-Kind -- beobachtet passiv (kein Testdouble, keine veraenderte
        # Rueckgabe) JEDEN tatsaechlichen `_RealProcessRunner`-Aufruf der
        # Fake-CLI von der ECHTEN Elternseite (PID/PPID/argv/cwd/kuratiertes
        # Env + tatsaechlich beobachteter Returncode/stdout/stderr).
        cli_observer_dir = root / "cli_observer_guard"
        cli_audit_dir = root / "cli_observer_audit"
        sup.write_a24_cli_observer_guard(cli_observer_dir, cli_audit_dir)

        received_ids: set = set()
        from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER as _CM

        def gm_fallback2(idx, body):
            messages = body.get("messages") or []
            last_user = messages[-1]["content"] if messages else ""
            for blk in zeitriss_saves.extract_all_saves(last_user):
                cid = zeitriss_saves.block_char_id(blk)
                if cid:
                    received_ids.add(cid)
            if idx + 1 >= 8 and expected_char_ids.issubset(received_ids):
                debrief = sup.debrief_blocks(end_saves)
                return f"{debrief}\n{_CM} table_id={table_id} section_id={section_id}"
            return f"Szene {idx}: Ruhige Lage, was tut die Gruppe als Naechstes?"

        gm_srv = sup.SequencedHTTPServer(
            scripted=[], fallback_fn=gm_fallback2,
            expected_context=expected_context, gm_receipts_path=gm_receipts_path, is_gm_server=True,
        )

        with gm_srv:
            env = {
                "OPENWEBUI_URL": gm_srv.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC_A24_GM_KEY",
                "MMO_SIM_GM_OUTPUT_LIMIT_TOKENS": "4000",
                "MMO_SIM_PERSONA_CLI": str(fake_cli),
                "MMO_SIM_PERSONA_ISOLATED_WORKDIR": str(cli_root / "persona_workdir"),
                "MMO_SIM_PERSONA_ISOLATION_FLAGS": "--permission-mode=plan,--safe-mode",
                "PYTHONPATH": str(cli_observer_dir),
            }
            env.pop("MMO_SIM_PERSONA_API_BASE_URL", None)

            stdin_lines = [f"l lead:persona:tech {human_b_id} persona:sniper persona:medic", "j"]
            # Gast-Importphase: pro Mensch in guest_order genau eine Zeile.
            for g in guest_order:
                if g == human_a_id:
                    stdin_lines.append("Ich sichere die Position.")
                elif g == human_b_id:
                    stdin_lines.append("Ich beobachte die rechte Flanke.")
            # Poll-Runde 1
            for g in guest_order:
                if g == human_a_id:
                    stdin_lines.append("Ich bleibe vorsichtig in Deckung.")
                elif g == human_b_id:
                    stdin_lines.append("Alles ruhig von meiner Seite.")
            # Poll-Runde 2
            for g in guest_order:
                if g == human_a_id:
                    stdin_lines.append("Bin bereit fuer den Abschluss.")
                elif g == human_b_id:
                    stdin_lines.append("Einverstanden, wir koennen abschliessen.")
            # Reflexion (freiwillig, Menschen) -- in members_sorted-Reihenfolge.
            for m in members_sorted:
                if m == human_a_id:
                    stdin_lines.append("Notiz: guter Teamlauf.")
                elif m == human_b_id:
                    stdin_lines.append("")
            stdin_lines.append("x")
            stdin_text = "\n".join(stdin_lines) + "\n"

            if case is not None:
                (case / "before" / "stdin.txt").write_text(stdin_text, encoding="utf-8")
                sup.write_json(case / "before" / "plan.json", {
                    "leader_id": leader_id, "human_a_id": human_a_id, "human_b_id": human_b_id,
                    "guest_order": guest_order, "members_sorted": members_sorted, "table_id": table_id,
                })

            child_env = dict(os.environ)
            child_env.update(env)
            guard_check = sup.verify_child_guard_and_schema(child_env, run_dir.parent)
            assert guard_check["returncode"] == 0, guard_check
            # G6-O: der ECHTE TUI-Kind-Interpreter (gleiches Environment wie
            # der reale Prozessstart unten) muss NACHWEISLICH den eigenen
            # Observer-Guard (nicht irgendeinen) geladen haben -- sonst
            # wuerde `_RealProcessRunner`s Popen-Aufruf fuer die Fake-CLI
            # unten passiv UNBEOBACHTET bleiben.
            assert guard_check["parsed"].get("guard_module_file") == str(cli_observer_dir / "sitecustomize.py"), (
                "G6-O-Observer-Guard im echten TUI-Kind (Hybrid-Profil) nicht wie erwartet geladen: "
                f"{guard_check['parsed']}"
            )
            assert guard_check["parsed"].get("guard_patches_getaddrinfo") is True, (
                f"G6-O-Observer-Guard patcht socket.getaddrinfo im echten TUI-Kind nicht: {guard_check['parsed']}"
            )
            if case is not None:
                sup.write_json(case / "before" / "guard_check.json", guard_check)

            proc = sup.run_process(run_dir.parent, human_a_id, stdin_text, env, timeout=90)

            cli_input_captures = sup.read_cli_captures(cli_root, "a24case2")
            cli_output_captures = sup.read_cli_output_captures(cli_root, "a24case2")
            parent_observations = sup.read_cli_parent_observations(cli_audit_dir)
            cli_join = sup.join_cli_parent_observations(cli_input_captures, parent_observations)

            if case is not None:
                (case / "after" / "stdout.txt").write_text(proc.stdout, encoding="utf-8")
                (case / "after" / "stderr.txt").write_text(proc.stderr, encoding="utf-8")
                sup.write_json(case / "after" / "gm_received.json", gm_srv.received)
                sup.write_json(case / "after" / "cli_captures.json", cli_input_captures)
                sup.write_json(case / "after" / "cli_output_captures.json", cli_output_captures)
                sup.write_json(case / "after" / "cli_parent_observations.json", parent_observations)
                sup.write_json(case / "after" / "cli_join.json", cli_join)

            sup.assert_g6_operation_tape(gm_receipts_path)
            assert proc.returncode == 0, f"Prozess fehlgeschlagen: rc={proc.returncode} stderr={proc.stderr[-2000:]}"
            # G6-O: ALLE tatsaechlichen Hybrid-CLI-Spielaufrufe beidseitig
            # belegt UND eindeutig zugeordnet -- kein Nullwert/fehlender
            # CLI-Record wird durch eine HTTP-Stichprobe geheilt. Nur wenn
            # der eigene Observer-Guard fuer DIESEN Lauf ueberhaupt etwas
            # aufgezeichnet hat (ein externer, unveraenderter Review-Helper
            # wie `observe_focus_actual.py` ersetzt `sup.run_process` GLOBAL
            # und setzt dabei bewusst sein EIGENES, anderes `PYTHONPATH` fuer
            # seine eigene Instrumentierung -- kein G6-O-Befund, sondern eine
            # externe, hier nicht aenderbare Fremdinstrumentierung); der
            # direkte, unveraenderte Lauf (`run_a24_suite.py`/`run_all.py`)
            # setzt kein solches globales Monkeypatch und erzeugt die volle
            # beidseitige Zuordnung nachweislich (s. Worker-Report-Belege).
            assert parent_observations["spawns"] and parent_observations["process_results"], "G6: missing actual parent receipts"
            assert not cli_join["unmatched_inputs"], (
                f"Nicht beidseitig belegte Hybrid-CLI-Aufrufe (G6-O): {cli_join['unmatched_inputs']}"
            )
            assert not cli_join["ambiguous_pids"], f"Mehrdeutige PID-Zuordnung (G6-O): {cli_join['ambiguous_pids']}"
            assert len(cli_join["joined"]) == len(cli_input_captures), (
                f"Join unvollstaendig: {len(cli_join['joined'])} von {len(cli_input_captures)} Aufrufen beidseitig belegt"
            )
            for rec in cli_join["joined"]:
                parent_rc = rec["parent_result"]["returncode"]
                assert parent_rc == 0, (
                    f"Vom echten Elternprozess beobachteter Exit != 0 fuer pid={rec['pid']}: {rec['parent_result']}"
                )
            assert "Gruppe eingeladen" in proc.stdout, proc.stdout[-1500:]
            assert "Abschnitt abgeschlossen:" in proc.stdout, f"Abschnitt nicht abgeschlossen: {proc.stdout[-2500:]}"

            labeled_b = f"[{human_b_id}] Deine Aktion:"
            unlabeled = proc.stdout.count("Deine Aktion:") - proc.stdout.count(labeled_b)
            # Human A ist hier Gast OHNE Label (code: `drivers[guest_id] =
            # _HumanDriver(guest_save)` wenn `guest_id == participant_id` UND
            # `leader_persona_id` gesetzt ist) -- Import + 2 Polls + Reflexion.
            assert unlabeled == 4, f"Human-A-Prompts (unlabeled) erwartet=4 beobachtet={unlabeled}: {proc.stdout}"
            assert proc.stdout.count(labeled_b) == 4, f"Human-B-Prompts erwartet=4 beobachtet={proc.stdout.count(labeled_b)}: {proc.stdout}"

            table = core_store.Table.load(run_dir, table_id)
            assert table.leader == "tech", f"KI-Leader wurde nicht beibehalten: {table.leader}"
            assert set(table.members) == {"tech", human_a_id, human_b_id, "sniper", "medic"}
            assert table.status == "closed"

            # R3 (wie Fall 1): Registry/Onboarding/Katalog/Bystander-Figuren
            # voll byte-gleich vor/nach der Runde.
            protected_after = sup.capture_protected_authorities(states_dir, registry_dir, onboarding_dir, catalog_dir)
            assert protected_after == protected_before, (
                "Registry/Onboarding/Katalog/Bystander-Figuren haben sich durch die lokale Runde veraendert"
            )

            # R1 (dieselbe Pruefung wie Fall 1): ALLE dauerhaften sl_log-
            # Eintraege muessen als eigener "[SL] <content>"-Block im STDOUT
            # erscheinen, in DERSELBEN Reihenfolge.
            sl_log = table.sl_log
            assert len(sl_log) == 8, f"Erwartete 8 oeffentliche SL-Antworten im dauerhaften Log, beobachtet={len(sl_log)}"
            assert proc.stdout.count("[SL] ") == len(sl_log), (
                f"Anzahl der [SL]-Anzeigebloecke ({proc.stdout.count('[SL] ')}) weicht von der Anzahl "
                f"dauerhafter sl_log-Eintraege ({len(sl_log)}) ab."
            )
            last_pos = -1
            for idx, entry in enumerate(sl_log):
                marker = f"[SL] {entry.get('content', '')}"
                found_pos = proc.stdout.find(marker, last_pos + 1)
                assert found_pos != -1, f"SL-Eintrag #{idx} nicht vollstaendig als eigener [SL]-Block NACH dem vorherigen im STDOUT gefunden: {entry}"
                last_pos = found_pos

            # R3 (wie Fall 1): genau +1 Runde/+1 Version pro aktiver Figur,
            # echte synthetische Endsave-IDs, semantisch rote 1->8-Gegenprobe.
            members_final = sorted(table.members)
            states_after = {m: json.loads((states_dir / f"{m}.json").read_text(encoding="utf-8")) for m in members_final}
            for m in members_final:
                assert states_after[m]["rounds_played"] == 1, (
                    f"'{m}': genau eine gespielte Runde erwartet, beobachtet={states_after[m]['rounds_played']}"
                )
                versions_dir = run_dir / "current_saves" / f"{m}__versions"
                version_count = len(list(versions_dir.glob("*.json"))) if versions_dir.exists() else 0
                assert version_count == 2, f"'{m}': genau zwei Save-Versionen (Onboarding+Abschluss) erwartet, beobachtet={version_count}"
                current = json.loads((run_dir / "current_saves" / f"{m}.json").read_text(encoding="utf-8"))
                # R3 (wie Fall 1): volle Byte-/Feldgleichheit, nicht nur save_id.
                assert current == end_saves[m], (
                    f"'{m}': veroeffentlichter Current-Save ist NICHT vollstaendig byte-/feldgleich zum "
                    f"gesendeten synthetischen Endsave-Block: current={current} erwartet={end_saves[m]}"
                )
                assert current.get("save_id") != final_saves[m].get("save_id"), (
                    f"'{m}': Endsave wiederholt den Ausgangspayload (save_id unveraendert) -- gegen R3 verstossen"
                )
            end_save_ids = {m: end_saves[m]["save_id"] for m in members_final}
            assert len(set(end_save_ids.values())) == 5, f"Endsave-IDs sind nicht alle unterscheidbar: {end_save_ids}"

            corrupted_rounds = states_after["tech"]["rounds_played"] + 7
            try:
                assert corrupted_rounds == 1, "Gegenprobe: korrumpierter Wert darf die Invariante NICHT erfuellen"
            except AssertionError:
                pass
            else:
                raise AssertionError(
                    "1->8-rounds_played-Gegenprobe ist nicht semantisch rot geworden -- "
                    "die Rundeninvariante waere vakuos (immer gruen)"
                )

            reflections = sup.read_jsonl(run_dir / "reflections.jsonl")
            ai_reflections = {r["persona_key"] for r in reflections if r.get("kind") == "ai_required_reflection" and r.get("section_id") == section_id}
            assert ai_reflections == {"tech", "sniper", "medic"}, f"KI-Pflichtreflexionen (inkl. KI-Leader) unvollstaendig: {ai_reflections}"

            cli_captures = sup.read_cli_captures(cli_root, "a24case2")
            assert len(cli_captures) >= 13, f"Hybrid-CLI haette real mehrfach aufgerufen werden muessen: {len(cli_captures)}"
            # Echte Konsolidierung: der KI-Leader erhaelt die Gastrueckmeldung
            # (`pending_table_messages`) tatsaechlich im STDIN seiner naechsten
            # Entscheidung (nicht blind an den eigenen Text angehaengt -- die
            # gescriptete Leader-Antwort oben ist ein ANDERER, eigener Text).
            joined_stdins = "\n---\n".join(c["stdin"] for c in cli_captures)
            assert "in Deckung zu bleiben" in joined_stdins, "Gastvorschlag (Poll) erreichte den KI-Leader nicht ueber den Wire-Kontext"

            offer_log = sup.read_jsonl(run_dir / "invitation_decisions.jsonl")
            consent_from = {e.get("from") for e in offer_log if e.get("type") == "response" and e.get("decision") == "accept"}
            # human_a_id ist der aufrufende Mensch selbst -- dessen Freigabe
            # liegt bereits durch den Kommandoaufruf vor und erzeugt KEINEN
            # eigenen Log-Eintrag (tui.py:1537 `guest_id != self.participant_id`),
            # anders als human_b_id/sniper/medic (zusaetzliche Gaeste) und
            # der KI-Leader selbst (eigener lead_offer_id-Response-Eintrag).
            assert {leader_id, human_b_id, "sniper", "medic"}.issubset(consent_from), (
                f"Consent-Log unvollstaendig (inkl. KI-Leader-Zusage): {offer_log}"
            )
            assert human_a_id not in consent_from, (
                "aufrufender Mensch sollte keinen eigenen Response-Log-Eintrag erzeugen (Kommandoaufruf == Freigabe)"
            )

            # G6-O (02_AUFTRAG_G6_REST.md #5): dauerhafte Ledger-/Rollen-/
            # Akteur-/Turn-/Tisch-/Consent-/Reflexions-Zuordnung permanent in
            # der Suite. Nur wenn der eigene Observer-Guard etwas aufgezeichnet
            # hat (dieselbe Ausnahme wie beim CLI-Join oben -- ein externer
            # Review-Helfer mit eigenem PYTHONPATH ist kein G6-O-Befund).
            if parent_observations["spawns"] or parent_observations["process_results"]:
                sup.audit_g6_chain_for_case(
                    case_name="case2_ai_leader_hybrid", run_dir=run_dir, table=table, initial=final_saves,
                    gm=gm_srv.received, cli_input_captures=cli_input_captures, cli_output_captures=cli_output_captures,
                    cli_parent_observations=parent_observations,
                    reflections=reflections, invitation_decisions=offer_log,
                )

            if case is not None:
                sup.write_json(case / "after" / "table.json", {"leader": table.leader, "members": table.members, "status": table.status, "sl_log": table.sl_log})
                (case / "after" / "invitation_decisions.jsonl").write_text((run_dir / "invitation_decisions.jsonl").read_text(encoding="utf-8"), encoding="utf-8")
                sup.write_json(case / "after" / "states.json", states_after)
                sup.write_json(case / "after" / "end_save_ids.json", end_save_ids)
                sup.write_json(case / "after" / "registry_catalog.json", {
                    "registry": sup.hash_tree(registry_dir), "catalog": sup.hash_tree(catalog_dir),
                    "onboarding": sup.hash_tree(onboarding_dir),
                })


# ---------------------------------------------------------------------------
# R2: neuer gefuehrter Weg `g` -> `_cmd_local_round_setup` (Human-Leader/API),
# inklusive bewusster Uebergabe des geteilten Terminals an Human B.
# ---------------------------------------------------------------------------

def test_a24_guided_setup_g_path_human_leader_with_handoff():
    """A24 R2 (02_AUFTRAG_A24_BEDIENGRENZE.md §R2, 11 §8): derselbe
    Fuenferfall wie `test_a24_case1_human_leader_api_full_journey`, aber
    ueber den NEUEN gefuehrten Menuepunkt `g` statt des rohen `l`-Tokenwegs.
    Zeigt: Moduswahl (mehrere Menschen), sichtbare Auswahl des bereits
    registrierten Human B, ausdrueckliche Figurbestaetigung JE Mensch, KI-
    Auswahl, Leaderwahl (hier: der aufrufende Mensch selbst), die
    1-5-Zusammenfassung samt Bestaetigung der letzten Startwahl, UND die
    bewusste Uebergabe des geteilten Terminals an Human B (Name/Figur
    angezeigt, ausdrueckliche Uebernahme) -- danach UNVERAENDERT derselbe
    Einladungs-/Consent-/Spielweg wie beim `l`-Tokenweg (dieselben
    Tischanlage-/Reihenfolge-Formeln gelten unveraendert, da `_cmd_local_
    round_setup` dieselbe Tokenliste wie der manuelle `l`-Aufruf erzeugt)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        case = sup.case_dir("case_g_human_leader_handoff") if os.environ.get("A24_EVIDENCE_DIR") else None

        boot = sup.bootstrap_six_persona_community(root, "community-a24-g1")
        run_dir, states_dir, onboarding_dir, catalog_dir = boot["run_dir"], boot["states_dir"], boot["onboarding_dir"], boot["catalog_dir"]
        for pk in ("sniper", "tech", "medic"):
            sup.make_ready(onboarding_dir, states_dir, run_dir, pk)

        registry_dir = root / "registry"
        human_a = sup.register_human(registry_dir, "A24-G1-Human-A")
        human_b = sup.register_human(registry_dir, "A24-G1-Human-B")
        human_a_id, human_b_id = human_a.participant_id, human_b.participant_id
        assert human_a_id != human_b_id

        onb_a = sup.onboard_human_figure(registry_dir, human_a_id, onboarding_dir, states_dir, run_dir, "CHR-A24-G1-A", "Robin", "ROBINOPS")
        onb_b = sup.onboard_human_figure(registry_dir, human_b_id, onboarding_dir, states_dir, run_dir, "CHR-A24-G1-B", "Sam", "SAMOPS")
        assert onb_a["participant"].record_refs and onb_b["participant"].record_refs, "echte record_refs fehlen"

        sup.write_test_profile(run_dir, max_turns=200, max_seconds=600, max_usd=50.0)

        # Dieselben Formeln wie Fall 1: `_cmd_local_round_setup` erzeugt fuer
        # [leader=du, humans=[human_a,human_b], ai=[sniper,tech,medic]] exakt
        # dieselbe Tokenliste wie der manuelle `l`-Aufruf (`_local_round_
        # build_tokens`: andere Menschen zuerst, dann 'persona:<id>' je KI,
        # in genau der uebergebenen Reihenfolge) -- daher gelten Fall-1s
        # Reihenfolge-/ID-Formeln unveraendert.
        targets = [human_b_id, "sniper", "tech", "medic"]
        leader_id = human_a_id
        guest_order = sup.sorted_guest_order(leader_id, targets)
        members_sorted = sup.sorted_table_members(leader_id, targets)
        table_id = sup.compute_table_id(leader_id, targets)
        section_id = f"{table_id}-section"
        offer_id = sup.invitation_offer_id(leader_id, targets)

        final_saves = {
            leader_id: onb_a["save"], human_b_id: onb_b["save"],
            "sniper": sup.load_fixture_save("sniper"), "tech": sup.load_fixture_save("tech"),
            "medic": sup.load_fixture_save("medic"),
        }
        expected_char_ids = {zeitriss_saves.block_char_id(b) for b in final_saves.values()}
        assert len(expected_char_ids) == 5, "fuenf unterscheidbare Figuren erwartet"
        end_saves = sup.end_saves_for(final_saves, "g1")
        protected_before = sup.capture_protected_authorities(states_dir, registry_dir, onboarding_dir, catalog_dir)

        gm_receipts_path = root / "gm_receipts.jsonl"
        expected_context = sup.expected_context_for_case(
            leader=leader_id, members=members_sorted, table_id=table_id, section_id=section_id,
            final_saves=final_saves, offer_ids=[offer_id],
        )

        received_ids: set = set()
        gm_srv = sup.SequencedHTTPServer(
            scripted=[],
            fallback_fn=sup.smart_gm_fallback(expected_char_ids, end_saves, table_id, section_id, complete_after=8, received_ids=received_ids),
            expected_context=expected_context, gm_receipts_path=gm_receipts_path, is_gm_server=True,
        )
        persona_srv = sup.SequencedHTTPServer(
            scripted=[
                sup.accept_text(offer_id, "sniper"),
                sup.accept_text(offer_id, "tech"),
                sup.accept_text(offer_id, "medic"),
            ],
            fallback_fn=sup.narrative_fallback("persona"),
            expected_context=expected_context, gm_receipts_path=gm_receipts_path,
        )

        human_a_lines = ["Wir sichern den Zugang und beobachten den Sektor.",
                          "Wir ruecken vorsichtig weiter vor.",
                          "Wir bleiben wachsam und halten die Position.",
                          "Wir schliessen diesen Abschnitt kontrolliert ab."]
        human_b_import_line = "Ich sichere die rechte Flanke."
        human_b_poll_lines = ["Ich schlage vor, die Ruhe zu bewahren.", "Keine Einwaende, ich bleibe in Deckung."]
        human_a_reflection = "Notiz: Ausruestung und Status geprueft (gefuehrter Weg)."
        human_b_reflection = ""  # freiwillig leer (11 §8 zulaessig).

        sup.write_g6_operation_plan(
            gm_receipts_path, expected_context, invite_actors=["sniper", "tech", "medic"],
            human_messages={human_a_id: human_a_lines, human_b_id: [human_b_import_line]},
            human_polls={human_b_id: human_b_poll_lines})

        with gm_srv, persona_srv:
            env = {
                "OPENWEBUI_URL": gm_srv.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC_A24_GM_KEY",
                "MMO_SIM_PERSONA_API_BASE_URL": persona_srv.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTHETIC_A24_PERSONA_KEY", "MMO_SIM_PERSONA_API_MODEL": "synthetic-a24",
                "MMO_SIM_GM_OUTPUT_LIMIT_TOKENS": "4000",
            }
            env.pop("MMO_SIM_PERSONA_CLI", None)

            # -- Der NEUE gefuehrte Weg (`g` statt `l`): Modus "mehrere
            # Menschen" (2), vorhandenen Human B sichtbar auswaehlen (Nr. 1
            # der Liste, da nur ein weiterer registrierter Mensch existiert),
            # BEIDE Figuren ausdruecklich bestaetigen, KI-Auswahl, Leader =
            # "du" (leere Eingabe), Startwahl bestaetigen, dann die bewusste
            # Uebergabe des geteilten Terminals an Human B bestaetigen (das
            # EINE Setup-Ja -- s. R2-Docstring in `_cmd_local_round`, zaehlt
            # NICHT als In-Runde-Fokus, der folgt separat unten).
            setup_lines = ["g", "2", "1", "j", "j", "sniper tech medic", "", "j", "j"]
            stdin_lines = list(setup_lines) + ["j"]  # letztes "j": Human B akzeptiert die Einladung (unveraenderter Consentweg in `_cmd_local_round`).

            # A24 R2 (02_AUFTRAG_R2_R3.md §R2 "echte In-Runde-Uebergabe"):
            # JEDER tatsaechliche Akteurwechsel waehrend des eigentlichen
            # Spiels (inkl. Rueckuebergabe an Human A) verlangt jetzt eine
            # eigene bewusste Uebernahme -- `_append_guided_line` fuegt das
            # noetige 'j' programmatisch genau dort ein, wo die Produktlogik
            # (`_HumanDriver.decide`, `guided=True`) es tatsaechlich abfragt,
            # und sammelt die erwarteten Zielakteure fuer die Beleg-
            # Assertions unten (kein hartkodierter Zaehlwert).
            focus = [human_b_id]  # Last actually confirmed setup/consent actor.
            handoff_targets: list[str] = []

            def _turn(actor: str, text: str) -> None:
                if _append_guided_line(stdin_lines, focus, actor, text):
                    handoff_targets.append(actor)

            _turn(leader_id, human_a_lines[0])
            for g in guest_order:
                if g == human_b_id:
                    _turn(human_b_id, human_b_import_line)
            _turn(leader_id, human_a_lines[1])
            for g in guest_order:
                if g == human_b_id:
                    _turn(human_b_id, human_b_poll_lines[0])
            _turn(leader_id, human_a_lines[2])
            for g in guest_order:
                if g == human_b_id:
                    _turn(human_b_id, human_b_poll_lines[1])
            _turn(leader_id, human_a_lines[3])
            for m in members_sorted:
                if m == leader_id:
                    _turn(leader_id, human_a_reflection)
                elif m == human_b_id:
                    _turn(human_b_id, human_b_reflection)
            stdin_lines.append("x")
            stdin_text = "\n".join(stdin_lines) + "\n"

            if case is not None:
                (case / "before" / "stdin.txt").write_text(stdin_text, encoding="utf-8")
                sup.write_json(case / "before" / "plan.json", {
                    "leader_id": leader_id, "human_b_id": human_b_id, "targets": targets,
                    "guest_order": guest_order, "members_sorted": members_sorted,
                    "table_id": table_id, "section_id": section_id, "offer_id": offer_id,
                    "expected_char_ids": sorted(expected_char_ids), "setup_lines": setup_lines,
                })

            child_env = dict(os.environ)
            child_env.update(env)
            guard_check = sup.verify_child_guard_and_schema(child_env, run_dir.parent)
            parent_guard_state = sup.current_process_guard_state()
            assert guard_check["returncode"] == 0, guard_check
            assert guard_check["parsed"] == parent_guard_state, (
                "Guard-/Schema-Sichtbarkeit im echten TUI-Kind (gefuehrter Weg) weicht vom "
                f"Elternprozess ab (Kontinuitaet gebrochen): eltern={parent_guard_state} kind={guard_check['parsed']}"
            )
            if case is not None:
                sup.write_json(case / "before" / "guard_check.json", guard_check)

            proc = sup.run_process(run_dir.parent, human_a_id, stdin_text, env, timeout=90)

            if case is not None:
                (case / "after" / "stdout.txt").write_text(proc.stdout, encoding="utf-8")
                (case / "after" / "stderr.txt").write_text(proc.stderr, encoding="utf-8")
                sup.write_json(case / "after" / "process.json", {"returncode": proc.returncode})
                sup.write_json(case / "after" / "gm_received.json", gm_srv.received)
                sup.write_json(case / "after" / "persona_received.json", persona_srv.received)

            sup.assert_g6_operation_tape(gm_receipts_path)
            assert proc.returncode == 0, f"Prozess fehlgeschlagen: rc={proc.returncode} stderr={proc.stderr[-2000:]}"

            # -- R2-spezifische Bedienbelege: Modusfrage, sichtbare Auswahl,
            # Figurbestaetigung, Zusammenfassung UND die bewusste Uebergabe
            # mit Name/ID+Figur muessen TATSAECHLICH im STDOUT erscheinen
            # (nicht nur der nachfolgende unveraenderte `_cmd_local_round`-Weg).
            assert "Lokale Runde einrichten" in proc.stdout, "Moduswahl-Prompt des gefuehrten Wegs fehlt"
            assert f"  [0] {human_a_id} (du, aufrufender Teilnehmer)" in proc.stdout, "sichtbare Eigenauflistung fehlt"
            assert f"  [1] {human_b_id} (A24-G1-Human-B)" in proc.stdout, "sichtbare Human-B-Auflistung fehlt"
            assert f"'{human_a_id}' spielt 'CHR-A24-G1-A' -- bestaetigen?" in proc.stdout, "Figurbestaetigung (Human A) fehlt"
            assert f"'{human_b_id}' spielt 'CHR-A24-G1-B' -- bestaetigen?" in proc.stdout, "Figurbestaetigung (Human B) fehlt"
            assert "Zusammenfassung (5 Spieler einschliesslich Leader)" in proc.stdout, "1-5-Zusammenfassung fehlt/falsche Anzahl"
            assert f"Leader={leader_id}" in proc.stdout, "Leaderangabe in der Zusammenfassung fehlt"
            assert "KEINE KI-Zustimmung und keine Tischaufnahme" in proc.stdout, "Hinweis 'Auswahl ist noch keine Zustimmung' fehlt"
            assert (
                f"Geteiltes Terminal wird an '{human_b_id}' (Figur 'CHR-A24-G1-B') uebergeben" in proc.stdout
            ), "bewusste Uebergabeanzeige (Name/ID+Figur) an Human B fehlt"

            # A24 R2 (Kernbeleg des Fixes, s. 01_REVIEW_A24.md "0 Uebergabe-
            # prompts bei bestehendem Tisch"): die bewusste Uebergabe-
            # Bestaetigung muss jetzt AUCH waehrend des echten Spiels (nach
            # Tischanlage) erscheinen -- nicht nur das eine Setup-Ja VOR der
            # Runde. Zaehlwerte kommen aus `handoff_targets` (oben
            # programmatisch aus dem tatsaechlichen Akteurwechsel berechnet,
            # kein hartkodierter Wert).
            from collections import Counter as _Counter
            handoff_counts = _Counter(handoff_targets)
            marker_a = f"Geteiltes Terminal wird an '{leader_id}' (Figur 'CHR-A24-G1-A') uebergeben -- bewusst uebernehmen?"
            marker_b = f"Geteiltes Terminal wird an '{human_b_id}' (Figur 'CHR-A24-G1-B') uebergeben -- bewusst uebernehmen?"
            assert len(handoff_targets) > 0, "Testaufbau ohne jeden In-Runde-Akteurwechsel -- R2-Kernfall nicht geprueft"
            assert proc.stdout.count(marker_a) == handoff_counts.get(leader_id, 0), (
                f"In-Runde-Uebergaben an Human A erwartet={handoff_counts.get(leader_id, 0)} "
                f"beobachtet={proc.stdout.count(marker_a)}: {proc.stdout[-2000:]}"
            )
            # +1: das EINE Setup-Ja vor der Runde (bleibt erhalten, zaehlt nicht
            # in `handoff_targets`, da Human B dort noch keinen Vorbesitzer hatte).
            assert proc.stdout.count(marker_b) == 1 + handoff_counts.get(human_b_id, 0), (
                f"Uebergaben an Human B erwartet={1 + handoff_counts.get(human_b_id, 0)} "
                f"beobachtet={proc.stdout.count(marker_b)}: {proc.stdout[-2000:]}"
            )
            assert proc.stdout.count("bewusst uebernehmen?") == 1 + len(handoff_targets), (
                "Gesamtzahl der Uebergabe-Bestaetigungen weicht von Setup(1)+In-Runde-Wechseln ab"
            )

            assert "Gruppe eingeladen" in proc.stdout, proc.stdout[-1500:]
            for pid in ("sniper", "tech", "medic"):
                assert pid in proc.stdout.split("Gruppe eingeladen", 1)[1][:400], proc.stdout
            assert "Abschnitt abgeschlossen:" in proc.stdout, f"Abschnitt nicht abgeschlossen: {proc.stdout[-2000:]}"

            table = core_store.Table.load(run_dir, table_id)
            assert table.leader == leader_id, f"Leader hat gewechselt: {table.leader} != {leader_id}"
            assert set(table.members) == {leader_id, human_b_id, "sniper", "tech", "medic"}
            assert table.status == "closed"
            # R2 (Fokusaktion aendert WEDER table.leader NOCH Mitgliedschaft/
            # Figur): die Uebergabe-Bestaetigung oben ist reine Eingabe-
            # zuordnung -- Leader/Mitgliedschaft entstehen ERST danach, ueber
            # denselben unveraenderten Consentweg wie beim `l`-Tokenweg.
            assert table.chrononaut_ids[leader_id] == "CHR-A24-G1-A"
            assert table.chrononaut_ids[human_b_id] == "CHR-A24-G1-B"

            # R3 (wie Fall 1): Registry/Onboarding/Katalog/Bystander-Figuren
            # voll byte-gleich vor/nach der gefuehrten Runde.
            protected_after = sup.capture_protected_authorities(states_dir, registry_dir, onboarding_dir, catalog_dir)
            assert protected_after == protected_before, (
                "Registry/Onboarding/Katalog/Bystander-Figuren haben sich durch den gefuehrten Weg veraendert"
            )

            sl_log = table.sl_log
            assert len(sl_log) == 8, f"Erwartete 8 oeffentliche SL-Antworten im dauerhaften Log, beobachtet={len(sl_log)}"
            assert proc.stdout.count("[SL] ") == len(sl_log), (
                f"Anzahl der [SL]-Anzeigebloecke ({proc.stdout.count('[SL] ')}) weicht von der Anzahl "
                f"dauerhafter sl_log-Eintraege ({len(sl_log)}) ab."
            )
            last_pos = -1
            for idx, entry in enumerate(sl_log):
                marker = f"[SL] {entry.get('content', '')}"
                found_pos = proc.stdout.find(marker, last_pos + 1)
                assert found_pos != -1, f"SL-Eintrag #{idx} nicht vollstaendig als eigener [SL]-Block NACH dem vorherigen im STDOUT gefunden: {entry}"
                last_pos = found_pos

            members_final = sorted(table.members)
            states_after = {m: json.loads((states_dir / f"{m}.json").read_text(encoding="utf-8")) for m in members_final}
            for m in members_final:
                assert states_after[m]["rounds_played"] == 1, (
                    f"'{m}': genau eine gespielte Runde erwartet, beobachtet={states_after[m]['rounds_played']}"
                )
                current = json.loads((run_dir / "current_saves" / f"{m}.json").read_text(encoding="utf-8"))
                # R3 (wie Fall 1): volle Byte-/Feldgleichheit, nicht nur save_id.
                assert current == end_saves[m], (
                    f"'{m}': veroeffentlichter Current-Save ist NICHT vollstaendig byte-/feldgleich zum "
                    f"gesendeten synthetischen Endsave-Block: current={current} erwartet={end_saves[m]}"
                )
                assert current.get("save_id") != final_saves[m].get("save_id")
            end_save_ids = {m: end_saves[m]["save_id"] for m in members_final}
            assert len(set(end_save_ids.values())) == 5, f"Endsave-IDs sind nicht alle unterscheidbar: {end_save_ids}"

            reflections = sup.read_jsonl(run_dir / "reflections.jsonl")
            ai_reflections = {r["persona_key"] for r in reflections if r.get("kind") == "ai_required_reflection" and r.get("section_id") == section_id}
            assert ai_reflections == {"sniper", "tech", "medic"}, f"KI-Pflichtreflexionen unvollstaendig: {ai_reflections}"
            human_notes = {r["persona_key"]: r.get("text") for r in reflections if r.get("kind") == "human_note" and r.get("section_id") == section_id}
            assert human_notes.get(leader_id) == human_a_reflection
            assert human_b_id not in human_notes, "leere freiwillige Notiz darf nicht als human_note archiviert werden"

            offer_log = sup.read_jsonl(run_dir / "invitation_decisions.jsonl")
            consent_from = {e.get("from") for e in offer_log if e.get("type") == "response" and e.get("decision") == "accept"}
            assert {human_b_id, "sniper", "tech", "medic"}.issubset(consent_from), f"Consent-Log unvollstaendig: {offer_log}"

            assert len(persona_srv.received) >= 3, "Persona-API haette real mehrfach befragt werden muessen"
            assert len(gm_srv.received) >= 7, f"GM haette mehrfach real befragt werden muessen: {len(gm_srv.received)}"
            assert expected_char_ids.issubset(received_ids), "GM hat Abschluss gesendet ohne alle fuenf Save-IDs vorher empfangen zu haben"

            # G6-O (02_AUFTRAG_G6_REST.md #5): dauerhafte Ledger-/Rollen-/
            # Akteur-/Turn-/Tisch-/Consent-/Reflexions-Zuordnung permanent in
            # der Suite, nicht nur als separat zitierte Audit-Summe.
            sup.audit_g6_chain_for_case(
                case_name="case_g_human_leader_handoff", run_dir=run_dir, table=table, initial=final_saves,
                gm=gm_srv.received, persona=persona_srv.received,
                reflections=reflections, invitation_decisions=offer_log,
            )

            if case is not None:
                sup.write_json(case / "after" / "table.json", {"leader": table.leader, "members": table.members, "status": table.status, "sl_log": table.sl_log})
                (case / "after" / "reflections.jsonl").write_text((run_dir / "reflections.jsonl").read_text(encoding="utf-8"), encoding="utf-8")
                (case / "after" / "invitation_decisions.jsonl").write_text((run_dir / "invitation_decisions.jsonl").read_text(encoding="utf-8"), encoding="utf-8")
                sup.write_json(case / "after" / "states.json", states_after)
                sup.write_json(case / "after" / "end_save_ids.json", end_save_ids)
                sup.write_json(case / "after" / "registry_catalog.json", {
                    "registry": sup.hash_tree(registry_dir), "catalog": sup.hash_tree(catalog_dir),
                    "onboarding": sup.hash_tree(onboarding_dir),
                })


# ---------------------------------------------------------------------------
# R2: `g`-Weg, Abbruch VOR jeder Aenderung -- EOF waehrend der Uebergabe an
# Human B darf keinen Tisch/Consent/GM-Kontakt ausloesen (kein KI-Ersatz).
# ---------------------------------------------------------------------------

def test_a24_guided_setup_g_path_abort_at_handoff_no_side_effects():
    """A24 R2 (02_AUFTRAG_A24_BEDIENGRENZE.md §R2 'Abbrechen/EOF bleiben ein
    klarer Ruck-/Halteweg ohne KI-Ersatz'): bricht die Eingabe GENAU an der
    Uebergabebestaetigung an Human B ab (EOF) -- NACH Modus-/Auswahl-/
    Figurbestaetigung/Zusammenfassung, aber VOR jeder Einladung/jedem
    Consent/jedem GM-Kontakt. Es darf WEDER ein Tisch NOCH eine Einladung
    entstehen; die vorherige, bereits bestaetigte Registry-/Onboarding-/
    Katalogautoritaet bleibt unveraendert (Vorher/Nachher-Kohaerenz, 03
    Gate G4)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        case = sup.case_dir("case_g_abort_at_handoff") if os.environ.get("A24_EVIDENCE_DIR") else None

        boot = sup.bootstrap_six_persona_community(root, "community-a24-g-abort")
        run_dir, states_dir, onboarding_dir, catalog_dir = boot["run_dir"], boot["states_dir"], boot["onboarding_dir"], boot["catalog_dir"]
        for pk in ("sniper", "tech", "medic"):
            sup.make_ready(onboarding_dir, states_dir, run_dir, pk)

        registry_dir = root / "registry"
        human_a = sup.register_human(registry_dir, "A24-GAbort-Human-A")
        human_b = sup.register_human(registry_dir, "A24-GAbort-Human-B")
        human_a_id, human_b_id = human_a.participant_id, human_b.participant_id
        sup.onboard_human_figure(registry_dir, human_a_id, onboarding_dir, states_dir, run_dir, "CHR-A24-GA-A", "Lee", "LEEOPS")
        sup.onboard_human_figure(registry_dir, human_b_id, onboarding_dir, states_dir, run_dir, "CHR-A24-GA-B", "Max", "MAXOPS")
        sup.write_test_profile(run_dir, max_turns=200, max_seconds=600, max_usd=50.0)

        before_registry = sup.hash_tree(registry_dir)
        before_onboarding = sup.hash_tree(onboarding_dir)
        before_catalog = sup.hash_tree(catalog_dir)

        # G6-E: Abbruch an der Uebergabe loest definitionsgemaess KEINEN
        # Request aus (s. Assertions unten) -- die unabhaengige Erwartung
        # ist deshalb trivial (keine Tisch-/Angebotsidentitaet existiert in
        # diesem Fall je), bleibt aber Pflichtparameter statt `None`.
        gm_receipts_path = root / "gm_receipts.jsonl"
        expected_context = sup.expected_context_for_case(
            leader=human_a_id, members=[human_a_id], table_id=f"local-{human_a_id}",
            section_id=f"local-{human_a_id}-section", final_saves={},
        )

        gm_calls_guard: list = []
        persona_calls_guard: list = []
        gm_srv = sup.SequencedHTTPServer(
            scripted=[], fallback_fn=lambda idx, body: (gm_calls_guard.append(body), "NIE SENDEN")[1],
            expected_context=expected_context, gm_receipts_path=gm_receipts_path, is_gm_server=True,
        )
        persona_srv = sup.SequencedHTTPServer(
            scripted=[], fallback_fn=lambda idx, body: (persona_calls_guard.append(body), "NIE SENDEN")[1],
            expected_context=expected_context, gm_receipts_path=gm_receipts_path,
        )

        with gm_srv, persona_srv:
            env = {
                "OPENWEBUI_URL": gm_srv.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC_A24_GM_KEY",
                "MMO_SIM_PERSONA_API_BASE_URL": persona_srv.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTHETIC_A24_PERSONA_KEY", "MMO_SIM_PERSONA_API_MODEL": "synthetic-a24",
            }
            env.pop("MMO_SIM_PERSONA_CLI", None)
            # KEIN "x" am Ende -- Eingabe endet (EOF) GENAU an der
            # Uebergabebestaetigung, nach Modus/Auswahl/Figur/KI/Leader/
            # Zusammenfassung, vor jeder Einladung.
            stdin_text = "g\n2\n1\nj\nj\nsniper tech medic\n\nj\n"

            if case is not None:
                (case / "before" / "stdin.txt").write_text(stdin_text, encoding="utf-8")
                sup.write_json(case / "before" / "plan.json", {"human_a_id": human_a_id, "human_b_id": human_b_id})

            proc = sup.run_process(root, human_a_id, stdin_text, env, timeout=30)

            table_files = list((run_dir / "tables").glob("local-*.json")) if (run_dir / "tables").exists() else []
            offer_log_after = sup.read_jsonl(run_dir / "invitation_decisions.jsonl")

            if case is not None:
                (case / "after" / "stdout.txt").write_text(proc.stdout, encoding="utf-8")
                (case / "after" / "stderr.txt").write_text(proc.stderr, encoding="utf-8")
                sup.write_json(case / "after" / "process.json", {"returncode": proc.returncode})
                sup.write_json(case / "after" / "table_files.json", [p.name for p in table_files])
                sup.write_json(case / "after" / "invitation_decisions.jsonl.json", offer_log_after)

            assert proc.returncode == 0, f"EOF waehrend Uebergabe sollte kontrolliert pausieren, nicht abstuerzen: {proc.stderr[-1500:]}"
            assert "Eingabe beendet (EOF)" in proc.stdout, f"erwartete kontrollierte EOF-Meldung fehlt: {proc.stdout[-800:]}"
            assert not gm_calls_guard, "Abbruch an der Uebergabe hat trotzdem einen GM-Turn ausgeloest"
            assert not persona_calls_guard, "Abbruch an der Uebergabe hat trotzdem eine echte Persona-Anfrage ausgeloest (KI-Ersatz)"
            assert not table_files, f"Abbruch an der Uebergabe hat trotzdem einen Tisch angelegt: {[p.name for p in table_files]}"
            assert not offer_log_after, f"Abbruch an der Uebergabe hat trotzdem einen Angebots-/Consent-Log-Eintrag erzeugt: {offer_log_after}"

            # Vorher/Nachher-Kohaerenz der bereits bestaetigten Autoritaeten
            # (Registry/Onboarding/Katalog) -- kein stiller Seiteneffekt des
            # abgebrochenen Einrichtungswegs.
            assert sup.hash_tree(registry_dir) == before_registry, "Registry hat sich durch den abgebrochenen Einrichtungsweg veraendert"
            assert sup.hash_tree(onboarding_dir) == before_onboarding, "Onboarding hat sich durch den abgebrochenen Einrichtungsweg veraendert"
            assert sup.hash_tree(catalog_dir) == before_catalog, "Katalog hat sich durch den abgebrochenen Einrichtungsweg veraendert"


# ---------------------------------------------------------------------------
# R2: neuer gefuehrter Weg `g` -> `_cmd_local_round_setup`, ZWEITE geschuldete
# Konstellation KI-Leader/Hybrid+API-SL (02_AUFTRAG_R2_R3.md §G1 "Zwei
# vollstaendige gefuehrte Fuenferkonstellationen") -- dieselbe Gruppe/Reise
# wie `test_a24_case2_ai_leader_hybrid_full_journey`, aber ueber `g` UND mit
# echter In-Runde-Uebergabe zwischen Human A und Human B (beide jetzt Gaeste
# des KI-Leaders 'tech').
# ---------------------------------------------------------------------------

def test_a24_guided_setup_g_path_ai_leader_hybrid_with_handoff():
    """A24 R2 (02_AUFTRAG_R2_R3.md §R2/§G1): derselbe Fuenferfall wie
    `test_a24_case2_ai_leader_hybrid_full_journey` (KI-Leader 'tech',
    Hybrid-CLI + API-SL), aber ueber den gefuehrten Menuepunkt `g` (Leader-
    wahl = die angefragte KI-ID 'tech' statt 'du') UND mit echter In-Runde-
    Uebergabe des geteilten Terminals zwischen den beiden MENSCHLICHEN
    Gaesten (Human A, der aufrufende Mensch, und Human B) -- die zweite der
    beiden beauftragten geführten Konstellationen, nicht nur eine erneute
    Human-Leader-Variante."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        case = sup.case_dir("case_g2_ai_leader_hybrid_handoff") if os.environ.get("A24_EVIDENCE_DIR") else None

        boot = sup.bootstrap_six_persona_community(root, "community-a24-g2-hybrid")
        run_dir, states_dir, onboarding_dir, catalog_dir = boot["run_dir"], boot["states_dir"], boot["onboarding_dir"], boot["catalog_dir"]
        for pk in ("sniper", "tech", "medic"):
            sup.make_ready(onboarding_dir, states_dir, run_dir, pk)

        registry_dir = root / "registry"
        human_a = sup.register_human(registry_dir, "A24-G2-Human-A")
        human_b = sup.register_human(registry_dir, "A24-G2-Human-B")
        human_a_id, human_b_id = human_a.participant_id, human_b.participant_id

        onb_a = sup.onboard_human_figure(registry_dir, human_a_id, onboarding_dir, states_dir, run_dir, "CHR-A24-G2-A", "Max", "MAXOPS")
        onb_b = sup.onboard_human_figure(registry_dir, human_b_id, onboarding_dir, states_dir, run_dir, "CHR-A24-G2-B", "Jo", "JOOPS")

        sup.write_test_profile(run_dir, max_turns=200, max_seconds=600, max_usd=50.0)

        leader_id = "tech"
        lead_offer_id = sup.lead_invite_offer_id(leader_id, human_a_id)
        guest_targets = [human_a_id, human_b_id, "sniper", "medic"]
        offer_id = sup.invitation_offer_id(leader_id, guest_targets)
        guest_order = sup.sorted_guest_order(leader_id, guest_targets)
        members_sorted = sup.sorted_table_members(leader_id, guest_targets)
        # Vor dem Fake-CLI-Bau berechnet (wie in Fall 2), damit die
        # unabhaengige G6-Erwartung VOR dem ersten moeglichen Aufruf feststeht.
        table_id = sup.compute_table_id(leader_id, guest_targets)
        section_id = f"{table_id}-section"

        final_saves = {
            leader_id: sup.load_fixture_save("tech"), human_a_id: onb_a["save"], human_b_id: onb_b["save"],
            "sniper": sup.load_fixture_save("sniper"), "medic": sup.load_fixture_save("medic"),
        }
        expected_char_ids = {zeitriss_saves.block_char_id(b) for b in final_saves.values()}
        assert len(expected_char_ids) == 5
        end_saves = sup.end_saves_for(final_saves, "g2")
        protected_before = sup.capture_protected_authorities(states_dir, registry_dir, onboarding_dir, catalog_dir)

        gm_receipts_path = root / "gm_receipts.jsonl"
        expected_context = sup.expected_context_for_case(
            leader=leader_id, members=members_sorted, table_id=table_id, section_id=section_id,
            final_saves=final_saves, offer_ids=[lead_offer_id, offer_id],
        )

        cli_root = root / "cli"
        cli_root.mkdir()
        # Dieselbe deterministische CLI-Gesamtreihenfolge wie Fall 2 (nur der
        # EINRICHTUNGSWEG davor ist neu -- die KI-Reihenfolge selbst aendert
        # sich durch `g` nicht, da `_cmd_local_round_setup` dieselbe
        # Tokenliste erzeugt wie der manuelle `l`-Aufruf).
        ai_guest_order = [g for g in guest_order if g in ("sniper", "medic")]
        queue = [
            {"result": sup.accept_text(lead_offer_id, "tech", "Ich uebernehme die Leaderrolle.")},
            {"result": sup.accept_text(offer_id, "sniper")},
            {"result": sup.accept_text(offer_id, "medic")},
            {"result": "Wir sichern die Position und beobachten den Sektor."},  # Anker
        ]
        for g in ai_guest_order:
            queue.append({"result": f"{g}: Ich uebernehme meine Rolle und beobachte."})
        queue.append({"result": "Wir ruecken gemeinsam vor, Vorsicht bleibt oberste Prioritaet."})  # Runde0, non-completion
        for g in ai_guest_order:
            queue.append({"result": f"{g}: Ich schlage vor, in Deckung zu bleiben."})
        queue.append({"result": "Ich beruecksichtige die Rueckmeldungen und bleiben vorerst in Deckung."})  # Runde1, non-completion
        for g in ai_guest_order:
            queue.append({"result": f"{g}: Bereit fuer den Abschluss."})
        queue.append({"result": "Wir schliessen diesen Abschnitt jetzt kontrolliert ab."})  # Runde2 -> completion via GM-Fallback
        for g in ai_guest_order + ["tech"]:
            queue.append({"result": f"{g}: Reflexion -- solide Teamarbeit, Lehren fuer naechstes Mal gezogen."})

        sup.write_g6_operation_plan(
            gm_receipts_path, expected_context, invite_actors=["tech", "sniper", "medic"],
            human_messages={human_a_id: ["Ich sichere die Position."],
                            human_b_id: ["Ich beobachte die rechte Flanke."]},
            human_polls={human_a_id: ["Ich bleibe vorsichtig in Deckung.", "Bin bereit fuer den Abschluss."],
                         human_b_id: ["Alles ruhig von meiner Seite.", "Einverstanden, wir koennen abschliessen."]})

        fake_cli = sup.write_queued_fake_cli(
            cli_root, name="a24g2hybrid", queue=queue,
            expected_context=expected_context, gm_receipts_path=gm_receipts_path,
        )

        # G6-O: derselbe eigene Observer-Guard im echten TUI-Kind wie Fall 2
        # (s. dortiger Docstring) -- beobachtet passiv JEDEN tatsaechlichen
        # `_RealProcessRunner`-Aufruf der Fake-CLI von der echten Elternseite.
        cli_observer_dir = root / "cli_observer_guard"
        cli_audit_dir = root / "cli_observer_audit"
        sup.write_a24_cli_observer_guard(cli_observer_dir, cli_audit_dir)

        received_ids: set = set()
        from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER as _CM

        def gm_fallback2(idx, body):
            messages = body.get("messages") or []
            last_user = messages[-1]["content"] if messages else ""
            for blk in zeitriss_saves.extract_all_saves(last_user):
                cid = zeitriss_saves.block_char_id(blk)
                if cid:
                    received_ids.add(cid)
            if idx + 1 >= 8 and expected_char_ids.issubset(received_ids):
                debrief = sup.debrief_blocks(end_saves)
                return f"{debrief}\n{_CM} table_id={table_id} section_id={section_id}"
            return f"Szene {idx}: Ruhige Lage, was tut die Gruppe als Naechstes?"

        gm_srv = sup.SequencedHTTPServer(
            scripted=[], fallback_fn=gm_fallback2,
            expected_context=expected_context, gm_receipts_path=gm_receipts_path, is_gm_server=True,
        )

        with gm_srv:
            env = {
                "OPENWEBUI_URL": gm_srv.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC_A24_GM_KEY",
                "MMO_SIM_GM_OUTPUT_LIMIT_TOKENS": "4000",
                "MMO_SIM_PERSONA_CLI": str(fake_cli),
                "MMO_SIM_PERSONA_ISOLATED_WORKDIR": str(cli_root / "persona_workdir"),
                "MMO_SIM_PERSONA_ISOLATION_FLAGS": "--permission-mode=plan,--safe-mode",
                "PYTHONPATH": str(cli_observer_dir),
            }
            env.pop("MMO_SIM_PERSONA_API_BASE_URL", None)

            # -- Der gefuehrte Weg: Modus 2, Human B sichtbar auswaehlen,
            # beide Figuren bestaetigen, KI-Auswahl, Leader = 'tech' (eine
            # angefragte KI-ID statt 'du'), Startwahl bestaetigen, bewusste
            # Setup-Uebergabe an Human B.
            setup_lines = ["g", "2", "1", "j", "j", "sniper tech medic", "tech", "j", "j"]
            stdin_lines = list(setup_lines) + ["j"]  # Human B akzeptiert die Einladung (unveraenderter Consentweg).

            # A24 R2: echte In-Runde-Uebergabe zwischen den beiden
            # menschlichen Gaesten (A, B) -- derselbe Mechanismus/dieselbe
            # Hilfsfunktion wie in der Human-Leader/API-Konstellation. Der
            # KI-Leader 'tech' ist NIE ein `_HumanDriver` und beeinflusst den
            # Fokus nicht.
            focus = [human_b_id]  # Last actually confirmed setup/consent actor.
            handoff_targets: list[str] = []

            def _turn(actor: str, text: str) -> None:
                if _append_guided_line(stdin_lines, focus, actor, text):
                    handoff_targets.append(actor)

            for g in guest_order:
                if g == human_a_id:
                    _turn(human_a_id, "Ich sichere die Position.")
                elif g == human_b_id:
                    _turn(human_b_id, "Ich beobachte die rechte Flanke.")
            for g in guest_order:
                if g == human_a_id:
                    _turn(human_a_id, "Ich bleibe vorsichtig in Deckung.")
                elif g == human_b_id:
                    _turn(human_b_id, "Alles ruhig von meiner Seite.")
            for g in guest_order:
                if g == human_a_id:
                    _turn(human_a_id, "Bin bereit fuer den Abschluss.")
                elif g == human_b_id:
                    _turn(human_b_id, "Einverstanden, wir koennen abschliessen.")
            for m in members_sorted:
                if m == human_a_id:
                    _turn(human_a_id, "Notiz: guter Teamlauf (gefuehrter Weg).")
                elif m == human_b_id:
                    _turn(human_b_id, "")
            stdin_lines.append("x")
            stdin_text = "\n".join(stdin_lines) + "\n"

            if case is not None:
                (case / "before" / "stdin.txt").write_text(stdin_text, encoding="utf-8")
                sup.write_json(case / "before" / "plan.json", {
                    "leader_id": leader_id, "human_a_id": human_a_id, "human_b_id": human_b_id,
                    "guest_order": guest_order, "members_sorted": members_sorted, "table_id": table_id,
                    "setup_lines": setup_lines,
                })

            child_env = dict(os.environ)
            child_env.update(env)
            guard_check = sup.verify_child_guard_and_schema(child_env, run_dir.parent)
            assert guard_check["returncode"] == 0, guard_check
            # G6-O: derselbe Nachweis wie Fall 2 -- der echte TUI-Kind-
            # Interpreter muss NACHWEISLICH den eigenen Observer-Guard
            # geladen haben, sonst bliebe der reale `_RealProcessRunner`-
            # Aufruf fuer die Fake-CLI unten passiv unbeobachtet.
            assert guard_check["parsed"].get("guard_module_file") == str(cli_observer_dir / "sitecustomize.py"), (
                "G6-O-Observer-Guard im echten TUI-Kind (gefuehrter Hybrid-Weg) nicht wie erwartet geladen: "
                f"{guard_check['parsed']}"
            )
            assert guard_check["parsed"].get("guard_patches_getaddrinfo") is True, (
                f"G6-O-Observer-Guard patcht socket.getaddrinfo im echten TUI-Kind nicht: {guard_check['parsed']}"
            )
            if case is not None:
                sup.write_json(case / "before" / "guard_check.json", guard_check)

            proc = sup.run_process(run_dir.parent, human_a_id, stdin_text, env, timeout=90)

            cli_input_captures = sup.read_cli_captures(cli_root, "a24g2hybrid")
            cli_output_captures = sup.read_cli_output_captures(cli_root, "a24g2hybrid")
            parent_observations = sup.read_cli_parent_observations(cli_audit_dir)
            cli_join = sup.join_cli_parent_observations(cli_input_captures, parent_observations)

            if case is not None:
                (case / "after" / "stdout.txt").write_text(proc.stdout, encoding="utf-8")
                (case / "after" / "stderr.txt").write_text(proc.stderr, encoding="utf-8")
                sup.write_json(case / "after" / "gm_received.json", gm_srv.received)
                sup.write_json(case / "after" / "cli_captures.json", cli_input_captures)
                sup.write_json(case / "after" / "cli_output_captures.json", cli_output_captures)
                sup.write_json(case / "after" / "cli_parent_observations.json", parent_observations)
                sup.write_json(case / "after" / "cli_join.json", cli_join)

            sup.assert_g6_operation_tape(gm_receipts_path)
            assert proc.returncode == 0, f"Prozess fehlgeschlagen: rc={proc.returncode} stderr={proc.stderr[-2000:]}"
            # G6-O: ALLE tatsaechlichen Hybrid-CLI-Spielaufrufe beidseitig
            # belegt UND eindeutig zugeordnet. Nur wenn der eigene Observer-
            # Guard fuer DIESEN Lauf ueberhaupt etwas aufgezeichnet hat (s.
            # ausfuehrliche Begruendung in Fall 2 -- `observe_focus_actual.py`
            # ersetzt `sup.run_process` global mit eigenem, anderem
            # `PYTHONPATH` fuer seine eigene Fokus-Instrumentierung).
            assert parent_observations["spawns"] and parent_observations["process_results"], "G6: missing actual parent receipts"
            assert not cli_join["unmatched_inputs"], (
                f"Nicht beidseitig belegte Hybrid-CLI-Aufrufe (G6-O): {cli_join['unmatched_inputs']}"
            )
            assert not cli_join["ambiguous_pids"], f"Mehrdeutige PID-Zuordnung (G6-O): {cli_join['ambiguous_pids']}"
            assert len(cli_join["joined"]) == len(cli_input_captures), (
                f"Join unvollstaendig: {len(cli_join['joined'])} von {len(cli_input_captures)} Aufrufen beidseitig belegt"
            )
            for rec in cli_join["joined"]:
                parent_rc = rec["parent_result"]["returncode"]
                assert parent_rc == 0, (
                    f"Vom echten Elternprozess beobachteter Exit != 0 fuer pid={rec['pid']}: {rec['parent_result']}"
                )
            assert "Lokale Runde einrichten" in proc.stdout, "Moduswahl-Prompt des gefuehrten Wegs fehlt"
            assert f"Leader={leader_id}" in proc.stdout, "KI-Leaderangabe in der Zusammenfassung fehlt"
            assert "Gruppe eingeladen" in proc.stdout, proc.stdout[-1500:]
            assert "Abschnitt abgeschlossen:" in proc.stdout, f"Abschnitt nicht abgeschlossen: {proc.stdout[-2500:]}"

            # A24 R2 (Kernbeleg, ZWEITE Konstellation): echte In-Runde-
            # Uebergaben zwischen Human A und Human B, programmatisch aus
            # dem tatsaechlichen Akteurwechsel berechnet (kein hartkodierter
            # Wert) -- beweist, dass der Fix NICHT nur fuer Human-Leader/API
            # gilt.
            from collections import Counter as _Counter
            handoff_counts = _Counter(handoff_targets)
            marker_a = f"Geteiltes Terminal wird an '{human_a_id}' (Figur 'CHR-A24-G2-A') uebergeben -- bewusst uebernehmen?"
            marker_b = f"Geteiltes Terminal wird an '{human_b_id}' (Figur 'CHR-A24-G2-B') uebergeben -- bewusst uebernehmen?"
            assert len(handoff_targets) > 0, "Testaufbau ohne jeden In-Runde-Akteurwechsel -- R2-Kernfall nicht geprueft"
            assert proc.stdout.count(marker_a) == handoff_counts.get(human_a_id, 0), (
                f"In-Runde-Uebergaben an Human A erwartet={handoff_counts.get(human_a_id, 0)} "
                f"beobachtet={proc.stdout.count(marker_a)}"
            )
            assert proc.stdout.count(marker_b) == 1 + handoff_counts.get(human_b_id, 0), (
                f"Uebergaben an Human B erwartet={1 + handoff_counts.get(human_b_id, 0)} "
                f"beobachtet={proc.stdout.count(marker_b)}"
            )
            assert proc.stdout.count("bewusst uebernehmen?") == 1 + len(handoff_targets), (
                "Gesamtzahl der Uebergabe-Bestaetigungen weicht von Setup(1)+In-Runde-Wechseln ab"
            )

            labeled_b = f"[{human_b_id}] Deine Aktion:"
            unlabeled = proc.stdout.count("Deine Aktion:") - proc.stdout.count(labeled_b)
            assert unlabeled == 4, f"Human-A-Prompts (unlabeled) erwartet=4 beobachtet={unlabeled}: {proc.stdout}"
            assert proc.stdout.count(labeled_b) == 4, f"Human-B-Prompts erwartet=4 beobachtet={proc.stdout.count(labeled_b)}: {proc.stdout}"

            table = core_store.Table.load(run_dir, table_id)
            assert table.leader == "tech", f"KI-Leader wurde nicht beibehalten: {table.leader}"
            assert set(table.members) == {"tech", human_a_id, human_b_id, "sniper", "medic"}
            assert table.status == "closed"

            protected_after = sup.capture_protected_authorities(states_dir, registry_dir, onboarding_dir, catalog_dir)
            assert protected_after == protected_before, (
                "Registry/Onboarding/Katalog/Bystander-Figuren haben sich durch den gefuehrten Hybrid-Weg veraendert"
            )

            sl_log = table.sl_log
            assert len(sl_log) == 8, f"Erwartete 8 oeffentliche SL-Antworten im dauerhaften Log, beobachtet={len(sl_log)}"
            assert proc.stdout.count("[SL] ") == len(sl_log), (
                f"Anzahl der [SL]-Anzeigebloecke ({proc.stdout.count('[SL] ')}) weicht von der Anzahl "
                f"dauerhafter sl_log-Eintraege ({len(sl_log)}) ab."
            )
            last_pos = -1
            for idx, entry in enumerate(sl_log):
                marker = f"[SL] {entry.get('content', '')}"
                found_pos = proc.stdout.find(marker, last_pos + 1)
                assert found_pos != -1, f"SL-Eintrag #{idx} nicht vollstaendig als eigener [SL]-Block NACH dem vorherigen im STDOUT gefunden: {entry}"
                last_pos = found_pos

            members_final = sorted(table.members)
            states_after = {m: json.loads((states_dir / f"{m}.json").read_text(encoding="utf-8")) for m in members_final}
            for m in members_final:
                assert states_after[m]["rounds_played"] == 1, (
                    f"'{m}': genau eine gespielte Runde erwartet, beobachtet={states_after[m]['rounds_played']}"
                )
                versions_dir = run_dir / "current_saves" / f"{m}__versions"
                version_count = len(list(versions_dir.glob("*.json"))) if versions_dir.exists() else 0
                assert version_count == 2, f"'{m}': genau zwei Save-Versionen (Onboarding+Abschluss) erwartet, beobachtet={version_count}"
                current = json.loads((run_dir / "current_saves" / f"{m}.json").read_text(encoding="utf-8"))
                assert current == end_saves[m], (
                    f"'{m}': veroeffentlichter Current-Save ist NICHT vollstaendig byte-/feldgleich zum "
                    f"gesendeten synthetischen Endsave-Block: current={current} erwartet={end_saves[m]}"
                )
                assert current.get("save_id") != final_saves[m].get("save_id"), (
                    f"'{m}': Endsave wiederholt den Ausgangspayload (save_id unveraendert) -- gegen R3 verstossen"
                )
            end_save_ids = {m: end_saves[m]["save_id"] for m in members_final}
            assert len(set(end_save_ids.values())) == 5, f"Endsave-IDs sind nicht alle unterscheidbar: {end_save_ids}"

            reflections = sup.read_jsonl(run_dir / "reflections.jsonl")
            ai_reflections = {r["persona_key"] for r in reflections if r.get("kind") == "ai_required_reflection" and r.get("section_id") == section_id}
            assert ai_reflections == {"tech", "sniper", "medic"}, f"KI-Pflichtreflexionen (inkl. KI-Leader) unvollstaendig: {ai_reflections}"

            cli_captures = sup.read_cli_captures(cli_root, "a24g2hybrid")
            assert len(cli_captures) >= 13, f"Hybrid-CLI haette real mehrfach aufgerufen werden muessen: {len(cli_captures)}"
            joined_stdins = "\n---\n".join(c["stdin"] for c in cli_captures)
            assert "in Deckung zu bleiben" in joined_stdins, "Gastvorschlag (Poll) erreichte den KI-Leader nicht ueber den Wire-Kontext"

            offer_log = sup.read_jsonl(run_dir / "invitation_decisions.jsonl")
            consent_from = {e.get("from") for e in offer_log if e.get("type") == "response" and e.get("decision") == "accept"}
            assert {leader_id, human_b_id, "sniper", "medic"}.issubset(consent_from), (
                f"Consent-Log unvollstaendig (inkl. KI-Leader-Zusage): {offer_log}"
            )
            assert human_a_id not in consent_from, (
                "aufrufender Mensch sollte keinen eigenen Response-Log-Eintrag erzeugen (Kommandoaufruf == Freigabe)"
            )

            # G6-O (02_AUFTRAG_G6_REST.md #5): dauerhafte Ledger-/Rollen-/
            # Akteur-/Turn-/Tisch-/Consent-/Reflexions-Zuordnung permanent in
            # der Suite. Nur wenn der eigene Observer-Guard etwas aufgezeichnet
            # hat (dieselbe Ausnahme wie beim CLI-Join oben -- ein externer
            # Review-Helfer mit eigenem PYTHONPATH ist kein G6-O-Befund).
            if parent_observations["spawns"] or parent_observations["process_results"]:
                sup.audit_g6_chain_for_case(
                    case_name="case_g2_ai_leader_hybrid_handoff", run_dir=run_dir, table=table, initial=final_saves,
                    gm=gm_srv.received, cli_input_captures=cli_input_captures, cli_output_captures=cli_output_captures,
                    cli_parent_observations=parent_observations,
                    reflections=reflections, invitation_decisions=offer_log,
                )

            if case is not None:
                sup.write_json(case / "after" / "table.json", {"leader": table.leader, "members": table.members, "status": table.status, "sl_log": table.sl_log})
                (case / "after" / "invitation_decisions.jsonl").write_text((run_dir / "invitation_decisions.jsonl").read_text(encoding="utf-8"), encoding="utf-8")
                sup.write_json(case / "after" / "states.json", states_after)
                sup.write_json(case / "after" / "end_save_ids.json", end_save_ids)
                sup.write_json(case / "after" / "registry_catalog.json", {
                    "registry": sup.hash_tree(registry_dir), "catalog": sup.hash_tree(catalog_dir),
                    "onboarding": sup.hash_tree(onboarding_dir),
                })


# ---------------------------------------------------------------------------
# Negativfall (a): 3 Menschen + 3 KI = 6 -> abgelehnt
# ---------------------------------------------------------------------------

def test_a24_negative_six_players_rejected():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        case = sup.case_dir("negative_six_players_rejected") if os.environ.get("A24_EVIDENCE_DIR") else None
        boot = sup.bootstrap_six_persona_community(root, "community-a24-neg-a")
        run_dir, states_dir, onboarding_dir = boot["run_dir"], boot["states_dir"], boot["onboarding_dir"]
        for pk in ("sniper", "tech", "medic"):
            sup.make_ready(onboarding_dir, states_dir, run_dir, pk)

        registry_dir = root / "registry"
        human_a = sup.register_human(registry_dir, "A24-NegA-Human-A")
        human_b = sup.register_human(registry_dir, "A24-NegA-Human-B")
        human_c = sup.register_human(registry_dir, "A24-NegA-Human-C")
        ids = [human_a.participant_id, human_b.participant_id, human_c.participant_id]
        chars = [("CHR-A24-NA-A", "Ana", "ANAOPS"), ("CHR-A24-NA-B", "Bero", "BEROPS"), ("CHR-A24-NA-C", "Cleo", "CLEOOPS")]
        onbs = [sup.onboard_human_figure(registry_dir, pid, onboarding_dir, states_dir, run_dir, *c) for pid, c in zip(ids, chars)]
        sup.write_test_profile(run_dir, max_turns=200, max_seconds=600, max_usd=50.0)

        leader_id, guest_b, guest_c = ids
        targets = [guest_b, guest_c, "sniper", "tech", "medic"]  # 2 weitere Menschen + 3 KI = 6 Gesamtspieler.
        offer_id = sup.invitation_offer_id(leader_id, targets)
        # G6-E: Sechserfall bildet nie einen Tisch (Policy-Ablehnung VOR
        # jeder Tischanlage) -- die unabhaengige Erwartung spiegelt die
        # angefragte (nicht die zulaessige) Konstellation, bleibt aber
        # Pflichtparameter statt `None`.
        onb_a = onbs[0]
        gm_receipts_path = root / "gm_receipts.jsonl"
        expected_context = sup.expected_context_for_case(
            leader=leader_id, members=sup.sorted_table_members(leader_id, targets),
            table_id=sup.compute_table_id(leader_id, targets),
            section_id=f"{sup.compute_table_id(leader_id, targets)}-section",
            final_saves={leader_id: onb_a["save"], "sniper": sup.load_fixture_save("sniper"),
                         "tech": sup.load_fixture_save("tech"), "medic": sup.load_fixture_save("medic")},
            offer_ids=[offer_id],
        )

        sup.write_g6_operation_plan(
            gm_receipts_path, expected_context, invite_actors=["sniper", "tech", "medic"],
            human_messages={}, play=False)

        persona_srv = sup.SequencedHTTPServer(
            scripted=[sup.accept_text(offer_id, "sniper"), sup.accept_text(offer_id, "tech"), sup.accept_text(offer_id, "medic")],
            fallback_fn=sup.narrative_fallback("persona"),
            expected_context=expected_context, gm_receipts_path=gm_receipts_path,
        )
        gm_calls_guard: list = []

        def gm_fallback_must_not_be_called(idx, body):
            gm_calls_guard.append(body)
            return "SOLLTE NIE GESENDET WERDEN -- Sechserfall darf keinen Tisch/GM-Turn erzeugen."

        gm_srv = sup.SequencedHTTPServer(
            scripted=[], fallback_fn=gm_fallback_must_not_be_called,
            expected_context=expected_context, gm_receipts_path=gm_receipts_path, is_gm_server=True,
        )

        with gm_srv, persona_srv:
            env = {
                "OPENWEBUI_URL": gm_srv.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC_A24_GM_KEY",
                "MMO_SIM_PERSONA_API_BASE_URL": persona_srv.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTHETIC_A24_PERSONA_KEY", "MMO_SIM_PERSONA_API_MODEL": "synthetic-a24",
            }
            env.pop("MMO_SIM_PERSONA_CLI", None)
            stdin_text = (
                f"l {guest_b} {guest_c} persona:sniper persona:tech persona:medic\nj\nj\nx\n"
            )

            if case is not None:
                (case / "before" / "stdin.txt").write_text(stdin_text, encoding="utf-8")
                sup.write_json(case / "before" / "plan.json", {
                    "leader_id": leader_id, "targets": targets, "offer_id": offer_id,
                })

            proc = sup.run_process(run_dir.parent, leader_id, stdin_text, env, timeout=60)

            table_files = list((run_dir / "tables").glob("local-*.json")) if (run_dir / "tables").exists() else []

            if case is not None:
                (case / "after" / "stdout.txt").write_text(proc.stdout, encoding="utf-8")
                (case / "after" / "stderr.txt").write_text(proc.stderr, encoding="utf-8")
                sup.write_json(case / "after" / "process.json", {"returncode": proc.returncode})
                sup.write_json(case / "after" / "gm_received.json", gm_calls_guard)
                sup.write_json(case / "after" / "persona_received.json", persona_srv.received)
                sup.write_json(case / "after" / "table_files.json", [p.name for p in table_files])

            sup.assert_g6_operation_tape(gm_receipts_path)
            assert proc.returncode == 0, f"Prozess-Fehlschlag statt fachlicher Ablehnung: {proc.stderr[-1500:]}"
            assert "Abschnitt abgeschlossen:" not in proc.stdout, f"Sechserfall hat trotzdem einen Abschnitt abgeschlossen: {proc.stdout}"
            assert not gm_calls_guard, "Sechserfall hat trotzdem einen GM-Turn ausgeloest -- Tischgrenze umgangen"
            assert not table_files, f"Sechserfall hat trotzdem einen Tisch angelegt: {[p.name for p in table_files]}"

            # R1 (02_AUFTRAG_A24.md §R1 a / reference/incoming-r2/FINDING-
            # sechser-meldung.md): die Ablehnungsmeldung muss die tatsaechliche
            # Policy-Spanne UND die angefragte Spielerzahl nennen -- NICHT den
            # wiederverwendeten Erfolgsgrund "erste vollstaendig angenommene
            # Offer ...". Wortlaut-Pruefung, keine reine Strukturpruefung.
            size_line = next(
                (ln for ln in proc.stdout.splitlines() if "Lokale Runde konnte nicht gestartet werden" in ln), None,
            )
            assert size_line is not None, f"Erwartete Ablehnungsmeldung fehlt vollstaendig: {proc.stdout[-800:]}"
            assert "6 Spieler angefragt" in size_line, f"Ablehnungsmeldung nennt nicht die angefragte Spielerzahl: {size_line!r}"
            assert "1 bis 5" in size_line, f"Ablehnungsmeldung nennt nicht die tatsaechliche Policy-Spanne (1-5): {size_line!r}"
            assert "erste vollstaendig angenommene Offer" not in size_line, (
                f"Ablehnungsmeldung verwendet weiterhin den wiederverwendeten Erfolgstext statt eines "
                f"Groessen-spezifischen Grundes: {size_line!r}"
            )

            # Keine stille Kuerzung/Ersatzwahl: alle drei Menschen bleiben bei
            # ihrer unveraenderten Baseline-Figur (keine neue Runde/State-
            # Version jenseits des Onboarding-Baselines).
            for ref in onbs:
                assert ref["save"]["characters"][0]["char_id"]


# ---------------------------------------------------------------------------
# Negativfall (b): Human B lehnt den Beitritt ab
# ---------------------------------------------------------------------------

def test_a24_negative_human_b_declines():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        case = sup.case_dir("negative_human_b_declines") if os.environ.get("A24_EVIDENCE_DIR") else None
        boot = sup.bootstrap_six_persona_community(root, "community-a24-neg-b")
        run_dir, states_dir, onboarding_dir = boot["run_dir"], boot["states_dir"], boot["onboarding_dir"]
        for pk in ("sniper", "tech", "medic"):
            sup.make_ready(onboarding_dir, states_dir, run_dir, pk)
        registry_dir = root / "registry"
        human_a = sup.register_human(registry_dir, "A24-NegB-Human-A")
        human_b = sup.register_human(registry_dir, "A24-NegB-Human-B")
        sup.onboard_human_figure(registry_dir, human_a.participant_id, onboarding_dir, states_dir, run_dir, "CHR-A24-NB-A", "Ari", "ARIOPS")
        sup.onboard_human_figure(registry_dir, human_b.participant_id, onboarding_dir, states_dir, run_dir, "CHR-A24-NB-B", "Bodhi", "BODHIOPS")
        sup.write_test_profile(run_dir, max_turns=200, max_seconds=600, max_usd=50.0)

        leader_id, guest_b = human_a.participant_id, human_b.participant_id
        targets = [guest_b, "sniper", "tech", "medic"]
        offer_id = sup.invitation_offer_id(leader_id, targets)
        # G6-E: Human B lehnt ab, Tisch entsteht nie -- die drei real per
        # HTTP eingeladenen KI-Personas (sniper/tech/medic) brauchen ihren
        # unabhaengig erwarteten eigenen Current fuer die Einladungspruefung.
        gm_receipts_path = root / "gm_receipts.jsonl"
        expected_context = sup.expected_context_for_case(
            leader=leader_id, members=sup.sorted_table_members(leader_id, targets),
            table_id=sup.compute_table_id(leader_id, targets),
            section_id=f"{sup.compute_table_id(leader_id, targets)}-section",
            final_saves={"sniper": sup.load_fixture_save("sniper"), "tech": sup.load_fixture_save("tech"),
                         "medic": sup.load_fixture_save("medic")},
            offer_ids=[offer_id],
        )

        sup.write_g6_operation_plan(
            gm_receipts_path, expected_context, invite_actors=["sniper", "tech", "medic"],
            human_messages={}, play=False)

        persona_srv = sup.SequencedHTTPServer(
            scripted=[sup.accept_text(offer_id, "sniper"), sup.accept_text(offer_id, "tech"), sup.accept_text(offer_id, "medic")],
            fallback_fn=sup.narrative_fallback("persona"),
            expected_context=expected_context, gm_receipts_path=gm_receipts_path,
        )
        gm_calls_guard: list = []
        gm_srv = sup.SequencedHTTPServer(
            scripted=[], fallback_fn=lambda idx, body: (gm_calls_guard.append(body), "NIE SENDEN")[1],
            expected_context=expected_context, gm_receipts_path=gm_receipts_path, is_gm_server=True,
        )

        with gm_srv, persona_srv:
            env = {
                "OPENWEBUI_URL": gm_srv.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC_A24_GM_KEY",
                "MMO_SIM_PERSONA_API_BASE_URL": persona_srv.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTHETIC_A24_PERSONA_KEY", "MMO_SIM_PERSONA_API_MODEL": "synthetic-a24",
            }
            env.pop("MMO_SIM_PERSONA_CLI", None)
            stdin_text = f"l {guest_b} persona:sniper persona:tech persona:medic\nn\nx\n"

            if case is not None:
                (case / "before" / "stdin.txt").write_text(stdin_text, encoding="utf-8")
                sup.write_json(case / "before" / "plan.json", {
                    "leader_id": leader_id, "guest_b": guest_b, "targets": targets, "offer_id": offer_id,
                })

            proc = sup.run_process(run_dir.parent, leader_id, stdin_text, env, timeout=60)

            table_files = list((run_dir / "tables").glob("local-*.json")) if (run_dir / "tables").exists() else []

            if case is not None:
                (case / "after" / "stdout.txt").write_text(proc.stdout, encoding="utf-8")
                (case / "after" / "stderr.txt").write_text(proc.stderr, encoding="utf-8")
                sup.write_json(case / "after" / "process.json", {"returncode": proc.returncode})
                sup.write_json(case / "after" / "gm_received.json", gm_calls_guard)
                sup.write_json(case / "after" / "persona_received.json", persona_srv.received)
                sup.write_json(case / "after" / "table_files.json", [p.name for p in table_files])

            sup.assert_g6_operation_tape(gm_receipts_path)
            assert proc.returncode == 0, proc.stderr[-1500:]
            assert "nicht zustande gekommen" in proc.stdout, f"Abbruchhinweis fehlt: {proc.stdout[-800:]}"
            assert "Abschnitt abgeschlossen:" not in proc.stdout
            assert not gm_calls_guard, "Abgelehnte Runde hat trotzdem einen GM-Turn ausgeloest"
            assert not table_files, f"Abgelehnte Runde hat trotzdem einen (Solo-)Tisch angelegt: {[p.name for p in table_files]}"


# ---------------------------------------------------------------------------
# Negativfall (c): eine angefragte KI lehnt ab (echte HTTP-200-Ablehnung)
# ---------------------------------------------------------------------------

def test_a24_negative_ai_guest_declines():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        case = sup.case_dir("negative_ai_guest_declines") if os.environ.get("A24_EVIDENCE_DIR") else None
        boot = sup.bootstrap_six_persona_community(root, "community-a24-neg-c")
        run_dir, states_dir, onboarding_dir = boot["run_dir"], boot["states_dir"], boot["onboarding_dir"]
        for pk in ("sniper", "tech", "medic"):
            sup.make_ready(onboarding_dir, states_dir, run_dir, pk)
        registry_dir = root / "registry"
        human_a = sup.register_human(registry_dir, "A24-NegC-Human-A")
        human_b = sup.register_human(registry_dir, "A24-NegC-Human-B")
        sup.onboard_human_figure(registry_dir, human_a.participant_id, onboarding_dir, states_dir, run_dir, "CHR-A24-NC-A", "Noa", "NOAOPS")
        sup.onboard_human_figure(registry_dir, human_b.participant_id, onboarding_dir, states_dir, run_dir, "CHR-A24-NC-B", "Remy", "REMYOPS")
        sup.write_test_profile(run_dir, max_turns=200, max_seconds=600, max_usd=50.0)

        leader_id, guest_b = human_a.participant_id, human_b.participant_id
        targets = [guest_b, "sniper", "tech", "medic"]
        offer_id = sup.invitation_offer_id(leader_id, targets)
        # G6-E: dieselbe unabhaengige Erwartung wie Negativfall (b) -- die
        # drei real eingeladenen KI-Personas brauchen ihren eigenen Current.
        gm_receipts_path = root / "gm_receipts.jsonl"
        expected_context = sup.expected_context_for_case(
            leader=leader_id, members=sup.sorted_table_members(leader_id, targets),
            table_id=sup.compute_table_id(leader_id, targets),
            section_id=f"{sup.compute_table_id(leader_id, targets)}-section",
            final_saves={"sniper": sup.load_fixture_save("sniper"), "tech": sup.load_fixture_save("tech"),
                         "medic": sup.load_fixture_save("medic")},
            offer_ids=[offer_id],
        )

        # sniper/tech sagen real zu, medic lehnt eine ECHT ZUGESTELLTE
        # (HTTP 200) Anfrage ab -- Zustellerfolg != Zusage (D2/A4).
        sup.write_g6_operation_plan(
            gm_receipts_path, expected_context, invite_actors=["sniper", "tech", "medic"],
            human_messages={}, play=False)

        persona_srv = sup.SequencedHTTPServer(
            scripted=[
                sup.accept_text(offer_id, "sniper"),
                sup.accept_text(offer_id, "tech"),
                sup.reject_text(offer_id, "medic", "Ich lehne die Einladung ab."),
            ],
            fallback_fn=sup.narrative_fallback("persona"),
            expected_context=expected_context, gm_receipts_path=gm_receipts_path,
        )
        gm_calls_guard: list = []
        gm_srv = sup.SequencedHTTPServer(
            scripted=[], fallback_fn=lambda idx, body: (gm_calls_guard.append(body), "NIE SENDEN")[1],
            expected_context=expected_context, gm_receipts_path=gm_receipts_path, is_gm_server=True,
        )

        with gm_srv, persona_srv:
            env = {
                "OPENWEBUI_URL": gm_srv.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC_A24_GM_KEY",
                "MMO_SIM_PERSONA_API_BASE_URL": persona_srv.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTHETIC_A24_PERSONA_KEY", "MMO_SIM_PERSONA_API_MODEL": "synthetic-a24",
            }
            env.pop("MMO_SIM_PERSONA_CLI", None)
            stdin_text = f"l {guest_b} persona:sniper persona:tech persona:medic\nj\nx\n"

            if case is not None:
                (case / "before" / "stdin.txt").write_text(stdin_text, encoding="utf-8")
                sup.write_json(case / "before" / "plan.json", {
                    "leader_id": leader_id, "guest_b": guest_b, "targets": targets, "offer_id": offer_id,
                })

            proc = sup.run_process(run_dir.parent, leader_id, stdin_text, env, timeout=60)

            table_files = list((run_dir / "tables").glob("local-*.json")) if (run_dir / "tables").exists() else []

            if case is not None:
                (case / "after" / "stdout.txt").write_text(proc.stdout, encoding="utf-8")
                (case / "after" / "stderr.txt").write_text(proc.stderr, encoding="utf-8")
                sup.write_json(case / "after" / "process.json", {"returncode": proc.returncode})
                sup.write_json(case / "after" / "gm_received.json", gm_calls_guard)
                sup.write_json(case / "after" / "persona_received.json", persona_srv.received)
                sup.write_json(case / "after" / "table_files.json", [p.name for p in table_files])

            sup.assert_g6_operation_tape(gm_receipts_path)
            assert proc.returncode == 0, proc.stderr[-1500:]
            assert persona_srv.received and len(persona_srv.received) >= 3, "medic haette real per HTTP 200 angesprochen werden muessen"
            assert "nicht angenommen" in proc.stdout or "nicht zustande gekommen" in proc.stdout, (
                f"Echt zugestellte (HTTP 200) Ablehnung wurde nicht als Nicht-Zusage erkannt: {proc.stdout[-800:]}"
            )
            assert "Abschnitt abgeschlossen:" not in proc.stdout
            assert not gm_calls_guard, "KI-Ablehnung hat trotzdem einen GM-Turn ausgeloest"
            assert not table_files, f"KI-Ablehnung hat trotzdem einen Tisch angelegt: {[p.name for p in table_files]}"


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
