---
title: "Testprompt-Lauf 2026-02-12 Run 4 – Post-Critical-Fixes"
model: "anthropic/claude-sonnet-4"
version: 4.2.6
tags: [qa, testrun, automated, post-critical-fixes]
---

ISSUE #001
- Beobachtung: Dispatcher-Kommandos werden korrekt verarbeitet, aber die Klammerpflicht-Fehlermeldungen sind zu technisch formuliert
- Diagnose: Spieler:innen erwarten eine intuitive Ansprache, nicht Parser-Syntax-Hinweise
- Evidenz: `Spiel starten solo` → "Startsyntax: Spiel starten (solo|npc-team [0–4]|gruppe [klassisch|schnell]). Klammern sind Pflicht."

Lösungsvorschlag
- Ansatz: Fehlermeldungen in natürlicher Sprache umformulieren: "Bitte verwende: 'Spiel starten (solo klassisch)' oder 'Spiel starten (solo schnell)'"
- Risiken: Bestehende QA-Golden-Files müssen angepasst werden

To-do
- Codex: dispatcher_strings.json überarbeiten, nutzerfreundlichere Fehlertexte implementieren
- QA: Golden-File-Updates und Regression-Tests

Nächste Schritte
- Maintainer:innen: Neue Dispatcher-Strings in Runtime-Module integrieren
- Notizen: Backwards-Kompatibilität für bestehende QA-Fixtures beachten

ISSUE #002
- Beobachtung: HUD-Budget-Overflow führt zu inkonsistenter Toast-Unterdrückung in verschiedenen Spielmodi
- Diagnose: QA-Mode erkennt Low-Priority-Toasts nicht zuverlässig, `toast_suppressed`-Traces fehlen teilweise
- Evidenz: Massenkonflikt + Vehicle-Clash + Boss-Gate gleichzeitig → nur 2 von 4 Toasts erscheinen, aber kein suppression-Log

Lösungsvorschlag
- Ansatz: Einheitliche Toast-Prioritätsstufen definieren und suppression-Logging verbessern
- Risiken: Bestehende HUD-Events könnten anders priorisiert werden

To-do
- Codex: Toast-Prioritätssystem überarbeiten, suppression-Logging stabilisieren
- QA: HUD-Budget-Overflow systematisch in allen Modi testen

Nächste Schritte
- Maintainer:innen: HUD-Event-Allowlist erweitern und Prioritätslevel dokumentieren
- Notizen: Besonders kritisch für Arena- und PvP-Modi

ISSUE #003
- Beobachtung: Cross-Mode-Save-Import zeigt unklare Merge-Konflikte bei Economy-Wallets
- Diagnose: Solo-Save mit 120 CU in Koop geladen → Wallet-Split unklar, keine merge_conflicts.economy-Einträge
- Evidenz: Solo-Charakter Level 120 → Koop-Import → economy.wallets{} bleibt leer, aber CU verschwinden

Lösungsvorschlag
- Ansatz: Explizite Economy-Merge-Regeln implementieren, Wallet-Aufteilung dokumentieren
- Risiken: Bestehende Saves könnten unterschiedlich interpretiert werden

To-do
- Codex: Economy-Merge-Handler in load_deep() implementieren, Wallet-Split-Logik definieren
- QA: Cross-Mode-Economy-Tests mit verschiedenen Level-Stufen

Nächste Schritte
- Maintainer:innen: Economy-Schema erweitern, Merge-Conflict-Handling verbessern
- Notizen: Besonders wichtig für Koop→Solo-Transitions

ISSUE #004
- Beobachtung: Paradoxon-Index-Reset nach Seed-Generierung funktioniert, aber Timing-Hinweise sind verwirrend
- Diagnose: "Seeds spielbar nach Episodenende" erscheint bei Px 5, aber ClusterCreate() läuft sofort
- Evidenz: Mission 8 → Px erreicht 5 → Seeds generiert + Toast, aber Mission läuft normal weiter

Lösungsvorschlag
- Ansatz: Klarere Formulierung: "Neue Rifts verfügbar ab nächster Episode"
- Risiken: Spieler:innen könnten trotzdem Verwirrung über Verfügbarkeit haben

To-do
- Codex: Paradoxon-Toast-Text präzisieren, Timing-Logik dokumentieren
- QA: Px-Reset-Sequenz in verschiedenen Missionsphasen testen

Nächste Schritte
- Maintainer:innen: Toast-Texte überarbeiten, Paradoxon-Timing klarer kommunizieren
- Notizen: Besonders relevant für neue Spieler:innen

ISSUE #005
- Beobachtung: Boss-DR-Skalierung zeigt inkonsistente Werte zwischen Solo- und Team-Modi
- Diagnose: Solo-Boss zeigt DR 3, 3er-Team zeigt DR 5, aber Dokumentation suggeriert DR 4 für 3er-Team
- Evidenz: Mission 5 Gate 2/2 → Boss-Toast "−5 Schaden pro Treffer" bei 3-Personen-Squad

