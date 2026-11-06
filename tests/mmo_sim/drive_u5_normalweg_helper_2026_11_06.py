#!/usr/bin/env python3
"""
tests/mmo_sim/drive_u5_normalweg_helper_2026_11_06.py -- ZR-VOLLENDUNG-
OHNE-LAN-NACHZUG-20261106-R3, Stage 4a (U5-Normalwegbeleg ueber den ECHTEN
Gast-Helfer-PROZESS): belegt am ECHTEN ausgelieferten Launcher
(`scripts/mmo_sim.py`, GM NUR als Grenzinjektion
`MMO_SIM_GM_TRANSPORT_DOUBLE`, NIE Live-Modell) den persoenlichen
Normalweg mit ZWEI persoenlichen Figuren (operator1 UND guest1, beide
NICHT figurlos) an einem lokalen Tisch -- wobei der Gast NICHT ueber
`r4._open_guest_fifo_pair(...)` (direktes FIFO-Plumbing) bedient wird,
sondern ueber den ECHTEN Helfer-Prozess `scripts/zeitriss-gast-terminal.sh`
(Subprozess mit stdin/stdout-Pipes) -- derselbe FIFO-Kanal, aber ueber ein
echtes, separates Betriebssystem-Programm gespiegelt (`cat OUT_FIFO &` auf
dessen eigenen stdout), nicht ueber einen Test-only Direktzugriff.

Launcher-/GM-Double-Mechanik ist bytegleich aus der bestehenden
`drive_r4_evidence_2026_11_04.py`-Harness importiert (`r4._LineReader`,
`_drain`, `_wait_for_marker`, `_wait_for_path`, `_send_op`, `_send_guest`,
`_write_gm_double_config`, `_gm_double_env`, `_seed_guest_figure`,
`_LAUNCHER`) -- kein zweiter Admissions-/Transportpfad. `r4._LineReader`
(roher `os.read()` ohne TextIOWrapper-Pufferfalle) wird hier NICHT nur
gegen eine rohe FIFO verwendet, sondern GENAUSO gegen den `fileno()` von
`helper.stdout` (Helfer-Subprozess) UND von `proc.stdout` (Operator-
Subprozess, s.u. "entscheidender Unterschied zur Vorlage" unten) --
dieselbe Lese-Semantik, zwei verschiedene reale Pipe-Fds.

ENTSCHEIDENDER STRUKTURBEFUND (empirisch aus `mmo_sim/ui/tui.py:
_cmd_table_start`/F1-Nachzug UND `core/runtime.py:run_full_section`
hergeleitet, NICHT geraten): bringt der Betreiber (hier operator1) eine
EIGENE abgeschlossene Figur mit (`own_figure is not None` via
`_resolve_member`), bleibt der Betreiber -- bytegleich zum bestehenden
"mitspielenden Hostweg" (`test_full_a_to_b_to_a_table_journey`) -- der
SPIELENDE LEADER des Tisches; der Gast wird zum NICHT-Leader-Mitglied.
NUR der Leader sendet direkt an die SL (`core/runtime.py:act`s
Docstring: "nur der Leader sendet"); sein `_HumanDriver._is_leader=True`
zeigt daher UNBEDINGT die Zeile "Empfaenger: Spielleitung (SL)" vor JEDEM
seiner Zuege. Ein NICHT-Leader-Mitglied mit eigener mitgebrachter Figur
bekommt dagegen (laut `core/runtime.py:run_full_section`-Docstring "Gaeste
einzeln (Import)") GENAU EINEN eigenen ersten Beitrag, der zwar ECHT an
die SL durchlaeuft, aber mit der Empfaengerzeile "Empfaenger: ueber
Leader an Spielleitung (dein Erstbeitrag, mit deinem Save)" angezeigt
wird (`ui/tui.py:_HumanDriver._purpose_label`, Fall 2 von 3 explizit
dokumentiert) -- NICHT mit dem woertlichen Substring "Empfaenger:
Spielleitung (SL)". Das heisst: bringt der Betreiber (wie von diesem
Auftrag verlangt) eine EIGENE Figur mit, zeigt NUR DAS OPERATOR-FENSTER
(`proc.stdout`) die woertliche Zeile "Empfaenger: Spielleitung (SL)";
das GAST-FENSTER (Helfer-Stdout) zeigt die STRUKTURELL verwandte, aber
woertlich andere Erstbeitrags-Zeile. Dieser Treiber belegt daher Assertion
B EHRLICH an BEIDEN realen Fenstern (zitiert beide woertlichen Zeilen),
statt eine im Produkt nicht erreichbare Woertlichkeit vorzutaeuschen --
s. Report fuer die volle Herleitung.

Pure Python, nur `assert`, echter Exitcode, kein pytest."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import drive_r4_evidence_2026_11_04 as r4  # noqa: E402
import _r6_evidence_helpers as r6  # noqa: E402

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import catalog  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER  # noqa: E402
from _full_v7_fixture import full_v7_save  # noqa: E402

_OUT_ROOT = Path("/home/altair/zr-vollendung-20261106/evidence/u5-normalweg")
_GUEST_HELPER = _REPO_ROOT / "scripts" / "zeitriss-gast-terminal.sh"


def run_scene_u5() -> dict:
    out_dir = _OUT_ROOT
    mf = r6.Manifest(out_dir)
    findings: dict = {}

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data, run_dir, states_dir = root / "op_data", root / "run", root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        in_fifo, out_fifo = fifo_dir / "guest_in.fifo", fifo_dir / "guest_out.fifo"
        calls_log, cfg_path = root / "gm_calls.jsonl", root / "gmdouble_cfg.json"

        write_test_profile(run_dir, max_turns=200)

        # Zwei persoenliche Figuren, VOR Prozessstart geseedet -- dasselbe
        # Muster wie `r4._seed_guest_figure` (dieselbe Funktion, einmal auf
        # die Operator-Ablage `data_dir/onboarding`+`catalog` angewendet --
        # s. `scripts/mmo_sim.py:379-380` fuer diese Pfadautoritaet --,
        # einmal auf die Gast-Ablage `data_dir/guests/guest1/...`, s.
        # `scripts/mmo_sim.py:446-447`). KEIN zweiter Seeding-Mechanismus.
        operator_char_id = "chrono-vollendung-operator"
        guest_char_id = "chrono-vollendung-gast"
        operator_seed_save = r4._seed_guest_figure(
            op_data / "onboarding", op_data / "catalog", "operator1",
            operator_char_id, "fixture-vollendung-operator-001",
        )
        guest_onboarding = op_data / "guests" / "guest1" / "onboarding"
        guest_catalog = op_data / "guests" / "guest1" / "catalog"
        r4._seed_guest_figure(
            guest_onboarding, guest_catalog, "guest1",
            guest_char_id, "fixture-vollendung-guest-001",
        )
        # R4-NACHZUG-BEFUND 2 (empirisch): `r4._seed_guest_figure` ruft NUR
        # `catalog.register` (fuegt die Figur hinzu), NIE `catalog.bind_for_
        # section` -- `catalog.last_selected` (die Quelle von `_build_resume_
        # card`s `chrononaut_id`, s. `ui/tui.py:2466`, und damit der
        # Abschlusskarte "hat_character"-Weiche) bleibt dadurch `None`, auch
        # wenn `onboarding.peek(...).final_save` bereits eine echte Figur
        # trägt. Szene A (`drive_v_journey`) prueft die Abschlusskarte nicht,
        # dieser Treiber (Assertion C) tut es -- deshalb hier ZUSAETZLICH die
        # aktive Bindung auf BEIDEN Katalogen setzen (kein neuer Mechanismus,
        # dieselbe Funktion, die der echte Produktweg bei jeder Tischbindung
        # ohnehin aufruft, s. `ui/tui.py:3173`/`:3824`/`:4308`).
        catalog.bind_for_section(op_data / "catalog", "operator1", operator_char_id, has_open_section=False)
        catalog.bind_for_section(guest_catalog, "guest1", guest_char_id, has_open_section=False)
        # R4-NACHZUG-BEFUND (empirisch, s. `test_stage5_tui_wiring_2026_11_02.
        # py:_register_own_figure`-Docstring, tui.py:3131-3140): der Gast
        # bekommt seinen Persona-State+Current AUTOMATISCH ueber den
        # `tisch-annehmen`/Intake-Weg des Hosts; der OPERATOR hat KEINEN
        # aequivalenten Intake-Schritt (er "nimmt sich nicht selbst an") --
        # `r4._seed_guest_figure` allein (nur Onboarding+Katalog) reicht
        # fuer den LEADER deshalb NICHT: ohne persistierten Persona-State
        # lehnt `store._validate_harvest` ihn beim Abschluss als 'missing'
        # ab (`persona_state_store.load_state` -> `FileNotFoundError`).
        # Derselbe zusaetzliche Schritt wie `_register_own_figure(...,
        # run_dir=..., states_dir=...)` fuer den HOST in jenem Test.
        from mmo_sim.core import store as core_store
        from mmo_sim.core.persona_state import PersonaStateStore
        ps_store = PersonaStateStore(schema_path=r4._SCHEMA_PATH)
        onboarding.ensure_participant_persona_state(
            ps_store, states_dir, "operator1", operator_char_id, operator_seed_save,
        )
        core_store.publish_current_save(run_dir, "operator1", operator_seed_save, ps_store, states_dir)

        table_id = "local-operator1-guest1"
        final_path = run_dir / "completion" / f"{table_id}-section__final.json"
        operator_current_path = run_dir / "current_saves" / "operator1.json"
        guest_current_path = run_dir / "current_saves" / "guest1.json"

        # GM-Double: GENAU drei Antworten fuer GENAU drei reale GM-Rufe
        # dieses Normalwegs (empirisch aus `core/runtime.py:run_full_
        # section` hergeleitet: Leader-Anker (operator1), Gast-Erstbeitrag
        # (guest1), zweiter Leader-Zug mit Debrief+Marker) -- der Debrief
        # traegt ZWEI getrennte v7-Bloecke (je ein Chrononaut), damit
        # `zeitriss_saves.harvest_from_debrief` (iteriert ALLE gefundenen
        # fenced ```json-Bloecke) BEIDEN Teilnehmern eine gueltige,
        # fortschrittstragende Endfassung zuordnet.
        operator_debrief_block = full_v7_save(
            operator_char_id, name="Operator-operator1",
            save_id="fixture-vollendung-operator-002", level=2,
        )
        guest_debrief_block = full_v7_save(
            guest_char_id, name="Gast-guest1",
            save_id="fixture-vollendung-guest-002", level=2,
        )
        debrief_text = (
            "Abschnitt beendet, beide Standsicherungen anbei.\n"
            "```json\n" + json.dumps(operator_debrief_block) + "\n```\n"
            "```json\n" + json.dumps(guest_debrief_block) + "\n```\n"
            + COMPLETION_MARKER
        )
        r4._write_gm_double_config(
            cfg_path,
            responses=[
                "SL-Antwort auf den Operator-Anker.",
                "SL-Antwort auf den Gast-Erstbeitrag.",
                debrief_text,
            ],
            calls_log=calls_log,
        )
        env = r4._gm_double_env(cfg_path)
        argv = [
            sys.executable, "-B", str(r4._LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest1:{in_fifo}:{out_fifo}",
        ]
        utc_start = r6.utc(time.time())
        proc = subprocess.Popen(
            argv, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        # Operator-Fenster wird jetzt INTERAKTIV mitgelesen (nicht erst am
        # Ende via `communicate()`) -- operator1 spielt mit, braucht also
        # dieselbe Marker-Wartesemantik wie der Gast. `_LineReader`/
        # `_wait_for_marker`/`_drain` sind fd-generisch (s. r4-Docstring),
        # funktionieren daher UNVERAENDERT auch auf `proc.stdout.fileno()`.
        host_reader = r4._LineReader(proc.stdout.fileno())

        r4._wait_for_path(in_fifo, overall=15.0)
        r4._wait_for_path(out_fifo, overall=15.0)

        # DER entscheidende Unterschied zur Vorlage: der Gast wird ueber
        # den ECHTEN Helfer-PROZESS bedient (eigenes Betriebssystem-
        # Programm mit stdin/stdout-Pipes), NICHT ueber
        # `r4._open_guest_fifo_pair(...)` (direktes Test-FIFO-Plumbing).
        helper = subprocess.Popen(
            [str(_GUEST_HELPER), "guest1", str(in_fifo), str(out_fifo)],
            cwd=str(_REPO_ROOT), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        guest_reader = r4._LineReader(helper.stdout.fileno())

        host_boot = r4._drain(host_reader, settle=0.6, overall=10.0)
        helper_header = r4._drain(guest_reader, settle=0.6, overall=10.0)
        helper_header_joined = "".join(helper_header)
        assert "ZEITRISS -- lokaler Gast-Anschluss" in helper_header_joined, helper_header_joined

        # ── Assertion A0 (R2-C1 / 01_NACHZUG §21, U1 "Prompt steht vor
        # Eingabe"): die aktive Boot-Menue-Aufforderung "Auswahl:" steht BEREITS
        # in DIESEM Drain, der VOR dem ersten `_send_guest(...)` eingesammelt
        # wurde -- der Gast sieht seine Aufforderung also vor der erwarteten
        # Eingabe. Vor dem R3-Fix gab der getimede Gast-Leser
        # `_readline_guest_menu` sein Prompt erst beim tatsaechlichen Konsum
        # (nach gemeldeter Bereitschaft) aus; dann fehlte "Auswahl:" in genau
        # diesem Pre-Eingabe-Drain. Ehrliche Grenze (02_ABNAHME §E): gepufferter
        # Empfang beweist nicht den exakten Schreibzeitpunkt -- aber die
        # Aufforderung LIEGT hier nachweislich vor jeder gesendeten Gastzeile.
        assert "Auswahl:" in helper_header_joined, (
            "R2-C1: aktive Menue-Aufforderung 'Auswahl:' fehlt im Pre-Eingabe-"
            "Drain des Gast-Boot-Menues:\n" + helper_header_joined
        )

        # ── Assertion A: echte nummerierte Menue-/Auswahlfuehrung im
        # Gast-Fenster (ECHTER Helfer-Prozess-Stdout, nicht Testkonstrukt).
        r4._send_guest(helper.stdin, "tisch")
        tisch_menu_lines = r4._wait_for_marker(
            guest_reader, "Tisch -- [1] Offene Tische suchen", overall=15.0,
        )
        tisch_menu_joined = "".join(tisch_menu_lines)
        assert "[1] Offene Tische suchen" in tisch_menu_joined, tisch_menu_joined
        assert "[2] Tisch anfragen" in tisch_menu_joined, tisch_menu_joined
        r4._send_guest(helper.stdin, "/zurueck")
        r4._drain(guest_reader, settle=0.6, overall=8.0)

        # ── Normalweg: Gast fragt an, Operator nimmt an und startet.
        r4._send_op(proc, "tisch-anbieten mesaU5")
        time.sleep(0.6)
        r4._send_guest(helper.stdin, "tisch-anfragen mesaU5")
        after_request = r4._drain(guest_reader, settle=0.6, overall=10.0)
        after_request_joined = "".join(after_request)
        assert "Anfrage an Tisch 'mesaU5' gestellt" in after_request_joined, after_request_joined

        r4._send_op(proc, "tisch-annehmen mesaU5 guest1")
        time.sleep(0.6)
        assert guest_current_path.exists(), (
            "U5: tisch-annehmen haette den Gast-Startsave publizieren muessen."
        )

        r4._send_op(proc, "tisch-start mesaU5")

        # ── Operator1 bringt eine EIGENE Figur mit, bleibt also (anders als
        # in Szene A, wo der figurlose Betreiber den Gast zum Leader macht)
        # der mitspielende LEADER des Tisches; guest1 wird zum zusaetzlichen
        # Mitspieler-Token und muss den Rundenbeitritt ERST ausdruecklich
        # bestaetigen (`core/runtime.py`s "Dieser lokalen Runde ... beitreten?
        # [j/n]"-Konsensabfrage, echo-gespiegelt ins Helfer-Fenster ueber
        # `_FifoInputReader(echo_fn=...)`), BEVOR der Leader-Anker-Zug beginnt.
        consent_prompt = r4._wait_for_marker(
            guest_reader, "beitreten? [j/n]", overall=15.0,
        )
        consent_prompt_joined = "".join(consent_prompt)
        assert "Dieser lokalen Runde" in consent_prompt_joined, consent_prompt_joined
        r4._send_guest(helper.stdin, "j")

        # ── Assertion B, Operator-Haelfte: operator1 ist Leader (eigene
        # Figur) -- sein Leader-Anker-Zug zeigt UNBEDINGT die woertliche
        # Empfaengerzeile "Empfaenger: Spielleitung (SL)" in SEINEM Fenster
        # (proc.stdout), VOR seiner Antwort.
        operator_anchor_prompt = r4._wait_for_marker(
            host_reader, "Empfaenger: Spielleitung (SL)", overall=25.0,
        )
        operator_anchor_joined = "".join(operator_anchor_prompt)
        assert "Empfaenger: Spielleitung (SL)" in operator_anchor_joined, operator_anchor_joined
        r4._send_op(proc, "Ich sichte knapp die Lage am Tisch.")

        # ── Assertion B, Gast-Haelfte: guest1 ist NICHT Leader -- sein
        # eigener erster Beitrag laeuft zwar ECHT an die SL durch ("Gaeste
        # einzeln (Import)"), zeigt aber die strukturell verwandte,
        # woertlich andere Erstbeitrags-Empfaengerzeile. Zitiert im Report
        # als ehrlicher Beleg der realen Produktmechanik (kein erfundener
        # zweiter Marker).
        guest_first_prompt = r4._wait_for_marker(
            guest_reader, "Empfaenger: ueber Leader an Spielleitung", overall=25.0,
        )
        guest_first_joined = "".join(guest_first_prompt)
        assert "Empfaenger: ueber Leader an Spielleitung" in guest_first_joined, guest_first_joined
        assert "Unbekannte Auswahl" not in guest_first_joined, guest_first_joined
        r4._send_guest(helper.stdin, "Ich erkunde die Umgebung mit meiner eigenen Figur.")

        # ── Zweiter Leader-Zug (Operator): operator1s Kanal-Cursor stand
        # seit dem Anker-Zug (dort war `sl_log` noch leer) auf 0 -- diese
        # zweite Anzeige zeigt BEIDE bisherigen SL-Antworten auf einmal,
        # aber OHNE Zeitgedanke (`_sl_already_shown` war beim vorigen
        # Aufruf ebenfalls 0, s. Report fuer die empirische Herleitung).
        operator_second_prompt = r4._wait_for_marker(
            host_reader, "Empfaenger: Spielleitung (SL)", overall=25.0,
        )
        operator_second_joined = "".join(operator_second_prompt)
        assert "Empfaenger: Spielleitung (SL)" in operator_second_joined, operator_second_joined
        assert "Unbekannte Auswahl" not in operator_second_joined, operator_second_joined
        r4._send_op(proc, "Ich schliesse den Abschnitt ab.")

        # ── Nach dem Debrief (COMPLETION_MARKER) fragt der Abschluss die
        # freiwillige lokale Notiz JE Mitglied ab -- empirisch belegte
        # `table.members`-Reihenfolge: guest1 ZUERST, dann operator1 (NICHT
        # Beitrittsreihenfolge) -- erst danach wird __final.json geschrieben.
        # Guest1s Kanal-Cursor stand seit seinem Erstbeitrag auf >0 (es
        # sah dort bereits den Operator-Anker) -- diese Nachhol-Anzeige
        # (BEIDE verbleibenden SL-Antworten + der sanitisierte Debrief)
        # ist die ECHTE zweite Wartephase, an der die Zeitgedanke-Naht
        # (`_sl_already_shown>0 UND neue SL-Eintraege`) tatsaechlich feuert
        # (Assertion F).
        guest_reflection_prompt = r4._wait_for_marker(guest_reader, "eigene lokale Notiz", overall=25.0)
        guest_reflection_joined = "".join(guest_reflection_prompt)
        zeitgedanke_seam_fired = "[Zeitgedanke] " in guest_reflection_joined
        r4._send_guest(helper.stdin, "Abschlussnotiz Gast: Reise erfolgreich.")
        r4._wait_for_marker(host_reader, "eigene lokale Notiz", overall=25.0)
        r4._send_op(proc, "Abschlussnotiz Operator: Tischrunde erfolgreich geleitet.")

        r4._wait_for_path(final_path, overall=25.0)

        # ── Assertion C: persoenliche Abschlusskarte in BEIDEN Fenstern.
        host_finish_tail = r4._drain(host_reader, settle=0.8, overall=10.0)
        host_finish_joined = "".join(host_finish_tail)
        guest_finish_tail = r4._drain(guest_reader, settle=0.8, overall=10.0)
        guest_finish_joined = "".join(guest_finish_tail)
        assert "Abschlusskarte fuer 'operator1'" in host_finish_joined, host_finish_joined
        assert "Abschlusskarte fuer 'guest1'" in guest_finish_joined, guest_finish_joined
        # Nummerierte Export-/Rueckkehr-/Weiterspielen-Schritte (zusaetzlicher,
        # unabhaengiger Beleg fuer Assertion A im selben Gast-Fenster).
        assert ") Export des eigenen Standes" in guest_finish_joined, guest_finish_joined
        assert ") Zurueck zum Tisch/HQ" in guest_finish_joined, guest_finish_joined
        assert ") Weiterspielen" in guest_finish_joined, guest_finish_joined

        try:
            r4._send_op(proc, "beenden")
        except BrokenPipeError:
            pass
        try:
            stdout_tail, stderr_text = proc.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout_tail, stderr_text = proc.communicate()
        utc_end = r6.utc(time.time())
        full_host_stdout = (
            "".join(host_boot) + "".join(tisch_menu_lines) + "".join(after_request)
            + "".join(operator_anchor_prompt) + "".join(operator_second_prompt)
            + "".join(host_finish_tail) + stdout_tail
        )
        assert proc.returncode == 0, f"U5: Launcher-Lauf gescheitert: {stderr_text}"
        assert final_path.exists(), "U5: der regulaere Abschluss haette __final.json schreiben muessen."

        try:
            helper.stdin.close()
        except BrokenPipeError:
            pass
        try:
            helper.wait(timeout=15)
        except subprocess.TimeoutExpired:
            helper.kill()
            helper.wait()
        helper_stdout_tail = helper.stdout.read()
        helper_stderr_text = helper.stderr.read()
        full_guest_stdout = (
            helper_header_joined + tisch_menu_joined + after_request_joined
            + consent_prompt_joined + guest_first_joined + guest_reflection_joined
            + guest_finish_joined
            + helper_stdout_tail
        )
        # KEIN manuelles `os.close()` auf den rohen Fds hier: `host_reader`/
        # `guest_reader` wickeln `proc.stdout.fileno()`/`helper.stdout.
        # fileno()` -- dieselben Fds verwaltet bereits das jeweilige
        # `Popen`-Objekt (gelesen via `.read()`/`.wait()` oben); ein
        # zusaetzlicher `os.close()` waere ein Doppel-Close desselben Fds.

        # ── Assertion D: persoenliche Rueckkehr re-lesbar -- fuer guest1
        # ueber den echten Produktleser `onboarding.peek` auf der privaten
        # Gastablage (dieselbe Autoritaet wie Szene A `run_scene_v3`); fuer
        # operator1 ueber den echten Operator-Leser `current_saves/
        # operator1.json` (die direkte Host-Current-Autoritaet, s. Report
        # fuer die Herleitung, WARUM `onboarding.peek` fuer operator1 NICHT
        # die aktualisierte Fassung triegt -- `_writeback_registered_guest_
        # saves` schreibt NUR fuer `_table_guest_terminals`-Mitglieder
        # zurueck, operator1 ist keines).
        guest_private = onboarding.peek(guest_onboarding, "guest1")
        assert guest_private is not None and guest_private.final_save is not None, (
            "U5: die abgeschlossene Gastfassung haette ueber onboarding.peek lesbar sein muessen."
        )
        guest_reloaded_char = guest_private.final_save["characters"][0]
        assert guest_reloaded_char["id"] == guest_char_id, guest_reloaded_char
        assert guest_reloaded_char["lvl"] == 2, guest_reloaded_char

        assert operator_current_path.exists(), (
            "U5: der Operator-Eigenstand haette unter current_saves/operator1.json liegen muessen."
        )
        operator_reloaded_block = json.loads(operator_current_path.read_text(encoding="utf-8"))
        operator_reloaded_char = operator_reloaded_block["characters"][0]
        assert operator_reloaded_char["id"] == operator_char_id, operator_reloaded_char
        assert operator_reloaded_char["lvl"] == 2, operator_reloaded_char

        # ── Evidenz.
        r6.write_process_result(
            out_dir, "launcher", argv=argv, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=proc.returncode,
            stdout_text=full_host_stdout, stderr_text=stderr_text,
            pid=proc.pid,
        )
        helper_argv = [str(_GUEST_HELPER), "guest1", str(in_fifo), str(out_fifo)]
        r6.write_process_result(
            out_dir, "guest_helper_process", argv=helper_argv, cwd=str(_REPO_ROOT),
            utc_start=utc_start, utc_end=utc_end, exit_code=helper.returncode,
            stdout_text=full_guest_stdout, stderr_text=helper_stderr_text,
            pid=helper.pid,
        )
        mf.record_process_files(
            "launcher", aussage="u5_operator_leader_launcher_transcript", run_id="U5",
            teilnehmer_figur="operator1", tisch_abschnitt="mesaU5/local-operator1-guest1-section",
        )
        mf.record_process_files(
            "guest_helper_process", aussage="u5_guest_real_helper_process_transcript", run_id="U5",
            teilnehmer_figur="guest1", tisch_abschnitt="mesaU5/local-operator1-guest1-section",
        )
        mf.export_tree(
            run_dir, "run", aussage="u5_run_dir_after_finish", run_id="U5",
            teilnehmer_figur="beide", tisch_abschnitt="mesaU5/local-operator1-guest1-section",
        )
        mf.export_tree(
            guest_onboarding, "guest_onboarding", aussage="u5_guest_private_after_finish",
            run_id="U5", teilnehmer_figur="guest1",
        )
        mf.export_tree(
            op_data / "onboarding", "operator_onboarding", aussage="u5_operator_onboarding_unchanged_snapshot",
            run_id="U5", teilnehmer_figur="operator1",
        )
        mf.export_file(
            calls_log, "gm_calls.jsonl", aussage="u5_gm_double_calls", run_id="U5",
            teilnehmer_figur="beide",
        )
        mf.write_json_body(
            "io_transcript.json",
            {
                "helper_header": helper_header_joined,
                "tisch_numbered_menu": tisch_menu_joined,
                "after_request": after_request_joined,
                "round_join_consent_prompt": consent_prompt_joined,
                "operator_anchor_recipient_line": operator_anchor_joined,
                "guest_first_contribution_recipient_line": guest_first_joined,
                "operator_second_recipient_line": operator_second_joined,
                "guest_reflection_catchup_with_zeitgedanke": guest_reflection_joined,
                "zeitgedanke_seam_fired": zeitgedanke_seam_fired,
                "host_completion_card_tail": host_finish_joined,
                "guest_completion_card_tail": guest_finish_joined,
                "operator_reloaded_char": {"id": operator_reloaded_char["id"], "lvl": operator_reloaded_char["lvl"]},
                "guest_reloaded_char": {"id": guest_reloaded_char["id"], "lvl": guest_reloaded_char["lvl"]},
            },
            aussage="u5_dialog_io_transcript", run_id="U5", teilnehmer_figur="beide",
        )
        mf.write_manifest()
        mf.write_summary({
            "szene": "U5_normalweg_echter_gast_helfer_prozess",
            "aussage": (
                "Operator1 (eigene Figur, Leader) und guest1 (eigene Figur, NICHT Leader) spielen "
                "eine reguläre lokale Tischrunde über den ECHTEN Helfer-Prozess "
                "scripts/zeitriss-gast-terminal.sh (nicht direktes FIFO-Plumbing); regulärer "
                "Abschluss, persönliche Abschlusskarten in BEIDEN Fenstern, persönliche Rückkehr "
                "beider Figuren (lvl 2) über den jeweils echten Leser (onboarding.peek für den "
                "Gast, current_saves/operator1.json für den Operator) wieder lesbar."
            ),
            "echter_neuer_os_prozess_gast": True,
            "echter_neuer_os_prozess_operator": True,
            "gm_anbieter_ist_grenzinjektion": "MMO_SIM_GM_TRANSPORT_DOUBLE, NIE Live-Modell",
            "operator_ist_leader_weil_eigene_figur": True,
            "final_written": final_path.exists(),
            "operator_personal_reload_lvl": operator_reloaded_char["lvl"],
            "guest_personal_reload_lvl": guest_reloaded_char["lvl"],
            "zeitgedanke_seam_fired": zeitgedanke_seam_fired,
        })

        findings["zeitgedanke_seam_fired"] = zeitgedanke_seam_fired
        findings["final_written"] = final_path.exists()
        return findings


def main() -> int:
    if _OUT_ROOT.exists():
        import shutil
        shutil.rmtree(_OUT_ROOT)
    _OUT_ROOT.mkdir(parents=True)
    try:
        run_scene_u5()
        print("OK   U5_normalweg_echter_gast_helfer_prozess")
        return 0
    except AssertionError as e:
        print(f"FAIL U5_normalweg_echter_gast_helfer_prozess: {e}")
        return 1
    except Exception:
        print("ERROR U5_normalweg_echter_gast_helfer_prozess:")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
