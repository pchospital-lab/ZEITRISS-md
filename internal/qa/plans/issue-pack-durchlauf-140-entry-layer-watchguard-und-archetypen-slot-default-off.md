---
title: "Issue-Pack Durchlauf 140 – Entry-Layer-Watchguard + Archetypen aus Default-Slots"
version: 1.0.0
status: abgeschlossen
tags: [qa, onboarding, startvertrag, slots]
---

# Ziel

Den Anschlusslauf nach Durchlauf 139 produktseitig festziehen: Archetypen/Pregens aus dem Default-Wissensspeicher entfernen, Entry-Layer-Onboarding (README/Setup-Guide/Setup-Script) per Smoke-Watchguard absichern und die Folgearbeit als eigenen Track in den Known-Issues verankern.

## Scope

- `master-index.json`
- `tools/test_onboarding_start_save_watchguard.js`
- `README.md`
- `docs/setup-guide.md`
- Prozessspur (`internal/qa/logs/`, `internal/qa/process/known-issues.md`)

## Checkliste

- [x] `chars-options` im `master-index.json` auf optionalen Nicht-Default-Slot (`slot:false`) setzen.
- [x] Entry-Layer-Guard ergänzen (README/Setup-Guide/Setup-Script: `solo klassisch` Default, natürliche Sprache, `solo schnell` optional/Fast-Lane).
- [x] README/Setup-Guide auf den neuen Default-Ladepfad (19 Wissensmodule = 1+18 Runtime) harmonisieren.
- [x] Neuen Follow-up-Track `ZR-021` in `known-issues.md` anlegen und Durchlauf 140 rückreferenzieren.
- [x] Pflicht-Smoke (`bash scripts/smoke.sh`) ausführen.
- [x] Link-Lint für geänderte Doku-/QA-Dateien ausführen.