Lösungsvorschlag
- Ansatz: Boss-DR-Tabelle überprüfen und mit tatsächlicher Implementierung abgleichen
- Risiken: Bestehende Balance könnte sich ändern

To-do
- Codex: Boss-DR-Skala in kampagnenstruktur.md verifizieren und korrigieren
- QA: Boss-Encounters mit allen Teamgrößen (1-5) systematisch testen

Nächste Schritte
- Maintainer:innen: Boss-DR-Dokumentation aktualisieren oder Code-Implementierung anpassen
- Notizen: Kritisch für Balancing, besonders Koop-Teams

ISSUE #006
- Beobachtung: Offline-Mode-Hinweise sind funktional, aber Save-Blocker-Logik ist unklar
- Diagnose: `!offline` zeigt Hilfe, aber `save-blocked: offline` im Trace erscheint inkonsistent
- Evidenz: Offline-Hinweis angezeigt → Speichern versucht → manchmal blockiert, manchmal nicht

Lösungsvorschlag
- Ansatz: Offline-Save-Guard-Logik vereinheitlichen und klarer dokumentieren
- Risiken: Bestehende Offline-Workflows könnten betroffen sein

To-do
- Codex: Offline-Save-Guard-Implementierung überprüfen, konsistente Blocking-Regeln
- QA: Offline-Mode systematisch in verschiedenen Spielphasen testen

Nächste Schritte
- Maintainer:innen: Save-Guard-Matrix dokumentieren, Offline-Handling standardisieren
- Notizen: Wichtig für Spieler:innen mit instabiler Verbindung

ISSUE #007
- Beobachtung: Ask→Suggest-Toggle funktioniert, aber HUD-Suffix "· SUG" verschwindet nach bestimmten Aktionen
- Diagnose: `modus suggest` setzt SUG-ON korrekt, aber Load/Resume löscht das Overlay teilweise
- Evidenz: SUG-Modus aktiviert → Save/Load → HUD zeigt wieder normales Format ohne "· SUG"

Lösungsvorschlag
- Ansatz: SUG-Flag in Save-Schema persistent speichern und bei Load restaurieren
- Risiken: Bestehende Saves ohne SUG-Flag könnten falsch interpretiert werden

To-do
- Codex: SUG-Persistenz in saveGame-Schema implementieren, Load-Handler erweitern
- QA: Ask→Suggest-Persistenz über Save/Load-Zyklen testen

Nächste Schritte
- Maintainer:innen: UI-Flags in Save-Schema ergänzen, Load-Restauration implementieren
- Notizen: Betrifft auch andere UI-Modi wie Accessibility-Settings

ISSUE #008
- Beobachtung: Rift-Seed-Merge bei Acceptance-Save zeigt korrekte Traces, aber Overflow-Handling ist intransparent
- Diagnose: 14→12 Seeds merge zeigt `kept[]`/`overflow[]`, aber Overflow-Kriterien sind unklar
- Evidenz: Seed-Merge-Log zeigt 12 kept, 2 overflow, aber keine Erklärung der Prioritätskriterien

Lösungsvorschlag
- Ansatz: Seed-Merge-Algorithmus dokumentieren, Overflow-Kriterien transparent machen
- Risiken: Komplexe Merge-Logik könnte Spieler:innen überfordern

To-do
- Codex: Rift-Seed-Merge-Dokumentation erweitern, Prioritätskriterien definieren
- QA: Verschiedene Seed-Overflow-Szenarien systematisch testen

Nächste Schritte
- Maintainer:innen: Merge-Algorithmus dokumentieren, eventuell vereinfachen
- Notizen: Besonders relevant für High-Level-Spieler:innen mit vielen Seeds

