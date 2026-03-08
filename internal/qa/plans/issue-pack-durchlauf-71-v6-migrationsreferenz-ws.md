---
title: "Issue-Pack Fahrplan – Durchlauf 71 (V6-Migrationsreferenz im Wissensspeicher)"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 71 (V6-Migrationsreferenz im Wissensspeicher)

Quelle: Follow-up auf den Abschlusscheck, mit Fokus auf klare KI-SL-Migrationsfähigkeit ohne externe Repo-Dateien.

## Ziel

1. V6→V7-Migrationsreferenz direkt im Wissensspeicher verankern.
2. SL-Referenz auf diese interne WS-Quelle umstellen.
3. Prozessspur (Log + Statusmatrix + Known-Issues) ergänzen.

## Scope dieses Durchlaufs

- `systems/gameflow/speicher-fortsetzung.md`
- `core/sl-referenz.md`
- `internal/qa/logs/2026-03-08-issue-pack-durchlauf-71-v6-migrationsreferenz-ws.md`
- `internal/qa/process/ruf-alien-statusmatrix.md`
- `internal/qa/process/known-issues.md`

## Exit-Kriterien

- `bash scripts/smoke.sh` bleibt grün.
- V6→V7-Migrationsbeispiel ist im WS auffindbar und aus der SL-Referenz verlinkt.
- Durchlauf 71 ist in Statusmatrix und ZR-018-Prozesspfad referenziert.
