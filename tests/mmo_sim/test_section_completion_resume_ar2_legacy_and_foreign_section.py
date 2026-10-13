#!/usr/bin/env python3
"""
tests/mmo_sim/test_section_completion_resume_ar2_legacy_and_foreign_section.py
— AR2 Teil C (01_ABSCHLUSSVERTRAG.md): "drei Ergebnisse statt None als
Freibrief" fuer `_section_completion_recovery.find_recoverable_entry`.

Vor AR2 filterte `find_recoverable_entry` Kandidaten AUSSCHLIESSLICH ueber
`entry["section_id"] == section_id` -- ein Legacy-Eintrag (section_id fehlt
komplett, z.B. ein Aufrufer aus der Zeit vor R12-AUTORECOVERY) war dadurch
fuer die Suche UNSICHTBAR und der Aufrufer fiel auf einen stillschweigenden
NEUEN Spielturn zurueck, obwohl der juengste sl_log-Eintrag bereits den
Abschluss-Marker trug (kein ausstehender Beleg != ein bekannter, aber
unzureichend gebundener Beleg). AR2 behandelt den juengsten Eintrag jetzt
auch ohne jede Section-Bindung (`section_id is None`) als Kandidaten -- ein
Legacy-Marker-Treffer endet damit kontrolliert in HOLD statt in einer
automatischen, unautorisierten neuen Anfrage.

Gleichzeitig darf das NICHT zu einer Globalblockade werden: ein juengster
Eintrag mit einer EXPLIZITEN, ANDEREN (fremden) `section_id` bleibt weiterhin
komplett unberuecksichtigt -- "keine Fremd-Section rueckwaerts", der
Aufrufer bleibt fuer eine wirklich neue/andere Section normal spielbar.

Reine Unit-Tests gegen die zustandslose Funktion selbst (wie die
bestehenden AR05/AR11-Tests in test_section_completion_resume_provenance.py)
-- kein I/O, keine echte Runtime noetig.

Pure Python, nur `assert`, echter Exitcode, kein pytest."""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import mmo_sim.core._section_completion_recovery as recovery  # noqa: E402
from mmo_sim.core.completion_marker import completion_marker_matches  # noqa: E402

MARKER = "SECTION-ABSCHLUSS-BESTAETIGT"
TABLE_ID = "t-ar2-legacy"
SECTION_ID = "section-ar2-legacy-current"


def test_legacy_entry_without_section_binding_matching_marker_holds_not_normal():
    """Ein Legacy-Eintrag (section_id fehlt komplett) ist der juengste
    `sl_log`-Eintrag, traegt den Abschluss-Marker UND (hypothetisch, um
    GENAU die Section-Bindungsluecke von der bereits bestehenden AR11-
    Schnappschusspruefung zu isolieren) einen vollstaendigen Schnappschuss.
    Vor AR2 waere das 'unsichtbar' gewesen (section_id passt nicht exakt) --
    `(None, None)`, der Aufrufer haette einen NEUEN Spielturn gestartet,
    obwohl bereits eine durabel empfangene Markerantwort vorlag. AR2 liefert
    jetzt stattdessen einen expliziten HOLD-Grund (kontrollierter Stopp)."""
    legacy_entry = {
        "turn_idx": 0,
        "leader_message": "Anker (Legacy-Aufrufer, section_id nie gesetzt).",
        "origin_persona_key": "leader_pk",
        "content": f"Abschnitt beendet.\n{MARKER}",
        "section_id": None,
        "expected_prev_ref_by_member": {"leader_pk": None},
    }
    found, hold_reason = recovery.find_recoverable_entry(
        [legacy_entry], SECTION_ID, TABLE_ID, MARKER, completion_marker_matches,
    )
    assert found is None, "ein Legacy-Marker-Treffer darf NIE blind als fertig gebundener Beleg geerntet werden."
    assert hold_reason is not None, (
        "ein bekannter Marker-Treffer ohne jede Section-Bindung muss HOLD sein, nicht "
        "'kein Beleg' (das waere wieder der stillschweigende Rueckfall auf einen neuen Turn)."
    )


