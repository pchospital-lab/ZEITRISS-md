---
title: "QA-Log 2026-03-09 – Durchlauf 132 (Host-Anker/JSON-First + Debrief-Split-Angebot)"
status: "abgeschlossen"
run_id: "zr-021-d132"
---

# Kontext

Feedback auf Durchlauf 131: In der Praxis posten Gruppen im neuen Chat oft
mehrere Save-JSONs direkt hintereinander, ohne "Spiel laden". Erwartet wird,
dass der Merge sofort läuft und der zuerst gepostete Save den Session-Anker
setzt. Zusätzlich soll nach Debrief ein sichtbares Split-Angebot verfügbar sein,
um Gruppenwechsel sauber im HQ abzuwickeln.

# Umgesetzte Änderungen

1. **JSON-first-Dispatcher für reale Lobby-Praxis**
   - `systems/toolkit-gpt-spielleiter.md`: Load-Flow startet jetzt bei
     erkanntem Save-JSON (auch ohne `Spiel laden`); bei Mehrfach-JSON gilt
     explizit `first JSON sets session_anchor`.
   - `core/sl-referenz.md`: gleiche Regel als Runtime-Referenz ergänzt.

2. **Host-/Ankerlogik explizit als Reihenfolgeregel**
   - `meta/masterprompt_v6.md` und `core/spieler-handbuch.md` benennen den
     Praxisfall "mehrere JSONs in erster Nachricht" nun explizit mit
     chatreihenfolgebasierter Session-Anker-Setzung.

3. **Debrief-Split-Angebot als geordneter HQ-Schritt**
   - `systems/toolkit-gpt-spielleiter.md`: Im HQ-Workflow nach Debrief/Heimkehr
     einen kurzen Split-Angebot-Block ergänzt.
   - `meta/masterprompt_v6.md` und
     `systems/gameflow/speicher-fortsetzung.md`: Debrief→HQ→Split-Angebot als
     gewünschter Koop-Rhythmus ergänzt (ohne Auto-Weiterdruck ins Briefing).

# Ausgeführte Checks

1. `bash scripts/smoke.sh`

# Bewertung

Der praktische MMO-Loop ist jetzt klarer an der echten Nutzung ausgerichtet:
JSON-first-Merge im neuen Chat ohne Zusatzkommando, deterministische
Session-Anker-Setzung per Reihenfolge und expliziter Split-Pfad direkt nach
Debrief im HQ.
