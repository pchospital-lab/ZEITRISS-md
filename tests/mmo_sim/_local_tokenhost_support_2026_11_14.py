#!/usr/bin/env python3
"""tests/mmo_sim/_local_tokenhost_support_2026_11_14.py -- gemeinsamer
Offline-Testhelfer (SCOPE.json: "kontrollierte neue Testprozesse; kein
Produktmodul").

N4-N2 (API-CONTRACT-N4N2.md): dieser Support ist stdlib-only und
importiert BEIM MODULIMPORT KEIN Produktmodul (`local_model_profile`/
`setup`/`launcher`) -- diese werden ausschliesslich LAZY innerhalb der
`_cmd_*`-Kommandofunktionen importiert (`_product_modules()`), NACH dem
Fruehschutz.

KRITISCHER UNTERSCHIED ZU N4-N1: dieses Modul installiert BEIM IMPORT
KEINEN Guard mehr (das war der N1-Platzhalterdefekt). Es gibt GENAU EINEN
Weg, einen Primaerguard zu installieren: `bootstrap_isolation(context=
{...})` mit einem vollstaendigen, wertfreien Kontext-Dict (siehe
`EarlyIsolationGuard.from_context`/`_validate_context` unten). Ein
Primaerguard liegt prozessweit am `sys`-Modul
(`_GUARD_SINGLETON_ATTR` = "_n4n2_isolation_guard_singleton"): die ERSTE
erfolgreiche Primaerinstallation gewinnt, jeder weitere Aufruf (egal ob
mit `context=` oder den alten Legacy-Parametern `private_home=/
private_root=/real_home=/repo_root=/allowed_children=`) liefert
AUSSCHLIESSLICH dieselbe bereits installierte Instanz zurueck -- ohne sie
neu zu konfigurieren. Ein Legacy-Aufruf OHNE existierenden Primaerguard
(ungeschuetzter Erstaufruf ausserhalb von Mains `bootstrap_entry.py`)
wirft sichtbar `IsolationBootstrapError` (kein stiller Platzhalterguard,
kein fall-open-Autoload).

Zwei Zwecke:

1. Fruehschutz (`EarlyIsolationGuard`/`bootstrap_isolation`): MUSS von
   jedem Konsumenten (Testdatei ODER Kindprozess unten) importiert/
   aufgerufen werden, BEVOR irgendein Produktmodul geladen wird. Ein
   `sys.addaudithook` laesst sich NICHT entfernen -- einmal installiert,
   bleibt er fuer den Rest des Prozesses aktiv. Der Guard setzt tatsaechlich
   durch (nicht nur als Statusfeld): Lesen/Metadaten nur in benannten
   Quell-/Dependency-/privaten Bereichen, Schreiben/Erzeugen/Umbenennen/
   Loeschen nur in privaten Bereichen, echte Credentialpfade (lexikalisch
   bestimmt) immer gesperrt, echtes Netz gesperrt, Subprozesse nur ueber
   eine verbrauchbare, exakte Rolle+argv+Fixture+Export+Anzahl-Erlaubnis.
   Metadaten (`os.stat`/`os.lstat`/`os.path.exists`/`os.path.isfile`/
   `Path.stat`/`Path.exists`/`Path.is_file`) haben KEIN Audit-Event und
   werden deshalb explizit gewrapt (Klassifikation VOR dem echten Aufruf).

2. I4-Nachweis "zwei frische Kinder, beide persistierten Zustaende" --
   genau zwei eigenstaendige `python3`-Kindprozesse (vorab exakt per
   Argv registriert, Teil des bounded-Runner-Buendels), jeweils mit
   eigenem `--context <private_json>` fuer eine eigene Primaerinstallation
   in ihrem eigenen frischen Interpreter plus eigenem before/after-Export:

     write-matrix <env_path_a> <env_path_b> <fixture_path> [--context <p>]
         EIN Schreiberkind, ECHTER Writer (`local_model_profile.
         build_local_profile_updates` + `setup._update_env_file_
         preserving`, dieselben Produktfunktionen wie `launcher.py`/
         `action_rekeys`) erzeugt ZWEI private Profile: A (echter
         Erfolg) und B (derselbe Writer, aber mit einem SYNTHETISCHEN
         Fehler NUR am verpflichtenden Readback-IO-Seam
         `setup._read_env_file` -- liefert tatsaechlich `False` UND
         belegt den Pending-Marker). Liest Token/URL/Modell/Limits aus
         einer privaten synthetischen JSON-Fixturedatei (`fixture_path`)
         -- NIEMALS aus argv.

     read-matrix <env_path_a> <env_path_b> <fixture_path> [--context <p>]
         EIN Leserkind, startet als VOELLIG NEUER Interpreter (kein
         geteilter Modul-/Prozessstatus mit `write-matrix`), liest BEIDE
         Pfade mit den ECHTEN `setup.resolve_model_provider`/
         `launcher.resolve_model_provider_choice`-Resolvern und vergleicht
         INTERN alle sieben Felder (provider, base_url, model, api_key,
         owui_base_url, gm_max_tokens, persona_max_tokens) gegen die
         Fixture -- druckt NUR boolesche Feldergebnisse auf stdout, NIE
         die Werte selbst.

Keine echten Secrets, keine echte Nutzerdatei (alle Pfade sind private
Tempdateien der Aufrufer). Kein echtes Netz/Docker."""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"


# ─── Dedizierte Ausnahmen (API-CONTRACT-N4N2.md §1) ─────────────────────
# N4-N3 Fix (01_GENERALREVIEW.md §5 "Unterschiedliche Exceptionklassen
# durch Modulaliase"): diese Datei wird in mehreren Testdateien per
# `importlib.util.spec_from_file_location` unter JEWEILS ANDEREM
# Modulnamen (`o1_local_tokenhost_support`/`o2_local_tokenhost_support`/
# ...) im selben Prozess neu ausgefuehrt -- ohne Ankerbindung wuerde jede
# Ausfuehrung EIGENE, nicht identische Klassenobjekte erzeugen, und ein
# `except IsolationViolation` eines "Alias"-Moduls wuerde eine in einem
# ANDEREN Alias geworfene Instanz nicht fangen. Die ERSTE Ausfuehrung in
# diesem Prozess gewinnt und bindet die kanonischen Klassen an den
# vorhandenen Prozessanker (`sys`, denselben wie `_GUARD_SINGLETON_ATTR`
# unten); jede weitere Ausfuehrung uebernimmt dieselben Klassenobjekte.
_EXCEPTION_ANCHOR_ATTR = "_n4n2_isolation_exception_classes"
_existing_exception_classes = getattr(sys, _EXCEPTION_ANCHOR_ATTR, None)

if _existing_exception_classes is not None:
    IsolationBootstrapError = _existing_exception_classes["IsolationBootstrapError"]
    IsolationViolation = _existing_exception_classes["IsolationViolation"]
