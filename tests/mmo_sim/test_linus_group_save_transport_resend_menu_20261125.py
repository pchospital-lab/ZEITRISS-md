#!/usr/bin/env python3
"""
tests/mmo_sim/test_linus_group_save_transport_resend_menu_20261125.py --
ZR-PLAYTEST-ANSCHLUSS-20261125 (Linus-Fix).

Deckt den NEUEN, bestellten TUI-Bedienweg `ui.tui.TuiSession._offer_group_
save_transport_resend_menu` ab -- der END-USER-erreichbare Weg (das
Betreiber-/Tischleiter-Terminal, aufgerufen NACH der bestehenden "kann
fortgesetzt werden"-Zeile in `_run_table_round`), ueber den der belegte
Live-Fall (zwei NPC-Tischmitglieder, transport_error-HOLD, KEIN
`best_candidate_block`) tatsaechlich geloest werden kann, OHNE dass
`_print_group_save_hold_status_lines` je einen eigenen Hinweis dafuer
zeigt (die betrachtet NUR `is_human_driver`-Mitglieder).

Faehrt die ECHTE, unveraenderte Produktmethode -- nur `self` ist ein
minimaler Duck-Typing-Stand-in (`run_dir`/`_print`/`_readline_with_
controls`), GENAU wie `test_rec2_orphan_recovery_menu_20261123_r1.py`s
`_FakeTuiSession` fuer `_offer_orphan_recovery_menu`. `table` ist der ECHTE
Tisch aus `build_two_member_table` (reale `table_id`/`chrononaut_ids`).

Deckt ab:
  1. KEIN Mitglied erfuellt die Guards (z.B. nur HOLD mit Kandidat, oder gar
     kein HOLD) -> KEINE Nachfrage (keine Antwort wird konsumiert -- die
     Fake wirft sonst), Run bytegleich.
  2. 'nein'/'/zurueck' bleiben wirkungslos (kein Write).
  3. 'ja' autorisiert GENAU den (die) eligible Datensatz/Datensaetze
     (`state` -> `validating`) -- ein bereits `adopted`/erschoepftes/mit-
     Kandidat-Mitglied bleibt UNVERAENDERT.
  4. Wiederholtes Oeffnen+Bestaetigen NACH einer bereits erfolgten Freigabe
     ist ein No-op (Datensatz bereits nicht mehr `hold`).

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
from mmo_sim.domain.zeitriss import save_correction as domain  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_LEADER_CID = "chrono-leader"
_GUEST_CID = "chrono-guest"


class _FakeTuiSession:
    """Minimaler Duck-Typing-Stand-in fuer `TuiSession` -- analog zu
    `test_rec2_orphan_recovery_menu_20261123_r1._FakeTuiSession`. Wirft, wenn
    mehr Prompts gestellt werden als Antworten gecannt wurden."""

    def __init__(self, run_dir: Path, answers: list[tuple[str, str | None]]):
        self.run_dir = run_dir
        self._answers = list(answers)
        self.printed: list[str] = []

    def _print(self, text: str) -> None:
        self.printed.append(text)

    def _readline_with_controls(self, prompt: str, *, context: str):
        if not self._answers:
            raise AssertionError(
                "FakeTuiSession: unerwarteter zusaetzlicher Prompt -- keine weiteren Antworten gecannt "
                f"(prompt={prompt!r})."
            )
        return self._answers.pop(0)


def _build_table_with_transport_hold(root: Path, table_id: str):
    """Baut einen 2er-Tisch + transport_error-HOLD fuer `guest_pk`, OHNE
    jeden `best_candidate_block` -- derselbe Ausgangszustand wie
    `test_linus_transport_error_no_candidate_fresh_resend_20261125.py`,
    hier direkt am Korrekturdatensatz (kein echter GM-Call noetig, dieser
    Test prueft nur die Menuelogik, nicht den Versandpfad)."""
    env = make_env(root)
    lobby, table, ps_store = build_two_member_table(env, table_id=table_id)
    del lobby, ps_store
    section_id = f"{table.table_id}-section"
    repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
    sc.load_or_init_record(
        env.run_dir, repair_key, persona_key="guest_pk", char_id=_GUEST_CID,
        operation_key=sc.ROLE_GROUP, table_id=table.table_id, section_id=section_id,
    )
    sc.begin_attempt(env.run_dir, repair_key)
    sc.mark_hold(env.run_dir, repair_key, reason="transport_error:timed out")
    record = sc.load_record(env.run_dir, repair_key)
    assert record["state"] == "hold" and record["last_reason"] == "transport_error:timed out"
    assert record.get("best_candidate_block") is None
    return env, table, repair_key, section_id


def _snapshot(run_dir: Path) -> dict:
    out = {}
    for p in sorted(run_dir.rglob("*")):
        if p.is_file():
            out[str(p.relative_to(run_dir))] = p.read_bytes()
    return out


# ---------------------------------------------------------------------------
# (1) Kein eligible Mitglied -> KEINE Nachfrage, bytegleich.
# ---------------------------------------------------------------------------


def test_no_prompt_when_no_member_eligible():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        env = make_env(root)
        lobby, table, ps_store = build_two_member_table(env, table_id="t-menu-1")
        del lobby, ps_store
        before = _snapshot(env.run_dir)
        fake = _FakeTuiSession(env.run_dir, answers=[])
        TuiSession._offer_group_save_transport_resend_menu(fake, table, ["guest_pk"])
        assert fake.printed == []
        after = _snapshot(env.run_dir)
        assert after == before


def test_no_prompt_when_hold_already_has_candidate():
    """Existiert bereits ein `best_candidate_block`, ist der bestehende
    kostenlose Best-effort-Pfad zustaendig -- dieses Menue bleibt stumm."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        env, table, repair_key, section_id = _build_table_with_transport_hold(root, "t-menu-2")
        record = dict(sc.load_record(env.run_dir, repair_key))
        record["best_candidate_block"] = full_v7_save(_GUEST_CID, name="Guest")
        sc._write_record(env.run_dir, repair_key, record)
        before = _snapshot(env.run_dir)

        fake = _FakeTuiSession(env.run_dir, answers=[])
        TuiSession._offer_group_save_transport_resend_menu(fake, table, ["guest_pk"])
        assert fake.printed == []
        after = _snapshot(env.run_dir)
        assert after == before


