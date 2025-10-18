---
title: "ZEITRISS QA-Fahrplan 2025"
version: 1.8.6
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
`make lint` bündelt beide Runtime-Läufe sowie Doc-Link-, Umlaut- und Markdown-
Checks in einem Schritt.

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
| 2025-06-12 | Runtime-Stubs & Routing-Layer | SR; QA-Log 2025-06-22 |
| 2025-06-13 | Beta-GPT-Nachlauf | QA-Log 2025-06-13; Maßnahmenpaket Beta-GPT 2025-06 |
| 2025-06-14 | Offline-Audit Jammer-Flow | QA-Log 2025-06-14 |
| 2025-06-15 | QA-Follow-up-Mapping | QA-Log 2025-06-22 |
| 2025-06-16 | Follow-ups & Checklisten | QA-Log 2025-06-22 |
| 2025-06-17 | Koop-Debrief & Wallet-Split | README §HQ/Chronopolis; QA-Log 2025-06-20 |
| 2025-06-18 | Compliance-Abgleich | RT 4.2.2; R(Flags) |
| 2025-06-19 | Pre-City-Hub Dokumentation | README §ITI-HQ & Chronopolis; QA-Log 2025-06-19 |
| 2025-06-22 | Fahrplan-/QA-Log-Synchronität | QA-Log 2025-06-22 |
| 2025-07-05 | Beta-GPT Deltas (Save/HUD/Arena) | QA-Log 2025-07-05 |
| 2025-07-18 | Beta-GPT Regression Save/HUD/Compliance | QA-Log 2025-07-18 |
| 2025-10-21 | Beta-GPT 2025-10-15 Nacharbeiten validiert | QA-Log 2025-10-21 |
| 2025-10-28 | Beta-GPT 2025-10-28 Deltas dokumentiert | QA-Log 2025-10-28; Maßnahmenpaket Beta-GPT 2025-10-28 |
| 2025-10-29 | HQ-DeepSave & Wissensspiegel entschlackt | QA-Log 2025-10-29 |
| 2025-10-30 | QA-Artefakte sichtbar verknüpft | QA-Log 2025-10-30 |
| 2025-10-31 | Wissensmodule von QA-Hinweisen bereinigt | QA-Log 2025-10-31 |
| 2025-11-01 | Deepcheck-Sync & Fahrplan 1.8.5 | QA-Log 2025-11-01 |
| 2025-11-02 | Wissensmodule entschlackt (Review) | QA-Log 2025-11-02 |

Detailnotizen zu jeder Session befinden sich im QA-Audit.

## Arbeitsstränge & Ziele

- **Dokumentation & Index** – README, Repo-Map und `master-index.json` halten
  die Runtime-Referenz schlank. *Stand 2025-10-31:* Die Dokumenten-Landkarte
  verweist ausschließlich auf runtime-relevante Module; QA-Artefakte bleiben in
  `internal/qa/` dokumentiert und werden außerhalb des Wissensspeichers
  gepflegt.
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
- [x] `systems/gameflow/speicher-fortsetzung.md` strukturell neu gliedern
      (Zeilenführung, Abschnittslogik, Semantik „Load-Verhalten“ bis
      „Koop-Debrief“) und Abgleich mit Laufzeit-Flows dokumentieren.
- [x] `gameplay/kampagnenstruktur.md` auf QA-fremde Abschnitte prüfen (z. B.
      „Performance-Ziele“, „Build-Roadmap“) und entscheiden, ob diese Inhalte in
      Wissensmodule oder interne Dev-Dokumente gehören.

## Maßnahmenübersicht Beta-GPT 2025-06 (Issues #1–#16)

**Referenzkürzel**

