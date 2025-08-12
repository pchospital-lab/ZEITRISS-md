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
- Siehe `systems/runtime-stub-routing-layer.md` für einen Stub für eine eigene Runtime.
  Dieses Dokument ist eine reine Entwicklerübersicht und wird **nicht** vom Spiel geladen;
  Spielmodule dürfen es nicht einbinden.
- Aktiviere das Hook `.githooks/pre-commit` per `git config core.hooksPath .githooks`.
- Führe die dort beschriebenen Tests nur aus, wenn du am Stub arbeitest.
- Signalaktionen benötigen ein Gerät (Comlink, Terminal, Kabel oder Relais); ohne Hardware keine Netzinteraktion.

Vielen Dank für deine Mithilfe!

## Offline-Lint ausführen

- `python3 tools/lint_runtime.py` prüft die Runtime-Guards.
- `bash scripts/smoke.sh` startet alle Linter gesammelt.
- Kritische Links verwaltet `.lint/doc_anchors.json`; geprüft durch `scripts/lint_doc_links.py`.

## Windows-Support

Die Skripte erwarten eine POSIX-kompatible Umgebung. Die CI nutzt `ubuntu-latest`.
Unter Windows führe Tests daher mit Git-Bash oder WSL aus.

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


<a id="schreibweise-umlaute"></a>
## Schreibweise – Umlaute (kanonisch)

- **Fließtext:** Bitte die deutschen Umlaute **ä/ö/ü/ß** verwenden.
- **ASCII-Ersatz** (`ae/oe/ue/ss`) ist **nur** in Code, IDs, Dateinamen oder
  technischen Kontexten erlaubt (z. B. Anker-IDs, Regex, Slugs).
- **Beispiele (kanonisch im Text):** „Heldenwürfel“, „Würfelmechanik“, „Überblick“.
- **Qualitätssicherung:** `scripts/lint_umlauts.py` prüft kanonische Schreibweisen.
  Fehler werden als `[FAIL]` gemeldet. Mapping: `CANON` im Skript.
- **Tests lokal:** `python3 scripts/lint_umlauts.py` oder `make smoke`.

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
- [ ] `SceneCounter` wird via `NextScene()` erhöht.
## ITI-HQ & Chronopolis

- **ITI-HQ** stellt Shop, Clinic, Workshop, Briefing und Fraktionskontakte
  bereit und erlaubt Speichern.
- **Chronopolis** ist eine optionale City ab Level 10, freischaltbar über
  den "Chronopolis‑Schlüssel". Speichern und FR-Kontakte sind dort
  blockiert, Rifts lassen sich nicht starten.
- Zutritt zum HQ nur für ITI-Agenten; Gäste benötigen `guest_custody`.
- Signalraum bleibt deaktiviert; Aktionen erfordern reale Geräte wie Terminal, Kabel oder Comlink.

## PvP-Arena (HQ-Training)

- Arena läuft im HQ-Kontext; keine Seeds, kein Paradoxon, kein Boss, keine FR-Intervention und keine CU-Belohnung.
- Runden & Timer: Best-of-N, bei 0 Sudden Death, OOB-Strafe eskaliert.
- Fairness: Loadout-Budget 5 Punkte, Psi nach Policy, Fahrzeuge optional.
- Signalpflicht: Hack/Jam nur mit Gerät; 2 km Reichweite, Jammer beachten.
- Speichern während einer Arena ist blockiert.
- State-Safety: SYS/PP/Heat/Stress/Cooldowns werden nach dem Match restauriert.
- Killswitch: `arena_abort()` stellt den Zustand wieder her.
- Logging: Ergebnis landet im Codex oder HUD.
*© 2025 pchospital – private use only. See LICENSE.
