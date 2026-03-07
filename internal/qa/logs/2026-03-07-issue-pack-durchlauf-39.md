---
title: "QA-Log – Issue-Pack Durchlauf 39"
date: 2026-03-07
scope: "OpenWebUI-Standardpfad: explizites !save, Load via JSON-Paste (Spiel laden optional), Charakterbogen"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- `uploads/ZEITRISS_v7_save_load_issue_pack.md`
- Maintainer-Fokus: Chat-only-Loop priorisieren, Snapshot/Resume nicht mehr
  als Standard verkaufen; stattdessen lesbarer Charakterbogen im laufenden Spiel.

## Umsetzung in diesem Durchlauf

1. **Save-/Load-Doku auf OpenWebUI geschärft (`systems/gameflow/speicher-fortsetzung.md`)**
   - Command-Übersicht auf den Chat-Standard normiert: explizites `!save`, Laden via
     JSON-Copy-Paste als Primärpfad (`Spiel laden` optional), `!bogen` als Lesesicht.
   - Die frühere Session-Suspend-Sektion wurde durch eine
     Charakterbogen-Sektion ersetzt.
   - Warntext für reinen Chatbetrieb (Host-Runtime-Features nicht garantiert)
     direkt in die Save-Doku integriert.

2. **SL-Referenz + README synchronisiert**
   - `core/sl-referenz.md`: `!save` + JSON-Paste als kanonischer Chatpfad präzisiert,
     `!bogen` ergänzt.
   - `README.md`: Koop-/Save-Hinweise um `!bogen` und OpenWebUI-Warntext ergänzt.

3. **QA-Absicherung**
   - Pflicht-Smoke unverändert ausgeführt, um Regressionen auszuschließen.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