else:
    class IsolationBootstrapError(RuntimeError):
        """bootstrap_isolation konnte keinen Primaerguard installieren/
        abrufen (fehlender/ungueltiger Kontext, leeres Exportziel, oder
        ungeschuetzter Legacy-Erstaufruf ohne existierenden Primaerguard).
        Sichtbares Scheitern -- KEIN stiller Platzhalterguard."""

    class IsolationViolation(Exception):
        """Ein kontrollierter IO-/Metadaten-/Netz-/Kindprozessversuch hat die
        durchgesetzte Grenze verletzt. NIE FileNotFoundError, NIE ein stiller
        False-Fallback -- dedizierte Ausnahme, positive private IO ist davon
        unberuehrt."""

    setattr(sys, _EXCEPTION_ANCHOR_ATTR, {
        "IsolationBootstrapError": IsolationBootstrapError,
        "IsolationViolation": IsolationViolation,
    })


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _support_hash() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def _hash_context_dict(d: dict) -> str:
    """N4-N3 Fix (01_GENERALREVIEW.md §3 "Der Kontexthash ist ... auf den
    beiden Seiten verschieden definiert"): identische kanonische
    Serialisierung wie Mains `bootstrap_entry.py`/`run_bundle.py`
    (sort_keys, kompakte Separatoren, kein ASCII-Escaping) -- derselbe
    `guard_context` muss auf beiden Seiten denselben Hash ergeben."""
    return hashlib.sha256(
        json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _implicit_interpreter_roots() -> set:
    """Die laufende Interpreterinstallation (stdlib/site-packages) muss
    IMMER lesbar bleiben -- sonst zerstoert die durchgesetzte Lesegrenze
    den eigenen Testlauf (jeder spaetere `import xyz` loest ein echtes
    `open`-Audit-Event auf eine .py/.pyc-Datei unterhalb des Python-
    Installationspfads aus). Dies ist eine feste, nicht konfigurierbare
    Basisfreigabe fuer "die Python-Installation selbst", UNABHAENGIG von
    den im Kontext benannten Quell-/Dependencybereichen (die zusaetzliche,
    vom Aufrufer benannte Bereiche abdecken, z.B. ausserhalb des venv
    liegender Drittcode). Rein lexikalisch (sys.prefix/site.*-Attribute),
    keine Festplattenzugriffe."""
    roots = {
        sys.prefix, sys.exec_prefix,
        getattr(sys, "base_prefix", sys.prefix),
        getattr(sys, "base_exec_prefix", sys.exec_prefix),
    }
    try:
        import site
        roots.update(site.getsitepackages())
    except Exception:
        pass
    try:
        import site
        roots.add(site.getusersitepackages())
    except Exception:
        pass
    return {r for r in roots if r}


def _ancestor_chain(path: str) -> list:
    """Alle Vorfahrenverzeichnisse von `path` bis zur Dateisystemwurzel,
    rein lexikalisch (os.path.dirname-Kette, KEINE Festplattenzugriffe).
    N4-N3-Fix (01_GENERALREVIEW.md §5 "Path.resolve benoetigt Metadaten
    der Vorfahren"): `Path.resolve`/`realpath` ruft intern `lstat` auf
    JEDEM Vorfahren eines aufgeloesten Pfads auf, nicht nur auf dem Pfad
    selbst -- ohne diese Liste blockiert der Metadaten-Wrapper bereits
    den allerersten Resolve-Aufruf auf einen eigenen benannten Bereich."""
    out = []
    cur = os.path.normpath(path)
    while True:
        parent = os.path.dirname(cur)
        if not parent or parent == cur:
            break
        out.append(parent)
        cur = parent
    return out


# ─── Fruehschutz -- VOR jedem Produktimport verfuegbar ─────────────────

class EarlyIsolationGuard:
    """Installiert einen `sys.addaudithook`, der fuer den Rest des
    Prozesses aktiv bleibt (kann nicht entfernt/durch ein Testmonkeypatch
    unbemerkt deaktiviert werden -- `sys.addaudithook` ist in CPython
    absichtlich nicht entfernbar), UND patcht beim Primaerinstall zusaetzlich
    die Metadaten-APIs (`os.stat`/`os.lstat`/`os.path.exists`/
    `os.path.isfile`/`Path.stat`/`Path.exists`/`Path.is_file`) global --
    diese haben KEIN verlaessliches Audit-Event.

    Direkt konstruierbar (z.B. fuer eine Selbstprobe mit einer eigenen
    synthetischen `real_home_class`) ODER ueber die prozessweite,
    idempotente Fabrik `bootstrap_isolation(...)` unten. NUR eine ueber
    `bootstrap_isolation` (`primary=True`) installierte Instanz patcht
    `Path.home`/`Path.expanduser`/`os.path.expanduser`/Metadaten-APIs
    GLOBAL und sperrt Netz/Subprozess."""

    _CREDENTIAL_HOME_RELATIVE = (".openwebui_env",)
    _CREDENTIAL_REPO_RELATIVE = (os.path.join("scripts", "litellm", ".env"),)

    _MUTATE_WRITE_EVENTS = frozenset({
        "os.rename", "os.remove", "os.unlink", "os.mkdir", "os.rmdir",
        "shutil.copyfile", "shutil.copymode", "shutil.copystat", "shutil.copy",
        "shutil.copy2", "shutil.copytree", "shutil.move", "shutil.rmtree",
    })
    _LIST_READ_EVENTS = frozenset({"os.scandir", "os.listdir"})

    def __init__(self, *, bundle_id="selfprobe", process_id="selfprobe",
                 role="selfprobe", real_home_class, repo_root=None,
                 source_read_roots=(), dep_read_roots=(),
                 private_write_roots=(), shared_fixture_root=None,
                 export_before_path=None, export_after_path=None,
                 credential_block_roots=(), artifact_read_paths=()):
        self.bundle_id = str(bundle_id)
        self.process_id = str(process_id)
        self.role = str(role)
        self.real_home_class = str(real_home_class)
        self.repo_root = str(repo_root) if repo_root else None
        self.source_read_roots = [str(p) for p in (source_read_roots or ())]
        self.dep_read_roots = [str(p) for p in (dep_read_roots or ())]
        self.private_write_roots = [str(p) for p in (private_write_roots or ())]
        self.shared_fixture_root = str(shared_fixture_root) if shared_fixture_root else None
        self.export_before_path = str(export_before_path) if export_before_path else None
        self.export_after_path = str(export_after_path) if export_after_path else None
        # N4-N3 (INTERFACE-CONTRACT.json guard_context, 13. Schluessel):
        # read-only, NIEMALS sys.path -- exakte benannte Kontext-/Kind-
        # phasen-/Vertragsdateien, die der Elternprozess lesen darf, ohne
        # dafuer einen ganzen Verzeichnisbereich freizugeben.
        self.artifact_read_paths = [str(p) for p in (artifact_read_paths or ())]
        # I1.2: "private home" (Path.home/expanduser-Ziel) ist der erste
        # benannte private Schreibbereich -- es gibt dafuer keinen eigenen
        # Kontextschluessel mehr (anders als die alte Legacy-API).
        self.private_home = self.private_write_roots[0] if self.private_write_roots else tempfile.gettempdir()

        self._credential_block_roots_init = [str(p) for p in (credential_block_roots or ())]
        self._credential_classes = self._build_credential_classes()
        self._self_probe_blocked_paths: set = set()

        self._implicit_read_roots = _implicit_interpreter_roots()
        named_read = [self.repo_root] + self.source_read_roots + self.dep_read_roots + \
            self.private_write_roots + ([self.shared_fixture_root] if self.shared_fixture_root else [])
        self._read_roots = self._implicit_read_roots | {r for r in named_read if r}
        named_write = self.private_write_roots + ([self.shared_fixture_root] if self.shared_fixture_root else [])
        self._write_roots = {r for r in named_write if r}

        # N4-N3 Fix P1/rc96 (01_GENERALREVIEW.md §5 "Exportpfade gespeichert,
        # nicht freigegeben"): die zwei gebundenen Exportpfade sind IMMER
        # innerhalb der eigenen privaten Wurzel schreibbar -- EXAKTE
        # Dateifreigabe (nicht der ganze Ordner), damit `before`/`after`
        # tatsaechlich geschrieben werden koennen, ohne die Schreibgrenze
        # auf den gesamten privaten Bereich auszudehnen (der ist es
        # bereits ueber private_write_roots; dieses Set sichert zusaetzlich
        # den Fall ab, dass ein Exportpfad bewusst AUSSERHALB eines
        # benannten Wurzelordners liegt).
        self._export_write_exact = {
            os.path.normcase(os.path.normpath(p))
            for p in (self.export_before_path, self.export_after_path) if p
        }

        # N4-N3 Fix P5 (01_GENERALREVIEW.md §5 "Path.resolve benoetigt
        # Metadaten der Vorfahren"): exakte Vorfahrenverzeichnisse aller
        # benannten Lesewurzeln -- NUR Metadatentraversal (lstat/stat/
        # exists/is_file), NIE Verzeichnislisten/-inhalt/-schreiben.
        self._metadata_ancestor_paths: set = set()
        for _root in named_read:
            if _root:
                self._metadata_ancestor_paths.update(_ancestor_chain(_root))
        for _root in self._implicit_read_roots:
            self._metadata_ancestor_paths.update(_ancestor_chain(_root))

        # N4-N3 Fix P2 (artifact_read_paths): read-only, exakte Dateien,
        # NIEMALS Praefixe/Verzeichnisse, NIEMALS sys.path.
        self._artifact_read_exact = {
            os.path.normcase(os.path.normpath(p)) for p in self.artifact_read_paths
        }

        # N4-N3 Fix P4 (private os.open->os.fdopen/io.open(fd)-Kette,
        # private Popen-PIPE-Deskriptoren): nur FDs, die eine gewrapte
        # private Operation DIESES Prozesses selbst erzeugt hat, gelten als
        # "besessen" -- schliessen loescht die Herkunft, keine pauschale
        # Integerfreigabe.
        self._owned_fds: set = set()
        self._trusted_dirfd_open_depth: int = 0

        self._expected_counts: dict = {}
        self._unexpected_blocked = 0
        self._unexpected_counts_by_operation: dict = {}
        self._underlying_io_calls: dict = {}
        self.install_order: list = []
        self._self_probe = False
        self._primary = False

        self._child_grants: dict = {}
        self._child_authorizations: list = []
        self._child_consumption: list = []
        self._child_starts: list = []
        self._child_ends: list = []

        self._context_hash = _hash_context_dict(self._context_dict())

    @classmethod
    def from_context(cls, context: dict) -> "EarlyIsolationGuard":
        return cls(**context)

    def _context_dict(self) -> dict:
        return {
            "bundle_id": self.bundle_id, "process_id": self.process_id, "role": self.role,
            "real_home_class": self.real_home_class, "repo_root": self.repo_root,
            "source_read_roots": list(self.source_read_roots),
            "dep_read_roots": list(self.dep_read_roots),
            "private_write_roots": list(self.private_write_roots),
            "shared_fixture_root": self.shared_fixture_root,
            "export_before_path": self.export_before_path,
            "export_after_path": self.export_after_path,
            "credential_block_roots": list(self._credential_block_roots_init),
            "artifact_read_paths": list(self.artifact_read_paths),
        }

    # ── Lexikalische Pfadklassenbestimmung (KEIN exists/stat/open) ─────
    def _build_credential_classes(self) -> set:
        classes: set = set()

        def _add(base: str, rel: str) -> None:
            if not base:
                return
            p = os.path.join(base, rel)
            classes.add(p)
            classes.add(os.path.normpath(p))
            classes.add(os.path.normcase(os.path.abspath(p)))

        for rel in self._CREDENTIAL_HOME_RELATIVE:
            _add(self.real_home_class, rel)
        if self.repo_root:
            for rel in self._CREDENTIAL_REPO_RELATIVE:
                _add(self.repo_root, rel)
        env_home = os.environ.get("HOME")
        if env_home and env_home != self.real_home_class:
            for rel in self._CREDENTIAL_HOME_RELATIVE:
                _add(env_home, rel)
        for extra in self._credential_block_roots_init:
            classes.add(extra)
            classes.add(os.path.normpath(extra))
            classes.add(os.path.normcase(os.path.abspath(extra)))
        return classes

    def _alias_candidates(self, s: str) -> frozenset:
        candidates = {s, os.path.normpath(s), os.path.normcase(os.path.abspath(s))}
        tilde_rest = None
        if s == "~":
            tilde_rest = ""
        elif s.startswith("~/") or s.startswith("~" + os.sep):
            tilde_rest = s[2:]
        if tilde_rest is not None:
            expanded = os.path.join(self.real_home_class, tilde_rest) if tilde_rest else self.real_home_class
            candidates.add(expanded)
            candidates.add(os.path.normcase(os.path.abspath(expanded)))
        if s.startswith("$HOME"):
            expanded = self.real_home_class + s[len("$HOME"):]
            candidates.add(expanded)
            candidates.add(os.path.normcase(os.path.abspath(expanded)))
        return frozenset(candidates)

    def _classify(self, raw):
        """Liefert die Aliaskandidaten-Menge fuer `raw`, oder `None` wenn
        der Pfad NICHT sicher lexikalisch abbildbar ist (fd-Zahl, nicht
        dekodierbare Bytes) -- `None` wird vom Aufrufer IMMER als
        Ablehnung behandelt (Symlink-/Verzeichnis-fd-Tricks)."""
        if isinstance(raw, bool):
            return None
        if isinstance(raw, int):
            return None
        try:
            s = os.fspath(raw)
        except TypeError:
            return None
        if isinstance(s, bytes):
            try:
                s = s.decode("utf-8", "surrogateescape")
            except Exception:
                return None
        return self._alias_candidates(s)

    def _matches_blocked(self, candidates) -> bool:
        if candidates & self._credential_classes:
            return True
        if candidates & self._self_probe_blocked_paths:
            return True
        return False

    @staticmethod
    def _in_roots(candidates, roots) -> bool:
        norm_roots = [os.path.normcase(os.path.normpath(r)) for r in roots if r]
        for c in candidates:
            nc = os.path.normcase(os.path.normpath(c))
            for r in norm_roots:
                if nc == r or nc.startswith(r + os.sep):
                    return True
        return False

    def _in_read_roots(self, candidates) -> bool:
        return self._in_roots(candidates, self._read_roots)

    def _in_write_roots(self, candidates) -> bool:
        return self._in_roots(candidates, self._write_roots)

    @staticmethod
    def _in_exact(candidates, exact_norm_set) -> bool:
        """EXAKTE Dateiuebereinstimmung (kein Praefix/Verzeichnis) -- fuer
        die zwei gebundenen Exportpfade (P1) und `artifact_read_paths`
        (P2): beide duerfen NIE zu einer Ordnerfreigabe werden."""
        for c in candidates:
            if os.path.normcase(os.path.normpath(c)) in exact_norm_set:
                return True
        return False

    def _in_export_write_exact(self, candidates) -> bool:
        return self._in_exact(candidates, self._export_write_exact)

    def _in_artifact_read_exact(self, candidates) -> bool:
        return self._in_exact(candidates, self._artifact_read_exact)

    def _in_metadata_ancestors(self, candidates) -> bool:
        """Integration fix: pytest's own rootdir-/package-root-discovery
        probes individual NAMED marker files (`__init__.py`, `pytest.ini`,
        `pyproject.toml`, ...) directly INSIDE an ancestor directory, not
        just the ancestor directory itself (e.g. `Path(ancestor,
        '__init__.py').is_file()`). The exact-ancestor-directory match
        alone rejected these well-behaved, content-blind existence probes.
        Still METADATA-only (no `os.listdir`/`os.scandir` -- a separate,
        unaffected audit event) and still requires the parent directory to
        be an actual named ancestor; this does not grant directory
        listing, content reads, or writes of /home or any other ancestor."""
        norm_ancestors = {os.path.normcase(os.path.normpath(a)) for a in self._metadata_ancestor_paths}
        for c in candidates:
            nc = os.path.normcase(os.path.normpath(c))
            if nc in norm_ancestors:
                return True
            if os.path.dirname(nc) in norm_ancestors:
                return True
        return False

    # ── Selbstprobensteuerung ───────────────────────────────────────────
    def begin_self_probe(self) -> None:
        self._self_probe = True

    def end_self_probe(self) -> None:
        self._self_probe = False

    def register_self_probe_block(self, path) -> None:
        """Fuegt EINEN zusaetzlichen, rein synthetischen Sperrpfad hinzu
        (fuer Selbstproben-Negativziele INNERHALB privater Testfixtures --
        NIE echte Credentials). Wirkt wie die echten Credentialklassen,
        also mit Vorrang vor jeder Positivfreigabe."""
        cls = self._alias_candidates(os.fspath(path))
        self._self_probe_blocked_paths |= cls

    def clear_self_probe_blocks(self) -> None:
        self._self_probe_blocked_paths = set()

    def _record_block(self, op: str) -> None:
        # Keine nachtraegliche Umklassifikation: der zum Zeitpunkt des
        # Blocks aktive `_self_probe`-Zustand entscheidet endgueltig.
        if self._self_probe:
            self._expected_counts[op] = self._expected_counts.get(op, 0) + 1
        else:
            self._unexpected_blocked += 1
            self._unexpected_counts_by_operation[op] = self._unexpected_counts_by_operation.get(op, 0) + 1

    # ── Kinderberechtigung (verbrauchbar: Rolle+argv+env+cwd+Fixture+Export) ─
    def register_child(self, role, argv, fixture_paths, export_id, count=1, *,
                        context_path=None, context_sha256=None, minimal_env=None,
                        cwd=None, private_root=None) -> None:
        """N4-N3 Fix (01_GENERALREVIEW.md §5 "Kinderberechtigung
        ueberschreibbar; env/cwd nicht verbindlich gebunden"): die
        gemeinsame reine `child_grant_decision` lehnt jede Aenderung der
        Bindung (env/cwd/argv/Fixture/Kontext) fuer denselben argv-
        Schluessel ab UND verweigert die Wiederbelebung eines bereits
        VERBRAUCHTEN Grants -- eine erneute Registrierung mit demselben
        argv kann einen erschoepften Grant nicht mehr erneuern."""
        decision, reason = child_grant_decision(
            self._child_grants, role, argv, fixture_paths, context_path,
            context_sha256, minimal_env, cwd, private_root, export_id,
        )
        if decision != "GRANT":
            self._record_block("register_child")
            raise IsolationViolation(f"N4-N2-Guard: Kinderregistrierung abgelehnt ({reason}): {role!r}")
        key = tuple(str(a) for a in argv)
        if key not in self._child_grants:
            self._child_grants[key] = {
                "role": str(role), "fixture_paths": [str(p) for p in fixture_paths],
                "export_id": str(export_id), "remaining": int(count), "consumed": False,
                "binding": _child_binding(role, argv, fixture_paths, context_path,
                                           context_sha256, minimal_env, cwd, private_root, export_id),
            }
        self._child_authorizations.append({
            "role": str(role), "argv": list(key),
            "fixture_paths": [str(p) for p in fixture_paths],
            "export_id": str(export_id), "count": int(count),
        })

    def authorize_and_consume(self, argv, *, cwd=None, env=None) -> None:
        """Beim `subprocess.Popen`-Audit (UND synthetisch direkt aus einer
        Selbstprobe aufrufbar, OHNE einen dritten Interpreter zu starten):
        exaktes argv-Match UND Restzahl>0 UND (falls bei der Registrierung
        gebunden) passendes env/cwd -> verbrauchen; sonst
        `IsolationViolation`. KEINE klassenweite wiederverwendbare Menge.
        Ein auf 0 verbrauchter Grant wird `consumed` markiert (s.
        `child_grant_decision`/`register_child`: eine spaetere erneute
        Registrierung desselben argv kann ihn NICHT erneuern)."""
        key = tuple(str(a) for a in argv)
        grant = self._child_grants.get(key)
        if grant is None or grant["remaining"] <= 0:
            self._record_block("subprocess_popen")
            raise IsolationViolation(f"Kindprozess nicht autorisiert oder bereits verbraucht: {key!r}")
        binding = grant.get("binding") or {}
        bound_cwd = binding.get("cwd")
        bound_env = dict(binding.get("minimal_env") or ())
        if bound_cwd is not None and cwd is not None and str(cwd) != bound_cwd:
            self._record_block("subprocess_popen")
            raise IsolationViolation(f"N4-N2-Guard: Kindprozess-cwd abweichend von Registrierung: {cwd!r}")
        if bound_env and env is not None and dict(env) != bound_env:
            self._record_block("subprocess_popen")
            raise IsolationViolation("N4-N2-Guard: Kindprozess-env abweichend von Registrierung.")
        grant["remaining"] -= 1
        if grant["remaining"] <= 0:
            grant["consumed"] = True
        self._child_consumption.append({
            "argv": list(key), "role": grant["role"], "export_id": grant["export_id"],
            "remaining_after": grant["remaining"], "utc": _utcnow_iso(),
        })

    def record_child_start(self, *, role, pid, ppid, argv, utc=None) -> None:
        self._child_starts.append({
            "role": str(role), "pid": int(pid), "ppid": int(ppid),
            "argv": [str(a) for a in argv], "utc": utc or _utcnow_iso(),
        })

    def record_child_end(self, *, role, pid, rc, utc=None) -> None:
        self._child_ends.append({
            "role": str(role), "pid": int(pid), "rc": int(rc),
            "utc": utc or _utcnow_iso(),
        })

    # ── open()/Mutation/Listing/Netz/Subprozess ueber sys.addaudithook ──
    def _is_write_mode(self, mode, flags) -> bool:
        if mode:
            m = str(mode)
            return any(ch in m for ch in ("w", "a", "x", "+"))
        if flags is not None:
            try:
                f = int(flags)
            except (TypeError, ValueError):
                return True
            write_bits = (
                getattr(os, "O_WRONLY", 1) | getattr(os, "O_RDWR", 2) |
                getattr(os, "O_CREAT", 0) | getattr(os, "O_APPEND", 0) |
                getattr(os, "O_TRUNC", 0)
            )
            return bool(f & write_bits)
        return False

    #: Integration fix (pytest's own output-capture plugin opens os.devnull
    #: unconditionally, e.g. _pytest/capture.py FDCapture -- a real but
    #: fully inert kernel null device, never real user/credential data.
    #: Allowed unconditionally for both read and write; this is NOT a
    #: root/export-exact grant and does not widen any named root.
    _ALWAYS_ALLOWED_EXACT = frozenset({os.path.normcase(os.path.normpath(os.devnull))})

    def _handle_open(self, args) -> None:
        padded = tuple(args) + (None, None, None)
        path, mode, flags = padded[0], padded[1], padded[2]
        # N4-N3 Fix P4 (01_GENERALREVIEW.md §5 "Private os.open->os.fdopen-
        # Kette blockiert"): ein fd-basierter open (os.fdopen/io.open(fd),
        # auch INTERN durch subprocess beim Aufbau einer PIPE) ist NUR
        # erlaubt, wenn DIESER Prozess den fd selbst ueber eine gewrapte
        # private Operation (os.open/os.pipe) erzeugt hat. Schliessen
        # loescht die Herkunft -- keine pauschale Integerfreigabe.
        if isinstance(path, int) and not isinstance(path, bool):
            if path in self._owned_fds:
                return
            self._record_block("open")
            raise IsolationViolation(f"N4-N2-Guard: nicht autorisierter Datei-Descriptor fuer open: {path!r}")
        if self._trusted_dirfd_open_depth > 0:
            # see _install_fd_provenance_wrappers: dir_fd is invisible to
            # this audit event; the wrapper already verified it against an
            # owned fd before entering the real call.
            return
        cls = self._classify(path)
        if cls is None:
            self._record_block("open")
            raise IsolationViolation(f"N4-N2-Guard: nicht sicher klassifizierbarer Pfad fuer open: {path!r}")
        if self._in_exact(cls, self._ALWAYS_ALLOWED_EXACT):
            return
        if self._matches_blocked(cls):
            self._record_block("open")
            raise IsolationViolation(f"N4-N2-Guard: gesperrter Pfad fuer open: {path!r}")
        write_intent = self._is_write_mode(mode, flags)
        if write_intent:
            # N4-N3 Fix P1/rc96: EXAKTE Dateifreigabe fuer die zwei
            # gebundenen Exportpfade (nicht der ganze Ordner).
            allowed = self._in_write_roots(cls) or self._in_export_write_exact(cls)
        else:
            # N4-N3 Fix P2: EXAKTE Dateifreigabe fuer artifact_read_paths
            # (nie ein Verzeichnis-/Praefixgrant).
            allowed = self._in_read_roots(cls) or self._in_artifact_read_exact(cls)
        if not allowed:
            self._record_block("open")
            kind = "write" if write_intent else "read"
            raise IsolationViolation(f"N4-N2-Guard: open ({kind}) ausserhalb erlaubter Wurzeln: {path!r}")

    _MUTATE_ARG_LAYOUT = {
        "os.remove": (1, 1), "os.unlink": (1, 1), "os.rmdir": (1, 1),
        "os.mkdir": (1, 1), "os.rename": (2, 2), "shutil.rmtree": (1, 1),
    }

    #: Integration fix: shutil's copy family audits `(src, dst)` -- `src`
    #: is READ (e.g. a real product file inside a named source root being
    #: staged into a private fake-repo fixture, a common test pattern),
    #: only `dst` is a MUTATION needing write-root membership. The generic
    #: `_MUTATE_ARG_LAYOUT` default (all path args need write-root) wrongly
    #: rejected every such copy with a legitimate read-only source.
    _MUTATE_SRC_DST_EVENTS = {
        "shutil.copyfile": (1, 1), "shutil.copymode": (1, 1),
        "shutil.copystat": (1, 1), "shutil.copytree": (1, 1),
    }

    # N4-N3 Fix P3 (01_GENERALREVIEW.md §5 "Normale CPython-dirfd-Defaults
    # werden als fremder Descriptor gesperrt"): CPython uebergibt im Audit-
    # Event fuer os.mkdir/os.remove/os.rename/... den dir_fd-Wert IMMER
    # (nicht `None`) -- der Standardwert fuer "kein explizites dir_fd" ist
    # `-1` (DIR_FD_CONVERTER), nicht `None`. Vorher wurde JEDER gewoehnliche
    # Aufruf ohne dir_fd (also praktisch jeder Aufruf) als "fremder
    # Deskriptor" fehlklassifiziert und blockiert. Nur ein echter,
    # tatsaechlich uebergebener (nicht-negativer) dir_fd ist der strenge,
    # abzulehnende Fall.
    _NO_EXPLICIT_DIR_FD = (None, -1)

    def _handle_mutate(self, event: str, args) -> None:
        if event in self._MUTATE_SRC_DST_EVENTS:
            n_src, n_dst = self._MUTATE_SRC_DST_EVENTS[event]
            src_args, dst_args = args[:n_src], args[n_src:n_src + n_dst]
            for p in src_args:
                if p is None:
                    continue
                cls = self._classify(p)
                if cls is None or self._matches_blocked(cls) or not self._in_read_roots(cls):
                    self._record_block(event)
                    raise IsolationViolation(f"N4-N2-Guard: gesperrte/nicht erlaubte Kopierquelle ({event}): {p!r}")
            for p in dst_args:
                if p is None:
                    continue
                cls = self._classify(p)
                if cls is None or self._matches_blocked(cls) or not self._in_write_roots(cls):
                    self._record_block(event)
                    raise IsolationViolation(f"N4-N2-Guard: gesperrtes/nicht erlaubtes Kopierziel ({event}): {p!r}")
            return
        n_paths, n_dirfd_total = self._MUTATE_ARG_LAYOUT.get(event, (2, 0))
        path_args = args[:n_paths]
        dir_fd_args = args[n_paths:n_paths + n_dirfd_total] if n_dirfd_total else ()
        # os.mkdir hat (path, mode, dir_fd) -- der mode (int) ist KEIN Pfad.
        if event == "os.mkdir" and len(args) >= 3:
            dir_fd_args = (args[2],)
        # Integration fix (consistent with P4 fd-provenance): shutil.
        # rmtree's safe-fd implementation legitimately uses `os.unlink(name,
        # dir_fd=topfd)`/`os.rmdir(name, dir_fd=topfd)` with a dir_fd it
        # obtained from its OWN prior wrapped `os.open()` on an already
        # root-checked private path -- rejecting EVERY non-negative dir_fd
        # outright (P3's literal fix) would make `shutil.rmtree` on one's
        # own private tmp dir permanently unusable on this platform. A
        # dir_fd we did NOT open ourselves remains the strict, rejected
        # case; an owned one is trusted (the directory was already
        # write-root-checked when WE opened it) and `name` here is
        # dir_fd-RELATIVE (not cwd-relative) so path reclassification below
        # is skipped for it.
        dir_fd_owned = any(
            isinstance(d, int) and not isinstance(d, bool) and d in self._owned_fds
            for d in dir_fd_args
        )
        if not dir_fd_owned and any(d not in self._NO_EXPLICIT_DIR_FD for d in dir_fd_args):
            self._record_block(event)
            raise IsolationViolation(f"N4-N2-Guard: dir_fd-relative Mutation abgelehnt ({event}): {args!r}")
        if dir_fd_owned:
            return
        for p in path_args:
            if p is None:
                continue
            cls = self._classify(p)
            if cls is None or self._matches_blocked(cls) or not self._in_write_roots(cls):
                self._record_block(event)
                raise IsolationViolation(f"N4-N2-Guard: gesperrte/nicht erlaubte Mutation ({event}): {p!r}")

    # N4-N3 Fix P12 (01_GENERALREVIEW.md §5 "Link-/Netzgrenzen ...
    # unvollstaendig"): Symlink-/Hardlink-Erzeugung ist im engen
    # Testharness nie noetig -- unconditional ablehnen, unabhaengig vom
    # Ziel (verhindert u.a. einen Link, der aus einer erlaubten Wurzel
    # heraus auf einen gesperrten Bereich zeigt).
    def _handle_link(self, event: str, args) -> None:
        self._record_block(event)
        raise IsolationViolation(f"N4-N2-Guard: Symlink-/Hardlink-Erzeugung im Testharness abgelehnt ({event}): {args!r}")

    def _handle_list(self, event: str, args) -> None:
        path = args[0] if args else None
        if path is None:
            path = "."
        # Integration fix (consistent with _handle_open's fd-provenance
        # check P4): shutil.rmtree's safe-fd implementation calls
        # `os.scandir(dirfd)`/`os.unlink(name, dir_fd=dirfd)` using an
        # INTEGER directory fd it obtained from its OWN prior (wrapped,
        # root-checked) `os.open()` call on an allowed private path -- the
        # int itself is never a path string `_classify` can lexically
        # evaluate. Only a fd THIS process actually opened counts as
        # "owned"; an unrecognized int is still rejected.
        if isinstance(path, int) and not isinstance(path, bool):
            if path in self._owned_fds:
                return
            self._record_block(event)
            raise IsolationViolation(f"N4-N2-Guard: nicht autorisierter Datei-Descriptor fuer Listing ({event}): {path!r}")
        cls = self._classify(path)
        if cls is None or self._matches_blocked(cls) or not self._in_read_roots(cls):
            self._record_block(event)
            raise IsolationViolation(f"N4-N2-Guard: gesperrtes/nicht erlaubtes Listing ({event}): {path!r}")

    def _handle_popen(self, args) -> None:
        executable, popen_args, cwd, env = args
        argv = tuple(str(a) for a in (popen_args or [executable]))
        self.authorize_and_consume(argv, cwd=cwd, env=env)

    # N4-N3 Fix P12 (01_GENERALREVIEW.md §5): echtes Netz VOR jeder IO
    # sperren -- nicht nur `connect`, auch Namensauflösung und
    # Datagrammversand ohne vorherigen `connect` (UDP `sendto`).
    _NETWORK_EVENTS = frozenset({"socket.connect", "socket.getaddrinfo", "socket.gethostbyname", "socket.sendto"})
    _LINK_EVENTS = frozenset({"os.symlink", "os.link"})

    def _audit_hook(self, event: str, args: tuple) -> None:
        if event == "open":
            self._handle_open(args)
        elif event in self._MUTATE_WRITE_EVENTS:
            self._handle_mutate(event, args)
        elif event in self._LINK_EVENTS:
            self._handle_link(event, args)
        elif event in self._LIST_READ_EVENTS:
            self._handle_list(event, args)
        elif event in self._NETWORK_EVENTS and self._primary:
            self._record_block(event)
            raise IsolationViolation(f"N4-N2-Guard: echte Netzoperation gesperrt (kein registriertes Double): {event}")
        elif event == "subprocess.Popen" and self._primary:
            self._handle_popen(args)

    # ── Metadaten-Wrapper (KEIN Audit-Event -> explizit gewrapt) ────────
    def _check_metadata(self, op: str, path, dir_fd) -> None:
        # N4-N3 Fix P3: -1 ist der CPython-Normalwert fuer "kein explizites
        # dir_fd" (s. `_NO_EXPLICIT_DIR_FD`), kein fremder Deskriptor.
        # Integration fix (consistent mit der Mutations-Ausnahme oben):
        # ein von UNS SELBST geoeffneter, bereits root-gepruefter dir_fd
        # wird vertraut (z.B. shutil.rmtree-Safe-fd-Pfad); `path` ist dann
        # dir_fd-RELATIV, eine erneute cwd-bezogene Klassifikation waere
        # falsch. Ein fremder dir_fd bleibt der strenge, abgelehnte Fall.
        if dir_fd not in self._NO_EXPLICIT_DIR_FD:
            if isinstance(dir_fd, int) and not isinstance(dir_fd, bool) and dir_fd in self._owned_fds:
                return
            self._record_block(op)
            raise IsolationViolation(f"N4-N2-Guard: dir_fd-relative Metadatenpruefung abgelehnt ({op}): {path!r}")
        cls = self._classify(path)
        if cls is None:
            self._record_block(op)
            raise IsolationViolation(f"N4-N2-Guard: nicht sicher klassifizierbarer Pfad fuer {op}: {path!r}")
        if self._matches_blocked(cls):
            self._record_block(op)
            raise IsolationViolation(f"N4-N2-Guard: gesperrter Pfad fuer {op}: {path!r}")
        # N4-N3 Fix P5: exakte Vorfahren benannter Lesewurzeln duerfen
        # Metadaten (lstat/stat/exists/is_file) liefern -- `Path.resolve`/
        # `realpath` braucht das fuer JEDEN Vorfahren eines aufgeloesten
        # Pfads, nicht nur fuer den Pfad selbst. P2: artifact_read_paths
        # sind ebenfalls metadatenfaehig (Elternprozess prueft Existenz
        # von Kindphasen-Dateien).
        if not (self._in_read_roots(cls) or self._in_artifact_read_exact(cls) or self._in_metadata_ancestors(cls)):
            self._record_block(op)
            raise IsolationViolation(f"N4-N2-Guard: {op} ausserhalb erlaubter Lese-/Metadatenwurzeln: {path!r}")
        self._underlying_io_calls[op] = self._underlying_io_calls.get(op, 0) + 1

    def _install_metadata_wrappers(self) -> None:
        guard = self
        real_os_stat = os.stat
        real_os_lstat = os.lstat
        real_os_path_exists = os.path.exists
        real_os_path_isfile = os.path.isfile
        real_path_stat = pathlib.Path.stat
        real_path_exists = pathlib.Path.exists
        real_path_is_file = pathlib.Path.is_file

        def _guarded_os_stat(path, *a, **kw):
            guard._check_metadata("stat", path, kw.get("dir_fd"))
            return real_os_stat(path, *a, **kw)

        def _guarded_os_lstat(path, *a, **kw):
            guard._check_metadata("lstat", path, kw.get("dir_fd"))
            return real_os_lstat(path, *a, **kw)

        def _guarded_os_path_exists(path):
            guard._check_metadata("os_path_exists", path, None)
            return real_os_path_exists(path)

        def _guarded_os_path_isfile(path):
            guard._check_metadata("os_path_isfile", path, None)
            return real_os_path_isfile(path)

        def _guarded_path_stat(self_path, *a, **kw):
            guard._check_metadata("path_stat", self_path, kw.get("dir_fd"))
            return real_path_stat(self_path, *a, **kw)

        def _guarded_path_exists(self_path, *a, **kw):
            guard._check_metadata("path_exists", self_path, None)
            return real_path_exists(self_path, *a, **kw)

        def _guarded_path_is_file(self_path, *a, **kw):
            guard._check_metadata("path_is_file", self_path, None)
            return real_path_is_file(self_path, *a, **kw)

        os.stat = _guarded_os_stat
        os.lstat = _guarded_os_lstat
        os.path.exists = _guarded_os_path_exists
        os.path.isfile = _guarded_os_path_isfile
        pathlib.Path.stat = _guarded_path_stat
        pathlib.Path.exists = _guarded_path_exists
        pathlib.Path.is_file = _guarded_path_is_file

    def _install_private_home(self) -> None:
        """Patcht `pathlib.Path.home`/`Path.expanduser`/`os.path.expanduser`
        PROZESSWEIT auf `self.private_home`. Reale `HOME`/`CODEX_HOME`-
        Umgebungsvariablen werden NICHT geschrieben -- nur die Python-Ebene
        wird umgelenkt, damit spaetere `mock.patch.object(Path, "home",
        ...)`-Aufrufe einzelner Tests weiterhin normal ueber dieser
        Baseline verschachteln (beim Verlassen des `with`-Blocks stellt
        `mock.patch` automatisch WIEDER UNSERE patchte Fassung her, nicht
        das echte CPython-Original).

        API-CONTRACT-N4N2.md §5.2: zusaetzlich `tempfile.tempdir` auf den
        ersten benannten privaten Schreibbereich umbiegen -- sonst landen
        `tempfile.mkdtemp()`/`NamedTemporaryFile()`-Aufrufe OHNE explizites
        `dir=` (so wie es die ~30 Profiltests tun) ausserhalb der
        durchgesetzten Schreibgrenze und lösen eine `IsolationViolation`
        aus. Nur beim Primaerinstall, nur dieser eine Prozessstatus
        (`tempfile.tempdir` ist, wie `Path.home`, ein globaler Modulzustand)."""
        private_home = self.private_home
        tempfile.tempdir = self.private_write_roots[0]

        def _priv_home(_cls):
            return pathlib.Path(private_home)

        def _priv_path_expanduser(self_path):
            s = str(self_path)
            if s == "~":
                return pathlib.Path(private_home)
            if s.startswith("~/") or s.startswith("~" + os.sep):
                return pathlib.Path(private_home) / s[2:]
            return self_path

        def _priv_os_expanduser(path):
            if isinstance(path, bytes):
                return path
            s = os.fspath(path)
            if s == "~":
                return private_home
            if s.startswith("~/") or s.startswith("~" + os.sep):
                return private_home + s[1:]
            return s

        pathlib.Path.home = classmethod(_priv_home)
        pathlib.Path.expanduser = _priv_path_expanduser
        os.path.expanduser = _priv_os_expanduser

    def _install_fd_provenance_wrappers(self) -> None:
        """N4-N3 Fix P4: wrapped `os.open`/`os.pipe`/`os.close` erlauben
        die NACHVOLLZIEHBARE private os.open->os.fdopen/io.open(fd)-Kette
        sowie private Popen-PIPE-Deskriptoren (subprocess wrappt seine
        intern via `os.pipe` erzeugten Enden ueber `io.open(fd, ...)` --
        ohne Herkunftsnachweis wuerde das als fremder Deskriptor
        blockiert). Nur tatsaechlich hier erzeugte fds gelten als
        "besessen"; Schliessen loescht die Herkunft sofort (keine
        pauschale Integerfreigabe)."""
        guard = self
        real_os_open = os.open
        real_os_pipe = os.pipe
        real_os_close = os.close

        def _guarded_os_open(path, flags, *a, **kw):
            # Integration fix: CPython's "open" audit event omits dir_fd
            # entirely (`sys.audit("open", path, mode, flags)`) -- a
            # dir_fd-relative os.open (e.g. shutil.rmtree's safe-fd descent
            # via `os.open(entry.name, flags, dir_fd=topfd)`) is therefore
            # LEXICALLY INDISTINGUISHABLE in `_handle_open` from a
            # cwd-relative bare-name open (`entry.name` is relative to the
            # fd, not to cwd, so `os.path.abspath` would resolve it wrong).
            # When the dir_fd itself is one WE already own (root-checked at
            # the time it was opened), mark this one call as trusted so
            # `_handle_open`'s audit callback (fired synchronously inside
            # `real_os_open` below) can skip path reclassification for it.
            dir_fd = kw.get("dir_fd")
            trusted = isinstance(dir_fd, int) and not isinstance(dir_fd, bool) and dir_fd in guard._owned_fds
            if trusted:
                guard._trusted_dirfd_open_depth += 1
            try:
                fd = real_os_open(path, flags, *a, **kw)
            finally:
                if trusted:
                    guard._trusted_dirfd_open_depth -= 1
            guard._owned_fds.add(fd)
            return fd

        def _guarded_os_pipe(*a, **kw):
            r, w = real_os_pipe(*a, **kw)
            guard._owned_fds.update({r, w})
            return r, w

        def _guarded_os_close(fd, *a, **kw):
            guard._owned_fds.discard(fd)
            return real_os_close(fd, *a, **kw)

        os.open = _guarded_os_open
        os.pipe = _guarded_os_pipe
        os.close = _guarded_os_close

    def install(self, *, primary: bool = False) -> None:
        self._primary = primary
        sys.addaudithook(self._audit_hook)
        self.install_order.append("audit_hook")
        if primary:
            self._install_private_home()
            self.install_order.append("private_home")
            self._install_metadata_wrappers()
            self.install_order.append("metadata_wrappers")
            self._install_fd_provenance_wrappers()
            self.install_order.append("fd_provenance_wrappers")

    # ── Export (INTERFACE-CONTRACT.json phase_required_fields, 27 Felder) ──
    def export_status(self, *, test_or_fixture_id=None, parent_process_id=None,
                       runner_sha256=None, bootstrap_sha256=None, profile_sha256=None,
                       completion_status="running") -> dict:
        """NIE echte Nutzerkonfiguration, NIE Tokenwerte -- nur Zaehler/
        Installationsreihenfolge/wirksame Rootklassen/Hashes/Kinderbelege.
        Feldnamen folgen INTERFACE-CONTRACT.json `phase_required_fields`
        (N4-N3-Umbenennung ggue. N4-N2, 01_GENERALREVIEW.md §5 "Validator
        prueft Schluessel statt entscheidende Werte"): `completion_state`
        -> `completion_status`, `context_hash` -> `context_sha256_
        without_secrets`, `effective_allowed_root_classes` -> getrennte
        `enforced_read_roots`/`enforced_write_roots`, neu `artifact_
        read_paths`/`metadata_ancestor_paths`. `runner_sha256`/
        `bootstrap_sha256`/`profile_sha256` sind Mains Provenienzwerte
        (`evidence_context`) -- NUR Durchreichen, falls der Aufrufer sie
        kennt; dieses Modul kann sie nicht selbst ermitteln.
        `counters.unexpected_blocked` bleibt ZUSAETZLICH fuer die
        eingefrorenen routing/F1-Aufrufer erhalten (API-CONTRACT-N4N2.md
        Legacy-Vertrag: `export_status().counters.unexpected_blocked`)."""
        return {
            "bundle_id": self.bundle_id,
            "process_id": self.process_id,
            "role": self.role,
            "test_or_fixture_id": test_or_fixture_id or self.process_id,
            "parent_process_id": parent_process_id,
            "pid": os.getpid(),
            "ppid": os.getppid(),
            "actual_utc": _utcnow_iso(),
            "runner_sha256": runner_sha256,
            "bootstrap_sha256": bootstrap_sha256,
            "support_sha256": _support_hash(),
            "profile_sha256": profile_sha256,
            "context_sha256_without_secrets": self._context_hash,
            "install_order": list(self.install_order),
            "enforced_read_roots": sorted(self._read_roots),
            "enforced_write_roots": sorted(self._write_roots),
            "artifact_read_paths": list(self.artifact_read_paths),
            "metadata_ancestor_paths": sorted(self._metadata_ancestor_paths),
            "expected_probe_counts_by_operation": dict(self._expected_counts),
            "unexpected_counts_by_operation": dict(self._unexpected_counts_by_operation),
            "underlying_io_calls_by_operation": dict(self._underlying_io_calls),
            "child_authorizations": list(self._child_authorizations),
            "child_starts": list(self._child_starts),
            "child_consumption": list(self._child_consumption),
            "child_ends": list(self._child_ends),
            "completion_status": completion_status,
            # Rueckwaertskompatibel (eingefrorene routing/F1-Aufrufer, s.
            # Docstring oben): KEIN Ersatz fuer die obigen Contract-Felder.
            "counters": {"unexpected_blocked": self._unexpected_blocked},
        }

    def export_phase(self, phase: str, path, *, evidence=None, completion_status="running",
                      events=None) -> dict:
        """N4-N3 Fix G-SEAM-EVIDENCE (MAIN-SEAM-SPEC.md:104-117,
        01_GENERALREVIEW.md §3 "Exportargumente passen nicht zusammen"):
        PINNED Aufrufsignatur `guard.export_phase(phase, path, *, evidence,
        completion_status, events=None)`. Vorher leitete diese Methode
        beliebige `**kwargs` ungeprueft an `export_status(**kwargs)`
        weiter -- ein `evidence=`-Schluessel (wie Mains `bootstrap_entry.py`
        ihn seit je uebergibt) war dort kein bekanntes Keyword und loeste
        einen deterministischen `TypeError` vor dem allerersten Export aus
        (rc96). `evidence` (Mains Provenienz, NIE in den Guard-Konstruktor)
        liefert test_or_fixture_id/parent_process_id/runner_sha256/
        bootstrap_sha256/profile_sha256/context_sha256_without_secrets;
        fehlende Felder fallen auf `export_status`s eigene Defaults zurueck
        (Solo-Fallback ohne Mains Runner, s. `main()` unten). `events` wird
        aktuell nur entgegengenommen und veraendert den Exportsatz nicht --
        die eigentliche Ereignis-Kreuzpruefung lebt in der reinen Funktion
        `phase_value_validation` (der Aufrufer uebergibt die echten Events
        dort separat, kein zweiter Weg)."""
        evidence = dict(evidence or {})
        data = self.export_status(
            test_or_fixture_id=evidence.get("test_or_fixture_id"),
            parent_process_id=evidence.get("parent_process_id"),
            runner_sha256=evidence.get("runner_sha256"),
            bootstrap_sha256=evidence.get("bootstrap_sha256"),
            profile_sha256=evidence.get("profile_sha256"),
            completion_status=completion_status,
        )
        if evidence.get("context_sha256_without_secrets"):
            data["context_sha256_without_secrets"] = evidence["context_sha256_without_secrets"]
        data["phase"] = phase
        Path(path).write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
        return data

    def export_guard_state(self, path) -> dict:
        """N4-N3 Fix (01_GENERALREVIEW.md §5 "Eingefrorene Routing-API
        gebrochen"): EIN-Argument-Aufruf (N4-N1 hiess die Datei
        export_guard_state; API-CONTRACT-N4N2.md Legacy-Vertrag bleibt
        `export_guard_state(path)`). Schreibt einen EIGENEN, wertfreien
        privaten Statussnapshot nach `path` -- hat KEINE `phase` und
        ersetzt/ueberschreibt NIE eine offizielle before/after-
        Phasendatei (die laufen ausschliesslich ueber `export_phase`)."""
        data = self.export_status()
        Path(path).write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
        return data


_EXPORT_REQUIRED_FIELDS = (
    "bundle_id", "process_id", "role", "test_or_fixture_id", "parent_process_id",
    "pid", "ppid", "phase", "actual_utc", "runner_sha256", "bootstrap_sha256",
    "support_sha256", "profile_sha256", "context_sha256_without_secrets",
    "install_order", "enforced_read_roots", "enforced_write_roots",
    "artifact_read_paths", "metadata_ancestor_paths",
    "expected_probe_counts_by_operation", "unexpected_counts_by_operation",
    "underlying_io_calls_by_operation", "child_authorizations", "child_starts",
    "child_consumption", "child_ends", "completion_status",
)

_HASH_HEX_LEN = 64
_OPTIONAL_HASH_FIELDS = ("runner_sha256", "bootstrap_sha256", "profile_sha256")
_REQUIRED_HASH_FIELDS = ("support_sha256", "context_sha256_without_secrets")
_COMPLETION_STATUSES = ("ready", "running", "completed", "failed", "export_error")
_COUNT_DICT_FIELDS = (
    "expected_probe_counts_by_operation", "unexpected_counts_by_operation",
    "underlying_io_calls_by_operation",
)
_LIST_FIELDS = (
    "install_order", "enforced_read_roots", "enforced_write_roots",
    "artifact_read_paths", "metadata_ancestor_paths", "child_authorizations",
    "child_starts", "child_consumption", "child_ends",
)


def _is_nonempty_hash(value) -> bool:
    return isinstance(value, str) and len(value) == _HASH_HEX_LEN and all(c in "0123456789abcdef" for c in value)


def validate_export_schema(data) -> list:
    """Bootstrap-/Export-Validator-Seam (INTERFACE-CONTRACT.json
    `phase_required_fields`, 01_GENERALREVIEW.md §5 "Validator prueft
    Schluessel statt entscheidende Werte"): prueft TYPEN und NICHTLEERE
    Hashes/Identitaeten + `phase` in {before,after} + ALLE
    `phase_required_fields` mit korrektem Typ -- NICHT nur
    Schluesselanwesenheit. `runner_sha256`/`bootstrap_sha256`/
    `profile_sha256` sind Mains Provenienzwerte; dieses Modul akzeptiert
    dafuer `None` ODER einen echten 64-Hex-Hash (nicht jede leere/kaputte
    Zeichenkette) -- ein Solo-Fallback-Kindprozess ohne Mains Runner kann
    sie nicht selbst ermitteln. `support_sha256`/`context_sha256_
    without_secrets` sind IMMER selbst berechenbar und deshalb STRENG
    nichtleer gefordert. Main's `run_bundle_n4n3.py`/der Profiltest
    koennen dieselbe Funktion fuer die externe Nachherpruefung
    wiederverwenden, OHNE einen dritten Prozess zu starten."""
    if not isinstance(data, dict):
        return ["not_a_dict"]
    problems = [k for k in _EXPORT_REQUIRED_FIELDS if k not in data]

    if data.get("phase") not in ("before", "after"):
        problems.append("phase_invalid")
    for key in ("bundle_id", "process_id", "role", "test_or_fixture_id", "actual_utc"):
        if not isinstance(data.get(key), str) or not data.get(key):
            problems.append(f"empty_or_invalid_type:{key}")
    if data.get("parent_process_id") is not None and not isinstance(data.get("parent_process_id"), str):
        problems.append("invalid_type:parent_process_id")
    for key in ("pid", "ppid"):
        value = data.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            problems.append(f"not_a_positive_int:{key}")
    for key in _REQUIRED_HASH_FIELDS:
        if not _is_nonempty_hash(data.get(key)):
            problems.append(f"invalid_or_empty_hash:{key}")
    for key in _OPTIONAL_HASH_FIELDS:
        value = data.get(key)
        if value is not None and not _is_nonempty_hash(value):
            problems.append(f"invalid_hash:{key}")
    for key in _LIST_FIELDS:
        if not isinstance(data.get(key), list):
            problems.append(f"not_a_list:{key}")
    for key in _COUNT_DICT_FIELDS:
        value = data.get(key)
        if not isinstance(value, dict) or any(
            (not isinstance(v, int)) or isinstance(v, bool) or v < 0 for v in value.values()
        ):
            problems.append(f"not_a_nonnegative_count_dict:{key}")
    if data.get("completion_status") not in _COMPLETION_STATUSES:
        problems.append("invalid_completion_status")
    return problems


def phase_value_validation(expected_plan, phase_record, events) -> list:
    """N4-N3 (MAIN-SEAM-SPEC.md geteilter Seam 2, 01_GENERALREVIEW.md §5
    "Validator prueft Schluessel statt entscheidende Werte"): vergleicht
    einen Phasensatz GEGEN den erwarteten Plan UND die tatsaechlichen
    Start-/Verbrauchs-/Endereignisse -- IDs/Rolle/Test/Parent/Hashes
    gleich geplant; PID kreuzpasst mit beobachteten Ereignissen; Zaehler
    nichtnegativ; verbotene underlying_io je Operation 0; Kinderzahlen
    phasenkorrekt (before: 0 echte Starts/Verbraeuche/Enden; erfolg-
    reicher after: genau 1 Writer + 1 Reader je Start/Verbrauch/Ende).
    Reine Funktion -- kein Prozess, kein IO."""
    if not isinstance(phase_record, dict):
        return ["phase_record_not_a_dict"]
    if not isinstance(expected_plan, dict):
        return ["expected_plan_not_a_dict"]
    problems = validate_export_schema(phase_record)

    for key in ("bundle_id", "process_id", "role", "test_or_fixture_id", "parent_process_id",
                "runner_sha256", "bootstrap_sha256", "support_sha256", "profile_sha256",
                "context_sha256_without_secrets"):
        if key in expected_plan and expected_plan[key] != phase_record.get(key):
            problems.append(f"mismatch:{key}")

    events = list(events or [])
    observed_pids = {e.get("pid") for e in events if isinstance(e, dict)}
    if events and phase_record.get("pid") not in observed_pids:
        problems.append("pid_not_cross_matched_with_events")

    unexpected_total = sum(
        v for v in (phase_record.get("unexpected_counts_by_operation") or {}).values()
        if isinstance(v, int) and not isinstance(v, bool)
    )
    if unexpected_total:
        problems.append("unexpected_blocked_nonzero")

    underlying = phase_record.get("underlying_io_calls_by_operation") or {}
    for op in (expected_plan.get("forbidden_underlying_io_ops") or ()):
        if underlying.get(op):
            problems.append(f"forbidden_underlying_io_nonzero:{op}")

    def _role_events(field, role):
        return [e for e in (phase_record.get(field) or []) if isinstance(e, dict) and e.get("role") == role]

    phase = phase_record.get("phase")
    writer_counts = tuple(len(_role_events(f, "child-writer")) for f in
                           ("child_starts", "child_consumption", "child_ends"))
    reader_counts = tuple(len(_role_events(f, "child-reader")) for f in
                           ("child_starts", "child_consumption", "child_ends"))
    if phase == "before":
        if any(writer_counts) or any(reader_counts):
            problems.append("before_phase_has_real_child_activity")
    elif phase == "after" and phase_record.get("completion_status") == "completed":
        # N4-N3 Fix (01_GENERALREVIEW.md §3 "Der Abschlussvalidator wuerde
        # auch einen korrekten Testlauf ablehnen"): NUR die Rolle, die laut
        # `expected_plan` tatsaechlich Kinder plant (der Profilparent),
        # muss genau 1 Writer+1 Reader je Start/Verbrauch/Ende zeigen. Die
        # 13 uebrigen aeusseren Tests UND beide Kinder selbst planen KEINE
        # eigenen Kinder -- ihre erfolgreiche After-Phase darf NICHT wegen
        # fehlender Writer-/Reader-Zaehler abgewiesen werden, sondern nur
        # wegen UNERWARTETER Kindaktivitaet.
        if expected_plan.get("expects_children"):
            if writer_counts != (1, 1, 1) or reader_counts != (1, 1, 1):
                problems.append("after_success_child_counts_not_exactly_one_writer_one_reader")
        else:
            if any(writer_counts) or any(reader_counts):
                problems.append("after_success_unexpected_child_activity_for_non_planning_role")

    return problems


_PRE_DISPATCH_PATH_LIST_KEYS = ("source_read_roots", "dep_read_roots", "private_write_roots", "artifact_read_paths")
_PRE_DISPATCH_PATH_SCALAR_KEYS = ("repo_root", "export_before_path", "export_after_path")


def bootstrap_pre_dispatch_validation(context) -> list:
    """N4-N3 (MAIN-SEAM-SPEC.md geteilter Seam 3): DIESELBE Pruefung, die
    `bootstrap_entry` (Main) vor jedem Dispatch laeuft -- bekannte
    Schluessel/Typen/absolute Pfade/eigene Exportmitgliedschaft. Reine
    Funktion (keine Ausnahme, keine Installation) -- Profilgegenproben
    fuettern hiermit private ungueltige Eingaben + einen protokollierenden
    Dispatcher, OHNE einen zusaetzlichen Prozess zu starten."""
    if not isinstance(context, dict):
        return ["context_not_a_dict"]
    problems = [k for k in _REQUIRED_CONTEXT_KEYS if k not in context]
    if problems:
        return problems
    if not isinstance(context.get("bundle_id"), str) or not context["bundle_id"]:
        problems.append("empty_or_invalid_type:bundle_id")
    if not isinstance(context.get("process_id"), str) or not context["process_id"]:
        problems.append("empty_or_invalid_type:process_id")
    if context.get("role") not in ("outer-test", "child-writer", "child-reader", "selfprobe"):
        problems.append("invalid_role")
    for key in _PRE_DISPATCH_PATH_SCALAR_KEYS:
        value = context.get(key)
        if value is not None and (not isinstance(value, str) or not os.path.isabs(value)):
            problems.append(f"not_an_absolute_path:{key}")
    for key in _PRE_DISPATCH_PATH_LIST_KEYS:
        value = context.get(key)
        if not isinstance(value, list) or any(
            (not isinstance(p, str)) or not os.path.isabs(p) for p in value
        ):
            problems.append(f"not_a_list_of_absolute_paths:{key}")
    export_before = context.get("export_before_path")
    export_after = context.get("export_after_path")
    if not export_before or not export_after:
        problems.append("export_target_empty")
    else:
        own_roots = [os.path.normcase(os.path.normpath(p)) for p in (context.get("private_write_roots") or [])]

        def _owned(p):
            norm = os.path.normcase(os.path.normpath(p))
            return any(norm == r or norm.startswith(r + os.sep) for r in own_roots)

        if not _owned(export_before) or not _owned(export_after):
            problems.append("export_path_outside_own_private_root")
    return problems


def _child_binding(role, argv, fixture_paths, context_path, context_sha256,
                    minimal_env, cwd, private_root, export_id) -> dict:
    """Reine Hilfsfunktion: kanonische, vergleichbare Bindung eines
    Kinderrechts (fuer `child_grant_decision`/`register_child`)."""
    return {
        "role": str(role),
        "fixture_paths": tuple(str(p) for p in (fixture_paths or ())),
        "context_path": str(context_path) if context_path else None,
        "context_sha256": str(context_sha256) if context_sha256 else None,
        "minimal_env": tuple(sorted((str(k), str(v)) for k, v in dict(minimal_env or {}).items())),
        "cwd": str(cwd) if cwd else None,
        "private_root": str(private_root) if private_root else None,
        "export_id": str(export_id),
    }


#: N4-N3: "exactly two role grants" bindet NUR die zwei kanonischen
#: Primaerrollen -- ad-hoc Selbstproben-Rollennamen (z.B.
#: "selfprobe-consumption-N") teilen sich denselben PROZESSWEITEN
#: EARLY_GUARD-Speicher wie die echten Kinder, duerfen die Zweier-
#: Obergrenze fuer child-writer/child-reader aber NICHT beeinflussen.
_PRIMARY_CHILD_ROLES = frozenset({"child-writer", "child-reader"})


def child_grant_decision(store, role, argv, fixture_paths, context_path, context_sha256,
                          minimal_env, cwd, private_root, export_id) -> tuple:
    """N4-N3 (MAIN-SEAM-SPEC.md geteilter Seam 4, 01_GENERALREVIEW.md §5
    "Kinderberechtigung ueberschreibbar; env/cwd nicht verbindlich
    gebunden"): EINE reine Entscheidung, die sowohl das echte
    Primaerlager (genau zwei Rollen: child-writer/child-reader) als auch
    ein getrenntes synthetisches Testlager bedient. Lehnt Replay eines
    bereits VERBRAUCHTEN Grants, eine geaenderte Bindung (env/cwd/argv/
    Fixture/Kontext) fuer denselben Schluessel, und eine doppelte/dritte
    gleichzeitig lebende Primaerrolle ab. Reine Funktion -- `store` wird
    NICHT mutiert, der Aufrufer entscheidet ueber das Schreiben."""
    key = tuple(str(a) for a in argv)
    binding = _child_binding(role, argv, fixture_paths, context_path, context_sha256,
                              minimal_env, cwd, private_root, export_id)
    existing = store.get(key)
    if existing is not None:
        if existing.get("consumed"):
            return ("REJECT", "replay_of_consumed_grant_argv")
        if existing.get("binding") != binding:
            return ("REJECT", "changed_binding_for_existing_argv")
        return ("GRANT", "idempotent_existing_grant")
    if binding["role"] in _PRIMARY_CHILD_ROLES:
        live_primary_roles = {
            v["binding"]["role"] for v in store.values()
            if not v.get("consumed") and v["binding"]["role"] in _PRIMARY_CHILD_ROLES
        }
        if binding["role"] in live_primary_roles:
            return ("REJECT", "duplicate_live_grant_for_role")
        if len(live_primary_roles) >= 2:
            return ("REJECT", "third_grant_exceeds_two_role_limit")
    return ("GRANT", "new_grant")


# ─── Prozessweiter Singleton-Anker ──────────────────────────────────────
# Haengt bewusst am IMMER selben `sys`-Modulobjekt (ueberlebt jede
# Wiederausfuehrung dieser Datei im selben Prozess unter einem anderen
# Modulnamen, z.B. per `spec_from_file_location` aus mehreren Testdateien).
_GUARD_SINGLETON_ATTR = "_n4n2_isolation_guard_singleton"

#: N4-N3 (MAIN-SEAM-SPEC.md "Guard context (EXACTLY these 13 keys)"):
#: `credential_block_roots`/`artifact_read_paths` ergaenzt ggue. N4-N2.
_REQUIRED_CONTEXT_KEYS = (
    "bundle_id", "process_id", "role", "real_home_class", "repo_root",
    "source_read_roots", "dep_read_roots", "private_write_roots",
    "shared_fixture_root", "export_before_path", "export_after_path",
    "credential_block_roots", "artifact_read_paths",
)


def _validate_context(context) -> None:
    if not isinstance(context, dict):
        raise IsolationBootstrapError("bootstrap_isolation: context muss ein dict sein.")
    missing = [k for k in _REQUIRED_CONTEXT_KEYS if k not in context]
    if missing:
        raise IsolationBootstrapError(f"bootstrap_isolation: fehlende Pflichtschluessel: {missing!r}")
    if not context.get("export_before_path") or not context.get("export_after_path"):
        raise IsolationBootstrapError("bootstrap_isolation: Exportziel(e) leer.")


def bootstrap_isolation(*, context: dict = None, **legacy) -> "EarlyIsolationGuard":
    """Prozessweite, idempotente Fabrik. GENAU EIN Weg installiert einen
    ECHTEN Primaerguard: `context=<vollstaendiges Kontext-Dict>` (s.
    `_REQUIRED_CONTEXT_KEYS`), aufgerufen von Mains `bootstrap_entry.py`
    VOR jedem pytest-/Produkt-/Drittimport. Erste Primaerinstallation
    gewinnt: jeder weitere Aufruf -- egal ob mit `context=` oder den alten
    Legacy-Parametern (`private_home=`, `private_root=`, `real_home=`,
    `repo_root=`, `allowed_children=`, aus den eingefrorenen routing/F1-
    Testdateien) -- liefert AUSSCHLIESSLICH die bereits installierte
    Instanz zurueck, OHNE sie neu zu installieren oder umzukonfigurieren.
    Fehlt `context` UND existiert noch KEIN Primaerguard (ungeschuetzter
    Erstaufruf ausserhalb von Mains Einstieg, z.B. ein Legacy-Aufruf ohne
    vorherige Primaerinstallation) -> `IsolationBootstrapError` (sichtbares
    Scheitern, kein stiller Platzhalterguard)."""
    guard = getattr(sys, _GUARD_SINGLETON_ATTR, None)
    if guard is not None:
        return guard
    if context is None:
        raise IsolationBootstrapError(
            "bootstrap_isolation: kein Primaerguard installiert und kein context= "
            "uebergeben -- Legacy-Parameter koennen NUR einen bereits installierten "
            "Primaerguard abrufen, niemals selbst installieren."
        )
    _validate_context(context)
    guard = EarlyIsolationGuard.from_context(context)
    guard.install(primary=True)
    setattr(sys, _GUARD_SINGLETON_ATTR, guard)
    return guard


def _load_explicit_context(value):
    """Haelt den EINEN erlaubten Weg, einen ausdruecklich gelieferten
    Kontext zu lesen: `value` ist entweder ein Pfad auf eine JSON-Datei
    ODER Inline-JSON. Beschaedigtes/unlesbares JSON scheitert SICHTBAR
    (IsolationBootstrapError) -- es wird NIE still durch einen
    Ersatzkontext uebergangen (Flo-Vorgabe 2026-11-15, Punkt 3)."""
    text = value
    try:
        if isinstance(value, str) and os.path.isfile(value):
            with open(value, "r", encoding="utf-8") as fh:
                text = fh.read()
    except OSError as exc:
        raise IsolationBootstrapError(
            f"self_bootstrap_isolation: ausdruecklich gelieferte Kontextdatei nicht lesbar: {exc}"
        )
    try:
        return json.loads(text)
    except (ValueError, TypeError) as exc:
        raise IsolationBootstrapError(
            f"self_bootstrap_isolation: ausdruecklich gelieferter Kontext nicht als JSON lesbar: {exc}"
        )


def _build_private_outer_context() -> dict:
    """Erzeugt EINEN vollstaendigen, in sich gueltigen Privatkontext fuer
    den aeusseren Testprozess (Rolle 'outer-test'). `real_home_class` wird
    HIER -- VOR jeder Guard-Installation, also mit noch unveraendertem
    `Path.home()`/`expanduser` -- bestimmt, damit die daraus abgeleiteten
    ECHTEN Credentialklassen (`~/.openwebui_env` u.a.) sowie der env-HOME-
    Zweig weiterhin gesperrt bleiben. Der private Schreibbereich ist ein
    frisches `mkdtemp()` unter dem ECHTEN System-Tempdir (bevor
    `tempfile.tempdir` durch die Installation umgelenkt wird); beide
    Exportpfade liegen in diesem Bereich (erfuellt
    `bootstrap_pre_dispatch_validation`)."""
    real_home = str(Path.home())
    private_root = os.path.realpath(tempfile.mkdtemp(prefix="lth-outer-self-"))
    shared = os.path.join(private_root, "shared-fixture")
    exports = os.path.join(private_root, "exports")
    os.makedirs(shared, exist_ok=True)
    os.makedirs(exports, exist_ok=True)
    return {
        "bundle_id": "self-bootstrap-" + os.path.basename(private_root),
        "process_id": "outer-" + str(os.getpid()),
        "role": "outer-test",
        "real_home_class": real_home,
        "repo_root": str(_REPO_ROOT),
        "source_read_roots": [str(_SCRIPTS_DIR)],
        "dep_read_roots": [],
        "private_write_roots": [private_root],
        "shared_fixture_root": shared,
        "export_before_path": os.path.join(exports, "outer.before.json"),
        "export_after_path": os.path.join(exports, "outer.after.json"),
        "credential_block_roots": [],
        "artifact_read_paths": [],
    }


def self_bootstrap_isolation(*, explicit_context: dict = None) -> "EarlyIsolationGuard":
    """Option A (von Flo am 2026-11-15 bestaetigt): EIN gemeinsamer, sicherer
    Self-Bootstrap im bestehenden Test-Support, den die betroffenen
    Testdateien FRUEH -- vor jedem schutzbeduerftigen Produktimport --
    aufrufen. Unterscheidet drei Faelle SICHTBAR und ersetzt den frueheren
    Legacy-Aufruf `bootstrap_isolation(private_home=..., repo_root=...)`, der
    ohne vorinstallierten Primaerguard (z.B. unter `python3 -m unittest -q`
    oder `run_all.py` ohne Mains `bootstrap_entry.py`) zwingend scheiterte:

    1. Ein bereits korrekt installierter Primaerguard (externer/Runner-
       Einstieg via `bootstrap_isolation(context=...)` aus Mains
       `bootstrap_entry.py`) wird UNVERAENDERT WIEDERVERWENDET.
    2. Ein AUSDRUECKLICH gelieferter Kontext (Parameter `explicit_context`
       ODER Umgebungsvariable `LTH_CONTEXT_JSON`, selbst Dateipfad oder
       Inline-JSON) wird STRIKT validiert; ist er beschaedigt/unvollstaendig,
       scheitert dieser Aufruf SICHTBAR -- NIE stiller Ersatzkontext.
    3. Ohne externen Guard UND ohne ausdruecklichen Kontext wird ein
       VOLLSTAENDIGER, validierter PRIVATER Kontext erzeugt und als
       Primaerguard installiert.

    In allen Faellen bleibt die Schutzwirkung erhalten: echte Benutzer-/
    Credentialdateien und echter Netz-/Backendkontakt bleiben gesperrt; es
    gibt keinen Guardabbau, keine zusaetzlichen Skips, keine Abschwaechung
    von Assertions und kein Aufweiten auf echte Benutzerpfade. Die strenge
    Fehlersemantik von `bootstrap_isolation` selbst bleibt UNVERAENDERT (die
    Profilgegenproben pruefen sie weiter direkt)."""
    # IO-Isolationsmassnahme (keine Aufweichung des Schutzes): sobald ein
    # Primaerguard `open(write)` UNBEDINGT erzwingt, wuerde Pythons Bytecode-
    # Cache (`__pycache__/*.pyc`) fuer JEDES danach kompilierte Modul ausser-
    # halb der Privatwurzeln schreiben und eine IsolationViolation ausloesen
    # (unter `python3 -m unittest -q` scheitern sonst die nachfolgend impor-
    # tierten Testmodule beim Import). Bytecode-Schreiben im isolierten Inter-
    # preter abschalten vermeidet genau diese Nebenwirkung, ohne erlaubte
    # Wurzeln aufzuweiten, Assertions abzuschwaechen oder den echten
    # Credential-/Netzschutz anzutasten.
    sys.dont_write_bytecode = True
    existing = getattr(sys, _GUARD_SINGLETON_ATTR, None)
    if existing is not None:
        return existing  # Fall 1: externer Primaerguard -> unveraendert weiter.

    ctx = explicit_context
    source = "explicit_context" if ctx is not None else None
    if ctx is None:
        env_ctx = os.environ.get("LTH_CONTEXT_JSON")
        if env_ctx:
            source = "LTH_CONTEXT_JSON"
            ctx = _load_explicit_context(env_ctx)
    if ctx is not None:
        problems = bootstrap_pre_dispatch_validation(ctx)
        if problems:  # Fall 2: beschaedigt/unvollstaendig -> sichtbar scheitern.
            raise IsolationBootstrapError(
                "self_bootstrap_isolation: ausdruecklich gelieferter Kontext "
                f"({source}) ist unvollstaendig/beschaedigt und wird NICHT still "
                f"ersetzt: {problems!r}"
            )
        return bootstrap_isolation(context=ctx)

    # Fall 3: vollstaendigen privaten Kontext erzeugen + installieren.
    ctx = _build_private_outer_context()
    problems = bootstrap_pre_dispatch_validation(ctx)
    if problems:  # defensiver Selbsttest -- darf praktisch nie eintreten.
        raise IsolationBootstrapError(
            f"self_bootstrap_isolation: intern erzeugter Privatkontext ungueltig: {problems!r}"
        )
    return bootstrap_isolation(context=ctx)


# ─────────────────────────────────────────────────────────────────────────
# Weg 3 (von Flo am 2026-11-15 beauftragt): schlanke PROZESSBRUECKE fuer die
# gemeinsame `python3 -m unittest -q`-Discovery.
#
# Problem: ein ab Import installierter `sys.addaudithook`-Guard ist nicht
# entfernbar und regiert dann den GESAMTEN geteilten Interpreter -- er bricht
# vorher-gruene Fremdtests (echte `git`-Subprozesse, W11s globalen
# socket.socket-Patch) und kontaminiert `unexpected_blocked`. Die
# Guard-/Isolations-Testfamilie ist ein Frisch-Prozess-Konstrukt.
#
# Loesung: im geteilten Elternprozess wird WEDER Guard NOCH Produktimport NOCH
# globaler Patch ausgefuehrt. Die betroffenen Module stellen beim Import nur
# diese Bruecke bereit (via `load_tests` + EIN TestCase-Vertreter). Der
# Vertreter startet den ECHTEN geschuetzten Testkoerper in einem FRISCHEN
# Python-Interpreter (mit frueh installiertem Schutz) und reicht dessen
# Ergebnis verbindlich zurueck. Standalone/run_all.py/Bundle laufen
# unveraendert ueber den echten Koerper (siehe `is_real_body_env`).
_UNITTEST_CHILD_ENV = "LTH_UNITTEST_CHILD"
_RUNNER_ENTRY_ENV = "LTH_BOOTSTRAP_ENTRY"
_RUNNER_CONTEXT_ENV = "LTH_CONTEXT_JSON"
_CHILD_RESULT_MARKER = "LTH_CHILD_RESULT:"


def is_real_body_env() -> bool:
    """True, wenn dieser Prozess den ECHTEN geschuetzten Testkoerper ausfuehren
    soll statt nur die Bruecke bereitzustellen:
      * ein von der Bruecke gestarteter frischer Kindinterpreter
        (`LTH_UNITTEST_CHILD=1`), ODER
      * eine Bundle-/Runner-Phase. Der Runner setzt `LTH_CONTEXT_JSON` (den
        Guard-Kontext-Umschlag) in JEDER pytest-Phase -- `LTH_BOOTSTRAP_ENTRY`
        dagegen nur in der Profil-Phase (i==1). `LTH_CONTEXT_JSON` ist daher
        das verlaessliche Runner-Signal fuer ALLE Phasen; beide werden
        geprueft.
    Das aufrufende Modul ergaenzt `__name__ == '__main__'` (Standalone /
    run_all.py starten die Datei als Skript). Unter dem geteilten `python3 -m
    unittest -q` ist KEINE dieser LTH_*-Variablen gesetzt -> Bruecke."""
    return (
        os.environ.get(_UNITTEST_CHILD_ENV) == "1"
        or bool(os.environ.get(_RUNNER_CONTEXT_ENV))
        or bool(os.environ.get(_RUNNER_ENTRY_ENV))
    )


def _collect_module_suite(module) -> "unittest.TestSuite":
    """Sammelt die tatsaechlichen fachlichen Tests eines Moduls: zuerst
    `unittest.TestCase`-Klassen; findet sich keine (pytest-artige F1-Dateien
    mit `def test_*()`), werden die Modul-`test_*`-Funktionen als echte
    Testfaelle verpackt -- KEINE uebersprungene Assertion, KEINE leere Suite."""
    suite = unittest.TestLoader().loadTestsFromModule(module)
    if suite.countTestCases() > 0:
        return suite
    fn_suite = unittest.TestSuite()
    for name in sorted(vars(module)):
        obj = getattr(module, name)
        if name.startswith("test_") and callable(obj) and not isinstance(obj, type):
            fn_suite.addTest(unittest.FunctionTestCase(obj))
    return fn_suite


def run_module_as_child(module) -> int:
    """Wird NUR im frischen Kindinterpreter aus dem `__main__`-Zweig der
    betroffenen Module gerufen (Schutz ist dann bereits frueh via Import
    installiert). Fuehrt die echten fachlichen Tests mit echten Assertions
    aus und meldet das Ergebnis als EINE Markerzeile auf STDOUT zurueck
    (reiner fd-Write, nicht guard-blockiert -- kein Dateischreiben noetig).
    Rueckgabecode 0 nur bei tatsaechlich ausgefuehrten, fehlerfreien Tests."""
    suite = _collect_module_suite(module)
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=1).run(suite)
    payload = {
        "ran": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(getattr(result, "skipped", []) or []),
        "success": bool(result.wasSuccessful() and result.testsRun > 0),
    }
    sys.stdout.write("\n" + _CHILD_RESULT_MARKER + json.dumps(payload) + "\n")
    sys.stdout.flush()
    return 0 if payload["success"] else 1


