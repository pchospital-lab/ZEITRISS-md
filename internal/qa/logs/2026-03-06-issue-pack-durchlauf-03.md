---
title: "QA-Log – Issue-Pack Durchlauf 03"
version: 0.1.0
tags: [qa, log]
---

# QA-Log – Issue-Pack Durchlauf 03

## Kontext
- Input: `uploads/ZEITRISS_codex_issue_pack.md`
- Fokus: Issue 1/2 (Save/Wallet-SSOT, Teil 1) + Issue 5 (Versionsdrift, Teil 1).

## Umgesetzter Scope

1. **Seed-Spiegel im Kampagnenmodul auf Arc-v7-Namen gezogen**
   - Referenzen wurden von `arc_dashboard.offene_seeds[]` auf
     `arc.open_seeds[]` umgestellt.
   - Das zugehörige Pseudocode-Beispiel nutzt denselben Spiegelpfad.

2. **Save-/Economy-Passagen im Save-Modul präzisiert**
   - Cross-Mode-Referenzpfade zeigen für persönliche Guthaben auf
     `characters[].wallet`.
   - Audit-Text und Scope-Hinweise benennen Charakter-Wallets statt
     `economy.wallets{}` als aktiven Standard.
   - Arc-Pflichtpfade wurden im Abschnitt auf `arc` +
     `open_seeds/factions/questions/timeline` ausgerichtet.

3. **Versionsfallback in runtime.js harmonisiert**
   - `ZR_VERSION`-Fallback wurde von 4.2.5 auf 4.2.6 angehoben,
     passend zu `package.json`.

## QA-Checks
- Pflichtcheck: `bash scripts/smoke.sh`.

## Offene Restpunkte (nächster Durchlauf)
1. `core/sl-referenz.md` vollständig auf Save-v7-Zielmodell konsolidieren
   (`characters[]`, `economy.hq_pool`, `arc`).
2. Drift-Guards in `tools/lint_runtime.py` ergänzen, damit Legacy-Tokens in
   aktiven Runtime-Passagen früh in CI auffallen.

## Status
- Durchlauf 03: **abgeschlossen**.
