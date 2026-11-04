#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_betreiber_r2_f4_gast_erschaffung_produktweg_2026_11_04.py
-- ZR-BETREIBER-GASTERSCHAFFUNG-20261103-R2, F4 (GENERAL-REVIEW.md §F4):
eng freigegebene Gast-Erschaffung als ECHTER Produktweg.

R1-Luecke (General-Review), die dieser Treiber schliesst: der alte O5-
Treiber (`test_zr_betreiber_o5_erschaffung_abandon_guard_2026_11_03.py`,
unveraendert als schmale Regression erhalten) ruft `run_admitted_creation_
dialog` DIREKT auf -- "freigegeben" ist dort NUR Prompttext, es gibt KEINEN
Grant-Check, `get_reply` wird NIE aufgerufen (die SL liefert den Save
sofort), und geprueft wird NUR `onboarding.final_save`. Dieser Treiber
deckt stattdessen den ECHTEN Produktweg: konkrete Anfrage -> durable
Betreiberentscheidung (Grant) -> echter, bedienter Terminaldialog (`get_
reply` wird tatsaechlich via einem Fake-Readline aufgerufen) -> persoenliche
Katalog-/Current-Veroeffentlichung -> Lektuere durch einen FRISCHEN
Subprozess ueber den echten Produktleser (`core.store.load_current_save`)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss import creation_service as creation_grants  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


class _SpyGm:
    """Modellrand-Double: wirft SOFORT bei Aufruf -- Nachweis, dass bei
    fehlender/abgelehnter/fremder/veralteter Freigabe (F4 §2) NIE ein
    GM-Aufruf stattfindet (gleiches Muster wie `test_zr_betreiber_r2_f1_...
    _SpyFactory`)."""

    def turn(self, turn_idx: int, user_text: str, **kw) -> dict:
        raise AssertionError("_SpyGm: kein GM-Aufruf erwartet (fehlende/ungueltige Freigabe).")


def _spy_gm_factory():
    return _SpyGm()


class _OneShotCreationGm:
    """Liefert GENAU EINE vorgegebene v7-Save-Antwort im ERSTEN Turn --
    wirft bei jedem weiteren Aufruf (Beleg gegen einen unerwarteten
    zweiten Turn, Muster O5 `_OneShotGm`)."""

    def __init__(self, block: dict):
        self._block = block
        self.calls = 0

    def turn(self, turn_idx: int, user_text: str, **kw) -> dict:
        self.calls += 1
        if self.calls > 1:
            raise AssertionError("_OneShotCreationGm: unerwarteter zweiter Turn.")
        content = "```json\n" + json.dumps(self._block, ensure_ascii=False) + "\n```"
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "f4-fake"}


class _AskOnceThenNeverGm:
    """Liefert im ERSTEN Turn eine blosse Frage (KEIN v7-Block) -- treibt
    den Dialog in den `get_reply`-Aufruf, ohne dass bereits etwas
    veroeffentlicht werden koennte. Wirft bei jedem weiteren Aufruf."""

    def __init__(self):
        self.calls = 0

    def turn(self, turn_idx: int, user_text: str, **kw) -> dict:
        self.calls += 1
        if self.calls > 1:
            raise AssertionError("_AskOnceThenNeverGm: unerwarteter zweiter Turn.")
        return {
            "content": "Wie soll deine Figur heissen?", "usage": {}, "sources": [], "latency_s": 0.0,
            "chat_id": "f4-ask",
        }


def _fixed_input(line: str):
    def _fn(prompt: str = "") -> str:
        return line
    return _fn


def _build_guest(root: Path, *, guest_id: str, run_dir: Path, states_dir: Path, gm_transport_factory, printed: list):
    return TuiSession(
        onboarding_dir=root / f"onboarding_{guest_id}", catalog_dir=root / f"catalog_{guest_id}",
        participant_id=guest_id, print_fn=printed.append,
        run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
        gm_transport_factory=gm_transport_factory, host_capable=False,
    )


