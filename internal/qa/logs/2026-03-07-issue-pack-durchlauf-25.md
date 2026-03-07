---
title: "QA-Log – Issue-Pack Durchlauf 25"
date: 2026-03-07
scope: "Terminologie-/Editorial-Drift bereinigen und Lint-Guard ausweiten"
status: abgeschlossen
tags: [qa, log]
---

## Quelle
- ZR-016 (externer Codex-Issue-Pack), fortlaufende Runtime-Konsolidierung.
- Offene Restfunde in geladenen Modulen (`GPTs`, `Film ab!`) nach den letzten
  Editorial-Sweeps.

## Umsetzung in diesem Durchlauf

1. **Runtime-Terminologie bereinigt**
   - `gameplay/kampagnenstruktur.md`: "GPTs" auf `KI-SL` umgestellt.
   - `core/sl-referenz.md`: Save-Hinweis von `Film ab!` auf neutralen
     `Einsatzrückblick`-Befehl umgestellt.
   - `core/wuerfelmechanik.md` und `systems/kp-kraefte-psi.md`: verbleibende
     `Film ab!`-Formulierungen in in-world-konformes Wording überführt.

2. **Lint-Guard erweitert (`tools/lint_runtime.py`)**
   - SSOT-Check erkennt jetzt `GPT` und `GPTs` über Pattern `\\bGPTs?\\b`.
   - Runtime-Meta-Check ebenfalls auf `GPTs?` angehoben.
   - Editorial-Aid-Check von Einzeldatei auf alle Runtime-Markdowns erweitert;
     geprüft werden jetzt: `Playlist`, `Soundtrack`, `Akte X`, `am Set`,
     `Sora`, `Video-KI`, `Film ab!`.

3. **QA-Nachführung**
   - Neuer Fahrplan/Log für Durchlauf 25 angelegt.
   - `internal/qa/process/known-issues.md` um Durchlauf 25 ergänzt.

## Checks
- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
