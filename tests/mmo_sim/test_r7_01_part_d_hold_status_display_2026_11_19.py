#!/usr/bin/env python3
"""
tests/mmo_sim/test_r7_01_part_d_hold_status_display_2026_11_19.py --
ZR-ALTAIR-UPDATER-SPIELTEST-NACHZUG-20261119-R7, §02 (R7-01) Part D.

Belegt am echten Produktcode (`ui.tui.TuiSession._print_group_save_hold_
status_lines`, der von `_run_table_round`s bestehender, bytegleich
belassener "kann fortgesetzt werden"-Zeile aus aufgerufen wird) die
bestellte eindeutige Speicheranzeige:

1. Fuer ein noch fehlendes Mitglied MIT einem tatsaechlich terminalen
   `STATE_HOLD`-Korrekturdatensatz erscheint eine Zusatzzeile MIT dem
   letzten bestaetigten Save, dem Fehlergrund in verstaendlicher Kurzform
   (`public_hold_reason`, NIE der rohe interne `last_reason`-Text) und
   einem Hinweis auf die verfuegbare normale Wiederaufnahme.
2. Fuer ein Mitglied OHNE terminalen HOLD (z.B. eine noch offene, nicht
   terminale Korrektur) erscheint KEINE solche Zusatzzeile (keine falsche
   Fehlermeldung fuer einen Fall, der tatsaechlich noch normal weiterlaeuft).
3. Die Zeile erscheint am EIGENEN Terminal des betroffenen Mitglieds
   (`_table_guest_terminals`-Zuordnung), nicht am Betreiberkanal.
4. Nur tatsaechlich menschliche Treiber (`is_human_driver`) werden
   ueberhaupt betrachtet.

Reiner Lesezugriff auf bereits bestehende Korrekturdatensaetze/Save-
Autoritaet -- kein Modellaufruf, kein neues Menuesystem.

Pure Python, nur `assert`, echter Exitcode."""
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

import mmo_sim.core.save_correction as sc  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss import save_correction as domain  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_LEADER_CID = "chrono-leader"
_GUEST_CID = "chrono-guest"


class _HumanLikeDriver:
    is_human_driver = True


def _register_private_figure(onboarding_dir: Path, catalog_dir: Path, participant_id: str, char_id: str) -> dict:
    save = full_v7_save(char_id, name=participant_id, save_id=f"fixture-{participant_id}-001", level=3)
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
    ))
    catalog.bind_for_section(catalog_dir, participant_id, char_id, has_open_section=False)
    return save


def test_hold_status_line_shows_last_save_public_reason_and_resume_hint():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        env = make_env(root)
        lobby, table, ps_store = build_two_member_table(env, table_id="t-r7-d1")
        del lobby, ps_store

        guest_id = "guest_pk"
        guest_onboarding_dir = root / "guest_onboarding"
        guest_catalog_dir = root / "guest_catalog"
        _register_private_figure(guest_onboarding_dir, guest_catalog_dir, guest_id, _GUEST_CID)

        section_id = f"{table.table_id}-section"
        repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
        sc.load_or_init_record(
            env.run_dir, repair_key, persona_key=guest_id, char_id=_GUEST_CID,
            operation_key=sc.ROLE_GROUP, table_id=table.table_id, section_id=section_id,
        )
        sc.begin_attempt(env.run_dir, repair_key)
        sc.mark_hold(env.run_dir, repair_key, reason="unjustified_semantic_drift")
        record = sc.load_record(env.run_dir, repair_key)
        assert record["state"] == "hold" and record["last_reason"] == "unjustified_semantic_drift"

        guest_printed: list[str] = []
        leader_printed: list[str] = []
        leader_session = TuiSession(
            onboarding_dir=root / "leader_onboarding", catalog_dir=root / "leader_catalog",
            participant_id="leader_pk", print_fn=leader_printed.append,
            run_dir=env.run_dir, states_dir=env.states_dir, host_capable=True,
        )
        guest_session = TuiSession(
            onboarding_dir=guest_onboarding_dir, catalog_dir=guest_catalog_dir,
            participant_id=guest_id, print_fn=guest_printed.append,
            run_dir=env.run_dir, states_dir=env.states_dir, host_capable=False,
        )
        leader_session.register_guest_terminal(guest_id, guest_session)

        drivers = {"leader_pk": _HumanLikeDriver(), guest_id: _HumanLikeDriver()}
        leader_session._print_group_save_hold_status_lines(table, [guest_id], drivers)

        assert leader_printed == [], (
            f"die Zusatzzeile muss am EIGENEN Terminal des betroffenen Mitglieds erscheinen, "
            f"NICHT am Betreiberkanal: {leader_printed}"
        )
        assert len(guest_printed) == 1, guest_printed
        line = guest_printed[0]
        assert "NICHT gespeichert" in line, line
        assert "unjustified_semantic_drift" in line, (
            f"der Fehlergrund muss ueber public_hold_reason in verstaendlicher Kurzform erscheinen: {line}"
        )
        assert "Level 3" in line, (
            f"der letzte bestaetigte Save (echte registrierte Figur, Level 3) muss erkennbar sein, "
            f"NICHT der Fallback 'kein frueherer bestaetigter Stand bekannt': {line}"
        )
        assert "Wiederaufnahme" in line, line


