#!/usr/bin/env python3
"""tests/mmo_sim/test_local_tokenhost_creation_2026_11_14.py — ZR-LOCAL-
TOKENHOST-N1, B1 (O4/O5-Unterfall): Erschaffung mit echtem Rollenbezug.

Macht den in 01_GENERALREVIEW.md/N1-05 belegten Fehler auf dem L1-Snapshot
sichtbar und bestaetigt den reparierten Weg: `mmo_sim/core/creation_
service.py:run_admitted_creation_dialog` rief `read_admission_block`/
`request_ledger.begin` VOR dem N1-Fix OHNE jeden `gm_transport.is_dollar_
billed`-Bezug auf -- beide blieben am Default `dollar_billed=True` haengen,
UNABHAENGIG vom tatsaechlich uebergebenen GM-Transport. Ein echter lokaler
(`is_dollar_billed=False`) Transport haette dadurch trotzdem als
dollarpflichtig gebucht/gegatet, ein echter Cloud-Gegenfall waere nicht von
einem lokalen Fall unterscheidbar gewesen.

Erreicht den reparierten Weg ueber die ECHTEN Produktfunktionen:
  - `mmo_sim.core.creation_service.run_admitted_creation_dialog` -- derselbe
    gemeinsame Kern, den `ui/tui.py:_cmd_new_or_switch_character` (Mensch)
    UND `domain/zeitriss/community_creation.py` (Persona) aufrufen. Der
    menschliche Pfad wird hier GENAUSO wie in `ui/tui.py:_human_get_reply`
    angesteuert (gleicher `role="creation_dialog"`-Vertrag, gleiche
    Admission-/Ledger-Bindung) -- ohne eine vollstaendige `TuiSession` zu
    konstruieren (ausserhalb vertretbarem Testaufwand fuer dieses enge
    Zeitfenster); das ist eine bewusste, im IMPL-REPORT benannte Grenze.
  - `mmo_sim.domain.zeitriss.community_creation.advance_one_persona_creation`
    (Persona-Erstfigur ueber den echten Community-Einstieg).
  - `mmo_sim.domain.zeitriss.community_creation.advance_additional_persona_
    creation` (Persona-Zusatzfigur ueber den echten Community-Einstieg).

Nur das aeusserste GM-Transport-Fake (`_GM`, analog `test_p2_community_
creation.py`/`test_r1_persona_b1_b2_rework_2026_10_02.py`) ersetzt den
Netzwerkrand -- Admission/Ledger/Onboarding/Catalog/Store laufen echt. Kein
echter Modellcall, kein Netz, kein Docker, keine echten Saves/Figuren
ausser den synthetischen Testfixtures. Pure Python, `unittest`."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import unittest.mock as mock
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
_SETUP_PY = _SCRIPTS_DIR / "setup.py"
_LOCAL_PROFILE_PY = _SCRIPTS_DIR / "local_model_profile.py"

# Repo-Root IMMER an Position 0 (nicht nur "falls fehlend"): in CI laeuft jede
# Testdatei als eigener Prozess, wo der Skriptordner (_HERE) automatisch auf
# sys.path[0] liegt; zusaetzlich fuegt setup.py sich selbst "scripts/" an
# sys.path[0] an. Ohne diese explizite Voranstellung traefe ein frischer
# "import mmo_sim" faelschlich das gleichnamige Launcher-Shim
# "scripts/mmo_sim.py" statt des echten Pakets ("mmo_sim is not a package").
sys.path.insert(0, str(_REPO_ROOT))


def _load(name: str, path: Path):
    """Laedt ein scripts/-Modul per Pfad unter eindeutigem Namen, ohne
    "scripts/" dauerhaft vor den Repo-Root auf sys.path zu zwingen."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# Das mmo_sim-Paket VOR dem Laden von setup.py importieren/cachen. Einmal in
# sys.modules, ist die spaetere sys.path-Reihenfolge fuer diese Importe egal.
from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import request_ledger  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.creation_service import ReplyResult, run_admitted_creation_dialog  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.community_bootstrap import bootstrap_community  # noqa: E402
from mmo_sim.domain.zeitriss.community_creation import (  # noqa: E402
    advance_additional_persona_creation,
    advance_one_persona_creation,
)
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402

