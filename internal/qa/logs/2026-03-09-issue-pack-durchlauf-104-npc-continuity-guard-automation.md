---
title: "QA-Log 2026-03-09 – Durchlauf 104 (NPC-Continuity-Guard-Automation)"
status: "abgeschlossen"
run_id: "zr-019-d104"
---

# Kontext

Die Durchläufe 94–103 haben den NPC/MMO-Strang inhaltlich sauber verankert.
Offen war noch die Guard-Automatisierung für die NPC-spezifischen
Kontinuitätsanker, damit Folgeänderungen nicht nur per Review, sondern auch
im Pflicht-Smoke auffallen.

# Umgesetzte Änderungen

1. **Automatisierter NPC-Kontinuitäts-Guard ergänzt**
   - Datei: `tools/test_npc_continuity_consistency.js`
   - Prüft über die drei SSOT-Orte (`meta/masterprompt_v6.md`,
     `systems/gameflow/speicher-fortsetzung.md`, `core/sl-referenz.md`) die
     Pflichtanker `npc_roster`, `active_npc_ids`, Scope-Enum
     (`personal|session|iti`) und die Mensch-vor-NPC-Slotregel.
   - Validiert zusätzlich ein NPC-Contract-Fixture (Budgets, Status-Enum,
     Leave-Zuordnung, kompakter Cross-Pollination-Beat).

2. **Fixture für NPC-Join/Leave/Cross-Pollination ergänzt**
   - Datei: `internal/qa/fixtures/npc_continuity_output_contract.json`
   - Enthält einen Mehrfach-Load-Fall mit Personal- und Session-NPC,
     Slotauflösung (Teamgröße 5, Menschen zuerst), Leave-Auflösung
     (`personal` mit Owner, `session` beim Session-Anker) und einem
     kompakten Offscreen-Rückkehrbeat.

3. **Pflicht-Smoke erweitert**
   - Datei: `scripts/smoke.sh`
   - Neuer Block `node tools/test_npc_continuity_consistency.js` ist jetzt
     fester Bestandteil der CI-Smoke-Strecke.

4. **Prozessdoku aktualisiert**
   - Dateien:
     - `internal/qa/process/known-issues.md`
     - `internal/qa/process/continuity-redesign-statusmatrix.md`
   - Evidenzlauf 104 dokumentiert und Watchpoint für NPC-v7-Felder auf
     „automatisiert im Smoke“ gehoben.

5. **Fahrplanlauf dokumentiert**
   - Datei:
     `internal/qa/plans/issue-pack-durchlauf-104-npc-continuity-guard-automation.md`

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**
2. `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`
   - Ergebnis: **grün**

# Bewertung

Der NPC-Kontinuitätsstrang ist nun nicht nur textlich harmonisiert, sondern
mit einem dedizierten Pflicht-Guard abgesichert. Damit sinkt das Risiko,
dass spätere Save-v7-/Kontinuitätsänderungen die MMO-Persistenzregeln
unbemerkt aufweichen.
