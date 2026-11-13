---
title: "Spielerstart — ZEITRISS im Terminal"
version: 1.1.0
tags: [guide]
---

# Dein erster Einsatz im Terminal (Linux Mint)

Hier findest du den Weg von der Einrichtung bis zu deiner nächsten Runde auf
Linux Mint:
**starten → Figur wählen → spielen → speichern → fortsetzen**. Nach einem
abgeschlossenen Abschnitt nimmst du deinen Chrononauten als Save-Datei mit
und setzt ihn auf einem anderen eingerichteten ZEITRISS-Rechner fort.
Für das optionale Ausprobieren im Chat nutze den [Chat-Setup-Guide](setup-guide.md).

> Der lokale Speicher- und Fortsetzungsweg ist als begrenzte Beta-Etappe
> unabhängig abgenommen (29. Oktober 2026). Der vorhandene Referenzlauf
> umfasst fünf Figuren in einem Duo und einem Trio mit je zwei geschlossenen
> Runden, fünf geladene Endsaves und eine wirksame Duo-Folgeaktion.
> [Prüfstand und Grenzen](terminal-status.md)

## Installation

> **Reiner Gast an einem fremden Tisch?** Wenn du nur bei jemandem mitspielst,
> der den Tisch und die KI-Spielleitung bereitstellt (lokaler
> Betreiber-/Gast-Tisch), brauchst du **keinen eigenen Modellzugang** und nicht
> die volle Einrichtung unten — du tippst über deine zugewiesenen Kanäle mit und
> machst selbst keine Modellaufrufe. Folge direkt dem Gastweg im
> [Koop-Leitfaden: Lokal mit Betreiber und Gästen](koop-online-spielen.md). Die
> Installation unten gilt für den eigenen Spiel- oder Betreiberstart.

Entpacke das heruntergeladene ZEITRISS-Projekt (auch ein Pfad mit
Leerzeichen funktioniert). Der normale Weg dorthin ist der Dateimanager:
**Doppelklick auf `zeitriss.sh`** im entpackten Ordner. Nemo (der
Mint-Standard-Dateimanager) fragt dabei einmalig, wie die Datei ausgeführt
werden soll — wähle **„Im Terminal ausführen"**. Das ist die erforderliche
einmalige lokale Ausführungs-/Vertrauensfreigabe des Dateimanagers; danach
öffnet sich ein Terminal mit dem Launcher. Alternativ startest du denselben
Launcher direkt aus einem bereits offenen Terminal im entpackten Ordner:

```bash
./zeitriss.sh
```

Der Starter richtet beim ersten Lauf automatisch eine eigene, private
Projektumgebung unterhalb des Projektordners ein (`.venv/`, Python 3.12 als
dokumentierte Referenzversion) und installiert dort die für den Spielbetrieb
benötigten Bibliotheken (u. a. zur Saveprüfung, s. `requirements-ci.txt`).
Das ersetzt den früheren Weg mit manuell aktivierter Entwickler-venv: kein
Git-Checkout, kein eigenes `python3 -m venv`, keine globale `pip install`,
kein Spielbetrieb als root. Ein gewöhnlicher späterer Start installiert
nichts erneut. Fehlt Python 3 oder das Python-Modul `venv` (z. B. auf einer
Mint-Minimalinstallation), nennt der Starter das konkret im Terminal
(z. B. `sudo apt install python3-venv`) und bricht sichtbar ab, statt
stumm weiterzulaufen. Andere Betriebssystem- und Installationsvarianten
sind hier nicht als geprüft ausgewiesen.

Echtes Spielen braucht außerdem eine eingerichtete KI-Spielleitung und ein
begrenztes Modellbudget. Für KI-Mitspieler kommt eine Persona-Anbindung
hinzu. Folge dazu dem [Setup-Guide](setup-guide.md); die private
Projektumgebung allein richtet noch keinen Modellzugang ein. Modellzugangsdaten gehören
nicht in Spielstände, öffentliche Protokolle oder das Repository.

## Starten

```bash
./zeitriss.sh
```

