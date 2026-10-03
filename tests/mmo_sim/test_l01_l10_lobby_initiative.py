#!/usr/bin/env python3
"""
tests/mmo_sim/test_l01_l10_lobby_initiative.py — neue dauerhafte Regressionen
fuer den Lobby-Initiativdurchstich (01_AUFTRAG_LOBBY_INITIATIVE.md §4 A-E,
02_ABNAHME.md L01-L10, MAIN-DATENWEGENTSCHEIDUNG.md).

Deckt die neue Initiative AM PRODUKT (`ui/tui.py:TuiSession._cmd_lobby_
initiative`, Menuepunkt 'b') -- kein Testhelper baut den Tisch ausserhalb
des Produktwegs, Controllerlogik/Testdoubles liefern NUR deterministische
Entscheidungen/SL-Antworten, nie fehlende Produktlogik. Personas sind
markierte Testdoubles (`_ScriptedDriver`); die eigentliche Ableitung
(`core.store.derive_group_and_leader`/`create_table_from_offer_log`),
Requestautorisierung (`core.admission`/`core.request_ledger`) und Spiel-
runtime (`core.app_service.run_play_session`) laufen UNVERAENDERT ueber den
echten Produktweg.

L01 Community-Eintritt/>5 sichtbar/leerer Inferenzloop bei alle pausiert.
L02 eigener Vorschlag aus tatsaechlicher Aeusserung, eigener Kontext.
L03 Ablehnung -> kein Konsens/keine heimliche Restgruppe.
L04 0/6 -> kontrollierter Reject ohne Current-/Mitgliedschaftswrites.
L05/L06/L07 vollstaendige Lobby->Tisch->Abschnitt->Lobby-Reise (echte
    Factories + Loopback-HTTP fuer die Persona-Antwort).
L08 known-ID-Wiederaufnahme (kein Doppelrequest) UND echter Neustart-
    Prozess, der ein noch offenes eigenes Angebot weiterfuehrt.
L09 Admission-Stop VOR dem naechsten Request.
L10 manueller `l`-Weg bleibt unveraendert (Erhalt-Beleg ueber denselben
    `lobby_service.request_admitted_decision`, s. `test_l10_*`)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import lobby_service  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import _stop_flag_path, write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.community_bootstrap import bootstrap_community  # noqa: E402
from mmo_sim.domain.zeitriss.policy import (  # noqa: E402
    COMPLETION_MARKER,
    ZeitrissHarvestValidator,
    ZeitrissTableSizePolicy,
)
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
_FIX = _REPO_ROOT / "internal" / "qa" / "harness" / "lobby" / "fixtures" / "saves"
_FIXTURE_PERSONAS = ("sniper", "tech", "cqb", "face", "medic", "pyro")


class _ScriptedDriver:
    """Markiertes Testdouble an der Treibergrenze: liefert der Reihe nach
    `answers` als rohen Antworttext, unabhaengig vom Kontext (`decide`
    nimmt KEINE eigene Entscheidung vorweg -- die Interpretation der
    Kontrollvertraege passiert ausschliesslich im Produktweg, `adapters.
    base.interpret_decision_contract`/`interpret_initiative_proposal`)."""

    def __init__(self, persona_key: str, answers: list[str]):
        self.persona_key = persona_key
        self.config = None
        self.answers = list(answers)
        self.calls: list[dict] = []

    def decide(self, context: dict) -> ParticipantDecision:
        self.calls.append(context)
        text = self.answers.pop(0) if self.answers else "invalid"
        return ParticipantDecision(text=text, origin_source=f"fake:{self.persona_key}")


class _RaisingDriver:
    """Wirft bei JEDEM `.decide()`-Aufruf -- fuer L08/L09-Kontrollen, die
    beweisen sollen, dass GAR KEIN neuer Modellaufruf stattfindet."""

    def __init__(self, persona_key: str):
        self.persona_key = persona_key
        self.config = None

    def decide(self, context: dict) -> ParticipantDecision:
        raise AssertionError(f"unerwarteter Modellaufruf fuer {self.persona_key!r}")


class _TableGM:
    """Gescriptetes GM-Fake -- liefert nach `turns_before_marker` Turns den
    Abschluss-Marker fuer `table_id`/`section_id` ZUSAMMEN mit den echten
    v7-Save-Bloecken JEDES Mitglieds (`final_saves`, analog `SmartGmServer`
    in `e2e_real_subprocess_dialog.py`) -- ohne diese Bloecke kann
    `core.store.complete_section`/`_validate_harvest` keinen gueltigen
    Abschluss ernten (jedes Mitglied braucht GENAU EINEN passenden,
    identitaetsgeprueften Save-Block, s. `domain.zeitriss.saves.
    harvest_from_debrief`)."""

    def __init__(self, table_id: str, section_id: str, final_saves: dict[str, dict], turns_before_marker: int = 2):
        self.table_id = table_id
        self.section_id = section_id
        self.final_saves = final_saves
        self.turns_before_marker = turns_before_marker
        self.calls: list[str] = []

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append(text)
        if len(self.calls) >= self.turns_before_marker:
            debrief = "\n".join(
                f"```json\n{json.dumps(block, ensure_ascii=False)}\n```" for block in self.final_saves.values()
            )
            # Der Marker MUSS als eigene Top-Level-Zeile beginnen (tokens[0]
            # == marker, s. `core.completion_marker.completion_marker_
            # matches`) -- nicht mitten im Satz eingebettet.
            content = f"{debrief}\n{COMPLETION_MARKER} table_id={self.table_id} section_id={self.section_id}"
        else:
            content = "Ihr beobachtet die Umgebung aufmerksam. Was tut ihr als naechstes?"
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "table"}


def _new_env(root: Path):
    states_dir = root / "states"
    run_dir = root / "run"
    onboarding_dir = root / "onboarding"
    catalog_dir = root / "catalog"
    states_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    return _SCHEMA, states_dir, run_dir, onboarding_dir, catalog_dir


def _make_ready(onboarding_dir, states_dir, run_dir, persona_key: str) -> str:
    """Bringt `persona_key` in denselben spielbereiten Zustand wie eine
    bereits abgeschlossene, veroeffentlichte Erschaffung (fertiger Save,
    publizierter Current) -- KEIN neuer Erschaffungsdialog, KEIN Fixture-
    Karriereskript als Produktfunktion; nutzt ausschliesslich vorhandene
    Produktfunktionen (`onboarding`/`core.store.publish_current_save`),
    genau wie bestehende P1/P2-Tests (`test_p2_community_creation.py`)."""
    save = json.loads((_FIX / f"{persona_key}.json").read_text(encoding="utf-8"))
    chrono_id = save["characters"][0]["char_id"]
    ps_store = PersonaStateStore(schema_path=_SCHEMA)
    onboarding.start_or_resume(onboarding_dir, persona_key)
    onboarding.complete_with_save(onboarding_dir, persona_key, save, ZeitrissHarvestValidator(), chrono_id)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, persona_key, chrono_id, save)
    core_store.publish_current_save(run_dir, persona_key, save, ps_store, states_dir)
    return chrono_id


def _bootstrap_community(root: Path, community_id: str, persona_keys: list[str]):
    schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
    ps_store = PersonaStateStore(schema_path=schema_path)
    community_dir = run_dir / "community"
    drafts = {
        pk: {
            "real_name": pk, "archetype": "SIMULIERT", "play_style": "SIMULIERT",
            "charwunsch": "SIMULIERT/DEMO -- kein Erschaffungsdialog (Testfixture).",
            "plays_char": {
                "save_file": "NOCH_NICHT_ERSCHAFFEN", "character_id": "NOCH_NICHT_ERSCHAFFEN",
                "name": "NOCH_NICHT_ERSCHAFFEN", "callsign": "NOCH_NICHT_ERSCHAFFEN",
            },
        }
        for pk in persona_keys
    }
    bootstrap_community(community_dir, community_id, 1, drafts, ps_store, states_dir, today="2026-09-26")
    return schema_path, states_dir, run_dir, onboarding_dir, catalog_dir


def _session(participant_id, onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
             gm_transport_factory, persona_driver_factory, printed: list[str]):
    return TuiSession(
        onboarding_dir, catalog_dir, participant_id,
        input_fn=lambda prompt="": (_ for _ in ()).throw(EOFError()),
        print_fn=printed.append,
        run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
        gm_transport_factory=gm_transport_factory,
        persona_driver_factory=persona_driver_factory,
    )


def test_l01_all_paused_no_infinite_loop_large_lobby():
    """L01: >5 sichtbare Mitglieder, alle pausieren ihr Fenster -> keine
    Inferenzschleife, kein Tisch, keine neue Community/IDs."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = list(_FIXTURE_PERSONAS)  # 6 Mitglieder -- deckt "grosse Lobby >5" ab.
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _bootstrap_community(
            root, "community-op", keys,
        )
        write_test_profile(run_dir)
        for pk in keys:
            _make_ready(onboarding_dir, states_dir, run_dir, pk)

        drivers = {pk: _ScriptedDriver(pk, ['{"action": "pause"}']) for pk in keys}
        printed: list[str] = []
        session = _session(
            "op", onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
            gm_transport_factory=lambda *_a, **_kw: (_ for _ in ()).throw(AssertionError("kein GM-Call erwartet")),
            persona_driver_factory=lambda pk: drivers[pk],
            printed=printed,
        )
        session._cmd_lobby_initiative()
        out = "\n".join(printed)
        assert "6 Mitglieder" in out, out
        assert "alle Mitglieder pausiert" in out, out
        assert not list((run_dir / "tables").glob("*.json")), "kein Tischanlageversuch erwartet"
        assert core_store._read_locks(run_dir) == {}, "keine Chrononaut-Bindung ohne Tisch erwartet"
        # Keine neue Community/keine zusaetzlichen Personas erzeugt.
        from mmo_sim.domain.zeitriss.community_bootstrap import peek as peek_bootstrap
        result = peek_bootstrap(run_dir / "community", "community-op")
        assert sorted(result.personas_written) == sorted(keys)


