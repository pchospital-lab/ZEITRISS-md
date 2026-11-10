#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generischer Plattform-unabhängiger Setup-Launcher für OpenWebUI-Bausätze.

EIN Launcher-Core für beliebige OpenWebUI-Bausätze. Projekt-Identität
(Name, Tagline, „Starten"-Wording, Begrüßung) kommt aus dem optionalen
`launcher`-Block in setup.json — der Code selbst ist projekt-agnostisch
und in allen Repos byte-identisch.

Menü-Launcher für Windows / macOS / Linux. Ein Script, ein Menü:

    [1] Komplett-Setup in OpenWebUI (empfohlen)
    [L] Lore-Setup — nur wenn scripts/rite.py existiert
    [2] Inhalt woanders nutzen (Export-Paket erzeugen)
    [3] Starten (Browser öffnen)
    [4] Aktualisieren (git pull + Sync)
    [5] API-Keys ändern
    [6] Bei mir läuft was nicht (Diagnose)
    [7] Reset — Neuinstallation (destruktiv)
    [X] Beenden

Der Launcher ersetzt `setup.py` nicht, er ruft dessen Funktionen auf.
Ziel: Nutzer müssen sich keine Kommandozeilen-Befehle merken.

Aufruf (pro Repo via dünnem Shim scripts/<projekt>.py):
    python scripts/<projekt>.py
    ./<projekt>.sh             (Unix-Wrapper, delegiert hierher)
    <projekt>.bat              (Windows-Doppelklick, delegiert hierher)
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import urllib.request
import urllib.error
import webbrowser
from pathlib import Path
from typing import Optional

# UTF-8-Output sicherstellen — Windows-cmd läuft per Default mit cp1252/cp850,
# dann würde `print("✓")` mit UnicodeEncodeError crashen. Auf Python 3.7+
# kann man stdout/stderr nachträglich umkonfigurieren; bei älteren Python-
# Versionen oder exotischen Terminals fallen wir stumm zurück auf Replace-Modus,
# damit der Launcher lieber ein '?' statt eines Exceptions zeigt.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass


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

try:
    # Optionaler Projekt-Einstieg-Hook (P2/MMO-Sim, PLAN.md §2/§4 M3): der
    # generische Launcher-Core kennt keine MMO-Sim-Sonderfälle, nur diesen
    # einen optionalen Hook. Ohne das Modul läuft der Launcher unverändert
    # weiter (analog zum rite_module-Muster oben).
    import mmo_sim_launcher_hook as project_hook  # noqa: E402
except ImportError:
    project_hook = None  # type: ignore[assignment]


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
    m = meta()
    line = "=" * 58
    ver = _read_version()
    ver_part = f"Version {ver}  |  " if ver and ver != "?" else ""
    print()
    print(bold(line))
    print(bold(f"  {m['name']} - Launcher (Setup + Betrieb)"))
    print(bold(f"  {ver_part}{m['tagline']}"))
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
    """WP1c/PF1.4: unterscheidet, WARUM Docker nicht nutzbar ist, statt
    jeden Fehlschlag pauschal als "Daemon läuft nicht" zu melden — die
    nötige nächste Aktion ist für jeden Fall eine andere.

    Reihenfolge: (1) Engine fehlt ganz, (2) Compose-Plugin fehlt,
    (3) `docker ps` scheitert mit Permission-Hinweis (Nutzer nicht in der
    `docker`-Gruppe), (4) sonstiger `docker ps`-Fehlschlag (Daemon aus)."""
    if not _cmd_available("docker"):
        return False, "Docker-Engine fehlt (Download: https://docs.docker.com/get-docker/)"

    try:
        r_compose = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True, text=True, timeout=5,
        )
    except subprocess.TimeoutExpired:
        return False, "docker compose version hing fest (Timeout) — Docker-Daemon prüfen."
    except Exception as e:
        return False, f"docker-Aufruf fehlgeschlagen: {e.__class__.__name__}"
    if r_compose.returncode != 0:
        return False, "Docker Compose-Plugin fehlt (Installation: https://docs.docker.com/compose/install/)."

    try:
        r_ps = subprocess.run(
            ["docker", "ps"],
            capture_output=True, text=True, timeout=5,
        )
    except subprocess.TimeoutExpired:
        return False, "docker ps hing fest (Timeout) — Docker-Daemon prüfen."
    except Exception as e:
        return False, f"docker-Aufruf fehlgeschlagen: {e.__class__.__name__}"
    if r_ps.returncode != 0:
        stderr_l = (r_ps.stderr or "").lower()
        if "permission denied" in stderr_l or "dial unix" in stderr_l:
            return False, (
                "Kein Zugriff auf den Docker-Daemon (fehlende Gruppenrechte). "
                "Nutzer zur 'docker'-Gruppe hinzufügen: sudo usermod -aG docker $USER, "
                "danach neu einloggen (oder neuen Shell-Login starten)."
            )
        return False, f"Docker-Daemon läuft nicht. {_docker_daemon_hint()}"
    return True, "Docker läuft (inkl. Compose-Plugin)"



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
    # Der Key kann an drei Stellen liegen, in absteigender Priorität:
    #   1) Umgebungsvariable (höchste Priorität, überschreibt alles)
    #   2) ~/.openwebui_env (wo `action_rekeys` ihn hinschreibt)
    #   3) scripts/litellm/.env (wo `run_install_litellm` ihn hinschreibt)
    env_val = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if env_val.startswith("sk-or-"):
        return True, "OPENROUTER_API_KEY in der Umgebung gesetzt"
    home_env = Path.home() / ".openwebui_env"
    if home_env.exists():
        try:
            for line in home_env.read_text("utf-8").splitlines():
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                if line.startswith("export "):
                    line = line[len("export "):]
                if line.startswith("OPENROUTER_API_KEY="):
                    v = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if len(v) > 10:
                        return True, f"in {home_env} hinterlegt"
        except Exception:
            pass
    litellm_env = REPO / "scripts" / "litellm" / ".env"
    if litellm_env.exists():
        try:
            for line in litellm_env.read_text("utf-8").splitlines():
                if line.startswith("OPENROUTER_API_KEY=") and len(line.split("=", 1)[1].strip()) > 10:
                    return True, f"in {litellm_env.relative_to(REPO)} hinterlegt"
        except Exception:
            pass
    return False, "nicht gefunden (Env, ~/.openwebui_env, LiteLLM-.env)"


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


def _expected_litellm_container_name() -> Optional[str]:
    """Projektspezifischer Containername (`litellm-<project-slug>`, s.
    `setup.py:run_install_litellm`), z.B. `litellm-zeitriss` für dieses
    Projekt. `None`, wenn `setup.json` nicht lesbar ist."""
    try:
        cfg = load_cfg()
        return f"litellm-{setup_module._docker_slug(cfg['project'])}"
    except Exception:
        return None


def _litellm_ok() -> tuple[bool, str]:
    """WP1c/PF1.4: route-/projektgenau statt "irgendein litellm"-Container —
    ein fremder Container (z.B. `litellm-arxion` eines anderen Bausatzes)
    darf den benötigten ZEITRISS-Schritt NICHT als erledigt gelten lassen."""
    if not _cmd_available("docker"):
        return False, "Docker fehlt"
    expected = _expected_litellm_container_name()
    try:
        r = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}", "--filter", "name=litellm"],
            capture_output=True, text=True, timeout=5,
        )
        names = [n.strip() for n in r.stdout.splitlines() if n.strip()]
    except Exception:
        return False, "kein litellm-Container aktiv (Check fehlgeschlagen)"
    if not names:
        return False, "kein litellm-Container aktiv"
    if expected is None:
        # setup.json nicht lesbar -- kann die Route NICHT pruefen. WP-N2-1a:
        # das darf KEIN grosszuegiger Pass sein (sonst liesse ein laufender
        # Fremd-Container den Auto-Wire-Schritt uebersprungen zurueck, ohne
        # dass die Route je bestaetigt wurde) -- "nicht prüfbar" ist
        # ehrlicher als ein Fallback-"OK".
        return False, (
            f"setup.json nicht lesbar -- Route nicht prüfbar "
            f"(Container laufen: {', '.join(names)})"
        )
    if expected in names:
        return True, f"Container läuft: {expected}"
    return False, (
        f"läuft, aber nicht der für dieses Projekt erwartete Container "
        f"({', '.join(names)} statt {expected}) — gehört vermutlich zu einem anderen Bausatz."
    )


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


def _default_preset_id(cfg: dict) -> str:
    """Preset-ID der Default-Variante.

    Seit dem Multi-Variant-Umbau gibt es kein top-level `preset_id` mehr in
    setup.json (MODERN-Shape) — die Preset-IDs leben in `variants[<name>]`.
    `setup_module.load_config` garantiert nach dem Normalisieren immer ein
    `variants`-Dict + ein gueltiges `default_variant`, auch fuer LEGACY-
    setup.json (dort synthetisiert als Variante "default"). Dieser Helper ist
    die EINE Stelle, die das aufloest — nie wieder direkt `cfg["preset_id"]`,
    das wirft bei MODERN-Shape KeyError.
    """
    return cfg["variants"][cfg["default_variant"]]["preset_id"]


