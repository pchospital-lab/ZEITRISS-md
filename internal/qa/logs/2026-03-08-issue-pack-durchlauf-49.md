---
title: "QA-Log – Issue-Pack Durchlauf 49"
date: 2026-03-08
scope: "Issue 6: Save-Größenbudget und Prune-Standard"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- Upload-Issue-Pack: `uploads/ZEITRISS_v7_save_load_issue_pack.md` (Issue 6).
- Fahrplan: `internal/qa/plans/issue-pack-durchlauf-49.md`.

## Umsetzung in diesem Durchlauf

1. **Masterprompt v7-Regeln erweitert**
   - `meta/masterprompt_v6.md` ergänzt `summaries` im Save-Template
     (`summary_last_episode`, `summary_last_rift`, `summary_active_arcs`).
   - Feste Save-Budget-Caps dokumentiert (Trace/Market/Artifact/Notes,
     Arc-Listen, Milestones pro Charakter) plus HQ-Prune-Regel.

2. **Save-Doku (Modul 12) synchronisiert**
   - `systems/gameflow/speicher-fortsetzung.md` führt `summaries.*` im
     Kompakt-Profil.
   - Neue Sektion zum OpenWebUI-Save-Budget mit Rolling-Caps und Verdichtung
     älterer Verlaufsdetails in `summaries.*`.

3. **SL-Referenz + README nachgezogen**
   - `core/sl-referenz.md` spiegelt `summaries.*` im persistenten Save-Schema
     und nennt dieselben Caps.
   - `README.md` ergänzt einen knappen OpenWebUI-Hinweis zum Save-Budget,
     damit Integratoren den JSON-Korridor direkt sehen.

4. **QA-Status aktualisiert**
   - `internal/qa/process/known-issues.md` um Durchlauf 49 erweitert.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.

## Ergebnis / Anschluss

- Save-Größenbudget ist als v7-Standard dokumentarisch konsistent verankert.
- Offene Restblöcke aus ZR-017 bleiben: SSOT-Bereinigung der letzten Legacy-Textreste,
  Mixed-Split-Protokoll, Px-Zustandsautomat und vollständige v7-E2E-Fixtures.
