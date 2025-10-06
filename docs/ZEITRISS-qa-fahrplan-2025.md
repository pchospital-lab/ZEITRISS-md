---
title: "ZEITRISS QA-Fahrplan 2025"
version: 1.2.0
tags: [meta]
---

# ZEITRISS QA-Fahrplan 2025

## Zielbild
Der Fahrplan bündelt sämtliche QA-Aufgaben für ZEITRISS 2025. Er knüpft an die
Copy-&-Paste-Protokolle aus Beta-GPT- und MyGPT-Tests an, priorisiert die daraus
abgeleiteten Maßnahmen und verweist auf die zugehörigen Artefakte. Prozess- und
Formatregeln stehen in `AGENTS.md`, `CONTRIBUTING.md` sowie
[maintainer-ops.md](maintainer-ops.md); dieses Dokument konzentriert
sich ausschließlich auf QA-Inhalte, Status und Nachverfolgung.

## QA-Zyklus
1. **Vorbereitung:** Maintainer:innen aktualisieren den Wissensstand gemäß
   Maintainer-Ops und stellen sicher, dass Beta-GPT und MyGPT denselben Content
   erhalten.
2. **Testlauf:** Tester:innen führen den Playtest anhand des
   [Copy-&-Paste-Auftrags](tester-playtest-briefing.md) durch, lassen den GPT den
   kompletten QA-Lauf eigenständig simulieren und prüfen das Ergebnis auf die
   geforderten `ISSUE`-, `Lösungsvorschlag`-, `To-do`- und `Nächste Schritte`-
   Blöcke.
3. **Archivierung:** Das vollständige Chatprotokoll wird unter
   `internal/qa/2025-beta-qa-log.md` eingetragen und mit Datum, Plattform und
   Build versehen.
4. **Aufgabenaufbereitung:** Codex überführt die strukturierten Blöcke in diesen
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

## Regressionstest-Termine 2025

- **Q1 2025 (19.03.2025 – Acceptance-Smoke-Abgleich)**
  - Umfang: Vollständiger Regressionstest (Build 4.2.2) mit Save/Load und Boss-Gates.
  - Status: ✅ abgeschlossen.
  - QA-Log: `internal/qa/2025-beta-qa-log.md`, Abschnitt 2025-03-19.
- **Q2 2025 (09.–13.06.2025)**
  - Umfang: Regressionstest im MyGPT-Beta-Klon mit Fokus auf Spiegelprozesse und Save-Restore.
  - Status: 🗓️ geplant.
  - QA-Log: Eintrag folgt nach Lauf.
- **Q3 2025 (08.–12.09.2025)**
  - Umfang: Regressionstest im MyGPT-Beta-Klon mit Arena- und Großteam-Schwerpunkt.
  - Status: 🗓️ geplant.
  - QA-Log: Eintrag folgt nach Lauf.
- **Q4 2025 (08.–12.12.2025)**
  - Umfang: Regressionstest im MyGPT-Beta-Klon mit Jahresabschluss- und Spiegelkontrolle.
  - Status: 🗓️ geplant.
  - QA-Log: Eintrag folgt nach Lauf.

## Maßnahmen-Backlog (Priorisiert)
### Sprint 1 – sofort angehen
- [x] README-Querverweise auf Audit, Fahrplan und QA-Log ergänzen.
  (2025-03-17 – QA-Log 2025-03-17, Commit: 131046d)
- [x] CONTRIBUTING-Abschnitt "Beta-GPT & QA-Übergaben" gegen den neuen
  QA-Zyklus prüfen und anpassen.
  (2025-03-17 – QA-Log 2025-03-17, Commits: 131046d, 03dad05)
- [x] QA-Log (`internal/qa/2025-beta-qa-log.md`) mit erstem Testprotokoll füllen
  und Prioritäten in diesem Fahrplan verlinken.
  (2025-03-17 – QA-Log 2025-03-17, Commit: 131046d)
- [x] QA-Fahrplan überarbeiten (dieses Dokument).
  (2025-03-17 – QA-Log 2025-03-17, Commits: 5cbfce8, d2a3b4c, 3338360)

### Sprint 2 – innerhalb der nächsten zwei Iterationen
- [x] Acceptance-Smoke-Checkliste gegen aktuelle Runtime-Skripte spiegeln
  (Boss-Gates, HUD-Badges, Psi-Heat) und Ergebnisse im QA-Log dokumentieren.
  (2025-03-23 – QA-Log 2025-03-19, Commit: e4d2872)
