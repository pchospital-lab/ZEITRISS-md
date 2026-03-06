---
title: "Known Issues & Triage-Prozess"
version: 1.0.0
tags: [meta, qa]
---

# Known Issues & Triage-Prozess

Diese Seite bündelt den Prozess für offene QA-Funde, die nicht direkt im
Runtime-Content gelöst werden (z. B. Tooling-, Workflow- oder Plattformfragen).

## Ziel

- Einheitlicher Ort für Triagestatus (`neu`, `geprüft`, `geplant`,
  `in Umsetzung`, `abgeschlossen`, `verworfen`).
- Klare Verlinkung zwischen Eingangsquelle, Fahrplan, Log und Umsetzung.
- Saubere Trennung zwischen Runtime-Änderungen und Meta-Prozessarbeit.

## Prozess (leichtgewichtig)

1. **Erfassen**
   - Issue im QA-Log benennen und mit Quelle verlinken (Upload, Playtest,
     Audit, Maintainer-Report).
2. **Triagieren**
   - Priorität (`P0`–`P3`), Scope (Runtime/Meta/Tooling) und Besitzer:in
     festlegen.
3. **Planen**
   - Falls umsetzungsrelevant: Ticket in den Fahrplan (`internal/qa/plans/`)
     aufnehmen.
4. **Umsetzen**
   - Änderungen im Repo durchführen, Pflichtprüfungen laufen lassen,
     Commit/PR mit Referenz auf den QA-Eintrag versehen.
5. **Abschließen**
   - Status in dieser Liste, im QA-Log und im Fahrplan synchron auf
     `abgeschlossen` oder `verworfen` setzen.

## Aktuelle Known Issues

| ID | Titel | Quelle | Priorität | Scope | Status | Notiz |
| --- | --- | --- | --- | --- | --- | --- |
| ZR-015 | Interne QA-Known-Issues in GitHub-Issue-Triage spiegeln | `uploads/deep-research-report(4).md` | P3 | Meta/Prozess | abgeschlossen | Diese Prozessseite ist der kanonische Startpunkt; operative Arbeit läuft weiterhin über Fahrplan + QA-Log. |
| ZR-016 | Externer Codex-Issue-Pack in iterative Fahrplan-Cluster überführen | `uploads/ZEITRISS_codex_issue_pack.md` | P0 | Runtime/QA | in Umsetzung | Durchläufe dokumentiert unter `internal/qa/plans/issue-pack-durchlauf-01.md`, `internal/qa/plans/issue-pack-durchlauf-02.md`, `internal/qa/plans/issue-pack-durchlauf-03.md` und `internal/qa/plans/issue-pack-durchlauf-04.md`, `internal/qa/plans/issue-pack-durchlauf-05.md`, `internal/qa/plans/issue-pack-durchlauf-06.md`, `internal/qa/plans/issue-pack-durchlauf-07.md` und `internal/qa/plans/issue-pack-durchlauf-08.md` und `internal/qa/plans/issue-pack-durchlauf-09.md` und `internal/qa/plans/issue-pack-durchlauf-10.md` und `internal/qa/plans/issue-pack-durchlauf-11.md`; QA-Logs unter `internal/qa/logs/2026-03-06-issue-pack-durchlauf-01.md`, `internal/qa/logs/2026-03-06-issue-pack-durchlauf-02.md`, `internal/qa/logs/2026-03-06-issue-pack-durchlauf-03.md`, `internal/qa/logs/2026-03-06-issue-pack-durchlauf-04.md`, `internal/qa/logs/2026-03-06-issue-pack-durchlauf-05.md`, `internal/qa/logs/2026-03-06-issue-pack-durchlauf-06.md`, `internal/qa/logs/2026-03-06-issue-pack-durchlauf-07.md` und `internal/qa/logs/2026-03-06-issue-pack-durchlauf-08.md` und `internal/qa/logs/2026-03-06-issue-pack-durchlauf-09.md` und `internal/qa/logs/2026-03-06-issue-pack-durchlauf-10.md` und `internal/qa/logs/2026-03-06-issue-pack-durchlauf-11.md`. |

## Pflegehinweis

Neue Meta-Issues werden zuerst hier erfasst und danach in Fahrplan/Log
verknüpft. Runtime-Issues bleiben primär im Fahrplan, werden aber bei
prozessualem Bedarf mit Referenz in dieser Datei gespiegelt.
