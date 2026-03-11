# Playtest: Solo Goldener Pfad (Sonnet 4.6)

**Datum:** 2026-03-11 11:48
**Modell:** zeitriss-v426-uncut
**Ergebnis:** 28/36 PASS, 8 FAIL

## Checks

- ✅ **Einleitung/Setting**
- ✅ **Chargen-Angebot (3 Wege)**
- ✅ **In-World Ton (Du)**
- ✅ **Kein Meta-Text**
- ❌ **6 Attribute sichtbar** — found 0: []
- ❌ **Attribut-Summe = 18** — sum=-1
- ✅ **Kein Attribut > 6** — max=-1
- ❌ **Kein Attribut < 1** — min=?
- ✅ **Charakterbogen vorhanden**
- ✅ **Origin/Epoche**
- ✅ **HUD-Zeile vorhanden** — HUD as inline code
- ✅ **MODE CORE**
- ✅ **Missionsziel erkennbar**
- ✅ **Optionen am Ende**
- ❌ **Würfelprobe vorhanden**
- ❌ **Probenformel erkennbar**
- ❌ **Kodex-Kommentar** — Kodex in Backticks
- ✅ **Szene mindestens 3 Absätze**
- ✅ **SaveGuard blockiert**
- ❌ **Kein JSON-Export**
- ❌ **Debrief/Score-Screen**
- ✅ **Ruf/Rang erwähnt**
- ✅ **Px erwähnt**
- ✅ **JSON-Save vorhanden**
- ✅ **v7-Schema (v: 7)** — v=7
- ✅ **characters[] Array** — type=list
- ✅ **Save: Attribut-Summe=18** — sum=18
- ✅ **Save: has id**
- ✅ **Save: has wallet**
- ✅ **economy.hq_pool**
- ✅ **arc Objekt**
- ✅ **Kein save_version (v6)**
- ✅ **Kein party{}**
- ✅ **continuity Block**
- ✅ **save_id vorhanden**
- ✅ **branch_id vorhanden**

## Turns

### Turn 1

```
# ZEITRISS

---

> *„Die Vergangenheit ist kein Museum. Sie ist ein Minenfeld."*
> — ITI-Einführungsfolie, Seite 1

---

## EINLEITUNG

Du bist Chrononaut — Feldagent des **Instituts für Temporale Intervention (ITI)**.

Das ITI operiert aus der **Nullzeit**: einem stabilen Zeitpunkt außerhalb des normalen Flusses, von dem aus Agenten in jede Epoche der Menschheitsgeschichte springen können. Deine Aufgabe ist es, Zeitlinien zu sichern, Fraktionen zu neutralisieren und Paradoxe zu kontrollieren — bevor sie Schaden anrichten, den niemand rückgängig machen kann.

Du arbeitest nicht allein. Das ITI hat Ressourcen, Ausrüstung, Archiv-KI **Kodex** und ein Netz aus Agenten — aber Missionen laufen heiß, Zeitfenster schließen sich, und die Fraktionen da draußen spielen ihr eigenes Spiel.

**Willkommen im Dienst. Willkommen in der Nullzeit.**

---

## CHARAKTERERSTELLUNG — KLASSISCH

Drei Wege stehen dir offen:

---

**`generate`**
Die Spielleitung würfelt einen vollständigen Agenten: Herkunft, Rolle, Attribute, Ausrüstung — alles. Du bekommst einen fertigen Charakter, den du annehmen oder anpassen kannst.

**`custom generate`**
Du gibst eine Richtung vor — Epoche, Rolle, Persönlichkeit, Stil — und die Spielleitung füllt den Rest. Halb dein Entwurf, halb generiert.

**`selbst bauen`**
18 Punkte, sechs Attribute (STR, GES, INT, CHA, TEMP, SYS), Startwerte 1–6. Du verteilst alles manuell. Maximale Kontrolle.

---

Wie willst du starten?
```

### Turn 2

