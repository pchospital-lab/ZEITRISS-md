---
title: "GitHub Public-Checkliste (Solo-Maintainer)"
version: 1.0.0
tags: [meta]
---

# GitHub Public-Checkliste (Solo-Maintainer)

Diese Checkliste ist für die finale Freigabe eines öffentlichen ZEITRISS-Repositories gedacht.
Zielbild: **Lesen, herunterladen, Issues melden** – keine externe PR-Pipeline.

## 1) Repository-Features

- [ ] **Issues aktiv** (für Bugs/Vorschläge).
- [ ] **Discussions deaktivieren** (falls kein Forum gewünscht).
- [ ] **Projects deaktivieren** (falls nicht genutzt).
- [ ] **Wiki deaktivieren** (wenn keine separate Doku dort gepflegt wird).

## 2) Pull-Request-Kanal minimieren

- [ ] PR-Template vorhanden (`.github/PULL_REQUEST_TEMPLATE.md`) mit Hinweis auf Issue-Only-Feedback.
- [ ] Workflow zum Schließen externer PRs aktiv (`.github/workflows/close-external-prs.yml`).
- [ ] Community-Policy verweist klar auf Issue-basiertes Feedback.

## 3) Issue-Erstellung steuern

- [ ] `blank_issues_enabled: false` in `.github/ISSUE_TEMPLATE/config.yml` gesetzt.
- [ ] Mindestens ein Content-/Bug-Template vorhanden.
- [ ] Security-Template + Verweis auf private Meldung vorhanden.
- [ ] Contact-Links führen auf README/Policy/Security-Mail.

## 4) Security & Vertrauen

- [ ] **Private vulnerability reporting** in GitHub-Settings aktivieren.
- [ ] `SECURITY.md` enthält Mailkontakt und gewünschte Meldedaten.
- [ ] In Issue-Templates steht ein Hinweis, akute Schwachstellen nicht öffentlich zu posten.

## 5) Branch- und Schreibschutz

- [ ] Branch protection auf `main` aktivieren.
- [ ] Optional: „Require a pull request before merging" aktivieren, damit direkte Fremd-Commits ausgeschlossen sind.
- [ ] Optional: Nur Maintainer darf mergen/pushen.

## 6) Maintenance-Signale

- [ ] README enthält klaren Scope (Self-Hosting, kein SLA, private Nutzung etc.).
- [ ] `LICENSE`, `SECURITY.md`, `docs/community-policy.md`, `CONTRIBUTING.md` sind konsistent.
- [ ] CI-Smoke (`.github/workflows/smoke.yml`) läuft grün.

## 7) Einmaliger Public-Preflight

- [ ] Prüfen, ob wirklich nur gewünschte Dateien öffentlich sind (insb. `internal/`, `docs/dev/`, QA-Artefakte).
- [ ] Keine Secrets/API-Keys/Private Keys im Repo-History-Stand.
- [ ] Kontakt-/Impressumsdaten nur dort, wo sie bewusst und nötig sind.

## 8) Optionaler Komfort für dich als Solo-Maintainer

- [ ] GitHub-Benachrichtigungen für neue Issues aktiv halten.
- [ ] Labels standardisieren (`bug`, `content`, `security`, `question`, `wontfix`).
- [ ] Default-Issue-Template im Team kommunizieren (falls Tester:innen mitarbeiten).

Stand: Diese Liste ergänzt die bestehenden Repo-Dokumente und ist bewusst GUI-orientiert.