def test_l02_l03_proposal_and_rejection_no_table():
    """L02: eigener Vorschlag aus tatsaechlicher Aeusserung (strukturierter
    Kontrollvertrag), eigener Kontext (system-Feld nicht leer). L03:
    Ablehnung -> kein Konsens, kein Tisch, keine heimliche Restgruppe."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["sniper", "tech"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _bootstrap_community(
            root, "community-op", keys,
        )
        write_test_profile(run_dir)
        for pk in keys:
            _make_ready(onboarding_dir, states_dir, run_dir, pk)

        sniper_driver = _ScriptedDriver("sniper", ['{"action": "propose", "wants": ["tech"]}'])
        tech_driver = _ScriptedDriver("tech", ["Ich habe leider keine Lust heute."])  # Prosa != Consent -> invalid -> reject
        drivers = {"sniper": sniper_driver, "tech": tech_driver}
        printed: list[str] = []
        session = _session(
            "op", onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
            gm_transport_factory=lambda *_a, **_kw: (_ for _ in ()).throw(AssertionError("kein GM-Call erwartet ohne Tisch")),
            persona_driver_factory=lambda pk: drivers[pk],
            printed=printed,
        )
        session._cmd_lobby_initiative()
        out = "\n".join(printed)
        assert "schlaegt eine Runde vor" in out and "wants=['tech']" in out, out
        # L02: der eigene Kontext (system-Feld) wurde tatsaechlich befuellt (nicht leer).
        assert sniper_driver.calls and sniper_driver.calls[0].get("system") is not None
        assert "ohne bestaetigten Tisch" in out, out
        assert not list((run_dir / "tables").glob("*.json"))
        assert core_store._read_locks(run_dir) == {}


def test_l04_oversize_group_controlled_reject_no_writes():
    """L04: 6 (0/6-Grenze verletzt: >5) -> kontrollierter Reject OHNE
    Current-/Mitgliedschaftswrites (kein Tisch, keine Locks)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = list(_FIXTURE_PERSONAS)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _bootstrap_community(
            root, "community-op", keys,
        )
        write_test_profile(run_dir)
        for pk in keys:
            _make_ready(onboarding_dir, states_dir, run_dir, pk)

        leader, guests = keys[0], keys[1:]
        # R1.2-Nachzug (REVIEW-LOBBY.md §3.2): offer_id traegt jetzt die
        # window_id -- `lobby_service.offer_id_for` ist die EINE Stelle, die
        # Produkt UND Test uebereinstimmend nutzen (keine zweite, davon
        # abweichende Formel). Erstes Fenster einer frischen Community ist
        # deterministisch "lobby-community-op-0"; leader wird als Erster
        # geplant (deterministische FairScheduler-Reihenfolge), turn_idx=0.
        offer_id = lobby_service.offer_id_for("lobby-community-op-0", leader, 0)
        drivers = {leader: _ScriptedDriver(leader, [json.dumps({"action": "propose", "wants": guests})])}
        for g in guests:
            drivers[g] = _ScriptedDriver(
                g, [f"ENTSCHEIDUNG offer_id={offer_id} participant_id={g} decision=accept"],
            )
        printed: list[str] = []
        session = _session(
            "op", onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
            gm_transport_factory=lambda *_a, **_kw: (_ for _ in ()).throw(AssertionError("kein GM-Call erwartet")),
            persona_driver_factory=lambda pk: drivers[pk],
            printed=printed,
        )
        session._cmd_lobby_initiative()
        out = "\n".join(printed)
        assert "konnte nicht angelegt werden" in out, out
        assert not list((run_dir / "tables").glob("*.json"))
        assert core_store._read_locks(run_dir) == {}


