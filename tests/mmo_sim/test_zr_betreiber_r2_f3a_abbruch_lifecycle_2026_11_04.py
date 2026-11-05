#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_betreiber_r2_f3a_abbruch_lifecycle_2026_11_04.py --
ZR-BETREIBER-GASTERSCHAFFUNG-20261103-R2-NACHZUG, F3a (STOP-BOUNDARY.md B2
"der Stop wird nur zu einem dauerhaften HOLD; der geforderte Abbruch-
Lifecycle fehlt"): ein menschlich bestaetigter '/abbrechen' VOR der ersten
Abschlussentscheidung muss ein WIRKLICHER, dauerhafter Verwurf sein (nicht
Pause) -- die akzeptierte Gast-Startdatei bleibt bytegleich, die betroffene
Figurenbindung wird freigegeben, eine erneute Tischteilnahme ist ueber den
normalen Produktweg moeglich, und der Vorgang laesst sich NICHT durch
Neustart/Retry wiederbeleben.

Kern-Rueckhalt (bereits von Main geliefert, hier nur GENUTZT): der
gemeinsame atomare Entscheid-Slot (`core.admission.try_commit_table_
decision`/`read_table_decision`) UND `table_admission.request_table_stop`.
Dieser Treiber deckt den PRODUKT-/UI-Weg darueber: `/abbrechen` am
Spielzug-Prompt eines Betreiber-Tisches ruft jetzt `request_table_stop`
auf (statt nur zu pausieren), und der Rueckweg (`ui/tui.py:_run_table_
round`/`_finalize_genuine_table_abort`) gibt die Chrononaut-Bindung frei
und schliesst Store-Tisch + Admission-Record."""
from __future__ import annotations

import hashlib
import json
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

from mmo_sim.core import admission as core_admission  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core import table_admission  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


class _SpyGm:
    """Modellrand-Double: wirft SOFORT bei Aufruf -- '/abbrechen' VOR dem
    ersten Spielrequest darf NIEMALS einen GM-Request ausloesen (der
    Kontrolltoken wird VOR dem Versand ausgewertet, s. `_HumanDriver.
    decide()`)."""

    def __init__(self):
        self.calls = 0

    def turn(self, *a, **kw):
        self.calls += 1
        raise AssertionError("GM-Transport wurde aufgerufen -- '/abbrechen' haette VOR jedem Request greifen muessen.")


def _register_private_figure(onboarding_dir: Path, catalog_dir: Path, participant_id: str, char_id: str) -> dict:
    save = full_v7_save(char_id, name=participant_id, save_id=f"fixture-{participant_id}-001", level=1)
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
    ))
    return save


def _scripted_input(reply: str):
    calls = {"n": 0}

    def _fn(prompt: str = "") -> str:
        calls["n"] += 1
        return reply
    return _fn, calls


def test_f3a_abbrechen_vor_entscheidung_ist_echter_verwurf_mit_wiederteilnahme():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        host_onboarding, host_catalog = root / "host_onboarding", root / "host_catalog"
        guest_onboarding, guest_catalog = root / "guest_onboarding", root / "guest_catalog"
        write_test_profile(run_dir, max_turns=200)

        operator_id, guest_id, char_id = "betreiber_f3a", "gast_f3a", "CHR-GASTF3A"
        table_key = "mesaF3a"

        guest_save = _register_private_figure(guest_onboarding, guest_catalog, guest_id, char_id)

        guest_input, guest_calls = _scripted_input("/abbrechen")
        guest_printed: list[str] = []
        guest_session = TuiSession(
            onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id=guest_id,
            input_fn=guest_input, print_fn=guest_printed.append,
            run_dir=run_dir, host_capable=False,
        )

        host_printed: list[str] = []
        spy_gm = _SpyGm()
        host_session = TuiSession(
            onboarding_dir=host_onboarding, catalog_dir=host_catalog, participant_id=operator_id,
            print_fn=host_printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: spy_gm,
            host_capable=True,
        )

        host_session._cmd_table_offer([table_key])
        guest_session._cmd_table_request_join([table_key])
        host_session._cmd_table_accept([table_key, guest_id])
        host_session.register_guest_terminal(guest_id, guest_session)

        # Die ECHTE, bereits hostseitig veroeffentlichte Startfassung des
        # Gasts (s. `_cmd_table_accept`) -- das ist "seine akzeptierte
        # Anfangsdatei" im Sinne des Auftrags. sha256 VOR dem Abbruch.
        guest_save_path = run_dir / "current_saves" / f"{guest_id}.json"
        assert guest_save_path.exists(), "akzeptierte Gast-Startfassung muesste bereits vorliegen."
        sha_before = hashlib.sha256(guest_save_path.read_bytes()).hexdigest()

        try:
            host_session._cmd_table_start([table_key])
            raise AssertionError("ein echter Verwurf VOR dem ersten Zug muss ueber EndOfInput zurueckkehren.")
        except EndOfInput:
            pass

        assert spy_gm.calls == 0, "kein GM-Request vor dem bestaetigten Verwurf."
        assert guest_calls["n"] == 1, "der Gast hat genau einmal '/abbrechen' eingegeben."
        assert any("wirklich verworfen" in p for p in guest_printed), guest_printed

        record = table_admission.load_record(run_dir, table_key)
        section_id = record["section_id"]
        assert record["state"] == table_admission.STATE_CLOSED, record

        # (Durabilitaet 1) der gemeinsame atomare Entscheid-Slot ist auf
        # 'stopped' gefallen -- DIES ist die maßgebliche, durable Wahrheit
        # (Main-Kern, hier nur gelesen).
        decision = core_admission.read_table_decision(run_dir, section_id)
        assert decision is not None and decision.get("decision") == "stopped", decision

        table = core_store.Table.load(run_dir, section_id)
        assert table.status == "closed", table.status

        # sha256 NACH dem Abbruch -- unveraendert (kein Save, kein Rollback
        # bereits angenommenen Fortschritts, weil nie welcher entstand).
        sha_after = hashlib.sha256(guest_save_path.read_bytes()).hexdigest()
        assert sha_after == sha_before, (
            "die akzeptierte Gast-Startfassung haette bytegleich bleiben muessen."
        )

        # Bindungsfreigabe: der Chrononaut ist NICHT mehr an den toten
        # Tisch gesperrt.
        lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert lobby.is_locked(char_id) is None, (
            f"Chrononaut haette nach echtem Verwurf freigegeben werden muessen: "
            f"{lobby.is_locked(char_id)!r}"
        )

        # Wiederteilnahme ueber den normalen Produktweg: NEUER Tisch,
        # dieselbe Figur wird wieder angenommen (kein Lock-Konflikt mehr).
        table_key_2 = "mesaF3a-zwei"
        host_session._cmd_table_offer([table_key_2])
        guest_session._cmd_table_request_join([table_key_2])
        host_session._cmd_table_accept([table_key_2, guest_id])
        record_2 = table_admission.load_record(run_dir, table_key_2)
        assert record_2["roster"] == [operator_id, guest_id], record_2

        # (Durabilitaet 2) Neustart/Retry belebt den verworfenen Vorgang
        # NICHT: ein spaeterer Versuch, den gemeinsamen Entscheid-Slot
        # DESSELBEN (toten) Tisches auf 'plan_committed' zu drehen,
        # verliert gegen den bereits durabel gefallenen 'stopped'-Entscheid
        # -- derselbe Produktvertrag, den O3/O4 bereits fuer den
        # dedizierten '/stop'-Weg belegen, hier fuer den '/abbrechen'-Weg.
        revival_won, revival_decision = core_admission.try_commit_table_decision(
            run_dir, section_id, "plan_committed",
        )
        assert revival_won is False, "ein 'toter' Tisch darf NICHT nachtraeglich 'plan_committed' werden."
        assert revival_decision.get("decision") == "stopped", revival_decision


def test_f3a_pause_bleibt_unterscheidbar_von_echtem_abbruch_kein_entscheid():
    """Gegenprobe (02_NACHZUG F3a 'Pause wird NICHT als sauberer Abbruch
    ausgegeben'): '/pause' am selben Betreiber-Tisch setzt KEINEN
    Entscheid-Slot -- der Abschnitt bleibt real fortsetzbar, nicht
    verworfen."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        host_onboarding, host_catalog = root / "host_onboarding", root / "host_catalog"
        guest_onboarding, guest_catalog = root / "guest_onboarding", root / "guest_catalog"
        write_test_profile(run_dir, max_turns=200)

        operator_id, guest_id, char_id = "betreiber_f3a_p", "gast_f3a_p", "CHR-GASTF3AP"
        table_key = "mesaF3aPause"

        _register_private_figure(guest_onboarding, guest_catalog, guest_id, char_id)

        guest_input, guest_calls = _scripted_input("/pause")
        guest_printed: list[str] = []
        guest_session = TuiSession(
            onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id=guest_id,
            input_fn=guest_input, print_fn=guest_printed.append,
            run_dir=run_dir, host_capable=False,
        )
        host_printed: list[str] = []
        spy_gm = _SpyGm()
        host_session = TuiSession(
            onboarding_dir=host_onboarding, catalog_dir=host_catalog, participant_id=operator_id,
            print_fn=host_printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: spy_gm,
            host_capable=True,
        )
        host_session._cmd_table_offer([table_key])
        guest_session._cmd_table_request_join([table_key])
        host_session._cmd_table_accept([table_key, guest_id])
        host_session.register_guest_terminal(guest_id, guest_session)

        try:
            host_session._cmd_table_start([table_key])
            raise AssertionError("Pause muss ebenfalls ueber EndOfInput zurueckkehren.")
        except EndOfInput:
            pass

        assert spy_gm.calls == 0
        assert any("Kontrolliert pausiert" in p for p in guest_printed), guest_printed
        assert not any("wirklich verworfen" in p for p in guest_printed), guest_printed

        record = table_admission.load_record(run_dir, table_key)
        section_id = record["section_id"]
        # KEIN Entscheid gefallen -- '/pause' ist KEIN Abbruch.
        decision = core_admission.read_table_decision(run_dir, section_id)
        assert decision is None, f"'/pause' haette KEINEN Entscheid-Slot setzen duerfen: {decision}"
        # Tisch bleibt real offen/fortsetzbar (kein 'closed').
        assert record["state"] == table_admission.STATE_STARTED, record
        table = core_store.Table.load(run_dir, section_id)
        assert table.status != "closed", table.status


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
