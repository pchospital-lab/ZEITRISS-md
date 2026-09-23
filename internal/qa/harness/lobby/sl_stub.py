#!/usr/bin/env python3
"""
lobby/sl_stub.py — fixture-getriebener SL-TestDouble fuer den Lobby/Tisch-Durchstich.

KLAR ALS STUB MARKIERT: Diese Klasse macht KEINEN Netz-/Modell-/OWUI-/OpenRouter-Call.
Sie liest ausschliesslich vorher abgelegte, deutlich als SIMULIERT/FIXTURE markierte
JSON-Dateien aus fixtures/sl_canned/ und gibt deren Inhalt turnweise zurueck.

Contract-Naht zum spaeteren echten SL-Adapter
----------------------------------------------
`SLStub.turn(turn_idx, user_text)` gibt exakt denselben Rueckgabevertrag zurueck wie
`agent_mp.sl_client.SLSession.turn()`:
    {"content": str, "usage": {...}, "sources": [...], "latency_s": float, "chat_id": str}
`section.py` (der Aufrufer) kennt nur diesen Vertrag, nie die Stub-internen Details.

WICHTIG (Korrektur einer frueheren Ueberzeichnung, NB-A/R7): ein identischer
Rueckgabevertrag allein beweist NICHT, dass ein spaeterer echter Adapter den
AUSGEHENDEN `user_text` (inkl. des vom Aufrufer eingebetteten Save-Blocks, s.
`section.run_section`) unveraendert an die eigentliche SL weiterreicht — reale
Transportgrenzen (Kontext-Kappung, Nachrichtenumformung) sind eine SEPARATE, hier
NICHT geprueft Eigenschaft eines kuenftigen echten Adapters, nicht dieses Stubs.
`SLStub.calls[i]['user_text']` protokolliert exakt das, was der Aufrufer
tatsaechlich als `text` an `.turn()` uebergeben hat — die Abnahme prueft genau
DIESEN protokollierten Text (nicht nur den separat gefuehrten `sl_log`-Eintrag).
Um spaeter echt zu verbinden: in `section.py` die Konstruktion von `SLStub(...)`
durch `agent_mp.sl_client.new_sl_session(run_dir)` ersetzen — der Aufrufcode
(`.turn(...)` und die nachgelagerte Save-Ernte via `saves.extract_all_saves`)
bleibt nur dann unveraendert GUELTIG, wenn der echte Adapter denselben
Text-Empfangsvertrag erfuellt (Save als Teil von `user_text` ankommt); nutzt der
echte Adapter stattdessen eine STRUKTURIERTE Payload-API (Text + getrennter
Save-Parameter statt eingebettetem Block), muss die entsprechende
Empfangsassertion angepasst — NICHT einfach umgangen — werden. JETZT ist NICHTS
live verbunden; `SLSession` selbst wird in diesem Slice nirgends importiert oder
aufgerufen.
"""
from __future__ import annotations

import json
from pathlib import Path


class SLStubExhausted(RuntimeError):
    """Mehr .turn()-Aufrufe als die Fixture-Datei Turns enthaelt."""


class SLStub:
    """Fixture-getriebener Ersatz fuer `SLSession`. Kein Netzwerk, kein Prozess.

    Liest eine JSON-Fixture mit dem Format
        {"turns": [{"content": "..."}, ...]}
    und gibt bei jedem `.turn()`-Aufruf den naechsten Eintrag zurueck, contract-gleich
    zu `SLSession.turn()`. `usage`/`sources`/`latency_s` sind deterministische
    Platzhalterwerte (keine echten Tokenzahlen), `chat_id` ist stabil pro Instanz.
    """

    def __init__(self, fixture_path: str | Path, chat_id: str | None = None):
        self.fixture_path = Path(fixture_path)
        data = json.loads(self.fixture_path.read_text(encoding="utf-8"))
        self._turns: list[dict] = data.get("turns", [])
        self._next_idx = 0
        self.chat_id = chat_id or f"stub-{self.fixture_path.stem}"
        self.calls: list[dict] = []  # Operator-Beleg: was wurde wann angefragt

    def turn(self, turn_idx: int, user_text: str) -> dict:
        """Contract-gleich zu SLSession.turn(): {content, usage, sources, latency_s, chat_id}.

        `turn_idx` wird NICHT zum Indizieren der Fixture verwendet (die Fixture ist eine
        einfache Sequenz) — er wird nur mitprotokolliert, wie es der reale Aufrufer tut.
        """
        if self._next_idx >= len(self._turns):
            raise SLStubExhausted(
                f"SLStub {self.fixture_path.name}: keine weiteren gecannten Turns "
                f"(angefragt turn_idx={turn_idx}, vorhanden={len(self._turns)})."
            )
        turn = self._turns[self._next_idx]
        self._next_idx += 1
        content = turn["content"]
        record = {
            "turn_idx": turn_idx,
            "user_text": user_text,
            "content": content,
        }
        self.calls.append(record)
        return {
            "content": content,
            "usage": {"prompt_tokens": 0, "completion_tokens": 0},
            "sources": [],
            "latency_s": 0.0,
            "chat_id": self.chat_id,
        }


def new_sl_stub(fixture_path: str | Path) -> SLStub:
    """Convenience-Factory, spiegelt `sl_client.new_sl_session()` als Stub-Pendant."""
    return SLStub(fixture_path)
