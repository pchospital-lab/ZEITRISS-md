#!/usr/bin/env python3
"""
tests/mmo_sim/test_r3_f3_host_persona_authority.py — ZR-FIGURENREISE-TISCH-
NACHZUG-20261102-R3, enger Nachzug F3 (02_NACHZUG.md §B/F3,
review/independent-r2-review.md §3 F3_HOST_PERSONA_AUTHORITY).

Deckt die zwei in der Review benannten normalen Ausweichpfade, die die
Bestandsgrenze bisher umgingen -- BEIDE mit demselben, zu §1 spiegel-
bildlichen `table_admission`-/Betreiber-Mechanismus:

- §1 `_cmd_table_request_persona` prueft zwar die eigene Bestandsliste, bindet
  den Zielhost des angefragten Tisches aber NICHT -- eine eigene bestaetigte
  Persona von Host A konnte ueber das normale Kommando einen offenen Tisch
  von Host B anfragen. Der Fix lehnt eine Anfrage an einen Tisch mit FREMDEM
  `host_id` ab (0 Writes vor Abweisung).

- §2 die normalen Treiberwege fuer freie Persona-/Leader-IDs
  (`persona:<id>` / `lead:persona:<id>`, DIREKT als Expertenalias ODER ueber
  den GEFUEHRTEN Auswahlweg -- `_local_round_select_ai` ->
  `_local_round_build_tokens`; beide muenden in genau einen `_cmd_local_round`)
  durften bisher jede freie ID als Persona treiben. Die Grenze ist
  SYMMETRISCH zu §1: ein Alias darf keine ID als Persona treiben, die SELBST
  ein aktiver FREMDER Betreiber ist (ein `table_admission`-Record mit
  `host_id == <id>`, state offen/gestartet) -- das waere das Marionettenspiel
  eines anderen Betreibers (Review: "Ein Alias darf eine bekannte ID
  auswaehlen, aber keinen anderen Bestand freigeben"). Reine Lesepruefung
  (`table_admission.find_open_host_table`) VOR jedem Audit-Logwrite, Consent-
  oder Modellaufruf -- 0 Writes, 0 Calls bei Ablehnung.

Erhaelt (Regressionsschutz, Baseline-Sweep `run-r3/worker/s2-baseline-
sweep.md`: KEIN legitim getriebener Persona-Token ist zugleich eigener
Betreiber): die eigene/freie Experten-Persona OHNE eigenen Betreibertisch
(a24/ux1_r5/p1/r4/i1/g03) UND der aufrufende Teilnehmer selbst (`<id> ==
self.participant_id` -- auch wenn er selbst gerade einen eigenen Tisch
betreibt, bleibt sein EIGENER Persona-/KI-Leader-Alias zulaessig). Eine
unbekannte freie ID faellt unveraendert auf den `_resolve_member`->None-
Negativpfad. Der direkte Expertenalias einer freien, NICHT-betreibenden
Persona bleibt damit am unveraenderten Consent-/Admission-Gate gebunden
(NICHT besitz-gesperrt) -- Gegenprobe unten.

Fakes nur am GM-/Persona-Transportrand, Muster aus
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

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core import lobby_service  # noqa: E402
from mmo_sim.core import table_admission  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.community_bootstrap import bootstrap_community  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


class _SpyFactory:
    """Wirft SOFORT bei Aufruf -- Nachweis Providerfreiheit (Muster aus
    `test_r2_f1_f2_f3_tabledienst_2026_11_02.py`). Bei einer korrekten
    §2-Betreiber-Abweisung VOR dem Treiber-/Modellrand darf diese Factory
    nie konstruiert/aufgerufen werden."""

    def __init__(self, label: str):
        self.label = label
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        raise AssertionError(f"Spy-Factory '{self.label}' wurde aufgerufen (Gate-Bruch).")


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
    ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, participant_id, char_id, save)
    core_store.publish_current_save(run_dir, participant_id, save, ps_store, states_dir)
    return save


def _bootstrap_own_persona(run_dir: Path, states_dir: Path, host_id: str, persona_key: str) -> None:
    """Legt `persona_key` als EIGENE bestaetigte Hostpersona von `host_id`
    an (Muster aus `test_r2_f1_f2_f3_tabledienst_2026_11_02.py`)."""
    ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
    community_dir = run_dir / "community"
    drafts = {
        persona_key: {
            "real_name": persona_key, "archetype": "Test-Archetyp",
            "play_style": "SIMULIERT/DEMO", "charwunsch": "SIMULIERT/DEMO (R3-F3-Testfixture).",
            "plays_char": {
                "save_file": "NOCH_NICHT_ERSCHAFFEN", "character_id": "NOCH_NICHT_ERSCHAFFEN",
                "name": "NOCH_NICHT_ERSCHAFFEN", "callsign": "NOCH_NICHT_ERSCHAFFEN",
            },
        },
    }
    result = bootstrap_community(community_dir, f"community-{host_id}", 1, drafts, ps_store, states_dir, today="2026-11-02")
    assert persona_key in result.personas_written, result.reason


def _host_session(onboarding_dir, catalog_dir, run_dir, states_dir, participant_id, *, factories: bool = True):
    kwargs = dict(
        onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=participant_id,
        run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH, host_capable=True,
    )
    if factories:
        kwargs["gm_transport_factory"] = _SpyFactory(f"{participant_id}_gm")
        kwargs["persona_driver_factory"] = _SpyFactory(f"{participant_id}_persona")
    return TuiSession(**kwargs)


def _table_files(run_dir: Path) -> list[str]:
    tables_dir = run_dir / "tables"
    return sorted(p.name for p in tables_dir.glob("*.json")) if tables_dir.exists() else []


# --------------------------------------------------------------------------
# §1 -- `_cmd_table_request_persona`: Zielhost-Bindung (R2-Nachzug geschlossen)
# --------------------------------------------------------------------------
def test_f3_request_persona_rejects_foreign_table_host_before_mutation():
    """F3 §1: Host A's eigene bestaetigte Persona darf NICHT an einen von
    Host B offenen Tisch anfragen, auch wenn die Persona im eigenen Bestand
    steht -- 0 Writes vor Abweisung."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)
        _bootstrap_own_persona(run_dir, states_dir, "hostA", "ownpersona_a")

        table_admission.offer_table(run_dir, host_id="hostB", table_key="mesaB")

        host_a_session = _host_session(onboarding_dir, catalog_dir, run_dir, states_dir, "hostA", factories=False)
        printed: list[str] = []
        host_a_session._print = printed.append
        host_a_session._cmd_table_request_persona(["mesaB", "ownpersona_a"])
        assert any("fremden Betreiber" in p for p in printed), printed

        record = table_admission.load_record(run_dir, "mesaB")
        assert record["requests"] == [], (
            f"Fremde-Tisch-Persona-Anfrage haette NICHT mutieren duerfen: {record}"
        )
        assert record["roster"] == ["hostB"], record


