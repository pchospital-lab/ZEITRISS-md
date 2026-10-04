---
title: "Spielerstart — ZEITRISS im Terminal"
version: 1.0.0
tags: [guide]
---

# Spielerstart — ZEITRISS im Terminal

Der Terminal-Client ist ein kontrolliert offline geprüfter Entwicklungskandidat, keine fertige Endnutzer-Installation. Zum portablen Chat-Weg ohne Terminal: [README](../README.md) und [Koop-Leitfaden](koop-online-spielen.md). Prüfgrenzen: [mmo-sim.md](mmo-sim.md).

## Starten

Voraussetzung: entpackter ZEITRISS-Ordner, installiertes `python3` und ein Terminal in diesem Ordner. Starte:

```bash
python3 scripts/launcher.py
```

Wähle **`[M] ZEITRISS MMO-Sim (Terminal, kein Browser)`**. `[3]` startet dagegen den Browser für den portablen Chat-Weg; beide Wege sind nicht austauschbar.

Echtes Spielen benötigt eine getrennt eingerichtete KI-Spielleitung (SL), KI-Mitspieler zusätzlich eine Persona-Anbindung. Siehe [Setup-Guide](setup-guide.md). Diese Anleitung ist kein Nachweis einer abgeschlossenen Einrichtung.

## Das Menü, Taste für Taste

Zum Fortsetzen wählst du `[l]` oder `[g]`. Den fehlenden Standüberblick und `[e]` erklärt „Beenden, fortsetzen, Stand ansehen“.

- **`[n]`** — vorhandene Figur aktivieren **oder** eine neue erschaffen.
- **`[i]`** — Figur importieren: Dateipfad oder mehrzeiliger JSON-Text. **Beides** mit einer eigenen Zeile `ENDE` abschließen, auch einen reinen Dateipfad; sonst wartet der Client weiter.
- **`[e]`** — deinen aktuellen Save als Text anzeigen **und** zusätzlich in eine Datei schreiben.
- **`[g]`** — eine lokale Runde **geführt** einrichten: fragt Schritt für Schritt, wer mitspielt.
- **`[l]`** — direkt spielen/fortsetzen (der Weg, den `[g]` am Ende ohnehin aufruft).
- **`[c]`** — deine KI-Spielgemeinschaft anlegen **oder fortsetzen**: Besteht schon eine, setzt du sie fort (keine zweite Gemeinschaft, keine neue Population). Gibt es noch keine und sind SL-/Persona-Anbindung als Objekte konfiguriert, wählst du bewusst die **Herkunft der Startprofile** — ein klar als Demo/synthetisch gekennzeichneter Pool oder eine getrennte, als „production" bezeichnete Neuanlage. Das ist **keine** Offline-/Kostenlosmodus-Entscheidung: Im direkt anschließenden, persona-geführten Erschaffungsdialog können **beide** Herkünfte echte, budgetpflichtige Anfragen auslösen, solange die jeweilige Persona weder bereits abgeschlossen noch gesperrt ist. Eine konfigurierte Anbindung ist dabei nur eine Objektprüfung, keine Garantie einer tatsächlich funktionierenden Verbindung (die kann erst beim echten Aufruf fehlschlagen). Ohne konfigurierte SL-/Persona-Anbindung bleibt der gesamte Erschaffungsdialog ohne jeden Modellaufruf.
- **`[b]`** — deine eigenen, bereits über `[c]` angelegten KI-Personas in einem begrenzten Fenster zusammenbringen. Das ist **keine** öffentliche Lobby mit fremden Spielern, sondern wirkt nur auf deinen eigenen Bestand.
- **`[s]`** — Status/Einstellungen ansehen (reine Anzeige).
- **`[x]`** — Hauptmenü beenden; kein Abbruchbefehl während einer Runde.

## Solo spielen

Eine eigene Figur brauchst du vorher über `[n]`. Danach `[l]` wählen, ohne weitere Menschen oder KI-Personas. Auch solo bleibt die KI-Spielleitung dabei.

## Mehrere Menschen an einem Gerät

Bis zu fünf Menschen insgesamt (inklusive Leader) können sich **ein** Terminal teilen. Der einfachste Weg ist `[g]`: Du wählst „Mehrere Menschen an diesem Gerät", wählst bekannte Mitspieler aus oder registrierst neue. **Bei einer neu registrierten Person:** Die Registrierung selbst legt noch **keine fertige Figur** an — ohne eine bereits abgeschlossene eigene Figur bricht die anschließende Bestätigung für diese Person ab und verlangt zuerst ihren eigenen Teilnehmer-Durchgang (`[n]` neu erschaffen oder `[i]` importieren); danach die lokale Runde erneut einrichten. Eine normale Menüführung, die dafür eigens auf die Identität der neu registrierten Person umschaltet, gibt es heute nicht — `[n]`/`[i]` arbeiten immer unter der beim Programmstart festgelegten eigenen Teilnehmer-ID weiter, auch nach einem erneuten Launcher-Aufruf (offene, noch nicht geschlossene Erstnutzerlücke). Jeder bestätigt am Ende seine eigene, dann vorhandene Figur ausdrücklich, und du bestimmst den Leader (du selbst oder eine eingeladene KI-Persona). Vor jeder Übergabe des geteilten Terminals an eine andere Person zeigt der Client Name, Teilnehmer-ID und Figur an und verlangt eine bewusste Bestätigung — niemand übernimmt unbemerkt.

## KI-Mitspieler (optional)

