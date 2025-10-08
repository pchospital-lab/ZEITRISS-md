---
title: "Tester-Playtest-Briefing"
version: 1.1.0
tags: [meta]
---

# Tester-Playtest-Briefing

Dieser Leitfaden bündelt den standardisierten Playtest-Auftrag für ZEITRISS und erweitert ihn um eine
strukturierte Testmatrix für Solo-, Koop- und PvP-Szenarien. Die Standardpipeline besteht darin, ein
Custom-GPT mit dem Wissenspaket aufzusetzen, den untenstehenden Auftrag zu kopieren und das GPT den
kompletten Ablauf autonom (inklusive Squad-, Koop- und PvP-Simulationen) durchspielen zu lassen. Das
resultierende Protokoll liefert automatisch strukturierte `ISSUE`, `Lösungsvorschlag`, `To-do`- und
`Nächste Schritte`-Blöcke für Codex und wird unverändert in das Codex-Fenster (Programmier-KI)
übertragen. Tester:innen posten den Auftrag genau einmal; das GPT simuliert alle benötigten Läufe
eigenständig und fasst sie im beschriebenen Format zusammen.

## Wissensspeicher vorbereiten

Vor dem Testlauf werden identische Datenquellen in jeder Plattform geladen:

- `meta/masterprompt_v6.md`
- `README.md`
- `master-index.json`
- Alle 18 Runtime-Module aus `core/`, `gameplay/`, `characters/` und `systems/` (ohne
  `systems/runtime-stub-routing-layer.md`).

Eine Zielgruppen- und Dokumentenübersicht findest du in der README unter
[„Dokumenten-Landkarte“](../README.md#dokumenten-landkarte); sie zeigt, wie Tester:innen ihre
Findings an Maintainer:innen und den Repo-Agenten übergeben.

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

> **Einmal senden, vollständigen QA-Run abwarten:** Der GPT simuliert Solo-, NPC-Squad-, Koop- und
> PvP-Szenarien selbstständig. Tester:innen posten diesen Auftrag genau einmal und warten, bis alle
> Abschnitte samt Abschluss-Blocks geliefert wurden.

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
> Arbeite zusätzlich jeden Punkt der in diesem Dokument hinterlegten
> Acceptance-Smoke-Checkliste (siehe Abschnitt „Acceptance-Smoke-Checkliste“)
> ab, vermerke Abweichungen im Evidenz-Block und kennzeichne die Prüfnummer
> (1–13) pro Befund.
>
> Erstelle nach Abschluss aller Simulationen eine strukturierte Ergebnisübersicht ausschließlich in
> folgendem Format (eine Leerzeile trennt die Blöcke, keine zusätzlichen Kommentare):
>
> ```text
> ISSUE #<laufende Nummer>
> - Beobachtung: <kurze Beschreibung>
> - Diagnose: <Root Cause oder Regelverweis>
> - Evidenz: <Reproduktionsschritte oder Log-Hinweis>
>
> Lösungsvorschlag
> - Ansatz: <Empfohlene Korrektur>
> - Risiken: <Folgen oder Abhängigkeiten>
>
> To-do
> - Codex: <konkreter Umsetzungsauftrag>
> - QA: <benötigter Test oder Nachweis>
>
> Nächste Schritte
> - Maintainer:innen: <Sync- oder Upload-Aktion>
> - Notizen: <optionale Hinweise>
> ```
>
> Wiederhole diesen Block für jedes identifizierte Thema. Wenn kein weiteres Thema offen ist, beende
> die Antwort nach dem letzten Block ohne zusätzliche Zusammenfassung.

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
   Stadt-Diensten, Fraktionswechseln, Rufsystem, Boss-Gates, HUD-Badges, Psi-Heat) im Protokoll
   stehen.
6. Überprüfe, dass die GPT-Antwort alle `ISSUE`-, `Lösungsvorschlag`-, `To-do`- und `Nächste Schritte`-
   Blöcke enthält und keine freien Zusatzabschnitte erzeugt. Fehlende Angaben lässt du das GPT in
   derselben Sitzung nachreichen. Dokumentiere zusätzlich für jeden Acceptance-Smoke-Punkt (1–13),
   ob er bestanden wurde oder welcher Nachtest angesetzt ist.
7. Analyse unverändert in den Report kopieren. Ergänzend können Datum oder besondere Beobachtungen als
   Randnotizen ergänzt werden. Standardplattform ist das OpenAI-MyGPT im Beta-Klon.
8. Report an die Maintainer:innen übergeben; daraus entsteht entweder eine neue QA-Notiz oder ein
   Update für bestehende Audits. Ergebnis wird in Codex übertragen, damit Aufgaben strukturiert
   abgearbeitet werden können.

## Template für den Report an die Maintainer:innen

