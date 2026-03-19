---
title: "ZEITRISS QA-Audit 2025"
version: 1.0.25
tags: [meta, qa]
---

# ZEITRISS QA-Audit 2025

## Audit-Update 2026-03-01 – Repo-Nachcheck vor Playtest

- Vollständiger Repo-Nachcheck nach Pflichtsuite durchgeführt (`make lint`,
  `make test`, `bash scripts/smoke.sh`, `python3 tools/lint_runtime.py`,
  `GM_STYLE=verbose python3 tools/lint_runtime.py`,
  `python3 scripts/lint_doc_links.py`, `python3 scripts/lint_umlauts.py`).
- Ergebnis: keine neuen Befunde, keine Drift zwischen Runtime-Content,
  Wissensmodulen und QA-Layern festgestellt.
- Playtest-Freigabe aus Repo-Sicht unverändert grün; Follow-up erst bei neuen
  Tester-Logs erforderlich.

## Audit-Update 2026-02-26 – Fahrzeugfenster-Closure verifiziert

- Runtime-Härtung für Fahrzeugkontexte bestätigt: Alias-Felder und
  verschachtelte Payloads lösen die Chronopolis-/Temporal-Ausnahme zuverlässig
  aus.
- Rift-Guard bestätigt: Bei aktiven Rift-Ops bleiben temporale und
  Chronopolis-Legenden blockiert („Rift-Protokoll aktiv“), inklusive Debrief-
  Spiegel.
- QA-Dokumentation ist jetzt vollständig synchron (QA-Log, Fahrplan und Audit
  führen denselben Closure-Stand).

## Audit-Update 2027-03-24 – SSOT-Nachlauf (HUD-Level sichtbar, Px situativ)

- UX-Forderung erfolgreich gespiegelt: Charakterlevel bleibt als dauerhafte
  HUD-Information sichtbar.
- Paradoxon-Anzeige wurde auf situative Einblendung umgestellt; `🌀` erscheint
  nur bei Px-relevanten Ereignissen statt permanent im Basis-Overlay.
- Core-Quickrefs und HUD-Referenztabellen sind wieder deckungsgleich
  (Handbuch/SL-Referenz/HUD-System).

## Audit-Update 2027-03-23 – SSOT-Nachlauf (Paradoxon-Portal-Icon)

- Symbolik nach UX-Feedback nachgeschärft: Paradoxon nutzt durchgängig `🌀`
  als Portal-/Rift-Marker.
- TK-Cooldown wurde auf `✋` entkoppelt, sodass keine visuelle Doppelbelegung
  mit dem zentralen Progress-Signal besteht.
- Konsistenz über Core/HUD/Gameplay/Toolkit/Zustände bestätigt; Folgeauftrag
  für historische QA- und Briefing-Beispiele angelegt.

## Audit-Update 2027-03-22 – SSOT-Nachlauf (Icon-/Meilenstein-Drift)

- Rückmeldungsbasierter Vollscan über Core/HUD/Gameplay/Toolkit durchgeführt;
  verbliebene Driftstellen für Chronopolis-Level-10-Anker und Iconbelegung
  bereinigt.
- Core-Meilensteintexte führen den Chronopolis-Schlüssel nun explizit als
  Level-10-Übergabe.
- HUD-Symbolik wurde auf Stern-Notation (`☆`) für Rift-Bonus harmonisiert und
  als Zwischenstand mit eindeutiger Icon-Belegung dokumentiert.
- Folgeauftrag protokolliert: repo-weiter Icon-Audit über narrative Samples,
  um Restdrift außerhalb der zentralen Tabellen systematisch zu schließen.

## Audit-Update 2027-03-21 – SSOT-Nachlauf (Core-Konsistenz)

- Core-Quickformate nach Closure erneut geprüft und gezielt nachgeschärft:
  Chronopolis-Schlüssel bei Level 10 im Spielerfluss ergänzt,
  Spielstart-Textblöcke zwischen Handbuch (Spielerinput) und SL-Referenz
  (Dispatcher-Invarianten) sauber getrennt.
- Schwierigkeit/Rift-Bonus-Visualisierung in den Quickformaten auf weiße
  Sterne (☆) vereinheitlicht; Blitzdarstellung als Driftquelle entfernt.
- QA-Folgeauftrag angelegt: repo-weiter Symbol-/Stilabgleich für verbleibende
  Difficulty-Darstellungen außerhalb der Core-Quickformate.

## Update 2027-03-20b – Runtime-Entkopplung von Setup-/Wartungshinweisen

- `core/sl-referenz.md` bereinigt den Strukturteil um Repo-/Setup-Hinweise
  (`master-index.json`, Wissensspeicher-Bestückung, Landingpage-Betrieb), um
  Runtime-Fokus der Spielleitung zu sichern.
- `core/spieler-handbuch.md` entfernt den Wartungshinweis zur README-Pflege aus
  dem Schnellzugriff auf Regelteile.
- Ergebnis: Trennung zwischen Runtime-Content und Betriebsdokumentation ist
  wieder konsistent; operative Setup-Anweisungen verbleiben außerhalb der
  Wissensmodule.

## Update 2027-03-20 – SSOT-Pipeline Durchlauf 5 abgeschlossen (Konfliktprüfung & Closure)

- Suchanker-Set (`optional`, `Pflicht`, `empfohlen`, `Rift`, `Belohnung`,
  `CU`, `Scaling`) wurde gegen Core/README/Gameplay/Systems geprüft.
- Dabei gefundene Restdrift wurde bereinigt: Startwurf-Verweise
  (`rift_artifact_variant=start_roll`) sind aus `core/sl-referenz.md` und
  `systems/toolkit-gpt-spielleiter.md` entfernt; der Artefakt-Drop bleibt
  konsistent boss-only in Szene 10.
- Restpunkt „Single-Source-of-Truth-Pass" wechselt auf **abgeschlossen**, da
  Closure-Gate (Plan/Audit/Log-Sync + Pflichttestpaket) erfüllt ist.

## Update 2027-03-19 – SSOT-Pipeline Durchlauf 4 abgeschlossen (Systems-Pass)

- `systems/currency/cu-waehrungssystem.md` markiert die CU-Formel und Px-5-
  `ClusterCreate()` jetzt explizit als MUSS-Invarianten.
- `systems/gameflow/speicher-fortsetzung.md` verankert SaveGuard HQ-only,
  Px-Quelle/Reset-Logik und Currency-Sync als bindende SSOT-Anker.
- `systems/toolkit-gpt-spielleiter.md` führt MUSS/SOLL/KANN für optionale
  Komfortpfade vs. Kerninvarianten aus, damit der Spielleiter-Loop nicht driftet.
- Restpunkt bleibt auf „in Umsetzung", da die abschließende Konfliktprüfung/
  Closure als letzter Pipeline-Schritt noch aussteht.

## Update 2027-03-18 – SSOT-Durchlauf 3a (Artefakt-Balance nachgeschärft)

- Die Gameplay-Regeln führen Rift-Artefaktwürfe wieder eindeutig als
  Boss-only-Mechanik (Szene 10).
- Die zuvor erwähnte Startwurf-Hausregel wurde aus dem Regeltext entfernt, um
  Balancing-Drift zwischen Runs zu vermeiden.
- Stoppuhr-Artefakte bleiben als Plot-Element zulässig, ohne den Boss-Drop zu
  ersetzen.

## Update 2027-03-18 – SSOT-Pipeline Durchlauf 3 abgeschlossen (Gameplay-Pass)

- `gameplay/kampagnenuebersicht.md` führt den Quickstart jetzt explizit als
  optionalen Zugriffspfad ohne Regeländerung und spiegelt damit den Core-Kanon.
- `gameplay/kampagnenstruktur.md` ergänzt einen SSOT-Ankerblock mit
  MUSS/SOLL/KANN; damit sind Boss-Rhythmus, Px-5-`ClusterCreate()` und
  CU-Formel als Invarianten direkt im Gameplay-Loop markiert.
- Der Restpunkt bleibt auf „in Umsetzung", da der Systems-Pass und die
  abschließende Konfliktprüfung/Closure noch ausstehen.

## Update 2027-03-17 – SSOT-Pipeline Durchlauf 2 abgeschlossen (Anker-Sync README/Core)

- Der README-Spiegel folgt jetzt dem zuvor extrahierten Core-Kanon: Px bleibt
  Belohnungssystem, Px 5 triggert `ClusterCreate()` und die CU-Formel ist für
  Core/Rift identisch benannt.
- Optionalität ist in der Landingpage klar als zusätzlicher Zugriffspfad
  markiert; bindende Kernregeln (Boss-Timing, SaveGuard HQ-only) bleiben
  unverändert.
