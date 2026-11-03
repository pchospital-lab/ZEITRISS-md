#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_betreiber_o1_operator_rollenentkopplung_2026_11_03.py
-- ZR-BETREIBER-GASTERSCHAFFUNG-20261103-R1, O1 (design.md §2/§4, echte
TUI-Verdrahtung in `ui/tui.py:_cmd_local_round`).

Treibt die ECHTE Kommando-Oberflaeche ueber `TuiSession._cmd_local_round`
(Aufruf wie ueber 'l operator lead:persona:<id>' am Terminal): 'operator'
ALS FUEHRENDES Token markiert den Betreibermodus, 'lead:persona:gm_nova'
macht die Persona 'gm_nova' zum Leader. Modellrand-Double: `_OneShotDebrief
Gm` (in-process GM-Transport, EHRLICH als Double gekennzeichnet) liefert im
ersten Turn direkt den Debrief inkl. Abschluss-Marker + gueltigem v7-Save
fuer die Persona, damit die Runde in GENAU einem Turn durchlaeuft.

Asserts (design.md §2/§4, LINUS-BRIEF.md §A/§B):
1. Der Operator landet NICHT in `table.members`/`chrononaut_ids` (O1).
2. `table.operator_meta['operator_id']` == Operator-Teilnehmer-ID, GETRENNT
   von `members` (O1).
3. Kein Operator-Save/-Harvest/-Phantomspieler: `complete_section`/Harvest
   lief nur ueber die Persona -- kein `current_saves/<operator>.json`, kein
   Onboarding-Abschluss fuer den Operator.
4. Die automatische Spektator-Ausgabe (`_print_spectator_view`, nach dem
   Rundenende aufgerufen) erscheint auf dem Betreiberterminal ('[Zuschauer]'
   -praefigierte Zeilen) -- UND das gesamte Terminal-Protokoll enthaelt NIE
   den `operator_view`-exklusiven Feldnamen (`chrononaut_ids`/`operator_meta`
   als Textfragment).
