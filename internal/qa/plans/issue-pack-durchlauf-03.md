---
title: "Issue-Pack Fahrplan – Durchlauf 03"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 03

Quelle: `uploads/ZEITRISS_codex_issue_pack.md`

## Ziel
Den Save-/Wallet-SSOT weiter in Richtung **v7-Einheitsmodell** ziehen und
sichtbare Legacy-Dialekte in Runtime-Modulen reduzieren.

## Scope dieses Durchlaufs

- C1 Save-SSOT + Wallet (P0, Teil 1)
  - Referenzen auf `arc_dashboard.offene_seeds[]` in aktiven Runtime-Texten auf
    `arc.open_seeds[]` umstellen.
  - Save-/Economy-Texte in `speicher-fortsetzung.md` auf
    `characters[].wallet` + `economy.hq_pool` präzisieren.
  - Boss-DR-Rosterhinweis auf `characters[]` vereinheitlichen.

- C5 Versionsdrift (P1, Teil 1)
  - `runtime.js`-Fallback für `ZR_VERSION` auf 4.2.6 angleichen.

## Nicht im Scope (bewusst verschoben)

- Vollständige Bereinigung aller Legacy-Hinweise in `core/sl-referenz.md`
  (großer Block, folgt in Durchlauf 04).
- Laufzeit-Migrationen in `runtime.js` (Importpfad bleibt unverändert).

## Exit-Kriterium für Durchlauf 03

- Geänderte Runtime-Module nutzen für aktive Seed-Spiegel den Arc-v7-Namen
  `arc.open_seeds[]`.
- Save-/Economy-Passagen im Durchlauf-Scope referenzieren das Zielmodell
  `characters[].wallet` + `economy.hq_pool`.
- Pflichtcheck `bash scripts/smoke.sh` ist grün.
