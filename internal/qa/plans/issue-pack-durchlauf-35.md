---
title: "Issue-Pack Fahrplan – Durchlauf 35"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 35

Quelle: Fortsetzung ZR-016 mit Fokus auf Issue 1 (Save-Schema v7 als einzige
Runtime-Wahrheit) und Issue 6 (Drift-Tests) aus
`uploads/ZEITRISS_codex_issue_pack.md`.

## Ziel

Das ausführliche HQ-Deepsave-Beispiel im Save-Modul auf das v7-Zielmodell
ziehen (ohne aktive Legacy-/Compliance-Reste) und einen dedizierten Lint-Guard
ergänzen, der genau diesen Block auf Rückfälle prüft.

## Scope dieses Durchlaufs

- `systems/gameflow/speicher-fortsetzung.md`
- `tools/lint_runtime.py`
- QA-Nachführung: Log + Known-Issues-Update

## Nicht im Scope

- Änderungen an der Laufzeit-Importlogik in `runtime.js`.
- Umbenennung historischer Dateien wie `masterprompt_v6.md`.
- Neue Save-Feldfamilien außerhalb des bestehenden v7-Kanons.

## Exit-Kriterium für Durchlauf 35

- Der Abschnitt „Voller HQ-Deepsave (Solo/Gruppe)“ nutzt nur v7-Strukturen
  (`v`, `characters[]`, `wallet`, `economy.hq_pool`, `arc`).
- Legacy-/Altpfade (`save_version`, `party`, `team`, `economy.cu`,
  `economy.wallets`, `arc_dashboard`) sind aus dem aktiven HQ-Deepsave-Block
  entfernt.
- Ein neuer Lint-Check prüft den HQ-Deepsave-Block explizit auf die v7-SSOT
  und schlägt bei Rückfällen fehl.
- `bash scripts/smoke.sh` läuft vollständig grün.
