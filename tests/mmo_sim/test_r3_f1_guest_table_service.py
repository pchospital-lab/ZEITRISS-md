#!/usr/bin/env python3
"""
tests/mmo_sim/test_r3_f1_guest_table_service.py — ZR-FIGURENREISE-TISCH-
NACHZUG-20261102-R3, enger Nachzug F1 (02_NACHZUG.md §A,
review/independent-r2-review.md §3 F1_GUEST_HOST_SERVICE).

Deckt GENAU den in der Review benannten Rest: der begrenzte lokale
Gastdienst muss WIRKLICH bis Annahme, Spieleingabe und persoenlicher
Save-Rueckgabe reichen -- nicht nur Suche/Anfrage/Status/Ruecknahme (das
deckt bereits `test_r2_f1_f2_f3_tabledienst_2026_11_02.py`, hier nicht
dupliziert):

- `_cmd_table_request_join` bindet jetzt die TATSAECHLICH gewaehlte eigene
  Figur/Fassung des Gasts (aus seiner PRIVATEN Wurzel) an die Anfrage --
  kein stilles Importieren des aktiven Hostsaves.
- `_cmd_table_accept` uebernimmt diese Figur/Fassung ERST nach
  ausdruecklicher Hostannahme, HOSTSEITIG unter den eigenen Host-Wurzeln.
- Waehrend des tatsaechlichen Tischspiels (`_cmd_table_start`) erreichen
  echte Gastentscheidungen denselben Hostspielkern UEBER EINEN EIGENEN,
  ehrlich gekennzeichneten In-Process-Teilnehmeranschluss
  (`register_guest_terminal`) -- beobachtbar ALS Gast-Client-Eingabe
  (eigene `input_fn`/`print_fn` des Gasts werden aufgerufen, NIE die des
  Hosts), KEIN Host-Fake, der alle Menschen ersetzt.
- Nach echtem Abschluss liest der Gast seinen eigenen aktuellen Save
  ueber seine EIGENE Session zurueck.
- Der Gast macht dabei NULL eigene Provider-/Modellaufrufe (keine
  `gm_transport_factory`/`persona_driver_factory` auf seiner eigenen
  Session konfiguriert -- strukturell unerreichbar, nicht nur ungenutzt).

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
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


def _register_private_figure(
    onboarding_dir: Path, catalog_dir: Path, participant_id: str, char_id: str, level: int = 1,
) -> dict:
    """Guest-seitig: NUR die eigene private Wurzel (keine `run_dir`/
    `states_dir`-Veroeffentlichung -- `_resolve_member` faellt dann
    folgerichtig auf `onboarding.peek(...).final_save` zurueck, die
    ECHTE Autoritaet fuer eine eigene, noch nicht beim Host bekannte
    Figur)."""
    save = full_v7_save(char_id, name=participant_id, save_id=f"fixture-{participant_id}-001", level=level)
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
    ))
    return save


def _register_host_figure(
    onboarding_dir: Path, catalog_dir: Path, run_dir: Path, states_dir: Path,
    participant_id: str, char_id: str, level: int = 1,
) -> dict:
    save = full_v7_save(char_id, name=participant_id, save_id=f"fixture-{participant_id}-001", level=level)
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
    ))
    ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, participant_id, char_id, save)
    core_store.publish_current_save(run_dir, participant_id, save, ps_store, states_dir)
    return save


class _SpyFactory:
    def __init__(self, label: str):
        self.label = label

    def __call__(self, *args, **kwargs):
        raise AssertionError(f"Spy-Factory '{self.label}' wurde aufgerufen (Gate-Bruch).")


class _FakeTableGm:
    def __init__(self, debrief_text: str):
        self._debrief = debrief_text
        self.calls = 0

    def turn(self, turn_idx, text, **kw):
        self.calls += 1
        if self.calls < 3:
            return {"content": f"SL-Antwort #{self.calls} (kein Abschluss)."}
        return {"content": self._debrief}


def _counting_input(label, j_n_answer="j"):
    calls = {"n": 0}

    def _fn(prompt: str = "") -> str:
        if "[j/n]" in prompt:
            return j_n_answer
        calls["n"] += 1
        return f"{label}-Zug {calls['n']}."
    return _fn, calls


def test_f1_request_join_binds_own_private_figure_not_host_active_save():
    """Die Anfrage bindet die TATSAECHLICH eigene Figur des Gasts (aus
    seiner privaten Wurzel) -- kein stilles Importieren des aktiven
    Hostsaves. Host und Gast haben BEWUSST unterschiedliche Figuren."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        host_onboarding, host_catalog = d / "host_onboarding", d / "host_catalog"
        guest_onboarding, guest_catalog = d / "guest_onboarding", d / "guest_catalog"
        write_test_profile(run_dir, max_turns=200)
        _register_host_figure(host_onboarding, host_catalog, run_dir, states_dir, "host1", "CHR-HOST1")
        _register_private_figure(guest_onboarding, guest_catalog, "guest1", "CHR-GUEST1")

        host_session = TuiSession(
            onboarding_dir=host_onboarding, catalog_dir=host_catalog, participant_id="host1",
            run_dir=run_dir, states_dir=states_dir, host_capable=True,
        )
        guest_session = TuiSession(
            onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id="guest1",
            run_dir=run_dir, host_capable=False,
        )
        host_session._cmd_table_offer(["mesaF1"])
        printed: list[str] = []
        guest_session._print = printed.append
        guest_session._cmd_table_request_join(["mesaF1"])
        assert any("CHR-GUEST1" in p and "kein Hostsave-Import" in p for p in printed), printed

        offer = table_admission.load_record(run_dir, "mesaF1")
        assert offer["requests"] == ["guest1"], offer

        from mmo_sim.ui.tui import _read_table_guest_offer
        sidecar = _read_table_guest_offer(run_dir, "mesaF1", "guest1")
        assert sidecar is not None, "Sidecar-Angebot haette geschrieben werden muessen."
        assert sidecar["chrononaut_id"] == "CHR-GUEST1", (
            f"Gebundene Figur haette die EIGENE Gastfigur sein muessen, nicht die des Hosts: {sidecar}"
        )
        # Guest-private Wurzel bleibt unberuehrt vom Host, Host-Wurzel
        # bleibt unberuehrt vom Gast (noch vor der Annahme).
        assert not (host_catalog / "catalog__guest1.json").exists()


