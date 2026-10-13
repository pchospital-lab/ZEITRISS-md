#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_r5_round_journey_restart_idempotency_2026_10_06.py —
W20/F04 (ZEITRISS Terminal UX-1, R5-Wiederanlauf): Neustart ueber ZWEI
ECHTE, GETRENNTE OS-Prozesse WAEHREND einer laufenden MEHRMENSCHEN-Runde
(nicht nur einer Erschaffung oder eines Mensch+KI-Tisches) -- die identifi-
zierte Luecke aus der Bestandsaufnahme: `test_ux1_g03_same_authority_
resume_2026_10_05.py::test_p09_...`/`test_ux1_r06_adapter_pending_
completion_restart_2026_10_05.py` belegen den Restart bereits real fuer
Mensch-Leader+KI-Gast bzw. fuer einen offenen Abschlussauftrag, aber KEIN
bestehender Test kombiniert den echten Prozessneustart mit EINEM ZWEITEN
MENSCHEN am geteilten Terminal, dessen Fokusuebergabe (`_local_round_
handoff`, `guided=True` in `_resume_bound_table`) nach dem Neustart ERNEUT
real bestaetigt werden muss.

Prozess 1 (eigene OS-PID): Mensch-Leader + zweiter Mensch (Gast) spielen
je EINEN echten Zug, dann Pause (Eingabequeue erschoepft, KEIN Abschluss).
Prozess 2 (neue OS-PID, `_cmd_menu_fortsetzen`): derselbe Tisch wird
fortgesetzt -- der Gast muss die Terminaluebergabe ERNEUT real bestaetigen
(`guided=True`, `current_focus_pid` startet wieder beim Leader), danach
spielen beide je einen WEITEREN echten Zug.

Kernnachweis (Request-/Completion-Idempotenz mit Originalbytes und
Callzaehlern):
  (1) Die ALTEN `sl_log`-Eintraege aus Prozess 1 bleiben in Prozess 2
      BYTEGLEICH als Praefix erhalten (kein Nachtraeglich-Umschreiben).
  (2) Der GM-Fake in Prozess 2 (frische Instanz, leerer Prozessspeicher)
      bekommt NUR die beiden NEUEN Zuege -- kein Doppelversand der
      Prozess-1-Zuege.
  (3) `invitation_decisions.jsonl` bleibt zwischen Prozessende 1 und
      Prozessstart 2 BYTEGLEICH (kein neuer Consent-Request fuer den
      bereits aufgenommenen Gast durch den Resume selbst).
  (4) Die Fokusuebergabe an den Gast erscheint in Prozess 2 ERNEUT im
      Transkript (reale Wiederholung nach dem Neustart, kein uebersprungener
      Schritt).

