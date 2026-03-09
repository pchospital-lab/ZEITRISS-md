---
title: "QA-Log 2026-03-09 – Durchlauf 127 (ITI-SSOT-Verankerung Referenz + Kampagnenübersicht)"
status: "abgeschlossen"
run_id: "zr-020-d127"
---

# Kontext

Nach den Durchläufen 122-126 war der ITI-Hauskanon bereits weitgehend
harmonisiert. Für noch robustere Laufzeitkonsistenz fehlte jedoch in
`core/sl-referenz.md` ein expliziter Pflicht-Heimkehr-Beat mit ITI-Lagezeile,
sowie in `gameplay/kampagnenuebersicht.md` eine direkte SSOT-Verankerung von
player-facing Atlas + Kernpersonal für die sichtbare Einstiegsebene.

# Umgesetzte Änderungen

1. **SL-Referenz gehärtet (Heimkehr + SSOT-Anker)**
   - Datei: `core/sl-referenz.md`
   - Vor dem HQ-Menü wurde der Pflicht-Heimkehr-Beat (2-4 Sätze) als feste
     Ausgabeform ergänzt, inkl. optionaler einzeiliger `ITI-Lage`.
   - Zusätzlich wurden ITI-Atlas (8 Hauptorte) und Kernpersonal
     (Renier/Mira/Lorian/Vargas/Narella) explizit als Runtime-SSOT im
     HQ/Chronopolis-Abschnitt verankert.

2. **Kampagnenübersicht ergänzt (sichtbarer Hauskanon)**
   - Datei: `gameplay/kampagnenuebersicht.md`
   - Im Abschnitt "Chronopolis & ITI-Struktur" wurde ein kompakter
     ITI-Hardcanon-Block ergänzt: gleicher Heimatraum über Solo/NPC/Multiplayer,
     8 kanonische Hauptorte, Alias nur als Unterzonen, fixes Kernpersonal.

3. **Prozessartefakte ergänzt/aktualisiert**
   - Fahrplan ergänzt:
     `internal/qa/plans/issue-pack-durchlauf-127-iti-ssot-verankerung-referenz-uebersicht.md`.
   - Known-Issue/Statusmatrix um Evidenz für Durchlauf 127 erweitert.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
2. `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`

# Bewertung

Der ITI-Hauskanon ist nun auch im SL-Referenzfluss und im
Kampagnen-Einstiegsmodul konsistent sichtbar: feste Heimkehr, feste Orte,
feste Kernrollen. Damit sinkt das Risiko für erneuten Parallelkanon in
laufenden und neu gestarteten Chats weiter.
