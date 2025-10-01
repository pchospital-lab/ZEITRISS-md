---
title: "Tester-Playtest-Briefing"
version: 1.0.0
tags: [meta]
---

# Tester-Playtest-Briefing

Dieser Leitfaden bündelt den standardisierten Playtest-Auftrag für ZEITRISS und erweitert ihn um eine
strukturierte Testmatrix für Solo-, Koop- und PvP-Szenarien. Die Standardpipeline besteht darin, ein
Custom-GPT mit dem Wissenspaket aufzusetzen, den untenstehenden Auftrag zu kopieren und das GPT den
kompletten Ablauf autonom (inklusive Squad-, Koop- und PvP-Simulationen) durchspielen zu lassen. Das
resultierende Protokoll wird unverändert in das Codex-Fenster (Programmier-KI) übertragen, damit dort
die QA-Aufgaben erzeugt werden.

## Wissensspeicher vorbereiten

Vor dem Testlauf werden identische Datenquellen in jeder Plattform geladen:

- `meta/masterprompt_v6.md`
- `README.md`
- `master-index.json`
- Alle 18 Runtime-Module aus `core/`, `gameplay/`, `characters/` und `systems/` (ohne
  `systems/runtime-stub-routing-layer.md`).

Optional kann der Masterprompt zusätzlich im Wissensspeicher gesichert werden. Wichtig: Prüfe, dass
der Masterprompt als System-Prompt unterhalb des 8000-Zeichen-Fensters bleibt, damit alle
Kernanweisungen vollständig geladen werden. Für Custom-GPTs empfiehlt sich ein dediziertes System-
Prompt-Feld, das das korrekte Handling von Kodex-Kommandos, Save/Load und Progressionsphasen betont.

## Testumfang und Meilensteine

- **HQ und Kodex-HUD:** Briefings, Loop-Start, Archiv-Updates, Ask→Suggest-Wechsel und
  Eskalationsregeln gegentesten.
- **Antwortformat & Spannung:** Prüfen, ob das GPT eine straffe Abschnittsstruktur liefert, den
  erwachsenen Thriller-Ton hält und relevante Infos dicht bündelt, ohne abzuschweifen.
- **Progressionsstufen:** Frühphase (Tutorial, Solo-Kernmissionen), Midgame (Stadtzugang,
  Fraktionskontakte, erweiterte HQ-Räume) und Endgame (Riftloop, Boss-Rotation, Artefaktwirtschaft)
  vollständig abdecken.
- **Stadt und Fraktionen:** Freischaltung ab dem definierten Level prüfen, Services (Werkstatt,
  Archiv, Schwarzmärkte) validieren und Ruf-/Fraktions-Wechsel dokumentieren.
- **Squad-Konfigurationen:** Wechsel zwischen Solo, Solo+NPC-Squad und Koop-Teams testen;
  Squad-Rollen, Synergieboni und Respec-Flows nachvollziehen.
- **PvP-Inhalte:** Queue-Aufbau, Regeltext, Fraktionsboni, Belohnungen sowie Safe-Zone/Combat-Zone-
  Trennung beobachten.
- **Riftloop und Sonderereignisse:** Loop-Reset, Rekonfiguration der Missionsketten und Auswirkungen
  auf Paradoxon-Index und Kodex prüfen.
- **Paradoxon-Anweisung:** Sicherstellen, dass Paradoxon-Index, Resonanz und `ClusterCreate()` exakt
  wie im Regelkern laufen (Reset auf 0 nach Seed-Anlage, Seeds erst nach Episodenende spielbar) und
  dass Riftloops keine unerlaubten Shortcuts erzeugen.

## Copy-&-Paste-Auftrag für den GPT

> (OOC: Spieleentwickler) Bitte lies den kompletten ZEITRISS-Datensatz aufmerksam und führe
> nacheinander folgende simulierte Durchläufe als Chrononaut: Solo ohne Begleitteam, Solo mit NPC-
> Squad, Koop mit einem voll simulierten Spielerteam (inkl. Absprache, Rollen- und Loot-Verteilung)
> sowie PvP-Gefechte zwischen zwei simulierten Fraktionen. Für jede Phase (Frühphase, Midgame,
> Endgame) müssen HQ-Briefing, Mission, Stadt-/Fraktionsmodule, Paradoxon-Index-Handling und Kodex-
> HUD demonstriert werden. Stelle sicher, dass alle Squad-Mitglieder und PvP-Gegner glaubwürdig
> agieren (inkl. Chat-/Voice-Callouts) und dokumentiere Sync-, Save- und Konfliktauflösungen.
>
> Bündle die Ergebnisse in klaren Abschnitten und halte einen straffen, erwachsenen Agenten-Thriller-
> Ton ohne Abschweifungen.
>
> Prüfe Save/Load mit dem aktuellen `saveGame`-Schema (inkl. `zr_version`, `Charakter`-Blöcken,
> `Kodex`-Einträgen und optionalem `arc_dashboard`), kontrolliere HQ-Briefing-Schleifen,
> Accessibility-Dialoge, Offline-Hinweise sowie Ask→Suggest- und Kodex-Kommandos. Cross-Mode-Saves
> müssen getestet werden (z. B. Solo-Save in Koop importieren, Koop-Save in PvP laden und Konflikte
> kennzeichnen). Dokumentiere jede Unstimmigkeit, Balance-Frage oder Regelunklarheit.
>
> Liefere anschließend eine nummerierte Analyse mit Problem, möglicher Lösung für Codex
> (Programmier-KI) und Hinweisen aus Sicht von Spieler:innen sowie Spielleitung. Jede Nummer
> enthält: beobachtete Situation, Diagnose, reproduzierbare Schritte und eine umsetzbare Empfehlung.

