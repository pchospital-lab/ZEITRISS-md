#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_q04_round_setup_connects_new_person_2026_10_05.py —
Q04 (REVIEW.md R02, 05.10.2026, ZEITRISS Terminal UX-1, W12-Nacharbeit).

Negative Altprobe (dokumentiert, nicht erneut ausgefuehrt): vor dieser
Aenderung registrierte der Rundenassistent eine neue Person (`neu:Ben`),
brach aber ab, sobald diese noch keine Figur hatte, und verlangte einen
komplett SEPARATEN Teilnehmerdurchgang samt erneuter Rundeneinrichtung
(s. REVIEW.md Q04, `evidence/counterprobes/Q04_NEW_PERSON_ROUND_GAP` im
Review-Paket).

Positive Regression (dieser Test): `_local_round_confirm_figure()` fuer
eine figurlose Person verbindet jetzt den vorhandenen Registrierungs-/
Fokus-/Katalog-/Importweg (Fokusbestaetigung ueber `_local_round_handoff`,
DANACH die bestehende Erschaffungsflaeche `_cmd_menu_charaktere` UNTER DER
ID dieser Person) -- kein manuell editiertes JSON, keine zweite
Profilautoritaet, kein Liveanbieterassistent (synthetischer Fake-GM).

Pure Python, nur `assert`, synthetische Daten/Temp-Dirs."""
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
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _full_v7_fixture import upgrade_narrow_save  # noqa: E402

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402
import _a24_local_support as sup  # noqa: E402

_FIX = _REPO_ROOT / "internal" / "qa" / "harness" / "lobby" / "fixtures" / "saves"


class _FakeGm:
    """Liefert SOFORT im ersten Call den gueltigen v7-Save-Block -- ein
    einziger echter Zug reicht bis zum Abschluss (derselbe Musteraufbau
    wie `test_m3_tui.py`/`test_ux1_q07_...`, kein Liveanbieterassistent)."""

    def __init__(self, save_block: dict):
        self.save_block = save_block
        self.calls: list[tuple[int, str]] = []

    def turn(self, idx, text):
        self.calls.append((idx, text))
        return {"content": "```json\n" + json.dumps(self.save_block) + "\n```"}


def _scripted_input(values):
    q = list(values)

    def input_fn(prompt: str = "") -> str:
        if q:
            return q.pop(0)
        raise EOFError()

    return input_fn


def test_q04_new_person_without_figure_is_connected_not_aborted():
    """Kernreproduktion: eine frisch registrierte Person OHNE Figur fuehrt
    NICHT mehr sofort zum Abbruch -- Fokusbestaetigung + Erschaffung UNTER
    ihrer eigenen ID schliessen die Luecke innerhalb desselben Durchgangs."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        registry_dir = root / "registry"
        run_dir, states_dir = root / "run", root / "states"
        onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
        run_dir.mkdir(parents=True, exist_ok=True)
        states_dir.mkdir(parents=True, exist_ok=True)
        write_test_profile(run_dir)

        # 'neu:Ben' -- der Produktweg selbst registriert ueber dieselbe
        # Registry (`_local_round_select_humans`); hier direkt nachgebaut,
        # um den Fokus auf die Figur-Luecke danach zu legen.
        new_person = sup.register_human(registry_dir, "Ben")
        ben_id = new_person.participant_id

        save_block = upgrade_narrow_save(json.loads((_FIX / "sniper.json").read_text(encoding="utf-8")))
        gm = _FakeGm(save_block)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir, catalog_dir, "leader",
            input_fn=_scripted_input([
                "j",  # Fokusbestaetigung (_local_round_handoff): Terminal an Ben uebergeben
                "1",  # Charaktere-Untermenue: [1] Auswaehlen/neu erstellen
                "j",  # abschliessende Figurbestaetigung "'ben...' spielt '...' -- bestaetigen?"
            ]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=sup.SCHEMA,
            gm_transport_factory=lambda: gm,
        )

        confirmed = session._local_round_confirm_figure(ben_id)
        out = "\n".join(printed)

        assert confirmed is True, out
        # Kein Abbruch mehr -- die alte, endgueltige Blockermeldung darf
        # NICHT mehr erscheinen.
        assert "bitte zuerst im eigenen Teilnehmer-Durchgang" not in out, out
        # Ein echter Erschaffungszug (Fake-GM) ist tatsaechlich gefolgt.
        assert len(gm.calls) == 1, gm.calls
        assert "Erschaffung abgeschlossen" in out, out

        from mmo_sim.domain.zeitriss import onboarding
        state = onboarding.peek(onboarding_dir, ben_id)
        assert state is not None and state.status == "completed", state

        resolved = session._resolve_member(ben_id)
        assert resolved is not None, "Ben muss nach der Verbindung eine echte Figur haben"


def test_q04_focus_handoff_declined_stays_honest_no_bypass():
    """Erhaltungsprobe: lehnt die Person die Fokusuebergabe ab, bleibt dies
    ein klarer Rueckweg (kein KI-Ersatz, keine Dummyfigur, kein stiller
    Weiterspielen ohne echte Figur)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        registry_dir = root / "registry"
        onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"

        new_person = sup.register_human(registry_dir, "Ben")
        ben_id = new_person.participant_id

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir, catalog_dir, "leader",
            input_fn=_scripted_input(["n"]),  # Fokusuebergabe abgelehnt
            print_fn=printed.append,
        )
        confirmed = session._local_round_confirm_figure(ben_id)
        out = "\n".join(printed)
        assert confirmed is False, out
        assert "bitte zuerst im eigenen Teilnehmer-Durchgang" in out, out

        from mmo_sim.domain.zeitriss import onboarding
        assert onboarding.peek(onboarding_dir, ben_id) is None, "keine Figur, kein stiller Fortschritt"


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
