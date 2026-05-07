#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ZEITRISS – Plattform-unabhängiger Setup-Launcher.

Menü-Launcher für Windows / macOS / Linux. Ein Script, fünf Aufgaben:

    [1] Erstinstallation starten
    [2] ZEITRISS aktualisieren
    [3] API-Keys neu verbinden
    [4] Problem? Diagnose starten
    [5] Spiel starten (Browser öffnen)
    [X] Beenden

Der Launcher ersetzt `setup.py` nicht, er ruft dessen Funktionen auf.
Ziel: Spieler:innen müssen sich keine Kommandozeilen-Befehle merken.

Aufruf:
    python scripts/zeitriss.py
    ./zeitriss.sh              (Unix-Wrapper, delegiert hierher)
    zeitriss.bat               (Windows-Doppelklick, delegiert hierher)
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import urllib.request
import urllib.error
import webbrowser
from pathlib import Path
from typing import Optional


# ── Repo-Wurzel finden (same logic as setup.py) ──────────────────────

def find_repo_root() -> Path:
    """Walk up until setup.json is found."""
    here = Path(__file__).resolve()
    for candidate in [here.parent, *here.parents]:
        if (candidate / "setup.json").exists():
            return candidate
    if (Path.cwd() / "setup.json").exists():
        return Path.cwd()
    print("FEHLER: setup.json nicht gefunden. Bitte aus dem Repo-Root starten.")
    sys.exit(1)


REPO = find_repo_root()
# scripts/setup.py importieren, damit wir dessen run_setup / run_sync nutzen
sys.path.insert(0, str(REPO / "scripts"))

try:
    import setup as setup_module  # noqa: E402  (importiert nach sys.path-Mutation)
except ImportError as e:
    print(f"FEHLER: scripts/setup.py kann nicht importiert werden: {e}")
    sys.exit(1)


# ── Darstellung (Unicode-sparsam, Windows-cmd-kompatibel) ────────────

USE_COLOR = True
if os.environ.get("NO_COLOR"):
    USE_COLOR = False
elif sys.platform == "win32" and not os.environ.get("WT_SESSION"):
    # Alte Windows-Terminals (cmd ohne VT) können kein ANSI — schalte ab.
    USE_COLOR = os.environ.get("FORCE_COLOR") == "1"


def _col(code: str, text: str) -> str:
    if not USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def green(t: str) -> str: return _col("32", t)
def red(t: str) -> str: return _col("31", t)
def yellow(t: str) -> str: return _col("33", t)
def bold(t: str) -> str: return _col("1", t)
def dim(t: str) -> str: return _col("2", t)


def banner() -> None:
    line = "=" * 58
    print()
    print(bold(line))
    print(bold("  ZEITRISS - Installationshilfe"))
    print(bold(f"  Version {_read_version()}  |  Tech-Noir Zeitreise-RPG"))
    print(bold(line))


def _read_version() -> str:
    try:
        import json
        return json.loads((REPO / "setup.json").read_text("utf-8")).get("version", "?")
    except Exception:
        return "?"


# ── Status-Checks (schnell, nichts verändernd) ───────────────────────

def _cmd_available(name: str) -> bool:
    return shutil.which(name) is not None


def _python_ok() -> tuple[bool, str]:
    # Wir laufen ja gerade in Python, also OK — aber melde Version.
    return True, f"Python {sys.version_info.major}.{sys.version_info.minor}"


def _docker_ok() -> tuple[bool, str]:
    if not _cmd_available("docker"):
        return False, "docker nicht im PATH"
    try:
        r = subprocess.run(
            ["docker", "ps"],
            capture_output=True, text=True, timeout=5,
        )
    except Exception as e:
        return False, f"docker-Aufruf fehlgeschlagen: {e.__class__.__name__}"
    if r.returncode != 0:
        # Häufigster Fall: Docker Desktop nicht gestartet
        return False, "Docker-Dienst nicht gestartet"
    return True, "Docker läuft"


def _openwebui_url() -> str:
    return os.environ.get("OPENWEBUI_URL") or "http://localhost:8080"


