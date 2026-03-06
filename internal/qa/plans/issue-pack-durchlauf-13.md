---
title: "Issue-Pack Fahrplan – Durchlauf 13"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 13

Quelle: `uploads/ZEITRISS_codex_issue_pack.md`

## Ziel
Issue 10 aus dem externen Pack weiterführen: Chronopolis-Logik zwischen
Instanzraum (`CITY`) und HQ-Kanon klarer trennen, damit Persistenz- und
Service-Aussagen im Runtime-Kanon nicht gegeneinander laufen.

## Scope dieses Durchlaufs

- Präzisierung in `gameplay/kampagnenuebersicht.md`:
  - explizite Chronopolis-Instanzlogik (`CITY`) formulieren,
  - klare Trennung zwischen instanzlokalen Zuständen und HQ-Persistenz,
  - HQ-Kernprozesse (Shop/Lizenz/Klinik/Speichern) als HQ-exklusiv verankern.
- QA-Nachführung:
  - neues Durchlauf-Log,
  - ZR-016 in `internal/qa/process/known-issues.md` um Durchlauf 13 erweitern.

## Nicht im Scope (bewusst verschoben)

- Vollständiger Sweep aller Chronopolis-Verweise in sämtlichen Runtime-Modulen.
- Zusätzliche Runtime-Lints speziell für Chronopolis-Persistenzbegriffe.
- Strukturänderungen am Save-Schema selbst.

## Exit-Kriterium für Durchlauf 13

- Chronopolis-Abschnitt in der Kampagnenübersicht enthält einen klaren
  SSOT-Block zur Instanzlogik und Persistenztrennung.
- `bash scripts/smoke.sh` läuft grün.
