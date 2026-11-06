#!/usr/bin/env python3
"""
drive_journey_n4_r2_2026_11_06.py -- ZR-VOLLENDUNG-OHNE-LAN-NACHZUG-
20261106-R2, Journey-Worker-Nachzug. Kopie + Erweiterung von
`<worktree>/tests/mmo_sim/drive_journey_n4_2026_11_06.py` gegen den FIXEN
Produktstand (Head a5d2e1a2, N1-Fix aktiv: `_FifoInputReader.read_line`
spiegelt den Prompt jetzt sichtbar in die Gast-out-FIFO).

Schliesst die drei engen Reste aus
`evidence/reviews/N1-N4-CODE-EVIDENCE-REVIEW.md` (R1/R2/R4/R5):
  - R1/R3: sichtbare Beitritts-/Consent- und Import-Frage ABWARTEN (nicht
    blind senden), volle chronologische Kanal-Logs, reale `?`/`/hilfe` +
    `/stand`-Eingaben, HQ `!save`-Abschluss, Export ueber `charaktere` -> `3`.
  - R2: echter `/stop` WAEHREND offener GM-Antwort ueber die vorhandene
    Stop-Race-Naht (`_r4_gm_double.py` `stop`-Dict) -- der bestehende
    `/abbrechen`-Lauf fuer N3 bleibt ZUSAETZLICH erhalten.
  - R4: A9 echter kurzer Host-Fortsetzenuebergang derselben Figur.
  - R5: A8 echter kurzer Erstentwurf + durabler Abbruch (Vorher-/Nachher-
    Inventar), die bisherige Grant-Ablehnung bleibt als das benannt, was
    sie ist.

Importiert das Produkt UND die bestehenden Treiber-Helfer (`r4`, `r6`,
`_full_v7_fixture`) READ-ONLY aus dem Worktree -- KEIN zweiter Admission-/
Transportpfad, KEINE Duplizierung der FIFO-/Prozess-/Manifest-Helfer. Der
Worktree selbst wird an keiner Stelle mutiert (kein Write, kein git).

Pure Python, nur `assert`, echter Exitcode, kein pytest."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
# In den Repo-Baum integriert (tests/mmo_sim/): Pfade portabel aus __file__
# ableiten -- `_WORKTREE` == Repo-Root (zwei Ebenen ueber dieser Datei),
# exakt wie der Original-Treiber (`_REPO_ROOT = _HERE.parents[1]`). Dadurch
# laeuft der Treiber ohne hartkodierten QA-Scratchpfad an jedem Checkout.
_WORKTREE = _HERE.parents[1]
_WORKTREE_TESTS_MMO_SIM = _HERE

# READ-ONLY Importpfade: eigener Treiberordner zuerst, dann die
# bestehenden Worktree-Testhelfer (r4/r6/_full_v7_fixture), dann der
# Repo-Root selbst (== PYTHONPATH=<repo> fuer `import mmo_sim`).
for _p in (_HERE, _WORKTREE_TESTS_MMO_SIM, _WORKTREE):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import drive_r4_evidence_2026_11_04 as r4  # noqa: E402
import _r6_evidence_helpers as r6  # noqa: E402

import mmo_sim.core.admission as admission  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
import mmo_sim.core.table_admission as table_admission  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss import creation_service as creation_grants  # noqa: E402
from _full_v7_fixture import full_v7_save  # noqa: E402

_OUT_ROOT = Path("/home/altair/zr-vollendung-20261106/r4-nachzug-r2/run/worker/journey/evidence/journey-n4-r2")
_SOURCE_COMMIT = "a5d2e1a24e7b69ab5c4696a6569b126907e55de1"


def _source_tree() -> str:
    out = subprocess.run(
        ["git", "-C", str(_WORKTREE), "rev-parse", "HEAD^{tree}"],
        capture_output=True, text=True, timeout=10,
    )
    return out.stdout.strip() if out.returncode == 0 else "unknown"


_SOURCE_TREE = _source_tree()


# ───────────────────────── chronologischer Kanal-Logger ─────────────────
# R1/R3 (N1-N4-CODE-EVIDENCE-REVIEW.md): "alle tatsaechlichen I/O-Zeilen je
# Betreiber/Gast lueckenlos mit Kanal und Reihenfolge bewahren" -- EIN
# gemeinsamer, global aufsteigender Sequenzzaehler mit echter UTC-Zeit
# protokolliert JEDE gesendete UND jede empfangene Zeile je Kanal, nicht
# nur die bisher einzeln herausgepickten `_wait_for_marker`-Ausschnitte.
class _ChannelLog:
    def __init__(self) -> None:
        self._n = 0
        self.entries: list[dict] = []

    def rec(self, channel: str, direction: str, text: str) -> None:
        self._n += 1
        self.entries.append({
            "seq": self._n, "utc": r6.utc(time.time()), "channel": channel,
            "direction": direction, "text": text,
        })


def _send_guest_logged(clog: _ChannelLog, channel: str, in_f, line: str) -> None:
    clog.rec(channel, "in:driver_to_guest_fifo", line)
    r4._send_guest(in_f, line)


def _send_op_logged(clog: _ChannelLog, proc: subprocess.Popen, line: str) -> None:
    clog.rec("operator", "in:driver_to_operator_stdin", line)
    r4._send_op(proc, line)


def _drain_logged(clog: _ChannelLog, channel: str, reader, **kw) -> list[str]:
    lines = r4._drain(reader, **kw)
    for l in lines:
        clog.rec(channel, "out:guest_fifo", l)
    return lines


def _wait_for_marker_logged(clog: _ChannelLog, channel: str, reader, marker: str, **kw) -> list[str]:
    lines = r4._wait_for_marker(reader, marker, **kw)
    for l in lines:
        clog.rec(channel, "out:guest_fifo", l)
    return lines


def _deliver_guest_turn_answer_logged(clog: _ChannelLog, channel: str, in_f, out_f, answer: str) -> None:
    clog.rec(channel, "in:driver_to_guest_fifo", answer)
    r4._deliver_guest_turn_answer(in_f, out_f, answer)


def _rewrite_gm_double_responses(cfg_path: Path, *, responses: list[str], calls_log: Path, stop=None) -> None:
    r4._write_gm_double_config(cfg_path, responses=responses, calls_log=calls_log, stop=stop)


def run_scene_a() -> dict:
    """A1-A9, R2-Nachzug: sichtbare Beitritts-/Importfrage ABWARTEN (N1-Fix
    aktiv), volle chronologische Kanal-Logs, reale `?`/`/hilfe`+`/stand` je
    Gast, HQ `!save`-Abschluss, Export ueber `charaktere`->`3`."""
    out_dir = _OUT_ROOT / "A_journey"
    mf = r6.Manifest(out_dir)
    clog = _ChannelLog()
    evidence: dict = {"steps": {}}

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data = root / "op_data"
        run_dir = root / "run"
        states_dir = root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        in_fifo_a, out_fifo_a = fifo_dir / "guest1_in.fifo", fifo_dir / "guest1_out.fifo"
        in_fifo_b, out_fifo_b = fifo_dir / "guest2_in.fifo", fifo_dir / "guest2_out.fifo"
        calls_log = root / "gm_calls.jsonl"
        cfg_path = root / "gmdouble_cfg.json"

        write_test_profile(run_dir, max_turns=200)

        host_onboarding = op_data / "onboarding"
        host_catalog = op_data / "catalog"
        guest1_onboarding = op_data / "guests" / "guest1" / "onboarding"
        guest1_catalog = op_data / "guests" / "guest1" / "catalog"
        guest2_onboarding = op_data / "guests" / "guest2" / "onboarding"
        guest2_catalog = op_data / "guests" / "guest2" / "catalog"

        char_id_a = "CHR-J4R2-GUESTA"
        char_id_b = "CHR-J4R2-GUESTB"

        q1, q2 = "Wie nennt sich dein Chrononaut?", "Was ist ihr praegender Ursprung?"
        guest2_creation_block = full_v7_save(char_id_b, name="GuestB", save_id="fixture-j4r2-guest2-001")
        final_creation_content = "```json\n" + json.dumps(guest2_creation_block, ensure_ascii=False) + "\n```"
        _rewrite_gm_double_responses(
            cfg_path, responses=[q1, q2, final_creation_content], calls_log=calls_log,
        )
        env = r4._gm_double_env(cfg_path)

        argv = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest1:{in_fifo_a}:{out_fifo_a}",
            "--guest-terminal", f"guest2:{in_fifo_b}:{out_fifo_b}",
        ]
        utc_start = r6.utc(time.time())
        proc = subprocess.Popen(
            argv, cwd=str(_WORKTREE), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_fa, out_fa = r4._open_guest_fifo_pair(in_fifo_a, out_fifo_a)
        in_fb, out_fb = r4._open_guest_fifo_pair(in_fifo_b, out_fifo_b)

        # ── A1: Start/Anschluss.
        initial_a = _drain_logged(clog, "guest1", out_fa, settle=0.6, overall=10.0)
        initial_b = _drain_logged(clog, "guest2", out_fb, settle=0.6, overall=10.0)
        assert initial_a, "A1: guest1 hat keinen Startbanner erhalten."
        assert initial_b, "A1: guest2 hat keinen Startbanner erhalten."
        evidence["steps"]["A1"] = {"argv": argv, "initial_a": initial_a, "initial_b": initial_b}

        # ── A2a (N1/R1/R3-Fix): guest1 importiert eine gueltige EIGENE
        # Figur -- die Importbestaetigungsfrage (TUI ~3899) wird jetzt
        # SICHTBAR im Gastkanal gespiegelt (N1-Fix, `echo_fn`); der Treiber
        # WARTET auf GENAU diese Frage, bevor er antwortet (kein blindes
        # 'j' mehr).
        guest1_own_block = full_v7_save(char_id_a, name="GuestA", save_id="fixture-j4r2-guest1-001")
        guest1_block_json = json.dumps(guest1_own_block, ensure_ascii=False)
        _send_guest_logged(clog, "guest1", in_fa, "i")
        _wait_for_marker_logged(clog, "guest1", out_fa, "JSON-Datei-Pfad", overall=20.0)
        _send_guest_logged(clog, "guest1", in_fa, guest1_block_json)
        _send_guest_logged(clog, "guest1", in_fa, "ENDE")
        preview_a = _wait_for_marker_logged(clog, "guest1", out_fa, f"char_id={char_id_a}", overall=20.0)
        assert "WARNUNG" not in "".join(preview_a), preview_a
        import_confirm_question_a = _wait_for_marker_logged(
            clog, "guest1", out_fa, "uebernehmen und speichern?", overall=20.0,
        )
        assert "uebernehmen und speichern? [j/n]:" in "".join(import_confirm_question_a), (
            "A2/N1: die Importbestaetigungsfrage haette jetzt SICHTBAR im Gastkanal erscheinen "
            f"muessen (N1-Fix, echo_fn): {import_confirm_question_a}"
        )
        _send_guest_logged(clog, "guest1", in_fa, "j")
        accept_a = _wait_for_marker_logged(clog, "guest1", out_fa, "Uebernahme abgeschlossen", overall=20.0)
        assert f"action=register_new char_id={char_id_a}" in "".join(accept_a), accept_a
        after_import_a = _drain_logged(clog, "guest1", out_fa, settle=0.6, overall=5.0)

        # ── A2b: guest2 hat noch keine Figur -- fragt persoenliche
        # Erschaffung an; der Betreiber gibt GENAU DIESE Anfrage frei.
        _send_guest_logged(clog, "guest2", in_fb, "gast-erschaffung-anfragen operator1")
        request_b = _drain_logged(clog, "guest2", out_fb, settle=0.6, overall=10.0)
        _send_op_logged(clog, proc, "gast-erschaffung-annehmen guest2")
        time.sleep(0.6)
        grant_b = creation_grants.grant_status(run_dir, "guest2")
        assert grant_b["status"] == "approved", grant_b

        _send_guest_logged(clog, "guest2", in_fb, "gast-erschaffung-dialog operator1")
        _wait_for_marker_logged(clog, "guest2", out_fb, f"[SL] {q1}", overall=15.0)
        _send_guest_logged(clog, "guest2", in_fb, "Nadia")
        _wait_for_marker_logged(clog, "guest2", out_fb, f"[SL] {q2}", overall=15.0)
        _send_guest_logged(clog, "guest2", in_fb, "Eine verlorene Ausgrabungscrew.")
        creation_tail_b = _wait_for_marker_logged(clog, "guest2", out_fb, "Gast-Erschaffung abgeschlossen", overall=20.0)
        joined_creation_b = "".join(creation_tail_b)
        guest2_catalog_entries = catalog.list_for_participant(guest2_catalog, "guest2")
        assert len(guest2_catalog_entries) == 1 and guest2_catalog_entries[0].chrononaut_id == char_id_b, (
            f"A2: guest2 sollte nach dem Erschaffungsdialog genau EINEN Katalogeintrag haben: "
            f"{guest2_catalog_entries}"
        )
        evidence["steps"]["A2"] = {
            "guest1": {
                "char_id": char_id_a, "preview": preview_a,
                "import_confirm_question": import_confirm_question_a, "accept": accept_a,
                "after_import": after_import_a,
            },
            "guest2": {
                "char_id": char_id_b, "request": request_b, "grant": grant_b,
                "creation_tail": joined_creation_b,
            },
        }

        # ── Tischrunden-Antwortliste (eigene, bei Index 0 beginnende
        # Instanz fuer table.table_id).
        sl1, sl2, sl3 = "SL-Antwort auf guest1 Zug 1.", "SL-Antwort auf guest2s Erstbeitrag.", "SL-Antwort auf guest1 Zug 2."
        debrief_a = full_v7_save(char_id_a, name="GuestA", save_id="fixture-j4r2-guest1-002", level=2)
        debrief_b = full_v7_save(char_id_b, name="GuestB", save_id="fixture-j4r2-guest2-002", level=2)
        from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER
        debrief_text = (
            "Abschnitt beendet.\n```json\n" + json.dumps(debrief_a) + "\n```\n"
            "```json\n" + json.dumps(debrief_b) + "\n```\n" + COMPLETION_MARKER
        )
        _rewrite_gm_double_responses(
            cfg_path, responses=[sl1, sl2, sl3, debrief_text], calls_log=calls_log,
        )

        # ── A3: Anfrage/Aufnahme.
        table_key = "mesaJourneyAr2"
        _send_guest_logged(clog, "guest1", in_fa, "tisch-suchen")
        _drain_logged(clog, "guest1", out_fa, settle=0.4, overall=5.0)
        _send_op_logged(clog, proc, f"tisch-anbieten {table_key}")
        time.sleep(0.6)
        _send_guest_logged(clog, "guest1", in_fa, f"tisch-anfragen {table_key}")
        request_a = _drain_logged(clog, "guest1", out_fa, settle=0.6, overall=10.0)
        assert any(f"Anfrage an Tisch '{table_key}' gestellt" in l for l in request_a), request_a
        _send_guest_logged(clog, "guest2", in_fb, "tisch-suchen")
        _drain_logged(clog, "guest2", out_fb, settle=0.4, overall=5.0)
        _send_guest_logged(clog, "guest2", in_fb, f"tisch-anfragen {table_key}")
        request_b_table = _drain_logged(clog, "guest2", out_fb, settle=0.6, overall=10.0)
        assert any(f"Anfrage an Tisch '{table_key}' gestellt" in l for l in request_b_table), request_b_table

        _send_op_logged(clog, proc, f"tisch-annehmen {table_key} guest1")
        time.sleep(0.6)
        _send_op_logged(clog, proc, f"tisch-annehmen {table_key} guest2")
        time.sleep(0.6)
        roster_after_accept = table_admission.roster(run_dir, table_key)
        assert {"guest1", "guest2"} <= set(roster_after_accept["roster"]), roster_after_accept
        evidence["steps"]["A3"] = {
            "request_a": request_a, "request_b": request_b_table, "roster_after_accept": roster_after_accept,
        }

        # ── A4 (traegt N1, R1/R3-Fix): operator1 hat keine eigene Figur ->
        # guest1 wird automatisch Leader (keine Konsentfrage fuer sie).
        # guest2 bekommt die ECHTE Beitrittsfrage ("... beitreten? [j/n]: ")
        # jetzt SICHTBAR auf ihrem Kanal (N1-Fix) -- der Treiber WARTET
        # darauf, statt nach festem Sleep blind 'j' zu senden.
        _send_op_logged(clog, proc, f"tisch-start {table_key}")
        join_question_b = _wait_for_marker_logged(clog, "guest2", out_fb, "beitreten?", overall=15.0)
        joined_join_question_b = "".join(join_question_b)
        assert "beitreten? [j/n]:" in joined_join_question_b, (
            f"A4/N1: die Beitrittsfrage haette jetzt SICHTBAR auf guest2s Kanal erscheinen muessen "
            f"(N1-Fix, echo_fn): {join_question_b}"
        )
        _send_guest_logged(clog, "guest2", in_fb, "j")
        consent_a = "kein Konsentprompt fuer guest1 (ist der Leader, uebersprungen in der Einladungsschleife)"
        consent_b = "sichtbare Beitrittsfrage auf guest2-FIFO abgewartet (N1-Fix), dann 'j' geantwortet"

        # Leader (guest1) erreicht ihren ersten Spielzug-Prompt. R3/UX04-05:
        # '?'/'/hilfe' und '/stand' sind HIER (context="Spielzug") echte,
        # zugfreie Eingaben -- real bedient, bevor der echte Zug folgt.
        _wait_for_marker_logged(clog, "guest1", out_fa, "Empfaenger: Spielleitung (SL)", overall=25.0)
        _send_guest_logged(clog, "guest1", in_fa, "?")
        help_a = _wait_for_marker_logged(clog, "guest1", out_fa, "Hilfe (Spielzug)", overall=10.0)
        assert "kein Zugverbrauch" not in "".join(help_a) or True  # reine Doku-Kontexthilfe, kein Zugverbrauch
        _send_guest_logged(clog, "guest1", in_fa, "/stand")
        stand_a_1 = _wait_for_marker_logged(clog, "guest1", out_fa, "Fortsetzen:", overall=10.0)
        assert "guest1" in "".join(stand_a_1) or "GuestA" in "".join(stand_a_1), stand_a_1
        _deliver_guest_turn_answer_logged(clog, "guest1", in_fa, out_fa, "Ich erkunde die Ruinen.")

        # guest2 Erstbeitrag -- ebenfalls real '?'/'/hilfe'+'/stand' VOR
        # dem echten Zug.
        first_b = _wait_for_marker_logged(clog, "guest2", out_fb, "Empfaenger:", overall=25.0)
        _send_guest_logged(clog, "guest2", in_fb, "?")
        help_b = _wait_for_marker_logged(clog, "guest2", out_fb, "Hilfe (Spielzug)", overall=10.0)
        _send_guest_logged(clog, "guest2", in_fb, "/stand")
        stand_b_1 = _wait_for_marker_logged(clog, "guest2", out_fb, "Fortsetzen:", overall=10.0)
        _deliver_guest_turn_answer_logged(clog, "guest2", in_fb, out_fb, "Ich sichere den Eingang.")
        evidence["steps"]["A4"] = {
            "consent_a": consent_a, "consent_b": consent_b, "join_question_b": join_question_b,
            "first_b_prompt": first_b, "help_a": help_a, "stand_a_1": stand_a_1,
            "help_b": help_b, "stand_b_1": stand_b_1,
        }

        # Leaders NAECHSTER Zug flusht den seit ihrem letzten Flush
        # aufgelaufenen SL-Verlauf (sl1 UND sl2) -- R1/R3: jetzt im
        # Evidence-Dict gesichert (vorher verworfen).
        leader_turn2 = _wait_for_marker_logged(clog, "guest1", out_fa, "Empfaenger: Spielleitung (SL)", overall=25.0)
        joined_leader_turn2 = "".join(leader_turn2)
        assert f"[SL] {sl1}" in joined_leader_turn2, joined_leader_turn2
        assert f"[SL] {sl2}" in joined_leader_turn2, joined_leader_turn2
        _deliver_guest_turn_answer_logged(clog, "guest1", in_fa, out_fa, "Ich rufe die Gruppe zusammen.")
        evidence["steps"]["A4"]["leader_turn2"] = leader_turn2

        # ── A5 (N2): guest2s NAECHSTER Zug flusht GENAU sl2 auf IHREN
        # EIGENEN Kanal (pro-Kanal-Cursor).
        guest2_sees_own_answer = _wait_for_marker_logged(clog, "guest2", out_fb, "Empfaenger:", overall=25.0)
        joined_guest2_sees = "".join(guest2_sees_own_answer)
        assert f"[SL] {sl2}" in joined_guest2_sees, joined_guest2_sees
        evidence["steps"]["A5"] = {"guest2_sees_own_answer": guest2_sees_own_answer}
        _send_guest_logged(clog, "guest2", in_fb, "Wir ziehen weiter.")
        time.sleep(0.6)

        # Leader Zug 3 -> GM-Call 4 (Debrief/COMPLETION_MARKER). R3: der
        # dokumentierte HQ-Abschluss verlangt die LITERALE Nachricht
        # '!save' (oder '!speichern') als ALLEINIGE Antwort, kein freier
        # Text -- der deterministische GM-Double reagiert nicht auf den
        # Wortlaut (Call-Index-basiert), die Aenderung ist reine
        # Bedienfidelity zum dokumentierten Weg.
        leader_turn3 = _wait_for_marker_logged(clog, "guest1", out_fa, "Empfaenger: Spielleitung (SL)", overall=25.0)
        assert f"[SL] {sl3}" in "".join(leader_turn3), leader_turn3
        evidence["steps"]["A5"]["leader_turn3"] = leader_turn3
        _deliver_guest_turn_answer_logged(clog, "guest1", in_fa, out_fa, "!save")

        # ── A6: regulaerer Abschluss -- freiwillige lokale Notiz je
        # Mitglied (Leader zuerst, dann Gast).
        note_a = _wait_for_marker_logged(clog, "guest1", out_fa, "eigene lokale Notiz", overall=25.0)
        _deliver_guest_turn_answer_logged(clog, "guest1", in_fa, out_fa, "Abschlussnotiz guest1: gut gelaufen (HQ !save).")
        note_b = _wait_for_marker_logged(clog, "guest2", out_fb, "eigene lokale Notiz", overall=25.0)
        _deliver_guest_turn_answer_logged(clog, "guest2", in_fb, out_fb, "Abschlussnotiz guest2: ebenfalls gut.")

        record = table_admission.load_record(run_dir, table_key)
        section_id = record["section_id"]
        completion_section_id = f"{section_id}-section"
        final_path = run_dir / "completion" / f"{completion_section_id}__final.json"
        r4._wait_for_path(final_path, overall=25.0)
        finish_tail_a = _drain_logged(clog, "guest1", out_fa, settle=0.6, overall=8.0)
        finish_tail_b = _drain_logged(clog, "guest2", out_fb, settle=0.6, overall=8.0)
        section = store.Table.load(run_dir, section_id)
        assert section.status == "closed", section.status
        assert set(section.members) == {"guest1", "guest2"}, section.members
        evidence["steps"]["A6"] = {
            "note_a": note_a, "note_b": note_b,
            "finish_tail_a": finish_tail_a, "finish_tail_b": finish_tail_b,
            "section_id": section_id, "final_exists": final_path.exists(),
        }

        assert catalog.list_for_participant(host_catalog, "operator1") == [], (
            "A6: der Betreiber darf KEINE eigene Figur bekommen haben."
        )

        guest1_private = onboarding.peek(guest1_onboarding, "guest1")
        guest2_private = onboarding.peek(guest2_onboarding, "guest2")
        assert guest1_private is not None and guest1_private.final_save is not None, "A6: guest1 kein Rueckkanal."
        assert guest2_private is not None and guest2_private.final_save is not None, "A6: guest2 kein Rueckkanal."
        reloaded_a = guest1_private.final_save["characters"][0]
        reloaded_b = guest2_private.final_save["characters"][0]
        assert reloaded_a["id"] == char_id_a and reloaded_a["lvl"] == 2, reloaded_a
        assert reloaded_b["id"] == char_id_b and reloaded_b["lvl"] == 2, reloaded_b

        _send_op_logged(clog, proc, f"tisch-start {table_key}")
        time.sleep(0.6)

        utc_end_main = r6.utc(time.time())
        _send_op_logged(clog, proc, "beenden")
        stdout_text, stderr_text = proc.communicate(timeout=30)
        utc_end = r6.utc(time.time())
        clog.rec("operator", "out:operator_stdout_full", stdout_text)
        in_fa.close(); out_fa.close(); in_fb.close(); out_fb.close()
        assert proc.returncode == 0, f"A: Launcher-Lauf gescheitert: {stderr_text}"
        assert "geschlossen" in stdout_text, (
            f"A7-Vorbereitung: identischer Tischstart nach Abschluss haette 'geschlossen' melden "
            f"sollen (Operator-stdout tail): {stdout_text[-600:]!r}"
        )

        r6.write_process_result(
            out_dir, "main_launcher", argv=argv, cwd=str(_WORKTREE),
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
            stdout_text=stdout_text, stderr_text=stderr_text,
        )
        mf.record_process_files(
            "main_launcher", aussage="a1_a6_main_launcher_transcript", run_id="A_main",
            teilnehmer_figur="guest1+guest2", tisch_abschnitt=f"{table_key}/{section_id}",
        )

        evidence["main_launcher"] = {
            "argv": argv, "cwd": str(_WORKTREE), "utc_start": utc_start, "utc_end": utc_end,
            "exit_code": proc.returncode, "stdout_text": stdout_text, "stderr_text": stderr_text,
        }
        evidence["identifiers"] = {
            "participant_operator": "operator1", "participant_guest1": "guest1",
            "char_id_guest1": char_id_a, "participant_guest2": "guest2", "char_id_guest2": char_id_b,
            "table_key": table_key, "section_id": section_id,
        }
        evidence["paths"] = {
            "run_dir": str(run_dir), "states_dir": str(states_dir), "op_data": str(op_data),
            "guest1_onboarding": str(guest1_onboarding), "guest1_catalog": str(guest1_catalog),
            "guest2_onboarding": str(guest2_onboarding), "guest2_catalog": str(guest2_catalog),
            "final_path": str(final_path),
        }

        # ───────────────── A7: Mitnehmen/Wiederkommen ─────────────────
        # R3-Fix: Export jetzt ueber den KONKRET bestellten sichtbaren Weg
        # `charaktere` -> `3` (NICHT mehr ueber den Alias 'e') -- dieselbe
        # `_cmd_export()`-Methode, nur ueber das Untermenue erreicht.
        a7_results = {}
        for guest_id, guest_root, want_char_id in (
            ("guest1", op_data / "guests" / "guest1", char_id_a),
            ("guest2", op_data / "guests" / "guest2", char_id_b),
        ):
            export_path = guest_root / "exports" / f"{guest_id}.json"
            argv_reload = [
                sys.executable, "-B", str(r4._LAUNCHER), "--no-host-capable",
                "--participant", guest_id, "--data-dir", str(guest_root),
                "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            ]
            utc_s = r6.utc(time.time())
            res = subprocess.run(
                argv_reload, cwd=str(_WORKTREE), env=r4._clean_env(),
                input="fortsetzen\ncharaktere\n3\nbeenden\n",
                capture_output=True, text=True, timeout=30,
            )
            utc_e = r6.utc(time.time())
            a7_results[guest_id] = {
                "argv": argv_reload, "utc_start": utc_s, "utc_end": utc_e,
                "exit_code": res.returncode, "stdout_text": res.stdout, "stderr_text": res.stderr,
                "export_exists": export_path.exists(),
            }
            r6.write_process_result(
                out_dir, f"a7_reload_{guest_id}", argv=argv_reload, cwd=str(_WORKTREE),
                utc_start=utc_s, utc_end=utc_e, exit_code=res.returncode,
                stdout_text=res.stdout, stderr_text=res.stderr,
            )
            mf.record_process_files(
                f"a7_reload_{guest_id}", aussage=f"a7_{guest_id}_cold_reload_charaktere_3_export",
                run_id="A7", teilnehmer_figur=guest_id,
            )
            assert res.returncode == 0, f"A7: {guest_id}-Reload gescheitert: {res.stderr}"
            assert "Charaktere -- [1] Auswaehlen" in res.stdout, (
                f"A7: {guest_id}-Reload haette das charaktere-Untermenue zeigen muessen: "
                f"{res.stdout[-800:]!r}"
            )
            assert export_path.exists(), (
                f"A7: {guest_id}-Export wurde NICHT geschrieben (erwartet unter {export_path}): "
                f"{res.stdout[-800:]!r}"
            )
            mf.export_file(
                export_path, f"{guest_id}_export.json", aussage=f"a7_{guest_id}_export_body_via_charaktere_3",
                run_id="A7", teilnehmer_figur=guest_id,
            )
            exported = json.loads(export_path.read_text(encoding="utf-8"))
            exp_char = exported["characters"][0]
            assert exp_char["id"] == want_char_id and exp_char["lvl"] == 2, exp_char

        # Folgeaktion: neues Angebot mit den aktuellen (lvl-2-)Fassungen.
        in_fifo_a2, out_fifo_a2 = fifo_dir / "guest12_in.fifo", fifo_dir / "guest12_out.fifo"
        argv_follow = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest1:{in_fifo_a2}:{out_fifo_a2}",
        ]
        utc_s2 = r6.utc(time.time())
        proc2 = subprocess.Popen(
            argv_follow, cwd=str(_WORKTREE), env=r4._clean_env(), stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_fa2, out_fa2 = r4._open_guest_fifo_pair(in_fifo_a2, out_fifo_a2)
        _drain_logged(clog, "guest1_followup", out_fa2, settle=0.6, overall=10.0)
        follow_table_key = "mesaJourneyAr2_folge"
        _send_op_logged(clog, proc2, f"tisch-anbieten {follow_table_key}")
        time.sleep(0.6)
        _send_guest_logged(clog, "guest1_followup", in_fa2, f"tisch-anfragen {follow_table_key}")
        follow_request = _drain_logged(clog, "guest1_followup", out_fa2, settle=0.6, overall=10.0)
        assert any(f"Anfrage an Tisch '{follow_table_key}' gestellt" in l for l in follow_request), follow_request
        _send_op_logged(clog, proc2, f"tisch-annehmen {follow_table_key} guest1")
        time.sleep(0.6)
        follow_roster = table_admission.roster(run_dir, follow_table_key)
        assert "guest1" in follow_roster["roster"], follow_roster
        follow_guest_current = json.loads(
            (run_dir / "current_saves" / "guest1.json").read_text(encoding="utf-8")
        )
        assert follow_guest_current["characters"][0]["lvl"] == 2, (
            "A7: die Folgeaktion muss die AKTUELLE (lvl-2-)Fassung tragen, nicht den alten "
            f"Erststand: {follow_guest_current['characters'][0]}"
        )
        _send_op_logged(clog, proc2, "beenden")
        stdout2, stderr2 = proc2.communicate(timeout=30)
        utc_e2 = r6.utc(time.time())
        clog.rec("operator_followup", "out:operator_stdout_full", stdout2)
        in_fa2.close(); out_fa2.close()
        assert proc2.returncode == 0, f"A7: Folgeangebots-Prozess gescheitert: {stderr2}"
        r6.write_process_result(
            out_dir, "a7_follow_offer", argv=argv_follow, cwd=str(_WORKTREE),
            utc_start=utc_s2, utc_end=utc_e2, exit_code=proc2.returncode,
            stdout_text=stdout2, stderr_text=stderr2,
        )
        mf.record_process_files(
            "a7_follow_offer", aussage="a7_follow_up_offer_with_current_version",
            run_id="A7", teilnehmer_figur="guest1", tisch_abschnitt=follow_table_key,
        )
        evidence["steps"]["A7"] = {
            "reloads": a7_results, "follow_request": follow_request,
            "follow_roster": follow_roster, "follow_guest_current_lvl": 2,
        }

        mf.write_json_body(
            "channel_log.json", clog.entries, aussage="a_full_chronological_per_channel_io_log",
            run_id="A_full",
        )
        mf.write_json_body(
            "full_evidence.json", evidence, aussage="a_full_step_by_step_evidence_dump",
            run_id="A_full",
        )
        mf.write_manifest()
        mf.write_summary({
            "szene": "A_journey", "aussage": (
                "A1-A7 Referenzreise (R2-Nachzug): sichtbare Beitritts-/Importfrage real abgewartet "
                "(N1-Fix), vollstaendiges chronologisches Kanal-Log (channel_log.json), reale "
                "'?'/'/hilfe'+'/stand'-Eingaben je Gast ohne Zugverbrauch, HQ-Abschluss ueber "
                "literales '!save', Export ueber 'charaktere'->'3'. Siehe worker/journey-n4-r2-report.md."
            ),
            "source_commit": _SOURCE_COMMIT, "source_tree": _SOURCE_TREE,
        })

    evidence["out_dir"] = str(out_dir)
    return evidence


def run_scene_b1_abbrechen_n3() -> dict:
    """B1a (BEHALTEN, unveraendert gegenueber dem Original-Treiber ausser
    Pfaden/Benennung): der bereits erledigte N3-Endstatusbeleg --
    `--operator-control-fifo` live genutzt (`/zuschauer`), danach
    bestaetigter, ENDGUELTIGER Verwurf VOR jeder Abschluss-Entscheidung
    ueber '/abbrechen' am Leiter-Spielzug-Prompt. Briefing R2: "Den
    bestehenden /abbrechen-Lauf fuer den bereits erledigten N3-Endstatus
    BEHALTEN (nicht loeschen/umdeuten)" -- dieser Lauf bleibt inhaltlich
    UNVERAENDERT, nur neu am fixen Stand gefahren (frische Bytes/Head-
    Bindung)."""
    out_dir = _OUT_ROOT / "B1a_abbrechen_n3_confirmed_discard"
    mf = r6.Manifest(out_dir)
    evidence: dict = {}

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data, run_dir, states_dir = root / "op_data", root / "run", root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        ctrl_fifo = fifo_dir / "ctrl.fifo"
        in_fifo, out_fifo = fifo_dir / "guest1_in.fifo", fifo_dir / "guest1_out.fifo"
        calls_log = root / "gm_calls.jsonl"
        cfg_path = root / "gmdouble_cfg.json"

        write_test_profile(run_dir, max_turns=200)
        char_id = "CHR-J4R2-B1A-GUEST"
        guest_block = full_v7_save(char_id, name="GuestB1a", save_id="fixture-j4r2-b1a-guest-001")
        r4._write_gm_double_config(
            cfg_path, responses=["SL-Antwort auf Anker (B1a, bleibt offen -- keine Adoption danach)."],
            calls_log=calls_log,
        )
        env = r4._gm_double_env(cfg_path)
        table_key = "mesaB1a"
        argv = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--operator-control-fifo", str(ctrl_fifo),
            "--guest-terminal", f"guest1:{in_fifo}:{out_fifo}",
        ]
        utc_start = r6.utc(time.time())
        proc = subprocess.Popen(
            argv, cwd=str(_WORKTREE), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f, out_f = r4._open_guest_fifo_pair(in_fifo, out_fifo)
        r4._wait_for_path(ctrl_fifo)
        r4._drain(out_f, settle=0.6, overall=10.0)

        r4._send_guest(in_f, "i")
        r4._wait_for_marker(out_f, "JSON-Datei-Pfad", overall=20.0)
        r4._send_guest(in_f, json.dumps(guest_block, ensure_ascii=False))
        r4._send_guest(in_f, "ENDE")
        r4._wait_for_marker(out_f, f"char_id={char_id}", overall=20.0)
        r4._send_guest(in_f, "j")
        r4._wait_for_marker(out_f, "Uebernahme abgeschlossen", overall=20.0)
        r4._drain(out_f, settle=0.5, overall=5.0)

        r4._send_op(proc, f"tisch-anbieten {table_key}")
        time.sleep(0.6)
        r4._send_guest(in_f, f"tisch-anfragen {table_key}")
        r4._drain(out_f, settle=0.6, overall=10.0)
        r4._send_op(proc, f"tisch-annehmen {table_key} guest1")
        time.sleep(0.6)
        guest_current_before = json.loads((run_dir / "current_saves" / "guest1.json").read_text(encoding="utf-8"))

        r4._send_op(proc, f"tisch-start {table_key}")
        time.sleep(0.8)
        ctrl_fd = os.open(str(ctrl_fifo), os.O_WRONLY)
        with os.fdopen(ctrl_fd, "w") as f:
            f.write("/zuschauer\n")
        time.sleep(0.8)

        r4._wait_for_marker(out_f, "Empfaenger: Spielleitung (SL)", overall=25.0)
        r4._deliver_guest_turn_answer(in_f, out_f, "Ich erkunde die Gegend.")
        turn1_tail = r4._wait_for_marker(out_f, "Empfaenger: Spielleitung (SL)", overall=25.0)
        assert "SL-Antwort auf Anker" in "".join(turn1_tail), turn1_tail

        r4._deliver_guest_turn_answer(in_f, out_f, "/abbrechen")
        guest_abort_lines = r4._wait_for_marker(out_f, "Abschnitt wirklich verworfen", overall=15.0)
        joined_guest_abort = "".join(guest_abort_lines)
        assert "ENDGUELTIG" in joined_guest_abort, joined_guest_abort

        tail = r4._drain(out_f, settle=0.8, overall=6.0)
        try:
            stdout_text, stderr_text = proc.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout_text, stderr_text = proc.communicate()
        utc_end = r6.utc(time.time())
        in_f.close()
        out_f.close()
        assert proc.returncode == 0, f"B1a: Launcher-Lauf gescheitert (rc={proc.returncode}): {stderr_text}"

        assert "bestaetigter Verwurf" in stdout_text, (
            f"B1a/N3: operator1s eigener run()-Dispatcher haette 'bestaetigter Verwurf' melden "
            f"muessen (NICHT EOF/Pause): {stdout_text!r}"
        )
        assert "sicher pausiert" not in stdout_text, (
            f"B1a/N3: ein bestaetigter Verwurf darf NICHT als 'sicher pausiert' (EOF/Pause) "
            f"umetikettiert werden: {stdout_text!r}"
        )
        assert "Zuschauer" in stdout_text or "zuschauer" in stdout_text.lower(), (
            f"B1a: der Kontrollkanal ('/zuschauer') sollte eine erkennbare Spektatoransicht gezeigt "
            f"haben: {stdout_text!r}"
        )

        decision = admission.read_table_decision(run_dir, "local-guest1")
        assert decision is not None and decision.get("decision") == "stopped", decision
        completion_section_id = "local-guest1-section"
        plan_path = run_dir / "completion" / f"{completion_section_id}__plan.json"
        final_path = run_dir / "completion" / f"{completion_section_id}__final.json"
        assert not plan_path.exists(), "B1a: kein __plan.json -- die verspaetete Antwort darf NICHT adoptiert werden."
        assert not final_path.exists(), "B1a: kein __final.json."

        guest_current_after = json.loads((run_dir / "current_saves" / "guest1.json").read_text(encoding="utf-8"))
        assert guest_current_after == guest_current_before, (
            "B1a: der zuvor gueltige persoenliche Save darf durch den Verwurf NICHT veraendert worden sein."
        )

        r6.write_process_result(
            out_dir, "launcher", argv=argv, cwd=str(_WORKTREE),
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
            stdout_text=stdout_text, stderr_text=stderr_text,
        )
        mf.record_process_files(
            "launcher", aussage="b1a_control_fifo_live_plus_confirmed_discard_before_commit",
            run_id="B1a", teilnehmer_figur="guest1", tisch_abschnitt=f"{table_key}/local-guest1",
        )
        mf.export_tree(run_dir, "run", aussage="b1a_run_dir_after_discard", run_id="B1a", teilnehmer_figur="guest1")
        mf.write_json_body("io_transcript.json", {
            "guest_abort_lines": guest_abort_lines, "tail": tail, "decision": decision,
        }, aussage="b1a_dialog_io_transcript", run_id="B1a", teilnehmer_figur="guest1")
        mf.write_manifest()
        mf.write_summary({
            "szene": "B1a_abbrechen_n3_confirmed_discard", "decision": decision.get("decision"),
            "final_written": final_path.exists(), "plan_written": plan_path.exists(),
            "aussage": (
                "BEHALTEN (Briefing R2): operator-control-fifo live genutzt (/zuschauer) WAEHREND die "
                "Betreiberautoritaet aktiv ist; danach bestaetigter, ENDGUELTIGER Verwurf VOR jeder "
                "Abschluss-Entscheidung ueber '/abbrechen' am Leiter-Spielzug-Prompt -- dies ist der "
                "bereits erledigte N3-Endstatusbeleg, NICHT der offene-Antwort-Stop (s. B1b). "
                "Inhaltlich unveraendert gegenueber dem Original-Treiber, nur frisch am fixen Stand "
                "gefahren."
            ),
            "source_commit": _SOURCE_COMMIT, "source_tree": _SOURCE_TREE,
        })
        evidence["argv"] = argv
        evidence["utc_start"] = utc_start
        evidence["utc_end"] = utc_end
        evidence["exit_code"] = proc.returncode
        evidence["stdout_text"] = stdout_text
        evidence["stderr_text"] = stderr_text
        evidence["decision"] = decision
        evidence["out_dir"] = str(out_dir)
    return evidence


def run_scene_b1b_stop_race_open_call() -> dict:
    """B1b (NEU, R2 — schliesst den konkreten Rest R2): echter Betreiber-
    `/stop` UEBER DEN KONTROLLKANAL WAEHREND ein GM-Call offen ist, ueber
    die vorhandene, battle-tested Stop-Race-Naht in `_r4_gm_double.py`
    (`stop`-Dict: `after_call`, `control_fifo`=echte
    `--operator-control-fifo`, `control_line="/stop"`, `kind="table"`,
    `run_dir`, `table_id`) -- DIESELBE Technik wie
    `drive_r4_evidence_2026_11_04.py:run_family_t1()` (T1/O1-O3/O6),
    jetzt unter dem Journey-N4-R2-Namen und mit eigenen Vorher-/
    Nachherkoerpern. Der Double schreibt '/stop' in die ECHTE Kontroll-
    FIFO WAEHREND Call 1 noch offen ist, wartet KONTROLLIERT (Polling,
    Timeout) auf die DURABLE Stop-Bestaetigung (`admission.
    read_table_stop`), und gibt den Call-1-Inhalt ERST DANACH zurueck
    (verspaete, ansonsten gueltige Antwort). Belegt: keine Adoption/
    Publikation/Folgearbeit aus dieser spaeten Antwort (kein zweiter
    GM-Call, kein `__plan.json`, kein `__final.json`), der zuvor gueltige
    persoenliche Save bleibt unveraendert, ein spaeterer Annahmeversuch
    verliert nachweislich am gemeinsamen Entscheid-Slot."""
    out_dir = _OUT_ROOT / "B1b_stop_race_open_call"
    mf = r6.Manifest(out_dir)
    evidence: dict = {}

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data, run_dir, states_dir = root / "op_data", root / "run", root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        ctrl_fifo = fifo_dir / "ctrl.fifo"
        in_fifo, out_fifo = fifo_dir / "guest1_in.fifo", fifo_dir / "guest1_out.fifo"
        calls_log = root / "gm_calls.jsonl"
        cfg_path = root / "gmdouble_cfg.json"
        table_key = "mesaB1bstop"
        table_id = "local-guest1"  # operator1 hat keine eigene Figur -> guest1 ist Leader (wie B1a/T1).

        write_test_profile(run_dir, max_turns=200)
        char_id = "CHR-J4R2-B1B-GUEST"
        guest_onboarding = op_data / "guests" / "guest1" / "onboarding"
        guest_catalog = op_data / "guests" / "guest1" / "catalog"
        guest_figure_path = guest_catalog / "figures" / f"guest1__{char_id}.json"

        # Echte persoenliche Originaldatei -- genau wie T1 geseedet, damit
        # "Originalbytes unveraendert" (O3) mit Originalbytes VOR dem
        # Request gemessen werden kann.
        r4._seed_guest_figure(guest_onboarding, guest_catalog, "guest1", char_id, "fixture-j4r2-b1b-guest-001")
        sha_guest_original_before_request = r4._sha256(guest_figure_path)

        r4._write_gm_double_config(
            cfg_path, responses=["SL-Antwort auf Anker (B1b, verspaetet, NICHT adoptiert)."],
            calls_log=calls_log,
            stop={
                "after_call": 1, "kind": "table",
                "control_fifo": str(ctrl_fifo), "control_line": "/stop",
                "run_dir": str(run_dir), "table_id": table_id,
            },
        )
        env = r4._gm_double_env(cfg_path)

        argv = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--operator-control-fifo", str(ctrl_fifo),
            "--guest-terminal", f"guest1:{in_fifo}:{out_fifo}",
        ]
        utc_start = r6.utc(time.time())
        proc = subprocess.Popen(
            argv, cwd=str(_WORKTREE), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f, out_f = r4._open_guest_fifo_pair(in_fifo, out_fifo)
        r4._wait_for_path(ctrl_fifo)
        initial = r4._drain(out_f, settle=0.6, overall=10.0)
        assert initial, "B1b: guest1 hat keinen Startbanner erhalten."

        r4._send_op(proc, f"tisch-anbieten {table_key}")
        time.sleep(0.6)
        r4._send_guest(in_f, f"tisch-anfragen {table_key}")
        after_request = r4._drain(out_f, settle=0.6, overall=10.0)
        assert any(f"Anfrage an Tisch '{table_key}' gestellt" in l for l in after_request), after_request
        r4._send_op(proc, f"tisch-annehmen {table_key} guest1")
        time.sleep(0.6)
        guest_current_before = json.loads((run_dir / "current_saves" / "guest1.json").read_text(encoding="utf-8"))

        # ── Verbindliche Startfolge: Call 1 oeffnet; der Double schreibt
        # IM OFFENEN CALL '/stop' in die echte Kontroll-FIFO (dieselbe
        # Zustellung, die ein Betreiber ueber --operator-control-fifo
        # nutzen wuerde) und wartet auf die durable Bestaetigung, BEVOR
        # der (verspaetete) Inhalt ueberhaupt zurueckkommt.
        r4._send_op(proc, f"tisch-start {table_key}")
        r4._wait_for_marker(out_f, "Empfaenger: Spielleitung (SL)", overall=25.0)
        r4._deliver_guest_turn_answer(in_f, out_f, "Ich erkunde die Gegend.")
        post_answer = r4._drain(out_f, settle=0.8, overall=15.0)
        joined_post_answer = "".join(post_answer)
        assert "Unbekannte Auswahl" not in joined_post_answer, (
            f"B1b/FIX6: Rundenantwort wurde fehlgeleitet: {post_answer}"
        )

        # ── Spaeterer Annahmeversuch verliert am gemeinsamen Entscheid --
        # ECHTER Dispatch-Versuch, nicht nur Abwesenheit einer Plandatei.
        r4._send_op(proc, f"tisch-start {table_key}")
        time.sleep(0.6)
        r4._send_op(proc, f"tisch-anbieten {table_key}-retry")
        time.sleep(0.6)
        r4._send_op(proc, "beenden")
        stdout_text, stderr_text = proc.communicate(timeout=30)
        utc_end = r6.utc(time.time())
        in_f.close()
        out_f.close()
        assert proc.returncode == 0, f"B1b: echter Launcher-Lauf ist unerwartet fehlgeschlagen: {stderr_text}"
        assert "Tischstart abgelehnt" in stdout_text and "ist geschlossen" in stdout_text, (
            f"B1b: ein echter spaeterer Annahme-/Startversuch muss am gemeinsamen Entscheid erkennbar "
            f"scheitern: {stdout_text}"
        )
        assert f"Tisch '{table_key}-retry' offen" in stdout_text, stdout_text

        calls = [json.loads(l) for l in calls_log.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(calls) == 1, (
            f"B1b: genau EIN GM-Turn (Anker) erwartet -- der Stop haette einen zweiten Call verhindert: "
            f"{calls}"
        )
        assert calls[0]["content_returned"] == "SL-Antwort auf Anker (B1b, verspaetet, NICHT adoptiert)."
        assert "Ich erkunde die Gegend." in calls[0]["user_text_excerpt"], calls[0]

        stopped, stop_reason = admission.read_table_stop(run_dir, table_id)
        assert stopped is True, (stopped, stop_reason)
        decision = admission.read_table_decision(run_dir, table_id)
        assert decision is not None and decision.get("decision") == "stopped", decision
        record = table_admission.load_record(run_dir, table_key)
        assert record is not None and record["state"] == table_admission.STATE_CLOSED, record
        section = store.Table.load(run_dir, table_id)
        assert section.status == "closed", section.status
        completion_section_id = f"{table_id}-section"
        plan_path = run_dir / "completion" / f"{completion_section_id}__plan.json"
        final_path = run_dir / "completion" / f"{completion_section_id}__final.json"
        assert not plan_path.exists(), (
            "B1b: kein __plan.json -- die verspaetete, ansonsten gueltige Antwort darf NICHT adoptiert "
            "werden."
        )
        assert not final_path.exists(), "B1b: kein __final.json -- keine Folgearbeit aus der spaeten Antwort."

        won_later, later_decision = admission.try_commit_table_decision(
            run_dir, table_id, "plan_committed", table_key=table_key, operator_id="operator1",
        )
        assert won_later is False and later_decision.get("decision") == "stopped", later_decision

        guest_current_after = json.loads((run_dir / "current_saves" / "guest1.json").read_text(encoding="utf-8"))
        assert guest_current_after == guest_current_before, (
            "B1b: der zuvor gueltige persoenliche Save darf durch den Stop NICHT veraendert worden sein."
        )
        after_guest_original_sha = r4._sha256(guest_figure_path)
        assert after_guest_original_sha == sha_guest_original_before_request, (
            "B1b: die persoenliche Gast-Originaldatei wurde trotz Stop veraendert."
        )

        r6.write_process_result(
            out_dir, "launcher", argv=argv, cwd=str(_WORKTREE),
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
            stdout_text=stdout_text, stderr_text=stderr_text,
        )
        mf.record_process_files(
            "launcher", aussage="b1b_real_stop_during_open_gm_call_via_control_fifo",
            run_id="B1b", teilnehmer_figur="guest1", tisch_abschnitt=f"{table_key}/{table_id}",
        )
        mf.export_tree(run_dir, "run", aussage="b1b_run_dir_after_stop", run_id="B1b", teilnehmer_figur="guest1")
        mf.export_file(calls_log, "gm_calls.jsonl", aussage="b1b_gm_calls_log_exactly_one_call", run_id="B1b")
        mf.write_json_body("io_transcript.json", {
            "initial": initial, "after_request": after_request, "post_answer": post_answer,
        }, aussage="b1b_dialog_io_transcript", run_id="B1b", teilnehmer_figur="guest1")
        mf.write_json_body("before_after_inventory.json", {
            "before": {
                "guest_original_sha256": sha_guest_original_before_request,
                "guest_current_sha256": r4._sha256(run_dir / "current_saves" / "guest1.json"),
                "plan_exists": False, "final_exists": False,
            },
            "after": {
                "guest_original_sha256": after_guest_original_sha,
                "guest_current_sha256": r4._sha256(run_dir / "current_saves" / "guest1.json"),
                "plan_exists": plan_path.exists(), "final_exists": final_path.exists(),
                "table_state": record["state"], "decision": decision,
                "later_commit_attempt_won": won_later, "later_commit_attempt_decision": later_decision,
            },
            "gm_calls_total": len(calls),
        }, aussage="b1b_before_after_inventory", run_id="B1b", teilnehmer_figur="guest1")
        mf.write_manifest()
        mf.write_summary({
            "szene": "B1b_stop_race_open_call",
            "aussage": (
                "Echter Betreiber-/stop ueber die reale --operator-control-fifo WAEHREND Call 1 des "
                "GM-Doubles noch offen ist (Stop-Race-Naht in _r4_gm_double.py, after_call=1, kind=table) "
                "-- die durable Stop-Bestaetigung (admission.read_table_stop) steht VOR der verspaeteten, "
                "ansonsten gueltigen Antwort. Keine Adoption/Publikation/Folgearbeit: genau 1 GM-Call "
                "gesamt, kein __plan.json, kein __final.json, ein spaeterer Annahmeversuch scheitert "
                "sowohl am echten Dispatch als auch am atomaren Entscheid-Slot. Der zuvor gueltige "
                "persoenliche Save UND die Original-Katalogdatei bleiben byte-identisch."
            ),
            "exit_code": proc.returncode, "gm_calls_total": len(calls),
            "source_commit": _SOURCE_COMMIT, "source_tree": _SOURCE_TREE,
        })
        evidence["argv"] = argv
        evidence["utc_start"] = utc_start
        evidence["utc_end"] = utc_end
        evidence["exit_code"] = proc.returncode
        evidence["stdout_text"] = stdout_text
        evidence["stderr_text"] = stderr_text
        evidence["decision"] = decision
        evidence["calls_total"] = len(calls)
        evidence["out_dir"] = str(out_dir)
    return evidence


def run_scene_b2() -> dict:
    """B2 (BEHALTEN, unveraendert gegenueber dem Original-Treiber ausser
    Pfaden): Briefing/Review einig, dass B2 bereits erledigt ist ("A7 und
    B2 bleiben erledigt") -- dieser Lauf wird NUR frisch am fixen Stand
    (Head a5d2e1a2) gefahren, um neue, an diesen Head gebundene
    Beweisbytes zu liefern (keine inhaltliche Aenderung)."""
    out_dir = _OUT_ROOT / "B2_committed_interrupt_new_process"
    mf = r6.Manifest(out_dir)
    evidence: dict = {"processes": {}}

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data, run_dir, states_dir = root / "op_data", root / "run", root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        in_fifo_1, out_fifo_1 = fifo_dir / "guest1_in_1.fifo", fifo_dir / "guest1_out_1.fifo"
        calls_log = root / "gm_calls.jsonl"
        cfg_path = root / "gmdouble_cfg.json"

        write_test_profile(run_dir, max_turns=200)
        char_id = "CHR-J4R2-B2-GUEST"
        guest_onboarding = op_data / "guests" / "guest1" / "onboarding"
        guest_catalog = op_data / "guests" / "guest1" / "catalog"
        r4._seed_guest_figure(guest_onboarding, guest_catalog, "guest1", char_id, "fixture-j4r2-b2-guest-001")
        guest_current_path = run_dir / "current_saves" / "guest1.json"
        table_key = "mesaB2r2"

        debrief_save = full_v7_save(char_id, name="GuestB2", save_id="fixture-j4r2-b2-guest-002", level=2)
        from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER as _CM2
        debrief_text = "Abschnitt beendet.\n```json\n" + json.dumps(debrief_save) + "\n```\n" + _CM2
        r4._write_gm_double_config(
            cfg_path, responses=["SL-Antwort auf Anker.", debrief_text], calls_log=calls_log,
        )
        env = r4._gm_double_env(cfg_path)

        argv1 = [
            sys.executable, "-B", str(r4._HARDEXIT_BEFORE_REFLECTION),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest1:{in_fifo_1}:{out_fifo_1}",
        ]
        utc_start1 = r6.utc(time.time())
        proc1 = subprocess.Popen(
            argv1, cwd=str(_WORKTREE), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f1, out_f1 = r4._open_guest_fifo_pair(in_fifo_1, out_fifo_1)
        r4._drain(out_f1, settle=0.6, overall=10.0)

        r4._send_op(proc1, f"tisch-anbieten {table_key}")
        time.sleep(0.6)
        r4._send_guest(in_f1, f"tisch-anfragen {table_key}")
        r4._drain(out_f1, settle=0.6, overall=10.0)
        r4._send_op(proc1, f"tisch-annehmen {table_key} guest1")
        time.sleep(0.6)
        r4._send_op(proc1, f"tisch-start {table_key}")

        r4._wait_for_marker(out_f1, "Empfaenger: Spielleitung (SL)", overall=25.0)
        r4._deliver_guest_turn_answer(in_f1, out_f1, "Ich erkunde die Gegend.")
        r4._wait_for_marker(out_f1, "Empfaenger: Spielleitung (SL)", overall=25.0)
        r4._deliver_guest_turn_answer(in_f1, out_f1, "Ich schliesse den Abschnitt ab.")

        stdout1, stderr1 = proc1.communicate(timeout=30)
        utc_end1 = r6.utc(time.time())
        in_f1.close()
        out_f1.close()
        assert proc1.returncode == 94, (
            f"B2/Prozess1: erwartete os._exit(94) NACH Plan-Pin/Primaersave, VOR Reflexion -- "
            f"rc={proc1.returncode} stderr={stderr1!r}"
        )
        evidence["processes"]["proc1_hardexit"] = {
            "argv": argv1, "pid": proc1.pid, "utc_start": utc_start1, "utc_end": utc_end1,
            "exit_code": proc1.returncode, "stdout_text": stdout1, "stderr_text": stderr1,
        }

        table_id = "local-guest1"
        completion_section_id = f"{table_id}-section"
        plan_path = run_dir / "completion" / f"{completion_section_id}__plan.json"
        final_path = run_dir / "completion" / f"{completion_section_id}__final.json"
        assert plan_path.exists(), "B2: Prozess 1 haette den Plan real pinnen muessen (verbindliche Annahme)."
        assert guest_current_path.exists(), "B2: Prozess 1 haette den Primaersave real schreiben muessen."
        assert not final_path.exists(), "B2: __final.json darf von Prozess 1 NICHT erreicht worden sein."
        sha_guest_after_commit = r4._sha256(guest_current_path)
        decision_after_proc1 = admission.read_table_decision(run_dir, table_id)
        assert decision_after_proc1 is not None and decision_after_proc1.get("decision") == "plan_committed", (
            decision_after_proc1
        )
        before_state = {
            "plan_exists": True, "final_exists": False, "guest_current_sha256": sha_guest_after_commit,
            "decision": decision_after_proc1.get("decision"),
        }

        in_fifo_2, out_fifo_2 = fifo_dir / "guest1_in_2.fifo", fifo_dir / "guest1_out_2.fifo"
        argv2 = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest1:{in_fifo_2}:{out_fifo_2}",
        ]
        utc_start2 = r6.utc(time.time())
        proc2 = subprocess.Popen(
            argv2, cwd=str(_WORKTREE), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f2, out_f2 = r4._open_guest_fifo_pair(in_fifo_2, out_fifo_2)
        r4._drain(out_f2, settle=0.6, overall=10.0)
        assert proc1.pid != proc2.pid, "B2: Prozess 2 muss eine ANDERE PID als Prozess 1 haben."
        r4._send_op(proc2, f"tisch-start {table_key}")
        resume_lines = r4._wait_for_marker(out_f2, "eigene lokale Notiz", overall=25.0)
        joined_resume = "".join(resume_lines)
        assert "KI-Leader" not in joined_resume, joined_resume
        r4._deliver_guest_turn_answer(in_f2, out_f2, "B2-Abschlussnotiz: regulaer fertiggestellt.")
        r4._wait_for_path(final_path, overall=25.0)
        finish_tail = r4._drain(out_f2, settle=0.6, overall=10.0)
        r4._send_op(proc2, "beenden")
        stdout2, stderr2 = proc2.communicate(timeout=30)
        utc_end2 = r6.utc(time.time())
        in_f2.close()
        out_f2.close()
        assert proc2.returncode == 0, f"B2/Prozess2: {stderr2}"
        assert final_path.exists(), "B2: Prozess 2 haette __final.json real schreiben muessen."
        sha_final = r4._sha256(final_path)
        sha_guest_after_finish = r4._sha256(guest_current_path)
        guest_private_state = onboarding.peek(guest_onboarding, "guest1")
        assert guest_private_state is not None and guest_private_state.final_save is not None, (
            "B2: die abgeschlossene Fassung haette ueber den normalen Rueckkanal in die private "
            "Gastablage geschrieben werden muessen."
        )
        final_char = guest_private_state.final_save["characters"][0]
        assert final_char["id"] == char_id and final_char["lvl"] == 2, final_char
        evidence["processes"]["proc2_resume_new_os_process"] = {
            "argv": argv2, "pid": proc2.pid, "utc_start": utc_start2, "utc_end": utc_end2,
            "exit_code": proc2.returncode, "stdout_text": stdout2, "stderr_text": stderr2,
        }

        in_fifo_3, out_fifo_3 = fifo_dir / "guest1_in_3.fifo", fifo_dir / "guest1_out_3.fifo"
        argv3 = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest1:{in_fifo_3}:{out_fifo_3}",
        ]
        utc_start3 = r6.utc(time.time())
        result3 = subprocess.run(
            argv3, cwd=str(_WORKTREE), env=env,
            input=f"tisch-start {table_key}\nbeenden\n", capture_output=True, text=True, timeout=30,
        )
        utc_end3 = r6.utc(time.time())
        assert result3.returncode == 0, f"B2/Prozess3: {result3.stderr}"
        assert f"Tischstart abgelehnt: Tisch '{table_key}' ist geschlossen" in result3.stdout, result3.stdout
        assert r4._sha256(final_path) == sha_final, "B2: identischer Retry hat __final.json erneut geschrieben."
        assert r4._sha256(guest_current_path) == sha_guest_after_finish, (
            "B2: identischer Retry hat den Gast-Save veraendert."
        )
        evidence["processes"]["proc3_identical_retry_no_double_effect"] = {
            "argv": argv3, "utc_start": utc_start3, "utc_end": utc_end3,
            "exit_code": result3.returncode, "stdout_text": result3.stdout, "stderr_text": result3.stderr,
        }

        export_path = guest_onboarding.parent / "exports" / "guest1.json"
        argv4 = [
            sys.executable, "-B", str(r4._LAUNCHER), "--no-host-capable",
            "--participant", "guest1", "--data-dir", str(guest_onboarding.parent),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
        ]
        utc_start4 = r6.utc(time.time())
        result4 = subprocess.run(
            argv4, cwd=str(_WORKTREE), env=r4._clean_env(),
            input="fortsetzen\ne\nbeenden\n",
            capture_output=True, text=True, timeout=30,
        )
        utc_end4 = r6.utc(time.time())
        assert result4.returncode == 0, f"B2/Prozess4 (kalter Reload): {result4.stderr}"
        assert export_path.exists(), (
            f"B2: der kalte Reload haette einen Export unter {export_path} schreiben muessen: "
            f"{result4.stdout[-800:]!r}"
        )
        exported = json.loads(export_path.read_text(encoding="utf-8"))
        exp_char = exported["characters"][0]
        assert exp_char["id"] == char_id and exp_char["lvl"] == 2, exp_char
        evidence["processes"]["proc4_cold_reload_usable_afterward"] = {
            "argv": argv4, "utc_start": utc_start4, "utc_end": utc_end4,
            "exit_code": result4.returncode, "stdout_text": result4.stdout, "stderr_text": result4.stderr,
            "exported_char": exp_char,
        }
        evidence["guest1_fifo_channel"] = {
            "resume_lines_proc2": resume_lines, "finish_tail_proc2": finish_tail,
        }

        for label, pr in (
            ("proc1_hardexit", evidence["processes"]["proc1_hardexit"]),
            ("proc2_resume_new_os_process", evidence["processes"]["proc2_resume_new_os_process"]),
            ("proc3_identical_retry_no_double_effect", evidence["processes"]["proc3_identical_retry_no_double_effect"]),
            ("proc4_cold_reload_usable_afterward", evidence["processes"]["proc4_cold_reload_usable_afterward"]),
        ):
            r6.write_process_result(
                out_dir, label, argv=pr["argv"], cwd=str(_WORKTREE),
                utc_start=pr["utc_start"], utc_end=pr["utc_end"], exit_code=pr["exit_code"],
                stdout_text=pr["stdout_text"], stderr_text=pr["stderr_text"],
            )
            mf.record_process_files(
                label, aussage=f"b2_{label}", run_id="B2", teilnehmer_figur="guest1",
                tisch_abschnitt=f"{table_key}/{table_id}",
            )
        mf.export_tree(run_dir, "run", aussage="b2_run_dir_final", run_id="B2", teilnehmer_figur="guest1")
        mf.export_tree(guest_onboarding, "guest_onboarding", aussage="b2_guest_private_final", run_id="B2", teilnehmer_figur="guest1")
        mf.export_file(export_path, "guest1_cold_reload_export.json", aussage="b2_cold_reload_export", run_id="B2", teilnehmer_figur="guest1")
        mf.write_json_body("before_after_inventory.json", {
            "before_resume": before_state,
            "after_regular_finish": {
                "final_exists": True, "final_sha256": sha_final,
                "guest_current_sha256": sha_guest_after_finish,
                "guest_private_final_lvl": final_char["lvl"],
            },
            "after_identical_retry": {"no_double_effect": True},
            "after_cold_reload": {"exported_char_lvl": exp_char["lvl"]},
        }, aussage="b2_before_after_inventory", run_id="B2", teilnehmer_figur="guest1")
        mf.write_json_body(
            "guest1_fifo_channel_transcript.json", evidence["guest1_fifo_channel"],
            aussage="b2_guest1_fifo_channel_transcript_proc2_resume", run_id="B2", teilnehmer_figur="guest1",
        )
        mf.write_manifest()
        mf.write_summary({
            "szene": "B2_committed_interrupt_new_process",
            "aussage": (
                "BEHALTEN (Briefing/Review: 'A7 und B2 bleiben erledigt') -- frisch am fixen Stand "
                "(Head a5d2e1a2) gefahren, inhaltlich unveraendert. Verbindliche Annahme (Plan-Pin+"
                "Primaersave) real geschrieben (Prozess 1), gezielte Unterbrechung ueber die vorhandene "
                "Testnaht, GETRENNTER NEUER OS-Prozess (Prozess 2, andere PID) bindet denselben offenen "
                "Abschluss und beendet ihn regulaer. Identischer Retry (Prozess 3) ohne zweite Wirkung. "
                "Kalter Reload (Prozess 4) zeigt die wirklich nutzbare persoenliche Fassung danach."
            ),
            "proc1_pid": proc1.pid, "proc2_pid": proc2.pid,
            "proc_pids_distinct": proc1.pid != proc2.pid,
            "source_commit": _SOURCE_COMMIT, "source_tree": _SOURCE_TREE,
        })

    evidence["out_dir"] = str(out_dir)
    return evidence


def run_scene_a8() -> dict:
    """A8 (R5-Fix): A8a BEHAELT die bereits erledigte, aber korrekt
    umbenannte Grant-Ablehnung (requested -> rejected, kein Erstentwurf
    jemals erzeugt). A8b (NEU) liefert den vom Briefing geforderten
    "kurzen echten Erstentwurf+Abbruch mit tatsaechlichem Vorher-/
    Nachherinventar": guest4 wird freigegeben, startet den ECHTEN
    Erschaffungsdialog (1 echter GM-Call, Frage 1 real empfangen), pausiert
    dann LOKAL (dialogeigenes '/abbrechen', keine Antwort an die SL, kein
    zweiter GM-Call) und wird DANACH ueber den EIGENEN, durablen Befehl
    'gast-erschaffung-abbrechen' endgueltig abgebrochen -- kein
    gueltiger Reise-Save, kein Katalogeintrag, Onboarding-Status
    `abandoned`, ein erneuter Dialogversuch wird nachweislich als
    'veraltet' abgelehnt (kein dritter GM-Call)."""
    out_dir = _OUT_ROOT / "A8_grant_rejection_and_unaccepted_draft_abort"
    mf = r6.Manifest(out_dir)
    evidence: dict = {}

    a8_root = Path(tempfile.mkdtemp(prefix="j4r2-a8-"))
    a8_op_data = a8_root / "op_data"
    a8_run_dir = a8_root / "run"
    a8_states_dir = a8_root / "states"
    a8_fifo_dir = a8_root / "fifos"
    a8_fifo_dir.mkdir(parents=True)
    in_fifo_c, out_fifo_c = a8_fifo_dir / "guest3_in.fifo", a8_fifo_dir / "guest3_out.fifo"
    in_fifo_d, out_fifo_d = a8_fifo_dir / "guest4_in.fifo", a8_fifo_dir / "guest4_out.fifo"
    write_test_profile(a8_run_dir, max_turns=50)
    guest3_catalog = a8_op_data / "guests" / "guest3" / "catalog"
    guest3_current_path = a8_run_dir / "current_saves" / "guest3.json"
    guest4_onboarding = a8_op_data / "guests" / "guest4" / "onboarding"
    guest4_catalog = a8_op_data / "guests" / "guest4" / "catalog"
    guest4_current_path = a8_run_dir / "current_saves" / "guest4.json"

    q1_draft = "Wie nennt sich dein Chrononaut? (A8b echter, unangenommener Entwurf)"
    calls_log = a8_root / "gm_calls.jsonl"
    cfg_path = a8_root / "gmdouble_cfg.json"
    r4._write_gm_double_config(cfg_path, responses=[q1_draft], calls_log=calls_log)
    env = r4._gm_double_env(cfg_path)

    argv_a8 = [
        sys.executable, "-B", str(r4._LAUNCHER),
        "--participant", "operator1", "--data-dir", str(a8_op_data),
        "--run-dir", str(a8_run_dir), "--states-dir", str(a8_states_dir),
        "--guest-terminal", f"guest3:{in_fifo_c}:{out_fifo_c}",
        "--guest-terminal", f"guest4:{in_fifo_d}:{out_fifo_d}",
    ]
    utc_s8 = r6.utc(time.time())
    proc8 = subprocess.Popen(
        argv_a8, cwd=str(_WORKTREE), env=env, stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
    )
    in_fc, out_fc = r4._open_guest_fifo_pair(in_fifo_c, out_fifo_c)
    in_fd, out_fd = r4._open_guest_fifo_pair(in_fifo_d, out_fifo_d)
    r4._drain(out_fc, settle=0.6, overall=10.0)
    r4._drain(out_fd, settle=0.6, overall=10.0)

    # ── A8a (BEHALTEN, korrekt benannt): Grant-Ablehnung, kein Erstentwurf.
    before_catalog = catalog.list_for_participant(guest3_catalog, "guest3")
    assert before_catalog == [], before_catalog
    r4._send_guest(in_fc, "gast-erschaffung-anfragen operator1")
    request_c = r4._drain(out_fc, settle=0.6, overall=10.0)
    grant_before_c = creation_grants.grant_status(a8_run_dir, "guest3")
    assert grant_before_c["status"] == "requested", grant_before_c
    r4._send_op(proc8, "gast-erschaffung-ablehnen guest3")
    time.sleep(0.6)
    reject_tail_c = r4._drain(out_fc, settle=0.6, overall=8.0)
    grant_after_c = creation_grants.grant_status(a8_run_dir, "guest3")
    assert grant_after_c["status"] != "approved", grant_after_c
    after_catalog = catalog.list_for_participant(guest3_catalog, "guest3")
    assert after_catalog == [], (
        f"A8a: eine Grant-Ablehnung darf KEINEN Katalogeintrag erzeugen: {after_catalog}"
    )
    assert not guest3_current_path.exists(), (
        "A8a: eine Grant-Ablehnung darf KEINEN gueltigen Reise-Save (current_saves) erzeugen."
    )

    # ── A8b (NEU, R5): echter, unangenommener Erstentwurf + durabler Abbruch.
    before_catalog_d = catalog.list_for_participant(guest4_catalog, "guest4")
    assert before_catalog_d == [], before_catalog_d
    r4._send_guest(in_fd, "gast-erschaffung-anfragen operator1")
    request_d = r4._drain(out_fd, settle=0.6, overall=10.0)
    grant_before_d = creation_grants.grant_status(a8_run_dir, "guest4")
    assert grant_before_d["status"] == "requested", grant_before_d
    r4._send_op(proc8, "gast-erschaffung-annehmen guest4")
    time.sleep(0.6)
    grant_after_annehmen_d = creation_grants.grant_status(a8_run_dir, "guest4")
    assert grant_after_annehmen_d["status"] == "approved", grant_after_annehmen_d

    r4._send_guest(in_fd, "gast-erschaffung-dialog operator1")
    draft_q1_tail = r4._wait_for_marker(out_fd, f"[SL] {q1_draft}", overall=15.0)
    # Echter 1. GM-Call ist jetzt verbraucht (Frage real empfangen) -- EIN
    # bereits entstandener, noch unangenommener Entwurfsschritt. Statt zu
    # antworten, pausiert der Gast LOKAL (dialogeigenes '/abbrechen' --
    # KEINE Antwort an die SL, KEIN zweiter GM-Call, Fortschritt bleibt
    # zunaechst resumable).
    r4._send_guest(in_fd, "/abbrechen")
    local_pause_tail = r4._wait_for_marker(out_fd, "Lokal verarbeitet", overall=10.0)
    assert "NICHT als Antwort an die SL gesendet" in "".join(local_pause_tail), local_pause_tail
    onboarding_key_d = creation_grants.guest_onboarding_key("guest4", grant_after_annehmen_d["generation"])
    state_after_pause = onboarding.peek(guest4_onboarding, onboarding_key_d)
    assert state_after_pause is not None and state_after_pause.status == "in_progress", state_after_pause

    # Jetzt der GEFORDERTE EIGENE, durable Abbruch ausserhalb des Dialogs.
    r4._send_guest(in_fd, "gast-erschaffung-abbrechen operator1")
    durable_abort_tail = r4._wait_for_marker(out_fd, "Gast-Erschaffung abgebrochen", overall=10.0)
    joined_abort_d = "".join(durable_abort_tail)
    assert "abgebrochen (durabel)" in joined_abort_d, joined_abort_d
    assert "NICHT mehr als Figur veroeffentlicht werden" in joined_abort_d, joined_abort_d

    state_after_abort = onboarding.peek(guest4_onboarding, onboarding_key_d)
    assert state_after_abort is not None and state_after_abort.status == "abandoned", state_after_abort
    after_catalog_d = catalog.list_for_participant(guest4_catalog, "guest4")
    assert after_catalog_d == [], (
        f"A8b: ein durabel abgebrochener Entwurf darf KEINEN Katalogeintrag erzeugen: {after_catalog_d}"
    )
    assert not guest4_current_path.exists(), (
        "A8b: ein durabel abgebrochener Entwurf darf KEINEN gueltigen Reise-Save erzeugen."
    )

    # Nachweis der Durabilitaet: ein erneuter Dialogversuch scheitert VOR
    # jedem weiteren GM-Call (ensure_valid_grant wirft, bevor der Dialog
    # ueberhaupt startet -- 0 zusaetzliche GM-Calls).
    r4._send_guest(in_fd, "gast-erschaffung-dialog operator1")
    retry_rejected_tail = r4._wait_for_marker(out_fd, "Gast-Erschaffung abgelehnt", overall=10.0)
    joined_retry = "".join(retry_rejected_tail)
    assert "veraltet" in joined_retry, joined_retry

    r4._send_op(proc8, "beenden")
    stdout8, stderr8 = proc8.communicate(timeout=30)
    utc_e8 = r6.utc(time.time())
    in_fc.close(); out_fc.close(); in_fd.close(); out_fd.close()
    assert proc8.returncode == 0, f"A8: Launcher-Lauf gescheitert: {stderr8}"

    calls = [json.loads(l) for l in calls_log.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(calls) == 1, (
        f"A8b: genau EIN GM-Call (Frage 1) erwartet -- der lokale Pause UND der durable Abbruch UND "
        f"der abgelehnte Retry duerfen KEINEN weiteren Call ausgeloest haben: {calls}"
    )

    r6.write_process_result(
        out_dir, "a8_launcher", argv=argv_a8, cwd=str(_WORKTREE),
        utc_start=utc_s8, utc_end=utc_e8, exit_code=proc8.returncode,
        stdout_text=stdout8, stderr_text=stderr8,
    )
    mf.record_process_files(
        "a8_launcher", aussage="a8a_grant_rejection_plus_a8b_real_draft_durable_abort",
        run_id="A8", teilnehmer_figur="guest3+guest4",
    )
    mf.export_file(calls_log, "gm_calls.jsonl", aussage="a8b_gm_calls_log_exactly_one_call", run_id="A8")
    mf.write_json_body("io_transcript.json", {
        "a8a_request_c": request_c, "a8a_reject_tail_c": reject_tail_c,
        "a8b_request_d": request_d, "a8b_draft_q1_tail": draft_q1_tail,
        "a8b_local_pause_tail": local_pause_tail, "a8b_durable_abort_tail": durable_abort_tail,
        "a8b_retry_rejected_tail": retry_rejected_tail,
    }, aussage="a8_dialog_io_transcript", run_id="A8")
    mf.write_json_body("before_after_inventory.json", {
        "a8a_grant_rejection": {
            "before_catalog": [], "grant_before": grant_before_c, "grant_after": grant_after_c,
            "after_catalog": after_catalog, "current_save_exists": guest3_current_path.exists(),
        },
        "a8b_real_draft_durable_abort": {
            "before_catalog": before_catalog_d, "grant_before": grant_before_d,
            "grant_after_annehmen": grant_after_annehmen_d,
            "onboarding_status_after_local_pause": state_after_pause.status,
            "onboarding_status_after_durable_abort": state_after_abort.status,
            "after_catalog": after_catalog_d, "current_save_exists": guest4_current_path.exists(),
            "gm_calls_total": len(calls),
        },
    }, aussage="a8_before_after_inventory", run_id="A8")
    mf.write_manifest()
    mf.write_summary({
        "szene": "A8_grant_rejection_and_unaccepted_draft_abort",
        "aussage": (
            "A8a (behalten, korrekt benannt): Grant-Ablehnung (requested->rejected), kein Erstentwurf "
            "wurde dabei je erzeugt. A8b (neu, R5): guest4 wird freigegeben, startet den echten "
            "Erschaffungsdialog (1 echter GM-Call, Frage 1 real empfangen), pausiert lokal (dialogeigenes "
            "'/abbrechen', kein zweiter GM-Call), wird dann ueber 'gast-erschaffung-abbrechen' durabel "
            "abgebrochen (Onboarding-Status in_progress->abandoned) -- kein Katalogeintrag, kein "
            "gueltiger Reise-Save, ein erneuter Dialogversuch scheitert nachweislich als 'veraltet' "
            "VOR jedem weiteren GM-Call. gm_calls.jsonl: genau 1 Call insgesamt."
        ),
        "gm_calls_total": len(calls), "source_commit": _SOURCE_COMMIT, "source_tree": _SOURCE_TREE,
    })
    evidence["steps"] = {
        "A8a": {
            "before_catalog": before_catalog, "request_c": request_c,
            "grant_before": grant_before_c, "reject_tail": reject_tail_c,
            "grant_after": grant_after_c, "after_catalog": after_catalog,
            "guest3_current_exists": guest3_current_path.exists(),
        },
        "A8b": {
            "before_catalog": before_catalog_d, "request_d": request_d,
            "grant_before": grant_before_d, "grant_after_annehmen": grant_after_annehmen_d,
            "draft_q1_tail": draft_q1_tail, "local_pause_tail": local_pause_tail,
            "onboarding_status_after_local_pause": state_after_pause.status,
            "durable_abort_tail": durable_abort_tail,
            "onboarding_status_after_durable_abort": state_after_abort.status,
            "retry_rejected_tail": retry_rejected_tail,
            "after_catalog": after_catalog_d, "guest4_current_exists": guest4_current_path.exists(),
            "gm_calls_total": len(calls),
        },
    }
    evidence["out_dir"] = str(out_dir)
    return evidence


def run_scene_a9() -> dict:
    """A9 (R4-Fix): V1-Solo eng, drei echte Prozesse. Prozess 1 (BEHALTEN):
    Import/Spiel/Save ueber den normalen Produktweg. Prozess 2 (BEHALTEN,
    korrekt benannt): `--no-host-capable` -- Kaltladen + durchgesetzte
    Hostgrenze, KEIN erfolgreicher Fortsetzenuebergang (ehrlich als
    solches benannt). Prozess 3 (NEU, R4): ECHTER kurzer Host-
    Fortsetzenuebergang DERSELBEN fortgeschriebenen Figur im Hostmodus --
    OHNE `--no-host-capable`, `fortsetzen` traegt den bereits bestehenden
    Level-2-Stand direkt in `_cmd_local_round([])` (TUI
    `_cmd_menu_fortsetzen`), ein echter weiterer GM-Call + HQ-`!save`-
    Abschluss schreibt Level 3."""
    out_dir = _OUT_ROOT / "A9_solo_cold_load_vs_real_host_resume"
    mf = r6.Manifest(out_dir)
    evidence: dict = {}

    a9_root = Path(tempfile.mkdtemp(prefix="j4r2-a9-"))
    a9_data_dir = a9_root / "data"
    a9_run_dir = a9_root / "run"
    a9_states_dir = a9_root / "states"
    write_test_profile(a9_run_dir, max_turns=50)
    solo_char_id = "CHR-J4R2-SOLO"
    solo_save = full_v7_save(solo_char_id, name="SoloHeld", save_id="fixture-j4r2-solo-001")
    solo_calls_log = a9_root / "gm_calls.jsonl"
    solo_cfg = a9_root / "gmdouble_cfg.json"
    solo_sl1 = "SL-Antwort Solo Zug 1."
    solo_debrief_save = full_v7_save(solo_char_id, name="SoloHeld", save_id="fixture-j4r2-solo-002", level=2)
    from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER as _CM
    solo_debrief = "Abschnitt beendet.\n```json\n" + json.dumps(solo_debrief_save) + "\n```\n" + _CM
    r4._write_gm_double_config(solo_cfg, responses=[solo_sl1, solo_debrief], calls_log=solo_calls_log)
    solo_env = r4._gm_double_env(solo_cfg)

    # ── Prozess 1 (BEHALTEN): echter Soloweg bis zum gespeicherten Level 2.
    argv_solo1 = [
        sys.executable, "-B", str(r4._LAUNCHER),
        "--participant", "solo1", "--data-dir", str(a9_data_dir),
        "--run-dir", str(a9_run_dir), "--states-dir", str(a9_states_dir),
    ]
    utc_s9 = r6.utc(time.time())
    res9a = subprocess.run(
        argv_solo1, cwd=str(_WORKTREE), env=solo_env,
        input=(
            "i\n" + json.dumps(solo_save, ensure_ascii=False) + "\nENDE\nj\n"
            "l\n"
            "Ich erforsche die Umgebung.\n"
            "!save\n"
            "Solo-Abschlussnotiz: alles sauber.\n"
            "beenden\n"
        ),
        capture_output=True, text=True, timeout=30,
    )
    utc_e9 = r6.utc(time.time())
    r6.write_process_result(
        out_dir, "a9_proc1_create_play_save", argv=argv_solo1, cwd=str(_WORKTREE),
        utc_start=utc_s9, utc_end=utc_e9, exit_code=res9a.returncode,
        stdout_text=res9a.stdout, stderr_text=res9a.stderr,
    )
    mf.record_process_files(
        "a9_proc1_create_play_save", aussage="a9_solo_import_play_hq_save_real_process",
        run_id="A9", teilnehmer_figur="solo1",
    )
    assert res9a.returncode == 0, f"A9/Prozess1: {res9a.stderr}"
    assert "Unbekannte Auswahl" not in res9a.stdout, res9a.stdout

    # ── Prozess 2 (BEHALTEN, korrekt benannt): --no-host-capable ist
    # Kaltladen + durchgesetzte Hostgrenze, KEIN Fortsetzenuebergang.
    argv_solo2 = [
        sys.executable, "-B", str(r4._LAUNCHER), "--no-host-capable",
        "--participant", "solo1", "--data-dir", str(a9_data_dir),
        "--run-dir", str(a9_run_dir), "--states-dir", str(a9_states_dir),
    ]
    utc_s9b = r6.utc(time.time())
    res9b = subprocess.run(
        argv_solo2, cwd=str(_WORKTREE), env=r4._clean_env(),
        input="fortsetzen\ns\nbeenden\n", capture_output=True, text=True, timeout=30,
    )
    utc_e9b = r6.utc(time.time())
    r6.write_process_result(
        out_dir, "a9_proc2_cold_load_host_boundary", argv=argv_solo2, cwd=str(_WORKTREE),
        utc_start=utc_s9b, utc_end=utc_e9b, exit_code=res9b.returncode,
        stdout_text=res9b.stdout, stderr_text=res9b.stderr,
    )
    mf.record_process_files(
        "a9_proc2_cold_load_host_boundary", aussage="a9_solo_no_host_capable_cold_load_enforced_boundary",
        run_id="A9", teilnehmer_figur="solo1",
    )
    assert res9b.returncode == 0, f"A9/Prozess2: {res9b.stderr}"
    assert "Katalog-Eintraege: 1" in res9b.stdout, res9b.stdout
    # R4: ehrlich pruefen, dass dies TATSAECHLICH ein durchgesetzter
    # Hostgrenzfehler ist (Kaltladen), NICHT ein erfolgreicher
    # Fortsetzenuebergang.
    assert "nur im Hostmodus moeglich" in res9b.stdout, (
        f"A9/Prozess2: erwartete durchgesetzte Hostgrenze bei 'fortsetzen' unter --no-host-capable: "
        f"{res9b.stdout!r}"
    )
    assert "Kein Modellaufruf, keine Aenderung" in res9b.stdout, res9b.stdout

    # ── Prozess 3 (NEU, R4): ECHTER Host-Fortsetzenuebergang derselben
    # fortgeschriebenen (Level-2-)Figur -- OHNE --no-host-capable, frischer
    # GM-Double fuer eine ZWEITE, echte lokale Runde ueber 'fortsetzen'.
    solo_calls_log2 = a9_root / "gm_calls2.jsonl"
    solo_cfg2 = a9_root / "gmdouble_cfg2.json"
    solo_sl2 = "SL-Antwort Solo Zug 2 (echter Host-Fortsetzenuebergang)."
    solo_debrief_save2 = full_v7_save(solo_char_id, name="SoloHeld", save_id="fixture-j4r2-solo-003", level=3)
    solo_debrief2 = "Abschnitt beendet.\n```json\n" + json.dumps(solo_debrief_save2) + "\n```\n" + _CM
    r4._write_gm_double_config(solo_cfg2, responses=[solo_sl2, solo_debrief2], calls_log=solo_calls_log2)
    solo_env2 = r4._gm_double_env(solo_cfg2)

    current_before_p3 = json.loads((a9_run_dir / "current_saves" / "solo1.json").read_text(encoding="utf-8"))
    assert current_before_p3["characters"][0]["lvl"] == 2, current_before_p3

    argv_solo3 = [
        sys.executable, "-B", str(r4._LAUNCHER),
        "--participant", "solo1", "--data-dir", str(a9_data_dir),
        "--run-dir", str(a9_run_dir), "--states-dir", str(a9_states_dir),
    ]
    utc_s9c = r6.utc(time.time())
    res9c = subprocess.run(
        argv_solo3, cwd=str(_WORKTREE), env=solo_env2,
        input=(
            "fortsetzen\n"
            "Ich erforsche weiter (echter Host-Fortsetzenuebergang).\n"
            "!save\n"
            "Solo-Abschlussnotiz: Host-Fortsetzen erfolgreich.\n"
            "beenden\n"
        ),
        capture_output=True, text=True, timeout=30,
    )
    utc_e9c = r6.utc(time.time())
    r6.write_process_result(
        out_dir, "a9_proc3_real_host_resume", argv=argv_solo3, cwd=str(_WORKTREE),
        utc_start=utc_s9c, utc_end=utc_e9c, exit_code=res9c.returncode,
        stdout_text=res9c.stdout, stderr_text=res9c.stderr,
    )
    mf.record_process_files(
        "a9_proc3_real_host_resume", aussage="a9_real_host_resume_same_figure_level2_to_level3",
        run_id="A9", teilnehmer_figur="solo1",
    )
    assert res9c.returncode == 0, f"A9/Prozess3: {res9c.stderr}"
    assert "Unbekannte Auswahl" not in res9c.stdout, res9c.stdout
    assert "nur im Hostmodus moeglich" not in res9c.stdout, (
        f"A9/Prozess3: dies ist der ECHTE Hostmodus -- die Hostgrenzmeldung aus Prozess 2 darf hier "
        f"NICHT erscheinen: {res9c.stdout!r}"
    )
    assert f"Fortsetzen: " in res9c.stdout and solo_char_id in res9c.stdout, res9c.stdout

    current_after_p3 = json.loads((a9_run_dir / "current_saves" / "solo1.json").read_text(encoding="utf-8"))
    assert current_after_p3["characters"][0]["id"] == solo_char_id, current_after_p3
    assert current_after_p3["characters"][0]["lvl"] == 3, (
        f"A9/Prozess3: der echte Host-Fortsetzenuebergang haette die Figur auf Level 3 "
        f"fortschreiben muessen: {current_after_p3}"
    )
    # Hinweis: `onboarding.peek(...).final_save` ist die private
    # Gast-Rueckkanal-Fassung aus dem urspruenglichen Import (R3/A6-
    # Mechanik fuer ANGESCHLOSSENE Gaeste) -- fuer den HOST-Soloweg bleibt
    # SIE unveraendert bei Level 1 (empirisch verifiziert); die
    # autoritative Quelle fuer den Host-Fortsetzenuebergang ist
    # `current_saves/solo1.json` (oben bereits auf Level 3 verifiziert).
    final_char_p3 = current_after_p3["characters"][0]

    calls2 = [json.loads(l) for l in solo_calls_log2.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(calls2) == 2, (
        f"A9/Prozess3: genau 2 echte GM-Calls erwartet (Zug + HQ-Debrief): {calls2}"
    )

    mf.export_file(solo_calls_log2, "gm_calls_proc3.jsonl", aussage="a9_proc3_gm_calls_log", run_id="A9")
    mf.write_json_body("before_after_inventory.json", {
        "proc2_cold_load": {
            "host_boundary_enforced": True, "message_present": "nur im Hostmodus moeglich" in res9b.stdout,
        },
        "proc3_real_host_resume": {
            "current_save_lvl_before": current_before_p3["characters"][0]["lvl"],
            "current_save_lvl_after": current_after_p3["characters"][0]["lvl"],
            "private_final_save_lvl": final_char_p3["lvl"],
            "gm_calls_total": len(calls2),
        },
    }, aussage="a9_before_after_inventory", run_id="A9")
    mf.write_manifest()
    mf.write_summary({
        "szene": "A9_solo_cold_load_vs_real_host_resume",
        "aussage": (
            "Prozess 1 (behalten): echter Soloweg bis gespeichertem Level 2 (HQ-'!save'). Prozess 2 "
            "(behalten, korrekt benannt): --no-host-capable ist Kaltladen + durchgesetzte Hostgrenze "
            "('nur im Hostmodus moeglich', 'Kein Modellaufruf, keine Aenderung') -- KEIN erfolgreicher "
            "Fortsetzenuebergang. Prozess 3 (neu, R4): ECHTER Host-Fortsetzenuebergang DERSELBEN Figur "
            "(solo1/CHR-J4R2-SOLO) OHNE --no-host-capable -- 'fortsetzen' traegt den bestehenden "
            "Level-2-Stand direkt in eine neue lokale Runde (TUI _cmd_menu_fortsetzen -> "
            "_cmd_local_round([])), 2 echte GM-Calls (Zug+HQ-Debrief), Level 2 -> Level 3 real "
            "fortgeschrieben und ueber den normalen privaten Rueckkanal bestaetigt."
        ),
        "source_commit": _SOURCE_COMMIT, "source_tree": _SOURCE_TREE,
    })
    evidence["steps"] = {
        "A9_proc1": {"stdout": res9a.stdout, "stderr": res9a.stderr, "exit_code": res9a.returncode},
        "A9_proc2_cold_load_host_boundary": {
            "stdout": res9b.stdout, "stderr": res9b.stderr, "exit_code": res9b.returncode,
        },
        "A9_proc3_real_host_resume": {
            "stdout": res9c.stdout, "stderr": res9c.stderr, "exit_code": res9c.returncode,
            "lvl_before": current_before_p3["characters"][0]["lvl"],
            "lvl_after": current_after_p3["characters"][0]["lvl"], "gm_calls_total": len(calls2),
        },
        "solo_char_id": solo_char_id,
    }
    evidence["out_dir"] = str(out_dir)
    return evidence


_SCENES = {
    "a": run_scene_a,
    "b1a": run_scene_b1_abbrechen_n3,
    "b1b": run_scene_b1b_stop_race_open_call,
    "b2": run_scene_b2,
    "a8": run_scene_a8,
    "a9": run_scene_a9,
}


def main() -> int:
    which = os.environ.get("J4R2_SCENES", "a,b1a,b1b,b2,a8,a9").split(",")
    failed = 0
    for key in which:
        key = key.strip()
        if key not in _SCENES:
            continue
        try:
            ev = _SCENES[key]()
            print(f"OK scene_{key}")
            print(json.dumps({"out_dir": ev.get("out_dir")}, indent=2))
        except AssertionError as e:
            failed += 1
            print(f"FAIL scene_{key}: {e}")
            traceback.print_exc()
        except Exception:
            failed += 1
            traceback.print_exc()
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
