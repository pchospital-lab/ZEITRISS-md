---
title: "QA-Log – Issue-Pack Durchlauf 57 (Ruf/Alien)"
date: 2026-03-08
scope: "SSOT-Nachschärfung Ruf/Tier + Alien/Mystery-Onboarding"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- Upload-Issue-Pack: `uploads/ZEITRISS_ruf_alien_review.md`.
- Fahrplan: `internal/qa/plans/issue-pack-durchlauf-57-ruf-alien.md`.

## Umsetzung in diesem Durchlauf

1. **Ruf-/Tier-SSOT vereinheitlicht**
   - `characters/charaktererschaffung-grundlagen.md` auf klare Trennung
     `reputation.iti` (operativ) vs. `reputation.factions.*` (narrativ) umgestellt.
   - Deterministische ITI-Ruf-Progression (M1/M5/M10/M15/M20) als Standardpfad verankert.
   - Rang-Mapping 0–5 kanonisiert und Debrief-Format vereinheitlicht.
   - Level-10-Meilenstein von Lizenzzugang entkoppelt (Chronopolis/Vertrauen vs. Tierpfad).

2. **Tier-V-Freigabe korrigiert**
   - `characters/ausruestung-cyberware.md`: Tier V von Quest-only auf kaufbare
     Lizenz bei Ruf +5 umgestellt (5.000 CU), inklusive Klartext zur CU-basierten
     Begrenzung.

3. **Onboarding-/Mystery-Ton geschärft**
   - `core/spieler-handbuch.md`: harte Alien-Föderations-Aussage in
     Gerücht-/Aktenlogik überführt; Mystery-Contract ergänzt.
   - `gameplay/kampagnenuebersicht.md`: frühe Alien-Lesart entschärft,
     Graue/Greys als Incident-/Deckname definiert, Mystery-Contract ergänzt.

4. **Runtime-nahe Formulierungen synchronisiert**
   - `meta/masterprompt_v6.md` und `core/sl-referenz.md` auf
     `ITI-Ruf-Update` im Debrief gezogen und um SSOT-Regeln ergänzt.

5. **QA-Anschluss erweitert**
   - Neue Statusmatrix `internal/qa/process/ruf-alien-statusmatrix.md` angelegt.
   - `internal/qa/process/known-issues.md` um ZR-018 als abgeschlossenen
     Anschlusslauf ergänzt.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.

## Ergebnis / Anschluss

- Der Ruf-/Tier-Pfad und die Mystery-Tonlage sind jetzt modulübergreifend
  konsistenter dokumentiert.
- Folge-Durchläufe können direkt gegen ZR-018-Statusmatrix + Watchpoints prüfen,
  ohne den Upload-Text erneut vollständig zu zerlegen.
