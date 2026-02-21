---
title: "ZEITRISS QA-Fahrplan 2025"
version: 1.23.14
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

## Nachtrag 2027-03-24 – SSOT-Nachlauf 9 (HUD-Levelanker & Px-Kontextlogik)

Folgelauf auf UX-Motivationsfeedback: Das HUD soll das Charakterlevel dauerhaft
zeigen, während Paradoxon nur dann sichtbar ist, wenn es mechanisch relevant
ist.

- **Daueranker erweitert:** `Lvl` ist in Core/HUD als persistentes HUD-Element
  festgelegt.
- **Px-Anzeige geschärft:** `🌀` wird als kontextsensitives Signal geführt
  (Px-relevante Zustände, Resonanz/Backlash, ClusterCreate), nicht als
  Dauer-Icon.
- **SSOT-Mirror:** `core/spieler-handbuch.md`, `core/sl-referenz.md` und
  `characters/hud-system.md` auf dieselbe Icon- und Headerlogik synchronisiert.
- **Folgeschritt:** Historischer Icon-Audit bleibt offen, die aktive
  Runtime-Spezifikation ist konsistent.

## Nachtrag 2027-03-23 – SSOT-Nachlauf 8 (Paradoxon-Portal-Icon & TK-Entkopplung)

Nach Nutzerfeedback zur Symbolwirkung wurde das zentrale Paradoxon-Icon
gezielt als Portalmarker gesetzt.

- **Paradoxon-Icon:** `🌀` ist wieder das primäre Spieler-Signal für
  Px/Rift-Progress.
- **TK-Cooldown-Icon:** auf `✋` verschoben, um die Symbolrollen nicht zu
  vermischen.
- **Konsistenzpass:** Core/HUD/Gameplay/Toolkit/Zustände auf dieselbe
  Icon-Logik harmonisiert.
- **Folgeschritt:** historisierte QA-/Briefing-Beispiele auf Icon-Drift prüfen.

## Nachtrag 2027-03-22 – SSOT-Nachlauf 7 (Core-Meilensteine + Icon-Konsolidierung)

Anschlusslauf auf Basis der offenen Rückmeldung: nicht nur Quickformate,
sondern auch HUD-/Beispielmodule wurden auf dieselbe Symbol- und Gate-Logik
gezogen.

- **Chronopolis-Gate erweitert:** Core-Meilensteine nennen den Level-10-
  Schlüsselübergabepunkt jetzt explizit.
- **HUD-Symbolik konsolidiert:** Rift-Bonus überall als `☆`; `🌀` nicht mehr
  für Paradoxon verwendet.
- **Icon-Entzerrung fixiert:** `🌀` bleibt TK-Cooldown, `🔄` bleibt Paradoxon.
- **Folgeschritt:** dedizierter Icon-Audit-Pass für narrative Beispiele in
  weiteren Runtime-Modulen (Stil-/Sprachkonsistenz-Track).

## Nachtrag 2027-03-21 – SSOT-Nachlauf (Chronopolis-Key, Startrollentrennung, Stern-Notation)

Direkter Folgepass nach der Closure-Nachschärfung: gezielte Konsistenzkorrektur
für drei gemeldete Driftpunkte in den Core-Quickformaten.

- **Chronopolis-Zugangsanker:** Spieler-Handbuch nennt jetzt explizit die
  Schlüsselübergabe bei Level 10 als CITY-Gate.
- **Rollenabgrenzung Spielstart:** SL-Referenz führt nur Dispatcher-/Runtime-
  Invarianten; spielerseitige Eingabebeispiele bleiben im Handbuch.
- **Difficulty-Notation:** Rift-Bonusdarstellung wieder auf weiße Sterne (☆)
  vereinheitlicht (keine Blitz-Notation in den Quickformaten).
- **Folgeschritt:** Stil-/Sprachkonsistenz-Pass erweitert um repo-weiten
  Stern-/Symbolabgleich außerhalb der Core-Quickformate.

## Nachtrag 2027-03-20b – Closure-Nachschärfung (Runtime-Entkopplung von Setup-Hinweisen)

Direktes Follow-up nach Durchlauf 5: In den Core-Wissensmodulen verbliebene
Meta-/Wartungshinweise wurden entfernt, damit Laufzeit-Content und
Betriebsdokumentation klar getrennt bleiben.

- `core/sl-referenz.md`: Struktur-Abschnitt auf reine Regelmodul-Navigation
  reduziert; Verweise auf Wissensspeicher-Bestückung, `master-index.json` und
  Landingpage-Betrieb entfernt.
- `core/spieler-handbuch.md`: Wartungshinweis zur README-Mitsynchronisierung aus
  dem Runtime-Abschnitt gestrichen.
- Wirkung: Die Spielleitung erhält in Runtime-Slots nur noch
  regel-/szenenrelevante Inhalte; Setup bleibt in README/`docs/setup-guide.md`.

## Nachtrag 2027-03-20 – SSOT-Pipeline Durchlauf 5 (Konfliktprüfung & Closure)

Der fünfte Pipeline-Durchlauf ist abgeschlossen. Die Suchanker-Prüfung
(`optional`, `Pflicht`, `empfohlen`, `Rift`, `Belohnung`, `CU`, `Scaling`) wurde
gegen Core/README/Gameplay/Systems durchgeführt und der Restpunkt ist jetzt
formal geschlossen.

- **Konfliktfund aufgelöst:** Verbliebene Startwurf-Referenzen
  (`rift_artifact_variant=start_roll`) wurden in `core/sl-referenz.md` und
  `systems/toolkit-gpt-spielleiter.md` entfernt; Artefakt-Drops bleiben
  boss-only (Rift-Boss, Szene 10).
- **Kanonanker bestätigt:** CU-Formel, Px-5-`ClusterCreate()`, SaveGuard HQ-only
  und MUSS/SOLL/KANN sind weiterhin konsistent gespiegelt.
- **Closure-Gate erfüllt:** Restkatalog, Fahrplan, Audit und QA-Log wurden im
  selben Lauf synchronisiert; Pflichttestpaket vollständig grün.

Nächster Fokus: Restkatalog-Punkt 3 (Economy-/Scaling-Checkliste) und
Punkt 4 (Stil-/Sprachkonsistenz) weiterführen.

## Nachtrag 2027-03-19 – SSOT-Pipeline Durchlauf 4 (Systems-Pass)

Der vierte Pipeline-Durchlauf ist abgeschlossen. Die Systems-Module
`systems/currency/cu-waehrungssystem.md`,
`systems/gameflow/speicher-fortsetzung.md` und
`systems/toolkit-gpt-spielleiter.md` spiegeln den Core-Kanon jetzt explizit.

- **Normsprache gespiegelt:** In allen drei Zielmodulen sind SSOT-Anker mit
  MUSS/SOLL/KANN ergänzt, damit Pflicht- und Optionalitätslogik konsistent
  bleibt.
- **Belohnungsanker gespiegelt:** CU-Formel sowie Px-5-`ClusterCreate()` bleiben
  als systemweite Invarianten markiert; es gibt keine alternativen Triggerpfade.
- **Optionalitätsanker gespiegelt:** Komfortpfade (z. B. Filmmodus,
  Zusatz-Trace, QA-Felder) bleiben klar als KANN/optional gekennzeichnet.
- **Closure-Gate bleibt aktiv:** Restpunkt „Single-Source-of-Truth-Pass" bleibt
  bis zur Konfliktprüfung/Closure auf _in Umsetzung_.

Nächster Durchlauf: **Konfliktprüfung & Closure** gemäß Suchanker-Set
(`optional`, `Pflicht`, `empfohlen`, `Rift`, `Belohnung`, `CU`, `Scaling`).

## Nachtrag 2027-03-18 – SSOT-Pipeline Durchlauf 3a (Balance-Nachschärfung Artefakte)

Nach dem Gameplay-Pass wurde die Artefakt-Policy gezielt nachgeschärft, um
Balancing-Drift auszuschließen.

- **Boss-only fixiert:** Rift-Artefaktwürfe erfolgen wieder ausschließlich nach
  dem Rift-Boss in Szene 10.
- **Hausregel entfernt:** Die Startwurf-Variante
  (`rift_artifact_variant=start_roll`) ist aus den Gameplay-Regeln entfernt.
- **Balance-Anker geschärft:** Stoppuhr-Artefakte bleiben reine
  Plot-Schwachstellen und ersetzen den Boss-Drop nicht.

Nächster Durchlauf bleibt unverändert: **Systems-Pass** gemäß Modulreihenfolge.

## Nachtrag 2027-03-18 – SSOT-Pipeline Durchlauf 3 (Gameplay-Pass)

Der dritte Pipeline-Durchlauf ist abgeschlossen. Die Gameplay-Module
`gameplay/kampagnenuebersicht.md` und `gameplay/kampagnenstruktur.md` spiegeln
den Core-Kanon jetzt explizit.

- **Optionalitätsanker gespiegelt:** Quickstart ist als optionaler
  Zugriffspfad markiert und ändert keine Kernregeln.
- **Belohnungsanker gespiegelt:** Der Gameplay-Loop führt Px weiter als
  Belohnungssystem mit `ClusterCreate()` bei Px 5.
- **Normsprache gespiegelt:** Im Core-/Rift-Loop sind MUSS/SOLL/KANN als
  semantische Leitlinie für Invarianten, Standardpfad und Varianten ergänzt.
- **Closure-Gate bleibt aktiv:** Restpunkt „Single-Source-of-Truth-Pass" bleibt
  bis nach Systems-Pass plus Konfliktprüfung auf _in Umsetzung_.

Nächster Durchlauf: **Systems-Pass** gemäß Modulreihenfolge
(`systems/currency/cu-waehrungssystem.md`,
`systems/gameflow/speicher-fortsetzung.md`,
`systems/toolkit-gpt-spielleiter.md`).

## Nachtrag 2027-03-17 – SSOT-Pipeline Durchlauf 2 (Anker-Sync README/Core)

Der zweite Pipeline-Durchlauf ist abgeschlossen. README-Begriffe und Prioritäten
folgen jetzt explizit dem Kanon aus `core/sl-referenz.md` und
`core/spieler-handbuch.md`.

- **Belohnungsanker gespiegelt:** README nennt Px weiterhin als
  Belohnungssystem, `ClusterCreate()` bei Px 5 und die identische CU-Formel für
  Core und Rift (`Basiswert × Ergebnis × Seed-Multi × Hazard-Pay`).
- **Optionalitätsanker geschärft:** Schnellstart bleibt explizit optionaler
  Zugriffspfad; Kernregeln bleiben unverändert bindend.
- **Normsprache gespiegelt:** README führt Muss/Soll/Kann als Redaktionsanker
  (MUSS = Invariant, SOLL = Standardpfad, KANN = Komfortvariante).
- **Closure-Gate bleibt aktiv:** Restpunkt „Single-Source-of-Truth-Pass" bleibt
  bis nach Gameplay- und Systems-Pass auf _in Umsetzung_.

Nächster Durchlauf: **Gameplay-Pass** gemäß Modulreihenfolge
(`gameplay/kampagnenuebersicht.md`, `gameplay/kampagnenstruktur.md`).

## Nachtrag 2027-03-16 – SSOT-Pipeline Durchlauf 1 (Kanon-Extraktion)

Der erste Pipeline-Durchlauf ist abgeschlossen und extrahiert den kanonischen
Anker für die Folgeschritte aus `core/sl-referenz.md` und
`core/spieler-handbuch.md`.

- **Kernkanon Belohnung/Rift:** Px bleibt Belohnungssystem; Px 5 erzeugt via
  `ClusterCreate()` 1-2 Rift-Seeds. Die CU-Formel gilt identisch für Core und
  Rift (`Basiswert × Ergebnis × Seed-Multi × Hazard-Pay`).
- **Semantikanker Optionalität:** Optional bedeutet ergänzender Pfad ohne
  Änderung der Kerninvarianten (Boss-Timing, SaveGuard HQ-only, Debrief/HQ-
  Flow).
- **Normsprache für Folgeläufe:** Muss/Soll/Kann als verbindliche
  Redaktionslogik eingeführt (MUSS = invariant, SOLL = Standardpfad,
  KANN = Komfortvariante ohne Regeländerung).
- **Closure-Gate bleibt aktiv:** Restpunkt „Single-Source-of-Truth-Pass" bleibt
  bis nach README/Core-Sync + Gameplay- und Systems-Pass auf _in Umsetzung_.

Nächster Durchlauf: **Anker-Sync README/Core** gemäß extrahiertem Glossar.

## Nachtrag 2027-03-08 – Seed-Caps & Intro-Wording

- **#A1 – Rift-Skalierung deckeln** ✅ abgeschlossen.
  `sg_bonus` ist jetzt auf +3 gedeckelt; `cu_multi` auf 1,6.
  Referenzen: `gameplay/kampagnenstruktur.md`,
  `systems/gameflow/speicher-fortsetzung.md`,
  `systems/toolkit-gpt-spielleiter.md`.
- **#A2 – Core-Einführung korrigieren** ✅ abgeschlossen.
  Epochen-Hinweis von „jede Mission“ auf „jede Episode“ umgestellt.
  Referenz: `core/zeitriss-core.md`.

## Nachtrag 2027-03-09 – Tiefenanalyse-Mirror: Runtime-Pseudocode-Policy & Inventur

Kontext: Umsetzung der Tiefenanalyse aus `uploads/tiefenanalyse-regelwerk-und-onboarding.md` mit
Fokus auf konsistente Wissensmodule ohne auswertbare Template-Delimiters im Runtime-Content.

### Verbindliche Policy (ab sofort)

- **Pseudocode bleibt Pflicht** in Runtime-Wissensmodulen, wenn er Runtime-/Tool-Logik spiegelt.
- **Template-Syntax `{{ ... }}` / `{% ... %}` ist in Runtime-Wissensmodulen unzulässig**, weil
  Plattformen Fragmente als ausführbare Template-Logik interpretieren können.
- Runtime-Module enthalten stattdessen **template-neutrale Formen**:
  - Regeltext (normativ),
  - Schrittlisten/Flows,
  - JSON-/YAML-Beispiele,
  - nicht-ausführbare Funktionssignaturen in Klartext.
- Engine-nahe Implementierungsdetails bleiben in `runtime.js`, `tools/`, `scripts/` oder
  internen Dev-Dokumenten (`docs/dev/`, `internal/`).

### Umsetzungsplan (Tiefenanalyse-Paket A)

