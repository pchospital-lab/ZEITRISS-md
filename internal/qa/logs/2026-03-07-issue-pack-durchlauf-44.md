---
title: "QA-Log – Issue-Pack Durchlauf 44"
date: 2026-03-07
scope: "Verständlichkeit: Kanon pro aktiver Runde statt missverständlicher Side-Run-Lesart"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- Maintainer-Follow-up: Formulierungen waren funktional korrekt, aber für
  Spielpraxis mit dauerhaft getrennten Gruppen noch zu missverständlich.
- Fahrplan: `internal/qa/plans/issue-pack-durchlauf-44.md`

## Umsetzung in diesem Durchlauf

1. **Spielerlesbare Vereinfachung**
   - `README.md`: Klartext auf "beide Gruppen dürfen normal weiterspielen" und
     "Hauptfortschritt pro aktivem Host-Chat" umgestellt.

2. **Prompt-/SL-Konsens nachgezogen**
   - `meta/masterprompt_v6.md` und `core/sl-referenz.md` auf dieselbe
     Einfachregel synchronisiert (Kanon pro aktivem Host; Merge bleibt host-priorisiert).

3. **Save-SSOT präzisiert**
   - `systems/gameflow/speicher-fortsetzung.md`:
     - OpenWebUI-Lobbybetrieb ohne Side-Run-Missverständnis formuliert.
     - Mid-Episode-5er→3/2-Regel auf "beide Pfade spielbar" + "pro Chat ein
       Host-Kanon" umgestellt.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
