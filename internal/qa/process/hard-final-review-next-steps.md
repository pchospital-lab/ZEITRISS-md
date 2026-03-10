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
  - `upload-snapshot-watchguard-ok`
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
  - Durchlauf 162: Resolver-Rollout auf
    `director-layer-watchguard`,
    `onboarding-start-save-watchguard` und
    `iti-hardcanon-watchguard` erweitert.
  - Durchlauf 163: Upload-Kontext (`uploads/hard-final-review.md`) per
    Pflicht-Watchguard abgesichert (`upload-snapshot-watchguard-ok`).
  - Durchlauf 164: Resolver-Rollout auf
    `ruf-alien-watchguard`,
    `physicality-watchguard` und
    `kausalabfang-watchguard` erweitert.

## Offene Anschluss-Tasks (priorisiert)

1. **Resolver-Rollout bei neuen/angepassten Guards fortführen**
   - Bei jeder künftigen Guard-Neuanlage standardmäßig
     `resolveUniqueMarkdownTarget` nutzen und keine Einzellösungen mehr
     einführen.
2. **Prozessseiten weiter schlank halten**
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
