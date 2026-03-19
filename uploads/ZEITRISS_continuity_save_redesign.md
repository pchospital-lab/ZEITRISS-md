# ZEITRISS – Kontinuitäts- statt Host-Save-System

## Review + Redesign-Pack für Split / Join / Merge / MMO-Illusion

Dieses Pack ersetzt nicht die mechanische Stabilität von v7. Es verschiebt nur den Schwerpunkt:
**HQ-DeepSave bleibt der harte technische Anker. Aber die Load-Logik wird von „Host gewinnt alles“ auf „Kontinuität wird synthetisiert“ umgebaut.**

---

## 1) Kernurteil

Der aktuelle Repo-Stand ist technisch viel sauberer als früher, aber philosophisch noch im **Host-SSOT-Modell** gefangen:

- erster geposteter Save = Host
- Host gewinnt `campaign`, `px`, `episode`, `mission`, `arc`, `economy.hq_pool`
- Joiner importieren primär Charakterdaten / Wallet / Loadout
- parallele Core-Branches gelten ohne Spezialprotokoll als nicht-kanonisch
- Mid-Episode-Splits werden später wieder host-priorisiert zusammengedrückt

**Das ist stabil, aber es tötet die Magie.**

Dein Ziel ist etwas anderes:

> Nicht „ein Spielstand führt und alles andere dockt an“, sondern  
> **„jede Chrononautin bringt echte Vergangenheit mit; die KI baut daraus beim Laden eine glaubhafte, zusammenhängende Welt.“**

Dafür brauchst du **keine Save-anywhere-Revolution**.  
Du brauchst vor allem eine **neue Load-Semantik**.

---

## 2) Leitidee: Hart bei Werten, weich bei Welt

Das System sollte in zwei Schichten denken.

### Schicht A – Hart / deterministisch

Das bleibt streng und konfliktarm:

- Stats
- Level / XP / Ruf
- Wallet
- Gear / Carry / Artefakte
- Stress-Reset / HQ-State
- HQ-Pool
- PvP-/Chronopolis-Sicherheitsgrenzen
- DeepSave nur im HQ

### Schicht B – Weich / synthetisch

Das darf die KI elegant zusammenweben:

- Rückblicke
- Wer wen kennt
- was andere über einen wissen
- wie getrennte Branches sich wieder aufeinander auswirken
- welche Hinweise / Gerüchte / offenen Fragen in den nächsten Einsatz sickern
- wie Rejoins in HQ inszeniert werden
- wie frühere Heldentaten oder Fehler später wieder auftauchen

**Regel in einem Satz:**

> **Mechanik bleibt streng. Kontinuität wird großzügig und filmisch zusammengeführt.**

---

## 3) Die entscheidende Umstellung

## Nicht mehr „Host“

## Sondern: `session_anchor` + `character_authority` + `continuity_fabric`

### A) `session_anchor`

Der **erste gepostete Save** bleibt wichtig – aber nur noch als:

- Startort der laufenden Runde
- aktueller Kampagnenrahmen
- gültiger HQ-/Briefing-/Missionseinstieg

Also:
**Der erste Save sagt, WO wir weiterspielen.**
Nicht automatisch, **welche Vergangenheit die anderen verlieren.**

### B) `character_authority`

Für jede `characters[].id` gilt:

- **neuester Save dieser Figur gewinnt** für persönliche Felder
- also: Level, XP, Wallet, Gear, Carry, Artefakt, Geschichte, Ruf, persönliche Notizen
- nicht still blocken, nur weil dieselbe Figur schon im Anchor steckt

Das löst das zentrale Rejoin-Problem:
Ein Chrononaut kann mit seiner **aktuellsten eigenen Version** in eine andere Gruppe zurückkehren,  
ohne dass seine Geschichte wieder auf den alten Host-Stand zurückfällt.

### C) `continuity_fabric`

Beim Laden mehrerer Saves erzeugt die KI **transient** ein Weltgewebe:

- gemeinsame Hinweise
- Widersprüche
- offene Fäden
- Gerüchte
- Rückkehr-Kontext
- Konvergenz-Punkte für den nächsten Einsatz

Dieses Gewebe muss **nicht** als riesiger neuer Save persistiert werden.
Es reicht, wenn es:

