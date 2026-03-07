---
title: "QA-Log – Issue-Pack Durchlauf 16"
date: 2026-03-06
scope: "Issue 13: Item-Registry-Layer (non-breaking SSOT-Schritt)"
status: abgeschlossen
tags: [qa, log]
---

## Quelle
- Externer Pack `uploads/ZEITRISS_codex_issue_pack.md`, Schwerpunkt Issue 13
  (kanonische Item-Registry für Gear/Implantate/Artefakte).
- Folgearbeit nach Durchlauf 15, um verbleibende Strukturdrifts im
  Equipment-Wording zu reduzieren.

## Umsetzung in diesem Durchlauf

1. **Registry-SSOT ergänzt (`characters/ausruestung-cyberware.md`)**
   - Kanonisches Registry-Muster aufgenommen (`id`, `display_name`, `type`,
     `tier`, `cost`, optional `tags`/`alt_skin`).
   - Save-Kompatibilität explizit festgezogen: Pflicht bleibt
     `equipment[{name,type,tier}]`.
   - Optionale Zusatzfelder `item_id` und `skin` als Alias-/Registry-Bridge
     dokumentiert.

2. **Masterprompt nachgezogen (`meta/masterprompt_v6.md`)**
   - Equipment-Regel um optionales `item_id`/`skin` ergänzt,
     ohne das Save-v7-Pflichtformat zu ändern.

3. **SL-Referenz synchronisiert (`core/sl-referenz.md`)**
   - Persistentes Save-Schema ergänzt auf
     `equipment:[{name,type,tier,item_id?,skin?}]` als kompatiblen
     Erweiterungspfad.

4. **QA-Nachführung**
   - Fahrplan/Log für Durchlauf 16 ergänzt.
   - `internal/qa/process/known-issues.md` (ZR-016) um Durchlauf 16 erweitert.

## Checks
- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
