# Fahrplan – Durchlauf 207 (Playtest-Readiness-Gate)

## Kontext

Die harten Runtime-/Prozess-Drifts sind bis Durchlauf 206 geschlossen.
Vor dem nächsten größeren Playtest-Lauf fehlt jedoch ein kompakter,
operativer Go/No-Go-Gate, der die bereits bestehenden Anforderungen aus
Smoke, WS-Setup und Tester-Briefing in einer kurzen Checkliste bündelt.

## Ziel

- Einen klaren Playtest-Readiness-Gate als Prozessdokument verankern.
- Anschlussfähigkeit sichern: Plan/Log/Prozessspiegel konsistent auf
  Durchlauf 207 fortschreiben.

## Arbeitspakete

1. Neues Prozessdokument anlegen:
   - `internal/qa/process/playtest-readiness-gate.md`
2. Prozessspiegel aktualisieren:
   - `internal/qa/process/hard-final-review-next-steps.md`
   - `internal/qa/process/known-issues.md` (ZR-021)
3. QA-Log für Durchlauf 207 erfassen:
   - `internal/qa/logs/2026-03-11-issue-pack-durchlauf-207-playtest-readiness-gate.md`
4. Pflichtcheck ausführen:
   - `bash scripts/smoke.sh`

## Abnahme

- Der neue Gate enthält eine kurze, ausführbare Go/No-Go-Liste
  (Setup, Pflicht-Smoke, zentrale Invarianten, Evidence-Ablage).
- Hard-Final-Anschlussübersicht und Known-Issues spiegeln Durchlauf 207.
- Pflicht-Smoke läuft ohne Fehler.
