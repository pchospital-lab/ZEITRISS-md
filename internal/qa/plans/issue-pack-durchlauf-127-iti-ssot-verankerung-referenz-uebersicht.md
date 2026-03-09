---
title: "Issue-Pack Durchlauf 127 – ITI-SSOT-Verankerung in Referenz + Kampagnenübersicht"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_ITI_mmo_konsistenz_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-126-iti-hq-pflichtbeat-restdrift-core.md"
---

# Ziel

Den ITI-Hauskanon im aktiven Referenzslot und in der Kampagnenübersicht weiter
härten: Pflicht-Heimkehr-Beat in der SL-Referenz explizit machen und
player-facing Atlas + Kernpersonal auch im Kampagnenmodul als Runtime-SSOT
sichtbar verankern.

# Checkliste

- [x] Restdrift per Repo-Scan geprüft (HQ-Heimkehr-/ITI-Atlas-Anker in aktiven Modulen).
- [x] `core/sl-referenz.md` um Pflicht-Heimkehr-Beat + ITI-Lage-Zeile ergänzt.
- [x] `core/sl-referenz.md` um ITI-Atlas/Kernpersonal als Runtime-SSOT ergänzt.
- [x] `gameplay/kampagnenuebersicht.md` um ITI-Hardcanon-Abschnitt (Atlas + Kernpersonal + Single/Multi-Konsistenz) ergänzt.
- [x] QA-Log für Durchlauf 127 angelegt.
- [x] `bash scripts/smoke.sh` erfolgreich ausgeführt.
- [x] `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` erfolgreich ausgeführt.

# Abschluss

Durchlauf 127 stärkt die ITI/MMO-Konsistenz im Runtime-SSOT entlang der
Spielerführung: die Referenz erzwingt den Heimkehr-Beat klarer, und die
Kampagnenübersicht trägt denselben festen Atlas und dasselbe Kernpersonal in den
sichtbaren Hauskanon.
