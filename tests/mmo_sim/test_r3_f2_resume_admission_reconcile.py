#!/usr/bin/env python3
"""
tests/mmo_sim/test_r3_f2_resume_admission_reconcile.py — ZR-FIGURENREISE-
TISCH-NACHZUG-20261102-R3, enger Nachzug F2 (02_NACHZUG.md §B/F2,
review/independent-r2-review.md §3 F2_TABLE_SECTION_LIFECYCLE).

Deckt GENAU den in der Review benannten normalen Kontrollflussfehler:
- `tisch-start` beginnt einen Abschnitt, bindet ihn, pausiert kontrolliert
  mitten im ersten Zug (Admission `state="started"`, `section_id` gebunden,
  Store-Tisch real noch offen).
- Ein FRISCHER Prozess (neue `TuiSession`, dieselbe Platte) setzt GENAU
  diesen Abschnitt ueber den NORMALEN 'Fortsetzen'-Menueweg fort
  (`_cmd_menu_fortsetzen` -> `_resume_bound_table`, NICHT ueber
  `tisch-start`) und schliesst ihn tatsaechlich ab.
- Ein erneuter `tisch-start` auf DIESELBE `table_key` (noch ein frischer
  Prozess) trifft danach ehrlich auf 'geschlossen' -- KEIN `__2`-
  Folgeabschnitt, KEINE neue Tischdatei, KEIN Zusatzeffekt. Das ist der
  Vor-Fix-Fehler: `_resume_bound_table` buchte den Admission-Abschluss
  bisher NIE, also blieb die Admission faelschlich `state="started"` und
  `start_table` akzeptierte den erneuten Aufruf idempotent, bevor
  `create_table_from_offer_log` die bereits geschlossene Generation
  ueberspringt und `__2` anlegt.

Zusaetzlich: ein frueher Startabbruch (fehlende Laufumgebung, VOR jeder
`create_table_from_offer_log`-Persistenz) darf keine eingefrorene
'gestartet'-Sackgasse hinterlassen -- der Tisch bleibt danach real
bedienbar (erneuter `request_join` moeglich).

Fakes nur am GM-Transportrand, Muster aus
`test_r2_f1_f2_f3_tabledienst_2026_11_02.py` -- Produktpersistenz laeuft
echt. Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402
from _section_completion_resume_fixtures import debrief_with_marker  # noqa: E402

from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core import table_admission  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.registry.participants import Participant, ParticipantRegistry  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


def _register_human_identity(onboarding_dir: Path, participant_id: str) -> None:
    """`_resume_bound_table` unterscheidet Mensch/Persona ueber die
    VORHANDENE `ParticipantRegistry` (`TuiSession._local_round_list_
    humans`), NICHT ueber `catalog`/`onboarding` -- ein am geteilten
    Geraet mitspielender Mensch muss hier eingetragen sein, sonst gilt er
    beim Fortsetzen faelschlich als ungetriebene Persona. `_save` direkt
    (statt `register_participant`, das IMMER eine neue zufaellige ID
    vergibt) -- dieselbe deterministische Teilnehmer-ID wie der Rest
    dieses Tests."""
    registry = ParticipantRegistry(onboarding_dir.parent / "registry")
    registry._save(Participant(participant_id=participant_id, kind="human", display_name=participant_id))


class _SpyFactory:
    def __init__(self, label: str):
        self.label = label

    def __call__(self, *args, **kwargs):
        raise AssertionError(f"Spy-Factory '{self.label}' wurde aufgerufen (Gate-Bruch).")


class _NeverClosingGm:
    def turn(self, turn_idx, text, **kw):
        return {"content": "SL-Antwort (nie fertig)."}


class _FakeTableGm:
    def __init__(self, debrief_text: str):
        self._debrief = debrief_text
        self.calls = 0

    def turn(self, turn_idx, text, **kw):
        self.calls += 1
        if self.calls < 3:
            return {"content": f"SL-Antwort #{self.calls} (kein Abschluss)."}
        return {"content": self._debrief}


def _pausing_after_consent_input():
    def _fn(prompt: str = "") -> str:
        if "[j/n]" in prompt:
            return "j"
        if "Wahl [a/k]" in prompt:
            return "a"
        return "/pause"
    return _fn


def _smart_input():
    counter = {"n": 0}

    def _fn(prompt: str = "") -> str:
        if "[j/n]" in prompt:
            return "j"
        if "Wahl [a/k]" in prompt:
            return "a"
        counter["n"] += 1
        return f"Zug {counter['n']}."
    return _fn


def _register_own_figure(
    onboarding_dir: Path, catalog_dir: Path, participant_id: str, char_id: str, level: int = 1,
    *, run_dir: Path, states_dir: Path,
) -> dict:
    save = full_v7_save(char_id, name=participant_id, save_id=f"fixture-{participant_id}-001", level=level)
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
    ))
    catalog.bind_for_section(catalog_dir, participant_id, char_id, has_open_section=False)
    ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, participant_id, char_id, save)
    core_store.publish_current_save(run_dir, participant_id, save, ps_store, states_dir)
    return save


def _fresh_host_session(onboarding_dir, catalog_dir, run_dir, states_dir, *, input_fn, gm_transport_factory):
    """Jede Instanz hier steht fuer einen FRISCHEN Interpreter -- kein
    gemeinsames Python-Objekt/Cache mit einer vorherigen Instanz, nur die
    gemeinsame Platte (`run_dir`/`states_dir`/`onboarding_dir`/
    `catalog_dir`), exakt wie ein echter Prozessneustart es waere."""
    return TuiSession(
        onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="host1",
        input_fn=input_fn, print_fn=lambda *_a, **_kw: None,
        run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
        gm_transport_factory=gm_transport_factory, persona_driver_factory=_SpyFactory("host_persona"),
        host_capable=True,
    )


def test_f2_resume_menu_closes_admission_and_repeated_start_hits_closed_not_duplicate():
    """Der konkrete, in der Review benannte Fall: Pause -> frischer Prozess
    setzt ueber den NORMALEN Fortsetzenweg fort und schliesst ab ->
    erneuter `tisch-start` auf dieselbe `table_key`. Vorher/Nachher-Bytes:
    GENAU EINE Tischdatei unter `run_dir/tables/` bleibt bestehen, KEINE
    zweite (`__2`) entsteht."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)
        _register_own_figure(
            onboarding_dir, catalog_dir, "host1", "CHR-HOST1", level=1,
            run_dir=run_dir, states_dir=states_dir,
        )
        _register_own_figure(
            onboarding_dir, catalog_dir, "guest1", "CHR-GUEST1", level=1,
            run_dir=run_dir, states_dir=states_dir,
        )
        _register_human_identity(onboarding_dir, "guest1")

        # Prozess 1: anbieten, annehmen, starten -- kontrolliert pausiert
        # MITTEN im ersten Zug (Admission bleibt "started", section_id
        # real gebunden, Store-Tisch bleibt offen).
        host_p1 = _fresh_host_session(
            onboarding_dir, catalog_dir, run_dir, states_dir,
            input_fn=_pausing_after_consent_input(), gm_transport_factory=lambda: _NeverClosingGm(),
        )
        guest_session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="guest1",
            run_dir=run_dir, host_capable=False,
        )
        host_p1._cmd_table_offer(["mesaR3"])
        guest_session._cmd_table_request_join(["mesaR3"])
        host_p1._cmd_table_accept(["mesaR3", "guest1"])
        try:
            host_p1._cmd_table_start(["mesaR3"])
            raise AssertionError("Tischstart haette per /pause mit EndOfInput enden muessen.")
        except EndOfInput:
            pass

        record_after_pause = table_admission.load_record(run_dir, "mesaR3")
        bound_section_id = record_after_pause.get("section_id")
        assert bound_section_id, "section_id haette trotz Pause gebunden sein muessen."
        assert record_after_pause["state"] == table_admission.STATE_STARTED, record_after_pause
        section_after_pause = core_store.Table.load(run_dir, bound_section_id)
        assert section_after_pause.status != "closed", "Testvoraussetzung: Section muss real offen sein."

        tables_dir = run_dir / "tables"
        before_table_files = sorted(p.name for p in tables_dir.glob("*.json"))
        assert before_table_files == [f"{bound_section_id}.json"], before_table_files

        # Prozess 2 (frischer Interpreter): setzt ueber den NORMALEN
        # 'Fortsetzen'-Menueweg (NICHT 'tisch-start') fort und beendet den
        # Abschnitt real (Debrief mit Marker nach 2 Leerzuegen).
        debrief_host = full_v7_save("CHR-HOST1", name="host1", save_id="fixture-host1-r3-002", level=1)
        debrief_guest = full_v7_save("CHR-GUEST1", name="guest1", save_id="fixture-guest1-r3-002", level=1)
        debrief_text = debrief_with_marker({"CHR-HOST1": debrief_host, "CHR-GUEST1": debrief_guest})
        fake_gm = _FakeTableGm(debrief_text)
        host_p2 = _fresh_host_session(
            onboarding_dir, catalog_dir, run_dir, states_dir,
            input_fn=_smart_input(), gm_transport_factory=lambda: fake_gm,
        )
        host_p2._cmd_menu_fortsetzen()

        section_after_resume = core_store.Table.load(run_dir, bound_section_id)
        assert section_after_resume.status == "closed", (
            f"Testvoraussetzung: der echte Fortsetzenweg haette den Abschnitt abschliessen muessen "
            f"(status={section_after_resume.status!r})."
        )
        record_after_resume = table_admission.load_record(run_dir, "mesaR3")
        assert record_after_resume["state"] == table_admission.STATE_CLOSED, (
            "F2: der normale Fortsetzenweg haette die Admission nachfuehren (schliessen) muessen, "
            f"state={record_after_resume['state']!r} (Vor-Fix-Fehler: blieb 'started')."
        )
        assert record_after_resume["section_id"] == bound_section_id, (
            "Die Admission-Bindung haette unveraendert dieselbe section_id behalten muessen."
        )

        # Prozess 3 (noch ein frischer Interpreter): erneuter 'tisch-start'
        # auf DIESELBE table_key -- ehrlich 'geschlossen', KEIN __2.
        host_p3 = _fresh_host_session(
            onboarding_dir, catalog_dir, run_dir, states_dir,
            input_fn=_SpyFactory("sollte nie Input brauchen -- Start wird VOR jedem Zug abgelehnt"),
            gm_transport_factory=_SpyFactory("host_gm_p3"),
        )
        printed: list[str] = []
        host_p3._print = printed.append
        host_p3._cmd_table_start(["mesaR3"])
        assert any("Tischstart abgelehnt" in p and "geschlossen" in p for p in printed), printed

        after_table_files = sorted(p.name for p in tables_dir.glob("*.json"))
        assert after_table_files == before_table_files, (
            f"Erneuter 'tisch-start' auf geschlossene table_key haette KEINE neue Tischdatei "
            f"(insbesondere kein '__2') anlegen duerfen: vorher={before_table_files} "
            f"nachher={after_table_files}"
        )
        final_record = table_admission.load_record(run_dir, "mesaR3")
        assert final_record["state"] == table_admission.STATE_CLOSED, final_record
        assert final_record["section_id"] == bound_section_id, final_record


