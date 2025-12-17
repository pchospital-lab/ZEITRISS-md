---
title: "ZEITRISS QA-Fahrplan 2025"
version: 1.13.6
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
| 2025-11-03 | QA-Fahrplan 1.8.6 Sync & Wissensmodule-Check | QA-Log 2025-11-03 |
| 2025-11-04 | Deepcheck-Fortsetzung & Fahrplan 1.8.7 Mirror | QA-Log 2025-11-04 |
| 2025-11-06 | Regression Audit-Maßnahmen #13–#20 | QA-Log 2025-11-06 |
| 2025-11-26 | Simulativer Acceptance-/Save-Lauf | QA-Log 2025-11-26 |
| 2025-12-03 | Testprompt Voll-Lauf (Acceptance 1–15, Save v6) | QA-Log 2025-12-03 |

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
    Acknowledge, Arena-Schema sowie Alias-/Funk-Logs ab (`tools/test_start.js`,
    `tools/test_accessibility.js`, `tools/test_chronopolis_ack.js`,
    `tools/test_arena_schema.js`, `tools/test_alias_trace.js`).
  - Mission-5-Badge-Flow als automatisierter Follow-up-Check mit Golden File:
    `tools/test_acceptance_followups.js` nutzt
    `internal/qa/fixtures/mission5_badge_snapshots.json`, um Gate 2/2,
    Foreshadow-Badge, SF-OFF/SF-ON-Reset und Boss-DR-Toast stringstabil zu
    prüfen.
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

## Maßnahmenpaket Beta-GPT 2025-12 (Copy-Paste-QA)

Die folgenden Punkte stammen aus dem Copy-Paste-Testlauf (Acceptance 1–15, Save v6) und sind für
den nächsten Umsetzungszyklus einzuplanen. Sie sind priorisiert nach Impact auf Release-Qualität.

### 1. Boss-Gate-Mission 5/10 entkoppeln (Gate fix 2/2, FS separat)

- HUD-Spec `HUD` auf `GATE 2/2 · FS 0/4` zum Missionsstart M5/M10 umstellen, Gate nicht mehr an
  Foreshadow-Counts koppeln.
- Toolkit `TK(16)` (Foreshadow, Suggest & Arena) spiegeln: Gate-Status fix, Foreshadows erhöhen
  nur `FS`.
- Runtime (`RT` → `StartMission()`, `scene_overlay()`) prüfen und falls nötig Gate-Status auf den
  festen Startwert setzen; Boss-Toast/Flags synchronisieren.
- QA: Mission-5-Badge-Check (Prüfnummern 11–12) in Solo/NPC/Koop/Arena erneut laufen lassen.

### 2. `phase`-Feld konsolidieren (technisch lowercase)

- README-Beispiele und Seeds auf `phase: core|transfer|rift` (lowercase) angleichen; Flavor-Groß-
  schreibung aus YAML entfernen.
- Speicher-Doku `M12` ergänzen: HQ-Save immer `phase: core`; Missionslaufzeit steuert
  `campaign.type/scene`.
- Toolkit-Hinweis in `TK(11)`/`TK(16)`: `phase` wird zur Laufzeit gesetzt, Seeds tragen nur den
  Missions-Typ.
- QA: Cross-Mode-Smoke (Solo → Koop → PvP) sicherstellen, dass `phase` konstant bleibt.

### 3. Rift-Seeds mit optionalen Seed-Tiers ergänzen

- Kampagnenstruktur `gameplay/kampagnenstruktur.md` um Hinweise zu optionalen
  Seed-Tiers (Early/Mid/Late) erweitern – ohne Level-Gating, freier Zugriff ab
  Level 1; Beispiel-Seeds nennen und Arc-Dashboard-Spiegel zeigen.
- Optionales Feld `seed_tier` in Arc-Dashboard beschreiben; Seed-Beispiele und
  Save-Schema aktualisieren.
- QA: Drei Rifts fahren (Level 8 / 120 / 500+) und Seed-Zuordnung dokumentieren
  – nur als Balancing-Hinweis, nicht als Sperre.

### 4. Arena-Phase-Strike-Logs von Psi-Heat trennen

- Entscheidung fixieren: neues Feld `logs.arena_psi[]` **oder** verpflichtendes Tagging
  (`category: arena|psi`, `heat_delta` vs. `sys_cost`). Schema in `M12` ergänzen.
- Toolkit-Logger (`phase_strike_cost`/`log_phase_strike_event`) anpassen; README/Psi-Modul um
  QA-Hinweise ergänzen.
- QA: Acceptance 13 erneut (Psi-Heat + Arena-Strike) mit Filterkriterien prüfen.

### 5. Accessibility-Felder robust spiegeln

- Speicher-Doku `M12` klarstellen: `contrast`/`badge_density`/`output_pace` empfohlen, Defaults
  beim Laden wenn Felder fehlen; Serializer setzt explizit nur `gm_style`/`suggest_mode`.
- Optional Defaults im Serializer (`RT` → UI-Prep) ergänzen; README-Beispiel anpassen.
- QA: Save ohne Accessibility-Felder laden, `!accessibility` auf Standardwerte prüfen.

### 6. Save-Beispiele für High-Level-/Rift-Play ergänzen

- Speicher-Doku um Abschnitt „High-Level-Progression (100–1000)“ erweitern und Referenz-Testsave
  (Lvl 8/120/520 mit Seeds 1–25/80–150/400–1000) verlinken.
- QA-Log/Audit auf neuen Testspeicherstand verweisen; Archivierung unter `internal/qa/fixtures`
  prüfen.

### 7. Gear-Alias „Multi-Tool-Armband“ dokumentieren

- Alias-Doku `README`/`Toolkit` um Eintrag „Multi-Tool-Armband → Multi-Tool-Handschuh“ ergänzen;
  Hardware-Regel „kein Armband“ bleibt bestehen.
- QA: Acceptance 9 als Stil-Compliance führen (still mapping, kein neues Item).

### 8. Offline/Ask→Suggest/Alias/Squad-Radio als stabil vermerken

- QA-Abschnitt (README oder QA-Handbuch) um Kurznotiz ergänzen: Ask→Suggest, Offline-FAQ,
  Alias-/Squad-Radio-Logs Smoke bestanden in Solo/NPC/Koop/PvP.
- QA-Log aktualisieren, Status als Referenz für Regressionen markieren.

### 9. Dispatcher-Smoke 0–4 als Referenzstatus halten

- Optional Mini-Tabelle im QA-Kapitel anlegen („Dispatcher-Smoke 0–4 bestanden“), damit künftige
  Änderungen die Basislinie kennen.
