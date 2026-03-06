---
title: "QA-Log – Issue-Pack Durchlauf 15"
date: 2026-03-06
scope: "Issue 2: Wallet-/Ökonomie-SSOT (HQ-Pool-Wording) nachschärfen"
status: abgeschlossen
tags: [qa, log]
---

## Quelle
- Externer Pack `uploads/ZEITRISS_codex_issue_pack.md`, Schwerpunkt Issue 2
  (Wallet-/Ökonomie-Modell kanonisieren).
- Folgearbeit aus Durchlauf 03/04 mit verbleibenden Textdrifts bei
  Arena-/Debrief-Hinweisen.

## Umsetzung in diesem Durchlauf

1. **Arena-Einstieg konsolidiert (`gameplay/kampagnenstruktur.md`)**
   - Gebührenfluss auf `economy.hq_pool` als Primärpfad umgestellt.
   - Credits-Fallback nur noch als Legacy-Importsynchronisierung benannt.

2. **Toolkit-Referenzen nachgezogen (`systems/toolkit-gpt-spielleiter.md`)**
   - `arenaStart()`-Beschreibung auf `economy.hq_pool` umgestellt.
   - Debrief-Hinweis `HQ-Pool` ebenfalls auf `economy.hq_pool` normalisiert.

3. **SL-Referenz synchronisiert (`core/sl-referenz.md`)**
   - Phase-Strike-/Arena-Hinweis auf `economy.hq_pool` aktualisiert.
   - Debrief- und String-Input-Abschnitt auf HQ-Pool + `characters[].wallet`
     als Zielmodell präzisiert.

4. **QA-Nachführung**
   - Fahrplan/Log für Durchlauf 15 ergänzt.
   - `internal/qa/process/known-issues.md` (ZR-016) um Durchlauf 15 erweitert.

## Checks
- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
