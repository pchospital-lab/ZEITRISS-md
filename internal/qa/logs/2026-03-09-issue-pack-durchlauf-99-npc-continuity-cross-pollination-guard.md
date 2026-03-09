---
title: "QA-Log 2026-03-09 – Durchlauf 99 (NPC-Kontinuität Cross-Pollination-Guard)"
status: "abgeschlossen"
run_id: "zr-019-d99"
---

# Kontext

Nach Durchlauf 98 war das NPC-Schema formal in allen Kernmodulen enthalten,
aber der Upload-Review ließ bei den Verhaltensregeln noch Restspielraum:
Join/Leave-Zuordnung (`personal|session|iti`) und die Form der
Offscreen-Fortwirkung waren nicht überall gleich explizit als Guard-Text
formuliert.

# Umgesetzte Änderungen

1. **Masterprompt um Verhaltensguard ergänzt**
   - `meta/masterprompt_v6.md`
   - Join/Leave-Regel ergänzt: `personal` folgt `owner_id`, `session` bleibt am
     Session-Anker, `iti` fällt auf Hintergrundstatus, Scope-Wechsel nur mit
     sichtbarem Inworld-Transfer-Beat.
   - Cross-Pollination-Regel ergänzt: genau eine kompakte Rückkehrfortschreibung
     (Auftrag + Veränderung + Hook), typischerweise Gerücht/Wunde/Gegenstand/
     Boss-Tell/Haltungswechsel.

2. **Speichermodul um expliziten Beat erweitert**
   - `systems/gameflow/speicher-fortsetzung.md`
   - Neuer Pflichtbeat `NPC-Cross-Pollination` ergänzt (max. 1 Hook), damit der
     Kontinuitätsrückblick bei Offscreen-NPCs nicht in unscharfes Fluff driftet.

3. **SL-Referenz-Guard nachgezogen**
   - `core/sl-referenz.md`
   - Save-v7-Hinweisblock ergänzt um Join/Leave-Guard und die
     Ein-Satz-Offscreen-Rückkehrregel für NPCs.

4. **QA-Prozessdoku aktualisiert**
   - `internal/qa/process/known-issues.md`
   - `internal/qa/process/continuity-redesign-statusmatrix.md`
   - Durchlauf 99 als Evidenzlauf und Watchpoint-Erweiterung dokumentiert.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**

2. `python3 tools/lint_links.py meta/masterprompt_v6.md core systems/gameflow internal/qa/plans internal/qa/logs internal/qa/process`
   - Ergebnis: **grün**

# Bewertung

Der NPC-Kontinuitätsstrang ist damit nicht nur strukturell, sondern auch
verhaltensseitig konsistent: Übergänge zwischen Solo/Gruppe bleiben narrativ
sichtbar, und Offscreen-Fortschreibung bleibt kompakt und anschlussfähig.
