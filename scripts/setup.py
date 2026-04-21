#!/usr/bin/env python3
"""
Universal Setup for OpenWebUI-based AI projects.

Works on Windows, macOS, Linux, and Android (Termux).
Zero external dependencies — uses only Python standard library.

Usage:
    python setup.py                    # Interactive OpenWebUI setup
    python setup.py --export           # Export knowledge pack (for Lumo etc.)
    python setup.py --export --flat    # Export flat (no subdirs, numbered)

Reads project config from setup.json in the repo root.
Auto-detects knowledge files from master-index.json (slot:true)
or kb/ directory.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import platform
import shutil
import ssl
import sys
import textwrap
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from getpass import getpass
from pathlib import Path
from typing import Any, Optional


# ── Helpers ─────────────────────────────────────────────────────────

def find_repo_root() -> Path:
    """Walk up from this script to find the repo root (has setup.json)."""
    here = Path(__file__).resolve().parent
    for candidate in [here.parent, here, Path.cwd()]:
        if (candidate / "setup.json").exists():
            return candidate
    # Fallback: try cwd
    if (Path.cwd() / "setup.json").exists():
        return Path.cwd()
    print_error("setup.json not found. Run from the repo root or scripts/ dir.")
    sys.exit(1)


def load_config(repo: Path) -> dict:
    """Load and validate setup.json."""
    cfg_path = repo / "setup.json"
    with open(cfg_path, encoding="utf-8") as f:
        cfg = json.load(f)
    required = ["project", "preset_id", "preset_name", "masterprompt", "params"]
    missing = [k for k in required if k not in cfg]
    if missing:
        print_error(f"setup.json missing keys: {', '.join(missing)}")
        sys.exit(1)
    return cfg


# ── Knowledge file discovery ────────────────────────────────────────

def discover_knowledge_files(repo: Path, cfg: dict) -> list[Path]:
    """
    Find knowledge files. Strategy:
    1. If master-index.json exists and has slot:true modules → use those
    2. Else if kb/ dir exists → use all .md (and .json) files in it
    3. Else → error
    """
    files: list[Path] = []

    # Strategy 1: master-index.json with slots
    idx_path = repo / "master-index.json"
    if idx_path.exists():
        with open(idx_path, encoding="utf-8") as f:
            idx = json.load(f)
        for mod in idx.get("modules", []):
            if mod.get("slot") is True:
                rel = mod["path"].split("#")[0]  # strip anchors
                fp = repo / rel
                if fp.exists():
                    files.append(fp)
                else:
                    print_warn(f"Slot file missing: {rel}")
        if files:
            return files

    # Strategy 2: kb/ directory
    kb_dir = repo / "kb"
    if kb_dir.is_dir():
        for p in sorted(kb_dir.rglob("*")):
            if p.suffix in (".md", ".json") and p.is_file():
                files.append(p)
        if files:
            return files

    print_error("No knowledge files found (no master-index.json slots and no kb/ dir).")
    sys.exit(1)


# ── Terminal output (cross-platform) ───────────────────────────────

_SUPPORTS_COLOR: Optional[bool] = None


def _color_supported() -> bool:
    global _SUPPORTS_COLOR
    if _SUPPORTS_COLOR is not None:
        return _SUPPORTS_COLOR
    if os.environ.get("NO_COLOR"):
        _SUPPORTS_COLOR = False
    elif os.environ.get("FORCE_COLOR"):
        _SUPPORTS_COLOR = True
    elif platform.system() == "Windows":
        _SUPPORTS_COLOR = os.environ.get("TERM") == "xterm" or hasattr(
            sys.stdout, "isatty"
        ) and sys.stdout.isatty() and os.environ.get("WT_SESSION")
    else:
        _SUPPORTS_COLOR = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    return _SUPPORTS_COLOR


def _c(code: str, text: str) -> str:
    if _color_supported():
        return f"\033[{code}m{text}\033[0m"
    return text


def print_ok(msg: str) -> None:
    print(f"  {_c('32', '✓')}  {msg}")


def print_warn(msg: str) -> None:
    print(f"  {_c('33', '⚠')}  {msg}")


def print_error(msg: str) -> None:
    print(f"  {_c('31', '✗')}  {msg}", file=sys.stderr)


def print_info(msg: str) -> None:
    print(f"  {_c('36', 'ℹ')}  {msg}")


def print_header(text: str) -> None:
    width = max(len(text) + 6, 40)
    border = "═" * (width - 2)
    print()
    print(f"  {_c('1', '╔' + border + '╗')}")
    print(f"  {_c('1', '║')}  {text.ljust(width - 4)}  {_c('1', '║')}")
    print(f"  {_c('1', '╚' + border + '╝')}")
    print()


# ── HTTP client (stdlib only) ──────────────────────────────────────

class APIClient:
    """Minimal HTTP client for OpenWebUI REST API."""

    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        # Allow self-signed certs for localhost
        self._ctx = ssl.create_default_context()
        if "localhost" in base_url or "127.0.0.1" in base_url:
            self._ctx.check_hostname = False
            self._ctx.verify_mode = ssl.CERT_NONE

    def _request(
        self,
        method: str,
        path: str,
        data: Any = None,
        content_type: str = "application/json",
        timeout: Optional[float] = None,
    ) -> tuple[int, bytes]:
        url = f"{self.base_url}{path}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        body = None

        if data is not None:
            if content_type == "application/json":
                body = json.dumps(data).encode("utf-8")
                headers["Content-Type"] = "application/json"
            else:
                # multipart handled separately
                body = data
                headers["Content-Type"] = content_type

        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(
                req, timeout=timeout or self.timeout, context=self._ctx
            ) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()
        except (urllib.error.URLError, OSError) as e:
            return 0, str(e).encode()

    def get(self, path: str, **kw: Any) -> tuple[int, Any]:
        code, body = self._request("GET", path, **kw)
        try:
            return code, json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return code, body

    def post_json(self, path: str, data: dict, **kw: Any) -> tuple[int, Any]:
        code, body = self._request("POST", path, data=data, **kw)
        try:
            return code, json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return code, body

    def delete(self, path: str) -> tuple[int, Any]:
        code, body = self._request("DELETE", path)
        try:
            return code, json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return code, body

    def upload_file(self, path: str, filepath: Path) -> tuple[int, Any]:
        """Multipart file upload using stdlib."""
        boundary = f"----PythonSetup{hashlib.md5(str(time.time()).encode()).hexdigest()}"
        filename = filepath.name
        with open(filepath, "rb") as f:
            file_data = f.read()

        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            f"Content-Type: application/octet-stream\r\n\r\n"
        ).encode("utf-8")
        body += file_data
        body += f"\r\n--{boundary}--\r\n".encode("utf-8")

        return self._request(
            "POST",
            path,
            data=body,
            content_type=f"multipart/form-data; boundary={boundary}",
        )

    # ── High-level methods ──────────────────────────────────────────

    def check_health(self) -> bool:
        code, _ = self._request("GET", "/api/config", timeout=5)
        return code == 200

    def check_auth(self) -> bool:
        code, _ = self.get("/api/v1/files/")
        return code == 200

    def test_model(self, model_id: str) -> bool:
        code, _ = self.post_json(
            "/api/chat/completions",
            {
                "model": model_id,
                "messages": [{"role": "user", "content": "OK"}],
                "max_tokens": 5,
                "stream": False,
            },
            timeout=15,
        )
        return code == 200

    def list_knowledge(self) -> list[dict]:
        code, data = self.get("/api/v1/knowledge/")
        if code == 200 and isinstance(data, dict):
            return data.get("items", [])
        return []

    def delete_knowledge(self, kb_id: str) -> bool:
        code, _ = self.delete(f"/api/v1/knowledge/{kb_id}/delete")
        return code == 200

    def create_knowledge(self, name: str, description: str) -> Optional[str]:
        code, data = self.post_json(
            "/api/v1/knowledge/create",
            {"name": name, "description": description},
        )
        if code == 200 and isinstance(data, dict):
            return data.get("id")
        return None

    def add_file_to_knowledge(self, kb_id: str, file_id: str) -> bool:
        """Link a file to a KB. HTTP 200 is the source of truth — the response's
        `files` field is None in several OpenWebUI versions (known bug).
        """
        code, _data = self.post_json(
            f"/api/v1/knowledge/{kb_id}/file/add",
            {"file_id": file_id},
        )
        return code == 200

    def list_files(self) -> list[dict]:
        code, data = self.get("/api/v1/files/")
        if code != 200:
            return []
        if isinstance(data, dict) and "items" in data:
            return data["items"]
        if isinstance(data, list):
            return data
        return []

    def delete_file(self, file_id: str) -> bool:
        code, _ = self.delete(f"/api/v1/files/{file_id}")
        return code == 200

    def do_upload_file(self, filepath: Path) -> Optional[str]:
        code, body = self.upload_file("/api/v1/files/", filepath)
        try:
            data = json.loads(body) if isinstance(body, bytes) else body
        except (json.JSONDecodeError, TypeError):
            return None
        if isinstance(data, dict):
            return data.get("id")
        return None

    def list_models(self) -> list[dict]:
        code, data = self.get("/api/models")
        if code != 200:
            return []
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        if isinstance(data, list):
            return data
        return []

    def upsert_model(self, payload: dict) -> tuple[bool, str]:
        """Create or update a model preset. Returns (success, action)."""
        models = self.list_models()
        exists = any(m.get("id") == payload["id"] for m in models)

        if exists:
            code, data = self.post_json("/api/v1/models/model/update", payload)
            return code == 200, "updated"
        else:
            code, data = self.post_json("/api/v1/models/create", payload)
            return code == 200, "created"

    def delete_model(self, model_id: str) -> tuple[bool, bool]:
        """Delete a model preset by id. Returns (existed, ok)."""
        code, _ = self.delete(f"/api/v1/models/model/delete?id={model_id}")
        if code == 200:
            return True, True
        if code == 404:
            return False, True
        return False, False

    # ── RAG / embedding plumbing ────────────────────────────────────

    def get_embedding_config(self) -> dict:
        """Current embedding config. Empty dict if the endpoint is unavailable."""
        code, data = self.get("/api/v1/retrieval/embedding")
        if code == 200 and isinstance(data, dict):
            return data
        return {}

    def patch_embedding_config(self, payload: dict) -> bool:
        """Update embedding config. OpenWebUI uses POST /update on this endpoint."""
        code, _ = self.post_json("/api/v1/retrieval/embedding/update", payload)
        return code == 200

    def reset_kb_vectors(self, kb_id: str) -> bool:
        """Ask OpenWebUI to rebuild embeddings for a knowledge base.
        The endpoint name changes between versions; try the known variants."""
        for path in (
            f"/api/v1/knowledge/{kb_id}/reset",
            f"/api/v1/knowledge/{kb_id}/reindex",
        ):
            code, _ = self.post_json(path, {})
            if code == 200:
                return True
        return False

    def query_kb(
        self, kb_id: str, query: str, k: int = 5, timeout: float = 30.0
    ) -> dict:
        """Directly query a knowledge base via the retrieval endpoint.

        This hits OpenWebUI's native retrieval path (embed query + vector search),
        NOT /api/chat/completions — the chat endpoint does no RAG injection.

        Returns dict with 'ok' (bool), 'hits' (int), 'snippets' (list[str]),
        'distances' (list[float]), 'code' (int).
        """
        result = {"ok": False, "hits": 0, "snippets": [], "distances": [], "code": 0}
        code, data = self.post_json(
            "/api/v1/retrieval/query/collection",
            {
                "query": query,
                "collection_names": [kb_id],
                "k": k,
            },
            timeout=timeout,
        )
        result["code"] = code
        if code != 200 or not isinstance(data, dict):
            return result

        docs = data.get("documents") or []
        dists = data.get("distances") or []
        # OpenWebUI wraps in one list per collection, unwrap:
        if docs and isinstance(docs[0], list):
            docs = docs[0]
        if dists and isinstance(dists[0], list):
            dists = dists[0]

        result["snippets"] = [str(d) for d in docs]
        result["distances"] = [float(x) for x in dists if isinstance(x, (int, float))]
        result["hits"] = len(result["snippets"])
        result["ok"] = result["hits"] > 0
        # Diagnostic: if the endpoint returned 200 but we got nothing, surface
        # the top-level shape so troubleshooting isn't a blind exercise.
        if result["hits"] == 0 and isinstance(data, dict):
            result["response_keys"] = sorted(data.keys())
        return result


# ── Export mode ─────────────────────────────────────────────────────

def run_export(repo: Path, cfg: dict, flat: bool = False, out_dir: Optional[str] = None) -> None:
    """Export a knowledge pack for manual platform setup (Lumo etc.)."""
    project = cfg["project"]
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    base = Path(out_dir) if out_dir else repo / ".exports"
    slug = project.lower().replace(" ", "-")
    dest = base / f"{slug}-knowledge-pack-{stamp}"
    know_dir = dest / "knowledge"
    sys_dir = dest / "system"

    kb_files = discover_knowledge_files(repo, cfg)
    mp_path = repo / cfg["masterprompt"]

    if not mp_path.exists():
        print_error(f"Masterprompt not found: {cfg['masterprompt']}")
        sys.exit(1)

    print_header(f"{project} – Export Knowledge Pack")

    know_dir.mkdir(parents=True, exist_ok=True)
    sys_dir.mkdir(parents=True, exist_ok=True)

    if flat:
        # Flat mode: numbered files, no subdirs
        for i, fp in enumerate(kb_files, 1):
            dst = know_dir / f"{i:02d}-{fp.name}"
            shutil.copy2(fp, dst)
            print_ok(f"[{i}/{len(kb_files)}] {dst.name}")
    else:
        # Structured: preserve relative paths
        for i, fp in enumerate(kb_files, 1):
            try:
                rel = fp.relative_to(repo)
            except ValueError:
                rel = Path(fp.name)
            dst = know_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(fp, dst)
            print_ok(f"[{i}/{len(kb_files)}] {rel}")

    # Copy masterprompt
    shutil.copy2(mp_path, sys_dir / "SYSTEM_PROMPT_ONLY.md")
    print_ok(f"System prompt: system/SYSTEM_PROMPT_ONLY.md")

    # Generate setup instructions
    _write_setup_readme(dest, cfg, len(kb_files), flat)
    print_ok("Setup instructions: SETUP-ANLEITUNG.md")

    print()
    print_info(f"Export complete: {dest}")
    print_info(f"Knowledge files: {len(kb_files)}")
    print_info(f"Total size: {_dir_size_human(dest)}")
    print()

    # Gitignore exports
    gitignore = base / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n", encoding="utf-8")


def _write_setup_readme(dest: Path, cfg: dict, file_count: int, flat: bool) -> None:
    """Write a human-readable setup guide into the export pack."""
    project = cfg["project"]
    params = cfg.get("params", {})
    suggestions = cfg.get("suggestions", [])
    start_cmd = suggestions[0] if suggestions else "Start"
    default_model = cfg.get("default_model", "anthropic/claude-sonnet-4.6")
    preset_name = cfg.get("preset_name", project)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    flat_note = ""
    if flat:
        flat_note = (
            "\n  Die Dateien sind nummeriert und liegen alle in einem Ordner —\n"
            "  perfekt für Plattformen die keine Unterordner unterstützen.\n"
        )

    lines = [
        f"# {project} – Setup-Anleitung",
        "",
        f"Dieses Paket enthält alles, um {project} auf einer beliebigen",
        "KI-Plattform einzurichten.",
        "",
        "## Inhalt",
        "",
        f"- `knowledge/` — {file_count} Wissensdateien → ins **Projektwissen**",
    ]
    if flat_note:
        lines.append(flat_note.rstrip())
    lines += [
        "- `system/SYSTEM_PROMPT_ONLY.md` → in die **Projekt-Anweisungen**",
        "- Diese Anleitung (`SETUP-ANLEITUNG.md`) → nur für dich, nicht hochladen",
        "",
        "**Wichtig:** Nur den Inhalt von `knowledge/` ins Projektwissen laden.",
        "Die Datei `SYSTEM_PROMPT_ONLY.md` und diese Anleitung gehören **nicht**",
        "in den Wissensspeicher. Wenn du auf Lumo einen Drive-Ordner verlinkst,",
        "verlinke nur den Ordner mit den Wissensdateien — nicht diesen Export-Ordner.",
        "",
        "## Einrichtung (allgemein)",
        "",
        "1. **Neues Projekt / Custom AI / Preset erstellen**",
        f"   Name: `{preset_name}`",
        "",
        "2. **Projekt-Anweisungen / System-Prompt setzen**",
        "   Inhalt von `system/SYSTEM_PROMPT_ONLY.md` komplett einfügen.",
        "",
        "3. **Projektwissen / Knowledge Base bestücken**",
        "   Alle Dateien aus `knowledge/` hochladen — sonst nichts.",
        "",
        "4. **Parameter (falls einstellbar)**",
        f"   - Temperature: {params.get('temperature', 0.8)}",
        f"   - Top-P: {params.get('top_p', 0.9)}",
        f"   - Frequency Penalty: {params.get('frequency_penalty', 0.3)}",
        f"   - Max Tokens: {params.get('max_tokens', 64000)}",
        "",
        "5. **Starten**",
        f"   Neuen Chat öffnen → `{start_cmd}`",
        "",
        "## Einrichtung auf Lumo (Proton)",
        "",
        f"1. **Proton Drive:** Ordner `{project}` erstellen.",
        f"2. **Nur** die Dateien aus `knowledge/` in diesen Drive-Ordner laden.",
        "   Nicht die Anleitung, nicht den Systemprompt — nur die Wissensdateien.",
        f"3. **Lumo:** Neues Projekt `{project}` erstellen.",
        "4. In **Anweisungen**: Inhalt von `system/SYSTEM_PROMPT_ONLY.md` einfügen.",
        f"5. **Projektwissen**: Den Drive-Ordner `{project}` verlinken.",
        "6. Websuche im Spielbetrieb **deaktivieren**.",
        f"7. Neuen Chat starten: `{start_cmd}`",
        "",
        "**Tipp:** Das Setup macht man am besten am Desktop. Danach kann man auf",
        "dem Handy einfach das Projekt öffnen und losspielen — Proton Drive",
        "synchronisiert automatisch.",
    ]

    # Save management section — use project-specific text if provided
    save_info = cfg.get("save_info")
    if save_info and isinstance(save_info, list):
        lines.append("")
        lines.extend(save_info)
    else:
        # Default: generic save management (ZEITRISS-style)
        lines += [
        "",
        "## Spielstände verwalten",
        "",
        "Beim Speichern (`!save` im HQ) erzeugt die KI einen JSON-Block.",
        "Auf Lumo wird dieser automatisch als Datei im Chat-Wissen abgelegt.",
        "",
        "### Solo",
        "",
        "Beim Laden in einem neuen Chat: **Alten Spielstand vorher entfernen**,",
        "falls noch einer im Chat-Wissen liegt. Sonst sieht die KI zwei Stände",
        "und versucht zu mergen statt sauber zu laden.",
        "Faustregel: Immer nur der **aktuelle** Spielstand im Chat-Wissen.",
        "",
        "### Gruppe",
        "",
        f"{project} ist ein Gruppenspiel! Mehrere Spielstände gleichzeitig",
        "einfügen ist gewollt — der erste Save setzt den Kampagnenrahmen,",
        "jeder weitere bringt seinen Charakter mit (Merge).",
        "",
        "Aber: **Nur aktuelle Stände einfügen.** Veraltete JSONs aus früheren",
        "Sessions vorher aus dem Chat-/Projektwissen löschen, sonst mischt",
        "die KI alte und neue Daten zusammen.",
        "",
        "### Aufräumen",
        "",
        "Nach längeren Spielphasen das Projektwissen prüfen und veraltete",
        "Spielstände löschen — nur den jeweils neuesten pro Charakter behalten.",
        ]

    lines += [
        "",
        "## Erwartungsmanagement",
        "",
        f"Das Referenz-Erlebnis ist aktuell `{default_model}`.",
        "Andere Modelle und Plattformen können bei Regeltreue und Tiefe abweichen.",
        "",
        "---",
        f"Erstellt am {stamp} mit setup.py",
    ]

    content = "\n".join(lines) + "\n"

    (dest / "SETUP-ANLEITUNG.md").write_text(content, encoding="utf-8")


def _dir_size_human(path: Path) -> str:
    total = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    if total < 1024:
        return f"{total} B"
    if total < 1024 * 1024:
        return f"{total / 1024:.1f} KB"
    return f"{total / (1024 * 1024):.1f} MB"


# ── Setup mode (OpenWebUI) ─────────────────────────────────────────

DEFAULT_EMBED_ENGINE = "sentence-transformers"
DEFAULT_EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def _ensure_embedding_engine(
    client: "APIClient",
    wanted: Optional[str],
    ollama_url: Optional[str],
    ollama_model: Optional[str],
) -> None:
    """Pre-flight: make sure a supported embedding engine is configured.

    Behaviour:
      - wanted == 'default' -> explicitly set sentence-transformers / MiniLM.
      - wanted == 'ollama'  -> set engine=ollama with model/url from args.
      - wanted is None      -> inspect current config, warn on mismatch,
                               never touch it.

    After any PATCH we read the config back and verify the change really landed
    (OpenWebUI silently keeps the old value in some error branches).
    Never raises: problems are reported but don't abort the whole setup.
    """
    current = client.get_embedding_config()
    engine = (current.get("RAG_EMBEDDING_ENGINE") or "").strip().lower()
    model = current.get("RAG_EMBEDDING_MODEL") or ""

    def _pretty(e: str, m: str) -> str:
        if not e:
            return "default (OpenWebUI built-in, z.B. MiniLM)"
        return f"{e} / {m or '?'}"

    print_info(f"Embedding-Engine aktuell: {_pretty(engine, model)}")

    def _apply_and_verify(label: str, payload: dict, expect_engine: str, expect_model: str) -> None:
        print_info(f"Setze Embedding-Engine auf {label}...")
        ok = client.patch_embedding_config(payload)
        if not ok:
            print_warn(f"Konnte Embedding-Engine nicht aktualisieren — weiter mit bestehender Config.")
            return
        # Read-after-write verify
        after = client.get_embedding_config()
        got_engine = (after.get("RAG_EMBEDDING_ENGINE") or "").strip().lower()
        got_model = (after.get("RAG_EMBEDDING_MODEL") or "").strip()
        if got_engine == expect_engine and (not expect_model or got_model == expect_model):
            print_ok(f"Embedding-Engine auf {label} gesetzt und verifiziert.")
        else:
            print_warn(
                f"Engine-Update nicht wirksam: wollte {expect_engine}/{expect_model or '?'}, "
                f"OpenWebUI meldet {got_engine or '(leer)'}/{got_model or '(leer)'}.\n"
                f"     Prüfe OpenWebUI Admin → Dokumente → Embedding Model."
            )

    if wanted == "default":
        if engine == DEFAULT_EMBED_ENGINE and model == DEFAULT_EMBED_MODEL:
            print_ok("Embedding-Engine bereits auf Default — nichts zu tun.")
            return
        _apply_and_verify(
            "Default (MiniLM)",
            {
                "embedding_engine": DEFAULT_EMBED_ENGINE,
                "embedding_model": DEFAULT_EMBED_MODEL,
            },
            DEFAULT_EMBED_ENGINE,
            DEFAULT_EMBED_MODEL,
        )
        return

    if wanted == "ollama":
        target_model = ollama_model or "nomic-embed-text"
        target_url = ollama_url or "http://host.docker.internal:11434"
        if engine == "ollama" and model == target_model:
            print_ok(f"Embedding-Engine bereits Ollama/{target_model} — nichts zu tun.")
            return
        _apply_and_verify(
            f"Ollama ({target_model} via {target_url})",
            {
                "embedding_engine": "ollama",
                "embedding_model": target_model,
                "ollama_config": {"url": target_url, "key": ""},
            },
            "ollama",
            target_model,
        )
        return

    # wanted is None — only warn if something looks fishy, never touch it
    if engine and engine not in ("ollama", "openai", "sentence-transformers"):
        print_warn(
            f"Unbekannte Embedding-Engine '{engine}'. Das Retrieval könnte fehlschlagen.\n"
            f"     Tipp: python setup.py --embedding default   (zurück auf OpenWebUI-Default)"
        )


def _run_verify_retrieval(
    client: "APIClient",
    kb_id: str,
    verify_cfg: dict,
) -> bool:
    """Run a canary retrieval against the freshly built KB.

    Queries the vector store directly (not the chat endpoint — that doesn't RAG).
    Returns True if retrieval is functional, False otherwise.
    Never raises; prints clear diagnostics.
    """
    query = verify_cfg.get("query") or verify_cfg.get("prompt")
    expect_any = verify_cfg.get("expect_any") or []
    expect_sources_min = max(1, int(verify_cfg.get("expect_sources_min") or 1))
    top_k = int(verify_cfg.get("top_k") or 5)

    if not query:
        print_info("Kein Verify-Query in setup.json — überspringe Retrieval-Check.")
        return True

    print_info(f"Retrieval-Check: query='{query[:60]}...' gegen KB {kb_id[:8]}...")
    result = client.query_kb(kb_id, query, k=top_k)

    if not result["ok"]:
        extra = ""
        if result.get("response_keys"):
            extra = f" [top-level-keys: {', '.join(result['response_keys'])}]"
        print_error(
            f"Retrieval-Check fehlgeschlagen (HTTP {result['code']}, hits={result['hits']}){extra}."
        )
        return False

    hits = result["hits"]
    joined = " \n".join(result["snippets"])
    hit_phrases = [p for p in expect_any if p in joined]

    # Compact snippet preview
    if result["snippets"]:
        preview = result["snippets"][0].strip().replace("\n", " ")[:140]
        print_info(f"Top-Treffer: {preview!r}")
    if result["distances"]:
        print_info(
            f"Hits: {hits}, Top-Distanzen: "
            + ", ".join(f"{d:.3f}" for d in result["distances"][:3])
        )
    if expect_any:
        print_info(f"Erwartete Phrasen gefunden: {hit_phrases or '—'}")

    ok_hits = hits >= expect_sources_min
    ok_phrase = bool(hit_phrases) if expect_any else True

    if ok_hits and ok_phrase:
        print_ok("KB-Retrieval funktioniert — Chunks gefunden und Regel-Phrase matched.")
        return True

    if not ok_hits:
        print_error(
            f"KB-Retrieval failed: nur {hits} Treffer zurückgegeben "
            f"(mindestens {expect_sources_min} erwartet). "
            "Meist: Embedding-Engine passt nicht zu den Vektoren."
        )
    if expect_any and not ok_phrase:
        print_error(
            "KB-Retrieval liefert zwar Treffer, aber keine erwartete Regel-Phrase. "
            "Chunking/Embedding liefert nur schwach passende Passagen."
        )

    print_info(
        "Troubleshooting:\n"
        "     • Embedding-Engine prüfen (Admin → Dokumente → Embedding Model)\n"
        "     • python setup.py --reset-embeddings     (Vektor-DB dieser KB neu bauen)\n"
        "     • python setup.py --embedding default    (zurück auf OpenWebUI-Default)"
    )
    return False


def run_setup(repo: Path, cfg: dict, opts: Optional[dict] = None) -> None:
    """Interactive OpenWebUI setup: KB + files + preset."""
    opts = opts or {}
    project = cfg["project"]

    print_header(f"{project} – OpenWebUI Setup")

    assume_yes = bool(opts.get("assume_yes"))

    # ── URL ──────────────────────────────────────────────────────────
    url = os.environ.get("OPENWEBUI_URL", "").strip()
    if not url:
        if assume_yes:
            url = "http://localhost:3000"
        else:
            url = input("  OpenWebUI URL [http://localhost:3000]: ").strip()
            if not url:
                url = "http://localhost:3000"

    # ── API Key ──────────────────────────────────────────────────────
    api_key = os.environ.get("OPENWEBUI_API_KEY", "").strip()
    if not api_key:
        env_model_key = f"{project.upper().replace(' ', '_').replace('-', '_')}_API_KEY"
        api_key = os.environ.get(env_model_key, "").strip()
    if not api_key:
        print()
        print(f"  OpenWebUI API-Key benötigt.")
        print(f"  (Erstellen unter: {url} → Einstellungen → Konto → API-Schlüssel)")
        print()
        api_key = getpass("  API-Key eingeben: ")
        if not api_key:
            print_error("Kein API-Key angegeben.")
            sys.exit(1)

    client = APIClient(url, api_key)

    # ── Connectivity ─────────────────────────────────────────────────
    print_info("Verbindung prüfen...")
    if not client.check_health():
        print_error(f"OpenWebUI nicht erreichbar: {url}")
        sys.exit(1)
    print_ok("OpenWebUI erreichbar")

    if not client.check_auth():
        print_error("API-Key ungültig oder nicht autorisiert.")
        sys.exit(1)
    print_ok("API-Key gültig")

    # ── Embedding-Engine Precheck ────────────────────────────────────
    _ensure_embedding_engine(
        client,
        wanted=opts.get("embedding"),
        ollama_url=opts.get("ollama_url"),
        ollama_model=opts.get("ollama_model"),
    )

    # ── Model selection ──────────────────────────────────────────────
    default_model = cfg.get("default_model", "anthropic/claude-sonnet-4.6")
    env_model_var = f"{project.upper().replace(' ', '_').replace('-', '_')}_MODEL"
    model = os.environ.get(env_model_var, "").strip()

    if not model:
        if assume_yes:
            model = default_model
            print_info(f"--yes: Verwende Default-Modell {model}")
        else:
            print()
            print(f"  {_c('1', 'Modell-Auswahl')}")
            print(f"  {project} läuft provider-neutral — das Modell wählst du selbst.")
            print(f"  Hinweis: Remote-Modelle können Kosten verursachen und Eingaben")
            print(f"  an Drittanbieter übermitteln. Keine sensiblen Daten in Prompts.")
            print()
            print(f"  [1] Empfohlen: {default_model}")
            print(f"  [2] Model-ID manuell eingeben")
            choice = input("  Auswahl [1/2] (Standard 1): ").strip() or "1"

            if choice == "1":
                model = default_model
                print_info(f"Prüfe Modell: {model}")
                if not client.test_model(model):
                    print_warn("Modell nicht erreichbar — trotzdem verwenden? (j/n)")
                    if input("  ").strip().lower() not in ("j", "y", "ja", "yes"):
                        model = input("  Alternative Model-ID: ").strip()
                        if not model:
                            print_error("Kein Modell angegeben.")
                            sys.exit(1)
            elif choice == "2":
                model = input("  Model-ID eingeben: ").strip()
                if not model:
                    print_error("Kein Modell angegeben.")
                    sys.exit(1)
            else:
                print_error(f"Ungültige Auswahl: {choice}")
                sys.exit(1)

    print_ok(f"Base Model: {model}")

    # ── Discover knowledge files ─────────────────────────────────────
    kb_files = discover_knowledge_files(repo, cfg)
    print_info(f"{len(kb_files)} Wissensdateien erkannt")

    # Size check
    for fp in kb_files:
        sz = fp.stat().st_size
        if sz > 150_000:
            print_warn(f"{fp.name}: {sz/1024:.0f} KB — über 150 KB, Indexierung könnte fehlschlagen")

    # ── Preset aufräumen (falls Upgrade die ID verwaist hat) ─────────
    preset_id = cfg["preset_id"]
    existed, ok = client.delete_model(preset_id)
    if existed and ok:
        print_ok(f"Altes Preset aufgeräumt (Id: {preset_id}).")
    elif not existed:
        print_info("Kein vorhandenes Preset mit dieser ID — Neuinstallation.")
    else:
        print_warn(f"Konnte altes Preset nicht aufräumen (Id: {preset_id}) — fahre trotzdem fort.")

    # ── Knowledge Base (destroy & recreate) ──────────────────────────
    kb_name = cfg.get("kb_name", f"{project} Wissensspeicher")
    kb_desc = cfg.get("kb_description", f"Wissensspeicher für {project}")

    print()
    print_info("Knowledge Base vorbereiten...")

    # Find and remove existing KBs with same name
    existing_kbs = [
        kb for kb in client.list_knowledge() if kb.get("name") == kb_name
    ]
    if existing_kbs:
        print_info(f"{len(existing_kbs)} bestehende KB(s) entfernen...")
        for kb in existing_kbs:
            if opts.get("reset_embeddings"):
                # Best-effort: drop the old vector collection *before* deleting
                # the KB entry, so Chroma doesn't leave an orphan directory
                # around. The rebuilt KB gets a brand-new collection UUID
                # anyway — the real embedding-engine fix goes through
                # --embedding default|ollama, not through this flag.
                client.reset_kb_vectors(kb["id"])
            client.delete_knowledge(kb["id"])

        # Clean up old files matching our filenames
        our_filenames = {fp.name for fp in kb_files}
        old_files = [
            f for f in client.list_files() if f.get("filename") in our_filenames
        ]
        if old_files:
            print_info(f"{len(old_files)} alte Dateien aufräumen...")
            for f in old_files:
                client.delete_file(f["id"])
            print_ok(f"{len(old_files)} alte Dateien entfernt")

    # Create new KB
    kb_id = client.create_knowledge(kb_name, kb_desc)
    if not kb_id:
        print_error("Knowledge Base konnte nicht erstellt werden.")
        sys.exit(1)
    action = "aktualisiert" if existing_kbs else "erstellt"
    print_ok(f"Knowledge Base {action} (ID: {kb_id[:12]}...)")

    # ── Upload files ─────────────────────────────────────────────────
    print()
    print_info(f"Lade {len(kb_files)} Dateien hoch...")
    print()

    uploaded_ids: list[str] = []
    errors = 0

    for i, fp in enumerate(kb_files, 1):
        file_id = client.do_upload_file(fp)
        if file_id:
            uploaded_ids.append(file_id)
            try:
                rel = fp.relative_to(repo)
            except ValueError:
                rel = fp.name
            print_ok(f"[{i}/{len(kb_files)}] {rel}")
        else:
            print_error(f"[{i}/{len(kb_files)}] {fp.name} — Upload fehlgeschlagen")
            errors += 1

    print()
    if errors:
        print_warn(f"{len(kb_files) - errors}/{len(kb_files)} Dateien hochgeladen ({errors} Fehler)")
    else:
        print_ok(f"Alle {len(kb_files)} Dateien hochgeladen")

    # ── Link files to KB ─────────────────────────────────────────────
    print_info("Verknüpfe Dateien mit Knowledge Base...")

    api_ok = 0
    api_fail = 0
    for fid in uploaded_ids:
        if client.add_file_to_knowledge(kb_id, fid):
            api_ok += 1
        else:
            # Retry once after short delay (indexing may still be running)
            time.sleep(1)
            if client.add_file_to_knowledge(kb_id, fid):
                api_ok += 1
            else:
                api_fail += 1

    # Truth source: HTTP 200 on /file/add means the link was persisted.
    # `GET /knowledge/{id}.files` is null across several OpenWebUI versions,
    # so we don't count on it. The real end-to-end signal is the Retrieval-Check
    # below — if it returns chunks from the expected files, linkage is good.
    expected = len(uploaded_ids)
    if api_fail == 0:
        print_ok(f"Alle {api_ok} Dateien verknüpft (HTTP 200)")
    else:
        print_warn(
            f"{api_ok}/{expected} Dateien via API verknüpft, "
            f"{api_fail} Fehler — Retrieval-Check zeigt gleich, ob’s trotzdem reicht."
        )

    # ── Model preset ─────────────────────────────────────────────────
    print()
    print_info("Model-Preset einrichten...")

    mp_path = repo / cfg["masterprompt"]
    if not mp_path.exists():
        print_error(f"Masterprompt nicht gefunden: {cfg['masterprompt']}")
        sys.exit(1)
    system_prompt = mp_path.read_text(encoding="utf-8")

    params = cfg.get("params", {})
    suggestions = [{"content": s} for s in cfg.get("suggestions", [])]

    # ── Profile image (docs/gameicon.png → data URL) ────────────────
    profile_image_url = ""
    icon_path = repo / "docs" / "gameicon.png"
    if icon_path.exists():
        with open(icon_path, "rb") as img_f:
            b64 = base64.b64encode(img_f.read()).decode()
        profile_image_url = f"data:image/png;base64,{b64}"
        print_ok(f"Game Icon geladen: {icon_path.name} ({icon_path.stat().st_size // 1024} KB)")
    else:
        print_info("Kein Game Icon gefunden (docs/gameicon.png) — übersprungen")

    payload = {
        "id": cfg["preset_id"],
        "name": cfg["preset_name"],
        "base_model_id": model,
        "meta": {
            "description": cfg.get("preset_description", ""),
            "profile_image_url": profile_image_url,
            "capabilities": None,
            "knowledge": [{"id": kb_id, "name": kb_name}],
            "suggestion_prompts": suggestions,
        },
        "params": {
            "system": system_prompt,
            "temperature": params.get("temperature", 0.8),
            "top_p": params.get("top_p", 0.9),
            "frequency_penalty": params.get("frequency_penalty", 0.3),
            "max_tokens": params.get("max_tokens", 64000),
        },
    }

    success, action = client.upsert_model(payload)
    if success:
        print_ok(f"Preset {action}: {cfg['preset_name']}")
    else:
        print_error("Preset konnte nicht erstellt/aktualisiert werden.")
        sys.exit(1)

    # ── Verify Retrieval ─────────────────────────────────────────────
    verify_cfg = cfg.get("verify") or {}
    verify_ok = True
    if opts.get("no_verify"):
        print_info("Retrieval-Check per --no-verify übersprungen.")
    elif not verify_cfg:
        print_info("Kein verify-Block in setup.json — Retrieval-Check übersprungen.")
    else:
        print()
        verify_ok = _run_verify_retrieval(client, kb_id, verify_cfg)

    # ── Summary ──────────────────────────────────────────────────────
    print()
    print_header("Setup abgeschlossen!" if verify_ok else "Setup abgeschlossen (mit Warnung)")
    print(f"  Preset:        {cfg['preset_name']}")
    print(f"  Base Model:    {model}")
    print(f"  Knowledge:     {len(kb_files)} Dateien")
    print(f"  Temperature:   {params.get('temperature', 0.8)}")
    print(f"  Top-P:         {params.get('top_p', 0.9)}")
    print(f"  Freq-Penalty:  {params.get('frequency_penalty', 0.3)}")
    print(f"  Max Tokens:    {params.get('max_tokens', 64000)}")
    print()

    start_cmd = cfg.get("suggestions", ["Start"])[0]
    print(f"  So geht's weiter:")
    print(f"  1. Öffne {url} im Browser")
    print(f"  2. Starte einen neuen Chat")
    print(f"  3. Wähle das Modell \"{cfg['preset_name']}\"")
    print(f"  4. Tippe: {start_cmd}")
    print()

    if not verify_ok:
        print_warn(
            "Retrieval-Check war nicht eindeutig grün. "
            "Die SL antwortet zwar, zieht aber evtl. keine KB-Fakten.\n"
            "     Nächster Versuch: python setup.py --reset-embeddings"
        )
        if opts.get("strict"):
            # Opt-in: some users wrap this script in CI — Exit 2 so automation
            # notices the warning. Default stays on 0 for doppelklick-friendly
            # behaviour.
            sys.exit(2)


# ── Main ────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Universal setup for OpenWebUI-based AI projects.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python setup.py                          # OpenWebUI setup (interactive)
              python setup.py --export                 # Export knowledge pack
              python setup.py --export --flat          # Flat export (no subdirs)
              python setup.py --export -o ~/Desktop/pack  # Export to custom dir
              python setup.py --reset-embeddings       # Clean orphan vectors
              python setup.py --strict                 # Exit 2 on verify fail (CI)
              python setup.py --embedding ollama       # Force Ollama as embedder
              python setup.py --no-verify              # Skip retrieval check
        """),
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export knowledge pack instead of OpenWebUI setup",
    )
    parser.add_argument(
        "--flat",
        action="store_true",
        help="Flat export: numbered files, no subdirectories",
    )
    parser.add_argument(
        "-o", "--output",
        help="Output directory for export (default: .exports/)",
    )
    parser.add_argument(
        "--embedding",
        choices=["default", "ollama"],
        help=(
            "Embedding-Engine vor dem Setup erzwingen. "
            "'default' = OpenWebUI Built-in (empfohlen für Normalos), "
            "'ollama' = lokales Ollama mit nomic-embed-text."
        ),
    )
    parser.add_argument(
        "--ollama-url",
        default=None,
        help="Ollama-URL (nur mit --embedding ollama, Default: http://host.docker.internal:11434).",
    )
    parser.add_argument(
        "--ollama-model",
        default=None,
        help="Ollama-Embedding-Modell (Default: nomic-embed-text).",
    )
    parser.add_argument(
        "--reset-embeddings",
        action="store_true",
        help="Vektor-Collection dieser KB vor dem Rebuild zurücksetzen.",
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Retrieval-Check nach Setup überspringen (nicht empfohlen).",
    )
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Keine Rückfragen stellen (für automatisierte Läufe).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit-Code 2 bei fehlgeschlagenem Retrieval-Check (für CI/CD).",
    )
    args = parser.parse_args()

    repo = find_repo_root()
    cfg = load_config(repo)

    if args.export:
        run_export(repo, cfg, flat=args.flat, out_dir=args.output)
    else:
        run_setup(
            repo,
            cfg,
            opts={
                "embedding": args.embedding,
                "ollama_url": args.ollama_url,
                "ollama_model": args.ollama_model,
                "reset_embeddings": args.reset_embeddings,
                "no_verify": args.no_verify,
                "assume_yes": args.yes,
                "strict": args.strict,
            },
        )


if __name__ == "__main__":
    main()
