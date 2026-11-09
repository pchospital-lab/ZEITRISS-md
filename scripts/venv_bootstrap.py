#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/venv_bootstrap.py — private Projektumgebung fuer den normalen
Mint-Spielstart (F1-1, 03_F1_AUFTRAG.md §F1-1).

Vorher hatte der Starter (`zeitriss.sh` -> `scripts/zeitriss.py`) KEINE
venv-Logik: er lief mit dem erstbesten `python3` von PATH. `mmo_sim/domain/
zeitriss/save_validation.py` importiert aber `jsonschema`/`referencing`
direkt (`requirements-ci.txt`) -- auf einem frisch entpackten Download ohne
vorinstallierte Pakete scheitert `[M] ZEITRISS spielen` dann mit einem
rohen `ModuleNotFoundError`, sichtbar erst beim Betreten des Terminalspiels,
nicht vorher. Ein normaler Nutzer soll dafuer weder `git clone` noch ein
manuell aktiviertes Entwickler-`venv` (bisher nur in docs/spielerstart.md
als Referenzweg dokumentiert) brauchen.

Dieses Modul stellt sicher, dass der laufende Prozess in einer PRIVATEN,
wiederverwendbaren Projekt-venv unterhalb des entpackten Repo-Roots laeuft
(`<repo_root>/.venv`), bevor projektinterne Importe mit Fremdabhaengigkeiten
stattfinden. Es wird ganz am Anfang von `scripts/zeitriss.py` (Haupteinstieg
ueber den Starter) UND `scripts/mmo_sim.py` (Direktaufruf, falls jemand ihn
ohne den Starter startet) aufgerufen -- beide Einstiege landen damit in
DERSELBEN venv, kein zweiter Bootstrap-Mechanismus.