def _persona_http_server(responses: list[tuple[int, dict]]):
    class _Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            return

        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0) or 0)
            self.rfile.read(length) if length else b""
            self.server.calls.append(1)  # type: ignore[attr-defined]
            status, payload = self.server.next_response()  # type: ignore[attr-defined]
            data = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    class _Srv(HTTPServer):
        def __init__(self):
            super().__init__(("127.0.0.1", 0), _Handler)
            self.calls: list[int] = []
            self._responses = list(responses)
            self._thread = threading.Thread(target=self.serve_forever, daemon=True)

        def next_response(self):
            return self._responses.pop(0) if self._responses else (500, {"error": "keine weitere Antwort"})

        @property
        def base_url(self):
            host, port = self.server_address
            return f"http://{host}:{port}"

        def __enter__(self):
            self._thread.start()
            return self

        def __exit__(self, *exc):
            self.shutdown()
            self.server_close()

    return _Srv()


def test_l05_l06_l07_full_lobby_to_table_positive_journey_real_factories_loopback():
    """L05/L06/L07: vollstaendige positive Reise ueber ECHTE Factories +
    einen echten Loopback-HTTP-Server fuer die Gast-Persona (`tech`,
    `PersonaApiDriver` gegen 127.0.0.1) -- der Leader (`sniper`) ist ein
    markiertes Testdouble (Kontrollvertragsantworten sind erlaubt
    deterministisch, s. 02_ABNAHME). Deckt: eigener Vorschlag -> echte
    Zustimmung -> `create_table_from_offer_log` -> `run_play_session` mit
    mehreren gescripteten Spielturns -> gueltiger Abschluss -> Rueckkehr in
    die Lobby (Locks geloest, `Lobby.members()` enthaelt beide wieder) ->
    ein zweites, NEUES begrenztes Fenster sieht sie wieder als frei/bereit."""
    from mmo_sim.adapters.persona_api import PersonaApiConfig, PersonaApiDriver

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["sniper", "tech"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _bootstrap_community(
            root, "community-op", keys,
        )
        write_test_profile(run_dir)
        for pk in keys:
            _make_ready(onboarding_dir, states_dir, run_dir, pk)

        table_id = "lobby-sniper-tech"
        section_id = f"{table_id}-section"
        final_saves = {pk: json.loads((_FIX / f"{pk}.json").read_text(encoding="utf-8")) for pk in keys}
        gm = _TableGM(table_id, section_id, final_saves, turns_before_marker=3)
        sniper_driver = _ScriptedDriver("sniper", [
            json.dumps({"action": "propose", "wants": ["tech"]}),
            "Wir bewegen uns vorsichtig weiter.",
            "Bleibt aufmerksam, Ende der Runde.",
            "Ich nehme mit, dass wir gut zusammengespielt haben.",  # Pflicht-Reflexion (Leader)
        ])

        with _persona_http_server([
            (200, {"choices": [{"message": {
                "content": (
                    f"ENTSCHEIDUNG offer_id={lobby_service.offer_id_for('lobby-community-op-0', 'sniper', 0)} "
                    "participant_id=tech decision=accept explanation=Klingt gut."
                ),
            }}]}),
            # Gast-Importturn (`act(tech, attach_import_save=True)`, W2/A24) --
            # normaler Spieltext, KEIN save_payload (die Runtime bindet den
            # Save selbst aus `import_save_payload`, s. `core/runtime.py:act`).
            (200, {"choices": [{"message": {"content": "Ich sichere die rechte Flanke."}}]}),
            # Pflicht-KI-Reflexion (Gast) nach gueltigem Ernteschritt.
            (200, {"choices": [{"message": {"content": "Ich nehme mit, dass ich gut gedeckt war."}}]}),
        ]) as persona_srv:
            tech_driver = PersonaApiDriver(
                PersonaApiConfig(base_url=persona_srv.base_url, api_key="SYNTH", model="synthetic-e2e"), "tech",
            )
            drivers = {"sniper": sniper_driver, "tech": tech_driver}
            printed: list[str] = []
            session = _session(
                "op", onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
                gm_transport_factory=lambda *_a, **_kw: gm,
                persona_driver_factory=lambda pk: drivers[pk],
                printed=printed,
            )
            session._cmd_lobby_initiative()
            out = "\n".join(printed)
            assert "lobby_offer_response" not in out
            assert "antwortet auf Angebot" in out and "accept" in out, out
            assert "Lobby-Tisch abgeschlossen" in out, out
            assert persona_srv.calls, "Gast-Persona haette real ueber HTTP befragt werden muessen"

        table = core_store.Table.load(run_dir, table_id)
        assert table.status == "closed" and set(table.members) == {"sniper", "tech"}
        assert table.leader == "sniper"
        assert len(gm.calls) >= 3, "echte gescriptete Spielturns zwischen Import und Abschluss erwartet"

        # L07: Rueckkehr -- Locks geloest, beide wieder frei/spielbereit fuer
        # ein NEUES begrenztes Fenster (kein automatischer zweiter Abschnitt).
        assert core_store._read_locks(run_dir) == {}
        lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert set(lobby.members()) >= {"sniper", "tech"}

        # K1/K2-Nachzug (REVIEW-LOBBY.md §3: "Das gelieferte L05/L06/L07-
        # Szenario prueft im zweiten Fenster lediglich, ob die Ausgabe die
        # Mitglieder als frei/gebunden={} zeigt. Es prueft nicht die
        # tatsaechlichen neuen Antworten oder das Unterbleiben eines zweiten
        # Tischs."): ORIGINAL (oben) reichte ein EINZIGER geteilter
        # `_ScriptedDriver` fuer beide Personas und pruefte nur die
        # Roster-Textzeile. DERIVAT hier: je EIN eigener Driver pro Persona
        # (echte, tatsaechlich verbrauchte NEUE Antworten belegbar), UND ein
        # Beleg, dass NACH dem NEUEN (genuin anderen) Fenster kein zweiter
        # Tisch entsteht -- die neue stabile Fenster-ID (K1/K2) darf das
        # bereits resolvte erste Angebot nicht wiederverwenden.
        sniper_driver2 = _ScriptedDriver("sniper", ['{"action": "pause"}'])
        tech_driver2 = _ScriptedDriver("tech", ['{"action": "pause"}'])
        drivers2 = {"sniper": sniper_driver2, "tech": tech_driver2}
        printed2: list[str] = []
        session2 = _session(
            "op", onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
            gm_transport_factory=lambda *_a, **_kw: (_ for _ in ()).throw(AssertionError("kein GM-Call erwartet")),
            persona_driver_factory=lambda pk: drivers2[pk],
            printed=printed2,
        )
        session2._cmd_lobby_initiative()
        out2 = "\n".join(printed2)
        assert "frei/spielbereit=['sniper', 'tech']" in out2 or "'sniper'" in out2, out2
        assert "gebunden={}" in out2, out2
        # Echte NEUE Antworten -- BEIDE Driver tatsaechlich (real, nicht per
        # Ledger-Replay) genau einmal befragt, kein altes Angebot/Consent
        # wiederverwendet.
        assert len(sniper_driver2.calls) == 1, (
            f"sniper haette im NEUEN Fenster real (nicht per Ledger-Replay) gefragt werden muessen: "
            f"{len(sniper_driver2.calls)} Aufrufe"
        )
        assert len(tech_driver2.calls) == 1, (
            f"tech haette im NEUEN Fenster real (nicht per Ledger-Replay) gefragt werden muessen: "
            f"{len(tech_driver2.calls)} Aufrufe"
        )
        assert "'sniper' pausiert" in out2 and "'tech' pausiert" in out2, out2
        # Ausbleiben eines zweiten Tischs: weiterhin GENAU EIN Tisch
        # (`lobby-sniper-tech`), keine `__2`-Generation entstanden.
        assert sorted(p.name for p in (run_dir / "tables").glob("*.json")) == [f"{table_id}.json"], (
            "kein zweiter Tisch/keine neue Generation erwartet, solange beide pausieren"
        )


def test_l08_request_admitted_decision_no_duplicate_request_for_same_identity():
    """L08 (Einheitstest auf dem gemeinsamen Dienst selbst): fuer DIESELBE
    Operationsidentitaet (table_id/section_id/role/turn_idx/participant)
    sendet ein zweiter Aufruf KEINEN zweiten Request -- die bereits
    empfangene Antwort wird durabel wiederverwendet (kein Treiberaufruf,
    `_RaisingDriver` wuerde sonst sofort auffallen)."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        write_test_profile(run_dir)
        driver = _ScriptedDriver("sniper", ["Erste echte Antwort."])
        decision1, reason1 = lobby_service.request_admitted_decision(
            run_dir, driver, {"system": "s", "user": "u"},
            role="lobby_initiative", participant="sniper", section_id="lobby-x", turn_idx=0,
        )
        assert reason1 is None and decision1.text == "Erste echte Antwort."
        assert len(driver.calls) == 1

        raising = _RaisingDriver("sniper")
        decision2, reason2 = lobby_service.request_admitted_decision(
            run_dir, raising, {"system": "s", "user": "u"},
            role="lobby_initiative", participant="sniper", section_id="lobby-x", turn_idx=0,
        )
        assert reason2 is None
        assert decision2.text == "Erste echte Antwort.", "durable Antwort haette wiederverwendet werden muessen"
        assert decision2.origin_source == "ledger:recovered"

        # Andere Operationsidentitaet (anderer turn_idx) bleibt ein legitimer neuer Request.
        driver2 = _ScriptedDriver("sniper", ["Zweite echte Antwort, neuer Turn."])
        decision3, reason3 = lobby_service.request_admitted_decision(
            run_dir, driver2, {"system": "s", "user": "u"},
            role="lobby_initiative", participant="sniper", section_id="lobby-x", turn_idx=1,
        )
        assert reason3 is None and decision3.text == "Zweite echte Antwort, neuer Turn."
        assert len(driver2.calls) == 1


def test_l08_real_restart_process_resumes_open_offer_without_duplicate_offer():
    """L08 mit ECHTEM Neustart-Prozess: Prozess 1 (echter Subprozess
    `scripts/mmo_sim.py`) laesst 'sniper' ein Angebot stellen
    (`MMO_SIM_LOBBY_INITIATIVE_LIMIT=1`, danach beendet der begrenzte
    Schritt das Fenster). Prozess 2 ist ein WIRKLICH NEUER, eigenstaendiger
    Python-Prozess (andere PID) -- er liest das noch offene eigene Angebot
    aus dem persistenten Offer-Log weiter (kein zweites, doppeltes Angebot
    von 'sniper') und 'tech' antwortet real ueber Loopback-HTTP."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["sniper", "tech"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _bootstrap_community(
            root, "community-op", keys,
        )
        write_test_profile(run_dir)
        for pk in keys:
            _make_ready(onboarding_dir, states_dir, run_dir, pk)

        import os

        class _ProcessResult:
            def __init__(self, pid, returncode, stdout, stderr):
                self.pid = pid
                self.returncode = returncode
                self.stdout = stdout
                self.stderr = stderr

        def run_process(participant: str, stdin_text: str, env_extra: dict, limit: int) -> "_ProcessResult":
            """ECHTER, EIGENSTAENDIGER Python-Subprozess (`subprocess.Popen`,
            nicht dieselbe `TuiSession`-Instanz) -- `Popen.pid` belegt die
            tatsaechliche, von Prozess 1 verschiedene Betriebssystem-PID
            (L08: "wirklich neuer Interpreter"), `subprocess.run` allein
            liefert dafuer keine PID am `CompletedProcess`."""
            env = dict(os.environ)
            env.update(env_extra)
            env["MMO_SIM_LOBBY_INITIATIVE_LIMIT"] = str(limit)
            cmd = [sys.executable, str(_REPO_ROOT / "scripts" / "mmo_sim.py"),
                   "--data-dir", str(root), "--participant", participant]
            proc = subprocess.Popen(
                cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, env=env, cwd=str(root),
            )
            pid = proc.pid
            stdout, stderr = proc.communicate(input=stdin_text, timeout=30)
            return _ProcessResult(pid, proc.returncode, stdout, stderr)

        with _persona_http_server([
            # Prozess 1: 'sniper' erhaelt sein EIGENES Initiativfenster (kein
            # offenes Angebot wartet auf ihn) -> propose.
            (200, {"choices": [{"message": {"content": json.dumps({"action": "propose", "wants": ["tech"]})}}]}),
        ]) as persona_srv_1:
            env1 = {
                "MMO_SIM_PERSONA_API_BASE_URL": persona_srv_1.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTH", "MMO_SIM_PERSONA_API_MODEL": "synthetic-e2e",
                "OPENWEBUI_URL": "http://127.0.0.1:1", "OPENWEBUI_API_KEY": "unused",
            }
            p1 = run_process("op", "b\nx\n", env1, limit=1)
            assert p1.returncode == 0, p1.stderr
            assert "schlaegt eine Runde vor" in p1.stdout, p1.stdout

        log_after_p1 = lobby_service.read_offer_log(run_dir)
        offers_after_p1 = [r for r in log_after_p1 if r.get("type") == "offer"]
        assert len(offers_after_p1) == 1, "genau EIN Angebot nach Prozess 1 erwartet"
        offer_id = offers_after_p1[0]["offer_id"]
        table_id, section_id = "lobby-sniper-tech", "lobby-sniper-tech-section"
        final_saves = {pk: json.loads((_FIX / f"{pk}.json").read_text(encoding="utf-8")) for pk in keys}
        debrief_blocks = "\n".join(f"```json\n{json.dumps(b, ensure_ascii=False)}\n```" for b in final_saves.values())

        with _persona_http_server([
            # K1/K2-Nachzug (01_AUFTRAG_LOBBY_KONTINUITAET.md §3 A):
            # ORIGINAL (vor dem K1/K2-Fix, window_section_id = f"lobby-
            # {community_id}-{len(offene Angebote)}"): ein Neustart aenderte
            # die Requestidentitaet ("...-0" -> "...-1"), 'sniper' wurde
            # deshalb -- trotz bereits vollstaendig akzeptiertem eigenem
            # Vorschlag -- ERNEUT um eine eigene Initiative gebeten (musste
            # hier bewusst per Mock-Antwort "pause" antworten, um KEIN
            # zweites Angebot zu erzeugen).
            # DERIVAT (nach dem K1/K2-Fix, persistenter Fenster-Cursor +
            # `already_acted`-Vorpausierung, s. `ui/tui.py:_cmd_lobby_
            # initiative`): 'sniper' hat in DIESEM (fortgesetzten) Fenster
            # bereits ein offenes Angebot gestellt (`proposed_by`/`from`)
            # und wird deshalb ueberhaupt nicht mehr erneut geplant/gefragt
            # -- kein Request, kein Mock-Verbrauch fuer sniper noetig.
            # DIFF: -1 HTTP-Response (die fruehere sniper-"pause"-Antwort
            # entfaellt ersatzlos); 'tech' beantwortet jetzt als ERSTE
            # tatsaechliche Anfrage dieses (fortgesetzten) Fensters.
            (200, {"choices": [{"message": {
                "content": f"ENTSCHEIDUNG offer_id={offer_id} participant_id=tech decision=accept explanation=Ja.",
            }}]}),
            (200, {"choices": [{"message": {"content": "Wir sichern das Gebiet."}}]}),  # sniper Leader-Anker
            (200, {"choices": [{"message": {"content": "Ich bin bereit."}}]}),  # tech Gast-Import
            (200, {"choices": [{"message": {"content": "Ich nehme mit, dass wir gut zusammengespielt haben."}}]}),  # Reflexion sniper
            (200, {"choices": [{"message": {"content": "Ich nehme mit, dass ich gut gedeckt war."}}]}),  # Reflexion tech
        ]) as persona_srv_2, _persona_http_server([
            (200, {"choices": [{"message": {"content": "Ihr steht bereit. Was tut ihr?"}}]}),
            (200, {"choices": [{"message": {
                "content": f"{debrief_blocks}\n{COMPLETION_MARKER} table_id={table_id} section_id={section_id}",
            }}]}),
        ]) as gm_srv_2:
            env2 = {
                "MMO_SIM_PERSONA_API_BASE_URL": persona_srv_2.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTH", "MMO_SIM_PERSONA_API_MODEL": "synthetic-e2e",
                "OPENWEBUI_URL": gm_srv_2.base_url, "OPENWEBUI_API_KEY": "SYNTH",
            }
            p2 = run_process("op", "b\nx\n", env2, limit=2)
            assert p2.returncode == 0, p2.stderr
            assert p2.pid != p1.pid, "Prozess 2 muss ein ECHTER neuer Prozess sein (andere PID)"
            assert "schlaegt eine Runde vor" not in p2.stdout, (
                "sniper haette sein bereits offenes Angebot NICHT ein zweites Mal stellen duerfen: "
                f"{p2.stdout}"
            )
            assert "'sniper' pausiert" not in p2.stdout, (
                "sniper haette in diesem fortgesetzten Fenster gar nicht erst erneut geplant/gefragt "
                f"werden duerfen (already_acted-Vorpausierung, K1/K2): {p2.stdout}"
            )
            assert "antwortet auf Angebot" in p2.stdout and "accept" in p2.stdout, p2.stdout
            assert "Lobby-Tisch abgeschlossen" in p2.stdout, p2.stdout

        log_after_p2 = lobby_service.read_offer_log(run_dir)
        offers_after_p2 = [r for r in log_after_p2 if r.get("type") == "offer"]
        assert len(offers_after_p2) == 1, "kein zweites/doppeltes Angebot durch den Neustart entstanden"
        table = core_store.Table.load(run_dir, table_id)
        assert table.status == "closed" and set(table.members) == {"sniper", "tech"}


