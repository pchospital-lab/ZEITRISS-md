#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_r5_synthetic_creation_process_journey_2026_10_06.py
— W19/F03 (ZEITRISS Terminal UX-1, R5): ENDLICHE synthetische Erschaffung
bis zu einem gueltigen v7-Save UEBER DEN ECHTEN Erschaffungsvertrag (`ui/
tui.py:_cmd_new_or_switch_character` -> `core/creation_service.
run_admitted_creation_dialog`), gespielt gegen die ECHTE `scripts/
mmo_sim.py`-Runtime in ECHTEN, EIGENSTAENDIGEN Subprozessen (Muster 1:1 aus
`e2e_real_subprocess_dialog.py`/`test_p2_community_creation_real_subprocess.py`
wiederverwendet) -- KEIN direktes Speichern/keine Save-Injektion als
Shortcut. Die Fake-SL (`_ux1_r5_synthetic_creation_support.
CreationCapableSmartGmServer`) sitzt AUSSCHLIESSLICH an der aeusseren GM-/
Persona-Transportgrenze.

BELEGTRENNUNG (Brief-Auflage "Erschaffung-vs-Bestandsfixture im Beleg klar
trennen"):
  - "ECHTE ERSCHAFFUNG GESTARTET" markiert jede Figur, die durch den echten
    SL-Erschaffungsdialog gegen die Fake-SL entstanden ist (Server-Bucket
    `srv.creation_calls`, char_id-Format `chrono-synth-...`).
  - "BESTANDSFIXTURE/EXTERN" markiert die in `test_external_json_import_
    without_overwriting_existing_figure` ueber 'i' importierte, VORGEFERTIGTE
    externe v7-JSON -- KEINE Erschaffung ueber die Fake-SL, reiner
    Importpfad (anderer, bereits bestehender Produktweg)."""
from __future__ import annotations

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

from _full_v7_fixture import full_v7_save  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
import _a24_local_support as sup  # noqa: E402
from _ux1_r5_synthetic_creation_support import (  # noqa: E402
    CREATION_SIGNATURE,
    CreationCapableSmartGmServer,
    creation_char_id,
)

MMO_SIM = _REPO_ROOT / "scripts" / "mmo_sim.py"


def _run(data_dir: Path, participant: str, stdin_text: str, env_extra: dict, timeout: int = 30) -> subprocess.CompletedProcess:
    import os
    env = dict(os.environ)
    env.update(env_extra)
    cmd = [sys.executable, str(MMO_SIM), "--data-dir", str(data_dir), "--participant", participant]
    return subprocess.run(cmd, input=stdin_text, capture_output=True, text=True, env=env, cwd=str(data_dir), timeout=timeout)


def _env_for(srv: CreationCapableSmartGmServer) -> dict:
    return {"OPENWEBUI_URL": srv.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC_UX1_R5_KEY"}


def _catalog_figure_files(data_dir: Path) -> list[Path]:
    fdir = data_dir / "catalog" / "figures"
    return sorted(fdir.glob("*.json")) if fdir.is_dir() else []


def test_finite_creation_to_real_v7_save_then_solo_round_next_turn_and_completion():
    """Kernvertrag F03 Punkt 1+2: der Mensch ('n' am Hauptmenue, kein
    'neu'-Zusatzschritt bei leerem Katalog) durchlaeuft den ECHTEN
    Erschaffungsdialog gegen die Fake-SL bis zu einem gueltigen v7-Save
    (GENAU EIN Frage-Call + GENAU EIN Save-Call -- endlich, kein direktes
    Speichern), danach eine echte Solo-Runde ('l' ohne Gast-Tokens) mit
    MINDESTENS EINEM echten Zwischenturn ('Szene N') VOR dem Abschluss
    (`complete_after=2`), bis zum echten Abschluss (`Abschnitt
    abgeschlossen:`). ECHTE ERSCHAFFUNG GESTARTET (kein Bestandsfixture)."""
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        write_test_profile(data_dir / "run")
        registry_dir = data_dir / "registry"
        leader = sup.register_human(registry_dir, "Solo-T")
        pid = leader.participant_id
        table_id, section_id = f"local-{pid}", f"local-{pid}-section"

        with CreationCapableSmartGmServer(table_id, section_id, complete_after=2) as srv:
            env = _env_for(srv)
            stdin_text = "n\nIch packe leichte Ausruestung und waehle einen Rufnamen.\nl\nIch sichere die Umgebung.\nIch beobachte weiter.\n\nx\n"
            proc = _run(data_dir, pid, stdin_text, env)
            assert proc.returncode == 0, f"echter Subprozess fehlgeschlagen: {proc.stderr[-2000:]}\n{proc.stdout[-2000:]}"

            # Erschaffung: GENAU EIN Frage-Call, GENAU EIN Save-Call (endlich).
            assert len(srv.creation_calls) == 2, (
                f"Fake-SL-Erschaffungszweig haette genau 2x real aufgerufen werden muessen "
                f"(1 Frage + 1 Save): {len(srv.creation_calls)}"
            )
            first_creation_opening = srv.creation_calls[0]["messages"][0]["content"]
            assert CREATION_SIGNATURE in first_creation_opening, (
                "Erschaffung muss ueber die ECHTE, in ui/tui.py hartkodierte Eroeffnungszeile "
                f"laufen, nicht ueber eine Testfixture: {first_creation_opening!r}"
            )
            assert "Erschaffungsdialog gestartet" in proc.stdout
            assert "Erschaffung abgeschlossen: char_id=" in proc.stdout

            # Spiel: mindestens EIN echter Zwischenturn ("Szene") VOR dem
            # Abschluss -- kein Sofortabschluss ohne jeden weiteren Turn.
            assert len(srv.calls) >= 2, f"Solo-Runde haette mindestens 2 echte GM-Turns gebraucht: {len(srv.calls)}"
            assert "Szene 1:" in proc.stdout, "kein echter Zwischenturn vor dem Abschluss im Beleg sichtbar"
            assert "Abschnitt abgeschlossen:" in proc.stdout, proc.stdout[-800:]

            # Die tatsaechlich gespeicherte Figur stammt NACHWEISLICH aus der
            # Fake-SL-Erschaffung (char_id-Format), nicht aus einer Fixture-
            # Datei (`internal/qa/harness/lobby/fixtures/saves/*.json` nutzt
            # NIE das Praefix `chrono-synth-`).
            figure_files = _catalog_figure_files(data_dir)
            assert len(figure_files) == 1, figure_files
            saved = json.loads(figure_files[0].read_text(encoding="utf-8"))
            # Darstellungsmigration (02_TESTVERTRAG.md): gelesener
            # persoenlicher Save, Export-Schema kennt auf Figurenebene nur
            # `id` (additionalProperties:false), kein zusaetzliches
            # `char_id`. Gleicher Wert/gleiche Identitaet.
            char_id = saved["characters"][0]["id"]
            assert char_id.startswith("chrono-synth-"), f"kein per Fake-SL-Erschaffung erzeugter char_id: {char_id}"


def test_pause_then_real_separate_process_resumes_same_state():
    """Kernvertrag F03 Punkt 2 (Solo-Reise an echter Prozessgrenze):
    Prozess 1 erschafft die Figur und spielt GENAU EINEN Zwischenturn,
    dann real-pausiert (EOF WAEHREND des laufenden Abschnitts, kein
    expliziter Abschluss). Prozess 2 ist ein ECHTER, SEPARATER
    Subprozess MIT EINEM FRISCHEN `CreationCapableSmartGmServer` (leerer
    Prozessspeicher) -- Fortsetzen (`fortsetzen`) bindet denselben Tisch
    (`_cmd_menu_fortsetzen`), der naechste Spielzug fuehrt zum ECHTEN
    Abschluss. Keine zweite Figur, keine doppelte Erschaffung, dieselbe
    char_id vorher/nachher."""
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        write_test_profile(data_dir / "run")
        registry_dir = data_dir / "registry"
        leader = sup.register_human(registry_dir, "Solo-T-Resume")
        pid = leader.participant_id
        table_id, section_id = f"local-{pid}", f"local-{pid}-section"

        with CreationCapableSmartGmServer(table_id, section_id, complete_after=2) as srv1:
            env1 = _env_for(srv1)
            # Erschaffung + GENAU EIN Spielzug, dann EOF (kein 'x', kein
            # Abschluss) -- echte Pause WAEHREND des offenen Abschnitts.
            stdin1 = "n\nIch packe leicht.\nl\nIch sichere die Umgebung.\n"
            proc1 = _run(data_dir, pid, stdin1, env1)
            assert proc1.returncode == 0, proc1.stderr[-2000:]
            assert "Erschaffung abgeschlossen: char_id=" in proc1.stdout
            assert "Abschnitt abgeschlossen:" not in proc1.stdout, (
                "Vorbedingung verletzt: Prozess 1 darf den Abschnitt noch NICHT abschliessen"
            )
            assert len(srv1.creation_calls) == 2
            assert len(srv1.calls) == 1, f"Prozess 1 soll genau 1 echten Spielturn ausloesen: {len(srv1.calls)}"

        figure_files_before = _catalog_figure_files(data_dir)
        assert len(figure_files_before) == 1
        # Darstellungsmigration (02_TESTVERTRAG.md): gelesener persoenlicher
        # Save, Export-Schema kennt auf Figurenebene nur `id`.
        char_id_before = json.loads(figure_files_before[0].read_text(encoding="utf-8"))["characters"][0]["id"]
        bytes_before = figure_files_before[0].read_bytes()

        # Prozess 2: ECHTER, SEPARATER Subprozess MIT NEUER Serverinstanz
        # (leerer Prozessspeicher) -- Restart-Sicherheit wird real geprueft,
        # nicht nur behauptet.
        with CreationCapableSmartGmServer(table_id, section_id, complete_after=2) as srv2:
            env2 = _env_for(srv2)
            stdin2 = "fortsetzen\nIch beobachte weiter und handle vorsichtig.\n\nx\n"
            proc2 = _run(data_dir, pid, stdin2, env2)
            assert proc2.returncode == 0, proc2.stderr[-2000:]
            assert "Erschaffungsdialog gestartet" not in proc2.stdout, (
                "Prozess 2 darf KEINE zweite Erschaffung starten -- die Figur existiert bereits"
            )
            assert len(srv2.creation_calls) == 0, "Prozess 2 darf keinen Erschaffungs-Request ausloesen"
            assert "Abschnitt abgeschlossen:" in proc2.stdout, (
                f"Prozess 2 (neuer, separater Prozess) haette den Abschnitt echt abschliessen "
                f"muessen: {proc2.stdout[-1000:]}"
            )

        figure_files_after = _catalog_figure_files(data_dir)
        assert len(figure_files_after) == 1, "keine zweite/zusaetzliche Figur durch den Resume"
        # Darstellungsmigration (02_TESTVERTRAG.md): gelesener persoenlicher
        # Save, Export-Schema kennt auf Figurenebene nur `id`.
        char_id_after = json.loads(figure_files_after[0].read_text(encoding="utf-8"))["characters"][0]["id"]
        assert char_id_after == char_id_before, (
            f"derselbe Stand erwartet, nicht dieselbe char_id: {char_id_before!r} != {char_id_after!r}"
        )
        assert figure_files_after[0].read_bytes() == bytes_before, (
            "Figur-Archivbytes duerfen sich durch den reinen Fortsetzen-Spielzug nicht aendern"
        )


def test_second_own_figure_via_real_creation_does_not_overwrite_first():
    """Kernvertrag F03 Punkt 3 (zweite eigene Figur): nach der ersten echten
    Erschaffung startet die Person ueber 'n' -> 'neu' eine BEWUSST ZWEITE,
    ebenfalls echte Erschaffung gegen dieselbe Fake-SL. ECHTE ERSCHAFFUNG
    GESTARTET fuer BEIDE Figuren -- die erste bleibt byteidentisch
    erhalten, die zweite bekommt eine ECHT ANDERE char_id (kein Konflikt/
    HOLD, kein Ueberschreiben)."""
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        write_test_profile(data_dir / "run")
        registry_dir = data_dir / "registry"
        leader = sup.register_human(registry_dir, "Solo-T-Second")
        pid = leader.participant_id
        table_id, section_id = f"local-{pid}", f"local-{pid}-section"

        with CreationCapableSmartGmServer(table_id, section_id, complete_after=2) as srv:
            env = _env_for(srv)
            stdin_text = (
                "n\nIch packe leicht.\n"
                "n\nneu\nIch waehle diesmal schwere Ausruestung.\n"
                "\n"  # "Bekannte Persona zu einem gemeinsamen Frischstart einladen" -- leer = nein.
                "s\nx\n"
            )
            proc = _run(data_dir, pid, stdin_text, env)
            assert proc.returncode == 0, proc.stderr[-2000:]
            assert proc.stdout.count("Erschaffung abgeschlossen: char_id=") == 2, (
                f"beide Erschaffungen muessen real abgeschlossen werden: {proc.stdout}"
            )
            assert "angehalten" not in proc.stdout, (
                f"die zweite echte Erschaffung darf NICHT am B2-OWNER-Konfliktguard haengen bleiben "
                f"(Fake-SL muss eine ECHT ANDERE Figur liefern): {proc.stdout[-1500:]}"
            )
            assert len(srv.creation_calls) == 4, (
                f"zwei vollstaendige Erschaffungen = 2x(Frage+Save) = 4 Calls: {len(srv.creation_calls)}"
            )

        figure_files = _catalog_figure_files(data_dir)
        assert len(figure_files) == 2, figure_files
        # Darstellungsmigration (02_TESTVERTRAG.md): gelesene persoenliche
        # Saves, Export-Schema kennt auf Figurenebene nur `id`.
        char_ids = sorted(json.loads(f.read_text(encoding="utf-8"))["characters"][0]["id"] for f in figure_files)
        assert len(set(char_ids)) == 2, f"beide Figuren muessen unterschiedliche char_ids haben: {char_ids}"
        assert "Katalog-Eintraege: 2" in proc.stdout


def test_external_json_import_without_overwriting_existing_figure():
    """Kernvertrag F03 Punkt 3 (externes persoenliches JSON): nach der
    ersten ECHTEN Erschaffung importiert die Person ('i') ein externes,
    VORGEFERTIGTES v7-JSON (BESTANDSFIXTURE/EXTERN -- KEINE Erschaffung
    ueber die Fake-SL, reiner Importpfad). Die bereits erschaffene erste
    Figur bleibt byteidentisch erhalten; die importierte Figur wird als
    eigene, inaktive Zweitfigur registriert (kein automatischer
    Aktivwechsel ohne ausdrueckliches 'w')."""
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        write_test_profile(data_dir / "run")
        registry_dir = data_dir / "registry"
        leader = sup.register_human(registry_dir, "Solo-T-Import")
        pid = leader.participant_id
        table_id, section_id = f"local-{pid}", f"local-{pid}-section"

        # BESTANDSFIXTURE/EXTERN: ein vorgefertigtes, von der Fake-SL
        # UNABHAENGIGES v7-JSON (eigener char_id-Namensraum
        # 'chrono-external-...', bewusst NICHT 'chrono-synth-...'). R12
        # Savegate (B1): der echte Importpfad ('i') prueft jetzt ebenfalls
        # BEIDE v7-Schemas ("Import abgelehnt (strukturell ungueltig)") --
        # der alte Minimalblock scheiterte daran. `full_v7_save` liefert
        # denselben Fixture-Block, vollstaendig schemakonform, mit
        # identischer Identitaet (char_id/name/callsign/save_id
        # unveraendert).
        external_save = full_v7_save(
            "chrono-external-test-001", name="Externe Figur", callsign="EXT",
            save_id="external-fixture-001",
        )

        with CreationCapableSmartGmServer(table_id, section_id, complete_after=2) as srv:
            env = _env_for(srv)
            stdin_text = (
                "n\nIch packe leicht.\n"
                "i\n" + json.dumps(external_save) + "\nENDE\nj\nb\n"
                "s\nx\n"
            )
            proc = _run(data_dir, pid, stdin_text, env)
            assert proc.returncode == 0, proc.stderr[-2000:]
            assert "Erschaffung abgeschlossen: char_id=" in proc.stdout
            assert "Vorschau: char_id=chrono-external-test-001" in proc.stdout
            assert "Zweite Figur registriert (INAKTIV): char_id=chrono-external-test-001" in proc.stdout
            # Nur die Erschaffung (1 Frage + 1 Save) hat die Fake-SL real
            # befragt -- der Import ist ein eigener, von der Fake-SL
            # unabhaengiger Produktweg.
            assert len(srv.creation_calls) == 2, srv.creation_calls
            assert "Katalog-Eintraege: 2" in proc.stdout

        figure_files = _catalog_figure_files(data_dir)
        assert len(figure_files) == 2, figure_files
        # Darstellungsmigration (02_TESTVERTRAG.md): gelesene persoenliche
        # Saves, Export-Schema kennt auf Figurenebene nur `id`.
        by_char_id = {
            json.loads(f.read_text(encoding="utf-8"))["characters"][0]["id"]: f
            for f in figure_files
        }
        assert "chrono-external-test-001" in by_char_id
        imported = json.loads(by_char_id["chrono-external-test-001"].read_text(encoding="utf-8"))
        assert imported["save_id"] == "external-fixture-001"
        created_char_ids = [cid for cid in by_char_id if cid.startswith("chrono-synth-")]
        assert len(created_char_ids) == 1, "die echte Erschaffung muss unveraendert als eigene Figur bestehen bleiben"


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