def _openwebui_ok() -> tuple[bool, str]:
    url = _openwebui_url()
    try:
        with urllib.request.urlopen(f"{url}/api/version", timeout=3) as r:
            body = r.read().decode("utf-8", errors="replace")
        if '"version"' in body:
            return True, f"OpenWebUI erreichbar ({url})"
        return False, f"{url} antwortet, aber keine Version erkannt"
    except urllib.error.URLError:
        return False, f"{url} nicht erreichbar"
    except Exception as e:
        return False, f"Fehler bei {url}: {e.__class__.__name__}"


def _openrouter_key_status() -> tuple[bool, str]:
    # Wir haben keinen zuverlässigen lokalen Platz, wo der Key IMMER liegt.
    # Checke LiteLLM-.env (wenn LiteLLM im Standard-Setup installiert wurde)
    # oder die Umgebungsvariable.
    env_val = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if env_val.startswith("sk-or-"):
        return True, "OPENROUTER_API_KEY in der Umgebung gesetzt"
    litellm_env = REPO / "scripts" / "litellm" / ".env"
    if litellm_env.exists():
        try:
            for line in litellm_env.read_text("utf-8").splitlines():
                if line.startswith("OPENROUTER_API_KEY=") and len(line.split("=", 1)[1].strip()) > 10:
                    return True, f"in {litellm_env.relative_to(REPO)} hinterlegt"
        except Exception:
            pass
    return False, "nicht gefunden (weder Env noch LiteLLM-.env)"


def _owui_key_status() -> tuple[bool, str]:
    if os.environ.get("OPENWEBUI_API_KEY", "").strip():
        return True, "OPENWEBUI_API_KEY in der Umgebung"
    # ~/.openwebui_env auto-check
    home_env = Path.home() / ".openwebui_env"
    if home_env.exists():
        try:
            for line in home_env.read_text("utf-8").splitlines():
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                # "export X=Y" und "X=Y" beide unterstützen
                if line.startswith("export "):
                    line = line[len("export "):]
                if line.startswith("OPENWEBUI_API_KEY=") and len(line.split("=", 1)[1].strip()) > 10:
                    return True, f"in {home_env} hinterlegt"
        except Exception:
            pass
    return False, "nicht gefunden (weder Env noch ~/.openwebui_env)"


def _litellm_ok() -> tuple[bool, str]:
    # LiteLLM-Container aktiv?
    if not _cmd_available("docker"):
        return False, "Docker fehlt"
    try:
        r = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}", "--filter", "name=litellm"],
            capture_output=True, text=True, timeout=5,
        )
        names = [n.strip() for n in r.stdout.splitlines() if n.strip()]
        if names:
            return True, f"Container läuft: {', '.join(names)}"
    except Exception:
        pass
    return False, "kein litellm-Container aktiv"


def print_status_block() -> None:
    checks = [
        ("Python", _python_ok),
        ("Docker", _docker_ok),
        ("OpenWebUI", _openwebui_ok),
        ("OpenRouter-Key", _openrouter_key_status),
        ("OpenWebUI-Key", _owui_key_status),
        ("LiteLLM-Cache", _litellm_ok),
    ]
    print(bold("\n  Status:"))
    for name, fn in checks:
        try:
            ok, info = fn()
        except Exception as e:
            ok, info = False, f"Check-Fehler: {e.__class__.__name__}"
        mark = green("[OK]") if ok else red("[--]")
        print(f"   {mark}  {name:<16} {dim(info)}")


# ── Menü-Aktionen ────────────────────────────────────────────────────

def load_cfg() -> dict:
    return setup_module.load_config(REPO)


def _ensure_owui_env() -> bool:
    """Auto-lade ~/.openwebui_env in os.environ, wenn Keys fehlen.

    Returns True, wenn OPENWEBUI_API_KEY jetzt gesetzt ist (oder vorher schon war).
    Returns False, wenn auch nach Auto-Load nichts gefunden wurde.
    """
    if os.environ.get("OPENWEBUI_API_KEY", "").strip():
        return True
    home_env = Path.home() / ".openwebui_env"
    if not home_env.exists():
        return False
    try:
        for line in home_env.read_text("utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export "):]
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            # Nur setzen, wenn leer — bestehende Env-Werte nicht überschreiben
            if k and v and not os.environ.get(k):
                os.environ[k] = v
    except Exception as e:
        print(yellow(f"  Warnung: konnte {home_env} nicht lesen: {e}"))
        return False
    return bool(os.environ.get("OPENWEBUI_API_KEY", "").strip())