def _default_preset_name(cfg: dict) -> str:
    """Anzeige-Name der Default-Variante (für den Start-Hinweis)."""
    return cfg["variants"][cfg["default_variant"]].get("preset_name", _default_preset_id(cfg))


# Modul-weiter Meta-Cache, damit nicht jeder print() setup.json neu liest.
_META_CACHE: Optional[dict] = None


def meta() -> dict:
    """Projekt-Identität für die Launcher-Texte — generisch aus setup.json.

    Liest den optionalen `launcher`-Block aus setup.json und füllt fehlende
    Felder mit neutralen Defaults aus `project`. So ist der Launcher-Code in
    allen Bausätzen byte-identisch; nur setup.json unterscheidet sich.

    Felder (alle optional im `launcher`-Block):
      - name:       Anzeigename (Default: cfg["project"])
      - tagline:    Untertitel im Banner (Default: "OpenWebUI-Bausatz")
      - noun:       Wort fürs Produkt im Lauftext (Default: "Bausatz")
      - start_label: Label für Menü [3] (Default: "Starten")
      - start_hint: Hinweis nach dem Browser-Öffnen (Default: generisch)
      - farewell:   Abschiedszeile bei [X] (Default: "Bis bald.")
      - export_intro: Einleitungssatz für Export [2] (Default: generisch)
    """
    global _META_CACHE
    if _META_CACHE is not None:
        return _META_CACHE
    try:
        cfg = load_cfg()
    except Exception:
        cfg = {}
    project = cfg.get("project", "Bausatz")
    lb = (cfg.get("launcher") or {}) if isinstance(cfg.get("launcher"), dict) else {}
    name = lb.get("name", project)
    m = {
        "name": name,
        "tagline": lb.get("tagline", "OpenWebUI-Bausatz"),
        "noun": lb.get("noun", "Bausatz"),
        "start_label": lb.get("start_label", "Starten"),
        "start_hint": lb.get("start_hint", ""),
        "farewell": lb.get("farewell", "Bis bald."),
        "export_intro": lb.get(
            "export_intro",
            f"Ich packe den {name}-Inhalt (Masterprompt + Wissensmodule)",
        ),
        # Begriff fürs Lore-Setup-Erlebnis ([L]) — projektgerecht, da das
        # narrative Framing pro Bausatz unterschiedlich ist. Nur relevant,
        # wenn rite.py da ist.
        "lore_moment": lb.get("lore_moment", "Lore-Moment"),
        # Kurzes Framing-Label hinter dem [L]-Menüpunkt ("eingerahmt als …").
        "lore_label": lb.get("lore_label", "narrativ eingerahmt"),
    }
    _META_CACHE = m
    return m


def _detect_install_state() -> str:
    """Erkennt, ob der Bausatz in OpenWebUI bereits eingerichtet ist.

    Fünf Zustände — bewusst defensiv klassifiziert. Bei Unsicherheit ist
    "unreachable" der ehrlichste Default, damit Caller den User explizit
    fragen statt stumm zu reinstallieren.

    Returns:
        "fresh":          Nichts da. Klassisches Erstinstall ist richtig.
        "installed":      Preset + verlinkte KB existieren in OpenWebUI.
                          → Update-Pfad ist der semantisch richtige Default.
        "partial":        Halb-Zustand (Preset ohne KB-Link, Preset weg aber
                          andere Spuren da, ODER eine verwaiste gleichnamige
                          KB ohne Preset/Manifest -- WP-N2-1d: typischer
                          Abbruch zwischen KB- und Preset-Anlage in
                          `run_setup`). Klassik-Install räumt auf,
                          aber nur nach expliziter User-Bestätigung.
        "partial_no_key": Manifest vorhanden, aber kein API-Key in der Umgebung
                          (frische Shell, Repo-Klon ohne Setup-Lauf). Live-Check
                          unmöglich, run_setup wird sowieso gleich nach Key
                          fragen — daher KEIN extra Confirm-Prompt im Caller.
        "unreachable":    OpenWebUI antwortet nicht oder Setup-Konfig kaputt.
                          Caller MUSS warnen, bevor er Klassik-Install startet —
                          sonst löscht run_setup eine in 30 s erreichbare KB.

    Wichtig zur Manifest-Logik: Das `.openwebui-sync.json`-Manifest ist NUR
    ein Indiz für frühere Sync-Aktivität, kein Wahrheits-Anker. Live-Preset+KB
    ohne Manifest ist ein **funktionierender** Zustand (Hand-Setup, alte
    setup.py-Version, manueller Übertrag); `run_sync` schreibt das Manifest
    beim ersten Lauf neu. Daher: Preset+KB-Link → "installed", egal ob
    Manifest da ist. Manifest ohne Preset → "partial" (Sync-Spur stumm zurück-
    geblieben, OWUI wurde gewiped).
    """
    try:
        cfg = load_cfg()
        preset_id = _default_preset_id(cfg)
    except Exception:
        return "unreachable"

    # Manifest-Check: nur als Heuristik für verwaiste Sync-Spuren.
    manifest_path = REPO / ".openwebui-sync.json"
    has_manifest = False
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as fh:
                m = json.load(fh)
            kb_files = m.get("kb_files") or {}
            has_manifest = isinstance(kb_files, dict) and len(kb_files) > 0
        except (OSError, json.JSONDecodeError):
            has_manifest = False

    # Ohne API-Key kein Live-Check mehr möglich. Eigener Sub-State, damit der
    # Caller den Confirm-Prompt skippen kann — run_setup fragt sowieso gleich
    # nach dem Key, das doppelt-fragen ist nur Reibung. Manifest-leer + kein
    # Key bleibt dagegen "fresh" (nichts hier, ganz normaler Erstinstall).
    if not _ensure_owui_env():
        return "partial_no_key" if has_manifest else "fresh"

    url = _openwebui_url()
    try:
        client = setup_module.APIClient(url, os.environ["OPENWEBUI_API_KEY"])
        if not client.check_health():
            # OWUI nicht erreichbar — KRITISCHER Fall: wenn OWUI gerade hochboot,
            # antwortet /health 30 s lang nicht, hat aber Preset+KB im Speicher.
            # Wenn wir hier stumm "fresh" zurückgeben, läuft der User in
            # Klassik-Install und verliert seine Daten kurz nach OWUI-Boot.
            # Daher: "unreachable" → Caller fragt explizit.
            return "unreachable"
        preset = client.get_model(preset_id)
        # WP-N3-1c: `get_model` kollabiert JEDEN Nicht-200 auf `None` --
        # identisch zu einem bestätigten "Preset existiert nicht". Ein
        # echter HTTP-Fehler (401/500/0/unlesbar) ist aber KEIN bestätigtes
        # "fehlt", nur weil 404 das auch wäre. `last_model_status` ist
        # best-effort (Doubles ohne dieses Attribut -> Default 200, altes
        # Verhalten unverändert); nur ein ECHTER APIClient setzt es.
        model_status = getattr(client, "last_model_status", 200)
        if preset is None and model_status not in (200, 404):
            return "unreachable"

        # WP-N2-1d: verwaiste KB erkennen (ohne Preset/Manifest -- z.B. nach
        # einem Abbruch zwischen KB-Anlage und Preset-Anlage in `run_setup`,
        # das die KB vor dem Preset anlegt). Ohne diesen Check klassifiziert
        # die Funktion unten "fresh" -> `action_install` erreicht `run_setup`
        # ungefragt, das gleichnamige KBs vor der Neuanlage stillschweigend
        # LÖSCHT (s. `run_setup`s "destroy & recreate"-Block). Gleicher
        # Name-Match wie dort (exaktes `kb_name`), damit beide Stellen
        # dieselbe KB meinen.
        kb_name = cfg.get("kb_name", f"{cfg['project']} Wissensspeicher")
        kb_items = client.list_knowledge()
        # WP-N3-1c: dieselbe Status-Unterscheidung wie oben -- eine leere
        # Liste wegen HTTP-Fehler ist KEIN bestätigtes "keine KBs da".
        kb_status = getattr(client, "last_knowledge_status", 200)
        if not kb_items and kb_status != 200:
            return "unreachable"
        has_orphaned_kb = any(kb.get("name") == kb_name for kb in kb_items)
    except Exception:
        return "unreachable"

    has_preset = preset is not None

    # KB-Verknüpfung am Preset prüfen — Preset ohne KB ist ein halber Zustand.
    # Schema-Pfad live verifiziert (OpenWebUI 0.9.x): `preset.meta.knowledge`
    # ist eine Liste von {id, name}-Einträgen direkt am Top-Level-Preset.
    # Bei Schema-Wackler in 0.10+ hier validieren.
    has_kb_link = False
    if has_preset:
        try:
            meta = (preset or {}).get("meta") or {}
            kb_list = meta.get("knowledge") or []
            has_kb_link = isinstance(kb_list, list) and len(kb_list) > 0
        except Exception:
            has_kb_link = False

    # Live-Wahrheit: Preset + KB-Link reicht. Manifest ist NICHT Pflicht-Anker,
    # weil run_sync ihn beim ersten Lauf eines installierten Stacks neu erzeugt.
    if has_preset and has_kb_link:
        return "installed"
    if has_preset or has_manifest or has_orphaned_kb:
        return "partial"
    return "fresh"


