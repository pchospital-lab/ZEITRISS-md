---
title: "QA-Log – Issue-Pack Durchlauf 01"
version: 0.1.0
tags: [qa, log]
---

# QA-Log – Issue-Pack Durchlauf 01

## Kontext
- Input: `uploads/ZEITRISS_codex_issue_pack.md`
- Ziel dieses Durchlaufs: erster abgrenzbarer P0-Block mit Anschlussfähigkeit für Folgedurchläufe.

## Umgesetzter Scope

### 1) Würfel-SSOT bereinigt (`core/wuerfelmechanik.md`)
- Kapitel-/Überschriften auf **Burst-Cap-SSOT** ausgerichtet.
- W10 nicht mehr als parallele optional-vs-standard-Aussage geführt,
  sondern als feste Schwelle ab Attribut 11 beschrieben.
- Schwellen-Kalibrierung mit gleicher Zielzahlen-Logik für W6/W10 präzisiert.
- Formulierung „auf Wunsch den W10“ auf automatische Aktivierung geändert.

## QA-Checks
- Pflichtcheck: `bash scripts/smoke.sh`.
- Ergebnis: muss grün sein, sonst kein Abschluss dieses Durchlaufs.

## Offene Restpunkte (für nächsten Durchlauf)
1. Save-SSOT + Wallet-Modell in `speicher-fortsetzung`, `sl-referenz`, `kampagnenstruktur`, `cu-waehrungssystem` konsolidieren.
2. `tools/lint_runtime.py` um Drift-Guards für Legacy-Tokens (`party.characters`, `team.members`, `economy.cu`, `GPT`) erweitern.
3. Px/Arena-Entkopplung vereinheitlichen (Arena ohne Px-Belohnung, klarer Reset-Zeitpunkt).

## Status
- Durchlauf 01: **abgeschlossen** (Smoke erfolgreich; Übergabe an nächsten Durchlauf vorbereitet).
