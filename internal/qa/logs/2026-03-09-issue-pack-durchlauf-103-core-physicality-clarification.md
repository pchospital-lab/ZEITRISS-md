---
title: "QA-Log 2026-03-09 – Durchlauf 103 (Core-Physicality-Klarstellung)"
status: "abgeschlossen"
run_id: "zr-019-d103"
---

# Kontext

Durchlauf 102 war inhaltlich gut gemeint, hat im Core-Wording jedoch
holografische Begriffe zu breit ersetzt. Das war semantisch zu streng: Der
Kanon erlaubt Hologramm-/Lichtbild-Projektionen weiterhin, solange diese
sichtbar an Geräteflächen verankert sind. Verboten bleibt nur das implizite
Handgelenk-HUD als mobiler Default.

# Umgesetzte Änderungen

1. **Core-Text auf Kanonintention zurückgeführt**
   - Datei: `core/zeitriss-core.md`
   - HQ-/Trainingspassagen nutzen wieder zulässige Hologrammbegriffe
     (z. B. holografische Lichtbild-Anzeigen, Hologramm-Module, Holosuites).
   - Zusätzlich wurde die Guard-Regel direkt im Abschnitt verankert:
     Projektionen nur an sichtbarer ITI-Infrastruktur
     (Holosuite/Briefingglas/Tischprojektor), kein mobiler Handgelenk-Default.

2. **QA-Prozessdoku aktualisiert**
   - Dateien:
     - `internal/qa/process/known-issues.md`
     - `internal/qa/process/continuity-redesign-statusmatrix.md`
   - Evidenzlauf 103 ergänzt, damit Folgeänderungen die semantische Trennung
     (Retina-HUD vs. verankerte Inworld-Projektion) stabil halten.

3. **Fahrplanlauf dokumentiert**
   - Datei:
     `internal/qa/plans/issue-pack-durchlauf-103-core-physicality-clarification.md`

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**

# Bewertung

Der Physicality-Strang ist damit wieder präzise statt überkorrigiert:
"Hologramm" bleibt als Stilmittel erlaubt, aber technisch klar gerahmt.
Dadurch sinkt das Risiko neuer Missverständnisse bei der KI-SL in späteren
Textläufen.
