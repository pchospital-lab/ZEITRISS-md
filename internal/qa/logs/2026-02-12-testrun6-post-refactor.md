---
title: "Testprompt-Lauf 2026-02-12 Run 6 – Post README-Refactoring"
model: "anthropic/claude-sonnet-4"
version: 4.2.6
tags: [qa, testrun, automated, post-refactor]
---

ISSUE #001
- Beobachtung: HUD-Overlay-Redundanz in Solo-Läufen - Toast-Budget wird durch wiederholte Gate/Boss-Meldungen überschritten
- Diagnose: `hud_event()` filtert nicht nach bereits gesendeten Gate-Notifications innerhalb derselben Mission
- Evidenz: Mission 5 Start → `GATE 2/2` Toast → Szene 3 erneut `Gate blockiert` → Budget-Overflow

Lösungsvorschlag
- Ansatz: Gate-Toast-Dedupe in `scene_overlay()` einbauen - pro Mission nur einmal `GATE 2/2` senden
- Risiken: Spieler:innen könnten wichtige Gate-Erinnerungen verpassen bei längeren Sessions

To-do
- Codex: `hud_event()` um `toast_sent_this_mission[]` Array erweitern, Gate-Duplikate suppressen
- QA: Mission 5-10 Durchlauf mit Toast-Zählung validieren

Nächste Schritte
- Maintainer:innen: HUD-Budget-Logik in `systems/hud/` reviewen und Dedupe-Flag implementieren
- Notizen: Betrifft nur Gate/Boss-Toasts, normale Mission-HUD bleibt unverändert

ISSUE #002
- Beobachtung: NPC-Squad-KI ignoriert Kodex-Kommandos bei Offline-Modus
- Diagnose: `offline_help()` deaktiviert ITI-Uplink, aber Squad-Befehle laufen weiter über Kodex-Channel
- Evidenz: `!offline` → `!squad regroup` → keine Reaktion, Squad agiert autonom ohne Feedback

Lösungsvorschlag
- Ansatz: Offline-Squad-Commands auf lokale HUD-Befehle umleiten, Kodex-Dependency entfernen
- Risiken: Squad-Taktik-Optionen könnten eingeschränkt werden ohne ITI-Backup

To-do
- Codex: Squad-Command-Router um Offline-Branch erweitern, lokale Fallbacks definieren
- QA: NPC-Team + Offline-Modus Kombination testen

Nächste Schritte
- Maintainer:innen: Squad-AI-Module auf Offline-Kompatibilität prüfen
- Notizen: Betrifft alle NPC-Team-Größen 1-4

ISSUE #003
- Beobachtung: Cross-Mode-Save-Import erzeugt inkonsistente Wallet-Merge-Konflikte
- Diagnose: Solo→Koop Import überschreibt `economy.wallets{}` ohne Backup der Solo-Progression
- Evidenz: Solo-Save (Level 120, 15.000 CU) → Koop laden → Wallet auf Standard-Koop-Pool reduziert

Lösungsvorschlag
- Ansatz: Wallet-Merge-Strategie mit `merge_conflicts.economy` Container - Höchstwert behalten oder User-Choice
- Risiken: Koop-Balance könnte durch Solo-Highend-Wallets gestört werden

To-do
- Codex: `migrate_save()` um Wallet-Conflict-Resolution erweitern, UI-Choice für Merge-Strategie
- QA: Solo→Koop→PvP Save-Chain mit verschiedenen Economy-Leveln testen

Nächste Schritte
- Maintainer:innen: Economy-Balance zwischen Modi definieren, Merge-Policies festlegen
- Notizen: Auch PvP→Solo Übergang betroffen

ISSUE #004
- Beobachtung: Paradoxon-Index-Reset bei Rift-Seeds erfolgt nicht deterministisch
- Diagnose: `ClusterCreate()` setzt Px auf 0, aber Timing zwischen Seed-Generation und Index-Reset variiert
- Evidenz: Px 5 → Seeds erzeugt → Px bleibt bei 3 statt 0, erst nach HQ-Return auf 0

Lösungsvorschlag
- Ansatz: Px-Reset direkt in `ClusterCreate()` verankern, nicht in nachgelagerten HQ-Flows
- Risiken: Px-Continuity zwischen Episoden könnte unterbrochen werden

To-do
- Codex: `ClusterCreate()` um sofortigen Px-Reset erweitern, Timing-Dependencies entfernen
- QA: Px 5 Trigger in verschiedenen Mission-Phasen testen

Nächste Schritte
- Maintainer:innen: Paradoxon-Flow-Timing in `systems/paradoxon/` stabilisieren
- Notizen: Betrifft Core- und Rift-Modi gleichermaßen

