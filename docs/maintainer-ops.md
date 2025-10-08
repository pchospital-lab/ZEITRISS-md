---
title: "Maintainer-Ops"
version: 1.2.1
tags: [meta]
---

# Maintainer-Ops

Dieses Memo bündelt alle internen Abläufe für den Betrieb von
**ZEITRISS 4.2.2**. Haltet die Schritte strikt ein, damit QA, Releases und
Plattform-Listings synchron bleiben.

## Wissensspeicher & Grundsetup

Der vollständige Datensatz für GPTs und Custom-AIs besteht aus folgenden
Bestandteilen und wird in jeder Zielplattform in den Wissensspeicher geladen:

1. **Masterprompt:** `meta/masterprompt_v6.md`
2. **Dokumentationsanker:** `README.md` und `master-index.json`
3. **Runtime-Module:** Exakt die unten aufgelisteten 18 Markdown-Dateien aus den Runtime-Verzeichnissen.

| Kategorie    | Datei |
|--------------|-------|
| **characters** | `characters/ausruestung-cyberware.md` |
|              | `characters/charaktererschaffung.md` |
|              | `characters/cyberware-und-bioware.md` |
|              | `characters/psi-talente.md` |
|              | `characters/zustaende-hud-system.md` |
| **core**     | `core/wuerfelmechanik.md` |
|              | `core/zeitriss-core.md` |
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

Optional kann der Masterprompt zusätzlich als Wissensspeicher-Eintrag
gesichert werden, um lange Sessions stabil zu halten.

> **Abgrenzung:** `systems/runtime-stub-routing-layer.md`, `runtime.js`, Skripte und Tools verbleiben ausschließlich im Repo.
> `runtime.js` dient als Offline-Laufzeit für QA-Tests (siehe `tools/`-Suite) und wird nicht in produktive Wissensspeicher
> übernommen.

