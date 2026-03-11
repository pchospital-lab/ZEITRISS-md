---
# Fahrplan – Durchlauf 209 (Chronopolis Kodex-Sperrmodus)

## Kontext

Die Chronopolis-Contract-Schärfung ist umgesetzt (freier Infiltrationslauf,
kein Save, Reaktionslogik), aber ein Rest-Unsync blieb in Kodex/HUD-Tonalität:
mehrere Stellen klangen noch wie durchgehend verfügbarer Kodex-Zugriff. Für
Playtests soll Chronopolis als eigener Sperrmodus klar lesbar sein
(_Kodex dunkel, HUD lebendig_).

## Ziel

- Chronopolis als eigenen Kodex-Sperrmodus in den zentralen Runtime-SSOT-Dateien
  synchronisieren.
- `!offline` in `CITY` explizit als Sperrmodus-Antwort (statt Re-Sync-Rezept)
  verankern.
- Anschlussfähigkeit sichern: Plan/Log/Prozessspiegel auf Durchlauf 209
  fortschreiben.

## Arbeitspakete

1. Runtime-SSOT angleichen:
   - `core/spieler-handbuch.md`
   - `core/sl-referenz.md`
   - `characters/hud-system.md`
   - `meta/masterprompt_v6.md`
   - `gameplay/kampagnenstruktur.md`
   - `systems/toolkit-gpt-spielleiter.md`
2. Prozessspiegel fortschreiben:
   - `internal/qa/process/hard-final-review-next-steps.md`
   - `internal/qa/process/known-issues.md`
3. QA-Log erfassen:
   - `internal/qa/logs/2026-03-11-issue-pack-durchlauf-209-chronopolis-kodex-sperrmodus.md`
4. Pflichtchecks ausführen:
   - `bash scripts/smoke.sh`
   - `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`

## Abnahme

- Chronopolis-Sperrmodus in allen oben genannten SSOT-Dateien konsistent
  formuliert.
- `!offline` differenziert zwischen Standard-Offline und Chronopolis-Sperrmodus.
- Pflicht-Smoke und Link-Lint laufen fehlerfrei.