def _confirm_reinstall_after_partial() -> bool:
    """Bestätigung für Erstinstall, wenn `_detect_install_state()` "partial" meldet.

    Standard-Antwort "j", weil die Klassik-Install den halben Zustand sauber
    überschreibt — aber wir machen die Frage trotzdem explizit, damit der User
    versteht, dass etwas neu aufgebaut wird statt nur ergänzt.
    """
    print()
    print(yellow(f"  {meta()['name']} sieht halb installiert aus (Preset oder KB-Link fehlt)."))
    print("  Eine Erstinstallation baut Preset + Knowledge Base sauber neu auf.")
    print(dim("  Bestehende Daten in OpenWebUI mit dieser Preset-ID werden ersetzt."))
    print()
    ans = _prompt("  Trotzdem fortfahren? (j/n) [j]: ").strip().lower()
    return ans in ("", "j", "y", "ja", "yes")


def _confirm_reinstall_unreachable() -> bool:
    """Bestätigung, wenn OpenWebUI nicht erreichbar ist ("unreachable"-State).

    Wichtig: hier ist der Default ABSICHTLICH "n". Wenn OWUI gerade hochboot,
    soll der User lieber 30 s warten und nochmal drücken, als blind die KB
    zu verlieren, weil run_setup gleich zuschlägt sobald OWUI antwortet.
    """
    print()
    print(yellow("  OpenWebUI antwortet gerade nicht."))
    print("  Wenn du OpenWebUI gerade gestartet hast, warte 30 Sekunden und drücke [1] erneut.")
    print(dim("  Falls OpenWebUI wirklich neu eingerichtet werden muss: trotzdem fortfahren."))
    print(dim("  Bestehende Daten (falls OWUI doch noch hochkommt) werden dann ersetzt."))
    print()
    ans = _prompt("  Trotzdem fortfahren? (j/n) [n]: ").strip().lower()
    return ans in ("j", "y", "ja", "yes")


def _finish_installed_connection(cfg: dict) -> None:
    """WP-N3-1a: der erhaltende Anschlussschritt für den `installed`-Zweig.

    Vorher endete `action_install` im `installed`-Zweig per `action_update()`
    (git-pull + `run_sync`, bearbeitet nur Preset/KB/Dateien) → `return` --
    der Anschlusshelfer `ensure_litellm_autowire` lag nur HINTER `run_setup`
    und wurde auf diesem Weg NIE erreicht. Diese Funktion ruft ihn jetzt
    direkt auf (idempotent, ändert KB/Preset nicht) — für ZIP UND Checkout
    gleich erreichbar, weil `setup_module`/`load_cfg` in beiden Auslieferungs-
    formen identisch funktionieren. Fehlender Master-Key: `ensure_litellm_
    autowire` selbst druckt dafür bereits den genau erforderlichen nächsten
    Schritt (Menü [1]/--install-litellm) statt dass wir hier etwas erfinden.
    """
    try:
        setup_module.ensure_litellm_autowire(REPO, cfg)
    except Exception as e:
        print(red(f"  Verkabelungs-Check fehlgeschlagen: {e.__class__.__name__}: {e}"))


def _resolve_orphaned_kb_for_partial(cfg: dict) -> Optional[dict]:
    """WP-N3-1b: bei state=='partial' gezielt prüfen, ob GENAU der
    WP-N2-1d-Orphaned-KB-Fall vorliegt (eindeutig namensgleiche KB, aber
    KEIN Preset) -- NUR dafür ist die erhaltende Ergänzung (statt Confirm→
    `run_setup`s destroy&recreate) ohne Mehrdeutigkeit sicher. Andere
    'partial'-Spielarten (Preset ohne KB-Link, nur Manifest-Spur) liefern
    None -- für sie bleibt der bisherige, ausdrücklich bestätigte Reinstall-
    Pfad die richtige, nicht-vorbelegte Wahl.

    Returns die KB (dict mit u.a. 'id'/'name') bei eindeutigem Treffer,
    sonst None (kein Key, unreachable, kein Preset-Check möglich, oder
    mehrdeutig/keine KB) -- niemals eine Mutation, reiner Read.
    """
    try:
        if not _ensure_owui_env():
            return None
        url = _openwebui_url()
        client = setup_module.APIClient(url, os.environ["OPENWEBUI_API_KEY"])
        if not client.check_health():
            return None
        preset_id = _default_preset_id(cfg)
        if client.get_model(preset_id) is not None:
            return None  # Preset existiert schon -- anderer 'partial'-Fall
        kb_name = cfg.get("kb_name", f"{cfg['project']} Wissensspeicher")
        matches = [kb for kb in client.list_knowledge() if kb.get("name") == kb_name]
        if len(matches) == 1:
            return matches[0]
        return None
    except Exception:
        return None


def _complete_orphaned_kb_partial(cfg: dict, kb: dict) -> None:
    """WP-N3-1b: erhaltende Fortführung für die eindeutig passende,
    namensgleiche KB ohne Preset -- ruft `setup_module.complete_orphaned_
    kb_install` (ERGÄNZT Preset-Link + Manifest, löscht/ersetzt nichts),
    danach denselben Connection-Schritt wie der `installed`-Pfad."""
    print()
    print(green(f"  ✓ Vorhandene Knowledge Base gefunden (ID: {kb.get('id')}, Name: {kb.get('name')})."))
    print("  Kein Preset dazu — ich ergänze den fehlenden Teil, OHNE die KB neu aufzubauen.")
    print(dim("  Für einen kompletten Neuaufbau: [7] Reset — eigene, ausdrückliche Wahl."))
    ok = setup_module.complete_orphaned_kb_install(REPO, cfg, kb["id"])
    if not ok:
        print(red("  Ergänzung nicht vollständig — Details oben. Bitte [6] Diagnose prüfen."))
        _pause()
        return
    _finish_installed_connection(cfg)
    _pause()


def _ensure_owui_env() -> bool:
    """Auto-lade ~/.openwebui_env in os.environ, wenn Keys fehlen.

    Returns True, wenn OPENWEBUI_API_KEY jetzt gesetzt ist (oder vorher schon war).
    Returns False, wenn auch nach Auto-Load nichts gefunden wurde.

    WP-N2-2c: vorher brach die Funktion sofort mit `return True` ab, sobald
    `OPENWEBUI_API_KEY` schon im Prozess-Env stand -- eine NUR in der Datei
    gespeicherte bewusste Wahl (z.B. `MMO_SIM_PERSONA_CLI`/`_API_*`) wurde
    dann NIE geladen. Jetzt wird die Datei immer gelesen und fehlende Werte
    nachgeladen; bereits gesetzte Prozesswerte werden (wie bisher) NIE
    überschrieben (`not os.environ.get(k)`-Guard unverändert)."""
    key_already_set = bool(os.environ.get("OPENWEBUI_API_KEY", "").strip())
    home_env = Path.home() / ".openwebui_env"
    if not home_env.exists():
        return key_already_set
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
        return key_already_set
    return bool(os.environ.get("OPENWEBUI_API_KEY", "").strip())


def action_install_lore() -> None:
    """Menüpunkt Lore-Setup: Prolog → klassisches Setup → Finale.

    Ruft exakt denselben ``action_install`` wie der Standard-Menüpunkt,
    nur eingerahmt in Kodex-Prolog (vorher) und Welcome-Box (hinterher).
    Wenn das Rite-Modul nicht importierbar ist (z.B. bei ZIP-Download ohne
    scripts/rite.py), informieren wir den Nutzer kurz und starten dann den
    klassischen Flow — damit er nicht rätselt, warum er plötzlich im
    Standard-Setup-Screen steht.

    Idempotenz-Check vorab (analog zu action_install): Wenn der Bausatz
    bereits installiert ist, leiten wir auf [4] Update um — ohne Lore-
    Rahmung, weil das Update kein Bergungs-Narrativ ist, sondern Routine.
    Lore-Setup ist explizit der Bergungs-Moment; das gibt es nur einmal.
    """
    if rite_module is None:
        print(yellow("\n  Lore-Modul nicht verfügbar — starte Standard-Komplett-Setup."))
        action_install()
        return

    state = _detect_install_state()
    if state == "installed":
        print(bold("\n  [L] Lore-Setup\n"))
        print(green(f"  ✓ {meta()['name']} ist bereits eingerichtet."))
        print()
        print(f"  Das Lore-Setup ist der {meta()['lore_moment']} — den gibt es nur einmal.")
        print("  Für aktuelle Repo-Files leite ich dich auf [4] Aktualisieren um.")
        print(dim("  Wenn du das Lore-Ritual neu erleben willst:"))
        print(dim("    → [7] Reset → [L] Lore-Setup"))
        print()
        ans = _prompt("  Update jetzt starten? (j/n) [j]: ").strip().lower()
        if ans in ("", "j", "y", "ja", "yes"):
            action_update()
        return
    if state == "partial":
        print(bold("\n  [L] Lore-Setup\n"))
        if not _confirm_reinstall_after_partial():
            print(dim("  Abbruch. Tipp: [6] Diagnose zeigt, was genau fehlt."))
            _pause()
            return
        # User hat bestätigt — Bergungs-Ritual läuft jetzt regulär.
    elif state == "partial_no_key":
        # Wie in action_install: Key-Frage kommt gleich, kein extra Prompt.
        # Hinweis bewusst minimal, damit das Lore-Ritual gleich danach atmet.
        print(bold("\n  [L] Lore-Setup\n"))
        print(dim("  Hinweis: Eine alte Sync-Spur liegt im Repo. "
                  "run_setup fragt gleich nach dem API-Key."))
    elif state == "unreachable":
        print(bold("\n  [L] Lore-Setup\n"))
        if not _confirm_reinstall_unreachable():
            _pause()
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
    # `_skip_state_check=True`, weil wir oben schon klassifiziert haben —
    # sonst doppelte API-Calls und doppelte User-Prompts.
    action_install(_skip_state_check=True)

    # Finale nur, wenn die Installation wirklich durchlief. Wir erkennen
    # das daran, dass Preset + OWUI-Key jetzt vorhanden sind.
    try:
        cfg = load_cfg()
        if not os.environ.get("OPENWEBUI_API_KEY"):
            return
        client = setup_module.APIClient(url, os.environ["OPENWEBUI_API_KEY"])
        preset = client.get_model(_default_preset_id(cfg))
        if preset is None:
            return
        rite_module.finale(url)
    except Exception:
        # Lore-Finale ist Kosmetik, niemals ein harter Fehler.
        return


