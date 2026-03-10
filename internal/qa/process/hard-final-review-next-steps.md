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

## Offene Anschluss-Tasks (priorisiert)

1. **QA-Übersicht weiter entrümpeln**
   - Historische Langläufe in Prozessdokumenten perspektivisch in Archive
     verschieben; aktive Übersichten kurz halten.
2. **Watchguard-Zielpfade stabil halten**
   - Bei künftigen Makro-Umzügen den neuen
     `chronopolis-gate-watchguard` auf den gültigen Runtime-Pfad nachziehen.
3. **Upload-Kontext klar markieren**
   - Historische Upload-Reviews weiterhin als Snapshot
     kennzeichnen, damit sie nicht mit aktuellem SSOT-Status verwechselt werden.

## Operativer Ablauf für nächste Durchläufe

1. Scope im neuen Plan unter `internal/qa/plans/` festhalten.
2. Änderungen durchführen.
3. `bash scripts/smoke.sh` ausführen.
4. Ergebnis im Log unter `internal/qa/logs/` dokumentieren.
5. `known-issues.md` + diese Anschlussübersicht synchron aktualisieren.

## Referenzen

- Prozessstatus: `internal/qa/process/known-issues.md`
- Historischer Review-Snapshot: `uploads/hard-final-review.md`
