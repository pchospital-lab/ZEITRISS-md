---
title: "QA-Log Durchlauf 147 - Hard-Final-Review Slot-Count SSOT-Sync"
version: 1.0.0
tags: [qa, log, meta, ssot, onboarding]
---

# Kontext

Im Hard-Final-Review blieb ein Maintainer-Drift offen:
AGENTS führte noch 20 WS-/Slot-Einträge, während README und Setup-Doku
bereits den produktiven Default mit 19 Wissensmodulen ausweisen.

## Umgesetzte Änderungen

1. `AGENTS.md`
   - Zählung auf den echten Default harmonisiert:
     - `19 WS-Dateien + Masterprompt`
     - `19 Wissensspeicher-Module + Masterprompt`
     - `19 Slots (Spieler-Handbuch + 18 Runtime-Module)`

2. `internal/qa/process/known-issues.md`
   - ZR-021 um den Anschlusslauf 147 ergänzt
     (Slot-Count-SSOT-Sync).

## Verifikation

- Pflicht-Smoke erfolgreich (`bash scripts/smoke.sh`).

## Ergebnis

Der Setup-/Onboarding-SSOT ist wieder konsistent: AGENTS, README und
Setup-Doku verwenden dieselbe Default-Slotzählung und vermeiden damit
künftige Maintainer-Verwirrung beim Wissensspeicher-Setup.
