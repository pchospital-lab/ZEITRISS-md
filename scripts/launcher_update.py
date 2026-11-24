#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/launcher_update.py — Update-Mechanik für `scripts/launcher.py`
Menüpunkt [4] "Nach Updates suchen" (ZR-ALTAIR-UPDATER-SPIELTEST-20261118-r2,
U1-U6 aus 02_UPDATE_VERHALTEN_UND_ABNAHME.md).

Dieses Modul enthält die testbare Mechanik (Git-/HTTP-/ZIP-IO, Sicherheits-
prüfungen, Statusdatei) getrennt vom dünnen, interaktiven Caller in
`launcher.py` — Tests treiben die Funktionen hier direkt gegen kontrollierte
Git-/HTTP-/Archiv-Fixtures, ohne echtes Netz oder ein echtes Backend.

Kernentscheidungen:

- **U1 Check:** `check_for_update()` liest NUR (git ls-remote / GitHub-API-
  GET), tauscht nie Dateien aus und synct nie. Eine nicht erreichbare Quelle
  oder eine unbestimmte ZIP-Herkunft liefert `status == "unknown"`, nie
  `"current"`.
- **U2/U3 Install:** `perform_git_update()` pinnt genau die beim Check
  gelesene Zielrevision (Fast-forward-only, kein Force/Reset). Für ZIP-
  Installationen übernimmt `adopt_staged_update()` nach `validate_and_
  stage_zip()` nur eindeutig produktzugehörige Dateien; ein `managed_files`-
  Hash-Manifest in der Statusdatei erkennt lokale Abweichungen seit dem
  letzten verwalteten Lauf (auch bei der ERSTEN Übernahme einer bisher
  unverwalteten ZIP-Installation, die dabei in den verwalteten Stand
  überführt wird, statt die aktuelle Fernrevision blind als "schon
  installiert" zu verbuchen).
- **U4 Schutz:** `PROTECTED_RELPATHS` schließt Nutzdaten/Config/Secrets aus
  jeder Übernahme aus; `validate_and_stage_zip()` lehnt Symlinks, Sonder-
  dateien, Pfad-Traversal/absolute Pfade und übergroße Archive VOR jeder
  Dateisystemänderung ab.
- **U5 Sync getrennt vom Dateistand:** `run_sync_subprocess()` ruft
  `scripts/setup.py --sync` als NEUEN Python-Prozess auf (nie die bereits
  im laufenden Launcher importierten alten `setup`-Modulbytes) und
  schreibt das Sync-Ergebnis separat von `installed_rev` in die
  Statusdatei — "Dateien neu, Sync offen" bleibt dadurch sichtbar und wird
  von einem erneuten Check nicht als "Aktuell" verdeckt.
- **U6 Neustart:** `restart_launcher()` ersetzt den Prozess per `os.execv`
  mit dem echten Starter-Einstieg (`scripts/zeitriss.py`) — kein Weiter-
  spielen mit bereits importierten alten Modulen.

Kein Modell-/GM-Aufruf, keine neuen Zugangsdaten, kein Zwangsupdate."""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import queue
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

# ── Konstanten ─────────────────────────────────────────────────────────

STATE_FILENAME = ".zeitriss-update-state.json"
LOCK_FILENAME = ".zeitriss-update.lock"

# Die offizielle Quelle (s. KICKOFF.md Baseline) — nur als Fallback für
# Installationen OHNE eigenen Git-Remote (ZIP-Download). Ein Git-Checkout
# fragt immer seinen TATSÄCHLICH konfigurierten `origin`, nicht diese
# Konstante.
OFFICIAL_REPO_OWNER = "pchospital-lab"
OFFICIAL_REPO_NAME = "ZEITRISS-md"
OFFICIAL_BRANCH = "main"

GITHUB_API_COMMIT_URL = "https://api.github.com/repos/{owner}/{repo}/commits/{branch}"

# Wartungs-/Test-Override für die ZIP-Bezugsquelle — analog zur
# bestehenden LAUNCHER_GIT-Konvention in launcher.py: ändert NUR die
# Bezugs-URL, nie den danach laufenden Sicherheitsweg (jedes Archiv
# durchläuft weiterhin ungekürzt `validate_and_stage_zip`). Ein normaler
# Spielerlauf setzt diese Variable nie.
#
# R3-04/e: der Kommentar allein war keine Durchsetzung -- war
# ARCHIVE_URL_ENV_OVERRIDE gesetzt, griff er in JEDER Umgebung, auch bei
# einem normalen Spieler. Jetzt braucht es ZUSÄTZLICH den expliziten
# Dev-/Test-Freigabeschalter unten; ohne ihn ist der Override inert (die
# offizielle GitHub-URL wird verwendet), egal was in der Override-Variable
# selbst steht.
ARCHIVE_URL_ENV_OVERRIDE = "LAUNCHER_UPDATE_ARCHIVE_URL"
ARCHIVE_URL_OVERRIDE_ENABLE_FLAG = "LAUNCHER_UPDATE_ALLOW_ARCHIVE_OVERRIDE"
_ALLOWED_ARCHIVE_SCHEMES = ("http", "https", "file")

# R7-03 (ZR-ALTAIR-UPDATER-SPIELTEST-NACHZUG-20261119-R7 §04): ein r6-Test
# tauschte NUR die Archivbytes (`ARCHIVE_URL_ENV_OVERRIDE`) -- `check_for_
# update` las weiter die OFFIZIELLE Quelle, der dort gelesene `remote_rev`
# (offizielles `main`) wanderte unveraendert als `target_rev` bis zu
# `mark_files_updated`/`adopt_staged_update`: der persistierte `installed_
# rev` nannte danach eine ANDERE Revision als die tatsaechlich installierten
# Kandidatenbytes. `CANDIDATE_REV_ENV_OVERRIDE` pinnt deshalb die von `check_
# for_update` gemeldete Zielrevision an DENSELBEN expliziten Kandidaten --
# bewusst HINTER demselben bereits bestehenden Freigabeschalter (`ARCHIVE_
# URL_OVERRIDE_ENABLE_FLAG`), NICHT einem eigenen: ein kontrollierter Vor-
# Merge-Test setzt beide Override-Variablen gemeinsam und bindet sie damit
# IMMER an denselben gepinnten Endkandidaten, nie unabhaengig voneinander.
# Ein normaler Spielerlauf setzt diese Variable nie; ohne den Freigabe-
# schalter bleibt sie inert -- der offizielle Default-Check liest dann
# weiterhin ausschliesslich die offizielle Quelle (read-only, unveraendert).
CANDIDATE_REV_ENV_OVERRIDE = "LAUNCHER_UPDATE_CANDIDATE_REV"

# Nie durch eine Dateiübernahme berührt — Nutzdaten, Secrets, private
# Laufzeitumgebung, Sync-Zuordnung. Pfade relativ zum Repo-Root.
PROTECTED_RELPATHS: tuple[str, ...] = (
    "internal/mmo_sim_data",
    ".openwebui-sync.json",
    ".venv",
    ".exports",
    ".dev",
    "scripts/litellm/.env",
    STATE_FILENAME,
    STATE_FILENAME + ".tmp",
    LOCK_FILENAME,
)

MAX_ZIP_ENTRIES = 20_000
MAX_ZIP_ENTRY_BYTES = 50 * 1024 * 1024
MAX_ZIP_TOTAL_BYTES = 500 * 1024 * 1024
MAX_DOWNLOAD_BYTES = 300 * 1024 * 1024


# ── Statusdatei ──────────────────────────────────────────────────────────

def state_path(repo: Path) -> Path:
    return repo / STATE_FILENAME


def read_state(repo: Path) -> dict:
    p = state_path(repo)
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text("utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def write_state(repo: Path, **fields) -> dict:
    """Merged-Update der Statusdatei (liest, aktualisiert, schreibt atomar
    via tmp+rename). Unbekannte/alte Felder bleiben erhalten."""
    state = read_state(repo)
    state.update(fields)
    tmp = state_path(repo).with_name(state_path(repo).name + ".tmp")
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False, sort_keys=True) + "\n", "utf-8")
    tmp.replace(state_path(repo))
    return state


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# R3-03: Exklusivsperre gegen GLEICHZEITIGE Updateversuche -- kein neuer
# Dienst/Daemon, nur eine PID-Lockdatei neben der Statusdatei. Eine
# Lockdatei eines bereits beendeten Prozesses (z. B. nach einem Absturz)
# gilt als verwaist und wird übernommen, statt den Nutzer dauerhaft
# auszuschließen.
def _lock_path(repo: Path) -> Path:
    return repo / LOCK_FILENAME


def _lock_registry_key(lp: Path) -> str:
    """Stabiler Schluessel fuer die prozesslokale Registry gehaltener
    Lock-fds (`_HELD_LOCK_FDS`). Aufgeloester absoluter Pfad, damit
    `acquire`/`release` dieselbe Sperre ueber identische Repos erkennen."""
    try:
        return str(lp.resolve(strict=False))
    except OSError:
        return str(lp)


def _fd_still_matches_path(fd: int, lp: Path) -> bool:
    """`True`, wenn die offene `fd` und der AKTUELLE Verzeichniseintrag `lp`
    dieselbe Datei sind (`st_dev`/`st_ino`). Schuetzt gegen einen Geist-fd:
    ein gleichzeitiger Prozess kann `lp` zwischen `os.open` und dem eigenen
    `flock`-Erwerb unlinkt/ersetzt haben -- dann haelt die eigene fd nur
    noch eine verwaiste Inode, die nicht mehr dem Pfad entspricht, und ein
    DRITTER Prozess koennte den (wieder freien) Pfad erneut frisch erwerben
    (zwei gleichzeitige Owner). Muster uebernommen aus der bereits
    virtiofs-geprueften `mmo_sim/lab/runner.py:_fd_still_matches_path`."""
    try:
        fd_st = os.fstat(fd)
        path_st = os.stat(lp)
    except OSError:
        return False
    return fd_st.st_dev == path_st.st_dev and fd_st.st_ino == path_st.st_ino


def _peek_lock_pid(fd: int) -> Optional[int]:
    """Liest den rein INFORMATIVEN PID-Eintrag aus der Lockdatei (erste
    Whitespace-getrennte Zahl). `None`, wenn leer/unlesbar/unparsebar --
    der Aufrufer behandelt das NICHT als 'frei', sondern als unklare
    Sperre (G3a-Muster). Die massgebliche Autoritaet ist der `flock`, nie
    dieser Wert (eine PID kann durch Wiederverwendung taeuschen)."""
    try:
        raw = os.pread(fd, 4096, 0)
        return int(raw.decode("utf-8").strip().split()[0])
    except (OSError, ValueError, IndexError, UnicodeDecodeError):
        return None


# R6-02 (ZR-ALTAIR-UPDATER-SPIELTEST-NACHZUG-20261119-r6, 01_GENERAL_
# REVIEW.md R6-02): die MASSGEBLICHE Mutual-Exclusion gegen gleichzeitige
# Updateversuche ist jetzt ein kernelverwalteter `fcntl.flock(LOCK_EX|
# LOCK_NB)` auf einer stabilen, fuer die gesamte Besitzdauer OFFEN
# gehaltenen Lock-fd -- NICHT mehr die fruehere Folge "PID lesen + Pfad
# per `unlink()` loeschen". Jene Folge hatte ein echtes TOCTOU-Fenster
# INNERHALB des Verwaist-Helfers ZWISCHEN seinem letzten `read_text`
# (PID == erwarteter toter Besitzer) und `unlink()`: ein zweiter Prozess B
# konnte in dieser Luecke die tote Sperre uebernehmen, seinen eigenen Lock
# veroeffentlichen und lebend bleiben -- worauf A's ausstehendes `unlink()`
# nur noch den PFADNAMEN (jetzt B's lebenden Lock) traf und loeschte; A
# legte danach seinen eigenen an und beide Installer schrieben gleichzeitig.
# `unlink(path)` ist atomar, aber KEIN atomares Compare-and-delete: es
# entfernt, was JETZT unter dem Namen liegt, nicht "nur, wenn Inhalt==X".
# Der Fix ersetzt das Prinzip, statt nur einen weiteren Read einzufuegen:
#  * Ein toter frueherer Besitzer verliert seinen `flock` automatisch durch
#    den Kernel (fd-Schluss bei Prozessende) -- es gibt KEINE manuelle
#    Verwaist-Loeschung mehr, also auch kein read->unlink-Fenster.
#  * Ein lebender fremder Besitzer haelt den `flock` WIRKLICH -> unser
#    `LOCK_NB` scheitert -> wir weisen ab und fassen die Datei NICHT an.
#  * Der PID-Inhalt bleibt rein informativ (Fehlermeldung/Diagnose).
# `fcntl.flock` ist POSIX (Linux/macOS); Muster + virtiofs-Eignung sind in
# `mmo_sim/lab/runner.py:_acquire_lock` bereits belegt. Uebergangs-Caveat:
# eine von PRE-R6-Code geschriebene Altsperre (PID ohne gehaltenen flock)
# eines noch lebenden Prozesses wuerde hier als uebernahmefaehig gelten --
# bounded, da die Sperre nur waehrend eines aktiven Updatelaufs existiert
# und neuer Code durchgaengig flockt.
_HELD_LOCK_FDS: dict[str, int] = {}


def acquire_update_lock(repo: Path) -> Optional[str]:
    """`None` bei Erfolg (DIESER Prozess haelt ab jetzt den OS-Lock, bis
    `release_update_lock`), sonst ein Fehlertext (lebender fremder Besitzer
    ODER unklare/beschaedigte Sperre). Siehe R6-02-Block oben.

    Reentrancy: haelt dieser Prozess die Sperre bereits (Eintrag in
    `_HELD_LOCK_FDS`), ist ein zweiter Erwerb ein No-Op-Erfolg -- kein
    zweiter `flock` auf einer neuen fd (POSIX: Lock haengt an der
    open-file-description, ein zweiter unabhaengiger Erwerb im selben
    Prozess wuerde sich sonst selbst blockieren)."""
    lp = _lock_path(repo)
    key = _lock_registry_key(lp)
    if key in _HELD_LOCK_FDS:
        return None
    payload = f"{os.getpid()} {_now_iso()}".encode("utf-8")
    attempts = 0
    while True:
        attempts += 1
        if attempts > 1000:
            return (
                "Ein anderer Update-Vorgang blockiert die Sperre dauerhaft "
                "(staendige Neubelegung) — bitte erneut versuchen."
            )
        try:
            fd = os.open(str(lp), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            fd = None
        if fd is not None:
            # Frischer Erwerb: O_EXCL hat die Datei soeben exklusiv angelegt.
            # Zusaetzlich den OS-Lock belegen und die fd fuer die gesamte
            # Besitzdauer offen halten.
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                # Ein gleichzeitiger Reklamierer hat unsere frische Datei
                # bereits per O_RDWR geoeffnet und geflockt -- Datei stehen
                # lassen (Reklamationspfad der naechsten Runde behandelt sie)
                # und neu versuchen.
                os.close(fd)
                continue
            try:
                if not _fd_still_matches_path(fd, lp):
                    fcntl.flock(fd, fcntl.LOCK_UN)
                    os.close(fd)
                    continue
                os.pwrite(fd, payload, 0)
            except BaseException:
                try:
                    fcntl.flock(fd, fcntl.LOCK_UN)
                except OSError:
                    pass
                os.close(fd)
                raise
            _HELD_LOCK_FDS[key] = fd
            return None

        # Reklamationspfad: die Sperrdatei existiert bereits.
        try:
            fd = os.open(str(lp), os.O_RDWR)
        except FileNotFoundError:
            # Zwischen O_EXCL-Fehlschlag und hier verschwunden -> frisch neu.
            continue
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            # Ein ANDERER Prozess haelt den OS-Lock WIRKLICH (lebend) -- der
            # einzige Fall eines moeglichen Zweitschreibers, und genau den
            # verhindert flock strukturell. Datei NICHT anfassen.
            held = _peek_lock_pid(fd)
            os.close(fd)
            if held is not None and held != os.getpid():
                return (
                    f"Ein anderer Update-Vorgang läuft bereits (PID {held}) "
                    "— bitte warten oder abbrechen."
                )
            return (
                "Ein anderer Update-Vorgang läuft bereits — bitte warten "
                "oder abbrechen."
            )
        # flock erworben: NIEMAND haelt den OS-Lock. Ein toter frueherer
        # Besitzer hat ihn per Kernel verloren (keine manuelle Verwaist-
        # Loeschung noetig). Geist-fd ausschliessen (Pfad zwischenzeitlich
        # ersetzt?), dann Inhalt bewerten.
        if not _fd_still_matches_path(fd, lp):
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
            continue
        existing = _peek_lock_pid(fd)
        if existing is None:
            # Leer/unlesbar/unparsebar ist KEIN Beleg fuer "frei": unklare
            # Sperre kontrolliert HALTEN (G3a), NICHT ueberschreiben, NICHT
            # loeschen -- erworbenen flock wieder freigeben, abweisen.
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
            return (
                "Ein anderer Update-Vorgang läuft bereits (Sperre wird "
                "soeben geschrieben oder ist beschaedigt) — bitte erneut "
                "versuchen."
            )
        # Parsebarer PID eines frueheren Besitzers; der gehaltene flock
        # beweist, dass dieser NICHT mehr lebt. Besitz uebernehmen: nur den
        # informativen Payload in-place ersetzen (KEIN unlink, KEINE
        # Neuanlage -- der stabile Inode bleibt, es entsteht nie ein leer/
        # frei sichtbarer Zwischenzustand).
        try:
            os.ftruncate(fd, 0)
            os.pwrite(fd, payload, 0)
        except BaseException:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            except OSError:
                pass
            os.close(fd)
            raise
        _HELD_LOCK_FDS[key] = fd
        return None


def release_update_lock(repo: Path) -> None:
    """Gibt NUR die EIGENE, per `fcntl.flock` tatsaechlich gehaltene Sperre
    frei. Ohne gehaltene fd (keine Registry-Eintragung: Fremdsperre oder nie
    erworben) ist dies ein No-Op -- es wird NICHTS gelesen, nichts
    verglichen, nichts geloescht. Die Datei wird nur entfernt, wenn ihr
    AKTUELLER Verzeichniseintrag noch derselbe Inode wie die gehaltene fd
    ist; danach flock freigeben und fd schliessen."""
    lp = _lock_path(repo)
    key = _lock_registry_key(lp)
    fd = _HELD_LOCK_FDS.pop(key, None)
    if fd is None:
        return
    try:
        if _fd_still_matches_path(fd, lp):
            try:
                lp.unlink()
            except OSError:
                pass
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        except OSError:
            pass
        try:
            os.close(fd)
        except OSError:
            pass


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _apply_executable_bits(src: Path, dst: Path) -> None:
    """R4-03-Fix (01_GENERAL_REVIEW.md R4-03, 02_NACHZUG_AUFTRAG.md Block
    C): SHA256-Gleichheit sagt NICHTS über Dateimodi -- die in
    `validate_and_stage_zip` wiederhergestellten `0o111`-Bits kamen bei
    identischen Bytes bisher NICHT am Ziel an (der Resume-Skip ließ `dst`
    komplett unberührt, auch dessen Modus). Additiv NUR die ausführbaren
    Bits (`0o111`) aus dem bereits geprüften Staging-Quellmode auf `dst`
    übernehmen -- kein Folgen von Symlinks (Verteidigung in der Tiefe:
    `dst` ist an diesem Punkt bereits über `_resolved_dst_escapes_repo`
    als Nicht-Symlink bestätigt, hier zusätzlich erneut geprüft) und kein
    Übernehmen irgendwelcher anderer Modusbits (SUID/SGID/Sticky/Gruppen-/
    World-Schreibrechte aus dem Paket bleiben unberührt, nur die drei
    Ausführen-Bits werden -- additiv ODER-verknüpft, nie ersetzend --
    gesetzt)."""
    if dst.is_symlink():
        return
    try:
        wanted = src.stat().st_mode & 0o111
        if not wanted:
            return
        dst_mode = dst.stat().st_mode
        if (dst_mode & 0o111) != wanted:
            os.chmod(dst, dst_mode | wanted)
    except OSError:
        pass


def _atomic_copy_file(src: Path, dst: Path) -> None:
    """R4-04-Fix (01_GENERAL_REVIEW.md R4-04, 02_NACHZUG_AUFTRAG.md Block
    C): `shutil.copy2` schrieb bisher DIREKT in `dst` -- ein I/O-Fehler
    mitten in einer einzelnen Kopie konnte `dst` bereits gekürzt/teilweise
    überschrieben zurücklassen; ein Wiederanlauf, der nur Quell- ODER
    vollen Zielhash kennt, wertete einen solchen Teilinhalt als FREMDE
    Abweichung (`deviated`/`unverified`) statt als eigenen abgebrochenen
    Schritt. Stattdessen: vollständige Kopie in eine TEMPORÄRE Datei im
    GLEICHEN Zielverzeichnis (gleiches Dateisystem, `os.replace` ist dort
    atomar) -- `dst` wird so NIE in einem Teilzustand sichtbar: ein Fehler
    WÄHREND des Kopierens lässt `dst` unverändert (altes Original oder gar
    nicht vorhanden), ein Fehler NACH dem Kopieren aber vor `os.replace`
    hinterlässt höchstens eine verwaiste Temp-Datei (kein Produktpfad)."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{dst.name}.", suffix=".zrupd-tmp", dir=str(dst.parent))
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        shutil.copy2(src, tmp_path)
        os.replace(tmp_path, dst)
    except OSError:
        try:
            tmp_path.unlink()
        except OSError:
            pass
        raise


