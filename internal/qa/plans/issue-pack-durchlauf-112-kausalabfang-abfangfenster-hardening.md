---
title: "Issue-Pack Durchlauf 112 – Kausalabfang Abfangfenster-Hardening"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_never_happened_gadget_pack.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-111-kausalabfang-watchguard-hardening-infra.md"
---

# Ziel

Die Upload-Empfehlung nennt das ITI-Abfangfenster explizit als **eng begrenzte
Rückholung (Sekunden bis wenige Minuten)**. Dieser Zeitrahmen soll als
SSOT-Anker + Smoke-Guard abgesichert werden.

1. Abfangfenster-Wording in den Kernmodulen nachziehen.
2. Watchguard um den neuen Pflichtanker erweitern.
3. Prozessdoku + QA-Log für Anschlusslauf 112 aktualisieren.

# Checkliste

- [x] `core/spieler-handbuch.md` um den Zeitfenster-Anker (Sekunden bis wenige Minuten) ergänzt.
- [x] `systems/toolkit-gpt-spielleiter.md` um den Zeitfenster-Anker ergänzt.
- [x] `meta/masterprompt_v6.md` um den Zeitfenster-Anker ergänzt.
- [x] `tools/test_kausalabfang_watchguard.js` um Abfangfenster-Regex erweitert.
- [x] `internal/qa/process/known-issues.md` um Evidenzlauf 112 ergänzt.
- [x] `internal/qa/process/continuity-redesign-statusmatrix.md` um Evidenzlauf 112 + Watchpoint ergänzt.
- [x] QA-Log für Durchlauf 112 angelegt.
- [x] `bash scripts/smoke.sh` erfolgreich ausgeführt.
- [x] `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` erfolgreich ausgeführt.

# Abschluss

Durchlauf 112 verhindert, dass das Kausalabfang-Modul bei späteren
Textänderungen in ein zu weites Retcon-Fenster driftet. Die kurze
ITI-Rückholspanne ist jetzt in SSOT + CI gemeinsam verankert.
