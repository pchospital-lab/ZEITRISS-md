---
title: "ZEITRISS-md Zeitreise RPG"
version: 4.0
tags: [meta]
---

# ZEITRISS-md Zeitreise RPG

Dieses Repository enthält die Markdown-Regeln für **ZEITRISS 4.0**, ein textbasiertes Zeitreise-Rollenspiel.
Jedes Unterverzeichnis steht für einen Themenbereich, und jede Datei enthält ein Regelmodul.
Alle Module beginnen nun mit einem YAML-Header, der Titel, Version und thematische Tags enthält.

## Struktur
Alle Regeln liegen als einzelne Markdown-Dateien vor und werden einzeln in das KI-Tool geladen. Die folgende Tabelle bietet einen Kurzüberblick über alle Module:

| Datei | Inhalt |
|-------|-------|
| [README.md](README.md) | Überblick über Projekt und Workflow |
| [core/zeitriss-core.md](core/zeitriss-core.md) | Grundregeln und Setting |
| [core/wuerfelmechanik.md](core/wuerfelmechanik.md) | Würfelsystem & Proben |
| [characters/charaktererschaffung.md](characters/charaktererschaffung.md) | Charaktererschaffung & Progression |
| [characters/ausruestung-cyberware.md](characters/ausruestung-cyberware.md) | Ausrüstung, Waffen & Gadgets |
| [characters/cyberware-und-bioware.md](characters/cyberware-und-bioware.md) | Implantate & Bioware |
| [characters/psi-talente.md](characters/psi-talente.md) | Psi-Fähigkeiten |
| [characters/zustaende-hud-system.md](characters/zustaende-hud-system.md) | Zustände & HUD-Mechanik |
| [gameplay/kampagnenstruktur.md](gameplay/kampagnenstruktur.md) | Kampagnenaufbau & ITI-HQ |
| [gameplay/kampagnenuebersicht.md](gameplay/kampagnenuebersicht.md) | Kampagnenüberblick |
| [gameplay/fahrzeuge-konflikte.md](gameplay/fahrzeuge-konflikte.md) | Fahrzeuge & Konfliktsystem |
| [gameplay/kreative-generatoren.md](gameplay/kreative-generatoren.md) | Generatoren für Missionen & NSCs |
| [gameplay/team-perks.md](gameplay/team-perks.md) | Team-Boni |
| [gameplay/massenkonflikte.md](gameplay/massenkonflikte.md) | Regeln für Massenkonflikte |
| [systems/gameflow/cinematic-start.md](systems/gameflow/cinematic-start.md) | Cineastischer Einstieg |
| [systems/gameflow/gruppenstart-filmisch.md](systems/gameflow/gruppenstart-filmisch.md) | Filmischer Gruppenstart |
| [systems/gameflow/speicher-fortsetzung.md](systems/gameflow/speicher-fortsetzung.md) | Speicher- und Fortsetzungssystem (Zeitlinien-Tracker & Paradoxon-Index) |
| [systems/currency/cu-waehrungssystem.md](systems/currency/cu-waehrungssystem.md) | Chrono-Unit-Währungssystem |
| [systems/kp-kraefte-psi.md](systems/kp-kraefte-psi.md) | Details zu Psi-Kräften |
| [systems/toolkit-gpt-spielleiter.md](systems/toolkit-gpt-spielleiter.md) | Toolkit für die KI-Spielleitung |
| [meta/masterprompt_v5.md](meta/masterprompt_v5.md) | Masterprompt für das KI-Tool |

Die Dateien können als Trainingsgrundlage für ein LLM dienen, um ZEITRISS autonom zu leiten.

## Beispielworkflow
1. Öffne `masterprompt_v5.md` und kopiere den Inhalt in das Anweisungsfenster deines MyGPT (max. 8k Zeichen).
 Die Datei enthält bereits den einmaligen Sicherheitshinweis für den Spielstart.
2. Lade bis zu 20 der oben genannten Markdown-Dateien als Regelmodule in dein KI-Tool.
  Beispiele sind `zeitriss-core.md` oder `kampagnenstruktur.md`.
3. Prüfe in jeder Datei den YAML-Header auf Titel und Version.
4. Eigene Missionen kannst du mit dem Missions-Generator in
   `kreative-generatoren.md` erstellen.

## Spielstart

Um ein Abenteuer mit GPT zu beginnen, tippe einen der folgenden Befehle in dein Chatfenster (die Icons sind optional):

- **Neues Spiel (solo)** – startet ein frisches Abenteuer mit einem einzelnen Chrononauten.
GPT führt dich durch die Charaktererschaffung und liefert eine kurze Einführung ins ITI.
- **Savegame laden (solo)** – lädt einen zuvor gespeicherten Einzelspieler-Spielstand.
GPT fragt nach deinem Speicher-Code und setzt die Handlung nach einem kurzen Rückblick fort.
- **Neues Spiel Gruppe** – initiiert eine neue Mission für mehrere Chrononauten.
GPT koordiniert die Gruppen-Charaktererschaffung und stellt anschließend das Szenario vor.
- **Savegame laden (Gruppe)** – lädt einen vorhandenen Gruppen-Spielstand.
GPT fordert den Speicher-Code an und führt die Gruppe nach einem Rückblick nahtlos weiter.

Diese Befehle können frei eingegeben werden.
Sie dienen dazu, zwischen Einzel- und Gruppenspiel sowie Neu- oder Fortsetzung zu wählen.
Der Befehl `menü` (engl. `menu`, alternativ `optionen`) öffnet jederzeit das taktische HUD-Menü.
Im Menü lässt sich über `modus` der Erzählstil wechseln, z.B. auf **Covert-Ops Technoir**.


Die Inhalte stehen für private kreative Nutzung bereit.
Eine 1:1-Kopie oder kommerzielle Veröffentlichung ist nur mit Zustimmung erlaubt (siehe LICENSE).
Gemäß Lizenz richten sich diese Regeln ausschließlich an Erwachsene (18+).
