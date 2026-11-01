#!/usr/bin/env python3
"""
mmo_sim/core/population_backup.py — Populationsweites Backup + Restore
(ZR-POPULATION-BACKUP-RESTORE-20261101-R1, Nachzug F1-F6).

Ausloesegrenze (verifiziert an `core/runtime.py`/`core/store.py`, b8908318):
`core.runtime.SectionRuntime.run_full_section`s lokale `finalize()` ruft bei
echtem Abschnittsabschluss ZULETZT `store.finalize_section_after_reflection`
(PHASE 2: Guards pruefen, Chrononaut-Locks freigeben, `<section>__final.json`
schreiben, Tisch `status=\"closed\"`) und gibt genau dann
`SectionOutcome.completion.success == True` zurueck -- NUR in diesem Zweig
(Phase 1 ok UND Pflichtreflexionen ok). Diese Runtime kennt aber weder
`catalog_dir` noch `registry_dir` -- der volle Root-Kontext liegt erst bei den
beiden tatsaechlichen Produktionscallern vor, die `app_service.
run_play_session` aufrufen: `ui/tui.py:TuiSession._run_table_round` und
`core/lobby_flow.py:play_bound_table` (von TUI UND Lab verwendet, s. dessen
Moduldocstring). `backup_after_section_completed()` unten ist deshalb bewusst
NICHT in `runtime.py` verdrahtet, sondern in diesen beiden Callern direkt
NACH `outcome.completion.success`-Pruefung.

Idempotenz: `generation_id` wird deterministisch aus
`(run_id, table_id, section_id)` abgeleitet (NIE aus einem Zeitstempel) --
ein wiederholter Aufruf fuer denselben Abschluss (Resume, Retry, Prozess-
Neustart) sichert nie ein zweites Mal. Ein durabler Taskdatensatz unter
`backup_root/backup_tasks/<generation_id>.json` bindet, ob dieser Abschluss
bereits eine veroeffentlichte Generation hat -- ein Absturz NACH dem
Primaerabschluss, aber VOR dem Backup-Erfolg, ist damit wiederaufnehmbar.

Nachzug F1-F6 (gegenueber der R1-Erstfassung ergaenzt):
- F1: `verify_population_consistency` prueft semantisch, dass ein mehrteiliger
  Produktwrite (store.publish_current_save: current -> Version -> persona-state-
  Ref) NICHT als hashstabiler Mischstand veroeffentlicht wird.
- F2: Der Taskdatensatz bindet einen `completion_fingerprint`; ein spaeter
  nachgeholter Retry kennzeichnet maschinenlesbar, dass ein SPAETERER Stand
  aufgenommen wurde. `reconstruct_missing_backup_tasks` findet abgeschlossene
  Abschnitte ohne Taskdatensatz aus den echten Abschlussrecords wieder.
- F3: Alle erwartbaren I/O-Fehler ueber den gesamten Sicherungsweg werden in
  ein getrenntes `failed`-Ergebnis uebersetzt; der Fehlerpfad haengt NICHT
  davon ab, auf dem defekten Ziel noch schreiben zu koennen.
- F4: Der Restore besitzt sein Ziel -- privat erworbenes Staging, atomare
  Aktivierung, NIE Loeschung eines fremden Ziels.
- F5/C5: `validate_generation_for_restore` prueft Symlinks (lstat), eindeutige
  kanonische Zielpfade und benoetigte Produktreferenzen vor der Aktivierung.
- F6: Auth-/Token-/Provider-/Env-Dateien werden in allen rekursiven Rollen
  zuverlaessig ausgeschlossen und auditierbar vermerkt."""
from __future__ import annotations

import ctypes
import errno
import fnmatch
import hashlib
import json
import os
import shutil
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path

SCHEMA_VERSION = "zr-population-backup/1"

# Dateinamen/-muster, die NIE Teil einer Generation werden (transiente/OS-
# Artefakte). `lab.lock.json` traegt die PID des aktiven Lab-Prozesses
# (lab/runner.py:_lock_path) -- ein reiner OS-/Prozesslock, KEINE fachliche
# Chrononaut-/Request-Bindung (die liegt in `locks.json`/`run_id.json`/
# `completion/`, bleibt also erhalten).
_EXCLUDED_NAME_PATTERNS = ("lab.lock.json", "*.tmp", "*.tmp-*", "__pycache__", ".DS_Store")

# F6 (CODE-REVIEW C6): Bekannte Auth-/Token-/Provider-/Env-Dateien werden in
# ALLEN rekursiv gescannten Rollen zuverlaessig von der Population getrennt --
# eine `auth.json`/`.env`/`*_token.json` INNERHALB einer Datenwurzel wird nie
# gehasht, nie kopiert, nie restauriert, sondern auditierbar im Manifest unter
# `excluded` vermerkt. Rein dateinamenbasiert und case-insensitiv; der
# Dateiinhalt wird dabei NIE gelesen. Die Muster decken die gaengigen
# Provider-/Shell-/Cloud-Credential-Namen ab; echte Secrets sind NIE
# Testmaterial (nur ein klar erkennbarer Fake-Sentinel, s. Tests).
_AUTH_EXCLUDED_PATTERNS = (
    ".env", ".env.*", "*.env",
    "auth.json", "auth.*.json", "*_auth.json", "*-auth.json",
    "credentials.json", "credentials.*.json", "*_credentials.json", "*.credentials",
    "token.json", "tokens.json", "*_token.json", "*.token",
    "api_key*", "*api_key*", "apikey*", "*apikey*", "*api-key*",
    "*credentials*",
    "secret.json", "secrets.json", "*.secret", "*.secrets",
    "*.pem", "*.key", "*.p12", "*.pfx", "*.keystore", "*.keyfile",
    "id_rsa", "id_rsa.*", "id_dsa", "id_ecdsa", "id_ed25519",
    "session_auth*", "*session_auth*",
    "provider_auth*", "*provider_token*", "*access_token*", "*refresh_token*",
    "oauth*.json", "*oauth_token*",
    "service-account*.json", "*service_account*.json", "*serviceaccount*.json",
    "kubeconfig", "*kubeconfig*", ".netrc", ".npmrc", ".pgpass", ".pypirc", ".htpasswd",
)

ROLES = ("onboarding", "catalog", "run", "states", "registry", "prefs")
"""Die sechs gesicherten Rollen (s. `delivery/preflight-inventory.md`).
`prefs` wird NICHT rekursiv gescannt (s. `_PREFS_GLOBS`), alle anderen schon."""

_PREFS_GLOBS = ("ui_prefs*.json", "last_participant.json")

ROLE_TARGET_SUBDIR = {
    "onboarding": "onboarding", "catalog": "catalog", "run": "run",
    "states": "states", "registry": "registry", "prefs": "",
}
"""Zielordnername je Rolle INNERHALB eines frisch restaurierten
`target_root` -- deckungsgleich mit den CLI-Default-Unterordnernamen
(`scripts/mmo_sim.py`), damit ein restaurierter `target_root` direkt als
neues `--data-dir` verwendbar ist. `prefs` hat bewusst KEINEN eigenen
Unterordner: `onboarding_prefs.py` erwartet `ui_prefs*.json`/
`last_participant.json` DIREKT im data_root (Geschwister von `onboarding/`),
nicht in einem eigenen `prefs/`-Ordner. Die Backup-interne Staging-/
Generationsablage nutzt dagegen weiterhin den Rollennamen `prefs` als Ordner
(reine Bookkeeping-Organisation des Backups)."""

# Spiegelt `store._CURRENT_SAVE_REF_FIELD` (b8908318) -- bewusst als Konstante
# dupliziert statt `store` zu importieren (vermeidet eine Importkante von einem
# reinen Datei-/Backupmodul auf den grossen Store). Bei einer Umbenennung in
# `store` schlaegt der F1-Konsistenztest sofort an (dangling ref), kein stiller
# Drift.
_CURRENT_SAVE_REF_FIELD = "current_save_version"


class PopulationBackupError(RuntimeError):
    """Gemeinsame Basisklasse fuer alle in diesem Modul geworfenen Fehler."""


class RootOverlapError(PopulationBackupError):
    """Eine konfigurierte Rolle ueberlappt mit `backup_root` (Rekursionsschutz)
    oder mit einer anderen Rolle -- Fehlkonfiguration, kein Laufzeitfehler."""


class DriftDetectedError(PopulationBackupError):
    """Mindestens eine Quelldatei hat sich WAEHREND des Kopiervorgangs
    veraendert (Groesse/mtime_ns) -- kein populationsweit konsistenter
    Schnitt. Fuehrt zu einem kontrolliert fehlgeschlagenen Backup, NIE zu
    einer veroeffentlichten Mischgeneration."""


class RestoreRejectedError(PopulationBackupError):
    """Eine Generation/ein Ziel ist fuer den Restore nicht geeignet
    (beschaedigt, unvollstaendig, Pfadausbruch, belegtes Ziel) -- kontrollierte
    Ablehnung, kein teilaktivierbarer Bestand."""


