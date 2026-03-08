---
title: "QA-Log 2026-03-08 – Durchlauf 81 (Kontinuitäts-Redesign)"
status: "abgeschlossen"
run_id: "zr-018-d81"
---

# Kontext

Basierend auf `uploads/ZEITRISS_continuity_save_redesign.md` wurde der Fokus
von "Host gewinnt alles" auf "Session-Anker + persönliche Wahrheit +
Kontinuitätsgewebe" umgestellt. Ziel war ein narrativ wirksamer Multi-Load,
ohne Save-anywhere einzuführen.

# Umgesetzte Änderungen

1. **README – Multiplayer-/Merge-Semantik aktualisiert**
   - Host-SSOT-Bullets auf Session-Anker, Charakter-Autorität und
     Kontinuitätsrückblick umgestellt.
   - Core-Split-Kanon via `continuity.split.family_id` ergänzt.

2. **Masterprompt – Save-v7-Template erweitert**
   - Neuer Root-Block `continuity` in das kanonische JSON-Beispiel aufgenommen.
   - Regeln ergänzt: Echo-Budgets, Multi-Load-Pflichtrecap,
     Charakter-Autorität statt reinem Duplicate-Block.

3. **Save/Load-SSOT – `speicher-fortsetzung.md` umgebaut**
   - Multi-Save-Importtext von Host auf Session-Anker umgestellt.
   - Neues Kapitel "Kontinuitätsmodell (Session-Anker statt Host-SSOT)"
     inkl. Goldregel, Kapsel und Pflichtausgabe.
   - Nicht-kanonische Branch-Passage für Core-Splits präzisiert:
     `family_id`-basierte Kanonisierung, sonst Importmodus.

4. **SL-Referenz harmonisiert**
   - Duplicate-Character-Regel auf Rejoin-/`continuity_conflict`-Pfad geändert.
   - Split/Merge-Abschnitt auf Session-Anker + Konvergenzlogik angehoben.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**

2. `python3 tools/lint_links.py core systems meta/masterprompt_v6.md README.md`
   - Ergebnis: **grün**

# Bewertung

- Kontinuitäts-Redesign ist jetzt in den zentralen SSOT-Dokumenten verankert.
- Mechanische Invarianten (HQ-only Save, Px-State-Determinismus,
  Mischpfad-Allowlist) bleiben intakt.
- Für Anschlussläufe empfohlen: gezielte Beispiel-Saves (`internal/qa/fixtures`)
  mit `continuity.split.*` und `convergence_tags[]` ergänzen.
