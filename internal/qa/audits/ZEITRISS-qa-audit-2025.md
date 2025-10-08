---
title: "ZEITRISS QA-Audit 2025"
version: 1.0.0
tags: [meta, qa]
---

# ZEITRISS QA-Audit 2025

## Kontext und Auftrag
Die QA-Crew hat den Systemtest zu **ZEITRISS 4.2.2** mit Schwerpunkt auf
Systemkohärenz, Balance, HQ-Abläufe und urbane Interaktionen dokumentiert. Dieses
Audit bündelt die Erkenntnisse, bewertet den aktuellen Umsetzungsstand und
priorisiert die nächsten Entwicklungsschritte. Grundlage sind die aufgeführten
Testbeobachtungen sowie der Repositorystand `c9a4da2`.

## Rollen & Artefakte
- **Tester:innen** führen Playthroughs in den vorgesehenen GPT-Instanzen durch
  und kopieren das Ergebnis unverändert in das QA-Log unter
  `internal/qa/logs/2025-beta-qa-log.md`.
- **Maintainer:in (Solo-Setup 2025)** führt alle Beta-GPT-Tests durch,
  indem der vorbereitete Testprompt in den Beta-Klon geladen wird. Der GPT
  spielt den vollständigen QA-Lauf autonom durch und liefert strukturierte
  `ISSUE`-, `Lösungsvorschlag`-, `To-do`- und `Nächste Schritte`-Blöcke. Die
  komplette Antwort wird unverändert an Codex übergeben, der die Ergebnisse in
  Repo-Tasks und Dokumentationen überführt.
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
der Arena und das uneinheitliche „Heat“-Vokabular, das Spieler:innen wie Tools
verwirrt. Ohne Korrektur gefährden diese Punkte die Anschlussfähigkeit von
Regelreferenzen, die Progressionsökonomie und das Balancing in
Hochstufen-Spielrunden.

## Maßnahmenkatalog (Priorisiert)
1. **Modulnummern & Cross-References harmonisieren.** Modul 6 verweist weiterhin
   auf einen „ausgelassenen siebten Teil“, während Master-Index und Dateien
   Modul 7 führen. Status: *erledigt* – Modul 6, Modul 7, Kampagnenübersicht und
   README benennen die Sequenz nun konsistent.
2. **Paradoxon-Farm in der PvP-Arena unterbinden.** Arena-Belohnungssystem an
   Episoden- oder Rufmarker koppeln. Status: *erledigt* – Px-Bonus wird nur noch
   einmal pro Episode vergeben; `arena_episode_stamp` markiert den konsumierten
   Lauf.
3. **Heat-Terminologie trennen.** Psi-, Alarm-, Tech- und Stress-Anzeigen klar
   benennen; Save-Schema migrieren. Status: *erledigt* – Psi-Heat wird nun
   explizit geführt (`psi_heat`), Save-Version 5 migriert Altstände automatisch,
   HUD/Toolkits zeigen Psi-Heat getrennt von Stress & Tech-Heat.
4. **Exploding-DMG-Spitzen begrenzen.** Arena/Boss-Dämpfer als Pflicht setzen
   und Boss-DR automatisieren. Status: *erledigt* – Arena-HUD halbiert
   Exploding-Overflow automatisch, Boss-Spawn vergibt DR 2/3 inkl. HUD-Hinweis.
5. **High-Level-Progression auf Prestige-Perks umstellen.** Attribute nicht
   weiter erhöhen, stattdessen qualitative Boni verankern. Status: *erledigt* –
   Core-Regelwerk setzt ab Prestige-Level auf erzählerische Perks und ersetzt
   den Standard-Attributsbonus durch Legendenpfade.
6. **Psi vs. Non-Psi balancieren.** Phase-Strike-Kosten in PvP anheben,
   Anti-Psi-Grundschutz verbreitern. Status: *erledigt* – Arena setzt
   `phase_strike_tax = +1 SYS`, Kernanzüge tragen `psi_buffer` (+2 SG,
   neutralisiert Bonus-Schaden).
