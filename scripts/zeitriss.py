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
Ziel: Spieler müssen sich keine Kommandozeilen-Befehle merken.

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

try:
    import rite as rite_module  # noqa: E402  (Lore-Overlay: nur Prolog + Finale)
except ImportError:
    # Rite ist optional — ohne läuft der Launcher weiter wie bisher.
    rite_module = None  # type: ignore[assignment]


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


def _open_browser(url: str) -> bool:
    """Versucht den Default-Browser auf ``url`` zu öffnen. Gibt True zurück,
    wenn's geklappt hat (bzw. beim OS keine Exception flog).

    Auf Headless-Linux ohne DISPLAY/WAYLAND_DISPLAY wird bewusst nichts
    versucht — wir wollen keine ominose Fehlermeldung produzieren.
    """
    if sys.platform.startswith("linux") and not (
        os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
    ):
        return False
    try:
        return bool(webbrowser.open(url))
    except Exception:
        return False


def _python_ok() -> tuple[bool, str]:
    # Wir laufen ja gerade in Python, also OK — aber melde Version.
    return True, f"Python {sys.version_info.major}.{sys.version_info.minor}"


def _docker_daemon_hint() -> str:
    """Plattform-passende Erinnerung, wie man Docker startet."""
    if sys.platform == "win32":
        return "Öffne Docker Desktop (Wal-Icon in der Taskleiste) und warte 1–2 Minuten, bis es läuft"
    if sys.platform == "darwin":
        return "Öffne Docker Desktop (Wal-Icon in der Menu-Bar) und warte, bis der Status 'Docker Desktop is running' ist"
    # Linux
    return "Starte den Docker-Daemon, z. B. 'sudo systemctl start docker'"


def _docker_ok() -> tuple[bool, str]:
    if not _cmd_available("docker"):
        return False, "Docker nicht installiert (Download: https://docs.docker.com/get-docker/)"
    try:
        r = subprocess.run(
            ["docker", "ps"],
            capture_output=True, text=True, timeout=5,
        )
    except Exception as e:
        return False, f"docker-Aufruf fehlgeschlagen: {e.__class__.__name__}"
    if r.returncode != 0:
        return False, f"Docker-Daemon läuft nicht. {_docker_daemon_hint()}"
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


