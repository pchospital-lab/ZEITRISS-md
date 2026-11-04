#!/usr/bin/env python3
"""
tests/mmo_sim/_r4_gm_double.py -- ZR-BETREIBER-GASTERSCHAFFUNG-20261104-R4,
TEIL B Grenzinjektions-Double fuer FIX5 (`mmo_sim/adapters/factories.py:
_load_gm_transport_double`).

Dieses Modul lebt BEWUSST in der Testdatei, NICHT im Produkt (FIX5s
Docstring/Kommentar). Es wird vom ECHTEN Launcher-Subprozess
(`scripts/mmo_sim.py`) ueber `MMO_SIM_GM_TRANSPORT_DOUBLE=tests.mmo_sim.
_r4_gm_double:build` lazy per `importlib.import_module` geladen -- der
Subprozess importiert dieses Modul also FRISCH in seinem EIGENEN
Interpreter, kein geteilter Python-Zustand mit dem Treiberprozess. Jede
Konfiguration kommt daher ausschliesslich ueber eine JSON-Konfigdatei
(`MMO_SIM_R4_GMDOUBLE_CONFIG`), deren Pfad der Treiber VOR dem Subprozessstart
schreibt.

Konfigformat (`MMO_SIM_R4_GMDOUBLE_CONFIG`-Datei):
{
  "responses": ["<content fuer Call 1>", "<content fuer Call 2>", ...],
  "calls_log": "<Pfad fuer JSONL-Aufrufspur>",
  "stop": {                                   # optional, sonst kein Stop-Rennen
    "after_call": 1,                          # 1-basiert: NACH diesem Call wird gestoppt
    "kind": "table" | "creation",
    "control_fifo": "<Pfad der echten Kontroll-FIFO>",
    "control_line": "/stop" | "gast-erschaffung-stop <guest_id>",
    "run_dir": "<Pfad>",
    "operator_id": "...", "guest_id": "...", "generation": 1   # NUR kind=="creation"
  } | null
}

Der Double schreibt die Kontrollzeile WAEHREND des offenen Calls (Call
`after_call`) in die ECHTE Kontroll-FIFO (derselbe Zustellweg, den ein
Betreiber ueber `--operator-control-fifo` benutzen wuerde) und wartet
KONTROLLIERT (kein Zufallstiming, Polling mit Timeout) auf die durable
Bestaetigung -- GENAU die Technik von `drive_r3_g5_evidence_2026_11_04.py`s
`StopViaRealControlFifoGm`, nur jetzt am FIX5-Seam statt an einer direkt
konstruierten Session. Call `after_call`s Inhalt wird ERST NACH der
durablen Bestaetigung zurueckgegeben (spaete Antwort, korrekt verbucht,
keine Publikation -- s. Briefing T1/T4).

Jeder Aufruf wird in `calls_log` (JSONL) protokolliert -- die echte
Aufrufspur fuer T3s "Anbieterrequests + fehlende Gastprovider-Nutzung"-
Nachweis."""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

_STATE: dict = {"call_index": 0}


