---
title: "QA-Log 2026-03-09 – Durchlauf 136 (README Landingpage Onboarding-Sharpening)"
status: "abgeschlossen"
run_id: "zr-021-d136"
---

# Kontext

Nach Durchlauf 135 war der Startvertrag in Runtime, Setup-Guide und Script
harmonisiert. In der README blieb jedoch noch ein Restdrift: Der Topblock war
zwar solide, aber nicht maximal auf das Produktversprechen fokussiert, und im
Hosting-Abschnitt stand noch ein alter DeepSeek-Default-Hinweis.

# Umgesetzte Änderungen

1. **README-Topblock auf Produktversprechen geschärft**
   - `README.md`: MMO-ohne-Server und Save=Charakter expliziter und früher
     positioniert.
   - `README.md`: Einstieg "du musst das Regelwerk nicht lesen" klar als
     KI-SL-first Onboarding formuliert.

2. **Onboarding-Hierarchie vereinheitlicht**
   - `README.md`: Startstandard bleibt `Spiel starten (solo klassisch)` plus
     natürliche Sprache; `solo schnell` nur noch explizit als optionale
     Fast-Lane benannt.
   - `README.md`: Quickstart-Headline auf "In 3-5 Minuten starten" harmonisiert.

3. **Modell-Drift im Hosting-Hinweis bereinigt**
   - `README.md`: Altformulierung "DeepSeek V3 als empfohlener
     Preis-Leistungs-Default" ersetzt durch Referenzmodell-Hinweis auf
     `anthropic/claude-sonnet-4.6`.

4. **Prozessspur fortgeschrieben**
   - `internal/qa/process/known-issues.md`: Durchlauf 136 in der ZR-020-Kette
     dokumentiert.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
2. `python3 tools/lint_links.py README.md internal/qa/plans/issue-pack-durchlauf-136-readme-landingpage-onboarding-sharpening.md internal/qa/logs/2026-03-09-issue-pack-durchlauf-136-readme-landingpage-onboarding-sharpening.md internal/qa/process/known-issues.md`

# Bewertung

Die README trägt jetzt im Einstieg klarer die Produktfantasie statt
Betriebsdetails: MMO-Illusion ohne Server, Save als Charakter und direkter
KI-SL-Start. Gleichzeitig ist der Modellhinweis konsistent zum aktuellen
Onboarding-Contract.
