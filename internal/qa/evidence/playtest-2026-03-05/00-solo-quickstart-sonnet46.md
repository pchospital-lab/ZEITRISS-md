# Playtest: Solo Quickstart — Save v7 Schema-Test

**Datum:** 2026-03-05
**Modell:** zeitriss-v426-uncut (Sonnet 4.6)
**Szenario:** `Spiel starten (solo schnell)` → Rolle 2 (Ghost) → Mira Voss / Phantom → `!save`

---

## Ergebnis

### Charakter-Erstellung ✅
- Rolle: Ghost (Infiltration)
- Attribute: STR 2, GES 6, INT 4, CHA 3, TEMP 2, SYS 1 = **18 ✓**
- Attribut-Cap 6 eingehalten ✅
- Rank: Rekrut ✅
- Wallet: 100 CU ✅

### HUD-Darstellung ✅
- Ruf und Lizenz-Tier im Charakterbogen: `RUF ITI +0 · Ordo Mnemonika +0 · LIZENZ Tier 0`
- Summencheck explizit angezeigt
- Equipment mit Tier-Angabe

### Save-Output ✅

```json
{
  "v": 7, "zr": "4.2.6",
  "campaign": {
    "episode": 1, "mission": 1, "px": 0, "mode": "mixed",
    "rift_seeds": []
  },
  "characters": [{
    "id": "CHR-0001", "name": "Mira Voss", "callsign": "Phantom", "rank": "Rekrut",
    "lvl": 1, "xp": 0,
    "origin": { "epoch": "Nullzeit", "hominin": "Homo sapiens sapiens", "role": "Infiltratorin" },
    "attr": { "STR": 2, "GES": 6, "INT": 4, "CHA": 3, "TEMP": 2, "SYS": 1 },
    "hp": 10, "hp_max": 10, "stress": 0,
    "has_psi": false,
    "sys_installed": 0,
    "talents": ["Schattenschritt", "Schlösser knacken"],
    "equipment": [
      {"name": "Silenced Compact", "type": "weapon", "tier": 1},
      {"name": "Tarnjacke", "type": "armor", "tier": 1},
      {"name": "Dietrichset", "type": "gadget", "tier": 1},
      {"name": "Comlink", "type": "gadget", "tier": 1},
      {"name": "Medpack x2", "type": "consumable", "tier": 1}
    ],
    "implants": [],
    "reputation": {
      "iti": 0, "faction": "Ordo Mnemonika",
      "factions": { "ordo_mnemonika": 0, "chrono_symmetriker": 0,
                    "kausalklingen": 0, "zerbrechliche_ewigkeit": 0 }
    },
    "wallet": 100
  }],
  "economy": { "hq_pool": 0 },
  "logs": {
    "trace": [], "market": [], "artifact_log": [], "notes": [],
    "flags": { "runtime_version": "4.2.6", "chronopolis_unlocked": false }
  },
  "arc": { "factions": {}, "questions": [], "hooks": [] },
  "ui": { "gm_style": "verbose", "suggest_mode": false,
    "contrast": "standard", "badge_density": "standard",
    "output_pace": "normal", "voice_profile": "gm_third_person" }
}
```

### Schema-Check

| Prüfpunkt | Ergebnis |
|-----------|----------|
| `v: 7` | ✅ |
| `characters[]` (kein `character{}`) | ✅ |
| `attr` (kein `attributes`) | ✅ |
| `reputation` mit Fraktionen | ✅ |
| `has_psi: false` (kein leerer Psi-Block) | ✅ |
| Equipment als `[{name, type, tier}]` | ✅ |
| Keine Laufzeit-Daten (exfil, cooldowns) | ✅ |
| Logs konsolidiert (4 Arrays) | ✅ |
| Keine Arena (nicht genutzt) | ✅ |

**Fazit:** v7-Schema wird beim Solo-Quickstart korrekt und vollständig ausgegeben. Alle Felder konform, keine Legacy-v6-Reste.
