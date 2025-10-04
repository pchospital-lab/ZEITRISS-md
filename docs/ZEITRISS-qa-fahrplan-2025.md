---
title: "ZEITRISS QA-Fahrplan 2025"
version: 1.0.0
tags: [meta]
---

# ZEITRISS QA-Fahrplan 2025

## Zielbild
Der Fahrplan bündelt alle Schritte, um ZEITRISS 2025 über Plattformen und Releases hinweg konsistent, geprüft und dokumentiert zu halten. Er dient als Arbeitsgrundlage für Maintainer:innen, QA-Agenten und beitragende KIs. Jede Maßnahme zielt darauf ab, den bestehenden Qualitätsstandard zu sichern, Inkonsistenzen früh zu erkennen und Aktualisierungen parallel in Repository und Wissensspeicher abzubilden.

## Leitprinzipien
- **Single Source of Truth.** README, master-index und Runtime-Module bleiben die maßgeblichen Referenzen. Meta-Dokumente (CONTRIBUTING, AGENTS, Maintainer-Ops) definieren Prozesse und werden bei Änderungen synchron gepflegt.
- **Strikte Trennung Runtime vs. Meta.** Laufzeit-Content bleibt frei von Dev-Hinweisen; alle QA- und Prozessnotizen tragen `tags: [meta]` und leben in `docs/` oder `meta/`.
- **Verpflichtende QA-Schleifen.** Kein Merge ohne erfolgreiche Lints, Tests, Smoke-Run und dokumentiertes Ergebnis.
- **Transparente Nachverfolgung.** Jede Änderung mit Auswirkung auf Spielverhalten, Dokumentation oder rechtliche Hinweise erhält einen Eintrag in CHANGELOG und QA-Log.
- **Terminologie-Hygiene.** Glossar und Toolkit-Begriffe gelten als verbindlich. Neue Begriffe werden sofort in Glossar, Runtime-Modulen und QA-Checklisten gespiegelt.

## Arbeitsstränge & Ziele
| Bereich | Zielzustand | Primäre Artefakte |
| --- | --- | --- |
| Dokumentation | README, Repo-Map und Maintainer-Doku spiegeln denselben Aufbau, verlinken QA-Fahrplan und Audit-Log. | README, docs/ZEITRISS-qa-fahrplan-2025.md, docs/ZEITRISS-qa-audit-2025.md |
| Beitragsprozesse | CONTRIBUTING verweist auf Agents-Regeln, QA-Checklisten und Changelog-Pflichten; Branch- und Commit-Standards eingehalten. | CONTRIBUTING.md, AGENTS.md |
| Tests & Automation | make lint, make test, scripts/smoke.sh laufen lokal und in CI stabil; Smoke-Reports werden archiviert. | Makefile, scripts/smoke.sh, QA-Logs |
| Recht & Lizenzen | Lizenz, Markenhinweise und Disclaimer sind aktuell, datiert und in README sowie LICENSE konsistent. | README.md, LICENSE, docs/trademark.md |

## Maßnahmen-Backlog (Priorisiert)
### Sprint 1 – sofort angehen
- [ ] README-Querverweise prüfen, ob neue QA-Dokumente (Fahrplan, Audit) überall genannt werden.
- [ ] CONTRIBUTING-Abschnitt "QA und Wartung" um explizite Referenz auf QA-Fahrplan erweitern.
- [ ] Scripts: Smoke-Test-Ergebnisformat dokumentieren (Template im QA-Log hinterlegen).
- [x] QA-Fahrplan erstellen und im Repo ablegen (dieses Dokument).

