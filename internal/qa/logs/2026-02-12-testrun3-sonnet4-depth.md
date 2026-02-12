---
title: "Testprompt-Lauf 2026-02-12 Run 3 – Depth + Grounding"
model: "anthropic/claude-sonnet-4"
version: 4.2.6
tags: [qa, testrun, automated, depth-enforced]
---

ISSUE #001
- Beobachtung: HUD-Ausgabe zu komplex und unübersichtlich in frühen Szenen
- Diagnose: Physikalitäts-Gate wird nicht konsequent durchgesetzt - zu viele technische Begriffe ohne Hardware-Referenz
- Evidenz: Infiltrationsszenen zeigen "Netzwerk-Analyse" statt "Terminal-Zugriff mit Handscanner"

Lösungsvorschlag
- Ansatz: Jede Tech-Interaktion muss konkretes Gerät benennen (Comlink, Jammer, Kabel, Terminal)
- Risiken: Könnte Immersion durch ständige Hardware-Erwähnungen belasten

To-do
- Codex: Physicality-Guard in allen Tech-Beschreibungen implementieren
- QA: Stichproben-Check auf Hardware-freie Tech-Referenzen

Nächste Schritte
- Maintainer:innen: Masterprompt um konkrete Hardware-Listen erweitern
- Notizen: Besonders bei Hacking und Überwachung kritisch

ISSUE #002
- Beobachtung: Paradoxon-Index-Mechanik inkonsistent zwischen Core- und Rift-Ops
- Diagnose: ClusterCreate() wird zu früh ausgelöst, Seeds erscheinen vor Episodenende
- Evidenz: Level 120+ Test zeigt Rift-Seeds bereits nach Mission 8 statt nach Debrief

Lösungsvorschlag
- Ansatz: Paradoxon-Reset strikt nach Episodenende, Seeds erst dann spielbar
- Risiken: Spieler könnten Progression als zu langsam empfinden

To-do
- Codex: Paradoxon-Index-Reset-Timing korrigieren
- QA: Episodenende-Trigger für alle Level-Bereiche testen

Nächste Schritte
- Maintainer:innen: Seed-Verfügbarkeit an Episodenstatus koppeln
- Notizen: Besonders kritisch bei Level 400+ Progression

ISSUE #003
- Beobachtung: Save/Load-Schema unvollständig bei Cross-Mode-Transfers
- Diagnose: Solo-Saves in Koop-Mode verlieren Squad-Daten, keine merge_conflicts-Behandlung
- Evidenz: JSON-Export zeigt fehlende squad_radio und ui.host_override Einträge

Lösungsvorschlag
- Ansatz: Vollständige Cross-Mode-Validierung mit Conflict-Resolution
- Risiken: Komplexere Save-Struktur könnte Performance belasten

To-do
- Codex: Cross-Mode-Save-Handler implementieren mit merge_conflicts Container
- QA: Alle Mode-Kombinationen (Solo↔Koop↔PvP) durchtesten

Nächste Schritte
- Maintainer:innen: Save-Schema um Cross-Mode-Felder erweitern
- Notizen: Priorität auf Solo→Koop Transfers legen

ISSUE #004
- Beobachtung: Boss-DR-Skalierung bei großen Teams (4-5 Spieler) zu schwach
- Diagnose: DR-Formel berücksichtigt Teamsynergien nicht ausreichend
- Evidenz: 5er-Team eliminiert Mission-10-Boss in 3 Runden statt erwarteten 8-12

Lösungsvorschlag
- Ansatz: Exponentielles DR-Scaling ab 4+ Teammitgliedern
- Risiken: Könnte große Teams übermäßig bestrafen

To-do
- Codex: Boss-DR-Formel für Teams 4+ anpassen
- QA: Kampfdauer-Statistiken für alle Teamgrößen sammeln

Nächste Schritte
- Maintainer:innen: Balance-Daten aus Playtests einbeziehen
- Notizen: Auch Mini-Boss-Skalierung überprüfen

