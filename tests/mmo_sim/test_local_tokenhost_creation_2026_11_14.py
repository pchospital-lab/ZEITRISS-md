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
import json
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
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))


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
from mmo_sim.core.compat_load_service import build_compat_repair_fn  # noqa: E402
from mmo_sim.core.creation_service import ReplyResult, run_admitted_creation_dialog  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.core.admission import _atomic_write_json, _status_path  # noqa: E402
from mmo_sim.core import recovery_ops  # noqa: E402
from mmo_sim.core.save_correction import (  # noqa: E402
    ROLE_CREATION, load_record as load_correction_record,
    pursue_single_figure_correction, send_correction_turn,
)
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
from _recovery_ops_r1_fixtures import apply_p5_grant, make_p5_drift_hold, make_synthetic_run  # noqa: E402
from mmo_sim.lab.runner import request_stop  # noqa: E402


def _set_budget_exhausted(run_dir: Path, *, max_usd: float = 0.01) -> None:
    """O5-A.A3: wie `_recovery_ops_r2_fixtures.set_budget_exhausted` --
    dieselbe `lab.status.json`-Manipulation, hier lokal nachgebaut, um
    keine zusaetzliche Abhaengigkeit auf die (nicht in dieser Order-
    Allowlist stehende) r2-Fixturedatei zu ziehen."""
    path = _status_path(Path(run_dir))
    data = json.loads(path.read_text(encoding="utf-8"))
    data["max_usd"] = max_usd
    data["usd_spent"] = max_usd
    _atomic_write_json(path, data)

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