def action_install_lore() -> None:
    """Menüpunkt Lore-Setup: Prolog → klassisches Setup → Finale.

    Ruft exakt denselben ``action_install`` wie der Standard-Menüpunkt,
    nur eingerahmt in Kodex-Prolog (vorher) und Welcome-Box (hinterher).
    Wenn das Rite-Modul nicht importierbar ist, fallen wir stumm auf
    den klassischen Flow zurück.
    """
    if rite_module is None:
        action_install()
        return

    url = _openwebui_url()
    try:
        rite_module.prologue(url)
    except Exception as e:
        # Lore darf Installation niemals blockieren. Wenn der Prolog
        # crasht, ganz kurz melden und normal weitermachen.
        print(dim(f"  (Lore-Prolog übersprungen: {e.__class__.__name__})"))

    # Installation läuft 1:1 wie beim Standard-Menüpunkt. Alle Fehler-
    # meldungen, Retries und Prompts von setup.py bleiben sichtbar.
    action_install()

    # Finale nur, wenn die Installation wirklich durchlief. Wir erkennen
    # das daran, dass Preset + OWUI-Key jetzt vorhanden sind.
    try:
        cfg = load_cfg()
        if not os.environ.get("OPENWEBUI_API_KEY"):
            return
        client = setup_module.APIClient(url, os.environ["OPENWEBUI_API_KEY"])
        preset = client.get_model(cfg["preset_id"])
        if preset is None:
            return
        rite_module.finale(url)
    except Exception:
        # Lore-Finale ist Kosmetik, niemals ein harter Fehler.
        return


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
        url = _openwebui_url()
        print(yellow("\n  🌐 Jetzt bist du kurz im Browser dran — drei Schritte (A→B→C):"))
        print()
        print(bold("  A) Admin-Account in OpenWebUI anlegen"))
        print(f"     OpenWebUI öffnet sich auf {url}")
        print("     Benutzername + Passwort setzen — bleibt rein lokal.")
        print()
        print(bold("  B) OpenRouter-Key als Connection in OpenWebUI eintragen"))
        print("     Profil-Icon oben rechts → Einstellungen → Verbindungen")
        print("     → '+ Verbindung hinzufügen' (engl.: '+ Add Connection'):")
        print("       Base URL:  https://openrouter.ai/api/v1")
        print("       API-Key:   dein 'sk-or-v1-...' von https://openrouter.ai/keys")
        print("     Speichern.")
        print()
        print(bold("  C) OpenWebUI-API-Key für mich erzeugen"))
        print("     (brauche ich gleich, um Preset + Knowledge Base anzulegen)")
        print("     Profil-Icon → Einstellungen → Account → API Keys")
        print("     → 'Create new key' → Key kopieren.")
        print()
        # Browser-Komfort: nur öffnen, wenn eine Anzeige verfügbar scheint.
        if _open_browser(url):
            print(dim("  (Den Browser habe ich dir schon geöffnet.)"))
        print()
        print(yellow("  ⏸️  Ich warte hier, während du A+B+C erledigst. Danach Key unten einfügen."))
        print()
        print(dim("  (Einfügen: Windows CMD Rechtsklick, macOS Cmd+V, Linux Ctrl+Shift+V.)"))
        from getpass import getpass
        key = getpass("  OpenWebUI-API-Key hier einfügen (Eingabe ist unsichtbar, das ist normal): ").strip()
        if not key:
            print(red("  Kein Key eingegeben, Abbruch."))
            _pause()
            return
        os.environ["OPENWEBUI_API_KEY"] = key
        os.environ.setdefault("OPENWEBUI_URL", url)

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
        print(yellow("  Voraussetzung: bei OpenRouter unter 'settings/privacy' den Provider"))
        print(yellow("  'Anthropic' (oder AWS Bedrock) explizit erlauben — sonst cached LiteLLM nicht."))
        print(yellow("  Direktlink: https://openrouter.ai/settings/privacy"))
        ans = _prompt("  Aktivieren? (j/n): ").lower()
        if ans in ("j", "y", "ja", "yes", ""):
            try:
                setup_module.run_install_litellm(REPO, load_cfg())
            except SystemExit:
                pass
            except Exception as e:
                print(red(f"\n  LiteLLM-Install fehlgeschlagen: {e.__class__.__name__}: {e}"))

    _pause()


def _git(*args: str) -> subprocess.CompletedProcess:
    """Thin wrapper: git -C REPO <args>, erfasst stdout+stderr."""
    return subprocess.run(
        ["git", "-C", str(REPO), *args],
        capture_output=True, text=True,
    )


