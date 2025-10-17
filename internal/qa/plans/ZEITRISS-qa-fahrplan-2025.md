---
title: "ZEITRISS QA-Fahrplan 2025"
version: 1.8.2
tags: [meta]
---

# ZEITRISS QA-Fahrplan 2025

Der Fahrplan fasst alle QA-Maßnahmen für ZEITRISS 2025 kompakt zusammen und
verweist auf Audit sowie QA-Log für Detailbelege. Die Historie der älteren
Zwischenstände wurde nach `internal/qa/audits/ZEITRISS-qa-audit-2025.md`
verschoben, damit dieses Dokument den aktuellen Fokus abbildet.

## Zielbild

- Beta-GPT- und MyGPT-Läufe liefern konsistente QA-Protokolle.
- Audit, Fahrplan und QA-Log spiegeln denselben Maßnahmen- und Wissensstand.
- Wissensmodule dokumentieren jede Runtime-Änderung unmittelbar.

## QA-Zyklus

1. **Vorbereitung** – Maintainer:innen gleichen Wissensstände gemäß
   [`docs/maintainer-ops.md`](../../../docs/maintainer-ops.md) ab und prüfen die
   20 Wissensspeicher-Slots.
2. **Testlauf** – Tester:innen nutzen das
   [Tester-Briefing](../../../docs/qa/tester-playtest-briefing.md) inklusive
   Acceptance-Smoke-Checkliste und Mission-5-Badge-Check.
3. **Archivierung** – Komplette Protokolle landen unter
   `internal/qa/logs/2025-beta-qa-log.md` mit Datum, Plattform und Build.
4. **Umsetzung & Sync** – Repo-Agent (Codex) priorisiert Befunde, setzt sie um
   und synchronisiert Audit, Fahrplan und Referenzdokumente.

## Pflicht-Testpaket (Repo-Agent)

Das Pflicht-Testpaket wird bei jeder Änderung ausgeführt und im QA-Log
referenziert:

- `make lint`
- `make test`
- `bash scripts/smoke.sh`
- `python3 tools/lint_runtime.py`
- `GM_STYLE=verbose python3 tools/lint_runtime.py`
- `python3 scripts/lint_doc_links.py`
- `python3 scripts/lint_umlauts.py`

