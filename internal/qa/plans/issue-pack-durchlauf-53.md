---
title: "Issue-Pack Fahrplan – Durchlauf 53"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 53

Quelle: `uploads/ZEITRISS_v7_save_load_issue_pack.md` (Issue 1 Re-Validierung: v7-SSOT ohne Parallelformat).

## Ziel

1. Widersprüchliche v7-Feldnamen (`zr_version`, `mission_in_episode`, `attributes`, `arc.open_*`) im Save-SSOT entfernen.
2. Save-Doku, SL-Referenz und Spielerpfad bei Semver-Hinweisen auf den kanonischen Header (`zr`) synchronisieren.
3. Legacy-Pfade explizit als Import-Bridge markieren, damit kein zweites Exportformat suggeriert wird.

## Scope dieses Durchlaufs

- `systems/gameflow/speicher-fortsetzung.md`
  - Abschnitt „Kanonisches Save-Exportformat“ auf das Masterprompt-v7-Modell harmonisieren.
  - Arc-Beschreibung auf `factions/questions/hooks` angleichen.
  - Legacy-Liste um alte Alias-Felder ergänzen und Semver-/Pflichtfeldtexte auf `zr` nachziehen.
- `core/sl-referenz.md`
  - Semver-Passage und Kompaktprofil-Kurzbaum auf `zr` + Legacy-Normalisierung präzisieren.
- `core/spieler-handbuch.md`
  - Semver-Hinweis auf `zr` harmonisieren (Legacy `zr_version` nur Importpfad).
- `internal/qa/process/known-issues.md`
  - ZR-017 um Durchlauf-53-Revalidierung ergänzen.

## Exit-Kriterium

- Es gibt keinen zweiten „kanonischen“ v7-Exportblock mit abweichenden Feldnamen.
- Semver-Kommunikation ist in Save-Doku, SL-Referenz und Spielerpfad konsistent.
- Pflicht-Smoke (`bash scripts/smoke.sh`) läuft grün.
