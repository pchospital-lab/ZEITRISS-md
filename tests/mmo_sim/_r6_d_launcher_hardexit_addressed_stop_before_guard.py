#!/usr/bin/env python3
"""
tests/mmo_sim/_r6_d_launcher_hardexit_addressed_stop_before_guard.py --
ZR-BETREIBER-GASTERSCHAFFUNG-20261105-R6, Familie `d_t2` (G5/D, 01_NACHZUG.md
§D, STOP-EVIDENCE.md §4.4): gebundene Skriptdatei (KEIN `-c`-Platzhalter),
die den ECHTEN, UNVERAENDERTEN `scripts/mmo_sim.py:main()` importiert und
exakt den gleichen EINEN Monkeypatch an der GENAU gleichen Grenze setzt wie
`_r5_t2_launcher_hardexit_in_primary_publication.py` (ECHT INNERHALB
`store.complete_section`s Primaer-Schreibsequenz, `PersonaStateStore.
save_state` ruft den ECHTEN Store ZUERST auf, erkennt DANACH am
`kernereignis`-Text, ob dies der Abschluss-Schreibschritt war).

STOP-EVIDENCE.md §4.4 "Kleinstmoeglicher Nachzug": "die schon erlaubte
Grenzbarriere [DIESER Helper] kann den tatsaechlichen Statewrite beenden
[ECHTER `save_state`-Aufruf zuerst, unveraendert], den bestehenden
Kontrollanschluss bedienen lassen [DANACH, VOR dem Hardexit, auf die ECHTE
`admission.read_table_stop`-Durabilitaet warten -- der Kontroll-Thread
(`_OperatorControlScope`, `--operator-control-fifo`) laeuft NEBENLAEUFIG in
DIESEM SELBEN Prozess seit Eintritt in `tisch-start` und verarbeitet eine vom
Treiber gesendete '/stop'-Zeile UEBER DEN ECHTEN PRODUKTWEG] und erst danach
hart beenden [os._exit(94), GENAU wie der R5-Helper, NOCH VOR dem Completed-
Guard]."

Der Patch ERFINDET KEINE Stop-/Entscheidungsdatei selbst (er liest nur die
reale `admission.read_table_stop`-Durabilitaet, geschrieben vom echten
`_OperatorControlScope._handle_stop` -> `table_admission.request_table_stop`)
und ERSETZT NICHT den Produkt-Finishrumpf (derselbe Hardexit-Zeitpunkt wie
beim R5-Helper -- NOCH VOR dem Completed-Guard, `_resume_and_harvest`
erreicht ihn daher nie).

Konfiguration ueber Umgebungsvariablen (vom Treiber gesetzt, NICHT an den
echten Launcher weitergereicht -- reine Helper-interne Steuerung):
- `MMO_SIM_R6_D_RUN_DIR`: `run_dir` fuer `admission.read_table_stop`.
- `MMO_SIM_R6_D_TABLE_ID`: der adressierte `table_id`.
- `MMO_SIM_R6_D_SIGNAL_PATH`: Datei, die GENAU an der Grenze (realer
  Statewrite abgeschlossen, Completed-Guard noch ausstehend) geschrieben
  wird -- der Treiber wartet darauf, BEVOR er '/stop' sendet (damit der Stop
  garantiert NACH dem Planwrite/Primaerwrite ankommt, nicht davor -- sonst
  wuerde ein zu frueher Stop den Plan selbst verhindern, s. Treiber-Docstring).
- `MMO_SIM_R6_D_WAIT_TIMEOUT` (Default 20s): maximale Wartezeit auf die
  durable Stop-Bestaetigung, bevor trotzdem hart beendet wird (Diagnose-
  Grenze, kein Produktverhalten).

`sys.argv[1:]` wird UNVERAENDERT an `launcher.main(...)` durchgereicht --
literal argv wie beim echten CLI-Aufruf."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REPO_ROOT_STR = str(_REPO_ROOT)
if _REPO_ROOT_STR in sys.path:
    sys.path.remove(_REPO_ROOT_STR)
sys.path.insert(0, _REPO_ROOT_STR)

from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402

_REAL_SAVE_STATE = PersonaStateStore.save_state


def _save_state_then_wait_for_addressed_stop_then_hardexit(self, pk, state, states_dir=None):
    """Ruft den ECHTEN `save_state` zuerst auf (Fortschrittszustand wird
    wirklich geschrieben) -- erkennt DANACH am `kernereignis`-Text, ob dies
    der Abschluss-Schreibschritt der Primaerpublikation war. Ist das der
    Fall: signalisiert die Grenze (Statewrite fertig, Guard noch offen) und
    WARTET (Polling auf die ECHTE `admission.read_table_stop`-Durabilitaet,
    geschrieben vom nebenlaeufigen `--operator-control-fifo`-Kontrollthread
    desselben Prozesses), bevor der Prozess hart beendet wird -- NOCH VOR dem
    unmittelbar folgenden Completed-Guard-Write."""
    target_path = _REAL_SAVE_STATE(self, pk, state, states_dir=states_dir)
    rounds_played = state.get("rounds_played")
    entry = (state.get("round_history") or {}).get(str(rounds_played)) or {}
    kernereignis = entry.get("kernereignis") or ""
    if kernereignis.startswith("Abschnitt ") and kernereignis.endswith(" abgeschlossen."):
        run_dir = Path(os.environ["MMO_SIM_R6_D_RUN_DIR"])
        table_id = os.environ["MMO_SIM_R6_D_TABLE_ID"]
        signal_path = Path(os.environ["MMO_SIM_R6_D_SIGNAL_PATH"])
        timeout = float(os.environ.get("MMO_SIM_R6_D_WAIT_TIMEOUT", "20"))
        signal_path.parent.mkdir(parents=True, exist_ok=True)
        signal_path.write_text(
            json.dumps({
                "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "kernereignis": kernereignis, "pid": os.getpid(),
            }),
            encoding="utf-8",
        )
        from mmo_sim.core import admission
        deadline = time.time() + timeout
        while time.time() < deadline:
            stopped, _reason = admission.read_table_stop(run_dir, table_id)
            if stopped:
                break
            time.sleep(0.02)
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(94)
    return target_path


PersonaStateStore.save_state = _save_state_then_wait_for_addressed_stop_then_hardexit

import scripts.mmo_sim as launcher  # noqa: E402

if __name__ == "__main__":
    sys.exit(launcher.main(sys.argv[1:]))
