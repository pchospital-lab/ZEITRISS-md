---
title: "Issue-Pack Fahrplan – Durchlauf 61 (Ruf/Alien Watchpoints II)"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 61 (Ruf/Alien Watchpoints II)

Quelle: Anschlusslauf auf `uploads/ZEITRISS_ruf_alien_review.md` nach
Durchlauf 60.

## Ziel

1. Verbleibende Ruf-Wording-Restdrift in Ausrüstungstexten auf
   `ITI-Ruf + Lizenz-Tier` härten.
2. Falschspur-Generatoren konsistent halten, damit `Greys` nie als gesicherte
   Spezies, sondern als ITI-Deckname gelesen werden.
3. QA-Anschluss in den Prozessdokumenten fortschreiben.

## Scope dieses Durchlaufs

- Inhaltliche Korrekturen in:
  - `characters/ausruestung-cyberware.md`
  - `gameplay/kreative-generatoren-begegnungen.md`
- QA-Anschluss:
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-61-ruf-alien-watchpoints-ii.md`
  - `internal/qa/process/ruf-alien-statusmatrix.md`
  - `internal/qa/process/known-issues.md`

## Exit-Kriterien

- Ausrüstungsfreigaben referenzieren formal `ITI-Ruf` und `Lizenz-Tier` statt
  unpräziser `Rang oder Ruf`-Formulierung.
- Urban-Myth-Generator markiert `Greys` explizit als ITI-Deckname/Falschspur.
- ZR-018 bleibt als abgeschlossen markiert; Durchlauf 61 ist im
  Prozessprotokoll nachvollziehbar.
- Pflicht-Smoke (`bash scripts/smoke.sh`) bleibt grün.
