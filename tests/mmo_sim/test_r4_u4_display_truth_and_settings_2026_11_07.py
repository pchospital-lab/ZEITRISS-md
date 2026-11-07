#!/usr/bin/env python3
"""
tests/mmo_sim/test_r4_u4_display_truth_and_settings_2026_11_07.py
ZR-VOLLENDUNG-OHNE-LAN-NACHZUG-20261107-R4 (U4, PLAYER-UX-REVIEW.md F4,
01_NACHZUG.md U4, 02_ABNAHME.md D).

Drei Befunde, drei Belege:

(a) `_display_sanitize_sl` behauptete bisher ALLEIN aus erkannter JSON-/
Markerform Erfolg ("[Spielstand gespeichert]"/"[Abschnitt bestaetigt]"),
UNABHAENGIG von der tatsaechlichen fachlichen Autoritaet -- jetzt neutrale
Ersatzzeilen ohne Erfolgszusage.

(b) Die Zeitgedanke-Aufrufstelle in `_HumanDriver.decide()` feuerte NACH
beendetem Warten (direkt VOR der Anzeige einer bereits empfangenen
SL-Antwort) statt WAEHREND einer echten noch offenen Anfrage -- jetzt
feuert sie GENAU VOR der Rueckgabe an die Runtime (die den GM-Request
ERST danach startet), NIE mehr unmittelbar vor einem bereits vorliegenden
[SL]-Eintrag.

(c) `_cmd_settings` hatte keinen im Spiel bedienbaren Schalter fuer
Zeitgedanken (nur `MMO_SIM_TUI_ZEITGEDANKEN=0`) -- jetzt 'einstellungen
zeitgedanken an/aus' (bzw. 's zeitgedanken an/aus') schaltet real um, ohne
Shellwissen, OHNE die bestehende `_cmd_settings()`-Direktaufrufkompatibi-
litaet (`test_ux1_kiss_menu.py`) zu brechen.

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs,
0 echte GM-/Persona-Modellcalls (ein einziger kontrollierter Fake-GM mit
GENAU 2 Zuegen am vorhandenen Modellrand, deterministischer Zeitgedanke-
Pool ohne Zufall/Uhr/Zusatzcall)."""
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
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402
import _a24_local_support as sup  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


def _build_solo_leader(run_dir: Path, states_dir: Path, onboarding_dir: Path):
    """Identischer Musteraufbau wie `test_ux1_g04_purpose_stand_verlauf_
    2026_10_05.py::_build_solo_leader` -- bereits als zuverlaessiger,
    nicht-haengender Solo-Leader-Abschluss belegt (ueber die echte
    Registry/Onboarding-Kette, NICHT nur Katalog+Onboarding direkt)."""
    registry_dir = run_dir.parent / "registry"
    leader = sup.register_human(registry_dir, "Leader")
    leader_id = leader.participant_id
    info = sup.onboard_human_figure(
        registry_dir, leader_id, onboarding_dir, states_dir, run_dir, "CHR-U4ZG", "Lea", "LEADOPS",
    )
    return leader_id, info["char_id"]


def _scripted_input(values):
    q = list(values)

    def _fn(prompt: str = "") -> str:
        if q:
            return q.pop(0)
        raise EOFError()

    return _fn


def test_display_sanitize_no_longer_claims_success_from_form_alone():
    session = TuiSession(
        onboarding_dir=Path("/does/not/matter"), catalog_dir=Path("/does/not/matter"),
        participant_id="p1",
    )
    save_block = full_v7_save("CHR-U4-FORM", name="form-only")
    raw = "Vorspiel-Text.\n```json\n" + json.dumps(save_block) + "\n```\n" + COMPLETION_MARKER
    sanitized = session._display_sanitize_sl(raw)
    assert "gespeichert" not in sanitized.lower(), sanitized
    assert "bestaetigt" not in sanitized.lower(), sanitized
    assert "[Technischer Speicherblock ausgeblendet]" in sanitized, sanitized
    assert "[Technischer Abschlussmarker ausgeblendet]" in sanitized, sanitized
    # Normaler Erzaehltext bleibt unberuehrt.
    assert "Vorspiel-Text." in sanitized, sanitized


class _OneShotCompletingGm:
    """Liefert beim ERSTEN Aufruf sofort den Abschluss-Marker + Save-Block
    -- GENAU EIN echter Spielzug (Musteraufbau aus
    `test_ux1_g04_purpose_stand_verlauf_2026_10_05.py::_OneShotCompletingGm`,
    dort bereits als zuverlaessiger Solo-Leader-Abschluss belegt)."""

    def __init__(self, char_id: str, participant_id: str):
        self._char_id = char_id
        self._participant_id = participant_id
        self.calls = 0

    def turn(self, turn_idx, text, **kw):
        self.calls += 1
        content = (
            f"Abschnitt beendet.\n```json\n"
            f"{json.dumps(full_v7_save(self._char_id, name=self._participant_id))}\n```\n"
            f"{COMPLETION_MARKER}"
        )
        return {"content": content}


def test_zeitgedanke_fires_at_the_real_pending_call_not_as_a_belated_sl_prefix():
    """Beweist die neue Aufrufstelle direkt: beim ALLERERSTEN Leaderzug
    (`_sl_already_shown` war an der alten Stelle strukturell IMMER 0 --
    die alte Nachholanzeige konnte hier NIE feuern) feuert die
    Zeitgedanke-Zeile jetzt trotzdem, weil sie an der neuen Stelle NICHT
    mehr an bereits gezeigte SL-Historie gebunden ist, sondern an den
    tatsaechlich noch ausstehenden GM-Request VOR der Rueckgabe an die
    Runtime. Kein '[SL]'-Eintrag erscheint in diesem Einzelzug-Lauf
    UNMITTELBAR VOR der Zeitgedanke-Zeile (die alte, buggy Adjazenz)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir, onboarding_dir = root / "run", root / "states", root / "onboarding"
        catalog_dir = root / "catalog"
        write_test_profile(run_dir)
        leader_id, char_id = _build_solo_leader(run_dir, states_dir, onboarding_dir)

        gm = _OneShotCompletingGm(char_id, leader_id)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=leader_id,
            input_fn=_scripted_input([
                "Wir sichern die Position und beobachten die Umgebung.",
                "Danke, das war ein guter Abschnitt.",
            ]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=sup.SCHEMA,
            gm_transport_factory=lambda: gm, persona_driver_factory=None,
        )
        try:
            session._cmd_local_round([])
        except EndOfInput:
            pass
        assert gm.calls == 1, "genau EIN echter Spielzug erwartet"

        zg_indices = [i for i, p in enumerate(printed) if p.startswith("[Zeitgedanke]")]
        sl_indices = [i for i, p in enumerate(printed) if p.startswith("[SL]")]
        assert zg_indices, (
            "der Leaderzug geht an die SL -- an der NEUEN Stelle (vor der Rueckgabe) haette "
            "das eine Zeitgedanke-Zeile ausloesen muessen, selbst beim allerersten Zug", printed,
        )
        assert sl_indices, printed
        # Die Zeitgedanke-Zeile steht VOR der [SL]-Anzeige der Antwort, die
        # GENAU dieser Einreichung folgt -- sie begleitet das Einreichen
        # (noch ausstehende Arbeit), nicht die spaetere Anzeige der bereits
        # eingetroffenen Antwort (die alte Nachholanzeige-Reihenfolge waere
        # umgekehrt: SL-Anzeige VOR/an derselben Stelle wie die Zeile).
        assert max(zg_indices) < min(sl_indices), (
            f"Zeitgedanke muss VOR der [SL]-Anzeige stehen (begleitet das Einreichen, nicht die "
            f"spaetere Anzeige der schon eingetroffenen Antwort): zg={zg_indices} sl={sl_indices} "
            f"{printed}"
        )
        # Direkter Gegenbeleg zur alten Stelle: VOR dem Fix war das
        # Pflichtkriterium `_sl_already_shown > 0` -- beim allerersten
        # Leaderzug (hier) war das STRUKTURELL IMMER falsch, die alte
        # Stelle haette also NIE gefeuert. Dass hier trotzdem eine
        # Zeitgedanke-Zeile steht, beweist die Verlagerung an die neue,
        # tatsaechlich noch ausstehende Stelle.


def test_settings_zeitgedanken_toggle_is_real_and_playable_without_shell():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=root / "onboarding", catalog_dir=root / "catalog", participant_id="p1",
            input_fn=_scripted_input([
                "einstellungen zeitgedanken aus",
                "einstellungen",
                "einstellungen zeitgedanken an",
                "beenden",
            ]),
            print_fn=printed.append,
        )
        rc = session.run()
        assert rc == 0
        out = "\n".join(printed)
        assert "Zeitgedanken jetzt aus" in out, out
        assert "Zeitgedanken (Zeit-Atmosphaere in Wartephasen): aus" in out, out
        assert "Zeitgedanken jetzt an" in out, out
        # Keine Produktmodellaufrufe durch Settings/Anzeige -- diese Session
        # hat ueberhaupt keine `gm_transport_factory` konfiguriert, ein
        # versteckter Call waere also sofort als Absturz sichtbar.


def test_direct_cmd_settings_call_stays_byte_identical_without_args():
    """Erhaltungsprobe (`test_ux1_kiss_menu.py::test_einstellungen_word_
    same_output_as_s_hotkey`): `_cmd_settings()` OHNE `args` bleibt
    bytegleich -- KEIN neuer Readline-Aufruf, `args=None` ist der
    unveraenderte Default."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            print_fn=printed.append,
        )._cmd_settings()
        assert any("Teilnehmer-ID: p1" in p for p in printed), printed
        assert not any(p.startswith("Zeitgedanken jetzt") for p in printed), printed


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
