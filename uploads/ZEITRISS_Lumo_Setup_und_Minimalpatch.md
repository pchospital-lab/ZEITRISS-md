# ZEITRISS auf Lumo — Setup-Draft & Minimalpatch

## Entscheidungsbild

- **ZEITRISS-Masterprompt:** in **Projekt-Anweisungen** von Lumo.
- **Nicht** zusätzlich in **Personalisierung**.
- **Personalisierung** für ZEITRISS am besten **leer oder neutral** lassen.
- **Projektwissen:** nur die **19 Default-Module** laden.
- **Nicht** das ganze Repo an Proton Drive / Projektwissen hängen.
- **OpenWebUI bleibt Referenzplattform**; Lumo ist ein kompatibler, aber weniger fein steuerbarer Zweitpfad.
- **Keine inhaltlichen Umbauten** am Regelwerk vor dem Langzeit-Playtest.
- **Keine Schema-Auslagerung** aus dem Masterprompt.
- **Keine Modul-Splits** nur um künstlich einen „freien Slot“ zu füllen.

---

## Vorschlag für neue Repo-Datei: `docs/setup-lumo.md`

```md
---
title: "ZEITRISS auf Lumo (Proton)"
version: 4.2.6
tags: [meta, setup, lumo]
---

# ZEITRISS auf Lumo (Proton)

Diese Anleitung beschreibt den **kompatiblen Zweitpfad** für ZEITRISS auf
**Lumo by Proton**. Die **Referenzplattform** bleibt **OpenWebUI + OpenRouter**,
weil dort System-Prompt, Modellwahl und Laufzeit-Parameter explizit steuerbar
sind. Lumo funktioniert, ist aber bewusst einfacher gehalten.

## 1. Was auf Lumo wohin gehört

### Projekt-Anweisungen

Hier gehört der komplette Inhalt von:

- `meta/masterprompt_v6.md`

hinein.

**Wichtig:**

- Der ZEITRISS-Masterprompt gehört auf Lumo **in die Projekt-Anweisungen**.
- Er gehört **nicht** in die Personalisierung.
- Er gehört **nicht** ins Projektwissen.

### Projektwissen

Hier gehören **nur die 19 Default-Module** hinein:

1. `core/spieler-handbuch.md`
2. `core/zeitriss-core.md`
3. `core/wuerfelmechanik.md`
4. `core/sl-referenz.md`
5. `characters/charaktererschaffung-grundlagen.md`
6. `characters/ausruestung-cyberware.md`
7. `systems/kp-kraefte-psi.md`
8. `characters/zustaende.md`
9. `characters/hud-system.md`
10. `gameplay/kampagnenstruktur.md`
11. `gameplay/kampagnenuebersicht.md`
12. `gameplay/kreative-generatoren-missionen.md`
13. `gameplay/kreative-generatoren-begegnungen.md`
14. `gameplay/fahrzeuge-konflikte.md`
15. `gameplay/massenkonflikte.md`
16. `systems/currency/cu-waehrungssystem.md`
17. `systems/gameflow/speicher-fortsetzung.md`
18. `systems/gameflow/cinematic-start.md`
19. `systems/toolkit-gpt-spielleiter.md`

### Nicht in Projektwissen laden

- `README.md`
- `master-index.json`
- `meta/masterprompt_v6.md`
- Dev-/QA-Dokumente
- Schema-Dateien
- optionale Fallback-/Archiv-Dateien

## 2. Personalisierung auf Lumo

Die **Personalisierung** sollte für ZEITRISS **leer oder neutral** bleiben,
weil sie global wirkt und mit Projekten kollidieren kann.

**Empfohlen:** leer lassen.

**Wenn du sie unbedingt nutzen willst, dann nur neutral und kurz**, z. B.:

`Antworte standardmäßig auf Deutsch. Sei direkt, klar und kritisch.`

**Nicht empfohlen:**

- ZEITRISS-Masterprompt dort einfügen
- Rollenspielregeln dort doppeln
- Save-/HUD-/Kodex-Logik dort erneut beschreiben

## 3. Empfohlener Aufbau in Proton Drive

Für Lumo **niemals das komplette Repo** an ein Projekt hängen.

Lege stattdessen einen **sauberen Ordner nur für Lumo** an, z. B.:

`ZEITRISS-Lumo-Default/`

Dort hinein kopierst du **nur die 19 Default-Module**.

Optional kannst du daneben einen zweiten Ordner pflegen:

`ZEITRISS-Lumo-Optional/`

für Dinge, die **nicht standardmäßig** verknüpft sein sollen.

So verhinderst du, dass Lumo versehentlich optionale, historische oder rein
technische Dateien in den Spielkontext zieht.

## 4. Projekt anlegen

1. In Lumo ein neues Projekt `ZEITRISS` anlegen.
2. In **Anweisungen** den Inhalt von `meta/masterprompt_v6.md` einfügen.
3. In **Projektwissen** entweder:
   - die 19 Default-Dateien direkt hochladen, oder
   - den vorbereiteten Proton-Drive-Ordner `ZEITRISS-Lumo-Default/` verknüpfen.
4. Websuche für den eigentlichen Spielbetrieb **aus** lassen.
5. Neuen Chat starten.

## 5. Spielstart

Empfohlene Startprompts:

- `Spiel starten (solo klassisch)`
- `Spiel laden`
- `Ich will solo neu anfangen und meinen Charakter generieren.`

Savegames werden wie auf anderen Plattformen **direkt als JSON in den Chat**
gegeben.

## 6. Qualität auf Lumo

Lumo bietet derzeit nicht dieselbe explizite Feinsteuerung wie OpenWebUI.
Plane deshalb so:

- **Projekt-Anweisungen** = harter ZEITRISS-Rahmen
- **Projektwissen** = 19 Default-Module
- **Personalisierung** = leer/neutral
- **„Länger nachdenken“** = manueller Qualitätshebel bei kritischen Zügen

Typische Momente für den Button:

- Save laden / Merge / Rejoin
- HQ-DeepSave
- Boss-/Rift-Szenen
- Chronopolis-Exit
- widersprüchliche Kontinuität
- komplexe Gruppenlagen

## 7. Lumo-spezifische Grenzen

Lumo ist für ZEITRISS **spielbar**, aber nicht die Referenzplattform.

Das bedeutet praktisch:

- weniger kontrollierbar als OpenWebUI
- keine dokumentierten OpenWebUI-Äquivalente für Temperature/Top-P/Systemfeld
- deshalb mehr Gewicht auf saubere Projekt-Anweisungen und ein kuratiertes Projektwissen

## 8. Sicherheits- und Stilhinweis

ZEITRISS bleibt auch auf Lumo ein **filmischer Agenten-Thriller**.

Die Spielleitung soll:

- illegalen Real-World-How-to-Stil vermeiden
- Hacking, Gewalt und Infiltration **in-world und outcome-basiert** halten
- keine Schritt-für-Schritt-Anleitungen für echte Rechtsverstöße geben

Das passt sowohl zum ZEITRISS-Action-Contract als auch zu Lumo als Plattform.
```

