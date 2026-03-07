---
title: "ZR-016 Statusmatrix – Externer Codex-Issue-Pack"
version: 0.2.0
tags: [qa, process]
---

# ZR-016 Statusmatrix – Externer Codex-Issue-Pack

Ziel dieser Matrix: schnelle Anschlussfähigkeit nach 36+ Durchläufen, ohne
lange Einzelauflistungen in `known-issues.md`.

## Legende

- **abgeschlossen:** Umsetzungsdurchlauf dokumentiert und Pflichtcheck grün.
- **abgeschlossen (verifiziert):** Umsetzungsdurchlauf dokumentiert, Pflichtcheck
  grün und Status in Known-Issues/Fahrplan synchron nachgeführt.

## Issue-Status (Pack 1–13)

| Issue | Titel (Kurzform) | Status | Letzte Evidenz-Durchläufe | Primäre Evidenz |
| --- | --- | --- | --- | --- |
| 1 | Save-Schema v7 als einzige Wahrheit | abgeschlossen (verifiziert) | 34–36, 38 | `internal/qa/logs/2026-03-07-issue-pack-durchlauf-34.md`, `internal/qa/logs/2026-03-07-issue-pack-durchlauf-35.md`, `internal/qa/logs/2026-03-07-issue-pack-durchlauf-36.md`, `internal/qa/logs/2026-03-07-issue-pack-durchlauf-38.md` |
| 2 | Wallet-/Ökonomie-Modell kanonisieren | abgeschlossen | 03–04, 15 | `internal/qa/logs/2026-03-06-issue-pack-durchlauf-03.md`, `internal/qa/logs/2026-03-06-issue-pack-durchlauf-04.md`, `internal/qa/logs/2026-03-06-issue-pack-durchlauf-15.md` |
| 3 | Würfelkanon auf eine Regel | abgeschlossen | 01 | `internal/qa/logs/2026-03-06-issue-pack-durchlauf-01.md` |
| 4 | Px/Cluster/Arena entkoppeln | abgeschlossen | 02 | `internal/qa/logs/2026-03-06-issue-pack-durchlauf-02.md` |
| 5 | Versionen/Ränge/Compliance-Reste | abgeschlossen | 05, 33 | `internal/qa/logs/2026-03-06-issue-pack-durchlauf-05.md`, `internal/qa/logs/2026-03-07-issue-pack-durchlauf-33.md` |
| 6 | Drift-Tests gegen SSOT-Drift | abgeschlossen (verifiziert) | 04, 06, 34–35, 38 | `internal/qa/logs/2026-03-06-issue-pack-durchlauf-04.md`, `internal/qa/logs/2026-03-06-issue-pack-durchlauf-06.md`, `internal/qa/logs/2026-03-07-issue-pack-durchlauf-34.md`, `internal/qa/logs/2026-03-07-issue-pack-durchlauf-35.md`, `internal/qa/logs/2026-03-07-issue-pack-durchlauf-38.md` |
| 7 | Runtime-Kanon von Autorenessay trennen | abgeschlossen | 21–22 | `internal/qa/logs/2026-03-07-issue-pack-durchlauf-21.md`, `internal/qa/logs/2026-03-07-issue-pack-durchlauf-22.md` |
| 8 | Ton-Bibel Core/Rift/Mythic | abgeschlossen | 18–20 | `internal/qa/logs/2026-03-07-issue-pack-durchlauf-18.md`, `internal/qa/logs/2026-03-07-issue-pack-durchlauf-19.md`, `internal/qa/logs/2026-03-07-issue-pack-durchlauf-20.md` |
| 9 | Psi optional sauber normalisieren | abgeschlossen | 09–10 | `internal/qa/logs/2026-03-06-issue-pack-durchlauf-09.md`, `internal/qa/logs/2026-03-06-issue-pack-durchlauf-10.md` |
| 10 | Chronopolis-Logik präzisieren | abgeschlossen | 13–14 | `internal/qa/logs/2026-03-06-issue-pack-durchlauf-13.md`, `internal/qa/logs/2026-03-06-issue-pack-durchlauf-14.md` |
| 11 | Pacing-/Token-Budget als Feature | abgeschlossen | 07 | `internal/qa/logs/2026-03-06-issue-pack-durchlauf-07.md` |
| 12 | Meta-/Modellbegriffe aus Runtime entfernen | abgeschlossen | 12, 22 | `internal/qa/logs/2026-03-06-issue-pack-durchlauf-12.md`, `internal/qa/logs/2026-03-07-issue-pack-durchlauf-22.md` |
| 13 | Item-/Ausrüstungs-Registry normalisieren | abgeschlossen | 16–17 | `internal/qa/logs/2026-03-06-issue-pack-durchlauf-16.md`, `internal/qa/logs/2026-03-06-issue-pack-durchlauf-17.md` |

## Anschlussfähiger Next Step

1. **ZR-016 ist formal geschlossen:** Folgearbeit bei neuen Funden als neue
   Known-Issue-ID erfassen (statt ZR-016 weiter zu überladen).
2. **Bei Runtime-Änderungen mit Bezug auf Issue 1–13:** neues Ticket anlegen,
   Plan/Log mit neuer Durchlaufnummer führen und Matrix nur am betroffenen
   Issue als Re-Validierung ergänzen.