# setup.py / local_model_profile.py erst JETZT (nach dem mmo_sim-Cache) per Pfad
# laden -- setup.py schiebt sich selbst "scripts/" an sys.path[0], was dem
# bereits gecachten mmo_sim-Paket nicht mehr schaden kann.
lmp = _load("n1_local_model_profile_under_test", _LOCAL_PROFILE_PY)
setup_mod = _load("n1_setup_under_test", _SETUP_PY)

from _full_v7_fixture import full_v7_block_text, full_v7_save  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


def _v7_block(char_id: str, name: str = "Nova") -> str:
    return full_v7_block_text(char_id, name=name, level=1)


def _new_env(root: Path):
    schema_path = _SCHEMA
    states_dir = root / "states"
    run_dir = root / "run"
    onboarding_dir = root / "onboarding"
    catalog_dir = root / "catalog"
    states_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    return schema_path, states_dir, run_dir, onboarding_dir, catalog_dir


class _GM:
    """Aeusserstes GM-Transport-Fake -- traegt `is_dollar_billed`/
    `output_limit_tokens`/`base_url` wie ein echter Adapter
    (`GmOwuiTransport`/Testdoubles in `test_p2_community_creation.py`).
    Liefert bei `reply_is_save=True` SOFORT einen vollstaendigen v7-Block
    (Dialog schliesst im ERSTEN Turn ab, kein `get_reply`/Persona-Call
    noetig) -- hinreichend, um GENAU den Admission-/Ledger-Bindungsfehler
    (N1-05) sichtbar zu machen, ohne einen mehrstufigen Dialog zu
    simulieren."""

    def __init__(self, reply_text: str, *, is_dollar_billed=True, output_limit_tokens=4096, base_url=None):
        self.reply_text = reply_text
        self.is_dollar_billed = is_dollar_billed
        self.output_limit_tokens = output_limit_tokens
        self.base_url = base_url
        self.calls = 0

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls += 1
        return {
            "content": self.reply_text, "usage": {"prompt_tokens": 12, "completion_tokens": 8},
            "sources": [], "latency_s": 0.01, "chat_id": "creation-n1-test",
        }


class _LegacyGM:
    """Transport-Fake OHNE `is_dollar_billed`-Attribut -- alte/Cloud-
    Transporte, fuer die `getattr(gm_transport, 'is_dollar_billed', True)`
    auf den Default `True` zurueckfallen MUSS (02-Vorgabe: "Default True
    fuer alte/Cloudtransporte")."""

    def __init__(self, reply_text: str):
        self.reply_text = reply_text
        self.calls = 0

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls += 1
        return {"content": self.reply_text, "usage": {"prompt_tokens": 1, "completion_tokens": 1},
                "sources": [], "latency_s": 0.0, "chat_id": "creation-n1-legacy"}


class _AcceptPersonaDriver:
    """Persona-Treiber-Fake, der jede Einladungs-/Entscheidungsfrage mit
    einer strukturell validierbaren Zustimmung beantwortet. Fuer die Faelle
    unten NIE tatsaechlich fuer eine Erschaffungsfrage aufgerufen (der GM
    liefert den fertigen Save bereits im ersten Turn) -- `.calls` bestaetigt
    das explizit."""

    def __init__(self, persona_key: str):
        self.persona_key = persona_key
        self.calls = 0

    def decide(self, context: dict) -> ParticipantDecision:
        self.calls += 1
        return ParticipantDecision(text="Bereit.", origin_source="TEST_N1_B1", meta={"usage": {}})


def _ledger_role_records(run_dir: Path, role: str) -> list[dict]:
    return [r for r in request_ledger._all_records(run_dir) if r.get("role") == role]


def _write_fake_local_home(root: Path) -> Path:
    """Baut ein PRIVATES Fixture-`~/.openwebui_env` mit einem gueltigen
    lokalen Profil (`ZEITRISS_MODEL_PROVIDER=local`) -- fuer
    `community_creation.py:_early_gate_dollar_billed()`/`_tui_early_gate_
    dollar_billed()`, die `setup.resolve_model_provider()` OHNE expliziten
    `env_path` aufrufen (dieselbe Stelle, die die echte Transport-Factory
    nutzt). NIE die echte Nutzerdatei -- `Path.home` wird vom Aufrufer per
    `mock.patch.object` auf GENAU dieses Tempverzeichnis umgelenkt."""
    fake_home = root / "fake_home"
    fake_home.mkdir(parents=True, exist_ok=True)
    env_path = fake_home / ".openwebui_env"
    updates = lmp.build_local_profile_updates(
        base_url="http://127.0.0.1:18001/v1", model="nemotron-n1-b1-test",
        api_key="test-local-token-not-secret",
    )
    assert setup_mod._update_env_file_preserving(env_path, updates)
    return fake_home


