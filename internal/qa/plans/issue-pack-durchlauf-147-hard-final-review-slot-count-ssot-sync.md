---
title: "Issue-Pack Durchlauf 147 - Hard-Final-Review Slot-Count SSOT-Sync"
version: 1.0.0
tags: [qa, plan, meta, ssot, onboarding]
---

# Ziel

Den verbleibenden Maintainer-Drift zur Wissensspeicher-Anzahl schließen:
AGENTS muss dieselbe Default-Zählung wie README/Setup führen
(19 Slots = Spieler-Handbuch + 18 Runtime-Module).

## Scope

- `AGENTS.md`
- `internal/qa/process/known-issues.md`
- QA-Log für Durchlauf 147

## Checkliste

1. AGENTS-Zählung auf den tatsächlichen Default-Stack synchronisieren.
2. Begriffspaare in AGENTS konsistent halten (WS-Dateien, Wissensmodule, Slots).
3. Prozessspur in Known-Issues um Durchlauf 147 ergänzen.
4. Pflicht-Smoke ausführen (`bash scripts/smoke.sh`).

## Anschluss / Offene Watchpoints

- Bei künftigen Slot-Änderungen zuerst `master-index.json` und Setup-Pipeline,
  danach README/Setup-Guide/AGENTS in einem Durchlauf gemeinsam anpassen.
