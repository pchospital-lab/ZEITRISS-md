---
title: "Issue-Pack Durchlauf 118 – Kausalabfang Motiv-/Lagefenster-Hardening"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_never_happened_gadget_pack.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-117-kausalabfang-anti-retcon-wording-hardening.md"
---

# Ziel

Das Upload-Paket begrenzt den Kausalabfang nicht nur zeitlich (Sekunden bis
wenige Minuten), sondern auch kausal auf Fälle, in denen **Tatmotivation und
Einsatzlage** des Ziels noch dieselben bleiben.

1. Motiv-/Lage-Grenze in den fünf Kernmodulen explizit und parallel ergänzen.
2. Watchguard um einen Pflichtanker auf Motiv+Lage erweitern.
3. QA-/Prozessartefakte für Anschlusslauf 118 fortschreiben.

# Checkliste

- [x] `core/spieler-handbuch.md` enthält die Motiv-/Lage-Grenze im Kausalabfang-Block.
- [x] `core/sl-referenz.md` enthält denselben Motiv-/Lage-Anker im Standardmodul.
- [x] `systems/toolkit-gpt-spielleiter.md` führt Motiv-/Lage-Grenze bei den Voraussetzungen.
- [x] `meta/masterprompt_v6.md` trägt denselben Motiv-/Lage-Anker im Cleanup-Block.
- [x] `characters/ausruestung-cyberware.md` führt den Motiv-/Lage-Anker im Gadget-Flavor.
- [x] `tools/test_kausalabfang_watchguard.js` prüft Motiv+Lage als Pflichtanker.
- [x] `internal/qa/process/known-issues.md` um Evidenzlauf 118 ergänzt.
- [x] `internal/qa/process/continuity-redesign-statusmatrix.md` um Evidenzlauf 118 + Watchpoint ergänzt.
- [x] QA-Log für Durchlauf 118 angelegt.
- [x] `bash scripts/smoke.sh` erfolgreich ausgeführt.
- [x] `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` erfolgreich ausgeführt.

# Abschluss

Durchlauf 118 härtet das enge ITI-Abfangfenster kausal nach: Der Kausalabfang
bleibt auf Fälle begrenzt, in denen Zielmotivation und Einsatzlage nicht zu
alternativen Geschichtsverläufen kippen.