1. **Inventur**
   - Runtime-Pfade (`core/`, `characters/`, `gameplay/`, `systems/`) nach `{{`/`{%` durchsuchen.
   - Pro Fundstelle markieren: _neutral umschreiben_ vs. _in Dev/Tooling auslagern_.
2. **Migration**
   - Regel-/Spielwirkung im Runtime-Modul behalten (Mirror-Pflicht).
   - Template-Delimiters entfernen und in robuste, lesbare Pseudocode-Form überführen.
3. **Synchronisierung**
   - Bei Strukturänderungen README-Dokumentenlandkarte, `master-index.json` und Toolkit-Verweise
     mitpflegen.
4. **QA-Dokumentation**
   - Jede Session mit Befehlen, Ergebnis und Rest-Risiken im QA-Log dokumentieren.

### Priorisierter Backlog für Folgeläufe

- **T1 (hoch):** Runtime-Template-Inventur komplettieren und in QA-Log als Checkliste ablegen.
- **T2 (hoch):** `characters/hud-system.md` Macro-Blöcke in template-neutrale Runtime-Spezifikation
  umformen; Engine-Details in Tooling/Dev referenzieren.
- **T3 (hoch):** `gameplay/kreative-generatoren-begegnungen.md` ausführbare Macro-Snippets
  in regelhafte Generatorbeschreibung + Beispielausgaben überführen.
- **T4 (mittel):** `systems/toolkit-gpt-spielleiter.md` Template-Fragmente auf Runtime-Relevanz
  prüfen und nur die normative, modellunabhängige Darstellung im Wissensslot belassen.
- **T5 (mittel):** Versionsdrift 4.2.6/4.2.7 in separatem Paket harmonisieren (kein Mischstand
  zwischen Frontmatter und Lauftext).

### Definition „zulässig / unzulässig“ (Kurzbeispiele)

- ✅ Zulässig: `Wenn Px == 5: ClusterCreate auslösen, Index auf 0 setzen.`
- ✅ Zulässig: JSON-Beispiel `{ "px": 5, "clustercreate": true }`.
- ❌ Unzulässig im Runtime-Slot: `{% if campaign.px == 5 %}...{% endif %}`.
- ❌ Unzulässig im Runtime-Slot: `{{ hud_tag('Px 5/5') }}`.

Referenzbeleg: QA-Log-Eintrag **2027-03-09 – Repo-Agent – Tiefenanalyse-Fortsetzung**.


## Nachtrag 2027-03-10 – Lauf 1: Runtime-Neutralisierung umgesetzt

Umsetzungsfokus dieses Laufs: T1–T3 in priorisierten Runtime-Dateien ausgeführt
(ohne Runtime-Code-/Tooling-Änderungen).

- **T1 (hoch):** Inventur erneut ausgeführt und Spot-Fixes in den identifizierten
  Kernmodulen vorgenommen (`characters/`, `gameplay/`, `core/`, `systems/`).
- **T2 (hoch):** `characters/hud-system.md` Macro-Block in klare
  Anzeige-Spezifikation (ASCII vs. Standard-Ansicht) überführt.
- **T3 (hoch):** `gameplay/kreative-generatoren-begegnungen.md`
  Macro-Snippets in template-neutrale Ablaufbeschreibungen (`rand_event`,
  `roll_legendary`) migriert.
- **Zusätzliche Neutralisierung:** `{{SG_AUTO}}`-Platzhalter sowie
  Template-Beispiele in `gameplay/kampagnenstruktur.md`,
  `gameplay/kreative-generatoren-missionen.md`, `systems/kp-kraefte-psi.md` und
  `core/sl-referenz.md` auf runtime-neutrale Formulierungen umgestellt.

**Offen für Folgeläufe**
- **T4 (mittel):** in Lauf 2 umgesetzt (Template-Delimiter im Toolkit auf
  template-neutrale Pseudocode-Notation umgestellt).
- **T5 (mittel):** in Lauf 2 umgesetzt (Versionsharmonisierung in
  `docs/setup-guide.md` auf 4.2.6).

## Nachtrag 2027-03-10 – Lauf 2: Toolkit-Entzerrung (T4) & Versionsharmonisierung (T5)

Umsetzungsfokus dieses Laufs: Abschluss der offenen Punkte T4 und T5 aus dem
Tiefenanalyse-Backlog.

- **T4 (mittel):** `systems/toolkit-gpt-spielleiter.md` vollständig von
  auswertbaren Delimitern bereinigt (`{{ ... }}` / `{% ... %}` / `{# ... #}` →
  template-neutrale Pseudocode-Klammernotation).
- **T5 (mittel):** `docs/setup-guide.md` auf konsistente Versionsführung 4.2.6
  harmonisiert (Frontmatter + Lauftext).
- **Mirror-Status:** Keine Runtime-JS-/Tooling-Änderung; Lauf betrifft
  Wissensmodule + Meta-Dokumentation.

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
| 2027-03-08 | Bug-/Optimierungscheck, Pflichtpaket grün | QA-Log 2027-03-08 |
| 2026-01-14 | Beta-GPT Playtest 2026-01-14 übernommen | QA-Log 2026-01-14 |
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
| 2025-10-28 | Beta-GPT 10-28 Deltas dokumentiert | QA-Log 2025-10-28; Paket 2025-10-28 |
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
| 2025-12-22 | Pflichtprüfungen vollständig grün | Repo-Checks (make lint/test, smoke, Linter) |

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
- [x] Restliche Module unter `systems/gameflow/` auf Zeilenlängen, Listen- und
      Absatzumbrüche prüfen (Formatierungs-Review nach
      `systems/gameflow/speicher-fortsetzung.md` und
      `systems/gameflow/cinematic-start.md`).
  - [x] Wissensmodule erneut auf QA-Aufträge oder Smoke-Listen prüfen und bei
        Treffern in das Tester-Briefing
        (`docs/qa/tester-playtest-briefing.md`) auslagern; Mirror und ggf. offene
        Deltas im QA-Log dokumentieren.

### Offene Formatierungs-Tasks (Zeilenlänge ≤ 100)

- [x] `characters/hud-system.md` auf Tabellen- und Fließtext-Umbrüche geprüft
      und unter die 100-Zeichen-Vorgabe gebracht.
- [x] `characters/charaktererschaffung-optionen.md` mit Spezies-Tabelle und
      Archetypen-Bullets neu umbrechen.
- [x] `characters/zustaende.md` (Zustandsbeschreibungen, Px/PP-Tabellen) an die
      Zeilenlängenvorgabe anpassen.
- [x] QA-/Log-Dokumente unter `internal/qa/` aufbreite Tabellen prüfen und
      kürzen.
- [x] Skripte (`scripts/`) auf überlange Strings/Kommentare prüfen und
      umbrechen.
- [x] `runtime.js` auf überlange Strings/Kommentare kontrolliert und
      vollständig unter die Vorgabe gebracht (Rest-Umbrüche nachgezogen).

### Lore & Px-Klarstellungen

- [x] Lore-Module (u.a. `systems/gameflow/cinematic-start.md`,
      `core/wuerfelmechanik.md`, `systems/kp-kraefte-psi.md`) auf Px-Resonanz-
      Framing und Missionsfreiheit prüfen und vereinheitlichen.
- [x] Briefing-/HUD-Texte angleichen, damit das Hauptereignis einer Mission im
      bekannten Verlauf bleibt und robuste Methoden explizit erlaubt sind, wenn
      die Zeitlinie stabil bleibt.

## Maßnahmen – Wissensspeicher 20-Slot-Optimierung (Entwurf 2025-12-28)

**Zielbild:** Retrieval-Leistung der Wissensmodule erhöhen, indem sehr kurze Module
thematisch konsolidiert und sehr lange Module in klar getrennte Teilmodule
aufgespalten werden. Die Umstellung soll keine Verschlimmbesserung erzeugen und
inklusive Querverweisen, Index- und QA-Sync erfolgen.

### Phase 1 – Konsolidierung kurzer Module (Slots freimachen)

1. **Cyberware bündeln**
   - Quelle: `characters/ausruestung-cyberware.md` (integriert)
   - Ziel: `characters/ausruestung-cyberware.md`
   - Leitplanken: Einleitung + Regeln + Bioware-Sektionen übernehmen; bestehende
     Legalitäts-/Wartungsanker (`#legalitäts--wartungs-stufen`) stabil halten oder
     sauber migrieren.
2. **Psi bündeln**
   - Quelle: `systems/kp-kraefte-psi.md` (integriert)
   - Ziel: `systems/kp-kraefte-psi.md`
   - Leitplanken: Talentlisten direkt hinter Kernmechanik platzieren; Anker wie
     `#mentale-maskierung` prüfen und bei Bedarf weiterleiten.

**Ergebnis Phase 1:** Zwei Slots werden freigemacht, ohne thematische
Fragmentierung zu erzeugen.

### Phase 2 – Split langer Module (Retrieval-Klarheit)

1. **Modul 5 (Zustände/HUD) aufspalten (✅ erledigt)**
   - Teil A: Zustände/Statusregeln → `characters/zustaende.md`
   - Teil B: HUD-/Interface-System → `characters/hud-system.md`
2. **Modul 3 (Charaktererschaffung) aufspalten (✅ erledigt)**
   - Teil A: Erschaffungsschritte & Basiswerte →
     `characters/charaktererschaffung-grundlagen.md`
   - Teil B: Optionen/Module/Sonderregeln →
     `characters/charaktererschaffung-optionen.md`

**Ergebnis Phase 2:** Lange Module werden in semantisch saubere Teile zerlegt,
ohne Querbezüge zu verlieren.

### Review 2027-03-09 – Phase 1–2 Konsolidierungscheck

- `characters/ausruestung-cyberware.md`: **beibehalten** (keine sichere Kürzung ohne
  Regelverlust).
- `systems/kp-kraefte-psi.md`: **beibehalten** (keine redundanten Regelblöcke).
- `characters/zustaende.md` + `characters/hud-system.md`: **beibehalten** (Split bleibt
  retrieval-klar).
- `characters/charaktererschaffung-grundlagen.md` +
  `characters/charaktererschaffung-optionen.md`: **beibehalten** (Trennung reduziert
  Komplexität).

### Phase 3 – Sync & QA

- **Querverweise aktualisieren:** alle Links/Anker in Runtime-Modulen, README und
  `master-index.json` prüfen und anpassen.
- **Wissensspiegel sichern:** falls Runtime-Änderungen betroffen sind, Spiegel in
  README/Runtime-Markdowns/Toolkit-Makros dokumentieren.
- **QA-Log ergänzen:** Befehle + Ergebnisse je Schritt im QA-Log erfassen.
- **Pflicht-Testpaket ausführen:** siehe `CONTRIBUTING.md#verpflichtende-pruefungen`.

**Status:** ✅ abgeschlossen (QA-Log 2026-11-03, Audit-Update 2026-11-03).

## Maßnahmenübersicht Beta-GPT 2025-06 (Issues #1–#16)

**Referenzkürzel**

`R` = README.md (Abschnittskürzel in Klammern, z. B. `R(QA)` → README §QA-Checks 2025-06-27)  
`RT` = runtime.js  
`M12` = systems/gameflow/speicher-fortsetzung.md  
`TK(16)` = systems/toolkit-gpt-spielleiter.md – Modul 16  
`TK(11)` = systems/toolkit-gpt-spielleiter.md – Modul 11  
`HUD` = characters/hud-system.md  
`DOC` = doc.md  
`BRF` = docs/qa/tester-playtest-briefing.md
`CW` = systems/currency/cu-waehrungssystem.md

## Maßnahmenpaket Beta-GPT 2025-12 (Copy-Paste-QA)

Die folgenden Punkte stammen aus dem Copy-Paste-Testlauf (Acceptance 1–15, Save v6) und sind für
den nächsten Umsetzungszyklus einzuplanen. Sie sind priorisiert nach Impact auf Release-Qualität.

### 1. Boss-Gate-Mission 5/10 entkoppeln (Gate fix 2/2, FS separat) (✅ erledigt)

- HUD-Spec `HUD` auf `GATE 2/2 · FS 0/4` zum Missionsstart M5/M10 umstellen, Gate nicht mehr an
  Foreshadow-Counts koppeln.
- Toolkit `TK(16)` (Foreshadow, Suggest & Arena) spiegeln: Gate-Status fix, Foreshadows erhöhen
  nur `FS`.
- Runtime (`RT` → `StartMission()`, `scene_overlay()`) prüfen und falls nötig Gate-Status auf den
  festen Startwert setzen; Boss-Toast/Flags synchronisieren.
- QA: Mission-5-Badge-Check (Prüfnummern 11–12) in Solo/NPC/Koop/Arena erneut laufen lassen.

### 2. `phase`-Feld konsolidieren (technisch lowercase) (✅ erledigt)

- README-Beispiele und Seeds auf `phase: core|transfer|rift` (lowercase) angleichen; Flavor-Groß-
  schreibung aus YAML entfernen.
- Speicher-Doku `M12` ergänzen: HQ-Save immer `phase: core`; Missionslaufzeit steuert
  `campaign.type/scene`.
- Toolkit-Hinweis in `TK(11)`/`TK(16)`: `phase` wird zur Laufzeit gesetzt, Seeds tragen nur den
  Missions-Typ.
- QA: Cross-Mode-Smoke (Solo → Koop → PvP) sicherstellen, dass `phase` konstant bleibt.

### 3. Rift-Seeds mit optionalen Seed-Tiers ergänzen (✅ erledigt)

- Kampagnenstruktur `gameplay/kampagnenstruktur.md` um Hinweise zu optionalen
  Seed-Tiers (Early/Mid/Late) erweitern – ohne Level-Gating, freier Zugriff ab
  Level 1; Beispiel-Seeds nennen und Arc-Dashboard-Spiegel zeigen.
- Optionales Feld `seed_tier` in Arc-Dashboard beschreiben; Seed-Beispiele und
  Save-Schema aktualisieren.
- QA: Drei Rifts fahren (Level 8 / 120 / 500+) und Seed-Zuordnung dokumentieren
  – nur als Balancing-Hinweis, nicht als Sperre.

### 4. Arena-Phase-Strike-Logs von Psi-Heat trennen (✅ erledigt)

- Entscheidung fixieren: neues Feld `logs.arena_psi[]` **oder** verpflichtendes Tagging
  (`category: arena|psi`, `heat_delta` vs. `sys_cost`). Schema in `M12` ergänzen.
