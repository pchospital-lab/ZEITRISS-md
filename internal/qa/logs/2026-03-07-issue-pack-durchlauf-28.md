---
title: "QA-Log – Issue-Pack Durchlauf 28"
date: 2026-03-07
scope: "Setup-Default Sonnet + Runtime-Wording + Save-v7-Talente"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- ZR-016 (externer Codex-Issue-Pack), Fortsetzung nach Maintainer-Feedback:
  - Setup-Script-Default noch auf DeepSeek.
  - verbleibende Begriffe `Schaman:innen` / `Wahrsager:innen`.
  - Nachfrage zu Save-v7-Vollständigkeit (Talente/Epochenfahrzeug).

## Umsetzung in diesem Durchlauf

1. **Setup-Standardmodell vereinheitlicht (`scripts/setup-openwebui.sh`)**
   - `DEFAULT_REMOTE_MODEL` auf `anthropic/claude-sonnet-4.6` gesetzt.
   - Prompt-Beispiel für manuelle Model-ID auf Sonnet 4.6 angepasst.
   - Header-Hinweis zur Standardmodell-Variable auf Sonnet 4.6 präzisiert.

2. **Runtime-Wording bereinigt (`gameplay/kampagnenuebersicht.md`, `systems/kp-kraefte-psi.md`)**
   - Formulierungen mit `Schaman:innen` / `Wahrsager:innen` auf einfache Formen umgestellt
     (`Schamanen`, `Wahrsager`, `Orakel`, `Mystiker`).

3. **Save-v7-Klarstellung erweitert (`systems/gameflow/speicher-fortsetzung.md`)**
   - Kanonisches v7-Exportbeispiel je Charakter um `talents[]` und `implants[]` ergänzt.
   - Ergänzender Hinweis aufgenommen:
     - `talents[]` gehört im v7-Kanon in `characters[]`.
     - Epochenfahrzeuge sind missions-/szenengebundener Kontext und kein globales Pflichtfeld im Save-Export.

4. **QA-Nachführung**
   - Neuer Fahrplan/Log für Durchlauf 28 angelegt.
   - `internal/qa/process/known-issues.md` um Durchlauf 28 ergänzt.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
