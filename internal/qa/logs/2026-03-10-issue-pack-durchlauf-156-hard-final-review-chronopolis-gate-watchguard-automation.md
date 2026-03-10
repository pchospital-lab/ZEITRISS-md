---
title: "QA-Log – Durchlauf 156 (Hard Final Review Chronopolis-Gate-Watchguard-Automation)"
date: 2026-03-10
result: bestanden
owner: codex
---

# Kontext

In der Anschlussübersicht (Durchlauf 155) war der manuelle Block
"Manual Chronopolis Gate Smoke" als offener Automatisierungsrest geführt.
Für reproduzierbare Folge-Durchläufe wurde dieser Rest nun in einen
Pflicht-Watchguard überführt.

# Umgesetzt

1. Neuer Chronopolis-Gate-Watchguard ergänzt:
   - `tools/test_chronopolis_gate_watchguard.js`
   - Prüft die fünf bisherigen Manual-Punkte direkt gegen den Runtime-Makrotext:
     - Lvl10-Key-Grant + HQ-Hook,
     - `fr_contact` nur im HQ,
     - `chrono_launch_rift` nur im HQ nach Episodenende,
     - Epoch-Fallback `chrono.epoch -> campaign.epoch`,
     - Chronopolis bleibt `CITY` und zählt nicht als HQ.

2. Pflicht-Smoke auf Guard umgestellt:
   - `scripts/smoke.sh` ruft den neuen Watchguard auf
     (`chronopolis-gate-watchguard-ok`).
   - Der bisherige manuelle Echo-Block wurde entfernt.

3. Prozessspur aktualisiert:
   - Neuer Plan: `internal/qa/plans/issue-pack-durchlauf-156-hard-final-review-chronopolis-gate-watchguard-automation.md`
   - `internal/qa/process/known-issues.md` um Durchlauf-156 ergänzt.
   - `internal/qa/process/hard-final-review-next-steps.md` priorisierte Aufgaben synchronisiert.

# Validierung

- Einzeltest erfolgreich:
  - `node tools/test_chronopolis_gate_watchguard.js`
- Pflicht-Smoke erfolgreich:
  - `bash scripts/smoke.sh`

# Ergebnis

Der letzte manuelle Chronopolis-Gate-Rest ist jetzt als verpflichtender,
maschinell auswertbarer Smoke-Guard abgesichert. Folge-Durchläufe können ohne
Handprüfung an genau diesem Punkt anschließen.
