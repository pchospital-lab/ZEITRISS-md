#!/usr/bin/env python3
"""
tests/mmo_sim/test_r5_fix3b_guest_creation_request_without_raw_operator_id_2026_11_07.py
-- ZR-VOLLENDUNG-OHNE-LAN-NACHZUG-20261107-R5 (Arbeitsblock 2 Punkt 1, F3/
UX-R4-04: "Der dokumentierte erste Gast-Erschaffungsweg verlangt weiterhin
eine nicht angebotene Betreiberkennung").

Vorher stammte die Betreiberliste in `_cmd_gast_erschaffung_anfragen_menu`
AUSSCHLIESSLICH aus offenen Tischen (`table_admission.list_open_tables`).
Vor dem ersten Tischangebot eines Betreibers war diese Liste deshalb LEER
-- die Meldung bot die rohe Betreiber-ID beilaeufig als gleichwertige
Option an, obwohl in Wahrheit eine fehlende Voraussetzung vorlag. Dieser
Test belegt am echten `TuiSession`-Code (KEIN neues Discoveryprotokoll,
dieselbe bestehende `list_open_tables`-Lesequelle):

1. VOR jedem Tischangebot zeigt die leere-Liste-Meldung die zutreffende
   Voraussetzung (Betreiber muss zuerst einen Tisch anbieten) + den
   erreichbaren naechsten Schritt -- NICHT die rohe ID als gleichwertigen
   Normalweg.
2. NACHDEM der Betreiber einmal '[tisch] -> [5]' (`_cmd_table_offer`,
   figurfrei moeglich) ausgefuehrt hat, erscheint er in der Liste
   NUMMERIERT -- der Gast waehlt per Nummer, OHNE jemals eine rohe
   Betreiber-ID einzugeben.
3. Diese nummerierte Auswahl fuehrt zu einer echten Anfrage
   (`creation_grants.request_creation`) UND einer echten Freigabe durch
   den Betreiber (`_cmd_gast_erschaffung_entscheiden_menu` ->
   `_cmd_gast_erschaffung_annehmen`), ebenfalls beide nummeriert -- der
   dokumentierte Normalweg erreicht Anfrage+Freigabe ohne rohe ID.

Pure Python, nur `assert`, echter Exitcode, synthetischer Temp-Dir
(gemeinsamer `run_dir` fuer Host+Gast, wie bei der echten lokalen Runde),
0 echte GM-/Modellcalls (Anfrage/Freigabe sind reine Dateischreibvorgaenge,
kein GM-Request)."""
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

from mmo_sim.ui.tui import TuiSession  # noqa: E402


def _scripted_input(values):
    q = list(values)

    def _fn(prompt: str = "") -> str:
        if q:
            return q.pop(0)
        raise EOFError()

    return _fn


def test_empty_operator_list_explains_precondition_not_raw_id_as_normal_path():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        printed: list[str] = []
        guest = TuiSession(
            onboarding_dir=root / "guest_ob", catalog_dir=root / "guest_cat",
            participant_id="gast_fix3b_empty", run_dir=run_dir,
            print_fn=printed.append, host_capable=False,
        )
        guest._input = _scripted_input([""])  # leer = abbrechen, keine rohe ID eintippen.
        guest._cmd_gast_erschaffung_anfragen_menu()
        out = "\n".join(printed)
        assert "anbieten" in out, (
            "Die leere-Liste-Meldung muss die zutreffende Voraussetzung (Betreiber bietet "
            "zuerst einen Tisch an) nennen.", out,
        )
        assert "naechste" in out.lower() or "danach" in out.lower() or "nachdem" in out.lower() or \
            "erneut" in out.lower(), (
            "Die Meldung muss einen erreichbaren naechsten Schritt nennen.", out,
        )


def test_guest_requests_and_operator_grants_via_numbered_choice_without_raw_id():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        host_printed: list[str] = []
        guest_printed: list[str] = []
        host_id = "betreiber_fix3b"
        guest_id = "gast_fix3b"

        host = TuiSession(
            onboarding_dir=root / "host_ob", catalog_dir=root / "host_cat",
            participant_id=host_id, run_dir=run_dir, print_fn=host_printed.append, host_capable=True,
        )
        guest = TuiSession(
            onboarding_dir=root / "guest_ob", catalog_dir=root / "guest_cat",
            participant_id=guest_id, run_dir=run_dir, print_fn=guest_printed.append, host_capable=False,
        )

        # Betreiber bietet EINMAL einen (figurfreien) Tisch an -- derselbe
        # bestehende '[tisch] -> [5]'-Weg, kein neuer Discoverymechanismus.
        host._cmd_table_offer(["tbl-fix3b"])

        # Gast: '[charaktere] -> [4]' -- waehlt den Betreiber NUR per Nummer.
        guest._input = _scripted_input(["1"])
        guest._cmd_gast_erschaffung_anfragen_menu()
        guest_out = "\n".join(guest_printed)
        assert f"[1] {host_id}" in guest_out, (
            "Der Betreiber muss NACH seinem Tischangebot nummeriert in der Liste erscheinen.",
            guest_out,
        )
        assert f"Erschaffungsanfrage an Betreiber '{host_id}' gestellt" in guest_out, guest_out

        # Betreiber: '[charaktere] -> [4]' entscheiden -- Gast UND Entscheidung
        # ebenfalls beide per Nummer, keine rohe guest_id/Entscheidungssyntax.
        host._input = _scripted_input(["1", "1"])
        host._cmd_gast_erschaffung_entscheiden_menu()
        host_out = "\n".join(host_printed)
        assert f"[1] {guest_id}" in host_out, host_out
        assert f"Gast '{guest_id}' freigegeben" in host_out, (
            "Die nummerierte Anfrage+Entscheidung muss zu einer echten Freigabe fuehren.", host_out,
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
