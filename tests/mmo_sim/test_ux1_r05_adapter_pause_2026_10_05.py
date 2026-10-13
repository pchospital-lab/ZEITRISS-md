#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_r05_adapter_pause_2026_10_05.py — W13/R05 (UX09,
CASE-REVIEW.json "2+3 tischbereit/accept/reject/pause nicht komplett
geliefert"): die fehlende dritte Antwortform fuer den 2-Menschen+3-KI-
Consentpfad.

`test_a24_local_two_humans_2026_10_01.py` deckt bereits "tischbereit"
(`test_a24_case1_human_leader_api_full_journey`, exakt 2 Menschen + 3 KI)
und "abgelehnt" (`test_a24_negative_human_b_declines`,
`test_a24_negative_ai_guest_declines`) real ab. "Pausiert" fehlte: der
zusaetzliche menschliche Gast am Rundenbeitritt konnte `/pause` zwar
EINGEBEN, aber `mmo_sim/ui/tui.py` las diesen EINEN Prompt (anders als
praktisch jeder andere Menschprompt in der Datei) bisher ueber ein rohes
`_readline` statt des zentralen Kontrollvertrags (`_readline_with_controls`)
-- `/pause` landete dadurch ununterscheidbar in derselben 'invalid'-Schublade
wie Kauderwelsch, nie als eigene, korrekt benannte 'paused'-Entscheidung im
Einladungs-Log. Kein neuer Produktweg: derselbe Kontrollvertrag, den jeder
andere Prompt in dieser Datei bereits benutzt (`_CONTROL_TOKENS`); 'j'/'n'
bleiben fuer JEDEN bestehenden Aufrufer bytegleich (s. volle 9/9 weiterhin
gruene `test_a24_local_two_humans_2026_10_01.py`-Suite).

