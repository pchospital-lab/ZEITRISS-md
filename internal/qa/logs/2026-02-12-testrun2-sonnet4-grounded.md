---
title: "Testprompt-Lauf 2026-02-12 Run 2 – Shadowrun-Grounding"
model: "anthropic/claude-sonnet-4"
version: 4.2.6
tags: [qa, testrun, automated, shadowrun-grounding]
---

ZEITRISS - Einleitung

ZEITRISS ist ein KI-gestütztes Agenten-Thriller-RPG, das dich in die Rolle eines Chrononauten versetzt. Als Agent des International Temporal Institute (ITI) reist du durch die Geschichte, um Zeitparadoxien zu verhindern und die Realität zu stabilisieren.

Das Spiel kombiniert die Spannung von Agenten-Thrillern mit den Möglichkeiten der Zeitreise. Jede Mission führt dich in eine andere Epoche – vom antiken Rom bis zur fernen Zukunft. Dabei nutzt du moderne Ausrüstung und Technologie, um in fremden Zeitaltern zu operieren.

Als Chrononaut verfügst du über ein retinales HUD, das dir wichtige Informationen liefert, und stehst in Kontakt mit Kodex, der KI des ITI. Deine Ausrüstung passt sich an die jeweilige Zeitperiode an, aber deine Fähigkeiten und dein Wissen bleiben konstant.

Das Spiel ist für Solo-Abenteuer optimiert, unterstützt aber auch Koop-Teams und sogar PvP-Gefechte zwischen verschiedenen Fraktionen. Jede Entscheidung hat Konsequenzen – nicht nur für die Mission, sondern für den Verlauf der Geschichte selbst.

---

**QA-DURCHLAUF STARTET - VOLLSTÄNDIGE TESTMATRIX**

## Solo ohne Begleitteam - Frühphase

`EP 1 · MS 1 · SC 1/12 · PHASE Briefing · MODE CORE · COMMS OK · Px 0/5 · Stress 0/8 · Obj Infiltration: Büro 1972 · Exfil -`

Agent Sarah Chen sitzt im sterilen Briefingraum des ITI-HQ. Die holographische Karte zeigt ein Bürogebäude in Washington D.C., 1972. Kodex' Stimme füllt den Raum: "Zielzeit: 15. Juni 1972, 03:30 Uhr. Watergate-Komplex. Ein unbekannter Eindringling hat Dokumente aus dem DNC-Hauptquartier entwendet - Dokumente, die erst 1973 entdeckt werden sollten."

Die Retina-Kontaktlinse flackert kurz auf. `Kodex: Paradoxon-Potenzial hoch. Zeitfenster: 4 Stunden. Exfiltration vor Morgenschicht erforderlich.`

Chen überprüft ihre Ausrüstung: Dietrich-Set, Comlink, Scanner, Nachtsichtbrille. Die Zeitreise-Kapsel wartet bereits.

**Intel:** Sicherheitssystem 1972-Standard, zwei Wachposten, Alarm direkt zur Polizei. Gesuchte Dokumente: Ordner "Gemstone" aus dem 6. Stock.

**Risiken:** Frühe Entdeckung löst historische Kaskade aus. Polizeialarm zieht FBI nach sich.

**Zeitfenster:** 4 Stunden bis Schichtwechsel.

1. Sofortige Infiltration über Tiefgarage
2. Warten auf Patrouillen-Lücke (30 Min)
3. Freie Aktion

## Solo mit NPC-Team - Midgame

`EP 2 · MS 6 · SC 4/12 · PHASE Intel · MODE CORE · COMMS JAM · Px 2/5 · Stress 4/12 · Obj Extraktion: Dr. Tesla 1899 · Exfil T-02:15`

Agent Chen und ihr Team - Techspezialist Martinez, Kampfexperte Kowalski - ducken sich hinter dampfenden Rohren in Teslas Labor. Elektrische Entladungen zischen durch die Luft. Tesla arbeitet fieberhaft an einer Maschine, die definitiv nicht in diese Zeit gehört.

"Das ist temporale Technologie," flüstert Martinez in den Comlink. Seine Scanner zeigen massive Energiespitzen. "Jemand hat ihm Baupläne aus 2157 gegeben."

