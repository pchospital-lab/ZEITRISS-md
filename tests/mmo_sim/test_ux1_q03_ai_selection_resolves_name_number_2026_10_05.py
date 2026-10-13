#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_q03_ai_selection_resolves_name_number_2026_10_05.py —
Q03 (REVIEW.md R02, 05.10.2026, ZEITRISS Terminal UX-1, W12-Nacharbeit).

Negative Altprobe (dokumentiert, nicht erneut ausgefuehrt): vor dieser
Aenderung forderte `_local_round_select_ai()` weiterhin "Auswahl per ID"
und gab ROHE Tokens zurueck -- die Testeingabe `1` blieb das bedeutungslose
Token `1`, keine Auswahl aus dem angezeigten Bestand (s. REVIEW.md Q03,
`evidence/counterprobes/Q03_AI_ID_SELECTION` im Review-Paket).

Positive Regression (dieser Test): Eingabe `1`/Name waehlt tatsaechlich den
angezeigten Eintrag und loest in die vorhandene autoritative Persona-ID
(`pk`) auf. Technische ID-Eingabe bleibt ein gueltiger Experten-/
Kompatibilitaetsalias. Ein unbekanntes Token (weder Index noch Name noch
ID) bleibt unveraendert als freie Persona-ID durchgereicht (kein neues
Verbot).

Pure Python, nur `assert`, synthetische Daten/Temp-Dirs, 0 Persona-/GM-
Calls (reines Ansehen+Auswahl, wie UX03/UX10 verlangen)."""
from __future__ import annotations

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

from mmo_sim.ui.tui import TuiSession  # noqa: E402
import _a24_local_support as sup  # noqa: E402


class _ForbiddenPersonaFactory:
    def __call__(self, persona_key: str):
        raise AssertionError(f"Q03: reine Auswahl darf keinen Persona-Call ausloesen ({persona_key!r})")


class _ForbiddenGm:
    def turn(self, *a, **kw):
        raise AssertionError("Q03: reine Auswahl darf keinen GM-Call ausloesen")


def _session_with_community(root: Path):
    pid = "q03-tester"
    community_id = f"community-{pid}"
    env = sup.bootstrap_six_persona_community(root, community_id)
    written = sorted(env["bootstrap"].personas_written)
    assert written == ["cqb", "face", "medic", "pyro", "sniper", "tech"], written
    session = TuiSession(
        onboarding_dir=env["onboarding_dir"], catalog_dir=env["catalog_dir"], participant_id=pid,
        run_dir=env["run_dir"], states_dir=env["states_dir"], schema_path=env["schema"],
        gm_transport_factory=lambda: _ForbiddenGm(), persona_driver_factory=_ForbiddenPersonaFactory(),
    )
    return session, written


def test_q03_numeric_index_resolves_to_authoritative_persona_id():
    """Kernreproduktion: Eingabe '1' (erster angezeigter Eintrag) muss die
    tatsaechliche Persona-ID liefern, NICHT das rohe Token '1'."""
    with tempfile.TemporaryDirectory() as td:
        session, written = _session_with_community(Path(td))
        printed: list[str] = []
        session._print = printed.append
        # sorted(written) == ["cqb", "face", "medic", "pyro", "sniper", "tech"]
        # -> Index 1=cqb, 3=medic.
        session._input = lambda prompt="": "1 3"
        tokens = session._local_round_select_ai()
        assert tokens == ["cqb", "medic"], tokens
        assert "1" not in tokens, "Q03: das rohe Indextoken '1' darf nicht mehr als 'Auswahl' durchgehen"
        assert any("[1]" in p and "cqb" in p for p in printed), printed


def test_q03_display_name_resolves_case_insensitively():
    """Name-Auswahl: der angezeigte Name (`pk`) loest case-insensitiv in
    die autoritative ID auf (Grossschreibvariante 'TECH' -> 'tech') --
    Archetyp-/Herkunftsbeschreibung bleibt davon ausgenommen (mehrwortig,
    nicht eindeutig vom leerzeichengetrennten Mehrfachauswahlformat
    trennbar)."""
    with tempfile.TemporaryDirectory() as td:
        session, _written = _session_with_community(Path(td))
        session._print = lambda *_a: None
        session._input = lambda prompt="": "TECH"
        tokens = session._local_round_select_ai()
        assert tokens == ["tech"], tokens


def test_q03_technical_id_remains_valid_expert_alias():
    """Erhaltungsprobe: die bisherige, direkte ID-Eingabe bleibt weiterhin
    ein gueltiger (jetzt optionaler) Experten-/Kompatibilitaetsweg --
    bestehende Skripttests mit roher ID bleiben unveraendert gueltig."""
    with tempfile.TemporaryDirectory() as td:
        session, _written = _session_with_community(Path(td))
        session._print = lambda *_a: None
        session._input = lambda prompt="": "sniper tech"
        tokens = session._local_round_select_ai()
        assert tokens == ["sniper", "tech"], tokens


def test_q03_unknown_token_stays_free_persona_id_passthrough():
    """Kein neues Verbot: ein Token, das weder Index noch bekannter Name
    noch bekannte ID ist, bleibt unveraendert durchgereicht (freie
    Persona-ID ausserhalb der eigenen Community, z.B. Expertenfall)."""
    with tempfile.TemporaryDirectory() as td:
        session, _written = _session_with_community(Path(td))
        session._print = lambda *_a: None
        session._input = lambda prompt="": "irgendeine-fremde-id"
        tokens = session._local_round_select_ai()
        assert tokens == ["irgendeine-fremde-id"], tokens


def test_q03_duplicate_display_names_require_index_disambiguation():
    """Bei Dubletten (zwei Eintraege mit identischem Anzeigenamen) bleibt
    die reine Namenswahl bewusst ungeloest (kein Raten) -- die Anzeige
    nennt dafuer je Zeile zusaetzlich den Index, ueber den eindeutig
    gewaehlt werden kann."""
    with tempfile.TemporaryDirectory() as td:
        session, _written = _session_with_community(Path(td))
        overview = [("alpha", "Zwilling (Herkunft: demo/SIMULIERT)"), ("beta", "Zwilling (Herkunft: demo/SIMULIERT)")]
        resolved = session._resolve_known_ai_tokens(["Zwilling"], overview)
        # Ambige Namenswahl wird NICHT automatisch geraten -- bleibt als
        # Rohtoken durchgereicht (kein stiller Zufallstreffer).
        assert resolved == ["Zwilling"], resolved
        resolved_by_index = session._resolve_known_ai_tokens(["2"], overview)
        assert resolved_by_index == ["beta"], resolved_by_index


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