ISSUE #005
- Beobachtung: Kodex-Kommandos in Offline-Mode unzureichend dokumentiert
- Diagnose: !offline zeigt nur Basis-Hinweise, erweiterte Funktionen fehlen
- Evidenz: Offline-Save-Blocker und Resync-Prozedur nicht im Hilfetext

Lösungsvorschlag
- Ansatz: Vollständige Offline-Dokumentation mit allen verfügbaren Kommandos
- Risiken: Zu detaillierte Hilfe könnte UI überladen

To-do
- Codex: Offline-Hilfe um Save-Blocker und Resync-Hinweise erweitern
- QA: Offline-Mode-Funktionalität komplett durchgehen

Nächste Schritte
- Maintainer:innen: Offline-Dokumentation in runtime-Module einarbeiten
- Notizen: Auch für Accessibility-Integration relevant

ISSUE #006
- Beobachtung: HUD-Toast-Budget wird in Action-Szenen regelmäßig überschritten
- Diagnose: Vehicle-Clash und Mass-Conflict Events umgehen Budget-Kontrolle
- Evidenz: 4+ Toasts in Verfolgungsszenen trotz 2-Toast-Limit

Lösungsvorschlag
- Ansatz: Sonder-Events in Budget einrechnen oder explizit ausklammern
- Risiken: Wichtige Action-Info könnte unterdrückt werden

To-do
- Codex: HUD-Budget-System für Sonder-Events überarbeiten
- QA: Toast-Zählung in verschiedenen Szenentypen validieren

Nächste Schritte
- Maintainer:innen: HUD-Event-Prioritäten neu definieren
- Notizen: QA-Mode-Traces für Budget-Overflow nutzen

ISSUE #007
- Beobachtung: Chronopolis-Freischaltung zu früh im Spielverlauf
- Diagnose: Level 10+ Zugang überspringt wichtige Stadt-Progression
- Evidenz: Spieler umgehen Fraktions-Services durch direkten Chronopolis-Zugang

Lösungsvorschlag
- Ansatz: Chronopolis-Freischaltung auf Level 20+ verschieben oder Voraussetzungen erweitern
- Risiken: Könnte Endgame-Content zu weit nach hinten schieben

To-do
- Codex: Chronopolis-Unlock-Bedingungen überprüfen und anpassen
- QA: Stadt-Progression vs. Chronopolis-Timing analysieren

Nächste Schritte
- Maintainer:innen: Balance zwischen Stadt-Content und Endgame finden
- Notizen: Spieler-Feedback zu Progression-Geschwindigkeit einbeziehen

ISSUE #008
- Beobachtung: Ask→Suggest-Toggle-Persistenz fehlerhaft nach Load
- Diagnose: UI-State wird nicht korrekt in Save-Schema übertragen
- Evidenz: !modus suggest setzt nach Reload auf Ask zurück

Lösungsvorschlag
- Ansatz: UI-Flags vollständig in Save-Container integrieren
- Risiken: Save-Größe könnte durch UI-State-Daten anwachsen

To-do
- Codex: UI-Persistenz-Layer für alle Modi-Toggles implementieren
- QA: Load-Roundtrip für alle UI-Einstellungen testen

Nächste Schritte
- Maintainer:innen: Save-Schema um UI-Container erweitern
- Notizen: Auch für Accessibility-Settings relevant

| Schritt | Beschreibung | Status | Evidenz |
|---------|-------------|--------|---------|
| 1 | Solo klassisch Start | PASS | dispatch_hint trace logged |
| 2 | Solo schnell Start | PASS | role selection → briefing flow |
| 3 | NPC-Team Erstellung | PASS | 3 NPCs autogen, briefing reached |
| 4 | NPC-Team Überzahl | PASS | Error text "0-4 Begleiter" shown |
| 5 | Gruppe schnell | PASS | 2 saves + 1 role → briefing |
| 6 | Gruppe mit Zahl | PASS | Error "keine Zahl bei gruppe" |
| 7 | Save laden | PASS | HQ recap, skip_entry_choice=true |
| 8 | Mission Save-Block | PASS | "SaveGuard: nur im HQ" message |
| 9 | Px 5 Seeds | PASS | Seeds created, "nach Episodenende" |
| 10 | Boss Helper | PASS | Mission 4→5 foreshadow listed |
| 11 | Mission 5 Gate | PASS | GATE 2/2, FS 0/4, Boss-DR toast |
| 12 | Psi-Heat Reset | PASS | +1 in conflict, auto-reset to 0 |
| 13 | Accessibility Dialog | FAIL | Toast shown but settings not saved |
| 14 | UI Persistenz | FAIL | Settings lost after reload |
| 15 | Offline-Mode | PASS | Help shown, save-blocker active |

