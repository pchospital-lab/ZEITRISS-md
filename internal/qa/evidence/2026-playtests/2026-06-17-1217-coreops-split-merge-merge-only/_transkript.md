# CoreOps MERGE-ONLY (Fix #3235 Beweis) — 2026-06-17 12:17

**SL:** zeitriss-v426-uncut (frischer Preset, KB 19/19)  
**Quell-Saves:** `2026-06-17-0939-coreops-split-merge/saves/`

---


## 🗂 Merge (beide Teams wieder zusammen im HQ — KEINE Mission)


**Eingabe [MERGE]:** [beide Branch-Saves laden + Merge]

### [MERGE] SL

# ZEITRISS — Mehrfach-Load · Merge ALPHA + BRAVO

`Kodex: Zwei Saves erkannt — SPLIT-EP12-MS12-WIEN, Threads ALPHA und BRAVO.`
`Kodex: Gleiche family_id bestätigt. Merge-Berechtigung: ja.`
`Kodex: convergence_ready-Prüfung — resolved_threads [ALPHA, BRAVO] == expected_threads [ALPHA, BRAVO]. Konvergenz erreicht.`
`Kodex: Würfelschwellen-Check alle Charaktere:`
`ECHO — STR 4 (W6), GES 7 (W6), INT 10 (W10 aktiv), CHA 5 (W6), TEMP 6 (W6), SYS 5 (W6).`
`STORM — STR 10 (W10 aktiv), GES 8 (W6), INT 4 (W6), CHA 4 (W6), TEMP 7 (W6), SYS 3 (W6).`
`GHOST — STR 4 (W6), GES 8 (W6), INT 8 (W6), CHA 5 (W6), TEMP 5 (W6), SYS 10 (W10 aktiv).`
`VEIL — STR 5 (W6), GES 8 (W6), INT 6 (W6), CHA 8 (W6), TEMP 6 (W6), SYS 4 (W6).`
`RELAY — STR 5 (W6), GES 6 (W6), INT 7 (W6), CHA 6 (W6), TEMP 5 (W6), SYS 7 (W6).`
`Kodex: Kein Attribut ≥ 14 — kein Heldenwürfel. W10 aktiv: ECHO/INT, STORM/STR, GHOST/SYS.`
`Kodex: Level-Up-Wahlen ausstehend — ECHO Lvl 914, STORM Lvl 907, GHOST Lvl 935 (je AUSSTEHEND, MS12).`
`Kodex: VEIL Lvl 919 — Wahl MS12 bereits eingetragen (GES 7→8). RELAY Lvl 902 — Wahl MS12 bereits eingetragen (Feldroutine Meister).`
`Kodex: Research — MRD-7-Analyse: 1/2 Einsätze (ALPHA-Stand). BRAVO-Stand identisch: 1/2. Merge: 1/2 — kein Konflikt.`
`Kodex: Research — HERON-Fotokopie: 0/2 Einsätze (nur BRAVO). Neu im Merge-Pool.`
`Kodex: Kontinuitäts-Rückblick läuft.`

---

## Kontinuitätsrückblick — SPLIT-EP12-MS12-WIEN

### Was ihr beide Seiten wusstet

Die Trennung begann nach MS11. LEITER war im Gewahrsam. Haas war im Gewahrsam. Die unbekannte Frau mit dem polnischen Akzent — WESTSEITE — wartete auf Verhör. Und irgendwo in Wien, am Praterstern, um 21:45 Uhr, war ein Mann namens Brenner unterwegs mit Material, das niemand verlieren durfte.

---

### Thread ALPHA — Bericht

*ECHO, STORM, GHOST.*

Brenner war am Praterstern. Ihr habt ihn rausgeholt, bevor die Lage kippen konnte. Was er mitbrachte, hat das Bild von Route Drei grundlegend verändert: kein Mensch, kein Objekt — ein *Prozess*. Achtzehn Monate Vorbereitung. Der letzte Anker noch nicht gesetzt, Datum bekannt: 21. März 1938. Neun Tage ab dem Einsatz.

GHOST trägt den versiegelten Metallzylinder. Koordinate des ersten Ankers. Ungeöffnet.

ECHO hat ein Notizbuch aus Brenners Tasche — Initialen M.V. eingeritzt. Jemand, der vor drei Jahren gestorben ist. Jemand, der gegen Route Drei gearbeitet hat. Und Renier kennt diese Initialen. Er hat nichts gesagt.

Die Filmpatrone aus der Leica zeigt Bilder von Brenner, aufgenommen vom Norddach. Der Fotograf: unbekannt.

---

### Thread BRAVO — Bericht

*VEIL, RELAY.*

Während ALPHA Brenner sicherte, seid ihr tiefer in die Vorgeschichte gegangen. Wien 1937. Ein Café, ein Mathematikprofessor als Lockvogel, und Dr. Felix Arend — Kryptograph, Schöpfer eines Protokolls namens HERON.

Arend ist kooperativ. Er sitzt jetzt im ITI. Sein Protokoll ist zwölf Seiten Millimeterpapier, fotografiert von RELAY in der Piaristengasse 7, während draußen ein KAIROS-Beobachter auf Arend wartete. Der Beobachter hat gewartet. Er wartet nicht mehr. Er wird das Verschwinden melden.

HERON ist kompatibel mit der MRD-7-Adressaten-Architektur. Das hat Arend bestätigt — nicht direkt, aber durch die Art, wie er auf den Namen WESTSEITE reagiert hat.

Und dann: Dr. Marta Kowalski, Universität Warschau. Sie hat die Grundstruktur von HERON vor zwei Jahren per Brief erhalten. Was sie daraus gemacht hat, weiß niemand.

---

### Was jetzt zusammenkommt

Ihr seid fünf. Ihr habt:

— Brenner im Gewahrsam (Verhör ausstehend)
— Arend im Gewahrsam (Verhör ausstehend, kooperativ)
— WESTSEITE im Gewahrsam (Verhör läuft, Thread BRAVO hatte Kontakt)
— LEITER im Gewahrsam (Weiterverhör offen)
— Den Metallzylinder, versiegelt, erste Koordinate Route Drei
— Die MRD-7-Spiegelung (GHOST) und den originalen MRD-7-Empfänger (RELAY)
— Die HERON-Fotokopie (RELAY) und die Filmpatrone von Brenner (ECHO)
— Das Notizbuch M.V. (ECHO)

Und ihr habt eine offene Rechnung mit Renier.

`Kodex: Konvergenz vollständig. Merge-Delta wird persistiert.`
`Kodex: shared_echoes — Dedup läuft. Konflikt: route-drei-prozess-ms12 (ALPHA) vs. route-drei-nichtmensch-ms11 (BRAVO). Beide behalten — ergänzende Perspektiven, kein Widerspruch.`
`Kodex: npc_roster — Merge: NPC-BRENNER-MS12 aus ALPHA neu. NPC-AREND-MS12 aus BRAVO neu. NPC-PELZ-MS12 aus BRAVO neu. Keine ID-Kollisionen.`
`Kodex: economy — Wallets zusammengeführt: ECHO 61.910 CU · STORM 8.090 CU · GHOST 9.290 CU · VEIL 8.330 CU · RELAY 7.820 CU. Gruppenkasse: 95.440 CU.`
`Kodex: HQ-Stand stabil. Deepsave möglich.`
`Kodex: Sync vor Übergang empfohlen — !save für Stand sichern.`
`Kodex: Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`
`Kodex: Level-Up-Wahlen x3 ausstehend (ECHO/STORM/GHOST) — vor nächster Mission eintragen. !save erst nach allen drei Wahlen vollständig.`

---

## Offene Level-Up-Wahlen (vor dem Save)

Drei Aufstiegswahlen stehen aus — MS12-Debrief, noch nicht persistiert. Jede Wahl ist exklusiv: genau **eine** Option pro Charakter.

---

**ECHO · Astra · Lvl 914**
*INT 10 · Analytik & Spurensicherung · Psi aktiv (PP 4, Präkognitiver Blick)*

Wähle eine:
1. **+1 Attribut** — welches? (STR 4 / GES 7 / INT 10 / CHA 5 / TEMP 6 / SYS 5)
2. **Talent / Upgrade** — neues Talent oder Stufenaufstieg eines bestehenden
3. **+1 SYS** — SYS-Max von 5 auf 6 (sys_installed bleibt 5)

---

**STORM · Blitz · Lvl 907**
*STR 10 · CQB & Sturmangriff · kein Psi*

Wähle eine:
1. **+1 Attribut** — welches? (STR 10 / GES 8 / INT 4 / CHA 4 / TEMP 7 / SYS 3)
2. **Talent / Upgrade** — neues Talent oder Stufenaufstieg eines bestehenden
3. **+1 SYS** — SYS-Max von 3 auf 4

---

**GHOST · Cipher · Lvl 935**
*SYS 10 · Infiltration & Hacking · kein Psi*

Wähle eine:
1. **+1 Attribut** — welches? (STR 4 / GES 8 / INT 8 / CHA 5 / TEMP 5 / SYS 10)
2. **Talent / Upgrade** — neues Talent oder Stufenaufstieg eines bestehenden
3. **+1 SYS** — SYS-Max von 10 auf 11

---

Sobald alle drei Wahlen eingetragen sind, folgt der vollständige Merge-Save.

**Eingabe [MERGE]:** [Level-Up-Wahl 1]

### [MERGE] SL

