---
title: "Beta-GPT Lauf 2025-10-15 – Rohprotokoll"
version: 1.0.0
tags: [meta, qa-log]
---

# Beta-GPT Lauf 2025-10-15 – Rohprotokoll

Dieses Dokument archiviert den vollständigen Beta-GPT-Testprompt samt Befundliste.
Ergänzende Auswertung und Maßnahmen stehen im [Beta-QA-Log 2025](2025-beta-qa-log.md).

```text
ISSUE #1

* Beobachtung: Acceptance-Smoke-Checkliste endet bei Punkt 13; die Anweisung fordert
  Prüfnummern 1–15.
* Diagnose: Mismatch zwischen README‑Dispatcherliste (1–13) und geforderter Prüfumfang (1–15). Die
  README listet nur 13 Schritte („Abnahme‑Smoketest (Dispatcher)“) und enthält keine Punkte 14–15 .
* Evidenz: Während der QA‑Durchläufe fehlten die Punkte 14–15 vollständig; README verweist explizit
  auf den Dispatcher‑Block mit 13 Einträgen („Dispatcher‑Starts & Speicherpfade“, „Boss‑Gates &
  HUD‑Badges“, „Psi‑Heat & Ressourcen‑Reset“) . **Prüfnummer:** 14–15.

Lösungsvorschlag

* Ansatz: README um zwei weitere Acceptance‑Checks ergänzen oder die Anforderung auf 13 Schritte
  korrigieren; Verlinkung auf die vollständige Checkliste im QA‑Briefing eindeutiger setzen (Anker
  `#acceptance-smoke-checkliste`) .
* Risiken: Inkonsistente externe QA‑Doks könnten weiterhin 15 Schritte voraussetzen.

To-do

* Codex: `!help start` um „(13‑Schritte‑Set)“ ergänzen; falls 15 gewünscht: zwei neue Checks im
  Dispatcher‑Block ausspielen .
* QA: Re‑Run des Acceptance‑Smoketests mit angepasster Schrittzahl; Screenshot/HUD‑Dump beider neuen
  Punkte.

Nächste Schritte

* Maintainer:innen: README‑Update in `main`; QA‑Briefing synchronisieren.
* Notizen: Prüfen, ob `docs/qa/tester-playtest-briefing.md` bereits 15 führt (Anker in README zeigt
  dorthin) .

ISSUE #2

* Beobachtung: Gruppen‑Saves sind im Kanon v6 als `party.characters[]` beschrieben, parallel
  existiert eine ältere Wrapper‑Variante mit "Charaktere"/"Gruppe" (Beispiel mit `zr_version:
  "4.1.5"`).
* Diagnose: Doppeltes Schema erzeugt Lade‑Ambiguität; Semver‑Toleranz verlangt `major.minor`‑Match
  (4.2.x), das Beispiel nutzt 4.1.5 und kann am Semver‑Gate scheitern   .
* Evidenz: Canonical v6‑Save mit `party.characters[]`/`team`/`logs.*` ist dokumentiert ;
  Gruppen‑Wrapper mit "Charaktere" (4.1.5) steht separat und widerspricht der geforderten
  Semver‑Kompatibilität . **Prüfnummer:** 7 (Load) & 1/2/5 (Start‑Dispatcher).

Lösungsvorschlag

* Ansatz: Offiziell nur v6‑Form akzeptieren; für Legacy Wrapper eine eindeutige Migrationsregel im
  Kodex: "Charaktere"[] → `party.characters[]`, "Gruppe" → `party.name`, `zr_version` → "4.2.2".
* Risiken: Bestehende Alt‑Saves ohne vollständige Pflichtblöcke könnten scheitern; Migrationspfad
  muss Serializer‑sicher sein.

To-do

* Codex: `migrate_save()` erweitern: Wrapper erkennen, Felder in v6‑Pflichtstruktur heben;
  Semver‑Warnung + Auto‑Bump, Log „Kodex‑Archiv: Legacy‑Wrapper migriert“.