class _ClarifyingThenSaveGM:
    """O4-B.B2-Fix (evidence/INDEPENDENT-GENERAL-REVIEW.md Tabelle C):
    liefert im ERSTEN Turn eine echte Rueckfrage OHNE fertigen v7-Block --
    erst NACH einer tatsaechlichen Persona-Antwort (zweiter Turn) liefert
    der GM den fertigen Save. `driver.calls==0` mit direkter GM-
    Erstantwort (wie `_GM` oben) allein beweist die geforderte "mindestens
    einen tatsaechlich aufgerufenen Persona-Adapter"-Teilbedingung nicht."""

    def __init__(self, clarifying_text: str, final_v7_block: str, *, is_dollar_billed=True,
                 output_limit_tokens=4096, base_url=None):
        self.clarifying_text = clarifying_text
        self.final_v7_block = final_v7_block
        self.is_dollar_billed = is_dollar_billed
        self.output_limit_tokens = output_limit_tokens
        self.base_url = base_url
        self.calls = 0

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls += 1
        content = self.clarifying_text if self.calls == 1 else self.final_v7_block
        return {
            "content": content, "usage": {"prompt_tokens": 12, "completion_tokens": 8},
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
    einer strukturell validierbaren Zustimmung beantwortet. Fuer manche
    Faelle NIE tatsaechlich fuer eine Erschaffungsfrage aufgerufen (der GM
    liefert den fertigen Save bereits im ersten Turn) -- `.calls` bestaetigt
    das explizit; fuer den O4-B.B2-Gegenfall (echter GM-Rueckfrageturn) WIRD
    er aufgerufen, dann bestimmt `is_dollar_billed` (default `True`, wie der
    echte `getattr(persona_driver, 'is_dollar_billed', True)`-Fallback in
    `community_creation.py`) das Gate fuer DIESEN Persona-Request."""

    def __init__(self, persona_key: str, *, is_dollar_billed: bool = True):
        self.persona_key = persona_key
        self.is_dollar_billed = is_dollar_billed
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
        (`advance_one_persona_creation`), lokaler GM-Transport.

        O4-B.B2-Fix (evidence/INDEPENDENT-GENERAL-REVIEW.md Tabelle C): der
        GM stellt im ERSTEN Turn eine echte Rueckfrage (kein fertiger
        v7-Block) -- der Persona-Adapter (`_AcceptPersonaDriver`) muss
        dadurch tatsaechlich aufgerufen werden, BEVOR der zweite GM-Turn
        den fertigen Save liefert. Vorher lieferte der GM den Save bereits
        im ersten Turn und `driver.calls==0` wurde faelschlich als
        hinreichender Beleg behandelt."""
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

        gm = _ClarifyingThenSaveGM(
            "Magst du mir noch mehr ueber deine Figur erzaehlen, bevor wir abschliessen?",
            _v7_block("chrono-persona_first"), is_dollar_billed=False,
        )
        driver = _AcceptPersonaDriver("persona_first", is_dollar_billed=False)
        with mock.patch.object(Path, "home", return_value=fake_home):
            outcome = advance_one_persona_creation(
                run_dir=self.run_dir, states_dir=self.states_dir, schema_path=self.schema_path,
                onboarding_dir=self.onboarding_dir, catalog_dir=self.catalog_dir,
                community_id="community-n1-b1", generation=1, persona_key="persona_first",
                gm_transport_factory=lambda *a, **k: gm,
                persona_driver_factory=lambda pk: driver,
            )
        self.assertEqual(outcome.status, "completed", outcome.reason)
        self.assertEqual(gm.calls, 2, "Rueckfrage-Turn + Save-Turn -- genau zwei echte GM-Anfragen.")
        self.assertGreater(
            driver.calls, 0,
            "der Persona-Adapter muss fuer die GM-Rueckfrage tatsaechlich aufgerufen worden sein -- "
            "driver.calls==0 mit direkter GM-Erstantwort allein beweist das nicht.",
        )
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
        (`advance_additional_persona_creation`), lokaler GM-Transport.

        O4-B.B2-Fix (evidence/INDEPENDENT-GENERAL-REVIEW.md Tabelle C):
        wie beim Erstfigur-Gegenstueck oben -- der GM stellt im ersten Turn
        eine echte Rueckfrage, der Persona-Adapter muss tatsaechlich
        antworten, BEVOR der zweite Turn den fertigen Save liefert."""
        self._give_existing_figure("persona_extra", "chrono-extra-old", "ExtraOld")
        write_test_profile(self.run_dir, max_usd=0.0)
        fake_home = _write_fake_local_home(self.root)

        generation = len(catalog.list_for_participant(self.catalog_dir, "persona_extra")) + 1
        gm = _ClarifyingThenSaveGM(
            "Erzaehl mir noch etwas mehr ueber deine zweite Figur, bevor wir abschliessen?",
            _v7_block("chrono-extra-new"), is_dollar_billed=False,
        )
        driver = _AcceptPersonaDriver("persona_extra", is_dollar_billed=False)
        with mock.patch.object(Path, "home", return_value=fake_home):
            outcome = advance_additional_persona_creation(
                run_dir=self.run_dir, states_dir=self.states_dir, schema_path=self.schema_path,
                onboarding_dir=self.onboarding_dir, catalog_dir=self.catalog_dir,
                community_id="community-n1-b1-extra", generation=generation, persona_key="persona_extra",
                gm_transport_factory=lambda *a, **k: gm,
                persona_driver_factory=lambda pk: driver,
            )
        self.assertEqual(outcome.status, "completed", outcome.reason)
        self.assertEqual(gm.calls, 2, "Rueckfrage-Turn + Save-Turn -- genau zwei echte GM-Anfragen.")
        self.assertGreater(
            driver.calls, 0,
            "der Persona-Adapter muss fuer die GM-Rueckfrage tatsaechlich aufgerufen worden sein -- "
            "driver.calls==0 mit direkter GM-Erstantwort allein beweist das nicht.",
        )
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


class CorrectionAndCompatRepairDollarBillingTests(unittest.TestCase):
    """O5-A (02_NACHARBEIT.md Gruppe D): belegt die D-Fixes in
    `core.save_correction.send_correction_turn` und `core.compat_load_
    service.build_compat_repair_fn`/`_sl_backed_repair` -- VOR dem Fix
    gaben beide Funktionen `dollar_billed` nicht an `read_admission_block`/
    `request_ledger.begin` weiter, blieben also am Default `True` haengen,
    unabhaengig vom tatsaechlich uebergebenen GM-Transport. Ruft BEIDE neuen
    Sendefunktionen real auf (keine Scheinabnahme durch Helper-only-Tests)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        _, _, self.run_dir, _, _ = _new_env(self.root)

    def test_send_correction_turn_local_transport_sends_at_max_usd_zero_ledger_reflects_dollar_billed_false(self):
        write_test_profile(self.run_dir, max_usd=0.0)
        gm = _GM(_v7_block("chrono-correction-local"), is_dollar_billed=False)
        outcome = send_correction_turn(
            self.run_dir, role="save_correction", table_id=None, section_id=None,
            participant="human-correction", turn_idx=0,
            outgoing_text="Bitte korrigiere das Format.", gm_transport=gm,
        )
        self.assertFalse(outcome.blocked, outcome.reason)
        self.assertEqual(gm.calls, 1)
        records = _ledger_role_records(self.run_dir, "save_correction")
        self.assertTrue(records, "mindestens ein save_correction-Ledgereintrag erwartet.")
        for rec in records:
            self.assertFalse(rec["dollar_billed"], rec)

    def test_send_correction_turn_cloud_legacy_blocked_at_max_usd_zero_no_bypass(self):
        """Gegenfall: ein Transport OHNE `is_dollar_billed`-Attribut (alt/
        Cloud) muss am Default `dollar_billed=True` haengen -- `max_usd=0.0`
        blockiert VOR jedem physischen Versand, kein automatischer Bypass."""
        write_test_profile(self.run_dir, max_usd=0.0)
        gm = _LegacyGM(_v7_block("chrono-correction-cloud"))
        outcome = send_correction_turn(
            self.run_dir, role="save_correction", table_id=None, section_id=None,
            participant="human-correction-cloud", turn_idx=0,
            outgoing_text="Bitte korrigiere das Format.", gm_transport=gm,
        )
        self.assertTrue(outcome.blocked)
        self.assertTrue((outcome.reason or "").startswith("admission_blocked:"), outcome.reason)
        self.assertEqual(gm.calls, 0, "kein einziger echter Transportversuch -- das Gate stoppt VOR dem Versand.")

    def test_compat_repair_fn_local_transport_sends_at_max_usd_zero_ledger_reflects_dollar_billed_false(self):
        write_test_profile(self.run_dir, max_usd=0.0)
        gm = _GM(_v7_block("chrono-compat-local"), is_dollar_billed=False)
        repair = build_compat_repair_fn(
            self.run_dir, repair_key="compat-local-test", char_id="chrono-compat-local",
            participant_id="human-compat", gm_transport=gm,
        )
        # Kein "economy"-Schluessel -- die lokale, kostenlose Wallet-Projektion
        # findet nichts zu aendern (`changed=False`) und faellt echt auf den
        # SL-Request-Pfad durch, statt den Produktpfad zu umgehen.
        result = repair({"foo": "bar"}, ["required: foo"])
        self.assertIsNotNone(result, "SL-gestuetzte Reparatur haette trotz max_usd=0.0 real senden muessen.")
        self.assertEqual(gm.calls, 1)
        records = _ledger_role_records(self.run_dir, "save_compat_load_repair")
        self.assertTrue(records, "mindestens ein save_compat_load_repair-Ledgereintrag erwartet.")
        for rec in records:
            self.assertFalse(rec["dollar_billed"], rec)

    def test_compat_repair_fn_cloud_legacy_blocked_at_max_usd_zero_no_bypass(self):
        write_test_profile(self.run_dir, max_usd=0.0)
        gm = _LegacyGM(_v7_block("chrono-compat-cloud"))
        repair = build_compat_repair_fn(
            self.run_dir, repair_key="compat-cloud-test", char_id="chrono-compat-cloud",
            participant_id="human-compat-cloud", gm_transport=gm,
        )
        result = repair({"foo": "bar"}, ["required: foo"])
        self.assertIsNone(result, "blockierter Versuch liefert None (kontrolliertes HOLD oben), kein Bypass.")
        self.assertEqual(gm.calls, 0, "kein einziger echter Transportversuch -- das Gate stoppt VOR dem Versand.")

    def test_send_correction_turn_unclear_sent_in_flight_holds_no_retry_local_transport(self):
        """O5-C.C1 (RELEASE-CASES.json): "offener/unklarer GM-Request bei
        ... Correction/Compat bleibt HOLD, physischer Requestcounter
        unveraendert beim Resume" -- derselbe Mechanismus wie
        `test_w48_save_correction_2026_10_07.py::test_sc10_unclear_sent_in_
        flight_never_retried_or_renumbered` (Crash zwischen `begin()`
        [state=sent] und Antwort/Fehlerabschluss), hier erstmals mit einem
        ECHTEN lokalen (`is_dollar_billed=False`) Transport: der zweite
        Aufruf fuer DIESELBE Operationsidentitaet trifft `request_ledger.
        begin()`s `OpenReservationExistsError` -- kein Retry, kein neuer
        Requestdatensatz, der unklare Datensatz bleibt bytegleich."""
        write_test_profile(self.run_dir, max_usd=0.0)
        request_id = request_ledger.begin(
            self.run_dir, role=ROLE_CREATION, content="Korrektur bitte.", reserved_usd=0.001,
            turn_idx=1, participant="local-sc10", dollar_billed=False,
        )
        before = request_ledger.load_request(self.run_dir, request_id)
        self.assertEqual(before["state"], "sent")

        class _ExplodingLocalGm:
            is_dollar_billed = False

            def turn(self, *a, **k):
                raise AssertionError("unklarer sent-Zustand darf NIE einen neuen Versand ausloesen.")

        outcome = send_correction_turn(
            self.run_dir, role=ROLE_CREATION, table_id=None, section_id=None,
            participant="local-sc10", turn_idx=1, outgoing_text="Korrektur bitte.",
            gm_transport=_ExplodingLocalGm(),
        )
        self.assertTrue(outcome.blocked)
        self.assertTrue((outcome.reason or "").startswith("unclear_sent_in_flight"), outcome.reason)
        after = request_ledger.load_request(self.run_dir, request_id)
        self.assertEqual(after, before, "der unklare Requestdatensatz bleibt bytegleich -- kein Ueberschreiben.")
        self.assertEqual(
            len(request_ledger._all_records(self.run_dir)), 1,
            "physischer Requestcounter unveraendert beim Resume -- kein zweiter Datensatz.",
        )

    def test_compat_repair_fn_unclear_sent_in_flight_holds_no_retry_local_transport(self):
        """O5-C.C1-Nachzug: derselbe unklare-sent-Zustand, jetzt fuer den
        Kompatibilitaets-Reparaturweg (`compat_load_service._sl_backed_
        repair` implementiert dieselbe `request_ledger.begin`/
        `OpenReservationExistsError`-Kette direkt, ohne `send_correction_
        turn` zu teilen) -- lokaler Transport, kein Retry, kein zweiter
        Datensatz."""
        write_test_profile(self.run_dir, max_usd=0.0)
        from mmo_sim.core.compat_load_service import ROLE_COMPAT_LOAD
        request_id = request_ledger.begin(
            self.run_dir, role=ROLE_COMPAT_LOAD, content="Korrektur bitte.", reserved_usd=0.001,
            turn_idx=1, participant="local-compat-sc10", dollar_billed=False,
        )
        before = request_ledger.load_request(self.run_dir, request_id)
        self.assertEqual(before["state"], "sent")

        class _ExplodingLocalGm:
            is_dollar_billed = False

            def turn(self, *a, **k):
                raise AssertionError("unklarer sent-Zustand darf NIE einen neuen Compat-Versand ausloesen.")

        repair = build_compat_repair_fn(
            self.run_dir, repair_key="compat-local-sc10", char_id="chrono-compat-sc10",
            participant_id="local-compat-sc10", gm_transport=_ExplodingLocalGm(),
        )
        result = repair({"foo": "bar"}, ["required: foo"])
        self.assertIsNone(result, "unklarer sent-Zustand liefert None (kontrolliertes HOLD), kein Bypass.")
        after = request_ledger.load_request(self.run_dir, request_id)
        self.assertEqual(after, before)
        self.assertEqual(len(request_ledger._all_records(self.run_dir)), 1)

    def test_send_correction_turn_durable_result_reused_after_crash_before_checkpoint_local_transport(self):
        """O5-C.C2 (RELEASE-CASES.json): "erhaltenes dauerhaftes Ergebnis
        vor Settlement/Publikation wird wiederverwendet; kein zweiter
        Send" -- derselbe Mechanismus wie `test_sc09_durable_result_
        reused_after_crash_before_checkpoint`, hier mit einem ECHTEN
        lokalen Transport: nach einer bereits durabel empfangenen Antwort
        (Crash NACH Antwort, VOR Checkpoint) liefert ein zweiter Aufruf fuer
        DIESELBE Operationsidentitaet dasselbe Ergebnis wieder, OHNE den
        Transport nochmal real anzusprechen."""
        write_test_profile(self.run_dir, max_usd=0.0)
        gm = _GM(_v7_block("chrono-correction-sc09-local"), is_dollar_billed=False)
        first = send_correction_turn(
            self.run_dir, role=ROLE_CREATION, table_id=None, section_id=None,
            participant="local-sc09", turn_idx=1, outgoing_text="Korrektur bitte.", gm_transport=gm,
        )
        self.assertFalse(first.blocked)
        self.assertEqual(gm.calls, 1)

        class _ExplodingLocalGm:
            is_dollar_billed = False

            def turn(self, *a, **k):
                raise AssertionError("bereits durabel empfangenes Ergebnis darf NIE einen zweiten Send ausloesen.")

        second = send_correction_turn(
            self.run_dir, role=ROLE_CREATION, table_id=None, section_id=None,
            participant="local-sc09", turn_idx=1, outgoing_text="Korrektur bitte.",
            gm_transport=_ExplodingLocalGm(),
        )
        self.assertFalse(second.blocked)
        self.assertEqual(second.text, first.text)
        self.assertEqual(second.request_id, first.request_id)
        self.assertEqual(
            len(request_ledger._all_records(self.run_dir)), 1,
            "die Wiederverwendung erzeugt KEINEN zweiten Requestdatensatz.",
        )

    def test_compat_repair_fn_durable_result_reused_after_crash_before_checkpoint_local_transport(self):
        """O5-C.C2-Nachzug: derselbe Wiederverwendungsmechanismus fuer den
        Kompatibilitaets-Reparaturweg, lokaler Transport."""
        write_test_profile(self.run_dir, max_usd=0.0)
        gm = _GM(_v7_block("chrono-compat-sc09-local"), is_dollar_billed=False)
        repair_key = "compat-local-sc09"
        repair = build_compat_repair_fn(
            self.run_dir, repair_key=repair_key, char_id="chrono-compat-sc09-local",
            participant_id="local-compat-sc09", gm_transport=gm,
        )
        first = repair({"foo": "bar"}, ["required: foo"])
        self.assertIsNotNone(first)
        self.assertEqual(gm.calls, 1)

        class _ExplodingLocalGm:
            is_dollar_billed = False

            def turn(self, *a, **k):
                raise AssertionError("bereits durabel empfangenes Compat-Ergebnis darf NIE einen zweiten Send ausloesen.")

        repair_again = build_compat_repair_fn(
            self.run_dir, repair_key=repair_key, char_id="chrono-compat-sc09-local",
            participant_id="local-compat-sc09", gm_transport=_ExplodingLocalGm(),
        )
        second = repair_again({"foo": "bar"}, ["required: foo"])
        self.assertIsNotNone(second, "die durabel empfangene Antwort muss wiederverwendet werden, nicht None liefern.")
        self.assertEqual(
            len(request_ledger._all_records(self.run_dir)), 1,
            "die Wiederverwendung erzeugt KEINEN zweiten Requestdatensatz.",
        )


class P5GrantVorabgateLocalDollarBillingTests(unittest.TestCase):
    """O5-A.A3 (RELEASE-CASES.json): das P5-Grant-Vorabgate in
    `save_correction.pursue_single_figure_correction` (save_correction.py
    ~1005-1064, "P5-Marker"-Fix) -- EIN terminaler Drift-Hold erhält vom
    Betreiber eine `recovery_ops.apply_p5`-Einmalautorisierung; der
    anschliessende Vorabgate-Check (`read_admission_block`, VOR jedem
    Grant-/`attempts_used`-Verbrauch) muss denselben `gm_transport.
    is_dollar_billed`-Marker lesen wie jeder reguläre Korrektur-Versand
    ("Markerweitergabe korrigieren" -- vorher hing dieser EINE Vorabgate-
    Aufruf fest am Cloud-Default `dollar_billed=True`, unabhängig vom
    tatsächlich übergebenen lokalen Transport). Stop/Deadline/Requestcap
    bleiben davon UNABHÄNGIG wirksam -- blockieren sie, bleibt der P5-Grant
    UNVERBRAUCHT (`consumed` unverändert, `attempts_used` unverändert)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.run_dir = make_synthetic_run(self.root)

    def _grant(self, repair_key: str) -> dict:
        return json.loads(recovery_ops._p5_grant_path(self.run_dir, repair_key).read_text(encoding="utf-8"))

    def test_local_dollar_billed_false_bypasses_exhausted_cloud_budget_consumes_grant_and_accepts(self):
        p5 = make_p5_drift_hold(self.run_dir, persona_key="local-p5", char_id="chrono-local-p5")
        apply_p5_grant(self.run_dir, p5["repair_key"])
        grant_before = self._grant(p5["repair_key"])
        self.assertFalse(grant_before["consumed"], "Grant muss vor dem Versuch unverbraucht sein.")

        # Ein BEKANNT ERSCHOEPFTES Cloud-Budget (max_usd=usd_spent=0.0) --
        # ein regulaerer Cloud-Transport (Default dollar_billed=True) wuerde
        # hier am Dollargate blockieren (s. naechster Test). Der tatsaechlich
        # uebergebene LOKALE Transport (is_dollar_billed=False) darf das
        # Vorabgate trotzdem passieren.
        _set_budget_exhausted(self.run_dir, max_usd=0.0)
        valid_block_text = "```json\n" + json.dumps(p5["valid_save"]) + "\n```"
        gm = _GM(valid_block_text, is_dollar_billed=False, output_limit_tokens=512)

        outcome = pursue_single_figure_correction(
            run_dir=self.run_dir, participant_id=p5["persona_key"], expected_chrononaut_id=p5["char_id"],
            candidate_block=p5["invalid_candidate"], gm_transport=gm, role=ROLE_CREATION,
        )
        self.assertEqual(outcome.status, "accepted", outcome)
        self.assertEqual(gm.calls, 1, "genau EIN echter P5-Zusatzversand, kein Doppelsend.")

        grant_after = self._grant(p5["repair_key"])
        self.assertTrue(grant_after["consumed"], "Grant muss nach erfolgreichem Vorabgate+Versand verbraucht sein.")

        records = _ledger_role_records(self.run_dir, ROLE_CREATION)
        self.assertTrue(records, "mindestens ein save_correction-Ledgereintrag fuer den P5-Zusatzversand erwartet.")
        self.assertTrue(
            any(not rec["dollar_billed"] for rec in records),
            "der P5-Zusatzversand selbst muss den lokalen Marker (dollar_billed=False) tragen.",
        )

    def test_cloud_legacy_transport_blocked_by_same_exhausted_budget_grant_not_consumed(self):
        """Gegenprobe (belegt, dass der obige Fix real greift, nicht nur
        zufaellig durchlaeuft): DERSELBE erschoepfte Cloud-Budgetzustand,
        aber ein Transport OHNE `is_dollar_billed`-Attribut (alt/Cloud,
        Default `True`) -- muss am Vorabgate blockieren, VOR jedem
        Grant-/`attempts_used`-Verbrauch."""
        p5 = make_p5_drift_hold(self.run_dir, persona_key="cloud-p5", char_id="chrono-cloud-p5")
        apply_p5_grant(self.run_dir, p5["repair_key"])
        grant_before = self._grant(p5["repair_key"])
        record_before = load_correction_record(self.run_dir, p5["repair_key"])

        _set_budget_exhausted(self.run_dir, max_usd=0.0)
        gm = _LegacyGM("unused -- darf nie gesendet werden")

        outcome = pursue_single_figure_correction(
            run_dir=self.run_dir, participant_id=p5["persona_key"], expected_chrononaut_id=p5["char_id"],
            candidate_block=p5["invalid_candidate"], gm_transport=gm, role=ROLE_CREATION,
        )
        self.assertEqual(outcome.status, "hold")
        self.assertTrue((outcome.reason or "").startswith("gate_blocked_before_consume:"), outcome.reason)
        self.assertEqual(gm.calls, 0, "kein physischer Versand -- das Vorabgate stoppt VOR dem Grant-Verbrauch.")

        grant_after = self._grant(p5["repair_key"])
        record_after = load_correction_record(self.run_dir, p5["repair_key"])
        self.assertEqual(grant_after, grant_before, "Grant darf sich bei Block NICHT veraendern (unverbrauchter Grant).")
        self.assertEqual(
            record_after["attempts_used"], record_before["attempts_used"],
            "attempts_used darf sich bei Block NICHT veraendern.",
        )

    def test_stop_requested_blocks_local_dollar_billed_transport_grant_unconsumed(self):
        """Stop/Deadline/Requestcap bleiben UNABHAENGIG vom lokalen
        dollar_billed-Marker wirksam: ein bereits gesetzter Stop blockiert
        den P5-Grant-Verbrauch GENAUSO fuer einen lokalen (dollar_billed=
        False) Transport -- der Grant bleibt unverbraucht erhalten."""
        p5 = make_p5_drift_hold(self.run_dir, persona_key="stop-p5", char_id="chrono-stop-p5")
        apply_p5_grant(self.run_dir, p5["repair_key"])
        grant_before = self._grant(p5["repair_key"])
        record_before = load_correction_record(self.run_dir, p5["repair_key"])

        request_stop(self.run_dir, "synthetic O5-A.A3 review stop")
        gm = _GM("unused -- darf nie gesendet werden", is_dollar_billed=False)

        outcome = pursue_single_figure_correction(
            run_dir=self.run_dir, participant_id=p5["persona_key"], expected_chrononaut_id=p5["char_id"],
            candidate_block=p5["invalid_candidate"], gm_transport=gm, role=ROLE_CREATION,
        )
        self.assertEqual(outcome.status, "hold")
        self.assertTrue((outcome.reason or "").startswith("gate_blocked_before_consume:"), outcome.reason)
        self.assertEqual(gm.calls, 0, "Stop blockiert VOR jedem physischen Versand, auch lokal/dollar-exempt.")

        grant_after = self._grant(p5["repair_key"])
        record_after = load_correction_record(self.run_dir, p5["repair_key"])
        self.assertEqual(grant_after, grant_before, "Grant darf sich bei Stop-Block NICHT veraendern.")
        self.assertEqual(record_after["attempts_used"], record_before["attempts_used"])


class _TwoTurnGM:
    """GM-Double mit EINEM echten Dialogschritt vor dem Save: Turn 1 liefert
    eine Rueckfrage (KEIN Save), Turn 2 (nach der Menschenantwort) liefert
    den fertigen v7-Block. Belegt O4-B.B1s "mindestens einen menschlichen
    Dialogschritt vor gueltigem Save" -- `_GM` oben schliesst immer schon im
    ERSTEN Turn ab."""

    def __init__(self, question_text: str, save_block_text: str, *, is_dollar_billed=False):
        self.question_text = question_text
        self.save_block_text = save_block_text
        self.is_dollar_billed = is_dollar_billed
        self.output_limit_tokens = 4096
        self.calls: list[tuple[int, str]] = []

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append((idx, text))
        content = self.question_text if len(self.calls) == 1 else self.save_block_text
        return {
            "content": content, "usage": {"prompt_tokens": 10, "completion_tokens": 5},
            "sources": [], "latency_s": 0.01, "chat_id": "o4b1-tui-dispatch",
        }


class TuiSessionRealDispatchCreationTests(unittest.TestCase):
    """O4-B.B1 (RELEASE-CASES.json): echte `TuiSession` mit synthetischen
    Pfaden/input_fn/print_fn; `_cmd_new_or_switch_character` REAL
    dispatchen (nicht `run_admitted_creation_dialog` direkt aufrufen, wie
    die Klasse `HumanEquivalentCreationDollarBillingTests` oben es -- laut
    eigenem Docstring bewusst eingestanden -- tut), mit mindestens einem
    menschlichen Dialogschritt VOR dem gueltigen Save. Pass-1-Gap, hier
    geschlossen (live gegen den echten `ui/tui.py`-Code verifiziert, nicht
    aus Gedaechtnis angenommen):
      - Fuer einen frischen Teilnehmer OHNE bestehende Figur beginnt
        `_cmd_new_or_switch_character` den Erschaffungsdialog SOFORT (kein
        separates "neu"/Umschaltwahl-Prompt -- das gibt es nur, wenn
        bereits eine aktive Figur existiert, s. `test_r2_r6_fresh_start_
        durable_identity_2026_10_02.py`).
      - Das routenneutrale P5-Vorabgate (`_tui_early_gate_dollar_billed`,
        `mmo_sim/ui/tui.py` Zeile ~57) liest `setup.resolve_model_provider()`
        OHNE expliziten `env_path` -- braucht also ein ECHTES persistiertes
        lokales Profil unter `Path.home()/.openwebui_env` (nicht nur ein
        `gm_transport.is_dollar_billed`-Attribut), sonst haelt der Dialog
        schon vor dem ersten GM-Call am Dollargate (`max_usd=0.0`)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.schema_path, self.states_dir, self.run_dir, self.onboarding_dir, self.catalog_dir = _new_env(self.root)

    def test_tui_session_real_dispatch_new_character_one_human_dialog_step_before_save(self):
        from mmo_sim.ui.tui import TuiSession

        write_test_profile(self.run_dir, max_usd=0.0)
        fake_home = _write_fake_local_home(self.root)
        gm = _TwoTurnGM(
            "Wie soll deine Figur heissen und woher kommt sie?",
            _v7_block("chrono-o4b1-tui", "O4B1Tui"),
            is_dollar_billed=False,
        )
        printed: list[str] = []
        with mock.patch.object(Path, "home", return_value=fake_home):
            session = TuiSession(
                self.onboarding_dir, self.catalog_dir, "human_o4b1",
                input_fn=self._scripted_input([
                    "Meine Figur heisst Nova und kommt aus dem Jahr 2142.",  # ECHTER menschlicher Dialogschritt
                ]),
                print_fn=printed.append,
                run_dir=self.run_dir, states_dir=self.states_dir, schema_path=self.schema_path,
                gm_transport_factory=lambda *_a, **_k: gm,
            )
            session._cmd_new_or_switch_character()

        self.assertEqual(len(gm.calls), 2, "GENAU zwei reale GM-Turns: Rueckfrage, dann Save nach Menschenantwort.")
        self.assertEqual(gm.calls[0][0], 0, "erster Turn ist der automatische Anker (turn_idx 0).")
        self.assertEqual(
            gm.calls[1][1], "Meine Figur heisst Nova und kommt aus dem Jahr 2142.",
            "der zweite GM-Turn muss die ECHTE Menschenantwort als Text tragen (kein Auto-Advance).",
        )
        self.assertEqual(
            catalog.active_chrononaut_id(self.catalog_dir, "human_o4b1"), "chrono-o4b1-tui",
            "die ueber den echten TuiSession-Dispatch erschaffene Figur muss aktiv/gespeichert sein.",
        )
        records = _ledger_role_records(self.run_dir, "creation_dialog")
        self.assertEqual(len(records), 2, "beide reale Turns (Anker+Menschenantwort) erzeugen je einen Ledgereintrag.")
        for rec in records:
            self.assertFalse(rec["dollar_billed"], rec)
        self.assertFalse(
            any("Traceback" in p for p in printed), "kein ungefangener Rohfehler im Spielertext.",
        )

    @staticmethod
    def _scripted_input(lines):
        it = iter(lines)

        def _fn(prompt: str = "") -> str:
            try:
                return next(it)
            except StopIteration:
                raise EOFError()
        return _fn


if __name__ == "__main__":
    unittest.main()