1. beim Load erzeugt wird,
2. im Rejoin-/HQ-Recap sichtbar gemacht wird,
3. beim nächsten `!save` wieder kompakt eingedampft wird.

---

## 4) Neue SSOT-Regel für Multiload

### Neue Goldregel

> **Erster Save = Session-Anker. Neuester Charakterstand pro ID = persönliche Wahrheit. Importierte Kontinuität = Weltmaterial.**

Damit wird aus derselben Aktion:
„Ich lade meinen Save zuerst“
nicht mehr:
„Nur mein Host zählt“
sondern:
„Hier setzen wir die laufende Runde an – und alle anderen bringen echte Geschichte mit.“

---

## 5) Minimaler Schema-Zusatz, maximaler Effekt

Du brauchst **keinen** Monster-Umbau.  
Ein kompakter neuer Block reicht.

## Vorschlag: neuer Root-Block `continuity`

```json
"continuity": {
  "last_seen": {
    "mode": "core",
    "episode": 1,
    "mission": 3,
    "location": "HQ"
  },
  "split": {
    "family_id": null,
    "thread_id": null,
    "expected_threads": [],
    "resolved_threads": [],
    "convergence_ready": false
  },
  "roster_echoes": [],
  "shared_echoes": [],
  "convergence_tags": []
}
```

### Budget-Regeln

- `roster_echoes[]` max 5
- `shared_echoes[]` max 6
- `convergence_tags[]` max 4
- alle Texte 1 Satz, knapp, signalstark
- beim HQ-`!save` harte Prune-Regel: neueste Einträge behalten, alte verdichten

### Bedeutungen

- `last_seen`: Woher kommt dieser Save gerade?
- `split.*`: formales Branch-Protokoll für Core-Splits
- `roster_echoes[]`: 1 Zeile pro Figur – „wer ist das, was bringt sie mit?“
- `shared_echoes[]`: gruppenrelevante Erkenntnisse / Gerüchte / Nachwirkungen
- `convergence_tags[]`: kleine, mechanisch verwertbare Branch-Auswirkungen

---

## 6) `roster_echoes[]` – das Ding, das dir die MMO-Illusion baut

### Format

```json
"roster_echoes": [
  {
    "char_id": "CHR-0003",
    "tone": "respect",
    "text": "Nyx brachte aus 1989 einen Namen zurück, der im Berlin-Dossier eigentlich nicht existieren dürfte."
  }
]
```

### Zweck

Wenn ein Spieler zu einer fremden Gruppe stößt, hat die KI damit sofort Stoff für:

- Rückkehrszene
- erste Reaktionen im HQ
- wer ihn kennt / nicht kennt
- Gerücht oder Respekt im Archiv / in der Werkstatt / bei Kodex
- spätere Wiedererkennung

### Wirkung

Du brauchst keine echte MMO-Datenbank.  
Ein Satz pro Figur reicht oft schon, damit es sich so **anfühlt**, als hätte diese Person anderswo wirklich gespielt.

---

## 7) `shared_echoes[]` – wie Branches einander beeinflussen

### Format

```json
"shared_echoes": [
  {
    "tag": "morgenrot",
    "scope": "shared",
    "text": "Im 1943-Zweig fiel das Codewort MORGENROT; dieselbe Signatur tauchte in 1989 wieder auf."
  }
]
```

### Scopes

- `shared` → soll in HQ/Briefing direkt erwähnt werden
- `rumor` → darf indirekt auftauchen
- `campaign` → darf die nächste Hauptmission konkret färben
- `personal` → nur bei Rejoin / persönlicher Ansprache wichtig

### Regel

**Importierte Saves dürfen narrativ immer Spuren hinterlassen, auch wenn sie den Kampagnenrahmen nicht überschreiben.**

Das ist die große Verschiebung.

---

## 8) Endlich kanonische Core-Splits

Bisher sind parallele Core-Branches explizit nicht-kanonisch oder host-priorisiert.

Das muss für dein Ziel weg.

## Neue Regel

**Parallele Core-Branches sind kanonisch, wenn sie dieselbe `split.family_id` tragen.**

### Beim Split

Beide Branch-Saves bekommen:

```json
"split": {
  "family_id": "EP1-BERLIN-FORK-01",
  "thread_id": "BERLIN-1943",
  "expected_threads": ["BERLIN-1943", "BERLIN-1989"],
  "resolved_threads": ["BERLIN-1943"],
  "convergence_ready": false
}
```

