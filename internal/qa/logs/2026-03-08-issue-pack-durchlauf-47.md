---
title: "QA-Log – Issue-Pack Durchlauf 47"
date: 2026-03-08
scope: "Issue 2 Nachschärfung: obsolet gewordene Runtime-Komfortbefehle aus Spieldoku entfernen"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- Upload-Issue-Pack: `uploads/ZEITRISS_v7_save_load_issue_pack.md` (Issue 2).
- Fahrplan: `internal/qa/plans/issue-pack-durchlauf-47.md`.
- Review-Feedback: Runtime-Komfortbefehle sind für den realen Spielbetrieb obsolet.

## Umsetzung in diesem Durchlauf

1. **Chat-only Betriebsstandard verankert**
   - `README.md`: Runtime-only Auflistung entfernt; stattdessen klare
     chat-only-Formulierung mit HQ-`!save` + JSON-Paste (+ optional `Spiel laden`).

2. **WS-/Spielerdoku bereinigt**
   - `systems/gameflow/speicher-fortsetzung.md`: Runtime-Komforthinweis
     (`!load`, `!suspend`, `!resume`, `!autosave hq`) entfernt.
   - `core/spieler-handbuch.md`: OpenWebUI-Hinweis auf kanonischen
     Chatpfad fokussiert, ohne Runtime-Befehlskatalog.
   - `characters/hud-system.md`: Obsolete Runtime-Befehle aus der
     Befehlstabelle entfernt; `Spiel laden` als optionales Startsignal
     im JSON-Loadpfad geführt.

3. **Altverweis korrigiert**
   - `core/wuerfelmechanik.md`: veralteten `autosave hq`-Hinweis durch den
     geltenden HQ-`!save`-Standard ersetzt.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.

## Ergebnis / Anschluss

- Der dokumentierte Spielbetrieb ist wieder konsistent chat-native und
  frei von obsoleten Runtime-Komfortpfaden.
- ZR-017 bleibt offen für die großen Restblöcke (v7-SSOT-Härtung,
  Mixed-Split-Protokoll, Dedupe/Lineage, Px-Zustandsautomat, E2E-Fixtures).