### Sprint 2 – innerhalb der nächsten zwei Iterationen
- [ ] Acceptance-Smoke-Checkliste gegen aktuelle Runtime-Skripte spiegeln (Boss-Gates, HUD-Badges, Psi-Heat).
- [ ] Maintainer-Ops mit Plattform-spezifischen QA-Tasks für 2025 ergänzen (z. B. LUMO Save/Load-Protokoll).
- [ ] CHANGELOG-Einträge mit QA-Hinweisen anreichern (welche Tests liefen für jede Version?).
- [ ] Glossar um neue Terminologie aus Version 4.2.2 erweitern (Psi-Heat, Tier-Gates, Kodex-Badges).

### Sprint 3 – langfristig planen
- [ ] Automatisierten Link-Lint für README/Docs in CI aufnehmen.
- [ ] Tooling erweitern, um YAML-Header und Pflichtfelder automatisiert zu prüfen (`tools/lint_runtime.py` ausbauen).
- [ ] Regelmäßige Plattform-Regressionstests (MyGPT, LUMO, lokal) als wiederkehrenden Termin im Maintainer-Kalender verankern.

## Wiederkehrende Checklisten
### Vor jedem Commit / PR
- [ ] `make lint`, `make test`, `scripts/smoke.sh` lokal erfolgreich ausgeführt.
- [ ] CHANGELOG und relevante Dokumentation aktualisiert, falls Verhalten oder Prozesse betroffen sind.
- [ ] QA-Fahrplan und Audit-Log geprüft: offener Punkt referenziert oder aktualisiert.
- [ ] Branch folgt Namensschema `topic/kurzbeschreibung`; Commit-Message im Imperativ mit Scope-Prefix (`docs:`, `fix:` ...).

### Vor Release-Freeze
- [ ] Alle Plattformen (MyGPT, LUMO, Ollama/OpenWebUI) tragen denselben Wissensstand.
- [ ] Release-Checkliste aus `docs/maintainer-ops.md` vollständig abgearbeitet.
- [ ] QA-Audit aktualisiert (neue Tests, Auffälligkeiten, offene Fragen).
- [ ] Rechtliche Hinweise (Markenbriefing, Impressum, LICENSE) mit aktueller Versionsnummer versehen.

### Quartalsweise Review
- [ ] QA-Fahrplan gegen reale Umsetzungen spiegeln und Status-Spalte aktualisieren.
- [ ] Agents-Checkliste auf neue Regeln oder Tooling-Anforderungen prüfen.
- [ ] Prüfen, ob zusätzliche Automatisierung (z. B. Pre-commit Hooks) aufgenommen werden muss.
- [ ] Plattform-Monitoring: Upload-Prozesse testen und etwaige API-/Plattformänderungen dokumentieren.

## Status-Dashboard (Stand: initialer Commit)
| Maßnahme | Status | Nächster Schritt | Owner |
| --- | --- | --- | --- |
| QA-Fahrplan veröffentlichen | ✅ erledigt | README/Docs verlinken | Maintainer-Team |
| README-Querverweise auf QA-Dokumente | ⚪ offen | Prüfen & ergänzen | Maintainer-Team |
| CONTRIBUTING um QA-Verweise ergänzen | ⚪ offen | Abschnitt überarbeiten | Docs-Verantwortliche |
| Automatisierte Link-Prüfung | ⚪ geplant | Tooling evaluieren | Repo-Agent |
| Plattform-Regressionstests 2025 | ⚪ geplant | Testtermine anlegen | QA-Koordination |

## Nächste Schritte
1. Repo-Map und Maintainer-Doku um Verweis auf diesen Fahrplan ergänzen.
2. PR anlegen, der CONTRIBUTING und Maintainer-Ops mit klaren QA-Verweisen aktualisiert.
3. Acceptance-Smoke-Checkliste mit aktuellen Mechaniken gegenprüfen und Delta dokumentieren.
4. Ergebnisse im QA-Audit loggen und Fortschritt im Dashboard aktualisieren.

> **Hinweis:** Aktualisiere den Statusabschnitt bei jeder Änderung dieses Fahrplans. Jede abgeschlossene Maßnahme erhält Datum und Commit-Referenz im QA-Audit.
