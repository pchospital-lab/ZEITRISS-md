#!/usr/bin/env python3
"""
mmo_sim/core/recovery_ops.py — Operator-Recovery-Faehigkeiten R-P3/R-P5
(ZR-RECOVERY-OFFLINE-20261015-R1, 03_RECOVERY_VERTRAG.md). NEUE, additive
Datei -- kein bestehendes Verhalten wird hier ersetzt.

Zwei getrennte, NICHT atomar gekoppelte Operatoraktionen (03 §Haltbarkeit:
"P3/P5 sind nicht atomar gekoppelt"):

  R-P3 (`P3_CLASSIFY_UNKNOWN_KEEP_LEDGER_BLOCKED`): persistiert einen
  ADDITIVEN Auditdatensatz fuer einen Requestdatensatz mit unbekanntem
  Ausgang (`state="sent"`, nie beantwortet) -- der Originalrequest, seine
  Reservierung und `open_requests()` bleiben byte-unveraendert. Das ist
  KEIN Requestabschluss (niemals `accounted`/`finish_received`/
  `finish_error`/Refund/Resend).

  R-P5 (`P5_AUTHORIZE_SINGLE_SYNTHETIC_EXTRA_ATTEMPT`): persistiert eine
  GEBUNDENE Einmalautorisierung (`allowance=1`) fuer EINEN bestehenden
  `save_corrections`-Datensatz mit `state="hold"`,
  `last_reason="unjustified_semantic_drift"`, `attempts_used=1`. Die
  Autorisierung selbst startet KEINEN Request und adoptiert KEINEN Save --
  sie wird von `core.save_correction.pursue_single_figure_correction`
  gezielt erkannt und hoechstens EINMAL verbraucht (s. dort,
  `try_consume_p5_allowance` unten).

Beide Aktionen:
  * `inspect`/`plan` sind REIN LESEND (kein Verzeichnis-/Lockfile-Write als
    Nebenwirkung) -- Planbindung an Zielidentitaet, Vorzustandshash, Wirkung.
  * `apply` ist eine bewusste, einzeln freigegebene Operatoraktion, die
    SELBST keine Inferenz ausloest; sie liest Plan->Apply frisch von Platte
    unter echter Schreiber-Exklusivitaet (derselbe `fcntl.flock` auf
    `lab.lock.json`, den `mmo_sim.lab.runner.LabRunner` bereits verwendet --
    KEIN zweiter, unbeachteter Lockmechanismus) und ist NUR auf
    ausdruecklich als synthetischer Testroot markierten `run_dir`s erlaubt
    (Markerdatei `RECOVERY_SYNTHETIC_TEST_ROOT`, s. `_require_synthetic_
    root`). Ein lokaler Hash schuetzt die Bindung zwischen Plan und Apply,
    NICHT gegen einen bereits schreibberechtigten Angreifer -- das ehrliche
    Vertrauensmodell steht in `OPERATOR.md`.

Idempotenz: ein wiederholter `apply` mit IDENTISCHEN gebundenen Feldern
(Zielidentitaet, Vorzustandshash, Operatorentscheidung/Grund/Beleg) ist ein
No-op (keine weiteren Wirkungen/Events). Ein `apply` mit ANDERER
Entscheidung oder veraendertem Vorzustand fuer dieselbe Operation ist ein
kontrollierter Konflikt (`RecoveryConflictError`), NIE ein stilles
Ueberschreiben."""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import stat
import time
import uuid
from pathlib import Path

from . import request_ledger
from . import save_correction as _save_correction
from .admission import _atomic_write_json

#: 03_RECOVERY_VERTRAG.md §R-P3/§R-P5 -- exakte Aktionskennungen, auch im
#: persistierten Auditdatensatz/der Autorisierung gebunden.
P3_ACTION = "P3_CLASSIFY_UNKNOWN_KEEP_LEDGER_BLOCKED"
P5_ACTION = "P5_AUTHORIZE_SINGLE_SYNTHETIC_EXTRA_ATTEMPT"

#: Die EINZIGE Fallklasse, fuer die R-P5 ueberhaupt in Betracht kommt (03
#: §R-P5: "Nur ein bestehender hold-Record mit reason=unjustified_semantic_
#: drift ... attempts_used=1").
P5_REQUIRED_REASON = "unjustified_semantic_drift"
P5_REQUIRED_ATTEMPTS_USED = 1
P5_ALLOWANCE = 1

#: Markerdatei-Name -- deren Anwesenheit unter dem (aufgeloesten) `run_dir`
#: ist der EINZIGE Zulassungsnachweis fuer `apply_*` (s. Moduldocstring).
#: Ein echter LA1/P3/P5/W78/W72-Root traegt diese Datei nie automatisch.
SYNTHETIC_ROOT_MARKER = "RECOVERY_SYNTHETIC_TEST_ROOT"


class RecoveryError(RuntimeError):
    """Gemeinsame Basisklasse aller kontrolliert abgelehnten Recovery-
    Aufrufe -- NIE ein stiller Erfolg/No-op fuer einen fehlerhaften/
    unklaren/unberechtigten Aufruf (fail-closed, analog `request_ledger.
    IndeterminateRequestRecordError`)."""


class RecoveryUnsafeRootError(RecoveryError):
    """`run_dir` ist kein sicherer, ausdruecklich als synthetischer Testroot
    markierter Pfad (abs./../Symlink/fehlende Markerdatei)."""


class RecoveryUnsafeIdentityError(RecoveryError):
    """Ein vom Aufrufer uebergebenes Identitaetsfeld (z.B. `repair_key`)
    enthaelt ein Pfad-Trickmuster (Separator/`..`/Nullbyte) -- wird NIE
    direkt als Dateinamensbestandteil verwendet (s. `_safe_file_token`)."""


class RecoveryTargetNotFoundError(RecoveryError):
    """Der referenzierte Requestdatensatz/Korrekturdatensatz existiert
    nicht unter diesem `run_dir`."""


class RecoveryNotEligibleError(RecoveryError):
    """Der referenzierte Datensatz erfuellt die fachliche Vorbedingung der
    jeweiligen Aktion nicht (z.B. kein `state=hold`/`reason=
    unjustified_semantic_drift`/`attempts_used=1` fuer R-P5, oder der
    Request ist bereits abgeschlossen/kein unbekannter Ausgang fuer R-P3)."""


class RecoveryPreconditionChangedError(RecoveryError):
    """Der zwischen `plan` und `apply` neu gelesene Vorzustand (Hash/
    Identitaet) stimmt nicht mehr mit dem urspruenglich geplanten ueberein
    -- kontrollierter Abbruch statt eines Apply auf veraltetem Plan."""


class RecoveryConflictError(RecoveryError):
    """Fuer dieselbe Operation existiert bereits ein Audit-/Grant-Datensatz
    mit ANDEREN gebundenen Feldern (andere Entscheidung/Grund/Beleg) --
    kontrollierter Konflikt statt eines stillen Ueberschreibens."""


class RecoveryExclusivityUnavailableError(RecoveryError):
    """Die echte, mit `mmo_sim.lab.runner.LabRunner` GETEILTE Schreiber-
    Exklusivitaet (`fcntl.flock` auf `lab.lock.json`) konnte nicht erworben
    werden -- ein anderer aktiver Controller (LabRunner ODER ein
    gleichzeitiger zweiter `apply`-Aufruf) haelt sie gerade. 03 §Haltbarkeit:
    'ohne gesicherte Exklusivitaet HOLD'."""


class RecoveryAuditUnreadableError(RecoveryError):
    """Eine vorhandene Recovery-Audit-/Grant-Datei ODER der referenzierte
    `save_corrections`-Datensatz ist vorhanden, aber nicht lesbar/parsebar
    oder strukturell widersspruechlich (Duplicate-Key/NaN/Bool-als-Zaehler)
    -- kontrollierte Sperre statt Behandlung als abwesend/gueltig (G2-
    Lesevertrag-Analogie, s. `request_ledger.IndeterminateRequestRecordError`)."""


class RecoveryMissingRunIdentityError(RecoveryError):
    """R2-N1-Fix (GENERALREVIEW.md §4 BIND, `p3_missing_run_id`): `apply_p3`/
    `apply_p5` lehnen eine fehlende/ungueltige Run-Identitaet (`run_binding.
    run_id is None`, s. `_run_binding`) ab, STATT mit `run_id: null` zu
    applizieren. `inspect`/`plan_*` duerfen die Abwesenheit weiterhin rein
    lesend MELDEN (`run_binding={"run_id": None, ...}` bleibt ein gueltiger
    Planinhalt) -- NUR `apply_*` selbst ist an dieser Stelle fail-closed,
    weil Apply die einzige Funktion mit tatsaechlicher Schreibwirkung ist."""


class RecoveryPlanRequiredError(RecoveryError):
    """R2-N1-Fix (CONTROL.json `core_plan_clarification`, GENERALREVIEW.md
    §4 BIND, `p3_plan_missing`): JEDER oeffentliche Mutations-Einstieg --
    `apply_p3`/`apply_p5` eingeschlossen, nicht nur die bereits an
    `--plan-file` gebundene CLI -- verlangt einen vom Aufrufer tatsaechlich
    GELIEFERTEN vorherigen `plan_p3`/`plan_p5`-Plan. `plan=None` plant
    NICHT mehr still intern neu und appliziert dann -- das ist jetzt eine
    kontrollierte Ablehnung VOR jeder Wirkung, kein stillschweigend
    umgangener Pflichtparameter (frueheres Verhalten/alte CLI-Quellen
    bleiben dabei unveraendert dokumentiert, s. Moduldocstring-Historie;
    diese Praezisierung gilt NEU und ausdruecklich auch fuer die Core-API)."""