`R` = README.md (Abschnittskürzel in Klammern, z. B. `R(QA)` → README §QA-Checks 2025-06-27)  
`RT` = runtime.js  
`M12` = systems/gameflow/speicher-fortsetzung.md  
`TK(16)` = systems/toolkit-gpt-spielleiter.md – Modul 16  
`TK(11)` = systems/toolkit-gpt-spielleiter.md – Modul 11  
`HUD` = characters/zustaende-hud-system.md  
`DOC` = doc.md  
`BRF` = docs/qa/tester-playtest-briefing.md  
`CW` = systems/currency/cu-waehrungssystem.md  
`GM` = gameplay/kreative-generatoren-missionen.md  
`SR` = internal/runtime/runtime-stub-routing-layer.md

README-Abschnittskürzel:  
`R(QA)` = README §QA-Checks 2025-06-27  
`R(RT)` = README §Runtime-Helper  
`R(Schnell)` = README §Schnellstart & QA-Checks  
`R(Flags)` = README §§Runtime-Flags & Offline-Protokoll  
`R(Koop)` = README §Koop-Ökonomie  
`R(Start)` = README §Spielstart  
`R(Chrono)` = README §ITI-HQ & Chronopolis  
`R(Chat)` = README §Chat-Kurzbefehle

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

| Issue | Thema | Status | Primärref. |
| ----- | ------------------------------ | ------------ | ---------- |
| #1 | Save-Version 5→6 angleichen | ✅ abgeschlossen | R; M12 |
| #2 | Foreshadow Gate vs. Season Total trennen | ✅ abgeschlossen | R(QA); TK(16) |
| #3 | `scene_overlay()`/`!boss status` | ✅ abgeschlossen | R(RT); TK(16) |
| #4 | `SF-OFF`-Badge Preconditions | ✅ abgeschlossen | R(Schnell) |
| #5 | `arenaStart(options)` Makro + HUD-Toast | ✅ abgeschlossen | R(RT); TK(16) |
| #6 | `comms_check()` Funktionsspec | ✅ abgeschlossen | R(RT); DOC; TK(11) |
| #7 | Save-Dedupe `team.members`→`party.characters` | ✅ abgeschlossen | M12 |
| #8 | `logs.fr_interventions[]` doppelt | ✅ abgeschlossen | M12 |
| #9 | Acceptance 12 Reihenfolge Badge/Toast | ✅ abgeschlossen | R(QA) |
| #10 | Wallet-Init Solo→Koop | ✅ abgeschlossen | R(Koop); M12 |
| #11 | Accessibility-/Offline-Checks | ✅ abgeschlossen | R(QA) |
| #12 | README „Spiel laden“ syncen | ✅ abgeschlossen | R(Start); M12 |
| #13 | Foreshadow-Reset Evidenz | ✅ abgeschlossen | R(QA); TK(16) |
| #14 | Arena-Save-Guard Acceptance | ✅ abgeschlossen | R(RT); R(QA) |
| #15 | City/Chronopolis Acceptance | ✅ abgeschlossen | R(QA) |

## Formatierungs-Backlog 2025-10 (Dokumentation)

- ✅ **QA-Logs 2025-07-05/07-18/10-15:** Markdown-Zeilen unter 100 Zeichen
  gebracht (Stand 2025-10-21).
- ✅ **Fahrplan-Tabellen „Maßnahmenpaket Beta-GPT 2025-07“:** Spaltenkürzel
  geprüft, Zeilenlängen passen (Stand 2025-10-21).

Aktuell keine offenen Formatierungsaufgaben.

## Maßnahmenpaket Beta-GPT 2025-07-18 (Issues #1–#12)

Der Beta-GPT-Lauf vom 2025-07-18 offenbart neue Regressionen rund um Save-Guards,
HUD-Badges, Persistenz-Flags und Dispatcher-Hinweise. Die Tabelle listet alle
offenen Maßnahmen auf. Detailnotizen stehen im QA-Log 2025-07-18 sowie im
[Rohprotokoll des Beta-GPT-Laufs](../logs/2025-07-18-beta-gpt-delta.md).

