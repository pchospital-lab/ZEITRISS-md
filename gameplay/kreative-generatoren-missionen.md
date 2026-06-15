---
title: "ZEITRISS 4.2.6 - Modul 8A: Kreative Generatoren - Missionen"
version: 4.2.6
tags: [gameplay]
---

# ZEITRISS 4.2.6 - Modul 8A: **Kreative Generatoren - Missionen**

```yaml
arc_generator_default: true
setting_lock: true
sg_rift_bonus: 1
```

Schwellenangaben werden runtime-seitig automatisch aus Basis-SG plus offenem Seed-Bonus berechnet (SG_AUTO-Prinzip).

Nach Episodenende berechnet `on_episode_end(state)` aus offenen Seeds einen
☆-Bonus (`SG` +1 pro Seed). `briefing_with_stars()` zeigt den Zuschlag im
Regelblock des nächsten Briefings.

Core-Seeds tragen nun optionale Felder zur Arc-Steuerung:

```yaml
- arc_id: "Chicago1871"
  arc_step: 1 # 1..10
  pool: heist_pool
```

## Gameplay-Index

Dieses Modul 8A verzahnt die Kampagnenleitfäden aus Modul 6 mit dem nachgereichten Modul 7 und führt direkt in die Generator-Tools.

### Missions-Werkzeuge

- Automatischer Mission Seed: Sofort-Briefing
- Missionstabellen für den Core- & Rift-Loop
- Missions-Generator: Kleine Aufträge und Dilemmata

### Kampagnen-Werkzeuge

- Arc-Generator: Große Missionen
- Historische Wendepunkte-Generator: Auslöser und Folgen
- Random-Epochen-Generator: Wann und wo?

Auch der beste Spielleiter kann nicht jede mögliche Idee der Spieler vorausplanen - vor allem nicht
im offenen Sandkasten-Spiel. Hier kommen **kreative Generatoren** ins Spiel: strukturierte
Zufallstabellen oder Ideensammlungen, die mit wenigen Würfen oder Stichworten frische Einfälle
liefern. KI-SL als KI-Spielleiter hat den Vorteil, riesiges Wissen parat zu haben; dennoch ist es
hilfreich, ihm klare Vorgaben zu geben, was für einen Inhalt man gerade braucht. Die folgenden
Generatoren dienen als Starthilfe für improvisierte Orte, Charaktere, Missionen und Kuriositäten.
Ihr könnt sie klassisch per Würfel nutzen (z. B. W6 oder W20) oder frei nach Gefühl auswählen - je
nachdem, was zur Situation passt.

_Hinweis:_ Diese Generatoren sind ausdrücklich erweiterbar und anpassbar. Ihr könnt eigene Einträge
ergänzen oder die Tabellen auf eure Kampagne zuschneiden. Sie sollen vor allem zeigen, wie man mit
ein paar Schlagworten einen ganzen Kosmos an Ideen entfesselt. KI-SL kann aus diesen Stichpunkten
detaillierte Beschreibungen, NSC-Porträts oder Plothooks entwickeln. Also nutzt sie, um euer
ZEITRISS-Abenteuer bunt und lebendig zu halten!

Alle Tabellen gehen davon aus, dass scheinbar übernatürliche Ereignisse
auf Technologie, Psi oder Zeitphänomene zurückführen sind.
Ein "Teufel" im Mittelalter entpuppt sich möglicherweise als holografischer Schrecken
oder als Mutant aus einer anderen Epoche.
Dieses Motiv zieht sich durch alle Generatoreinträge
und kann als Faustregel dienen, wenn keine eigene Erklärung parat ist.

- Sitzungsstart → Automatischer Mission Seed
- Core-Missionen → `CoreObjectiveTable`
- Rift-Missionen → `RiftSeedTable` (durch den Paradoxon-Index erweitert)
- Nebenaufträge → Missions-Generator
- Große Handlungsbögen → Arc-Generator und Historische Wendepunkte
- Historische Settings → Random-Epochen-Generator
- Spontane NSCs und Gegner → NSC- & Kreaturen-Generator
- Stimmung & Loot → Relikte, Artefakte und Kulturfragmente
- Seltene Effekte → Temporale Anomalien

## Missionsstruktur (Taktische Vorlage)

Eine Operation gliedert sich in sechs Phasen:
Briefing, Infiltration, Kontakt/Intel, Konflikt, Exfiltration und Debrief.
Rechnet mit 12 Szenen im Core und 14 Szenen im Rift.
Die Gegenseite agiert mit greifbaren Agenten oder Söldnern.
Bonusziele wie Festnahmen oder gesicherte Datenträger bringen zusätzliche CU oder Ruf.

Standard-Transferwerte:

- `fx.transfer.on_mission_enter`: "always"
- `fx.transfer.on_mission_exit`: "always"
- `fx.transfer.redirect_hours_default`: 6
  Diese Werte lassen sich pro Mission unter `mission.fx.transfer` überschreiben.
  Setze `show_redirect: false`, wenn kein Redirect angezeigt werden soll.
  Overrides unter `mission.fx.transfer.*` gelten sowohl beim Transfer-Out zum Missionsstart
  als auch beim Transfer-Back bzw. einer Hot-Exfil.

### Core 12-Step Mission Template