def test_f4_gebundene_anfrage_freigabe_bedienter_dialog_persoenlicher_save_und_frischer_prozess():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        write_test_profile(run_dir, max_turns=200)
        operator_id, guest_id, char_id = "betreiber_f4", "gast_f4", "CHR-GASTF4-001"
        block = full_v7_save(char_id, name="Rook")

        gm = _OneShotCreationGm(block)
        guest_printed: list = []
        guest = _build_guest(
            root, guest_id=guest_id, run_dir=run_dir, states_dir=states_dir,
            gm_transport_factory=lambda: gm, printed=guest_printed,
        )

        # Vor jeder Freigabe: eine reine ID-Tischanfrage/Prompttext ist
        # KEINE Autoritaet -- der Dialog muss strukturell ablehnen, 0
        # GM-Aufrufe.
        spy_guest = _build_guest(
            root, guest_id=guest_id, run_dir=run_dir, states_dir=states_dir,
            gm_transport_factory=_spy_gm_factory, printed=guest_printed,
        )
        spy_guest._cmd_gast_erschaffung_dialog([operator_id])
        assert any("kein gueltiger Betreiber-Grant" in p for p in guest_printed), guest_printed
        assert onboarding.peek(guest.onboarding_dir, creation_grants.guest_onboarding_key(guest_id, 1)) is None

        # F4 §1: konkrete Anfrage -- echter Produktbefehl, kein Direktruf
        # der Domaenenschicht.
        guest._cmd_gast_erschaffung_anfragen([operator_id])
        record = creation_grants.grant_status(run_dir, guest_id)
        assert record["status"] == "requested", record

        # F4 §1: Betreiberentscheidung bindet Gast + GENAU EINEN
        # Erschaffungsvorgang dauerhaft.
        host_printed: list = []
        host = TuiSession(
            onboarding_dir=root / "host_onboarding", catalog_dir=root / "host_catalog",
            participant_id=operator_id, print_fn=host_printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            host_capable=True,
        )
        host._cmd_gast_erschaffung_annehmen([guest_id])
        record = creation_grants.grant_status(run_dir, guest_id)
        assert record["status"] == "approved" and record["generation"] == 1, record

        # F4 §3: Gast bedient TATSAECHLICH den Terminaldialog -- echter
        # get_reply-Adapter (kein Direktruf des Dialogkerns).
        guest._cmd_gast_erschaffung_dialog([operator_id])
        assert gm.calls == 1, f"genau ein Turn erwartet, calls={gm.calls}"
        onboarding_key = creation_grants.guest_onboarding_key(guest_id, 1)
        state = onboarding.peek(guest.onboarding_dir, onboarding_key)
        assert state is not None and state.status == "completed", state
        assert state.final_save == block, "persoenlicher Save muss real ueber complete_with_save gelandet sein."

        # F4 §5: persoenlicher Gastsave + Registrierung + aktive Fassung
        # gehoeren zum normalen Gastbestand.
        entries = catalog.list_for_participant(guest.catalog_dir, guest_id)
        assert any(e.chrononaut_id == char_id for e in entries), entries
        assert catalog.active_chrononaut_id(guest.catalog_dir, guest_id) == char_id
        assert catalog.load_figure_save(guest.catalog_dir, guest_id, char_id) == block

        # F4 §5: ein neuer Prozess (echter Subprozess) findet + liest die
        # Gastdatei UEBER DEN ECHTEN PRODUKTLESER (core.store.load_current_
        # save), nicht ueber eine Testspezial-Lektuere.
        script = (
            "import sys, json\n"
            f"sys.path.insert(0, {str(_REPO_ROOT)!r})\n"
            "from pathlib import Path\n"
            "from mmo_sim.core.persona_state import PersonaStateStore\n"
            "from mmo_sim.core import store as core_store\n"
            f"ps_store = PersonaStateStore(schema_path=Path({str(_SCHEMA_PATH)!r}))\n"
            f"save = core_store.load_current_save({str(run_dir)!r}, {guest_id!r}, ps_store, "
            f"states_dir=Path({str(states_dir)!r}))\n"
            "print(json.dumps(save))\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", script], capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0, f"Subprozess fehlgeschlagen: {result.stderr}"
        produced = json.loads(result.stdout)
        assert produced == block, "frischer Subprozess muss ueber den Produktleser denselben Save lesen."

        # Ergaenzend (in-process, "fuer eine Tischanfrage verwenden"): eine
        # NEUE TuiSession-Instanz (simuliert einen Neustart des Clients)
        # loest ueber `_resolve_member` dieselbe Figur auf, OHNE
        # Python-Objektzustand aus der obigen Session zu teilen.
        fresh_guest = _build_guest(
            root, guest_id=guest_id, run_dir=run_dir, states_dir=states_dir,
            gm_transport_factory=_spy_gm_factory, printed=[],
        )
        resolved = fresh_guest._resolve_member(guest_id)
        assert resolved is not None and resolved[1] == char_id, resolved