# ── Git-IO (read-only wo möglich) ────────────────────────────────────────

def git_cmd() -> list[str]:
    """Wie `launcher.py:_git_cmd()` — Default `git`, per `LAUNCHER_GIT`
    überschreibbar (z. B. eigener Credential-Wrapper)."""
    override = os.environ.get("LAUNCHER_GIT", "").strip()
    return override.split() if override else ["git"]


def run_git(repo: Path, *args: str, timeout: float = 20.0) -> subprocess.CompletedProcess:
    return subprocess.run(
        [*git_cmd(), "-C", str(repo), *args],
        capture_output=True, text=True, timeout=timeout,
    )


@dataclass
class LocalState:
    source: str          # "git" | "zip" | "unmanaged"
    rev: Optional[str]   # Commit-SHA (git) oder zuletzt verwaltete ZIP-Zielrevision
    dirty: bool
    detail: str


def detect_local_state(repo: Path) -> LocalState:
    """Bestimmt den WIRKLICH installierten Stand — Git selbst ist dabei
    die Autorität für Git-Checkouts (nicht die Statusdatei, die nur
    Zusatz-Metadaten hält); für ZIP-Installationen ist die Statusdatei die
    einzige Quelle. Fehlt sie (unverwaltete ZIP-Installation), ist `rev`
    bewusst `None` — ein unbekannter Stand darf nie als bestimmt gelten."""
    if (repo / ".git").exists():
        r = run_git(repo, "rev-parse", "HEAD")
        if r.returncode != 0:
            return LocalState("git", None, False, f"git rev-parse fehlgeschlagen: {r.stderr.strip()}")
        head = r.stdout.strip()
        dirty_r = run_git(repo, "status", "--porcelain", "--untracked-files=no")
        dirty = bool(dirty_r.stdout.strip()) if dirty_r.returncode == 0 else False
        return LocalState("git", head, dirty, "Git-Checkout")

    state = read_state(repo)
    if state.get("method") == "zip" and state.get("installed_rev"):
        # R3-04/d: `installed_rev` kam bisher ungeprüft aus der Statusdatei --
        # eine seither von Hand geänderte/entfernte verwaltete Datei blieb
        # unsichtbar ("current" trotz lokaler Abweichung). Jetzt wird der
        # tatsächliche Dateibestand gegen das zuletzt geschriebene SHA-256-
        # Manifest geprüft; jede Abweichung setzt `dirty` -- exakt dasselbe
        # Feld, das der Git-Zweig schon für "Revision stimmt, aber lokal
        # verändert" nutzt.
        managed = state.get("managed_files")
        dirty = False
        if isinstance(managed, dict):
            for relpath, expected_hash in managed.items():
                p = repo / relpath
                if not p.exists():
                    dirty = True
                    break
                try:
                    if _sha256_file(p) != expected_hash:
                        dirty = True
                        break
                except OSError:
                    dirty = True
                    break
        return LocalState("zip", state["installed_rev"], dirty, "verwaltete ZIP-Installation")
    return LocalState("unmanaged", None, False, "unverwaltete Installation (Herkunft nicht sicher bestimmbar)")