def test_f1_accept_publishes_own_figure_hostside_after_explicit_acceptance():
    """Erst NACH ausdruecklicher Hostannahme uebernimmt der Host die
    Gastfigur -- hostseitig, unter seinen EIGENEN Wurzeln."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        host_onboarding, host_catalog = d / "host_onboarding", d / "host_catalog"
        guest_onboarding, guest_catalog = d / "guest_onboarding", d / "guest_catalog"
        write_test_profile(run_dir, max_turns=200)
        _register_host_figure(host_onboarding, host_catalog, run_dir, states_dir, "host1", "CHR-HOST1")
        _register_private_figure(guest_onboarding, guest_catalog, "guest1", "CHR-GUEST1")

        host_session = TuiSession(
            onboarding_dir=host_onboarding, catalog_dir=host_catalog, participant_id="host1",
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH, host_capable=True,
        )
        guest_session = TuiSession(
            onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id="guest1",
            run_dir=run_dir, host_capable=False,
        )
        host_session._cmd_table_offer(["mesaF1b"])
        guest_session._cmd_table_request_join(["mesaF1b"])

        # Vor Annahme: Host-Wurzel kennt 'guest1' noch nicht.
        assert not (host_catalog / "catalog__guest1.json").exists()

        host_session._cmd_table_accept(["mesaF1b", "guest1"])

        # Nach Annahme: Host hat die Gastfigur UNTER SEINEN EIGENEN
        # Wurzeln uebernommen (hostseitiger Write nach Annahme).
        ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
        published = core_store.load_current_save_or_raise(run_dir, "guest1", ps_store, states_dir=states_dir)
        from mmo_sim.domain.zeitriss import saves as zeitriss_saves
        assert zeitriss_saves.block_char_id(published) == "CHR-GUEST1", published

        from mmo_sim.ui.tui import _read_table_guest_offer
        assert _read_table_guest_offer(run_dir, "mesaF1b", "guest1") is None, (
            "Sidecar haette nach erfolgreicher Uebernahme geloescht werden muessen."
        )


def test_f1_guest_client_input_drives_hostcore_and_personal_save_returns():
    """Enger Nachweis (02_NACHZUG.md §A): Gast mit eigenem Bestand, Host
    mit anderem Bestand, Anfrage mit Fassung, echte Hostannahme,
    beobachtbarer Gastbeitrag AM EIGENEN Terminal (nicht Host-Fake),
    geschlossener Abschnitt, persoenlicher aktueller Save beim Gast."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        host_onboarding, host_catalog = d / "host_onboarding", d / "host_catalog"
        guest_onboarding, guest_catalog = d / "guest_onboarding", d / "guest_catalog"
        write_test_profile(run_dir, max_turns=200)
        _register_host_figure(host_onboarding, host_catalog, run_dir, states_dir, "host1", "CHR-HOST1")
        _register_private_figure(guest_onboarding, guest_catalog, "guest1", "CHR-GUEST1")

        host_input, host_calls = _counting_input("host")
        guest_input, guest_calls = _counting_input("guest")
        host_printed: list[str] = []
        guest_printed: list[str] = []

        debrief_host = full_v7_save("CHR-HOST1", name="host1", save_id="fixture-host1-f1-002", level=1)
        debrief_guest = full_v7_save("CHR-GUEST1", name="guest1", save_id="fixture-guest1-f1-002", level=1)
        debrief_text = debrief_with_marker({"CHR-HOST1": debrief_host, "CHR-GUEST1": debrief_guest})
        fake_gm = _FakeTableGm(debrief_text)

        host_session = TuiSession(
            onboarding_dir=host_onboarding, catalog_dir=host_catalog, participant_id="host1",
            input_fn=host_input, print_fn=host_printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: fake_gm, persona_driver_factory=_SpyFactory("host_persona"),
            host_capable=True,
        )
        # Der Gast macht STRUKTURELL null eigene Provider-/Modellaufrufe
        # -- weder `gm_transport_factory` noch `persona_driver_factory`
        # sind auf seiner eigenen Session ueberhaupt konfiguriert.
        guest_session = TuiSession(
            onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id="guest1",
            input_fn=guest_input, print_fn=guest_printed.append,
            run_dir=run_dir, host_capable=False,
        )

        host_session._cmd_table_offer(["mesaF1c"])
        guest_session._cmd_table_request_join(["mesaF1c"])
        host_session._cmd_table_accept(["mesaF1c", "guest1"])

        # Der schmale, ehrlich gekennzeichnete In-Process-Anschluss: der
        # Host registriert, dass GENAU dieser Gast ueber seine EIGENE
        # Session bedient wird (kein Host-Fake fuer alle Menschen).
        host_session.register_guest_terminal("guest1", guest_session)

        host_session._cmd_table_start(["mesaF1c"])

        # Beobachtbar ALS Gast-Client-Eingabe: der Gast hat tatsaechlich
        # selbst getippt (eigener Input-Call-Zaehler > 0) UND die
        # SL-Antworten auf SEINEM EIGENEN Bildschirm gesehen -- nicht auf
        # dem des Hosts.
        assert guest_calls["n"] > 0, "Der Gast haette selbst tatsaechlich eingeben muessen."
        assert any(p.startswith("[SL]") for p in guest_printed), (
            f"Der Gast haette SL-Antworten auf seinem EIGENEN Terminal sehen muessen: {guest_printed}"
        )
        # Der Host-Bildschirm hat KEINE Eingabeaufforderung/Antwort fuer
        # den Gast gezeigt, die eigentlich am Gastterminal lief (kein
        # Host-Fake, der den Gast einfach mitbedient).
        assert not any("guest1" in p and "Deine Aktion" in p for p in host_printed)

        record = table_admission.load_record(run_dir, "mesaF1c")
        section = core_store.Table.load(run_dir, record["section_id"])
        assert section.status == "closed", f"Abschnitt haette abgeschlossen sein sollen: {section.status}"
        assert record["state"] == table_admission.STATE_CLOSED, record

        # Persoenlicher aktueller Save beim Gast: der Gast liest ihn
        # ueber SEINE EIGENE Session zurueck (dieselbe Autoritaet wie
        # jeder echte Spielstart).
        resolved = guest_session._resolve_member("guest1")
        assert resolved is not None, "Gast haette seinen eigenen aktuellen Save zurueckbekommen muessen."
        _save_back, chrono_back = resolved
        assert chrono_back == "CHR-GUEST1", resolved


