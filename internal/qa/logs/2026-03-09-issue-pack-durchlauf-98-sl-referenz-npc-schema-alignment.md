---
title: "QA-Log 2026-03-09 – Durchlauf 98 (SL-Referenz NPC-Schema-Alignment)"
status: "abgeschlossen"
run_id: "zr-019-d98"
---

# Kontext

Die Durchläufe 94-97 haben NPC-Persistenz in Masterprompt, Speichermodul,
Toolkit, Cinematic-Start und Kampagnenstruktur verankert. In
`core/sl-referenz.md` war die technische Save-v7-Kurzreferenz jedoch noch ohne
den expliziten `continuity`-Block für `npc_roster[]`/`active_npc_ids[]` und
ohne die zugehörigen Budget-/Slot-Regeln.

# Umgesetzte Änderungen

1. **Save-v7-Kurzreferenz erweitert (continuity + NPC-Felder)**
   - `core/sl-referenz.md`
   - `continuity{last_seen, split, roster_echoes, shared_echoes,
     convergence_tags, npc_roster[], active_npc_ids[]}` in den
     Referenz-Block aufgenommen.

2. **NPC-Budget- und Enum-Regeln in der Referenz ergänzt**
   - `core/sl-referenz.md`
   - Kontinuitäts-Budgets (`roster_echoes/shared_echoes/convergence_tags/
     npc_roster/active_npc_ids`) ergänzt.
   - NPC-Scope (`personal|session|iti`) und Status-Enum
     (`attached|hq|assigned|recovering|missing|rival`) dokumentiert.

3. **Mischgruppen-Regel als Guard-Hinweis nachgezogen**
   - `core/sl-referenz.md`
   - Mensch-vor-NPC-Slotlogik + Pflicht-NPC-Lagebild im
     Kontinuitätsrückblick explizit genannt.

4. **Anschlussfähigkeit im QA-Prozess aktualisiert**
   - `internal/qa/process/known-issues.md`
   - `internal/qa/process/continuity-redesign-statusmatrix.md`
   - Durchlauf 98 als Evidenzlauf für „SL-Referenz-Alignment“ ergänzt.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**

2. `python3 tools/lint_links.py core internal/qa/plans internal/qa/logs internal/qa/process`
   - Ergebnis: **grün**

# Bewertung

Die SL-Referenz ist nun wieder auf derselben NPC-Kontinuitätsbasis wie die
anderen SSOT-nahen Module. Das reduziert Folgedrift bei Review, Playtest und
späteren Save-v7-Änderungen.
