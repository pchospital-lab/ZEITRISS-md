---
title: "Beta-GPT Lauf 2025-10-29 – Rohprotokoll"
version: 1.0.0
tags: [meta, qa-log]
---

# Beta-GPT Lauf 2025-10-29 – Rohprotokoll

Dieses Dokument archiviert den vollständigen Testprompt inklusive Befundliste. Ergänzende Maßnahmen stehen im Fahrplan.

```text
ISSUE #1

* Beobachtung: Widerspruch bei Pflichtfeldern des HQ-Deepsave – die Pseudocode‑Liste „required=[…]“ enthält `logs.foreshadow`, `logs.fr_interventions`, `logs.psi` und `arena` **nicht**, die spätere Pflichtfeld‑Aufzählung verlangt sie jedoch explizit.
* Diagnose: Doppelpflege der Spezifikation in Modul 12; Pseudocode und Text laufen auseinander. Serializer‑Erwartungen sind unklar. 
* Evidenz: **SaveGuard (Pseudocode)** listet u. a. nur `logs{artifact_log,market,offline,kodex,alias_trace,squad_radio,flags}`; im Abschnitt **„Pflichtfelder“** werden zusätzlich `logs.foreshadow`, `logs.fr_interventions`, `logs.psi` und `arena` gefordert. 

Lösungsvorschlag

* Ansatz: Single‑Source der Pflichtfeldliste (Tabellenblock) und Referenz im Pseudocode per „siehe Tabelle“. Serializer klar auf **eine** Liste normieren.
* Risiken: Migrationsbedarf für bestehende Saves ohne die zusätzlichen Logs/`arena`.

To-do

* Codex: Serializer aktualisieren: `assert has(logs.foreshadow, logs.fr_interventions, logs.psi, arena)`; fehlende Blöcke automatisch als leere Strukturen ergänzen und warnen.
* QA: Regressionstest „!save“ mit minimiertem Save (nur Pflichtfelder). Erwartet: **kein** Fehler, fehlende Felder auto‑ergänzt.

Nächste Schritte

* Maintainer:innen: Spezifikation mergen; Deps (Docs/Serializer) synchronisieren.
* Notizen: Changelog mit Migrationshinweis an QA verteilen.

ISSUE #2

* Beobachtung: JSON‑Beispiel im Save‑Kapitel widerspricht der Pflichtfeldliste (es fehlen `economy.wallets{}`, `logs.foreshadow`, `logs.fr_interventions`, `logs.psi`, `arena`).
* Diagnose: Beispiel veraltet; fördert Fehlimplementierungen bei Integrator:innen. 
* Evidenz: Gezeigter Beispiel‑Save enthält nur `logs{artifact_log,market,offline,kodex,alias_trace,squad_radio,flags}` und kein `economy.wallets{}`/`arena`, obwohl diese als Pflicht geführt sind. 

Lösungsvorschlag

* Ansatz: Beispiel‑Save auf Pflichtumfang heben; Kommentarzeilen mit Kurzbeschreibung je Block.
* Risiken: Keine.

To-do

* Codex: Beispiel‑JSON in Modul 12 aktualisieren (inkl. `economy.wallets{}`, `logs.foreshadow[]`, `logs.fr_interventions[]`, `logs.psi[]`, `arena{…}`).
* QA: Lint‑Check: Beispiel lässt sich ohne fehlende Schlüssel laden.

Nächste Schritte

* Maintainer:innen: Doc‑Update ausrollen.
* Notizen: README‑Querverweis „Immersives Laden“ prüfen, ob Screens die neuen Felder zeigen. 

ISSUE #3

* Beobachtung: Arena‑Modus soll HQ‑Saves blockieren, SaveGuard prüft aber nur `state.location=="HQ"`/Exfil‑Flags; ein expliziter Check auf `arena.active` fehlt.
* Diagnose: Potenzielle Lücke – falls `state.location` im PvP fälschlich „HQ“ bleibt, könnte ein Save trotz aktiver Arena durchgehen.  
* Evidenz: SaveGuard‑Assertions listen keinen Arena‑Blocker; Toolkit beschreibt hingegen, dass Arena SaveGuards aktiviert und Saves während Arena sperrt.  

Lösungsvorschlag

* Ansatz: SaveGuard erweitern: `assert not arena.active, "Arena aktiv – HQ‑Save gesperrt."`
* Risiken: Ältere Testskripte für PvP müssen angepasst werden.

To-do

* Codex: Guard implementieren; HUD‑Toast „SaveGuard: Arena aktiv“.
* QA: PvP‑Flow: Arena starten → `!save` → erwartete Sperre.

Nächste Schritte

* Maintainer:innen: Runtime‑Stub & Docs synchronisieren.
* Notizen: Arena‑Audit in `logs.psi[]` (Policy) beibehalten. 

ISSUE #4

* Beobachtung: **Foreshadow‑Gate‑Badge** Terminologie uneinheitlich („Foreshadow 0/2“ vs. „GATE 0/2“) und paralleler FS‑Zähler in‑Mission („FS 0/4“).
* Diagnose: UI‑Labels uneindeutig; verwechselt Gate‑Erfüllung (2/2) mit Missions‑Foreshadows (0/4). Risiko für QA‑Fehlablesungen.  
* Evidenz (Acceptance Nr. 11–12): HUD‑Toast „Boss blockiert – **Foreshadow 0/2**“ vor M5; Toolkit fordert **GATE n/2** **und** in M5 den separaten Zähler **FS 0/4**.  

Lösungsvorschlag

* Ansatz: Einheitlich **GATE x/2** für das Vorab‑Gate; **FS x/4** nur in der Mission. Toast‑Text harmonisieren.
* Risiken: UI‑Strings müssen in Logs/Badges konsistent umgestellt werden.

To-do

* Codex: `scene_overlay()` → Badge‑Label fixieren; `!boss status` Klartext „Gate erfüllt: x/2 · Mission FS: y/4“.
* QA: Mission 4→5: prüfen, dass Gate‑Badge **GATE 2/2** und in M5 **FS 0/4** separat erscheinen (Acceptance 11–12). 

Nächste Schritte

* Maintainer:innen: String‑Table aktualisieren.
* Notizen: Debrief‑Export soll beide Zähler getrennt führen.

ISSUE #5

* Beobachtung: **Paradoxon‑Reset‑Timing** bei `ClusterCreate()` ist widersprüchlich (sofort vs. „erst nach einer Runde“).
* Diagnose: Kampagnenstruktur erlaubt dramaturgischen „one‑round delay“, Save/Runtime‑Text spricht vom sofortigen Reset.  
* Evidenz: „Reset greift erst nach einer Runde…“ in Kampagnenstruktur; „setzt Px=0 zurück“ ohne Verzögerung in Modul 12.  

Lösungsvorschlag

* Ansatz: Einheitlich definieren: **Reset am Missionsende**, HUD‑Hinweis in Szene danach. Pseudocode mit Delay‑Flag dokumentieren.
* Risiken: Minimal verändertes Timing kann selten Foreshadow/Heat‑Interaktionen beeinflussen.

To-do

* Codex: `ClusterCreate()` → `px_reset_deferred=true` bis `EndMission()`.
* QA: Mission mit Px 5 → prüfen, dass Reset erst im Debrief/HQ sichtbar wird.

Nächste Schritte

* Maintainer:innen: Docs/Pseudocode angleichen.
* Notizen: HUD‑Toast „Px‑Reset nach Szene abgeschlossen“ hinzufügen.

ISSUE #6

* Beobachtung: **Boss‑DR‑HUD‑Toast** ist in der Kampagnenstruktur gefordert, im Toolkit nicht als Pflicht‑Overlay verankert.
* Diagnose: Risiko, dass DR‑Dämpfer nicht sichtbar ist; Exploding‑Overflow wird dann inkonsistent gehandhabt.  
* Evidenz: Kampagnenstruktur: „Boss‑DR aktiviert – −X Schaden pro Treffer“; Toolkit definiert DR‑Variablen, aber keinen obligatorischen Toast beim Spawn.  

Lösungsvorschlag

* Ansatz: `generate_boss()` zwingend `hud_tag("Boss‑DR aktiviert – −{X} Schaden pro Treffer")`.
* Risiken: Keine.

To-do

* Codex: Boss‑Spawn Hook ergänzen.
* QA: M5/M10 und Rift‑Sz.10 → Toast erscheint; Schaden reduziert.

Nächste Schritte

* Maintainer:innen: Toolkit aktualisieren.
* Notizen: DR‑Wert in `campaign.boss_dr` für Debrief loggen.

ISSUE #7

* Beobachtung: **Mission‑5 Badge‑Check** – Reset von **SF‑OFF → SF‑ON** nach Abschluss **oder Abbruch** ist beschrieben, aber nicht eindeutig an einen End‑Hook gebunden.
* Diagnose: Unklare Implementationsstelle; Gefahr, dass bei „aborted“ kein Auto‑Reset erfolgt. (Acceptance Nr. 12)  
* Evidenz: Toolkit nennt `set_self_reflection(true)`/`logs.flags.last_mission_end_reason`, jedoch ohne verbindlichen End‑Trigger‑Pfad. Acceptance fordert Reset in beiden Fällen.  

Lösungsvorschlag

* Ansatz: `EndMission()` immer `set_self_reflection(true)` aufrufen, `last_mission_end_reason` (`completed|aborted`) setzen; HUD‑Toast `SF‑ON (post‑M5 reset)` protokollieren.
* Risiken: Keine.

To-do

* Codex: End‑Hook fixieren; Log‑Eintrag ergänzen.
* QA: Zwei Läufe M5 – einmal normal beenden, einmal früh abbrechen. Erwartet: in beiden Fällen SF‑ON + Logauszug im Debrief (Acceptance 12). 

Nächste Schritte

* Maintainer:innen: Merge & Release‑Note.
* Notizen: Add Testfall in Dispatcher‑Suite.

ISSUE #8

* Beobachtung: **Solo→Koop/PvP Cross‑Mode** ist funktional beschrieben (Wallet‑Init, Arena‑Spiegel), aber es fehlen **konkrete Import‑Beispiele** im Doc‑Fluss.
* Diagnose: Integrationsrisiko für Teams; Unklar, wann Wallet‑Init passiert und wie `mode_previous`/`policy_players[]` in Logs/`logs.psi[]` dokumentiert werden. 
* Evidenz: Koop‑Debrief & Wallet‑Split spezifiziert (inkl. Solo→Koop‑Umstieg), Arena‑Status dokumentiert – kein durchgehendes Beispiel „Solo‑Save importieren → Koop → Arena laden“. 

Lösungsvorschlag

* Ansatz: Schritt‑für‑Schritt‑Beispiel mit JSON‑Diffs im Modul 12 (Solo‑Save → Koop‑Wallets → Arena‑Session).
* Risiken: Keine.

To-do

* Codex: Beispiel‑Sektion „Cross‑Mode Import“ ergänzen.
* QA: Smoke‑Pfad: Solo‑Save laden → Koop‑Mission Debrief (Wallet‑Init) → Arena starten; Logs prüfen.

Nächste Schritte

* Maintainer:innen: Docs erweitern.
* Notizen: `logs.psi[]` Eintrag `mode_previous` sichtbar machen.

ISSUE #9

* Beobachtung: **Ökonomie‑Widerspruch** zwischen Generator‑Modul und CU‑System (Basisprämie).
* Diagnose: Modul 8A nennt Mission‑Economy 300/500/600 (Teil/Erfolg/Bonus), Modul 15 nennt Risiko‑Basen 400/500/600 (Low/Mid/High). Metrik widerspricht sich.  
* Evidenz: „Mission Economy“ Tabelle (300/500/600) vs. „Core‑Ops Belohnungen“ (Low 400/Mid 500/High 600).  

Lösungsvorschlag

* Ansatz: Einheitliche Formel definieren (z. B. Risiko‑Basis × Erfolgs‑Multiplikator) und in beiden Modulen spiegeln; HUD‑Rechner anzeigen.
* Risiken: Balance‑Shift erforderlich.

To-do

* Codex: CU‑Berechnung zentralisieren; `EndMission(outcome)` nutzt eine Quelle.
* QA: Drei Missionsfälle (Low/Teil, Mid/Erfolg, High/Bonus) rechnen und mit Tooltips vergleichen.

Nächste Schritte

* Maintainer:innen: Module 8A/15 harmonisieren.
* Notizen: README‑Quickref anpassen. 

ISSUE #10

* Beobachtung: **Acceptance‑Dispatcher Nr. 11–12** nennen „Boss blockiert – **Foreshadow 0/2**“, Toolkit beschreibt zusätzlich „**GATE n/2**“‑Badge – Dopplung kann Verwirrung erzeugen.
* Diagnose: Zwei Oberflächenanzeigen für das gleiche Gate. (Acceptance Nr. 11–12)  
* Evidenz: Acceptance‑Text (Foreshadow 0/2‑Toast) vs. Toolkit (GATE‑Badge Pflicht + FS‑Zähler).  

Lösungsvorschlag

* Ansatz: Nur **eine** Gate‑Anzeige aktiv (Badge), Toast optional beim ersten Gate‑Treffer.
* Risiken: UI‑Gewohnheiten der Tester ändern sich leicht.

To-do

* Codex: Gate‑Toast auf „first‑seen“ begrenzen; Badge bleibt persistent.
* QA: M4→M5: nur Badge persistent; einmaliger Gate‑Toast.

Nächste Schritte

* Maintainer:innen: UI‑Spezifikation konsolidieren.
* Notizen: Screenshots im QA‑Fahrplan ersetzen.

ISSUE #11

* Beobachtung: **Funk/Comms Reichweite & Hardwarepflicht** sind in mehreren Modulen beschrieben; es fehlt ein zentraler „Comms‑Check“ Verhaltensblock im Regeltext (nur Toolkit‑Makro referenziert).
* Diagnose: Regelreferenz verteilt (HUD/Comms‑Spec, CU‑Standardloadout, Toolkit‑Hinweise). Ein kompakter, normativer Abschnitt reduziert Rückfragen.  
* Evidenz: Toolkit „Funk & Signale“ (Comlink ≈ 2 km; **Hardwarepflicht**) vs. Loadout in Modul 15 – kein einheitlicher Regelblock in Core‑Sektion.  

Lösungsvorschlag

* Ansatz: Kurzes **„Comms‑Core“** Kapitel im Core/README verankern; Toolkit referenziert dorthin.
* Risiken: Keine.

To-do

* Codex: Comms‑Check‑Regeltext extrahieren, in README/Core verlinken.
* QA: Missions‑Log: Jammer‑Fall → `!offline` protokolliert, Hardware‑Workaround gefordert (Acceptance‑Stil).

Nächste Schritte

* Maintainer:innen: Docs restrukturieren.
* Notizen: „signal_space=false“ als sichtbares Flag im Regelkern erwähnen. 

ISSUE #12

* Beobachtung: **Foreshadow‑Mirror‑Pflicht** verlangt persistentes `logs.foreshadow[]`; Save‑Beispiel/Guard‑Liste unterschlägt dieses Feld (siehe Issue #1/#2), wodurch Acceptance Nr. 11 („Foreshadow‑Gate sichtbar“) gefährdet ist.
* Diagnose: Ohne garantierte Persistenz droht Inkonsistenz von Gate‑Zählern zwischen Sitzungen.  
* Evidenz: Toolkit schreibt Mirror‑Pflicht (Dedupe, First/Last‑Seen), Save‑Pseudocode listet Feld nicht; Beispiel‑JSON ebenso nicht.  

Lösungsvorschlag

* Ansatz: `logs.foreshadow[]` als Pflicht (siehe Issue #1/#2) und `!boss status` auf diese Quelle binden.
* Risiken: Keine.

To-do

* Codex: Serializer & Beispiel anpassen; Ladepfad dedupliziert Tokens.
* QA: Laden/Speichern – Gate‑Zähler bleibt stabil, „GATE x/2“ korrekt.

Nächste Schritte

* Maintainer:innen: Merge mit Pflichtfeld‑Fix.
* Notizen: QA‑Evidenz im HUD/Log‑Auszug sichern.

ISSUE #13

* Beobachtung: **Acceptance‑Nr. 14–15 (Accessibility/UI‑Persistenz)** – Felder existieren (`contrast`, `badge_density`, `output_pace`), aber es fehlt ein kompaktes „UI‑Preset“ Beispiel im Save‑Kapitel.
* Diagnose: Bedienhinweis verteilt zwischen README und Save‑Modul; Integrator:innen wünschen einen vollständigen Save‑Schnipsel mit aktivem High‑Contrast & Dense‑Badges.  
* Evidenz: Acceptance beschreibt den Ablauf; Beispiel‑Save zeigt Standard‑UI.  

Lösungsvorschlag

* Ansatz: Zweites Beispiel‑JSON „Accessibility‑Preset“ ins Save‑Kapitel.
* Risiken: Keine.

To-do

* Codex: Muster‑Save mit `ui{contrast:"high",badge_density:"dense",output_pace:"slow"}` bereitstellen.
* QA: `!accessibility` öffnen → Werte persistiert (Acceptance 14–15).

Nächste Schritte

* Maintainer:innen: Docs ergänzen; Screens aktualisieren.
* Notizen: Dispatcher‑Smoke zeigt nun beide Wege (Default/Preset).
```

