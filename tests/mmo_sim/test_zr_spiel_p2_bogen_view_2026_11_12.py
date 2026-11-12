#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_spiel_p2_bogen_view_2026_11_12.py — ZR-SPIEL-FINISH-P2
Block B (lokaler read-only Charakterbogen), standalone Assert-Skript
(Konvention der datierten `tests/mmo_sim/test_*_2026_*.py` -- `python3 -m
unittest -q` findet die Modulfunktionen hier NICHT, da keine
`unittest.TestCase`; `scripts/smoke.sh` startet solche Dateien additiv
direkt, s. andere `test_f1_*`-Dateien).

Deckt:
  - `mmo_sim/ui/sheet_view.py` (`render_character_sheet`,
    `try_open_in_external_terminal`): reine Projektion, fehlende Felder als
    "nicht gespeichert"/"—", kein Shell-String, kein Erfolg ohne echten
    Prozessstart.
  - `mmo_sim/ui/tui.py:TuiSession._cmd_show_bogen`: Quelle NUR `core.store.
    load_current_save_or_raise` (NICHT `_resolve_active_save`/`_resolve_
    real_active_chrononaut_id`/`_cmd_export` -- keine Nebenwirkungen),
    `/bogen` an `_readline_with_controls` (verbraucht keinen Zug, derselbe
    Prompt läuft weiter), `!bogen` bleibt an DIESEM Leser unveraendert
    normaler (ingame weitergereichter) Text.

Double-Grenze: NUR der Terminal-Fensterstart (`subprocess.Popen`) UND der
GM-Transport sind gedoubelt. `TuiSession`, `core.store`, `PersonaStateStore`,
`onboarding`, `sheet_view.render_character_sheet` laufen ECHT gegen ein
echtes temporaeres Repo-Verzeichnis. Kein Docker/Netzwerk-Call.

Tests:
  (1) test_progress_save_shown_over_older_save_and_correct_active_person
      (jetzt zusaetzlich: Kopfzeile zweier verschiedener Figuren, R-B1)
  (2) test_broken_ref_missing_save_and_pending_compat_handled_without_mutation
  (3) test_failing_gm_double_does_not_block_viewer_and_no_secret_second_start
  (4) test_bogen_control_token_consumes_no_turn_bang_form_still_forwarded
  (5) test_window_open_success_and_failure_fallback_inline_without_aborting

N1-B-Nachzug (R-B1/R-B2, General-Bogenreview `2e7cb4e3`):
  (6) test_header_line_uses_actual_character_not_fixed_zirkel_nadia_sample
  (7) test_header_line_missing_name_and_callsign_shown_honestly_not_as_sample
  (8) test_window_title_contains_header_and_static_hint_not_just_fixed_label
  (9) test_window_open_oserror_branch_with_deterministically_stubbed_emulator
  (10) test_window_open_no_emulator_present_returns_false_without_calling_popen
  (11) test_window_open_early_process_exit_after_successful_popen_falls_back_inline
  (12) test_window_open_long_running_process_after_popen_counts_as_success
  (13) test_bogen_shows_inline_same_prompt_when_emulator_present_but_exits_immediately

Pure Python, nur `assert`, echter Exitcode, kein Docker/Netzwerk.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import traceback
import unittest.mock as mock
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _full_v7_fixture import full_v7_save  # noqa: E402

import mmo_sim.core.store as core_store  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding as ob  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.domain.zeitriss.save_compatibility import build_compat_envelope  # noqa: E402
from mmo_sim.ui import sheet_view  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


