#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_betreiber_o6_autoritaet_und_spectator_2026_11_03.py --
ZR-BETREIBER-GASTERSCHAFFUNG-20261103-R1, O6 (design.md §1a/§4/§6).

Zwei getrennte Grenzen:

1. Autoritaet (`table_admission.request_table_stop`): ein FALSCHER
   `operator_id` (nicht der persistierte Host) UND ein korrekter Host mit
   einem NICHT gebundenen/falsch gebundenen `table_id`-Ziel werden BEIDE mit
   `OperatorAuthorityError` abgelehnt, OHNE jeden Write (kein Stop-File).
   Erst der korrekte Host MIT korrekt gebundenem Ziel setzt den Stop real.
2. `store.spectator_view`: strikte Whitelist -- ein Tisch mit vollstaendig
   befuellten privaten Feldern (`chrononaut_ids`, `operator_meta` inkl.
   `offer_log`/Secret-aehnlichem Marker, `sl_log`-Eintraegen mit privaten
   Nebenkeys wie `save_payload`/`chat_id`/`gm_request_id`/`origin_source`/
   `leader_message`/`origin_raw_input`) liefert NIE eines dieser privaten
   Felder/Keys zurueck -- negativ-assertiert als Dict-Keys UND als
   String-Scan ueber das serialisierte Ergebnis (Belt-and-Suspenders gegen
   eine versehentlich mitkopierte verschachtelte Struktur). `table_messages`
   ist der private Absprachekanal (design.md §4: "privater Absprachekanal")
   und wird ebenfalls AUSGESCHLOSSEN -- der Zuschauer-Feed speist sich
   ausschliesslich aus oeffentlicher SL-Erzaehlung (`sl_log`)."""
from __future__ import annotations

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

import mmo_sim.core.admission as admission  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
import mmo_sim.core.table_admission as table_admission  # noqa: E402


def test_o6_falscher_operator_id_wird_abgelehnt_kein_write():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td)
        table_admission.offer_table(run_dir, host_id="hostA", table_key="o6-key")
        table_admission.bind_section(run_dir, table_key="o6-key", host_id="hostA", section_id="sec-1")
        try:
            table_admission.request_table_stop(
                run_dir, table_key="o6-key", operator_id="imposter", table_id="sec-1",
                reason="sollte nie geschrieben werden",
            )
            raise AssertionError("OperatorAuthorityError haette hier werfen muessen (fremder operator_id).")
        except table_admission.OperatorAuthorityError:
            pass
        stopped, _reason = admission.read_table_stop(run_dir, "sec-1")
        assert stopped is False, "ein abgelehnter Stop-Versuch darf KEINE Datei hinterlassen."


def test_o6_korrekter_host_aber_falsches_bindungsziel_wird_abgelehnt():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td)
        table_admission.offer_table(run_dir, host_id="hostB", table_key="o6-key2")
        table_admission.bind_section(run_dir, table_key="o6-key2", host_id="hostB", section_id="sec-bound")
        try:
            table_admission.request_table_stop(
                run_dir, table_key="o6-key2", operator_id="hostB", table_id="sec-ANDERS",
                reason="sollte nie geschrieben werden",
            )
            raise AssertionError(
                "OperatorAuthorityError haette hier werfen muessen (korrekter Host, "
                "aber table_id stimmt nicht mit der gebundenen section_id ueberein)."
            )
        except table_admission.OperatorAuthorityError:
            pass
        assert admission.read_table_stop(run_dir, "sec-ANDERS") == (False, None)
        assert admission.read_table_stop(run_dir, "sec-bound") == (False, None)


def test_o6_korrekter_host_und_ziel_setzt_den_stop_real():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td)
        table_admission.offer_table(run_dir, host_id="hostC", table_key="o6-key3")
        table_admission.bind_section(run_dir, table_key="o6-key3", host_id="hostC", section_id="sec-ok")
        table_admission.request_table_stop(
            run_dir, table_key="o6-key3", operator_id="hostC", table_id="sec-ok",
            reason="echter Betreiber-Stop.",
        )
        stopped, reason = admission.read_table_stop(run_dir, "sec-ok")
        assert stopped is True and reason == "echter Betreiber-Stop.", (stopped, reason)


_PRIVATE_SECRET_MARKER = "GEHEIM-NIE-IM-SPECTATOR-9f3c"


def _table_with_private_payload(run_dir: Path) -> store.Table:
    table = store.Table(
        table_id="o6-privacy-tisch", leader="gm_persona", members=["gm_persona", "held_anna"],
        chrononaut_ids={"gm_persona": "chrono-gm", "held_anna": "chrono-anna"},
        run_dir=run_dir,
        operator_meta={
            "operator_id": "betreiber1",
            "offer_log": [{"type": "offer", "secret": _PRIVATE_SECRET_MARKER}],
            "derivation_reason": "test",
            "source_offer_id": "o1",
            "dissenters": {},
        },
    )
    table.sl_log.append({
        "turn_idx": 1, "content": "Oeffentliche SL-Erzaehlung.",
        "save_payload": {"secret": _PRIVATE_SECRET_MARKER},
        "chat_id": _PRIVATE_SECRET_MARKER, "gm_request_id": _PRIVATE_SECRET_MARKER,
        "origin_source": _PRIVATE_SECRET_MARKER, "leader_message": _PRIVATE_SECRET_MARKER,
        "origin_raw_input": _PRIVATE_SECRET_MARKER,
    })
    # Direkt am Objekt angehaengt (kein Disk-Roundtrip noetig fuer einen
    # reinen Projektionstest) -- identische Form wie `post_table_message`
    # tatsaechlich schreibt (store.py:710: `{"from": persona_key, "text": text}`).
    table.table_messages.append({"from": "held_anna", "text": "Lass uns nach links gehen."})
    return table


def test_o6_spectator_view_enthaelt_keine_privaten_felder():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td)
        table = _table_with_private_payload(run_dir)

        view = store.spectator_view(table)

        # `table_messages` ist der private Absprachekanal (design.md §4:
        # "privater Absprachekanal") und darf NIE in den Zuschauer-Feed --
        # genau wie chrononaut_ids/operator_meta eine verbotene Top-Level-Key.
        forbidden_top_level_keys = {"chrononaut_ids", "operator_meta", "table_messages"}
        assert forbidden_top_level_keys.isdisjoint(view.keys()), view.keys()

        for entry in view["sl_log"]:
            forbidden_entry_keys = {
                "save_payload", "chat_id", "gm_request_id", "origin_source",
                "leader_message", "origin_raw_input",
            }
            assert forbidden_entry_keys.isdisjoint(entry.keys()), entry

        # Belt-and-suspenders: das gesamte serialisierte Ergebnis darf den
        # Geheim-Marker an KEINER Stelle tragen -- auch nicht verschachtelt
        # ueber einen Feldnamen, den diese Pruefung nicht einzeln kennt.
        serialized = json.dumps(view, ensure_ascii=False)
        assert _PRIVATE_SECRET_MARKER not in serialized, serialized

        # table_messages ist KEIN Zuschauerinhalt -- der Betreiber-Stream
        # speist sich ausschliesslich aus oeffentlicher SL-Erzaehlung
        # (O6/design.md §4). Der private Text darf an KEINER Stelle auftauchen.
        assert "table_messages" not in view, view.keys()
        assert "Lass uns nach links gehen." not in serialized, serialized
        assert view["sl_log"] == [{"turn_idx": 1, "content": "Oeffentliche SL-Erzaehlung."}]
        assert view["members"] == ["gm_persona", "held_anna"]
        assert view["leader"] == "gm_persona"
        assert view["table_id"] == "o6-privacy-tisch"


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
