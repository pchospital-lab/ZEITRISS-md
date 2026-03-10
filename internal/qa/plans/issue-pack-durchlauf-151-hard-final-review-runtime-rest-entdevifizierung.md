---
title: "Issue-Pack Durchlauf 151 – Hard Final Review: Runtime-Rest-Entdevifizierung"
date: 2026-03-10
status: abgeschlossen
owner: codex
scope: Runtime/QA
---

# Ziel

Verbleibende QA-/Testrun-Referenzen in aktiven Runtime-Modulen entfernen bzw.
neutralisieren, damit die geladenen Wissensspeicher konsequent auf den
Spielkanon fokussieren.

# Arbeitspaket

- [x] `systems/gameflow/speicher-fortsetzung.md`: QA-/Testrun-Label in
      Laufzeitregeln entkoppeln (UI-Persistenz, Cross-Mode-Matrix, Load-Hinweis,
      HQ-Loop-Freeplay).
- [x] `systems/toolkit-gpt-spielleiter.md`: QA-spezifische Formulierungen im
      HUD-/SUG-Abschnitt und Runtime-Makro-Hinweis neutralisieren.
- [x] `gameplay/kampagnenstruktur.md`: Testrun-Label am Seed-Lock entfernen.
- [x] Prozessspur für Durchlauf 151 (Plan/Log/known-issues) ergänzen.
- [x] Pflicht-Smoke ausführen.

# QA-Checkliste

- [x] `bash scripts/smoke.sh`
- [x] Spot-Check: geänderte Runtime-Dateien enthalten keine neuen
      `QA`/`Testrun`-Labels an den bearbeiteten Stellen.

# Anschluss / Watchpoints

- Bei künftigen Regeltext-Ergänzungen in Runtime-Slots keine
  verfahrensbezogenen Begriffe (`Testrun`, `Acceptance`, `QA-Mode`) mehr im
  Kanontext verwenden.