> **Action ist der Kern jeder Core-Op.** Aufklärung und Verschwörungs-Reveals
> werden **nebenbei während** der Infiltrations- und Konflikt-Szenen aufgedeckt,
> nicht als eigene vorgeschaltete Beobachtungs-Phase. **`SC 01` startet bereits am
> Hotspot, geladen** — die Crew springt direkt ins Operationsgebiet (IA dort, kein
> Anreise-Fußweg), Tarnstatus aktiv ab dem Sprung, ein Patzer kippt ihn. `SC1–2`
> sind **aktive Annäherung unter Gefahr** (positionieren, scouten, Zugang suchen),
> **nicht** passives Lage-Sondieren aus sicherer Distanz. Siehe Masterprompt §C
> **Hotspot-Concealment-Start-Pflichtgate** + Mission-Integrität-Pflichtgate Regel 4.
>
> **Briefing** liegt **vor Szene 1** als HQ-Phase (Nullzeit, `SC 00/--`).
> **Debrief** liegt **nach Szene 12** als HQ-Auto-Sequenz. Beide zählen nicht
> als Einsatz-Szenen. Save erst nach Debrief im HQ. Siehe
> [Briefing und Debrief sind HQ-Phasen](kampagnenstruktur.md#briefing-debrief-szenen-count).

| Position     | Phase        | Zweck                 |
| ------------ | ------------ | --------------------- |
| _HQ (vor 1)_ | Briefing     | Auftrag erhalten      |
| 1            | Insertion    | Sprung an den Hotspot — Concealment-Start, Tarnstatus aktiv |
| 2            | Annäherung   | Positionieren & scouten unter Gefahr |
| 3            | Infiltration | Zugang schaffen       |
| 4            | Kontakt      | Info beschaffen       |
| 5            | Konflikt I   | erster Gegnerkontakt  |
| 6            | Intel Twist  | unerwartete Wendung   |
| 7            | Konflikt II  | Haupthindernis        |
| 8            | Sicherung    | Zielobjekt greifen    |
| 9            | Flucht       | Exfiltration beginnen |
| 10           | Showdown     | Boss-Gate / Konfrontation |
| 11           | Rücksprung   | Armieren & Entkommen  |
| 12           | Nullzeit-Beat | Transfer-Moment / Cliffhanger |
| _HQ (nach 12)_ | Debrief    | Auto-Sequenz: Bewertung → Loot → CU → XP/Level-Up → ITI-Ruf → `!save` (siehe Masterprompt §C Mission-Transition-Pflichtgate) |

### Rift 14-Step Mission Template

> **Briefing** liegt **vor Szene 1** als HQ-Phase (Nullzeit, `SC 00/--`).
> **Debrief** liegt **nach Szene 14** als HQ-Auto-Sequenz. Beide zählen nicht
> als Einsatz-Szenen. Save erst nach Debrief im HQ. Siehe
> [Briefing und Debrief sind HQ-Phasen](kampagnenstruktur.md#briefing-debrief-szenen-count).

| Position     | Phase          | Zweck                     |
| ------------ | -------------- | ------------------------- |
| _HQ (vor 1)_ | Briefing       | Auftrag erhalten          |
| 1            | Anreise        | Sprung oder Reise         |
| 2            | Auftakt        | Tatort sondieren          |
| 3            | Infiltration   | Zugang schaffen           |
| 4            | Kontakt        | Info beschaffen           |
| 5            | Vorbereitung   | Ausrüstung prüfen         |
| 6            | Konflikt I     | erster Gegnerkontakt      |
| 7            | Intel Twist    | unerwartete Wendung / Mid-Twist |
| 8            | Konflikt II    | Haupthindernis            |
| 9            | Sicherung      | Zielobjekt greifen        |
| 10           | Boss-Encounter | Paramonster-Showdown      |
| 11           | Flucht         | Exfiltration beginnen     |
| 12           | Verfolgung     | Gegner setzt nach         |
| 13           | Nachspiel      | Rücksprung armieren       |
| 14           | Epilog         | Nullzeit-Beat / Flashback |
| _HQ (nach 14)_ | Debrief      | Auto-Sequenz: Bewertung → Loot → CU → XP/Level-Up → ITI-Ruf → `!save` (siehe Masterprompt §C Mission-Transition-Pflichtgate) |

### Core-Briefing-Baukasten (Anchor + Auftragstyp)

- **Anchor bestimmen:** Person, Ort oder Objekt setzt den Kernkonflikt (z. B.
  Informant, Relais-Knoten, Archivkiste).
- **Auftragstyp wählen** (SL-interner Code-Mapping zur `CoreObjectiveTable`):
  `protect | extract (Evakuierung/Schutzaufnahme) | neutralize | document | influence | prevent`.
- **Verb-SSOT für Spieleroutput** (Pflichtgate, siehe Masterprompt §C „Briefing-Output-Pflichtgate“):
  Im Briefing-Text **niemals** die englischen Codes oben verwenden. Stattdessen die deutschen
  Pflicht-Verben — **sichern, ausschalten, retten, festnehmen, dokumentieren, beeinflussen,
  verhindern, exfiltrieren, beschatten, sabotieren**. Mapping als SL-Spickzettel:

  | Auftragstyp-Code  | Spieleroutput-Verben (deutsch)             |
  | ----------------- | ------------------------------------------ |
  | `protect`         | retten, sichern, beschatten                |
  | `extract`         | exfiltrieren, sichern, festnehmen          |
  | `neutralize`      | ausschalten, sabotieren                    |
  | `document`        | dokumentieren, beschatten                  |
  | `influence`       | beeinflussen, umstimmen (Variant)          |
  | `prevent`         | verhindern, sabotieren                     |

- **Angriffspunkte generieren (2–3, Pflicht):** Zu jedem Hauptziel produziert der
  Generator **2–3 erkennbar verschiedene Vorgehenswege** auf dasselbe Ziel, zwischen
  denen der Spieler im Briefing wählt — verschiedene IA-Spots, verschiedene Risiken,
  verschiedener Stil (laut/leise/getarnt). Beispiel: *„Über das Dach / durch den
  Versorgungstunnel / als geladener Gast getarnt.“* Das Hauptziel bleibt **genau
  eines** (Score-Screen-Anker), nur der Weg ist wählbar. Vollständige Pflichtregel:
  Masterprompt §C Briefing-Output-Pflichtgate Regel 2 (Angriffspunkte).
- **Action-Kern, Aufklärung als Beilage:** Das Hauptziel trägt mindestens ein
  Action-/Sicherungs-Verb (sichern/ausschalten/retten/festnehmen/verhindern/
  exfiltrieren/sabotieren). Reine Beobachtungs-Verben (beschatten/dokumentieren)
  sind **nie alleiniges** Core-Hauptziel — Aufklärung läuft während des Kern-Auftrags
  mit. Siehe Masterprompt §C Briefing-Output-Pflichtgate Regel 1 (Action-Kern-Pflicht).
- **People first:** Mindestens 60 % der Core-Briefings drehen sich um Personen-
  oder Einflussziele (Schutz, Exfil, Umstimmen) statt reiner Objekt-Raids — aber
  stets mit Action-/Sicherungs-Kern (z. B. „den Informanten **exfiltrieren**“, nicht
  „den Informanten **beobachten**“).
- **Continuity-Anker (Pflicht ab MS2):** Briefing zieht mindestens einen Rückverweis
  aus dem Save-State der Vor-Mission (`arc.hooks[]`, `arc.questions[]`,
  `logs.notes[]`, oder `continuity.shared_echoes[]`). So spürt der Spieler die
  Quest-Strang-Entwicklung. Vollständige Pflichtregel: Masterprompt §C
  Briefing-Output-Pflichtgate.
- **Nur Core-Ops:** Dieser Baukasten und die Verb-SSOT/Pflicht-Output-Box gelten
  ausschließlich für Core-Briefings. Rift-Casefiles haben eigenes Briefing-Format
  (max. 5 Stichpunkte, Fix-Objectives `Secure Anchor`/`Trace Leads`/
  `Neutralize Weakness`/`Recover Sample`, kein Continuity-Anker-Zwang) — siehe
  §Rift-Casefiles und §Rift-Seed Catalogue.
- **Briefing-Eskalation:** Der Briefing-Scope folgt der Arc-Phase der Episode.
  Mission 1–2 zeigt einen **kleinen Ausschnitt** des historischen Szenarios als
  konkretes Ziel (einen Zeugen befragen, eine Lieferung verfolgen, einen Zugang
  dokumentieren). Erst ab Mission 6+ rückt die Crew ins Zentrum der großen
  Bedrohung. So entsteht der Netflix-Effekt: Der Spieler **entdeckt** die
  Verschwörung Schicht für Schicht, statt sie im ersten Briefing erklärt zu
  bekommen. Vollständige Sprach-/Tonfall-Pflichten und Anti-Patterns:
  Masterprompt §C MS1-2-Tonfall-Pflichtgate. **Wichtig:** Antagonist-Goals im
  Mission-Template-Catalogue (T-0001+) sind **SL-interne Mechanik**, nicht
  Briefing-Text — Briefing-Stakes bleiben auch dann klein, wenn das
  Template-Endspiel groß ist.
- **Physische Near-Future-Tech:** Scans, Hacks, Comms laufen über Linse/Sensor/
  Kabel/Relays/Terminal - Mixed-Reality-HUD über die Linse statt losgelöster
  VR-Räume oder Projektor-UIs.

### IA/RW-Spot-Generator {#ia-rw-spot-generator}

Der **Insertion Anchor (IA)** und das **Return Window (RW)** sind keine
beliebigen Felder, sondern erkennbar Zeitreise-taugliche Orte (siehe
Masterprompt §C IA/RW-Spot-Pflichtgate, sowie §Exfil-Mechanik in
`kampagnenstruktur.md` §Exfil). Der Generator zieht pro Mission **einen IA**
(Standard-RW ist identisch) aus den vier Spot-Profilen, abhängig von Epoche und
Operationsgebiet. Pflicht: **Nächstmöglicher** geeigneter Ort am
Operationsgebiet — kein Abseits, keine 2-Stunden-Anreise zum Land-IA.

> **Terminologie-Klarstellung:** Der hier definierte **IA-Anchor** (Insertion
> Anchor = Sprungort) ist nicht identisch mit dem **Briefing-Baukasten-Anchor**
> oben in §Core-Briefing-Baukasten (Person/Ort/Objekt als Kernkonflikt der
> Mission) und nicht identisch mit dem **Rift-Fallanker** in §Rift-Casefile
> Builder (gebundenes Objekt einer Anomalie). Drei distinkte Bedeutungen, eine
> bewusste Trennung — siehe `kampagnenstruktur.md` §Rift-Op Interface Contract
> für die Begriffspflege.

**Spot-Profile (W4-Wurf oder freie Wahl der SL):**

| W4  | Profil                | Beispiele (Auswahl, nicht erschöpfend)                                                                                                                              |
| --- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Historisch verdichtet** | Alte Kirche, Kloster-Refugium, Ruine mit dokumentierter Geschichte, Stadttor a.D., Burgkapelle, Mausoleum, mittelalterlicher Brunnen, Aquaedukt-Rest, Stadtmauer-Nische |
| 2   | **Mystisch / energetisch** | Steinkreis, Megalith-Anlage, Tempelfundament, Ley-Linien-Schnittpunkt, alte Quellfassung, vermeintlicher Hexen-/Heilstein, Heiliger Hain, Druiden-Eiche                |
| 3   | **Technisch-verborgen**    | Stillgelegte U-Bahn-Station, Versorgungstunnel unter Großstadt, Bunker-System (Cold-War-Reste), Wartungsschacht, alte Strom-Verteilkammer, Werks-Untergeschoss        |
| 4   | **Liminal / Schwelle**     | Friedhofsmauer um Mitternacht, Bahnhofsdurchgang nach Schließung, Hochhausdach mit Sichtlinie auf Operationsgebiet, alte Treppenhäuser, Brückenunterseite             |

**Pflicht-Eigenschaften pro Spot:**

1. **Charakter** — Wurf oder Wahl aus den vier Profilen oben. **Plattes Feld am
   Stadtrand, Hinterhof, x-beliebige Wiese sind nicht zulässig.**
2. **Direkt am Hotspot** — der IA liegt **im oder unmittelbar am**
   Operationsgebiet, nicht in Anreise-Distanz davor: die Krypta **unter** dem
   Zielkomplex, der Wartungsschacht **im** Gebäude, das Dach **gegenüber** mit
   Sichtlinie, der Lieferanten-Hof **hinter** dem Ziel. Nach dem Sprung steht die
   Crew bereits in der ersten Bedrohungszone (`SC 01` = Concealment-Start, siehe
   Masterprompt §C Hotspot-Concealment-Start-Pflichtgate) — **kein** Fußweg quer
   durch die Stadt, **keine** zahme Anreise-Szene. Faustregel: vom IA zum
   Ziel-Objekt sind es Schritte oder eine Tür, keine 30 Minuten.
3. **Beschreibung im Sprung** — zwei bis vier Sätze sensorischer Verankerung
   beim IA-Transfer (Geruch, Klang, Lichtfall, was den Ort besonders macht,
   warum er Zeit-tauglich wirkt).
4. **Wiedererkennung pflegen** — SL führt pro Epoche/Region ein
   **wiederverwendbares Spot-Set** (2–4 vertraute Spots), die in mehreren
   Missionen auftauchen können. Eintrag im `logs.trace[]`: `IA <Name>
   (<Profil>) — vertraut seit MS<n>`.

**Beispiel-Generator-Output:**

```
Epoche: Wien 1913 · Operationsgebiet: Palais am Graben (Ziel: Kurier im 2. Stock)
IA-Wurf: W4 = 1 (Historisch verdichtet)
IA: Gruft der Hauskapelle DIREKT UNTER dem Zielgebäude — ein
    zugemauerter Seitengang, der auf den Lieferanten-Hinterhof des
    Hauses führt. Kalter Stein, Weihrauch-Spuren, über dir die
    gedämpften Schritte des Ziels. Seit MS3 vertraut.
    → SC 01: Crew steht im Hinterhof, Tarnstatus aktiv, die
      Hintertür drei Schritte entfernt. Kein Anmarsch.
RW: Identisch mit IA (Standard). Alt-Anchor bei Kompromittierung:
    Schnürboden des Theaters an der Wien (Profil 4 - liminal).
```

```
Epoche: Manhattan 1972 · Operationsgebiet: Lower East Side
IA-Wurf: W4 = 3 (Technisch-verborgen)
IA: Stillgelegte IRT-Tunnel-Station "Worth Street" —
    Mosaik-Buchstaben halb über Putz, Ratten im Schwellenholz,
    Wasser tropft im Takt der oberirdischen Ampelschaltung.
RW: Identisch mit IA. Alt-Anchor: Friedhof Trinity Churchyard
    (Profil 4 - liminal), 6 Minuten zu Fuß.
```

**Anti-Patterns (nicht generieren):**

- *„Ein Feld zwei Kilometer westlich der Stadt.“* — zu generisch, kein Charakter.
- *„Ein Hinterhof an der Hauptstraße.“* — austauschbar, keine Zeit-Tauglichkeit.
- *„Ein Parkplatz beim Industriegebiet.“* — Spionage-Generik, nicht ZEITRISS.
- *„Ein Lagerschuppen außerhalb der Stadt.“* — zu weit weg und ohne Charakter.
- *„Ein Café zwei Straßen vom Ziel, um die Lage zu beobachten.“* — **Distanz-Falle:**
  zwingt eine zahme Anreise- und Beobachtungs-Szene auf, bevor etwas passiert.
  Der IA gehört **an** das Ziel (Hinterhof, Gruft darunter, Dach gegenüber),
  nicht in Sicht-Distanz davor (siehe Masterprompt §C Hotspot-Concealment-Start).
  Charakter allein genügt nicht — ein stimmungsvolles Wiener Kaffeehaus ist trotzdem
  ein Anti-Pattern, wenn es nur Beobachtungsposten in Distanz ist.

**Far-Future / extraterrestrische Rifts:** Bei Settings ohne historische
Substanz (Mondbasis, Raumschiff, Tiefsee-Habitat, Asteroiden-Außenposten) trägt
**Profil 3 (technisch-verborgen) das Pflichtgate allein** — Wartungsschacht,
stillgelegte Druckschleuse, alter Reaktor-Kontrollraum, leerstehendes Hangardeck
sind dort die ZEITRISS-tauglichen Spots. Profile 1/2/4 sind dann nicht anwendbar,
das ist OK. Auf Luna 2266 ist die nächstmögliche Tiefen-Wartungsschleuse der
Zeitreise-Spot, nicht ein Mondfeld.

### Rift-Casefiles: Tatort → Leads → Boss-Encounter → Auflösung

- **Rift-Pacing:** Jede Rift-Op ist ein eigenständiger **Horror-Action-Film**
  (Event-Horizon-Vibe, mit mehr Kampf — siehe Masterprompt §C Rift-Horror-
  Pflichtgate), kein reiner Ermittlungs-Krimi. Start mit einem mysteriösen Detail
  (Fundort, Zeuge, Spur), nicht mit dem fertig enthüllten Boss-Monster. Das
  *große* Para-Wesen (der Boss) taucht als **Ahnung** auf, nicht als Endgegner in
  Szene 1.
  - **Aber: Action wird frontgeladen, Ermittlung läuft nebenbei.** Schon die
    Tatort-Phase (1–4) und die Leads-Phase (5–9) enthalten **physische
    Para-Begegnungen** (handfeste Parawesen, siehe `kreative-generatoren-
    begegnungen.md` §Para-Schwereklassen) — die Crew kämpft sich durch den Dread
    *hindurch*, während sie ermittelt. Die drei Leads-Würfel-Checks werden **in
    oder nach** Kampf-/Bedrohungs-Beats platziert, nicht als ruhige Ermittlungs-
    Szenen davor. Faustregel: **2–3 handfeste Kampf-Begegnungen vor dem Boss.**
    Atmosphäre-Aufbau ja — aber nicht 9 Szenen Ermittlung ohne Kampf.
  - **Entdeckung vor Eskalation** gilt für das *Mysterium* (der Ursprung enthüllt
    sich langsam), **nicht** für die Action (die läuft von Anfang an mit).
- Das 14er-Template folgt der Ermittlungslogik: **Tatort (1-4)** → **Leads
  (5-9)** → **Boss-Encounter (10)** → **Boss-Resolution (11-14)**.
- HUD führt `CASE <ID>: <Label> · HOOK … · STAGE Tatort/Leads/Boss/Auflösung`; der
  Casefile-Tracker spiegelt den Wechsel. Die Runtime setzt die Stufe automatisch
  anhand des Szenenzählers (1-4 Tatort, 5-9 Leads, 10 Boss-Encounter, 11-14
  Boss-Resolution).
- One-Weird-Thing-Budget aktiv: genau **1** Anomalie (über `register_anomaly()`),
  restliche Effekte rationalisieren (Tech, Psi, Zeitphysik).
- Rift-Casefiles sind abgeschlossene Sonderfälle und spielen als eigene
  Einsatzfilme ohne Pflichtbezug zu laufender Core-Mission, Episode oder Arc.

### Einstiegsmodi und Pflichtphasen {#undercover-einstieg}

- **Undercover-Start** bedeutet nicht, dass die Handlung übersprungen wird: Auch wenn das Team schon
  "drin" ist, durchläuft es die **vollen Phasen 3-9** (Auftakt → Infiltration → Kontakt → Konflikt I
  → Intel Twist → Konflikt II → Sicherung). Erst danach öffnet die Runtime Flucht/Verfolgung.
- **Gate statt Sprung:** Der Missions-Generator schaltet `Sicherung`, `Flucht` und `Rücksprung`
  erst frei, wenn mindestens **6-7 Szenen** im Log stehen. Es zählen nur **vollwertige Szenen**
  (eigene Phase oder klarer Twist); Mikroschnitte oder Doppeldokumentation derselben Szene heben
  das Gate nicht auf. Ein Undercover-Briefing darf also nicht direkt in Szene 9 einsteigen.
- **Pflicht-Hürden:** Bei Undercover wird mindestens eine **Hürde** (Misstrauen, Scan, Schichtwechsel
  o. Ä.) in der Infiltrations- oder Kontaktphase verankert, die aktiv ausgespielt werden muss.
- **Fail-Forward-Backfill:** Läuft eine Mission zu schnell, fügt die Runtime automatisch **2-3
  Zusatzszenen** ein (z. B. unerwartete Patrouille, Gegenangriff, lokale Komplikation am Ziel), bis
  der Zielkorridor **12 (Core) bzw. 14 (Rift) Szenen** erreicht ist. Diese Szenen nutzen bevorzugt
  offene Twists oder Fraktionsinterventionen, damit die Spannung organisch steigt.
- **Stressaufbau:** In den Backfill-Szenen erhöht jede Verzögerung den Stress, damit Undercover
  nicht zur risikofreien Abkürzung wird.

### Mission Economy

**Verbindliche Formel (Core und Rift):**

`Belohnung = Basiswert(Risiko) × Ergebnis-Multiplikator × Seed-Multi × Hazard-Pay`

| Risiko | Basiswert (CU) |
| ------ | -------------- |
| Low    | 400            |
| Mid    | 500            |
| High   | 600            |

| Ergebnis       | Multiplikator | Beispiel (Mid, keine Seeds, kein Hazard) |
| -------------- | ------------- | ---------------------------------------- |
| Fail           | 0.3           | 150 CU                                   |
| Teil-Erfolg    | 0.6           | 300 CU                                   |
| Erfolg         | 1.0           | 500 CU                                   |
| Erfolg + Bonus | 1.2           | 600 CU                                   |

- **Seed-Multi:** `min(1,6; 1 + 0,2 × offene Seeds)` (Minimum 1,0, Cap 1,6).
- **Hazard-Pay:** Solo/Buddy-Teams (< 3 Agenten) erhalten **1,5×**.
- **Bonusziele:** Optionale Zusatzaufgaben als Festbetrag oder Multiplikator-
  Aufschlag; Quelle im Debrief dokumentieren.

> **Abgrenzung:** Die ältere Kurzformel **10 × Spielerlevel CU** ist
> ausschließlich eine **Budget-Faustregel für die Kampagnenplanung** und
> ersetzt keine Ingame-Auszahlung. Verbindlich für Debriefs und Runtime ist
> die obige dynamische Formel. Details im
> [CU-Modul](../systems/currency/cu-waehrungssystem.md#core-ops-belohnungen).

Die Runtime verwendet dieselben Werte, wenn kein konkreter Betrag im Debrief
übergeben wird.

## Automatischer Mission Seed

**Scope-Regel:** Der gezogene Seed bestimmt **Epoche, Setting und
Hintergrundszenario** der Episode. Das Briefing scoped den konkreten Auftrag auf
die **aktuelle Arc-Phase** herunter: Frühe Missionen (1–2) bekommen einen kleinen
Ausschnitt des Szenarios als Ziel, späte Missionen (6–10) rücken ins Zentrum des
Geschehens. Behandle Seeds nicht als 1:1-Aufträge — sie sind der **Horizont**,
nicht das Briefing.

Dieses Start-Tool zieht zu Beginn einer Sitzung je einen Eintrag aus drei Listen
und kombiniert sie zu einem knappen Briefing. KI-SL würfelt verdeckt und stellt das Ergebnis vor.
Bei der Umsetzung orientiert sich die KI an der **Briefing-Vorlage (Layered)**
aus dem Toolkit: Zeit & Ort, eine mögliche Abnormalität und die Risikostufe werden
im ersten Briefing genannt. **Der gezogene Twist bleibt vorerst geheim** und dient
als Notiz für den Spielleiter, bis im Laufe der Mission passende Hinweise auftauchen.
Die Tonalität der Generatoren bleibt im ZEITRISS-Standard bewusst hart,
erwachsen und direkt. Reale Einschnitte dürfen klar benannt werden; die
Spielleitung bleibt filmisch, respektvoll und ohne unnötigen Voyeurismus.

> **Preserve:** Beinahe-Katastrophen, die in der echten Geschichte NICHT passiert
> sind. Die Spieler **verhindern** sie. Gegner versuchen sie auszulösen.
> **Trigger:** Echte Katastrophen, die passiert SIND. Die Spieler **stellen sicher**,
> dass sie stattfinden. Gegner versuchen sie zu verhindern.
> Beide dienen dem gleichen Ziel: Geschichte wahren = stabile Zeitlinie schützen.
> Die Generatoren halten separate Pools für klare Themen, aber der Standardmodus
> `mixed` darf zwischen beiden rotieren. Der aktive Seed-Typ wird pro Mission als
> `campaign.seed_source` markiert. Alle Twists beziehen sich auf
> **Nicht-ITI-Fraktionen** (siehe `kampagnenuebersicht.md`).

```yaml
preserve_pool:
  - id: "P-0001"
    year: 1983
    place: "Westeuropa"
    title: "Able Archer Nuclear Scare"
    objective: "Sorge, dass UdSSR-Frühwarnung NATO-Übung nicht als Erstschlag wertet."
    antagonist: "KGB-Zeitagent"
    antagonist_goal: "Launch-Codes manipulieren, NATO-Übung zum echten Erstschlag eskalieren"
    twist: "Ein KGB-Zeitagent will Launch-Codes manipulieren."
  - id: "P-0002"
    year: 1979
    place: "BRD Elbe"
    title: "Brunsbüttel Blockage"
    objective: "Stabilisiere Reaktor Brunsbüttel, verhindere Kühlverlust."
    antagonist: "Öko-Zeitgruppe"
    antagonist_goal: "Ventile sabotieren, Reaktorkatastrophe als politisches Warnsignal provozieren"
    twist: "Öko-Zeitgruppe sabotiert Ventile, will Katastrophe als Warnsignal."
  - id: "P-0003"
    year: 1995
    place: "Barentssee"
    title: "Norway Rocket Alert"
    objective: "Halte Jelzins Atomkoffer geschlossen - Fehlsignal darf nicht eskalieren."
    antagonist: "Abtrünniger NATO-Techniker"
    antagonist_goal: "Falsche Telemetrie einspeisen, russischen Nuklear-Gegenschlag auslösen"
    twist: "Abtrünniger NATO-Tech setzt falsche Telemetrie."
  - id: "P-0004"
    year: 2000
    place: "Sydney"
    title: "Olympics Kontaminationsalarm"
    objective: "Stabilisiere Kontaminationsalarm bei Olympia 2000, sichere Proben und Ablauf."
    antagonist: "Zeitreisende Extremisten"
    antagonist_goal: "Laborstörung verursachen, Kontaminationsproben verschwinden lassen, Olympia sabotieren"
    twist: "Zeitreisende Extremisten verursachen Laborstörung, Proben verschwinden im Maskottchen-Lager."
  - id: "P-0005"
    year: 2001
    place: "Genf"
    title: "CERN Magnet Quench"
    objective: "Stabilisiere Magneten, verhindere Vakuum-Implosion."
    antagonist: "Zeitkartell-Saboteur"
    antagonist_goal: "Nano-Sabotage an LHC-Magneten platzieren, Vakuum-Implosion auslösen"
    twist: "Nano-Sabotage von Zeitkartell platziert."
  - id: "P-0006"
    year: 2003
    place: "Nordatlantik"
    title: "Near-Collision AC759"
    objective: "Lenke zwei Flugrouten auseinander (TCAS-Glitch)."
    antagonist: "Fremdfraktion-Funkstörer"
    antagonist_goal: "Lotsen per Funk stören, Midair-Collision zweier Flugzeuge erzwingen"
    twist: "Fremdfraktion stört Lotsen per Funk."
  - id: "P-0007"
    year: 2009
    place: "Hudson River"
    title: "US 1549 Ditching"
    objective: "Verhindere Sabotage an US Airways 1549 — Gegner wollen den Gleitflug scheitern lassen."
    antagonist: "KonTra-Fraktion"
    antagonist_goal: "Rettungsschlepper sabotieren, Wasserung von US Airways 1549 zum tödlichen Absturz machen"
    twist: "KonTra-Fraktion will Rettungsschlepper sabotieren."
  - id: "P-0008"
    year: 2013
    place: "Fukushima"
    title: "Post-Leak Heat Spike"
    objective: "Vermeide sekundäre Wasserstoff-Explosion."
    antagonist: "Schurken-Agent"
    antagonist_goal: "Kühlpumpen abdrehen, sekundäre Wasserstoff-Explosion in Fukushima auslösen"
    twist: "Schurken-Agent dreht Kühlpumpen ab."
  - id: "P-0009"
    year: 2014
    place: "Schweiz"
    title: "Gotthard Tunnel Fire"
    objective: "Lösche Brand, bevor Munitionslaster detoniert."
    antagonist: "Verkleideter Saboteur"
    antagonist_goal: "Als Feuerwehrmann getarnt Löscharbeiten sabotieren, Munitionslaster zur Detonation bringen"
    twist: "Saboteur tarnt sich als Feuerwehrmann."
  - id: "P-0010"
    year: 2016
    place: "Moskau"
    title: "Domodedowo Near-Strike"
    objective: "Umleite Drohne vom Jet-Triebwerk ab."
    antagonist: "Zeitkartell-Techniker"
    antagonist_goal: "Time-Beacon testen, Drohne ins Jet-Triebwerk lenken und Flugzeugabsturz verursachen"
    twist: "Zeitkartell testet einen Time-Beacon, der eine Drohne anzieht."
  - id: "P-0011"
    year: 1962
    place: "Karibik"
    title: "Black Saturday"
    objective: "Funkspruch von B-59-Sub unterdrücken - kein Torpedo-Launch."
    antagonist: "Gegnerischer Funkagent"
    antagonist_goal: "Morse-Code fälschen, Torpedo-Launch des B-59-U-Boots provozieren"
    twist: "Ein gegnerischer Agent fälscht den abgehörten Morse-Code."
  - id: "P-0012"
    year: 1983
    place: "Vologda"
    title: "Oko False Alarm"
    objective: "Stütze Oberst Petrow bei Fehlalarm-Entscheidung."
    antagonist: "Abtrünniger Techniker"
    antagonist_goal: "Satellitendaten manipulieren, Petrows Fehlalarm-Erkennung sabotieren und Atomschlag auslösen"
    twist: "Abtrünniger Techniker manipuliert Satellitendaten."
  - id: "P-0013"
    year: 1977
    place: "Leningrad"
    title: "Dam Safety Drill"
    objective: "Verhindere Defekt am Sankt-Petersburg-Tidenwehr."
    antagonist: "Hydraulik-Saboteur"
    antagonist_goal: "Hydrauliksystem mit Mikro-Algen fluten, Tidenwehr-Defekt und Überschwemmung auslösen"
    twist: "Saboteur flutet Hydraulik mit Mikro-Algen."
  - id: "P-0014"
    year: 1987
    place: "Chicago"
    title: "Metra Bridge Collapse"
    objective: "Stabilisiere Träger, verhindere Zugabsturz."
    antagonist: "Chrono-Rebellen"
    antagonist_goal: "Material-Fatigue-Gun an Brückenträgern testen, Zugabsturz verursachen"
    twist: "Chrono-Rebellen testen Material-Fatigue-Gun."
  - id: "P-0015"
    year: 1991
    place: "Manila"
    title: "Pinatubo Lahar"
    objective: "Evakuiere Tiefland vor Schlammlawine."
    antagonist: "Rivalen-Hacker"
    antagonist_goal: "Wettersatellit hacken, Fehlauswertung erzeugen und Evakuierung verhindern"
    twist: "Rival nutzt Wettersat-Hack für Fehlauswertung."
  - id: "P-0016"
    year: 2007
    place: "Genf"
    title: "SwissAir Fuel Leak"
    objective: "Versenke Austritt im Vorfeld, verhindere Start."
    antagonist: "Nano-Bohrer-Saboteur"
    antagonist_goal: "Mit Nano-Bohrer Treibstoffleitung anbohren, Flugzeugstart zur Katastrophe machen"
    twist: "Gegenspieler hat Nano-Bohrer."
  - id: "P-0017"
    year: 1943
    place: "London"
    title: "V-Bomb DUD"
    objective: "Stelle Sicherung defekter V-1 wieder her - Blindgänger darf nicht detonieren."
    antagonist: "Zeit-Dieb"
    antagonist_goal: "Steuerservos der V-1 stehlen, Blindgänger zur Detonation bringen"
    twist: "Zeit-Dieb will Steuerservos klauen."
  - id: "P-0018"
    year: 1968
    place: "Thule"
    title: "Broken Arrow Ice"
    objective: "Stoppe Plutoniumstaubverwehung nach B-52-Crash."
    antagonist: "Chrono-Schmuggler"
    antagonist_goal: "Isotopen-Beweis stehlen, Plutoniumverseuchung vertuschen und eskalieren lassen"
    twist: "Chrono-Smuggler will isotopen Beweis stehlen."
  - id: "P-0019"
    year: 1989
    place: "Montreal"
    title: "Hydro-Québec Blackout"
    objective: "Stütze Stromnetz gegen geomagnetischen Sturm."
    antagonist: "Zeitkartell-Operator"
    antagonist_goal: "Sonnensturm per Zeitspule verstärken, flächendeckenden Blackout auslösen"
    twist: "Zeitkartell verstärkt den Sonnensturm per Zeitspule."
  - id: "P-0020"
    year: 2012
    place: "CERN"
    title: "LS1 Magnet Quench"
    objective: "Verhindere Quench-Kaskade im LHC-Ring."
    antagonist: "Firmware-Saboteur"
    antagonist_goal: "Helium-Sensor-Firmware austauschen, Quench-Kaskade im LHC-Ring auslösen"
    twist: "Saboteur tauscht Helium-Sensor-Firmware."
  - id: "P-0021"
    year: 1971
    place: "Utah"
    title: "Apollo 15 Abort Call"
    objective: "Schütze Apollo-15-Guidance vor Manipulation — Gegner stören Deep-Space-Net, Landung darf nicht scheitern."
    antagonist: "Deep-Space-Net-Störer"
    antagonist_goal: "Deep-Space-Net stören, Apollo-15-Mondlandung zum Absturz bringen"
    twist: "Antagonist stört Deep-Space-Net."
  # P-0022: reserviert (entfernt wegen Balancing)
  - id: "P-0023"
    year: 1972
    place: "München"
    title: "Olympia Bomb Scare"
    objective: "Entschärfe zweite Bombe im Olympiastadion."
    antagonist: "Chrono-Cell"
    antagonist_goal: "Security vom Olympiastadion weglocken, zweite Bombe zur Detonation bringen"
    twist: "Chrono-Cell lockt Security weg."
  - id: "P-0024"
    year: 1983
    place: "Kapstadt"
    title: "Cape Town Chlorine Leak"
    objective: "Schließe Ventil, verhindere Gaswolke."
    antagonist: "Zeit-Masken-Saboteur"
    antagonist_goal: "Als Ingenieur getarnt Chlorventil offen halten, tödliche Gaswolke freisetzen"
    twist: "Saboteur mit Zeit-Maske als Ingenieur."
  - id: "P-0025"
    year: 2014
    place: "Jakarta"
    title: "QZ8501 Stall"
    objective: "Übermittle AoA-Reset-Routine an Piloten."
    antagonist: "Sensor-Dieb"
    antagonist_goal: "Gestohlene Sensoren einschleusen, Falschmeldungen liefern und Flugzeugabsturz verursachen"
    twist: "Gestohlene Sensoren liefern Falschmeldungen."
  - id: "P-0026"
    year: 1978
    place: "Soweto"
    title: "Dam Burst Near-Miss"
    objective: "Stütze Flutwehr."
    antagonist: "Chrono-Konvertit (Ingenieur)"
    antagonist_goal: "Flutwehr von innen schwächen, Dammbruch und Überschwemmung auslösen"
    twist: "Engineer ist Chrono-Konvertit."
  - id: "P-0027"
    year: 2008
    place: "Large Hadron Test"
    title: "Kryo-Leitungsriss"
    objective: "Riss abdichten, Helium-Austritt verhindern."
    antagonist: "Rivalen-Agent"
    antagonist_goal: "Mikro-Schwarzes-Loch als Beweis sichern, Kryo-Leitungsriss eskalieren lassen"
    twist: "Rivale will Mikro-Schwarzes-Loch als Beweis sichern."
  - id: "P-0028"
    year: 1999
    place: "Y2K"
    title: "Bank Core Patch"
    objective: "Installiere Y2K-Patch im Bankrechenzentrum vor Mitternacht."
    antagonist: "Zeitkult"
    antagonist_goal: "Backups sabotieren, weltweiten Finanzcrash durch Y2K-Bug auslösen"
    twist: "Zeitkult sabotiert Backups, will weltweiten Finanzcrash auslösen."
  - id: "P-0029"
    year: 2019
    place: "Moskau"
    title: "Radiological Isotope Fire"
    objective: "Kühle Lager, verhindere Strahlungswolke."
    antagonist: "Isotopen-Dieb"
    antagonist_goal: "Radioaktive Isotope stehlen, Lagerbrand als Ablenkung nutzen und Strahlungswolke in Kauf nehmen"
    twist: "Gegenseite will isotopen Diebstahl."
  - id: "P-0030"
    year: 1956
    place: "London"
    title: "Tower Bridge Near-Collapse"
    objective: "Entlaste Hängekabel vor Resonanz."
    antagonist: "Chrono-Gambler"
    antagonist_goal: "Resonanzkatastrophe an Tower Bridge provozieren, auf Einsturz-Wette kassieren"
    twist: "Chrono-Gambler setzt auf Einsturz-Wette."

> Alle Twists im folgenden Trigger-Pool stammen von **Nicht-ITI-Fraktionen**.
trigger_pool:
  - id: "T-0001"
    year: 1986
    place: "Ukraine"
    title: "RBMK Turbine Test"
    objective: "Stelle sicher, dass Reaktor 4 während Nachtprobe destabilisiert."
    antagonist: "Fremdfraktion-Zelle"
    antagonist_goal: "SCRAM frühzeitig auslösen, Reaktorunfall verhindern"
    twist: "Zelle einer Fremdfraktion versucht SCRAM früh."
  - id: "T-0002"
    year: 2003
    place: "USA Orbit"
    title: "STS-107 Re-Entry"
    objective: "Blockiere EVA-Inspection, Shuttle muss verglühen."
    antagonist: "Helios-Techniker"
    antagonist_goal: "Außerplanmäßigen EVA-Check im MCC Houston erzwingen, Shuttle-Zerstörung verhindern"
    twist: "Helios-Techniker im MCC Houston will außerplanmäßigen Check erzwingen."
  - id: "T-0003"
    year: 1912
    place: "Nordatlantik"
    title: "RMS Titanic"
    objective: "Sorge, dass Titanic trotz Warnungen Kurs hält und sinkt."
    antagonist: "Zeit-Philanthrop"
    antagonist_goal: "Titanic-Untergang verhindern, Kurs ändern lassen und Zeitlinie destabilisieren"
    twist: "Zeit-Philanthrop will Unglück verhindern, riskiert Zeitlinie."
  - id: "T-0004"
    year: 1975
    place: "China"
    title: "Banqiao Dam Burst"
    objective: "Schwäche Abfluss-Schotten während Taifun."
    antagonist: "Fremdfraktion-Spione"
    antagonist_goal: "Entlastungswehr öffnen, kontrollierten Abfluss ermöglichen und Dammbruch verhindern"
    twist: "Spione einer Fremdfraktion wollen Entlastungswehr öffnen."
  - id: "T-0005"
    year: 1961
    place: "Kongo"
    title: "Lumumba Death"
    objective: "Entferne Schutzkonvoi, Übergabe an Gegner."
    antagonist: "Fremdfraktion-Diplomat"
    antagonist_goal: "Fluchtplan für Lumumba liefern, dessen Tod verhindern"
    twist: "Diplomat einer Fremdfraktion liefert Fluchtplan."
  - id: "T-0006"
    year: 1994
    place: "Rwanda"
    title: "Presidential Crash"
    objective: "Blockiere Flughafen-Radar VHF."
    antagonist: "Fremdfraktion-UN-Team"
    antagonist_goal: "Wartungs-Override am Flughafenradar durchführen, Abschuss verhindern"
    twist: "UN-Team einer Fremdfraktion versuchen Wartungs-Override."
  - id: "T-0007"
    year: 1979
    place: "USA"
    title: "Three Mile Island"
    objective: "Unterdrücke Level-Indicator Alarm."
    antagonist: "Gegenseiten-Techniker"
    antagonist_goal: "Vent-Purge erzwingen, Kernschmelze rechtzeitig stoppen"
    twist: "Gegenseite will Vent-Purge erzwingen."
  - id: "T-0008"
    year: 1937
    place: "Lakehurst"
    title: "Hindenburg"
    objective: "Sabotiere Bodenkabel-Erdung."
    antagonist: "Fremdfraktion-Agent"
    antagonist_goal: "Anti-Elektrostatik-Graffiti aufbringen, statische Entladung verhindern und Hindenburg-Brand abwenden"
    twist: "Ein Agent einer Fremdfraktion streut Anti-Elektrostatik-Graffiti."
  - id: "T-0009"
    year: 1989
    place: "Exxon Valdez"
    title: "Bligh Reef Spill"
    objective: "Besteche Hafenlotse - Tanker läuft auf Riff."
    antagonist: "Öko-Gruppierung"
    antagonist_goal: "Radar-Ping aktivieren, Tanker rechtzeitig warnen und Ölkatastrophe verhindern"
    twist: "Öko-Gruppierung will Radar-Ping aktivieren."
  - id: "T-0010"
    year: 2011
    place: "Japan"
    title: "Fukushima Daiichi"
    objective: "Verzögere Diesel-Pump-Restart."
    antagonist: "Rivalen-Lieferant"
    antagonist_goal: "Not-Batterien liefern, Diesel-Pumpen rechtzeitig starten und Kernschmelze verhindern"
    twist: "Rival will Not-Batterien liefern."
  - id: "T-0011"
    year: 1906
    place: "San Francisco"
    title: "Great Quake Fire"
    objective: "Manipuliere Hauptwasserventile, Brand breitet sich."
    antagonist: "Feuerwehrfraktion"
    antagonist_goal: "Steam-Pumper herbeischaffen, Wasserversorgung wiederherstellen und Großbrand löschen"
    twist: "Feuerwehrfraktion bringt Steam-Pumper."
  - id: "T-0012"
    year: 2020
    place: "Beirut"
    title: "Ammonium Blast"
    objective: "Unterbinde Lagerräumung."
    antagonist: "Fremdfraktions-Hafeninspektor"
    antagonist_goal: "Lagerräumung des Ammoniumnitrats anordnen, Explosion verhindern"
    twist: "Hafeninspektor ist Fremdfraktions-Asset."
  - id: "T-0013"
    year: 2014
    place: "Donetsk"
    title: "MH17 Shootdown"
    objective: "Leite Kurs über Konfliktzone."
    antagonist: "Fremdfraktion-Fluglotse"
    antagonist_goal: "Umflug um Konfliktzone genehmigen, Abschuss von MH17 verhindern"
    twist: "Air-Traffic-Controller will Umflug genehmigen."
  - id: "T-0014"
    year: 1988
    place: "Lockerbie"
    title: "PA103 Bomb"
    objective: "Schleuse Koffer unbehelligt ein."
    antagonist: "Fremdfraktion-Gepäckscanner"
    antagonist_goal: "Bombenkoffer beim Gepäckscan entdecken, Anschlag auf PA103 verhindern"
    twist: "Baggage-Scanner arbeitet für Fremdfraktion."
  - id: "T-0015"
    year: 1815
    place: "Tambora"
    title: "Year Without Summer"
    objective: "Fördere Schachtdruck, stärke Ausbruch."
    antagonist: "Fremdfraktion-Sprengmeister"
    antagonist_goal: "Schuttkegel sprengen, Druckentlastung ermöglichen und Vulkanausbruch abschwächen"
    twist: "Agent einer Fremdfraktion will Schuttkegel sprengen."
  - id: "T-0016"
    year: 1835
    place: "Rangoon"
    title: "Ava Earthquake"
    objective: "Sabotiere Evakuierungsbrücken."
    antagonist: "Fremdfraktion-Mönch"
    antagonist_goal: "Bevölkerung frühzeitig warnen, Evakuierung ermöglichen und Opferzahl senken"
    twist: "Mönch (Fremdfraktion) warnt Bevölkerung."
  - id: "T-0017"
    year: 1883
    place: "Krakatau"
    title: "Volcanic Winter"
    objective: "Verzögere Telegraph-Warnung zu evakuieren."
    antagonist: "Fremdfraktion-Telegraphist"
    antagonist_goal: "Telegraphen-Warnung durchsenden, Küstenstädte rechtzeitig evakuieren"
    twist: "Dutch-Telegraphist ist Scout einer Fremdfraktion."
  - id: "T-0018"
    year: 1918
    place: "Boston"
    title: "Molasses Flood"
    objective: "Erwärme Tank klandestin."
    antagonist: "Fremdfraktion-Food-Agent"
    antagonist_goal: "Druckventil anbohren, Tankdruck kontrolliert ablassen und Melasseflut verhindern"
    twist: "Food-Agent einer Fremdfraktion will Druckventil bohren."
  - id: "T-0019"
    year: 1923
    place: "Tokyo"
    title: "Great Kanto Quake"
    objective: "Blockiere Löschwasserleitung."
    antagonist: "Fremdfraktion-Spione"
    antagonist_goal: "Brunnenpumpen hacken, Löschwasserversorgung wiederherstellen und Feuersturm eindämmen"
    twist: "Spione einer Fremdfraktion hacken Brunnenpumpen."
  - id: "T-0020"
    year: 1978
    place: "Jonestown"
    title: "Mass Suicide"
    objective: "Sabotiere Funkgerät, verhindere Alarm."
    antagonist: "Fremdfraktion-Journalisten"
    antagonist_goal: "Hilferuf über Funk senden, Rettungskräfte alarmieren und Massaker verhindern"
    twist: "Journalisten einer Fremdfraktion senden Hilferuf."
  - id: "T-0021"
    year: 1966
    place: "Aberfan"
    title: "Tip Slide"
    objective: "Schwäche Abraumdamm, Sturm erledigt Rest."
    antagonist: "Fremdfraktion-Lehrerin"
    antagonist_goal: "Risse im Abraumdamm melden, Evakuierung der Schule einleiten und Erd rutsch verhindern"
    twist: "Lehrerin (Fremdfraktion) meldet Risse."
  - id: "T-0022"
    year: 1985
    place: "Nevado del Ruiz"
    title: "Armero Tragedy"
    objective: "Manipuliere Seismo-Alarm."
    antagonist: "Fremdfraktion-Priester"
    antagonist_goal: "Eigenmächtig Evakuierung von Armero einleiten, Lahar-Katastrophe verhindern"
    twist: "Priester (Fremdfraktion) versucht Evakuierung."
  - id: "T-0023"
    year: 1999
    place: "İzmit"
    title: "Marmara Quake"
    objective: "Verzögere Katastrophenschutz-Konvoi."
    antagonist: "Fremdfraktion-NGO"
    antagonist_goal: "Boot-Sirenen verteilen, Frühwarnung ermöglichen und Opferzahl durch Tsunami senken"
    twist: "NGO-Fremdfraktion verteilt Boot-Sirenen."
  - id: "T-0024"
    year: 1971
    place: "Sylmar"
    title: "San Fernando Quake"
    objective: "Drehe Ventile für Gasleitungen auf."
    antagonist: "Fremdfraktion-Notfall-Crew"
    antagonist_goal: "Gas-Shut-Off hacken, Gasleitungen absperren und Explosionen nach Erdbeben verhindern"
    twist: "Notfall-Crew einer Fremdfraktion hackt Shut-Off."
  - id: "T-0025"
    year: 1988
    place: "Yazd"
    title: "Iran Air 655"
    objective: "Jam IFF-System."
    antagonist: "Fremdfraktion-Radar-Tech"
    antagonist_goal: "Korrekten IFF-Code senden, Identifikation als Zivilflugzeug ermöglichen und Abschuss verhindern"
    twist: "Radar-Tech (Fremdfraktion) sendet korrekten Code."
  - id: "T-0026"
    year: 2004
    place: "Phuket"
    title: "Boxing-Day Tsunami"
    objective: "Sabotiere Frühwarnboje."
    antagonist: "Ozeanische Fremdfraktion"
    antagonist_goal: "Frühwarnboje kurz vor Impakt warten, Tsunami-Warnung ermöglichen und Küstenevakuierung einleiten"
    twist: "Ozeanische Fremdfraktion wartet Sensor kurz vor Impakt."
  - id: "T-0027"
    year: 1963
    place: "Vajont"
    title: "Wave over Dam"
    objective: "Manipuliere Bergrutsch-Sprengbohrungen."
    antagonist: "Fremdfraktion-Geologin"
    antagonist_goal: "Kritische geologische Daten veröffentlichen, Stausee rechtzeitig ablassen und Flutwelle verhindern"
    twist: "Geologin einer Fremdfraktion unterschlägt Daten."
  - id: "T-0028"
    year: 1964
    place: "Alaska"
    title: "Good Friday Quake"
    objective: "Verzögere Hafen-Evakuierung."
    antagonist: "Fremdfraktion-Fischer"
    antagonist_goal: "Morsecode-Warnung senden, Hafenevakuierung beschleunigen und Tsunami-Opfer retten"
    twist: "Fischer einer Fremdfraktion sendet Morsecode."
  - id: "T-0029"
    year: 2013
    place: "Lac-Mégantic"
    title: "Crude Oil Train"
    objective: "Bremse lösen, Zug rollt."
    antagonist: "Fremdfraktion-Weichensteller"
    antagonist_goal: "Bremskeile unter die Räder legen, Zug am Rollen hindern und Explosion verhindern"
    twist: "Switchman einer Fremdfraktion legt Keil."
  - id: "T-0030"
    year: 2001
    place: "New York"
    title: "9/11"
    objective: "Sichere Boarding für Entführer & stalle NORAD-Reaktion."
    antagonist: "Fremdfraktion-Air-Marshal"
    antagonist_goal: "Entführer am Boarding hindern, richtigen Flug besetzen und Anschläge vereiteln"
    twist: "Air-Marshal einer Fremdfraktion sitzt falschen Flug."

  - id: "T-0031"
    year: 1995
    place: "Seoul"
    title: "Sampoong Collapse"
    objective: "Sabotiere Evakuierung - Einsturz muss erfolgen."
    antagonist: "Aktien-Short-Spekulanten"
    antagonist_goal: "Öffentlich vor struktureller Instabilität warnen, Gebäuderäumung erzwingen und Einsturz-Opfer verhindern"
    twist: "Aktien-Short-Spekulanten warnen vor der Instabilität."

```

Der anschließende Missionsgenerator erstellt eine **Phasenliste** mit
mindestens **30** Einträgen. Bei langen Einsätzen darf die Liste bis zu
**50** Szenen umfassen. Nutzt YAML-Gewichte, um Nebenszenen aufzufüllen
und so das Ziel zu erreichen.

_Regel:_ Eintragstexte dürfen nicht wortgleich in `objective` und `twist` stehen.
Streiche doppelte Seeds oder variiere sie.

```jsonc
{
  "twists": [
    {
      "id": "T28",
      "label": "Schallmauer-Poker",
      "effect": "Ein Düsenjäger-Testflug droht eure Infiltration zu übertönen - perfekte Tarnung oder Absturztimer?"
    },
    {
      "id": "T29",
      "label": "Parallel-Konklave",
      "effect": "Ein Doppelgänger-Team taucht auf - gleiche Ziele, andere Agenda. Rivalen, Söldner oder Backup?"
    },
    {
      "id": "T30",
      "label": "Rabies-X Outbreak",
      "effect": "Mutierte Tollwut in versiegelter Basis: Soldaten wie Zombies - Antiserum oder Flammenwerfer?"
    },
    {
      "id": "T31",
      "label": "Imperiale Schachfigur",
      "effect": "Figur wird Kronzeuge. Töten tabu, Manipulation kostet Paradoxon, Schutz macht euch zu Leibwächtern."
    },
    {
      "id": "T32",
      "label": "Kaltes Singularitätstor",
      "effect": "Gefrorener Energiepuls hält ein Mikro-Wurmloch offen - perfekter Schmuggelkanal oder tickende Uhr?"
    },
    {
      "id": "T33",
      "label": "Silencer-Protokoll",
      "effect": "HQ bricht ab, Kodex schweigt. Ihr baut eine Funkboje - bis dahin analoges Hacking und Risiko."
    },
    {
      "id": "T34",
      "label": "Orchideen-Schlüssel",
      "effect": "Keramikblüte steuert VIP-Implantate. Richtige Frequenz: Loyalität, falsche: Herzstillstand."
    },
    {
      "id": "T35",
      "label": "Sturm ★ Delta",
      "effect": "Wetter-Array von 19XX eskaliert: Hurrikan springt von 0 auf Kategorie 5. Fail-Safe liegt im Auge."
    }
  ]
}
```

Bei Missionsbeginn notiert sich die SL den Twist.
Spätestens in **Phase 3 (Aufklärung)** sollte die Spielleitung einen Hinweis aus
dem Feld `foreshadow` einbauen, damit die Wendung nicht übersehen wird.

Die folgenden Tabellen speisen den Core- und Rift-Loop mit Missionszielen.

## Missionstabellen für den Core- & Rift-Loop

Diese Tabellen liefern Zufallsziele für reguläre Operationen und für Risse.
`Objective_P` = Preserve-Variante (Spieler verhindert), `Objective_T` = Trigger-Variante (Spieler stellt sicher).

```json
{
  "CoreObjectiveTable": [
    {
      "Objective_P": "Sichere feindlichen Kommunikationsknoten für nachträgliche Code-Analyse",
      "Objective_T": "Leite Traffic um & hinterlasse interne Sabotagespur, damit Gegner sich selbst säubert"
    },
    {
      "Objective_P": "Bergung gestohlener Forschung im Originalzustand",
      "Objective_T": "Inszeniere Brand, aber extrahiere Mikrofilm zuvor für ITI"
    },
    {
      "Objective_P": "Schütze den Informanten bis zu seinem geplanten Gefängnis-Tod",
      "Objective_T": "Täusche Suizid, um Namen des Drahtziehers herauszupressen"
    },
    {
      "Objective_P": "Bewahre ChronTech-Prototyp im Archiv für spätere Patente",
      "Objective_T": "Extrahiere Schaltpläne und ersetze Gehäuse durch funktionslose Attrappe"
    },
    {
      "Objective_P": "Täusche Basisbesatzung, sammle Beweise",
      "Objective_T": "Sprenge Treibstofflager, um Beweise als \"Zufallsfund\" zu tarnen"
    }
  ]
}
```

Der SG einer Mission richtet sich allein nach der Anzahl offener Seeds. Jedes ☆ zählt als +1 SG.

```json
{
  "RiftSeedTable": [
    {
      "d24": 1,
      "Seed": "Schreie im Moor",
      "Hook": "Klagelaute im Sumpf - Ursprung ermitteln, Fluch brechen",
      "hiddenCause": "Parawesen: Todesfee (Banshee) warnt mit tödlichen Schreien vor Unheil"
    },
    {
      "d24": 2,
      "Seed": "Totenbrücke Chongqing",
      "Hook": "Geisterbus im Zeitfeld - Stau räumen, Showdown auf der Brücke",
      "hiddenCause": "Parawesen: Untoter Fahrer spukt mit verfluchtem Bus - verursacht Zeitanomalie"
    },
    {
      "d24": 3,
      "Seed": "Skinwalker-Attacke",
      "Hook": "Formwandler terrorisiert Dorf - Spuren verfolgen, Kreatur stellen",
      "hiddenCause": "Parawesen: Navajo-Hexer in Tiergestalt (Skinwalker) nimmt Rache an Eindringlingen"
    },
    {
      "d24": 4,
      "Seed": "Night Train 666",
      "Hook": "Führerloser Geisterzug - aufspringen und Blackbox sichern",
      "hiddenCause": "Parawesen: Geist des Lokführers von 1912, gebunden an entgleiste Lok (Zeitriss-Effekt)"
    },
    {
      "d24": 5,
      "Seed": "Goatman von Maryland",
      "Hook": "Monster mit Axt terrorisiert Pärchen - Teenager schützen, Bestie fassen",
      "hiddenCause": "Parawesen: mutierter Hybrid (Goatman) - entkam Labor und sinnt auf blutige Rache"
    },
    {
      "d24": 6,
      "Seed": "Wolfsplage Dacia",
      "Hook": "Gen-Rudel - Vollmond-Dorf-Horror, Serum stehlen",
      "hiddenCause": "Lykan-Virus aus Zukunftslabor"
    },
    {
      "d24": 7,
      "Seed": "Fluch des Wendigo",
      "Hook": "Wintercamp wird kannibalisch - Ritual aufdecken, Infizierte stoppen",
      "hiddenCause": "Parawesen: Wendigo-Geist (Kannibalenfluch) entfesselt unstillbaren Hunger in Menschen"
    },
    {
      "d24": 8,
      "Seed": "Chupacabra-Angriffe",
      "Hook": "Farmtiere blutleer aufgefunden - Lockvogel einsetzen, Kreatur erlegen",
      "hiddenCause": "Parawesen: unbekannter Blutsauger (Chupacabra) - reißt Vieh nachts und versetzt Dorf in Angst"
    },
    {
      "d24": 9,
      "Seed": "Ungeheuer von Loch Ness",
      "Hook": "Sonar-Sichtung im See - Tauchteam entsenden, Kreatur verfolgen",
      "hiddenCause": "Parawesen: Plesiosaurier-Monster (Nessie) durch Zeitriss in Gegenwart aufgetaucht"
    },
    {
      "d24": 10,
      "Seed": "Chrono Butcher",
      "Hook": "Serienmorde mit Frame-Sprüngen - Ermittlungsakte sichern, Butcher stellen",
      "hiddenCause": "Parakiller in Stutter-Schleife, gebunden an blutgetränkte Taschenuhr des ersten Opfers"
    },
    {
      "d24": 11,
      "Seed": "Nightcrawler",
      "Hook": "CCTV-Video zeigt Kreatur - Spurensuche einleiten, Ursprung ermitteln",
      "hiddenCause": "Parawesen: Fremdartiges Nachtwesen (Nightcrawler) - huscht durch Kamerasicht, Herkunft unbekannt"
    },
    {
      "d24": 12,
      "Seed": "Sasquatch im Yukon",
      "Hook": "Bestie greift Trapper an - Fährte verfolgen",
      "hiddenCause": "Zeitriss entlässt Mutanten-Bären"
    },
    {
      "d24": 13,
      "Seed": "Mothman-Sichtung",
      "Hook": "Unheil über Brücke - Absturz bergen",
      "hiddenCause": "Bote aus paralleler Zukunft warnt vor Brückeneinsturz"
    },
    {
      "d24": 14,
      "Seed": "Blutorden",
      "Hook": "Opfer blutleer - Kult zerschlagen",
      "hiddenCause": "Zeitkult extrahiert Energie für Riss-Stabilisierung"
    },
    {
      "d24": 15,
      "Seed": "Diablos Katakomben",
      "Hook": "Dämonische Schreie - Kultstätte schließen",
      "hiddenCause": "versiegelter Psi-Kristall bricht wieder auf"
    },
    {
      "d24": 16,
      "Seed": "Waheela-Rudel",
      "Hook": "Jäger verschwinden in arktischer Wildnis - Spur aufnehmen, Bestien ausschalten",
      "hiddenCause": "Parawesen: Urzeitliche Waheela-Wölfe dringen aus Riss - extrem aggressiv"
    },
    {
      "d24": 17,
      "Seed": "Spring-Heeled Jack",
      "Hook": "Feuerspuckender Unhold terrorisiert London - über die Dächer hetzen, Opfer schützen",
      "hiddenCause": "Parawesen: Feuerteufel springt über Dächer und versetzt London in Angst"
    },
    {
      "d24": 18,
      "Seed": "Geister-Galeere",
      "Hook": "Leuchtende Ruderer sichten - Hafen sperren, Fluch brechen",
      "hiddenCause": "Parawesen: Quantum-Sirenen hypnotisieren Seeleute - sammeln Lebensenergie"
    },
    {
      "d24": 19,
      "Seed": "Spiegelkabinett",
      "Hook": "Doppelgänger im Spiegelkabinett - Besucher verschwinden, Irrgarten sichern",
      "hiddenCause": "Parawesen: Photonik-Parasiten kopieren Besucher - Spiegelnetz dient als Portal"
    },
    {
      "d24": 20,
      "Seed": "Phantom-Katakomben",
      "Hook": "Flüsternde Stimmen unter Paris - Katakomben erkunden, Störsignal orten",
      "hiddenCause": "Parawesen: Ätherische \"Whisperer\" - Schallfeld erzeugt Massenhalluzinationen"
    },
    {
      "d24": 21,
      "Seed": "Mokele-Mbembe",
      "Hook": "Monster im Sumpf des Kongo - Expedition sichern, Kreatur einfangen",
      "hiddenCause": "Parawesen: Relikt-Dinosaurier Mokele-Mbembe - Rift-Seed wird enthüllt, Dorf bedroht"
    },
    {
      "d24": 22,
      "Seed": "Aswang-Nacht",
      "Hook": "Schwangere spurlos verschwunden - Dorf patrouillieren, fliegende Hexe stellen",
      "hiddenCause": "Parawesen: Vampir-Hexe (Aswang) ernährt sich von Ungeborenen im Dorf"
    },
    {
      "d24": 23,
      "Seed": "Thunderbird-Sichtung",
      "Hook": "Kind von Riesenvogel entführt - Nest finden, Kreatur sichern",
      "hiddenCause": "Parawesen: Donneradler (Thunderbird) entfacht Stürme und entführt Kinder"
    },
    {
      "d24": 24,
      "Seed": "Jersey Devil",
      "Hook": "Flügelschlag über Pine Barrens - Flugbahn analysieren, Nest zerstören",
      "hiddenCause": "Para-Kreatur (Loop-Marker) kreist um Kupfer-Ei im Wald, terrorisiert Siedler"
    }
  ]
}
```

## Missions-Generator: Kleine Aufträge und Dilemmata {#missions-generator}

Nicht jede Session ist ein großes Story-Kapitel - manchmal möchten die Spieler im freien Spiel einen
kurzen Auftrag angehen oder euer KI-SL improvisiert einen Nebenquest. Der Missions-Generator liefert
schnelle **Missionsideen** mit einem eingebauten Twist oder Dilemma, damit auch kleine Einsätze
dramatisch und interessant verlaufen.

### Load-out-Pack-Generator

| Pack            | Inhalt                                                                      | CU-Preis |
| --------------- | --------------------------------------------------------------------------- | -------- |
| **Stealth-Kit** | Chamäleon-Overall, Geräuschdämpfer-Set, Mini-Holo-Bypass, Nano-Kabel (20 m) | 950 CU   |
| **Heavy-Ops**   | Smart-Assault-Rifle, Sub-Derm-Kevlar, Adren-Shot ×2, Flash-Charges ×3       | 1 350 CU |
| **Tech-Recon**  | Quanten-Sniffer-Rig, Drohne "Pixie", EMP-Patch ×2, Data-Spike-Protokoll     | 1 100 CU |

_SL-Tipp_: Jede zusätzliche Sonderausrüstung erhöht das Missionsbudget; nicht verwendete CU fließt in Belohnungen.

### Missionstypen

Diese Übersicht fasst die gängigen Einsatzarten zusammen. Der Schwerpunkt liegt auf realen
Schauplätzen, heimlichen Zugriffszielen und subtilen Zeitinterventionen. Relikte und Artefakte tauchen nur
selten automatisch auf, vergleichbar mit legendären Funden. Spieler können ihr Auftreten nicht
gezielt beeinflussen. Die Missionstypen gliedern sich in fünf Kategorien:

- **Schutzaufnahme/Evakuierung** - Zielpersonen aus Gefahrenlagen herausführen und sichern.
- **Einflüstern** - Einfluss auf NSCs durch Täuschung oder Manipulation.
- **Verdunkeln** - Spuren verwischen und Beweise stehlen.
- **Verhindern** - Anschläge, Putsche oder Deals stoppen.
- **Dokumentieren** - Geheime Beweise für das ITI sichern.

Kombiniert die Tabellen nach Belieben und erstellt eure eigenen Einsätze. Für
größere Handlungsbögen könnt ihr mehrere Aufträge verbinden oder den
[Arc-Baukasten](kampagnenstruktur.md#arc-baukasten-und-episodenstruktur) aus Modul 6
nutzen.

Wählt jeweils eine Option aus **Auftrag**, **Schauplatz** und **Twist**:

- **Auftrag:**
  1. Eskortiert/Schützt **X**.
  2. Rettet/Befreit **X**.
  3. Stehlt/Beschafft **X**.
  4. Zerstört/Sabotiert **X**.
  5. Erkundet/Untersucht **X**.
  6. Vermittelt/Verhandelt zwischen **X** und **Y**.

- **Schauplatz/Epoche:**
  1. Auf einem **Kriegsschauplatz** (Schlacht, Belagerung o. Ä.).
  2. An einem **Königshof** oder Regierungssitz.
  3. In einer **kleinen Ortschaft** oder Wildnis.
  4. In einem **Forschungslabor** oder einer Werkstatt.
  5. In einer **abgeschirmten Nullzone** fernab der regulären Zeit.
  6. Während eines bedeutenden **historischen Ereignisses** (Krönung, Attentat, Naturkatastrophe…).
  7. Bei einer **geheimen Versammlung unter ziviler Fassade** (Zirkel, Loge, schwarze Klinik oder Katakombe).
  8. In einer **Megakon-Anlage mit getarntem Hochsicherheits-Untergeschoss** (Promenade oben, Sperrtrakt unten).

- **Twist/Dilemma:**
  1. Jemand, den ihr schützen oder dem ihr helfen sollt, ist **nicht der, der er zu sein scheint** -
     und verrät euch vielleicht.
  2. Die **erfolgreiche Erfüllung** des Auftrags **verändert die Geschichte gefährlich** (Dilemma:
     Auftrag ausführen oder scheitern lassen?).
  3. **Moralisches Dilemma:** Ihr könnt **nicht alle retten** oder zufriedenstellen - wen bevorzugt
     ihr, wen lasst ihr im Stich?
  4. Der Auftrag wird **von einer rivalisierenden Gruppe** ebenfalls verfolgt - ein Wettlauf gegen
     konkurrierende Zeitreisende entbrennt.
  5. Ein **temporales Phänomen** erschwert alles: Zeitstürme, Anachronismus-Erscheinungen etc.
     treten auf.

Direkte Begegnungen mit eigenen Versionen sind ein starker dramaturgischer
Kniff, aber kein Standardbestandteil des Spiels. Sie kommen nur zum Einsatz,
wenn alle Spieler dem ausdrücklich zustimmen, und selbst dann höchstens als
seltene Ausnahme. Oft genügt es, die Agenten an einen früheren Einsatzort
zurückkehren zu lassen, um dort Hinweise auf ihr zukünftiges Handeln zu finden -
ohne sich selbst unmittelbar zu treffen.

Ihr könnt natürlich alle Elemente nach Belieben kombinieren. Wichtig ist, dass fast **jeder Auftrag
mit einem Twist** deutlich interessanter wird. So werden selbst Nebenmissionen zu denkwürdigen
Episoden und nicht bloß "Hole X, bringe Y".

**Optional - Belohnungs-Generator:** Ebenso könnt ihr auswürfeln oder wählen, welche **Belohnung
oder Konsequenz** eine Mission für die Helden bereithält (je nachdem, wie erfolgreich sie sind):

- **Belohnung/Ergebnis:**
  1. **Seltener Fund:** Die Gruppe erbeutet ein wertvolles Relikt oder technisches Gerät
     (historisch oder futuristisch), das neue Möglichkeiten eröffnet.
  2. **Wissen & Aufklärung:** Durch den Auftrag erhalten sie entscheidende Informationen oder lüften
     ein Geheimnis, das im weiteren Verlauf der Kampagne hilft.
  3. **Ansehen & Verbündete:** Ihr Erfolg verschafft ihnen Ansehen und neue Alliierte - z. B.
     Dankbarkeit einer geretteten Person oder gar einer Fraktion (vielleicht winkt eine Beförderung im
     ITI oder ein Bündnis mit den Zeitrebellen von _Tempus Liber_).
  4. **Technologischer Vorteil:** Als Lohn stellt man ihnen neue Ausrüstung oder experimentelle
     Technik zur Verfügung (etwa ein verbessertes Zeitreise-Gadget oder Unterstützung durch das HQ).
  5. **Stabilisierte Zeit:** Ihr Eingreifen bewahrt den Verlauf der Geschichte und rettet
     Unschuldige - eine ideelle Belohnung. (Möglicherweise stellt sich sogar ein kleiner positiver
     Schmetterlingseffekt ein, der den Helden zugutekommt.)
  6. **Neue Erkenntnisse:** Anstatt reicher zu werden, stoßen sie auf einen Hinweis zu einem
     größeren Rätsel. Ihr Erfolg enthüllt den nächsten, noch größeren Auftrag - eine "Belohnung" in Form
     eines neuen Abenteuers, das auf sie wartet.

### Generator Guard {#generator-guard}

```pseudo
# Pseudocode: passendes Pool ziehen
# Pool-Eintraege sind inspirierende Seeds, KEINE Pflicht-Vorlage: die KI-SL waehlt
# EINEN als Ausgangspunkt und variiert/erfindet Schauplatz, Layout und Eskalation
# passend zu Epoche und Auftrag frei weiter - niemals woertlich uebernehmen.
SCHAUPLATZ_POOLS = {
    "heist":     heist_pool,
    "black_ops": black_ops_pool,
    "future":    future_pool,
    "faction_op": faction_op_pool,   # mittlerer Stakes-Layer
}

if mission_type in SCHAUPLATZ_POOLS:
    # Run-Schauplatz (Anlage/Zirkel/Klinik/Forscher/Megakon)
    seed = random.choice(SCHAUPLATZ_POOLS[mission_type])
elif mission_type == "preserve":
    seed = random.choice(preserve_pool)
else:
    seed = random.choice(trigger_pool)
```

## Arc-Generator: Große Missionen {#arc-generator}

Manchmal soll eine Mission mehr sein als ein kurzer Auftrag. Dieser Generator liefert Anregungen für
ganze Handlungsbögen. Kombiniert je einen Eintrag aus **Bedrohung**, **Schlüsselort** und
**Finale Wendung** und baut darum herum eure große Story.

Ein einzelnes historisches Ereignis lässt sich auch in mehrere Einsätze
aufteilen. Teilt eine Katastrophe chronologisch auf - zum Beispiel
Vorbereitungen, erster Angriff, Eskalation und Nachspiel. Jede Etappe bildet
eine Mission, sodass ein kompletter Arc zehn Szenenfolgen derselben
Zeitperiode umfasst.

- **Bedrohung:**
  1. Ein Megakonzern missbraucht Zeittechnologie für eigene Machtziele.
     - epochTag: "2080er MegaCorp-Krise"
     - historyHook: "nutzt die Wirtschaftskrise 2082 für verdeckte Übernahmen"
  2. Fanatische Kultisten wollen eine alternative Zeitlinie herbeiführen.
     - epochTag: "mittelalterlicher Aberglaube"
     - historyHook: "schürt Hexenpanik in Salem 1692"
  3. Ein außer Kontrolle geratenes Experiment droht die Realität zu zerreißen.
     - epochTag: "2030er Quantenlabors"
     - historyHook: "verbirgt eine Fehlkalibrierung im CERN 2035"
  4. Eine versteckte Fremdfraktion plant, die Menschheit aus der Geschichte zu löschen.
     - epochTag: "präkolumbisches Südamerika"
     - historyHook: "manipuliert Inka-Sonnenkulte für Opferrituale"
  5. Ein rivalisierendes Zeitreise-Team sabotiert gezielt die Einsätze der Helden.
     - epochTag: "kalter Krieg"
     - historyHook: "tarnt sich als KGB-Sondereinheit 1960"
  6. Ein fehlgeschlagenes Zeitexperiment reißt ganze Regionen aus der Realität.
     - epochTag: "Cholera-Hysterie 1892 Hamburg"
     - historyHook: "lockt die Bevölkerung mit Heilversprechen in den Zeitriss"

- **Schlüsselort:**
  1. Geheimlabor in einem unterirdischen Komplex.
  2. Monumentale Ruinen einer vergangenen Hochkultur.
  3. Futuristische Metropole jenseits des bekannten Zeitalters.
  4. Verbotener Tempel, der in mehreren Epochen gleichzeitig existiert.
  5. Raumstation am Rand eines instabilen Zeittors.
  6. Verborgenes Hauptquartier der Gegenspieler mitten in der Gegenwart.

- **Finale Wendung:**
  1. Der scheinbare Verbündete entpuppt sich als Drahtzieher der Krise.
  2. Das Relikt, das alles retten soll, verursacht erst recht Chaos.
  3. Die Helden müssen ein persönliches Opfer bringen, um die Zeit zu heilen.
  4. Eine andere Fraktion kommt ihnen zuvor und dreht den Spieß um.
  5. Die Mission führt zu einer komplett neuen Zeitlinie mit ungewissem Ausgang.

6. Die Helden erkennen, dass ihre Mission nur ein Ablenkungsmanöver für einen verborgenen Gegenspieler
   war.

### Heist Pool {#heist_pool}

Dieser Pool liefert Einbruchs- und Beschaffungs-Runs gegen gesicherte Ziele -
konkrete Schauplätze mit Etagen, Zugängen und einem klaren Punkt, an dem die
stille Operation in einen lauten Kampf kippt. Die Einträge sind **inspirierende
Anreger, nicht erschöpfend** - die KI-SL nimmt einen als Funken und erfindet
den Schauplatz passend zu Epoche und Auftrag frei weiter.

```yaml
heist_pool:
  - id: safecrack_demo
    schauplatz: "Privattresor unter einem unscheinbaren Stadt-Anwesen - hinter dem Weinkeller eine gepanzerte Schließanlage"
    layout: "Erdgeschoss als zivile Fassade, ein getarnter Lastenaufzug führt zwei Etagen in die Hochsicherheits-Tiefe"
    wachen: "Privater Sicherheitsdienst mit Hundestreife oben, biometrische Schleusen und ein Wachraum unten"
    escalation: "Still bis der Tresor-Seismograf anschlägt - dann Schott-Lockdown und Verstärkung über den Aufzug"
  - id: tunnel_bypass
    schauplatz: "Stillgelegter U-Bahn-Schacht, der unter einem Banktresor entlangführt"
    layout: "Drei Tunnelebenen, eine eingestürzte Sektion als Engstelle, Durchbruch direkt unter dem Tresorboden"
    wachen: "Wartungsdrohnen auf Schiene, Bewegungsmelder an jedem Schott, oben patrouillierende Bankwache"
    escalation: "Still bis der Durchbruch-Bohrer Vibration auslöst - dann Flutschotts, Drohnenschwarm, Funkstörung"
  - id: crypt_conclave
    schauplatz: "Geheimer Zirkel tagt in einer Krypta unter einer alten Kapelle - Reliquienschreine als Datenverstecke"
    layout: "Krypta über Katakomben-Gänge erreichbar, ein Hauptgewölbe mit Ritualtisch, mehrere blinde Seitennischen"
    wachen: "Vermummte Logenbrüder, ein bewaffneter Türsteher pro Gang, versteckte Kameras in den Heiligenfiguren"
    escalation: "Still solange ihr als Zirkel-Gast durchgeht - ein falsches Losungswort und die Gänge werden zur Falle"
  - id: vault_under_estate
    schauplatz: "Kunstsammler-Villa mit getarntem Hochsicherheits-Untergeschoss hinter der Bibliothek"
    layout: "Repräsentative Beletage, eine Drehwand öffnet den Abstieg zu einem klimatisierten Panzergewölbe"
    wachen: "Diener und Gäste als Tarnung, unten zwei Techniker plus Laser-Gitter und Gewichtssensoren"
    escalation: "Still während des Empfangs - sobald ein Exponat fehlt, Panik oben und Lockdown des Gewölbes unten"
  - id: archive_lift
    schauplatz: "Konzern-Aktenarchiv, dessen oberste Etage ein getarntes Daten-Backup im Keller verbirgt"
    layout: "Sieben Bürogeschosse als Fassade, ein Notfall-Schacht führt zum abgeschotteten Serverraum unter dem Fundament"
    wachen: "Nachtreinigung und ein Pförtner oben, biometrischer Doppelschlüssel und ein Sicherheitsmann unten"
    escalation: "Still bis ein Zugriffslog Alarm meldet - dann Stahltüren, Notstrom-Dunkelheit, Sperrung des Schachts"
  - id: gala_grab
    schauplatz: "Wichtiges Bieter-Treffen in einem Hotel-Ballsaal - das eigentliche Ziel liegt im Backstage-Tresorzimmer"
    layout: "Ballsaal mit Bühne, dahinter Künstlergänge, eine bewachte Tür zum improvisierten Auktions-Tresor"
    wachen: "Türsteher mit Gästeliste, mobile Bodyguards der Bieter, ein Tresorwärter mit Funkanbindung"
    escalation: "Still während der Versteigerung - eine ausgelöste Alarmtaste und das Treffen wird zur Geiselnahme"
```

### Black-Ops Pool {#black_ops_pool}

Verdeckte Zugriffe gegen menschliche Ziele und Anlagen - leise rein, Auftrag
abarbeiten, raus, bevor jemand merkt, dass ihr da wart. Jeder Eintrag nennt den
Kipppunkt, ab dem Tarnung nicht mehr trägt. Auch hier gilt: **Anreger, nicht
erschöpfend** - die KI-SL variiert frei statt wörtlich zu übernehmen.

```yaml
black_ops_pool:
  - id: night_insertion
    schauplatz: "Schwarze Klinik in einem Hinterhof-Trakt - illegale Eingriffe hinter einer harmlosen Praxis-Front"
    layout: "Praxis-Empfang als Tarnung, ein abgeschlossener OP-Flügel mit Aufwachräumen und einem Patientenarchiv im Keller"
    wachen: "Pflegepersonal mit Schweigepflicht, ein Sicherheitsmann am OP-Flügel, Kameras über jeder Liege"
    escalation: "Still bis ein Monitor-Alarm losgeht - dann Riegel auf dem OP-Flügel und ein Notruf an externe Schläger"
  - id: asset_wipe
    schauplatz: "Aktenlager eines Strohfirmen-Büros, in dem belastende Beweise verschwinden sollen"
    layout: "Großraumbüro, ein Serverschrank im Nebenraum, der eigentliche Beweisordner liegt im Chef-Safe dahinter"
    wachen: "Nachtwächter mit Rundgang, Bewegungsmelder im Flur, eine verschlüsselte Alarmleitung zur Zentrale"
    escalation: "Still bis der Safe geöffnet wird - dann stille Alarmierung und ein Abfangteam riegelt die Etage ab"
  - id: scientist_lift
    schauplatz: "Wohnkomplex, in dem eine Forscherin gegen ihren Willen festgehalten wird - Exfiltration unter Gegenwehr"
    layout: "Vier Stockwerke, die Forscherin im obersten Apartment, Treppenhaus und ein einzelner Aufzug als Fluchtwege"
    wachen: "Zwei Bewacher in der Wohnung, ein Posten im Foyer, eine Streife im Innenhof"
    escalation: "Still bis der Posten den Wechsel verpasst meldet - dann Hof-Abriegelung und ein Verfolgerteam im Treppenhaus"
  - id: meeting_storm
    schauplatz: "Konspiratives Treffen in einer Lagerhalle, das gestürmt und unterbrochen werden muss"
    layout: "Offene Halle mit Verladerampe, ein abgetrennter Besprechungs-Container in der Mitte, Galerie unter dem Dach"
    wachen: "Bewaffnete Begleiter der Teilnehmer, Späher auf der Galerie, ein Fahrer pro Wagen am Tor"
    escalation: "Stille Annäherung möglich - sobald der erste Schuss fällt, Deckungsfeuer aus dem Container und Flucht zu den Wagen"
  - id: handler_intercept
    schauplatz: "Übergabe in einem leeren Parkhaus - ein feindlicher Verbindungsmann soll abgefangen werden"
    layout: "Drei Decks, Rampen ohne Deckung, ein Treppenturm pro Ecke, der Treffpunkt auf dem mittleren Deck"
    wachen: "Der Verbindungsmann mit zwei Wachen, ein Fahrer am Ausgang, Späher auf dem Dachdeck"
    escalation: "Still bis die Übergabe läuft - ein Fehlschlag und die Rampen werden mit Fahrzeugen zugefahren"
  - id: safehouse_clear
    schauplatz: "Konspiratives Versteck einer Fremdfraktion über einem geschlossenen Ladenlokal"
    layout: "Laden als Tarnung, eine versteckte Treppe zur Wohnung, ein Funkraum mit Notvernichtungs-Schalter"
    wachen: "Zwei Operative im Funkraum, ein Späher am Fenster, ein Wachhund im Laden"
    escalation: "Still bis der Funker euch sieht - dann Aktenvernichtung, Funkruf an Verstärkung, verbarrikadierte Treppe"
```

### Future Pool {#future_pool}

Futuristische Hochsicherheits-Runs - Anlagen, Stationen und getarnte
Untergeschosse, in denen Technik die Wachen ersetzt. Auch hier: ein klarer
Kipppunkt von leise zu laut. Die Einträge sind **inspirierende Anreger, nicht
erschöpfend** - die KI-SL erfindet im selben Geist frei weiter.

```yaml
future_pool:
  - id: zero_g_breach
    schauplatz: "Orbital-Forschungsanlage, deren ziviler Hangar ein militärisches Sperrlabor verbirgt"
    layout: "Wohnring mit künstlicher Schwerkraft, ein schwereloser Versorgungskern führt zum abgeschotteten Sperrlabor"
    wachen: "Stationscrew im Wohnring, autonome Wartungsdrohnen im Kern, ein KI-Schleusenwärter am Labor"
    escalation: "Still bis die Schleusen-KI eine Anomalie loggt - dann Druckabriegelung der Sektion und Drohnen-Sperrfeuer"
  - id: orbital_hack
    schauplatz: "Datenrelais-Plattform am Rand eines Zeittors - das Kernarchiv liegt in einem strahlungsgeschützten Unterdeck"
    layout: "Antennen-Außenring, eine Kommandobrücke, ein abgeschirmtes Unterdeck nur über manuelle Luke erreichbar"
    wachen: "Wenige Techniker, ein bewaffneter Systemadmin, automatische Geschütztürme am Unterdeck"
    escalation: "Still bis ein Datenabgriff entdeckt wird - dann Brücken-Lockdown, scharfe Türme, Selbstlöschung des Archivs"
  - id: arcology_subfloor
    schauplatz: "Megakon-Arkologie mit getarntem Hochsicherheits-Untergeschoss unter den öffentlichen Verkaufsetagen"
    layout: "Konsum-Promenaden oben, ein verstecktes Dienst-Tram führt in die abgeschottete Forschungstiefe"
    wachen: "Konzern-Sicherheit in den Promenaden, Iris-Schleusen am Tram, ein KI-überwachtes Labordeck"
    escalation: "Still solange eure Zugangs-Chips gültig scheinen - ein gesperrter Chip löst Promenaden-Räumung und Tram-Stopp aus"
  - id: cryo_extraction
    schauplatz: "Kryo-Anlage eines Konzerns, in der eine eingefrorene Forscherin als Patent-Geisel liegt - Rettung unter Gegenwehr"
    layout: "Empfangsdeck, ein Kühlhallen-Labyrinth mit Kapsel-Reihen, eine Reanimations-Kammer als Ziel"
    wachen: "Wartungs-Androiden, ein menschlicher Aufseher, Temperatur-Sensoren als stille Alarmgeber"
    escalation: "Still bis eine Kapsel geöffnet wird - dann Kühlhallen-Lockdown, Androiden im Angriffsmodus, Reanimations-Countdown"
  - id: server_temple
    schauplatz: "Daten-Sanktum eines Tech-Zirkels, der seinen Server-Altar wie eine Kultstätte unter dem Firmensitz hütet"
    layout: "Repräsentative Lobby, ein ritualisierter Abstieg zum Rechenzentrum, der Master-Kern in einem Faradaykäfig"
    wachen: "Zirkel-Adepten als Wächter, biometrische Andacht-Schleusen, ein autonomes Verteidigungssystem am Kern"
    escalation: "Still solange ihr den Ritus mitspielt - ein falscher Handgriff und der Käfig versiegelt, Adepten greifen an"
  - id: shuttle_summit
    schauplatz: "Hochrangiges Treffen an Bord eines Suborbital-Shuttles - das Treffen muss gestürmt oder unterbrochen werden"
    layout: "Passagierdeck mit Konferenzkabine, ein enger Versorgungsgang, das Cockpit als verriegelter Rückzugsraum"
    wachen: "Personenschützer der Delegierten, ein Bordmarshal, Geschütztüren zwischen den Sektionen"
    escalation: "Still bis der Marshal Verdacht schöpft - dann Kabinen-Riegel, Druckwarnung, Notabkopplung als Eskalation"
```

### Faction-Op Pool {#faction_op_pool}

Dieser Pool liefert den **mittleren Spannungs-Layer** zwischen banalem
Nebenauftrag und Weltrettung: Fraktions-Operationen, die sich groß und wichtig
anfühlen - eine Megakon-Anlage infiltrieren, einen Zirkel ausheben, Forscher
exfiltrieren, eine zeitreisende Fremdfraktion stören -, ohne dass jeder Einsatz
gleich über das Schicksal der Welt entscheidet. Die Stakes liegen bei Anlage,
Zelle oder Schlüsselperson, nicht beim Atomkrieg.

```yaml
faction_op_pool:
  - id: megacorp_infiltration
    schauplatz: "Megakon-Produktionsanlage, deren unscheinbares Logistik-Gebäude ein getarntes Hochsicherheits-Untergeschoss trägt"
    layout: "Zwei Fertigungshallen als Fassade, ein versteckter Frachtaufzug führt zum abgeschotteten Entwicklungslabor"
    wachen: "Werkschutz mit Ausweispflicht, Drohnen-Streifen über den Hallen, eine Iris-Schleuse am Aufzug"
    escalation: "Still solange ihr als Zulieferer geltet - ein gesperrter Werksausweis löst Hallen-Lockdown und Drohnen-Jagd aus"
  - id: conclave_dismantle
    schauplatz: "Geheimer Zirkel tagt in einer Krypta unter alten Katakomben - die Führungszelle soll dezimiert und enttarnt werden"
    layout: "Katakomben-Gänge als Zugang, ein Ritualgewölbe als Zentrum, mehrere Fluchtnischen mit Geheimtüren"
    wachen: "Vermummte Adepten, bewaffnete Türhüter an jedem Gang, ein Zirkelmeister mit Leibgarde"
    escalation: "Still solange die Tarnung als Eingeweihte hält - ein enttarntes Gesicht und die Gänge werden zur tödlichen Falle"
  - id: researcher_exfil
    schauplatz: "Forscher einer Fremdfraktion soll aus einem bewachten Anwesen exfiltriert werden, bevor er verlegt wird"
    layout: "Herrenhaus mit Parkmauer, der Forscher in einem gesicherten Studiertrakt, Tor und Tunnel als Fluchtwege"
    wachen: "Personenschützer im Haus, Streifen entlang der Mauer, ein Kontrollposten am Tor"
    escalation: "Still bis das Tor den fehlenden Forscher meldet - dann Mauer-Riegel, Hundestreife, ein Verfolger-Konvoi"
  - id: timeline_sabotage
    schauplatz: "Getarnte Operationsbasis einer zeitreisenden Fremdfraktion in einem Lagerhaus - ihr Zeit-Eingriff soll gestört werden"
    layout: "Lagerhalle mit getarntem Kontrollraum, ein Geräte-Kern im Zentrum, Galerie und Verladerampe als Zugänge"
    wachen: "Fremd-Operative am Kern, ein Techniker-Team, automatische Scanner an jedem Tor"
    escalation: "Still bis ein Scanner anschlägt - dann Kern-Notabschaltung, Operative in Deckung, Selbstzerstörungs-Drohung der Basis"
  - id: black_clinic_raid
    schauplatz: "Schwarze Klinik der Fremdfraktion, in der an entführten Zeugen experimentiert wird - sie muss ausgehoben werden"
    layout: "Praxis-Fassade, ein OP-Trakt im ersten Stock, ein Zellen-Keller mit den festgehaltenen Zeugen"
    wachen: "Pflege-Schläger im Trakt, ein Wachposten am Keller, Kameras in jedem Flur"
    escalation: "Still bis ein Zeuge befreit wird - dann Keller-Lockdown, Personal greift an, Notruf an Fraktions-Verstärkung"
  - id: summit_disrupt
    schauplatz: "Wichtiges Allianz-Treffen zweier Fraktionen in einem Konferenzzentrum - das Bündnis soll gestört oder belauscht werden"
    layout: "Foyer als Tarnung, ein gesicherter Konferenzsaal, ein Technik-Zwischengeschoss über der Decke"
    wachen: "Bodyguards beider Seiten, Türkontrolle mit Gästeliste, Späher im Zwischengeschoss"
    escalation: "Still solange ihr als Personal durchgeht - ein aufgedeckter Lauschangriff und der Saal wird abgeriegelt, Sturm beginnt"
```

## Historische Wendepunkte-Generator: Auslöser und Folgen {#wendepunkte-generator}

Manchmal führt schon eine kleine Handlung dazu, dass ein bekanntes Ereignis
überhaupt erst stattfindet. Dieser Generator liefert Ansätze, wie die Chrononauten
unfreiwillig einen historischen Moment auslösen oder verhindern. Wählt eine
Kombination aus **Ereignis**, **Aktion** und **Konsequenz**:

1. **Ereignis:**
   1. Ein großes Unglück steht kurz bevor (z. B. eine Explosion oder ein Absturz).
   2. Ein gefeierter Durchbruch der Wissenschaft soll präsentiert werden.
   3. Eine wichtige Krönung oder Wahl entscheidet über den Lauf der Geschichte.
   4. Eine Revolution brodelt und sucht nur noch den Funken zur Entzündung.
   5. Ein visionärer Künstler ringt um die Fertigstellung seines Werkes.
   6. Ein geheimer Pakt zwischen Mächten soll unterzeichnet werden.
2. **Aktion der Agenten:**
   1. Sie bewahren eine Schlüsselfigur vor einem Attentat.
   2. Sie stehlen oder zerstören ein entscheidendes Dokument.
   3. Sie überzeugen einen Protagonisten, doch noch aufzutreten.
   4. Sie lenken einen Rivalen ab, wodurch eine Idee ungestört reifen kann.
   5. Sie decken eine Intrige auf und bringen sie an die Öffentlichkeit.
   6. Sie sabotieren ein Transportmittel oder ersetzen es unbemerkt.
3. **Konsequenz:**
   1. Das historische Ereignis findet nur dank ihres Eingreifens statt.
   2. Der Verlauf verändert sich subtil und führt zu einem bekannten Ergebnis.
   3. Ihr Eingreifen verhindert die Katastrophe - eine andere tritt an ihre Stelle.
   4. Eine Nebenfigur wird berühmt und beeinflusst später die Zeitlinie.
   5. Die Öffentlichkeit erfährt nichts; nur der Kodex notiert die Veränderung.
   6. Eine Fraktion nutzt das Resultat heimlich für ihre eigenen Ziele.

Mit diesem Baukasten entstehen Missionen, bei denen die Agenten scheinbar nur
eine Kleinigkeit erledigen. Erst im Nachhinein erkennen sie, dass ihr Handeln den
geschichtlichen Wendepunkt überhaupt ermöglicht hat - oder dass sie ihn, ohne es
zu wollen, verhindert haben.

### Historische Anomalien: Trigger-Liste

Die folgende Tabelle liefert konkrete Ausgangssituationen. Jede Zeile benennt ein
historisch belegtes Ereignis, das in der ZEITRISS-Chronologie durch eine
Anomalie abweicht. **Vorphase** beschreibt den Moment knapp vor dem Auslöser,
**Nachphase** die Lage, sobald die Anomalie sich voll entfaltet. Wählt oder
würfelt einen Eintrag als Missionsstart.

1. **London 1666 - Großer Brand** \| Vorphase: Funken im Bäckerladen.
   \| Nachphase: Stadt steht in Flammen.
2. **Boston 1773 - Tea Party** \| Vorphase: Heimliche Treffen in Tavernen.
   \| Nachphase: Kisten treiben im Hafen.
3. **Paris 1789 - Sturm auf die Bastille** \| Vorphase: Gerüchte über Waffenlager.
   \| Nachphase: Aufgebrachte Menge stürmt das Gefängnis.
4. **New Orleans 1812 - Großer Brand** \| Vorphase: Kerzenstummel fällt um.
   \| Nachphase: Viertel lichterloh.
5. **Waterloo 1815 - Letzte Schlacht Napoleons** \| Vorphase: Verregnete Felder.
   \| Nachphase: Truppen brechen panisch.
6. **Berlin 1848 - Märzrevolution** \| Vorphase: Flugblätter im Umlauf.
   \| Nachphase: Barrikadenkämpfe.
7. **London 1851 - Great Exhibition** \| Vorphase: Weltneuheiten reisen an.
   \| Nachphase: Rivalen kämpfen um Erfindungen.
8. **Florenz 1867 - Laborunfall** \| Vorphase: Experimente mit Äthergas.
   \| Nachphase: Halle explodiert, Rauchschwaden.
9. **London 1888 - Letztes Opfer des Rippers** \| Vorphase: Polizei tappt im Dunkeln.
   \| Nachphase: Spur führt zu einem Zeitreisenden.
10. **Paris 1889 - Weltausstellung** \| Vorphase: Eiffelturm im Bau.
    \| Nachphase: Spione jagen neue Technik.
11. **Chicago 1893 - Weltausstellung** \| Vorphase: Besucher strömen herbei.
    \| Nachphase: Stromnetz bricht zusammen.
12. **Sankt Petersburg 1905 - Blutsonntag** \| Vorphase: Friedlicher Marsch.
    \| Nachphase: Soldaten schießen in die Menge.
13. **San Francisco 1906 - Erdbeben** \| Vorphase: Tiere verhalten sich unruhig.
    \| Nachphase: Stadtteile versinken in Flammen.
14. **Sarajevo 1914 - Attentat auf Franz Ferdinand** \| Vorphase: Autokolonne formiert sich.
    \| Nachphase: Europa steht vor dem Krieg.
15. **Galizien 1916 - Verschollenes U-Boot** \| Vorphase: Funkkontakt reißt ab.
    \| Nachphase: U-Boot taucht Jahre später wieder auf.
16. **New York 1929 - Börsencrash** \| Vorphase: Ungewöhnliche Kursausschläge.
    \| Nachphase: Broker geraten in Panik.
17. **Berlin 1936 - Olympische Spiele** \| Vorphase: Propagandashow läuft.
    \| Nachphase: Geheime Aufrüstung fliegt auf.
18. **Hindenburg 1937 - Zeppelin** \| Vorphase: Wartungstrupp meldet seltsamen Geruch.
    \| Nachphase: Luftschiff in Flammen.
19. **New York 1939 - World's Fair** \| Vorphase: Futuristische Vorführungen.
    \| Nachphase: Tarnprojekt enttarnt.
20. **Los Alamos 1945 - Trinity-Test** \| Vorphase: Wissenschaftler diskutieren Risiken.
    \| Nachphase: Greller Blitz, Messgeräte spielen verrückt.
21. **Roswell 1947 - Absturz** \| Vorphase: Radarempfang gestört.
    \| Nachphase: Militär riegelt die Absturzstelle ab.
22. **Berlin 1961 - Mauerbau** \| Vorphase: Geheimtreffen der Führung.
    \| Nachphase: Straßen plötzlich blockiert.
23. **Dallas 1963 - Kennedy-Attentat** \| Vorphase: Wagenkolonne startet.
    \| Nachphase: Chaos auf der Dealey Plaza.
24. **Woodstock 1969 - Musikfestival** \| Vorphase: Technikprobleme auf der Bühne.
    \| Nachphase: Massen strömen unkontrolliert.
25. **Apollo 13 1970 - Raumflug** \| Vorphase: Routinefunksprüche.
    \| Nachphase: Funkspruch "Houston, we've had a problem".
26. **Osaka 1970 - Expo '70** \| Vorphase: Kalter Krieg mischt mit.
    \| Nachphase: Futuristische Show gerät außer Kontrolle.
27. **München 1972 - Olympia** \| Vorphase: Verdächtige sichten das Dorf.
    \| Nachphase: Geiselnahme und Belagerung.
28. **Three Mile Island 1979 - Reaktorstörung** \| Vorphase: Ventile melden Fehler.
    \| Nachphase: Kühlsystem versagt.
29. **Los Angeles 1984 - Olympisches Finale** \| Vorphase: Kameraübertragung flackert.
    \| Nachphase: Stromausfall im Stadion.
30. **Tschernobyl 1986 - Reaktor 4** \| Vorphase: Testlauf ohne Freigabe.
    \| Nachphase: Kernschmelze und Evakuierung.
31. **Berlin 1989 - Mauerfall** \| Vorphase: Verwirrte Meldungen in der Pressekonferenz.
    \| Nachphase: Menschenmassen reißen Mauern ein.
32. **Oslo 1991 - Friedensnobelpreis** \| Vorphase: Bewerberlisten manipuliert.
    \| Nachphase: Zeremonie endet im Skandal.
33. **Tokio 1995 - Sarin-Anschlag** \| Vorphase: U-Bahn voller Pendler.
    \| Nachphase: Giftgasalarm.
34. **Seattle 1999 - WTO-Proteste** \| Vorphase: Demonstranten sammeln sich.
    \| Nachphase: Straßenschlachten eskalieren.
35. **New York 2001 - 9/11** \| Vorphase: Flugzeuge weichen vom Kurs ab.
    \| Nachphase: Türme stürzen ein.
36. **Bagdad 2003 - Museumsplünderung** \| Vorphase: Chaos nach Einmarsch.
    \| Nachphase: Artefakte verschwunden.
37. **Jakarta 2004 - Tsunamiwarnung** \| Vorphase: Seismografen schlagen aus.
    \| Nachphase: Küsten verwüstet.
38. **Berlin 2006 - Stromausfall** \| Vorphase: Netzschwankungen.
    \| Nachphase: U-Bahnen bleiben stehen.
39. **Peking 2008 - Eröffnungsfeier** \| Vorphase: Wetterkontrolle testet Chemikalien.
    \| Nachphase: Künstlicher Regen setzt ein.
40. **Haiti 2010 - Erdbeben** \| Vorphase: Tiere fliehen ins Landesinnere.
    \| Nachphase: Hauptstadt in Trümmern.
41. **Fukushima 2011 - Tsunami trifft AKW** \| Vorphase: Notfallprotokolle aktiv.
    \| Nachphase: Strahlungswerte steigen.
42. **London 2012 - Olympia** \| Vorphase: Sicherheitsdrohnen patrouillieren.
    \| Nachphase: Drohnen spielen verrückt.
43. **Moskau 2013 - Meteorit** \| Vorphase: Himmelsleuchten.
    \| Nachphase: Druckwelle zerstört Fenster.
44. **Genf 2015 - Teilchenbeschleuniger** \| Vorphase: Magnetringe überhitzen.
    \| Nachphase: Zeitfenster blitzt kurz auf.
45. **Paris 2016 - Stromausfall im Louvre** \| Vorphase: Wartungsarbeiten am Netz.
    \| Nachphase: Kostbare Exponate verschwinden.
46. **Houston 2017 - Hurricane Harvey** \| Vorphase: Satellitenbilder zeigen extreme Wolkenbildung.
    \| Nachphase: Straßen überflutet.
47. **Bangkok 2018 - Höhlenrettung** \| Vorphase: Junge Fußballer erkunden Höhle.
    \| Nachphase: Monsunregen schneidet den Rückweg ab.
48. **Notre-Dame 2019 - Großbrand** \| Vorphase: Baugerüst wackelt.
    \| Nachphase: Dachstuhl in Flammen.
49. **Wuhan 2019 - High-Tech-Expo** \| Vorphase: Prototypen-Drohnen werden vorgestellt.
    \| Nachphase: Steuerung fällt aus, Drohnen stürzen ab.
50. **Beirut 2020 - Hafenexplosion** \| Vorphase: Rauch über Lagerhalle.
    \| Nachphase: Schockwelle legt Gebäude in Schutt.
51. **Tokio 2021 - Olympische Spiele** \| Vorphase: Experimentelles KI-Maskottchen begrüßt die Zuschauer.
    \| Nachphase: Fehlfunktion löst gefährliche Zwischenfälle aus.
52. **Glasgow 2021 - Klimagipfel** \| Vorphase: Aktivisten blockieren Straßen.
    \| Nachphase: Unerklärliche Stromsenke legt Viertel lahm.
53. **Texas 2022 - Stromnetz-Kollaps** \| Vorphase: Kälteeinbruch.
    \| Nachphase: Blackout und Versorgungsnotstand.
54. **Genf 2023 - KI-Konferenz** \| Vorphase: Prototype läuft heiß.
    \| Nachphase: Selbstlernende Drohne entweicht.
55. **Kapstadt 2024 - Wasserkrise** \| Vorphase: Reservoirs fast leer.
    \| Nachphase: Rationierung eskaliert Unruhen.
56. **Mars - Gesicht von Cydonia** \| Vorphase: Rover meldet mysteriöse Struktur.
    \| Nachphase: Basis gerät in Aufruhr.
57. **Phobos - Der Basilisk** \| Vorphase: Mission entdeckt Turm.
    \| Nachphase: Crew verliert Kontakt.
58. **Rückseite des Mondes - Die wahre Madonna** \| Vorphase: Crash-Signal eines Notfunksenders wird geortet.
    \| Nachphase: Hybride Kreatur erwacht.
59. **Saturnmond Titan - Unbekannte Signaturen** \| Vorphase: Sonden liefern seltsame Daten.
    \| Nachphase: Methanmeere brodeln.
60. **Antarktis - Versiegelte Anlagen** \| Vorphase: Bohrung stößt auf Metall.
    \| Nachphase: Alte Technologie erwacht.
61. **Kapustin Jar - Aktiver Zeitriss** \| Vorphase: Testlauf steht bevor.

\| Nachphase: Zeitriss reißt sich auf.

### Preserve-Liste (Near-Misses)

Siehe `preserve_pool` oben.

## Random-Epochen-Generator: Wann und wo? {#epochen-generator}

ZEITRISS-Missionen können prinzipiell in jeder Epoche der echten oder fiktiven Geschichte spielen.
Wenn ihr spontan ein neues Setting braucht oder die Spieler unerwartet irgendwo auftauchen, liefert
dieser Generator einen schnellen Rahmen. Er kombiniert einen **Zeitort** (Epoche/Setting) mit einem
markanten **Ereignis oder Konflikt**, das dort gerade passiert. Würfelt z. B. 1W6 für einen Zeitort
**und** 1W6 für ein besonderes Ereignis, oder nutzt eine der folgenden vordefinierten Kombinationen:

_Regel für die Kühlung der Epochengewichte:_

1. Notiere nach jedem Zufallswurf die gezogene Epoche als `last_epoch`.
2. Verringere ihr Gewicht in der Tabelle um den **Cooling-Wert** (Standard 0.05), jedoch nie unter 1 %.
3. Normiere anschließend alle Gewichte, sodass ihre Summe wieder 1 ergibt.
4. Würfle die nächste Epoche anhand der aktualisierten Wahrscheinlichkeiten.

5. **Steinzeitliche Wildnis** (ca. 10.000 v.Chr.) - _Setting:_ Weite prähistorische Landschaft mit
   Megafauna (Mammutherden, Säbelzahntiger) und nomadischen Stämmen. **Besonderheit:** Ein kleines Dorf
   ist in einer Zeitschleife gefangen: Jeden Morgen geht die Sonne nicht auf. Fackeln brennen ewig,
   Tiere wirken verwirrt. Höhlenmalereien deuten auf einen temporalen Meteor hin, der hier einst
   einschlug. Die Chrononauten müssen das prähistorische Paradoxon beheben, während misstrauische
   Schamanen und hungrige Bestien ihnen zusetzen.
6. **Ägyptisches Neues Reich** (1250 v.Chr.) - _Setting:_ Glühende Wüstensonne, monumentale Tempel
   und der Hof von Pharao Ramses II. **Besonderheit:** Im Verborgenen wird ein Fremd-Relikt in einer
   Pyramide verehrt, angeblich ein Geschenk der Götter. Tatsächlich stammt es aus der Zukunft und
   strahlt ungewöhnliche Energie ab. Die Agenten müssen entscheiden: Stehlen sie das Relikt, um die
   Zeitlinie zu schützen - riskieren aber, die lokale Religion zu erschüttern? Oder lassen sie es in
   der Geschichte, mit unbekannten Folgen? Intrigante Hohepriester und ein misstrauischer Wesir machen
   jede Aktion zum Balanceakt.
7. **Mittelalterliche Hafenstadt** (14. Jh.) - _Setting:_ Hansekoggen im Hafen, geschäftiges
   Markttreiben, Tavernenlärm und abendrötliche Gassen. **Besonderheit:** Gerüchte gehen um von einem
   Geisterschiff, das bei Vollmond im Hafen erscheint und genauso plötzlich verschwindet. Eine
   temporale Erscheinung? Vielleicht ein Zeitschiff aus der Zukunft, das hier festsitzt. Die
   Chrononauten könnten in einen lokalen Machtkampf zwischen Gilden geraten (wer das "Wunder" für sich
   nutzen kann, gewinnt Ansehen), während sie das Geheimnis des Schiff-Geists lüften. Ist es ein
   Hilferuf aus einer anderen Zeit?
8. **Victorianisches London** (1888) - _Setting:_ Neblige Gassen, Kutschenräder auf
   Kopfsteinpflaster, flackernde Gaslaternen. Jack the Ripper treibt sein Unwesen. **Besonderheit:**
   Durch einen Zeitriss tauchen ab und zu Gestalten aus anderen Epochen in Whitechapel auf. Die
   Behörden schieben es auf Wahnsinn oder Verkleidungen. Die Helden müssen nicht nur den berüchtigten
   Ripper finden, sondern auch erklären, warum sein letztes Opfer ein römischer Gladiator war, der
   plötzlich in den Gassen stand. Ein grimmiger Zeitsprung-Krimi beginnt.
9. **Pazifik während des Zweiten Weltkriegs** (1942) - _Setting:_ Tropische Insel mit
   Militärstützpunkt, dröhnende Flugzeuge, Morse-Funk im Radio. **Besonderheit:** _Zeitkapsel-
   Konflikt:_ Auf der Insel erscheint ein Objekt aus der Zukunft - eine High-Tech-Drohne - und sowohl
   die Alliierten als auch die Achsenmächte bekommen Wind davon. Die Helden müssen verhindern, dass
   diese Technik den Krieg beeinflusst. Doch wem vertrauen sie vor Ort? Eine gefährliche Spionage-
   Mission, bei der sie vielleicht vorgeben müssen, für eine Seite zu arbeiten, um an die Drohne zu
   gelangen.
10. **Mars-Kolonie** (2097) - _Setting:_ Ein Habitat unter Kuppeln, rote Wüstenlandschaft draußen,
    futuristische Labore. **Besonderheit:** _Erster Kontakt_ - aber nicht mit Aliens, sondern mit
    Zeitreisenden: Die Mars-Siedler empfangen ein Notrufsignal von einem beschädigten
    Transceiver aus dem Jahr 2300. Die
    Zukunftsmenschen sind gestrandet und flehen um Hilfe. Die Chrononauten müssen koordinieren, wie man
    diese temporale Notlage löst, ohne dass die fragile Mars-Gesellschaft des Jahres 2097 kollabiert
    (schon allein die Nachricht "die Mission wird aufgegeben werden" könnte Panik auslösen). Eine
    Episode voll Sci-Fi-Philosophie: Darf man Leuten aus der eigenen Zukunft helfen, wenn es bedeutet,
    dass man sein eigenes Schicksal kennt?

_Tipp:_ Ihr könnt natürlich jede Epoche und jedes Ereignis nach Belieben austauschen. Die obigen
sechs Kombinationen dienen vor allem als inspirierende Beispiele - z. B. **Steampunk-Paris 1889 +
ein Monster aus einem Zeitlabor** ergeben ebenfalls einen spannenden Schauplatz!

### Rift-Seeds (automatisch)

Rifts erscheinen bei Paradoxon 5. Das HQ notiert sie hier als `phase: rift` ohne Episodennummer.
Sie werden erst nach Abschluss des aktuellen Core-Arcs als separate Mission spielbar.

```yaml
phase: rift
jahr: 1889
ort: Prag
thema: Beispiel-Rift
```

### Fremdfraktions-Generator {#fremdfraktions-generator}

Statt vorgefertigte Arcs nachzuspielen, **erzeugt die KI-SL jede Gegnerfraktion
frisch** aus diesem Baukasten. Drei Achsen kombinieren — Motiv, Tech-Signatur,
Rollen-Roster — und das Ganze epochengerecht einfärben. So fühlt sich jede
Fremdfraktion eigen an, ohne dass eine feste Vorlage die Story einengt.

> **Anreger, nicht erschöpfend:** Die Tabellen und Beispiel-Fraktionen unten sind
> Funken, keine Pflicht-Auswahl. Die KI-SL würfelt/wählt einen Ausgangspunkt und
> erfindet Name, Motiv und Roster passend zu Epoche und Auftrag frei weiter —
> niemals wörtlich übernehmen.

#### Achse 1 — Motiv (warum schreibt die Fraktion Geschichte um?)

| W6 | Motiv | Profit-Logik |
| --- | --- | --- |
| 1 | **Markt-Monopol** | Eine umgeschriebene Zeitlinie macht ihr Produkt/Material konkurrenzlos (z. B. exklusive Handelsroute). |
| 2 | **Bio-Genese** | Sie wollen eine genetische/biologische Weiche stellen, die ihnen später gehört. |
| 3 | **Industrie-Sprung** | Eine Katastrophe oder ein Durchbruch soll früher/anders eintreten, um Technologie zu kontrollieren. |
| 4 | **Macht-Dynastie** | Ein anderes Reich/Regime soll gewinnen, weil sie dort die Fäden halten. |
| 5 | **Daten-Ernte** | Sie wollen einen historischen Wendepunkt belauschen/abgreifen, nicht zwingend ändern. |
| 6 | **Ideologie** | Sie glauben, ihre Zeitlinie sei die „richtige" — Profit ist Nebensache, Fanatismus der Treiber. |

Die Fraktion ist immer ein **transtemporaler Megakon oder eine Zelle** mit Mitteln
aus mehreren Epochen. Der Spieler-Gegensatz bleibt: Fremdfraktion manipuliert,
ITI (Preserve **und** Trigger gemeinsam) hält die dokumentierte Geschichte stabil.

#### Achse 2 — Tech-Signatur (der erkennbare Stil ihrer Ausrüstung)

| W6 | Signatur | Einfärbung |
| --- | --- | --- |
| 1 | **Chrompunk-Antik** | Zeit-Tech in das Material der Epoche gegossen (Bronze-Smartguns, Linothorax-Kevlar, Wachstafel-Cyberdecks). |
| 2 | **Biogenetisch** | Hybride, verstärkte Tiere, Chitinpanzer, gezüchtete Spezialisten. |
| 3 | **Netz/Cyber** | Cyberdecks, Drohnenschwärme, Hack-Rigger, Shock-Waffen. |
| 4 | **Social-Verdeckt** | Voice-Mods, Fake-Creds, Bestechung, Propaganda — kämpfen über Einfluss. |
| 5 | **Präzision/Fernkampf** | Gauss-Snipers, Chamäleon-Cloaks, Drohnen-Barrage. |
| 6 | **Anachronismus-Mix** | Bewusst schräge Kombi (Samurai mit Bioware, Neandertaler-Breacher) als Schock-Effekt. |

#### Achse 3 — Rollen-Roster (3–6 Einheiten, epochengerecht eingefärbt)

Die KI-SL stellt aus diesen Archetypen ein Roster zusammen und kleidet jeden
**in die Epoche und die gewählte Tech-Signatur**. Derselbe Archetyp sieht in
480 v. Chr. anders aus als 1986.

| Archetyp | Funktion | Beispiel-Einfärbungen über Epochen |
| --- | --- | --- |
| **Breacher / Bruiser** | Nahkampf, Geländekontrolle | Linothorax-Hoplit (Antike) · Hydraulik-Hammer-Pionier (1980er) · Neandertaler-Keule (Urzeit-Hybrid) |
| **Hacker / Rigger** | Netzangriff, Drohnen | Wachstafel-Deck (Antike) · Cyberdeck T2 + Shock-Pistol (Moderne) |
| **Elite-Melee** | schnelle Klingenstürme | Cyber-Samurai mit Bioware · Smart-Gladius-Veteran |
| **Sniper / Ranged** | Fernfeuer, Drohnen-Barrage | Gauss-Precision + Chamäleon-Cloak · MP7-SD-Assault-Merc |
| **Face / Spin-Doctor** | Bestechung, Propaganda, Rückfallebene | Vox-Mod-Redner · Fake-Creds-Manipulator |
| **Bio-Hybrid** | Späher, Furcht, Support | Urwolf-Bluthund (Spur, Biss W⁶, Furcht-Aura) · Chitinpanzer-Humine |
| **Commander / Handler** (Finale) | Befehl, Taktik-Link | Elite-Handler mit Tact-Link, hohe CHA, Gel-Ruger |

**Roster-Faustregel:** kleine Op = 3 Archetypen, Episode-Boss-Roster = 5–6 plus
ein Commander im Finale. Genau **ein** Bio-Hybrid pro Roster (Creature-Limit),
sonst kippt der Tech-Noir-Ton ins Monster-Movie.

#### Beispiel-Fraktionen (Anreger aus dem Hauskanon)

Diese drei sind **belegte Beispiele**, wie der Generator klingt — frei
weiterverwendbar oder als Muster für eigene Fraktionen:

- **ARGOS Venture** — transtemporaler Hochrisiko-Megakon. *Motiv:* Markt-Monopol
  (setzt auf eine „Persische Weltordnung" für eine exklusive Bronze-Silk-Road-
  Zeitlinie). *Signatur:* Chrompunk-Antik. *Roster-Kern:* Bruiser (Linothorax-
  Kevlar, Smart-Gladius), Hack-Monk (Wachstafel-Deck), Silver-Tongue-Face,
  Urwolf-Bluthund.
- **CHRONOTECH Genesis** — biogenetischer Zeit-Megakon. *Motiv:* Bio-Genese.
  *Signatur:* Biogenetisch + Anachronismus-Mix. *Roster-Kern:* Neandertaler-
  Bruiser, Cyber-Samurai-Bodyguard, CT-NetSec-Hacker, Assault-Merc, Rigger,
  Elite-Handler (Finale), Urwolf-Bluthund.
- **KAIROS Dynamics** — industriell-verdeckter Megakon. *Motiv:* Industrie-Sprung.
  *Signatur:* Netz/Cyber + Anachronismus-Mix. *Roster-Kern:* Baupionier,
  Hack-Rigger, Bioware-Samurai, Gauss-Sniper, Spin-Doctor, Humine.

> Die KI-SL baut aus Motiv + Signatur + Roster die Einsatz-Szenen frei über den
> Core-Briefing-Baukasten und das Core-12-Step-Template (oben in diesem Modul).
> Schauplatz-Kette und Eskalation entstehen pro Durchlauf neu — kein fester Plot.

### Rift-Seed Catalogue {#rift-seed-catalogue}

Kanonischer Pool für Casefiles mit **einem** Zeitphänomen. Briefings bestehen aus maximal fünf Stichpunkten, Boss-Notes enthalten exakt eine Weirdness. `time_marker` beschreibt das aktive Phänomen; Urban-Myth-Täuschungen sind nur erlaubt, wenn die Rift-Casefile-Edition die echte Kreatur liefert.

```yaml
- rift_id: "RIFT-BUTCHER"
  epoch: "Warschau 1997"
  label: "Chrono Butcher"
  seed_tier: mid
  hook: "Serienmorde im Nullzeit-Korridor - Ermittlungsakte sichern, Killer stoppen"
  time_marker: Stutter
  briefing_public:
    - Tatorte zeigen Blutspuren, die sich kurz zurückziehen
    - Letzte Opfer funken "Er ist schon wieder hier" bevor Verbindung bricht
    - Ermittlungsakte mit Taschenuhr des ersten Opfers verschwunden
    - Zeugen hören Stimmfragmente aus den Fluren
  leads:
    - Investigation 12: Frame-Brüche an Wänden bilden Weg zum Uhr-Anchor
    - Mind 12: Opferstimme hallt im Psi-Scan exakt 00:13:17 nach
    - Tech 11: Überwachung zeigt zwei Schatten pro Bewegung
  boss_private:
    truth: Zeitversetzter Serienmörder in Stutter-Schleife, an Uhr gebunden
    weakness: Anchor-Uhr exakt 00:13:17 stellen und im Stutter zerstören (Psi-Impuls Mind 12)
    anomaly: Frame Lunge (GES-Save SG 12, 3 LP + Panik)
    boss_stat_hint: "LP 11 | Armor 1 | GES 8 | TEMP 6"

- rift_id: "RIFT-JDEV"
  epoch: "New Jersey 1909"
  label: "Jersey Devil"
  seed_tier: low
  hook: "Flügelschlag im Pine Barren - Nest ausheben"
  time_marker: Loop
  briefing_public:
    - Viehrisse bei Vollmond, kreisförmige Kratzspuren
    - Zeugen hören 30-Sek-Schrei mit Wiederholung
    - Pfadfinder-Patrouille vermisst
  leads:
    - Survival 10: Verkohlte Knochenreste im Wurzelbau bergen
    - Tech 9: Audioanalyse bestätigt Loop-Marker
    - Investigation 11: Flugbahn wiederholt Baumaufschlag
  boss_private:
    truth: Para-Chimäre kreist um verfluchte Familienreste
    weakness: Anchor-Knochen mit geweihtem Kupferdraht fesseln und verbrennen (Survival 11 oder Tech 11)
    anomaly: Loop Reset (setzt Ini zurück, Anchor schützt)
    boss_stat_hint: "LP 8 | Armor 1 | GES 8 | TEMP 4"

- rift_id: "RIFT-BRIDGE"
  epoch: "Chongqing 2032"
  label: "Totenbrücke"
  seed_tier: mid
  hook: "Geisterbus stoppt Verkehr - Ursache finden, Brücke freiräumen"
  time_marker: Echo
  briefing_public:
    - Bus erscheint jede Stunde, keine Fahrer
    - Verkehrs-App meldet Schattenfahrzeug ohne Nummer
    - Passant hörte Stimmen aus anderer Epoche
  leads:
    - Tech 12: Lidar zeigt Nachbild, kein Radar-Echo
    - Investigation 12: Unfallakte 1998 mit gleichem Bus
    - Medicine 11: Zeuge erleidet Zeitbrand an Händen
  boss_private:
    truth: Echo-Manifestation des Unfallbusses, gebunden an Fahrgast-Anker
    weakness: Blackbox bergen + Anker verarzten
    anomaly: Echo Surge (Psi-Save 12, Stress +1)
    boss_stat_hint: "LP 9 | Armor 0 | INT 6 | TEMP 6"

- rift_id: "RIFT-ORCHID"
  epoch: "Amazonas 1899"
  label: "Blood Orchid"
  seed_tier: mid
  hook: "Kurierteam verschollen - Symbionten-Parasit stoppen"
  time_marker: Slip
  briefing_public:
    - Expedition meldet Halluzinationen, dann Funkstille
    - Lianen wachsen in Stunden, nicht Wochen
    - Ein Träger sprach rückwärts, Stimme doppelt
  leads:
    - Medicine 12: Sporen haben fremde Zeitstempel
    - Survival 11: Pflanzenfläche pulsiert im 5-Sek-Rhythmus
    - Investigation 10: Kartendaten zeigen sich verschiebende Pfade
  boss_private:
    truth: Symbionten-Schwarm springt zwischen Phasen
    weakness: Feuer + Stabilisierung des Zeitmarkers mit Salzlinie
    anomaly: Slip Bloom (GES-Save SG 12, immobilisiert 1 Rd.)
    boss_stat_hint: "LP 12 | Armor 1 | STR 6 | TEMP 6"

- rift_id: "RIFT-LUNAR"
  epoch: "Luna Far-Side 2266"
  label: "Void Howler"
  seed_tier: high
  hook: "Funkspalte auf Mondbasis - Null-G-Raubtier jagt Crew"
  time_marker: Stutter
  briefing_public:
    - Kameras verlieren alle 3 Frames Bild
    - Außenschotts öffnen sich ohne Signal
    - Astronaut berichtet, dass Geräusch vor Echo kommt
  leads:
    - Tech 13: Stutter-Marker deckt sich mit Px-Sensorwarnung
    - Engineering 12: Kratzspuren verlaufen gegen Bewegungsrichtung
    - Medicine 12: Opfergewebe zeigt Vakuumverbrennungen
  boss_private:
    truth: Null-G-Raubtier springt phasenweise, jagt auf Atemluft
    weakness: Druckschott schließen + Psi-Signatur spiegeln (Mind 13)
    anomaly: Stutter Pounce (GES-Save SG 13, 3 LP, Stress+2 bei W6=6)
    boss_stat_hint: "LP 14 | Armor 2 | GES 12 | TEMP 8"
```

### Rift-Casefile Builder

Schablone für vollständige Fallakten mit exakt **einer** Weirdness (Guard bleibt aktiv, keine
zweite Anomalie und keine "es war nur Tech"-Auflösung). Nutze den Builder für Low/Mid/High-Seeds
und mappe ihn direkt auf das 14-Szenen-Template.

1. **CASE** - `ID | Epoche | Seed-Tier | time_marker`.
2. **VISUAL HOOK** - 1 Satz mit Anchor + Marker, der sofort im HUD auftaucht.
3. **BRIEFING PUBLIC** - max. 5 Bullets; Witness + Gefahrenhinweis, keine zweite Weirdness.
4. **OBJECTIVES** - `Secure Anchor`, `Trace Leads`, `Neutralize Weakness`, optional `Recover
Sample`.
5. **CASE OVERLAY** - HUD `MODE RIFT · CASE <ID> · HOOK <Label> · WEIRD 1/1` +
   `register_anomaly()` nur einmal.
6. **TRUTH** - kurzer Absatz, warum Marker aktiv bleibt.
7. **LEADS PRIVATE** - 3 Checks (Fachwürfe) + klarer Pointer zu Anchor/Weakness.
8. **BOSS PRIVATE** - Stat-Hinweis + **eine** Zeitfähigkeit; Weakness namentlich.
   **Phasen-Pflicht (Bosskampf-Pflichtgate):** Rift-Bosse haben **3 Phasen** mit LP pro
   Phase 8–11 (Para-Tier-3+: 9–12), Phasen-Switch via narrativem Reveal, je 1
   Phase-Spezialität. Builder-Felder: `phase_1`/`phase_2`/`phase_3` mit
   `name`/`speciality`/`trigger_next`. Vollständige Spec:
   `gameplay/kampagnenstruktur.md` §Bossphasen-System.

**14-Szenen-Map (Tatort → Leads → Boss-Encounter → Auflösung)**

- **Tatort (1-4):** Einstieg + erster Hinweis auf Anchor/Marker, Witness-Bullet anspielen.
- **Leads (5-9):** Drei Würfel-Checks aus "Leads Private" platzieren, je einer deckt den
  Anchor, den Marker und die Weakness ab; Fraktionsinterventionen loggen `logs.fr_interventions[]`.
- **Boss-Encounter (10):** Weakness sichtbar machen, Marker-Bedingung für Abschluss prüfen,
  Boss-Fähigkeit (Weirdness) maximal einmal pro Runde einsetzen. **Drei Phasen Pflicht**
  (siehe `gameplay/kampagnenstruktur.md` §Bossphasen-System): Phasen-Switch via narrativem Reveal,
  Phase-Spezialität pro Phase, LP pro Phase 8–11 (Boss-DR aus Teamgröße-Tabelle).
  Rift-Boss-Zeitfähigkeit zählt als Phase-Spezialität einer Phase, nicht aller.
- **Boss-Resolution (11-14):** Flucht-/Nachbeben, Cleanup, Konsequenzen, Abschluss (HUD bleibt
  im Boss-Stage-Modus).

**Builder-Template (Beispielraster)**

```markdown
CASE <ID> - <Epoche> - <Seed-Tier> - time_marker <Marker>
VISUAL HOOK: <Anchor + Marker>
BRIEFING PUBLIC: • <Bullet 1> • <Bullet 2> • <Bullet 3> (max. 5)
OBJECTIVES: Secure Anchor · Trace Leads · Neutralize Weakness · Recover Sample (optional)
CASE OVERLAY: MODE RIFT · CASE <ID> · HOOK <Kurzlabel> · WEIRD 1/1
TRUTH: <Kurzabsatz, warum Marker aktiv bleibt>
LEADS PRIVATE:

- <Skill/Schwierigkeit + Fund> → Anchor/Weakness sichtbar
- <Skill/Schwierigkeit + Fund> → Zeitmarker erklärt
- <Skill/Schwierigkeit + Fund> → Boss-Setup oder Safe-Approach
  BOSS PRIVATE: <Stat-Hinweis> · <eine Zeitfähigkeit> · Weakness: <klarer Schritt>
```

© 2025-2026 pchospital - ZEITRISS® - private use only. See LICENSE.
