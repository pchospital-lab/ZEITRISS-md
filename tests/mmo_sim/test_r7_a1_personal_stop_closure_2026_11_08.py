#!/usr/bin/env python3
"""
tests/mmo_sim/test_r7_a1_personal_stop_closure_2026_11_08.py --
ZR-VOLLENDUNG-OHNE-LAN-NACHZUG-20261108-R7 (01_NACHZUG.md A1, GENERAL-
REVIEW.md §3, 02_ABNAHME.md §A "Persoenlicher Gastkanal"/"Figur/Stand"/
"Naechster Schritt").

Die bisherige Stopmeldung (`_run_table_round`s Stop-Zweig, `decided ==
"stopped"`) kopierte Admission-Gate-Prosa ("VOR der Entscheidung",
"Figurenbindung freigegeben") an Betreiber UND jeden betroffenen Gast,
OHNE die beauftragten Aussagen zu "kein neuer Fortschritt uebernommen" und
"eigener letzter gueltiger Stand bleibt erhalten" (NUR wenn er existiert).

Dieser Test belegt am echten `TuiSession`/`_run_table_round`-Code (derselbe
Fixture-Aufbau wie `test_r6_g03_guest_stop_channel_notice_2026_11_07.py`,
ein Betreiber-Stop bereits VOR Rundenstart echt gewonnen -- GM-Transport
wird NIE erreicht, 0 Modellaufrufe):

1. Die gemeinsame Kernzeile (Abschnitt gestoppt, ENDGUELTIG, kein neuer
   Fortschritt uebernommen) ist WORTGLEICH fuer Betreiber UND Gast (G-R6-03
   bleibt unveraendert gueltig).
2. Ein Gast MIT tatsaechlich registrierter eigener Figur sieht zusaetzlich
   "sein eigener Stand bleibt erhalten" MIT seiner echten Figur/Save --
   KEIN "kein persoenlicher Spielstand".
3. Ein figurfreier Betreiber (kein `chrononaut_id` im Katalog) sieht
   dagegen ehrlich "keine eigene Figur -- kein persoenlicher Spielstand",
   KEIN erfundener Save.
4. Der naechste zulaessige sichtbare Schritt wird je Rolle genannt (Gast:
   Tisch suchen/beitreten; Betreiber: Hauptmenue/Solo-Fortsetzen).
5. Der betroffene Gast sieht SOFORT danach wieder ein gueltiges,
   erreichbares Menue (Reuse von `_reprint_reachable_menu_for_guest`) --
   OHNE zuerst `/stand` tippen zu muessen.

Pure Python, nur `assert`, echter Exitcode, 0 echte GM-/Modellaufrufe."""
from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402
from _section_completion_resume_fixtures import build_two_member_table, make_env  # noqa: E402

from mmo_sim.core import admission as core_admission  # noqa: E402
from mmo_sim.core import table_admission  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402


class _SpyGm:
    def __init__(self):
        self.calls = 0

    def turn(self, *a, **kw):
        self.calls += 1
        raise AssertionError("GM-Transport wurde aufgerufen -- der vorab gewonnene Stop haette ihn verhindern muessen.")


def _scripted_input(values):
    q = list(values)

    def _fn(prompt: str = "") -> str:
        if q:
            return q.pop(0)
        raise EOFError()

    return _fn


def _register_private_figure(onboarding_dir: Path, catalog_dir: Path, participant_id: str, char_id: str) -> dict:
    save = full_v7_save(char_id, name=participant_id, save_id=f"fixture-{participant_id}-001", level=3)
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
    ))
    catalog.bind_for_section(catalog_dir, participant_id, char_id, has_open_section=False)
    return save