def test_l09_admission_stop_halts_before_next_request():
    """L09: ein bestehender Lab-Stop blockiert den ALLERERSTEN Request
    dieses Fensters -- kein weiterer Modellaufruf, kein kostenfreier Retry."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["sniper", "tech"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _bootstrap_community(
            root, "community-op", keys,
        )
        write_test_profile(run_dir)
        for pk in keys:
            _make_ready(onboarding_dir, states_dir, run_dir, pk)
        _stop_flag_path(run_dir).write_text(json.dumps({"reason": "Betreiber-Stop (Test)"}), encoding="utf-8")

        printed: list[str] = []
        session = _session(
            "op", onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
            gm_transport_factory=lambda *_a, **_kw: (_ for _ in ()).throw(AssertionError("kein GM-Call erwartet")),
            persona_driver_factory=lambda pk: _RaisingDriver(pk),
            printed=printed,
        )
        session._cmd_lobby_initiative()
        out = "\n".join(printed)
        assert "gestoppt (Admission-Gate" in out, out
        assert "Betreiber-Stop (Test)" in out, out


def test_l10_manual_l_path_uses_same_shared_admitted_decision_service():
    """L10 (Erhalt): der manuelle `l`-Weg bleibt unveraendert benutzbar UND
    nutzt jetzt real denselben Dienst (`lobby_service.request_admitted_
    decision`) wie die neue Lobbyinitiative -- kein stiller Wechsel von
    Mensch auf Persona, keine zweite Kontrollvertragsimplementierung."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["sniper", "tech"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _bootstrap_community(
            root, "community-op", keys,
        )
        write_test_profile(run_dir)
        for pk in keys:
            _make_ready(onboarding_dir, states_dir, run_dir, pk)

        final_saves = {pk: json.loads((_FIX / f"{pk}.json").read_text(encoding="utf-8")) for pk in keys}
        gm = _TableGM("local-sniper-tech", "local-sniper-tech-section", final_saves, turns_before_marker=1)
        tech_driver = _ScriptedDriver("tech", [
            "ENTSCHEIDUNG offer_id=invite-sniper-tech participant_id=tech decision=accept explanation=Dabei.",
        ])
        printed: list[str] = []
        session = _session(
            "sniper", onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
            gm_transport_factory=lambda *_a, **_kw: gm,
            persona_driver_factory=lambda pk: tech_driver,
            printed=printed,
        )
        from mmo_sim.ui.tui import EndOfInput

        try:
            session._cmd_local_round(["persona:tech"])
        except EndOfInput:
            # Der menschliche Leader-Anker bricht kontrolliert per EOF ab
            # (kein gescriptetes Terminal-Stdin hier) -- Consent + Tischanlage
            # sind bereits VOR diesem ersten Spielzug abgeschlossen, exakt wie
            # in `test_p2_community_creation.py`s Referenzpattern.
            pass
        out = "\n".join(printed)
        assert "Gruppe eingeladen" in out and "tech" in out, out
        # Derselbe request_ledger-Datensatz traegt jetzt (ueber lobby_service)
        # zusaetzlich den durablen result_text -- Beleg, dass der manuelle
        # Weg tatsaechlich denselben Dienst durchlaeuft, nicht eine Kopie.
        records = [
            json.loads(p.read_text(encoding="utf-8")) for p in (run_dir / "requests").glob("*.json")
        ]
        guest_invite_records = [r for r in records if r.get("role") == "guest_invite"]
        assert guest_invite_records and guest_invite_records[0].get("result_text"), (
            "manueller l-Weg sollte ueber lobby_service.request_admitted_decision laufen "
            "(result_text sollte jetzt durabel mitgeschrieben werden)"
        )


