---
title: "Tester-Playtest-Briefing"
version: 1.3.8
tags: [meta]
---

# Tester-Playtest-Briefing

Dieser Leitfaden bündelt den standardisierten Playtest-Auftrag für ZEITRISS
und erweitert ihn um eine strukturierte Testmatrix für Solo-, Koop- und
PvP-Szenarien. Die Standardpipeline besteht darin, ein Custom-GPT mit dem
Wissenspaket aufzusetzen, den untenstehenden Auftrag zu kopieren und das GPT
den kompletten Ablauf autonom (inklusive Squad-, Koop- und PvP-Simulationen)
durchspielen zu lassen. Das
resultierende Protokoll liefert automatisch strukturierte `ISSUE`, `Lösungsvorschlag`, `To-do`- und
`Nächste Schritte`-Blöcke für Codex und wird unverändert in das Codex-Fenster
(Programmier-KI) übertragen. Tester:innen posten den Auftrag genau einmal; das GPT simuliert alle
benötigten Läufe eigenständig und fasst sie im beschriebenen Format zusammen.

## Wissensspeicher vorbereiten

> **Smoketest-Rahmen:** Die Acceptance-Smoke-Checkliste ist ein QA-/Abnahme-
> Workflow für Beta-GPT oder CI, nicht Teil des Live-Spielbetriebs. Im regulären
> Spiel löst kein Spielerkommando („Spiel starten“, „Speichern“ etc.) den
> Smoketest aus. Der Copy-&-Paste-Auftrag unten enthält die Smoke-Schritte,
> damit Beta-GPT-Sessions sie autonom abdecken; für das produktive GPT bleiben
> sie im Wissensspeicher nur als Referenz.

Vor dem Testlauf werden identische Datenquellen in jeder Plattform geladen:

- `meta/masterprompt_v6.md`
- `README.md`
- `master-index.json`
- Alle 18 Runtime-Module aus `core/`, `gameplay/`, `characters/` und `systems/` (ohne
  `internal/runtime/runtime-stub-routing-layer.md`).
- Diese QA-Briefing-Datei (`docs/qa/tester-playtest-briefing.md`) bleibt nur für QA-
  Sessions (z. B. Beta-GPT). Sie wird nicht in produktive Wissensspeicher
  geladen.