@dataclass
class IncompleteInstall:
    target_rev: str
    install_started_at: Optional[str]
    install_error: Optional[str]
    files_known: int


def incomplete_install(repo: Path) -> Optional[IncompleteInstall]:
    """R5-01: öffentliche Prüffunktion für einen PERSISTENTEN Teilinstal-
    lationszustand -- liest `install_phase` FRISCH von der Platte (kein
    In-Memory-Zustand wie `launcher._update_restart_required`), ist also
    auch in einem frisch gestarteten Prozess wahr.

    `_adopt_staged_update_locked` setzt `install_phase == "in_progress"`,
    BEVOR die erste Datei eines Laufs angefasst wird, und erst auf
    `"complete"`, wenn die GESAMTE Übernahme (inkl. Manifest-Update und
    `installed_rev`) durchgelaufen ist. Scheitert der Lauf mitten im
    Kopieren (`OSError`), bleibt `"in_progress"` stehen -- exakt der
    Mischzustand, den diese Funktion melden soll. Dieser Marker ist ZIP-
    spezifisch (`_adopt_staged_update_locked`); `mark_files_updated`
    (Git-Pfad) setzt ihn bei einem erfolgreichen Git-Update explizit auf
    `"complete"`, damit ein Git-Update nie fälschlich als Teilinstallation
    gilt.

    Liefert `None`, wenn KEINE Teilinstallation ansteht -- insbesondere
    auch dann, wenn nur eine reine Neustartpflicht besteht
    (`install_phase == "complete"`, aber `launcher._update_restart_
    required` im selben oder einem anderen Prozess True ist): eine
    abgeschlossene Übernahme, die nur noch auf ihren Neustart wartet, ist
    KEINE Teilinstallation -- das bleibt weiterhin Sache von
    `_block_if_restart_required`.

    Liefert außerdem IMMER `None` für ein tatsächliches Git-Checkout
    (`.git` vorhanden) -- der Marker ist ZIP-spezifisch; für ein
    Git-Checkout ist Git selbst die Autorität über den installierten
    Stand (s. `detect_local_state`), nicht diese Statusdatei. Das fängt
    auch den (unrealistischen, aber defensiv behandelten) Fall ab, dass
    ein VERWAISTER `"in_progress"`-Eintrag aus einer früheren ZIP-
    Installation in der Statusdatei stehen bleibt, nachdem die
    Installation anderweitig (z. B. manuell) auf ein Git-Checkout
    umgestellt wurde -- so ein Leftover darf niemals einen ZIP-
    Recovery-Versuch (`_attempt_zip_install`) auf einem Git-Checkout
    auslösen."""
    if (repo / ".git").exists():
        return None
    state = read_state(repo)
    if state.get("install_phase") != "in_progress":
        return None
    target_rev = state.get("target_rev")
    if not target_rev:
        # Sollte durch den Schreiber oben nie vorkommen (target_rev wird
        # IMMER zusammen mit install_phase="in_progress" geschrieben) --
        # ohne eine gebundene Zielrevision ist aber keine sinnvolle,
        # zielgebundene Wiederaufnahme möglich; ehrlich als "kein
        # bestimmbarer Teilinstallationszustand" behandeln statt zu raten.
        return None
    managed = state.get("managed_files")
    return IncompleteInstall(
        target_rev=target_rev,
        install_started_at=state.get("install_started_at"),
        install_error=state.get("install_error"),
        files_known=len(managed) if isinstance(managed, dict) else 0,
    )


def fetch_remote_head_via_git(
    repo: Path, *, remote: str = "origin", ref: str = "HEAD", timeout: float = 10.0,
) -> tuple[Optional[str], Optional[str]]:
    """Reiner Lesezugriff: `git ls-remote <remote> <ref>` — kein fetch/pull,
    tauscht nichts aus. Rückgabe `(sha, fehlergrund)`."""
    try:
        r = subprocess.run(
            [*git_cmd(), "-C", str(repo), "ls-remote", remote, ref],
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return None, "Zeitüberschreitung bei git ls-remote"
    except Exception as e:  # pragma: no cover - defensiv
        return None, f"{e.__class__.__name__}: {e}"
    if r.returncode != 0:
        last = (r.stderr.strip().splitlines() or ["git ls-remote fehlgeschlagen"])[-1]
        return None, last
    line = r.stdout.strip().splitlines()[0] if r.stdout.strip() else ""
    sha = line.split()[0] if line else None
    if not sha:
        return None, "git ls-remote lieferte keine lesbare Antwort"
    return sha, None


def _default_http_get(url: str, timeout: float) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "zeitriss-launcher-update"})
    with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 - feste https-API-URL/Test-Override
        return r.read()


