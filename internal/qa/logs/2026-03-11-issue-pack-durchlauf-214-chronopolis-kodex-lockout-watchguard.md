# QA-Log – Durchlauf 214 (Chronopolis Kodex-Lockout Watchguard)

## Ausgangslage

Der Chronopolis-Sperrmodus ist in den zentralen Runtime-SSOT-Texten bereits
klar verankert, aber es fehlte noch ein dedizierter Guard im Pflicht-Smoke,
der die kritischen Crossfile-Anker dauerhaft zusammenhält.

## Umsetzung

- Neuer Watchguard ergänzt:
  - `tools/test_chronopolis_kodex_lockout_watchguard.js`
  - prüft die Kernanker über HUD, Spieler-Handbuch, SL-Referenz und
    Masterprompt (`Kodex dunkel, HUD lebendig`, `kodex [thema]` in `CITY`
    gesperrt, `!offline`-Sperrmodus in `CITY`, HQ-Vollzugriff außerhalb
    `CITY`).
- Pflicht-Smoke erweitert:
  - `scripts/smoke.sh` führt den neuen Watchguard aus und greppt auf
    `chronopolis-kodex-lockout-watchguard-ok`.
- Prozessspiegel nachgezogen:
  - `internal/qa/process/known-issues.md`
  - `internal/qa/process/hard-final-review-next-steps.md`

## Ergebnis

Die Chronopolis-Kodex-Lockout-Formel ist jetzt nicht nur textlich, sondern auch
als automatisierter Drift-Guard im Standard-Gate abgesichert. Künftige
Mikrodrift in Kurztexten (HUD/FAQ/Befehle) wird damit früh im Smoke sichtbar.

## Checks

- `bash scripts/smoke.sh` → bestanden.
- `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` → bestanden.
