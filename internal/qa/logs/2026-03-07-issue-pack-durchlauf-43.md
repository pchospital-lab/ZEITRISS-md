---
title: "QA-Log – Issue-Pack Durchlauf 43"
date: 2026-03-07
scope: "OpenWebUI-Hopper/Leaver-Betrieb: Host-SSOT vs. Side-Run klargezogen"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- Maintainer-Follow-up: reale private OpenWebUI-Nutzung mit häufigem Host-Wechsel,
  wechselnden Gruppen und Leaver/Rejoin nach fast jeder Mission.
- Fahrplan: `internal/qa/plans/issue-pack-durchlauf-43.md`

## Umsetzung in diesem Durchlauf

1. **Save-SSOT um Lobbybetrieb ergänzt**
   - `systems/gameflow/speicher-fortsetzung.md`: neuer Unterabschnitt
     „OpenWebUI-Lobbybetrieb (Hopper/Leaver)".
   - Festgelegt: pro Chat genau ein kanonischer Host; Joiner importieren
     Charakterdaten, Wallet und Loadout; kein impliziter Episodenwechsel.

2. **Leitquellen synchronisiert**
   - `README.md`: Hopper-Betrieb als Side-Run-Modell dokumentiert,
     Leaver-Rejoin auf Host-Stand konkretisiert.
   - `meta/masterprompt_v6.md`: Host-Hopping als erlaubtes, aber
     nicht-kanonisches Kampagnenmodell ergänzt.
   - `core/sl-referenz.md`: Betriebsregel im Chat-Kurzbefehlsumfeld gespiegelt.

3. **Mid-Episode-Regel nachgeschärft**
   - `systems/gameflow/speicher-fortsetzung.md`: Mid-Episode-Abschnitt um
     Mission-zu-Mission-Hopper-Hinweis erweitert.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
