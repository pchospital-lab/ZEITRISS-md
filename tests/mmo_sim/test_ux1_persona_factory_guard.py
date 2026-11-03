#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_persona_factory_guard.py — UX18 (ZEITRISS Terminal
UX-1, OFFENE_BEDIENBEFUNDE.md Punkt 8, General-Befund G04).

Vorher stand `self.persona_driver_factory(guest_id)` (Gast-Einladungsweg)
UND `self.persona_driver_factory(leader_persona_id)` (KI-Leader-Weg) VOR dem
schuetzenden `try`-Block -- eine fehlende Konfiguration konnte dort als
unerwarteter Python-Traceback durchschlagen statt der sonst beobachtbaren
ruhigen Textzeile. Dieser Test beweist: beide Wege liefern jetzt eine
ehrliche Textzeile, KEIN Traceback, KEIN stiller Fallback/Folgecall -- und
beim Gastweg bleibt der Tisch mit den uebrigen Teilnehmern nutzbar.

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs."""
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

from _full_v7_fixture import full_v7_save, upgrade_narrow_save  # noqa: E402

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
_FIXTURE_SAVE = upgrade_narrow_save(json.loads(
    (_REPO_ROOT / "internal" / "qa" / "harness" / "lobby" / "fixtures" / "saves" / "sniper.json").read_text(encoding="utf-8")
))


def _synthetic_save(char_id: str, name: str) -> dict:
    return full_v7_save(char_id, name=name, save_id=f"fixture-{char_id.lower()}-initial-001")


def _bootstrap_own_persona(run_dir: Path, states_dir: Path, host_id: str, persona_key: str) -> None:
    """R4-Nachzug (F3-Rest, Generalklaerung): `_cmd_local_round`s freier
    Alias-Pfad (`persona:`/`lead:persona:`) treibt eine normale KI-Persona
    nur noch aus dem EIGENEN bestaetigten Bestand des einladenden Hosts
    (`self._known_ai_overview()`, `community-<host_id>`) -- `_make_ready`
    unten (reine Figur-/Save-Registrierung) begruendet KEINE Zugehoerigkeit.
    MUSS VOR `_make_ready` fuer dieselbe `persona_key` laufen (umgekehrte
    Reihenfolge ueberschreibt den gleich danach publizierten Spielstand
    wieder mit dem Bootstrap-Entwurf). Dieser Test PRUEFT ausdruecklich den
    kaputten-Factory-Pfad (UX18) -- die Persona muss den Bestandscheck
    unbeschadet passieren, damit ueberhaupt `persona_driver_factory`
    (hier: `_broken_persona_factory`) erreicht wird. Identisches Muster zu
    `test_r3_f3_host_persona_authority.py:_bootstrap_own_persona`."""
    from mmo_sim.domain.zeitriss.community_bootstrap import bootstrap_community
    ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
    community_dir = run_dir / "community"
    drafts = {
        persona_key: {
            "real_name": persona_key, "archetype": "Test-Archetyp", "play_style": "SIMULIERT/DEMO",
            "charwunsch": "SIMULIERT/DEMO (UX18-Testfixture).",
            "plays_char": {
                "save_file": "NOCH_NICHT_ERSCHAFFEN", "character_id": "NOCH_NICHT_ERSCHAFFEN",
                "name": "NOCH_NICHT_ERSCHAFFEN", "callsign": "NOCH_NICHT_ERSCHAFFEN",
            },
        },
    }
    result = bootstrap_community(community_dir, f"community-{host_id}", 1, drafts, ps_store, states_dir, today="2026-11-03")
    assert persona_key in result.personas_written, result.reason


def _make_ready(onboarding_dir: Path, states_dir: Path, run_dir: Path, persona_key: str) -> None:
    """Dieselbe Produktwegfolge wie `_a24_local_support.make_ready`
    (`onboarding` + `core.store.publish_current_save`), hier mit einem
    synthetischen (statt Fixture-datei-gebundenen) Save -- die Persona
    braucht eine ECHTE abgeschlossene Figur, damit der Testlauf ueberhaupt
    bis zum Factory-Aufruf vordringt (derselbe Kontrollfluss wie im Produkt:
    erst Figur aufloesen, DANACH den Treiber bauen)."""
    save = _synthetic_save(f"CHR-{persona_key.upper()}", persona_key)
    chrono_id = save["characters"][0]["id"]
    ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
    onboarding.start_or_resume(onboarding_dir, persona_key)
    onboarding.complete_with_save(onboarding_dir, persona_key, save, ZeitrissHarvestValidator(), chrono_id)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, persona_key, chrono_id, save)
    core_store.publish_current_save(run_dir, persona_key, save, ps_store, states_dir)


def _scripted_input(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


class _FakeCreationGm:
    def __init__(self):
        self.calls: list[tuple[int, str]] = []

    def turn(self, idx, text):
        self.calls.append((idx, text))
        if len(self.calls) == 1:
            return {"content": "Wie beginnt deine Zeitreise?"}
        return {"content": "```json\n" + json.dumps(_FIXTURE_SAVE) + "\n```"}


def _broken_persona_factory(_persona_key: str):
    """Entspricht `adapters/factories.py:default_persona_driver_factory`s
    unkonfiguriertem Zweig: wirft eine `RuntimeError` beim AUFRUF (nicht
    erst beim Benutzen des zurueckgegebenen Treibers) -- genau der
    Kontrollfluss aus OFFENE_BEDIENBEFUNDE.md Punkt 8."""
    raise RuntimeError("Persona-Anbindung nicht konfiguriert (Testsimulation UX18)")


def test_ai_leader_invite_with_broken_persona_factory_is_caught_honestly():
    """UX18 Leaderweg: `l lead:persona:<id>` mit kaputter Persona-Factory
    darf keinen Traceback werfen -- ehrliche Textzeile, `session.run()`
    bleibt kontrolliert (rc=0)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write_test_profile(d / "run")
        # R4-Nachzug (F3-Rest, Generalklaerung): 'broken_leader' muss eigene
        # bestaetigte Hostpersona von 'p1' sein, s. Docstring von
        # `_bootstrap_own_persona` (VOR `_make_ready`).
        _bootstrap_own_persona(d / "run", d / "states", "p1", "broken_leader")
        _make_ready(d / "onboarding", d / "states", d / "run", "broken_leader")
        printed: list[str] = []
        gm = _FakeCreationGm()
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input([
                "n", "Ich erwache in einem Rift.",
                "l lead:persona:broken_leader",
            ]),
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: gm,
            persona_driver_factory=_broken_persona_factory,
        )
        rc = session.run()
        assert rc == 0
        assert any("KI-Leader 'broken_leader' nicht moeglich" in p for p in printed), printed
        assert not any("Traceback" in p for p in printed), printed


