---
title: "QA-Log 2026-03-09 – Durchlauf 94 (NPC-Kontinuität & MMO-Immersion-Hardening)"
status: "abgeschlossen"
run_id: "zr-019-d94"
---

# Kontext

Das Upload-Paket `uploads/ZEITRISS_npc_mmo_immersion_review.md` identifizierte
nach Abschluss des Session-Anker-Redesigns den größten Restbruch bei
NPC-Chrononauten: Alttext zu „temporärem Solo-NPC-Team“, ein Reset-Pseudopfad
für Gruppenstarts und fehlende kompakte NPC-Persistenz im v7-Kontinuitätsblock.

# Umgesetzte Änderungen

1. **Toolkit auf persistente NPC-Kontinuität umgestellt**
   - `systems/toolkit-gpt-spielleiter.md`
   - Abschnitt „Solo-Modus mit temporärem NPC-Team“ vollständig ersetzt durch
     persistente Solo-/Gruppenkontinuität, Scope-/Statusmodell,
     Mensch-vor-NPC-Slotlogik, Pflichtbeats sowie neues
     `StartGroupContinuity(...)`-Pseudomakro ohne Px-/Seed-Reset.

2. **Masterprompt-v7-Schema um NPC-Kapsel erweitert**
   - `meta/masterprompt_v6.md`
   - Save-Template ergänzt um `continuity.npc_roster[]` und
     `continuity.active_npc_ids[]`; Regeln für Caps, Scope/Status,
     NPC-Slot-Priorität und erweiterten Mehrfach-Load-Rückblick mit
     NPC-Lagebild nachgezogen.

3. **Save/Fortsetzung auf denselben Kontinuitätsvertrag gehoben**
   - `systems/gameflow/speicher-fortsetzung.md`
   - Kompakt-Profil + Kontinuitätskapsel um NPC-Felder erweitert, harte Caps
     dokumentiert, Mischgruppen-Slotregel ergänzt und
     Pflichtausgabe beim Mehrfach-Load von 4 auf 5 Blöcke
     (inkl. NPC-Lagebild) angehoben.

4. **Physicality-Wording im Startmodul bereinigt**
   - `systems/gameflow/cinematic-start.md`
   - „Hologramm-Begleiter“/„Hologramme“ an die Linse-/Comlink-Terminologie
     angepasst (`Linsen-Lichtbilder`, `Lichtbilder`).

5. **Anschlussfähigkeit in QA-Prozessakten dokumentiert**
   - `internal/qa/process/continuity-redesign-statusmatrix.md`
   - `internal/qa/process/known-issues.md`
   - NPC/MMO-Follow-up als neuer dokumentierter Anschlussblock + Durchlauf-94-
     Eintrag ergänzt.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**

2. `python3 tools/lint_links.py core systems meta/masterprompt_v6.md README.md internal/qa/plans internal/qa/logs internal/qa/process`
   - Ergebnis: **grün**

# Bewertung

Der SSOT-Vertrag ist jetzt durchgängig auf persistente NPC-Chrononauten
gezogen. Damit fällt der letzte große MMO-Immersionsbruch zwischen
Spieler-Kontinuität und NPC-Kontinuität im aktiven Wissensspeicher weg.
