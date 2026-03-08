---
title: "QA-Log – Issue-Pack Durchlauf 61 (Ruf/Alien Watchpoints II)"
date: 2026-03-08
scope: "Ruf-Wording und Greys-Deckname in Runtime-Texten"
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
- Fahrplan: `internal/qa/plans/issue-pack-durchlauf-61-ruf-alien-watchpoints-ii.md`.

## Umsetzung in diesem Durchlauf

1. **Ausrüstungszugriff auf SSOT-Wording gehärtet**
   - `characters/ausruestung-cyberware.md`: Hinweistext bei den
     Tier-Lizenzen von „Rang oder Ruf" auf den formalen Pfad
     `ITI-Ruf (reputation.iti) + Lizenz-Tier` umgestellt.
   - Effekt: Keine implizite Drift mehr zwischen Fraktionssignalen und
     formaler Ausrüstungsfreigabe.

2. **Urban-Myth-Falschspur präzisiert**
   - `gameplay/kreative-generatoren-begegnungen.md`: W20-Eintrag
     `Greys` als `Greys (ITI-Deckname)` markiert.
   - Effekt: Frühe Lesart bleibt konsequent bei Incident-/Feldjargon statt
     bestätigter Speziesbehauptung.

3. **QA-Prozess fortgeschrieben**
   - `internal/qa/process/ruf-alien-statusmatrix.md`: Follow-up-Hinweis um
     Durchlauf 61 ergänzt.
   - `internal/qa/process/known-issues.md`: ZR-018-Notiz um Watchpoint-Lauf
     61 erweitert.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.

## Ergebnis / Anschluss

- ZR-018 bleibt abgeschlossen; Durchlauf 61 schließt zwei verbleibende
  Watchpoint-Wordingstellen und hält damit Ruf-/Mystery-SSOT auch in
  Generator- und Ausrüstungsrandtexten stabil.
