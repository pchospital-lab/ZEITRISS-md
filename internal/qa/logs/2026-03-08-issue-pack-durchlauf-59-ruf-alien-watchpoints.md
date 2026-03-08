---
title: "QA-Log – Issue-Pack Durchlauf 59 (Ruf/Alien Watchpoints)"
date: 2026-03-08
scope: "Ruf-Begriffe + Mystery-Tonlage in Referenz-/Kerntexten"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- Ursprungsreview: `uploads/ZEITRISS_ruf_alien_review.md`.
- Vorläufe:
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-57-ruf-alien.md`
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-58-ruf-alien-followup.md`
- Fahrplan: `internal/qa/plans/issue-pack-durchlauf-59-ruf-alien-watchpoints.md`.

## Umsetzung in diesem Durchlauf

1. **Rufbegriff in Kampagnenübersicht präzisiert**
   - `gameplay/kampagnenuebersicht.md`: Stadt-/Händlerabschnitt auf
     SSOT-Sprache gezogen.
   - Formale Progression jetzt explizit als `ITI-Rang/ITI-Ruf` benannt,
     Fraktionsruf als politischer Modifikator (Preise/Zugang/Misstrauen).

2. **Referenz-Cheat-Sheet begrifflich gehärtet**
   - `core/sl-referenz.md`: KPI-Zeilen „Auswertung" von
     `Rufpunkte, Ressourcen` auf `ITI-Ruf, Fraktionssignal, Ressourcen`
     umgestellt (beide Vorkommen).

3. **Mystery-Tonlage im Core-Text stabilisiert**
   - `core/zeitriss-core.md`: Absatz zu kleineren Akteuren so
     umformuliert, dass scheinbar fremde Einflüsse als Akten-/Spur-Lage
     geführt werden, bis Verifikation vorliegt.
   - Klar benannt: Standardread über fehlklassifizierte Zeitphänomene,
     posthumane Operationen oder Falschbilder.

4. **QA-Prozess fortgeschrieben**
   - `internal/qa/process/ruf-alien-statusmatrix.md`: Hinweis auf
     Durchlauf 59 ergänzt.
   - `internal/qa/process/known-issues.md`: ZR-018-Notiz um den
     Watchpoint-Lauf erweitert.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.

## Ergebnis / Anschluss

- ZR-018 bleibt abgeschlossen; Durchlauf 59 schließt begriffliche
  Restdrift in Referenzstellen und stabilisiert den Mystery-Contract in
  Kernlore-Texten.
- Folge-Durchläufe halten die bestehenden Watchpoints weiter aktiv
  (Debrief-Label, Rangnamen-Konsistenz, Tier-V-Rückfall, Onboarding-Ton).
