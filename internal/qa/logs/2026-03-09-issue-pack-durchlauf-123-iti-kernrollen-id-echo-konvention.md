---
title: "QA-Log 2026-03-09 – Durchlauf 123 (ITI-Kernrollen-ID & Echo-Konvention)"
status: "abgeschlossen"
run_id: "zr-020-d123"
---

# Kontext

Nach Durchlauf 122 blieb aus dem ITI/MMO-Review der Feinschliff offen,
Kontinuitätsfelder gezielt für feste ITI-Kontakte zu normieren
(`npc_roster[]`, `roster_echoes[]`, `shared_echoes[]`) ohne neues
Save-Subsystem.

# Umgesetzte Änderungen

1. **Speichermodul: feste ITI-ID-Konvention ergänzt**
   - Datei: `systems/gameflow/speicher-fortsetzung.md`
   - ITI-Kernrollen als feste IDs dokumentiert:
     `ITI-RENIER`, `ITI-MIRA`, `ITI-LORIAN`, `ITI-VARGAS`, `ITI-NARELLA`
     (+ optionale Service-Anker).
   - Regel ergänzt: Kernrollen gelten ohne Save-Eintrag als Hauskanon;
     `npc_roster[]`/Echo nur bei relevanter offener Bindung.
   - Echo-Kurzform standardisiert: `ITI-ID :: Status/Hook`.

2. **Toolkit: NPC-Kontinuität parallel ergänzt**
   - Datei: `systems/toolkit-gpt-spielleiter.md`
   - Abschnitt „Kompaktmodell für NPC-Kontinuität" um dieselbe
     ITI-ID-Konvention, Save-Sparregel und Echo-Kurzform erweitert.

3. **Prozessartefakte synchronisiert**
   - Fahrplan ergänzt:
     `internal/qa/plans/issue-pack-durchlauf-123-iti-kernrollen-id-echo-konvention.md`.
   - Known-Issue-Notiz und Statusmatrix-Evidenz auf Durchlauf 123 erweitert.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
2. `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`

# Bewertung

Der ITI-Hauskanon ist nun auch auf Kontinuitätsebene präziser: feste,
wiedererkennbare ITI-Kontakte sind als IDs verankert, während Save-Budget und
bestehende v7-Struktur unverändert bleiben.
