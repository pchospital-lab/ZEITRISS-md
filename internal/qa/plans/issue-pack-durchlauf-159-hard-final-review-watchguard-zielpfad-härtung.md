---
title: "Issue-Pack Durchlauf 159 – Hard-Final-Review Watchguard-Zielpfad-Härtung"
date: 2026-03-10
status: abgeschlossen
owner: codex
scope: Runtime/QA + Meta/Prozess
issue: ZR-021
---

# Ziel

Der `chronopolis-gate-watchguard` soll bei künftigen Runtime-Makro-Umzügen
nicht mehr manuell auf einen einzelnen Pfad nachgezogen werden müssen.
Die Zielpfadauflösung wird deshalb im Guard selbst robust gemacht.

# Arbeitspaket

1. `tools/test_chronopolis_gate_watchguard.js` so erweitern, dass das
   relevante Runtime-Makrofile automatisch gefunden wird.
2. Guard auf Mehrdeutigkeit absichern (Fail bei mehreren Treffern).
3. Prozessspur aktualisieren (`hard-final-review-next-steps.md`,
   `known-issues.md`, Durchlauf-Log).
4. Pflicht-Smoke laufen lassen.

# Abnahmekriterien

- `chronopolis-gate-watchguard` findet den gültigen Zielpfad automatisch.
- Bei mehreren potenziellen Zielpfaden schlägt der Guard deterministisch fehl.
- Prozessseiten enthalten den Durchlauf-159-Stand.
- `bash scripts/smoke.sh` ist grün.
