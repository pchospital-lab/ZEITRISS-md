---
title: "ZEITRISS Vereinheitlichungs-Fahrplan 2025"
version: 1.0.0
tags: [meta]
---

# ZEITRISS Vereinheitlichungs-Fahrplan 2025

## Zielsetzung
Dieser Fahrplan übersetzt die extern dokumentierten Vereinheitlichungs-Hinweise
in konkrete Aufgaben für ZEITRISS. Er priorisiert Sprach- und
Formatangleichungen, überprüft Metadaten und stärkt den vorgesehenen
QA-Workflow. Alle Schritte erfolgen gemäß `AGENTS.md`, `CONTRIBUTING.md` sowie
den Maintainer-Richtlinien.

## Maßnahmenübersicht
1. **Dokumentensprache vereinheitlichen**
   - README: Abschnittsüberschriften in konsistente deutsche Terminologie
     überführen (z. B. „Wie du beitragen kannst“ statt „How to Contribute“).
   - CONTRIBUTING: Frontmatter-Titel und Überschriften eindeutschen (z. B.
     „Beitragsrichtlinien“, „Rollen & Pflichten“).
   - Folgeprüfung: Stichtagskontrolle aller weiteren Root-Dokumente
     (`CHANGELOG.md`, `LICENSE`, `doc.md` usw.) auf verbliebene englische
     Überschriften.
2. **YAML-Frontmatter und Versionsstände prüfen**
   - Abgleich der `version`-Felder in README, CONTRIBUTING und relevanten
     `docs/`-Artefakten mit dem Maintainer-Stand.
   - Bei Anpassungen: Version hochzählen, Änderungsnotiz in `CHANGELOG.md`
     ergänzen und Veröffentlichungs-Checkliste aus `docs/maintainer-ops.md`
     anwenden.
3. **Lizenzhinweise schärfen**
   - LICENSE/LIZENZ-Übersicht auf vollständige Zuordnung (Texte: CC BY-NC 4.0,
     Code: MIT, Links zu Volltexten) prüfen.
   - README-Hinweis mit präziser Formulierung und funktionierendem Link
     hinterlegen.
   - Falls nötig: `docs/trademark.md` sowie weitere Rechtstexte für Konsistenz
     validieren.
4. **Begriffskonsistenz & Format-Checks**
   - Stichprobenartige Prüfung repräsentativer Runtime-Module aus `core/`,
     `gameplay/` und `systems/` gegen die in `AGENTS.md` definierte Checkliste
     (u. a. Terminologie „Rift-Seeds“, Ihr-Form, Szenenzählung).
   - Ergebnisse protokollieren und eventuelle Abweichungen als Issues oder
     Pull-Requests aufbereiten.
5. **KI-Review- und QA-Prozess aktiv nutzen**
   - Bei jedem größeren Diff: Review über ARXION oder äquivalente
     Vergleichs-KI anstoßen, Findings in `docs/ZEITRISS-qa-audit-2025.md`
     dokumentieren.
   - Beta-GPT-Playtests für spielrelevante Änderungen durchführen; Reports im
     QA-Fahrplan aktualisieren.
   - Commit- und PR-Notizen um ausgeführte Tests ergänzen (z. B. `make lint`,
     `make test`, `bash scripts/smoke.sh`).

## Zeitplan & Verantwortlichkeiten
- **Sprint 1 (Woche 1–2):** Sprachangleichung in README/CONTRIBUTING
  abschließen, Lizenzprüfung durchführen.
- **Sprint 2 (Woche 3):** YAML-Versionen aktualisieren, `CHANGELOG.md` und
  Maintainer-Checklisten synchronisieren.
- **Sprint 3 (Woche 4–5):** Runtime-Stichprobe durchführen, Ergebnisse
  dokumentieren, notwendige Nacharbeiten einplanen.
- **Kontinuierlich:** QA- und KI-Review-Prozesse bei jeder inhaltlichen
  Änderung anwenden und dokumentieren.

## Erfolgskriterien
- Keine englischsprachigen Überschriften oder Frontmatter-Titel in
  Root-Dokumenten.
- Lizenztext und Verweise vollständig, inkl. funktionierender Links auf CC- und
  MIT-Volltexte.
- YAML-Frontmatter spiegelt aktuelle Versionen wider; Versionserhöhungen
  nachvollziehbar im Changelog.
- Dokumentierte QA-/KI-Review-Ergebnisse im Audit-Log, keine offenen
  Terminologie-Abweichungen in Stichproben.

## Nachverfolgung
Pflege Fortschrittsupdates im Maintainer-Journal (`docs/maintainer-ops.md`) und
halte Review-Tickets in eurem Issue-Tracker aktuell. Bei Abweichungen sofort die
zuständigen Maintainer:innen informieren und Korrekturmaßnahmen planen.
