#!/usr/bin/env python3
"""
tests/mmo_sim/test_r6_g03_guest_stop_channel_notice_2026_11_07.py --
ZR-VOLLENDUNG-OHNE-LAN-NACHZUG-20261107-R6 (GENERAL-REVIEW.md §4/G-R6-03,
01_NACHZUG.md Arbeitsblock3, 02_ABNAHME.md §C).

`_run_table_round`s Stop-Block (vorher `tui.py` ~9712-9733) druckte den
endgueltigen Verwurf (`decided == "stopped"`) NUR auf den Betreiberkanal
(`self._print`). Ein betroffener Gast MIT eigenem registriertem Terminal
(`io is not self`, s. `_table_guest_terminals`) bekam diese Meldung NIE --
er blieb unverstanden am Aktionsprompt stehen, ohne zu erfahren, dass der
Abschnitt bereits ENDGUELTIG verworfen wurde.

Dieser Test setzt den tischadressierten Betreiber-Stop ECHT (`table_
admission.request_table_stop`, dieselbe Autoritaet wie O2/O3) VOR dem
Rundenstart -- der gemeinsame atomare Entscheid-Slot ist dadurch bereits
auf "stopped" gewonnen, BEVOR `_run_table_round` auch nur den ersten
Leader-Zug anfordert. Das bestehende Admission-Gate (`core/runtime.py:
_check_gate`, Pruefpunkt 2 "zwischen Persona-Request und GM-Request")
blockt dadurch GENAU NACH dem Leader-Erstzug, OHNE dass der GM-Transport
jemals erreicht wird (Spy wirft bei jedem Aufruf) -- derselbe Mechanismus
wie in `test_zr_betreiber_o3_stop_vor_planpin_2026_11_03.py`, hier ueber
den echten TUI-Rundenaufruf statt direkt gegen `store.complete_section`.

Belegt:

1. Der Betreiberkanal (`self`/Leader-Session) bekommt weiterhin die
   endgueltige Verwurf-Meldung (unveraendertes Verhalten).
2. Der betroffene GAST mit eigenem registrierten Terminal bekommt DIESELBE
   verstaendliche Meldung jetzt AUCH -- "gestoppt/nicht abgeschlossen",
   "ENDGUELTIG"/"kein Fortsetzen", eigener Stand/Figurenbindung frei,
   naechster zulaessiger Schritt.
3. Kein GM-/Modellaufruf hat jemals stattgefunden (Spy-GM-Zaehler bleibt 0).
4. Die betroffene Figurenbindung ist nach dem Verwurf tatsaechlich wieder
   frei (Reuse der bestehenden `_finalize_genuine_table_abort`-Autoritaet).

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
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_TODAY_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)


class _SpyGm:
    """Modellrand-Double: wirft SOFORT -- der bereits VOR Rundenstart
    gewonnene Betreiber-Stop muss den GM-Request verhindern, BEVOR er
    jemals gesendet wird (dieselbe Belegform wie die bestehenden O2/O3/F3a-
    Tests)."""

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


def test_guest_channel_gets_stop_notice_distinct_from_operator_channel():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        env = make_env(root)
        table_key = "mesa-g03"
        leader_id, guest_id = "leader_pk", "guest_pk"

        lobby, table, ps_store = build_two_member_table(env, table_id="g03-tisch")
        leader_save = full_v7_save("chrono-leader", name="Leader")
        guest_save = full_v7_save("chrono-guest", name="Guest")

        # Admission binden + den tischadressierten Betreiber-Stop ECHT
        # VOR dem Rundenstart gewinnen (O2/O3-Autoritaet, hier bewusst
        # NICHT ueber den Kontroll-Thread, sondern VORHER gesetzt -- der
        # gemeinsame Entscheid-Slot ist dadurch bereits "stopped", bevor
        # `_run_table_round` den ersten Zug anfordert).
        table_admission.offer_table(env.run_dir, host_id=leader_id, table_key=table_key)
        table_admission.bind_section(
            env.run_dir, table_key=table_key, host_id=leader_id, section_id=table.table_id,
        )
        table_admission.request_table_stop(
            env.run_dir, table_key=table_key, operator_id=leader_id, table_id=table.table_id,
            reason="R6-G03-Test: Stop vor Rundenstart.",
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

        assert spy_gm.calls == 0, "kein GM-Request haette jemals gesendet werden duerfen."

        operator_out = "\n".join(leader_printed)
        guest_out = "\n".join(guest_printed)

        # (1) Betreiberkanal: unveraendertes Verhalten -- bekommt weiterhin
        # die endgueltige Verwurf-Meldung.
        assert "ENDGUELTIG" in operator_out and "Betreiber-Stop" in operator_out, operator_out

        # (2) Betroffener Gastkanal: DIESELBE verstaendliche Meldung jetzt
        # AUCH -- vorher war `guest_printed` hier leer/ohne jeden Stop-
        # Hinweis.
        assert "ENDGUELTIG" in guest_out and "Betreiber-Stop" in guest_out, (
            "der betroffene Gastkanal haette die endgueltige Verwurf-Meldung bekommen muessen "
            "(vorher: nur der Betreiberkanal).", guest_out,
        )
        assert "kein Fortsetzen" in guest_out or "nicht abgeschlossen" in guest_out, guest_out

        # (3) Dieselbe Meldung -- kein zweiter, abweichender Text (Reuse,
        # keine zweite Stop-/Adoptionsautoritaet mit eigenem Wortlaut).
        operator_stop_line = next(ln for ln in leader_printed if "Betreiber-Stop" in ln)
        guest_stop_line = next(ln for ln in guest_printed if "Betreiber-Stop" in ln)
        assert operator_stop_line == guest_stop_line, (operator_stop_line, guest_stop_line)

        # (4) Figurenbindung ist nach dem Verwurf tatsaechlich wieder frei
        # (Reuse von `_finalize_genuine_table_abort`, keine neue Autoritaet).
        assert lobby.is_locked("chrono-leader") is None, lobby.is_locked("chrono-leader")
        assert lobby.is_locked("chrono-guest") is None, lobby.is_locked("chrono-guest")

        record = table_admission.load_record(env.run_dir, table_key)
        assert record["state"] == table_admission.STATE_CLOSED, record


def test_spectator_without_membership_is_not_addressed_by_stop_notice():
    """Gegenprobe: nur TATSAECHLICHE Tischmitglieder (`drivers`, hier ueber
    `getattr(driver, 'is_human_driver', False)` gefiltert) bekommen die
    Stop-Meldung -- diese Formel ist dieselbe wie die bereits bestehende,
    unveraenderte Erfolgskarten-Filterung (s. `_print_section_completion_
    card`-Aufrufer) und schliesst reine Zuschauer/Nicht-Mitglieder
    strukturell aus, weil sie gar nicht erst in `drivers` auftauchen."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        env = make_env(root)
        table_key = "mesa-g03b"
        # `build_two_member_table` verdrahtet den Tisch-Leader/-Gast FEST auf
        # `leader_pk`/`guest_pk` + Figuren `chrono-leader`/`chrono-guest`
        # (s. Fixture); der Rundenaufruf MUSS dieselben IDs tragen, sonst
        # findet `_run_table_round`s Leader-Anker (`act(self.table.leader,
        # contexts_by_persona[...])`, runtime.py) seinen Kontext nicht
        # (KeyError). Isolation ggue. Test 1 kommt bereits aus eigenem
        # tempdir + eigenem `table_key`/`table_id`, nicht aus abweichenden
        # Teilnehmer-IDs.
        leader_id, guest_id = "leader_pk", "guest_pk"

        lobby, table, ps_store = build_two_member_table(env, table_id="g03b-tisch")
        leader_save = full_v7_save("chrono-leader", name="Leader")
        guest_save = full_v7_save("chrono-guest", name="Guest")

        table_admission.offer_table(env.run_dir, host_id=leader_id, table_key=table_key)
        table_admission.bind_section(
            env.run_dir, table_key=table_key, host_id=leader_id, section_id=table.table_id,
        )
        table_admission.request_table_stop(
            env.run_dir, table_key=table_key, operator_id=leader_id, table_id=table.table_id,
            reason="R6-G03b-Test: Stop vor Rundenstart.",
        )

        leader_printed: list[str] = []
        guest_printed: list[str] = []
        bystander_printed: list[str] = []
        spy_gm = _SpyGm()

        leader_session = TuiSession(
            onboarding_dir=root / "leader_onboarding", catalog_dir=root / "leader_catalog",
            participant_id=leader_id, input_fn=_scripted_input(["Wir beobachten die Lage."]),
            print_fn=leader_printed.append, run_dir=env.run_dir, states_dir=env.states_dir,
            gm_transport_factory=lambda: spy_gm, host_capable=True,
        )
        guest_session = TuiSession(
            onboarding_dir=root / "guest_onboarding", catalog_dir=root / "guest_catalog",
            participant_id=guest_id, print_fn=guest_printed.append,
            run_dir=env.run_dir, states_dir=env.states_dir, host_capable=False,
        )
        # Ein registriertes Terminal unter einer NICHT-Mitglieds-ID -- nie
        # Teil von `drivers`, darf also NIE adressiert werden (Zuschauer-
        # Gegenprobe).
        bystander_session = TuiSession(
            onboarding_dir=root / "bystander_onboarding", catalog_dir=root / "bystander_catalog",
            participant_id="zuschauer_b", print_fn=bystander_printed.append, host_capable=False,
        )
        leader_session.register_guest_terminal(guest_id, guest_session)
        leader_session.register_guest_terminal("zuschauer_b", bystander_session)

        leader_session._run_table_round(
            table, lobby, ps_store, leader_id=leader_id, leader_persona_id=None,
            leader_driver=None, active_save=leader_save,
            guest_specs=[(guest_id, False, guest_save, None)],
            guided=False, current_focus_pid=None,
            operator_mode=False, operator_table_key=table_key,
        )

        assert any("Betreiber-Stop" in ln for ln in guest_printed), guest_printed
        assert not bystander_printed, (
            "ein registriertes Terminal, das NICHT Tischmitglied ist, darf von der "
            "Stop-Meldung nicht adressiert werden.", bystander_printed,
        )


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