def test_f4_fehlende_abgelehnte_fremde_grant_kein_gm_aufruf_kein_save():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        write_test_profile(run_dir, max_turns=200)
        operator_a, operator_b, guest_id = "betreiber_a", "betreiber_b", "gast_f4_neg"

        host_a = TuiSession(
            onboarding_dir=root / "host_a_onboarding", catalog_dir=root / "host_a_catalog",
            participant_id=operator_a, print_fn=lambda s: None,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH, host_capable=True,
        )
        host_b = TuiSession(
            onboarding_dir=root / "host_b_onboarding", catalog_dir=root / "host_b_catalog",
            participant_id=operator_b, print_fn=lambda s: None,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH, host_capable=True,
        )
        guest_printed: list = []
        guest = _build_guest(
            root, guest_id=guest_id, run_dir=run_dir, states_dir=states_dir,
            gm_transport_factory=_spy_gm_factory, printed=guest_printed,
        )

        # (a) fehlend: nie angefragt.
        guest._cmd_gast_erschaffung_dialog([operator_a])
        assert any("kein gueltiger Betreiber-Grant" in p for p in guest_printed), guest_printed

        # (b) abgelehnt.
        guest._cmd_gast_erschaffung_anfragen([operator_a])
        host_a._cmd_gast_erschaffung_ablehnen([guest_id])
        guest_printed.clear()
        guest._cmd_gast_erschaffung_dialog([operator_a])
        assert any("kein gueltiger Betreiber-Grant" in p for p in guest_printed), guest_printed

        # (c) fremd: Betreiber B kann eine an A adressierte Anfrage nicht
        # entscheiden.
        guest._cmd_gast_erschaffung_anfragen([operator_a])
        host_b_printed: list = []
        host_b.print_fn = host_b_printed.append  # type: ignore[attr-defined]
        try:
            creation_grants.decide_creation_request(
                run_dir, operator_id=operator_b, guest_id=guest_id, approve=True,
            )
            raise AssertionError("decide_creation_request haette bei fremdem Betreiber ablehnen muessen.")
        except creation_grants.CreationGrantError:
            pass

        # (d) fremd (Dialogseite): Grant existiert fuer operator_a, der
        # Gast ruft den Dialog aber mit operator_b auf.
        host_a._cmd_gast_erschaffung_annehmen([guest_id])
        guest_printed.clear()
        guest._cmd_gast_erschaffung_dialog([operator_b])
        assert any("kein gueltiger Betreiber-Grant" in p for p in guest_printed), guest_printed

        # In KEINEM der obigen Faelle wurde jemals ein Save veroeffentlicht.
        assert catalog.list_for_participant(guest.catalog_dir, guest_id) == []
        assert not (run_dir / "current_saves" / f"{guest_id}.json").exists()


def test_f4_host_capable_ist_nie_ein_bypass():
    # Strukturell: `host_capable` taucht im Grant-Modul an KEINER Stelle
    # auf (grep-belegt, echte Assertion ueber inspect.getsource -- analog
    # altem O5-Test fuer creation_service/onboarding).
    import inspect
    src = inspect.getsource(creation_grants)
    assert "host_capable" not in src, "host_capable darf in creation_service.py (Grant-Modul) nicht auftauchen."

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        write_test_profile(run_dir, max_turns=200)
        operator_id, guest_id = "betreiber_hc", "gast_hc"

        guest_printed: list = []
        # BEWUSST host_capable=True auf der Gastseite -- die Kapazitaets-
        # rolle alleine darf NIE als Freigabe durchgehen, die Autoritaet
        # kommt ausschliesslich aus dem Grant.
        pseudo_host_guest = TuiSession(
            onboarding_dir=root / "onboarding", catalog_dir=root / "catalog",
            participant_id=guest_id, print_fn=guest_printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=_spy_gm_factory, host_capable=True,
        )
        pseudo_host_guest._cmd_gast_erschaffung_dialog([operator_id])
        assert any("kein gueltiger Betreiber-Grant" in p for p in guest_printed), guest_printed
        assert catalog.list_for_participant(pseudo_host_guest.catalog_dir, guest_id) == []


