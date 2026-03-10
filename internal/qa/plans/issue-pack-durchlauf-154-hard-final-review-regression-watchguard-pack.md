---
title: "Issue-Pack Durchlauf 154 – Hard Final Review: Regression-Watchguard-Pack"
date: 2026-03-10
status: abgeschlossen
owner: codex
scope: Runtime/QA
---

# Ziel

Die bereits bereinigten Hard-Final-Review-Restpunkte gegen Regression absichern,
damit Split-/Merge-Kanon, Einstiegskanon und HQ-Kernbereich nicht durch spätere
Textedits wieder in alte Formulierungen zurückfallen.

# Arbeitspaket

- [x] Audit der betroffenen Runtime-Module auf Restdrift durchgeführt
      (`speicher-fortsetzung.md`, `cinematic-start.md`,
      `kampagnenstruktur.md`).
- [x] Neuen Guard `tools/test_hard_final_review_watchguard.js` angelegt.
- [x] Guard-Regeln umgesetzt:
  - Split/Merge bleibt kanonisch für Core-Parallelpfade + separate Rift-Ops.
  - `continuity.split.family_id` bleibt Pflicht bei Core-Parallelpfaden.
  - Legacy-Satz „standardmäßig nur nach Episodenende ... Rift-Ops“ bleibt
    ausgeschlossen.
  - Einstiegskanon-Altanker „Sobald die Fraktionswahl steht“ bleibt
    ausgeschlossen.
  - HQ-Altanker „Weiterentwicklung eines gemeinsamen Hauptquartiers“ bleibt
    ausgeschlossen, fester HQ-Kernbereich bleibt Pflichtanker.
- [x] Guard in `scripts/smoke.sh` als Pflichtcheck integriert.
- [x] Prozessspur für Durchlauf 154 (Plan/Log/known-issues) ergänzt.
- [x] Pflicht-Smoke ausgeführt.

# QA-Checkliste

- [x] `node tools/test_hard_final_review_watchguard.js`
- [x] `bash scripts/smoke.sh`

# Anschluss / Watchpoints

- Bei größeren Textkürzungen in Runtime-Modulen Guard-Regexe kurz gegenlesen,
  damit der semantische Kern stabil bleibt.
- Bei künftigen Startpfad-Änderungen weiterhin auf Kanontrennung achten:
  Default-Pfad bleibt produktiv, Varianten bleiben optional markiert.