- QA: Bei Dispatcher-Änderungen Acceptance 0–4 erneut durchlaufen lassen.
`GM` = gameplay/kreative-generatoren-missionen.md
`SR` = internal/runtime/runtime-stub-routing-layer.md
`PSI` = systems/kp-kraefte-psi.md
`VEH` = gameplay/fahrzeuge-konflikte.md
`MASS` = gameplay/massenkonflikte.md

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

## Maßnahmenpaket Beta-GPT 2025-11-26 (Issues #1–#9)

Der simulative Maintainer-Lauf vom 2025-11-26 deckt Dokumentationslücken rund
um Mission 5 Auto-Reset, Arena-Cross-Mode-Laden, Suggest-Modus-Persistenz und
Save-Beispiele auf. Die Tabelle sammelt alle offenen Punkte; Details stehen im
QA-Log 2025-11-26.

| Issue | Thema | Status | Primärref. |
| ----- | ------------------------------ | ------------ | ---------- |
| #1 | Mission 5 Self-Reflection Auto-Reset Beispiel | ✅ – Save/HUD-Beispiel ergänzt | M12; HUD |
| #2 | Arena-Saves beim Laden auf HQ zurücksetzen | ✅ – Runtime-Reset & Doku | RT; M12 |
| #3 | Acceptance-Smoke-Kurzfassung im Wissensspiegel | ✅ – Kurzabläufe in README/DOC | R(QA); DOC |
| #4 | Foreshadow-Gate-Badge 0/2 vs. 2/2 präzisieren | ✅ – HUD/Toolkit präzisiert | HUD; TK(16) |
| #5 | Save-Beispiel für `modes` inkl. `suggest` | ✅ – Beispielblock dokumentiert | M12; R |
| #6 | Chronopolis-Warncut & Flag-Verhalten erläutern | ✅ – Warncut-Flag erklärt | R(Chrono); M12 |
| #7 | HQ-only SaveGuard: Story-Beispiel für Missionsabbruch | ✅ – Guard-Story im Modul | M12; R |
| #8 | Array-only Gruppensave: Migration mit Wallet-Init | ✅ – Migration & Wallet-Init | M12 |
| #9 | Psi-Heat-Reset (Konflikt vs. HQ) klarziehen | ✅ – Reset-Regel dokumentiert | RT; PSI |

**QA-Testreferenz (11-26 Paket)**
- Mission 5 Badge-Check erneut mit Save-Reset-Flags abbilden.
- Arena-Save in HQ laden und Guard/Reset beobachten.

**QA-Testreferenz (10-28 Paket)**
- Regressionstest `!save` mit Minimal-HQ-Save (nur Pflichtfelder). Erwartet:
  Serializer ergänzt fehlende Pflichtblöcke leer und meldet Warnung – keine
  Blocker.

## Maßnahmenpaket Maintainer 2025-12-02 (Issues #1–#11)

Der erneute Testprompt-Lauf vom 2025-12-02 liefert einen Px-Balancing-Bug und
zehn Dokumentations-/Save-Themen (Acceptance-Spiegel, SaveGuard, Wallets, HUD).
Alle Punkte sind offen und warten auf Umsetzung im Wissensspiegel.

| Issue | Thema | Status | Primärref. |
| ----- | ------------------------------ | ------------ | ---------- |
| #1 | Px-Balancing: Fail/Patzer senken Px | ✅ abgeschlossen | RT; TK(16); R(QA) |
| #2 | Acceptance-Smoke-Liste im Runtime-Set spiegeln | ✅ abgeschlossen | R(QA); DOC; BRF |
| #3 | `select_state_for_save()` Pflichtfelder angleichen | ✅ abgeschlossen | M12; R(Start); RT |
| #4 | Wallet-Init-Begriff vereinheitlichen | ✅ abgeschlossen | M12; R(Koop) |
| #5 | Self-Reflection: Charakterwert hat Vorrang | ✅ abgeschlossen | HUD; RT; M12 |
| #6 | Arena-SaveGuard: `location`-Set und Blocker dokumentieren | ✅ abgeschlossen | R; TK(16); SR |
| #7 | `!accessibility`-Dialog (Optionen → JSON) ausformulieren | ✅ abgeschlossen | R(Chat); HUD |
| #8 | Gruppensaves ohne `team.members[]` zeigen (Legacy nur Migration) | ✅ abgeschlossen | M12 |
| #9 | Suggest-Modus vs. Self-Reflection entkoppeln | ✅ abgeschlossen | TK(16); R(Chat) |
| #10 | Markt-Log auf 24 Einträge limit dokumentieren | ✅ abgeschlossen | M12; CW |
| #11 | PvP-Arena als optionales Endgame kennzeichnen | ✅ abgeschlossen | R(QA); TK(16) |

## Maßnahmenpaket Maintainer 2025-12-12 (Issues #1–#6)

Der jüngste Testprompt-Lauf (inklusive HQ-Deepsave, Mission 5 Badge-Check und
Arena-Cross-Mode) identifiziert sechs neue Dokumentations- und Strukturthemen,
die im Wissensspiegel verankert wurden. Alle Punkte sind umgesetzt und
zwischen README, QA-Briefing, Speichermodul, Psi-Modul und Toolkit
abgestimmt.

| Issue | Thema | Status | Primärref. |
| ----- | ------------------------------ | ------------ | ------------- |
| #1 | Acceptance-Smoke-Checkliste als Runtime-Mirror ergänzen | ✅ abgeschlossen – README/DOC spiegeln Acceptance 1–15 inkl. Dispatcher-Verweis | R(QA); BRF; DOC |
| #2 | Self-Reflection: Truth-Source `character.self_reflection` klarstellen | ✅ abgeschlossen – Speichermodul/HUD priorisieren Charakterwert + Auto-Reset | HUD; RT; M12 |
| #3 | Boss-Gate/Foreshadow Terminologie und Reset-Zeitpunkte vereinheitlichen | ✅ abgeschlossen – HUD/Toolkit-Status und README-Smoke synchronisiert | HUD; TK(16); R(QA) |
| #4 | Cross-Mode Währungs-Sync (Solo→Koop→Arena) mit Schrittfolge dokumentieren | ✅ abgeschlossen – Schrittfolge & Beispiel-Save im Speichermodul | M12; R(Koop); CW |
| #5 | Arena-Psi-Regeln (Phase-Strike, Tax, Buffer) in einem Unterabschnitt bündeln | ✅ abgeschlossen – Psi-Modul bündelt Arena-Psi-Bullets (Tax/Buffer/Logs) | PSI; TK(16); RT |
| #6 | Fahrzeug- und Massenkonflikt-Regeln in Smoke-Flow verankern | ✅ abgeschlossen – doc.md Smoke-Flow mit Arena-/Fahrzeugtests ergänzt | R(QA); VEH; MASS |