def action_install() -> None:
    print(bold("\n  [1] Erstinstallation\n"))
    print("  Was jetzt passiert:")
    print("   1. Voraussetzungen werden geprüft (Docker, Python, OpenWebUI).")
    print("   2. Das Regelwerk wird in OpenWebUI als Preset + Knowledge Base angelegt.")
    print("   3. Optional: LiteLLM-Cache-Container (spart ~90 % der Modellkosten).")
    print()

    ok, info = _docker_ok()
    if not ok:
        print(red(f"  ✗ Docker fehlt/läuft nicht: {info}"))
        print()
        print("  Bitte installiere Docker Desktop (Windows/macOS) oder Docker Engine (Linux),")
        print("  starte es und komm zurück. Anleitung: https://docs.docker.com/get-docker/")
        _pause()
        return

    ok, info = _openwebui_ok()
    if not ok:
        print(yellow(f"  ⚠  OpenWebUI ist nicht erreichbar: {info}"))
        print()
        print("  ZEITRISS braucht einen laufenden OpenWebUI-Container.")
        ans = _prompt("  Soll ich OpenWebUI jetzt starten? (j/n): ").lower()
        if ans in ("j", "y", "ja", "yes", ""):
            _start_openwebui()
        else:
            print(dim("  Abbruch. Erst OpenWebUI starten, dann nochmal Menü-Punkt [1]."))
            _pause()
            return

    if not _ensure_owui_env():
        print(yellow("\n  Ich brauche einen OpenWebUI-API-Key, um Preset + Knowledge Base anzulegen."))
        print(f"  Hol dir den Key in OpenWebUI unter {_openwebui_url()}/")
        print("  (Profil-Icon oben rechts → Einstellungen → Account → API-Keys → Create new key).")
        print()
        from getpass import getpass
        key = getpass("  Key hier einfügen (Eingabe ist unsichtbar, das ist normal): ").strip()
        if not key:
            print(red("  Kein Key eingegeben, Abbruch."))
            _pause()
            return
        os.environ["OPENWEBUI_API_KEY"] = key
        os.environ.setdefault("OPENWEBUI_URL", _openwebui_url())

    try:
        setup_module.run_setup(REPO, load_cfg())
    except SystemExit:
        pass
    except Exception as e:
        print(red(f"\n  Erstinstallation fehlgeschlagen: {e.__class__.__name__}: {e}"))
        _pause()
        return

    # LiteLLM-Anfrage nach Full-Setup — nur wenn noch kein litellm-Container läuft
    ok, _ = _litellm_ok()
    if not ok:
        print()
        print(bold("  LiteLLM-Cache aktivieren? (spart ~90 % Prompt-Kosten, sehr empfohlen)"))
        ans = _prompt("  Aktivieren? (j/n): ").lower()
        if ans in ("j", "y", "ja", "yes", ""):
            try:
                setup_module.run_install_litellm(REPO, load_cfg())
            except SystemExit:
                pass
            except Exception as e:
                print(red(f"\n  LiteLLM-Install fehlgeschlagen: {e.__class__.__name__}: {e}"))

    _pause()


def action_update() -> None:
    print(bold("\n  [2] ZEITRISS aktualisieren\n"))

    # Git-Pull (nur wenn Repo git-versioniert)
    if (REPO / ".git").exists() and _cmd_available("git"):
        print(dim("  Hole neueste Änderungen von GitHub..."))
        r = subprocess.run(
            ["git", "-C", str(REPO), "pull", "--ff-only"],
            capture_output=True, text=True,
        )
        out = (r.stdout + r.stderr).strip()
        if r.returncode == 0:
            if "Bereits aktuell" in out or "Already up to date" in out:
                print(green("  ✓  Repo war schon aktuell."))
            else:
                print(green("  ✓  Repo aktualisiert."))
                print(dim("    " + "\n    ".join(out.splitlines()[-4:])))
        else:
            print(yellow(f"  ⚠  git pull hat Probleme: {out.splitlines()[-1] if out else '?'}"))
            print(dim("    Sync läuft trotzdem weiter mit dem lokalen Stand."))
    else:
        print(dim("  Kein Git-Repo (vermutlich ZIP-Download) - überspringe git pull."))

    # Env laden, dann Sync
    if not _ensure_owui_env():
        print(red("\n  OPENWEBUI_API_KEY fehlt - bitte erst einmal Menüpunkt [1] (Install)"))
        print(red("  oder [3] (Keys neu verbinden) ausführen, damit ~/.openwebui_env existiert."))
        _pause()
        return

    print()
    try:
        setup_module.run_sync(REPO, load_cfg())
    except SystemExit:
        pass
    except Exception as e:
        print(red(f"\n  Update fehlgeschlagen: {e.__class__.__name__}: {e}"))

    _pause()


