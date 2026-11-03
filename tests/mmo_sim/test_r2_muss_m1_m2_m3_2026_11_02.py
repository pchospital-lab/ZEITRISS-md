#!/usr/bin/env python3
"""
tests/mmo_sim/test_r2_muss_m1_m2_m3_2026_11_02.py — ZR-FIGURENREISE-TISCH-
NACHZUG-20261102-R2, gezielte Schliessung dreier im Auftrag (02_NACHZUG.md)
namentlich benannter Unterfaelle, die in der ersten R2-Runde ohne
ausgefuehrte Evidenz blieben:

M1 — F2 „Solo → Gruppe → Solo"-Folge (02_NACHZUG §F2, Z.25):
     eine kurze tatsaechliche Solo→Gruppe→Solo-Folge am wirklichen
     Startweg; der Gruppengast hat einen ANDEREN Level-Stand, das allein
     verhindert die Aufnahme nicht; Vorher/Nachher-Bindungs-/Abschlussbytes.
M2 — F3 „Leader-Gegenprobe" (02_NACHZUG §F3, Z.31/33):
     eine im Spielpfad ALS LEADER abgeleitete Persona
     (`store.derive_group_and_leader`) erhaelt KEINE
     `table_admission`-Hostrechte; 0 Writes.
M3 — F5 „unbeteiligte Persona" + „inaktive Heimatfigur" (02_NACHZUG §F5, Z.49):
     eine wirkungslose Aufnahme (Fremdzuordnungs-Konflikt eines
     zurueckkehrenden Gasts) laesst Hostfigur, unbeteiligte Persona UND
     inaktive Heimatfigur byteweise unveraendert; 0 Fremddatenverlust.

Fakes nur am GM-Transportrand (`_FakeTableGm`, Muster aus
`test_r2_f1_f2_f3_tabledienst_2026_11_02.py`) -- Produktpersistenz laeuft echt.

Pure Python, nur `assert`, echter Exitcode."""
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

from _full_v7_fixture import full_v7_save  # noqa: E402
from _section_completion_resume_fixtures import debrief_with_marker  # noqa: E402

from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core import table_admission  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.community_bootstrap import bootstrap_community  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


class _SpyFactory:
    """Wirft SOFORT bei Aufruf -- Nachweis Providerfreiheit (identisches
    Muster zu `test_r2_f1_f2_f3_tabledienst_2026_11_02.py`)."""

    def __init__(self, label: str):
        self.label = label

    def __call__(self, *args, **kwargs):
        raise AssertionError(f"Spy-Factory '{self.label}' wurde aufgerufen (Gate-Bruch).")


class _FakeTableGm:
    """Zwei SL-Antworten ohne Abschluss-Marker, danach (Zug 3+) der volle
    Debrief MIT Marker -- derselbe Rhythmus wie `_FakeTableGm` in den
    bestehenden R2-Suiten."""

    def __init__(self, debrief_text: str):
        self._debrief = debrief_text
        self.calls = 0

    def turn(self, turn_idx, text, **kw):
        self.calls += 1
        if self.calls < 3:
            return {"content": f"SL-Antwort #{self.calls} (kein Abschluss)."}
        return {"content": self._debrief}


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
    *, run_dir: Path | None = None, states_dir: Path | None = None,
) -> dict:
    save = full_v7_save(char_id, name=participant_id, save_id=f"fixture-{participant_id}-001", level=level)
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
    ))
    if run_dir is not None and states_dir is not None:
        ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
        onboarding.ensure_participant_persona_state(ps_store, states_dir, participant_id, char_id, save)
        core_store.publish_current_save(run_dir, participant_id, save, ps_store, states_dir)
    return save


def _bootstrap_own_persona(run_dir: Path, states_dir: Path, host_id: str, persona_key: str) -> None:
    """Legt `persona_key` als EIGENE bestaetigte Persona von `host_id` an
    (`bootstrap_community`-Produktfunktion) -- schreibt genau den
    Persona-State `states_dir/<persona_key>.json`, der unten als
    'unbeteiligte Persona' vor/nach verglichen wird."""
    ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
    community_dir = run_dir / "community"
    drafts = {
        persona_key: {
            "real_name": persona_key, "archetype": "Test-Archetyp",
            "play_style": "SIMULIERT/DEMO", "charwunsch": "SIMULIERT/DEMO (R2-M3-Testfixture).",
            "plays_char": {
                "save_file": "NOCH_NICHT_ERSCHAFFEN", "character_id": "NOCH_NICHT_ERSCHAFFEN",
                "name": "NOCH_NICHT_ERSCHAFFEN", "callsign": "NOCH_NICHT_ERSCHAFFEN",
            },
        },
    }
    result = bootstrap_community(community_dir, f"community-{host_id}", 1, drafts, ps_store, states_dir, today="2026-11-02")
    assert persona_key in result.personas_written, result.reason