class _DelegatingChildBase(unittest.TestCase):
    """Elternvertreter im geteilten Interpreter: startet den echten Koerper in
    einem frischen Interpreter und bindet dessen Ergebnis. Unterklassen setzen
    `_module_file`, `_module_label`, `_min_domain_tests`, `_timeout_s`."""
    _module_file = None
    _module_label = None
    _min_domain_tests = 1
    _timeout_s = 300

    def test_protected_body_runs_in_fresh_interpreter(self):
        # Kontrollierte MINIMALE Umgebung: NICHT die (moeglicherweise durch
        # W11 o.ae. mutierte) Eltern-os.environ erben. Nur das Noetige + die
        # Kindmarke, die Rekursion/Re-Delegation verhindert (im Kind ist
        # `is_real_body_env()` True -> kein `load_tests` definiert).
        env = {
            "HOME": os.environ.get("HOME", ""),
            "PATH": os.environ.get("PATH", ""),
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            _UNITTEST_CHILD_ENV: "1",
        }
        try:
            proc = subprocess.run(
                [sys.executable, self._module_file],
                env=env, cwd=str(_REPO_ROOT),
                capture_output=True, text=True, timeout=self._timeout_s,
            )
        except subprocess.TimeoutExpired as exc:
            self.fail(
                f"Prozessbruecke {self._module_label}: Kindinterpreter-Timeout "
                f"nach {self._timeout_s}s -- Elterntest schlaegt fehl.\n"
                f"stdout(tail):\n{(exc.stdout or '')[-2000:]}\n"
                f"stderr(tail):\n{(exc.stderr or '')[-2000:]}")
        log_tail = ("stdout(tail):\n" + proc.stdout[-2500:] +
                    "\n---stderr(tail)---\n" + proc.stderr[-4500:])
        marker = None
        for line in proc.stdout.splitlines():
            if line.startswith(_CHILD_RESULT_MARKER):
                marker = line[len(_CHILD_RESULT_MARKER):]
        self.assertIsNotNone(
            marker,
            f"Prozessbruecke {self._module_label}: Kind lieferte KEIN Ergebnis "
            f"(Start-/Bootstrapfehler? Exit 0 ohne ausgefuehrte Tests gilt NICHT "
            f"als Erfolg).\n{log_tail}")
        data = json.loads(marker)
        # Getrennte Ausweisung: 1 Elternvertreter vs. tatsaechlich ausgefuehrte
        # fachliche Kindtests.
        sys.stderr.write(
            f"[prozessbruecke] {self._module_label}: 1 Elternvertreter -> "
            f"{data['ran']} fachliche Kindtests "
            f"(failures={data['failures']}, errors={data['errors']}, "
            f"skipped={data['skipped']})\n")
        self.assertEqual(
            proc.returncode, 0,
            f"Prozessbruecke {self._module_label}: Kind-Exitcode "
            f"{proc.returncode} != 0.\n{log_tail}")
        self.assertEqual(
            data["failures"], 0,
            f"Prozessbruecke {self._module_label}: {data['failures']} Kind-"
            f"Failure(s).\n{log_tail}")
        self.assertEqual(
            data["errors"], 0,
            f"Prozessbruecke {self._module_label}: {data['errors']} Kind-"
            f"Error(s).\n{log_tail}")
        self.assertGreaterEqual(
            data["ran"], self._min_domain_tests,
            f"Prozessbruecke {self._module_label}: nur {data['ran']} Kindtests "
            f"ausgefuehrt, erwartet >= {self._min_domain_tests} "
            f"(geschrumpfte/leere Suite).\n{log_tail}")
        self.assertTrue(
            data["success"],
            f"Prozessbruecke {self._module_label}: Kind meldete keinen Erfolg."
            f"\n{log_tail}")


