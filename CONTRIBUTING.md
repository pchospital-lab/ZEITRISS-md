---
title: "Contribution Guidelines"
version: 1.1
tags: [meta]
---

# CONTRIBUTING

Bitte beachte folgende Richtlinien beim Bearbeiten der Markdown-Dateien:

- Jeder Abschnitt beginnt mit einem YAML-Header (`title`, `version`, `tags`).
- Halte Zeilen möglichst unter 120 Zeichen und verwende UTF-8.
- Wrappe lange Absätze bei etwa 100 Zeichen.
- Pull Requests sollten bestehende Dateien aktualisieren oder neue Module ergänzen.
- Verwende praegnante Commit-Nachrichten im Imperativ.
- Oeffne Pull Requests stets gegen den `main`-Branch.
- Siehe `systems/runtime-stub-routing-layer.md` für einen optionalen Stub für eine eigene Runtime.
  Das Spiel funktioniert auch ohne diese Vorlage.
- Optionaler Check: Aktiviere das Hook `.githooks/pre-commit` per `git config core.hooksPath .githooks`.
- Führe vor jedem PR die Tests aus `systems/runtime-stub-routing-layer.md` aus.

Vielen Dank für deine Mithilfe!

## Formatierungshinweise

- Nutze Bindestriche (`-`) als Aufzählungszeichen.
- Kursivtext wird mit Unterstrichen (`_Text_`) gesetzt, fetter Text mit doppelten Sternchen (`**Text**`).
- Vermeide Leerzeichen am Zeilenende.
- Lasse eine Leerzeile zwischen zwei Absätzen.

**Beispiel:**

```
- Ein Punkt
_kursiv_ und **fett**
```


## HUD- und Regeltext-Stil

- HUD-Informationen (in-world) werden blau markiert: `<span style="color:#6cf">HUD</span>`
- Regelhinweise (OOC) erscheinen in Orange: `<span style="color:#f93">Regel</span>`
- Nutze diese Kennzeichnung sparsam, um schnelle Orientierung zu bieten.

## PR-Checkliste

- [ ] Core-Op nutzt 12 Szenen.
- [ ] Rift-Op enthält 14 Szenen in drei Akten.
- [ ] Jede Szene benennt **Conflict, Goal, Spur**.
- [ ] Preserve- und Trigger-Ziele vorhanden.
- [ ] HQ-Phase und CU-Abrechnung eingebaut.
- [ ] Psi-Optionen nur bei passendem Tag.
- [ ] `SceneCounter` wird via `EndScene()` erhöht.
*© 2025 pchospital – private use only. See LICENSE.
