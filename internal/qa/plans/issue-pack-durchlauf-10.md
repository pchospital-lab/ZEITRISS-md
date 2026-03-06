---
title: "Issue-Pack Fahrplan – Durchlauf 10"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 10

Quelle: `uploads/ZEITRISS_codex_issue_pack.md`

## Ziel
Kurskorrektur zu Issue 9 gemäß Maintainer-Feedback: Psi bleibt
**Weltstandard**, während die aktive Nutzung weiter charakterabhängig über
`has_psi` gesteuert wird.

## Scope dieses Durchlaufs

- In `systems/kp-kraefte-psi.md` die Formulierung "Psi optionaler Baseline-Modus"
  zurücknehmen und stattdessen Weltstandard + Charakter-Gating festziehen.
- In `gameplay/kampagnenuebersicht.md` Psionik als festen Weltbestandteil
  beschreiben, inklusive Discoverability im Spielverlauf.
- Änderung aus Durchlauf 09 an `characters/ausruestung-cyberware.md`
  beibehalten (Anomalie-Puffer).
- ZR-016 um Durchlauf 10 (Plan + Log) erweitern.

## Nicht im Scope (bewusst verschoben)

- Umbau der gesamten Charaktererschaffung auf prominente Psi-Onboarding-Flows.
- Neue Progressions-Subsysteme für Psi-Training.

## Exit-Kriterium für Durchlauf 10

- Psi ist in bearbeiteten Runtime-Modulen als Weltstandard verankert.
- `has_psi` bleibt als Charakter-Gating klar benannt.
- Pflichtcheck `bash scripts/smoke.sh` ist grün.