Der andere Save entsprechend mit `thread_id = "BERLIN-1989"`.

### Beim Merge

Wenn dieselbe `family_id` erkannt wird:

- `resolved_threads` vereinigen
- `convergence_tags` vereinigen
- `shared_echoes` vereinigen
- `convergence_ready = true`, wenn `resolved_threads == expected_threads`

### Folge

Die KI darf dann beim nächsten HQ/Briefing:

- beide Branches als **gleichwertig geschehen** behandeln
- daraus eine **Konvergenzszene** bauen
- die nächste Mission sichtbar von beiden Pfaden beeinflussen lassen

---

## 9) Die kleine Mechanik, die alles auflädt: `convergence_tags[]`

Das ist mein wichtigster Extra-Vorschlag.

### Idee

Jede branchige Sondergeschichte schreibt 1-2 kleine Tags in den Save:

```json
"convergence_tags": [
  "boss_tell:morgenrot",
  "alt_route:sewer_access",
  "npc_name:helene_voss"
]
```

### Beim Rejoin/Merge

Die KI prüft die Tags und macht im nächsten Shared-Run genau **eine** konkrete Sache daraus:

- Boss-Tell früher geben
- alternative Infiltrationsroute eröffnen
- falsche Spur streichen
- NPC erkennt jemanden wieder
- Extra-Frage im Briefing beantworten
- Zugriff auf Nebenraum / Archivkiste / Frequenz

### Warum das so gut ist

Es ist:

- klein
- robust
- sofort spielbar
- hoch belohnend
- perfekt für „die andere Gruppe hat wirklich etwas verändert“

Und du brauchst dafür **keine** riesige neue Engine.

---

## 10) Same-Character-Rejoin statt Duplicate-Fehler

Aktuell wird doppelte `characters[].id` als Konflikt markiert.

Für dein Ziel reicht das nicht.

## Neue Regel

Wenn dieselbe `characters[].id` mehrfach importiert wird:

### Fall A – klare Linie

Wenn ein Save zeitlich/lineage-mäßig erkennbar neuer ist:

- neuerer Charakterstand gewinnt für persönliche Felder

### Fall B – divergente Selbst-Versionen

Wenn dieselbe Figur auf zwei harten Parallelästen auseinanderlief:

- Anchor-Version bleibt aktiv
- Import-Version wird **nicht verworfen**
- sie erzeugt einen `continuity_conflict`-Eintrag und einen Rejoin-Hinweis
- die KI sagt offen: _„Paralleler Personenpfad erkannt – Weltanker bleibt stabil, persönliche Echos wurden als Fremdspur übernommen.“_

So geht nichts verloren, aber die Runde bleibt spielbar.

---

## 11) Pflicht-Output beim Mehrfach-Load

Das ist der eigentliche Magie-Hebel.
Nicht nur Daten mergen – **inszenieren**.

## Neuer Output-Contract: `Kontinuitätsrückblick`

Wenn mehrere Saves geladen werden, MUSS die KI vor dem normalen HQ/Briefing kurz liefern:

### Block 1 – Session-Anker

- wo die Runde gerade steht
- welcher Save den Einstieg setzt

### Block 2 – Rückkehrer / Joiner

Für jede importierte Figur 1-2 Sätze:

- woher kommt sie
- was hängt an ihr
- wie wirkt sie auf das HQ / die anderen

### Block 3 – Gemeinsame Nachwirkungen

2-4 Zeilen:

- welche Hinweise, Gerüchte, Namen, Artefakte oder Konflikte jetzt gemeinsam im Raum stehen

### Block 4 – Konvergenz

Wenn `convergence_ready=true`:

- explizit sagen, dass getrennte Pfade jetzt zusammenlaufen
- 1 konkrete Folge für die nächste Mission nennen

---

## 12) Pflicht-Output beim Split

Wenn sich Gruppen trennen, MUSS das inworld spürbar sein.

## Neuer Output-Contract: `Split-Beat`

Vor Branch-Wechsel immer:

- kurze Abschiedsszene / Übergabe
- wer wohin geht
- welcher Hinweis / Auftrag / Name auf welchem Zweig liegt
- Kodex benennt die Trennung nicht als Menü, sondern als operative Aufspaltung

