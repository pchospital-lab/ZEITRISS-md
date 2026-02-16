# 2026-02-16 — OpenWebUI Testrun (Post-Spieler-Handbuch-Refactor)

**Tester:** Altair (automatisiert via OpenWebUI API)
**Plattform:** OpenWebUI 0.8.1 + OpenRouter
**Modell:** anthropic/claude-sonnet-4 (Preset: ZEITRISS v4.2.6 – Local Uncut)
**Wissensspeicher:** 20 Dateien (core/spieler-handbuch.md als Slot 1, README entfernt)
**Anlass:** Validierung nach README→Spieler-Handbuch-Refactor

## Zusammenfassung

5 Testruns durchgeführt, davon 1 Vergleichsrun auf Opus 4.6.

### Run 1: Klassischer Start (Sonnet vs. Opus)

**Sonnet (4.574 Zeichen):**
- ✅ Einleitung paraphrasiert (nicht wörtlich zitiert)
- ✅ Vollständiger Charakterbogen mit konkreten Zahlen
- ✅ HUD-Zeile korrekt formatiert
- ✅ Guter Noir-Ton, Szene 1 immersiv
- ⚠️ Erfindet "Zeitkristall-Reserven" (nicht im Regelwerk)
- ⚠️ Health/Stress-Berechnung eigene Formeln statt Regelwerk
- ⚠️ Nennt ITI "Internationaler Zeitforschungsrat" (falsch)
- ⚠️ Attribute korrekt übernommen (18 Punkte)

**Opus 4.6 (2.199 Zeichen):**
- ✅ Atmosphärisch dichter, filmischer Einstieg
- ✅ Besserer Noir-Ton ("Die Kälte trifft dich zuerst...")
- ✅ HUD-Zeile vorhanden
- ❌ Erfindet "TEMP" als Organisation statt ITI
- ⚠️ Kürzerer Output, keine Charaktererschaffung
- ⚠️ Stress 0/5 statt korrektem Maxwert

### Run 2: Mid-Game Mission 5 Boss-Gate (Sonnet, 2.866 Zeichen)

- ✅ Save/Load korrekt — Kodex-Recap mit Missionshistorie
- ✅ !sf off wird anerkannt, Self-Reflection deaktiviert
- ✅ Boss-Foreshadowing stark: "Der Architekt" als übergreifender Antagonist
- ✅ HUD korrekt: EP 1 · MS 5 · SC 0/12 · Px 3/5
- ✅ Foreshadow-Pattern erkannt, Boss-Gate-Sequenz eingeleitet
- ✅ Atmosphärisch bester Run — Director Kellerman, rote Verwerfungslinien
- ⚠️ Nur Briefing-Szene, keine Folge-Szenen (API-Output-Limit)
- ⚠️ Keine FS 0/4 Anzeige im HUD

### Run 3: Rift-Op Mothman + Chronopolis (Sonnet, 1.670 Zeichen)

- ✅ Save korrekt geladen, Rift-Seeds aus arc_dashboard erkannt
- ✅ Chronopolis-Zugang Level 12 korrekt validiert
- ✅ HQ-Atmosphäre gut (Cafeteria, Agenten verschiedener Epochen)
- ✅ RS-017 Mothman korrekt referenziert
- ⚠️ Erfindet "silberne Augen und Chronopolis-Tattoo" (nicht im Regelwerk)
- ⚠️ Rift-Op noch nicht gestartet (nur HQ-Szene, API-Limit)
- ⚠️ Kein CASE/HOOK/STAGE Overlay für Rift

### Run 4: PvP Arena (Sonnet, 1.652 Zeichen)

- ✅ Arena-Setup mit Tier, Gebühr und Loadout-Budget
- ✅ Save korrekt geladen
- ⚠️ Chronopolis-Zugang bei Level 8 angezeigt — Regelwerk sagt Level 10+ ❌
- ⚠️ Arena-Werte (Gebühr 800 CU, Budget 2400, Payout 1600) sind erfunden
- ⚠️ Kein Arena-Kampf durchgespielt (nur Setup)

### Run 5: Echtes Gruppenspiel mit Save-Handoff (Sonnet)

**Run 5a — Gruppenstart (3.340 Zeichen):**
- ✅ Zwei Charaktere korrekt erstellt (PHANTOM + CIPHER)
- ✅ HUD zeigt Squad-Anzeige
- ✅ Briefing szenisch mit Operationsleiter
- ⚠️ Attribute viel zu hoch (STR 8, GES 12, INT 13 — Max ist ~5 bei Start)
- ⚠️ Health 40/40, Stress 0/35 — falsche Werte
- ⚠️ Nur Szene 1 (Briefing), kein Save-Output

**Run 5b — Handoff: Spieler B übernimmt (1.876 Zeichen):**
- ✅ Save korrekt geladen, CIPHER als Spieler erkannt
- ✅ PHANTOM wird als NPC-Partner gesteuert
- ✅ Squad-Radio-Kommunikation funktioniert
- ✅ Szene 5 mit korrektem HUD (SC 5/12)
- ✅ Rückblick aus Save-Logs korrekt paraphrasiert
- ✅ Taktische Optionen sinnvoll (Lichtausfall/Feueralarm/Türschloss)
- ✅ Zeitfenster-Druck spürbar

## Gesamtbewertung

### Funktioniert ✅
- HUD-Format konsistent über alle Runs
- Save/Load mit v6-Schema wird erkannt
- Noir-Atmosphäre durchgehend gut
- Würfelproben korrekt notiert
- 3 Optionen + Freie Aktion eingehalten
- Kodex meldet sich kontextgerecht
- Gruppen-Handoff via Save funktioniert
- Spieler-Handbuch-Refactor hat keine Regression verursacht

### Verbesserungsbedarf ⚠️
- RAG-Retrieval nutzt Regelwerk nicht vollständig (erfindet Werte)
- Attribut-Ranges werden nicht eingehalten (zu hohe Startwerte bei Gruppe)
- Arena- und Ökonomie-Werte oft erfunden statt aus Regelwerk
- Chronopolis-Unlock-Level inkonsistent
- Einleitung nicht wörtlich zitiert (Masterprompt verlangt es)
- API-Single-Shot zu kurz für komplette Missionen

### Empfehlung
- Für echtes Spielen: Browser-Chat (Multi-Turn), nicht API-Single-Shot
- Opus 4.6 liefert bessere Atmosphäre, Sonnet bessere Regeltreue
- Regelwerk ist solide — die Schwäche liegt im RAG der Plattform
