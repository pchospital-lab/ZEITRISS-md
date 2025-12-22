---
title: "QA-Evidenz Index 2025"
version: 0.1.1
tags: [meta, qa]
---

# QA-Evidenz – Beta-GPT-Läufe 2025

Dieser Ordner bündelt die Nachweise (HUD-Dumps, Save-Ausschnitte,
Dispatcher-Transkripte), die die Beta-GPT-Logs zur Validierung der
Regressionstests verlangen. Maintainer:innen kopieren die relevanten
Ausschnitte nach Abschluss eines Laufs hier hinein und verlinken sie in
den zugehörigen QA-Log-Abschnitten.

## Dateien

- [`2025-beta-gpt-evidenz.md`](2025-beta-gpt-evidenz.md) – Sammelprotokoll
  für die Beta-GPT-Läufe vom 05.07., 18.07. und 15.10.2025 mit Checklisten
  für jede geforderte Evidenz.
- [`2026-10-plattform-contract-action-gewalt.md`](2026-10-plattform-contract-action-gewalt.md)
  – Quellenmemo zum Plattform-Contract „Action & Gewalt“ (Outcome statt Anleitung).

## Workflow

1. Beta-GPT-Lauf durchführen und das Rohprotokoll wie gewohnt unter
   `internal/qa/logs/` archivieren.
2. Relevante HUD-/Save-/Dispatcher-Auszüge in dieses Evidenzprotokoll
   übertragen und die Checkboxen abhaken.
3. Die verlinkten QA-Log-Einträge aktualisieren (Statuskommentar) und das
   Audit auf den neuen Evidenzstand verweisen.

So bleiben Audit, Fahrplan, QA-Log und Evidenzsammlung synchron, sobald die
Beta-GPT-Läufe erneut „live" geprüft werden.
