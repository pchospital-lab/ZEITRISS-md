---
title: "Hard-Final-Review – Anschlussübersicht"
date: 2026-03-10
status: aktiv
owner: codex
scope: Runtime/QA + Meta/Prozess
---

# Zweck

Diese Seite ist die kompakte Arbeitsübersicht nach Abschluss der Hard-Final-
Review-Runde (Durchläufe 145–154). Sie dient als schneller Einstieg für den
nächsten Anschlusslauf.

## Aktueller Stand (Kurzfassung)

- ZR-021 ist in `known-issues.md` als **abgeschlossen** dokumentiert.
- Die Kernpunkte aus dem Hard Final Review sind umgesetzt und über
  Pflicht-Watchguards im Smoke abgesichert:
  - `default-slot-dependency-watchguard-ok`
  - `director-layer-watchguard-ok`
  - `hard-final-review-watchguard-ok`
  - `chronopolis-gate-watchguard-ok`
  - `upload-snapshot-watchguard-ok`
  - `process-compactness-watchguard-ok`
  - `watchguard-loader-consistency-ok`
- Pflicht-Smoke bleibt der zentrale Merge-Gate-Check.
- Durchlaufhistorie wurde zur Anschlussfähigkeit kompakt gehalten:
  - Historie 73–156: `internal/qa/process/archive/known-issues-durchlaufhistorie-73-156.md`
  - Historie 157–179: `internal/qa/process/archive/hard-final-review-durchlaufhistorie-157-179.md`
- Durchlauf 180 fokussiert auf Prozesspflege: Anschlussübersicht entschlackt
  und Detailhistorie 157–179 ins Archiv ausgelagert.
- Durchlauf 181 härtet den Meta-Guard weiter: `watchguard-loader-consistency`
  erzwingt jetzt zusätzlich den `scopeLabel` im `createDocTextLoader(...)`
  aller Watchguards.
- Durchlauf 182 bereinigt den Onboarding-Watchguard technisch auf direkte
  Loader-Nutzung (`readText`/`getDocText` aus `createDocTextLoader(...)`)
  und entfernt lokale Wrapper-/Direktlese-Helfer.
- Durchlauf 183 härtet den Meta-Guard gegen Kommentar-Drift und erzwingt,
  dass Loader-Lese-APIs (`readMarkdown`/`getDocText`/`readText`) direkt aus
  `createDocTextLoader(...)` gebunden werden.
- Durchlauf 184 normiert die `scopeLabel`-Diagnostik im Meta-Guard:
  `scopeLabel` muss auf `Watchguard` enden und darf keine Slash-Zeichen
  enthalten.
- Durchlauf 185 härtet die Label-Kohärenz weiter: `scopeLabel` muss jetzt
  semantisch zum jeweiligen Guard-Dateinamen passen (Token-Vergleich im
  Meta-Guard), damit Diagnosebezüge in Smoke/CI eindeutig bleiben.
- Durchlauf 186 ergänzt ein Neuanlage-Playbook für künftige Guards:
  `tools/templates/watchguard.template.js` als Startpunkt plus
  `internal/qa/process/watchguard-neuanlage-checkliste.md` als
  Maintainer-Checkliste.

## Offene Anschluss-Tasks (priorisiert)

1. **Resolver-/Loader-Standard bei neuen/angepassten Guards fortführen**
   - Bei jeder künftigen Guard-Neuanlage standardmäßig
     `createDocTextLoader` (inkl. `readMarkdown`/`getDocText`) nutzen und
     keine Einzellösungen mehr einführen.
   - Für Neuanlagen die Checkliste
     `internal/qa/process/watchguard-neuanlage-checkliste.md` und das
     Template `tools/templates/watchguard.template.js` als Startpunkt nutzen.
2. **Prozessseiten weiter schlank halten**
   - Der `process-compactness-watchguard` schützt Grundanker + Zeilenbudget;
     lange Durchlaufprosa weiterhin nur in Archive/Statusmatrizen führen.
3. **Weltstatus-Rückkopplung stabil halten**
   - Bei künftigen Textanpassungen die Formel
     „genau eine Weltstatus-Zeile pro Missionszyklus aus
     `arc.factions/questions/hooks` mit Folgewirkung“ in allen
     Runtime-SSOT-Referenzen synchron halten.

## Operativer Ablauf für nächste Durchläufe

1. Scope im neuen Plan unter `internal/qa/plans/` festhalten.
2. Änderungen durchführen.
3. `bash scripts/smoke.sh` ausführen.
4. Ergebnis im Log unter `internal/qa/logs/` dokumentieren.
5. `known-issues.md` + diese Anschlussübersicht synchron aktualisieren.

## Referenzen

- Prozessstatus: `internal/qa/process/known-issues.md`
- Historischer Review-Snapshot: `uploads/hard-final-review.md`
- Archiv 157–179: `internal/qa/process/archive/hard-final-review-durchlaufhistorie-157-179.md`
- Neuanlage-Checkliste: `internal/qa/process/watchguard-neuanlage-checkliste.md`

---
