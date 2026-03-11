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

- Durchlauf 198 schließt eine verbleibende LP-Restdrift im aktiven Gameplay-Regeltext: Der Teamgrößen-Pseudocode in `gameplay/massenkonflikte.md` nutzt jetzt `effektive_LP = LP_Pool × ceil(team_size / 2)` statt `effektive_HP = HP_Pool × ...`, damit die Terminologie auch in Regel-Formeln konsistent bleibt.

- Durchlauf 199 schließt die verbleibende LP-Restdrift in einem aktiven QA-Playtestskript: `internal/qa/playtest-2026-02-22-round2.sh` nutzt in der Gladiator-Startnachricht nun `LP 12/12` statt `HP 12/12`, damit die Terminologie auch in Round2-Evidenzpfaden konsistent bleibt.

- Durchlauf 200 verankert einen dauerhaften LP-Terminologie-Watchguard im Pflicht-Smoke: `tools/test_lp_terminology_watchguard.js` scannt aktive Runtime-/QA-Pfade fail-fast auf `\bHP\b|Hitpoints`, und `scripts/smoke.sh` grept auf `lp-terminology-watchguard-ok`.

- Durchlauf 201 schließt eine verbleibende aktive Slot-Count-Restdrift im QA-Audit: `internal/qa/audits/ZEITRISS-qa-audit-2025.md` verwendet nun konsistent den kanonischen 19er-Defaultpfad (Spieler-Handbuch + 18 Runtime-Module) statt einer veralteten 20er-Formulierung.

