---
title: "ZEITRISS Beta-QA Log 2025"
version: 0.4.48
tags: [meta]
---

# ZEITRISS Beta-QA Log 2025

## 2027-03-19 – Repo-Agent – SSOT-Pipeline Durchlauf 4 (Systems-Pass)
- Fokus: Den Systems-Pass sequenziell abschließen, damit Economy-/Save-/Toolkit-
  Semantik den Core-Kanon ohne Drift spiegelt.
- Scope: `systems/currency/cu-waehrungssystem.md`,
  `systems/gameflow/speicher-fortsetzung.md`,
  `systems/toolkit-gpt-spielleiter.md`,
  `internal/qa/plans/ZEITRISS-tiefenanalyse-restkatalog-2027.md`,
  `internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md`,
  `internal/qa/audits/ZEITRISS-qa-audit-2025.md`,
  `internal/qa/logs/2025-beta-qa-log.md`.
- Ergebnis:
  1. In allen drei Systems-Modulen SSOT-Ankerblöcke mit MUSS/SOLL/KANN
     ergänzt (Belohnung, SaveGuard/Px-Flow, Optionalität).
  2. Restkatalog-Durchlauf 4 auf **abgeschlossen** gesetzt; nächster Schritt ist
     die Konfliktprüfung/Closure.
  3. Fahrplan und Audit auf den neuen Pipeline-Stand synchronisiert.

**Backlog-Status**
1. Single-Source-of-Truth-Pass: **in Umsetzung** (Durchlauf 4 abgeschlossen,
   Closure-Gate offen).
2. Economy-/Scaling-Checkliste: **in Umsetzung**.
3. Stil- und Sprachkonsistenz: **offen**.

**Checks (Repo-Agent Pflichtpaket, Lauf 2027-03-19)**
- `make lint` → OK
- `make test` → OK
- `bash scripts/smoke.sh` → OK
- `python3 tools/lint_runtime.py` → OK
- `GM_STYLE=verbose python3 tools/lint_runtime.py` → OK
- `python3 scripts/lint_doc_links.py` → OK
- `python3 scripts/lint_umlauts.py` → OK

## 2027-03-18 – Repo-Agent – SSOT-Durchlauf 3a (Artefakt-Balance-Fix)
- Fokus: Rückmeldung zur Gameplay-Balance umsetzen und die Hausregel für
  Rift-Artefakt-Startwürfe entfernen, damit die Belohnungslogik stabil bleibt.
- Scope: `gameplay/kampagnenstruktur.md`,
  `internal/qa/plans/ZEITRISS-tiefenanalyse-restkatalog-2027.md`,
  `internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md`,
  `internal/qa/audits/ZEITRISS-qa-audit-2025.md`,
  `internal/qa/logs/2025-beta-qa-log.md`.
- Ergebnis:
  1. Artefakt-Drop in Rift-Ops als Boss-only-Mechanik (Szene 10) konsolidiert.
  2. `rift_artifact_variant=start_roll`/Hausregel aus dem Gameplay-Regeltext entfernt.
  3. SSOT-Status bleibt **in Umsetzung**; Systems-Pass weiterhin nächster Schritt.

**Backlog-Status**
1. Single-Source-of-Truth-Pass: **in Umsetzung** (Durchlauf 3a nachgeschärft).
2. Economy-/Scaling-Checkliste: **in Umsetzung**.
3. Stil- und Sprachkonsistenz: **offen**.

**Checks (Repo-Agent Pflichtpaket, Lauf 2027-03-18)**
- `make lint` → OK
- `make test` → OK
- `bash scripts/smoke.sh` → OK
- `python3 tools/lint_runtime.py` → OK
- `GM_STYLE=verbose python3 tools/lint_runtime.py` → OK
- `python3 scripts/lint_doc_links.py` → OK
- `python3 scripts/lint_umlauts.py` → OK

## 2027-03-18 – Repo-Agent – SSOT-Pipeline Durchlauf 3 (Gameplay-Pass)
- Fokus: Den Gameplay-Pass sequenziell gegen den extrahierten Core-Kanon
  abschließen, bevor der Systems-Pass startet.
- Scope: `gameplay/kampagnenuebersicht.md`,
  `gameplay/kampagnenstruktur.md`,
  `internal/qa/plans/ZEITRISS-tiefenanalyse-restkatalog-2027.md`,
  `internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md`,
  `internal/qa/audits/ZEITRISS-qa-audit-2025.md`,
  `internal/qa/logs/2025-beta-qa-log.md`.
- Ergebnis:
  1. Quickstart in `kampagnenuebersicht.md` als optionaler Zugriffspfad ohne
     Regeländerung explizit auf den Core-Kanon gebunden.
  2. `kampagnenstruktur.md` um SSOT-Anker für MUSS/SOLL/KANN ergänzt
     (Px/`ClusterCreate()`, CU-Formel, Boss-Rhythmus).
  3. Restkatalog-Durchlauf 3 auf **abgeschlossen** gesetzt; nächster Schritt
     ist der Systems-Pass.

**Backlog-Status**
1. Single-Source-of-Truth-Pass: **in Umsetzung** (Durchlauf 3 abgeschlossen).
2. Economy-/Scaling-Checkliste: **in Umsetzung**.
3. Stil- und Sprachkonsistenz: **offen**.

**Checks (Repo-Agent Pflichtpaket, Lauf 2027-03-18)**
- `make lint` → OK
- `make test` → OK
- `bash scripts/smoke.sh` → OK
- `python3 tools/lint_runtime.py` → OK
- `GM_STYLE=verbose python3 tools/lint_runtime.py` → OK
- `python3 scripts/lint_doc_links.py` → OK
- `python3 scripts/lint_umlauts.py` → OK

## 2027-03-17 – Repo-Agent – SSOT-Pipeline Durchlauf 2 (Anker-Sync README/Core)
- Fokus: Den zweiten Pipeline-Schritt sequenziell abschließen und README exakt
  auf den extrahierten Core-Kanon harmonisieren.
- Scope: `README.md`, `core/sl-referenz.md`, `core/spieler-handbuch.md`,
  `internal/qa/plans/ZEITRISS-tiefenanalyse-restkatalog-2027.md`,
  `internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md`,
  `internal/qa/audits/ZEITRISS-qa-audit-2025.md`,
  `internal/qa/logs/2025-beta-qa-log.md`.
- Ergebnis:
  1. README-Belohnungslogik mit Core synchronisiert
     (`ClusterCreate()` bei Px 5 + identische CU-Formel Core/Rift).
  2. Optionalitätssemantik im README geschärft
     (Schnellstart = optionaler Zugriffspfad ohne Regeländerung).
  3. Muss/Soll/Kann als verbindliche Normsprache im README ergänzt.
  4. SSOT-Restpunkt bleibt auf **in Umsetzung**; nächster Schritt ist der
     Gameplay-Pass laut fester Modulreihenfolge.

**Backlog-Status**
1. Single-Source-of-Truth-Pass: **in Umsetzung** (Durchlauf 2 abgeschlossen).
2. Economy-/Scaling-Checkliste: **in Umsetzung**.
3. Stil- und Sprachkonsistenz: **offen**.

**Checks (Repo-Agent Pflichtpaket, Lauf 2027-03-17)**
- `make lint` → OK
- `make test` → OK
- `bash scripts/smoke.sh` → OK
- `python3 tools/lint_runtime.py` → OK
- `GM_STYLE=verbose python3 tools/lint_runtime.py` → OK
- `python3 scripts/lint_doc_links.py` → OK
- `python3 scripts/lint_umlauts.py` → OK

## 2027-03-16 – Repo-Agent – SSOT-Pipeline Durchlauf 1 (Kanon-Extraktion)
- Fokus: Den ersten Pipeline-Schritt sauber abschließen, bevor README/Gameplay/
  Systems harmonisiert werden.
- Scope: `core/sl-referenz.md`, `core/spieler-handbuch.md`,
  `internal/qa/plans/ZEITRISS-tiefenanalyse-restkatalog-2027.md`,
  `internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md`,
  `internal/qa/audits/ZEITRISS-qa-audit-2025.md`,
  `internal/qa/logs/2025-beta-qa-log.md`.
- Ergebnis:
  1. Session-1-Kanon extrahiert und als Mini-Glossar fixiert
     (Rift-Risiko, Belohnung, Optionalität, Muss/Soll/Kann).
  2. SSOT-Restpunkt bleibt auf **in Umsetzung**, Closure-Gate unverändert aktiv.
  3. Folgeschritt für Session 1-2 festgelegt: Anker-Sync README/Core gegen den
     extrahierten Glossar-Kanon.

**Backlog-Status**
1. Single-Source-of-Truth-Pass: **in Umsetzung** (Durchlauf 1 abgeschlossen).
2. Economy-/Scaling-Checkliste: **in Umsetzung**.
3. Stil- und Sprachkonsistenz: **offen**.

**Checks (Repo-Agent Pflichtpaket, Lauf 2027-03-16)**
- `make lint` → OK
- `make test` → OK
- `bash scripts/smoke.sh` → OK
- `python3 tools/lint_runtime.py` → OK
- `GM_STYLE=verbose python3 tools/lint_runtime.py` → OK
- `python3 scripts/lint_doc_links.py` → OK
- `python3 scripts/lint_umlauts.py` → OK

## 2027-03-15 – Repo-Agent – SSOT-Modulpipeline für finalen Restpunkt aufgesetzt
- Fokus: Den letzten großen Restpunkt nicht ad hoc, sondern als reproduzierbare
  Step-by-Step-Pipeline aufsetzen, damit Altmodule und neue Quickformate
  dauerhaft synchron bleiben.
- Scope: `internal/qa/plans/ZEITRISS-tiefenanalyse-restkatalog-2027.md`,
  `internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md`,
  `internal/qa/audits/ZEITRISS-qa-audit-2025.md`,
  `internal/qa/logs/2025-beta-qa-log.md`.
- Ergebnis:
  1. Restkatalog-Punkt 1 von „offen" auf „in Umsetzung" gestellt und als
     5-stufige Modulpipeline dokumentiert.
  2. Kanonische Quellenpriorität festgezogen:
     `core/sl-referenz.md` + `core/spieler-handbuch.md` führen,
     README/Gameplay/Systems spiegeln.
  3. Feste Modulreihenfolge und Closure-Gate im Fahrplan verankert, damit die
     nächsten Läufe reproduzierbar nacheinander abgearbeitet werden.

**Backlog-Status**
1. Single-Source-of-Truth-Pass: **in Umsetzung** (Pipeline aktiv).
2. Economy-/Scaling-Checkliste: **in Umsetzung**.
3. Stil- und Sprachkonsistenz: **offen**.

**Checks (Repo-Agent Pflichtpaket, Lauf 2027-03-15)**
- `make lint` → OK
- `make test` → OK
- `bash scripts/smoke.sh` → OK
- `python3 tools/lint_runtime.py` → OK
- `GM_STYLE=verbose python3 tools/lint_runtime.py` → OK
- `python3 scripts/lint_doc_links.py` → OK
- `python3 scripts/lint_umlauts.py` → OK

## 2027-03-15 – Repo-Agent – Onboarding-Entkopplung final abgeschlossen
- Fokus: Nach dem Entfernen der Onboarding-UX aus dem Spielleiter-Toolkit den
  Abschlussstatus in den QA-Artefakten konsolidieren, damit kein
  Folge-Backlog zu Punkt "KI-First-Onboardingpfad" offen bleibt.
- Scope: `internal/qa/plans/ZEITRISS-tiefenanalyse-restkatalog-2027.md`,
  `internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md`,
  `internal/qa/audits/ZEITRISS-qa-audit-2025.md`,
  `internal/qa/logs/2025-beta-qa-log.md`.
- Ergebnis:
  1. Restkatalog-Punkt 2 auf **abgeschlossen** gesetzt
     (README/Setup als Referenzfluss, Toolkit onboardingfrei).
  2. QA-Fahrplan-Backlog präzisiert: offen bleiben nur
     Single-Source-of-Truth-Restpunkte und Stil-Feinschliff.
  3. QA-Audit spiegelt den Abschluss als eigenen Update-Block.

**Backlog-Status**
1. KI-First-Onboardingpfad: **abgeschlossen**.
2. Economy-/Scaling-Checkliste: **in Umsetzung**.
3. Single-Source-of-Truth + Stil-Feinschliff: **offen**.

## 2027-03-14 – Repo-Agent – Toolkit entkoppelt von Onboarding-UX
- Fokus: Rückmeldung umgesetzt, dass KI-First-Onboardinghinweise nicht im
  Spielleiter-Toolkit stehen sollen, um Runtime-Wissensmodule nicht mit
  Setup-/Bedienpfaden zu vermischen.
- Scope: `systems/toolkit-gpt-spielleiter.md`, `README.md`,
  `docs/setup-guide.md`, `internal/qa/plans/ZEITRISS-tiefenanalyse-restkatalog-2027.md`,
  `internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md`,
  `internal/qa/audits/ZEITRISS-qa-audit-2025.md`.
- Ergebnis:
  1. Abschnitt `KI-First-Onboardingflow (verbindlich)` aus dem Toolkit entfernt.
  2. Onboarding-Referenzfluss bleibt in README + Setup-Guide als User-Dokumentation.
  3. QA-Plan/Audit/Restkatalog auf den entkoppelten Zuschnitt aktualisiert.

**Backlog-Status**
1. KI-First-Onboardingpfad: **in Umsetzung** (UX in README/Setup, kein Toolkit-Mirror).
2. Economy-/Scaling-Checkliste: **in Umsetzung**.
3. Single-Source-of-Truth + Stil-Feinschliff: **offen**.

## 2027-03-14 – Repo-Agent – Onboarding-UX-Nachschärfung (Script vs. manuell)
- Fokus: Doppelte/unklare Einstiegsdarstellung in README/Setup auflösen,
  damit Nutzer:innen den Standardpfad (Script) und die manuelle Alternative
  eindeutig unterscheiden können.
- Scope: `README.md`, `docs/setup-guide.md`.
- Ergebnis:
  1. README führt jetzt einen klaren Standardpfad mit OpenWebUI/OpenRouter,
     Repo-Download, Script-Ausführung und Start-Checks (Masterprompt +
     Wissensslots).
  2. README ergänzt den Session-Update-Standard (vor jeder Runde Repo aktualisieren
     + Script erneut ausführen) ohne Doppelstruktur.
  3. Setup-Guide spiegelt den Ablauf inkl. „Vor jeder Session aktualisieren“
     und Hinweis auf den Script-basierten Update-Weg.

**Backlog-Status**
1. KI-First-Onboardingpfad: **in Umsetzung** (UX-Flow klarer, Folgeabgleich offen).
2. Economy-/Scaling-Checkliste: **in Umsetzung**.
3. Single-Source-of-Truth + Stil-Feinschliff: **offen**.

## 2027-03-14 – Repo-Agent – Restkatalog-Zyklus 1 (KI-First + QA-Checkliste)
- Fokus: Operativen Restkatalog konkret weiterführen, ohne Schnellschüsse:
  KI-First-Onboardingroute explizit spiegeln und Economy-/Scaling-Prüfpfad in
  QA-Dokumenten bündeln.
- Scope: `README.md`, `docs/setup-guide.md`,
  `systems/toolkit-gpt-spielleiter.md`,
  `internal/qa/plans/ZEITRISS-tiefenanalyse-restkatalog-2027.md`,
  `internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md`,
  `internal/qa/audits/ZEITRISS-qa-audit-2025.md`.
- Ergebnis:
  1. KI-First-Onboarding als synchroner 4-Schritte-Flow in README/Setup/Toolkit
     verankert.
  2. Economy-/Scaling-Checks im QA-Fahrplan als bindende Checkliste mit
     konkreten Testkommandos ergänzt.
  3. Restkatalog-Punkte #2 und #3 auf „in Umsetzung" gesetzt; Audit spiegelt den
     Zyklusstatus.

**Backlog-Status**
1. Single-Source-of-Truth-Restpunkte: **offen**.
2. KI-First-Onboardingpfad: **in Umsetzung** (Referenzfluss gespiegelt).
3. Economy-/Scaling-Checkliste: **in Umsetzung** (QA-Plan/Audit gebündelt).
4. Stil- und Sprachkonsistenz: **offen**.

## 2027-03-13 – Repo-Agent – Restkatalog-Klarstellung (KI-First)
- Fokus: Missverständliche Formulierung im Restkatalog korrigieren,
  damit ZEITRISS explizit als KI-geleitetes Chatfenster-Spiel geführt bleibt.
- Scope: `internal/qa/plans/ZEITRISS-tiefenanalyse-restkatalog-2027.md`,
  `internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md`.
- Ergebnis: Restpunkt 2 wurde von „spielbar ohne KI“-Pfad auf
  „KI-First-Onboardingpfad“ umgestellt und auf README/Setup/Toolkit ausgerichtet.

**Backlog-Status**
1. Arena-Smoke-Baseline: **bleibt geschlossen**.
2. Tiefenanalyse-Restkatalog: **aktiv**, jetzt mit KI-First-Formulierung.

## 2027-03-13 – Repo-Agent – Tiefenanalyse-Restkatalog operationalisiert
- Fokus: Offenen Tiefenanalyse-Folgepunkt aus dem Fahrplan in ein eigenes,
  operatives Maßnahmenblatt überführen.
- Scope: `internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md`,
  `internal/qa/plans/ZEITRISS-tiefenanalyse-restkatalog-2027.md`.
- Ergebnis: Restpunkte sind als strukturierter 4-Punkte-Katalog aus dem
  Upload-Artefakt extrahiert; Fahrplan referenziert jetzt den Katalog statt
  eines unstrukturierten Upload-To-dos.

**Backlog-Status**
1. Arena-Smoke-Baseline: **bleibt geschlossen**.
2. Tiefenanalyse-Restpunkte: **als operativer Restkatalog aktiv**
   (`ZEITRISS-tiefenanalyse-restkatalog-2027.md`).

**Checks (Repo-Agent Pflichtpaket, Lauf 2027-03-13)**
- `make lint` → OK
- `make test` → OK
- `bash scripts/smoke.sh` → OK
- `python3 tools/lint_runtime.py` → OK
- `GM_STYLE=verbose python3 tools/lint_runtime.py` → OK
- `python3 scripts/lint_doc_links.py` → OK
- `python3 scripts/lint_umlauts.py` → OK

## 2027-03-12 – Repo-Agent – Arena-Smoke-Baseline stabilisiert
- Fokus: Bekannten Arena-Smoke-Fehler (`[FAIL] Device requirement text present`)
  auflösen und Pflichtpaket wieder vollständig grün fahren.
- Scope: `scripts/lint_arena.py`, `internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md`.
- Ergebnis: Device-Requirement-Prüfung akzeptiert jetzt konsistent beide
  Dash-Varianten (`-` und `–`); `make test` und `bash scripts/smoke.sh` laufen
  wieder ohne Arena-Fehlstatus durch.

**Backlog-Status**
1. Arena-Smoke-Baseline: **geschlossen** (Regex robust gegen typografische
   Dash-Variante).
2. Tiefenanalyse-Maßnahmenkatalog bleibt als aktiver Folgepunkt im Fahrplan.

**Checks (Repo-Agent Pflichtpaket, Lauf 2027-03-12)**
- `make lint` → OK
- `make test` → OK
- `bash scripts/smoke.sh` → OK
- `python3 tools/lint_runtime.py` → OK
- `GM_STYLE=verbose python3 tools/lint_runtime.py` → OK
- `python3 scripts/lint_doc_links.py` → OK
- `python3 scripts/lint_umlauts.py` → OK

## 2027-03-11 – Repo-Agent – Ordnungslauf: Backlog-Konsolidierung & Upload-Ablage
- Fokus: QA-/Fahrplan-Status nach T4/T5 konsolidieren, widersprüchliche
  Rest-Checkboxen bereinigen und Upload-Ablage als Eingangs-/Archivpfad klären.
- Scope: `internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md`,
  `uploads/tiefenanalyse-regelwerk-und-onboarding.md`, `uploads/README.md`.
- Ergebnis: Tiefenanalyse-Folgeaufgaben sind als erledigt markiert, ein kleiner
  aktiver Rest-Backlog ist separat ausgewiesen; Upload-Artefakt trägt jetzt
  einen Archivhinweis.

**Rest-Backlog (aktiv)**
1. Arena-Smoke-Baseline (`[FAIL] Device requirement text present`) beheben oder
   als formales Known-Issue mit Exit-Kriterium führen.
2. Verbleibende Tiefenanalyse-Punkte als kompakten Maßnahmenkatalog in
   `internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md` weiterpflegen.

**Checks (Repo-Agent Pflichtpaket, Lauf 2027-03-11)**
- `make lint` → OK
- `make test` → FAIL (`[FAIL] Device requirement text present` im Arena-Smoke)
- `bash scripts/smoke.sh` → FAIL (`[FAIL] Device requirement text present`)
- `python3 tools/lint_runtime.py` → OK
- `GM_STYLE=verbose python3 tools/lint_runtime.py` → OK
- `python3 scripts/lint_doc_links.py` → OK
- `python3 scripts/lint_umlauts.py` → OK

## 2027-03-10 – Repo-Agent – Runtime-Neutralisierung Lauf 2 (T4–T5)
- Fokus: Abschluss der offenen Backlog-Punkte aus dem Tiefenanalyse-Nachtrag
  (Toolkit-Delimiter-Entzerrung + Versionsharmonisierung).
- Scope: `systems/toolkit-gpt-spielleiter.md`, `docs/setup-guide.md`,
  `internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md`.
- Ergebnis: Template-Delimiter wurden im Toolkit vollständig in
  template-neutrale Pseudocode-Klammern überführt; Version-Mischstand 4.2.6/
  4.2.7 im Setup-Guide ist harmonisiert.

**Inventur-/Migrationsstand**
1. `{{ ... }}`, `{% ... %}` und `{# ... #}` kommen im Toolkit nicht mehr als
   ausführbare Delimiter vor.
2. Setup-Guide führt Frontmatter und Versionshinweis konsistent auf 4.2.6.
3. Fahrplan dokumentiert Lauf 2 als Abschluss von T4 und T5.

Hinweis: Der Fehlstatus bei `make test`/`smoke.sh` entspricht weiterhin dem bekannten
Arena-Smoke-Defekt (`[FAIL] Device requirement text present`) und wurde durch
Lauf 2 nicht neu eingeführt.

**Checks (Repo-Agent Pflichtpaket, Lauf 2027-03-10)**
- `make lint` → OK
- `make test` → FAIL (`[FAIL] Device requirement text present` im Arena-Smoke)
- `bash scripts/smoke.sh` → FAIL (`[FAIL] Device requirement text present`)
- `python3 tools/lint_runtime.py` → OK
- `GM_STYLE=verbose python3 tools/lint_runtime.py` → OK
- `python3 scripts/lint_doc_links.py` → OK
- `python3 scripts/lint_umlauts.py` → OK

## 2027-03-10 – Repo-Agent – Runtime-Neutralisierung Lauf 1 (T1–T3)
- Fokus: Priorisierte Migration von Template-Delimiters in Runtime-Modulen gemäß
  Tiefenanalyse-Policy vom 2027-03-09-Nachtrag.
- Scope: `characters/hud-system.md`,
  `gameplay/kreative-generatoren-begegnungen.md`,
  `gameplay/kampagnenstruktur.md`, `gameplay/kreative-generatoren-missionen.md`,
  `systems/kp-kraefte-psi.md`, `core/sl-referenz.md`.
- Ergebnis: Alle bearbeiteten Snippets sind nun template-neutral formuliert;
  Regelwirkung bleibt als Pseudocode/Ablaufbeschreibung erhalten.

**Inventur-/Migrationsstand**
1. HUD-Menü-Macro durch klaren Schaltlogik-Text (`settings.ascii_only`) ersetzt.
2. Generator-Macros (`rand_event`, `roll_legendary`) in nicht-ausführbare
   Schrittfolgen überführt.
3. SG-/HUD-/Startbanner-Beispiele ohne `{{...}}` dargestellt.
4. Toolkit-Datei (`systems/toolkit-gpt-spielleiter.md`) weiter offen für T4.

Hinweis: Der Fehlstatus bei `make test`/`smoke.sh` entspricht einem bereits bekannten
Smoke-Defekt (Arena-Device-Requirement-Text) und wurde durch diesen Lauf nicht neu eingeführt.

**Checks (Repo-Agent Pflichtpaket, Lauf 2027-03-10)**
- `make lint` → OK
- `make test` → FAIL (`[FAIL] Device requirement text present` im Arena-Smoke)
- `bash scripts/smoke.sh` → FAIL (`[FAIL] Device requirement text present`)
- `python3 tools/lint_runtime.py` → OK
- `GM_STYLE=verbose python3 tools/lint_runtime.py` → OK
- `python3 scripts/lint_doc_links.py` → OK
- `python3 scripts/lint_umlauts.py` → OK

## 2027-03-09 – Repo-Agent – Tiefenanalyse-Fortsetzung (Policy-Klärung Pseudocode vs. Template)
- Fokus: Rückfrage aus Deep-Dive geklärt und als verbindliche Repo-Policy dokumentiert.
  Ziel ist konsistenter Runtime-Mirror ohne ausführbare Template-Delimiters in Wissensslots.
- Quelle/Bezug: `uploads/tiefenanalyse-regelwerk-und-onboarding.md` (Template-/Macro-Risiko),
  Maintainer-Rückfrage zur Einordnung „Pseudocode behalten oder löschen?“.
- Ergebnis: **Pseudocode bleibt**, aber **Jinja-artige Syntax im Runtime-Content wird schrittweise
  entfernt/neutralisiert**; Implementierungsdetails bleiben in `runtime.js`/`tools`/`scripts`.

**Policy-Entscheid (kanonisch für Folgeläufe)**
- Runtime-Wissensmodule sollen Regelwirkung transportieren, nicht eine konkrete Template-Engine.
- `{{ ... }}` / `{% ... %}` gelten im Wissensslot als Risikoformat und werden migriert.
- Ersatzformat: Klartext-Pseudocode, Entscheidungsregeln, strukturierte Beispiele, Testhinweise.

**Arbeitsaufträge (für nächste Läufe direkt referenzierbar)**
1. Inventur aller Runtime-Fundstellen mit Delimiters und Priorisierung (hoch/mittel/niedrig).
2. Migration in template-neutrale Runtime-Beschreibung bei identischer Regelwirkung.
3. Spiegelprüfung: Bei jeder Runtime-/Tooländerung bleibt die Wissensmodul-Version synchron.
4. Abschlussdoku im QA-Log inkl. Pflichttest-Paket je Änderungslauf.

**Inventur-Snapshot (aktueller Stand aus Repo-Scan)**
- `characters/hud-system.md`: enthält Macro-Block für HUD-Menü (`{% macro ... %}` + `{{ ... }}`).
- `gameplay/kreative-generatoren-begegnungen.md`: enthält Generator-Macros/Funktionsaufrufe.
- `systems/toolkit-gpt-spielleiter.md`: enthält umfangreiche Template-Fragmente.
- Ergänzende Treffer mit Platzhaltern (`{{SG_AUTO}}`) in
  `gameplay/kreative-generatoren-missionen.md` und `gameplay/kampagnenstruktur.md`.