def test_f1_f5_accept_and_personal_writeback_survive_fresh_process_reader():
    """INTEGRIERTE Probe (R4-Nachzug Briefing A, Generalbefund F1/F5):
    separater privater Gastbestand -> sichtbare Suche/Anfrage mit
    konkreter Fassung -> Hostannahme UEBER DIE GETEILTE Regel
    (`_apply_participant_save_intake`, dieselbe Entscheidungskette wie
    `_cmd_import` -- NICHT mehr der rohe `complete_with_save`-Pfad) ->
    beobachteter echter Gastbeitrag am EIGENEN Terminal -> wirklicher
    Abschluss -> persoenlicher Rueckkanal (`_writeback_registered_guest_
    saves`, symmetrisch zu `register_guest_terminal`) -> PROZESSENDE
    SIMULIERT: eine BRANDNEUE `TuiSession` mit rein dateibasiertem Zugriff
    auf den privaten Gastroot (kein `run_dir`, KEINE Objektreferenz auf
    die alte `guest_session`) findet die ABSCHLUSSfassung
    (`fixture-guest1-f1-002`), NICHT mehr die Startfassung
    (`fixture-guest1-001`). Assert auf Save-ID/Feld-/Byte-Unterschied,
    nicht nur char_id (genau der in 02_NACHZUG.md §A/F1 benannte Rest) --
    UND Gast-Provideraufrufe == 0."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        host_onboarding, host_catalog = d / "host_onboarding", d / "host_catalog"
        guest_onboarding, guest_catalog = d / "guest_onboarding", d / "guest_catalog"
        write_test_profile(run_dir, max_turns=200)
        _register_host_figure(host_onboarding, host_catalog, run_dir, states_dir, "host1", "CHR-HOST1")
        start_save = _register_private_figure(guest_onboarding, guest_catalog, "guest1", "CHR-GUEST1")
        assert start_save["save_id"] == "fixture-guest1-001", start_save["save_id"]

        host_input, host_calls = _counting_input("host")
        guest_input, guest_calls = _counting_input("guest")
        host_printed: list[str] = []
        guest_printed: list[str] = []

        debrief_host = full_v7_save("CHR-HOST1", name="host1", save_id="fixture-host1-f1wb-002", level=1)
        # Abschlussfassung: Save-ID UND massgebliche Fortschrittsfelder
        # (lvl/wallet) weichen bewusst von der Startfassung ab.
        debrief_guest = full_v7_save(
            "CHR-GUEST1", name="guest1", save_id="fixture-guest1-f1-002", level=3, wallet=250.0,
        )
        debrief_text = debrief_with_marker({"CHR-HOST1": debrief_host, "CHR-GUEST1": debrief_guest})
        fake_gm = _FakeTableGm(debrief_text)

        host_session = TuiSession(
            onboarding_dir=host_onboarding, catalog_dir=host_catalog, participant_id="host1",
            input_fn=host_input, print_fn=host_printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: fake_gm, persona_driver_factory=_SpyFactory("host_persona"),
            host_capable=True,
        )
        # Der Gast macht STRUKTURELL null eigene Provider-/Modellaufrufe.
        guest_session = TuiSession(
            onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id="guest1",
            input_fn=guest_input, print_fn=guest_printed.append,
            run_dir=run_dir, host_capable=False,
        )

        host_session._cmd_table_offer(["mesaF1wb"])
        guest_session._cmd_table_request_join(["mesaF1wb"])
        host_session._cmd_table_accept(["mesaF1wb", "guest1"])
        host_session.register_guest_terminal("guest1", guest_session)
        host_session._cmd_table_start(["mesaF1wb"])

        assert guest_calls["n"] > 0, "Der Gast haette selbst tatsaechlich eingeben muessen."
        record = table_admission.load_record(run_dir, "mesaF1wb")
        section = core_store.Table.load(run_dir, record["section_id"])
        assert section.status == "closed", f"Abschnitt haette abgeschlossen sein sollen: {section.status}"

        # PROZESSENDE SIMULIEREN: brandneue Session, rein dateibasiert,
        # OHNE run_dir (keine geteilte Wurzel, kein Objekt der alten
        # `guest_session`) -- genau die private Gastwurzel.
        fresh_guest_printed: list[str] = []
        fresh_guest_reader = TuiSession(
            onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id="guest1",
            print_fn=fresh_guest_printed.append,
            host_capable=False,
        )
        resolved = fresh_guest_reader._resolve_member("guest1")
        assert resolved is not None, "Frischer Gastleser haette seine Figur finden muessen."
        found_save, found_char_id = resolved
        assert found_char_id == "CHR-GUEST1", resolved
        assert found_save.get("save_id") == "fixture-guest1-f1-002", (
            f"Frischer Gastleser haette die ABSCHLUSSfassung finden muessen, nicht die "
            f"Startfassung: {found_save.get('save_id')!r}"
        )
        assert found_save.get("save_id") != start_save["save_id"], (
            "Save-ID haette sich von der Startfassung unterscheiden muessen."
        )
        assert found_save != start_save, (
            "Der zurueckgegebene Save muss sich tatsaechlich in den Bytes unterscheiden, "
            "nicht nur in der char_id."
        )
        found_char0 = found_save["characters"][0]
        start_char0 = start_save["characters"][0]
        assert found_char0.get("lvl") != start_char0.get("lvl") or found_char0.get("wallet") != start_char0.get("wallet"), (
            "Massgebliche Fortschrittsfelder (lvl/wallet) haetten sich von der Startfassung "
            "unterscheiden muessen."
        )

        # Katalog/Onboarding des Gasts (eigener privater Bestand)
        # spiegeln ebenfalls die Abschlussfassung -- nicht nur der
        # Current-Resolve-Pfad.
        guest_onboarding_state = onboarding.peek(guest_onboarding, "guest1")
        assert guest_onboarding_state is not None and guest_onboarding_state.final_save is not None
        assert guest_onboarding_state.final_save.get("save_id") == "fixture-guest1-f1-002"
        figure_save = catalog.load_figure_save(guest_catalog, "guest1", "CHR-GUEST1")
        assert figure_save is not None and figure_save.get("save_id") == "fixture-guest1-f1-002"


def test_f1_f5_accept_parks_on_foreign_char_id_assignment_zero_writes():
    """Gegenprobe (a) (R4-Nachzug Briefing A Punkt 1 + Generalnachschaerfung
    "keine wirksame halbe Aufnahme"): dieselbe char_id ist bereits einem
    ANDEREN Teilnehmer im Hostkatalog zugeordnet (R2-Nachzug
    F5-Fremdzuordnungscheck, `catalog.find_registration`) -- die Annahme
    bleibt an der NEUEN Schreibstelle (`_cmd_table_accept`) GEPARKT, 0
    Writes am massgeblichen Figurenstand. Die geparkte Figurenuebernahme
    laesst die Roster-Buchung (`table_admission.accept_request`) JETZT
    BEWUSST UNWIRKSAM -- der Gast bleibt NICHT im Roster, seine Anfrage
    bleibt ehrlich OFFEN/pending (keine angenommene halbe Besetzung ohne
    uebernommene Figur)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        host_onboarding, host_catalog = d / "host_onboarding", d / "host_catalog"
        guest_onboarding, guest_catalog = d / "guest_onboarding", d / "guest_catalog"
        write_test_profile(run_dir, max_turns=200)
        _register_host_figure(host_onboarding, host_catalog, run_dir, states_dir, "host1", "CHR-HOST1")
        # Ein ANDERER Teilnehmer ("other1") hat CHR-SHARED bereits im
        # Hostkatalog registriert (z.B. ein frueherer eigener Import).
        catalog.register(host_catalog, catalog.CatalogEntry(
            participant_id="other1", chrononaut_id="CHR-SHARED", persona_key="other1",
        ))
        catalog.store_figure_save(
            host_catalog, "other1", "CHR-SHARED",
            full_v7_save("CHR-SHARED", name="other1", save_id="fixture-other1-001"),
        )
        # guest1 bringt (kollidierend) DIESELBE char_id mit.
        _register_private_figure(guest_onboarding, guest_catalog, "guest1", "CHR-SHARED")

        host_session = TuiSession(
            onboarding_dir=host_onboarding, catalog_dir=host_catalog, participant_id="host1",
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH, host_capable=True,
        )
        guest_session = TuiSession(
            onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id="guest1",
            run_dir=run_dir, host_capable=False,
        )
        host_session._cmd_table_offer(["mesaF1foreign"])
        guest_session._cmd_table_request_join(["mesaF1foreign"])

        printed: list[str] = []
        host_session._print = printed.append
        host_session._cmd_table_accept(["mesaF1foreign", "guest1"])

        assert any("geparkt" in p and "Fremdzuordnung" in p for p in printed), printed
        # 0 Writes am massgeblichen Figurenstand: kein eigener Figursave
        # fuer guest1 im Hostkatalog, kein veroeffentlichter Current.
        assert catalog.load_figure_save(host_catalog, "guest1", "CHR-SHARED") is None
        ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
        try:
            published = core_store.load_current_save_or_raise(run_dir, "guest1", ps_store, states_dir=states_dir)
        except core_store.CurrentSaveUnavailableError:
            published = None
        assert published is None, "guest1 haette KEINEN veroeffentlichten Current-Save bekommen duerfen."
        # KEINE wirksame halbe Aufnahme: der Gast ist NICHT im Roster,
        # seine Anfrage bleibt ehrlich OFFEN/pending (retry-faehig,
        # Sidecar bleibt erhalten).
        record = table_admission.load_record(run_dir, "mesaF1foreign")
        assert "guest1" not in record["roster"], (
            f"guest1 haette bei geparkter Figurenuebernahme NICHT als angenommenes "
            f"Rostermitglied gebucht werden duerfen: {record}"
        )
        assert "guest1" in record["requests"], (
            f"Die Anfrage haette ehrlich offen/pending bleiben muessen: {record}"
        )
        from mmo_sim.ui.tui import _read_table_guest_offer
        assert _read_table_guest_offer(run_dir, "mesaF1foreign", "guest1") is not None, (
            "Sidecar haette bei geparkter Uebernahme erhalten bleiben muessen (retry-faehig)."
        )