- Toolkit-Logger (`phase_strike_cost`/`log_phase_strike_event`) anpassen; README/Psi-Modul um
  QA-Hinweise ergänzen.
- QA: Acceptance 13 erneut (Psi-Heat + Arena-Strike) mit Filterkriterien prüfen.

### 5. Accessibility-Felder robust spiegeln (✅ erledigt)

- Speicher-Doku `M12` klarstellen: `contrast`/`badge_density`/`output_pace` optional, Defaults
  greifen bei fehlenden Feldern; SaveGuard prüft den normalisierten UI-Block.
- README-Beispiel anpassen und Default-Logik der Migration/Serializer spiegeln.
- QA: Save ohne Accessibility-Felder laden, `!accessibility` auf Standardwerte prüfen.

### 6. Save-Beispiele für High-Level-/Rift-Play ergänzen (✅ erledigt)

- Speicher-Doku um Abschnitt „High-Level-Progression (100–1000)“ erweitern und Referenz-Testsave
  (Lvl 8/120/520 mit Seeds 1–25/80–150/400–1000) verlinken.
- QA-Log/Audit auf neuen Testspeicherstand verweisen; Archivierung unter `internal/qa/fixtures`
  prüfen.

### 7. Gear-Armbänder zulassen (✅ erledigt)

- Runtime-Gear-Alias entfernt; Armbänder sind reguläres Gear ohne
  Normalisierung.
- QA-Check zu Armband-Loadouts entfällt (Thema obsolet, bleibt nur in den Alt-Protokollen).

### 8. Offline/Ask→Suggest/Alias/Squad-Radio als stabil vermerken (✅ erledigt)

- QA-Abschnitt (README oder QA-Handbuch) um Kurznotiz ergänzen: Ask→Suggest, Offline-FAQ,
  Alias-/Squad-Radio-Logs Smoke bestanden in Solo/NPC/Koop/PvP.
- QA-Log aktualisieren, Status als Referenz für Regressionen markieren.

### 9. Dispatcher-Smoke 0–4 als Referenzstatus halten (✅ erledigt)

- Optional Mini-Tabelle im QA-Kapitel anlegen („Dispatcher-Smoke 0–4 bestanden“), damit künftige
  Änderungen die Basislinie kennen.
- QA: Bei Dispatcher-Änderungen Acceptance 0–4 erneut durchlaufen lassen.
`GM` = gameplay/kreative-generatoren-missionen.md
`SR` = internal/runtime/runtime-stub-routing-layer.md
`PSI` = systems/kp-kraefte-psi.md
`VEH` = gameplay/fahrzeuge-konflikte.md
`MASS` = gameplay/massenkonflikte.md

## Maßnahmenpaket Copy-Paste-QA 2025-12 (Issues #1–#14)

Der Copy-Paste-Lauf (Acceptance 1–15, Save v6, QA-Runner) ist vollständig
abgeglichen. Die folgenden Punkte fassen den aktuellen Zustand zusammen und
halten die nächsten Schritte für Folge-Läufe fest.

| Issue | Kurzfassung | Fahrplan/Nächste Schritte | Status |
| ----- | ------------------------------ | -------------------------------------------- | ------ |
| #1 | Paradoxon-Intro invertiert | Einleitungstext korrigieren: Px steigt nur bei sauberer Stabilisierung; hartes Eingreifen lässt Px stagnieren oder sinken. QA: Einleitung/Start-Text gegen README spiegeln. | ✅ erledigt |
| #2 | Doppelte Zeile in Acceptance #6 | Duplicate in `docs/qa/tester-playtest-briefing.md` und `doc.md` entfernt; QA-Parser bleibt auf kanonische Fehltexte aus Runtime/Toolkit ausgerichtet. | ✅ erledigt |
| #3 | `arc_dashboard` optional vs. Pflichtcontainer | Speicherdoku/README/QA-Briefing harmonisiert; Save-Preview immer mit `arc_dashboard`. QA: Cross-Mode-Import mit Pflichtcontainer prüfen. | ✅ erledigt |
| #4 | Armbänder erlaubt, keine Normalisierung | Gear-Alias entfernen, Armbänder zulassen; Runtime + README + HUD + Toolkit + Speicher-Doku synchronisieren. QA-Check auf Armband-Loadouts entfällt (Thema abgeschlossen). | ✅ erledigt |
| #5 | `seed_source` (trigger vs. trigger_pool) | Toolkit auf `seed_source = preserve|trigger` gespiegelt, Fixture angepasst; Pools bleiben `preserve_pool`/`trigger_pool`. | ✅ erledigt |
| #6 | Boss-Gate/DR-Logs | PASS; optional `logs.trace[].boss` standardisieren (Typ/DR) für Snapshot-Stabilität. QA: Mission 5 Abschluss/Abbruch prüfen. | ✅ pass |
| #7 | Ask↔Suggest | PASS; Overlay-Parser akzeptiert `· SUG` als optionales Suffix. QA: `SUG-ON/OFF` Toasts prüfen. | ✅ pass |
| #8 | Psi-Heat vs. Px-Reset | Psi-Module/README klären: Arena-Fails resetten `campaign.px` nicht; Px-Reset folgt nur nach Px 5 + Debrief/HQ. | ✅ erledigt |
| #9 | Accessibility Legacy-Mapping | PASS; QA erweitert um Legacy-Import (`full|minimal`, `rapid|quick`). | ✅ pass |
| #10 | Offline-Fallback | PASS; Rate-Limit & SaveGuard behalten. Optionaler Hinweis „Mission läuft weiter“. | ✅ pass |
| #11 | Vehikel-/Massenkonflikt-Logs | PASS; strukturierte `logs.hud[]`-Events als Pflichtlog prüfen. | ✅ pass |
| #12 | Chronopolis/Economy-Audit | PASS; `economy_audit`-Trace bei HQ-Save standardisiert. | ✅ erledigt |
| #13 | Rift-Boss-Szenenindex | Generator-Map auf Boss-Encounter Szene 10 + Resolution Szene 11–14 harmonisiert. QA: Golden-Files updaten. | ✅ erledigt |
| #14 | Test-Save v6 Fixture | Fixture `savegame_v6_test.json` aktualisiert (Seed-Source konsistent). | ✅ erledigt |

README-Abschnittskürzel:  
`R(QA)` = README §QA-Checks 2025-06-27  
`R(RT)` = README §Runtime-Helper  
`R(Schnell)` = README §Schnellstart & QA-Checks  
`R(Flags)` = README §§Runtime-Flags & Offline-Protokoll  
`R(Koop)` = README §Koop-Ökonomie  
`R(Start)` = README §Spielstart  
`R(Chrono)` = README §ITI-HQ & Chronopolis  
`R(Chat)` = README §Chat-Kurzbefehle

## Maßnahmenpaket Tester-Playtest 2025-12-18 (Issues #1–#12)

Der aktuelle Playtest (Tester-Briefing + eigener Lauf) liefert neue Findings zu
Dispatcher-Strings, Save-Containern, Mission‑5‑Badges, Arena/Psi-Logs,
Sonder-Overlays, Atmosphere-Contract-Capture, Economy-Brücke, QA-Fixtures sowie
zwei Flow-Regressionen im HQ/Charakter-Setup. Zusätzlich ist eine
Stilabweichung („Handgelenk“-Regel) aufgefallen, die als neues Issue geführt
wird. Die folgenden Punkte sind offen und müssen in den nächsten Zyklen
abgearbeitet werden.

1. **Issue #1 – Dispatcher-Fehlertext `gruppe 3` zu kurz (✅ erledigt)**  
   Dispatcher-String auf „Bei gruppe keine Zahl angeben. (klassisch/schnell
   sind erlaubt)“ harmonisiert; Snapshot-Quellen synchronisiert.
2. **Issue #2 – Save-Container/Parser-Vollständigkeit (✅ erledigt)**  
   QA-Parser/Fixtures um Pflichtcontainer `logs.trace[]` und
   `logs.arena_psi[]` ergänzt; Test-Save/Briefing-Listen spiegeln die Container,
   Negativtest für fehlendes `logs.arena_psi` ergänzt.
3. **Issue #3 – Mission-5-Badge-Snapshot nach Load (✅ erledigt)**  
   Mission‑5‑HUD und Auto‑Reset‑Flags werden im Save/Load geprüft; Acceptance‑Check
   validiert Gate/SF/Boss‑Toast sowie `self_reflection_auto_reset_*` nach Load.
4. **Issue #4 – Arena-Psi-Logs & SaveGuard-Regeln (✅ erledigt)**  
   `logs.arena_psi[]` stets vorhanden; SaveGuard blockt bei `arena.active`
   oder `queue_state != idle`; Arena-Flow (Start → Phase-Strike → Save → HQ)
   erneut prüfen.
5. **Issue #5 – Sonder-Overlays strukturiert loggen (✅ erledigt)**  
   `vehicle_clash` und `mass_conflict` als strukturierte `logs.hud[]`-Events
   ergänzt (Tempo/Stress/Schaden/Chaos/Break-SG); HUD-Parser normalisiert
   strukturierte Einträge für Save/Load.
6. **Issue #6 – Atmosphere-Contract Capture (QA-only) (✅ erledigt)**  
   Optionales QA-Flag `logs.flags.atmosphere_contract_capture` eingeführt,
   speichert 8–12-Zeiler pro Phase inkl. PASS/FAIL für Banned-Terms und
   HUD-Toast-Zählung; Fixture und Wissensmodule gespiegelt.
7. **Issue #7 – Economy-Scaling-Brücke dokumentieren (✅ erledigt)**  
   `cu_waehrungssystem.md` um Brücke „Rewards → Wallet-Richtwerte 400+“
   ergänzt; High-Tier-Sinks/Chronopolis-Preisanker dokumentiert; QA-Pfad für
   Lvl 120/512/900+ ergänzt.
8. **Issue #8 – QA-Fixture „Gold Save“ aktualisieren (✅ erledigt)**  
   Vollständigen Save-Block als Fixture fixiert; QA-Referenz enthält den
   erweiterten Flags-Block inkl. Atmosphere-Contract.
9. **Issue #9 – Szene-Counter in Charaktererstellung (✅ erledigt)**  
   Szene-Anzeige bleibt im HQ (inkl. Charaktererstellung) aus; Scene-Overlay
   erscheint nur in Missionen/Rifts.
10. **Issue #10 – Einleitung endet sporadisch zu früh (✅ erledigt)**  
   HQ-Kurzintro um die Schlusszeile ergänzt und im Start-Flow gespiegelt.
11. **Issue #11 – „Handgelenk“-Regel entfernen (✅ erledigt)**  
   Handgelenk-Projektionen als Legacy markiert; Hardware-Anker bleiben
   (Linse/Terminal/Kabel), kein Handgelenk-Default.
12. **Issue #12 – Arena-SceneCounter/HUD-Overlay prüfen (✅ erledigt)**  
   Arena zeigt keinen Szenenzähler; `scene_overlay()` rendert ausschließlich
   bei `location='FIELD'`. Entscheidung in README/Toolkit/Speicher-Modul
   gespiegelt und Runtime angepasst.

**Hinweise zum Playtest-Output**