def _update_repo_via_git() -> bool:
    """Führt einen freundlichen git pull durch. Bei lokalen Änderungen bietet
    das Script ``git stash`` an, zieht, und stasht dann wieder auf.

    Ziel: Der Nutzer verliert **nie** seine Handgriffe, auch wenn er aus
    Versehen eine Datei editiert hat. Aber er muss auch nichts mergen.

    Returns:
        True, wenn das Repo jetzt in einem konsistenten Zustand ist und
        der nachfolgende Sync sinnvoll weiterlaufen kann.
        False, wenn ein Konflikt/Fehler Aufmerksamkeit braucht (etwa
        Stash-Pop-Konflikt mit Marker in Dateien) — Caller sollte
        den Sync dann NICHT blind starten.
    """
    print(dim("  Hole neueste Änderungen von GitHub..."))

    # Lokale Anpassungen (tracked only, untracked bleiben unberührt).
    dirty = _git("status", "--porcelain", "--untracked-files=no").stdout.strip()
    stashed = False
    if dirty:
        print(yellow("  ⚠  Du hast lokale Änderungen an Dateien aus dem Repo."))
        print(dim("     Damit der Pull nicht kracht, lege ich sie kurz auf den Stash-Stack"))
        print(dim("     und stelle sie danach wieder her (git stash)."))
        ans = _prompt("  Fortfahren? (j/n): ").lower()
        if ans not in ("j", "y", "ja", "yes", ""):
            print(dim("  Pull übersprungen, Sync läuft mit lokalem Stand weiter."))
            return True
        r = _git("stash", "push", "-m", "zeitriss.py auto-stash")
        if r.returncode != 0:
            print(yellow("  ⚠  git stash fehlgeschlagen — überspringe Pull, behalte lokalen Stand."))
            print(dim("    " + (r.stderr.strip().splitlines() or ["?"])[-1]))
            return True
        stashed = True

    r = _git("pull", "--ff-only")
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        if "Bereits aktuell" in out or "Already up to date" in out:
            print(green("  ✓  Repo war schon aktuell."))
        else:
            print(green("  ✓  Repo aktualisiert."))
            print(dim("    " + "\n    ".join(out.splitlines()[-4:])))
    else:
        # Pull fehlgeschlagen (Netz, DNS, non-FF). Nach unserem Stash sollte
        # non-FF eigentlich nicht mehr vorkommen, aber wir handhaben es trotzdem.
        last_line = (out.splitlines() or ["?"])[-1]
        print(yellow(f"  ⚠  git pull hat Probleme: {last_line}"))
        print(dim("    Sync läuft trotzdem weiter mit dem lokalen Stand."))

    if stashed:
        r = _git("stash", "pop")
        if r.returncode == 0:
            print(dim("  ✓  Deine lokalen Änderungen sind zurück aus dem Stash."))
        else:
            # Heiß: stash pop hat einen Merge-Konflikt erzeugt. Die Arbeitsdateien
            # enthalten jetzt <<<<<<< / ======= / >>>>>>> Marker, der Stash
            # bleibt im Stack. Sync darf hier NICHT weiterlaufen — sonst
            # syncen wir kaputte Dateien.
            print()
            print(red("  ✗  Deine Änderungen kollidieren mit dem Update von GitHub."))
            print(yellow("     Die betroffenen Dateien enthalten jetzt Konflikt-Marker"))
            print(yellow("     (<<<<<<< / ======= / >>>>>>>) und müssen manuell aufgelöst werden."))
            print(dim(""))
            print(dim("     Eine sichere Kopie deiner Änderungen liegt im Stash. Hilfreiche Kommandos:"))
            print(dim("       git status               — zeigt die konflikt-Dateien"))
            print(dim("       git stash list           — zeigt deinen Stash-Eintrag"))
            print(dim("       git stash show -p        — zeigt deinen Original-Diff"))
            print(dim("       git checkout -- <datei>  — verwirft deine lokale Variante"))
            print(dim("       git stash drop           — entsorgt den Stash, wenn du fertig bist"))
            print()
            print(yellow("  Ich brich den Sync hier ab, damit nichts Kaputtes nach OpenWebUI wandert."))
            return False
    return True


def action_update() -> None:
    print(bold("\n  [2] ZEITRISS aktualisieren\n"))

    # Git-Pull (nur wenn Repo git-versioniert)
    if (REPO / ".git").exists() and _cmd_available("git"):
        if not _update_repo_via_git():
            # Stash-Pop-Konflikt o.ä. — Sync überspringen, damit wir nicht gegen
            # konflikt-markierte Dateien pushen.
            _pause()
            return
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


def _parse_env_file(path: Path) -> dict[str, str]:
    """Liest eine ~/.openwebui_env-artige Datei ein, tolerant gegen
    `export`-Prefix und Quotes. Gibt {KEY: VALUE} zurück (Kommentare/leere
    Zeilen ignoriert).
    """
    result: dict[str, str] = {}
    if not path.exists():
        return result
    try:
        for line in path.read_text("utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export "):]
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k:
                result[k] = v
    except OSError:
        pass
    return result


def _mask(secret: str) -> str:
    """Maskiert einen Key für die Anzeige: zeigt nur die letzten 4 Zeichen."""
    if not secret:
        return "(leer)"
    if len(secret) <= 4:
        return "*" * len(secret)
    return f"…{secret[-4:]}"


