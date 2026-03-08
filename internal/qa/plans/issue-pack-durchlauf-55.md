---
title: "Issue-Pack Fahrplan – Durchlauf 55"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 55

Quelle: `uploads/ZEITRISS_v7_save_load_issue_pack.md` (WS-/OpenWebUI-Grenze nachschärfen: kein Repo-Pfad als KI-SL-Abhängigkeit).

## Ziel

1. Sicherstellen, dass WS-Dateien den Save-Kanon ohne Repo-Dateipfad-Abhängigkeit beschreiben.
2. Klarstellen, dass externe Schema-Dateien ausschließlich Tooling/Runtime außerhalb des Wissensspeichers sind.
3. KI-SL-Leittexte auf den sichtbaren Kanon (Masterprompt + 20 Wissensmodule) fokussieren.

## Scope dieses Durchlaufs

- `systems/gameflow/speicher-fortsetzung.md`
  - Schema-Abschnitt von Repo-Pfaden auf WS-Only-Kanon umstellen.
  - Klartextprofil als maßgebliche Struktur für KI-SL markieren.
- `core/sl-referenz.md`
  - Save-Abschnitt auf Kompakt-Profil im Wissensspeicher fokussieren.
  - Externe Schemas als Runtime-/Tooling-Hilfe außerhalb WS deklarieren.
- `internal/qa/process/known-issues.md`
  - ZR-017 um Durchlauf-55-Nachschärfung ergänzen.

## Exit-Kriterium

- WS-Texte implizieren keine Abhängigkeit auf Repo-Dateipfade für KI-SL-Laufzeit.
- Pflicht-Smoke (`bash scripts/smoke.sh`) läuft grün.
