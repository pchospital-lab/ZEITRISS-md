---
title: "Issue-Pack Fahrplan – Durchlauf 49"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 49

Quelle: `uploads/ZEITRISS_v7_save_load_issue_pack.md` (Issue 6: Save-Größenbudget).

## Ziel

V7-Saves für lange Kampagnen (5er-Team, Highend) per dokumentiertem Rolling-Window
robust halten, ohne spielkritische Informationen zu verlieren.

## Scope dieses Durchlaufs

- `meta/masterprompt_v6.md`: Save-Budget-Caps + Prune-Regel (`summaries.*`) in
  die kanonischen v7-Regeln aufnehmen.
- `systems/gameflow/speicher-fortsetzung.md`: Kompakt-Profil um
  `summaries.*` ergänzen und feste Caps für Log-/Arc-/History-Felder dokumentieren.
- `core/sl-referenz.md`: Runtime-Kurzreferenz um Save-Budget-Regeln spiegeln.
- `README.md`: OpenWebUI-Hinweis für Save-Budget ergänzen.
- `internal/qa/process/known-issues.md`: ZR-017-Notiz auf Durchlauf 49 erweitern.
- Pflicht-Smoke ausführen.

## Exit-Kriterium

- Save-Budget ist konsistent in Masterprompt, Save-Doku, SL-Referenz und README
  beschrieben.
- `summaries.summary_last_episode`, `summary_last_rift`,
  `summary_active_arcs` sind als Prune-Ziel benannt.
- Pflicht-Smoke bleibt grün.