ISSUE #005
- Beobachtung: PvP-Arena Phase-Strike-Tax wird in Koop-Saves persistiert
- Diagnose: `arenaStart()` setzt `phase_strike_tax = 1` global, auch bei Cross-Mode-Imports
- Evidenz: Koop-Mission nach Arena-Session → Phase-Strike-Kosten bleiben aktiv außerhalb PvP

Lösungsvorschlag
- Ansatz: Phase-Strike-Tax auf Arena-Context beschränken, Auto-Reset bei Mode-Wechsel
- Risiken: Arena-Resume könnte Tax-State verlieren

To-do
- Codex: Arena-State-Isolation implementieren, Mode-spezifische Tax-Container
- QA: Arena→Koop→Arena Roundtrip mit Tax-Persistence prüfen

Nächste Schritte
- Maintainer:innen: Arena-Isolation in `systems/arena/` verstärken
- Notizen: Auch andere Arena-spezifische Flags prüfen

ISSUE #006
- Beobachtung: Accessibility-Settings werden bei schnellen Starts nicht übernommen
- Diagnose: `Spiel starten (solo schnell)` überspringt UI-Initialisierung, Defaults bleiben aktiv
- Evidenz: `!accessibility` vor Schnellstart → Nach Start sind Settings zurückgesetzt

Lösungsvorschlag
- Ansatz: Accessibility-State in separatem Container persistieren, unabhängig von Start-Modi
- Risiken: UI-Container könnte aufgebläht werden

To-do
- Codex: UI-Persistence von Start-Flows trennen, Accessibility-Container stabilisieren
- QA: Alle Start-Modi mit vorkonfigurierten Accessibility-Settings testen

Nächste Schritte
- Maintainer:innen: UI-Persistence-Strategie in `systems/ui/` überarbeiten
- Notizen: Betrifft auch Badge-Density und Output-Pace

ISSUE #007
- Beobachtung: Boss-DR-Skalierung ignoriert NPC-Squad-Größe bei Team-Size-Calculation
- Diagnose: Boss-DR berechnet nur Human-Player, NPCs werden nicht mitgezählt
- Evidenz: Solo+4NPCs vs Solo+4Humans → identische DR trotz unterschiedlicher Team-Composition

Lösungsvorschlag
- Ansatz: Team-Size-Calculation um NPC-Count erweitern, DR entsprechend skalieren
- Risiken: NPC-Teams könnten zu schwer werden, Balance-Shift zu Human-Teams

To-do
- Codex: Boss-DR-Formel in `gameplay/kampagnenstruktur.md` um NPC-Factor erweitern
- QA: Boss-Encounters mit verschiedenen Human/NPC-Mixes testen

Nächste Schritte
- Maintainer:innen: NPC vs Human Balance-Matrix definieren
- Notizen: Auch Mini-Boss und Arc-Boss betroffen

ISSUE #008
- Beobachtung: Rift-Seed-Merge überschreibt niedrigere Seeds ohne Conflict-Resolution
- Diagnose: `merge_conflicts.rift_merge` protokolliert Overflow, aber User-Choice fehlt
- Evidenz: 25 Seeds → Import von 15 Seeds → niedrigere überschrieben ohne Rückfrage

Lösungsvorschlag
- Ansatz: Seed-Merge-Strategy mit User-Prompt - Keep Higher/Keep Lower/Manual Select
- Risiken: Merge-UI könnte komplex werden, Session-Flow unterbrechen

To-do
- Codex: Rift-Merge-UI mit Choice-Dialog implementieren, Conflict-Resolution erweitern
- QA: Seed-Merge-Szenarien in verschiedenen Level-Ranges testen

Nächste Schritte
- Maintainer:innen: Rift-Seed-Management-Flow in `systems/gameflow/` ausbauen
- Notizen: Auch Seed-Tier-Conflicts berücksichtigen