def make_delegating_load_tests(module_file, module_label, min_domain_tests, timeout_s=300):
    """Baut die `load_tests`-Funktion fuer den Elternprozess: liefert eine
    Suite mit GENAU EINEM Vertreter, der den echten Koerper im frischen
    Interpreter ausfuehrt. Im Kind (is_real_body_env()) wird `load_tests`
    gar nicht erst definiert -> keine Re-Delegation/Rekursion."""
    cls = type(
        "DelegatingChildTest_" + str(module_label),
        (_DelegatingChildBase,),
        {
            "_module_file": str(module_file),
            "_module_label": str(module_label),
            "_min_domain_tests": int(min_domain_tests),
            "_timeout_s": int(timeout_s),
        },
    )

    def load_tests(loader, standard_tests, pattern):  # unittest load_tests protocol
        suite = unittest.TestSuite()
        suite.addTest(cls("test_protected_body_runs_in_fresh_interpreter"))
        return suite

    return load_tests


class _ParentModeProductStub:
    """Inertes Double fuer Produktmodule/-symbole, die in KLASSENKOERPERN zur
    Importzeit ausgewertet werden (z.B. ein `factories_mod.<MARKER>` in einem
    Klassenattribut). Im geteilten Discovery-Elternprozess werden diese
    Klassen NIE ausgefuehrt (die Prozessbruecke delegiert an frische Kinder),
    daher genuegt ein Platzhalter, dessen Attributzugriff einen stabilen,
    hashbaren String liefert -- NUR damit die Klassendefinition nicht crasht.
    Kein Produktverhalten, kein Guard, kein echter Import."""

    def __getattr__(self, name):
        return "__parent_mode_stub__." + name


