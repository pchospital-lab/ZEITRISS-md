---
title: "GitHub Public-Checkliste (Solo-Maintainer)"
version: 1.1.0
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

## 9) Freigabeprotokoll (Ist-Stand)

Stand: 2026-02-15 (GitHub-GUI manuell geprüft)

### Settings → General → Features

- [x] Issues: **an**
- [x] Pull requests: **an**
  - [x] PR Creation: **Collaborators only**
- [x] Discussions: **aus**
- [x] Projects: **aus**
- [x] Wiki: **aus / nicht genutzt**

### Settings → General → Pull Requests (Merge)

- [x] Allow squash merging: **an**
- [x] Allow merge commits: **aus**
- [x] Allow rebase merging: **aus**
- [x] Auto-merge: **aus**
- [x] Automatically delete head branches: **an**

### Settings → Rules → Rulesets

- [x] Ruleset `main – Solo, agent-freundlich` auf Default-Branch `main`
- [x] Bypass list leer
- [ ] Enforcement aktiv (**derzeit: Disabled**, bei Private/Free ggf. nicht enforcebar)
- [x] Restrict deletions
- [x] Block force pushes
- [x] Require linear history
- [x] Require a pull request before merging (Required approvals: `0`)
- [x] Allowed merge methods: **Squash only**
- [x] Require status checks: **ZEITRISS Offline Smoke**

### Repo-Artefakte (statisch vorhanden)

- [x] PR-Hinweis: `.github/PULL_REQUEST_TEMPLATE.md`
- [x] Externe PRs schließen: `.github/workflows/close-external-prs.yml`
- [x] Issue-Steuerung: `.github/ISSUE_TEMPLATE/config.yml`
- [x] Security-Prozess: `SECURITY.md`, `.github/ISSUE_TEMPLATE/security.yml`
- [x] Community-Policy: `docs/community-policy.md`

Stand: Diese Liste ergänzt die bestehenden Repo-Dokumente und ist bewusst GUI-orientiert.
