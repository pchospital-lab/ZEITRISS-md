---
title: "Issue-Pack Fahrplan – Durchlauf 70 (Abschlusscheck v7 + Linkhygiene)"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 70 (Abschlusscheck v7 + Linkhygiene)

Quelle: Anschlusslauf auf `uploads/ZEITRISS_ruf_alien_review.md` mit Fokus auf
abschließende Generalprüfung (v7-SSOT, Linkhygiene, Wissensspeicher-Grenzen).

## Ziel

1. Pflicht-Smoke inkl. v7-Guards erneut vollständig verifizieren.
2. Wissensspeicher-interne Linkhygiene prüfen und Außenverweise aus WS/Masterprompt entfernen.
3. Prozesspfad (Plan/Log/Statusmatrix/Known-Issues) für den Abschlusslauf ergänzen.

## Scope dieses Durchlaufs

- Wissensspeicher-Texte:
  - `core/sl-referenz.md`
  - `core/spieler-handbuch.md`
  - `gameplay/kampagnenstruktur.md`
  - `systems/gameflow/speicher-fortsetzung.md`
- QA-Prozess:
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-70-abschlusscheck-v7-links.md`
  - `internal/qa/process/ruf-alien-statusmatrix.md`
  - `internal/qa/process/known-issues.md`

## Exit-Kriterien

- `bash scripts/smoke.sh` läuft grün.
- Keine lokalen WS/Masterprompt-Links zeigen auf Nicht-WS-Dateien.
- Durchlauf 70 ist in Statusmatrix und Known-Issues (ZR-018) referenziert.