7. **Tech-Dominanz-Check auf kleine Teams ausweiten.** `tech_heat` früher
   triggern und Gerätezwang durchsetzen. Status: *erledigt* – Solo- und
   Duo-Teams feuern `tech_solution()` nun bei niedrigeren Limits und die
   Toolkit-Makros sperren Tech-Ketten, bis `confirm_device_slot()` ein Field Kit
   bestätigt.
8. **Suspend-Snapshot als Komfortfunktion implementieren.** HQ-Save-Pflicht
   erhalten, aber Session-Pause erlauben. Status: *erledigt* – `!suspend` legt
   einen 24h-Snapshot an, `!resume` setzt ihn einmalig fort und respektiert den
   HQ-Deepsave.
9. **Exfil-Kommunikation im HUD verstärken.** Auto-Toasts für Arming/Alt-Anchor
   und RW-Ticks. Status: *erledigt* – `!exfil arm/alt/tick/status` triggern
   automatische HUD-Toasts, aktualisieren Anchor/ALT und spiegeln den Timer im
   Overlay.
10. **Arena-Matchmaking mit Tier-Loadouts absichern.** Artefakt-Spitzen kappen,
    Proc-Budget limitieren. Status: *erledigt* – Runtime-Stub erzwingt
    Tier-Gates, kappt Artefakt-Überhänge und bremst Proc-Ketten mit pro Tier
    gesetztem Budget.
11. **Boss-Foreshadow-Gate erzwingen.** Szene 10 blockieren, bis Hinweise
    geliefert sind. Status: *erledigt* – `NextScene()` hält Szene 9, bis vier
    (Core) bzw. zwei (Rift) Foreshadows über Makros registriert sind und meldet
    den Gate im HUD. Nachweis: Commit `b245bef` (*Boss-Foreshadow-Gate aktiviert*)
    und QA-Log 2025-03-19 (Acceptance-Smoke-Abgleich).
12. **Mission-Generator linten.** Gewichte und Duplicate-Seeds automatisch
    prüfen. Status: *erledigt* – `scripts/lint_mission_generator.py` prüft die
    Pools und stellt d24-Abdeckung sicher. Nachweis: Commit `5a3fbb3`
    (*Add mission generator lint*); automatisierte Prüfung läuft über
    `scripts/tests/test_lint_mission_generator.py`.
13. **Endgame-Ökonomie justieren.** Chronopolis-Angebote mit Rang/Research-Gates
    und Daily Stock versehen. Status: *erledigt* – Runtime koppelt das
    Tagesangebot an Dienstgrad und Research-Level, der Pool rotiert filmisch pro
    HQ-Zyklus. Nachweis: Commit `7d91e53` (*Implement Chronopolis stock gating*);
    Regressionseintrag im QA-Log steht aus.
14. **Signal-Space-Konsequenz in Texten verankern.** Remote-Hack-Formulierungen
    bereinigen, `comms_check()` erzwingen. Status: *erledigt* – Arena-Makro
    zwingt `must_comms`, Ausrüstungshinweis verankert Hardwarepflicht.
    Nachweis: Commit `8fe8de2` (*Sichere Remote-Hacks über comms_check*);
    QA-Log-Erweiterung für Remote-Hacks ist geplant.
15. **Urban Quick-Card zentral anbieten.** Deckungs- und Verfolgungsreferenzen in
    `/help` bündeln. Status: *erledigt* – `/help urban` liefert Deckungsgrade,
    Distanzstufen und HUD-Tags; README verankert die Schnellhilfe. Nachweis:
    Commit `52d1ba5` (*Add HUD quick-help cards for urban ops and SG benchmarks*);
    QA-Log-Eintrag folgt nach nächstem Stadt-Playtest.