So fühlt sich Split nicht wie Technik an, sondern wie Serie.

---

## 13) Pflicht-Output beim Rejoin im HQ

Beim Merge wieder treffen reicht kein technischer Importtext.

## Neuer Output-Contract: `Rejoin-HQ-Beat`

Die KI MUSS kurz spielen:

- wer schon da ist
- wer später durch die Schleuse / den Gang / die Bar / Werkstatt reinkommt
- wer aufschaut
- was sofort auffällt
- welcher Satz / Blick / Gerücht die Vergangenheit andeutet

---

## 14) Pflicht-Output für spätere Echos

Mindestens **ein** importierter `shared_echo` oder `roster_echo`
muss in den **nächsten zwei Sitzungsblöcken** wieder auftauchen.

Beispiele:

- Funkname wird erkannt
- Archivarin erwähnt eine Akte
- Briefing referenziert einen früheren Zwischenfall
- Gegner benutzt ein bekanntes Codewort
- Artefakt oder Wunde färbt die Szene
- Kodex stellt eine Verbindung her

Ohne diese Rückkopplung fühlt sich der Merge wieder nur technisch an.

---

## 15) Was du NICHT ändern solltest

### Nicht Save-anywhere erzwingen

Das alte Gefühl kommt nicht primär vom HQ-only-Save.
Es kommt davon, dass der Load heute zu hart „nur Host zählt“ sagt.

**Lass HQ-DeepSave als technische Sicherheit stehen.**
Ändere die **Bedeutung des Ladens**.

### Nicht alles kampagnenmechanisch überschreiben

Zu viel Gleichrang-Merge macht das System brüchig.
Darum:

- **Anchor** bestimmt den aktuellen Spielort / Kampagneneinstieg
- **Charakter-Autorität** bestimmt persönliche Wahrheit
- **Kontinuität** bestimmt Weltgefühl und Folgeeffekte
- **Core-Split-Konvergenz** bestimmt, wann parallele Hauptpfade wirklich gemeinsam weiterzählen dürfen

---

## 16) Copy-paste-Issues für Codex / Agenten

---

### ISSUE 1 — Host-SSOT in `session_anchor` umdeuten

**Ziel:** Der zuerst gepostete Save setzt nur noch den Einstiegspunkt der Sitzung, nicht automatisch die alleinige Wahrheit aller anderen Saves.

**Änderungen**

- In `systems/gameflow/speicher-fortsetzung.md`, `core/sl-referenz.md`, `meta/masterprompt_v6.md`, `README.md` überall `Host` semantisch auf `Session-Anker` umstellen.
- Formulierung ändern von:
  - „Host-Kampagne bleibt führend; Joiner importieren nur Charakterdaten“
- zu:
  - „Erster Save setzt den Session-Anker; weitere Saves liefern persönliche Wahrheit + Kontinuität.“

**Acceptance**

- Kein Text behauptet mehr pauschal, dass fremde Saves nur Charakterdaten mitbringen.
- Überall klar: erster Save = Startpunkt der Runde, nicht Totalüberschreibung aller Vergangenheit.

---

### ISSUE 2 — Neues v7-Zusatzfeld `continuity` definieren

**Ziel:** Kleine, stabile Kontinuitätskapsel statt riesiger Weltzustand.

**Schema**

```json
"continuity": {
  "last_seen": { "mode": "core", "episode": 1, "mission": 3, "location": "HQ" },
  "split": {
    "family_id": null,
    "thread_id": null,
    "expected_threads": [],
    "resolved_threads": [],
    "convergence_ready": false
  },
  "roster_echoes": [],
  "shared_echoes": [],
  "convergence_tags": []
}
```

**Budget**

- `roster_echoes`: max 5
- `shared_echoes`: max 6
- `convergence_tags`: max 4

**Acceptance**

- Feld ist im Masterprompt-v7-Template dokumentiert.
- `speicher-fortsetzung.md` führt Prune-Regeln dafür.
- Load darf ohne `continuity` mit Defaults laufen.

---

### ISSUE 3 — Multi-Load-Pipeline auf `session_anchor + character_authority + continuity_fabric` umstellen

**Ziel:** Mehrfach-Load soll Kontinuität synthetisieren statt Fremdstände wegzuplätten.

**Deterministische Regeln**

