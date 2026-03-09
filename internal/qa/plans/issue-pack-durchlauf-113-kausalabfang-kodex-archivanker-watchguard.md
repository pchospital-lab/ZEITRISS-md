---
title: "Issue-Pack Durchlauf 113 – Kausalabfang Kodex-Archivanker-Watchguard"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_never_happened_gadget_pack.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-112-kausalabfang-abfangfenster-hardening.md"
---

# Ziel

Die Upload-Vorlage enthält den Kodex-Satz `Lokale Erinnerung driftet. Archivanker
aktiv.` als wichtige Ton-/Physikalitätsleitplanke für Mandela-/Nachhall-Effekte.
Dieser Satz soll als expliziter Hardening-Anker in SSOT + Watchguard verankert
werden.

1. Kodex-Defaults in Toolkit und Masterprompt synchronisieren.
2. Watchguard um einen Pflicht-Regex für den Archivanker ergänzen.
3. Prozess-/QA-Artefakte für Anschlusslauf 113 fortschreiben.

# Checkliste

- [x] `systems/toolkit-gpt-spielleiter.md` um den Kodex-Archivanker ergänzt.
- [x] `meta/masterprompt_v6.md` um den gleichen Kodex-Archivanker ergänzt.
- [x] `tools/test_kausalabfang_watchguard.js` um Archivanker-Regex erweitert.
- [x] `internal/qa/process/known-issues.md` um Evidenzlauf 113 ergänzt.
- [x] `internal/qa/process/continuity-redesign-statusmatrix.md` um Evidenzlauf 113 + Watchpoint ergänzt.
- [x] QA-Log für Durchlauf 113 angelegt.
- [x] `bash scripts/smoke.sh` erfolgreich ausgeführt.
- [x] `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` erfolgreich ausgeführt.

# Abschluss

Durchlauf 113 hält den Kausalabfang-Kodexton technisch-trocken und verhindert,
dass Memory-Drift künftig nur implizit oder spektakelig formuliert wird. Der
Archivanker ist jetzt als Pflichtcheck in SSOT + Smoke verankert.