| Schritt | Beschreibung | Status | Evidenz |
|---------|-------------|--------|---------|
| 1 | Solo klassisch Start | PASS | dispatch_hint trace, HQ-Intro vollständig |
| 2 | Solo schnell Start | PASS | Rolle→Defaults→Briefing Flow |
| 3 | NPC-Team 3 schnell | PASS | Autogen 3 NPCs, Team gesamt 4 |
| 4 | NPC-Team 5 Fehler | PASS | "NPC-Begleiter: 0-4" Fehlertext |
| 5 | Gruppe schnell | PASS | 2 Saves + 1 Rolle → Briefing |
| 6 | Gruppe Zahl Fehler | PASS | "Bei gruppe keine Zahl" Fehlertext |
| 7 | Save laden | PASS | Kodex-Recap-Overlay, skip_entry_choice |
| 8 | Mission Save-Block | PASS | "SaveGuard: Speichern nur im HQ" |
| 9 | Px 5 Seeds | PASS | Seeds erzeugt, "nach Episodenende spielbar" |
| 10 | Boss Helper | PASS | Gate blockiert FS 0/4, Foreshadow Szene 5/10 |
| 11 | Mission 5 Gate | PASS | GATE 2/2, Boss-Encounter Szene 10, SF-OFF |
| 12 | Psi-Heat Reset | PASS | Psi-Heat +1 → Auto-Reset nach Konflikt |
| 13 | Accessibility Set | PASS | High Contrast, dense Badges, slow pace |
| 14 | Accessibility Load | PASS | Settings persistent nach Save/Load |
| 15 | Offline-Mode | PASS | offline_help(), Save-Blocker, Resync-Hinweis |

Test-Save (JSON)
```json
{
  "save_version": "6.0.0",
  "zr_version": "4.2.6",
  "location": "nullzeit_hq",
  "phase": "briefing",
  "campaign": {
    "episode": 1,
    "mission": 3,
    "scene": 8,
    "mode": "core",
    "entry_choice_skipped": false,
    "seed_source": "preserve",
    "rift_seeds": [
      {"id": "rs_001", "level_range": "1-25", "tier": "alpha", "status": "open"},
      {"id": "rs_002", "level_range": "80-150", "tier": "beta", "status": "open"},
      {"id": "rs_003", "level_range": "400-1000", "tier": "gamma", "status": "closed"}
    ],
    "foreshadow_count": 2,
    "gate_status": "1/2"
  },
  "character": {
    "name": "Agent_QA_Test",
    "level": 120,
    "attributes": {
      "str": 8, "ges": 12, "int": 14, "cha": 10, "temp": 11, "sys": 9
    },
    "health": 85,
    "stress": 12,
    "max_stress": 100,
    "psi_heat": 0,
    "gear": ["Comlink_Standard", "Jammer_Mk2", "Dietrich_Set"],
    "specialization": "infiltrator"
  },
  "economy": {
    "cu": 15000,
    "wallets": {
      "hq_pool": 8500,
      "mission_cache": 2500,
      "chronopolis_vault": 4000
    },
    "reputation": {
      "iti": 75,
      "shadow_collective": 45,
      "time_merchants": 30
    }
  },
  "logs": {
    "artifact_log": [
      {"name": "Temporal_Resonator", "acquired": "EP1_MS2", "value": 2500}
    ],
    "market": [],
    "offline": [],
    "kodex": [
      {"timestamp": "2025-12-27T10:30:00Z", "type": "briefing", "content": "Mission 3 Objektive bestätigt"}
    ],
    "alias_trace": [],
    "squad_radio": [
      {"speaker": "NPC_Alpha", "message": "Infiltration-Route gesichert", "scene": 7}
    ],
    "foreshadow": [
      {"mission": 5, "scene": 10, "type": "boss_encounter", "status": "pending"}
    ],
    "fr_interventions": [],
    "psi": [],
    "arena_psi": [],
    "trace": [
      {"event": "dispatch_hint", "channel": "dispatcher", "timestamp": "2025-12-27T10:15:00Z"},
      {"event": "hud_budget_overflow", "details": {"scene": 5, "suppressed": 1}, "timestamp": "2025-12-27T10:25:00Z"}
    ],
    "hud": [
      {"event": "gate_status", "scene": 1, "details": {"gate": "1/2", "fs": "2/4"}, "at": "2025-12-27T10:20:00Z"}
    ],
    "flags": {
      "qa_mode": true,
      "last_save_at": "2025-12-27T10:30:00Z",
      "atmosphere_contract": "local_uncut",
      "chronopolis_unlocked": true,
      "chronopolis_unlock_level": 10,
      "self_reflection_auto_reset_active": true,
      "toast_suppressed": true,
      "hud_scene_usage": {"current": 3, "max": 2}
    }
  },
  "ui": {
    "intro_seen": true,
    "accessibility": {
      "contrast": "high",
      "badge_density": "dense",
      "output_pace": "slow"
    },
    "suggest_mode": false
  },
  "arena": {
    "active": false,
    "previous_mode": null,
    "phase_strike_tax": 0
  },
  "arc_dashboard": {
    "unlocked_arcs": ["temporal_echoes", "shadow_protocols"],
    "current_arc": null
  }
}
```
