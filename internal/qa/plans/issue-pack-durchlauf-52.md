---
title: "Issue-Pack Fahrplan – Durchlauf 52"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 52

Quelle: `uploads/ZEITRISS_v7_save_load_issue_pack.md` (Issue 4 Rest: Mixed Split/Merge).

## Ziel

1. Das offene Mixed-Split-Präzedenzmodell (Rift/PvP/Chronopolis/Abort) als
   deterministisches Importmodell dokumentieren.
2. README, SL-Referenz, Save-Doku und Masterprompt auf denselben
   Präzedenzgraphen synchronisieren.
3. Fixture-/Smoke-Evidenz um non-kanonische Mixed-Importmarker erweitern.

## Scope dieses Durchlaufs

- `systems/gameflow/speicher-fortsetzung.md`
  - Nicht-kanonische Branches um 6-stufigen Merge-Präzedenzgraph + Beispiele
    (Rift+PvP, Abort, Chronopolis) ergänzen.
- `core/sl-referenz.md`
  - Chat-/SL-Regelteil um denselben Mixed-Split-Importstandard ergänzen.
- `meta/masterprompt_v6.md`
  - Save-v7-Regeln um identische Mixed-Split-Präzedenz als SSOT ergänzen.
- `README.md`
  - Bring-Your-Character Abschnitt auf denselben Mixed-Split-Guard präzisieren.
- `internal/qa/fixtures/savegame_v7_merge_rift_pvp.json`
  - Non-kanonische Branch-Reason + Allowlist + Chronopolis-Loghinweis ergänzen.
- `internal/qa/fixtures/savegame_v7_abort_resume.json`
  - Abort-Importmarker (`non_canonical_branch`, `abort_marker`) ergänzen.
- `tools/test_v7_issue_pack.js`
  - Assertions für Mixed-Import-Reason/Allowlist/Chronopolis-Log und
    Abort-Importmarker ergänzen.
- `internal/qa/process/known-issues.md`
  - ZR-017 Fortschritt auf Durchlauf 52 fortschreiben.

## Exit-Kriterium

- Das formale Mixed-Split-Präzedenzmodell ist in allen kanonischen Quellen
  konsistent beschrieben.
- Fixture-Strecke prüft non-kanonische Mixed-Imports deterministisch.
- Pflicht-Smoke (`bash scripts/smoke.sh`) läuft grün.
