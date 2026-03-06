---
title: "Issue-Pack Fahrplan – Durchlauf 14"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 14

Quelle: `uploads/ZEITRISS_codex_issue_pack.md`

## Ziel
Nachschärfung von Issue 10 (Chronopolis/ITI-Logik): Das Regelwerk soll
konsistent ausdrücken, dass **ITI der Überbegriff** ist (HQ-Kern +
Chronopolis-Ring), während Save-/Service-Regeln weiterhin eindeutig am
**HQ-Kern** hängen.

## Scope dieses Durchlaufs

- Terminologie- und Logikabgleich in den geladenen Kernmodulen:
  - `meta/masterprompt_v6.md`
  - `core/spieler-handbuch.md`
  - `core/sl-referenz.md`
  - `gameplay/kampagnenuebersicht.md`
  - `systems/gameflow/speicher-fortsetzung.md`
- Chronopolis-Flavor präzisieren:
  - als gescheiterte Episodenzeitlinie,
  - mit offenem Stimmungsraum (düster/instabil/anders organisiert),
  - ohne starre Mood-Vorgabe.
- QA-Nachführung in `internal/qa/process/known-issues.md` + neues Log.

## Nicht im Scope (bewusst verschoben)

- Vollständige redaktionelle Vereinheitlichung aller älteren Beispieltexte.
- Neue Lint-Regeln für ITI/HQ-Terminologie.
- Strukturänderungen am Save-Schema v7 selbst.

## Exit-Kriterium für Durchlauf 14

- Die fünf genannten SSOT-/Runtime-Module nutzen denselben Rahmen:
  - ITI als Überbegriff,
  - HQ-Kern als Save-/Service-Bereich,
  - Chronopolis als `CITY`-Instanz ohne Savepoint.
- `bash scripts/smoke.sh` ist grün.
