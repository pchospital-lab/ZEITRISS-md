---
title: "Issue-Pack Fahrplan – Durchlauf 31"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 31

Quelle: Fortsetzung ZR-016 mit Fokus auf Restdrift im Save-Modul (`speicher-fortsetzung.md`).

## Ziel

Verbleibende Textdrifts im Save-Modul beseitigen, die v7-Kanon und Legacy-Import
vermischt darstellen:
- keine Formulierungen mehr, die v6 als aktives Exportformat darstellen,
- Arc-/Ökonomie-Wording im Leittext auf v7 (`arc.timeline`, `economy.hq_pool`) ziehen,
- Guard ergänzen, damit v6-Exportbehauptungen nicht zurückkehren.

## Scope dieses Durchlaufs

- `systems/gameflow/speicher-fortsetzung.md`
- `tools/lint_runtime.py`
- QA-Nachführung: Log + Known-Issues-Update

## Nicht im Scope

- Laufzeit-Umbau in `runtime.js`.
- Entfernen aller v6-Migrationsbeispiele aus der Save-Doku.
- Rebalancing von Save-/Economy-Werten.

## Exit-Kriterium für Durchlauf 31

- `speicher-fortsetzung.md` benennt v7 konsistent als einziges aktives Exportformat.
- Aussagen wie „Aktuelle Saves (v6)" oder „Single Source Save v6" sind entfernt.
- Timeline-/Ökonomie-Referenzen im Leittext sind auf v7-Pfade ausgerichtet.
- Neuer Lint-Guard schlägt bei v6-Exportbehauptungen im Save-Modul fehl.
- `bash scripts/smoke.sh` läuft grün.
