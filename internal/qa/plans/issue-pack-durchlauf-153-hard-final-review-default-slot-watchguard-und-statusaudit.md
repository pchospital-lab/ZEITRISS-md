---
title: "Issue-Pack Durchlauf 153 – Hard Final Review: Default-Slot-Watchguard & Statusaudit"
date: 2026-03-10
status: abgeschlossen
owner: codex
scope: Runtime/QA
---

# Ziel

Den verbleibenden Hard-Final-Review-Anschluss als laufende Qualitätssicherung
absichern: Das Default-Modul `charaktererschaffung-grundlagen.md` darf keine
implizite Runtime-Abhängigkeit auf das optionale Modul
`charaktererschaffung-optionen.md` zurückbekommen.

# Arbeitspaket

- [x] Neuen Watchguard `tools/test_default_slot_dependency_watchguard.js`
      anlegen.
- [x] Guard auf Pflichtfall ausrichten:
      `characters/charaktererschaffung-grundlagen.md` enthält **keinen** direkten
      Verweis auf `charaktererschaffung-optionen.md`.
- [x] Guard in `scripts/smoke.sh` integrieren.
- [x] Prozessspur für Durchlauf 153 (Plan/Log/known-issues) ergänzen.
- [x] Pflicht-Smoke ausführen.

# QA-Checkliste

- [x] `node tools/test_default_slot_dependency_watchguard.js`
- [x] `bash scripts/smoke.sh`

# Anschluss / Watchpoints

- Wenn neue optionale Charaktermodule entstehen, Default-Slots weiterhin ohne
  harte Dateiabhängigkeit halten.
- Bei Erweiterungen am Startpfad prüfen, ob der Onboarding-Guard und der neue
  Default-Slot-Guard weiterhin denselben Produktpfad absichern.
