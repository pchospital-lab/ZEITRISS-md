---
title: "Issue-Pack Durchlauf 74 – Round4 Abschluss-Restdrift"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-08"
links:
  issue: "internal/qa/process/known-issues.md#zr-018-ruf-tier-progress-und-alienmystery-onboarding-als-ssot-nachziehen"
  statusmatrix: "internal/qa/process/ruf-alien-statusmatrix.md"
---

# Ziel

Nach Durchlauf 73 verbleibende SSOT-/Konsistenzreste aus dem Round-4-Review
gezielt schließen und den Anschlusslauf sauber dokumentieren.

1. Voice-Default im Kernmodul auf `gm_second_person` nachziehen.
2. Semver-Wording im Toolkit auf den kanonischen `zr`-Pfad schärfen
   (inkl. Legacy-Hinweis).
3. Pflicht-Smoke + Linkprüfung erneut fahren und dokumentieren.

# Checkliste

- [x] Restdrift im Kernmodul (`core/zeitriss-core.md`) behoben.
- [x] Start-Dispatcher-Wording in `systems/toolkit-gpt-spielleiter.md`
      auf `zr` + Legacy-Normalisierung harmonisiert.
- [x] Pflicht-Smoke ausgeführt.
- [x] Linklint ausgeführt.
- [x] Prozess-/Statusmatrix auf Durchlauf 74 ergänzt.

# Abschluss

Der Round-4-Abschlusslauf schließt verbleibende Textdrifts ohne neue
Regeländerung: Runtime-Default-Voice und Save-Semver-Sprache sind im geladenen
Kanon nun konsistent auf der v7-SSOT-Linie.