def test_l10_manual_l_path_repeated_invite_same_group_is_asked_again():
    """L10-Nacharbeit (END-CRITIC.md §6, kritischer Befund, selbst behoben):
    eine SPAETERE, inhaltlich unabhaengige Einladung an DIESELBE Gruppe
    (Leader+Gast identisch) MUSS real gefragt werden -- contract-v2
    `02_PRODUKTVERTRAG_MMO_SIM.md` §3 verlangt ausdruecklich, dass
    'wiederkehrende bekannte Mitspieler' funktionieren. Vor der Nacharbeit
    band `_admitted_invite_decision` (tui.py) `lobby_service.request_
    admitted_decision` OHNE `section_id`/`turn_idx` -- die Identitaet
    `(None, None, 'guest_invite', None, 'tech')` war ueber die gesamte
    Laufzeit von `run_dir` identisch, wodurch `find_durable_result` Runde 2
    faelschlich mit Runde 1s laengst abgeschlossener Antwort beantwortete,
    OHNE den Treiber ein zweites Mal aufzurufen (critic-Probe
    `probe2_same_offer.py`, 0 Treiberaufrufe in Runde 2). Runde 1 lehnt ab
    (kein Tisch, keine Lock-/GM-Seiteneffekte, `tech` bleibt frei); Runde 2,
    SPAETER, mit DERSELBEN Gruppe, muss `tech`s Treiber ERNEUT real
    aufrufen."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["sniper", "tech"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _bootstrap_community(
            root, "community-op", keys,
        )
        write_test_profile(run_dir)
        for pk in keys:
            _make_ready(onboarding_dir, states_dir, run_dir, pk)

        tech_driver = _ScriptedDriver("tech", [
            "ENTSCHEIDUNG offer_id=invite-sniper-tech participant_id=tech decision=reject "
            "explanation=Runde1-nicht-jetzt.",
            "ENTSCHEIDUNG offer_id=invite-sniper-tech participant_id=tech decision=reject "
            "explanation=Runde2-immer-noch-nicht-aber-ECHT-neu-gefragt.",
        ])
        printed: list[str] = []
        session = _session(
            "sniper", onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
            gm_transport_factory=lambda *_a, **_kw: None,
            persona_driver_factory=lambda pk: tech_driver,
            printed=printed,
        )

        session._cmd_local_round(["persona:tech"])
        assert len(tech_driver.calls) == 1, "Runde 1 sollte tech genau einmal real fragen"
        out1 = "\n".join(printed)
        assert "nicht angenommen" in out1 and "reject" in out1, out1

        printed.clear()
        session._cmd_local_round(["persona:tech"])
        assert len(tech_driver.calls) == 2, (
            "Runde 2 (dieselbe Gruppe Leader=sniper/Gast=tech, SPAETER) muss tech ERNEUT real "
            "fragen -- vor der Nacharbeit wurde hier 0 Mal gefragt (stille Wiederverwendung der "
            "Ablehnung aus Runde 1 ueber `find_durable_result`, s. END-CRITIC.md §6)"
        )
        out2 = "\n".join(printed)
        assert "nicht angenommen" in out2 and "reject" in out2, out2


if __name__ == "__main__":
    import traceback

    tests = [
        test_l01_all_paused_no_infinite_loop_large_lobby,
        test_l02_l03_proposal_and_rejection_no_table,
        test_l04_oversize_group_controlled_reject_no_writes,
        test_l05_l06_l07_full_lobby_to_table_positive_journey_real_factories_loopback,
        test_l08_request_admitted_decision_no_duplicate_request_for_same_identity,
        test_l08_real_restart_process_resumes_open_offer_without_duplicate_offer,
        test_l09_admission_stop_halts_before_next_request,
        test_l10_manual_l_path_uses_same_shared_admitted_decision_service,
        test_l10_manual_l_path_repeated_invite_same_group_is_asked_again,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
            passed += 1
        except Exception:
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed}/{len(tests)} Tests bestanden.")
    sys.exit(0 if failed == 0 else 1)