- Muss/Soll/Kann ist als Redaktionsnorm in README ergänzt und dient als
  semantischer Anker für die nächsten Modul-Pässe.
- Der Restpunkt verbleibt auf „in Umsetzung", bis Gameplay- und Systems-Pass
  plus Closure-Gate abgeschlossen sind.

## Update 2027-03-16 – SSOT-Pipeline Durchlauf 1 abgeschlossen (Kanon-Extraktion)

- Der erste Durchlauf der SSOT-Pipeline ist durchgeführt und als Kanon-Mini-Glossar im
  Restkatalog dokumentiert (Rift-Risiko, Belohnung, optionale Module, Muss/Soll/Kann).
- Als kanonische Quellen bleiben `core/sl-referenz.md` und `core/spieler-handbuch.md`;
  README/Gameplay/Systems werden in den Folgedurchläufen ausschließlich gegen diese
  Begriffe harmonisiert.
- Der Restpunkt bleibt bewusst auf "in Umsetzung", bis die nachgelagerten Sync-Pässe
  inklusive Closure-Gate und Pflichttestpaket abgeschlossen sind.

## Update 2027-03-15 – Onboarding-Entkopplung abgeschlossen

- Restkatalog 2027 führt den KI-First-Onboardingpfad jetzt als **abgeschlossen**:
  Referenzfluss bleibt in README + Setup-Guide, das Toolkit bleibt frei von
  Setup-/Bedienanweisungen.
- QA-Fahrplan-Backlog wurde entsprechend geschärft; offen bleiben nur
  Single-Source-of-Truth-Restpunkte und Stil-/Sprach-Feinschliff.
- Der Abschlussstatus ist im QA-Log dokumentiert und als Folgeanker für die
  nächsten Restkatalog-Zyklen referenziert.

## Update 2027-03-15 – SSOT-Modulpipeline für den letzten Restpunkt gestartet

- Für den verbleibenden Restkatalog-Punkt „Single-Source-of-Truth-Pass"
  existiert jetzt ein verbindlicher, sequenzieller Durchlauf (5 Stufen), damit
  alte und neue Regelmodule nicht mehr gegeneinander driften.
- Kanonische Quellenreihenfolge ist festgelegt: `core/sl-referenz.md` und
  `core/spieler-handbuch.md` definieren das Quickformat; README, Gameplay- und
  Systems-Module werden entlang dieser Quelle harmonisiert.
- Der Fahrplan führt die feste Modulreihenfolge für die nächsten QA-Zyklen; der
  Restpunkt darf erst auf „abgeschlossen" wechseln, wenn Restkatalog, Fahrplan,
  Audit und QA-Log synchron aktualisiert sind und das Pflichttestpaket grün ist.

## Update 2027-03-14 – KI-First-Onboarding & Economy-/Scaling-Checkliste

- README und Setup-Guide führen den KI-First-Onboardingfluss
  (Setup → Wissensslots → Sessionstart → HQ-zentrierter Loop) als
  Referenzstrecke; Toolkit bleibt auf Spielleitlogik fokussiert.
- QA-Fahrplan bündelt Economy-/Scaling-Sicherungen als verpflichtende
  Checkliste (Seed-Caps/Merge, Foreshadow-Gates, Save/Load-Trace,
  Runtime-Lintläufe).
- Restkatalog 2027 markiert Punkt 2 und 3 als „in Umsetzung" und verweist auf
  diesen Zyklus.

## Update 2027-03-08 – Seed-Caps & Core-Intro-Wording

- Runtime-Spiegel präzisiert: Rift-Mods deckeln ab sofort sowohl den
  Schwellenbonus (`sg_bonus = min(3; offene Seeds)`) als auch den Loot-Multi
  (`cu_multi = min(1,6; 1 + 0,2 × offene Seeds)`).
- Kampagnenstruktur, Save-/Fortsetzungsmodul und Toolkit-Makro `apply_rift_mods_next_episode()`
  sind auf dieselbe Cap-Logik synchronisiert.
- `core/zeitriss-core.md` korrigiert in der Einführung den Epochenbezug auf
  „jede Episode", damit Missions-/Episodenhierarchie konsistent bleibt.

## Update 2026-01-14 – Beta-KI Playtest 2026-01-14 übernommen

- QA-Log 0.4.31 archiviert das vollständige Playtest-Protokoll inkl. Test-Save
  v6, HUD/Trace-Belegen und dem HQ-Abgleich nach Import.
- QA-Fahrplan 1.20.0 ergänzt das Maßnahmenpaket 2026-01-14 mit Issues #1–#9 und
  markiert Issue #8 als nicht anwendbar (Auftraggeber-Entscheid, Self-Hosted,
  kein Store, 18+).
- Offene Punkte: Dokument-Drift Rift-Map, Pre-City-Hub Save-Regel, Seed-Merge-
  Auswahlregel, SaveGuard-Prioritäten, Toast-Prioritäten, UI-Override-Hinweis,
  Test-Save-Integration.

## Update 2026-01-14 – Repo-Agent – Action-Contract filmisch geschärft

- Action-Contract präzisiert: filmische Beats, abstrakte Technik, keine
  Schritt-für-Schritt-Anleitungen. Änderungen in README, Toolkit und
  Kampagnenstruktur gespiegelt.
- QA-Testprompt ergänzt: pro Phase neue Szenarien und Konfliktvarianten.
- QA-Fahrplan 1.20.1 und QA-Log 0.4.32 synchronisiert.
- **Referenzen:** README, Toolkit, Kampagnenstruktur, Tester-Briefing,
  QA-Fahrplan/QA-Log.

## Update 2027-03-07 – Local-Uncut & LM-Studio 2026-05 gespiegelt

- QA-Fahrplan 1.18.0 führt das Maßnahmenpaket „Local-Uncut & LM-Studio 2026-05"
  als abgeschlossen; Wissensmodule spiegeln Sampling-Presets, RAG-Trim und den
  Template-Guard für LM-Studio lokal.
- README und Toolkit dokumentieren die beiden gpt-oss-20b-Presets (ZEITRISS-
  PLAY, Noir/Interlude), Kontextprofile 16k/24k/32k mit GPU-/CPU-Defaults sowie
  das Big-RAG-Limit 4 (Affinity 0,74, Chunk 650, Overlap 96). Template-Braces
  werden als No-Op behandelt, um lokale Modelle vor Syntax-Ausgaben zu schützen.
- QA-Log 0.4.29 hält die Pflichtsuite fest; nach dem Merge sind keine offenen
  Punkte aus dem Paket mehr zu verfolgen.

## Update 2027-03-06 – Copy-Paste-QA 2026-12 abgeschlossen

- QA-Fahrplan 1.15.0 und QA-Log 0.4.28 markieren alle elf Copy-Paste-QA 2026-12-Issues als
  erledigt (Dispatcher-Strings, Wrapper-Import, arc_dashboard-Guard, Self-Reflection-M5/M10,
  HUD-Events, Toast-Budget, Rift-Seed-Cap, Economy/Arena/Chronopolis-Load, deterministische
  Save-/Trace-Timestamps).
- Regressionstests sichern die deterministischen Zeitmarken, HUD-Autostamps, Chronopolis-Trace
  sowie Economy- und Arena-Merge ab; der Gold-Roundtrip bleibt ohne Containerverlust.
- Wissensmodule und Runtime-Doku spiegeln HUD/Self-Reflection/Seed-Cap/Economy-Guards; offene
  Compliance- oder Format-Themen bestehen nicht.

## Kontext und Auftrag

Die QA-Crew hat den Systemtest zu **ZEITRISS 4.2.2** mit Schwerpunkt auf
Systemkohärenz, Balance, HQ-Abläufe und urbane Interaktionen dokumentiert. Dieses
Audit bündelt die Erkenntnisse, bewertet den aktuellen Umsetzungsstand und
priorisiert die nächsten Entwicklungsschritte. Grundlage sind die aufgeführten
Testbeobachtungen sowie der Repositorystand `c9a4da2`.

## Rollen & Artefakte

- **Tester** führen Playthroughs in den vorgesehenen KI-Instanzen durch
  und kopieren das Ergebnis unverändert in das QA-Log unter
  `internal/qa/logs/2025-beta-qa-log.md`.
- **Maintainer:in (Solo-Setup 2025)** führt alle Beta-KI-Tests durch,
  indem der vorbereitete Testprompt in den Beta-Klon geladen wird. Die KI
  spielt den vollständigen QA-Lauf autonom durch und liefert strukturierte
  `ISSUE`-, `Lösungsvorschlag`-, `To-do`- und `Nächste Schritte`-Blöcke. Die
  komplette Antwort wird unverändert an Codex übergeben, der die Ergebnisse in
  Repo-Tasks und Dokumentationen überführt. Gleichzeitig prüft die Maintainer-
  Rolle, ob alle 19 Wissensspeicher-Module geladen sind (Spieler-Handbuch +
  18 Runtime-Module) und ob Laufzeitänderungen
  als Regel-/Pseudocode-Spiegel in den Runtime-Dokumenten hinterlegt wurden.
