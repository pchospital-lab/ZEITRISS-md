---
title: "Beta-GPT Lauf 2025-07-05 – Rohprotokoll"
version: 1.0.0
tags: [meta, qa-log]
---

# Beta-GPT Lauf 2025-07-05 – Rohprotokoll

Dieses Dokument archiviert den vollständigen Beta-GPT-Testprompt samt Befundliste.
Ergänzende Auswertung und Maßnahmen stehen im [Beta-QA-Log 2025](2025-beta-qa-log.md).

```text
ISSUE #1

* Beobachtung: Save-Schema drifts – Beispiel-JSON nutzt `save_version: 6`,
  Serializer/Migrationscode und Kurzschema führen `save_version: 5`.
* Diagnose: Unsauberer Versionsstand in `speicher-fortsetzung.md` zwischen Beispiel-Block (v6) und
  `select_state_for_save()`/Migration (v5).
* Evidenz: Beispiel-DeepSave zeigt `save_version: 6` (HQ-only-Block) ; `select_state_for_save()`
  setzt hart `save_version: 5` und die Migration endet bei 5.

Lösungsvorschlag

* Ansatz: Einheitlich auf `save_version: 6` heben (Serializer, Migrationsziel, Kurzschema).
  Kurzschema/Codebeispiel synchronisieren.
* Risiken: Inkompatibilität alter QA-Snippets; ggf. einmalige Migration `5→6`.

To-do

* Codex: Serializer auf v6 setzen; `migrate_save()` um Schritt `5→6` ergänzen (keine
  Strukturänderung, nur Meta-Bump).
* QA: Lade-/Speicherlauf mit v5→v6-Migration; Smoke-Case 7/8 erneut prüfen (Load ohne
  Einstiegsauswahl, Save-Blocker im Feld).

Nächste Schritte

* Maintainer:innen: Wissensbasis & Runtime-Skripte in einem Commit angleichen; PR mit QA-Log
  verlinken.
* Notizen: Cross-Mode-Tests mit gemischten Saves (Solo/Koop) ebenfalls gegen v6 fahren.

ISSUE #2

* Beobachtung: Foreshadow-Zähler uneinheitlich (Gate 2/2 vs. Gesamtsoll 4 für Core);
  HUD-/Statusreferenzen widersprechen sich.
* Diagnose: Toolkit spiegelt „Foreshadow n/m (Core=4, Rift=2)“ als Gesamtziel,
  während Boss-Gates pro Mission 2/2 verlangen (M5 & M10).
* Evidenz: Boss-Foreshadow-Checklist: je 2 Hinweise vor M5 und M9/M10. ; Toolkit-Mirror beschreibt
  Core=4 insgesamt.

Lösungsvorschlag

* Ansatz: Anzeige klar trennen: `Foreshadow Gate 2/2 (diese Mission)` + optional
  `Season Total 2/4`. `!boss status` soll beide Werte ausgeben.
* Risiken: UI-String-Änderung; bestehende QA-Referenzen (FS 0/2) müssen angepasst bleiben.

To-do

* Codex: `!boss status` erweitern (Gate- und Staffelzähler getrennt);
  HUD-Badge „FS x/2 · Total y/4“ in Precision.
* QA: Acceptance 11/12 neu screenshotten (Gate bleibt 2/2, Total optional).

Nächste Schritte

* Maintainer:innen: README/Toolkit-Text konsolidieren (Gate vs. Total).
* Notizen: Kein Regelwandel – nur Darstellung/Statusausgabe.

ISSUE #3

* Beobachtung: Referenzierte Befehle/Makros ohne formale Definition
  (`scene_overlay()`, teils `!boss status`-Ablauf).
* Diagnose: Toolkit/README verweisen auf `scene_overlay()` zur
  Foreshadow-Rücksetzung nach StartMission; definierte Makro-Signatur fehlt im
  Modul.
* Evidenz: QA-Checks 2025‑06‑27 nennen `scene_overlay()` und `!boss status`
  Reset-Beleg, ohne Makro-Blöcke.

Lösungsvorschlag

* Ansatz: `scene_overlay(total, pressure, env)` öffentlich in Toolkit
  dokumentieren (Inputs/Outputs); `!boss status`-Output spezifizieren (Gate,
  Total, letzte Tokens).
* Risiken: Minimal; nur Doku/Signatur-Sync.

To-do

* Codex: Makro-Header & Rückgabewerte in Modul 16 sichtbar machen;
  `!boss status` Help-Text in README ergänzen.
* QA: Mission‑Start protokollieren: vor/nach `StartMission()` HUD-Log +
  `!boss status` Reset „FS 0/2“.

Nächste Schritte

* Maintainer:innen: Doku-PR (Toolkit + README) bündeln.
* Notizen: Linter-Tag für FS‑Reset hinzufügen (z. B. `LINT:FS_RESET_OK`).

ISSUE #4

* Beobachtung: Mission‑5‑Badge‑Check fordert `SF-OFF`-Badge beim Start, Auto-Umschalten nicht
  spezifiziert.
* Diagnose: Schnellstart sieht `!sf off` als manuellen Toggle vor; Acceptance 12 verlangt
  Sichtbarkeit von `SF-OFF` beim Start von M5 ohne klaren Precondition-Hinweis.
* Evidenz: „Mission 5 starten → … Badge `SF-OFF` …“ (Acceptance 12) ; `SF-OFF`-Mechanik via `!sf
  off` beschrieben, kein Auto-Flag in StartMission.

Lösungsvorschlag

* Ansatz: Acceptance präzisieren („Vor M5 `!sf off` setzen“) **oder**
  StartMission(M5) temporär `self_reflection=false` setzen und nach Debrief
  resetten.
* Risiken: Auto-Umschalten könnte Stilpräferenzen verletzen; daher bevorzugt Testtext anpassen.

To-do

* Codex: `!sf` Helptext + Acceptance-Notiz im README verlinken (Badge-Check Precondition).
* QA: Badge-Reset auf `SF-ON` nach Abbruch/Abschluss explizit loggen
  (HUD-Auszug). (Mission‑5‑Check)

Nächste Schritte

* Maintainer:innen: QA-Fahrplan-/README-Formulierung synchen.
* Notizen: Badge-Reset im HUD-Counter (Toast) beibehalten.

ISSUE #5

* Beobachtung: Arena-PvP Einstieg (`arenaStart(options)`) wird gefordert, Makro/Doku nicht
  vollständig enthalten; Kosten-Toast hängt an `phase_strike_cost()`.
* Diagnose: README/Toolkit referenzieren `arenaStart()` inkl.
  `phase_strike_tax = 1` und Arena-Toast bei `phase_strike_cost()`, aber
  `arenaStart`-Definition fehlt; Kosten- und Schutzklauseln stehen unter Psi
  (Phase-Strike).
* Evidenz: Acceptance pos. 15 → Arena-Toast über `phase_strike_cost()`; kein expliziter
  `arenaStart`-Makro-Block.

Lösungsvorschlag

* Ansatz: `arenaStart(options)` im Toolkit definieren (Flags setzen,
  Save-Blocker aktivieren, Snapshot/Restore nutzen, PvP-Modus an).
  `apply_arena_rules()`/`phase_strike_tax` aus Psi-Modul verlinken.
* Risiken: Schnittstellenklarheit mit Save-Guard (HQ-only) sicherstellen.

To-do

* Codex: Arena-Makro implementieren; HUD-Toast „Arena: Phase‑Strike …“ als
  verifizierbares Event loggen (`logs.psi[]`).
* QA: PvP-Smoke (pos. 15) mit HUD-/Log-Belegen fahren.

Nächste Schritte

* Maintainer:innen: Toolkit-PR (Arena-API + Save-Guard-Hook).
* Notizen: Arena-`save_guard()` bereits vorbereitet (Speichern blockiert).

ISSUE #6

* Beobachtung: `comms_check(device, range)` ist Pflichtreferenz, jedoch ohne zentrale
  Funktionsspezifikation.
* Diagnose: README fordert `comms_check` (Funk/Jammer/Relais); Toolkit verweist nur per Text, keine
  klaren Parameter/Effekte definiert.
* Evidenz: Kurzreferenz & Helper `!helper comms` in README, aber keine formale Schnittstelle
  (Input/Return/Errors).

Lösungsvorschlag

* Ansatz: Minimalspezifikation (required args, Std-Outputs, HUD-Pings bei
  Jammer/Relais/Range); ASCII/Unicode-Hinweise integrieren.
* Risiken: Keiner – Dokuergänzung.

To-do

* Codex: `comms_check()`-Spec (device, range_m, jammed, relays) + HUD-Vokab
  verlinken.
* QA: Offline-Hinweise/`!offline`-Flow gegen `offline_help()` prüfen.

Nächste Schritte

* Maintainer:innen: README+Toolkit konsolidieren; HUD-Vokabeln referenzieren.
* Notizen: Accessibility: `ascii_only`-Fallback in HUD-Menü ist vorhanden.

ISSUE #7

* Beobachtung: Doppelstruktur für Gruppen im Save (`team.members[]` und `party.characters[]`) führt
  zu Mehrdeutigkeiten.
* Diagnose: Beispiel-Save führt beide Felder; Kurzschema sagt „Gruppen-Save analog mit
  `party.characters[]`, kein zweites Schema“.
* Evidenz: Sample enthält `team` **und** `party`, wodurch Merge-Regeln/Wallets nicht eindeutig
  gebunden sind.

Lösungsvorschlag

* Ansatz: Kanonisch `party.characters[]` für spielende Agent:innen; `team` nur
  für NSC-Zelle/Flavor (optional). Serializer-Dedupe-Regel: `party` → primär,
  `team.members` → ignorieren oder in `party` migrieren.
* Risiken: Altsaves mit `team`-Zählung; Migration nötig.

To-do

* Codex: `migrate_save()` erweitert: `team.members → party.characters` (bei leeren `party`).
* QA: Cross-Mode-Save-Import (Solo→Koop, Koop→PvP) einmal mit Altsave (`team`)
  testen; Wallet-Split & HUD prüfen.

Nächste Schritte

* Maintainer:innen: Schemahinweis in README/Speicher-Modul präzisieren.
* Notizen: Wallets referenzieren `party.characters[].id` – validieren.

ISSUE #8

* Beobachtung: Doppelte Dokumentationszeile zu `logs.fr_interventions[]`.
* Diagnose: Copy‑Paste in Speicher-Modul erzeugt Redundanz (zwei identische Bullets).
* Evidenz: Abschnitt listet `logs.fr_interventions[]` zweimal hintereinander.

Lösungsvorschlag

* Ansatz: Duplikat entfernen; einen konsistenten Eintrag mit Dashboard-Verweis `!dashboard status`.
* Risiken: Keine.

To-do

* Codex: Doku bereinigen.
* QA: N/A.

Nächste Schritte

* Maintainer:innen: Minor edit mergen.
* Notizen: Arc-Dashboard-Snapshot bleibt QA‑Evidenz.

ISSUE #9

* Beobachtung: Acceptance 12 verknüpft Mini‑Boss‑DR‑Hinweis („Boss‑Encounter in Szene 10“) und `SF-
  OFF`-Badge, ohne Reihenfolge/Abhängigkeiten zu präzisieren.
* Diagnose: Toolkit erzeugt Boss-DR-HUD-Tag für Core (Szene 10) beim Gate, aber Badge-Logik
  (Self‑Reflection) ist unabhängig.
* Evidenz: HUD‑Tag „Boss-Encounter in Szene 10 (Core M{mission_in_episode})“ wird gesetzt; `SF-OFF`
  kommt aus separatem Toggle.

Lösungsvorschlag

* Ansatz: Acceptance um explizite Reihenfolge ergänzen: (1) Gate erfüllt (2/2), (2) optional `!sf
  off`, (3) Mission 5 Start → HUD-Tag + Badge sichtbar.
* Risiken: Dokumentationsänderung.

To-do

* Codex: Boss-Toast & Badge-Sektion in README präzisieren (Voraussetzungen).
* QA: Mission‑5‑Badge‑Check mit HUD-/Log‑Auszug neu belegen.

Nächste Schritte

* Maintainer:innen: README‑Acceptance-Block updaten.
* Notizen: Keine Engine-Änderung nötig.

ISSUE #10

* Beobachtung: Cross‑Mode‑Saves: Koop‑Wallets (`economy.wallets{}`) dokumentiert,
  aber kein klarer Importpfad von Solo‑Saves (ohne Wallets) in Koop‑Runs.
* Diagnose: Wallet-Persistenz/Binding an `party.characters[].id`
  beschrieben; Autoload/Merge kann Solo→Koop, aber Wallet-Init (Default) nicht
  explizit genannt.
* Evidenz: Wallet-Mechanik + Debrief-Formate vorhanden; Merge-Regeln
  definieren ID-basiertes Zusammenführen, aber kein „Wallet seeden bei
  Erstimport“.

Lösungsvorschlag

* Ansatz: Beim Gruppen‑Merge: fehlende `economy.wallets{}` initialisieren (alle
  beteiligten `party.characters[].id` mit Balance 0). Debrief nach erster
  Koop‑Mission erzeugt Split‑Einträge.
* Risiken: Keine; nur Defaults.

To-do

* Codex: `migrate_save()` erweitert: wenn `party.characters[]` existiert und
  `economy.wallets` fehlt → leeres Wallet‑Mapping erzeugen.
* QA: Solo‑Save in Koop importieren → Mission spielen → Wallet‑Split & HQ‑Pool verifizieren.

Nächste Schritte

* Maintainer:innen: Dokuzeile in Speicher‑Modul ergänzen.
* Notizen: Debrief-Linien `Wallet-Split (n×)`/`HQ-Pool …` bereits spezifiziert.

ISSUE #11

* Beobachtung: Accessibility/Offline‑Hinweise vorhanden, aber Acceptance „Accessibility‑Dialoge“
  nicht als eigener Prüfpfad referenziert.
* Diagnose: HUD-Menü ASCII‑Fallback, Offline‑Protokoll, `!offline` und
  Suggest‑Fallback sind dokumentiert – Acceptance-Checkliste (1–15) erwähnt
  diese nicht; QA-Anker fehlt.
* Evidenz: `hud_menu()` ASCII, `offline_help()` erzeugt HUD‑Zeile/Protokoll, `!offline`-FAQ
  vorhanden.

Lösungsvorschlag

* Ansatz: Acceptance‑Smoke um zwei Punkte erweitern: (a) ASCII‑HUD‑Menü Render
  (settings.ascii_only), (b) Offline‑Dialog (Jammer an → `!offline` →
  Protokollzeile + Suggest‑Fallback‑Toast).
* Risiken: Keine.

To-do

* Codex: README „Abnahme‑Smoketest“ um Accessibility‑Checks ergänzen.
* QA: Evidenzblöcke (HUD‑ASCII‑Render, Offline‑Toast, Log‑Zeile
  „Offline-Protokoll (n×) …“).

Nächste Schritte

* Maintainer:innen: QA‑Fahrplan aktualisieren.
* Notizen: `Ask→Suggest`-Badge/Overlay ebenfalls als Accessibility‑Hilfsmodus referenzieren.

ISSUE #12

* Beobachtung: Mission‑Startfluss widerspricht teils den „Einstieg“-Hinweisen beim Laden (kein
  klassisch/schnell nach Load) vs. globalem Einstiegskapitel.
* Diagnose: Speicher‑Modul verlangt nach Load sofortigen Recap +
  StartMission ohne Einstiegsauswahl; README nennt allgemeine Startpfade inkl.
  Einstiegstypen – potenziell missverständlich.
* Evidenz: „Spiel laden + kompatibler Save → **kein** klassisch/schnell; Kodex‑Recap‑Overlay …“
  (Dispatcher 7) ; Speicher‑Modul bestätigt diesen Flow.

Lösungsvorschlag

* Ansatz: README beim „Spiel laden“-Abschnitt auf denselben Flow festnageln (kein
  Einstiegsauswahldialog); Verweis auf Modul 12.
* Risiken: Doku‑Konsistenz only.

To-do (abgeschlossen)

* README-Linkanker auf `speicher-fortsetzung` ergänzt; Dispatcher-Load-Flow bestätigt:
  `load_deep()` setzt HQ-Recap ohne EntryChoice (`skip_entry_choice=true`).
* QA: Dispatcher‑Punkt 7 erneut validiert – Syntax-Hinweis liefert einmalig
  `dispatch_hint` (channel `dispatcher`), Klammerpflicht-Fehlertext bleibt laut
  Runtime/README kanonisch.

Nächste Schritte

* Maintainer:innen: README-PR.
* Notizen: Keine Engine‑Änderung.

ISSUE #13

* Beobachtung: KPI/Badge‑Check Mission 5 „Foreshadow 2/2 → Start → FS 0/2“ verlangt eindeutige
  Reset-Bestätigung im Log; Log-Quelle (HUD vs. QA‑Log) nicht explizit.
* Diagnose: QA‑Check nennt „HUD‑Log notieren … `scene_overlay()` `FS 0/2` … QA‑Log führt Evidenz“.
  Quelle/Format-Zwang unscharf.
* Evidenz: QA-Block 2025‑06‑27 (Toolkit) spricht beide Logs an; README wiederholt die Checks
  allgemein.

Lösungsvorschlag

* Ansatz: Ein Satz in README: „Als Evidenz gilt die HUD‑Zeile im Missionslog (`logs.hud[]`) **und**
  der QA‑Auszug im Testjournal; beide referenzieren denselben Zeitstempel.“
* Risiken: None.

To-do

* Codex: `logs.hud[]`-Einschub für FS‑Reset schreiben; `!boss status` nach Start in `logs.hud[]`
  spiegeln.
* QA: Badge‑Check re‑run mit Doppelnachweis (HUD‑Trace+QA‑Log).

Nächste Schritte

* Maintainer:innen: Doku-/Logschema synchronisieren.
* Notizen: Einheitliche Tag‑Kennzeichnung `Foreshadow`/`FS-Reset` nutzen.

ISSUE #14

* Beobachtung: PvP/Arena speichert korrekt nicht (Save‑Guard), aber kein expliziter Hinweis im
  Dispatcher/Acceptance.
* Diagnose: Arena‑`save_guard()` blockiert Save; Acceptance nennt den Arena‑Toast, nicht aber den
  Save‑Blocker als UX‑Hinweis.
* Evidenz: `save_guard()` im Toolkit → `Speichern blockiert – Arena aktiv`.

Lösungsvorschlag

* Ansatz: Acceptance pos. 15 ergänzen: „Während Arena-Run erzeugt Kodex Toast
  ‚Speichern blockiert – Arena aktiv‘ bei Save‑Versuch.“
* Risiken: Keine.

To-do

* Codex: README‑Acceptance erweitern; `!save` in Arena als Testschritt listen.
* QA: Arena‑Run → `!save` → Toast verifizieren.

Nächste Schritte

* Maintainer:innen: README-Update.
* Notizen: HQ‑only bleibt unverändert.

ISSUE #15

* Beobachtung: City/Chronopolis‑Module: Warn‑Banner/Cache/Rotation dokumentiert; Acceptance‑Smoke
  (1–15) prüft City‑Flows nicht.
* Diagnose: City‑Flows (Warn‑Popup, Daily‑Stock, Rotation, Save‑Blocker in CITY) sind beschrieben,
  aber kein Minimal‑Acceptance (z. B. „CITY betretbar ab L10, Save blockiert, `!chrono stock`
  liefert Einträge“).
* Evidenz: City‑Doku inkl. Save‑Block, Daily‑Roll, UI‑Banner vorhanden.

Lösungsvorschlag

* Ansatz: Acceptance‑Smoke um City-Minimaltest erweitern (Warn‑Popup einmalig, `!chrono stock`,
  Save‑Blocker in CITY).
* Risiken: Keine.

To-do

* Codex: README „Abnahme‑Smoketest“ ergänzen (City‑Block).
* QA: Einmaliger Run mit Level‑Gate L10 → Betreten CITY → `!save` blockiert → `!chrono
  stock`/`!chrono tick` Evidenz.

Nächste Schritte

* Maintainer:innen: Task im QA‑Fahrplan hinzufügen.
* Notizen: Chronopolis‑Logs gehen in `logs.market[]`; Debrief fasst als `Chronopolis-Trace (n×)`
  zusammen.
```