Keine globale `pip install`, kein `--user`, kein Spielbetrieb als root
(F1-1-Vorgabe). Ein bereits vollstaendig eingerichteter Lauf installiert bei
spaeteren Starts nichts erneut (Hash-Sentinel gegen `requirements-ci.txt`).
Fehler bleiben als normale, lesbare Textzeilen im Terminal sichtbar -- kein
stiller Fallback auf den Systeminterpreter."""
from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

_SENTINEL_NAME = ".ready"
_REQUIRED_RUNTIME_DEPS = ("jsonschema", "referencing")


def venv_dir(repo_root: Path) -> Path:
    return repo_root / ".venv"


def _venv_python(venv_dir_: Path) -> Path:
    if sys.platform == "win32":
        return venv_dir_ / "Scripts" / "python.exe"
    return venv_dir_ / "bin" / "python3"


def _requirements_file(repo_root: Path) -> Path:
    return repo_root / "requirements-ci.txt"


def _requirements_hash(repo_root: Path) -> str:
    req = _requirements_file(repo_root)
    data = req.read_bytes() if req.is_file() else b""
    return hashlib.sha256(data).hexdigest()


def already_in_venv(venv_dir_: Path) -> bool:
    """True, wenn der AKTUELL laufende Interpreter bereits `venv_dir_` als
    `sys.prefix` hat (also: wir muessen nicht neu starten)."""
    try:
        return Path(sys.prefix).resolve() == venv_dir_.resolve()
    except OSError:
        return False


def _is_root() -> bool:
    return sys.platform != "win32" and hasattr(os, "geteuid") and os.geteuid() == 0


def _required_deps_available() -> bool:
    """True, wenn alle von `save_validation.py` benoetigten Laufzeit-Pakete
    im AKTUELLEN Interpreter bereits importierbar sind. Prueft nur per
    `importlib.util.find_spec` (kein echter Import -- kein Seiteneffekt).
    Damit kann eine bereits gueltige Umgebung wiederverwendet werden (z. B.
    CI, die `requirements-ci.txt` vor `run_all.py` per `pip install --user`
    bereitstellt, oder ein vom Nutzer selbst aktiviertes Dev-venv), statt
    zusaetzlich eine private `.venv` anzulegen -- F1-1 erlaubt ausdruecklich
    das Wiederverwenden einer vorhandenen gueltigen Umgebung."""
    return all(
        importlib.util.find_spec(dep) is not None for dep in _REQUIRED_RUNTIME_DEPS
    )


def ensure_running_in_project_venv(repo_root: Path, *, stream=None) -> None:
    """Idempotent: no-op, wenn der Prozess schon in `<repo_root>/.venv`
    laeuft, wenn `ZEITRISS_SKIP_VENV_BOOTSTRAP` gesetzt ist, oder wenn die
    benoetigten Laufzeit-Abhaengigkeiten im aktuellen Interpreter bereits
    importierbar sind (Wiederverwendung einer vorhandenen gueltigen
    Umgebung -- vermeidet den Seiteneffekt einer neuen `.venv` bzw. einen
    `os.execv`-Wechsel in Kind-/Tooling-/Test-/CI-Prozessen, die ihre Deps
    schon mitbringen). Sonst: venv anlegen/wiederverwenden, Pins aus
    `requirements-ci.txt` nur bei Drift (neu/geaendert) installieren, dann
    per `os.execv` in denselben Aufruf unter dem venv-Interpreter wechseln.

    Nie ein stiller Fallback: jeder Fehlerpfad druckt eine lesbare
    Begruendung und beendet den Prozess mit Exit-Code 1 -- das Terminal
    bleibt offen, der Fehler bleibt sichtbar (F1-1-Vorgabe)."""
    out = stream or sys.stdout

    if os.environ.get("ZEITRISS_SKIP_VENV_BOOTSTRAP"):
        return

    venv_dir_ = venv_dir(repo_root)
    if already_in_venv(venv_dir_):
        return

    if _required_deps_available():
        return

    if _is_root():
        print(
            "\n  ZEITRISS soll nicht als root laufen -- es braucht keine "
            "Systeminstallation.\n  Starte das Spiel als normaler Benutzer, "
            "z. B. mit ./zeitriss.sh\n",
            file=out,
        )
        sys.exit(1)

    venv_python = _venv_python(venv_dir_)
    marker = venv_dir_ / _SENTINEL_NAME
    req_hash = _requirements_hash(repo_root)

    needs_create = not venv_python.exists()
    if needs_create:
        print("  Richte private ZEITRISS-Projektumgebung ein (einmalig) …", file=out)
        try:
            subprocess.run(
                [sys.executable, "-m", "venv", str(venv_dir_)],
                check=True, capture_output=True, text=True,
            )
        except FileNotFoundError:
            print(
                "\n  FEHLER: Das Python-Modul 'venv' ist nicht verfuegbar.\n"
                "  Linux Mint: sudo apt install python3-venv\n",
                file=out,
            )
            sys.exit(1)
        except subprocess.CalledProcessError as exc:
            print(
                f"\n  FEHLER: Private Projektumgebung konnte nicht erstellt "
                f"werden.\n  {exc.stderr or exc}\n",
                file=out,
            )
            sys.exit(1)

    needs_install = (
        needs_create
        or not marker.is_file()
        or marker.read_text(encoding="utf-8").strip() != req_hash
    )
    if needs_install:
        req_file = _requirements_file(repo_root)
        if req_file.is_file():
            print(
                "  Installiere benötigte Bibliotheken in die private "
                "Projektumgebung …",
                file=out,
            )
            try:
                subprocess.run(
                    [
                        str(venv_python), "-m", "pip", "install", "--quiet",
                        "-r", str(req_file),
                    ],
                    check=True, capture_output=True, text=True,
                )
            except subprocess.CalledProcessError as exc:
                print(
                    f"\n  FEHLER: Abhängigkeiten konnten nicht installiert "
                    f"werden.\n  {exc.stderr or exc}\n"
                    "  Prüfe Internetzugang/Berechtigungen und starte "
                    "erneut.\n",
                    file=out,
                )
                sys.exit(1)
        marker.write_text(req_hash, encoding="utf-8")

    # `os.execv` ersetzt den Prozess sofort und löst dabei KEINEN normalen
    # Interpreter-Shutdown aus -- ohne expliziten Flush gehen alle bisher
    # nur in den stdio-Puffer geschriebenen `print(...)`-Meldungen dieser
    # Funktion verloren, sobald stdout nicht an ein TTY, sondern an eine
    # Pipe/Datei hängt (dort ist Python block- statt linegepuffert). Beobachtet
    # beim Delta-Test: ohne diesen Flush fehlten die Bootstrap-Zeilen komplett
    # im umgeleiteten Log.
    try:
        out.flush()
    except (OSError, ValueError):
        pass
    try:
        os.execv(str(venv_python), [str(venv_python), *sys.argv])
    except OSError as exc:
        print(
            f"\n  FEHLER: Konnte nicht in die private Projektumgebung "
            f"wechseln ({exc}).\n",
            file=out,
        )
        sys.exit(1)
