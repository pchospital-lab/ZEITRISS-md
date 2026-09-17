#!/usr/bin/env python3
"""
agent_mp/sl_client.py — schlanker OWUI-SL-Client für den 'Leader schreibt'-Harness.

Wiederverwendet owui_client.OWUIChat (Browser-Pfad, local:-Temp-Chat, OWUI-
eigenes RAG) 1:1 — dieser Client fügt nur das Datei-Persistieren des SL-Chats
(sl_history.md + sl_history.jsonl) hinzu, wie es die datei-vermittelte
Architektur B (siehe DESIGN.md) braucht. KEINE eigene Save-Detection/Quality-
Logik hier — die lebt weiterhin in solo_journey.py/coreops_split_merge.py und
wird von Altair direkt auf den zurückgegebenen SL-Text angewendet, damit sie
nicht dupliziert wird.

Env: OPENWEBUI_URL, OPENWEBUI_API_KEY (wie bestehender Harness).
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from owui_client import OWUIChat  # noqa: E402

# ─── Config (verifiziert gegen solo_journey.py, 2026-09-15 die aktuellste Quelle) ──
BASE_URL = os.environ.get("OPENWEBUI_URL", "http://127.0.0.1:8080")
API_KEY = os.environ.get("OPENWEBUI_API_KEY", "")
SL_MODEL = "zeitriss-v426-uncut"
# Live-KB verifiziert 2026-09-15 in solo_journey.py. Ältere Skripte
# (group-harness.py: a56706c9, coreops-harness.py: bb266c62) referenzieren
# historische/tote Collections — NICHT verwenden.
KB_ID = "9ad88aff-f881-4920-9fca-75094294ead8"
TIMEOUT_SL = 420
PRICE_IN, PRICE_OUT = 3.0, 15.0  # Sonnet-4.6 USD/1M, nur Anzeige


class SLSession:
    """Ein SL-Turn-Zyklus mit Datei-Persistenz für die datei-vermittelte Architektur B.

    Hält EINEN OWUIChat (= EIN geteilter SL-Chat für den ganzen Run) und
    schreibt jeden Turn in sl_history.md (lesbar) + sl_history.jsonl
    (maschinenlesbar), so wie DESIGN.md §3 es vorsieht.
    """

    def __init__(self, run_dir: Path, sl_model: str | None = None,
                 kb_id: str | None = None, timeout: int = TIMEOUT_SL):
        if not API_KEY:
            raise RuntimeError(
                "OPENWEBUI_API_KEY fehlt — erst: set -a; . ~/.openwebui_env; set +a")
        self.run_dir = Path(run_dir)
        self.md_path = self.run_dir / "sl_history.md"
        self.jsonl_path = self.run_dir / "sl_history.jsonl"
        self.chat = OWUIChat(
            BASE_URL, API_KEY, sl_model or SL_MODEL,
            kb_id=kb_id or KB_ID, timeout=timeout,
        )
        self.cum_cost = 0.0
        if not self.md_path.exists():
            self.md_path.write_text(
                f"# SL-Chat-Verlauf\n\nchat_id: `{self.chat.chat_id}`  \n"
                f"model: `{self.chat.model}`  \nkb_id: `{self.chat.kb_id}`\n\n---\n",
                encoding="utf-8",
            )

    def turn(self, turn_idx: int, user_text: str) -> dict:
        """Schickt user_text an die SL, persistiert Turn, gibt Ergebnis zurück.

        Rückgabe-Vertrag identisch zu OWUIChat.say(): {content, usage,
        sources, latency_s, chat_id} — Save-Detection/Quality-Checks aus dem
        bestehenden Harness lassen sich unverändert darauf anwenden.
        """
        res = self.chat.say(user_text)
        ptok = res["usage"].get("prompt_tokens", 0)
        ctok = res["usage"].get("completion_tokens", 0)
        cost = ptok / 1e6 * PRICE_IN + ctok / 1e6 * PRICE_OUT
        self.cum_cost += cost
        sources = self.chat.source_files()

        with self.md_path.open("a", encoding="utf-8") as fh:
            fh.write(f"\n## Turn {turn_idx:02d} — Leader-Post\n\n{user_text}\n")
            fh.write(f"\n## Turn {turn_idx:02d} — SL\n\n{res['content']}\n")
            if sources:
                fh.write(f"\n> _RAG: {', '.join(sources)}_\n")

        record = {
            "turn": turn_idx,
            "leader_post": user_text,
            "sl_content": res["content"],
            "prompt_tokens": ptok,
            "completion_tokens": ctok,
            "cost_usd": round(cost, 6),
            "cum_cost_usd": round(self.cum_cost, 6),
            "rag_sources": sources,
            "latency_s": res["latency_s"],
            "chat_id": res["chat_id"],
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        with self.jsonl_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

        return res

    def usage_summary(self) -> dict:
        return {
            "chat_id": self.chat.chat_id,
            "model": self.chat.model,
            "kb_id": self.chat.kb_id,
            "cum_cost_est_usd": round(self.cum_cost, 6),
        }

    @classmethod
    def from_history(cls, run_dir: Path, sl_model: str | None = None,
                     kb_id: str | None = None, timeout: int = TIMEOUT_SL) -> "SLSession":
        """Rekonstruiert eine SLSession aus sl_history.jsonl (M1-Fix).

        Schliesst die in ORCHESTRATION.md §2 selbst benannte Luecke: bei einem
        Mehr-Turn-Run ueber GETRENNTE Python-Aufrufe (Altair ruft sl_client pro
        Turn neu auf) haelt kein Prozess die OWUIChat-Historie im Speicher.
        Diese Factory liest jede JSONL-Zeile, baut die chat.history als
        User/Assistant-Paare wieder auf und uebernimmt die chat_id — VOR dem
        naechsten .turn()-Aufruf. Korrupte Zeilen werden uebersprungen, nicht
        fatal. Ohne diese Funktion muesste jeder Turn die fehleranfaellige
        Handrekonstruktion wiederholen.
        """
        sess = cls(run_dir, sl_model=sl_model, kb_id=kb_id, timeout=timeout)
        if not sess.jsonl_path.exists():
            return sess
        history: list[dict] = []
        last_chat_id: str | None = None
        last_cum = 0.0
        for line in sess.jsonl_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue  # korrupte Zeile ueberspringen, Run bleibt lauffaehig
            history.append({"role": "user", "content": rec.get("leader_post", "")})
            history.append({"role": "assistant", "content": rec.get("sl_content", "")})
            if rec.get("chat_id"):
                last_chat_id = rec["chat_id"]
            if "cum_cost_usd" in rec:
                last_cum = rec["cum_cost_usd"]
        sess.chat.history = history
        if last_chat_id:
            sess.chat.chat_id = last_chat_id
        sess.cum_cost = last_cum
        return sess


def new_sl_session(run_dir: str | Path, sl_model: str | None = None,
                    kb_id: str | None = None) -> SLSession:
    """Convenience-Factory, wie new_sl_chat() in solo_journey.py."""
    return SLSession(Path(run_dir), sl_model=sl_model, kb_id=kb_id)


if __name__ == "__main__":
    print(f"agent_mp.sl_client: SL_MODEL={SL_MODEL} KB_ID={KB_ID} "
          f"BASE_URL={BASE_URL} API_KEY_set={bool(API_KEY)}")
