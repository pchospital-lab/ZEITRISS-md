# ZEITRISS – Review: Ruf/Tier-Progress + Alien/Mystery-Kern

## Kurzfazit

- **Der neue Ruf-/Tier-Gedanke ist spielerisch stark.** Er passt deutlich besser zur aktuellen Missionslänge und zum 5/10-Bossrhythmus.
- **Schema-seitig ist v7 dafür bereit.** `reputation.iti`, `rank` und Tier-Lizenzen existieren bereits.
- **Das Repo ist aber noch nicht SSOT-sauber.** Vor allem das alte Rufmodell, die Kopplung ITI-Ruf = bester Fraktionsruf, Tier V als Quest-only sowie uneinheitliche Rangnamen bremsen die neue Linie.
- **Der Alien-/Mystery-Kern ist wieder da**, aber noch nicht gleichmäßig verteilt: tief in `core/zeitriss-core.md` stark, in der Player-Onboarding-Schicht noch teils verwässert.

---

## Copy-paste-Issue 1 – ITI-Ruf von Fraktionsruf entkoppeln

**Titel:** SSOT: `reputation.iti` als operativer Lizenzruf, `reputation.factions.*` als narrative Politik sauber trennen

**Problem:**
Aktuell vermischen mehrere Texte operativen ITI-Ruf, Fraktionsruf und Tier-Freischaltung. Für den neuen Boss-basierten Progress muss klar sein:
- `reputation.iti` = formaler Institutsruf
- `reputation.factions.*` = politisches / erzählerisches Standing
- Tier-/Lizenzzugang hängt an `reputation.iti`, nicht am besten Fraktionswert

**Warum:**
Sonst kollidiert der neue deterministische Boss-Progress mit Wahl-/Fraktionsspiel und erzeugt Drift in Debrief, Shop, Save und Rank-Anzeige.

**To-do:**
1. In `characters/charaktererschaffung-grundlagen.md` alle Stellen ersetzen, die ITI-Ruf aus Fraktionsruf ableiten.
2. In allen spielrelevanten Modulen festhalten:
   - `reputation.iti` steuert **Rang, Lizenz-Tier, Freigaben**
   - `reputation.factions.*` steuert **Rabatte, Zugänge, Misstrauen, Story-Folgen**
3. In Debrief/Score-Screen bei Ruf-Update immer explizit `ITI-Ruf` benennen.
4. Kein automatischer Hard-Link `iti = max(factions.*)` mehr.

**Direkt übernehmbarer Ersatztext:**

```md
## Rufsystem (ITI & Fraktionen)

ZEITRISS trennt ab jetzt sauber zwischen **operativem ITI-Ruf** und **Fraktionsruf**.

- **`reputation.iti`** = formaler Ruf beim Institut. Er steuert **Rang**, **Lizenz-Tier**, offizielle **Freigaben** und den Zugriff auf hochwertigere ITI-Ressourcen.
- **`reputation.factions.*`** = politisches und erzählerisches Standing bei einzelnen Strömungen, Zellen und Machtblöcken. Dieser Ruf kann positiv oder negativ ausfallen, ohne den formalen ITI-Ruf automatisch zu überschreiben.

Damit gilt: Ein Chrononaut kann beim ITI als zuverlässig gelten, ohne von jeder Fraktion geliebt zu werden — und umgekehrt.
```

---

## Copy-paste-Issue 2 – Neuer Ruf-/Tier-Progress als SSOT festziehen

**Titel:** Progression umstellen: ITI-Ruf +1 nach erster Core-Mission, danach +1 an jedem Core-Boss

**Problem:**
Das alte Rufmodell mit groben Missionsmengen passt nicht mehr zur heutigen Missionslänge, Bossdramaturgie und zum Serienrhythmus.

**Zielbild:**
- Start: Ruf 0
- Nach erster erfolgreich abgeschlossener **Core-Mission**: Ruf 1
- Danach: **+1 ITI-Ruf bei jedem erfolgreich abgeschlossenen Core-Boss**
  - Mission 5 → Ruf 2
  - Mission 10 → Ruf 3
  - Mission 15 → Ruf 4
  - Mission 20 → Ruf 5
- Rift-Ops, Arena, Chronopolis, HQ-Freerun und Training geben **standardmäßig keinen automatischen ITI-Ruf**
- Fehlschlag/Abort gibt **keinen** automatischen Rufgewinn

