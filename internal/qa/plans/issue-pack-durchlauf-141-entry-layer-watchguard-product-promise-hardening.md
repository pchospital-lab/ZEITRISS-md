---
title: "Issue-Pack Durchlauf 141 – Entry-Layer-Watchguard Product-Promise-Hardening"
version: 1.0.0
status: abgeschlossen
tags: [qa, onboarding, startvertrag, watchguard]
---

# Ziel

Den Post-140-Anschlusslauf für ZR-021 absichern: Der bestehende Onboarding-Watchguard soll nicht nur Startsyntax/Defaultpfade prüfen, sondern auch die produktseitigen Entry-Layer-Kernaussagen (MMO-ohne-Server, Save=Charakter, 19-Module-Default, Archetypen außerhalb Default) gegen Regression schützen.

## Scope

- `tools/test_onboarding_start_save_watchguard.js`
- Prozessspur (`internal/qa/logs/`, `internal/qa/process/known-issues.md`)

## Checkliste

- [x] Entry-Layer-Watchguard um Produktversprechen-Checks im README erweitert (`MMO ohne Server`, `Save = Charakter`, Niedrigschwellen-Start).
- [x] Entry-Layer-Watchguard um Default-Ladepfad-Checks erweitert (README + Setup-Guide: 19 Module/Slots).
- [x] Entry-Layer-Watchguard um Optionalitäts-Check erweitert (`chars-options` nicht im Default-Ladepfad im Setup-Guide).
- [x] Pflicht-Smoke (`bash scripts/smoke.sh`) ausführen.
- [x] Link-Lint für geänderte QA-/Prozessdateien ausführen.
