# Fahrplan – Durchlauf 214 (Chronopolis Kodex-Lockout Watchguard)

## Kontext

Die Chronopolis-Sperrmodus-Härtung ist in den Runtime-SSOT-Dateien umgesetzt,
aber bislang nicht als eigener Drift-Guard im Pflicht-Smoke verankert. Damit
können künftige Mikroformulierungen in HUD/FAQ/Befehlslisten unbemerkt
auseinanderlaufen.

## Ziel

- Dauerhaften Watchguard für den CITY-Kodex-Lockout etablieren.
- Kritische Anker synchron absichern:
  - `Kodex dunkel, HUD lebendig`
  - `kodex [thema]` in `CITY` gesperrt
  - `!offline` in `CITY` als Sperrmodus-Antwort
  - HQ-Vollzugriff explizit außerhalb `CITY`
- Anschlussdoku in Fahrplan/Log/Prozess fortschreiben.

## Arbeitspakete

1. Neuen Watchguard anlegen:
   - `tools/test_chronopolis_kodex_lockout_watchguard.js`
2. Pflicht-Smoke erweitern:
   - `scripts/smoke.sh`
3. Prozessspiegel aktualisieren:
   - `internal/qa/process/hard-final-review-next-steps.md`
   - `internal/qa/process/known-issues.md`
4. QA-Log dokumentieren:
   - `internal/qa/logs/2026-03-11-issue-pack-durchlauf-214-chronopolis-kodex-lockout-watchguard.md`
5. Pflichtcheck ausführen:
   - `bash scripts/smoke.sh`

## Abnahme

- Neuer Watchguard läuft im Pflicht-Smoke mit grünem Token.
- Chronopolis-Kodex-Lockout bleibt als SSOT-Querschnitt technisch abgesichert.
- Prozessseiten sind auf Durchlauf 214 synchronisiert.
