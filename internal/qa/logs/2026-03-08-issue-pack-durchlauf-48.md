---
title: "QA-Log – Issue-Pack Durchlauf 48"
date: 2026-03-08
scope: "Issue 7: Dedupe + Merge-Lineage dokumentarisch verankern"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- Upload-Issue-Pack: `uploads/ZEITRISS_v7_save_load_issue_pack.md` (Issue 7).
- Fahrplan: `internal/qa/plans/issue-pack-durchlauf-48.md`.

## Umsetzung in diesem Durchlauf

1. **Masterprompt (v7-Template) gehärtet**
   - `meta/masterprompt_v6.md` ergänzt Pflichtfelder `save_id`,
     `parent_save_id`, `merge_id`, `branch_id` direkt im kanonischen Save-JSON.
   - Dedupe-Verhalten als KI-SL-Regel ergänzt:
     duplicate `save_id` => Branch-Duplikat blocken,
     duplicate `characters[].id` => Konflikt markieren statt still mergen.
   - `logs.flags` um `imported_saves`, `duplicate_branch_detected`,
     `duplicate_character_detected` ergänzt.

2. **Runtime-Doku synchronisiert**
   - `systems/gameflow/speicher-fortsetzung.md` führt die gleichen
     Lineage-Schlüssel im Kompakt-Profil.
   - Merge-Schutz ergänzt: verworfene/konflikthafte Imports in
     `logs.flags.imported_saves[]` protokollieren, Konfliktflags explizit setzen,
     Allowlist-Erweiterung für `duplicate_branch` / `duplicate_character`.

3. **SL-Referenz + README nachgezogen**
   - `core/sl-referenz.md` spiegelt Lineage-Pflichtfelder, Dedupe-Regeln und
     `imported_saves[]`-Protokoll.
   - `README.md` enthält eine kurze Merge-Schutz-Notiz für den
     OpenWebUI-Hostbetrieb.

4. **QA-Status aktualisiert**
   - `internal/qa/process/known-issues.md`: ZR-017-Notiz auf Durchlauf 48
     (Dedupe/Lineage-Doku) erweitert.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.

## Ergebnis / Anschluss

- Dedupe/Lineage ist als v7-Standard jetzt konsistent in Masterprompt,
  Save-Doku und SL-Referenz dokumentiert.
- Offene Restblöcke aus ZR-017 bleiben: Mixed-Split-Protokoll,
  Px-Zustandsautomat, v7-E2E-Fixtures.
