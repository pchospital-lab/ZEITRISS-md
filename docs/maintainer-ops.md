---
title: "Maintainer-Ops"
version: 1.2.2
tags: [meta]
---

# Maintainer-Ops

Dieses Memo bündelt alle internen Abläufe für den Betrieb von
**ZEITRISS 4.2.6**. Haltet die Schritte strikt ein, damit QA, Releases und
Plattform-Listings synchron bleiben.

## Wissensspeicher & Grundsetup

Der vollständige Datensatz für GPTs und Custom-AIs besteht aus folgenden
Bestandteilen. Die Wissensspeicher-Slots sind für `README.md` plus die 19 Runtime-Module
reserviert - der Masterprompt bleibt im Systemfeld (oder als erste
Chatnachricht), Repo-Hilfsdateien bleiben offline:

1. **Masterprompt:** `meta/masterprompt_v6.md` (Local-Uncut 4.2.6, Systemfeld
   bzw. erste Nachricht). Die Vorversion liegt als Referenz in
   `meta/archive/masterprompt_v6_legacy.md`.
2. **README:** `README.md` als Wissensmodul für Einstieg, Einleitung und
   Betriebsnavigation hochladen.
3. **Runtime-Module:** Exakt die unten aufgelisteten 19 Markdown-Dateien aus
   den Runtime-Verzeichnissen (`core/`, `characters/`, `gameplay/`, `systems/`).
4. **Nicht hochladen:** `master-index.json` bleibt ein repo-internes
   Steuerdokument für Setup-Automation und QA.

> **Slot-Kontrolle:** Nach jedem Upload, Export oder Speicherstand prüfen, ob
> alle 20 Wissensmodule (README + 19 Runtime-Module) geladen sind.
> Fehlende oder veraltete Module unverzüglich nachfordern und erneut hochladen.

| Kategorie    | Datei |
|--------------|-------|
| **characters** | `characters/ausruestung-cyberware.md` |
|              | `characters/charaktererschaffung-grundlagen.md` |
|              | `characters/charaktererschaffung-optionen.md` |
|              | `characters/zustaende.md` |
|              | `characters/hud-system.md` |
| **core**     | `core/wuerfelmechanik.md` |
|              | `core/zeitriss-core.md` |
|              | `core/sl-referenz.md` |
| **gameplay** | `gameplay/fahrzeuge-konflikte.md` |
|              | `gameplay/kampagnenstruktur.md` |
|              | `gameplay/kampagnenuebersicht.md` |
|              | `gameplay/kreative-generatoren-begegnungen.md` |
|              | `gameplay/kreative-generatoren-missionen.md` |
|              | `gameplay/massenkonflikte.md` |
| **systems**  | `systems/currency/cu-waehrungssystem.md` |
|              | `systems/gameflow/cinematic-start.md` |
|              | `systems/gameflow/speicher-fortsetzung.md` |
|              | `systems/kp-kraefte-psi.md` |
|              | `systems/toolkit-gpt-spielleiter.md` |

### Runtimes & Tests außerhalb des Wissensspeichers

- `internal/runtime/runtime-stub-routing-layer.md`, `runtime.js`, Skripte und
  Tools verbleiben ausschließlich im Repo.
- **Repo-Agent:innen verpflichten sich, jede bestätigte Laufzeitänderung
  unmittelbar als Regelwerk, Prozessbeschreibung oder Pseudocode in den
  Wissensspeicher-Modulen zu spiegeln** (z. B. README, Runtime-Handbücher).
  Nur so erreichen produktive GPTs denselben Funktionsumfang ohne lokale
  Skripte.
- Halte einen Abgleich im QA-Journal fest (`internal/qa/logs/`), sobald du eine
  Laufzeitänderung spiegelst. Notiere Commit-ID, Datum und die Module, die den
  Pseudocode/Regeltext enthalten.
