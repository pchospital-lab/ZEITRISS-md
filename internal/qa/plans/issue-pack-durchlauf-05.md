---
title: "Issue-Pack Fahrplan – Durchlauf 05"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 05

Quelle: `uploads/ZEITRISS_codex_issue_pack.md`

## Ziel
Den Enum-Drift bei Rangbezeichnungen (`Recruit` vs. `Rekrut`) im Runtime-Pfad
schließen und die Iteration für den nächsten Drift-Guard vorbereiten.

## Scope dieses Durchlaufs

- C5 Versions-/Enum-Drift (P1, Teil 1)
  - `runtime.js` auf `Rekrut` als Standard-Rangwert umstellen.
  - Rank-Gating in Chronopolis auf den kanonischen Rangbegriff ausrichten.
  - Legacy-Eingaben mit `Recruit` weiterhin kompatibel akzeptieren
    (Import-/Fallback-Pfad).

## Nicht im Scope (bewusst verschoben)

- Entfernen von Legacy-/Compatibility-Hooks außerhalb des Rang-Enums.
- Vollständiger GPT-Terminologie-Cleanup in allen Runtime-Modulen.
- Neue globale Drift-Lints gegen alle Legacy-Tokens.

## Exit-Kriterium für Durchlauf 05

- `runtime.js` nutzt `Rekrut` als Default für Rangwerte und Min-Rank-Fallbacks.
- Bestehende Saves mit `Recruit` bleiben über Kompatibilitäts-Mapping lauffähig.
- Pflichtcheck `bash scripts/smoke.sh` ist grün.