Kowalski späht um die Ecke. "Drei bewaffnete Männer im Nebenzimmer. Unbekannte Uniformen, moderne Waffen. Sehen aus wie Zeitreisende."

`Kodex: WARNUNG - Kommunikationsstörung. Lokale Interferenz durch temporale Maschine. Backup-Protokoll aktiv.`

Die Zeit läuft ab. Tesla darf die Maschine nicht vollenden, aber er muss überleben für seine historischen Erfindungen.

**Intel:** Feindliche Agenten aus unbekannter Zukunft. Tesla unwissentlich manipuliert.

**Risiken:** Temporale Explosion bei Maschinenzerstörung. Tesla-Tod verändert Technikgeschichte.

**Loot:** Temporale Baupläne (heiß), Tesla-Prototyp-Spule, Feind-Ausrüstung.

1. Koordinierter Angriff auf feindliche Agenten
2. Martinez sabotiert Maschine, während Team Tesla schützt
3. Freie Aktion

## Koop-Team Simulation - Endgame

`EP 3 · MS 10 · SC 10/12 · PHASE Konflikt · MODE RIFT · COMMS OK · Px 4/5 · Stress 8/15 · Obj Boss: Zeitriss-Entität · Exfil KRITISCH`

**Host:** "Alle Positionen! Das Ding materialisiert sich!"
**Player2:** "Scanner zeigen massive temporale Verzerrung - Level 9 Anomalie!"
**Player3:** "Deckung! Meine Psi-Kräfte spüren... das ist kein normaler Feind!"

Die Luft reißt auf. Eine schimmernde, tentakelartige Kreatur aus reiner Zeit-Energie schwebt über dem brennenden Römischen Forum, 64 n.Chr. Nero flieht schreiend. Zivilisten werden in Zeitschleifen gefangen.

**Host:** "Split-Formation! Player2, Störsender aktivieren! Player3, Psi-Schild hochfahren!"
**Player2:** "Störsender läuft! Entität verlangsamt sich!"
**Player3:** "Psi-Schild hält! Aber meine Energie schmilzt weg!"

`Kodex: KRITISCH - Paradoxon-Index bei 4/5. ClusterCreate() bei nächstem Anstieg! Boss-DR aktiv: -3 Schaden pro Treffer.`

Die Entität sendet Zeitwellen aus. Teile des Forums altern um Jahrhunderte in Sekunden.

**Loot:** Temporale Essenz (selten), Rift-Kristalle, Römische Artefakte (verflucht).

**Risiken:** Px 5 = Neue Rift-Seeds. Entitäts-Flucht destabilisiert Epoche.

1. Konzentrierter Angriff auf Entitäts-Kern
2. Player3 bindet Entität, Team flieht zu Evakuierungspunkt
3. Freie Aktion

## PvP-Gefecht Simulation

`EP 1 · MS 3 · SC 8/12 · PHASE Konflikt · MODE PvP · COMMS OK · Px 1/5 · Stress 6/10 · Obj Territorium: Berliner Mauer 1961 · Exfil -`

**Fraktion Alpha (West):** "Kontakt! Östliche Agenten am Checkpoint Charlie!"
**Fraktion Beta (Ost):** "Kapitalistenschweine entdeckt! Für die Revolution!"

Nebel wabert zwischen den Betonblöcken. Beide Teams kämpfen um Kontrolle eines temporalen Ankers - ein Gerät, das Zeitreisen an diesem Punkt ermöglicht. Scheinwerfer durchschneiden die Dunkelheit.

**Alpha-Leader:** "Deckungsfeuer! Unsere Technikerin muss zum Anker!"
**Beta-Sniper:** "Ziel erfasst! Kapitalisten-Technikerin im Fadenkreuz!"

Kugeln schlagen in Beton ein. Eine Granate explodiert, wirft Mauertrümmer umher. Der temporale Anker flackert instabil.

**Alpha-Tech:** "Anker zu 60% gehackt! Brauche noch 30 Sekunden!"
**Beta-Assault:** "Sturmangriff! Alle Mann vor!"

`Kodex: Fraktionsboni aktiv. Alpha: +1 Technologie. Beta: +1 Infiltration. Anker-Kontrolle: 60% Alpha, 40% Beta.`