- **Codex (Repo-Agent)** überträgt beschlossene Maßnahmen in Branches, Commits
  und QA-Protokolle. Änderungen an Runtime-Content und Dev-Dokumentation bleiben
  strikt getrennt.
- **Audit-Archiv** liegt in `internal/qa/audits/ZEITRISS-qa-audit-2025.md`;
  vollständige Protokolle befinden sich im QA-Ordner unter
  `internal/qa/`.

## Methodik

- Analyse der gelieferten Testnotizen (Solo bis Großgruppe, Level 3–100) mit
  Schwerpunkt auf PvP-Arena, HQ-Progression und urbanen Szenarien.
- Stichprobenhafte Abgleiche im Repository (z. B. Modul 6 Kampagnenstruktur,
  Toolkit-Flags für `debug_rolls`, Terminologie „Heat“).
- Priorisierung nach Auswirkung auf Spielbalance, UX und technische Konsistenz.

## Gesamtbewertung

Die Testreihe bestätigt, dass der aktuelle Build stabil läuft, jedoch mehrere
Kernsysteme inkonsistent benannt oder nur teilweise abgesichert sind. Besonders
kritisch sind widersprüchliche Modulnummern, farmbare Paradoxon-Belohnungen in
der Arena und das uneinheitliche „Heat“-Vokabular, das Spieler wie Tools
verwirrt. Ohne Korrektur gefährden diese Punkte die Anschlussfähigkeit von
Regelreferenzen, die Progressionsökonomie und das Balancing in
Hochstufen-Spielrunden.

## Update 2026-11-04 – Economy-Audit-Status Sync

- QA-Fahrplan 1.13.34 markiert das Copy-Paste-QA-Issue #12 (Chronopolis/Economy-
  Audit) als ✅ erledigt; der HQ-Save schreibt den `economy_audit`-Trace
  kanonisch.
- QA-Log 2026-11-04 dokumentiert den Abgleich und den Pflicht-Testlauf.

## Update 2025-11-04 – Deepcheck-Fortsetzung & Fahrplan 1.8.7

- QA-Fahrplan wurde auf Version 1.8.7 angehoben; die Deepcheck-Tabelle führt
  nun die Läufe vom 2025-11-03 und 2025-11-04.
- QA-Log 2025-11-04 dokumentiert die Synchronisation sowie den erfolgreichen
  Pflicht-Testlauf (`make lint`, `make test`, Smoke- und Linter-Skripte).
- Wissensmodule (README, Toolkit, Systems) bleiben frei von störenden
  QA-Anweisungen; keine Laufzeitänderungen notwendig.

## Update 2025-11-05 – QA-Evidenz-JSON-Handshake

- Maintainer liefern den Beta-KI-Testprompt jetzt als JSON-Block, prüfen
  ihn in einer zweiten ZEITRISS-Instanz und stellen den abgeglichenen Datensatz
  bereit; Codex übernimmt die Artefakte unverändert.
- Evidenzprotokoll `internal/qa/evidence/2025-beta-gpt-evidenz.md` Version 0.2.0
  enthält die JSON-Hand-offs für die Läufe 2025-07-05, 2025-07-18, 2025-10-15
  und 2025-10-28.
- QA-Log markiert die entsprechenden „QA-Referenzen“-Checkboxen als erledigt;
  Audit-Abschnitte verweisen fortan auf das Evidenzprotokoll statt auf offene
  Maintainer-Lieferungen.

## Update 2025-11-06 – Regressionsevidenz Audit-Maßnahmen #13–#20

- QA-Log 2025-11-06 dokumentiert die Regressionstests für Chronopolis-Stock-
  Gating, Signalspace-Guards, Urban-Quick-Card, HQ-Moments, Rift-Boss-Loot,
  Charaktercap und Arena-Großteams.
- Audit-Einträge #13–#20 verlinken auf den neuen QA-Log-Abschnitt und streichen
  die Platzhalter „QA-Log-Eintrag folgt“.
- QA-Fahrplan 2025 aktualisiert die Referenzspalten der betroffenen
  Maßnahmenübersichten entsprechend.

## Update 2025-11-26 – Simulativer Acceptance-/Save-Lauf

- QA-Log 2025-11-26 spiegelt den Maintainer-Lauf (Solo/Koop/PvP, Mission 5,
  Acceptance-Smoke) mit Save-V6-Beispiel und neun Issue-Blöcken.
- QA-Fahrplan 1.8.8 ergänzt Deepcheck-Tabelle und neues Maßnahmenpaket
  2025-11-26 (Dokulücken zu Self-Reflection-Reset, Arena-Cross-Mode,
  Suggest-Modus, Chronopolis-Warnung, Array-only-Saves, Psi-Heat-Reset).
- Maßnahmenstatus: alle neun Punkte offen; Umsetzung in README/Toolkit/Save-
  Modulen ausstehend.

## Update 2025-12-02 – Px-/Acceptance-Folgelauf

- QA-Log 2025-12-02 dokumentiert den erneuten Testprompt-Lauf mit Px-Regression
  (Fail-Forward erhöht Px, soll senken) und 11 offenen Folgepunkten zu
  Acceptance-Spiegel, SaveGuard, Wallet-Init, Self-Reflection, Arena und PvP-
  Kennzeichnung.
- QA-Fahrplan auf Version 1.8.9 angehoben; neues Maßnahmenpaket 2025-12-02 mit
  Status „offen“ für alle Punkte angelegt.
- Nächste Schritte: Px-Balancing und Dokumentations-Sync priorisieren, danach
  Save-/HUD-Klärungen und PvP-Hinweis in README/Toolkit.
- Maßnahmenpaket 2025-12-02 vollständig umgesetzt (Px-Balancing, Acceptance-
  Spiegel, Save- und Arena-Deltas); QA-Fahrplan und QA-Log aktualisiert.

## Update 2025-12-03 – Acceptance-/Save-Voll-Lauf

- QA-Log 2025-12-03 fasst den vollständigen Testprompt (Solo, Solo+NPC, Koop,
  Rift, Arena, Mission 5 Badge-Check, Save/Load v6) zusammen und liefert drei
  neue Issues zu Accessibility-Enums, Offline-Hilfe-Feldnamen und der
  nummerierten Acceptance-Smoke-Liste.
