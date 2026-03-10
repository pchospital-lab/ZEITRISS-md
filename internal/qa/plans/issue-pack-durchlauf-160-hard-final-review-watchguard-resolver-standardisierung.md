---
title: "Issue-Pack Durchlauf 160 – Hard-Final-Review Watchguard-Resolver-Standardisierung"
date: 2026-03-10
status: abgeschlossen
owner: codex
scope: Runtime/QA + Meta/Prozess
issue: ZR-021
---

# Ziel

Die robuste Zielpfad-Fundlogik aus Durchlauf 159 soll nicht als Einzel-
Implementierung verbleiben, sondern als wiederverwendbare Utility in `tools/`
vorliegen, damit neue/angepasste Watchguards konsistent aufgebaut werden.

# Arbeitspaket

1. Gemeinsame Resolver-Utility für eindeutige Markdown-Zielpfadauflösung in
   `tools/` ergänzen (Preferred-Pfade + kontrollierter Fallback-Scan).
2. `tools/test_chronopolis_gate_watchguard.js` auf die Utility umstellen,
   ohne inhaltliche Guard-Regeln zu ändern.
3. Prozessspur synchronisieren (`hard-final-review-next-steps.md`,
   `known-issues.md`, Durchlauf-Log).
4. Pflicht-Smoke laufen lassen.

# Abnahmekriterien

- Utility liefert deterministisch genau einen gültigen Zielpfad oder failt klar.
- `chronopolis-gate-watchguard` nutzt die Utility produktiv.
- Prozessseiten enthalten den Durchlauf-160-Stand.
- `bash scripts/smoke.sh` ist grün.

---
