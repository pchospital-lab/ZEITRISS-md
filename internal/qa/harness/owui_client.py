#!/usr/bin/env python3
"""
owui_client.py — OpenWebUI-Client, der EXAKT den Browser-Chat-Pfad nachfährt.

Hintergrund (2026-06-15): OWUI 0.9.5 hat den kopflosen API-Pfad
`/api/chat/completions` OHNE chat_id kaputt ('NoneType'.startswith). Der Browser
crasht NICHT, weil er `parent_id`/`user_message` mitschickt und OWUI dann selbst
einen Chat anlegt — UND dabei sein eingebautes RAG fährt (KB-Retrieval-Inject,
sichtbar als `sources` in der Response + [n]-Zitate im Text).

Dieser Client repliziert genau das:
  - Stock-OWUI, KEIN Source-Patch -> überlebt Updates, ist endnutzer-identisch.
  - OWUI macht das RAG selbst (kein manuelles Snippet-Injizieren).
  - Conversation-State wird clientseitig als messages[]-Historie gehalten
    (wie ein durchgehender Chat-Thread).

Verifiziert: Anker ABSOLUT-7 nur mit `files:[collection]` beantwortet, sources
liefert echte KB-Dateinamen, prompt_tokens ~56k (MP + Retrieval).
"""
from __future__ import annotations
import json
import time
import urllib.error
import urllib.request
import uuid
from typing import Any


class OWUIError(RuntimeError):
    pass


class OWUIChat:
    """Ein durchgehender SL-Chat-Thread gegen ein OWUI-Preset, mit KB + RAG."""

    def __init__(self, base_url: str, api_key: str, model: str,
                 kb_id: str | None = None,
                 timeout: int = 420, max_retries: int = 3, backoff: float = 2.0):
        self.base = base_url.rstrip("/")
        self.key = api_key
        self.model = model
        self.kb_id = kb_id
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff = backoff
        self.history: list[dict] = []   # roll-forward Konversation
        # Temporary-Chat-Prefix 'local:' => OWUI fährt RAG voll, persistiert aber
        # NICHTS in der DB (= 'Temporary Chat'-Modus des Browsers). Verhindert
        # DB-Müll bei Mehr-Turn-Läufen. Verifiziert 2026-06-15 (52->52 Chats).
        self.chat_id: str = f"local:playtest-{uuid.uuid4().hex[:10]}"
        self.last_usage: dict = {}
        self.last_sources: list = []

    # ── HTTP ──────────────────────────────────────────────────────────────
    def _post(self, path: str, body: dict, timeout: int | None = None) -> dict:
        data = json.dumps(body).encode()
        last_err: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                req = urllib.request.Request(
                    self.base + path, data=data, method="POST",
                    headers={"Authorization": f"Bearer {self.key}",
                             "Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req, timeout=timeout or self.timeout) as r:
                    return json.loads(r.read().decode())
            except urllib.error.HTTPError as e:
                txt = e.read().decode()[:400]
                last_err = OWUIError(f"HTTP {e.code}: {txt}")
                if e.code in (401, 403, 404):
                    raise last_err
            except Exception as e:  # noqa: BLE001
                last_err = e
            time.sleep(self.backoff ** attempt)
        raise last_err  # type: ignore[misc]

    # ── ein SL-Turn ───────────────────────────────────────────────────────
    def say(self, user_text: str) -> dict:
        """Schickt eine Nutzer-Nachricht, gibt {content, usage, sources, latency} zurück.

        Fährt den Browser-Pfad: parent_id/user_message + messages[]-Historie,
        files:[collection] -> OWUI macht RAG selbst.
        """
        self.history.append({"role": "user", "content": user_text})
        # WICHTIG: KEIN parent_id/user_message senden. Das würde is_new_chat=True
        # auslösen, OWUI ignoriert dann das 'local:' und legt einen UUID-Chat in
        # der DB an (= Müll). Nur chat_id='local:...' + messages[] => RAG läuft,
        # nichts persistiert. Verifiziert 2026-06-15 (Chat-Count bleibt konstant).
        body: dict[str, Any] = {
            "model": self.model,
            "stream": False,
            "chat_id": self.chat_id,                 # local: => kein DB-Persist
            "messages": self.history,
        }
        if self.kb_id:
            body["files"] = [{"type": "collection", "id": self.kb_id}]

        t0 = time.time()
        resp = self._post("/api/chat/completions", body)
        latency = time.time() - t0

        try:
            content = resp["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise OWUIError(f"Unerwartete Response-Struktur: {json.dumps(resp)[:300]}") from e

        self.history.append({"role": "assistant", "content": content})
        self.last_usage = resp.get("usage") or {}
        self.last_sources = resp.get("sources") or []
        return {
            "content": content,
            "usage": self.last_usage,
            "sources": self.last_sources,
            "latency_s": latency,
            "chat_id": self.chat_id,
        }

    def source_files(self) -> list[str]:
        """Dateinamen der letzten RAG-Treffer (für Verify, dass KB feuert)."""
        names: set[str] = set()
        for grp in self.last_sources:
            if not isinstance(grp, dict):
                continue
            src = grp.get("source") or {}
            if isinstance(src, dict) and src.get("name"):
                names.add(str(src["name"]).split("/")[-1])
            for m in (grp.get("metadata") or []):
                if isinstance(m, dict) and m.get("name"):
                    names.add(str(m["name"]).split("/")[-1])
        return sorted(names)


def stateless_completion(base_url: str, api_key: str, model: str,
                         system: str, user: str,
                         temperature: float = 0.92, max_tokens: int = 300,
                         timeout: int = 60) -> str:
    """Einfacher stateless Call für Persona-Turns (kein Chat-State, kein RAG).

    Persona braucht keinen RAG und keine OWUI-Chat-Persistenz — nutzt denselben
    Browser-Pfad-Trick (parent_id/user_message), damit der 0.9.5-Bug nicht greift.
    """
    base = base_url.rstrip("/")
    body = {
        "model": model, "stream": False,
        "chat_id": f"local:persona-{uuid.uuid4().hex[:10]}",
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "temperature": temperature, "max_tokens": max_tokens,
    }
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        base + "/api/chat/completions", data=data, method="POST",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        resp = json.loads(r.read().decode())
    return resp["choices"][0]["message"]["content"].strip()