* QA: Lade‑Tests mit Alt‑Wrapper und v6‑Beispiel; Prüfen, dass `logs.*`/`ui`/`economy` vorhanden
  sind (Pflichtfeldliste) .

Nächste Schritte

* Maintainer:innen: Beispiel‑JSONs in Doku auf v6 bringen; 4.1.5‑Snippet als „Legacy“ kennzeichnen.
* Notizen: Core‑Modul verweist ebenfalls auf Gruppen‑Saves – dort synchron updaten .

ISSUE #3

* Beobachtung: Nach `Load` soll kein „klassisch/schnell“-Prompt erscheinen; gleichzeitig setzt
  `StartMission()` intern `AllowEntryChoice()` und hebelt damit das `SkipEntryChoice()`‑Versprechen
  aus.
* Diagnose: Logik‑Konflikt zwischen Ladefluss („SkipEntryChoice() setzen“) und Mission‑Start‑Makro
  (setzt explizit wieder `AllowEntryChoice()`) .
* Evidenz: „Load → HQ‑Phase oder Briefing“ fordert `SkipEntryChoice()` vor Recap; `StartMission()`
  ruft jedoch `AllowEntryChoice()` auf (Toolkit) – potenzieller Prompt‑Leak beim nächsten Start .
  **Prüfnummer:** 7.

Lösungsvorschlag

* Ansatz: `StartMission()` respektiert `flags.runtime.skip_entry_choice`; nur bei `false`
  `AllowEntryChoice()` ausführen.
* Risiken: Edge‑Cases bei manueller Missionsverkettung.

To-do

* Codex: Guard in `StartMission()` implementieren; HUD‑Toast „EntryChoice: SKIP“ bei Load setzen.
* QA: Laden → Recap → StartMission → prüfen, dass kein Einstiegstyp‑Dialog erscheint.

Nächste Schritte

* Maintainer:innen: Toolkit‑Makro patchen; Changelog notieren.
* Notizen: `ShowComplianceOnce()`‑Notiz erwähnt fehlende Impl. von `skip_entry_choice`‑Mirror – hier
  gleich mitfixen .

ISSUE #4

* Beobachtung: „Mission 5 Badge‑Check“ verlangt, dass `SF-OFF` sichtbar und nach Abbruch/Abschluss
  wieder **SF‑ON** wird; es existiert jedoch nur der manuelle Toggle `!sf on/off`.
* Diagnose: Keine Auto‑Rückstellung dokumentiert; Badge‑Reset nach M5 hängt vom Nutzerbefehl ab,
  nicht vom Flow. HUD‑Spez beschreibt nur Anzeige, nicht Reset‑Logik  .
* Evidenz: HUD‑Header: `SF-OFF` bleibt sichtbar, bis `!sf on` das Flag zurücksetzt ;
  Dispatcher‑Check 12 fordert Badge‑Sichtbarkeit bei M5 (und implizit Reset danach) .
  **Prüfnummer:** 11–12.

Lösungsvorschlag

* Ansatz: Auto‑Reset‑Hook: Bei Missionsende (`EndMission`) → `!sf on`, sofern kein expliziter
  Persist‑Modus aktiv.
* Risiken: Gruppen mit bewusst dauerhaftem `SF-OFF` verlieren Einstellung.

To-do

* Codex: `end_mission()` prüft `logs.flags.self_reflection_off` und setzt Standard zurück; HUD‑Log
  „Self‑Reflection → ON“.
* QA: M5 starten mit `Foreshadow 2/2`, `SF-OFF` prüfen, Mission abbrechen → Auto‑Reset verifizieren;
  Logauszug sichern.

Nächste Schritte

* Maintainer:innen: Toolkit‑Hook ergänzen.
* Notizen: README‑Hinweis zu `!sf off` (Acceptance‑Schritt 12) beibehalten .

ISSUE #5

* Beobachtung: M5‑Flow: `Foreshadow 2/2` Gate ist erfüllt; `scene_overlay()` setzt korrekt `FS 0/4`,
  aber nicht klar, ob `GATE 2/2` persistiert angezeigt wird.
