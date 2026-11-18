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

import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

# ── Konstanten ─────────────────────────────────────────────────────────

STATE_FILENAME = ".zeitriss-update-state.json"

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
ARCHIVE_URL_ENV_OVERRIDE = "LAUNCHER_UPDATE_ARCHIVE_URL"
_ALLOWED_ARCHIVE_SCHEMES = ("http", "https", "file")

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


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


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
        return LocalState("zip", state["installed_rev"], False, "verwaltete ZIP-Installation")
    return LocalState("unmanaged", None, False, "unverwaltete Installation (Herkunft nicht sicher bestimmbar)")


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
    status: str                  # "current" | "update_available" | "unknown"
    reason: str
    local: LocalState
    remote_rev: Optional[str]
    checked_at: str
    sync_pending: bool = False
    sync_detail: str = ""


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
    return GitUpdateResult(True, "Repo auf die geprüfte Zielrevision aktualisiert.", rev)


def mark_files_updated(repo: Path, *, method: str, rev: str) -> None:
    """Hält den Dateistand fest, BEVOR der (separate) Sync-Schritt läuft —
    U5: Dateistand und Backend-Sync sind getrennte Ergebnisse."""
    write_state(repo, method=method, installed_rev=rev, installed_at=_now_iso(), sync_status="pending")


# ── U3/U4 ZIP-Installationspfad ──────────────────────────────────────────

def build_archive_url(rev: str, *, owner: str = OFFICIAL_REPO_OWNER, project: str = OFFICIAL_REPO_NAME) -> str:
    """URL der ZIP-Quelle für `rev`. Per `LAUNCHER_UPDATE_ARCHIVE_URL`
    überschreibbar (Platzhalter `{rev}`) — ausschließlich für Wartung/
    Tests, analog zur bestehenden `LAUNCHER_GIT`-Konvention: ändert NUR die
    Bezugs-URL, NIE den danach laufenden Sicherheitsweg (jedes Archiv
    durchläuft weiterhin ungekürzt `validate_and_stage_zip`). Ein normaler
    Spielerlauf setzt diese Variable nie; nur http/https/file erlaubt."""
    override = os.environ.get(ARCHIVE_URL_ENV_OVERRIDE, "").strip()
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