def test_f1_f5_accept_parks_on_active_binding_zero_writes():
    """Gegenprobe (b) (R4-Nachzug Briefing A Punkt 1 + Generalnachschaerfung
    "keine wirksame halbe Aufnahme"): die mitgebrachte Char-ID ist bereits
    an einem ANDEREN Tisch aktiv gebunden (`core_store.Lobby.
    lock_chrononaut`, dieselbe Autoritaet wie `core_store.
    chrononaut_active_binding`) -- die Annahme bleibt kontrolliert
    GEPARKT, 0 Writes am massgeblichen Figurenstand, UND der Gast bleibt
    NICHT im Roster (seine Anfrage bleibt ehrlich offen/pending)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        host_onboarding, host_catalog = d / "host_onboarding", d / "host_catalog"
        guest_onboarding, guest_catalog = d / "guest_onboarding", d / "guest_catalog"
        write_test_profile(run_dir, max_turns=200)
        _register_host_figure(host_onboarding, host_catalog, run_dir, states_dir, "host1", "CHR-HOST1")
        _register_private_figure(guest_onboarding, guest_catalog, "guest1", "CHR-GUEST1")

        # CHR-GUEST1 ist bereits an einem ANDEREN (elsewhere laufenden)
        # Tisch aktiv gebunden -- derselbe Lock-Speicher, den
        # `core_store.chrononaut_active_binding` liest.
        core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy()).lock_chrononaut(
            "CHR-GUEST1", "anderer-tisch-id",
        )

        host_session = TuiSession(
            onboarding_dir=host_onboarding, catalog_dir=host_catalog, participant_id="host1",
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH, host_capable=True,
        )
        guest_session = TuiSession(
            onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id="guest1",
            run_dir=run_dir, host_capable=False,
        )
        host_session._cmd_table_offer(["mesaF1locked"])
        guest_session._cmd_table_request_join(["mesaF1locked"])

        printed: list[str] = []
        host_session._print = printed.append
        host_session._cmd_table_accept(["mesaF1locked", "guest1"])

        assert any("geparkt" in p for p in printed), printed
        assert catalog.load_figure_save(host_catalog, "guest1", "CHR-GUEST1") is None
        ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
        try:
            published = core_store.load_current_save_or_raise(run_dir, "guest1", ps_store, states_dir=states_dir)
        except core_store.CurrentSaveUnavailableError:
            published = None
        assert published is None, "guest1 haette waehrend aktiver Fremdbindung KEINEN Current bekommen duerfen."
        # KEINE wirksame halbe Aufnahme: der Gast ist NICHT im Roster,
        # seine Anfrage bleibt ehrlich OFFEN/pending.
        record = table_admission.load_record(run_dir, "mesaF1locked")
        assert "guest1" not in record["roster"], (
            f"guest1 haette bei geparkter (fremdgebundener) Figurenuebernahme NICHT als "
            f"angenommenes Rostermitglied gebucht werden duerfen: {record}"
        )
        assert "guest1" in record["requests"], (
            f"Die Anfrage haette ehrlich offen/pending bleiben muessen: {record}"
        )


def test_f1_f5_accept_identical_retry_is_noop_identical_no_double_effect():
    """Gegenprobe (c) (R4-Nachzug Briefing A Punkt 1, A20-Analogon):
    bringt derselbe Gast seine BEREITS hostseitig uebernommene, BYTE-
    IDENTISCHE Figur an einem zweiten Tisch erneut mit, loest die geteilte
    Op `noop_identical` aus -- kein zweiter Fortschritt/Doppeleffekt,
    kein erneuter Figursave-Write."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        host_onboarding, host_catalog = d / "host_onboarding", d / "host_catalog"
        guest_onboarding, guest_catalog = d / "guest_onboarding", d / "guest_catalog"
        write_test_profile(run_dir, max_turns=200)
        _register_host_figure(host_onboarding, host_catalog, run_dir, states_dir, "host1", "CHR-HOST1")
        _register_private_figure(guest_onboarding, guest_catalog, "guest1", "CHR-GUEST1")

        host_session = TuiSession(
            onboarding_dir=host_onboarding, catalog_dir=host_catalog, participant_id="host1",
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH, host_capable=True,
        )
        guest_session = TuiSession(
            onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id="guest1",
            run_dir=run_dir, host_capable=False,
        )
        # Erster Tisch: regulaere Erstannahme (register_new).
        host_session._cmd_table_offer(["mesaF1retryA"])
        guest_session._cmd_table_request_join(["mesaF1retryA"])
        host_session._cmd_table_accept(["mesaF1retryA", "guest1"])
        figure_after_first = catalog.load_figure_save(host_catalog, "guest1", "CHR-GUEST1")
        assert figure_after_first is not None
        figure_write_time_first = (host_catalog / "figures" / "guest1__CHR-GUEST1.json").stat().st_mtime_ns

        # Zweiter Tisch: dieselbe (unveraenderte) private Figur erneut
        # angeboten -- die geteilte Op erkennt die bereits bekannte,
        # BYTE-IDENTISCHE Char-ID und liefert `noop_identical`.
        printed: list[str] = []
        host_session._print = printed.append
        host_session._cmd_table_offer(["mesaF1retryB"])
        guest_session._cmd_table_request_join(["mesaF1retryB"])
        host_session._cmd_table_accept(["mesaF1retryB", "guest1"])

        assert any("identisch" in p for p in printed), printed
        figure_write_time_second = (host_catalog / "figures" / "guest1__CHR-GUEST1.json").stat().st_mtime_ns
        assert figure_write_time_second == figure_write_time_first, (
            "Ein identischer Retry haette den bereits hinterlegten Figursave NICHT erneut "
            "schreiben duerfen (kein Doppeleffekt)."
        )
        assert catalog.load_figure_save(host_catalog, "guest1", "CHR-GUEST1") == figure_after_first


