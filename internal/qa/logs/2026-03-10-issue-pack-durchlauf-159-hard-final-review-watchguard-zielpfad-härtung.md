---
title: "Log – Durchlauf 159 (Hard-Final-Review / Watchguard-Zielpfad-Härtung)"
date: 2026-03-10
status: abgeschlossen
owner: codex
scope: Runtime/QA + Meta/Prozess
issue: ZR-021
---

## Kontext

Der offene Anschluss-Task aus der Hard-Final-Review-Übersicht verlangte eine
stabilere Pflege des `chronopolis-gate-watchguard`, damit Pfad-Umzüge der
Runtime-Makros nicht als manueller Folgeschritt liegenbleiben.

## Umsetzung

- `tools/test_chronopolis_gate_watchguard.js` wurde von statischem Dateipfad auf
  robuste Zielpfad-Ermittlung umgestellt:
  - bevorzugt weiterhin `internal/runtime/toolkit-runtime-makros.md`;
  - fällt bei Pfadänderungen auf eine kontrollierte Suche in Markdown-Dateien
    mit Runtime/Toolkit/Makro-Signalbegriffen zurück;
  - akzeptiert nur genau einen Treffer mit den Kernmakros
    `chrono_grant_key_if_lvl10()` + `chrono_launch_rift(seed_id)`.
- Der Guard gibt den aufgelösten Zielpfad explizit aus, damit Smoke-Logs bei
  Umzügen sofort nachvollziehbar bleiben.
- Prozessseiten synchronisiert:
  - `internal/qa/process/hard-final-review-next-steps.md`
  - `internal/qa/process/known-issues.md`

## Ergebnis

- Der bisher manuell nachzuziehende Pfad-Task ist technisch entschärft.
- Hard-Final-Review-Anschluss bleibt bei Runtime-Refactors reproduzierbarer.

## Checks

- `node tools/test_chronopolis_gate_watchguard.js` erfolgreich.
- `bash scripts/smoke.sh` erfolgreich.