def test_f3_request_persona_accepts_own_table_rejects_foreign_table_same_persona():
    """F3 §1 Positive Gegenprobe: dieselbe eigene Persona darf am EIGENEN
    Tisch weiterhin anfragen -- die Zielhost-Pruefung engt die bereits
    angenommene positive Bahn nicht ein."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)
        _bootstrap_own_persona(run_dir, states_dir, "hostA", "ownpersona_a")
        table_admission.offer_table(run_dir, host_id="hostA", table_key="mesaA")

        host_a_session = _host_session(onboarding_dir, catalog_dir, run_dir, states_dir, "hostA", factories=False)
        host_a_session._print = lambda *_a: None
        host_a_session._cmd_table_request_persona(["mesaA", "ownpersona_a"])
        record = table_admission.load_record(run_dir, "mesaA")
        assert record["requests"] == ["ownpersona_a"], record


# --------------------------------------------------------------------------
# §2 -- `table_admission.find_open_host_table`: reine Betreiber-Lesefunktion
# --------------------------------------------------------------------------
def test_f3_find_open_host_table_reader_semantics():
    """F3 §2 (Lesekern): `find_open_host_table` liefert den `table_key` eines
    AKTIVEN (offen/gestartet) Tisches, dessen Betreiber die ID IST, sonst
    None -- die exakte Entscheidungsgrundlage des Treibergates. Keine
    Mutation."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        # keine Ablage -> None (kein Verzeichnis).
        assert table_admission.find_open_host_table(run_dir, "operatorx") is None

        # offener eigener Tisch -> erkannt.
        table_admission.offer_table(run_dir, host_id="operatorx", table_key="mesax")
        assert table_admission.find_open_host_table(run_dir, "operatorx") == "mesax"
        # fremde/unbekannte ID ohne eigenen Tisch -> None (bleibt treibbar).
        assert table_admission.find_open_host_table(run_dir, "freeexpert") is None

        # gestarteter Tisch bleibt aktiv -> weiterhin erkannt.
        table_admission.start_table(run_dir, table_key="mesax", host_id="operatorx")
        assert table_admission.find_open_host_table(run_dir, "operatorx") == "mesax"

        # geschlossener Tisch ist NICHT mehr aktiv -> None (Betreiber inaktiv).
        table_admission.close_table(run_dir, table_key="mesax", host_id="operatorx")
        assert table_admission.find_open_host_table(run_dir, "operatorx") is None


