---
title: "Issue-Pack Durchlauf 148 - Hard-Final-Review Runtime-Toolkit Entdevifizierung"
version: 1.0.0
tags: [qa, plan, runtime, toolkit, ssot]
---

# Ziel

Den verbleibenden Runtime-Ballast im produktiven Toolkit reduzieren, indem
QA-/Smoke-Spiegelinhalte aus dem aktiven Wissensspeicher entfernt werden.

## Scope

- `systems/toolkit-gpt-spielleiter.md`
- `internal/qa/process/known-issues.md`
- QA-Log für Durchlauf 148

## Checkliste

1. Produktiven HQ-Loop-Contract im Toolkit von QA-Flag-Hinweisen bereinigen.
2. Runtime-Spiegel der Acceptance-Smoke-Checkliste aus dem Toolkit entfernen
   (QA bleibt in `docs/` und `internal/`).
3. ZR-021-Statusspur in `known-issues.md` um Durchlauf 148 ergänzen.
4. Pflicht-Smoke ausführen (`bash scripts/smoke.sh`).

## Anschluss / Offene Watchpoints

- Falls künftig erneut QA-Spiegel in Runtime-Slots landen, per Watchguard oder
  Review-Regel auf `internal/`-/`docs/`-Verweise in produktiven Wissensmodulen
  prüfen.
