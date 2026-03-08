---
title: "Issue-Pack Fahrplan – Durchlauf 60 (Ruf/Alien Restdrift)"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 60 (Ruf/Alien Restdrift)

Quelle: Anschlusslauf auf `uploads/ZEITRISS_ruf_alien_review.md` nach
Durchlauf 59.

## Ziel

1. Verbleibende Frühlese-Drift bei scheinbar harten Alien-Begriffen in
   Spielerbeispielen glätten.
2. Mystery-Contract im Spieltext halten: erst Aktenlage/Feldread, dann
   belastbare Auflösung.
3. QA-Anschluss in den Prozessdokumenten dokumentieren.

## Scope dieses Durchlaufs

- Inhaltliche Korrektur in:
  - `gameplay/kampagnenstruktur.md`
- QA-Anschluss:
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-60-ruf-alien-restdrift.md`
  - `internal/qa/process/ruf-alien-statusmatrix.md`
  - `internal/qa/process/known-issues.md`

## Exit-Kriterien

- Beispieltexte in `gameplay/kampagnenstruktur.md` formulieren scheinbare
  Alien-Spuren als Feldread/Ikonographie statt als bestätigten Fakt.
- ZR-018 bleibt als abgeschlossen markiert; die Restdrift ist im
  Prozessprotokoll als weiterer Watchpoint-Lauf nachvollziehbar.
- Pflicht-Smoke (`bash scripts/smoke.sh`) bleibt grün.