class HumanEquivalentCreationDollarBillingTests(unittest.TestCase):
    """`run_admitted_creation_dialog` direkt angesteuert -- derselbe
    gemeinsame Kern/Vertrag wie `ui/tui.py:_human_get_reply`
    (`role='creation_dialog'`, kein eigener Modellrequest fuer die
    menschliche Antwortseite)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        _, _, self.run_dir, self.onboarding_dir, _ = _new_env(self.root)

    def _never_called_get_reply(self, _turn_idx: int, _sl_text: str) -> ReplyResult:
        raise AssertionError(
            "get_reply darf hier nie aufgerufen werden -- der GM liefert den fertigen "
            "v7-Block bereits im ersten Turn."
        )

    def test_local_transport_bypasses_dollar_gate_ledger_reflects_dollar_billed_false(self):
        """N1-05-Kernfehler: VOR dem Fix blieb `dollar_billed` im Ledger
        IMMER `True` -- ein echter lokaler (`is_dollar_billed=False`)
        GM-Transport haette trotzdem dollarpflichtig gegatet/gebucht. Mit
        `max_usd=0.0` UND `dollar_billed=False` muss die Erschaffung trotzdem
        bis zum Save durchlaufen (der Dollargate ist fuer diese Rolle nicht
        zustaendig), UND das Ledger muss den tatsaechlichen Transport
        widerspiegeln, nicht den alten Default."""
        write_test_profile(self.run_dir, max_usd=0.0)
        onboarding.start_or_resume(self.onboarding_dir, "human-leader")
        gm = _GM(_v7_block("chrono-human-local"), is_dollar_billed=False)
        outcome = run_admitted_creation_dialog(
            run_dir=self.run_dir, onboarding_dir=self.onboarding_dir,
            participant_id="human-leader", turn_idx_start=0,
            initial_outgoing="Ich moechte eine Figur erschaffen.",
            gm_transport=gm, get_reply=self._never_called_get_reply,
            harvest_validator=ZeitrissHarvestValidator(), role="creation_dialog",
        )
        self.assertEqual(outcome.status, "completed", outcome.reason)
        self.assertEqual(outcome.chrononaut_id, "chrono-human-local")
        self.assertEqual(gm.calls, 1)
        records = _ledger_role_records(self.run_dir, "creation_dialog")
        self.assertTrue(records, "mindestens ein creation_dialog-Ledgereintrag erwartet.")
        for rec in records:
            self.assertFalse(rec["dollar_billed"], rec)
            self.assertIn("prompt_tokens", rec["usage"])

    def test_cloud_legacy_transport_still_stops_at_max_usd_zero_no_bypass(self):
        """Gegenfall: ein Transport OHNE `is_dollar_billed`-Attribut (alt/
        Cloud) muss weiterhin am Default `dollar_billed=True` haengen --
        `max_usd=0.0` stoppt VOR der ersten GM-Completion, keine Erschaffung,
        kein automatischer Dollargate-Bypass durch den N1-Fix."""
        write_test_profile(self.run_dir, max_usd=0.0)
        onboarding.start_or_resume(self.onboarding_dir, "human-leader-cloud")
        gm = _LegacyGM(_v7_block("chrono-human-cloud"))
        outcome = run_admitted_creation_dialog(
            run_dir=self.run_dir, onboarding_dir=self.onboarding_dir,
            participant_id="human-leader-cloud", turn_idx_start=0,
            initial_outgoing="Ich moechte eine Figur erschaffen.",
            gm_transport=gm, get_reply=self._never_called_get_reply,
            harvest_validator=ZeitrissHarvestValidator(), role="creation_dialog",
        )
        self.assertEqual(outcome.status, "paused", outcome.reason)
        self.assertEqual(gm.calls, 0, "kein einziger echter GM-Call -- das Gate stoppt VOR dem Versand.")

    def test_stop_check_still_wins_over_local_dollar_exempt_route(self):
        """O5-Gegenfall (Q07-Analogon fuer die Erschaffung): ein adressierter
        Stop muss den lokalen (`dollar_billed=False`, sonst dollar-
        gatefreien) Erschaffungspfad trotzdem anhalten -- der N1-Fix
        exemptiert NUR den Dollargate, keine universellen Stop-/Turn-Checks."""
        write_test_profile(self.run_dir, max_usd=0.0)
        onboarding.start_or_resume(self.onboarding_dir, "human-leader-stop")
        gm = _GM(_v7_block("chrono-human-stop"), is_dollar_billed=False)
        outcome = run_admitted_creation_dialog(
            run_dir=self.run_dir, onboarding_dir=self.onboarding_dir,
            participant_id="human-leader-stop", turn_idx_start=0,
            initial_outgoing="Ich moechte eine Figur erschaffen.",
            gm_transport=gm, get_reply=self._never_called_get_reply,
            harvest_validator=ZeitrissHarvestValidator(), role="creation_dialog",
            stop_check=lambda: True,
        )
        self.assertEqual(outcome.status, "stopped", outcome.reason)
        self.assertEqual(gm.calls, 0, "Stop muss VOR jedem GM-Request gewinnen, auch im dollar-exempten lokalen Pfad.")


class PersonaCommunityCreationDollarBillingTests(unittest.TestCase):
    """Dieselbe N1-05-Bindung ueber den echten Community-Einstieg
    (`advance_one_persona_creation`/`advance_additional_persona_creation`) --
    Persona-Erstfigur UND Persona-Zusatzfigur."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.schema_path, self.states_dir, self.run_dir, self.onboarding_dir, self.catalog_dir = _new_env(self.root)
        self.ps_store = PersonaStateStore(schema_path=self.schema_path)

    def test_persona_first_figure_local_transport_ledger_reflects_dollar_billed_false(self):
        """Persona-Erstfigur ueber den echten Community-Einstieg
        (`advance_one_persona_creation`), lokaler GM-Transport."""
        community_dir = self.run_dir / "community"
        draft = {"persona_first": {
            "real_name": "PersonaFirst", "archetype": "SIMULIERT: Technik",
            "play_style": "SIMULIERT: eigenstaendig", "charwunsch": "SIMULIERT/DEMO.",
            "plays_char": {"save_file": "NOCH_NICHT_ERSCHAFFEN", "character_id": "NOCH_NICHT_ERSCHAFFEN",
                           "name": "NOCH_NICHT_ERSCHAFFEN", "callsign": "NOCH_NICHT_ERSCHAFFEN"},
        }}
        bootstrap_community(community_dir, "community-n1-b1", 1, draft, self.ps_store, self.states_dir, today="2026-11-14")
        write_test_profile(self.run_dir, max_usd=0.0)
        fake_home = _write_fake_local_home(self.root)

        gm = _GM(_v7_block("chrono-persona_first"), is_dollar_billed=False)
        driver = _AcceptPersonaDriver("persona_first")
        with mock.patch.object(Path, "home", return_value=fake_home):
            outcome = advance_one_persona_creation(
                run_dir=self.run_dir, states_dir=self.states_dir, schema_path=self.schema_path,
                onboarding_dir=self.onboarding_dir, catalog_dir=self.catalog_dir,
                community_id="community-n1-b1", generation=1, persona_key="persona_first",
                gm_transport_factory=lambda *a, **k: gm,
                persona_driver_factory=lambda pk: driver,
            )
        self.assertEqual(outcome.status, "completed", outcome.reason)
        self.assertEqual(gm.calls, 1)
        self.assertEqual(driver.calls, 0, "Persona-Treiber darf fuer einen im ersten Turn fertigen Save nicht gebraucht werden.")
        records = _ledger_role_records(self.run_dir, "community_creation_gm")
        self.assertTrue(records, "mindestens ein community_creation_gm-Ledgereintrag erwartet.")
        for rec in records:
            self.assertFalse(rec["dollar_billed"], rec)

    def _give_existing_figure(self, participant_id: str, char_id: str, name: str) -> dict:
        """Minimaler bestehender Bestand fuer die Zusatzfigur-Vorbedingung --
        derselbe Produktweg wie `test_r1_persona_b1_b2_rework_2026_10_02.py:
        _give_existing_figure`."""
        self.ps_store.save_state(participant_id, {
            "v": 2, "persona_key": participant_id, "real_name": name,
            "archetype": "N1-B1-NACHWEIS", "play_style": "N1-B1-NACHWEIS", "charwunsch": "N1-B1-NACHWEIS",
            "plays_char": {"save_file": "NOCH_NICHT_ERSCHAFFEN", "character_id": "NOCH_NICHT_ERSCHAFFEN",
                           "name": "NOCH_NICHT_ERSCHAFFEN", "callsign": "NOCH_NICHT_ERSCHAFFEN"},
            "rounds_played": 1,
        }, states_dir=self.states_dir)
        save = full_v7_save(char_id, name=name, level=5, save_id=f"fixture-{char_id}")
        onboarding.start_or_resume(self.onboarding_dir, participant_id)
        onboarding.complete_with_save(self.onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
        onboarding.ensure_participant_persona_state(self.ps_store, self.states_dir, participant_id, char_id, save)
        catalog.register(self.catalog_dir, catalog.CatalogEntry(
            participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
        ))
        catalog.store_figure_save(self.catalog_dir, participant_id, char_id, save)
        core_store.publish_current_save(self.run_dir, participant_id, save, self.ps_store, self.states_dir)
        catalog.bind_for_section(self.catalog_dir, participant_id, char_id, has_open_section=False)
        return save

    def test_persona_additional_figure_local_transport_ledger_reflects_dollar_billed_false(self):
        """Persona-Zusatzfigur ueber den echten Community-Einstieg
        (`advance_additional_persona_creation`), lokaler GM-Transport."""
        self._give_existing_figure("persona_extra", "chrono-extra-old", "ExtraOld")
        write_test_profile(self.run_dir, max_usd=0.0)
        fake_home = _write_fake_local_home(self.root)

        generation = len(catalog.list_for_participant(self.catalog_dir, "persona_extra")) + 1
        gm = _GM(_v7_block("chrono-extra-new"), is_dollar_billed=False)
        driver = _AcceptPersonaDriver("persona_extra")
        with mock.patch.object(Path, "home", return_value=fake_home):
            outcome = advance_additional_persona_creation(
                run_dir=self.run_dir, states_dir=self.states_dir, schema_path=self.schema_path,
                onboarding_dir=self.onboarding_dir, catalog_dir=self.catalog_dir,
                community_id="community-n1-b1-extra", generation=generation, persona_key="persona_extra",
                gm_transport_factory=lambda *a, **k: gm,
                persona_driver_factory=lambda pk: driver,
            )
        self.assertEqual(outcome.status, "completed", outcome.reason)
        self.assertEqual(gm.calls, 1)
        records = _ledger_role_records(self.run_dir, "community_creation_gm")
        self.assertTrue(records, "mindestens ein community_creation_gm-Ledgereintrag erwartet.")
        for rec in records:
            self.assertFalse(rec["dollar_billed"], rec)

        # Resume/Reentry: ein zweiter Aufruf fuer dieselbe bereits
        # abgeschlossene Generation darf KEINEN weiteren GM-Request
        # ausloesen (02: "keine zweite Anfrage nach Empfang/unklarem
        # Ergebnis").
        gm2 = _GM(_v7_block("chrono-extra-should-not-be-used"), is_dollar_billed=False)
        with mock.patch.object(Path, "home", return_value=fake_home):
            outcome2 = advance_additional_persona_creation(
                run_dir=self.run_dir, states_dir=self.states_dir, schema_path=self.schema_path,
                onboarding_dir=self.onboarding_dir, catalog_dir=self.catalog_dir,
                community_id="community-n1-b1-extra", generation=generation, persona_key="persona_extra",
                gm_transport_factory=lambda *a, **k: gm2,
                persona_driver_factory=lambda pk: driver,
            )
        self.assertIn(outcome2.status, ("completed", "already_ready"), outcome2.reason)
        self.assertEqual(gm2.calls, 0, "Reentry auf eine bereits abgeschlossene Generation darf keinen neuen GM-Request senden.")


if __name__ == "__main__":
    unittest.main()
