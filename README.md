# ZEITRISS-md Zeitreise RPG

Dieses Repository enthält die Markdown-Regeln für **ZEITRISS 4.0**, ein textbasiertes Zeitreise-Rollenspiel. Jedes Unterverzeichnis steht für einen Themenbereich und jede Datei enthält ein Regelmodul. Alle Module beginnen nun mit einem YAML-Header, der Titel, Version und thematische Tags enthält.

## Struktur
- **core/** – Grundregeln und Würfelsystem
- **characters/** – Charaktererschaffung, Zustände und Ausrüstung
- **gameplay/** – Kampagnenstruktur, Konflikte, kreative Generatoren, Kampagnenuebersicht und alle Missionsbeschreibungen in `missionen.md`
- **systems/** – Erweiterte Systeme wie HQ, PSI, Speichermechanik
- **meta/** – Masterprompt und Leitfaden für GPT-Spielleitungen

Die Dateien können als Trainingsgrundlage für ein LLM dienen, um ZEITRISS autonom zu leiten.

## Beispielworkflow
1. Wähle ein Modul aus den Unterordnern, z.B. `core` oder `gameplay`.
2. Sieh dir den YAML-Header an, um Titel und Version zu prüfen.
3. Nutze das Dokument `meta/masterprompt.md` als Grundlage für eine KI-Spielleitung.
4. Lade die Markdown-Dateien nacheinander in dein KI-Tool oder lies sie für dein eigenes Abenteuer.
5. Eigene Missionen kannst du im Ordner `gameplay/missionen.md` ergänzen.

## Spielstart

Um ein Abenteuer mit GPT zu beginnen, tippe einen der folgenden Befehle in dein Chatfenster (die Icons sind optional):

- **Neues Spiel (solo)** – startet ein frisches Abenteuer mit einem einzelnen Chrononauten. GPT führt dich durch die Charaktererschaffung und liefert eine kurze Einführung ins ITI.
- **Savegame laden (solo)** – lädt einen zuvor gespeicherten Einzelspieler-Spielstand. GPT fragt nach deinem Speicher-Code und setzt die Handlung nach einem kurzen Rückblick fort.
- **Neues Spiel Gruppe** – initiiert eine neue Mission für mehrere Chrononauten. GPT koordiniert die Gruppen-Charaktererschaffung und stellt anschließend das Szenario vor.
- **Savegame laden (Gruppe)** – lädt einen vorhandenen Gruppen-Spielstand. GPT fordert den Speicher-Code an und führt die Gruppe nach einem Rückblick nahtlos weiter.

Diese Befehle können frei eingegeben werden und dienen dazu, zwischen Einzel- und Gruppenspiel sowie Neu- oder Fortsetzung zu wählen.

Die Inhalte stehen für private kreative Nutzung bereit. Eine 1:1-Kopie oder kommerzielle Veröffentlichung ist nur mit Zustimmung erlaubt (siehe LICENSE).
