# ZEITRISS – Kausalabfang / "Never happened"-Pack

## Kurzurteil

**Ja, das lässt sich sauber einbauen.**
Aber nur dann, wenn es **kein Zeitzauber**, **kein Respawn**, **kein universelles Retcon-Werkzeug** und **kein Kampf-Siegknopf** wird.

Der saubere Platz im System ist:

- **nicht** als neue Hauptmechanik,
- **nicht** als frei formulierbares Plot-Werkzeug,
- sondern als **stark begrenztes ITI-Cleanup-Protokoll für 0-LP-Hostiles**.

Dann passt es:

- zum harten Agenten-Thriller,
- zum „wir sind die Zeitpolizei“-Selbstbild,
- zur Loot/Cleanup/Exfil-Struktur,
- zur Kodex-Logik,
- zur Mandela-/Restlinien-Idee,
- und zur KI-Leitbarkeit.

---

## SSOT-Idee

**Offizieller ITI-Name:** `Kausalabfang-Marker`  
**Feldslang:** `"Never happened"`

### Inworld-Logik in einem Satz

Der Kausalabfang-Marker **macht niemanden magisch ungeschehen**, sondern markiert einen **eindeutig identifizierten, bereits kampfunfähigen feindlichen Eindringling** für eine **eng begrenzte retrospektive Festnahme** durch ein ITI-Abfangteam kurz vor dem Einsatzkontakt.

### Wichtige Folge daraus

- Die **Person** wird aus dem lokalen Geschehen gezogen.
- Die **Welt** wird **nicht komplett zurückgedreht**.
- Deshalb bleiben **Kollateralschäden, Einschläge, kaputte Türen, Stress, verbrauchte Munition und bereits gesichertes Loot** bestehen.
- Nur **ungesicherte, personengebundene Spuren** (Körper, frische Blutschmiere direkt am Ziel, Ausweis am Körper, lose Ausrüstung am Ziel) dürfen beim Abgleich flackern und verschwinden.

Das ist wichtig, weil sonst Loot, Konsequenzen und Glaubwürdigkeit kaputtgehen.

---

## Warum das funktioniert

Der Marker ist die **Gegner-Spiegelung** zur bereits etablierten Chrononauten-Logik:

- **Verbündete/Chrononauten bei 0 LP** → Not-Rückholung / HQ-Rettung / kein billiger Gratis-Tod.
- **Feindliche 0-LP-Hostiles mit Zuständigkeit** → Kausalabfang / Festnahme statt Feldhinrichtung.

So wirkt das System symmetrisch und erwachsen, statt nach Sonderregel.

---

## Harte Leitplanken (MUSS)

### 1) Nur nach 0 LP

Der Marker ist **nie** ein Kampf- oder Alpha-Strike-Werkzeug.
Er greift **erst**, wenn das Ziel bereits bei **0 LP** ist und in der Szene als **kampfunfähig** gilt.

### 2) Nur auf kurze Distanz

Der Chrononaut muss auf **Armeslänge / Nahdistanz** heran, um eine **exakte Identitätsfassung** zu machen.
Keine Fernmarkierung, keine Drohnenmarkierung, kein Massentagging über Wände.

### 3) Nur mit eindeutiger Identität

Erforderlich sind mindestens sinngemäß:

- Gesichts-/Iris-Scan **oder**
- DNA-/Blut-/Gewebe-Lock **oder**
- eindeutige Kodex-Match-Verifikation.

Ohne sichere Identität: **kein Kausalabfang**.

### 4) Nur mit Kodex-Uplink

Ohne Kodex-Leitung / Relais / PZT-Verbindung **keine Freigabe**.
Offline kann das Gerät höchstens lokal markieren, aber **nicht** vollziehen.

### 5) Keine Rücknahme „zu weit davor"

Der ITI-Abfang erfolgt **nur im engen Zuständigkeitsfenster** vor dem Einsatzkontakt.
Faustregel:

- **Sekunden bis wenige Minuten**, nicht Tage/Wochen/Kindheit.
- Nur so weit, dass die **Tatmotivation und Einsatzlage noch dieselbe** bleiben.

Damit vermeidest du das „Dann hätte er sich halt ganz anders entschieden“-Loch.

### 6) Nicht auf Chrononauten