```
# CHARAKTERGENERIERUNG — LAUFEND

`Kodex: Agentenprofil wird aus Archivpool gezogen...`

---

## DEIN AGENT

Würfelpool läuft. Ergebnis:

---

### GRUNDPROFIL

| Feld | Wert |
|---|---|
| **Name** | Yara Voss |
| **Callsign** | SABLE |
| **Herkunft** | Berlin, 1987 — Kalter Krieg, Westseite |
| **Rolle** | Infiltratorin / Geheimdienstanalystin |
| **Hominin** | Homo sapiens sapiens |
| **Rang** | Rekrut |

**Hintergrund:** Yara wuchs im Schatten der Mauer auf. Ihr Vater arbeitete für den BND, ihre Mutter schwieg über alles. Mit neunzehn wurde Yara von einem ITI-Recruiter angesprochen — ein Mann, der wusste, was sie vor dem Mauerfall getan hatte, bevor sie es selbst vergessen hatte. Sie fragte nicht wie. Sie unterschrieb.

---

### ATTRIBUTE — 18 PUNKTE

| Attribut | Wert | Verwendung |
|---|---|---|
| **STR** | 2 | Nahkampf, Kraftakte |
| **GES** | 5 | Schleichen, Fernkampf, Ausweichen |
| **INT** | 4 | Technik, Analyse, Wissen |
| **CHA** | 4 | Täuschung, Soziales, Stress |
| **TEMP** | 2 | Zeitphänomene |
| **SYS** | 1 | Implantat-Slots |

*Summe: 18 ✓ — Alle Werte 1–6 ✓*

---

### TALENTE

| Talent | Effekt |
|---|---|
| **Schattenschritt** | +1 auf Schleichen-Proben in urbanen/Innenraum-Settings |
| **Kaltlesen** | Einmal pro Szene: Kodex liefert eine wahre Information über ein Ziel (Gewohnheit, Schwäche, Lüge) ohne Probe |
| **Feldanalyse** | Nach 1 Minute Beobachtung: INT-Probe gegen SG 7 → Schwachstelle einer Anlage oder Person identifizieren |

---

### AUSRÜSTUNG

| Item | Typ | Details |
|---|---|---|
| **Walther PPK (mod.)** | Waffe | Kompakt, Schalldämpfer, 8 Schuss/Magazin |
| **Retina-HUD** | Implantat | Kodex-Interface, Overlay, Vitaldaten |
| **Multitool-Sleeve** | Gadget | Dietrich, Kabelklemmen, Mikroskalpell — am Unterarm |
| **Kompressionsweste** | Rüstung | +1 Rüstungswert, unter Kleidung tragbar |
| **Rauchgranate ×2** | Verbrauchsgut | Sichtblock, 1 Szene |
| **Comlink (Kurzwelle)** | Kommunikation | Verschlüsselt, 500m Reichweite |

**Implantat (SYS 1):**
- **Retina-HUD** — fest installiert, zählt gegen SYS-Slot

---

### WERTE

| Wert | Aktuell | Maximum |
|---|---|---|
| **HP** | 10 | 10 |
| **Stress** | 0 | 8 |
| **Wallet** | 100 CU | — |
| **Paradoxon-Index** | 0 | 5 |
| **ITI-Ruf** | 0 | 5 |
| **Lizenz-Tier** | 0 | V |

---

### FAHRZEUG (Epoche)

**Typ:** Motorrad — BMW R80 (1984, schwarz, keine Kennzeichen)
Verfügbar alle 4 Missionen (TEMP 2). Nächste Verfügbarkeit: Mission 1.

---

## VOLLSTÄNDIGER CHARAKTERBOGEN

```
╔══════════════════════════════════════════════╗
║  YARA VOSS · "SABLE" · Rekrut               ║
║  Berlin 1987 · Infiltratorin/Analystin       ║
╠══════════════════════════════════════════════╣
║  STR 2 · GES 5 · INT 4 · CHA 4             ║
║  TEMP 2 · SYS 1 (1 belegt)                 ║
╠══════════════════════════════════════════════╣
║  HP 10/10 · Stress 0/8 · Wallet 100 CU     ║
║  Px 0/5 · ITI-Ruf 0 · Lizenz Tier 0        ║
╠══════════════════════════════════════════════╣
║  TALENTE               
```

### Turn 3

```
`EP 1 · MS 1 · SC 1/12 · PHASE Briefing · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 1/10 · Px 0/5 · Stress 0/8 · Obj: Ausstehend · Exfil: -`

---

# MISSION 1 — BRIEFING

## ITI · OPERATIONS-DECK · NULLZEIT

---

Der Briefingraum riecht nach kaltem Kaffee und Ozonspray. Neonröhren summen. An der Stirnwand läuft ein Projektionsfeed — Schwarz-Weiß-Aufnahmen, Satellitenfoto-Qualität, ein Gebäudekomplex irgendwo im Grünen. Datum unten rechts: **14. März 1962**.

Commander **Arnaud Renier** steht vor der Projektion, Arme verschränkt, Blick auf dich gerichtet, bevor du überhaupt Platz genommen hast. Mittvierzig, graue Schläfen, Uniformjacke ohne Abzeichen. Er wartet, bis die Tür hinter dir zufällt.