def parent_mode_product_stub() -> "_ParentModeProductStub":
    return _ParentModeProductStub()


_PROVIDER_ENV_PREFIXES = ("ZEITRISS_", "OPENWEBUI_", "OPENROUTER_", "MMO_SIM_PERSONA_")


def clean_provider_env() -> dict:
    """Entfernt alle bereits im Prozess gesetzten Provider-/Persona-/
    OWUI-Variablen und liefert sie zurueck (zum Wiederherstellen in
    tearDown) -- ein Test darf nicht von einer zufaellig im Testrunner-
    Prozess bereits gesetzten Umgebung profitieren oder daran scheitern."""
    saved: dict = {}
    for key in list(os.environ):
        if key.startswith(_PROVIDER_ENV_PREFIXES):
            saved[key] = os.environ.pop(key)
    return saved


# KEIN Guard-Install hier beim Modulimport (N1-Defekt, entfernt). Jeder
# Konsument (Testdatei ODER `main()` unten) muss `bootstrap_isolation(...)`
# SELBST aufrufen, bevor irgendein Produktmodul geladen wird.


# ─── Produktimporte -- NUR lazy, NIE beim Modulimport ──────────────────

_PRODUCT_MODULES: dict = {}


def _product_modules() -> dict:
    """Lazy-Import von `local_model_profile`/`setup`/`launcher` -- NUR
    beim ersten `_cmd_*`-Aufruf, NACH dem Fruehschutz oben."""
    if not _PRODUCT_MODULES:
        if str(_SCRIPTS_DIR) not in sys.path:
            sys.path.insert(0, str(_SCRIPTS_DIR))
        import local_model_profile as lmp
        import setup as setup_mod
        import launcher as launcher_mod
        _PRODUCT_MODULES["lmp"] = lmp
        _PRODUCT_MODULES["setup_mod"] = setup_mod
        _PRODUCT_MODULES["launcher_mod"] = launcher_mod
    return _PRODUCT_MODULES