16. **HQ-Moments mechanisch verankern.** Tabelle mit Buff-Icons einführen.
    Status: *erledigt* – Toolkit listet HQ-Buffs als HUD-Icons inkl.
    Makro-Snippet, Dopplungen werden per Kampagnenflag geblockt. Nachweis:
    Commit `9a1675d` (*Intro-Guard und HQ-Moments nachziehen*); QA-Log-Ergänzung
    für HQ-Runs steht aus.
17. **Arena zwingt JSON-Würfellog.** `debug_rolls` standardmäßig aktivieren.
    Status: *erledigt* – Toolkit-Default wurde auf `true` gesetzt und README
    dokumentiert das neue Standardverhalten. Nachweis: Commit `8208170`
    (*feat: add transfer frames and debug roll output*) sowie QA-Log 2025-03-19
    (Acceptance-Smoke-Abgleich – JSON-Log aktiv).
18. **Rift-Boss-Drops automatisieren.** Toolkit-Trigger `on_rift_boss_down()`
    für Loot-Erinnerung. Status: *erledigt* – neues Makro setzt den Boss-Flag,
    stößt das para-Loot an und markiert den Legendary-Wurf im Log. Nachweis:
    Commit `22d3c33` (*Automatisiere Rift-Boss-Loot und Arena-Takt*); QA-Log
    reflektiert den Lauf nach nächstem Rift-Test.
19. **Attribut-Cap kommunizieren.** Charaktererschaffung um Prestige-Hinweis
    ergänzen. Status: *erledigt* – Charaktererschaffung betont das Cap bei 10
    und verweist auf Prestige-Aufstiege für höhere Werte. Nachweis:
    Commit `1be6f57` (*Sichert Attributbudget bei der Charaktererschaffung*);
    QA-Log-Ergänzung im Charaktererstellungs-Regressionstest ausstehend.
20. **Arena-Großteams mit Timern steuern.** 30-Sekunden-Takt und Move-Limit im
    HUD. Status: *erledigt* – Arena initialisiert nun Großteam-Zyklen, trackt
    Moves und blendet Timer sowie Limit im HUD ein. Nachweis: Commit `22d3c33`
    (*Automatisiere Rift-Boss-Loot und Arena-Takt*); QA-Log-Eintrag für
    Großteam-Matches wird vorbereitet.
21. **Boss-Pressure-Variationen schützen.** Memory-Pool/Cooldown für
    Druck-Set-Auswahl. Status: *erledigt* – Toolkit setzt eine
    Zweifach-Cooldown-Liste ein, bevor Druck-Sets wieder freigegeben
    werden.
22. **Self-Reflection-Flag sichtbar machen.** HUD-Badge `SF-OFF` ergänzen.
    Status: *erledigt* – Runtime blendet das Badge ein, wenn `self_reflection:
    false` aktiv ist; `!sf on/off` steuern das Flag und loggen den Status.
23. **Intro-Guard beim Laden aktivieren.** Einleitung nur bei Erststart zeigen.
    Status: *erledigt* – Runtime speichert `intro_seen` im UI-State und spielt
    das HQ-Kurzintro nur beim Erststart aus.
24. **DelayConflict für Heist/Street justieren.** Mission-Tags reduzieren
    Verzögerung. Status: *erledigt* – `StartMission()` normalisiert Mission-Tags
    und `DelayConflict` senkt bei `heist`/`street` automatisch die Schwelle.
25. **Briefing mit ☆-Feedback ausliefern.** Overlay standardisieren. Status:
    *erledigt* – Toolkit zeigt das ☆-HUD beim Missionsstart automatisch,
    `briefing_with_stars()` zieht den SG-Zuschlag konsistent nach.
26. **TK-Nahkampf-Cooldown visualisieren.** HUD-Icon nach Einsatz. Status:
    *erledigt* – Runtime blendet `TK🌀` nach `!tk melee` ein und `!tk ready`
    entfernt die Sperre nach der Cooldown-Runde.
27. **Arena-Gebühr progressiv staffeln.** Vermögensabhängige Kosten definieren.
    Status: *erledigt* – Staffelung mit 1 %/2 %/3 %-Brackets koppelt Gebühren an
    das HQ-Vermögen.
