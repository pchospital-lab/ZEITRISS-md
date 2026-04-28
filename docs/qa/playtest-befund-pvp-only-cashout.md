---
title: "Playtest-Befund: PvP-only Cashout/Push-Loop"
version: 1.0.0
tags: [qa, playtest, pvp, cashout]
status: draft
updated: 2026-04-28
---

# Playtest-Befund: PvP-only Cashout/Push-Loop

Ziel: Für den nächsten Testzyklus den aktuellen Stand aus
`docs/qa/pvp-bio-nachcheck-status.md` reproduzierbar verifizieren,
inklusive sauberem Anschluss für Folge-Agenten.

## Scope

- **PVP-01** PvP-only L1 → Cashout → Levelpfad
- **PVP-02** Push-your-luck mit Pending-Verlust
- **SAVE-01** Strict-Export nach PvP gegen v7-Export-Schema
- **XMODE-01** Core → PvP → Rift (Mode-/Ökonomie-Drift)

## Preflight

1. `bash scripts/smoke.sh` muss grün sein.
2. Arbeitsbranch + Commit-Hash im Befund notieren.
3. Test-Preset notieren (Solo/Koop, Startlevel, Squadgröße, Match-Policy).

## Testprotokoll (zum Ausfüllen)

### Metadaten

- Datum:
- Branch:
- Commit:
- Tester:
- Setup (LLM/Temperatur/Preset):

### PVP-01 — PvP-only Karrierepfad

**Erwartung**

- Arena vergibt **kein Px**, **keine RiftSeeds**.
- Cashout vergibt **Training-XP/Missionsäquivalent**, CU/Ruf/Ladder gemäß Contract.
- Level-Fortschritt wird persistiert (`level_history`/Karrierepfad bleibt nachvollziehbar).

**Befund**

- Status: ☐ Pass ☐ Warnung ☐ Fail
- Beobachtung:
- Save-/Log-Hinweise:

### PVP-02 — Push-your-luck (Pending)

**Erwartung**

- Nach Sieg klare Wahl: **Cashout** vs **Push**.
- Pending-Bonus steigt bei Push; bei Niederlage verfällt/verkleinert Pending deterministisch.
- Banked bleibt geschützt.

**Befund**

- Status: ☐ Pass ☐ Warnung ☐ Fail
- Beobachtung:
- Save-/Log-Hinweise:

### SAVE-01 — Strict Export nach PvP

**Erwartung**

- Export validiert gegen `systems/gameflow/saveGame.v7.export.schema.json`.
- `ui.action_mode="uncut"` vorhanden.
- `campaign.mode` bleibt im Export nicht fälschlich dauerhaft auf `pvp` kleben.

**Befund**

- Status: ☐ Pass ☐ Warnung ☐ Fail
- Beobachtung:
- Validator-Output:

### XMODE-01 — Core → PvP → Rift

**Erwartung**

- Mode-Restore über `arena.previous_mode` robust, Legacy-Fallback `mixed`.
- Keine Ökonomie-Drift (Px/Seeds bleiben im PvP-Pfad unangetastet).
- Cross-Mode-Übergang bleibt savebar/reimportierbar.

**Befund**

- Status: ☐ Pass ☐ Warnung ☐ Fail
- Beobachtung:
- Save-/Diff-Hinweise:

## Kurzfazit

- Gesamtstatus: ☐ Grün ☐ Gelb ☐ Rot
- Kritische Findings:
- Empfohlene Follow-ups:

## Artefakte

- Run-Notizen:
- Export-Dateien:
- Diff-/Validator-Logs:

