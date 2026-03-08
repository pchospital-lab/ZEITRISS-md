---
title: "QA-Log – Issue-Pack Durchlauf 53"
date: 2026-03-08
scope: "Issue 1 Re-Validierung: v7-SSOT ohne Parallelformat"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- Upload-Issue-Pack: `uploads/ZEITRISS_v7_save_load_issue_pack.md` (Issue 1 Nachschärfung).
- Fahrplan: `internal/qa/plans/issue-pack-durchlauf-53.md`.

## Umsetzung in diesem Durchlauf

1. **V7-Exportbeispiel konsolidiert**
   - In `systems/gameflow/speicher-fortsetzung.md` wurde der widersprüchliche
     „Kanonisches Save-Exportformat“-Block von Altfeldern (`zr_version`,
     `mission_in_episode`, `attributes`, `arc.open_*`) auf den v7-SSOT mit
     `zr`, `campaign.mission`, `attr` und `arc.{factions,questions,hooks}`
     umgestellt.

2. **Legacy klar als Import-Bridge markiert**
   - Derselbe Abschnitt benennt die Altfelder jetzt explizit als reine
     Importpfade (`zr_version`, `campaign.mission_in_episode`,
     `characters[].attributes`, `arc.open_seeds/open_questions/timeline`).

3. **Semver-/Pflichtfeldtexte synchronisiert**
   - `systems/gameflow/speicher-fortsetzung.md`, `core/sl-referenz.md` und
     `core/spieler-handbuch.md` referenzieren den kanonischen Header `zr`;
     Legacy `zr_version` wird nur noch als Normalisierung beim Import erklärt.

4. **Known-Issues fortgeschrieben**
   - `internal/qa/process/known-issues.md` erhielt den Verweis auf
     Durchlauf 53 als SSOT-Revalidierung ohne neue Regeländerung.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.

## Ergebnis / Anschluss

- Die Save-v7-Dokumentation besitzt keinen konkurrierenden „zweiten“
  Exportkanon mehr.
- Nächste Durchläufe können auf dieser konsolidierten Basis gezielt weitere
  Runtime-/Fixture-Regressionen prüfen.
