---
title: "ZEITRISS QA-Fahrplan 2025"
version: 1.1.0
tags: [meta]
---

# ZEITRISS QA-Fahrplan 2025

## Zielbild
Der Fahrplan bündelt sämtliche QA-Aufgaben für ZEITRISS 2025. Er knüpft an die
Copy-&-Paste-Protokolle aus Beta-GPT- und MyGPT-Tests an, priorisiert die daraus
abgeleiteten Maßnahmen und verweist auf die zugehörigen Artefakte. Prozess- und
Formatregeln stehen in `AGENTS.md`, `CONTRIBUTING.md` sowie
[docs/maintainer-ops.md](docs/maintainer-ops.md); dieses Dokument konzentriert
sich ausschließlich auf QA-Inhalte, Status und Nachverfolgung.

## QA-Zyklus
1. **Vorbereitung:** Maintainer:innen aktualisieren den Wissensstand gemäß
   Maintainer-Ops und stellen sicher, dass Beta-GPT und MyGPT denselben Content
   erhalten.
2. **Testlauf:** Tester:innen führen den Playtest anhand des
   [Copy-&-Paste-Auftrags](docs/tester-playtest-briefing.md) durch.
3. **Archivierung:** Das vollständige Chatprotokoll wird unter
   `internal/qa/2025-beta-qa-log.md` eingetragen und mit Datum, Plattform und
   Build versehen.
4. **Aufgabenaufbereitung:** Codex überführt die offenen Punkte in diesen
   Fahrplan (Status, Priorität) und versieht sie mit Verweisen auf Commits, PRs
   oder Issues.
5. **Umsetzung:** Maßnahmen laufen in separaten Branches; Testbefehle und
   Ergebnisse werden im Commit-Body dokumentiert.
6. **Review & Sync:** Nach Abschluss einer Maßnahme wird das Audit aktualisiert,
   der Abschnitt im QA-Log abgehakt und gegebenenfalls ein weiterer Beta-Test
   gestartet.

## Rollen & Übergabe
- **Maintainer:innen** halten Wissensstände synchron, bauen Beta-GPT-Instanzen
  und stoßen Tests an.
- **Tester:innen** dokumentieren Ergebnisse unverändert und liefern sie an Codex
  über das QA-Log.
- **Codex (Repo-Agent)** priorisiert die Befunde, setzt Änderungen um und
  aktualisiert Audit, Fahrplan sowie Referenzdokumente.
- **Audit-Archiv:** `docs/ZEITRISS-qa-audit-2025.md` (Zusammenfassung) und
  `internal/qa/` (vollständige Logs).

## Arbeitsstränge & Ziele
- **Dokumentation & Index:** README, Repo-Map und Index spiegeln QA-Dokumente
  und verlinken Audit sowie Fahrplan konsistent.
  - Artefakte: `README.md`, `master-index.json`, QA-Dokumente
- **Beitragsprozesse:** Verweise auf QA-Workflow in `CONTRIBUTING.md` und
  `AGENTS.md` aktuell halten.
  - Artefakte: `CONTRIBUTING.md`, `AGENTS.md`
- **Tests & Automation:** Makefile- und Script-Läufe dokumentieren; Smoke- und
  Spezialtests werden im QA-Log referenziert.
  - Artefakte: `Makefile`, `scripts/smoke.sh`, QA-Log-Einträge
- **Datenschutz & Plattformen:** Plattformhinweise und Offline-First-Vorgaben
  bleiben in Maintainer-Ops, Audit und Fahrplan synchron.
  - Artefakte: `docs/maintainer-ops.md`, Audit, QA-Log
- **Recht & Compliance:** Lizenz- und Markenhinweise mit QA-Maßnahmen abgleichen
  und bei Bedarf PRs initiieren.
  - Artefakte: `LICENSE`, `docs/trademark.md`, QA-Log-Referenzen