**Beim allerersten Start** fehlt die KI-Spielleitung noch — wähle im
Launcher-Menü zuerst **`[1] ZEITRISS einrichten`** (Details:
[Setup-Guide](setup-guide.md#komplett-setup-in-openwebui-empfohlen)).
Danach, und bei jedem weiteren Start, wähle **`[M] ZEITRISS spielen
(Terminal)`** — das ist der normale Produktweg. Die Browserauswahl `[3]`
gehört zum nachgeordneten, optionalen Chat-Spielweg. Direktaufruf
`python3 scripts/mmo_sim.py` funktioniert weiterhin unverändert und
verwendet dieselbe private Projektumgebung und denselben Datenspeicherort.

Beim ersten Start erscheint eine kurze Einführung. Mit `einfuehrung` kannst
du sie im Hauptmenü erneut öffnen. Das Terminal verwendet beim normalen
Neustart die zuletzt für seine Datenablage verwendete Teilnehmeridentität.
Eine abweichende `--participant`-Angabe ist ein bewusster Teilnehmerwechsel.

## Dein Menü

| Eingabe | Was du dort machst |
| --- | --- |
| `charaktere` | Figur auswählen, erschaffen, importieren oder exportieren |
| `spielen` | Eine Runde zusammenstellen oder deine KI-Spielgemeinschaft öffnen |
| `fortsetzen` | Einen vorhandenen eigenen Stand fortsetzen |
| `registrieren` | Eine weitere Person am gemeinsamen Terminal aufnehmen |
| `tisch` | Tisch suchen/anfragen (Gast) oder anbieten/annehmen/starten (Betreiber) — gemeinsames lokales Spielen, siehe [Koop-Leitfaden: Lokal mit Betreiber und Gästen](koop-online-spielen.md) |
| `einstellungen` | Status und Einstellungen ansehen |
| `beenden` | Das Hauptmenü verlassen |

`?` oder `/hilfe` zeigt Hilfe zur aktuellen Eingabe, ohne einen Spielzug zu
verbrauchen. `/stand` zeigt den passenden eigenen Stand. Während eines
Abschnitts blätterst du mit `/verlauf` durch dessen bisherige Einträge;
`/pause` hält die Runde kontrolliert an. Im Hauptmenü erklären diese
Abschnittsbefehle, dass noch kein entsprechender Abschnitt läuft.

Deinen eigenen Charakterbogen (letzter gespeicherter Stand) siehst du jederzeit
rein lokal mit `/bogen` — an jeder normalen Eingabe, auch am Spielzug, ohne
einen Zug zu verbrauchen und ohne dass dafür die Spielleitung angesprochen
wird. Im Hauptmenü bzw. unter `charaktere` erreichst du dieselbe Anzeige auch
über `bogen` bzw. `!bogen`. Diese Anzeige ist ein unveränderlicher Schnappschuss
zum Zeitpunkt des Öffnens; spätere Spielfortschritte zeigt erst ein bewusstes
erneutes `/bogen`. Ingame bleibt `!bogen` (ohne Slash, während eines laufenden
Dialogs mit der Spielleitung) unverändert ein an die Spielleitung
weitergereichter Text, keine lokale Anzeige.

## Figur wählen, erschaffen, importieren, exportieren

Öffne `charaktere`. Du kannst eine vorhandene Figur aktivieren oder bewusst
eine weitere erschaffen. Bei mehreren Figuren wählst du über die angezeigte
Nummer; die Chrononaut-ID bleibt ebenfalls verwendbar.

Beim **Import** kannst du einen Dateipfad oder mehrzeiligen JSON-Text
angeben. Schließe beides mit einer eigenen Zeile **`ENDE`** ab — auch einen
Dateipfad. Ohne diese Abschlusszeile wartet die Eingabe weiter.

Beim **Export** wird dein aktueller gültiger Save angezeigt und zusätzlich
in eine Datei geschrieben. Bewahre eine eigene Kopie auf, zum Beispiel auf
einem USB-Stick — so nimmst du deinen Chrononauten mit und importierst ihn
auf einem anderen eingerichteten ZEITRISS-Rechner über denselben Weg. Eine
begonnene, aber noch unvollständige Erschaffung ist noch kein fertiger
Spielstand.

## Solo spielen

Wähle oder erschaffe zuerst deine Figur. Öffne anschließend `spielen` und
stelle die Runde ohne weitere Teilnehmer zusammen. Auch solo übernimmt die
KI die Spielleitung. Eine KI-Spielerpersona ist dafür nicht erforderlich.

## Gemeinsam an einem Gerät spielen

Über `registrieren` bekommt eine weitere Person ihre Teilnehmeridentität.
Bestätigt sie die Fokusübernahme, wählt, erschafft oder importiert sie ihre
eigene Figur im selben Terminal. Anschließend kehrt die Eingabe zu dir zurück.

Im geführten Rundenaufbau kannst du eine neue Person auch über `neu:<Name>`
aufnehmen. Ihre Figurerstellung läuft vor dem gemeinsamen Start. Eine
abgelehnte Fokusübernahme löscht die Registrierung nicht; die Figur lässt
sich später ergänzen. Private Tische umfassen einen bis fünf Spieler
inklusive Leader, Menschen und KI-Personas zusammen.

Bei jedem Teilnehmerwechsel zeigt der Client, wer jetzt eingibt. Die neue
Person bestätigt die Übernahme. Das geteilte Terminal ist ein gemeinsamer
Bildschirm; lokale Notizen sind dadurch nicht automatisch vor Mitlesenden
privat.

## KI-Mitspieler einladen

KI-Personas können eine Einladung annehmen, ablehnen oder pausieren. Sie
sind eigene Mitspieler mit Figuren, keine Nebenfiguren der Spielleitung und
keine automatischen Ersatzspieler. Fehlt eine ausdrücklich gewünschte
Zusage, startet nicht stillschweigend eine verkleinerte Wunschgruppe.
Wähle deine Runde in diesem Fall bewusst neu.

Die Herkunft einer Community aus Demo- oder Produktionsprofilen entscheidet
nicht darüber, ob die anschließende Erschaffung echte Modellkosten erzeugt.
Auch Demo-Profile sind kein allgemeiner Kostenlosmodus.

## Personas nachziehen oder vorspielen lassen

Du wirst beim Spielen **nie ausgebremst**: Deine eigenen Abschnitte spielst du,
wann du willst, ohne auf KI-Personas zu warten. Ob und wann deren eigene
Abschnitte laufen, entscheidest allein du — nie automatisch im Hintergrund,
nie mit ständigem Nachfragen.

Im begrenzten Lobbyfenster stehen dafür drei bewusste Aktionen:

- **`[3]` Personas spielen lassen (Catch-up):** die von dir gewählten Personas
  spielen ihre Abschnitte nach, bis sie gleich **viele** Abschnitte gespielt
  haben wie du. (Fair ist die gleiche *Anzahl* Abschnitte — welchen Inhalt oder
  welches Level dabei herauskommt, ist egal und darf sich unterscheiden.)
- **`[5]` Personas vorspielen lassen:** die gewählten Personas legen **jetzt
  einen Abschnitt vor** (praktisch, wenn du kurz weg musst) — du spielst
  danach deinen und gruppierst dich wieder.
- **`[4]` Aktive Gruppe / Ausschluss:** nimm eine Persona aus deiner Gruppe
  heraus oder wieder auf. Eine ausgeschlossene Persona wird **nie** nachgezogen,
  taucht nie als Kandidat auf und stört dich nie. So spielst du die Kampagne
  z. B. nur mit deiner Stammgruppe.

Bei `[3]`/`[5]` wählst du, **welche** Personas mitmachen (kommagetrennt, leer =
alle in Frage kommenden) und bekommst vorher einen klaren Hinweis, dass du
währenddessen **wartest**. Personas, mit denen du gerade an einem
**laufenden** gemeinsamen Abschnitt gebunden bist, werden währenddessen weder
nachgezogen noch vorgespielt — euer Abschnitt läuft ja noch. Ist der gemeinsame
Abschnitt **abgeschlossen**, kannst du dieselben Mitspieler über `[5]` aber
bewusst ihren **nächsten eigenen** Abschnitt vorspielen lassen (genau der
Pausen-Fall von oben); fürs Nachziehen `[3]` sind sie dann ohnehin schon
gleichauf.
Im Normalfall brauchst du das alles gar nicht: spiel einfach mit deiner
Gruppe weiter, und zieh die anderen höchstens mal in einer eigenen Spielpause
nach.

## Wer empfängt deine Eingabe?

Die Empfängerzeile vor dem Zug ist maßgeblich. Der Leader sendet an die
Spielleitung. Der erste Beitrag eines neuen Gasts mit seinem Save wird über
den Leader weitergegeben. Spätere Gastbeiträge sind zunächst Tischabsprache
und erscheinen beim Leader vor dessen nächstem Zug.

Eine ausdrücklich als eigene lokale Abschlussnotiz gekennzeichnete Eingabe
wird dagegen weder an Tisch noch Spielleitung weitergeleitet. Sie ist
freiwillig und darf leer bleiben. Ein verlässlicher technischer Rollenwechsel
zwischen Mensch und KI während einer laufenden Runde ist nicht als eigene
Menüfunktion nachgewiesen.

## Beenden, fortsetzen, Stand ansehen

Im Hauptmenü beendet `beenden` den Client. Während einer Runde verwendest du
**`/pause`**, Ctrl-C oder EOF. Ein einzelnes `x` oder `q` in einem normalen
Spielzug ist kein universeller Abbruchbefehl, sondern kann Spieltext sein.
Mit einem vorangestellten Backslash lässt sich ein Befehl als Text eingeben,
beispielsweise `\/pause`.

Starte später denselben Client mit derselben Datenablage und wähle
`fortsetzen`. Ein eigener gültiger Save kann auch ohne Community fortsetzbar
sein. Bei einer nur begonnenen Erschaffung weist die Fortsetzen-Karte auf
`charaktere` beziehungsweise `n` hin; sie behauptet keinen fertigen Save.

Gespeichert wird im HQ mit `!save` (oder `!speichern`): die Spielleitung
gibt deinen aktuellen Stand als Save-Block aus, der Client erntet ihn und
schließt damit den laufenden Abschnitt ab. Danach zeigt dir der Client deine
persönliche **Abschlusskarte** mit den nächsten Schritten als nummerierte
Auswahl — den eigenen Stand exportieren und zurück zu deinem vorherigen Menü
(eine leere Eingabe oder `/zurueck` führt ebenfalls dorthin): zum Hauptmenü,
wenn du dort geparkt warst; zum Tisch-Untermenü, wenn du dort warst; und zur
vorherigen "Welcher Tisch?"-Frage, wenn du konkret in dieser noch offenen
Tischfrage steckst. Spielst du als Gast an einem
Tisch mit, kommt eine zulässige Folgeaktion wie einen weiteren Tisch
suchen/beitreten hinzu. `!bogen` zeigt nur den Charakterbogen an und
speichert nicht. In Briefing, Einsatz und Debrief ist Speichern gesperrt
(SaveGuard) — erst zurück im HQ. Die Save-Erkennung haengt am `!save`-
Kommando und am tatsächlichen Save-Block, nicht an einer festen
Formulierung der Spielleitung.

Bei einem unterbrochenen Abschnittsabschluss kann eine bereits vollständig
lokal verbuchte und eindeutig zugeordnete Originalantwort wiederverwendet
werden. Bei unklarem Ausgang bleibt die Runde angehalten, statt denselben
Zug auf Verdacht erneut zu senden. Der Automatismus ist offline geprüft;
seine vollständige Live-Abnahme steht separat aus.

## Best Effort und SAVECOMPAT

Besteht ein `!save`-Kandidat die Prüfung nicht, kann das System höchstens
**drei** zusätzliche vollständige Korrekturen anfordern; ein früherer
brauchbarer Erfolg beendet das sofort. Ein geeigneter Kandidat **mit**
strukturellen Listenwarnungen kann den Abschluss trotzdem ermöglichen.
Die App berücksichtigt dafür auch die ursprüngliche Ausgabe und übernimmt
den besten zulässigen Stand. Harte Bindungs- oder Driftkonflikte werden
dadurch nicht aufgehoben. Verbleibende Warnungen sind **kein** bestandener
Schema-Check; der nächste Load bereinigt den Stand nicht garantiert vollständig.

Für den Kompatibilitätsweg kann das System einen **SAVECOMPAT**-Stand samt
Herkunft sichern. Dieser zählt selbst noch nicht als Export oder
abgeschlossener Abschnitt — Details:
`systems/gameflow/speicher-fortsetzung.md#kompatibilitaetsstand`.
Welche Fehlerart wie behandelt wird, hängt vom Einzelfall ab: Es gibt
**keine** pauschale Regel wie „Typfehler landen immer bei SAVECOMPAT", und
keine Garantie für einen verlustfreien oder vollständig schemagültigen
Export beim nächsten Start. Maßgeblich ist, was dein Terminal beim
tatsächlichen Laden/Fortsetzen übernimmt.

## Wenn der Start nicht gelingt

Eine fehlende Spielleiter- oder Persona-Anbindung wird als solche gemeldet.
Eine Budget- oder Zustandsgrenze ist kein abgeschlossener Spielzug. Ändere
bei einem unklaren Ausgang nicht einfach Teilnehmer-ID, Generation oder
Datenablage, um denselben offenen Vorgang neu zu starten. Halte den Zustand
fest und nutze die [Betriebsdokumentation](mmo-sim.md).

## Bekannte Grenzen

Das Terminal ist ein lokales Spiel an einem Rechner, ohne Netzwerk-Lobby und
ohne Remote-Mitspielen über getrennte Geräte — das ist keine offene
Baustelle, sondern die aktuelle Produktgrenze (Linux Mint, lokal, Stand 8.
November 2026). Für das optionale Ausprobieren über eine Chatplattform nutze
den [Koop-/Chat-Leitfaden](koop-online-spielen.md).

Der abgenommene lokale Referenzweg und die Grenzen weiterer Betriebsarten
stehen im [Terminalstatus](terminal-status.md). Die vollständige Live-Abnahme
zusätzlicher Crash-Recovery-Pfade bleibt separat. Ein persönlicher Save
ersetzt kein vollständiges Community-Backup.

## Vorhandene Tastenkürzel

Die ausgeschriebenen Menüpunkte sind der normale Einstieg. Weiterhin gelten
`n` für Figurenwahl/Erschaffung, `i` für Import, `e` für Export, `g` für die
geführte Runde, `l` für direkten Spielstart/Fortsetzen, `c` für die eigene
KI-Spielgemeinschaft, `b` für deren begrenztes Spielfenster, `s` für Status
und `x` für das Beenden des Hauptmenüs. Die Kürzel sind keine zweite sichtbare
Menühierarchie.
