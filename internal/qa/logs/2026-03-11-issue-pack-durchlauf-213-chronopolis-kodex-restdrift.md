# QA-Log – Durchlauf 213 (Chronopolis/Kodex Restdrift)

## Ausgangslage

Nach den letzten Chronopolis-Härtungen war der Contract funktional konsistent,
aber einzelne Formulierungen waren noch nicht überall gleich explizit. Das
betraf v. a. Vollzugriff-Hinweise und die Sichtbarkeit der `CITY`-Sperre beim
`kodex`-Befehl.

## Umsetzung

- `characters/hud-system.md`:
  - Zugriffsmatrix präzisiert: **HQ/ITI-Vollzugriff nur außerhalb `CITY`**.
- `core/sl-referenz.md`:
  - Mini-FAQ synchronisiert auf **„HQ/ITI-Kern außerhalb `CITY` = Vollzugriff“**.
- `core/spieler-handbuch.md`:
  - Befehlszeile `kodex [thema]` auf **„in `CITY` gesperrt“** ergänzt.

## Ergebnis

Der Sperrmodus-Contract ist jetzt auch in den kompakten Nutzerformulierungen
sauber und ohne Restmehrdeutigkeit verankert: `CITY` bleibt expliziter
Ausnahmezustand, ohne den regulären HQ-Vollzugriff außerhalb `CITY` zu
schwächen.

## Checks

- `bash scripts/smoke.sh` → bestanden.
- `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` → bestanden.
