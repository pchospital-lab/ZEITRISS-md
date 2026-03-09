---
title: "QA-Log 2026-03-09 – Durchlauf 101 (Toolkit Physicality-Wording-Guard)"
status: "abgeschlossen"
run_id: "zr-019-d101"
---

# Kontext

Nach den NPC/MMO-Läufen 94–100 war die Logik stabil, aber im Toolkit stand im
Abschnitt "HUD-Overlay und Kodex-Ausgaben" noch ein allgemeines
"holografisch"-Wording. Das war kein Funktionsfehler, aber ein kleiner
Risikopunkt gegen den Physicality-Guard (Linse/HUD als Default, freie
Projektionen nur als benannte Inworld-Fläche).

# Umgesetzte Änderungen

1. **Toolkit-Wording geschärft**
   - Datei: `systems/toolkit-gpt-spielleiter.md`
   - Im HUD-Stilblock explizit festgelegt:
     - Default = linsengebundene Sichtfeldprojektion (Retina-Linse).
     - Freie Projektionen nur bei benannter Fläche/Gerät (z. B.
       HQ-Briefingglas).

2. **QA-Prozessdoku aktualisiert**
   - Dateien:
     - `internal/qa/process/known-issues.md`
     - `internal/qa/process/continuity-redesign-statusmatrix.md`
   - Durchlauf 101 als weiterer Evidenzlauf für den Physicality-Watchpoint
     ergänzt.

3. **Fahrplanlauf dokumentiert**
   - Datei:
     `internal/qa/plans/issue-pack-durchlauf-101-toolkit-physicality-wording-guard.md`

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**

2. `python3 tools/lint_links.py systems/toolkit-gpt-spielleiter.md internal/qa/plans internal/qa/logs internal/qa/process`
   - Ergebnis: **grün**

# Bewertung

Der NPC/MMO- und Physicality-Strang bleibt damit nicht nur regel- und
schemaseitig, sondern auch in der erzählerischen Toolkit-Anleitung konsistent.
Das senkt das Risiko, dass in Folgeänderungen wieder ein losgelöstes
Hologramm-Default-Wording einschleicht.
