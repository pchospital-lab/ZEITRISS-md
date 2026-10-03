#!/usr/bin/env python3
"""
tests/mmo_sim/test_i4_figure_continuity.py — I4 Figurenkontinuitaet
(02_ABNAHME_I4, Vertrag §3 A-E, verbindliche Wege 1-5).

Ergaenzt zusaetzlich zur externen Abnahmeprobe
`tests-review/review_i4_figure_roundtrip.py` (nicht Teil dieses Repos, prueft
nur INNERHALB eines Prozesses):

  - Weg 1 (`test_weg1_same_process_second_tuisession_...`): ACHTUNG --
    dieser Test verwendet nur eine ZWEITE `TuiSession`-Instanz auf denselben
    Verzeichnissen INNERHALB DESSELBEN Interpreterprozesses (kein echter
    Prozessneustart trotz des Namens 'frischer Prozess' in fruehreren
    Fassungen dieser Datei -- Review-Befund 2026-09-25, Vertrag §"Test- und
    Teambelege"). Nach A->B->A muss sie weiterhin A_neu und die zuletzt
    gewaehlte Figur wiederfinden -- kein Re-Insert, kein stiller Rollback.
    Eine Variante mit ECHTEN neuen Interpreterprozessen (`subprocess.run`)
    liegt separat in `test_i4_active_authority_subprocess.py::test_i4aa_
    weg1_real_subprocess_roundtrip`.
  - Weg 3: Re-Import einer bereits registrierten INAKTIVEN Figur -- identische
    Bytes sind idempotent (No-op), abweichende Bytes verlangen dieselbe
    ausdrueckliche Konfliktwahl wie fuer die aktive Figur (kein blindes
    Ueberschreiben, kein stilles Parken ohne Entscheidungsmoeglichkeit).
  - Weg 4: die atomare Katalog-Publikation (`catalog.store_figure_save`)
    uebersteht eine simulierte Unterbrechung (Crash zwischen tmp-Write und
    Rename) ohne die zuletzt gueltige Fassung zu beschaedigen/verlieren.
  - Weg 5: zwei lokale Teilnehmer mit je eigenen Figuren behalten getrennte
    Bindungen -- ein Aktivwechsel des einen beruehrt den anderen nicht.

Pure Python, nur `assert`, echter Exitcode. Providerfrei (synthetisches
GM-/Treiber-Double, kein externer Modellaufruf)."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import app_service, store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import (  # noqa: E402
    COMPLETION_MARKER, ZeitrissHarvestValidator, ZeitrissTableSizePolicy,
)
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_FIX = _REPO_ROOT / "internal" / "qa" / "harness" / "lobby" / "fixtures"
_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


def _sv(pk: str) -> dict:
    return json.loads((_FIX / "saves" / f"{pk}.json").read_text(encoding="utf-8"))


def _script(lines):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


class _GM:
    """Synthetisches GM-Double: liefert vorgegebene Antworten der Reihe
    nach, danach eine neutrale Fortsetzung. Kein externer Aufruf."""

    def __init__(self, answers):
        self.answers = list(answers)
        self.calls = []

    def turn(self, idx, text):
        self.calls.append({"turn_idx": idx, "user_text": text})
        content = self.answers.pop(0) if self.answers else "Die Szene laeuft weiter."
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "i4-test"}


def _final_text(blocks: dict, table_id: str, section_id: str) -> str:
    body = "\n".join("```json\n" + json.dumps(b) + "\n```" for b in blocks.values())
    return f"{body}\n{COMPLETION_MARKER} table_id={table_id} section_id={section_id}"


class _Driver:
    """Synthetischer Spielzug-Treiber (kein Modellzugriff); liefert den
    Save-Payload NUR im ersten Zug (Anker), wie ein echter Persona-/
    Human-Treiber es beim Import-Anker tut."""

    def __init__(self, save):
        self.save = save
        self.inputs: list = []

    def decide(self, ctx):
        self.inputs.append(copy.deepcopy(ctx))
        return ParticipantDecision(
            "Eine eigene Aktion", save_payload=self.save if len(self.inputs) == 1 else None,
            origin_source="synthetic:test",
        )


class Rig:
    """Selbststaendiger, ausschliesslich in-repo-basierter Testaufbau (kein
    externer --helpers-dir noetig) -- spiegelt exakt die Produktions-
    Aufrufkette (`TuiSession`/`core.app_service.run_play_session`), rein
    synthetische Fixtures aus `internal/qa/harness/lobby/fixtures`."""

    def __init__(self, base: Path, members=("sniper",)):
        self.base = Path(base)
        self.run = self.base / "run"
        self.states = self.base / "states"
        self.onboard = self.base / "onboarding"
        self.cat = self.base / "catalog"
        self.members = list(members)
        self.saves = {p: _sv(p) for p in members}
        self.ids = {p: saves.block_char_id(b) for p, b in self.saves.items()}
        self.ps = PersonaStateStore(_SCHEMA)
        for p in members:
            st = json.loads((_FIX / "persona_states" / f"{p}.json").read_text())
            st["rounds_played"] = 0
            st["round_history"] = {}
            st.pop("current_save_version", None)
            self.ps.save_state(p, st, states_dir=self.states)

    def ui(self, p="sniper", gm=None, inputs=None, shown=None) -> TuiSession:
        return TuiSession(
            self.onboard, self.cat, p, input_fn=_script(inputs or []),
            print_fn=(shown.append if shown is not None else (lambda x: None)),
            run_dir=self.run, states_dir=self.states, schema_path=_SCHEMA,
            gm_transport_factory=(lambda: gm) if gm is not None else None,
        )

    def import_all(self) -> None:
        for p, b in self.saves.items():
            self.ui(p, inputs=[json.dumps(b), "ENDE"])._cmd_import()

    def table(self, tid="pair"):
        lobby = store.Lobby(self.run, ZeitrissTableSizePolicy())
        for p in self.members:
            lobby.join(p)
        events = [{"type": "offer", "id": "explicit-synthetic", "from": self.members[0], "wants": self.members[1:]}]
        events += [
            {"type": "consent", "from": p, "offer_id": "explicit-synthetic", "accept": True}
            for p in self.members[1:]
        ]
        t, _derivation = store.create_table_from_offer_log(lobby, tid, events, self.ids)
        return lobby, t

    def play(self, lobby, table, gm, drivers, sid="section", maximum=6):
        contexts = {
            p: {"system": "EIGENER_KONTEXT_" + p, "user": "Spiele deine Rolle.", "import_save_payload": self.saves[p]}
            for p in self.members
        }
        return app_service.run_play_session(
            lobby, table, gm, TableController(table.leader, drivers), sid, contexts,
            self.states, "2026-09-24", "2026-09-24T00:00:00", COMPLETION_MARKER,
            ZeitrissHarvestValidator(), self.ps, saves.harvest_from_debrief, max_turns=maximum,
        )

    def current(self, p="sniper"):
        return store.load_current_save(self.run, p, self.ps, states_dir=self.states)


def _progressed(r: "Rig") -> dict:
    """Baut fuer 'sniper' einen gueltigen Abschnittsabschluss mit einem NEUEN
    Save (A_neu) -- dasselbe Muster wie die externe I4-Abnahmeprobe
    (`tests-review/review_i4_figure_roundtrip.py:progressed`)."""
    write_test_profile(r.run, max_turns=100, max_seconds=1000, max_usd=None)
    r.import_all()
    new = copy.deepcopy(r.saves["sniper"])
    new["save_id"] = "i4-test-after-section-A-002"
    lobby, table = r.table("pair")
    gm = _GM(["Die Szene laeuft.", _final_text({"sniper": new}, "pair", "section")])
    out = r.play(lobby, table, gm, {"sniper": _Driver(r.saves["sniper"])})
    assert out.completion.success, f"Fixture-Abschnitt muss abschliessen: {out.completion}"
    assert r.current() == new, "Fixture muss einen echten neuen Current-Save etablieren"
    return new


# ── Weg 1: zweite TuiSession (SELBER Prozess) nach A -> B -> A ─────────────
# Review-Befund 2026-09-25 ("Test- und Teambelege"): dieser Test verwendet
# nur eine zweite `TuiSession`-Instanz im GLEICHEN Python-Prozess, KEINEN
# echten Interpreterneustart -- entsprechend umbenannt (vorher irrefuehrend
# `test_weg1_fresh_process_...`). Die Positivaussagen bleiben unveraendert
# gueltig, nur die Prozessbehauptung war unzutreffend. Eine Variante mit
# ECHTEN neuen Interpreterprozessen liegt in
# `test_i4_active_authority_subprocess.py::test_i4aa_weg1_real_subprocess_roundtrip`.

def test_weg1_same_process_second_tuisession_retains_a_neu_after_a_b_a():
    with tempfile.TemporaryDirectory() as td:
        r = Rig(td, ("sniper",))
        new = _progressed(r)
        b = _sv("tech")
        b_id = saves.block_char_id(b)
        a_id = r.ids["sniper"]

        # B inaktiv importieren ('b' behalten -- A bleibt aktiv).
        r.ui(inputs=[json.dumps(b), "ENDE", "b"])._cmd_import()
        # Aktivwechsel zu B, dann zurueck zu A -- innerhalb DIESES Prozesses.
        r.ui(inputs=[b_id])._cmd_new_or_switch_character()
        r.ui(inputs=[a_id])._cmd_new_or_switch_character()
        assert r.current() == new, "Rueckwechsel innerhalb des Prozesses muss A_neu liefern"

        # I4 Weg 1 (02_ABNAHME_I4): eine ZWEITE `TuiSession`-Instanz (kein
        # gemeinsames In-Memory-Objekt, aber DERSELBE Interpreterprozess --
        # ein echter Prozessneustart wird separat in
        # `test_i4_active_authority_subprocess.py` geprueft) auf DENSELBEN
        # Verzeichnissen muss dieselbe aktuelle Auswahl UND Fassung
        # wiederfinden -- kein Re-Insert, kein stiller Rollback.
        second_ui = r.ui()
        card = second_ui._build_resume_card()
        assert card is not None and card.chrononaut_id == a_id, \
            "Fortsetzen-Karte einer zweiten TuiSession muss A als zuletzt gewaehlt zeigen"
        assert catalog.active_chrononaut_id(r.cat, "sniper") == a_id
        second_ps = PersonaStateStore(_SCHEMA)
        assert store.load_current_save(r.run, "sniper", second_ps, states_dir=r.states) == new, \
            "eine zweite TuiSession muss weiterhin A_neu als Current liefern (kein Reset auf den urspruenglichen Import)"
        # B behaelt auch unter einer zweiten TuiSession seine eigene Fassung.
        assert catalog.load_figure_save(r.cat, "sniper", b_id) == b, \
            "B darf durch den Rueckwechsel zu A nicht verloren gehen"


# ── Weg 3: Re-Import einer INAKTIVEN Figur (identisch/abweichend) ──────────

def test_weg3_inactive_figure_identical_reimport_is_noop():
    with tempfile.TemporaryDirectory() as td:
        r = Rig(td, ("sniper",))
        r.import_all()
        b = _sv("tech")
        b_id = saves.block_char_id(b)
        # Erster Import von B: inaktiv registrieren (A bleibt aktiv, 'b').
        r.ui(inputs=[json.dumps(b), "ENDE", "b"])._cmd_import()
        assert catalog.load_figure_save(r.cat, "sniper", b_id) == b

        # Identischer Re-Import derselben inaktiven Figur B: MUSS als No-op
        # erkannt werden (A20: "identischer Import No-op" gilt fuer JEDE
        # bekannte Char-ID, nicht nur die aktive) -- keine Konfliktrueckfrage,
        # keine zweite Registrierung/Aenderung.
        shown2: list = []
        r.ui(inputs=[json.dumps(b), "ENDE"], shown=shown2)._cmd_import()
        assert any("kein zweiter Fortschritt" in s or "Identischer Save" in s for s in shown2), \
            f"identischer Re-Import einer inaktiven Figur muss als No-op erkannt werden, shown={shown2}"
        assert catalog.active_chrononaut_id(r.cat, "sniper") == r.ids["sniper"], "A bleibt aktiv"
        assert catalog.load_figure_save(r.cat, "sniper", b_id) == b, "B unveraendert"


def test_weg3_inactive_figure_divergent_reimport_needs_explicit_choice():
    with tempfile.TemporaryDirectory() as td:
        r = Rig(td, ("sniper",))
        r.import_all()
        b = _sv("tech")
        b_id = saves.block_char_id(b)
        r.ui(inputs=[json.dumps(b), "ENDE", "b"])._cmd_import()

        b_changed = copy.deepcopy(b)
        b_changed["save_id"] = "i4-test-tech-changed"

        # Abweichender Stand OHNE gueltige explizite Wahl -> geparkt, KEIN
        # blindes Ueberschreiben von B's bisheriger Fassung.
        r.ui(inputs=[json.dumps(b_changed), "ENDE", "xxx"])._cmd_import()
        assert catalog.load_figure_save(r.cat, "sniper", b_id) == b, \
            "ohne gueltige explizite Konfliktwahl darf B's bisherige Fassung nicht ersetzt werden"

        # Ausdrueckliche Wahl 'a' (uebernehmen) -- B DARF jetzt aktualisiert
        # werden (bewusste Entscheidung, kein automatisches Hochleveln). Der
        # anschliessende zweite Prompt (Aktivwechsel A->B) wird mit 'b'
        # (bisherige aktive Figur A behalten) beantwortet -- dieser Test
        # prueft den Importkonflikt der INAKTIVEN Figur, nicht den Aktivwechsel.
        r.ui(inputs=[json.dumps(b_changed), "ENDE", "a", "b"])._cmd_import()
        assert catalog.load_figure_save(r.cat, "sniper", b_id) == b_changed, \
            "nach ausdruecklicher Wahl 'a' muss B's Katalogfassung aktualisiert sein"
        # A (die aktive Figur) bleibt von diesem inaktiven Konflikt unberuehrt.
        assert catalog.active_chrononaut_id(r.cat, "sniper") == r.ids["sniper"]
        assert r.current() == r.saves["sniper"]


# ── Weg 4: atomare Publikation uebersteht eine simulierte Unterbrechung ────

def test_weg4_interrupted_catalog_write_keeps_last_valid_bytes():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        first = {"v": 7, "save_id": "first", "characters": [{"char_id": "chrono-a"}]}
        catalog.store_figure_save(d, "p1", "chrono-a", first)
        before = catalog.load_figure_save(d, "p1", "chrono-a")
        assert before == first

        # Unterbrechung SIMULIEREN: der tmp-Write findet statt, aber das
        # abschliessende `Path.replace` (atomarer Rename) schlaegt fehl
        # (Crash "zwischen" Schreiben und Umbenennen) -- die zuletzt
        # gueltige Datei darf dabei NICHT beschaedigt/geleert werden (Vertrag
        # §3 C: "Fehler bei Uebernahme/Auswahl duerfen keinen alten Snapshot
        # still zum gueltigen Current machen und keine andere Figur
        # verlieren").
        real_replace = Path.replace

        def _boom(self, target):
            if self.name.endswith(".json.tmp"):
                raise OSError("simulierter Absturz vor dem atomaren Rename")
            return real_replace(self, target)

        Path.replace = _boom
        try:
            try:
                catalog.store_figure_save(
                    d, "p1", "chrono-a",
                    {"v": 7, "save_id": "second-crashed", "characters": [{"char_id": "chrono-a"}]},
                )
                assert False, "simulierter Absturz haette propagieren muessen"
            except OSError:
                pass
        finally:
            Path.replace = real_replace

        after = catalog.load_figure_save(d, "p1", "chrono-a")
        assert after == before, \
            "eine unterbrochene Publikation darf die letzte gueltige Fassung nicht beschaedigen/verlieren"
        assert after["save_id"] == "first", "kein stiller Rollback auf einen ANDEREN Stand, kein zweiter Fortschritt"


def test_weg4_stale_catalog_active_id_does_not_corrupt_outgoing_figure():
    """End-Critic-Befund (BLOCKER 1, END-CRITIC-I4.md): das bereits VOR
    diesem I4-Fix bestehende Absturzfenster zwischen `core_store.publish_
    current_save` und `catalog.bind_for_section` (in `_switch_active_
    figure`/`_cmd_import`/`_cmd_new_or_switch_character`) kann `catalog.
    active_chrononaut_id` veraltet stehenlassen. `_sync_outgoing_active_
    figure` darf sich beim naechsten Wechselversuch NICHT auf dieses Feld
    verlassen -- sonst schreibt es die tatsaechlichen (zur ANDEREN Figur
    gehoerenden) Current-Daten unter der ID der veralteten "aktiven" Figur
    in deren Katalogpersistenz und zerstoert deren zuletzt gueltigen Stand
    (Vertrag §3 C/E: keine Vermischung, kein Verlust einer Figur)."""
    with tempfile.TemporaryDirectory() as td:
        r = Rig(td, ("sniper",))
        a_neu = _progressed(r)
        b = _sv("tech")
        b_id = saves.block_char_id(b)
        a_id = r.ids["sniper"]

        # B inaktiv importieren ('b' behalten -- A bleibt aktiv).
        r.ui(inputs=[json.dumps(b), "ENDE", "b"])._cmd_import()
        assert catalog.active_chrononaut_id(r.cat, "sniper") == a_id
        assert catalog.load_figure_save(r.cat, "sniper", b_id) == b

        # Absturz simulieren: `catalog.bind_for_section` schlaegt fehl,
        # NACHDEM `core_store.publish_current_save` (im Produktcode
        # unveraendert von I4) bereits gelaufen ist.
        real_bind = catalog.bind_for_section

        def _boom(*a, **kw):
            raise OSError("simulierter Absturz zwischen publish_current_save und bind_for_section")

        catalog.bind_for_section = _boom
        ui = r.ui()
        entries = catalog.list_for_participant(r.cat, "sniper")
        try:
            try:
                ui._switch_active_figure(b_id, entries)
                assert False, "der injizierte Fehler haette propagieren muessen (Testaufbau ungueltig sonst)"
            except OSError:
                pass
        finally:
            catalog.bind_for_section = real_bind

        assert r.current() == b, "Current traegt nach dem simulierten Absturz bereits B's Daten"
        assert catalog.active_chrononaut_id(r.cat, "sniper") == a_id, \
            "catalog.active_chrononaut_id bleibt veraltet auf A stehen (bind_for_section lief nicht)"

        # Zweiter, spaeterer Wechselversuch (z.B. nach Prozess-Restart) --
        # zielt erneut auf B, waehrend der Katalog faelschlich A als aktiv
        # ausweist.
        ui2 = r.ui()
        entries2 = catalog.list_for_participant(r.cat, "sniper")
        ui2._switch_active_figure(b_id, entries2)

        assert catalog.load_figure_save(r.cat, "sniper", a_id) == a_neu, \
            "A's eigene Katalogfassung darf durch das veraltete active_chrononaut_id-Feld " \
            "nicht mit B's Daten ueberschrieben werden (A_neu darf nicht verloren gehen)"


# ── Weg 5: zwei lokale Teilnehmer behalten getrennte Bindungen ─────────────

def test_weg5_two_participants_keep_independent_bindings():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        catalog.register(d, catalog.CatalogEntry("p1", "chrono-p1-a", "p1"))
        catalog.register(d, catalog.CatalogEntry("p1", "chrono-p1-b", "p1"))
        catalog.register(d, catalog.CatalogEntry("p2", "chrono-p2-a", "p2"))
        catalog.bind_for_section(d, "p1", "chrono-p1-a", has_open_section=False)
        catalog.bind_for_section(d, "p2", "chrono-p2-a", has_open_section=False)

        assert catalog.active_chrononaut_id(d, "p1") == "chrono-p1-a"
        assert catalog.active_chrononaut_id(d, "p2") == "chrono-p2-a"

        # p1 wechselt zu seiner zweiten Figur -- p2s Bindung bleibt unberuehrt.
        catalog.bind_for_section(d, "p1", "chrono-p1-b", has_open_section=False)
        assert catalog.active_chrononaut_id(d, "p1") == "chrono-p1-b"
        assert catalog.active_chrononaut_id(d, "p2") == "chrono-p2-a", \
            "p2 darf durch p1s Wechsel nicht veraendert werden"
        assert {e.chrononaut_id for e in catalog.list_for_participant(d, "p1")} == {"chrono-p1-a", "chrono-p1-b"}
        assert {e.chrononaut_id for e in catalog.list_for_participant(d, "p2")} == {"chrono-p2-a"}


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
