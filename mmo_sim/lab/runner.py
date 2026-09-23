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

import json
import os
from dataclasses import dataclass, field
from pathlib import Path


class SingletonViolationError(RuntimeError):
    pass


@dataclass
class LabBudget:
    """Explizite Betreibergrenzen (03 §6) — OHNE Default-"unbegrenzt"."""

    max_turns: int
    max_seconds: float
    max_usd: float


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


def _lock_path(run_dir: Path) -> Path:
    return run_dir / "lab.lock.json"


def _status_path(run_dir: Path) -> Path:
    return run_dir / "lab.status.json"


def _stop_flag_path(run_dir: Path) -> Path:
    return run_dir / "lab.stop"


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
        else:
            self._turns_used = 0
            self._seconds_elapsed = 0.0
            self._usd_spent = 0.0
            self._usd_unknown_turns = 0

    def start(self) -> None:
        """Wirft `SingletonViolationError`, wenn bereits ein LEBENDER Lock-
        Inhaber existiert (kein zweiter schreibender Controller, 02 §8/A12)."""
        lock_path = _lock_path(self.run_dir)
        if lock_path.exists():
            data = json.loads(lock_path.read_text(encoding="utf-8"))
            other_pid = data.get("pid")
            if isinstance(other_pid, int) and other_pid != self.pid and _pid_alive(other_pid):
                raise SingletonViolationError(
                    f"Lab-Lauf bereits aktiv (pid={other_pid}) fuer {self.run_dir} — "
                    f"kein zweiter schreibender Simulationscontroller."
                )
        lock_path.write_text(json.dumps({"pid": self.pid}), encoding="utf-8")
        if _stop_flag_path(self.run_dir).exists():
            _stop_flag_path(self.run_dir).unlink()
        self._write_status()

    def stop(self, reason: str) -> None:
        """Setzt ein Stop-Flag — der laufende Prozess (derselbe oder ein
        angehefteter Status-Leser) prueft `should_stop()` vor jedem neuen
        Request und pausiert dann geordnet, statt hart abzubrechen."""
        _stop_flag_path(self.run_dir).write_text(
            json.dumps({"reason": reason}), encoding="utf-8",
        )

    def should_stop(self) -> tuple[bool, str | None]:
        if _stop_flag_path(self.run_dir).exists():
            data = json.loads(_stop_flag_path(self.run_dir).read_text(encoding="utf-8"))
            return True, data.get("reason")
        if self._turns_used >= self.budget.max_turns:
            return True, f"max_turns erreicht ({self.budget.max_turns})"
        if self._seconds_elapsed >= self.budget.max_seconds:
            return True, f"max_seconds erreicht ({self.budget.max_seconds})"
        if self._usd_spent >= self.budget.max_usd:
            return True, f"max_usd erreicht ({self.budget.max_usd})"
        return False, None

    def record_turn(self, seconds: float, usd: float) -> None:
        """Budget WIRD VOR dem naechsten Request geprueft (`should_stop`),
        Verbrauch NACH der Antwort verrechnet (03 §6: 'vor neuen Requests
        Budget reservieren, nach Antwort tatsaechliche Usage verrechnen')."""
        self._turns_used += 1
        self._seconds_elapsed += seconds
        self._usd_spent += usd
        self._write_status()

    def _write_status(self) -> None:
        stop_requested, stop_reason = self.should_stop()
        # A9/D4: `usd_unknown_turns` wird AUSSCHLIESSLICH von `core/
        # admission.py:record_turn_usage` fortgeschrieben (pro echtem
        # GM-Turn, nicht ueber `LabRunner.record_turn()`) -- frisch von der
        # Platte uebernehmen, damit ein `_write_status()`-Aufruf diesen
        # Zaehler nicht mit einem veralteten In-Memory-Stand ueberschreibt.
        on_disk = read_status(self.run_dir)
        usd_unknown_turns = on_disk.usd_unknown_turns if on_disk is not None else self._usd_unknown_turns
        status = LabStatus(
            running=True, pid=self.pid, turns_used=self._turns_used,
            seconds_elapsed=self._seconds_elapsed, usd_spent=self._usd_spent,
            stop_requested=stop_requested, stop_reason=stop_reason,
            max_turns=self.budget.max_turns, max_seconds=self.budget.max_seconds,
            max_usd=self.budget.max_usd, usd_unknown_turns=usd_unknown_turns,
        )
        _status_path(self.run_dir).write_text(
            json.dumps(status.__dict__, ensure_ascii=False, indent=2), encoding="utf-8",
        )

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
        lock_path = _lock_path(self.run_dir)
        if lock_path.exists():
            data = json.loads(lock_path.read_text(encoding="utf-8"))
            if data.get("pid") == self.pid:
                lock_path.unlink()
        status_path = _status_path(self.run_dir)
        if status_path.exists():
            data = json.loads(status_path.read_text(encoding="utf-8"))
            data["running"] = False
            status_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_status(run_dir: str | Path) -> LabStatus | None:
    path = _status_path(Path(run_dir))
    if not path.exists():
        return None
    return LabStatus(**json.loads(path.read_text(encoding="utf-8")))