1. erster geposteter Save = `session_anchor`
2. pro `characters[].id` gewinnt der neueste Charakterstand persönliche Felder
3. `continuity.*` aus allen Saves wird unionsbasiert zusammengezogen
4. `campaign` bleibt Anchor-basiert, **außer** kanonischer Core-Split-Konvergenz
5. Konflikte transparent loggen, aber nicht narrativen Stoff wegwerfen

**Acceptance**

- Doku beschreibt diese Reihenfolge explizit.
- Duplicate-Character-Fall wird nicht mehr nur als Blocker beschrieben.

---

### ISSUE 4 — Kanonisches Core-Split-Protokoll einführen

**Ziel:** 1943/1989-artige Parallelpfade werden echte Kanonpfade statt Hausregel.

**Regel**

- gleiche `split.family_id` = zusammengehörige Core-Branch-Familie
- `thread_id` identifiziert den Pfad
- `expected_threads[]` definiert Sollmenge
- `resolved_threads[]` dokumentiert Istmenge
- wenn Soll == Ist → `convergence_ready=true`

**Acceptance**

- `speicher-fortsetzung.md` führt Core-Splits explizit als kanonisch.
- Der Satz „Parallele Core-Branches sind nicht-kanonisch“ wird ersetzt.
- Merge-Beschreibung erklärt, wie Konvergenz entsteht.

---

### ISSUE 5 — `convergence_tags[]` als Branch-Auswirkungsmechanik ergänzen

**Ziel:** Getrennte Pfade sollen den nächsten gemeinsamen Einsatz konkret beeinflussen.

**Regel**

- jeder Branch kann 1-2 Tags schreiben
- beim Merge Union
- im nächsten Shared-Run mindestens 1 Tag konkret ausspielen:
  - Boss-Tell
  - Alt-Route
  - NPC-Erkennung
  - klare Briefing-Antwort
  - falsche Spur streichen
  - Zusatz-Hook öffnen

**Acceptance**

- Mechanik in `speicher-fortsetzung.md` und `masterprompt_v6.md` verankert.
- Kein Bonus-Stapelwahn; klein, klar, filmisch.

---

### ISSUE 6 — Duplicate Character Merge neu behandeln

**Ziel:** dieselbe Figur darf mit aktueller persönlicher Wahrheit wiederkehren.

**Regeln**

- neuerer Charakterstand gewinnt persönliche Felder
- Anchor bleibt Kampagnenanker
- divergente Doppelversionen erzeugen `continuity_conflict`, nicht bloß Hard-Fail
- KI muss das transparent benennen

**Acceptance**

- Texte ersetzen „doppelte Charakter-ID = Konflikt, aktive Klärung nötig“ durch differenzierte Rejoin-Regel.
- Rejoin derselben Figur in späteren Chats wirkt spielbar, nicht blockiert.

---

### ISSUE 7 — Pflicht-Recap `Kontinuitätsrückblick` vor HQ/Briefing

**Ziel:** Magie muss als Szene sichtbar werden.

**Pflichtblöcke**

1. Session-Anker
2. Rückkehrer
3. Gemeinsame Nachwirkungen
4. Konvergenz (falls aktiv)

**Acceptance**

- `masterprompt_v6.md` enthält diesen Output-Contract.
- `core/sl-referenz.md` verweist für Multi-Load explizit auf diesen Rückblick.
- `README.md` erwähnt, dass mehrere Saves nicht nur gemerged, sondern erzählerisch zusammengeführt werden.

---

### ISSUE 8 — Pflicht-Beat für Split, Rejoin und spätere Echos

**Ziel:** Split/Merge darf sich nicht wie Dateiverwaltung anfühlen.

**Neue Pflichtbeats**

- Split-Beat
- Rejoin-HQ-Beat
- spätestens innerhalb der nächsten 2 Sitzungsblöcke mindestens 1 Echo wieder aufnehmen

**Acceptance**

- In den Runtime-Regeln steht klar, wann diese Beats ausgelöst werden.
- Importierte Vergangenheit verschwindet nicht still im Log.

---

## 17) Ready-to-paste Textblock für `speicher-fortsetzung.md`