def action_rekeys() -> None:
    print(bold("\n  [3] API-Keys neu verbinden\n"))
    print("  Hier hinterlegen wir die beiden Keys dauerhaft in `~/.openwebui_env`,")
    print("  damit du sie in Zukunft nicht mehr eintippen musst.")
    print()
    print(f"  OpenWebUI ist erreichbar unter: {_openwebui_url()}")
    print("  Hol den OpenWebUI-Key: Profil-Icon → Einstellungen → Account → API-Keys.")
    print()

    url = _prompt(f"  OpenWebUI-URL [{_openwebui_url()}]: ").strip() or _openwebui_url()

    from getpass import getpass
    owui_key = getpass("  OpenWebUI-API-Key (Eingabe unsichtbar): ").strip()
    if not owui_key:
        print(red("  Kein Key eingegeben. Abbruch."))
        _pause()
        return

    or_key = getpass("  OpenRouter-API-Key (sk-or-..., leer lassen um zu überspringen): ").strip()

    home_env = Path.home() / ".openwebui_env"
    lines = [
        "# Von zeitriss.py geschrieben - von Launcher automatisch gelesen.",
        f"OPENWEBUI_URL={url}",
        f"OPENWEBUI_API_KEY={owui_key}",
    ]
    if or_key:
        lines.append(f"OPENROUTER_API_KEY={or_key}")
    home_env.write_text("\n".join(lines) + "\n", encoding="utf-8")

    try:
        home_env.chmod(0o600)
    except Exception:
        # Windows-NTFS: chmod wirkungslos; bewusst stumm (kein Panik-Warn für Markus).
        pass

    print(green(f"\n  ✓  Keys gespeichert in {home_env}"))
    os.environ["OPENWEBUI_URL"] = url
    os.environ["OPENWEBUI_API_KEY"] = owui_key
    if or_key:
        os.environ["OPENROUTER_API_KEY"] = or_key
    _pause()


def action_diagnose() -> None:
    print(bold("\n  [4] Diagnose\n"))
    print_status_block()
    print()
    print("  Prüfungen im Detail:")

    # OpenWebUI-Smoke via API (nur wenn Env da)
    _ensure_owui_env()
    if not os.environ.get("OPENWEBUI_API_KEY"):
        print(yellow("   !  Kein OPENWEBUI_API_KEY - überspringe Preset- und KB-Check."))
    else:
        try:
            client = setup_module.APIClient(
                _openwebui_url(), os.environ["OPENWEBUI_API_KEY"]
            )
            if not client.check_health():
                print(red("   ✗  OpenWebUI /health antwortet nicht."))
            else:
                print(green("   ✓  OpenWebUI /health OK"))

            if not client.check_auth():
                print(red("   ✗  API-Key ungültig oder ohne Rechte."))
            else:
                print(green("   ✓  API-Key akzeptiert"))

            cfg = load_cfg()
            preset_id = cfg["preset_id"]
            preset = client.get_model(preset_id)
            if preset is None:
                print(red(f"   ✗  Preset '{preset_id}' existiert nicht (Install nötig?)"))
            else:
                print(green(f"   ✓  Preset '{preset.get('name', preset_id)}' gefunden"))
                meta = (preset.get("meta") or {}).get("knowledge") or []
                if meta and isinstance(meta, list):
                    kb_id = (meta[0].get("id") if isinstance(meta[0], dict) else meta[0])
                    if kb_id:
                        v_cfg = cfg.get("verify", {})
                        q = v_cfg.get("query", "")
                        if q:
                            result = client.query_kb(kb_id, q, k=v_cfg.get("top_k", 5))
                            hits = result.get("hits", 0)
                            if hits > 0:
                                print(green(f"   ✓  KB-Retrieval OK ({hits} Treffer)"))
                            else:
                                print(red("   ✗  KB-Retrieval lieferte 0 Treffer - vermutlich Sync nötig"))
        except Exception as e:
            print(red(f"   ✗  Diagnose-Fehler: {e.__class__.__name__}: {e}"))

    _pause()