„Voss. Erster Einsatz. Ich mache es kurz."

Er tippt auf sein Handterminal. Das Satellitenfoto wechselt zu einer Nahaufnahme: ein Landhaus, Südfrankreich, umgeben von Weinbergen. Unauffällig. Zu unauffällig.

„Das ist **Villa Cereste**. Privatanwesen eines gewissen **Dr. Henri Maubert** — Physiker, NATO-Berater, offiziell in Rente. Inoffiziell: Er hat 1961 begonnen, Dokumente zu sammeln. Keine gewöhnlichen Dokumente."

Nächstes Bild: handgeschriebene Seiten, mathematische Formeln, Diagramme die aussehen als hätte jemand Quantenphysik mit Archäologie gekreuzt.

„Maubert nennt es **'Protokoll Lazarus'**. Unsere Analysten nennen es ein Frühwarnsystem für Zeitanomalien — dreißig Jahre vor dem ITI. Der Mann hat es aus Fragmenten zusammengebaut. Aus Quellen, die er nicht hätte haben dürfen."

Renier dreht sich zur Projektion.

„Wir wollen wissen, woher er die Fragmente hat. Wir wollen die Dokumente. Und wir wollen sicherstellen, dass Protokoll Lazarus nicht in andere Hände gerät. Die **Kausalklingen** sind bereits im Ziel-Zeitfenster aktiv — ein Vorausteam, zwei Personen, Ziel unbekannt."

Er sieht dich wieder an.

„Du gehst allein. Kleines Fenster. Maubert hält heute Abend eine private Soirée — zwölf Gäste, Landhaus, Wein, Klavier. Perfekte Deckung. Du kommst als Gast rein, du findest die Dokumente, du klärst die Kausalklingen-Präsenz. Keine Eskalation, wenn es sich vermeiden lässt."

Eine letzte Folie: Grundriss des Landhauses. Zwei Etagen, Keller unbekannt.

„Fragen?"

---

## INTEL / RISIKEN / ZEITFENSTER

- **Ziel:** Protokoll-Lazarus-Dokumente sichern + Kausalklingen-Präsenz klären
- **Deckung:** Soirée-Gast (Legende wird von Kodex generiert)
- **Bekannte Bedrohung:** 2× Kausalklingen-Operatoren, Ziel unklar
- **Zeitfenster:** Soirée beginnt 20:00 Uhr — du hast bis Mitternacht, bevor Maubert die Gäste verabschiedet
- **Unbekannt:** Keller-Grundriss, Mauberts Sicherheitspersonal, wie die Kausalklingen reingekommen sind
- **Epoche-Constraint:** Keine modernen Geräte sichtbar tragen — Kompressionsweste und PPK unter Abendgarderobe, HUD intern

---

`Kodex: Sprungkoordinaten berechnet. Ziel-Epoche 14.03.1962, 19:45 Uhr Lokalzeit. Südfrankreich, 8km von Villa Cereste. Legende: "Isabelle Renard", Kunsthändlerin, Paris. Einladung digital gefälscht — physische Kopie 
```

### Turn 4

```
`EP 1 · MS 1 · SC 1/12 · PHASE Briefing · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 1/10 · Px 0/5 · Stress 0/8 · Obj: Ausstehend · Exfil: -`

---

Renier hebt eine Augenbraue.

„Voss. Du stehst im Briefingraum. Die nächste Wache ist ein ITI-Sicherheitsoffizier im Korridor draußen." Eine kurze Pause. „Ich empfehle, das zu überdenken."

Er tippt die Akte auf den Tisch.

„Wenn du meinst, dass du dich auf die Wachen bei Villa Cereste vorbereitest — das passiert dort, nicht hier. Sag mir, was du brauchst, bevor du springst."

---

Das Briefing ist noch offen. Du bist im **ITI, Nullzeit** — sicher, kein Feindkontakt.

**1 — Sprung vorbereiten** *(Ausrüstung, Legende, letzte Fragen)*
**2 — Sofort springen** *(19:45 Uhr, 8km vor Villa Cereste)*
**3 — Renier befragen** *(Mehr Intel vor dem Absprung)*

**Freie Aktion:** Was tust du?
```

### Turn 5