- HQ‑Import aus v6‑Save zeigt korrektes Overlay (`EP/MS/SC`) und Rift‑Seeds,
  Szene‑Anzeige in der Charaktererstellung bleibt unterdrückt
  (umgesetzt in Issue #9: HQ‑Labor ≠ Mission).
- Der Handgelenk‑Verweis („Multi‑Tool‑Handschuh am Handgelenk“) ist eine
  Altregel aus früheren Outputs und widerspricht dem Retinal‑HUD‑Prinzip
  (umgesetzt in Issue #11: in Toolkit/README korrigiert).

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
Alle Punkte sind umgesetzt und im Wissensspiegel verankert.

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
| #1 | Acceptance-Smoke-Checkliste als Runtime-Mirror ergänzen | ✅ | R(QA); BRF; DOC |
| #2 | Self-Reflection: Truth-Source `character.self_reflection` | ✅ | HUD; RT; M12 |
| #3 | Boss-Gate/Foreshadow Terminologie & Reset-Zeitpunkte | ✅ | HUD; TK(16); R(QA) |
| #4 | Cross-Mode Währungs-Sync (Solo→Koop→Arena) | ✅ | M12; R(Koop); CW |
| #5 | Arena-Psi-Regeln (Phase-Strike, Tax, Buffer) bündeln | ✅ | PSI; TK(16); RT |
| #6 | Fahrzeug-/Massenkonflikt-Regeln im Smoke-Flow | ✅ | R(QA); VEH; MASS |

Details zum Maßnahmenpaket 2025-12-12:
- #1 README/DOC spiegeln Acceptance 1–15 inkl. Dispatcher-Verweis.
- #2 Speichermodul/HUD priorisieren `character.self_reflection` + Auto-Reset.
- #3 HUD/Toolkit-Status und README-Smoke synchronisiert.
- #4 Schrittfolge + Beispiel-Save im Speichermodul dokumentiert.
- #5 Psi-Modul bündelt Arena-Psi-Bullets (Tax/Buffer/Logs).
- #6 doc.md Smoke-Flow um Arena-/Fahrzeugtests ergänzt.

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
| #4 | Single Source of Truth für Rift-Seeds | ✅ | M12; TK(16); gameplay/kampagnenstruktur |
| #5 | Arena-Mode-Reset (campaign.mode ← previous_mode) | ✅ abgeschlossen | TK(16); RT; SR |
| #6 | Host-Regel beim Multi-Save-Import | ✅ abgeschlossen | README; M12 |
| #7 | CU-Formel konsolidieren (Risko, Hazard-Pay, 10×Level) | ✅ | CW; Modul 15; Modul 8A |
| #8 | Boss-DR nach Teamgröße staffeln | ✅ | HUD; TK(16); gameplay/kampagnenstruktur |
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

## Maßnahmenpaket Copy-Paste-QA 2025-12-27 (Issues #1–#17)

Der erneute Copy-Paste-Lauf (Acceptance 1–15, Save v6 Import/Export) bestätigt den grünen Status
der Runtime, deckt aber mehrere Doku- und Schema-Divergenzen auf. Die folgenden Punkte sind für die
nächsten Durchläufe einzuplanen.

| Issue | Thema | Fahrplan/Nächste Schritte | Status |
| ----- | ------------------------------ | -------------------------------------------- | ------ |
| #1 | Dispatcher-Smoke (Acceptance 1–6) | Golden-Strings/Hint als Single Source halten; README ↔ Fixtures diffen; Smoke 1–6 in CI forcieren. | ✅ erledigt |
| #2 | Load-Flow Flags | Persistenzquelle auf `campaign.entry_choice_skipped`/`ui.intro_seen` festlegen; `flags.runtime.skip_entry_choice` als transient dokumentieren. | ✅ erledigt |
| #3 | SaveGuard-Reihenfolge | Guard-Strings als Golden-Strings zentralisieren; `log_save_blocked()` immer mit `reason`+`phase/location`. | ✅ erledigt |
| #4 | Gear-Label Stabilität | Doku ergänzen: Gear-Namen werden nicht normalisiert; optional Snapshot-Test für Loadout-Namen. | ✅ erledigt |
| #5 | Paradoxon-Cluster/Merge-Cap | Klarstellung: kein Hard-Limit beim Erzeugen, Cap 12 nur beim Merge; Trace-Payload (`cluster_create`, `rift_seed_merge_cap_applied`) harmonisieren. | ✅ erledigt |
| #6 | Boss-Helper/Foreshadow | `!helper boss` Output (Gate+FS) stringstabil halten; DR/Teamgröße im Trace erzwingen. | ✅ erledigt |
| #7 | Mission-5 Badge Auto-Reset | SF-OFF Schritt 0 dokumentiert; Auto-Reset M5/M10 Flags symmetrisch prüfen, Badge-Strings als Golden-Checks halten. | ✅ erledigt |
| #8 | Modus Ask↔Suggest | Overlay-Suffix `· SUG` nach Load deterministisch; Snapshot-Runner ergänzen. | ✅ erledigt |
| #9 | Offline-Flow | Rate-Limit/Hints beibehalten; SaveGuard-Order (offline→arena→hq_only→chronopolis) testen, offline-log Schema stabilisieren. | ✅ erledigt |
| #10 | HUD-Events/QA-Budget | Schema auf `logs.hud` Objekt-Events prüfen oder Trace-Spiegel definieren; QA-Runner um Roundtrip für `vehicle_clash`/`mass_conflict` erweitern. | ✅ erledigt |
| #11 | Arena/PvP Resume | Arena-Guard-Strings fixieren; Resume-Token + `merge_conflicts` Trace stabil halten. | ✅ erledigt |
| #12 | Psi-Heat Reset | Konflikt-/HQ-Reset deterministisch halten; Acceptance 13 Solo & Arena testen. | ✅ erledigt |
| #13 | Accessibility Persistenz | Speicher-Snippet (`speicher-fortsetzung.md`) erweitert um `contrast`/`badge_density`/`output_pace`; Hinweis „Snippet gekürzt“ falls Beispiel minimal bleibt. | ✅ erledigt |
| #14 | Economy-Audit High-Tier | Trace-Payload (`target_range`, `chronopolis_sinks`) stabilisieren; Anchor-Tests 120/512/900+ in QA belassen. | ✅ erledigt |
| #15 | Wallet-/Merge-Shape | Wallets auf ID→{name,balance} festlegen; Ablageort `merge_conflicts` (Trace vs. `logs.flags`) kanonisieren und Migrationshinweis ergänzen. | ✅ erledigt |
| #16 | Onboarding Intro | HQ-Intro als Vollzitat verankert; README/Toolkit spiegeln die Langform, QA-Fixtures nutzen das vollständige Zitat. | ✅ erledigt |
| #17 | Save v6 Fixture (bereitgestellt) | Fixture in `internal/qa/fixtures/` spiegeln und gegen Validator laufen lassen; Reimport-Roundtrip Solo→Koop→PvP prüfen. | ✅ erledigt |

**Fixture-Spiegel (Copy-Paste-QA 2025-12-27)**

- Neues Vollschema-Beispiel
  `internal/qa/fixtures/savegame_v6_copy_paste_2025-12-27.json` spiegelt den Acceptance-Lauf:
  Persistenzanker `campaign.entry_choice_skipped/ui.intro_seen`, HUD-Events
  `vehicle_clash`/`mass_conflict`, Wallet-Union (`id → {name,balance}`) plus deterministische
  `merge_conflicts`-Traces und Offline-Hilfe-Guard.
- QA-Roundtrip: Fixture laden → HQ-Recap (Skip EntryChoice) → Koop- und PvP-Reimport;
  HUD-Events, SaveGuard-Reihenfolge und Merge-Trace (`merge_conflicts` +
  `rift_seed_merge_cap_applied` sofern Seeds abweichen) gegentesten.

Legende: 🟢 pass = kein Fix, als Golden-Check festhalten; 🟠 offen = Doku/Schemata präzisieren.

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
| #5 | Gear-Armband als eigenes Gear | ✅ abgeschlossen – keine Normalisierung, keine weiteren QA-Checks zu Armbändern | RT; TK(16); R |
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
- Smoke #8 SaveGuard: „Speichern nur im HQ“-Toast vs. Mission/Exfil/Arena-Blocker,
  Snapshot-Toleranz prüfen.
- Dispatcher-Smoke #4/#6: Startoptionen `npc-team 5` bzw. `gruppe 3` ohne Markdown, Strings
  Acceptance-konform.
- Economy/Rift/Wallet: CU-Formel für identische Mission in Core vs. Rift (Seeds/Hazard-Pay),
  Wallet-Split inkl. Rest-Policy loggen, Paradoxon-Index-Verhalten in Rift klarstellen.
- Arena: Load resettet auf HQ, Phase-Strike-Tax in `logs.arena_psi[]`, Option für Lobby-Resume
  klären.

## Maßnahmenpaket Tester-Playtest 2025-12-XX (Issues #1–#12, Review-Update)

Der erneute Tester-Lauf (Briefing vollständig, Output gegengeprüft) bestätigt die zwölf Issues,
liefert aber Präzisierungen zu Teamgröße, Rift-Zusammenwurf, Seed-Gating, Px-Reset und Offline-
Konnektivität. Die Punkte sind als nächste Umsetzungswelle zu planen; Priorität hat die
Konsistenz der Runtime-Entscheidung in Wissensmodulen, Save-Schema und QA-Snapshots.

1. **Issue #1 – Teamgröße kanonisch auf 5 festziehen (1 Spieler + 4 NPCs/Spieler) (✅ erledigt)**  
   Zielbild: aktive Party **1–5** (Standard = 5). `npc-team N` steht für **NPC-Begleiter 0–4**,
   effektive Party = 1+N, Clamp auf 5. `arena.team_size` und Start-Dispatcher prüfen
   (1–5, 0 nur Legacy → clamp auf 1). Veraltete 0–4/5–6-Angaben entfernen.
2. **Issue #2 – SaveGuard-Blocker-String konsolidieren (✅ erledigt)**  
   Ein kanonischer User-Text („Speichern nur im HQ…“) plus `logs.trace[]`-Guard-Reason
   (`save_blocked`, `reason=hq_only`) für QA. README/Acceptance auf dieselbe Phrase trimmen.
3. **Issue #3 – `!load` ohne Einstiegsauswahl (✅ erledigt)**  
   Load-Flow endet nach Recap direkt im HQ/Briefing (kein klassisch/schnell). `load_deep()` setzt
   `campaign.entry_choice_skipped=true` und `ui.intro_seen=true`, Modul 12/Toolkit/README
   konsistent gespiegelt.
4. **Issue #4 – Rift-Zusammenwurf deckeln & überschüssige Rifts abgeben (✅ erledigt)**  
   Merge-Flow deckelt offene Rift-Seeds auf 12, überschüssige Seeds gehen automatisch an
   ITI-NPC-Teams; Auswahl (kept/handoff) steht im Trace `merge_conflicts.rift_merge`. Kein
   globaler Reset von Paradoxon/Seeds beim Merge.
5. **Issue #5 – Legacy-Save-Beispiele in `zeitriss-core.md` bereinigen (✅ erledigt)**  
   Save-Beispiele auf v6-Shape (inkl. `party.characters[]`, `save_version`, `logs.*`) umgestellt und
   Gruppenstruktur klargestellt.
6. **Issue #6 – Rift-Seeds: spielbar nach Episodenabschluss (✅ erledigt)**  
   Seeds entstehen bei Px 5, bleiben bis Episodenabschluss gesperrt; Core/Toolkit/README gespiegelt.
7. **Issue #7 – Px-Reset-Timing festlegen (✅ erledigt)**  
   Reset bleibt **nach der Mission / im Debrief/HQ**; Flags `px_reset_pending/confirm` dokumentiert
   und in Wissensmodulen konsolidiert.
8. **Issue #8 – Boss-DR/HUD-Doku konsolidieren (✅ erledigt)**  
   HUD/README spiegeln Teamcap 1–5 und Boss-DR nach Boss-Typ (Mini vs. Arc/Rift); QA-Trace ergänzt
   `logs.trace[].boss.type`/`dr` für Mission-Start-Snapshots.
9. **Issue #9 – `logs.hud[]`-Overlays mit Timestamp (✅ erledigt)**  
   `logs.hud[]`-Events akzeptieren `at`, der Serializer ergänzt fehlende Timestamps beim HQ-Save.
   README/Toolkit/Save-Docs spiegeln die ISO-Stempel-Regel.
10. **Issue #10 – Offline-Konnektivität: HQ immer mit Kodex (✅ erledigt)**  
   Klarstellung: HQ **immer** mit Kodex-Uplink; Offline-Kappung gilt **nur während Mission**.
   Offline-Help und Save-Doku spiegeln den Re-Sync-Blocker im HQ.
11. **Issue #11 – Economy-Audit-Trace ergänzen (✅ erledigt)**  
   `economy_audit` in `logs.trace[]` beim HQ-Save (Level, HQ-Pool, Wallet-Sum, Richtwerte,
   Chronopolis-Sinks). HUD-Toast nur bei Out-of-Range.
12. **Issue #12 – Atmosphere-Contract-Capture in QA-Mode erzwingen (✅ erledigt)**  
   QA-Mode (`logs.flags.qa_mode=true`) erzwingt pro Phase 8–12 Zeilen plus Banned-Terms-Status
   und HUD-Toast-Zählung; SaveGuard blockt unvollständige Captures.

**QA-Hinweis (Review-Update)**  

- Teamgröße-Entscheid (1–5) muss in Save-Schema, Dispatcher, HUD-DR, Arena-Policy und
  QA-Fixtures gespiegelt werden.  
- Rift-Zusammenwurf: Deckel + Auswahl-UI/Logik und Abgabe an ITI-Teams in Save/Trace
  dokumentieren.  
- Offline: HQ bleibt online; Mission-only-Kappung reduziert SaveGuard-Missverständnisse.

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
- Teamgrößen-Regeln (Team gesamt 1–5, `npc-team` = 0–4 NPCs) festziehen; die
  Forderung nach 0–4 Teamgröße ist überholt.
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
| #14 | Teamgrößen-Fehlertexte | ✅ Validator/Start/HUD-Strings auf Team gesamt 1–5 harmonisiert,
| | | `npc-team` bleibt 0–4 NPCs; Docs und Tests angepasst |
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
| #3 | SaveGuard-Texte vereinheitlichen | Kanonische Guard-Matrix (`Speichern nur im HQ…`/Exfil/Arena/SYS nicht voll installiert) definieren und README/Save-Modul/Toolkit/Snapshots synchronisieren. | ✅ erledigt |
| #4 | Boss-DR & Teamgröße clampen | Teamgröße auf 1–5 hart clampen (Load/ArenaStart), DR-Tabelle anpassen; Legacy-Saves loggen Migration/Conflict. HUD/Toolkit-DR-Else-Branch streichen. | ✅ erledigt |
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
- ✅ UI-/Runtime-Normalisierung klemmt Teamgrößen hart auf 1–5, mappt
  `badge_density/output_pace` auf kanonische Enums und spiegelt Queue-/Zonen-
  Felder im Arena-Block der Saves.
- ✅ Offline-Fallbacks sind gehärtet: `!offline` besitzt ein 60-Sekunden-Rate-
  Limit, SaveGuard blockiert HQ-Saves ohne Uplink und schreibt einen
  Trace-Eintrag.
- ✅ SaveGuard wertet Arena-Queue-States
  (`idle|searching|matched|staging|active|completed`) beim Serialisieren aus,
  leitet `active/phase` daraus ab und sperrt HQ-Saves während laufendem
  Matchmaking; Tests prüfen aktiv blockierte Saves.

## Maßnahmenpaket Local-Uncut & LM-Studio 2026-05 (Issues #1–#7)

Die Umstellung auf lokale Runs mit gpt-oss-20b in LM Studio soll Store-
Compliance-Ballast entfernen, die „uncut“-Regeln sichtbar machen und parallel
stabile Presets für Consumer-Hardware liefern. Die Tabelle fasst die offenen
Aufgaben inkl. Fundstellen zusammen.

| Issue | Kurzfassung | Fahrplan/Nächste Schritte | Status |
| ----- | ------------------------------ | -------------------------------------------- | ------ |
| #1 | LM-Studio-Sampling-Presets | Zwei Presets anlegen (ZEITRISS-PLAY 0,60/0,92/60/0,05/1,06;
| | | Noir/Interlude 0,70/0,94/80/0,07/1,05) plus Antwort-Limit 1100–1600
| | | Tokens; Kontextprofile 16k/24k/32k dokumentieren und GPU/CPU-Defaults
| | | (Offload, Flash Attention, Batch 128–512, Thread-Pool nach Kernen)
| | | in README/Toolkit spiegeln. | ✅ erledigt |
| #2 | RAG-Settings entschlacken | Big-RAG auf Limit 4, Affinity 0,74, Chunk 650, Overlap 96
| | | trimmen; QA-Preset trennt Runtime-Module von QA-Dokumenten. Fundstelle:
| | | aktuelle RAG-Werte in LM-Studio-Preset/Tooling. | ✅ erledigt |
| #3 | Compliance-Makros neutralisieren | `ShowComplianceOnce`/`StoreCompliance` in README und
| | | `systems/toolkit-gpt-spielleiter.md` zu No-Ops umbauen oder entfernen;
| | | `systems/gameflow/speicher-fortsetzung.md` entbindet Loads von der
| | | Pflicht, den Hinweis auszugeben. | ✅ erledigt |
| #4 | Action-Contract Default auf „uncut“ | Save-/UI-Defaults auf `action_mode=frei|uncut`,
| | | Pattern `full_scene` (statt intent-cut-result), `loot_policy=full_loot`,
| | | `body_handling=protocol` umstellen; Schema-/Beispielblöcke in
| | | `systems/gameflow/speicher-fortsetzung.md` und README anpassen. | ✅ erledigt |
| #5 | Loot/Cleanup/Exfil als Gameplay | Loot-Blöcke wieder standardisieren (Waffen/Tools,
| | | Keys/Daten, Wert/CU, Hinweise, „heißes Loot“ markiert) ohne Body-Search-
| | | Anleitung; Cleanup als Risiko/Protokoll mit Kosten (Zeit, Stress,
| | | Noise/Heat) beschreiben; Exfil-Fenster wieder hervorheben. Spiegel in
| | | README, Toolkit und kampagnenstruktur. | ✅ erledigt |
| #6 | Template-Syntax-Guard | Systemprompt/Toolkit ergänzen: `{%`/`{{` ignorieren, keine
| | | Template-Klammern ausgeben; Fokus auf Klartext-Regeln, um oss-20b
| | | Verwirrung zu vermeiden. | ✅ erledigt |
| #7 | Neuer Systemprompt & Presets | Systemprompt „ZEITRISS 4.2.5 – LOCAL UNCUT“ liegt in
| | | `meta/masterprompt_v6.md` (Legacy in `meta/archive/masterprompt_v6_legacy.md`),
| | | Hinweise in README/Toolkit/Debrief aktualisiert. LM-Studio-Presets weiter
| | | trennen (PLAY uncut vs. QA mit niedriger Temp, QA-Blockformat). | ✅ erledigt |

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
QA-Stylevertrag. Alle Punkte sind umgesetzt und im Runtime-Overlay sowie in
den Wissensmodulen verankert.

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

