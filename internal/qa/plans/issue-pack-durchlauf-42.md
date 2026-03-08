---
title: "Issue-Pack Fahrplan – Durchlauf 42"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 42

Quelle: Follow-up zu `uploads/ZEITRISS_v7_save_load_issue_pack.md` + Maintainer-Rückfrage zum 5er→3/2-Split mitten in einer Episode.

## Ziel

Den Mid-Episode-Fall ohne Branch-Protokoll unmissverständlich festlegen:
- Was ist kanonisch, wenn sich eine 5er-Gruppe nach 1-2 Missionen trennt?
- Was passiert mit der abgetrennten 2er-Gruppe in neuem Chat?
- Wann und wie ist der Rejoin zulässig?

## Scope dieses Durchlaufs

- Präzisierung in `systems/gameflow/speicher-fortsetzung.md`, `meta/masterprompt_v6.md`, `core/sl-referenz.md`, `README.md`.
- Explizite Aussage „kein automatischer Episoden-Sprung für Solist:innen“.
- Pflicht-Smoke als Regression-Gate.

## Exit-Kriterium

- Der 5er→3/2-Fall ist in allen Leitquellen konsistent beschrieben.
- Host-Run als kanonische Quelle bleibt eindeutig.
- Pflicht-Smoke bleibt grün.
