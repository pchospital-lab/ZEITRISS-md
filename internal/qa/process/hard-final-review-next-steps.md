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
  - `watchguard-smoke-coverage-ok`
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
- Durchlauf 187 härtet den Meta-Guard weiter auf Smoke-Output-Kohärenz:
  `watchguard-loader-consistency` erzwingt nun pro `test_*watchguard.js`
  auch das erwartete Ergebnis-Token (`<dateiname-normalisiert>-ok`) via
  `console.log(...)`; die Neuanlage-Checkliste enthält dazu jetzt eine
  explizite Dateiname→Token-Regel.
- Durchlauf 188 ergänzt einen strukturellen Coverage-Guard:
  `test_watchguard_smoke_coverage.js` erzwingt, dass alle
  `test_*watchguard.js` in `scripts/smoke.sh` enthalten sind und keine
  stale/doppelten Referenzen bestehen.
- Durchlauf 189 härtet den Coverage-Guard auf Dateinamen-Varianten:
  `test_watchguard_smoke_coverage.js` erfasst jetzt auch
  `test_*watchguard_*.js`, damit Meta-Watchguards mit Zusatzsuffix nicht
  aus der Abdeckungsprüfung fallen.

- Durchlauf 190 schließt den offenen v7-SSOT-Feinschliff: Save-Doku, Schema, Fixtures und v7-Guards wurden auf einen einheitlich schlanken HQ-Exportvertrag gehärtet (ohne Root-`location`/`phase`, mit verpflichtender Lineage + Root-Blöcken), plus Sync-Fixes für Auto-HQ-Flow und 19-Module-Setuptext.

- Durchlauf 191 zieht einen verbleibenden Slot-Count-Unsync nach: `docs/maintainer-ops.md` ist jetzt ebenfalls auf den 19er-Defaultpfad (Spieler-Handbuch + 18 Runtime-Module) synchronisiert.
- Durchlauf 192 bereinigt verbleibende LP-Terminologie-Drift in spielnahen aktiven Texten (Ablösung von „HP/Hitpoints“ durch „LP“ in Gameplay- und Runtime-Stub-Ausgaben), ohne Regeländerung.
- Durchlauf 193 führt die Sozialkonflikt-Formulierung in Modul 7 zurück auf den Wurfkern (CHA/SG bei Normalo-NSCs, Oppositionswurf bei Named-NPCs) und markiert Wortgefecht-Leisten nur noch als optionales Erzähl-Overlay.
- Durchlauf 194 präzisiert die Terminologie in Modul 7: kein separates Willenskraft-Attribut, sondern CHA (Charisma) als Attribut, das u. a. Willenskraft abbildet.
- Durchlauf 195 präzisiert den Sozialkonflikt-Flow im Sinne des Pen-&-Paper-Spiels: erst Ausspielen/SL-Bewertung, dann nur bei unklarem oder aktiv umkämpftem Ausgang SG-/Oppositionswurf.
- Durchlauf 196 schärft die Save-Doku semantisch nach: zwei weiterhin vorhandene Legacy-Bridge-Beispiele in `speicher-fortsetzung.md` sind jetzt explizit als Legacy markiert (`Legacy-Bridge`, `v: 6`, Klarhinweis zu `location`/`phase` als reine Migrationsfelder), damit kein zweiter v7-Exportpfad suggeriert wird.

- Durchlauf 197 schließt einen verbliebenen LP-Restdrift im QA-Evidenzpfad: `internal/qa/playtest-2026-02-22-deep.sh` nutzt in der statischen Assistant-Nachricht nun `LP` statt `HP`, damit auch Playtest-Skripte die kanonische Spielerterminologie konsistent abbilden.

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