**Nächste Schritte (konkret umsetzbar)**

- Alle Maßnahmen des 2025-12-12-Pakets sind gespiegelt. Der Abgleich im QA-Lauf
  2025-12-13 ist bereits abgeschlossen; Details stehen im folgenden
  Maßnahmenpaket.

## Maßnahmenpaket Maintainer 2025-12-13 (Issues #1–#9)

Der aktuelle Testprompt-Voll-Lauf (inklusive HQ-Deepsave und Acceptance 1–15) bringt neun neue
Dokumentations- und Strukturthemen, die in den Wissensmodulen und im Serializer gespiegelt werden
müssen. Der komplette Rohtext liegt unter
`internal/qa/evidence/2025-12-13-testprompt-raw.md`.

| Issue | Thema | Status | Primärref. |
| ----- | ------------------------------ | ------------ | ------------- |
| #1 | Vollständiges v6-Test-Save als Fixture | ✅ abgeschlossen | M12; README |
| #2 | Self-Reflection Flags vs. Charakterwert | ✅ abgeschlossen | HUD; RT; M12 |
| #3 | Versionsstring Modul 12 (4.2.2 vs. 4.2.3) | ✅ abgeschlossen | M12; README; master-index |
| #4 | Single Source of Truth für Rift-Seeds | ✅ abgeschlossen | M12; TK(16); gameplay/kampagnenstruktur.md |
| #5 | Arena-Mode-Reset (campaign.mode ← previous_mode) | ✅ abgeschlossen | TK(16); RT; SR |
| #6 | Host-Regel beim Multi-Save-Import | ✅ abgeschlossen | README; M12 |
| #7 | CU-Formel konsolidieren (Risko, Hazard-Pay, 10×Level) | ✅ abgeschlossen | CW; Modul 15; Modul 8A |
| #8 | Boss-DR nach Teamgröße staffeln | ✅ abgeschlossen | HUD; TK(16); gameplay/kampagnenstruktur.md |
| #9 | Acceptance-Smoke 1–15 als Runtime-Overlay bereitstellen | ✅ abgeschlossen | R(QA); DOC; BRF |

**QA-Testreferenz (12-13 Paket)**
- Acceptance-Smoke erneut mit dem geposteten HQ-Deepsave durchlaufen (Solo → Koop → Arena) und
  gegen das neue Fixture spiegeln.
- Mission-5-Badge-Check und Arena-Exit gezielt beobachten, um Self-Reflection- und Mode-Reset-
  Deltas zu reproduzieren.

## Maßnahmenpaket Copy-Paste-QA 2025-12-XX (Issues #1–#6)

Der Copy-Paste-Lauf ist gespiegelt: Missionsstart zieht die Teamgröße, staffelt den Boss-DR per
Matrix, und Toolkit/HUD spiegeln den Wert samt Toast. Phase-Strike-Logs landen verbindlich in
`logs.arena_psi[]`, Foreshadow-/Gate-Persistenz wurde vereinheitlicht, und die CU-Formel deckt Core-
und Rift-Einsätze inkl. Seeds/Hazard-Pay ab. Cross-Mode-Saves führen strukturierte
`logs.flags.merge_conflicts[]`, und die v6-Fixtures enthalten alle Pflichtcontainer.

| Issue | Thema | Status | Primärref. |
| ----- | ------------------------------ | ------------ | ---------------- |
| #1 | Boss-DR nach Teamgröße statt Fixwerten spiegeln | ✅ abgeschlossen | gameplay/kampagnenstruktur.md; systems/toolkit-gpt-spielleiter.md; systems/wuerfelmechanik.md |
| #2 | Phase-Strike-Logs auf `logs.arena_psi[]` konsolidieren | ✅ abgeschlossen | systems/kp-kraefte-psi.md; gameplay/kampagnenstruktur.md; README.md |
| #3 | Foreshadow-/Gate-Begriffe und Persistenz vereinheitlichen | ✅ abgeschlossen | README.md; systems/toolkit-gpt-spielleiter.md; systems/gameflow/speicher-fortsetzung.md |
| #4 | Rift-CU-Belohnung als Single-Formel dokumentieren | ✅ abgeschlossen | systems/currency/cu-waehrungssystem.md; gameplay/kampagnenstruktur.md |
| #5 | Merge-Konflikte in Cross-Mode-Saves strukturiert loggen | ✅ abgeschlossen | systems/gameflow/speicher-fortsetzung.md; README.md |
| #6 | Pflichtfelder Save v6 mit Fixture absichern (`logs.arena_psi` etc.) | ✅ abgeschlossen | systems/gameflow/speicher-fortsetzung.md; internal/qa/fixtures/ |

**QA-Referenz (Copy-Paste-QA)**

- Acceptance-Smoke #12 Solo+Duo: Boss-DR-Matrix für Teamgrößen 1–5, HUD-Toast spiegelt Toolkit-
  Wert (`campaign.boss_dr`).
- PvP-/Arena-Lauf mit Phase-Strike: Save-Validator erwartet Einträge in `logs.arena_psi[]` mit
  Fähigkeit, Szenario und Kostenquelle (Tax/Buffer).
- Foreshadow-/Gate-Check: `!helper boss` liefert Zahlen, Szenenblockade triggert Toast und wird als
  `logs.foreshadow[]` persistiert; Gate-Flags spiegeln ins Save-Schema.
- Rift-Reward-Regression: Level 8/120/520/1000 bei identischem Risiko und Seeds, Debrief nennt die
  CU-Formel (10×Level×Risiko×Hazard-Pay×Seed-Multiplikator) einheitlich.
- Cross-Mode-Merge: Solo→Koop→PvP mit divergierenden Wallet-/Seed-Deltas erzeugt strukturierte
  `logs.flags.merge_conflicts[]`, HUD zeigt Kurztoast; Save-Merge folgt dem Host-Pfad.
- SaveGuard-Full-Matrix: Fixture `savegame_v6_matrix` und `savegame_v6_highlevel.json` prüfen die
  Pflichtcontainer (`logs.arena_psi[]`, `logs.flags.merge_conflicts[]` usw.), Unknown Fields werden
  toleriert.

## Maßnahmenpaket Maintainer 2025-12-03 (Issues #1–#3)

Der erneute Testprompt-Voll-Lauf liefert drei neue Spiegel-Themen: Accessibility-
Enums divergieren zwischen Schema und Dialog, Offline-Hilfe nutzt verschiedene
Feldnamen und die 15er Acceptance-Liste ist im Runtime-Set zu knapp gespiegelt.
Alle Punkte sind umgesetzt.