28. **Chronopolis-Reset-Rhythmus fixieren.** City-Tick nach Episoden und optional
    nach drei Missionen. Status: *erledigt* – Episodenabschluss triggert
    sofortigen Reset; ein konfigurierbarer Drei-Missions-Takt hält die Stadt
    lebendig.
29. **Gefährdungs-Skala vereinheitlichen.** Einheitliche Risk-Level-Icons.
    Status: *erledigt* – Toolkit formatiert `R1–R4` automatisch als HUD-Badges,
    Artefakt-Pool & HUD-Dokumentation spiegeln die neue Skala.
30. **Würfel-Benchmarks bündeln.** One-Pager für SG/Exploding-Optionen unter
    `/help sg`. Status: *erledigt* – `/help sg` fasst Würfelgrößen, Zielwerte und
    Exploding-Ansagen filmisch auf einer Zeile zusammen.

## Nachverfolgung & Nächste Schritte
1. **Validierung:** Maßnahmen 1–10 anhand der Commits prüfen und Ergebnisse im
   QA-Fahrplan sowie im entsprechenden Abschnitt des QA-Logs dokumentieren.
2. **Dokumentation:** Punkte 11–20 in README, Maintainer-Ops und Glossar
   spiegeln, sobald Runtime-Anpassungen bestätigt sind; Referenzen im QA-Log
   hinterlegen. Jeder QA-Log-Eintrag notiert den verwendeten Beta-GPT-Testprompt,
   damit Regressionen reproduzierbar bleiben. Maintainer-Ops wurde am
   2025-03-21 auf Version 1.2.0 angehoben und beschreibt nun die Spiegelprozesse
   nach MyGPT-Freigabe.
3. **Roadmap:** Themen 21–30 mit der UX-/Tooling-Roadmap verknüpfen, in den
   QA-Fahrplan übernehmen und Priorität über den jeweiligen QA-Log-Eintrag
   abstimmen.

## Befunde Beta-GPT-Lauf 2025-06 (ISSUE #1–#16)
Der Testprompt vom Juni 2025 ergänzt 16 neue Baustellen rund um HQ-Saves,
Gruppenschemata und PvP-Logik. Die folgenden Einträge bilden den aktuellen
Analyse- und Maßnahmenstand ab. Alle Punkte wurden in den QA-Fahrplan
übernommen und stehen dort mit Verantwortlichkeiten sowie Terminankern.

**Status-Legende:** `[ ] Offen`, `[x] Erledigt`