## Maßnahmen-Backlog (Priorisiert)
### Sprint 1 – sofort angehen
- [x] README-Querverweise auf Audit, Fahrplan und QA-Log ergänzen. (2025-03-17 – QA-Log 2025-03-17, Commit: folgt nach Merge)
- [x] CONTRIBUTING-Abschnitt "Beta-GPT & QA-Übergaben" gegen den neuen
  QA-Zyklus prüfen und anpassen. (2025-03-17 – QA-Log 2025-03-17, Commit: folgt nach Merge)
- [x] QA-Log (`internal/qa/2025-beta-qa-log.md`) mit erstem Testprotokoll füllen
  und Prioritäten in diesem Fahrplan verlinken. (2025-03-17 – QA-Log 2025-03-17, Commit: folgt nach Merge)
- [x] QA-Fahrplan überarbeiten (dieses Dokument).

### Sprint 2 – innerhalb der nächsten zwei Iterationen
- [ ] Acceptance-Smoke-Checkliste gegen aktuelle Runtime-Skripte spiegeln
  (Boss-Gates, HUD-Badges, Psi-Heat) und Ergebnisse im QA-Log dokumentieren.
- [ ] Maintainer-Ops anpassen: MyGPT als alleinige QA-Plattform herausstellen und Spiegelprozesse für Store-GPT, LUMO und lokale Instanzen dokumentieren.
- [ ] CHANGELOG-Einträge mit QA-Nachweisen versehen (Verweis auf QA-Log-Abschnitte).
- [ ] Glossar um neue Terminologie aus Version 4.2.2 erweitern
  (Psi-Heat, Tier-Gates, Kodex-Badges) und Synchronität dokumentieren.
- [ ] Audit-Abschnitte 11–20 gegen reale Commits spiegeln und Referenzen
  nachtragen.

### Sprint 3 – langfristig planen
- [ ] Automatisierten Link-Lint für README und Docs in CI evaluieren und
  Ergebnis im QA-Log festhalten.
- [ ] Tooling erweitern, um YAML-Header und Pflichtfelder automatisiert zu
  prüfen (`tools/lint_runtime.py` erweitern) und QA-Nachweis ablegen.
- [ ] Wiederkehrende MyGPT-Regressionstests terminieren und Status pro Quartal protokollieren; Spiegelplattformen nur bei Bedarf kontrollieren.

## Status-Dashboard (Stand: Überarbeitung 2025-03-17)
| Maßnahme | Status | Nächster Schritt | Owner |
| --- | --- | --- | --- |
| QA-Fahrplan aktualisieren | ✅ erledigt | README-Referenz prüfen | Maintainer-Team |
| README-Querverweise | ✅ 2025-03-17 | Commit-Verweis nach Merge ergänzen | Maintainer-Team |
| QA-Log initial füllen | ✅ 2025-03-17 | Folgeprotokolle hinzufügen | QA-Koordination |
| CONTRIBUTING anpassen | ✅ 2025-03-17 | Commit-Verweis nach Merge ergänzen | Docs-Verantwortliche |
| Automatisierte Link-Prüfung | ⚪ geplant | Tooling evaluieren | Repo-Agent |
| Plattform-Regressionstests | ⚪ geplant | Termine festlegen | QA-Koordination |

## Pflege & Reporting
- Prüfe bei jeder Änderung, ob Audit und QA-Log entsprechende Einträge erhalten.
- Verweise in PR-Beschreibungen auf betroffene QA-Log-Abschnitte.
- Nutze Issues oder Projektboards für umfangreiche Maßnahmen und verknüpfe sie
  mit diesem Fahrplan.
- Dokumentiere Abschlüsse mit Datum und Commit in Audit und QA-Log, nicht in den
  Runtime-Dateien.

> Aktualisiere den Statusabschnitt bei jeder Änderung dieses Fahrplans. Jede
> abgeschlossene Maßnahme erhält Datum, Commit-Referenz und Verweis auf das
> korrespondierende QA-Log.
