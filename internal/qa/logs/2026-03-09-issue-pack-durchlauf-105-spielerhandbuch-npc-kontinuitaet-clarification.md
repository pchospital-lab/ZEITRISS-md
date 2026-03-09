---
title: "QA-Log 2026-03-09 – Durchlauf 105 (Spielerhandbuch NPC-Kontinuitätsklarstellung)"
status: "abgeschlossen"
run_id: "zr-019-d105"
---

# Kontext

Die Durchläufe 94–104 haben den NPC-Kontinuitätsstrang im technischen Kern
vollständig abgesichert (Schema, Guards, Join/Leave, Cross-Pollination,
Physicality). Im Spieler-Handbuch war `npc-team` bislang primär als
Startsyntax beschrieben. Für Anschlussklarheit im Player-Pfad wurde eine
kompakte Kontinuitätsnotiz ergänzt.

# Umgesetzte Änderungen

1. **Spieler-Handbuch um NPC-Kontinuitätsnotiz ergänzt**
   - Datei: `core/spieler-handbuch.md`
   - Ergänzt unter den Startbefehlen:
     - bekannte NPC-Chrononauten bleiben als Kontinuitätsakteure erhalten
       (HQ/Funk/Offscreen statt stilles Verschwinden),
     - Menschen zählen zuerst gegen Teamgröße 5,
     - abwesende NPCs bringen beim Wiedersehen eine kurze
       Offscreen-Fortschreibung (Auftrag + Veränderung + Hook).

2. **Prozessdoku aktualisiert**
   - Dateien:
     - `internal/qa/process/known-issues.md`
     - `internal/qa/process/continuity-redesign-statusmatrix.md`
   - Evidenzlauf 105 ergänzt und als Follow-up-Klarstellung im
     NPC/MMO-Block dokumentiert.

3. **Fahrplanlauf dokumentiert**
   - Datei:
     `internal/qa/plans/issue-pack-durchlauf-105-spielerhandbuch-npc-kontinuitaet-clarification.md`

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**
2. `python3 tools/lint_links.py core/spieler-handbuch.md internal/qa/plans internal/qa/logs internal/qa/process`
   - Ergebnis: **grün**

# Bewertung

Der NPC/MMO-Strang ist damit nun auch auf der Spieleroberfläche sauber
angeschlossen: Die Startsyntax `npc-team` trägt explizit die gleiche
Persistenzphilosophie wie die technischen SSOT-Module.