def action_play() -> None:
    url = _openwebui_url()
    print(bold("\n  [5] Spiel starten\n"))
    ok, info = _openwebui_ok()
    if not ok:
        print(red(f"  OpenWebUI ist nicht erreichbar: {info}"))
        print(f"  Starte Docker und OpenWebUI, dann nochmal.")
        _pause()
        return
    print(f"  Öffne Browser auf {url} ...")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(yellow(f"  Konnte Browser nicht öffnen ({e}). Bitte manuell: {url}"))
    print(dim("  In OpenWebUI: Neuer Chat → Modell 'ZEITRISS v4.2.6 Uncut' wählen → 'Spiel starten (solo klassisch)'"))
    _pause()


# ── Utilities ────────────────────────────────────────────────────────

def _prompt(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:
        return ""


def _pause() -> None:
    try:
        input(dim("\n  Weiter mit Enter..."))
    except EOFError:
        pass


def _start_openwebui() -> None:
    """Startet einen OpenWebUI-Container mit den bewährten Flags.

    Defensiv: wird außer von action_install() ggf. auch an anderen Stellen
    aufgerufen, daher hier eigener Docker-Check — nicht blind auf den
    Caller vertrauen.
    """
    if not _cmd_available("docker"):
        print(red("  Docker ist nicht installiert — OpenWebUI kann nicht gestartet werden."))
        return
    # Check, ob bereits ein Container existiert (nur gestoppt)
    r = subprocess.run(
        ["docker", "ps", "-a", "--format", "{{.Names}}", "--filter", "name=open-webui"],
        capture_output=True, text=True,
    )
    names = [n.strip() for n in r.stdout.splitlines() if n.strip()]

    if "open-webui" in names:
        print(dim("  Container 'open-webui' existiert bereits, starte ihn..."))
        subprocess.run(["docker", "start", "open-webui"], check=False)
    else:
        print(dim("  Erstelle neuen OpenWebUI-Container (das kann beim ersten Mal ~1-2 Minuten dauern)..."))
        cmd = [
            "docker", "run", "-d",
            "--name", "open-webui",
            "--restart", "always",
            "-p", "8080:8080",
            "-v", "open-webui:/app/backend/data",
            "ghcr.io/open-webui/open-webui:main",
        ]
        subprocess.run(cmd, check=False)

    # Warte auf healthy (max 60s)
    import time
    for i in range(12):
        time.sleep(5)
        ok, _ = _openwebui_ok()
        if ok:
            print(green(f"  ✓  OpenWebUI läuft ({i*5 + 5}s)"))
            return
    print(yellow("  ⚠  OpenWebUI startet noch. Gib ihm noch 30s und versuche dann nochmal."))


# ── Main-Loop ────────────────────────────────────────────────────────

def main() -> int:
    while True:
        banner()
        print_status_block()
        print()
        print(bold("  Was möchtest du tun?"))
        print("   [1]  Erstinstallation (Preset + Knowledge Base in OpenWebUI anlegen)")
        print("   [2]  ZEITRISS aktualisieren (git pull + Sync)")
        print("   [3]  API-Keys neu verbinden")
        print("   [4]  Problem? Diagnose starten")
        print("   [5]  Spiel starten (Browser öffnen)")
        print("   [X]  Beenden")
        print()
        choice = _prompt("  Auswahl: ").strip().lower()

        if choice == "1":
            action_install()
        elif choice == "2":
            action_update()
        elif choice == "3":
            action_rekeys()
        elif choice == "4":
            action_diagnose()
        elif choice == "5":
            action_play()
        elif choice in ("x", "q", "quit", "exit", ""):
            print(dim("\n  Bis bald, Chrononaut.\n"))
            return 0
        else:
            print(yellow(f"  Unbekannte Auswahl: {choice!r}"))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(dim("\n  Abgebrochen."))
        sys.exit(130)