def test_f1_f5_rejected_request_leaves_current_save_unchanged():
    """Gegenprobe (d) (R4-Nachzug Briefing A Punkt 1): eine vom Host
    ABGELEHNTE Anfrage (`_cmd_table_reject`, kein `_cmd_table_accept`)
    hinterlaesst GAR KEINEN veroeffentlichten Current-Save fuer den Gast --
    kein halber/stillschweigend uebernommener Zustand."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        host_onboarding, host_catalog = d / "host_onboarding", d / "host_catalog"
        guest_onboarding, guest_catalog = d / "guest_onboarding", d / "guest_catalog"
        write_test_profile(run_dir, max_turns=200)
        _register_host_figure(host_onboarding, host_catalog, run_dir, states_dir, "host1", "CHR-HOST1")
        _register_private_figure(guest_onboarding, guest_catalog, "guest1", "CHR-GUEST1")

        host_session = TuiSession(
            onboarding_dir=host_onboarding, catalog_dir=host_catalog, participant_id="host1",
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH, host_capable=True,
        )
        guest_session = TuiSession(
            onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id="guest1",
            run_dir=run_dir, host_capable=False,
        )
        host_session._cmd_table_offer(["mesaF1reject"])
        guest_session._cmd_table_request_join(["mesaF1reject"])
        host_session._cmd_table_reject(["mesaF1reject", "guest1"])

        record = table_admission.load_record(run_dir, "mesaF1reject")
        assert "guest1" not in record["roster"], record
        assert catalog.load_figure_save(host_catalog, "guest1", "CHR-GUEST1") is None
        ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
        try:
            published = core_store.load_current_save_or_raise(run_dir, "guest1", ps_store, states_dir=states_dir)
        except core_store.CurrentSaveUnavailableError:
            published = None
        assert published is None, "Eine abgelehnte Annahme haette KEINEN Current-Save veroeffentlichen duerfen."


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
