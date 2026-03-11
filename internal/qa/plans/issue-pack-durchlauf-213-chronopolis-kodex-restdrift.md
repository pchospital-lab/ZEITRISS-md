# Fahrplan – Durchlauf 213 (Chronopolis/Kodex Restdrift)

## Kontext

Nach den Sperrmodus- und `ABSOLUT-7/CITY`-Durchläufen blieb kleine
Formulierungsdrift in den Nutzeroberflächen: einzelne Hinweise klangen noch
nach unbedingtem Vollzugriff oder ohne expliziten `CITY`-Scope.

## Ziel

- Restdrift in HUD-/FAQ-/Befehlsformulierungen auflösen.
- Gleiches Framing in Spieler-Handbuch, SL-Referenz und HUD:
  Vollzugriff nur außerhalb `CITY`, Kodex-Befehle in `CITY` gesperrt.
- Anschlussdoku (Fahrplan, Log, Prozessstand) aktualisieren.

## Arbeitspakete

1. Runtime-Wording präzisieren:
   - `characters/hud-system.md`
   - `core/sl-referenz.md`
   - `core/spieler-handbuch.md`
2. Prozessspiegel fortschreiben:
   - `internal/qa/process/hard-final-review-next-steps.md`
   - `internal/qa/process/known-issues.md`
3. QA-Log erfassen:
   - `internal/qa/logs/2026-03-11-issue-pack-durchlauf-213-chronopolis-kodex-restdrift.md`
4. Pflichtcheck ausführen:
   - `bash scripts/smoke.sh`

## Abnahme

- Keine unqualifizierte „Vollzugriff“-Formulierung mehr ohne `CITY`-Scope.
- Kodex-Befehl im Spieler-Handbuch explizit als `CITY`-gesperrt markiert.
- Pflicht-Smoke grün.
