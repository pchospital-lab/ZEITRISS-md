---
title: "Issue-Pack Fahrplan – Durchlauf 38"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 38

Quelle: Fortsetzung ZR-016 mit Fokus auf formalen Abschluss der verbliebenen
Nachpflege aus der neuen Statusmatrix (Issue 1 + 6) und sauberer Übergabe in
künftige, eigenständige Known-Issues.

## Ziel

ZR-016 prozessual schließen: Reststatus synchronisieren, Abschlusskriterien
sichtbar dokumentieren und den Primärindex (`issue-pack-statusmatrix.md`) als
stabile Anschlussbasis für Folgearbeit konsolidieren.

## Scope dieses Durchlaufs

- `internal/qa/process/issue-pack-statusmatrix.md` (Status-Sync + Closure-Text)
- `internal/qa/process/known-issues.md` (ZR-016 Status auf abgeschlossen)
- QA-Nachführung: Plan + Log

## Nicht im Scope

- Neue Runtime-Regeländerungen in den WS-Modulen.
- Umbau bestehender Lint-/Test-Logik außerhalb der laufenden Smoke-Checks.
- Rückwirkende Neuformatierung alter Durchlauf-Logs.

## Exit-Kriterium für Durchlauf 38

- Statusmatrix markiert alle 13 Pack-Issues konsistent als abgeschlossen bzw.
  abgeschlossen verifiziert.
- Known-Issues-Eintrag ZR-016 ist formal auf `abgeschlossen` gesetzt und
  verweist weiterhin auf die Statusmatrix als Primärindex.
- `bash scripts/smoke.sh` läuft vollständig grün.
