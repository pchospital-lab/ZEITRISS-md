---
title: "Log – Durchlauf 158 (Hard-Final-Review Prozesspflege / Known-Issues kompakt)"
date: 2026-03-10
status: abgeschlossen
owner: codex
scope: Meta/Prozess
issue: ZR-021
---

## Kontext

Anschluss auf den Hard-Final-Review-Fahrplan mit Fokus auf wartbare
Prozessseiten (`known-issues.md` + Anschlussübersicht) für Folge-Durchläufe.

## Umsetzung

- `internal/qa/process/known-issues.md` wurde auf eine kompakte
  Triage-Tabelle normalisiert (kurze Notizen statt Langprosa in Zellen).
- Detailverläufe verbleiben in bestehenden SSOT-Prozessquellen:
  - `internal/qa/process/issue-pack-statusmatrix.md`
  - `internal/qa/process/v7-save-load-statusmatrix.md`
  - `internal/qa/process/ruf-alien-statusmatrix.md`
  - `internal/qa/process/archive/known-issues-durchlaufhistorie-73-156.md`
- `internal/qa/process/hard-final-review-next-steps.md` wurde auf den
  Durchlauf-158-Stand synchronisiert.

## Ergebnis

- Prozessseiten sind für neue Anschlussläufe schneller erfassbar.
- Keine Runtime-Regeländerung; reine Meta-/Prozesspflege.

## Checks

- `bash scripts/smoke.sh` erfolgreich.
