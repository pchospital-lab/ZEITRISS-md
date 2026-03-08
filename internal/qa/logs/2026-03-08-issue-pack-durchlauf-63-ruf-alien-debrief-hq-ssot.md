---
title: "QA-Log – Issue-Pack Durchlauf 63 (Debrief/HQ-SSOT-Klarzug)"
date: 2026-03-08
scope: "Debrief-Label und HQ-Freigabelogik in Kampagnenstruktur"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- Ursprungsreview: `uploads/ZEITRISS_ruf_alien_review.md`.
- Vorläufe:
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-57-ruf-alien.md`
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-58-ruf-alien-followup.md`
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-59-ruf-alien-watchpoints.md`
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-60-ruf-alien-restdrift.md`
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-61-ruf-alien-watchpoints-ii.md`
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-62-ruf-alien-greys-feindbild.md`
- Fahrplan: `internal/qa/plans/issue-pack-durchlauf-63-ruf-alien-debrief-hq-ssot.md`.

## Umsetzung in diesem Durchlauf

1. **Debrief-Begriffe im Ablauf vereinheitlicht**
   - `gameplay/kampagnenstruktur.md`: Missions-Abschlussschritt 5 auf
     `ITI-Ruf-Update` gehärtet; Fraktionssignale als ergänzende Information
     markiert.
   - Flowchart-/Tabellen-/Kurzcheck-Passagen von generischem `Ruf` auf den
     kanonischen Debrief-Begriff gezogen.

2. **HQ- und Lizenzzugang eindeutig getrennt**
   - Gleiche Datei: Abschnitt zu höheren Ausbaustufen präzisiert.
   - Ergebnis:
     - Fraktionsruf bleibt politisch/narrativ (Beziehungen, Preise, Zugang,
       Misstrauen).
     - Formale ITI-Zugänge und Tier-Freischaltungen laufen über
       `reputation.iti`.

3. **QA-Anschluss dokumentiert**
   - `internal/qa/process/ruf-alien-statusmatrix.md` um Durchlauf 63 ergänzt.
   - `internal/qa/process/known-issues.md` (ZR-018) mit Referenz auf
     Durchlauf 63 fortgeschrieben.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.

## Ergebnis / Anschluss

- ZR-018 bleibt abgeschlossen.
- Durchlauf 63 schließt verbliebene Debrief/HQ-Wording-Drift in
  `gameplay/kampagnenstruktur.md` und hält den Anschlussfahrplan für
  Folge-QA nachvollziehbar.