**Warum:**
- Früh spürbare Belohnung nach der ersten vollen Folge
- Dramatische Progression synchron zu Mini-Boss / Episoden-Boss
- Tier-Aufstiege fühlen sich wie Staffelhöhepunkte an

**To-do:**
1. Altes Ruf-Tabellenmodell aus `characters/charaktererschaffung-grundlagen.md` entfernen.
2. In `meta/masterprompt_v6.md` Debrief-Logik konkretisieren.
3. In `core/sl-referenz.md` oder `core/zeitriss-core.md` einen kleinen SSOT-Kasten ergänzen.
4. Score-Screen-Beispiel für M1, M5, M10 ergänzen.

**Direkt übernehmbarer Ersatztext:**

```md
### ITI-Ruf – Standard-Progression (SSOT)

Der formale **ITI-Ruf** (`reputation.iti`) wächst im Standardmodus **deterministisch** über den Core-Loop:

- **Start:** Ruf 0
- **Erste erfolgreich abgeschlossene Core-Mission:** Ruf +1
- **Danach:** Ruf +1 bei jedem erfolgreich abgeschlossenen Core-Boss
  - **Mission 5:** Mini-Boss → +1
  - **Mission 10:** Episoden-Boss → +1
  - **Mission 15:** Mini-Boss → +1
  - **Mission 20:** Episoden-Boss → +1

Damit ergibt sich im Normalfall:
- nach Mission 1 → **Ruf 1**
- nach Mission 5 → **Ruf 2**
- nach Mission 10 → **Ruf 3**
- nach Mission 15 → **Ruf 4**
- nach Mission 20 → **Ruf 5**

**Wichtig:**
- Nur **erfolgreich abgeschlossene Core-Missionen/Bossabschlüsse** zählen für diesen Pfad.
- **Rift-Ops, Arena, Chronopolis, HQ-Freeruns und Training** verleihen standardmäßig **keinen automatischen ITI-Ruf**.
- **Fehlschläge oder Abbrüche** geben keinen Rufgewinn; Fraktionsruf und Storyfolgen können sich trotzdem verändern.
- **Cap:** `reputation.iti` maximal 5.
```

---

## Copy-paste-Issue 3 – Tier-V-Logik an das neue Ziel anpassen

**Titel:** Tier V nicht länger quest-only, wenn „alles offen, aber durch CUs begrenzt“ der neue Standard sein soll

**Problem:**
Der neue Wunsch lautet: Bei Ruf 5 sollen alle Möglichkeiten grundsätzlich offenstehen, harte Begrenzung läuft dann über CU und HQ-Sinks. Aktuell blockiert Tier V als Quest-only diesen Loop.

**To-do:**
1. `characters/ausruestung-cyberware.md` anpassen.
2. In allen Shop-/Freigabetexten Tier V als kaufbare Lizenz behandeln.
3. Optional: Sonderobjekte weiterhin separat über Quest, aber nicht das gesamte Tier.

**Direkt übernehmbarer Ersatztext:**

```md
**Tier-Lizenzen — Preistabelle:**

| Tier | Ruf-Anforderung | Lizenzkosten |
|------|-----------------|--------------|
| 0    | —               | Frei         |
| I    | Ruf +1          | 200 CU       |
| II   | Ruf +2          | 500 CU       |
| III  | Ruf +3          | 1.500 CU     |
| IV   | Ruf +4          | 3.000 CU     |
| V    | Ruf +5          | 5.000 CU     |

Ab **Ruf +5** stehen grundsätzlich alle regulären ITI-Lizenzpfade offen. Die eigentliche Begrenzung läuft dann über **CU**, Verfügbarkeit, Storyfreigaben und HQ-Ressourcen — nicht mehr über eine pauschale Tier-V-Sperre.
```

**Hinweis:**
Wenn einzelne Artefakte, Schiffe oder Sondermodule trotzdem exklusiv bleiben sollen, dann als **Objekt-/Projektfreigabe** formulieren, nicht als globales Tier-V-Verbot.

---

## Copy-paste-Issue 4 – Rangnamen einmalig kanonisieren

**Titel:** `rank`-String im v7-Save mit einem festen Ruf-Mapping definieren

**Problem:**
Der Save speichert `rank`, der Debrief zeigt Rangnamen, aber die Begriffe driften noch.

**To-do:**
1. Ein einziges Mapping definieren.
2. Beispiele in Save-Schema, Handbuch und Debrief auf dieses Mapping ziehen.
3. Keine alternierenden Begriffe mehr für denselben Rufwert.

