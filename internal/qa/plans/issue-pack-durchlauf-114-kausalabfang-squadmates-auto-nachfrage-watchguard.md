---
title: "Issue-Pack Durchlauf 114 – Kausalabfang Squadmates/Auto-Nachfrage-Watchguard"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_never_happened_gadget_pack.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-113-kausalabfang-kodex-archivanker-watchguard.md"
---

# Ziel

Die Upload-Leitplanken fordern einerseits die harte Sperre für **Squadmates**,
andererseits die klare KI-Regel **unnamed automatisch / named nachfragen**. Beide
Anker stehen bereits in SSOT-Texten, waren im Watchguard aber noch nicht als
Pflichtregex verankert.

1. Kausalabfang-Watchguard um den `Squadmates`-Sperranker ergänzen.
2. Kausalabfang-Watchguard um den Auto-/Nachfrage-Anker erweitern.
3. QA-/Prozessartefakte für Anschlusslauf 114 fortschreiben.

# Checkliste

- [x] `tools/test_kausalabfang_watchguard.js` prüft `Squadmates` als Pflichtanker in allen Kerndateien.
- [x] `tools/test_kausalabfang_watchguard.js` prüft in strikten Dateien die Regel `Unbenannte Hostiles automatisch, benannte Ziele nachfragen`.
- [x] `internal/qa/process/known-issues.md` um Evidenzlauf 114 ergänzt.
- [x] `internal/qa/process/continuity-redesign-statusmatrix.md` um Evidenzlauf 114 + Watchpoint ergänzt.
- [x] QA-Log für Durchlauf 114 angelegt.
- [x] `bash scripts/smoke.sh` erfolgreich ausgeführt.
- [x] `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` erfolgreich ausgeführt.

# Abschluss

Durchlauf 114 schließt zwei verbliebene Driftlücken in der Guard-Automation:
`Squadmates` ist jetzt als explizite Sperre testseitig erzwungen und die
Auto-vs.-Nachfrage-Regel für unbenannte/benannte Ziele wird in Toolkit +
Masterprompt bei Folgeänderungen aktiv mitvalidiert.
