---
title: "QA-Log – Issue-Pack Durchlauf 05"
version: 0.1.0
tags: [qa, log]
---

# QA-Log – Issue-Pack Durchlauf 05

## Kontext
- Input: `uploads/ZEITRISS_codex_issue_pack.md`
- Fokus: Issue 5 (Versions-/Enum-Drift, Teil 1).

## Umgesetzter Scope

1. **Rang-Enum in Runtime auf kanonischen Wert gezogen**
   - `runtime.js` nutzt jetzt `Rekrut` als Basiswert in `RANK_ORDER`.
   - Default- und Fallback-Ränge in Chronopolis-Gating und Character-Init
     wurden von `Recruit` auf `Rekrut` umgestellt.

2. **Kompatibilität für Legacy-Saves erhalten**
   - `rankIndex()` mappt den Altwert `Recruit` weiterhin auf denselben Rangindex,
     damit bestehende Save-Stände lauffähig bleiben.

## QA-Checks
- Pflichtcheck: `bash scripts/smoke.sh`.

## Offene Restpunkte (nächster Durchlauf)
1. Drift-Guard erweitern: verbotene Modellbegriffe (`GPT`, `Recruit`) in
   geladenen Runtime-Modulen gezielt prüfen.
2. Compliance-Reste im Runtime-Kanon priorisieren und in kleinen Schritten
   entfernen (ohne Importkompatibilität zu brechen).

## Status
- Durchlauf 05: **abgeschlossen**.
