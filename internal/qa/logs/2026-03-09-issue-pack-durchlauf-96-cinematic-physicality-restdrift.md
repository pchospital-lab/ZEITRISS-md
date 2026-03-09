---
title: "QA-Log 2026-03-09 – Durchlauf 96 (Cinematic-Physicality-Restdrift)"
status: "abgeschlossen"
run_id: "zr-019-d96"
---

# Kontext

Nach Durchlauf 95 war das Hardwareprinzip korrekt, aber im Modul
`systems/gameflow/cinematic-start.md` standen noch zwei hybride Formulierungen
(`Linsen-Lichtbilder/HUD-Hologramme`, `Lichtbilder/Hologramm-Projektionen`),
die Linse-HUD und HQ-Inworld-Projektionen sprachlich unnötig vermischten.

# Umgesetzte Änderungen

1. **Solo-Begleiter-Formulierung präzisiert**
   - `systems/gameflow/cinematic-start.md`
   - Die Aufzählung im Solo-Abschnitt nutzt jetzt klar
     „Linsen-Lichtbilder im HUD oder Comlink-Begleiter“.

2. **Kulturkollisions-Beispiel auf HQ-Flächen verankert**
   - `systems/gameflow/cinematic-start.md`
   - Die bisherige Formulierung „Lichtbilder/Hologramm-Projektionen im HQ“ wurde
     auf „Lichtbilder auf den HQ-Briefingflächen“ konkretisiert.

3. **Known-Issues Anschlussfähigkeit fortgeschrieben**
   - `internal/qa/process/known-issues.md`
   - Durchlauf 96 als gezielter Restdrift-Fix inklusive Plan/Log-Referenzen
     ergänzt.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**

# Bewertung

Die Physicality-Kommunikation bleibt technoir-kompatibel (feste HQ-Projektionen
sind möglich), ohne den Guard gegen unklare HUD-/Hologramm-Defaults
aufzuweichen.
