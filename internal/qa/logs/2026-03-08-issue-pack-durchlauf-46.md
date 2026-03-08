---
title: "QA-Log – Issue-Pack Durchlauf 46"
date: 2026-03-08
scope: "Issue 2: OpenWebUI-native Save/Load sauber von Runtime-Komfort trennen"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- Upload-Issue-Pack: `uploads/ZEITRISS_v7_save_load_issue_pack.md` (Issue 2).
- Fahrplan: `internal/qa/plans/issue-pack-durchlauf-46.md`.

## Umsetzung in diesem Durchlauf

1. **README-Betriebsgrenze ergänzt**
   - `README.md`: Multiplayer/OpenWebUI-Abschnitt um eine klare Trennung
     erweitert:
     - chat-nativ sicher: `!save`, `!bogen`, JSON-Copy-Paste, optional `Spiel laden`
     - runtime-only optional: `!load`, `!suspend`, `!resume`, `!autosave hq`

2. **Save-Doku synchronisiert**
   - `systems/gameflow/speicher-fortsetzung.md`: OpenWebUI-Hinweis um
     Runtime-Grenze ergänzt (Host-Runtime erforderlich für Komfortbefehle).

3. **Spielerpfad/HUD synchronisiert**
   - `core/spieler-handbuch.md`: Befehlsübersicht um `!bogen` ergänzt und
     OpenWebUI-Hinweis zu runtime-only Komfortbefehlen verankert.
   - `characters/hud-system.md`: Befehle `load/suspend/resume/autosave hq`
     explizit als runtime-only markiert + Hinweiskasten auf robusten
     Chat-Standardpfad.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.

## Ergebnis / Anschluss

- Issue-2-Teilziel „OpenWebUI-native vs. runtime-only sauber trennen" ist in
  den Spieler- und Betriebsdokumenten konsistent verankert.
- Nächster Anschluss in ZR-017: v7-SSOT-Härtung, Mixed-Split-Protokoll,
  Dedupe/Lineage, Px-Zustandsautomat und E2E-Fixtures weiter priorisieren.