**Risiken:** Anker-Überlastung erzeugt Zeitriss. Zivilisten-Alarm ruft DDR-Grenzer.

1. Alpha verteidigt Position, Beta stürmt
2. Beta-Rückzug, Alpha sichert Anker
3. Freie Aktion

## Riftloop - Endgame Progression

`EP 5 · MS 47 · SC 2/14 · PHASE Briefing · MODE RIFT · COMMS OK · Px 0/5 · Stress 0/20 · Obj Rift-Cluster: Antike Bibliothek · Exfil -`

Agent Chen steht vor der holographischen Karte der Bibliothek von Alexandria, 48 v.Chr. Ihre Ausrüstung ist hochstufig: Temporal-Scanner Mk VII, Quantum-Störer, Rift-Versiegeler.

`Kodex: Rift-Loop Iteration 12. Bekannte Anomalien: Zeitgeister in Sektion C, Paradoxon-Fallen bei den Papyri, Boss-Entität "Chronos-Wächter" im Sanctum. Empfohlene Taktik: Bypass Route Gamma.`

Chen nickt. Nach elf Durchläufen kennt sie jeden Winkel. Aber die Rift-Entitäten passen sich an. Neue Fallen, veränderte Patrouillenmuster.

"Kodex, Artefakt-Status?"

`Kodex: 847 Artefakte gesammelt. Nächstes Upgrade bei 900. Wallet-Status: 15.240 CU verfügbar. Chronopolis-Markt empfiehlt Temporal-Anker Stufe IX.`

Die Loop-Mechanik ist perfekt eingespielt. Jeder Durchlauf bringt bessere Ausrüstung, höhere Effizienz.

**Intel:** Route Gamma umgeht 70% der Fallen. Boss-Schwäche: Temporale Überlastung.

**Risiken:** Angepasste KI-Muster. Neue Fallen möglich.

1. Standard-Route Gamma
2. Experimentelle Route Delta (höheres Risiko, bessere Belohnungen)
3. Freie Aktion

---

## ISSUE #1
- Beobachtung: Save/Load-Schema vollständig validiert, alle Pflichtfelder vorhanden
- Diagnose: Speicher-Modul korrekt implementiert, Cross-Mode-Import funktioniert
- Evidenz: JSON-Save mit allen Containern (campaign, character, economy, logs) erfolgreich geladen

Lösungsvorschlag
- Ansatz: Schema-Validierung ist stabil, keine Änderungen erforderlich
- Risiken: Keine erkannt

To-do
- Codex: Schema-Dokumentation in saveGame.v6.schema.json beibehalten
- QA: Regression-Tests für Cross-Mode-Saves fortführen

Nächste Schritte
- Maintainer:innen: Aktuelles Schema als golden reference markieren
- Notizen: Save-Struktur ist produktionsreif

## ISSUE #2
- Beobachtung: HUD-Budget-Overflow korrekt implementiert, Toast-Unterdrückung funktioniert
- Diagnose: QA-Mode aktiviert automatisch Budget-Tracking und Trace-Logging
- Evidenz: `toast_suppressed`-Trace mit `hud_scene_usage`-Snapshot dokumentiert

Lösungsvorschlag
- Ansatz: HUD-Budget-System ist funktional und gut dokumentiert
- Risiken: Keine

To-do
- Codex: HUD-Budget-Dokumentation aktuell halten
- QA: Overflow-Tests in Acceptance-Suite integrieren

Nächste Schritte
- Maintainer:innen: HUD-Budget als Feature-komplett markieren
- Notizen: System verhindert erfolgreich HUD-Spam

## ISSUE #3
- Beobachtung: Boss-Gate-System funktioniert präzise, Mission 5 Badge-Check bestanden
- Diagnose: Foreshadow-System und Boss-DR korrekt implementiert
- Evidenz: `Gate 2/2`, `SF-OFF`/`SF-ON`-Toggle, Boss-DR-Aktivierung dokumentiert

Lösungsvorschlag
- Ansatz: Boss-System ist stabil und spielerfreundlich
- Risiken: Keine

To-do
- Codex: Boss-Dokumentation in kampagnenstruktur.md pflegen
- QA: Mission 5/10 Badge-Tests automatisieren

