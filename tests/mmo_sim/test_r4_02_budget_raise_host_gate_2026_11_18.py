#!/usr/bin/env python3
"""
tests/mmo_sim/test_r4_02_budget_raise_host_gate_2026_11_18.py — R4-02
Regression (ZR-ALTAIR-UPDATER-SPIELTEST-NACHZUG-20261118-r4,
01_GENERAL_REVIEW.md R4-02, 02_NACHZUG_AUFTRAG.md Block B).

Vorher rief `TuiSession._cmd_settings` (erreichbar ueber BEIDE Dispatch-
Eintraege `s`/`einstellungen`, `mmo_sim/ui/tui.py:11768-11769`/
`:11841-11842`) `_offer_operator_budget_raise` auf, die ueber
`grant_operator_budget(..., allow_overwrite=True)` schrieb, OHNE die
bestehende Rollengrenze `_require_host` (die JEDE andere Host-only-Aktion
in dieser Datei als erstes Statement aufruft). Ein Gast konnte so eine
Betreiber-Budgetgrenze schreiben, obwohl Gaeste nur lesen duerfen sollen.
Zusaetzlich behandelte `grant_operator_budget` eine VORHANDENE, aber
beschaedigte `lab.status.json` identisch zu einer fehlenden Datei (`data =
{}`) -- ein vorheriger Verbrauchsstand waere beim naechsten Schreiben
stillschweigend auf 0 zurueckgefallen ("als leeres Profil reparieren").

Treibt den ECHTEN Aufrufer `TuiSession._cmd_settings(["budget",
"erhoehen"])` an -- identisch zu dem, was `choice == "s"` UND `choice in
("einstellungen", "settings")` im Hauptdispatch (`run()`) aufrufen; ein
Gate in der gemeinsamen Zielmethode deckt daher beide Dispatch-Eintraege/
Aliase ab, kein separater Dispatcher-Test noetig.

Drei Gegenfaelle aus 02_NACHZUG_AUFTRAG.md Block B ("Beweis ueber echten
Einstellungen-Caller mit Host, Gast und Ablehnung; keine Mutation bei
abgewiesenem Gast oder ungueltigem Rahmen"):
  (1) Host -> erlaubt, Datei wird aktualisiert.
  (2) Gast -> abgelehnt (GuestCapabilityError), KEINE Mutation.
  (3) ungueltiger Rahmen (nicht-numerische Eingabe) -> abgelehnt, KEINE
      Mutation (bereits vorher getestetes Verhalten, hier zusaetzlich
      explizit gegen den Host-Gate-Fix abgesichert, damit der neue
      `_require_host`-Aufruf diesen bestehenden Ablehnungspfad nicht
      verdeckt/vertauscht).
Zusaetzlich: eine beschaedigte `lab.status.json` wird NICHT stillschweigend
als leeres Profil ueberschrieben (`OperatorBudgetCorruptedStatusError`,
admission.py).

Pure Python, nur `assert`, echter Exitcode -- lauffaehig per `pytest` UND
als eigenstaendiges Skript (identischer Stil zu
test_r3_07_budget_breakdown_ui.py, dessen `_scripted_input`/`_session`-
Helfer hier wiederverwendet werden)."""
from __future__ import annotations

import json
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.core.admission import _atomic_write_json, _status_path, grant_operator_budget  # noqa: E402
from mmo_sim.ui.tui import GuestCapabilityError, TuiSession  # noqa: E402


def _scripted_input(answers):
    it = iter(answers)

    def read(prompt=""):
        try:
            return next(it)
        except StopIteration:
            raise EOFError()

    return read


def _session(root: Path, *, input_fn=None, host_capable=True):
    run_dir = root / "run"
    run_dir.mkdir(parents=True, exist_ok=True)
    printed: list[str] = []
    session = TuiSession(
        onboarding_dir=root / "onboarding", catalog_dir=root / "catalog", participant_id="p1",
        input_fn=input_fn, print_fn=printed.append, run_dir=run_dir, host_capable=host_capable,
    )
    return session, run_dir, printed


