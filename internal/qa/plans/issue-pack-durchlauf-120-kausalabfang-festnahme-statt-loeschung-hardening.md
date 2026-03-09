---
title: "Issue-Pack Durchlauf 120 – Kausalabfang Festnahme-statt-Löschung Hardening"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_never_happened_gadget_pack.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-119-housekeeping-vor-deepsearch.md"
---

# Ziel

Den Upload-Anker „Cleanup statt Zauber / Festnahme statt Löschung" als explizites
Leitmotiv SSOT-weit absichern, damit Kausalabfang in Anschlussläufen nicht in
Lösch-/Retcon-Sprache zurückkippt.

1. Leitmotiv in allen fünf Kausalabfang-Kernmodulen explizit setzen.
2. Watchguard um einen positiven Pflichtregex „Festnahme statt Löschung" erweitern.
3. Prozessdoku (Plan/Log/known-issues/Statusmatrix) synchron ergänzen.

# Checkliste

- [x] `core/spieler-handbuch.md` auf Leitmotiv „Festnahme statt Löschung" ergänzt.
- [x] `core/sl-referenz.md` auf Leitmotiv „Festnahme statt Löschung" ergänzt.
- [x] `systems/toolkit-gpt-spielleiter.md` auf Leitmotiv „Festnahme statt Löschung" ergänzt.
- [x] `meta/masterprompt_v6.md` auf Leitmotiv „Festnahme statt Löschung" ergänzt.
- [x] `characters/ausruestung-cyberware.md` auf Leitmotiv „Festnahme statt Löschung" ergänzt.
- [x] `tools/test_kausalabfang_watchguard.js` um Pflichtregex erweitert.
- [x] QA-Log für Durchlauf 120 angelegt.
- [x] `bash scripts/smoke.sh` erfolgreich ausgeführt.
- [x] `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` erfolgreich ausgeführt.

# Abschluss

Durchlauf 120 schärft das Kausalabfang-Leitmotiv semantisch nach und verankert
es gleichzeitig als CI-pflichtigen Driftguard.
