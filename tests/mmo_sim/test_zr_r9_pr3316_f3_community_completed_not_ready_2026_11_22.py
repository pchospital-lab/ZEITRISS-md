#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_r9_pr3316_f3_community_completed_not_ready_2026_11_22.py —
ZR-R9-PR3316-PREMERGE-NACHZUG-20261122, Befund F3 (COMMUNITY-REVIEW.md
§B1, 01_REVIEW.txt Abschnitt 4): `ui/tui.py:_cmd_community` klassifiziert
jeden `onboarding.peek(...).status == "completed"` sofort als
`Fertig/tischbereit`, entfernt ihn aus `open_` und kehrt bei leerem `open_`
zurück. Der bestehende Domainvertrag (`community_creation.py:
_publication_reconcile`) verlangt dagegen zusätzlich Current, Katalog-
eintrag, Figurablage, Persona-State-Identität und aktive Bindung --
`onboarding.complete_with_save` setzt den Status bereits VOR diesen
Publikationswirkungen. Ein Absturz/Schreibfehler GENAU dazwischen (einer
der fünf Publikationsnähte) ist ein vorgesehener Recoveryfall -- VOR
diesem PR durchlief die Community-Ansicht solche Fälle kostenfrei über
`_publication_reconcile`; nach diesem PR werden sie faelschlich als
tischbereit aussortiert und sind über die Menü-Auswahl nicht mehr
erreichbar (belegt durch `repro_completed_publication.py`).

Nachzug: `community_creation.py:peek_publication_readiness` (additive
reine Lese-Funktion, identische Prüfung wie `_publication_reconcile`,
0 Requests, 0 Writes) + `ui/tui.py:_cmd_community` klassifiziert
`completed` nur dann als `Fertig/tischbereit`, wenn dieser Peek
`"already_ready"` liefert -- sonst bleibt die Persona ehrlich `offen` und
eine bewusste Auswahl erreicht den vorhandenen kostenfreien
`_publication_reconcile`.

Echter Caller: `mmo_sim.ui.tui.TuiSession._cmd_community()` end-to-end,
identisches Testmuster/Helfer zu `test_p2_community_creation.py`s
`test_cmd_community_view_and_back_zero_inference_with_finished_and_drafts_c3`
(kein isolierter Nachbau der Klassifikationslogik).

Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_block_text, full_v7_save  # noqa: E402

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


class _GM:
    def __init__(self, scripted_replies: list[str]):
        self.scripted = list(scripted_replies)
        self.calls: list[str] = []

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append(text)
        content = self.scripted.pop(0) if self.scripted else "Die Erschaffung laeuft weiter."
        return {
            "content": content, "usage": {"prompt_tokens": 5, "completion_tokens": 5},
            "sources": [], "latency_s": 0.0, "chat_id": "creation",
        }


class _ExplodingGM:
    """Beleg fuer 0 Inferenz bei Ansicht/Zurueck UND bei der kostenfreien
    Publikations-Nachholung (Reconcile braucht KEINEN GM-Call)."""

    def turn(self, *a, **kw):
        raise AssertionError("kein GM-Call erwartet -- weder Ansicht/Zurueck noch Reconcile brauchen Inferenz.")


class _FakePersonaDriver:
    def __init__(self, persona_key: str, answers: list[str]):
        self.persona_key = persona_key
        self.config = None
        self.answers = list(answers)
        self.calls: list[dict] = []

    def decide(self, context: dict) -> ParticipantDecision:
        self.calls.append(context)
        if not self.answers:
            raise RuntimeError(f"_FakePersonaDriver[{self.persona_key}]: keine weiteren Antworten gescriptet.")
        text = self.answers.pop(0)
        return ParticipantDecision(
            text=text, origin_source="fake:community_creation",
            meta={"usage": {"prompt_tokens": 3, "completion_tokens": 3}},
        )


def _v7_block(char_id: str, name: str = "Nova") -> str:
    return full_v7_block_text(char_id, name=name)


def _scripted_then_eof_input(*answers: str):
    queue = list(answers)

    def _input(prompt: str = "") -> str:
        if queue:
            return queue.pop(0)
        raise EOFError()

    return _input


def _new_env(root: Path):
    schema_path = _SCHEMA
    states_dir = root / "states"
    run_dir = root / "run"
    onboarding_dir = root / "onboarding"
    catalog_dir = root / "catalog"
    states_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    return schema_path, states_dir, run_dir, onboarding_dir, catalog_dir