| Issue | Thema | Status | Primärref. |
| ----- | ------------------------------ | ---------------------- | ---------- |
| #1 | Exfil-SaveGuard & `campaign.exfil.active` Reset | ✅ – Guard & Reset RT | RT; M12 |
| #2 | Mission 5 HUD Gate-Badge (FS 2/2 · Saison 0/4) | ✅ – HUD `GATE 2/2` | RT; R; HUD |
| #3 | `SF-OFF` Persistenzflag & Overlay | ✅ – HUD & Save in Sync | RT; R; HUD |
| #4 | Solo→Koop Wallet-Initialisierung | ✅ – Wallet-Autoinit | RT; R; M12 |
| #5 | Arena `phase_strike_tax` Persistenz | ✅ – Psi-Log aktiv | RT; R; TK(16) |
| #6 | Compliance-Flag Mirror Runtime↔Campaign | ✅ – Mirror aktiv | RT; TK(16) |
| #7 | FIFO-Deckel `logs.offline[]` | ✅ – Queue = 12 | RT; R |
| #8 | Boss-Gate Badge `GATE` in `scene_overlay()` | ✅ – Toolkit spiegelt | RT; TK(16); HUD |
| #9 | Dispatcher-Hinweis `!radio clear`/`!alias clear` | ✅ – Start-Hilfe | RT; R |
| #10 | `px_tracker()` ETA-Heuristik | ✅ – ETA-Hinweis | RT; R |
| #11 | Heist/Street Tag-Normalisierung | ✅ – Split `|`/`,` | RT; TK(16) |
| #12 | Semver-Mismatch-Fehlertext | ✅ – Dispatcher = R | R; TK(16) |

## Maßnahmenpaket Beta-GPT 2025-10-15 (Issues #1–#15)

Der Beta-GPT-Lauf vom 2025-10-15 deckt erneut Diskrepanzen zwischen Acceptance-
Checkliste, Save-Schema, HUD-Badges und Accessibility-/Arena-Flows auf. Die
folgenden Maßnahmen sind offen und müssen mit Wissensmodulen, Dispatcher und
Runtime synchronisiert werden. Detailnotizen stehen im QA-Log 2025-10-15 sowie
im [aktuellen Rohprotokoll](../logs/2025-10-15-beta-gpt-delta.md).

| Issue | Thema | Status | Primärref. |
| ----- | ------------------------------ | ------------ | ---------- |
| #1 | Acceptance-Smoke auf 15 Prüfschritte | ✅ abgeschlossen | R(QA); BRF |
| #2 | Legacy-Gruppensaves → v6-Migration | ✅ abgeschlossen | RT; M12 |
| #3 | `StartMission()` respektiert `skip_entry_choice` | ✅ abgeschlossen | RT; TK(16) |
| #4 | Auto-Reset `SF-OFF` nach Mission 5 | ✅ abgeschlossen | RT; HUD |
| #5 | Gate-Badge-Persistenz in M5/M10 HUD | ✅ abgeschlossen | RT; HUD |
| #6 | Arena-Phase im Save verankern | ✅ abgeschlossen | RT; SR |
| #7 | Arena-Logs & Cross-Mode-Evidenz | ✅ abgeschlossen | RT; TK(16) |
| #8 | NPC-Squad-Autoradio & Preset-Logging | ✅ abgeschlossen | RT; TK(16) |
| #9 | `chronopolis_warn_seen` Persistenz & Debrief | ✅ abgeschlossen | RT; R(Chrono) |
| #10 | Hazard-Pay vor Wallet-Split | ✅ abgeschlossen | RT; M12 |
| #11 | Boss-DR-HUD-Toast verpflichtend | ✅ abgeschlossen | RT; HUD |
| #12 | `logs.foreshadow[]` als Pflichtfeld | ✅ abgeschlossen | RT; M12 |
| #13 | `!accessibility`-Dialog + UI-Persistenz | ✅ abgeschlossen | RT; R(Chat) |
| #14 | Dispatcher-Startoption `trigger` | ✅ abgeschlossen | RT; R(Start); BRF |
| #15 | Cinematic-HUD-Header nach Briefing | ✅ abgeschlossen | RT; HUD |