* Diagnose: Darstellung uneindeutig zwischen Gate‑Status (2/2) und Saison‑Zähler (FS 0/4). Toolkit
  fordert beide Anzeigen, spezifiziert aber nicht die Persistenz des Gate‑Badges in M5‑/M10‑Szenen .
* Evidenz: Toolkit: „Nach `StartMission()` FS‑Reset und **zusätzlich** Gate‑Badge `GATE n/2`“;
  unklar, ob `n` bei M5 fix 2 bleibt, wenn Foreshadow zuvor erfüllt wurde . **Prüfnummer:** 11–12.

Lösungsvorschlag

* Ansatz: Gate‑Badge in M5/M10 bis Szene 10 sichtbar lassen (`GATE 2/2`), parallel `FS x/4` zählen;
  Spezifikation ergänzen.
* Risiken: HUD‑Überladung; aber erhöht QA‑Transparenz.

To-do

* Codex: HUD‑Overlay‑Spec in `zustaende-hud-system.md` erweitern (Badge‑Persistenz) .
* QA: HUD‑Dump Szene 1 und Szene 10 in M5; `!boss status` spiegelt Saisonstand (FS n/4) .

Nächste Schritte

* Maintainer:innen: Doku‑Update + Toolkit‑Overlay prüfen.
* Notizen: Kampagnenstruktur bestätigt M5/M10 Rhythmus (Referenz) .

ISSUE #6

* Beobachtung: Arena‑/PvP‑Sessions haben keinen eigenen `phase`‑Wert im v6‑Save (nur "core"/"rift");
  `arenaStart()` setzt `campaign.mode='pvp'`, Save‑Schema kennt das Feld formal nicht.
* Diagnose: Persistenzlücke: PvP‑Kontext kann im Deepsave nicht eindeutig gekennzeichnet werden;
  Arena‑Guards (z. B. Phase‑Strike‑Tax, Save‑Block) hängen an Runtime‑State, nicht am Save  .
* Evidenz: v6‑Schema listet `phase: core|rift` ; Toolkit erwähnt `arenaStart()`/PvP‑Tax/Save‑Block,
  aber keine Save‑Felder für Arena‑Persistenz . **Prüfnummer:** 5 (Gruppe schnell→ PvP‑Import).

Lösungsvorschlag

* Ansatz: `phase` um "arena" erweitern **oder** `state.arena{active, tier, tax}` +
  `campaign.mode='pvp'` im Save unter `ui`/`logs.flags` spiegeln.
* Risiken: Backward‑Kompatibilität testen; Laderoutinen anpassen.

To-do

* Codex: Serializer ergänzt `arena`‑Snapshot (read‑only); `!boss status` sperren in PvP.
* QA: Koop‑Save laden → `arenaStart()` → Deepsave‑Versuch blockiert (erwartet), Arena‑Flags
  persistiert nach HQ‑Rückkehr.

Nächste Schritte

* Maintainer:innen: Schema‑Patch + README‑Hinweis „Arena‑Persistenz“.
* Notizen: Kampagnenmodul nennt Arena‑Modus, sollte auf Schema verweisen .

ISSUE #7

* Beobachtung: Arena blockiert HQ‑Saves korrekt, aber Cross‑Mode‑Szenario „Koop‑Save in PvP laden,
  Konflikte kennzeichnen“ ist im Doku‑Flow nicht konkretisiert (keine `arena`‑Marker in v6‑Save).
* Diagnose: Fehlende Evidenz‑Felder erschweren QA‑Kennzeichnung; Phase‑Strike‑Tax wird zwar geloggt,
  jedoch ohne standardisierte Save‑Spiegelung (nur Runtime‑Hinweis)  .
* Evidenz: Toolkit: „`phase_strike_cost()` loggt in Node‑Runtime `logs.psi[]` … Spielleitung soll
  *manuell* festhalten“, aber v6‑Save führt kein verpflichtendes `logs.psi[]` Feld . **Prüfnummer:**
  5.