**Vorschlagsmapping:**

```md
### Rang-Mapping (SSOT)

| ITI-Ruf | Rang |
|--------:|------|
| 0 | Rekrut |
| 1 | Operator I |
| 2 | Feldagent |
| 3 | Senior-Feldagent |
| 4 | Elitechrononaut |
| 5 | Apex-Agent |
```

**Debrief-Format:**

```text
Rang Feldagent · ITI-Ruf +2 · Lizenz Tier II
```

---

## Copy-paste-Issue 5 – Level-10-Meilenstein vs. Lizenz-Tier entwirren

**Titel:** Clarify: Level 10 = Chronopolis/Vertrauen, Ruf/Tier = Lizenzzugang

**Problem:**
Aktuell klingt es teilweise so, als würde Level 10 bereits breiteren Gear-Zugang freischalten. Das kollidiert mit dem gewünschten Ruf-/Tierpfad.

**Empfehlung:**
- **Level 10** = Vertrauen, Chronopolis-Schlüssel, größere Verantwortung, ggf. narrative Sonderrechte
- **Ruf/Tier** = formaler Shop-/Lizenzzugang

**Direkt übernehmbarer Ersatztext:**

```md
**Klarstellung:**
Der **Level-10-Meilenstein** steht primär für **Vertrauen, Chronopolis-Freigabe und operative Verantwortung**.
Der **formale Zugriff auf ITI-Ausrüstungslinien** läuft dagegen über **ITI-Ruf und Lizenz-Tier**.

Level-Meilensteine und Ruf-Tiers dürfen sich dramaturgisch überschneiden, ersetzen sich aber nicht.
```

---

## Copy-paste-Issue 6 – Player-Onboarding vom harten Alien-Fakt befreien

**Titel:** Spieler-Handbuch: „galaktische Föderation fortgeschrittener Alien-Spezies“ in Gerücht-/Aktenlogik umschreiben

**Problem:**
Der Mystery-Kern funktioniert am stärksten, wenn früh **Alien-Ikonographie** da ist, aber noch **nicht** als harte Welt-Tatsache bestätigt wird. Genau das wird im Player-Onboarding aktuell unterlaufen, sobald dort wörtlich von einer fortgeschrittenen Alien-Föderation gesprochen wird.

**Ziel:**
- Unheimlich bleiben
- Spieler sollen UFO/Grey/Galactic-Vibes spüren
- aber nicht den Eindruck bekommen, dass ZEITRISS schlicht „Aliens sind real“ als Baseline setzt

**Direkt übernehmbarer Ersatztext für die Einleitung:**

```md
Seitdem operiert das ITI aus der Nullzeit, einem versteckten Hub jenseits des normalen Zeitstroms. Von dort aus koordiniert es Einsätze überall und jederzeit. In beschlagnahmten Dossiers tauchen Gerüchte über „Fremde“, „Graue“ und angebliche Bündnisse jenseits der Menschheit auf — doch im ITI gilt eine nüchterne Arbeitsregel: Solange keine harten Beweise vorliegen, werden solche Fälle als **fehlklassifizierte Zeitphänomene, posthumane Bio-Hüllen, Fraktionsoperationen oder Zukunftstechnologie** behandelt.

Hilfe von außen gibt es nicht. Die Menschheit rettet ihre Zeitlinie selbst: mit eigener Forschung, eigener Härte und Entscheidungen, die niemand außerhalb des ITI je mitbekommen wird.
```

---

## Copy-paste-Issue 7 – Das eigentliche Setting als „Mystery Contract“ explizit machen

**Titel:** Einen kurzen Mystery-Contract in Player-Handbuch/Kampagnenübersicht ergänzen

**Problem:**
Der Kern von ZEITRISS ist nicht „keine Weirdness“, sondern: **Weirdness zuerst als Mythos/Alien/Okkultik erlebt, später plausibel und verstörend erklärt**. Das sollte einmal glasklar als Ton-Regel im Repo stehen.

**Direkt übernehmbarer Kasten:**

