---
title: "ZEITRISS Lumo Setup"
version: 1.1.0
tags: [meta, setup, lumo]
---

# ZEITRISS auf Lumo (Proton) einrichten

## Export-Paket erzeugen

```bash
python scripts/setup.py --export
```

Das erstellt einen Ordner mit:
- `knowledge/` — 19 Wissensdateien (mit Unterordnern)
- `system/SYSTEM_PROMPT_ONLY.md` — Masterprompt
- `SETUP-ANLEITUNG.md` — Kurzanleitung

Für flache Dateien ohne Unterordner (einfacher für Einzel-Upload):

```bash
python scripts/setup.py --export --flat
```

## Einrichtung

1. **Proton Drive:** Ordner `ZEITRISS` erstellen.
2. Alle Dateien aus `knowledge/` in diesen Drive-Ordner laden.
3. **Lumo:** Neues Projekt `ZEITRISS` erstellen.
4. In **Anweisungen**: Inhalt von `system/SYSTEM_PROMPT_ONLY.md` einfügen.
5. **Projektwissen**: Den Drive-Ordner `ZEITRISS` verlinken.
6. Personalisierung leer lassen oder neutral:
   `Antworte standardmäßig auf Deutsch. Sei direkt, klar und kritisch.`
7. Websuche im Spielbetrieb **deaktivieren**.
8. Neuen Chat starten: `Spiel starten (solo klassisch)`

**Tipp:** Das Setup ist ein Desktop-Job (5 Min). Danach kann man auf dem
Handy einfach das Projekt öffnen und losspielen — Proton Drive
synchronisiert automatisch.

## Was gehört wohin?

| Ziel | Inhalt | Nicht |
| ---- | ------ | ----- |
| **Projekt-Anweisungen** | `SYSTEM_PROMPT_ONLY.md` | Nicht doppeln in Personalisierung |
| **Projektwissen** | 19 Dateien aus `knowledge/` | Nicht den Masterprompt hochladen |
| **Personalisierung** | Leer oder neutral | Keinen ZEITRISS-Prompt hier |

## Erwartungsmanagement

- **Referenz-Erlebnis:** `anthropic/claude-sonnet-4.6` auf OpenWebUI
- Lumo ist spielbar und macht Spaß, aber andere Modelle können bei
  Regeldetails und Thinking abweichen
- Das ist kein Plattform-Bashing — stärkste Modelle = stärkstes Erlebnis

## Bestehendes Charaktermaterial

Funktioniert auch auf Lumo. Wenn kein zuverlässiger Bildinput: Textweg
mit Rolle, Hintergrund, Stärken, Schwächen, prägendes Talent und
Ausrüstungsrichtung.