def adopt_staged_update(
    repo: Path, staging_root: Path, target_rev: str, *, protected: tuple = PROTECTED_RELPATHS,
) -> AdoptResult:
    """U3/U4/U5: übernimmt eine bereits von `validate_and_stage_zip`
    geprüfte Dateimenge in `repo`. Schützt `protected`-Pfade immer.
    Erkennt lokale Abweichungen seit der letzten verwalteten Übernahme
    über ein SHA-256-Manifest (`managed_files` in der Statusdatei); bei
    JEDER Abweichung wird GAR NICHTS geschrieben (kein Teil-Mix), die
    betroffenen Dateien werden konkret benannt. Eine bisher unverwaltete
    Installation (kein Manifest) hat per Definition keine Abweichung —
    die erste bewusst gewählte Aktualisierung überführt sie in den
    verwalteten Stand, statt die Zielrevision blind als "schon
    installiert" zu verbuchen."""
    source_root = _effective_source_root(staging_root)
    if not (source_root / "setup.json").exists():
        return AdoptResult(False, (
            "Der Staging-Inhalt sieht nicht wie ein ZEITRISS-Paket aus (setup.json fehlt) — "
            "Übernahme abgebrochen, die bestehende Installation ist unverändert."
        ))

    protected_abs = [(repo / p).resolve() for p in protected]

    def is_protected(rel: Path) -> bool:
        target = (repo / rel).resolve()
        return any(target == p or p in target.parents for p in protected_abs)

    prior_manifest = (read_state(repo).get("managed_files") or {})
    if not isinstance(prior_manifest, dict):
        prior_manifest = {}

    planned: list[tuple[Path, Path]] = []
    deviated: list[str] = []
    for root, _dirs, files in os.walk(source_root):
        rel_root = Path(root).relative_to(source_root)
        for fname in files:
            rel = rel_root / fname if str(rel_root) != "." else Path(fname)
            if is_protected(rel):
                continue
            relposix = rel.as_posix()
            baseline_hash = prior_manifest.get(relposix)
            dst = repo / rel
            if baseline_hash is not None and dst.exists():
                try:
                    current_hash = _sha256_file(dst)
                except OSError:
                    current_hash = None
                if current_hash != baseline_hash:
                    deviated.append(relposix)
            planned.append((Path(root) / fname, rel))

    if deviated:
        shown = ", ".join(deviated[:5])
        more = f" (+{len(deviated) - 5} weitere)" if len(deviated) > 5 else ""
        return AdoptResult(False, (
            f"Lokale Änderungen an verwalteten Dateien seit der letzten Aktualisierung erkannt: "
            f"{shown}{more}. Übernahme gestoppt, NICHTS wurde verändert. Sichere oder verwerfe diese "
            "Dateien bewusst, dann [4] erneut versuchen."
        ), deviated=deviated)

    write_state(repo, method="zip", sync_status="pending", install_started_at=_now_iso(), target_rev=target_rev)

    copied = 0
    new_manifest = dict(prior_manifest)
    try:
        for src, rel in planned:
            dst = repo / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            new_manifest[rel.as_posix()] = _sha256_file(dst)
            copied += 1
    except OSError as e:
        write_state(repo, sync_status="failed", install_error=f"{e.__class__.__name__}: {e}")
        return AdoptResult(False, (
            f"Übernahme mitten im Kopieren abgebrochen: {e.__class__.__name__}: {e}. "
            f"{copied} von {len(planned)} Datei(en) bereits übernommen — [4] erneut ausführen, "
            "um gezielt weiterzumachen (nichts wird dabei als 'fertig' markiert, bis alles durch ist)."
        ), files_copied=copied)

    write_state(
        repo, method="zip", installed_rev=target_rev, installed_at=_now_iso(),
        sync_status="pending", managed_files=new_manifest,
    )
    return AdoptResult(True, "Programmdateien übernommen. Die Synchronisierung mit OpenWebUI steht noch aus.",
                        files_copied=copied)


@dataclass
class ZipUpdateResult:
    ok: bool
    message: str
    installed_rev: Optional[str] = None


def perform_zip_update(
    repo: Path, *, zip_url: str, target_rev: str, opener: Optional[Callable] = None, timeout: float = 120.0,
) -> ZipUpdateResult:
    """U3: kompletter ZIP-Weg ohne Git — Download in frisches Staging,
    Sicherheitsprüfung, dann Übernahme. Räumt Staging/Download danach auf."""
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

        adopt = adopt_staged_update(repo, staging, target_rev)
        if not adopt.ok:
            return ZipUpdateResult(False, adopt.message)
        return ZipUpdateResult(True, adopt.message, installed_rev=target_rev)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ── U5: Sync im NEUEN Prozess ────────────────────────────────────────────

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
    Dateistand in die Statusdatei."""
    cmd = list(argv_override) if argv_override is not None else [
        sys.executable, str(repo / "scripts" / "setup.py"), "--sync", "--yes",
    ]
    if argv_override is None:
        if all_variants:
            cmd.append("--all-variants")
        elif variant:
            cmd.extend(["--variant", variant])

    run = runner or subprocess.run
    try:
        r = run(cmd, cwd=str(repo), capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        write_state(repo, sync_status="failed", sync_error="Sync-Zeitüberschreitung", sync_failed_at=_now_iso())
        return False, "Sync-Zeitüberschreitung."

    tail = "\n".join((r.stdout + r.stderr).strip().splitlines()[-12:])
    if r.returncode == 0:
        write_state(repo, sync_status="ok", sync_at=_now_iso(), sync_error=None)
        return True, tail
    write_state(repo, sync_status="failed", sync_error=tail, sync_failed_at=_now_iso())
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
