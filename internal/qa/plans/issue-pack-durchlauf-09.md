---
title: "Issue-Pack Fahrplan – Durchlauf 09"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 09

Quelle: `uploads/ZEITRISS_codex_issue_pack.md`

## Ziel
Issue 9 (Psi-Gating) iterativ umsetzen: Baseline-Spiel ohne Psi als klaren
Standard festziehen und psi-spezifische Mechaniken auf den aktivierten
Psi-Modus begrenzen.

## Scope dieses Durchlaufs

- SSOT-Baseline in `systems/kp-kraefte-psi.md` explizit ergänzen
  (`has_psi=false` als Standard, `has_psi=true` als Aktivmodus).
- Kernausrüstung in `characters/ausruestung-cyberware.md` sprachlich von
  "Psi als immer da" auf "Anomalie-/Resonanzschutz situativ" ziehen.
- Kampagnenüberblick in `gameplay/kampagnenuebersicht.md` auf
  optionale Psi-Ebene kalibrieren und unzulässige Terminologie bereinigen.
- ZR-016 um Durchlauf 09 (Plan + Log) erweitern.

## Nicht im Scope (bewusst verschoben)

- Vollständige N-/T-Stufen-Neujustierung in Modul 3B.
- Tiefenüberarbeitung sämtlicher Generatoren/Encounter-Dateien auf
  Psi-Tonlage.
- Neue Runtime-Flags über `has_psi` hinaus.

## Exit-Kriterium für Durchlauf 09

- Psi-Baseline (`has_psi=false`) ist in den bearbeiteten Runtime-Modulen
  eindeutig und widerspruchsfrei benannt.
- Keine Formulierung in den geänderten Abschnitten behauptet Psi als
  obligatorischen Weltstandard.
- Pflichtcheck `bash scripts/smoke.sh` ist grün.
