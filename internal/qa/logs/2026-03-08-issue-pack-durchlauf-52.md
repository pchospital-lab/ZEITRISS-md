---
title: "QA-Log – Issue-Pack Durchlauf 52"
date: 2026-03-08
scope: "Issue 4 Rest: formales Mixed-Split-Präzedenzmodell"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- Upload-Issue-Pack: `uploads/ZEITRISS_v7_save_load_issue_pack.md` (Issue 4 Rest).
- Fahrplan: `internal/qa/plans/issue-pack-durchlauf-52.md`.

## Umsetzung in diesem Durchlauf

1. **Mixed-Split-Präzedenzmodell formalisiert**
   - `systems/gameflow/speicher-fortsetzung.md` beschreibt jetzt den
     deterministischen 6-Stufen-Graphen für nicht-kanonische Mischpfade
     (globale Kampagne → branch-lokale Allowlist → Charakter-Dedupe →
     Arena-Normalisierung → Chronopolis-Logs → Debrief-Konsolidierung).
   - Zusatzregeln für `logs.flags.imported_saves[]` (`reason=non_canonical_branch`)
     und Pflicht-Hinweistext wurden ergänzt.

2. **SSOT-Synchronisierung in Runtime-Referenzen**
   - `core/sl-referenz.md`, `meta/masterprompt_v6.md` und `README.md` wurden
     auf denselben Mixed-Split-Importstandard ausgerichtet.

3. **QA-Fixture-/Smoke-Evidenz erweitert**
   - `internal/qa/fixtures/savegame_v7_merge_rift_pvp.json` ergänzt um
     `reason=non_canonical_branch`, `allowed_fields`, Chronopolis-Lognachweis
     sowie Hinweis in `logs.notes[]`.
   - `internal/qa/fixtures/savegame_v7_abort_resume.json` ergänzt um
     Abort-Importmarker (`abort_marker`) im non-kanonischen Importpfad.
   - `tools/test_v7_issue_pack.js` validiert die neuen Marker im Pflichtlauf.

4. **Known-Issue-Fortschritt aktualisiert**
   - `internal/qa/process/known-issues.md` auf Durchlauf 52 fortgeschrieben.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.

## Ergebnis / Anschluss

- ZR-017 ist mit dem formalen Mixed-Split-Präzedenzmodell inhaltlich
  vollständig umgesetzt; verbleibende Folgearbeit ist nur Re-Validierung bei
  zukünftigen Regeländerungen.
