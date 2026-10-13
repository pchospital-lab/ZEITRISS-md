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

Beim allerersten Start (leeres Datenverzeichnis) zeigt der Client eine kurze, drei Zeilen lange Einführung — sie blockiert nichts, deine nächste Eingabe läuft sofort normal weiter. Über `einfuehrung` im Hauptmenü kannst du sie jederzeit erneut sehen.

## Das Menü: KISS-Hauptmenü und Kompatibilitäts-Hotkeys

Das Hauptmenü zeigt **nur noch** die **eine** Zielhierarchie als Wörter (`fortsetzen`/`spielen`/`charaktere`/`registrieren`/`einstellungen`/`beenden`) — der vollständige alte Einzelbuchstaben-Hotkeybaum erscheint auf diesem Bildschirm **nicht mehr zusätzlich darunter** (R06-Korrektur: zuvor stand hier fälschlich, er bleibe sichtbar). Die Original-Hotkeys funktionieren als **unsichtbare** Kompatibilitätsaliase weiterhin unverändert (siehe unten) — sie werden nur nicht mehr auf dem Bildschirm selbst beworben, damit es nicht dauerhaft zwei sichtbare Normalansichten nebeneinander gibt:

- **`spielen`** → Untermenü „Runde zusammenstellen" (= `[g]`/`[l]`) bzw. „Meine KI-Spielgemeinschaft" (= `[c]`/`[b]`).
- **`charaktere`** → Untermenü „Auswählen/neu erstellen" (= `[n]`), „Importieren" (= `[i]`), „Exportieren/ansehen" (= `[e]`).
- **`registrieren`** → siehe „Mehrere Menschen an einem Gerät" unten — die einzige vollständig NEUE Funktion dieser Runde.
- **`einstellungen`** → dasselbe wie `[s]`.
- **`fortsetzen`** → führt fort, wenn eine echte, dir zugeordnete Spielgemeinschaft ODER eine eigene abgeschlossene Figur-Save existiert (siehe „Beenden, fortsetzen, Stand ansehen" unten); ohne jeden Beleg eine ehrliche Meldung statt eines Neuanfangs.
- **`beenden`** → dasselbe wie `[x]`/`q`.

`?`/`/hilfe` zeigt an JEDER Eingabe (Hauptmenü, Untermenüs, Spielzug, Figur-Erschaffungsantwort) Kontexthilfe, ohne Zugverbrauch und ohne die laufende Auswahl zu verwerfen. `/stand` funktioniert ebenfalls überall, auch im Hauptmenü — **am geteilten Terminal während eines laufenden Spielzugs zeigt es dabei den Stand der GERADE EINGEBENDEN Person**, nicht pauschal den Stand der Person, die den Prozess ursprünglich gestartet hat. `/verlauf` und `/pause` (kontrolliert pausieren, dein zuletzt gültiger Stand bleibt erhalten, kein weiterer Modellaufruf) beziehen sich dagegen auf einen laufenden Spielabschnitt — im Hauptmenü, wo es noch keinen solchen Abschnitt gibt, nennen sie das ehrlich statt mit „Unbekannte Auswahl" zu antworten. Innerhalb eines laufenden Abschnitts zeigt `/verlauf` die **vollständige, nie gekürzte** bisherige Historie dieses Schritts über sichtbare Seitennavigation (je 10 Einträge, aktuellste zuerst; eine wiederholte `/verlauf`-Eingabe an derselben Stelle blättert weiter zurück bis „Anfang des Verlaufs erreicht") — nicht mehr nur die letzten 10 Einträge. Ein literaler Text, der wie ein solcher Befehl aussieht, bleibt über ein führendes `\` eingebbar (z. B. `\/pause`). Bare `x`/`q`/ein Fragezeichen mitten im Satz werden dabei NICHT als Abbruch verschluckt.

Die Original-Hotkeys bleiben funktional unverändert erhalten — als dokumentierte, weiterhin genau gleich wirkende Kompatibilitätsaliase, nicht mehr als eigener sichtbarer Menüblock:

- **`[n]`** — vorhandene Figur aktivieren **oder** eine neue erschaffen. Bei
  mehreren vorhandenen Figuren zeigt die Liste jetzt eine Nummer je Eintrag
  (`[1] ...`, `[2] ...`); du kannst zum Aktivieren diese Nummer eingeben (die
  Chrononaut-ID bleibt zusätzlich als Detailweg gültig).
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

Bis zu fünf Menschen insgesamt (inklusive Leader) können sich **ein** Terminal teilen. Der einfachste Weg ist `[g]`: Du wählst „Mehrere Menschen an diesem Gerät", wählst bekannte Mitspieler aus oder registrierst neue. Jeder bestätigt am Ende seine eigene, dann vorhandene Figur ausdrücklich, und du bestimmst den Leader (du selbst oder eine eingeladene KI-Persona). Vor jeder Übergabe des geteilten Terminals an eine andere Person zeigt der Client Name, Teilnehmer-ID und Figur an und verlangt eine bewusste Bestätigung — niemand übernimmt unbemerkt. Die eigene Beitrittsfrage jeder zusätzlichen menschlichen Person („… dieser lokalen Runde beitreten? [j/n]") erkennt dabei ebenfalls `/zurueck`, `/abbrechen` und `/pause`: wer dort pausiert, erzeugt keine Zusage und keinen Tisch mit dieser Besetzung — kein blosses „ungültige Eingabe" wie bei echtem Kauderwelsch.

**Eine ZWEITE, NEUE Person bekommt jetzt ihre eigene Figur direkt im Terminal — auf zwei gleichwertigen Wegen:** Entweder vorab im Hauptmenü **`registrieren`** (Namen eingeben, Fokusübernahme bestätigen — danach läuft `[n]`/`[i]` tatsächlich unter GENAU ihrer neuen Teilnehmer-ID, ohne `--participant`-Kommandozeilenargument oder Launcher-Neustart; nach Abschluss/Abbruch kehrt der Fokus automatisch zu dir zurück), oder direkt **während** der `[g]`-Einrichtung mit `neu:<Name>` an der Mitspieler-Auswahl: Die anschließende Figurbestätigung übergibt für GENAU diese neue Person ebenfalls den Fokus (dieselbe Übernahmebestätigung) und führt sie direkt in die bestehende Erschaffungs-/Import-Fläche — sie schließt ihre Figur fertig ab, bevor die Runde startet, kein separater Teilnehmer-Durchgang nötig. Lehnt die Person die Fokusübernahme (auf beiden Wegen) ab, bleibt sie registriert (keine verlorene Eingabe), aber ohne eigene Figur — über `registrieren` oder einen erneuten `[g]`-Durchgang später nachholbar.

## KI-Mitspieler (optional)

Beim Einrichten einer Runde kannst du KI-Personas einladen — eine Einladung ist **keine automatische Zusage** (Annahme, Ablehnung oder Pause sind echt, nicht vorgetäuscht). Hast du dabei bestimmte Teilnehmer ausdrücklich angefragt und sagt nicht jeder zu, startet die Runde **nicht automatisch** ohne sie oder mit einer stillschweigend verkleinerten Gruppe: Der Client meldet offen, wer fehlt, und verlangt eine bewusste neue Auswahl — einfach `[l]` bzw. `[g]` erneut aufrufen.

## Figur: wählen, erschaffen, importieren, exportieren

- **Wählen/neu erschaffen:** `[n]` aktiviert eine vorhandene Figur oder startet bewusst eine weitere Erschaffung, niemals automatisch.
- **Import/Export:** `[i]` beziehungsweise `[e]`, wie oben beschrieben.
- **Rollentausch zwischen Mensch und KI-Persona während der Runde:** Dafür gibt es keinen eigenen Menüpunkt — ein solcher Wunsch lässt sich nur als normale Absprache im Zugtext äußern. Belegt ist, dass diese Absprache am Tisch ankommt; dass Figur, Spielstand und Zugrecht dabei tatsächlich zuverlässig umgebunden werden, ist nicht geprüft.

## Wer gerade eingibt, wer an die Spielleitung sendet

Am geteilten Terminal gibt zu jedem Zeitpunkt **eine** Person ein. Bei einer geführten Runde (`[g]`) zeigt der Client vor jedem Wechsel klar, an wen die Eingabe übergeben wird, und verlangt eine bewusste Übernahme-Bestätigung — das gilt auch für die Rückübergabe an dich. **Unmittelbar vor jedem Zugprompt zeigt der Client jetzt zusätzlich eine eigene Empfänger-Zeile:** „Empfänger: Spielleitung (SL)" für den Leader, „Empfänger: über Leader an Spielleitung (dein Erstbeitrag, mit deinem Save)" für den allerersten Zug eines neu beigetretenen Gasts, „Empfänger: Tischabsprache (dein Tisch/Leader) — NICHT direkt an die SL" für jeden weiteren, regulären Gastzug. Der dahinterliegende Eingabe-Prompt selbst bleibt unverändert „Deine Aktion:"/„[Name] Deine Aktion:". Konkret: Der **Leader** ist diejenige Person (Mensch oder zustimmende KI-Persona), deren Zugtext **direkt** an die Spielleitung geht. Der **erste** Zug eines neu beigetretenen Gasts (dein Import-/Anker-Save) geht ebenfalls, über den Leader weitergeleitet, bis zur Spielleitung durch. **Jeder weitere, reguläre** Gastzug wird dagegen zunächst nur als Tischnachricht gespeichert und dem Leader vor seinem nächsten Zug als „[Tischabsprache] {Name}: {Text}" angezeigt — er geht nicht selbst direkt an die Spielleitung. Zusätzlich kann am Ende eines Abschnitts eine **private Abschlussnotiz** abgefragt werden (für Menschen freiwillig, leere Antwort erlaubt, Hilfe/`?` verbraucht dabei keinen Reflexionsturn) — sie wird **nie** weitergeleitet, nur lokal gespeichert; lokale Nichtweiterleitung bedeutet aber **keine** Vertraulichkeit gegenüber anderen Menschen, die am selben geteilten Terminal mitlesen. Für diesen vierten, lokalen Fall zeigt der Client unmittelbar vor derselben Eingabestelle jetzt eine eigene, von den drei obigen Empfänger-Zeilen klar unterschiedene Kennzeichnung: **„Empfänger: eigene lokale Notiz (NICHT an Spielleitung/Tisch, freiwillig, leer = keine Notiz, keine Vertraulichkeitszusage bei geteiltem Bildschirm)."** — zuvor zeigte diese Abfrage fälschlich dieselbe Zeile wie ein echter Spielzug (z. B. „Empfänger: Spielleitung (SL)"), obwohl die Notiz tatsächlich nie an SL/Tisch ging.

## Beenden, fortsetzen, Stand ansehen

**Menü beenden:** `[x]`/`beenden` ist eine Hauptmenü-Auswahl, kein überall gültiger Spielabbruch. Bist du bereits mitten in einer Runde bei „Deine Aktion", ist ein eingegebenes `x` **kein** Abbruchbefehl, sondern wird als ganz normaler Spieltext verarbeitet — wohin dieser Text tatsächlich geht, hängt vom Moment ab, siehe oben. Während eines laufenden Zugs pausierst du statt dessen bewusst über **`/pause`** (oder Ctrl-C/EOF im Terminal) — kontrolliert, kein weiterer Modellaufruf, dein zuletzt gültiger Stand bleibt erhalten. **Fortsetzen:** Die Fortsetzen-Zeile erscheint bereits, sobald **irgendein** eigener, gültiger Stand existiert — eine echte, dir zugeordnete Spielgemeinschaft (angelegt über `[c]`) **oder** schon eine einzelne, über `[n]` abgeschlossene Solo-Figur **ohne** jede Gemeinschaft (R06-Korrektur: zuvor stand hier fälschlich, ohne Gemeinschaft bleibe die Zeile grundsätzlich aus — der deutlich häufigere Einstiegsweg „Figur erschaffen → solo spielen" erzeugt nie eine Community und wurde dadurch fälschlich von „Fortsetzen" ausgeschlossen, obwohl ein echter Save vorhanden ist). Mit Gemeinschaft zeigt die Zeile `Fortsetzen: community-<deine-id> · <deine-id> · <chrononaut-id> — <Stand>`; ganz ohne Gemeinschaft (reine Solo-Figur) erscheint an derselben Stelle `Fortsetzen: keine Community · <deine-id> · <chrononaut-id> — <Stand>` — in beiden Fällen führt das Wort `fortsetzen` direkt zurück zur jeweiligen eigenen Runde. **Auch eine bereits begonnene, aber noch NICHT abgeschlossene Erschaffung bekommt eine eigene Fortsetzen-Karte** (UX11, P04-Korrektur — zuvor blieb die Zeile hier fälschlich ganz aus, obwohl real etwas Fortsetzbares existierte): ohne jeden abgeschlossenen Save zeigt sie „Figur-Erschaffung begonnen, noch nicht abgeschlossen (fortsetzen über ‚n'/[charaktere])" statt eines Stand-Textes. Nur wenn wirklich **weder** ein abgeschlossener Save **noch** eine schon begonnene Erschaffung existiert, bleibt die Zeile ganz aus; du startest dann über `[l]`/`spielen` bzw. `[n]`. `[e]` zeigt dir separat und zuverlässig deinen tatsächlich aktuellen, veröffentlichten Stand (nicht nur eine Zwischennotiz). Keine Zusage zur vollständigen Datenverlustfreiheit: Es gilt jeweils nur der zuletzt tatsächlich geschriebene gültige Save.

## Wenn etwas fehlt: ehrliche Meldung statt Vortäuschung

Echtes gemeinsames Spielen braucht eine eingerichtete SL-Anbindung (dieselbe wie beim portablen Chat-Weg, siehe [Setup-Guide](setup-guide.md)) und, für KI-Mitspieler, eine Persona-Anbindung. Fehlt die **SL-Anbindung**, bekommst du beim Versuch zu spielen eine klare Textmeldung, keinen stillen Fehlstart. Fehlt die **Persona-Anbindung** beim Einladen eines KI-Gastes oder eines KI-Leaders, bekommst du jetzt ebenfalls eine ruhige Textzeile (z. B. „Einladung an Persona '…' nicht möglich (Persona-Anbindung: …) — kein Modellaufruf, dieser Gast bleibt außen vor.") statt einer unerwarteten Fehlermeldung; ein einzelner betroffener Gast schließt die übrige Runde nicht aus. Unabhängig davon bleibt: **kein** stiller Fehlstart und **kein** vorgetäuschter Erfolg.

## Was heute (noch) nicht geht

Eine öffentliche Lobby gibt es nicht: `[b]` nutzt ausschließlich deine KI-Gemeinschaft. Netzwerkspiel über getrennte Geräte ist noch nicht ausgeliefert.


Wird direkt nach dem Abschluss-Spielzug einer Szene unterbrochen, holt dein naechster normaler `fortsetzen`-Aufruf die bereits vollstaendig verbuchte Antwort automatisch nach (kein neuer Spielzug, keine Zusatzeingabe deinerseits) — vorausgesetzt, sie ist eindeutig als dieselbe Original-Anfrage erkennbar. Ist sie nur empfangen, aber noch nicht vollstaendig verbucht, oder laesst sich die Herkunft nicht eindeutig binden, pausiert `fortsetzen` statt dessen kontrolliert, ohne deinen Stand zu veraendern. Danach (bei erfolgreicher Ernte) laufen die Pflicht-Reflexionen und der endgueltige Abschluss wie gewohnt.
