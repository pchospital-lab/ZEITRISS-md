---
title: "Issue-Pack Durchlauf 146 - Hard-Final-Review Regie-SSOT-Watchguard"
version: 1.0.0
tags: [qa, plan, runtime, ssot, watchguard]
---

# Ziel

Anschluss auf Durchlauf 145: Regie-Layer nicht nur im Toolkit, sondern
parallel im Masterprompt und in der SL-Referenz als SSOT-Pflichtbeat
verankern und per Smoke-Watchguard gegen künftigen Drift absichern.

## Scope

- `meta/masterprompt_v6.md`
- `core/sl-referenz.md`
- `systems/gameflow/cinematic-start.md`
- `tools/test_director_layer_watchguard.js`
- `scripts/smoke.sh`
- `internal/qa/process/known-issues.md`
- QA-Log für Durchlauf 146

## Checkliste

1. Regie-Layer-Formulierung (ein Relevanzsatz vor Briefing, eine
   ITI-Bulletin-Mikronachricht nach Heimkehr) im Masterprompt ergänzen.
2. Dieselben Pflichtbeats in der SL-Referenz sichtbar nachziehen.
3. Runtime-Defaultpfad in `cinematic-start.md` im Einstiegskapitel
   explizit markieren (kanonisch vs. optionale Varianten).
4. Neuen Smoke-Watchguard für Regie-Layer bauen und in
   `scripts/smoke.sh` aufnehmen.
5. Pflicht-Smoke ausführen (`bash scripts/smoke.sh`).

## Anschluss / Offene Watchpoints

- Falls später weitere Start-/Flowmodule den Regie-Layer aufnehmen, den
  neuen Watchguard auf diese Dateien erweitern.
- Bei künftigen SSOT-Rundläufen prüfen, ob der Relevanzsatz in
  spieler-sichtiger Doku (Handbuch) als Soft-Formulierung ergänzt werden
  soll, ohne den Einstieg zu überfrachten.
