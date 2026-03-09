---
title: "QA-Log 2026-03-09 – Durchlauf 128 (ITI-Alias-Drift Runtime-Stub)"
status: "abgeschlossen"
run_id: "zr-020-d128"
---

# Kontext

Die aktiven Runtime-Module sind seit Durchlauf 127 auf den ITI-Hardcanon
harmonisiert. Im internen Entwickler-Stub (`internal/runtime`) lagen jedoch
noch Alt-Hauptorte (`Gatehall`, `Research-Wing`, `Mission-Briefing-Pod`) als
kanonische Router-Ziele vor. Das riskierte Re-Import von Parallelkanon bei
künftigen Tooling-/Runtime-Arbeiten.

# Umgesetzte Änderungen

1. **Runtime-Stub auf kanonischen ITI-Atlas umgestellt**
   - Datei: `internal/runtime/runtime-stub-routing-layer.md`
   - Der JSON-Router nutzt jetzt die 8 Hauptorte als kanonische Raum-IDs
     (`Quarzatrium`, `Kodex-Archiv`, `Med-Lab`, `Operations-Deck`,
     `Quartiere`, `Hangar-Axis`, `Zero Time Lounge`, `Pre-City-Hub`).

2. **Alias-Bridge beibehalten (ohne gleichwertige Hauptort-Rolle)**
   - Datei: `internal/runtime/runtime-stub-routing-layer.md`
   - Legacy-Begriffe bleiben als Alias erhalten (z. B. `gatehall`,
     `mission-briefing-pod`, `research-wing`), werden aber auf den
     kanonischen Atlas geroutet.

3. **Router-Beispiele synchronisiert**
   - Datei: `internal/runtime/runtime-stub-routing-layer.md`
   - Das Router-Call-Beispiel und der Type-Kommentar für `room_id` zeigen jetzt
     ein kanonisches Ziel (`Kodex-Archiv`) statt Alt-Hauptorten.

4. **Prozessartefakte aktualisiert**
   - Fahrplan ergänzt:
     `internal/qa/plans/issue-pack-durchlauf-128-iti-alias-drift-runtime-stub.md`.
   - Known-Issue/Statusmatrix um Evidenz für Durchlauf 128 erweitert.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
2. `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`

# Bewertung

Der ITI-Hauskanon ist jetzt auch in den internen Runtime-Routingstubs
konsistent: keine konkurrierenden HQ-Hauptorte mehr, nur noch Alias-Bridge auf
den festen Atlas. Das reduziert Rückfallrisiko bei künftigen Refactors.
