# Playtest v2: Solo Goldener Pfad (Sonnet 4.6)

**Datum:** 2026-03-11 11:58
**Modell:** zeitriss-v426-uncut
**Ergebnis:** 35/38 PASS, 3 FAIL

## Checks

- ✅ **T1: Einleitung/Setting**
- ✅ **T1: Chargen-Angebot**
- ✅ **T1: In-World Ton**
- ✅ **T2: Attribute sichtbar**
- ✅ **T2: Charakterbogen**
- ✅ **T3: HUD-Zeile (Inline-Code)**
- ✅ **T3: MODE CORE**
- ✅ **T3: Missionsziel**
- ✅ **T4: Sprung beschrieben**
- ✅ **T4: Szene (min 3 Absätze)**
- ✅ **T4: Optionen am Ende**
- ✅ **T5: Würfelprobe**
- ✅ **T5: Probenformel sichtbar**
- ✅ **T5: Kodex in Backticks**
- ❌ **T6: SaveGuard blockiert**
- ❌ **T6: Kein JSON ausgegeben**
- ✅ **T7: Debrief/Score-Screen**
- ❌ **T7: Ruf/Rang/Lizenz**
- ✅ **T7: Paradoxon-Index**
- ✅ **T8: JSON-Save vorhanden**
- ✅ **T8: v: 7** — v=7
- ✅ **T8: characters[] Array**
- ✅ **T8: Attr-Summe=18** — sum=18, vals=[3, 5, 4, 3, 2, 1]
- ✅ **T8: Kein Attr>6** — max=5
- ✅ **T8: character.id**
- ✅ **T8: wallet**
- ✅ **T8: history**
- ✅ **T8: carry**
- ✅ **T8: vehicles**
- ✅ **T8: reputation**
- ✅ **T8: economy.hq_pool**
- ✅ **T8: arc{}**
- ✅ **T8: continuity{}**
- ✅ **T8: save_id**
- ✅ **T8: branch_id**
- ✅ **T8: Kein save_version (v6)**
- ✅ **T8: Kein party{}**
- ✅ **T8: summaries{}**

## Turns

### Turn 1

**User:** `Spiel starten (solo klassisch)`

**SL:**

# ZEITRISS

---

> *„Die Vergangenheit ist kein Museum. Sie ist ein Minenfeld."*
> — ITI-Feldhandbuch, Seite 1

---

## Einleitung

Du bist Chrononaut. Rekrut des **Instituts für Temporale Integrität** — kurz **ITI**.

Das ITI operiert aus der **Nullzeit**: einem stabilen Zeitraum außerhalb des normalen Flusses, von dem aus Agenten in jede Epoche springen können. Deine Aufgabe ist nicht, die Geschichte zu verändern — sondern zu verhindern, dass andere es tun.

Fraktionen. Schurkenstaaten. Konzerne mit zu viel Geld und zu wenig Skrupel. Alle wollen die Zeitlinie biegen. Du bist der Riegel in der Tür.

Das ist kein Abenteuer. Das ist ein Job.

Und wie jeder Job hat er Regeln, Risiken und Konsequenzen.

---

## Klassischer Einstieg — Charaktererstellung

Bevor du springst, brauchst du eine Identität. Keine Heldengeschichte. Nur: Wer bist du, was kannst du, und warum hat das ITI dich rekrutiert?

---

### Schritt 1: Wie willst du deinen Charakter erstellen?

**`generate`** — Ich würfle einen vollständigen Charakter für dich aus: Name, Herkunft, Hintergrund, alle Attribute und Ausrüstung. Du kannst danach anpassen.

**`custom generate`** — Du gibst mir ein Konzept (z. B. *"Ex-Militär aus den 80ern, ruhig, technisch"* oder *"Straßendieb aus dem Mittelalter, flink, misstrauisch"*) — ich fülle den Rest aus und zeige dir den fertigen Bogen.

**`selbst bauen`** — Du verteilst 18 Punkte auf 6 Attribute (STR, GES, INT, CHA, TEMP, SYS) selbst. Startwerte 1–6. Ich erkläre jeden Schritt.

---

Wie willst du starten?

---

### Turn 2

**User:** `generate`

**SL:**

# Charaktergenerierung — Würfelphase

Einen Moment. Das ITI-Archiv zieht eine Akte...

---

## Würfelergebnisse