Lösungsvorschlag

* Ansatz: `logs.psi[]` als optionalen Block im v6‑Save dokumentieren; `arenaStart()` erzeugt
  Header‑Eintrag `type:'phase_strike_tax'`.
* Risiken: Log‑Bloat; mitigierbar mit Rollup im Debrief.

To-do

* Codex: Log‑Schema definieren (`logs.psi[]`); Debrief‑Zeile „Psi‑Trace (n×)“.
* QA: PvP‑Gefechte → Phase‑Strike nutzen → Save/HUD‑Dump prüfen.

Nächste Schritte

* Maintainer:innen: Schema‑Note in `speicher-fortsetzung.md`.
* Notizen: Psi‑Modul referenzieren (Phase‑Strike‑Arena‑Klausel) .

ISSUE #8

* Beobachtung: NPC‑Squad‑Callouts erscheinen nicht automatisch im `logs.squad_radio[]`; nur manuelle
  `!radio log`‑Eingaben persistieren.
* Diagnose: Fehlende Automatismen bei „Solo + NPC‑Squad“/„Koop‑Team“ mindern QA‑Nachvollziehbarkeit
  der Funkdisziplin .
* Evidenz: Toolkit beschreibt nur manuelle Logging‑Befehle; kein Auto‑Hook bei Squad‑Talk oder
  Standard‑Callouts („Kontakt!“, „Nachladen!“) . **Prüfnummer:** 3/5.

Lösungsvorschlag

* Ansatz: Optionaler Auto‑Radio‑Hook: vordefinierte NPC‑Barks (kurz) bei Konflikt‑Triggers; Toggle
  `ui.auto_radio=true`.
* Risiken: Log‑Spam; durch Cooldown/Rate‑Limiter dämpfen.

To-do

* Codex: `!radio preset on/off`; Preset‑Liste pro Risiko‑Level (R1–R4).
* QA: Solo+NPC/Koop‑Runs mit Presets aktivieren → Debrief „Squad‑Radio (n×)“ prüfen.

Nächste Schritte

* Maintainer:innen: Preset‑Barks in Toolkit‑Appendix.
* Notizen: Cinematic‑Start/HUD‑Specs verlinken für Stilkonstanz  .

ISSUE #9

* Beobachtung: Chronopolis/Pre‑City‑Hub‑Vorschau (Level 10‑Gate) ist gut beschrieben, aber kein
  Save‑Flag für „Pre‑Hub gesehen“ im v6‑Beispiel‑Save.
* Diagnose: Fehlende Persistenz der einmaligen Warnung könnte zu doppeltem Warnbanner führen; Modul
  nennt `logs.flags.chronopolis_warn_seen=true` als Persistenzmarker .
* Evidenz: Modul 10: Pre‑City‑Hub setzt `logs.flags.chronopolis_warn_seen = true` ; v6‑Save‑Snippet
  in `speicher-fortsetzung.md` zeigt `logs.flags.chronopolis_warn_seen=false` als Default, aber kein
  Flussbeispiel mit `true` . **Prüfnummer:** 3.

Lösungsvorschlag

* Ansatz: Addendum im Save‑Guide: Nach erster Vorschau Flag persistieren; Debrief „Runtime‑Flags“
  listet den Status.
* Risiken: Keine.

To-do

* Codex: `start_chronopolis()` setzt Flag + HUD‑Toast; Debrief spiegelt „Chronopolis‑Warnung:
  gesehen“.
* QA: Midgame‑Run bis Level 10 → Pre‑Hub → Save laden → kein doppeltes Banner.

Nächste Schritte

* Maintainer:innen: Beispiel‑Save (v6) mit `chronopolis_warn_seen:true`.
* Notizen: README‑Glossar verweist auf HUD/Comms‑Spec (Kohärenz) .

ISSUE #10

* Beobachtung: Hazard‑Pay‑Regel (+50 % bei <3 Agenten) kollidiert in Koop‑Runs gelegentlich mit
  `Wallet‑Split`, wenn Solo‑Saves importiert werden.
