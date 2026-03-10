---
title: "Log – Durchlauf 163 (Hard-Final-Review / Upload-Snapshot-Watchguard)"
date: 2026-03-10
status: abgeschlossen
owner: codex
scope: Runtime/QA + Meta/Prozess
issue: ZR-021
---

## Kontext

Die Anschlussübersicht führte als offenen Punkt weiterhin, historische
Upload-Reviews klar als Snapshot zu markieren. Obwohl
`uploads/hard-final-review.md` bereits einen Hinweisblock enthält, fehlte noch
eine automatische Regression-Absicherung im Pflicht-Smoke.

## Umsetzung

- Neuer Guard `tools/test_upload_snapshot_watchguard.js` ergänzt.
- Guard prüft in `uploads/hard-final-review.md`:
  - explizite Snapshot-Kennzeichnung (`historischer Snapshot`),
  - Verweis auf `internal/qa/process/known-issues.md`,
  - Verweis auf `internal/qa/process/hard-final-review-next-steps.md`.
- `scripts/smoke.sh` um den neuen Pflicht-Check erweitert
  (`upload-snapshot-watchguard-ok`).
- Prozessseiten synchronisiert:
  - `internal/qa/process/hard-final-review-next-steps.md`
  - `internal/qa/process/known-issues.md`

## Ergebnis

Der Upload-Kontext ist jetzt nicht nur redaktionell, sondern auch per
Pflicht-Watchguard abgesichert. Damit ist der historische Review-Snapshot gegen
späteren Drift im regulären Smoke-Gate geschützt.

## Checks

- `node tools/test_upload_snapshot_watchguard.js` erfolgreich.
- `bash scripts/smoke.sh` erfolgreich.
