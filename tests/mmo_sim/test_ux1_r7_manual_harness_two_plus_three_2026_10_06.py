#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_r7_manual_harness_two_plus_three_2026_10_06.py —
R7/W30 (ZEITRISS Terminal UX-1, Reparatur R7P02): belegt, dass der ECHTE
freie Harness (`manual_offline_harness.py`, NICHT eine Testdoppel-Nach-
bildung seiner Verdrahtung) nach dem W30-Fix tatsaechlich eine 2+3-Runde
bilden kann.

Befund (Main-Pre-T-Gate, s. BRIEF-W30.md): der unveraenderte Harness
registrierte nur EINEN Menschen ("Leader") und machte KEINE KI-Persona
ueber den echten Produktweg tischbereit -- 'l persona:medic' scheiterte
deshalb immer mit "Einladung an 'medic' nicht moeglich: keine abge-
schlossene Figur vorhanden.". Ein blinder Tester konnte so KEINE 2+3-Runde
bilden.

Fix (`manual_offline_harness.py`): beim Setup wird jetzt eine bekannte,
klar SIMULIERT markierte KI-Spielgemeinschaft (sniper/tech/medic) ueber
denselben Produktweg wie die bestehenden A24-Tests bereitgestellt
(`_a24_local_support.bootstrap_six_persona_community` + `make_ready` --
Community-Bootstrap + Onboarding + `core.store.publish_current_save`,
kein Save-Inject in eine Runde). Der menschliche Leader heisst neutral
"Testspieler A" statt "Leader". `complete_after` des GM-Doubles wurde von
2 auf 8 angehoben (derselbe Wert wie der bestehende, erfolgreiche A24-
Fuenferrundentest `test_a24_guided_setup_g_path_human_leader_with_
handoff`) -- mit dem alten Wert versuchte der GM-Double den Abschluss
bereits nach der zweiten Nachricht, lange bevor alle fuenf Mitglieder
(2 Menschen + 3 KI) ueberhaupt importiert hatten, und der Abschnitt wurde
dadurch strukturell IMMER unterbrochen.

Dieser Test faehrt `manual_offline_harness.py` SELBST (nicht
`scripts/mmo_sim.py` direkt) als echten, eigenstaendigen Subprozess mit
gepipter stdin -- exakt der reale Einstiegspunkt, den ein blinder Tester
(T) benutzt.

R7/W32 (F02-Folgeanpassung, BRIEF-W32.md): der Harness legt seine vier
Callbelege seit dem F02-Fix nicht mehr flach unter `logs/*.jsonl` ab,
sondern je Prozess exklusiv unter `logs/run-NNNN/*.jsonl`
(`_next_exclusive_run_logs_dir`, 1-basiert, `run-0001` ist der erste
Harness-Prozess fuer ein `--data-dir`). Die beiden Stellen, die
`persona_decision_calls.jsonl` lesen, wurden auf den tatsaechlich
massgeblichen Lauf umgestellt -- Assertions selbst unveraendert.

Drei Szenarien:

  test_two_plus_three_via_real_harness_reaches_closed_with_post_import_
  contribution: Prozess 1 (frischer `--data-dir`) erschafft die eigene
  Figur ECHT ueber '[n]' UND registriert/erschafft eine zweite Person
  ("Testspieler B") ECHT ueber 'registrieren' (derselbe Erschaffungs-GM,
  kein Save-Inject). Prozess 2 (ECHTER SEPARATER Subprozess, DIESELBE
  Datenroot -- Prozessneustart ohne Replay) laedt Testspieler B + die drei
  bereitgestellten KI (sniper/tech/medic) ueber den bestehenden
  'l <id> persona:...'-Tokenweg ein und spielt bis zum echten `closed`,
  inklusive eines regulaeren Tischabsprache-Beitrags von Testspieler B
  NACH ihrem Erstimport (eigenes Label im Produkt, s. unten).

  test_reject_scenario_blocks_table_formation: `--scenario reject
  --reject-persona-key medic` -- eine der bereitgestellten KI lehnt ECHT
  per HTTP ab, die Runde kommt kontrolliert NICHT zustande (klar von
  'ungueltige Eingabe' unterscheidbar), kein stiller kleinerer Tisch.

  test_solo_regression_still_closes: Solo-Weg (keine Einladung) bleibt
  nach dem W30-Fix funktionsfaehig und erreicht echtes `closed` (die
  angehobene `complete_after`-Schwelle braucht dafuer entsprechend mehr
  Spielzuege als vorher, s. Kommentar in `manual_offline_harness.py`).

