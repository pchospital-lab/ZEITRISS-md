---
title: "Issue-Pack Fahrplan – Durchlauf 59 (Ruf/Alien Watchpoints)"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 59 (Ruf/Alien Watchpoints)

Quelle: Anschlusslauf auf `uploads/ZEITRISS_ruf_alien_review.md` nach
Durchläufen 57-58.

## Ziel

1. Restdrift bei Ruf-Begriffen in spielnahen Übersichts-/Referenztexten
   schließen (`ITI-Ruf` statt unklarer Sammelbegriffe).
2. Mystery-Tonlage in Kernlore absichern, damit „scheinbar fremde" Spuren
   nicht als harte Alien-Fakten gelesen werden.
3. QA-Anschlussdokumente fortschreiben, damit Folge-Durchläufe klare
   Watchpoints haben.

## Scope dieses Durchlaufs

- Inhaltliche Korrekturen in:
  - `gameplay/kampagnenuebersicht.md`
  - `core/sl-referenz.md`
  - `core/zeitriss-core.md`
- QA-Anschluss:
  - `internal/qa/process/ruf-alien-statusmatrix.md`
  - `internal/qa/process/known-issues.md`
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-59-ruf-alien-watchpoints.md`

## Exit-Kriterien

- Keine unpräzisen „Rufpunkte"-Labels mehr in den bearbeiteten
  spielrelevanten Referenzstellen; stattdessen klare Trennung
  `ITI-Ruf`/Fraktionssignal.
- Kampagnenübersicht benennt Stadtzugänge entlang der SSOT-Linie
  (`ITI-Rang/ITI-Ruf` für formalen Pfad, Fraktionsruf als politischer Modifikator).
- Loretext in `core/zeitriss-core.md` vermeidet harte Alien-Fakt-Formulierungen
  im frühen/neutralen Lesepfad.
- Pflicht-Smoke (`bash scripts/smoke.sh`) bleibt grün.