def _cmd_write_matrix(env_path_a: Path, env_path_b: Path, fixture_path: Path) -> int:
    """I4: EIN Schreiberkind, ECHTER Writer -- erzeugt A (echter Erfolg)
    UND B (derselbe Writer, synthetischer Fehler NUR am verpflichtenden
    Readback-IO-Seam `setup_mod._read_env_file` -> tatsaechliches
    `False` + Pending-Marker bleibt belegt). Liest Token/URL/Modell/Limits
    aus der privaten JSON-Fixturedatei -- NIE aus argv."""
    mods = _product_modules()
    lmp = mods["lmp"]
    setup_mod = mods["setup_mod"]

    fixture = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
    updates = lmp.build_local_profile_updates(
        base_url=fixture["base_url"], model=fixture["model"], api_key=fixture["api_key"],
        owui_base_url=fixture.get("owui_base_url"),
        gm_max_tokens=fixture.get("gm_max_tokens", lmp.DEFAULT_GM_MAX_TOKENS),
        persona_max_tokens=fixture.get("persona_max_tokens", lmp.DEFAULT_PERSONA_MAX_TOKENS),
    )

    ok_a = setup_mod._update_env_file_preserving(env_path_a, updates)

    real_read_env_file = setup_mod._read_env_file
    env_path_b_resolved = Path(env_path_b)

    def _synthetic_readback_failure(path):
        if Path(path) == env_path_b_resolved:
            raise OSError("synthetic: I4 Readback-IO-Seam-Fehler (Pending-Probe, kein Secret)")
        return real_read_env_file(path)

    setup_mod._read_env_file = _synthetic_readback_failure
    try:
        ok_b = setup_mod._update_env_file_preserving(env_path_b, updates)
    finally:
        setup_mod._read_env_file = real_read_env_file

    marker_b_pending = setup_mod._pending_marker_path(env_path_b).exists()
    print(f"WROTE_A:{ok_a}")
    print(f"WROTE_B:{ok_b}:{marker_b_pending}")
    return 0 if (ok_a and not ok_b and marker_b_pending) else 1


