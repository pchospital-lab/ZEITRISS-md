#!/usr/bin/env python3
"""
tests/mmo_sim/_r5_t2_launcher_hardexit_in_primary_publication.py --
ZR-BETREIBER-GASTERSCHAFFUNG-20261105-R5, Phase t1t2, T2 (STOP-BOUNDARY.md
§4.2): gebundene Skriptdatei (KEIN `-c`-Platzhalter, literal als
`[sys.executable, "-B", <dieser Pfad>, <echte Launcher-Flags>]` gestartet),
die den ECHTEN, UNVERAENDERTEN `scripts/mmo_sim.py:main()` importiert (nicht
nachgebaut) und VOR dessen Aufruf GENAU EINEN Monkeypatch an einer Grenze
setzt, die -- anders als `_r4_launcher_hardexit_before_reflection.py`
(Eintritt in `SectionRuntime._collect_reflections`, `runtime.py:924` --
NACH ALLEN Primaersaves, von R5 ausdruecklich als Ersatz ausgeschlossen) --
ECHT INNERHALB `store.complete_section`s Primaer-Schreibsequenz liegt
(`store.py:1986`, Pro-Mitglied-Schleife in `_resume_and_harvest`,
`store.py:1767-1830`: Primaersave (`:1807`) -> Version (`:1808`) ->
Fortschrittszustand (`persona_state_store.save_state`, `:1812-1818`) ->
Completed-Guard (`:1820-1829`)).

Monkeypatch-Ziel: `mmo_sim.core.persona_state.PersonaStateStore.save_state`
-- der ECHTE, unveraenderte Store wird ZUERST aufgerufen (der Fortschritts-
zustand wird also WIRKLICH atomar auf Platte geschrieben, exakt wie ohne
Patch), DANACH (nicht davor) prueft der Patch, ob dieser konkrete Aufruf der
Abschluss-Schreibschritt der Primaerpublikation war (eindeutiges Erkennungs-
merkmal: der `kernereignis`-Text `f"Abschnitt {section_id} am Tisch
{table.table_id} abgeschlossen."`, den `store.py:1814` baut -- diese exakte
Formatzeichenkette wird im GESAMTEN `mmo_sim`-Baum NUR an dieser EINEN Stelle
erzeugt, s. `grep -rn 'kernereignis=' mmo_sim/`). Trifft das Erkennungs-
merkmal zu, beendet der Patch den Prozess hart (`os._exit(94)`) -- NOCH VOR
dem unmittelbar folgenden `guard_path.write_text(...)` (`store.py:1820-1829`,
dem Completed-Guard). Jeder ANDERE `save_state`-Aufruf (z.B. waehrend
Onboarding/Figuren-Erschaffung, VOR der eigentlichen Abschluss-Runde) laeuft
UNVERAENDERT durch den echten Store, OHNE Exit -- der Patch ersetzt NICHT
den gesamten Rumpf, nur den Rueckkehrpunkt NACH dem einen erkannten Aufruf.

Ergebnis: Primaersave UND Version UND Fortschrittszustand fuer das
betroffene Mitglied sind beim Exit bereits real auf Platte; der Completed-
Guard fehlt noch, `_resume_and_harvest`/`complete_section` kehrt NIE
erfolgreich zurueck, `store.return_to_lobby`/`SectionRuntime.
_collect_reflections` (`runtime.py:923-924`) werden NIE erreicht -- eine
Phase frueher als der R4-Helper, aber eben noch nach echtem Beginn (nicht
vor dem ersten Schreibschritt) und vor Ende der Primaerpublikation.

`sys.argv[1:]` wird UNVERAENDERT an `launcher.main(...)` durchgereicht --
literal argv wie beim echten CLI-Aufruf."""
from __future__ import annotations

import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REPO_ROOT_STR = str(_REPO_ROOT)
if _REPO_ROOT_STR in sys.path:
    sys.path.remove(_REPO_ROOT_STR)
sys.path.insert(0, _REPO_ROOT_STR)

from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402

_REAL_SAVE_STATE = PersonaStateStore.save_state


def _save_state_then_hardexit_before_guard(self, pk, state, states_dir=None):
    """Ruft den ECHTEN `save_state` zuerst auf (Fortschrittszustand wird
    wirklich geschrieben) -- erkennt DANACH am `kernereignis`-Text des
    gerade geschriebenen Zustands, ob dies der Abschluss-Schreibschritt der
    Primaerpublikation war, und beendet den Prozess NUR in diesem Fall hart,
    BEVOR der Aufrufer (`store._resume_and_harvest`) den unmittelbar
    folgenden Completed-Guard schreiben kann."""
    target_path = _REAL_SAVE_STATE(self, pk, state, states_dir=states_dir)
    rounds_played = state.get("rounds_played")
    entry = (state.get("round_history") or {}).get(str(rounds_played)) or {}
    kernereignis = entry.get("kernereignis") or ""
    if kernereignis.startswith("Abschnitt ") and kernereignis.endswith(" abgeschlossen."):
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(94)
    return target_path


PersonaStateStore.save_state = _save_state_then_hardexit_before_guard

import scripts.mmo_sim as launcher  # noqa: E402

if __name__ == "__main__":
    sys.exit(launcher.main(sys.argv[1:]))