```text
# Playtest-Report ZEITRISS
- Version: (z. B. 4.2.2 beta)
- Testplattform: OpenAI (MyGPT Beta)
- Datum & Uhrzeit: (lokal)
- Tester:in: (Alias)

## GPT-Analyse
(Paste aus der GPT-Antwort – inklusive aller ISSUE-/Lösungsvorschlag-/To-do-/Nächste-Schritte-Blöcke)

## Save/Load-Beleg
saveGame({...})

## Eigene Anmerkungen
- (Optionale Ergänzung)
- (Weitere Beobachtungen)
```

## Hinweise zur Weiterverarbeitung

- Maintainer:innen übertragen die strukturierten ISSUE-/Lösungsvorschlag-/To-do-/Nächste-Schritte-
  Blöcke aus der GPT-Antwort in eine QA-Notiz (z. B. als Ergänzung zu
  `internal/qa/audits/ZEITRISS-qa-audit-2025.md` oder einen neuen Eintrag in den
  Fahrplan). Der
  Save/Load-Block dient als Nachweis für den Kodex- und Charakterstand.
- Reports werden lokal oder in einer gesicherten Team-Ablage archiviert, damit der Ablauf offline
  nachvollziehbar bleibt.
- Weitere Durchläufe mit alternativen Solo-Builds oder Gruppen-Saves nutzen denselben Auftrag. Die
  Ansprache, Kodex-Hinweise und Offline-Optionen bleiben dadurch konsistent.
  Spiegelplattformen (Store-GPT, LUMO, lokal) erhalten den freigegebenen Stand ohne eigene QA-Optimierung; dokumentiere nur Abweichungen bei Bedarf.
- Menschliche Gruppen können optional nachziehen, sind aber nicht Teil des Standard-Workflows. Primär
  dient der Auftrag dazu, dass das GPT sämtliche Multiplayer- und Progressionspfade autonom
  simuliert.
- Für PvP- oder Fraktions-Audits empfiehlt sich eine Gegenüberstellung der getesteten Fraktionen,
  Rufstufen und Stadt-Services. Dokumentiere Abweichungen, damit Balancing-Tasks gezielt priorisiert
  werden können.

## Acceptance-Smoke-Checkliste

> **Hinweis:** Der standardisierte Beta-GPT-Testprompt verpflichtet sich, jeden
> Punkt dieser Checkliste automatisch abzudecken. Dokumentiere Abweichungen im
> QA-Log und im Fahrplan unter den Deepcheck-Aufgaben.

### Dispatcher-Starts & Speicherpfade

1. `Spiel starten (solo klassisch)` → Erschaffung → HQ-Intro → Briefing → SC 1
2. `Spiel starten (solo schnell)` → Rolle → Defaults → Briefing/SC 1
3. `Spiel starten (npc-team 3 schnell)` → Autogen-NSCs (3) → Briefing
4. `Spiel starten (npc-team 5)` → Fehlertext „Teamgröße 0–4 …“
5. `Spiel starten (gruppe schnell)` → 2 Saves + 1 Rolle → Briefing
6. `Spiel starten (gruppe 3)` → Fehlertext „Bei *gruppe* keine Zahl …“
7. `Spiel laden` + kompatibler Save → Kodex-Recap-Overlay → HQ/Briefing (keine Startfrage)
8. `Speichern` während Mission → Blocker „Speichern nur im HQ …“
9. Gear-Alias: „Multi-Tool-Armband ausrüsten“ → still → „Multi-Tool-Handschuh“
10. „Px 5“ triggern → Hinweis: Seeds erzeugt, spielbar nach Episodenende, Reset danach

### Boss-Gates & HUD-Badges

11. `!helper boss` nach Mission 4 → Foreshadow-Liste zeigt Szene 5/10. HUD-Toast
    `Boss blockiert – Foreshadow 0/2`, bis Hinweise erfüllt sind.
12. Mission 5 starten → HUD blendet Mini-Boss-DR (`Boss-Encounter in Szene 10`)
    und Badge `SF-OFF` ein; Foreshadow-Schritte zählen im HUD hoch.

### Psi-Heat & Ressourcen-Reset

13. Psi-Charakter in Konflikt schicken, Psi-Aktion nutzen → HUD meldet
    `Psi-Heat +1`; nach Konflikt springt Psi-Heat automatisch auf 0. HQ-Transfer
    setzt SYS/Stress/Psi-Heat zurück.

### QA-Abgleich 2025-03-23

- **Boss-Gates & HUD-Badges:** `scene_overlay()` blendet bei deaktivierter
  Selbstreflexion das Badge `SF-OFF` ein und führt Foreshadow-Zähler mit, während
  `assert_foreshadow()` in Präzisionsläufen Warnungen ausgibt; validiert über
  `GM_STYLE=precision node tools/test_foreshadow.js` sowie das HUD-Skript.
- **Psi-Heat-Reset:** `migrate_save()` und `hydrate_state()` setzen Psi-Heat in
  Konflikt- und HQ-Transfers deterministisch zurück und verhindern Speichervorgänge
  mit Restwärme.
- **Log-Verweis:** Vollständiges Prüfprotokoll im QA-Log vom 2025-03-19.