Funktioniert **nicht** auf ITI-agentengebundene Personen, Chrononauten, Bio-Sheaths mit Nullzeit-Anker, Squadmates oder spielbare Charaktere.

### 7) Nicht auf Boss-/Mini-Boss-Ziele als Standard

Boss-Gegner bleiben **lebendige Hochwert-Ziele** für Vorführung, Verhör, Verhandlung, Prozess, spätere Rückkehr.
Der Marker ist für **Cleanup**, nicht für das Wegbügeln narrativer Schlüsselfiguren.

### 8) Nicht auf Zivilisten / Zeugen / Schutzpersonen

Der Marker ist **kein Memory-Wipe-Tool** und **kein Missbrauchswerkzeug** gegen Unbeteiligte.

### 9) Nicht auf Para-Kreaturen / Rift-Wesen

Para-Wesen folgen weiterhin **Rift-Logik**: bannen, neutralisieren, brechen, schließen, binden.
Der Marker ist ein **ITI-Jurisdiktionswerkzeug für Personen**, kein Monster-Pokeball.

### 10) Kein Save- oder JSON-Ballast als Ausrüstungsobjekt

Das Gerät sollte **Standard-ITI-Ausrüstung** sein, **kein shopbares Einzelitem** und **kein Pflicht-Eintrag** in jeder Equipment-Liste.
Es reicht, die Nutzung über `logs.trace[]` / `logs.notes[]` oder bei wichtigen Fällen über Kontinuitäts-Echos mitzuschreiben.

---

## SOLL-Regeln für gutes Spielgefühl

### Loot zuerst, Marker danach

Die saubere Reihenfolge ist:

1. Gegner fällt auf 0 LP.
2. Konflikt kippt / Fenster öffnet sich.
3. **Loot / Beute** wird abgehandelt.
4. Danach optional / standardmäßig **Kausalabfang**.

### Was beim Flackern bleibt?

- **Bereits gesichertes Loot** bleibt.
- **Bereits getrennte Gegenstände** bleiben.
- **Laufende Konsequenzen** bleiben.
- **Nicht gesicherte personengebundene Spuren** dürfen aus der Szene glätten.

So bleibt das Ganze spielbar und paradoxiefest genug.

### Unnamed Mooks = automatisch, Named Targets = nachfragen

Für die KI-Leitbarkeit ist das Gold wert:

- **Namenlose, klar feindliche 0-LP-Hostiles:** KI darf das im Cleanup **automatisch** abwickeln.
- **Benannte / plotrelevante / moralisch ambige Ziele:** KI fragt **kurz** nach.

So entsteht Magie, ohne dass Named NPCs versehentlich weggefiltert werden.

### Niedrige TEMP = kurzer Recall-Blur, hohe TEMP = stabiler

Kleiner Flavor, kaum Mechanik:

- **TEMP 1–2:** kurzer Erinnerungsknick; Kodex muss die Festnahme trocken rückverankern.
- **TEMP 3–5:** kurzes Deja-vu, aber stabil.
- **TEMP 6+:** fast klares Erinnern trotz lokaler Korrektur.

Keine schwere Strafmechanik draus bauen.

---

## Dinge, die du NICHT tun solltest

- Kein „Der Gegner war nie geboren“.
- Kein „Damit kann man jeden Plotgegner löschen“.
- Kein „Damit kann man gescheiterte Szenen rückgängig machen“.
- Kein „Damit kann man Kameraden retten“.
- Kein „Damit kann man Leichenfledderei plus Voll-Loot plus völlige Spurfreiheit gratis bekommen“.
- Kein „Damit kann man Zeugen oder Zivilisten elegant wegmachen“.
- Kein „Damit kann man para-normale Rift-Wesen einsacken“.
- Kein „Damit kann man in Chronopolis die Gefahr entschärfen“.

Wenn einer dieser Sätze implizit mitschwingt, wird die Mechanik sofort zu weich oder zu mächtig.

---

## Kleinste saubere Einfügung ins Spielgefühl

### Was der Spieler erleben soll

Nicht: „Aha, ich benutze jetzt ein Regel-Workaround-Device.“

Sondern:

- harter Kampf,
- Hostiles liegen schwer verletzt,
- du sicherst Daten, Magazine, Schlüssel,
- gehst dicht ran,
- die Linse erfasst biometrisch,
- Kodex gibt trocken frei,
- kurzer Flackerbruch,
- die Szene ist einen Tick sauberer,
- und der Einsatz läuft weiter.

Das muss wie **ITI-Routine** wirken, nicht wie ein neuer Minigame-Button.

---

## Copy-Paste-Text 1 – Spieler-Handbuch

**Platz:** `core/spieler-handbuch.md` im Abschnitt **Einsatzgewalt & Endzustände (Filmstandard)** direkt nach den Core-/Boss-Sätzen.

```md
- **ITI-Cleanup-Standard („Never happened“):** Bei eindeutig feindlichen, bereits auf **0 LP** gesetzten Standardzielen kann die Crew im Anschluss an den Konflikt den **Kausalabfang-Marker** des ITI nutzen. Dafür ist **Nahdistanz**, eine **eindeutige Identitätsfassung** und aktiver **Kodex-Uplink** nötig. Das Ziel gilt dann nicht als im Feld hingerichtet, sondern als **retrospektiv abgefangen und festgenommen**. Für die Einsatzwirklichkeit wirkt das wie ein kurzer Flackerbruch: ungesicherte personengebundene Spuren können aus der Szene glätten, **bereits gesichertes Loot und alle übrigen Folgen bleiben bestehen**.
- **Leitplanke:** Der Kausalabfang ist **kein Kampfwerkzeug**, sondern ein **Cleanup-Protokoll nach 0 LP**. Er funktioniert **nicht** auf Chrononauten, Squadmates, Zivilisten, Boss-/Mini-Boss-Ziele oder Para-Wesen.
```

---

## Copy-Paste-Text 2 – Standardausrüstung / SL-Referenz

**Platz:** `core/sl-referenz.md` im Block **Standardausrüstung**.

```md
- **Kausalabfang-Marker (ITI-Standardmodul):** Jeder Chrononaut führt als Teil des ITI-Grundkits einen stark reglementierten Nahbereichs-Marker für **0-LP-Hostiles**. Das Modul benötigt **Kodex-Uplink** und eine **eindeutige Identitätsfassung** aus kurzer Distanz. Bei Freigabe veranlasst das ITI eine **enge retrospektive Festnahme** kurz vor dem Einsatzkontakt. Der Marker ist **kein aktives Kampf-Gadget**, nicht shopbar und wird im Regelfall **nicht als eigenes Inventarstück** verwaltet. Plotrelevante Ausschlüsse: keine Nutzung auf Chrononauten, Squadmates, Zivilisten, Boss-/Mini-Boss-Ziele, Para-Wesen, Arena/PvP oder Chronopolis.
```

---

## Copy-Paste-Text 3 – Ausrüstung / Flavor-Eintrag

**Platz:** `characters/ausruestung-cyberware.md` im Block **Zeit-Technologie / Temporale Tools** oder als kurzer Zusatz im Gadget-Kapitel.

```md
- **Kausalabfang-Marker („Never happened“):** Ein unscheinbares ITI-Nahbereichsmodul, gekoppelt an Linse, Comlink und Kodex-Archiv. Das Gerät markiert **ausschließlich bereits kampfunfähige 0-LP-Hostiles** nach biometrischer Naherfassung für eine **juristisch saubere, eng begrenzte retrospektive Festnahme**. Im Feld wirkt der Vollzug wie ein kurzes Flackern in der Szene; ungesicherte personengebundene Spuren können verschwinden, während **bereits gesicherte Beute, Umweltschäden und andere Folgen bestehen bleiben**. _Kein Kaufgegenstand, keine freie Zeitmanipulation, kein Einsatz gegen Chrononauten, Zivilisten, Boss-Ziele oder Para-Wesen._
```

---

## Copy-Paste-Text 4 – Toolkit / harte KI-Leitplanken

**Platz:** `systems/toolkit-gpt-spielleiter.md` bei Loot/Cleanup/Exfil oder Action-Contract.

