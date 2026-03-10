---
title: "Issue-Pack Durchlauf 156 – Hard Final Review: Chronopolis-Gate-Watchguard-Automation"
date: 2026-03-10
status: abgeschlossen
owner: codex
scope: Runtime/QA + Meta/Prozess
---

# Ziel

Den verbleibenden manuellen Chronopolis-Gate-Block im Pflicht-Smoke
vollständig automatisieren, damit der Anschlussprozess ohne manuelle
Interpretationsschritte reproduzierbar bleibt.

# Arbeitspaket

- [x] Neuer Guard `tools/test_chronopolis_gate_watchguard.js` erstellt.
- [x] Die bisherigen Manual-Checks als Regex-Anker in den Makros abgesichert:
      Lvl10-Key-Grant im HQ-Hook, `fr_contact` HQ-only, Rift-Launch-Gate,
      Epoch-Fallback und CITY-vs-HQ-Anker.
- [x] `scripts/smoke.sh` auf den neuen Guard umgestellt und den manuellen
      Chronopolis-Block entfernt.
- [x] Prozessspur (Plan/Log/known-issues/next-steps) synchronisiert.
- [x] Pflicht-Smoke ausgeführt.

# QA-Checkliste

- [x] `node tools/test_chronopolis_gate_watchguard.js`
- [x] `bash scripts/smoke.sh`

# Anschluss / Watchpoints

- Wenn Chronopolis-Makros aus `internal/runtime/toolkit-runtime-makros.md`
  in andere Runtime-Slots migriert werden, Guard-Targetpfad mitziehen.
- Nächster Housekeeping-Schritt bleibt die weitere Entrümpelung langer
  Prozess-Historien in Richtung Archive.
