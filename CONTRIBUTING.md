---
title: "Beitragsrichtlinien"
version: 1.2.0
tags: [meta]
---

# Beitragsrichtlinien

Bitte beachte die folgenden Richtlinien, wenn du Markdown-Dateien in diesem Repository
bearbeitest.

## Grundregeln

- Jeder Abschnitt beginnt mit einem YAML-Header (`title`, `version`, `tags`).
- Ausnahme: Der Masterprompt (`meta/masterprompt_*.md`) wird seit Version 4.2.2 ohne
  YAML-Header gepflegt und muss unter 8 000 Zeichen (≈ 8 k Window) bleiben.
- Halte Zeilenlängen bei maximal 100 Zeichen und speichere Dateien in UTF-8.
- Pull Requests aktualisieren bestehende Dateien oder ergänzen neue Module.
- Schreibe prägnante Commit-Nachrichten im Imperativ und öffne PRs stets gegen den
  `main`-Branch.
- `internal/runtime/runtime-stub-routing-layer.md` dient als Referenz für eine eigene Runtime.
  Dieses Dokument bleibt Developer-Only; Spielmodule dürfen es nicht einbinden.
- Aktiviere das Hook `.githooks/pre-commit` über `git config core.hooksPath .githooks`.
- Signalaktionen setzen reale Hardware voraus (Comlink, Terminal, Kabel oder Relais). Ohne
  Gerät keine Netzinteraktion.
- Melde Terminologie- oder Regelabweichungen mit dem Issue-Template
  [Content Bug](.github/ISSUE_TEMPLATE/content-bug.yml).

Vielen Dank für deine Mithilfe!

## Vor dem ersten Commit

