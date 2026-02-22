# 02-debrief-save-sonnet
- **Model:** zeitriss-v426-uncut-sonnet
- **Cost:** $0.045735
- **Tokens:** in:5300 out:1989

## Output

`EP 1 · MS 5 · SC 12/12 · PHASE Debrief · MODE CORE · COMMS OK · Lvl 4 ▓▓▓▓▓▓▓▓░░ 680/800 XP · Px 4/5 · Stress 3/10 · Obj ABGESCHLOSSEN · Exfil —`

---

## ◼ SCORE-SCREEN — MISSION 5 ◼
### *„Archivschatten"* · Core-Op · Episode 1

---

```
BEWERTUNG
─────────────────────────────────────────
Primärziel      Archivmodul gesichert     ✓
Sekundärziel    Zeitlinie stabil          ✓
Bonus           Keine Zivilopfer          ✓
Malus           —                         —
─────────────────────────────────────────
GESAMTWERTUNG                        ★★★★☆
Klasse: GHOST (Elite-Schwelle: 4 Sterne)
```

---

```
KAMPF-PROTOKOLL
─────────────────────────────────────────
Feinde neutralisiert        2 / 2
Feinde entkommen            0
Kollateralschäden           0
Lautstärke-Peak             MEDIUM
Heat beim Abzug             NIEDRIG
─────────────────────────────────────────
```

---

```
RESSOURCEN-RECAP
─────────────────────────────────────────
Stress eingegangen          +3
Stress abgebaut             0
Px-Änderung                 +1  →  4/5
Ausrüstung verbraucht       —
─────────────────────────────────────────
⚠  Px 4/5 — ein weiterer Eingriff
   löst ClusterCreate aus.
─────────────────────────────────────────
```

---

```
LOOT-RECAP
─────────────────────────────────────────
Archivmodul MK-II           [Datenloot]
  → ITI-Archiv übergeben    +200 CU Bonus
Sidearm (neutralisierter
  Gegner, Standardmodell)   [Waffe, heiß]
  → Einbehalten oder
    verkaufen (80 CU)
─────────────────────────────────────────
```

---

```
CU-ABRECHNUNG
─────────────────────────────────────────
Bestand vorher              1.800 CU
Mission-Sold                  400 CU
Ziel-Bonus (Archiv)           200 CU
Stern-Bonus (4★)              150 CU
─────────────────────────────────────────
GESAMT                      2.550 CU
─────────────────────────────────────────
```

---

```
XP & LEVEL
─────────────────────────────────────────
XP vorher                   680 / 800
Mission-XP                  +80
Bonus-XP (Zivilos)          +20
Bonus-XP (Zeitlinie)        +25
─────────────────────────────────────────
XP aktuell                  805 / 800
─────────────────────────────────────────
⬆  LEVEL UP  →  Level 5
   +1 Attributpunkt frei
   +1 Talentslot frei
   Neuer Schwellenwert: 1.200 XP
─────────────────────────────────────────
```

---

```
RUF-UPDATE
─────────────────────────────────────────
ITI-Vertrauen               +1   →  7/10
Fraktion KRON               —
Fraktion SABLE              —
─────────────────────────────────────────
Bekanntheitsgrad (Heat)     NIEDRIG
─────────────────────────────────────────
```

---

`Kodex: Mission 5 archiviert. Px 4/5 — kritische Schwelle. Level-Up ausstehend: 1 Attributpunkt, 1 Talentslot. CU-Bestand 2.550.`

---

## SPEICHERSTAND

```json
{
  "zr_version": "4.2.6",
  "save_version": 6,
  "location": "HQ",
  "phase": "core",
  "character": {
    "id": "CHR-NOVA",
    "name": "Nova",
    "level": 5,
    "attributes": {
      "STR": 3,
      "GES": 4,
      "INT": 4,
      "CHA": 2,
      "TEMP": 3,
      "SYS_max": 4,
      "SYS_installed": 2,
      "SYS_runtime": 2,
      "SYS_used": 0
    },
    "talents": [
      "Schleichen I",
      "Hacking I",
      "Nahkampf I"
    ],
    "bioware": [],
    "equipment": {
      "primary": "Standardpistole (ITI-Ausgabe)",
      "secondary": "Sidearm (erbeutet, heiß)",
      "armor": ["Leichte Komposit-Weste"],
      "gadgets": ["Handscanner", "Jammer Mk.I"]
    },
    "stress": 3,
    "psi_heat": 0,
    "cooldowns": {},
    "level_up_pending": {
      "attribute_points": 1,
      "talent_slots": 1
    }
  },
  "campaign": {
    "episode": 1,
    "mission_in_episode": 5,
    "scene": 12,
    "px": 4,
    "mode": "mixed",
    "rift_seeds": []
  },
  "party": { "characters": [] },
  "economy": {
    "cu": 2550,
    "wallets": {}
  },
  "logs": {
    "hud": [],
    "foreshadow": [],
    "artifact_log": ["Archivmodul MK-II → ITI übergeben"],
    "market": ["Sidearm (heiß, 80 CU Verkaufswert)"],
    "psi": [],
    "arena_psi": [],
    "flags": {
      "ms5_complete": true,
      "archivmodul_secured": true,
      "timeline_stable": true,
      "no_civilian_casualties": true
    }
  },
  "arc_dashboard": {
    "offene_seeds": [],
    "fraktionen": {
      "ITI": { "vertrauen": 7 },
      "KRON": { "vertrauen": 0 },
      "SABLE": { "vertrauen": 0 }
    }
  },
  "ui": {
    "gm_style": "verbose",
    "suggest_mode": false,
    "action_mode": "uncut"
  },
  "arena": { "active": false }
}
```

---

**Speicherstand gesichert.** Kopiere den JSON-Block für deinen nächsten Start.

Bereit für **HQ-Runde** — Level-Up ausstehend. Willst du jetzt Attribut und Talent vergeben, bevor Mission 6 gebrieft wird?

**1** — Level-Up abschließen (Attribut + Talent wählen)
**2** — Ausrüstung verwalten / Sidearm verkaufen
**3** — Direkt zu Mission 6 Briefing

**Freie Aktion** — Was tust du?
