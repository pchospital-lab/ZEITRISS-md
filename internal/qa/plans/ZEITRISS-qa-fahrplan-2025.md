---
title: "ZEITRISS QA-Fahrplan 2025"
version: 1.5.0
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

| Datum       | Schwerpunkt                    | Referenzen |
| ----------- | ------------------------------ | ---------- |
| 2025-06-11  | Repo-Analyse & Maßnahmenplan   | README §QA-Artefakte; QA-Log 2025-06-22 |
| 2025-06-12  | Runtime-Stubs & Routing-Layer  | `systems/runtime-stub-routing-layer.md`; QA-Log 2025-06-22 |
| 2025-06-13  | Beta-GPT-Nachlauf              | QA-Log 2025-06-13; Maßnahmenpaket Beta-GPT 2025-06 |
| 2025-06-14  | Offline-Audit Jammer-Flow      | QA-Log 2025-06-14 |
| 2025-06-15  | QA-Follow-up-Mapping           | QA-Log 2025-06-22 |
| 2025-06-16  | Follow-ups & Checklisten       | QA-Log 2025-06-22 |
| 2025-06-17  | Koop-Debrief & Wallet-Split    | README §HQ/Chronopolis; QA-Log 2025-06-20 |
| 2025-06-18  | Compliance-Abgleich            | `runtime.js` 4.2.2; README §§Runtime-Flags & Offline-Protokoll |
| 2025-06-19  | Pre-City-Hub Dokumentation     | README §ITI-HQ & Chronopolis; QA-Log 2025-06-19 |
| 2025-06-22  | Fahrplan-/QA-Log-Synchronität | QA-Log 2025-06-22 |
| 2025-07-05  | Beta-GPT Deltas (Save/HUD/Arena) | QA-Log 2025-07-05 |

Detailnotizen zu jeder Session befinden sich im QA-Audit.

## Arbeitsstränge & Ziele

- **Dokumentation & Index** – README, Repo-Map und `master-index.json` verweisen
  konsistent auf Audit, Fahrplan und QA-Log.
- **Beitragsprozesse** – `CONTRIBUTING.md` und `AGENTS.md` spiegeln den aktuellen
  QA-Workflow.
- **Tests & Automation** – Makefile- und Script-Läufe sind dokumentiert; Smoke-
  und Spezialtests werden im QA-Log belegt.
- **Wissensspiegel** – Wissensmodule enthalten die Spiegel der lokalen Runtimes;
  Abweichungen werden mit Commit-ID im QA-Log erfasst.
- **Datenschutz & Plattformen** – Maintainer-Ops, Audit und Fahrplan halten
  Plattformhinweise und Offline-First-Vorgaben synchron.

## Maßnahmenübersicht Beta-GPT 2025-06 (Issues #1–#16)

Alle Maßnahmen des Beta-GPT-Laufs Juni 2025 sind abgeschlossen. Die Tabelle
fasst Status und Hauptverweise zusammen; weiterführende Evidenz steht im
QA-Audit und im Beta-QA-Log.

| Issue | Thema                      | Status | Primärreferenzen |
| ----- | -------------------------- | ------ | ---------------- |
| #1    | Save-Schema                | ✅ abgeschlossen | `runtime.js`; Modul 12; QA-Log 2025-06-29 |
| #2    | Save-Normalisierung        | ✅ abgeschlossen | `runtime.js`; QA-Log 2025-06-11 |
| #3    | Arc-Dashboard              | ✅ abgeschlossen | `runtime.js`; QA-Log 2025-06-13 |
| #4    | Load-Flows                 | ✅ abgeschlossen | Toolkit; QA-Log 2025-06-11 |
| #5    | Exfil-Policy               | ✅ abgeschlossen | README; QA-Log 2025-06-11 |
| #6    | PvP-Modusflag              | ✅ abgeschlossen | `runtime.js`; QA-Log 2025-06-24 |
| #7    | Accessibility-Menü         | ❌ verworfen     | Maintainer:innen-Entscheid 2025-06-13 |
| #8    | Offline-Fallback           | ✅ abgeschlossen | Toolkit; QA-Log 2025-06-18 |
| #9    | Versionierung              | ✅ abgeschlossen | `runtime.js`; QA-Log 2025-06-11 |
| #10   | Foreshadow-Log             | ✅ abgeschlossen | `runtime.js`; QA-Log 2025-06-27 |
| #11   | Koop-Ökonomie              | ✅ abgeschlossen | README; Modul 12; QA-Log 2025-06-20 |
| #12   | Chronopolis-Warnung        | ✅ abgeschlossen | `runtime.js`; QA-Log 2025-06-11 |
| #13   | Ask→Suggest                | ✅ abgeschlossen | Toolkit; QA-Log 2025-06-27 |
| #14   | Suspend-Snapshot           | ✅ abgeschlossen | Toolkit; QA-Log 2025-06-22 |
| #15   | PSI-Arena-Regeln           | ✅ abgeschlossen | `runtime.js`; QA-Log 2025-06-27 |
| #16   | Markt-Log                  | ✅ abgeschlossen | README; Modul 15; QA-Log 2025-06-28 |