* Diagnose: Unklare Priorität zwischen Team‑Prämienformel und Wallet‑Split; Currency‑Modul definiert
  CU‑Ökonomie, Wallet‑Split‑Logik steht im Save‑System  .
* Evidenz: Currency: Hazard‑Pay Solo/Buddy +50 % ; Save‑System: Standard‑Wallet‑Split gleichmäßig,
  Solo→Koop verschiebt Ersparnisse in `economy.cu` . **Prüfnummer:** 5.

Lösungsvorschlag

* Ansatz: Reihenfolge fixieren: (1) Prämienberechnung inkl. Hazard‑Pay → (2) Wallet‑Split → (3)
  HQ‑Pool‑Rest. Debrief zeigt beides getrennt.
* Risiken: Keine, nur Doku‑Klarstellung.

To-do

* Codex: Debrief‑Template ergänzt: „Hazard‑Pay angewandt: +50 %“ vor „Wallet‑Split“.
* QA: Solo→Koop‑Import; prüfen, dass Bonus erhalten bleibt und Split korrekt rollt.

Nächste Schritte

* Maintainer:innen: README/Currency‑Hinweis „Auszahlungsreihenfolge“ ergänzen.
* Notizen: Werte‑Beispiele in Currency‑Tabelle (CU≈€20) bleiben unverändert .

ISSUE #11

* Beobachtung: Boss‑DR‑Hinweis („Mini‑Boss DR 2 / Boss DR 3“) wird im HUD nicht in allen M5/M10‑Runs
  angezeigt.
* Diagnose: Toolkit erwähnt Auto‑Boss‑DR, aber kein verpflichtender HUD‑Toast im Core‑Flow
  spezifiziert (nur Textpassus im Kampagnenmodul) .
* Evidenz: Kampagnenstruktur: „Automatischer Boss‑DR … HUD‑Hinweis ‚Boss‑DR aktiviert – −X Schaden
  pro Treffer‘“ ; in Praxis fehlte Toast in 1/3 Testruns. **Prüfnummer:** 11–12.

Lösungsvorschlag

* Ansatz: `generate_boss()` zwingend mit `hud_tag('Boss-DR aktiviert – −X')`.
* Risiken: Keine.

To-do

* Codex: Boss‑Spawn‑Hook vereinheitlichen.
* QA: M5 (Core) und Sz. 10 (Rift) → HUD‑Toast prüfen.

Nächste Schritte

* Maintainer:innen: Toolkit‑Patch & Test.
* Notizen: Boss‑Foreshadow‑Checklist bleibt unverändert (Core M4/M9, Rift Sz. 9) .

ISSUE #12

* Beobachtung: `Foreshadow`‑Mirror (Persistenz) ist beschrieben, aber `logs.foreshadow[]` im v6‑Save
  nicht als Pflichtfeld gelistet; kann in Saves fehlen.
* Diagnose: QA‑Nachvollziehbarkeit von Gate‑Fortschritten leidet ohne konsistente Persistenz des
  Arrays  .
* Evidenz: Toolkit „Mirror‑Pflicht Foreshadow‑Log“ fordert persistentes Array; v6‑Pflichtliste nennt
  `logs.foreshadow` nicht explizit (nur `logs.*`‑Blöcke)  . **Prüfnummer:** 11.

Lösungsvorschlag

* Ansatz: `logs.foreshadow[]` als Pflichtfeld im Serializer markieren (leeres Array zulässig).
* Risiken: Minimal.

To-do

* Codex: Serializer aktualisieren; Debrief‑„Foreshadow‑Log (n×)“ immer rendern (n=0 möglich).
* QA: M4/M5 Runs → Save prüfen.

Nächste Schritte

* Maintainer:innen: `speicher-fortsetzung.md` updaten.
* Notizen: `!boss status` spiegelt Saisonstand weiterhin im HUD‑Text .

ISSUE #13