## Maßnahmenpaket Spielbericht 2026-06 (Issues #1–#9)

Die folgenden Punkte stammen aus dem aktuellen Spielbericht (Player-Run +
GPT-Dialog). Schwerpunkt ist die sprachliche Entschärfung von
Moderations-Triggern, die Stabilisierung des Noir-Vokabulars und die
QA-Absicherung gegen How-to-Nähe sowie Digital-Drift.

| Issue | Kurzfassung | Fahrplan/Nächste Schritte | Status |
| ----- | ---------------------------------------- | ------------------------------------------- | ------ |
| #1 | Bio-Seed/Save-Wording entschärfen | `kreative-generatoren-missionen.md` Seed P-0004 und `speicher-fortsetzung.md` Beispiel-Strings auf Kontaminationsalarm/Probenverlust/Laborstörung umstellen (keine Erreger/Anschlag/Toxin). Optional `sensitive:true` + Core-Filter. QA: Smoke-Check „Banned Terms“ um Bio-Trigger ergänzen. | ✅ abgeschlossen |
| #2 | Extract/Kidnapping-Framing | Missionstyp „Verschwinden“ in Schutzaufnahme/Evakuierung umtexten, ggf. Split in Core/Opt-in. README-Mapping `extract → Evakuierung/Schutzaufnahme` ergänzen. QA: Acceptance-Regel für objective=`extract` ohne Entführungswortlaut. | ✅ abgeschlossen |
| #3 | Lockpick/Hack-How-to entfernen | `ausruestung-cyberware.md`, `characters/charaktererschaffung-grundlagen.md`, `cu_waehrungssystem.md` auf abstrakte Kompetenz-Boni umstellen (kein Dietrich/Lockpick/knacken/Hacker-Kit). QA: Banned-Terms erweitern (player-facing). | ✅ abgeschlossen |
| #4 | Encounter-Hack/Real-Targets entschärfen | `kreative-generatoren-begegnungen.md` Methoden auf physische Manipulation umstellen, reale Targets/SSL/Backdoor in In-World-Begriffe übersetzen. QA: Atmosphere-Contract-Banned-Terms um „Hack/Backdoor/SSL“ ergänzen. | ✅ abgeschlossen |
| #5 | Noir-Lexikon gegen Digital-Drift | Zentrale Mapping-Tabelle (Toolkit/README) für Knoten/Vault/Holo/Debug etc. definieren. `kampagnenstruktur.md`, `kreative-generatoren-begegnungen.md`, Gear-Namen auf Noir-Lexikon drehen. QA: Contract-Prüfung erweitert (hits + HUD-Toast 80/20). | ✅ abgeschlossen |
| #6 | Tone-Filter: `NAME.EXT` | Tone-Filter-Mapping auf „Aktenanhang/Beilage/Abzug“ umstellen oder Token entfernen; Whitelist/Blacklist für digitale Ersatzwörter ergänzen. QA: Atmosphere-Excerpt darf „uplink file“ nicht enthalten. | ✅ abgeschlossen |
| #7 | Dev-Kommandos aus Player-Facing | Knowledge-Pack-Splitting (Prod ohne Kommandoliste, QA mit Liste) oder Sanitizer-Regel für Backticked Commands. QA: 3 Szenen prüfen, keine Funktions-/Command-Tokens im Fließtext. | ✅ abgeschlossen |
| #8 | Atmosphere-Contract erweitern | `logs.flags.atmosphere_contract_capture` um `banned_terms.hits[]`, `howto_hits[]`, `rewrite_suggestion` ergänzen. QA-Playtest-Briefing: pro Phase Capture-Excerpt, FAIL → Issue. | ✅ abgeschlossen |
| #9 | „Richtlinien“ in Worldbuilding | `kampagnenstruktur.md` Überschrift „Content-Richtlinien“ in „Leitplanken/Bühnenregeln/Spielleitfaden“ umbenennen; optional Soft-Fail für Meta-Wörter in Contract. | ✅ abgeschlossen |

## Maßnahmenpaket Chrononauten-Presets 2026-07 (Issues #1–#4)

Die folgenden Punkte stammen aus dem aktuellen Review der vordefinierten
Chrononauten (Pregens, Schnellstart, Tutorial). Ziel ist, **alle Presets
vollständig editor-kompatibel** zu machen und **Rassenmodifikatoren, Talente
sowie Cyber-/Bioware** konsequent mitzuberechnen. So lassen sich alle
Beispielcharaktere 1:1 im Character-Editor nachbauen, ohne versteckte
Legacy-Regeln oder Skill-Sidepaths.

| Issue | Kurzfassung | Fahrplan/Nächste Schritte | Status |
| ----- | ---------------------------------------- | ------------------------------------------- | ------ |
| #1 | Pregens & Start-Archetypen auf 18-Punkte-Schema umstellen | `characters/charaktererschaffung-optionen.md`: Abschnitt `### Pregens` + alle<br>`## Start-Archetypen`-Blöcke auf **Editor-Basiswerte** umstellen<br>(Attribute starten bei 0, Rassenmods addieren, dann 18 Punkte).<br>**Rassenmods, Talente, Cyber-/Bioware** pro Pregen prüfen und in den<br>Attributzeilen spiegeln; SYS-Kosten der Implantate miterfassen.<br>Flavour-Zeilen an neue Schwerpunkte angleichen. QA: Jeder Pregen =<br>Summe 18 (vor Mods) + Editor-Nachbau (Rasse/Mods/Implantate/Talente). | ✅ erledigt |
| #2 | Schnellstart & Quick-Build editor-konform machen | `characters/charaktererschaffung-optionen.md`: `### Quick-Build für One-Shots`<br>auf Preset-Auswahl umstellen (kein „8 Punkte frei“).<br>`### Schnellstart-Chrononauten` auf Editor-Presets mit 18 Punkten +<br>Rassenmods umstellen; **Skills-Altbestand** entfernen oder 1:1 in<br>Talente übersetzen. Psi-Option klar als Toggle deklarieren. Unique-Gear<br>ohne direkte Px-Manipulation modellieren. QA: Alle Schnellstart-Presets<br>im Editor (Rasse/Mods/Implantate/Talente) nachbaubar. | ✅ erledigt |
| #3 | Tutorial-Charakter Jonas editorfähig machen | `characters/charaktererschaffung-grundlagen.md` → „Beispielcharakter für die<br>Tutorialrunde“: Attribute auf 18-Punkte-Schema bringen (inkl.<br>Rassenmods/Talente/Cyber-/Bioware, falls gesetzt). Text zur Probechance<br>prüfen und ggf. angleichen. QA: Jonas lässt sich im Editor ohne<br>Sonderregeln bauen. | ✅ erledigt |
| #4 | Preset-Validator gegen Drift | Tooling-Check aufsetzen (`tools/validate_presets.*` oder Parser):<br>prüft Presets auf 6 Attribute, Summe=18 (vor Mods), Start-Caps,<br>**Rassenmods**, **Talente**, **Cyber-/Bioware** inkl. SYS-Budget. Optional<br>strukturierte Preset-Quelle (JSON/YAML) definieren und Doku daraus<br>generieren. QA: Validator rot → nach Fix grün; Pflichtlauf im QA-Paket<br>dokumentieren. | ✅ erledigt |

**Umsetzungsstand 2026-07**

- ✅ `characters/charaktererschaffung-grundlagen.md` und
  `characters/charaktererschaffung-optionen.md` auf Editor-Basiswerte (18 Punkte)
  umgestellt: Start-Archetypen, Schnellstart-Chrononauten, Pregens und
  Tutorial-Preset spiegeln Rassenmods, Talente sowie SYS-Last der
  Cyber-/Bioware.
- ✅ Quick-Build und Schnellstart-Formate auf Preset-Auswahl gedreht; Skills
  in Talente übersetzt, Psi-Option als Toggle markiert, Unique-Gear ohne
  direkte Px-Manipulation.
- ✅ Preset-Validator `tools/validate_presets.py` prüft Attribute, Mods,
  Talente und SYS-Budget; `make lint` führt den Check aus.

## Maßnahmenpaket PvP-Arena Mixed-Reality 2026-08 (Issues #1–#9)

Dieses Paket bündelt die MR-Schärfung der PvP-Arena (Ausrüstung, Haptik,
Magnetfeld-Deck, Shared-Overlay) samt diegetischer HUD-Schicht. Ziel ist, dass
Arena-Outputs **physisch** wirken, ohne Digitalraum-Vibe.

| Issue | Kurzfassung | Fahrplan/Nächste Schritte | Status |
| ----- | ---------------------------------------- | ------------------------------------------- | ------ |
| #1 | Arena als MR-Trainingsanlage verankern | `gameplay/kampagnenstruktur.md`: „Simulation“ durch MR-Trainingsanlage ersetzen, Suit-Lock/Med-Scan und Reset-Logik diegetisch erklären. QA: 1 Arena-Probelauf ohne VR-Vokabular. | ✅ abgeschlossen |
| #2 | Hardware-/Facility-Kasten ergänzen | `gameplay/kampagnenstruktur.md`: kurzer MR-Absatz (Suit/Helm, Magnetfeld, Beacon-Gitter, Safe/Combat-Zonen), 1 Beispielabsatz „Eintritt in die Arena“. QA: Stil-Check gegen Holodeck/VR-Termine. | ✅ abgeschlossen |
| #3 | Default-Map umbenennen | `systems/toolkit-gpt-spielleiter.md`: Default `map` auf physische Bezeichnung (z. B. „Magnet-Deck A“) ändern; ggf. Legacy-Hinweis. QA: Arena-Start zeigt neuen Map-Label. | ✅ abgeschlossen |
| #4 | Diegetisches HUD als Default | `systems/toolkit-gpt-spielleiter.md`: `arena_hud()` um `style='diegetic'` ergänzen; Labels „Halle/Grenze/Zeit/Runde“ verwenden, Debug-Style optional. QA: HUD in beiden Styles prüfen. | ✅ abgeschlossen |
| #5 | Fahrzeug-Rigs für Arena | `gameplay/kampagnenstruktur.md`: Arena-Fahrzeugrigs beschreiben (Harness + MR-Karosse + Magnetfeld). `vehicle_policy='rig'` im Toolkit dokumentieren. QA: Chase-Szene mit Rig vs. off. | ✅ abgeschlossen |
| #6 | Kulisse = Set + MR-Overlay | `gameplay/kampagnenstruktur.md`: Kulissen-Satz ergänzen (Set/Props/Licht + MR), kein Epochensprung. QA: Prompt „Kulisse 1700“ bleibt Arena. | ✅ abgeschlossen |
| #7 | Feedback-Intensität als Kalibrierung | `gameplay/kampagnenstruktur.md` + Toolkit: `feedback_intensity` (off/low/standard) beschreiben; nur Beschreibung, keine Werte. QA: Start mit low/off prüfen. | ✅ abgeschlossen |
| #8 | Shared-Overlay Lore | `gameplay/kampagnenstruktur.md`: Beacon-Gitter + Suit-Marker erklären, damit alle dieselbe MR sehen. QA: Szene „Einer steigt ins Fahrzeug“ konsistent beschreiben. | ✅ abgeschlossen |
| #9 | Dämpfer diegetisch erklären | `gameplay/kampagnenstruktur.md`: Exploding-Dämpfer als Impuls-Governor erklären; optional diegetischer Toast. QA: Arena-Start-Info ohne Runtime-Begriffe verständlich. | ✅ abgeschlossen |

**Umsetzungsstand 2026-08**

- ✅ QA-Probelauf bestätigt MR-Trainingsterminologie, Beacon-Gitter,
  Suit-Lock/Med-Scan, physische Map-Labels und diegetische HUD-Labels.
- ✅ QA-Log 2026-08-15 dokumentiert den Abschluss; QA-Fahrplan ist synchron.

## Maßnahmenpaket Spielstart & Charaktererschaffung 2026-09 (Issues #1–#6)

Dieses Paket fasst den Feinschliff für Spielstart, Herkunftslogik und
Charakterdossier zusammen. Ziel ist ein runderer Einstieg mit klaren Defaults,
Origin-Block und Echo-Talent, ohne das Spieldesign zu verändern.