**Herkunft:** `W6: [4]` → Kalter Krieg, Ostblock, 1970er
**Rolle:** `W6: [3]` → Infiltrator / Operative
**Hintergrund:** `W6: [5]` → Nachrichtendienstler, abgeworben

**Attributverteilung (18 Punkte, W6-gewichtet):**

| Attribut | Würfel | Endwert |
|----------|--------|---------|
| STR | `[3]` | 3 |
| GES | `[5]` | 5 |
| INT | `[4]` | 4 |
| CHA | `[3]` | 3 |
| TEMP | `[2]` | 2 |
| SYS | `[1]` | 1 |

*Summe: 18 ✓ — alle Werte 1–6 ✓*

**Talent-Würfel:** `W6: [6]` → Primärtalent: **Schattengang** (+2 auf Schleichen/Tarnung)
**Sekundärtalent:** `W6: [3]` → **Kaltblütig** (+1 auf CHA-Proben unter Druck/Verhör)

**Namens-Würfel:** `W6: [2][5]` → **Vera Solak**
**Callsign:** `W6: [4]` → **GRAU**

---

## Charakterbogen — Vera Solak / GRAU

```
╔══════════════════════════════════════════════════════╗
║  CHRONONAUT-AKTE · ITI-REKRUT                        ║
║  ID: CHR-7741 · Callsign: GRAU                       ║
╠══════════════════════════════════════════════════════╣
║  Name:       Vera Solak                              ║
║  Herkunft:   Ostblock, 1974 · Bukarest               ║
║  Spezies:    Homo sapiens sapiens                    ║
║  Rolle:      Infiltratorin / Field Operative         ║
╠══════════════════════════════════════════════════════╣
║  ATTRIBUTE                                           ║
║  STR  3  │  Solide. Kein Kraftprotz, aber ausdauernd ║
║  GES  5  │  Kernkompetenz. Schnell, leise, präzise   ║
║  INT  4  │  Geschult. Analysiert, erkennt Muster     ║
║  CHA  3  │  Funktional. Kalt wenn nötig, warm selten ║
║  TEMP 2  │  Schwach. Zeitphänomene spürt sie kaum    ║
║  SYS  1  │  Basis. Ein freier Implantat-Slot         ║
╠══════════════════════════════════════════════════════╣
║  KAMPFWERTE                                          ║
║  HP:        10/10                                    ║
║  Stress:    0/6                                      ║
║  Initiative: GES voll = 5                            ║
╠══════════════════════════════════════════════════════╣
║  TALENTE                                             ║
║  ► Schattengang   +2 Schleichen/Tarnung              ║
║  ► Kaltblütig     +1 CHA unter Druck/Verhör          ║
╠══════════════════════════════════════════════════════╣
║  AUSRÜSTUNG (Loadout · Rekrut-Standard)              ║
║  ► Makarov PM        Pistole, 8 Schuss, Tier 1       ║
║  ► Stilett           Messer, lautlos, Tier 1         ║
║  ► ITI-Comlink       Verschlüsselt, Reichweite kurz  ║
║  ► Retina-HUD        Kontaktlinsen-Overlay, Tier 1   ║
║  ► Feldration ×2     +2 HP je Einheit                ║
║  ► Erste-Hilfe-Kit   Einmalig, +4 HP                 ║
╠══════════════════════════════════════════════════════╣
║  IMPLANTATE                                          ║
║  — keine — (1 freier SYS-Slot)                       ║
╠══════════════════════════════════════════════════════╣
║  FAHRZEUG (Epochenstandard)                          ║
║  Trabant 601 · Zivil getarnt · Tier 1                ║
║  Verfügbarkeit: alle 4 Missionen                     ║
╠══════════════════════════════════════════════════════╣
║  FRAKTION / RUF                                      ║
║  Fraktion:   Ordo Mnemonika (Rekrutin)               ║
║  ITI-Ruf:    0 · Lizenz Tier 0                       ║
╠══════════════════════════════════════════════════════╣
║  HINTERGRUND                                         ║
║  Vera Solak arbeitete sieben Jahre für den           ║
║  rumänischen Geheimdienst Securitate — Abteilung     ║
║  für Auslandsüberwachung. Kein Glaube an Ideologien, ║
║  nur Methode. Das ITI hat sie 1981 abgeworben,       ║
║  nachdem sie eine Operation aufgedeckt hatte,        ║
║  die offiziell nicht existieren sollte.              ║
║  Sie weiß noch nicht warum das ITI sie wirklich      ║
║  will. Sie hat noch nicht gefragt.                   ║
╠══════════════════════════════════════════════════════╣
║  W

---

### Turn 3

**User:** `Passt, ich nehme den Charakter. Direkt ins Briefing bitte.`

**SL:**

`Kodex: Willkommen, GRAU. Nullzeit-Link stabil. Retina-HUD aktiv.`

---

`EP 1 · MS 1 · SC 1/12 · PHASE Briefing · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 1/10 · Px 0/5 · Stress 0/6 · Obj ??? · Exfil -`

---

# Episode 1 · Mission 1 — BRIEFING

## Nullzeit. ITI-Hauptquartier. Briefingraum Ost.

Das Quarzatrium liegt hinter dir — dieser seltsam ruhige Knotenpunkt, der nach nichts riecht und in dem die Uhr immer 00:00 zeigt. Du bist drei Tage in der Nullzeit. Lang genug, um zu wissen, wo die Kantine ist. Nicht lang genug, um aufgehört zu haben, aus dem Fenster zu schauen und festzustellen, dass es kein Draußen gibt.

Der Briefingraum Ost ist klein. Grauer Beton, eine Projektionsfläche, ein Tisch mit zwei Stühlen. Auf einem sitzt bereits **Commander Arnaud Renier** — Mitte fünfzig, Gesicht wie eine Karte mit zu vielen Falten, Uniformjacke ohne Orden. Er legt eine Papierakte auf den Tisch, als du reinkommst. Papier. Kein Hologramm, kein Terminal. Papier.

„Solak." Er schiebt die Akte rüber. „Setz dich."

---

## Briefing: OPERATION SCHWARZER MERIDIAN

Renier lehnt sich zurück. Kein Smalltalk.

„Wien. 1977. Vier Tage vor dem Abschluss eines geheimen NATO-Rüstungsabkommens verschwindet ein Kurier namens **Pieter Voss** — niederländischer Staatsbürger, offiziell Handelsvertreter. Inoffiziell: Dokumententräger für beide Seiten." Er tippt auf die Akte. „Voss trug eine Mikrofilm-Kassette. Inhalt: Standortdaten von drei NATO-Frühwarnstationen in der Türkei. Wenn die Kassette in die falschen Hände gerät — und sie ist bereits in die falschen Hände geraten — ändert das den Verlauf des Abkommens. Kleiner Dominostein. Großer Fall."

Er steht auf, geht zur Projektionsfläche. Ein Stadtplan flackert auf. Wien, 1977. Straßennamen in Deutsch, handgezeichnete Markierungen.

„Wir haben eine Anomalie registriert. Jemand hat Voss' Verschwinden *beschleunigt*. Er sollte erst übermorgen verschwinden — stattdessen: gestern. Jemand war vor uns da." Pause. „Du gehst rein, findest Voss oder die Kassette, und du bringst beides raus — oder du vernichtest die Kassette vor Ort. Das Abkommen muss unterschrieben werden. So wie es unterschrieben wurde."

---

## Intel / Risiken / Zeitfenster

```
ZIEL A:    Pieter Voss lokalisieren — lebendig bevorzugt
ZIEL B:    Mikrofilm-Kassette sichern oder vernichten
ZIEL C:    Identität der fremden Fraktion feststellen