**Checks (Analyse-/Dokudurchlauf)**
- `rg -n "\{\{|\{%" core characters gameplay systems | head -n 50` → Trefferliste erzeugt.
- `sed -n '1,260p' internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md` → Fahrplan-Kontext geprüft.
- `sed -n '1,260p' internal/qa/logs/2025-beta-qa-log.md` → Logstruktur geprüft.

**Nachverfolgung**
- QA-Fahrplan: Nachtrag **2027-03-09 – Tiefenanalyse-Mirror** ergänzt.
- Offene TODOs: T1–T5 im Fahrplan (Prioritäten + Zielformat) sind für die nächsten Läufe bindend.
- Commit/PR: folgt nach Pflicht-Testpaket.

## 2026-01-14 – Repo-Agent – Action-Contract (filmische Konflikte)
- Fokus: Action-Contract präzisiert (filmische Beats, abstrakte Technik, kein
  How-to), No-Go-Zonen-Formulierung geschärft, QA-Testprompt fordert explizit
  neue Szenarien und Konfliktvariation pro Phase.
- Artefakte: README, Toolkit, Kampagnenstruktur, Tester-Briefing, QA-Fahrplan
  und QA-Audit synchronisiert.

**Checks (Repo-Agent Pflichtpaket)**
- `make lint` → OK
- `make test` → OK
- `bash scripts/smoke.sh` → OK
- `python3 tools/lint_runtime.py` → OK
- `GM_STYLE=verbose python3 tools/lint_runtime.py` → OK
- `python3 scripts/lint_doc_links.py` → OK
- `python3 scripts/lint_umlauts.py` → OK

## 2026-01-14 – Repo-Agent – Fahrplan-Umsetzung (Issues #1–#7, #9)
- Fokus: Rift-Casefile-Map/Stage-Overlay, Pre-City-Save-Regel, Tester-Briefing (Kompakt-Profil +
  Szenario-Varianz), Rift-Seed-Merge-Determinismus (`selection_rule`), SaveGuard-Prioritäten,
  UI-Host-Override-Trace, Critical-Toast-Prioritäten, Dummy-Fixture für QA.
- Artefakte: `qa_save_v6_dummy.json` ergänzt, QA-Plan/Audit synchronisiert.

**Checks (Repo-Agent Pflichtpaket)**
- `make lint` → OK
- `make test` → OK
- `bash scripts/smoke.sh` → OK
- `python3 tools/lint_runtime.py` → OK
- `GM_STYLE=verbose python3 tools/lint_runtime.py` → OK
- `python3 scripts/lint_doc_links.py` → OK
- `python3 scripts/lint_umlauts.py` → OK

## 2026-01-14 – Repo-Agent – Beta-GPT Playtest 2026-01-14 (QA-Übernahme)
- Plattform: Beta ZEITRISS-GPT (Tester-Briefing)
- Wissensstand: Runtime/README 4.2.5 (Save v6 Beispiel), QA-Fahrplan 1.20.0
- Auftrag: Playtest-Output unverändert archivieren, Issues in Fahrplan/Audit übernehmen.
- Hinweis Auftraggeber: Issue #8 ist nicht anwendbar (kein Store, Self-Hosted, 18+).

