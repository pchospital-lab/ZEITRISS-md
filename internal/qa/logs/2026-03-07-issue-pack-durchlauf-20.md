---
title: "QA-Log – Issue-Pack Durchlauf 20"
date: 2026-03-07
scope: "Boss-Endzustände filmisch auf Festsetzungspfad ziehen"
status: abgeschlossen
tags: [qa, log]
---

## Quelle
- Maintainer-Feedback auf Durchlauf 19: Boss-/Mini-Boss-Gegner bei 0 LP primär
  nicht töten, sondern schwer verletzt festsetzen und ITI-Richterpfad stärken.

## Umsetzung in diesem Durchlauf

1. **Spieler-Handbuch nachgeschärft (`core/spieler-handbuch.md`)**
   - Rift-Formulierung von „Akte-X-Vibe" auf markenfreie
     „Mystery-Casefile-Fallfilm"-Sprache umgestellt.
   - Block "Einsatzgewalt & Endzustände (Filmstandard)" angepasst:
     Core-Bosse/Mini-Bosse bei 0 LP primär besiegt + schwer verletzt +
     festsetzbar; ITI-Richterpfad als Standard.
   - Todesentscheidungen als Ausnahmefälle in Schlüsselmomenten verankert.

2. **Boss-Generator ergänzt (`gameplay/kreative-generatoren-begegnungen.md`)**
   - Neue Endzustand-Policy im Boss-Generator: Core-Mini-/Episodenbosse bei
     0 LP standardmäßig festsetzen (ITI-Gewahrsam statt Soforttod).

3. **QA-Nachführung**
   - Fahrplan/Log für Durchlauf 20 ergänzt.
   - `internal/qa/process/known-issues.md` (ZR-016) um Durchlauf 20 erweitert.

## Checks
- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