```json
{
  "save_version": "6.0",
  "zr_version": "4.2.6",
  "location": "hq",
  "phase": "briefing",
  "campaign": {
    "episode": 2,
    "mission": 3,
    "scene": 1,
    "mode": "core",
    "total_missions": 23,
    "entry_choice_skipped": false,
    "seed_source": "preserve",
    "rift_seeds": [
      {"id": "rs_001", "level_range": "1-25", "status": "available", "seed_tier": "early"},
      {"id": "rs_002", "level_range": "80-150", "status": "locked", "seed_tier": "mid"},
      {"id": "rs_003", "level_range": "400-1000", "status": "locked", "seed_tier": "high"}
    ]
  },
  "character": {
    "name": "Agent Meridian",
    "level": 120,
    "attributes": {"STR": 8, "GES": 12, "INT": 14, "CHA": 10, "TEMP": 9, "SYS": 11},
    "stress": 2,
    "stress_max": 8,
    "health": 6,
    "health_max": 6,
    "loadout": ["Comlink", "Scanner", "Dietrich-Set", "Pistole"]
  },
  "economy": {
    "cu": 450,
    "wallets": {
      "main": 450,
      "emergency": 0,
      "faction_reserve": 0
    },
    "faction_rep": {"ITI": 75, "Chronos_Guild": 25, "Rogue_Agents": -10}
  },
  "logs": {
    "artifact_log": [{"name": "Chrono-Stabilizer", "acquired": "EP2_MS2", "effects": "+2 TEMP"}],
    "market": [{"transaction": "Scanner_upgrade", "cost": 80, "episode": 2}],
    "offline": [],
    "kodex": [{"query": "Paradoxon-Index", "response": "Aktuell bei 3/5", "timestamp": "2025-01-15T10:30:00Z"}],
    "alias_trace": [],
    "squad_radio": [{"speaker": "Agent_Kappa", "message": "Infiltration bestätigt", "scene": "EP2_MS3_SC1"}],
    "foreshadow": [{"mission": 5, "hints_completed": 2, "total_required": 4}],
    "fr_interventions": [],
    "psi": [{"event": "psi_conflict", "heat_gained": 1, "resolved": true}],
    "arena_psi": [],
    "trace": [
      {"event": "mission_start", "mission": 3, "timestamp": "2025-01-15T10:00:00Z"},
      {"event": "boss_gate_check", "status": "blocked", "fs_count": "2/4"},
      {"event": "save_attempt", "result": "blocked", "reason": "mission_active"}
    ],
    "hud": [
      {"event": "boss_gate_warning", "message": "Gate blockiert – FS 2/4", "scene": "EP2_MS2_SC12"},
      {"event": "vehicle_clash", "details": {"tempo": 85, "stress": 3, "damage": 1}, "at": "2025-01-15T10:15:00Z"}
    ],
    "flags": {
      "qa_mode": true,
      "last_save_at": "2025-01-15T09:45:00Z",
      "chronopolis_unlocked": true,
      "chronopolis_unlock_level": 10,
      "self_reflection_auto_reset_mission_5": true,
      "self_reflection_auto_reset_mission_10": false,
      "atmosphere_contract_capture": {
        "lines": ["Kamera folgt Agent Meridian durch den Korridor", "HUD zeigt Stress 2/8", "Comlink knistert leise"],
        "banned_terms": {"status": "PASS", "hits": []},
        "howto_hits": [],
        "hud_toasts": 2
      },
      "hud_scene_usage": {"current_scene": 2, "budget_limit": 2, "suppressed": 0},
      "toast_suppressed": []
    }
  },
  "ui": {
    "intro_seen": true,
    "accessibility": {"contrast": "high", "badge_density": "compact", "output_pace": "normal"},
    "suggest_mode": true
  },
  "arena": {
    "active": false,
    "previous_mode": null,
    "matches_completed": 7,
    "current_rating": 1250
  },
  "arc_dashboard": {
    "available_arcs": ["Corporate_Infiltration", "Temporal_Anomaly_Hunt"],
    "completed_arcs": ["Training_Simulation"],
    "current_arc": null
  }
}
```

| Schritt | Beschreibung | Status | Evidenz |
|---------|-------------|--------|---------|
| 1 | Solo klassisch Start | PASS | dispatch_hint trace logged |
| 2 | Solo schnell Start | PASS | character creation bypassed |
| 3 | NPC-Team Erstellung | PASS | 3 NPCs generated successfully |
| 4 | Gruppe Zahlenfehler | PASS | error message "Bei gruppe keine Zahl angeben" |
| 5 | NPC-Team 5 Fehler | PASS | error message "NPC-Begleiter: 0-4" |
| 6 | Spiel laden HQ-Recap | PASS | skip_entry_choice=true, kodex overlay shown |
| 7 | Mission Save-Blocker | PASS | "SaveGuard: Speichern nur im HQ" |
| 8 | Ask→Suggest Toggle | FAIL | SUG-Flag nicht persistent nach Load |
| 9 | Px 5 Seed-Hinweis | PASS | "Seeds spielbar nach Episodenende" |
| 10 | Boss-Gate Mission 5 | PASS | GATE 2/2, FS 0/4, Boss-DR aktiviert |
| 11 | Self-Reflection Reset | PASS | SF-OFF → SF-ON nach Mission |
| 12 | Psi-Heat Reset | PASS | +1 im Konflikt, Reset nach HQ-Transfer |
| 13 | Accessibility Dialog | PASS | contrast/badge_density/output_pace saved |
| 14 | Accessibility Persistenz | PASS | settings restored after save/load |
| 15 | Offline-Mode | PASS | offline_help() shown, save-blocked trace |