| Issue | Thema | Status | Primärref. |
| ----- | ------------------------------ | ------------ | ------------- |
| #1 | Badge-Dichte/Output-Pace vereinheitlichen (`full|minimal` → `standard|compact`) | ✅ abgeschlossen | M12; RT; R(QA) |
| #2 | Offline-Hilfe-Feldname auf `offline_help_last_scene` konsolidieren | ✅ abgeschlossen | M12; RT; SR |
| #3 | Acceptance-Smoke 1–15 im Runtime-Mirror schließen (Boss/SF/SUG/Psi/Access/Arena) | ✅ abgeschlossen | R(QA); DOC; BRF |

## Maßnahmenpaket Copy-Paste-QA 2025-12-XX (Issues #1–#15)

Der Copy-Paste-Testlauf (Acceptance 1–15, Save v6, Multi-Level-Seed-Set) liefert 15 neue Findings.
Sie werden in den kommenden Durchläufen sukzessive abgearbeitet. Rohreferenz: vollständiger
Save-Block (HQ/Core, Px 4/5, Seeds #011/#085/#404, Wallet 4×) sowie die Mission-5-Badge-Abfolge:
SF-OFF vor Start, Gate 2/2, Boss-DR-Toast in Szene 10, Auto-Reset auf SF-ON bei Abort/Complete.

| Issue | Thema | Status | Primärref. |
| ----- | ------------------------------ | ------------------------- | ---------------- |
| #1 | QA-Mode für `ShowComplianceOnce()` (HUD-Toast-Kanal) | ✅ abgeschlossen | RT; R; TK(16) |
| #2 | Save-Schema v6 vs. README (Single Source, `field_notes`, `team.members`) | ✅ abgeschlossen – README & Modul 12 verweisen auf einheitliches Schema | M12; R |
| #3 | Mission 5 Auto-Reset-Toast und QA-Schritt 0 „SF toggeln“ verankern | ✅ abgeschlossen – QA-Briefing führt Schritt 0 `!sf off`, HUD-Reset bleibt dokumentiert | RT; HUD; BRF |
| #4 | SaveGuard-Copy vereinheitlichen (`toast_save_block(reason)`) | ✅ abgeschlossen – HQ-/Arena-/Exfil-Blocker teilen denselben Text | RT; R |
| #5 | Gear-Alias „Multi-Tool-Armband → Handschuh“ auch im Live-Equip | ✅ abgeschlossen – Runtime normalisiert Loadouts/Saves auf den Handschuh | RT; TK(16); R |
| #6 | Dispatcher-Fehlertexte Startoptionen auf Acceptance-Strings trimmen | ✅ abgeschlossen – Gruppe/NPC-Fehler ohne Markdown | RT; TK(16) |
| #7 | Gruppensave-Doku auf v6-kanonisch (Legacy nur Import) festziehen | ✅ abgeschlossen – `party.characters[]` ist die einzige Quelle, Legacy-Spiegel dokumentiert | M12; R |
| #8 | `logs.field_notes[]` Pflicht vs. optional entscheiden und spiegeln | ✅ abgeschlossen – Feld optional, Serializer/Docs spiegeln leere Arrays | M12; R |
| #9 | CU-Belohnungsformel vereinheitlichen (Quickstart/Generator/Währung) | ✅ abgeschlossen – Schnellstart/Generator/CW nutzen einheitliche Risiko/Seed/Hazard-Formel | CW; GM; R |
| #10 | Px-Policy für Rifts klären (`campaign.px` vs. `rift_px`) | ✅ abgeschlossen – `campaign.px` ist Single Source, `rift_px` wird verworfen | R; M12; gameplay/kampagnenstruktur.md |
| #11 | Rift-Seeds um Cluster/Level-Metadaten erweitern (1–25/80–150/400–1000) | ✅ abgeschlossen – optionale `cluster_hint`/`level_hint` in Save/Dashboard dokumentiert | gameplay/kampagnenstruktur.md; M12 |
| #12 | Wallet-Splitting: Restverteilung deterministisch loggen | ✅ abgeschlossen – Roster-Order & HQ-Pool-Hinweis fix | R; M12 |
| #13 | Artefaktwirtschaft: Sink/Salvage einführen (kein Verkauf) | ✅ abgeschlossen – Archiv-/Salvage-Sink ersetzt Verkäufe, keine CU-Auszahlung | CW; README; gameplay/kampagnenstruktur.md |
| #14 | Arena-Ladepolitik: Lobby-Saves/Resume-Token definieren | ✅ abgeschlossen | RT; SR; R |
| #15 | Rift-Launch-Guards auf v6-Felder normalisieren (`location`, Seeds als Objekte) | ✅ abgeschlossen | TK(16); M12; RT; R |

**QA-Testreferenz (Rohform Copy-Paste-Lauf)**

- Save v6 (HQ, ARC 1/EP 2/MS 4, Seeds #011/#085/#404, Squad-Level 7/120/580/1000, Wallet-Split
  4×) inkl. HUD/Logs/Flags als Fixture-Basis.
- Mission 5 Badge-Check: Start mit `!sf off`, HUD `GATE 2/2 · FS 0/4 · SF-OFF`, Boss-DR-Toast in
  Szene 10, Auto-Reset auf SF-ON bei Abort/Complete, Log-Feld
  `self_reflection_auto_reset_reason` gesetzt.
- Smoke #8 SaveGuard: HQ-only-Toast vs. Mission/Exfil/Arena-Blocker, Snapshot-Toleranz prüfen.
- Smoke #9 Gear-Alias: Command „Multi-Tool-Armband ausrüsten“ mappt still auf Handschuh, optional
  `logs.alias_trace[]`/`logs.hud[]`.
- Dispatcher-Smoke #4/#6: Startoptionen `npc-team 5` bzw. `gruppe 3` ohne Markdown, Strings
  Acceptance-konform.
- Economy/Rift/Wallet: CU-Formel für identische Mission in Core vs. Rift (Seeds/Hazard-Pay),
  Wallet-Split inkl. Rest-Policy loggen, Paradoxon-Index-Verhalten in Rift klarstellen.
- Arena: Load resettet auf HQ, Phase-Strike-Tax in `logs.arena_psi[]`, Option für Lobby-Resume
  klären.

## Maßnahmenpaket Copy-Paste-QA 2026-01 (Issues #1–#16, Rohform)

Der jüngste Copy-Paste-Testlauf (Solo, Solo+Squad, Koop, PvP; Seeds 1–25/80–150/400–1000) brachte
16 neue Befunde plus zusätzliche Vorgaben der Tester:innen. Alle Punkte sind abgeschlossen und
werden im Umsetzungsstand dokumentiert; die Rohbeobachtungen aus den HUD-/Log-Auszügen bleiben hier
erhalten, damit keine Kontextdetails verloren gehen.

### Globale Leitplanken

- Artefakte und Relikte sollen ohne Sonderregeln wie reguläre Items handelbar bleiben; keine
  Ausnahmen in Economy- oder Save-Flows.
- Ruf/Fraktionen/Preserve-Trigger strenger fassen (langsamer Progress), idealerweise bereits in
  der Charactererstellung verankern.
- Deepsave erzwingen: Bei „speichern“/„deepsave“ im HQ immer einen vollständigen JSON-Deepsave
  schreiben; „light save“ eliminieren.

### Rohnotizen aus dem Testlauf

- E2E-Läufe pro Modus spielbar, aber es fehlt ein kanonisches E2E-Trace-Schema, das Logs
  (`logs.hud`, `logs.squad_radio`, `logs.kodex`, `logs.foreshadow`, `logs.fr_interventions`) pro
  Szene ablegt.
- Compliance/Ansprache-Flow blockiert Smoke-Runs; benötigt QA-Bypass (`qa_mode`).
- Rift-Seeds: Freischaltung widersprüchlich (Episode vs. Arc); HUD/Toolkit müssen konsolidiert
  werden.
- Gate/Foreshadow-Terminologie driftet (GATE 0/2 vs. Gate 0/4 vs. Foreshadow 2/4); Toasts und HUD
  müssen auf das 2/2-Gate + 4/4-FS-Set festgezogen werden.
- Paradoxon-Effekte weichen zwischen Modulen ab (Stress/HP/SG/Initiative); eine Quelle fehlt.
- SYS-Semantik kollidiert mit SaveGuard (SYS_used vs. freie SYS); `SYS_installed` und
  `SYS_runtime` müssen sauber getrennt werden.
- SaveGuard-Pflichtfelder (`logs.flags.merge_conflicts`, `logs.arena_psi`) fehlen in Beispielen;
  JSON-Schema-Version nötig.
- Accessibility-Persistenz: `save_deep()` speichert nur Teilfelder, `contrast/badge_density/
  output_pace` fehlen nach Load.
- Offline-Hinweis spricht von Save-Sperre, obwohl HQ-only gilt; Text muss Cloud-Sync präzisieren.
- Cross-Mode-Merge verwirft Seeds/Counter still; Konfliktliste muss verpflichtend gefüllt werden.
- Load-Guard erzwingt HQ und verschweigt Arena-Context-Drops; Conflict-Toast fehlt.
- High-Level-Ökonomie (100+/400+/1000) unklar: Rewards vs. Kosten skaliert nicht sauber.
- Artefaktprogression: Drop selten, Verkauf gesperrt, Skalierung im Endgame unattraktiv; braucht
  Research-/Archiv-Value.
- Teamgrößen-Regeln auf 0–4 vereinheitlichen; Fehlermeldungen entsprechend vereinfachen.
- Mission 5 Badge/SF-OFF-Test braucht stringstabile Snapshots (Gate 2/2, FS 0/4, Boss-DR-Toast,
  Auto-Reset-Flags).
- Offizielles, schema-volles QA-Save fehlt (Lvl 7/120/512+, Seeds offen/geschlossen, Wallets,
  Arena/PvP/Psi-Logs) – sollte als Fixture versioniert werden.

### Fahrplan (Issues #1–#16)

| Issue | Kurzfassung | Fahrplan/Nächste Schritte |
| ----- | ------------------------------ | -------------------------------------------- |
| #1 | E2E-Trace-Schema pro Szene/Modus | ✅ Schema & Runtime-Hooks (Start/Rift/Arena) dokumentiert,
| | | Trace landet in `logs.trace[]` |
| #2 | Compliance-QA-Bypass | ✅ `qa_mode` = HUD-Toast-only, Start-Dispatcher übernimmt
| | | Player-Count/Ansprache |
| #3 | Rift-Seed Freischaltung Episode | ✅ Runtime/Toolkit/README angleichen: HQ-only nach Episodenende (AC#10 Mirror) |
| #4 | Gate vs. Foreshadow Terminologie | ✅ `NextScene()` fixiert Gate-Toast auf FS 0/4; HUD
| | | und Boss-Helper spiegeln Gate 2/2 konstant |
| #5 | Paradoxon-Effekte vereinheitlichen | ✅ Single-Source-Tabelle in Modul 12; README verweist auf Px 0–4/5 Schema |
| #6 | SYS-Semantik/SaveGuard trennen | ✅ `SYS_installed`/`SYS_runtime` Pflicht, Save-Migration |
| | | und Fehlermeldungen aktiv |
| #7 | Save-Schema Pflichtfelder | ✅ `saveGame.v6.schema.json` versioniert; Loader prüft Pflichtcontainer; GPT-Kompaktprofil dokumentiert |
| #8 | Accessibility-Persistenz | ✅ `save_deep()` zieht UI-Felder via `prepare_save_ui()`,
| | | SaveGuard erzwingt kompletten Block |
| #9 | Offline-HUD-FAQ präzisieren | ✅ FAQ/Stub/README spiegeln Cloud-Sync & HQ-only-Policy;
| | | QA-Bypass-Text ergänzt |
| #10 | Cross-Mode-Merge-Konflikte | ✅ Loader-Hook `push_merge_conflict()` protokolliert Seeds/Counter/UI/Arena |
| #11 | Arena-Load-Konfliktmarkierung | ✅ Load erzeugt Toast + `merge_conflicts` bei Arena-State |
| #12 | High-Level-Ökonomie | ✅ Modul 15 führt die Level-100/400/1000-Tabelle (Reward vs. Sinks),
| | | README verweist auf Seed-Stack/Hazard-Pay und unveränderte Wallet-Splits |
| #13 | Artefaktprogression | ✅ Modul 15 dokumentiert Research-/Archivwerte und prozentuale Buffs,
| | | freier Artefakthandel bleibt im Kampagnen- und README-Regelblock verankert |
| #14 | Teamgrößen-Fehlertexte | ✅ Validator/Start/HUD-Strings auf 0–4 vereinheitlicht, Docs
| | | und Tests angepasst |
| #15 | Mission 5 Badge/SF-OFF Snapshot | ✅ QA-Runner `tools/test_acceptance_followups.js` prüft HUD/Flags gegen Golden File |
| #16 | QA-Fixture Save v6 voll | ✅ Fixture `internal/qa/fixtures/savegame_v6_full.json` dokumentiert |

## Maßnahmenpaket Agenten-Thriller-Ton 2026-02 (Issues #1–#9)

Der jüngste Playtest und das begleitende GPT-Memo zeigen Drifts im Ton: Core-Ops sollen wie
Infiltrations-/Agentenmissionen wirken, Rift-Ops wie Ermittlungsfälle (im Stil eines gritty
Tech-Noir-Procedurals, True Detective × X-Files, mit physischer Near-Future-Operative-Technologie
statt abstrakter System- oder Digitalraumästhetik), ohne „Digitalraum“-Eindruck. HUD-Mechanik
bleibt unverändert, aber die Interpretation und Generator-Outputs müssen nachgeschärft werden.
Alle Punkte sind abgeschlossen; der Abschnitt dient als referenzierte Belegspur für den
abgeschlossenen Tone-Shift.

| Issue | Kurzfassung | Fahrplan/Nächste Schritte |
| ----- | ------------------------------ | -------------------------------------------- |
| #1 | Physicality Gate erzwingen | ✅ Runtime erzwingt Hardware-Angaben (`require_scan_device/`
| | | `require_hack_device/must_comms`) + `HARDWARE`-Toasts; README/Toolkit/HUD-Spec spiegeln |
| #2 | Core vs. Rift Loop klarziehen | ✅ Runtime setzt Core=Episode, Rift=Casefile (`loop` + HUD
| | | `MODE RIFT · CASE … · STAGE …`), Launch bleibt HQ-only nach Episodenende |
| #3 | Core-Ziele diversifizieren | ✅ Briefings fordern Anchor + Auftragstyp (`protect|extract|`
| | | `neutralize|document|influence|prevent`), 60 % People/Influence-Fokus in README/Toolkit/Generator |
| #4 | Rift als Case Engine | ✅ Casefile-Tracker (Tatort→Leads→Boss) + HUD-Stage, 14er-Template und
| | | One-Weird-Thing-Guard dokumentiert; QA 20 Rifts prüfen bleibt als Hinweis |
| #5 | EntryChoice sichtbar machen | ✅ Szene 0/1 blendet `MODE CORE/RIFT · EntryChoice …` als HUD-Toast ein, Skip-Flag respektiert (Runtime + Docs aktualisiert) |
| #6 | Rift-Seed normalisieren | ✅ Normalizer erzwingt `id/label/status/seed_tier/hook`, füllt fehlende Felder aus Seed-Katalog; Launch setzt `active_seed_hook` |
| #7 | Welt-Beats als Standard | ✅ Fraktionsinterventionen loggen automatisch Briefing/Mid/Debrief nach `logs.fr_interventions[]` (mit Szene/Episode/Mission) |
| #8 | HUD als dünnes Overlay führen | ✅ HUD-Header zeigen `MODE CORE/RIFT` + `CASE <ID>: <Label> · HOOK …`; Entry-Toasts/Case-Hooks als Backtick-Overlay, HUD-Spec/Toolkit/README gespiegelt |
| #9 | One-Weird-Thing-Rule aktivieren | ✅ Runtime-Guard `register_anomaly()` (Core 0/Rift 1 +
| | | `WEIRD`-Toast); README/Toolkit/Generator spiegeln Budget 1 |

