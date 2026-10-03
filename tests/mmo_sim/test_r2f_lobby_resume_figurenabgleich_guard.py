#!/usr/bin/env python3
"""
tests/mmo_sim/test_r2f_lobby_resume_figurenabgleich_guard.py — neue
dauerhafte Repo-Regression fuer den Figurenwerteabgleich vor Lobby-Resume
(MAIN-QUELLENENTSCHEIDUNG-FIGURENABGLEICH.md, extern:
`tests-review/review_resume_current_identity.py` im Lieferpaket, NICHT Teil
dieses Repos).

Die gemeinsame `ui/tui.py:_resume_consistency_hold_reason` (bereits von
`test_r2c`/`test_r2d`/`test_r2e` fuer Schluessel-/Lock-/Belegketten-Relationen
geprueft) verglich bisher NUR die Schluesselmenge und den Lockeigentuemer der
GESPEICHERTEN `Table.chrononaut_ids`-Werte -- NICHT deren Zuordnung zu den
tatsaechlich ueber `self._resolve_member` aufgeloesten Current-Figuren. Werden
zwei vollstaendige Werte in der Tischmap zwischen zwei Mitgliedern VERTAUSCHT
(gleiche Schluessel, gleiche Locks bleiben erhalten), rutschte ein noch
unresolviertes, bereits vollstaendig bestaetigtes Angebot im ALLGEMEINEN
Angebotszweig bisher bis zu Personaentscheidungen/GM-Turns/Resolution-Nachtrag
durch und scheiterte erst an der spaeteren Save-Validierung (Harvest).

Fixstelle: `_resume_consistency_hold_reason` erhaelt jetzt zusaetzlich die
bereits aufgeloeste `resolved_chrononaut_ids`-Map (persona_key ->
`block_char_id(active_save)`) und vergleicht sie pro Mitglied gegen
`table.chrononaut_ids` -- Identitaet, NICHT Save-Version (eine neuere gueltige
Save-Version DERSELBEN Figur bleibt zulaessig). BEIDE Aufrufstellen (Finder-
zweig, allgemeiner Angebotszweig) reichen die Map jetzt durch.

Reuse (kein zweiter Bootstrap-Baustein): `test_r2c_lobby_resume_zuordnung_
guard.py`s `_seed`/`_run_child`/`_own_decision_calls` (Finderzweig-Seeding
ueber `gm-init-failure`, B2-Stil) UND `test_r2e_lobby_resume_open_offer_
guard.py`s `_seed_unresolved_open_offer`/`_run_child`/`_protected_snapshot`
(allgemeiner-Angebotszweig-Seeding ueber `resolution-write-failure`, B1-Stil)
werden unveraendert importiert. Kein eigener Child-Entry-Point noetig -- die
Figurenvertauschung selbst ist reine Testdateikorruption ZWISCHEN zwei
`_run_child`-Aufrufen (identische Technik wie `test_r2c`s/`test_r2d`s/
`test_r2e`s missing-map/missing-lock-Faelle), die neue Save-Version wird
direkt ueber die bestehende `core.store.publish_current_save`-Autoritaet
veroeffentlicht (identische Technik wie `tests-review/review_resume_current_
identity.py`s `newer-same-figure`-Fall). Kein `run_play_session`-
Rettungscallback -- alle Faelle laufen ueber den tatsaechlichen,
unveraenderten Spielstart-Pfad (`ui/tui.py:_play_bound_table`/
`_cmd_lobby_initiative` -> `app_service.run_play_session`); Assertions pruefen
echte Diskzustaende (Tabellenstatus/Locks/Currents/Log), nicht bloss Log-/
Helfererfolg.

Deckt:
- Vertauschung am allgemeinen (bisher ungeschuetzten) Angebotszweig: Hold vor
  jeder Personaentscheidung/jedem GM-Turn, geschuetzte Bytes unveraendert,
  Tisch bleibt `active`; nach Test-Restore schliesst derselbe Tisch real ab,
  ohne erneute Zustimmung.
- Vertauschung am Finderzweig: haelt bereits ueber `store.find_bound_active_
  unplayed_table`s eigenen Wertevergleich (unveraendert) UND jetzt zusaetzlich
  ueber denselben gemeinsamen Guard (Doppelpruefung, MAIN-QUELLENENTSCHEIDUNG-
  FIGURENABGLEICH.md: "im Finderweg redundant ... aber harmlos/konsistent")
  -- keine Regression durch den neuen Parameter.
- Neuere gueltige Save-Version DERSELBEN Figur (nur `save_id` geaendert,
  `block_char_id` identisch) bleibt zulaessig und schliesst normal ab -- kein
  falscher Fix, der Save-ID-/Versionsgleichheit statt Figuren-Identitaet
  verlangt.

Ueber den Dateinamen `test_*.py` automatisch in `run_all.py` eingebunden."""
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