Test-Save (JSON)
```json
{
  "save_version": "6.0",
  "zr_version": "4.2.6",
  "location": "hq",
  "phase": "briefing",
  "campaign": {
    "episode": 1,
    "mission": 3,
    "scene": 7,
    "mode": "core",
    "difficulty": "standard",
    "entry_choice_skipped": false,
    "seed_source": "preserve",
    "rift_seeds": [
      {
        "id": "rift_001",
        "level_range": "1-25",
        "status": "locked",
        "unlock_after_episode": 1
      },
      {
        "id": "rift_002",
        "level_range": "80-150",
        "status": "locked",
        "unlock_after_episode": 2
      }
    ]
  },
  "character": {
    "name": "Agent Sigma",
    "level": 120,
    "attributes": {
      "STR": 8,
      "GES": 12,
      "INT": 14,
      "CHA": 6,
      "TEMP": 10,
      "SYS": 11
    },
    "health": 85,
    "stress": 12,
    "max_stress": 100,
    "gear": [
      "Comlink (verschlüsselt)",
      "Handscanner MkIII",
      "Zeitanker-Modul"
    ]
  },
  "economy": {
    "credits": 15420,
    "wallets": {
      "hq_pool": 8500,
      "mission_cache": 3200,
      "chronopolis_fund": 3720
    }
  },
  "logs": {
    "artifact_log": [
      {
        "name": "Temporaler Stabilisator",
        "acquired": "Mission 2",
        "effect": "+2 TEMP bei Paradoxon-Checks"
      }
    ],
    "market": [],
    "offline": [],
    "kodex": [
      {
        "query": "Paradoxon-Index Status",
        "response": "Aktuell bei 2/5 - moderate Verzerrung",
        "timestamp": "2025-12-27T14:30:00Z"
      }
    ],
    "alias_trace": [],
    "squad_radio": [
      {
        "sender": "Agent Delta",
        "message": "Exfil-Route gesichert",
        "timestamp": "2025-12-27T14:25:00Z"
      }
    ],
    "foreshadow": [],
    "fr_interventions": [],
    "psi": [
      {
        "event": "Psi-Konflikt Mission 2",
        "heat_gained": 1,
        "auto_reset": true
      }
    ],
    "arena_psi": [],
    "trace": [
      {
        "event": "dispatch_hint",
        "channel": "dispatcher",
        "details": "Solo klassisch gestartet"
      },
      {
        "event": "save_blocked",
        "reason": "mission_active",
        "message": "SaveGuard: Speichern nur im HQ"
      }
    ],
    "hud": [
      {
        "event": "vehicle_clash",
        "scene": 5,
        "details": {
          "tempo": 8,
          "stress": 15,
          "damage": 2
        },
        "at": "2025-12-27T14:20:00Z"
      }
    ],
    "flags": {
      "qa_mode": true,
      "chronopolis_unlocked": true,
      "chronopolis_unlock_level": 10,
      "last_save_at": "2025-12-27T14:35:00Z",
      "atmosphere_contract_capture": {
        "lines": 10,
        "banned_terms": {
          "status": "PASS",
          "hits": []
        },
        "howto_hits": [],
        "hud_toasts": 2
      }
    }
  },
  "ui": {
    "intro_seen": true,
    "contrast": "standard",
    "badge_density": "standard",
    "output_pace": "normal"
  },
  "arena": {
    "active": false,
    "previous_mode": null
  },
  "arc_dashboard": {
    "unlocked_arcs": [],
    "current_arc": null
  }
}
```