def _log_call(cfg: dict, *, table_id: str, call_index: int, turn_idx: int, user_text: str, content: str) -> None:
    calls_log = cfg.get("calls_log")
    if not calls_log:
        return
    record = {
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "table_id": table_id,
        "call_index": call_index,
        "turn_idx": turn_idx,
        "user_text_len": len(user_text or ""),
        "user_text_excerpt": (user_text or "")[:4000],
        "content_returned": content,
    }
    path = Path(calls_log)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _run_stop_race(stop_cfg: dict) -> None:
    """Signalisiert den Stop und wartet (Polling, Timeout 20s) auf die
    durable Bestaetigung -- Double NUR an der GM-Transport-Grenze, der
    eigentliche Stop laeuft ueber den ECHTEN Produktweg.

    Zwei Zustellwege (je nach `kind`):
    - `kind=="table"`: `/stop` ist ein spezielles Kontrollzeilen-Token, das
      NUR vom `--operator-control-fifo`-Kontroll-Thread gelesen wird
      (`scripts/mmo_sim.py:_fifo_control_line_source`) -- die Kontrollzeile
      wird daher direkt in die echte Kontroll-FIFO geschrieben.
    - `kind=="creation"`: `gast-erschaffung-stop <guest_id>` ist ein
      GEWOEHNLICHER Top-Level-Menuebefehl (`elif choice ==
      "gast-erschaffung-stop"`), den NUR der Betreiber ueber sein EIGENES
      regulaeres stdin eingibt -- der Double kann das nicht selbst
      zustellen (kein Zugriff auf das stdin des externen Treiberprozesses).
      Stattdessen beruehrt der Double eine Signaldatei (`signal_file`); der
      EXTERNE Treiber beobachtet diese Datei und tippt den ECHTEN Befehl
      ueber das reale Operator-stdin ein, sobald sie erscheint -- der
      Double selbst ruft NIE eine interne Kommandomethode auf."""
    if stop_cfg.get("control_fifo"):
        control_fifo = stop_cfg["control_fifo"]
        control_line = stop_cfg["control_line"]
        fd = os.open(str(control_fifo), os.O_WRONLY)
        with os.fdopen(fd, "w") as f:
            f.write(control_line + "\n")
    elif stop_cfg.get("signal_file"):
        signal_path = Path(stop_cfg["signal_file"])
        signal_path.parent.mkdir(parents=True, exist_ok=True)
        signal_path.write_text(
            json.dumps({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}), encoding="utf-8",
        )
    else:
        raise ValueError("_r4_gm_double: stop-Konfiguration braucht 'control_fifo' oder 'signal_file'.")

    import mmo_sim.core.admission as admission

    run_dir = Path(stop_cfg["run_dir"])
    kind = stop_cfg["kind"]
    deadline = time.time() + 20.0
    if kind == "table":
        table_id = stop_cfg["table_id"]
        while time.time() < deadline:
            stopped, _reason = admission.read_table_stop(run_dir, table_id)
            if stopped:
                return
            time.sleep(0.02)
        raise AssertionError(
            f"_r4_gm_double: Tisch-Stop fuer table_id={table_id!r} wurde nicht rechtzeitig "
            "durabel ueber die echte Kontroll-FIFO bestaetigt."
        )
    if kind == "creation":
        from mmo_sim.domain.zeitriss import creation_service

        decision_id = creation_service._creation_decision_id(
            stop_cfg["operator_id"], stop_cfg["guest_id"], stop_cfg["generation"],
        )
        while time.time() < deadline:
            decision = admission.read_table_decision(run_dir, decision_id)
            if decision is not None:
                return
            time.sleep(0.02)
        raise AssertionError(
            f"_r4_gm_double: Erschaffungs-Stop fuer decision_id={decision_id!r} wurde nicht "
            "rechtzeitig durabel ueber die echte Kontroll-FIFO bestaetigt."
        )
    raise ValueError(f"_r4_gm_double: unbekannte stop.kind={kind!r}")


class _R4GmDoubleTransport:
    """GRENZINJEKTION (02 §1) -- KEIN Live-Modelllauf. Erfuellt exakt den
    `GMTransport`-Vertrag (`mmo_sim/adapters/base.py`): `{content, usage,
    sources, latency_s, chat_id}`."""

    def __init__(self, table_id: str, cfg: dict):
        self._table_id = table_id
        self._cfg = cfg
        self._responses = list(cfg.get("responses") or [])

    def turn(self, turn_idx: int, user_text: str, output_limit_tokens=None) -> dict:
        _STATE["call_index"] += 1
        call_index = _STATE["call_index"]
        content = self._responses.pop(0) if self._responses else ""
        stop_cfg = self._cfg.get("stop")
        if stop_cfg is not None and stop_cfg.get("after_call") == call_index:
            _run_stop_race(stop_cfg)
        _log_call(
            self._cfg, table_id=self._table_id, call_index=call_index, turn_idx=turn_idx,
            user_text=user_text, content=content,
        )
        return {
            "content": content, "usage": {}, "sources": [], "latency_s": 0.0,
            "chat_id": f"r4-double-{call_index}",
        }

    def usage_summary(self) -> dict:
        return {}


def build(table_id: str):
    """Der in `MMO_SIM_GM_TRANSPORT_DOUBLE=tests.mmo_sim._r4_gm_double:build`
    benannte Callable -- `mmo_sim/adapters/factories.py:default_gm_transport_
    factory`s innere `factory(table_id)` ruft dies MIT `table_id` auf und
    gibt das Ergebnis direkt zurueck (FIX5-Vertrag)."""
    config_path = os.environ["MMO_SIM_R4_GMDOUBLE_CONFIG"]
    cfg = json.loads(Path(config_path).read_text(encoding="utf-8"))
    return _R4GmDoubleTransport(table_id, cfg)