def test_no_hold_status_line_for_non_terminal_member():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        env = make_env(root)
        lobby, table, ps_store = build_two_member_table(env, table_id="t-r7-d2")
        del lobby, ps_store

        guest_id = "guest_pk"
        section_id = f"{table.table_id}-section"
        repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
        # NUR angelegt/in Korrektur -- state bleibt "validating"/"correction_
        # pending", NIE terminal "hold". Ein solches Mitglied wartet noch
        # auf einen normalen, bereits laufenden Korrekturversuch -- KEINE
        # Fehlermeldung ist hier ehrlich.
        sc.load_or_init_record(
            env.run_dir, repair_key, persona_key=guest_id, char_id=_GUEST_CID,
            operation_key=sc.ROLE_GROUP, table_id=table.table_id, section_id=section_id,
        )
        sc.begin_attempt(env.run_dir, repair_key)
        record = sc.load_record(env.run_dir, repair_key)
        assert record["state"] == "correction_pending"

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=root / "leader_onboarding", catalog_dir=root / "leader_catalog",
            participant_id="leader_pk", print_fn=printed.append,
            run_dir=env.run_dir, states_dir=env.states_dir, host_capable=True,
        )
        drivers = {"leader_pk": _HumanLikeDriver(), guest_id: _HumanLikeDriver()}
        session._print_group_save_hold_status_lines(table, [guest_id], drivers)
        assert printed == [], (
            f"ein nicht-terminaler Korrekturdatensatz (noch laufende Reparatur) darf KEINE "
            f"Fehler-/Hold-Zeile ausloesen: {printed}"
        )


def test_no_hold_status_line_for_non_human_driver():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        env = make_env(root)
        lobby, table, ps_store = build_two_member_table(env, table_id="t-r7-d3")
        del lobby, ps_store

        guest_id = "guest_pk"
        section_id = f"{table.table_id}-section"
        repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
        sc.load_or_init_record(
            env.run_dir, repair_key, persona_key=guest_id, char_id=_GUEST_CID,
            operation_key=sc.ROLE_GROUP, table_id=table.table_id, section_id=section_id,
        )
        sc.begin_attempt(env.run_dir, repair_key)
        sc.mark_hold(env.run_dir, repair_key, reason="unjustified_semantic_drift")

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=root / "leader_onboarding", catalog_dir=root / "leader_catalog",
            participant_id="leader_pk", print_fn=printed.append,
            run_dir=env.run_dir, states_dir=env.states_dir, host_capable=True,
        )

        class _AiDriver:
            pass  # kein is_human_driver -- Standard-AI-/Persona-Treiber.

        drivers = {"leader_pk": _HumanLikeDriver(), guest_id: _AiDriver()}
        session._print_group_save_hold_status_lines(table, [guest_id], drivers)
        assert printed == [], (
            f"ein NICHT-menschlicher Treiber (Persona/KI) darf KEINE persoenliche "
            f"Speicherstatuszeile ausloesen: {printed}"
        )


def _run_all() -> int:
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in fns:
        try:
            fn()
            print(f"OK   {fn.__name__}")
            passed += 1
        except AssertionError:
            print(f"FAIL {fn.__name__}")
            traceback.print_exc()
        except Exception:
            print(f"ERROR {fn.__name__}")
            traceback.print_exc()
    print(f"\n{passed}/{len(fns)} passed")
    return 0 if passed == len(fns) else 1


if __name__ == "__main__":
    raise SystemExit(_run_all())
