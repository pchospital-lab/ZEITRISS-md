---
title: "QA-Log 2026-03-08 – Durchlauf 90 (Merge-Conflict-Contract Alignment)"
status: "abgeschlossen"
run_id: "zr-018-d90"
---

# Kontext

Nach Durchlauf 89 war der narrative Continuity-Output-Contract bereits guard-
seitig abgesichert. Bei der Review des Upload-Issue-Packs fiel jedoch eine
Dokudrift im Cross-Mode-Abschnitt auf: Das `merge_conflicts[]`-Beispiel in
`systems/gameflow/speicher-fortsetzung.md` verwendete ein
`anchor_value|guest_value|resolution`-Format, das nicht dem Runtime-Contract aus
`runtime.js` (`field|source|target|mode|note|resolved`) entspricht und zugleich
mit `logs.flags.continuity_conflicts[]` verwechselt werden konnte.

# Umgesetzte Änderungen

1. **SSOT-Beispiel harmonisiert**
   - `systems/gameflow/speicher-fortsetzung.md`
   - Cross-Mode-JSON-Beispiel für `merge_conflicts[]` auf
     `source` / `target` / `mode` umgestellt.

2. **Semantische Entflechtung klargestellt**
   - Das alte `resolution`-Placeholder aus dem Beispiel entfernt, damit keine
     Vermischung mit dem dedizierten Continuity-Konfliktpfad
     (`logs.flags.continuity_conflicts[]`) mehr entsteht.

3. **QA-Prozess nachgezogen**
   - Fahrplan für Durchlauf 90 angelegt.
   - Known-Issues um Durchlauf-90-Evidenz ergänzt.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**

2. `python3 tools/lint_links.py core systems meta/masterprompt_v6.md README.md internal/qa/plans internal/qa/logs internal/qa/process`
   - Ergebnis: **grün**

# Bewertung

Die Dokumentation spiegelt jetzt wieder exakt den laufenden Runtime-Contract
für Cross-Mode-Mergekonflikte. Das reduziert Fehlinterpretationen in
Anschlussläufen und hält die Trennung zwischen technischem Merge-Konfliktpfad
und narrativem Continuity-Konfliktpfad sauber.
