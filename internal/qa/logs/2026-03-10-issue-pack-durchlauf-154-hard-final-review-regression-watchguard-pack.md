---
title: "QA-Log – Durchlauf 154 (Hard Final Review Regression-Watchguard-Pack)"
date: 2026-03-10
result: bestanden
owner: codex
---

# Kontext

Der Hard-Final-Review wurde in den letzten Läufen inhaltlich weitgehend
abgeschlossen. Für Anschlussfähigkeit fehlte noch eine gebündelte
Regressionsabsicherung auf drei Restdrift-Klassen: Split-/Merge-Kanon,
Einstiegskanon und HQ-Kernbereichs-Wording.

# Umgesetzt

1. Neuer Guard `tools/test_hard_final_review_watchguard.js`
   - Prüft in `systems/gameflow/speicher-fortsetzung.md`, dass
     Split/Merge kanonisch für Core-Parallelpfade + separate Rift-Ops bleibt.
   - Prüft Pflichtanker `continuity.split.family_id` bei Core-Parallelpfaden.
   - Blockt den alten Legacy-Satz „standardmäßig nur nach Episodenende ...
     Rift-Ops kanonisch“.
   - Prüft in `systems/gameflow/cinematic-start.md`, dass der Altanker
     „Sobald die Fraktionswahl steht“ nicht zurückkehrt.
   - Prüft in `gameplay/kampagnenstruktur.md`, dass der Altanker
     „Weiterentwicklung eines gemeinsamen Hauptquartiers“ nicht zurückkehrt und
     der feste HQ-Kernbereich explizit bleibt.
   - Erfolgstoken: `hard-final-review-watchguard-ok`.

2. Smoke-Integration
   - `scripts/smoke.sh` um den neuen Pflichtcheck erweitert.

3. Prozessspur
   - Plan ergänzt:
     `internal/qa/plans/issue-pack-durchlauf-154-hard-final-review-regression-watchguard-pack.md`
   - `internal/qa/process/known-issues.md` um Durchlauf 154 erweitert.

# Validierung

- Einzelprüfung erfolgreich:
  - `node tools/test_hard_final_review_watchguard.js`
- Pflicht-Smoke erfolgreich:
  - `bash scripts/smoke.sh`

# Ergebnis

Die verbleibenden Hard-Final-Review-Watchpoints sind jetzt als zusammenhängender
Pipeline-Guard verankert. Damit bleibt die Runtime-SSOT robuster gegenüber
sprachlichem Rückdrift bei späteren Inhaltsüberarbeitungen.
