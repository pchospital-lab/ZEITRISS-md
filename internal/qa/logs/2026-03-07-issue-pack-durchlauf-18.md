---
title: "QA-Log – Issue-Pack Durchlauf 18"
date: 2026-03-07
scope: "Ton-Kanon Core/Rift/Mythic konsolidieren (Issue 8)"
status: abgeschlossen
tags: [qa, log]
---

## Quelle
- `uploads/ZEITRISS_codex_issue_pack.md` (Issue 8: Ton-Bibel für Core/Rift/Mythic).

## Umsetzung in diesem Durchlauf

1. **Spieler-Handbuch ergänzt (`core/spieler-handbuch.md`)**
   - Neuer SSOT-Block "Ton-Kanon (SSOT)" mit verbindlichem Ebenenmodell:
     Core-Ops (Default), Rift-Ops (Default), Mythic-/Lore-Layer (optional).
   - Leitregel ergänzt: Mythic ist Zusatzstoff nur nach expliziter Freigabe.

2. **Kampagnenübersicht geschärft (`gameplay/kampagnenuebersicht.md`)**
   - Neue "Ton-Bibel (Core/Rift/Mythic)" im Gameplay-Indexbereich.
   - Introtext auf geerdeten Default und explizites Layering ausgerichtet.

3. **Generator-Modul gewichtet (`gameplay/kreative-generatoren-missionen.md`)**
   - Verbindliche Ton-Gewichtung ergänzt: Core plausibel-operativ,
     Rift One-Weird-Thing investigativ, Mythic nur per Opt-in.

4. **QA-Nachführung**
   - Fahrplan/Log für Durchlauf 18 angelegt.
   - `internal/qa/process/known-issues.md` (ZR-016) um Durchlauf 18 erweitert.

## Checks
- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
