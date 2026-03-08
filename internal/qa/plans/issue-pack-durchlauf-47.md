---
title: "Issue-Pack Fahrplan – Durchlauf 47"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 47

Quelle: `uploads/ZEITRISS_v7_save_load_issue_pack.md` (Issue 2, Nachschärfung nach Review-Feedback).

## Ziel

Den Save/Load-Betriebsstandard strikt auf den realen Chatbetrieb festziehen:
obsolet gewordene Runtime-Komfortbefehle (`load/suspend/resume/autosave hq`)
werden aus Spieler-/WS-Dokumenten entfernt, statt als optionale Befehle geführt.

## Scope dieses Durchlaufs

- `README.md`: Betriebsstandard als chat-only Pfad formulieren.
- `systems/gameflow/speicher-fortsetzung.md`: Runtime-Komforthinweis entfernen.
- `core/spieler-handbuch.md`: OpenWebUI-Hinweis auf kanonischen Chatpfad
  fokussieren, ohne Runtime-Befehlsliste.
- `characters/hud-system.md`: Befehlstabelle von obsoleten Runtime-Befehlen
  bereinigen; nur kanonischen Load-Pfad führen.
- `core/wuerfelmechanik.md`: veralteten `autosave hq`-Verweis auf
  HQ-DeepSave-Standard (`!save`) umstellen.
- Pflicht-Smoke als Regression-Gate ausführen.

## Exit-Kriterium

- In den spielrelevanten Modulen bleibt kein aktiver Bedienpfad für
  `load/suspend/resume/autosave hq` übrig.
- Save/Load ist einheitlich als HQ-`!save` + JSON-Paste (optional `Spiel laden`)
  beschrieben.
- Pflicht-Smoke bleibt grün.
