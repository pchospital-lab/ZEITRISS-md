---
title: "Issue-Pack Fahrplan – Durchlauf 50"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 50

Quelle: `uploads/ZEITRISS_v7_save_load_issue_pack.md` (Issue 8: Px-Regel bei Split/Merge).

## Ziel

Den Paradoxon-Index für Split/Merge deterministisch machen, damit ein bereits
verbrauchter Px-5-Zustand nicht durch spätere Branch-Merges wieder auftaucht.

## Scope dieses Durchlaufs

- `meta/masterprompt_v6.md`: v7-Schema um `campaign.px_state` erweitern und
  Merge-Priorität (`consumed > pending_reset > stable`) dokumentieren.
- `systems/gameflow/speicher-fortsetzung.md`: Kompakt-Profil, Split/Merge-Regeln
  und Px-Abschnitt auf denselben Zustandslauf schärfen.
- `core/sl-referenz.md`: Persistentes Schema + Split/Merge-Kurzreferenz um den
  Px-Zustands-Guard ergänzen.
- `README.md`: Multiplayer-Merge-Hinweis um den Px-State-Guard erweitern.
- `internal/qa/process/known-issues.md`: ZR-017-Notiz auf Durchlauf 50 fortschreiben.
- Pflicht-Smoke ausführen.

## Exit-Kriterium

- `campaign.px_state` ist in Masterprompt, Save-Doku und SL-Referenz
  konsistent benannt (`stable|pending_reset|consumed`).
- Merge-Regel ist überall gleich: `consumed > pending_reset > stable`.
- Pflicht-Smoke bleibt grün.
