---
title: "Issue-Pack Fahrplan – Durchlauf 06"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 06

Quelle: `uploads/ZEITRISS_codex_issue_pack.md`

## Ziel
Den Drift-Guard ausbauen, damit verbotene Modellbegriffe in SSOT-Dateien
früh in CI auffallen und nicht in den Runtime-Kanon zurückrutschen.

## Scope dieses Durchlaufs

- C6 Drift-Tests (P1, Teil 1)
  - `tools/lint_runtime.py` um einen SSOT-Check auf verbotene Begriffe
    erweitern.
  - Prüfumfang auf die drei zentralen SSOT-Quellen begrenzen:
    `core/spieler-handbuch.md`, `core/sl-referenz.md`,
    `meta/masterprompt_v6.md`.
  - Begriffe `GPT` und `Recruit` als CI-Fail im SSOT-Check definieren.

## Nicht im Scope (bewusst verschoben)

- Vollständiger GPT-Terminologie-Cleanup in allen Runtime-Modulen außerhalb
  der drei SSOT-Dateien.
- Entfernung/Refactoring von Compliance-Kompatibilitätspfaden in `runtime.js`.
- Zusätzliche neue Lint-Cluster für weitere Legacy-Tokens.

## Exit-Kriterium für Durchlauf 06

- `tools/lint_runtime.py` enthält einen automatischen SSOT-Check auf
  verbotene Begriffe (`GPT`, `Recruit`) in den drei Zieldateien.
- Pflichtcheck `bash scripts/smoke.sh` läuft vollständig grün.
