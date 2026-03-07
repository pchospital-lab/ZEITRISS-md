---
title: "Issue-Pack Fahrplan – Durchlauf 27"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 27

Quelle: Fortsetzung ZR-016 (Klarstellung Save-SSOT-Formulierung im Save-Modul).

## Ziel
Die Save-SSOT-Formulierung so schärfen, dass eindeutig kommuniziert wird:
Es gibt genau ein kanonisches Exportformat (v7), nicht "Kurzfassung vs. Vollfassung"
als zweite Speicherform.

## Scope dieses Durchlaufs

- Textklarstellung im Save-Modul:
  - `systems/gameflow/speicher-fortsetzung.md`
- Lint-Nachzug auf neue Überschrift/Terminologie:
  - `tools/lint_runtime.py`
- QA-Nachführung:
  - neues Log `internal/qa/logs/2026-03-07-issue-pack-durchlauf-27.md`
  - Update `internal/qa/process/known-issues.md` (ZR-016)

## Nicht im Scope

- Runtime.js-Umbau.
- Neue Save-Felder oder Schemaänderungen.
- Änderungen an Mission-/Tonlogik.

## Exit-Kriterium für Durchlauf 27

- Der Save-Abschnitt benennt klar ein einziges Exportformat (`v7`).
- Legacy-Hinweise sind ausdrücklich als Migration/Import-Bridge markiert.
- Lint prüft den aktualisierten Blocknamen weiterhin.
- `bash scripts/smoke.sh` ist grün.
