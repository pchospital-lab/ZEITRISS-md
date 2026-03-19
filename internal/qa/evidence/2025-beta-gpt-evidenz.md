---
title: "QA-Evidenz Beta-KI 2025"
version: 0.2.0
tags: [meta, qa]
---

# QA-Evidenz – Beta-KI Läufe 2025

**Evidenzstand:** Alle Auszüge spiegeln den freigegebenen Build **4.2.2**
(`zr_version`/`runtime_version`).

Dieses Protokoll listet die für die Beta-KI-Regressionsläufe geforderten
Nachweise. Seit 2025-11-05 liefern die Maintainer den Beta-KI-Testprompt
als JSON-Block, spiegeln ihn in einer zweiten ZEITRISS-Instanz und übergeben
den abgeglichenen Datensatz an Codex. Die HUD-/Save-/Dispatcher-Auszüge werden
hier abgelegt und in QA-Log sowie Audit verlinkt.

## 2025-07-05 – Save/HUD/Arena-Deltas

Referenzen: QA-Log [2025-07-05](../logs/2025-beta-qa-log.md#2025-07-05--tester-beta-gpt--schema-hud-und-arena-deltas),
QA-Fahrplan §„Maßnahmenpaket Beta-KI 2025-07“. Die technischen Fixes sind
abgeschlossen; die Nachweise stammen aus dem JSON-Hand-off 2025-11-05.

- [x] **Migration 5→6 (DeepSave):** Vorher-/Nachher-JSON für einen
      Gruppensave, der den Wechsel von `save_version: 5` auf `save_version: 6`
      dokumentiert.

```json
{
  "before": {
    "save_version": 5,
    "zr_version": "4.2.2",
    "ui": { "intro_seen": 0 },
    "campaign": {
      "mode": "preserve",
      "exfil": { "active": true, "sweeps": 1, "anchor": "Atlas-Korridor" }
    },
    "logs": {
      "flags": { "runtime_version": "4.2.2", "chronopolis_warn_seen": "false" }
    }
  },
  "after": {
    "save_version": 6,
    "zr_version": "4.2.2",
    "ui": {
      "intro_seen": false,
      "gm_style": "verbose",
      "suggest_mode": false,
      "contrast": "standard"
    },
    "campaign": {
      "exfil": {
        "active": true,
        "armed": false,
        "hot": false,
        "sweeps": 1,
        "stress": 0,
        "anchor": "Atlas-Korridor",
        "alt_anchor": null,
        "ttl": 0
      }
    },
    "logs": {
      "flags": {
        "runtime_version": "4.2.2",
        "chronopolis_warn_seen": true,
        "foreshadow_gate_progress": 0,
        "foreshadow_gate_snapshot": 0
      }
    }
  }
}
```

- [x] **Foreshadow/HUD-Reset:** Screenshot oder HUD-Log mit `Foreshadow 2/2`
      vor Missionsstart sowie `FS 0/2` nach `StartMission()`; zusätzlich die
      QA-Journal-Notiz zum Reset.

```text
Overlay vor Start: EP 2 · MS 5 · SC 0/12 · MODE verbose · Objective: Gate-Test · FS 2/2 · GATE 2/2 · Px 1 · SYS 0 · Lvl -
Boss-Status vor Reset: Gate 2/2 · Mission FS 2/2
HUD-Log vor Start: [Foreshadow] Foreshadow: Signal im Torbogen | [Foreshadow] Foreshadow: Störfrequenz über dem Atrium
Overlay nach Start: EP 2 · MS 5 · SC 0/12 · MODE verbose · Objective: Gate-Test · ANCR ? · RW 08:00 · FS 0/2 · GATE 2/2 · Px 1 · SYS 0 · Lvl - · FR:ruhig
Boss-Status nach Reset: Gate 2/2 · Mission FS 0/2
```

- [x] **Arena- & City-Smoke:** Dispatcher-Transkript mit `Speichern blockiert – Arena aktiv`
      sowie City-Minimaltest (`!chrono stock`, Warn-Banner). Ein kurzer Debrief-Ausschnitt
      genügt.

```text
Arena SaveGuard: SaveGuard: Arena aktiv – HQ-Save gesperrt.
Chronopolis · Tagesangebot 2025-10-18
— Era-Skins —
🔒 Era-Skin: Krakatoa 1883 Survivor · 200 CU (Rank Operator I)
Warn-Antwort: Chronopolis-Warnung quittiert.
HUD-Toast: [CITY] Chronopolis-Warnung quittiert – Stadtbriefing aktiv.
```

## 2025-07-18 – Save/HUD/Compliance Regression

Referenzen: QA-Log [2025-07-18](../logs/2025-beta-qa-log.md#2025-07-18--tester-beta-gpt--savehudcompliance-regression),
QA-Fahrplan §„Maßnahmenpaket Beta-KI 2025-07-18“.

- [x] **Exfil- & Wallet-Autoinit:** Save-Ausschnitt, der den Rücksprung von
      `campaign.exfil.active` sowie die Wallet-Initialisierung vor dem Debrief
      zeigt.

```json
{
  "walletSplitLines": [
    "Wallet-Split (2×): Alpha +100 CU | Beta +200 CU",
    "HQ-Pool: 0 CU verfügbar."
  ],
  "saveExcerpt": {
    "campaign_exfil": {
      "active": false,
      "armed": false,
      "hot": false,
      "sweeps": 0,
      "stress": 0,
      "anchor": null,
      "alt_anchor": null,
      "ttl": 8
    },
    "economy_wallets": {
      "operator": { "balance": 0, "name": "Operator" },
      "alpha": { "balance": 100, "name": "Alpha" },
      "beta": { "balance": 200, "name": "Beta" }
    }
  }
}
```

- [x] **SF-OFF Persistenz + Arena Psi-Log:** HUD-Log mit `SF-OFF` Badge und
      zugehöriger `logs.psi[]`-Zeile (`phase_strike_tax`).

```text
SF-Kommando: SF-OFF – introspektive Sequenzen gesperrt.
HUD-Eintrag: [SF-OFF] Self-Reflection deaktiviert – Fokus bleibt extern.
Phase-Strike-Kosten: 3
Psi-Log-Eintrag: ability=phase_strike · base_cost=2 · tax=1 · total_cost=3 · mode=preserve · arena_active=true
```

- [x] **Dispatcher-Hinweise & Semver-Text:** Ausschnitt aus dem Start-Dispatcher,
      der `!radio clear`/`!alias clear` nennt und den vereinheitlichten
      Semver-Warntext enthält.

```text
Startbefehle:
- Vor jedem Einsatz: !radio clear und !alias clear ausführen, damit Funk- und Alias-Logs frisch sind.
- Spiel starten (solo [preserve|trigger]) [klassisch|schnell]
- Spiel starten (npc-team [0–4] [preserve|trigger]) [klassisch|schnell]
- Spiel starten (gruppe [preserve|trigger]) [klassisch|schnell]
- Spiel laden
Klammern sind Pflicht. Rollen-Kurzformen: infil/tech/face/cqb/psi.
Speichern nur im HQ. Px 5 ⇒ ClusterCreate() (Rift-Seeds nach Episodenende).

Semver-Warnung: Kodex-Archiv: Datensatz v4.1 nicht kompatibel mit v4.2. Bitte HQ-Migration veranlassen.
```

## 2025-10-15 – Acceptance-/HUD-/Accessibility-Deltas

Referenzen: QA-Log [2025-10-15](../logs/2025-beta-qa-log.md#2025-10-15--tester-beta-gpt--acceptancehudsave-drift) sowie
QA-Fahrplan §„Maßnahmenpaket Beta-KI 2025-10-15“.

- [x] **Acceptance-Smoke 15 Schritte:** Dokumentierter Lauf (Checkliste oder
      HUD-Protokoll), der die Schritte 1–15 durchläuft und die neuen Punkte für
      Accessibility, City und Arena enthält.

```text
1. `spiel starten (solo klassisch)` → Intro & HQ-Overlay (vgl. `node tools/test_start.js`).
2. `spiel starten (solo schnell)` → Kurzbriefing bestätigt denselben Einstieg.
3. `spiel starten (npc-team 3 schnell)` → Autogen-NSCs (3) & Wallet-Init (`[HQ] Wallets initialisiert (1×)`).
4. `spiel starten (npc-team 5)` → Fehlermeldung „Teamgröße 0–4 …“ (siehe Testausgabe).
5. `spiel starten (gruppe schnell)` → Gruppenlauf (`gruppe-trigger-schnell`).
6. `spiel starten (gruppe 3)` → Fehlermeldung „Bei *gruppe* keine Zahl …“.
7. `!load`-Pfad in `node tools/test_save.js` → Kodex-Recap & HQ-Overlay.
8. `save_deep()` während Mission → Blocker „SaveGuard: Arena aktiv – HQ-Save gesperrt.“
9. Gear-Alias-Spiegel laut README/Speicherfortsetzung: „Multi-Tool-Armband“ ⇒ „Multi-Tool-Handschuh“.
10. Px 5 Trigger (`node tools/test_save.js`) → Hinweis „Seeds nach Episodenende“.
11. `!helper boss`/Foreshadow → Gate 2/2 siehe HUD-Auszug oben.
12. Mission 5 Start (`StartMission()`) → Boss-DR Toast + GATE 2/2 + SF-Autoreset.
13. Psi-Heat Reset (`node tools/test_hud.js`) → TK-/Psi-Buffer wieder aktiv.
14. `!accessibility …` → Kontrast hoch, Badges kompakt, Pace langsam (`!accessibility status`).
15. Save laden + `!accessibility status` → Einstellungen persistieren (siehe Accessibility-Status oben).
```

- [x] **Save-Migration Legacy-Gruppensave:** Beispiel für einen v5-Gruppensave,
      der durch den Loader auf Schema v6 gehoben wird (inkl. `allow_entry_choice`
      Flag und Arena-Phase).

```json
{
  "save_version": 6,
  "zr_version": "4.2.2",
  "party": {
    "characters": [
      { "id": "alpha", "callsign": "Alpha", "stress": 0, "psi_heat": 0 },
      { "id": "beta", "callsign": "Beta", "stress": 0, "psi_heat": 0 }
    ]
  },
  "team": {
    "members": [
      { "id": "alpha", "callsign": "Alpha", "stress": 0, "psi_heat": 0 },
      { "id": "beta", "callsign": "Beta", "stress": 0, "psi_heat": 0 }
    ]
  },
  "arena": {
    "active": true,
    "phase": "active",
    "mode": "squad",
    "previous_mode": "preserve",
    "team_size": 1,
    "phase_strike_tax": 0
  },
  "flags": {
    "runtime_version": "4.2.2",
    "compliance_shown_today": false,
    "foreshadow_gate_progress": 0
  }
}
```

- [x] **HUD-Dumps & Accessibility-Dialog:** Screenshot oder HUD-Log mit
      `SF-OFF` Auto-Reset, Gate-Badge Persistenz (M5/M10) sowie dem neuen
      `!accessibility`-Dialog.

```text
Overlay Mission 5: EP 1 · MS 5 · SC 0/12 · MODE verbose · Objective: Boss-Test · GATE 2/2 · SF-OFF
HUD-Log: [BOSS] Mini-Boss in Szene 10 – Overflow halbiert. | [BOSS] Boss-DR aktiviert – −X Schaden pro Treffer
Accessibility Status: Kontrast: hoch · HUD-Badges: kompakt · Output-Takt: langsam
```

- [x] **Dispatcher-Trigger & Cinematic-Header:** Transkript, das die Option
      `trigger` beim Start-Dispatcher und den erzwingenden Cinematic-Header nach
      dem Briefing festhält.

```text
Dispatcher: Compliance-Hinweis + HQ-Kurzintro … → Antwort `solo-trigger-klassisch`
Overlay vor Mission: EP 0 · MS 0 · SC 0/12 · MODE verbose · Objective: ? · FS 0/4 · Px 0 · SYS 1 · Lvl -
`launch_mission()` → `mission-launched`
Overlay nach Briefing: EP 0 · MS 0 · SC 0/12 · MODE verbose · Objective: ? · ANCR ? · RW 08:00 · FS 0/4 · Px 0 · SYS 1 · Lvl - · FR:beobachter
```

> **Hinweis:** Sobald ein Kasten abgehakt ist, bitte die betreffenden
> QA-Log-Abschnitte aktualisieren und im Audit den neuen Evidenzstand
> vermerken.

## 2025-10-28 – SaveGuard/HUD/Ökonomie-Deltas

Referenzen: QA-Log [2025-10-28](../logs/2025-beta-qa-log.md#2025-10-28--tester-beta-gpt--savehudarena-divergenzen),
QA-Fahrplan §„Maßnahmenpaket Beta-KI 2025-10-28“.

- [x] **HQ-DeepSave Mindestfelder & Wallet-Split:** Minimal-HQ-Save mit
      vollständigen Pflichtblöcken (`economy.wallets`, `logs.foreshadow`,
      `ui.badges`) inklusive Wallet-Split vor/nach Paradoxon-Reset.

```json
{
  "economy": {
    "cu": 0,
    "wallets": {
      "ghost": { "balance": 100, "name": "Ghost" },
      "nova": { "balance": 100, "name": "Nova" }
    }
  },
  "logs": {
    "foreshadow": [
      {
        "token": "manual:gate_echo",
        "tag": "Foreshadow",
        "message": "Gate Echo",
        "scene": 2,
        "first_seen": null,
        "last_seen": null
      }
    ],
    "flags": { "foreshadow_gate_expected": true }
  },
  "ui": {
    "gm_style": "verbose",
    "intro_seen": true,
    "badge_density": "compact",
    "contrast": "high",
    "suggest_mode": false,
    "output_pace": "normal"
  }
}
```

- [x] **Arena-Active Guard:** HUD-/Dispatcher-Trace, der den Save-Blocker bei
      aktiver Arena dokumentiert (`Arena aktiv – HQ-Save gesperrt`).

```text
Arena SaveGuard: SaveGuard: Arena aktiv – HQ-Save gesperrt.
```

- [x] **Foreshadow-/Gate-Badges & Accessibility-Preset:** HUD-Screenshot oder
      Logauszug mit getrennten `Foreshadow n/2`- und `Gate n/2`-Badges sowie dem
      zusätzlichen Accessibility-Preset im Dispatcher.

```text
Overlay Mission 5: EP 1 · MS 5 · SC 0/12 · MODE verbose · Objective: Boss-Test · GATE 2/2 · SF-OFF
Accessibility-Status: Kontrast: hoch · HUD-Badges: kompakt · Output-Takt: langsam
```

- [x] **Ökonomie-Formeln & Boss-DR-Toast:** Debrief-/HUD-Protokoll, das die
      neuen Ökonomie-Formeln (Mission-/CU-Split) sowie den automatischen
      Boss-DR-Toast bestätigt.

```text
HUD: [BOSS] Mini-Boss in Szene 10 – Overflow halbiert. | [BOSS] Boss-DR aktiviert – −X Schaden pro Treffer
Debrief:
Belohnungen · Chrono Units +480 CU · Resonanz Px 1/5 (5/5 bis Px+1) · Rang Recruit
Hazard-Pay: 60 CU priorisiert (HQ-Pool).
Wallet-Split (1×): Ghost +480 CU · HQ-Pool: 180 CU verfügbar.
```