---

## Minimaler Repo-Patch, den ich wirklich empfehlen würde

### A) Unbedingt

1. **Neue Datei:** `docs/setup-lumo.md`
2. **README ergänzen:** unter „Manuelles Setup“ einen Link auf die Lumo-Anleitung
3. **`docs/setup-guide.md` ergänzen:** ein kurzer Hinweis „Für Lumo siehe `docs/setup-lumo.md`“

### B) Sehr sinnvoll, ohne Regelsystem anzufassen

4. **Neues Script:** `scripts/export-knowledge-pack.sh`
   - liest `master-index.json`
   - kopiert alle Einträge mit `"slot": true` in einen Exportordner
   - schreibt zusätzlich eine Textdatei `UPLOAD-ONLY-THIS.txt`
   - legt `meta/masterprompt_v6.md` separat als `SYSTEM_PROMPT_ONLY.md` ab

**Ziel:**
Manuelle Builder laden nicht mehr aus dem Repo-Baum zusammen, sondern arbeiten
mit einem **sauberen, generierten Upload-Pack**.

### C) Optional, erst wenn euch die Baumstruktur weiter nervt

5. Nicht-Default-Dateien aus Laufzeitordnern herausziehen:
   - `characters/charaktererschaffung-optionen.md` → `meta/optional/` oder `docs/optional/`
   - `systems/gameflow/saveGame.v6.schema.json` → `meta/schema/`
   - `systems/gameflow/saveGame.v7.schema.json` → `meta/schema/`

Das ist sauber, aber **nicht zwingend vor dem Playtest**, wenn ihr den Export-Pack nutzt.

---

## Was ich explizit nicht ändern würde

- **Schema NICHT aus dem Masterprompt entfernen**
- **Schema NICHT statt Masterprompt ins Projektwissen schieben**
- **große Runtime-Module NICHT vorschnell splitten**
- **den freien Headroom NICHT künstlich füllen**
- **den Masterprompt NICHT zusätzlich in Personalisierung duplizieren**

Begründung:
ZEITRISS funktioniert gerade. Alles, was an Save-Vertrag, Regeltreue und
Kontinuität hängt, sollte auf Lumo eher **konzentriert** als weiter verstreut
werden.

---

## Kurzfassung für Flo

Wenn du jetzt nur das Sicherste machen willst:

1. **Masterprompt nur in Projekt-Anweisungen**
2. **Personalisierung leer lassen**
3. **Nur 19 Default-Dateien ins Projektwissen**
4. **Kein Repo-Content-Split vor dem Langzeit-Playtest**
5. **Nur Lumo-Doku + Upload-Pack ergänzen**

Das ist der Patch mit der besten Risiko/Nutzen-Balance.