@dataclass(frozen=True)
class PopulationRoots:
    """Die sechs tatsaechlich konfigurierten Datenwurzeln EINES Laufs. Jede
    Rolle wird vom Aufrufer explizit uebergeben (kein angenommener gemeinsamer
    Elternordner)."""

    onboarding_dir: Path
    catalog_dir: Path
    run_dir: Path
    states_dir: Path
    registry_dir: Path
    prefs_root: Path

    def as_dict(self) -> dict[str, Path]:
        return {
            "onboarding": Path(self.onboarding_dir),
            "catalog": Path(self.catalog_dir),
            "run": Path(self.run_dir),
            "states": Path(self.states_dir),
            "registry": Path(self.registry_dir),
            "prefs": Path(self.prefs_root),
        }


@dataclass(frozen=True)
class GenerationKey:
    """Stabile Abschlussidentitaet -- NIE Zeitstempel/Verzeichnisname."""

    run_id: str
    table_id: str
    section_id: str

    def as_string(self) -> str:
        return f"{self.run_id}|{self.table_id}|{self.section_id}"

    def generation_id(self) -> str:
        digest = hashlib.sha256(self.as_string().encode("utf-8")).hexdigest()
        return f"gen-{digest[:40]}"


@dataclass
class FileRecord:
    role: str
    rel_path: str
    size: int
    sha256: str


@dataclass
class BackupOutcome:
    # "created" | "already_done" | "resumed_publish" | "failed_drift"
    # | "failed_inconsistent" | "failed"
    status: str
    generation_id: str
    manifest: dict | None = None
    error: str | None = None


@dataclass
class BackupHookResult:
    """Rueckgabe des nach `section_completed` verdrahteten Hooks --
    ABSICHTLICH getrennt vom Primaer-`CompletionResult` ('Primaerabschluss und
    Zusatzbackup bekommen getrennte Ergebnisse')."""

    attempted: bool
    succeeded: bool
    generation_id: str | None = None
    error: str | None = None
    already_done: bool = False


# ── Dateisammlung ────────────────────────────────────────────────────────


def _is_excluded_name(name: str) -> bool:
    return any(fnmatch.fnmatch(name, pat) for pat in _EXCLUDED_NAME_PATTERNS)


def _is_auth_excluded_name(name: str) -> bool:
    """True fuer bekannte Auth-/Token-/Provider-/Env-Dateinamen (F6). Case-
    insensitiv; prueft NUR den Namen, liest NIE den Inhalt."""
    low = name.lower()
    return any(fnmatch.fnmatch(low, pat) for pat in _AUTH_EXCLUDED_PATTERNS)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_safe_regular_file(path: Path) -> bool:
    """True NUR fuer eine echte reguläre Datei auf Linkebene selbst.
    `os.lstat` (NIE `os.stat`/`Path.is_file()` -- beide folgen Symlinks)
    macht einen Symlink (zeigt ggf. nach aussen, z.B. auf `~/.ssh/id_rsa`
    oder `../../.env`) als `S_ISLNK`, nie `S_ISREG`, erkennbar -- UNABHAENGIG
    vom Zielinhalt, der hier NIE gelesen/dereferenziert wird. Deckt dieselbe
    Klasse auch fuer FIFO/Device/Socket-Spezialdateien ab."""
    try:
        st = os.lstat(path)
    except OSError:
        return False
    return stat.S_ISREG(st.st_mode)


def _raise_walk_error(exc: OSError) -> None:
    """F3 (CODE-REVIEW R2): `os.walk` meldet einen Traversierungsfehler (z.B.
    ein wegen Berechtigung nicht betretbares Unterverzeichnis einer rekursiven
    Rolle) normalerweise STILL und laesst den betroffenen Unterbaum einfach
    weg. Das wuerde eine hashkorrekte TEILpopulation als vollstaendig gesichert
    erscheinen lassen. Stattdessen wird der Fehler hochgereicht und von der
    aeusseren Backup-I/O-Barriere in ein kontrolliert fehlgeschlagenes Backup
    uebersetzt -- kein stiller Scanverlust."""
    raise exc


def _scan_kind_strict(path: Path) -> str:
    """'regular' fuer eine echte reguläre Datei auf Linkebene, 'skip' fuer einen
    Symlink/eine Spezialdatei (FIFO/Device/Socket -- bewusste, auditierbare
    Auslassung). WIRFT bei einem echten Zugriffs-/I/O-Fehler des `lstat`
    (Berechtigung, I/O) -- F3: eine unlesbare BENOETIGTE Datei darf NICHT
    stillschweigend als 'uebersprungene Spezialdatei' aus dem angeblich
    vollstaendigen Snapshot verschwinden. `lstat` folgt keinem Symlink, ein
    kaputter Symlink liefert also weiterhin sauber 'skip'."""
    st = os.lstat(path)  # kein try/except: Zugriffsfehler propagieren (F3)
    return "regular" if stat.S_ISREG(st.st_mode) else "skip"


def _iter_root_files(
    root: Path, *, recursive: bool, globs: tuple[str, ...] | None = None,
) -> tuple[list[Path], list[Path], list[Path]]:
    """Liefert (sichere Dateipfade, uebersprungene unsichere Pfade,
    ausgeschlossene Auth-/Secret-Pfade) unter `root`, je sortiert.
    `recursive=False` (Rolle `prefs`) durchsucht NUR die direkte Ebene nach
    `globs`. Einziger Chokepoint fuer den Populationsscan
    (`_collect_population_files_and_excluded`/`_fingerprint` rufen ausschliesslich
    diese Funktion) -- ein Symlink/eine Spezialdatei wird hier NIE geoeffnet
    oder dereferenziert, eine Auth-/Secret-Datei (F6) wird nie gelesen; beide
    werden nur uebersprungen und getrennt zurueckgemeldet. Ein echter Zugriffs-/
    Traversierungsfehler (F3) wird dagegen NICHT verschluckt, sondern als
    `OSError` hochgereicht (kein stiller Verlust eines benoetigten Unterbaums)."""
    if not root.exists():
        return [], [], []
    safe: list[Path] = []
    skipped: list[Path] = []
    auth_excluded: list[Path] = []
    if not recursive:
        candidates: set[Path] = set()
        for pat in globs or ():
            candidates.update(root.glob(pat))
        for p in candidates:
            if _is_excluded_name(p.name):
                continue
            if _is_auth_excluded_name(p.name):
                auth_excluded.append(p)
                continue
            (safe if _scan_kind_strict(p) == "regular" else skipped).append(p)
        return sorted(safe), sorted(skipped), sorted(auth_excluded)
    for dirpath, dirnames, filenames in os.walk(root, onerror=_raise_walk_error):
        dirnames[:] = [d for d in dirnames if not _is_excluded_name(d)]
        for fn in filenames:
            if _is_excluded_name(fn):
                continue
            p = Path(dirpath) / fn
            if _is_auth_excluded_name(fn):
                auth_excluded.append(p)
                continue
            (safe if _scan_kind_strict(p) == "regular" else skipped).append(p)
    return sorted(safe), sorted(skipped), sorted(auth_excluded)


def _resolved(path: Path) -> Path:
    try:
        return path.resolve()
    except OSError:
        return path.absolute()


def _assert_no_overlap(roots: PopulationRoots, backup_root: Path) -> None:
    """Fehlkonfiguration (Backup-Ziel innerhalb einer Quellwurzel oder
    umgekehrt) wird LAUT abgelehnt, statt eine rekursive Selbstsicherung
    zu riskieren. Rolle `prefs` ist NICHT rekursiv (nur ein Filename-Glob
    direkt im Ordner) -- ein Backup-Ziel UNTERHALB von `prefs_root` (z.B.
    `<data_dir>/population_backups`, der ueblichste Fall bei Default-Layout)
    wird vom Glob nicht erfasst und ist deshalb KEIN Rekursionsrisiko; nur
    Gleichheit oder ein Backup-Ziel, das `prefs_root` selbst umschliesst,
    bleibt eine Fehlkonfiguration."""
    backup_resolved = _resolved(backup_root)
    for name, raw_p in roots.as_dict().items():
        p = _resolved(raw_p)
        if name == "prefs":
            if p == backup_resolved or backup_resolved in p.parents:
                raise RootOverlapError(
                    f"backup_root {backup_resolved} ueberlappt mit Rolle 'prefs' ({p}) -- "
                    "Backup-Ziel darf 'prefs_root' nicht umschliessen/sein."
                )
            continue
        if p == backup_resolved or backup_resolved in p.parents or p in backup_resolved.parents:
            raise RootOverlapError(
                f"backup_root {backup_resolved} ueberlappt mit Rolle {name!r} ({p}) -- "
                "Backup-Ziel muss ausserhalb jeder rekursiv gescannten Populationswurzel liegen."
            )


def collect_population_files(roots: PopulationRoots) -> list[FileRecord]:
    """Vollstaendiges, deterministisch sortiertes Dateiinventar ueber ALLE
    sechs Rollen (whole_population). Jede Datei wird genau einmal gelesen
    und gehasht -- Manifest und spaeterer Kopiervorgang nutzen denselben
    Scan, kein zweites, potenziell abweichendes Re-Scan. Uebersprungene
    Symlinks/Spezialdateien/Auth-Dateien s.
    `_collect_population_files_and_excluded`."""
    records, _excluded = _collect_population_files_and_excluded(roots)
    return records


