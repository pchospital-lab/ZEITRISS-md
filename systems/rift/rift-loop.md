---
title: "ZEITRISS 4.0 – Modul 18: Core & Rift Loop"
version: 4.0
tags: [systems]
---

# ZEITRISS 4.0 – Modul 18: Core & Rift Loop

Dieses Modul fasst das Paradox-Subsystem, die Cluster-Mechanik und den Wechsel
zwischen Core- und Rift-Missionen zusammen. Es basiert auf dem Developer
Handoff "Revision Core & Rift Loop".

## 1. Paradox-Subsystem (5 Stufen)

Die Tabelle beschreibt die Effekte während einer Mission und im ITI-HQ.

| Stufe | In-Mission-Effekt | HQ-Effekt |
|-------|------------------|-----------|
|0–1 | Stabil | – |
|2 | HUD-Flackern | – |
|3 | Audio-Echo, leichte Desynchronisierung | – |
|4 | 1s Zeitstillstand, Warn-Ping | "Riss-Vorstufe"-Flag |
|**5** | *kein* Zusatz (Flow bleibt sauber) | **ClusterCreate()** → 1–2 Rift-Seeds; Paradox wird auf 0 gesetzt |

Der Paradoxon-Index wird über Missionen hinweg verfolgt. Bei Erreichen von
Stufe 5 wird automatisch die Cluster-Erzeugung ausgelöst.

## 2. Cluster-Erzeugung (Backend-Macro)

```pseudocode
if paradox_level == 5:
    num = roll(1,2)
    cluster = []
    for i in range(num):
        cluster.append(roll_from("RiftSeedTable"))
    save_to_saveblock(cluster)  # attach to JSON save
    paradox_level = 0
```

*Severity* startet bei 1 und steigt pro nicht bearbeitetem Arc um +1 (max 3).
Die erzeugte Cluster-JSON wird dem Spielstand gemäß dem Modul-12-Schema
hinzugefügt.

## 3. Mission-Schemas

| Schiene | Generator | Artefakte? | Stil | HUD-Header |
|---------|-----------|------------|------|-----------|
|**Core-Ops**|Rand-Epochen & Core-Ziele|**NEIN**|Realistischer Spionage-Thriller|`[CORE MISSION • …]` (Blau-Grau)|
|**Rift-Ops**|RiftSeeds d10|**JA**|Blockbuster-Anomalie, rational erklärt|`[RIFT RESPONSE • …]` (Orange-Rot)|

Der Core-Generator darf kein Artefakt-Flag setzen. Rift-Seeds müssen ein
Artefakt- oder Anomalie-Flag enthalten.

## 4. HUD- und UI-Tokens

```
[CORE MISSION • CODE]      # default, blue-grey palette
[RIFT RESPONSE • CL-ID]    # anomaly, orange-red palette
```

In den Codex-Zeilen wird bei Core-Missionen "ChronTech-Operation …" und bei
Rift-Missionen "Temporale Instabilität erkannt …" ausgegeben.

## 5. Contra-Fraktion Ruleset

* **Core-Ops:** Audit-/Sabotage-Fokus, keine Psi-Elemente.
* **Rift-Ops:** Tech-Analyse (Contain & Copy).
  * `scan_artifact()` gibt +CU/+Blueprint und erhöht die Severity um +1.
* Briefings müssen einen Contra-Zielblock enthalten: "*Vermeide Psi-Kontakt.
  Priorität: Datensicherung.*"

## 6. SL-(GPT) Workflow

1. Generate Core-Mission (Artefakt = False).
2. Track Paradox; bei Stufe 5 wird **ClusterCreate()** ausgeführt.
3. Zwischen den Arcs oder auf Spielerwunsch **ClusterDashboard** anzeigen:
   ```json
   "OpenRifts": [
     {"ID":"R-71","Seed":"Emerald Kraken","Severity":1,"Deadline":-10}
   ]
   ```
4. Spieler können `launch_rift(id)` wählen → Rift-Seed laden, 1-Session
   Mission. Bei Erfolg wird der Eintrag entfernt, sonst steigt die Severity.
5. Rückkehr zum Core-Generator.

## 7. Deliverables

* **Neue Tabellen**
  * `CoreObjectiveTable.json`
  * `RiftSeedTable.json`
* **Macros / API**
  * `ClusterCreate()`
  * `ClusterDashboard()`
  * `LaunchRift(id)`
  * `ScanArtifact()` (Contra special)
* **HUD Theme Switcher** (Blue-Grey ⇆ Orange-Red)
* **Save-Block Extension** (open rifts array)

Weitere Details und Beispielhooks finden sich in `RiftSeedTable.json`.