# --------------------------------------------------------------------------
# §2 -- `_cmd_local_round`: Treibergate gegen fremden aktiven Betreiber
# --------------------------------------------------------------------------
def test_f3_local_round_rejects_driving_foreign_operator_as_persona_before_write_or_model():
    """F3 §2 (Kern): ein `persona:<id>`-Treiber, dessen `<id>` SELBST ein
    aktiver fremder Betreiber ist, wird im normalen `_cmd_local_round`-Weg
    abgewiesen -- VOR jedem Offer-Logwrite und VOR jedem Treiber-/Modell-
    aufruf (0 Writes, 0 Calls). Der fremde Tisch bleibt unveraendert."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)
        _register_own_figure(onboarding_dir, catalog_dir, "host1", "CHR-HOST1", run_dir=run_dir, states_dir=states_dir)
        # 'operatorx' ist selbst aktiver Betreiber eines EIGENEN offenen Tisches.
        table_admission.offer_table(run_dir, host_id="operatorx", table_key="mesax")

        host_session = _host_session(onboarding_dir, catalog_dir, run_dir, states_dir, "host1")
        printed: list[str] = []
        host_session._print = printed.append
        before = _table_files(run_dir)

        host_session._cmd_local_round(["persona:operatorx"])

        assert any("aktiver Betreiber" in p and "operatorx" in p and "mesax" in p for p in printed), printed
        assert host_session.gm_transport_factory.calls == 0, "GM-Factory darf nicht konstruiert werden"
        assert host_session.persona_driver_factory.calls == 0, "Persona-Factory darf nicht konstruiert werden"
        assert lobby_service.read_offer_log(run_dir) == [], "kein Offer-/Audit-Write vor Abweisung"
        assert _table_files(run_dir) == before, "kein Tisch angelegt"
        rec = table_admission.load_record(run_dir, "mesax")
        assert rec["state"] == table_admission.STATE_OPEN and rec["roster"] == ["operatorx"] and rec["requests"] == [], rec


def test_f3_local_round_rejects_driving_foreign_operator_as_leader_before_write_or_model():
    """F3 §2 (Leaderweg): derselbe Betreiber-Schutz greift fuer
    `lead:persona:<id>` -- ein Alias darf einen fremden aktiven Betreiber
    auch nicht als KI-Leader treiben."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)
        _register_own_figure(onboarding_dir, catalog_dir, "host1", "CHR-HOST1", run_dir=run_dir, states_dir=states_dir)
        table_admission.offer_table(run_dir, host_id="operatorx", table_key="mesax")

        host_session = _host_session(onboarding_dir, catalog_dir, run_dir, states_dir, "host1")
        printed: list[str] = []
        host_session._print = printed.append

        host_session._cmd_local_round(["lead:persona:operatorx"])

        assert any("aktiver Betreiber" in p and "operatorx" in p for p in printed), printed
        assert host_session.gm_transport_factory.calls == 0, printed
        assert host_session.persona_driver_factory.calls == 0, printed
        assert lobby_service.read_offer_log(run_dir) == [], "kein Offer-/Audit-Write vor Abweisung"
        rec = table_admission.load_record(run_dir, "mesax")
        assert rec["state"] == table_admission.STATE_OPEN and rec["roster"] == ["operatorx"], rec