Die aktuelle Beschreibung liegt zusätzlich in
[`CONTRIBUTING.md`](../../../CONTRIBUTING.md#verpflichtende-pruefungen).

## Rollen & Übergabe

- **Maintainer:innen** – Halten Wissensstände synchron, stoßen Tests an und
  spiegeln Runtimes.
- **Tester:innen** – Dokumentieren die QA-Läufe unverändert und liefern sie ins
  QA-Log.
- **Codex (Repo-Agent)** – Priorisiert die Ergebnisse, setzt Maßnahmen um und
  aktualisiert Audit, Fahrplan und Referenzen.

## Deepcheck-Kurzprotokolle 2025

| Datum | Schwerpunkt | Referenzen |
| ----------- | ------------------------------ | ---------- |
| 2025-06-11 | Repo-Analyse & Maßnahmenplan | README §QA-Artefakte; QA-Log 2025-06-22 |
| 2025-06-12 | Runtime-Stubs & Routing-Layer | `systems/runtime-stub-routing-layer.md`; QA-Log 2025-06-22 |
| 2025-06-13 | Beta-GPT-Nachlauf | QA-Log 2025-06-13; Maßnahmenpaket Beta-GPT 2025-06 |
| 2025-06-14 | Offline-Audit Jammer-Flow | QA-Log 2025-06-14 |
| 2025-06-15 | QA-Follow-up-Mapping | QA-Log 2025-06-22 |
| 2025-06-16 | Follow-ups & Checklisten | QA-Log 2025-06-22 |
| 2025-06-17 | Koop-Debrief & Wallet-Split | README §HQ/Chronopolis; QA-Log 2025-06-20 |
| 2025-06-18 | Compliance-Abgleich | `runtime.js` 4.2.2; README §§Runtime-Flags & Offline-Protokoll |
| 2025-06-19 | Pre-City-Hub Dokumentation | README §ITI-HQ & Chronopolis; QA-Log 2025-06-19 |
| 2025-06-22 | Fahrplan-/QA-Log-Synchronität | QA-Log 2025-06-22 |
| 2025-07-05 | Beta-GPT Deltas (Save/HUD/Arena) | QA-Log 2025-07-05 |
| 2025-07-18 | Beta-GPT Regression Save/HUD/Compliance | QA-Log 2025-07-18 |
| 2025-10-21 | Beta-GPT 2025-10-15 Nacharbeiten validiert | QA-Log 2025-10-21 |

Detailnotizen zu jeder Session befinden sich im QA-Audit.

## Arbeitsstränge & Ziele

- **Dokumentation & Index** – README, Repo-Map und `master-index.json` verweisen
  konsistent auf Audit, Fahrplan und QA-Log.
- **Beitragsprozesse** – `CONTRIBUTING.md` und `AGENTS.md` spiegeln den aktuellen
  QA-Workflow.
- **Tests & Automation** – Makefile- und Script-Läufe sind dokumentiert; Smoke-
  und Spezialtests werden im QA-Log belegt.
  - Node-Smoke deckt Start-Trigger, Accessibility-Persistenz, Chronopolis-
    Acknowledge und Arena-Schema ab (`tools/test_start.js`,
    `tools/test_accessibility.js`, `tools/test_chronopolis_ack.js`,
    `tools/test_arena_schema.js`).
- **Wissensspiegel** – Wissensmodule enthalten die Spiegel der lokalen Runtimes;
  Abweichungen werden mit Commit-ID im QA-Log erfasst.
- **Datenschutz & Plattformen** – Maintainer-Ops, Audit und Fahrplan halten
  Plattformhinweise und Offline-First-Vorgaben synchron.

## Maßnahmen – Formatierung & Tooling

**Ist-Stand 2025-07-19**

- Zeilenlängen- und Formatvorgaben (≤ 100 Zeichen, UTF-8, Absatzabstand) sind in
  [`CONTRIBUTING.md`](../../../CONTRIBUTING.md#grundregeln) dokumentiert, werden
  aktuell jedoch nicht durch ein separates Markdownlint-/Prettier-Setup
  automatisiert.
- Das Pflicht-Testpaket (`make lint`, `make test`, `bash scripts/smoke.sh` plus
  Direktaufrufe der Python-Linter) deckt Runtime-, Link- und Terminologie-Checks
  ab; zusätzliche Node-Abhängigkeiten sind bislang nicht eingebunden.
- Die lokalen pre-commit-Hooks rufen ausschließlich projektinterne Python-Checks
  auf und spiegeln keine externen Formatter.

**To-dos**

- [x] Evaluieren, ob ein schlankes `.markdownlint`-Profil (max 100 Zeichen,
      Frontmatter-Ausnahmen) den bestehenden QA-Checks ergänzt, ohne
      widersprüchliche Format-Rewrites zu erzeugen. → `.markdownlint.yaml`
      eingebunden; `npm run lint:md` deckt QA-Plan, QA-Audit und QA-Index ab
      und läuft automatisch via `make lint`.
- [x] Abklären, ob ein optionales `.prettierrc` lediglich Dokumentationsbereiche
      adressieren soll; Ziel: keine automatischen Rewraps in Runtime-Modulen
      (`core/`, `systems/`). → `.prettierrc.json` beschränkt sich auf Repo-
      Dokumentation und belässt Runtime-Module unangetastet.
- [x] Falls zusätzliche Tools eingeführt werden, Makefile-, `package.json`- und
      pre-commit-Konfigurationen so erweitern, dass das Pflicht-Testpaket stabil
      bleibt und neue Abhängigkeiten klar dokumentiert werden. → `npm run`
      Skripte ergänzt, Makefile erweitert, markdownlint in pre-commit-Hooks
      verankert.

## Maßnahmenübersicht Beta-GPT 2025-06 (Issues #1–#16)

Alle Maßnahmen des Beta-GPT-Laufs Juni 2025 sind abgeschlossen. Die Tabelle
fasst Status und Hauptverweise zusammen; weiterführende Evidenz steht im
QA-Audit und im Beta-QA-Log.

| Issue | Thema | Status | Primärreferenzen |
| ----- | -------------------------- | ------ | ---------------- |
| #1 | Save-Schema | ✅ abgeschlossen | `runtime.js`; Modul 12; QA-Log 2025-06-29 |
| #2 | Save-Normalisierung | ✅ abgeschlossen | `runtime.js`; QA-Log 2025-06-11 |
| #3 | Arc-Dashboard | ✅ abgeschlossen | `runtime.js`; QA-Log 2025-06-13 |
| #4 | Load-Flows | ✅ abgeschlossen | Toolkit; QA-Log 2025-06-11 |
| #5 | Exfil-Policy | ✅ abgeschlossen | README; QA-Log 2025-06-11 |
| #6 | PvP-Modusflag | ✅ abgeschlossen | `runtime.js`; QA-Log 2025-06-24 |
| #7 | Accessibility-Menü | ❌ verworfen | Maintainer:innen-Entscheid 2025-06-13 |
| #8 | Offline-Fallback | ✅ abgeschlossen | Toolkit; QA-Log 2025-06-18 |
| #9 | Versionierung | ✅ abgeschlossen | `runtime.js`; QA-Log 2025-06-11 |
| #10 | Foreshadow-Log | ✅ abgeschlossen | `runtime.js`; QA-Log 2025-06-27 |
| #11 | Koop-Ökonomie | ✅ abgeschlossen | README; Modul 12; QA-Log 2025-06-20 |
| #12 | Chronopolis-Warnung | ✅ abgeschlossen | `runtime.js`; QA-Log 2025-06-11 |
| #13 | Ask→Suggest | ✅ abgeschlossen | Toolkit; QA-Log 2025-06-27 |
| #14 | Suspend-Snapshot | ✅ abgeschlossen | Toolkit; QA-Log 2025-06-22 |
| #15 | PSI-Arena-Regeln | ✅ abgeschlossen | `runtime.js`; QA-Log 2025-06-27 |
| #16 | Markt-Log | ✅ abgeschlossen | README; Modul 15; QA-Log 2025-06-28 |

## Maßnahmenpaket Beta-GPT 2025-07 (Issues #1–#15)

Der Beta-GPT-Lauf vom 2025-07-05 lieferte neue Findings rund um Save-Versionen,
Foreshadow-Darstellung, Arena-/Comms-Makros und Acceptance-Checks. Die folgende
Tabelle dokumentiert den offenen Maßnahmenblock. Detailnotizen: QA-Log
2025-07-05 sowie [Rohprotokoll des Beta-GPT-Laufs](../logs/2025-07-05-beta-gpt-delta.md)
und das ergänzende Chatprotokoll (Maintainer:innen-Archiv).

| Issue | Thema | Status | Primärreferenzen |
| ----- | -------------------------------------------------- | ------------ | ---------------- |
| #1 | Save-Version 5→6 Angleichen (Serializer, Migration) | ✅ abgeschlossen | README; Speicher-Fortsetzung |
| #2 | Foreshadow Gate vs. Season Total trennen | ✅ abgeschlossen | README QA 25-06-27; Toolkit 16 |
| #3 | `scene_overlay()`/`!boss status` Schnittstellen | ✅ abgeschlossen | README Runtime-Helper; Toolkit 16 |
| #4 | `SF-OFF`-Badge Preconditions dokumentieren | ✅ abgeschlossen | README Schnellstart & QA-Checks |
| #5 | `arenaStart(options)` Makro + HUD-Toast | ✅ abgeschlossen | README Runtime-Helper; Toolkit 16 |
| #6 | `comms_check()` Funktionsspec | ✅ abgeschlossen | README Runtime-Helper;<br>doc.md;<br>Toolkit 11 |
| #7 | Save-Dedupe `team.members`→`party.characters` | ✅ abgeschlossen | `systems/gameflow/speicher-fortsetzung.md` |
| #8 | Doppelte `logs.fr_interventions[]`-Zeile | ✅ abgeschlossen | `systems/gameflow/speicher-fortsetzung.md` |
|  | entfernen |  |  |
| #9 | Acceptance 12 Reihenfolge Boss-Toast vs. Badge | ✅ abgeschlossen | README QA-Checks 2025-06-27 |
| #10 | Wallet-Init Solo→Koop | ✅ abgeschlossen | README Koop-Ökonomie;<br>`systems/gameflow/speicher-fortsetzung.md` |
| #11 | Accessibility-/Offline-Checks in Acceptance-Smoke | ✅ abgeschlossen | README QA-Checks 2025-06-27 |
| #12 | README „Spiel laden“ mit Speicher-Modul syncen | ✅ abgeschlossen | README Spielstart; |
|  |  |  | `systems/gameflow/speicher-fortsetzung.md` |
| #13 | Foreshadow-Reset Evidenz (HUD + QA-Log) präzisieren | ✅ abgeschlossen | README QA-Checks 2025-06-27; |
|  |  |  | Toolkit Schnittstellen |
| #14 | Arena-Save-Guard als Acceptance-Schritt | ✅ abgeschlossen | README Runtime-Helper & QA-Checks |
| #15 | City/Chronopolis Acceptance-Smoke | ✅ abgeschlossen | README QA-Checks 2025-06-27 |

## Formatierungs-Backlog 2025-10 (Dokumentation)

- **QA-Logs 2025-07-05/07-18/10-15:** Markdown-Zeilen > 100 Zeichen kürzen, ohne
  Chatlog-Details zu verlieren. Review offen.
- **Fahrplan-Tabellen (Abschnitt „Maßnahmenpaket Beta-GPT 2025-07“):**
  Tabellen-Spalten neu aufteilen oder Kürzel definieren, damit die Markdown-
  Zeilen unter 100 Zeichen bleiben.

## Maßnahmenpaket Beta-GPT 2025-07-18 (Issues #1–#12)

Der Beta-GPT-Lauf vom 2025-07-18 offenbart neue Regressionen rund um Save-Guards,
HUD-Badges, Persistenz-Flags und Dispatcher-Hinweise. Die Tabelle listet alle
offenen Maßnahmen auf. Detailnotizen stehen im QA-Log 2025-07-18 sowie im
[Rohprotokoll des Beta-GPT-Laufs](../logs/2025-07-18-beta-gpt-delta.md).

| Issue | Thema | Status | Primärreferenzen |
| ----- | -------------------------------------------------- | ---------- | ---------------- |
| #1 | Exfil-SaveGuard & `campaign.exfil.active` Reset | ✅ abgeschlossen – Guard & Reset laut Runtime | runtime.js; |
|  |  |  | `systems/gameflow/speicher-fortsetzung.md` |
| #2 | Mission 5 HUD Gate-Badge (FS 2/2 · Saison 0/4) | ✅ abgeschlossen – HUD blendet `GATE 2/2` ein | runtime.js; |
|  |  |  | README; |
|  |  |  | characters/zustaende-hud-system.md |
| #3 | `SF-OFF` Persistenzflag & Overlay-Kopplung | ✅ abgeschlossen – Flag spiegelt HUD & Save | runtime.js; |
|  |  |  | README; |
|  |  |  | characters/zustaende-hud-system.md |
| #4 | Solo→Koop Wallet-Initialisierung vor Debrief | ✅ abgeschlossen – Wallet-Autoinit aktiv | runtime.js;<br>README |
| #5 | Arena `phase_strike_tax` Persistenz in `logs.psi[]` | ✅ abgeschlossen – Steuer landet im Psi-Log | runtime.js; |
|  |  |  | README; |
|  |  |  | systems/toolkit-gpt-spielleiter.md |
| #6 | Compliance-Flag Mirror Runtime↔Campaign | ✅ abgeschlossen – Mirror `logs.flags` aktiv | runtime.js; |
|  |  |  | systems/toolkit-gpt-spielleiter.md |
| #7 | FIFO-Deckel `logs.offline[]` | ✅ abgeschlossen – Queue capped auf 12 | runtime.js;<br>README |
| #8 | Boss-Gate Badge `GATE` in `scene_overlay()` | ✅ abgeschlossen – Toolkit/GPT spiegeln Badge | runtime.js; |
|  |  |  | systems/toolkit-gpt-spielleiter.md; |
|  |  |  | characters/zustaende-hud-system.md |
| #9 | Dispatcher-Hinweis `!radio clear`/`!alias clear` | ✅ abgeschlossen – Hinweis Teil der Start-Hilfe | runtime.js; |
|  |  |  | README |
| #10 | `px_tracker()` ETA-Heuristik & README-Kommunikation | ✅ abgeschlossen – ETA-Hinweis sync | runtime.js; |
|  |  |  | README |
| #11 | Heist/Street Tag-Normalisierung für Konflikt-Delay | ✅ abgeschlossen – Tagsplit `|`/`,` erlaubt | runtime.js; |
|  |  |  | systems/toolkit-gpt-spielleiter.md |
| #12 | Semver-Mismatch-Fehlertext vereinheitlichen | ✅ abgeschlossen – Dispatcher-Text = README | README; |
|  |  |  | systems/toolkit-gpt-spielleiter.md |

## Maßnahmenpaket Beta-GPT 2025-10-15 (Issues #1–#15)

Der Beta-GPT-Lauf vom 2025-10-15 deckt erneut Diskrepanzen zwischen Acceptance-
Checkliste, Save-Schema, HUD-Badges und Accessibility-/Arena-Flows auf. Die
folgenden Maßnahmen sind offen und müssen mit Wissensmodulen, Dispatcher und
Runtime synchronisiert werden. Detailnotizen stehen im QA-Log 2025-10-15 sowie
im [aktuellen Rohprotokoll](../logs/2025-10-15-beta-gpt-delta.md).

| Issue | Thema | Status | Primärreferenzen |
| ----- | -------------------------------------------------- | --------- | ---------------- |
| #1 | Acceptance-Smoke auf 15 Prüfschritte angleichen | ✅ abgeschlossen | README §QA-Checks 2025-06-27; |
|  |  |  | Tester-Briefing §Acceptance-Smoke |
| #2 | Legacy-Gruppensaves → v6-Migration & Semver-Warnung | ✅ abgeschlossen | runtime.js; |
|  |  |  | systems/gameflow/speicher-fortsetzung.md |
| #3 | `StartMission()` respektiert `skip_entry_choice` | ✅ abgeschlossen | runtime.js; |
|  |  |  | systems/toolkit-gpt-spielleiter.md |
| #4 | Auto-Reset `SF-OFF` nach Mission 5 implementieren | ✅ abgeschlossen | runtime.js; |
|  |  |  | characters/zustaende-hud-system.md |
| #5 | Gate-Badge-Persistenz in M5/M10 HUD spezifizieren | ✅ abgeschlossen | runtime.js; |
|  |  |  | characters/zustaende-hud-system.md |
| #6 | Arena-Phase im Save schemafest verankern | ✅ abgeschlossen | runtime.js; systems/runtime-stub-routing-layer.md |
| #7 | Arena-Logs (`logs.psi[]`) & Cross-Mode-Evidenz | ✅ abgeschlossen | runtime.js; |
|  |  |  | systems/toolkit-gpt-spielleiter.md |
| #8 | NPC-Squad-Autoradio &<br>Preset-Logging | ✅ abgeschlossen | runtime.js;<br>systems/toolkit-gpt-spielleiter.md |
| #9 | `chronopolis_warn_seen`<br>Persistenz & Debrief | ✅ abgeschlossen | runtime.js;<br>README §ITI-HQ & Chronopolis |
| #10 | Hazard-Pay vor Wallet-Split fixieren | ✅ abgeschlossen | runtime.js; |
|  |  |  | systems/gameflow/speicher-fortsetzung.md |
| #11 | Boss-DR-HUD-Toast verpflichtend machen | ✅ abgeschlossen | runtime.js; characters/zustaende-hud-system.md |
| #12 | `logs.foreshadow[]` als Pflichtfeld kennzeichnen | ✅ abgeschlossen | runtime.js; |
|  |  |  | systems/gameflow/speicher-fortsetzung.md |
| #13 | `!accessibility`-Dialog + UI-Persistenz | ✅ abgeschlossen | runtime.js; README §Chat-Kurzbefehle |
| #14 | Dispatcher-Startoption `trigger` dokumentieren | ✅ abgeschlossen | runtime.js; |
|  |  |  | README §Spielstart; |
|  |  |  | Tester-Briefing |
| #15 | Cinematic-HUD-Header nach Briefing erzwingen | ✅ abgeschlossen | runtime.js; |
|  |  |  | characters/zustaende-hud-system.md |

**Stand 2025-10-21:** README, QA-Briefing und Masterprompt spiegeln die 15 Acceptance-Schritte,
`runtime.js`/Toolkit dokumentieren `ShowComplianceOnce()` als Primär-Makro mit Alias
`StoreCompliance()`, und Save-/Modul-Dokumente führen Wallets, HQ-Moments, Logs (`logs.psi[]`,
`logs.fr_interventions[]`, `logs.flags.foreshadow_gate_*`) sowie Modul-9-Begriffe konsistent.

## Maßnahmenpaket Beta-GPT 2025-10-28 (Issues #1–#13)

Der Beta-GPT-Lauf vom 2025-10-28 deckt neue Abweichungen zwischen SaveGuard,
Pflichtfeld-Docs, Arena-Blockern und Ökonomie-/HUD-Texten auf. Die Tabelle bündelt
alle offenen Maßnahmen; Detailnotizen stehen im QA-Log 2025-10-28 und im
Maintainer-Rohprotokoll (Archiv).

| Issue | Thema | Status | Primärreferenzen |
| ----- | -------------------------------------------------- | ------------ | ---------------- |
| #1 | HQ-DeepSave Pflichtfelder vereinheitlichen | 🟠 offen – Serializer & Docs syncen | runtime.js;<br>systems/gameflow/speicher-fortsetzung.md;<br>Modul 12 |
| #2 | Save-Beispiel um Pflichtblöcke erweitern | 🟠 offen – JSON anpassen | Modul 12 |
| #3 | Arena-Active-Blocker im SaveGuard verankern | 🟠 offen – Guard + Toast | runtime.js;<br>characters/zustaende-hud-system.md |
| #4 | Foreshadow-/Gate-Badges terminologisch trennen | 🟠 offen – UI-Strings harmonisieren | characters/zustaende-hud-system.md;<br>runtime.js |
| #5 | Paradoxon-Reset auf Missionsende verzögern | 🟠 offen – ClusterCreate Hook | runtime.js;<br>systems/toolkit-gpt-spielleiter.md |
| #6 | Boss-DR-HUD-Toast als Pflicht overlayn | 🟠 offen – Spawn-Hook fixieren | runtime.js;<br>characters/zustaende-hud-system.md |
| #7 | Mission-5 Self-Reflection Reset an EndMission binden | 🟠 offen – End-Hook klarziehen | runtime.js;<br>systems/gameflow/speicher-fortsetzung.md |
| #8 | Cross-Mode Import Beispielstrecke ergänzen | 🟠 offen – Schrittfolge dokumentieren | Modul 12;<br>README |
| #9 | Mission-/CU-Ökonomie auf eine Formel normieren | 🟠 offen – Tabellen angleichen | Modul 8A;<br>Modul 15;<br>runtime.js |
| #10 | Gate-Badge vs. Toast Anzeige konsolidieren | 🟠 offen – Doppelmeldungen klären | characters/zustaende-hud-system.md;<br>README |
| #11 | Comms-Core Regelblock zentral verankern | 🟠 offen – Core/README ergänzen | README;<br>doc.md |
| #12 | Foreshadow-Mirror Pflichtfeld absichern | 🟠 offen – Save + Status | runtime.js;<br>systems/gameflow/speicher-fortsetzung.md |
| #13 | Accessibility-Preset Beispiel ergänzen | 🟠 offen – Zweites Muster-Save | Modul 12 |

**QA-Testreferenz**
- Regressionstest `!save` mit Minimal-HQ-Save (nur Pflichtfelder). Erwartet:
  Serializer ergänzt fehlende Pflichtblöcke leer und meldet Warnung – keine
  Blocker.

## Regressionstest-Termine 2025

| Zeitraum | Umfang | Status | QA-Log |
| ---------------- | ---------------------------------------------------- | ------ | ------ |
| 19.03.2025 | Acceptance-Smoke-Abgleich (Build 4.2.2) | ✅ abgeschlossen | 2025-03-19 |
| 09.–13.06.2025 | Regression MyGPT-Beta (Spiegelprozesse & Save-Restore) | ✅ abgeschlossen | 2025-06-28 |
| 08.–12.09.2025 | Regression MyGPT-Beta (Arena & Großteam) | ✅ abgeschlossen | 2025-09-11 |
| 08.–12.12.2025 | Regression MyGPT-Beta (Jahresabschluss) | ✅ abgeschlossen | 2025-12-10 |

## Mission 5 Badge-Check (Kurzablauf)

1. HQ-Save mit `scene_overlay().foreshadow == 2` laden.
2. Mission 5 starten und HUD-Einblendungen (`SF-OFF`, Toast) protokollieren.
3. HUD-/Log-Auszug im QA-Log dokumentieren (Akzeptanz-Position 12).
4. Nach Abschluss den Reset auf `SF-ON` prüfen und im QA-Log vermerken.

Der komplette Ablauf ist im Tester-Briefing sowie in `tools/test_acceptance_followups.js`
dokumentiert.

## Pflege & Reporting

- Audit und QA-Log nach jeder Maßnahme aktualisieren und Commits verlinken.
- PR-Beschreibungen auf betroffene QA-Log-Abschnitte verweisen.
- Regressionstermine nach jedem Lauf hier und im QA-Log abhaken.
- Debrief-Auszugsprotokolle (`logs.market[]`, Foreshadow, Funk) weiterhin im
  QA-Log archivieren.