# ─────────────────────────── Root-/Pfadsicherheit ───────────────────────────


def _validate_run_dir_path(run_dir) -> Path:
    """Inspect/Plan/Apply-gemeinsame Pfadpruefung (03 §Haltbarkeit: 'verweigert
    abs./../Symlink/...-Tricks, unklare Rootidentitaet ... vor Wirkung').
    Verlangt einen bereits ABSOLUTEN Pfad ohne `..`-Segmente, dessen
    aufgeloeste Form mit der uebergebenen Form identisch ist (kein
    Symlink-Umweg) -- reiner Lesecheck, kein Dateisystem-Write."""
    raw = Path(run_dir)
    if not raw.is_absolute():
        raise RecoveryUnsafeRootError(f"run_dir muss ein absoluter Pfad sein (erhalten: {run_dir!r}).")
    if ".." in raw.parts:
        raise RecoveryUnsafeRootError(f"run_dir darf kein '..'-Segment enthalten (erhalten: {run_dir!r}).")
    if raw.exists() and raw.is_symlink():
        raise RecoveryUnsafeRootError(f"run_dir selbst darf kein Symlink sein (erhalten: {run_dir!r}).")
    resolved = raw.resolve(strict=False)
    if raw.exists() and resolved != raw:
        raise RecoveryUnsafeRootError(
            f"run_dir {run_dir!r} loest ueber einen Symlink-Elternpfad zu einem anderen "
            f"Pfad auf ({resolved}) -- unklare Rootidentitaet, kontrollierte Ablehnung."
        )
    return resolved


def _safe_resolved_subpath(resolved_run_dir: Path, *parts: str) -> Path:
    """R2-PATH-LEASE-Fix (GENERALREVIEW.md §4: "`_validate_run_dir_path`
    prueft nur den Root selbst -- Unterpfade separat sicher behandeln").
    `_validate_run_dir_path` bindet nur `run_dir` selbst gegen einen
    Symlink-Elternpfad -- ein Unterpfad WIE `run/recovery` konnte bisher
    selbst ein Symlink auf ein fremdes Verzeichnis sein (Originalbeleg:
    `apply_p3` schrieb den Audit dann AUSSERHALB des freigegebenen Roots).
    Prueft deshalb JEDE Zwischenkomponente von `resolved_run_dir` abwaerts:
    existiert eine Komponente bereits, darf sie selbst KEIN Symlink sein,
    und ihre aufgeloeste Form muss weiterhin UNTER `resolved_run_dir`
    liegen. Eine noch nicht vorhandene Komponente (z.B. vor dem allerersten
    `apply_*` fuer dieses `run_dir`) ist unproblematisch -- sie existiert ja
    noch nicht, kann also noch keine Pfadumleitung SEIN; sie wird bei
    tatsaechlicher Anlage (`_ensure_parent_dir`/`mkdir`) regulaer unter dem
    Root neu erzeugt. Reiner Lesecheck, kein Dateisystem-Write."""
    current = resolved_run_dir
    for part in parts:
        current = current / part
        try:
            current_lstat = current.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(current_lstat.st_mode):
            raise RecoveryUnsafeRootError(
                f"{current} ist ein Symlink -- Unterpfade unterhalb des freigegebenen Roots "
                f"{resolved_run_dir} duerfen nicht per Symlink umgeleitet werden."
            )
        resolved_current = current.resolve(strict=False)
        try:
            resolved_current.relative_to(resolved_run_dir)
        except ValueError:
            raise RecoveryUnsafeRootError(
                f"{current} loest zu einem Pfad ausserhalb des freigegebenen Roots "
                f"{resolved_run_dir} auf ({resolved_current}) -- kontrollierte Ablehnung."
            ) from None
    return current


def _require_synthetic_root(resolved_run_dir: Path) -> None:
    """NUR fuer `apply_*` (03 §Haltbarkeit: 'Apply NUR auf ausdruecklich
    kuenstlich erzeugten Testroots'). Die Markerdatei ist der EINZIGE
    Zulassungsnachweis -- kein Pfadmuster-Raten, kein automatisches
    Erkennen 'sieht nach Test aus'. Ein echter LA1/P3/P5-Root traegt diese
    Datei nie, solange niemand sie dort bewusst anlegt."""
    marker = resolved_run_dir / SYNTHETIC_ROOT_MARKER
    # R2-N1-Fix (GENERALREVIEW.md §4 PATH/LEASE, `p3_marker_symlink`):
    # `Path.is_file()` FOLGT Symlinks -- ein symlinked Markername (Ziel ein
    # beliebiges fremdes reguläres File) wurde bisher als gueltiger
    # synthetischer Nachweis akzeptiert. `os.lstat` prueft den
    # Verzeichniseintrag SELBST, VOR jeder Dereferenzierung -- derselbe
    # Mechanismus wie bereits `_read_strict_json_file` fuer Audit-/
    # Grant-/Planziele; kein synthetischer Nachweis ueber einen
    # symlinked Marker, kein Lesen fremder Referenzdaten per Symlink.
    try:
        marker_lstat = marker.lstat()
    except FileNotFoundError:
        marker_lstat = None
    except OSError as exc:
        raise RecoveryUnsafeRootError(f"{marker}: lstat fehlgeschlagen ({exc}).") from exc
    if marker_lstat is None:
        raise RecoveryUnsafeRootError(
            f"run_dir {resolved_run_dir} ist nicht als synthetischer Testroot markiert "
            f"(fehlende Markerdatei {marker}) -- Apply ist ausschliesslich auf ausdruecklich "
            "kuenstlich erzeugten Testroots erlaubt (03_RECOVERY_VERTRAG.md §Haltbarkeit); "
            "ein testweise frischer Root ist dadurch noch keine neue spielbare LA1-Identitaet, "
            "aber ein echter Root wird ohne diese bewusste Markierung NIE automatisch zugelassen."
        )
    if stat.S_ISLNK(marker_lstat.st_mode):
        raise RecoveryUnsafeRootError(
            f"{marker} ist ein Symlink -- kein synthetischer Nachweis ueber einen symlinked "
            "Marker (R2-N1-Fix p3_marker_symlink); die Markerdatei selbst muss eine reguläre "
            "Datei UNTER dem freigegebenen run_dir sein."
        )
    if not stat.S_ISREG(marker_lstat.st_mode):
        raise RecoveryUnsafeRootError(
            f"{marker} ist keine reguläre Datei (z.B. FIFO/Device/Verzeichnis) -- kein "
            "gueltiger synthetischer Testroot-Nachweis."
        )


def _safe_file_token(value: str, *, label: str) -> str:
    """Identitaetsfelder, die DIREKT in einen neuen Dateinamen einfliessen
    (z.B. `repair_key` fuer den P5-Grant-Pfad), werden hier GEPRUEFT statt
    wie `save_correction._record_path` nur per `.replace('/', '_')`
    entschaerft -- ein Pfadseparator/`..`/Nullbyte in einem vom Aufrufer
    (CLI-Argument) stammenden Identitaetsfeld wird kontrolliert ABGELEHNT
    (malformed_paths_json_counters_rejected), nicht stillschweigend
    ersetzt."""
    if not isinstance(value, str) or not value:
        raise RecoveryUnsafeIdentityError(f"{label} muss ein nichtleerer String sein (erhalten: {value!r}).")
    if "/" in value or "\\" in value or "\x00" in value or ".." in value:
        raise RecoveryUnsafeIdentityError(
            f"{label} enthaelt ein Pfad-Trickmuster (Separator/'..'/Nullbyte) und wird nicht "
            f"als Dateinamensbestandteil akzeptiert (erhalten: {value!r})."
        )
    return value


