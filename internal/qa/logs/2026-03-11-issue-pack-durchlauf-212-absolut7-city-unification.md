# QA-Log – Durchlauf 212 (ABSOLUT-7/CITY Zusammenführung)

## Ausgangslage

Review-Hinweis: `ABSOLUT-7` wird aktuell doppelt gelesen (allgemeines
Projektionsmodell + Chronopolis-Lore-Guard). Gewünscht ist eine saubere
Zusammenführung, bei der Chronopolis klar als Zusatzfall geführt wird.

## Umsetzung

- Im Psi-Modul (`systems/kp-kraefte-psi.md`) einen expliziten
  **Chronopolis-Zusatz** als Anhang `ABSOLUT-7/CITY` ergänzt
  (Leseregel: CITY-Verweise meinen den Anhang, nicht ein zweites Modell).
- Runtime-SSOT synchron auf Marker `ABSOLUT-7/CITY` umgestellt:
  - `core/spieler-handbuch.md`
  - `core/sl-referenz.md`
  - `gameplay/kampagnenstruktur.md`
  - `meta/masterprompt_v6.md`
  - `systems/toolkit-gpt-spielleiter.md`

## Ergebnis

`ABSOLUT-7` bleibt das übergeordnete ITI-Projektionsmodell,
`ABSOLUT-7/CITY` ist der klar benannte Chronopolis-Zusatzfall.
Damit entfällt die doppelte Lesart bei gleichbleibendem Lore-Ton.

## Checks

- `bash scripts/smoke.sh` → bestanden.