def test_f3_completed_but_unpublished_persona_stays_open_not_falsely_tischbereit():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _new_env(root)
        write_test_profile(run_dir)
        printed: list[str] = []

        exploding_gm = _ExplodingGM()
        # Echte, vom Pool generierte Keys -- erst NACH der TuiSession-Anlage
        # bekannt (s.u.), darum vergleichen die Factories gegen dieses
        # gemeinsame, von aussen befuellte Set statt gegen ein Literal.
        no_inference_keys: set[str] = set()

        def gm_factory(chat_id: str):
            pk = chat_id.split("onboarding-", 1)[1]
            if pk in no_inference_keys:
                return exploding_gm
            return _GM([_v7_block(f"chrono-{pk}", pk)])

        def persona_factory(pk: str):
            if pk in no_inference_keys:
                return _FakePersonaDriver(pk, [])  # darf nie befragt werden.
            return _FakePersonaDriver(pk, ["Bereit."])

        session = TuiSession(
            onboarding_dir, catalog_dir, "human_f3_caller",
            input_fn=_scripted_then_eof_input(),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=gm_factory, persona_driver_factory=persona_factory,
        )
        planned_keys = list(session._synthetic_starter_pool("community-human_f3_caller", size=8).keys())
        assert len(planned_keys) == 8
        finished_pk, stuck_pk = planned_keys[0], planned_keys[1]
        no_inference_keys.add(stuck_pk)

        # finished_pk: regulaerer Weg -- echte mehrstufige Erschaffung bis
        # Save, danach VOLLSTAENDIG publiziert (Baseline, wie C3-Test).
        session._input = _scripted_then_eof_input("d", finished_pk)
        session._cmd_community()

        ps_store = PersonaStateStore(schema_path=schema_path)
        assert core_store.load_current_save_or_raise(run_dir, finished_pk, ps_store, states_dir=states_dir) is not None

        # stuck_pk: GENAU der belegte Crash-/Recoveryfall -- `onboarding.
        # complete_with_save` (dieselbe reale Produktfunktion wie
        # `core/creation_service.py`) setzt status=completed + final_save,
        # OHNE dass `_publication_reconcile` je lief (kein Current, kein
        # Katalogeintrag, keine Figurablage, keine Persona-State-Identitaet,
        # keine aktive Bindung) -- exakt das Fenster aus COMMUNITY-REVIEW.md
        # §B1.
        onboarding.start_or_resume(onboarding_dir, stuck_pk)
        stuck_block = full_v7_save(f"chrono-{stuck_pk}", name="Stuck")
        onboarding.complete_with_save(
            onboarding_dir, stuck_pk, stuck_block, ZeitrissHarvestValidator(), f"chrono-{stuck_pk}",
        )
        prior = onboarding.peek(onboarding_dir, stuck_pk)
        assert prior is not None and prior.status == "completed" and prior.final_save == stuck_block
        assert core_store.load_current_save_or_raise(run_dir, stuck_pk, ps_store, states_dir=states_dir) is None, (
            "Vorbedingung: stuck_pk hat trotz completed-Onboarding NOCH KEINEN Current."
        )

        # Reine Ansicht/Zurueck -- MUSS 0 Requests ausloesen UND stuck_pk
        # ehrlich als 'offen' zeigen (NICHT als tischbereit aussortieren).
        requests_before = list((run_dir / "requests").glob("*.json")) if (run_dir / "requests").is_dir() else []
        printed.clear()
        session._input = _scripted_then_eof_input("/zurueck")
        session._cmd_community()
        requests_after = list((run_dir / "requests").glob("*.json")) if (run_dir / "requests").is_dir() else []
        assert len(requests_after) == len(requests_before), "Ansicht/Zurueck darf KEINEN neuen Request ausloesen."

        finished_line = next(line for line in printed if "Fertig/tischbereit" in line)
        open_line = next(line for line in printed if "Noch offen/wartend" in line)
        assert finished_pk in finished_line, finished_line
        assert stuck_pk not in finished_line, (
            f"F3-Regression: completed-aber-unpubliziert wird faelschlich als tischbereit gezeigt -- {finished_line}"
        )
        assert stuck_pk in open_line, (
            f"stuck_pk muss ehrlich als fortsetzbar/offen sichtbar bleiben -- {open_line}"
        )

        # stuck_pk's Onboarding-Datensatz bleibt durch die reine Ansicht
        # bytegleich -- kein stiller Schreibzugriff fuer Anzeigezwecke.
        after_view = onboarding.peek(onboarding_dir, stuck_pk)
        assert after_view.status == "completed" and after_view.final_save == stuck_block

        # Bewusste Auswahl von stuck_pk -- erreicht den bestehenden
        # KOSTENFREIEN `_publication_reconcile` (0 GM-Calls, `_ExplodingGM`
        # wuerde sonst werfen), publiziert jetzt ALLE fuenf Naehte nach.
        printed.clear()
        session._input = _scripted_then_eof_input(stuck_pk)
        session._cmd_community()

        published_stuck = core_store.load_current_save_or_raise(run_dir, stuck_pk, ps_store, states_dir=states_dir)
        assert published_stuck == stuck_block, (
            "die bewusste Auswahl muss den bereits vorliegenden final_save kostenfrei publizieren."
        )
        # `_ExplodingGM.turn()` wirft bei JEDEM Aufruf -- das Erreichen
        # dieser Zeile ohne Exception ist bereits der Beleg fuer 0 GM-Calls.


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
