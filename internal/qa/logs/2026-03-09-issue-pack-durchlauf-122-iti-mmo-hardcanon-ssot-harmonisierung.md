---
title: "QA-Log 2026-03-09 – Durchlauf 122 (ITI/MMO-Hardcanon SSOT-Harmonisierung)"
status: "abgeschlossen"
run_id: "zr-019-d122"
---

# Kontext

Der ITI/MMO-Review (`uploads/ZEITRISS_ITI_mmo_konsistenz_review.md`) meldet
Restdrift im Hauskanon: konkurrierende Ortsnamen, HQ-Ausbau-Altlogik,
unterschiedliche Heimkehr-Setzung und zu weiche Runtime-Verankerung des
ITI-Kernpersonals.

# Umgesetzte Änderungen

1. **Toolkit-Atlas + Drift-Guard nachgezogen**
   - Datei: `systems/toolkit-gpt-spielleiter.md`
   - Sechs alte Bereichsnamen durch kanonische Acht-Orte-Liste ersetzt,
     Alias-Regel ergänzt und Kernpersonal (Renier, Mira, Fraktionskontakte)
     als feste Runtime-Rollen verankert.
   - Pflicht-Heimkehr-Beat inkl. kompakter ITI-Dienstlagezeile ergänzt.

2. **HQ-Ausbau auf Zugangs-/Lizenzlogik umgestellt**
   - Dateien: `gameplay/kampagnenstruktur.md`,
     `characters/charaktererschaffung-grundlagen.md`,
     `core/sl-referenz.md`, `core/zeitriss-core.md`
   - Ausbau-/Freikaufpfad entfernt bzw. umformuliert, Abschnitt in der
     Kampagnenstruktur zu „HQ-Betrieb und Zugangsfreigaben“ umgestellt.
   - Freiwillig/Verpflichtend-Drift bei HQ-Heimkehr auf festen Beat harmonisiert.

3. **Masterprompt-Hardcanon ergänzt**
   - Datei: `meta/masterprompt_v6.md`
   - ITI-Drift-Guard, kanonische Hauptorte und Kernpersonal als
     Laufzeit-Mussregel in der HQ/Sprung-Sektion ergänzt.

4. **Begriffsdrift bereinigt**
   - Datei: `characters/charaktererschaffung-grundlagen.md`
   - Vollname auf „Institut für Temporale Intervention“ vereinheitlicht.

5. **Prozessartefakte synchronisiert**
   - Neuer Fahrplan: `internal/qa/plans/issue-pack-durchlauf-122-iti-mmo-hardcanon-ssot-harmonisierung.md`
   - Prozessseiten aktualisiert: `internal/qa/process/known-issues.md` und
     `internal/qa/process/continuity-redesign-statusmatrix.md`.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
2. `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`

# Bewertung

ITI-Heimatwelt ist nun SSOT-seitig klarer als konstanter Laufzeitraum gesetzt:
player-facing Atlas einheitlich, Kernrollen fixiert, Fortschritt ohne
Basisbau-Mechanik, Heimkehr-Beat konsistent.
