---
title: "ZEITRISS Lumo Setup"
version: 1.0.0
tags: [meta, setup, lumo]
---

# ZEITRISS auf Lumo (Proton) einrichten

Diese Anleitung beschreibt den **minimalen, stabilen Setup-Pfad** für Lumo.
Ziel ist ein sauberer Projektaufbau ohne Doppel-Instruktionen und ohne falsche
Erwartungen an die Modelltreue.

## Klare Empfehlung

- **Masterprompt nur in die Projekt-Anweisungen**
- **nicht** zusätzlich in Personalisierung
- **nicht** ins Projektwissen
- ins Projektwissen nur die **19 Default-Module**
- keine inhaltlichen Umbauten vor dem Langzeit-Playtest

## Was gehört wohin?

### Projekt-Anweisungen

Hier kommt der komplette Inhalt von `meta/masterprompt_v6.md` hinein.

### Projektwissen

Hier gehören nur die 19 Default-Module hinein (alle `slot: true` aus
`master-index.json`).

Praktischer Weg: Erzeuge mit `scripts/export-knowledge-pack.sh` ein kuratiertes
Upload-Paket und nimm daraus nur den Ordner `knowledge/`.

### Personalisierung

Für ZEITRISS möglichst leer lassen oder nur neutral halten, z. B.:

`Antworte standardmäßig auf Deutsch. Sei direkt, klar und kritisch.`

**Wichtig:** Den ZEITRISS-Masterprompt hier nicht doppeln.

## Modell-Erwartung klar kommuniziert

ZEITRISS ist auf Lumo spielbar und kann Spaß machen, gerade bei
Abomodellen ohne Tokenfokus. Gleichzeitig gilt:

- **Referenz-/Best-Erlebnis:** `anthropic/claude-sonnet-4.6`
- andere Modelle (inkl. Lumo-Setups) können beim Thinking und bei
  Regeldetails merkbar abweichen

Das soll keine Plattform abwerten, sondern Erwartungsmanagement sichern:
Das stärkste ZEITRISS-Erlebnis entsteht aktuell mit den stärksten Modellen.

## Schritt-für-Schritt

1. Neues Lumo-Projekt `ZEITRISS` erstellen.
2. In **Anweisungen** `meta/masterprompt_v6.md` einfügen.
3. In **Projektwissen** nur die 19 Default-Module laden (idealerweise via
   Export-Paket).
4. Personalisierung leer/neutral halten.
5. Websuche im Spielbetrieb deaktivieren.
6. Neuen Chat starten mit `Spiel starten (solo klassisch)` oder `Spiel laden`.

## Sicherheit & Stil

Der Action-Contract bleibt plattformübergreifend gleich:

- filmisch, in-world, outcome-basiert
- keine Schritt-für-Schritt-Anleitungen für reale Straftaten
- keine Real-World-How-to-Ausleitungen

Damit bleibt ZEITRISS stiltreu und kompatibel mit den Sicherheitsgrenzen der
jeweiligen Plattform.
