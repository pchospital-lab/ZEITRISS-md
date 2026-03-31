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
        code, data = self.post_json(
            f"/api/v1/knowledge/{kb_id}/file/add",
            {"file_id": file_id},
        )
        if code != 200 or not isinstance(data, dict):
            return False
        files = data.get("files") or []
        return len(files) > 0

    def list_files(self) -> list[dict]:
        code, data = self.get("/api/v1/files/")
        if code == 200 and isinstance(data, list):
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

def run_setup(repo: Path, cfg: dict) -> None:
    """Interactive OpenWebUI setup: KB + files + preset."""
    project = cfg["project"]

    print_header(f"{project} – OpenWebUI Setup")

    # ── URL ──────────────────────────────────────────────────────────
    url = os.environ.get("OPENWEBUI_URL", "").strip()
    if not url:
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

    # ── Model selection ──────────────────────────────────────────────
    default_model = cfg.get("default_model", "anthropic/claude-sonnet-4.6")
    env_model_var = f"{project.upper().replace(' ', '_').replace('-', '_')}_MODEL"
    model = os.environ.get(env_model_var, "").strip()

    if not model:
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

    link_ok = 0
    link_fail = 0
    for fid in uploaded_ids:
        if client.add_file_to_knowledge(kb_id, fid):
            link_ok += 1
        else:
            link_fail += 1

    if link_fail == 0:
        print_ok(f"Alle {link_ok} Dateien verknüpft")
    else:
        print_warn(
            f"{link_ok}/{len(uploaded_ids)} verknüpft ({link_fail} Fehler)"
            " — bitte in OpenWebUI prüfen"
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

    payload = {
        "id": cfg["preset_id"],
        "name": cfg["preset_name"],
        "base_model_id": model,
        "meta": {
            "description": cfg.get("preset_description", ""),
            "profile_image_url": "",
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

    # ── Summary ──────────────────────────────────────────────────────
    print()
    print_header("Setup abgeschlossen!")
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


# ── Main ────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Universal setup for OpenWebUI-based AI projects.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python setup.py                    # OpenWebUI setup (interactive)
              python setup.py --export           # Export knowledge pack
              python setup.py --export --flat    # Export flat (numbered, no subdirs)
              python setup.py --export -o ~/Desktop/pack  # Export to custom dir
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
    args = parser.parse_args()

    repo = find_repo_root()
    cfg = load_config(repo)

    if args.export:
        run_export(repo, cfg, flat=args.flat, out_dir=args.output)
    else:
        run_setup(repo, cfg)


if __name__ == "__main__":
    main()