def _snapshot_tree(*roots: Path) -> dict[str, bytes]:
    """Byteweiser Snapshot aller Dateien unter `roots` (rel. zu ihrem
    jeweiligen Elternteil, damit getrennte Wurzeln kollisionsfrei bleiben)."""
    snap: dict[str, bytes] = {}
    for root in roots:
        if not root.exists():
            continue
        for p in sorted(root.rglob("*")):
            if p.is_file():
                snap[str(p.relative_to(root.parent))] = p.read_bytes()
    return snap


# ── M1: F2 Solo -> Gruppe -> Solo ───────────────────────────────────────────


def test_m1_f2_solo_group_solo_sequence_distinct_sections_and_bytes():
    """M1 (02_NACHZUG §F2, Z.25): drei echte Abschnitte am wirklichen
    Startweg (`_cmd_table_start` -> `_cmd_local_round`), jeweils mit EIGENER
    gebundener section_id und echtem Abschluss. Der Gruppengast hat einen
    anderen Level-Stand (Level 3 ggue. Host Level 1) und wird dennoch
    aufgenommen -- der Levelunterschied allein blockt die Aufnahme nicht.
    Vorher/Nachher-Admissionsbytes (vor Start keine Bindung, nach Start
    gebunden + geschlossen) belegen die Folge; alle drei section_ids sind
    verschieden (kein zweiter Abschnitt derselben Identitaet)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)
        _register_own_figure(
            onboarding_dir, catalog_dir, "host1", "CHR-HOST1", level=1,
            run_dir=run_dir, states_dir=states_dir,
        )
        # ANDERER Level-/Abschnittsstand als der Host (02_NACHZUG §F2 Z.25).
        _register_own_figure(
            onboarding_dir, catalog_dir, "guest1", "CHR-GUEST1", level=3,
            run_dir=run_dir, states_dir=states_dir,
        )

        def _run_section(table_key: str, guest_ids: list[str], debrief_saves: dict, seq: str) -> str:
            fake_gm = _FakeTableGm(debrief_with_marker(debrief_saves))
            host_session = TuiSession(
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="host1",
                input_fn=_smart_input(), print_fn=lambda *_a, **_kw: None,
                run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
                gm_transport_factory=lambda: fake_gm, persona_driver_factory=_SpyFactory("host_persona"),
                host_capable=True,
            )
            host_session._cmd_table_offer([table_key])
            for g in guest_ids:
                gs = TuiSession(
                    onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=g,
                    input_fn=_smart_input(), print_fn=lambda *_a, **_kw: None,
                    run_dir=run_dir, host_capable=False,
                )
                gs._cmd_table_request_join([table_key])
                host_session._cmd_table_accept([table_key, g])

            rec_before = table_admission.load_record(run_dir, table_key)
            assert rec_before.get("section_id") is None, f"{seq}: vor Start noch keine Bindung erwartet."
            assert rec_before["roster"] == ["host1", *guest_ids], f"{seq}: roster vor Start={rec_before['roster']!r}"

            host_session._cmd_table_start([table_key])

            rec_after = table_admission.load_record(run_dir, table_key)
            assert rec_after.get("section_id"), f"{seq}: section_id haette gebunden sein muessen."
            assert rec_after["state"] == table_admission.STATE_CLOSED, (
                f"{seq}: Abschnitt haette real schliessen muessen (state={rec_after['state']!r})."
            )
            section = core_store.Table.load(run_dir, rec_after["section_id"])
            assert section.status == "closed", f"{seq}: Store-Tisch nicht geschlossen ({section.status!r})."
            return rec_after["section_id"]

        def _host_save(sid: str) -> dict:
            return full_v7_save("CHR-HOST1", name="host1", save_id=sid, level=1)

        def _guest_save(sid: str) -> dict:
            return full_v7_save("CHR-GUEST1", name="guest1", save_id=sid, level=3)

        sec_solo1 = _run_section("solo-a", [], {"CHR-HOST1": _host_save("fx-h-solo1")}, "Solo-1")
        sec_group = _run_section(
            "grp-b", ["guest1"],
            {"CHR-HOST1": _host_save("fx-h-grp"), "CHR-GUEST1": _guest_save("fx-g-grp")}, "Gruppe",
        )
        sec_solo2 = _run_section("solo-c", [], {"CHR-HOST1": _host_save("fx-h-solo2")}, "Solo-2")

        assert len({sec_solo1, sec_group, sec_solo2}) == 3, (
            f"Alle drei Abschnitte muessen verschiedene section_ids haben: "
            f"{sec_solo1!r}/{sec_group!r}/{sec_solo2!r}"
        )


# ── M2: F3 Leader-Gegenprobe ────────────────────────────────────────────────


def test_m2_f3_persona_as_derived_leader_gets_no_host_rights():
    """M2 (02_NACHZUG §F3, Z.31 'Eine als Leader eingesetzte Persona erhaelt
    keine Hostrechte', Z.33 '... Leader-Gegenprobe reichen'): Die im
    Spielpfad abgeleitete Leaderrolle (`store.derive_group_and_leader`,
    erste voll angenommene Offer) verleiht KEINE `table_admission`-
    Hostrechte -- jede host-only Transition prueft ausschliesslich den
    persistierten `record['host_id']`, NIE die abgeleitete Leaderrolle
    (table_admission.py Modul-Docstring Z.11-16). Der Leader-als-Host-
    Versuch wirft `HostAuthorityError` und hinterlaesst 0 Writes
    (byteidentischer Record)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir = d / "run"
        # Host-autoritativer Tisch gehoert ausschliesslich "host1".
        table_admission.offer_table(run_dir, host_id="host1", table_key="mesaL")

        # Im Spielpfad wird "persona_leader" ALS LEADER abgeleitet: sie bietet,
        # host1 nimmt vollstaendig an -> erste voll angenommene Offer.
        offer_log = [
            {"type": "offer", "id": "o1", "from": "persona_leader", "wants": ["host1"]},
            {"type": "consent", "offer_id": "o1", "from": "host1", "accept": True},
        ]
        derivation = core_store.derive_group_and_leader(offer_log)
        assert derivation.leader == "persona_leader", derivation
        assert derivation.leader != "host1", "Testvoraussetzung: Leader != Admission-Host."

        record_path = run_dir / "table_admission" / "mesaL.json"
        bytes_before = record_path.read_bytes()
        record_before = json.loads(bytes_before)
        assert record_before["host_id"] == "host1"

        # Jede host-only Transition, mit der ABGELEITETEN LEADER-ID aufgerufen,
        # muss abgewiesen werden -- die Leaderrolle ist kein Hostrecht.
        host_only_attempts = [
            lambda: table_admission.start_table(run_dir, table_key="mesaL", host_id="persona_leader"),
            lambda: table_admission.accept_request(run_dir, table_key="mesaL", host_id="persona_leader", guest_id="whoever"),
            lambda: table_admission.bind_section(run_dir, table_key="mesaL", host_id="persona_leader", section_id="sec-x"),
            lambda: table_admission.close_table(run_dir, table_key="mesaL", host_id="persona_leader"),
            lambda: table_admission.remove_member(run_dir, table_key="mesaL", host_id="persona_leader", guest_id="host1"),
        ]
        for attempt in host_only_attempts:
            try:
                attempt()
                raise AssertionError("Leader-als-Host-Versuch haette HostAuthorityError werfen muessen.")
            except table_admission.HostAuthorityError:
                pass

        # 0 Writes: der persistierte Record ist byteweise unveraendert.
        assert record_path.read_bytes() == bytes_before, (
            "Leader-Gegenprobe haette den Admission-Record NICHT aendern duerfen (0 Writes)."
        )

        # Positive Gegenprobe: der ECHTE Host (host1) darf dieselbe Operation.
        started = table_admission.start_table(run_dir, table_key="mesaL", host_id="host1")
        assert started["state"] == table_admission.STATE_STARTED


# ── M3: F5 unbeteiligte Persona + inaktive Heimatfigur ──────────────────────


def _run_import(session: TuiSession, raw_text: str) -> None:
    """Treibt `TuiSession._cmd_import()` mit vorab bereitgestelltem
    Mehrzeilentext (Muster `test_r2_f5_foreign_registration_conflict_...py`)."""
    lines = iter(raw_text.splitlines() + ["ENDE"])
    base_input = session._input

    def _fn(prompt: str = "") -> str:
        try:
            return next(lines)
        except StopIteration:
            return base_input(prompt)
    session._input = _fn
    session._cmd_import()
    session._input = base_input


def test_m3_f5_ineffective_intake_leaves_uninvolved_roles_byte_identical():
    """M3 (02_NACHZUG §F5, Z.49 'Zeige gezielte gespeicherte Vorher/
    Nachherbytes fuer Hostfigur, unbeteiligte Persona und inaktive
    Heimatfigur'): ein zurueckkehrender Gast (bob) bringt eine Figur mit,
    deren char_id im geteilten lokalen Install bereits einem ANDEREN
    Teilnehmer (alice) zugeordnet ist -- eine wirkungslose Aufnahme
    (Fremdzuordnungs-Konflikt VOR dem ersten Zielwrite). Drei ausdruecklich
    benannte unbeteiligte Rollen bleiben byteweise unveraendert:
      - Hostfigur (host1 / CHR-HOST1, aktiver Current + State + Katalog),
      - unbeteiligte Persona (bystanderpersona, Persona-State),
      - inaktive Heimatfigur (ida / CHR-HOME, registriert, nie gesperrt).
    bob erhaelt 0 Writes; alice (die zugeordnete Figur) verliert keine
    Fremddaten."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"

        # Hostfigur (aktiv).
        _register_own_figure(
            onboarding_dir, catalog_dir, "host1", "CHR-HOST1", level=2,
            run_dir=run_dir, states_dir=states_dir,
        )
        # Inaktive Heimatfigur (registriert + eigener Current, nie gesperrt).
        _register_own_figure(
            onboarding_dir, catalog_dir, "ida", "CHR-HOME", level=4,
            run_dir=run_dir, states_dir=states_dir,
        )
        # Die kollidierende Figur gehoert alice (zugeordnete Fremdfigur).
        _register_own_figure(
            onboarding_dir, catalog_dir, "alice", "CHR-SHARED", level=1,
            run_dir=run_dir, states_dir=states_dir,
        )
        # Unbeteiligte Persona (bestaetigt, ohne eigene Figur).
        _bootstrap_own_persona(run_dir, states_dir, "host1", "bystanderpersona")

        # Vorher-Bytes der drei benannten unbeteiligten Rollen (Current/State/
        # Katalog/Community) -- plus der zugeordneten Fremdfigur (alice).
        host_before = _snapshot_tree(
            run_dir / "current_saves", states_dir, catalog_dir,
        )
        # Explizite Einzelbelege (Audit): genau die drei benannten Dateien.
        host_current_before = (run_dir / "current_saves" / "host1.json").read_bytes()
        persona_state_before = (states_dir / "bystanderpersona.json").read_bytes()
        home_current_before = (run_dir / "current_saves" / "ida.json").read_bytes()
        alice_catalog_before = (catalog_dir / "catalog__alice.json").read_bytes()

        # bob (zurueckkehrender Gast, GLEICHER catalog_dir -- geteiltes lokales
        # Install) versucht, EXAKT die alice zugeordnete char_id zu importieren.
        foreign_save = full_v7_save("CHR-SHARED", name="bob", save_id="fixture-bob-return-001", level=9)
        raw_text = json.dumps(foreign_save, ensure_ascii=False)

        bob_session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="bob",
            input_fn=lambda p="": "n", print_fn=lambda *_a, **_kw: None,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH, host_capable=False,
        )
        printed: list[str] = []
        bob_session._print = printed.append
        _run_import(bob_session, raw_text)

        # Wirkungslose Aufnahme: Fremdzuordnungs-Konflikt, kein Write.
        assert any("Fremdzuordnungs-Konflikt" in p for p in printed), printed
        assert any("'alice'" in p for p in printed), printed

        # 0 Writes unter bob.
        assert not (catalog_dir / "catalog__bob.json").exists(), "bob haette KEINEN Katalogeintrag bekommen duerfen."
        bob_state = onboarding.peek(onboarding_dir, "bob")
        assert bob_state is None or bob_state.final_save is None, "bob haette KEINEN Onboarding-Stand bekommen duerfen."

        # Nachher-Bytes: die drei benannten Rollen + die zugeordnete Fremdfigur
        # sind byteweise unveraendert (kein Fremddatenverlust).
        assert (run_dir / "current_saves" / "host1.json").read_bytes() == host_current_before, "Hostfigur veraendert."
        assert (states_dir / "bystanderpersona.json").read_bytes() == persona_state_before, "Unbeteiligte Persona veraendert."
        assert (run_dir / "current_saves" / "ida.json").read_bytes() == home_current_before, "Inaktive Heimatfigur veraendert."
        assert (catalog_dir / "catalog__alice.json").read_bytes() == alice_catalog_before, "Alice (Fremdzuordnung) veraendert."

        # Gesamter persistenter Datenbaum der unbeteiligten Rollen unveraendert.
        host_after = _snapshot_tree(
            run_dir / "current_saves", states_dir, catalog_dir,
        )
        assert host_after == host_before, (
            "Der wirkungslose Import haette KEINE der bestehenden Dateien aendern/anlegen duerfen: "
            f"hinzugekommen/geaendert={sorted(set(host_after) - set(host_before)) or '—'}, "
            f"entfernt={sorted(set(host_before) - set(host_after)) or '—'}"
        )


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
