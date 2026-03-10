# QA-Log – Durchlauf 178 (Hard-Final-Review Weltstatus-Watchguard Folgewirkungsanker)

## Ausgangslage

Die Durchläufe 166–177 haben SSOT-Drift bereinigt und den Loader-Standard in
allen Hard-Final-Review-Watchguards stabilisiert. Für die Weltstatus-
Rückkopplung bestand noch ein kleiner Robustheitsgap: Der Director-Layer-
Guard prüfte den Weltstatusanker bereits in den Kernreferenzen, jedoch noch
nicht zusätzlich im Runtime-Kampagnenkanon (`gameplay/kampagnenstruktur.md`) und
ohne verpflichtenden Folgewirkungs-Patternanker.

## Umsetzung

- `tools/test_director_layer_watchguard.js` strukturell geschärft:
  - Dokumentlisten getrennt in
    - `fullDirectorLayerDocs` (Relevanzsatz + ITI-Bulletin + Weltstatus),
    - `worldstatusDocs` (inkl. `gameplay/kampagnenstruktur.md`).
- Weltstatus-Assertion in allen betroffenen Dokumenten gehärtet:
  - weiterhin „genau eine Weltstatus-Zeile pro Missionszyklus“,
  - weiterhin Quelle aus `arc.factions/questions/hooks`,
  - neu verpflichtend: expliziter Folgewirkungsanker
    (`Folge`/`Folgewirkung`).
- Damit ist der bereits eingeführte inhaltliche Pflichtsatz
  („Weltstatus-Zeile mit konkreter Folge“) jetzt auch technisch enger
  regressionsgesichert.

## Ergebnis

- `node tools/test_director_layer_watchguard.js` läuft grün
  (`director-layer-watchguard-ok`).
- Pflicht-Smoke grün:
  - `bash scripts/smoke.sh` → „All smoke checks passed.“
- Prozessspur auf Durchlauf-178-Stand aktualisiert (`known-issues.md` und
  `hard-final-review-next-steps.md`).
