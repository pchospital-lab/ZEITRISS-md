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
  (2) test_broken_ref_missing_save_and_pending_compat_handled_without_mutation
  (3) test_failing_gm_double_does_not_block_viewer_and_no_secret_second_start
  (4) test_bogen_control_token_consumes_no_turn_bang_form_still_forwarded
  (5) test_window_open_success_and_failure_fallback_inline_without_aborting

Pure Python, nur `assert`, echter Exitcode, kein Docker/Netzwerk.
"""
from __future__ import annotations

import json
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

        printed.clear()
        with mock.patch.object(sheet_view, "try_open_in_external_terminal", return_value=False):
            session._cmd_show_bogen(speaker_pid="p2")
        out_p2 = "\n".join(printed)
        assert "Bravo" in out_p2 and "Alpha" not in out_p2, (
            "am geteilten Terminal muss GENAU die tatsaechlich eingebende Person "
            f"(speaker_pid) gezeigt werden, nicht pauschal eine andere Figur:\n{out_p2}"
        )
        assert "Geld: 42" in out_p2


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

def test_window_open_uses_plain_argv_no_shell_and_writes_private_tempfile():
    calls = []

    def _fake_popen(argv):
        calls.append(argv)
        return mock.Mock()

    lines = ["Zeile A", "Zeile B mit Umlaut äöü"]
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