- Durchlauf 202 schärft die Lesesicherheit im Legacy-Bridge-Bereich von `systems/gameflow/speicher-fortsetzung.md`: Eine explizite Leseregel stellt direkt am großen HQ-Beispiel klar, dass `v: 7` dort ausschließlich als Import-/Migrations-Bridge zu lesen ist und kein kanonischer v7-Neu-Exportpfad entsteht.
- Durchlauf 203 schärft den Chronopolis-Play-Contract über drei SSOT-Ebenen: `core/spieler-handbuch.md` ergänzt den Spieler-Merksatz „freier Infiltrationslauf“, `meta/masterprompt_v6.md` verankert Spielmodus + Reaktionslogik (genau ein Beat pro bedeutsamer Aktion), und `gameplay/kampagnenstruktur.md` ergänzt die Leitplanken 4A/4B/4C inklusive seltener Apex-Bedrohung bevorzugt auf Rückweg/Exit.
- Durchlauf 204 synchronisiert die sichtbare Modul-6-Kapitelbenennung auf den gehärteten Chronopolis-Contract: Indexeintrag + Kapitelüberschrift in `gameplay/kampagnenstruktur.md` führen Chronopolis nun explizit als „Freier Infiltrationslauf“ statt „Endgame-Hub“.
- Durchlauf 205 synchronisiert verbleibende Chronopolis-Lesedrift in `core/sl-referenz.md`: Die Formulierungen „ohne Missionsdruck“/Hub-Lesart wurden auf den gehärteten Runtime-Contract (freier Infiltrationslauf mit Reaktionsdruck) nachgezogen.
- Durchlauf 206 synchronisiert die verbliebene Dev-Doku-Lesedrift in `docs/dev/chronopolis-map-blueprint.md`: Der Abschluss verweist nun auf den Chronopolis-Spielmodus als freier Infiltrationslauf statt auf die Altbenennung „Endgame-Hub“.
- Durchlauf 207 ergänzt einen kompakten Playtest-Go/No-Go-Gate in `internal/qa/process/playtest-readiness-gate.md`, damit Setup, Pflicht-Smoke, Invarianten-Kurzcheck und Evidence-Ablage vor neuen Testrunden verbindlich abgeprüft werden.
- Durchlauf 208 verankert die Gate-Nutzung zusätzlich im Pre-Test-Workflow: `docs/qa/tester-playtest-briefing.md` und die Deepsearch-Anschlusscheckliste in `internal/qa/process/continuity-redesign-statusmatrix.md` verweisen jetzt explizit auf das verpflichtende Vorab-Abarbeiten des Playtest-Gates.
- Durchlauf 209 synchronisiert den Chronopolis-Kodex-Sperrmodus in den Runtime-SSOT-Dateien (Spieler-Handbuch, SL-Referenz, HUD-System, Masterprompt, Kampagnenstruktur, Toolkit): In `CITY` gilt jetzt eindeutig „Kodex dunkel, HUD lebendig“ inkl. `!offline`-Sonderantwort statt Re-Sync-Rezept.
- Durchlauf 210 schärft das Wording nach Review-Feedback: SaveGuard-Re-Sync in `core/sl-referenz.md` ist jetzt klar auf reguläre Offline-Missionen außerhalb Chronopolis begrenzt (HQ-Kern wieder online), und die Sperrmodus-Begründung benennt explizit das Echo-Kollapsrisiko der von Kodex instanzierten CITY-Zeitlinie (HUD + Masterprompt).
- Durchlauf 211 verankert einen Lore-Guard `ABSOLUT-7` in den Runtime-SSOTs (Spieler-Handbuch, SL-Referenz, Masterprompt, Kampagnenstruktur, Toolkit): Chronopolis darf als kodex-instanziierter Resonanzraum angedeutet werden, bleibt spielpraktisch aber strikt physischer Infiltrationsraum statt Matrix-/Digitalraum-Modus.
- Durchlauf 212 führt die Doppel-Lesbarkeit um `ABSOLUT-7` zusammen: `systems/kp-kraefte-psi.md` enthält jetzt den expliziten Chronopolis-Anhang `ABSOLUT-7/CITY`, und die Runtime-SSOTs verwenden denselben Marker als Zusatzfall des Absolut-7-Projektionsmodells statt als separates zweites Konstrukt.
- Durchlauf 213 schließt verbleibende Mikro-Restdrift im Chronopolis-Kodex-Contract: kompakte HUD-/FAQ-/Befehlsformulierungen in `characters/hud-system.md`, `core/sl-referenz.md` und `core/spieler-handbuch.md` markieren Vollzugriff nun explizit als **außerhalb `CITY`** und kennzeichnen `kodex [thema]` im Spieler-Handbuch eindeutig als **in `CITY` gesperrt**.
- Durchlauf 214 ergänzt den dauerhaften Runtime-Guard für diesen Contract: `tools/test_chronopolis_kodex_lockout_watchguard.js` prüft im Pflicht-Smoke (`scripts/smoke.sh`) die Crossfile-Anker für Chronopolis-Sperrmodus (`Kodex dunkel, HUD lebendig`), `!offline`-Sonderantwort in `CITY`, `kodex [thema]`-Sperre in `CITY` und HQ-Vollzugriff explizit außerhalb `CITY`.
- Durchlauf 215 ergänzt die Lore-Klammer für Langzeitspiel in den Runtime-SSOTs (`core/spieler-handbuch.md`, `core/sl-referenz.md`): Zeitriss als Kausalwunde, Absolut/Nullzeit/Zeitriss als Zustände derselben Grenzphysik, Kodex als Bruchlinien-Koppler (nicht Realitäts-"Erschaffer") sowie der Merksatz `ABSOLUT-7 liest keine Zukunft. Es macht Bruchlinien lesbar.`
- Durchlauf 216 ergänzt in `core/sl-referenz.md` direkt am Weltstatus-Pflichtsatz eine Leitformel für Langzeitspiel: Jeder gelöste Einsatz stabilisiert die Hauptlinie und verhindert, dass Bruchwelten als Riss/Echo/Kreatur in die Wirklichkeit zurückdrücken.

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
4. **Playtest-Gate vor externen Testrunden anwenden**
   - Vor jedem neuen Playtest-Lauf die Checkliste
     `internal/qa/process/playtest-readiness-gate.md` vollständig durchgehen
     (inkl. Pflicht-Smoke und Evidence-Pfad).
   - Diese Reihenfolge auch in den operativen Vordokumenten halten:
     `docs/qa/tester-playtest-briefing.md` und
     `internal/qa/process/continuity-redesign-statusmatrix.md`.
5. **Chronopolis-Sperrmodus stabil halten**
   - Bei Änderungen an Comms/Kodex/HUD den CITY-Contract parallel prüfen:
     _Kodex dunkel, HUD lebendig_, keine freien Kodex-Abfragen in Chronopolis,
     `!offline` mit eigener Sperrmodus-Antwort.
   - Für Regressionsschutz den Pflicht-Guard
     `tools/test_chronopolis_kodex_lockout_watchguard.js` als Referenz nutzen
     und bei Scope-Erweiterungen synchron nachziehen.
   - Auch kurze FAQ-/Menütexte auf `CITY`-Scope prüfen (keine unqualifizierten
     „Vollzugriff“-Formulierungen ohne den Zusatz außerhalb `CITY`).

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
- Playtest-Gate: `internal/qa/process/playtest-readiness-gate.md`

---
