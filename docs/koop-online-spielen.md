---
title: "Koop & Online zusammen spielen"
version: 1.2.0
tags: [guide]
---

# ZEITRISS zusammen spielen — Koop & Online

Dieser Leitfaden beschreibt, **wie man ZEITRISS mit anderen spielt** — zu zweit
am Küchentisch genauso wie mit einer Runde, die sich über die halbe Welt
verteilt findet. Es braucht **keinen zentralen Server**, keine Registrierung und
keine App. Alles läuft über die eine Sache, die du sowieso schon hast: **deinen
Spielstand als JSON.**

> **Kurz gesagt:** Dein `!save`-JSON *ist* dein Charakter. Solange du es hast,
> kannst du überall mitspielen — und du verlierst es nie.

---

## Die Grundidee

ZEITRISS speichert deinen kompletten Fortschritt in einem portablen
JSON-Block. Dieser Block ist gleichzeitig dein Charakterbogen, dein
Kampagnenstand und dein Eintrittsticket in jede Runde. Daraus ergibt sich ein
**„MMO-Feeling ohne Server":**

- Du levelst **solo** auf deiner Lieblingsplattform, wann und wie du willst.
- Wenn du Lust auf gemeinsames Spiel hast, **triffst du dich mit anderen** (z. B.
  auf einem Discord-Server) und bietest deinen Stand an.
- Ihr spielt zusammen einen Abschnitt — danach geht jeder mit seinem
  aktualisierten JSON wieder seiner Wege oder ihr macht weiter.

Der Clou: Es ist völlig egal, auf welcher Plattform jemand sonst spielt. Das
JSON ist universell.

---

## 1. Solo zuerst — dein Charakter wächst bei dir

Richte dir ZEITRISS auf **deiner** Plattform ein (OpenWebUI, oder wo auch immer
du eine LLM-Runde mit Projektwissen laufen lässt). Spiel dich ein, mach ein paar
Missionen, finde deinen Charakter. Dein Fortschritt lebt in deinem JSON — du
bist niemandem Rechenschaft schuldig und an keine Runde gebunden.

Erst wenn du **Lust auf gemeinsames Spiel** hast, wird der Rest hier relevant.

Wie viel gemeinsames Spiel dazukommt, ist völlig offen — ZEITRISS ist bewusst
vielfältig spielbar, es gibt keinen „Normalfall". **Solo mit deinem NPC-Team
ist für sich genommen schon die vollständige MMO-Simulation** — ein ganzes
Team, eine ganze Kampagne, nur du. Von da aus geht vieles:

- Manche bleiben fast durchgehend solo und holen sich echte Mitspieler nur
  gezielt zu großen Momenten dazu — **zu** einem Boss, **zu** einem Rift — und
  spielen danach wieder allein weiter.
- Andere spielen umgekehrt fast alles online in der Gruppe, Abschnitt für
  Abschnitt, laden immer gemeinsam und wickeln HQ jedes Mal automatisch ab
  (siehe Abschnitt 5a). Erst **nach einer ganzen Episode** nehmen sie sich Zeit
  für sich allein: laden ihren Charakter solo, machen in Ruhe Feintuning im HQ
  und stecken das verdiente Geld z. B. in Chronopolis.

Beides ist gleich richtig. Koop ist kein Zwang und kein Dauerzustand, sondern
ein Andock-Punkt, den du dir nimmst, wann und so oft er dir passt.

---

## 2. Wo man sich trifft

Es gibt keinen offiziellen Treffpunkt — und das ist Absicht. In der Praxis
bilden sich **private Discord-Server** als Anlaufstellen: dort hängen Spieler ab,
posten ihren Stand und verabreden sich für Runden. Jede Community organisiert
sich, wie sie will.