def action_rekeys() -> None:
    print(bold("\n  [3] API-Keys neu verbinden\n"))

    home_env = Path.home() / ".openwebui_env"
    existing = _parse_env_file(home_env)

    if existing:
        print("  Ich habe bereits gespeicherte Werte gefunden:")
        if "OPENWEBUI_URL" in existing:
            print(f"    • OpenWebUI-URL:       {existing['OPENWEBUI_URL']}")
        if "OPENWEBUI_API_KEY" in existing:
            print(f"    • OpenWebUI-API-Key:   {_mask(existing['OPENWEBUI_API_KEY'])}")
        if "OPENROUTER_API_KEY" in existing:
            print(f"    • OpenRouter-Key:      {_mask(existing['OPENROUTER_API_KEY'])}")
        print()
        print(dim("  Enter = vorhandenen Wert behalten. Neue Eingabe = überschreiben."))
    else:
        print("  Keine gespeicherten Werte gefunden — lege neue Datei an.")
    print()

    default_url = existing.get("OPENWEBUI_URL") or _openwebui_url()
    url = _prompt(f"  OpenWebUI-URL [{default_url}]: ").strip() or default_url

    from getpass import getpass
    existing_owui = existing.get("OPENWEBUI_API_KEY", "")
    owui_hint = f" (Enter = behalten: {_mask(existing_owui)})" if existing_owui else ""
    owui_input = getpass(f"  OpenWebUI-API-Key{owui_hint} (Eingabe unsichtbar): ").strip()
    owui_key = owui_input or existing_owui
    if not owui_key:
        print(red("  Kein Key eingegeben. Abbruch."))
        _pause()
        return

    existing_or = existing.get("OPENROUTER_API_KEY", "")
    or_hint = f" (Enter = behalten: {_mask(existing_or)})" if existing_or else " (leer lassen, um zu überspringen)"
    or_input = getpass(f"  OpenRouter-API-Key (sk-or-...){or_hint}: ").strip()
    or_key = or_input or existing_or

    lines = [
        "# Von zeitriss.py geschrieben - vom Launcher automatisch gelesen.",
        f"OPENWEBUI_URL={url}",
        f"OPENWEBUI_API_KEY={owui_key}",
    ]
    if or_key:
        lines.append(f"OPENROUTER_API_KEY={or_key}")
    home_env.write_text("\n".join(lines) + "\n", encoding="utf-8")

    try:
        home_env.chmod(0o600)
    except OSError:
        # Windows-NTFS: chmod wirkungslos; bewusst stumm (keine Panik-Warn für den Nutzer).
        pass

    print(green(f"\n  ✓  Keys gespeichert in {home_env}"))
    os.environ["OPENWEBUI_URL"] = url
    os.environ["OPENWEBUI_API_KEY"] = owui_key
    if or_key:
        os.environ["OPENROUTER_API_KEY"] = or_key
    _pause()


def _extract_kb_id(preset: dict) -> Optional[str]:
    """Zieht die erste KB-ID aus dem Preset-Meta. Tolerant gegen
    unterschiedliche Formate: Liste von Dicts mit ``id``, Liste von Strings,
    oder — wenn etwas exotisch ist — None statt Crash.
    """
    meta = (preset.get("meta") or {}).get("knowledge")
    if not isinstance(meta, list) or not meta:
        return None
    first = meta[0]
    if isinstance(first, dict):
        kb_id = first.get("id")
    elif isinstance(first, str):
        kb_id = first
    else:
        return None
    return kb_id if isinstance(kb_id, str) and kb_id else None


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
                kb_id = _extract_kb_id(preset)
                if kb_id is None:
                    print(yellow("   !  Preset gefunden, aber KB-Verknüpfung konnte nicht gelesen werden — Format unerwartet"))
                else:
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
    if not _open_browser(url):
        print(yellow(f"  Konnte Browser nicht automatisch öffnen. Bitte manuell: {url}"))
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

