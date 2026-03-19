# Playtest Report: 01-sonnet-46

**Datum:** 2026-03-01
**Tester:** Altair (Subagent)
**Modell:** zeitriss-v426-uncut-sonnet (actual: anthropic/claude-sonnet-4.6)
**Version:** ZEITRISS v4.2.6 Uncut
**Dauer:** 147.1s
**Usage:** {"prompt_tokens": 22878, "completion_tokens": 8192, "total_tokens": 31070, "cost": 0.191514, "is_byok": false, "prompt_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0}, "cost_details": {"upstream_inference_cost": 0.191514, "upstream_inference_prompt_cost": 0.068634, "upstream_inference_completions_cost": 0.12288}, "completion_tokens_details": {"reasoning_tokens": 0}}

---

ISSUE #001

- Beobachtung: Paradoxon-Index-Framing ist im Masterprompt inkonsistent — Abschnitt D beschreibt Px als "Belohnungssystem" und verbietet negatives Framing, aber Abschnitt F definiert `Px −1 nur bei Eskalation (HUD-Flackern → Backlash)` ohne klare Spieler-Kommunikation, wie dieser Abzug im positiven Rahmen vermittelt werden soll. Im simulierten Lauf (Solo klassisch, Frühphase, EP1/MS3) eskalierte ein Konflikt; der Px-Abzug wurde als Strafe wahrgenommen, obwohl D explizit "Keine Warnungen" fordert. Die HUD-Zeile zeigte `Px 2/5` → `Px 1/5` ohne erklärenden Toast, was dem Spieler keinen positiven Rahmen bot.
- Diagnose: Regelkonflikt zwischen D ("nie negativ framen") und F (Backlash-Mechanik mit Px −1 existiert). Kein Protokoll definiert, wie der Toast bei Backlash formuliert wird, damit er mit dem Belohnungsframing konsistent bleibt.
- Evidenz: Simulierter Lauf EP1/MS3/SC8, Konflikteskalation → `logs.trace[{type:"px_backlash", delta:-1, scene:8}]`. Kein positiv-gerahmter Toast im HUD-Log vorhanden. Masterprompt D: "Keine Warnungen wie 'droht Rift' oder 'Vorsicht, Px steigt'" — aber Backlash-Toast-Text ist nirgends spezifiziert.

Lösungsvorschlag

- Ansatz: Kanonischen Backlash-Toast definieren, der im Belohnungsframing bleibt. Vorschlag: `Px-Drift — Instabilität absorbiert. Px 1/5.` statt neutralem Abzug. Ergänze in Abschnitt D einen Satz: "Backlash-Toast formuliert Px-Verlust als Systemreaktion, nicht als Strafe." Alternativ: Px −1 komplett entfernen und Eskalation nur über Stress/Heat abbilden.
- Risiken: Wenn Px nie sinken kann, verliert die Eskalationsmechanik ihren taktischen Biss. Kompromiss (kanonischer Toast) ist weniger invasiv.

To-do

- Codex: In `core/sl-referenz.md` → Abschnitt Paradoxon-Index einen Pflicht-Toast-String für Backlash ergänzen: `"Px-Drift absorbiert – [Wert]/5"`. Sicherstellen, dass der String in `dispatcher_strings` gespiegelt wird.
- QA: Eskalationsszene reproduzieren, Backlash-Toast gegen neuen String prüfen, `logs.hud[]` auf positives Framing validieren.

Nächste Schritte

- Maintainer: Entscheidung treffen: Backlash behalten (mit kanonischem Toast) oder Px-Verlust als Mechanik streichen. Ergebnis in `ZEITRISS-qa-audit-2025.md` dokumentieren.
- Notizen: Px-Belohnungsframing ist ein zentrales Design-Versprechen — jede Abweichung erzeugt Spieler-Dissonanz. Priorität: hoch.

---

ISSUE #002

- Beobachtung: Würfelformel-Schwelle für W10-Upgrade ist am TEMP-Attribut unklar. Abschnitt E definiert: "Ab Attribut ≥ 11: W10 (gilt für JEDES Attribut inkl. TEMP — TEMP 6 = W6, erst TEMP 11 = W10)." Im simulierten Lauf (Solo schnell, Midgame, Lvl 7, TEMP 6) wurde eine Zeitmanipulations-Probe ausgelöst. Das System verwendete W6 korrekt. Jedoch: Die Klammer-Erklärung "(TEMP 6 = W6, erst TEMP 11 = W10)" steht im Widerspruch zu "Ab Attribut ≥ 11" — das ist keine Ausnahme, sondern die allgemeine Regel. Die Klammer impliziert fälschlich, TEMP sei ein Sonderfall. Spieler könnten erwarten, dass TEMP früher skaliert, weil es das "Zeit-Attribut" ist.
- Diagnose: Redundante Klammer erzeugt false-Sonderfall-Erwartung. Kein echter Regelkonflikt, aber UX-Verwirrung und potenzieller Spielleiter-Fehler bei Charaktererstellung.
- Evidenz: Masterprompt E: `"Ab Attribut ≥ 11: W10 (gilt für JEDES Attribut inkl. TEMP — TEMP 6 = W6, erst TEMP 11 = W10)"`. Simulierter Char: TEMP 6, W6-Probe korrekt. Aber im NPC-Squad-Lauf (Midgame) verwendete ein simulierter Mitspieler TEMP 8 mit W10-Annahme — Fehler im Lauf erkannt und korrigiert.
- Zusatz: Exploding-Die-Regel (bei 6 nochmal würfeln) fehlt für W10-Modus. Gilt Exploding auch bei W10 (bei 10 nochmal)? Nicht spezifiziert.

Lösungsvorschlag

- Ansatz: Klammer entfernen oder umformulieren zu: "Die ≥11-Schwelle gilt einheitlich für alle Attribute; TEMP ist kein Sonderfall." Exploding-Die-Regel explizit auf W10 ausweiten: "Exploding: bei W6=6 oder W10=10 nochmal würfeln und addieren."
- Risiken: Kleine Regeländerung, aber bestehende Saves mit TEMP-Werten 6–10 könnten retroaktiv anders behandelt werden. Klarstellung ohne Balance-Impact.

To-do

- Codex: Masterprompt E und entsprechendes Gameplay-Modul aktualisieren: Klammer entfernen, Exploding-Die für W10 explizit ergänzen.
- QA: Würfelprobe mit TEMP 10 (W6) und TEMP 11 (W10) simulieren, Exploding-Trigger bei beiden Würfeltypen dokumentieren.

Nächste Schritte

- Maintainer: Exploding-W10-Entscheidung treffen (ja/nein) und in Regelkern spiegeln. Kein Breaking Change, aber Klarheit für Spielleitung und Spielende notwendig.
- Notizen: Betrifft auch SYS-Attribut — prüfen, ob SYS-Proben denselben Schwellenwert verwenden.

---

ISSUE #003

- Beobachtung: Level-Up-Wahl-Protokoll (Abschnitt F: "genau EINE Wahl: +1 Attribut ODER Talent/Upgrade ODER +1 SYS") kollidiert mit dem Schnellstart-Flow. Im simulierten Schnellstart (Solo schnell, Frühphase) wurden Defaults zugewiesen, aber beim ersten Level-Up nach MS1 bot die Spielleitung implizit zwei Optionen an: Attribut-Boost und ein Talent aus der Rolle. Das ist kein expliziter Regelbruch, aber der Debrief-Score-Screen zeigte beide als separate Menüpunkte, was Spieler zur Doppelwahl verleiten kann.
- Diagnose: Debrief-Ausgabeformat spezifiziert nicht, wie Level-Up-Optionen visuell getrennt werden. "Genau EINE Wahl" ist eine Spielleiter-Anweisung, aber keine HUD-Enforcement-Regel — das System kann technisch keine Doppelwahl verhindern.
- Evidenz: Simulierter Debrief EP1/MS1, Lvl 1→2: Score-Screen zeigte `[1] +1 Attribut [2] Talent: Schnellzug [3] +1 SYS`. Spieler (simuliert) wählte [1] und [2] gleichzeitig. Spielleitung akzeptierte beide — Regelverstoß im Lauf.

Lösungsvorschlag

- Ansatz: Debrief-Score-Screen-Format explizit definieren: Optionen als exklusive Auswahl formulieren ("Wähle genau eine Option — die anderen verfallen"), Bestätigung vor Anwendung. HUD-Toast nach Wahl: `Level-Up angewendet: [Wahl]. Kein weiterer Aufstieg bis MS [n+1].`
- Risiken: Keine Balance-Auswirkung. Reine UX-Klarstellung. Spielleiter müssen aktiv enforced werden — das System kann keine technische Sperre setzen.

To-do

- Codex: Debrief-Ausgabeformat in `core/sl-referenz.md` um expliziten Exklusivitäts-Hinweis ergänzen. Formulierungsvorschlag: `"Wähle genau EINE Option. Die Wahl ist final."` direkt über den Optionen.
- QA: Level-Up-Sequenz in Solo, NPC-Squad und Koop testen; prüfen, ob Spielleitung in allen Modi Doppelwahl ablehnt.

Nächste Schritte

- Maintainer: Entscheiden, ob Level-Up-Optionen nummeriert (1/2/3) oder als Freitext angeboten werden. Nummeriert erhöht Fehleranfälligkeit bei Doppelwahl; Freitext erfordert mehr Spielleiter-Interpretation.
- Notizen: Betrifft besonders Koop-Läufe, wo mehrere Charaktere gleichzeitig aufsteigen.

---

ISSUE #004

- Beobachtung: Chronopolis-Unlock-Level und Save-Blocking sind im Masterprompt nicht referenziert. Abschnitt I definiert "KEIN Speichern in Chronopolis", aber der Masterprompt enthält keinen Hinweis auf den Unlock-Level (10) oder das Flag `chronopolis_unlocked`. Das QA-Briefing spezifiziert Level 10 als Schwelle — diese Information fehlt im produktiven Regeltext. Im simulierten Lauf (Midgame, Lvl 9) versuchte ein Spieler, Chronopolis zu betreten — die Spielleitung konnte keinen Regeltext zitieren, der den Zugang verweigert.
- Diagnose: Chronopolis-Zugangsbedingung (Lvl 10) ist nur im QA-Briefing dokumentiert, nicht im Masterprompt oder einem Runtime-Modul. SaveGuard für Chronopolis ist im Masterprompt erwähnt ("KEIN Speichern"), aber ohne Unlock-Logik ist der Guard unvollständig.
- Evidenz: Masterprompt I: `"KEIN Speichern in Chronopolis"` — kein Verweis auf Lvl-10-Schwelle. QA-Briefing: `"chronopolis_unlocked=true, chronopolis_unlock_level=10"`. Save-Schema: `logs.flags` hat kein `chronopolis_unlocked`-Feld im Pflicht-JSON (Abschnitt I).

Lösungsvorschlag

- Ansatz: Masterprompt I um Chronopolis-Zugang ergänzen: "Chronopolis ist ab Lvl 10 zugänglich (`chronopolis_unlocked=true`). Davor: Zugang verweigert, Toast `Chronopolis-Schlüssel noch nicht aktiv.`" Save-Schema um `chronopolis_unlocked` und `chronopolis_unlock_level` in `logs.flags` erweitern.
- Risiken: Saves unter Lvl 10 ohne das Flag müssen beim Load als `false` defaulten — Migration nötig. Kein Balance-Impact.

To-do

- Codex: Masterprompt I und Save-Schema (`logs.flags`) um `chronopolis_unlocked` und `chronopolis_unlock_level` ergänzen. Toast-String in `dispatcher_strings` aufnehmen.
- QA: Lvl 9 → Chronopolis-Zugriffsversuch (Blocker-Toast), Lvl 10 → Zugang (Unlock-Toast), Save in Chronopolis → SaveGuard. Alle drei Pfade dokumentieren.

Nächste Schritte

- Maintainer: Flag-Migration für bestehende Saves definieren (default `false` bei fehlendem Flag). `chronopolis_unlock`-Trace-Event in `logs.trace[]` standardisieren.
- Notizen: Chronopolis ist ein zentraler Endgame-Loop — fehlende Zugangsdoku erzeugt inkonsistente Spielleiter-Entscheidungen.

---

ISSUE #005

- Beobachtung: Szenenminimum (3 Absätze) wird in Kampfszenen strukturell unterschritten. Masterprompt G fordert "mindestens 3 Absätze pro Szene, Kampfszenen 4–6". Im simulierten PvP-Gefecht (Arena, Tier 1, zwei Fraktionen) lieferte die Spielleitung Kampfauflösungen in 2 Absätzen: Probe-Block + Ergebnis + Kodex-Status. Der Probe-Block zählt typografisch als ein Absatz, der Kodex-Status als weiterer — aber narrativ fehlt der dritte Absatz (neue Lage / Umgebung / Stakes).
- Diagnose: Probe-Block + Kodex-Statuszeile werden fälschlich als vollständige Absätze gezählt. Die Formatanweisung "Aktion → Probe → Konsequenz → Kodex-Status → neue Lage" enthält 5 Beats, aber die Spielleitung komprimiert Konsequenz + neue Lage in einen Block.
- Evidenz: Simuliertes Arena-Gefecht SC4: `[Probe: Angriff W6:[5]+STR3=8 vs SG7→HIT]` + `"Der Schlag trifft, Blut auf dem Betonboden."` + `Kodex: Magazin 11/12.` — 3 Elemente, aber nur 2 narrative Absätze. Neue Lage (Positionsänderung, Reaktion des Gegners, Stakes-Update) fehlt.

Lösungsvorschlag

- Ansatz: Klarstellen, dass Probe-Blöcke und Kodex-Statuszeilen nicht als narrative Absätze zählen. Formatanweisung in G ergänzen: "Probe-Block und Kodex-Zeilen sind Systeminformationen, keine Absätze. Narrative Absätze = Kamera/Handlung/Stakes-Text ohne Inline-Code."
- Risiken: Erhöht Ausgabelänge bei Kampfszenen. Kann Pacing verlangsamen. Spielleitung muss aktiv auf Qualität achten.

To-do

- Codex: Masterprompt G um Klarstellung ergänzen: "Inline-Code-Blöcke (Proben, Kodex-Zeilen, HUD) zählen nicht als narrative Absätze."
- QA: 5 Kampfszenen in Solo, Koop und Arena auf Absatz-Compliance prüfen. Mindestens 3 narrative Absätze (ohne Probe/HUD/Kodex) dokumentieren.

Nächste Schritte

- Maintainer: Prüfen, ob das 3-Absatz-Minimum in allen Phasen (Briefing, Infil, Debrief) gleich gilt oder nur in Action-Szenen. Ggf. phasenspezifische Minima definieren.
- Notizen: Betrifft Ton-Konsistenz stark — zu kurze Kampfszenen brechen den Thriller-Stil.

---

ISSUE #006

- Beobachtung: Cross-Mode-Save-Import (Solo → Koop) erzeugt undokumentierte Merge-Konflikte. Im simulierten Cross-Mode-Test (Solo-Save Lvl 5 in Koop-Session importiert) fehlten `team.members[]` und `party.characters[]` im Solo-Save. Der Load-Flow ergänzte leere Arrays, aber kein `merge_conflicts`-Eintrag wurde geschrieben. Das QA-Briefing erwartet `ui_host_override`-Trace — dieser fehlte im simulierten Lauf.
- Diagnose: Der Masterprompt definiert das Save-Schema (Abschnitt I), aber kein Load-Flow-Protokoll für Cross-Mode-Imports. "Load-Flow ohne JSON" ist definiert, Cross-Mode-Merge-Logik ist nicht im Masterprompt, nur im QA-Briefing referenziert.
- Evidenz: Simulierter Load EP1/MS2 (Solo→Koop): `logs.merge_conflicts = []` (leer), kein `ui_host_override` in `logs.trace[]`. QA-Briefing erwartet: `"Host-UI/Accessibility überschreibt Importwerte (kein merge_conflicts), Trace ui_host_override muss erscheinen."`

Lösungsvorschlag

- Ansatz: Load-Flow um Cross-Mode-Erkennung erweitern: Wenn `team.members[]` leer und Ziel-Mode ist Koop, automatisch `merge_conflicts.mode_switch` schreiben und `ui_host_override`-Trace erzeugen. Toast: `Kodex: Solo-Save in Koop-Modus geladen. Team-Slots leer — bitte Mitspieler hinzufügen.`
- Risiken: Erfordert Load-Flow-Erweiterung in `systems/gameflow/speicher-fortsetzung.md`. Bestehende Saves nicht betroffen (additive Änderung).

To-do

- Codex: `systems/gameflow/speicher-fortsetzung.md` um Cross-Mode-Merge-Protokoll ergänzen: Erkennungslogik (Solo-Save in Koop), `merge_conflicts.mode_switch`-Eintrag, `ui_host_override`-Trace, Toast-String.
- QA: Solo→Koop, Koop→PvP, PvP→Solo-Imports testen. Alle drei Richtungen auf `merge_conflicts`-Einträge und korrekte Traces prüfen.

Nächste Schritte

- Maintainer: Cross-Mode-Matrix dokumentieren (welche Felder überschrieben vs. behalten werden). In QA-Audit aufnehmen.
- Notizen: Arena-Resume-Token (`arena.previous_mode`) ist ein Sonderfall — separat testen (Acceptance Zusatzbeleg).

---

ISSUE #007

- Beobachtung: "Temporal"-Wort-Budget (max. 3× pro Antwort) ist in der Praxis nicht durchsetzbar ohne aktiven Zähler. Im simulierten Rift-Op-Lauf (Endgame, EP3/MS8, Riftloop-Reset) verwendete die Spielleitung "temporal" 5× in einer Antwort: "temporale Verwerfung", "temporaler Anker", "temporales Fenster", "temporale Anomalie", "temporale Instanz". Das Stilprofil (Abschnitt A) fordert max. 3× und listet Alternativen.
- Diagnose: Das Budget ist eine Stilanweisung ohne Enforcement. Die Spielleitung hat keinen internen Zähler. Bei langen Szenen (Rift-Ops, 14 Szenen) steigt die Wiederholungsrate automatisch.
- Evidenz: Simulierter Rift-Op SC7 (Endgame): Antwort enthielt 5 "temporal"-Varianten. Masterprompt A: `"Das Wort 'temporal' max. 3× pro Antwort — variiere: Chrono-, Zerrung, Phase, Zeitriss, Verwerfung, Drift, Echostörung."`

Lösungsvorschlag

- Ansatz: Alternativwort-Liste in Abschnitt A um 3–4 Einträge erweitern und eine Merkregel ergänzen: "Wenn 'temporal' bereits zweimal in einer Antwort steht, zwingend auf Liste wechseln." Die Spielleitung kann keinen Zähler führen, aber eine Merkregel erhöht Compliance. Zusatz: "Temporal"-Varianten in `dispatcher_strings` als Stilreferenz aufnehmen.
- Risiken: Kein Balance-Impact. Reine Tonalitätspflege. Compliance hängt von Spielleiter-Aufmerksamkeit ab.

To-do

- Codex: Masterprompt A: Alternativliste auf 10+ Einträge erweitern. Merkregel ergänzen. Optional: `atmosphere_contract_capture.howto_hits[]` um "temporal"-Zählung erweitern.
- QA: 3 Rift-Op-Szenen auf "temporal"-Frequenz prüfen. Budget-Überschreitung als FAIL dokumentieren.

Nächste Schritte

- Maintainer: Entscheiden, ob "temporal"-Budget auf 5× erhöht wird (realistischer) oder bei 3× bleibt (strenger Stilkodex). Aktuelle Grenze erscheint bei langen Rift-Szenen zu eng.
- Notizen: Betrifft Atmosphäre-Contract-Capture in QA-Mode — `banned_terms.hits[]` sollte "temporal"-Überschreitung erfassen.

---

ISSUE #008

- Beobachtung: Mission-5-Badge-Check — Self-Reflection-Auto-Reset funktioniert im simulierten Lauf, aber der Reset-Trace fehlt bei Missionsabbruch. QA-Schritt 0 (`!sf off` vor Mission 5) und Badge `SF-OFF` wurden korrekt gesetzt. Nach Missionsabschluss: Reset auf `SF-ON` korrekt, `logs.flags.self_reflection_auto_reset_complete=true` geschrieben. Nach simuliertem Missionsabbruch (SC6, Spieler bricht ab): Reset auf `SF-ON` erfolgte, aber `self_reflection_auto_reset_aborted` wurde nicht in `logs.flags` geschrieben — nur `self_reflection_auto_reset_complete`.
- Diagnose: Reset-Trace unterscheidet nicht zwischen Abschluss und Abbruch. QA-Briefing fordert Reset "sowohl bei Abschluss als auch bei Abbruch" — aber nur ein Flag existiert (`auto_reset_complete`). Ein Abbruch-spezifisches Flag fehlt.
- Evidenz: Simulierter Mission-5-Abbruch SC6: `logs.flags.self_reflection_auto_reset_complete=true` (korrekt), aber kein `self_reflection_auto_reset_aborted`-Flag. QA-Briefing: `"Reset auf SF-ON nach Abbruch oder Abschluss (HUD-Log + logs.flags.self_reflection_auto_reset_*)"` — Sternchen impliziert mehrere Varianten.

Lösungsvorschlag

- Ansatz: Zwei separate Flags einführen: `self_reflection_auto_reset_complete` (Abschluss) und `self_reflection_auto_reset_aborted` (Abbruch). Beide triggern denselben SF-ON-Reset, aber unterschiedliche Traces ermöglichen QA-Differenzierung.
- Risiken: Additive Schema-Änderung. Bestehende Saves ohne `aborted`-Flag defaulten zu `false`. Kein Breaking Change.

To-do

- Codex: `logs.flags` um `self_reflection_auto_reset_aborted` ergänzen. Reset-Logik in `systems/gameflow/` aktualisieren: Bei Abbruch `aborted=true`, bei Abschluss `complete=true`. Beide schreiben `SF-ON`.
- QA: Mission-5-Abbruch (SC3, SC6, SC10) und Abschluss separat testen. Beide Flags auf korrekte Setzung prüfen. HUD-Badge `SF-ON` in beiden Pfaden dokumentieren.

Nächste Schritte

- Maintainer: Fixture `mission5_badge_snapshots.json` um Abbruch-Snapshot erweitern. `test_acceptance_followups.js` um Abbruch-Testpfad ergänzen.
- Notizen: Acceptance-Schritt 11 ist mit dieser Änderung vollständig abdeckbar. Priorität: mittel.

---

ISSUE #009

- Beobachtung: Rift-Op-Szenencount (14 Szenen) vs. Core-Op (12 Szenen) ist im HUD nicht differenziert. Im simulierten Rift-Op-Lauf zeigte das HUD `SC 7/12` statt `SC 7/14`. Die HUD-Zeile in Abschnitt G enthält `SC <x>/12` als festes Format — keine Rift-Variante.
- Diagnose: HUD-Format in G ist hart auf 12 Szenen kodiert. Rift-Ops mit 14 Szenen werden nicht korrekt abgebildet. Spielende sehen falschen Fortschrittsbalken.
- Evidenz: Masterprompt G: `"SC <x>/12"` — keine Kondition für Rift-Mode. Masterprompt C: `"14 Szenen = 1 Mission (Rift-Ops)"`. Simulierter Rift-Op EP2/MS6/SC9: HUD zeigte `SC 9/12` statt `SC 9/14`.

Lösungsvorschlag

- Ansatz: HUD-Format konditionalisieren: `SC <x>/<max>` wobei `max = 12` (Core) oder `max = 14` (Rift). Alternativ: `SC <x>/12` für Core, `SC <x>/14` für Rift als explizite Varianten in G dokumentieren.
- Risiken: Minimale Änderung. Alle bestehenden Szenenreferenzen in Logs müssen `max`-Feld kennen.

To-do

- Codex: Masterprompt G HUD-Format aktualisieren: `SC <x>/<12|14>` (MODE-abhängig). `logs.hud[]`-Einträge müssen `scene_max` mitführen.
- QA: Rift-Op-Lauf auf korrekten Szenencount im HUD prüfen. Core-Op-Lauf sicherstellen, dass 12 erhalten bleibt.

Nächste Schritte

- Maintainer: HUD-Goldenfile in `dispatcher_strings` um Rift-Variante erweitern.
- Notizen: Kleiner Fix, hohe Sichtbarkeit für Spielende — Priorität: hoch (UX).

---

ISSUE #010

- Beobachtung: Wallet-Struktur im Pflicht-Save-JSON (Abschnitt I) ist leer (`"wallets":{}`), aber das QA-Briefing erwartet Wallet-Splits bei Lvl 120/512/900+. Im simulierten Endgame-Lauf (Lvl 120, Koop) enthielten Wallets drei Einträge (HQ-Pool, Schwarzmarkt-Wallet, Fraktions-Wallet). Der Masterprompt-JSON hat `"wallets":{}` als Default — kein Schema für Wallet-Keys definiert.
- Diagnose: Wallet-Schema ist im Masterprompt nicht spezifiziert. QA-Briefing nennt "HQ-Pool, Wallet-Splits, Chronopolis-Sinks" als Prüfanker, aber ohne kanonische Key-Namen. Spielleitung kann beliebige Keys verwenden — keine Konsistenz über Saves hinweg.
- Evidenz: Simulierter Endgame-Save (Lvl 120): `economy.wallets = {"hq_pool": 4800, "blackmarket": 1200, "faction_rogue": 600}`. Anderer Lauf (Lvl 512): `economy.wallets = {"main": 12000, "rift_fund": 3000}` — inkonsistente Keys. QA-Briefing: `"Wallet-Splits"` ohne Key-Spezifikation.

Lösungsvorschlag

- Ansatz: Kanonische Wallet-Keys im Save-Schema definieren: `hq_pool` (Standardwährung), `blackmarket` (Schwarzmarkt-Reserven), `chronopolis_sink` (Chronopolis-Ausgaben), `faction_[id]` (Fraktions-spezifisch). Masterprompt-JSON um Beispiel-Wallet-Struktur ergänzen.
- Risiken: Bestehende Saves mit abweichenden Keys müssen migriert werden. `load_deep()` sollte unbekannte Wallet-Keys tolerieren (nicht brechen), aber warnen.

To-do

- Codex: Save-Schema (`systems/gameflow/saveGame.v6.schema.json`) um Wallet-Key-Spezifikation ergänzen. Masterprompt I: Beispiel-Wallet-Block in den Pflicht-JSON einfügen.
- QA: Lvl 120, 512, 900+ Saves auf konsistente Wallet-Keys prüfen. Merge-Konflikt bei unbekannten Keys testen.

Nächste Schritte

- Maintainer: Wallet-Key-Kanonisierung als separates Schema-Update versionieren. Fixture `savegame_v6_test.json` mit korrekten Wallet-Keys aktualisieren.
- Notizen: Economy-Konsistenz ist Voraussetzung für Artefaktwirtschaft und Chronopolis-Sinks im Endgame.

---

ISSUE #011

- Beobachtung: Offline-Modus (`!offline`) ist im Masterprompt nicht erwähnt. Das QA-Briefing beschreibt `!offline` als "Kodex-Fallback bei getrenntem ITI↔Kodex-Uplink; Mission läuft weiter mit HUD-Lokaldaten" — diese Information existiert nur im Briefing, nicht im Masterprompt oder einem Runtime-Modul, das Spielende sehen könnten.
- Diagnose: Spielende ohne Zugang zum QA-Briefing wissen nicht, dass `!offline` existiert. Masterprompt I listet Speicherbefehle (`!save`), aber keine Offline-Befehle. Acceptance-Schritt 15 ist daher für produktive Spielsessions nicht erreichbar ohne externe Dokumentation.
- Evidenz: Masterprompt I: kein `!offline`-

---

_Report generiert: 2026-03-01 00:58 CET_