Beim Einrichten einer Runde kannst du KI-Personas einladen — eine Einladung ist **keine automatische Zusage** (Annahme, Ablehnung oder Pause sind echt, nicht vorgetäuscht). Hast du dabei bestimmte Teilnehmer ausdrücklich angefragt und sagt nicht jeder zu, startet die Runde **nicht automatisch** ohne sie oder mit einer stillschweigend verkleinerten Gruppe: Der Client meldet offen, wer fehlt, und verlangt eine bewusste neue Auswahl — einfach `[l]` bzw. `[g]` erneut aufrufen.

## Figur: wählen, erschaffen, importieren, exportieren

- **Wählen/neu erschaffen:** `[n]` aktiviert eine vorhandene Figur oder startet bewusst eine weitere Erschaffung, niemals automatisch.
- **Import/Export:** `[i]` beziehungsweise `[e]`, wie oben beschrieben.
- **Rollentausch zwischen Mensch und KI-Persona während der Runde:** Dafür gibt es keinen eigenen Menüpunkt — ein solcher Wunsch lässt sich nur als normale Absprache im Zugtext äußern. Belegt ist, dass diese Absprache am Tisch ankommt; dass Figur, Spielstand und Zugrecht dabei tatsächlich zuverlässig umgebunden werden, ist nicht geprüft.

## Wer gerade eingibt, wer an die Spielleitung sendet

Am geteilten Terminal gibt zu jedem Zeitpunkt **eine** Person ein. Bei einer geführten Runde (`[g]`) zeigt der Client vor jedem Wechsel klar, an wen die Eingabe übergeben wird, und verlangt eine bewusste Übernahme-Bestätigung — das gilt auch für die Rückübergabe an dich. Der **Leader** ist diejenige Person (Mensch oder zustimmende KI-Persona), deren Zugtext **direkt** an die Spielleitung geht. Für Gäste unterscheidet der Client je Moment: Der **erste** Zug eines neu beigetretenen Gasts (dein Import-/Anker-Save) geht ebenfalls, über den Leader weitergeleitet, bis zur Spielleitung durch. **Jeder weitere, reguläre** Gastzug wird dagegen zunächst nur als Tischnachricht gespeichert und dem Leader vor seinem nächsten Zug als „[Tischabsprache] {Name}: {Text}" angezeigt — er geht nicht selbst direkt an die Spielleitung. Zusätzlich kann am Ende eines Abschnitts eine **private Abschlussnotiz** abgefragt werden (für Menschen freiwillig, leere Antwort erlaubt) — sie wird **nie** weitergeleitet, nur lokal gespeichert; lokale Nichtweiterleitung bedeutet aber **keine** Vertraulichkeit gegenüber anderen Menschen, die am selben geteilten Terminal mitlesen. Der Eingabe-Prompt ist für alle diese Fälle derselbe generische „Deine Aktion:" — der Client zeigt dabei nicht sichtbar an, dass gerade die private Notiz gemeint ist; eine erkennbare, frei wählbare private Eingabe gibt es heute nicht.

## Beenden, fortsetzen, Stand ansehen

**Menü beenden:** `[x]` ist eine Hauptmenü-Auswahl, kein überall gültiger Spielabbruch. Bist du bereits mitten in einer Runde bei „Deine Aktion", ist ein eingegebenes `x` **kein** Abbruchbefehl, sondern wird als ganz normaler Spieltext verarbeitet — wohin dieser Text tatsächlich geht (direkt an die Spielleitung oder zunächst nur als Tischabsprache an den Leader), hängt vom Moment ab, siehe oben „Wer gerade eingibt, wer an die Spielleitung sendet". Eine sichere Unterbrechung außerhalb des Menüs ist Ctrl-C im Terminal (pausiert, kein weiterer Modellaufruf). **Fortsetzen:** Es gibt (noch) keine eigene „Fortsetzen"-Taste — und die vorgesehene Info-Zeile mit deinem letzten Stand wird über den normalen Startweg heute nicht angezeigt, selbst wenn ein Stand existiert (bekannte, noch offene Lücke). Du startest einfach erneut `[l]` oder `[g]`, ohne vorherige Anzeige, welcher Stand das wäre. `[e]` zeigt dir separat und zuverlässig deinen tatsächlich aktuellen, veröffentlichten Stand (nicht nur eine Zwischennotiz) — das ist der Weg, deinen Stand vor einem Neustart zu prüfen; gleichzusetzen mit der (heute nicht angezeigten) automatischen Zusammenfassung ist das nicht. Keine Zusage zur vollständigen Datenverlustfreiheit: Es gilt jeweils nur der zuletzt tatsächlich geschriebene gültige Save.

## Wenn etwas fehlt: ehrliche Meldung statt Vortäuschung

Echtes gemeinsames Spielen braucht eine eingerichtete SL-Anbindung (dieselbe wie beim portablen Chat-Weg, siehe [Setup-Guide](setup-guide.md)) und, für KI-Mitspieler, eine Persona-Anbindung. Fehlt die **SL-Anbindung**, bekommst du beim Versuch zu spielen eine klare Textmeldung, keinen stillen Fehlstart. Fehlt dagegen die **Persona-Anbindung** ausgerechnet beim Einladen eines KI-Gastes, ist das heute nicht in jedem Fall ebenso ruhig abgefangen: Statt einer klaren Textzeile kann in diesem einen Fall eine unerwartete Fehlermeldung erscheinen (bekannte, noch offene Einzellücke). Unabhängig davon bleibt: **kein** stiller Fehlstart und **kein** vorgetäuschter Erfolg.

## Was heute (noch) nicht geht

Eine öffentliche Lobby gibt es nicht: `[b]` nutzt ausschließlich deine KI-Gemeinschaft. Netzwerkspiel über getrennte Geräte ist noch nicht ausgeliefert.
