---
title: "Maintainer-Ops"
version: 1.2.0
tags: [meta]
---

# Maintainer-Ops

Dieses Memo bündelt alle internen Abläufe für den Betrieb von
**ZEITRISS 4.2.2**. Haltet die Schritte strikt ein, damit QA, Releases und
Plattform-Listings synchron bleiben.

## Wissensspeicher & Grundsetup

Der vollständige Datensatz für GPTs und Custom-AIs besteht aus folgenden
Bestandteilen und wird in jeder Zielplattform in den Wissensspeicher geladen:

- `meta/masterprompt_v6.md`
- `README.md`
- `master-index.json`
- Alle 18 Runtime-Module in `core/`, `gameplay/`, `characters/` und `systems/`
  (ohne `systems/runtime-stub-routing-layer.md`).

Optional kann der Masterprompt zusätzlich als Wissensspeicher-Eintrag gesichert
werden, um lange Sessions stabil zu halten.

Hinweise zum Rollenmodell (Repo-Agent, MyGPT, Beta-GPT, Kodex) stehen in
`AGENTS.md`. Diese Datei konzentriert sich auf ausführbare Abläufe.

**Grundsatz:** Alle QA-Läufe finden ausschließlich im OpenAI-MyGPT-Beta-Klon statt. Erst nach einer grünen
Abnahme werden Store-GPT, Proton LUMO und lokale Instanzen mit genau diesem Stand gespiegelt; separate
Optimierungen für andere Plattformen sind derzeit nicht vorgesehen.

## QA-Plattformstrategie

- **Referenz-Plattform:** Der Beta-Klon von **ZEITRISS [Ver. 4.2.2]** auf OpenAI-MyGPT ist die einzige
  Instanz für aktive QA-Läufe. Alle Regressionstests, Acceptance-Smokes und Save/Load-Prüfungen werden hier
  durchgeführt und anschließend im QA-Log abgelegt.
- **Freigabebedingung:** Erst nachdem der Beta-Klon die QA als „grün“ meldet und Codex die
  Nachverfolgung im QA-Fahrplan geschlossen hat, darf der Wissensstand auf weitere Plattformen gespiegelt
  werden.
- **Spiegelroutine:** Store-GPT, Proton LUMO und lokale Installationen erhalten ausschließlich den
  freigegebenen Stand. Abweichungen oder Ergänzungen werden nicht eigenständig ausprobiert, sondern als
  Findings an Codex zurückgegeben.
- **Dokumentation:** Jede Spiegelung wird mit Datum, Zielplattform und Verweis auf den passenden
  QA-Log-Abschnitt dokumentiert. Nur so bleibt nachvollziehbar, welche Plattform welchen Stand lädt.

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
7. Sämtliche QA-Sessions ausschließlich im Beta-Klon durchführen. Plattform
   läuft online, besitzt aber kein Web-Tool; dokumentiert das Verhalten im
   QA-Log.
8. QA und Publishing erst freigeben, wenn die Chat-Historie keine
   personenbezogenen Daten enthält.
9. Nach bestandener QA den Stand in den Haupt-GPT übertragen und erst danach
   das Store-Listing aktualisieren. Vermerkt die Spiegelung mit Verweis auf
   den QA-Log-Eintrag des grünen Runs.

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
3. Übertrage den Stand unverändert in den produktiven MyGPT und dokumentiere Datum sowie QA-Log-Referenz.
4. Spiegele denselben Export im Anschluss auf Store-GPT, Proton LUMO und lokale Instanzen in dieser
   Reihenfolge. Jede Plattform erhält exakt denselben Datei-Satz.
5. Ergänze im QA-Log einen kurzen Spiegelvermerk (Plattform, Datum, Verantwortliche Person). Abweichungen
   werden als neue Findings festgehalten.

### Sync-Checks & Beispielworkflow

- Nach jedem freigegebenen Update bestätigen, dass MyGPT und Store-GPT denselben Stand
  führen (Masterprompt, README, Module) und den Release anschließend auf LUMO sowie lokal spiegeln.
- Sicherstellen, dass exakt 18 Runtime-Module plus `master-index.json` geladen
  sind; der Runtime-Stub bleibt außen vor.
- Für Schnelltests die Checkliste aus [docs/acceptance-smoke.md](acceptance-smoke.md)
  nutzen und Ergebnisse hier protokollieren.
