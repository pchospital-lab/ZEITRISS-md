---
title: "QA-Log 2026-03-10 – Durchlauf 141 (Entry-Layer-Watchguard Product-Promise-Hardening)"
version: 1.0.0
date: 2026-03-10
status: abgeschlossen
tags: [qa, onboarding, startvertrag, watchguard]
---

# Kontext

Durchlauf 140 hat den Einstiegspfad bereits auf `solo klassisch` + natürliche Sprache harmonisiert und Archetypen aus den Default-Slots gezogen. Als nächster Qualitätsschritt blieb ein Watchguard-Gap: Das Entry-Layer-Produktversprechen (MMO-ohne-Server/Save=Charakter/Niedrigschwellenstart) war textlich vorhanden, aber noch nicht automatisiert abgesichert.

# Umgesetzte Änderungen

## 1) Onboarding-Watchguard um Produktversprechen erweitert

- Datei: `tools/test_onboarding_start_save_watchguard.js`
- Ergänzungen für `README.md`:
  - Pflichtanker `MMO ohne Server`.
  - Pflichtanker `Save = Charakter`.
  - Niedrigschwellen-Hinweis (`Regelwerk nicht vorab lesen`).
  - Default-Ladepfad-Anker (`19 Slots` oder `19 Wissensmodule`).

## 2) Setup-Guide-Drift für Default-/Optionalpfad mitgesichert

- Datei: `tools/test_onboarding_start_save_watchguard.js`
- Ergänzungen für `docs/setup-guide.md`:
  - Pflichtanker `19 Default-Module/-Slots`.
  - Pflichtanker, dass `characters/charaktererschaffung-optionen.md` nicht im Default-Ladepfad liegt.

## 3) Prozessspur fortgeführt

- Datei: `internal/qa/process/known-issues.md`
- Änderungen:
  - ZR-020-Chronik um Durchlauf 141 ergänzt.
  - ZR-021-Notiz um den neuen Hardening-Schritt aktualisiert.

# Verifikation

1. `bash scripts/smoke.sh` → erfolgreich (`All smoke checks passed`, inkl. `onboarding-start-save-watchguard-ok`).
2. `python3 tools/lint_links.py internal/qa/plans/issue-pack-durchlauf-141-entry-layer-watchguard-product-promise-hardening.md internal/qa/logs/2026-03-10-issue-pack-durchlauf-141-entry-layer-watchguard-product-promise-hardening.md internal/qa/process/known-issues.md` → keine Broken Links.

# Ergebnis

Der Entry-Layer-Startvertrag ist jetzt zusätzlich gegen Produktversprechen-Regressionen abgesichert: Nicht nur Startsyntax/Flow-Anker, sondern auch die zentrale MMO-/Save-Kommunikation und der 19-Module-Defaultpfad werden im Pflicht-Smoke überwacht.
