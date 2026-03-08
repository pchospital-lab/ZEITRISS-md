---
title: "Issue-Pack Durchlauf 76 – HQ-Save/Reset Klarheit"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-08"
links:
  issue: "internal/qa/process/known-issues.md#zr-018-ruf-tier-progress-und-alienmystery-onboarding-als-ssot-nachziehen"
  statusmatrix: "internal/qa/process/ruf-alien-statusmatrix.md"
---

# Ziel

Rückfrage zur Save-Semantik präzise beantworten und die SSOT-Texte harmonisieren:

1. Klar markieren, dass Speichern ausschließlich im HQ erfolgt.
2. Klar markieren, dass `stress`/`psi_heat` im Debrief auf HQ-Basis zurückgesetzt
   werden, bevor ein HQ-Save entsteht.
3. Gleichzeitig dokumentieren, warum die Felder trotzdem im v7-Schema bleiben
   (expliziter HQ-Status + stabile Legacy-/Import-Normalisierung).
4. Pflicht-Smoke ausführen.

# Checkliste

- [x] Masterprompt um explizite HQ-Save/Reset-Invariante ergänzt.
- [x] `core/sl-referenz.md` bei Persistenzfeldern entsprechend präzisiert.
- [x] `systems/gameflow/speicher-fortsetzung.md` beim kanonischen Exportblock
      um dieselbe Invariante ergänzt.
- [x] Pflicht-Smoke ausgeführt.
- [x] Prozessanker auf Durchlauf 76 erweitert.

# Abschluss

Die Save-Semantik ist jetzt an allen drei SSOT-Orten konsistent: HQ-only Save,
Debrief-Reset vor Save und dennoch explizite Felder im Schema für Transparenz
und Migrationsstabilität.