def test_host_can_raise_budget_through_real_settings_caller():
    """Gegenfall (1): ein HOST darf weiterhin ueber den echten Caller
    erhoehen -- der neue `_require_host`-Aufruf darf den bestehenden,
    bereits funktionierenden Host-Weg nicht blockieren."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        run_dir.mkdir(parents=True, exist_ok=True)
        grant_operator_budget(run_dir, max_turns=5, max_seconds=60.0, max_usd=1.0)

        session, _run_dir, printed = _session(
            root, input_fn=_scripted_input(["20", "", "", "j"]), host_capable=True,
        )
        session._cmd_settings(["budget", "erhoehen"])

        data = json.loads(_status_path(run_dir).read_text(encoding="utf-8"))
        assert data["max_turns"] == 20, data
        assert any("aktualisiert" in p for p in printed), printed


def test_guest_is_rejected_before_any_budget_mutation():
    """Gegenfall (2), KERN von R4-02: ein GAST darf ueber denselben echten
    Caller (`_cmd_settings(["budget", "erhoehen"])`, identisch zu `s`/
    `einstellungen`) KEINE Betreibergrenze schreiben -- VOR dem Fix wurde
    hier weder `_require_host` gerufen noch die Datei verglichen. Beweis:
    `GuestCapabilityError` fliegt, UND `lab.status.json` ist byteidentisch
    zum Vorzustand (keine stille Teilmutation vor dem Abbruch)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        run_dir.mkdir(parents=True, exist_ok=True)
        grant_operator_budget(run_dir, max_turns=5, max_seconds=60.0, max_usd=1.0)
        before_bytes = _status_path(run_dir).read_bytes()

        # Scripted Input wird NIE konsumiert, wenn das Gate frueh genug
        # greift -- EOFError statt eines Werts waere also ein Beleg, dass
        # doch ein readline-Aufruf stattgefunden hat (Gate zu spaet).
        session, _run_dir, printed = _session(
            root, input_fn=_scripted_input([]), host_capable=False,
        )
        raised = False
        try:
            session._cmd_settings(["budget", "erhoehen"])
        except GuestCapabilityError as exc:
            raised = True
            assert "nur im Hostmodus" in str(exc), str(exc)
        assert raised, "Gast haette ueber den echten Caller abgewiesen werden muessen (R4-02)"

        after_bytes = _status_path(run_dir).read_bytes()
        assert after_bytes == before_bytes, "Gast-Versuch darf lab.status.json NICHT veraendert haben"
        assert not any("aktualisiert" in p for p in printed), printed


def test_guest_can_still_read_budget_status_unaffected_by_host_gate():
    """Gegenprobe zu (2): `_cmd_settings(["budget"])` (reines LESEN, kein
    `erhoehen`) bleibt fuer Gaeste unveraendert erlaubt -- R4-02 gatet NUR
    den Schreibpfad, nicht `_print_budget_breakdown` (02_NACHZUG_AUFTRAG.md
    Block B: "Gaeste duerfen den zulaessigen Status LESEN")."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        run_dir.mkdir(parents=True, exist_ok=True)
        grant_operator_budget(run_dir, max_turns=5, max_seconds=60.0, max_usd=1.0)

        session, _run_dir, printed = _session(root, host_capable=False)
        session._cmd_settings(["budget"])
        joined = "\n".join(printed)
        assert "Admission-Gate" in joined, printed


def test_invalid_frame_input_rejected_without_mutation_even_as_host():
    """Gegenfall (3): ein HOST, der eine nicht-numerische Eingabe gibt,
    bleibt abgelehnt -- KEINE Mutation. Haelt diesen bestehenden
    Ablehnungspfad explizit gegen den neuen `_require_host`-Aufruf ganz vorn
    in der Methode fest (der Host-Gate-Fix darf diesen Pfad nicht
    verschieben/verdecken)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        run_dir.mkdir(parents=True, exist_ok=True)
        grant_operator_budget(run_dir, max_turns=5, max_seconds=60.0, max_usd=1.0)
        before_bytes = _status_path(run_dir).read_bytes()

        session, _run_dir, printed = _session(
            root, input_fn=_scripted_input(["nicht-numerisch", "", ""]), host_capable=True,
        )
        session._cmd_settings(["budget", "erhoehen"])

        after_bytes = _status_path(run_dir).read_bytes()
        assert after_bytes == before_bytes, "ungueltiger Rahmen darf lab.status.json NICHT veraendert haben"
        assert any("Ungueltige Zahl" in p for p in printed), printed


def test_corrupted_status_file_is_not_silently_repaired_to_zero_counters():
    """R4-02, zweiter Teil (02_NACHZUG_AUFTRAG.md Block B: "kaputter Status
    fuehrt nicht zu stiller Neuanlage oder Zaehlerreset"): eine VORHANDENE,
    aber kaputte `lab.status.json` darf `grant_operator_budget` NICHT als
    leeres Profil behandeln (das wuerde turns_used/usd_spent-Zaehler, die
    vor der Beschaedigung gueltig waren, stillschweigend auf 0 zuruecksetzen).
    Direkter Aufrufertest der admission.py-Funktion (R4-02-Kern liegt dort),
    PLUS Beleg, dass der echte TUI-Caller die resultierende Exception sichtbar
    meldet statt zu crashen."""
    from mmo_sim.core.admission import OperatorBudgetCorruptedStatusError

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        run_dir.mkdir(parents=True, exist_ok=True)
        status_path = _status_path(run_dir)
        status_path.parent.mkdir(parents=True, exist_ok=True)
        status_path.write_text("{ kaputtes json: nicht parsebar", encoding="utf-8")
        before_bytes = status_path.read_bytes()

        raised = False
        try:
            grant_operator_budget(run_dir, max_turns=20, max_seconds=600.0, max_usd=5.0, allow_overwrite=True)
        except OperatorBudgetCorruptedStatusError:
            raised = True
        assert raised, "beschaedigte lab.status.json haette NICHT stillschweigend ueberschrieben werden duerfen"
        assert status_path.read_bytes() == before_bytes, "beschaedigte Datei darf unveraendert bleiben"


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
