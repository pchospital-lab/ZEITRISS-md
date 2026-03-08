---
title: "QA-Log – Issue-Pack Durchlauf 45"
date: 2026-03-08
scope: "Issue 5: Arena-Savegrenze completed vs idle dokumentarisch und runtime-konsistent festziehen"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- Upload-Issue-Pack: `uploads/ZEITRISS_v7_save_load_issue_pack.md` (Issue 5).
- Fahrplan: `internal/qa/plans/issue-pack-durchlauf-45.md`.

## Umsetzung in diesem Durchlauf

1. **Save-Doku synchronisiert**
   - `systems/gameflow/speicher-fortsetzung.md`: Arena-Save-Regel auf eine
     konsistente Aussage präzisiert: Block nur bei aktivem Matchmaking/Run,
     Save wieder erlaubt im Abschlusszustand (`queue_state=idle|completed` bei
     inaktiver Arena).

2. **SL-Referenz synchronisiert**
   - `core/sl-referenz.md`: dieselbe Grenzregel für den operativen
     Spielleitungs-Text verankert (PvP→HQ-Savepunkt bleibt explizit nutzbar).

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.

## Ergebnis / Anschluss

- Issue-5-Teilziel „eine Wahrheit zu `idle` vs `completed`" ist für die
  Hauptdoku und SL-Referenz bereinigt.
- Nächster Anschluss in ZR-017: Mixed-Split-Protokoll, Px-Zustandsautomat,
  Dedupe/Lineage und E2E-Fixtures weiter priorisieren.