Pure Python, nur `assert`, echter Exitcode, synthetische Temp-Dirs, ECHTE
eigenstaendige Subprozesse von `manual_offline_harness.py` selbst."""
from __future__ import annotations

import re
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

from mmo_sim.core import store as core_store  # noqa: E402

import _a24_local_support as sup  # noqa: E402

HARNESS = _HERE / "manual_offline_harness.py"
_AI_KEYS = ("sniper", "tech", "medic")
_LEADER_ID_RE = re.compile(r"Deine Teilnehmer-ID: (p[0-9a-f]+)")
_B_ID_RE = re.compile(r"Neu registriert: (p[0-9a-f]+) \(Testspieler B\)")


def _run_harness(data_dir: Path, stdin_text: str, *, extra_args=(), timeout: int = 150) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "-B", str(HARNESS), "--data-dir", str(data_dir), *extra_args]
    return subprocess.run(cmd, input=stdin_text, cwd=str(_REPO_ROOT), capture_output=True, text=True, timeout=timeout)


def _run_logs_dir(data_dir: Path, run_no: int) -> Path:
    """R7/W32 (F02-Folgeanpassung): `run_no`-ter Harness-Prozess (1-basiert)
    fuer dieses `data_dir` -- muss zur Zaehlung in
    `manual_offline_harness._next_exclusive_run_logs_dir` passen."""
    return data_dir / "logs" / f"run-{run_no:04d}"


def test_two_plus_three_via_real_harness_reaches_closed_with_post_import_contribution():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)

        # Prozess 1: Testspieler A erschafft die eigene Figur ECHT ueber
        # '[n]', dann registriert/erschafft Testspieler B ECHT ueber
        # 'registrieren' (derselbe Erschaffungs-GM, kein Save-Inject, kein
        # zweiter Prozess-/Figurweg).
        stdin1 = "\n".join([
            "n", "Standardausruestung Testspieler A (W30-Beleg).",
            "registrieren", "Testspieler B", "j", "n",
            "Standardausruestung Testspieler B (W30-Beleg).",
        ]) + "\n"
        p1 = _run_harness(data_dir, stdin1)
        assert p1.returncode == 0, f"Prozess 1 fehlgeschlagen: rc={p1.returncode}\n{p1.stderr[-2000:]}"
        out1 = p1.stdout
        assert out1.count("Erschaffung abgeschlossen:") == 2, (
            f"beide frischen Erschaffungen (Testspieler A UND B) muessen echt abgeschlossen sein: {out1[-1500:]}"
        )
        leader_match = _LEADER_ID_RE.search(out1)
        b_match = _B_ID_RE.search(out1)
        assert leader_match, f"Teilnehmer-ID des Leaders nicht gefunden: {out1[:500]}"
        assert b_match, f"Testspieler B wurde nicht ueber 'registrieren' echt registriert: {out1[-1500:]}"
        leader_id, b_id = leader_match.group(1), b_match.group(1)
        assert leader_id != b_id

        # Prozess 2: ECHTER SEPARATER Subprozess, DIESELBE Datenroot
        # (Prozessneustart ohne Replay) -- laedt Testspieler B + die drei
        # bereitgestellten KI ueber den bestehenden 'l <id> persona:...'-
        # Tokenweg ein. Grosszuegige, aber begrenzte Zugfolge (12 Runden je
        # Akteur): die genaue Rundenanzahl bis zum Abschluss haengt an der
        # internen Reihenfolge (Erstimport aller fuenf Mitglieder zuerst,
        # danach reguläre Tischabsprache-Runden) -- empirisch belegt
        # (worker/W30/logs/) genuegt das reichlich, ohne eine exakte Zahl
        # als Produktvertrag vorauszusetzen.
        tokens = f"{b_id} persona:sniper persona:tech persona:medic"
        moves = []
        for i in range(1, 13):
            moves += [f"Leader-Zug-{i}-W30.", f"TestspielerB-Zug-{i}-W30."]
        stdin2 = "\n".join([f"l {tokens}", "j", *moves, "Leader-Notiz-W30.", "TestspielerB-Notiz-W30."]) + "\n"
        p2 = _run_harness(data_dir, stdin2)
        assert p2.returncode == 0, f"Prozess 2 fehlgeschlagen: rc={p2.returncode}\n{p2.stderr[-2000:]}"
        out2 = p2.stdout

        assert f"[{b_id}] Dieser lokalen Runde (Leader: {leader_id}) beitreten?" in out2, out2[-1500:]
        assert "Gruppe eingeladen" in out2, out2[-1500:]
        for pk in _AI_KEYS:
            assert pk in out2.split("Gruppe eingeladen", 1)[1][:400], out2
        assert "Abschnitt abgeschlossen:" in out2, (
            f"2+3-Runde muss ueber den freien Harness real schliessen koennen (R7P02-Kernbeleg): {out2[-2000:]}"
        )

        # -- Kernbeleg "regulaerer Gastbeitrag NACH Erstimport" (01_AUFTRAG.md
        # §A, 03_TESTDATEN_UND_PRUEFUNG.md): Testspieler Bs Erstimport laeuft
        # ueber ein eigenes Produktlabel ("...dein Erstbeitrag, mit deinem
        # Save"); ihr spaeterer regulaerer Beitrag erscheint eigenstaendig
        # unter der Tischabsprache ("[Tischabsprache] <ihre ID>: ..."),
        # NICHT nur die Markerzeile. Reihenfolge: Erstimport-Label VOR dem
        # ersten Tischabsprache-Beitrag.
        import_label = "Empfaenger: ueber Leader an Spielleitung (dein Erstbeitrag, mit deinem Save)"
        tisch_b = f"[Tischabsprache] {b_id}:"
        assert import_label in out2, f"Erstimport-Label fuer Testspieler B fehlt: {out2[-1500:]}"
        assert tisch_b in out2, f"kein regulaerer Tischabsprache-Beitrag von Testspieler B: {out2[-2000:]}"
        assert out2.index(import_label) < out2.index(tisch_b), (
            "Reihenfolge verletzt: regulaerer Beitrag darf nicht vor dem Erstimport erscheinen"
        )

        run_dir = data_dir / "run"
        table_id = sup.compute_table_id(leader_id, [b_id, *_AI_KEYS])
        table = core_store.Table.load(run_dir, table_id)
        assert table.status == "closed", table.status
        assert set(table.members) == {leader_id, b_id, *_AI_KEYS}, table.members

        reflections = sup.read_jsonl(run_dir / "reflections.jsonl")
        section_id = f"{table_id}-section"
        human_notes = {
            r["persona_key"]: r.get("text") for r in reflections
            if r.get("kind") == "human_note" and r.get("section_id") == section_id
        }
        assert human_notes.get(leader_id), f"Leader-Abschlussnotiz fehlt: {human_notes}"
        assert human_notes.get(b_id), f"Testspieler-B-Abschlussnotiz fehlt: {human_notes}"
        ai_reflections = {
            r["persona_key"] for r in reflections
            if r.get("kind") == "ai_required_reflection" and r.get("section_id") == section_id
        }
        assert ai_reflections == set(_AI_KEYS), f"KI-Pflichtreflexionen unvollstaendig: {ai_reflections}"

        # R7/W32 (F02-Folgeanpassung): die persona-Einladungen/-Entscheidungen
        # dieser 2+3-Runde laufen in Prozess 2 -- dessen eigener, exklusiver
        # Logordner ist `run-0002` (Prozess 1 hat bereits `run-0001` belegt).
        persona_decisions = sup.read_jsonl(_run_logs_dir(data_dir, 2) / "persona_decision_calls.jsonl")
        decisions = {c["participant_id"]: c["decision"] for c in persona_decisions}
        for pk in _AI_KEYS:
            assert decisions.get(pk) == "accept", f"'{pk}': echte accept-Entscheidung ueber HTTP erwartet: {decisions}"


def test_reject_scenario_blocks_table_formation():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        stdin1 = "\n".join([
            "n", "Standardausruestung Testspieler A (W30-Reject-Beleg).",
            "l persona:medic",
        ]) + "\n"
        p = _run_harness(data_dir, stdin1, extra_args=["--scenario", "reject", "--reject-persona-key", "medic"])
        assert p.returncode == 0, f"Prozess fehlgeschlagen: rc={p.returncode}\n{p.stderr[-2000:]}"
        out = p.stdout
        leader_match = _LEADER_ID_RE.search(out)
        assert leader_match, out[:500]
        leader_id = leader_match.group(1)

        # -- Echte HTTP-Ablehnung, klar der angefragten Persona zugeordnet,
        # UND klar von 'ungueltige Eingabe' unterscheidbar (eigener Text).
        assert "Einladung an 'medic' nicht angenommen (Entscheidung: reject)." in out, out[-1200:]
        assert "nicht alle angefragten Teilnehmer haben zugesagt" in out, out[-1200:]
        assert "Gruppe eingeladen" not in out, (
            "eine echt abgelehnte Einladung darf KEINEN (auch keinen kleineren) Tisch anlegen"
        )

        table_id = sup.compute_table_id(leader_id, ["medic"])
        table_file = data_dir / "run" / "tables" / f"{table_id}.json"
        assert not table_file.exists(), "eine echt abgelehnte Einladung darf keinen Tisch anlegen"

        # R7/W32 (F02-Folgeanpassung): einziger Harness-Prozess in diesem
        # Testfall -- sein exklusiver Logordner ist `run-0001`.
        persona_decisions = sup.read_jsonl(_run_logs_dir(data_dir, 1) / "persona_decision_calls.jsonl")
        assert persona_decisions == [
            {
                "offer_id": sup.invitation_offer_id(leader_id, ["medic"]),
                "participant_id": "medic", "decision": "reject",
            }
        ], persona_decisions


def test_solo_regression_still_closes():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        moves = [f"Solo-Zug-{i}-W30." for i in range(1, 9)]
        stdin1 = "\n".join([
            "n", "Standardausruestung Testspieler A (W30-Solo-Beleg).",
            "l", *moves, "Solo-Notiz-W30.",
        ]) + "\n"
        p = _run_harness(data_dir, stdin1)
        assert p.returncode == 0, f"Prozess fehlgeschlagen: rc={p.returncode}\n{p.stderr[-2000:]}"
        out = p.stdout
        leader_match = _LEADER_ID_RE.search(out)
        assert leader_match, out[:500]
        leader_id = leader_match.group(1)

        assert "Abschnitt abgeschlossen:" in out, (
            f"Solo-Weg muss nach dem W30-Fix weiterhin real schliessen (Regression): {out[-2000:]}"
        )
        table_id = sup.compute_table_id(leader_id, [])
        table = core_store.Table.load(data_dir / "run", table_id)
        assert table.status == "closed", table.status
        assert set(table.members) == {leader_id}, table.members


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
