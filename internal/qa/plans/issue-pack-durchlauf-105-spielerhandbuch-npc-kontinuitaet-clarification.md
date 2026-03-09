---
title: "Issue-Pack Durchlauf 105 – Spielerhandbuch NPC-Kontinuitätsklarstellung"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_npc_mmo_immersion_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-104-npc-continuity-guard-automation.md"
---

# Ziel

Den letzten Spielerpfad-Rest im NPC/MMO-Strang schließen: Das
Spieler-Handbuch soll `npc-team` nicht nur als Startsyntax nennen, sondern die
persistente NPC-Kontinuitätslogik auch kurz und klar im Player-Wording
abbilden.

1. `core/spieler-handbuch.md` um eine kompakte NPC-Kontinuitätsnotiz ergänzen
   (Menschen-vor-NPC-Slotregel, HQ/Offscreen-Fortbestand, kompakte
   Offscreen-Fortschreibung).
2. Prozessdoku um Evidenzlauf 105 ergänzen.
3. Pflicht-Smoke und Linkprüfung erneut ausführen.

# Checkliste

- [x] `core/spieler-handbuch.md` um Player-Notiz zur NPC-Kontinuität ergänzt.
- [x] `internal/qa/process/known-issues.md` um Durchlauf 105 ergänzt.
- [x] `internal/qa/process/continuity-redesign-statusmatrix.md` um Evidenzlauf 105 ergänzt.
- [x] QA-Log für Durchlauf 105 angelegt.
- [x] `bash scripts/smoke.sh` erfolgreich ausgeführt.
- [x] `python3 tools/lint_links.py core/spieler-handbuch.md internal/qa/plans internal/qa/logs internal/qa/process` erfolgreich ausgeführt.

# Abschluss

Durchlauf 105 schließt die verbleibende Formulierungslücke im
Spieler-Handbuch. Damit ist die NPC-Persistenzlogik nicht nur im technischen
SSOT (Masterprompt/Save/Toolkit/SL-Referenz), sondern auch im
spieler-sichtigen Startpfad konsistent sichtbar.