def fetch_remote_head_via_api(
    api_url: str, *, http_get: Optional[Callable[[str, float], bytes]] = None, timeout: float = 10.0,
) -> tuple[Optional[str], Optional[str]]:
    """GitHub-REST `GET /repos/<owner>/<repo>/commits/<branch>` → `sha`.
    `http_get` ist für Tests injizierbar (kontrollierte HTTP-Fixture)."""
    getter = http_get or _default_http_get
    try:
        body = getter(api_url, timeout)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return None, f"{e.__class__.__name__}: {e}"
    except Exception as e:  # pragma: no cover - defensiv
        return None, f"{e.__class__.__name__}: {e}"
    try:
        data = json.loads(body)
        sha = data.get("sha") if isinstance(data, dict) else None
    except (json.JSONDecodeError, AttributeError, TypeError):
        return None, "Antwort der Quelle war kein lesbares JSON"
    if not sha or not isinstance(sha, str):
        return None, "Antwort enthielt keine Revision"
    return sha, None


# ── U1: Check (read-only) ────────────────────────────────────────────────

@dataclass
class UpdateCheckResult:
    status: str                  # "current" | "update_available" | "ahead" | "diverged" | "unknown"
    reason: str
    local: LocalState
    remote_rev: Optional[str]
    checked_at: str
    sync_pending: bool = False
    sync_detail: str = ""


def _git_object_present_locally(repo: Path, sha: str, *, timeout: float = 10.0) -> bool:
    """Prüft NUR, ob das Objekt bereits im lokalen Object-Store liegt (z. B.
    aus einem früheren `fetch`/`clone`) — ohne selbst zu fetchen. `check_for_
    update` darf laut Vertrag nie fetchen; diese Prüfung ist reine lokale
    Objekt-DB-Abfrage, kein Netzzugriff."""
    r = run_git(repo, "cat-file", "-e", f"{sha}^{{commit}}", timeout=timeout)
    return r.returncode == 0


def _git_is_ancestor(repo: Path, maybe_ancestor: str, descendant: str, *, timeout: float = 10.0) -> Optional[bool]:
    """`True`/`False` ob `maybe_ancestor` ein Vorfahre von `descendant` ist
    (oder gleich), `None` wenn das nicht bestimmbar war (z. B. fehlende
    Objekte nach einem reinen `ls-remote` ohne `fetch`). Nur lesend."""
    r = run_git(repo, "merge-base", "--is-ancestor", maybe_ancestor, descendant, timeout=timeout)
    if r.returncode == 0:
        return True
    if r.returncode == 1:
        return False
    return None


def check_for_update(
    repo: Path,
    *,
    remote: str = "origin",
    owner: str = OFFICIAL_REPO_OWNER,
    project: str = OFFICIAL_REPO_NAME,
    branch: str = OFFICIAL_BRANCH,
    http_get: Optional[Callable[[str, float], bytes]] = None,
    timeout: float = 10.0,
) -> UpdateCheckResult:
    """U1: vergleicht installierten gegen geprüften verfügbaren Stand, OHNE
    Dateien zu tauschen oder zu syncen. Eine nicht erreichbare Quelle oder
    eine unbestimmte lokale Herkunft ergibt NIE `"current"`."""
    local = detect_local_state(repo)
    checked_at = _now_iso()

    # R7-03 (ZR-ALTAIR-UPDATER-SPIELTEST-NACHZUG-20261119-R7 §04): kontrollierter
    # Vor-Merge-Kandidatenpfad -- NUR wirksam, wenn BEIDE Override-Variablen
    # (dieselbe Freischaltung wie der Archiv-URL-Override) gesetzt sind, damit
    # Zielrevision UND Archivbytes IMMER gemeinsam an denselben gepinnten
    # Kandidaten gebunden sind (s. `CANDIDATE_REV_ENV_OVERRIDE`-Docstring). Der
    # `reason`-Text nennt diesen Pfad ausdrücklich "kontrollierter Vor-Merge-
    # Test" -- NIE "geprüfte/offizielle Quelle" -- ein ungeprüftes Archiv wird
    # damit nicht als offizielles Main etikettiert. Ohne BEIDE Variablen bleibt
    # dieser Zweig inert; der Default-Check unten liest unverändert read-only
    # ausschließlich die offizielle Quelle.
    candidate_rev = os.environ.get(CANDIDATE_REV_ENV_OVERRIDE, "").strip()
    if candidate_rev and os.environ.get(ARCHIVE_URL_OVERRIDE_ENABLE_FLAG, "").strip():
        prior_state = read_state(repo)
        sync_pending = prior_state.get("sync_status") in ("pending", "failed")
        sync_detail = prior_state.get("sync_error", "") if sync_pending else ""
        write_state(repo, last_check_status="ok", last_check_at=checked_at, last_known_remote_rev=candidate_rev)
        if local.rev is None:
            return UpdateCheckResult(
                "unknown", "lokaler Stand nicht sicher bestimmbar (unverwaltete Installation)",
                local, candidate_rev, checked_at, sync_pending, sync_detail,
            )
        if local.rev == candidate_rev:
            return UpdateCheckResult(
                "current",
                "lokaler Stand entspricht dem gepinnten Kandidaten (kontrollierter Vor-Merge-Test, "
                "KEIN offizieller Check)",
                local, candidate_rev, checked_at, sync_pending, sync_detail,
            )
        return UpdateCheckResult(
            "update_available",
            "gepinnter Kandidat (kontrollierter Vor-Merge-Test, KEIN offizieller Check)",
            local, candidate_rev, checked_at, sync_pending, sync_detail,
        )

    if local.source == "git":
        remote_rev, err = fetch_remote_head_via_git(repo, remote=remote, timeout=timeout)
    else:
        api_url = GITHUB_API_COMMIT_URL.format(owner=owner, repo=project, branch=branch)
        remote_rev, err = fetch_remote_head_via_api(api_url, http_get=http_get, timeout=timeout)

    prior_state = read_state(repo)
    sync_pending = prior_state.get("sync_status") in ("pending", "failed")
    sync_detail = prior_state.get("sync_error", "") if sync_pending else ""

    if err or not remote_rev:
        write_state(repo, last_check_status="unknown", last_check_at=checked_at, last_check_error=err or "keine Revision")
        return UpdateCheckResult("unknown", err or "Quelle lieferte keine Revision", local, None, checked_at,
                                  sync_pending, sync_detail)

    write_state(repo, last_check_status="ok", last_check_at=checked_at, last_known_remote_rev=remote_rev)

    if local.rev is None:
        return UpdateCheckResult(
            "unknown", "lokaler Stand nicht sicher bestimmbar (unverwaltete Installation)",
            local, remote_rev, checked_at, sync_pending, sync_detail,
        )

    if local.rev == remote_rev:
        return UpdateCheckResult("current", "lokaler Stand entspricht der geprüften Quelle",
                                  local, remote_rev, checked_at, sync_pending, sync_detail)

    # R3-04/a: eine ungleiche Revision ist NICHT automatisch "neuer" --
    # ein lokaler Dev-Stand kann der geprüften Quelle bereits voraus sein,
    # oder beide Stände können divergiert sein. `check_for_update` darf
    # laut Vertrag nie fetchen (nur `ls-remote`), kann die Vorfahren-
    # beziehung also nur dann prüfen, wenn das Zielobjekt schon lokal
    # vorliegt (z. B. aus einem früheren Fetch/Clone). Liegt es nicht vor,
    # bleibt die ehrliche Antwort "update_available" (Ordnung unbestimmt,
    # aber neueres Objekt existiert nachweislich an der Quelle) -- siehe
    # Doku-Hinweis in `reason` für diesen Grenzfall.
    if local.source == "git" and _git_object_present_locally(repo, remote_rev, timeout=timeout):
        local_ahead = _git_is_ancestor(repo, remote_rev, local.rev, timeout=timeout)
        remote_ahead = _git_is_ancestor(repo, local.rev, remote_rev, timeout=timeout)
        if local_ahead and not remote_ahead:
            return UpdateCheckResult(
                "ahead", "lokaler Stand ist der geprüften Quelle bereits voraus (eigene Commits)",
                local, remote_rev, checked_at, sync_pending, sync_detail,
            )
        if local_ahead is False and remote_ahead is False:
            return UpdateCheckResult(
                "diverged", "lokaler Stand und geprüfte Quelle sind divergiert (kein gemeinsamer Fast-forward-Weg)",
                local, remote_rev, checked_at, sync_pending, sync_detail,
            )

    return UpdateCheckResult("update_available", "neuere Revision an der geprüften Quelle verfügbar",
                              local, remote_rev, checked_at, sync_pending, sync_detail)


# ── U2/U3 Git-Installationspfad ──────────────────────────────────────────

@dataclass
class GitUpdateResult:
    ok: bool
    message: str
    new_rev: Optional[str] = None