def action_install(*, _skip_state_check: bool = False) -> None:
    print(bold("\n  [1] Komplett-Setup in OpenWebUI\n"))

    # Idempotenz-Check: Schon installiert → auf [4] Update umleiten.
    # `_skip_state_check=True` ist Keyword-only (siehe `*,` in der Signatur),
    # damit niemand das Argument versehentlich positional setzt. Genutzt von
    # action_install_lore() und action_diagnose()-Auto-Fix, die beide den
    # State vorher schon klassifiziert haben — sonst doppelte API-Calls und
    # doppelte User-Prompts.
    if not _skip_state_check:
        state = _detect_install_state()
        if state == "installed":
            print(green(f"  ✓ {meta()['name']} ist bereits eingerichtet."))
            print()
            print("  Für aktuelle Repo-Files leite ich dich auf [4] Aktualisieren um.")
            print(dim("  Wenn du wirklich alles neu willst (z.B. nach kaputtem Stand): [7] Reset."))
            print()
            ans = _prompt("  Update jetzt starten? (j/n) [j]: ").strip().lower()
            if ans in ("", "j", "y", "ja", "yes"):
                action_update()
            # WP-N3-1a: `action_update()` (git-pull + run_sync) ergänzt KEINEN
            # Backendanschluss -- ohne diesen Aufruf lief der installed-Zweig
            # bisher per `return` am Anschlusshelfer vorbei (nie erreicht,
            # weder bei bestätigtem noch bei abgelehntem Update-Angebot).
            _finish_installed_connection(load_cfg())
            _pause()
            return
        if state == "partial":
            orphaned_kb = _resolve_orphaned_kb_for_partial(load_cfg())
            if orphaned_kb is not None:
                _complete_orphaned_kb_partial(load_cfg(), orphaned_kb)
                return
            if not _confirm_reinstall_after_partial():
                print(dim("  Abbruch. Tipp: [6] Diagnose zeigt, was genau fehlt."))
                _pause()
                return
            # Ab hier: User hat Erstinstall trotz "partial" bestätigt —
            # run_setup räumt halbe Zustände sauber auf.
        elif state == "partial_no_key":
            # Manifest da, kein Key in der Umgebung. Kein Confirm-Prompt —
            # run_setup fragt gleich nach dem Key, der echte Bestimmungs-Moment
            # liegt dort. Eine Mini-Info reicht, damit der User weiß, dass es
            # nicht ganz "fresh" ist und etwas neu aufgebaut werden könnte.
            print(dim("  Hinweis: Eine alte Sync-Spur liegt im Repo. "
                      "run_setup fragt jetzt nach dem API-Key."))
        elif state == "unreachable":
            if not _confirm_reinstall_unreachable():
                _pause()
                return
            # Ab hier: User hat trotz fehlender OWUI-Antwort bestätigt.
            # action_install hat eigene OWUI-Reachability-Checks weiter unten,
            # die ihn dann nochmal sauber abfangen, falls OWUI immer noch down.

    print("  Was jetzt passiert:")
    print("   1. Voraussetzungen werden geprüft (Docker, Python, OpenWebUI).")
    print("   2. Einmal einrichten: Admin-Account im Browser (A/B) + OpenRouter-Key verdeckt im Terminal (C).")
    print(f"   3. Der {meta()['noun']}-Inhalt wird in OpenWebUI als Preset + Knowledge Base angelegt.")
    print("   4. LiteLLM-Cache-Container einrichten (spart ~90 % der Modellkosten).")
    print()
    print(dim("  Hinweis: Bei Schritt 2 kommt der OpenRouter-Key-Teil — plane gleich mit ein,"))
    print(dim("  unter https://openrouter.ai/settings/privacy den Provider 'Anthropic' zu erlauben."))
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
        print(f"  {meta()['name']} braucht einen laufenden OpenWebUI-Container.")
        ans = _prompt("  Soll ich OpenWebUI jetzt starten? (j/n) [j]: ").lower()
        if ans in ("j", "y", "ja", "yes", ""):
            _start_openwebui()
            # Nach dem Start muss OpenWebUI auch wirklich antworten — sonst rennt
            # der User in den A/B/C-Browser-Block und landet auf einer leeren
            # Seite. Einmal nachprüfen, bei NOT-OK sauber rausgehen.
            ok, info = _openwebui_ok()
            if not ok:
                print()
                print(red(f"  OpenWebUI ist nach dem Start noch nicht bereit: {info}"))
                print(yellow("  Bitte 20-30 Sekunden warten und Menü-Punkt [1] erneut starten."))
                _pause()
                return
        else:
            print(dim("  Abbruch. Erst OpenWebUI starten, dann nochmal Menü-Punkt [1]."))
            _pause()
            return

    if not _ensure_owui_env():
        url = _openwebui_url()
        print(yellow("\n  🌐 Jetzt bist du kurz im Browser dran — zwei Schritte (A→B):"))
        print()
        print(bold("  A) Admin-Account in OpenWebUI anlegen"))
        print(f"     OpenWebUI öffnet sich auf {url}")
        print("     Benutzername + Passwort setzen — bleibt rein lokal.")
        print()
        print(bold("  B) OpenWebUI-API-Key für mich erzeugen"))
        print("     (brauche ich gleich, um Preset + Knowledge Base anzulegen)")
        print("     Profil-Icon → Einstellungen → Account → API Keys")
        print("     → 'Create new key' → Key kopieren.")
        print()
        # Browser-Komfort: nur öffnen, wenn eine Anzeige verfügbar scheint.
        if _open_browser(url):
            print(dim("  (Den Browser habe ich dir schon geöffnet.)"))
        print()
        print(yellow("  ⏸️  Ich warte hier, während du A+B erledigst. Danach Key unten einfügen."))
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

    # Externer OpenRouter-Key EINMAL verdeckt erfassen (WP1a/PF1.1): vorher
    # musste er hier zusätzlich manuell als OWUI-Connection eingetragen
    # werden (früherer Browser-Schritt B, jetzt gestrichen) UND wurde
    # später in `run_install_litellm` per getpass ERNEUT abgefragt — keine
    # einmalige Erfassung. Die OWUI↔LiteLLM-Connection erledigt das
    # vorhandene Auto-Wire (`_ensure_owui_litellm_connection` in
    # run_install_litellm) automatisch, sobald der Key gesetzt ist; sobald
    # `OPENROUTER_API_KEY` hier in der Umgebung steht, entfällt der zweite
    # getpass-Prompt dort von selbst (er zieht den Wert zuerst aus
    # os.environ, s. run_install_litellm Schritt 2).
    or_ok, _ = _openrouter_key_status()
    if not or_ok:
        home_env_existing = _parse_env_file(Path.home() / ".openwebui_env")
        loaded_or = home_env_existing.get("OPENROUTER_API_KEY", "").strip()
        if loaded_or:
            os.environ["OPENROUTER_API_KEY"] = loaded_or
        else:
            print()
            print(bold("  C) OpenRouter-Key (einmal, verdeckt)"))
            print("     Von https://openrouter.ai/keys — 'sk-or-v1-...'.")
            print(yellow("     Unter https://openrouter.ai/settings/privacy den Provider"))
            print(yellow("     'Anthropic' erlauben — sonst cached LiteLLM später nicht."))
            from getpass import getpass
            or_key = getpass("  OpenRouter-API-Key (Eingabe ist unsichtbar): ").strip()
            if not or_key:
                print(red("  Kein OpenRouter-Key eingegeben, Abbruch."))
                _pause()
                return
            if not or_key.startswith("sk-or-"):
                print(red("  Das sieht nicht nach einem OpenRouter-Key aus. Erwartet: sk-or-..."))
                _pause()
                return
            os.environ["OPENROUTER_API_KEY"] = or_key

    # WP1b, Aufrufer 1: erfasste Keys feldweise erhaltend nach
    # ~/.openwebui_env persistieren (vorher: nur os.environ, PF1.2 — der
    # Folgestart fand die lokale Auth nicht wieder, weil action_rekeys der
    # einzige Schreibpfad war).
    home_env = Path.home() / ".openwebui_env"
    persist_updates = {
        "OPENWEBUI_URL": os.environ.get("OPENWEBUI_URL", _openwebui_url()),
        "OPENWEBUI_API_KEY": os.environ["OPENWEBUI_API_KEY"],
    }
    if os.environ.get("OPENROUTER_API_KEY", "").strip():
        persist_updates["OPENROUTER_API_KEY"] = os.environ["OPENROUTER_API_KEY"]
    if not home_env.is_file():
        home_env.write_text("# Vom Launcher geschrieben - automatisch gelesen.\n", encoding="utf-8")
    if not setup_module._update_env_file_preserving(home_env, persist_updates):
        print(yellow(f"  Warnung: Keys konnten nicht nach {home_env} persistiert werden — nur für diesen Lauf gesetzt."))

    # WP1d/PF1.6: Bestands-Re-Check NACH Auth, VOR dem mutierenden run_setup.
    # Die Klassifizierung ganz oben lief ohne Key (kein Live-Check möglich)
    # und kann daher "fresh"/"partial_no_key" geliefert haben, selbst wenn
    # in OpenWebUI längst Preset+KB existieren — run_setup würde die dann
    # BLIND LÖSCHEN (es räumt gleichnamige Presets/KBs vor dem Neuaufbau
    # auf, siehe run_setup). Mit dem jetzt gesetzten Key ist ein echter
    # Live-Check möglich; der hat Vorrang vor der alten Klassifizierung.
    recheck_state = _detect_install_state()
    if recheck_state == "installed":
        print()
        print(green(f"  ✓ {meta()['name']} ist in OpenWebUI bereits eingerichtet."))
        print(dim("  Das war beim ersten Check (ohne Key) noch nicht sichtbar."))
        print("  Für aktuelle Repo-Files leite ich dich auf [4] Aktualisieren um — kein destruktiver Neuaufbau.")
        print()
        ans = _prompt("  Update jetzt starten? (j/n) [j]: ").strip().lower()
        if ans in ("", "j", "y", "ja", "yes"):
            action_update()
        # WP-N3-1a: wie beim Eingangscheck -- `action_update()` ersetzt den
        # Anschluss nicht. Vorher endete dieser Zweig hier per `return`,
        # ohne `ensure_litellm_autowire` je zu erreichen (auch nicht nach
        # einem erfolgreichen `run_setup`-Lauf, weil der ja übersprungen
        # wurde). Läuft für ZIP und Checkout gleich, weil `setup_module`
        # in beiden Auslieferungsformen identisch ist.
        _finish_installed_connection(load_cfg())
        _pause()
        return
    if recheck_state == "partial":
        orphaned_kb = _resolve_orphaned_kb_for_partial(load_cfg())
        if orphaned_kb is not None:
            _complete_orphaned_kb_partial(load_cfg(), orphaned_kb)
            return
        if not _confirm_reinstall_after_partial():
            print(dim("  Abbruch. Tipp: [6] Diagnose zeigt, was genau fehlt."))
            _pause()
            return
    elif recheck_state == "unreachable":
        if not _confirm_reinstall_unreachable():
            _pause()
            return
    # "fresh" (oder ein residuales "partial_no_key") -> normaler Erstinstall
    # ist der korrekte, nicht-destruktive nächste Schritt.

    # run_setup kann per sys.exit(1) abbrechen (z.B. ungültiger API-Key); in
    # dem Fall wäre es falsch, danach noch den LiteLLM-Install-Prompt zu zeigen,
    # weil kein Preset zum Dranhängen existiert. Erfolg explizit tracken.
    setup_ok = False
    try:
        setup_module.run_setup(REPO, load_cfg())
        setup_ok = True
    except SystemExit as e:
        # Exit-Code 0 = Erfolg (kommt vor, wenn setup.py mit sys.exit(0) endet).
        code = e.code if isinstance(e.code, int) else 1
        if code == 0:
            setup_ok = True
        else:
            print(red(f"\n  Komplett-Setup abgebrochen (Exit {code}) — überspringe LiteLLM-Schritt."))
            print(dim("  Wenn der Fehler am API-Key lag: Menü [5] API-Keys ändern."))
    except Exception as e:
        print(red(f"\n  Erstinstallation fehlgeschlagen: {e.__class__.__name__}: {e}"))
        _pause()
        return

    if not setup_ok:
        _pause()
        return

    # LiteLLM-Anfrage nach Full-Setup. WP-N2-1a: ein laufender passender
    # Container ist nur ein Komponentenhinweis (Prozess existiert), kein
    # Beleg für eine funktionierende OWUI<->LiteLLM-Connection/Route -- der
    # Auto-Wire-/Connection-Check muss daher idempotent trotzdem laufen statt
    # den ganzen Schritt zu überspringen. `ensure_litellm_autowire` dupliziert
    # eine bereits korrekt verbundene Route NICHT (eigene Idempotenz-Checks).
    ok, info = _litellm_ok()
    if ok:
        print()
        print(green(f"  ✓ LiteLLM-Cache läuft bereits ({info}) — prüfe/bestätige die Verkabelung..."))
        try:
            setup_module.ensure_litellm_autowire(REPO, load_cfg())
        except Exception as e:
            print(red(f"  Verkabelungs-Check fehlgeschlagen: {e.__class__.__name__}: {e}"))
    else:
        print()
        print(bold("  LiteLLM-Cache aktivieren? (gehört zum Golden Setup, spart ~90 % Prompt-Kosten)"))
        print("  Das ist der Referenz-Stack, gegen den wir kalibrieren — Sonnet 4.6 + LiteLLM + OpenWebUI.")
        print(yellow("  Voraussetzung: bei OpenRouter unter 'settings/privacy' den Provider"))
        print(yellow("  'Anthropic' explizit erlauben — sonst cached LiteLLM nicht."))
        print(yellow("  Direktlink: https://openrouter.ai/settings/privacy"))
        ans = _prompt("  Aktivieren? (j/n, Default: j): ").lower()
        if ans in ("j", "y", "ja", "yes", ""):
            try:
                setup_module.run_install_litellm(REPO, load_cfg())
            except SystemExit:
                pass
            except Exception as e:
                print(red(f"\n  LiteLLM-Install fehlgeschlagen: {e.__class__.__name__}: {e}"))

    _pause()