def _scripted_input(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


def _onboard(data_dir: Path, participant_id: str, save: dict) -> None:
    """Gemeinsames Testsetup (Muster `test_fix5b_tui_quota_catch_2026_10_23.
    py:_onboard_solo_participant`): Onboarding abschliessen + Persona-State
    anlegen -- Voraussetzung fuer `core.store.publish_current_save`."""
    char_id = save["characters"][0]["id"]
    ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
    ob.start_or_resume(data_dir / "onboarding", participant_id)
    ob.complete_with_save(data_dir / "onboarding", participant_id, save, ZeitrissHarvestValidator(), char_id)
    ob.ensure_participant_persona_state(ps_store, data_dir / "states", participant_id, char_id, save)


def _publish(data_dir: Path, participant_id: str, save: dict) -> None:
    """Veroeffentlicht `save` als neue Current-Version fuer `participant_id`
    -- derselbe Produktweg wie ein echter Import/Rundenabschluss
    (`core.store.publish_current_save`), NICHT Testfixture-Direktschreiben
    an `current_saves/`."""
    ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
    core_store.publish_current_save(
        data_dir / "run", participant_id, save, ps_store, states_dir=data_dir / "states",
    )


def _session(data_dir: Path, participant_id: str, input_lines: list[str], *, gm_transport_factory=None) -> tuple[TuiSession, list[str]]:
    printed: list[str] = []
    session = TuiSession(
        onboarding_dir=data_dir / "onboarding", catalog_dir=data_dir / "catalog",
        participant_id=participant_id,
        input_fn=_scripted_input(input_lines), print_fn=printed.append,
        run_dir=data_dir / "run", states_dir=data_dir / "states", schema_path=_SCHEMA_PATH,
        gm_transport_factory=gm_transport_factory,
    )
    return session, printed


# ── (1): Fortschritt vor Katalogsave, korrekte aktive Person am Terminal ──

def test_progress_save_shown_over_older_save_and_correct_active_person():
    with tempfile.TemporaryDirectory() as tmp_s:
        d = Path(tmp_s)

        save_p1_v1 = full_v7_save("CHR-P1", name="Alpha", wallet=100)
        _onboard(d, "p1", save_p1_v1)
        _publish(d, "p1", save_p1_v1)
        # Fortschritt: EIN weiterer, spaeterer publish ersetzt die aeltere
        # (Katalog-/Erst-)Fassung -- `_cmd_show_bogen` MUSS den NEUESTEN
        # Stand zeigen, nicht die erste Version.
        save_p1_v2 = full_v7_save("CHR-P1", name="Alpha", wallet=9999)
        _publish(d, "p1", save_p1_v2)

        save_p2 = full_v7_save("CHR-P2", name="Bravo", wallet=42)
        _onboard(d, "p2", save_p2)
        _publish(d, "p2", save_p2)

        session, printed = _session(d, "p1", [])
        with mock.patch.object(sheet_view, "try_open_in_external_terminal", return_value=False):
            session._cmd_show_bogen(speaker_pid="p1")
        out_p1 = "\n".join(printed)
        assert "Geld: 9999" in out_p1, (
            f"muss den NEUESTEN (Fortschritts-)Stand zeigen, nicht die aeltere Fassung:\n{out_p1}"
        )
        assert "Geld: 100" not in out_p1
        assert "Alpha" in out_p1 and "Bravo" not in out_p1
        # R-B1: die KOPFzeile (erste Zeile) muss ebenfalls Alpha zeigen -- der
        # vorherige feste Kopf "ZIRKEL · Nadia Kersten" durfte hier NIE stehen.
        header_p1 = printed[0].split("\n")[0]
        assert "ALPHA" in header_p1 and "Alpha" in header_p1, header_p1
        assert "ZIRKEL" not in header_p1 and "Nadia" not in header_p1, header_p1

        printed.clear()
        with mock.patch.object(sheet_view, "try_open_in_external_terminal", return_value=False):
            session._cmd_show_bogen(speaker_pid="p2")
        out_p2 = "\n".join(printed)
        assert "Bravo" in out_p2 and "Alpha" not in out_p2, (
            "am geteilten Terminal muss GENAU die tatsaechlich eingebende Person "
            f"(speaker_pid) gezeigt werden, nicht pauschal eine andere Figur:\n{out_p2}"
        )
        assert "Geld: 42" in out_p2
        # Zweite, eindeutig ANDERE Figur -- die Kopfzeile darf keine
        # Beispielidentitaet (ZIRKEL/Nadia) UND nicht die der ERSTEN Figur
        # (Alpha) zeigen; sie muss zur tatsaechlich angezeigten Figur passen.
        header_p2 = printed[0].split("\n")[0]
        assert "BRAVO" in header_p2 and "Bravo" in header_p2, header_p2
        assert "ZIRKEL" not in header_p2 and "Nadia" not in header_p2, header_p2
        assert "Alpha" not in header_p2 and "ALPHA" not in header_p2, header_p2
        assert header_p1 != header_p2, "zwei verschiedene Figuren muessen auch im Kopf verschieden sein"


# ── (6)/(7): R-B1 -- dynamischer Kopf direkt auf `render_character_sheet` ──

def test_header_line_uses_actual_character_not_fixed_zirkel_nadia_sample():
    """Direkter Unit-Nachweis (ohne TUI-Session) fuer `render_character_
    sheet`: zwei eindeutig verschiedene Figuren muessen auch im KOPF
    (erste Zeile) verschieden UND korrekt sein -- keine der beiden darf
    die alte Beispielidentitaet "ZIRKEL"/"Nadia Kersten" zeigen."""
    save_alpha = {"characters": [{"id": "CHR-A", "name": "Juliet", "callsign": "WHISKEY"}]}
    save_bravo = {"characters": [{"id": "CHR-B", "name": "Kilo", "callsign": "TANGO"}]}

    lines_alpha = sheet_view.render_character_sheet(save_alpha, persona_key="a")
    lines_bravo = sheet_view.render_character_sheet(save_bravo, persona_key="b")

    assert "WHISKEY" in lines_alpha[0] and "Juliet" in lines_alpha[0], lines_alpha[0]
    assert "ZIRKEL" not in lines_alpha[0] and "Nadia" not in lines_alpha[0], lines_alpha[0]

    assert "TANGO" in lines_bravo[0] and "Kilo" in lines_bravo[0], lines_bravo[0]
    assert "ZIRKEL" not in lines_bravo[0] and "Nadia" not in lines_bravo[0], lines_bravo[0]
    assert "WHISKEY" not in lines_bravo[0] and "Juliet" not in lines_bravo[0], (
        "Figur B darf im Kopf nicht die Identitaet von Figur A tragen"
    )
    assert lines_alpha[0] != lines_bravo[0]
    # Die zweite (personenunabhaengige) Snapshot-Hinweiszeile bleibt erhalten.
    assert "statisch" in lines_alpha[1].lower() and "GM-Bogen" in lines_alpha[1]
    assert lines_alpha[1] == lines_bravo[1]


def test_header_line_missing_name_and_callsign_shown_honestly_not_as_sample():
    """Fehlende Name/Callsign-Werte muessen EHRLICH als `NOT_SAVED`
    erscheinen -- keinesfalls als Nadia/ZIRKEL-Beispieldefault (R-B1
    verlangt ausdrueckllich, dass fehlende Namen nicht zu Nadia/ZIRKEL
    werden)."""
    save_no_identity = {"characters": [{"id": "CHR-X"}]}  # kein name, kein callsign
    lines = sheet_view.render_character_sheet(save_no_identity, persona_key="x")
    header = lines[0]
    assert sheet_view.NOT_SAVED in header, header
    assert "ZIRKEL" not in header and "Nadia" not in header, header
    assert header.count(sheet_view.NOT_SAVED) == 2, (
        f"sowohl fehlender Name als auch fehlendes Callsign muessen ehrlich markiert sein:\n{header}"
    )


def test_window_title_contains_header_and_static_hint_not_just_fixed_label():
    """R-B1-Sichtbefund: der vorherige feste Fenstertitel 'ZEITRISS - Bogen'
    zeigte beim tatsaechlichen Fensterstart weder Figur noch Snapshot-
    Hinweis sichtbar (Inhalt scrollt aus dem Sichtbereich). Der Titel muss
    jetzt die tatsaechliche Kopfzeile UND einen statischen Hinweis tragen."""
    save = {"characters": [{"id": "CHR-Y", "name": "Yankee", "callsign": "ZULU"}]}
    lines = sheet_view.render_character_sheet(save, persona_key="y")

    calls = []

    def _fake_popen(argv):
        calls.append(argv)
        return _running_proc_mock()

    with mock.patch.object(sheet_view.shutil, "which", return_value="/usr/bin/xterm"):
        ok = sheet_view.try_open_in_external_terminal(lines, popen_fn=_fake_popen)
    assert ok is True
    argv = calls[0]
    assert argv[0] == "xterm" and argv[1] == "-T", argv
    title = argv[2]
    assert "ZULU" in title and "Yankee" in title, title
    assert "statisch" in title.lower(), title
    tmp_candidates = [a for a in argv if a.endswith(".txt")]
    Path(tmp_candidates[0]).unlink(missing_ok=True)


# ── (2): defekte Referenz / kein Save / pending-compat -- keine Mutation ──

def test_broken_ref_missing_save_and_pending_compat_handled_without_mutation():
    with tempfile.TemporaryDirectory() as tmp_s:
        d = Path(tmp_s)

        # (a) Noch gar kein Save -- ehrliche Meldung, keine Datei entsteht.
        session_a, printed_a = _session(d, "frisch", [])
        with mock.patch.object(sheet_view, "try_open_in_external_terminal", return_value=False):
            session_a._cmd_show_bogen()
        assert "Noch kein gespeicherter Charakterbogen vorhanden" in "\n".join(printed_a)
        assert not (d / "run" / "current_saves").exists(), (
            "eine reine Anzeige darf KEINE current_saves/-Struktur anlegen"
        )

        # (b) Bekannte, aber gerade UNLESBARE Autoritaet (korrupte Versions-
        # datei, Ref zeigt weiter drauf) -- klarer Lesefehler, KEIN stiller
        # Rueckfall auf eine alte Fassung, UND keine Mutation der korrupten
        # Datei/des Persona-States durch den Anzeigeversuch selbst.
        save_b = full_v7_save("CHR-B", name="Charlie")
        _onboard(d, "b", save_b)
        _publish(d, "b", save_b)
        version_path = d / "run" / "current_saves" / "b__versions" / "0001.json"
        assert version_path.is_file()
        version_path.write_text("{NICHT VALIDES JSON", encoding="utf-8")
        before_bytes = version_path.read_bytes()
        state_path = d / "states" / "b.json"
        state_before = state_path.read_bytes() if state_path.is_file() else None

        session_b, printed_b = _session(d, "b", [])
        with mock.patch.object(sheet_view, "try_open_in_external_terminal", return_value=False):
            session_b._cmd_show_bogen()
        out_b = "\n".join(printed_b)
        assert "Noch kein gespeicherter Charakterbogen vorhanden" not in out_b, (
            "eine BEKANNTE, nur gerade unlesbare Autoritaet ist NICHT dasselbe wie "
            "'kein Save' -- stiller Rueckfall auf diese Deutung waere falsch"
        )
        assert "nicht lesbar" in out_b.lower() or "nicht abrufbar" in out_b.lower(), out_b
        assert "Charlie" not in out_b, "keine alte/erratene Fassung als Ersatz anzeigen"
        assert version_path.read_bytes() == before_bytes, "die korrupte Datei bleibt unveraendert (reiner Lesezugriff)"
        if state_before is not None:
            assert state_path.read_bytes() == state_before, "Persona-State bleibt unveraendert"

        # (c) Ein noch nicht adoptierter Pending-Compat-Umschlag ohne jeden
        # echten Current-Save -- `_cmd_show_bogen` nutzt NUR `load_current_
        # save_or_raise` und darf den Umschlag NICHT adoptieren/anzeigen
        # (anders als `_resolve_active_save`).
        # Persona-State valide ueber denselben Weg wie jede andere Testfigur
        # anlegen (`_onboard`) -- OHNE `_publish`, damit tatsaechlich noch
        # KEIN echter Current-Save existiert.
        save_c = full_v7_save("CHR-C", name="Charlie-Onboard")
        _onboard(d, "c", save_c)
        envelope = build_compat_envelope(
            envelope_version=1, repair_key="repair-c", char_id="CHR-C-COMPAT",
            participant_id="c", operation_key="op-1", table_id=None, section_id=None,
            raw_responses=[], best_view={"characters": [{"id": "CHR-C-COMPAT", "name": "Delta-Pending"}]},
            last_valid=None, created_ts=1.0,
        )
        compat_dir = d / "run" / "save_compat" / "repair-c"
        compat_dir.mkdir(parents=True)
        compat_path = compat_dir / "0001.json"
        compat_path.write_text(json.dumps(envelope), encoding="utf-8")
        compat_before = compat_path.read_bytes()

        session_c, printed_c = _session(d, "c", [])
        with mock.patch.object(sheet_view, "try_open_in_external_terminal", return_value=False):
            session_c._cmd_show_bogen()
        out_c = "\n".join(printed_c)
        assert "Noch kein gespeicherter Charakterbogen vorhanden" in out_c, (
            f"ohne echten Current-Save darf ein Pending-Compat-Umschlag NICHT als Bogen "
            f"erscheinen:\n{out_c}"
        )
        assert "Delta-Pending" not in out_c
        assert compat_path.read_bytes() == compat_before, "der Umschlag darf durch die Anzeige NICHT adoptiert/veraendert werden"
        assert not (d / "run" / "current_saves" / "c__versions").exists(), (
            "die Anzeige darf keinen neuen Current-Save aus dem Umschlag erzeugen"
        )


# ── (3): fehlschlagende GM-/Netzdoubles blockieren den Viewer nicht ───────

def test_failing_gm_double_does_not_block_viewer_and_no_secret_second_start():
    class _ExplodingGm:
        def __init__(self):
            self.calls = 0

        def turn(self, *a, **kw):
            self.calls += 1
            raise AssertionError("GM-Transport darf fuer die Bogen-Anzeige NIEMALS aufgerufen werden")

    with tempfile.TemporaryDirectory() as tmp_s:
        d = Path(tmp_s)
        save = full_v7_save("CHR-E", name="Echo", wallet=7)
        _onboard(d, "e", save)
        _publish(d, "e", save)

        gm = _ExplodingGm()
        before_catalog = sorted(p.relative_to(d) for p in d.rglob("*") if "catalog" in p.parts)
        session, printed = _session(d, "e", [], gm_transport_factory=lambda: gm)
        with mock.patch.object(sheet_view, "try_open_in_external_terminal", return_value=False):
            session._cmd_show_bogen()
        out = "\n".join(printed)
        assert "Echo" in out and "Geld: 7" in out
        assert gm.calls == 0, "lokaler Bogen darf KEINEN Modell-/Netzaufruf ausloesen"
        after_catalog = sorted(p.relative_to(d) for p in d.rglob("*") if "catalog" in p.parts)
        assert before_catalog == after_catalog, (
            "kein heimlicher zweiter Spielstart/keine neue Katalogbindung durch die Anzeige"
        )


# ── (4): '/bogen' verbraucht keinen Zug, '!bogen' bleibt Ingame-Text ─────

def test_bogen_slash_form_at_control_reader_loops_same_prompt_without_consuming_input():
    with tempfile.TemporaryDirectory() as tmp_s:
        d = Path(tmp_s)
        save = full_v7_save("CHR-G", name="Golf")
        _onboard(d, "g", save)
        _publish(d, "g", save)

        session, printed = _session(d, "g", ["/bogen", "Ich handle entschlossen."])
        with mock.patch.object(sheet_view, "try_open_in_external_terminal", return_value=False):
            text, control = session._readline_with_controls(
                "Zug: ", context="Spielzug", history=[], speaker_pid="g", bypass_claim=True,
            )
        assert control is None and text == "Ich handle entschlossen.", (
            "'/bogen' muss intern abgefangen werden und DENSELBEN Prompt fortsetzen -- "
            f"der zweite Skriptwert muss als normaler Zugtext zurueckkommen: {(text, control)!r}"
        )
        out = "\n".join(printed)
        assert "Golf" in out, "der Bogen muss tatsaechlich angezeigt worden sein, bevor der Prompt weiterlief"


def test_ingame_bang_bogen_at_same_reader_passes_through_unchanged():
    """Ingame bleibt '!bogen' (kein Slash) unveraendert normaler, an die SL
    weiterzureichender Text -- '/bogen' und '!bogen' duerfen an DIESEM
    Leser NICHT dieselbe Wirkung haben."""
    with tempfile.TemporaryDirectory() as tmp_s:
        d = Path(tmp_s)
        session, printed = _session(d, "h", ["!bogen"])
        text, control = session._readline_with_controls(
            "Zug: ", context="Spielzug", history=[], speaker_pid="h", bypass_claim=True,
        )
        assert (text, control) == ("!bogen", None), (
            "'!bogen' (Bang-Form) darf an diesem Leser NICHT abgefangen werden -- "
            f"es muss unveraendert als Text zurueckkommen: {(text, control)!r}"
        )
        assert printed == [], "kein lokaler Bogen-Druck fuer die unveraendert weitergereichte Bang-Form"


# ── (5): Fensteroeffnung -- Erfolg/Fehlschlag, Snapshot pro Aufruf ───────

def _running_proc_mock():
    """Prozess-Double, das nach dem Start noch LAEUFT (`Popen.wait` liefert
    innerhalb der Schonfrist keinen Exitcode, sondern `TimeoutExpired` --
    derselbe Vertrag wie ein echtes, noch offenes Fenster)."""
    proc = mock.Mock()
    proc.wait.side_effect = subprocess.TimeoutExpired(cmd="x", timeout=0.4)
    return proc


def _early_exit_proc_mock(returncode: int = 0):
    """Prozess-Double, das INNERHALB der Schonfrist schon wieder beendet ist
    (z.B. Emulator ohne `DISPLAY`) -- `Popen.wait` liefert sofort einen
    Exitcode statt zu blocken."""
    proc = mock.Mock()
    proc.wait.return_value = returncode
    return proc


def test_window_open_uses_plain_argv_no_shell_and_writes_private_tempfile():
    calls = []

    def _fake_popen(argv):
        calls.append(argv)
        return _running_proc_mock()

    lines = ["Zeile A", "Zeile B mit Umlaut äöü"]
    # Emulatorpraesenz deterministisch stubben: der headless CI-Runner hat
    # weder xterm noch gnome-terminal installiert -- ohne diesen Patch
    # kurzschliesst try_open_in_external_terminal via `shutil.which(...) is
    # None` auf False, und der argv-/tempfile-Pfad, den genau dieser Test
    # prueft, wird nie betreten (lokal gruen, weil hier ein Emulator liegt;
    # auf CI rot). Mit gestubbtem which WIRD ein Emulator gefunden -> der
    # beabsichtigte Pfad wird umgebungsunabhaengig geprueft. Reiner Test-
    # Double, keine Produktcode-Aenderung.
    with mock.patch.object(sheet_view.shutil, "which", return_value="/usr/bin/xterm"):
        ok = sheet_view.try_open_in_external_terminal(lines, popen_fn=_fake_popen)
    assert ok is True
    assert len(calls) == 1
    argv = calls[0]
    assert isinstance(argv, list) and all(isinstance(a, str) for a in argv), (
        "reiner argv-Aufruf, keine Shell-Zeichenkette/Interpolation"
    )
    assert argv[0] in ("xterm", "gnome-terminal")
    tmp_candidates = [a for a in argv if a.endswith(".txt")]
    assert tmp_candidates, argv
    written = Path(tmp_candidates[0]).read_text(encoding="utf-8")
    assert "Zeile A" in written and "Zeile B mit Umlaut äöü" in written
    Path(tmp_candidates[0]).unlink(missing_ok=True)


# ── (9)/(10)/(11)/(12): R-B2 -- frueher Prozessausgang, OSError, kein
#    Emulator, positiver Start deterministisch getrennt ────────────────

def test_window_open_oserror_branch_with_deterministically_stubbed_emulator():
    """Der VORHERIGE OSError-Test stubbte `shutil.which` nicht -- auf einem
    headless Runner ohne xterm/gnome-terminal bricht die Kandidatenschleife
    schon VOR dem `popen_fn`-Aufruf ab (`continue`), und der Test wird aus
    dem falschen Grund gruen. Mit gestubbter Emulatorpraesenz wird der
    OSError-Zweig tatsaechlich erreicht."""
    def _always_fails(argv):
        raise OSError("kein Emulator erreichbar (simuliert)")

    with mock.patch.object(sheet_view.shutil, "which", return_value="/usr/bin/xterm"):
        ok = sheet_view.try_open_in_external_terminal(["X"], popen_fn=_always_fails)
    assert ok is False, "ein fehlgeschlagener Fensterstart muss False liefern, damit der Aufrufer inline zeigt"


def test_window_open_no_emulator_present_returns_false_without_calling_popen():
    calls = []

    def _popen_should_not_be_called(argv):
        calls.append(argv)
        return _running_proc_mock()

    with mock.patch.object(sheet_view.shutil, "which", return_value=None):
        ok = sheet_view.try_open_in_external_terminal(["X"], popen_fn=_popen_should_not_be_called)
    assert ok is False
    assert calls == [], "ohne bekannten Emulator darf gar kein Prozessstart versucht werden"


def test_window_open_early_process_exit_after_successful_popen_falls_back_inline():
    """R-B2 (belegter Fehler): `try_open_in_external_terminal` gab vorher
    `True` zurueck, sobald `popen_fn` OHNE OSError zurueckkehrte -- auch
    wenn der Kindprozess (z.B. fehlendes `DISPLAY`) unmittelbar danach
    wieder beendet war. Jetzt: ein frueher Exit (hier returncode=1,
    beliebiger Code) innerhalb der Schonfrist zaehlt NICHT als offenes
    Fenster."""
    def _popen_exits_immediately(argv):
        return _early_exit_proc_mock(returncode=1)

    with mock.patch.object(sheet_view.shutil, "which", return_value="/usr/bin/xterm"):
        ok = sheet_view.try_open_in_external_terminal(["X"], popen_fn=_popen_exits_immediately)
    assert ok is False, "ein unmittelbar wieder beendeter Kindprozess darf NICHT als offenes Fenster gelten"


def test_window_open_long_running_process_after_popen_counts_as_success():
    """Gegenprobe zu (11): laeuft der Prozess nach der Schonfrist noch
    (`TimeoutExpired`), gilt der Fensterstart weiterhin als erfolgreich --
    der Fix darf einen echten erfolgreichen Start nicht faelschlich
    zurueckweisen."""
    def _popen_keeps_running(argv):
        return _running_proc_mock()

    with mock.patch.object(sheet_view.shutil, "which", return_value="/usr/bin/xterm"):
        ok = sheet_view.try_open_in_external_terminal(["X"], popen_fn=_popen_keeps_running)
    assert ok is True


def test_window_open_failure_returns_false_for_inline_fallback():
    def _always_fails(argv):
        raise OSError("kein Emulator erreichbar (simuliert)")

    ok = sheet_view.try_open_in_external_terminal(["X"], popen_fn=_always_fails)
    assert ok is False, "ein fehlgeschlagener Fensterstart muss False liefern, damit der Aufrufer inline zeigt"


def test_bogen_falls_back_to_inline_display_on_window_failure_without_aborting_prompt():
    with tempfile.TemporaryDirectory() as tmp_s:
        d = Path(tmp_s)
        save = full_v7_save("CHR-I", name="India", wallet=55)
        _onboard(d, "i", save)
        _publish(d, "i", save)

        session, printed = _session(d, "i", [])
        with mock.patch.object(sheet_view, "try_open_in_external_terminal", return_value=False):
            session._cmd_show_bogen()
        out = "\n".join(printed)
        assert "India" in out and "Geld: 55" in out, (
            f"bei Fensterstartfehler muss derselbe Bogen inline erscheinen:\n{out}"
        )

        # Fensterstartfehler darf die Session NICHT beenden -- ein weiterer
        # normaler Aufruf (bewusstes Neuoeffnen) funktioniert unveraendert.
        printed.clear()
        save_v2 = full_v7_save("CHR-I", name="India", wallet=999)
        _publish(d, "i", save_v2)
        with mock.patch.object(sheet_view, "try_open_in_external_terminal", return_value=False):
            session._cmd_show_bogen()
        out2 = "\n".join(printed)
        assert "Geld: 999" in out2, (
            "ein bewusstes Neuoeffnen NACH einem neuen Save muss den NEUEN Stand zeigen "
            f"(kein eingefrorener Altstand):\n{out2}"
        )


# ── (13): _cmd_show_bogen bleibt inline, wenn der Emulator vorhanden ist,
#    aber sein Kindprozess unmittelbar beendet ──────────────────────────

def test_bogen_shows_inline_same_prompt_when_emulator_present_but_exits_immediately():
    """Geht NICHT ueber einen vollstaendigen Mock von
    `try_open_in_external_terminal` (wie Tests 1-5) und NICHT ueber ein
    `popen_fn`-Double (das `_cmd_show_bogen` gar nicht durchreicht) --
    `_cmd_show_bogen` ruft die Funktion mit ihrem ECHTEN Default
    `popen_fn=subprocess.Popen` auf (als Default-Parameter bereits beim
    Funktionsdefinieren gebunden; ein spaeteres `mock.patch.object(subprocess,
    'Popen', ...)` haette darauf KEINE Wirkung). Deshalb wird hier ein
    tatsaechlich existierender, aber augenblicklich beendender Realprozess
    verwendet (`/bin/true` statt eines echten Terminalemulators) --
    dasselbe Verhalten wie ein Emulator ohne `DISPLAY` (R-B2), ohne
    Produktcode fuer den Test anzupassen. Erwartet: derselbe Bogen
    erscheint inline, UND '/bogen' am Kontrollleser setzt denselben
    Prompt fort (keine Session-Unterbrechung durch den Fensterfehler)."""
    with tempfile.TemporaryDirectory() as tmp_s:
        d = Path(tmp_s)
        save = full_v7_save("CHR-K", name="Kilo", wallet=321)
        _onboard(d, "k", save)
        _publish(d, "k", save)

        session, printed = _session(d, "k", ["/bogen", "Weiter geht's."])

        fake_candidates = (("true", lambda title: []),)
        with mock.patch.object(sheet_view, "_TERMINAL_CANDIDATES", fake_candidates), \
             mock.patch.object(sheet_view.shutil, "which", return_value="/bin/true"):
            text, control = session._readline_with_controls(
                "Zug: ", context="Spielzug", history=[], speaker_pid="k", bypass_claim=True,
            )
        assert control is None and text == "Weiter geht's.", (
            f"ein fruehzeitig beendeter Emulatorprozess darf den Prompt NICHT abbrechen: {(text, control)!r}"
        )
        out = "\n".join(printed)
        assert "Kilo" in out and "Geld: 321" in out, (
            f"bei frueh gescheitertem Fensterstart muss derselbe Bogen inline erscheinen:\n{out}"
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
