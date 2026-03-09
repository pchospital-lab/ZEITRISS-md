---
title: "Issue-Pack Durchlauf 108 – Kausalabfang/\"Never happened\" Integration"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_never_happened_gadget_pack.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-107-physicality-watchguard-automation.md"
---

# Ziel

Das Upload-Paket `ZEITRISS_never_happened_gadget_pack.md` als konsistente,
strikt begrenzte Cleanup-Regel in den WS-Kerntexten verankern, ohne neue
Subsysteme einzuführen.

1. Spielernahe Regel im Handbuch verankern (nach 0 LP, Cleanup statt Zauber).
2. SL-/Toolkit-Leitplanken für Anwendung, Reihenfolge und Sperren ergänzen.
3. Masterprompt auf dieselbe Reihenfolge + Verbotsmatrix harmonisieren.
4. Ausrüstungs-Flavour als ITI-Standardmodul dokumentieren (nicht shopbar).
5. QA-Prozessdoku um Evidenzlauf 108 ergänzen.

# Checkliste

- [x] `core/spieler-handbuch.md` um Kausalabfang-Regel ergänzt.
- [x] `core/sl-referenz.md` Standardausrüstung + Cleanup-Reihenfolge ergänzt.
- [x] `systems/toolkit-gpt-spielleiter.md` um Kausalabfang-Guard erweitert.
- [x] `meta/masterprompt_v6.md` Cleanup-Regel (Loot → Kausalabfang → Cleanup) ergänzt.
- [x] `characters/ausruestung-cyberware.md` Flavor-Eintrag als ITI-Standardmodul ergänzt.
- [x] `internal/qa/process/continuity-redesign-statusmatrix.md` um Lauf 108 ergänzt.
- [x] `internal/qa/process/known-issues.md` um Lauf 108 ergänzt.
- [x] `bash scripts/smoke.sh` erfolgreich ausgeführt.
- [x] `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` erfolgreich ausgeführt.

# Abschluss

Durchlauf 108 verankert den Kausalabfang als enges ITI-Cleanup-Protokoll
(klarer 0-LP-Trigger, klare Sperren, klare Reihenfolge) über Handbuch,
SL-Referenz, Toolkit, Masterprompt und Ausrüstungsmodul hinweg.
