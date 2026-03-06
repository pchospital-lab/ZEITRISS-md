---
title: "Issue-Pack Fahrplan – Durchlauf 04"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 04

Quelle: `uploads/ZEITRISS_codex_issue_pack.md`

## Ziel
Den noch offenen Save-SSOT-Drift in `core/sl-referenz.md` beheben und einen
Drift-Guard ergänzen, damit v7-Zielpfade in der SL-Referenz stabil bleiben.

## Scope dieses Durchlaufs

- C1 Save-SSOT + Wallet (P0, Teil 2)
  - Save-v7-Block in `core/sl-referenz.md` auf das v7-Zielmodell konsolidieren:
    `v: 7`, `characters[].wallet`, `economy.hq_pool`, `arc.timeline`.
  - Legacy-Begriffe dort nur als Import/Migration (v6) führen, nicht als
    aktiven Runtime-Standard.

- C6 Drift-Tests (P1, Teil 1)
  - `tools/lint_runtime.py` um einen Save-Contract-Check für den Save-v7-
    Abschnitt in `core/sl-referenz.md` erweitern.
  - Check soll Zielpfade erzwingen und zentrale Legacy-Standardformulierungen
    im v7-Block als Fehler markieren.

## Nicht im Scope (bewusst verschoben)

- Runtime-Migrationslogik in `runtime.js` (Importpfad bleibt unverändert).
- Vollständige Bereinigung aller Legacy-Token im gesamten Repo außerhalb des
  Save-v7-Abschnitts.

## Exit-Kriterium für Durchlauf 04

- Save-v7-Abschnitt in `core/sl-referenz.md` referenziert das Zielmodell
  konsistent (`v: 7`, `characters[].wallet`, `economy.hq_pool`, `arc`).
- `tools/lint_runtime.py` prüft den Save-v7-Abschnitt auf Zielmodell +
  Legacy-Drift.
- Pflichtcheck `bash scripts/smoke.sh` ist grün.