_COMPARE_FIELDS = (
    "provider", "base_url", "model", "api_key", "owui_base_url",
    "gm_max_tokens", "persona_max_tokens",
)


def _cmd_read_matrix(env_path_a: Path, env_path_b: Path, fixture_path: Path) -> int:
    """I4.2: EIN frisches Leserkind -- liest BEIDE Fixtures mit den ECHTEN
    `setup.resolve_model_provider`/`launcher.resolve_model_provider_
    choice`-Resolvern (kein geteilter Modulzustand mit `write-matrix`,
    eigener Interpreter) und vergleicht INTERN alle sieben Felder gegen
    die private Fixture -- druckt NUR boolesche Ergebnisse, NIE Werte."""
    mods = _product_modules()
    setup_mod = mods["setup_mod"]
    launcher_mod = mods["launcher_mod"]

    fixture = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
    expected_a = {
        "provider": "local",
        "base_url": fixture["base_url"], "model": fixture["model"], "api_key": fixture["api_key"],
        "owui_base_url": fixture.get("owui_base_url"),
        "gm_max_tokens": fixture.get("gm_max_tokens", 4096),
        "persona_max_tokens": fixture.get("persona_max_tokens", 400),
    }

    overall_ok = True
    for resolver_name, resolver in (
        ("setup", setup_mod.resolve_model_provider),
        ("launcher", launcher_mod.resolve_model_provider_choice),
    ):
        # A: erwarteter Erfolg, exakte Feldgleichheit bei allen sieben Feldern.
        provider_a, profile_a, _reason_a = resolver(env_path_a)
        matches = {}
        for field in _COMPARE_FIELDS:
            if field == "provider":
                matches[field] = (provider_a == expected_a["provider"])
            else:
                actual = getattr(profile_a, field, None) if profile_a is not None else None
                matches[field] = (actual == expected_a[field])
        all_match = all(matches.values())
        print(f"FIELD_MATCH_A_{resolver_name}:" + ",".join(f"{k}={v}" for k, v in matches.items()))
        print(f"ALL_MATCH_A_{resolver_name}:{all_match}")
        overall_ok = overall_ok and all_match

        # B: haltender Zustand, Pending bleibt (kein Erfolgsdouble).
        provider_b, profile_b, _reason_b = resolver(env_path_b)
        is_hold = (provider_b == "hold" and profile_b is None)
        print(f"HOLD_B_{resolver_name}:{is_hold}")
        overall_ok = overall_ok and is_hold

    return 0 if overall_ok else 1


