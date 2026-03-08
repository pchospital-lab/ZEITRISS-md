---
title: "Issue-Pack Durchlauf 89 – Continuity-Output-Contract Guard"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-08"
links:
  issue: "uploads/ZEITRISS_continuity_save_redesign.md"
  statusmatrix: "internal/qa/process/known-issues.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-88-anchor-template-toolkit-restdrift.md"
---

# Ziel

Die erzählerischen Pflichtausgaben aus dem Kontinuitäts-Redesign
(Kontinuitätsrückblick, Split-/Rejoin-Beat, Echo-Fortwirkung ≤ 2 Sitzungsblöcke)
als maschinenlesbaren QA-Guard absichern, damit Folgeänderungen keine stillen
Regressionen im Output-Contract einführen.

1. QA-Fixture für Multi-Load-Recap mit allen vier Pflichtblöcken ergänzen.
2. Guard-Skript ergänzen, das Recap, Split-/Rejoin-Beat und Echo-Fenster prüft.
3. Guard in `scripts/smoke.sh` integrieren.
4. Pflichtchecks erneut ausführen und Anschlusslauf dokumentieren.

# Checkliste

- [x] Neue Fixture `internal/qa/fixtures/continuity_output_contract_multi_load.json` angelegt.
- [x] Guard `tools/test_continuity_output_contract.js` prüft Pflichtblöcke + Echo-Fenster.
- [x] `scripts/smoke.sh` führt den neuen Guard aus.
- [x] Pflicht-Smoke ausgeführt.
- [x] Linklint ausgeführt.

# Abschluss

Durchlauf 89 härtet die Continuity-Ausgabe auf QA-Ebene: Neben Schema/Lineage
wird jetzt auch der narrative Mindestvertrag für Multi-Load/Split/Rejoin
programmatisch mitgeprüft.