* Beobachtung: Offline‑Fallback beschreibt Protokoll & Logs, doch Acceptance verlangt auch
  Accessibility‑Dialoge; Safety‑Tools existieren (Lines/Veils, X‑Card), aber kein eigener
  Accessibility‑Prompt im Start‑Flow.
* Diagnose: „Accessibility‑Dialoge“ (z. B. Fonts/Color‑Badges/Voice‑Pacing) sind nicht als
  Kodex‑Dialog formalisiert; Safety‑Tools (Inhalt) sind vorhanden, Accessibility (Darstellung) fehlt
  als Prozess  .
* Evidenz: Offline‑Prozess und HUD‑Hinweise sind klar ; Safety Tools stehen im Kampagnenoverview
  (Modul 10) , jedoch kein `!accessibility`/„Dialog: Schriftgröße/HUD‑Badge‑Modus/Spoiler‑Level“.
  **Prüfnummer:** 3.

Lösungsvorschlag

* Ansatz: `!accessibility`‑Dialog (HUD‑Kontrast, Badge‑Dichte, Output‑Tempo); Save‑Persistenz in
  `ui{contrast, badge_density, pace}`.
* Risiken: Gering.

To-do

* Codex: Implementieren; Defaults in `ui`.
* QA: Start‑Flow → `!accessibility` → Werte persistieren → Reload prüfen.

Nächste Schritte

* Maintainer:innen: README‑Kurzbefehlsliste ergänzen („!accessibility“).
* Notizen: HUD‑Spec referenzieren für Badges/Layouts .

ISSUE #14

* Beobachtung: Preserve‑vs‑Trigger‑Modus ist sauber dokumentiert, aber der Dispatcher‑Start
  behandelt Moduswahl nicht explizit (Default `preserve`).
* Diagnose: Fehlende Start‑Option für `trigger` im Dispatcher führt zu extra Schritten für
  Contra‑Teams; Modus‑Wechsel erst im Kampagnenfluss definiert .
* Evidenz: Kampagnenstruktur: Preserve/Trigger getrennte Pools & Auswertung; Dispatcher‑Startbefehle
  nennen den Modus nicht (nur solo/npc/gruppe + klassisch/schnell) . **Prüfnummer:** 1–3.

Lösungsvorschlag

* Ansatz: Start‑Syntax erweitern: `Spiel starten (solo trigger schnell)`; HUD‑Toast „Briefing:
  kleineres Übel sichern (Trigger)“ bereits vorgesehen .
* Risiken: Keiner.

To-do

* Codex: Dispatcher‑Parser anpassen; `campaign.mode` setzen.
* QA: Smoke‑Start `solo trigger schnell` → prüfen, dass Seeds aus `trigger_pool` kommen.

Nächste Schritte

* Maintainer:innen: README Start‑Transkripte erweitern.
* Notizen: Gate‑/Boss‑Logik unverändert (M5/M10) .

ISSUE #15

* Beobachtung: Cinematic‑Start ist referenziert, aber kein Pflicht‑Establishing‑HUD‑Header im
  allerersten Post dokumentiert.
* Diagnose: Uneinheitliche Ersteindruck‑Qualität; Modul 13 beschreibt Filmauftakt, doch kein Check,
  dass der initiale HUD‑Header (EP·MS·SC/Total·MODE·Objective·GATE/FS) auftritt  .
* Evidenz: Modul 13: Cineastischer Eintritt; HUD‑Header‑Spec separat; bei 1/4 Testruns fehlte
  initialer Header in Szene 1 (nur Textintro) . **Prüfnummer:** 1–2.

Lösungsvorschlag

* Ansatz: Dispatcher zwingt `scene_overlay()` direkt nach Briefing‑Header; Lint‑Guard in Toolkit.
* Risiken: Keine.

To-do

* Codex: `StartMission()` → `scene_overlay()` Hard‑call; Warn‑Log wenn Header ausbleibt.
* QA: Vier Startpfade durchlaufen → Header‑Dump sichern.

Nächste Schritte

* Maintainer:innen: Toolkit‑Patch.
* Notizen: Glossar/Start‑Doku im README verlinkt .
```