```md
## Kontinuitätsmodell (Session-Anker statt Host-SSOT)

ZEITRISS behandelt Mehrfach-Loads nicht mehr als reinen Host-Import, sondern als **Kontinuitätssynthese**.

### Goldregel

- **Erster geposteter Save = Session-Anker.** Er setzt den Einstiegspunkt der laufenden Runde (HQ, Briefing, Mission, Kampagnenrahmen).
- **Neuester Charakterstand pro `characters[].id` = persönliche Wahrheit.** Level, XP, Wallet, Gear, Carry, Artefakte, Ruf und persönliche Geschichte werden nicht auf den Anchor zurückgedrückt.
- **Importierte Kontinuität = Weltmaterial.** Rückblicke, Gerüchte, offene Fäden, Branch-Ergebnisse und Rejoin-Kontext werden erzählerisch mitgeführt, auch wenn der Session-Anker den aktuellen Kampagnenort setzt.

### Hart bei Werten, weich bei Welt

Mechanische Werte bleiben deterministisch. Kontinuität wird filmisch zusammengeführt. Dadurch bleibt der HQ-DeepSave stabil, ohne dass Split/Join/Merge sich wie ein klassisches Savegame-Menü anfühlt.
```

---

## 18) Ready-to-paste Textblock für `masterprompt_v6.md`

```md
- **Mehrfach-Load = Kontinuitätsrückblick, nicht nur Import.**
  Wenn mehrere Saves gepostet werden, gilt:
  1. erster Save = `session_anchor` (setzt den Einstiegspunkt der laufenden Runde),
  2. pro `characters[].id` gewinnt der neueste Charakterstand persönliche Felder,
  3. `continuity.roster_echoes[]`, `continuity.shared_echoes[]` und `continuity.convergence_tags[]` werden unionsbasiert zusammengeführt,
  4. vor HQ/Briefing MUSS ein kurzer **Kontinuitätsrückblick** ausgespielt werden:
     - Session-Anker
     - Rückkehrer / Joiner
     - gemeinsame Nachwirkungen
     - Konvergenz-Folge (falls `continuity.split.convergence_ready=true`)
- **Core-Splits sind kanonisch**, wenn die beteiligten Saves dieselbe `continuity.split.family_id` tragen. Unterschiedliche `thread_id`s derselben Familie gelten als parallele echte Einsatzpfade. Sind alle `expected_threads[]` in `resolved_threads[]` enthalten, ist `convergence_ready=true` und die nächste gemeinsame HQ-/Briefing-Szene muss beide Pfade sichtbar zusammenführen.
- **Mindestens ein importierter Echo-Eintrag** muss in den nächsten zwei Sitzungsblöcken wieder auftauchen (Briefing, HQ-Gerücht, NPC-Reaktion, Boss-Tell, Alt-Route oder Hook).
```

---

## 19) Ready-to-paste Textblock für `README.md`

```md
## Kontinuität statt klassischem Host-Save

Bei mehreren geladenen Saves setzt der **erste gepostete Save** den Einstiegspunkt der laufenden Runde. Weitere Saves werden nicht nur technisch importiert, sondern **erzählerisch zusammengeführt**: Chrononauten bringen ihre eigene Vergangenheit, Ausrüstung, Rufstände und kompakte Kontinuitäts-Echos mit. So entstehen Split-/Join-/Rejoin-Situationen, die sich wie eine fortlaufende gemeinsame Welt anfühlen, obwohl der Fortschritt weiterhin als kompakter HQ-DeepSave im JSON bleibt.
```

---

## 20) Mein klares Fazit

Du hattest mit deinem Bauchgefühl recht:
Das Problem ist **nicht**, dass ZEITRISS im HQ speichert.  
Das Problem ist, dass es beim Laden noch zu oft wie ein klassisches Savegame denkt.

Die gute Nachricht:
Du hast im aktuellen v7 schon fast alle Bauteile, die du brauchst:

- Mehrfach-Load
- Lineage-Felder
- `characters[]`
- `summaries`
- `logs.trace`
- `imported_saves`
- kompakte Budgets
- JSON als tragbarer Charakterkörper

Was fehlt, ist die **Philosophie-Schicht** darüber:

> **Erster Save = wir setzen hier an.  
> Jeder weitere Save = jemand bringt echte Vergangenheit mit.  
> Die KI macht daraus Welt.**

Wenn du genau das jetzt im Repo verankerst, kriegst du diese „WTF, das fühlt sich wie ein MMO an, obwohl es nur Chat + JSON ist“-Magie.