def _git_cmd() -> list[str]:
    """Basis-Git-Kommando — standardmäßig `git`, optional ueberschreibbar.

    Der Enduser clont das Repo mit seinem eigenen Auth (HTTPS-Credential-
    Manager oder SSH); fuer ihn funktioniert plain `git pull` ohne Zutun.

    Wer einen eigenen Git-Wrapper braucht (z.B. ein Maintainer mit
    Custom-Credential-Helper / Multi-Account-Setup), setzt die Umgebungs-
    variable `LAUNCHER_GIT` auf den Wrapper-Namen oder -Pfad — dann laufen
    alle Pull-/Stash-Operationen darueber. Beispiel: `LAUNCHER_GIT=ghrepo`.
    Mehrteilige Kommandos werden per Whitespace gesplittet.
    """
    override = os.environ.get("LAUNCHER_GIT", "").strip()
    return override.split() if override else ["git"]


def _git(*args: str) -> subprocess.CompletedProcess:
    """Thin wrapper: <git-cmd> -C REPO <args>, erfasst stdout+stderr.

    Das Git-Kommando kommt aus `_git_cmd()` (Default `git`, per `LAUNCHER_GIT`
    ueberschreibbar). `-C REPO` wirkt auch auf Wrapper, die git-Argumente
    durchreichen.
    """
    return subprocess.run(
        [*_git_cmd(), "-C", str(REPO), *args],
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
        r = _git("stash", "push", "-m", "launcher.py auto-stash")
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
    print(bold(f"\n  [4] {meta()['name']} aktualisieren\n"))

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
        print(red("\n  OPENWEBUI_API_KEY fehlt — bitte erst Menüpunkt [1] (Komplett-Setup)"))
        print(red("  oder [5] (API-Keys ändern) ausführen, damit ~/.openwebui_env existiert."))
        _pause()
        return

    print()
    sync_ok = False
    try:
        setup_module.run_sync(REPO, load_cfg())
        sync_ok = True
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 1
        if code == 0:
            sync_ok = True
        else:
            print(red(f"\n  Sync abgebrochen (Exit {code})."))
            print(dim("  Tipp: Menü [6] Diagnose zeigt, was fehlt."))
    except Exception as e:
        print(red(f"\n  Update fehlgeschlagen: {e.__class__.__name__}: {e}"))

    if sync_ok:
        print()
        if project_hook is not None:
            print(green("  ✓ Update abgeschlossen — starte mit Menü [M] ZEITRISS spielen (Terminal)."))
        else:
            print(green(f"  ✓ Update abgeschlossen — starte mit Menü [3] {meta()['start_label']}."))

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
    print(bold("\n  [5] API-Keys ändern\n"))

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
        print(dim("  `-` eingeben = vorhandenen Wert löschen (bei optionalen Feldern)."))
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
    if existing_or:
        or_hint = f" (Enter = behalten: {_mask(existing_or)}, '-' = löschen)"
    else:
        or_hint = " (leer lassen, um zu überspringen)"
    or_input = getpass(f"  OpenRouter-API-Key (sk-or-...){or_hint}: ").strip()
    if or_input == "-":
        or_key = ""
        if existing_or:
            print(dim("  OpenRouter-Key wird gelöscht."))
    else:
        or_key = or_input or existing_or

    # WP1b, Aufrufer 2: derselbe feldweise-erhaltende Helfer wie
    # `action_install`/`run_install_litellm` statt des 4-Zeilen-Neubaus —
    # erhält andere Felder/Kommentare, die in dieser Datei stehen könnten.
    updates = {"OPENWEBUI_URL": url, "OPENWEBUI_API_KEY": owui_key}
    remove: set = set()
    if or_key:
        updates["OPENROUTER_API_KEY"] = or_key
    else:
        remove.add("OPENROUTER_API_KEY")
    if not home_env.is_file():
        home_env.write_text("# Vom Launcher geschrieben - automatisch gelesen.\n", encoding="utf-8")
    if not setup_module._update_env_file_preserving(home_env, updates, remove=remove):
        print(red(f"  Keys konnten nicht gespeichert werden ({home_env})."))
        _pause()
        return

    print(green(f"\n  ✓  Keys gespeichert in {home_env}"))
    os.environ["OPENWEBUI_URL"] = url
    os.environ["OPENWEBUI_API_KEY"] = owui_key
    if or_key:
        os.environ["OPENROUTER_API_KEY"] = or_key
    _pause()


# Sentinel-Werte für _extract_kb_id, damit der Caller zwischen „leer“
# (Preset ohne KB-Verknüpfung) und „Format unerwartet“ unterscheiden kann.
KB_ID_MISSING = "__kb_missing__"   # meta.knowledge fehlt oder ist []
KB_ID_WEIRD = "__kb_weird__"       # meta.knowledge hat exotischen Typ


def _extract_kb_id(preset: dict) -> Optional[str]:
    """Zieht die erste KB-ID aus dem Preset-Meta. Gibt zurück:
      - eine ID (str) bei erfolgreichem Lookup
      - ``KB_ID_MISSING`` wenn meta.knowledge fehlt oder leer ist
        (Preset existiert, aber hat keine KB verlinkt — typisch nach
        abgebrochenem Setup oder Reset-Zwischenstand)
      - ``KB_ID_WEIRD`` bei exotischem Typ in meta.knowledge[0]
    """
    meta = (preset.get("meta") or {}).get("knowledge")
    if not isinstance(meta, list) or not meta:
        return KB_ID_MISSING
    first = meta[0]
    if isinstance(first, dict):
        kb_id = first.get("id")
    elif isinstance(first, str):
        kb_id = first
    else:
        return KB_ID_WEIRD
    if isinstance(kb_id, str) and kb_id:
        return kb_id
    return KB_ID_WEIRD


def action_diagnose() -> None:
    print(bold("\n  [6] Bei mir läuft was nicht (Diagnose)\n"))
    print_status_block()
    print()
    print("  Prüfungen im Detail:")

    # Sammelt Findings als (label, kind)-Tupel. `kind` identifiziert die
    # Aktion, mit der sich der Befund automatisch beheben ließe — oder
    # "manual", wenn es keinen sinnvollen Auto-Fix gibt.
    # kinds:
    #   "rekeys"  → action_rekeys()  (User muss neuen Key ins Terminal pasten)
    #   "install" → action_install()
    #   "sync"    → action_update()  (enthält Sync)
    #   "manual"  → keine Auto-Aktion, Hinweis bleibt Text
    fixes: list[tuple[str, str]] = []

    # OpenWebUI-Smoke via API (nur wenn Env da)
    _ensure_owui_env()
    if not os.environ.get("OPENWEBUI_API_KEY"):
        print(yellow("   !  Kein OPENWEBUI_API_KEY — überspringe Preset- und KB-Check."))
        fixes.append(("Menü [5] API-Keys ändern — OpenWebUI-API-Key eintragen.", "rekeys"))
    else:
        try:
            client = setup_module.APIClient(
                _openwebui_url(), os.environ["OPENWEBUI_API_KEY"]
            )
            if not client.check_health():
                print(red("   ✗  OpenWebUI /health antwortet nicht."))
                fixes.append((
                    "OpenWebUI-Container prüfen (Docker läuft? Port 8080 frei?) und Menü [1] neu starten.",
                    "manual",
                ))
            else:
                print(green("   ✓  OpenWebUI /health OK"))

            if not client.check_auth():
                print(red("   ✗  API-Key ungültig oder ohne Rechte."))
                fixes.append((
                    "Menü [5] API-Keys ändern — neuen OpenWebUI-API-Key in OpenWebUI erzeugen und eintragen.",
                    "rekeys",
                ))
            else:
                print(green("   ✓  API-Key akzeptiert"))

            cfg = load_cfg()
            preset_id = _default_preset_id(cfg)
            preset = client.get_model(preset_id)
            if preset is None:
                print(red(f"   ✗  Preset '{preset_id}' existiert nicht (Install nötig?)"))
                fixes.append((
                    "Menü [1] Komplett-Setup — Preset + Knowledge Base neu anlegen.",
                    "install",
                ))
            else:
                print(green(f"   ✓  Preset '{preset.get('name', preset_id)}' gefunden"))
                kb_id = _extract_kb_id(preset)
                if kb_id == KB_ID_MISSING:
                    print(red("   ✗  Preset hat keine KB verlinkt (meta.knowledge leer)."))
                    fixes.append((
                        "Menü [4] Aktualisieren — verknüpft Preset und KB neu.",
                        "sync",
                    ))
                    kb_id = None
                elif kb_id == KB_ID_WEIRD:
                    print(yellow("   !  Preset gefunden, aber meta.knowledge hat unerwartetes Format."))
                    fixes.append((
                        "Menü [4] Aktualisieren — Preset/KB werden dabei neu verknüpft.",
                        "sync",
                    ))
                    kb_id = None
                if kb_id:
                    v_cfg = cfg.get("verify", {})
                    q = v_cfg.get("query", "")
                    if q:
                        result = client.query_kb(kb_id, q, k=v_cfg.get("top_k", 5))
                        hits = result.get("hits", 0)
                        if hits > 0:
                            print(green(f"   ✓  KB-Retrieval OK ({hits} Treffer)"))
                        else:
                            print(red("   ✗  KB-Retrieval lieferte 0 Treffer — KB ist leer oder nicht indexiert."))
                            fixes.append((
                                "Menü [4] Aktualisieren — triggert einen Sync, der die KB neu indexiert.",
                                "sync",
                            ))
        except Exception as e:
            print(red(f"   ✗  Diagnose-Fehler: {e.__class__.__name__}: {e}"))
            fixes.append((
                "OpenWebUI-Erreichbarkeit prüfen (Docker, Port 8080) und dann Menü [6] erneut.",
                "manual",
            ))

    # LiteLLM: Wenn Status-Block ihn als fehlend zeigt, ist das nicht zwingend
    # ein Fehler (manche User wollen ohne Cache spielen), aber es gehört zum
    # Golden Setup — deshalb als Empfehlung, nicht als Fehler.
    #
    # Schlauer Vorschlag: Wenn alle anderen Checks grün sind und nur der
    # LiteLLM-Cache fehlt, schicke den User direkt auf `--install-litellm`
    # (~1 Minute, lässt Preset/KB/Embeddings unangetastet) statt auf das
    # Komplett-Setup (könnte versehentlich Preset/KB neu bauen).
    #
    # Bewusst konservativ: **jedes** andere Finding (auch "manual"-only oder
    # "rekeys") blockt den Fast-Path. Begründung: wenn z.B. OWUI nicht
    # erreichbar ist, kann --install-litellm zwar Container starten, aber
    # weder Connection noch Preset-Rewire schreiben — der User läuft dann
    # in halben Erfolg statt aufgeräumtes Komplett-Setup. Lieber einmal mehr
    # den vollen Pfad als ein halb-verkabeltes System.
    litellm_active, _ = _litellm_ok()
    if not litellm_active and _cmd_available("docker"):
        print(yellow("   !  LiteLLM-Cache-Container läuft nicht — gehört zum Golden Setup (~90 % Ersparnis)."))
        if len(fixes) == 0:
            # Alle Kern-Checks (OWUI-Health, Auth, Preset, KB-Retrieval)
            # grün — minimaler Fix reicht.
            fixes.append((
                "LiteLLM-Cache nachinstallieren (`scripts/setup.py --install-litellm`) — "
                "Preset, KB und Embeddings bleiben unangetastet.",
                "litellm",
            ))
        else:
            fixes.append((
                "Menü [1] Komplett-Setup erneut durchlaufen — am Ende wird der LiteLLM-Cache angeboten.",
                "install",
            ))

    print()
    if not fixes:
        if project_hook is not None:
            print(green("  Alle Prüfungen grün. Mit Menü [M] ZEITRISS spielen (Terminal)."))
        else:
            print(green(f"  Alle Prüfungen grün. Mit Menü [3] {meta()['start_label']}."))
        _pause()
        return

    print(bold("  Empfohlene nächste Schritte:"))
    for i, (label, _kind) in enumerate(fixes, 1):
        print(f"   {i}. {label}")

    # Auto-Fix-Kaskade: wenn es mindestens einen Befund mit echtem Auto-Fix gibt,
    # biete an, die empfohlenen Schritte direkt auszuführen. "manual"-Befunde
    # werden dabei übersprungen (der User erledigt sie selbst, Text bleibt oben).
    autofixable = [f for f in fixes if f[1] != "manual"]
    if not autofixable:
        print()
        print(dim("  Keine automatische Reparatur möglich — bitte die Schritte manuell abarbeiten."))
        _pause()
        return

    print()
    ans = _prompt("  Soll ich die empfohlenen Schritte jetzt ausführen? (j/n) [j]: ").lower()
    if ans not in ("j", "y", "ja", "yes", ""):
        _pause()
        return

    # Ausführung in der gesammelten Reihenfolge. Doppelte kinds nur einmal laufen
    # lassen (mehrere Befunde zeigen oft auf dieselbe Aktion — Sync zweimal zu
    # triggern hilft niemandem).
    done: set[str] = set()
    for label, kind in autofixable:
        if kind in done:
            continue
        done.add(kind)
        print()
        print(bold(f"  ▶  {label}"))
        if kind == "rekeys":
            action_rekeys()
        elif kind == "install":
            # Diagnose hat den fehlenden Stand schon nachgewiesen — wir
            # überspringen den State-Check in action_install, sonst bekommt
            # der User nach dem Auto-Fix-"j" gleich den partial-Prompt nochmal.
            action_install(_skip_state_check=True)
        elif kind == "sync":
            action_update()
        elif kind == "litellm":
            # Minimaler Fix: nur den LiteLLM-Cache nachinstallieren.
            # Lässt Preset, KB und Embeddings völlig unangetastet (kein
            # Re-Embedding-Lauf, kein KB-Rebuild). Idempotent in setup.py.
            try:
                setup_module.run_install_litellm(REPO, load_cfg())
            except SystemExit:
                pass
            except Exception as e:
                print(red(f"\n  LiteLLM-Install fehlgeschlagen: {e.__class__.__name__}: {e}"))

    # Re-Diagnose: Lief der Fix durch? Wenn nicht, Eskalation auf [7] Reset anbieten.
    print()
    print(bold("  Nochmal prüfen:"))
    still_broken = _diagnose_has_errors()
    if not still_broken:
        if project_hook is not None:
            print(green("  ✓ Alles grün. Mit Menü [M] ZEITRISS spielen (Terminal)."))
        else:
            print(green(f"  ✓ Alles grün. Mit Menü [3] {meta()['start_label']}."))
    else:
        print(red("  ✗ Das reichte noch nicht."))
        print(yellow("  Empfehlung: Menü [7] Reset — komplett neu aufsetzen (löscht OpenWebUI-State)."))
    _pause()


def _diagnose_has_errors() -> bool:
    """Kompakter Re-Check nach Auto-Fix: True, wenn noch mindestens ein
    Kern-Check scheitert (OWUI erreichbar, Auth ok, Preset da, KB liefert Treffer).
    Gibt selbst keine Ausgabe — der Caller kommuniziert Ergebnis.
    """
    if not os.environ.get("OPENWEBUI_API_KEY"):
        return True
    try:
        client = setup_module.APIClient(_openwebui_url(), os.environ["OPENWEBUI_API_KEY"])
        if not client.check_health() or not client.check_auth():
            return True
        cfg = load_cfg()
        preset = client.get_model(_default_preset_id(cfg))
        if preset is None:
            return True
        kb_id = _extract_kb_id(preset)
        if not kb_id or kb_id in (KB_ID_MISSING, KB_ID_WEIRD):
            return True
        v_cfg = cfg.get("verify", {})
        q = v_cfg.get("query", "")
        if q:
            result = client.query_kb(kb_id, q, k=v_cfg.get("top_k", 5))
            if result.get("hits", 0) == 0:
                return True
    except Exception:
        return True
    return False


def _preview_reset_targets(client, project: str, preset_id: str) -> dict:
    """Listet alle Objekte, die ein Reset löschen würde — zur Vorschau
    im Launcher, *bevor* der User RESET tippt. Tolerant gegen API-Fehler:
    bei Ausfall gibt's leere Listen statt Crash, der Reset selbst macht
    dann seinen eigenen Match-Lauf.
    """
    result = {"presets": [], "kbs": [], "manifest": None, "error": None}
    try:
        all_models = client.list_models() if hasattr(client, "list_models") else []
        for m in all_models:
            if m.get("id") == preset_id:
                result["presets"].append(m.get("name") or preset_id)
                break
        for kb in client.list_knowledge():
            name = kb.get("name") or ""
            if name == project or name.startswith(project):
                result["kbs"].append(name)
    except Exception as e:
        result["error"] = f"{e.__class__.__name__}: {e}"
    return result


def action_reset() -> None:
    """Menüpunkt [7]: Kompletter Reset — OpenWebUI-State plattmachen und
    frisch neu aufsetzen. Optional inklusive LiteLLM-Container.

    Reihenfolge bewusst so: Erst Env prüfen (sonst können wir eh nichts
    inspizieren), dann Treffer-Vorschau live aus OWUI holen, dann
    LiteLLM-Wahl, dann RESET-Typo-Bestätigung. Damit tippt der User nie
    `RESET` und wird danach mit „Key fehlt“ abgewiesen oder bemerkt zu
    spät, dass eine nicht-projektzugehörige KB mit ähnlichem Namen
    mitgerissen wäre.
    """
    print(bold("\n  [7] Reset — Neuinstallation\n"))
    print(red("  ⚠️  Destruktive Aktion. Bitte genau lesen."))
    print()

    # Env zuerst prüfen — ohne API-Key kein Preview, kein Reset.
    if not _ensure_owui_env():
        print(red("  OPENWEBUI_API_KEY fehlt. Erst Menü [5] ausführen, dann [7] erneut."))
        _pause()
        return

    # Live-Vorschau gegen OWUI: was wird tatsächlich angefasst?
    cfg = load_cfg()
    project = cfg["project"]
    preset_id = _default_preset_id(cfg)
    url = _openwebui_url()
    manifest = REPO / ".openwebui-sync.json"
    targets = None
    try:
        client = setup_module.APIClient(url, os.environ["OPENWEBUI_API_KEY"])
        if client.check_health() and client.check_auth():
            targets = _preview_reset_targets(client, project, preset_id)
    except Exception as e:
        print(yellow(f"  Warnung: Vorschau konnte nicht geladen werden: {e.__class__.__name__}: {e}"))

    print(bold("  Konkret gelöscht wird auf deiner OpenWebUI-Instanz:"))
    if targets is None:
        print(yellow("   ⚠  Vorschau nicht verfügbar (OpenWebUI offline?). Reset läuft blind."))
    else:
        if targets["presets"]:
            for n in targets["presets"]:
                print(f"   • Preset: '{n}' (id: {preset_id})")
        else:
            print(dim(f"   • Preset '{preset_id}' ist nicht vorhanden — wird übersprungen."))
        if targets["kbs"]:
            print(f"   • Knowledge Base(s) mit Name == '{project}' oder Präfix '{project}':")
            for n in targets["kbs"]:
                print(f"       - '{n}'")
        else:
            print(dim(f"   • Keine KB matcht '{project}' — wird übersprungen."))
    if manifest.exists():
        print(f"   • Lokales Sync-Manifest: {manifest.name}")
    else:
        print(dim(f"   • Kein Sync-Manifest vorhanden — wird übersprungen."))
    print()
    print(bold("  Was behalten bleibt:"))
    print("   • Der OpenWebUI-Container + dein Admin-Account")
    print("   • Deine API-Keys (~/.openwebui_env)")
    print("   • Andere Presets/KBs in deiner OpenWebUI-Installation")
    print()

    # Warnung bei mehreren KB-Treffern — das ist die Backup-KB-Falle.
    if targets and len(targets["kbs"]) > 1:
        print(red("  ⚠  Mehrere KBs treffen das Namens-Präfix. Wenn eine davon deine"))
        print(red("      Backup-/Sandbox-KB ist: jetzt abbrechen und sie umbenennen."))
        print()

    ans = _prompt("  Auch LiteLLM-Container löschen und neu hochziehen? (j/n) [n]: ").lower()
    reset_litellm = ans in ("j", "y", "ja", "yes")
    if reset_litellm:
        print(yellow("   → LiteLLM wird gestoppt, Container + scripts/litellm/.env entfernt."))
    else:
        print(dim("   → LiteLLM bleibt unberührt."))
    print()

    # Typo-Schutz: Copy-Paste-tolerant (strip), aber Wording ohne „exakt“.
    confirm = _prompt("  Zur Bestätigung tippe RESET (Großbuchstaben): ").strip()
    if confirm != "RESET":
        print(dim("\n  Abgebrochen — nichts verändert."))
        _pause()
        return

    try:
        setup_module.run_reset(REPO, load_cfg(), opts={"reset_litellm": reset_litellm})
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 1
        if code != 0:
            print(red(f"\n  Reset abgebrochen (Exit {code}). Prüfe OpenWebUI-Status und versuche es erneut."))
            _pause()
            return
    except Exception as e:
        print(red(f"\n  Reset fehlgeschlagen: {e.__class__.__name__}: {e}"))
        _pause()
        return

    # Wenn LiteLLM gelöscht wurde, nach dem frischen Setup neu anbieten —
    # derselbe Flow wie am Ende von action_install.
    if reset_litellm:
        ok, _ = _litellm_ok()
        if not ok:
            print()
            print(bold("  LiteLLM-Cache wieder aktivieren? (gehört zum Golden Setup)"))
            print(yellow("  Voraussetzung: bei OpenRouter 'settings/privacy' → Anthropic erlauben."))
            ans = _prompt("  Aktivieren? (j/n) [j]: ").lower()
            if ans in ("j", "y", "ja", "yes", ""):
                try:
                    setup_module.run_install_litellm(REPO, load_cfg())
                except Exception as e:
                    print(red(f"  LiteLLM-Install fehlgeschlagen: {e.__class__.__name__}: {e}"))

    print()
    if project_hook is not None:
        print(green("  ✓ Reset abgeschlossen — mit Menü [M] ZEITRISS spielen (Terminal)."))
    else:
        print(green(f"  ✓ Reset abgeschlossen — mit Menü [3] {meta()['start_label']}."))
    _pause()


def action_play() -> None:
    url = _openwebui_url()
    print(bold(f"\n  [3] {meta()['start_label']}\n"))
    ok, info = _openwebui_ok()
    if not ok:
        print(yellow(f"  ⚠  OpenWebUI ist nicht erreichbar: {info}"))
        if _cmd_available("docker"):
            ans = _prompt("  Soll ich OpenWebUI jetzt starten? (j/n) [j]: ").lower()
            if ans in ("j", "y", "ja", "yes", ""):
                _start_openwebui()
                ok, info = _openwebui_ok()
                if not ok:
                    print()
                    print(red(f"  OpenWebUI ist nach dem Start noch nicht bereit: {info}"))
                    print(dim("  20-30 Sekunden warten, dann [3] erneut."))
                    _pause()
                    return
            else:
                print(dim("  Ok. Starte Docker und OpenWebUI, dann [3] erneut."))
                _pause()
                return
        else:
            print(red("  Docker fehlt — bitte installieren, OpenWebUI-Container starten, dann [3] erneut."))
            _pause()
            return
    print(f"  Öffne Browser auf {url} ...")
    if not _open_browser(url):
        print(yellow(f"  Konnte Browser nicht automatisch öffnen. Bitte manuell: {url}"))
    _m = meta()
    if _m["start_hint"]:
        for _line in _m["start_hint"].split("\n"):
            print(dim("  " + _line))
    else:
        print(dim(f"  In OpenWebUI: Neuer Chat → Modell '{_default_preset_name(load_cfg())}' wählen → los geht's."))
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
            # WP-N2-1b: dieser Container läuft ohne `--network=host` gebridgt
            # -- aus seiner Sicht ist `127.0.0.1` der Container selbst, nicht
            # der Host, auf dem LiteLLM loopback-only published wird. Der
            # TATSÄCHLICHE Anschluss an LiteLLM läuft über das GEMEINSAME
            # Docker-Netz + den Container-Namen (`setup.py:
            # _ensure_owui_on_litellm_network` / `_owui_litellm_target_host`),
            # NICHT über `host.docker.internal` (auf nativer Linux-Engine
            # erreicht die Bridge-Gateway-Adresse einen 127.0.0.1-publizierten
            # Port nicht). `--add-host` bleibt nur als harmloser Docker-Desktop-
            # Kompatibilitätshint (dort ist host.docker.internal ohnehin da);
            # auf Linux ist es ein No-Op, kein benötigter Pfad.
            "--add-host", "host.docker.internal:host-gateway",
            # ENABLE_API_KEYS=true: seit neueren OpenWebUI-Versionen (ab 0.11.x)
            # ist die API-Key-Erstellung per Default deaktiviert. Ohne dieses
            # Flag kann der User keinen OpenWebUI-API-Key erzeugen, den der
            # Launcher aber zwingend braucht, um Preset + Knowledge Base
            # anzulegen. Muss beim FIRST-Boot gesetzt sein (PersistentConfig
            # auth.enable_api_keys wird danach in der DB eingefroren).
            "-e", "ENABLE_API_KEYS=true",
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
    print(bold("\n  [2] Inhalt woanders nutzen (Export-Paket erzeugen)\n"))
    print("  " + meta()["export_intro"])
    print("  in einen Ordner, den du manuell in deine Zielplattform hochladen")
    print("  kannst.")
    print()
    print(yellow("  ⚠️  Das ist ein Best-Effort-Weg. Kalibriert wird nur gegen"))
    print(yellow("     OpenWebUI. Andere Plattformen: Regel-Glitches sind möglich."))
    print()
    print(bold("  Welches Format?"))
    print("   [1]  Strukturiert (Ordner mit Unterordnern core/, systems/, ...)")
    print(dim("        → für Plattformen mit Datei-Upload, die Ordner behalten"))
    print("   [2]  Flach (alle Dateien nummeriert in einem Ordner)")
    print(dim("        → für Plattformen ohne Ordner-Support"))
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

    results = []
    try:
        for flat in modes:
            results.append(setup_module.run_export(REPO, cfg, flat=flat, out_dir=out_dir))
    except SystemExit as exc:
        print(red(f"\n  Export abgebrochen (Exitcode {exc.code})."))
        if results:
            print(yellow("  Bereits erfolgreich erzeugt; fehlgeschlagene Variante fehlt:"))
            for result in results:
                print(yellow(f"   • {result.name} ({result.with_suffix('.zip').name})"))
        _pause()
        return
    except Exception as e:
        print(red(f"\n  Export fehlgeschlagen: {e.__class__.__name__}: {e}"))
        _pause()
        return

    print("\n  Erfolgreich erzeugt:")
    for result in results:
        print(green(f"   ✓ {result.name}"))
        print(green(f"     {result.with_suffix('.zip').name}"))
    print()
    print(bold("  Hinweise für den Import in deine Zielplattform:"))
    print("   • Direkter Weg: system/SYSTEM_PROMPT_ONLY.md vollständig als")
    print("     Projekt-Anweisung; dann nicht zusätzlich als Wissensdokument.")
    print("   • Bootstrap-Weg: system/PROJECT_BOOTSTRAP_INSTRUCTIONS.md als")
    print("     Anweisung und SYSTEM_PROMPT_ONLY.md zusätzlich als Projektquelle.")
    print("   • Die Wissensmodule gehen als 'Wissen' / 'Projekt-Dateien' /")
    print("     'Knowledge' rein — je nachdem wie die Plattform das nennt.")
    print("   • Ohne retrieval-fähige Plattform wird's unzuverlässig.")
    print(dim("   • Plattform-spezifische Tipps: docs/setup-guide.md#portabler-export-ohne-gewähr"))
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
    # Einmalig beim Start ~/.openwebui_env laden, damit Status-Block korrekte
    # Werte zeigt (sonst zeigt er bei frischer Shell [--] obwohl die Keys da sind).
    _ensure_owui_env()
    m = meta()
    has_lore = rite_module is not None
    has_mmo_sim = project_hook is not None
    while True:
        banner()
        print_status_block()
        print()
        print(bold("  Was möchtest du tun?"))
        print()
        print(dim("  ── Einrichtung (wähle einen Weg) ──────────────")) 
        print("   [1]  ZEITRISS einrichten (empfohlen, Golden Setup)")
        if has_lore:
            print(f"   [L]  Einrichten mit Einstimmung (optional) — wie [1], {m['lore_label']}")
        print("   [2]  Masterprompt und Wissensdateien exportieren (ohne Gewähr)")
        print()
        print(dim("  ── Im Betrieb ───────────────────────────────"))
        if has_mmo_sim:
            print("   [M]  ZEITRISS spielen (Terminal)")
        print(f"   [3]  {m['start_label']} (Browser öffnen)")
        print("   [4]  Aktualisieren (git pull + Sync)")
        print("   [5]  API-Keys ändern")
        print("   [6]  Bei mir läuft was nicht (Diagnose)")
        print("   [7]  Reset — Neuinstallation (⚠ destruktiv)")
        print()
        print("   [X]  Beenden")
        print()
        choice = _prompt("  Auswahl: ").strip().lower()

        if choice == "1":
            action_install()
        elif choice == "l" and has_lore:
            action_install_lore()
        elif choice == "2":
            action_export()
        elif choice == "3":
            action_play()
        elif choice == "m" and has_mmo_sim:
            project_hook.launch()
        elif choice == "4":
            action_update()
        elif choice == "5":
            action_rekeys()
        elif choice == "6":
            action_diagnose()
        elif choice == "7":
            action_reset()
        elif choice in ("x", "q", "quit", "exit"):
            print(dim(f"\n  {meta()['farewell']}\n"))
            return 0
        elif choice == "":
            # Nur Enter gedrückt: Menü neu rendern, nicht beenden.
            continue
        else:
            print(yellow(f"  Unbekannte Auswahl: {choice!r}"))
            _pause()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(dim("\n  Abgebrochen."))
        sys.exit(130)