def action_export() -> None:
    """Menupunkt [2]: Export-Paket für andere Chat-Plattformen erzeugen.

    Fragt Format (strukturiert / flat / beide), optional Ausgabe-Pfad,
    ruft setup.py:run_export() auf, zeigt Ergebnis und öffnet den
    Ausgabe-Ordner im Dateimanager, wenn möglich.
    """
    print(bold("\n  [2] Regelwerk woanders nutzen (Export-Paket erzeugen)\n"))
    print("  Ich packe das ZEITRISS-Regelwerk (Masterprompt + 19 Wissensmodule)")
    print("  in einen Ordner, den du manuell in deine Chat-Plattform (Lumo,")
    print("  Claude Projects, OpenAI Projects, ...) hochladen kannst.")
    print()
    print(yellow("  ⚠️  Das ist ein Best-Effort-Weg. Wir testen gegen OpenWebUI,"))
    print(yellow("     nicht gegen andere Plattformen. Regel-Glitches sind möglich."))
    print()
    print(bold("  Welches Format?"))
    print("   [1]  Strukturiert (Ordner mit Unterordnern core/, systems/, ...)")
    print(dim("        → für Plattformen mit Datei-Upload, die Ordner behalten"))
    print("   [2]  Flach (alle Dateien nummeriert in einem Ordner)")
    print(dim("        → für Plattformen ohne Ordner-Support (Claude Projects etc.)"))
    print("   [3]  Beides erzeugen")
    print("   [X]  Abbrechen")
    print()
    choice = _prompt("  Auswahl [1]: ").strip().lower() or "1"
    if choice in ("x", "q", "exit", "abbrechen"):
        print(dim("  Abgebrochen."))
        _pause()
        return
    if choice not in ("1", "2", "3"):
        print(yellow(f"  Unbekannte Auswahl: {choice!r} — abgebrochen."))
        _pause()
        return

    default_out = str(REPO / ".exports")
    out_input = _prompt(f"  Ausgabe-Ordner [{default_out}]: ").strip()
    out_dir = out_input or default_out

    print()
    cfg = load_cfg()
    modes = []
    if choice == "1":
        modes = [False]
    elif choice == "2":
        modes = [True]
    else:
        modes = [False, True]

    try:
        for flat in modes:
            setup_module.run_export(REPO, cfg, flat=flat, out_dir=out_dir)
    except SystemExit:
        pass
    except Exception as e:
        print(red(f"\n  Export fehlgeschlagen: {e.__class__.__name__}: {e}"))
        _pause()
        return

    print()
    print(bold("  Hinweise für den Import in deine Zielplattform:"))
    print("   • masterprompt.md kommt als SYSTEMPROMPT / Projekt-Anweisung")
    print("     in die Zielplattform — NICHT als Wissensdokument.")
    print("   • Die 19 Wissensmodule gehen als 'Wissen' / 'Projekt-Dateien' /")
    print("     'Knowledge' rein — je nachdem wie die Plattform das nennt.")
    print("   • Ohne retrieval-fähige Plattform wird's unzuverlässig.")
    print(dim("   • Plattform-spezifische Tipps: docs/setup-guide.md#portabler-export"))
    print()

    # Ordner im Dateimanager öffnen (plattform-spezifisch, best-effort)
    print(dim(f"  Falls der Dateimanager nicht öffnet (z. B. SSH/Headless):"))
    print(dim(f"  Pfad zum Kopieren: {out_dir}"))
    ans = _prompt("  Ausgabe-Ordner jetzt im Dateimanager öffnen? (j/n) [j]: ").strip().lower()
    if ans in ("", "j", "y", "ja", "yes"):
        _open_folder(out_dir)

    _pause()


def _open_folder(path: str) -> None:
    """Öffnet einen Ordner plattform-neutral im Dateimanager.

    Best-effort: schlägt still fehl, wenn kein Dateimanager verfügbar
    (z. B. Headless-SSH). Keine Exception raisen.
    """
    try:
        if sys.platform == "win32":
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", path], check=False)
        else:
            subprocess.run(["xdg-open", path], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(dim(f"  (Konnte Ordner nicht öffnen: {e.__class__.__name__} — manuell öffnen: {path})"))


def main() -> int:
    while True:
        banner()
        print_status_block()
        print()
        print(bold("  Was möchtest du tun?"))
        print()
        print(dim("  ── Installation ──────────────────────────────"))
        print("   [1]  Komplett-Setup in OpenWebUI (empfohlen)")
        print("   [L]  Lore-Setup — wie [1], eingerahmt als ITI-Bergung")
        print("   [2]  Regelwerk woanders nutzen (Export-Paket erzeugen)")
        print()
        print(dim("  ── Im Betrieb ───────────────────────────────"))
        print("   [3]  Spiel starten (Browser öffnen)")
        print("   [4]  ZEITRISS aktualisieren (git pull + Sync)")
        print("   [5]  API-Keys ändern")
        print("   [6]  Bei mir läuft was nicht (Diagnose)")
        print()
        print("   [X]  Beenden")
        print()
        choice = _prompt("  Auswahl: ").strip().lower()

        if choice == "1":
            action_install()
        elif choice == "l":
            action_install_lore()
        elif choice == "2":
            action_export()
        elif choice == "3":
            action_play()
        elif choice == "4":
            action_update()
        elif choice == "5":
            action_rekeys()
        elif choice == "6":
            action_diagnose()
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