- QA-Fahrplan 1.9.1 ergänzt den Deepcheck 2025-12-03 sowie das Maßnahmenpaket
  2025-12-03 (#1–#3) mit Status „abgeschlossen“.
- Umsetzung: README/DOC/QA-Briefing harmonisieren die Acceptance-Punkte 11–15
  samt SF-/SUG-Hinweisen; Save-Modul und Runtime mappen `badge_density`
  (`full|minimal` → `standard|compact`) und konsolidieren
  `offline_help_last_scene` als kanonisches Feld.

## Update 2025-12-19 – Playtest-Fixes (Issues #1/#9/#11)

- QA-Log 2025-12-19 dokumentiert die Repo-Anpassungen: Dispatcher-Fehlertext
  `gruppe 3` harmonisiert, Scene-Overlay im HQ (Charaktererstellung) entfernt,
  Handgelenk-Default als Legacy markiert.
- Runtime setzt `location='FIELD'` beim Missionsstart und rendert das
  Scene-Overlay nur noch in Missionen/Rifts; Acceptance-Fixture und Tests
  spiegeln den HQ-Nullwert.
- QA-Fahrplan 1.13.8 markiert Issues #1/#9/#11 als abgeschlossen.
- Offener Follow-up: Arena-SceneCounter/HUD-Overlay prüfen (Fahrplan Issue #12),
  um HQ-Start und Arena-Flow konsistent zu halten.

## Update 2025-12-19 – Economy-Scaling & Gold Save (Issues #7/#8)

- Economy-Scaling-Brücke dokumentiert: Rewards→Wallet-Richtwerte ab Level 400+
  sowie Chronopolis-Preisanker für High-Tier-Sinks sind im CU-Modul ergänzt.
- QA-Briefing benennt Level 120/512/900+ als Prüfanker für HQ-Pool, Wallet-Split
  und Chronopolis-Sinks.
- Gold-Save-Fixture (`savegame_v6_full.json`) trägt den erweiterten
  Atmosphere-Contract-Block und HUD-Usage-Flags als Referenz.
- QA-Fahrplan 1.13.12 markiert Issues #7/#8 als abgeschlossen.

## Update 2025-12-19 – HQ-Intro Schlusszeile (Issue #10)

- HQ-Kurzintro um die Schlusszeile ergänzt und Start-Dispatcher-Doku gespiegelt.
- QA-Log 2025-12-19 dokumentiert den Pflicht-Testlauf.
- QA-Fahrplan 1.13.15 markiert Issue #10 des Tester-Playtests 2025-12-18 als
  abgeschlossen.

## Update 2025-12-19 – Accessibility-Defaults (Issue #5)

- README und Modul 12 stellen klar, dass fehlende Accessibility-Felder durch
  Migration/Serializer auf Defaults normalisiert werden.
- QA-Log 2025-12-19 dokumentiert den Pflicht-Testlauf und den UI-Block-Check.
- QA-Fahrplan 1.13.17 markiert Issue #5 im Beta-KI-12-Plan als erledigt.

## Update 2026-04 – Tester-Playtest-Fortschritt

- Maßnahmenpaket Tester-Playtest 2026-04 fortgeschrieben: SaveGuard wertet
  Arena-Queue-States (`idle|…|completed`) beim Serialisieren aus, sperrt HQ-
  Saves während Matchmaking und harmonisiert die HQ-Blockertexte.
- UI-/Runtime-Normalisierung klemmt Teamgrößen hart auf 0–4, mapped
  `badge_density/output_pace` und schreibt Arena-Queue-/Zonen-Felder in den
  Save; Load-Merge protokolliert Konflikte inkl. Credits-Fallbacks in
  `logs.trace`.
- Chronopolis-Gate ist auf Level 10 angehoben; Debrief-Flow setzt Unlock-Toast
  und Trace (`chronopolis_unlock_level`) und trennt Pre-City-Checks von den
  Stadttests im QA-Plan.
- Offline-Flows besitzen ein 60-Sekunden-Rate-Limit; SaveGuard blockiert HQ-
  Saves ohne Uplink mit Trace-Eintrag und Toast, Acceptance-Smoke spiegelt die
  kanonischen Dispatcher-Strings.
- Fahrplan-Version 1.12.0 spiegelt alle 13 Punkte des Pakets als ✅ abgeschlossen
  (Tabelle + Checkliste im Abschnitt „Tester-Playtest 2026-04“); QA-Log und
  Fixtures sind damit synchron zum Audit.

## Update 2026-05-06 – Playtest-Fixes (Issues #2/#5)

- QA-Log 2026-05-06 dokumentiert die Ergänzung der Pflichtcontainer
  `logs.trace[]` und `logs.arena_psi[]` in Test-Saves und Briefings sowie den
  neuen Negativtest für fehlendes `logs.arena_psi`.
- Sonder-Overlays (Verfolgung/Massenkonflikt) loggen strukturierte
  `logs.hud[]`-Events (`vehicle_clash`, `mass_conflict`); der Runtime-Parser
  normalisiert die Records für Save/Load.
- QA-Fahrplan wurde auf Version 1.13.11 angehoben und markiert Issues #2/#5
  des Playtest-Pakets 2025-12-18 als erledigt.

## Update 2026-05-07 – Mission-5-Load-Snapshot (Issue #3)

- Acceptance-Follow-up prüft Mission‑5‑HUD, Gate/SF/Boss‑Toast und
  Auto‑Reset‑Flags (`self_reflection_auto_reset_*`) nach Save/Load.
- QA-Fahrplan wurde auf Version 1.13.13 angehoben und markiert Issue #3 des
  Playtest-Pakets 2025-12-18 als erledigt.

## Update 2026-05-08 – Atmosphere-Contract Capture (Issue #6)

- Optionales QA-Flag `logs.flags.atmosphere_contract_capture` ergänzt und im
  Runtime-Normalizer sowie im Gold-Save-Fixture verankert.
- Wissensmodule (README, Toolkit, Speicher-Modul, QA-Briefing) dokumentieren
  8–12-zeilige Exzerpte pro Phase inkl. PASS/FAIL-Status und HUD-Toast-Zählung.
- QA-Fahrplan 1.13.14 markiert Issue #6 des Tester-Playtest-Pakets 2025-12-18
  als abgeschlossen; QA-Log führt den Testlauf vom 2026-05-08.

## Update 2026-05-09 – Arena-SceneCounter/HUD-Overlay (Issue #12)

- `scene_overlay()` rendert nur noch bei `location='FIELD'`; HQ und Arena
  bleiben ohne Szenenzähler.
- Wissensmodule (README, Toolkit, Speicher-Modul) spiegeln den Arena-Ausschluss
  des Overlays.
- QA-Fahrplan 1.13.16 markiert Issue #12 des Tester-Playtest-Pakets 2025-12-18
  als abgeschlossen; QA-Log dokumentiert den Lauf vom 2026-05-09.

## Update 2026-05-10 – High-Level-Regression & Beta-KI-12 Abschluss

- README referenziert die High-Level-Fixture (`savegame_v6_highlevel.json`) als
  Regressionanker für Rift-/Endgame-Saves mit Seed-Tiers.
- QA-Fahrplan 1.13.18 markiert das Beta-KI-12-Maßnahmenpaket (Issues #1–#9)
  als abgeschlossen; QA-Log dokumentiert den Abgleich.

## Update 2026-07-02 – Chrononauten-Presets 2026-07

- Charaktererschaffung bündelt Presets auf dem 18-Punkte-Schema inklusive
  Rassenmods, Talenten und SYS-Last der Cyber-/Bioware; Quick-Build und
  Schnellstart-Presets sind editorfähig dokumentiert.

## Update 2026-11-03 – Wissensspeicher-Phase-3-Sync & Vereinheitlichung

- QA-Fahrplan markiert die Phase-3-Synchronisierung der 20-Slot-Optimierung als
  abgeschlossen; QA-Log 2026-11-03 dokumentiert Pflichtlauf und Referenzen.
- Vereinheitlichungs-Fahrplan 2025 schließt die Stichprobenprüfung in Runtime-
  Modulen ab (Core, Gameplay, Systems) und vermerkt keine Abweichungen.
- QA-Pflichtpaket ausgeführt (Lint, Tests, Smoke, Runtime- und Link-/Umlaut-
  Lints) und in QA-Log/Commit-Notizen gespiegelt.
- Preset-Validator `tools/validate_presets.py` prüft Attribute, Mods und
  SYS-Budgets und läuft über `make lint`.
- QA-Fahrplan 1.13.22 und QA-Log 2026-07-02 dokumentieren den Abschluss.

## Update 2026-08-15 – PvP-Arena Mixed-Reality Abschluss

- QA-Probelauf bestätigt MR-Trainingsanlage, Beacon-Gitter, Suit-Lock/Med-Scan,
  Rig-Hardware sowie diegetische HUD-Labels ohne VR-Vokabular.
- QA-Fahrplan 1.13.26 markiert das PvP-Arena-MR-Paket (Issues #1–#9) als
  abgeschlossen; QA-Log dokumentiert den Lauf vom 2026-08-15.

## Maßnahmenkatalog (Priorisiert)

1. **Modulnummern & Cross-References harmonisieren.** Modul 6 verweist weiterhin
   auf einen „ausgelassenen siebten Teil“, während Master-Index und Dateien
   Modul 7 führen. Status: _erledigt_ – Modul 6, Modul 7, Kampagnenübersicht und
   README benennen die Sequenz nun konsistent.
2. **Paradoxon-Farm in der PvP-Arena unterbinden.** Arena-Belohnungssystem an
   Episoden- oder Rufmarker koppeln. Status: _erledigt_ – Px-Bonus wird nur noch
   einmal pro Episode vergeben; `arena_episode_stamp` markiert den konsumierten
   Lauf.
3. **Heat-Terminologie trennen.** Psi-, Alarm-, Tech- und Stress-Anzeigen klar
   benennen; Save-Schema migrieren. Status: _erledigt_ – Psi-Heat wird nun
   explizit geführt (`psi_heat`), Save-Version 5 migriert Altstände automatisch,
   HUD/Toolkits zeigen Psi-Heat getrennt von Stress & Tech-Heat.
4. **Exploding-DMG-Spitzen begrenzen.** Arena/Boss-Dämpfer als Pflicht setzen
   und Boss-DR automatisieren. Status: _erledigt_ – Arena-HUD halbiert
   Exploding-Overflow automatisch, Boss-Spawn vergibt DR 2/3 inkl. HUD-Hinweis.
5. **High-Level-Progression auf Prestige-Perks umstellen.** Attribute nicht
   weiter erhöhen, stattdessen qualitative Boni verankern. Status: _erledigt_ –
   Core-Regelwerk setzt ab Prestige-Level auf erzählerische Perks und ersetzt
   den Standard-Attributsbonus durch Legendenpfade.
6. **Psi vs. Non-Psi balancieren.** Phase-Strike-Kosten in PvP anheben,
   Anti-Psi-Grundschutz verbreitern. Status: _erledigt_ – Arena setzt
   `phase_strike_tax = +1 SYS`, Kernanzüge tragen `psi_buffer` (+2 SG,
   neutralisiert Bonus-Schaden).
7. **Tech-Dominanz-Check auf kleine Teams ausweiten.** `tech_heat` früher
   triggern und Gerätezwang durchsetzen. Status: _erledigt_ – Solo- und
   Duo-Teams feuern `tech_solution()` nun bei niedrigeren Limits und die
   Toolkit-Makros sperren Tech-Ketten, bis `confirm_device_slot()` ein Field Kit
   bestätigt.
8. **Suspend-Snapshot als Komfortfunktion implementieren.** HQ-Save-Pflicht
   erhalten, aber Session-Pause erlauben. Status: _erledigt_ – `!suspend` legt
   einen 24h-Snapshot an, `!resume` setzt ihn einmalig fort und respektiert den
   HQ-Deepsave.
9. **Exfil-Kommunikation im HUD verstärken.** Auto-Toasts für Arming/Alt-Anchor
   und RW-Ticks. Status: _erledigt_ – `!exfil arm/alt/tick/status` triggern
   automatische HUD-Toasts, aktualisieren Anchor/ALT und spiegeln den Timer im
   Overlay.
10. **Arena-Matchmaking mit Tier-Loadouts absichern.** Artefakt-Spitzen kappen,
    Proc-Budget limitieren. Status: _erledigt_ – Runtime-Stub erzwingt
    Tier-Gates, kappt Artefakt-Überhänge und bremst Proc-Ketten mit pro Tier
    gesetztem Budget.
11. **Boss-Foreshadow-Gate erzwingen.** Szene 10 blockieren, bis Hinweise
    geliefert sind. Status: _erledigt_ – `NextScene()` hält Szene 9, bis vier
    (Core) bzw. zwei (Rift) Foreshadows über Makros registriert sind und meldet
    den Gate im HUD. Nachweis: Commit `b245bef` (_Boss-Foreshadow-Gate aktiviert_)
    und QA-Log 2025-03-19 (Acceptance-Smoke-Abgleich).
12. **Mission-Generator linten.** Gewichte und Duplicate-Seeds automatisch
    prüfen. Status: _erledigt_ – `scripts/lint_mission_generator.py` prüft die
    Pools und stellt d24-Abdeckung sicher. Nachweis: Commit `5a3fbb3`
    (_Add mission generator lint_); automatisierte Prüfung läuft über
    `scripts/tests/test_lint_mission_generator.py`.
13. **Endgame-Ökonomie justieren.** Chronopolis-Angebote mit Rang/Research-Gates
    und Daily Stock versehen. Status: _erledigt_ – Runtime koppelt das
    Tagesangebot an Dienstgrad und Research-Level, der Pool rotiert filmisch pro
    HQ-Zyklus. Nachweis: Commit `7d91e53` (_Implement Chronopolis stock gating_);
    QA-Log 2025-11-06 (Regressionsevidenz Maßnahmen #13–#20).
14. **Signal-Space-Konsequenz in Texten verankern.** Remote-Hack-Formulierungen
    bereinigen, `comms_check()` erzwingen. Status: _erledigt_ – Arena-Makro
    zwingt `must_comms`, Ausrüstungshinweis verankert Hardwarepflicht.
    Nachweis: Commit `8fe8de2` (_Sichere Remote-Hacks über comms_check_);
    QA-Log 2025-11-06 (Regressionsevidenz Maßnahmen #13–#20).
15. **Urban Quick-Card zentral anbieten.** Deckungs- und Verfolgungsreferenzen in
    `/help` bündeln. Status: _erledigt_ – `/help urban` liefert Deckungsgrade,
    Distanzstufen und HUD-Tags; README verankert die Schnellhilfe. Nachweis:
    Commit `52d1ba5` (_Add HUD quick-help cards for urban ops and SG benchmarks_);
    QA-Log 2025-11-06 (Regressionsevidenz Maßnahmen #13–#20).
16. **HQ-Moments mechanisch verankern.** Tabelle mit Buff-Icons einführen.
    Status: _erledigt_ – Toolkit listet HQ-Buffs als HUD-Icons inkl.
    Makro-Snippet, Dopplungen werden per Kampagnenflag geblockt. Nachweis:
    Commit `9a1675d` (_Intro-Guard und HQ-Moments nachziehen_); QA-Log 2025-11-06
    (Regressionsevidenz Maßnahmen #13–#20).
17. **Arena zwingt JSON-Würfellog.** `debug_rolls` standardmäßig aktivieren.
    Status: _erledigt_ – Toolkit-Default wurde auf `true` gesetzt und README
    dokumentiert das neue Standardverhalten. Nachweis: Commit `8208170`
    (_feat: add transfer frames and debug roll output_) sowie QA-Log 2025-03-19
    (Acceptance-Smoke-Abgleich – JSON-Log aktiv).
18. **Rift-Boss-Drops automatisieren.** Toolkit-Trigger `on_rift_boss_down()`
    für Loot-Erinnerung. Status: _erledigt_ – neues Makro setzt den Boss-Flag,
    stößt das para-Loot an und markiert den Legendary-Wurf im Log. Nachweis:
    Commit `22d3c33` (_Automatisiere Rift-Boss-Loot und Arena-Takt_); QA-Log
    2025-11-06 (Regressionsevidenz Maßnahmen #13–#20).
19. **Attribut-Cap kommunizieren.** Charaktererschaffung um Prestige-Hinweis
    ergänzen. Status: _erledigt_ – Charaktererschaffung betont das Cap bei 10
    und verweist auf Prestige-Aufstiege für höhere Werte. Nachweis:
    Commit `1be6f57` (_Sichert Attributbudget bei der Charaktererschaffung_);
    QA-Log 2025-11-06 (Regressionsevidenz Maßnahmen #13–#20).
20. **Arena-Großteams mit Timern steuern.** 30-Sekunden-Takt und Move-Limit im
    HUD. Status: _erledigt_ – Arena initialisiert nun Großteam-Zyklen, trackt
    Moves und blendet Timer sowie Limit im HUD ein. Nachweis: Commit `22d3c33`
    (_Automatisiere Rift-Boss-Loot und Arena-Takt_); QA-Log 2025-11-06
    (Regressionsevidenz Maßnahmen #13–#20).
21. **Boss-Pressure-Variationen schützen.** Memory-Pool/Cooldown für
    Druck-Set-Auswahl. Status: _erledigt_ – Toolkit setzt eine
    Zweifach-Cooldown-Liste ein, bevor Druck-Sets wieder freigegeben
    werden.
22. **Self-Reflection-Flag sichtbar machen.** HUD-Badge `SF-OFF` ergänzen.
    Status: _erledigt_ – Runtime blendet das Badge ein, wenn `self_reflection:
false` aktiv ist; `!sf on/off` steuern das Flag und loggen den Status.
23. **Intro-Guard beim Laden aktivieren.** Einleitung nur bei Erststart zeigen.
    Status: _erledigt_ – Runtime speichert `intro_seen` im UI-State und spielt
    das HQ-Kurzintro nur beim Erststart aus.
24. **DelayConflict für Heist/Street justieren.** Mission-Tags reduzieren
    Verzögerung. Status: _erledigt_ – `StartMission()` normalisiert Mission-Tags
    und `DelayConflict` senkt bei `heist`/`street` automatisch die Schwelle.
25. **Briefing mit ☆-Feedback ausliefern.** Overlay standardisieren. Status:
    _erledigt_ – Toolkit zeigt das ☆-HUD beim Missionsstart automatisch,
    `briefing_with_stars()` zieht den SG-Zuschlag konsistent nach.
26. **TK-Nahkampf-Cooldown visualisieren.** HUD-Icon nach Einsatz. Status:
    _erledigt_ – Runtime blendet `TK🌀` nach `!tk melee` ein und `!tk ready`
    entfernt die Sperre nach der Cooldown-Runde.

## Beta-KI 2025-07 – Save/HUD/Arena-Deltas (Update: 2025-10-20)

- **Status:** Alle Issues #1–#15 sind laut QA-Fahrplan 1.8.2 (fortgeschrieben
  aus 1.8.0) und
  Beta-QA-Log 2025-07-20 abgeschlossen; README, Toolkit und HUD-Modul spiegeln
  Gate-/Badge-/City-Flows.
- **Fahrplan:** Abschnitt „Maßnahmenpaket Beta-KI 2025-07“ führt sämtliche
  Punkte als ✅ und verweist auf die Runtime- und Wissensmodule.
- **QA-Log:** Eintrag 2025-07-20 bestätigt die Umsetzung und die
  Pflichttest-Läufe.
- **Evidenz:** JSON-Hand-off 2025-11-05 belegt HUD-/Save-/Arena-Traces im
  [`internal/qa/evidence/2025-beta-gpt-evidenz.md`](../evidence/2025-beta-gpt-evidenz.md)
  (§2025-07-05).

## Beta-KI 2025-07-18 – Save/HUD/Compliance-Regression (Update: 2025-10-20)

- **Status:** Maßnahmen #1–#12 sind laut QA-Fahrplan 1.8.2 umgesetzt; HUD-Badges
  (`SF-OFF`, `GATE 2/2`), Psi-Logs und Dispatcher-Hinweise wurden in Runtime,
  README, Toolkit und HUD-Modul gespiegelt.
- **Fahrplan:** Tabelle „Maßnahmenpaket Beta-KI 2025-07-18“ markiert alle
  Punkte als ✅ und verlinkt auf die betroffenen Module.
- **QA-Log:** Eintrag 2025-07-20 dokumentiert die Pflichttestläufe sowie die
  Doku-Synchronisation.
- **Evidenz:** Exfil-/Wallet-Traces sowie Psi-/HUD-Logs liegen über den JSON-
  Hand-off 2025-11-05 in
  [`internal/qa/evidence/2025-beta-gpt-evidenz.md`](../evidence/2025-beta-gpt-evidenz.md)
  (§2025-07-18) vor.

## Beta-KI 2025-10-15 – Acceptance-/HUD-/Accessibility-Deltas (Update: 2025-10-20)

- **Status:** Alle 15 Maßnahmen sind in QA-Fahrplan 1.8.2 als ✅ vermerkt; die
  Acceptance-Smoke umfasst wieder 15 Prüfschritte, das Save-Schema erzwingt
  `logs.foreshadow[]` und Arena-Phase-Marker, HUD & Dispatcher spiegeln den
  Auto-Reset von `SF-OFF`, Cinematic-Header und Accessibility-Dialog.
- **Fahrplan:** Tabelle „Maßnahmenpaket Beta-KI 2025-10-15“ listet die
  aktualisierten Referenzen auf Runtime, README, Toolkit, HUD-Modul und
  Tester-Briefing.
- **QA-Log:** Eintrag 2025-10-20 bestätigt den grünen Pflichttest-Stack und
  verweist seit 2025-11-05 auf die abgeschlossene QA-Evidenz.
- **Evidenz:** Acceptance-Checkliste, HUD-Dumps und Dispatcher-Transkripte sind
  über den JSON-Hand-off 2025-11-05 im
  [`internal/qa/evidence/2025-beta-gpt-evidenz.md`](../evidence/2025-beta-gpt-evidenz.md)
  (§2025-10-15) dokumentiert.

## Beta-KI 2025-10-28 – SaveGuard/HUD/Ökonomie-Deltas (Update: 2025-10-28)

- **Status:** Alle 13 Maßnahmen sind laut QA-Fahrplan 1.8.2 als ✅ markiert;
  `runtime.js` validiert HQ-DeepSaves inklusive Arena-Active-Blocker,
  Paradoxon-Reset und Boss-DR-Toast, während README, Modul 12
  (`systems/gameflow/speicher-fortsetzung.md`) und HUD-/Core-Sektionen die
  getrennten Foreshadow-/Gate-Badges, Ökonomie-Formeln sowie das zusätzliche
  Accessibility-Preset spiegeln.
- **Fahrplan:** Tabelle „Maßnahmenpaket Beta-KI 2025-10-28“ verweist auf die
  aktualisierten Runtime- und Wissensmodule (RT, M12, HUD, Core) und verlinkt die
  QA-Testreferenz (`!save` Minimal-HQ-Save).
- **QA-Log:** Eintrag 2025-10-28 verweist seit 2025-11-05 auf den erledigten
  JSON-Hand-off (HUD-/Save-/Arena-Evidenz) und markiert die Checkbox als ✅.
- **Evidenz:** HUD-/Save-Dumps, Wallet-Splits und Arena-Guards liegen im
  Evidenz-Log (`internal/qa/evidence/2025-beta-gpt-evidenz.md` §2025-10-28)
  über den JSON-Hand-off 2025-11-05 vor.

## QA-Follow-up #14 – Chronopolis-Basar Balance (Stand: 2025-06-28)

- **Stichprobe Runtime:** `CHRONO_CATALOG` listet aktuell einen Tagespool aus
  drei Kategorien (`Temporal Ships`, `Never-Was Gadgets`, `Era-Skins`). Die
  Limits (`CHRONO_CATEGORY_LIMITS`) sorgen für 1 Schiff, 3 Gadgets und 4 Skins
  pro Reset. `rollChronopolisStock()` koppelt die Auswahl an Tagesdatum und
  Reset-Serial, wodurch Daily-Rerolls deterministisch reproduzierbar bleiben.
- **Gating & Preise:** `chronopolisStockReport()` versieht alle Einträge mit
  Rang- (`minRank`) und Research-Schranken (`minResearch`). Die untersuchten
  Items decken Preisbereiche von 200 CU (Era-Skins) bis 5 400 CU (Temporal
  Ships) ab. Für unzureichend qualifizierte Crews erzeugt der Report Lock-Hinweise
  (`🔒 … (Rank … · Research …)`), sodass QA den Balance-Status direkt am HUD-Text
  erkennt.
- **Log-Persistenz:** `log_market_purchase()` normalisiert Einträge auf
  `logs.market[]`, trimmt Kosten in ganze CU und ergänzt automatisch Px-Klauseln
  (`Px ±n`), sobald `px_delta` gesetzt wird. Das Limit (`MARKET_LOG_LIMIT = 24`)
  hält den Debrief schlank; ältere Einkäufe werden FIFO gekappt.
- **QA-Bedarf:** Maintainer liefern für Premium-Angebote (Temporal Ships
  ≥ 5 000 CU) noch Px- und Quellenhinweise, damit der Debrief Konsolenrabatte
  (`note`, `source`) unterscheidet. QA vermerkt jeden Testlauf im Beta-Log mit
  Chronopolis-Report, Px-Delta und Rang/Research-Kontext.

**Update 2025-06-28 – Hochstufen-Stichprobe abgeschlossen:** Das Node-Skript
`tools/test_chronopolis_high_tier.js` setzt eine Chief-Agentin mit Research 4,
rollt `chronopolisStockReport()` (Daily-Roll) und bestätigt, dass sämtliche Slots
ohne 🔒-Locks erscheinen. Anschließend protokolliert es einen Kauf (`log_market_purchase()`
mit `px_delta`) und prüft den Debrief-Trace (`Chronopolis-Trace`) auf Px-Klausel,
Notiz und Quellenhinweis. QA-Log 2025-06-28 führt den Lauf samt Output auf und
schließt die Beobachtung. 27. **Arena-Gebühr progressiv staffeln.** Vermögensabhängige Kosten definieren.
Status: _erledigt_ – Staffelung mit 1 %/2 %/3 %-Brackets koppelt Gebühren an
das HQ-Vermögen. 28. **Chronopolis-Reset-Rhythmus fixieren.** City-Tick nach Episoden und optional
nach drei Missionen. Status: _erledigt_ – Episodenabschluss triggert
sofortigen Reset; ein konfigurierbarer Drei-Missions-Takt hält die Stadt
lebendig. 29. **Gefährdungs-Skala vereinheitlichen.** Einheitliche Risk-Level-Icons.
Status: _erledigt_ – Toolkit formatiert `R1–R4` automatisch als HUD-Badges,
Artefakt-Pool & HUD-Dokumentation spiegeln die neue Skala. 30. **Würfel-Benchmarks bündeln.** One-Pager für SG/Exploding-Optionen unter
`/help sg`. Status: _erledigt_ – `/help sg` fasst Würfelgrößen, Zielwerte und
Exploding-Ansagen filmisch auf einer Zeile zusammen.

## Nachverfolgung & Nächste Schritte

1. **Validierung:** Maßnahmen 1–10 anhand der Commits prüfen und Ergebnisse im
   QA-Fahrplan sowie im entsprechenden Abschnitt des QA-Logs dokumentieren.
2. **Dokumentation:** Punkte 11–20 in README, Maintainer-Ops und Glossar
   spiegeln, sobald Runtime-Anpassungen bestätigt sind; Referenzen im QA-Log
   hinterlegen. Jeder QA-Log-Eintrag notiert den verwendeten Beta-KI-Testprompt,
   damit Regressionen reproduzierbar bleiben. **Repo-Agenten liefern den
   Wissensspiegel (Runtime-Module, Toolkit) innerhalb desselben Commits** und
   dokumentieren ihn. Maintainer bestätigen anschließend den Transfer in
   produktive Plattform-Runtimes (siehe Maintainer-Ops) inklusive Datum und
   Commit-ID. Maintainer-Ops wurde am 2025-03-21 auf Version 1.2.0 angehoben und
   beschreibt nun die Spiegelprozesse nach KI-Spielleitung-Freigabe.
3. **Roadmap:** Themen 21–30 mit der UX-/Tooling-Roadmap verknüpfen, in den
   QA-Fahrplan übernehmen und Priorität über den jeweiligen QA-Log-Eintrag
   abstimmen.
4. **Tooling-Abgleich:** `.markdownlint.yaml` (Zeilenlänge 100, Frontmatter-Ausnahmen)
   und `.prettierrc.json` (Doc-only Overrides) sind produktiv eingebunden.
   `make lint` ruft der Reihe nach `npm run lint:rt`, `GM_STYLE=verbose npm run
lint:rt`, `python3 scripts/lint_doc_links.py`, `python3 scripts/lint_umlauts.py`,
   `npm run lint:links` und `npm run lint:md` auf. Das Markdownlint-Skript
   basiert auf der Python-Implementierung der `.markdownlint.yaml` und prüft QA-
   Plan, QA-Audit und QA-Index; der Pre-Commit-Hook `markdownlint` verweist auf
   dieselbe Konfiguration. Optionales
   `npm run format:docs:check` steht für
   Dokumentations-Reviews bereit (Prettier lokal installieren, falls benötigt).

## Befunde Beta-KI-Lauf 2025-06 (ISSUE #1–#16)

Der Testprompt vom Juni 2025 ergänzt 16 neue Baustellen rund um HQ-Saves,
Gruppenschemata und PvP-Logik. Die folgenden Einträge bilden den aktuellen
Analyse- und Maßnahmenstand ab. Alle Punkte wurden in den QA-Fahrplan
übernommen und stehen dort mit Verantwortlichkeiten sowie Terminankern.

**Status-Legende:** `[ ] Offen`, `[x] Erledigt`

### Issue #1 – HQ-Save-Pflichtfelder

- **Status:** [x] Erledigt
- **Kerndiagnose:** Minimal-HQ-Saves ließen `economy`, `logs`, `ui` und
  `campaign.px` leer.
- **Empfohlene Umsetzung:** Serializer ergänzt die Pflichtpfade (`economy`,
  `logs`, `ui`), synchronisiert Kampagnen-Px und die Linterregel
  `SAVE_REQ_FIELDS` prüft die Defaultstruktur.
- **Statusnotiz:** ✅ Behoben – Saves liefern wieder vollständige
  Pflichtfelder. Referenz: Commit `3e4f306`.

### Issue #2 – Gruppensave-Konsistenz

- **Status:** [x] Erledigt
- **Kerndiagnose:** Drei konkurrierende Arrays für Teamzusammenstellungen
  verhindern einen stabilen Merge.
- **Empfohlene Umsetzung:** Normalizer in `load_deep()` verankern,
  Kanonstruktur `party.characters[]` setzen und Legacy-Aliase dokumentieren.
- **Risiko bei Verzug:** Merge-Dialoge bleiben unzuverlässig.
- **Statusnotiz:** ✅ `load_deep()` konsolidiert Gruppenroster auf
  `party.characters[]`; Dokumentation spiegelt die Alias-Bereinigung.

### Issue #3 – Arc-Dashboard

- **Status:** [x] Erledigt
- **Kerndiagnose:** Das Arc-Dashboard muss als Pflichtcontainer im Save-Schema
  und in der Doku auftauchen, damit Cross-Mode-Imports stabil bleiben.
- **Umsetzung:** `arc_dashboard` ist als Pflichtobjekt im Schema sowie in
  Speicher-, README- und QA-Briefing-Texten dokumentiert; Serializer und
  `load_deep()` normalisieren Seeds, Fraktionen und Fragen.
- **Risiko bei Verzug:** Der Story-Hub verliert nach einem Reload Kontext.

### Issue #4 – Load-Compliance

- **Status:** [x] Erledigt
- **Kerndiagnose:** Einstiegstrigger feuern mehrfach, da ein Statusflag fehlt.
- **Umsetzung:** Runtime-Ansatz in `runtime.js` greift nicht, weil die Datei im
  aktiven Regelwerk fehlt. Flag-Handling muss in zugänglichen Makros/Toolkits
  neu verankert werden.
- **Statusnotiz:** ✅ Toolkit setzt `SkipEntryChoice()` direkt nach dem Laden und
  gibt den Auswahlmodus über `AllowEntryChoice()` nach Missionsstart frei.
  QA-Fahrplan & Logs halten die Evidenz aus dem Acceptance-Smoke 2025-06-13
  fest (SaveGuard während Arena und Reset nach Exit).
- **Risiko bei Verzug:** Spieler erhalten direkt nach `!load`
  wiederholte Dialoge.

### Issue #5 – Hot-Exfil Px-Verlust

- **Status:** [x] Erledigt
- **Kerndiagnose:** FAQ und Runtime widersprachen sich bei der Px-Strafe.
- **Umsetzung:** Toolkit-Default `px_loss_on_hot_fail` wurde auf `false`
  gestellt; README und Kampagnenleitfaden markieren die Px-Strafe als
  optionalen Opt-in-Schalter.
- **Statusnotiz:** ✅ Opt-in-Dokumentation gleicht Erwartungen und Runtime ab.
- **Testnachweis:** `PYTHONPATH=. python3 scripts/lint_umlauts.py` (OK,
  2025-06-11).

### Issue #6 – Phase-Strike-Kosten

- **Status:** [x] Erledigt
- **Kerndiagnose:** PvP-Kosten sind doppelt definiert, das Modus-Flag bleibt
  unklar.
- **Empfohlene Umsetzung:** `campaign.mode` als Quelle nutzen, Helper
  `is_pvp()` einführen und die Kosten zentralisieren.
- **Statusnotiz:** ✅ `campaign.mode` steuert jetzt `is_pvp()` sowie
  `phase_strike_tax()/phase_strike_cost()`. Arena-Start/Exit setzen den Modus,
  `state.arena.phase_strike_tax` spiegelt den Zuschlag und der HUD-Toast
  `Arena: Phase-Strike belastet +1 SYS (Kosten 3)` samt `logs.psi[]`-Trace
  belegt den Aufschlag. (Commit: wird im PR referenziert.)
- **Risiko bei Verzug:** Die Psi-Balance kippt in Sparring-Szenen.

### Issue #7 – Accessibility-Dialog

- **Status:** [x] Entfällt
- **Kerndiagnose:** Es fehlt ein einheitliches Menü für Barrierefreiheit.
- **Entscheid:** Maintainer verwerfen das HUD-Menü (2025-06-13); Schrift-
  größen-Anpassungen bleiben Aufgabe der Endgeräte/Apps.
- **Dokumentation:** Fahrplan 2025 markiert Issue #7 als verworfen, keine
  Umsetzung in `runtime.js` vorgesehen.

### Issue #8 – Offline-Fallback

- **Status:** [x] Erledigt
- **Kerndiagnose:** Kein definierter Offline-Dialog trotz HUD-Alerts.
- **Empfohlene Umsetzung:** `offline_help()` ergänzen, ein lokales FAQ
  bereitstellen und den Ask→Suggest-Flow offline spiegeln.
- **Statusnotiz:** ✅ Toolkit-`offline_help()` liefert FAQ-Text für den im
  Einsatz gekappten ITI↔Kodex-Uplink, `!offline` ruft das Feldprotokoll ab
  (Mission läuft mit HUD-Lokaldaten weiter) und `must_comms()` triggert den
  Fallback samt Hinweis, wenn Reichweite oder Jammer die Verbindung kappen.
  (Commit: wird im PR referenziert.)
- **Risiko bei Verzug:** Die Kodex-Hilfe bricht bei Verbindungsproblemen ab.

### Issue #9 – Semver-Benennung

- **Status:** [x] Erledigt
- **Kerndiagnose:** `ZR_VERSION` und `zr_version` werden uneinheitlich
  verwendet.
- **Empfohlene Umsetzung:** Dokumentation harmonisieren, Fehlermeldungen beide
  Werte nennen lassen und das Log um die Runtime-Version ergänzen.
- **Risiko bei Verzug:** Fehlermeldungen bleiben missverständlich.
- **Statusnotiz:** ✅ Semver-Prüfung setzt auf `zr_version`↔`ZR_VERSION`,
  Runtime-Version wird als `logs.flags.runtime_version` persistiert; Doku
  und Fehlermeldungen ziehen nach. (Commit: wird im PR referenziert.)

### Issue #10 – Foreshadow-Gates

- **Status:** [x] Erledigt
- **Kerndiagnose:** Foreshadow-Fortschritt ist nicht im Save verankert.
- **Empfohlene Umsetzung:** `logs.foreshadow` persistieren und ein
  HUD-Badge anbinden.
- **Risiko bei Verzug:** Das Gate lässt sich durch Reloads unterlaufen.
- **Statusnotiz:** ✅ Persistente `logs.foreshadow` + HUD-Badge umgesetzt;
  `ForeshadowHint()` schreibt Marker, `!boss status` zeigt `Foreshadow n/m`.
  (Commit: wird im PR referenziert.)

### Issue #11 – Koop-CU-Verteilung

- **Status:** [x] Erledigt
- **Kerndiagnose:** Team- und Charakter-Wallets werden nicht sauber getrennt.
- **Empfohlene Umsetzung:** Debrief-Dialog um Splits ergänzen, Standard
  `economy.cu` führen und persönliche Wallets separat buchen.
- **Statusnotiz:** ✅ Wallet-Split-Dialog zeigt Koop-Summen (`Wallet-Split (n×)`
  & `HQ-Pool`) und schreibt individuelle Guthaben nach `economy.wallets{}`.
  QA-Log 2025-06-17 dokumentiert Smoke-/Lint-Läufe samt Debrief-Trace.
- **Risiko bei Verzug:** Belohnungsverteilung bleibt strittig und Saves driften.

### Issue #12 – Chronopolis-Warnung

- **Status:** [x] Erledigt
- **Kerndiagnose:** Das einmalige Popup besitzt kein Persistenzflag.
- **Empfohlene Umsetzung:** `logs.flags.chronopolis_warn_seen` setzen.
- **Risiko bei Verzug:** Die Warnung erscheint bei jedem Eintritt erneut.
- **Statusnotiz:** Toolkit setzt das Flag nun beim Chronopolis-Einstieg und
  bindet das Popup nur einmal ein. (Commit: wird im PR referenziert.)

### Issue #13 – Ask→Suggest

- **Status:** [x] Erledigt
- **Kerndiagnose:** Die geforderte Mechanik ist nicht dokumentiert oder
  standardisiert.
- **Empfohlene Umsetzung:** Toolkit-Makro `suggest_actions()` bereitstellen und
  README ergänzen.
- **Risiko bei Verzug:** Beratungssituationen bleiben UX-seitig lückenhaft.
- **Statusnotiz:** Suggest-Modus schaltet via `modus suggest`/`modus ask`,
  das Toolkit-Makro `suggest_actions()` kennzeichnet Vorschläge und README
  beschreibt den Ablauf. (Commit: wird im PR referenziert.)

### Issue #14 – Suspend-Snapshot

- **Status:** [x] Erledigt
- **Kerndiagnose:** Initiative- und Timer-Zustände fehlten beim Resume.
- **Empfohlene Umsetzung:** Snapshot um `initiative.order[]`,
  `initiative.active_id` und `hud.timers[]` erweitern.
- **Risiko bei Verzug:** Konflikte verlieren nach `!resume` ihre Struktur.
- **Statusnotiz:** Suspend-Snapshot übernimmt Initiative-Reihenfolge und HUD-
  Timer; `tools/test_suspend.js` deckt das Resume ab. (Commit: wird im PR
  referenziert.)

### Issue #15 – PSI-Buffer-Arena

- **Status:** [x] Erledigt
- **Kerndiagnose:** PvP-Dämpfer sind nicht zentral dokumentiert.
- **Empfohlene Umsetzung:** `apply_arena_rules()` bündelt `psi_buffer` und
  Dämpfer, Dokumentation vereinheitlichen.
- **Risiko bei Verzug:** Mods und Toolkits setzen Arena-Regeln falsch um.
- **Statusnotiz:** Runtime & Stub setzen den Helper um, Docs heben den zentralen
  PvP-Abgleich hervor. (Commit: wird im PR referenziert.)

### Issue #16 – Chronopolis-Marktlog

- **Status:** [x] Erledigt
- **Kerndiagnose:** Käufe erzeugen kein Save-Log trotz Px-Auswirkungen.
- **Empfohlene Umsetzung:** `logs.market[]` um Timestamp, Item, Kosten und eine
  Px-Klausel erweitern.
- **Risiko bei Verzug:** Px-Verluste bleiben nicht nachvollziehbar.
- **Statusnotiz:** Runtime & Serializer schreiben `logs.market[]` (Timestamp,
  Item, Kosten, Px-Klausel); README & Speicher-Doku verweisen auf
  `log_market_purchase()` für den Debrief-Trace. (Commit: wird im PR
  referenziert.)

**Folgeaufgaben:**

- [x] QA ergänzt Regressionstests (Dispatcher-Suite, Cross-Mode-Läufe,
      Debrief-Splits) und trägt die Nachweise im Evidenzprotokoll unter
      `internal/qa/evidence/2025-beta-gpt-evidenz.md` nach; QA-Log und Fahrplan
      verweisen seit dem JSON-Hand-off 2025-11-05 auf die Ablage.
- [x] Codex erstellt Branches für Schema-/Runtime-Änderungen (#1–#16) und
      verknüpft Commits mit dem Audit; Umsetzung läuft auf dem Arbeitszweig
      `work` und die Commit-Historie referenziert die Audit-IDs.
- [x] Maintainer synchronisieren README, Modul 12 und Master-Index nach
      Abschluss der jeweiligen Teilaufgaben; die aktuellen Mirrors stehen seit
      Version 1.16.0 auf demselben Stand wie die Runtime-Hooks.

## Update 2026-01-14 – Repo-Agent (Fahrplan Issues #1–#7, #9)

- **Status:** [x] Erledigt
- **Umsetzungskern:**
  - Rift-Casefile-Map auf 14-Szenen-Standard (1–4 Tatort, 5–9 Leads, 10 Boss,
    11–14 Auflösung) konsolidiert und Stage-Overlay gespiegelt.
  - Pre-City-Hub als HQ-savebar fixiert; Kampagnenübersicht angepasst.
  - Tester-Briefing auf Kompakt-Profil + Kodex-Terminologie aktualisiert,
    Szenario-Varianz eingefordert, UI-Host-Override als Erwartung ergänzt.
  - Rift-Seed-Merge deterministisch: Auswahlregel (Tier/Discovered/Marker) +
    `selection_rule` in Merge-Trace und Flags dokumentiert.
  - SaveGuard-Prioritäten als Tabelle in Modul 12 verankert.
  - HUD-Prioritäten erweitert (Critical-Tags) und UI-Override-Trace
    `ui_host_override` ergänzt.
  - Dummy-Fixture `qa_save_v6_dummy.json` ergänzt (QA-Profile + fehlendes `at`).
- **Referenzen:** QA-Log 2026-01-14, README, Modul 12, Toolkit, Runtime.
- **Tests:** Pflichtpaket ausgeführt (siehe QA-Log/Commit).

## Offene Fragen für das Team (Stand: 2025-04-02)

Die folgenden Punkte galten im ursprünglichen Audit als ungeklärt und sind für
den Live-Gang bewertet:

- **Master-Index `modul_7`.** Die Nummerierung bleibt kanonisch: Modul 7 ist
  dauerhaft `gameplay/fahrzeuge-konflikte.md`. Cross-References in
  README, Kampagnenstruktur und Master-Index verweisen einheitlich auf diese
  Datei; weitere Umbenennungen sind nicht vorgesehen.
- **Px-Ökonomie.** Die Limitierung der Arena-Belohnung auf einmal pro Episode
  bildet den finalen Rahmen für Version 4.2.2. Weitere Ruf- oder
  Trainingsmarker werden frühestens im nächsten Major-Update geprüft und sind
  kein Blocker für den Release.
- **Save-Schema-Mapping (`psi_heat`).** Die Migration ist produktiv über
  `runtime.migrate_save()` implementiert. `save_version` 6 erzwingt die neuen
  Felder (`psi_heat`, `psi_heat_max`) und die Acceptance-Smoke prüft den Pfad.
  Die Toolchain basiert auf den vorhandenen Runtime-Tests (`tools/test_save.js`,
  `npm run test:save`) und benötigt keine zusätzliche Utility-Datei.

Bitte priorisierte Maßnahmen an Codex melden und dabei den relevanten
QA-Log-Eintrag referenzieren, damit Audit und Fahrplan in nachfolgenden
Iterationen synchron bleiben.
