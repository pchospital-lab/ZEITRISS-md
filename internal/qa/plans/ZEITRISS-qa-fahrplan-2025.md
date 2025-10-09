---
title: "ZEITRISS QA-Fahrplan 2025"
version: 1.2.0
tags: [meta]
---

# ZEITRISS QA-Fahrplan 2025

## Zielbild
Der Fahrplan bündelt sämtliche QA-Aufgaben für ZEITRISS 2025. Er knüpft an die
Copy-&-Paste-Protokolle aus Beta-GPT- und MyGPT-Tests an, priorisiert die daraus
abgeleiteten Maßnahmen und verweist auf die zugehörigen Artefakte. Prozess- und
Formatregeln stehen in `AGENTS.md`, `CONTRIBUTING.md` sowie
[maintainer-ops.md](../../../docs/maintainer-ops.md); dieses Dokument konzentriert
sich ausschließlich auf QA-Inhalte, Status und Nachverfolgung.

## QA-Zyklus
1. **Vorbereitung:** Maintainer:innen aktualisieren den Wissensstand gemäß
   Maintainer-Ops, prüfen die 20 Wissensspeicher-Slots auf Vollständigkeit und
   stellen sicher, dass Beta-GPT und MyGPT denselben Content erhalten.
   Laufzeitänderungen werden parallel als Regel- oder Pseudocode-Spiegel in den
   geladenen Modulen vermerkt.
2. **Testlauf:** Tester:innen führen den Playtest anhand des
   [Copy-&-Paste-Auftrags](../../../docs/qa/tester-playtest-briefing.md) durch.
   Der GPT simuliert den kompletten QA-Lauf inklusive der vollständigen
   Acceptance-Smoke-Checkliste (siehe Abschnitt "Acceptance-Smoke-Checkliste"
   im Briefing). Abschließend prüfen die Tester:innen die Antwort auf die
   geforderten `ISSUE`-, `Lösungsvorschlag`-, `To-do`- und
   `Nächste Schritte`-Blöcke.
3. **Archivierung:** Das vollständige Chatprotokoll wird unter
   `internal/qa/logs/2025-beta-qa-log.md` eingetragen und mit Datum, Plattform und
   Build versehen.
4. **Aufgabenaufbereitung:** Codex überführt die strukturierten Blöcke in diesen
   Fahrplan (Status, Priorität), ergänzt Live-Erkenntnisse aus Repo-Agent-
   Deepchecks unter "Deepcheck-Aufgaben" und versieht sie mit Verweisen auf
   Commits, PRs oder Issues.
5. **Umsetzung:** Maßnahmen laufen in separaten Branches; Testbefehle und
   Ergebnisse werden im Commit-Body dokumentiert.
6. **Review & Sync:** Nach Abschluss einer Maßnahme wird das Audit aktualisiert,
   der Abschnitt im QA-Log abgehakt und gegebenenfalls ein weiterer Beta-Test
   gestartet.

## Rollen & Übergabe
- **Maintainer:innen** halten Wissensstände synchron, bauen Beta-GPT-Instanzen
  und stoßen Tests an.
- **Tester:innen** dokumentieren Ergebnisse unverändert und liefern sie an Codex
  über das QA-Log.
- **Codex (Repo-Agent)** priorisiert die Befunde, setzt Änderungen um und
  aktualisiert Audit, Fahrplan sowie Referenzdokumente.
- **Audit-Archiv:** `internal/qa/audits/ZEITRISS-qa-audit-2025.md`
  (Zusammenfassung) und `internal/qa/logs/` (vollständige Logs).

## Deepcheck-Aufgaben (Repo-Agent Sessions)
- Jede Analyse- oder Verbesserungsrunde mit Codex erhält einen eigenen
  Session-Eintrag im Fahrplan. Dort werden die identifizierten Maßnahmen,
  Folgeaufgaben und Referenzen gesammelt, bis sie abgeschlossen sind.
- Neue Session-Einträge werden direkt während des Chats gepflegt, damit der
  Wissensstand zwischen Beta-GPT-Reports und manuellen Deepchecks konsistent
  bleibt.
- Sobald ein Punkt umgesetzt ist, wandert der Status auf ✅ und der passende
  Commit, PR oder QA-Log-Verweis wird ergänzt.

### Sessions 2025

