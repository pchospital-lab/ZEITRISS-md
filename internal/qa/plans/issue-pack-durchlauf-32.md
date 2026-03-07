---
title: "Issue-Pack Fahrplan – Durchlauf 32"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 32

Quelle: Fortsetzung ZR-016 mit Fokus auf Restdrift im Load-/Koop-Text von
`systems/gameflow/speicher-fortsetzung.md`.

## Ziel

Aktive Ablauftexte im Save-Modul auf v7-Zielmodell ziehen, damit kein
Betriebsfluss mehr Legacy-Pfade als Standard suggeriert:
- `load_deep()` beschreibt v7-Zielstruktur statt v6-Struktur,
- Multi-Import/Mid-Session-Merge referenzieren `economy.hq_pool` und `characters[]`,
- Wallet-Split-Sektion nutzt `characters[].wallet` statt Legacy-Container.

## Scope dieses Durchlaufs

- `systems/gameflow/speicher-fortsetzung.md`
- QA-Nachführung: Log + Known-Issues-Update

## Nicht im Scope

- Umbau der Runtime-Implementierung in `runtime.js`.
- Entfernung aller Legacy-Migrationsbeispiele aus dem Save-Modul.
- Änderungen an Mission-/Balance-Regeln.

## Exit-Kriterium für Durchlauf 32

- Load-/Merge-Abschnitte nennen nur v7-Zielpfade als aktiven Fluss.
- Wallet-Split/Hazard-Pay referenziert `characters[].wallet` + `economy.hq_pool`.
- `bash scripts/smoke.sh` läuft vollständig grün.