- Nutze lokale Runtimes weiter für Entwicklung und Tests; dokumentiere
  Abweichungen zwischen Skript und Wissensbasis, bis sie synchronisiert sind.
  Maintainer:innen prüfen im Review, ob dieser Wissensspiegel vorliegt, bevor
  sie Plattform-Runtimes aktualisieren.

### Spiegelhinweis für Laufzeitänderungen

- Prüft nach jedem Merge, ob `runtime.js` oder andere Offline-Laufzeitdateien
  angepasst wurden.
- Übertragt bestätigte Änderungen manuell in die produktive Runtime der
  Plattform (MyGPT/Store-GPT) gemäß Abschnitt
  ["Spiegelprozess nach QA-Freigabe"](#spiegelprozess-nach-qa-freigabe).
  Grundlage ist stets der durch den Repo-Agenten bereits vollständig
  gespiegelte Wissensstand.
- Dokumentiert den Mirror im QA-Log inkl. Commit-ID, Datum und Hinweis darauf,
  welches Wissensspeicher-Modul die Pseudocode-/Regelspiegelung enthält, damit
  Foreshadow-Log und andere Laufzeitfeatures ingame verfügbar bleiben.

Hinweise zum Rollenmodell (Repo-Agent, MyGPT, Beta-GPT, Kodex) stehen in
`AGENTS.md`. Eine Dokumenten-Landkarte mit Zielgruppen und Übergabepunkten
findest du im Abschnitt
[„Dokumenten-Landkarte"](setup-guide.md#dokumenten-landkarte) des Setup-Guides. Diese
Datei konzentriert sich auf ausführbare Abläufe.

**Grundsatz:** Alle QA-Läufe finden ausschließlich im OpenAI-MyGPT-Beta-Klon
statt. Erst nach einer grünen Abnahme werden Store-GPT und OpenWebUI-Instanzen mit genau diesem Stand gespiegelt; separate Optimierungen für andere
Plattformen sind derzeit nicht vorgesehen.

## QA-Plattformstrategie

- **Referenz-Plattform:** Der Beta-Klon von **ZEITRISS [Ver. 4.2.6]** auf
  OpenAI-MyGPT ist die einzige Instanz für aktive QA-Läufe. Alle
  Regressionstests, Acceptance-Smokes und Save/Load-Prüfungen werden hier
  durchgeführt und anschließend im QA-Log abgelegt.
- **Freigabebedingung:** Erst nachdem der Beta-Klon die QA als "grün" meldet
  und Codex die Nachverfolgung im QA-Fahrplan geschlossen hat, darf der
  Wissensstand auf weitere Plattformen gespiegelt werden.
- **Spiegelroutine:** Store-GPT und OpenWebUI-Installationen erhalten
  ausschließlich den freigegebenen Stand. Abweichungen oder Ergänzungen werden
  nicht eigenständig ausprobiert, sondern als Findings an Codex zurückgegeben.
- **Dokumentation:** Jede Spiegelung wird mit Datum, Zielplattform und Verweis
  auf den passenden QA-Log-Abschnitt dokumentiert. Nur so bleibt nachvollziehbar,
  welche Plattform welchen Stand lädt.

## QA-Artefakte & Nachverfolgung

- [QA-Fahrplan 2025](../internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md) -
  priorisierte Maßnahmenliste mit Status-Tracking und Commit-Verweisen.
- [QA-Audit 2025](../internal/qa/audits/ZEITRISS-qa-audit-2025.md) -
  Zusammenfassung der Testläufe inklusive Bewertungsmatrix.
- [Beta-QA-Log 2025](../internal/qa/logs/2025-beta-qa-log.md) - vollständige
  Copy-&-Paste-Protokolle aus Beta-GPT/MyGPT mit Nachverfolgung.
- [Tester-Playtest-Briefing](./qa/tester-playtest-briefing.md) -
  Standardauftrag für Beta-/MyGPT-Läufe inklusive Acceptance-Smoke.

Stand 2025-06-22: Deepcheck-Sessions 2025-06-11-2025-06-16 abgeschlossen,
Maßnahmenblöcke (Save, HUD/UX, PvP/Arena) auf ✅ gesetzt; siehe QA-Fahrplan &
QA-Log 2025-06-22.

Verknüpfe jede QA-Maßnahme in PR-Beschreibungen mit dem passenden Log-Abschnitt
und aktualisiere Audit sowie Fahrplan nach dem Merge. Aktuelle QA-Läufe finden
ausschließlich im OpenAI-MyGPT-Beta statt. Der Standardprompt aus dem
Tester-Playtest-Briefing lässt den GPT den gesamten QA-Lauf autonom simulieren
und liefert strukturierte `ISSUE`-, `Lösungsvorschlag`-, `To-do`- und
`Nächste Schritte`-Blöcke für Codex. Store-GPT und OpenWebUI-Instanzen
spiegeln erst nach erfolgreicher MyGPT-Abnahme denselben Stand ohne zusätzliche
Plattformoptimierung.

### Solo-Maintainer-Workflow (Stand 2025)

- **Arbeitsaufteilung:** Aktuell betreut eine Person das Projekt. Alle
  Repositoriumsaufgaben laufen über Codex (Repo-Agent). Operative QA- und
  Playtest-Sessions erfolgen ausschließlich im Beta-GPT, indem ein vorbereiteter
  Testprompt in den Chat gelegt wird.
- **Übergabeformat:** Die Beta-GPT-Antwort bündelt den vollständigen QA-Run samt
  `ISSUE`-, `Lösungsvorschlag`-, `To-do`- und `Nächste Schritte`-Blöcken. Diese
  Ausgabe wird unverändert in ein neues Anweisungsfenster für Codex kopiert.
  Codex überträgt daraus die erforderlichen Änderungen in Repo-Dateien,
  Fahrpläne und QA-Logs.
- **Nachweise:** Der Testprompt deckt Acceptance-Smokes, Regressionen und
  Spiegel-Checks ab. Codex dokumentiert die Ergebnisse in den Maintainer- und
  QA-Dokumenten und referenziert die jeweiligen Chatlogs.
- **Erweiterbarkeit:** Sollte sich das Team vergrößern, bleibt dieser Ablauf
  gültig, bis eine alternative Rollenaufteilung dokumentiert wird. Zusätzliche
  Maintainer:innen richten eigene Beta-Klone ein und liefern ihre Ergebnisse in
  derselben Form an Codex.

### Standardbefehl für Repo-Agent:innen

Nutze für Folgeaufträge immer dieselbe Kurzform, damit Codex den QA-Fahrplan
Schritt für Schritt abarbeitet und nur Repo-Artefakte aktualisiert:

> `Codex, arbeite bitte den QA-Fahrplan (internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md)
> Schritt für Schritt ab und setze die genannten Maßnahmen direkt im Repo um.
> Spiegle jede Laufzeitänderung in den Wissensmodulen (README, Systems-Module)
> und halte die Trennung zwischen Runtime-Stubs (runtime.js, routing-layer) und
> den GPT-Laufzeitdateien strikt ein.`

Der Zusatz stellt klar, dass lokale Hilfsskripte (z. B. `runtime.js`) nur für
Tests dienen und alle ingame-relevanten Inhalte in die Wissensmodule gehören.

## Plattform-Workflows

### OpenAI MyGPT & GPT-Store
1. Einen Custom GPT **ZEITRISS [Ver. 4.2.6]** erstellen.
2. Einen Pitch mit max. 300 Zeichen hinterlegen, z. B. "Zeitreise-RPG mit
   Kodex-HUD, explosiven Würfeln und Solo/Coop-Balancing. Keine echten Daten,
   mehr Infos auf https://zeitriss.org/".
3. `meta/masterprompt_v6.md` (Local-Uncut 4.2.6) vollständig in das
   Masterprompt-Feld kopieren und speichern. Die Legacy-Fassung liegt bei
   Bedarf in `meta/archive/masterprompt_v6_legacy.md`.
4. `README.md` und alle 19 Runtime-Module (ohne Runtime-Stub) in den
   Wissensspeicher hochladen. `master-index.json` nicht hochladen.
5. Den GPT direkt klonen und **ZEITRISS [Ver. 4.2.6] beta** nennen.
6. Sämtliche QA-Sessions ausschließlich im Beta-Klon durchführen und Verhalten
   im QA-Log dokumentieren.
7. QA und Publishing erst freigeben, wenn die Chat-Historie keine
   personenbezogenen Daten enthält.
8. Nach bestandener QA den Stand in den Haupt-GPT übertragen und erst danach
   das Store-Listing aktualisieren. Vermerkt die Spiegelung mit Verweis auf den
   QA-Log-Eintrag des grünen Runs.

### Lokaler Betrieb (Ollama + OpenWebUI)
1. Nach erfolgreicher MyGPT-Abnahme Ollama mit dem gewünschten Modell
   installieren und OpenWebUI lokal verbinden.
2. Entweder `./scripts/setup-openwebui.sh` ausführen oder manuell
   Masterprompt plus 20 Wissensmodule (README + 19 Runtime-Module) importieren.
3. Es erfolgen derzeit keine dedizierten lokalen Optimierungen; prüfe nur, ob
   der freigegebene Stand geladen wird, und notiere Abweichungen im QA-Log.

### Spiegelprozess nach QA-Freigabe

1. Prüfe im QA-Fahrplan, dass der relevante Abschnitt als abgeschlossen markiert und mit Commit-ID
   versehen ist.
2. Exportiere den Wissensspeicher aus dem MyGPT-Beta-Klon (README + 19 Runtime-Module).
3. Übertrage den Stand unverändert in den produktiven MyGPT und dokumentiere
   Datum sowie QA-Log-Referenz.
4. Spiegele denselben Export im Anschluss auf Store-GPT und lokale
   OpenWebUI-Instanzen in dieser Reihenfolge. Jede Plattform erhält exakt
   denselben Datei-Satz.
5. Ergänze im QA-Log einen kurzen Spiegelvermerk (Plattform, Datum,
   verantwortliche Person). Abweichungen werden als neue Findings festgehalten.

### Sync-Checks & Beispielworkflow

- Nach jedem freigegebenen Update bestätigen, dass MyGPT und Store-GPT denselben
  Stand führen (Masterprompt + README + 19 Runtime-Module) und den Release
  anschließend auf OpenWebUI spiegeln.
- Sicherstellen, dass exakt 20 Wissensmodule geladen sind; der Runtime-Stub
  bleibt außen vor.
- Für Schnelltests die Checkliste aus
  [Acceptance-Smoke](./qa/tester-playtest-briefing.md#acceptance-smoke-checkliste)
  nutzen und Ergebnisse hier protokollieren.
- Detailablauf für Uploads siehe Abschnitt "Beispielworkflow" im README; dort
  stehen die Datei-Checks, die beim Laden kontrolliert werden.

## Go-Live-Checkliste (Build 4.2.6)
Vor der Spiegelung auf produktive Plattformen sind die folgenden Schritte
abzuschließen und im QA-Log zu dokumentieren:

1. **Repository-Prüfungen**
   - `make lint` (inkl. doppeltem Runtime-Lint, Doc-Link- und Umlaut-Checks sowie
     Markdownlint für Wissensmodule)
   - `make test`
   - `npm run test:acceptance` (Mission-5-Badge-/HUD-Snapshots gegen Golden File)
   - `npm run test:hud`
   - `npm run test:debrief`
   - `npm run test:comms`
   Alle Läufe müssen ohne Fehler durchlaufen; Warnungen werden im Commit-Log
   vermerkt.
2. **Dokumentationsabgleich**
   - Audit, Fahrplan und Maintainer-Ops auf denselben Stand bringen (Versionen
     prüfen, offene Fragen schließen, QA-Referenzen ergänzen).
   - README-Sektion "QA-Artefakte & Nachverfolgung" auf aktuelle Links testen.
3. **QA-Log & Freigabe**
  - Acceptance-Smoke gegen
    [Acceptance-Smoke](./qa/tester-playtest-briefing.md#acceptance-smoke-checkliste)
    abhaken und den Lauf im QA-Log mit Datum, Plattform und Build-ID
    protokollieren.
   - Offene Punkte im QA-Log schließen oder vertagen (inkl. Verweis auf den
     verantwortlichen Commit).
4. **Spiegelentscheidung**
   - Erst wenn alle obigen Schritte grün sind, Beta-GPT → Produktiv-GPT →
     Store-GPT → lokale OpenWebUI-Instanzen spiegeln.
   - Jede Spiegelung mit Datum, Plattform und QA-Log-Verweis festhalten.

## QA-Loop & Speicherstände
Halte für QA und Save/Load-Checks den Übergabeprozess in
`CONTRIBUTING.md#beta-gpt-qa-uebergaben` ein. Ergänzend gilt:

### Beta-GPT & Playtests
1. Klone nach jedem Release-Kandidaten den produktiven MyGPT zu
   **ZEITRISS [Ver. 4.2.6] beta**.
2. Starte Playtests ausschließlich im Beta-Klon, füge den Auftrag aus
   `docs/qa/tester-playtest-briefing.md` in die erste Chat-Nachricht ein und lasse
   den GPT den kompletten QA-Run ohne weitere Eingriffe simulieren.
3. Prüfe, dass die Antwort die geforderten `ISSUE`-, `Lösungsvorschlag`-,
   `To-do`- und `Nächste Schritte`-Blöcke je Befund enthält, und übertrage sie
   gesammelt und unverändert an Codex (Repo-Agent). Codex erstellt daraus
   Tickets, dokumentiert Freigaben und aktualisiert QA-/Maintainer-Docs.
4. Notiere im QA-Log, welcher Beta-GPT-Prompt verwendet wurde, damit spätere
   Regressionen denselben Ablauf nachvollziehen können.
5. Synchronisiere den Wissensspeicher des produktiven MyGPT sowie weiterer
   Plattformen erst, nachdem Codex die QA als grün markiert hat.

### Übergabe an Codex & Dokumentation
1. Exportiere nach jeder Beta-GPT-Session das vollständige Chatlog (inklusive
   Debug-Ausgaben) und sende es unverändert an Codex. Die vom GPT erzeugten
   `ISSUE`-, `Lösungsvorschlag`-, `To-do`- und `Nächste Schritte`-Blöcke ersetzen
   separate Stichpunktlisten.
2. Markiere im Log klar die Plattform (Standard: MyGPT Beta auf openai.com),
   den Build-Stand und den verwendeten Wissensspeicher.
3. Notiere in deiner Übergabe, ob Uploads, Save/Load-Checks oder
   Plattformspiegelungen bereits erfolgt sind. Codex übernimmt daraufhin die
   Pflege der Dateien `internal/qa/logs/2025-beta-qa-log.md`,
   `internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md` und
   `internal/qa/audits/ZEITRISS-qa-audit-2025.md` im
   Repo.
4. Nachdem Codex die QA-Dokumente aktualisiert und alle Findings abgearbeitet
   hat, spiegelst du den freigegebenen Stand auf Store-GPT und lokale OpenWebUI-Instanzen. Dokumentiere Abweichungen ausschließlich dann, wenn sie
   vom MyGPT-Referenzlauf abweichen.

### Zusätzliche QA-Pflichten
1. Plane mindestens drei komplette Durchläufe im MyGPT-Beta ein; weitere
   Plattformen erhalten denselben Stand ohne eigenständige QA-Schleifen.
2. In jeder Session Save/Load prüfen: `saveGame({...})` ausgeben lassen, lokal
   sichern, neuen Chat öffnen und den Reimport testen.
3. Accessibility-Dialoge (HUD-Erklärung, Offline-Hinweise) und
   HQ-Briefing-Schleifen abgleichen.
4. Acceptance-Smoke-Checklist aus `docs/qa/tester-playtest-briefing.md`
   ergänzen und Abweichungen festhalten. Smoketests laufen bei jedem Merge
   automatisch im Repo; dokumentiert ergänzende Befunde weiterhin im QA-Log.
5. Falls die GitHub-Action `scripts/smoke.sh` mit einem `ECONNRESET` beim
   Artefakt-Upload scheitert, Job erneut anstoßen. Der Fehler entsteht beim
   Finalisieren des Uploads und erfordert inhaltlich keine Anpassung am Repo.

### Regressionstest-Zeitplan 2025

- **Q1 2025 (19.03.2025 - Acceptance-Smoke-Abgleich)**
  - Schwerpunkt: Vollständiger Regressionstest (Build 4.2.6) mit Save/Load.
  - Status: ✅ abgeschlossen.
  - QA-Log: `internal/qa/logs/2025-beta-qa-log.md`, Abschnitt 2025-03-19.
- **Q2 2025 (09.-13.06.2025)**
  - Schwerpunkt: Spiegelprozesse, Save/Load-Regression und Upload-Checks.
  - Status: 🗓️ geplant.
  - QA-Log: Eintrag folgt nach Lauf.
- **Q3 2025 (08.-12.09.2025)**
  - Schwerpunkt: Arena-Großteam-Regression, HUD-Badges und Timer.
  - Status: 🗓️ geplant.
  - QA-Log: Eintrag folgt nach Lauf.
- **Q4 2025 (08.-12.12.2025)**
  - Schwerpunkt: Jahresabschluss-Regression mit Spiegelkontrolle.
  - Status: 🗓️ geplant.
  - QA-Log: Eintrag folgt nach Lauf.

> Aktualisiere Termine bei Verschiebungen unmittelbar im QA-Fahrplan und hier;
> Spiegelplattformen nur nach grüner MyGPT-Abnahme synchronisieren.

## Systemgrenzen (Reminder)
- KI-Spielleitung kann keine Dateien schreiben oder Repos verändern;
  Speicherstände nur via Copy & Paste.
- Save-Funktionen laufen ausschließlich über das HQ. Missionen lassen sich
  abbrechen, aber nicht zwischen-speichern.
- MyGPT und Store-GPT laufen online ohne Webtool. Ollama/OpenWebUI bleiben vollständig offline und ohne Webtools.
- DSGVO-konforme Chats sicherstellen: keine realen personenbezogenen Daten
  posten, keine unverschlüsselten Log-Transkripte.

## Release-Checkliste
- Versionierung nach **MAJOR.MINOR.PATCH**. `CHANGELOG.md`, `README.md`,
  `master-index.json` und Store-Listing synchron aktualisieren.
- Rechtliche Hinweise prüfen (`docs/trademark.md`, `LICENSE`,
  Markenverweise im README).
- `make lint`, `make test` und `scripts/smoke.sh` ausführen; Ergebnisse im
  QA-Log vermerken.
- Vor Freigabe sicherstellen, dass auf jeder Plattform exakt 20
  Wissensmodule (README + 19 Runtime-Module) plus Masterprompt vorliegen -
  ohne den Runtime-Stub und ohne `master-index.json` im Wissensspeicher.
- Erst releasen, wenn der Beta-GPT auf MyGPT grün meldet. Danach Store-GPT aktualisieren und den freigegebenen Stand lokal in
  OpenWebUI spiegeln. Siehe
  `CONTRIBUTING.md#beta-gpt-qa-uebergaben` für die Übergabe an Codex.