def test_f3_local_round_guided_tokens_for_foreign_operator_hit_same_gate():
    """F3 §2 (gefuehrter Weg): die REALE Tokenausgabe des gefuehrten
    Auswahlwegs (`_local_round_build_tokens`) fuer einen ausgewaehlten
    fremden Betreiber ist ein `persona:`/`lead:persona:`-Token, das in
    denselben `_cmd_local_round`-Gate laeuft und dort abgewiesen wird --
    der Leak ist NICHT nur auf dem direkten Expertenalias geschlossen."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)
        _register_own_figure(onboarding_dir, catalog_dir, "host1", "CHR-HOST1", run_dir=run_dir, states_dir=states_dir)
        table_admission.offer_table(run_dir, host_id="operatorx", table_key="mesax")
        host_session = _host_session(onboarding_dir, catalog_dir, run_dir, states_dir, "host1")
        host_session._print = lambda *_a: None

        # Gefuehrte Auswahl von 'operatorx' als Mitspieler (Leader = Host selbst).
        guest_tokens = host_session._local_round_build_tokens(["host1"], ["operatorx"], "host1")
        assert guest_tokens == ["persona:operatorx"], guest_tokens
        # Gefuehrte Auswahl von 'operatorx' als Leader.
        leader_tokens = host_session._local_round_build_tokens(["host1"], ["operatorx"], "operatorx")
        assert leader_tokens == ["lead:persona:operatorx"], leader_tokens

        for tokens in (guest_tokens, leader_tokens):
            printed: list[str] = []
            host_session._print = printed.append
            host_session._cmd_local_round(tokens, guided=True, initial_focus="host1")
            assert any("aktiver Betreiber" in p for p in printed), (tokens, printed)
            assert host_session.gm_transport_factory.calls == 0, (tokens, printed)
            assert host_session.persona_driver_factory.calls == 0, (tokens, printed)
            host_session._print = lambda *_a: None
        assert lobby_service.read_offer_log(run_dir) == [], "kein Offer-/Audit-Write vor Abweisung"


def test_f3_local_round_preserves_own_operators_self_persona_drive():
    """F3 §2 Erhaltungsprobe (Self-Exemption): betreibt der AUFRUFER selbst
    einen eigenen offenen Tisch, bleibt sein EIGENER Persona-Alias
    (`persona:<self>`) zulaessig -- die Betreiber-Grenze UND die R4-Nachzug-
    Bestandsgrenze treffen nur FREMDE IDs, nie `self.participant_id` selbst.

    R4-Nachzug (F3-Rest): der zusaetzlich angefragte 'ghostguest' ist eine
    unbekannte freie ID (kein eigener Bestand, keine Figur) -- er stoppt die
    Runde jetzt BEREITS am neuen Bestandsgate (VOR jedem Treiber-/
    Modellaufruf), nicht mehr erst an der spaeteren Figurpruefung
    (`_resolve_member`->None). Nachgewiesen ohne Modellaufruf; der eigene
    Alias wird davor weiterhin NICHT abgewiesen."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)
        _register_own_figure(onboarding_dir, catalog_dir, "host1", "CHR-HOST1", run_dir=run_dir, states_dir=states_dir)
        # host1 betreibt SELBST einen eigenen offenen Tisch -> er IST Betreiber.
        table_admission.offer_table(run_dir, host_id="host1", table_key="mesaown")
        assert table_admission.find_open_host_table(run_dir, "host1") == "mesaown"

        host_session = _host_session(onboarding_dir, catalog_dir, run_dir, states_dir, "host1")
        printed: list[str] = []
        host_session._print = printed.append
        # Eigener Persona-Alias + eine unbekannte freie ID (stoppt jetzt sauber
        # am Bestandsgate, VOR jedem Treiber-/Modellaufruf).
        host_session._cmd_local_round(["persona:host1", "persona:ghostguest"])

        # Der eigene Alias wurde NICHT betreiber-gesperrt ...
        assert not any("aktiver Betreiber" in p for p in printed), printed
        # ... die Runde stoppt stattdessen am Bestandsgate fuer die unbekannte
        # freie ID, ohne Modellaufruf -- NICHT (mehr) an der Figurpruefung.
        assert any(
            "ghostguest" in p and "keine eigene bestaetigte" in p for p in printed
        ), printed
        assert not any("keine abgeschlossene Figur" in p for p in printed), printed
        assert host_session.gm_transport_factory.calls == 0, printed
        assert host_session.persona_driver_factory.calls == 0, printed
        # Eigener Tisch unveraendert.
        rec = table_admission.load_record(run_dir, "mesaown")
        assert rec["state"] == table_admission.STATE_OPEN and rec["roster"] == ["host1"], rec


