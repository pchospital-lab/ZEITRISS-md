---
# Fahrplan – Durchlauf 210 (Chronopolis Sperrmodus Wording-Fix)

## Kontext

Nach Durchlauf 209 blieb ein Präzisierungsbedarf in zwei Formulierungen:
1) SaveGuard-Re-Sync-Satz in der SL-Referenz klang so, als könnte HQ trotz
   Missionsende weiterhin generell offline sein.
2) Sperrmodus-Begründung sollte explizit benennen, dass Kodex die temporäre
   Chronopolis-Instanz selbst erzeugt und Live-Interaktion Echo-Kollapsrisiko
   für die Instanz inkl. Crew erzeugen kann.

## Ziel

- Wording auf den beabsichtigten Runtime-Contract schärfen.
- Missverständnisse zu HQ-Re-Sync und Chronopolis-Echo-Risiko entfernen.

## Arbeitspakete

1. Formulierung in `core/sl-referenz.md` präzisieren (SaveGuard-Re-Sync-Scope).
2. Formulierung in `characters/hud-system.md` präzisieren (Echo-Kollapsrisiko).
3. Masterprompt-Begründung in `meta/masterprompt_v6.md` spiegeln.
4. Prozessspiegel fortschreiben (`hard-final-review-next-steps.md`, `known-issues.md`).
5. Pflichtcheck ausführen: `bash scripts/smoke.sh`.

## Abnahme

- Kein missverständlicher HQ-offline-Dauereindruck mehr.
- Echo-Begründung nennt Instanz-/Crew-Risiko klar.
- Pflicht-Smoke grün.