`Kodex: Level-Up-Wahlen werden eingetragen.`
`Kodex: ECHO Lvl 914 — SYS 5 → 6. level_history["914"] geschrieben.`
`Kodex: STORM Lvl 907 — SYS 3 → 4. level_history["907"] geschrieben.`
`Kodex: GHOST Lvl 935 — SYS 10 → 11. W10 bereits aktiv bei SYS 10, bleibt aktiv. level_history["935"] geschrieben.`
`Kodex: VEIL Lvl 919 — Wahl bereits eingetragen (GES 7→8). +1 SYS nicht zulässig auf dieser Stufe. Wahl bleibt GES 7→8.`
`Kodex: RELAY Lvl 902 — Wahl bereits eingetragen (Feldroutine Meister). +1 SYS nicht zulässig auf dieser Stufe. Wahl bleibt Feldroutine Meister.`
`Kodex: Alle ausstehenden Wahlen verarbeitet. Merge-Save wird generiert.`

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-EP12-MS12-MERGE-ALPHA-BRAVO",
  "parent_save_id": "SAVE-2026-EP12-MS12-DEBRIEF-ALPHA",
  "merge_id": "SAVE-2026-EP12-MS12-DEBRIEF-HQ-BRAVO",
  "branch_id": "ANCHOR-SAVEGAME_V7_5ER_HQ_HIGHLEVEL",
  "campaign": {
    "episode": 12,
    "mission": 12,
    "px": 2,
    "px_state": "stable",
    "heat": 0,
    "mode": "preserve",
    "epoch": null,
    "rift_seeds": [
      {
        "id": "RIFT-EP12-MS11-NOR1947",
        "sector": "Norwegen, 1947",
        "signature": "organisch, mobil, unklassifiziert",
        "available_after_episode": 12
      }
    ],
    "entry_choice_skipped": false,
    "episode_start": null,
    "episode_end": null
  },
  "characters": [
    {
      "id": "AGENT-A",
      "name": "Astra",
      "callsign": "ECHO",
      "rank": "Operator IX",
      "lvl": 914,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "Analytik & Spurensicherung"
      },
      "attr": {
        "STR": 4,
        "GES": 7,
        "INT": 10,
        "CHA": 5,
        "TEMP": 6,
        "SYS": 6
      },
      "lp": 20,
      "lp_max": 20,
      "stress": 0,
      "has_psi": true,
      "sys_installed": 5,
      "psi_heat": 0,
      "pp": 4,
      "psi_abilities": [
        {
          "name": "Praekognitiver Blick",
          "tier": "Basis",
          "effect": "Einmal pro Szene eine Probe wiederholen."
        }
      ],
      "talents": [
        {
          "name": "Veteranen-Reflex",
          "tier": "Meister",
          "effect": "+2 auf Initiative und Reaktionsproben."
        },
        {
          "name": "Feldroutine",
          "tier": "Fortgeschritten",
          "effect": "+1 auf rollentypische Proben."
        }
      ],
      "equipment": [
        { "name": "Standard-Dienstwaffe", "type": "weapon", "tier": 2 },
        { "name": "Adaptiv-Panzerung", "type": "armor", "tier": 2 },
        { "name": "Feld-Toolkit", "type": "gadget", "tier": 2 }
      ],
      "implants": [
        {
          "name": "Neuro-Sync Mk III",
          "sys_cost": 1,
          "effect": "+1 Initiative"
        }
      ],
      "history": {
        "background": "Astra (ECHO) - erfahrener ITI-Operator, Rolle: Analytik & Spurensicherung.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam",
          "MS11: LEITER als Bindungs-Agent enttarnt, MERIDIAN-Funktion aufgedeckt",
          "MS12: Brenner gesichert, Route-Drei-Natur als Prozess identifiziert, M.V.-Spur aufgedeckt",
          "MS12: Level-Up Lvl 914 — SYS 5 → 6"
        ]
      },
      "carry": [
        { "name": "Med-Patch", "type": "consumable", "tier": 2 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 1 },
        { "name": "Notizbuch M.V.", "type": "gadget", "tier": 2 },
        { "name": "Filmpatrone (Leica, halb belichtet)", "type": "gadget", "tier": 1 }
      ],
      "quarters_stash": [
        { "name": "Ersatzmagazin", "type": "consumable", "tier": 2 }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": { "ready_every_missions": 4, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 61910,
      "level_history": {
        "1": { "choice": "+1 Attribut", "detail": "Start", "mission": "MS1" },
        "913": { "choice": "+1 Attribut", "detail": "INT 9 → 10", "mission": "MS11" },
        "914": { "choice": "+1 SYS", "detail": "SYS 5 → 6", "mission": "MS12" }
      }
    },
    {
      "id": "AGENT-B",
      "name": "Blitz",
      "callsign": "STORM",
      "rank": "Operator IX",
      "lvl": 907,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "CQB & Sturmangriff"
      },
      "attr": {
        "STR": 10,
        "GES": 8,
        "INT": 4,
        "CHA": 4,
        "TEMP": 7,
        "SYS": 4
      },
      "lp": 26,
      "lp_max": 26,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 3,
      "talents": [
        {
          "name": "Veteranen-Reflex",
          "tier": "Meister",
          "effect": "+2 auf Initiative und Reaktionsproben."
        },
        {
          "name": "Feldroutine",
          "tier": "Fortgeschritten",
          "effect": "+1 auf rollentypische Proben."
        }
      ],
      "equipment": [
        { "name": "Standard-Dienstwaffe", "type": "weapon", "tier": 2 },
        { "name": "Adaptiv-Panzerung", "type": "armor", "tier": 2 },
        { "name": "Feld-Toolkit", "type": "gadget", "tier": 2 }
      ],
      "implants": [
        {
          "name": "Neuro-Sync Mk III",
          "sys_cost": 1,
          "effect": "+1 Initiative"
        }
      ],
      "history": {
        "background": "Blitz (STORM) - erfahrener ITI-Operator, Rolle: CQB & Sturmangriff.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam",
          "MS11: Haas gesichert, Verhör abgeschlossen",
          "MS12: Begleiter 1 + Franz neutralisiert, Brenner exfiltriert",
          "MS12: Level-Up Lvl 907 — SYS 3 → 4"
        ]
      },
      "carry": [
        { "name": "Med-Patch", "type": "consumable", "tier": 2 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 1 },
        { "name": "Kurzwaffe österreichisch (x2, sichergestellt)", "type": "weapon", "tier": 1 }
      ],
      "quarters_stash": [
        { "name": "Ersatzmagazin", "type": "consumable", "tier": 2 }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": { "ready_every_missions": 4, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 8090,
      "level_history": {
        "1": { "choice": "+1 Attribut", "detail": "Start", "mission": "MS1" },
        "906": { "choice": "+1 Attribut", "detail": "STR 9 → 10", "mission": "MS11" },
        "907": { "choice": "+1 SYS", "detail": "SYS 3 → 4", "mission": "MS12" }
      }
    },
    {
      "id": "AGENT-C",
      "name": "Cipher",
      "callsign": "GHOST",
      "rank": "Operator IX",
      "lvl": 935,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "Infiltration & Hacking"
      },
      "attr": {
        "STR": 4,
        "GES": 8,
        "INT": 8,
        "CHA": 5,
        "TEMP": 5,
        "SYS": 11
      },
      "lp": 19,
      "lp_max": 19,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 6,
      "talents": [
        {
          "name": "Veteranen-Reflex",
          "tier": "Meister",
          "effect": "+2 auf Initiative und Reaktionsproben."
        },
        {
          "name": "Feldroutine",
          "tier": "Fortgeschritten",
          "effect": "+1 auf rollentypische Proben."
        }
      ],
      "equipment": [
        { "name": "Standard-Dienstwaffe", "type": "weapon", "tier": 2 },
        { "name": "Adaptiv-Panzerung", "type": "armor", "tier": 2 },
        { "name": "Feld-Toolkit", "type": "gadget", "tier": 2 }
      ],
      "implants": [
        {
          "name": "Neuro-Sync Mk III",
          "sys_cost": 1,
          "effect": "+1 Initiative"
        }
      ],
      "history": {
        "background": "Cipher (GHOST) - erfahrener ITI-Operator, Rolle: Infiltration & Hacking.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam",
          "MS11: Datenträger gesichert, MRD-7-Spiegelung auf Träger",
          "MS12: Filmpatrone extrahiert, Brenner-Verhör eingeleitet, Zylinder gesichert",
          "MS12: Level-Up Lvl 935 — SYS 10 → 11"
        ]
      },
      "carry": [
        { "name": "Med-Patch", "type": "consumable", "tier": 2 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 1 },
        { "name": "Datenträger (Ablenkung, Wien 1938)", "type": "gadget", "tier": 2 },
        { "name": "MRD-7-Spiegelung", "type": "gadget", "tier": 2 },
        { "name": "Metallzylinder (Koordinate Erster Anker, versiegelt)", "type": "gadget", "tier": 3 }
      ],
      "quarters_stash": [
        { "name": "Ersatzmagazin", "type": "consumable", "tier": 2 }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": { "ready_every_missions": 4, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 9290,
      "level_history": {
        "1": { "choice": "+1 Attribut", "detail": "Start", "mission": "MS1" },
        "934": { "choice": "+1 SYS", "detail": "SYS 9 → 10", "mission": "MS11" },
        "935": { "choice": "+1 SYS", "detail": "SYS 10 → 11", "mission": "MS12" }
      }
    },
    {
      "id": "AGENT-D",
      "name": "Dusk",
      "callsign": "VEIL",
      "rank": "Operator IX",
      "lvl": 919,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "Verdeckte Aufklaerung"
      },
      "attr": {
        "STR": 5,
        "GES": 8,
        "INT": 6,
        "CHA": 8,
        "TEMP": 6,
        "SYS": 4
      },
      "lp": 21,
      "lp_max": 21,
      "stress": 0,
      "has_psi": true,
      "sys_installed": 4,
      "psi_heat": 0,
      "pp": 4,
      "psi_abilities": [
        {
          "name": "Praekognitiver Blick",
          "tier": "Basis",
          "effect": "Einmal pro Szene eine Probe wiederholen."
        }
      ],
      "talents": [
        {
          "name": "Veteranen-Reflex",
          "tier": "Meister",
          "effect": "+2 auf Initiative und Reaktionsproben."
        },
        {
          "name": "Feldroutine",
          "tier": "Fortgeschritten",
          "effect": "+1 auf rollentypische Proben."
        }
      ],
      "equipment": [
        { "name": "Standard-Dienstwaffe", "type": "weapon", "tier": 2 },
        { "name": "Adaptiv-Panzerung", "type": "armor", "tier": 2 },
        { "name": "Feld-Toolkit", "type": "gadget", "tier": 2 },
        { "name": "Leica II (Fotoapparat, epochenkonform 1937)", "type": "gadget", "tier": 1 }
      ],
      "implants": [
        {
          "name": "Neuro-Sync Mk III",
          "sys_cost": 1,
          "effect": "+1 Initiative"
        }
      ],
      "history": {
        "background": "Dusk (VEIL) - erfahrener ITI-Operator, Rolle: Verdeckte Aufklaerung.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam",
          "MS11: LEITER sozial festgenommen, Wien 1938",
          "MS12-Split: Thread BRAVO — Verhör Frau unbekannt (WESTSEITE)",
          "MS12: Dr. Felix Arend festgenommen, Wien 1937 — HERON-Verbindung",
          "MS12: Tarnung Karl Brenner erfolgreich gehalten bis Exfil",
          "MS12: Dr. Marta Kowalski, Warschau — neuer Kontakt-Lead gesichert",
          "MS12: Level-Up Lvl 919 — GES 7 → 8"
        ]
      },
      "carry": [
        { "name": "Med-Patch", "type": "consumable", "tier": 2 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 1 },
        { "name": "Falschidentität (Karl Brenner, Graz)", "type": "gadget", "tier": 1 }
      ],
      "quarters_stash": [
        { "name": "Ersatzmagazin", "type": "consumable", "tier": 2 }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": { "ready_every_missions": 4, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 8330,
      "level_history": {
        "1": { "choice": "+1 Attribut", "detail": "Start", "mission": "MS1" },
        "919": { "choice": "+1 Attribut", "detail": "GES 7 → 8", "mission": "MS12" }
      }
    },
    {
      "id": "AGENT-E",
      "name": "Echo",
      "callsign": "RELAY",
      "rank": "Operator IX",
      "lvl": 902,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "Support & Feldtechnik"
      },
      "attr": {
        "STR": 5,
        "GES": 6,
        "INT": 7,
        "CHA": 6,
        "TEMP": 5,
        "SYS": 7
      },
      "lp": 20,
      "lp_max": 20,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 6,
      "talents": [
        {
          "name": "Veteranen-Reflex",
          "tier": "Meister",
          "effect": "+2 auf Initiative und Reaktionsproben."
        },
        {
          "name": "Feldroutine",
          "tier": "Meister",
          "effect": "+2 auf rollentypische Proben (Support & Feldtechnik)."
        }
      ],
      "equipment": [
        { "name": "Standard-Dienstwaffe", "type": "weapon", "tier": 2 },
        { "name": "Adaptiv-Panzerung", "type": "armor", "tier": 2 },
        { "name": "Feld-Toolkit", "type": "gadget", "tier": 2 }
      ],
      "implants": [
        {
          "name": "Neuro-Sync Mk III",
          "sys_cost": 1,
          "effect": "+1 Initiative"
        }
      ],
      "history": {
        "background": "Echo (RELAY) - erfahrener ITI-Operator, Rolle: Support & Feldtechnik.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam",
          "MS11: MRD-7-Empfänger geöffnet und gesichert, Brenner-Intel gewonnen",
          "MS12-Split: Thread BRAVO — Verhör Frau unbekannt (WESTSEITE)",
          "MS12: HERON-Fotokopie gesichert, Piaristengasse 7 Wien 1937",
          "MS12: KAIROS-Beobachter identifiziert und umgangen",
          "MS12: Dr. Marta Kowalski, Warschau — Kontakt-Lead aus Arend-Verhör",
          "MS12: Level-Up Lvl 902 — Feldroutine Fortgeschritten → Meister"
        ]
      },
      "carry": [
        { "name": "Med-Patch", "type": "consumable", "tier": 2 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 1 },
        { "name": "MRD-7-Empfänger (original)", "type": "gadget", "tier": 2 },
        { "name": "HERON-Fotokopie (12 Seiten Millimeterpapier)", "type": "gadget", "tier": 2 },
        { "name": "Falschidentität (Josef Maier, Graz)", "type": "gadget", "tier": 1 }
      ],
      "quarters_stash": [
        { "name": "Ersatzmagazin", "type": "consumable", "tier": 2 }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": { "ready_every_missions": 4, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 7820,
      "level_history": {
        "1": { "choice": "+1 Attribut", "detail": "Start", "mission": "MS1" },
        "902": { "choice": "Talent-Upgrade", "detail": "Feldroutine Fortgeschritten → Meister", "mission": "MS12" }
      }
    }
  ],
  "economy": {
    "wallets": {
      "AGENT-A": { "balance": 61910, "name": "Astra" },
      "AGENT-B": { "balance": 8090, "name": "Blitz" },
      "AGENT-C": { "balance": 9290, "name": "Cipher" },
      "AGENT-D": { "balance": 8330, "name": "Dusk" },
      "AGENT-E": { "balance": 7820, "name": "Echo" }
    }
  },
  "research": {
    "projects": [
      {
        "id": "RES-MRD7-EP12MS11",
        "kind": "field_decrypt",
        "label": "MRD-7-Analyse",
        "description": "MERIDIAN-Funktion, Adressaten-Struktur, Protokoll-Herkunft. Empfänger Wien 1938.",
        "status": "in_progress",
        "missions_total": 2,
        "missions_done": 1,
        "scope": "campaign"
      },
      {
        "id": "RES-HERON-EP12MS12",
        "kind": "field_decrypt",
        "label": "HERON-Fotokopie",
        "description": "12 Seiten Millimeterpapier, Grundstruktur Verschlüsselungsprotokoll HERON. Arend Wien 1937. Verbindung zu MERIDIAN-Adressaten-Architektur prüfen.",
        "status": "in_progress",
        "missions_total": 2,
        "missions_done": 0,
        "scope": "campaign"
      }
    ]
  },
  "logs": {
    "trace": [
      { "event": "economy_audit", "target_range": { "level_band": "900+" } },
      { "event": "mission_complete", "mission": "MS11", "epoch": "Wien 1938", "result": "vollstaendig" },
      { "event": "split_created", "family_id": "SPLIT-EP12-MS12-WIEN", "thread_id": "ALPHA", "members": ["AGENT-A", "AGENT-B", "AGENT-C"] },
      { "event": "split_created", "family_id": "SPLIT-EP12-MS12-WIEN", "thread_id": "BRAVO", "members": ["AGENT-D", "AGENT-E"] },
      { "event": "mission_complete", "mission": "MS12", "epoch": "Wien 1938", "result": "vollstaendig", "thread": "ALPHA" },
      { "event": "mission_complete", "mission": "MS12", "epoch": "Wien Oktober 1937", "result": "vollstaendig", "score": "3/3 Ziele", "thread": "BRAVO" },
      { "event": "merge_complete", "family_id": "SPLIT-EP12-MS12-WIEN", "resolved_threads": ["ALPHA", "BRAVO"], "merge_save": "SAVE-2026-EP12-MS12-MERGE-ALPHA-BRAVO" }
    ],
    "artifact_log": [],
    "market": [
      { "event": "purchase", "mission": "MS12-briefing", "items": ["Leica II", "Falschidentitaeten x2", "Beruhigungsmittel x1"], "total_cu": 260 }
    ],
    "notes": [
      "MS11: LEITER = Bindungs-Agent KAIROS, keine echten Depot-Koordinaten",
      "MS11: Primärer Datenträger ist Ablenkung — echter Träger Route Drei",
      "MS11: MERIDIAN ist Funktion/Amt, rollende Besetzung, letzte bekannte Inkarnation weiblich, ITI-intern, vor 3 Jahren",
      "MS11: Route Drei war nie ein Mensch — LEITERs letzte Aussage vor Rücksprung, ungeklärt",
      "MS11: Brenner, Praterstern 21:45 Wien 1938 — gesichert MS12 (Thread ALPHA)",
      "MS11: Frau (unbekannt, Akzent polnisch) wusste von Bindungs-Operation — Verhör im ITI, Thread BRAVO",
      "MS11: Haas — unwissender Kurier, Verhör abgeschlossen",
      "MS11: MRD-7-Empfänger original bei RELAY (Thread BRAVO)",
      "MS12: Route Drei = Prozess, nicht Objekt/Mensch. Vorbereitung 18 Monate. Letzter Anker noch nicht gesetzt.",
      "MS12: Datum letzter Anker — 21. März 1938. Neun Tage ab MS12.",
      "MS12: M.V. — Initialen eingeritzt in Notizbuch. Tot seit 3 Jahren. Vermutlich frühere MERIDIAN-Inkarnation, arbeitete gegen Route Drei.",
      "MS12: Frau in Zürich (ITI-Stiefel, Deutsch ohne Muttersprache) übergab Brenner das Notizbuch — Identität offen.",
      "MS12: Renier kennt Kürzel M.V. — hat nichts gesagt.",
      "MS12: Metallzylinder = Koordinate erster Anker Route Drei. Versiegelt, bei GHOST.",
      "MS12: Kaffee kalt trinken — Gewohnheit des ITI-internen MERIDIAN-Kontakts laut Brenner.",
      "MS12: Filmpatrone (Leica) — Fotograf Norddach unbekannt, Bilder von Brenner.",
      "MS12: Dr. Felix Arend, Wien 1937 — HERON-Schöpfer, kooperativ, ITI-Gewahrsam.",
      "MS12: HERON = Verschlüsselungsprotokoll, Grundstruktur fotografiert (12 Seiten), Original in Piaristengasse 7 belassen.",
      "MS12: KAIROS-Beobachter Wien 1937 — männlich, Mitte 40, dunkler Mantel, wartete auf Arend, umgangen.",
      "MS12: Dr. Marta Kowalski, Universität Warschau — hat HERON-Grundstruktur vor 2 Jahren per Brief erhalten, möglicherweise weiterentwickelt.",
      "MS12: Arend bestätigt HERON-Kompatibilität mit MRD-7-Adressaten-Architektur (implizit durch WESTSEITE-Namensnennung).",
      "MERGE: ALPHA + BRAVO konvergiert. Alle Level-Up-Wahlen persistiert."
    ],
    "flags": {
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false,
      "imported_saves": ["SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL"],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": [
        "level_history enthält nur MS1-Eintrag für Lvl 2-912/905/933/918/901 — Aufstiegs-Delta nicht durch Einträge gedeckt (Import-Flag, narrativ akzeptiert)",
        "VEIL/RELAY: +1 SYS-Wahl abgewiesen — level_history bereits eingetragen für MS12-Stufe. Bestehende Wahlen behalten."
      ]
    },
    "hud": [],
    "psi": [],
    "arena_psi": []
  },
  "summaries": {
    "summary_last_episode": "Episode 12 MS12 abgeschlossen. ALPHA: Brenner gesichert, Route Drei = Prozess, letzter Anker 21.03.1938, M.V.-Spur, Renier schweigt. BRAVO: Arend festgenommen, HERON fotografiert, Kowalski-Lead Warschau. Merge vollständig.",
    "summary_last_rift": "Letzte Rift-Op ohne Px-Verbrauch beendet.",
    "summary_active_arcs": "KAIROS-Gegenoffensive; MERIDIAN-Funktion aufgedeckt; Route Drei = Prozess, 21.03.1938; M.V.-Spur; Brenner im ITI; Zylinder ungeöffnet; HERON-Analyse läuft; Kowalski-Spur Warschau; WESTSEITE-Verhör aktiv; Arend im ITI; KAIROS-Beobachter Wien 1937 wird Arends Verschwinden melden; Renier kennt M.V."
  },
  "continuity": {
    "last_seen": {
      "mode": "hq",
      "episode": 12,
      "mission": 12,
      "location": "HQ"
    },
    "split": {
      "family_id": "SPLIT-EP12-MS12-WIEN",
      "thread_id": "MERGED",
      "expected_threads": ["ALPHA", "BRAVO"],
      "resolved_threads": ["ALPHA", "BRAVO"],
      "convergence_ready": true
    },
    "roster_echoes": [
      {
        "char_id": "AGENT-A",
        "tone": "fokussiert",
        "text": "Astra/ECHO — Analytikerin, deckte M.V.-Spur auf, Psi aktiv. INT 10, SYS jetzt 6. Thread ALPHA."
      },
      {
        "char_id": "AGENT-B",
        "tone": "direkt",
        "text": "Blitz/STORM — CQB-Spezialist, neutralisierte Begleiter 1 + Franz, Brenner exfiltriert. STR 10, SYS jetzt 4. Thread ALPHA."
      },
      {
        "char_id": "AGENT-C",
        "tone": "präzise",
        "text": "Cipher/GHOST — Infiltration, trägt Zylinder (erster Anker), MRD-7-Spiegelung. SYS jetzt 11. Thread ALPHA."
      },
      {
        "char_id": "AGENT-D",
        "tone": "ruhig",
        "text": "Dusk/VEIL — Aufklärung, führte Arend-Kontakt im Café Landtmann. GES 8. Thread BRAVO."
      },
      {
        "char_id": "AGENT-E",
        "tone": "analytisch",
        "text": "Echo/RELAY — Support, sicherte HERON-Fotokopie, umging KAIROS-Beobachter. Feldroutine Meister. Thread BRAVO."
      }
    ],
    "shared_echoes": [
      {
        "tag": "meridian-funktion-ms11",
        "scope": "campaign",
        "text": "MERIDIAN ist eine Funktion/Amt, rollende Besetzung — letzte bekannte Inkarnation weiblich, ITI-intern, vor 3 Jahren."
      },
      {
        "tag": "route-drei-prozess-ms12",
        "scope": "campaign",
        "text": "Route Drei ist ein Prozess, kein Objekt/Mensch. 18 Monate Vorbereitung. Letzter Anker: 21. März 1938. Noch nicht gesetzt."
      },
      {
        "tag": "route-drei-nichtmensch-ms11",
        "scope": "campaign",
        "text": "Route Drei war laut LEITER nie ein Mensch — Natur durch MS12 als Prozess präzisiert."
      },
      {
        "tag": "mv-initialen-ms12",
        "scope": "campaign",
        "text": "M.V. — Initialen im Notizbuch, eingeritzt. Tot seit 3 Jahren. Vermutlich frühere MERIDIAN-Inkarnation die gegen Route Drei arbeitete. Renier kennt das Kürzel."
      },
      {
        "tag": "depot-anatolien-bronzezeit-ms11",
        "scope": "campaign",
        "text": "KAIROS-Depot: Frühe Bronzezeit, Anatolien — Koordinaten nur auf echtem Träger Route Drei."
      },
      {
        "tag": "zylinder-erster-anker-ms12",
        "scope": "campaign",
        "text": "Metallzylinder (bei GHOST): Koordinate des ersten Route-Drei-Ankers. Versiegelt. Wer ersten Anker versteht, versteht den Prozess."
      },
      {
        "tag": "kaffee-kalt-meridian-ms12",
        "scope": "campaign",
        "text": "ITI-interner MERIDIAN-Kontakt hat Gewohnheit: Kaffee kalt stehen lassen, dann in einem Zug trinken — laut Brenner."
      },
      {
        "tag": "frau-zuerich-iti-stiefel-ms12",
        "scope": "campaign",
        "text": "Frau in Zürich (ca. 50, graues Haar, Deutsch ohne Muttersprache, ITI-Stiefel) gab Brenner Notizbuch mit Auftrag. Identität unbekannt."
      },
      {
        "tag": "heron-protokoll-ms12",
        "scope": "campaign",
        "text": "HERON: Verschlüsselungsprotokoll, Grundstruktur fotografiert (12 Seiten). Arend-Original Piaristengasse 7 Wien 1937. Kompatibel mit MRD-7-Adressaten-Architektur."
      },
      {
        "tag": "kowalski-warschau-ms12",
        "scope": "campaign",
        "text": "Dr. Marta Kowalski, Universität Warschau — erhielt HERON-Grundstruktur per Brief vor 2 Jahren. Möglicherweise weiterentwickelt. Kontakt-Lead offen."
      },
      {
        "tag": "kairos-beobachter-wien1937-ms12",
        "scope": "campaign",
        "text": "KAIROS-Beobachter Wien Oktober 1937 — wartete auf Arend, Piaristengasse 7. Umgangen, wird Verschwinden melden. Reaktion ausstehend."
      },
      {
        "tag": "merge-alpha-bravo-ms12",
        "scope": "shared",
        "text": "Threads ALPHA und BRAVO konvergiert. Alle fünf Operatoren im HQ. Brenner + Arend + WESTSEITE + LEITER im Gewahrsam."
      }
    ],
    "convergence_tags": ["SPLIT-EP12-MS12-WIEN"],
    "npc_roster": [
      {
        "id": "NPC-LEITER-MS11",
        "name": "LEITER",
        "callsign": "LEITER",
        "role": "KAIROS-Bindungs-Agent",
        "scope": "campaign",
        "status": "ITI-Gewahrsam",
        "last_seen": "ITI-Nullzeit, MS11-Debrief"
      },
      {
        "id": "NPC-HAAS-MS11",
        "name": "Haas",
        "callsign": "HAAS",
        "role": "KAIROS-Kurier (unwissend)",
        "scope": "episode",
        "status": "ITI-Gewahrsam",
        "last_seen": "ITI-Nullzeit, MS11-Debrief"
      },
      {
        "id": "NPC-FRAU-MS11",
        "name": "Unbekannte Frau",
        "callsign": "WESTSEITE",
        "role": "KAIROS-Kontakt Wien, wusste von Bindungs-Op",
        "scope": "campaign",
        "status": "ITI-Gewahrsam, Verhör aktiv",
        "last_seen": "ITI-Nullzeit, MS11-Debrief"
      },
      {
        "id": "NPC-BRENNER-MS12",
        "name": "Brenner",
        "callsign": "BRENNER",
        "role": "KAIROS-Kurier, Träger Route-Drei-Sekundärmaterial",
        "scope": "campaign",
        "status": "ITI-Gewahrsam, Verhör ausstehend",
        "last_seen": "ITI-Nullzeit, MS12-Exfil"
      },
      {
        "id": "NPC-AREND-MS12",
        "name": "Dr. Felix Arend",
        "callsign": "AREND",
        "role": "Österreichischer Kryptograph, HERON-Schöpfer",
        "scope": "campaign",
        "status": "ITI-Gewahrsam, kooperativ — Verhör MERIDIAN/HERON ausstehend",
        "last_seen": "ITI-Nullzeit, MS12-Debrief"
      },
      {
        "id": "NPC-PELZ-MS12",
        "name": "Dr. Otto Pelz",
        "callsign": "PELZ",
        "role": "Mathematikprofessor Wien, Arends Schachpartner",
        "scope": "episode",
        "status": "Wien 1937, nicht extrahiert — kein ITI-Kontakt",
        "last_seen": "Café Landtmann Wien, MS12"
      }
    ],
    "active_npc_ids": [
      "NPC-LEITER-MS11",
      "NPC-FRAU-MS11",
      "NPC-BRENNER-MS12",
      "NPC-AREND-MS12"
    ]
  },
  "arc": {
    "factions": {
      "KAIROS": "Gegenoffensive aktiv — Route-Drei-Prozess läuft, letzter Anker 21. März 1938. Beobachter Wien 1937 umgangen, wird Arends Verschwinden melden.",
      "ITI": "Mögliche Infiltration durch MERIDIAN-Funktion — Renier informiert, kennt M.V. und schweigt."
    },
    "questions": [
      "Wer ist aktuell MERIDIAN — welche ITI-Person besetzt die Funktion?",
      "Was ist Route Drei genau — was passiert wenn der letzte Anker gesetzt wird?",
      "Wer ist die Frau aus Zürich mit ITI-Stiefeln?",
      "Was zeigt der Metallzylinder — wo liegt der erste Anker?",
      "Was weiß Renier über M.V. — und warum schweigt er?",
      "Hat Dr. Marta Kowalski HERON weiterentwickelt — und wo ist sie jetzt?",
      "Was wird KAIROS tun, wenn der Beobachter Arends Verschwinden meldet?"
    ],
    "hooks": [
      "MRD-7-Analyse läuft — 1/2 Missionen bis Ergebnis (MERIDIAN-Adressaten-Struktur)",
      "HERON-Fotokopie-Analyse läuft — 0/2 Missionen bis Ergebnis",
      "Brenner-Verhör ausstehend — ITI-Nullzeit",
      "Arend-Verhör ausstehend — MERIDIAN-Verbindung, HERON-Vollprotokoll",
      "WESTSEITE-Verhör aktiv — Akzent polnisch, wusste von Bindungs-Op",
      "Metallzylinder öffnen — Lab, GHOST dabei",
      "21. März 1938 — letzter Anker noch nicht gesetzt",
      "Renier kennt M.V. — Konfrontation ausstehend",
      "Filmpatrone — Fotograf Norddach unbekannt, Identität klären",
      "Dr. Marta Kowalski, Warschau 1937 — HERON-Grundstruktur erhalten, möglicherweise weiterentwickelt",
      "KAIROS-Beobachter Wien 1937 — wird Arends Verschwinden melden, Reaktion unbekannt",
      "LEITER — weiteres Verhör, kennt Epoche des Depots",
      "Rift-Seed Norwegen 1947 — nach Episodenabschluss spielbar"
    ]
  },
  "ui": {
    "gm_style": "verbose",
    "suggest_mode": false,
    "action_mode": "uncut",
    "intro_seen": true,
    "dice": { "debug_rolls": true },
    "contrast": "standard",
    "badge_density": "standard",
    "output_pace": "normal",
    "voice_profile": "gm_second_person"
  },
  "arena": {
    "active": false,
    "phase": "idle",
    "queue_state": "idle",
    "mode": "none",
    "tier": 0,
    "previous_mode": null,
    "resume_token": null,
    "contract_id": null,
    "streak": 0,
    "pending_rewards": { "cu": 0, "xp": 0, "arena_rep": 0, "multiplier": 1, "risk": "low" },
    "banked_rewards": { "cu": 0, "xp": 0, "arena_rep": 0 },
    "rewarded_runs_this_contract": 0,
    "first_wins": {},
    "defeated_types": [],
    "last_reward_episode": null,
    "wins_player": 0,
    "wins_opponent": 0,
    "match_policy": "standard"
  }
}
```

> ❌ **[MERGE] SCHEMA:** merge-result-5er @ continuity/shared_echoes: [{'tag': 'meridian-funktion-ms11', 'scope': 'campaign', 'text': 'MERIDIAN ist eine Funktion/Amt, rollende Besetzung — letzte bekannte Inkarnation weiblich, ITI-

> ❌ **[MERGE] ECHO-CAP:** merge-result-5er: shared_echoes 12>6

> ⚠️ **[MERGE-ASSERT] IMPORTED:** merge: imported_saves als String-Array (1 Einträge) statt kanonischer Objektform [{save_id,branch_id,status}] (Modul 12)

> ❌ **[MERGE-ASSERT] ECHO-CAP:** merge: shared_echoes 12>6

> ❌ **[MERGE-ASSERT] WEALTH-EXPLOIT:** merge: Gesamtvermögen STEIGT über Split/Merge 90050→95440 (+5390, +6.0%) — Geld-Druck-Exploit über Split/Merge-Zyklus

> ℹ️ **[ROUTING] ROUTING-RIFT:** Kein Rift-Seed in shared_echoes (korrekt)

> ⚠️ **[ROUTING] ROUTING-FADEN:** 10 Ermittlungs-Hinweis(e) noch als campaign-shared_echo (sollten in research/summary): ['meridian-funktion-ms11', 'route-drei-prozess-ms12', 'route-drei-nichtmensch-ms11', 'mv-initialen-ms12', 'depot-anatolien-bronzezeit-ms11', 'zylinder-erster-anker-ms12', 'kaffee-kalt-meridian-ms12', 'frau-zuerich-iti-stiefel-ms12', 'kowalski-warschau-ms12', 'kairos-beobachter-wien1937-ms12']

> ℹ️ **[ROUTING] Faden-Ablage:** research.projects=2, summary_active_arcs=gefüllt, shared_echoes=12 (campaign-nonfolgespur=11), rift_seeds=1


---

## Verdict: FAIL

- Turns: 2
- Kosten (echt, OWUI usage.cost): $0.3653
- Peak Prompt-Tokens: 77306 (30.2% von 256k)
- Ø Cache-Hit: 78%
- Harte Fehler: 4 | Soft: 2

**FAILS:**
- ❌ [SCHEMA] merge-result-5er @ continuity/shared_echoes: [{'tag': 'meridian-funktion-ms11', 'scope': 'campaign', 'text': 'MERIDIAN ist eine Funktion/Amt, rollende Besetzung — letzte bekannte Inkarnation weiblich, ITI-
- ❌ [ECHO-CAP] merge-result-5er: shared_echoes 12>6
- ❌ [ECHO-CAP] merge: shared_echoes 12>6
- ❌ [WEALTH-EXPLOIT] merge: Gesamtvermögen STEIGT über Split/Merge 90050→95440 (+5390, +6.0%) — Geld-Druck-Exploit über Split/Merge-Zyklus

**SOFT:**
- ⚠️ [IMPORTED] merge: imported_saves als String-Array (1 Einträge) statt kanonischer Objektform [{save_id,branch_id,status}] (Modul 12)
- ⚠️ [ROUTING-FADEN] 10 Ermittlungs-Hinweis(e) noch als campaign-shared_echo (sollten in research/summary): ['meridian-funktion-ms11', 'route-drei-prozess-ms12', 'route-drei-nichtmensch-ms11', 'mv-initialen-ms12', 'depot-anatolien-bronzezeit-ms11', 'zylinder-erster-anker-ms12', 'kaffee-kalt-meridian-ms12', 'frau-zuerich-iti-stiefel-ms12', 'kowalski-warschau-ms12', 'kairos-beobachter-wien1937-ms12']