def perform_git_update(
    repo: Path, *, target_rev: Optional[str] = None, remote: str = "origin", timeout: float = 60.0,
) -> GitUpdateResult:
    """U2/U3: Fast-forward-only auf `target_rev` (pinnt exakt die beim Check
    gelesene Revision — wandert `remote` währenddessen weiter, betrifft das
    diesen Lauf nicht). Stoppt bei lokalen Änderungen oder einem nicht-FF-
    Divergenzfall mit konkretem Hinweis — kein Stash/Force/Reset hier."""
    dirty_r = run_git(repo, "status", "--porcelain", "--untracked-files=no", timeout=timeout)
    if dirty_r.returncode != 0:
        return GitUpdateResult(False, f"git status fehlgeschlagen: {dirty_r.stderr.strip()}")
    if dirty_r.stdout.strip():
        files = dirty_r.stdout.strip().splitlines()
        return GitUpdateResult(False, (
            "Lokale Änderungen an Repo-Dateien erkannt — Update gestoppt, nichts verändert "
            f"({len(files)} Datei(en)). Sichere/klärst du sie (z. B. `git stash` oder `git diff`), "
            "kannst du [4] danach erneut versuchen."
        ))

    fetch = run_git(repo, "fetch", remote, timeout=timeout)
    if fetch.returncode != 0:
        last = (fetch.stderr.strip().splitlines() or ["?"])[-1]
        return GitUpdateResult(False, f"git fetch fehlgeschlagen: {last}")

    rev = target_rev
    if rev is None:
        rev, err = fetch_remote_head_via_git(repo, remote=remote, timeout=timeout)
        if err or not rev:
            return GitUpdateResult(False, f"Zielrevision nicht bestimmbar: {err}")

    before = run_git(repo, "rev-parse", "HEAD", timeout=timeout).stdout.strip()
    if before == rev:
        return GitUpdateResult(True, "Bereits auf der Zielrevision.", rev)

    merge = subprocess.run(
        [*git_cmd(), "-C", str(repo), "merge", "--ff-only", rev],
        capture_output=True, text=True, timeout=timeout,
    )
    if merge.returncode != 0:
        lines = (merge.stdout + merge.stderr).strip().splitlines()
        last = lines[-1] if lines else "?"
        return GitUpdateResult(False, (
            f"Fast-forward nicht möglich ({last}) — dein lokaler Branch ist divergiert. "
            "Kein automatischer Reset/Force; bitte Stand manuell prüfen (z. B. `git log --oneline -5`)."
        ))
    # R3-04/b: `git merge --ff-only <rev>` kann exit 0 melden, OHNE HEAD auf
    # `rev` zu bewegen -- z. B. wenn `rev` bereits ein Vorfahre von HEAD ist
    # (lokaler Stand ist der Zielrevision schon voraus): Git meldet dann
    # "Already up to date.", HEAD bleibt unveraendert. Vorher wurde hier
    # blind `rev` als `new_rev` zurueckgegeben, auch wenn HEAD etwas ganz
    # anderes ist -- der tatsaechliche Stand nach dem Merge MUSS erneut
    # gelesen werden, statt den angefragten Zielwert ungeprueft zu behaupten.
    after = run_git(repo, "rev-parse", "HEAD", timeout=timeout).stdout.strip()
    if after != rev:
        after_short = after[:10] if after else "?"
        return GitUpdateResult(False, (
            f"Merge meldete Erfolg, aber HEAD ({after_short}) entspricht nicht der Zielrevision "
            f"({rev[:10]}) — z. B. weil dein Stand der Zielrevision bereits voraus ist. Nichts wurde "
            "zurückgesetzt; bitte Stand manuell prüfen (z. B. `git log --oneline -5`)."
        ))
    return GitUpdateResult(True, "Repo auf die geprüfte Zielrevision aktualisiert.", after)


def mark_files_updated(repo: Path, *, method: str, rev: str) -> None:
    """Hält den Dateistand fest, BEVOR der (separate) Sync-Schritt läuft —
    U5: Dateistand und Backend-Sync sind getrennte Ergebnisse.

    R5-01: `install_phase` ist ein ZIP-spezifischer Teilinstallations-
    marker (s. `_adopt_staged_update_locked`/`incomplete_install`). Der
    Git-Pfad hier tauscht Dateien immer atomar über `git merge --ff-only`
    aus (kein eigener Datei-für-Datei-Kopierschritt, der mittendrin
    scheitern könnte) -- er setzt den Marker deshalb explizit auf
    `"complete"`, statt ihn unberührt zu lassen. Ohne das könnte ein
    FRÜHERER, unterbrochener ZIP-Teilstand (`"in_progress"`) fälschlich
    weiter als offene Teilinstallation gelten, obwohl der tatsächliche
    Dateistand bereits durch den Git-Pfad vollständig und konsistent neu
    gesetzt wurde."""
    write_state(
        repo, method=method, installed_rev=rev, installed_at=_now_iso(),
        sync_status="pending", install_phase="complete",
    )


# ── U3/U4 ZIP-Installationspfad ──────────────────────────────────────────

def build_archive_url(rev: str, *, owner: str = OFFICIAL_REPO_OWNER, project: str = OFFICIAL_REPO_NAME) -> str:
    """URL der ZIP-Quelle für `rev`. Per `LAUNCHER_UPDATE_ARCHIVE_URL`
    überschreibbar (Platzhalter `{rev}`) — ausschließlich für Wartung/
    Tests, analog zur bestehenden `LAUNCHER_GIT`-Konvention: ändert NUR die
    Bezugs-URL, NIE den danach laufenden Sicherheitsweg (jedes Archiv
    durchläuft weiterhin ungekürzt `validate_and_stage_zip`). Ein normaler
    Spielerlauf setzt diese Variable nie; nur http/https/file erlaubt.
    Wirkt NUR, wenn zusätzlich `ARCHIVE_URL_OVERRIDE_ENABLE_FLAG` gesetzt
    ist (R3-04/e) -- sonst inert, auch wenn die Override-Variable selbst
    einen Wert hat (z. B. versehentlich aus einer alten Shell-Umgebung)."""
    override = os.environ.get(ARCHIVE_URL_ENV_OVERRIDE, "").strip()
    if override and not os.environ.get(ARCHIVE_URL_OVERRIDE_ENABLE_FLAG, "").strip():
        override = ""
    if override:
        url = override.format(rev=rev)
        scheme = url.split("://", 1)[0].lower() if "://" in url else ""
        if scheme not in _ALLOWED_ARCHIVE_SCHEMES:
            raise ValueError(f"{ARCHIVE_URL_ENV_OVERRIDE}: Schema {scheme!r} nicht erlaubt")
        return url
    return f"https://github.com/{owner}/{project}/archive/{rev}.zip"


def download_zip_archive(
    url: str, dest: Path, *, timeout: float = 30.0, max_bytes: int = MAX_DOWNLOAD_BYTES,
    opener: Optional[Callable] = None,
) -> None:
    """Lädt `url` in die (frische) Datei `dest`, mit hartem Größendeckel.
    `opener(url, timeout)` ist für Tests injizierbar (muss ein binäres,
    kontextfähiges Leseobjekt liefern). Schreibt NIE in den Repo-Baum."""
    open_fn = opener or (lambda u, t: urllib.request.urlopen(
        urllib.request.Request(u, headers={"User-Agent": "zeitriss-launcher-update"}), timeout=t))
    try:
        with open_fn(url, timeout) as resp:
            total = 0
            with open(dest, "wb") as out:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > max_bytes:
                        raise ValueError(f"Download überschreitet die Sicherheitsgrenze ({max_bytes} Bytes).")
                    out.write(chunk)
    except ValueError:
        raise
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise ValueError(f"Download fehlgeschlagen: {e.__class__.__name__}: {e}") from e


def validate_and_stage_zip(zip_path: Path, staging_root: Optional[Path] = None) -> Path:
    """U4: prüft JEDEN Archiveintrag (keine Symlinks/Sonderdateien, keine
    absoluten Pfade/Traversal, Größendeckel pro Datei und gesamt) und
    extrahiert erst danach in einen FRISCHEN Staging-Ordner — nie den
    echten Repo-Baum. Wirft `ValueError` mit konkretem Grund bei jeder
    Verletzung; nichts wird vor einer vollständig bestandenen Prüfung
    geschrieben."""
    if not zipfile.is_zipfile(zip_path):
        raise ValueError("Datei ist kein gültiges ZIP-Archiv (beschädigt oder falsches Format).")

    staging_root = staging_root or Path(tempfile.mkdtemp(prefix="zeitriss-update-staging-"))
    staging_root.mkdir(parents=True, exist_ok=True)
    resolved_root = staging_root.resolve()

    try:
        with zipfile.ZipFile(zip_path) as zf:
            infos = zf.infolist()
            if len(infos) > MAX_ZIP_ENTRIES:
                raise ValueError(f"ZIP enthält zu viele Einträge ({len(infos)}) — abgelehnt.")
            total = 0
            for info in infos:
                name = info.filename
                if not name or name.startswith("/") or name.startswith("\\") or ":" in name:
                    raise ValueError(f"Unsichere Pfadangabe im Archiv: {name!r}")
                if ".." in Path(name).parts:
                    raise ValueError(f"Pfad-Traversal im Archiv erkannt: {name!r}")
                mode = info.external_attr >> 16
                if stat.S_ISLNK(mode):
                    raise ValueError(f"Symlink im Archiv abgelehnt: {name!r}")
                # Nur echte Typ-Bits pruefen (S_IFMT) -- viele Zip-Erzeuger
                # (u.a. `zipfile.writestr(name, data)`, Windows-Tools) setzen
                # GAR KEINE Unix-Typ-Bits, nur Permission-Bits (z.B. 0o600).
                # `external_attr >> 16 == 0o600` ist dann eine VOELLIG normale
                # Datei, keine Sonderdatei -- `mode and not S_ISREG/S_ISDIR`
                # wuerde das faelschlich ablehnen, weil 0o600 selbst keine
                # S_IFREG-Bits (0o100000) trägt.
                file_type = stat.S_IFMT(mode)
                if file_type and not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                    raise ValueError(f"Sonderdatei im Archiv abgelehnt: {name!r}")
                if info.file_size > MAX_ZIP_ENTRY_BYTES:
                    raise ValueError(f"Einzeldatei zu groß: {name!r} ({info.file_size} Bytes)")
                total += info.file_size
                if total > MAX_ZIP_TOTAL_BYTES:
                    raise ValueError("ZIP-Gesamtgröße überschreitet die Sicherheitsgrenze.")
                target = (resolved_root / name).resolve()
                if target != resolved_root and resolved_root not in target.parents:
                    raise ValueError(f"Zielpfad außerhalb des Staging-Bereichs: {name!r}")
            zf.extractall(staging_root)
            # CRIT-R2-01/U3: `zipfile.extractall()` stellt die Unix-Permission-
            # Bits NICHT wieder her -> der dokumentierte Starter `zeitriss.sh`
            # (und jede andere im Archiv ausführbar markierte Datei) verlöre ihr
            # +x-Bit, und `./zeitriss.sh` wäre nach einem ZIP-Update ohne
            # manuelles `chmod +x` nicht mehr startbar. Darum die im Archiv
            # vermerkten AUSFÜHRUNGS-Bits gezielt wieder setzen: nur `0o111`
            # (nie Typ-, Setuid-/Setgid-/Sticky-Bits), nur additiv zu den vom
            # umask gesetzten Lese-/Schreibrechten, und nur wenn das Archiv für
            # diesen Eintrag überhaupt ein Exec-Bit vermerkt hat. Alle `name`
            # sind oben bereits auf Traversal/Absolut/Symlink/Sonderdatei
            # geprüft (die Funktion wirft sonst vor `extractall`).
            for info in infos:
                archived_exec = (info.external_attr >> 16) & 0o111
                if not archived_exec:
                    continue
                staged = resolved_root / info.filename
                if staged.is_file():
                    current = stat.S_IMODE(staged.stat().st_mode)
                    staged.chmod(current | archived_exec)
    except zipfile.BadZipFile as e:
        raise ValueError(f"ZIP-Archiv beschädigt: {e}") from e
    return staging_root


