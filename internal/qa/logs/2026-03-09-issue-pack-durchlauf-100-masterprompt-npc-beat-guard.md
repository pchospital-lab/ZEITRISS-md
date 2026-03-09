---
title: "QA-Log 2026-03-09 – Durchlauf 100 (Masterprompt NPC-Beat-Guard)"
status: "abgeschlossen"
run_id: "zr-019-d100"
---

# Kontext

Der NPC/MMO-Strang war nach Durchlauf 99 strukturell und verhaltensseitig
weitgehend konsistent. Bei der SSOT-Gegenprüfung blieb eine kleine, aber
relevante Asymmetrie: `NPC-Departure-Beat` und `NPC-Recognition-Beat` waren
in Speichermodul/Toolkit explizit, im Masterprompt-Regelblock jedoch nur
implizit abgedeckt.

# Umgesetzte Änderungen

1. **Masterprompt-Guard ergänzt**
   - Datei: `meta/masterprompt_v6.md`
   - Neuer expliziter Guard unter den Save-v7-Regeln:
     - Beim Verlassen eines bekannten NPCs: kurze Inworld-Übergabe (1–2 Sätze).
     - Beim Wiederauftauchen: mindestens eine konkrete gemeinsame Szene als
       Wiedererkennungsanker.

2. **QA-Prozessdoku nachgezogen**
   - Dateien:
     - `internal/qa/process/known-issues.md`
     - `internal/qa/process/continuity-redesign-statusmatrix.md`
   - Durchlauf 100 als Evidenzlauf ergänzt; Watchpoint-Liste um den
     Masterprompt-Pflichtbeat-Check erweitert.

3. **Fahrplanlauf dokumentiert**
   - Datei: `internal/qa/plans/issue-pack-durchlauf-100-masterprompt-npc-beat-guard.md`

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**

2. `python3 tools/lint_links.py meta/masterprompt_v6.md internal/qa/plans internal/qa/logs internal/qa/process`
   - Ergebnis: **grün**

# Bewertung

Mit Durchlauf 100 ist der NPC-Pflichtbeat-Kanon auf allen SSOT-nahen Ebenen
synchron. Das reduziert den Risiko-Cluster "funktional richtig, aber
Masterprompt nicht explizit genug" für kommende Änderungen.