## Maßnahmenpaket Rift-/Casefile-Generatoren 2026-03 (Issues #1–#5)

Der Copy-Paste-Lauf zum Rift-/Casefile-Thema hat fünf zentrale Baustellen identifiziert. Sie zielen
auf klare Default-Ausgaben (echte Para-Kreaturen), einen kanonischen Seed-Katalog und konsistente
Persistenz. Alle Punkte sind abgeschlossen und werden über den Umsetzungsstand gespiegelt.

| Issue | Kurzfassung | Fahrplan/Nächste Schritte |
| ----- | ------------------------------ | -------------------------------------------- |
| #1 | Para-Creature-Generator auf Rift-Casefile-Default drehen | `gameplay/kreative-generatoren-`
| | | `begegnungen.md`: Abschnitt `#para-creature-generator` durch “Rift Casefile Edition” ersetzen,
| | | alte Urban-Myth-Edition als `#urban-myth-generator` auslagern; One-Weird-Thing (1 Zeiteffekt,
| | | 1 Anchor, 3–5 Tells, 1 Weakness) als Standard; optional `master-index.json` Pooltitel
| | | aktualisieren; QA: 10 Seeds, keine Tech-Falschspuren |
| #2 | Rift-Seed Catalogue kanonisch anlegen | `gameplay/kreative-generatoren-missionen.md` um
| | | neuen Abschnitt `#rift-seed-catalogue` erweitern (Casefile-Schema mit `rift_id/epoch/label/`
| | | `hook/briefing_public/leads/boss_private`), `RiftSeedTable`-Einträge 10/24 auf
| | | `Chrono Butcher`/`Jersey Devil` setzen, Deepsea-Seed in future/Arc verschieben; QA: 10 Seeds
| | | ziehen, Briefing max. 5 Bullets, Boss 1 Zeiteffekt |
| #3 | Rift-Casefile-Builder als Output-Template verankern | Unter dem neuen Catalogue einen
| | | “Rift-Casefile Builder”-Block einfügen (CASE, VISUAL HOOK, BRIEFING PUBLIC, OBJECTIVES,
| | | CASE OVERLAY, TRUTH, LEADS PRIVATE, BOSS PRIVATE; 14-Szenen-Map); QA: 3 Seeds (low/mid/high)
| | | als komplette Fallakte rendern |
| #4 | One-Weird-Thing-Guard als Default dokumentieren | Guard-Text in Para-Creature-Generator und
| | | Rift-Seed Catalogue ergänzen: keine zweite Anomalie, keine “es war nur Tech” in Rifts,
| | | Urban-Myth-Generator nur als Falschspur; QA: 5 Rift-Runs prüfen, dass nur 1 Weirdness aktiv |
| #5 | Rift-Seed-Persistenz erweitern | `systems/toolkit-gpt-spielleiter.md` (Makro
| | | `generate_rift_seeds()`): Seed-Objekt um `label/seed_tier/hook/time_marker` ergänzen,
| | | optional Load-Normalizer für Alt-Saves; QA: Save/Load mit 3 Seeds, HQ-Briefing zeigt
| | | vollständige Seed-Daten |