Eine Zielgruppen- und Dokumentenübersicht findest du in der README unter
[„Dokumenten-Landkarte“](../../README.md#dokumenten-landkarte); sie zeigt, wie
Tester:innen ihre Findings an Maintainer:innen und den Repo-Agenten übergeben.

Optional kann der Masterprompt zusätzlich im Wissensspeicher gesichert werden. Wichtig: Prüfe, dass
der Masterprompt als System-Prompt unterhalb des 8000-Zeichen-Fensters bleibt, damit alle
Kernanweisungen vollständig geladen werden. Für Custom-GPTs empfiehlt sich ein dediziertes
System-Prompt-Feld, das das korrekte Handling von Kodex-Kommandos, Save/Load und Progressionsphasen
betont.

## Beispielworkflow (Setup & Autoload)

1. Öffne `meta/masterprompt_v6.md`, kopiere den vollständigen Text in das
   Anweisungsfenster der Zielplattform und dokumentiere den Upload im internen
   Protokoll (`internal/qa/logs/`).
2. Lade anschließend `README.md`, `master-index.json` und die 18 Runtime-Module
   wie oben beschrieben in den Wissensspeicher.
3. Kontrolliere jeden YAML-Header auf `title`, `version` und konsistente `tags`.
   Nur Module mit gültigem Header werden vom GPT sicher erkannt.
4. Führe bei Bedarf den Abnahme-Smoketest (Abschnitt
   [Abnahme-Smoketest](#abnahme-smoketest)) durch und protokolliere Autoload,
   Save/Load und Fehlermeldungen pro Plattform.
5. Für Mission Seeds, Encounter- oder Arc-Generatoren verweist du den GPT auf
   [gameplay/kreative-generatoren-missionen.md](../../gameplay/kreative-generatoren-missionen.md)
   sowie die dort verlinkten Unterkapitel. Diese Module enthalten sämtliche
   Tabellen, YAML-Beispiele und Briefing-Vorlagen.

## Referenzen & Fixtures

- **Vollständiges Test-Save (v6):** `internal/qa/fixtures/savegame_v6_test.json` enthält Cross-Mode-
  und Arena-Spuren, `logs.trace[]`, `logs.psi[]`, `logs.arena_psi[]`,
  `economy.wallets{}` sowie `campaign.rift_seeds[]`. Es dient den
  Acceptance-Prüfpunkten 4 und 10 als Save-Quelle und wird bei Schema-Updates gespiegelt.
- **Schema-Referenz:** `systems/gameflow/saveGame.v6.schema.json` bildet das kanonische
  Save-Schema ab; `load_deep()` validiert Saves dagegen und bricht bei fehlenden Containern mit
  `Save-Schema (saveGame.v6)` ab. Die Datei liegt nur für Tool-Validierung im Repo und wird
  **nicht** in den Wissensspeicher geladen – für GPT-Validierung gilt das Kompakt-Profil in
  `systems/gameflow/speicher-fortsetzung.md` („Kompakt-Profil für GPT (Save v6)“).
- **QA-Runner:** `npm run test:acceptance` sowie `tools/test_acceptance_followups.js` prüfen die
  Mission‑5/HUD-Golden-Files aus `internal/qa/fixtures/mission5_badge_snapshots.json`. Beide
  Läufe gehören zu den Pflichttests und werden im QA-Log referenziert.
- **High-Level-Progression:** `internal/qa/fixtures/savegame_v6_highlevel.json` zeigt drei Stände
  (Lvl 8/120/520) mit Seed-Pools und optionaler `seed_tier`-Kennzeichnung. Nutzung: Regression für
  Rifts und Endgame-Scaling; die Datei liegt nur lokal als QA-Bezugspunkt und ist nicht Teil des
  produktiven Wissensspeichers.
- **Schema-voller Save:** `internal/qa/fixtures/savegame_v6_full.json` vereint Level 7/120/512 mit
  offenen und geschlossenen Seeds, vollständigem UI-Block, Wallet-Splits, Arena-/PvP-/Psi-Logs
  sowie Merge-Conflict-Einträgen. Der Datensatz belegt alle Pflichtcontainer und eignet sich für
  Roundtrip-Tests und Loader-Dedupe.
- **HUD-Overlays für Verfolgungen/Massenkonflikte:** Start-Overlay `EP·MS·SC · MODE · Gate/FS`
  setzen, Crash/Stress im HUD notieren und Massenkonflikte mit Flag `Mass Conflict` markieren.
  Sonder-Overlays sollen zusätzlich strukturierte `logs.hud[]`-Events (`vehicle_clash`,
  `mass_conflict`) enthalten, damit QA-Parser und Checks reproduzierbar bleiben.
- **Mission‑5 Badge-Snapshots:** `internal/qa/fixtures/mission5_badge_snapshots.json` enthält
  HUD- und Flag-Referenzen (Gate 2/2, FS 0/4, SF‑OFF/SF‑ON, Boss‑DR). Der Follow-up-
  Runner `tools/test_acceptance_followups.js` prüft die Strings automatisiert, die
  manuelle Mission‑5-Dokumentation bleibt Teil des Abschluss-Reports.

## Testumfang und Meilensteine

- **HQ und Kodex-HUD:** Briefings, Loop-Start, Archiv-Updates, Ask→Suggest-Wechsel und
  Eskalationsregeln gegentesten.
- **Antwortformat & Spannung:** Prüfen, ob das GPT eine straffe Abschnittsstruktur liefert, den
  erwachsenen Thriller-Ton hält und relevante Infos dicht bündelt, ohne abzuschweifen.
- **Progressionsstufen:** Frühphase (Tutorial, Solo-Kernmissionen), Midgame (Stadtzugang,
  Fraktionskontakte, erweiterte HQ-Räume) und Endgame (Riftloop, Boss-Rotation, Artefaktwirtschaft)
  vollständig abdecken.
- **Stadt und Fraktionen:** Freischaltung ab dem definierten Level prüfen, Services (Werkstatt,
  Archiv, Schwarzmärkte) validieren und Ruf-/Fraktions-Wechsel dokumentieren.
- **QA-Splitting Chronopolis:** Frühphase testet ausschließlich den Transit-/Pre-City-Flow.
  Ab Level 10 schaltet die Runtime den Chronopolis-Schlüssel frei, setzt
  `logs.flags.chronopolis_unlocked=true`, `chronopolis_unlock_level=10`, schreibt ein
  `chronopolis_unlock`-Trace-Event (Level/Quelle) und blendet den Toast
  `Chronopolis-Schlüssel aktiv – Level 10+ erreicht.` ein.
- **Squad-Konfigurationen:** Wechsel zwischen Solo, Solo+NPC-Squad und Koop-Teams testen;
  Squad-Rollen, Synergieboni und Respec-Flows nachvollziehen.
- **PvP-Inhalte:** Queue-Aufbau, Regeltext, Fraktionsboni, Belohnungen sowie Safe-Zone/Combat-Zone-
  Trennung beobachten.
- **Riftloop und Sonderereignisse:** Loop-Reset, Rekonfiguration der Missionsketten und Auswirkungen
  auf Paradoxon-Index und Kodex prüfen.
- **Paradoxon-Anweisung:** Sicherstellen, dass Paradoxon-Index, Resonanz und `ClusterCreate()` exakt
  wie im Regelkern laufen (Reset auf 0 nach Seed-Anlage, Seeds erst nach Episodenende spielbar) und
  dass Riftloops keine unerlaubten Shortcuts erzeugen.

> **Manueller Abgleich:** Der Beta-GPT deckt Mission‑5-Badge-Check, Ask→Suggest-Wechsel,
> Accessibility-/Offline-Hinweise sowie die Acceptance-Smoke-Checkliste ab, Tester:innen müssen
> jedoch prüfen, ob der Autolauf jeden Punkt tatsächlich dokumentiert. Fehlen Nachweise, forderst du
> sie im selben Chat explizit nach oder ergänzt sie manuell im Report.

## Copy-&-Paste-Auftrag für den GPT

Der komplette Auftrag steht im folgenden Copyblock. Ein Klick auf das Kopiersymbol umfasst den
Abschnitt von der Überschrift bis zum Abschluss-Hinweis.

> **Einmal senden, vollständigen QA-Run abwarten:** Der GPT simuliert Solo-, NPC-Squad-, Koop- und
> PvP-Szenarien selbstständig. Tester:innen posten diesen Auftrag genau einmal und warten, bis alle
> Abschnitte samt Abschluss-Blocks geliefert wurden.

> **Vor dem Absenden prüfen:** Ist das Wissenspaket vollständig geladen (Masterprompt, README,
> Index, Runtime-Module, diese Briefing-Datei)? Ist das Speicherfenster groß genug für den
> System-Prompt? Falls nein, zuerst Aufteilung oder Kürzung vornehmen, damit der GPT den
> vollständigen
> Auftrag verarbeiten kann.

```text
> (OOC: Spieleentwickler) Bitte lies den kompletten ZEITRISS-Datensatz aufmerksam und führe
> nacheinander folgende simulierte Durchläufe als Chrononaut: Solo ohne Begleitteam, Solo mit NPC-
> Squad, Koop mit einem voll simulierten Spielerteam (inkl. Absprache, Rollen- und Loot-Verteilung)
> sowie PvP-Gefechte zwischen zwei simulierten Fraktionen. Für jede Phase (Frühphase, Midgame,
> Endgame) müssen HQ-Briefing, Mission, Stadt-/Fraktionsmodule, Paradoxon-Index-Handling und Kodex-
> HUD demonstriert werden. Führe zusätzlich Rifts in mindestens drei Level-Clustern durch (z. B.
> 1–25, 80–150, 400–1000), inklusive Loop-Reset, Seed-Öffnung, Artefaktwirtschaft und Auswirkungen
> auf Paradoxon-Index und Kodex. Stelle sicher, dass alle Squad-Mitglieder und PvP-Gegner
> glaubwürdig agieren (inkl. Chat-/Voice-Callouts) und dokumentiere Sync-, Save- und
> Konfliktauflösungen.
>
> Bündle die Ergebnisse in klaren Abschnitten und halte einen straffen,
> erwachsenen Agenten-Thriller-Ton ohne Abschweifungen.
>
> Prüfe Save/Load mit dem aktuellen `saveGame`-Schema (Pflichtfelder laut
> Speicher-Modul: `save_version`, `zr_version`, `location`, `phase`, `campaign`,
> `character`, `economy` inklusive `wallets{}`, `logs` mit `artifact_log`, `market`,
> `offline`, `kodex`, `alias_trace`, `squad_radio`, `foreshadow`,
> `fr_interventions`, `psi`, `arena_psi`, `trace`, `hud`, `flags` sowie `ui`,
> `arena`, `arc_dashboard`). Kontrolliere HQ-Briefing-Schleifen,
> Accessibility-Dialoge,
> Offline-Hinweise sowie Ask→Suggest- und Kodex-Kommandos. Cross-Mode-Saves müssen
> getestet werden (z. B. Solo-Save in Koop importieren, Koop-Save in PvP laden und
> Konflikte kennzeichnen). Decke bei Save- und Load-Prüfungen auch späte Progression
> ab (Level 100+, 400+, 1000) und halte fest, wie Artefakt-/Rift-Boni, Wallets und
> Psi-/Fraktionswerte skaliert werden. Für den Ökonomiepfad nutze explizit
> Level 120, 512 und 900+ als Prüfanker (HQ-Pool, Wallet-Splits,
> Chronopolis-Sinks) und vermerke, ob die Richtwerte eingehalten werden.
> Dokumentiere jede Unstimmigkeit, Balance-
> Frage oder Regelunklarheit.
>
> Hänge an deine Antwort einen Abschnitt `Test-Save (JSON)` an. Er enthält einen
> vollständig ausgefüllten `saveGame`-Block mit Dummy-Testdaten auf Basis des
> kanonischen Schemas (`save_version`, `zr_version`, `location`, `phase`,
> `campaign`, `character`, `economy` inkl. `wallets{}`, `logs` mit `artifact_log`,
> `market`, `offline`, `kodex`, `alias_trace`, `squad_radio`, `foreshadow`,
> `fr_interventions`, `psi`, `arena_psi`, `trace`, `hud`, `flags`, dazu `ui`,
> `arena`, `arc_dashboard`) sowie passende Kodex- und Charakterwerte.
> Bilde darin mindestens
> zwei Level- und Rift-Varianten ab (z. B. <10, 120, 500+ inklusive Seeds und
> Artefaktboni), damit Skalierung und Persistenz über den vollen Bereich 1–1000
> validiert werden können. Gib den Block in einem ```json```-Snippet aus, damit der
> automatische Abgleich ohne Nachbearbeitung möglich ist. Zusatzfelder, die
> ausschließlich für nachgelagerte Tools gedacht sind, dürfen angehängt werden,
> müssen aber das Save-Schema nicht verletzen und werden vom Serializer ansonsten
> ignoriert. Der JSON-Block kann als Appendix ans Ende der Antwort oder direkt
> als Evidenz unter einem ISSUE-Block erscheinen; beide Varianten sind gültig
> und werden vom Runner/Parser akzeptiert.
>
> Führe danach den **„Mission 5 Badge-Check“** wie im QA-Fahrplan beschrieben
> durch: Starte mit `Gate 2/2`, **Schritt 0: setze vor Missionsbeginn `!sf off`**,
> beginne Mission 5, bestätige Toast, Badge (`SF-OFF`) und den HUD-Zähler
> (`FS 0/4`) und halte den HUD-/Log-Auszug fest. Prüfe zum Abschluss den
> Badge-Reset auf `SF-ON` nach Abbruch oder Abschluss (HUD-Log +
> `logs.flags.self_reflection_auto_reset_*`). Die automatisierten Snapshots im
> QA-Runner (`tools/test_acceptance_followups.js`) dienen als Referenz, das
> manuelle Protokoll bleibt Pflicht.
>
> Arbeite zusätzlich jeden Punkt der in diesem Dokument hinterlegten
> Acceptance-Smoke-Checkliste (siehe Abschnitt „Acceptance-Smoke-Checkliste“)
> ab, vermerke Abweichungen im Evidenz-Block und kennzeichne die Prüfnummer
> (1–15) pro Befund.
>   Acceptance-Smoke-Checkliste (Kurzfassung zum Abarbeiten im selben Lauf):
>   1. `Spiel starten (solo klassisch)` → Erschaffung → HQ-Intro → Briefing → SC 1
>   2. `Spiel starten (solo schnell)` → Rolle → Defaults → Briefing/SC 1
>   3. `Spiel starten (npc-team 3 schnell)` → Autogen-NSCs (3) → Briefing
>   4. `Spiel starten (npc-team 5)` → Fehlertext „NPC-Begleiter: 0–4 (Team gesamt 1–5).
>      Bitte erneut eingeben (z. B. npc-team 3).“
>   5. `Spiel starten (gruppe schnell)` → 2 Saves + 1 Rolle → Briefing
>   6. `Spiel starten (gruppe 3)` → Fehlertext „Bei gruppe keine Zahl angeben.
>      (klassisch/schnell sind erlaubt)“
>   7. `Spiel laden` + kompatibler Save → Kodex-Recap-Overlay → HQ/Briefing
>   8. `Speichern` während Mission → Blocker „Speichern nur im HQ …“
>   9. Gear-Check: „Multi-Tool-Armband ausrüsten“ bleibt als Armband im Loadout
>   10. „Px 5“ triggern → Hinweis: Seeds erzeugt, spielbar nach Episodenende, Reset danach
>   11. `!helper boss` nach Mission 4 → Foreshadow-Liste zeigt Szene 5/10, Toast
>       `Gate blockiert – FS 0/4 (Gate 2/2 bleibt gesetzt)`
>   12. Mission 5 → **Schritt 0 `!sf off` vor Missionsstart**, HUD meldet
>       `Boss-Encounter in Szene 10`, `GATE 2/2`, ggf. `SF-OFF`; Szene 10 Toast
>       `Boss-DR aktiviert – −X Schaden` (DR nach Teamgröße laut
>       [Boss-DR-Skala](../../gameplay/kampagnenstruktur.md#boss-rhythmus-pro-episode))
>       und Reset auf `SF-ON`
>   13. Psi-Charakter: Aktion löst `Psi-Heat +1` aus, Reset auf 0 nach
>       Konflikt/HQ-Transfer
>   14. `!accessibility` → `High Contrast`, `Badges: dense/compact`, `Output pace:
>       slow`; Toast notieren, Save-Preview aktualisiert
>   15. Save laden → `!accessibility` erneut öffnen → Einstellungen persistiert
>       (`contrast: high`, `badge_density: dense|compact`, `output_pace: slow`)
>
> Erstelle nach Abschluss aller Simulationen eine strukturierte Ergebnisübersicht ausschließlich in
> folgendem Format (eine Leerzeile trennt die Blöcke, keine zusätzlichen Kommentare). Den JSON-
> Appendix kannst du entweder nach dem letzten Block oder innerhalb des passenden ISSUE als
> Evidenz platzieren – Hauptsache, er bleibt als ```json``` formatiert.
>
> ISSUE #<laufende Nummer>
> - Beobachtung: <kurze Beschreibung>
> - Diagnose: <Root Cause oder Regelverweis>
> - Evidenz: <Reproduktionsschritte oder Log-Hinweis>
>
> Lösungsvorschlag
> - Ansatz: <Empfohlene Korrektur>
> - Risiken: <Folgen oder Abhängigkeiten>
>
> To-do
> - Codex: <konkreter Umsetzungsauftrag>
> - QA: <benötigter Test oder Nachweis>
>
> Nächste Schritte
> - Maintainer:innen: <Sync- oder Upload-Aktion>
> - Notizen: <optionale Hinweise>
>
> Wiederhole diesen Block für jedes identifizierte Thema. Wenn kein weiteres Thema offen ist, beende
> die Antwort nach dem letzten Block ohne zusätzliche Zusammenfassung.
```

### Atmosphere Contract (Stil-Check)

- Contract-Inhalte: 3rd-Person-Narration (`voice_profile = gm_third_person`),
  Physicality-Guard inkl. Banned Terms (keine Digitalräume/Matrix/Holodeck),
  Rift = Casefile-Monster-Hunt, Core rational/noir, HUD schlank
  (Ziel 80 % Szene/20 % HUD, max. 2 Toasts/Szene).
- Die Runtime exportiert den Contract als `logs.flags.atmosphere_contract`.
  In QA-Mode (`logs.flags.qa_mode=true`) ist pro Phase ein 8–12-zeiliger
  Exzerpt-Block Pflicht: `logs.flags.atmosphere_contract_capture` mit `lines`,
  `banned_terms.status` (PASS/FAIL, `banned_terms.hits[]`),
  `howto_hits[]`, `rewrite_suggestion` und `hud_toasts`
  (HUD-Toast-Zählung).

### Action & Gewalt Contract (Outcome-Check)

- **PASS:** Gewaltmomente laufen als Actionfilm-Cut (Intent → Cut → Ergebnis),
  keine Schritt-für-Schritt-Beschreibung, kein Body-Handling. Konsequenzen
  erscheinen als Noise/Stress/Heat/Zeitfenster; Loot/Intel nur als Outcome-Tag
  oder Debrief-Recap. `modus action|gewalt` respektiert die gewählte Stufe.
- **FAIL:** Konkrete Gewaltanleitungen, optimierende How-to-Tipps, detailliertes
  Durchsuchen von Körpern oder explizite Verletzungsdarstellungen.
- **Trace:** `logs.flags.platform_action_contract` hält den aktiven Modus.
  Optional können Cuts via `log_action_contract_guard("Notiz", {phase, scene})`
  in `logs.flags.howto_guard_hits[]` abgelegt werden.

### Compliance-Hinweis im QA-Lauf

- Nutze `ShowComplianceOnce(qa_mode=true)`, um nur den HUD-Toast zu setzen und
  den Chat von Compliance-Text freizuhalten. Der Start-Dispatcher übernimmt
  Ansprache und Player-Count aus dem Kommando.

### QA-Flags & Zusatzmarker

- **Boss-Trace:** `logs.trace[].boss` hält beim Missionsstart `type=mini|arc|rift`
  sowie den DR-Wert, damit Boss-Snapshots eindeutig sind.
- **Weirdness-Budget:** `weirdness_budget_status()` liefert QA-Snapshots; Rift-
  Anomalien landen im Casefile-Tracker.
- **SaveGuard-Suffixe:** Alle SaveGuards hängen den Grund konsistent an
  „– HQ-Save gesperrt.“ an. Das erleichtert den Abgleich der Guard-Matrix in
  QA-Logs.

## Ablauf für Tester:innen

### Zusatz-Checks: Verfolgungen & Massenkonflikte

- **Cineastische Verfolgung:** Pro Testlauf eine Verfolgung mit HUD-Startoverlay durchführen,
  Crash/Stress-Einträge festhalten und sicherstellen, dass `Vehicle Clash`-Notizen im Log landen.
- **Massenkonflikt:** Einen kurzen Ansturm oder Rückzug markieren
  (`Mass Conflict`-Flag im HUD, Szenentitel setzen), Kernschaden (3 bzw. 4–5 bei
  schweren Waffen) und Chaos-/Stress-Spitzen loggen; bei drei Chaos-Punkten den
  SG 12 Break-Point prüfen.

1. Masterprompt (`meta/masterprompt_v6.md`), `README.md`, `master-index.json` und alle
   Runtime-Module (ohne `internal/runtime/runtime-stub-routing-layer.md`) wie im Quickstart
   beschrieben laden. Optional Masterprompt zusätzlich in den Wissensspeicher übernehmen.
   Verifiziere, dass der GPT den Begriff **Kodex** korrekt nutzt und keine Legacy-Nennungen wie
   „Codex“ oder veraltete Save-Felder (`zr_version < 4.x`) ausgibt.
2. Den Auftrag oben senden und sicherstellen, dass das GPT jede geforderte Progressionsphase
   (Frühphase, Midgame, Endgame) vollständig durchläuft. Der Run gilt erst als abgeschlossen,
   wenn HQ-Loop, Mission, Stadt-/Fraktions-Interaktionen, Save/Load und Paradoxon-Index-
   Anpassungen demonstriert sind. Fehlende Abschnitte lässt du das GPT in derselben Sitzung
   nachliefern.
3. Prüfen, ob das GPT die gesamte Testmatrix eigenständig abarbeitet und lückenlos dokumentiert:
   - **Solo ohne Begleitteam:** Fokus auf Progression, Ressourcenfluss, Paradoxon-Index und
     Reaktionen des Kodex-HUD ohne externe Einflüsse. Der Kampagnenmodus (`preserve|trigger`) wird
     vor dem Start über `!kampagnenmodus` gesetzt und muss nach dem Start im Save sichtbar sein.
   - **Solo mit NPC-Team:** Verhalten der Squad-KI, Taktik-Befehle, Auto-Revive und Balance der
     Missionsziele kontrollieren. Prüfen, ob NPCs korrekt auf HQ-Briefings, Kodex-Kommandos und
     Stadt-Services reagieren. `!kampagnenmodus trigger` vor dem Start muss das Seed-Feld
     (`campaign.seed_source = trigger`) spiegeln und das Autoteam korrekt skalieren.
    - **Simuliertes Koop-Team:** Kommunikations- und Sync-Prompts, gemeinsame Save-Blöcke,
      Quest-Skalierung sowie Codex-Rollenverteilung validieren. Cross-Session-Saves (Host ↔
      Mitspieler:in) müssen im Protokoll auftauchen. Der Gruppenstart
      `Spiel starten (gruppe schnell)` darf keine zusätzliche Zahlenabfrage zulassen und
      übernimmt den vorher gesetzten Kampagnenmodus in
      `campaign.mode`/`campaign.seed_source`.
   - **Simuliertes PvP:** Matchmaking-Hinweise, Regeltexte, Fraktionsboni und Konfliktauflösungen
     erfassen. Sicherstellen, dass PvP-Gefechte den Paradoxon-Index korrekt adressieren und keine
     Solo-/Koop-Elemente leaken.
   - **Riftloop (Endgame):** Überprüfen, ob Loop-Reset, Boss-Rotation und Belohnungsumwandlung
     konsistent sind. Prüfen, wie Kodex und HUD auf wiederholte Schleifen reagieren.
4. Manueller Save/Load-Test: `saveGame({...})` anfordern, lokal sichern, neuen Chat starten und den
   Reimport prüfen. Der GPT muss `zr_version`, Kodex-Archivdaten und alle Charakterwerte sauber
   rekonstruieren. Zusätzlich Cross-Mode-Prüfung durchführen (z. B. Solo-Save in Koop laden). Der
   Abschnitt `Test-Save (JSON)` aus der GPT-Antwort dient als Referenz und Import-Block für den
   automatisierten Gegencheck in einer frischen ZEITRISS-Instanz; nur dieser JSON-Block wird in die
   zweite Instanz kopiert, das restliche Protokoll bleibt dem QA-Log vorbehalten.
5. Verifizieren, dass der GPT-Output HUD-Presets, Offline-Optionen (`!offline` –
   Kodex-Fallback bei getrenntem ITI↔Kodex-Uplink; Mission läuft weiter mit HUD-Lokaldaten),
   das Accessibility-Panel (`!accessibility`), Paradoxon-Index-Hinweise und Ask→Suggest-Toggle
   erklärt. Achte zudem darauf, dass der GPT im selben Durchlauf den **Mission 5 Badge-Check**
   simuliert, den HUD-/Log-Auszug in den Evidenzen sichert, den Foreshadow-Reset dokumentiert und
    die Chronopolis-Warnung bei Bedarf mit `!chronopolis ack` quittiert. Falls
    Informationen fehlen, gezielt nachfragen, bis alle Acceptance-Smoke-Punkte
    (inkl. Gear-Checks, `Spiel starten`-Varianten, HQ-Erweiterungen, Stadt-
    Diensten, Fraktionswechseln, Rufsystem, Boss-Gates, HUD-Badges, Psi-Heat)
    im Protokoll stehen.
6. Prüfen, ob der GPT im `To-do – Codex`-Block konkrete Umsetzungsaufgaben benennt. Das
   Pflicht-Testpaket für Repo-Agent:innen ist in
   [CONTRIBUTING.md → Verpflichtende Prüfungen](../../CONTRIBUTING.md#verpflichtende-pruefungen)
   dokumentiert und wird unabhängig vom QA-Report durch Codex ausgeführt; der GPT muss die
   Befehle nicht mehr auflisten.
7. Überprüfen, dass die GPT-Antwort alle `ISSUE`-, `Lösungsvorschlag`-, `To-do`-
   und `Nächste Schritte`-Blöcke enthält und keine freien Zusatzabschnitte
   erzeugt. Fehlende Angaben lässt du das GPT in derselben Sitzung nachreichen.
   Dokumentiere zusätzlich für jeden Acceptance-Smoke-Punkt (1–15), ob er
   bestanden wurde oder welcher Nachtest angesetzt ist.
   Ergänze – falls der GPT Auslassungen macht – klar benannte Nachforderungen
   („Fehlt Acceptance-Schritt 9, bitte nachliefern …“) im selben Chat, damit
   Runner und Parser die Nachträge eindeutig zuordnen können.
8. Analyse unverändert in den Report kopieren. Ergänzend können Datum oder
   besondere Beobachtungen als Randnotizen ergänzt werden. Standardplattform ist
   das OpenAI-MyGPT im Beta-Klon.
9. Report an die Maintainer:innen übergeben; daraus entsteht entweder eine neue
   QA-Notiz oder ein Update für bestehende Audits. Ergebnis wird in Codex
   übertragen, damit Aufgaben strukturiert abgearbeitet werden können.

## Abnahme-Smoketest (Runtime-Overlay) {#abnahme-smoketest}

   1. **Dispatcher & Speicherpfade** – Spielstart solo klassisch/schnell, NPC-Teams
   (`npc-team 3|5`), Gruppe (Fehlertext bei Zahl), Gruppe schnell (2 Saves +
   1 Rolle), `Spiel laden` → Kodex-Overlay, Save-Blocker in Mission, Gear-Check
   (Armband bleibt) und Px 5 Hinweis („Seeds nach Episodenende spielbar“).
2. **Boss-Gates & HUD** – `!helper boss` nach Mission 4 kündigt Szene 5/10 und
   `Gate 2/2` an; Mission 5 startet mit Schritt 0 `!sf off`, blendet
   `Boss-Encounter in Szene 10`, `GATE 2/2` und ggf. `SF-OFF` ein, Szene 10
   triggert `Boss-DR aktiviert – −X Schaden` mit Auto-Reset `SF-ON` zum Debrief.
3. **Psi & Ressourcen** – Psi-Konflikt meldet `Psi-Heat +1`, danach Reset;
   HQ-Transfer setzt SYS/Stress/Psi-Heat zurück.
4. **Accessibility & Persistenz** – `!accessibility` speichert Kontrast,
   Badge-Dichte und Ausgabetempo, Toast notieren; nach erneutem Laden bleiben
   die Werte erhalten. Vollständige Wortlaute decken `doc.md` und das
   Tester-Briefing ab.

**Stabile Flows (Regression-Basis)**
- Ask→Suggest-Overlay bleibt getrennt von Self-Reflection und läuft in Solo,
  NPC, Koop und PvP stabil.
- Offline-FAQ (`!offline`) sowie Alias-/Squad-Radio-Logs bestehen den Smoke in
  Solo/NPC/Koop/PvP identisch.
- Gear-Bezeichnungen bleiben erhalten; Armbänder werden nicht normalisiert.

**Dispatcher-Smoke-Basislinie**
| Schritt | Inhalt | Status |
| ------ | ----------------------------- | -------- |
| 1 | Spielstart solo klassisch/schnell | ✅ stabil |
| 2 | NPC-Team 0–4 erstellt (Team gesamt 1–5) | ✅ stabil |
| 3 | Gruppe klassisch/schnell (Fehlertext bei Zahl) | ✅ stabil |
| 4 | Spiel laden → HQ-Recap & Overlay | ✅ stabil |
| 5 | Missions-Blocker verhindern Saves | ✅ stabil |
| 6 | Gear-Armband bleibt erhalten & Px 5 Hinweis sichtbar | ✅ stabil |

## Boss-Gate-Status & Terminologie (Referenzstrings)

| Zeitpunkt | Foreshadow-Ziel | Gate-Anzeige | Erwartete Strings |
| --------- | ---------------- | ------------ | ----------------- |
| Episodenstart/HQ | noch nicht gesetzt | kein Gate-HUD | `!boss status` meldet nur Saisonstand `Mission FS 0/4` (Core) bzw. `0/2` (Rift) |
| Nach Mission 4/9 | Hinweise stehen aus | `Gate 0/2` (HUD/Toast) | `!helper boss` zeigt Foreshadow-Liste Szene 5/10, Toast `Gate blockiert – FS 0/4 (Gate 2/2 bleibt gesetzt)` |
| Start Mission 5/10 | FS-Zähler läuft | `GATE 2/2` + `FS 0/4` (Core) bzw. `FS 0/2` (Rift) | `!boss status` meldet `Gate 2/2 · Mission FS 0/4` (oder `0/2`); sichtbarer `GATE 2/2`-Toast |
| Szene 10 | alle Hinweise platziert | `GATE 2/2` + Boss-Toast | `Boss-DR aktiviert – −X Schaden pro Treffer` (DR skaliert nach Boss-Typ und Teamgröße 1–5) |

## QA-Checks 2025-06-27 – Mission 5 Gate, Suggest & Arena

- **Mission 5/10 Foreshadow-Gate & Boss-Toast.** `ForeshadowHint()` zweimal aufrufen
  (`Gate 2/2` Evidenz), HUD-Log vor Missionsstart sichern und `!boss status`
  nach `StartMission()` notieren. Das Overlay muss auf `FS 0/4` (Core) bzw. `FS 0/2` (Rift)
  zurücksetzen, der Befehl meldet parallel den Saisonbedarf (`Gate n/2 · Mission FS n/4`
  bzw. `n/2`).
  {# LINT:FS_RESET_OK #}
- **Gate vs. Season Total.** Halte zwei Nachweise fest: HUD-Log `Gate 2/2` vor dem Start
  sowie `scene_overlay()`/`!boss status` direkt nach `StartMission()`.
- **Ask→Suggest Wechsel.** `modus suggest` erzeugt den Toast `SUG-ON` und ergänzt das Overlay
  um `· SUG`; `modus ask` liefert `SUG-OFF`. Dokumentiere beide Meldungen mit Overlay-Zeile.
- **Vehikel-Chases.** `vehicle_overlay('vehicle', tempo, stress, schaden)` einsetzen und die
  Werte im QA-Log referenzieren.
- **Phase-Strike Arena (Zusatztest).** `arenaStart()` aktiviert PvP, setzt
  `phase_strike_tax = 1` und löst den HUD-Toast „Arena: Phase-Strike …“ bei
  `phase_strike_cost()` aus. Dokumentiere Save-Blocker `SaveGuard: Arena aktiv …`
  separat, damit der PvP-Guard auch nach der neuen Accessibility-Prüfung
  nachvollziehbar bleibt.
- **Self-Reflection Guard.** Acceptance-Schritt 12 verlangt `SF-OFF` beim Start
  von Mission 5 und den automatischen Reset auf `SF-ON` nach Missionsende –
  sowohl bei Abschluss als auch bei Abbruch. Das Flag wird ausschließlich durch
  `!sf off` gesetzt; `scene_overlay()` (`… · SF-OFF`) und HUD-Badge protokollieren
  Start & Reset.
- **Accessibility/Offline Acceptance.** Ergänze `!help offline`/`offline_help()`
  sowie Accessibility-Menü-Checks (`/help access`, HUD-Kontrast) als
  Pflichtschritte – Acceptance 14/15 verlangen HUD-Toast + Persistenzkontrolle.
- **Chronopolis Acceptance-Smoketest.** `tools/test_chronopolis_high_tier.js` bildet Markt-Limits,
  Px-Trace und Hochstufen-Angebote ab; Debrief-Zeilen im QA-Log 2025-06-28 verlinken.
- **Automatisierter Beleg.** `tools/test_acceptance_followups.js` reproduziert Foreshadow-Reset,
  Suggest-HUD, Vehikel-Overlay-Notizen und Arena-Toast für Beta-/MyGPT-Spiegel.

## Playtest-Feedback (externe Rückmeldung)

Wir freuen uns über Rückmeldungen zu Flow und Regelfragen. Scanne den QR-Code
oder besuche [www.zeitriss.org](https://www.zeitriss.org/), um Eindrücke aus
Playtests zu schicken.

## Template für den Report an die Maintainer:innen

```text
# Playtest-Report ZEITRISS
- Version: (z. B. 4.2.5 beta)
- Testplattform: OpenAI (MyGPT Beta)
- Datum & Uhrzeit: (lokal)
- Tester:in: (Alias)

## GPT-Analyse
(Paste aus der GPT-Antwort – inklusive aller ISSUE-/Lösungsvorschlag-/To-do-/
Nächste-Schritte-Blöcke)

## Save/Load-Beleg
saveGame({...})

## Eigene Anmerkungen
- (Optionale Ergänzung)
- (Weitere Beobachtungen)
```

## Hinweise zur Weiterverarbeitung

- Maintainer:innen übertragen die strukturierten ISSUE-/Lösungsvorschlag-/
  To-do-/Nächste-Schritte-Blöcke aus der GPT-Antwort in eine QA-Notiz (z. B. als
  Ergänzung zu `internal/qa/audits/ZEITRISS-qa-audit-2025.md` oder einen neuen
  Eintrag in den Fahrplan). Der Save/Load-Block dient als Nachweis für den
  Kodex- und Charakterstand.
- Reports werden lokal oder in einer gesicherten Team-Ablage archiviert, damit der Ablauf offline
  nachvollziehbar bleibt.
- Weitere Durchläufe mit alternativen Solo-Builds oder Gruppen-Saves nutzen
  denselben Auftrag. Die Ansprache, Kodex-Hinweise und Offline-Optionen bleiben
  dadurch konsistent. Spiegelplattformen (Store-GPT, LUMO, lokal) erhalten den
  freigegebenen Stand ohne eigene QA-Optimierung; dokumentiere nur Abweichungen
  bei Bedarf.
- Menschliche Gruppen können optional nachziehen, sind aber nicht Teil des
  Standard-Workflows. Primär dient der Auftrag dazu, dass das GPT sämtliche
  Multiplayer- und Progressionspfade autonom simuliert.
- Für PvP- oder Fraktions-Audits empfiehlt sich eine Gegenüberstellung der getesteten Fraktionen,
  Rufstufen und Stadt-Services. Dokumentiere Abweichungen, damit Balancing-Tasks gezielt priorisiert
  werden können.

## Acceptance-Smoke-Checkliste

> **Hinweis:** Der standardisierte Beta-GPT-Testprompt verpflichtet sich, jeden
> Punkt dieser Checkliste automatisch abzudecken. Der Smoketest gehört exklusiv
> in QA-/Beta-GPT-Läufe oder CI (`scripts/smoke.sh`), nicht in den regulären
> Spielablauf. Dokumentiere Abweichungen im QA-Log und im Fahrplan unter den
> Deepcheck-Aufgaben.

### Dispatcher-Starts & Speicherpfade

1. `Spiel starten (solo klassisch)` → Erschaffung → HQ-Intro → Briefing → SC 1
2. `Spiel starten (solo schnell)` → Rolle → Defaults → Briefing/SC 1
3. `Spiel starten (npc-team 3 schnell)` → Autogen-NSCs (3) → Briefing
4. `Spiel starten (npc-team 5)` → Fehlertext „NPC-Begleiter: 0–4 (Team gesamt 1–5).
   Bitte erneut eingeben (z. B. npc-team 3).“
5. `Spiel starten (gruppe schnell)` → 2 Saves + 1 Rolle → Briefing
6. `Spiel starten (gruppe 3)` → Fehlertext „Bei gruppe keine Zahl angeben.
   (klassisch/schnell sind erlaubt)“
7. `Spiel laden` + kompatibler Save → Kodex-Recap-Overlay → HQ/Briefing (keine Startfrage)
8. `Speichern` während Mission → Blocker „Speichern nur im HQ …“
9. Gear-Check: „Multi-Tool-Armband ausrüsten“ bleibt als Armband im Loadout
10. „Px 5“ triggern → Hinweis: Seeds erzeugt, spielbar nach Episodenende, Reset danach

### Boss-Gates & HUD-Badges

11. `!helper boss` nach Mission 4 → Foreshadow-Liste zeigt Szene 5/10. HUD-Toast
    `Gate blockiert – FS 0/4 (Gate 2/2 bleibt gesetzt)`, bis Hinweise erfüllt
    sind.
12. Mission 5 starten → HUD meldet den Encounter-Hinweis
    `Boss-Encounter in Szene 10`, zeigt `GATE 2/2` und – falls zuvor deaktiviert –
    `SF-OFF`. Der Foreshadow-Zähler startet bei `FS 0/4` und zählt hoch. In
    Szene 10 erscheint der Toast `Boss-DR aktiviert – −X Schaden pro Treffer`
    (DR nach Teamgröße laut
    [Boss-DR-Skala](../../gameplay/kampagnenstruktur.md#boss-rhythmus-pro-episode));
    beim Missionsende (Abbruch oder Abschluss) setzt die Runtime Self-Reflection
    automatisch auf `SF-ON` zurück.

### Psi-Heat & Ressourcen-Reset

13. Psi-Charakter in Konflikt schicken, Psi-Aktion nutzen → HUD meldet
    `Psi-Heat +1`; nach Konflikt springt Psi-Heat automatisch auf 0. HQ-Transfer
    setzt SYS/Stress/Psi-Heat zurück.

### Accessibility & UI-Persistenz

14. `!accessibility` auslösen → Dialog öffnet sich. `High Contrast`,
    `Badges: dense` oder `compact` und `Output pace: slow` bestätigen; HUD-Toast
    „Accessibility aktualisiert …“ notieren und die aktualisierten UI-Felder im
    Save-Preview sichern. Legacy-Werte `full|minimal` werden auf
    `standard|compact` gemappt.
15. Save laden → `!accessibility` erneut öffnen → Einstellungen sind
    persistiert (`contrast: high`, `badge_density: dense|compact`,
    `output_pace: slow`).

### QA-Abgleich 2025-03-23

- **Boss-Gates & HUD-Badges:** `scene_overlay()` blendet bei deaktivierter
  Selbstreflexion das Badge `SF-OFF` ein und führt Foreshadow-Zähler mit, während
  `assert_foreshadow()` in Präzisionsläufen Warnungen ausgibt; validiert über
  `GM_STYLE=precision node tools/test_foreshadow.js` sowie das HUD-Skript.
- **Psi-Heat-Reset:** `migrate_save()` und `hydrate_state()` setzen Psi-Heat in
  Konflikt- und HQ-Transfers deterministisch zurück und verhindern Speichervorgänge
  mit Restwärme.
- **Log-Verweis:** Vollständiges Prüfprotokoll im QA-Log vom 2025-03-19.