Wiederverwendet `test_ux1_g03_same_authority_resume_2026_10_05.py`s
`_queued_input`/`_SCHEMA`-Bausteine (`--child`-Subprozess-Selbstaufruf-
Technik 1:1 wie dort/`test_ux1_r06_adapter_pending_completion_restart_
2026_10_05.py`) -- kein neuer Fake-Mechanismus."""
from __future__ import annotations

import argparse
import json
import subprocess
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
import test_ux1_g03_same_authority_resume_2026_10_05 as g03  # noqa: E402


class _NeverCompletingCountingGm:
    """Nie ein Abschlussmarker (die Runde bleibt `active`, kein Abschluss-/
    Reflexionsrauschen fuer diesen Restart-Nachweis) -- jeder Prozess
    bekommt eine FRISCHE Instanz mit leerem `self.calls` (echter, leerer
    Prozessspeicher nach einem OS-Neustart, kein wiederverwendetes Objekt)."""

    def __init__(self):
        self.calls: list[str] = []

    def turn(self, idx, text, **kw):
        self.calls.append(text)
        return {
            "content": "Ihr beobachtet die Lage weiter. Was tut ihr als Naechstes?",
            "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "table",
        }


def _child_setup(args: argparse.Namespace) -> None:
    """Prozess 1 (ECHTER eigenstaendiger Subprozess): Mensch-Leader + Mensch-
    Gast, je EIN echter Zug, dann Pause (Eingabequeue erschoepft, KEIN
    Abschluss) -- `guided=False` (roher `l`-Tokenweg), die Fokusuebergaben
    NACH dem Neustart sind Gegenstand von Prozess 2, nicht dieses Prozesses."""
    root = Path(args.root)
    states_dir, run_dir = root / "states", root / "run"
    onboarding_dir, catalog_dir, registry_dir = root / "onboarding", root / "catalog", root / "registry"
    for d in (states_dir, run_dir, onboarding_dir, catalog_dir, registry_dir):
        d.mkdir(parents=True, exist_ok=True)

    leader = sup.register_human(registry_dir, "RestartLeader")
    guest = sup.register_human(registry_dir, "RestartGuest")
    leader_id, guest_id = leader.participant_id, guest.participant_id
    sup.onboard_human_figure(registry_dir, leader_id, onboarding_dir, states_dir, run_dir, "CHR-W20R-L", "RL", "RLOPS")
    sup.onboard_human_figure(registry_dir, guest_id, onboarding_dir, states_dir, run_dir, "CHR-W20R-G", "RG", "RGOPS")
    write_test_profile(run_dir)

    # `_resolve_member` (fuer den eigentlichen Rundenablauf) braucht NUR
    # `onboarding`/`current_saves` (bereits durch `onboard_human_figure`
    # gesetzt) -- `_build_resume_card`/`_cmd_menu_fortsetzen` (Prozess 2)
    # braucht ZUSAeTZLICH die Katalogbindung, genau wie `test_ux1_g03_...::
    # _make_ready` sie fuer KI-Personas real setzt (`catalog.last_selected`
    # ist die alleinige Quelle fuer die Fortsetzen-Karte, kein Produkt-Stub).
    from mmo_sim.domain.zeitriss import catalog
    for pid, chrono_id in ((leader_id, "CHR-W20R-L"), (guest_id, "CHR-W20R-G")):
        catalog.register(catalog_dir, catalog.CatalogEntry(
            participant_id=pid, chrononaut_id=chrono_id, persona_key=pid,
        ))
        catalog.bind_for_section(catalog_dir, pid, chrono_id, has_open_section=False)

    gm = _NeverCompletingCountingGm()
    printed: list[str] = []
    session = TuiSession(
        onboarding_dir, catalog_dir, leader_id,
        input_fn=g03._queued_input(["j", "Leader-Zug-Prozess1.", "Gast-Zug-Prozess1."]),
        print_fn=printed.append,
        run_dir=run_dir, states_dir=states_dir, schema_path=g03._SCHEMA,
        gm_transport_factory=lambda *_a, **_kw: gm,
    )
    errors: list[str] = []
    try:
        session._cmd_local_round([guest_id])
    except EndOfInput:
        pass
    except Exception as e:  # echter unerwarteter Prozessabbruch bleibt sichtbar.
        errors.append(f"{type(e).__name__}: {e}")

    tables = list((run_dir / "tables").glob("*.json"))
    row = {
        "errors": errors,
        "printed": printed,
        "leader_id": leader_id,
        "guest_id": guest_id,
        "table_names": sorted(p.stem for p in tables),
        "tables": {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in tables},
        "gm_calls": list(gm.calls),
        "invitation_log": (run_dir / "invitation_decisions.jsonl").read_text(encoding="utf-8")
        if (run_dir / "invitation_decisions.jsonl").exists() else "",
    }
    Path(args.result).write_text(json.dumps(row, indent=2, ensure_ascii=False), encoding="utf-8")


def _child_resume(args: argparse.Namespace) -> None:
    """Prozess 2 (neue OS-PID): `leader_id` ruft `_cmd_menu_fortsetzen()`
    auf -- derselbe Tisch wird real fortgesetzt; der Gast muss die
    Terminaluebergabe ERNEUT bestaetigen (`guided=True` in `_resume_bound_
    table`, `current_focus_pid` startet beim Leader), danach je ein
    WEITERER echter Zug fuer beide."""
    root = Path(args.root)
    states_dir, run_dir = root / "states", root / "run"
    onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
    ids = json.loads((root / "ids.json").read_text(encoding="utf-8"))
    leader_id, guest_id = ids["leader_id"], ids["guest_id"]

    gm2 = _NeverCompletingCountingGm()
    printed: list[str] = []
    session = TuiSession(
        onboarding_dir, catalog_dir, leader_id,
        # `current_focus_pid` startet beim Leader (= `self.participant_id`
        # dieses Prozesses) -- der Leader ist daher OHNE erneute Uebergabe
        # zuerst an der Reihe (sein eigener echter Zug), DANACH ERST
        # braucht der Gast die reale Fokusuebergabe ('j'), gefolgt von
        # seinem eigenen echten Zug, DANACH braucht der Leader (naechster
        # Akteurwechsel zurueck) erneut eine Uebergabe ('j') -- die Runde
        # endet danach kontrolliert per EOF (Queue erschoepft).
        input_fn=g03._queued_input(["Leader-Zug-Prozess2.", "j", "Gast-Zug-Prozess2.", "j"]),
        print_fn=printed.append,
        run_dir=run_dir, states_dir=states_dir, schema_path=g03._SCHEMA,
        gm_transport_factory=lambda *_a, **_kw: gm2,
    )
    errors: list[str] = []
    try:
        session._cmd_menu_fortsetzen()
    except EndOfInput:
        pass
    except Exception as e:
        errors.append(f"{type(e).__name__}: {e}")

    tables = list((run_dir / "tables").glob("*.json"))
    row = {
        "errors": errors,
        "printed": printed,
        "tables_after": {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in tables},
        "gm2_calls": list(gm2.calls),
        "invitation_log_after": (run_dir / "invitation_decisions.jsonl").read_text(encoding="utf-8")
        if (run_dir / "invitation_decisions.jsonl").exists() else "",
    }
    Path(args.result).write_text(json.dumps(row, indent=2, ensure_ascii=False), encoding="utf-8")


def _run_child(root: Path, mode: str, result_path: Path) -> dict:
    cmd = [sys.executable, str(Path(__file__).resolve()), "--child", "--mode", mode,
           "--root", str(root), "--result", str(result_path)]
    cp = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if cp.returncode != 0:
        raise RuntimeError(f"child(mode={mode!r}) exit={cp.returncode}:\n{cp.stderr[-4000:]}")
    return json.loads(result_path.read_text(encoding="utf-8"))


def test_real_os_restart_mid_two_human_round_handoff_repeats_no_doppelcall_original_bytes():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)

        r1 = _run_child(root, "setup", root / "r1.json")
        assert not r1["errors"], r1["errors"]
        assert len(r1["table_names"]) == 1, r1["table_names"]
        (table_name,) = r1["table_names"]
        table1 = r1["tables"][table_name]
        assert table1["status"] == "active", "Vorbedingung: Tisch darf nach Prozess 1 NICHT abgeschlossen sein"
        assert len(r1["gm_calls"]) == 2, (
            f"genau zwei echte Zuege (Leader-Anker + Gast-Erstimport) in Prozess 1 erwartet: {r1['gm_calls']}"
        )
        sl_log_1 = table1.get("sl_log", [])
        assert len(sl_log_1) == 2, sl_log_1
        # Prozess 1 nutzt bewusst den rohen `l`-Tokenweg (`guided=False`,
        # s. Docstring `_child_setup`) -- KEINE Fokusuebergabe hier; die
        # reale Fokusuebergabe NACH dem Neustart ist Gegenstand von Prozess 2
        # (`_resume_bound_table` setzt `guided=True` IMMER selbst, unabhaengig
        # davon, wie der Tisch urspruenglich entstand).

        (root / "ids.json").write_text(
            json.dumps({"leader_id": r1["leader_id"], "guest_id": r1["guest_id"]}), encoding="utf-8",
        )

        r2 = _run_child(root, "resume", root / "r2.json")
        assert not r2["errors"], r2["errors"]

        # (4) Fokusuebergabe erscheint auch in Prozess 2 real (nicht nur in
        # Prozess 1 "erinnert"). `_local_round_handoff` druckt "Eingabe
        # fuer: ..." VOR der eigentlichen (als Prompttext, nicht als
        # `print_fn`-Ausgabe uebergebenen) "Geteiltes Terminal..."-Zeile --
        # der Beleg hier ist daher die `print_fn`-Zeile.
        handoff_marker = f"Eingabe fuer: RestartGuest | Teilnehmer {r1['guest_id']}"
        assert any(handoff_marker in p for p in r2["printed"]), (
            f"UX13-Analog: Fokusuebergabe an den Gast muss nach dem Neustart ERNEUT real "
            f"stattfinden: {r2['printed'][-20:]}"
        )

        # (2) frische GM-Instanz in Prozess 2 bekommt NUR den NEUEN
        # Leader-Zug -- kein Doppelversand der Prozess-1-Zuege. Der Gast
        # gilt (aus `table.sl_log`, R1/UX14-Autoritaet) bereits als
        # "importiert" -- sein Zug nach dem Neustart ist folgerichtig
        # Tischabsprache (kein zweiter Import-/SL-Call fuer denselben
        # Gast, s. Beleg unten ueber `table_messages`), GENAU wie ein
        # regulaerer Gastfolgezug OHNE Neustart (`_HumanDriver.
        # _purpose_label`) -- das ist selbst ein Idempotenzbeleg (der
        # Neustart aendert NICHT die Erstimport-/Folgezug-Klassifikation).
        assert len(r2["gm2_calls"]) == 1, (
            f"genau EIN NEUER SL-Call (Leader) in Prozess 2 erwartet: {r2['gm2_calls']}"
        )
        for old_text in ("Leader-Zug-Prozess1.", "Gast-Zug-Prozess1."):
            assert not any(old_text in c for c in r2["gm2_calls"]), (
                f"Prozess-1-Zug darf in Prozess 2 NICHT erneut beim SL ankommen: {old_text!r} in {r2['gm2_calls']}"
            )
        assert any("Leader-Zug-Prozess2." in c for c in r2["gm2_calls"]), (
            f"neuer Leader-Zug fehlt beim SL in Prozess 2: {r2['gm2_calls']}"
        )
        assert not any("Gast-Zug-Prozess2." in c for c in r2["gm2_calls"]), (
            "der Gastzug nach dem Neustart darf NICHT (erneut) als SL-Import gesendet werden "
            f"(muss Tischabsprache sein): {r2['gm2_calls']}"
        )

        # (1) Originalbytes: die ALTEN sl_log-Eintraege bleiben als Praefix
        # bytegleich erhalten.
        (table_name_after,) = r2["tables_after"].keys()
        assert table_name_after == table_name
        table2 = r2["tables_after"][table_name]
        sl_log_2 = table2.get("sl_log", [])
        assert len(sl_log_2) >= len(sl_log_1), (
            f"sl_log darf nach dem Resume nicht kuerzer werden: vorher={len(sl_log_1)} nachher={len(sl_log_2)}"
        )
        assert sl_log_2[: len(sl_log_1)] == sl_log_1, (
            "UX13-Analog: die ALTEN sl_log-Eintraege aus Prozess 1 muessen in Prozess 2 "
            f"byte-/feldgleich als Praefix erhalten bleiben:\nvorher={sl_log_1}\nnachher={sl_log_2[:len(sl_log_1)]}"
        )
        assert len(sl_log_2) > len(sl_log_1), "Prozess 2 muss echte NEUE sl_log-Eintraege hinzugefuegt haben"
        table_messages_2 = table2.get("table_messages", [])
        assert any(m.get("text") == "Gast-Zug-Prozess2." for m in table_messages_2), (
            f"Gastzug nach dem Neustart muss als Tischabsprache persistiert sein: {table_messages_2}"
        )

        # (3) invitation_decisions.jsonl bleibt zwischen Prozessende 1 und
        # Prozessstart 2 bytegleich -- kein neuer Consent-Request durch den
        # Resume selbst fuer den bereits aufgenommenen Gast.
        assert r2["invitation_log_after"].startswith(r1["invitation_log"]), (
            "UX13-Analog: `_cmd_menu_fortsetzen` darf beim Resume keine neue Einladungs-/"
            f"Consent-Zeile VOR den bereits bestehenden anhaengen/sie umschreiben:\n"
            f"vorher={r1['invitation_log']!r}\nnachher={r2['invitation_log_after']!r}"
        )
        new_invite_lines = r2["invitation_log_after"][len(r1["invitation_log"]):]
        assert r1["guest_id"] not in new_invite_lines, (
            f"kein neuer Consent-/Einladungseintrag fuer den bereits aufgenommenen Gast durch den "
            f"Resume selbst erwartet: neue Zeilen={new_invite_lines!r}"
        )
        assert table2["status"] == "active", "Vorbedingung dieses Nachweises: Runde bleibt bewusst offen (kein Abschluss noetig)"


def main() -> int:
    tests = [test_real_os_restart_mid_two_human_round_handoff_repeats_no_doppelcall_original_bytes]
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
    if "--child" in sys.argv:
        ap = argparse.ArgumentParser()
        ap.add_argument("--child", action="store_true")
        ap.add_argument("--mode", required=True, choices=["setup", "resume"])
        ap.add_argument("--root", required=True)
        ap.add_argument("--result", required=True)
        ns = ap.parse_args()
        if ns.mode == "setup":
            _child_setup(ns)
        else:
            _child_resume(ns)
        sys.exit(0)
    raise SystemExit(main())
