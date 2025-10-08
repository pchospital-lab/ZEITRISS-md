---
title: "MyGPT Acceptance Smoke"
version: 1.2.0
tags: [testing]
---

# MyGPT Acceptance Smoke

> **Hinweis:** Der standardisierte Beta-GPT-Testprompt verpflichtet sich, jeden
> Punkt dieser Checkliste automatisch abzudecken. Dokumentiere Abweichungen im
> QA-Log und im Fahrplan unter den Deepcheck-Aufgaben.

## Dispatcher-Starts & Speicherpfade
1. `Spiel starten (solo klassisch)` → Erschaffung → HQ-Intro → Briefing → SC 1
2. `Spiel starten (solo schnell)` → Rolle → Defaults → Briefing/SC 1
3. `Spiel starten (npc-team 3 schnell)` → Autogen-NSCs (3) → Briefing
4. `Spiel starten (npc-team 5)` → Fehlertext „Teamgröße 0–4 …“
5. `Spiel starten (gruppe schnell)` → 2 Saves + 1 Rolle → Briefing
6. `Spiel starten (gruppe 3)` → Fehlertext „Bei *gruppe* keine Zahl …“
7. `Spiel laden` + kompatibler Save → Kodex-Recap-Overlay → HQ/Briefing (keine Startfrage)
8. `Speichern` während Mission → Blocker „Speichern nur im HQ …“
9. Gear-Alias: „Multi-Tool-Armband ausrüsten“ → still → „Multi-Tool-Handschuh“
10. „Px 5“ triggern → Hinweis: Seeds erzeugt, spielbar nach Episodenende, Reset danach

## Boss-Gates & HUD-Badges
11. `!helper boss` nach Mission 4 → Foreshadow-Liste zeigt Szene 5/10. HUD-Toast
    `Boss blockiert – Foreshadow 0/2`, bis Hinweise erfüllt sind.
12. Mission 5 starten → HUD blendet Mini-Boss-DR (`Boss-Encounter in Szene 10`)
    und Badge `SF-OFF` ein; Foreshadow-Schritte zählen im HUD hoch.

## Psi-Heat & Ressourcen-Reset
13. Psi-Charakter in Konflikt schicken, Psi-Aktion nutzen → HUD meldet
    `Psi-Heat +1`; nach Konflikt springt Psi-Heat automatisch auf 0. HQ-Transfer
    setzt SYS/Stress/Psi-Heat zurück.

## QA-Abgleich 2025-03-23
- **Boss-Gates & HUD-Badges:** `scene_overlay()` blendet bei deaktivierter
  Selbstreflexion das Badge `SF-OFF` ein und führt Foreshadow-Zähler mit, während
  `assert_foreshadow()` in Präzisionsläufen Warnungen ausgibt; validiert über
  `GM_STYLE=precision node tools/test_foreshadow.js` sowie das HUD-Skript.
- **Psi-Heat-Reset:** `migrate_save()` und `hydrate_state()` setzen Psi-Heat in
  Konflikt- und HQ-Transfers deterministisch zurück und verhindern Speichervorgänge
  mit Restwärme.
- **Log-Verweis:** Vollständiges Prüfprotokoll im QA-Log vom 2025-03-19.