## Maßnahmenpaket Beta-GPT 2025-07 (Issues #1–#15)

Der Beta-GPT-Lauf vom 2025-07-05 lieferte neue Findings rund um Save-Versionen,
Foreshadow-Darstellung, Arena-/Comms-Makros und Acceptance-Checks. Die folgende
Tabelle dokumentiert den offenen Maßnahmenblock. Detailnotizen: QA-Log
2025-07-05 sowie [Rohprotokoll des Beta-GPT-Laufs](../logs/2025-07-05-beta-gpt-delta.md)
und das ergänzende Chatprotokoll (Maintainer:innen-Archiv).

| Issue | Thema                                              | Status       | Primärreferenzen |
| ----- | -------------------------------------------------- | ------------ | ---------------- |
| #1    | Save-Version 5→6 Angleichen (Serializer, Migration) | ✅ abgeschlossen | README; `systems/gameflow/speicher-fortsetzung.md` |
| #2    | Foreshadow Gate vs. Season Total trennen            | ✅ abgeschlossen | README QA-Checks 2025-06-27; Toolkit Modul 16 |
| #3    | `scene_overlay()`/`!boss status` Schnittstellen     | ✅ abgeschlossen | README Runtime-Helper; Toolkit Modul 16 |
| #4    | `SF-OFF`-Badge Preconditions dokumentieren          | ✅ abgeschlossen | README Schnellstart & QA-Checks |
| #5    | `arenaStart(options)` Makro + HUD-Toast             | ✅ abgeschlossen | README Runtime-Helper; Toolkit Schnittstellen |
| #6    | `comms_check()` Funktionsspec                       | ✅ abgeschlossen | README Runtime-Helper; `doc.md`; Toolkit Modul 11 |
| #7    | Save-Dedupe `team.members`→`party.characters`       | ✅ abgeschlossen | `systems/gameflow/speicher-fortsetzung.md` |
| #8    | Doppelte `logs.fr_interventions[]`-Zeile entfernen  | ✅ abgeschlossen | `systems/gameflow/speicher-fortsetzung.md` |
| #9    | Acceptance 12 Reihenfolge Boss-Toast vs. Badge      | ✅ abgeschlossen | README QA-Checks 2025-06-27 |
| #10   | Wallet-Init Solo→Koop                               | ✅ abgeschlossen | README Koop-Ökonomie; `systems/gameflow/speicher-fortsetzung.md` |
| #11   | Accessibility-/Offline-Checks in Acceptance-Smoke   | ✅ abgeschlossen | README QA-Checks 2025-06-27 |
| #12   | README „Spiel laden“ mit Speicher-Modul syncen      | ✅ abgeschlossen | README Spielstart; `systems/gameflow/speicher-fortsetzung.md` |
| #13   | Foreshadow-Reset Evidenz (HUD + QA-Log) präzisieren | ✅ abgeschlossen | README QA-Checks 2025-06-27; Toolkit Schnittstellen |
| #14   | Arena-Save-Guard als Acceptance-Schritt             | ✅ abgeschlossen | README Runtime-Helper & QA-Checks |
| #15   | City/Chronopolis Acceptance-Smoke                   | ✅ abgeschlossen | README QA-Checks 2025-06-27 |

## Regressionstest-Termine 2025

| Zeitraum         | Umfang                                              | Status | QA-Log |
| ---------------- | ---------------------------------------------------- | ------ | ------ |
| 19.03.2025       | Acceptance-Smoke-Abgleich (Build 4.2.2)              | ✅ abgeschlossen | 2025-03-19 |
| 09.–13.06.2025   | Regression MyGPT-Beta (Spiegelprozesse & Save-Restore) | ✅ abgeschlossen | 2025-06-28 |
| 08.–12.09.2025   | Regression MyGPT-Beta (Arena & Großteam)             | ✅ abgeschlossen | 2025-09-11 |
| 08.–12.12.2025   | Regression MyGPT-Beta (Jahresabschluss)              | ✅ abgeschlossen | 2025-12-10 |

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