def _extract_context_arg(argv: list) -> tuple:
    if "--context" in argv:
        idx = argv.index("--context")
        context_path = argv[idx + 1]
        return argv[:idx], context_path
    return argv, None


def main(argv: list) -> int:
    argv, context_path = _extract_context_arg(argv)
    guard = None
    context = None
    if context_path:
        context = json.loads(Path(context_path).read_text(encoding="utf-8"))
        guard = bootstrap_isolation(context=context)
        guard.export_phase("before", context["export_before_path"], completion_status="running")

    try:
        if len(argv) < 2:
            print(
                "usage: _local_tokenhost_support_2026_11_14.py "
                "write-matrix <env_a> <env_b> <fixture_path> [--context <p>] | "
                "read-matrix <env_a> <env_b> <fixture_path> [--context <p>]",
                file=sys.stderr,
            )
            rc = 2
        else:
            cmd = argv[1]
            if cmd == "write-matrix":
                if len(argv) != 5:
                    print("usage: ... write-matrix <env_a> <env_b> <fixture_path>", file=sys.stderr)
                    rc = 2
                else:
                    rc = _cmd_write_matrix(Path(argv[2]), Path(argv[3]), Path(argv[4]))
            elif cmd == "read-matrix":
                if len(argv) != 5:
                    print("usage: ... read-matrix <env_a> <env_b> <fixture_path>", file=sys.stderr)
                    rc = 2
                else:
                    rc = _cmd_read_matrix(Path(argv[2]), Path(argv[3]), Path(argv[4]))
            else:
                print(f"unbekanntes Kommando: {cmd!r}", file=sys.stderr)
                rc = 2

        if guard is not None:
            guard.export_phase(
                "after", context["export_after_path"],
                completion_status="completed" if rc == 0 else "failed",
            )
        return rc
    except Exception:
        if guard is not None:
            try:
                guard.export_phase("after", context["export_after_path"], completion_status="export_error")
            except Exception:
                pass
        raise


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