def _collect_population_files_and_excluded(
    roots: PopulationRoots,
) -> tuple[list[FileRecord], list[str]]:
    """Wie `collect_population_files`, liefert zusaetzlich die beim Scan
    uebersprungenen unsicheren Eintraege (Symlink/Spezialdatei) UND die
    ausgeschlossenen Auth-/Secret-Dateien (F6) als Klartextzeilen fuer
    `build_manifest(excluded_notes=...)` -- derselbe Scan, kein zweiter
    Re-Scan."""
    records: list[FileRecord] = []
    excluded: list[str] = []
    rootmap = roots.as_dict()
    for role, root in rootmap.items():
        recursive = role != "prefs"
        files, skipped, auth_excluded = _iter_root_files(
            root, recursive=recursive, globs=_PREFS_GLOBS if role == "prefs" else None,
        )
        for f in files:
            rel = f.relative_to(root).as_posix()
            records.append(FileRecord(role=role, rel_path=rel, size=f.stat().st_size, sha256=_sha256_file(f)))
        for sp in skipped:
            rel = sp.relative_to(root).as_posix()
            excluded.append(f"{role}/{rel} (Symlink/Spezialdatei uebersprungen)")
        for ax in auth_excluded:
            rel = ax.relative_to(root).as_posix()
            excluded.append(f"{role}/{rel} (Auth-/Secret-/Env-Datei ausgeschlossen)")
    return sorted(records, key=lambda r: (r.role, r.rel_path)), excluded


def _fingerprint(roots: PopulationRoots) -> dict[tuple[str, str], tuple[int, int]]:
    """(role, rel_path) -> (size, mtime_ns) -- Grundlage fuer die
    Driftpruefung (atomic_generation): ein Unterschied zwischen dem
    Fingerprint VOR und NACH dem Kopieren heisst, eine Quelldatei wurde
    waehrend der Aufnahme von einem anderen Schreiber veraendert. Nutzt
    denselben Chokepoint wie der Scan -- Auth-/Symlink-Dateien sind hier
    ebenfalls nicht enthalten, die Driftpruefung bleibt deckungsgleich mit
    dem gesicherten Dateiumfang."""
    out: dict[tuple[str, str], tuple[int, int]] = {}
    rootmap = roots.as_dict()
    for role, root in rootmap.items():
        recursive = role != "prefs"
        files, _skipped, _auth = _iter_root_files(
            root, recursive=recursive, globs=_PREFS_GLOBS if role == "prefs" else None,
        )
        for f in files:
            rel = f.relative_to(root).as_posix()
            st = f.stat()
            out[(role, rel)] = (st.st_size, st.st_mtime_ns)
    return out


def _content_fingerprint_sha256(files: list[FileRecord]) -> str:
    """Stabiler Inhaltsfingerprint des aufgenommenen Standes (sortiert ueber
    role/rel_path/size/sha256). Dient F2: der Taskdatensatz bindet, WELCHER
    Datenstand bei der (ersten) Aufnahme vorlag -- ein spaeter nachgeholter
    Retry kann so maschinenlesbar zeigen, ob er denselben oder einen spaeteren
    Stand gesichert hat."""
    h = hashlib.sha256()
    for f in sorted(files, key=lambda r: (r.role, r.rel_path)):
        h.update(f"{f.role}\x00{f.rel_path}\x00{f.size}\x00{f.sha256}\n".encode("utf-8"))
    return h.hexdigest()


# ── F1: Semantische Konsistenz des aufgenommenen Standes ───────────────────


