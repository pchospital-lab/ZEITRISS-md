---
title: "QA-Log – Issue-Pack Durchlauf 62 (Greys/Feindbild-Schärfung)"
date: 2026-03-08
scope: "Grey-Logik und Gegnerklarheit in Runtime-Texten"
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
- Fahrplan: `internal/qa/plans/issue-pack-durchlauf-62-ruf-alien-greys-feindbild.md`.
- Reviewer-Feedback: Greys nicht als Nano-Anzug-Only und nicht nur ITI-Deckname;
  klare Gegnerfraktionen für den Spielkern sichtbar halten.

## Umsetzung in diesem Durchlauf

1. **Urban-Myth-Eintrag fachlich korrigiert**
   - `gameplay/kreative-generatoren-begegnungen.md`: W20-Eintrag 13 von
     `Greys (ITI-Deckname) - Nano-Skin-Anzüge ...` auf
     `Greys - posthumane Fernzukunfts-Menschen (jenseits T-/N-Stufe), oft Einsatzteams externer Zeitmanipulator-Fraktionen` geändert.
   - Effekt: Kein künstlicher ITI-Only-Read, kein Nano-Anzug-Only-Read.

2. **Kampagnenübersicht auf Gegnerklarheit nachgezogen**
   - `gameplay/kampagnenuebersicht.md`: Mystery-Contract- und
     Beispielfraktions-Passagen so geschärft, dass
     - Greys als Feldbegriff mit posthumanem Ursprung lesbar bleiben,
     - aber klare Gegenspieleroptionen über externe Zeitmanipulator-Fraktionen
       explizit benannt werden.
   - Effekt: Mystery bleibt erhalten, Spielkern „ITI vs. Zeitmanipulatoren"
     wird klarer.

3. **QA-Prozess fortgeschrieben**
   - `internal/qa/process/ruf-alien-statusmatrix.md`: Follow-up-Hinweis um
     Durchlauf 62 ergänzt.
   - `internal/qa/process/known-issues.md`: ZR-018-Notiz um Durchlauf 62
     erweitert.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.

## Ergebnis / Anschluss

- ZR-018 bleibt abgeschlossen; Durchlauf 62 korrigiert die inhaltliche
  Überverengung aus Durchlauf 61 und stabilisiert gleichzeitig die
  Gegnerklarheit für spielbaren Konflikt.
