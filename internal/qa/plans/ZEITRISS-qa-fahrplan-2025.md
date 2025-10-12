---
title: "ZEITRISS QA-Fahrplan 2025"
version: 1.3.1
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

## Pflicht-Testpaket (Repo-Agent)

Der Repo-Agent führt bei jeder Änderung – auch reinen Dokumentationsupdates –
das vollständige Pflicht-Testpaket aus und protokolliert Ergebnisse in Commit,
PR und QA-Log:

- `make lint` – Runtime- und Link-Lints via NPM.
- `make test` – Modul- und Tool-Unittests.
- `bash scripts/smoke.sh` – Sammellauf der Python-Lints, Tool-Checks und HUD-
  Regressionen.
- `python3 tools/lint_runtime.py` – Direkter Lauf zur schnellen Fehlersuche.
- `GM_STYLE=verbose python3 tools/lint_runtime.py` – Gegencheck ohne
  Precision-Warnungen.
- `python3 scripts/lint_doc_links.py` – Verifiziert Dokumenten- und Ankerlinks.
- `python3 scripts/lint_umlauts.py` – Prüft Umlaute und Zeichensatz.

✅ **Status 2025-06-13:** Testpaket im Fahrplan verankert; jedes Ergebnis wird im
QA-Log zur Maßnahme referenziert.