**Umsetzungsstand 2026-03**

- [x] Issue #1 Para-Creature-Generator auf Rift-Casefile-Default gedreht.
- [x] Issue #2 Rift-Seed Catalogue kanonisiert (Chrono Butcher + Jersey Devil, Deepsea verschoben).
- [x] Issue #3 Rift-Casefile-Builder mit 14-Szenen-Map und Output-Raster verankert.
- [x] Issue #4 One-Weird-Thing-Guard sichtbar in Generator und Catalogue dokumentiert.
- [x] Issue #5 Rift-Seed-Persistenz (`label/seed_tier/hook/time_marker`) in Toolkit-Makro
      umgesetzt.

## Maßnahmenpaket Tester-Playtest 2026-04 (Issues #1–#13)

Der erneute Durchlauf des Tester-Briefings (Acceptance 1–15, Mission 5 Badge-Check, HQ-Deepsave)
liefert 13 neue Findings. Der Fokus liegt auf stringstabilen Dispatcher-/SaveGuard-Texten,
Pflichtfeldern im Save-Schema, Boss-/Team-Clamps, Px-Reset-Timing, Chronopolis-Gating,
Arena-/Queue-States, UI-Enums, Cross-Mode-Konflikten, Offline-Guards, Output-Vertrag und einem
vollständigen v6-Fixture. Alle Punkte sind abgeschlossen; Abschnitt und Tabelle dokumentieren die
nachgewiesenen Fixes für Folgeaudits.