import test_r2c_lobby_resume_zuordnung_guard as r2c  # noqa: E402
import test_r2e_lobby_resume_open_offer_guard as r2e  # noqa: E402

from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402


def _swap_chrononaut_values(table_path: Path) -> None:
    """Vertauscht GENAU die zwei vollstaendigen `chrononaut_ids`-Werte
    zwischen 'sniper' und 'tech' -- Mitgliederliste, Mapschluessel und
    vorhandene Locks bleiben unveraendert (identische Testeingabe wie
    `tests-review/review_resume_current_identity.py`s `swapped-map`-Fall)."""
    obj = json.loads(table_path.read_text(encoding="utf-8"))
    ids = obj["chrononaut_ids"]
    assert "sniper" in ids and "tech" in ids, "Testannahme verletzt: beide Mitglieder fehlten bereits vor der Vertauschung"
    assert ids["sniper"] != ids["tech"], "Testannahme verletzt: Werte waren bereits identisch, keine echte Vertauschung"
    ids["sniper"], ids["tech"] = ids["tech"], ids["sniper"]
    table_path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def test_figurenabgleich_open_offer_swap_holds_then_restores():
    """Vertauschung am allgemeinen Angebotszweig (bisher ungeschuetzter
    zweiter Einstieg): ein noch unresolviertes, vollstaendig bestaetigtes
    Angebot darf trotz gleicher Schluessel/Locks NICHT bis zu
    Personaentscheidungen/GM-Turns/Resolution-Nachtrag durchrutschen, wenn
    die gespeicherte Figurenzuordnung vertauscht ist."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        r1 = r2e._seed_unresolved_open_offer(root)
        tid = r1["tables"][0]["table_id"]

        table_path = root / "run" / "tables" / f"{tid}.json"
        original_table_bytes = table_path.read_bytes()

        _swap_chrononaut_values(table_path)
        before = r2e._protected_snapshot(root)

        r2 = r2e._run_child(root, "pause", root / "05-open-offer-swap-conflict.json")
        after = r2e._protected_snapshot(root)

        assert not r2["errors"], (
            f"eine konkrete kontrollierte Meldung wird erwartet, keine rohe Ausnahme: {r2['errors']}"
        )
        assert r2c._own_decision_calls(r2) == 0, "kein Persona-/Consent-Call vor dem Hold"
        assert r2["gm_calls"] == 0, "kein GM-/Spielstart bei vertauschten Figurenwerten"
        assert r2["tables"][0]["status"] == "active", "Tisch bleibt bei Vertauschung aktiv"
        assert before == after, (
            "geschuetzte Bytes (Tables/Locks/Angebotslog/Currents/States) duerfen sich "
            "beim Hold NICHT zusaetzlich veraendern -- insbesondere KEIN Figurentausch, "
            "kein Lock-Ergaenzen, keine neue Resolution als Scheinreparatur"
        )
        assert any(tid in p for p in r2["printed"]), f"konkrete Tisch-ID in der Meldung erwartet: {r2['printed']}"

        table_path.write_bytes(original_table_bytes)

        r3 = r2e._run_child(root, "pause", root / "05-open-offer-swap-restored.json")
        assert not r3["errors"], r3["errors"]
        assert len(r3["tables"]) == 1 and r3["tables"][0]["table_id"] == tid
        assert r3["tables"][0]["status"] == "closed", "nach Wiederherstellung muss derselbe Tisch real abschliessen"
        assert r3["gm_calls"] >= 3
        assert not r3["locks"]
        assert all(v is not None for v in r3["current_ids"].values())
        assert r2c._own_decision_calls(r3) == 0, "kein erneuter Initiativ-/Consent-Request nach Restore-Resume"


def test_figurenabgleich_finder_swap_still_holds_then_restores():
    """Vertauschung am Finderzweig (B2-Stil, Resolution bereits geschrieben):
    haelt weiterhin -- ZUERST ueber `store.find_bound_active_unplayed_table`s
    eigenen, unveraenderten Wertevergleich (der Kandidat wird dort gar nicht
    erst gefunden), UND deckungsgleich ueber denselben gemeinsamen Guard,
    falls dieser je unabhaengig vom Finder erreicht wuerde -- keine Regression
    durch den neuen `resolved_chrononaut_ids`-Parameter."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        r2c._seed(root)

        r1 = r2c._run_child(root, "gm-init-failure", root / "06-finder-swap-r1.json")
        assert not r1["errors"], r1["errors"]
        assert len(r1["tables"]) == 1 and r1["tables"][0]["status"] == "active"
        assert r1["gm_calls"] == 0
        assert '"outcome": "table_bound"' in r1["offers"]
        tid = r1["tables"][0]["table_id"]

        table_path = root / "run" / "tables" / f"{tid}.json"
        original_table_bytes = table_path.read_bytes()

        _swap_chrononaut_values(table_path)
        before = r2e._protected_snapshot(root)

        r2 = r2c._run_child(root, "pause", root / "06-finder-swap-conflict.json")
        after = r2e._protected_snapshot(root)

        assert not r2["errors"], (
            f"eine konkrete kontrollierte Meldung wird erwartet, keine rohe Ausnahme: {r2['errors']}"
        )
        assert r2c._own_decision_calls(r2) == 0, "kein Persona-/Consent-Call vor dem Hold"
        assert r2["gm_calls"] == 0, "kein GM-/Spielstart bei vertauschten Figurenwerten"
        assert r2["tables"][0]["status"] == "active", "Tisch bleibt bei Vertauschung aktiv"
        assert before == after, (
            "geschuetzte Bytes duerfen sich beim Hold NICHT zusaetzlich veraendern"
        )
        assert any(tid in p for p in r2["printed"]), f"konkrete Tisch-ID in der Meldung erwartet: {r2['printed']}"

        table_path.write_bytes(original_table_bytes)

        r3 = r2c._run_child(root, "pause", root / "06-finder-swap-restored.json")
        assert not r3["errors"], r3["errors"]
        assert len(r3["tables"]) == 1 and r3["tables"][0]["table_id"] == tid
        assert r3["tables"][0]["status"] == "closed", "nach Wiederherstellung muss derselbe Tisch real abschliessen"
        assert r3["gm_calls"] >= 3
        assert not r3["locks"]
        assert all(v is not None for v in r3["current_ids"].values())
        assert r2c._own_decision_calls(r3) == 0, "kein erneuter Initiativ-/Consent-Request nach Restore-Resume"