def test_f2_started_but_never_bound_start_stays_serviceable():
    """F2 §3: ein frueher Startabbruch (fehlende Laufumgebung, VOR
    `create_table_from_offer_log`) darf keine eingefrorene 'gestartet'-
    Sackgasse hinterlassen -- der Tisch bleibt danach real bedienbar."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir = d / "run"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)

        # Host-Session OHNE states_dir/schema_path/gm_transport_factory --
        # `_cmd_local_round` scheitert HIER garantiert VOR jeder
        # `create_table_from_offer_log`-Persistenz (frueher Laufumgebungs-
        # Check), also NIE eine section_id gebunden.
        host_session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="host1",
            run_dir=run_dir, host_capable=True,
        )
        host_session._cmd_table_offer(["mesaR3b"])
        printed: list[str] = []
        host_session._print = printed.append
        host_session._cmd_table_start(["mesaR3b"])
        assert any("bleibt offen" in p for p in printed), printed

        record = table_admission.load_record(run_dir, "mesaR3b")
        assert record["state"] == table_admission.STATE_OPEN, (
            f"Ein gescheiterter Start ohne gebundenen Abschnitt haette auf 'open' "
            f"zurueckfallen muessen, state={record['state']!r} (eingefrorene Sackgasse)."
        )
        assert not record.get("section_id"), record

        # Real bedienbar: eine Anfrage ist jetzt wieder moeglich (waere bei
        # eingefrorenem 'started' ueber `_require_open` abgelehnt worden).
        guest_session = TuiSession(
            onboarding_dir=d / "guest_onboarding", catalog_dir=d / "guest_catalog",
            participant_id="guest1", run_dir=run_dir, host_capable=False,
        )
        guest_session._cmd_table_request_join(["mesaR3b"])
        record_after_request = table_admission.load_record(run_dir, "mesaR3b")
        assert record_after_request["requests"] == ["guest1"], record_after_request


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
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