- **2025-06-11 – Codex-Deepcheck** (Status: 🔄 laufend)
  - Erkenntnis / To-do: Repository-Analyse bestätigt QA-Artefakte in README und
    `master-index.json`; Maßnahmenpaket Juni 2025 (#1–#16) bleibt offen und wird
    blockweise vorbereitet.
  - Referenz: README.md §QA-Artefakte, `master-index.json`, QA-Audit 2025.

### Session-Template

- **(Beispiel: 2025-06-03 – Codex-Deepcheck)** (Status: ✅, PR #…)
  - Erkenntnis / To-do: Struktur aktualisieren und Acceptance-Smoke an den
    Testprompt binden.
  - Referenz: QA-Log (Link einsetzen).

## Arbeitsstränge & Ziele
- **Dokumentation & Index:** README, Repo-Map und Index spiegeln QA-Dokumente
  und verlinken Audit sowie Fahrplan konsistent.
  - Artefakte: `README.md`, `master-index.json`, QA-Dokumente
- **Beitragsprozesse:** Verweise auf QA-Workflow in `CONTRIBUTING.md` und
  `AGENTS.md` aktuell halten.
  - Artefakte: `CONTRIBUTING.md`, `AGENTS.md`
- **Tests & Automation:** Makefile- und Script-Läufe dokumentieren; Smoke- und
  Spezialtests werden im QA-Log referenziert.
  - Artefakte: `Makefile`, `scripts/smoke.sh`, QA-Log-Einträge
- **Wissensspiegel:** Wissensspeicher-Module enthalten die Regel-/Pseudocode-
  Spiegel der lokalen Runtimes. Abweichungen werden im QA-Log samt Commit-ID
  und Upload-Datum hinterlegt.
  - Artefakte: `README.md`, Runtime-Module, `internal/qa/logs/`
- **Datenschutz & Plattformen:** Plattformhinweise und Offline-First-Vorgaben
  bleiben in Maintainer-Ops, Audit und Fahrplan synchron.
  - Artefakte: `/docs/maintainer-ops.md`, Audit, QA-Log
- **Recht & Compliance:** Lizenz- und Markenhinweise mit QA-Maßnahmen abgleichen
  und bei Bedarf PRs initiieren.
  - Artefakte: `LICENSE`, `/docs/trademark.md`, QA-Log-Referenzen

## Repo-Analyse 2025-06-11

### Abgleich Dokumentation & Index
- README weist weiterhin direkt auf Fahrplan, Audit, QA-Log und Maintainer-Ops
  und ist damit konform mit Sprint 1 (Querverweise).
- `master-index.json` listet unverändert die Runtime- und Meta-Module; keine
  veralteten QA-Verweise oder fehlende Einträge gegenüber dem README.
- QA-Audit 2025 enthält die vollständige Problemübersicht aus dem Beta-GPT-Test
  vom Juni 2025; Abgleich mit dem Fahrplan bestätigt, dass alle 16 Punkte
  übernommen wurden und dort in der Maßnahmenliste stehen.

### Priorisierte Umsetzungspakete (Ableitung aus Beta-GPT Juni 2025)
- [ ] **Save- & Load-Block:** Issues #1, #2, #4, #9, #10, #12, #14 – Fokus auf
  Schema/Linter, Load-Flags und Persistenz der Foreshadow- sowie Warn-Logs.
  Vor Umsetzung `tools/lint_runtime.py` und bestehende Dispatcher-Tests gegen
  neue Pflichtfelder spiegeln.
- [ ] **HUD- & UX-Block:** Issues #3, #5, #7, #8, #10, #13 – Arc-Dashboard,
  Accessibility-Menü, Offline-Fallback und Foreshadow-Badge bündeln; README und
  Toolkit-Dokumentation vorbereiten.
- [ ] **PvP- & Arena-Block:** Issues #6, #11, #15, #16 – Modus-Helper,
  Koop-Verteilung, Arena-Regeln und Markt-Logging gemeinsam angehen, damit
  Kampf- und Wirtschaftslogik synchron bleiben.
- QA-Koordination plant für jeden Block eine eigene Regression (Dispatcher,
  Cross-Mode, Koop-Debrief). Ergebnisse fließen nach Umsetzung in das
  Beta-QA-Log.

## Maßnahmenpaket Beta-GPT-Testprompt Juni 2025
Die folgenden Aufgaben leiten sich unmittelbar aus ISSUE #1–#16 des jüngsten
Beta-GPT-Laufs ab. Sie sind nach Workstream sortiert, enthalten konkrete
Zwischenschritte und markieren Abhängigkeiten zwischen Runtime, QA und
Dokumentation.

### Issue #1 – Save-Schema
- **Workstream:** Save-Schema
- **Statusnotiz:** ✅ Serializer ergänzt Pflichtfelder und die
  Linter-Regel `SAVE_REQ_FIELDS` (Commit `3e4f306`).
- **Owner:** Codex
- **Zieltermin:** KW 25
- **QA-Verankerung:** Dispatcher-Suite „HQ-Save Pflichtfelder“ erweitern.

### Issue #2 – Save-Normalisierung
- **Workstream:** Save-Normalisierung
- **Statusnotiz:** ✅ `load_deep()` normalisiert nun alle Gruppen-Aliase nach
  `party.characters[]`, dedupliziert Mehrfacheinträge und hält die
  Dokumentation aktuell (Commit: Fahrplan 2025-06-11).
- **Owner:** Codex
- **Zieltermin:** KW 26
- **QA-Verankerung:** Cross-Mode-Load-Test (Solo↔Koop↔PvP).

### Issue #3 – Arc-Dashboard
- **Workstream:** Arc-Dashboard
- **Statusnotiz:** ✅ Schema dokumentiert, Serializer/Deserializer übernehmen das
  optionale Dashboard konsistent. (Commit: wird im PR referenziert.)
- **Owner:** Codex & Maintainer:in
- **Zieltermin:** KW 27
- **QA-Verankerung:** Tools `test_save.js` und `test_load.js` decken Normalisierung
  ab; Episoden-Debrief-Reload mit Seeds bleibt für Cross-Check aktiv.

### Issue #4 – Load-Flows
- **Workstream:** Load-Flows
- **Statusnotiz:** ✅ `SkipEntryChoice()` setzt den Skip-Status nach dem Load direkt im
  Toolkit, `StartMission()` stellt ihn über `AllowEntryChoice()` wieder auf Auswahl.
  (Commit: wird im PR referenziert.)
- **Owner:** Codex
- **Zieltermin:** KW 25
- **QA-Verankerung:** Dreifachtest der Load-Pfade (wird nach Neuansatz reaktiviert).

### Issue #5 – Exfil-Policy
- **Workstream:** Exfil-Policy
- **Statusnotiz:** ✅ Default `px_loss_on_hot_fail=false` gesetzt und README/Guides auf die Opt-in-Strafe hingewiesen.
- **Testnachweis:** `PYTHONPATH=. python3 scripts/lint_umlauts.py` (OK, 2025-06-11).
  Commit: wird im PR referenziert.
- **Owner:** Codex & Maintainer:in
- **Zieltermin:** KW 26
- **QA-Verankerung:** Zwei Missionsläufe (TTL-Timeout vs. regulär).

### Issue #6 – PvP-Modusflag
- **Workstream:** PvP-Modusflag
- **Statusnotiz:** ✅ `campaign.mode` treibt nun `is_pvp()` sowie
  `phase_strike_tax()`/`phase_strike_cost()`. Arena-Start/Exit setzen das
  Modus-Flag, `state.arena.phase_strike_tax` dokumentiert den Aufschlag.
  (Commit: wird im PR referenziert.)
- **Owner:** Codex
- **Zieltermin:** KW 27
- **QA-Verankerung:** Drei Kampfmodi (Core/Rift/Arena) testen.

### Issue #7 – Accessibility
- **Workstream:** Accessibility
- **Nächster Schritt:** HUD-Menü liefern und Persistenztests durchführen.
- **Owner:** Codex & QA
- **Zieltermin:** KW 28
- **QA-Verankerung:** HQ-Onboarding-Regression.

### Issue #8 – Offline-Fallback
- **Workstream:** Offline-Fallback
- **Statusnotiz:** ✅ Toolkit-`offline_help()` liefert Terminal-/FAQ-Hinweis für
  den im Einsatz getrennten ITI↔Kodex-Uplink, `!offline` triggert das
  Feldprotokoll (Mission weiter mit HUD-Lokaldaten) und `must_comms()` lenkt auf
  den Fallback, sobald Reichweite/Jammer den Uplink kappen.
- **Owner:** Codex
- **Zieltermin:** KW 28
- **QA-Verankerung:** Tunneltest „Funk weg“ inklusive Re-Sync.

### Issue #9 – Versionierung
- **Workstream:** Versionierung
- **Statusnotiz:** ✅ Semver-Check vergleicht jetzt `zr_version` mit `ZR_VERSION`,
  Fehlermeldung und Doku sind harmonisiert und `logs.flags.runtime_version`
  hält die Laufzeitversion fest. (Commit: wird im PR referenziert.)
- **Owner:** Codex & Maintainer:in
- **Zieltermin:** KW 25
- **QA-Verankerung:** Migrationspfad-Test (`migrate_save()`).

### Issue #10 – Foreshadow-Log
- **Workstream:** Foreshadow-Log
- **Statusnotiz:** ✅ `logs.foreshadow` persistiert, `ForeshadowHint()` legt persistente Marker an, Toolkit-Makros spiegeln die Logik
  (Badge, `!boss status`) und das HUD zeigt den FS-Badge.
- **Mirror-Hinweis:** Maintainer:innen spiegeln die `runtime.js`-Änderungen nach QA-Abnahme in die produktive Runtime laut
  Maintainer-Ops (QA-Log-Eintrag ergänzen).
- **Testnachweis:** `npm run lint:rt`, `npm run test:hud`, `npm run test:save`.
- **Owner:** Codex
- **Zieltermin:** KW 26
- **QA-Verankerung:** M4→M10 Save/Load-Kette.

### Issue #11 – Koop-Ökonomie
- **Workstream:** Koop-Ökonomie
- **Nächster Schritt:** Debrief-Split-Dialog und Wallet-Logik ausarbeiten.
- **Owner:** Codex
- **Zieltermin:** KW 29
- **QA-Verankerung:** Drei Koop-Runs (gleich/ungleich/custom).

### Issue #12 – Chronopolis-Warnung
- **Workstream:** Chronopolis-Warnung
- **Statusnotiz:** ✅ Chronopolis-Warnung persistiert per Toolkit-Flag
  `logs.flags.chronopolis_warn_seen`; `start_chronopolis()` ruft das Warn-Popup
  nur einmal auf. (Commit: wird im PR referenziert.)
- **Owner:** Codex
- **Zieltermin:** KW 25
- **QA-Verankerung:** Doppel-Entry-Test vor und nach dem Save.

### Issue #13 – Ask→Suggest
- **Workstream:** Ask→Suggest
- **Statusnotiz:** ✅ Suggest-Modus toggelt über `modus suggest`/`modus ask`, das Toolkit-Makro `suggest_actions()` markiert
  Vorschläge als `Vorschlag:` und README dokumentiert den Flow. (Commit: wird im PR referenziert.)
- **Owner:** Codex & Maintainer:in
- **Zieltermin:** KW 27
- **QA-Verankerung:** Drei Missionsmuster (Verdunkeln/Verhindern/Dokumentieren).

### Issue #14 – Suspend-Snapshot
- **Workstream:** Suspend-Snapshot
- **Statusnotiz:** ✅ Suspend-Snapshot übernimmt Initiative-Reihenfolge und HUD-Timer;
  `tools/test_suspend.js` deckt das Resume ab. (Commit: wird im PR referenziert.)
- **Owner:** Codex
- **Zieltermin:** KW 26
- **QA-Verankerung:** Konflikt pausieren und fortsetzen; `tools/test_suspend.js` dokumentiert den Abgleich.

### Issue #15 – PSI-Arena-Regeln
- **Workstream:** PSI-Arena-Regeln
- **Statusnotiz:** ✅ `apply_arena_rules()` bündelt nun PvP-Dämpfer,
  `psi_buffer`-Flags sowie `phase_strike_tax`; Runtime-Stub und Docs spiegeln die
  Logik. (Commit: wird im PR referenziert.)
- **Owner:** Codex & Maintainer:in
- **Zieltermin:** KW 27
- **QA-Verankerung:** Arena-, Core- und Rift-Vergleich.

### Issue #16 – Markt-Log
- **Workstream:** Markt-Log
- **Statusnotiz:** ✅ Runtime-Helper `log_market_purchase()` schreibt `logs.market[]`
  (Timestamp, Artikel, Kosten, Px-Klausel); README und Speicher-Doku nennen den
  Debrief-Trace. (Commit: wird im PR referenziert.)
- **Owner:** Codex
- **Zieltermin:** KW 28
- **QA-Verankerung:** Chronopolis-Kauf inklusive Px-Folge.

**Koordinationshinweise:**

- QA pflegt nach jedem abgeschlossenen Punkt den Status im QA-Log und
  referenziert commit- bzw. PR-IDs.
- Maintainer:innen aktualisieren Modul 12, README und Master-Index gesammelt
  pro Block (`Save-Schema`, `HUD/UX`, `Arena/PvP`).
- Codex sammelt Runtime-Änderungen in logisch getrennten Branches, damit Review
  und Migration nachvollziehbar bleiben.

## Regressionstest-Termine 2025

- **Q1 2025 (19.03.2025 – Acceptance-Smoke-Abgleich)**
  - Umfang: Vollständiger Regressionstest (Build 4.2.2) mit Save/Load und Boss-Gates.
  - Status: ✅ abgeschlossen.
  - QA-Log: `internal/qa/logs/2025-beta-qa-log.md`, Abschnitt 2025-03-19.
- **Q2 2025 (09.–13.06.2025)**
  - Umfang: Regressionstest im MyGPT-Beta-Klon mit Fokus auf Spiegelprozesse und Save-Restore.
  - Status: 🗓️ geplant.
  - QA-Log: Eintrag folgt nach Lauf.
- **Q3 2025 (08.–12.09.2025)**
  - Umfang: Regressionstest im MyGPT-Beta-Klon mit Arena- und Großteam-Schwerpunkt.
  - Status: 🗓️ geplant.
  - QA-Log: Eintrag folgt nach Lauf.
- **Q4 2025 (08.–12.12.2025)**
  - Umfang: Regressionstest im MyGPT-Beta-Klon mit Jahresabschluss- und Spiegelkontrolle.
  - Status: 🗓️ geplant.
  - QA-Log: Eintrag folgt nach Lauf.

## Maßnahmen-Backlog (Priorisiert)
### Sprint 1 – sofort angehen
- [x] README-Querverweise auf Audit, Fahrplan und QA-Log ergänzen.
  (2025-03-17 – QA-Log 2025-03-17, Commit: 131046d)
- [x] CONTRIBUTING-Abschnitt "Beta-GPT & QA-Übergaben" gegen den neuen
  QA-Zyklus prüfen und anpassen.
  (2025-03-17 – QA-Log 2025-03-17, Commits: 131046d, 03dad05)
- [x] QA-Log (`internal/qa/logs/2025-beta-qa-log.md`) mit erstem Testprotokoll füllen
  und Prioritäten in diesem Fahrplan verlinken.
  (2025-03-17 – QA-Log 2025-03-17, Commit: 131046d)
- [x] QA-Fahrplan überarbeiten (dieses Dokument).
  (2025-03-17 – QA-Log 2025-03-17, Commits: 5cbfce8, d2a3b4c, 3338360)

### Sprint 2 – innerhalb der nächsten zwei Iterationen
- [x] Acceptance-Smoke-Checkliste gegen aktuelle Runtime-Skripte spiegeln
  (Boss-Gates, HUD-Badges, Psi-Heat) und Ergebnisse im QA-Log dokumentieren.
  (2025-03-23 – QA-Log 2025-03-19; Commit: e4d2872)
- [x] Maintainer-Ops anpassen: MyGPT als alleinige QA-Plattform herausstellen
  und Spiegelprozesse für Store-GPT, LUMO und lokale Instanzen dokumentieren.
  (2025-03-21 – Maintainer-Ops 1.2.0, Commit: d2a3b4c)
- [x] CHANGELOG-Einträge mit QA-Nachweisen versehen (Verweis auf QA-Log-Abschnitte).
  (2025-03-26 – QA-Log 2025-03-19 & 2025-03-17 verlinkt, Commit: e5da4ad)
- [x] Glossar um neue Terminologie aus Version 4.2.2 erweitern
  (Psi-Heat, Tier-Gates, Kodex-Badges) und Synchronität dokumentieren.
  (2025-03-26 – README-Glossar ergänzt, Commit: e5da4ad)
- [x] Audit-Abschnitte 11–20 gegen reale Commits spiegeln und Referenzen
  nachtragen.
  (2025-03-27 – QA-Log 2025-03-19 verlinkt; Commits: b245bef, 5a3fbb3,
  7d91e53, 8fe8de2, 52d1ba5, 9a1675d, 8208170, 22d3c33,
  1be6f57)

### Sprint 3 – langfristig planen
- [x] Automatisierten Link-Lint für README und Docs in CI evaluieren und
  Ergebnis im QA-Log festhalten.
  (2025-03-30 – QA-Log 2025-03-30, Commit: 445b8ed)
- [x] Tooling erweitern, um YAML-Header und Pflichtfelder automatisiert zu
  prüfen (`tools/lint_runtime.py` erweitern) und QA-Nachweis ablegen.
  (2025-10-05 – QA-Log 2025-10-05; Commit: 868883a)
- [x] Wiederkehrende MyGPT-Regressionstests terminieren und Status pro Quartal
  protokollieren; Spiegelplattformen nur bei Bedarf kontrollieren.
  (2025-04-02 – QA-Log 2025-04-02; Commit: 3338360)

## Status-Dashboard (Stand: Überarbeitung 2025-04-02)

- **QA-Fahrplan aktualisieren** — Status: ✅ erledigt; nächster Schritt:
  Statusblock bei jeder Änderung aktualisieren. Owner: Maintainer-Team.
- **README-Querverweise** — Status: ✅ 2025-03-17; nächster Schritt:
  README-Änderungen stets mit QA-Verweisen abgleichen. Owner:
  Maintainer-Team.
- **QA-Log initial füllen** — Status: ✅ 2025-03-17; nächster Schritt:
  Folgeprotokolle hinzufügen. Owner: QA-Koordination.
- **CONTRIBUTING anpassen** — Status: ✅ 2025-03-17; nächster Schritt:
  QA-Übergaben halbjährlich auditieren. Owner: Docs-Verantwortliche.
- **Acceptance-Smoke-Checkliste** — Status: ✅ 2025-03-23; nächster Schritt:
  QA-Log 2025-03-19 referenzieren. Owner: Repo-Agent.
- **Maintainer-Ops Spiegelprozesse** — Status: ✅ 2025-03-21; nächster
  Schritt: Spiegelprozesse bei Plattform-Änderungen prüfen. Owner:
  Maintainer-Team.
- **Automatisierte Link-Prüfung** — Status: ✅ 2025-03-30; nächster Schritt:
  Link-Lint in CI-Läufen beobachten. Owner: Repo-Agent.
- **Runtime-Lint YAML/Pflichtfelder** — Status: ✅ 2025-10-05; nächster
  Schritt: QA-Log 2025-10-05 referenzieren. Owner: Repo-Agent.
- **Plattform-Regressionstests** — Status: ✅ 2025-04-02; nächster Schritt:
  Q2-Regressionstest protokollieren. Owner: QA-Koordination.
- **CHANGELOG QA-Verweise** — Status: ✅ 2025-03-26; nächster Schritt:
  QA-Log-Referenzen beibehalten. Owner: Repo-Agent.
- **Glossar Terminologie 4.2.2** — Status: ✅ 2025-03-26; nächster Schritt:
  README-Glossar regelmäßig spiegeln. Owner: Docs-Verantwortliche.

## Pflege & Reporting
- Prüfe bei jeder Änderung, ob Audit und QA-Log entsprechende Einträge erhalten.
- Verweise in PR-Beschreibungen auf betroffene QA-Log-Abschnitte.
- Nutze Issues oder Projektboards für umfangreiche Maßnahmen und verknüpfe sie
  mit diesem Fahrplan.
- Dokumentiere Abschlüsse mit Datum und Commit in Audit und QA-Log, nicht in den
  Runtime-Dateien.
- Halte die Terminübersicht der Regressionstests aktuell und verweise nach jedem
  Lauf auf den entsprechenden QA-Log-Abschnitt.

> Aktualisiere den Statusabschnitt bei jeder Änderung dieses Fahrplans. Jede
> abgeschlossene Maßnahme erhält Datum, Commit-Referenz und Verweis auf das
> korrespondierende QA-Log.
