---
title: "Playtest-Readiness-Gate"
version: 0.1.0
tags: [qa, process]
---

# Playtest-Readiness-Gate (Go/No-Go)

Diese Checkliste ist der kurze Vorlauf vor einem neuen Playtest-Durchgang.
Sie ergänzt das `docs/qa/tester-playtest-briefing.md` um einen kompakten,
operativen Gate für Maintainer.

## 1) Setup-Gate

- OpenWebUI-Setup mit `python scripts/setup.py` vorbereitet.
- Erwarteter Wissensspeicherpfad aktiv: 19 Slots
  (Spieler-Handbuch + 18 Runtime-Module) + Masterprompt separat.
- Geplantes Modell für Regeltreue gesetzt:
  `anthropic/claude-sonnet-4.6`.

## 2) Repo-Gate (Pflicht)

```bash
bash scripts/smoke.sh
```

- Ergebnis muss vollständig grün sein.
- Kein Playtest-Start bei rotem Smoke.

## 3) Regel-/Terminologie-Gate (Kurzprüfung)

Vor Start stichprobenartig prüfen, dass keine offensichtliche Drift gegen
Pflichtinvarianten vorliegt:

- Save-Schema v7 als SSOT.
- LP-Terminologie in spieler-sichtigen Texten.
- Chronopolis-Contract: freier Infiltrationslauf mit Reaktionslogik.
- Psi-Kosten mit PP **und** SYS.

## 4) Evidence-Gate

- Ablagepfad vorab anlegen:
  `internal/qa/evidence/playtest-YYYY-MM-DD/`
- Pro Testfall eine Markdown-Datei mit:
  - Modell
  - Szenario/Testfall
  - Ergebnis (inkl. Abweichung/Follow-up)
  - relevante Save-Snippets (wenn nötig)

## 5) Go/No-Go-Entscheid

- **GO**, wenn alle vier Gates erfüllt sind.
- **NO-GO**, wenn mindestens ein Gate offen ist;
  dann erst Mini-Durchlauf (Plan/Log + Fix), anschließend erneut Gate prüfen.