def test_guest_invite_with_broken_persona_factory_is_caught_and_table_continues():
    """UX18 Gastweg: EIN Gast mit kaputter Persona-Factory scheitert
    ehrlich, der Rest der Runde (hier: Solo-Leader) bleibt lauffaehig --
    kein Abbruch der gesamten Runde wegen eines einzelnen Gastfehlers."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write_test_profile(d / "run")
        # R4-Nachzug (F3-Rest, Generalklaerung): 'broken_guest' muss eigene
        # bestaetigte Hostpersona von 'p1' sein, s. Docstring von
        # `_bootstrap_own_persona` (VOR `_make_ready`).
        _bootstrap_own_persona(d / "run", d / "states", "p1", "broken_guest")
        _make_ready(d / "onboarding", d / "states", d / "run", "broken_guest")
        printed: list[str] = []
        gm = _FakeCreationGm()
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input([
                "n", "Ich erwache in einem Rift.",
                "l persona:broken_guest",
                "/pause",
            ]),
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: gm,
            persona_driver_factory=_broken_persona_factory,
        )
        rc = session.run()
        assert rc == 0
        assert any("Einladung an Persona 'broken_guest' nicht moeglich" in p for p in printed), printed
        assert not any("Traceback" in p for p in printed), printed


def main() -> int:
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
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
