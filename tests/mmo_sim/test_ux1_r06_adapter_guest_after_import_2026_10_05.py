#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_r06_adapter_guest_after_import_2026_10_05.py —
W14/R06 (UX14, CASE-REVIEW.json "kompletter weiterer Gastzug am
Bedienzugang fehlt"; reference/r2/acceptance/RESULTS.json UX14
`coverage_note`: "Vierte Variante (weiterer regulaerer Gastzug) live nicht
erreicht, da der Fake-GM-Tisch nach dem ersten Gastzug automatisch
abschliesst."): die fehlende vierte Textzweck-Variante "Gast regulaer ->
Tisch" NACH einem bereits erfolgten Gast-Erstimport.

Befund (keine Produktaenderung noetig, reiner Testluecken-Befund): der
Produktcode (`mmo_sim/ui/tui.py:_HumanDriver._purpose_label`,
`core/runtime.py:SectionRuntime.run_section` — `poll_guests_and_
consolidate()`) unterscheidet bereits strukturell drei Spielzug-Faelle
(Leader->SL, Gast-Erstimport->SL-ueber-Leader, JEDER WEITERE Gastbeitrag
->Tischabsprache/`post_table_message`, NICHT SL) -- das bisherige
Manual-Offline-Harness-Fixture (`complete_after=1`) und die vorhandenen
A24-Subprozess-Fixtures schliessen den synthetischen Tisch aber
typischerweise VOR der zweiten "ongoing_round"-Iteration, in der
`poll_guests_and_consolidate()` ueberhaupt zum ersten Mal einen Gast nach
seinem Erstimport erneut befragt. Dieser Test haelt den Fake-GM gezielt
(`_NeverCompletingGm`, bereits vorhandener Baustein aus
`test_ux1_g04_purpose_stand_verlauf_2026_10_05.py`) ueber den Erstimport
HINAUS offen, bis die zweite, "regulaere" Gastrunde tatsaechlich
durchlaeuft, und bindet den Nachweis an drei unabhaengige Beobachtungen:
(1) die Empfaenger-/Zweckzeile wechselt von "Erstbeitrag" auf
"Tischabsprache", (2) der Beitrag landet NUR in `table.table_messages`
(`post_table_message`), NICHT ein zweites Mal im `sl_log` mit
`origin_persona_key=<Gast>`, (3) kein zweiter Save-/Importschreibzugriff
(`save_payload`) fuer denselben Gast.

Reines Re-Use bestehender Fixture-Bausteine (`_a24_local_support.py`
Registrierung/Onboarding, `_NeverCompletingGm`/`_scripted` aus der
vorhandenen G04-Testdatei) -- kein neues Fake, keine neue Engine, keine
Core-/Produktaenderung."""
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

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402
import _a24_local_support as sup  # noqa: E402


def _scripted(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


class _NeverCompletingGm:
    """Identischer Baustein wie
    `test_ux1_g04_purpose_stand_verlauf_2026_10_05.py::_NeverCompletingGm`
    (kein neuer Fake-Mechanismus): liefert nie einen Abschluss-Marker, die
    Runde bleibt offen, bis genug Zuege fuer die zweite "ongoing_round"
    (Gast-Poll NACH Erstimport) tatsaechlich stattgefunden haben."""

    def __init__(self):
        self.calls = 0

    def turn(self, turn_idx, text, **kw):
        self.calls += 1
        return {"content": f"SL-Antwort #{turn_idx} (kein Abschluss hier)."}


def test_guest_second_turn_after_import_routes_to_table_not_sl():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir, onboarding_dir, catalog_dir = (
            d / "run", d / "states", d / "onboarding", d / "catalog",
        )
        write_test_profile(run_dir)
        registry_dir = run_dir.parent / "registry"
        leader = sup.register_human(registry_dir, "Leader")
        guest = sup.register_human(registry_dir, "Guest")
        leader_id, guest_id = leader.participant_id, guest.participant_id
        sup.onboard_human_figure(
            registry_dir, leader_id, onboarding_dir, states_dir, run_dir, "CHR-LEAD", "Lea", "LEADOPS",
        )
        sup.onboard_human_figure(
            registry_dir, guest_id, onboarding_dir, states_dir, run_dir, "CHR-GUEST", "Gus", "GUESTOPS",
        )

        printed: list[str] = []
        gm = _NeverCompletingGm()
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=leader_id,
            input_fn=_scripted([
                "j",                                              # Gast bestaetigt den Beitritt.
                "Leader-Zug 1 (Anker).",                           # Leader -> SL (Anker).
                "Gast-Erstimport-Zug.",                            # Gast-Erstimport -> SL ueber Leader.
                "Leader-Zug 2 (ongoing_round=0, noch kein Gastpoll).",
                "Gast regulaerer Zug NACH Erstimport.",            # Gastpoll ongoing_round=1 -> Tischabsprache.
            ]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=sup.SCHEMA,
            gm_transport_factory=lambda: gm, persona_driver_factory=None,
        )
        try:
            session._cmd_local_round([guest_id])
        except EndOfInput:
            pass

        empf_lines = [p for p in printed if p.startswith("Empfaenger:")]
        # Leader-Zuege zeigen "Spielleitung (SL)" (Zug 1, Zug 2 "ongoing_
        # round=0" und der Prompt fuer den -- wegen Eingabeerschoepfung nie
        # abgeschlossenen -- dritten Leaderzug; die Beschriftung wird bereits
        # VOR dem Lesen gedruckt, s. `_HumanDriver.decide`).
        leader_labels = [p for p in empf_lines if p == "Empfaenger: Spielleitung (SL)"]
        assert len(leader_labels) == 3, empf_lines
        # Gast-Erstimport zeigt die Erstbeitrag-Beschriftung, genau einmal.
        import_labels = [p for p in empf_lines if p.startswith("Empfaenger: ueber Leader an Spielleitung")]
        assert len(import_labels) == 1, empf_lines
        # Kernassertion UX14 (vierte Variante): der ZWEITE Gastbeitrag NACH
        # dem Erstimport zeigt die Tischabsprache-Beschriftung, NICHT erneut
        # die Erstimport-/SL-Beschriftung -- und erscheint NACH dem
        # Erstimport-Label (echte zeitliche Reihenfolge, nicht nur Anzahl).
        table_labels = [p for p in empf_lines if p.startswith("Empfaenger: Tischabsprache")]
        assert len(table_labels) == 1, empf_lines
        assert empf_lines.index(import_labels[0]) < empf_lines.index(table_labels[0]), empf_lines

        table_id = f"local-{leader_id}-{guest_id}"
        table_file = run_dir / "tables" / f"{table_id}.json"
        data = json.loads(table_file.read_text(encoding="utf-8"))

        # (1) der zweite Gastbeitrag landet NUR als Tischabsprache, nicht im
        # sl_log (keine zweite SL-Nachricht mit demselben Gast als Ursprung).
        sl_origins = [e.get("origin_persona_key") for e in data.get("sl_log", [])]
        assert sl_origins.count(guest_id) == 1, (
            f"Gast duerfte genau EINMAL (Erstimport) als sl_log-Ursprung erscheinen, nicht erneut "
            f"beim regulaeren Folgezug: {sl_origins}"
        )
        table_messages = data.get("table_messages", [])
        guest_table_msgs = [m for m in table_messages if m.get("from") == guest_id]
        assert len(guest_table_msgs) == 1, table_messages
        assert guest_table_msgs[0]["text"] == "Gast regulaerer Zug NACH Erstimport.", guest_table_msgs

        # (2) der tatsaechlich AN DIE SL GESENDETE Text (`leader_message`,
        # NICHT die Fake-SL-Antwort `content`) enthaelt den zweiten
        # Gastbeitrag NICHT -- kein versteckter Zweitversand an die SL.
        leader_messages_text = " ".join(e.get("leader_message", "") for e in data.get("sl_log", []))
        assert "regulaerer Zug NACH Erstimport" not in leader_messages_text, leader_messages_text

        # (3) kein zweiter Import-/Save-Schreibzugriff fuer denselben Gast:
        # genau EIN eingebetteter v7-Save-Block (der Erstimport) im
        # kompletten an die SL gesendeten Text.
        # W63-Fix (R12-Restreparatur, 02_TESTVERTRAG.md Darstellungsmigration):
        # der eingebettete Save-Block schreibt die Figur schon unter dem
        # kanonischen Feld `id` (striktes Export-Schema, additionalProperties:
        # false auf Figurenebene kennt kein `char_id`), nicht mehr unter
        # `char_id` -- derselbe Identitaetswert ("CHR-GUEST"), nur der
        # Feldname wechselt. Zaehlung/Reihenfolge/Privatheit (table-vs-SL)
        # unveraendert scharf.
        assert leader_messages_text.count('"id": "CHR-GUEST"') == 1, leader_messages_text


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