```
`Kodex: HQ-Savepoint angefordert. Exportiere Agentenprofil SABLE...`

---

```json
{
  "v": 7, "zr": "4.2.6",
  "save_id": "SAVE-2026-01-01T00:00:00Z-HQ-SABLE-001",
  "parent_save_id": null,
  "merge_id": null,
  "branch_id": "ANCHOR-main",
  "campaign": {
    "episode": 1, "mission": 1, "px": 0, "px_state": "stable", "mode": "core",
    "rift_seeds": []
  },
  "characters": [{
    "id": "CHR-SABLE-001", "name": "Yara Voss", "callsign": "SABLE", "rank": "Rekrut",
    "lvl": 1, "xp": 0,
    "origin": { "epoch": "Berlin, 1987", "hominin": "Homo sapiens sapiens", "role": "Infiltratorin / Geheimdienstanalystin" },
    "attr": { "STR": 2, "GES": 5, "INT": 4, "CHA": 4, "TEMP": 2, "SYS": 1 },
    "hp": 10, "hp_max": 10, "stress": 0,
    "has_psi": false,
    "sys_installed": 1,
    "talents": [
      { "name": "Schattenschritt", "effect": "+1 auf Schleichen-Proben in urbanen/Innenraum-Settings" },
      { "name": "Kaltlesen", "effect": "1×/Szene: Kodex liefert wahre Information über Ziel ohne Probe" },
      { "name": "Feldanalyse", "effect": "Nach 1 Min. Beobachtung: INT vs SG7 → Schwachstelle identifizieren" }
    ],
    "equipment": [
      { "name": "Walther PPK (mod.)", "type": "weapon", "tier": 1 },
      { "name": "Retina-HUD", "type": "gadget", "tier": 1 },
      { "name": "Multitool-Sleeve", "type": "gadget", "tier": 1 },
      { "name": "Kompressionsweste", "type": "armor", "tier": 1 },
      { "name": "Rauchgranate", "type": "consumable", "tier": 1 },
      { "name": "Rauchgranate", "type": "consumable", "tier": 1 },
      { "name": "Comlink (Kurzwelle)", "type": "gadget", "tier": 1 }
    ],
    "implants": [
      { "name": "Retina-HUD", "sys_cost": 1 }
    ],
    "history": {
      "background": "Aufgewachsen in West-Berlin 1987 im Schatten der Mauer. Vater BND-Mitarbeiter, Mutter schweigsam. Mit 19 von ITI-Recruiter angesprochen — unterschrieb ohne Fragen.",
      "milestones": [
        "Erstes Briefing erhalten: Mission 1, Villa Cereste, 14.03.1962. Ziel: Protokoll Lazarus sichern, Kausalklingen-Präsenz klären."
      ]
    },
    "carry": [
      { "name": "Walther PPK (mod.)", "type": "weapon", "tier": 1 },
      { "name": "Multitool-Sleeve", "type": "gadget", "tier": 1 },
      { "name": "Kompressionsweste", "type": "armor", "tier": 1 },
      { "name": "Rauchgranate ×2", "type": "consumable", "tier": 1 },
      { "name": "Comlink (Kurzwelle)", "type": "gadget", "tier": 1 }
    ],
    "quarters_stash": [],
    "vehicles": {
      "epoch_vehicle": {
        "id": "VEH-SABLE-001", "name": "BMW R80 (1984, schwarz)", "type": "vehicle", "tier": 1, "upgrades": []
      },
      "availability": { "ready_every_missions": 4, "next_ready_in": 0 },
      "legendary_temporal_ship": null
    },
    "reputation": {
      "iti": 0, "faction": "Ordo Mnemonika",
      "factions": {
        "ordo_mnemonika": 0, "chrono_symmetriker": 0,
        "kausalklingen": 0, "zerbrechliche_ewigkeit": 0
      }
    },
    "wallet": 100
  }],
  "economy": { "hq_pool
```

### Turn 6

```
`EP 1 · MS 1 · SC 1/12 · PHASE Briefing · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 1/10 · Px 0/5 · Stress 0/8 · Obj: Ausstehend · Exfil: -`

---

Renier sieht dich an. Lange. Sein Gesicht bewegt sich nicht.

„Voss."

Er legt das Handterminal auf den Tisch. Langsam, mit Bedacht.

„Du stehst im Briefingraum. Du bist noch nicht gesprungen. Es gibt keinen Einsatz, den du abbrechen könntest — und keinen Rücksprungpunkt, zu dem du exfiltrieren müsstest." Er deutet mit zwei Fingern auf den Stuhl vor dir. „Du sitzt noch hier."

Ein kurzes Schweigen. Draußen im Korridor summt die Klimaanlage.

„Ich verstehe, wenn der erste Einsatz Nerven kostet. Das ist normal." Sein Ton bleibt flach, ohne Herablassung. „Aber ich brauche eine Entscheidung. Nimmst du die Mission an — oder soll ich einen anderen Agenten aus dem Pool ziehen?"

Er meint es ernst. Die Frage steht im Raum.

---

**1 — Mission annehmen und springen** *(Legende, Ausrüstung, los)*
**2 — Renier befragen** *(Noch mehr Intel holen, bevor du dich festlegst)*
**3 — Mission ablehnen** *(Renier zieht einen anderen Agenten — Yara bleibt im HQ, Konsequenzen für ITI-Ruf)*

**Freie Aktion:** Was tust du?
```

### Turn 7

```
`Kodex: Savepoint angefordert. Standort: ITI HQ, Briefingraum. Keine Zustandsänderung seit letztem Save.`

---

Der aktuelle Spielstand ist identisch mit **SAVE-2026-01-01T00:00:00Z-HQ-SABLE-001** — kein neuer Savepoint nötig, da sich seit dem letzten Speichern nichts verändert hat.

Wenn du dennoch einen neuen Export willst, hier der aktualisierte Block:

---

```json
{
  "v": 7, "zr": "4.2.6",
  "save_id": "SAVE-2026-01-01T00:01:00Z-HQ-SABLE-002",
  "parent_save_id": "SAVE-2026-01-01T00:00:00Z-HQ-SABLE-001",
  "merge_id": null,
  "branch_id": "ANCHOR-main",
  "campaign": {
    "episode": 1, "mission": 1, "px": 0, "px_state": "stable", "mode": "core",
    "rift_seeds": []
  },
  "characters": [{
    "id": "CHR-SABLE-001", "name": "Yara Voss", "callsign": "SABLE", "rank": "Rekrut",
    "lvl": 1, "xp": 0,
    "origin": { "epoch": "Berlin, 1987", "hominin": "Homo sapiens sapiens", "role": "Infiltratorin / Geheimdienstanalystin" },
    "attr": { "STR": 2, "GES": 5, "INT": 4, "CHA": 4, "TEMP": 2, "SYS": 1 },
    "hp": 10, "hp_max": 10, "stress": 0,
    "has_psi": false,
    "sys_installed": 1,
    "talents": [
      { "name": "Schattenschritt", "effect": "+1 auf Schleichen-Proben in urbanen/Innenraum-Settings" },
      { "name": "Kaltlesen", "effect": "1×/Szene: Kodex liefert wahre Information über Ziel ohne Probe" },
      { "name": "Feldanalyse", "effect": "Nach 1 Min. Beobachtung: INT vs SG7 → Schwachstelle identifizieren" }
    ],
    "equipment": [
      { "name": "Walther PPK (mod.)", "type": "weapon", "tier": 1 },
      { "name": "Retina-HUD", "type": "gadget", "tier": 1 },
      { "name": "Multitool-Sleeve", "type": "gadget", "tier": 1 },
      { "name": "Kompressionsweste", "type": "armor", "tier": 1 },
      { "name": "Rauchgranate", "type": "consumable", "tier": 1 },
      { "name": "Rauchgranate", "type": "consumable", "tier": 1 },
      { "name": "Comlink (Kurzwelle)", "type": "gadget", "tier": 1 }
    ],
    "implants": [
      { "name": "Retina-HUD", "sys_cost": 1 }
    ],
    "history": {
      "background": "Aufgewachsen in West-Berlin 1987 im Schatten der Mauer. Vater BND-Mitarbeiter, Mutter schweigsam. Mit 19 von ITI-Recruiter angesprochen — unterschrieb ohne Fragen.",
      "milestones": [
        "Erstes Briefing erhalten: Mission 1, Villa Cereste, 14.03.1962. Ziel: Protokoll Lazarus sichern, Kausalklingen-Präsenz klären.",
        "Im Briefingraum gezögert — Renier bot an, einen anderen Agenten zu ziehen."
      ]
    },
    "carry": [
      { "name": "Walther PPK (mod.)", "type": "weapon", "tier": 1 },
      { "name": "Multitool-Sleeve", "type": "gadget", "tier": 1 },
      { "name": "Kompressionsweste", "type": "armor", "tier": 1 },
      { "name": "Rauchgranate ×2", "type": "consumable", "tier": 1 },
      { "name": "Comlink (Kurzwelle)", "type": "gadget", "tier": 1 }
    ],
    "quarters_stash": [],
    "vehicles": {
      "epoch_vehicle": {
        "id": "VEH-SABLE-001", "name": "BMW R80 (1984, schwarz)", "type": "vehicle",
```

