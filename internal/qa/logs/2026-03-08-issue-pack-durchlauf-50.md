---
title: "QA-Log – Issue-Pack Durchlauf 50"
date: 2026-03-08
scope: "Issue 8: Px-Zustandsmodell für Split/Merge"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- Upload-Issue-Pack: `uploads/ZEITRISS_v7_save_load_issue_pack.md` (Issue 8).
- Fahrplan: `internal/qa/plans/issue-pack-durchlauf-50.md`.

## Umsetzung in diesem Durchlauf

1. **Masterprompt synchronisiert**
   - `meta/masterprompt_v6.md` erweitert das v7-Save-Template um
     `campaign.px_state`.
   - Zustandsmodell dokumentiert: `stable`, `pending_reset`, `consumed`.
   - Merge-Priorität festgezogen: `consumed > pending_reset > stable`
     inklusive Normalisierung von `campaign.px`.

2. **Save-Doku (Modul 12) nachgeschärft**
   - `systems/gameflow/speicher-fortsetzung.md` ergänzt `px_state`
     im Kompakt-Profil.
   - Split-/Merge-Regeln für Px auf den Zustands-Guard umgestellt
     (kein reines Px-Maximum mehr).
   - Nicht-kanonischer Importtext ergänzt um Guard gegen Px-Reanimation.

3. **SL-Referenz + README nachgezogen**
   - `core/sl-referenz.md` ergänzt `campaign.px_state` im persistenten
     Save-Schema und verweist im Px-Policy-Block auf die Merge-Priorität.
   - `README.md` enthält im Multiplayer-Merge-Hinweis denselben
     Px-State-Guard.

4. **QA-Status aktualisiert**
   - `internal/qa/process/known-issues.md` auf Durchlauf 50 erweitert.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.

## Ergebnis / Anschluss

- Px verhält sich bei Split/Merge jetzt als dokumentierter Zustandsautomat;
  ein verbrauchter Px-5-Stand kann nicht über Alt-Branches zurückkommen.
- Offene Restblöcke aus ZR-017 bleiben: Mixed-Split-Protokoll und vollständige
  v7-E2E-Fixtures für 5er-Pfade.
