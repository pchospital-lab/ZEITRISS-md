---
title: "QA-Log – Issue-Pack Durchlauf 42"
date: 2026-03-07
scope: "Klarstellung Mid-Episode-Split (5er→3/2) ohne Branch-Protokoll"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- Maintainer-Rückfrage im Anschluss an Durchlauf 41 (5er-Gruppe trennt sich mitten in der Episode in 3/2).
- Fahrplan: `internal/qa/plans/issue-pack-durchlauf-42.md`

## Umsetzung in diesem Durchlauf

1. **Klarfall im Spielerpfad ergänzt**
   - `README.md`: 5er→3/2-Szenario explizit ergänzt.
   - Aussage: 2er-Gruppe darf separat spielen, bleibt aber Side-Run; kanonisch bleibt der Host-Run.

2. **Kanon-Regel in Prompt/SL-Sicht nachgezogen**
   - `meta/masterprompt_v6.md`: Mid-Episode-Trennung als nicht-kanonischer Side-Run präzisiert.
   - `core/sl-referenz.md`: gleiche Regel im Befehls-/Betriebskontext ergänzt.

3. **Save-System-SSOT konkretisiert**
   - `systems/gameflow/speicher-fortsetzung.md`: neuer Unterabschnitt
     „Klarstellung: Mid-Episode-Trennung (5er → 3/2)" mit 4-Punkte-Regel:
     Host-Fortschritt kanonisch, Side-Run erlaubt, Rejoin erst im HQ nach
     Episodenende, kein automatischer Episoden-Sprung für Solist:innen.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
