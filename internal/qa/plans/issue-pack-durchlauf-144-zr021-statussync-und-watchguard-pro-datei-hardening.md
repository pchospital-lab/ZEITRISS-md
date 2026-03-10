---
title: "Issue-Pack Durchlauf 144 - ZR-021 Status-Sync und Onboarding-Watchguard pro Datei härten"
version: 1.0.0
tags: [qa, plan, onboarding, mmo]
---

# Ziel

Anschlusslauf zu ZR-021: Der Onboarding-Track soll vor dem nächsten
Deepsearch-Lauf sowohl **prozessual** als auch **technisch** auf einen klaren
Abschlussstand gebracht werden.

## Scope

- `tools/test_onboarding_start_save_watchguard.js`
- `internal/qa/process/known-issues.md`
- QA-Log für Durchlauf 144

## Checkliste

1. Onboarding-Watchguard für Startvertrag/HQ-Hinweise um pro-Datei-Pflichtchecks
   ergänzen (nicht nur Mindesttreffer).
2. Fehlermeldungen so formulieren, dass Regel + betroffene Datei direkt
   erkennbar sind.
3. ZR-021 in `known-issues.md` auf konsistenten Durchlauf-Stand 140-144
   synchronisieren und den Deepsearch-Übergabestatus klar markieren.
4. Pflicht-Smoke ausführen (`bash scripts/smoke.sh`).
5. Link-Lint für geänderte Doku-/QA-Dateien ausführen.

## Abschlusskriterien

- Watchguard schlägt bei Drift einzelner SSOT-Dateien zuverlässig an.
- ZR-021 ist in der Prozessspur als synchronisierter Übergabestand dokumentiert.
- Pflicht-Smoke bleibt grün.
