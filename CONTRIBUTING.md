---
title: "Beitragsrichtlinien"
version: 1.1.0
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
- `systems/runtime-stub-routing-layer.md` dient als Referenz für eine eigene Runtime.
  Dieses Dokument bleibt Developer-Only; Spielmodule dürfen es nicht einbinden.
- Aktiviere das Hook `.githooks/pre-commit` über `git config core.hooksPath .githooks`.
- Signalaktionen setzen reale Hardware voraus (Comlink, Terminal, Kabel oder Relais). Ohne
  Gerät keine Netzinteraktion.
- Melde Terminologie- oder Regelabweichungen mit dem Issue-Template
  [Content Bug](.github/ISSUE_TEMPLATE/content-bug.yml).

Vielen Dank für deine Mithilfe!

## Vor dem ersten Commit
1. Lies `AGENTS.md` vollständig und bestätige Stil-, Struktur- und Testpflichten.
2. Prüfe, ob deine Änderungen Runtime-Content oder Dev-Dokumentation betreffen, und halte die
   Trennung strikt ein (`tags: [meta]`).
3. Stimme dich mit den Plattformroutinen aus
   [docs/maintainer-ops.md](docs/maintainer-ops.md) ab. Dort findest du die nötigen Uploads,
   QA-Notizen und Smoke-Checks pro Release.
4. Aktualisiere bei Strukturänderungen `master-index.json`, interne Links und sämtliche
   Querverweise im README.

## Quellen der Wahrheit zur Laufzeit
- **Runtime-fähig** (wird im Spiel geladen):
  - `README.md` – Kurzreferenzen, Chat-Shortcodes, HUD-Hinweise.
  - `systems/toolkit-gpt-spielleiter.md` – Makros, Guards, Router, Runtime-Logik.
- **Dev-Dokumentation** (wirkt nicht zur Laufzeit):
  - `doc.md`, `/docs/**` – CI/PR-Review, Linter, Beispiele.

Merksatz: Alles, was ingame sichtbar oder aktiv sein soll, MUSS in README oder Toolkit stehen.

## Wissensspeicher-Workflow
- Die operative Plattformpflege liegt bei den Maintainer:innen. Sie folgen der Checkliste aus
  [docs/maintainer-ops.md](docs/maintainer-ops.md#wissensspeicher--grundsetup) und führen alle
  Uploads sowie QA-Läufe ausschließlich im OpenAI-MyGPT-Beta-Klon durch.
- Der Repo-Agent (Codex) arbeitet anhand der gelieferten Ergebnisse. Proton LUMO und lokale
  Instanzen erhalten erst nach einer grünen MyGPT-Abnahme denselben Stand; zusätzliche Optimierungen
  erfolgen nicht im Repo.
- Dokumentiere Plattform-Uploads und Save/Load-Befunde in den QA-Dokumenten
  `docs/ZEITRISS-qa-audit-2025.md` sowie `docs/ZEITRISS-qa-fahrplan-2025.md`, sobald entsprechende
  Informationen aus den Playtests vorliegen.
- Verweise für Missions-, Encounter- und Arc-Generatoren den GPT direkt auf die Module unter
  `gameplay/`. Kopien in PRs sind nicht zulässig.

<a id="beta-gpt-qa-uebergaben"></a>
## Beta-GPT & QA-Übergaben
- Maintainer:innen spielen den MyGPT-Beta-Klon gemäß
  [docs/maintainer-ops.md](docs/maintainer-ops.md#beta-gpt--playtests), exportieren das vollständige
  Chatlog und liefern es zusammen mit einer Kurzliste der Findings an Codex.
- Sobald das Material vorliegt, erledigt der Repo-Agent folgende Schritte:
  1. Chatlog unverändert in `internal/qa/2025-beta-qa-log.md` archivieren und Plattform, Build sowie
     Wissensstand notieren.
  2. Alle Findings in `docs/ZEITRISS-qa-fahrplan-2025.md` übernehmen, priorisieren und den
     Log-Abschnitt verlinken.
  3. Tickets branchweise abarbeiten; Tests und Referenzen in den Commits dokumentieren.
  4. Nach dem Merge `docs/ZEITRISS-qa-audit-2025.md` mit Datum, Commit-Link und Ergebnis ergänzen.
- Vergleichs-KIs (z. B. ARXION) lesen denselben Repo-Stand, prüfen Diffs und liefern bei Bedarf
  zusätzliche Reports. Abarbeitung und Dokumentation der Findings liegen ebenfalls beim Repo-Agenten.
- Den Plattform-Sync (Store-GPT, Proton LUMO, lokale Instanzen) übernehmen die Maintainer:innen erst
  nach grüner MyGPT-Abnahme. Im Repo muss nur sichergestellt sein, dass alle QA-Dokumente denselben
  Status führen.

## GM-Stil & Linting
- `gm_style` (persistenter State) oder `GM_STYLE` (ENV) steuern das Linting.
  - `verbose`: filmischer Modus, kein PRECISION-Lint.
  - `precision`: Header-/Decision-Pflicht, `assert_foreshadow` warnt.

## Pflicht-Invarianten (nicht brechen)
- Boss-Timing: Core-Mission 5 (Mini), Mission 10 (Boss); Rift-Szene 10.
- Signalspace: Hardwarepflicht (Comlink/Kabel/Relais/Jammer).
- HUD: Einheitliche Reihenfolge, TTL `mm:ss`; Exfil zeigt Sweeps & Stress.

## Tests
- Mindestumfang: `make lint`, `make test`, `bash scripts/smoke.sh`.
- Zusätzliche Runtime-Prüfungen: `python3 tools/lint_runtime.py` und
  `GM_STYLE=verbose python3 tools/lint_runtime.py`.
- Optionale Checks: `node tools/test_save.js`, `node tools/test_load.js`.
- Dispatcher-Smoke-Tests siehe [docs/acceptance-smoke.md](docs/acceptance-smoke.md).
- Dokumentiere plattformweite QA- und Release-Checks nach
  [docs/maintainer-ops.md](docs/maintainer-ops.md). Nutze die dort verlinkten
  Acceptance-Smoke-Listen als Vorlage für Reports.

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