| Issue | Kurzfassung | Fahrplan/Nächste Schritte | Status |
| ----- | ---------------------------------------- | ------------------------------------------- | ------ |
| #1 | Start-Defaults ohne Spielerzahl-Fragen | `README.md` und `systems/toolkit-gpt-spielleiter.md`: `solo` setzt Ansprache **Du** und `player_count = 1`, keine Nachfrage; `gruppe` nutzt **Ihr**, Spielerzahl wird im Charakterbau mitgezählt. Modusfrage nur, wenn `klassisch|schnell` fehlt. | ✅ abgeschlossen |
| #2 | `npc-team`-Semantik klären | `README.md` und Toolkit: `npc-team N` = NPC‑Begleiter 0–4 (Team gesamt 1–5). Fehltexte bleiben unverändert. QA: Start-Transkripte/Smoke-Check prüfen. | ✅ abgeschlossen |
| #3 | Origin-Block vor der Statistik | `characters/charaktererschaffung-grundlagen.md` und README: Origin-Block (Epoche/Ort, Rolle/Beruf, Tod-Kategorie) vor den Werten; Optionen _selbst bauen_, `generate`, `custom generate`. | ✅ abgeschlossen |
| #4 | Echo-Talent als drittes Talent | `characters/charaktererschaffung-grundlagen.md`: 2 freie Talente + 1 Echo-Talent aus dem früheren Leben, eng gefasst. Checkliste konsistent auf drei Talente ziehen. | ✅ abgeschlossen |
| #5 | Dossier-Ausgabe definieren | `characters/charaktererschaffung-grundlagen.md`: Akte, früheres Leben, Todeskategorie, ITI-Motiv, Echo-Talent, Rolle, Anker/Schwachstelle, Hook als Abschlussblock. | ✅ abgeschlossen |
| #6 | Nullzeit-Puffer statt „virtueller Raum“ | `characters/charaktererschaffung-grundlagen.md`: Wording auf Nullzeit-Puffer/Holo-Interface/Labor drehen, Körperbau erst nach Abschluss. | ✅ abgeschlossen |

## Maßnahmenpaket Plattform-Contract Action & Gewalt 2026-10 (Issues #1–#6)

OpenAI hat die Plattformregeln für Gewalt weiter verschärft. Ziel ist, den
Agenten-Thriller-Ton und filmische Action zu behalten, ohne in How-to oder
Body-Handling abzudriften. Loot/Intel bleibt als **abstrakter Outcome** im
Debrief oder als knapper Scene-Tag („Keycard erhalten“) sichtbar.

| Issue | Kurzfassung | Fahrplan/Nächste Schritte | Status |
| ----- | ---------------------------------------- | ------------------------------------------- | ------ |
| #1 | Contract-Memo archivieren | Neues Meta-Dokument unter `internal/qa/evidence/` anlegen (Titel: „Plattform-Contract: Action & Gewalt“), Quelle/Datum vermerken und im QA-Log referenzieren. | ✅ abgeschlossen |
| #2 | Actionfilm-Cut als SL-Pattern | `systems/toolkit-gpt-spielleiter.md`: Guard/Pattern „Outcome statt Anleitung“ ergänzen (Intent → Cut → Resultat + Konsequenzen + Optionen), ohne Policy-Sprache im In-World-Output. | ✅ abgeschlossen |
| #3 | Style-Compliance spiegeln | `README.md` und `gameplay/kampagnenstruktur.md` (No-Go-Zonen/Style-Compliance) um kurze Regeln ergänzen: keine Schritt-für-Schritt-Gewalt, kein Body-Handling, Konsequenzen via Noise/Stress/Heat/Zeitfenster. | ✅ abgeschlossen |
| #4 | Loot-Handling abstrahieren | Toolkit-/Debrief-Hinweise präzisieren (Keycards/Intel als Outcome, Loot-Recap im Debrief, keine „Durchsuchen“-Prozeduren). Relevante Makros: `itemforge()`, Loot-Reminder. | ✅ abgeschlossen |
| #5 | QA-Checks für Tester:innen | `docs/qa/tester-playtest-briefing.md` um PASS/FAIL-Kriterien ergänzen (Cut/Outcome bei zu konkreten Ansagen, keine How-to-Optimierungen, In-World bleibt). | ✅ abgeschlossen |
| #6 | Optionales Runtime-Logging | Prüfen, ob `logs.flags.platform_action_contract` und `logs.flags.howto_guard_hits[]` sinnvoll sind; falls ja, Save-Schema/Runtime/Toolkit/Debrief spiegeln und QA-Trace definieren. | ✅ abgeschlossen |

## Maßnahmenpaket QA-Copy-Paste-Lauf 2026-10 (Issues #1–#11)

Der aktuelle Copy-Paste-Lauf aus `docs/qa/tester-playtest-briefing.md` deckt
Acceptance 1–15 komplett ab und liefert 11 neue Findings. Schwerpunkte:
Compliance-Bypass im QA-Mode, Dispatcher-Strings, Px5/ClusterCreate,
Mission-5-Badge-Check, Psi-Heat-Logging, Suggest-Persistenz,
Offline-Guard-Wording, Accessibility-Roundtrip, Economy-Drift-Trace,
HUD-Toast-Budget sowie Arena-Merge-Konflikte. Der komplette QA-Save liegt im
Testlog (inkl. Seeds 1–25/80–150/400–1000, Wallet-Anker 120/512/900+, Arena-
Pfad, Offline-Rate-Limit und HUD-Object-Events).

| Issue | Kurzfassung | Fahrplan/Nächste Schritte | Status |
| ----- | ------------------------------ | ------------------------------------------- | ------ |
| #1 | QA-Mode-Compliance & Ansprache | `ShowComplianceOnce(qa_mode=true)` zeigt nur HUD-Toast; Dispatcher übernimmt `qa_player_count`/`qa_addressing`, Save-Flags spiegeln QA-Mode. Debrief-Runtime-Flag ergänzen. | ✅ erledigt (2026-11-06) |
| #2 | Dispatcher-Start & Fehltexte | Golden-Strings für Start-/Fehlertexte (Klammern-Pflicht), Syntax-Hint 1×/Session (`dispatch_hint`, channel `dispatcher`), Load-Flow ohne EntryChoice, SaveGuard HQ-only-Blocker-String. | ✅ abgeschlossen (Strings/Trace in RT & README gespiegelt) |
| #3 | Px 5 → ClusterCreate-Standard | Trace-Schema `cluster_create` vereinheitlichen (`px_before/after`, `seed_ids`, Episode/Mission/Scene/Loc + campaign_type), `campaign.rift_seeds[]` als Objekte normalisieren; HUD-Toast „Px Reset → 0“. | ✅ abgeschlossen (Cluster-Trace + Seed-Normalisierung 2026-11-06) |
| #4 | Mission‑5 Badge/SF-OFF Safeguard | QA-Hook beim Start von M5: wenn `SF-OFF` fehlt, Warn-Toast/Debrief-Hinweis + Flag `acceptance_12_missing_sf_off`; `foreshadow_gate_m5_seen` persistieren. | ✅ abgeschlossen (2026-11-07) |
| #5 | Psi-Heat Trace | `log_psi_event()` um Kategorien `psi_heat_inc/reset` mit Trigger ergänzen; Aggregation pro Konflikt, HQ-Transfer reset protokollieren. | ✅ abgeschlossen (2026-11-07) |
| #6 | Suggest-Persistenz-Guard | `normalize_save_v6()` synchronisiert `ui.suggest_mode` ↔ `character.modes` und schreibt HUD-Tag `· SUG` deterministisch; Roundtrip-Test (SUG-ON/OFF) fixieren. | ✅ abgeschlossen (Runtime/README/Spiegel aktualisiert 2026-11-05) |
| #7 | Offline-FAQ & SaveGuard | README/FAQ-Text auf „HQ-Deepsave erst nach Re-Sync; SaveGuard blockt Offline-Ende“ angleichen; SaveGuard-Meldung mit Suffix „– HQ-Save gesperrt.“ und Trace `save_blocked` standardisieren. | ✅ abgeschlossen (Runtime-Strings & Wissensmodule vereinheitlicht 2026-11-05) |
| #8 | Accessibility-Roundtrip | UI-Block (`contrast/badge_density/output_pace` etc.) vollständig speichern/ laden; Legacy-Mapping unit-testen; Acceptance 14/15 Runner um Diff-Check erweitern. | ✅ abgeschlossen (2026-11-07) |
| #9 | Economy: Currency-Sync Trace | `sync_primary_currency()` loggt `currency_sync` (before/after, reason) bei Wallet-Split, Hazard-Pay, Arena-Fee, Markt-Kauf; Ankerwerte 120/512/900+ im QA-Runner prüfen. | ✅ abgeschlossen (Trace `currency_sync` für Arena/Wallet/Hazard/Markt aktiv 2026-11-05) |
| #10 | HUD-Toast-Budget | `hud_toast()` mit Scene-Cap: bei Cap Merge/Suppress von Low-Priority-Toast; Suppressions tracen `toast_suppressed` inkl. `hud_scene_usage` und `qa_mode`. Gate/FS/Boss priorisieren. | ✅ abgeschlossen (HUD-Budget/Trace aktualisiert 2026-11-06) |
| #11 | Arena-Merge-Konflikt-Toast | `reset_arena_after_load()` erzwingt Toast „Merge-Konflikt: Arena-Status verworfen“ bei jeder Verwerfung des Arena-Blocks, plus `merge_conflicts[]` Record; Dedupe per Token. | ✅ abgeschlossen (Toast + Trace dedupliziert 2026-11-05) |

## Maßnahmenpaket Copy-Paste-QA 2026-12 (Issues #1–#11, Fahrplan-Update)

Der aktuelle Lauf des Tester-Briefings (Acceptance 1–15, Save v6) wurde in einer frischen Instanz
kopiert und bestätigt. Alle Acceptance-Schritte 1–6 sind PASS, aber die Befunde sind string-sensitiv
und drift-anfällig. Die folgenden Punkte bündeln die To-dos für die nächsten Durchläufe; sie sind
offen und müssen in Runtime, Wissensmodulen und QA-Runner gespiegelt werden.

1. **Issue #1 – Dispatcher-Strings zentralisieren & Hint deduplizieren**
   Start-/Fehler-Strings liegen mehrfach (Dispatcher-Referenz, Toolkit). Eine zentrale
   `dispatcher_strings`-Quelle einführen, Dispatcher-Hinweis „Klammern sind Pflicht“ nur 1× pro
   Session als `dispatch_hint` tracen. QA: Golden-Files für Startsyntax, `npc-team 5`- und
   `gruppe 3`-Fehlertexte sowie Negativpfad `Spiel starten solo` erweitern.
   _Status: ✅ abgeschlossen – `dispatcher_strings` als Runtime-Export + Fixture gespiegelt;
   Hint-Trace 1×/Session, QA-Runner nutzt die Golden-Strings (2025-12-30)._
2. **Issue #2 – Gruppen-Import vs. kanonischer Export trennen**
   Speicher-Modul klarstellen: Loader akzeptiert Multi-JSON/Wrapper (`Charaktere`), kanonischer
   DeepSave exportiert immer `party.characters[]`. Loader-Doku/Helper mit Hinweis „Wrapper nie als
   Ausgabe erzeugen“ versehen, QA-Fixtures auf `party.characters[]` prüfen.
   _Status: ✅ abgeschlossen – Loader hebt Wrapper (`Charaktere`/`characters`) auf
   `party.characters[]`/`team.members[]`, Serializer exportiert ausschließlich das
   kanonische Roster (2025-12-30)._
3. **Issue #3 – SaveGuard-Required-Paths mit `arc_dashboard` abgleichen**
   Guard-Pflichtliste enthält `ui`/`arena`, aber kein `arc_dashboard`, obwohl der Container als
   Pflicht geführt wird. Entweder `arc_dashboard` vor Guard auto-initialisieren und als Required
   ergänzen oder ausdrücklich dokumentieren, warum er fehlt. QA: Save ohne `arc_dashboard` muss
   entweder auto-gefüllt oder geblockt werden, kein stilles Weglassen.
   _Status: ✅ umgesetzt – `arc_dashboard` wird vor dem HQ-Save aufgefüllt, SaveGuard prüft alle
   Dashboard-Pflichtpfade (2025-12-25)._ 
4. **Issue #4 – Mission‑5 Self‑Reflection konsistent hooken**
   Self-Reflection nur über `set_self_reflection()` setzen und am Missionsende (M5/M10) automatisch
   auf `SF-ON` resetten; Flags `self_reflection_auto_reset_*` schreiben. QA: Golden-File für
   Start (SF-OFF), Szene 10 (Boss-DR) und Ende (SF-ON + Flags) pflegen.
   _Status: ✅ abgeschlossen – Auto-Reset M5/M10 nutzt nur noch `set_self_reflection()` inkl.
   History und QA-Check._
5. **Issue #5 – Ask↔Suggest & HUD-Budget-Overflow tracciert halten**
   `emit_toast()` Budget-Entscheidung zentralisieren, bei Unterdrückung immer
   `toast_suppressed`-Trace plus Snapshot `logs.flags.hud_scene_usage` schreiben
   (inkl. QA-Mode-Flag). Gate/FS/Boss/Arena-Toasts bleiben budgetfrei. QA:
   Overflow-Szene mit 5 Low-Priority-Toasts, 1–2 sichtbar, Rest suppressed +
   Trace.
   _Status: ✅ abgeschlossen – `emit_toast()` schreibt jede Suppression inkl.
   HUD-Usage- und `qa_mode`-Snapshot; Budget greift nur für Low-Priority-Toasts
   (2027-02-11)._
6. **Issue #6 – Rift-Seed-Stacking vs. Merge-Cap dokumentieren**
   README/Save-Doku präzisieren: Solo-Px5 stapelt Seeds ohne Hard-Limit, Merge deckelt offene
   Seeds auf 12 und gibt Überschuss an ITI-NPC-Teams. Trace `rift_seed_merge_cap_applied` mit
   kept/overflow + `merge_conflicts`-Eintrag, QA: Cross-Mode-Import 14→12 Seeds belegen.
   _Status: ✅ abgeschlossen – Merge-Cap-Trace (`rift_seed_merge_cap_applied`), Konflikt-Record
   und Doku-Update (2026-12-31)._ 
7. **Issue #7 – HUD-Events `vehicle_clash`/`mass_conflict` strukturieren**
   `hud_event()`-Helper einführen, Objekt-Events validieren (Allowlist, numerische Felder) und
   fehlende `at`-Timestamps auto-füllen. QA: Je 1 Chase + 1 Massenkonflikt pro Run mit
   Objekt-Events in `logs.hud[]` prüfen.
   _Status: ✅ abgeschlossen – hud_event-Helper, Allowlist/Auto-Timestamp und HUD-Log-Sanitizer
   aktiv (2027-01-10)._ 
8. **Issue #8 – Economy-Anker & Merge-Regeln auditieren**
   `economy_audit()` als Helper pro HQ-Transfer/Debrief mit Level-Anker (120/512/900+) und
   Host-Vorrang für `economy.cu`; Wallet-Merge union-by-agent-id, Konflikte in
   `logs.flags.merge_conflicts`. QA: Import darf HQ-Pool nicht addieren, Audit-Range prüfen.
   _Status: ✅ abgeschlossen – Host-HQ-Pool bleibt beim Merge dominant, Wallets werden union-by-id
   zusammengeführt und Konflikte landen in `merge_conflicts` (2027-01-20)._