1. Lies `AGENTS.md` vollständig und bestätige Stil-, Struktur- und Testpflichten.
2. Prüfe die [Dokumenten-Landkarte im README](README.md#dokumenten-landkarte), um Übergabepunkte
   zwischen Repo-Agent, Maintainer:innen und Tester:innen zu kennen.
3. Prüfe, ob deine Änderungen Runtime-Content oder Dev-Dokumentation betreffen, und halte die
   Trennung strikt ein (`tags: [meta]`).
4. Stimme dich mit den Plattformroutinen aus
   [docs/maintainer-ops.md](docs/maintainer-ops.md) ab. Dort findest du die nötigen Uploads,
   QA-Notizen und Smoke-Checks pro Release.
5. Aktualisiere bei Strukturänderungen `master-index.json`, interne Links und sämtliche
   Querverweise im README.

<a id="qualitaets-und-compliance-checkliste"></a>

## Qualitäts- und Compliance-Checkliste

- [ ] YAML-Header vorhanden, aktualisiert und syntaktisch korrekt (Ausnahme: Masterprompt).
- [ ] Strukturregeln eingehalten: Core-Ops mit 12 Szenen, Rift-Ops mit 14 Szenen in drei Akten und
      Pflichtfelder pro Szene gefüllt.
- [ ] Terminologie konsistent (z. B. `Rift-Seeds`, `HQ`, `SceneCounter`).
- [ ] Stilprüfung bestanden: filmischer Ton im Runtime-Content (Ihr-Form), Du-Ansprache im
      Masterprompt, sachlicher Stil in Dev-Dokumenten.
- [ ] Interne Links geprüft (`scripts/lint_doc_links.py`) und keine Dev-Verweise in Runtime-Modulen.
- [ ] Deutsche Umlaute korrekt verwendet (`scripts/lint_umlauts.py`).
- [ ] Trennung zwischen Runtime-Content und Dev-Dokumentation gewahrt (`tags: [meta]`).
- [ ] Querverweise in `master-index.json`, README, Toolkits und QA-Dokumenten aktualisiert.

## Quellen der Wahrheit zur Laufzeit

- **Runtime-fähig** (wird im Spiel geladen):
  - `README.md` – Kurzreferenzen, Chat-Shortcodes, HUD-Hinweise.
  - `systems/toolkit-gpt-spielleiter.md` – Makros, Guards, Router, Runtime-Logik.
- **Dev-Dokumentation** (wirkt nicht zur Laufzeit):
  - `doc.md`, `/docs/**` – CI/PR-Review, Linter, Beispiele.

Merksatz: Alles, was ingame sichtbar oder aktiv sein soll, MUSS in README oder Toolkit stehen.

## QA-Inhalte trennen

- QA- und Acceptance-Anweisungen landen in
  `docs/qa/tester-playtest-briefing.md`, `docs/maintainer-ops.md` oder den
  QA-Logs (`internal/qa/**`). Runtime-Module und Wissensspeicher bleiben frei
  von QA-Prompts, damit der Spielablauf nicht mit Abnahmelisten vermischt wird.
- Verweise auf Goldenfiles oder Smoke-Checks im Runtime-Bereich reduzieren und
  stattdessen in den QA-Dokumenten bündeln. Nur zwingend nötige Runtime-Hinweise
  (z. B. SaveGuards, HUD-Verhalten) bleiben in README/Toolkit.

## Wissensspeicher-Workflow

- Die operative Plattformpflege liegt bei den Maintainer:innen. Grundlage ist
  [docs/maintainer-ops.md](docs/maintainer-ops.md#wissensspeicher--grundsetup).
- **Referenzbetrieb ist lokal/self-hosted** (z. B. OpenWebUI + OpenRouter/Ollama).
  Externe GPT-Plattformen sind optional und werden nur bei Bedarf nachgezogen.
- Das Repository veröffentlicht keine vorgebauten gehosteten GPT-Instanzen.
  Nutzer:innen laden den Stand aus dem Repo und betreiben ihn eigenverantwortlich.
- Dokumentiere Setup-, Upload- und Save/Load-Befunde in den QA-Dokumenten
  `internal/qa/audits/ZEITRISS-qa-audit-2025.md` sowie
  `internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md`, sobald entsprechende
  Informationen aus den Playtests vorliegen.
- QA-Artefakte (QA-Aufträge, Acceptance-Smoke-Listen, Testprompts) bleiben im
  Tester-Briefing
  [`docs/qa/tester-playtest-briefing.md`](docs/qa/tester-playtest-briefing.md)
  und werden bei Bedarf manuell in QA-Sessions gepostet. Sie gehören nicht in
  die Wissensspeicher-Slots.
- Verweise für Missions-, Encounter- und Arc-Generatoren den GPT direkt auf die
  Module unter `gameplay/`. Kopien in PRs sind nicht zulässig.

<a id="beta-gpt-qa-uebergaben"></a>

## Beta-GPT & QA-Übergaben

- Automatisierte QA-Läufe können lokal über Presets (z. B. OpenWebUI) oder
  optional über Beta-GPT-Setups ausgeführt werden.
- Maintainer:innen liefern dem Repo-Agenten das vollständige Chatlog sowie die
  erzeugten `ISSUE`-, `Lösungsvorschlag`-, `To-do`- und `Nächste Schritte`-Blöcke.
- Sobald das Material vorliegt, erledigt der Repo-Agent folgende Schritte:
  1. Chatlog unverändert in `internal/qa/logs/2025-beta-qa-log.md` archivieren
     und Plattform, Build sowie Wissensstand notieren.
  2. Die strukturierten Blöcke in
     `internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md` übernehmen,
     priorisieren und den Log-Abschnitt verlinken.
  3. Tickets branchweise abarbeiten; Tests und Referenzen in den Commits
     dokumentieren.
  4. Nach dem Merge `internal/qa/audits/ZEITRISS-qa-audit-2025.md` mit Datum,
     Commit-Link und Ergebnis ergänzen.
- Vergleichs-KIs (z. B. ARXION) lesen denselben Repo-Stand, prüfen Diffs und
  liefern bei Bedarf zusätzliche Reports. Abarbeitung und Dokumentation der
  Findings liegen ebenfalls beim Repo-Agenten.
- Plattform-Syncs bleiben optional; maßgeblich ist, dass QA-Dokumente und
  Repo-Stand denselben Freigabestatus führen.

## GM-Stil & Linting

- `gm_style` (persistenter State) oder `GM_STYLE` (ENV) steuern das Linting.
  - `verbose`: filmischer Modus, kein PRECISION-Lint.
  - `precision`: Header-/Decision-Pflicht, `assert_foreshadow` warnt.

## Pflicht-Invarianten (nicht brechen)

- Boss-Timing: Core-Mission 5 (Mini), Mission 10 (Boss); Rift-Szene 10.
- Signalspace: Hardwarepflicht (Comlink/Kabel/Relais/Jammer).
- HUD: Einheitliche Reihenfolge, TTL `mm:ss`; Exfil zeigt Sweeps & Stress.

<a id="verpflichtende-pruefungen"></a>

## Verpflichtende Prüfungen

- `make lint` (führt `npm run lint:rt`, `GM_STYLE=verbose npm run lint:rt`,
  `python3 scripts/lint_doc_links.py`, `python3 scripts/lint_umlauts.py`,
  `npm run lint:links`, `npm run lint:md` und `npm run lint:presets` aus)
- `make test` (ruft `npm run test` auf, inklusive `npm run test:acceptance` mit den
  Mission‑5‑Golden‑Files)
- `bash scripts/smoke.sh` (inkl. `node tools/test_alias_trace.js` für Alias-/Funk-Logs)
- `python3 tools/lint_runtime.py`
- `GM_STYLE=verbose python3 tools/lint_runtime.py`
- `python3 scripts/lint_doc_links.py`
- `python3 scripts/lint_umlauts.py`

Auch bei reinen Dokumentationsänderungen sind diese Prüfungen auszuführen.
Die Linter validieren Format, Links und Terminologie der Markdown-Dateien
und verhindern, dass sich Inkonsistenzen in den Wissensspeicher einschleichen.

### Erweiterte QA & optionale Checks

- `python3 tools/lint_debrief_trace.py` – verifiziert Debrief-Trace-Ausgaben (Chronopolis, Foreshadow, Offline, Runtime-Flags).
- `node tools/test_save.js`, `node tools/test_load.js`
- `npm run format:docs:check` – optionaler Prettier-Check für Dokumentation
  (lokale Installation von `prettier` erforderlich).
- Dispatcher-Smoke-Tests siehe
  [Acceptance-Smoke](docs/qa/tester-playtest-briefing.md#acceptance-smoke-checkliste).
- Dokumentiere plattformweite QA- und Release-Checks nach
  [docs/maintainer-ops.md](docs/maintainer-ops.md) und nutze die dort verlinkten
  Acceptance-Smoke-Listen als Vorlage.

### pre-commit-Hooks

- Installation: `pip install pre-commit`.
- Ausführung: `pre-commit run --files <datei1> <datei2>`.

## Speicherstände

- Einziger Typ: Deepsave (HQ-only). Pflege `save_version` und führe `migrate_save()` mit.

## Chat-Kurzbefehle (Minimal-Set)

- `!save`, `!load`, `!hud status`, `!gear shop`, `!helper delay|comms|boss`, `!px`,
  `modus verbose|precision`.

## Offline-Lint ausführen

- `python3 tools/lint_runtime.py` prüft die Runtime-Guards.
- `bash scripts/smoke.sh` startet alle Linter gesammelt.
- Kritische Links verwaltet `.lint/doc_anchors.json` und wird über
  `scripts/lint_doc_links.py` geprüft.

## Windows-Unterstützung

Die Skripte erwarten eine POSIX-kompatible Umgebung. Die CI nutzt `ubuntu-latest`. Unter Windows
führst du Tests daher mit Git-Bash oder WSL aus.

## Formatierungshinweise

- Nutze Bindestriche (`-`) als Aufzählungszeichen.
- Kursivtext wird mit Unterstrichen (`_Text_`) gesetzt, fetter Text mit doppelten Sternchen
  (`**Text**`).
- Vermeide Leerzeichen am Zeilenende.
- Lasse eine Leerzeile zwischen zwei Absätzen.

**Beispiel:**

```
- Ein Punkt
_kursiv_ und **fett**
```

<a id="schreibweise-umlaute"></a>

## Schreibweise – Umlaute (kanonisch)

- **Fließtext:** Verwende die deutschen Umlaute **ä/ö/ü/ß**.
- **ASCII-Ersatz** (`ae/oe/ue/ss`) ist nur in Code, IDs, Dateinamen oder technischen Kontexten
  erlaubt (z. B. Anker-IDs, Regex, Slugs).
- **Beispiele (kanonisch im Text):** „Heldenwürfel“, „Würfelmechanik“, „Überblick“.
- **Qualitätssicherung:** `scripts/lint_umlauts.py` prüft kanonische Schreibweisen und meldet
  Fehler als `[FAIL]`. Siehe Mapping `CANON` im Skript.
- **Tests lokal:** `python3 scripts/lint_umlauts.py` oder `make smoke`.

## HUD- und Regeltext-Stil

- HUD-Informationen (in-world) werden blau markiert: `<span style="color:#6cf">HUD</span>`.
- Regelhinweise (OOC) erscheinen in Orange: `<span style="color:#f93">Regel</span>`.
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

- **ITI-HQ** stellt Shop, Clinic, Workshop, Briefing und Fraktionskontakte bereit und erlaubt
  Speichern.
- **Chronopolis** ist eine optionale City ab Level 10, freischaltbar über den
  „Chronopolis-Schlüssel“. Speichern und FR-Kontakte sind dort blockiert; Rifts lassen sich nicht
  starten.
- Zutritt zum HQ nur für ITI-Agenten; Gäste benötigen `guest_custody`.
- Signalraum bleibt deaktiviert; Aktionen erfordern reale Geräte wie Terminal, Kabel oder Comlink.

## PvP-Arena (HQ-Training)

- Arena läuft im HQ-Kontext; keine Seeds, kein Paradoxon, kein Boss, keine FR-Intervention und
  keine CU-Belohnung.
- Runden & Timer: Best-of-N, bei 0 Sudden Death, OOB-Strafe eskaliert.
- Fairness: Loadout-Budget 5 Punkte, Psi nach Policy, Fahrzeuge optional.
- Signalpflicht: Hack/Jam nur mit Gerät; 2 km Reichweite, Jammer beachten.
- Speichern während einer Arena ist blockiert.
- State-Safety: SYS/PP/Psi-Heat/Stress/Cooldowns werden nach dem Match restauriert.
- Killswitch: `arena_abort()` stellt den Zustand wieder her.
- Logging: Ergebnis landet im Kodex oder HUD.

© 2025 pchospital – ZEITRISS® – private use only. See LICENSE.
