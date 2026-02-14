---
title: "Maintainer-Ops"
version: 1.3.0
tags: [meta]
---

# Maintainer-Ops

Dieses Memo bündelt die operativen Abläufe für **ZEITRISS 4.2.6**.
Referenz ist ein lokaler/self-hosted Workflow; externe Plattformen bleiben
optional.

## Wissensspeicher & Grundsetup

Der Datensatz für Runtime-nahe GPT-Setups besteht aus:

1. **Masterprompt:** `meta/masterprompt_v6.md` (Systemfeld oder erste Nachricht).
2. **README:** `README.md`.
3. **Runtime-Module:** exakt die 19 Module aus `core/`, `characters/`,
   `gameplay/`, `systems/`.
4. **Nicht laden:** `master-index.json` und Dev-/QA-Dokumente.

> **Slot-Kontrolle:** Immer 20 Wissensmodule (README + 19 Runtime-Module)
> prüfen.

### Runtimes & Tests außerhalb des Wissensspeichers

- `runtime.js`, `tools/`, `scripts/`, `internal/runtime/` bleiben repo-intern.
- Jede Laufzeitänderung wird vom Repo-Agenten parallel in Wissensmodulen
  gespiegelt (README/Runtime-Markdowns/Toolkit).
- Mirror-Nachweis mit Commit-ID im QA-Log dokumentieren.

### Spiegelhinweis für Laufzeitänderungen

- Nach Merges prüfen, ob Runtime-/Tooling-Dateien geändert wurden.
- Bestätigte Änderungen in Wissensmodule spiegeln und danach erst in lokale
  Betriebsumgebungen übernehmen.

## QA-Plattformstrategie

- **Referenzpfad:** lokale QA über OpenWebUI (localhost) mit importiertem
  Wissensstand aus diesem Repo.
- **Automationspfad:** API-gesteuerte Testläufe (z. B. über Agenten wie Altair)
  sind erlaubt, solange vollständige Logs archiviert werden.
- **Externe GPT-Plattformen:** optional; kein Release-Blocker.
- **Grundsatz:** Das Repository liefert den kanonischen Stand. Der Betrieb
  erfolgt auf Verantwortung der nutzenden Person/Organisation.

## QA-Artefakte & Nachverfolgung

- [QA-Fahrplan 2025](../internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md)
- [QA-Audit 2025](../internal/qa/audits/ZEITRISS-qa-audit-2025.md)
- [Beta-QA-Log 2025](../internal/qa/logs/2025-beta-qa-log.md)
- [Tester-Playtest-Briefing](./qa/tester-playtest-briefing.md)

## Plattform-Workflows

### Lokaler Betrieb (OpenWebUI/Ollama/OpenRouter)

1. Lokale Zielumgebung starten (z. B. OpenWebUI auf `http://localhost:3000`).
2. Optional `./scripts/setup-openwebui.sh` ausführen.
3. Alternativ manuell Masterprompt + Wissensmodule importieren.
4. Nach jedem Merge Wissensmodule neu synchronisieren und Save/Load kurz prüfen.

### OpenAI MyGPT & GPT-Store (optional)

- Nur bei explizitem Bedarf spiegeln.
- Keine plattformspezifischen Sonderregeln in den Repo-Stand zurückschreiben,
  solange sie nicht allgemein gelten.

### Spiegelprozess nach QA-Freigabe

1. QA-Run im Log dokumentieren (Datum, Build, Plattform, Ergebnis).
2. Fixes auf Branch umsetzen, testen, mergen.
3. Nach Merge den aktualisierten Wissensstand in lokale Zielumgebung laden.
4. Optional denselben Stand auf externe Plattformen spiegeln.

## QA-Loop & Speicherstände

Halte den Übergabeprozess in
`CONTRIBUTING.md#beta-gpt-qa-uebergaben` ein.

## Beta-GPT & Playtests

- Beta-GPT- oder Plattformklone sind für Vergleichsläufe erlaubt, aber optional.
- Maßgeblich für Freigaben ist ein dokumentierter, reproduzierbarer QA-Lauf.

## Übergabe an Codex & Dokumentation

1. Vollständige Chatlogs inkl. `ISSUE`/`Lösungsvorschlag`/`To-do`/
   `Nächste Schritte` sichern.
2. Plattform, Build und Wissensstand im Log festhalten.
3. Findings in Fahrplan/Audit übernehmen und mit Commits verknüpfen.

## Systemgrenzen (Reminder)

- KI-Spielleitung schreibt keine Dateien ins Repo.
- Save-Funktionen laufen HQ-zentriert per Copy/Paste.
- Keine echten personenbezogenen Daten in Testchats.

## Release-Checkliste

- Versionierung (`CHANGELOG.md`, `README.md`, `master-index.json`) synchron.
- Rechtliche Hinweise prüfen (`docs/trademark.md`, `LICENSE`, README).
- `make lint`, `make test`, `bash scripts/smoke.sh` ausführen und dokumentieren.
- Public Release = Repo-Download + Eigenbetrieb; keine verpflichtende
  Bereitstellung vorgebauter gehosteter GPT-Instanzen.