**Stand 2025-10-21:** README, QA-Briefing und Masterprompt spiegeln die 15 Acceptance-Schritte,
`runtime.js`/Toolkit dokumentieren `ShowComplianceOnce()` als Primär-Makro mit Alias
`StoreCompliance()`, und Save-/Modul-Dokumente führen Wallets, HQ-Moments, Logs (`logs.psi[]`,
`logs.fr_interventions[]`, `logs.flags.foreshadow_gate_*`) sowie Modul-9-Begriffe konsistent.

## Maßnahmenpaket Beta-GPT 2025-10-28 (Issues #1–#13)

Der Beta-GPT-Lauf vom 2025-10-28 deckt neue Abweichungen zwischen SaveGuard,
Pflichtfeld-Docs, Arena-Blockern und Ökonomie-/HUD-Texten auf. Die Tabelle bündelt
alle offenen Maßnahmen; Detailnotizen stehen im QA-Log 2025-10-28 und im
Maintainer-Rohprotokoll (Archiv).

| Issue | Thema | Status | Primärref. |
| ----- | ------------------------------ | ------------ | ---------- |
| #1 | HQ-DeepSave Pflichtfelder vereinheitlichen | ✅ – Serializer prüft HUD/Logs | RT; M12 |
| #2 | Save-Beispiel um Pflichtblöcke erweitern | ✅ – JSON aktualisiert | M12 |
| #3 | Arena-Active-Blocker im SaveGuard | ✅ – Guard aktiviert | RT; R |
| #4 | Foreshadow-/Gate-Badges trennen | ✅ – Gate-Label harmonisiert | HUD; RT; BRF |
| #5 | Paradoxon-Reset auf Missionsende | ✅ – Reset-Flag + Toast | RT; TK(16); R |
| #6 | Boss-DR-HUD-Toast Pflicht | ✅ – Toast & DR-Wert | RT; R |
| #7 | Mission-5 Self-Reflection Reset | ✅ – Debrief-Reset | RT; M12 |
| #8 | Cross-Mode Import Beispielstrecke | ✅ – Doku erweitert | M12; R |
| #9 | Mission-/CU-Ökonomie Formel | ✅ – Formel & Fallback | GM; CW; RT |
| #10 | Gate-Badge vs. Toast Anzeige | ✅ – Einmalige Warnung | TK(16); R |
| #11 | Comms-Core Regelblock | ✅ – Core-Sektion & Verweis | R; DOC |
| #12 | Foreshadow-Mirror Pflichtfeld | ✅ – SaveGuard + Beispiel | RT; M12 |
| #13 | Accessibility-Preset Beispiel | ✅ – Zweites Muster-Save | M12 |

**QA-Testreferenz**
- Regressionstest `!save` mit Minimal-HQ-Save (nur Pflichtfelder). Erwartet:
  Serializer ergänzt fehlende Pflichtblöcke leer und meldet Warnung – keine
  Blocker.

## Regressionstest-Termine 2025

| Zeitraum | Umfang | Status | QA-Log |
| ---------------- | ---------------------------------------------------- | ------ | ------ |
| 19.03.2025 | Acceptance-Smoke-Abgleich (Build 4.2.2) | ✅ abgeschlossen | 2025-03-19 |
| 09.–13.06.2025 | Regression MyGPT-Beta (Spiegel/Saves) | ✅ abgeschlossen | 2025-06-28 |
| 08.–12.09.2025 | Regression MyGPT-Beta (Arena & Großteam) | ✅ abgeschlossen | 2025-09-11 |
| 08.–12.12.2025 | Regression MyGPT-Beta (Jahresabschluss) | ✅ abgeschlossen | 2025-12-10 |

## Mission 5 Badge-Check (Kurzablauf)

1. HQ-Save mit `scene_overlay()` → `GATE 2/2` laden.
2. Mission 5 starten und HUD-Einblendungen (`SF-OFF`, Gate-Badge, Boss-DR-Toast) protokollieren.
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