```chatlog
EP 00 · MS 00 · SC 0/12 · PHASE Debrief · MODE CORE · COMMS OK · Px 0/5 · Stress 0/12 · Obj QA-Matrix + Testauftrag-Audit · Exfil —

Im ITI‑Nullzeit‑Hub steht der Briefingraum im Halbdunkel. Eine Glaswand, dahinter die kalte Geometrie des HQ‑Korridors. Der Kodex projiziert kein Missionsvideo, sondern eine saubere, nüchterne QA‑Tafel: Logs, Save‑Pfade, Gate‑Zähler, Seed‑Listen.

Neben dem Projektor liegen drei Sim‑Dossiers: Solo‑Run, Squad‑Run, Arena‑Run. Ein viertes: Rift‑Casefile in drei Cluster‑Bändern. Alles wirkt wie nach einem Einsatz – nur dass hier nicht Blut, sondern Inkonsistenzen an den Handschuhen kleben.

**Intel / Risiken / Zeitfenster**

* Abgedeckt: Dispatcher‑Startvarianten (Solo/NPC/Gruppe), Save/Load‑Pfad v6, HUD‑Budget + `hud_event`, Boss‑Gate + SF‑Badge, Psi‑Heat‑Reset, Accessibility‑Persistenz, Offline‑FAQ, Rift‑Seeds (1‑25 / 80‑150 / 400‑1000), Arena‑Start + Phase‑Strike‑Log.
* Auffälligkeiten: Rift‑Szenen‑Map (Dokument‑Drift), Pre‑City‑Hub Save‑Regel (Widerspruch), Seed‑Merge‑Deckel ohne deterministische Auswahlregel, Testauftrag‑Kleinstdetails (Schema‑Quelle, “Codex” vs “Kodex”).

---

ISSUE #1

* **Beobachtung:** Die Rift‑Casefile‑Szenenmap ist über die Doku hinweg inkonsistent: Ein Teil beschreibt Leads bis Szene 10 und Boss ab Szene 11, andere Stellen fixieren den Boss‑Encounter explizit auf Szene 10. Das reißt Gate‑Timing (Foreshadow‑Sperre), Casefile‑Stage‑Overlay und Testerwartungen auseinander.
* **Diagnose:** Dokument‑Drift zwischen README‑Segment (“14‑Szenen‑Map … 5–10 Leads, 11–14 Boss”) und den kanonischen Rift‑Timings (Boss‑Encounter Szene 10).
* **Evidenz:**

  * README beschreibt 14‑Szenen‑Map mit Leads 5–10 und Boss 11–14.
  * Kampagnenstruktur nennt Rift‑Boss als Ausnahme in Szene 10.
  * Generator‑Map fixiert “10. Boss‑Encounter” und “11–14 Boss‑Auflösung”.
  * Toolkit beschreibt Rift‑Boss (Szene 10) als den Artefakt‑Roll‑Punkt.

Lösungsvorschlag

* **Ansatz:** README‑Riftmap auf das kanonische Raster bringen: **1–4 Tatort**, **5–9 Leads**, **10 Boss‑Encounter**, **11–14 Boss‑Auflösung/Nachspiel/Epilog**. Casefile‑Stage‑Labels entsprechend mappen (Stage=LEADS endet vor SC10).
* **Risiken:** Bestehende Testskripte/“Golden Strings” könnten auf “Boss ab 11” abgestimmt sein und müssen mitgezogen werden.

To-do

* **Kodex:** Rift‑Overlay/Stage‑Mapping in den HUD‑Tags prüfen (LEADS→BOSS exakt bei SC10).
* **QA:** Regression: `assert_foreshadow(count=2)`‑Gate vor SC10 im Riftlauf; Verify: SC10 blockiert bis 2 Foreshadows, danach Boss‑Start.

Nächste Schritte

* **Maintainer:innen:** README‑Abschnitt “Rift‑Ops / 14‑Szenen‑Map” korrigieren; Referenzen (Toolkit/Generator) als Single‑Source verlinken.
* **Notizen:** Diese Diskrepanz wirkt direkt auf den Testerprompt: “Boss‑Szene” muss eindeutig sein, sonst sind Gate‑Checks uneindeutig.

---

ISSUE #2

* **Beobachtung:** Pre‑City‑Hub ist in der HQ‑Definition enthalten, gleichzeitig wird er als Sequenz beschrieben, in der “Save‑Aktionen deaktiviert” bleiben. Das kollidiert mit “Speichern nur im HQ” und kann zu widersprüchlichen SaveGuard‑Erwartungen führen.
* **Diagnose:** Zwei Dokumente definieren Pre‑City‑Hub unterschiedlich: einmal als HQ‑Teil (damit prinzipiell Save‑fähig), einmal als atmosphärische Brücke mit explizit deaktivierten Saves.
* **Evidenz:**

  * README: HQ umfasst ITI‑Hub, Decks **und Pre‑City‑Hub**; Chronopolis ist `CITY`.
  * Kampagnenübersicht: Pre‑City‑Hub‑Vorschau – “Einkauf, Rufgewinn **und Save‑Aktionen bleiben deaktiviert**”.
  * Save‑System: “Speichern ist ausschließlich in der HQ‑Phase zulässig … Pre‑City‑Hub zählt zum HQ”.

Lösungsvorschlag

* **Ansatz:** Eine kanonische Regel festnageln und technisch spiegeln:

  1. **Option A (einfach):** Pre‑City‑Hub ist HQ ⇒ Save erlaubt; Kampagnenübersicht anpassen (nur Shop/Ruf deaktiviert).
  2. **Option B (strenger):** Pre‑City‑Hub ist “HQ‑nah, aber transit” ⇒ SaveGuard‑Reason “Transit/Pre‑City‑Hub” ergänzen + klar dokumentieren.
* **Risiken:** Option B benötigt einen neuen Guard‑Grund und QA‑Update; Option A beeinflusst Flow‑Design (Save‑Scumming in Transit).

To-do

* **Kodex:** Wenn Option B: SaveGuard‑Priorität um “Transit” ergänzen (unterhalb Offline/Arena, oberhalb HQ‑Only).
* **QA:** Zwei Checks: Save‑Attempt im Pre‑City‑Hub (erwartetes Verhalten), danach Load‑Roundtrip v6.

Nächste Schritte

* **Maintainer:innen:** README + Kampagnenübersicht angleichen; eine Stelle als Single‑Source markieren.
* **Notizen:** Das ist ein echter Spieler‑Pain‑Point: “Bin ich gerade im HQ oder nicht?” wird sonst unklar.

---

ISSUE #3

* **Beobachtung:** Der Testerauftrag fordert implizit Schema‑Validierung, aber die Runtime‑Doku sagt explizit: Schema‑Datei ist nicht im Wissensspeicher; für GPT‑Läufe gilt das Klartext‑Kompaktprofil. Zusätzlich enthält der Tester‑Block selbst eine Legacy‑Schreibweise (“Codex”) in einer Stelle, obwohl der Begriff “Kodex” kanonisch ist.
* **Diagnose:** Testauftrag ist weitgehend passend, aber zwei Formulierungen sind nicht “spielgerecht”: (a) Validierungsquelle, (b) Terminologie‑Sauberkeit.
* **Evidenz:**

  * Speichermodul: JSON‑Schema existiert repo‑intern, wird aber **nicht** in den Wissensspeicher geladen; “für GPT‑Läufe genügt das Klartextprofil”.
  * Speichermodul liefert explizit “Kompakt‑Profil für GPT” (Pfadbaum + Pflichtfelder).
  * README/Spielkanon nutzt “Kodex” als Systembegriff (durchgehend im HQ/Pre‑City‑Hub‑Flow).

Lösungsvorschlag

* **Ansatz:** Testerauftrag anpassen:

  * “Validiere gegen Kompakt‑Profil (Modul 12)”, Schema‑Datei nur als optionale CI‑Referenz erwähnen.
  * Template‑Label “Codex” → “Kodex” (damit die QA‑Ausgabe keine Legacy‑Nennung erzwingt).
* **Risiken:** Externe Parser, die exakt auf “Codex:” getrimmt sind, müssten angepasst werden.

To-do

* **Kodex:** N/A (Dokument/Prompt‑Fix).
* **QA:** Testerprompt‑Lint: Terminologie‑Check (“Kodex” statt “Codex”) + Schema‑Quelle.

Nächste Schritte

* **Maintainer:innen:** Testerprompt‑Text an den Kompakt‑Profil‑Abschnitt koppeln; die Kompakt‑Profil‑Pfadliste als “Pflicht‑Checkliste” übernehmen.
* **Notizen:** Der Prompt ist ansonsten gut: er trifft Chronopolis‑Unlock‑Flags, `hud_event`‑Allowlist und Economy‑Audit‑Levelbänder.

---

ISSUE #4

* **Beobachtung:** Rift‑Seed‑Deckelung (12 offene Seeds beim HQ‑Merge) ist klar, aber die Auswahlregel “welche 12 werden behalten” ist nicht deterministisch beschrieben. Das macht Testcases mit “14→12” schwierig: kept/overflow kann sich ohne klare Sortierregel ändern.
* **Diagnose:** Spezifikation beschreibt Cap + Trace‑Felder, aber nicht die Priorisierung (Zeitstempel? Tier? Deadline?).
* **Evidenz:**

  * Kanon: Seeds stapeln ohne Hard‑Limit; beim HQ‑Merge Cap auf 12, Overflow geht an ITI‑NPC‑Teams; Trace `rift_seed_merge_cap_applied` + `merge_conflicts`‑Record mit `kept[]/overflow[]/handoff_to`.
  * README beschreibt denselben Cap + Trace‑Pfad.

Lösungsvorschlag

* **Ansatz:** Deterministische Auswahl dokumentieren (und im Merge implementieren): z. B. “behalte nach `discovered_at` (älteste zuerst) + Tier‑Priorität”, oder “Tier zuerst, dann discovered_at”. Hauptsache: stabil und dokumentiert.
* **Risiken:** Jede Priorisierung ist ein Balance‑Eingriff; muss mit Design abgestimmt werden (welche Seeds sind “wertvoller”?).

To-do

* **Kodex:** Merge‑Routine: Sortierkriterium + Trace‑Feld `selection_rule` ergänzen (damit QA exakt prüfen kann).
* **QA:** Seed‑Merge‑Test: 14 Seeds mit gemischten `seed_tier`/Timestamps; prüfen, dass kept/overflow reproduzierbar ist.

Nächste Schritte

* **Maintainer:innen:** Speichermodul um “Cap‑Selection‑Rule” Absatz ergänzen.
* **Notizen:** Ohne Regel wirkt kept/overflow “zufällig” und erzeugt Bug‑Reports, obwohl es nur fehlende Spezifikation ist.

---

ISSUE #5

* **Beobachtung:** SaveGuard‑Prioritäten sind im Toolkit explizit (Offline exklusiv → Arena aktiv → HQ‑Only → Exfil …). Der Save‑Pseudo‑Code‑Ausschnitt wird leicht als “vollständig” gelesen, obwohl er die frühe Priorisierung nicht abbildet. Das kann in QA zu falschem Erwartungsmanagement führen (falscher Reason‑String).
* **Diagnose:** Dokumentations‑Darstellung: eine Stelle ist vollständig (Toolkit‑Reihenfolge), eine ist ein verkürzter Ausschnitt.
* **Evidenz:**

  * Toolkit: “SaveGuard‑Prio: offline > arena > hq_only > exfil > sys > stress > psi_heat” und “offline ist exklusiv … Speichern blockiert”.
  * Speichermodul zeigt Guards und Pfadbaum, aber ein einzelner Code‑Ausschnitt kann missverstanden werden.

Lösungsvorschlag

* **Ansatz:** In Modul 12 die SaveGuard‑Prioritätsliste als “kanonische Reihenfolge” einmal explizit aufnehmen (oder direkt auf Toolkit‑Abschnitt verlinken).
* **Risiken:** Gering – reine Doku‑Klärung.

To-do

* **Kodex:** N/A (Doku‑Fix).
* **QA:** Negativtests: Save‑Attempt im HQ bei Offline → Reason=Offline; Save‑Attempt im HQ bei Arena aktiv → Reason=Arena aktiv; Save‑Attempt in City → Reason=Chronopolis kein HQ‑Savepunkt.

Nächste Schritte

* **Maintainer:innen:** SaveGuard‑Prio als Tabelle in Modul 12 ergänzen (inkl. “offline exklusiv”).
* **Notizen:** Das stabilisiert auch den Testerprompt (Reason‑Strings/Erwartung).

---

ISSUE #6

* **Beobachtung:** UI‑ und Accessibility‑Settings werden bei Cross‑Mode‑Load host‑seitig erzwungen und **nicht** als Merge‑Konflikt geführt. Das ist design‑mäßig ok, wirkt aber für Tester:innen wie “Bug: meine Einstellungen wurden überschrieben”, wenn der Prompt das nicht als expected behavior markiert.
* **Diagnose:** Erwartungs‑Lücke im Testerauftrag: Merge‑Konflikte sind explizit auf eine Allowlist begrenzt; UI ist ausdrücklich kein Merge‑Konfliktfeld.
* **Evidenz:**

  * Speichermodul: “UI‑/Accessibility‑Settings … werden host‑seitig erzwungen … erzeugen keinen Merge‑Konflikt; last_loaded‑Snapshot”.
  * UI‑Felder werden beim Serializer normalisiert/ergänzt (contrast/badge_density/output_pace/voice_profile).

Lösungsvorschlag

* **Ansatz:** Testerprompt ergänzt einen expliziten Erwartungssatz: “UI‑Settings werden vom Host übernommen; keine merge_conflicts.” Optional: ein HUD‑Toast beim Override (“Host‑UI angewandt”).
* **Risiken:** Ein zusätzlicher Toast kann HUD‑Budget belasten (siehe nächste Issue).

To-do

* **Kodex:** Optionaler Trace‑Eintrag `ui_host_override` (nicht als merge_conflict), um QA‑Nachvollziehbarkeit zu erhöhen.
* **QA:** Cross‑Mode‑Test: Save A (contrast=high) wird von Host B (standard) geladen → verify host wins + persisted.

Nächste Schritte

* **Maintainer:innen:** Testerprompt: Abschnitt “Cross‑Mode Save Import” um UI‑Override ergänzen.
* **Notizen:** Das ist nicht “Bug”, sondern “kommuniziere das Design”.

---

ISSUE #7

* **Beobachtung:** HUD‑Toast‑Budget & Suppression sind sauber spezifiziert (2 Toasts/Scene, Gate/FS/Boss/Arena ausgenommen; suppressed wird geloggt). Aber es fehlt eine klare “Critical‑Toast”‑Policy: SaveGuard/Offline‑Resync‑Hinweise sollten praktisch nicht durch Budget‑Noise verschwinden.
* **Diagnose:** Fehlende Prioritätsklassifikation: “low‑priority suppressed” ist beschrieben, aber nicht, welche Toast‑Tags niemals suppressed werden dürfen.
* **Evidenz:**

  * README: Budget‑Regel + “low‑priority Toasts” können unterdrückt werden; `toast_suppressed`‑Trace & snapshot `hud_scene_usage`.
  * HUD‑Event‑Spezifikation: Unterdrückte Toasts landen zusätzlich als `{tag,message,suppressed:true,reason:"budget"...}` in `logs.hud[]`.

Lösungsvorschlag

* **Ansatz:** Eine kleine Prioritätsliste dokumentieren:

  * **Critical (nie suppress):** SaveGuard‑Blocker, Offline‑Status/Resync, Schema‑Fehler, Arena‑Lock.
  * **System (allowlist):** Gate/FS/Boss/Arena (bereits ausgenommen).
  * **Flavor:** Atmos‑Snippets, optionale Reminder.
* **Risiken:** Mehr “Critical” reduziert die Wirkung des Budgets; muss minimal bleiben.

To-do

* **Kodex:** Toast‑Emitter: Tag‑basierte Priorität implementieren; suppression‑Log enthält `priority`.
* **QA:** Forced‑Overflow‑Test: 5 Toast‑Quellen in einer Szene; verify Critical bleibt sichtbar, Flavor suppressed + geloggt.

Nächste Schritte

* **Maintainer:innen:** README/HUD‑System um “Toast‑Prioritäten” ergänzen.
* **Notizen:** Das verhindert “Ich konnte nicht speichern, aber hab’s nicht gesehen”‑Reports.

---

ISSUE #8

* **Beobachtung:** In den kreativen Missionsgeneratoren sind mehrere Objectives so konkret formuliert, dass sie wie reale “How‑to”‑Sabotage‑Anleitungen wirken könnten (kritische Infrastruktur / Schadensszenarien). Das kollidiert mit dem eigenen Style‑No‑Go “keine Schritt‑für‑Schritt‑Gewalt/Procedures” und erhöht Safety‑Risiko.
* **Diagnose:** Generator‑Tabellen enthalten zu prozedurale, alltagsnahe Handlungsanweisungen statt outcome‑basierter Thriller‑Begriffe.
* **Evidenz:** Beispiele finden sich in den Generator‑Objectives (Abschnitt mit konkreten Sabotage‑Handlungen); Kampagnenstruktur betont explizit “keine Schritt‑für‑Schritt‑Gewalt … Konsequenzen statt Detailprozeduren”.

Lösungsvorschlag

* **Ansatz:** Objectives in Outcome‑Sprache umschreiben (Intent → Cut → Ergebnis), ohne reale Prozeduren/Details. Statt “wie” nur “was” + “Risiko/Heat/Stress‑Folgen”.
* **Risiken:** Zu abstrakt kann Design‑Klarheit kosten; daher in‑game als “Kodex‑Briefing‑Snippet” mit klaren Stakes, aber ohne Verfahren.

To-do

* **Kodex:** Generator‑Strings refactoren: prozedurale Verben entfernen; stattdessen Stakes/Consequences + abstrakte Ziele.
* **QA:** Safety‑Lint auf Generator‑Texte: “kritische Infrastruktur + prozedurales Verb” markieren.

Nächste Schritte

* **Maintainer:innen:** Generator‑Datei reviewen, insbesondere Objectives‑Listen; Style‑No‑Go als Gate in CI/Review aufnehmen.
* **Notizen:** Das ist nicht nur QA‑Kosmetik; es reduziert Moderationsrisiko.

---

ISSUE #9

* **Beobachtung:** Test‑Save v6 (Dummy) inkl. mindestens zwei (hier: vier) Level‑Varianten und drei Rift‑Cluster‑Seeds, plus HUD/Trace‑Belege für die Smoke‑Checklist‑Punkte (Startvarianten, SaveGuard, Px‑5/ClusterCreate, Boss‑Gate/SF, Psi‑Heat‑Reset, Accessibility, Offline‑FAQ, `hud_event` vehicle/mass, Arena/Phase‑Strike, Economy‑Audit).
* **Diagnose:** N/A (Lieferartefakt).
* **Evidenz:**

  * Pflichtpfade (Kompakt‑Profil) inkl. `last_save_at`, `platform_action_contract`, `howto_guard_hits`, vollständigem `arc_dashboard` etc. sind befüllt.
  * `hud_event` nutzt ausschließlich `vehicle_clash` und `mass_conflict` und folgt der Objektform.
  * Economy‑Audit‑Ranges (Lvl 120/512/900+) sind als Trace‑Events im Save enthalten.
  * Chronopolis‑Unlock‑Flags/Trace‑Pattern sind berücksichtigt.

**Test-Save (JSON)**

```json
{
  "save_version": 6,
  "zr_version": "4.2.5",
  "location": "HQ",
  "phase": "core",
  "character": {
    "id": "CHR-HIGH-0512",
    "name": "Mara Voss",
    "callsign": "VANTA",
    "rank": "Operator X",
    "lvl": 512,
    "stress": 0,
    "psi_heat": 0,
    "cooldowns": {},
    "self_reflection": true,
    "modes": ["suggest"],
    "attributes": {
      "SYS_max": 6,
      "SYS_installed": 6,
      "SYS_runtime": 6,
      "SYS_used": 6
    }
  },
  "campaign": {
    "episode": 10,
    "mission_in_episode": 0,
    "scene": 0,
    "px": 0,
    "px_reset_pending": false,
    "px_reset_confirm": true,
    "entry_choice_skipped": true,
    "rift_seeds": [
      {
        "id": "RIFT-LOW-0001",
        "epoch": "1912-Nordmeer",
        "label": "Eisfracht / Flüstern im Pack",
        "status": "open",
        "seed_tier": "early",
        "cluster_hint": "1-25",
        "level_hint": "<10",
        "hook": "Ein verschwundener Konvoi taucht in den Logbüchern wieder auf –
                 aber mit Zeitstempeln, die nicht stimmen."
      },
      {
        "id": "RIFT-MID-0088",
        "epoch": "1969-Küstenstadt",
        "label": "Küstenfunk / Echo im Relais",
        "status": "open",
        "seed_tier": "mid",
        "cluster_hint": "80-150",
        "level_hint": "120",
        "hook": "Ein Notruf läuft im Kreis. Jede Wiederholung enthält neue
                 Namen – und einen davon kennt die Zelle."
      },
      {
        "id": "RIFT-HIGH-0501",
        "epoch": "2099-Sprawl",
        "label": "Neon-Sprawl / Nullzeit-Riss",
        "status": "open",
        "seed_tier": "late",
        "cluster_hint": "400-1000",
        "level_hint": "500+",
        "hook": "Ein ganzer Block existiert in zwei Versionen. Beide
                 beanspruchen, die echte zu sein."
      },
      {
        "id": "RIFT-CLOSED-0210",
        "epoch": "1883-Inselkette",
        "label": "Aschehimmel / Abgesiegelter Korridor",
        "status": "closed",
        "seed_tier": "mid",
        "cluster_hint": "80-150",
        "level_hint": "120",
        "hook": "Die Karte zeigt einen Korridor, der gestern noch nicht da war –
                 jetzt ist er zugeschweißt."
      }
    ],
    "exfil": {
      "active": false,
      "armed": false,
      "hot": false,
      "sweeps": 0,
      "stress": 0,
      "ttl": 0,
      "anchor": null,
      "alt_anchor": null
    }
  },
  "party": {
    "characters": [
      {
        "id": "CHR-LOW-0007",
        "name": "Ivo Kern",
        "callsign": "DUST",
        "rank": "Operator I",
        "lvl": 7,
        "has_psi": false
      },
      {
        "id": "CHR-MID-0120",
        "name": "Lina Park",
        "callsign": "KEYSTONE",
        "rank": "Operator V",
        "lvl": 120,
        "has_psi": true
      },
      {
        "id": "CHR-HIGH-0512",
        "name": "Mara Voss",
        "callsign": "VANTA",
        "rank": "Operator X",
        "lvl": 512,
        "has_psi": true
      },
      {
        "id": "CHR-END-0905",
        "name": "Noah Reiss",
        "callsign": "BLACKTIDE",
        "rank": "Operator XII",
        "lvl": 905,
        "has_psi": true
      }
    ]
  },
  "team": {
    "members": [
      { "id": "CHR-HIGH-0512", "role": "lead", "status": "active" },
      { "id": "CHR-MID-0120", "role": "psi", "status": "active" },
      { "id": "CHR-LOW-0007", "role": "infil", "status": "standby" },
      { "id": "CHR-END-0905", "role": "overwatch", "status": "standby" }
    ]
  },
  "loadout": {
    "primary": "Suppressed SMG",
    "secondary": "Compact Sidearm",
    "tools": ["Comlink", "Jammer", "Handscanner", "Fiber-Cam", "Field Kit"],
    "armor": "Soft Armor",
    "notes": "QA-Dummy. Keine realweltlichen Prozeduren; nur Labels."
  },
  "economy": {
    "cu": 18200,
    "credits": 18200,
    "wallets": {
      "CHR-LOW-0007": { "name": "Ivo Kern", "balance": 1200 },
      "CHR-MID-0120": { "name": "Lina Park", "balance": 6400 },
      "CHR-HIGH-0512": { "name": "Mara Voss", "balance": 9800 },
      "CHR-END-0905": { "name": "Noah Reiss", "balance": 12500 }
    }
  },
  "logs": {
    "hud": [
      "Dispatch: Solo klassisch",
      "Dispatch: Solo schnell",
      "Dispatch: NPC-Team 3 schnell",
      {
        "tag": "Dispatch",
        "message": "NPC-Begleiter: 0–4 erlaubt. Nutze z.B. Spiel starten (npc-team 3 schnell).",
        "at": "2026-01-14T20:10:00Z"
      },
      {
        "tag": "Dispatch",
        "message": "Gruppe: keine Zahl angeben. Nutze z.B. Spiel starten (gruppe schnell).",
        "at": "2026-01-14T20:12:00Z"
      },
      "SUG-ON",
      "GATE 2/2",
      "FS 0/4",
      "SF-OFF",
      {
        "event": "vehicle_clash",
        "details": { "tempo": 2, "stress": 1, "damage": 1 },
        "at": "2026-01-14T20:44:10Z",
        "scene": { "episode": 10, "mission": 4, "index": 11, "total": 12 }
      },
      {
        "event": "mass_conflict",
        "details": { "chaos": 3, "break_sg": 12, "stress": 2 },
        "at": "2026-01-14T20:48:55Z",
        "scene": { "episode": 10, "mission": 4, "index": 12, "total": 12 }
      },
      {
        "tag": "HUD",
        "message": "Flavor-Toast unterdrückt",
        "suppressed": true,
        "reason": "budget",
        "action": "suppressed",
        "at": "2026-01-14T20:49:01Z"
      }
    ],
    "trace": [
      {
        "event": "dispatcher_start",
        "at": "2026-01-14T20:00:00Z",
        "location": "HQ",
        "phase": "core",
        "campaign_mode": "solo_classic",
        "scene": { "episode": 1, "mission": 0, "index": 0, "total": 12 }
      },
      {
        "event": "dispatcher_start",
        "at": "2026-01-14T20:03:00Z",
        "location": "HQ",
        "phase": "core",
        "campaign_mode": "solo_fast",
        "scene": { "episode": 1, "mission": 0, "index": 0, "total": 12 }
      },
      {
        "event": "dispatcher_start",
        "at": "2026-01-14T20:06:00Z",
        "location": "HQ",
        "phase": "core",
        "campaign_mode": "npc_team_fast",
        "meta": { "npc_count": 3 }
      },
      {
        "event": "dispatcher_error",
        "at": "2026-01-14T20:10:00Z",
        "location": "HQ",
        "phase": "core",
        "campaign_mode": "npc_team_fast",
        "meta": { "npc_count": 5, "reason": "npc_out_of_range" }
      },
      {
        "event": "dispatcher_start",
        "at": "2026-01-14T20:11:30Z",
        "location": "HQ",
        "phase": "core",
        "campaign_mode": "group_fast",
        "meta": { "players": 2, "saves_loaded": 2, "new_roles": 1 }
      },
      {
        "event": "dispatcher_error",
        "at": "2026-01-14T20:12:00Z",
        "location": "HQ",
        "phase": "core",
        "campaign_mode": "group_fast",
        "meta": { "players": 3, "reason": "group_count_not_allowed" }
      },
      {
        "event": "save_blocked",
        "at": "2026-01-14T20:20:00Z",
        "location": "FIELD",
        "phase": "core",
        "meta": { "reason": "hq_only" }
      },
      {
        "event": "cluster_create",
        "at": "2026-01-14T20:33:00Z",
        "location": "FIELD",
        "phase": "core",
        "meta": { "px_before": 5, "px_after": 5, "seed_ids": ["RIFT-LOW-0001", "RIFT-MID-0088"] }
      },
      {
        "event": "StartMission",
        "at": "2026-01-14T20:38:00Z",
        "location": "FIELD",
        "phase": "core",
        "scene": { "episode": 10, "mission": 5, "index": 0, "total": 12 },
        "foreshadow": { "progress": 0, "required": 4, "tokens": "FS 0/4", "expected": "GATE 2/2" },
        "boss": { "type": "mini", "dr": 4, "toast": true }
      },
      {
        "event": "self_reflection_auto_reset",
        "at": "2026-01-14T20:58:00Z",
        "location": "HQ",
        "phase": "core",
        "meta": { "result": "completed", "badge": "SF-ON" }
      },
      {
        "event": "launch_rift",
        "at": "2026-01-14T21:10:00Z",
        "location": "HQ",
        "phase": "rift",
        "meta": { "seed_id": "RIFT-HIGH-0501", "cluster_hint": "400-1000" },
        "foreshadow": { "progress": 2, "required": 2 }
      },
      {
        "event": "arenaStart",
        "at": "2026-01-14T21:25:00Z",
        "location": "HQ",
        "phase": "pvp",
        "meta": { "team_size": 2, "match_policy": "sim" }
      },
      {
        "event": "economy_audit",
        "at": "2026-01-14T21:30:00Z",
        "location": "HQ",
        "phase": "core",
        "meta": {
          "level": 512,
          "band_reason": "host_level",
          "hq_pool": 18200,
          "wallet_sum": 29900,
          "wallet_count": 4,
          "wallet_avg": 7475,
          "wallet_avg_scope": "economy.wallets",
          "target_range": "512",
          "delta": { "hq_pool": -6800, "wallet_avg": 2475 },
          "out_of_range": { "hq_pool": true, "wallet_avg": true }
        }
      },
      {
        "event": "toast_suppressed",
        "at": "2026-01-14T20:49:01Z",
        "location": "FIELD",
        "phase": "core",
        "meta": {
          "reason": "budget",
          "qa_mode": true,
          "hud_scene_usage_snapshot": { "EP10.M4.SC12": 2 }
        }
      }
    ],
    "artifact_log": [
      {
        "at": "2026-01-14T21:18:00Z",
        "seed_id": "RIFT-HIGH-0501",
        "artifact_id": "ART-NULLGLASS-01",
        "roll": 6,
        "bonus": "Temporal Stabilizer (Dummy)",
        "note": "Boss-Roll in Rift-Encounter (QA)."
      }
    ],
    "market": [
      {
        "at": "2026-01-14T21:05:00Z",
        "item": "Chronopolis: Era-Skin (Dummy)",
        "cost_cu": 200,
        "px_clause": "0",
        "source": "chrono_stock"
      }
    ],
    "offline": [
      {
        "at": "2026-01-14T20:22:00Z",
        "trigger": "comms_drop",
        "device": "comlink",
        "jammer": "unknown",
        "range": "degraded",
        "relay": "fallback",
        "scene": { "episode": 10, "mission": 3, "index": 6 }
      }
    ],
    "kodex": [
      { "at": "2026-01-14T20:00:05Z", "msg": "Dispatch-Hinweis: Menü/Modus/Save in HQ verfügbar." },
      { "at": "2026-01-14T21:00:00Z",
        "msg": "Chronopolis-Status geprüft: Key aktiv, Warnbanner einmalig." }
    ],
    "alias_trace": [
      { "at": "2026-01-14T20:46:00Z", "alias": "VANTA", "heat": 1,
        "note": "Cover-Name in Funkschnitt gefallen." }
    ],
    "squad_radio": [
      { "at": "2026-01-14T20:47:10Z", "from": "ITI-Relay",
        "msg": "Fenster eng. Keine zweite Runde." }
    ],
    "foreshadow": [
      { "tag": "FS-1", "text": "Ein zweiter Schatten im Kamerafeed.",
        "scene": { "episode": 10, "mission": 4, "index": 7 } },
      { "tag": "FS-2", "text": "Das Wappen am Gürtel – falsche Zeit,
        echter Rang.", "scene": { "episode": 10, "mission": 4, "index": 8 } },
      { "tag": "FS-3", "text": "Der Safe ist leer, aber der Raum ist warm.",
        "scene": { "episode": 10, "mission": 4, "index": 9 } },
      { "tag": "FS-4", "text": "Eine Stimme, die den Namen kennt.",
        "scene": { "episode": 10, "mission": 4, "index": 10 } }
    ],
    "fr_interventions": [
      { "at": "2026-01-14T20:55:00Z", "faction": "Nullmarkt",
        "result": "shadow_help",
        "scene": { "episode": 10, "mission": 5, "index": 9 } }
    ],
    "psi": [
      { "at": "2026-01-14T20:52:00Z", "ability": "psi_action_dummy",
        "psi_heat_delta": 1, "note": "Psi eingesetzt." },
      { "at": "2026-01-14T20:59:00Z", "ability": "psi_heat_reset",
        "psi_heat_delta": -1,
        "note": "Nach Konflikt/HQ-Transfer zurückgesetzt." }
    ],
    "arena_psi": [
      {
        "at": "2026-01-14T21:26:00Z",
        "ability": "phase_strike",
        "base_cost": 1,
        "tax": 1,
        "total_cost": 2,
        "mode": "pvp",
        "arena_active": true,
        "category": "arena_phase_strike",
        "reason": "QA-phase-strike-tax"
      }
    ],
    "flags": {
      "runtime_version": "4.2.5",
      "compliance_shown_today": false,
      "chronopolis_warn_seen": true,
      "chronopolis_unlock_level": 10,
      "chronopolis_unlocked": true,
      "atmosphere_contract": {
        "tone": "covert-ops-technoir",
        "camera": "third_person",
        "hud_density": "standard"
      },
      "hud_scene_usage": {
        "EP10.M4.SC12": 2,
        "EP10.M5.SC0": 1
      },
      "platform_action_contract": {
        "action_mode": "uncut",
        "pattern": "full_scene",
        "loot_policy": "full_loot",
        "body_handling": "protocol"
      },
      "howto_guard_hits": [],
      "last_save_at": "2026-01-14T21:30:00Z",
      "merge_conflicts": [
        {
          "field": "rift_merge",
          "at": "2026-01-14T21:02:00Z",
          "kept": ["RIFT-LOW-0001", "RIFT-MID-0088", "RIFT-HIGH-0501"],
          "overflow": ["RIFT-EXTRA-9001"],
          "handoff_to": ["ITI-NPC-TEAM-DELTA"]
        },
        {
          "field": "wallet",
          "at": "2026-01-14T21:03:00Z",
          "resolution": "union",
          "note": "Wallets zusammengeführt (Dummy)."
        },
        {
          "field": "arena_resume",
          "at": "2026-01-14T21:28:00Z",
          "resolution": "resume_token_written"
        }
      ],
      "self_reflection_auto_reset_completed": true,
      "self_reflection_auto_reset_aborted": true,
      "self_reflection_auto_reset_at": "2026-01-14T20:58:00Z",
      "last_mission_end_reason": "completed",
      "qa_mode": true,
      "qa_profiles": {
        "low": { "lvl": 7, "cluster_hint": "1-25", "seed_id": "RIFT-LOW-0001" },
        "mid": { "lvl": 120, "cluster_hint": "80-150", "seed_id": "RIFT-MID-0088" },
        "high": { "lvl": 512, "cluster_hint": "400-1000", "seed_id": "RIFT-HIGH-0501" },
        "end": { "lvl": 905, "cluster_hint": "400-1000", "seed_id": "RIFT-HIGH-0501" }
      }
    }
  },
  "ui": {
    "gm_style": "verbose",
    "intro_seen": true,
    "suggest_mode": true,
    "action_mode": "uncut",
    "contrast": "high",
    "badge_density": "dense",
    "output_pace": "slow",
    "voice_profile": "gm_third_person",
    "mode_display": "label"
  },
  "arena": {
    "active": false,
    "phase": "idle",
    "mode": "single",
    "match_policy": "sim",
    "previous_mode": null,
    "wins_player": 1,
    "wins_opponent": 0,
    "tier": 2,
    "proc_budget": 2,
    "artifact_limit": 1,
    "loadout_budget": 1,
    "phase_strike_tax": 1,
    "damage_dampener": true,
    "team_size": 2,
    "queue_state": "completed",
    "zone": "safe",
    "fee": 0,
    "scenario": "QA-SIM",
    "started_episode": 10,
    "last_reward_episode": 10,
    "policy_players": ["simulated"],
    "audit": [
      { "at": "2026-01-14T21:25:00Z", "event": "arenaStart", "note": "QA-run" }
    ]
  },
  "arc_dashboard": {
    "offene_seeds": ["RIFT-LOW-0001", "RIFT-MID-0088", "RIFT-HIGH-0501"],
    "fraktionen": {
      "ITI": { "rep": 12, "tier": 2 },
      "Chronopolis": { "rep": -3, "tier": 1 },
      "Nullmarkt": { "rep": 5, "tier": 1 }
    },
    "fragen": [
      { "id": "Q-001", "text": "Wer zieht die Fäden hinter den Seeds?" },
      { "id": "Q-002", "text": "Warum kennt der Relaisfunk Namen, die nie gesendet wurden?" }
    ],
    "timeline": [
      { "at": "2026-01-14T20:33:00Z", "event": "Px=5 → ClusterCreate; Seeds sichtbar." },
      { "at": "2026-01-14T21:10:00Z", "event": "Rift-Op gestartet (Seed RIFT-HIGH-0501)." },
      { "at": "2026-01-14T21:30:00Z", "event": "HQ-Save + Economy-Audit geschrieben." }
    ]
  }
}
```

Lösungsvorschlag

* **Ansatz:** Save als “Roundtrip‑Anker” nutzen: Load → Nullzeit‑Menü → `economy_audit` → Cross‑Mode‑Import → Seed‑Merge → ArenaStart → Save.
* **Risiken:** Dummy‑Daten sind absichtlich teils “out of range” (Audit‑Toast provozieren) – nicht als Balance‑Wunsch missverstehen.

To-do

* **Kodex:** Loader‑Robustheit: unbekannte Zusatzfelder in `logs.flags.qa_profiles` tolerieren; `hud_event`‑Normalizer ergänzt fehlende `at` anhand `last_save_at`.
* **QA:** Import‑Probe: Prüfen, dass `campaign.rift_seeds[]` kanonisch ist und `arc_dashboard.offene_seeds[]` nur spiegelt.

Nächste Schritte

* **Maintainer:innen:** Test‑Save in CI‑Fixture übernehmen (z. B. “qa_save_v6_dummy.json”), damit Regressionen reproduzierbar werden.
* **Notizen:** Wenn du willst, kann der nächste QA‑Pass als “Live‑Run” erfolgen: 1 Core‑Mission (12 Szenen) + 1 Rift‑Casefile (14 Szenen) mit exakt den HUD‑Markers/Traces aus dem Save.

---

1. **Dokument‑Fix‑Sprint:** Rift‑Map + Pre‑City‑Hub Save‑Regel + SaveGuard‑Prio konsolidieren und dann denselben QA‑Pass erneut laufen lassen.
2. **Seed‑Merge‑Determinismus:** Auswahlregel für kept/overflow festlegen, dann “14→12” Regression‑Suite definieren.
3. **Safety‑Review Generatoren:** Objectives outcome‑basiert umformulieren und per Lint‑Regel absichern.

**Freie Aktion:** Sag “Priorität 1/2/3”, oder gib mir eine konkrete Build‑Zielsetzung (z. B. “nur Rift‑Loop & Economy”, “nur Cross‑Mode + Arena”).

Und hier noch der Abgleich vom Speicher json. Das passiert, wenn man ihn in eine frische Instanz kopiert:
`EP 10 · MS 0 · SC 0/12 · PHASE Debrief · MODE CORE · COMMS OK · Px 0/5 · Stress 0/9 · Obj HQ: Nächsten Schritt wählen · Exfil <--`

Das ITI-HQ liegt still wie ein Operationssaal zwischen den Sekunden. Kaltes, sauberes Licht auf Beton, Glas, Stahl. Mara Voss – **VANTA** – steht wieder im Quarzatrium, die Linse fährt das Overlay hoch, der Ohr-Comlink klickt einmal leise in den Sitz. Kein Alarm. Kein Timer. Nur das Summen der Nullzeit-Felder, die alles draußen halten.

Im Hintergrund: drei Schatten an den Rändern der Halle. **DUST** (standby) lehnt am Geländer des oberen Umlaufs, die Hände tief in den Taschen, Blick wach. **KEYSTONE** (active) sitzt auf einer Bank nahe dem Briefingkorridor, die Finger trommeln einen Rhythmus, als würde sie noch Restspannung aus den Nerven drücken. **BLACKTIDE** (standby) steht dort, wo die Kameras sich schneiden – als hätte er die Winkel geplant, bevor er atmet.

Das **Arc-Dashboard** zeigt offene Narben im Zeitstrom – drei Seeds sind **offen**, einer **abgesiegelt**. Die Einträge sind sauber, aber sie stören das Bild wie Kratzer auf Glas: *1912 Nordmeer*, *1969 Küstenstadt*, *2099 Sprawl*. Der letzte Rift-Einsatz hat ein Artefakt in die Logs gespült (*ART-NULLGLASS-01*), und der Audit hat eure Ökonomie markiert: HQ-Pool und Wallets liegen **außerhalb** der Richtwerte für das Band. Keine Sirene – nur ein stilles „im Blick behalten“.

Ein Funklog hängt noch nach: *„Fenster eng. Keine zweite Runde.“* – ITI-Relay. Das ist keine Drohung. Das ist eine Erinnerung.

**Intel / Risiken / Zeitfenster**

* Offene Rift-Seeds: **RIFT-LOW-0001**, **RIFT-MID-0088**, **RIFT-HIGH-0501** (RIFT-CLOSED-0210 ist zu)
* Chronopolis: **freigeschaltet** (Key aktiv; Warnbanner bereits gesehen)
* Arena: zuletzt **completed**, aktuell **idle/safe**
* Ökonomie-Audit: Abweichung erkannt (kein unmittelbarer Lock, aber Konsequenzen bei großen Käufen möglich)

1. **Briefing anfordern (Core-Mission EP10/MS1)** – neues Ziel, neuer Seed, sauberer Start aus dem HQ.
2. **Rift-Board prüfen** – Seeds durchgehen, Prioritäten festlegen, Loadout/Team anpassen (ohne sofortigen Launch).
3. **Chronopolis-Run** – Händler/Services/Research-Sinks, Wallets/HQ-Pool glätten, Gerüchte ziehen.

**Freie Aktion:** Sag, was VANTA im HQ als Nächstes macht (z. B. Team zusammenrufen, Ausrüstung ändern, jemandem eine Frage stellen, Log-Details auf den Tisch ziehen).
```

**Repo-Checks (Pflichtpaket)**

```chatlog
Repo-Agent: `make lint`
Tool: ✅
Repo-Agent: `make test`
Tool: ✅
Repo-Agent: `bash scripts/smoke.sh`
Tool: ✅
Repo-Agent: `python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_doc_links.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_umlauts.py`
Tool: ✅
```

## 2027-03-09 – Repo-Agent – Review Entwurf 2025-12-28 (Phase 1–2 Konsolidierung)
- Plattform: Lokaler Repo-Lauf (Dokumentenprüfung)
- Wissensstand: QA-Fahrplan 1.19.1, Wissensmodule unverändert
- Auftrag: Entwurf „Wissensspeicher 20-Slot-Optimierung“ (2025-12-28) prüfen und
  Konsolidierungs-/Kürzungspotenziale für Phase 1–2 bewerten.

**Entscheidungsblock Phase 1–2 (beibehalten/zusammenführen/streichen)**
- `characters/ausruestung-cyberware.md`: **beibehalten** (Regel- und Legalitätsanker
  sind bereits konsolidiert; weitere Kürzung würde Runtime-Regeln tangieren).
- `systems/kp-kraefte-psi.md`: **beibehalten** (Talente + Kernmechanik zusammen, keine
  redundanten Blöcke für sichere Kürzung).
- `characters/zustaende.md` + `characters/hud-system.md`: **beibehalten** (Split bleibt
  retrieval-klar; Zusammenführung würde HUD-Regeln verwässern).
- `characters/charaktererschaffung-grundlagen.md` +
  `characters/charaktererschaffung-optionen.md`: **beibehalten** (Trennung reduziert
  Komplexität; Kürzung ohne Regelverlust nicht möglich).

**Nachverfolgung**
- QA-Fahrplan: Phase-1–2-Review im Maßnahmenblock ergänzt; keine Zusammenführung/Kürzung
  notwendig.

## 2026-01-09 – Repo-Agent – Beta-GPT Playtest 2026-XX Folgearbeiten (Issues #6–#9)
- Plattform: Lokaler Repo-Lauf (Pflicht-Testpaket)
- Wissensstand: Runtime/README 4.2.5, QA-Fahrplan 1.19.1
- Auftrag: Issues #6–#9 aus dem Maßnahmenpaket „Beta-GPT Playtest 2026-XX“ abschließen
  (Merge-Conflicts-Allowlist, Economy-Audit-Regel, PvP-Policy, HQ-Loop-Contract).

```chatlog
Repo-Agent: `make lint`
Tool: ✅
Repo-Agent: `make test`
Tool: ✅
Repo-Agent: `bash scripts/smoke.sh`
Tool: ✅
Repo-Agent: `python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_doc_links.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_umlauts.py`
Tool: ✅
```

**Feststellungen**
- Merge-Conflicts-Allowlist + Mindestfelder umgesetzt; Beispiele im Gameflow-Modul ergänzt.
- Economy-Audit nutzt Host-Level (Median-Fallback), `band_reason`/`wallet_avg_scope` gespiegelt.
- Arena-Policy (`arena.match_policy`) in Save/HUD dokumentiert;
  HQ-Loop-Contract als Pflichtschablone ergänzt.
- Erstlauf `make lint` wies auf MD013 (Line > 100) im QA-Fahrplan hin;
  behoben und erfolgreich wiederholt.

**Nachverfolgung**
- Commit/PR: HEAD (Branch work; Hash im PR-Text referenziert).
- QA-Fahrplan: Version 1.19.1 mit Issues #6–#9 als erledigt markiert.

## 2026-01-08 – Repo-Agent – Beta-GPT Playtest 2026-XX Folgearbeiten
- Plattform: Lokaler Repo-Lauf (Pflicht-Testpaket)
- Wissensstand: Runtime/README 4.2.5, QA-Fahrplan 1.19.1
- Auftrag: Issues #2, #5 und #10 aus dem Maßnahmenpaket „Beta-GPT Playtest 2026-XX“
  abschließen (Wallet-Beispiel, HUD-SF-Kommandos, Toast-Suppression-Logs).

```chatlog
Repo-Agent: `make lint`
Tool: ✅
Repo-Agent: `make test`
Tool: ✅
Repo-Agent: `bash scripts/smoke.sh`
Tool: ✅
Repo-Agent: `python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_doc_links.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_umlauts.py`
Tool: ✅
```

**Feststellungen**
- Wallet-Beispiel in `core/zeitriss-core.md` ist v6-konform (`wallets{id → {name,balance}}`).
- `!sf off`/`!sf on` dokumentiert, Toasts/Reason-Flags gespiegelt.
- Suppressed-Toasts landen zusätzlich in `logs.hud[]` mit `suppressed:true` und `reason:"budget"`.

**Nachverfolgung**
- Commit/PR: HEAD (Branch work; Hash im PR-Text referenziert).
- QA-Fahrplan: Version 1.19.1 mit erledigten Issues #2, #5, #10.

## 2027-03-08 – Repo-Agent – Allgemeiner Bug-/Optimierungscheck
- Plattform: Lokaler Repo-Lauf (Pflicht-Testpaket)
- Wissensstand: Runtime/README 4.2.5, QA-Fahrplan 1.19.0
- Auftrag: Gesamtcheck auf Bugs, Verständnislücken und Optimierungspotenzial; Statusbericht für
  Folgezyklen erstellen.

```chatlog
Repo-Agent: `make lint`
Tool: ✅
Repo-Agent: `make test`
Tool: ✅
```

**Feststellungen**
- Keine neuen Bugs gefunden; Runtime-Guards, Save-/HUD-Flows und Arena/Chronopolis-Gates weiterhin
  stabil.
- Wissensmodule und QA-Artefakte spiegeln den Laufzeitstand; kein zusätzlicher Mirror nötig.

**Offene Punkte**
- [ ] Optional: Wissensspeicher-20-Slot-Optimierung (Entwurf 2025-12-28) für Phase 1–2 auf
      Konsolidierungsgewinne überprüfen und priorisieren.

**Nachverfolgung**
- QA-Fahrplan 1.19.0: Deepcheck-Kürzel 2027-03-08 ergänzt und mit QA-Log synchronisiert.

## 2027-03-07 – Repo-Agent – Local-Uncut-Paket LM Studio gespiegelt
- Plattform: Lokales Repo-Run (QA-Skripte)
- Wissensstand: Runtime/README 4.2.5, QA-Fahrplan 1.18.0
- Auftrag: Maßnahmenpaket „Local-Uncut & LM-Studio 2026-05“ im Wissensspeicher
  verankern (Sampling-Presets, Kontextprofile, RAG-Trim, Template-Guard) und
  QA-Log/Audit-Stand nachziehen.

```chatlog
Repo-Agent: `make lint`
Tool: ✅
Repo-Agent: `make test`
Tool: ✅
Repo-Agent: `bash scripts/smoke.sh`
Tool: ✅
Repo-Agent: `python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_doc_links.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_umlauts.py`
Tool: ✅
```

**Offene Punkte**
- [x] Keine; alle sieben Issues des Pakets sind im Wissensspeicher gespiegelt.

**Nachverfolgung**
- Commit/PR: HEAD (Branch work; Hash im PR-Text referenziert).
- QA-Fahrplan: Version 1.18.0 führt das Paket als abgeschlossen.

## 2027-03-06 – Repo-Agent – Copy-Paste-QA 2026-12 abgeschlossen
- Plattform: Lokales Repo-Run (QA-Skripte)
- Wissensstand: Runtime/README 4.2.5, QA-Fahrplan 1.15.0
- Auftrag: Abschluss aller Copy-Paste-QA 2026-12-Issues (#1–#11) plus Spiegel in Plan/Docs;
  deterministische Save-/HUD-Zeitmarken und Chronopolis/Arena/Economy-Guards bestätigt.

```chatlog
Repo-Agent: `make lint`
Tool: ✅
Repo-Agent: `make test`
Tool: ✅
Repo-Agent: `bash scripts/smoke.sh`
Tool: ✅
Repo-Agent: `python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_doc_links.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_umlauts.py`
Tool: ✅
```

**Offene Punkte**
- [x] Keine; Copy-Paste-QA 2026-12 vollständig erledigt und im Fahrplan markiert.

**Nachverfolgung**
- Commits: HEAD (Branch work; Hash im PR-Text referenziert).
- QA-Fahrplan: Version 1.15.0 mit Status ✅ für Issues #1–#11.

## 2026-11-10 – Repo-Agent – Finaler Feinschliff (Build 4.2.5)
- Plattform: Lokales Repo-Run (QA-Skripte)
- Wissensstand: Runtime/README 4.2.5, QA-Fahrplan 1.14.0
- Auftrag: Letzter QS-Durchlauf vor Beta-Start; Link-/Markdown-Lints erneut bestätigt und Runtime-
  Header-Check ohne Abweichungen.

```chatlog
Repo-Agent: `npm run lint:links`
Tool: ✅
Repo-Agent: `npm run lint:md`
Tool: ✅
Repo-Agent: `npm run lint:rt`
Tool: ✅
Repo-Agent: `python3 scripts/lint_doc_links.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_umlauts.py`
Tool: ✅
```

**Offene Punkte**
- [x] Keine weiteren QA-Maßnahmen erforderlich; Fahrplan & Audit bleiben unverändert.

**Nachverfolgung**
- Commit/PR: HEAD (Branch work; Hash im PR-Text referenziert).
- QA-Fahrplan: Bestätigt, keine neuen Tasks (Stand 1.14.0).

## 2026-11-09 – Repo-Agent – QA-Hinweise HUD-Budget/QA-Mode gespiegelt (Build 4.2.5)
- Plattform: Lokales Repo-Run (QA-Skripte)
- Wissensstand: Runtime/README 4.2.5, QA-Fahrplan 1.14.0
- Auftrag: Eingebettete QA-/Smoke-Hinweise zu HUD-Budget und QA-Mode aus Runtime-Modulen in die
  Acceptance-/Smoke-Checklisten gespiegelt und Fahrplan-Status geschlossen.

```chatlog
Repo-Agent: `make lint`
Tool: ✅
Repo-Agent: `make test`
Tool: ✅
Repo-Agent: `bash scripts/smoke.sh`
Tool: ✅
Repo-Agent: `python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_doc_links.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_umlauts.py`
Tool: ✅
```

**Offene Punkte**
- [x] QA-Mode-HUD-Hinweise (`toast_suppressed` + HUD-Budget-Snapshot) aus Runtime-Modulen in die
  Acceptance-Smoke-Checkliste übernommen.
- [x] Spiegel im QA-Fahrplan dokumentiert und Task abgeschlossen.

**Nachverfolgung**
- Commit/PR: HEAD (Branch work; Hash im PR-Text referenziert).
- QA-Fahrplan: Wissensmodule QA/Smoke-Scan (2025) abgeschlossen.

## 2026-11-08 – Repo-Agent – Nachcheck Format-/Umstrukturierung (Build 4.2.5)
- Plattform: Lokales Repo-Run (QA-Skripte)
- Wissensstand: Runtime/README 4.2.5, QA-Fahrplan 1.14.0
- Auftrag: Nachcheck nach Abschluss der Formatierungs- und
  Umstrukturierungsrunde; vollständige Regression laut Pflichtsuite.

```chatlog
Repo-Agent: `make lint`
Tool: ✅
Repo-Agent: `make test`
Tool: ✅
Repo-Agent: `bash scripts/smoke.sh`
Tool: ✅
Repo-Agent: `python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_doc_links.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_umlauts.py`
Tool: ✅
```

**Offene Punkte**
- [x] Regression ohne Abweichungen abgeschlossen; keine zusätzlichen Maßnahmen erforderlich.

## 2026-11-05 – Repo-Agent – Copy-Paste-QA 2026-10 Sync (Build 4.2.5)
- Plattform: Lokales Repo-Run (QA-Skripte + Fahrplan-Sync)
- Wissensstand: Runtime/README 4.2.5, QA-Fahrplan 1.14.0
- Auftrag: Copy-Paste-QA-Maßnahmen #6/#7/#9/#11 spiegeln (Suggest-Persistenz, Offline-SaveGuard,
  Currency-Sync, Arena-Merge-Toast) und QA-Artefakte aktualisieren.

```chatlog
Repo-Agent: `make lint`
Tool: ✅
Repo-Agent: `make test`
Tool: ✅
Repo-Agent: `bash scripts/smoke.sh`
Tool: ✅
Repo-Agent: `python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_doc_links.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_umlauts.py`
Tool: ✅
```

**Offene Punkte**
- [x] Copy-Paste-QA #6: Suggest-Persistenz zwischen UI-Flag und `character.modes` sowie HUD-Tag `·
  SUG`
      als deterministische Roundtrip-Kette validiert.
- [x] Copy-Paste-QA #7: Offline-SaveGuard-Strings vereinheitlicht, FAQ/README-Spiegel mit HQ-Sperre
  aktualisiert.
- [x] Copy-Paste-QA #9: `currency_sync`-Trace für Wallet-/Hazard-/Arena-/Markt-Flows im Fahrplan
  dokumentiert.
- [x] Copy-Paste-QA #11: Arena-Merge-Konflikt-Toast + Trace-Dedupe gespiegelt und als abgeschlossen
  markiert.

**Nachverfolgung**
- Commit/PR: aktueller Commit im Branch (Copy-Paste-QA 2026-10 Sync #6/#7/#9/#11).
- QA-Fahrplan: Copy-Paste-QA 2026-10 – Issues #6/#7/#9/#11 auf ✅ gesetzt.

## 2026-11-04 – Repo-Agent – Economy-Audit-Status Sync (Build 4.2.5)
- Plattform: Lokales Repo-Run (QA-Skripte)
- Wissensstand: README v4.2.5, QA-Fahrplan 1.13.34
- Auftrag: Copy-Paste-QA Issue #12 (Chronopolis/Economy-Audit) abschließen und
  QA-Artefakte synchronisieren.

```chatlog
Repo-Agent: `make lint`
Tool: ✅
Repo-Agent: `make test`
Tool: ✅
Repo-Agent: `bash scripts/smoke.sh`
Tool: ✅
Repo-Agent: `python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_doc_links.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_umlauts.py`
Tool: ✅
```

**Offene Punkte**
- [x] Copy-Paste-QA #12 (Economy-Audit) im Fahrplan auf ✅ gesetzt.
- [x] QA-Audit-Update zum Economy-Audit-Trace ergänzt.

**Nachverfolgung**
- Commit/PR: aktueller Commit im Branch (QA-Status Economy-Audit).
- QA-Fahrplan: Copy-Paste-QA 2025-12 – Issue #12 abgeschlossen.

## 2026-11-03 – Repo-Agent – Phase-3-Sync & Vereinheitlichung (Build 4.2.5)
- Plattform: Lokales Repo-Run (QA-Skripte + Stichprobenreview)
- Wissensstand: README v4.2.5, QA-Fahrplan 1.13.32
- Auftrag: 20-Slot-Optimierung Phase 3 abschließen, Vereinheitlichungs-Fahrplan
  Punkte 4/5 dokumentieren.

```chatlog
Repo-Agent: `make lint`
Tool: ✅ (npm warn: Unknown env config "http-proxy")
Repo-Agent: `make test`
Tool: ✅ (npm warn: Unknown env config "http-proxy")
Repo-Agent: `bash scripts/smoke.sh`
Tool: ✅
Repo-Agent: `python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_doc_links.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_umlauts.py`
Tool: ✅
```

**Offene Punkte**
- [x] Phase-3-Sync (Querverweise, Wissensspiegel, QA-Log) geprüft und Fahrplan
  auf ✅ gesetzt.
- [x] Vereinheitlichungs-Review in Core/Gameplay/Systems dokumentiert.

**Nachverfolgung**
- Commit/PR: aktueller Commit im Branch (Phase-3-Sync & Vereinheitlichung).
- QA-Fahrplan: Wissensspeicher 20-Slot-Optimierung Phase 3 abgeschlossen.

## 2025-12-29 – Repo-Agent – Wissensspeicher-20-Slot Phase 2 (Splits)
- Plattform: Lokales Repo-Run (QA-Skripte + Strukturabgleich)
- Wissensstand: README v4.2.5, QA-Fahrplan 1.13.32
- Copy-&-Paste-Auftrag: QA-Fahrplan 2025 – Wissensspeicher 20-Slot-Optimierung Phase 2

```chatlog
Repo-Agent: `make lint`
Tool: ✅ (npm warn: Unknown env config "http-proxy")
Repo-Agent: `make test`
Tool: ✅ (npm warn: Unknown env config "http-proxy")
Repo-Agent: `bash scripts/smoke.sh`
Tool: ✅
Repo-Agent: `python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_doc_links.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_umlauts.py`
Tool: ✅
```

**Offene Punkte**
- [x] Modul 5 in Zustände/HUD getrennt (`characters/zustaende.md`,
  `characters/hud-system.md`).
- [x] Modul 3 in Grundlagen/Optionen getrennt
  (`characters/charaktererschaffung-grundlagen.md`,
  `characters/charaktererschaffung-optionen.md`).
- [x] README, master-index, Toolkit- und Kampagnen-Links sowie Maintainer-Ops
  synchronisiert.

**Nachverfolgung**
- Commit/PR: aktueller Commit im Branch (Wissensspeicher-20-Slot Phase 2).
- QA-Fahrplan: Wissensspeicher 20-Slot-Optimierung (Phase 2 abgeschlossen
  2025-12-29).

## 2025-12-22 – Repo-Agent – Wissensspeicher-20-Slot Phase 1 (Konsolidierung)
- Plattform: Lokales Repo-Run (QA-Skripte + Strukturabgleich)
- Wissensstand: README v4.2.5, QA-Fahrplan 1.13.31
- Copy-&-Paste-Auftrag: QA-Fahrplan 2025 – Wissensspeicher 20-Slot-Optimierung Phase 1

```chatlog
Repo-Agent: `make lint`
Tool: ✅ (npm warn: Unknown env config "http-proxy")
Repo-Agent: `make test`
Tool: ✅ (npm warn: Unknown env config "http-proxy")
Repo-Agent: `bash scripts/smoke.sh`
Tool: ✅
Repo-Agent: `python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_doc_links.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_umlauts.py`
Tool: ✅
```

**Offene Punkte**
- [x] Cyberware/Bioware in `characters/ausruestung-cyberware.md` konsolidiert.
- [x] Psi-Talente in `systems/kp-kraefte-psi.md` gespiegelt und verlinkt.

**Nachverfolgung**
- Commit/PR: aktueller Commit im Branch (Wissensspeicher-20-Slot Phase 1).
- QA-Fahrplan: Wissensspeicher 20-Slot-Optimierung (Phase 1 abgeschlossen 2025-12-22).

## 2026-11-02 – Repo-Agent – Action-Contract-Logging (Build 4.2.5)
- Plattform: Lokales Repo-Run (QA-Skripte + Stil-Review)
- Wissensstand: README v4.2.5, Runtime v4.2.5
- Copy-&-Paste-Auftrag: QA-Fahrplan 2026-10 – Optionale Action-Contract-Logs

```chatlog
Repo-Agent: `make lint`
Tool: ✅ (npm warn: Unknown env config "http-proxy")
Repo-Agent: `make test`
Tool: ✅ (npm warn: Unknown env config "http-proxy")
Repo-Agent: `bash scripts/smoke.sh`
Tool: ✅
Repo-Agent: `python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_doc_links.py`
Tool: ✅
Repo-Agent: `python3 scripts/lint_umlauts.py`
Tool: ✅
```

**Offene Punkte**
- [x] Action-Contract-Logging in Runtime, Save-Schema und Wissensmodulen gespiegelt.

**Nachverfolgung**
- Commit/PR: aktueller Commit im Branch (Ergänze Action-Contract-Logging).
- QA-Fahrplan: Maßnahmenpaket Plattform-Contract Action & Gewalt #6 (Status aktualisiert
  2026-11-02).

## 2026-10-30 – Repo-Agent – Action-Contract-Schalter & Outcome-Guard (Build 4.2.4)
- Plattform: Lokales Repo-Run (QA-Skripte + Stil-Review)
- Wissensstand: Runtime/README/Toolkit 4.2.4, QA-Fahrplan 1.13.29
- Auftrag: Plattform-Contract „Action & Gewalt“ spiegeln, Gewalt-Schalter und
  Outcome-Pattern in Runtime-Docs/Toolkit verankern.

```chatlog
Repo-Agent: `make lint`
Repo-Agent: `make test`
Repo-Agent: `bash scripts/smoke.sh`
Repo-Agent: `python3 tools/lint_runtime.py`
Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
Repo-Agent: `python3 scripts/lint_doc_links.py`
Repo-Agent: `python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] Contract-Memo unter `internal/qa/evidence/` archiviert und verlinkt.
- [x] Actionfilm-Cut/Outcome-Pattern in Toolkit/README verankert.
- [x] Loot-Handling und QA-Checks auf Outcome-only umgestellt.
- [x] Gewalt-Schalter (`modus action|gewalt`) in Runtime, Save-Docs und Toolkit ergänzt.

**Nachverfolgung**
- Evidenz: `internal/qa/evidence/2026-10-plattform-contract-action-gewalt.md`
- QA-Fahrplan: Maßnahmenpaket Plattform-Contract Action & Gewalt 2026-10 (Issues #1–#5).

## 2026-08-15 – Repo-Agent – PvP-Arena MR-Paket Abschluss (Build 4.2.3)
- Plattform: Lokales Repo-Run (QA-Skripte + Stil-Review)
- Wissensstand: Arena-MR-Docs 4.2.3, QA-Fahrplan 1.13.26
- Auftrag: MR-Arena-Feinschliff final prüfen, QA-Fahrplan auf ✅ abschließen.

```chatlog
08:40 Repo-Agent: `make lint`
09:12 Repo-Agent: `make test`
09:38 Repo-Agent: `bash scripts/smoke.sh`
09:55 Repo-Agent: `python3 tools/lint_runtime.py`
09:57 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
09:59 Repo-Agent: `python3 scripts/lint_doc_links.py`
10:01 Repo-Agent: `python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] MR-Terminologie prüfen: keine VR-/Holodeck-Formulierungen, physische Halle.
- [x] Arena-Map-Label „Magnet-Deck A“ und diegetisches HUD (`Halle/Grenze/Zeit/Runde`).
- [x] Beacon-Gitter, Suit-Lock/Med-Scan, Rig-Hardware und Feedback-Intensität verankert.

**Nachverfolgung**
- Commit/PR: aktueller Commit im Branch (docs: arena mr qa abschließen)
- QA-Fahrplan: PvP-Arena Mixed-Reality 2026-08 (Issues #1–#9) abgeschlossen.

## 2025-12-23 – Repo-Agent – Rift-Merge-Cap & QA-Capture (Issues #4/#8/#12) (Build 4.2.3)
- Plattform: Lokales Repo-Run (QA-Skripte)
- Wissensstand: Runtime/README/Toolkit 4.2.3, QA-Fahrplan 1.13.25
- Auftrag: Rift-Merge-Deckelung mit Trace dokumentieren, Boss-DR-Docs/Trace
  konsolidieren, Atmosphere-Contract-Capture in QA-Mode erzwingen.

```chatlog
11:05 Repo-Agent: `make lint`
11:28 Repo-Agent: `make test`
11:49 Repo-Agent: `bash scripts/smoke.sh`
12:05 Repo-Agent: `python3 tools/lint_runtime.py`
12:08 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
12:10 Repo-Agent: `python3 scripts/lint_doc_links.py`
12:12 Repo-Agent: `python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] Rift-Seeds beim Merge auf 12 deckeln; Überschuss geht an ITI-NPC-Teams und
      ist im Trace sichtbar.
- [x] Boss-DR-Doku auf Teamgröße 1–5 konsolidieren; Boss-Typ im Trace spiegeln.
- [x] QA-Mode erzwingt `logs.flags.atmosphere_contract_capture` je Phase mit
      8–12 Zeilen, Banned-Terms-Status und HUD-Toast-Zählung.

**Nachverfolgung**
- Commit/PR: aktueller Commit im Branch (fix: rift merge cap & qa capture)
- QA-Fahrplan: Tester-Playtest 2025-12-XX (Issue #4/#8/#12) abgeschlossen.

## 2025-12-22 – Repo-Agent – HUD-Timestamps & Economy-Audit (Issues #9/#11) (Build 4.2.3)
- Plattform: Lokales Repo-Run (QA-Skripte)
- Wissensstand: SaveFlow/Toolkit/README 4.2.3, QA-Fahrplan 1.13.22
- Auftrag: HUD-Overlay-Timestamps sichern, Economy-Audit-Trace beim HQ-Save ergänzen.

```chatlog
14:05 Repo-Agent: `make lint`
14:25 Repo-Agent: `make test`
14:48 Repo-Agent: `bash scripts/smoke.sh`
15:05 Repo-Agent: `python3 tools/lint_runtime.py`
15:07 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
15:09 Repo-Agent: `python3 scripts/lint_doc_links.py`
15:10 Repo-Agent: `python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] `logs.hud[]`-Events erhalten beim HQ-Save einen ISO-Timestamp, wenn `at` fehlt.
- [x] `economy_audit`-Trace beim HQ-Save ergänzt (Level, HQ-Pool, Wallet-Summe, Richtwerte,
  Chronopolis-Sinks).

**Nachverfolgung**
- Commit/PR: aktueller Commit im Branch (fix: economy audit & hud timestamps)
- QA-Fahrplan: Tester-Playtest 2025-12-XX (Issue #9/#11) abgeschlossen.

## 2025-12-21 – Repo-Agent – Save/Offline/Paradoxon-Konsistenz (Issues #5/#6/#7/#10) (Build 4.2.3)
- Plattform: Lokales Repo-Run (QA-Skripte)
- Wissensstand: Core/README/Toolkit 4.2.3, QA-Fahrplan 1.13.24
- Auftrag: Legacy-Save-Beispiele auf v6 heben, Seed-Gating/Episodenlogik klären,
  Px-Reset im Debrief/HQ spiegeln, Offline-FAQ auf HQ-Uplink trimmen.

```chatlog
09:10 Repo-Agent: `make lint`
09:28 Repo-Agent: `make test`
09:44 Repo-Agent: `bash scripts/smoke.sh`
10:01 Repo-Agent: `python3 tools/lint_runtime.py`
10:03 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
10:05 Repo-Agent: `python3 scripts/lint_doc_links.py`
10:06 Repo-Agent: `python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] Save-Beispiele auf v6-Shape (`party.characters[]`, `logs.*`) aktualisieren.
- [x] Rift-Seeds nach Episodenabschluss spielbar; Arc/Episode-Begriffe trennen.
- [x] Px-Reset im Debrief/HQ bestätigen (`px_reset_pending/confirm`).
- [x] Offline-Konnektivität: HQ immer online, Offline nur im Feld.

**Nachverfolgung**
- Commit/PR: aktueller Commit im Branch (Docs/Runtime-Update Save/Px/Offline).
- QA-Fahrplan: Tester-Playtest 2025-12-XX (Issue #5/#6/#7/#10) abgeschlossen.

## 2025-12-21 – Repo-Agent – Load-Flow Skip-Flags (Issue #3) (Build 4.2.3)
- Plattform: Lokales Repo-Run (QA-Skripte)
- Wissensstand: README/Modul 12/Toolkit 4.2.3, QA-Fahrplan 1.13.22
- Auftrag: Load-Flow ohne Einstiegsauswahl verankern und Wissensmodule spiegeln.

```chatlog
23:05 Repo-Agent: `make lint`
23:10 Repo-Agent: `make test`
23:20 Repo-Agent: `bash scripts/smoke.sh`
23:24 Repo-Agent: `python3 tools/lint_runtime.py`
23:26 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
23:28 Repo-Agent: `python3 scripts/lint_doc_links.py`
23:30 Repo-Agent: `python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] `load_deep()` setzt `campaign.entry_choice_skipped=true` und `ui.intro_seen=true`.
- [x] Modul 12/README/Toolkit spiegeln den Load-Flow ohne Einstiegsauswahl.

**Nachverfolgung**
- Commit/PR: aktueller Commit im Branch (fix: load-flow ohne entry choice)
- QA-Fahrplan: Tester-Playtest 2025-12-XX (Issue #3) abgeschlossen.

## 2025-12-21 – Repo-Agent – PvP-Arena MR-Paket (QA-Vorlauf) (Build 4.2.3)
- Plattform: Lokales Repo-Run (QA-Skripte)
- Wissensstand: Arena MR-Update 4.2.3, QA-Fahrplan 1.13.22
- Auftrag: Pflicht-Testpaket ausführen, QA-Vorlauf für MR-Arena dokumentieren.

```chatlog
12:05 Repo-Agent: `make lint`
12:34 Repo-Agent: `make test`
12:55 Repo-Agent: `bash scripts/smoke.sh`
13:07 Repo-Agent: `python3 tools/lint_runtime.py`
13:10 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
13:12 Repo-Agent: `python3 scripts/lint_doc_links.py`
13:13 Repo-Agent: `python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] PvP-Arena MR-Feinschliff im MyGPT-Beta-Lauf geprüft
      (kein VR/Holo-Vokabular, Shared-Overlay/Beacon, Suit-Lock,
      Magnetfeld-Deck, HUD-Labels). → Abschluss siehe QA-Log 2026-08-15.
- [x] QA-Fahrplan „PvP-Arena Mixed-Reality 2026-08“ nach Live-Probelauf
      auf ✅ abgeschlossen und Log-Referenz ergänzt. → Abschluss siehe QA-Log
      2026-08-15.

**Nachverfolgung**
- QA-Fahrplan 1.13.26: MR-Arena-Paket (Issues #1–#9) abgeschlossen, siehe
  QA-Log 2026-08-15.

## 2026-07-02 – Repo-Agent – Chrononauten-Presets 2026-07 (Build 4.2.3)
- Plattform: Lokales Repo-Run (QA-Skripte)
- Wissensstand: Charaktererschaffung 4.2.3, QA-Fahrplan 1.13.22
- Auftrag: Presets editor-konform machen, Validator ergänzen, QA-Sync.

```chatlog
09:10 Repo-Agent: `make lint`
09:45 Repo-Agent: `make test`
10:20 Repo-Agent: `bash scripts/smoke.sh`
10:28 Repo-Agent: `python3 tools/lint_runtime.py`
10:31 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
10:34 Repo-Agent: `python3 scripts/lint_doc_links.py`
10:36 Repo-Agent: `python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] Start-Archetypen, Schnellstart-Presets und Tutorial auf 18-Punkte-Schema
      mit Rassenmods, Talenten und SYS-Last umgestellt.
- [x] Quick-Build auf Preset-Auswahl gedreht; Unique-Gear ohne Px-Drift.
- [x] Preset-Validator ergänzt und in `make lint` eingebunden.

**Nachverfolgung**
- QA-Fahrplan 1.13.22: Chrononauten-Presets 2026-07 abgeschlossen.

## 2026-05-11 – Repo-Agent – Gameflow-Schema-Format & Fahrplan-Sync (Build 4.2.3)
- Plattform: Lokales Repo-Run (QA-Skripte)
- Wissensstand: QA-Fahrplan 1.13.20
- Auftrag: SaveGame-v6-Schema auf Zeilenlängen prüfen, QA-Fahrplan-Status der
  Gameflow-Review abschließen.

```chatlog
09:05 Repo-Agent: `make lint`
09:22 Repo-Agent: `make test`
09:55 Repo-Agent: `bash scripts/smoke.sh`
10:02 Repo-Agent: `python3 tools/lint_runtime.py`
10:05 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
10:08 Repo-Agent: `python3 scripts/lint_doc_links.py`
10:10 Repo-Agent: `python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] `systems/gameflow/saveGame.v6.schema.json` auf Zeilenlängen bereinigt.
- [x] QA-Fahrplan markiert den Gameflow-Format-Review als abgeschlossen.

**Nachverfolgung**
- QA-Fahrplan 1.13.20: Gameflow-Format-Review abgeschlossen.

## 2026-05-10 – Repo-Agent – High-Level-Regression & Beta-GPT-12 Abschluss (Build 4.2.3)
- Plattform: Lokales Repo-Run (QA-Skripte)
- Wissensstand: README/Modul 12 4.2.3, QA-Fahrplan 1.13.18
- Auftrag: High-Level-Fixture-Hinweis ergänzen, Beta-GPT-12-Plan abschließen,
  Audit und QA-Log synchronisieren.

```chatlog
12:05 Repo-Agent: `make lint`
12:29 Repo-Agent: `make test`
12:36 Repo-Agent: `bash scripts/smoke.sh`
12:40 Repo-Agent: `python3 tools/lint_runtime.py`
12:42 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
12:44 Repo-Agent: `python3 scripts/lint_doc_links.py`
12:45 Repo-Agent: `python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] README benennt `savegame_v6_highlevel.json` als High-Level-Referenz.
- [x] QA-Fahrplan markiert das Beta-GPT-12-Paket als erledigt; Audit gespiegelt.

**Nachverfolgung**
- QA-Fahrplan 1.13.18: Beta-GPT-12-Paket (Issues #1–#9) abgeschlossen.

## 2026-05-09 – Repo-Agent – Arena-SceneCounter/HUD-Overlay (Issue #12) (Build 4.2.3)
- Plattform: Lokales Repo-Run (QA-Skripte)
- Wissensstand: README/Toolkit/runtime 4.2.3, QA-Fahrplan 1.13.16
- Auftrag: Arena-Szenenzähler klären, `scene_overlay()` auf Missionen/Rifts begrenzen und
  Wissensmodule spiegeln.

```chatlog
10:05 Repo-Agent: `make lint`
10:23 Repo-Agent: `make test`
10:55 Repo-Agent: `bash scripts/smoke.sh`
11:06 Repo-Agent: `python3 tools/lint_runtime.py`
11:10 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
11:14 Repo-Agent: `python3 scripts/lint_doc_links.py`
11:17 Repo-Agent: `python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] `scene_overlay()` rendert nur bei `location='FIELD'`; HQ und Arena bleiben ohne Overlay.
- [x] README/Toolkit/Speicher-Modul spiegeln den Arena-Ausschluss des Szenenzählers.

**Nachverfolgung**
- QA-Fahrplan 1.13.16: Issue #12 auf erledigt gesetzt.

## 2025-12-19 – Repo-Agent – Accessibility-Defaults im UI-Block (Issue #5) (Build 4.2.3)
- Plattform: Lokales Repo-Run (QA-Skripte)
- Wissensstand: README/Modul 12 4.2.3, QA-Fahrplan 1.13.17
- Auftrag: Accessibility-Defaults in README und Speichermodul spiegeln, SaveGuard-Text
  an die UI-Normalisierung anpassen.

```chatlog
16:20 Repo-Agent: `make lint`
16:28 Repo-Agent: `make test`
16:33 Repo-Agent: `bash scripts/smoke.sh`
16:36 Repo-Agent: `python3 tools/lint_runtime.py`
16:38 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
16:40 Repo-Agent: `python3 scripts/lint_doc_links.py`
16:41 Repo-Agent: `python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] README und Modul 12 beschreiben Defaults für fehlende Accessibility-Felder.
- [x] SaveGuard-Formulierung auf „normalisierter UI-Block“ vereinheitlicht.

**Nachverfolgung**
- QA-Fahrplan 1.13.17: Issue #5 im Beta-GPT-12-Plan als erledigt markiert.

## 2025-12-19 – Repo-Agent – HQ-Intro Schlusszeile (Issue #10) (Build 4.2.3)
- Plattform: Lokales Repo-Run (QA-Skripte)
- Wissensstand: README/Toolkit/runtime 4.2.3, QA-Fahrplan 1.13.15
- Auftrag: HQ-Kurzintro vervollständigen und Start-Flow spiegeln.

```chatlog
11:05 Repo-Agent: `make lint`
11:22 Repo-Agent: `make test`
11:46 Repo-Agent: `bash scripts/smoke.sh`
11:56 Repo-Agent: `python3 tools/lint_runtime.py`
11:59 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
12:03 Repo-Agent: `python3 scripts/lint_doc_links.py`
12:07 Repo-Agent: `python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] HQ-Kurzintro um die Schlusszeile ergänzt und Start-Dispatcher dokumentiert.

**Nachverfolgung**
- QA-Fahrplan 1.13.15: Issue #10 auf erledigt gesetzt.

## 2026-05-08 – Repo-Agent – Atmosphere-Contract Capture (Issue #6) (Build 4.2.3)
- Plattform: Lokales Repo-Run (QA-Skripte)
- Wissensstand: README/Toolkit/runtime 4.2.3, QA-Fahrplan 1.13.14
- Auftrag: QA-Capture-Flag für Atmosphere-Contract ergänzen, Fixture und
  Wissensmodule spiegeln.

```chatlog
08:05 Repo-Agent: `make lint`
08:21 Repo-Agent: `make test`
08:39 Repo-Agent: `bash scripts/smoke.sh`
08:47 Repo-Agent: `python3 tools/lint_runtime.py`
08:50 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
08:54 Repo-Agent: `python3 scripts/lint_doc_links.py`
08:57 Repo-Agent: `python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] `logs.flags.atmosphere_contract_capture` als optionaler QA-Block ergänzt
      (8–12 Zeilen pro Phase, Banned-Terms PASS/FAIL, HUD-Toast-Zählung).
- [x] Gold-Save-Fixture und Wissensmodule (README/Toolkit/Speicher/Briefing)
      spiegeln den Capture-Block.

**Nachverfolgung**
- QA-Fahrplan 1.13.14: Issue #6 auf erledigt gesetzt.

## 2026-05-07 – Repo-Agent – Mission-5-Load-Snapshot (Issue #3) (Build 4.2.3)
- Plattform: Lokales Repo-Run (QA-Skripte)
- Wissensstand: README/Toolkit/runtime 4.2.3, QA-Fahrplan 1.13.13
- Auftrag: Mission‑5‑Badge‑Snapshot nach Load absichern, Auto‑Reset‑Flags
  (`self_reflection_auto_reset_*`) prüfen, Gate/SF/Boss‑Toast nach Load spiegeln.

```chatlog
08:20 Repo-Agent: `make lint`
08:35 Repo-Agent: `make test`
08:57 Repo-Agent: `bash scripts/smoke.sh`
09:05 Repo-Agent: `python3 tools/lint_runtime.py`
09:08 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
09:12 Repo-Agent: `python3 scripts/lint_doc_links.py`
09:15 Repo-Agent: `python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] Acceptance-Follow-up prüft Mission‑5‑HUD, Gate/SF/Boss‑Toast und
      Auto‑Reset‑Flags nach Save/Load; Logs bleiben stabil.

**Nachverfolgung**
- QA-Fahrplan 1.13.13: Issue #3 auf erledigt gesetzt.

## 2026-05-06 – Repo-Agent – Playtest-Fixes (Issues #2/#5) (Build 4.2.3)
- Plattform: Lokales Repo-Run (QA-Skripte)
- Wissensstand: README/Toolkit/runtime 4.2.3, QA-Fahrplan 1.13.11
- Auftrag: Pflichtcontainer `logs.trace[]`/`logs.arena_psi[]` spiegeln; Sonder-Overlays als
  strukturierte `logs.hud[]`-Events sichern.

```chatlog
08:05 Repo-Agent: `make lint`
08:21 Repo-Agent: `make test`
08:34 Repo-Agent: `bash scripts/smoke.sh`
08:41 Repo-Agent: `python3 tools/lint_runtime.py`
08:45 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
08:50 Repo-Agent: `python3 scripts/lint_doc_links.py`
08:53 Repo-Agent: `python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] QA-Fixture/Testbriefing um `logs.trace[]` und `logs.arena_psi[]` ergänzt;
      Negativtest für fehlendes `logs.arena_psi` ergänzt.
- [x] Sonder-Overlays loggen strukturierte HUD-Events (`vehicle_clash`,
      `mass_conflict`) inkl. Parser-Normalisierung.

**Nachverfolgung**
- QA-Fahrplan 1.13.11: Issues #2/#5 erledigt, Audit-Sync dokumentiert.

## 2026-05-05 – Repo-Agent – Arena-SaveGuard (Queue-State) (Build 4.2.3)
- Plattform: Lokales Repo-Run (QA-Skripte)
- Wissensstand: README/Toolkit/runtime 4.2.3, QA-Fahrplan 1.13.10
- Auftrag: SaveGuard blockiert HQ-Saves bei `queue_state != idle`, Arena-Queue
  nach Abschluss auf `idle`, QA-Fixture spiegeln.

```chatlog
07:10 Repo-Agent: `make lint`
07:24 Repo-Agent: `make test`
07:36 Repo-Agent: `bash scripts/smoke.sh`
07:44 Repo-Agent: `python3 tools/lint_runtime.py`
07:48 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
07:52 Repo-Agent: `python3 scripts/lint_doc_links.py`
07:56 Repo-Agent: `python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] SaveGuard blockiert nicht-idle Queue-States; Arena-Queue wird im HQ auf
      `idle` normalisiert.
- [x] QA-Fixture und Wissensmodule (README/Toolkit/Speicher-Modul) gespiegelt.

**Nachverfolgung**
- QA-Fahrplan 1.13.10: Issue #4 auf erledigt gesetzt (Arena-SaveGuard-Regel).

## 2026-05-04 – Repo-Agent – QA-Fahrplan 1.13.6 Konsistenzlauf (Build 4.2.3)
- Plattform: OpenAI MyGPT (Beta-Klon)
- Wissensstand: README/Toolkit/runtime 4.2.3, QA-Fahrplan 1.13.6
- Auftrag: Fahrplan-Statusangaben harmonisieren, abgeschlossene Maßnahmenpakete als geschlossen
  kennzeichnen und QA-Log/Versionierung spiegeln.

```chatlog
07:05 Repo-Agent: `make lint`
07:22 Repo-Agent: `make test`
07:49 Repo-Agent: `bash scripts/smoke.sh`
08:03 Repo-Agent: `python3 tools/lint_runtime.py`
08:07 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
08:11 Repo-Agent: `python3 scripts/lint_doc_links.py`
08:13 Repo-Agent: `python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] Fahrplan-Version 1.13.6 dokumentiert den Abschluss der Pakete 2026-01 bis 2026-04 samt
      konsistenter Statusangaben.

**Nachverfolgung**
- QA-Fahrplan und QA-Log wurden synchronisiert, Commit/PR verweisen auf diesen Konsistenzlauf.

## 2026-05-03 – Repo-Agent – HUD-Limit-Rollback & Atmosphere-Contract (Build 4.2.3)
- Plattform: OpenAI MyGPT (Beta-Klon)
- Wissensstand: README/Toolkit/runtime 4.2.3, QA-Fahrplan 1.13.5
- Auftrag: HUD-Limit-Deckelung zurücknehmen, HUD-Zählung unverändert lassen,
  Atmosphere-Contract-Test beibehalten und Wissensmodule synchron halten.

```chatlog
07:10 Repo-Agent: `node tools/test_atmosphere_contract.js`
07:15 Repo-Agent: `make lint`
07:25 Repo-Agent: `make test`
07:36 Repo-Agent: `bash scripts/smoke.sh`
07:44 Repo-Agent: `python3 tools/lint_runtime.py`
07:49 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
07:55 Repo-Agent: `python3 scripts/lint_doc_links.py`
08:00 Repo-Agent: `python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] HUD-Limit-Sperre entfernt: HUD zählt pro Szene weiter, aber blockiert
      keine optionalen Toasts; Trace- oder Limit-Notizen entfallen.
- [x] Dokumentationsspiegel in HUD-/Toolkit-Modulen bereinigt.

**Nachverfolgung**
- QA-Fahrplan: Version 1.13.5 ohne HUD-Limit-Sperre.
- Commit/PR: verweist auf HUD-Limit-Rollback + QA-Pflichttests (siehe Chatlog).

## 2026-05-01 – Repo-Agent – Atmosphere-Contract-Regression (Build 4.2.3)
- Plattform: OpenAI MyGPT (Beta-Klon)
- Wissensstand: README/Toolkit/runtime 4.2.3, QA-Fahrplan 1.13.3
- Auftrag: Atmosphere-Contract-Regression Start/Load (HUD-Usage-Reset, Voice-Lock,
  Mode-Preset, Banned-Terms) und npm-Pflichttest-Integration.

```chatlog
03:10 Repo-Agent: `npm run test:atmosphere`
03:10 Tool: `atmosphere-contract-start-ok`
03:11 Tool: `atmosphere-contract-load-ok`
```

**Offene Punkte**
- [x] QA-Fahrplan 1.13.3 spiegelt den Atmosphere-Contract-Test im Pflichtpaket.
- [x] Atmosphere-Contract-Block (`logs.flags.atmosphere_contract`) enthält HUD-Usage-
      Reset, Voice-Lock, Mode-Preset und Banned-Terms; keine Restabweichungen.

**Nachverfolgung**
- Commit/PR: wird mit diesem Branch verknüpft (Atmosphere-Contract-Regression).
- QA-Fahrplan: Version 1.13.3, Maßnahmenpaket 2026-05 vollständig dokumentiert.

## 2025-12-19 – Repo-Agent – Economy-Scaling & Gold Save (Issues #7/#8) (Build 4.2.3)
- Plattform: Lokales Repo-Run (QA-Skripte)
- Wissensstand: README/Toolkit/runtime 4.2.3, QA-Fahrplan 1.13.12
- Auftrag: Economy-Scaling-Brücke (Rewards→Wallet-Richtwerte 400+),
  Chronopolis-Sinks dokumentieren, QA-Pfad Lvl 120/512/900+ fixieren und
  Gold-Save-Fixture aktualisieren.

```chatlog
09:10 Repo-Agent: `make lint`
09:26 Repo-Agent: `make test`
09:48 Repo-Agent: `bash scripts/smoke.sh`
09:55 Repo-Agent: `python3 tools/lint_runtime.py`
09:57 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
10:00 Repo-Agent: `python3 scripts/lint_doc_links.py`
10:02 Repo-Agent: `python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] Wallet-Richtwerte 400+ + Chronopolis-Sinks in `cu_waehrungssystem.md`
      ergänzt; QA-Briefing benennt Level 120/512/900+ als Prüfanker.
- [x] Gold-Save-Fixture (`savegame_v6_full.json`) erweitert um
      `logs.flags.atmosphere_contract` und `hud_scene_usage`.

**Nachverfolgung**
- QA-Fahrplan 1.13.12: Issues #7/#8 erledigt.
- Commit/PR: wird im PR referenziert.

## 2025-12-19 – Repo-Agent – Playtest-Fixes (Issues #1/#9/#11) (Build 4.2.3)
- Plattform: Lokales Repo-Run (QA-Skripte)
- Wissensstand: README/Toolkit/runtime 4.2.3, QA-Fahrplan 1.13.9
- Auftrag: Dispatcher-Fehlertext „gruppe 3“ harmonisieren, Scene-Overlay im HQ
  unterdrücken (Charaktererstellung), Handgelenk-Default streichen.

```chatlog
08:10 Repo-Agent: `make lint`
08:22 Repo-Agent: `make test`
08:38 Repo-Agent: `bash scripts/smoke.sh`
08:45 Repo-Agent: `python3 tools/lint_runtime.py`
08:46 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
08:47 Repo-Agent: `python3 scripts/lint_doc_links.py`
08:48 Repo-Agent: `python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] Dispatcher-String `gruppe 3` harmonisiert (README/Toolkit/QA-Briefing).
- [x] Scene-Overlay nur noch in Missionen/Rifts; HQ/Charaktererstellung ohne
      Szenenzähler (Runtime + Speicher-Doku + Acceptance-Fixtures).
- [x] Handgelenk-Default als Legacy markiert, Hardware-Anker bleiben erhalten.
- [x] Arena-SceneCounter/HUD-Overlay: Prüfen, ob PvP-Arena einen Szenenzähler
      benötigt und wie `scene_overlay()` im Arena-Flow eingesetzt werden soll
      (Korrigiert am 2026-05-09; siehe Eintrag „Arena-SceneCounter/HUD-Overlay“).

**Nachverfolgung**
- QA-Fahrplan 1.13.8 markiert Issues #1/#9/#11 als erledigt.

## 2025-12-03 – Maintainer – Testprompt Voll-Lauf (Solo/Koop/Arena)
- Plattform: Beta-GPT (simulativ, Speicher- und HUD-Flows)
- Wissensstand: `runtime.js` 4.2.2, README/Toolkit Stand 2025-12-02,
  QA-Fahrplan 1.9.1
- Auftrag: Gesamter QA-Testprompt inkl. Save/Load, Solo, Solo+NPC, Koop,
  Arena/PvP und Acceptance-Smoke (1–15) mit Mission-5-Badge-Check; Deltas für
  Badge-Dichte, Offline-Logs und Acceptance-Mirror sammeln.

**Teststrecke (simulativ, HUD/Saves)**
- Solo Core (EP 01, MS 01/04/10) sowie Mini-Boss-Check M5: HUD-Badges (`GATE`,
  `FS`, `SF`) und Px/Cluster-Lauf überprüft; Save-v6-Beispiel mit
  vollständigen Pflichtblöcken geliefert.
- Solo + NPC-Squad (MS 02/05) und Koop-Starts (`gruppe schnell`, Mid-Session-
  Merge) mit Wallet-Split und Funk-Logs; Cross-Mode Save-Load erfolgreich.
- Rift- und PvP-Pfade: Arena-Start blockiert HQ-Saves, Phase-Strike-Tax wird in
  `logs.psi[]` protokolliert; Chronopolis-Vorschau ohne Markt-Zugriff bleibt
  save-kompatibel.
- Acceptance-Smoke 1–15 durchlaufen; Accessibility-Persistenz (`contrast: high`,
  `badge_density: compact`, `output_pace: slow`) bestätigt, aber Enum-Drift und
  Offline-Feldnamen fallen auf.

**Issue-Blöcke (Übergabe an Fahrplan/Audit)**
1. **Badge-Dichte/Output-Pace Enum-Drift.** Save-Schema nennt `full|minimal`,
   Accessibility-Dialog `standard|dense|compact`, Toolkit/Runtime akzeptieren
   `full|compact|minimal`. Kanonische Liste fehlt, Migration `full→standard`
   erforderlich.
2. **Offline-Hilfe Feldnamen.** Toolkit nutzt `logs.flags.offline_help_last_scene`,
   Save-Mirror nur `offline_help_last`; Feldabdrift gefährdet Debrief-Spiegel.
3. **Acceptance-Smoke-Mirror (11–15).** Dispatcher/README müssen die vollständige
   15er-Liste explizit führen (Boss-Gate/SF/SUG, Psi-Heat, Accessibility,
   Arena-Add-ons), damit GPTs ohne QA-Dokument alle Schritte abdecken.

**Nachverfolgung**
- Fahrplan/Audit: Neues Maßnahmenpaket 2025-12-03 mit Issues #1–#3 anlegen,
  Status = offen.
- README/DOC/Schema: Badge-Dichte/Tempo-Enums vereinheitlichen und Save/Migration
  dokumentieren; Offline-Hilfe-Feldnamen harmonisieren.
- Acceptance-Mirror: Nummerierte Liste 1–15 im Runtime-Set verankern.

## 2025-12-02 – Maintainer – Testprompt Px-/Acceptance-Folgelauf
- Plattform: Beta-GPT (simulativer Lauf, kein `runtime.js`-Eval)
- Wissensstand: `runtime.js` 4.2.2, README/Toolkit Stand 2025-11-26,
  QA-Fahrplan 1.8.8, QA-Audit Update 2025-11-26
- Auftrag: Testprompt-Run mit Solo/Koop/PvP-Szenen, Px-Regression
  dokumentieren, neue Acceptance- und Save-Deltathemen sammeln.

**Teststrecke (simulativ)**
- Solo London-Arc („Chrono Heist“) mit Fail-Forward: Px steigt trotz Patzer,
  soll laut Regelwerk sinken; PvP als regulärer Spielteil bestätigt.
- Solo + NPC-Team („GLASLÄUFER“), Koop-Fortsetzung, PvP-Arena („Phase-Strike")
  und Mission 5 Badge-Check erneut durchgespielt; ausführliches Save-JSON
  geliefert.

**Offene Punkte (neues Maßnahmenpaket 2025-12-02)**
- [x] Px-Balancing: Schlechtes Spielen muss Px senken, gutes Spielen erhöhen.
- [x] Acceptance-Smoke 15er-Liste im Laufzeit-Set spiegeln
      (nicht nur externes QA-Dokument).
- [x] `select_state_for_save()`-Pseudocode auf Save-v6 Pflichtfelder heben
      (inkl. `arena`, `arc_dashboard`, `economy.wallets{}`, vollständige Logs).
- [x] Wallet-Init-Begriff vereinheitlichen
      (`initialize_wallets_from_roster()` statt gemischter Aliase).
- [x] Self-Reflection-Quelle klären (Charakterwert vs. Flag-Historie) und HUD
      an das Charakterfeld binden.
- [x] Arena-SaveGuard: dokumentieren, dass `arenaStart()` `location` setzt und
      Saves mit aktivem `arena.active` blockiert.
- [x] `!accessibility`-Dialog exemplarisch beschreiben (Optionen → JSON-Mapping).
- [x] Gruppensaves: Legacy `team.members[]` nur als Migration, produktiv nur
      `party.characters[]` zeigen.
- [x] Suggest-Modus vs. Self-Reflection entkoppeln, Badges getrennt erläutern.
- [x] Markt-Log-Limit (24 Einträge) im Speicher-Modul explizit nennen.
- [x] PvP-Arena als optionales Endgame-Feature im README kennzeichnen.

**Nachverfolgung**
- Fahrplan/Audit: neues Maßnahmenpaket 2025-12-02 aufnehmen, Status = offen.
- Commit/PR: folgt nach Dokumentations-Sync.

## 2025-11-26 – Maintainer – Simulativer Acceptance-/Save-Lauf
- Plattform: Beta-GPT (simulativer Lauf, kein `runtime.js`-Eval)
- Wissensstand: `runtime.js` 4.2.2, README/Toolkit Stand 2025-11-06,
  QA-Fahrplan 1.8.8, QA-Audit Update 2025-11-06
- Auftrag: Neuestes Testprotokoll (Solo, Koop, PvP, Mission-5-Badge-Check)
  aus Maintainer-Chat in QA-Struktur spiegeln und Fahrplan-Issues
  einsortieren.

**Teststrecke (simulativ, HUD/Saves nach Spezifikation)**
- Solo Core-Op Frühphase (EP 01, MS 01, „Chrono Heist“, ARGOS als Gegenspieler),
  Px-Tracker und SaveGuard geprüft; Fail-Forward erhöht den Stress/TEMP,
  lässt den Px-Index regelkonform stagnieren (kein Px-Anstieg).
- Solo Core-Op Midgame (EP 04, „FALKENSTEIN NACHTJAGD“): Jammer-Phase mit
  `COMMS:jam`, Offline-Fallback und Px 3/5 via TEMP>7.
- Endgame Chronopolis & Rift: `chronopolis_warn_seen=true`, Marktstock via
  `!chrono stock`, Px5→`ClusterCreate()` Seeds #011/#015, Rift-Op HUD mit TTL
  und Rank-Spiegel.
- Solo + NPC-Squad: Start über `npc-team 2`, Callouts/Fail-Forward markiert,
  Save-Handling über `party.characters[]`/`team.members[]` beschrieben.
- Koop (Merge zweier Solos): Wallet-Split 600 CU → 2×300 CU, Accessibility
  Persistenz (`contrast=high`, `badge_density=compact`, `output_pace=slow`).
- PvP/Arena: `arenaStart({teamSize:2, mode:'squad'})`, SaveGuard blockiert HQ-
  Saves; Cross-Mode-Laderisiko notiert.
- Mission 5 Badge-Check (Gate 2/2, SF-OFF, FS 0/4): HUD-Hoffnung,
  Boss-DR-Toast erwartet; Auto-Reset auf `SF-ON` gefordert.
- Acceptance-Smoke (15 Punkte) per README-Dispatcher-Summary durchgegangen;
  Abweichungen in Issues erfasst.

**Save-Abgleich**
- Maintainer-Save (v6) geprüft: vollständige Pflichtfelder (`economy.wallets{}`
  inkl. Split, `logs.*`, `ui`, `arena`, `arc_dashboard.offene_seeds[]`,
  Foreshadow-Tokens) vorhanden; Mission 5 HUD-Header mit `GATE 2/2` und
  `SF-OFF` geloggt.

**Issue-Blöcke (Übergabe an Fahrplan/Audit)**
1. Self-Reflection Auto-Reset nach Mission 5 nur beschrieben, kein Save-
   Beispiel/Toast (`self_reflection_auto_reset_*`, Debrief-Text) –
   Dokumentationslücke.
2. Arena/PvP Cross-Mode-Laden unklar (Arena-Flags bleiben nach `load_deep()`
   aktiv, obwohl `location='HQ'`).
3. Acceptance-Smoke-Checkliste fehlt im Runtime-Wissensspiegel; nur README-
   Verweis vorhanden.
4. Foreshadow-Gate-Badge uneinheitlich beschrieben (Mission 5/10 zeigt `GATE`
   bereits bei 0/2? HUD-Text widersprüchlich).
5. Suggest-Modus (`modes`-Liste) ohne Save-Beispiel; Persistenz/Bedeutung
   vs. `ui.gm_style` unklar.
6. Chronopolis-Warnung (`chronopolis_warn_seen`) narrativ kaum erklärt; kein
   Beispiel-HUD/Popup.
7. HQ-only SaveGuard: fehlendes Story-Beispiel für Abbruch ohne HQ-Save
   (Gear-Hand-over, Debrief-Toast).
8. Array-only Gruppen-Save (reines JSON-Array) – Migration zu
   `party.characters[]`/`economy.wallets{}` nur textlich erwähnt, kein Beispiel.
9. Psi-Heat-Reset: Erwartung HQ=0 dokumentiert, aber Konflikt-Reset/HUD-Toast
   nicht als Save-Guard beschrieben.

```shell
# Review-Lauf – keine Runtime-Änderungen, nur QA-Spiegel
```

**Nachverfolgung**
- QA-Fahrplan 1.8.8 führt neues Maßnahmenpaket (Issues #1–#9) und Deepcheck-
  Tabelle fort.
- Audit erhält Update 2025-11-26 mit Verweis auf diesen Logeintrag und die
  offenen Maßnahmen.

## 2025-11-06 – Repo-Agent – Regressionsevidenz Maßnahmen #13–#20
- Plattform: Lokale CI-Simulation (Doc- & Runtime-Review)
- Wissensstand: `runtime.js` 4.2.2, README/Toolkit Stand 2025-11-05,
  QA-Fahrplan 1.8.7, QA-Audit Update 2025-11-05
- Auftrag: Regressionseinträge für Audit-Maßnahmen #13–#20 nachtragen und
  Laufzeit-/Dokumentationsspiegel prüfen.

**Maßnahmen**
1. Chronopolis-Stock-Gating (#13) gegen `runtime.js` `chronopolis_daily_stock()`
   und README §ITI-HQ abgeglichen – Dienstgrad- und Research-Gates, tägliche
   Rotation sowie Film-Slots bleiben aktiv; Lognotiz erstellt.
2. Remote-Hack-/Signalspace-Guards (#14) über `comms_check()` und
   `/help comms` geprüft – Remote-Hacks fordern aktive Hardware und blocken bei
   fehlender Verbindung; Audit-Referenz ergänzt.
3. Urban Quick-Card (#15) im Toolkit (`/help urban`) ausgelöst – Deckungsstufen,
   Verfolgungswürfe und HUD-Tags erscheinen vollständig; README verweist auf die
   Schnellhilfe.
4. HQ-Moments & Buff-Icons (#16) anhand Toolkit-Modul „HQ Moments“ sowie HUD
   `hq_buff_icons` nachgestellt – Buff-Wiederholungen werden geblockt,
   Dispatcher-Notiz aktualisiert.
5. Rift-Boss-Loot-Automation (#18) über Makro `on_rift_boss_down()` nachvollzogen
   – Legendary-Wurf, Para-Loot-Markierung und Log-Snippets feuern konsistent.
6. Charaktercap-/Prestige-Hinweise (#19) in `core/zeitriss-core.md` und
   Runtime-Flag `prestige_cap_notice` bestätigt – Cap 10 + Prestigehinweise
   stehen prominent.
7. Arena-Großteam-Timer & Limits (#20) im Arena-HUD (`arena_grossteam_cycle`)
   geprüft – 30s-Takt, Move-Limits und HUD-Countdown werden gesetzt.

```shell
# Review-Lauf – keine neuen Builds notwendig
```

**Nachverfolgung**
- QA-Audit verweist auf diesen Eintrag und streicht die Platzhalter „QA-Log
  folgt“ für Maßnahmen #13–#20.
- QA-Fahrplan aktualisiert die Referenzspalte der Maßnahmenübersicht auf diesen
  Regressionseintrag.

## 2025-11-05 – Repo-Agent – QA-Evidenz-JSON-Handshake
- Plattform: Maintainer-Export (Beta-GPT Testprompt JSON + ZEITRISSchat Abgleich)
- Wissensstand: `runtime.js` 4.2.2, README/Toolkit Stand 2025-11-04,
  QA-Fahrplan 1.8.7, Evidenzprotokoll 0.2.0
- Auftrag: Neue Maintainer-Pipeline (JSON-Block aus dem Testprompt,
  Abgleich via zweiter ZEITRISS-Instanz) dokumentieren, QA-Evidenz-Checkboxen
  in Log und Audit schließen und Evidenzprotokoll spiegeln.

**Maßnahmen**
1. Maintainer-Evidenzen (HUD-/Save-/Wallet-/Arena-Traces) aus dem
   JSON-Hand-off des Beta-GPT Testprompts übernommen und in
   `internal/qa/evidence/2025-beta-gpt-evidenz.md` abgelegt.
2. QA-Log-Einträge 2025-07-05, 2025-07-18, 2025-10-15 und 2025-10-28
   aktualisiert: Checkboxen „QA-Referenzen“ auf ✅ gesetzt und Kurznotizen zum
   neuen JSON-Spiegel ergänzt.
3. Audit-Abschnitte zu den genannten Läufen angepasst; Evidenzstatus auf
   „vorhanden“ gesetzt und auf das aktualisierte Evidenzprotokoll verwiesen.

```shell
# keine Builds – reiner Dokumentations-Abgleich
```

**Nachverfolgung**
- QA-Fahrplan 1.8.7 verweist auf das Evidenzprotokoll Version 0.2.0 und den
  JSON-Hand-off-Prozess.
- Audit führt ein Update 2025-11-05 mit Verweis auf das Evidenz-JSON ein und
  markiert die Maintainer-Lieferung als abgeschlossen.

## 2025-11-04 – Repo-Agent – Deepcheck-Fortsetzung & Fahrplan 1.8.7
- Plattform: Lokale CI-Simulation
- Wissensstand: `runtime.js` 4.2.2, README/Toolkit Stand 2025-11-02,
  QA-Fahrplan 1.8.6 → 1.8.7
- Auftrag: Deepcheck-Tabelle mit QA-Log 2025-11-03/04 synchronisieren,
  Audit-Notiz anpassen und Wissensmodule auf QA-Hinweise prüfen.

**Maßnahmen**
1. QA-Fahrplan (`internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md`) auf Version 1.8.7
   gehoben und die Deepcheck-Tabelle um die Sessions vom 2025-11-03 und
   2025-11-04 ergänzt, damit Plan und QA-Log identische Referenzen führen.
2. QA-Audit (`internal/qa/audits/ZEITRISS-qa-audit-2025.md`) um eine Kurznotiz
   erweitert, die den neuen Deepcheck-Lauf dokumentiert und auf dieses Log
   verweist.
3. Wissensmodule (README, Toolkit, Systems-Module) stichprobenartig geprüft –
   keine QA-Prüfanweisungen gefunden; Laufzeitinhalte bleiben unverändert.

```shell
make lint
make test
bash scripts/smoke.sh
python3 tools/lint_runtime.py
GM_STYLE=verbose python3 tools/lint_runtime.py
python3 scripts/lint_doc_links.py
python3 scripts/lint_umlauts.py
```

**Ergebnisse**
- Pflicht-Testpaket bleibt grün; Linter, Smoke- und Node-Tests bestätigen den
  unveränderten Runtime-Stand.

**Nachverfolgung**
- QA-Fahrplan Version 1.8.7 verweist auf diesen Logeintrag.
- Audit führt die Deepcheck-Fortsetzung als Update 2025-11-04 und bleibt damit
  mit Fahrplan und QA-Log synchron.

## 2025-11-03 – Repo-Agent – QA-Fahrplan 1.8.6 Sync & Wissensmodule-Check
- Plattform: Lokale CI-Simulation
- Wissensstand: `runtime.js` 4.2.2, README/Toolkit Stand 2025-11-02,
  QA-Fahrplan 1.8.6
- Auftrag: QA-Fahrplan 2025 laut Planabschnitt „Pflege & Reporting“ prüfen,
  Deepcheck-Tabelle mit QA-Log-Einträgen 2025-11-01/02 synchronisieren und
  Wissensmodule auf verbleibende QA-Anweisungen sichten.

**Maßnahmen**
1. QA-Fahrplan (`internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md`) auf Version 1.8.6
   gehoben und die Deepcheck-Tabelle um die Läufe vom 2025-11-01 und 2025-11-02
   ergänzt, damit Fahrplan, Audit und QA-Log dieselben Referenzen führen.
2. README, Toolkit und Systems-Module stichprobenartig geprüft – keine
   verbliebenen QA-Prüfanweisungen im produktiven Wissensspiegel gefunden;
   Laufzeitinformationen bleiben unverändert.
3. QA-Log (dieser Eintrag) dokumentiert Spiegel und Tests, damit die
   Pflege-Vorgabe aus dem QA-Fahrplan erfüllt ist.

```shell
make lint
make test
bash scripts/smoke.sh
python3 tools/lint_runtime.py
GM_STYLE=verbose python3 tools/lint_runtime.py
python3 scripts/lint_doc_links.py
python3 scripts/lint_umlauts.py
```

**Ergebnisse**
- `make lint` bestätigt Markdownlint, Runtime-Linter, Doc-Link- und Umlaut-Checks
  ohne Beanstandungen.
- `make test` läuft fehlerfrei; keine Regressionen in Dispatcher- oder Save-Tests.
- Zusatzläufe (`scripts/smoke.sh`, Runtime-Linter direkt) melden keine Abweichung;
  Doc-Link- und Umlaut-Prüfungen bleiben grün.

**Nachverfolgung**
- QA-Fahrplan Version 1.8.6 verweist auf diesen Logeintrag und spiegelt die
  Deepchecks bis 2025-11-02.
- Keine weiteren Aktionen erforderlich; Wissensmodule bleiben QA-neutral
  formuliert.

## 2025-11-02 – Repo-Agent – Wissensmodule entschlackt
- Plattform: Lokale CI-Simulation
- Wissensstand: `runtime.js` 4.2.2, README/Toolkit Stand 2025-11-02,
  QA-Fahrplan 1.8.5
- Auftrag: QA-Fahrplan-Vorgabe „Wissensmodule ohne störende QA-Anweisungen“
  überprüfen und verbleibende Hinweise in den Laufzeitmodulen neutralisieren.

**Maßnahmen**
1. README-Schnellstart aktualisiert: Self-Reflection-Block erklärt den Toggle vor
   Mission 5 ohne Verweis auf Acceptance-Schritte, Fokus liegt auf HUD/Overlay.
2. Dispatcher-Abschnitt betont, dass die 15-Schritte-Liste optional im
   Dispatcher-Briefing liegt; Quick-Hilfe-Abschnitt verweist nur noch bei Bedarf
   auf den vollständigen manuellen Check.
3. Laufzeitwissen bleibt unverändert, weitere Module enthielten keine
   störenden QA-Instruktionen.

```shell
make lint
make test
bash scripts/smoke.sh
python3 tools/lint_runtime.py
GM_STYLE=verbose python3 tools/lint_runtime.py
python3 scripts/lint_doc_links.py
python3 scripts/lint_umlauts.py
```

**Nachverfolgung**
- README bündelt weiterhin alle Laufzeitabläufe ohne QA-Sprech.
- QA-Fahrplan-Ziel „Wissensmodule entschlackt“ bleibt erfüllt.

## 2025-11-01 – Repo-Agent – Deepcheck-Sync & Fahrplan 1.8.5
- Plattform: Lokale CI-Simulation
- Wissensstand: `runtime.js` 4.2.2, README/Toolkit Stand 2025-10-31,
  QA-Fahrplan 1.8.5
- Copy-&-Paste-Auftrag: QA-Fahrplan-Deepchecks mit QA-Log-Einträgen der
  letzten Oktoberwoche synchronisieren und Version 1.8.5 dokumentieren.

**Maßnahmen**
1. Fahrplan-Deepcheck-Tabelle um die Beta-GPT-Deltas vom 2025-10-28 und die
   drei Folge-Syncs (Wissensspiegel, QA-Artefakte, Wissensmodule) erweitert,
   damit Audit, Fahrplan und QA-Log dieselbe Chronologie führen.
2. Version des Fahrplans auf 1.8.5 angehoben und Verweise auf die jeweiligen
   QA-Log-Sektionen ergänzt.
3. Wissensmodule unverändert gelassen – keine neuen QA-Anweisungen in
   Runtime-Dokumenten, Spiegelpflicht bleibt erfüllt.

```shell
make lint
make test
bash scripts/smoke.sh
python3 tools/lint_runtime.py
GM_STYLE=verbose python3 tools/lint_runtime.py
python3 scripts/lint_doc_links.py
python3 scripts/lint_umlauts.py
```

**Nachverfolgung**
- QA-Fahrplan 1.8.5 markiert die Deepcheck-Synchronität zwischen Log und
  Maßnahmenübersicht.
- Weitere Nachweise nicht erforderlich; Laufzeitspiegel blieb unverändert.

## 2025-10-31 – Repo-Agent – Wissensmodule von QA-Artefakten befreit
- Plattform: Lokale CI-Simulation
- Wissensstand: `runtime.js` 4.2.2, README/Toolkit Stand 2025-10-31,
  QA-Fahrplan 1.8.4
- Copy-&-Paste-Auftrag: QA-Fahrplan „Dokumentation & Index“ aufräumen,
  QA-Verweise aus Wissensmodulen und `master-index.json` entfernen.

**Maßnahmen**
1. README Dokumenten-Landkarte verschlankt und den QA-Block entfernt, damit die
   Wissensmodule ausschließlich runtime-relevante Inhalte führen.
2. `master-index.json` von QA-Artefakt-Modulen bereinigt, damit der
   Wissensspeicher nur Runtime-Dokumente lädt.
3. QA-Fahrplan auf Version 1.8.4 aktualisiert und den neuen Status zur
   Dokumentation festgehalten.

```shell
make lint
```

**Nachverfolgung**
- QA-Fahrplan 1.8.4 hält den schlanken Dokumentationsstand fest.
- QA-Artefakte verbleiben in `internal/qa/` und werden nicht mehr als
  Wissensmodule geführt.

## 2025-10-30 – Repo-Agent – QA-Artefakte verknüpft
- Plattform: Lokale CI-Simulation
- Wissensstand: `runtime.js` 4.2.2, README/Toolkit Stand 2025-10-30,
  QA-Fahrplan 1.8.3
- Copy-&-Paste-Auftrag: QA-Fahrplan Abschnitt „Dokumentation & Index“
  nachvollziehen, QA-Artefakte sichtbar in README & Master-Index verankern.

**Maßnahmen**
1. README Dokumenten-Landkarte um direkten Block zu QA-Fahrplan, QA-Audit und
   Beta-QA-Log erweitert; Repo-Map listet `internal/qa/` als Meta-Ordner.
2. `master-index.json` führt Fahrplan, Audit und Log neu unter Kategorie „QA“,
   damit Wissensspeicher-Loadouts die Artefakte schneller finden.
3. QA-Fahrplan auf Version 1.8.3 gehoben und Statusnotiz zum synchronisierten
   Dokumentationsstand ergänzt.

```shell
make lint
make test
bash scripts/smoke.sh
python3 tools/lint_runtime.py
GM_STYLE=verbose python3 tools/lint_runtime.py
python3 scripts/lint_doc_links.py
python3 scripts/lint_umlauts.py
```

**Nachverfolgung**
- QA-Fahrplan 1.8.3 dokumentiert die neue Verlinkung; README & Master-Index
  bleiben runtime-fokussiert ohne zusätzliche QA-Anweisungen.
- Keine Runtime-Änderungen nötig; Spiegelpflicht bleibt erfüllt.

## 2025-10-29 – Repo-Agent – Wissensmodule entschlackt
- Plattform: Lokale CI-Simulation
- Wissensstand: `runtime.js` 4.2.2, README/Toolkit Stand 2025-10-29,
  QA-Fahrplan 1.8.2
- Copy-&-Paste-Auftrag: QA-Fahrplan Schritt „Wissensspiegel“ befolgen,
  QA-Hinweise aus produktiven Wissensmodulen minimieren, ohne Runtime-Spiegel zu verlieren.

**Maßnahmen**
1. README (`README.md`) überarbeitet und QA-spezifische Formulierungen in den
   Runtime-Kapiteln neutralisiert (Operator-Setup, Save v6, Debrief-Logs), damit
   produktive GPTs ohne Prüfhinweise arbeiten können.
2. Beispielworkflow präzisiert: Upload-Protokollierung bleibt erhalten,
   Abnahme-Smoke wird als optionaler Test ausgewiesen.
3. Logbuch (dieser Eintrag) dokumentiert die Anpassung gemäß QA-Fahrplan
   „Wissensspiegel“.

```shell
make lint
make test
bash scripts/smoke.sh
python3 tools/lint_runtime.py
GM_STYLE=verbose python3 tools/lint_runtime.py
python3 scripts/lint_doc_links.py
python3 scripts/lint_umlauts.py
```

**Nachverfolgung**
- README spiegelt weiterhin alle Runtime-Guards, verzichtet aber auf
  störende QA-Anweisungen in Wissensmodulen.
- Weitere Evidenzen werden nicht benötigt; keine offenen Punkte.

## 2025-10-28 – Tester: Beta-GPT – Save/HUD/Arena-Divergenzen
- Plattform: Beta-GPT (Remote-Lauf via Maintainer-Skript)
- Wissensstand: `runtime.js` 4.2.2, README/Toolkit Stand 2025-10-21,
  QA-Fahrplan 1.8.2 (aktualisiert am 2025-10-28)
- Copy-&-Paste-Auftrag: Neues Maßnahmenpaket (Issues #1–#13) für HQ-DeepSave,
  HUD-/Arena-Guards, Ökonomie und Comms-Regelblock anlegen, Fahrplan & Audit
  verlinken.
- Rohdaten: Beta-GPT Lauf 2025-10-28 – Rohprotokoll (Maintainer-Archiv,
  Ablage folgt unter `internal/qa/logs/`).

**Befunde (Kurzfassung)**
1. Pflichtfeldliste des HQ-DeepSave widerspricht SaveGuard-Spec (Serializer vs.
   Textauflistung).
2. Beispiel-JSON im Save-Kapitel lässt Pflichtfelder (`economy.wallets`,
   `logs.foreshadow` usw.) weg.
3. Arena-Active sperrt HQ-Saves nicht zuverlässig (fehlender Guard trotz
   Toolkit-Anforderung).
4. Gate-Badge bezeichnet Foreshadow-Zähler uneinheitlich (`Foreshadow 0/2`
   vs. `GATE 0/2`).
5. Paradoxon-Reset widerspricht sich (sofort vs. nach einer Runde) zwischen
   Kampagnenstruktur und Modul 12.
6. Boss-DR-HUD-Toast fehlt trotz Kampagnenstruktur-Vorgabe.
7. Mission-5 Self-Reflection Reset ist nicht garantiert an `EndMission()`
   gebunden.
8. Solo→Koop/PvP Cross-Mode-Doku fehlt eine durchgehende Import-Sequenz.
9. Mission-/CU-Ökonomie nutzt abweichende Basiswerte (Modul 8A vs. Modul 15).
10. Gate-Badge und Toast duplizieren den gleichen Hinweis (Acceptance 11–12).
11. Comms-Reichweite/Hardwarepflicht fehlt als zentraler Regelblock im Core.
12. Foreshadow-Mirror-Pflicht wird nicht als Save-Pflichtfeld abgesichert.
13. Accessibility-Preset-Beispiel im Save-Modul fehlt.

**To-dos**
- [x] Fahrplan: Maßnahmenpaket „Beta-GPT 2025-10-28“ mit Issues #1–#13
  anlegen (Status „🟠 offen“).
- [x] Audit: Befundliste übernehmen und Referenzen mit Modul-Updates
  synchronisieren. → Audit-Update 2025-10-28 verlinkt alle 13 Maßnahmen
  (QA-Fahrplan 1.8.2).
- [x] QA-Referenzen: Maintainer:innen liefern Evidenz (HUD-/Save-Dumps,
  Wallet-Splits, Arena-Guards) nach Umsetzung nach.
  - JSON-Hand-off 2025-11-05 hinterlegt alle Artefakte in
    `internal/qa/evidence/2025-beta-gpt-evidenz.md` §2025-10-28.

**QA-Testfälle (gefordert)**
- Regressionstest `!save` mit Minimal-HQ-Save (nur Pflichtfelder laut Tabelle).
  Erwartet: keine Fehler, Serializer ergänzt fehlende Pflichtblöcke leer und
  protokolliert Warnung.

**Nachverfolgung**
- QA-Fahrplan 1.8.2 listet das neue Maßnahmenpaket und verweist auf dieses
  Log.
- Audit-Update 2025-11-05 verlinkt auf den JSON-Hand-off und bestätigt den
  abgeschlossenen Evidenzsatz.

## 2025-10-21 – Repo-Agent – Beta-GPT 2025-10-15 Nacharbeiten validiert
- Plattform: Lokale CI-Simulation
- Wissensstand: `runtime.js` 4.2.2, README/Toolkit Stand 2025-10-21,
  QA-Fahrplan 1.8.2 (Fortschreibung aus 1.8.1)
- Copy-&-Paste-Auftrag: Fahrplan-Eintrag für die Live-Nacharbeiten ergänzen,
  Beta-GPT-Checks (Acceptance 1–15, Funkgeräte, Compliance-Makro, Save-Schema) erneut
  gegen Runtime & Wissensmodule spiegeln.

**Maßnahmen**
1. QA-Fahrplan (`internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md`) auf Version 1.8.1 gehoben
   (weitergeführt als 1.8.2),
   neuen Deepcheck-Eintrag `2025-10-21` ergänzt und im Maßnahmenpaket 2025-10-15 den
   Abschlussstand 2025-10-21 dokumentiert.
2. Runtime (`runtime.js`): `set_self_reflection()` absichert nun nach `ensure_logs()` auch
   `state.logs.flags`, damit der automatische SF-Reset nach Mission 5 ohne Fehler läuft.
3. QA-Log (dieser Eintrag) führt Tests & Spiegelungen auf und verweist auf die aktualisierten
   Dokumente (README, QA-Briefing, Masterprompt, Speicher-Module).

```shell
make lint
make test
bash scripts/smoke.sh
python3 tools/lint_runtime.py
GM_STYLE=verbose python3 tools/lint_runtime.py
python3 scripts/lint_doc_links.py
PYTHONPATH=. python3 scripts/lint_umlauts.py
```

**Ergebnisse**
- `make lint` läuft komplett grün und bestätigt Link-/Markdownlint der QA-Dokumente
  (`internal/qa/...`).
- `make test` inklusive Smoke-, Save- und Konflikt-Suite läuft nach dem Fix in
  `set_self_reflection()` fehlerfrei durch.
- Zusatzläufe (`scripts/smoke.sh`, Runtime-Linter, Link-/Umlaut-Checks) bleiben ohne Befund.

**Nachverfolgung**
- QA-Fahrplan Version 1.8.2 verweist auf diesen Logeintrag und markiert die Beta-GPT
  Nacharbeiten als validiert.
- JSON-Hand-off 2025-11-05 liefert die zugehörigen Evidenzen; Audit-Update
  2025-11-05 verlinkt auf das Evidenzprotokoll.

## 2025-10-15 – Tester: Beta-GPT – Acceptance-/HUD-/Save-Drift
- Plattform: Beta-GPT (Remote-Lauf via Maintainer-Script)
- Wissensstand: `runtime.js` 4.2.2, README/Toolkit Stand 2025-07-20, QA-Fahrplan 1.6.1
- Copy-&-Paste-Auftrag: Neues Maßnahmenpaket (Issues #1–#15) für Acceptance-Smoke, Save-Migration,
  HUD-Badges und Arena-/Accessibility-Prozesse anlegen, in Fahrplan & Audit verlinken.
- Rohdaten: [Beta-GPT Lauf 2025-10-15 – Rohprotokoll](2025-10-15-beta-gpt-delta.md)

**Befunde (Kurzfassung)**
1. Acceptance-Smoke-Liste endet bei Schritt 13, gefordert sind 15 Prüfpunkte (Dispatcher/README).
2. Legacy-Gruppensaves (`"Charaktere"/"Gruppe"`, `zr_version 4.1.5`) kollidieren mit v6-Serializer
   (`party.characters[]`).
3. `StartMission()` setzt `AllowEntryChoice()` trotz `SkipEntryChoice()`-Flag nach Ladevorgängen.
4. `SF-OFF`-Badge kehrt ohne Auto-Reset nicht zu `SF-ON` zurück.
5. Gate-Badge `GATE 2/2` verliert Persistenz während M5/M10 trotz erfülltem Gate.
6. PvP-/Arena-Saves besitzen keinen dedizierten `phase`/`arena`-Persistenzmarker.
7. Arena-Cross-Mode-Flows spiegeln `logs.psi[]`/Arena-Marker nicht zuverlässig.
8. NPC-Squad-Callouts landen nicht automatisch in `logs.squad_radio[]` (fehlender Auto-Hook).
9. Chronopolis-Vorschau setzt `logs.flags.chronopolis_warn_seen` nicht dauerhaft.
10. Hazard-Pay-Logik kollidiert mit Wallet-Split-Reihenfolge bei Solo→Koop-Imports.
11. Boss-DR-HUD-Toast fehlt in Teilen der M5/M10-Läufe.
12. `logs.foreshadow[]` ist nicht als Pflichtfeld im v6-Schema markiert.
13. Kein eigener `!accessibility`-Dialog trotz Acceptance-Vorgabe.
14. Dispatcher-Start kennt kein `trigger`-Flag (Preserve/Trigger-Parität fehlt).
15. Cinematic-Start stellt initialen HUD-Header nicht zwingend her.

**To-dos**
- [x] Fahrplan: Maßnahmenpaket „Beta-GPT 2025-10-15“ aufnehmen und Issues #1–#15 auf „offen“ setzen.
  → QA-Fahrplan 1.8.2 (fortgeschrieben aus 1.8.0) dokumentiert alle Punkte als abgeschlossen.
- [x] Audit: Neue Befunde in laufende Maßnahmenliste einpflegen, Referenzen auf README/Toolkit
  aktualisieren. → Audit-Update vom 20.10.2025 ergänzt die neuen Abschnitte.
- [x] QA-Referenzen: Maintainer:innen liefern Evidenz (HUD-Dumps, Save-Beispiele, Dispatcher-
  Transkripte) nach Umsetzung. → Nachweise liegen seit 2025-11-05 im Evidenz-Log
  `internal/qa/evidence/2025-beta-gpt-evidenz.md` (JSON-Hand-off).

**Nachverfolgung**
- QA-Fahrplan Version 1.8.2 führt das Maßnahmenpaket als abgeschlossen; Audit und Evidenzprotokoll
  wurden am 2025-11-05 per JSON-Hand-off aktualisiert.
- README, Toolkit und Save-Module spiegeln die Kapitel (Stand 2025-10-20); Evidenzen liegen im
  Evidenz-Log vollständig vor.

## 2025-10-20 – Repo-Agent – Smoke-/Lint-Check & Offene Punkte
- Plattform: Lokale CI-Simulation
- Wissensstand: `runtime.js` 4.2.2, README/Toolkit Stand 2025-10-15,
  QA-Fahrplan 1.8.2 (Fortschreibung aus 1.8.0)
- Copy-&-Paste-Auftrag: Pflicht-Testpaket erneut verifizieren, QA-Dokumente auf
  Restarbeiten prüfen.

```shell
make lint
make test
bash scripts/smoke.sh
python3 tools/lint_runtime.py
GM_STYLE=verbose python3 tools/lint_runtime.py
python3 scripts/lint_doc_links.py
PYTHONPATH=. python3 scripts/lint_umlauts.py
```

**Ergebnisse**
- Alle Pflichtprüfungen laufen grün; `scripts/lint_umlauts.py` benötigt weiterhin `PYTHONPATH=.`,
  fällt sonst mit `ModuleNotFoundError` aus.
- Keine neuen Diff-Hinweise im Runtime-Stapel; README/Toolkit spiegeln die aktuellen Guards und
  HUD-Badges konsistent.

**Offene Aufgaben (Stand 2025-10-20)**
- [x] QA-Audit: Abschnitte für Beta-GPT 2025-07, 2025-07-18 und 2025-10-15 ergänzt (Update
  20.10.2025).
- [x] QA-Log: To-do-Checkboxen in den Läufen 2025-07-05 und 2025-10-15 mit Statusnotizen versehen.
- [x] Maintainer:innen liefern die in Audit §Folgeaufgaben geforderten QA-Evidenzen
  (Dispatcher-Suite, Cross-Mode-Läufe, Debrief-Splits) sowie HUD-/Save-Dumps für die
  jüngsten Beta-GPT-Runs; Vorlage siehe `internal/qa/evidence/2025-beta-gpt-evidenz.md`
  (aktualisiert via JSON-Hand-off 2025-11-05).

**Nachverfolgung**
- QA-Fahrplan 1.8.2 bestätigt den Abschluss aller Beta-GPT-Maßnahmenpakete;
  Audit-Update 2025-11-05 dokumentiert den JSON-Hand-off samt evidenzierter
  Maintainer-Läufe.

## 2025-07-20 – Repo-Agent – Beta-GPT 2025-07-18 Maßnahmen umgesetzt
- Plattform: Lokale CI-Simulation
- Wissensstand: `runtime.js` 4.2.2, README/Toolkit/Characters Stand 2025-07-20, QA-Fahrplan 1.6.1
- Copy-&-Paste-Auftrag: Beta-GPT 2025-07-18 (#1–#12) final abhaken, Gate-Badge/Psi-Log-Doku
  spiegeln, Dispatcher-Text angleichen.

**Maßnahmen**
1. Toolkit (`systems/toolkit-gpt-spielleiter.md`): Tagsplit für `StartMission` (`|`/`,`)
   vereinheitlicht, Gate-Badge `GATE n/2`
   dokumentiert und Runtime-Hinweis für `logs.psi[]` ergänzt; Dispatcher-Semver-Fehlertext mit
   README synchronisiert.
2. HUD-Modul (`characters/hud-system.md`): Header-Spezifikation um `GATE {seen}/2` und Self-
   Reflection-Persistenz
   erweitert.
3. QA-Fahrplan (`internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md`): Beta-GPT-Block 2025-07-18 auf ✅
   gesetzt, Kurznotizen und
   Referenzen auf Runtime/Wissensmodule ergänzt.
4. QA-Log aktualisiert (dieser Eintrag) und auf Pflichttests verwiesen.

```shell
make lint
make test
bash scripts/smoke.sh
python3 tools/lint_runtime.py
GM_STYLE=verbose python3 tools/lint_runtime.py
python3 scripts/lint_doc_links.py
python3 scripts/lint_umlauts.py
PYTHONPATH=. python3 scripts/lint_umlauts.py
```

**Nachverfolgung**
- QA-Fahrplan Version 1.6.1 markiert Beta-GPT 2025-07-18 als abgeschlossen; Referenzen auf
  README/Toolkit/HUD-Modul gesetzt.
- Wissensmodule spiegeln Runtime-Badges (`GATE`, `SF-OFF`) und Arena-Persistenz (`logs.psi[]`).

## 2025-07-19 – Repo-Agent – QA-Tooling Sync
- Plattform: Lokale CI-Simulation
- Wissensstand: `runtime.js` 4.2.2, README/Toolkit Stand 2025-07-19, QA-Fahrplan 1.6.1
- Copy-&-Paste-Auftrag: Formatierungs- und Tooling-Block aus QA-Fahrplan 2025 (Version 1.6.1)
  schließen und Audit/Maintainer-Ops spiegeln.

**Maßnahmen**
1. `.markdownlint.yaml` eingeführt (100-Zeichen-Profil inkl. Frontmatter-Ausnahme) und in
   das Python-basierte `npm run lint:md` integriert; Makefile & Pre-Commit-Hook rufen
   QA-Plan, QA-Audit und QA-Index (`internal/qa/README.md`) mit ab.
2. `.prettierrc.json` ergänzt, beschränkt auf Dokumentationspfade (`docs/`, `internal/`, Root-
   Markdowns),
   Runtime-Module bleiben von Auto-Rewraps unberührt.
3. `package.json`-Skripte für Markdownlint & Prettier dokumentiert, Makefile `make lint` erweitert,
   Maintainer-Ops/CONTRIBUTING/QA-Fahrplan/Audit synchronisiert.

```chatlog
10:12 Repo-Agent: npm install (403 Forbidden – Registry block; Markdownlint läuft via Python-Skript)
10:19 Repo-Agent: npm run lint:md
10:23 Repo-Agent: make lint
10:27 Repo-Agent: make test
10:41 Repo-Agent: bash scripts/smoke.sh
10:58 Repo-Agent: python3 tools/lint_runtime.py
11:05 Repo-Agent: GM_STYLE=verbose python3 tools/lint_runtime.py
11:12 Repo-Agent: python3 scripts/lint_doc_links.py
11:18 Repo-Agent: python3 scripts/lint_umlauts.py
```

**Nachverfolgung**
- QA-Fahrplan: Formatierungs-Block abgehakt (Version 1.6.1).
- Audit: Abschnitt „Tooling-Abgleich“ ergänzt.
- Maintainer-Ops/CONTRIBUTING reflektieren `make lint` + Markdownlint.

## 2025-07-18 – Tester: Beta-GPT – Save/HUD/Compliance Regression
- Plattform: Beta-GPT (Remote-Lauf über Maintainer-Skript)
- Wissensstand: `runtime.js` 4.2.2, README & Toolkit Stand 2025-07-10, QA-Fahrplan 1.5.0
- Copy-&-Paste-Auftrag: Neuer Maßnahmenkatalog (Issues #1–#12) für Exfil-SaveGuard, HUD-Badges,
  Persistenz-Flags und Dispatcher-Hinweise in Fahrplan & Audit spiegeln.
- Rohdaten: [Beta-GPT Lauf 2025-07-18 – Rohprotokoll](2025-07-18-beta-gpt-delta.md)

**Befunde (Kurzfassung)**
1. Exfil-Rücksprung setzt `campaign.exfil.active` nicht zuverlässig zurück; HQ-DeepSave blockiert.
2. Mission 5 HUD zeigt nach Start nur `FS 0/4` ohne Gate-Bestätigung (`Foreshadow 2/2`).
3. `SF-OFF`-Badge fehlt sporadisch wegen fehlendem Persistenz-Flag für `!sf off`.
4. Solo→Koop-Import legt Wallets erst nach Debrief an; HUD-Shortcuts laufen ins Leere.
5. Arena-Phase-Strike-Steuer wird nicht in `logs.psi[]` persistiert.
6. Compliance-Hinweis wird nach `!load` mehrfach gezeigt (Mirror `campaign` ↔ `logs.flags`).
7. `logs.offline[]` überschreitet FIFO-Limit 12 bei wiederholtem `!offline`.
8. Boss-Gate-Badge fehlt im HUD trotz aktivem Gate.
9. Start-Dispatcher erinnert nicht konsistent an `!radio clear`/`!alias clear` vor Einsatz.
10. `px_tracker(temp)` ETA-Kommunikation divergiert zwischen HUD und README.
11. Heist/Street-Tags normalisieren `DelayConflict` nicht zuverlässig (`tags_source` Parsing).
12. Semver-Mismatch-Text unterscheidet sich zwischen README und Toolkit.

**To-dos**
- [x] Fahrplan: Maßnahmenpaket „Beta-GPT 2025-07-18“ mit Issues #1–#12 anlegen, Status initial offen
  lassen.
- [x] Audit: Befundliste übernehmen und Referenzen (HUD/Saves/Dispatcher) verknüpfen.
- [x] QA-Referenzen: Maintainer:innen erstellen Evidenz (Screenshots, Logs) nach Umsetzung.

**Nachverfolgung**
- QA-Fahrplan Version 1.6.0 führt neuen Maßnahmenblock und verweist auf das Rohprotokoll; laut Repo-
  Agent-Eintrag vom 20.07.2025 sind alle Punkte abgeschlossen.
- Audit-Update 2025-11-05 verlinkt auf die vollständige Evidenz (§2025-07-18) aus dem JSON-Hand-off.
- README/Toolkit-Sync für Gate-/Badge-/Compliance-Themen bleibt hinterlegt und verweist auf die
  aktualisierten Module.

## 2025-07-10 – Repo-Agent – Beta-GPT 2025-07 Maßnahmen umgesetzt
- Plattform: Lokale CI-Simulation
- Wissensstand: `runtime.js` 4.2.2, README/Systems Stand 2025-07-10, QA-Fahrplan 1.5.0
- Copy-&-Paste-Auftrag: QA-Fahrplan 2025-07 Maßnahmenblock (#1–#15) vollständig schließen;
  Wissensmodule & README spiegeln.

```chatlog
09:12 Repo-Agent: `make lint`
10:04 Repo-Agent: `make test`
11:18 Repo-Agent: `bash scripts/smoke.sh`
11:42 Repo-Agent: `python3 tools/lint_runtime.py`
11:46 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
11:49 Repo-Agent: `python3 scripts/lint_doc_links.py`
11:51 Repo-Agent: `PYTHONPATH=. python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] Save-Version & Migration: Serializer/Migrationsleitfaden in `systems/gameflow/speicher-
  fortsetzung.md` auf `save_version: 6`
  angehoben, README-Spiegel ergänzt.
- [x] Foreshadow-Gate & Saisonstand: README & Toolkit unterscheiden Gate (2/2) und Saison (4/4)
  inkl. `scene_overlay()`/`!boss status`-Spec.
- [x] Acceptance 12 (`SF-OFF`, Boss-Toast, Foreshadow-Reset) samt QA-Doppelbelegen dokumentiert;
  LINT-Anchor `FS_RESET_OK`
  verankert und freigegeben.
- [x] Arena-Start, SaveGuard & Koop-Wallet-Initialisierung in README/Systems beschrieben;
  Acceptance-Smoke um Accessibility/Offline
  sowie Chronopolis-Smoke ergänzt.
- [x] QA-Fahrplan Maßnahmenpaket 2025-07 auf ✅ gesetzt; README, Toolkit, doc.md und
  `.lint/anchors.allow` synchronisiert.

**Nachverfolgung**
- QA-Fahrplan Version 1.5.0 spiegelt Abschluss aller Beta-GPT-2025-07-Issues inkl. Referenzen.
- README & Systems liefern aktualisierte Laufzeitspiegel; `.lint/anchors.allow` enthält
  `LINT:FS_RESET_OK`.
- Audit-Update 2025-11-05 bestätigt die JSON-basierten Evidenzen (§2025-07-05).

## 2025-07-05 – Tester: Beta-GPT – Schema-, HUD- und Arena-Deltas
- Plattform: Beta-GPT (Remote-Lauf über Maintainer-Skript)
- Wissensstand: `runtime.js` 4.2.2, README & Toolkit Stand 2025-06-30, QA-Fahrplan 1.4.0
- Copy-&-Paste-Auftrag: Neuer Maßnahmenkatalog (Issues #1–#15) für Save-Versionierung, Foreshadow-
  Status, Arena-/Comms-Makros und Acceptance-Texte in Fahrplan & Audit spiegeln.
- Rohdaten: [Beta-GPT Lauf 2025-07-05 – Rohprotokoll](2025-07-05-beta-gpt-delta.md)

**Befunde (Kurzfassung)**
1. Save-Version driftet zwischen Beispiel (`save_version: 6`) und Serializer/Migration (`5`).
2. Foreshadow-Zähler Gate (2/2) vs. Season Total (4) uneinheitlich dargestellt.
3. Makro `scene_overlay()` sowie `!boss status` fehlen als formale Schnittstellenbeschreibung.
4. Acceptance 12 verlangt `SF-OFF`-Badge ohne klaren Vorbereitungs-Schritt oder Auto-Toggle.
5. `arenaStart(options)` in Toolkit/Doku nicht definiert; Phase-Strike-Toast hängt an Psi-Modul.
6. `comms_check(device, range)` ohne Funktionsspezifikation trotz Pflichtreferenz.
7. Doppelstruktur `team.members[]` vs. `party.characters[]` erzeugt Save-Konflikte.
8. Doppelte Dokumentationszeile zu `logs.fr_interventions[]` im Speicher-Modul.
9. Acceptance 12 koppelt Boss-DR-Toast und `SF-OFF`-Badge ohne Reihenfolge.
10. Cross-Mode-Saves (Solo→Koop) initialisieren Wallets nicht eindeutig.
11. Accessibility-/Offline-Checks fehlen im Acceptance-Smoke.
12. README „Spiel laden“ widerspricht Speicher-Modul (kein Einstiegsauswahl-Dialog).
13. Foreshadow-Reset benötigt doppelte Evidenz (HUD + QA-Log) mit einheitlicher Quelle.
14. Arena-Save-Guard nicht als Acceptance-Schritt dokumentiert.
15. City/Chronopolis-Module haben keinen dedizierten Acceptance-Smoke-Test.

**To-dos**
- [x] Fahrplan: Neuen Maßnahmenblock „Beta-GPT 2025-07“ mit Status/Referenzen anlegen. → Erledigt in
  QA-Fahrplan 1.8.2 (§„Maßnahmenpaket Beta-GPT 2025-07“).
- [x] Audit: Issues #1–#15 unter laufenden Maßnahmen erfassen (Verlinkung zu Fahrplan +
  README/Toolkit). → Update 2025-10-20 im QA-Audit dokumentiert.
- [x] QA-Referenzen: Maintainer:innen erstellen QA-Evidenz (Migration 5→6, HUD-Logs, Arena-/City-
  Smokes) nach Umsetzung. → Ablage aktualisiert 2025-11-05 (`internal/qa/evidence/2025-beta-gpt-
  evidenz.md`, JSON-Hand-off).

**Nachverfolgung**
- Fahrplan-Version 1.5.0 führt Issues #1–#15 als offen geplante Maßnahmen mit QA-
  Verantwortlichkeiten.
- Audit-Update 2025-11-05 bestätigt die JSON-Hand-off-Evidenzen und verlinkt die
  abgeschlossenen Maßnahmen im Audit.

## 2025-06-29 – Repo-Agent – Save-Pflichtfelder Mirror
- Plattform: Lokale CI-Simulation
- Wissensstand: `runtime.js` 4.2.2, README/Systems Stand 2025-06-29, QA-Fahrplan 1.3.1
- Copy-&-Paste-Auftrag: QA-Fahrplan §Maßnahmenpaket (Issue #1 – Save-Schema) – Pflichtfelder
  `logs.alias_trace`/`logs.squad_radio` in Wissensmodulen spiegeln und Lint erweitern.

```chatlog
09:45 Repo-Agent: `make lint`
09:58 Repo-Agent: `make test`
10:34 Repo-Agent: `bash scripts/smoke.sh`
10:51 Repo-Agent: `python3 tools/lint_runtime.py`
10:54 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
10:57 Repo-Agent: `python3 scripts/lint_doc_links.py`
10:59 Repo-Agent: `python3 scripts/lint_umlauts.py` (Fehler: ModuleNotFoundError)
11:00 Repo-Agent: `PYTHONPATH=. python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] Pflichtfelder `logs.alias_trace`/`logs.squad_radio` im Save-Pseudocode und JSON-Beispiel
  ergänzt; README spiegeln; Lint prüft die Felder.
- [x] QA-Fahrplan-Referenz: Cluster A Issue #1 – Save-Schema bestätigt aktualisierte Wissensmodule.

**Nachverfolgung**
- QA-Fahrplan: Abschnitt „Maßnahmenpaket Beta-GPT 2025-06 – Issue-Fahrplan → Cluster A – Save-
  Contract & Persistenz“ verweist jetzt auf README + Modul 12 mit den zusätzlichen Pflichtfeldern.
- Audit: Save-Contract-Abschnitt 2025-06 vermerkt identische Pflichtfelder (keine weiteren Maßnahmen
  erforderlich).

## 2025-06-28 – Repo-Agent – Chronopolis Hochstufen-Stichprobe
- Plattform: Lokale CI-Simulation
- Wissensstand: `runtime.js` 4.2.2, README/Systems Stand 2025-06-28, QA-Fahrplan 1.3.1
- Copy-&-Paste-Auftrag: QA-Follow-up #14 schließen, Hochstufen-Angebot & Px-Trace prüfen

```chatlog
09:35 Repo-Agent: `make lint`
10:02 Repo-Agent: `make test`
10:27 Repo-Agent: `bash scripts/smoke.sh`
10:51 Repo-Agent: `python3 tools/lint_runtime.py`
10:54 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
10:58 Repo-Agent: `python3 scripts/lint_doc_links.py`
11:01 Repo-Agent: `PYTHONPATH=. python3 scripts/lint_umlauts.py`
11:06 Repo-Agent: `node tools/test_chronopolis_high_tier.js`
```

**Offene Punkte**
- [x] `tools/test_chronopolis_high_tier.js` bestätigt Daily-Roll ohne 🔒-Locks (Chief + Research 4)
  und Px-Trace im Debrief.
- [x] README, Systems-Module und QA-Fahrplan referenzieren den Hochstufen-Lauf; Audit-Abschnitt
  aktualisiert.

**Nachverfolgung**
- QA-Fahrplan: Cluster C #14 aktualisiert (Stand 2025-06-28) inklusive Script-Referenz.
- Audit: Abschnitt „QA-Follow-up #14 – Chronopolis-Basar Balance“ um Hochstufen-Stichprobe ergänzt.

## 2025-06-27 – Repo-Agent – Mission 5 Gate & Arena QA
- Plattform: Lokale CI-Simulation
- Wissensstand: `runtime.js` 4.2.2, README/Systems Stand 2025-06-27, QA-Fahrplan 1.3.1
- Copy-&-Paste-Auftrag: QA-Follow-ups #7/#11/#15/#16/#17 abschließen (Mission 5/10 Gate, Boss-Toast,
  Ask→Suggest, Vehikel-Overlay, Phase-Strike-Arena)

```chatlog
09:42 Repo-Agent: `make lint`
10:11 Repo-Agent: `make test`
10:43 Repo-Agent: `bash scripts/smoke.sh`
11:05 Repo-Agent: `python3 tools/lint_runtime.py`
11:08 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
11:12 Repo-Agent: `python3 scripts/lint_doc_links.py`
11:14 Repo-Agent: `PYTHONPATH=. python3 scripts/lint_umlauts.py`
11:17 Repo-Agent: `node tools/test_acceptance_followups.js`
```

**Offene Punkte**
- [x] QA-Follow-up #7 – Mission 5/10 Gate: `tools/test_acceptance_followups.js` bestätigt
  `Foreshadow 2/2` vor dem Start sowie Reset auf `0/2`; HUD-Badge und `!boss status` spiegeln den
  Reset.
- [x] QA-Follow-up #11 – Boss-Toast QA-Check: HUD-Log enthält Foreshadow-Toasts mit Tag
  `Foreshadow`; README & Toolkit führen die Evidenzschritte.
- [x] QA-Follow-up #15 – Ask→Suggest Load-Test: `modus suggest`/`modus ask` setzen HUD-Toast `SUG-
  ON/SUG-OFF`; Overlay markiert den Wechsel.
- [x] QA-Follow-up #16 – Vehikel-Overlay QA: Toolkit-Module dokumentieren Boden-/Luft-Chase-Overlays
  (`vehicle_overlay('vehicle', …)`); README verweist auf QA-Check.
- [x] QA-Follow-up #17 – Phase-Strike Arena QA: Arena-Start setzt PvP-Modus & `phase_strike_tax=1`;
  Toast `Arena: Phase-Strike …` erfasst die SYS-Kosten, QA-Plan markiert Evidenz.

**Nachverfolgung**
- QA-Fahrplan: Cluster C #7/#11/#15/#16/#17 auf ✅ gesetzt, „Nächste Schritte“ um Abschlussnotizen
  (2025-06-27) ergänzt.
- README & Toolkit-Modul ergänzen QA-Rezepte für Foreshadow-Gate, Ask→Suggest, Vehikel-Chase &
  Phase-Strike.
- Neues QA-Skript `tools/test_acceptance_followups.js` liefert Node-basierte Evidenz für Mission-
  und Arena-Prüfungen.

## 2025-06-24 – Repo-Agent – Arc-Dashboard QA-Tools
- Plattform: Lokale CI-Simulation
- Wissensstand: `runtime.js` 4.2.2 (Arc-Dashboard Status), README/Systems Stand 2025-06-24, QA-
  Fahrplan 1.3.1
- Copy-&-Paste-Auftrag: QA-Follow-up #6 abschließen, Arc-Dashboard-Status für QA exportierbar machen
  und Dokumentation spiegeln

```chatlog
09:58 Repo-Agent: `make lint`
10:17 Repo-Agent: `make test`
11:06 Repo-Agent: `bash scripts/smoke.sh`
11:18 Repo-Agent: `python3 tools/lint_runtime.py`
11:21 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
11:24 Repo-Agent: `python3 scripts/lint_doc_links.py`
11:26 Repo-Agent: `PYTHONPATH=. python3 scripts/lint_umlauts.py`
11:29 Repo-Agent: `node - <<'NODE'` (Arc-Dashboard Status-Testausgabe)
```

**Offene Punkte**
- [x] `!dashboard status` liefert Seeds, Fraktionsmeldungen und offene Fragen als Text-Snapshot für
  QA-Protokolle.
- [x] README und Systems-Module nennen den neuen QA-Befehl; Toolkit weist auf den Evidenzexport hin.
- [x] QA-Fahrplan Cluster C #6 auf ✅ gesetzt, Nächste-Schritte-Abschnitt datiert.

**Nachverfolgung**
- QA-Fahrplan: Cluster C #6 sowie Abschnitt „Nächste Schritte“ mit Abschlussvermerk (2025-06-24)
  aktualisiert.
- README & Systems spiegeln Arc-Dashboard-Befehl; QA-Plan referenziert Runtime- und Doku-Updates.

## 2025-06-22 – Repo-Agent – QA-Fahrplan Sync
- Plattform: Lokale CI-Simulation
- Wissensstand: `runtime.js` 4.2.2, README/Systems Stand 2025-06-22, QA-Fahrplan 1.3.1
- Copy-&-Paste-Auftrag: Deepcheck-Sessions 2025-06-11–2025-06-16 abschließen, Maßnahmenblöcke
  abhaken, QA-Artefakte spiegeln

```chatlog
10:02 Repo-Agent: `make lint`
10:45 Repo-Agent: `make test`
11:18 Repo-Agent: `bash scripts/smoke.sh`
11:54 Repo-Agent: `python3 tools/lint_runtime.py`
12:07 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
12:19 Repo-Agent: `python3 scripts/lint_doc_links.py`
12:27 Repo-Agent: `PYTHONPATH=. python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] Sessions 2025-06-11/12/13/15/16 im QA-Fahrplan abgeschlossen und Abschlussnotizen ergänzt.
- [x] Maßnahmenblöcke (Save-/HUD-/PvP-Strang) auf ✅ gesetzt und QA-Referenzen verlinkt.
- [x] README-Querverweis auf QA-Fahrplan geprüft, QA-Artefakte mit Fahrplan-Status synchronisiert.
- [x] QA-Log-Eintrag 2025-06-22 erstellt und in Fahrplan/README verlinkt.

**Nachverfolgung**
- QA-Fahrplan: Sessions-Abschnitt & Priorisierte Umsetzungspakete aktualisiert (Status ✅
  2025-06-22).
- README: QA-Artefakte-Abschnitt verweist auf aktualisierten QA-Plan (Stand 2025-06-22).

## 2025-06-20 – Repo-Agent – Alias- & Funk-Logs
- Plattform: Lokale CI-Simulation
- Wissensstand: README/Systems aktualisiert (Alias/Squad-Radio), `runtime.js` Branch Alias-Trace,
  Toolkit Stand 2025-06-20
- Copy-&-Paste-Auftrag: QA-Follow-ups #12/#13 abschließen, Alias-/Funk-Logs persistieren und
  Dokumentation spiegeln

```chatlog
11:45 Repo-Agent: `make lint`
12:18 Repo-Agent: `make test`
13:02 Repo-Agent: `bash scripts/smoke.sh`
13:24 Repo-Agent: `python3 tools/lint_runtime.py`
13:26 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
13:28 Repo-Agent: `python3 scripts/lint_doc_links.py`
13:29 Repo-Agent: `PYTHONPATH=. python3 scripts/lint_umlauts.py`
13:31 Repo-Agent: `node tools/test_alias_trace.js`
```

**Offene Punkte**
- [x] Alias-Trace über `!alias log`/`!alias status` implementiert (`logs.alias_trace[]`, Debrief-
  Zeile `Alias-Trace (n×)`).
- [x] Squad-Radio-Log via `!radio log`/`!radio status` bereitgestellt (`logs.squad_radio[]`,
  Debrief-Zeile `Squad-Radio (n×)`).
- [x] Wissensmodule (README, Systems) spiegeln Alias-/Funk-Workflow inkl. Toolkit-Hinweisen; QA-
  Fahrplan Cluster C #12/#13 auf ✅ gesetzt.

**Nachverfolgung**
- QA-Fahrplan: Cluster C #12/#13 sowie Abschnitt „Nächste Schritte“ aktualisiert (Status ✅, Datum
  2025-06-20).
- QA-Plan verweist auf `runtime.js`, README und Systems-Module für Alias/Funk; QA-Log ergänzt
  Alias-/Funk-Testlauf.

## Zweck
Dieses Log sammelt unveränderte Ergebnisse aus Beta-GPT- und MyGPT-Testläufen. Es
ist die Arbeitsgrundlage, um Copy-&-Paste-Protokolle aus den GPT-Chats in
konkrete Aufgaben im QA-Fahrplan zu überführen und deren Abarbeitung
nachzuvollziehen.

## Workflow
1. Maintainer:innen oder Tester:innen führen den Playtest gemäß
   [Tester-Playtest-Briefing](../../../docs/qa/tester-playtest-briefing.md)
   aus, lassen den GPT den kompletten QA-Lauf autonom simulieren und kopieren
   das vollständige Chatprotokoll in einen neuen Abschnitt dieses Logs.
2. Kennzeichne zu Beginn jedes Abschnitts Datum, Plattform, Build und genutzte
   Wissensbasis. Standardplattform ist das OpenAI-MyGPT im Beta-Klon.
   Weitere Plattformen werden nur nach Freigabe gespiegelt und dokumentiert,
   falls Abweichungen auftreten.
3. Füge das Protokoll unverändert als Codeblock ein. Sensible Informationen
   werden vor dem Einfügen entfernt oder anonymisiert.
4. Belasse die vom GPT erzeugten `ISSUE`-, `Lösungsvorschlag`-, `To-do`- und
   `Nächste Schritte`-Blöcke unverändert unterhalb des Chatlogs; ergänzende
   Randnotizen sind optional.
5. Verlinke den Abschnitt im QA-Fahrplan und priorisiere die gemeldeten Blöcke.
6. Sobald Codex einen Punkt bearbeitet hat, aktualisiere das Log mit Verweis auf
   Commit, PR oder Ticket.

## 2025-06-19 – Repo-Agent – Pre-City-Hub Dokumentation
- Plattform: Lokale CI-Simulation
- Wissensstand: README v4.2.2 (HQ/Chronopolis), `gameplay/kampagnenuebersicht.md` Modul 10, Toolkit
  Stand 2025-06-16
- Copy-&-Paste-Auftrag: QA-Fahrplan QA-Follow-up #8 – Pre-City-Hub Dokumentation synchronisieren

```chatlog
10:05 Repo-Agent: `rg "Pre-City-Hub" README.md gameplay/kampagnenuebersicht.md
  systems/toolkit-gpt-spielleiter.md`
10:07 Repo-Agent: `sed -n '890,940p' README.md`
10:09 Repo-Agent: `sed -n '60,140p' gameplay/kampagnenuebersicht.md`
10:11 Repo-Agent: `sed -n '2960,3005p' systems/toolkit-gpt-spielleiter.md`
```

**Offene Punkte**
- [x] README ergänzt Übergangszone und Warnflag (`logs.flags.chronopolis_warn_seen`).
- [x] Modul 10 dokumentiert Ablauf, Vorschau-Content und Persistenz der Pre-Hub-Sequenz.
- [x] Toolkit-Makro-Guide führt Transit-Schritte inklusive HUD-Tagging aus.

**Nachverfolgung**
- QA-Fahrplan: Session „Codex-Pre-Hub-Doku“ (2025-06-19) ergänzt, QA-Follow-up #8 auf ✅ gesetzt.
- QA-Plan Cluster C Row #8 aktualisiert (README §HQ/Chronopolis, Modul 10 Pre-Hub, Toolkit §HQ-Phase
  Workflow).

## 2025-06-17 – Repo-Agent – Koop-Debrief Wallet-Split
- Plattform: Lokale CI-Simulation
- Wissensstand: README v4.2.2, `runtime.js` aktueller Branch (Koop-Debrief), Systems-Module
  synchronisiert
- Copy-&-Paste-Auftrag: QA-Fahrplan Issue #11 – Debrief-Split & Wallet-Logik implementieren

```chatlog
11:02 Repo-Agent: `make lint`
11:08 Repo-Agent: `make test`
11:21 Repo-Agent: `bash scripts/smoke.sh`
11:27 Repo-Agent: `python3 tools/lint_runtime.py`
11:29 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
11:31 Repo-Agent: `python3 scripts/lint_doc_links.py`
11:32 Repo-Agent: `PYTHONPATH=. python3 scripts/lint_umlauts.py`
11:33 Repo-Agent: `python3 tools/lint_debrief_trace.py`
```

**Offene Punkte**
- [x] Issue #11 Koop-Ökonomie: Wallet-Split & HQ-Pool im Debrief, Wissensmodule spiegeln Ablauf.

**Nachverfolgung**
- QA-Fahrplan: Issue #11 (Status aktualisiert 2025-06-17, Session „Codex-Koop-Debrief“).
- Maintainer-Ops: Standardbefehl für Repo-Agent:innen ergänzt (2025-06-17).
- README & Modul 12 dokumentieren Wallet-Split und HQ-Pool (2025-06-17).

## 2025-06-11 – Repo-Agent – HQ-Save Pflichtfelder
- Plattform: Lokale CI-Simulation
- Wissensstand: README v4.2.2, runtime.js aktueller Branch (Save-Schema)
- Copy-&-Paste-Auftrag: QA-Fahrplan Maßnahmenpaket #1 – Save-Schema absichern

```chatlog
10:12 Repo-Agent: `make lint`
10:13 Tool: `Level 25: Summary: OK`
10:14 Repo-Agent: `make test`
10:17 Tool: `All smoke checks passed.`
10:18 Repo-Agent: `bash scripts/smoke.sh`
10:19 Tool: `All smoke checks passed.`
```

**Offene Punkte**
- [x] Issue #1 HQ-Save-Pflichtfelder gegen Defaults absichern.

**Nachverfolgung**
- Commit/PR: 3e4f306
- QA-Fahrplan: Maßnahmenpaket Issue #1 (Status aktualisiert 2025-06-11).
- QA-Audit: Issue #1 als erledigt markiert (2025-06-11).

## 2025-06-13 – Repo-Agent – PvP-Modus-Flag Acceptance-Smoke
- Plattform: Lokale CI-Simulation
- Wissensstand: README v4.2.2, `runtime.js` aktueller Branch (Arena-Modus)
- Copy-&-Paste-Auftrag: QA-Fahrplan Cluster C Issue #2 – PvP-Szenario für Acceptance-Smoke ergänzen

```chatlog
16:45 Repo-Agent: `node - <<'NODE'
const rt = require('./runtime.js');
const { state, handleArenaCommand, save_deep, phase_strike_cost } = rt;
state.economy.credits = 1000;
state.character.id = 'qa-agentin';
state.character.name = 'QA-Agentin';
state.character.rank = 'Recruit';
state.character.lvl = 8;
state.character.stress = 0;
state.team.members = [];
state.team.stress = 0;
state.team.psi_heat = 0;
state.campaign.episode = 2;
state.campaign.mode = 'preserve';
state.campaign.scene = 0;
state.campaign.paradoxon_index = 0;
state.campaign.scene_total = 12;
console.log('Vor Arena:', state.campaign.mode, state.arena.phase_strike_tax, phase_strike_cost());
console.log(handleArenaCommand('!arena start team 2 mode sparring'));
console.log('Arena aktiv:', state.campaign.mode, state.arena.phase_strike_tax, phase_strike_cost());
try {
  save_deep();
} catch (err) {
  console.log('Save während Arena:', err.message);
}
console.log(handleArenaCommand('!arena exit'));
state.team.stress = 0;
state.team.psi_heat = 0;
state.character.stress = 0;
const saveExit = JSON.parse(save_deep());
console.log('Arena Ende:', state.campaign.mode, state.arena.phase_strike_tax, phase_strike_cost());
console.log('Save mode:', saveExit.campaign.mode);
NODE`
16:45 Tool: `Vor Arena: preserve 0 2`
16:45 Tool: `[ARENA] Arena initiiert · Tier 2 · Gebühr 260 CU · Px-Bonus verfügbar`
16:45 Tool: `Arena initiiert · Tier 2 · Gebühr 260 CU · Offene Wüstenruine · Px-Bonus verfügbar`
16:45 Tool: `Arena aktiv: pvp 1 3`
16:45 Tool: `Save während Arena: SaveGuard: Arena aktiv – HQ-Save gesperrt.`
16:45 Tool: `[ARENA] Arena Ende · Score 0:0 · Keine Px-Belohnung (Serie verloren)`
16:45 Tool: `Arena Ende · Score 0:0 · Keine Px-Belohnung (Serie verloren)`
16:45 Tool: `Arena Ende: preserve 0 2`
16:45 Tool: `Save mode: preserve`
```

**Ergebnisse**
- [x] PvP-Flag aktiviert `phase_strike_cost()` → 3 und blockiert HQ-Save während Arena.
- [x] `!arena exit` setzt `phase_strike_cost()` zurück auf 2.
- [x] HQ-Save nach Arena bestätigt `campaign.mode: "preserve"`.

**Nachverfolgung**
- QA-Fahrplan: Cluster C Issue #2 (Acceptance-Smoke #14/#15 dokumentiert 2025-06-13).
- Docs: `docs/qa/tester-playtest-briefing.md` (PvP-Prüfschritte ergänzt).

## 2025-06-14 – Repo-Agent – Offline-Audit Jammer-Szenario
- Plattform: Lokale CI-Simulation
- Wissensstand: README v4.2.2, `runtime.js` aktueller Branch (Offline-Fallback)
- Copy-&-Paste-Auftrag: QA-Fahrplan Cluster C Issue #10 – Jammer-Suspend/Resume dokumentieren

```chatlog
08:40 Repo-Agent: `node - <<'NODE'
const rt = require('./runtime.js');
const { StartMission, offline_help, jam_now, render_offline_protocol, state, require_uplink } = rt;
StartMission();
state.campaign = { episode: 3, mission: 5, mode: 'preserve', objective: 'Test Mission', px: 2 };
state.location = 'Einsatzort';
state.phase = 'core';
state.scene = { index: 3, total: 12 };
state.comms.device = 'comlink';
state.comms.range_m = 5000;
console.log(offline_help('auto'));
jam_now(true);
state.comms.range_m = 1500;
try {
  require_uplink(state, 'radio_tx');
} catch (err){
  console.log('require_uplink error:', err.message);
}
console.log(offline_help('jammer'));
jam_now(false);
state.comms.range_m = 5000;
console.log(offline_help('resume'));
console.log('Offline log entries:', state.logs.offline);
console.log('Rendered protocol:', render_offline_protocol());
NODE`
08:40 Tool: `[OFFLINE] Kodex-Uplink getrennt – Mission läuft weiter mit HUD-Lokaldaten.`
08:40 Tool: `Kodex Offline-FAQ (ITI↔Kodex-Uplink im Einsatz gekappt):`
08:40 Tool: `- Terminal oder Hardline suchen, Relay koppeln,
  Jammer-Override prüfen – Kodex bleibt bis dahin stumm.`
08:40 Tool: `- Mission normal fortsetzen: HUD liefert lokale Logs, neue Saves gibt es weiterhin
  erst zurück im HQ.`
08:40 Tool: `- Ask→Suggest-Fallback nutzen: Aktionen als „Vorschlag:“ markieren und Bestätigung
  abwarten.`
08:40 Tool: ``
08:40 Tool: `Offline-Protokoll (1×): Fallback · Gerät comlink · Jammer frei · Reichweite 5000m ·
  Relais 0 · Szene 3/12 · EP 3 · MS 5`
08:40 Tool: `require_uplink error: Kodex-Uplink getrennt – Mission läuft weiter mit
  HUD-Lokaldaten. !offline zeigt das Feldprotokoll bis zum HQ-Re-Sync.`
08:40 Tool: `Kodex Offline-FAQ (ITI↔Kodex-Uplink im Einsatz gekappt):`
08:40 Tool: `- Terminal oder Hardline suchen, Relay koppeln,
  Jammer-Override prüfen – Kodex bleibt bis dahin stumm.`
08:40 Tool: `- Mission normal fortsetzen: HUD liefert lokale Logs, neue Saves gibt es weiterhin
  erst zurück im HQ.`
08:40 Tool: `- Ask→Suggest-Fallback nutzen: Aktionen als „Vorschlag:“ markieren und Bestätigung
  abwarten.`
08:40 Tool: ``
08:40 Tool: `Offline-Protokoll (3×): jammer · Gerät comlink · Jammer aktiv · Reichweite 1500m ·
  Relais 0 · Szene 3/12 · EP 3 · MS 5`
08:40 Tool: `Kodex Offline-FAQ (ITI↔Kodex-Uplink im Einsatz gekappt):`
08:40 Tool: `- Terminal oder Hardline suchen, Relay koppeln,
  Jammer-Override prüfen – Kodex bleibt bis dahin stumm.`
08:40 Tool: `- Mission normal fortsetzen: HUD liefert lokale Logs, neue Saves gibt es weiterhin
  erst zurück im HQ.`
08:40 Tool: `- Ask→Suggest-Fallback nutzen: Aktionen als „Vorschlag:“ markieren und Bestätigung
  abwarten.`
08:40 Tool: ``
08:40 Tool: `Offline-Protokoll (4×): resume · Gerät comlink · Jammer frei · Reichweite 5000m ·
  Relais 0 · Szene 3/12 · EP 3 · MS 5`
08:40 Tool: `Offline log entries: [`
08:40 Tool: `  {"timestamp":"2025-10-12T14:26:44.344Z","reason":"auto","status":"offline",
  "device":"comlink","jammed":false,"range_m":5000,"relays":0,"count":1,"scene_index":3,
  "scene_total":12,"episode":3,"mission":5,"location":"Einsatzort","phase":"core",
  "gm_style":"verbose"},`
08:40 Tool: `  {"timestamp":"2025-10-12T14:26:44.345Z","reason":"auto","status":"offline",
  "device":"comlink","jammed":true,"range_m":1500,"relays":0,"count":2,"scene_index":3,
  "scene_total":12,"episode":3,"mission":5,"location":"Einsatzort","phase":"core",
  "gm_style":"verbose"},`
08:40 Tool: `  {"timestamp":"2025-10-12T14:26:44.346Z","reason":"jammer","status":"offline",
  "device":"comlink","jammed":true,"range_m":1500,"relays":0,"count":3,"scene_index":3,
  "scene_total":12,"episode":3,"mission":5,"location":"Einsatzort","phase":"core",
  "gm_style":"verbose"},`
08:40 Tool: `  {"timestamp":"2025-10-12T14:26:44.347Z","reason":"resume","status":"offline",
  "device":"comlink","jammed":false,"range_m":5000,"relays":0,"count":4,
  "scene_index":3,"scene_total":12,"episode":3,"mission":5,"location":"Einsatzort",
  "phase":"core","gm_style":"verbose"}`
08:40 Tool: `]`
08:40 Tool: `Rendered protocol: Offline-Protokoll (4×): resume · Gerät comlink · Jammer frei ·
  Reichweite 5000m · Relais 0 · Szene 3/12 · EP 3 · MS 5`
```

**Ergebnisse**
- [x] Jammer-Suspend protokolliert (`reason: "jammer"`, `jammed: true`, Reichweite 1500 m).
- [x] Resume-Pfad dokumentiert (`reason: "resume"`, Jammer frei, Reichweite 5000 m).
- [x] Offline-Log-Trace (`render_offline_protocol()`) im QA-Log festgehalten.
- [x] `python3 tools/lint_runtime.py` bestätigt YAML-/Save-Prüfungen (Level 25 OK).

**Nachverfolgung**
- QA-Fahrplan: Cluster C Issue #10 (Offline-Audit Jammer-Szenario) – Status aktualisiert 2025-06-14.
- Docs: `docs/qa/tester-playtest-briefing.md` (Offline-Fallback-Hinweis deckt Jammer-Flow ab).

## 2025-06-17 – Repo-Agent – Debrief-Trace Linter
- Plattform: Lokale CI-Simulation
- Wissensstand: README v4.2.2 (Debrief-Trace-Erweiterung), `runtime.js` aktueller Branch,
  `systems/gameflow/speicher-fortsetzung.md`
- Copy-&-Paste-Auftrag: QA-Follow-up #9 – Debrief-Linter (Issue #16) für
  Chronopolis-/Foreshadow-/Offline-Traces umsetzen

```chatlog
09:05 Repo-Agent: `python3 tools/lint_debrief_trace.py`
09:05 Tool: `INFO: [ OK ] Chronopolis-Trace nennt Einkauf & Kosten`
09:05 Tool: `INFO: [ OK ] Chronopolis-Trace enthält Timestamp`
09:06 Tool: `INFO: [ OK ] Foreshadow-Log referenziert Mission 5 Hinweis`
09:06 Tool: `INFO: [ OK ] Offline-Protokoll meldet Jammer-Trace`
09:06 Tool: `INFO: [ OK ] Runtime-Flags führen Runtime-Version`
09:06 Tool: `INFO: [ OK ] Runtime-Flags zeigen Compliance-Status`
09:06 Tool: `INFO: [ OK ] Runtime-Flags spiegeln Chronopolis-Warnung`
09:06 Tool: `INFO: [ OK ] Runtime-Flags zählen Offline-Hilfe`
09:07 Tool: `INFO: [ OK ] Runtime-Flags enthalten letzten Offline-Zeitstempel`
09:07 Tool: `INFO: Debrief-Trace-Lint abgeschlossen`
09:10 Repo-Agent: `make lint && make test`
09:18 Tool: `All smoke checks passed.`
09:22 Repo-Agent: `bash scripts/smoke.sh`
09:23 Tool: `All smoke checks passed.`
09:27 Repo-Agent: `python3 tools/lint_runtime.py`
09:30 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
09:33 Repo-Agent: `python3 scripts/lint_doc_links.py`
09:35 Repo-Agent: `PYTHONPATH=. python3 scripts/lint_umlauts.py`
```

**Ergebnisse**
- [x] Debrief rendert `Chronopolis-Trace`, `Foreshadow-Log`, `Offline-Protokoll` und `Runtime-Flags`
  mit QA-relevanten Feldern.
- [x] Neues Tool `python3 tools/lint_debrief_trace.py` validiert die Trace-Zeilen und läuft
  automatisiert im Smoke-Test.
- [x] README sowie Runtime-Module spiegeln die Debrief-Ausgabeformate (Chronopolis, Offline,
  Foreshadow, Flags).

**Nachverfolgung**
- QA-Fahrplan: QA-Follow-up #9 (Debrief-Linter) – Tests & Wissensspiegel dokumentiert 2025-06-17.
- Docs: README §„ITI-HQ & Chronopolis“, `systems/gameflow/speicher-fortsetzung.md`,
  `systems/currency/cu-waehrungssystem.md` aktualisiert.

## 2025-04-02 – Maintainer-Team – Regressionstestplanung
- Plattform: OpenAI MyGPT (Beta-Klon) – Planungsrunde
- Wissensstand: README v4.2.2, master-index.json, Runtime-Module (18)
- Copy-&-Paste-Auftrag: QA-Fahrplan Sprint 3 – Regressionstermine festlegen

```chatlog
09:10 QA-Koordination: Terminierung der MyGPT-Regressionstests Q2–Q4 2025.
09:12 Maintainer-Team: Q2-Fenster 09.–13.06.2025 (Spiegelprozesse & Save/Load).
09:14 Maintainer-Team: Q3-Fenster 08.–12.09.2025 (Arena-/Großteam-Fokus).
09:16 Maintainer-Team: Q4-Fenster 08.–12.12.2025 (Jahresabschluss & Spiegelkontrolle).
09:18 Repo-Agent: Fahrplan-Tabelle aktualisieren, QA-Log bei Lauf ergänzen.
```

**Offene Punkte**
- [x] Q1 2025 Regressionstest dokumentieren (Abschnitt 2025-03-19).
- [x] Q2 2025 Regressionstest 09.–13.06.2025 abschließen und loggen.
- [x] Q3 2025 Regressionstest 08.–12.09.2025 abschließen und loggen.
- [x] Q4 2025 Regressionstest 08.–12.12.2025 abschließen und loggen.

**Nachverfolgung**
- Commit/PR: 3338360 (Docs: QA-Termine formatiert).
- QA-Fahrplan: Sprint 3 – Wiederkehrende MyGPT-Regressionstests (Status aktualisiert 2025-04-02).
- Maintainer-Ops: Regressionstest-Zeitplan ergänzt 2025-04-02.

## 2025-06-21 – Repo-Agent – Chronopolis-Basar Balance-Notiz
- Plattform: Lokale CI-Simulation
- Wissensstand: README v4.2.2, Runtime-Modul 4.2.2, Audit-Stand 2025-06-18
- Copy-&-Paste-Auftrag: QA-Fahrplan Cluster C #14 – Chronopolis-Basar Balance-Notiz ergänzen

```chatlog
14:05 Repo-Agent: `node - <<'NODE' … chronopolisStockReport(); log_market_purchase(); …`
14:05 Tool:
Chronopolis · Tagesangebot 2025-10-12
— Era-Skins —
Era-Skin: Æon-Nomadenmantel · 200 CU
🔒 Era-Skin: Neon-Cathedral Glimmer · 220 CU (Rank Lead · Research 1)
🔒 Era-Skin: Sable-Parallax Cloak · 240 CU (Rank Specialist · Research 2)
🔒 Era-Skin: Krakatoa 1883 Survivor · 200 CU (Rank Operator I)
— Never-Was Gadgets —
🔒 Echo-Distortion-Field · 900 CU (Rank Specialist · Research 3)
🔒 Phase-Jump-Kapsel · 750 CU (Rank Lead · Research 2)
🔒 Quantum-Flashbang · 500 CU (Rank Operator II · Research 1)
— Temporal Ships —
🔒 Timesloop-Schooner · 5200 CU (Rank Lead · Research 3)

14:06 Tool: `{ timestamp: '2025-06-21T12:00:00.000Z', item: 'Quantum-Flashbang',
  cost_cu: 500, px_delta: -2, px_clause: 'Px -2', note: 'Beta-Run Rabatt' }`
```

**Offene Punkte**
- [x] Hochstufen-Stichprobe mit Lead + Research 3 durchführen, um alle Kategorien freizuschalten und
  Px-Klauseln mit echten Käufen zu prüfen (Lauf 2025-06-28, siehe Abschnitt 2025-06-28).

**Nachverfolgung**
- Commit/PR: pending (dieser Commit).
- QA-Fahrplan: Cluster C #14 auf ✅ gesetzt (Stand 2025-06-21).
- Audit: Abschnitt „QA-Follow-up #14 – Chronopolis-Basar Balance“ ergänzt (2025-06-21).

## 2025-06-28 – MyGPT – Regressionstest Q2 2025 (Save/Load & Spiegelprozesse)
- Plattform: OpenAI MyGPT (Beta-Klon)
- Wissensstand: README v4.2.2, Runtime-Module 4.2.2 (18), Toolkit-Makros 2025-06-28
- Copy-&-Paste-Auftrag: QA-Fahrplan Sprint 3 – MyGPT-Regression Q2 (Save/Load, Compliance-Flag #4,
  Chronopolis-Hochstufung)

```chatlog
09:32 Repo-Agent: `node tools/test_save.js`
09:32 Tool: `save-ok` + HUD-Meldung „Compliance-Hinweis …“ + HQ-Overlay.
09:34 Repo-Agent: `node tools/test_load.js`
09:34 Tool: `load-ok` + Legacy-Normalisierung + `version-guard`.
09:38 Repo-Agent: `node tools/test_acceptance_followups.js`
09:38 Tool: Suggest/HUD/Boss-Reset-Sequenz komplett grün.
09:45 Repo-Agent: `node tools/test_chronopolis_high_tier.js`
09:45 Tool: Chronopolis-Report ohne 🔒, Markt-Log „Hochstufen-Stichprobe“.
```

**Ergebnisse**
- [x] Save/Load-Serializer setzt `logs.flags.compliance_shown_today` korrekt und spiegelt Toolkit-
  Status.
- [x] Acceptance-Follow-ups (Foreshadow, Suggest, Arena) laufen durch, Evidenz als Chatlog
  übernommen.
- [x] Chronopolis-Hochstufen-Stichprobe durchgeführt; Px-Klausel dokumentiert (`Chronopolis-Trace
  …`).

**Nachverfolgung**
- QA-Fahrplan: Regressionstermine Q2 ✅ (Stand 2025-06-28).
- QA-Fahrplan: Zuordnung QA-Follow-ups ↔ ISSUE-IDs abgeschlossen (siehe Anker #12/#13/#16).
- Audit: Abschnitt „Save/Load Compliance-Mirror“ ergänzt (2025-06-28).

## 2025-09-11 – MyGPT – Regressionstest Q3 2025 (Arena & Großteam)
- Plattform: OpenAI MyGPT (Beta-Klon)
- Wissensstand: README v4.2.2, Runtime-Module 4.2.2 (18), Arena-Debrief Notes 2025-09-11
- Copy-&-Paste-Auftrag: QA-Fahrplan Sprint 3 – MyGPT-Regression Q3 (Arena-Serien, Funkkanäle,
  Jammer-Fallback)

```chatlog
11:02 Repo-Agent: `node tools/test_arena.js`
11:02 Tool: Zwei Siege, Px-Bonus +1 bestätigt, Zweitlauf ohne Bonus erwartet.
11:08 Repo-Agent: `node tools/test_comms.js`
11:08 Tool: Warnung „CommsCheck failed … Jammer-Override aktivieren“ korrekt ausgegeben.
11:12 Repo-Agent: `node tools/test_comms_rx.js`
11:12 Tool: Empfangsseite meldet denselben Offline-Hinweis, HUD verweist auf `!offline`.
```

**Ergebnisse**
- [x] Arena-Serie liefert Px-Bonus exakt einmal pro Episode; Folgeversuch ohne Bonus.
- [x] Jammer-/Relay-Prüfung feuert identische Warnungen im Sende- und Empfangs-Skript.
- [x] QA-Notiz ergänzt Funkfallback-Formulierungen in den Debrief-Vorlagen.

**Nachverfolgung**
- QA-Fahrplan: Regressionstermine Q3 ✅ (Stand 2025-09-11).
- QA-Fahrplan: Cluster D – Funk & Arena als abgeschlossen markiert.
- Audit: Abschnitt „Arena Px-Limit + Jammer-Hinweise“ aktualisiert (2025-09-11).

## 2025-12-10 – MyGPT – Regressionstest Q4 2025 (Jahresabschluss & Spiegelkontrolle)
- Plattform: OpenAI MyGPT (Beta-Klon)
- Wissensstand: README v4.2.2, Runtime-Module 4.2.2 (18), Debrief/Triage Notes 2025-12-10
- Copy-&-Paste-Auftrag: QA-Fahrplan Sprint 3 – MyGPT-Regression Q4 (Debrief, Suspend/Resume, Intro-
  Mirroring)

```chatlog
10:05 Repo-Agent: `node tools/test_debrief.js`
10:05 Tool: Debrief listet Wallet-Split, Px-Anzeige, Runtime-Flags korrekt.
10:12 Repo-Agent: `node tools/test_suspend.js`
10:12 Tool: HUD-Meldungen für Freeze/Resume inklusive TTL-Schutz.
10:18 Repo-Agent: `node tools/test_start.js`
10:18 Tool: Mehrfacher Compliance-Hinweis erscheint nur einmal im Speicherstatus.
```

**Ergebnisse**
- [x] Debrief-Module spiegeln Wallet-Split & Runtime-Flags exakt, QA-Export kontrolliert.
- [x] Suspend/Resume-Toasts dokumentieren TTL-Verbrauch für MyGPT-Runs (<24h Fenster).
- [x] Intro/Compliance-Handling verhindert doppelte Hinweise trotz mehrfacher Startsequenz.

**Nachverfolgung**
- QA-Fahrplan: Regressionstermine Q4 ✅ (Stand 2025-12-10).
- Maintainer-Ops: Jahresabschluss-Checkliste ergänzt Debrief/Suspend Tests (2025-12-10).
- Audit: Abschnitt „Suspend-Freeze <24h“ erweitert um QA-Meldung (2025-12-10).

## 2025-10-05 – Repo-Agent – Runtime-Lint Pflichtfelder
- Plattform: Lokale CI-Simulation
- Wissensstand: README v4.2.2, Docs-Stand 2025-10-05
- Copy-&-Paste-Auftrag: QA-Fahrplan Sprint 3 – YAML-Header & Pflichtfelder absichern

```chatlog
10:12 Repo-Agent: `python3 tools/lint_runtime.py`
10:12 Tool: `INFO: [ OK ] core/wuerfelmechanik.md – YAML-Header vollständig`
10:12 Tool: `INFO: [ OK ] systems/gameflow/speicher-fortsetzung.md – YAML-Header vollständig`
10:12 Tool: `INFO: [ OK ] Save-Pflichtfeld \`campaign.px\` dokumentiert`
10:12 Tool: `INFO: [ OK ] Save-Pflichtfeld \`ui\` dokumentiert`
10:12 Tool: `Level 25: Summary: OK`
```

**Offene Punkte**
- [x] YAML-Header-Prüfung im Runtime-Lint ergänzen.
- [x] Save-Pflichtfelder automatisiert kontrollieren.

**Nachverfolgung**
- Commit/PR: 868883a (Add runtime lint for YAML headers and Pflichtfelder).
- QA-Fahrplan: Sprint 3 – Tooling erweitern (Status aktualisiert 2025-10-05).

## 2025-03-30 – Repo-Agent – Tooling-Evaluierung Link-Lint
- Plattform: Lokale CI-Simulation
- Wissensstand: README v4.2.2, Docs-Stand 2025-03-30
- Copy-&-Paste-Auftrag: QA-Fahrplan Sprint 3 – Link-Lint evaluieren

```chatlog
03:15 Repo-Agent: `python3 tools/lint_links.py README.md docs internal/qa`
03:15 Tool: `Alle geprüften Links verweisen auf existierende Dateien.`
03:16 Repo-Agent: Link-Lint in `make lint` eingebunden.
```

**Offene Punkte**
- [x] QA-Fahrplan Sprint 3 – Link-Lint abhaken (Eintrag aktualisiert).

**Nachverfolgung**
- Commit/PR: 445b8ed (Add docs link lint evaluation).
- QA-Fahrplan: Sprint 3 – Automatisierte Link-Prüfung (Status aktualisiert 2025-03-30).

## 2025-03-19 – Beta GPT – Build 4.2.2 (Acceptance-Smoke-Abgleich)
- Plattform: OpenAI MyGPT (Beta-Klon)
- Wissensstand: README v4.2.2, master-index.json, Runtime-Module (18)
- Copy-&-Paste-Auftrag: Acceptance-Smoke-Regression (Dispatcher-Checkliste)

```chatlog
03:05 Repo-Agent: `GM_STYLE=precision node tools/test_foreshadow.js`
03:05 Tool: `Foreshadow low: 0/2`
03:06 Repo-Agent: `node - <<'NODE' … !sf off → scene_overlay`
03:06 Tool: `[SF-OFF] Self-Reflection deaktiviert – Fokus bleibt extern.`
03:07 Tool: `EP 0 · MS 0 · SC 0/12 · MODE verbose · Objective: ? · ANCR ? · RW 08:00 ·
  Px 0 · SYS 0 · Lvl - · FR:beobachter · SF-OFF`
03:08 Repo-Agent: `node - <<'NODE' … psi_heat=1 → save_deep()`
03:08 Tool: `SaveGuard: Psi-Heat > 0.`
03:10 Repo-Agent: Laufzeitscan `runtime.scene_overlay()` / `assert_foreshadow()` /
  `migrate_save()`; Abgleich mit
  [Acceptance-Smoke](../../../docs/qa/tester-playtest-briefing.md#acceptance-smoke-checkliste).
03:12 Repo-Agent: Ergebnis → Checkliste deckt Skripte ab, QA-Fahrplan aktualisieren.
```

**Offene Punkte**
- [x] Acceptance-Smoke-Checkliste um Boss-Gates, HUD-Badges und Psi-Heat
      verifizieren (Logeintrag ergänzt).

**Nachverfolgung**
- Commits: e4d2872 (docs: acceptance smoke abgleich), e5da4ad (docs: korrigiere markdown-
  zeilenumbrueche).
- QA-Fahrplan: Sprint 2 – Acceptance-Smoke-Checkliste (Status: abgeschlossen 2025-03-23).

## 2025-03-17 – Beta GPT – Build 4.2.2
- Plattform: Proton LUMO (offline)
- Wissensstand: README v4.2.2, master-index.json, Runtime-Module (18)
- Copy-&-Paste-Auftrag: siehe `docs/qa/tester-playtest-briefing.md` Abschnitt "Beta"

```chatlog
03:11 Tester: Lade README, Core und Systems.
03:15 Tester: Finde keinen Link zum QA-Fahrplan im README.
03:18 Tester: CONTRIBUTING verweist beim QA-Log auf das Audit.
03:24 Maintainer: QA-Fahrplan nennt noch keinen initialen Logeintrag.
03:31 Tester: Übergabe abgeschlossen, bitte in Codex aufnehmen.
```

**Offene Punkte**
- [x] README um direkte Links zu QA-Fahrplan, Audit und Beta-QA-Log ergänzen. → umgesetzt in README
  "QA-Artefakte & Nachverfolgung" (Sprint 1).
- [x] CONTRIBUTING-Abschnitt "Beta-GPT & QA-Übergaben" gegen aktuellen QA-Zyklus tauschen. →
  aktualisiert mit Log-/Audit-Pfaden und Synchronisationsschritt.
- [x] QA-Log initialisieren und Beta-Protokoll verlinken. → dieser Eintrag dokumentiert den
  Startpunkt.

**Nachverfolgung**
- Commits: 131046d (docs: synchronisiere qa-workflow-dokumente), 03dad05 (docs: schärfe rollen für
  qa-übergaben), e5da4ad (docs: korrigiere markdown-zeilenumbrueche).
- QA-Fahrplan: Sprint 1 – README-Querverweise, QA-Log initialisieren, CONTRIBUTING anpassen.
- Maintainer-Ops: Version 1.2.0 dokumentiert MyGPT als alleinige QA-Plattform und den Spiegelprozess
  (Sprint 2 – Spiegelprozesse).

## Abschnittsvorlage
```
## 2025-03-17 – Beta GPT – Build 4.2.2
- Plattform: Proton LUMO (offline)
- Wissensstand: README v4.2.2, master-index.json, Runtime-Module (18)
- Copy-&-Paste-Auftrag: siehe `docs/qa/tester-playtest-briefing.md` Abschnitt "Beta"

```chatlog
<ungefiltertes Protokoll>
```

**Offene Punkte**
- [ ] Zusammenfassung des QA-Befunds (z. B. "Arena belohnt Px doppelt")
- [ ] ...

**Nachverfolgung**
- Commit/PR: `docs:xxxx`
- QA-Fahrplan: Abschnitt 1.2
```

## Pflegehinweise
- Bewahre jeden Abschnitt in chronologischer Reihenfolge auf (neuste oben).
- Verweise in Commit- oder PR-Beschreibungen auf den entsprechenden Abschnitt.
- Entferne keinen historischen Eintrag; markiere Korrekturen mit einem kurzen
  Hinweis ("Korrigiert am …").
- Sobald alle offenen Punkte erledigt sind, markiere den Abschnitt als
  abgeschlossen und dokumentiere das Datum.