Hinweis: Die Befehlsliste wird zentral in
[CONTRIBUTING.md → Verpflichtende Prüfungen](../../../CONTRIBUTING.md#verpflichtende-pruefungen)
gepflegt und muss in QA-Reports nicht erneut als To-do aufgeführt werden.

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

- **2025-06-12 – Codex-Repo-Check** (Status: 🔄 laufend)
  - Erkenntnis / To-do: Runtime-Stubs für HUD/Foreshadow, Offline-Uplink und Arena
    gegen `runtime.js` 4.2.2 gespiegelt; SaveGuard-Pfade dokumentiert. PR-/Review-
    Abschluss steht noch aus.
  - Referenz: `systems/runtime-stub-routing-layer.md` (Mirror 2025-06-12),
    `runtime.js` QA-Abgleich.

- **2025-06-13 – Beta-GPT-Nachlauf (Codex)** (Status: 🔄 laufend)
  - Erkenntnis / To-do: Beta-GPT-Lauf dokumentierte 17 offene Punkte (ISSUE #1–#17)
    rund um Save-Contract, HUD-UX, PvP/PvE-Parität und Log-Persistenz. Maßnahmen
    wurden priorisiert und in den neuen Issue-Fahrplan (siehe Abschnitt
    "Maßnahmenpaket Beta-GPT 2025-06") übertragen. Weitere QA-Referenzen folgen
    nach zusätzlichen Testläufen.
  - Update 2025-06-13: Acceptance-Smoke #14/#15 (PvP-Flag, SaveGuard) im QA-Log
    2025-06-13 dokumentiert; PvP-/Arena-Validierung bleibt bis zum Abschluss der
    übrigen Beta-GPT-Nacharbeiten offen.
  - Referenz: internal/qa/logs/2025-beta-qa-log.md (§ 2025-06-13).
  - Testpaket (2025-06-13): `make lint`, `make test`, `bash scripts/smoke.sh`,
    `python3 tools/lint_runtime.py`, `GM_STYLE=verbose python3 tools/lint_runtime.py`,
    `python3 scripts/lint_doc_links.py`, `python3 scripts/lint_umlauts.py`.

- **2025-06-14 – Codex-Offline-Audit** (Status: ✅ erledigt)
  - Erkenntnis / To-do: Jammer-Suspend (`reason: "jammer"`, `jammed: true`) und
    Resume (`reason: "resume"`) im Offline-Log dokumentiert; `render_offline_protocol()`
    bestätigt den Jammer-Reset im HUD-Log.
  - Referenz: internal/qa/logs/2025-beta-qa-log.md (§ 2025-06-14).
  - Testpaket (2025-06-14): Inline-Test (`node`-Snippet für Offline-Audit) und
    `python3 tools/lint_runtime.py` (OK, QA-Log-Auszug 2025-06-14).
- **2025-06-15 – Codex-Planabgleich** (Status: 🔄 laufend)
  - Erkenntnis / To-do: Zuordnung der QA-Follow-ups aus dem Beta-GPT-Protokoll
    zu den Issues #1–#16 gestartet; Mapping-Tabelle in Cluster C ergänzt und
    offene Fälle für den nächsten Beta-Log-Abgleich markiert.
  - Referenz: interner Review dieses Fahrplans; QA-Log 2025-06-13 (Mapping in
    Vorbereitung).

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
  Offline-Fallback und Foreshadow-Badge bündeln; README und
  Toolkit-Dokumentation vorbereiten. Accessibility-Menü entfällt nach Maintainer-
  Entscheid vom 2025-06-13 (Schriftgrößen-Anpassung bleibt clientseitig).
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
- **Statusnotiz:** ✅ Serializer ergänzt Pflichtfelder (`SAVE_REQ_FIELDS`); Legacy-Root-Saves werden jetzt direkt in den Wissensmodulen beschrieben (manuelle `character{}`-Spiegelung ohne runtime.js). Modul 12 & README führen die Schrittfolge für GPT aus, Commit `3e4f306` + Folgecommit dokumentieren den Mirror.
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
- **Statusnotiz:** ❌ Verworfene Option – HUD behält das Standardmenü, Schrift-
  größen-Anpassungen erfolgen auf Endgeräten (Entscheid 2025-06-13, Maintainer-
  Sync bestätigt).
- **Owner:** —
- **Zieltermin:** entfällt
- **QA-Verankerung:** entfällt

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
- **Dokumentation:** Modul 15 „Chrono Units“ beschreibt den Chronopolis-Basar samt
  Markt-Trace (`log_market_purchase()`) und QA-Evidenzpfad. (Commit: wird im PR
  referenziert.)
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

## Mission 5 Badge-Check

Zur Absicherung der Foreshadow- und Badge-Kette aus ISSUE #3 dokumentiert dieser Abschnitt,
wie QA den Nachweis in jedem Beta-GPT-Lauf erbringt. Die Schritte ergänzen die
[Acceptance-Smoke-Checkliste](../../../docs/qa/tester-playtest-briefing.md#acceptance-smoke-checkliste)
um eine klar definierte Evidenz, damit das HUD-Verhalten von Mission 5 dauerhaft nachvollziehbar bleibt.

1. **Load vorbereiten:** Missionsverlauf bis zum Abschluss von Mission 4 spielen oder mit einem gültigen
   HQ-Save (`scene_overlay().foreshadow == 2`) starten. Stelle sicher, dass der Foreshadow-Zähler auf 2/2 steht.
2. **Mission 5 starten:** Wähle den Einsatz über das HUD. QA bestätigt, dass unmittelbar nach dem Start
   der Toast `Boss-Encounter in Szene 10` erscheint, das Badge `SF-OFF` eingeblendet wird und der HUD-Zähler
   `Foreshadow 2/2` meldet.
3. **HUD-Log erfassen:** Dokumentiere den Konsolen- bzw. HUD-Auszug (Text oder Screenshot) direkt im QA-Log und
   verweise auf die Acceptance-Smoke-Position 12. Bei MyGPT-Läufen genügt ein kopierter Chatlog-Block mit den
   gemeldeten HUD-Zeilen.
4. **Foreshadow-Reset prüfen:** Nach Missionsabbruch oder Abschluss sicherstellen, dass das Badge auf `SF-ON`
   zurückspringt und `ForeshadowHint()` keine offenen Marker mehr meldet. QA vermerkt das Ergebnis im Fahrplan-Status
   dieses Abschnitts.

> Der Copy-&-Paste-Auftrag im [Tester-Playtest-Briefing](../../../docs/qa/tester-playtest-briefing.md)
> weist den GPT explizit an, den Mission 5 Badge-Check im selben QA-Lauf zu simulieren und den
> HUD-/Log-Auszug als Evidenz in die `Evidenz`-Zeilen der ISSUE-Blöcke zu übernehmen.

> Ergebnisdokumentation: Abschnitt „Mission 5 Badge-Check“ dieses Fahrplans dient als Referenz. QA markiert den
> entsprechenden Punkt im Beta-QA-Log als erledigt und verweist auf das Testdatum sowie die verwendete Runtime-Version.

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
- **Offline-Audit Jammer-Flow** — Status: ✅ 2025-06-14; nächster Schritt:
  Jammer-Regression im Q3-Lauf dokumentieren. Owner: QA.

## Pflege & Reporting
- Prüfe bei jeder Änderung, ob Audit und QA-Log entsprechende Einträge erhalten.
- Verweise in PR-Beschreibungen auf betroffene QA-Log-Abschnitte.
- Nutze Issues oder Projektboards für umfangreiche Maßnahmen und verknüpfe sie
  mit diesem Fahrplan.
- Dokumentiere Abschlüsse mit Datum und Commit in Audit und QA-Log, nicht in den
  Runtime-Dateien.
- Archiviere im QA-Log jeden Debrief-Auszug aus `logs.market[]`, wie im
  Beta-GPT-Testlauf Juni 2025 gefordert; der Trace dient als Persistenznachweis
  für den Chronopolis-Basar.
- Halte die Terminübersicht der Regressionstests aktuell und verweise nach jedem
  Lauf auf den entsprechenden QA-Log-Abschnitt.

> Aktualisiere den Statusabschnitt bei jeder Änderung dieses Fahrplans. Jede
> abgeschlossene Maßnahme erhält Datum, Commit-Referenz und Verweis auf das
> korrespondierende QA-Log.

## Maßnahmenpaket Beta-GPT 2025-06 – Issue-Fahrplan

Die nachfolgende Übersicht strukturiert die im Beta-GPT-Lauf identifizierten
ISSUES #1–#17 in thematische Cluster, benennt Sofortmaßnahmen und weist die
zuständigen Rollen zu. Statusangaben werden nach Umsetzung aktualisiert; bis zur
finalen Bestätigung bleiben Einträge auf 🔄 offen.

### Cluster A – Save-Contract & Persistenz

| Status | Issue | Kernproblem | Sofortmaßnahme | Owner | Referenzartefakte |
| --- | --- | --- | --- | --- | --- |
| ✅ | #1 | Doppelte Save-Schemata (Root vs. `character{}`) | `normalize_save_v6()` implementiert, Alt-Saves gespiegelt, Dokumentation Modul 12/README aktualisiert | Codex, Maintainer:innen | `runtime.js`, `systems/gameflow/speicher-fortsetzung.md`, `README.md` |
| ✅ | #2 | Gruppensave-Konsistenz fehlt | `load_deep()` normalisiert Team-/Gruppen-Aliase nach `party.characters[]`, Deduplizierung dokumentiert | Codex | `runtime.js`, `systems/gameflow/speicher-fortsetzung.md` |
| ✅ | #4 | Load-Compliance driftet | `SkipEntryChoice()` setzt den Skip-Status direkt nach `load_deep()`, `StartMission()` ruft `AllowEntryChoice()` auf | Codex | `systems/toolkit-gpt-spielleiter.md`, `systems/gameflow/speicher-fortsetzung.md` |
| ✅ | #9 | Semver-Abgleich uneinheitlich | Semver-Check harmonisiert `zr_version`↔`ZR_VERSION`, Fehlermeldungen & Logs spiegeln die Runtime-Version | Codex, Maintainer:innen | `runtime.js`, `README.md` |
| ✅ | #10 | Foreshadow-Gate nicht persistiert | `logs.foreshadow` + `ForeshadowHint()` persistiert Marker, Toolkit-Badges spiegeln den Status (`!boss status`) | Codex | `runtime.js`, `systems/toolkit-gpt-spielleiter.md` |
| ✅ | #12 | Chronopolis-Warnung ohne Flag | `logs.flags.chronopolis_warn_seen` setzt Persistenz, Warn-Popup feuert nur einmal | Codex | `runtime.js`, `systems/gameflow/speicher-fortsetzung.md` |
| ✅ | #14 | Suspend-Snapshot verliert HUD/Initiative | Snapshot übernimmt Initiative/Taktik, `tools/test_suspend.js` belegt Resume-Flow | Codex | `runtime.js`, `tools/test_suspend.js`, `systems/toolkit-gpt-spielleiter.md` |
| ✅ | #16 | Markt-Log fehlt | `log_market_purchase()` schreibt Timestamp/Item/Kosten/Px, README & Modul 15 dokumentieren Debrief-Trace | Codex | `runtime.js`, `systems/currency/cu-waehrungssystem.md`, `internal/qa/logs/` |

### Cluster B – HUD, UX & Accessibility

| Status | Issue | Kernproblem | Sofortmaßnahme | Owner | Referenzartefakte |
| --- | --- | --- | --- | --- | --- |
| ✅ | #3 | Arc-Dashboard fehlt im Schema | Schema dokumentiert Dashboard, Serializer/Deserializer spiegeln Seeds/Fraktionen | Codex & Maintainer:in | `runtime.js`, `systems/gameflow/speicher-fortsetzung.md` |
| ✅ | #5 | Hot-Exfil Px-Strafe inkonsistent | Default `px_loss_on_hot_fail=false`, Guides markieren Opt-in-Strafe | Codex & Maintainer:in | `runtime.js`, `README.md`, `gameplay/kampagnenstruktur.md` |
| ✅ | #6 | PvP-Modusflag unklar | `campaign.mode` treibt `is_pvp()` + `phase_strike_tax()`; Arena-Start/Exit setzen Flag & Toast | Codex | `runtime.js`, `gameplay/kampagnenstruktur.md` |
| ⛔ | #7 | Accessibility-Menü gefordert | Verworfene Option – Maintainer:innen halten Menü extern (Entscheid 2025-06-13) | Codex, Maintainer:innen | Entscheidung QA-Sync 2025-06-13 |
| ✅ | #8 | Offline-Fallback ohne Leitplanke | Toolkit-`offline_help()` liefert FAQ, `!offline` + `must_comms()` decken Fallback ab | Codex | `runtime.js`, `systems/toolkit-gpt-spielleiter.md` |
| 🔄 | #11 | Koop-Ökonomie unsauber | Debrief-Split-Dialog & Wallet-Logik ausarbeiten | Codex | `runtime.js`, `systems/gameflow/speicher-fortsetzung.md` |
| ✅ | #13 | Ask→Suggest ohne Standard | Suggest-Modus toggelt via `modus`, Makro `suggest_actions()` markiert Vorschläge | Codex & Maintainer:in | `runtime.js`, `README.md`, `systems/toolkit-gpt-spielleiter.md` |
| ✅ | #15 | PSI-Arena-Regeln verteilt | `apply_arena_rules()` bündelt Dämpfer & `psi_buffer`, Docs spiegeln PvP-Abgleich | Codex & Maintainer:in | `runtime.js`, `systems/runtime-stub-routing-layer.md` |

### Cluster C – QA & Supporting Artefakte

| Status | QA-Follow-up | Beta-Issue | Kernproblem | Sofortmaßnahme | Owner | Referenzartefakte |
| --- | --- | --- | --- | --- | --- | --- |
| ✅ | #2 | #6 | QA-Szenarien für PvP-Mode-Flag | Acceptance-Smoke #5/#7/#14/#15 dokumentieren; HUD-/Save-Evidenz sichern (Dokumentiert 2025-06-13) | QA | `internal/qa/logs/2025-beta-qa-log.md`, `docs/qa/tester-playtest-briefing.md` |
| ✅ | #3 | #10 | Mission 5 Badge-Nachweis | QA-Plan um Badge-Check erweitern (siehe Abschnitt „Mission 5 Badge-Check“) | QA | `internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md` |
| ✅ | #18 | — | Pflicht-Testpaket fehlte im Fahrplan | Testpaket dokumentieren und im QA-Log referenzieren | QA | `internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md` |
| ⛔ | #5 | #7 | Accessibility-Profile testen | Entfällt – Menü wird nicht implementiert, siehe Entscheidung 2025-06-13 | QA | Entscheidung QA-Sync 2025-06-13 |
| 🔄 | #6 | #3 | Fraktionsinterventionen auditieren | Drei Missionen loggen, Dashboard prüfen | QA | `internal/qa/audits/ZEITRISS-qa-audit-2025.md` |
| 🔄 | #7 | #10 | Rift-Gate QA-Szenarien | Mission 5/10 Episodenabschluss tracken | QA | `internal/qa/logs/2025-beta-qa-log.md` |
| 🔄 | #8 | tbd | Pre-City-Hub-Dokumentation | README/Modul-Updates planen | Maintainer:innen | `README.md`, `gameplay/kampagnenuebersicht.md` |
| 🔄 | #9 | #16 | Debrief-Linter | Debrief-Trace-Checks in QA-Tools ergänzen | QA, Tooling | `tools/`, `scripts/` |
| ✅ | #10 | #8 | Offline-Audit QA-Flow | Jammer-Szenario suspend/resume dokumentiert (QA-Log 2025-06-14) | QA | `internal/qa/logs/2025-beta-qa-log.md` |
| 🔄 | #11 | #10 | Boss-Toast QA-Check | Core/Rift-Spawns überwachen | QA | `internal/qa/logs/2025-beta-qa-log.md` |
| 🔄 | #12 | tbd | Alias-Debrief QA-Test | Zwei Aliasläufe planen | QA | `internal/qa/logs/2025-beta-qa-log.md` |
| 🔄 | #13 | tbd | Squad-Radio-Log QA | Konfliktgrößen S–XL abdecken | QA | `internal/qa/logs/2025-beta-qa-log.md` |
| 🔄 | #14 | #16 | CU-Balance Audit | HQ-Basar Balance-Notiz ergänzen | QA, Maintainer:innen | `internal/qa/audits/ZEITRISS-qa-audit-2025.md` |
| 🔄 | #15 | #13 | Ask→Suggest Load-Test | Loader-Toast validieren | QA | `internal/qa/logs/2025-beta-qa-log.md` |
| 🔄 | #16 | tbd | Vehikel-Overlay QA | Boden- & Luft-Chase testen | QA | `internal/qa/logs/2025-beta-qa-log.md` |
| 🔄 | #17 | #15 | Phase-Strike Arena QA | Drei Einsätze protokollieren | QA | `internal/qa/logs/2025-beta-qa-log.md` |

#### Zuordnung QA-Follow-ups ↔ Beta-Issues (Stand: 2025-06-15)

- Abgeschlossen: QA-Follow-ups #2 (PvP-Modusflag → Issue #6), #3 (Mission 5
  Badge → Issue #10), #5 (Accessibility → Issue #7), #10 (Offline-Fallback →
  Issue #8) sowie #18 (Pflicht-Testpaket, Prozess-Item) sind im QA-Log bzw.
  diesem Fahrplan dokumentiert.
- Offen/fortlaufend: QA-Follow-ups #6, #7, #8, #9, #11, #12, #13, #14, #15,
  #16 und #17 warten auf weitere Evidenz aus Beta-GPT-Logs oder Tooling.
- Offen für den nächsten Beta-Log-Abgleich: Follow-ups #8 (Pre-City-Hub), #12
  (Alias-Debrief), #13 (Squad-Radio-Log) und #16 (Vehikel-Overlay). Diese
  Punkte benötigen eine konkrete Zuordnung zu den Issues #1–#16 oder eine
  separate QA-Kategorisierung.

> Hinweis: Die Tabellen führen QA-Folgeaufgaben bewusst doppelt (Codex-Implementierung
> und QA-Validierung), um parallele Verantwortlichkeiten sichtbar zu machen. Nach
> jedem abgeschlossenen Schritt sind Audit und QA-Log zu aktualisieren.

⚠️ **Zu klären:** Die Nummerierung der QA-Folgeaufgaben (#2, #3, #18 …) basiert auf dem Copy-&-Paste-Protokoll des Beta-GPT-Laufs und muss gegen die finalen ISSUE-IDs (#1–#16) gespiegelt werden. Der initiale Abgleich (Stand 2025-06-15) ist oben dokumentiert; die offenen Zuordnungen (#8, #12, #13, #16) bleiben als To-do markiert und werden nach Sichtung des vollständigen Beta-Logs geschlossen.