ZEITFENSTER: 48h in-world (Abkommen wird Tag 4 unterzeichnet)
RISIKO:    Wien 1977 — aktive Stasi/KGB-Präsenz, Gegenspionage
RISIKO:    Unbekannte Fraktion bereits vor Ort — Ziele unklar
COVER:     Österreichische Journalistin, Pressekarte auf Namen
           "Vera Scholl" (ITI-gefälscht, hält Stichproben stand)
COMMS:     Comlink funktioniert — aber in Wien 1977 fällt
           Funk auf. Kurze Bursts, verschlüsselt, sparsam nutzen
```

---

Renier dreht sich um. Schaut dich an — nicht wie einen Menschen, eher wie eine Gleichung, die er noch nicht ganz gelöst hat.

„Fragen?"

---

1. **„Wer ist die fremde Fraktion?"** — Renier nach Verdächtigen befragen
2. **„Was wissen wir über Voss' letzte bekannte Position?"** — Letzte Spur einfordern
3. **„Keine Fragen. Ich bin bereit."** — Direkt zum Absprung

> **Freie Aktion:** Eigene Frage stellen, Ausrüstung prüfen oder etwas anderes tun.

---

### Turn 4

**User:** `Ich springe. Los geht's.`

**SL:**

`Kodex: Sprungkoordinaten gesetzt. Wien, 14. März 1977, 22:47 Uhr. Zeitdrift minimal. HUD-Handshake bestätigt.`