| Issue | Kurzfassung | Fahrplan/Nächste Schritte | Status |
| ----- | ------------------------------ | -------------------------------------------- | ------ |
| #1 | Acceptance-Smoke Dispatcher-Strings angleichen | QA-Briefing/Runner auf kanonische Fehlertexte (`npc-team 5`, `gruppe 3`) und Gruppen-Flow („2 Saves + 1 Rolle“ klar definieren) trimmen; Strings optional zentralisieren oder Tests auf contains/startsWith umstellen. | ✅ erledigt |
| #2 | SaveGuard-Pflichtfelder vs. Prompt | Pflichtcontainer-Liste (inkl. `logs.trace`, `logs.arena_psi`, `logs.flags.merge_conflicts`) im QA-Prompt spiegeln; optional `required_containers` aus Schema exportieren und Negativtest „fehlendes logs.trace“ ergänzen. | ✅ erledigt |
| #3 | SaveGuard-Texte vereinheitlichen | Kanonische Guard-Matrix (`SaveGuard: HQ-only/Exfil aktiv/Arena aktiv/SYS nicht voll installiert`) definieren und README/Save-Modul/Toolkit/Snapshots synchronisieren. | ✅ erledigt |
| #4 | Boss-DR & Teamgröße clampen | Teamgröße auf 0–4 hart clampen (Load/ArenaStart), DR-Tabelle >4 entfernen; Legacy-Saves loggen Migration/Conflict. HUD/Toolkit-DR-Else-Branch streichen. | ✅ erledigt |
| #5 | Px-Reset & Seed-Gating präzisieren | Terminologie „Episode“ durchgängig nutzen, Reset beim Debrief→HQ mit `px_reset_pending/confirm`; Seeds erst nach Episodenende spielbar, Reset-Flags und Logs setzen. | ✅ erledigt |
| #6 | Chronopolis-Gate vs. Pre-City | QA-Plan splitten: Frühphase testet Pre-City-Hub (Werkstatt/Archiv) ohne Vollstadt; ab Level 10 Chronopolis/Fraktionen. Toast/Log `chronopolis_unlock_level=10` ergänzen. | ✅ erledigt |
| #7 | Arena Queue-/Zone-State vertraglich fixen | `arena.queue_state` Enum (`idle|searching|matched|staging|active|completed`) + optional `arena.zone` (`safe|combat`) definieren; HUD/Logs/Save spiegeln, Acceptance-Check für Queue-Transitions + SaveGuard während `arena.phase=active`. | ✅ erledigt |
| #8 | UI-Enums konsolidieren | Kanonisches Set (`badge_density: standard|dense|compact`, `output_pace: normal|fast|slow`) festziehen; Legacy-Mappings dokumentieren und Serializer normalisieren. | ✅ erledigt |
| #9 | Cross-Mode-Import Konfliktlogging | Merge-Layer erzwingt `merge_conflicts` bei Abweichungen (`campaign.mode`, Seeds, UI, Arena-State); `logs.trace` Merge-Event; QA-Checkliste fordert sichtbare Konflikte + Arena-Reset-Beleg. | ✅ erledigt |
| #10 | Offline-Fallback Rate-Limit + SaveGuard | Acceptance um Rate-Limit (`!offline` <60 s) und Save-Sperre bis HQ-Resync erweitern; eigener SaveGuard-Reason + `logs.trace` (`save-blocked: offline`). | ✅ erledigt |
| #11 | QA-Output-Vertrag widerspruchsfrei | Output-Regel festlegen: JSON-Block entweder als Appendix oder als Evidenz in ISSUE; Runner/Parser tolerant machen, Copyblock-Version anheben. | ✅ erledigt |
| #12 | Offizielles v6-Fixture bereitstellen | Schema-konformes Save (Lvl 7/120/520, Seeds 1–25/80–150/400–1000, Pflichtcontainer inkl. `logs.trace`/`logs.arena_psi`/`merge_conflicts`) unter `internal/qa/fixtures/` versionieren; CI-Test „schema-validate + load_deep + summarize“ ergänzen. | ✅ erledigt |
| #13 | `economy.credits` Spiegel klären | Entscheiden, ob `economy.credits` als derived/optional Feld verbleibt oder konsolidiert wird; Loader synchronisiert `credits = cu` bei fehlendem Feld, QA testet Arena/Wallet-Split ohne Divergenz. | ✅ erledigt |

**Umsetzungsstand 2026-04**

- ✅ SaveGuard-Pflichtcontainer (inkl. `logs.trace`, `logs.arena_psi`,
  `logs.flags.merge_conflicts`) sind im README gespiegelt; der Serializer bricht
  bei fehlendem Trace-Block ab.
- ✅ Px-Reset bestätigt erst im Debrief→HQ den Rücksetzer (`px_reset_confirm`,
  Trace-Event `px_reset`, HUD-Toast) und hält Seeds bis Episodenende gesperrt.
- ✅ Chronopolis ist erst ab Level 10 freigeschaltet; Debrief/HQ-Flow schreibt
  einen Unlock-Toast plus Trace (`chronopolis_unlock_level`) und der QA-Plan
  trennt Pre-City-Hub-Checks von den Stadttests.
- ✅ Load-Merge protokolliert Konfliktfelder (`conflict_fields`/`conflicts_added`)
  inklusive Arena-Reset/Zone/Queue-State in `logs.trace.merge_conflicts`;
  `savegame_v6_full.json` trägt Queue-/Zone-Felder, Credits-Fallbacks und die
  Trace-Belege als Fixture-Nachweis.
- ✅ Acceptance-Smoke-Dispatcher nutzt kanonische Fehlertexte für `npc-team 5`
  und `gruppe 3`, Quickstart betont den Gruppen-Flow mit 2 Saves + 1 Rolle.
- ✅ SaveGuard-Matrix vereinheitlicht alle HQ-Blocker mit Suffix „– HQ-Save
  gesperrt.“ (Arena/HQ/Exfil/Offline, SYS- und Stress/Psi-Checks) in Runtime
  und Wissensmodulen.
