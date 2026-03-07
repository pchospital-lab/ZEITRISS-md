---
title: "QA-Log – Issue-Pack Durchlauf 29"
date: 2026-03-07
scope: "Charakterbogen-Minimum + Fahrzeugpersistenz (v7 SSOT)"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- ZR-016 (externer Codex-Issue-Pack), Maintainer-Feedback:
  - Charakterbogen soll Story/History + persistente Kernfelder vollständig abdecken.
  - Epochenfahrzeug und optionales legendäres temporales Schiff konsistent im Spiel/Save.
  - Persönliches Tragen/Lagern (Carry vs. Quartier) mit klaren Grenzen für Merge/Split.

## Umsetzung in diesem Durchlauf

1. **Masterprompt-Template erweitert (`meta/masterprompt_v6.md`)**
   - Charakter-Schema um `history`, `carry`, `quarters_stash` und `vehicles` ergänzt.
   - v7-Regelblock ergänzt (Pflicht-Epochenfahrzeug, optionales temporales Schiff,
     TEMP-gesteuerte Verfügbarkeit, Split/Merge-Handling der Charakterfelder).

2. **Save-Doku konsolidiert (`systems/gameflow/speicher-fortsetzung.md`)**
   - Kompakt-Profil und kanonischer v7-Exportblock auf dieselben Felder erweitert.
   - Carry-/Quartier-Grenzen dokumentiert (`carry` max 6, `quarters_stash` max 24).
   - Fahrzeugpersistenz klargezogen: `vehicles.epoch_vehicle` Pflicht,
     `vehicles.legendary_temporal_ship` optional.

3. **SL-Referenz auf denselben Kanon gezogen (`core/sl-referenz.md`)**
   - Persistentes Save-Schema um die neuen Charakterbogen-/Fahrzeugfelder ergänzt.
   - Save-v7-Pflichtfeld-Abschnitt um die entsprechenden Zielpfade erweitert.

4. **Quartier-Wording ohne Logikbruch (`gameplay/kampagnenstruktur.md`)**
   - Quartier bleibt ohne Würfelbonus, erlaubt aber explizit den persistierten
     persönlichen Stash im Rahmen der Save-Grenzen.

5. **Drift-Guard erweitert (`tools/lint_runtime.py`)**
   - `check_save_v7_canonical_export_block()` prüft zusätzlich auf
     `history`, `carry`, `quarters_stash`, `vehicles`, `epoch_vehicle`.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