# ---------------------------------------------------------------------------
# (2) 'nein'/'/zurueck' bleiben wirkungslos.
# ---------------------------------------------------------------------------


def test_explicit_no_is_a_no_op_byte_identical():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        env, table, repair_key, section_id = _build_table_with_transport_hold(root, "t-menu-3")
        before = _snapshot(env.run_dir)
        fake = _FakeTuiSession(env.run_dir, answers=[("n", None)])
        TuiSession._offer_group_save_transport_resend_menu(fake, table, ["guest_pk"])
        after = _snapshot(env.run_dir)
        assert after == before, "ein explizites 'n' darf den Run NICHT veraendern."
        assert sc.load_record(env.run_dir, repair_key)["state"] == "hold"


def test_cancel_control_is_a_no_op_byte_identical():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        env, table, repair_key, section_id = _build_table_with_transport_hold(root, "t-menu-4")
        before = _snapshot(env.run_dir)
        fake = _FakeTuiSession(env.run_dir, answers=[("", "zurueck")])
        TuiSession._offer_group_save_transport_resend_menu(fake, table, ["guest_pk"])
        after = _snapshot(env.run_dir)
        assert after == before, "'/zurueck' darf den Run NICHT veraendern."
        assert sc.load_record(env.run_dir, repair_key)["state"] == "hold"


# ---------------------------------------------------------------------------
# (3) 'ja' autorisiert GENAU den eligible Datensatz -- Fremde bleiben unberuehrt.
# ---------------------------------------------------------------------------


def test_yes_authorizes_fresh_resend_other_member_untouched():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        env, table, repair_key, section_id = _build_table_with_transport_hold(root, "t-menu-5")

        # Fremder, bereits adoptierter Leader-Datensatz (Palimpsest-Analogon) --
        # muss unberuehrt bleiben.
        leader_repair_key = domain.group_repair_key(table.table_id, section_id, _LEADER_CID)
        sc.load_or_init_record(
            env.run_dir, leader_repair_key, persona_key="leader_pk", char_id=_LEADER_CID,
            operation_key=sc.ROLE_GROUP, table_id=table.table_id, section_id=section_id,
        )
        leader_adopted = sc.mark_adopted(
            env.run_dir, leader_repair_key, adopted_block=full_v7_save(_LEADER_CID, name="Leader"),
        )

        fake = _FakeTuiSession(env.run_dir, answers=[("j", None)])
        TuiSession._offer_group_save_transport_resend_menu(fake, table, ["guest_pk", "leader_pk"])

        guest_after = sc.load_record(env.run_dir, repair_key)
        assert guest_after["state"] == "validating", guest_after
        assert any("autorisiert" in line for line in fake.printed), fake.printed

        leader_after = sc.load_record(env.run_dir, leader_repair_key)
        assert leader_after == leader_adopted, (
            "die Freigabe des Gast-HOLDs darf den fremden, bereits adoptierten Leader-Datensatz NICHT anfassen."
        )


# ---------------------------------------------------------------------------
# (4) Wiederholtes Oeffnen+Bestaetigen NACH bereits erfolgter Freigabe -> No-op.
# ---------------------------------------------------------------------------


def test_reopening_after_authorization_is_a_no_op():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        env, table, repair_key, section_id = _build_table_with_transport_hold(root, "t-menu-6")

        fake1 = _FakeTuiSession(env.run_dir, answers=[("ja", None)])
        TuiSession._offer_group_save_transport_resend_menu(fake1, table, ["guest_pk"])
        record_after_first = sc.load_record(env.run_dir, repair_key)
        assert record_after_first["state"] == "validating"

        # Zweites Oeffnen+Bestaetigen desselben Menues: der Datensatz ist nicht
        # mehr "hold" -- das Menue findet GAR KEIN eligible Mitglied mehr und
        # fragt ueberhaupt nicht erneut nach (answers=[] wirft sonst).
        fake2 = _FakeTuiSession(env.run_dir, answers=[])
        TuiSession._offer_group_save_transport_resend_menu(fake2, table, ["guest_pk"])
        assert fake2.printed == []
        record_after_second = sc.load_record(env.run_dir, repair_key)
        assert record_after_second == record_after_first, (
            "ein zweites Oeffnen nach bereits erfolgter Freigabe darf den Datensatz NICHT veraendern."
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