def _hash_key(*parts: object) -> str:
    """Kollisionssicherer, pfadinjektionsfreier Dateiname fuer additive
    Recovery-Datensaetze (P3-Audit) -- bindet die VOLLE logische
    Operationsidentitaet + request_id ueber einen Hash, UNABHAENGIG vom
    tatsaechlichen Zeichenvorrat der einzelnen Felder (keine `/`-/`..`-
    Pruefung je Feld noetig, der Hash neutralisiert jedes Trickmuster)."""
    raw = json.dumps(parts, ensure_ascii=True, sort_keys=False, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ─────────────────────────── Strikte JSON-Reads ─────────────────────────────


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    seen: dict = {}
    for key, value in pairs:
        if key in seen:
            raise RecoveryAuditUnreadableError(
                f"doppelter JSON-Schluessel {key!r} im selben Objekt -- nicht eindeutig "
                "einordenbar (malformed_paths_json_counters_rejected)."
            )
        seen[key] = value
    return seen


def _reject_constant(name: str) -> None:
    """`json.loads` akzeptiert standardmaessig die NICHT-Standard-Literale
    `NaN`/`Infinity`/`-Infinity` -- fuer einen Recovery-Zaehler/-Datensatz
    ist das NIE ein gueltiger Wert (G2-Analogie: ein Zaehler ist entweder
    eine echte endliche Zahl oder fehlt; `NaN` ist widerspruechlich)."""
    raise RecoveryAuditUnreadableError(
        f"JSON-Konstante {name!r} ist in einem Recovery-/Korrekturdatensatz nicht zulaessig "
        "(malformed_paths_json_counters_rejected)."
    )


def _strict_json_loads(raw: str) -> object:
    try:
        return json.loads(raw, object_pairs_hook=_reject_duplicate_keys, parse_constant=_reject_constant)
    except RecoveryAuditUnreadableError:
        raise
    except (ValueError,) as exc:
        raise RecoveryAuditUnreadableError(f"JSON nicht lesbar/parsebar ({exc}).") from exc


def _is_int_not_bool(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _read_strict_json_file(path: Path) -> dict | None:
    """`None` NUR fuer eine echte, initial abwesende Datei. Eine vorhandene,
    aber nicht lesbare/parsebare/strukturell widerspruechliche Datei
    propagiert `RecoveryAuditUnreadableError` -- NIE als abwesend
    missgedeutet (G2-Analogie).

    R2-PATH-LEASE-Fix (GENERALREVIEW.md §4, "abwesend/unlesbar/nichtregulaer/
    symlinked/korrupt strikt trennen"): `Path.is_file()` FOLGT Symlinks --
    ein symlinked Pfad (z.B. ein Audit-/Grant-/Lock-/Markerziel, das per
    Symlink in ein fremdes Verzeichnis umgeleitet wurde) wurde zuvor
    stillschweigend ALS wäre es die reguläre Zieldatei gelesen. `os.lstat`
    (NICHT `os.stat`) prueft den Verzeichniseintrag selbst, BEVOR irgendein
    `open`/`read_text` ausgeloest wird -- ein Symlink wird dadurch kontrolliert
    ABGELEHNT statt dereferenziert, UND ein nichtregulaerer Eintrag (FIFO/
    Device/Verzeichnis) wird VOR jedem `open` erkannt (kein blockierendes
    Oeffnen einer FIFO ohne Schreiber)."""
    try:
        st = path.lstat()
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise RecoveryAuditUnreadableError(f"{path}: lstat fehlgeschlagen ({exc}).") from exc
    if stat.S_ISLNK(st.st_mode):
        raise RecoveryAuditUnreadableError(
            f"{path} ist ein Symlink -- wird kontrolliert abgelehnt statt dereferenziert "
            "(Pfadumleitungsschutz, malformed_paths_json_counters_rejected)."
        )
    if not stat.S_ISREG(st.st_mode):
        raise RecoveryAuditUnreadableError(
            f"{path} ist keine reguläre Datei (z.B. FIFO/Device/Verzeichnis) -- wird nicht "
            "geoeffnet (vermeidet u.a. eine blockierende FIFO-Oeffnung ohne Schreiber)."
        )
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RecoveryAuditUnreadableError(f"{path} vorhanden, aber nicht lesbar ({exc}).") from exc
    data = _strict_json_loads(raw)
    if not isinstance(data, dict):
        raise RecoveryAuditUnreadableError(f"{path}: Inhalt ist kein JSON-Objekt.")
    return data


def _read_save_correction_record_strict(run_dir, repair_key_token: str) -> dict | None:
    """Liest GENAU dieselbe Datei wie `core.save_correction.load_record`
    (`save_correction._record_path`), aber mit der strikten G2-artigen
    Lesedisziplin (Duplicate-Key/NaN zurueckgewiesen, Pflichtfelder
    typgeprueft) -- `save_correction.load_record` selbst bleibt
    UNVERAENDERT (kein Eingriff in dessen bestehenden, von vielen Tests
    gepruften Lesevertrag; diese Funktion ist eine reine Recovery-interne
    Zusatzpruefung VOR jeder Wirkung).

    R2-PATH-LEASE-Fix: `_safe_resolved_subpath` validiert den `save_corrections`-
    Unterpfad/die Zieldatei GEGEN eine Symlink-Umleitung, BEVOR
    `save_correction._record_path`/`_records_dir` (dessen `mkdir(exist_ok=True)`
    eine bereits existierende, aber UNSICHERE Zwischenkomponente still
    akzeptieren wuerde) ueberhaupt aufgerufen wird -- diese Pruefung bleibt
    rein lesend (lstat/resolve, kein Write) und erfolgt VOR jedem Nebeneffekt
    von `_record_path`."""
    resolved = _validate_run_dir_path(run_dir)
    _safe_resolved_subpath(resolved, "save_corrections", f"{repair_key_token}.json")
    path = _save_correction._record_path(resolved, repair_key_token)
    data = _read_strict_json_file(path)
    if data is None:
        return None
    required_str = ("repair_key", "persona_key", "char_id", "operation_key", "state")
    for key in required_str:
        if not isinstance(data.get(key), str):
            raise RecoveryAuditUnreadableError(
                f"save_corrections-Datensatz {path.name!r}: Pflichtfeld {key!r} fehlt/falscher Typ."
            )
    for key in ("table_id", "section_id", "last_reason"):
        if key in data and data[key] is not None and not isinstance(data[key], str):
            raise RecoveryAuditUnreadableError(
                f"save_corrections-Datensatz {path.name!r}: Feld {key!r} hat einen unzulaessigen Typ."
            )
    attempts_used = data.get("attempts_used")
    if not _is_int_not_bool(attempts_used):
        raise RecoveryAuditUnreadableError(
            f"save_corrections-Datensatz {path.name!r}: 'attempts_used' ({attempts_used!r}) ist kein "
            "gueltiger Zaehler (kein int oder bool-als-Zaehler) -- malformed_paths_json_counters_rejected."
        )
    return data


# ───────────────────────── Geteilte Schreiber-Exklusivitaet ─────────────────


def _lab_lock_path(run_dir) -> Path:
    """DIESELBE Datei, die `mmo_sim.lab.runner.LabRunner._acquire_lock`
    bereits als massgebliche `fcntl.flock`-Autoritaet verwendet (s. dortigen
    Docstring: 'eine stabile Lock-fd mit fcntl.flock(LOCK_EX|LOCK_NB) als
    MASSGEBLICHE Autoritaet') -- bewusst DIESELBE Konstante, kein zweiter,
    unbeachteter Lockpfad.

    R2-PATH-LEASE-Fix: `_safe_resolved_subpath` lehnt einen per Symlink
    umgeleiteten `lab.lock.json`-Eintrag ab, statt ihn stillschweigend zu
    dereferenzieren."""
    return _safe_resolved_subpath(Path(run_dir), "lab.lock.json")


class _SharedWriterExclusivity:
    """Erwirbt NICHT-BLOCKIEREND denselben OS-Lock wie ein aktiver
    `LabRunner` fuer die Dauer EINES `apply_*`-Aufrufs -- belegt/prueft
    NUR, dass gerade kein anderer Controller (LabRunner ODER ein
    gleichzeitiger zweiter Recovery-`apply`) exklusiv schreibt, und gibt
    ihn danach sofort wieder frei (Recovery ist keine Dauerbesitzrolle wie
    ein Lab-Lauf). Schlaegt der Erwerb fehl, ist das der einzig zulaessige
    Ausgang `RecoveryExclusivityUnavailableError` -- NIE ein stiller
    Weiterbetrieb ohne Exklusivitaet (03 §Haltbarkeit: 'ohne gesicherte
    Exklusivitaet HOLD').

    Rework-Fix (writer_exclusivity_unlink_race, Critic-Beleg
    `race_labrunner_sim.py`/`race_recovery_acquire.py`) -- ZWEI Teile, nicht nur
    einer, weil der zuerst nahegelegte alleinige Inode-Recheck sich bei echter
    Zweiprozess-Nachstellung (A haelt flock auf der UNLINKTEN alten Inode,
    B eroeffnet per `O_CREAT` eine KOMPLETT NEUE Inode am selben Pfad) als
    WIRKUNGSLOS erwiesen hat: `fcntl.flock` ist strikt PRO-INODE, nicht
    pro-Pfad (mit einem minimalen Zweiprozess-Primitivtest unabhaengig
    verifiziert) -- B's eigene fd matcht nach `os.open`+`flock` trivial IMMER
    den von B selbst gerade erst angelegten Pfad-Eintrag, unabhaengig davon,
    wie lange A's eigentlich schon unlinkte, aber noch geflockte alte Inode
    noch offen bleibt. Ein alleiniger `_fd_still_matches_path()`-Nachcheck
    (wie in `mmo_sim.lab.runner.LabRunner._acquire_lock`) schliesst NUR die
    ENGERE Drei-Prozess-Variante (ein ANDERER dritter Racer ersetzt den Pfad
    zwischen UNSEREM `os.open` und UNSEREM `flock`) -- nicht die hier
    belegte Zwei-Prozess-Variante (ein ausgehender `LabRunner` haelt seinen
    eigenen flock noch auf der bereits unlinkten alten Inode, WAEHREND wir
    ganz regulaer eine neue Inode am selben, nun leeren Pfad anlegen).

    Teil 1 -- `_fd_still_matches_path()` (1:1 aus dem Runner gespiegelt,
    `st_dev`/`st_ino`-Abgleich): nach jedem `flock`-Erwerb verifizieren, dass
    die offene fd noch dem AKTUELLEN Pfadeintrag entspricht; bei Abweichung
    (ein DRITTER Racer hat uns den Pfad unter der Hand ausgetauscht) die fd
    verwerfen und den gesamten Erwerb neu versuchen. Deckt die Drei-Prozess-
    Variante vollstaendig ab, identische Semantik wie im Runner.

    Teil 2 -- `_UNLINK_RACE_SETTLE_SECONDS` (NICHT im Runner vorhanden, hier
    noetig, weil Teil 1 die belegte Zwei-Prozess-Variante nicht schliesst):
    wird der Lock-Pfad bei ERWERBSBEGINN als (noch) nicht vorhanden
    beobachtet -- der Fall, in dem ein ausgehender `LabRunner` ihn gerade
    unlinkt haben KOENNTE, waehrend er seinen eigenen flock noch haelt --
    wird vor dem eigentlichen `os.open`/`flock`-Versuch eine KURZE, FESTE
    Wartezeit eingelegt, bevor der (dann fast immer weiterhin leere) Pfad
    als Freiwerb behandelt wird. Das reale Zeitfenster zwischen dem
    `unlink()` und dem eigenen `flock(LOCK_UN)` in `LabRunner.release()` ist
    laut dessen Docstring "ein paar CPU-Instruktionen" (Mikrosekunden-
    Groessenordnung); `_UNLINK_RACE_SETTLE_SECONDS` liegt um Groessenordnungen
    darueber und verschiebt den tatsaechlichen Vergabezeitpunkt zuverlaessig
    HINTER den realen Freigabezeitpunkt des ausgehenden `LabRunner` (mit
    echten Zweiprozess-Laeufen verifiziert, s. `test_writer_race_single_
    winner`). Das ist eine GRENZWERTIGE, keine ABSOLUTE Garantie: ein
    KUENSTLICH (nicht realistisch) ueber `_UNLINK_RACE_SETTLE_SECONDS`
    hinaus verbreitertes Fenster waere weiterhin nicht geschlossen -- das
    waere nur durch eine Reihenfolgeaenderung in `LabRunner.release()`
    selbst (`flock(LOCK_UN)` VOR statt NACH dem `unlink`) strukturell
    vollstaendig loesbar, was ausserhalb dieses engen Fixes liegt (B bleibt
    pristine). Beide Teile zusammen bleiben beim selben Mechanismus (derselbe
    `fcntl.flock` auf `lab.lock.json`, kein Zweitlock, keine neue Lock-Datei)
    und beim selben vertraglich einzig zulaessigen Fehlausgang: kontrolliertes
    `RecoveryExclusivityUnavailableError` (HOLD), NIE stiller Weiterbetrieb
    mit einer veralteten fd."""

    _MAX_ACQUIRE_ATTEMPTS = 50
    # S. Docstring Teil 2: grosszuegiges Vielfaches der laut Runner-Docstring
    # realen "paar CPU-Instruktionen" zwischen `unlink()` und `flock(LOCK_UN)`
    # in `LabRunner.release()` -- schliesst das realistische Zeitfenster,
    # ohne jeden Freiwerb messbar zu verlangsamen.
    _UNLINK_RACE_SETTLE_SECONDS = 0.05

    def __init__(self, run_dir):
        self._path = _lab_lock_path(run_dir)
        self._fd: int | None = None

    def __enter__(self) -> "_SharedWriterExclusivity":
        self._path.parent.mkdir(parents=True, exist_ok=True)
        for _attempt in range(self._MAX_ACQUIRE_ATTEMPTS):
            if not self._path.exists():
                # Teil 2: der Pfad ist gerade (noch) nicht da -- entweder
                # echter Erstgebrauch, oder ein ausgehender LabRunner hat ihn
                # soeben unlinkt und haelt seinen eigenen flock noch auf der
                # jetzt geisterhaften alten Inode. Von hier aus nicht
                # unterscheidbar -- kurz warten, DANN erst den (fast immer
                # weiterhin leeren) Pfad als Freiwerb behandeln.
                time.sleep(self._UNLINK_RACE_SETTLE_SECONDS)
            fd = os.open(self._path, os.O_CREAT | os.O_RDWR, 0o644)
            # R2-PATH-LEASE-Fix (GENERALREVIEW.md §4, "Erwerb UND jeder
            # Fehlerausgang inkl. OSError/BaseException vor fd-Uebergabe
            # muessen lokal aufraeumen"; Originalbeleg: "EIO beim Nach-
            # flock-Inodecheck liess im R1 die fd offen"). Vorher deckte NUR
            # der `flock`-Erwerb selbst einen eigenen Cleanup-Pfad ab; ein
            # `OSError` (z.B. EIO) ODER jede andere Ausnahme aus dem
            # NACHGELAGERTEN `_fd_still_matches_path`-Aufruf (`os.stat`/
            # `os.fstat`) propagierte UNGEFANGEN nach oben und liess die
            # bereits erworbene fd weder entsperrt noch geschlossen zurueck
            # -- ein fuer `__exit__` unerreichbarer, verwaister Lock. JETZT
            # steht die GESAMTE Spanne zwischen `os.open` und der
            # erfolgreichen Uebergabe an `self._fd` unter einem einzigen
            # `try`/`except BaseException`: jeder Fehlausgang entsperrt
            # (best-effort, falls der Lock ueberhaupt schon erworben wurde)
            # und schliesst die fd, DANN wird der echte Fehler als
            # `RecoveryExclusivityUnavailableError` (HOLD) bzw. unveraendert
            # weitergereicht. `continue` (Teil 1, siehe unten) ist keine
            # Ausnahme und verlaesst diesen Block unveraendert regulaer.
            flock_acquired = False
            try:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except OSError as exc:
                    raise RecoveryExclusivityUnavailableError(
                        f"Lab-Lock {self._path} ist aktiv belegt (vermutlich ein laufender "
                        f"LabRunner oder ein gleichzeitiger zweiter Recovery-apply) -- keine "
                        f"gesicherte Schreiber-Exklusivitaet, kontrolliertes HOLD statt eines "
                        f"ungesicherten Writes ({exc})."
                    ) from exc
                flock_acquired = True
                try:
                    matches = self._fd_still_matches_path(fd, self._path)
                except OSError as exc:
                    raise RecoveryExclusivityUnavailableError(
                        f"Lab-Lock {self._path}: Inode-Nachcheck nach flock-Erwerb fehlgeschlagen "
                        f"({exc}) -- keine gesicherte Schreiber-Exklusivitaet, kontrolliertes HOLD "
                        "statt eines ungesicherten Writes auf einer moeglicherweise veralteten fd."
                    ) from exc
                if not matches:
                    # Teil 1 (CRITIC-REPORT writer_exclusivity_unlink_race, Drei-
                    # Prozess-Variante): ein DRITTER Racer hat die Datei zwischen
                    # unserem os.open und unserem EIGENEN flock-Erwerb bereits
                    # unlinkt+neu angelegt -- unsere fd ist jetzt eine
                    # Geister-Inode. Verwerfen und den gesamten Erwerb neu
                    # versuchen, statt einer veralteten fd zu vertrauen.
                    fcntl.flock(fd, fcntl.LOCK_UN)
                    os.close(fd)
                    continue
                # R2-PATH-LEASE-Fix (GENERALREVIEW.md §4, "eine vorhandene
                # unklare/ungueltige Lease NICHT als frei behandeln";
                # Originalbeleg: "ein vorhandenes lab.lock.json mit
                # ungueltigem PID-Eintrag wird von Recovery als frei
                # behandelt"). `mmo_sim.lab.runner.LabRunner._acquire_lock`
                # validiert bei einer Reklamation bereits den VORHANDENEN
                # Inhalt (G3a: "unklare Lease kontrolliert halten, nicht als
                # frei ersetzen") -- diese Klasse tat das bisher NICHT, weil
                # sie selbst nie in die Datei schreibt und den Inhalt deshalb
                # schlicht ignorierte. Ein erfolgreicher `flock`-Erwerb
                # beweist nur, dass aktuell niemand den OS-Lock HAELT -- ein
                # VORHANDENER, aber strukturell unzuordenbarer Inhalt (z.B.
                # `{"pid": "invalid"}`) bleibt trotzdem eine unklare Lease,
                # kein Freiwerb. Eine tatsaechlich LEERE Datei ist nach
                # positiver Gegenkontrolle (GENERALREVIEW.md §4) weiterhin
                # KEIN Defekt -- nur eine NICHTLEERE, aber unparsebare/
                # strukturell ungueltige Nutzlast wird abgelehnt.
                raw = os.pread(fd, 1 << 16, 0)
                if raw.strip():
                    # R2-N1-Fix (GENERALREVIEW.md §4 PATH/LEASE,
                    # `p3_lease_missing_pid`): die vorherige Fassung verlangte
                    # nur "FALLS ein 'pid'-Schluessel vorhanden ist, muss er
                    # gueltig sein" -- eine nichtleere Lease OHNE jeden
                    # 'pid'-Schluessel ueberhaupt (z.B. `{}` oder eine JSON-
                    # Liste) rutschte dadurch als vermeintlich unproblematisch
                    # durch und wurde als frei behandelt. `mmo_sim.lab.runner.
                    # LabRunner._acquire_lock` verlangt dagegen UNBEDINGT einen
                    # gueltigen `int`-PID fuer JEDEN nichtleeren Inhalt (dessen
                    # `valid_pid`-Pruefung ist nicht an die Schluessel-
                    # Anwesenheit bedingt) -- dieselbe konservative Sicht wird
                    # hier jetzt uebernommen: nichtleerer Inhalt, der NICHT
                    # strikt {"pid": <echtes int, kein bool>, ...} ist (kein
                    # dict, kein 'pid'-Schluessel, falscher Typ, nicht
                    # dekodierbares JSON), bleibt UNKNOWN/HOLD -- NIE ein
                    # automatisches Behandeln als frei. Eine tatsaechlich
                    # LEERE Lockdatei (raw.strip() == b"") bleibt davon
                    # UNBERUEHRT weiterhin gueltig (positive Gegenkontrolle,
                    # GENERALREVIEW.md §4).
                    try:
                        existing_payload = json.loads(raw.decode("utf-8"))
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        existing_payload = None
                    owner_pid_valid = False
                    if isinstance(existing_payload, dict) and "pid" in existing_payload:
                        owner_pid = existing_payload.get("pid")
                        owner_pid_valid = isinstance(owner_pid, int) and not isinstance(owner_pid, bool)
                    if not owner_pid_valid:
                        raise RecoveryExclusivityUnavailableError(
                            f"Lab-Lock {self._path} hat einen vorhandenen, aber strukturell "
                            f"unklaren/unzuordenbaren Inhalt (kein eindeutiger gueltiger "
                            "Besitzer-PID) -- unklare Lease kontrolliert gehalten, kein "
                            "automatisches Behandeln als frei (G3a, dieselbe konservative "
                            "Sicht wie LabRunner._acquire_lock)."
                        )
                self._fd = fd
                return self
            except BaseException:
                if flock_acquired:
                    try:
                        fcntl.flock(fd, fcntl.LOCK_UN)
                    except OSError:
                        pass
                os.close(fd)
                raise
        raise RecoveryExclusivityUnavailableError(
            f"Lab-Lock {self._path} liefert nach {self._MAX_ACQUIRE_ATTEMPTS} Versuchen keinen "
            "stabilen Inode (wiederholte Unlink-waehrend-gehalten-Race durch einen gleichzeitigen "
            "LabRunner-Teardown) -- keine gesicherte Schreiber-Exklusivitaet, kontrolliertes HOLD "
            "statt eines ungesicherten Writes auf einer veralteten fd."
        )

    def __exit__(self, exc_type, exc, tb) -> None:
        # R2-N1-Fix (GENERALREVIEW.md §4 PATH/LEASE,
        # `release_unlock_error_closes_owned_fd`): ein injiziertes `OSError`
        # (z.B. EIO) direkt aus `fcntl.flock(..., LOCK_UN)` liess die eigene
        # fd bisher UNGESCHLOSSEN zurueck (die Exception propagierte, bevor
        # `os.close` erreicht wurde) -- ein gesunder Nachfolger blieb dadurch
        # blockiert, obwohl `apply_*` selbst bereits beendet war. `os.close`
        # steht jetzt in einem `finally`: die eigene fd wird IMMER
        # geschlossen, auch wenn `LOCK_UN` selbst eine Ausnahme wirft. Der
        # Primaerfehler aus `LOCK_UN` wird dabei NICHT verschluckt (kein
        # `try/except`, nur `try/finally`) -- er propagiert nach dem Close
        # unveraendert weiter, kein Scheinerfolg. Es werden ausschliesslich
        # die EIGENE, bereits erworbene fd geschlossen -- keine fremden
        # fds/Prozesse.
        if self._fd is not None:
            fd = self._fd
            self._fd = None
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)

    @staticmethod
    def _fd_still_matches_path(fd: int, path: Path) -> bool:
        """1:1 gespiegelt von `mmo_sim.lab.runner.LabRunner._fd_still_matches_path`
        (gleiche Semantik, gleicher Zweck): `st_dev`/`st_ino`-Abgleich zwischen der
        offenen fd und dem AKTUELLEN Pfadeintrag -- schliesst dieselbe Unlink-
        waehrend-flock-gehalten-Race wie im Runner (Inode-Identitaet statt Inhalt,
        da ein Inhaltsvergleich durch eine zufaellig identische neue Datei getaeuscht
        werden koennte, eine Inode-Identitaet nicht)."""
        try:
            path_stat = os.stat(path)
        except FileNotFoundError:
            return False
        fd_stat = os.fstat(fd)
        return (fd_stat.st_dev, fd_stat.st_ino) == (path_stat.st_dev, path_stat.st_ino)


# ───────────────────────────── Run-/Audit-Bindung ───────────────────────────


def _run_binding(resolved_run_dir: Path) -> dict:
    """REIN LESEND: liest `run_id.json` (von `core.store._run_id`
    geschrieben), falls bereits vorhanden -- ruft NIE `store._run_id`
    selbst auf (dessen Erstanlage-Zweig WUERDE die Datei schreiben, ein
    Nebenwrite, den `inspect`/`plan` nicht haben duerfen). Fehlt die Datei
    (noch kein echter Lauf/Store-Zugriff fuer dieses `run_dir`), bleibt
    `run_id` `None` -- kein erfundener Ersatzwert.

    R2-BIND-Fix (GENERALREVIEW.md §3, "`_run_binding()` akzeptiert
    Duplicate-Keys und nimmt fehlende/fehlerhafte Identitaet als `None`
    auf"): eine VORHANDENE `run_id.json` wird jetzt mit derselben strikten
    G2-artigen Lesedisziplin wie jeder andere Recovery-Datensatz gelesen
    (`_read_strict_json_file` -- Duplicate-Key/NaN/Symlink/nichtregulaer ->
    `RecoveryAuditUnreadableError`, NIE stillschweigend als `run_id=None`
    missgedeutet); ein fehlendes/leeres/typfalsches `run_id`-Feld in einer
    ANSONSTEN lesbaren Datei ist GENAUSO eine kontrollierte Sperre, kein
    `None`-Fallback. NUR eine tatsaechlich ABWESENDE Datei bleibt
    `run_id=None` (noch kein echter Lauf fuer dieses `run_dir`)."""
    p = _safe_resolved_subpath(resolved_run_dir, "run_id.json")
    data = _read_strict_json_file(p)
    if data is None:
        return {"run_dir": str(resolved_run_dir), "run_id": None}
    run_id = data.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        raise RecoveryAuditUnreadableError(
            f"{p}: Pflichtfeld 'run_id' fehlt/ist kein nichtleerer String (erhalten: {run_id!r}) "
            "-- kontrollierte Sperre statt eines erfundenen Ersatzwerts "
            "(malformed_paths_json_counters_rejected)."
        )
    return {"run_dir": str(resolved_run_dir), "run_id": run_id}


def _recovery_dir(run_dir) -> Path:
    """REIN LESEND -- erzeugt KEIN Verzeichnis. `inspect`/`plan_*` duerfen
    keinen Verzeichnis-Write als Nebenwirkung haben (s. Moduldocstring);
    nur `apply_*` legt ueber `_ensure_parent_dir` tatsaechlich an.

    R2-PATH-LEASE-Fix: `_safe_resolved_subpath` lehnt einen per Symlink
    umgeleiteten `recovery`-Unterpfad ab (Originalbeleg: `run/recovery ->
    <anderes Verzeichnis>`, `apply_p3` schrieb den Audit dadurch AUSSERHALB
    des freigegebenen Roots)."""
    return _safe_resolved_subpath(Path(run_dir), "recovery")


def _p3_audit_path(run_dir, audit_key: str) -> Path:
    """R2-PATH-LEASE-Fix: jede Zwischenkomponente (`recovery`, `p3_audits`,
    die Zieldatei selbst) wird einzeln gegen eine Symlink-Umleitung
    geprueft, nicht nur `recovery` ueber `_recovery_dir`."""
    return _safe_resolved_subpath(Path(run_dir), "recovery", "p3_audits", f"{audit_key}.json")


def _p5_grant_path(run_dir, repair_key_token: str) -> Path:
    """R2-PATH-LEASE-Fix: analog `_p3_audit_path` -- `recovery`, `p5_grants`
    UND die Zieldatei werden einzeln geprueft."""
    return _safe_resolved_subpath(Path(run_dir), "recovery", "p5_grants", f"{repair_key_token}.json")


def _ensure_parent_dir(path: Path) -> None:
    """NUR von `apply_p3`/`apply_p5` aufgerufen, unmittelbar VOR dem
    tatsaechlichen `_atomic_write_json`-Write -- erzeugt das Elternverzeichnis
    der additiven Recovery-Datei, falls es (beim allerersten Apply fuer
    dieses `run_dir`) noch nicht existiert."""
    path.parent.mkdir(parents=True, exist_ok=True)


def _bound_fields_equal(existing: dict, candidate: dict, *, bound_keys: tuple[str, ...]) -> bool:
    return all(existing.get(k) == candidate.get(k) for k in bound_keys)


# ═══════════════════════════════ R-P3 ═══════════════════════════════════════

#: Welche Felder die Idempotenz-/Konfliktpruefung fuer den P3-Audit bindet
#: (03 §R-P3: 'Andere Entscheidung oder veraenderter Vorzustand: kontrollierter
#: Konflikt'). `applied_ts`/`audit_id` sind bewusst NICHT gebunden -- ein
#: wiederholter identischer Apply darf einen neuen Zeitstempel/eine neue
#: `audit_id` tragen, ohne als Konflikt zu gelten (reine Beobachtungsmeta,
#: s. `apply_p3`-Idempotenzpfad).
#: R2-BIND-Fix (GENERALREVIEW.md §3, 04_NAECHSTER_BAU_R2.md "BIND"):
#: `run_binding`/`community_binding`/`generation_binding` sind JETZT Teil der
#: gebundenen Felder -- ein Audit mit identischer logischer Identitaet
#: (Tisch/Rolle/Turn/Teilnehmer/`request_id`) UND identischem Originalhash,
#: aber ANDEREM Run/Community/Generation, ist deshalb KEIN
#: `idempotent_noop` mehr (Originalbeleg: "ein vorhandener P3-Audit meldet
#: bei veraenderter Community/Generation idempotent_noop"), sondern ein
#: kontrollierter Konflikt (`RecoveryConflictError`).
_P3_BOUND_KEYS = (
    "action", "table_id", "section_id", "role", "turn_idx", "participant",
    "request_id", "original_file_sha256", "operator_decision", "reason", "evidence_ref",
    "run_binding", "community_binding", "generation_binding",
)


def _p3_identity(request: dict) -> tuple:
    return (
        request.get("table_id"), request.get("section_id"), request.get("role"),
        request.get("turn_idx"), request.get("participant"),
    )


def _is_unknown_outcome(request: dict) -> bool:
    """03 §R-P3: der Originalrequest ist 'sent/result_text=null/usage=null/
    settled_ts=null' -- tatsaechlich unbeantwortet, kein Transportfehler
    (`error`), keine bereits durable Antwort."""
    return (
        request.get("state") == "sent"
        and request.get("result_text") is None
        and request.get("usage") is None
        and request.get("settled_ts") is None
        and request.get("error") is None
    )


def plan_p3(
    run_dir, *, table_id, section_id, role, turn_idx, participant, request_id,
    community_binding: str | None = None, generation_binding: int | None = None,
) -> dict:
    """REIN LESEND. Liefert einen Plan, der die VOLLE Zielidentitaet, den
    Vorzustandshash der Originaldatei UND einen etwa schon vorhandenen
    Audit-Datensatz (fuer die Idempotenz-/Konfliktpruefung in `apply_p3`)
    bindet."""
    resolved = _validate_run_dir_path(run_dir)
    # R2-N1-Fix (GENERALREVIEW.md §4 PATH/LEASE, `p3_requests_symlink`):
    # `request_ledger._requests_dir` (`run_dir/requests`, `mkdir(exist_ok=
    # True)`) hat bisher KEINE eigene Symlink-Pruefung -- ein symlinked
    # `requests`-Unterbaum wurde dadurch stillschweigend dereferenziert statt
    # abgelehnt, bevor jeder nachfolgende Request-/P3-Lesezugriff. Dieselbe
    # bereits bestehende `_safe_resolved_subpath`-Pruefung (rein lesend,
    # KEIN Write) wie fuer `recovery`/den Marker wird deshalb jetzt AUCH
    # gegen den `requests`-Unterbaum selbst angewandt, VOR jedem Zugriff
    # ueber `request_ledger` -- nicht nur gegen das `recovery`-Verzeichnis.
    _safe_resolved_subpath(resolved, "requests")
    request = request_ledger.load_request(resolved, request_id)
    if request is None:
        raise RecoveryTargetNotFoundError(f"kein Requestdatensatz request_id={request_id!r} unter {resolved}.")
    identity = (table_id, section_id, role, turn_idx, participant)
    if _p3_identity(request) != identity:
        raise RecoveryNotEligibleError(
            f"Zielidentitaet {identity} passt nicht zum Requestdatensatz request_id={request_id!r} "
            f"(tatsaechlich {_p3_identity(request)}) -- kontrollierte Ablehnung VOR jeder Wirkung."
        )
    if not _is_unknown_outcome(request):
        raise RecoveryNotEligibleError(
            f"request_id={request_id!r} ist kein unbekannter Ausgang (state={request.get('state')!r}, "
            f"result_text={'gesetzt' if request.get('result_text') is not None else 'None'}, "
            f"error={request.get('error')!r}) -- R-P3 gilt ausdruecklich NUR fuer sent/unbeantwortet."
        )
    original_hash = _sha256_bytes(
        request_ledger._request_path(resolved, request_id).read_bytes()
    )
    audit_key = _hash_key("P3", *identity, request_id)
    existing_audit = _read_strict_json_file(_p3_audit_path(resolved, audit_key))
    return {
        "action": P3_ACTION, "audit_key": audit_key,
        "table_id": table_id, "section_id": section_id, "role": role,
        "turn_idx": turn_idx, "participant": participant, "request_id": request_id,
        "original_file_sha256": original_hash,
        "run_binding": _run_binding(resolved), "community_binding": community_binding,
        "generation_binding": generation_binding,
        "already_applied": existing_audit is not None,
        "existing_audit": existing_audit,
    }


def apply_p3(
    run_dir, *, table_id, section_id, role, turn_idx, participant, request_id,
    operator_decision: str, reason: str, evidence_ref: str,
    community_binding: str | None = None, generation_binding: int | None = None,
    plan: dict | None = None,
) -> dict:
    """Bewusste Operatoraktion. Liest Plan->Apply NEU unter echter
    Schreiber-Exklusivitaet (03 §Haltbarkeit) und schreibt GENAU EINEN
    additiven Auditdatensatz -- NIEMALS den Originalrequest. `operator_
    decision`/`reason`/`evidence_ref` sind PFLICHT (nichtleer) -- ein
    pauschales `reason='Flo'` ist laut Vertrag keine Rechtequelle, bleibt
    aber als Audit-Text zulaessig; die eigentliche Berechtigung ist der
    bewusste, explizit parametrisierte Aufruf selbst (s. OPERATOR.md)."""
    for label, value in (("operator_decision", operator_decision), ("reason", reason), ("evidence_ref", evidence_ref)):
        if not isinstance(value, str) or not value.strip():
            raise RecoveryError(f"{label} ist Pflicht und darf nicht leer sein.")
    # R2-N1-Fix (CONTROL.json `core_plan_clarification`, `p3_plan_missing`):
    # dieser oeffentliche Mutations-Einstieg appliziert NICHT mehr ohne einen
    # vom Aufrufer tatsaechlich gelieferten vorherigen Plan -- `plan=None`
    # ist jetzt eine kontrollierte Ablehnung VOR jeder Wirkung, kein stilles
    # internes Neuplanen+Anwenden. Die CLI (`lab/recovery_cli.py`) liefert
    # `plan` bereits IMMER (`--plan-file` ist dort Pflicht); nur die vorher
    # "optionale" Core-API wird hier jetzt konsistent dazu gemacht.
    if plan is None:
        raise RecoveryPlanRequiredError(
            "apply_p3 erfordert einen vom Aufrufer gelieferten vorherigen plan_p3(...)-Plan "
            "(core_plan_clarification) -- plan=None wird NICHT mehr stillschweigend neu "
            "geplant und angewandt."
        )
    resolved = _validate_run_dir_path(run_dir)
    _require_synthetic_root(resolved)
    with _SharedWriterExclusivity(resolved):
        fresh = plan_p3(
            resolved, table_id=table_id, section_id=section_id, role=role, turn_idx=turn_idx,
            participant=participant, request_id=request_id, community_binding=community_binding,
            generation_binding=generation_binding,
        )
        # R2-N1-Fix (`p3_missing_run_id`): Apply erzeugt KEINEN `run_id:null`-
        # Erfolg aus einer fehlenden/ungueltigen Run-Identitaet -- `inspect`/
        # `plan_p3` duerfen die Abwesenheit weiterhin rein lesend melden
        # (s. `_run_binding`), aber `apply_p3` selbst ist hier fail-closed.
        if fresh["run_binding"].get("run_id") is None:
            raise RecoveryMissingRunIdentityError(
                f"run_dir {resolved} hat keine lesbare run_id.json (run_binding.run_id ist "
                "None) -- apply_p3 appliziert NICHT mit einer fehlenden/ungueltigen Run-"
                "Identitaet (fail-closed)."
            )
        # R2-BIND-Fix (GENERALREVIEW.md §3): vorher wurden NUR `audit_key`/
        # `original_file_sha256` verglichen -- `run_binding`/`community_
        # binding`/`generation_binding` blieben voellig ungeprueft, obwohl
        # sie an `apply_p3` uebergeben werden. Originalbeleg: ein auf
        # Root/Run A, Community A/Generation 1 erstellter Plan wurde mit
        # identischen Requestbytes auf Root/Run B, Community B/Generation 2
        # erfolgreich appliziert, weil `audit_key`/`original_file_sha256`
        # (reine Funktionen der Requestbytes/Identitaet) bei einer
        # versehentlich kopierten/veralteten Quelle GLEICH bleiben koennen,
        # auch wenn Run/Community/Generation tatsaechlich abweichen. JETZT
        # wird die VOLLE im Plan gebundene Identitaet gegen die frisch von
        # Platte gelesene/vom Aufrufer tatsaechlich uebergebene verglichen.
        #
        # R2-N1-Fix (`p3_plan_wrong_action`): `plan.get("action")` war bisher
        # UEBERHAUPT NICHT Teil dieses Abgleichs -- ein vorgelegter Plan mit
        # einer FALSCHEN `action` (z.B. aus einem fremden Kontext kopiert,
        # aber mit zufaellig passendem `audit_key`/Hash/Bindungen) wurde
        # trotzdem appliziert, weil `action` selbst nie verglichen wurde.
        # `action` ist jetzt Teil derselben Vorzustandspruefung.
        if (
            plan.get("action") != fresh["action"]
            or plan.get("audit_key") != fresh["audit_key"]
            or plan.get("original_file_sha256") != fresh["original_file_sha256"]
            or plan.get("run_binding") != fresh["run_binding"]
            or plan.get("community_binding") != fresh["community_binding"]
            or plan.get("generation_binding") != fresh["generation_binding"]
        ):
            raise RecoveryPreconditionChangedError(
                "Der Vorzustand hat sich zwischen plan und apply veraendert (Requestdatei/"
                "Identitaet/Action/Run-/Community-/Generationbindung nicht mehr identisch) -- "
                "kontrollierter Abbruch statt Apply auf veraltetem oder fremdem Plan."
            )
        candidate = {
            "action": P3_ACTION, "audit_key": fresh["audit_key"],
            "table_id": table_id, "section_id": section_id, "role": role,
            "turn_idx": turn_idx, "participant": participant, "request_id": request_id,
            "original_file_sha256": fresh["original_file_sha256"],
            "run_binding": fresh["run_binding"], "community_binding": community_binding,
            "generation_binding": generation_binding,
            "operator_decision": operator_decision, "reason": reason, "evidence_ref": evidence_ref,
        }
        existing = fresh["existing_audit"]
        if existing is not None:
            if _bound_fields_equal(existing, candidate, bound_keys=_P3_BOUND_KEYS):
                return {"status": "idempotent_noop", "audit": existing}
            raise RecoveryConflictError(
                f"Fuer audit_key={fresh['audit_key']!r} existiert bereits ein Audit mit ANDEREN "
                "gebundenen Feldern (andere Entscheidung/Grund/Beleg oder veraenderter "
                "Vorzustand) -- kontrollierter Konflikt statt Ueberschreiben."
            )
        candidate["audit_id"] = uuid.uuid4().hex
        candidate["applied_ts"] = time.time()
        audit_path = _p3_audit_path(resolved, fresh["audit_key"])
        _ensure_parent_dir(audit_path)
        _atomic_write_json(audit_path, candidate)
        return {"status": "applied", "audit": candidate}


def list_p3_audits(run_dir) -> list[dict]:
    """REIN LESEND. Fuer `recovery inspect`/`status` -- die Original-
    requestdatensaetze selbst bleiben die Autoritaet fuer `open_requests()`;
    dies ist NUR eine Zusatzanzeige (03 §R-P3: 'Zusatzanzeige darf sie NICHT
    als erledigten Spielzug zaehlen')."""
    resolved = _validate_run_dir_path(run_dir)
    d = _recovery_dir(resolved) / "p3_audits"
    if not d.is_dir():
        return []
    return [_read_strict_json_file(p) for p in sorted(d.glob("*.json"))]


def inspect_p3_candidates(run_dir) -> list[dict]:
    """REIN LESEND: alle `open_requests()`-Datensaetze mit unbekanntem
    Ausgang (R-P3-Kandidaten), jeweils annotiert, ob bereits ein Audit
    existiert -- fuer `recovery inspect`."""
    resolved = _validate_run_dir_path(run_dir)
    # R2-N1-Fix (p3_requests_symlink): dieselbe Symlink-Pruefung wie in
    # `plan_p3` -- `inspect` ist eine eigene Lesestelle auf `requests`.
    _safe_resolved_subpath(resolved, "requests")
    audits_by_key = {a["audit_key"]: a for a in list_p3_audits(resolved) if a is not None}
    out = []
    for request in request_ledger.open_requests(resolved):
        if not _is_unknown_outcome(request):
            continue
        identity = _p3_identity(request)
        audit_key = _hash_key("P3", *identity, request.get("id"))
        out.append({
            "request_id": request.get("id"), "table_id": identity[0], "section_id": identity[1],
            "role": identity[2], "turn_idx": identity[3], "participant": identity[4],
            "audit_key": audit_key, "already_audited": audit_key in audits_by_key,
        })
    return out


# ═══════════════════════════════ R-P5 ═══════════════════════════════════════

#: R2-BIND-Fix (GENERALREVIEW.md §3): wie `_P3_BOUND_KEYS` -- `run_binding`/
#: `community_binding`/`generation_binding` sind jetzt gebunden, s. dort.
_P5_BOUND_KEYS = (
    "action", "repair_key", "persona_key", "char_id", "operation_key", "table_id", "section_id",
    "bound_attempts_used", "pre_state_sha256", "allowance", "operator_decision", "reason", "evidence_ref",
    "run_binding", "community_binding", "generation_binding",
)


def _p5_record_pre_state_hash(run_dir, repair_key_token: str) -> str:
    path = _save_correction._record_path(run_dir, repair_key_token)
    return _sha256_bytes(path.read_bytes())


def plan_p5(
    run_dir, *, repair_key: str, community_binding: str | None = None, generation_binding: int | None = None,
) -> dict:
    """REIN LESEND. `repair_key` ist dasselbe Schluesselformat wie
    `core.save_correction.load_or_init_record`/`domain.zeitriss.
    save_correction.creation_repair_key` -- wird hier NIE direkt als
    Dateinamensbestandteil ohne Pruefung verwendet (s. `_safe_file_token`).

    `generation_binding`: der Korrekturdatensatz selbst traegt bereits ein
    `generation`-Feld (`load_or_init_record(..., generation=...)`) -- DAS
    ist die Autoritaet, kein vom Operator unabhaengig behauptetes Feld.
    Uebergibt der Aufrufer `generation_binding` dennoch explizit, MUSS es
    mit dem gespeicherten Wert uebereinstimmen (sonst ein widerspruechliches
    Bindungsargument, kontrollierte Ablehnung statt stiller Uebernahme)."""
    resolved = _validate_run_dir_path(run_dir)
    token = _safe_file_token(repair_key, label="repair_key")
    record = _read_save_correction_record_strict(resolved, token)
    if record is None:
        raise RecoveryTargetNotFoundError(f"kein save_corrections-Datensatz repair_key={repair_key!r} unter {resolved}.")
    if record.get("state") != _save_correction.STATE_HOLD or record.get("last_reason") != P5_REQUIRED_REASON:
        raise RecoveryNotEligibleError(
            f"repair_key={repair_key!r}: state={record.get('state')!r}/last_reason="
            f"{record.get('last_reason')!r} -- R-P5 gilt ausdruecklich NUR fuer state='hold' mit "
            f"last_reason={P5_REQUIRED_REASON!r}."
        )
    if record.get("attempts_used") != P5_REQUIRED_ATTEMPTS_USED:
        raise RecoveryNotEligibleError(
            f"repair_key={repair_key!r}: attempts_used={record.get('attempts_used')!r} -- R-P5 gilt "
            f"ausdruecklich NUR fuer die bekannte Fallklasse attempts_used={P5_REQUIRED_ATTEMPTS_USED}."
        )
    record_generation = record.get("generation")
    if generation_binding is not None and generation_binding != record_generation:
        raise RecoveryError(
            f"generation_binding={generation_binding!r} widerspricht dem gespeicherten "
            f"'generation'-Feld ({record_generation!r}) des Korrekturdatensatzes -- kontrollierte "
            "Ablehnung statt eines unabhaengig behaupteten Bindungsarguments."
        )
    generation_binding = record_generation
    pre_hash = _p5_record_pre_state_hash(resolved, token)
    existing_grant = _read_strict_json_file(_p5_grant_path(resolved, token))
    return {
        "action": P5_ACTION, "repair_key": repair_key,
        "persona_key": record.get("persona_key"), "char_id": record.get("char_id"),
        "operation_key": record.get("operation_key"), "table_id": record.get("table_id"),
        "section_id": record.get("section_id"), "bound_attempts_used": P5_REQUIRED_ATTEMPTS_USED,
        "pre_state_sha256": pre_hash, "allowance": P5_ALLOWANCE,
        "run_binding": _run_binding(resolved), "community_binding": community_binding,
        "generation_binding": generation_binding,
        "already_applied": existing_grant is not None, "existing_grant": existing_grant,
    }


def apply_p5(
    run_dir, *, repair_key: str, operator_decision: str, reason: str, evidence_ref: str,
    community_binding: str | None = None, generation_binding: int | None = None, plan: dict | None = None,
) -> dict:
    """Bewusste Operatoraktion: persistiert GENAU EINE gebundene
    Einmalautorisierung (`allowance=1`, `consumed=False`). Startet KEINEN
    Request, adoptiert KEINEN Save. Kein Anheben von
    `save_correction.MAX_ADDITIONAL_REQUESTS`, kein Reset -- diese Funktion
    fasst `attempts_used`/den Korrekturdatensatz selbst NICHT an (das
    bleibt `core.save_correction.try_consume_p5_allowance` vorbehalten,
    aufgerufen aus dem bestehenden Korrekturpfad)."""
    for label, value in (("operator_decision", operator_decision), ("reason", reason), ("evidence_ref", evidence_ref)):
        if not isinstance(value, str) or not value.strip():
            raise RecoveryError(f"{label} ist Pflicht und darf nicht leer sein.")
    # R2-N1-Fix (CONTROL.json `core_plan_clarification`, `p3_plan_missing`,
    # analog `apply_p3`): plan=None appliziert NICHT mehr stillschweigend
    # neu geplant.
    if plan is None:
        raise RecoveryPlanRequiredError(
            "apply_p5 erfordert einen vom Aufrufer gelieferten vorherigen plan_p5(...)-Plan "
            "(core_plan_clarification) -- plan=None wird NICHT mehr stillschweigend neu "
            "geplant und angewandt."
        )
    resolved = _validate_run_dir_path(run_dir)
    _require_synthetic_root(resolved)
    token = _safe_file_token(repair_key, label="repair_key")
    with _SharedWriterExclusivity(resolved):
        fresh = plan_p5(
            resolved, repair_key=repair_key, community_binding=community_binding,
            generation_binding=generation_binding,
        )
        # R2-N1-Fix (`p3_missing_run_id`, analog `apply_p3`): Apply erzeugt
        # keinen `run_id:null`-Erfolg.
        if fresh["run_binding"].get("run_id") is None:
            raise RecoveryMissingRunIdentityError(
                f"run_dir {resolved} hat keine lesbare run_id.json (run_binding.run_id ist "
                "None) -- apply_p5 appliziert NICHT mit einer fehlenden/ungueltigen Run-"
                "Identitaet (fail-closed)."
            )
        # R2-BIND-Fix (GENERALREVIEW.md §3): analog `apply_p3` -- vorher
        # wurden NUR `repair_key`/`pre_state_sha256` verglichen; ein auf
        # einem anderen Root/Run bzw. unter anderer Community-/Generation-
        # bindung erstellter Plan wurde bei identischem Vorzustandshash
        # (z.B. einer versehentlich kopierten/veralteten Quelle) sonst
        # klaglos auf DIESEM `run_dir` appliziert. `action` ist jetzt
        # ebenfalls Teil des Abgleichs (analog `p3_plan_wrong_action`).
        if (
            plan.get("action") != fresh["action"]
            or plan.get("repair_key") != fresh["repair_key"]
            or plan.get("pre_state_sha256") != fresh["pre_state_sha256"]
            or plan.get("run_binding") != fresh["run_binding"]
            or plan.get("community_binding") != fresh["community_binding"]
            or plan.get("generation_binding") != fresh["generation_binding"]
        ):
            raise RecoveryPreconditionChangedError(
                "Der Korrekturdatensatz hat sich zwischen plan und apply veraendert, oder "
                "Action-/Run-/Community-/Generationbindung stimmen nicht mehr ueberein -- "
                "kontrollierter Abbruch statt Apply auf veraltetem oder fremdem Plan."
            )
        candidate = {
            "action": P5_ACTION, "repair_key": repair_key,
            "persona_key": fresh["persona_key"], "char_id": fresh["char_id"],
            "operation_key": fresh["operation_key"], "table_id": fresh["table_id"],
            "section_id": fresh["section_id"], "bound_attempts_used": fresh["bound_attempts_used"],
            "pre_state_sha256": fresh["pre_state_sha256"], "allowance": P5_ALLOWANCE,
            "run_binding": fresh["run_binding"], "community_binding": community_binding,
            "generation_binding": fresh["generation_binding"],
            "operator_decision": operator_decision, "reason": reason, "evidence_ref": evidence_ref,
        }
        existing = fresh["existing_grant"]
        if existing is not None:
            if _bound_fields_equal(existing, candidate, bound_keys=_P5_BOUND_KEYS):
                return {"status": "idempotent_noop", "grant": existing}
            raise RecoveryConflictError(
                f"Fuer repair_key={repair_key!r} existiert bereits eine Autorisierung mit ANDEREN "
                "gebundenen Feldern -- 'kein erneuter Grant an derselben gebundenen Fallentscheidung "
                "als Umgehung' (03 §R-P5)."
            )
        candidate["consumed"] = False
        candidate["consumed_ts"] = None
        candidate["grant_id"] = uuid.uuid4().hex
        candidate["granted_ts"] = time.time()
        grant_path = _p5_grant_path(resolved, token)
        _ensure_parent_dir(grant_path)
        _atomic_write_json(grant_path, candidate)
        return {"status": "applied", "grant": candidate}


def list_p5_grants(run_dir) -> list[dict]:
    resolved = _validate_run_dir_path(run_dir)
    d = _recovery_dir(resolved) / "p5_grants"
    if not d.is_dir():
        return []
    return [_read_strict_json_file(p) for p in sorted(d.glob("*.json"))]


def inspect_p5_candidates(run_dir) -> list[dict]:
    """REIN LESEND: alle `save_corrections/*.json`-Datensaetze (ohne die
    `_group_rounds`-Zaehlerdatei, s. `core.save_correction._round_counter_
    path`), die fachlich fuer R-P5 in Betracht kommen -- fuer `recovery
    inspect`."""
    resolved = _validate_run_dir_path(run_dir)
    d = Path(resolved) / "save_corrections"
    out = []
    if not d.is_dir():
        return out
    for p in sorted(d.glob("*.json")):
        try:
            record = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(record, dict):
            continue
        if record.get("state") != _save_correction.STATE_HOLD or record.get("last_reason") != P5_REQUIRED_REASON:
            continue
        if record.get("attempts_used") != P5_REQUIRED_ATTEMPTS_USED:
            continue
        repair_key = record.get("repair_key")
        if not isinstance(repair_key, str):
            continue
        grant = _read_strict_json_file(_p5_grant_path(resolved, repair_key))
        out.append({
            "repair_key": repair_key, "persona_key": record.get("persona_key"),
            "char_id": record.get("char_id"), "already_granted": grant is not None,
            "consumed": bool(grant.get("consumed")) if grant else None,
        })
    return out


def try_consume_p5_allowance(run_dir, *, repair_key: str, record: dict) -> bool:
    """Aufgerufen AUSSCHLIESSLICH aus `core.save_correction.pursue_single_
    figure_correction` fuer einen `record` mit `state=hold`/`last_reason=
    unjustified_semantic_drift`. Liefert `True`, wenn eine gebundene,
    passende Autorisierung existiert und der Aufrufer deshalb GENAU EINEN
    weiteren Slot (Slot 2) eroeffnen darf -- `False` sonst (der Aufrufer
    faellt dann auf die bestehende Resumierbarkeitspruefung zurueck).

    KEINE eigene `fcntl.flock`-Exklusivitaet hier: diese Funktion laeuft
    bereits innerhalb des bestehenden Einzelschreiber-pro-`run_dir`-
    Vertrags (derselbe, den jede andere Funktion in `save_correction.py`/
    `request_ledger.py` voraussetzt, s. deren Moduldocstrings) -- ein
    zweiter Lockerwerb AUS DEMSELBEN Prozess, der (als aktiver LabRunner)
    die Exklusivitaet bereits fuer die GESAMTE Laufdauer haelt, wuerde sich
    nur selbst blockieren (s. `lab.runner.LabRunner._acquire_lock`-
    Docstring: zwei fds auf dieselbe Datei sind bei `flock` NICHT derselbe
    Besitzer). Die Exklusivitaetspruefung bleibt `apply_p5` vorbehalten --
    DORT wird die Autorisierung ERST geschrieben, als bewusste, von jedem
    laufenden Controller UNABHAENGIGE Operatoraktion.

    Restart-/Crash-Sicherheit (03 §R-P5: 'Verbrauch + Requestidentitaet
    restartfest VOR dem naechsten physischen Versand'): markiert den Grant
    GENAU EINMAL als `consumed` (atomar), BEVOR der Aufrufer `begin_attempt`
    fuer Slot 2 aufruft (der eigentliche Versand folgt dort, NICHT hier). Ist
    der Grant beim Eintritt bereits `consumed` (ein fruehrerer Prozess hat
    diese Funktion bereits erfolgreich durchlaufen, ist aber VOR dem
    naechsten Schritt des Aufrufers abgestuerzt), wird NICHT erneut
    geschrieben (kein Doppelverbrauch), aber weiterhin `True` geliefert --
    der Aufrufer bleibt idempotent fortsetzbar.

    R2-BIND-Fix (GENERALREVIEW.md §3, "allowance=True wird wie 1 akzeptiert"):
    zusaetzlich STRIKT geprueft: (a) `grant.get("action")` muss GENAU
    `P5_ACTION` sein; (b) `operator_decision`/`reason`/`evidence_ref`
    muessen als nichtleere Strings VORHANDEN sein; (c) `allowance` muss ein
    ECHTES `int` UND `== 1` sein (`_is_int_not_bool` schliesst `True == 1`);
    (d) die im Grant gebundene `run_binding` muss mit der AKTUELL fuer
    dieses `run_dir` gueltigen Runidentitaet uebereinstimmen."""
    if record.get("state") != _save_correction.STATE_HOLD or record.get("last_reason") != P5_REQUIRED_REASON:
        return False
    resolved = _validate_run_dir_path(run_dir)
    try:
        token = _safe_file_token(repair_key, label="repair_key")
    except RecoveryUnsafeIdentityError:
        return False
    grant = _read_strict_json_file(_p5_grant_path(resolved, token))
    if grant is None:
        return False
    if grant.get("action") != P5_ACTION:
        return False
    for field in ("operator_decision", "reason", "evidence_ref"):
        value = grant.get(field)
        if not isinstance(value, str) or not value.strip():
            return False
    identity = (
        record.get("persona_key"), record.get("char_id"), record.get("operation_key"),
        record.get("table_id"), record.get("section_id"),
    )
    grant_identity = (
        grant.get("persona_key"), grant.get("char_id"), grant.get("operation_key"),
        grant.get("table_id"), grant.get("section_id"),
    )
    if identity != grant_identity:
        return False
    if grant.get("repair_key") != repair_key:
        return False
    if not _is_int_not_bool(grant.get("allowance")) or grant.get("allowance") != P5_ALLOWANCE:
        return False
    if record.get("attempts_used") != grant.get("bound_attempts_used"):
        return False
    if grant.get("run_binding") != _run_binding(resolved):
        # Der Grant ist an eine andere tatsaechliche Run-Identitaet gebunden
        # (z.B. ein von einem anderen Root/Run kopierter/veralteter Grant) --
        # kontrollierte Ablehnung statt eines ortsfremden Verbrauchs.
        return False
    pre_state_hash = _p5_record_pre_state_hash(resolved, token)
    if grant.get("pre_state_sha256") != pre_state_hash:
        # Der Korrekturdatensatz hat sich seit dem Grant veraendert (z.B. ein
        # anderer Prozess hat ihn inzwischen anders fortgeschrieben) -- die
        # gebundene Autorisierung passt nicht mehr zum aktuellen Vorzustand.
        return False
    # R2-N1-Fix (GENERALREVIEW.md §4 BIND, `p5_consumed_bad_type`): `grant.
    # get("consumed")` wurde bisher nur auf Wahrheitswert geprueft (`if not
    # grant.get("consumed")`) -- ein strukturell falscher Typ wie die STRING
    # `"false"` ist in Python TRUTHY (nichtleerer String), wurde also wie
    # `consumed=True` (bereits verbraucht) behandelt und rutschte UNGEPRUEFT
    # bis zur finalen `return True` durch, ohne die eigentlich noetige
    # strikte Typpruefung je zu durchlaufen -- ein Grant mit `consumed:
    # "false"` galt dadurch faelschlich als gueltig konsumierbar. `consumed`
    # MUSS jetzt ein ECHTES `bool` sein (sonst strukturell unklarer Grant,
    # kein angenommener Save/Transport).
    consumed_value = grant.get("consumed")
    if not isinstance(consumed_value, bool):
        return False
    if not consumed_value:
        consumed = dict(grant)
        consumed["consumed"] = True
        consumed["consumed_ts"] = time.time()
        _atomic_write_json(_p5_grant_path(resolved, token), consumed)
    return True