def test_f4_abbruch_vor_annahme_plus_spaete_antwort_und_recovery_keine_veroeffentlichung():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        write_test_profile(run_dir, max_turns=200)
        operator_id, guest_id, char_id = "betreiber_f4abb", "gast_f4abb", "CHR-GASTF4ABB-001"

        host = TuiSession(
            onboarding_dir=root / "host_onboarding", catalog_dir=root / "host_catalog",
            participant_id=operator_id, print_fn=lambda s: None,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH, host_capable=True,
        )
        gm = _AskOnceThenNeverGm()
        guest_printed: list = []
        guest = _build_guest(
            root, guest_id=guest_id, run_dir=run_dir, states_dir=states_dir,
            gm_transport_factory=lambda: gm, printed=guest_printed,
        )

        guest._cmd_gast_erschaffung_anfragen([operator_id])
        host._cmd_gast_erschaffung_annehmen([guest_id])
        onboarding_key = creation_grants.guest_onboarding_key(guest_id, 1)

        # Dialog beginnt (Entwurf -- noch keine verbindliche Annahme): der
        # erste GM-Turn ist nur eine Frage, kein Save. `_AskOnceThenNeverGm`
        # wuerde bei einem zweiten Turn werfen -- der Gast pausiert
        # (lokales '/pause', KEINE Antwort an die SL), der Dialog bleibt
        # offen/fortsetzbar, kein zweiter Turn.
        guest._input = _fixed_input("/pause")
        guest._cmd_gast_erschaffung_dialog([operator_id])
        assert gm.calls == 1, f"genau ein Turn erwartet (Entwurf), calls={gm.calls}"
        state = onboarding.peek(guest.onboarding_dir, onboarding_key)
        assert state is not None and state.status == "in_progress", state

        # F4 §4: expliziter, durabler Abbruch GENAU dieser Operation.
        guest._cmd_gast_erschaffung_abbrechen([operator_id])
        state_after_abandon = onboarding.peek(guest.onboarding_dir, onboarding_key)
        assert state_after_abandon is not None and state_after_abandon.status == "abandoned", state_after_abandon

        # Spaete Antwort/Recovery/Korrektur duerfen den aufgegebenen
        # Entwurf NICHT als Figur veroeffentlichen -- derselbe Durchgriff,
        # den `run_admitted_creation_dialog` bei einer verspaetet
        # eintreffenden gueltigen Antwort normalerweise machen wuerde.
        from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator
        late_block = full_v7_save(char_id, name="Spaet")
        try:
            onboarding.complete_with_save(
                guest.onboarding_dir, onboarding_key, late_block, ZeitrissHarvestValidator(), char_id,
            )
            raise AssertionError("complete_with_save haette nach Abbruch ValueError werfen muessen.")
        except ValueError as e:
            assert "abandoned" in str(e) or "abgebrochen" in str(e), str(e)
        assert onboarding.peek(guest.onboarding_dir, onboarding_key).final_save is None

        # Dieselbe (jetzt veraltete) Freigabe autorisiert keine erneute
        # Wiederaufnahme mehr -- 0 GM-Aufrufe fuer einen neuen Dialogversuch.
        spy_guest = _build_guest(
            root, guest_id=guest_id, run_dir=run_dir, states_dir=states_dir,
            gm_transport_factory=_spy_gm_factory, printed=guest_printed,
        )
        guest_printed.clear()
        spy_guest._cmd_gast_erschaffung_dialog([operator_id])
        assert any("kein gueltiger Betreiber-Grant" in p for p in guest_printed), guest_printed
        assert catalog.list_for_participant(guest.catalog_dir, guest_id) == []

        # Eine ECHTE neue Betreiberfreigabe (neue Generation) startet
        # dagegen einen frischen, unberuehrten Vorgang -- der Gast muss
        # dafuer (wie beim allerersten Mal) erneut eine Anfrage stellen,
        # eine bereits verbrauchte Freigabe autorisiert keine neue Runde.
        guest._cmd_gast_erschaffung_anfragen([operator_id])
        host._cmd_gast_erschaffung_annehmen([guest_id])
        record = creation_grants.grant_status(run_dir, guest_id)
        assert record["generation"] == 2, record
        new_onboarding_key = creation_grants.guest_onboarding_key(guest_id, 2)
        assert onboarding.peek(guest.onboarding_dir, new_onboarding_key) is None