def _effective_source_root(staging_root: Path) -> Path:
    """GitHub-ZIPs wickeln den Inhalt in genau einen Top-Level-Ordner
    (`<repo>-<rev>/`) — den erkennen und überspringen wir hier."""
    entries = list(staging_root.iterdir())
    if len(entries) == 1 and entries[0].is_dir():
        return entries[0]
    return staging_root


@dataclass
class AdoptResult:
    ok: bool
    message: str
    files_copied: int = 0
    deviated: list = field(default_factory=list)
    unverified: list = field(default_factory=list)
    # R4-05b-Fix: Altdateien, deren Löschung aus Pfad-/Symlink-
    # Schutzgründen übersprungen wurde (bleiben als "weiterhin verwaltet"
    # im Manifest stehen) -- getrennt von `removed`, damit der Aufrufer
    # diesen Fall nicht mit einer normal entfernten entfallenen Datei
    # verwechselt.
    deletion_skipped: list = field(default_factory=list)


def _resolved_dst_escapes_repo(repo_real: Path, dst: Path) -> bool:
    """R3-02/b: `is_protected` prüft nur die Pfad-STRUKTUR gegen eine feste
    Liste -- ein vorhandener ZIEL-Symlink (oder ein symlinkbasierter
    übergeordneter Ordner) auf ein Ziel AUSSERHALB der Installation wird
    davon nicht erfasst, und `shutil.copy2` würde dem Symlink folgen und
    fremde Bytes außerhalb der Installation überschreiben. Deshalb hier
    zusätzlich die tatsächlich aufgelöste (alle Symlinks augelöst) Zielseite
    prüfen, nicht nur den nominellen relativen Pfad."""
    if dst.is_symlink():
        return True
    # Eltern-Verzeichnis real auflösen (folgt Symlinks in Zwischenordnern);
    # existiert es noch nicht, ist nichts umzuleiten -- sicher.
    parent = dst.parent
    try:
        real_parent = Path(os.path.realpath(parent))
    except OSError:
        return True
    if real_parent != repo_real and repo_real not in real_parent.parents:
        return True
    return False


def adopt_staged_update(
    repo: Path, staging_root: Path, target_rev: str, *, protected: tuple = PROTECTED_RELPATHS,
    allow_unverified_overwrite: bool = False,
) -> AdoptResult:
    """U3/U4/U5: übernimmt eine bereits von `validate_and_stage_zip`
    geprüfte Dateimenge in `repo`. Schützt `protected`-Pfade immer.

    Drei getrennte Sicherheitsfragen (R3-02/R3-03/R3-04):
    - `deviated`: eine VERWALTETE Datei (bekannter `baseline_hash` aus dem
      letzten Manifest) hat sich seit der letzten Übernahme geändert --
      IMMER ein Stopp, nie überschreibbar (das wäre Datenverlust an einer
      Datei, die wir selbst zuletzt geschrieben haben).
    - `unverified`: eine EXISTIERENDE Datei ohne bekannten `baseline_hash`
      (nie verwaltet, z. B. erste Migration einer unverwalteten ZIP-
      Installation) weicht vom neuen Paketinhalt ab. "Unverwaltet" ist kein
      Beleg für "unverändert" oder "zum Überschreiben freigegeben" (R3-02) --
      per Default ebenfalls ein Stopp, aber mit `allow_unverified_overwrite=
      True` NACH einer informierten Zustimmung des Nutzers (der Caller zeigt
      die Liste vorher an) überschreibbar. Stimmt der Dateiinhalt bereits
      mit dem NEUEN Paketinhalt überein, ist das kein echter Unterschied und
      wird nie als `unverified` gemeldet.
    - Resumability (R3-03): eine Datei, deren aktueller Inhalt schon exakt
      dem ZIEL-Inhalt entspricht (z. B. aus einem unterbrochenen vorherigen
      Lauf mit demselben `target_rev`), gilt NIE als Abweichung -- sie wird
      nur übersprungen (kein erneutes Schreiben nötig), nicht blockiert.

    Bei jedem Stopp wird GAR NICHTS geschrieben (kein Teil-Mix). Nach
    erfolgreicher Übernahme werden vormals verwaltete Dateien, die im neuen
    Paket entfallen sind, entfernt -- aber NUR wenn ihr aktueller Inhalt noch
    exakt dem letzten Manifest entspricht (sonst könnte eine lokale/fremde
    Datei mitgelöscht werden, s. R3-03-Abnahme "unverwaltete fremde Dateien
    nicht mitlöschen"). Eine PID-Lockdatei verhindert gleichzeitige
    Updateversuche auf derselben Installation."""
    source_root = _effective_source_root(staging_root)
    if not (source_root / "setup.json").exists():
        return AdoptResult(False, (
            "Der Staging-Inhalt sieht nicht wie ein ZEITRISS-Paket aus (setup.json fehlt) — "
            "Übernahme abgebrochen, die bestehende Installation ist unverändert."
        ))

    lock_err = acquire_update_lock(repo)
    if lock_err:
        return AdoptResult(False, lock_err)

    try:
        return _adopt_staged_update_locked(
            repo, source_root, target_rev, protected=protected,
            allow_unverified_overwrite=allow_unverified_overwrite,
        )
    finally:
        release_update_lock(repo)