def test_personal_stop_closure_distinguishes_figure_free_operator_from_guest_with_save():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        env = make_env(root)
        table_key = "mesa-a1"
        leader_id, guest_id = "leader_pk", "guest_pk"

        lobby, table, ps_store = build_two_member_table(env, table_id="a1-tisch")
        leader_save = full_v7_save("chrono-leader", name="Leader")
        guest_save = full_v7_save("chrono-guest", name="Guest")

        # Nur der GAST hat eine tatsaechlich registrierte eigene Figur
        # (Katalog/Onboarding) -- der Leader/Betreiber bleibt bewusst
        # figurfrei, um genau die beauftragte Unterscheidung zu pruefen.
        guest_onboarding_dir = root / "guest_onboarding"
        guest_catalog_dir = root / "guest_catalog"
        _register_private_figure(guest_onboarding_dir, guest_catalog_dir, guest_id, "chrono-guest")

        table_admission.offer_table(env.run_dir, host_id=leader_id, table_key=table_key)
        table_admission.bind_section(
            env.run_dir, table_key=table_key, host_id=leader_id, section_id=table.table_id,
        )
        table_admission.request_table_stop(
            env.run_dir, table_key=table_key, operator_id=leader_id, table_id=table.table_id,
            reason="R7-A1-Test: Stop vor Rundenstart.",
        )
        decision_before = core_admission.read_table_decision(env.run_dir, table.table_id)
        assert decision_before is not None and decision_before.get("decision") == "stopped", decision_before

        leader_printed: list[str] = []
        guest_printed: list[str] = []
        spy_gm = _SpyGm()

        leader_session = TuiSession(
            onboarding_dir=root / "leader_onboarding", catalog_dir=root / "leader_catalog",
            participant_id=leader_id, input_fn=_scripted_input(["Wir beobachten die Lage."]),
            print_fn=leader_printed.append, run_dir=env.run_dir, states_dir=env.states_dir,
            gm_transport_factory=lambda: spy_gm, host_capable=True,
        )
        guest_session = TuiSession(
            onboarding_dir=guest_onboarding_dir, catalog_dir=guest_catalog_dir,
            participant_id=guest_id, print_fn=guest_printed.append,
            run_dir=env.run_dir, states_dir=env.states_dir, host_capable=False,
        )
        leader_session.register_guest_terminal(guest_id, guest_session)

        leader_session._run_table_round(
            table, lobby, ps_store, leader_id=leader_id, leader_persona_id=None,
            leader_driver=None, active_save=leader_save,
            guest_specs=[(guest_id, False, guest_save, None)],
            guided=False, current_focus_pid=None,
            operator_mode=False, operator_table_key=table_key,
        )

        assert spy_gm.calls == 0, "kein GM-Request haette jemals gesendet werden duerfen."
        operator_out = "\n".join(leader_printed)
        guest_out = "\n".join(guest_printed)

        # (1) Gemeinsame Kernzeile WORTGLEICH -- G-R6-03 bleibt gueltig.
        operator_stop_line = next(ln for ln in leader_printed if "Betreiber-Stop" in ln)
        guest_stop_line = next(ln for ln in guest_printed if "Betreiber-Stop" in ln)
        assert operator_stop_line == guest_stop_line, (operator_stop_line, guest_stop_line)
        assert "ENDGUELTIG" in operator_stop_line, operator_stop_line
        assert "kein neuer Fortschritt" in operator_stop_line, (
            "die Kernzeile haette ausdruecklich 'kein neuer Fortschritt uebernommen' nennen "
            "muessen.", operator_stop_line,
        )
        assert "nicht abgeschlossen" in operator_stop_line, operator_stop_line

        # (1b) 02_ABNAHME.md §A "Persoenlicher Gastkanal": KEINE interne
        # Admission-Gateprosa als Spielererklaerung. Die gemeinsame
        # Spieler-Kernzeile UND der komplette Gastkanal muessen frei von
        # interner Zulassungsgatter-Sprache sein (der technische Grund darf
        # ausschliesslich auf dem abgesetzten Betreiber-Diagnosekanal
        # stehen, s. tui.py-Stopzweig). Diese Zusicherung fehlte in der
        # ersten Fassung -- der Leak blieb dadurch unentdeckt, bis der
        # unabhaengige End-Critic ihn gegen den Auftrag fand.
        assert "Admission-Gate" not in operator_stop_line, (
            "die gemeinsame Spieler-Kernzeile haette KEINE interne "
            "Admission-Gateprosa enthalten duerfen.", operator_stop_line,
        )
        assert "Admission-Gate" not in guest_out, (
            "der Gastkanal (Spielererklaerung) haette KEINE interne "
            "Admission-Gateprosa enthalten duerfen.", guest_out,
        )

        # (2) Gast MIT registrierter Figur: eigener Stand bleibt erhalten,
        # ECHTE Figur/Save genannt, kein "kein persoenlicher Spielstand".
        assert "bleibt erhalten" in guest_out, guest_out
        assert "chrono-guest" in guest_out, (
            "der Gast haette seine ECHTE Figur/seinen Save genannt bekommen muessen "
            "(Resume-Autoritaet, kein erfundener Platzhalter).", guest_out,
        )
        assert "Keine eigene Figur" not in guest_out, (
            "ein Gast MIT tatsaechlich registrierter Figur darf NICHT 'keine eigene Figur' "
            "lesen.", guest_out,
        )

        # (3) Figurfreier Betreiber: ehrlich "keine eigene Figur", KEIN
        # erfundener Save.
        assert "Keine eigene Figur -- kein persoenlicher Spielstand." in operator_out, (
            "ein figurfreier Betreiber haette KEINEN erfundenen Spielstand sehen duerfen.",
            operator_out,
        )
        assert "bleibt erhalten" not in operator_out, (
            "ein figurfreier Betreiber darf keinen (erfundenen) 'bleibt erhalten'-Stand "
            "sehen.", operator_out,
        )

        # (4) Naechster zulaessiger Schritt je Rolle.
        assert "Tisch suchen/beitreten" in guest_out, (
            "der Gast haette den naechsten zulaessigen Schritt (Tisch suchen/beitreten) "
            "genannt bekommen muessen.", guest_out,
        )
        assert "Hauptmenue" in operator_out and (
            "Solo-Fortsetzen" in operator_out or "neues Angebot" in operator_out
        ), operator_out

        # (5) Der Gast sieht SOFORT ein erreichbares Menue -- OHNE zuerst
        # '/stand' tippen zu muessen (kein geheimer vorgeschalteter Befehl).
        assert "ZEITRISS MMO-Sim" in guest_out, (
            "der betroffene Gast haette SOFORT nach der Stopmeldung wieder ein gueltiges, "
            "erreichbares Menue sehen muessen (ohne zuerst '/stand' tippen zu muessen).",
            guest_out,
        )

        # Figurenbindung ist tatsaechlich wieder frei (unveraendertes
        # G-R6-03-Verhalten, Reuse `_finalize_genuine_table_abort`).
        assert lobby.is_locked("chrono-leader") is None
        assert lobby.is_locked("chrono-guest") is None


