#!/usr/bin/env python3
"""
tests/mmo_sim/_r6_evidence_helpers.py -- ZR-BETREIBER-GASTERSCHAFFUNG-
20261105-R6: gemeinsame Export-Helfer fuer die fuenf R6-Beweisfamilien
(a_dialog, a_correction, b_import, c_teilpub, d_t2).

Dieses Modul DUPLIZIERT NICHT die battle-tested FIFO-/Prozessinteraktions-
Helfer aus `drive_r4_evidence_2026_11_04.py` (`_drain`, `_wait_for_marker`,
`_wait_for_path`, `_open_guest_fifo_pair`, `_send_op`, `_send_guest`,
`_deliver_guest_turn_answer`, `_write_gm_double_config`, `_gm_double_env`,
`_seed_guest_figure`, `_clean_env`, `_LAUNCHER`, `_J4_TOLERATED_FIXTURE`,
`_GM_DOUBLE_SPEC`) -- jeder R6-Treiber importiert `drive_r4_evidence_2026_11_04
as r4` direkt und nutzt diese unveraendert. Dieses Modul liefert NUR das vom
Briefing verlangte Exportlayout, das vom bestehenden `r4._MANIFEST`-Format
(`{files:[...], runs:[...]}`) abweicht:

- je Prozess: `<label>.stdout.txt`, `<label>.stderr.txt` (leer = echte 0-Byte-
  Datei) und `<label>.run.json` mit `{label, argv, cwd, utc_start, utc_end,
  exit}` (literales argv, echtes cwd, echte UTC-Zeiten, echter Exitcode --
  NIE aus Request-/Dateizeiten rekonstruiert).
- `MANIFEST.json`: Liste von `{aussage, teilnehmer_figur, tisch_abschnitt,
  run_id, path, sha256, bytes}` fuer jeden exportierten Koerper.
- `SUMMARY.json`: freie Struktur je Familie (von den Treibern selbst befuellt).
"""
from __future__ import annotations

import hashlib
import json
import shutil
import time
from pathlib import Path


def utc(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_process_result(
    out_dir: Path, label: str, *, argv: list, cwd: str, utc_start: str, utc_end: str,
    exit_code: int, stdout_text: str, stderr_text: str, pid: int | None = None,
) -> dict:
    """Schreibt `<label>.stdout.txt`/`.stderr.txt` (leer = echte 0-Byte-Datei)
    und `<label>.run.json`; liefert das run.json-dict zurueck (fuer SUMMARY).

    `pid` (01_NACHZUG §U5 "wirkliche argv/PIDs/Quellbindungen erfassen"): die
    reale Betriebssystem-Prozess-ID des erfassten Prozesses wird, wenn vom
    Aufrufer mitgegeben, als `pid`-Feld ins run.json aufgenommen. Optional
    (Default None -> Feld wird weggelassen), damit Aufrufer ohne echten
    Subprozess (reine In-Process-Erfassung) unveraendert bleiben."""
    out_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = out_dir / f"{label}.stdout.txt"
    stderr_path = out_dir / f"{label}.stderr.txt"
    stdout_path.write_text(stdout_text, encoding="utf-8")
    stderr_path.write_text(stderr_text, encoding="utf-8")
    run_record = {
        "label": label, "argv": list(argv), "cwd": str(cwd),
        "utc_start": utc_start, "utc_end": utc_end, "exit": exit_code,
    }
    if pid is not None:
        run_record["pid"] = int(pid)
    (out_dir / f"{label}.run.json").write_text(
        json.dumps(run_record, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    return run_record


class Manifest:
    """Sammelt die vom Briefing verlangten Koerper-Eintraege und schreibt
    MANIFEST.json/SUMMARY.json am Ende einer Familie."""

    def __init__(self, out_dir: Path):
        self.out_dir = out_dir
        self.entries: list[dict] = []

    def export_file(
        self, src: Path, rel: str, *, aussage: str, run_id: str,
        teilnehmer_figur: str | None = None, tisch_abschnitt: str | None = None,
    ) -> Path:
        dest = self.out_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        self.entries.append({
            "aussage": aussage, "teilnehmer_figur": teilnehmer_figur,
            "tisch_abschnitt": tisch_abschnitt, "run_id": run_id,
            "path": str(dest.relative_to(self.out_dir)),
            "sha256": sha256_of(dest), "bytes": dest.stat().st_size,
        })
        return dest

    def export_tree(
        self, src_root: Path, rel_root: str, *, aussage: str, run_id: str,
        teilnehmer_figur: str | None = None, tisch_abschnitt: str | None = None,
    ) -> None:
        if not src_root.exists():
            return
        for p in sorted(src_root.rglob("*")):
            if p.is_file():
                rel = str(Path(rel_root) / p.relative_to(src_root))
                self.export_file(
                    p, rel, aussage=aussage, run_id=run_id,
                    teilnehmer_figur=teilnehmer_figur, tisch_abschnitt=tisch_abschnitt,
                )

    def write_json_body(
        self, rel: str, data: object, *, aussage: str, run_id: str,
        teilnehmer_figur: str | None = None, tisch_abschnitt: str | None = None,
    ) -> Path:
        dest = self.out_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        self.entries.append({
            "aussage": aussage, "teilnehmer_figur": teilnehmer_figur,
            "tisch_abschnitt": tisch_abschnitt, "run_id": run_id,
            "path": str(dest.relative_to(self.out_dir)),
            "sha256": sha256_of(dest), "bytes": dest.stat().st_size,
        })
        return dest

    def record_process_files(
        self, label: str, *, aussage: str, run_id: str,
        teilnehmer_figur: str | None = None, tisch_abschnitt: str | None = None,
    ) -> None:
        """Nimmt die bereits von `write_process_result` geschriebenen
        `<label>.{stdout,stderr,run}` in den Manifestindex auf (ohne erneut
        zu kopieren -- sie liegen bereits direkt in `out_dir`)."""
        for suffix in ("stdout.txt", "stderr.txt", "run.json"):
            p = self.out_dir / f"{label}.{suffix}"
            if not p.exists():
                continue
            self.entries.append({
                "aussage": aussage, "teilnehmer_figur": teilnehmer_figur,
                "tisch_abschnitt": tisch_abschnitt, "run_id": run_id,
                "path": str(p.relative_to(self.out_dir)),
                "sha256": sha256_of(p), "bytes": p.stat().st_size,
            })

    def write_manifest(self) -> None:
        (self.out_dir / "MANIFEST.json").write_text(
            json.dumps(self.entries, ensure_ascii=False, indent=2), encoding="utf-8",
        )

    def write_summary(self, data: object) -> None:
        (self.out_dir / "SUMMARY.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8",
        )
