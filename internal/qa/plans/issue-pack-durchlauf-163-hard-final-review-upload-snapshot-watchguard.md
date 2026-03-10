---
title: "Issue-Pack Durchlauf 163 – Hard-Final-Review Upload-Snapshot-Watchguard"
date: 2026-03-10
status: abgeschlossen
owner: codex
scope: Runtime/QA + Meta/Prozess
issue: ZR-021
---

# Ziel

Der Upload-Kontext aus `uploads/hard-final-review.md` soll dauerhaft als
historischer Snapshot abgesichert bleiben, damit der Dateiinhalt nicht erneut
als aktiver SSOT missverstanden wird.

# Arbeitspaket

1. Watchguard für `uploads/hard-final-review.md` ergänzen.
2. Pflicht-Smoke um den neuen Guard erweitern.
3. Prozessspur synchronisieren (`known-issues.md`,
   `hard-final-review-next-steps.md`, Durchlauf-Log).
4. Pflicht-Smoke ausführen.

# Abnahmekriterien

- `tools/test_upload_snapshot_watchguard.js` prüft Snapshot-Markierung und
  Verweise auf die aktiven Prozessseiten.
- `scripts/smoke.sh` enthält den neuen Pflicht-Guard.
- Prozessseiten sind auf Durchlauf 163 synchronisiert.
- `bash scripts/smoke.sh` ist grün.
