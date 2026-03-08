---
title: "QA-Log – Issue-Pack Durchlauf 64 (Chronopolis-Schlauchlevel + Level-10-Klarzug)"
date: 2026-03-08
scope: "Chronopolis-Wegführung als Schlauchlevel und Level-10-SSOT-Klarstellung"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- Ursprungsreview: `uploads/ZEITRISS_ruf_alien_review.md`.
- Zusatzhinweis: Maintainer-Feedback zur Chronopolis-Wegführung
  (fester Schleusenlauf statt frei wirkender Hub-Geometrie).
- Vorlauf:
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-63-ruf-alien-debrief-hq-ssot.md`
- Fahrplan:
  - `internal/qa/plans/issue-pack-durchlauf-64-ruf-alien-chronopolis-schlauchlevel.md`

## Umsetzung in diesem Durchlauf

1. **Level-10-Drift bereinigt (`core/zeitriss-core.md`)**
   - Meilensteintext auf Verantwortung/Chronopolis-Schlüssel fokussiert,
     ohne implizite Shop-Freigabe über Level.
   - Reputation-Abschnitt ergänzt: formale Ausrüstungsfreigaben bleiben an
     `ITI-Ruf + Lizenz-Tier` gebunden.

2. **Schlauchlevel-SSOT in Referenz verankert (`core/sl-referenz.md`)**
   - Level-10-Gate und Chronopolis-HQ-Abschnitt um feste Wegführung ergänzt:
     Eingangsschleuse → Ringlauf → gegenüberliegende Ausgangsschleuse.
   - Klarstellung, dass diese Wegführung bewusst nicht frei verzweigt ist.

3. **Kampagnenmodul auf Schlauchroute gehärtet (`gameplay/kampagnenstruktur.md`)**
   - Chronopolis-Pitch um explizite Schlauchroute erweitert.
   - Schleusenprotokoll um Ring-Transit-Logik (Entry/Traverse/Exit) ergänzt.

4. **Prozessanschluss fortgeschrieben**
   - `internal/qa/process/ruf-alien-statusmatrix.md` um Durchlauf 64 ergänzt.
   - `internal/qa/process/known-issues.md` (ZR-018) mit Durchlauf-64-Verweis
     aktualisiert.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.

## Ergebnis / Anschluss

- ZR-018 bleibt abgeschlossen.
- Der Chronopolis-Zugang ist jetzt in Core-/Referenz-/Kampagnenpfad
  konsistent als Schlauchlevel beschrieben und für Folge-QA klar verankert.