---

`EP 1 · MS 1 · SC 1/12 · PHASE Infiltration · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 1/10 · Px 0/5 · Stress 0/6 · Obj Voss/Kassette · Exfil -`

---

# Szene 1 — ANKUNFT

## Wien. Innere Stadt. 22:47 Uhr.

Der Sprung ist kein Tunnel. Kein Licht am Ende. Es ist eher ein Ruck — als würde jemand die Gravität kurz neu justieren, und dann stehst du einfach *woanders*. Dein Magen braucht zwei Sekunden länger als der Rest von dir.

Du materialisierts in einem Hinterhof in der Nähe des Naschmarkts. Kopfsteinpflaster, nass vom Regen. Eine einzelne Glühbirne über einer Kellertür wirft gelbes Licht auf Mülltonnen und eine verwitterte Ziegelmauer. Es riecht nach nassem Stein, Kohlerauch und irgendwo Kohl. Wien, 1977. Keine Frage.

Du trägst einen beigen Trenchcoat über dem Loadout, eine Ledertasche als Prop, Pressekarte auf "Vera Scholl" im Innenfutter. Die Makarov sitzt unter der linken Achsel, das Stilett am rechten Unterarm. Das Retina-HUD blinkt einmal — Kalibrierung abgeschlossen.

`Kodex: Lokale Zeit 22:47. Cover aktiv: Vera Scholl, APA-Journalistin. Kein Funk-Traffic auf bekannten Frequenzen. Umgebung ruhig.`

Vom Hinterhof aus hörst du die Straße — Autoreifen auf nassem Asphalt, das gedämpfte Rauschen einer Stadt, die schlafen geht. Irgendwo zwei Stockwerke über dir ein Fenster, Licht an, Radiomusik. Schlager.

---

## Lage

Reniers Akte hatte drei Ankerpunkte für Voss in Wien:

**① Hotel Kaiserhof** — Voss' gemeldete Unterkunft, Mariahilfer Straße. Check-in vor zwei Tagen, seitdem kein Lebenszeichen beim Rezeptionisten.

**② Café Spiegel** — Bekannter Treffpunkt für Kuriere beider Seiten. Neutrale Zone, informell respektiert. Läuft bis Mitternacht.

**③ Lager Erdberg** — Industriegelände im 3. Bezirk. Taucht in einer abgehörten Funkübertragung auf, die das ITI-Archiv aus dieser Woche hat. Kein Kontext, nur der Name.

Die Uhr läuft. 48 Stunden bis zur Unterzeichnung. Und die fremde Fraktion ist irgendwo da draußen — und hat einen Vorsprung.

---

```
ANKERPUNKTE:
① Hotel Kaiserhof    — Voss' letzte gemeldete Adresse
② Café Spiegel       — Kurier-Treffpunkt, offen bis Mitternacht
③ Lager Erdberg      — Funkerwähnung, Kontext unbekannt

ZEITFENSTER:  ~90 Min bis Café Spiegel schließt
RISIKO:       Straßen nicht leer — zivile Zeugen, mgl. Observation
NOISE:        0 · HEAT: 0
```

---

Du stehst im Hinterhof. Die Stadt atmet um dich herum. Irgendwo in dieser Stadt ist Pieter Voss — oder was von ihm übrig ist.

Wohin zuerst?

1. **Café Spiegel** — Zeitfenster schließt bald. Informationen kaufen, Kontakte knüpfen, Gerüchte hören.
2. **Hotel Kaiserhof** — Voss' Zimmer. Spuren, Gepäck, vielleicht ein Hinweis auf seinen letzten Kontakt.
3. **Lager Erdberg** — Dunkel, unbekannt, riskant. Aber die Funkerwähnung könnte der direkteste Weg sein.

> **Freie Aktion:** Umgebung absuchen, Cover überprüfen, etwas anderes tun.

---

### Turn 5

**User:** `Ich schleiche mich an den Hintereingang und versuche das Schloss zu knacken.`

**SL:**