def test_f4_unterbrochene_publikation_idempotenter_retry():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        write_test_profile(run_dir, max_turns=200)
        operator_id, guest_id, char_id = "betreiber_f4ret", "gast_f4ret", "CHR-GASTF4RET-001"
        block = full_v7_save(char_id, name="Retry")

        host = TuiSession(
            onboarding_dir=root / "host_onboarding", catalog_dir=root / "host_catalog",
            participant_id=operator_id, print_fn=lambda s: None,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH, host_capable=True,
        )
        gm = _OneShotCreationGm(block)
        guest_printed: list = []
        guest = _build_guest(
            root, guest_id=guest_id, run_dir=run_dir, states_dir=states_dir,
            gm_transport_factory=lambda: gm, printed=guest_printed,
        )
        guest._cmd_gast_erschaffung_anfragen([operator_id])
        host._cmd_gast_erschaffung_annehmen([guest_id])

        # Simuliert eine unterbrochene Veroeffentlichung: der Erschaffungs-
        # Claim + die Katalogregistrierung + das Figurenarchiv sind bereits
        # real geschrieben (wie bei einem Prozess, der GENAU zwischen
        # `store_figure_save` und der Current-/Persona-State-Publikation
        # abgestuerzt ist) -- Current/`bind_for_section` fehlen noch.
        attempt_key = creation_grants.guest_attempt_claim_key(guest_id)
        onboarding.record_attempt_claim(guest.onboarding_dir, attempt_key, generation=1, char_id=char_id)
        catalog.register(guest.catalog_dir, catalog.CatalogEntry(
            participant_id=guest_id, chrononaut_id=char_id, persona_key=guest_id,
        ))
        catalog.store_figure_save(guest.catalog_dir, guest_id, char_id, block)
        from mmo_sim.core import store as core_store
        assert catalog.active_chrononaut_id(guest.catalog_dir, guest_id) is None

        # Retry: derselbe Abschluss, dieselben bereits empfangenen Bytes,
        # KEIN zweiter GM-Aufruf (GM bleibt im `_OneShotCreationGm`
        # komplett unangetastet -- 0 Calls bis hierhin).
        assert gm.calls == 0
        guest._finish_granted_guest_creation(block, 1)

        # Jetzt vollstaendig abgeschlossen, idempotent (keine doppelten
        # Katalogeintraege, derselbe char_id/Inhalt).
        entries = catalog.list_for_participant(guest.catalog_dir, guest_id)
        assert len(entries) == 1 and entries[0].chrononaut_id == char_id, entries
        assert catalog.active_chrononaut_id(guest.catalog_dir, guest_id) == char_id
        from mmo_sim.core.persona_state import PersonaStateStore
        ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
        published = core_store.load_current_save(run_dir, guest_id, ps_store, states_dir=states_dir)
        assert published == block, "Retry haette die Current-Publikation nachholen muessen."

        # Ein zweiter, redundanter Retry-Aufruf (z.B. doppelte Zustellung
        # derselben Abschlussanweisung) bleibt ein reines No-op, kein
        # Konflikt/HOLD.
        guest_printed.clear()
        guest._finish_granted_guest_creation(block, 1)
        assert not any("angehalten" in p for p in guest_printed), guest_printed
        assert len(catalog.list_for_participant(guest.catalog_dir, guest_id)) == 1


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
