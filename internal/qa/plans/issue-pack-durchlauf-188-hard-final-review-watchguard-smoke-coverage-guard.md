# Fahrplan – Durchlauf 188 (Hard-Final-Review Watchguard-Smoke-Coverage-Guard)

## Kontext

Der Loader-/Label-Standard der Watchguards ist inzwischen gut abgesichert,
aber ein strukturelles Rest-Risiko bleibt: Neue `test_*watchguard.js` können
angelegt werden, ohne in `scripts/smoke.sh` als Pflichtcheck aufzutauchen.

## Ziel

- Sicherstellen, dass jeder Watchguard technisch im Pflicht-Smoke verankert ist.
- Stale-/Doppel-Referenzen in `scripts/smoke.sh` automatisch erkennen.
- QA-/Prozessspur auf Durchlauf-188-Stand fortführen.

## Arbeitspakete

1. Neuen Meta-Guard `tools/test_watchguard_smoke_coverage.js` einführen.
2. Meta-Guard in `scripts/smoke.sh` als Pflichtcheck aufnehmen.
3. Checkliste `watchguard-neuanlage-checkliste.md` um den neuen
   Coverage-Anker schärfen.
4. Prozessseiten (`known-issues.md`, `hard-final-review-next-steps.md`) auf
   Durchlauf 188 synchronisieren.
5. Pflicht-Smoke ausführen (`bash scripts/smoke.sh`).

## Abnahme

- Neuer Meta-Guard meldet bei vollständiger Abdeckung
  `watchguard-smoke-coverage-ok`.
- Smoke schlägt fehl, wenn ein Watchguard nicht in `scripts/smoke.sh`
  eingebunden ist oder stale/doppelt referenziert wird.
- Prozessseiten verweisen auf Durchlauf 188.
- `bash scripts/smoke.sh` läuft vollständig grün.