def _adopt_staged_update_locked(
    repo: Path, source_root: Path, target_rev: str, *, protected: tuple, allow_unverified_overwrite: bool,
) -> AdoptResult:
    protected_abs = [(repo / p).resolve() for p in protected]

    def is_protected(rel: Path) -> bool:
        target = (repo / rel).resolve()
        return any(target == p or p in target.parents for p in protected_abs)

    repo_real = Path(os.path.realpath(repo))
    prior_manifest = (read_state(repo).get("managed_files") or {})
    if not isinstance(prior_manifest, dict):
        prior_manifest = {}

    planned: list[tuple[Path, Path, str]] = []  # (src, rel, planned_hash)
    deviated: list[str] = []
    unverified: list[str] = []
    escaped: list[str] = []
    for root, _dirs, files in os.walk(source_root):
        rel_root = Path(root).relative_to(source_root)
        for fname in files:
            rel = rel_root / fname if str(rel_root) != "." else Path(fname)
            if is_protected(rel):
                continue
            relposix = rel.as_posix()
            src = Path(root) / fname
            dst = repo / rel
            if _resolved_dst_escapes_repo(repo_real, dst):
                escaped.append(relposix)
                continue
            baseline_hash = prior_manifest.get(relposix)
            planned_hash = _sha256_file(src)
            if dst.exists():
                try:
                    current_hash = _sha256_file(dst)
                except OSError:
                    current_hash = None
                if current_hash != planned_hash:
                    # Noch nicht auf dem Zielinhalt -- echte Abweichung?
                    if baseline_hash is not None:
                        if current_hash != baseline_hash:
                            deviated.append(relposix)
                    elif current_hash is not None and not allow_unverified_overwrite:
                        unverified.append(relposix)
                # current_hash == planned_hash: bereits auf Zielstand (z. B.
                # Rest eines unterbrochenen Laufs) -- keine Abweichung.
            planned.append((src, rel, planned_hash))

    if escaped:
        shown = ", ".join(escaped[:5])
        return AdoptResult(False, (
            f"Zielpfad zeigt über einen Symlink aus der Installation heraus: {shown} — "
            "Übernahme gestoppt, NICHTS wurde verändert. Symlink entfernen/ersetzen, dann erneut versuchen."
        ))

    if deviated:
        shown = ", ".join(deviated[:5])
        more = f" (+{len(deviated) - 5} weitere)" if len(deviated) > 5 else ""
        return AdoptResult(False, (
            f"Lokale Änderungen an verwalteten Dateien seit der letzten Aktualisierung erkannt: "
            f"{shown}{more}. Übernahme gestoppt, NICHTS wurde verändert. Sichere oder verwerfe diese "
            "Dateien bewusst, dann [4] erneut versuchen."
        ), deviated=deviated)

    if unverified:
        shown = ", ".join(unverified[:5])
        more = f" (+{len(unverified) - 5} weitere)" if len(unverified) > 5 else ""
        return AdoptResult(False, (
            f"Vorhandene, bisher NIE verwaltete Datei(en) weichen vom neuen Paketinhalt ab: "
            f"{shown}{more}. Herkunft nicht verlässlich bestimmbar (unverwaltet ≠ unverändert) — "
            "Übernahme gestoppt, NICHTS wurde verändert. Bewusst bestätigen oder diese Dateien vorher "
            "sichern/entfernen, dann erneut versuchen."
        ), unverified=unverified)

    # R5-01: `install_phase="in_progress"` ist der PERSISTENTE (disk-
    # gelesene) Teilinstallationsmarker -- anders als `_update_
    # restart_required` in launcher.py (ein In-Memory-Modulattribut, das
    # ein frischer Prozess nie sieht) überlebt dieser hier einen
    # Prozessneustart. Gesetzt BEVOR die erste Datei dieses Laufs
    # tatsächlich angefasst wird (zusammen mit `target_rev`); bleibt bei
    # einem `OSError` mitten im Kopieren unten unverändert stehen (der
    # dortige `write_state`-Aufruf setzt dieses Feld bewusst NICHT erneut
    # -- `write_state` merged nur die übergebenen Felder, lässt alles
    # andere unberührt). Erst der Erfolgsfall am Ende dieser Funktion
    # setzt ihn auf `"complete"`.
    write_state(
        repo, method="zip", sync_status="pending", install_started_at=_now_iso(),
        target_rev=target_rev, install_phase="in_progress",
    )

    copied = 0
    new_manifest = dict(prior_manifest)
    try:
        for src, rel, planned_hash in planned:
            dst = repo / rel
            if dst.exists():
                try:
                    if _sha256_file(dst) == planned_hash:
                        # R4-03-Fix: identische Bytes duerfen fehlende
                        # 0o111-Bits nicht ueberspringen (s. _apply_
                        # executable_bits-Docstring).
                        _apply_executable_bits(src, dst)
                        new_manifest[rel.as_posix()] = planned_hash
                        # R4-04-Fix (Zielbindung): das Manifest wird PRO
                        # DATEI persistiert (nicht erst am Ende) -- ein
                        # Abbruch an SPAETERER Stelle laesst den Fortschritt
                        # bis hierher ehrlich im State stehen, statt ihn bei
                        # einem naechsten Lauf (ggf. gegen eine inzwischen
                        # NEUERE Remote-Revision) als fremde Abweichung
                        # misszudeuten (s. Moduldoc-Verweis R4-04 oben).
                        write_state(repo, managed_files=new_manifest)
                        continue  # R3-03: bereits auf Zielstand, nicht erneut schreiben
                except OSError:
                    pass
            # R4-04-Fix: atomarer Austausch statt direkter `shutil.copy2`
            # in `dst` -- ein Fehler WAEHREND dieser einen Datei kann `dst`
            # dadurch nicht mehr in einem teilweise geschriebenen Zustand
            # zuruecklassen (s. _atomic_copy_file-Docstring).
            _atomic_copy_file(src, dst)
            new_manifest[rel.as_posix()] = planned_hash
            copied += 1
            write_state(repo, managed_files=new_manifest)  # R4-04: pro Datei persistiert, s.o.
    except OSError as e:
        write_state(repo, sync_status="failed", install_error=f"{e.__class__.__name__}: {e}")
        return AdoptResult(False, (
            f"Übernahme mitten im Kopieren abgebrochen: {e.__class__.__name__}: {e}. "
            f"{copied} von {len(planned)} Datei(en) in diesem Lauf übernommen — [4] erneut ausführen, "
            "um gezielt weiterzumachen (bereits korrekt kopierte Dateien werden beim Wiederanlauf "
            "erkannt und nicht erneut als Abweichung gewertet)."
        ), files_copied=copied)

    # R3-03: vormals verwaltete Dateien, die im neuen Paket entfallen sind,
    # werden entfernt -- NUR wenn ihr aktueller Inhalt noch exakt dem
    # letzten Manifest entspricht (sonst bleiben sie unberührt liegen,
    # damit nie eine fremde/lokal veränderte Datei mitgelöscht wird).
    new_relposix = {rel.as_posix() for _src, rel, _h in planned}
    removed = []
    deletion_skipped = []
    for relposix, old_hash in prior_manifest.items():
        if relposix in new_relposix:
            continue
        p = repo / relposix
        # R4-05b-Fix (01_GENERAL_REVIEW.md R4-05b, 02_NACHZUG_AUFTRAG.md
        # Block C): dieselbe Ziel-/Symlink-Schutzprüfung wie bei geplanten
        # Kopien -- OHNE sie würde `p.unlink()` einem Symlink-Elternordner
        # (oder einem selbst symlinkten `p`) folgen und außerhalb der
        # Installation löschen. Eine so geschützte Datei bleibt bewusst
        # als weiterhin "verwaltet" im Manifest stehen (kein Löschversuch)
        # und wird dem Aufrufer getrennt von `removed` gemeldet -- die
        # Dateiübernahme selbst ist zu diesem Zeitpunkt bereits
        # abgeschlossen, ein Abbruch der GESAMTEN Übernahme wäre hier nicht
        # verhältnismäßig.
        if _resolved_dst_escapes_repo(repo_real, p):
            deletion_skipped.append(relposix)
            continue
        if not p.exists():
            # R4-05c-Fix (01_GENERAL_REVIEW.md R4-05c): eine bereits VOR
            # dieser Übernahme fehlende Altdatei war nie "soeben entfernt"
            # -- sie wird trotzdem aus dem Manifest genommen (ein weiterhin
            # gemeldeter "verwaltet"-Eintrag für eine nicht mehr
            # existierende Datei würde den nächsten Lauf fälschlich als
            # dirty/entfallen markieren), aber bewusst NICHT in `removed`
            # gezählt (ehrliche Unterscheidung "von diesem Lauf entfernt"
            # vs. "war schon vorher weg").
            new_manifest.pop(relposix, None)
            continue
        try:
            if _sha256_file(p) != old_hash:
                continue  # lokal veraendert -- nicht automatisch entfernen
        except OSError:
            continue
        try:
            p.unlink()
            removed.append(relposix)
        except OSError:
            # R4-05c-Fix: eine fehlgeschlagene Löschung bleibt bewusst im
            # Manifest stehen (die Datei existiert unveraendert mit ihrem
            # alten Hash weiter -- "weiterhin verwaltet" ist hier ehrlich,
            # NICHT "erfolgreich entfernt").
            continue
        new_manifest.pop(relposix, None)

    write_state(
        repo, method="zip", installed_rev=target_rev, installed_at=_now_iso(),
        sync_status="pending", managed_files=new_manifest, install_phase="complete",
    )
    msg = "Programmdateien übernommen. Die Synchronisierung mit OpenWebUI steht noch aus."
    if removed:
        msg += f" ({len(removed)} entfallene Datei(en) entfernt.)"
    if deletion_skipped:
        shown = ", ".join(deletion_skipped[:5])
        more = f" (+{len(deletion_skipped) - 5} weitere)" if len(deletion_skipped) > 5 else ""
        msg += (
            f" ACHTUNG: {len(deletion_skipped)} entfallene Datei(en) NICHT gelöscht (Pfad zeigt über "
            f"einen Symlink aus der Installation heraus, bleiben als verwaltet stehen): {shown}{more}."
        )
    return AdoptResult(True, msg, files_copied=copied, deletion_skipped=deletion_skipped)


@dataclass
class ZipUpdateResult:
    ok: bool
    message: str
    installed_rev: Optional[str] = None
    deviated: list = field(default_factory=list)
    unverified: list = field(default_factory=list)


def perform_zip_update(
    repo: Path, *, zip_url: str, target_rev: str, opener: Optional[Callable] = None, timeout: float = 120.0,
    allow_unverified_overwrite: bool = False,
) -> ZipUpdateResult:
    """U3: kompletter ZIP-Weg ohne Git — Download in frisches Staging,
    Sicherheitsprüfung, dann Übernahme. Räumt Staging/Download danach auf.
    `allow_unverified_overwrite` s. `adopt_staged_update` (R3-02): NUR nach
    informierter Zustimmung des Nutzers setzen, der die `unverified`-Liste
    aus einem vorherigen Versuch bereits gesehen hat."""
    tmp_dir = Path(tempfile.mkdtemp(prefix="zeitriss-update-dl-"))
    try:
        zip_path = tmp_dir / "update.zip"
        try:
            download_zip_archive(zip_url, zip_path, opener=opener, timeout=timeout)
        except ValueError as e:
            return ZipUpdateResult(False, str(e))

        try:
            staging = validate_and_stage_zip(zip_path, staging_root=tmp_dir / "staging")
        except ValueError as e:
            return ZipUpdateResult(False, str(e))

        adopt = adopt_staged_update(repo, staging, target_rev, allow_unverified_overwrite=allow_unverified_overwrite)
        if not adopt.ok:
            return ZipUpdateResult(False, adopt.message, deviated=adopt.deviated, unverified=adopt.unverified)
        return ZipUpdateResult(True, adopt.message, installed_rev=target_rev)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ── U5: Sync im NEUEN Prozess ────────────────────────────────────────────