def test_late_answer_after_stopped_is_still_discarded_no_false_success():
    """Gegenprobe (02_ABNAHME.md §A "Warten"/"Stopkern"): eine Eingabe, die
    NACH dem gewonnenen Stop-Entscheid eintrifft, darf weiterhin KEINEN
    falschen Erfolg/automatischen neuen Call ausloesen -- unveraendertes
    Verhalten, hier am selben R7-A1-Fixture-Aufbau bestaetigt."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        env = make_env(root)
        table_key = "mesa-a1b"
        leader_id, guest_id = "leader_pk", "guest_pk"

        lobby, table, ps_store = build_two_member_table(env, table_id="a1b-tisch")
        leader_save = full_v7_save("chrono-leader", name="Leader")
        guest_save = full_v7_save("chrono-guest", name="Guest")

        table_admission.offer_table(env.run_dir, host_id=leader_id, table_key=table_key)
        table_admission.bind_section(
            env.run_dir, table_key=table_key, host_id=leader_id, section_id=table.table_id,
        )
        table_admission.request_table_stop(
            env.run_dir, table_key=table_key, operator_id=leader_id, table_id=table.table_id,
            reason="R7-A1b-Test: Stop vor Rundenstart.",
        )

        leader_printed: list[str] = []
        guest_printed: list[str] = []
        spy_gm = _SpyGm()

        leader_session = TuiSession(
            onboarding_dir=root / "leader_onboarding", catalog_dir=root / "leader_catalog",
            participant_id=leader_id, input_fn=_scripted_input(["eine verspaetete Antwort"]),
            print_fn=leader_printed.append, run_dir=env.run_dir, states_dir=env.states_dir,
            gm_transport_factory=lambda: spy_gm, host_capable=True,
        )
        guest_session = TuiSession(
            onboarding_dir=root / "guest_onboarding", catalog_dir=root / "guest_catalog",
            participant_id=guest_id, print_fn=guest_printed.append,
            run_dir=env.run_dir, states_dir=env.states_dir, host_capable=False,
        )
        leader_session.register_guest_terminal(guest_id, guest_session)

        leader_session._run_table_round(
            table, lobby, ps_store, leader_id=leader_id, leader_persona_id=None,
            leader_driver=None, active_save=leader_save,
            guest_specs=[(guest_id, False, guest_save, None)],
            guided=False, current_focus_pid=None,
            operator_mode=False, operator_table_key=table_key,
        )
        # Die gescriptete "verspaetete" Eingabe wurde NIE an einen GM-Call
        # oder einen Erfolgszweig gereicht (Spy wirft, falls doch).
        record = table_admission.load_record(env.run_dir, table_key)
        assert record["state"] == table_admission.STATE_CLOSED, record
        assert "ENDGUELTIG" in "\n".join(leader_printed)


def main() -> int:
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
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