## Ablauf für Tester:innen

1. Masterprompt (`meta/masterprompt_v6.md`), `README.md`, `master-index.json` und alle Runtime-Module
   (ohne `systems/runtime-stub-routing-layer.md`) wie im Quickstart beschrieben laden. Optional
   Masterprompt zusätzlich in den Wissensspeicher übernehmen. Verifiziere, dass der GPT den Begriff
   **Kodex** korrekt nutzt und keine Legacy-Nennungen wie „Codex“ oder veraltete Save-Felder
   (`zr_version < 4.x`) ausgibt.
2. Den Auftrag oben senden und sicherstellen, dass das GPT jede geforderte Progressionsphase
   (Frühphase, Midgame, Endgame) vollständig durchläuft. Der Run gilt erst als abgeschlossen, wenn
   HQ-Loop, Mission, Stadt-/Fraktions-Interaktionen, Save/Load und Paradoxon-Index-Anpassungen
   demonstriert sind. Fehlende Abschnitte lässt du das GPT in derselben Sitzung nachliefern.
3. Prüfen, ob das GPT die gesamte Testmatrix eigenständig abarbeitet und lückenlos dokumentiert:
   - **Solo ohne Begleitteam:** Fokus auf Progression, Ressourcenfluss, Paradoxon-Index und
     Reaktionen des Kodex-HUD ohne externe Einflüsse.
   - **Solo mit NPC-Team:** Verhalten der Squad-KI, Taktik-Befehle, Auto-Revive und Balance der
     Missionsziele kontrollieren. Prüfen, ob NPCs korrekt auf HQ-Briefings, Kodex-Kommandos und
     Stadt-Services reagieren.
   - **Simuliertes Koop-Team:** Kommunikations- und Sync-Prompts, gemeinsame Save-Blöcke,
     Quest-Skalierung sowie Codex-Rollenverteilung validieren. Cross-Session-Saves (Host ↔
     Mitspieler:in) müssen im Protokoll auftauchen.
   - **Simuliertes PvP:** Matchmaking-Hinweise, Regeltexte, Fraktionsboni und Konfliktauflösungen
     erfassen. Sicherstellen, dass PvP-Gefechte den Paradoxon-Index korrekt adressieren und keine
     Solo-/Koop-Elemente leaken.
   - **Riftloop (Endgame):** Überprüfen, ob Loop-Reset, Boss-Rotation und Belohnungsumwandlung
     konsistent sind. Prüfen, wie Kodex und HUD auf wiederholte Schleifen reagieren.
4. Manueller Save/Load-Test: `saveGame({...})` anfordern, lokal sichern, neuen Chat starten und den
   Reimport prüfen. Der GPT muss `zr_version`, Kodex-Archivdaten und alle Charakterwerte sauber
   rekonstruieren. Zusätzlich Cross-Mode-Prüfung durchführen (z. B. Solo-Save in Koop laden).
5. Verifizieren, dass der GPT-Output HUD-Presets, Sofa-Modus, Offline-Optionen, Paradoxon-Index-
   Hinweise und Ask→Suggest-Toggle erklärt. Falls Informationen fehlen, gezielt nachfragen, bis alle
   Acceptance-Smoke-Punkte (inkl. Gear-Aliasse, `Spiel starten`-Varianten, HQ-Erweiterungen,
   Stadt-Diensten, Fraktionswechseln, Rufsystem) im Protokoll stehen.
6. Analyse unverändert in den Report kopieren. Ergänzend können Plattform, Datum oder besondere
   Beobachtungen als Randnotizen ergänzt werden.
7. Report an die Maintainer:innen übergeben; daraus entsteht entweder eine neue QA-Notiz oder ein
   Update für bestehende Audits. Ergebnis wird in Codex übertragen, damit Aufgaben strukturiert
   abgearbeitet werden können.

## Template für den Report an die Maintainer:innen

```text
# Playtest-Report ZEITRISS
- Version: (z. B. 4.2.2 beta)
- Testplattform: (OpenAI / Proton LUMO / Ollama)
- Datum & Uhrzeit: (lokal)
- Tester:in: (Alias)

## GPT-Analyse
(Paste aus der GPT-Antwort)

## Save/Load-Beleg
saveGame({...})

## Eigene Anmerkungen
- (Optionale Ergänzung)
- (Weitere Beobachtungen)
```

## Hinweise zur Weiterverarbeitung

- Maintainer:innen übertragen die nummerierte Liste aus der GPT-Antwort in eine QA-Notiz (z. B. als
  Ergänzung zu `docs/ZEITRISS-qa-audit-2025.md` oder einen neuen Eintrag unter `docs/`). Der
  Save/Load-Block dient als Nachweis für den Kodex- und Charakterstand.
- Reports werden lokal oder in einer gesicherten Team-Ablage archiviert, damit der Ablauf offline
  nachvollziehbar bleibt.
- Weitere Durchläufe mit alternativen Solo-Builds oder Gruppen-Saves nutzen denselben Auftrag. Die
  Ansprache, Kodex-Hinweise und Offline-Optionen bleiben dadurch konsistent. Plattformen laufen online
  ohne Web-Tool; LUMO bietet Verschlüsselung, die lokale Instanz bleibt komplett offline.
- Menschliche Gruppen können optional nachziehen, sind aber nicht Teil des Standard-Workflows. Primär
  dient der Auftrag dazu, dass das GPT sämtliche Multiplayer- und Progressionspfade autonom
  simuliert.
- Für PvP- oder Fraktions-Audits empfiehlt sich eine Gegenüberstellung der getesteten Fraktionen,
  Rufstufen und Stadt-Services. Dokumentiere Abweichungen, damit Balancing-Tasks gezielt priorisiert
  werden können.