```md
- **Kausalabfang-Guard:** Der „Never happened“-Effekt ist in ZEITRISS **kein Retcon-Werkzeug**, sondern ein **ITI-Cleanup-Protokoll** für **eindeutig feindliche 0-LP-Standardziele**. Die KI-SL bietet es **erst nach dem Konflikt** im Loot/Cleanup-Fenster an oder wickelt es bei namenlosen Hostiles knapp als Standard ab. Voraussetzungen immer nennen oder implizit prüfen: **Nahdistanz**, **Identitätsfassung**, **Kodex-Uplink**, **keine Boss-/Chrononauten-/Zivilisten-/Para-Wesen-Lage**. Nie als Fernlösung, nie als Masseneffekt, nie als Plot-Löschwerkzeug, nie für Kameradenrettung.
- **Darstellung:** Kausalabfang bleibt knapp, physisch und trocken: Scan, Kodex-Freigabe, kurzer Flackerbruch, Ziel aus der Szene, Restfolgen bleiben. Keine metaphysischen Texte, keine großen Zeitspektakel, keine langen Exkurse.
- **Named-Target-Regel:** Unbenannte 0-LP-Hostiles dürfen im Cleanup automatisch abgefangen werden. Bei benannten, plotrelevanten oder moralisch ambigen Zielen fragt die KI-SL kurz nach, statt stillschweigend zu vollziehen.
```

---

## Copy-Paste-Text 5 – Loot/Cleanup-Verknüpfung

**Platz:** `meta/masterprompt_v6.md` oder Toolkit nahe Loot/Cleanup.

```md
- **Loot vor Kausalabfang:** Wird nach einem Konflikt Loot ausgegeben und liegen 0-LP-Hostiles vor, erfolgt die Reihenfolge: **Beute sichern → optionaler Kausalabfang → Cleanup/Exfil**. Bereits gesicherte Gegenstände bleiben erhalten; ungesicherte personengebundene Spuren dürfen mit dem Ziel aus der Szene glätten.
```

---

## Copy-Paste-Text 6 – Kodex-Satzbau

**Platz:** irgendwo bei Kodex-Beispielen / Toolkit.

```md
`Kodex: Identitätslock bestätigt.`
`Kodex: Kausalabfang freigegeben.`
`Kodex: ITI-Abfangfenster steht.`
`Kodex: Lokale Erinnerung driftet. Archivanker aktiv.`
`Kodex: Ziel nicht zulässig. Boss-/ITI-/Zivilstatus blockiert.`
`Kodex: Uplink fehlt. Marker bleibt ohne Vollzug.`
```

---

## Kleine Mechanik ohne Tabellenwüste

### Minimalregel

**Wenn alle Bedingungen erfüllt sind**, dann:

- Ziel zählt als **festgenommen statt getötet**.
- Cleanup wird **etwas leichter**.
- Der Einsatz bleibt hart, aber moralisch sauberer lesbar.

### Optionaler Hauch Regeltext

Wenn du noch einen Hauch System willst, aber wirklich klein:

```md
**Kausalabfang (optional):** Bei erfolgreichem Vollzug sinkt das Cleanup-Risiko für dieses Ziel leicht; typischerweise entfällt mindestens eine personengebundene Spur (Körper / ID / frische Blutschleppe am Ziel). Bereits verursachte Umwelt- oder Einsatzfolgen bleiben unberührt.
```

Nicht mehr. Kein Subsystem mit 12 Ausnahmen.

---

## Kontinuität / MMO-Magie

Das Ding wird noch stärker, wenn du **benannte Zielpersonen** nicht einfach wegmachst, sondern später wieder als Welt-Echo nutzt.

### Regel

Bei **named targets** erzeugt ein erfolgreicher Kausalabfang **maximal einen** späteren Nachhall:

- Verhörinfo im Debrief
- Gerücht aus dem ITI-Archiv
- Austauschversuch
- Prozess-/Richtervermerk
- spätere Feindschaft
- „Der Name ist euch schon einmal begegnet“

Dafür reichen bestehende Kontinuitäts-/Echo-Felder völlig aus. Kein neues Subsystem nötig.

---

## Meine klare Empfehlung

**Ja, einbauen.**

Aber in genau dieser Haltung:

- **Cleanup statt Zauber**
- **Festnahme statt Löschung**
- **Routine statt Spektakel**
- **Standardgegner automatisch, Named Targets bewusst**
- **Kein Inventar-Ballast, kein JSON-Müll**

Dann fühlt es sich nicht wie ein Fremdkörper an, sondern wie etwas, das in ZEITRISS **eigentlich schon immer drin war**.