def _parse_sync_result_line(output: str) -> Optional[dict]:
    """UPD-2: parst die EINE maschinenlesbare `SYNC_RESULT ...`-Zeile, die
    `setup.py --sync` am Ende jedes Laufs auf stdout schreibt (s. dortiges
    `_print_sync_machine_summary`). Keine neue Jobengine/IPC -- nur ein
    strukturiertes Feld auf dem bereits bestehenden, vollständig
    gepufferten Prozess-Output. `None`, wenn keine (oder keine lesbare)
    Zeile gefunden wurde -- ein älterer/fremder `setup.py`-Stand ohne
    diese Zeile darf NICHT als "0 Dateien" fehlinterpretiert werden.

    U3-Restnachzug (UPDATE_UX_REVIEW.md U3, 02_RESTAUFTRAG.md §U3):
    `coverage_undetermined` ist ein zusätzliches, rein lesendes Feld --
    fehlt es (älterer `setup.py`-Stand ohne diesen Nachzug), bleibt der
    Default `False` (identisch zum bisherigen, impliziten Verhalten: ein
    nicht-leeres `kb_failed` galt bislang IMMER als nachgewiesen fehlend)."""
    for line in reversed(output.splitlines()):
        line = line.strip()
        if not line.startswith("SYNC_RESULT "):
            continue
        fields: dict[str, str] = {}
        for tok in line[len("SYNC_RESULT "):].split(" "):
            if "=" not in tok:
                continue
            key, _, val = tok.partition("=")
            fields[key] = val
        try:
            kb_total = int(fields.get("kb_total", ""))
            kb_confirmed = int(fields.get("kb_confirmed", ""))
        except ValueError:
            return None
        kb_failed_raw = fields.get("kb_failed", "")
        kb_failed = [n for n in kb_failed_raw.split(",") if n]
        preset_ok = fields.get("preset_ok") == "1"
        coverage_undetermined = fields.get("coverage_undetermined") == "1"
        return {
            "kb_total": kb_total, "kb_confirmed": kb_confirmed,
            "kb_failed": kb_failed, "preset_ok": preset_ok,
            "coverage_undetermined": coverage_undetermined,
        }
    return None


class _StreamedCompleted:
    """Minimaler Ersatz für `subprocess.CompletedProcess` -- liefert
    `returncode`/`stdout`/`stderr` in derselben Form, die `run_sync_
    subprocess` unten bereits erwartet (`r.returncode`, `r.stdout + r.
    stderr`). `stderr` bleibt leer, da `_run_sync_streaming` stdout/stderr
    des Kindprozesses bereits zu EINEM chronologischen Strom zusammenführt
    (sonst müsste die Zeilenreihenfolge beim Zusammenführen rekonstruiert
    werden, ohne echten Mehrwert für Tail/`SYNC_RESULT`-Parsing)."""

    def __init__(self, returncode: int, stdout: str):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = ""


def _run_sync_streaming(cmd: list[str], *, cwd: str, timeout: float, env: dict) -> _StreamedCompleted:
    """U4 (UPDATE_UX_REVIEW.md R4, 02_RESTAUFTRAG.md §U4): ersetzt den
    bisherigen `subprocess.run(..., capture_output=True)` -- der puffert
    JEDE Ausgabe vollständig bis Prozessende, das Launcher-Menü [4] zeigte
    während eines laufenden Syncs deshalb WEDER aktuelle Datei noch Phase
    an (erst nach Abschluss/Abbruch). Liest stattdessen über einen
    Reader-Thread + Queue zeilenweise UND gibt jede Zeile sofort auf
    stdout aus, während derselbe äußere `timeout` durchgängig gegen die
    verstrichene Zeit geprüft wird (max. 1 s Polling-Granularität) --
    funktioniert auch bei einem Kindprozess, der für eine Weile GAR KEINE
    Zeile schreibt (reiner `readline()`-Blockierung ohne Timeout würde das
    verpassen). Bei Überschreiten: `proc.kill()` + dieselbe `subprocess.
    TimeoutExpired`, die der bisherige `subprocess.run`-Pfad auch warf --
    der Caller unterscheidet beide Pfade nicht."""
    proc = subprocess.Popen(
        cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1, env=env,
    )
    line_queue: "queue.Queue[Optional[str]]" = queue.Queue()

    def _reader() -> None:
        try:
            assert proc.stdout is not None
            for line in proc.stdout:
                line_queue.put(line)
        finally:
            line_queue.put(None)  # Sentinel: Pipe geschlossen (Prozessende).

    reader_thread = threading.Thread(target=_reader, daemon=True)
    reader_thread.start()

    lines: list[str] = []
    start = time.monotonic()
    while True:
        remaining = timeout - (time.monotonic() - start)
        if remaining <= 0:
            proc.kill()
            proc.wait()
            if proc.stdout is not None:
                proc.stdout.close()
            raise subprocess.TimeoutExpired(cmd=cmd, timeout=timeout, output="".join(lines))
        try:
            line = line_queue.get(timeout=min(remaining, 1.0))
        except queue.Empty:
            continue
        if line is None:
            break
        print(line, end="", flush=True)
        lines.append(line)
    proc.wait()
    if proc.stdout is not None:
        proc.stdout.close()
    return _StreamedCompleted(proc.returncode, "".join(lines))


def run_sync_subprocess(
    repo: Path, *, variant: Optional[str] = None, all_variants: bool = False, timeout: float = 600.0,
    argv_override: Optional[list[str]] = None, runner: Optional[Callable] = None,
) -> tuple[bool, str]:
    """U5: führt `scripts/setup.py --sync` in einem NEUEN Python-Prozess
    aus (eigener Interpreterstart über `sys.executable`), statt die im
    laufenden Launcher bereits importierten alten `setup`-Modulbytes
    erneut aufzurufen — ein frischer Dateistand auf der Platte wird damit
    garantiert durch frisch geladenen Code behandelt. `argv_override`/
    `runner` sind für Tests injizierbar (kontrollierte Fixture statt eines
    echten Backend-Aufrufs). Schreibt das Sync-Ergebnis GETRENNT vom
    Dateistand in die Statusdatei -- inkl. der UPD-2-Aufschlüsselung
    (`kb_total`/`kb_confirmed`/`kb_failed`/`preset_ok`), wenn der
    Kindprozess die `SYNC_RESULT`-Zeile liefert (s. `_parse_sync_result_
    line`); ohne sie bleiben diese Felder unverändert/unbestimmt.

    U3 (UPDATE_UX_REVIEW.md R3): `kb_checked_at` wird NUR gemeinsam MIT den
    `kb_*`-Feldern geschrieben -- also GENAU dann, wenn dieser Lauf wirklich
    eine `SYNC_RESULT`-Zeile geliefert hat. Ein Timeout oder ein Fehlschlag
    OHNE lesbare Zeile (`kb_summary is None`) lässt `kb_checked_at` UND die
    `kb_*`-Zähler vollständig unangetastet (`write_state`-Merge) -- VORHER
    bekam `sync_failed_at` bei jedem Lauf einen frischen Zeitstempel, auch
    wenn die `kb_*`-Zähler aus einem GANZ ANDEREN, älteren Lauf stammten
    (`_describe_kb_sync_status`/`_check_persisted_sync_status` las dann
    `sync_at or sync_failed_at`, zeigte also einen falschen "Stand:" neben
    stehengebliebenen Zählern an). `sync_at`/`sync_failed_at` bleiben
    unverändert die Zeit des GESAMTLAUFS (Erfolg/Fehlschlag des Kommandos),
    unabhängig davon, ob dieser Lauf überhaupt eine KB-Aufschlüsselung
    geliefert hat.

    U4 (UPDATE_UX_REVIEW.md R4): ohne injizierten `runner` läuft der Kind-
    prozess jetzt über `_run_sync_streaming` -- zeilenweise gelesen UND
    sofort ausgegeben, statt vollständig gepuffert erst nach Prozessende
    (`subprocess.run(capture_output=True)`). `ZEITRISS_SYNC_OUTER_DEADLINE_S`
    (= `timeout`) wird dem Kindprozess als Env-Var mitgegeben, damit `setup.
    py --sync` seine PRO-DATEI-Readiness-Deadlines am selben äußeren Rahmen
    deckeln kann (s. dort `_file_ready_deadline_s`), statt unabhängig davon
    bis zu 90 s PRO Datei zu pollen und den äußeren Rahmen zu überlaufen."""
    cmd = list(argv_override) if argv_override is not None else [
        sys.executable, str(repo / "scripts" / "setup.py"), "--sync", "--yes",
    ]
    if argv_override is None:
        if all_variants:
            cmd.append("--all-variants")
        elif variant:
            cmd.extend(["--variant", variant])

    env = dict(os.environ)
    env["ZEITRISS_SYNC_OUTER_DEADLINE_S"] = str(timeout)

    try:
        if runner is not None:
            r = runner(cmd, cwd=str(repo), capture_output=True, text=True, timeout=timeout, env=env)
        else:
            r = _run_sync_streaming(cmd, cwd=str(repo), timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        write_state(repo, sync_status="failed", sync_error="Sync-Zeitüberschreitung", sync_failed_at=_now_iso())
        return False, "Sync-Zeitüberschreitung."

    combined = r.stdout + r.stderr
    tail = "\n".join(combined.strip().splitlines()[-12:])
    kb_summary = _parse_sync_result_line(combined)
    extra_fields = dict(kb_summary) if kb_summary else {}
    if kb_summary:
        extra_fields["kb_checked_at"] = _now_iso()

    if r.returncode == 0:
        write_state(repo, sync_status="ok", sync_at=_now_iso(), sync_error=None, **extra_fields)
        return True, tail
    write_state(repo, sync_status="failed", sync_error=tail, sync_failed_at=_now_iso(), **extra_fields)
    return False, tail


# ── U6: Neustart ─────────────────────────────────────────────────────────

def restart_launcher(repo: Path, *, exec_fn: Optional[Callable[[list[str]], None]] = None) -> None:
    """Ersetzt den laufenden Prozess durch einen frischen Start über den
    echten Starter-Einstieg (`scripts/zeitriss.py`) — kein Weiterspielen
    mit bereits importierten alten Modulen nach einem Dateitausch.
    `exec_fn` ist für Tests injizierbar (captured call statt echtem
    `os.execv`, das den Testprozess ersetzen würde)."""
    entry = repo / "scripts" / "zeitriss.py"
    argv = [sys.executable, str(entry)]
    fn = exec_fn or (lambda a: os.execv(a[0], a))
    fn(argv)