- [x] Maintainer-Ops anpassen: MyGPT als alleinige QA-Plattform herausstellen
  und Spiegelprozesse für Store-GPT, LUMO und lokale Instanzen dokumentieren.
  (2025-03-21 – Maintainer-Ops 1.2.0, Commit: d2a3b4c)
- [x] CHANGELOG-Einträge mit QA-Nachweisen versehen (Verweis auf QA-Log-Abschnitte).
  (2025-03-26 – QA-Log 2025-03-19 & 2025-03-17 verlinkt, Commit: e5da4ad)
- [x] Glossar um neue Terminologie aus Version 4.2.2 erweitern
  (Psi-Heat, Tier-Gates, Kodex-Badges) und Synchronität dokumentieren.
  (2025-03-26 – README-Glossar ergänzt, Commit: e5da4ad)
- [x] Audit-Abschnitte 11–20 gegen reale Commits spiegeln und Referenzen
  nachtragen.
  (2025-03-27 – QA-Log 2025-03-19 verlinkt, Commits: b245bef, 5a3fbb3,
  7d91e53, 8fe8de2, 52d1ba5, 9a1675d, 8208170, 22d3c33, 1be6f57)

### Sprint 3 – langfristig planen
- [x] Automatisierten Link-Lint für README und Docs in CI evaluieren und
  Ergebnis im QA-Log festhalten.
  (2025-03-30 – QA-Log 2025-03-30, Commit: 445b8ed)
- [x] Tooling erweitern, um YAML-Header und Pflichtfelder automatisiert zu
  prüfen (`tools/lint_runtime.py` erweitern) und QA-Nachweis ablegen.
  (2025-10-05 – QA-Log 2025-10-05, Commit: 868883a)
- [x] Wiederkehrende MyGPT-Regressionstests terminieren und Status pro Quartal
  protokollieren; Spiegelplattformen nur bei Bedarf kontrollieren.
  (2025-04-02 – QA-Log 2025-04-02, Commit: 3338360)

## Status-Dashboard (Stand: Überarbeitung 2025-04-02)
| Maßnahme | Status | Nächster Schritt | Owner |
| --- | --- | --- | --- |
| QA-Fahrplan aktualisieren | ✅ erledigt | Statusblock bei jeder Änderung aktualisieren | Maintainer-Team |
| README-Querverweise | ✅ 2025-03-17 | README-Änderungen stets mit QA-Verweisen abgleichen | Maintainer-Team |
| QA-Log initial füllen | ✅ 2025-03-17 | Folgeprotokolle hinzufügen | QA-Koordination |
| CONTRIBUTING anpassen | ✅ 2025-03-17 | QA-Übergaben halbjährlich auditieren | Docs-Verantwortliche |
| Acceptance-Smoke-Checkliste | ✅ 2025-03-23 | QA-Log 2025-03-19 referenzieren | Repo-Agent |
| Maintainer-Ops Spiegelprozesse | ✅ 2025-03-21 | Spiegelprozesse bei Plattform-Änderungen prüfen | Maintainer-Team |
| Automatisierte Link-Prüfung | ✅ 2025-03-30 | Link-Lint in CI-Läufen beobachten | Repo-Agent |
| Runtime-Lint YAML/Pflichtfelder | ✅ 2025-10-05 | QA-Log 2025-10-05 referenzieren | Repo-Agent |
| Plattform-Regressionstests | ✅ 2025-04-02 | Q2-Regressionstest protokollieren | QA-Koordination |
| CHANGELOG QA-Verweise | ✅ 2025-03-26 | QA-Log-Referenzen beibehalten | Repo-Agent |
| Glossar Terminologie 4.2.2 | ✅ 2025-03-26 | README-Glossar regelmäßig spiegeln | Docs-Verantwortliche |

## Pflege & Reporting
- Prüfe bei jeder Änderung, ob Audit und QA-Log entsprechende Einträge erhalten.
- Verweise in PR-Beschreibungen auf betroffene QA-Log-Abschnitte.
- Nutze Issues oder Projektboards für umfangreiche Maßnahmen und verknüpfe sie
  mit diesem Fahrplan.
- Dokumentiere Abschlüsse mit Datum und Commit in Audit und QA-Log, nicht in den
  Runtime-Dateien.
- Halte die Terminübersicht der Regressionstests aktuell und verweise nach jedem
  Lauf auf den entsprechenden QA-Log-Abschnitt.

> Aktualisiere den Statusabschnitt bei jeder Änderung dieses Fahrplans. Jede
> abgeschlossene Maßnahme erhält Datum, Commit-Referenz und Verweis auf das
> korrespondierende QA-Log.
