#!/usr/bin/env python3
"""
mmo_sim/lab/runner.py — expliziter headless Lab-Betrieb (M4, 01 §3 M4,
03 §6, A11/A12).

"lab ist ein ausdruecklich gestarteter eigenstaendiger Runtime-Lauf ...
Singleton-Schutz und sauberer Stop/Status." KEIN neuer OpenClaw-Cron/
Autopush/Dreaming-Prozess — dies ist ein vom Nutzer gestarteter Python-
Prozess mit PID-Lockfile, Budget-Config und Stop-Flag-Datei.

Singleton-Schutz: EIN schreibender Simulationscontroller pro `run_dir`
(02 §8: "kein zweiter schreibender Simulationscontroller"). Ein zweiter
`LabRunner.start()`-Versuch auf demselben `run_dir` wird abgelehnt, solange
der Lock-Inhaber noch lebt (PID-Existenzpruefung)."""
from __future__ import annotations

import fcntl
import json
import os
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path


class SingletonViolationError(RuntimeError):
    pass


class LabRunnerRestartError(RuntimeError):
    """R3 (MAIN-KORREKTUR I2-Nacharbeit 2026-09-24, REVIEW-I2.md §3 Fall
    04): eine `LabRunner`-Instanz ist ein Einmal-Objekt pro `start()`-Zyklus
    -- s. `LabRunner.start()`-Docstring fuer die Begruendung."""


class LabRunnerMissingAuthorityError(RuntimeError):
    """G1 (MAIN-KORREKTUR I2-Reservierungsabschluss 2026-09-24, REVIEW-
    RESERVIERUNGSABSCHLUSS.md §4 Fall 06): ein bereits gestarteter Runner
    mit vorheriger Ledger-Buchung darf eine inzwischen fehlende
    `lab.status.json` NICHT durch einen veralteten In-Memory-Stand neu
    erzeugen -- s. `LabRunner.record_turn()`-Docstring."""


@dataclass
class LabBudget:
    """Explizite Betreibergrenzen (03 §6) — OHNE Default-"unbegrenzt".

    Headless-/Lab-Lobbydurchstich (Bau-GO 2026-09-27, H-E, ANSCHLUSSPLAN-
    HEADLESS.md Entscheidung 4): `max_usd` ist jetzt OPTIONAL (Default
    `None`) -- fuer das Hybrid-Profil (Turn-/Zeit-/Quota-unbekannt, KEINE
    erfundene Dollarrechnung) wird bewusst KEIN `max_usd` gesetzt, statt
    einen synthetischen/unendlichen Platzhalterwert zu erfinden. `max_turns`/
    `max_seconds` bleiben PFLICHTFELDER (jede Betriebsart braucht mindestens
    eine endliche Turn-/Zeitgrenze). `None` propagiert unveraendert in
    `LabStatus.max_usd` (dort bereits optional) -- `core.admission.
    read_admission_block` ueberspringt seine `max_usd`-Pruefungen dann
    strukturell komplett (kein `float >= None`, keine erfundene 0/Inf-
    Zahl), waehrend `max_turns`/`max_seconds` weiterhin gaten.

    F2-Fix (Critic-Nacharbeit, Bau-GO 2026-09-27): `max_wall_seconds`
    (optional, Default `None`) -- die REALE Laufzeitgrenze (Wall-Clock,
    getrennt von `max_seconds`, s. `LabStatus.wall_deadline`-Docstring)
    wandert damit in dieselbe Betreibergrenzen-Autoritaet wie die anderen
    drei Felder, statt wie zuvor eine rein lokale `_run_controller`-Variable
    zu sein, die `core.admission.read_admission_block` nicht sehen konnte
    (ANSCHLUSSPLAN-HEADLESS.md Entscheidung 4: 'vor JEDEM Request', nicht
    nur zwischen zwei Fenstern)."""

    max_turns: int
    max_seconds: float
    max_usd: float | None = None
    max_wall_seconds: float | None = None


@dataclass
class LabStatus:
    running: bool
    pid: int | None
    turns_used: int
    seconds_elapsed: float
    usd_spent: float
    stop_requested: bool
    stop_reason: str | None
    # I5-Fertigstellung: Budget-Obergrenzen zusaetzlich mitpersistiert, damit
    # `core/admission.py` (A1) den Stop komplett FRISCH VON DER PLATTE
    # berechnen kann -- ohne eine LabRunner-Instanz zu kennen. Optional
    # (Default None) fuer Rueckwaertskompatibilitaet mit alten Statusdateien.
    max_turns: int | None = None
    max_seconds: float | None = None
    max_usd: float | None = None
    # F2-Fix (Critic-Nacharbeit, Bau-GO 2026-09-27): ABSOLUTE `time.time()`-
    # Deadline (KEIN `time.monotonic()`-Wert -- der ist nicht prozess-
    # uebergreifend vergleichbar, s. `LabRunner.start()`), einmalig beim
    # jeweils aktuellen `start()`/`resume`-Aufruf aus `LabBudget.
    # max_wall_seconds` berechnet, NICHT bei jedem `_write_status()`-Aufruf
    # neu (sonst wuerde jeder Turn die Deadline weiter in die Zukunft
    # schieben). `core.admission.read_admission_block` liest dieses Feld
    # FRISCH VON DER PLATTE vor JEDEM Request (Initiative/Consent/Leader/
    # Gast/GM/Reflexion) -- vorher wurde die Wall-Clock-Grenze NUR einmal
    # PRO FENSTER in `lab.cli._run_controller`s eigener Schleife geprueft,
    # NICHT vor jedem einzelnen Request INNERHALB eines Fensters
    # (ANSCHLUSSPLAN-HEADLESS.md Entscheidung 4). Optional (Default None)
    # fuer Rueckwaertskompatibilitaet mit alten Statusdateien UND fuer
    # Laeufe ohne `--max-wall-seconds`.
    wall_deadline: float | None = None
    # A9/D4 (WEGKARTE §8): Anzahl Turns mit NICHT beobachtbarer Kostenangabe
    # (`core/admission.py:compute_turn_usd` lieferte `None`) -- getrennt
    # von `usd_spent` sichtbar, damit ein konservativ geschaetzter Anteil
    # nie mit echter gemeldeter Usage verwechselt wird. Optional (Default 0)
    # fuer Rueckwaertskompatibilitaet mit alten Statusdateien.
    usd_unknown_turns: int = 0
    # I2/A1 (MAIN-ENTSCHEIDUNG A1): optionales Feld, das `core.admission.
    # write_test_profile` in DIESELBE Datei schreibt (providerfreies
    # Testprofil, s. `core.admission._has_recognized_authorization`) --
    # Optional (Default None) fuer Vertraeglichkeit mit `LabRunner`, der
    # dieselbe Datei ohne Kenntnis dieses Feldes liest/schreibt (kein
    # Absturz bei `LabStatus(**json.loads(...))` auf einer vom Testprofil
    # vorbelegten Datei). Ein spaeterer `LabRunner._write_status()`-Aufruf
    # ersetzt die Datei durch eine ECHTE Live-/Budgetfreigabe (max_turns/
    # max_seconds/max_usd immer gesetzt) -- die bleibt fuer sich genommen
    # bereits als Autorisierung erkannt, unabhaengig von `provider_free`.
    provider_free: bool | None = None
    # B1 (MAIN-KORREKTUR I2-Nacharbeit 2026-09-24, REVIEW-I2.md §3): schlanke
    # Idempotenz-Kennung fuer bereits angewandte Kostennachbuchungen
    # (`core.admission.record_usd_delta`) -- NICHT die vollen Pro-Request-
    # Datensaetze (die bleiben unveraendert unter `run_dir/requests/`, die
    # aeltere Auflage "keine Duplizierung reicher Requestdaten hierher"
    # bleibt davon unberuehrt). Waechst NUR bei einer tatsaechlichen
    # Ueberschreitung (nicht pro Turn). Optional (Default leere Liste) fuer
    # Rueckwaertskompatibilitaet mit alten Statusdateien.
    reconciled_request_ids: list[str] = field(default_factory=list)
    # G3 (MAIN-KORREKTUR I2-Reservierungsabschluss 2026-09-24, REVIEW-
    # RESERVIERUNGSABSCHLUSS.md §4 Fall 05): eigene, von `reconciled_
    # request_ids` GETRENNTE Idempotenz-Kennung fuer bereits angewandte
    # Zeit-Abschlusswirkungen (`core.admission.add_seconds`) -- Zeit und
    # Geld sind unabhaengige Effekte DESSELBEN Requests, ein gemeinsamer
    # Marker wuerde einen Retry, bei dem nur einer der beiden Effekte
    # bereits angewandt war, faelschlich fuer BEIDE als erledigt halten.
    # Optional (Default leere Liste) fuer Rueckwaertskompatibilitaet mit
    # alten Statusdateien.
    reconciled_seconds_request_ids: list[str] = field(default_factory=list)


