---
title: "Hard-Final-Review – Anschlussübersicht"
date: 2026-03-10
status: aktiv
owner: codex
scope: Runtime/QA + Meta/Prozess
---

# Zweck

Diese Seite ist die kompakte Arbeitsübersicht nach Abschluss der Hard-Final-
Review-Runde (Durchläufe 145–154). Sie dient als schneller Einstieg für den
nächsten Anschlusslauf.

## Aktueller Stand (Kurzfassung)

- ZR-021 ist in `known-issues.md` als **abgeschlossen** dokumentiert.
- Die Kernpunkte aus dem Hard Final Review sind umgesetzt und über
  Pflicht-Watchguards im Smoke abgesichert:
  - `default-slot-dependency-watchguard-ok`
  - `director-layer-watchguard-ok`
  - `hard-final-review-watchguard-ok`
  - `chronopolis-gate-watchguard-ok`
- Pflicht-Smoke bleibt der zentrale Merge-Gate-Check.
- Die Prozessseiten sind auf operativen Einstieg getrimmt:
  - Durchlauf 157: Historie 73–156 aus `known-issues.md` archiviert.
  - Durchlauf 158: `known-issues.md` auf kompakte Triage-Notizen reduziert;
    Detailstände liegen in den jeweiligen Statusmatrizen/Archivdateien.
  - Durchlauf 159: `chronopolis-gate-watchguard` auf robuste
    Zielpfad-Ermittlung gehärtet (weniger manuelle Pflege bei Makro-Umzügen).
  - Durchlauf 160: gemeinsame Resolver-Utility für robuste
    Watchguard-Zielpfadauflösung in `tools/` eingeführt und im
    `chronopolis-gate-watchguard` produktiv genutzt.
  - Durchlauf 161: Resolver-Rollout auf
    `default-slot-dependency-watchguard` und
    `hard-final-review-watchguard` erweitert.

## Offene Anschluss-Tasks (priorisiert)

1. **Weitere Runtime-Watchguards auf die Resolver-Utility umziehen**
   - Restliche Guards (z. B. Director-/Onboarding-/ITI-Guards) bei nächster
     inhaltlicher Berührung auf die gemeinsame Zielpfad-Auflösung
     standardisieren.
2. **Upload-Kontext klar markieren**
   - Historische Upload-Reviews weiterhin als Snapshot kennzeichnen,
     damit sie nicht mit aktuellem SSOT-Status verwechselt werden.
3. **Prozessseiten weiter schlank halten**
   - Lange Durchlaufprosa nur in Archive/Statusmatrizen führen,
     aktive Seiten auf Triage-/Anschlussinformationen begrenzen.

## Operativer Ablauf für nächste Durchläufe

1. Scope im neuen Plan unter `internal/qa/plans/` festhalten.
2. Änderungen durchführen.
3. `bash scripts/smoke.sh` ausführen.
4. Ergebnis im Log unter `internal/qa/logs/` dokumentieren.
5. `known-issues.md` + diese Anschlussübersicht synchron aktualisieren.

## Referenzen

- Prozessstatus: `internal/qa/process/known-issues.md`
- Historischer Review-Snapshot: `uploads/hard-final-review.md`

---