Ein Discord-Server ist nur *ein* Weg. Genauso gut geht ein Gruppenchat, ein
Forum oder direkt der Messenger mit einem Kumpel (siehe
[Ganz ohne Discord](#ganz-ohne-discord)).

---

## 3. Deinen Stand anbieten

Willst du eine Runde anbieten oder in eine einsteigen, postest du deinen
**`!save`-JSON-Block** — und zwar **gleich von Anfang an**, nicht erst wenn
sich eine Gruppe gebildet hat. Das JSON ist der kanonische Weg: Episode,
Mission, Modus, Epoche, offene Rifts, Chronopolis-Stand — alles drin, für
alle im Treffpunkt sichtbar und lesbar.

Dazu passt optional ein schneller Teaser als menschenlesbare Kurzfassung.
Frei formuliert oder mit den Kurzbits aus `!bogen`. Zum Beispiel:

```
Core-Op · Episode 3 · Mission 5 (Mini-Boss in Sicht) · Epoche: Kalter Krieg
Level 6 · suche 2–3 Leute · Modus: tell
```

Oder für einen Rift-Lauf:

```
Rift-Op · Episoden-Boss-Run in Aussicht · 1 offener Rift · Level 9
suche 1–2 Leute · Modus: strict
```

Und ganz ehrlich: Zeig ruhig, was du hast. Ein harter Rift, ein Level, auf
das du stolz bist, ein Charakter mit Geschichte — **posten ist ausdrücklich
auch zum Angeben da.** Du gibst dabei nichts von dir preis, was dir schadet
(siehe [Du verlierst nie etwas](#8-du-verlierst-nie-etwas), unten).

> **Für Neugierige:** Ein gepostetes JSON kann man kurz in einen JSON-Viewer
> (oder einfach den Browser) werfen und nachsehen, was jemand für ein Szenario
> mitbringt — offene Rifts, spannende Epoche, ein Boss in Aussicht. So findest
> du Runden, die dich reizen, und steigst gezielt ein.

---

## 4. Zusammenkommen — die Lobby

Startet ihr als komplett neue Gruppe ohne bestehende Saves, kommt davor noch
ein Schritt: Jede Figur wird zuerst **einzeln in einem eigenen, frischen
Chat** erschaffen. Erst wenn alle Chargen-JSONs fertig sind, bringt ihr sie
gemeinsam in den einen neuen Spielchat — genau wie unten beschrieben.
Mehrere Charaktere gleichzeitig in einem Chat zu erstellen erzeugt Drift
zwischen den Figuren; darum bleibt jede Chargen ihr eigener, abgeschlossener
Chat-Abschnitt, bevor die Runde zusammenkommt.

Wenn die Runde steht, läuft das Zusammenkommen so:

1. **Alle posten ihr `!save`-JSON** in den Chat.
2. Ein Spieler übernimmt als **Leader** — er teilt seinen Bildschirm und führt
   die eigentliche ZEITRISS-Session in seinem Chat.
3. Der Leader fügt **zuerst seinen eigenen Save** ein und wartet die Antwort
   der Spielleitung ab — **der zuerst eingefügte Save setzt den
   Session-Anker** (Episode, Mission, Standort). Danach kommen die Gäste
   **einzeln nacheinander**: ein JSON einfügen, kurz die Reaktion der
   Spielleitung abwarten, dann der nächste. So bekommt jede Figur beim Eintreten
   ihren eigenen sauberen Moment, und die Runde versammelt sich Stück für Stück
   statt in einem Schwung — das läuft für die KI-Spielleitung deutlich sauberer,
   als alle Saves auf einmal hineinzukippen. Die eigenen Kampagnen der Gäste
   **pausieren** so lange und gehen nicht verloren.

Ab hier spielt ihr gemeinsam in **einem** Chat, den alle mitlesen können.

---

## 5. Spielen — strict oder tell

Bevor es losgeht, einigt sich die Runde auf einen von zwei Umgangsstilen. Das
ist eine **Absprache unter Spielern**, kein Spielbefehl — der Leader setzt sie am
Bildschirm um.

- **strict:** Jeder postet ohne weitere Absprache in den Chat, **was seine Figur
  in dieser Runde tut**. Der Leader übernimmt die Aktionen direkt. Schnell,
  chaotisch, näher am „jeder für sich".
- **tell:** Die Runde **bespricht jede Aktion** (jede „Row") gemeinsam. Der
  Leader interpretiert die Absprache und gibt sie ein. Langsamer, taktischer,
  näher am klassischen Pen-&-Paper-Tisch.

Alle sehen den Chat mit, also den kompletten Spielverlauf. Der Leader ist dabei
nur die **Hand an der Tastatur** — die Spielleitung macht die KI.

> **Aufteilen mitten in der Szene** (einer klopft vorne an, zwei schleichen
> hinten rein) ist **kein** technischer Split — das erzählt die KI-Spielleitung
> einfach parallel, im selben Chat. Ein echter Split mit getrennten Saves
> passiert nur an Abschnittsgrenzen.

---

## 5a. Vor einem Boss: kurz jeder für sich

Ein Muster, das sich für Online-Gruppen anbieten dürfte: Ihr spielt gemeinsam
Action-Abschnitt für Action-Abschnitt durch — und **kurz vor einem Boss**
(Mini-Boss um Mission 5, Episoden-Boss um Mission 10) geht noch einmal **jede
Figur für sich allein** zurück in ihren eigenen Chat, um sich vorzubereiten und
nachzujustieren: Equip, Klinik, Werkstatt, das Feintuning eben. Ein grobes
Zeitlimit von etwa 15 Minuten hält das knapp. Danach trefft ihr euch wieder in
**einem** Chat — auf dem Stand des Leaders, der zuletzt gespeichert hat — und
geht den Boss gemeinsam an.

Der Kern: Das Vorbereiten vor einem Boss ist ruhige Einzelarbeit, die niemanden
am Tisch aufhält; der Boss selbst ist der gemeinsame große Moment. Deshalb
splittet man dafür kurz auf und kommt geschlossen wieder zusammen. Das ist etwas
anderes als eine **ausgiebige gemeinsame HQ-Runde** — die ist ein eigener,
vollwertiger Spielabschnitt für sich (siehe Abschnitt 5b), kein schneller
Vor-Boss-Halt.

*(Das ist eine Idee zur Selbstorganisation, kein Spielbefehl — noch spielt
niemand real genug, um zu wissen, ob sich das so einspielt.)*

Und wer lieber zügig durchspielt, braucht diese Einzel-Vorbereitung gar nicht:
**Schnell-HQ** und **Auto-HQ** wickeln die HQ-Phase knapp und automatisch ab
(siehe [Spieler-Handbuch](../core/spieler-handbuch.md)), sodass die Gruppe
flüssig von Abschnitt zu Abschnitt weiterrattern kann, ohne stehen zu bleiben —
der Charakter bleibt trotzdem auf aktuellem Stand, und bei Bedarf lässt sich
noch per Pipe-Post etwas ins Briefing nachliefern. Beide Wege sind
gleichwertig.

---

## 5b. Das HQ ist ein eigener Schauplatz

Das HQ ist nicht bloß ein Speicherpunkt oder eine Werkstatt zwischen zwei
Missionen — **HQ erkunden** ist ein vollwertiger Spielabschnitt für sich: die
Nullzeitbar, der Club, das persönliche Quartier, das Archiv, dazu Klinik,
Werkstatt und die NPC-Crew. Ein ganzer Schauplatz zum Bespielen, ganz ohne
Chronopolis.

Darum kann eine Gruppe sich auch bewusst eine **ausgiebige gemeinsame
HQ-Runde** nehmen — anders als die schnelle Vor-Boss-Vorbereitung geht es hier
nicht ums Aufrüsten, sondern ums Miteinander: in der Nullzeitbar abhängen und
reden, sich gegenseitig ins persönliche Quartier einladen, im Archiv einem
Gerücht nachgehen, ein Verhör gemeinsam führen oder einfach die Chrononauten —
und einander — näher kennenlernen. So etwas passt gut **nach einer
abgeschlossenen Episode**, wenn Luft für Rollenspiel ist.

*(Auch das ist kein Muss: Manche Runden lieben diese ruhigen, dichten
HQ-Abende, andere rattern per Auto-HQ weiter zum nächsten Action-Abschnitt.
Beides ist ZEITRISS — das HQ trägt vom schnellen Boxenstopp bis zum ganzen
Rollenspiel-Abend alles.)*

---

## 6. Aufstieg in der Gruppe

Nach einer Mission kommt der Debrief mit Score und Level-Up. **Wichtig:** Der
Level-Up wird **vor** dem Speichern vergeben — das ist so gewollt und bleibt so
(ein Save ohne erledigten Aufstieg ist unvollständig).

Im fremd-geleiteten Multiplayer passiert dieser Aufstieg **live und sichtbar
vor der ganzen Runde**, am geteilten Bildschirm des Leaders. Das ist kein
Umweg, sondern ein **eingebautes Vertrauens-Feature**: Weil jede Figur ihre
**eine** Aufstiegswahl (`+1 Attribut` **oder** `Talent/Upgrade` **oder** `+1
SYS`) live vor Zeugen trifft, sieht die ganze Runde mit, dass alle
Charaktere regelkonform bleiben — niemand bläst still im Hintergrund Werte
auf. Verifikation durch mehrere Augen, ganz nebenbei.

- Im **tell**-Modus sagst du dem Leader deine Wahl als eine Zeile im Chat.
- Im **strict**-Modus postest du sie direkt.

Die Abrechnung (CU, XP, Level) siehst du im Debrief **bevor** du wählst. Dann
speichert der Leader — und dein aktualisierter Stand ist wieder in deinem
JSON.

---

## 7. Abschnitt beenden

Am Ende eines Abschnitts:

1. Der Leader **speichert** (`!save` im HQ) — die Spielleitung gibt **pro
   anwesender Figur einen eigenen vollständigen JSON-Block** aus.
2. Der Leader **wirft die JSONs zurück** in den Chat, jeder nimmt seinen.
3. Ihr entscheidet frei: **weiterspielen** (nächster Abschnitt, gleicher Leader
   oder neuer) oder **Wege trennen** — jeder zieht mit seinem frischen JSON
   weiter, solo oder in eine andere Runde.

Persönliche Fortschritte und Erinnerungen reisen mit. Fremde Kampagnenstände,
Auszahlungen und einzigartige Beute werden **nicht** kopiert — jeder behält
sauber seinen eigenen Stand.

---

## 8. Du verlierst nie etwas

Das ist der Kern, der das Ganze entspannt macht:

- **Dein JSON gehört dir.** Es zu posten gibt nichts von dir preis, was dir
  schadet — es ist eine Kopie, das Original bleibt bei dir.
- **Eine Gruppe zerbricht mitten im Spiel?** Kein Drama. Du hast dein letztes
  gespeichertes JSON. Nimm es und such dir eine neue Runde — oder spiel solo
  weiter.
- **Der Leader ist weg?** Dein Stand ist trotzdem sicher, sobald zuletzt
  gespeichert wurde. Deshalb speichert man an Abschnittsgrenzen.

Es gibt keinen Account, der gesperrt werden kann, und keinen Server, der
abstürzt. Solange du dein JSON hast, bist du im Spiel.

---

## Ganz ohne Discord

Der gleiche Ablauf funktioniert überall:

- **Am Tisch:** Ein Gerät, einer leitet, ihr sprecht per Voice oder direkt im
  Raum. JSONs schickt ihr euch schnell per Messenger auf das eine Gerät.
- **Zu zweit, spontan:** Du und ein Kumpel schickt euch die JSONs per Messenger,
  spielt eine Runde auf einem Gerät, danach das aktualisierte JSON zurück. Jeder
  geht nach Hause — auch im Spiel trennen sich die Wege wieder.

Die Mechanik ist immer dieselbe: **Save posten → zusammen spielen → Save
zurück.**

---

## Mehr dazu

Die Spielmechanik hinter dem Gruppenspiel (getrennte Saves, Session-Anker,
Splits & Merges, Gruppen-Px, Tod in der Gruppe) steht im
[Spieler-Handbuch](../core/spieler-handbuch.md) unter „MMO-Feeling ohne Server"
und „Der Gameflow".