- Detailablauf für Uploads siehe Abschnitt „Beispielworkflow“ im README; dort
  stehen die Datei-Checks, die beim Laden kontrolliert werden.

## QA-Loop & Speicherstände
Halte für QA und Save/Load-Checks den Übergabeprozess in
`CONTRIBUTING.md#beta-gpt-qa-uebergaben` ein. Ergänzend gilt:

### Beta-GPT & Playtests
1. Klone nach jedem Release-Kandidaten den produktiven MyGPT zu
   **ZEITRISS [Ver. 4.2.2] beta**.
2. Starte Playtests ausschließlich im Beta-Klon und füge den Auftrag aus
   `docs/tester-playtest-briefing.md` in die erste Chat-Nachricht ein.
3. Übertrage die Antwort des Beta-GPT gesammelt an Codex (Repo-Agent), damit
   daraus Aufgaben im QA-Fahrplan entstehen.
4. Synchronisiere den Wissensspeicher des produktiven MyGPT sowie weiterer
   Plattformen erst, nachdem Codex die QA als grün markiert hat.

### Übergabe an Codex & Dokumentation
1. Exportiere nach jeder Beta-GPT-Session das vollständige Chatlog (inklusive Debug-Ausgaben) und
   sende es unverändert an Codex. Eine kompakte Stichpunktliste der Findings beschleunigt die
   Übertragung in den QA-Fahrplan.
2. Markiere im Log klar die Plattform (Standard: MyGPT Beta auf openai.com), den Build-Stand und den
   verwendeten Wissensspeicher.
3. Notiere in deiner Übergabe, ob Uploads, Save/Load-Checks oder Plattformspiegelungen bereits erfolgt
   sind. Codex übernimmt daraufhin die Pflege der Dateien `internal/qa/2025-beta-qa-log.md`,
   `docs/ZEITRISS-qa-fahrplan-2025.md` und `docs/ZEITRISS-qa-audit-2025.md` im Repo.
4. Nachdem Codex die QA-Dokumente aktualisiert und alle Findings abgearbeitet hat, spiegelst du den
   freigegebenen Stand auf Store-GPT, Proton LUMO und lokale Instanzen. Dokumentiere Abweichungen
   ausschließlich dann, wenn sie vom MyGPT-Referenzlauf abweichen.

### Zusätzliche QA-Pflichten
1. Plane mindestens drei komplette Durchläufe im MyGPT-Beta ein; weitere
   Plattformen erhalten denselben Stand ohne eigenständige QA-Schleifen.
2. In jeder Session Save/Load prüfen: `saveGame({...})` ausgeben lassen, lokal
   sichern, neuen Chat öffnen und den Reimport testen.
3. Accessibility-Dialoge (HUD-Erklärung, Sofa-Modus, Offline-Hinweise) und
   HQ-Briefing-Schleifen abgleichen.
4. Acceptance-Smoke-Checklist aus `docs/acceptance-smoke.md` ergänzen und
   Abweichungen festhalten. Smoketests laufen bei jedem Merge automatisch im
   Repo; dokumentiert ergänzende Befunde weiterhin im QA-Log.
5. Falls die GitHub-Action `scripts/smoke.sh` mit einem `ECONNRESET` beim
   Artefakt-Upload scheitert, Job erneut anstoßen. Der Fehler entsteht beim
   Finalisieren des Uploads und erfordert inhaltlich keine Anpassung am Repo.

## Systemgrenzen (Reminder)
- KI-Spielleitung kann keine Dateien schreiben oder Repos verändern;
  Speicherstände nur via Copy & Paste.
- Save-Funktionen laufen ausschließlich über das HQ. Missionen lassen sich
  abbrechen, aber nicht zwischen-speichern.
- MyGPT und Store-GPT laufen online ohne Webtool. LUMO bietet Ende-zu-Ende-Verschlüsselung; Ollama/OpenWebUI bleiben vollständig
  offline und ohne Webtools.
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
- Erst release, wenn der Beta-GPT auf MyGPT grün meldet. Danach Store-GPT aktualisieren und den freigegebenen Stand auf LUMO sowie lokal spiegeln. Siehe `CONTRIBUTING.md#beta-gpt-qa-uebergaben` für die
  Übergabe an Codex.