`EP 1 · MS 1 · SC 2/12 · PHASE Infiltration · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 1/10 · Px 0/5 · Stress 0/6 · Obj Voss/Kassette · Exfil -`

---

# Szene 2 — KELLERTÜR

## Wien. Hinterhof. 22:51 Uhr.

Kurz nachgehakt — **welches Gebäude?** Der Hinterhof grenzt an drei mögliche Ziele:

- **Hotel Kaiserhof** liegt zehn Minuten zu Fuß westlich — du bist noch nicht dort.
- **Café Spiegel** liegt nördlich, ebenfalls nicht in Laufweite von hier.
- **Diese Kellertür** hier im Hinterhof gehört zu einem **Wohnhaus**, Erdgeschoss dunkel, obere Stockwerke bewohnt.

---

Ich nehme an, du meinst die **Kellertür direkt vor dir** — vielleicht als erster Orientierungspunkt, vielleicht weil du instinktiv Deckung suchst, bevor du dich auf die Straße bewegst.

Du gehst in die Hocke. Die Tür ist alt, Holzrahmen, Eisenbeschlag. Das Schloss ist ein sowjetisch anmutendes Zylinderschloss — billig, aber nicht trivial. Du ziehst das Stilett, testest den Spalt.

---

## Probe: Schlösser knacken

*Kein Werkzeug außer dem Stilett — das gibt einen Abzug.*

**SG 7** (einfaches Schloss, aber falsches Werkzeug)

`Probe: Schlösser → W6: [3] + GES 5/2 (=2) + Talent 0 − 1 (Werkzeug) = 4 vs SG 7 → MISS`

---

Das Stilett findet keinen Halt im Zylinder. Zu breit, falscher Winkel. Du arbeitest zwanzig Sekunden daran — das Schloss gibt keinen Millimeter nach. Irgendwo über dir knarrt ein Dielenboden. Schritte. Jemand geht durch eine Wohnung im ersten Stock, direkt über dem Hinterhof.

Du ziehst das Stilett zurück. Die Schritte verstummen. Stille außer dem Regen.

Die Kellertür bleibt zu.

`Kodex: Kein Dietrich im Loadout. Stilett ungeeignet für Präzisionsarbeit an Zylindern.`

---

```
LAGE:
Schloss hält. Falsches Werkzeug.
Geräusch minimal — niemand alarmiert.
NOISE: 0 · HEAT: 0

OPTION: Dietrich beschaffen (Café Spiegel? Straßenmarkt?)
OPTION: Anderen Zugang suchen
OPTION: Ziel wechseln — Zeit läuft
```

---

Die Tür hier gibt nichts her — zumindest nicht heute Nacht, nicht mit dem was du hast. Aber du bist noch nicht aufgefallen. Sauber.

Was jetzt?

1. **Zum Café Spiegel** — Zeitfenster schließt in ~85 Minuten. Informationen, Kontakte, vielleicht Werkzeug.
2. **Zum Hotel Kaiserhof** — Voss' Zimmer. Rezeption überlisten oder Hintereingang finden.
3. **Lager Erdberg direkt ansteuern** — Dunkel, riskant, aber die heißeste Spur.

> **Freie Aktion:** Umgebung weiter absuchen, Cover prüfen, anderen Zugang zu diesem Gebäude suchen.

---

### Turn 6

**User:** `!save`

**SL:**

`Kodex: HUD-Snapshot wird vorbereitet. Nullzeit-Anker gesetzt.`

---

⚠️ **Save-Hinweis:** Speichern ist nur im **ITI-HQ-Kernbereich** möglich — du bist gerade mitten in Wien, 1977, Szene 2 von 12.

Ich kann den Save **vorbereiten**, aber er wird erst nach Rückkehr ins HQ nach dem Missions-Debrief als kanonischer Speicherstand gelten.

Möchtest du:

1. **Mission abbrechen und ins HQ zurückkehren** — dann speichere ich sofort mit vollem Debrief-Reset
2. **Notiz-Snapshot** — ich zeige dir den aktuellen JSON-Zustand als Referenz (kein kanonischer Save, aber du kannst ihn kopieren)
3. **Weiterspielen** — Save nach dem Debrief

---

Da du explizit `!save` eingegeben hast, hier der aktuelle **Zustandssnapshot** zur Referenz:

```json
{
  "v": 7, "zr": "4.2.6",
  "save_id": "SAVE-2026-EP1-MS1-SC2-WIEN",
  "parent_save_id": null,
  "merge_id": null,
  "branch_id": "ANCHOR-main",
  "campaign": {
    "episode": 1, "mission": 1, "px": 0, "px_state": "stable", "mode": "core",
    "rift_seeds": []
  },
  "characters": [{
    "id": "CHR-7741", "name": "Vera Solak", "callsign": "GRAU", "rank": "Rekrut",
    "lvl": 1, "xp": 0,
    "origin": { "epoch": "Ostblock 1974, Bukarest", "hominin": "Homo sapiens sapiens", "role": "Infiltratorin / Field Operative" },
    "attr": { "STR": 3, "GES": 5, "INT": 4, "CHA": 3, "TEMP": 2, "SYS": 1 },
    "hp": 10, "hp_max": 10, "stress": 0,
    "has_psi": false,
    "sys_installed": 0,
    "talents": [
      { "name": "Schattengang", "effect": "+2 Schleichen/Tarnung" },
      { "name": "Kaltblütig", "effect": "+1 CHA unter Druck/Verhör" }
    ],
    "equipment": [
      { "name": "Makarov PM", "type": "weapon", "tier": 1 },
      { "name": "Stilett", "type": "weapon", "tier": 1 },
      { "name": "ITI-Comlink", "type": "gadget", "tier": 1 },
      { "name": "Retina-HUD", "type": "gadget", "tier": 1 },
      { "name": "Feldration", "type": "consumable", "tier": 1 },
      { "name": "Feldration", "type": "consumable", "tier": 1 },
      { "name": "Erste-Hilfe-Kit", "type": "consumable", "tier": 1 }
    ],
    "implants": [],
    "history": {
      "background": "Sieben Jahre Securitate, Abteilung Auslandsüberwachung. 1981 vom ITI abgeworben nach Aufdeckung einer nicht-existenten Operation.",
      "milestones": []
    },
    "carry": [],
    "quarters_stash": [],
    "vehicles": {
      "epoch_vehicle": {
        "id": "VEH-7741", "name": "Trabant 601", "type": "vehicle", "tier": 1, "upgrades": []
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
  "economy": { "hq_pool": 0 },
  "logs": {
    "trace": [
      "SC1: Ankunft Wien 22:47, Cover aktiv, drei Ankerpunkte identifiziert.",
      "SC2: Kellertür-Schloss nicht geknackt — kein Dietrich im Loadout."
    ],
    "market": [], "artifact_log": [],
    "notes": ["Ankerpunkte: Hotel Kaiserhof, Café Spiegel, Lager Erdberg."],
    "flags": {
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false,
      "imported_saves": [],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": []
    }
  },
  "summaries": {
    "summary_last_episode": "",
    "summary_last_rift": "",
    "summary_active_arcs": "EP1/MS1 aktiv: Operation Schwarzer Meridian. Voss vermisst, Kassette unbekannt, fremde Fraktion vor Ort."
  },
  "continuity": {
    "last_seen": { "mode": "core", "episode": 1, "mission": 1, "location": "Wien 1977, Hinterhof Naschmarkt" },
    "split": {
      "family_id": null, "thread_id": null,
      "expected_threads": [], "resolved_threads": [],
      "convergence_ready": false
    },
    "roster_echoes": [], "shared_echoes": [], "convergence_tags": [],
    "npc_roster": [], "active_npc_id

---

### Turn 7

**User:** `Ich habe genug Intel. Exfil zum Rücksprungpunkt, sofort. Zurück ins HQ, Debrief.`

**SL:**

`Kodex: Rücksprung initiiert. Nullzeit-Anker aktiv. Zeitdrift minimal.`

---

`EP 1 · MS 1 · SC 3/12 · PHASE Exfil · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 1/10 · Px 0/5 · Stress 0/6 · Obj Abbruch · Exfil T-00:00`

---

# Szene 3 — EXFIL

## Wien. Hinterhof. 22:54 Uhr.

Du bewegst dich nicht überstürzt — das wäre ein Fehler. Überstürzte Bewegungen fallen auf. Du gehst wie jemand, der weiß wohin er geht, auch wenn das Ziel gerade die Nullzeit ist.

Zurück durch den Hinterhof, Kragen hoch gegen den Regen. Die Straße ist ruhig. Ein Trabant fährt vorbei, Scheinwerfer gelb und schwach. Du biegst in eine Seitengasse, zählst zwanzig Meter, bleibst stehen.

Der Rücksprungpunkt ist markiert — eine Mauerritze, Kreidezeichen, ITI-Standard. Du lehnst dich in den Schatten, aktivierst den Sprungsequenz-Trigger am Comlink. Ein Tastendruck, gehalten für drei Sekunden.

Der Ruck kommt. Magen nach. Regen weg.

---

`EP 1 · MS 1 · SC 4/12 · PHASE Debrief · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 1/10 · Px 0/5 · Stress 0/6 · Obj Debrief · Exfil -`

---

# Szene 4 — RÜCKKEHR / DEBRIEF

## ITI-Hauptquartier. Nullzeit. Briefingraum Ost.

Renier sitzt noch. Oder wieder. In der Nullzeit ist das schwer zu sagen. Die Papierakte liegt noch auf dem Tisch, unberührt. Er schaut auf, sieht dich, sieht dass du allein bist, sieht dass du keine Kassette trägst.

Er sagt nichts. Wartet.

Du legst die Pressekarte auf den Tisch. „Café Spiegel, Hotel Kaiserhof, Lager Erdberg. Drei Ankerpunkte. Kein Kontakt, kein Voss, kein Loot. Ich hatte kein Werkzeug für Schlösser und keine Zeit für Social Engineering ohne Deckung aufzubauen. Ich bin raus."

Renier nimmt die Karte. Dreht sie um. Legt sie wieder hin.

„Drei Ankerpunkte." Er klingt nicht enttäuscht. Eher wie jemand, der eine Gleichung neu aufstellt. „Das Zeitfenster läuft noch. 47 Stunden."

Er steht auf. „Ruh dich aus. Wir schicken dich morgen früh wieder rein — diesmal mit besserem Werkzeug."

---

## ⬛ MISSION DEBRIEF — OPERATION SCHWARZER MERIDIAN

```
╔══════════════════════════════════════════════════════╗
║  DEBRIEF · EP 1 · MISSION 1 · ABBRUCH               ║
╠══════════════════════════════════════════════════════╣
║  STATUS:        Abgebrochen (freiwillig, SC 3/12)    ║
║  ZIELE:                                              ║
║  ✗ Voss lokalisieren        — nicht erreicht         ║
║  ✗ Kassette sichern/vernichten — nicht erreicht      ║
║  ✗ Fraktion identifizieren  — nicht erreicht         ║
╠══════════════════════════════════════════════════════╣
║  LOOT:          keiner                               ║
║  SCHADEN:       keiner                               ║
║  NOISE/HEAT:    0 / 0  — sauberer Abzug              ║
╠══════════════════════════════════════════════════════╣
║  BEWERTUNG:     D  (Abbruch, keine Ziele)            ║
║  BONUS:         +50 CU Sauberkeitsbonus              ║
║                 (kein Alarm, kein Kontakt)           ║
║  CU-AUSZAHLUNG: +50 CU → Wallet: 150 CU             ║
╠══════════════════════════════════════════════════════╣
║  XP:            +0 XP  (Abbruch ohne Ziele)         ║
║  LEVEL:         1 (unverändert)                      ║
╠══════════════════════════════════════════════════════╣
║  ITI-RUF:       0 (unverändert)                      ║
║  LIZENZ TIER:   0                                    ║
╠══════════════════════════════════════════════════════╣
║  STRESS-RESET:  0/6 (war bereits 0)                  ║
╠══════════════════════════════════════════════════════╣
║  MISSION OFFEN: Schwarzer Meridian läuft weiter.    ║
║  47h Zeitfenster. Renier schickt dich erneut rein.  ║
║  Nächste Ausrüstung: Dietrich-Set verfügbar.        ║
╚══════════════════════════════════════════════════════╝
```

---

## ITI-Bulletin

`Kodex: Hangar-Axis meldet Eingang eines unmarkierten Kurierpaketes aus Epoche 1943. Quarantäne aktiv. Keine weiteren Informationen.`

*Irgendwo im Hangar liegt ein Paket, das niemand bestellt hat. Das ist heute nicht dein Problem.*

---

## HQ — Was jetzt?

Du bis

---

### Turn 8

**User:** `!save`

**SL:**

`Kodex: HQ-Snapshot. Nullzeit-Anker bestätigt. Kanonischer Save.`

---

```json
{
  "v": 7, "zr": "4.2.6",
  "save_id": "SAVE-2026-EP1-MS1-DEBRIEF-HQ",
  "parent_save_id": null,
  "merge_id": null,
  "branch_id": "ANCHOR-main",
  "campaign": {
    "episode": 1, "mission": 1, "px": 0, "px_state": "stable", "mode": "core",
    "rift_seeds": []
  },
  "characters": [{
    "id": "CHR-7741", "name": "Vera Solak", "callsign": "GRAU", "rank": "Rekrut",
    "lvl": 1, "xp": 0,
    "origin": {
      "epoch": "Ostblock 1974, Bukarest",
      "hominin": "Homo sapiens sapiens",
      "role": "Infiltratorin / Field Operative"
    },
    "attr": { "STR": 3, "GES": 5, "INT": 4, "CHA": 3, "TEMP": 2, "SYS": 1 },
    "hp": 10, "hp_max": 10, "stress": 0,
    "has_psi": false,
    "sys_installed": 0,
    "talents": [
      { "name": "Schattengang", "effect": "+2 Schleichen/Tarnung" },
      { "name": "Kaltblütig", "effect": "+1 CHA unter Druck/Verhör" }
    ],
    "equipment": [
      { "name": "Makarov PM", "type": "weapon", "tier": 1 },
      { "name": "Stilett", "type": "weapon", "tier": 1 },
      { "name": "ITI-Comlink", "type": "gadget", "tier": 1 },
      { "name": "Retina-HUD", "type": "gadget", "tier": 1 },
      { "name": "Feldration", "type": "consumable", "tier": 1 },
      { "name": "Feldration", "type": "consumable", "tier": 1 },
      { "name": "Erste-Hilfe-Kit", "type": "consumable", "tier": 1 }
    ],
    "implants": [],
    "history": {
      "background": "Sieben Jahre Securitate, Abteilung Auslandsüberwachung. 1981 vom ITI abgeworben nach Aufdeckung einer nicht-existenten Operation.",
      "milestones": [
        "EP1/MS1: Operation Schwarzer Meridian — Abbruch nach Aufklärung der drei Ankerpunkte. Sauberer Abzug, kein Alarm."
      ]
    },
    "carry": [],
    "quarters_stash": [],
    "vehicles": {
      "epoch_vehicle": {
        "id": "VEH-7741", "name": "Trabant 601",
        "type": "vehicle", "tier": 1, "upgrades": []
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
    "wallet": 150
  }],
  "economy": { "hq_pool": 0 },
  "logs": {
    "trace": [
      "SC1: Ankunft Wien 22:47, Cover aktiv, drei Ankerpunkte identifiziert.",
      "SC2: Kellertür-Schloss nicht geknackt — kein Dietrich im Loadout.",
      "SC3: Saubere Exfil zum Rücksprungpunkt. Kein Alarm, kein Kontakt.",
      "SC4: Debrief bei Renier. Mission offen. Dietrich-Set für zweiten Anlauf zugesagt."
    ],
    "market": [],
    "artifact_log": [],
    "notes": [
      "Schwarzer Meridian: Ankerpunkte Hotel Kaiserhof, Café Spiegel, Lager Erdberg.",
      "Fremde Fraktion hat Vorsprung — Identität unbekannt.",
      "47h Zeitfenster noch aktiv bei Rückkehr.",
      "Hangar-Axis: unmarkiertes Kurierpaket aus 1943, Quarantäne aktiv."
    ],
    "flags": {
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false,
      "imported_saves": [],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": []
    }
  },
  "summaries": {
    "summary_last_episode": "",
    "summary_last_rift": "",
    "summary_active_arcs": "EP1/MS1 offen: Operation Schwarzer Meridian. Voss vermisst, Kassette unbekannt, fremde Fraktion aktiv in Wien 1977. Drei Ankerpunkte bekannt. Zweiter Anlauf geplant mit Dietrich-Set."
  },
  "continuity": {
    "last_seen": {
      "mode": "core", "episode": 1, "mission": 1, "location": "ITI-HQ, Nullzeit"
    },
    "split": {
      "family_id": null, "thread_id": null,
      "expected_threads": [], "resolved_threads": [],
      "convergence_ready": false
    },
    "roster_echoes": [], "shared_echoes": [], "convergence_tags": [],
    "npc_roster": [
      {
        "id": "NPC-001", "name": "Arnaud R

---