- ✅ QA-Output-Vertrag erlaubt den Save-v6-JSON-Block entweder als ISSUE-
  Evidenz oder als Appendix; Runner/Parser akzeptieren beide Varianten.
- ✅ UI-/Runtime-Normalisierung klemmt Teamgrößen hart auf 0–4, mappt
  `badge_density/output_pace` auf kanonische Enums und spiegelt Queue-/Zonen-
  Felder im Arena-Block der Saves.
- ✅ Offline-Fallbacks sind gehärtet: `!offline` besitzt ein 60-Sekunden-Rate-
  Limit, SaveGuard blockiert HQ-Saves ohne Uplink und schreibt einen
  Trace-Eintrag.
- ✅ SaveGuard wertet Arena-Queue-States
  (`idle|searching|matched|staging|active|completed`) beim Serialisieren aus,
  leitet `active/phase` daraus ab und sperrt HQ-Saves während laufendem
  Matchmaking; Tests prüfen aktiv blockierte Saves.

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
- Abschlussstand 2025-12-12 im Audit/QA-Log vermerken (README/DOC/Speicher/Psi
  gespiegelt).
- Regressionstermine nach jedem Lauf hier und im QA-Log abhaken.
- Debrief-Auszugsprotokolle (`logs.market[]`, Foreshadow, Funk) weiterhin im
  QA-Log archivieren.

## Maßnahmenpaket Atmosphären-Feintuning 2026-05 (Issues #1–#7)

Der jüngste Playtest (Rift-Ops mit gekürztem Briefing) liefert sieben
Atmosphären- und Perspektiv-Regressionen. Fokus: Physicality-Guard,
Voice-Lock, Rift-Template, Core-Noir, Default-Mode, HUD-Schlankheit und
QA-Stylevertrag. Alle Punkte sind offen und müssen im Runtime-Overlay sowie in
den Wissensmodulen verankert werden.

| Issue | Kurzfassung | Fahrplan/Nächste Schritte | Status |
| ----- | ------------------------------ | -------------------------------------------- | ------ |
| #1 | Physicality Guard erzwingen | Physicality-Guard als Default (Hardware + Sinnesdetail); Banned-Terms-Lexikon in Toolkit/README, HUD-Usage-Log für QA. | ✅ erledigt |
| #2 | Voice-Lock auf dritte Person | `voice_profile = gm_third_person` als Standard; Start/Load normalisieren, Decision-Prompts ohne 2nd-Person-Narration. | ✅ erledigt |
| #3 | Rift-Template = Monster-Hunt | Rift-Generator auf 14-Szenen-Map trimmen (Tatort→Leads→Boss Szene 10, | ✅ erledigt |
| | | eine Anomalie, Foreshadows Szene 9); Seed-Felder `{hook,` | |
| | | atrocity_scene, signature, time_skill, weakness_hint, boss_arena}` | |
| | | erzwingen; HUD führt Stages; QA: 3 Seeds prüfen (Szene 1 Opferbild, | |
| | | Szene 9 zwei Foreshadows, Szene 10 Bosskontakt + DR-Toast). | |
| #4 | Core/HQ-Noir festziehen | Briefings setzen Anchor + Auftragstyp, HQ-Szenen führen Sinneseindruck/Fraktionsbeat; Toolkit/README betonen rationalen Noir. | ✅ erledigt |
| #5 | Default-Mode-Preset reaktivieren | `modes` stets `mission_focus` + `covert_ops_technoir`; Normalizer ergänzt Legacy, Noir-Preset vor Szene 0. | ✅ erledigt |
| #6 | HUD als dünne Schicht halten | HUD-Usage pro Szene (Limit 2, Ziel 80/20 Szene vs. HUD); Gate/FS/Boss-DR-Strings bleiben unverändert. | ✅ erledigt |
| #7 | QA-Runner mit Atmosphere Contract | Atmosphere-Contract (3rd person, Physicality Guard, Casefile-Rift, Core-Noir) in QA-Briefing/Runtime verankert; Contract-Block für QA-Runner. | ✅ erledigt |

**Umsetzungsstand 2026-05**

- ✅ Issue #3 (Rift-Template) umgesetzt: `resolve_scene_total`,
  `StartMission()` und `launch_mission()` setzen die Szenentotale strikt auf
  12 (Corelauft) bzw. 14 (Rift) und überschreiben Altwerte; Rift-Casefiles
  leiten Stages automatisch aus dem 14-Szenen-Raster (Sz 1–4 Tatort,
  5–10 Leads, 11–14 Boss) ab und synchronisieren Tatort/Leads/Boss bei
  Missionsstart und jedem HUD-Durchlauf. Toolkit/README spiegeln den
  Missionstyp-Reset und die Boss-/Foreshadow-Gates, Acceptance-Tests prüfen
  das 12-Szenen-Core-Overlay.
- ✅ Issue #1/#6 (Physicality/HUD): Physicality-Guard läuft default, Banned-Terms-
  Lexikon ist in Toolkit/README gespiegelt; Runtime loggt HUD-Usage pro Szene
  (Limit 2, Ziel 80/20 Szene vs. HUD) und hält Gate/FS/Boss-Strings unverändert.
- ✅ Issue #2/#7 (Voice/Atmosphere Contract): `voice_profile` wird beim Start/Load
  auf `gm_third_person` normalisiert; Atmosphere-Contract (3rd person,
  Physicality Guard, Casefile-Rift, Core-Noir) steckt im QA-Briefing und als
  Runtime-Contract-Block für QA-Runner.
- ✅ Issue #4 (Core/HQ-Noir): Briefings fordern Anchor + Auftragstyp, HQ-Szenen
  führen Sinneseindrücke/Fraktionsbeats; Toolkit/README betonen rationalen Noir
  statt Menüsprache oder Digitalraum-Formulierungen.
- ✅ Issue #5 (Mode-Preset): Start/Load setzen `modes` auf `mission_focus` +
  `covert_ops_technoir`, Normalizer ergänzt Legacy-Saves; Noir-Preset greift vor
  Szene 0, Speicher-Doku und Fixtures spiegeln das Feld.
- ✅ Atmosphere-Contract-Regressionstest deckt Start- und Load-Pfade ab,
  validiert HUD-Usage-Reset, Voice-Lock, Mode-Preset und Banned-Terms und läuft
  im npm-Pflichtpaket automatisch mit.
- ✅ HUD-Limit bleibt unverändert: Toast-Sperren wurden verworfen, das HUD
  bleibt bewusst schlank geführt (80 % Szene/20 % HUD) und zählt weiterhin
  die Einblendungen pro Szene nur zur QA-Beobachtung.

