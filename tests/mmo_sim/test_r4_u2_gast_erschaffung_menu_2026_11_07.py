#!/usr/bin/env python3
"""
tests/mmo_sim/test_r4_u2_gast_erschaffung_menu_2026_11_07.py
ZR-VOLLENDUNG-OHNE-LAN-NACHZUG-20261107-R4 (U2, PLAYER-UX-REVIEW.md F2,
01_NACHZUG.md U2 Punkt 2/3).

Vorher waren die Betreiberentscheidung (annehmen/ablehnen) UND der
anschliessende eigene Gastdialog NUR ueber die rohen Aliase
`gast-erschaffung-annehmen/-ablehnen/-dialog <id>` erreichbar -- der
`[charaktere]`-Menuecode kannte dafuer keine entsprechende normale
Auswahl (General-Befund F2). Dieser Test beweist am echten
`TuiSession._cmd_menu_charaktere()`-Dispatch, dass eine komplette
Gast-Erschaffung GENAU EINMAL ueber nummerierte Menues laeuft, OHNE dass
der Testcode selbst einen `gast-erschaffung-*`-Wortbefehl eingibt:

1. Der Gast stellt seine Anfrage ueber `[charaktere] -> [4]` (bestehender
   Dienst `_cmd_gast_erschaffung_anfragen_menu`, unveraendert).
2. Das `[charaktere]`-Menue des Gastes zeigt danach zusaetzlich
   `[5] Eigenen Erschaffungsdialog fortsetzen` -- VOR der Freigabe meldet
   dies ehrlich 'kein gueltiger Betreiber-Grant' (kein Bypass).
3. Der figurfreie Betreiber sieht ueber `[charaktere] -> [4]` die offene
   Anfrage NUMMERIERT (`creation_service.list_requested_for_operator`) und
   entscheidet sie nummeriert (`[1] annehmen`) -- derselbe unveraenderte
   `_cmd_gast_erschaffung_annehmen` dahinter (`_require_host` bleibt aktiv).
4. Danach fuehrt `[charaktere] -> [5]` beim Gast den ECHTEN, freigegebenen
   Dialog zu Ende (ein einziger kontrollierter Fake-GM-Call, derselbe
   Musteraufbau wie `test_zr_betreiber_r2_f4_gast_erschaffung_produktweg_
   2026_11_04.py`) und veroeffentlicht die persoenliche Figur.

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs.
Null echte GM-/Persona-Modellcalls (ein einziger kontrollierter
Fake-GM-Call am vorhandenen Modellrand)."""
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

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import creation_service as creation_grants  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


class _OneShotCreationGm:
    """Liefert GENAU EINE vorgegebene v7-Save-Antwort im ERSTEN Turn --
    derselbe Musteraufbau wie
    `test_zr_betreiber_r2_f4_gast_erschaffung_produktweg_2026_11_04.py`."""

    def __init__(self, block: dict):
        self._block = block
        self.calls = 0

    def turn(self, turn_idx: int, user_text: str, **kw) -> dict:
        self.calls += 1
        if self.calls > 1:
            raise AssertionError("_OneShotCreationGm: unerwarteter zweiter Turn.")
        content = "```json\n" + json.dumps(self._block, ensure_ascii=False) + "\n```"
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "u2-fake"}


def _scripted_input(values):
    q = list(values)

    def input_fn(prompt: str = "") -> str:
        if q:
            return q.pop(0)
        raise EOFError()

    return input_fn


def test_full_gast_erschaffung_journey_uses_only_numbered_menus():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        write_test_profile(run_dir, max_turns=200)
        operator_id, guest_id = "betreiber_u2", "gast_u2"
        char_id = "CHR-U2MENU-001"
        gm = _OneShotCreationGm(full_v7_save(char_id, name="Mira"))

        guest_printed: list[str] = []
        guest = TuiSession(
            onboarding_dir=root / "onboarding_gast", catalog_dir=root / "catalog_gast",
            participant_id=guest_id, print_fn=guest_printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: gm, host_capable=False,
            input_fn=_scripted_input(["4", operator_id]),
        )
        # (1) Anfrage ausschliesslich ueber die nummerierte Charaktere-
        # Menuefuehrung -- kein roher 'gast-erschaffung-anfragen'-Aufruf.
        guest._cmd_menu_charaktere()
        assert "Erschaffungsanfrage an Betreiber" in "\n".join(guest_printed), guest_printed
        assert creation_grants.grant_status(run_dir, guest_id)["status"] == "requested"

        # (2) Vor Freigabe: '[5]' erscheint jetzt im Menue, meldet aber
        # ehrlich eine fehlende Freigabe -- kein Bypass, kein GM-Aufruf.
        guest_printed.clear()
        guest._input = _scripted_input(["5"])
        guest._cmd_menu_charaktere()
        out = "\n".join(guest_printed)
        assert "[5] Eigenen Erschaffungsdialog fortsetzen" in out, out
        assert "kein gueltiger Betreiber-Grant" in out, out
        assert gm.calls == 0, "vor der Freigabe darf KEIN GM-Aufruf stattfinden"

        # (3) Betreiber (figurfrei, host_capable) entscheidet NUMMERIERT
        # ueber die tatsaechlich an ihn gerichtete offene Anfrage -- kein
        # roher 'gast-erschaffung-annehmen <id>'-Aufruf im Testcode.
        operator_printed: list[str] = []
        operator = TuiSession(
            onboarding_dir=root / "onboarding_betreiber", catalog_dir=root / "catalog_betreiber",
            participant_id=operator_id, print_fn=operator_printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            host_capable=True,
            input_fn=_scripted_input(["4", "1", "1"]),
        )
        operator._cmd_menu_charaktere()
        op_out = "\n".join(operator_printed)
        assert f"[1] {guest_id}" in op_out, op_out
        assert f"Gast '{guest_id}' freigegeben" in op_out, op_out
        record = creation_grants.grant_status(run_dir, guest_id)
        assert record["status"] == "approved" and record["generation"] == 1, record

        # (4) Gast fuehrt ueber dasselbe '[5]' jetzt den ECHTEN, bedienten
        # Dialog zu Ende -- GENAU EIN Fake-GM-Call, persoenliche Figur
        # wird veroeffentlicht.
        guest_printed.clear()
        guest._input = _scripted_input(["5"])
        guest._cmd_menu_charaktere()
        out2 = "\n".join(guest_printed)
        assert gm.calls == 1, gm.calls
        assert "Erschaffung abgeschlossen" in out2, out2

        resolved = guest._resolve_member(guest_id)
        assert resolved is not None, "Gast muss nach der menuebedienten Freigabe eine echte Figur haben"
        assert resolved[1] == char_id, resolved


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