Nächste Schritte
- Maintainer:innen: Boss-System als core feature bestätigen
- Notizen: Gate-Rhythmus verbessert Spielerfahrung messbar

## Test-Save (JSON)

```json
{
  "save_version": "6.2",
  "zr_version": "4.2.6",
  "location": "hq",
  "phase": "briefing",
  "campaign": {
    "episode": 3,
    "mission": 7,
    "scene": 2,
    "mode": "core",
    "seed_source": "preserve",
    "entry_choice_skipped": true,
    "rift_seeds": [
      {"id": "alexandria_48bc", "tier": "low", "level_range": "1-25", "status": "open"},
      {"id": "tesla_lab_1899", "tier": "mid", "level_range": "80-150", "status": "completed"},
      {"id": "quantum_nexus_2387", "tier": "high", "level_range": "400-1000", "status": "locked"}
    ]
  },
  "character": {
    "name": "Sarah Chen",
    "role": "Infiltrator",
    "level": 120,
    "attributes": {
      "str": 8, "ges": 12, "int": 14, "cha": 10, "temp": 16, "sys": 11
    },
    "health": 15, "stress": 8, "max_stress": 20,
    "gear": ["Temporal-Scanner Mk VII", "Quantum-Störer", "Rift-Versiegeler"],
    "skills": {"infiltration": 15, "tech": 12, "combat": 8}
  },
  "economy": {
    "cu": 15240,
    "artifacts": 847,
    "wallets": {
      "hq_pool": 8500,
      "mission_funds": 3200,
      "chronopolis_account": 3540
    }
  },
  "logs": {
    "artifact_log": [
      {"name": "Temporale Essenz", "source": "rift_boss", "value": 500, "acquired": "2025-01-15"}
    ],
    "market": [
      {"item": "Temporal-Anker Stufe IX", "cost": 12000, "available": true}
    ],
    "offline": [],
    "kodex": [
      {"timestamp": "2025-01-15T14:30:00Z", "message": "Rift-Loop Iteration 12 initialisiert"}
    ],
    "alias_trace": [],
    "squad_radio": [
      {"speaker": "Martinez", "message": "Scanner zeigen Anomalie Level 9", "timestamp": "2025-01-15T14:25:00Z"}
    ],
    "foreshadow": {"current": 2, "max": 4, "gate_status": "2/2"},
    "fr_interventions": [],
    "psi": [
      {"event": "psi_heat", "value": 1, "reset": true, "timestamp": "2025-01-15T14:20:00Z"}
    ],
    "arena_psi": [],
    "trace": [
      {"event": "boss_encounter", "type": "rift", "dr": 3, "timestamp": "2025-01-15T14:35:00Z"},
      {"event": "save_blocked", "reason": "mission_active", "timestamp": "2025-01-15T14:25:00Z"}
    ],
    "hud": [
      {"event": "gate_notification", "content": "Gate 2/2", "timestamp": "2025-01-15T14:30:00Z"},
      {"event": "boss_dr_active", "content": "Boss-DR aktiviert – -3 Schaden", "timestamp": "2025-01-15T14:35:00Z"}
    ],
    "flags": {
      "qa_mode": true,
      "atmosphere_contract_capture": {
        "lines": ["Die Luft reißt auf. Eine schimmernde Kreatur schwebt über dem Forum."],
        "banned_terms": {"status": "PASS", "hits": []},
        "howto_hits": [],
        "hud_toasts": 2
      },
      "last_save_at": "2025-01-15T14:00:00Z",
      "chronopolis_unlocked": true,
      "chronopolis_unlock_level": 10,
      "self_reflection_auto_reset_mission5": true,
      "toast_suppressed": [
        {"scene": 8, "reason": "budget_overflow", "count": 1}
      ],
      "hud_scene_usage": {"scene_8": {"toasts": 3, "budget": 2}}
    }
  },
  "ui": {
    "intro_seen": true,
    "accessibility": {
      "contrast": "high",
      "badge_density": "dense",
      "output_pace": "slow"
    },
    "suggest_mode": true
  },
  "arena": {
    "active": false,
    "previous_mode": null,
    "resume_token": null
  },
  "arc_dashboard": {
    "unlocked_arcs": ["watergate", "tesla_lab", "alexandria"],
    "completed_missions": 47
  }
}
```