9. **Issue #9 – Arena/PvP Resume-Token & Mode-Restore stabilisieren**
   `reset_arena_after_load()` auf `arena.previous_mode`/`resume_token` priorisieren, damit
   Kampagnenmodus nach Arena korrekt zurückkehrt. SaveGuard blockt Arena-Saves, Merge-Konflikt-
   Toast standardisieren. QA: PvP-Flow laden/entladen, Mode-Restore und Phase-Strike-Tax-Logs
   prüfen.
   _Status: ✅ abgeschlossen – Load-Reset setzt Kampagnenmodus per previous/resume-Mode,
   Phase-Strike-Tax=0, SaveGuard blockt CITY/Arena (2027-03-02)._ 
10. **Issue #10 – Chronopolis-Unlock vereinheitlichen**
    Einheitlichen Unlock-Pfad bereitstellen (`chronopolis_unlocked`, Level/Key/Toast/Trace), HQ-
    SaveGuard blockt CITY. Migration: wenn Key-Item vorhanden, fehlende Flags ergänzen. QA:
    Level 9→10 Levelup → Toast/Flags/Trace; Save/Load stabil.
    _Status: ✅ abgeschlossen – Unlock prüft Level/Key auch beim Laden, SaveGuard meldet
    Chronopolis-Blocker, Trace/Toast werden nachgezogen (2027-03-02)._ 
11. **Issue #11 – Save v6 Fixture & Roundtrip sichern**
    Test-Save enthält alle Pflichtcontainer (Seeds, Economy-Anker, Arena/Chronopolis/HUD-Events,
    Atmosphere-Capture). Fixture als `savegame_v6_test.json`-Variante übernehmen, Exporter auf
    deterministische Reihenfolge/Timestamps vorbereiten. QA: Import → Spiel laden → Export →
    struktureller Diff ohne Containerverlust.
    _Status: ✅ abgeschlossen – Fixture `savegame_v6_test.json` trägt Chronopolis-, HUD- und
    Atmosphere-Capture-Blöcke, `last_save_at` fixiert Save-/HUD-Timestamps und ein Roundtrip-Test
    prüft den vollständigen Container-Erhalt (2027-03-05)._ 

## Maßnahmenpaket Copy-Paste-QA 2027-XX (Issues #1–#10, neuer Lauf)

Der erneute Copy-Paste-Lauf (Acceptance 1–15, Save v6, Solo/NPC/Koop/PvP) bestätigt die Matrix,
liefert aber zehn präzise Deltas. Die folgenden Punkte sind für den nächsten Zyklus einzuplanen
und mit QA-Runner sowie Fixtures abzugleichen.

1. **Issue #1 – Acceptance 1–15 Basislinie mit zwei Warnungen**
   Acceptance-Checkliste in allen Modi PASS; Warnungen: Foreshadow-Hint verweist auf
   „Mission 4/9" statt „Szene 4/9" (Issue #2) und SaveGuard-Priorität kann den Arena-Blocker
   überdecken (Issue #3).
   _Status: ✅ abgeschlossen – Warnungen gelöst (Szenen-Text + Guard-Order harmonisiert);
   Basislinie bleibt PASS._

2. **Issue #2 – Foreshadow-Gate-Text von Mission auf Szene umstellen**
   Gate-Hint („Fehlende Hinweise …“) und Boss-Foreshadow-Checklist referenzieren Mission 4/9,
   während Auto-Hints Szenen 4/9 nutzen. Text und Checklist konsequent auf Szenen umstellen
   (Core: Szene 4/9, Rift: Szene 9), Gate-Block-Hint anpassen.
   _Status: ✅ abgeschlossen – Helper/Toolkit stehen auf Szenen 4/9 (Core) bzw. 9 (Rift);
   `!boss status` spiegelt den Text._

3. **Issue #3 – SaveGuard-Priorität und Strings harmonisieren**
   Kanonische Reihenfolge: 1) Offline (exklusiv) → 2) Arena/Queue → 3) HQ-only → 4) weitere
   Guards. Toolkit nutzt abweichende Texte/Order. Alle Guards sollen die Speicher-Modul-Strings
   nutzen und Arena-Blocker sichtbar bleiben.
   _Status: ✅ abgeschlossen – Runtime/Toolkit speichern Guard-Order (offline → Arena → HQ →
   Exfil/SYS/Stressor) inkl. Trace `reason: arena_active`._

4. **Issue #4 – `phase`-Feld konsolidieren (core|transfer|rift|pvp)**
   Kompaktprofil listet `phase` als HQ/MISSION/ARENA, kollidiert mit Save-Modul (lowercase
   core|transfer|rift|pvp, HQ-Save = core). Doku angleichen und Loader-Fehlertext erlaubte Werte
   nennen.
   _Status: ✅ abgeschlossen – Phase-Felder akzeptieren nur core|transfer|rift|pvp, Loader wirft
   SaveGuard bei Abweichung; Docs angepasst._

5. **Issue #5 – Merge-Transparenz für Seed-Cap/Overflow**
   Host gewinnt Kampagnenblock; Seed-Cap 12 + Overflow zu ITI-Teams ist beschrieben, braucht aber
   standardisierten `merge_conflicts`-Record inkl. kept/overflow und Debrief-Zeile.
   _Status: ✅ abgeschlossen – Merge-Konflikte tragen `kept[]`/`overflow[]` + `handoff_to`;
   Trace + Debrief-Shapes dokumentiert._

6. **Issue #6 – Economy-Audit-Felder für High-Tier runs**
   Hazard-Pay/Reward-Formel klar, aber `economy_audit` braucht feste Keys: Level, HQ-Pool,
   Wallet-Summe, Zielrange (120/512/900+), Chronopolis-Sinks, Delta vs. Ziel. Semantik
   `economy.cu` (HQ-Pool) vs. `wallets{}` klarstellen.
   _Status: ✅ abgeschlossen – Audit führt Zielband + Delta-Felder, Chronopolis-Sinks bleiben
   enthalten; Toast nutzt das Zielband._

7. **Issue #7 – UI-Defaults `voice_profile` in README ergänzen**
   Serializer ergänzt `voice_profile` (default `gm_third_person`), README-UI-Auszug listet das
   Feld nicht. Doku-Drift schließen und Reload-Test um `voice_profile` erweitern.
   _Status: ✅ abgeschlossen – README/UI-Panel nennt `voice_profile` inkl. Default;
   QA-Checks bleiben bestehen._

8. **Issue #8 – HUD-Events strikt normalisieren**
   Allowlist nur `vehicle_clash`/`mass_conflict`; numerische Felder casten, Aliases mappen und
   `at` auto-füllen. Unbekannte Events sollen fallbacken statt Schema brechen.
   _Status: ✅ abgeschlossen – hud_event() mappt Aliasse, ergänzt Timestamps und fallbackt
   unbekannte Events auf HUD-Einträge._

9. **Issue #9 – Arena/PvP Mode-Restore und Phase-Strike-Logs absichern**
   `arenaStart()` soll `location='ARENA'`, `campaign.mode=pvp` und `previous_mode` setzen;
   SaveGuard blockt, Exit stellt zurück. Phase-Strike-Tax in `logs.arena_psi[]` mit Mode-
   Vorher/Nachher loggen.
   _Status: ✅ abgeschlossen – Arena-Start loggt `mode_previous`, SaveGuard nutzt Arena-Trace;
   Phase-Strike-Logs behalten Mode-Wechsel._

10. **Issue #10 – Test-Save v6 als Fixture übernehmen und Validator prüfen**
    Umfangreicher HQ-Core-Save (Lvl 8/120/512/950+, Seeds 1–25/80–150/400–1000, Arena/Offline/
    Economy/HUD-Logs) liegt vor. Validator könnte Zusatzfelder (`qa_profiles`, `economy.sinks`) zu
    strikt behandeln.
    _Status: ✅ abgeschlossen – Neues Fixture `savegame_v6_acceptance_full.json` enthält
    optionale Felder (`qa_profiles`, `economy.sinks`) und bleibt schema-konform._

## Maßnahmenpaket Dispatcher/Index-Glättung 2027-XX (Local-Uncut & LM Studio)

1. **Issue #1 – Dispatcher-Priorität vor „Neustart/Save?“**
   Masterprompt soll Start- und Load-Befehle zuerst erkennen und nur ohne Treffer „Neustart oder
   Save laden?“ anbieten (Solo/Gruppe automatisch setzen).
   _Status: ✅ umgesetzt – Masterprompt verankert Dispatcher-Check vor der Frage und präzisiert die
   Start-/Load-Ableitung._

2. **Issue #2 – Compliance-Bestätigung aus Toolkit entfernen**
   „Bitte bestätigen…“-Hinweis im Toolkit kollidiert mit leerem `ShowComplianceOnce()` und darf
   nicht mehr im Laufzeitfluss landen.
   _Status: ✅ bereinigt – Toolkit-Abschnitt markiert den Compliance-Hinweis als entfallen und
   unterbindet Bestätigungsaufforderungen._

3. **Issue #3 – Load-Flow ohne Modus-Abfrage spiegeln**
   Load soll Recap → HQ/Briefing ohne Nachfrage „klassisch/schnell“ laufen; fehlende JSONs via
   Kodex-Loader einsammeln.
   _Status: ✅ dokumentiert – Masterprompt nennt Modusfreiheit nach Load und den Kodex-Collector für
   fehlende JSONs._

4. **Issue #4 – Index-Hygiene Runtime vs. QA**
   QA-Briefings und Archivdateien dürfen nicht in den Runtime-Index; Index listet ausschließlich
   die 20 Wissensspeicher-Module (README, master-index*, 18 Runtime-Docs).
   _Status: ✅ dokumentiert – README stellt klar, dass QA-Briefings separat gepostet und nicht
   indiziert werden._

5. **Issue #5 – Sampling-Presets bewusst trennen**
   Missionen sollen das ZEITRISS-PLAY-Profil nutzen, HQ/ruhige Szenen Noir/Interlude; Response-
   Window aktiv limitieren.
   _Status: ✅ dokumentiert – README listet Einsatzregeln und Response-Limit-Schalter._

6. **Issue #6 – Kontextprofil auf 24k/32k statt 131k**
   Empfehlung: 24k als Default (32k bei langen HQ-Zyklen), 131k nur bei Spezialfällen; Tests gegen
   Tokens/s und Retrieval-Stabilität.
   _Status: ✅ dokumentiert – README nennt 24k/32k-Empfehlung und relativiert 131k._

## Maßnahmenpaket Beta-GPT Playtest 2026-XX (Issues #1–#12)

Der aktuelle Beta-GPT-Lauf (Tester-Briefing) liefert 11 dokumentierte Findings plus eine
Design-Korrektur: Preserve/Trigger sollen **nicht** strikt getrennt bleiben, sondern gemischt
spielbar sein. Die Punkte müssen in Runtime, Wissensmodulen und QA-Runner/Fahrplan sauber
nachvollzogen werden. Referenz: der mitgelieferte Save v6 (Multi-Level-Roster 8/120/512/905,
Seeds 1–25/80–150/400–1000, Mission‑5 Badge-Check, Offline-Trace, Arena-Reset).

1. **Issue #1 – Acceptance-Smoke-Checkliste #15 (Offline) fixieren**
   QA-Briefing/Acceptance-Liste auf exakt 15 Punkte normalisieren; Offline als eigener
   Acceptance-Schritt #15 ausweisen. Zusatz-Checks (Vehicle Clash/Mass Conflict/Arena) klar als
   „Nicht-Acceptance“ labeln. QA: Runner/Parser tolerieren 1–15 und taggen Offline separat.
   _Status: ✅ erledigt._

2. **Issue #2 – Save v6 Wallet-Beispiel in `zeitriss-core` korrigieren**
   `economy.wallets` im Beispiel auf Objektstruktur `{balance, name}` umstellen oder klar als
   nicht schema-valide Kurzform markieren. Doku-Hinweis „Schema v6“ ergänzen; Import-Test alt vs.
   neu (Fehler/PASS) definieren.
   _Status: ✅ erledigt – Beispiel auf v6-Objektstruktur korrigiert, Schema-Hinweis ergänzt._

3. **Issue #3 – Boss-DR konsolidieren (Teamgrößen-Skala)**
   `gameplay/kampagnenstruktur.md` als kanonisch setzen (Mini/Arc/Rift nach Teamgröße),
   `systems/wuerfelmechanik.md` und Generator-Snippets darauf harmonisieren. Boss-Toast nutzt
   berechneten DR. QA: Mission 5/10 Snapshot-Fixtures (Teamgröße 1–5) prüfen.
   _Status: ✅ erledigt – Würfelmechanik/Generatoren auf Team-DR gespiegelt._

4. **Issue #4 – Rift-Artefaktwurf: Boss-only Default + Variante**
   Artefakt-Drops als Default ausschließlich am Rift-Boss (Szene 10) definieren; optionaler
   Startwurf als Hausregel/Variant-Flag (`rift_artifact_variant=start_roll`) dokumentieren.
   QA: Rift-Lauf-Assertions (max. 1 Artefakt/Mission, Quelle = Boss).
   _Status: ✅ erledigt – Boss-only Default + Startwurf-Variante dokumentiert._

5. **Issue #5 – `!sf off|on` als offizielles HUD-Kommando**
   `systems/hud-system.md`/README-Kommandoliste um `!sf off|on` ergänzen, inkl. exakter
   Badge-/Toast-Strings (`SF-OFF`/`SF-ON`) und Log-Feld
   `self_reflection_last_change_reason`. Auto-Reset am Missionsende für complete/abort fixieren.
   QA: Acceptance 11 (M5 Start) + Abbruchpfad testen.
   _Status: ✅ erledigt – HUD/README-Kommandolisten ergänzt, Reason-Flag dokumentiert._

6. **Issue #6 – `merge_conflicts`-Katalog für Cross-Mode-Imports**
   Allowlist + Mindestfelder festlegen (`wallet`, `rift_merge`, `arena_resume`,
   `campaign_mode`, `phase_bridge`, `location_bridge`). Jeder Cross-Mode-Merge schreibt Trace +
   Conflict-Entry. `systems/gameflow/speicher-fortsetzung.md` um 2–3 Beispiele ergänzen.
   QA: Roundtrip Solo→Koop→PvP→HQ mit Diff auf `merge_conflicts[]`.
   _Status: ✅ erledigt – Allowlist/Mindestfelder, Beispiele ergänzt, Tests angepasst._