def _read_json_or_none(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _run_id_of(run_dir: Path) -> str | None:
    data = _read_json_or_none(Path(run_dir) / "run_id.json")
    if data is not None:
        rid = data.get("run_id")
        if isinstance(rid, str) and rid:
            return rid
    return None


def verify_population_consistency(roots: PopulationRoots) -> list[str]:
    """F1 (CODE-REVIEW C1): semantische Konsistenzpruefung ueber die
    tatsaechlichen mehrteiligen Produktwrites. `store.publish_current_save`
    (und der Ernte-Pfad in `finalize/_resume_and_harvest`) schreibt NACHEINANDER
    die direkte current-Datei, eine neue Versionsdatei und erst dann die
    `current_save_version`-Ref im persona-state. Ein zwischen diesen Schritten
    pausierter Schreiber hinterlaesst einen hashstabilen, aber fachlich
    GEMISCHTEN Stand (Drift-/Fingerprintpruefung allein erkennt ihn nicht).

    Geprueft werden aus dem tatsaechlich konfigurierten Quellstand heraus:
      (a) jede persona-state-Ref `current_save_version={run_id,seq}` dieses
          Laufs zeigt auf eine vorhandene Versionsdatei (keine dangling ref);
      (b) es existiert KEINE Versionsdatei mit hoeherer seq als die Ref (ein
          Schreiber hat eine neue Version geschrieben, die Ref aber noch nicht
          nachgezogen -- torn/paused publish nach Schritt 2);
      (c) die direkte current-Datei stimmt mit der referenzierten Version
          ueberein (torn/paused publish zwischen Schritt 1 und Schritt 3).

    Rueckgabe: Liste konkreter Inkonsistenzen (leer = konsistent). Wirft NICHT
    -- der Aufrufer laesst das Backup kontrolliert offen/fehlgeschlagen, statt
    einen Mischstand als gute Generation zu veroeffentlichen. Legitime nicht
    veroeffentlichte Personae (kein `current_save_version`) bleiben unberuehrt."""
    problems: list[str] = []
    run_dir = Path(roots.run_dir)
    states_dir = Path(roots.states_dir)
    if not states_dir.is_dir():
        return problems
    run_id = _run_id_of(run_dir)
    current_saves = run_dir / "current_saves"
    for state_file in sorted(states_dir.glob("*.json")):
        if _is_excluded_name(state_file.name) or _is_auth_excluded_name(state_file.name):
            continue
        if not _is_safe_regular_file(state_file):
            continue
        data = _read_json_or_none(state_file)
        if data is None:
            continue
        ref = data.get(_CURRENT_SAVE_REF_FIELD)
        if not isinstance(ref, dict):
            continue
        if run_id is not None and ref.get("run_id") != run_id:
            continue  # Ref eines anderen Laufs -- fuer diesen Schnitt nicht bindend
        seq = ref.get("seq")
        if seq is None:
            continue
        try:
            seq_i = int(seq)
        except (TypeError, ValueError):
            problems.append(f"{state_file.name}: ungueltige current_save_version.seq {seq!r}")
            continue
        pk = state_file.stem
        versions_dir = current_saves / f"{pk}__versions"
        version_path = versions_dir / f"{seq_i:04d}.json"
        if not version_path.is_file():
            problems.append(
                f"{pk}: persona-state verweist auf current_save_version seq {seq_i}, aber "
                f"Versionsdatei fehlt ({version_path.name}) -- abgebrochener/pausierter "
                "publish_current_save (dangling ref)."
            )
            continue
        # (b) hoehere Version als die Ref vorhanden -> Version geschrieben, Ref
        # nicht nachgezogen.
        max_seq = seq_i
        if versions_dir.is_dir():
            for vp in versions_dir.glob("*.json"):
                if vp.stem.isdigit():
                    max_seq = max(max_seq, int(vp.stem))
        if max_seq > seq_i:
            problems.append(
                f"{pk}: Versionsdatei seq {max_seq} vorhanden, persona-state-Ref steht aber auf "
                f"seq {seq_i} -- pausierter publish_current_save (Ref nicht nachgezogen)."
            )
            continue
        # (c) direkte current-Datei weicht von referenzierter Version ab.
        direct = current_saves / f"{pk}.json"
        if direct.is_file():
            vb = _read_json_or_none(version_path)
            db = _read_json_or_none(direct)
            if vb is not None and db is not None and vb != db:
                problems.append(
                    f"{pk}: direkte current-Datei weicht von referenzierter Version seq {seq_i} ab "
                    "-- gemischter Publikationsstand (pausierter mehrteiliger Write)."
                )
    return problems


# ── Durability-Helfer ────────────────────────────────────────────────────


def _fsync_file(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    except OSError:
        pass  # manche Dateisysteme (z.B. tmpfs in CI) verweigern fsync -- best effort
    finally:
        os.close(fd)


def _fsync_dir(path: Path) -> None:
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


def _atomic_write_bytes(target: Path, data: bytes) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(f"{target.name}.tmp-{os.getpid()}")
    with tmp.open("wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, target)
    _fsync_dir(target.parent)


def _atomic_write_json(target: Path, data: dict) -> None:
    _atomic_write_bytes(target, json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))


# ── Taskdatensatz (Idempotenz + Retry-Anker) ─────────────────────────────


def _backup_tasks_dir(backup_root: Path) -> Path:
    return backup_root / "backup_tasks"


def _task_path(backup_root: Path, generation_id: str) -> Path:
    return _backup_tasks_dir(backup_root) / f"{generation_id}.json"


def _read_task(backup_root: Path, generation_id: str) -> dict | None:
    p = _task_path(backup_root, generation_id)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _write_task(backup_root: Path, generation_id: str, data: dict) -> None:
    _atomic_write_json(_task_path(backup_root, generation_id), data)


def _try_write_task(backup_root: Path, generation_id: str, data: dict) -> None:
    """F3: ein Fehlerstatus darf NICHT davon abhaengen, auf dem (moeglicherweise
    gerade defekten) Backup-Ziel noch schreiben zu koennen. Schlaegt der
    Taskwrite selbst fehl, wird das geschluckt -- der Aufrufer liefert trotzdem
    ein ehrliches `failed`-Ergebnis zurueck."""
    try:
        _write_task(backup_root, generation_id, data)
    except OSError:
        pass


# ── Manifest ──────────────────────────────────────────────────────────────


def _generations_dir(backup_root: Path) -> Path:
    return backup_root / "generations"


def _staging_dir(backup_root: Path, generation_id: str) -> Path:
    return backup_root / "staging" / f"{generation_id}.tmp-{os.getpid()}"


def build_manifest(
    *, generation_key: GenerationKey, files: list[FileRecord], roots: PopulationRoots,
    created_at_utc: str, producer_code_anchor: str, product_commit: str | None,
    prev_generation_id: str | None, excluded_notes: list[str],
    capture: dict | None = None,
) -> dict:
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generation_id": generation_key.generation_id(),
        "run_id": generation_key.run_id,
        "table_id": generation_key.table_id,
        "section_id": generation_key.section_id,
        "created_at_utc": created_at_utc,
        "producer_code_anchor": producer_code_anchor,
        "product_commit": product_commit or "unknown",
        "prev_generation_id": prev_generation_id,
        "roots": sorted(roots.as_dict().keys()),
        "excluded": list(excluded_notes),
        "files": [
            {"role": f.role, "rel_path": f.rel_path, "size": f.size, "sha256": f.sha256}
            for f in files
        ],
    }
    if capture is not None:
        # F2: maschinenlesbare Aufnahme-/Identitaetsbindung (welcher Stand wurde
        # WANN gesichert, deckt er den Abschlusszeitpunkt?).
        manifest["capture"] = capture
    return manifest


_DEFAULT_EXCLUDED_NOTES = [
    "lab.lock.json (PID-OS-Prozesslock, keine fachliche Bindung)",
    "*.tmp, *.tmp-* (transiente Zwischendateien atomarer Produktwrites)",
    "Auth-/Token-/Provider-/Env-Dateien (s. _AUTH_EXCLUDED_PATTERNS, F6) -- "
    "nie Teil der Population, nie restauriert",
    "exports_dir (nicht Teil der sechs Rollen)",
]


# ── Backup-Erzeugung (whole_population, atomic_generation, retry_idempotence) ──


def _copy_files_to_staging(staging_dir: Path, roots: PopulationRoots, files: list[FileRecord]) -> None:
    rootmap = roots.as_dict()
    for rec in files:
        src = rootmap[rec.role] / rec.rel_path
        dst = staging_dir / rec.role / rec.rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        tmp = dst.with_name(f"{dst.name}.tmp-{os.getpid()}")
        with src.open("rb") as rf, tmp.open("wb") as wf:
            shutil.copyfileobj(rf, wf)
            wf.flush()
            os.fsync(wf.fileno())
        os.replace(tmp, dst)


def _verify_staging(staging_dir: Path, manifest: dict) -> list[str]:
    problems: list[str] = []
    for entry in manifest["files"]:
        p = staging_dir / entry["role"] / entry["rel_path"]
        if not p.is_file():
            problems.append(f"fehlt im Staging: {entry['role']}/{entry['rel_path']}")
            continue
        if p.stat().st_size != entry["size"]:
            problems.append(f"Groessenabweichung: {entry['role']}/{entry['rel_path']}")
            continue
        if _sha256_file(p) != entry["sha256"]:
            problems.append(f"Hashabweichung: {entry['role']}/{entry['rel_path']}")
    return problems


def _publish_generation(backup_root: Path, staging_dir: Path, generation_id: str, manifest: dict) -> Path:
    """Atomarer Rename staging -> generations/<generation_id>.

    Existiert das Ziel bereits (Absturz NACH einem frueheren erfolgreichen
    Rename, VOR dem Taskdatensatz-'done'), wird es jetzt GEPRUEFT, bevor das
    frisch validierte Staging verworfen wird (F2b/CODE-REVIEW R2): nur wenn der
    vorhandene Zielinhalt vollstaendig+hashkorrekt zu DIESEM Manifest passt, ist
    das idempotent OK und das Staging wird verworfen. Ist das vorhandene Ziel
    beschaedigt/unvollstaendig, wird es NICHT als gute Sicherung behandelt,
    sondern durch das frisch gepruefte Staging ersetzt -- sonst wuerde Latest/
    Done auf defekte Zielbytes zeigen, waehrend die gute Kopie weggeworfen
    wird."""
    _generations_dir(backup_root).mkdir(parents=True, exist_ok=True)
    target = _generations_dir(backup_root) / generation_id
    if target.exists():
        if not _verify_staging(target, manifest):
            # Vorhandenes Ziel ist vollstaendig + hashkorrekt -> idempotenter
            # Erfolg, eigenes Staging verwerfen.
            shutil.rmtree(staging_dir, ignore_errors=True)
            return target
        # Vorhandenes Ziel ist beschaedigt/unvollstaendig -> durch das frisch
        # gepruefte Staging ersetzen (G0 anderer Generationen bleibt unberuehrt,
        # nur genau dieses defekte Ziel wird korrigiert).
        shutil.rmtree(target, ignore_errors=True)
    os.replace(staging_dir, target)
    _fsync_dir(_generations_dir(backup_root))
    return target


def _update_latest_pointer(backup_root: Path, generation_id: str) -> None:
    _atomic_write_json(backup_root / "latest.json", {"generation_id": generation_id})
    _fsync_dir(backup_root)


def read_latest(backup_root: Path) -> dict | None:
    p = Path(backup_root) / "latest.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _generation_already_valid(backup_root: Path, generation_id: str) -> dict | None:
    """Prueft, ob `generations/<generation_id>` bereits vollstaendig+hash-
    korrekt auf der Platte liegt (Resume-Fall: Generation wurde publiziert,
    aber `latest.json`/Taskdatensatz wurden davor noch nicht aktualisiert).
    Gibt das gelesene Manifest zurueck, oder `None`."""
    gen_dir = _generations_dir(backup_root) / generation_id
    manifest_path = gen_dir / "manifest.json"
    if not manifest_path.is_file():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if _verify_staging(gen_dir, manifest):
        return None
    return manifest


def generate_population_backup(
    roots: PopulationRoots, generation_key: GenerationKey, backup_root: Path,
    *, producer_code_anchor: str, created_at_utc: str, product_commit: str | None = None,
    capture_is_at_completion: bool = False,
) -> BackupOutcome:
    """Haupteinstieg (whole_population + atomic_generation + retry_idempotence
    + F1-Konsistenz + F3-I/O-Fehlertrennung). Wiederholt aufrufbar fuer
    DIESELBE `generation_key` -- jeder Zustand (noch nichts getan / Staging
    crashed / Generation publiziert aber Latest fehlt / alles fertig) wird
    korrekt fortgesetzt, nie doppelt fachlich gewirkt.

    F3: ALLE erwartbaren nativen I/O-Fehler (OSError/PermissionError) ueber
    den gesamten Sicherungsweg -- Taskwrite, Fingerprint/Scan, Staging, Kopie,
    Manifest, Publish, Latest, Done -- werden in ein ehrliches `failed`-
    Ergebnis uebersetzt, NIE als Exception an den Aufrufer (und damit an den
    Primaerabschluss-Erfolg) weitergereicht. Programmierfehler (andere
    Exceptions) bleiben sichtbar und werden NICHT als Erfolg verdeckt."""
    backup_root = Path(backup_root)
    generation_id = generation_key.generation_id()
    try:
        _assert_no_overlap(roots, backup_root)
        return _generate_population_backup_inner(
            roots, generation_key, backup_root, generation_id,
            producer_code_anchor=producer_code_anchor, created_at_utc=created_at_utc,
            product_commit=product_commit, capture_is_at_completion=capture_is_at_completion,
        )
    except RootOverlapError:
        # Fehlkonfiguration (Rekursionsschutz): bleibt eine harte, laut
        # gemeldete Ablehnung fuer den Aufrufer (kein stilles `failed`).
        raise
    except OSError as exc:
        # F3: jeder erwartbare native I/O-Fehler an einer Phase VOR der Aufnahme
        # (Overlap/Read/Konsistenz/Fingerprint/Scan) -> getrenntes `failed`. Der
        # Fehlerstatus wird best-effort geschrieben (haengt nicht vom defekten
        # Ziel ab). F2: ein bereits gebundener `completion_fingerprint` eines
        # frueheren Versuchs wird erhalten (nie durch einen spaeteren Stand
        # ersetzt). Die Aufnahmephasen selbst binden den Fingerprint lokal
        # (s. `_generate_population_backup_inner`), sodass auch ein Fehler am
        # initialen Taskwrite/Publish den Abschluss-Fingerprint nicht verliert.
        existing = _read_task(backup_root, generation_id)
        reason = f"Backup-I/O-Fehler: {exc}"
        _try_write_task(backup_root, generation_id, {
            "generation_key": generation_key.as_string(), "generation_id": generation_id,
            "status": "failed", "last_error": reason,
            "completion_fingerprint": (existing or {}).get("completion_fingerprint"),
        })
        return BackupOutcome(status="failed", generation_id=generation_id, error=reason)


def _staged_roots(staging_dir: Path) -> PopulationRoots:
    """PopulationRoots, die auf die TATSAECHLICH kopierten Bytes im Staging
    zeigen (F1a): die Rollen liegen dort unter ihrem Rollennamen als
    Unterordner (`_copy_files_to_staging`)."""
    staging_dir = Path(staging_dir)
    return PopulationRoots(
        onboarding_dir=staging_dir / "onboarding", catalog_dir=staging_dir / "catalog",
        run_dir=staging_dir / "run", states_dir=staging_dir / "states",
        registry_dir=staging_dir / "registry", prefs_root=staging_dir / "prefs",
    )


def _generate_population_backup_inner(
    roots: PopulationRoots, generation_key: GenerationKey, backup_root: Path,
    generation_id: str, *, producer_code_anchor: str, created_at_utc: str,
    product_commit: str | None, capture_is_at_completion: bool = False,
) -> BackupOutcome:
    task = _read_task(backup_root, generation_id)
    if task is not None and task.get("status") == "done":
        # F2b: 'done' allein bescheinigt KEINEN Erfolg -- die veroeffentlichte
        # Generation muss tatsaechlich noch vollstaendig+hashkorrekt vorliegen.
        # Fehlt sie oder ist sie beschaedigt, ist die Sicherung nicht gut; nicht
        # faelschlich `already_done` melden, sondern frisch neu aufnehmen (die
        # neue gepruefte Kopie ersetzt dann das defekte Ziel in `_publish_generation`).
        if _generation_already_valid(backup_root, generation_id) is not None:
            return BackupOutcome(status="already_done", generation_id=generation_id, manifest=task.get("manifest"))

    already = _generation_already_valid(backup_root, generation_id)
    if already is not None:
        # PHASE-2-Resume: Generation liegt bereits vollstaendig+korrekt vor,
        # nur Latest-Zeiger/Taskdatensatz fehlen noch -- KEIN erneutes
        # Kopieren, NUR der fehlende Rest wird nachgezogen.
        _update_latest_pointer(backup_root, generation_id)
        _write_task(backup_root, generation_id, {
            "generation_key": generation_key.as_string(), "generation_id": generation_id,
            "status": "done", "manifest": already,
            "completion_fingerprint": (task or {}).get("completion_fingerprint"),
        })
        return BackupOutcome(status="resumed_publish", generation_id=generation_id, manifest=already)

    # F1: semantische Konsistenz der lebenden Quellen VOR der Aufnahme (fruehe
    # Ablehnung schon sichtbarer Mischstaende). Die massgebliche Pruefung an den
    # tatsaechlich kopierten Bytes folgt zusaetzlich nach dem Staging (F1a).
    inconsistencies = verify_population_consistency(roots)
    if inconsistencies:
        reason = "Populationsstand nicht konsistent (kein veroeffentlichbarer Schnitt): " + "; ".join(
            inconsistencies
        )
        _try_write_task(backup_root, generation_id, {
            "generation_key": generation_key.as_string(), "generation_id": generation_id,
            "status": "failed", "last_error": reason,
            "completion_fingerprint": (task or {}).get("completion_fingerprint"),
        })
        return BackupOutcome(status="failed_inconsistent", generation_id=generation_id, error=reason)

    pre_fingerprint = _fingerprint(roots)
    files, dynamic_excluded_notes = _collect_population_files_and_excluded(roots)
    content_fp = _content_fingerprint_sha256(files)

    # F2a: ehrliche Abschlussbindung. Nur ein TATSAECHLICH dauerhaft gebundener
    # Abschlussfingerprint (prior_fp) ODER eine SYNCHRON beim Abschluss erfolgte
    # Aufnahme (capture_is_at_completion) begruendet eine Gleichheitsaussage. Eine
    # nachgeholte Aufnahme ohne solche Bindung (rekonstruierter Task; erster
    # Taskwrite nie persistiert) laesst den historischen Bezug ausdruecklich
    # UNBEKANNT -- niemals ein aus dem neuen Inhalt selbst berechnetes `true`.
    prior_fp = (task or {}).get("completion_fingerprint")
    if prior_fp:
        completion_fp: str | None = prior_fp
        matches: bool | None = (content_fp == prior_fp)
        completion_known = True
    elif capture_is_at_completion:
        completion_fp = content_fp
        matches = True
        completion_known = True
    else:
        completion_fp = None
        matches = None
        completion_known = False

    def _task_fields(status: str, **extra: object) -> dict:
        base = {
            "generation_key": generation_key.as_string(), "generation_id": generation_id,
            "status": status, "completion_fingerprint": completion_fp,
            "completion_fingerprint_known": completion_known,
        }
        base.update(extra)
        return base

    def _fail(status: str, reason: str, staging: Path | None) -> BackupOutcome:
        if staging is not None:
            shutil.rmtree(staging, ignore_errors=True)
        _try_write_task(backup_root, generation_id, _task_fields("failed", last_error=reason))
        return BackupOutcome(status=status, generation_id=generation_id, error=reason)

    staging_dir: Path | None = None
    try:
        _write_task(backup_root, generation_id, _task_fields("pending"))

        prev = read_latest(backup_root)
        prev_generation_id = prev.get("generation_id") if prev else None

        capture = {
            "capture_fingerprint_sha256": content_fp,
            "completion_fingerprint_sha256": completion_fp,
            "completion_binding_known": completion_known,
            "captured_state_matches_section_completion": matches,
            "captured_at_utc": created_at_utc,
        }
        if not completion_known:
            capture["note"] = (
                "Historischer Abschlussbezug UNBEKANNT: nachgeholte Aufnahme ohne dauerhaft "
                "gebundenen Abschlussfingerprint -- keine Gleichheitszusage zum Abschlussstand."
            )
        elif matches is False:
            capture["note"] = (
                "SPAETER nachgeholte Aufnahme: der gesicherte Stand weicht vom gebundenen Stand "
                "bei Abschnittsabschluss ab (ehrliche Kennzeichnung, kein Umetikettieren)."
            )
        manifest = build_manifest(
            generation_key=generation_key, files=files, roots=roots, created_at_utc=created_at_utc,
            producer_code_anchor=producer_code_anchor, product_commit=product_commit,
            prev_generation_id=prev_generation_id,
            excluded_notes=_DEFAULT_EXCLUDED_NOTES + dynamic_excluded_notes,
            capture=capture,
        )

        staging_dir = _staging_dir(backup_root, generation_id)
        staging_dir.mkdir(parents=True, exist_ok=True)
        try:
            _copy_files_to_staging(staging_dir, roots, files)
        except OSError as exc:
            return _fail("failed", f"Schreibfehler waehrend der Aufnahme: {exc}", staging_dir)

        post_fingerprint = _fingerprint(roots)
        if pre_fingerprint != post_fingerprint:
            return _fail(
                "failed_drift",
                "Konkurrierender Schreibzugriff waehrend der Aufnahme erkannt (Fingerprint-Drift) -- "
                "kontrolliert fehlgeschlagenes Backup, kein veroeffentlichter Mischstand.",
                staging_dir,
            )

        # F1a: Konsistenz an den TATSAECHLICH kopierten Bytes pruefen -- faengt
        # den Mischstand eines Mehrdateiwriters, der ERST NACH der Vorpruefung
        # pausierte und so in genau diese Kopie geriet. Kein `created` fuer einen
        # inkonsistenten Schnitt.
        staged_problems = verify_population_consistency(_staged_roots(staging_dir))
        if staged_problems:
            return _fail(
                "failed_inconsistent",
                "Aufgenommene Bytes nicht konsistent (kein veroeffentlichbarer Schnitt): "
                + "; ".join(staged_problems),
                staging_dir,
            )

        manifest_bytes = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")
        (staging_dir / "manifest.json").write_bytes(manifest_bytes)
        _fsync_file(staging_dir / "manifest.json")

        problems = _verify_staging(staging_dir, manifest)
        if problems:
            return _fail("failed", "Selbstpruefung im Staging fehlgeschlagen: " + "; ".join(problems), staging_dir)

        _publish_generation(backup_root, staging_dir, generation_id, manifest)
        _update_latest_pointer(backup_root, generation_id)
        _write_task(backup_root, generation_id, _task_fields("done", manifest=manifest))
        return BackupOutcome(status="created", generation_id=generation_id, manifest=manifest)
    except OSError as exc:
        return _fail("failed", f"Backup-I/O-Fehler waehrend der Aufnahme: {exc}", staging_dir)


def retry_population_backup(
    roots: PopulationRoots, generation_key: GenerationKey, backup_root: Path,
    *, producer_code_anchor: str, created_at_utc: str, product_commit: str | None = None,
) -> BackupOutcome:
    """Wiederholungsweg fuer eine fehlende/fehlgeschlagene Sicherung. Nimmt
    bewusst KEIN GM-/Persona-/Harvest-Argument entgegen -- allein die Signatur
    macht einen neuen Spielzug/eine neue Reflexion/eine neue Ernte hier
    unmoeglich, nur Pfade+Identitaet. Technisch identisch zu
    `generate_population_backup` (dieselbe Idempotenz-, Konsistenz- und
    Fehlerbehandlung), eigener Name fuer die Bedienoberflaeche/den Testbeweis
    der Trennung. Der im Taskdatensatz gebundene `completion_fingerprint`
    sorgt dafuer, dass ein spaeter aufgenommener Stand ehrlich als solcher im
    Manifest erscheint (F2)."""
    return generate_population_backup(
        roots, generation_key, backup_root, producer_code_anchor=producer_code_anchor,
        created_at_utc=created_at_utc, product_commit=product_commit,
    )


def _table_status(run_dir: Path, table_id: str) -> str | None:
    """Liest `run_dir/tables/<table_id>.json["status"]` direkt (kein store-Import,
    vermeidet eine Importkante). `None`, wenn Datei/Feld fehlt oder unlesbar."""
    if not isinstance(table_id, str) or not table_id or "/" in table_id or "\\" in table_id \
            or table_id in (".", "..") or "\x00" in table_id:
        return None
    data = _read_json_or_none(Path(run_dir) / "tables" / f"{table_id}.json")
    if data is None:
        return None
    status = data.get("status")
    return status if isinstance(status, str) else None


def _safe_component(value: str) -> str:
    """Spiegelt `store._safe_component` (b8908318): nur `/` -> `_`. Fuer die
    Finalmarker-Dateinamen `completion/<section>__final.json`."""
    return str(value).replace("/", "_")


def section_completion_consistent(run_dir: Path, table_id: str, section_id: str) -> bool:
    """F1b (CODE-REVIEW R2): ein echter konsistenter Abschnittsabschluss liegt
    NUR vor, wenn SOWOHL der Finalmarker `completion/<section>__final.json`
    existiert ALS AUCH der zugehoerige Tisch tatsaechlich `status="closed"`
    persistiert ist. Der unveraenderte Abschlusswriter schreibt den Finalmarker
    VOR dem persistierten Tischstatus (`store.finalize_section_after_reflection`,
    STORE 1844-1851); ein Absturz dazwischen hinterlaesst einen Finalmarker ohne
    konsistenten Abschluss. Eine Rekonstruktion/ein Backup darf daraus KEINE gute
    Generation ableiten. Unbeteiligte offene Tische bleiben davon unberuehrt."""
    run_dir = Path(run_dir)
    final_path = run_dir / "completion" / f"{_safe_component(section_id)}__final.json"
    if not final_path.is_file():
        return False
    final = _read_json_or_none(final_path)
    if final is None or final.get("table_id") != table_id:
        return False
    return _table_status(run_dir, table_id) == "closed"


def reconstruct_missing_backup_tasks(roots: PopulationRoots, backup_root: Path) -> list[str]:
    """F2 (CODE-REVIEW C2, zweite Luecke): findet abgeschlossene Abschnitte, fuer
    die KEIN Backup-Taskdatensatz existiert, aus den echten Abschlussrecords
    (`run_dir/completion/<section>__final.json`) wieder und legt dafuer je einen
    `pending`-Task an -- damit ist ein Prozessabbruch ZWISCHEN erfolgreicher
    Primaerfinalisierung und dem ersten Backup-Taskwrite wiederaufnehmbar
    (`backup retry` findet den rekonstruierten Auftrag). KEINE GM-/Reflexions-/
    Ernte-/Fortschrittswiederholung -- es wird ausschliesslich ein ruhender
    Auftrag aus bereits persistierten Abschlussfakten abgeleitet. Ein Abschnitt
    mit bereits `done`-Task oder bereits gueltiger Generation wird NICHT
    angefasst (keine Doppel-Ernte, kein falscher `already_done`).

    Rueckgabe: Liste der neu rekonstruierten generation_ids (leer = nichts
    nachzuholen). Best-effort gegenueber I/O-Fehlern am Backup-Ziel (F3)."""
    backup_root = Path(backup_root)
    run_dir = Path(roots.run_dir)
    completion_dir = run_dir / "completion"
    if not completion_dir.is_dir():
        return []
    run_id = _run_id_of(run_dir)
    if not run_id:
        return []
    reconstructed: list[str] = []
    for final_path in sorted(completion_dir.glob("*__final.json")):
        data = _read_json_or_none(final_path)
        if data is None:
            continue
        section_id = data.get("section_id")
        table_id = data.get("table_id")
        if not isinstance(section_id, str) or not isinstance(table_id, str):
            continue
        # F1b: nur rekonstruieren, wenn der Abschluss tatsaechlich konsistent ist
        # (Finalmarker UND persistierter Tischstatus `closed`). Ein Absturz nach
        # dem Finalmarker, aber vor dem Tischabschluss, ist KEIN fertiger Abschnitt.
        if _table_status(run_dir, table_id) != "closed":
            continue
        key = GenerationKey(run_id=run_id, table_id=table_id, section_id=section_id)
        generation_id = key.generation_id()
        task = _read_task(backup_root, generation_id)
        if task is not None:
            continue  # bereits bekannt (pending/failed/done)
        if _generation_already_valid(backup_root, generation_id) is not None:
            continue  # Generation liegt schon gueltig vor
        try:
            _write_task(backup_root, generation_id, {
                "generation_key": key.as_string(), "generation_id": generation_id,
                "status": "pending", "reconstructed_from_completion_record": True,
            })
        except OSError:
            continue
        reconstructed.append(generation_id)
    return reconstructed


def read_backup_status(backup_root: Path, roots: PopulationRoots | None = None) -> dict:
    """Fuer eine 'backup status'-Bedienoberflaeche: letzte gute Generation +
    alle Taskdatensaetze, die NICHT 'done' sind (= retrybar). Wird `roots`
    uebergeben, werden zuerst fehlende Auftraege aus den Abschlussrecords
    rekonstruiert (F2), damit auch ein Abbruch vor dem ersten Taskwrite als
    offener Auftrag sichtbar/retrybar wird."""
    backup_root = Path(backup_root)
    if roots is not None:
        reconstruct_missing_backup_tasks(roots, backup_root)
    latest = read_latest(backup_root)
    pending_or_failed = []
    tasks_dir = _backup_tasks_dir(backup_root)
    if tasks_dir.is_dir():
        for p in sorted(tasks_dir.glob("*.json")):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if data.get("status") != "done":
                pending_or_failed.append(data)
    return {"latest_generation_id": latest.get("generation_id") if latest else None, "open_tasks": pending_or_failed}


# ── Hook nach section_completed ──────────────────────────────────────────


def backup_after_section_completed(
    *, completion_success: bool, run_id: str, table_id: str, section_id: str,
    roots: PopulationRoots, backup_root: Path, producer_code_anchor: str,
    created_at_utc: str, product_commit: str | None = None,
) -> BackupHookResult | None:
    """Von den Produktioncallern (`ui/tui.py:_run_table_round`,
    `core/lobby_flow.py:play_bound_table`) DIREKT NACH der Pruefung von
    `outcome.completion.success` aufgerufen. `None`, wenn der Abschnitt NICHT
    final abgeschlossen wurde -- kein Backup-Versuch fuer einen bloss
    erfolgreichen Spielzug, einen tolerierten Resume-Zwischenstand ohne
    Phase 2 oder einen abgelehnten Save (closure_boundary). Fehler HIER werden
    NIE an den Primaerabschluss-Erfolg gebunden.

    F3: Der Hook faengt NEBEN `PopulationBackupError` auch jeden erwartbaren
    nativen `OSError` ab (`generate_population_backup` uebersetzt diese
    bereits intern in `failed`, dies ist der zusaetzliche Sicherungsgurt an der
    Caller-Grenze) -- der direkte TUI-/Lobby-Pfad liegt NACH dem vorigen
    Produkt-try/except und darf unter keinen Umstaenden mit einer Backup-
    Exception verlassen werden."""
    if not completion_success:
        return None
    # F1b: echte Abschlussgrenze -- der ausloesende Abschnitt muss tatsaechlich
    # konsistent abgeschlossen sein (Finalmarker UND persistierter Tischstatus
    # `closed`). Im regulaeren Live-Pfad trifft `completion_success` erst zu,
    # NACHDEM `finalize_section_after_reflection` beides geschrieben hat -- der
    # Check ist dann erfuellt. Faellt er (z.B. Abbruch zwischen Finalmarker und
    # Tischabschluss, Hook dennoch aufgerufen), wird KEIN Backup fuer einen
    # unfertigen Abschluss erzeugt.
    try:
        if not section_completion_consistent(roots.run_dir, table_id, section_id):
            return None
    except OSError as exc:
        return BackupHookResult(attempted=True, succeeded=False, error=str(exc))
    key = GenerationKey(run_id=run_id, table_id=table_id, section_id=section_id)
    try:
        outcome = generate_population_backup(
            roots, key, Path(backup_root), producer_code_anchor=producer_code_anchor,
            created_at_utc=created_at_utc, product_commit=product_commit,
            capture_is_at_completion=True,
        )
    except (PopulationBackupError, OSError) as exc:
        return BackupHookResult(attempted=True, succeeded=False, error=str(exc))
    if outcome.status in ("created", "resumed_publish"):
        return BackupHookResult(attempted=True, succeeded=True, generation_id=outcome.generation_id)
    if outcome.status == "already_done":
        return BackupHookResult(
            attempted=True, succeeded=True, generation_id=outcome.generation_id, already_done=True,
        )
    return BackupHookResult(attempted=True, succeeded=False, generation_id=outcome.generation_id, error=outcome.error)


# ── Restore ───────────────────────────────────────────────────────────────


def _rel_path_is_safe(rel_path: str) -> bool:
    if not rel_path or rel_path.startswith("/") or rel_path.startswith("\\"):
        return False
    parts = Path(rel_path).parts
    if any(part in ("..", "") for part in parts):
        return False
    if Path(rel_path).is_absolute():
        return False
    return True


def _canonical_target_key(role: str, rel_path: str) -> str:
    """Normalisierter Ziel-Pfad einer Manifestzeile im restaurierten
    `target_root` (F5/C5: eindeutige Zielpfade). `prefs` hat KEINEN eigenen
    Unterordner (ROLE_TARGET_SUBDIR['prefs'] == '') -- eine `prefs`-Zeile mit
    `rel_path='run/...'` wuerde deshalb exakt dieselbe Zieldatei wie die Rolle
    `run` bezeichnen. Der Schluessel ist der POSIX-Zielpfad relativ zu
    `target_root`, damit genau solche rollenuebergreifenden Kollisionen
    erkennbar werden."""
    subdir = ROLE_TARGET_SUBDIR[role]
    return (Path(subdir) / rel_path).as_posix() if subdir else Path(rel_path).as_posix()


def validate_generation_for_restore(backup_root: Path, generation_id: str | None = None) -> dict:
    """Prueft Formatversion, Vollmanifest, Hashes, Pfadsicherheit, Dateitypen,
    eindeutige Zielpfade und benoetigte Produktreferenzen VOR jeder Aktivierung.
    Wirft `RestoreRejectedError` mit konkretem Grund, statt einen Teilbestand
    zu akzeptieren."""
    backup_root = Path(backup_root)
    if generation_id is None:
        latest = read_latest(backup_root)
        if latest is None or not latest.get("generation_id"):
            raise RestoreRejectedError("kein latest.json / keine Generation-ID vorhanden.")
        generation_id = latest["generation_id"]

    # Pfadsicherheit fuer den Identifier selbst: `generation_id` fliesst gleich in
    # einen Pfad-Join. Ein bedienbarer Aufrufer (TUI `_cmd_restore`) nimmt ihn als
    # Tastatur-Token entgegen -- ein Wert wie "../../etc" wuerde `gen_dir` aus
    # `generations/` herausschieben (Read-Pfadausbruch). Nur eine einzelne, sichere
    # Pfadkomponente zulassen; echte IDs sind "gen-<hex>" (GenerationKey).
    if (not generation_id or "/" in generation_id or "\\" in generation_id
            or "\x00" in generation_id or os.path.isabs(generation_id)
            or generation_id in (".", "..")):
        raise RestoreRejectedError(
            f"Generation {generation_id!r}: unsichere Generation-ID (Pfadausbruchsversuch)."
        )

    gen_dir = _generations_dir(backup_root) / generation_id
    manifest_path = gen_dir / "manifest.json"
    if not manifest_path.is_file():
        raise RestoreRejectedError(f"Generation {generation_id!r}: manifest.json fehlt.")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RestoreRejectedError(f"Generation {generation_id!r}: Manifest unlesbar/beschaedigt ({exc}).") from exc

    # Das Manifest-Feld `generation_id` ist Dateiinhalt (potenziell manipuliert)
    # und wird von `restore_population` fuer den Kopier-Pfad wiederverwendet. Es
    # MUSS mit dem bereits geguardeten Generationsordner uebereinstimmen, aus dem
    # dieses Manifest soeben gelesen wurde -- sonst koennte ein veraenderter Wert
    # (z.B. "../../anderswo") den Pfad-Guard oben umgehen und den Kopiervorgang
    # aus einem Verzeichnis ausserhalb von `generations/` lesen lassen.
    if manifest.get("generation_id") != generation_id:
        raise RestoreRejectedError(
            f"Generation {generation_id!r}: Manifest-Feld generation_id "
            f"{manifest.get('generation_id')!r} stimmt nicht mit dem Generationsordner "
            "ueberein (moeglicher Pfadausbruch ueber Manifest-Inhalt)."
        )

    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise RestoreRejectedError(
            f"Generation {generation_id!r}: unbekannte/nicht unterstuetzte schema_version "
            f"{manifest.get('schema_version')!r} (erwartet {SCHEMA_VERSION!r})."
        )

    entries = manifest.get("files")
    if not isinstance(entries, list):
        raise RestoreRejectedError(f"Generation {generation_id!r}: Manifest hat kein 'files'-Array.")
    # F4 (CODE-REVIEW R2): ein formal passendes, aber LEERES Manifest darf keinen
    # leeren Bestand aktivieren. Eine reale Population ist nie leer; eine einzelne
    # legitim leere OPTIONALE Rolle bleibt dagegen zulaessig (sie hat schlicht
    # keine Zeilen, waehrend andere Rollen Daten tragen).
    if not entries:
        raise RestoreRejectedError(
            f"Generation {generation_id!r}: leeres Manifest (files=[]) -- eine leere Population ist "
            "kein gueltiger Restore-Bestand."
        )

    manifest_keys: set[tuple[str, str]] = set()
    target_keys: dict[str, tuple[str, str]] = {}
    for entry in entries:
        role = entry.get("role")
        rel_path = entry.get("rel_path")
        if role not in ROLES:
            raise RestoreRejectedError(f"Generation {generation_id!r}: unbekannte Rolle {role!r} im Manifest.")
        if not isinstance(rel_path, str) or not _rel_path_is_safe(rel_path):
            raise RestoreRejectedError(
                f"Generation {generation_id!r}: unsicherer rel_path {rel_path!r} (Pfadausbruchsversuch)."
            )
        if (role, rel_path) in manifest_keys:
            raise RestoreRejectedError(
                f"Generation {generation_id!r}: doppelte Manifestzeile {role}/{rel_path}."
            )
        # F5/C5: eindeutige kanonische ZIELpfade (auch rollenuebergreifend) --
        # verhindert, dass `prefs` mit `rel_path='run/...'` dieselbe Zieldatei
        # wie die Rolle `run` ueberschreibt.
        tkey = _canonical_target_key(role, rel_path)
        if tkey in target_keys:
            other = target_keys[tkey]
            raise RestoreRejectedError(
                f"Generation {generation_id!r}: kollidierender Restore-Zielpfad {tkey!r} "
                f"({role}/{rel_path} vs. {other[0]}/{other[1]}) -- kein eindeutiger Zielbaum."
            )
        target_keys[tkey] = (role, rel_path)

        p = gen_dir / role / rel_path
        # F4 (CODE-REVIEW R2): NICHT nur das Blatt, auch jeder VORFAHRE im
        # Generationsbaum muss ein echtes Verzeichnis sein -- ein Symlink-Vorfahr
        # (z.B. `states` als Link nach aussen) wuerde sonst beim Kopieren
        # dereferenziert. `lstat` folgt keinem Link.
        ancestor = gen_dir
        for part in (Path(role) / rel_path).parts[:-1]:
            ancestor = ancestor / part
            try:
                if stat.S_ISLNK(os.lstat(ancestor).st_mode):
                    raise RestoreRejectedError(
                        f"Generation {generation_id!r}: Symlink-Vorfahre {part!r} im Pfad "
                        f"{role}/{rel_path} — abgelehnt (kein Pfadausbruch ueber Verzeichnislink)."
                    )
            except FileNotFoundError:
                break  # fehlender Vorfahr -> die Blattpruefung unten meldet 'Datei fehlt'
        # F5/C5: Symlink/Spezialdatei in der Generation (`is_file()` wuerde
        # Symlinks folgen) -- `_is_safe_regular_file` nutzt lstat.
        if not _is_safe_regular_file(p):
            if not p.exists() and not p.is_symlink():
                raise RestoreRejectedError(f"Generation {generation_id!r}: Datei fehlt — {role}/{rel_path}.")
            raise RestoreRejectedError(
                f"Generation {generation_id!r}: unsichere Datei (Symlink/Spezialdatei) — {role}/{rel_path}."
            )
        if p.stat().st_size != entry.get("size"):
            raise RestoreRejectedError(f"Generation {generation_id!r}: Groessenabweichung — {role}/{rel_path}.")
        if _sha256_file(p) != entry.get("sha256"):
            raise RestoreRejectedError(f"Generation {generation_id!r}: Hashabweichung — {role}/{rel_path}.")
        manifest_keys.add((role, rel_path))

    on_disk_keys: set[tuple[str, str]] = set()
    for role in ROLES:
        role_dir = gen_dir / role
        if not role_dir.is_dir():
            continue
        for dirpath, _dirnames, filenames in os.walk(role_dir):
            for fn in filenames:
                full = Path(dirpath) / fn
                on_disk_keys.add((role, full.relative_to(role_dir).as_posix()))
    extra = on_disk_keys - manifest_keys
    if extra:
        raise RestoreRejectedError(
            f"Generation {generation_id!r}: {len(extra)} Datei(en) auf der Platte sind im Manifest "
            f"nicht verzeichnet (unvollstaendiges/inkonsistentes Manifest), z.B. {sorted(extra)[0]}."
        )

    # F5/C5: benoetigte Produktreferenzen -- eine persona-state-Ref
    # `current_save_version={run_id,seq}` setzt voraus, dass die referenzierte
    # Versionsdatei (`run/current_saves/<pk>__versions/<seq>.json`) ebenfalls
    # gesichert ist. Fehlt sie, waere der restaurierte Bestand zwar formal
    # hashkorrekt, aber fachlich unvollstaendig (der current-Save liesse sich
    # nicht laden). Ein formal passendes, aber lueckenhaftes Manifest scheitert.
    _require_referenced_payload(generation_id, gen_dir, manifest_keys)

    return manifest


def _require_referenced_payload(
    generation_id: str, gen_dir: Path, manifest_keys: set[tuple[str, str]],
) -> None:
    """F5/C5: prueft, dass von den gesicherten persona-states referenzierte
    Pflichtdaten (current-Save-Versionsdateien) tatsaechlich im Manifest
    enthalten sind. Liest NUR aus der validierten Generation (`gen_dir`),
    nie aus einer Produktionswurzel."""
    for role, rel_path in sorted(manifest_keys):
        if role != "states" or not rel_path.endswith(".json"):
            continue
        data = _read_json_or_none(gen_dir / "states" / rel_path)
        if data is None:
            continue
        ref = data.get(_CURRENT_SAVE_REF_FIELD)
        if not isinstance(ref, dict):
            continue
        seq = ref.get("seq")
        if seq is None:
            continue
        try:
            seq_i = int(seq)
        except (TypeError, ValueError):
            raise RestoreRejectedError(
                f"Generation {generation_id!r}: persona-state {rel_path} hat ungueltige "
                f"current_save_version.seq {seq!r}."
            )
        pk = Path(rel_path).stem
        needed = ("run", f"current_saves/{pk}__versions/{seq_i:04d}.json")
        if needed not in manifest_keys:
            raise RestoreRejectedError(
                f"Generation {generation_id!r}: benoetigte Referenz fehlt -- persona-state {pk} "
                f"verweist auf current_save_version seq {seq_i}, aber {needed[1]} ist nicht "
                "gesichert (unvollstaendige Generation)."
            )
        # F4 (CODE-REVIEW R2): die direkte current-Datei gehoert ebenfalls zum
        # tragenden Produktbezug (publish_current_save/Ernte schreiben sie). Fehlt
        # sie, ist der restaurierte current-Save fachlich unvollstaendig.
        direct_needed = ("run", f"current_saves/{pk}.json")
        if direct_needed not in manifest_keys:
            raise RestoreRejectedError(
                f"Generation {generation_id!r}: benoetigte Referenz fehlt -- persona-state {pk} "
                f"verweist auf einen current-Save, aber {direct_needed[1]} ist nicht gesichert "
                "(unvollstaendige Generation)."
            )


_RENAME_NOREPLACE = 1  # linux/glibc RENAME_NOREPLACE
_AT_FDCWD = -100


def _activate_no_replace(staging: Path, target: Path) -> None:
    """F4 (CODE-REVIEW R2): aktiviert `staging` als `target` mit ECHTER atomarer
    Nichtueberschreibungssemantik. `os.rename` ersetzt unter POSIX ein bereits
    bestehendes LEERES Zielverzeichnis -- ein zwischen Vorpruefung und Aktivierung
    fremd angelegtes (auch leeres) Ziel darf aber NIE angetastet werden. Daher
    `renameat2(RENAME_NOREPLACE)`: schlaegt fehl, sobald `target` in irgendeiner
    Form existiert (leer oder nicht). Bei EEXIST -> kontrollierte Ablehnung, das
    fremde Ziel bleibt unberuehrt.

    Fallback (Kernel/Dateisystem ohne RENAME_NOREPLACE, ENOSYS/EINVAL): exklusiver
    Namenserwerb via `os.mkdir(target)` (atomar, scheitert wenn `target` existiert),
    dann Verschieben der Staginginhalte -- ebenfalls ohne je ein fremdes Ziel zu
    ueberschreiben."""
    try:
        libc = ctypes.CDLL(None, use_errno=True)
        renameat2 = libc.renameat2
        renameat2.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        res = renameat2(_AT_FDCWD, os.fsencode(str(staging)), _AT_FDCWD, os.fsencode(str(target)), _RENAME_NOREPLACE)
        if res == 0:
            return
        err = ctypes.get_errno()
        if err == errno.EEXIST:
            raise RestoreRejectedError(
                f"Zielordner {target} existiert bereits (atomar erkannt) -- fremder Bestand bleibt "
                "unangetastet, kein Ueberschreiben."
            )
        if err not in (errno.ENOSYS, errno.EINVAL):
            raise OSError(err, os.strerror(err))
    except AttributeError:
        pass  # renameat2 im libc-Symbolsatz nicht vorhanden -> Fallback
    # Fallback: exklusiver Namenserwerb, dann Inhalte verschieben.
    try:
        os.mkdir(target, 0o700)
    except FileExistsError as exc:
        raise RestoreRejectedError(
            f"Zielordner {target} existiert bereits -- fremder Bestand bleibt unangetastet "
            "(exklusiver Erwerb fehlgeschlagen)."
        ) from exc
    for child in sorted(os.listdir(staging)):
        os.replace(staging / child, target / child)
    os.rmdir(staging)


@dataclass
class RestoreOutcome:
    target_root: Path
    roots: PopulationRoots
    generation_id: str
    manifest: dict


def restore_population(backup_root: Path, target_root: Path, generation_id: str | None = None) -> RestoreOutcome:
    """Restauriert eine validierte Generation in einen NEU angelegten, privaten
    `target_root`.

    F4 (CODE-REVIEW C4): Der Restore besitzt sein Ziel. Er baut den vollstaendigen
    Bestand zunaechst in einem AUSSCHLIESSLICH selbst atomar erworbenen, privaten
    Staging-Verzeichnis (0o700) neben dem Ziel auf, validiert jede Kopie und
    aktiviert erst dann atomar per `os.rename`. In JEDEM Fehlerfall wird NUR das
    eigene Staging entfernt -- ein zwischenzeitlich anderweitig angelegtes,
    nichtleeres Zielverzeichnis bleibt bytegleich unangetastet (`os.rename`
    schlaegt darauf kontrolliert fehl). Ein abgebrochener Restore hinterlaesst
    keinen teilaktivierbaren Produktroot (das Ziel entsteht erst mit dem
    atomaren Rename, nicht waehrend des Kopierens)."""
    backup_root = Path(backup_root)
    target_root = Path(target_root)

    # Validierung zuerst (rein lesend auf `backup_root`), bevor irgendetwas am
    # Ziel/Elternordner geschieht.
    manifest = validate_generation_for_restore(backup_root, generation_id)
    gid = manifest["generation_id"]
    gen_dir = _generations_dir(backup_root) / gid

    # Fruehe, klare Ablehnung eines bereits bestehenden Ziels (kein stilles
    # Overwrite/Merge). Die eigentliche Zielgewinnung bleibt zusaetzlich atomar
    # ueber os.rename abgesichert (Race zwischen dieser Pruefung und Aktivierung).
    if target_root.exists():
        raise RestoreRejectedError(
            f"Zielordner {target_root} existiert bereits -- Restore verlangt einen neu angelegten "
            "Ordner, kein stilles Ueberschreiben eines bestehenden Bestands."
        )

    parent = target_root.parent
    parent.mkdir(parents=True, exist_ok=True)
    # Privat erworbenes Staging NEBEN dem Ziel (gleiches Dateisystem -> atomarer
    # Rename). `mkdtemp` legt mit 0o700 an und gehoert exklusiv diesem Prozess.
    staging = Path(tempfile.mkdtemp(prefix=f".restore-{gid}-", dir=parent))
    try:
        os.chmod(staging, 0o700)
        for entry in manifest["files"]:
            role, rel_path = entry["role"], entry["rel_path"]
            src = gen_dir / role / rel_path
            dst = staging / ROLE_TARGET_SUBDIR[role] / rel_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            tmp = dst.with_name(f"{dst.name}.tmp-{os.getpid()}")
            with src.open("rb") as rf, tmp.open("wb") as wf:
                shutil.copyfileobj(rf, wf)
                wf.flush()
                os.fsync(wf.fileno())
            os.replace(tmp, dst)
            if _sha256_file(dst) != entry["sha256"]:
                raise RestoreRejectedError(f"Restore-Kopie weicht vom Manifest ab: {role}/{rel_path}.")
        _fsync_dir(staging)
        # F4: Atomare Aktivierung mit echter Nichtueberschreibung -- auch ein
        # zwischenzeitlich fremd angelegtes LEERES Ziel wird nicht ersetzt
        # (`_activate_no_replace` nutzt renameat2 RENAME_NOREPLACE). Wir entfernen
        # in jedem Fehlerfall NUR unser eigenes Staging, NIE das (fremde) Ziel.
        _activate_no_replace(staging, target_root)
    except BaseException:
        # NUR das selbst erworbene Staging bereinigen -- niemals `target_root`.
        shutil.rmtree(staging, ignore_errors=True)
        raise
    _fsync_dir(parent)

    roots = PopulationRoots(
        onboarding_dir=target_root / "onboarding", catalog_dir=target_root / "catalog",
        run_dir=target_root / "run", states_dir=target_root / "states",
        registry_dir=target_root / "registry", prefs_root=target_root,
    )
    return RestoreOutcome(target_root=target_root, roots=roots, generation_id=gid, manifest=manifest)
