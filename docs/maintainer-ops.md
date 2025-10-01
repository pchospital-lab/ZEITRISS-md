---
title: "Maintainer-Ops"
version: 1.1.0
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

### KI-Rollen & Zugriffsebenen

- **Custom-GPT „ZEITRISS [Ver. 4.2.2]“ (Spielleitung).** Versorgt jede
  Spielsitzung mit Masterprompt, README, `master-index.json` und allen 18
  Runtime-Modulen. Andere Repo-Dokumente bleiben ausgeblendet, um den Flow über
  den Masterprompt zu steuern.
- **Programmier-KI Codex (Repo-Agent).** Arbeitet direkt im Git-Repository,
  folgt `AGENTS.md` und `CONTRIBUTING.md`, pflegt Module, Tools und
  Dokumentation und führt Builds sowie Commits durch. Tritt in Live-Sessions
  nicht auf.
- **Ingame-KI „Kodex“.** In-World-Wissensinterface des ITI. Liefert HUD-Frames,
  Missionsdaten und Archivzitate. Wird von der Spielleitung simuliert und klar
  von der Programmier-KI getrennt.

Der Masterprompt verankert diese Ebenen, delegiert Dev-Aufgaben an den
Repo-Agenten und hält den Kodex als immersive Stimme innerhalb der Fiktion.

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
   das Store-Listing aktualisieren.

### Proton LUMO (verschlüsselter Chat)
1. Die LUMO-App starten und einen neuen Chat öffnen.
2. `meta/masterprompt_v6.md`, `README.md`, `master-index.json` und alle
   Runtime-Module (ohne Runtime-Stub) über die Büroklammer hochladen.
3. Optional alle Dateien in den Wissensspeicher übernehmen.
4. Den Masterprompt zusätzlich als Chatnachricht einfügen, damit die Rolle zu
   Beginn fixiert ist.
5. Im QA-Log vermerken, welche LUMO-Funktionen (Dateiupload, Replay,
   Gerätewechsel) genutzt wurden und ob Markdown/JSON unverändert bleiben.

### Lokaler Betrieb (Ollama + OpenWebUI)
1. Ollama mit dem gewünschten Modell installieren und OpenWebUI lokal
   verbinden.
2. Masterprompt, README, Master-Index und alle Runtime-Module importieren
   (Upload oder Wissensbibliothek).
3. Acceptance-Smoke-Test offline durchspielen. Webtools stehen nicht zur
   Verfügung; optionale Integrationen vermerken.
4. Lokale Anpassungen im QA-Log festhalten und nach Freigabe auf MyGPT und
   LUMO spiegeln.

### Sync-Checks & Beispielworkflow

- Nach jedem Update bestätigen, dass MyGPT, LUMO und Ollama denselben Stand
  führen (Masterprompt, README, Module).
- Sicherstellen, dass exakt 18 Runtime-Module plus `master-index.json` geladen
  sind; der Runtime-Stub bleibt außen vor.
- Für Schnelltests die Checkliste aus [docs/acceptance-smoke.md](acceptance-smoke.md)
  nutzen und Ergebnisse hier protokollieren.
- Detailablauf für Uploads siehe Abschnitt „Beispielworkflow“ im README; dort
  stehen die Datei-Checks, die beim Laden kontrolliert werden.

## QA-Loop & Speicherstände
1. Mindestens drei komplette Durchläufe im MyGPT-Beta sowie je einen auf LUMO
   und lokal einplanen.
2. In jeder Session Save/Load prüfen: `saveGame({...})` ausgeben lassen, lokal
   sichern, neuen Chat öffnen und den Reimport testen.
3. Accessibility-Dialoge (HUD-Erklärung, Sofa-Modus, Offline-Hinweise) und
   HQ-Briefing-Schleifen abgleichen.
4. Ergebnisse, Auffälligkeiten und Save/Load-Belege im QA-Log unter
   `docs/ZEITRISS-qa-audit-2025.md` oder einem neuen Eintrag in `docs/`
   dokumentieren.
5. Acceptance-Smoke-Checklist aus `docs/acceptance-smoke.md` ergänzen und
   Abweichungen festhalten. Smoketests laufen bei jedem Merge automatisch im
   Repo; dokumentiert lokale Befunde zusätzlich.
6. Falls die GitHub-Action `scripts/smoke.sh` mit einem `ECONNRESET` beim
   Artefakt-Upload scheitert, Job erneut anstoßen. Der Fehler entsteht beim
   Finalisieren des Uploads und erfordert inhaltlich keine Anpassung am Repo.

## Systemgrenzen (Reminder)
- KI-Spielleitung kann keine Dateien schreiben oder Repos verändern;
  Speicherstände nur via Copy & Paste.
- Save-Funktionen laufen ausschließlich über das HQ. Missionen lassen sich
  abbrechen, aber nicht zwischen-speichern.
- MyGPT und LUMO laufen online, besitzen jedoch keinen Webzugang als Tool.
  LUMO bietet Ende-zu-Ende-Verschlüsselung; Ollama/OpenWebUI bleiben vollständig
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
- Erst release, wenn Beta-GPT, LUMO und Ollama denselben Wissensstand führen
  und QA grün meldet. Übergib QA-Berichte an Codex, damit daraus eine
  abarbeitbare Liste entsteht.

## Beta-GPT-Workflow

1. Beta-GPT vollständig mit Masterprompt, Wissensspeicher und allen Modulen
   bestücken.
2. Testauftrag aus `docs/tester-playtest-briefing.md` in den Chat kopieren und
   den GPT den Durchlauf selbst ausführen lassen.
3. Antwort in Codex übertragen, daraus eine QA-Notiz erstellen und die
   identifizierten Punkte strukturiert abarbeiten.