def _lock_path(run_dir: Path) -> Path:
    return run_dir / "lab.lock.json"


def _status_path(run_dir: Path) -> Path:
    return run_dir / "lab.status.json"


def _stop_flag_path(run_dir: Path) -> Path:
    return run_dir / "lab.stop"


def _atomic_write_json(path: Path, data: dict) -> None:
    """R2 (MAIN-KORREKTUR I2-Nacharbeit 2026-09-24, REVIEW-I2.md §3 Fall 03):
    dieselbe kleine atomare Dateihilfe wie `core.admission._atomic_write_json`
    (bewusst dupliziert statt cross-modulig importiert -- `lab/runner.py`
    haelt wie `core/admission.py` eigene kleine `_status_path`-artige
    Helfer, keine neue Modulkopplung). Schreibt zuerst in eine temporaere
    Datei im selben Verzeichnis, ersetzt `path` danach per `os.replace`
    (atomarer Rename) -- ein gewoehnlicher Teilschreib-`OSError` auf dem
    Temp-Pfad hinterlaesst `path` UNVERAENDERT (letzter gueltiger Stand
    bleibt lesbar). Kein fsync-/Powerloss-Haertungsprojekt. Ein Fehler wird
    NICHT verschluckt: die verwaiste Temp-Datei wird bestmoeglich
    aufgeraeumt, die Ausnahme propagiert an den Aufrufer."""
    tmp_path = path.with_name(f"{path.name}.tmp-{os.getpid()}-{uuid.uuid4().hex[:8]}")
    try:
        tmp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp_path, path)
    except OSError:
        tmp_path.unlink(missing_ok=True)
        raise


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # existiert, gehoert nur einem anderen Nutzer
    return True