Hinweise zum Rollenmodell (Repo-Agent, MyGPT, Beta-GPT, Kodex) stehen in
`AGENTS.md`. Eine Dokumenten-Landkarte mit Zielgruppen und Übergabepunkten findest du im
Abschnitt [„Dokumenten-Landkarte“](../README.md#dokumenten-landkarte) des README. Diese Datei
konzentriert sich auf ausführbare Abläufe.

**Grundsatz:** Alle QA-Läufe finden ausschließlich im OpenAI-MyGPT-Beta-Klon
statt. Erst nach einer grünen Abnahme werden Store-GPT, Proton LUMO und lokale
Instanzen mit genau diesem Stand gespiegelt; separate Optimierungen für andere
Plattformen sind derzeit nicht vorgesehen.

## QA-Plattformstrategie

- **Referenz-Plattform:** Der Beta-Klon von **ZEITRISS [Ver. 4.2.2]** auf OpenAI-MyGPT ist die einzige
  Instanz für aktive QA-Läufe. Alle Regressionstests, Acceptance-Smokes und
  Save/Load-Prüfungen werden hier durchgeführt und anschließend im QA-Log
  abgelegt.
- **Freigabebedingung:** Erst nachdem der Beta-Klon die QA als „grün“ meldet
  und Codex die Nachverfolgung im QA-Fahrplan geschlossen hat, darf der
  Wissensstand auf weitere Plattformen gespiegelt werden.
- **Spiegelroutine:** Store-GPT, Proton LUMO und lokale Installationen erhalten
  ausschließlich den freigegebenen Stand. Abweichungen oder Ergänzungen werden
  nicht eigenständig ausprobiert, sondern als Findings an Codex zurückgegeben.
- **Dokumentation:** Jede Spiegelung wird mit Datum, Zielplattform und Verweis
  auf den passenden QA-Log-Abschnitt dokumentiert. Nur so bleibt nachvollziehbar,
  welche Plattform welchen Stand lädt.

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

## Plattform-Workflows

### OpenAI MyGPT & GPT-Store
1. Einen Custom GPT **ZEITRISS [Ver. 4.2.2]** erstellen.
2. Einen Pitch mit max. 300 Zeichen hinterlegen, z. B. „Zeitreise-RPG mit
   Kodex-HUD, explosiven Würfeln und Solo/Coop-Balancing. Keine echten Daten,
   mehr Infos auf https://zeitriss.org/“.
3. `meta/masterprompt_v6.md` vollständig in das Masterprompt-Feld kopieren und
   speichern.
4. `README.md`, `master-index.json` sowie alle 18 Runtime-Module (ohne
   Runtime-Stub) in den Wissensspeicher hochladen.
5. Optional den Masterprompt zusätzlich im Wissensspeicher sichern, damit
   längere Sessions stabil bleiben.
6. Den GPT direkt klonen und **ZEITRISS [Ver. 4.2.2] beta** nennen.
7. Sämtliche QA-Sessions ausschließlich im Beta-Klon durchführen. Die Plattform
   läuft online, besitzt aber kein Web-Tool; dokumentiert das Verhalten im
   QA-Log.
8. QA und Publishing erst freigeben, wenn die Chat-Historie keine
   personenbezogenen Daten enthält.
9. Nach bestandener QA den Stand in den Haupt-GPT übertragen und erst danach
   das Store-Listing aktualisieren. Vermerkt die Spiegelung mit Verweis auf den
   QA-Log-Eintrag des grünen Runs.

### Proton LUMO (verschlüsselter Chat)
1. Nach erfolgreicher MyGPT-Abnahme die LUMO-App starten und einen neuen Chat
   öffnen.
2. `meta/masterprompt_v6.md`, `README.md`, `master-index.json` und alle
   Runtime-Module (ohne Runtime-Stub) über die Büroklammer hochladen.
3. Optional alle Dateien in den Wissensspeicher übernehmen.
4. Den Masterprompt zusätzlich als Chatnachricht einfügen, damit die Rolle zu
   Beginn fixiert ist.
5. Plattform wird aktuell nicht separat optimiert; dokumentiere nur
   Abweichungen, falls LUMO den freigegebenen Stand nicht übernimmt, und
   verlinke sie im QA-Log.

### Lokaler Betrieb (Ollama + OpenWebUI)
1. Nach erfolgreicher MyGPT-Abnahme Ollama mit dem gewünschten Modell
   installieren und OpenWebUI lokal verbinden.
2. Masterprompt, README, Master-Index und alle Runtime-Module importieren
   (Upload oder Wissensbibliothek).
3. Es erfolgen derzeit keine dedizierten lokalen Optimierungen; prüfe nur, ob
   der freigegebene Stand geladen wird, und notiere Abweichungen bei Bedarf im
   QA-Log.

### Spiegelprozess nach QA-Freigabe

1. Prüfe im QA-Fahrplan, dass der relevante Abschnitt als abgeschlossen markiert und mit Commit-ID
   versehen ist.
2. Exportiere den Wissensspeicher aus dem MyGPT-Beta-Klon (Masterprompt, README, master-index und
   Runtime-Module).
3. Übertrage den Stand unverändert in den produktiven MyGPT und dokumentiere
   Datum sowie QA-Log-Referenz.
4. Spiegele denselben Export im Anschluss auf Store-GPT, Proton LUMO und lokale
   Instanzen in dieser Reihenfolge. Jede Plattform erhält exakt denselben
   Datei-Satz.
5. Ergänze im QA-Log einen kurzen Spiegelvermerk (Plattform, Datum,
   verantwortliche Person). Abweichungen werden als neue Findings festgehalten.

### Sync-Checks & Beispielworkflow

- Nach jedem freigegebenen Update bestätigen, dass MyGPT und Store-GPT denselben
  Stand führen (Masterprompt, README, Module) und den Release anschließend auf
  LUMO sowie lokal spiegeln.
- Sicherstellen, dass exakt 18 Runtime-Module plus `master-index.json` geladen
  sind; der Runtime-Stub bleibt außen vor.
- Für Schnelltests die Checkliste aus
  [Acceptance-Smoke](./qa/tester-playtest-briefing.md#acceptance-smoke-checkliste)
  nutzen und Ergebnisse hier protokollieren.
- Detailablauf für Uploads siehe Abschnitt „Beispielworkflow“ im README; dort
  stehen die Datei-Checks, die beim Laden kontrolliert werden.

## Go-Live-Checkliste (Build 4.2.2)
Vor der Spiegelung auf produktive Plattformen sind die folgenden Schritte
abzuschließen und im QA-Log zu dokumentieren:

1. **Repository-Prüfungen**
   - `make lint`
   - `make test`
   - `npm run test:hud`
   - `npm run test:debrief`
   - `npm run test:comms`
   Alle Läufe müssen ohne Fehler durchlaufen; Warnungen werden im Commit-Log
   vermerkt.
2. **Dokumentationsabgleich**
   - Audit, Fahrplan und Maintainer-Ops auf denselben Stand bringen (Versionen
     prüfen, offene Fragen schließen, QA-Referenzen ergänzen).
   - README-Sektion „QA-Artefakte & Nachverfolgung“ auf aktuelle Links testen.
3. **QA-Log & Freigabe**
  - Acceptance-Smoke gegen
    [Acceptance-Smoke](./qa/tester-playtest-briefing.md#acceptance-smoke-checkliste)
    abhaken und den Lauf im QA-Log mit Datum, Plattform und Build-ID
    protokollieren.
   - Offene Punkte im QA-Log schließen oder vertagen (inkl. Verweis auf den
     verantwortlichen Commit).
4. **Spiegelentscheidung**
   - Erst wenn alle obigen Schritte grün sind, Beta-GPT → Produktiv-GPT →
     Store-GPT → Proton LUMO → lokale Instanzen spiegeln.
   - Jede Spiegelung mit Datum, Plattform und QA-Log-Verweis festhalten.

## QA-Loop & Speicherstände
Halte für QA und Save/Load-Checks den Übergabeprozess in
`CONTRIBUTING.md#beta-gpt-qa-uebergaben` ein. Ergänzend gilt:

### Beta-GPT & Playtests
1. Klone nach jedem Release-Kandidaten den produktiven MyGPT zu
   **ZEITRISS [Ver. 4.2.2] beta**.
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
   hat, spiegelst du den freigegebenen Stand auf Store-GPT, Proton LUMO und
   lokale Instanzen. Dokumentiere Abweichungen ausschließlich dann, wenn sie
   vom MyGPT-Referenzlauf abweichen.

### Zusätzliche QA-Pflichten
1. Plane mindestens drei komplette Durchläufe im MyGPT-Beta ein; weitere
   Plattformen erhalten denselben Stand ohne eigenständige QA-Schleifen.
2. In jeder Session Save/Load prüfen: `saveGame({...})` ausgeben lassen, lokal
   sichern, neuen Chat öffnen und den Reimport testen.
3. Accessibility-Dialoge (HUD-Erklärung, Sofa-Modus, Offline-Hinweise) und
   HQ-Briefing-Schleifen abgleichen.
4. Acceptance-Smoke-Checklist aus `docs/qa/tester-playtest-briefing.md`
   ergänzen und Abweichungen festhalten. Smoketests laufen bei jedem Merge
   automatisch im Repo; dokumentiert ergänzende Befunde weiterhin im QA-Log.
5. Falls die GitHub-Action `scripts/smoke.sh` mit einem `ECONNRESET` beim
   Artefakt-Upload scheitert, Job erneut anstoßen. Der Fehler entsteht beim
   Finalisieren des Uploads und erfordert inhaltlich keine Anpassung am Repo.

### Regressionstest-Zeitplan 2025

- **Q1 2025 (19.03.2025 – Acceptance-Smoke-Abgleich)**
  - Schwerpunkt: Vollständiger Regressionstest (Build 4.2.2) mit Save/Load.
  - Status: ✅ abgeschlossen.
  - QA-Log: `internal/qa/logs/2025-beta-qa-log.md`, Abschnitt 2025-03-19.
- **Q2 2025 (09.–13.06.2025)**
  - Schwerpunkt: Spiegelprozesse, Save/Load-Regression und Upload-Checks.
  - Status: 🗓️ geplant.
  - QA-Log: Eintrag folgt nach Lauf.
- **Q3 2025 (08.–12.09.2025)**
  - Schwerpunkt: Arena-Großteam-Regression, HUD-Badges und Timer.
  - Status: 🗓️ geplant.
  - QA-Log: Eintrag folgt nach Lauf.
- **Q4 2025 (08.–12.12.2025)**
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
- MyGPT und Store-GPT laufen online ohne Webtool. LUMO bietet
  Ende-zu-Ende-Verschlüsselung; Ollama/OpenWebUI bleiben vollständig offline und
  ohne Webtools.
- DSGVO-konforme Chats sicherstellen: keine realen personenbezogenen Daten
  posten, keine unverschlüsselten Log-Transkripte.

## Release-Checkliste
- Versionierung nach **MAJOR.MINOR.PATCH**. `CHANGELOG.md`, `README.md`,
  `master-index.json` und Store-Listing synchron aktualisieren.
- Rechtliche Hinweise prüfen (`docs/trademark.md`, `LICENSE`,
  Markenverweise im README).
- `make lint`, `make test` und `scripts/smoke.sh` ausführen; Ergebnisse im
  QA-Log vermerken.
- Vor Freigabe sicherstellen, dass auf jeder Plattform exakt 18
  Runtime-Module plus `master-index.json` und Masterprompt vorliegen – ohne den
  Runtime-Stub.
- Erst releasen, wenn der Beta-GPT auf MyGPT grün meldet. Danach Store-GPT
  aktualisieren und den freigegebenen Stand auf LUMO sowie lokal spiegeln. Siehe
  `CONTRIBUTING.md#beta-gpt-qa-uebergaben` für die Übergabe an Codex.
