---
title: "QA-Log – Issue-Pack Durchlauf 60 (Ruf/Alien Restdrift)"
date: 2026-03-08
scope: "Restdrift bei Alien-Ikonographie in Spielerbeispielen"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- Ursprungsreview: `uploads/ZEITRISS_ruf_alien_review.md`.
- Vorläufe:
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-57-ruf-alien.md`
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-58-ruf-alien-followup.md`
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-59-ruf-alien-watchpoints.md`
- Fahrplan: `internal/qa/plans/issue-pack-durchlauf-60-ruf-alien-restdrift.md`.

## Umsetzung in diesem Durchlauf

1. **Spielbeispiel in Kampagnenstruktur nachgeschärft**
   - `gameplay/kampagnenstruktur.md`: In der Beispiel-Episode „TITAN DRIFT"
     wurde die Formulierung von `Alien-Raptoren` auf
     `scheinbar "Alien"-Raptoren (zeitversetzte Fauna)` geändert.
   - Effekt: Früher Feldread bleibt erhalten, ohne einen bestätigten
     Spezies-Fakt im Onboarding-/Beispielpfad zu setzen.

2. **QA-Prozess fortgeschrieben**
   - `internal/qa/process/ruf-alien-statusmatrix.md`: Follow-up-Hinweis um
     Durchlauf 60 ergänzt.
   - `internal/qa/process/known-issues.md`: ZR-018-Notiz um den Restdrift-Lauf
     erweitert.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.

## Ergebnis / Anschluss

- ZR-018 bleibt abgeschlossen; Durchlauf 60 dokumentiert die letzte
  textliche Restdrift im Beispielpfad und hält den Mystery-Contract auch in
  Missionsbeispielen konsistent.