Reines Re-Use bestehender Fixture-Bausteine aus `_a24_local_support.py`
(derselbe reale Subprozess-Dispatch `scripts/mmo_sim.py --participant ...`,
dieselbe Sechs-Personas-Community/Registry/Onboarding-Bootstrap wie die
Nachbartests) -- kein neues Fake, keine neue Engine."""
from __future__ import annotations

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

import _a24_local_support as sup  # noqa: E402


def test_a24_r05_human_b_pauses_consent_distinguishable_from_reject():
    """2 Menschen + 3 KI (dieselbe Groesse wie UX09/Fall 1): Human B
    antwortet am Rundenbeitritt mit '/pause' statt 'n'. Erwartung:
    (1) kein Tisch, kein GM-Turn (derselbe Abbruch-Guard wie bei 'n' --
    ein pausierter zustimmungspflichtiger Gast ist weiterhin keine Zusage),
    (2) die Ablehnungs-/Pausemeldung nennt 'pausiert' + das Steuerwort
    (nicht denselben Text wie eine inhaltliche Ablehnung), (3) das
    Einladungs-Log fuehrt die Antwort als eigene 'decision':'paused'
    (nicht 'invalid'/'reject') -- real nachvollziehbar, nicht nur behauptet."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        case = sup.case_dir("r05_human_b_pauses_consent") if os.environ.get("A24_EVIDENCE_DIR") else None
        boot = sup.bootstrap_six_persona_community(root, "community-a24-r05-pause")
        run_dir, states_dir, onboarding_dir = boot["run_dir"], boot["states_dir"], boot["onboarding_dir"]
        for pk in ("sniper", "tech", "medic"):
            sup.make_ready(onboarding_dir, states_dir, run_dir, pk)
        registry_dir = root / "registry"
        human_a = sup.register_human(registry_dir, "A24-R05Pause-Human-A")
        human_b = sup.register_human(registry_dir, "A24-R05Pause-Human-B")
        sup.onboard_human_figure(registry_dir, human_a.participant_id, onboarding_dir, states_dir, run_dir, "CHR-A24-R05P-A", "Asa", "ASAOPS")
        sup.onboard_human_figure(registry_dir, human_b.participant_id, onboarding_dir, states_dir, run_dir, "CHR-A24-R05P-B", "Bix", "BIXOPS")
        sup.write_test_profile(run_dir, max_turns=200, max_seconds=600, max_usd=50.0)

        leader_id, guest_b = human_a.participant_id, human_b.participant_id
        targets = [guest_b, "sniper", "tech", "medic"]
        offer_id = sup.invitation_offer_id(leader_id, targets)
        gm_receipts_path = root / "gm_receipts.jsonl"
        expected_context = sup.expected_context_for_case(
            leader=leader_id, members=sup.sorted_table_members(leader_id, targets),
            table_id=sup.compute_table_id(leader_id, targets),
            section_id=f"{sup.compute_table_id(leader_id, targets)}-section",
            final_saves={"sniper": sup.load_fixture_save("sniper"), "tech": sup.load_fixture_save("tech"),
                         "medic": sup.load_fixture_save("medic")},
            offer_ids=[offer_id],
        )
        # Dieselbe G6-Operation-Plan-Vorbereitung wie die bestehenden
        # Negativfaelle -- die drei real per HTTP eingeladenen KI-Personas
        # brauchen ihren unabhaengig erwarteten eigenen Current, obwohl der
        # Tisch wegen Human Bs Pause nie entsteht.
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
            # '/pause' statt 'n' an genau demselben Prompt wie
            # `test_a24_negative_human_b_declines` -- einzige Abweichung.
            stdin_text = f"l {guest_b} persona:sniper persona:tech persona:medic\n/pause\nx\n"

            if case is not None:
                (case / "before" / "stdin.txt").write_text(stdin_text, encoding="utf-8")
                sup.write_json(case / "before" / "plan.json", {
                    "leader_id": leader_id, "guest_b": guest_b, "targets": targets, "offer_id": offer_id,
                })

            proc = sup.run_process(run_dir.parent, leader_id, stdin_text, env, timeout=60)

            table_files = list((run_dir / "tables").glob("local-*.json")) if (run_dir / "tables").exists() else []
            # Identischer Dateiname/-pfad wie `core.lobby_service.
            # append_offer_log_record` (`INVITATION_LOG_FILENAME`,
            # `_append_invitation_log`s einziger Schreibweg) -- reine
            # Lesesonde, kein neuer Store.
            invitation_log_path = run_dir / "invitation_decisions.jsonl"
            invitation_log = sup.read_jsonl(invitation_log_path) if invitation_log_path.exists() else []

            if case is not None:
                (case / "after" / "stdout.txt").write_text(proc.stdout, encoding="utf-8")
                (case / "after" / "stderr.txt").write_text(proc.stderr, encoding="utf-8")
                sup.write_json(case / "after" / "process.json", {"returncode": proc.returncode})
                sup.write_json(case / "after" / "gm_received.json", gm_calls_guard)
                sup.write_json(case / "after" / "persona_received.json", persona_srv.received)
                sup.write_json(case / "after" / "table_files.json", [p.name for p in table_files])
                sup.write_json(case / "after" / "invitation_log.json", invitation_log)

            assert proc.returncode == 0, proc.stderr[-1500:]
            assert "pausiert" in proc.stdout, f"'/pause' wurde nicht als eigene Pause-Antwort erkannt: {proc.stdout[-800:]}"
            assert "nicht zugestimmt" not in proc.stdout, (
                "Pause darf nicht als dieselbe inhaltliche Ablehnungsmeldung wie eine echte "
                f"Nein-Antwort erscheinen: {proc.stdout[-800:]}"
            )
            assert "Abschnitt abgeschlossen:" not in proc.stdout
            assert not gm_calls_guard, "Pausierter Gast hat trotzdem einen GM-Turn ausgeloest"
            assert not table_files, f"Pausierter Gast hat trotzdem einen Tisch angelegt: {[p.name for p in table_files]}"
            paused_entries = [e for e in (invitation_log or []) if e.get("from") == guest_b and e.get("type") == "response"]
            assert paused_entries and paused_entries[-1].get("decision") == "paused", (
                f"Einladungs-Log fuehrt Human Bs Pause nicht als eigene 'paused'-Entscheidung: {paused_entries}"
            )


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