def test_f3_local_round_rejects_driving_foreign_known_persona_without_own_table_valid_admission():
    """F3-Rest (Generalbefund F3, Negativ Bestandsgrenze): eine fremde, REAL
    existierende Persona (echte, aufloesbare Figur), die KEIN eigener
    bestaetigter Bestand von `host1` ist (`_known_ai_overview` liefert sie
    NICHT) UND KEINEN eigenen Betreibertisch fuehrt (`find_open_host_table`
    findet nichts), wird jetzt am Bestandsgate gehalten -- VOR jedem Write/
    Modellaufruf (0 Writes, 0 Calls).

    GUELTIGE Admission (`write_test_profile`) ist hier bewusst gesetzt: die
    Ablehnung darf NICHT nur daran liegen, dass kein Admissionprofil
    existiert. Nachgewiesener Gegensatz zum unveraenderten R3-Code (s.
    B-report.md, Gap-Proof): dort erreicht GENAU dieser Fall bei gueltiger
    Admission tatsaechlich den `persona_driver_factory`-Aufruf (1 Call) --
    der reine Betreiber-Check `find_open_host_table` reicht NICHT, um die
    beauftragte Bestandsfrage zu beantworten."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)  # GUELTIGE Admission.
        _register_own_figure(onboarding_dir, catalog_dir, "host1", "CHR-HOST1", run_dir=run_dir, states_dir=states_dir)
        # 'freepersona' hat eine ECHTE, aufloesbare Figur, ist aber KEIN
        # eigener Bestand von host1 (keine `_bootstrap_own_persona`) UND KEIN
        # eigener Betreiber (kein `table_admission`-Record).
        _register_own_figure(onboarding_dir, catalog_dir, "freepersona", "CHR-FREE", run_dir=run_dir, states_dir=states_dir)
        assert table_admission.find_open_host_table(run_dir, "freepersona") is None

        before = _table_files(run_dir)
        host_session = _host_session(onboarding_dir, catalog_dir, run_dir, states_dir, "host1")
        printed: list[str] = []
        host_session._print = printed.append
        host_session._cmd_local_round(["persona:freepersona"])

        # Der Alias wird NICHT betreiber-gesperrt (kein eigener Tisch von
        # 'freepersona') ...
        assert not any("aktiver Betreiber" in p for p in printed), printed
        # ... sondern am neuen Bestandsgate abgewiesen, VOR jedem Write/Call.
        assert any(
            "freepersona" in p and "keine eigene bestaetigte" in p for p in printed
        ), printed
        assert host_session.gm_transport_factory.calls == 0, printed
        assert host_session.persona_driver_factory.calls == 0, printed
        assert lobby_service.read_offer_log(run_dir) == [], "kein Offer-/Audit-Write vor Abweisung"
        assert _table_files(run_dir) == before, _table_files(run_dir)


def test_f3_direct_alias_own_confirmed_persona_reaches_consent_valid_admission():
    """F3-Rest (Generalbefund F3, Positiv): die EIGENE bestaetigte Persona
    (`_known_ai_overview()` liefert sie, NICHT der aufrufende Teilnehmer
    selbst) wird durch die neue Bestandsgrenze NICHT blockiert -- bei sonst
    GUELTIGER Admission/Host-Config erreicht der direkte Expertenalias
    `persona:<eigen>` tatsaechlich den realen Consent-/Spielweg: der Persona-
    Treiber wird am Modellrand fuer die Einladungsentscheidung
    (`decision_contract`) aufgerufen, die Zusage wird als 'accept'
    protokolliert, ein echter Tisch entsteht (`run_dir/tables/*.json`).

    Ersetzt die vorherige, UNVOLLSTAENDIGE Einrichtung dieses Tests (die
    Testpersona 'freepersona' war zuvor KEIN eigener Bestand von `host1` --
    s. B-report.md): die jetzige 'ownbot' ist ueber `_bootstrap_own_persona`
    ausdruecklich als eigene bestaetigte Hostpersona von `host1` angelegt.
    So bleiben die i1/a24-Basisregressionen (eigene/zustimmende Persona an
    den EIGENEN Tisch) strukturell unberuehrt."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)  # GUELTIGE Admission.
        _register_own_figure(onboarding_dir, catalog_dir, "host1", "CHR-HOST1", run_dir=run_dir, states_dir=states_dir)
        # 'ownbot' hat eine ECHTE, aufloesbare Figur UND ist eine EIGENE
        # bestaetigte Hostpersona von host1 -- der positive Fall, den die
        # Bestandsgrenze zulassen muss.
        _bootstrap_own_persona(run_dir, states_dir, "host1", "ownbot")
        _register_own_figure(onboarding_dir, catalog_dir, "ownbot", "CHR-OWNBOT", run_dir=run_dir, states_dir=states_dir)

        before = _table_files(run_dir)

        class _AcceptDriver:
            """Nimmt jede Einladungsentscheidung (`decision_contract`) real
            an -- derselbe Produktvertrag (`adapters.base.ParticipantDecision`)
            wie `_AcceptAllDriver` in `test_r4_organic_player_flow_2026_10_21.
            py`, hier lokal gehalten (kein Importzyklus ueber Testmodule)."""

            def __init__(self, pk: str):
                self.pk = pk
                self.calls: list[dict] = []

            def decide(self, ctx: dict) -> ParticipantDecision:
                self.calls.append(ctx)
                if "decision_contract" in ctx:
                    c = ctx["decision_contract"]
                    text = f"ENTSCHEIDUNG offer_id={c['offer_id']} participant_id={self.pk} decision=accept"
                    return ParticipantDecision(text=text, origin_source=f"accepttest:{self.pk}")
                return ParticipantDecision(text="Wir beobachten die Lage.", origin_source=f"accepttest:{self.pk}")

        drivers: dict[str, "_AcceptDriver"] = {}

        def persona_driver_factory(pk):
            drv = _AcceptDriver(pk)
            drivers[pk] = drv
            return drv

        class _NoOpGm:
            def __init__(self):
                self.calls = 0

            def turn(self, *a, **kw):
                self.calls += 1
                return {
                    "content": "Ihr beobachtet die Lage. Was tut ihr als naechstes?",
                    "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "t",
                }

        gm = _NoOpGm()
        host_session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="host1",
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: gm,
            persona_driver_factory=persona_driver_factory,
            host_capable=True,
        )
        printed: list[str] = []
        host_session._print = printed.append
        try:
            host_session._cmd_local_round(["persona:ownbot"])
        except EndOfInput:
            # Kontrollierte Pause am menschlichen Eigenzug des Testharness
            # (Default-`input_fn` liefert EOF) -- kein Fehlschlag, s. 02 §C.
            pass

        # Die eigene bestaetigte Persona wird NICHT am neuen Bestandsgate ...
        assert not any("keine eigene bestaetigte" in p for p in printed), printed
        # ... und NICHT an der Betreiber-Grenze abgewiesen.
        assert not any("aktiver Betreiber" in p for p in printed), printed
        # Der echte Consentweg wurde erreicht: der Persona-Treiber bekam die
        # Einladungsentscheidung (decision_contract) ...
        assert "ownbot" in drivers and drivers["ownbot"].calls, printed
        assert any("decision_contract" in c for c in drivers["ownbot"].calls), drivers["ownbot"].calls
        # ... und die Zusage wurde real als 'accept' protokolliert.
        offer_log = lobby_service.read_offer_log(run_dir)
        assert any(
            e.get("type") == "response" and e.get("from") == "ownbot" and e.get("decision") == "accept"
            for e in offer_log
        ), offer_log
        # Der Spielweg wurde tatsaechlich erreicht (ein echter Tisch ist
        # entstanden) -- nicht mehr am Admission-/Bestandsgate blockiert.
        assert _table_files(run_dir) != before, _table_files(run_dir)


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