5. Echte Filterprobe (kein Vakuum): ein Geheim-Marker wird REAL in ein
   privates Feld (`operator_meta`) der Table injiziert und der oeffentliche
   Zuschauer-Feed (`core_store.spectator_view`) daraus gerendert -- die
   Whitelist muss den Marker rauswerfen (er darf im Feed NICHT auftauchen)."""
from __future__ import annotations

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
from _zr_betreiber_fixtures_2026_11_03 import (  # noqa: E402
    SCHEMA_PATH, AcceptLeadDriver, bootstrap_own_persona, register_own_figure,
)

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

_PRIVATE_SECRET_MARKER = "GEHEIM-OPERATOR-TEST-4b71"


class _OneShotDebriefGm:
    """Modellrand-Double (EHRLICH gekennzeichnet): liefert im ERSTEN Turn
    bereits den vollstaendigen Debrief (Prosa + v7-Save-Block + Abschluss-
    Marker) -- die Betreiberrunde durchlaeuft GENAU einen Turn."""

    def __init__(self, persona_save: dict):
        self._persona_save = persona_save
        self.calls = 0

    def turn(self, turn_idx: int, user_text: str) -> dict:
        import json
        self.calls += 1
        content = (
            "Szene 1: Die Heldin erkundet die Ruine.\n"
            f"```json\n{json.dumps(self._persona_save)}\n```\n"
            f"{COMPLETION_MARKER}"
        )
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "o1-fake"}


def test_o1_operator_bleibt_ausserhalb_von_members_und_chrononaut_ids():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
        write_test_profile(run_dir, max_turns=200)

        operator_id = "betreiber_o1"
        persona_key = "gm_nova"
        persona_char_id = "CHR-O1-NOVA"

        bootstrap_own_persona(run_dir, states_dir, operator_id, persona_key)
        persona_save = register_own_figure(
            onboarding_dir, catalog_dir, persona_key, persona_char_id, run_dir=run_dir, states_dir=states_dir,
        )

        driver = AcceptLeadDriver(persona_key, play_replies=["Wir erkunden die Ruine."])
        gm = _OneShotDebriefGm(persona_save)

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=operator_id,
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=SCHEMA_PATH,
            gm_transport_factory=lambda: gm,
            persona_driver_factory=lambda pk: driver,
            host_capable=True,
        )
        try:
            # allow_operator_mode=True bildet exakt den frei getippten
            # 'l operator ...'-Dispatch (tui.py run(): choice=='l') nach --
            # nur dieser Pfad darf den 'operator'-Sentinel auswerten.
            section_id = session._cmd_local_round(
                ["operator", f"lead:persona:{persona_key}"], allow_operator_mode=True,
            )
        except EndOfInput:
            raise AssertionError(
                "unerwartete EndOfInput -- der Operator darf in diesem Modus an KEINEM Prompt "
                f"haengen (kein eigener Zug). printed={printed}"
            )

        assert section_id is not None, f"Betreibertisch haette entstehen muessen. printed={printed}"

        from mmo_sim.core import store as core_store
        table = core_store.Table.load(run_dir, section_id)

        # (1)+(2) O1: Operator NICHT in members/chrononaut_ids, GETRENNT in operator_meta.
        assert operator_id not in table.members, table.members
        assert operator_id not in table.chrononaut_ids, table.chrononaut_ids
        assert table.operator_meta.get("operator_id") == operator_id, table.operator_meta
        assert table.members == [persona_key], table.members
        assert persona_key in table.chrononaut_ids, table.chrononaut_ids

        # (3) kein Operator-Save/-Harvest/-Phantomspieler.
        operator_save_path = run_dir / "current_saves" / f"{operator_id}.json"
        assert not operator_save_path.exists(), "kein Operator-Save darf entstehen (strukturell kein Member)."
        from mmo_sim.domain.zeitriss import onboarding
        assert onboarding.peek(onboarding_dir, operator_id) is None, (
            "kein Onboarding-Datensatz fuer den Operator -- er hat nie eine Figur erschaffen."
        )
        # Persona-Save wurde real geerntet (Abschluss lief durch).
        persona_save_path = run_dir / "current_saves" / f"{persona_key}.json"
        assert persona_save_path.exists(), "die Persona-Figur haette real geerntet werden muessen."

        # (4) automatische Spektator-Ausgabe erscheint, NIE operator_view-Felder im Protokoll.
        zuschauer_lines = [p for p in printed if p.startswith("[Zuschauer]")]
        assert zuschauer_lines, f"Spektator-Ausgabe haette erscheinen muessen. printed={printed}"
        full_transcript = "\n".join(printed)
        assert "operator_meta" not in full_transcript, full_transcript
        assert "chrononaut_ids" not in full_transcript, full_transcript

        # (5) ECHTE Filterprobe (Abschluss-Critic-Befund 4: die alte
        # `_PRIVATE_SECRET_MARKER not in full_transcript`-Zeile war vakuum --
        # der Marker wurde nie injiziert). Jetzt wird er REAL in ein privates
        # Feld (`operator_meta`, nur Betreiber-sichtbar) der In-Memory-Table
        # gelegt und der OEFFENTLICHE Zuschauer-Feed daraus gerendert: die
        # Whitelist in `spectator_view` muss ihn rauswerfen.
        import json as _json
        table.operator_meta["_private_offer_marker"] = _PRIVATE_SECRET_MARKER
        spectator_payload = core_store.spectator_view(table)
        assert _PRIVATE_SECRET_MARKER not in _json.dumps(spectator_payload, ensure_ascii=False), (
            f"Geheim-Marker aus operator_meta leckte in den oeffentlichen Feed: {spectator_payload}"
        )


def test_o1_operator_sentinel_nur_ueber_frei_getippten_l_befehl():
    """Regression (Abschluss-Critic-Befund 2): der 'operator'-Sentinel darf
    NUR beim frei getippten 'l ...'-Kommando greifen, NIE bei roster-/setup-
    abgeleiteten `guest_tokens`. Sonst braechte ein ganz normaler
    menschlicher Mitspieler, der zufaellig/bewusst `--community operator`
    heisst und als erster Gast gelistet ist, den kompletten Tischstart ab
    (`--community` hat keine Reserved-Word-Pruefung, s. `lab/cli.py`).

    Deterministischer Strukturbeweis (kein voller Play-Lauf noetig, gleicher
    Stil wie der O5-`host_capable`-Check via `inspect`): (a) der Parameter
    `allow_operator_mode` existiert und defaultet auf False -> roster-/setup-
    Pfade (`_cmd_table_start`, `_cmd_local_round_setup`) werten den Sentinel
    nie aus; (b) der Sentinel-Zweig ist genau darauf gegated; (c) der frei
    getippte 'l'-Dispatch setzt `allow_operator_mode=True`."""
    import inspect
    from mmo_sim.ui.tui import TuiSession

    sig = inspect.signature(TuiSession._cmd_local_round)
    param = sig.parameters.get("allow_operator_mode")
    assert param is not None, "Parameter allow_operator_mode fehlt -- Sentinel-Gating nicht vorhanden."
    assert param.default is False, (
        f"allow_operator_mode muss auf False defaulten (roster/setup inert), ist {param.default!r}."
    )

    src = inspect.getsource(TuiSession._cmd_local_round)
    assert 'if allow_operator_mode and tokens and tokens[0] == "operator":' in src, (
        "Sentinel-Zweig ist nicht auf allow_operator_mode gegated."
    )

    run_src = inspect.getsource(TuiSession.run)
    assert "self._cmd_local_round(extra_tokens, allow_operator_mode=True)" in run_src, (
        "der frei getippte 'l'-Dispatch gibt allow_operator_mode=True nicht mehr weiter."
    )


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