def test_figurenabgleich_newer_save_version_same_figure_still_resumes():
    """Erhalt (Fall 03, kein falscher Fix): eine neuere gueltige Save-Version
    DERSELBEN Figur (nur `save_id` geaendert, `block_char_id`/Chrononaut-
    Identitaet unveraendert) darf den Resume NICHT blockieren -- der Guard
    vergleicht Figuren-Identitaet, keine starre Save-ID-/Versionsgleichheit."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        r1 = r2e._seed_unresolved_open_offer(root)
        tid = r1["tables"][0]["table_id"]

        run_dir = root / "run"
        states_dir = root / "states"
        # Identisch zu `test_r2c`/`test_r2e`s bereits genutztem Schema-Pfad.
        schema_path = r2c.l01._SCHEMA
        ps_store = PersonaStateStore(schema_path=schema_path)

        old_save_ids: dict[str, str | None] = {}
        new_char_ids: dict[str, str | None] = {}
        for pk in ("sniper", "tech"):
            save = core_store.load_current_save_or_raise(run_dir, pk, ps_store, states_dir)
            assert save is not None, f"Testannahme verletzt: kein veroeffentlichter Current-Save fuer {pk!r}"
            old_save_ids[pk] = save.get("save_id")
            old_char_id = zeitriss_saves.block_char_id(save)
            save["save_id"] = f"repo-regression-figurenabgleich-newer-version-{pk}"
            core_store.publish_current_save(run_dir, pk, save, ps_store, states_dir)
            republished = core_store.load_current_save_or_raise(run_dir, pk, ps_store, states_dir)
            new_char_ids[pk] = zeitriss_saves.block_char_id(republished)
            assert new_char_ids[pk] == old_char_id, (
                f"Testannahme verletzt: block_char_id fuer {pk!r} veraenderte sich trotz reiner Versionsbumpe"
            )
            assert republished.get("save_id") != old_save_ids[pk], (
                f"Testannahme verletzt: save_id fuer {pk!r} wurde nicht tatsaechlich neu veroeffentlicht"
            )

        r2 = r2e._run_child(root, "pause", root / "07-newer-version-resume.json")
        assert not r2["errors"], r2["errors"]
        assert len(r2["tables"]) == 1 and r2["tables"][0]["table_id"] == tid
        assert r2["tables"][0]["status"] == "closed", (
            "eine neuere gueltige Save-Version DERSELBEN Figur darf den Resume NICHT blockieren"
        )
        assert r2["gm_calls"] >= 3
        assert not r2["locks"]
        for pk in ("sniper", "tech"):
            assert r2["current_ids"][pk] is not None
            assert r2["current_ids"][pk] != old_save_ids[pk], (
                f"Testannahme verletzt: {pk!r} lief nicht tatsaechlich mit der neu veroeffentlichten Version weiter"
            )
        assert r2c._own_decision_calls(r2) == 0, "kein neuer Initiativ-/Consent-Request bei konsistenter Wiederaufnahme"


if __name__ == "__main__":
    import traceback

    tests = [
        test_figurenabgleich_open_offer_swap_holds_then_restores,
        test_figurenabgleich_finder_swap_still_holds_then_restores,
        test_figurenabgleich_newer_save_version_same_figure_still_resumes,
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
