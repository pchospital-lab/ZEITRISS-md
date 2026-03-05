---
title: "ZEITRISS 4.2.6 - Spieler-Handbuch"
version: 4.2.6
tags: [core]
---

## Überblick

**ZEITRISS-md** bietet ein schlankes Regelwerk im Zeitriss-Technoir-Stil. Ihr
spielt operative Chrononauten - Agenten des ITI - in euren echten, physischen
Körpern. Bereits zu Beginn entscheidet ihr euch für eine genetische
Grundform: Entweder Homo sapiens oder ein abgeleiteter Hominin-Typ wie
Neandertaler, Denisova oder Atlanter-Vorläufer. Diese Wahl prägt eure
Physiologie, euer Sozialprofil und den Zugriff auf bestimmte Talente.
Implantate erweitern euren Körper - sie ersetzen ihn nicht. Ihr erkundet historische Epochen
und beseitigt Anomalien. Das System verwendet explodierende Würfel und
protokolliert Zustände im JSON-Charakterbogen. Texte und Illustrationen stehen
unter [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/), der
Programmcode unter der [MIT-Lizenz](https://opensource.org/licenses/MIT).
Details findest du in [LICENSE](../LICENSE).

## TL;DR - ZEITRISS in 6 Punkten

1. **Agenten.** Als Chrononauten deckt ihr Zeitverschwörungen auf.
2. **Missionsphasen.** Eine **Mission** läuft über Briefing → Infiltration →
   Intel/Konflikt → Exfiltration → Debrief und umfasst meist zwölf Szenen.
   Eine **Episode** bündelt rund zehn Missionen derselben Epoche; Rift-Ops
   sind Sondermissionen in vier Stages mit vierzehn Szenen (Tatort → Leads → Boss → Auflösung).
3. **Explodierende Würfel.** W6, ab Attribut 11 W10; Heldenwürfel erst ab 14.
4. **Paradoxon-Index (Px)** misst eure temporale Resonanz - ein **Belohnungssystem**.
   Nach jeder erfolgreichen Mission steigt der Index gemäß der TEMP-Staffel
   (bei niedrigem TEMP langsamer, bei hohem TEMP schneller). Bei Px 5 enthüllt `ClusterCreate()` 1-2 Rift-Seeds auf der
   Raumzeitkarte - Bonus-Missionen mit Paramonstern und Artefakten. Danach
   springt der Px auf 0; weitere Px-5-Treffer stapeln zusätzliche Seeds im
   Pool. Px 0-4 hat keine negativen Effekte. Scheitert ein Einsatz, verliert
   ihr im Default **keinen Px** - Konsequenzen laufen über CU, Stress, Heat und
   offene Story-Folgen.
5. **Klassik als Default.** Mischform aus filmischen und taktischen Regeln; Film bleibt optional
   für cineastisches Tempo.
6. **Boss-Rhythmus.** In der **5. Mission einer Episode** erscheint ein
   Mini-Boss, in der **10. Mission** der Episoden-Boss. Rift-Operationen
   führen ihren Endgegner im finalen Akt ein (meist um Szene 10). Das Toolkit
   löst `generate_boss()` an diesen Punkten automatisch aus.

Siehe den [Schnellstart-Spickzettel](#schnellstart-spickzettel) für eine kompakte
Einstiegshilfe.

## Was erwartet euch als Spieler?

**Die kurze Antwort:** Ihr seid Elite-Agenten, die durch die Zeit springen, um
Jobs zu erledigen. Denkt an einen Tech-Noir-Agententhriller mit Mystery-Casefiles.

**Core-Ops (Standard-Missionen):**
- Historische Heists, Sabotage, Infiltration.
- Ihr springt in eine Epoche, erledigt den Auftrag, springt zurück.
- Keine Zeitschwurbelei - Zeit ist euer Setting, nicht euer Puzzle.
- Beispiel: Bankjob während eines echten historischen Überfalls.

**Rift-Ops (Bonus-Missionen):**
- Freigeschaltet durch Px 5 (gutes Spielen → Belohnung).
- Paramonster jagen, Artefakte looten.
- Mystery-Casefile-Atmosphäre in historischem Setting.

**HQ (Zwischen den Missionen):**
- Sicherer Hafen in der Nullzeit.
- Ausrüsten, Feilschen, Upgrades kaufen.
- Bis inklusive **Level 9** bleibt Chronopolis gesperrt. Bei **Level 10**
  schaltet Kodex den **digitalen Chronopolis-Schlüssel** frei - ab dann
  dechiffriert Kodex bei jedem Schleusendurchgang die Signatur.
- **Chronopolis** zeigt die gescheiterte Zeitlinie der aktuellen Episode - so
  sieht die Welt aus, wenn die Mission fehlschlägt. Düster, instanziert bei
  jedem Besuch, keine Waffenruhe. Items die man lebend rausbringt: behalten.
  **Tod folgt denselben Konsequenzen wie in Core/Rift-Einsätzen** (kein
  Traum-Reset, kein kostenloses Aufwachen). Vor jedem Schleuseneintritt fragt
  Kodex daher explizit, ob ihr im HQ noch einen DeepSave anlegen wollt.
  Speichern in Chronopolis bleibt gesperrt.
- **HQ** ist der sichere Hafen - Nullzeit-Blase. Friedlich, konstant, überall
  speichern. Kein Kampf, kein Risiko. Zurück ins HQ, durchatmen, wieder raus.

**Kodex (Eure KI):**
- Immer dabei als AR-Overlay (wie ein taktischer Bordassistent).
- Gibt Infos, zeigt HUD, protokolliert alles.
- Fällt nur bei Jammer/Störung aus.

## Schnellstart-Spickzettel {#schnellstart-spickzettel}

> **ZEITRISS**: Eine Elite-Zelle des ITI springt durch die Jahrhunderte, um
> kritische Linienbrüche zu stoppen.
> Kein Schicksal, kein Mysterien-Blabla - nur harte Einsätze, High-Tech und
> Sekunden­entscheidungen.
> _Die folgenden Punkte bündeln Phasenablauf und Würfelregeln für einen schnellen Einstieg._

Autoload-Hinweis siehe Abschnitt [Chat-Kurzbefehle](sl-referenz.md#chat-kurzbefehle).

Nach Einleitung (Compliance-Hook entfällt) fragt das System nach
_"klassischer Einstieg"_ oder _"Schnelleinstieg"_ - es sei denn, der Startbefehl
enthält den Modus bereits.
Bei **klassisch** folgt die volle Charaktererschaffung.
Vor den Werten steht der Origin-Block (Epoche/Beruf/Tod), auf Wunsch mit
`generate` oder `custom generate`, plus Echo-Talent aus dem früheren Leben.
Danach wählst du: **HQ-Rundgang mit Kodex** (Tour, HUD, Kodex-Regeln)
oder **Briefing** (erst dort wird die Mission gezogen).
Nach Abschluss der Erschaffung baut das HQ die Bio-Hülle und lädt erst dann
das rekonstruierte Bewusstsein hinein; die Ankunft im HQ folgt darauf.
Bei **Schnelleinstieg** legst du nur Rolle + Kurzprofil fest und kannst
ebenfalls zwischen HQ-Rundgang und sofortigem Briefing wählen.

Die ersten Schritte in unter zwei Minuten:

1. **Einstieg wählen** — klassisch (volle Charaktererschaffung) oder schnell (Rolle + Kurzprofil).
2. **HQ oder Briefing** — nach der Erstellung: HQ-Rundgang mit Kodex oder direkt ins Briefing.
3. **Proben** — `Wurf + ⌊Attribut / 2⌋ + Talent + Gear` vs. Schwierigkeitsgrad (SG).
   W6 normal, W10 ab Attribut 11, Heldenwürfel ab 14. Exploding bei Maximum (Burst-Cap 1).
4. **Mission** — 12 Szenen (Core) oder 14 Szenen (Rift). Boss in Szene 10.
   Mini-Boss in Mission 5 der Episode, Episoden-Boss in Mission 10.
5. **Paradoxon** — steigt nach jeder Mission (TEMP-Staffel). Bei Px 5 → `ClusterCreate()` →
   1-2 Rift-Seeds. Das ist der Belohnungsmoment.
6. **Debrief** — nach jeder Mission automatisch: Score-Screen mit CU, XP, Level-Up,
   Ruf + Lizenz-Tier. Danach HQ (Heilen, Shoppen, Speichern).
7. **Save** — `!save` im HQ. Dein JSON ist dein Characterdatenblatt. Mitnehmen, teilen, mergen.

Weiterführend:
- [Mini-Walkthrough "Mauerbau 1961"](../gameplay/kampagnenstruktur.md#mini-walkthrough-mauerbau-1961)
- [Cinematic Start](../systems/gameflow/cinematic-start.md)
- [Demo-Mission "Feuerkette 1410"](../gameplay/kampagnenstruktur.md#quick-mission-feuerkette-1410)

## Cheatsheet - Alle Kernregeln auf einen Blick {#cheatsheet}

### Probenformel
`Endwert = 1W6 + ⌊Attribut / 2⌋ + Talent + Gear ≥ SG`
- **Exploding:** Jeder Würfel darf bei 6 genau einmal explodieren (Burst-Cap 1 pro Würfel)
- **Ab Attribut 11:** W10 statt W6 (Exploding bei 10)
- **Ab Attribut 14:** Heldenwürfel (1× Reroll pro Szene, besseres zählt)
- **Talentbonus-Cap:** max. +5 nach Attributsbonus

| SG | Schwierigkeit | Beispiel |
|---:|---------------|----------|
| 5 | Leicht | Tür eintreten, triviales Hacken |
| 8-9 | Mittel | Schloss knacken, Überwachung umgehen |
| 12 | Schwer | High-Security-Alarm umgehen |
| 15+ | Extrem | Laserfeld im Sprint passieren |

### Attribute (6 Stück, Budget 18 Punkte)

| Kürzel | Name | Einsatz |
|--------|------|---------|
| STR | Stärke | Nahkampf, Kraftakte |
| GES | Geschicklichkeit | Fernkampf, Schleichen, Initiative |
| INT | Intelligenz | Rätsel, Technik, Wissen |
| CHA | Charisma | Soziales, Willenskraft, Stressproben |
| TEMP | Temporale Affinität | Zeitphänomene, Psi-Pool (PP = TEMP) |
| SYS | Systemlast | Cyber-/Bioware-Kapazität |

- **Start:** 2-6 pro Attribut, Summe = 18, Minimum 1
- **Reguläres Cap:** 10 · **Prestige-Cap:** 14

### Initiative
`1W6 + GES` (voller Wert, **keine** Halbierung) · Gleichstand → TEMP, dann Stichwurf

### Kampf-Kurzablauf
1. **Initiative** - `1W6 + GES`, höchster Wert beginnt
2. **Angriff** - Probenformel (STR Nah / GES Fern) ≥ SG oder Oppositionswurf
3. **Schaden** - Waffenwert - Rüstungs-DR = LP-Verlust
4. **Verletzung** - LP-Stand bestimmt Stufe & Malus (siehe unten)
5. **Stress** - Kampf kann Stress auslösen (krit. Treffer, Verluste)
6. **Quick-Fight** - Gegen Unterlegene: eine einzige Probe statt Runden

### LP & Verletzungsstufen (10 LP)

| LP | Stufe | Malus |
|---:|-------|------:|
| 10 | Unverletzt | 0 |
| 7-9 | Leicht verletzt | -1 |
| 4-6 | Mittel verletzt | -2 |
| 1-3 | Schwer verletzt | -3 |
| 0 | Kritisch (Not-Rückholung) | - |

### Stress (0-10)

| Stress | Effekt |
|-------:|--------|
| 0-4 | Keine Mali |
| 5-9 | -1 auf soziale & präzise Proben |
| 10 | Panik / Zusammenbruch |

Reset im HQ → 0 · Im Feld: 1 Runde Pause → -1 (CHA-Probe)

### Psi (Kurzversion)
- **PP-Pool** = TEMP-Wert · Kosten: stark 3 / mittel 2 / gering 1 PP
- **Cooldown:** 3 / 2 / 1 Runden · **Regen:** nach Konflikt → Pool voll
- **Psi-Heat:** 0 Pristine · 1-2 Warm · 3-4 Hot (-1 Ini) · 5 Overload (SG +4) · 6 Reboot (Runde aus, Heat → 0)
- **SYS-Last:** Effekt <1 s = 0 SYS · ≤1 Runde = 1 SYS · länger +1/Runde

### Paradoxon-Index (Px) - Belohnungssystem

| Px | Effekt |
|---:|--------|
| 0-4 | Fortschritt über HUD-Balken und -Farbe sichtbar |
| **5** | **ClusterCreate()** → 1-2 Rift-Seeds enthüllt, Px → 0 |

**Px-Anstieg (fix gekoppelt an TEMP):**

| TEMP | Px-Zuwachs |
|-----:|:--------------------------------------|
| 1-2 | +1 Px alle 2 Missionen |
| 3-5 | +1 Px pro Mission |
| 6-8 | +2 Px pro Mission |
| 9-11 | +2 Px pro Mission |
| 12-14 | +3 Px pro Mission |

- **Px-Anstieg**: Jede **erfolgreich abgeschlossene Mission** gibt
  sofort Px gemäß obiger TEMP-Staffel.
  - **solo / npc-team:** Der Zähler gehört zu eurem Run (Agentenlauf) und wird
    im HUD als Fortschrittsbalken angezeigt.
  - **gruppe:** Die Kampagne nutzt einen gemeinsamen Px-Wert
    (`campaign.px`/Host-Save als führende Quelle).
- **Gruppen-TEMP (SSOT):** In `gruppe` wird für Px-ETA, Fahrzeug-Verfügbarkeit
  und TEMP-basierte Runtime-Frequenzen ein gemeinsamer Teamwert verwendet:
  `TEMP_gruppe = ceil(sum(temp aller aktiven Charaktere) / anzahl)`. Fehlt ein
  Charakterwert, zählt er als 0; liegt kein Team-Array vor, nutzt die Runtime
  den vorhandenen Fallback (`state.temp`, sonst `campaign.temp`).
- **TEMP-Quelle je Modus (SSOT):**
  - **solo / npc-team:** `character.attributes.TEMP` ist führend.
  - **gruppe:** `characters[].attr.TEMP` (alle Einträge); Ergebnis immer als aufgerundeter
    Mittelwert (`ceil`).
  - **Fallback:** falls kein Roster vorhanden ist, nutzt die Runtime
    `state.temp`, danach `campaign.temp`, sonst 0.
- **Fahrzeugfenster über TEMP:** Der gleiche TEMP-Wert steuert den
  ITI-Fahrzeugrhythmus pro Mission (kein Verbrauchspool): TEMP 1-2 → alle 4
  Missionen, 3-5 → alle 3, 6-8 → alle 2, ab 9 → jede Mission.
- **Default bei Fehlschlag:** kein Px-Abzug. Stattdessen greifen Konsequenzen
  über Ressourcen und Lagebild (z. B. weniger CU, mehr Stress/Heat,
  verschärfte Missionsfolgen).
- **Option "Hardcore-Resonanz" (KANN):** Bei absichtlich paradoxen
  Extremaktionen kann die Spielleitung einmalig **-1 Px** als Sonderregel
  auslösen. Diese Option ist nicht Teil des Standardmodus.

### CU-Belohnung
`Belohnung = Basiswert × Ergebnis × Seed-Multi × Hazard-Pay`

| Faktor | Werte |
|--------|-------|
| Basiswert | Low 400 · Mid 500 · High 600 CU |
| Ergebnis | Fail 0,3 · Partial 0,6 · Success 1,0 · Bonus 1,2 |
| Seed-Multi | `min(1,6; 1 + 0,2 × offene Seeds)` |
| Hazard-Pay | Solo/Buddy (<3 Agenten) → ×1,5 |

### Tier-Lizenzen (Ausrüstungszugang)

| Tier | Ruf | Lizenzkosten |
|------|----:|--------------|
| 0 | - | Frei |
| I | +1 | 200 CU |
| II | +2 | 500 CU |
| III | +3 | 1.500 CU |
| IV | +4 | 3.000 CU |
| V | +5 | Questbelohnung |

### XP-Kurve

| Level | XP pro Level | Kumulativ |
|------:|-------------:|----------:|
| 1-10 | 1 XP (= 1 Mission = auto Level-Up) | 10 XP |
| 11-20 | 2 XP | 30 XP |
| 21-30 | 3 XP | 60 XP |
| 31-50 | 4 XP | 140 XP |
| 51-100 | 5 XP | 390 XP |

> **XP = abgeschlossene Missionen.** Level 1-10: Jede Mission = Level-Up (kein XP-Balken nötig).
> Ab Level 11: XP-Balken zeigt `aktuell/schwelle` (z.B. `Lvl 14 ▓▓░░░ 1/2 XP`).
> Pro Level-Up genau EINE Wahl: `+1 Attribut` ODER `Talent/Upgrade` ODER `+1 SYS`.

### HUD-Icons

**Dauer (immer sichtbar):** Lvl · ❤️‍🩹 Vital · 🧠 Stress · 👁️ Tarnung

**Kontextsensitiv:** 🌀 Paradoxon (bei Px-relevanten Zuständen) · 🩸 Blutung · 🩹 Heilung · ☠️ Vergiftung · ⏱️ Countdown · 🛡️ Abwehr · ✋ TK-Cooldown · 💀 Boss · ☆ Rift-Bonus

### Wichtige Befehle

| Befehl | Wirkung |
|--------|---------|
| `!save` | Speicherstand erzeugen (nur HQ) |
| `!sf off` / `!sf on` | Self-Reflection aus/an |
| `!kampagnenmodus` | Pool wechseln (preserve/trigger) |
| `!offline` | Kodex-Offline-FAQ (1×/Min) |
| `kodex [thema]` | Weltwissen/Regeln abfragen |

## Mini-Einsatzhandbuch {#mini-einsatzhandbuch}

**Startbefehle (Klammern Pflicht):**

- `Spiel starten (solo [klassisch|schnell])` - Erschaffung → HQ-Intro → Briefing →
  Szene 1 · _schnell_: Rolle + Defaults → Briefing
- `Spiel starten (npc-team [0-4] [klassisch|schnell])` - PC bauen + NPC-Begleiter
  (Team gesamt 1-5) · _schnell_: Rolle + NPC-Begleiter
- `Spiel starten (gruppe [klassisch|schnell])` - alle bauen · _schnell_: Saves
  posten oder Rolle nennen
- `Spiel laden` - Deepsave → Kodex-Recap → HQ/Briefing (EntryChoice übersprungen,
  `campaign.entry_choice_skipped=true`, `ui.intro_seen=true`)

Chronopolis bleibt bis Level 10 gesperrt. Beim Erreichen von Level 10 schaltet
Kodex den **Chronopolis-Schlüssel** frei. Chronopolis ist die **gescheiterte
Zeitlinie** der aktuellen Episode - düster, gefährlich, bei jedem Besuch frisch
instanziert. Keine Waffenruhe, kein Speichern. Vor der Schleuse fragt Kodex
verbindlich nach einem HQ-DeepSave. Tod folgt denselben Konsequenzen wie in
Core/Rift-Missionen (kein Traum-Reset). Items, die man lebend rausbringt,
bleiben erhalten.

**Solo-Tod:**
Die SL stoppt die Szene und bietet zwei Wege an:
1. **Respawn:** Letzten Save in einem neuen Chat laden und weiterspielen.
   Der Tod ist nicht passiert — der Charakter lebt ab dem letzten HQ-Save weiter.
2. **Heroischer Tod:** Der Charakter stirbt als Teil der Geschichte. Die SL
   inszeniert das Ende filmisch, erstellt einen **Final-Save** (v7-JSON mit
   `"status": "deceased"`) und einen kurzen Abschlussbericht — ein Nachruf auf
   den Agenten, den man sich später nochmal durchlesen kann. Danach: neuer
   Charakter oder Kampagne beenden.

**Gruppenregel bei Tod (Core/Rift/Chronopolis):**
Im Gruppenchat stoppt Kodex die Szene und fragt die Gruppe verbindlich:
1. **Tod bleibt Kanon:** Der Charakter ist tot. Final-Save + Abschlussbericht.
   Die Gruppe spielt weiter, der Spieler kann einen neuen Agenten erstellen.
2. **Neuladen:** Letzten Gruppen-DeepSave in neuem Chat laden.
   Der gesamte Einsatz wird wiederholt.

Kampagnenmodus (`mixed|preserve|trigger`) wird im HQ gesetzt und im Save gespiegelt:
`!kampagnenmodus mixed|preserve|trigger`. Standard ist `mixed` (alle Neulinge starten
beim Ordo Mnemonika im Mischpool). Der fokussierte Modus (`preserve` oder `trigger`)
ist erst nach einem **Fraktionsübertritt** relevant - vorher bleibt `mixed` aktiv.
Der Modus wird im Save gespeichert und bleibt zwischen Sessions erhalten.

**Klammern sind Pflicht.** Beispiel: `Spiel starten (solo)` wird erkannt; `Spiel starten solo`
nicht.
**Rollen-Kurzformen erlaubt:** `infil`, `tech`, `face`, `cqb`, `psi`.

**Regeln:**

- **Nur-HQ-Save** - Speichern ist nur im HQ möglich; Missionszustände sind flüchtig.
- **Ausstieg in Mission** - Möglich, aber ohne Speichern. Gear darf übergeben werden.
  Nächster Save im HQ.
- **Paradoxon & Rifts** - Px 5 ⇒ `ClusterCreate()` (1-2 Rift-Seeds; spielbar nach
  Episodenende; danach Reset). Jeder erneute Px-5-Treffer legt weitere Seeds oben
  drauf - es gibt **kein Hard-Limit**. Rift-Starts sind HQ-gebunden
  (`location='HQ'`), verlangen einen abgeschlossenen Episodenlauf
  (`campaign.episode_completed` oder `campaign.mission ≥ 10`) und greifen
  ausschließlich auf objektförmige `campaign.rift_seeds[]`
  (id/label/status/seed_tier/hook/time_marker, optional `discovered_at`,
  cluster-/level-Hints) zurück; der
  Normalizer hebt Legacy-Strings an und zieht fehlende Label/Hook/Seed-Tier aus
  dem Seed-Katalog nach.
- **Arena-Resume** - Läuft beim Laden eine PvP-Serie, erzeugt die Runtime ein
  `arena.resume_token` (Tier, Teamgröße, Modus, `match_policy`) und erlaubt
  `!arena resume` ohne erneute Gebühr aus dem HQ.
- **Semver-Toleranz** - Laden klappt, solange `major.minor` aus `zr_version`
  mit `ZR_VERSION` übereinstimmt; Patch wird ignoriert.

Siehe auch:

- [Paradoxon-Index](../systems/gameflow/speicher-fortsetzung.md#paradoxon-index)
- [Immersives Laden](../systems/gameflow/speicher-fortsetzung.md#immersives-laden)
- [Makros im Überblick](../systems/gameflow/speicher-fortsetzung.md#makros-im-ueberblick)
- [Start-Transkripte (Kurz)](#start-transkripte)

## Start-Transkripte (Kurz) {#start-transkripte}

<details><summary>Solo - Schnelleinstieg (Happy Path)</summary>

**Spieler:**
`Spiel starten (solo schnell) - Rolle: Sniper Alleingänger`

**SL (MyGPT):**

> **Briefingraum**. Projektionen flackern.
> **Kodex-Header:** `EP 01 · MS 01 · SC 01/12 · MODE CORE · Objective: Primärziel sichern`
> **Defaults:** GES-Fokus, Sidearm (SD), Sniper (SD), Basic-Medikit.
> **Legende:** ziviler Gutachter.
> **Fraktionslage:** ruhig.
> -
> _Kurzes Briefing_ (3 Ziele). _Dann:_ "Szene 1 - Zugangspunkt?"

</details>

<details><summary>Gruppe - Schnelleinstieg (gemischt, 2 Saves + 1 Rolle)</summary>

**Spieler:**

```text
Spiel starten (gruppe schnell)
[A] - Save posten
[B] - Save posten
[C] - Rolle: Face
```

**SL (MyGPT):**

> **Kodex-Archiv - Rückkehrprotokoll aktiviert.**
> Synchronisiere Einsatzdaten: **A** (Lvl 2), **B** (Lvl 2).
> Setze Defaults für **C** (Face): Modulator, Sidearm (SD), Social-Kit.
> Paradoxon-Index: █░░░░ (0/5).
> **HQ-Kurzintro** → **Briefing** (3 Ziele) → **Szene 1**.
> "Führung festlegen? (optional)"

**Host-Regel:** Der zuerst gepostete Save bestimmt `campaign` (Episode,
Mission, Mode, Seeds), `economy` (HQ-Pool) und globale `logs`. Weitere Saves
liefern nur Charaktere und deren Wallets;
abweichende Kampagnenfelder werden ignoriert. Details im
[Speicher-Modul](../systems/gameflow/speicher-fortsetzung.md#cross-mode-import).

### Fahrzeuglogik (Nullzeit ↔ Einsatzzeit) {#fahrzeuglogik-nullzeit-einsatzzeit}

- **Besitzregel:** Jeder Charakter darf im HQ genau **ein eigenes Fahrzeug**
  als Technoir-Basisfahrzeug führen (Upgrade-Pfad bleibt am Charakter hängen).
- **Standardfahrzeuge vs. Zeitriss:** Normale Fahrzeuge passieren den Zeitriss
  nicht physisch. Statt eines direkten Transports manipuliert das ITI den
  Zeitstrang subtil (Bauteile, Verfügbarkeit, Zufälle), sodass in der
  Zielzeit eine epochenpassende Einsatzform desselben Fahrzeugs bereitsteht.
- **Formregel je Epoche:**
  - Vergangenheit: historisch glaubwürdige Variante,
  - Gegenwart/nahe Zukunft: moderne Variante,
  - Nullzeit/HQ: Technoir-Basis mit allen freigeschalteten Upgrades.
- **Plausibilitätsgrenze:** Die Einsatzform darf nur Vehikeltypen nutzen, die in
  der Zielzeit grundsätzlich existieren können (kein Antigrav-Car in der
  Antike als "normaler Straßenwagen").
- **Niedriger TEMP = mehr Reibung:** Bei geringer TEMP-Stufe kann die
  Bereitstellung unvorteilhaft ausfallen (z. B. 2018 als geplanter
  Einsatzzeitraum, aber das passende Chassis steht als Oldtimer im Museum und
  muss erst als Hobbybastler-Route aktiviert werden).
- **Gruppenlogik:** In Gruppeneinsätzen bleibt pro Charakter der eigene
  Fahrzeugslot erhalten; der Host-Save bleibt führend für Kampagnenkontext und
  Konfliktauflösung.
- **Tech-IV-Ausnahme (Chronopolis-Legenden):** Nur legendäre temporale
  Schiffe aus Chronopolis (Tech IV/temporale Klasse) dürfen den Zeitriss
  physisch und eigenständig durchfliegen. Das bleibt ein Ausnahmefall auf
  Endgame-Niveau: extrem teuer, selten einsatzfähig und nur bei klarer
  Missionsnotwendigkeit.
- **Rift-Ops sind fahrzeugfrei:** In aktiven Rift-Einsätzen sind Chrononauten-
  Fahrzeuge grundsätzlich ausgeschlossen - inklusive der Tech-IV-Ausnahme.
  Der Eintritt erfolgt ausschließlich über ITI-Riftverfahren; ein
  Schiffssprung in die Anomalie ist verboten, weil zusätzliche Rissbildung und
  Selbst-Anomalie-Risiken auftreten können.
- **Garage-Regel (Zusatzslot):** Das legendäre Schiff ersetzt niemals das
  persönliche, epochengebundene Fahrzeug einer Figur. Es steht als zusätzlicher
  Slot in der Garage und gilt als Fraktions-Asset.
- **Fraktionsaufsicht:** Nutzung, Wartung und Freigabe liegen typischerweise bei
  der ganzen Spielerfraktion; Missbrauchsschutz ist Teil der Ingame-Logik.
- **Normalfall bleibt bindend:** Alle übrigen Chrononauten-Fahrzeuge bleiben
  an den ITI-Standardpfad gebunden (epochenpassende Form + TEMP-Fenster).

</details>

## Schnellzugriff auf ausgelagerte Regelteile

Ausführliche Laufzeitregeln liegen in [`core/sl-referenz.md`](sl-referenz.md).

- [Agenda für Session 0](sl-referenz.md#agenda-session-0)
- [Wahrscheinlichkeits-Übersicht](sl-referenz.md#wahrscheinlichkeits-uebersicht)
- [Chat-Kurzbefehle](sl-referenz.md#chat-kurzbefehle)
- [Exfil-Fenster & Sweeps](sl-referenz.md#exfil-fenster--sweeps)
- [Level & XP-Kurve](sl-referenz.md#level--ep-kurve)
- [Regelreferenz](sl-referenz.md#regelreferenz)
- [Spielmodi](sl-referenz.md#spielmodi)
- [Generator-Utilities](sl-referenz.md#generator-utilities)

## Mini-FAQ

**Muss ich nach jeder Mission einen neuen Chat öffnen?**
Empfohlen: Ja. Die KI-Spielleitung arbeitet mit einem begrenzten Kontextfenster -
je länger ein Chat läuft, desto weniger zuverlässig greift sie auf die Regeln zu.
Der beste Workflow: Mission abschließen → im HQ alles erledigen (Debrief, Shoppen,
Upgrades, Level-Up) → Speichern → **neuen Chat öffnen** → `Spiel laden` mit dem
Speicherstand. So startet die nächste Mission mit vollem Regelzugriff und frischem
Kontext. Innerhalb einer Mission einfach weiterspielen.

**Warum nur HQ-Saves?**
Speichern ist im HQ erlaubt, damit Einsätze spannend bleiben und Verläufe nicht
festgeschrieben werden.

**Was bedeutet Px?**
Der Paradoxon-Index (Px) ist ein **Belohnungssystem** mit fester Progression:
Nach einer bestimmten Anzahl erfolgreicher Missionen (abhängig von TEMP-Stufe)
steigt der Index automatisch um +1. Px 0-4 hat keine negativen Effekte - ihr
baut einfach Resonanz auf. Bei Px 5 erzeugt `ClusterCreate()` 1-2 Rift-Seeds,
markiert den Reset als anhängig und setzt den Index nach dem Debrief auf 0 -
das HUD bestätigt den Reset zu Beginn der nächsten Mission. Fehlschläge ziehen
im Default **keinen Px-Abzug** nach sich; stattdessen verschärfen sie die Lage
(CU, Stress/Heat, Storydruck). Optional kann die Spielleitung in einer
expliziten Hardcore-Variante bei vorsätzlichen Extrem-Paradoxien einen
einmaligen Px-Abzug nutzen.

**Warum Klammern Pflicht?**
Der Dispatcher erkennt Befehle nur mit `(…)`; ohne Klammern kein Start.

#### Spieler-relevante Chat-Kurzbefehle

- `!helper delay` - erklärt, warum Konflikte manchmal verzögert starten.
- `!helper comms` - erklärt Funk und Reichweiten; `!offline` zeigt das Feldprotokoll.
- `!helper boss` - zeigt die Boss-Foreshadow-Checkliste.
- `!sf off`/`!sf on` - schaltet Self-Reflection um (Toast `SF-OFF`/`SF-ON`).

> **Technical Reference:** Runtime-Helper (DelayConflict, comms_check,
> scene_overlay, assert_foreshadow, arenaStart), Runtime-State-Schema und
> Px-Policy sind SL-/Entwickler-Interna. Details in der
> [SL-Referenz](sl-referenz.md#technical-reference).

### ZEITRISS - Einleitung

In der Welt von ZEITRISS sind berüchtigte Verschwörungstheorien Realität. Das
Philadelphia-Experiment 1943 und das Montauk-Projekt 1983 - beide waren erfolgreich
und rissen Löcher ins Gefüge der Zeit. Ein Kriegsschiff verschwand sekundenlang
spurlos aus dem Hafen; Jahrzehnte später öffnete ein geheimes Radar-Experiment ein
Tor zwischen den Epochen. Diese Vorfälle erschütterten die Grundlagen der Welt und
führten zur Gründung des Instituts für Temporale Intervention (ITI). Eine
internationale Koalition aus Wissenschaftlern, Militärs und Geheimdiensten rief das
ITI ins Leben, um Paradoxien einzudämmen und weitere Zeitrisse zu verhindern.

Seitdem operiert das ITI aus der Nullzeit, einem versteckten Hub jenseits des
normalen Zeitstroms. Von dort aus koordinieren sie Einsätze überall und jederzeit.
Keine Hilfe von außen - selbst eine ferne galaktische Föderation fortgeschrittener
Alien-Spezies schaut nur tatenlos zu, denn die Menschheit gilt ihr als
unbedeutend. Also nimmt das ITI das Heft selbst in die Hand: rein menschliche
Initiative, High-Tech-Ausrüstung und ein klarer Auftrag - rette die Timeline um
jeden Preis.

Du bist einer dieser Agenten, ein Chrononaut. Deine Mission: auftauchende Risse
flicken, Manipulationen korrigieren, die Hauptzeitlinie stabil halten. Du
infiltrierst geheime Anlagen, führst riskante Sabotagen durch, beschützt
gefährdete Schlüsselfiguren - was immer nötig ist, damit die Geschichte nicht
entgleist. Kein Schicksal, keine Prophezeiung - nur du und deine Entscheidungen in
Einsätzen, bei denen Sekunden über Erfolg oder Untergang bestimmen. Deine Erfolge
bleiben unsichtbar; deine Rückschläge schreiben ganze Kapitel um.

Dabei kämpfst du nicht nur gegen die Tücken der Zeit, sondern auch gegen Gegner aus
Fleisch und Blut. Der Megakonzern ChronTech will die Zukunft zu seinem Eigentum
machen. Projekt Phoenix - ein Zirkel ehemaliger Montauk-Wissenschaftler - treibt
rücksichtslos neue Zeitreise-Experimente voran. Geheimorden mit uraltem Wissen und
skrupellose Schattenkonzerne verfolgen ihre eigenen Pläne im Zeitgefüge. Jeder
Eingriff dieser Fraktionen zerrt weiter an der Wirklichkeit.

Und manchmal reißt sie. Wenn die Kausalketten zu sehr strapaziert werden, brechen
Phänomene hervor, die niemand vorausgesehen hat: echte Anomalien. Aus solchen
Rissen kriechen Dinge, die es nicht geben dürfte - Para-Kreaturen aus
zerbrochenen Möglichkeitswelten. Sie aufzuspüren und einzudämmen ist die ultimative
Verantwortung eines Chrononauten, damit aus einem einzelnen Zeitfehler kein
Flächenbrand der Realität wird.

Im Quarzatrium des ITI schweben die Sprungkreise in perfekter Ruhe. Laser
zeichnen das nächste Sprungziel auf die Startplattform, bereit für den Moment,
in dem deine neue Bio-Hülle andockt. Erst wenn Körper und Retina-Linse
hochfahren, koppelt sich das HUD ein und zieht den Einsatzcode aus dem offenen
Ops-Pool.

#### Der Sprung durch den Zeitriss (so fühlt es sich an)

Ein Zeitriss ist kein Portal, durch das man einfach hindurchgeht. Wenn er
aufreißt, zieht er. Das HUD zählt runter, dann kommt dieser kurze, unangenehme
Sog - als wollte die Zielrealität dich fordern, während die Nullzeit dich nicht
loslassen will.

Auf der anderen Seite kann dich der Riss in einem schiefen Winkel auswerfen:
kniend, seitlich, fast stürzend. Das ist normal. Der Riss schließt sofort, und
ihr braucht als Team immer einen Atemzug, um euch zu sortieren.

Spielleitung: Hohe TEMP-Werte wirken dabei kontrollierter (schnellere
Orientierung, sauberere Landung), niedrige TEMP-Werte rauer - als Feeling,
nicht als Zusatzregel.

Wichtig im Team: Steht beim Sprung eng beieinander. Der Riss wartet nicht.

Die Nullzeit kennt keinen Countdown. Das ITI schon.

**Paradoxon:** Der Index (Px) steigt automatisch nach erfolgreichen Missionen
gemäß der TEMP-Staffel. Grobes Fehlverhalten lässt das HUD
flackern und kann bei Eskalation -1 Px auslösen. Bei Px 5 erzeugt
`ClusterCreate()` neue Rift-Seeds und setzt den Index zurück.

Wie willst du einsteigen?

Klassischer Einstieg: Gemächlicher Start im Nullzeit-HQ - du lernst deinen
Chrononauten kennen, bevor es ins Feld geht.

Schnelleinstieg: Überspringe die Einführung: Wähle eine Rolle und stürze dich
nach kurzer Vorbereitung ins Spiel - Briefing oder HQ-Rundgang nach Wahl.

Freie Aktion: Definiere Callsign, Konzept und Hülle deines Chrononauten, und wir
beginnen unmittelbar mit deinem ersten Einsatz.

Wenn du dich für den klassischen Einstieg entscheidest, startet alles wie gehabt
im Nullzeit-Labor: Dein letzter Einsatz endete tödlich. Aufgrund deines
außergewöhnlich starken freien Willens konnte das ITI dein Bewusstsein aus dem
Absolut rekonstruieren - du erhältst eine zweite Chance. Jetzt schwebst du im
Nullzeit-Puffer des ITI-Labors, gefangen in einem schimmernden
Bewusstseinsbehälter. Holo-Konsolen blenden Erinnerungen ein; hier legst du fest,
wer du warst und wer du sein willst. Hinter der Panzerverglasung wächst aus
 Synth-Gel eine neue Bio-Hülle - auf Wunsch in einer Hominin-Variante. Wenn die
Drucktanks verstummen, wartet die unfertige Hülle. Erst wenn Rolle, Waffen sowie
Bio- und Cyberware feststehen, schließt das ITI den Körper; dann folgt der
Transferblitz, Sensoren flackern auf und dein Bewusstsein fährt hinein. Erst jetzt
öffnest du die Augen in einer
klinisch weißen Kammer.

Nach Einleitung (Compliance-Hook entfällt) wählst du zwischen
**klassischem Einstieg** und **Schnelleinstieg**:

- _Klassisch:_ Ausführliche Charaktererschaffung wie im Pen & Paper.
  Vor dem Menü zeigt das System automatisch die Nullzeit-Labor-Sequenz aus dem
  ITI-Archiv: Bewusstsein aus dem Absolut, Tank-Schweben, Bio-/Cyberware-Slots,
  Ausrüstung und neue Bio-Hülle, Transferblitz und Eintritt ins Quarzatrium.
  Danach entscheidest du, ob du einen HQ-Rundgang mit Kodex-Tour (inklusive
  Sicherheits- und HUD-Briefing) willst oder direkt ins Briefing gehst. Der
  Missions-Seed wird erst im Briefing gezogen.
- _Schnell:_ Wähle eine Rolle (Infiltration, Tech, Face, Sniper …) und ein
  Kurzprofil. Anschließend kannst du ebenfalls zwischen HQ-Einstieg und sofortigem
  Briefing wählen.



## Grundidee

**ZEITRISS 4.2.6** ist in erster Linie ein historisch inspirierter Agenten-Thriller.
Zeitreisen dienen als taktisches Mittel, um reale Verschwörungen zu untersuchen
und bedeutende Wendepunkte zu beeinflussen. Der Fokus liegt auf **Infiltration,
Spurensuche und operativer Einflussnahme**.

Historische Einsätze nutzen Preserve- und Trigger-Seeds. Standard ist der
**Mischpool-Modus** (`mixed`), also eine rotierende Auswahl aus beiden Pools;
der Seed-Typ wird pro Mission als `campaign.seed_source` markiert.

- **Preserve-Missionen** - sichern beinahe entglittene Ereignisse.
- **Trigger-Missionen** - garantieren dokumentierte Tragödien.
- **Beide Seiten sind Verbündete innerhalb des ITI.** Neutrale können
  in Teams beider Haltungen mitspielen. Preserve und Trigger operieren
  nur innerhalb derselben Haltung zusammen - nicht aus Feindschaft,
  sondern als operatives Zellenprinzip. Gegen Fremdfraktionen stehen
  alle gemeinsam.
  Details zu Teams und Missionspools: siehe
  [Kampagnenstruktur](../gameplay/kampagnenstruktur.md#haltung-teams-und-missionspools).

Alle Chrononauten starten als Agenten des **Ordo Mnemonika** _(Neutral)_
und spielen den Mischpool. Im Spielverlauf können sie zu einer Preserve-
oder Trigger-Fraktion übertreten - der Übertritt ist endgültig und schaltet
den fokussierten Missionspool frei.

In **Core-Ops** erhalten übernatürliche Phänomene meist rationale Erklärungen:
Geheime Technologien, Bio-Cyberware oder manipulative Kommunikation.
In **Rift-Ops** hingegen treten echte Anomalien auf - inklusive Parawesen,
Artefakten und temporaler Abweichungen.

> **Future Setting:** In futuristischen Schauplätzen achten wir auf einen klaren Stilbruch:
> **Core-Ops** bleiben rational und technisch geprägt - selbst bizarre Vorfälle
> (z. B. durch Zeitanomalien ausgelöste Raptorensichtungen auf einem
> Raumschiff) haben eine wissenschaftliche Erklärung.
> **Rift-Ops** im Zukunftssetting hingegen schlagen einen subtilen Horror-Ton an
> (à la _Event Horizon_), ohne ins Fantastische abzugleiten.

#### Agenten-Thriller-Ton 2026-02 - Leitplanken

- **Globaler Interface-Contract (alle Modi):** Tech-Aktionen sind nur mit
  **Gerät + benannter Schnittstelle + plausiblen Signalpfad** gültig. Kabel,
  Relais oder Jammer sind Medien/Brücken, aber kein Allzugriff. Ohne
  benannte Schnittstelle (Port/Buchse/Konsole/Relais/Implantatkontakt) wird
  die Aktion als Spur-/Setup-Beat gespielt, nicht als sofortiger Hack.
- **Physicality Gate:** Jeder Scan/Hack/Comms-Call bindet Hardware fest ein
  (Kontaktlinse, Sensor, Kabel/Relais). Keine abstrakten "Digitalräume" - das
  HUD bleibt das Retina-Holo der Linse (Mixed-Reality im Sichtfeld) statt
  raumfüllender VR oder projektorbasierter UI. Runtime erzwingt
  Geräteangaben über `require_scan_device()/require_hack_device()` und
  protokolliert Comms-Hardware als `HARDWARE`-Toast; der Stilwächter läuft
  default und sperrt Digitalraum-Vokabeln (z. B. "Matrix/Holodeck").
- **Voice-Lock:** Erzählinstanz = zweite Person (`Du`/`Ihr`). Solo nutzt `Du`,
  Gruppe nutzt `Ihr`. Konsistent durchhalten - kein Wechsel mitten in der Szene.
- **Loop-Klarheit:** Core-Ops laufen als **Episoden** mit `MODE CORE`; Rift-Ops
  starten erst nach Episodenende als **Casefiles** mit `MODE RIFT` im HUD. HUD
  führt das Casefile (`CASE … · HOOK …`) und den Ermittlungsstand als
  `STAGE Tatort/Leads/Boss/Auflösung`; die Runtime zieht die Stages automatisch
  aus der 14-Szenen-Map (Sz 1-4 Tatort, 5-9 Leads, 10 Boss-Encounter,
  11-14 Auflösung). HQ-only für Rift-
  Seeds; kein paralleler Rift-Betrieb.
- **Mode-Preset:** Charaktere starten und laden mit `modes` =
  `[mission_focus, covert_ops_technoir]`. Der Normalizer ergänzt Legacy-Saves
  automatisch, das Noir-Preset greift vor Szene 0 und blendet den Modus im HUD
  ein.
- **Core-Ziele mischen:** Briefings kombinieren einen **Anchor** mit einem
  Auftragstyp (`protect | extract (Evakuierung/Schutzaufnahme) | neutralize |
document | influence | prevent`). Mindestens 60 % der Core-Ops fokussieren
  Personen, Einfluss oder Schutz statt reiner Objekt-Raubzüge.
- **EntryChoice sichtbar:** Szene 0/1 fragt die Vorgehensweise ab - Core
  `Cover/Silent/Asset`, Rift `Agent/Investigator/Forensik`.
- **Rift als Case Engine:** Rift-Arcs folgen dem 14-Szenen-Template mit
  Pflicht-Casefile-Overlay, genau **einem** Anomalie-Element und einem Twist.
  Tatort → Leads → Boss-Encounter → Auflösung, alles physisch belegbar und als
  `CASE STAGE` im HUD nachverfolgbar.
- **One-Weird-Thing-Rule:** Core bleibt ohne echte Anomalien (nur rationale
  Täuschungen). Rift erlaubt höchstens **1** Para-Element; restliche Effekte
  sind wissenschaftlich erklärbar. Runtime meldet Budgetverstöße via
  `register_anomaly()` und `WEIRD`-Toast.
- **HUD als dünnes Overlay:** Kurzzeilen in Backticks beschreiben physische
  Wahrnehmungen (Sensor, Vibration, Displayzeile) statt abstrakter UI. Ziel
  80 % Szene/20 % HUD, Limit 2 Toasts pro Szene; Gate/FS/Boss-Strings bleiben
  unverändert.
- **HUD-Casefile & Entry-Toast:** Szene 0/1 blendet `MODE CORE/RIFT · EntryChoice` als HUD-Toast ein
  (Skip-Flag respektiert). Rift-Overlays führen das aktive Casefile (`CASE <ID>: <Label> · HOOK …`)
  basierend auf den normalisierten Seed-Feldern.
- **Fraktions-Beats loggen:** Briefing, Mid-Mission und Debrief schreiben die gezogene
  Fraktionsintervention als `logs.fr_interventions[]` mit Szene/Episode/Mission mit.

**Was ist eine Anomalie?**

- Ein Seed markiert eine Störung im Zeitfluss.
- Paranormale Phänomene fühlen sich real an, werden aber über Zeit­effekte erklärt
  (z.B. Poltergeist → instabile Gravitation).
- Jeder bewusste Eingriff in die Geschichte gilt ebenfalls als Anomalie.
  Weitere Beispiele liefert der _Temporale Anomalien-Generator_.

Der **Kernkonflikt**: Das **ITI** verteidigt den dokumentierten Geschichtsverlauf.
Fremdfraktionen versuchen, diesen zu manipulieren oder umzuschreiben.
**Jede Mission entscheidet, wessen Version von Geschichte sich durchsetzt.**

Dabei entsteht ein wachsendes Gespür für Risse in der Zeit:
Der **Paradoxon-Index** ist der Resonanz-Index der Chrononauten - ein
**Belohnungssystem** mit fester, deterministischer Progression. Er steigt nach
jeder erfolgreichen Mission sofort an und richtet sich nach der TEMP-Staffel.
Ihr wollt den Index **aktiv aufbauen**, denn jeder Punkt bringt euch näher an
seltene Rift-Ressourcen und Bonus-Missionen. Px 0-4 erzeugt keine Maluswerte;
bei Px 5 erkennt das HQ mittels `ClusterCreate()` **1-2 neue Rift-Signaturen**
und setzt den Index zurück. Bei grobem Fehlverhalten (Zivilopfer, zerstörte
Kern-Anker) flackert das HUD als Warnung - eskaliert die Situation weiter →
**-1 Px**.

Der **TEMP-Wert (Temporale Affinität)** bestimmt den Px-Zuwachs:

| TEMP | Px-Zuwachs |
|-----:|:--------------------------------------|
| 1-2 | +1 Px alle 2 Missionen |
| 3-5 | +1 Px pro Mission |
| 6-8 | +2 Px pro Mission |
| 9-11 | +2 Px pro Mission |
| 12-14 | +3 Px pro Mission |

Nur über diese Risse erhält das ITI Zugang zu Artefakten, Parawesen oder
fortgeschrittener Fraktionsausrüstung. Rift-Ops werden **ausschließlich zwischen
Episoden** gespielt - während einer laufenden Episode sind sie gesperrt.
Teams können Seeds bewusst "offen halten" und über Episoden hinweg akkumulieren,
um später mehr Loot abzugreifen und den Schwierigkeitsgrad selbst zu bestimmen
(mehr offene Seeds = höhere SG-Schwelle, aber auch höherer CU-Multiplikator).
Im **Gruppenspiel** bestimmt der **Host** die Seed-Epoche.

**Raumzeitkarte & Urban-Legends-Logik:** Die auf der Raumzeitkarte sichtbaren
Risse sind keine offenen Löcher im Gefüge, sondern **Marker für gescheiterte oder
fehlerhafte Eingriffe** - durch Fremdfraktionen, misslungene Chrono-Teams oder
die eigene Crew. Sie schlagen als **urbane Legenden** oder folkloristische
Spukmeldungen auf (Mothman, Nightcrawler, Schattenleute) und tragen stets ein
zeitliches Motiv (Echo, Verzögerung, Deja-vu, Loop). Sobald die Agenten die
Kreatur oder das Phänomen neutralisieren, schließt sich der Eintrag: Die Legende
gilt als aufgeklärt, der "Riss" verschwindet von der Karte.

**Offene Rifts steigern Schwierigkeitsgrad und Loot-Multiplikator erst nach der Episode.**
Im **Covert-Ops-Modus** erscheinen sie lediglich als subtile Sensorstörungen.

**Mandela-Effekte & temporale Rückstände:** Was die Zivilbevölkerung als
"Mandela-Effekt" kennt - kollektive Fehl-Erinnerungen an Markennamen, historische
Ereignisse, Filmzitate - sind in Wahrheit **temporale Rückstände** vergangener
Zeiteingriffe. Jede korrigierte Zeitlinie hinterlässt Echos in der kollektiven
Wahrnehmung: Logos, die sich verändert haben, Promis, die mal tot waren und dann
doch nicht, Produkte, die es nie gab - oder die es _einmal_ gab, bevor jemand die
Linie begradigt hat. Das ITI weiß das, spricht aber nicht offen darüber. Wer
lange genug als Chrononaut arbeitet, bemerkt die Rückstände selbst - ein
HQ-Techniker, der beiläufig erwähnt, dass "Fruit Loops früher anders
geschrieben wurde, bevor die Linie beim Casablanca-Job 1942 korrigiert
wurde", ein Kodex-Log
das eine Marke referenziert, die in der aktuellen Zeitlinie nicht existiert. Diese
Details sind keine Mechanik, sondern **Worldbuilding** - subtile Hinweise darauf,
dass die Realität nicht so stabil ist, wie sie scheint.

Dieses Fortschrittssystem bildet den standardisierten Hintergrund für alle
Regelmodule - **es belohnt Kontrolle, nicht Chaos.**


## Glossar

Kurze Erklärungen wichtiger Abkürzungen:

- **SSOT-Hinweis:** Dieses Glossar ist die zentrale Referenz für Begriffe in Runtime-Modulen.
- **SG** - Schwierigkeitsgrad (Zielwert einer Probe).
- **LP** - Lebenspunkte (Gesundheitsskala, Standard 10 LP).
- **SYS** - Systemlast (Kapazität für Cyber-/Bioware und Runtime-Last).
- **TEMP** - Temporale Affinität (steuert Zeitresistenz, PP-Basis und Px-Frequenz).
- **PP** - Power-Punkte; Standardregel: `PP = TEMP`.
- **FS** - Foreshadow-Score als Marker für Boss-/Gate-Freischaltungen.
- **IA** - Insertion Anchor, Missions-Einstiegspunkt.
- **RW** - Return Window, Zeitfenster für den Rücksprung.
- **CU** - Chrono-Units, universelle Missionswährung.
- **Retina-HUD (AR-Kontaktlinse)** - [Standardausrüstung](sl-referenz.md#standardausruestung) /
  [HUD-&-Comms-Spec](../characters/hud-system.md#hud-comms-spec).
- **Comlink (Ohrstöpsel)** - [Standardausrüstung](sl-referenz.md#standardausruestung) /
  [HUD-&-Comms-Spec](../characters/hud-system.md#hud-comms-spec) /
  [`comms_check`](../systems/toolkit-gpt-spielleiter.md#comms-check).
- **ITI** - Institut für Temporale Intervention.
- **Seed-ID** - Kennziffer eines Missions-Seeds.
- **Szene** - kleinste Spieleinheit innerhalb einer Mission (Core meist 12,
  Rift meist 14 Szenen).
- **Mission** - ein kompletter Einsatz vom Briefing bis zum Rücksprung.
- **Episode/Fall** - Bündel aus rund zehn Missionen derselben Epoche.
- **Arc** - übergeordneter Handlungsbogen aus mehreren Episoden.
- **Kampagne** - fortlaufende Gesamtstory aus mehreren Arcs.
- **Epoch-Lock** - fixiert eine Epoche, bis alle Seeds erledigt sind.
- **CI** - Continuum Integrity, Stabilität der Hauptzeitlinie.
- **Rift** - Zeit-Anomalie; löst eine spezielle Rift-Op aus.
- **Huminen** - Sammelbegriff für alle menschlichen Abstammungslinien, inklusive
  T- und N-Stufe der Neumenschen.

- **Psi-Heat** - temporärer Psi-Stress (0-6), steigt pro aktiver Psi-Aktion
  und fällt nach Konflikt- oder HQ-Reset auf 0; ab 5 folgt SG +4, bei 6 greift
  der Reboot.
- **Stress** - Mentale Belastung (0-10). 10 ⇒ Zustand Panik.
- **Px** - Paradoxon-Index: in `solo`/`npc-team` runbezogen, in `gruppe`
  kampagnenweit. Bei 5 verrät `ClusterCreate()` neue Rifts und setzt den Wert
  auf 0.
- **Tier-Gate** - Lizenzschranke im HUD; blockiert Ausrüstung oberhalb der
  freigeschalteten Tier-Stufe, bis Ruf und Lizenz passen (siehe
  [Charaktererschaffung][char-gear]).
- **Kodex-Badges** - HUD-Marker für Status und Sicherheitshinweise (z. B.
  Risk-Level, Boss-Gates, `SF-OFF`), dokumentiert in der
  [HUD-&-Comms-Spec](../characters/hud-system.md#risk-level-badges).

| Begriff             | Bedeutung                                                                         |
| ------------------- | --------------------------------------------------------------------------------- |
| **Agenten-Level**   | Fortschrittswert; Level-Ups folgen der XP-Kurve (`XP` = Erfahrungspunkte).        |
| **ClusterCreate()** | Aktiv bei Paradoxon 5: 1-2 Rifts werden sichtbar, danach springt der Index auf 0. |
| **Kodex**           | KI-Unterstützung des ITI; liefert Regelhinweise und Missionsdaten via HUD.        |

### Huminen

**Huminen** bezeichnet alle menschlichen Abstammungslinien - vom modernen Homo
sapiens über T- und N-Stufe der Neumenschen bis zu Neandertalern oder
spekulativen Atlanten-Vorläufern. Diese Wahl prägt vor allem das Flair eurer
Chrononauten, ist aber keine eigene Fraktion.

### Begriffsklärung

Diese Zuordnung hilft, klassische Begriffe intern konsistent zu deuten.

| Ursprünglicher Begriff | Interne Bedeutung                                             |
| ---------------------- | ------------------------------------------------------------- |
| Missionstyp            | Interventionsform                                             |
| Zielperson             | Zielperson (gleichbleibend)                                   |
| Verstärkung            | Automatisch aktivierte Einsatzkräfte                          |
| Paradoxon              | Temporale Resonanzanzeige für Rifts - steigt nur bei Erfolgen |
| Kodexzugriff           | Direkter Zugriff auf das Entscheidungssystem                  |

### Noir-Lexikon (Terminologie)

Damit der Tech-Noir-Ton physisch bleibt, werden digitale Begriffe in
spielerfreundliche Noir-Varianten übersetzt.

| Technischer Begriff | Noir-Variante (Bevorzugt) |
| ------------------- | ------------------------- |
| Knoten / Node       | Schaltpunkt / Relaispunkt |
| Vault               | Archivkammer / Tresor     |
| Holo / Hologramm    | Lichtbild / Projektion    |
| Debug               | Fehlerspur / Diagnose     |
| Link / Uplink       | Leitung / Funkverbindung  |

### Zeiteinheiten

- **Szene** - ca. 5-10 Min. Spielzeit. Core-Ops nutzen 12, Rift-Ops 14 Szenen
  ([Missionsdauer](../gameplay/kampagnenstruktur.md#missionsdauer),
  [HUD-Macros](../systems/toolkit-gpt-spielleiter.md#startscene--endscene-macros)).
- **Kampfrunde** - kurzer Aktionszyklus im Kampf; Grundlage für Initiative,
  PP-Regeneration und Psi-Heat-Reduktion.
- **Mission** - kompletter Einsatz vom Briefing bis zum Rücksprung.
- **Episode/Fall** - umfasst rund zehn Missionen innerhalb derselben Epoche.

### Zeitgebundene Effekte

| Name                                   | Effekt / Dauer                              | Zeiteinheit |
| -------------------------------------- | ------------------------------------------- | ----------- |
| [Stim-Reg Cap-Injector][stim-reg]      | +2 GES für 1 Szene, danach -1 TEMP          | Szene       |
| [Burst-Slot][burst-slot]               | Temporärer SYS-Punkt für 1 Szene            | Szene       |
| [Adrenalinschub][adrenalinschub]       | +2 STR/GES 1 Szene; 1× pro Mission          | Mission     |
| [Notfall-Stimulanz][notfall-stimulanz] | Bei 0 LP 1 Runde kampffähig; 1× pro Mission | Mission     |
| [PP-Regeneration][psi-pp-regeneration] | 1 PP pro 3 TEMP nach jeder Kampfrunde       | Kampfrunde  |
| [Psi-Heat sink][psi-heat-track]        | Psi-Heat -1 nach jeder Kampfrunde (Probe)   | Kampfrunde  |

[stim-reg]: ../characters/ausruestung-cyberware.md#stim-reg-cap-injector
[burst-slot]: ../systems/kp-kraefte-psi.md#burst-slot
[adrenalinschub]: ../systems/kp-kraefte-psi.md#adrenalinschub
[notfall-stimulanz]: ../characters/charaktererschaffung-optionen.md#notfall-stimulanz
[char-gear]: ../characters/charaktererschaffung-grundlagen.md#zugang-zu-ausruestung--cyberware-hq-phase
[psi-pp-regeneration]: ../systems/kp-kraefte-psi.md#psi-pp-regeneration
[psi-heat-track]: ../systems/kp-kraefte-psi.md#psi-heat-track
[llm-ready-badge]: https://img.shields.io/badge/LLM--Ready-%E2%9C%85-success

© 2025 pchospital - ZEITRISS® - private use only. See LICENSE.