| # | Schwerpunkt | Status | Kerndiagnose | Empfohlene Umsetzung | Auswirkung bei Verzug |
| --- | --- | --- | --- | --- | --- |
| 1 | HQ-Save-Pflichtfelder | [x] Erledigt | Minimal-HQ-Saves ließen `economy`, `logs`, `ui` und `campaign.px` aus. | Serializer ergänzt Defaults (`economy`, `logs`, `ui`), Kampagnen-Px wird synchronisiert, Linterregel `SAVE_REQ_FIELDS` prüft Pflichtpfade. | ✅ Behoben – Saves liefern wieder vollständige Pflichtfelder. Referenz: Commit 3e4f306. |
| 2 | Gruppensave-Konsistenz | [ ] Offen | Drei konkurrierende Arrays für Teamzusammenstellungen. | Normalizer in `load_deep()` verankern; Kanonstruktur `party.characters[]`, Legacy-Aliase dokumentieren. | Merge-Dialoge bleiben unzuverlässig. |
| 3 | Arc-Dashboard | [ ] Offen | Laufzeit nutzt Dashboard, Schema definiert es nicht. | Optionales, aber standardisiertes Objekt dokumentieren; Serializer/Deserializer anbinden. | Story-Hub verliert nach Reload Kontext. |
| 4 | Load-Compliance | [ ] Offen | Einstiegstrigger feuern mehrfach, Flag fehlt. | `ShowComplianceOnce()` vor Recap ausführen, Flag `logs.flags.compliance_shown_today` speichern. | Wiederholte Dialoge direkt nach `!load`. |
| 5 | Hot-Exfil Px-Verlust | [ ] Offen | FAQ widerspricht Runtime-Strafe. | Default `exfil_fail_policy.px_loss=false` setzen oder FAQ präzisieren. | Inkonsistente Spielerwartungen, Balancing-Drift. |
| 6 | Phase-Strike-Kosten | [ ] Offen | PvP-Kosten doppelt definiert, Modus-Flag unklar. | `campaign.mode` als Quelle, Helper `is_pvp()` nutzen, Kosten zentralisieren. | Psi-Balance kippt in Sparring-Szenen. |
| 7 | Accessibility-Dialog | [ ] Offen | Kein einheitliches Menü für Barrierefreiheit. | `hud.accessibility()` mit persistierenden Flags und Onboarding-Preset implementieren. | Spieler:innen ohne Zugang zu Accessibility-Optionen. |
| 8 | Offline-Fallback | [ ] Offen | Kein definierter Offline-Dialog trotz HUD-Alerts. | `offline_help()` + lokales FAQ und Ask→Suggest-Flow offline spiegeln. | Kodex-Hilfe bricht bei Jammern weg. |
| 9 | Semver-Benennung | [ ] Offen | `ZR_VERSION` vs. `zr_version` uneinheitlich im Wording. | Dokumentation harmonisieren, Fehlermeldungen beide Werte nennen, Log ergänzt Runtime-Version. | Fehlermeldungen bleiben missverständlich. |
| 10 | Foreshadow-Gates | [ ] Offen | Fortschritt nicht im Save verankert. | `logs.foreshadow` persistieren und HUD-Badge anbinden. | Gate lässt sich durch Reload unterlaufen. |
| 11 | Koop-CU-Verteilung | [ ] Offen | Team- vs. Charakter-Wallet unklar. | Debrief-Dialog mit Splits, Standard `economy.cu`, persönliche Wallets separat buchen. | Konflikte um Belohnungsverteilung, Save-Drift. |
| 12 | Chronopolis-Warnung | [ ] Offen | Einmaliges Popup ohne Persistenzflag. | `logs.flags.chronopolis_warn_seen` setzen. | Warnung erscheint bei jedem Eintritt erneut. |
| 13 | Ask→Suggest | [ ] Offen | Mechanik gefordert, aber nicht dokumentiert oder standardisiert. | Toolkit-Makro `suggest_actions()` sowie README-Ergänzung bereitstellen. | UX-Lücke in Beratungssituationen. |
| 14 | Suspend-Snapshot | [ ] Offen | Initiative- und Timer-Zustände fehlen beim Resume. | Snapshot um `initiative.order[]`, `initiative.active_id`, `hud.timers[]` erweitern. | Konflikte verlieren Struktur nach `!resume`. |
| 15 | PSI-Buffer-Arena | [ ] Offen | PvP-Dämpfer nicht zentral dokumentiert. | `apply_arena_rules()` bündelt `psi_buffer` + Dämpfer, Dokumentation vereinheitlichen. | Mods/Toolkits setzen Regeln falsch um. |
| 16 | Chronopolis-Marktlog | [ ] Offen | Käufe erzeugen kein Save-Log trotz Px-Auswirkungen. | `logs.market[]` mit Timestamp, Item, Kosten und Px-Klausel speichern. | Px-Verluste bleiben nicht nachvollziehbar. |

**Folgeaufgaben:**

- [ ] QA ergänzt Regressionstests (Dispatcher-Suite, Cross-Mode-Läufe,
      Debrief-Splits) und versieht sie mit Referenzen im QA-Log.
- [ ] Codex erstellt Branches für Schema-/Runtime-Änderungen (#1–#16) und
      verknüpft Commits mit dem Audit.
- [ ] Maintainer:innen synchronisieren README, Modul 12 und Master-Index nach
      Abschluss der jeweiligen Teilaufgaben.

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
