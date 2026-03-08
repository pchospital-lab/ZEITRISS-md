---
title: "QA-Log 2026-03-08 – Durchlauf 79 (Round4 Anschluss: SSOT-Feldnamen)"
status: "abgeschlossen"
run_id: "zr-018-d79"
---

# Kontext

Nach den Round-4-Anschlussläufen 73–78 blieb ein kleiner, aber unnötiger
Terminologie-Drift in Runtime-Pseudocode/Dev-Checklisten sichtbar:
`open_seeds` wurde punktuell noch als Kurzform verwendet, obwohl der
kanonische Pfad `campaign.rift_seeds` lautet.

# Umgesetzte Änderungen

1. **Toolkit-Pseudocode harmonisiert**
   - `systems/toolkit-gpt-spielleiter.md`: Im Makro `StartGroupMode` wurde der
     Reset von `state.open_seeds = []` auf den kanonischen Pfad
     `state.campaign.rift_seeds = []` umgestellt; zusätzlich wird der
     Legacy-/Dashboard-Spiegel `state.arc.open_seeds = []` explizit mitgeführt.

2. **Dev-Checkliste auf SSOT-Feldnamen gezogen**
   - `gameplay/kampagnenstruktur.md`: Die Formeln nutzen jetzt
     `len(campaign.rift_seeds)` statt der ungebundenen Kurzform `open_seeds`.

3. **QA-Dokumentation aktualisiert**
   - Neuer Fahrplan: `internal/qa/plans/issue-pack-durchlauf-79-round4-ssot-feldnamen-restdrift.md`
   - Dieses QA-Log dokumentiert den Anschlusslauf.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**

2. `python3 tools/lint_links.py core characters gameplay systems meta/masterprompt_v6.md README.md`
   - Ergebnis: **grün** (alle geprüften Links vorhanden)

# Bewertung

- Keine Regeländerung und kein Balance-Eingriff.
- SSOT-Leseführung für Rift-Seed-Felder wurde in Pseudocode und Dev-Hinweisen
  konsistent nachgezogen.