7. **Issue #7 – Economy-Audit Levelband-Regel in Koop**
   Regel festlegen: Band-Auswahl (z. B. Host-Level vs. Median) und `wallet_avg`-Scope
   (`team.members` vs. alle `economy.wallets`). Audit speichert `band_reason`/`wallet_avg_scope`.
   QA: Fixture mit 8/120/512/905 Mischteam deterministisch prüfen.
   _Status: ✅ erledigt – Host-Level-Regel + Median-Fallback dokumentiert, Scope gespiegelt._

8. **Issue #8 – PvP-Policy: Cross-Alignment klären**
   Arena-Policy definieren (Sim/Range vs. Lore-Kampf), `arena.match_policy` ins Save aufnehmen,
   Regeltext in `gameplay/kampagnenuebersicht`/Arena-Doku ergänzen. QA: Pro-vs-Contra PvP
   durchführen, HUD/Save muss Policy zeigen.
   _Status: ✅ erledigt – Policy definiert, Save-Feld/HUD ergänzt, Docs gespiegelt._

9. **Issue #9 – HQ Loop Contract (Debrief → Freeplay)**
   Pflichtschablone für Debrief: Auto-Loot → CU/Wallet-Split → EP/Skill-Prompt → expliziter
   Freeplay-Menüanker (Bar/Werkstatt/Archiv + 1 Gerücht). Optional Flag
   `logs.flags.hq_freeplay_prompted=true` für QA.
   _Status: ✅ erledigt – HQ-Loop dokumentiert und in Wissensmodulen gespiegelt._

10. **Issue #10 – HUD-Toast-Suppression im Log spiegeln**
   Unterdrückte Toasts nicht im Player-HUD, aber als `logs.hud[]`-Eintrag mit
   `suppressed:true` + Grund speichern; Trace `toast_suppressed` bleibt Pflicht. QA:
   3–4 Low-Priority-Overlays, 2 sichtbar, Rest suppressed + Trace.
   _Status: ✅ erledigt – Suppressed-Entries in `logs.hud[]` mit `reason:"budget"`._

## Maßnahmenpaket Beta-GPT Playtest 2026-01-14 (Issues #1–#9)

Der Beta-GPT-Lauf vom 2026-01-14 liefert neun dokumentierte Punkte inklusive
Test-Save v6 (Multi-Level-Roster 7/120/512/905, Rift-Cluster 1–25/80–150/400–1000).
Referenz: QA-Log 2026-01-14.

1. **Issue #1 – Rift-Casefile-Szenenmap konsolidieren**
   README-Rift-Map auf kanonische Szenenfolge (1–4 Tatort, 5–9 Leads,
   10 Boss-Encounter, 11–14 Auflösung) harmonisieren und Stage-Overlay spiegeln.
   _Status: ✅ erledigt – README/Runtime/Toolkit auf 14er-Map + Stage-Overlay aktualisiert._

2. **Issue #2 – Pre-City-Hub Save-Regel klären**
   Entscheidung zwischen HQ-savebar vs. Transit-Guard dokumentieren; SaveGuard
   und Kampagnenübersicht synchronisieren.
   _Status: ✅ erledigt – Pre-City-Hub als HQ-savebar fixiert, Kampagnenübersicht gespiegelt._

3. **Issue #3 – Testerauftrag: Kompakt-Profil + Kodex-Terminologie**
   Testerprompt auf Kompakt-Profil (Modul 12) verankern und „Codex“ durch
   „Kodex“ ersetzen; Schema-Datei nur als optionale CI-Referenz.
   _Status: ✅ erledigt – Tester-Briefing auf Kompakt-Profil + Kodex-Terminologie angepasst._

4. **Issue #4 – Rift-Seed-Merge deterministisch beschreiben**
   Auswahlregel für kept/overflow definieren (Tier/Timestamp) und Trace-Feld
   `selection_rule` ergänzen, damit QA reproduzierbar bleibt.
   _Status: ✅ erledigt – Merge-Regel (Tier/Discovered/Timestamp) + `selection_rule` dokumentiert._

5. **Issue #5 – SaveGuard-Prioritäten in Modul 12 spiegeln**
   Kanonische Reihenfolge (offline > arena > hq_only > exfil > sys > stress >
   psi_heat) als Tabelle/Verweis im Speichermodul festhalten.
   _Status: ✅ erledigt – Prioritätstabelle in Modul 12 ergänzt._

6. **Issue #6 – UI/Accessibility-Override im Cross-Mode-Import markieren**
   Erwartungssatz im Testerprompt ergänzen; optional Trace `ui_host_override`
   für QA-Nachvollziehbarkeit.
   _Status: ✅ erledigt – Testerprompt + Trace `ui_host_override` ergänzt._

7. **Issue #7 – HUD-Toast-Prioritäten definieren**
   Critical-Toast-Policy ergänzen, damit SaveGuard/Offline/Schema/Arena nicht
   durch Budget-Suppression verschwinden.
   _Status: ✅ erledigt – Critical-Tags dokumentiert und Runtime-Prioritäten erweitert._

8. **Issue #8 – Action-Contract filmisch präzisieren**
   Filmische Action bleibt erlaubt, aber ohne Schritt-für-Schritt-Anleitungen:
   Beats/Impact/Risiko statt technischer Prozeduren. Leitplanken in README,
   Toolkit und Kampagnenstruktur verankern, damit Kämpfe „filmisch cool“
   beschrieben werden, ohne How-to-Charakter.
   _Status: ✅ erledigt – README/Toolkit/Kampagnenstruktur auf filmische, abstrakte
   Beats ausgerichtet._

9. **Issue #9 – Test-Save v6 als CI-Fixture**
   Dummy-Save als Fixture (z. B. `qa_save_v6_dummy.json`) übernehmen; Loader
   toleriert Zusatzfelder in `logs.flags.qa_profiles` und normalisiert
   fehlende `hud_event.at`.
   _Status: ✅ erledigt – Dummy-Save-Fixture ergänzt, Normalizer-Regel dokumentiert._

11. **Issue #11 – Acceptance-Report standardisieren + Save-Fixture**
    Report-Format (Steps 1–15 PASS/FAIL + Links auf `logs.trace`/`logs.hud`) fixieren;
    Offline numerisch als #15. Beigefügten Save v6 als Copy/Paste-Fixture aufnehmen
    (Self-Reflection Auto-Reset, toast_suppressed, rift_seed_merge_cap_applied, Arena-Resume).
    QA: Reimport-Tests Solo→Koop→PvP mit Diff auf `economy.wallets{}`, `merge_conflicts[]`, `ui`,
    `arena`, `campaign.rift_seeds[]`.
    _Status: ✅ erledigt._

12. **Issue #12 – Preserve/Trigger nicht strikt trennen (Mixed-Play)**
    Kampagnenmodus soll gemischt spielbar sein; keine harte Trennung zwischen `preserve` und
    `trigger`. Doku/Toolkit/Mission-Generator prüfen: Pool-Logik, UI-Ansage und Save-Felder
    (`campaign.mode`, `seed_source`) so anpassen, dass gemischtes Spielen als Standard erlaubt ist.
    QA: Runs mit wechselnden Seeds (Preserve/Trigger gemischt) ohne Konflikt-Fehlermeldung.
    _Status: ✅ erledigt – Mixed-Default + Seed-Quelle pro Mission dokumentiert._


## Teilumsetzung 2026-02-20 – Paradoxon als Reward-Balken (Pass 1)

Referenz: `uploads/tiefenanalyse-regelwerk-und-onboarding.md`, Punkt 3
(Paradoxon-Index).

### Umgesetzte Punkte

- [x] Paradoxon-Subsystem auf reinen Fortschrittsbalken geschärft:
  keine Heil-, PP- oder Zustands-Boni auf Px-Stufen.
- [x] `ClusterCreate()` bei Px 5 als einziger mechanischer Payoff in
  Zustands-/Kampagnenmodul konsolidiert.
- [x] HUD-Textbeispiele bereinigt (kein `Loot +1` auf Zwischenstufen).
- [x] Toolkit-Wording bereinigt (`Px-Fortschritt` statt
  `Px-Belohnungen`).

### Teilumsetzung 2026-02-20 – Terminologie-Pass Mission/Episode/Szene (Pass 2)

Referenz: `uploads/tiefenanalyse-regelwerk-und-onboarding.md`, Punkt 1
(Kampagnen-Hierarchie).

### Umgesetzte Punkte

- [x] TL;DR in `README.md` auf kanonische Begriffe umgestellt
  (Mission = 12 Szenen, Episode = ~10 Missionen).
- [x] TL;DR im `core/spieler-handbuch.md` mit identischer Formel gespiegelt.
- [x] Glossar/Zeiteinheiten im Spieler-Handbuch um Episode/Arc/Kampagne
  ergänzt, damit Mission/Episode/Szene konsistent referenzierbar sind.


### Teilumsetzung 2026-02-20 – Speichersystem-Pass (Pass 3, Korrektur)

Referenz: `uploads/tiefenanalyse-regelwerk-und-onboarding.md`, Punkt 2
(Speichersystem).

### Umgesetzte Punkte

- [x] `core/wuerfelmechanik.md` von „Nightly Auto-Save" auf klare HQ-only-Autosave-Regel umgestellt.
- [x] `core/zeitriss-core.md` Nullzeit-Menü präzisiert: `Pfad fortsetzen`
  bedeutet Episodenverlauf, nicht Mid-Mission-Rückkehr aus dem HQ.
- [x] `characters/hud-system.md` Nullzeit-Menü analog angepasst; kein Mid-Mission-Load aus HQ.

### Folgeaufgaben-Status (konsolidiert)

- [x] Terminologie-Pass Mission/Episode/Szene repo-weit vereinheitlicht
  (README + Spieler-Handbuch auf kanonische Hierarchie abgeglichen).
- [x] Speichersystem-Pass abgeschlossen (HQ-only/Autosave-Definition
  in allen Modulen angeglichen).
- [x] README-Onboarding nach Spielerfluss umbauen (Quickstart zuerst,
  rechtliche Hinweise nachgelagert). _(Statusabgleich 2027-03-11: README führt
  den 5-Minuten-Quickstart vor Lizenz-/Rechtsteilen.)_
- [x] Template-Guard-Pass in Wissensmodulen (Template-Syntax entfernen oder
  intern kapseln). _(Abschluss über Läufe T1-T4 vom 2027-03-10; offene Delimiter
  in Runtime-/Toolkit-Modulen bereinigt.)_
- [x] Setup-/Versionierungsdrift (inkl. Changelog-Regel) in einem separaten
  Release-Durchlauf schließen. _(Abschluss über T5 vom 2027-03-10; Setup-Guide
  auf 4.2.6 harmonisiert, Changelog im Root vorhanden.)_

### Zyklus 2027-03-14 – KI-First-Onboarding & Economy-/Scaling-Checks

- KI-First-Onboardingpfad in README und Setup-Guide als identischer
  4-Schritte-Referenzfluss gespiegelt (Setup → Wissensslots → Sessionstart →
  HQ-zentrierter Session-Loop). Toolkit bleibt frei von Onboarding-UX-Texten.
  _Folgestand 2027-03-15: abgeschlossen; Restkatalog-Punkt 2 geschlossen._
- Economy-/Scaling-Checks als bindende QA-Liste gebündelt:
  1. `node tools/test_economy_merge.js` (Seed-Caps, Merge-Deckel).
  2. `node tools/test_acceptance_followups.js` (Mission-5/Boss/Foreshadow-Gates).
  3. `node tools/test_save.js && node tools/test_load.js` (Save/Load inkl.
     `economy_audit`-Trace und Wallet-Pfade).
  4. Pflicht-Läufe `python3 tools/lint_runtime.py` +
     `GM_STYLE=verbose python3 tools/lint_runtime.py` (Runtime-Regelabgleich).


### Zyklus 2027-03-15 – SSOT-Modulpipeline (Vorbereitung auf Step-by-Step-Durchläufe)

- Kanonische Priorität verbindlich festgelegt: `core/sl-referenz.md` und
  `core/spieler-handbuch.md` sind Primärquelle für Quickformat-Regeln;
  README, Gameplay- und Systems-Module spiegeln diese Definitionen.
- Restkatalog-Punkt 1 in eine 5-stufige Modulpipeline überführt:
  1. Kanon-Extraktion (Glossar + Muss/Soll/Kann-Semantik),
  2. README/Core-Anker-Sync,
  3. Gameplay-Pass,
  4. Systems-Pass,
  5. Konfliktprüfung mit Suchankern + Closure-Gate.
- Durchlaufreihenfolge für die nächsten Sessions festgezurrt:
  `README.md` → `gameplay/kampagnenuebersicht.md` →
  `gameplay/kampagnenstruktur.md` → `systems/currency/cu-waehrungssystem.md`
  → `systems/gameflow/speicher-fortsetzung.md` →
  `systems/toolkit-gpt-spielleiter.md`.
- Abschlusskriterium für den Restpunkt: Statuswechsel auf „abgeschlossen“ erst
  nach synchronem Update in Restkatalog, Fahrplan, Audit und QA-Log inkl.
  Pflichttestpaket.

### Aktiver Rest-Backlog (für die nächsten Zyklen)

- [x] Arena-Smoke-Baseline repariert: Device-Requirement-Check toleriert in
  `scripts/lint_arena.py` beide Dash-Varianten (`-`/`–`); Pflichtläufe
  `make test` und `bash scripts/smoke.sh` wieder grün. _(Stand 2027-03-12)_
- [x] Tiefenanalyse-Upload in einen strukturierten Maßnahmenkatalog überführt
  (nur verbleibende Punkte), damit Upload-Artefakte nicht mehr als operative
  To-do-Liste dienen. _(Erfasst in
  `internal/qa/plans/ZEITRISS-tiefenanalyse-restkatalog-2027.md`, Stand
  2027-03-13.)_
- [ ] Restkatalog iterativ abarbeiten (Single-Source-of-Truth-Restpunkte und
  Stil-Feinschliff) entlang der 5-stufigen SSOT-Modulpipeline und pro Zyklus
  im QA-Log dokumentieren.
- [x] Economy-/Scaling-Sicherungen als gebündelte QA-Checkliste im Fahrplan
  verankert (Stand 2027-03-14).
