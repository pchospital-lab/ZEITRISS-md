#!/usr/bin/env python3
"""
tests/mmo_sim/test_r4_lobby_scheduling_fairness_2026_10_21.py — Pflicht-
Integrationstest fuer R4-FixB1 (B1-FIX-SPEC.md, 02_JETZT_ENTWICKELN.md §1,
Critic-Report BLOCKER B1).

Deckt den ECHTEN Produktpfad `core.lobby_flow.run_lobby_window` ueber
mehrere Fenster hinweg ab -- reales Roster, echte Tischbildung/-bindung/
-locks, skripteter Fake-GM + Fake-Personas (Muster: `worker/critic_repro_
starvation.py` und `test_r2_hauptbefund2_bound_table_recovery.py`). KEINE
im Test nachgebaute Phasenentscheidung als Ganzpfadbeleg (02§1-Verbot) --
jede Assertion geht ueber den echten Aufrufer.

B1 war: Fix1 (`find_bound_active_continuable_table`) gewann strukturell
IMMER gegen Fix2 (Free-Fallthrough), solange ein gebundener Tisch aktiv
blieb -- freie, spielbereite Figuren bekamen dadurch fuer die GESAMTE aktive
Spieldauer eines anderen Tisches null Initiative-Chancen. R4-FixB1
restrukturiert `run_lobby_window` so, dass die freie Runde IN JEDEM Fenster
ZUERST laeuft (STEP 1), und ein gebundener Tisch nur fortgesetzt wird, wenn
die freie Runde keinen neuen Tisch bildet (STEP 2).

Testet:
(A) FAIRNESS -- bei einem aktiven, fortsetzbaren gebundenen Tisch T1 UND
    spielbaren freien Figuren bekommt JEDE freie Figur eine Initiative-
    Anfrage WAEHREND T1 noch aktiv ist (nicht erst nach dessen Abschluss).
    Dieser Test MUSS auf dem Vor-B1-Fix-Stand fehlschlagen (diskriminierend
    -- separat per `git stash`/`git checkout` verifiziert, s. B1-IMPL-
    REPORT.md).
(B) FORTSETZUNG -- T1 bekommt ueber das GLEICHE `run_lobby_window`-Fenster
    (STEP 2, nachdem die freie Runde in STEP 1 keinen neuen Tisch gebildet
    hat) einen weiteren Zug (`sl_log` waechst), ohne Doppel-GM-Versand/
    Doppel-Harvest -- und schliesst danach korrekt ab (SECTION_COMPLETED,
    Locks freigegeben).
(C) KEIN ZWANGSBEITRITT -- cqb/face/medic werden nie Mitglieder von T1 und
    nie in `locks.json` gebunden; T1 bleibt ausschliesslich sniper+tech."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import test_l01_l10_lobby_initiative as l01  # noqa: E402

from mmo_sim.core import lobby_flow  # noqa: E402
from mmo_sim.core import lobby_service  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402

_FREE_KEYS = ("cqb", "face", "medic")
_TABLE_ID = "lobby-sniper-tech"


def _setup_roster_with_table_forming(root: Path):
    """Baut ein 5-Personen-Roster auf und spielt WINDOW 1 (sniper schlaegt
    vor, tech nimmt an -> T1 entsteht und spielt bis zur lokalen
    Sicherheitsobergrenze von `SectionRuntime`, NICHT bis zum Abschluss --
    `turns_before_marker=25` liegt bewusst ueber der lokalen Obergrenze,
    damit T1 einen ZWEITEN `run_lobby_window`-Aufruf braucht, um fertig zu
    werden -- exakt wie ein echter, mehrzuegiger aktiver Tisch)."""
    keys = ["sniper", "tech", *_FREE_KEYS]
    schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = l01._bootstrap_community(
        root, "community-op", keys,
    )
    write_test_profile(run_dir)
    for pk in keys:
        l01._make_ready(onboarding_dir, states_dir, run_dir, pk)

    section_id = f"{_TABLE_ID}-section"
    final_saves = {pk: l01._load_fixture_save(pk) for pk in ("sniper", "tech")}
    gm = l01._TableGM(_TABLE_ID, section_id, final_saves, turns_before_marker=25)

    sniper_driver = l01._ScriptedDriver("sniper", [
        json.dumps({"action": "propose", "wants": ["tech"]}),
    ] + ["Wir spielen weiter."] * 30 + ["Ich nehme mit, dass wir gut zusammengespielt haben."])
    first_offer_id = lobby_service.offer_id_for("lobby-community-op-0", "sniper", 0)
    tech_driver = l01._ScriptedDriver("tech", [
        f"ENTSCHEIDUNG offer_id={first_offer_id} participant_id=tech decision=accept explanation=Klingt gut.",
    ] + ["Ich sichere die Flanke."] * 30 + ["Ich nehme mit, dass ich gut gedeckt war."])
    # Freie Figuren pausieren ihr eigenes Fenster, sobald sie gefragt werden
    # -- harmlos/deterministisch, bildet aber garantiert KEINEN zweiten
    # Tisch (das waere ein eigenes Szenario), und laesst sich ueber
    # `driver.calls` als objektiver Initiative-Beleg auszaehlen.
    free_drivers = {pk: l01._ScriptedDriver(pk, ['{"action": "pause"}'] * 5) for pk in _FREE_KEYS}
    drivers = {"sniper": sniper_driver, "tech": tech_driver, **free_drivers}

    printed: list[str] = []
    session = l01._session(
        "op", onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
        gm_transport_factory=lambda *_a, **_kw: gm,
        persona_driver_factory=lambda pk: drivers[pk],
        printed=printed,
    )

    out1 = lobby_flow.run_lobby_window(session, ai_personas=None)
    assert out1.table_id == _TABLE_ID, out1
    assert out1.kind != lobby_flow.LobbyOutcomeKind.SECTION_COMPLETED, (
        f"T1 sollte nach Fenster 1 NOCH NICHT fertig sein (lokale Obergrenze < "
        f"turns_before_marker), bekam aber {out1.kind}"
    )
    for pk in _FREE_KEYS:
        assert len(free_drivers[pk].calls) == 0, (
            f"{pk} wurde bereits in Fenster 1 gefragt ({len(free_drivers[pk].calls)} Aufrufe) -- "
            "Fenster 1 ist reine Tischbildung, das ist hier nicht der Pruefgegenstand"
        )
    return run_dir, gm, drivers, free_drivers, session, len(gm.calls)


def test_r4_free_personas_get_initiative_while_bound_table_active():
    """(A) FAIRNESS + (B) FORTSETZUNG in einem echten Mehrfenster-Lauf: T1
    ist nach Fenster 1 aktiv+fortsetzbar (NICHT abgeschlossen). Fenster 2
    MUSS -- bevor/waehrend T1 fortgesetzt wird -- jede freie Figur
    (cqb/face/medic) tatsaechlich befragen (R4-FixB1 STEP 1 vor STEP 2),
    UND T1 bekommt im selben Fensteraufruf einen weiteren, echten Zug
    (sl_log waechst, kein Doppel-GM-Versand) bis zum Abschluss."""
    with tempfile.TemporaryDirectory() as td:
        run_dir, gm, drivers, free_drivers, session, gm_calls_after_window1 = (
            _setup_roster_with_table_forming(Path(td))
        )
        table_before = core_store.Table.load(run_dir, _TABLE_ID)
        assert table_before.status == "active"
        assert table_before.sl_log, "T1 sollte nach Fenster 1 bereits einen echten Zug im sl_log haben"
        sl_log_len_before = len(table_before.sl_log)

        # === WINDOW 2: T1 aktiv+fortsetzbar, cqb/face/medic frei die GANZE
        # ZEIT (ready=True, bound_table_id=None). ===
        out2 = lobby_flow.run_lobby_window(session, ai_personas=None)

        # (A) FAIRNESS -- KERN DES BLOCKER-FIXES: jede freie Figur wurde
        # WAEHREND T1 noch aktiv war (zu Beginn von Fenster 2) tatsaechlich
        # einmal befragt. Auf dem Vor-B1-Fix-Stand sind diese Zaehler 0
        # (Fix1 kehrt sofort zurueck, bevor der Free-Scheduler je erreicht
        # wird) -- diskriminierend verifiziert per git checkout, s. B1-IMPL-
        # REPORT.md.
        for pk in _FREE_KEYS:
            assert len(free_drivers[pk].calls) == 1, (
                f"{pk} sollte in Fenster 2 GENAU EINMAL befragt worden sein "
                f"(frei, bereit, T1 aktiv+fortsetzbar), bekam aber "
                f"{len(free_drivers[pk].calls)} Aufrufe -- R4-FixB1 STEP 1 lief nicht"
            )

        # (B) FORTSETZUNG -- T1 bekam im SELBEN Fensteraufruf (STEP 2, nach
        # der erfolglosen freien Runde) einen weiteren Zug, bis zum
        # Abschluss (25 Zuege gesamt, 20 aus Fenster 1 + 5 aus Fenster 2),
        # kein Doppel-GM-Versand (Gesamtzahl der GM-Aufrufe stimmt exakt).
        assert out2.table_id == _TABLE_ID, out2
        assert out2.kind == lobby_flow.LobbyOutcomeKind.SECTION_COMPLETED, out2
        assert len(gm.calls) == 25, f"erwartet genau 25 reale GM-Zuege gesamt, bekam {len(gm.calls)}"
        assert len(gm.calls) > gm_calls_after_window1, "T1 muss in Fenster 2 tatsaechlich fortgeschritten sein"

        table_after = core_store.Table.load(run_dir, _TABLE_ID)
        assert table_after.status == "closed"
        assert len(table_after.sl_log) >= sl_log_len_before, "sl_log darf beim Fortsetzen nicht schrumpfen"
        assert core_store._read_locks(run_dir) == {}, "Locks muessen nach Abschluss freigegeben sein"

        # (C) KEIN ZWANGSBEITRITT -- cqb/face/medic sind nie Mitglieder von
        # T1 geworden, egal in welchem Fenster.
        for pk in _FREE_KEYS:
            assert pk not in table_after.members, f"{pk} wurde faelschlich Mitglied von T1"
            assert pk not in table_after.chrononaut_ids, f"{pk} wurde faelschlich an T1 gebunden"


def test_r4_free_persona_never_forced_into_bound_table():
    """(C) KEIN ZWANGSBEITRITT, isoliert von (A)/(B): waehrend T1
    aktiv+fortsetzbar ist, bleibt eine freie Figur, die selbst NICHTS
    vorschlaegt (nur pausiert), zu JEDEM Zeitpunkt ungebunden -- kein
    automatischer Beitritt zum bestehenden gebundenen Tisch, egal wie oft
    `run_lobby_window` aufgerufen wird."""
    with tempfile.TemporaryDirectory() as td:
        run_dir, gm, drivers, free_drivers, session, _gm_calls_after_window1 = (
            _setup_roster_with_table_forming(Path(td))
        )
        lobby_flow.run_lobby_window(session, ai_personas=None)  # Fenster 2

        locks_after = core_store._read_locks(run_dir)
        for pk in _FREE_KEYS:
            assert pk not in locks_after, f"{pk} wurde trotz reinem Pausieren an einen Tisch gebunden"


if __name__ == "__main__":
    import traceback

    failures = []
    for name, fn in sorted(list(globals().items())):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"OK   {name}")
            except Exception as exc:  # noqa: BLE001
                failures.append(name)
                print(f"FAIL {name}: {exc}")
                traceback.print_exc()
    total = len([n for n in globals() if n.startswith("test_")])
    print(f"\n{total - len(failures)}/{total} Tests bestanden.")
    raise SystemExit(0 if not failures else 1)