class LabRunner:
    """EIN Lab-Lauf pro `run_dir`. `pid` ist injizierbar (Test-Determinismus);
    Default ist der echte `os.getpid()`."""

    def __init__(self, run_dir: str | Path, budget: LabBudget, pid: int | None = None):
        self.run_dir = Path(run_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.budget = budget
        self.pid = pid if pid is not None else os.getpid()
        # I5-Fix (Gegentest 09): ein Resume (neue LabRunner-Instanz fuer
        # DASSELBE run_dir) darf den bereits verbrauchten Verbrauch NICHT
        # auf 0 zuruecksetzen -- Verbrauch fortsetzen ist der Default; eine
        # neue Budgetfreigabe ist eine ausdrueckliche Betreiberentscheidung
        # (separates run_dir bzw. manuelles Zuruecksetzen der Statusdatei).
        existing = read_status(self.run_dir)
        if existing is not None:
            self._turns_used = existing.turns_used
            self._seconds_elapsed = existing.seconds_elapsed
            self._usd_spent = existing.usd_spent
            self._usd_unknown_turns = existing.usd_unknown_turns
            self._reconciled_request_ids = existing.reconciled_request_ids
            self._reconciled_seconds_request_ids = existing.reconciled_seconds_request_ids
        else:
            self._turns_used = 0
            self._seconds_elapsed = 0.0
            self._usd_spent = 0.0
            self._usd_unknown_turns = 0
            self._reconciled_request_ids = []
            self._reconciled_seconds_request_ids = []
        # R3 (MAIN-KORREKTUR I2-Nacharbeit 2026-09-24, REVIEW-I2.md §3 Fall
        # 04): diese Instanz darf `start()` nur EINMAL erfolgreich
        # durchlaufen -- s. `start()`-Docstring.
        self._started = False
        # ERGAENZUNG 4 (F2-Leaseabschluss, Bau-GO 2026-09-27): die offene
        # fd des exklusiven OS-Locks (`fcntl.flock`) -- s. `_acquire_lock`.
        # Diese fd, NICHT der PID-JSON-Inhalt, ist ab jetzt der eigentliche
        # Besitznachweis; sie bleibt fuer die gesamte Besitzdauer OFFEN
        # (erst `release()` schliesst sie) statt wie zuvor sofort nach dem
        # initialen Schreiben geschlossen zu werden.
        self._lock_fd: int | None = None
        # F2-Fix (Critic-Nacharbeit, Bau-GO 2026-09-27): wird in `start()`
        # EINMALIG aus `budget.max_wall_seconds` berechnet (wie `max_turns`/
        # `max_seconds`/`max_usd` selbst: eine BETREIBERGRENZE, die bei
        # jedem `start()`/`resume`-Aufruf aus dem AKTUELLEN `self.budget`
        # neu gilt, NICHT aus einer alten Statusdatei uebernommen wird --
        # anders als `_turns_used`/`_seconds_elapsed`/`_usd_spent`
        # oberhalb, die VERBRAUCH sind und deshalb fortgeschrieben werden).
        self._wall_deadline: float | None = None

    def start(self) -> None:
        """Wirft `SingletonViolationError`, wenn bereits ein LEBENDER Lock-
        Inhaber existiert (kein zweiter schreibender Controller, 02 §8/A12).

        R3 (MAIN-KORREKTUR I2-Nacharbeit 2026-09-24, REVIEW-I2.md §3 Fall
        04): wirft `LabRunnerRestartError`, wenn DIESE Instanz bereits
        einmal erfolgreich gestartet wurde -- VOR jeder Datei-/
        Statusaenderung, also auch vor dem Lock-Schreiben. Grund: der
        In-Memory-Stand dieser Instanz (`self._usd_spent`/`self._turns_used`)
        wurde EINMALIG im Konstruktor von der Platte gelesen. Zwischen
        einem `start()`/`release()`-Zyklus koennen externe Schreiber
        (`core.admission.record_usd_delta` u.a., z.B. ueber
        `core.request_ledger.finish_received`) `lab.status.json`
        veraendern, OHNE dass diese Instanz davon erfaehrt. Ein erneuter
        `_write_status()`-Aufruf DERSELBEN Instanz wuerde dann einen
        inzwischen neueren, autoritativen Betrag (`usd_spent`/`turns_used`)
        mit dem veralteten In-Memory-Wert ueberschreiben -- OBWOHL
        `reconciled_request_ids` bereits frisch von der Platte gelesen wird
        (s. `_write_status`), was einen inkonsistenten halb-frischen Zustand
        erzeugen wuerde (Kennung vermerkt, Betrag/Versuchsanzahl verloren).
        Ein Resume ist eine ausdrueckliche neue `LabRunner`-Instanz (deren
        Konstruktor den vollen Stand frisch liest, s. `test_05_new_runner_
        restart_positive_control`) -- KEIN Restart auf demselben Objekt."""
        if self._started:
            raise LabRunnerRestartError(
                f"LabRunner-Instanz fuer {self.run_dir} wurde bereits gestartet -- "
                "kein Restart auf DERSELBEN Instanz (R3, MAIN-KORREKTUR I2-Nacharbeit "
                "2026-09-24, REVIEW-I2.md §3 Fall 04); fuer ein Resume eine NEUE "
                "LabRunner-Instanz konstruieren (deren Konstruktor liest den vollen "
                "Stand frisch von der Platte)."
            )
        self._acquire_lock(_lock_path(self.run_dir))
        try:
            if _stop_flag_path(self.run_dir).exists():
                _stop_flag_path(self.run_dir).unlink()
            # L3 (ERGAENZUNG 4, Bau-GO 2026-09-27, REVIEW-LEASEABSCHLUSS.md §6
            # Fall 06): der Konstruktor liest `lab.status.json` EINMALIG beim
            # Objektbau -- liegt zwischen Konstruktion und diesem tatsaechlich
            # ERFOLGREICHEN Erwerb ein anderer Besitzer (der Verbrauch bucht
            # und wieder freigibt), ist dieser fruehe In-Memory-Stand STALE.
            # Erst ab hier, NACH gesicherter exklusiver Autoritaet
            # (`_acquire_lock` ist zurueckgekehrt), den tatsaechlich
            # maszgeblichen Verbrauch/Dedup FRISCH von der Platte uebernehmen
            # -- eine neue Instanz ist NICHT automatisch ein frischer
            # Erwerbszustand. Fehlt die Datei (echter Erstlauf), bleiben die
            # Konstruktor-Nullwerte unveraendert gueltig.
            on_disk = read_status(self.run_dir)
            if on_disk is not None:
                self._turns_used = on_disk.turns_used
                self._seconds_elapsed = on_disk.seconds_elapsed
                self._usd_spent = on_disk.usd_spent
                self._usd_unknown_turns = on_disk.usd_unknown_turns
                self._reconciled_request_ids = on_disk.reconciled_request_ids
                self._reconciled_seconds_request_ids = on_disk.reconciled_seconds_request_ids
            # F2-Fix (Critic-Nacharbeit, Bau-GO 2026-09-27): ABSOLUTE `time.
            # time()`-Deadline EINMALIG hier berechnen (nicht in
            # `_write_status`, sonst wuerde jeder spaetere `record_turn()`-
            # Aufruf die Deadline erneut in die Zukunft schieben) -- `time.
            # time()`, nicht `time.monotonic()`, weil `core.admission.
            # read_admission_block` diesen Wert in einem ANDEREN Prozess
            # (echter Persona-/GM-Request-Pfad) gegen SEINE eigene aktuelle
            # Zeit vergleicht; `monotonic()` hat pro Prozess einen eigenen,
            # nicht vergleichbaren Nullpunkt.
            self._wall_deadline = (
                time.time() + self.budget.max_wall_seconds
                if self.budget.max_wall_seconds is not None else None
            )
            self._write_status()
        except BaseException:
            # H10 Fall (e) (ERGAENZUNG 4, Bau-GO 2026-09-27): ein Fehler NACH
            # bereits erfolgreichem Lock-Erwerb (z.B. ein fehlschlagender
            # initialer Statuswrite) darf den OS-Lock nicht bis zum
            # zufaelligen Prozessende haengen lassen -- ein Aufrufer, dessen
            # `start()` wirft, ruft ueblicherweise KEIN `release()` auf
            # (er haelt sich ja fuer nie erfolgreich gestartet). Den soeben
            # erworbenen Lock hier explizit zurueckgeben, DANACH den echten
            # Fehler unveraendert propagieren.
            self._release_lock_after_failed_start()
            raise
        self._started = True

    def _release_lock_after_failed_start(self) -> None:
        """Gegenstueck zu `release()` fuer den Fall, dass `_acquire_lock`
        bereits erfolgreich war, aber ein SPAETERER Schritt in `start()`
        (Stop-Flag-Unlink, Statusrefresh, initialer `_write_status`) wirft --
        s. `start()`-Docstring, H10 Fall (e). Kein Statuswrite hier (der ist
        ja gerade fehlgeschlagen oder nie versucht worden); nur den OS-Lock
        freigeben und die Lock-Datei bedingt zurueckziehen (nur wenn sie noch
        den eigenen, gerade erst geschriebenen Eintrag traegt).

        E1-Fix (REVIEW-LEASE-AUSGAENGE.md §4, Bau-GO 2026-09-28): der
        bedingte `unlink` passiert JETZT, WAEHREND die eigene `flock`-
        Autoritaet noch gehalten wird -- `flock(LOCK_UN)`+`close` (Verlust
        der eigenen Autoritaet) folgen ERST DANACH im `finally`. Die
        vorherige Fassung gab zuerst den flock frei und las/unlinkte dann
        anhand einer bereits VERALTETEN PID-Lesung: ein Nachfolger konnte
        zwischen dieser Freigabe und dem spaeten `unlink` bereits erfolg-
        reich erwerben UND publizieren, sodass der alte Unlink dessen
        frische Lease entfernte (zwei lebende Owner, Faelle 02/03). Solange
        die eigene `flock`-Autoritaet noch besteht, kann kein Nachfolger
        seinen eigenen `flock`-Erwerb abschliessen (dessen `LOCK_EX|
        LOCK_NB` schlaegt zwingend fehl, bzw. ein bereits BLOCKIEREND
        wartender Reklamierer sieht durch `_fd_still_matches_path()` nach
        unserem Unlink korrekt eine geisterhafte fd und versucht neu) --
        der Pfad-Eingriff ist also niemals gegen eine fremde, bereits
        abgeschlossene Neuvergabe ungeschuetzt. `self._lock_fd` wird darum
        erst im `finally`, NACH dem tatsaechlichen `close`, auf `None`
        gesetzt (nicht vorher) -- der Zustand des Attributs spiegelt so
        durchgehend wider, ob die eigene Autoritaet noch besteht."""
        if self._lock_fd is None:
            return
        fd = self._lock_fd
        try:
            lock_path = _lock_path(self.run_dir)
            try:
                data = json.loads(lock_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                data = None
            if data is not None and data.get("pid") == self.pid:
                lock_path.unlink()
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
            self._lock_fd = None

    def _acquire_lock(self, lock_path: Path) -> None:
        """ERGAENZUNG 4 (F2-Leaseabschluss, Bau-GO 2026-09-27, REVIEW-
        LEASEABSCHLUSS.md §4/§5): ersetzt die vorherige Rename-/Rollback-
        Reklamation (`os.rename(lock_path, stale_marker)` -> Inhaltscheck ->
        ggf. Rueckstellung) durch EINE echte, ununterbrochene Exklusivitaets-
        grenze. Die alte Logik machte `lock_path` fuer die Dauer der
        Reklamation ZEITWEISE LEER -- ein dritter O_EXCL-Start konnte dieses
        Fenster als freie Ablage lesen (Fall 03), und ein gewoehnlicher
        `OSError` am Rueckstellungs-Rename hinterliess dasselbe Fenster
        dauerhaft (Fall 04). Kern-Entscheidung (Main-Plan): eine stabile
        Lock-fd mit `fcntl.flock(LOCK_EX|LOCK_NB)` als MASSGEBLICHE
        Autoritaet; der PID-JSON-Inhalt der Datei bleibt rein INFORMATIV
        (Anzeige/Diagnose, z.B. fuer `active_lock_pid`).

        Zwei Pfade, je nachdem ob die Datei bereits existiert:

        1. Frischer Erwerb (Datei existiert nicht): UNVERAENDERTER
           `os.open(..., O_CREAT|O_EXCL|O_WRONLY)` -- weiterhin der
           dateisystemseitig atomare Erwerbsnachweis fuer den allerersten
           Erwerb (erhaelt den bestehenden O_EXCL-Boundary-Testseam exakt).
           NEU: die zurueckgegebene fd wird zusaetzlich per `fcntl.flock`
           belegt und bleibt fuer die GESAMTE Besitzdauer OFFEN (`self.
           _lock_fd`), statt wie zuvor sofort nach dem Schreiben geschlossen
           zu werden -- ab hier ist die offene fd selbst der Besitznachweis.
        2. Reklamation (Datei existiert bereits, `FileExistsError`): die
           Datei wird OHNE O_EXCL geoeffnet und `fcntl.flock(fd, LOCK_EX|
           LOCK_NB)` versucht.
           - Schlaegt fehl (`OSError`, z.B. `BlockingIOError`): ein ANDERER
             Prozess haelt den OS-Lock gerade WIRKLICH -- das ist der
             einzige Fall, in dem ein zweiter schreibender Controller
             existieren koennte, und flock verhindert ihn strukturell.
             Die zu diesem Zeitpunkt gelesene PID ist rein informativ fuer
             die Fehlermeldung (G3a).
           - Gelingt: niemand haelt den OS-Lock gerade -- das ist STAERKERE
             Evidenz als eine PID-Lebendigkeitspruefung (`os.kill(pid, 0)`
             kann durch PID-Wiederverwendung taeuschen; ein tatsaechlich
             gehaltener flock kann es nicht). Der VORHANDENE Inhalt wird
             trotzdem validiert, BEVOR er ueberschrieben wird: ein
             strukturell UNGUELTIGER Owner-Eintrag (z.B. `pid: "not-a-pid"`,
             kein `int`) ist NICHT automatisch 'tot' -- ein unzuordenbarer
             Owner bleibt kontrolliert GEHALTEN (`SingletonViolationError`,
             der soeben erworbene flock wird dafuer wieder freigegeben),
             genau wie eine nicht lesbare/parsebare Lease-Datei (G3a:
             'unklare Lease kontrolliert halten', nicht als frei ersetzen).
             Ein gueltiger (auch vormals lebender, jetzt toter) PID-Eintrag
             wird ueberschrieben -- OHNE Zwischenschritt, OHNE dass der
             kanonische Pfad je als leer/frei sichtbar wird (L1, Faelle
             01-04): entweder haelt jemand den flock (Fehlschlag oben) oder
             niemand tut es (Erfolg hier).

        End-Critic-Nacharbeit (CRITIC-REPORT.md §2, 2026-09-27): die fruehere
        Fassung dieses Docstrings behauptete, es existiere "keine Zwischen-
        phase mehr" -- das war FALSCH. Zwischen `os.open(O_CREAT|O_EXCL)`
        (Frischerwerb) bzw. `os.open(O_RDWR)` (Reklamation) und dem jeweils
        EIGENEN `flock`-Erwerb liegt ein winziges, aber echtes Zeitfenster:
        ein GLEICHZEITIGER Zweitprozess kann in dieser Luecke die Datei
        unlinkt/ersetzt haben (z.B. weil er selbst als Reklamierer gewinnt
        und spaeter regulaer freigibt+unlinkt), sodass die eigene, bereits
        offene fd danach nur noch eine "geisterhafte" Inode haelt, die nicht
        mehr dem aktuellen `lock_path`-Verzeichniseintrag entspricht -- ein
        DRITTER Prozess kann den (wieder leeren) Pfad dann ganz normal ein
        zweites Mal frisch erwerben (zwei gleichzeitig erfolgreiche Owner).
        Deshalb wird NACH JEDEM `flock`-Erwerb (beide Zweige) per
        `_fd_still_matches_path()` (`st_dev`/`st_ino`-Abgleich zwischen der
        offenen fd und dem AKTUELLEN Pfadeintrag) verifiziert, dass die
        eigene fd noch lebt; bei Abweichung wird die fd verworfen und der
        GESAMTE Erwerb (beide Zweige, `while True`-Schleife unten) neu
        versucht, statt blind mit einer potenziell veralteten fd
        fortzufahren. Erst NACH dieser Verifikation gilt die Zwischenphase
        als tatsaechlich nicht mehr beobachtbar.

        Unterstuetzte Laufzeit-/OS-Grenze: `fcntl.flock` ist POSIX (Linux/
        macOS); kein Windows-Betrieb, kein Netzwerk-Dateisystem (NFS)
        garantiert. `virtiofs` (der tatsaechliche Mount-Typ des Default-
        Datenpfads `internal/mmo_sim_data` in dieser Bereitstellung, s.
        CRITIC-REPORT.md §3, 2026-09-27) wurde NACHTRAEGLICH mit einer
        echten Zweiprozess-Probe auf einem tatsaechlichen virtiofs-Pfad
        gezielt geprueft (3/3 stabil, `out/leaseabschluss-2026-09-27/worker/
        post-critic-fix-review/virtiofs-flock-probe/`): `fcntl.flock`
        erzwingt dort echte cross-prozessuale Exklusivitaet (LOCK_NB
        schlaegt waehrend fremdem Halten fehl, gelingt danach), UND
        `st_dev`/`st_ino` (die von `_fd_still_matches_path()` verwendete
        Grundlage) verhaelt sich dort wie erwartet (Uebereinstimmung bei
        derselben Datei, Abweichung nach Unlink+Neuanlage) -- KEIN
        NFS-artiges Caching-/Locking-Problem beobachtet. Same-Process-
        Sonderfall bewusst NICHT uebernommen: zwei
        verschiedene fds auf dieselbe Datei sind bei `flock` (anders als bei
        der alten PID-Gleichheitspruefung) selbst im selben Prozess NICHT
        automatisch derselbe Besitzer (POSIX-Semantik: der Lock haengt an
        der open-file-description, nicht am Prozess) -- kein bestehender
        Test verlangt einen zweiten echten `start()`-Erfolg mit gleicher
        `self.pid`; `LabRunnerRestartError` deckt den tatsaechlich
        getesteten Restart-derselben-Instanz-Fall weiterhin vollstaendig ab.
        """
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps({"pid": self.pid}).encode("utf-8")
        while True:
            try:
                fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            except FileExistsError:
                pass
            else:
                # Frischer Erwerb: dateisystemseitig bereits exklusiv
                # erwiesen (O_EXCL). flock zusaetzlich belegen, damit
                # derselbe fd fuer die gesamte Besitzdauer die
                # massgebliche Autoritaet bleibt.
                #
                # E2-Fix (REVIEW-LEASE-AUSGAENGE.md §5, Bau-GO 2026-09-28):
                # ALLES ab hier bis zur Uebergabe an `self._lock_fd` steht
                # unter einem einzigen `try`/`except BaseException` --
                # vorher deckte nur der `os.write`-Schritt einen eigenen
                # Fehlerpfad ab; ein `OSError` aus `_fd_still_matches_path()`
                # (z.B. `os.stat` mit EIO, nicht nur dem dort bereits
                # behandelten `FileNotFoundError`) propagierte UNGEFANGEN
                # nach oben und liess die bereits geoeffnete+gesperrte fd
                # weder geschlossen noch als `self._lock_fd` uebergeben
                # zurueck -- eine fuer `release()` unerreichbare, bis zum
                # zufaelligen Prozessende gehaltene Sperre (Gruppe 04). Der
                # gezielte `continue` fuer den erkannten Geist-fd-Fall bleibt
                # innerhalb desselben `try`: `continue` ist keine Ausnahme
                # und ueberspringt den `except`-Block unveraendert.
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX)
                    if not self._fd_still_matches_path(fd, lock_path):
                        # CRITIC-REPORT.md §2: ein gleichzeitiger Reklamierer
                        # hat die Datei gewonnen UND bereits wieder freige-
                        # geben/unlinkt, waehrend wir auf unseren EIGENEN
                        # (blockierenden) flock warteten -- unsere fd ist
                        # jetzt ein Geist. Verwerfen und den gesamten Erwerb
                        # neu versuchen.
                        fcntl.flock(fd, fcntl.LOCK_UN)
                        os.close(fd)
                        continue
                    # L1/Fall 04 (ERGAENZUNG 4): ein gewoehnlicher I/O-Fehler
                    # am tatsaechlichen Commit-Write darf weder eine zweite
                    # lebende Autoritaet noch einen dauerhaft blockierten
                    # Lock hinterlassen.
                    os.write(fd, payload)
                except BaseException:
                    # Kein abgeschlossener Besitzwechsel bei fehlgeschlagenem
                    # Erwerbsschritt: den soeben (ggf.) erworbenen OS-Lock
                    # wieder freigeben (Aufruf ist ein No-Op, falls `flock`
                    # selbst schon fehlschlug und nie griff), fd schliessen,
                    # DANN den echten Fehler unveraendert propagieren.
                    fcntl.flock(fd, fcntl.LOCK_UN)
                    os.close(fd)
                    raise
                self._lock_fd = fd
                return

            fd = os.open(lock_path, os.O_RDWR)
            # E2-Fix (REVIEW-ERWERBSABBRUCH.md §4, Bau-GO 2026-09-28): diese
            # erste Rueckkehrgrenze deckte bisher NUR `OSError` ab. Eine
            # Nicht-OSError-Ausnahme (z.B. `KeyboardInterrupt` durch ein
            # Signal genau an der Rueckkehr des tatsaechlich ERFOLGREICHEN
            # `flock`) propagierte ungefangen nach oben, ohne die fd zu
            # schliessen oder eine ggf. bereits erworbene `flock`-Autoritaet
            # freizugeben -- `self._lock_fd` blieb `None`, `release()`
            # konnte die verlorene fd nie erreichen, und ein gesunder
            # Nachfolger blieb bis zum zufaelligen Prozessende dieses
            # Aufrufers blockiert (Gruppe 04). Fehlerklassifikation bleibt
            # von Ressourcenabschluss GETRENNT: `OSError` bedeutet weiterhin
            # ein lebender Konkurrent (unveraendert `SingletonViolationError`
            # unten); jede andere Ausnahme (`KeyboardInterrupt`/
            # `SystemExit`/...) wird NICHT umgedeutet, sondern nach
            # bestmoeglichem lokalem Cleanup unveraendert weitergereicht.
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                other_pid = self._peek_owner_pid(fd)
                os.close(fd)
                if other_pid is not None:
                    raise SingletonViolationError(
                        f"Lab-Lauf bereits aktiv (pid={other_pid}) fuer {self.run_dir} — "
                        f"kein zweiter schreibender Simulationscontroller."
                    )
                raise SingletonViolationError(
                    f"Lab-Lock {lock_path} ist aktiv belegt -- unklare Lease kontrolliert "
                    "gehalten, kein automatisches Ueberschreiben (G3a)."
                )
            except BaseException:
                # Nicht-OSError an dieser Rueckkehrgrenze: der `flock`-
                # Erwerb kann bereits am Kernel erfolgreich gewesen sein,
                # bevor das Signal eintraf -- eine ggf. bereits gehaltene
                # eigene Autoritaet wieder freigeben (No-Op, falls `flock`
                # selbst nie griff), fd schliessen, DANN den echten Fehler
                # UNVERAENDERT propagieren (kein `SingletonViolationError`).
                fcntl.flock(fd, fcntl.LOCK_UN)
                os.close(fd)
                raise
            # E2-Fix (REVIEW-LEASE-AUSGAENGE.md §5, Bau-GO 2026-09-28): ab
            # hier gehoert der OS-Lock nachweislich uns (der `flock`-Erwerb
            # oben ist bereits erfolgreich zurueckgekehrt); JEDER weitere
            # Ausgang bis zur Uebergabe an `self._lock_fd` -- Pfad-/Inode-
            # Abgleich, `os.pread`, JSON-Decode, `os.pwrite`/`os.ftruncate`
            # -- steht darum unter einem gemeinsamen `try`/`except
            # BaseException`. Vorher deckten nur der explizite Ungueltig-
            # Owner-Fall und der `pwrite`/`ftruncate`-Schritt einen eigenen
            # Cleanup-Pfad ab; ein `OSError` aus `_fd_still_matches_path()`
            # (`os.stat`, z.B. EIO) oder direkt aus `os.pread` (z.B. EIO)
            # propagierte UNGEFANGEN nach oben und liess die bereits
            # gesperrte fd weder geschlossen noch uebergeben zurueck --
            # dieselbe unerreichbare-Sperre-Klasse wie beim Frischerwerb
            # (Gruppe 04, Reclaim-Varianten). Der gezielte `continue` fuer
            # den erkannten Geist-fd-Fall bleibt innerhalb desselben `try`:
            # `continue` ist keine Ausnahme und ueberspringt den `except`-
            # Block unveraendert.
            try:
                if not self._fd_still_matches_path(fd, lock_path):
                    # CRITIC-REPORT.md §2 (gleiche Invariantenklasse, hier
                    # theoretisch): die Datei wurde zwischen unserem
                    # `os.open` und unserem eigenen `flock`-Erwerb bereits
                    # durch einen anderen Prozess unlinkt+ersetzt. Verwerfen
                    # und neu versuchen statt einer geisterhaften fd zu
                    # vertrauen.
                    fcntl.flock(fd, fcntl.LOCK_UN)
                    os.close(fd)
                    continue
                # Der OS-Lock gehoert jetzt uns, UND die fd entspricht
                # nachweislich noch dem aktuellen Pfadeintrag -- niemand
                # sonst kann ihn gleichzeitig halten. Vorhandenen Inhalt
                # validieren, BEVOR er ueberschrieben wird (ein leerer
                # O_RDWR-Erfolg auf einer NICHT-neuen Datei bedeutet: der
                # vorherige Inhaber hat entweder sauber freigegeben (Datei
                # idR. bereits entfernt, dieser Zweig also selten) oder ist
                # abgestuerzt (Kernel hat seine fd automatisch geschlossen
                # -> flock automatisch freigegeben) -- in beiden Faellen
                # KEIN lebender Zweitbesitzer moeglich, s. Docstring).
                raw = os.pread(fd, 1 << 16, 0)
                if raw.strip():
                    try:
                        data = json.loads(raw.decode("utf-8"))
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        data = None
                    other_pid = data.get("pid") if isinstance(data, dict) else None
                    valid_pid = isinstance(other_pid, int) and not isinstance(other_pid, bool)
                    if not valid_pid:
                        raise SingletonViolationError(
                            f"Lab-Lock {lock_path} hat einen strukturell ungueltigen "
                            f"Owner-Eintrag ({other_pid!r}) -- unklare Lease kontrolliert "
                            "gehalten, kein automatisches Ueberschreiben, keine "
                            "Fremd-PID-Vermutung (G3a)."
                        )
                # WRITE zuerst, TRUNCATE erst NACH erfolgreichem Write (nicht
                # umgekehrt): schlaegt der Write fehl, bleibt der VORHERIGE
                # Inhalt vollstaendig erhalten (kein leeres/kaputtes File als
                # Nebenwirkung eines fehlgeschlagenen Commits -- L1: "keine
                # unsichere Zwischenphase").
                os.pwrite(fd, payload, 0)
                os.ftruncate(fd, len(payload))
            except BaseException:
                # L1/Fall 04 (ERGAENZUNG 4, REVIEW-LEASEABSCHLUSS.md §5):
                # kein abgeschlossener Besitzwechsel bei fehlgeschlagenem
                # Erwerbsschritt -- OS-Lock wieder freigeben, fd schliessen,
                # DANN den echten Fehler propagieren. Kein Fremdprozess
                # betroffen, kein dauerhaft blockierter Lock, kein
                # stillschweigend abgeschlossener Besitzwechsel.
                fcntl.flock(fd, fcntl.LOCK_UN)
                os.close(fd)
                raise
            self._lock_fd = fd
            return

    @staticmethod
    def _fd_still_matches_path(fd: int, lock_path: Path) -> bool:
        """CRITIC-REPORT.md §2 (2026-09-27): nach einem (ggf. blockierenden)
        `flock`-Erwerb verifizieren, dass die offene fd noch demselben
        Verzeichniseintrag entspricht wie `lock_path` -- schliesst die vom
        End-Critic bewiesene Race, bei der ein anderer Prozess die Datei
        zwischen unserem `os.open` und unserem EIGENEN `flock`-Erwerb bereits
        unlinkt+ersetzt hat, waehrend unsere fd weiterhin auf die ALTE, jetzt
        geisterhafte Inode zeigt (`st_dev`/`st_ino`-Abgleich, nicht Inhalt --
        ein Inhaltsvergleich koennte durch eine zufaellig identische neue
        Datei getaeuscht werden, eine Inode-Identitaet nicht)."""
        try:
            path_stat = os.stat(lock_path)
        except FileNotFoundError:
            return False
        fd_stat = os.fstat(fd)
        return (fd_stat.st_dev, fd_stat.st_ino) == (path_stat.st_dev, path_stat.st_ino)

    @staticmethod
    def _peek_owner_pid(fd: int) -> int | None:
        """Best-effort, rein informative Lesung des PID-Felds einer Lock-fd,
        NACHDEM ein `flock`-Erwerb bereits fehlgeschlagen ist (nur fuer die
        Fehlermeldung -- die Autoritaet selbst kommt ausschliesslich aus dem
        `flock`-Ergebnis, s. `_acquire_lock`-Docstring)."""
        try:
            raw = os.pread(fd, 1 << 16, 0)
            data = json.loads(raw.decode("utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return None
        pid = data.get("pid") if isinstance(data, dict) else None
        if isinstance(pid, int) and not isinstance(pid, bool):
            return pid
        return None

    def stop(self, reason: str) -> None:
        """Setzt ein Stop-Flag — der laufende Prozess (derselbe oder ein
        angehefteter Status-Leser) prueft `should_stop()` vor jedem neuen
        Request und pausiert dann geordnet, statt hart abzubrechen."""
        _stop_flag_path(self.run_dir).write_text(
            json.dumps({"reason": reason}), encoding="utf-8",
        )

    def should_stop(self) -> tuple[bool, str | None]:
        # F3-Fix (Critic-Nacharbeit, Bau-GO 2026-09-27): Rechenkern nach
        # `compute_stop_state` ausgelagert, damit `lab.cli._status_payload`
        # (H-C, `lab status`/`lab attach`) DENSELBEN frisch-von-der-Platte-
        # Zustand berichten kann, den auch der naechste echte Request sehen
        # wuerde -- s. dortigen Docstring. Verhalten dieser Methode
        # unveraendert.
        return compute_stop_state(
            self.run_dir, turns_used=self._turns_used, seconds_elapsed=self._seconds_elapsed,
            usd_spent=self._usd_spent, max_turns=self.budget.max_turns,
            max_seconds=self.budget.max_seconds, max_usd=self.budget.max_usd,
            wall_deadline=self._wall_deadline,
        )

    def record_turn(self, seconds: float, usd: float) -> None:
        """Budget WIRD VOR dem naechsten Request geprueft (`should_stop`),
        Verbrauch NACH der Antwort verrechnet (03 §6: 'vor neuen Requests
        Budget reservieren, nach Antwort tatsaechliche Usage verrechnen').

        C-Fix (MAIN-KORREKTUR I2-Nacharbeit 2026-09-24, REVIEW-BUCHUNGSGRENZEN.
        md §5 Fall 05): uebernimmt den vollen autoritativen `turns_used`/
        `seconds_elapsed`/`usd_spent`-Stand FRISCH von der Platte, BEVOR der
        eigene Zuwachs angewendet wird. Zwischen zwei `record_turn()`-
        Aufrufen (oder seit `start()`) koennen andere legitime Schreiber
        (`core.admission.record_turn_usage`/`record_usd_delta` ueber
        `core.request_ledger`) `lab.status.json` bereits veraendert haben,
        OHNE dass diese Instanz davon weiss -- ein rein in-memory
        fortgeschriebener Betrag wuerde einen inzwischen hoeheren
        autoritativen Betrag stillschweigend mit einem veralteten,
        niedrigeren Wert ueberschreiben (Betrag verloren), obwohl
        `_write_status()` `reconciled_request_ids`/`usd_unknown_turns`
        bereits separat frisch von der Platte uebernimmt (R3/B1). Kein
        Restart-Konflikt: der `start()`-Guard (`LabRunnerRestartError`)
        bleibt unveraendert unberuehrt, dies betrifft NUR den Betrag/die
        Versuchsanzahl innerhalb EINES `start()`/`release()`-Zyklus.

        G1-Fix (MAIN-KORREKTUR I2-Reservierungsabschluss 2026-09-24, REVIEW-
        RESERVIERUNGSABSCHLUSS.md §4 Fall 06): fehlt `lab.status.json`
        JETZT (`read_status()` liefert `None`), obwohl dieser Runner bereits
        gestartet wurde (frueher erfolgreicher Konstruktor-/`start()`-Read),
        ist das KEIN Ruecksprung in einen erstmaligen Initialzustand --
        `record_turn()` wirft VOR jeder Aenderung/jedem Schreibzugriff
        `LabRunnerMissingAuthorityError`, statt den zuletzt bekannten
        In-Memory-Stand als neue Autoritaet mit einem veralteten
        `seconds`/`usd`-Zuwachs und leeren Dedup-Listen frisch niederzuschreiben
        (das wuerde eine bereits committete Buchung -- hier `self._usd_spent`
        aus einer FRUEHEREN, jetzt verschwundenen Datei -- unwiederbringlich
        verlieren, sobald die naechste Zeile die Datei neu anlegt)."""
        on_disk = read_status(self.run_dir)
        if on_disk is None:
            raise LabRunnerMissingAuthorityError(
                f"lab.status.json fehlt bei {self.run_dir} -- dieser Runner wurde bereits "
                "gestartet (fruehere Buchung im Speicher vorhanden); ein spaeterer "
                "record_turn()-Aufruf darf die fehlende Autoritaetsdatei nicht aus einem "
                "veralteten In-Memory-Stand neu erzeugen (G1, REVIEW-RESERVIERUNGSABSCHLUSS.md "
                "§4 Fall 06)."
            )
        self._turns_used = on_disk.turns_used
        self._seconds_elapsed = on_disk.seconds_elapsed
        self._usd_spent = on_disk.usd_spent
        self._turns_used += 1
        self._seconds_elapsed += seconds
        self._usd_spent += usd
        self._write_status()

    def _write_status(self) -> None:
        """R3 (MAIN-KORREKTUR I2-Nacharbeit 2026-09-24, REVIEW-I2.md §3 Fall
        04): `start()` lehnt einen Restart DERSELBEN Instanz ab
        (`LabRunnerRestartError`) -- das schuetzt nur vor einem erneuten
        `start()`-Aufruf, NICHT davor, dass ANDERE legitime Schreiber
        (`core.admission.record_turn_usage`/`record_usd_delta` ueber
        `core.request_ledger`) `lab.status.json` waehrend eines laufenden
        `start()`/`release()`-Zyklus veraendern, OHNE dass diese Instanz
        davon erfaehrt (C-Fix, REVIEW-BUCHUNGSGRENZEN.md §5 Fall 05: exakt
        dieser Fall liess `record_turn()` frueher einen bereits extern
        gebuchten Betrag mit einem veralteten In-Memory-Wert ueberschreiben).
        `self._turns_used`/`self._seconds_elapsed`/`self._usd_spent` sind
        deshalb NICHT allein durch den Restart-Guard aktuell, sondern weil
        `record_turn()` sie vor jedem Zuwachs selbst frisch von der Platte
        uebernimmt (s. dessen Docstring) und `start()` sie direkt aus dem
        frischen Konstruktor-Read uebernimmt -- diese Methode selbst
        uebernimmt zusaetzlich `usd_unknown_turns`/`reconciled_request_ids`
        frisch von der Platte (s.u.), unabhaengig vom Aufrufer. `LabRunner.
        run_section()` ruft diese Methode bewusst NICHT auf -- die
        eigentliche Verbrauchsfortschreibung waehrend eines echten Turns
        passiert direkt ueber `core.admission.record_turn_usage`/
        `record_usd_delta` (s. `run_section`-Docstring), niemals ueber
        DIESE Instanz."""
        stop_requested, stop_reason = self.should_stop()
        # A9/D4: `usd_unknown_turns` wird AUSSCHLIESSLICH von `core/
        # admission.py:record_turn_usage` fortgeschrieben (pro echtem
        # GM-Turn, nicht ueber `LabRunner.record_turn()`) -- frisch von der
        # Platte uebernehmen, damit ein `_write_status()`-Aufruf diesen
        # Zaehler nicht mit einem veralteten In-Memory-Stand ueberschreibt.
        on_disk = read_status(self.run_dir)
        usd_unknown_turns = on_disk.usd_unknown_turns if on_disk is not None else self._usd_unknown_turns
        # B1/R3 (MAIN-KORREKTUR I2-Nacharbeit 2026-09-24): dieselbe
        # Frisch-von-der-Platte-Uebernahme wie `usd_unknown_turns` -- ein
        # `LabRunner`-eigener Statuswrite darf die von `core.admission.
        # record_usd_delta` bereits vermerkten Request-IDs nicht mit einem
        # veralteten In-Memory-Stand ueberschreiben (sonst waere ein Retry
        # NACH einem solchen Write nicht mehr gegen Doppelbuchung geschuetzt).
        reconciled_request_ids = (
            on_disk.reconciled_request_ids if on_disk is not None else self._reconciled_request_ids
        )
        # G3 (MAIN-KORREKTUR I2-Reservierungsabschluss 2026-09-24): dieselbe
        # Frisch-von-der-Platte-Uebernahme wie `reconciled_request_ids` --
        # sonst wuerde ein `LabRunner`-eigener Statuswrite die von
        # `core.admission.add_seconds` bereits vermerkten Zeit-Dedup-IDs mit
        # einem veralteten (leeren) In-Memory-Stand ueberschreiben.
        reconciled_seconds_request_ids = (
            on_disk.reconciled_seconds_request_ids if on_disk is not None
            else self._reconciled_seconds_request_ids
        )
        # G2c (Headless-/Lab-Lobbydurchstich, Bau-GO 2026-09-27, REVIEW-
        # HEADLESS-BETRIEBSGRENZEN.md Probe 04): `provider_free` ist eine
        # GETRENNTE, vertrauenswuerdige Testautoritaet (`core.admission.
        # write_test_profile`), KEINE von `LabRunner`/`LabBudget` selbst
        # ausgehende Groesse -- vorher schrieb `LabStatus(...)` dieses Feld
        # NIE explizit, sodass jeder `_write_status()`-Aufruf (auch der
        # allererste in `start()`) implizit den Dataclass-Default `None`
        # persistierte und damit eine bereits gesetzte `provider_free=True`-
        # Testfreigabe stillschweigend auf `None` degradierte (ein Labstart
        # ist KEIN stilles Test->Live-Upgrade, H-E). Frisch von der Platte
        # UEBERNEHMEN (nicht ableiten/neu setzen) erhaelt die bestehende
        # Autoritaet unveraendert -- ein Lauf OHNE vorherige `write_test_
        # profile`-Autorisierung bleibt weiterhin `None` (kein neu erfundenes
        # Testprofil durch einen echten Live-Start).
        provider_free = on_disk.provider_free if on_disk is not None else None
        status = LabStatus(
            running=True, pid=self.pid, turns_used=self._turns_used,
            seconds_elapsed=self._seconds_elapsed, usd_spent=self._usd_spent,
            stop_requested=stop_requested, stop_reason=stop_reason,
            max_turns=self.budget.max_turns, max_seconds=self.budget.max_seconds,
            max_usd=self.budget.max_usd, wall_deadline=self._wall_deadline,
            usd_unknown_turns=usd_unknown_turns,
            reconciled_request_ids=reconciled_request_ids,
            reconciled_seconds_request_ids=reconciled_seconds_request_ids,
            provider_free=provider_free,
        )
        # R2: atomarer Write (Temp-Datei + os.replace) statt direktem
        # `write_text` auf die Zieldatei -- s. `_atomic_write_json`.
        _atomic_write_json(_status_path(self.run_dir), status.__dict__)

    def run_section(self, *args, **kwargs):
        """Treibt EINEN Abschnitt ueber den gemeinsamen Application-Service
        (I1/I5/A4) -- Lab ist damit eine Betriebsart des Service, KEIN
        zweiter Loop mit eigenen Regeln (REVIEW-P2.md §I5-Korrekturrichtung).
        Verbrauchsfortschreibung passiert bereits PRO TURN in
        `core/runtime.SectionRuntime.submit()` (`core/admission.
        record_turn_usage`, dateibasiert) -- diese Methode ruft
        ABSICHTLICH NICHT zusaetzlich `self.record_turn()` auf (kein
        Doppel-Anrechnen ueber zwei unabhaengige Schreiber). Signatur
        identisch zu `core.app_service.run_play_session` (alle Argumente
        durchgereicht)."""
        from ..core.app_service import run_play_session
        return run_play_session(*args, **kwargs)

    def release(self) -> None:
        """L2 (ERGAENZUNG 4, Bau-GO 2026-09-27, REVIEW-LEASEABSCHLUSS.md §6
        Fall 05): der finale Statuswrite (`running=False`) passiert JETZT,
        WAEHREND `self._lock_fd` noch den exklusiven OS-Lock haelt --
        Freigabe (`flock(LOCK_UN)` + `close`) erst DANACH. Die alte Fassung
        entfernte zuerst die Lock-Datei und schrieb den Status ERST SPAETER;
        dazwischen konnte ein Nachfolger bereits erfolgreich starten UND
        publizieren, sodass der alte Release dessen frischen Status mit dem
        eigenen veralteten Stand ueberschrieb. Mit `flock` als Autoritaet
        ist dieses Fenster STRUKTURELL unmoeglich: solange `self._lock_fd`
        offen bleibt, kann kein anderer Prozess `_acquire_lock` erfolgreich
        durchlaufen (dessen `flock(LOCK_EX|LOCK_NB)` schlaegt zwingend fehl)
        -- der Statuswrite ist also bereits WAEHREND des Schreibens gegen
        jeden Nachfolger geschuetzt, nicht erst durch eine nachtraegliche
        `pid`-Nachpruefung. Der `pid`-Abgleich bleibt trotzdem als
        Verteidigung in der Tiefe erhalten (schuetzt z.B. gegen manuell
        von aussen manipulierte Statusdateien).

        E1-Fix (REVIEW-LEASE-AUSGAENGE.md §4, Bau-GO 2026-09-28): der
        bedingte `unlink` der Lock-Datei passiert JETZT ebenfalls NOCH
        WAEHREND die eigene `flock`-Autoritaet gehalten wird -- nicht erst
        danach. Die vorherige Fassung gab den flock zuerst frei und las/
        unlinkte danach anhand einer zu diesem Zeitpunkt bereits
        VERALTETEN PID-Lesung: ein Nachfolger konnte zwischen der
        Freigabe und diesem spaeten `unlink` bereits selbst erfolgreich
        erwerben, sodass der alte Unlink dessen frische Lease entfernte
        (zwei lebende Owner, Fall 02). `flock(LOCK_UN)` + `close(fd)`
        (der tatsaechliche Verlust der eigenen Autoritaet) erfolgen darum
        JETZT als LETZTER Schritt im `finally` -- NACH Statuswrite UND
        Unlink, nicht dazwischen. Solange die eigene Autoritaet noch
        besteht, kann kein Nachfolger seinen eigenen `flock`-Erwerb
        abschliessen und damit keine Race auf den Pfad-Eingriff mehr
        beobachten (derselbe Autoritaetsbezug wie bereits fuer den
        Statuswrite oben). `self._lock_fd` wird erst im `finally`, NACH
        dem tatsaechlichen `close`, auf `None` gesetzt."""
        if self._lock_fd is None:
            return
        fd = self._lock_fd
        try:
            status_path = _status_path(self.run_dir)
            if status_path.exists():
                try:
                    data = json.loads(status_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    data = None
                if data is not None and data.get("pid") == self.pid:
                    data["running"] = False
                    # R2: derselbe atomare Write wie `_write_status` -- ein
                    # Teilschreibfehler darf den zuletzt gueltigen
                    # autoritativen Stand nicht zerstoeren.
                    _atomic_write_json(status_path, data)
            lock_path = _lock_path(self.run_dir)
            try:
                lock_data = json.loads(lock_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                lock_data = None
            if lock_data is not None and lock_data.get("pid") == self.pid:
                lock_path.unlink()
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
            self._lock_fd = None


def read_status(run_dir: str | Path) -> LabStatus | None:
    path = _status_path(Path(run_dir))
    if not path.exists():
        return None
    return LabStatus(**json.loads(path.read_text(encoding="utf-8")))


def compute_stop_state(
    run_dir: str | Path, *, turns_used: int, seconds_elapsed: float, usd_spent: float,
    max_turns: int | None, max_seconds: float | None, max_usd: float | None,
    wall_deadline: float | None = None,
) -> tuple[bool, str | None]:
    """Reine, dateibasierte Stop-Berechnung (Stop-Flag-Datei ODER Budget-
    ueberschreitung) OHNE `LabRunner`-Instanz -- aus `LabRunner.should_stop()`
    extrahiert (F3-Fix, Critic-Nacharbeit Bau-GO 2026-09-27), damit `lab.cli.
    _status_payload` (H-C, `lab status`/`lab attach`) DENSELBEN frisch-von-
    der-Platte-Zustand berichten kann, den auch der naechste echte Request
    sehen wuerde -- statt das u.U. eingefrorene `LabStatus.stop_requested`/
    `stop_reason`-Feld vom letzten `_write_status()`-Aufruf zu spiegeln.
    `LabRunner.stop()`/das modulweite `request_stop()` schreiben bewusst
    AUSSCHLIESSLICH die separate Stop-Flag-Datei (H-C: enger, idempotenter
    Kontrollwrite, kein Reset) und rufen NIE `_write_status()` auf -- ohne
    diese Funktion blieb `lab.status.json.stop_requested` nach einem
    externen `lab stop` auf dem eingefrorenen Ausgangswert `False` stehen,
    obwohl `stop_flag_present`/`next_request_blocked` im selben `lab
    status`-JSON bereits frisch berichtet wurden (widerspruechliche Antwort).

    `max_turns`/`max_seconds` optional (statt wie in `LabBudget` verpflichtend),
    damit auch ein `LabStatus` aus einer aelteren, rueckwaertskompatiblen
    Statusdatei (dort beide `None`) ohne `TypeError` ausgewertet werden kann
    -- eine fehlende Grenze blockiert dann (wie `max_usd` bereits zuvor)
    schlicht nicht ueber diesen Kanal.

    F2-Fix (Critic-Nacharbeit, Bau-GO 2026-09-27): `wall_deadline` (optional,
    ABSOLUTER `time.time()`-Wert, s. `LabStatus.wall_deadline`-Docstring) --
    vorher wurde die reale Laufzeitgrenze NUR einmal PRO FENSTER in `lab.cli.
    _run_controller`s eigener Schleife geprueft (`time.monotonic()`,
    lokale Variable), NICHT vor jedem einzelnen Request (Initiative/Consent/
    Leader/Gast/GM/Reflexion) wie von ANSCHLUSSPLAN-HEADLESS.md Entscheidung
    4 gefordert. Diese Funktion wird sowohl von `LabRunner.should_stop()`
    (Controller-Schleife) ALS AUCH von `core.admission.read_admission_block`
    (der tatsaechliche Gate-Check vor JEDEM Request) konsultiert -- ein und
    dieselbe Deadline gilt jetzt an beiden Stellen."""
    stop_path = _stop_flag_path(Path(run_dir))
    if stop_path.exists():
        try:
            data = json.loads(stop_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
        return True, data.get("reason")
    if max_turns is not None and turns_used >= max_turns:
        return True, f"max_turns erreicht ({max_turns})"
    if max_seconds is not None and seconds_elapsed >= max_seconds:
        return True, f"max_seconds erreicht ({max_seconds})"
    # H-E (ANSCHLUSSPLAN-HEADLESS.md Entscheidung 4): `max_usd is None`
    # heisst Hybrid-Profil (Quota-unbekannt) -- KEINE Dollarpruefung,
    # keine erfundene Zahl (s. `LabBudget`-Docstring).
    if max_usd is not None and usd_spent >= max_usd:
        return True, f"max_usd erreicht ({max_usd})"
    if wall_deadline is not None and time.time() >= wall_deadline:
        return True, f"reale Laufzeitgrenze (Wall-Clock) erreicht (Deadline {wall_deadline})"
    return False, None


def active_lock_pid(run_dir: str | Path, *, exclude_pid: int | None = None) -> int | None:
    """Headless-/Lab-Lobbydurchstich (Bau-GO 2026-09-27, H-D/H06): REIN
    LESENDE Pruefung, ob fuer `run_dir` gerade ein LEBENDER Lab-Lock-Inhaber
    existiert -- OHNE eine `LabRunner`-Instanz zu konstruieren (kein
    `mkdir`, kein `read_status`-Seiteneffekt). Genutzt von
    `ui/tui.py:_cmd_lobby_initiative`/`_cmd_local_round`, damit eine
    gewoehnliche TUI waehrend eines aktiven Labs nicht heimlich zum zweiten
    Schreiber wird. Liefert `None` bei fehlendem/beschaedigtem/toten
    Lock -- eine unklare Lease-Lage ist HIER kein Fehlerfall (der Aufrufer
    behandelt `None` als "kein aktives Lab", genau wie zuvor ohne Lab).

    `exclude_pid` (Default `os.getpid()` bei Aufruf ueber die Wrapper unten,
    s. `ui/tui.py`): ein Lock, dessen PID mit `exclude_pid` uebereinstimmt,
    ist NICHT der hier gemeinte 'zweite schreibende Controller' -- H-D
    beschreibt zwei VERSCHIEDENE Prozesse um denselben `run_dir`; ein
    bestehender Testbestand (`test_i1_i2_i3_worker_matrix.py:test_i2_solo_
    play_blocked_when_lab_budget_exhausted`) konstruiert absichtlich einen
    `LabRunner` UND eine `TuiSession` in DERSELBEN Testinstanz/demselben
    Prozess, um zu belegen, dass 'dieselbe Gate-Grenze fuer JEDE Rolle,
    Mensch eingeschlossen' gilt -- dieser akzeptierte Erhaltbeleg darf durch
    den NEUEN H-D-Guard nicht faelschlich schon VOR dem Admission-Gate
    abgefangen werden."""
    lock_path = _lock_path(Path(run_dir))
    if not lock_path.exists():
        return None
    try:
        data = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    pid = data.get("pid")
    if not isinstance(pid, int) or isinstance(pid, bool):
        return None
    if exclude_pid is not None and pid == exclude_pid:
        return None
    if _pid_alive(pid):
        return pid
    return None


def request_stop(run_dir: str | Path, reason: str) -> None:
    """Headless-/Lab-Lobbydurchstich (Bau-GO 2026-09-27, H-C): `lab stop`
    ruft AUSSCHLIESSLICH diese Funktion -- KEINE `LabRunner`-Konstruktion
    (die Statusdatei/Budgetgrenzen bleiben unberuehrt, kein Reset). Identisch
    zu `LabRunner.stop()`, aber ohne dass ein Aufrufer erst eine Instanz mit
    eigenem (ggf. unpassendem) `LabBudget` bauen muss, nur um den Stop-Flag
    zu setzen. Idempotent (wiederholtes Aufrufen ueberschreibt lediglich den
    `reason`-Text derselben Flag-Datei) -- erzeugt KEINEN neuen Lauf, KEIN
    `lab.status.json`, falls noch keins existiert."""
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    _stop_flag_path(run_dir).write_text(json.dumps({"reason": reason}), encoding="utf-8")