```md
### Mystery-Contract von ZEITRISS

ZEITRISS spielt bewusst mit **UFO-, Alien-, Okkult- und Verschwörungsbildern**. Fälle dürfen sich im ersten Zugriff wie **Graue, Wunder, Geister, Götterboten oder außerirdische Besucher** anfühlen.

Der Standard-Read des ITI bleibt jedoch bodenständig: **erst Spur, dann Technik, dann Zeitphysik**.

- **Core-Ops** liefern auf lange Sicht fast immer eine rationale, wenn auch verstörende Erklärung.
- Typische Wahrheiten hinter dem Mythos sind: **posthumane Bio-Hüllen**, **fehlklassifizierte Zukunftstechnologie**, **Fraktions-PsyOps**, **Zeitversatz** oder **verdeckte Bergungsoperationen**.
- **Rift-Ops** dürfen echter und unberechenbarer wirken, bleiben aber in ZEITRISS trotzdem physisch und konkret.

Der stärkste Aha-Moment des Settings entsteht, wenn Spieler erst „Aliens!“ denken — und später begreifen, dass sie in Wahrheit einer viel älteren und zugleich menschlicheren Zukunftsspur gefolgt sind.
```

---

## Copy-paste-Issue 8 – „Die Grauen“ und „Greys“ vereinheitlichen

**Titel:** Graue Phänotypen als ITI-Deckname / Incident-Klasse definieren, nicht als sichere Spezies

**Problem:**
Einerseits gibt es „Die Grauen“ als offene Fremdfraktion, andererseits „Greys“ als Urban-Myth-Falschspur. Beides kann gleichzeitig cool sein, wirkt aber ohne Klammer unsauber.

**Empfehlung:**
„Graue/Greys“ = **ITI-Deckname** für Vorfälle mit bestimmter Silhouette/Ikonographie. Dahinter können verschiedene Wahrheiten liegen.

**Direkt übernehmbarer Ersatztext:**

```md
**Die Grauen / Greys** ist im ITI kein sauberer Speziesbegriff, sondern ein **Arbeits- und Deckname** für Vorfälle mit wiederkehrender Ikonographie: kleine, glatte Körper, übergroße Augen, sterile Fremdwirkung, medizinische oder beobachtende Signaturen.

Je nach Fall verbergen sich dahinter:
- posthumane Bio-Hüllen,
- speziell verzerrende Skinsuits,
- fehlklassifizierte Bergungsteams,
- Fraktions-PsyOps,
- oder bewusst gestreute Falschbilder.

Gerade diese Unschärfe macht den Begriff im Feld so gefährlich — er klingt eindeutig, ist es aber nicht.
```

---

## Direkt nutzbare Signature-Hooks

### 1) Roswell als ZEITRISS-Kernfall

```md
**Roswell 1947 – Absturzstelle bei Corona**

- **Erster Eindruck:** verkohlte Senke, versprengte „Folien“, Militärsperren, Zeugen berichten von kleinen grauen Gestalten.
- **Feldread:** mögliches UFO-Ereignis.
- **Wahrheitsebene 1:** Crash eines zeitversetzten Aufklärungs- oder Bergungsvehikels.
- **Wahrheitsebene 2:** Die geborgenen Körper wirken nichtmenschlich, tragen aber dieselbe Grundstruktur wie humane DNA.
- **Reveal-Spuren:** ITI-kompatible Frequenzen, Legierung aus einer noch nicht erreichbaren Zukunft, chirurgische Umbauten statt „fremder“ Anatomie.
```

### 2) Orbitaler „Grey Panic“ als modernes Signature-Casefile

```md
**Orbitalplattform Erebus – Grey Lockdown**

- **Erster Eindruck:** Crew meldet schmale graue Gestalten in den Lüftungsschächten, schwarze Augen im Stroboskoplicht, geöffnete Biolabore.
- **Feldread:** Alien-Boarding auf einer Raumstation.
- **Wahrheitsebene 1:** Ein instabiler Zeitriss hat Kleinraubdinosaurier und Paläobiomaterial in den Wartungsring verschlagen.
- **Wahrheitsebene 2:** Parallel arbeitet ein emissionsarmes Bergungsteam in posthumanen Exo-Skins an denselben Proben.
- **Reveal-Spuren:** Kratzmuster statt Werkzeugspuren, Wärmeprofile mit Tierbewegung, Funkantwort auf ITI-Band, „graue“ Silhouetten nur unter Notlicht eindeutig.
```

---

## Meine Empfehlung in einem Satz

**Mach den operativen Ruf deterministisch und bossbasiert, mach Fraktionsruf politisch und frei, und behandle „Aliens“ im Onboarding nie wieder als harte Welt-Tatsache, sondern als das, was ZEITRISS am besten kann: ein plausibles Mysterium, das erst später kippt.**
