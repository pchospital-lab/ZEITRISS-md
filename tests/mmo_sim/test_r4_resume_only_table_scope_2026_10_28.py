#!/usr/bin/env python3
"""
tests/mmo_sim/test_r4_resume_only_table_scope_2026_10_28.py — Regression fuer
`--resume-only-table` (ZR-N2R-ANSCHLUSS-20261019-R4, Duo-Anschluss
2026-10-28, STATE-ANCHOR.md "BLOCKER: Duo-only nicht mechanisch erzwungen").

BEFUND (DRIVER-PRECHECK-REPORT.md Abschnitt 7): `lab resume`/`lab start`
sind COMMUNITY-WEIT -- ohne explizite Personaauswahl entspricht `selected`
der GESAMTEN bestaetigten Community. Im money-free Nachweislauf wurde
dabei ZUERST ein nicht-ziel-relevanter, aber ebenfalls gebundener-aktiver
Tisch (dort: Trio-`__3`) weiterverarbeitet, bevor der eigentliche Zieltisch
(dort: Duo-`__2`) an der Reihe war.

FIX (additiv, `mmo_sim/lab/cli.py::_run_controller`): neue Option
`--resume-only-table <table_id>` leitet `selected` aus den tatsaechlichen
Mitgliedern des gebundenen Tisches ab (`core.store.Table.load`) -- derselbe
`selected`-Mechanismus, der fuer `--personas` bereits existiert und ueber
`catchup.run_catch_up`s `ai_personas`-Gate in `core.lobby_flow.
play_bound_table` JEDEN Tisch mit einem Mitglied ausserhalb dieser Menge
VOR jeder Treiberkonstruktion anhaelt (WAITING_HUMAN) -- kein neuer
Dispatch-/Auswahlcode, nur eine zusaetzliche, tischgebundene Quelle fuer
dieselbe bereits verifizierte Beschraenkung.

Methode: ECHTER `mmo_sim.lab.cli.main()`-Aufruf (derselbe Einstieg, den der
Harness-Driver per Subprozess aufruft) -- Persona-/GM-Factories werden
GENAUSO ueber das Modulattribut gepatcht wie `driver.integrated.py::
_lab_subprocess_entry` es fuer den echten Subprozess tut (money-free: keine
echte HTTP-/CLI-Inferenz, nur lokale Testdoubles). Zwei UNABHAENGIGE, bereits
gebundene UND bereits aktive (sl_log nicht leer, analog dem realen
Duo-`__2`/Trio-`__3`-Zustand) Tische existieren VOR dem Aufruf: der
Zieltisch (sniper+tech) und ein fremder Tisch (cqb+face+medic), der NICHT
Teil von `--resume-only-table` ist.

Reuse (Leitprinzip "Reuse vor Neubau"): Bootstrap/Fixture-Saves/`_TableGM`
aus `test_l01_l10_lobby_initiative.py`, direkte Tisch-/Lock-Konstruktion
analog `test_bl1_subset_starvation_2026_10_21.py::_construct_foreign_
stuck_table` (dort fuer einen UNGESPIELTEN fremden Tisch; hier zusaetzlich
mit nicht-leerem `sl_log`, um den realen "bereits aktiv gespielten" R4-Fall
abzudecken)."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import test_l01_l10_lobby_initiative as l01  # noqa: E402

import mmo_sim.adapters.factories as factories_mod  # noqa: E402
from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissTableSizePolicy  # noqa: E402
from mmo_sim.lab import cli as lab_cli  # noqa: E402

TARGET_TABLE_MEMBERS = ("sniper", "tech")
FOREIGN_TABLE_MEMBERS = ("cqb", "face", "medic")
TARGET_TABLE_ID = "lobby-sniper-tech"
FOREIGN_TABLE_ID = "lobby-cqb-face-medic"


class _ResumeThenPauseDriver:
    """Antwortet auf eine laufende Tischfortsetzung mit gewoehnlichem Text
    (GM-Fake schliesst danach sofort ab, `turns_before_marker=1`) und auf
    ein spaeteres freies Lobby-Initiativfenster IMMER mit `pause` -- kein
    neuer Tisch, kein zweiter Abschnitt (diese Regression prueft NUR den
    Scope-Filter, nicht Mehrrundenverhalten)."""

    def __init__(self, pk: str):
        self.pk = pk
        self.calls: list[dict] = []

    def decide(self, ctx: dict) -> ParticipantDecision:
        self.calls.append(ctx)
        if "begrenztes eigenes Lobby-Initiativfenster" in ctx.get("user", ""):
            return ParticipantDecision(text=json.dumps({"action": "pause"}), origin_source=f"r4scope:{self.pk}")
        return ParticipantDecision(text="Wir setzen die laufende Szene fort.", origin_source=f"r4scope:{self.pk}")


class _NeverCalledDriver:
    """Fail-closed-Wache: EIN Treiberaufruf fuer ein Mitglied des fremden
    Tisches waere bereits der Bug (R4-Execution-Scope: dieser Tisch darf von
    `--resume-only-table` ueberhaupt nicht erreicht werden)."""

    def __init__(self, pk: str):
        self.pk = pk

    def decide(self, ctx: dict) -> ParticipantDecision:
        raise AssertionError(
            f"{self.pk!r} gehoert zum fremden, NICHT ausgewaehlten Tisch und haette NIE einen "
            f"Treiberaufruf bekommen duerfen (--resume-only-table-Scope durchbrochen): {ctx!r}"
        )


def _bootstrap(root: Path):
    all_keys = list(TARGET_TABLE_MEMBERS) + list(FOREIGN_TABLE_MEMBERS)
    schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = l01._bootstrap_community(
        root, "community-r4scope", all_keys,
    )
    write_test_profile(run_dir)
    chrono_ids = {pk: l01._make_ready(onboarding_dir, states_dir, run_dir, pk) for pk in all_keys}
    all_saves = {pk: l01._load_fixture_save(pk) for pk in all_keys}
    gm_registry: dict[str, l01._TableGM] = {}

    def gm_transport_factory_builder(data_dir, repo_root):
        def gm_transport_factory(table_id: str | None = None):
            table = core_store.Table.load(run_dir, table_id)
            final_saves = {pk: all_saves[pk] for pk in table.members if pk in all_saves}
            gm = gm_registry.get(table_id)
            if gm is None:
                gm = l01._TableGM(table_id, f"{table_id}-section", final_saves, turns_before_marker=1)
                # I2/Q07 (core.admission.read_admission_block): die GM-Rolle
                # ist IMMER dollarbegrenzt -- `runtime.py` liest
                # `getattr(gm_transport, "output_limit_tokens", None)`, OHNE
                # dieses Attribut gilt output_bound_known=False und ein
                # hartes --max-usd lehnt JEDE Anfrage ab (Q07, money-free
                # Fail-closed, kein stilles Output=0). Analoge Rolle wie das
                # reale `MMO_SIM_GM_OUTPUT_LIMIT_TOKENS`-Env fuer den echten
                # Factory-Pfad (hier direkt am Testdouble, da dieser Test die
                # Factory komplett ersetzt).
                gm.output_limit_tokens = 4096
                gm_registry[table_id] = gm
            return gm
        return gm_transport_factory

    return run_dir, chrono_ids, gm_transport_factory_builder


def _bind_active_table(run_dir: Path, chrono_ids: dict, table_id: str, members: tuple[str, ...]) -> None:
    """Direkte Store-Level-Konstruktion EINES bereits gebundenen, AKTIVEN
    Tisches mit nicht-leerem `sl_log` (bereits gespielt, noch nicht
    abgeschlossen) -- deckt den realen R4-Zustand ab (Duo-`__2`/Trio-`__3`
    sind beide `active`, keiner ist `unplayed`), analog
    `test_bl1_subset_starvation_2026_10_21.py::_construct_foreign_stuck_
    table`, hier zusaetzlich mit `sl_log` statt leer."""
    (run_dir / "tables").mkdir(parents=True, exist_ok=True)
    leader = members[0]
    others = list(members[1:])
    offer_id = f"offer-{leader}-{table_id}"
    offer_log = [{"type": "offer", "id": offer_id, "from": leader, "wants": others}]
    offer_log += [{"type": "consent", "offer_id": offer_id, "from": pk, "accept": True} for pk in others]
    table = core_store.Table(
        table_id=table_id, leader=leader, members=list(members),
        chrononaut_ids={pk: chrono_ids[pk] for pk in members},
        run_dir=run_dir, status="active", sl_log=[{"turn": 1, "note": "r4scope-fixture"}],
        operator_meta={
            "offer_log": offer_log, "source_offer_id": offer_id, "dissenters": {},
            "derivation_reason": "r4-resume-only-table-regression-fixture",
        },
    )
    table.persist()
    lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    for pk in members:
        lobby.lock_chrononaut(chrono_ids[pk], table_id)


def test_resume_only_table_scopes_dispatch_to_target_table_only():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, chrono_ids, gm_transport_factory_builder = _bootstrap(root)

        _bind_active_table(run_dir, chrono_ids, TARGET_TABLE_ID, TARGET_TABLE_MEMBERS)
        _bind_active_table(run_dir, chrono_ids, FOREIGN_TABLE_ID, FOREIGN_TABLE_MEMBERS)

        drivers = {pk: _ResumeThenPauseDriver(pk) for pk in TARGET_TABLE_MEMBERS}
        drivers.update({pk: _NeverCalledDriver(pk) for pk in FOREIGN_TABLE_MEMBERS})

        orig_persona_factory = factories_mod.default_persona_driver_factory
        orig_gm_factory = factories_mod.default_gm_transport_factory
        factories_mod.default_persona_driver_factory = lambda data_dir, profile=None: (lambda pk: drivers[pk])
        factories_mod.default_gm_transport_factory = gm_transport_factory_builder
        import os
        env_added = "MMO_SIM_PERSONA_API_BASE_URL" not in os.environ
        os.environ.setdefault("MMO_SIM_PERSONA_API_BASE_URL", "http://127.0.0.1:1")
        try:
            rc = lab_cli.main([
                "start", "--data-dir", str(root), "--community", "r4scope", "--profile", "api",
                "--resume-only-table", TARGET_TABLE_ID,
                "--max-requests", "40", "--max-seconds", "120", "--max-usd", "5.0",
                "--max-wall-seconds", "60", "--max-idle-windows", "3",
            ], repo_root=_REPO_ROOT)
        finally:
            factories_mod.default_persona_driver_factory = orig_persona_factory
            factories_mod.default_gm_transport_factory = orig_gm_factory
            if env_added:
                os.environ.pop("MMO_SIM_PERSONA_API_BASE_URL", None)

        assert rc == 0, f"lab start (--resume-only-table) sollte geordnet mit rc=0 enden, war {rc}"

        # Nicht-Ziel-Tisch uebersprungen: KEIN Treiberaufruf fuer irgendein
        # fremdes Mitglied (sonst haette `_NeverCalledDriver` bereits oben
        # eine AssertionError geworfen, die `lab_cli.main` propagiert haette).
        for pk in FOREIGN_TABLE_MEMBERS:
            assert core_store.sections_played_by_participant(run_dir).get(pk, 0) == 0, (
                f"fremdes Mitglied {pk!r} haette NICHT vorankommen duerfen (Scope-Bruch)"
            )
        assert not core_store._table_has_final(run_dir, FOREIGN_TABLE_ID), (
            "fremder Tisch darf durch diesen gescopten Aufruf NICHT abgeschlossen worden sein"
        )

        # Ziel-Tisch erreicht: beide Zielmitglieder sind vorangekommen, der
        # Zieltisch hat seinen Final.
        counts_after = core_store.sections_played_by_participant(run_dir)
        for pk in TARGET_TABLE_MEMBERS:
            assert counts_after.get(pk, 0) >= 1, (
                f"Zielmitglied {pk!r} haette ueber den gescopten Resume-Dispatch vorankommen muessen: "
                f"{counts_after}"
            )
        assert core_store._table_has_final(run_dir, TARGET_TABLE_ID), (
            "Zieltisch haette ueber den normalen Dispatchweg abschliessen muessen"
        )
        assert any(drivers[pk].calls for pk in TARGET_TABLE_MEMBERS), (
            "mindestens ein Zielmitglied haette tatsaechlich einen Treiberaufruf bekommen muessen"
        )


def test_resume_only_table_rejects_unknown_table_before_any_dispatch():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, chrono_ids, gm_transport_factory_builder = _bootstrap(root)
        _bind_active_table(run_dir, chrono_ids, TARGET_TABLE_ID, TARGET_TABLE_MEMBERS)

        import contextlib
        import io
        import os
        env_added = "MMO_SIM_PERSONA_API_BASE_URL" not in os.environ
        os.environ.setdefault("MMO_SIM_PERSONA_API_BASE_URL", "http://127.0.0.1:1")
        stderr_buf = io.StringIO()
        try:
            with contextlib.redirect_stderr(stderr_buf):
                rc = lab_cli.main([
                    "start", "--data-dir", str(root), "--community", "r4scope", "--profile", "api",
                    "--resume-only-table", "lobby-this-table-does-not-exist",
                    "--max-requests", "40", "--max-seconds", "120", "--max-usd", "5.0",
                    "--max-wall-seconds", "60", "--max-idle-windows", "3",
                ], repo_root=_REPO_ROOT)
        finally:
            if env_added:
                os.environ.pop("MMO_SIM_PERSONA_API_BASE_URL", None)
        assert rc == 2, f"ein unbekannter --resume-only-table sollte VOR jedem Dispatch mit rc=2 (LabConfigError) enden, war {rc}"
        assert "lobby-this-table-does-not-exist" in stderr_buf.getvalue(), stderr_buf.getvalue()
        assert core_store.sections_played_by_participant(run_dir) == {}, (
            "ein abgelehnter unbekannter Tisch darf KEINE Bestandsmutation ausgeloest haben"
        )


def test_resume_only_table_and_personas_are_mutually_exclusive():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, chrono_ids, gm_transport_factory_builder = _bootstrap(root)
        _bind_active_table(run_dir, chrono_ids, TARGET_TABLE_ID, TARGET_TABLE_MEMBERS)

        import contextlib
        import io
        import os
        env_added = "MMO_SIM_PERSONA_API_BASE_URL" not in os.environ
        os.environ.setdefault("MMO_SIM_PERSONA_API_BASE_URL", "http://127.0.0.1:1")
        stderr_buf = io.StringIO()
        try:
            with contextlib.redirect_stderr(stderr_buf):
                rc = lab_cli.main([
                    "start", "--data-dir", str(root), "--community", "r4scope", "--profile", "api",
                    "--personas", "sniper,tech", "--resume-only-table", TARGET_TABLE_ID,
                    "--max-requests", "40", "--max-seconds", "120", "--max-usd", "5.0",
                    "--max-wall-seconds", "60", "--max-idle-windows", "3",
                ], repo_root=_REPO_ROOT)
        finally:
            if env_added:
                os.environ.pop("MMO_SIM_PERSONA_API_BASE_URL", None)
        assert rc == 2, f"--personas + --resume-only-table gleichzeitig muss rc=2 (LabConfigError) ergeben, war {rc}"
        assert "schliessen sich aus" in stderr_buf.getvalue(), stderr_buf.getvalue()


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failures = 0
    for fn in tests:
        try:
            fn()
            print(f"OK   {fn.__name__}")
        except Exception:
            failures += 1
            import traceback as _tb
            print(f"FAIL {fn.__name__}")
            _tb.print_exc()
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    sys.exit(1 if failures else 0)
