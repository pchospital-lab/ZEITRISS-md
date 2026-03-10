---
title: "Issue-Pack Durchlauf 152 – Hard Final Review: Split-/Branch-Import-Klarstellung"
date: 2026-03-10
status: abgeschlossen
owner: codex
scope: Runtime/QA
---

# Ziel

Den verbleibenden Begriffsdrift im Split-/Merge-Abschnitt von
`systems/gameflow/speicher-fortsetzung.md` entfernen: Überschrift und Einleitung
sollen nicht mehr implizieren, dass kanonische Core-Parallelpfade
"nicht-kanonisch" seien.

# Arbeitspaket

- [x] `systems/gameflow/speicher-fortsetzung.md`: Abschnittstitel von
      "Nicht-kanonische Branches ohne Protokoll" auf
      "Branch-Importe ohne Split-Protokoll" umstellen.
- [x] Einleitungsabsatz präzisieren: Core-Parallelpfade mit gleicher
      `continuity.split.family_id` bleiben kanonisch; nur gemischte Pfade ohne
      gemeinsames Split-Protokoll laufen als Branch-Import.
- [x] Prozessspur für Durchlauf 152 (Plan/Log/known-issues) ergänzen.
- [x] Pflicht-Smoke ausführen.

# QA-Checkliste

- [x] `bash scripts/smoke.sh`
- [x] Spot-Check auf Widerspruchsformulierung im Split-/Merge-Block
      (`Nicht-kanonische Branches` entfernt).

# Anschluss / Watchpoints

- Bei weiteren Textanpassungen im Save-System Überschriften immer gegen den
  tatsächlichen Kanonstatus (Core-Split kanonisch vs. Import-Fallback)
  spiegeln, damit kein semantischer SSOT-Drift zurückkommt.
