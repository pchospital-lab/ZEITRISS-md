---
title: "Beta-GPT Lauf 2025-07-18 – Rohprotokoll"
version: 1.0.0
tags: [meta, qa-log]
---

# Beta-GPT Lauf 2025-07-18 – Rohprotokoll

Dieses Dokument archiviert den vollständigen Beta-GPT-Testprompt samt Befundliste.
Ergänzende Auswertung und Maßnahmen stehen im [Beta-QA-Log 2025](2025-beta-qa-log.md).

```text
ISSUE #1

* Beobachtung: HQ-Deepsave nach Exfil scheitert sporadisch mit Guard-Fehler
  „Speichern nur im HQ …“, obwohl das Team bereits im HQ ist.
* Diagnose: `campaign.exfil.active` wird im Rücksprung-Flow nicht zuverlässig
  auf `false` gesetzt; SaveGuard erwartet `exfil_active == false`. In
  `transfer_back_to_hq()` fehlt ein explizites Zurücksetzen, erst der `HQ`-Zweig
  von `NextScene()` räumt sauber auf – das ist nicht garantiert Teil jedes
  Flows.
* Evidenz: Repro über Dispatcher (Acceptance 7–8): `Spiel laden` → Mission
  beenden → Exfil → **sofort Save** im Rückkehrframe auslösen → Guard feuert; erst
  nach zusätzlichem `NextScene("HQ")` gelingt `!save`. HQ-only-Restriktion &
  Pflichtwerte laut Save‑v6 Schema.

Lösungsvorschlag

* Ansatz: In `transfer_back_to_hq()` direkt `campaign.exfil.active=false`
  setzen, bevor der HQ‑Cut erfolgt; zusätzlich Guard im Save-Serializer auf
  `campaign.exfil.active` prüfen statt generischem `state.timer`.
* Risiken: Race‑Conditions bei Hot‑Exfil; Regression bei RW‑HUD‑Anzeige während des Cuts.

To-do

* Codex: Patch `transfer_back_to_hq()` um `exfil.active=false` + Toast `RW geschlossen`.
* QA: Wiederholung Acceptance 8 (Speichern während/kurz nach Mission) auf drei
  Pfaden (normaler Exfil, Hot‑Exfil, Abbruch) und Logvergleich.

Nächste Schritte

* Maintainer:innen: Runtime-Mirror im Wissensspeicher aktualisieren (Toolkit & Save‑Modul),
  anschließend Smoketest exportieren.
* Notizen: Prüfen, ob `exfil.ttl`/`armed` ebenfalls hart zurückgesetzt werden müssen, um HUD‑Ghosts
  zu vermeiden.

ISSUE #2

* Beobachtung: Mission‑5‑Badge‑Check scheitert: HUD zeigt nach Start von M5 `FS 0/4` statt
  erwartetem `Foreshadow 2/2`; Mini‑Boss‑Gate wirkt uneindeutig.
* Diagnose: `scene_overlay()` setzt nach `StartMission()` den FS‑Zähler hart auf `FS 0/4`.
  Saisonstand wird zwar via `!boss status` korrekt geführt, aber das on‑screen Badge verliert die
  vorab erfüllten 2/2‑Gates für M5.
* Evidenz: Acceptance Mission‑5‑Check: Vorbereitete `ForeshadowHint()`×2 → Start M5 → Overlay zeigt
  `FS 0/4`, während `!boss status` den Saisonstand korrekt meldet. Erwartung laut
  Dispatcher‑Hinweis: HUD zeigt `FS 0/4` **und** Badge‑Gate‑Bestätigung; derzeit keine klare
  Verknüpfung.

Lösungsvorschlag

* Ansatz: Overlay um zweiten, gatebezogenen Zähler ergänzen (`Gate 2/2 · FS 0/4`), der die
  Boss‑Freigabe unabhängig vom Szene‑FS‑Reset spiegelt.
* Risiken: HUD‑Dichte/Zeilenumbruch; Verwechslung Gate vs. Saisonstand.

To-do

* Codex: `scene_overlay()` erweitert rendern: Saison‑FS (n/4) **+** Gate‑FS (2/2) bei M5/10.
* QA: Acceptance „Foreshadow 2/2 → Start M5“ erneut ausführen und HUD‑Screenshot in Evidenzlog
  ablegen.

Nächste Schritte

* Maintainer:innen: HUD‑Spezifikation in `zustaende-hud-system.md`
  referenzieren; README‑Hinweis „Boss‑Gates & HUD‑Badges“ aktualisieren.
* Notizen: Boss‑Auto‑Foreshadows in Szene 4/9 prüfen (Auto‑Hints im Toolkit).

ISSUE #3

* Beobachtung: `SF-OFF`‑Badge wird in Mission 5 nicht konsistent angezeigt, obwohl `!sf off` vor
  Start gesetzt wurde.
* Diagnose: Abhängigkeit „Badge nur sichtbar, wenn Self‑Reflection vorher per
  `!sf off` deaktiviert“ ist dokumentiert, aber es fehlt ein persistenter
  Flag‑Mirror (Save/State), den `scene_overlay()` sicher lesen kann.
* Evidenz: Acceptance 12: `!sf off` vor M5 → Start M5 → Badge fehlt in ~30 %
  der Testruns (abhängig vom Einstiegspfad/Recap). README nennt Badge als
  Pflichtanzeige für M5.

Lösungsvorschlag

* Ansatz: `!sf on/off` als bool in `logs.flags.self_reflection` persistieren;
  `scene_overlay()` prüft diesen statt volatil‑runtime‑Only.
* Risiken: Migration älterer Saves ohne Feld.

To-do

* Codex: Kommandos `!sf on/off` implementieren (Persistenz
  `logs.flags.self_reflection`), Overlay‑Hook ergänzen.
* QA: Mission‑5‑Badge‑Check (Foreshadow 2/2 → M5) wiederholen, anschließend
  Abbruch und prüfen, ob `SF-ON` korrekt zurückkehrt (Reset‑Test).

Nächste Schritte

* Maintainer:innen: README Acceptance‑Hinweis beibehalten; Spezifizierung des
  Flags im Save‑Schema ergänzen.
* Notizen: `ui.intro_seen`‑ähnlicher Guard als Vorbild für Persistenzfelder.

ISSUE #4

* Beobachtung: „Solo→Koop“-Import verteilt Wallets erst **nach** einem Debrief;
  vor dem ersten Koop‑Payout existieren keine `economy.wallets{}`‑Einträge,
  wodurch HUD‑Wallet‑Shortcuts ins Leere laufen.
* Diagnose: Regeltext verlangt initiale Wallet‑Erzeugung **vor** der nächsten
  Auszahlung; im Flow fehlen aber Pre‑Debrief‑Wallet‑Placeholders, weshalb
  Koop‑HUD‑Abfragen auf `undefined` treffen.
* Evidenz: Cross‑Mode‑Test: Solo‑Save laden → Koop‑Start (2 NSCs) →
  `!wallet status` vor Mission liefert leere Struktur; Debrief erstellt Wallets
  korrekt. (Acceptance‑Smoketest: Dispatcher 5 + Koop‑Wallet‑Split.)

Lösungsvorschlag

* Ansatz: Bei Moduswechsel `party.characters[]` scannen und leere
  Wallet‑Einträge `{balance:0,name}` sofort anlegen.
* Risiken: Ghost‑Wallets bei später entfernten Chars; Mapping `id↔name` beachten.

To-do

* Codex: Hook „on group init“ ergänzt Wallet‑Init + HUD‑Toast „Wallets
  initialisiert (n×)“.
* QA: Solo→Koop→Debrief dreifach testen (gleichmäßiger Split, Ratio‑Split,
  Prozent‑Split).

Nächste Schritte

* Maintainer:innen: Readme‑Abschnitt „Koop‑Debrief & Wallet‑Split“
  unverändert; Changelog vermerken.
* Notizen: `economy.cu` als HQ‑Pool sichtbar halten.

ISSUE #5

* Beobachtung: `arenaStart()` blockiert Saves korrekt, aber der Psi‑Arena‑Aufschlag
  (`phase_strike_tax`) wird nicht in `logs.psi[]` persistiert.
* Diagnose: Psi‑Modul verlangt beim Arena‑Tax expliziten Log‑Eintrag samt
  HUD‑Toast; im getesteten PvP‑Flow erscheint nur der Toast, kein persistenter
  Trace.
* Evidenz: PvP‑Sparring (Acceptance: Boss/Arena‑Kurzinfo): `arenaStart()` →
  Phase‑Strike nutzen → HUD‑Toast „Arena: Phase‑Strike belastet +1 SYS“
  erscheint, `logs.psi[]` bleibt leer im Debrief.

Lösungsvorschlag

* Ansatz: `phase_strike_cost(state,{log:true})` erzwingen und `logs.psi[]`
  Schema (ability, base, tax, total, mode) spiegeln.
* Risiken: Log‑Spam; Performance bei vielen Psi‑Aktionen.

To-do

* Codex: Persistenzpfad für Psi‑Arena‑Tax herstellen; Debrief um `Psi-Trace
  (n×)` erweitern.
* QA: PvP‑Doppelmatch (Single/Squad) mit 3× Phase‑Strike; Debrief‑Diff prüfen.

Nächste Schritte

* Maintainer:innen: Psi‑Modul‑Mirror in Wissensbasis bestätigen.
* Notizen: `psi_buffer`‑Guard im PvP zusätzlich verifizieren.

ISSUE #6

* Beobachtung: `ShowComplianceOnce()` setzt Flag inkonsistent (Runtime vs.
  Campaign); nach `!load` erscheint der Hinweis 2×/Tag in Randfällen.
* Diagnose: Doppelte Spiegelung (`campaign.compliance_shown_today` und
  `state.logs.flags.compliance_shown_today`) ist vorgesehen, aber der
  Mirror‑Sync ist nicht überall garantiert; README/Toolkit nennen die
  beabsichtigte Kopplung explizit.
* Evidenz: Acceptance 7 (Load): Save laden → Recap → kurzer HQ‑Interlude →
  erneutes `Spiel laden` mit identischem Save in derselben Sitzung →
  Compliance erscheint erneut.

Lösungsvorschlag

* Ansatz: Nach `hydrate_state()` immer `SkipEntryChoice()` **und**
  `ShowComplianceOnce()` ausführen und die Flags bidirektional synchronisieren
  (Mirror‑Pfad im Toolkit hart verankern).
* Risiken: Compliance skippt legitime Erstanzeigen bei Semver‑Migration.

To-do

* Codex: Mirror‑Utility `sync_compliance_flags()` implementieren.
* QA: 3× Load‑Loop mit Semver‑OK und Semver‑Mismatch‑Probe
  (Negativfall‑Text prüfen).

Nächste Schritte

* Maintainer:innen: Docs‑Hinweis „Mirror‑Pflicht“ bleibt bestehen; QA‑Journal aktualisieren.
* Notizen: „Chronopolis‑Warnung“ auf ähnliches Doppelflag prüfen.

ISSUE #7

* Beobachtung: `!offline` erzeugt korrekte Toaster, aber `logs.offline[]` rotiert nicht bei >12
  Einträgen (FIFO) in allen Pfaden.
* Diagnose: Tooling beschreibt FIFO‑Deckel (max. 12); in mindestens einem Pfad
  (repeated `!offline` in gleicher Szene) wird Liste nicht nach links
  geschnitten.
* Evidenz: Solo‑Run (Frühphase): 14× `!offline` in derselben Szene → Debrief
  listet 14 Einträge, entgegen Spec „max. 12“. (Acceptance: Dispatcher –
  Offline‑Hinweise & Fallbacks.)

Lösungsvorschlag

* Ansatz: Vor Append immer `if len>=12: pop(0)` ausführen (bereits im Spec,
  überall anwenden).
* Risiken: Verlust ältester Evidenzen bei Langläufen; akzeptiert laut Spec.

To-do

* Codex: Konsolidierter `offline_help()`‑Hook in allen Pfaden.
* QA: 20× `!offline`‑Spam; Liste muss 12 Einträge halten mit korrekter
  `count`‑Fortzählung.

Nächste Schritte

* Maintainer:innen: Keine Doc‑Änderung; nur Implementierung angleichen.
* Notizen: Debrief-Feld „Offline-Protokoll (n×)“ sollte n=12 deckelklar
  anzeigen.

ISSUE #8

* Beobachtung: Boss‑Gate‑Hilfsbefehl `!helper boss` nach Mission 4 zeigt
  erwarteten Blocker, aber im HUD fehlt ein konsistenter „Gate aktiv“-Badge
  neben `FS x/y`.
* Diagnose: README verweist auf HUD‑Toast „Boss blockiert …“ und FS‑Zähler; ein
  persistenter Badge ist optional, aber das Glossar nennt „Kodex‑Badges“ für
  Status (z. B. Risk‑Level, Boss‑Gates). Aktuell kein dauerhafter Gate‑Badge bis
  zur Erfüllung.
* Evidenz: Acceptance 11: `!helper boss` nach M4 → einzelner Toast erscheint,
  Overlay danach ohne dauerhafte Gate‑Marke.

Lösungsvorschlag

* Ansatz: Kleines „GATE“‑Badge neben FS‑Zähler rendern, solange Gate nicht
  erfüllt (Core: bis 2/2 erreicht).
* Risiken: HUD‑Überfrachtung.

To-do

* Codex: `scene_overlay()` um `· GATE` erweitern, deaktiviert bei
  `Foreshadow>=2` (Core‑Gate).
* QA: M4→M5 Übergang erneut prüfen; Screenshot‑Beweis ergänzen.

Nächste Schritte

* Maintainer:innen: HUD‑Spec (Badges) in `zustaende-hud-system.md` nachziehen.
  (Glossar verweist bereits auf Badges.)
* Notizen: Auch für Rift‑Gate (2/2 in Szene 10) verwenden.

ISSUE #9

* Beobachtung: `!radio log`/`!alias log` erscheinen im Debrief, aber
  Start‑Dispatcher‑Flows vergessen den Clear‑Hinweis vor Einsatzstart
  gelegentlich.
* Diagnose: Toolkit/README empfehlen `!radio clear`/`!alias clear` vor neuen
  Einsätzen; Dispatcher‑Prompts nennen diese Clear‑Steps nicht in jedem
  Startpfad.
* Evidenz: Koop‑Run (Midgame): Vorhandene Funklogs werden in neue Mission
  übernommen; Debrief mischt Meldungen aus zwei Einsätzen.

Lösungsvorschlag

* Ansatz: Start‑Dispatcher ergänzt obligatorischen Hinweis „Logs vor
  Einsatzstart leeren“ und bietet Shortcut an.
* Risiken: Keine.

To-do

* Codex: `!help start` um Clear‑Remember erweitern.
* QA: Drei Startpfade (solo/npc/grupppe) auf Clear‑Hinweis prüfen.

Nächste Schritte

* Maintainer:innen: README‑Starttranskripte ggf. erweitern.
* Notizen: Debrief weiterhin zusammenfassend korrekt.

ISSUE #10

* Beobachtung: `px_tracker(temp)`‑Overlay überschätzt ETA in
  Low‑TEMP‑Kampagnen um 1 Mission.
* Diagnose: ETA‑Mapping im Toolkit nutzt Schwellen 3/7/10/13; Playtest mit
  TEMP 3 lieferte ETA 5, während Progression/Kommunikation in README temporär 4
  signalisierte (Inkonsistenz in Messaging, nicht unbedingt Regel).
* Evidenz: Solo‑Frühphase: TEMP 3 → HUD `ETA +1 in 5 Missionen`;
  README‑Kommschilderung im KPI‑Block legt eher 4 nahe
  (Interpretationsspielraum).

Lösungsvorschlag

* Ansatz: README klarstellen, dass ETA‑Heuristik Toolkit‑basiert ist; ggf.
  TEMP‑Bänder anpassen oder Beispielwerte an Toolkit angleichen.
* Risiken: Balance des Px‑Tempos.

To-do

* Codex: `px_tracker()`‑Text um „Heuristik“ ergänzen.
* QA: TEMP=3/7/10/14‑Runs prüfen, ob Anzeige und Dokumentation
  übereinstimmen.

Nächste Schritte

* Maintainer:innen: README KPI‑Beispielwerte aktualisieren.
* Notizen: Keine.

ISSUE #11

* Beobachtung: `StartMission()` setzt `AllowEntryChoice()` und zeigt
  Transfer‑Frame korrekt, aber `DelayConflict(4)` wird in Heist/Street‑Tags
  nicht konsistent reduziert.
* Diagnose: Spezifikation: Heist/Street senken Limit je −1 (min 2);
  Pfadabhängig scheint der Tag‑Normalizer nicht immer zu greifen (Liste vs.
  Pipe‑String).
* Evidenz: Heist‑Mission (Face‑Lead): Früher Konflikt erst ab Szene 4 statt 3;
  Toolkit‑Snippet zeigt Tag‑Reduktion, aber `tags_source`‑Parsing kann
  fehlschlagen, wenn als `'heist|street'` übergeben.

Lösungsvorschlag

* Ansatz: `tags_source` strikt normalisieren (split `|` **und** `,`), Lower‑Trim, uniq.
* Risiken: Keine.

To-do

* Codex: Tag‑Parser vereinheitlichen.
* QA: Heist/Street 4‑Runs; `can_open_conflict()` Soll/Ist prüfen.

Nächste Schritte

* Maintainer:innen: Keine Doc‑Änderung nötig.
* Notizen: Add Unit‑Test in Toolkit‑Spec.

ISSUE #12

* Beobachtung: Semver‑Mismatch‑Text unterscheidet sich zwischen README und Toolkit‑Pfad.
* Diagnose: README: „Kodex‑Archiv: Datensatz vX.Y nicht kompatibel …“; Toolkit‑Start‑Dispatcher
  nennt „Save stammt aus vX.Y … – nicht kompatibel.“ Uneinheitliches Wording.
* Evidenz: Acceptance 7 (Load): Mismatch provoziert; Texte differieren.

Lösungsvorschlag

* Ansatz: Einheitlichen Fehlertext aus README überall spiegeln.
* Risiken: Keine.

To-do

* Codex: Template‑String zentralisieren.
* QA: Semver‑Mismatch auf zwei Pfaden (Start‑Dispatcher & manueller `!load`) prüfen.

Nächste Schritte

* Maintainer:innen: Docs angleichen; Translator‑Keys einführen.
* Notizen: Keine.
```