def test_foreign_section_on_last_entry_does_not_block_new_section_normal_path():
    """Der juengste `sl_log`-Eintrag gehoert explizit zu einer ANDEREN,
    bereits anderweitig behandelten Section ('section-other') -- die
    aktuell angefragte Section ('section-ar2-legacy-current') ist davon
    komplett unberuehrt. 'Keine Fremd-Section rueckwaerts': der normale
    Spielweg (kein Abschlussbeleg fuer DIESE Section) muss unblockiert
    bleiben, `(None, None)`."""
    foreign_entry = {
        "turn_idx": 5,
        "leader_message": "Regulaerer Turn einer anderen, bereits erledigten Section.",
        "origin_persona_key": "leader_pk",
        "content": f"Abschnitt beendet.\n{MARKER}",
        "section_id": "section-other",
        "expected_prev_ref_by_member": {"leader_pk": {"run_id": "r1", "seq": 3}},
    }
    found, hold_reason = recovery.find_recoverable_entry(
        [foreign_entry], SECTION_ID, TABLE_ID, MARKER, completion_marker_matches,
    )
    assert found is None and hold_reason is None, (
        "ein Marker-Treffer einer FREMDEN, expliziten Section darf fuer eine andere "
        f"angefragte Section weder geerntet noch global blockiert werden -- got ({found!r}, {hold_reason!r})"
    )


def test_empty_sl_log_is_plain_normal_path():
    """Regressionsschutz AR01: ein leerer `sl_log` ist unveraendert `(None,
    None)` -- der allererste Aufruf einer Section darf durch keine der
    AR2-Erweiterungen beeinflusst werden."""
    found, hold_reason = recovery.find_recoverable_entry(
        [], SECTION_ID, TABLE_ID, MARKER, completion_marker_matches,
    )
    assert found is None and hold_reason is None


def test_request_binding_error_hook_is_consulted_only_for_an_otherwise_ready_entry():
    """Die optionale `request_binding_error`-Pruefung (AR2 Teil A) wird NUR
    fuer einen Eintrag aufgerufen, der die strukturellen Vorpruefungen
    (Section-Bindung, Marker, Schnappschuss) bereits erfuellt -- ein
    struktureller Fehlgriff (hier: fehlender Schnappschuss) darf NIE bis zur
    Request-Bindungspruefung durchrutschen (die reine, I/O-freie Natur
    dieses Moduls bleibt dadurch erhalten: der Callback sieht nur echte
    Kandidaten)."""
    calls = []

    def _never_should_be_called(entry):
        calls.append(entry)
        return "sollte nie aufgerufen werden"

    entry_without_snapshot = {
        "turn_idx": 0,
        "origin_persona_key": "leader_pk",
        "content": f"Abschnitt beendet.\n{MARKER}",
        "section_id": SECTION_ID,
        "expected_prev_ref_by_member": None,
    }
    found, hold_reason = recovery.find_recoverable_entry(
        [entry_without_snapshot], SECTION_ID, TABLE_ID, MARKER, completion_marker_matches,
        request_binding_error=_never_should_be_called,
    )
    assert found is None and hold_reason is not None
    assert calls == [], "request_binding_error darf fuer einen bereits strukturell abgelehnten Eintrag nie aufgerufen werden."

    entry_ready = dict(entry_without_snapshot, expected_prev_ref_by_member={"leader_pk": None})
    found2, hold_reason2 = recovery.find_recoverable_entry(
        [entry_ready], SECTION_ID, TABLE_ID, MARKER, completion_marker_matches,
        request_binding_error=lambda entry: "HOLD ueber Request-Bindung",
    )
    assert found2 is None and hold_reason2 == "HOLD ueber Request-Bindung"


def main() -> int:
    tests = [
        test_legacy_entry_without_section_binding_matching_marker_holds_not_normal,
        test_foreign_section_on_last_entry_does_not_block_new_section_normal_path,
        test_empty_sl_log_is_plain_normal_path,
        test_request_binding_error_hook_is_consulted_only_for_an_otherwise_ready_entry,
    ]
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
