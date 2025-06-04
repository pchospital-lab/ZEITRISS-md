# ZEITRISS-md Zeitreise RPG

Dieses Repository enthält die Markdown-Regeln für **ZEITRISS 4.0**, ein textbasiertes Zeitreise-Rollenspiel. Jedes Unterverzeichnis steht für einen Themenbereich und jede Datei enthält ein Regelmodul. Alle Module beginnen nun mit einem YAML-Header, der Titel, Version und thematische Tags enthält.

## Struktur
Alle Regeln liegen als einzelne Markdown-Dateien vor und werden einzeln in das KI-Tool geladen:
- `README.md` – Überblick über das Projekt (wird als Regelmodul mitgeladen)
- `zeitriss-core.md`
- `wuerfelmechanik.md`
- `charaktererschaffung.md`
- `ausruestung-cyberware.md`
- `loot-tables.md`
- `zustaende-hud-system.md`
- `kampagnenstruktur.md`
- `fahrzeuge-konflikte.md`
- `kreative-generatoren.md`
- `massenkonflikte.md`
- `kampagnenuebersicht.md`
- `missionen.md`
- `cinematic-start.md`
- `cu-waehrungssystem.md`
- `erweiterte-regelmodule.md`
- `gruppenstart-filmisch.md`
- `kp-kraefte-psi.md`
- `solo-npc-team.md`
- `speicher-fortsetzung.md`
- `toolkit-gpt-spielleiter.md`
- `meta/masterprompt_v5.md` – Masterprompt (Inhalt ins Anweisungsfenster kopieren, max. 8k Zeichen)

Die Dateien können als Trainingsgrundlage für ein LLM dienen, um ZEITRISS autonom zu leiten.

## Beispielworkflow
1. Öffne `meta/masterprompt_v5.md` und kopiere den Inhalt in das Anweisungsfenster deines MyGPT (max. 8k Zeichen).
2. Lade bis zu 20 der oben genannten Markdown-Dateien als Regelmodule in dein KI-Tool, zum Beispiel `zeitriss-core.md` oder `kampagnenstruktur.md`.
3. Prüfe in jeder Datei den YAML-Header auf Titel und Version.
4. Eigene Missionen kannst du in `missionen.md` ergänzen.

## Spielstart

Um ein Abenteuer mit GPT zu beginnen, tippe einen der folgenden Befehle in dein Chatfenster (die Icons sind optional):

- **Neues Spiel (solo)** – startet ein frisches Abenteuer mit einem einzelnen Chrononauten. GPT führt dich durch die Charaktererschaffung und liefert eine kurze Einführung ins ITI.
- **Savegame laden (solo)** – lädt einen zuvor gespeicherten Einzelspieler-Spielstand. GPT fragt nach deinem Speicher-Code und setzt die Handlung nach einem kurzen Rückblick fort.
- **Neues Spiel Gruppe** – initiiert eine neue Mission für mehrere Chrononauten. GPT koordiniert die Gruppen-Charaktererschaffung und stellt anschließend das Szenario vor.
- **Savegame laden (Gruppe)** – lädt einen vorhandenen Gruppen-Spielstand. GPT fordert den Speicher-Code an und führt die Gruppe nach einem Rückblick nahtlos weiter.

Diese Befehle können frei eingegeben werden und dienen dazu, zwischen Einzel- und Gruppenspiel sowie Neu- oder Fortsetzung zu wählen.


Die Inhalte stehen für private kreative Nutzung bereit. Eine 1:1-Kopie oder kommerzielle Veröffentlichung ist nur mit Zustimmung erlaubt (siehe LICENSE).
