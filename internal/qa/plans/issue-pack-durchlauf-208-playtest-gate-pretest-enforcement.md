# Fahrplan – Durchlauf 208 (Playtest-Gate Pretest-Enforcement)

## Kontext

Durchlauf 207 hat den Playtest-Readiness-Gate als eigenes Prozessdokument
angelegt. Für einen robusten Anschlusslauf fehlt noch die explizite
Verankerung dieses Gates in den operativen Pre-Test-Checklisten, damit der
Gate nicht nur existiert, sondern vor externen Läufen verbindlich ausgeführt
wird.

## Ziel

- Playtest-Readiness-Gate in den relevanten Pre-Test-Workflows verpflichtend
  referenzieren.
- Anschlussfähigkeit sichern: Fahrplan/Log/Prozessspiegel für Durchlauf 208
  konsistent fortschreiben.

## Arbeitspakete

1. Operative Playtest-Checkliste aktualisieren:
   - `docs/qa/tester-playtest-briefing.md`
2. Prozess-Checkliste für Anschlussläufe nachziehen:
   - `internal/qa/process/continuity-redesign-statusmatrix.md`
3. Prozessspiegel fortschreiben:
   - `internal/qa/process/hard-final-review-next-steps.md`
   - `internal/qa/process/known-issues.md` (ZR-021 um Durchlauf 208 ergänzen)
4. QA-Log für Durchlauf 208 erfassen:
   - `internal/qa/logs/2026-03-11-issue-pack-durchlauf-208-playtest-gate-pretest-enforcement.md`
5. Pflichtcheck + Linklint ausführen:
   - `bash scripts/smoke.sh`
   - `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`

## Abnahme

- Playtest-Gate ist in den operativen Pre-Test-Checklisten explizit als
  Pflicht vor externen Testläufen referenziert.
- Hard-Final-Anschlussübersicht und Known-Issues spiegeln Durchlauf 208.
- Pflicht-Smoke und Linklint laufen ohne Fehler.
