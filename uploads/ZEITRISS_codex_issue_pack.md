# ZEITRISS – Review + Codex-Issue-Pack

Dieses Dokument ist als Copy-Paste-Basis für GitHub-Issues, Codex-Aufträge oder Agenten-Tasks gedacht.

---

## Gesamturteil in einem Satz

ZEITRISS hat eine starke, seltene Kernidee und bereits erstaunlich viel Systemdisziplin – aber genau deshalb tun die aktuellen SSOT-Kollisionen besonders weh: Nicht die Vision ist das Problem, sondern mehrere konkurrierende Wahrheiten innerhalb des Runtime-Kanons.

---

## Priorität A – zuerst fixen

### Issue 1 — Save-Schema v7 als einzige Wahrheit durchziehen

**Titel**

`[P0] Save-Schema v7 als einzige Runtime-Wahrheit vereinheitlichen`

**Ziel**

Das Save-System soll in allen WS-Dateien, Save-Beispielen und Runtime-relevanten Dokus exakt dieselbe Struktur verwenden. Es darf nur noch **eine** kanonische Form geben.

**Problem**

Der aktuelle Runtime-Kanon spricht gleichzeitig mehrere Save-Dialekte:
- v7 mit `characters[]`, `wallet` pro Charakter, `economy.hq_pool`, `arc`
- v6/Legacy mit `party.characters[]`, `team.members[]`, `economy.cu`, `economy.wallets`, `arc_dashboard`
- zusätzliche Mischformen mit alten Feldnamen, alten Hilfscontainern und teils widersprüchlichen Migrationsaussagen

Das führt zu unsauberer Agentenarbeit, driftenden Saves und schwer nachvollziehbaren Merge-/Load-Pfaden.

**Aufgaben**

1. Definiere das **eine** kanonische Save-Schema für Runtime und Spieler-Export.
2. Nutze dieses Schema in **allen** geladenen Wissensspeicher-Dateien.
3. Verschiebe echte v6-Migrationsbeispiele aus den Runtime-Modulen in Dev-/Internal-Doku.
4. Kennzeichne Legacy-Migrationen nur noch als Importpfad, nicht als gleichwertige Dokumentation.
5. Benenne irreführende Artefakte um oder dokumentiere sie sauber (z. B. Dateiname `masterprompt_v6.md`, falls inhaltlich v7 gemeint ist).

**Nicht tun**

- Keine Zwischenversion `v6.5` erfinden.
- Keine zweite öffentliche Beispielstruktur parallel weiterführen.
- Keine Runtime-Doku mit Legacy-Feldern im aktiven Kanon belassen.

**Akzeptanzkriterien**

- In geladenen WS-Dateien gibt es genau **ein** kanonisches Save-Beispiel.
- Begriffe wie `party.characters[]`, `team.members[]`, `economy.cu`, `arc_dashboard`, `save_version: 6` erscheinen in Runtime-Modulen nicht mehr als aktiver Standard.
- Legacy wird nur noch als Import/Migration referenziert.
- Masterprompt, Save-Doku und SL-Referenz zeigen dieselbe Feldstruktur.

**Betroffene Dateien**

- `meta/masterprompt_v6.md`
- `systems/gameflow/speicher-fortsetzung.md`
- `core/sl-referenz.md`
- ggf. weitere WS-Dateien mit Save-Beispielen oder Save-Referenzen

---

### Issue 2 — Wallet-/Ökonomie-Modell kanonisieren

**Titel**

`[P0] Wallet- und HQ-Pool-Modell auf ein einziges Datenmodell reduzieren`

**Ziel**

Ein eindeutiges Ökonomie-Modell für Solo, Koop, Split und Merge.

**Problem**

Aktuell existieren mindestens zwei konkurrierende Modelle:
- Charakterzentriert: `character.wallet`
- Root-zentriert: `economy.wallets{}` plus `economy.cu`/`economy.hq_pool`

Solange beides parallel öffentlich dokumentiert wird, bleiben Split/Merge, Debrief und Teamwirtschaft unnötig fehleranfällig.

**Empfehlung**

Kanonisiere **ein** öffentliches Modell:
- pro Charakter: `wallet`
- global: `economy.hq_pool`

Interne Migrationslogik darf Altstände in dieses Modell überführen, aber der Runtime-Kanon und alle Spielertexte sollten nur noch dieses Modell kennen.

**Aufgaben**

1. Entscheide ein Zielmodell.
2. Passe Debrief, Shop, Arena, Split/Merge und Save-Doku daran an.
3. Dokumentiere klar, was beim Merge mit Gast-Wallets passiert.
4. Leite Legacy-Felder nur intern um und nenne sie nicht mehr als öffentlichen Standard.

**Akzeptanzkriterien**

- Kein öffentliches Runtime-Dokument nutzt gleichzeitig `wallet` **und** `economy.wallets` als kanonische Strukturen.
- HQ-Pool und Charakter-Wallets haben klar getrennte Verantwortlichkeiten.
- Merge-Regeln referenzieren exakt ein Modell.

**Betroffene Dateien**

- `meta/masterprompt_v6.md`
- `systems/gameflow/speicher-fortsetzung.md`
- `core/sl-referenz.md`
- `systems/currency/cu-waehrungssystem.md`
- Debrief-/Merge-Hooks in Runtime-naher Doku

---

### Issue 3 — Würfelkanon auf eine Regel reduzieren

**Titel**

`[P0] Würfel-SSOT bereinigen: Burst-Cap, W10-Schwelle und Heldenwürfel eindeutig definieren`

**Ziel**

Eine einzige, überall identische Würfelregel.

**Problem**

Der aktuelle Kanon kollidiert an drei Stellen:
- Burst-Cap wird mal klar definiert, mal gar nicht erwähnt.
- W10 ab Attribut 11 ist an mehreren Stellen Pflicht, an anderer Stelle aber als optionale Regel beschrieben.
- Heldenwürfel und Exploding sind nicht überall mit denselben Formulierungen verankert.

**Empfehlung**

Wenn du den aktuellen Spielerfluss erhalten willst, nimm als SSOT:
- W6 Standard
- W10 ab Attribut 11
- Heldenwürfel ab Attribut 14
- Burst-Cap: genau 1 Zusatzwurf pro Würfel, kein Ketten-Exploding

**Aufgaben**

1. Formuliere die Regel einmal sauber in einer Kernquelle.
2. Gleiche alle anderen WS-Dateien exakt daran an.
3. Entferne Formulierungen wie „optionale W10-Regel“, wenn W10 im Runtime-Kanon ohnehin verpflichtend ist.
4. Prüfe Beispiele, Tabellen, Quickrefs und Tooltips auf Konsistenz.

**Akzeptanzkriterien**

- Es gibt keinen geladenen Text mehr, der W10 gleichzeitig als Standard **und** als optional beschreibt.
- Burst-Cap wird überall gleich erklärt.
- Heldenwürfel, W10-Schwelle und Exploding-Beispiele widersprechen sich nicht mehr.

**Betroffene Dateien**

- `core/wuerfelmechanik.md`
- `meta/masterprompt_v6.md`
- `core/spieler-handbuch.md`
- `core/sl-referenz.md`

---

### Issue 4 — Px/Cluster/Arena sauber entkoppeln

**Titel**

`[P0] Paradoxon-Index als deterministischen Progressionspfad fixieren und Arena davon entkoppeln`

**Ziel**

Px soll wieder genau das sein, was das Projekt verspricht: ein klarer, lesbarer, deterministischer Progressions- und Belohnungsvektor.

**Problem**

Mehrere Texte behaupten gleichzeitig:
- Px sei strikt TEMP-gebunden und missionbasiert.
- Px 5 löse `ClusterCreate()` aus und resette danach.
- Der Reset passiere nach Debrief / via HQ-Bestätigung / zu Beginn der nächsten Mission.
- Arena könne ebenfalls Px-Belohnungen vergeben.

Damit ist die zentrale Progressionslogik nicht mehr glasklar.

**Empfehlung**

Kanonisiere:
- **Nur reguläre Missionen** verändern `campaign.px`.
- Arena gibt **kein Px**, sondern CU, Ruf, Trainings- oder Arena-spezifische Rewards.
- Sobald Px 5 erreicht: `ClusterCreate()` im Debrief, Seeds sichtbar, Reset im selben Flow dokumentiert.

**Aufgaben**

1. Bestimme exakt einen Reset-Zeitpunkt.
2. Entferne Arena->Px-Kopplung aus dem Standardkanon.
3. Vereinheitliche HUD-, Debrief- und Save-Texte.
4. Dokumentiere, ob Fehlschläge nie Px kosten oder ob es eine explizite Hardcore-Ausnahme gibt.

**Akzeptanzkriterien**

- Nur ein definierter Pfad verändert `campaign.px`.
- Reset-Zeitpunkt ist in allen WS-Dateien identisch.
- Arena hat einen eigenen Belohnungspfad ohne Progressionsbruch.

**Betroffene Dateien**

- `meta/masterprompt_v6.md`
- `core/spieler-handbuch.md`
- `core/sl-referenz.md`
- `gameplay/kampagnenstruktur.md`
- `systems/gameflow/speicher-fortsetzung.md`

---

### Issue 5 — Versionen, Ränge und Compliance-Reste aufräumen

**Titel**

`[P1] Versions-/Enum-Drift und tote Compliance-Pfade entfernen`

**Ziel**

Keine toten Flags, keine widersprüchlichen Enums, keine halb entfernten Legacy-Reste.

**Problem**

Es gibt sichtbare Drift bei:
- Versionsstrings
- Rangbezeichnungen (`Recruit` vs. `Rekrut`)
- Compliance-Mechanik (angeblich entfernt, aber an anderen Stellen noch als Flag/Hook/Notice vorhanden)

Das wirkt klein, ist aber klassischer „Vertrauensbruch-Code“: So etwas lässt Agenten und Maintainer permanent zögern, welcher Pfad noch gilt.

**Aufgaben**

1. Normalisiere Versionsbezug auf einen einzigen verlässlichen Wert.
2. Vereinheitliche Rang-Enums sprachlich.
3. Entferne tote Compliance-Notices und nicht mehr benutzte Save-Flags aus dem Runtime-Kanon.
4. Belasse reine Kompatibilität nur dort, wo sie technisch wirklich nötig ist.

**Akzeptanzkriterien**

- Keine widersprüchlichen Rang-Enums mehr.
- Keine kanonischen Save-Beispiele mit verwaisten Compliance-Flags.
- Dokumentation und Runtime sprechen dieselbe Sprache über den Startflow.

**Betroffene Dateien**

- `runtime.js`
- `package.json`
- `meta/masterprompt_v6.md`
- `core/sl-referenz.md`
- `systems/gameflow/speicher-fortsetzung.md`

---

### Issue 6 — Drift-Tests einbauen, damit so etwas nicht zurückkommt

**Titel**

`[P1] Contract-Tests gegen SSOT-Drift zwischen Masterprompt, WS-Modulen und Runtime ergänzen`

**Ziel**

Künftige Widersprüche sollen CI-basiert auffallen, bevor sie im Kanon landen.

**Problem**

Das Repo hat bereits Smoke-/Lint-Checks. Trotzdem sind offensichtliche Drift-Probleme in Schema, Terminologie und Progressionslogik durchgerutscht. Es fehlen also Prüfungen gegen **inhaltliche SSOT-Verletzungen**.

**Aufgaben**

1. Ergänze Lints/Tests für verbotene Legacy-Tokens in geladenen WS-Dateien.
2. Prüfe Würfel- und Progressions-Schlüsselbegriffe auf Widerspruch.
3. Prüfe Modellbegriffe (`GPT`, `Recruit`, alte Compliance-Flags, `economy.cu`, `party.characters[]`, `team.members[]` usw.).
4. Definiere eine kleine Liste kanonischer Invarianten, die maschinell prüfbar sind.

**Akzeptanzkriterien**

CI schlägt fehl, wenn in geladenen WS-Dateien zum Beispiel:
- `save_version: 6`
- `party.characters[]`
- `team.members[]`
- `economy.cu`
- `GPT`
- alte Compliance-Flags
- widersprüchliche Würfelformulierungen
auftauchen.

**Betroffene Dateien**

- `scripts/smoke.sh`
- neue oder bestehende Lint-Skripte unter `scripts/` oder `tools/`
- ggf. `AGENTS.md` zur Dokumentation neuer Invarianten

---

## Priorität B – Qualität und Identität des Spiels schärfen

### Issue 7 — Runtime-Kanon von Autorenessay trennen

**Titel**

`[P1] Wissensspeicher verschlanken: Runtime-Kanon und Autoren-/Leitungsessay trennen`

**Ziel**

Die KI-SL soll in den geladenen 20 Modulen vor allem Regeln, Prioritäten und klare Weltgrenzen sehen – nicht zu viele essayistische Nebensignale.

**Problem**

Mehrere geladene WS-Dateien enthalten zwar gutes Material, aber nicht alles ist gleich runtime-tauglich:
- Soundtrack-/Playlist-Ratschläge
- Regie-/Kamera-Metaphern
- längere GM-Essays
- Freizeit-/Slice-of-Life-Ideen
- Metaformulierungen für Directors/GM-Stil

Das ist nicht „schlecht“, aber es konkurriert im knappen Modellkontext mit wichtigeren Invarianten.

**Aufgaben**

1. Teile jede relevante WS-Datei in **Kanon/Runtime** und **Essay/Beispiele**.
2. Verschiebe lange Stil- oder Vorbereitungsratgeber in `docs/` oder `meta/`.
3. Lasse in geladenen WS-Dateien nur das, was die KI-SL in einer Session wirklich verlässlich wissen muss.
4. Halte Beispiele knapp und kanonisch.

**Akzeptanzkriterien**

- Geladene Module priorisieren Regeln, Grenzen, Dispatcher-Logik und Default-Ton.
- Ausführliche Essay-Passagen sind ausgelagert oder klar sekundär markiert.
- Wichtige Invarianten stehen sichtbar früher als Stimmungstexte.

**Betroffene Dateien**

- `systems/gameflow/cinematic-start.md`
- `systems/toolkit-gpt-spielleiter.md`
- `gameplay/kampagnenstruktur.md`
- weitere essaylastige WS-Dateien

---

### Issue 8 — Ton-Bibel für Core / Rift / Mythic sauber fixieren

**Titel**

`[P1] Ton-Kanon schärfen: Core-Thriller, Rift-Horror und optionale Mythic-Ebene trennen`

**Ziel**

Das Setting soll nicht „alles auf einmal“ sein, sondern bewusst skalieren.

**Problem**

ZEITRISS verspricht an seinen stärksten Stellen einen erwachsenen, bodenständigen, historisch geerdeten Agenten-Thriller. Gleichzeitig existieren im geladenen Kanon aber auch:
- Absolut-Kosmologie
- ferne Föderations-/Alien-Spuren
- historische und transhumane Extrem-Optionen
- Kryptiden-/Monster-Generatoren
- stark mythic/paranormale Einsprengsel

Dadurch verwischt die Identität: Ist ZEITRISS primär Technoir-Conspiracy, X-Files-Casefile, Cosmic-Metaphysik oder Kitchen-Sink-SF?

**Empfehlung**

Definiere drei Ebenen:
1. **Core-Ops Default:** grounded chrono-conspiracy thriller, rational lesbar, operativ, historisch geerdet
2. **Rift-Ops Default:** genau ein echtes Anomalie-Element pro Fall, investigativ, dunkler, aber nicht beliebig fantastisch
3. **Mythic-/Lore-Optional:** Absolut, Alien-Legenden, extreme Paracreatures, stärkere metaphysische Offenlegung

**Aufgaben**

1. Schreibe eine kurze Ton-Bibel.
2. Ordne jedes größere Lore-Element einer Ebene zu.
3. Gewichte Generatoren entsprechend.
4. Benenne optionale Layer explizit statt sie implizit mitzuschleppen.

**Akzeptanzkriterien**

- Spieler-Handbuch, Kampagnenübersicht und Generatoren sprechen denselben Ton-Kanon.
- Core bleibt lesbar und fokussiert.
- Rift bleibt besonders, statt alles paranormal zu machen.

**Betroffene Dateien**

- `core/spieler-handbuch.md`
- `gameplay/kampagnenuebersicht.md`
- `gameplay/kreative-generatoren-missionen.md`
- `gameplay/kreative-generatoren-begegnungen.md`
- ggf. Charakteroptionen / Einstiegsdoku

---

### Issue 9 — Psi endlich sauber optional oder sauber normalisieren

**Titel**

`[P1] Psi-Gating bereinigen: optionales Modul oder baseline Weltannahme – nicht beides gleichzeitig`

**Ziel**

Klarheit darüber, ob Psi eine seltene Zusatzschicht oder normaler Weltstandard ist.

**Problem**

Im Kanon wird Psi teils als optionales, seltenes Zusatzmodul beschrieben. Gleichzeitig verhalten sich andere Texte so, als seien Psi-Abschirmung, Psi-Widerstand, Psi-Anfälligkeit und psi-bezogene Infrastruktur quasi Standard.

Das erzeugt Weltlogik-Reibung.

**Empfehlung**

Bevorzugt für ZEITRISS-Stärke:
- **Psi bleibt optional und selten.**
- Default-Schutzsysteme werden neutraler beschrieben (`Neuro-Puffer`, `Anomalie-Puffer`, `Resonanzfilter`) statt als allgegenwärtige Psi-Infrastruktur.
- Wenn Psi aktiv ist, werden die erweiterten Begriffe und Regeln zugeschaltet.

**Aufgaben**

1. Definiere Baseline vs. Psi-Aktiv-Modus.
2. Überarbeite Rüstungen, Speziesbeschreibungen und Kampagnenübersicht entsprechend.
3. Stelle sicher, dass Nicht-Psi-Kampagnen keine unnötigen Psi-Grundannahmen tragen.

**Akzeptanzkriterien**

- Ohne aktiviertes Psi-Modul bleibt die Welt verständlich und vollständig.
- Psi-lastige Begriffe erscheinen nur dort, wo sie wirklich nötig sind.
- Standard-Equipment setzt keine Psi-Alltäglichkeit voraus.

**Betroffene Dateien**

- `systems/kp-kraefte-psi.md`
- `characters/ausruestung-cyberware.md`
- `characters/charaktererschaffung-optionen.md`
- `gameplay/kampagnenuebersicht.md`

---

### Issue 10 — Chronopolis ontologisch sauber machen

**Titel**

`[P1] Chronopolis-Regeln präzisieren: Instanzlogik, Persistenz und Service-Wrapper eindeutig definieren`

**Ziel**

Chronopolis soll als einer der coolsten Orte des Spiels **mehr** Kraft bekommen, nicht weniger – aber nur, wenn seine Logik scharf genug ist.

**Problem**

Aktuell ist Chronopolis zugleich:
- gescheiterte Episoden-Zeitlinie
- Kodex-instanzierte Gefahrenzone
- nicht Teil der echten Zeitlinie
- aber zugleich ein funktionsreicher Stadthub mit Händlern, Rang-Gating, Services, Fraktionsgerüchten und dauerhafter Beute-Persistenz

Das ist atmosphärisch stark, aber ontologisch unscharf.

**Empfehlung**

Definiere explizit:
- Was ist **instanzlokal**?
- Was wird beim Verlassen in HQ-Kanon überführt?
- Wie funktionieren Händler, Käufe, Kontakte und Intel?
- Welche Dinge sind echte Persistenz und welche nur Wrapper/Preview?

**Aufgaben**

1. Schreibe einen kurzen Chronopolis-Kanonblock.
2. Trenne `CITY`-Ereignisse von `HQ`-Services.
3. Definiere Persistenzregeln für Items, Kontakte, Intel, Käufe und Tod.
4. Gleiche alle Beschreibungen daran an.

**Akzeptanzkriterien**

- Kein Dokument widerspricht der Aussage „instanzierte Gefahrenzone“.
- Persistente Elemente sind klar benannt.
- Stadtflair bleibt erhalten, ohne die Logik des sicheren HQ zu verwischen.

**Betroffene Dateien**

- `core/spieler-handbuch.md`
- `gameplay/kampagnenuebersicht.md`
- `meta/masterprompt_v6.md`
- `systems/gameflow/speicher-fortsetzung.md`
- `gameplay/kampagnenstruktur.md`

---

### Issue 11 — Pacing-/Token-Budget als First-Class Feature einbauen

**Titel**

`[P1] Kompaktmodus und Szenen-Dichte-Presets ergänzen, damit Missionen im Chat nicht ausfransen`

**Ziel**

ZEITRISS soll auch in realen Chat-Sessions elegant spielbar bleiben, ohne seine filmische Wucht zu verlieren.

**Problem**

Der Kanon verlangt aktuell u. a.:
- 12 Szenen pro Core-Mission
- 14 pro Rift-Op
- meist mindestens 3 Absätze pro Szene
- bei Konflikten 4–6 Absätze
- zusätzliche HUD-, Intel-, Loot- und Optionsblöcke

Das ist atmosphärisch stark, kann aber im laufenden Chat extrem lang, teuer und ermüdend werden.

**Empfehlung**

Baue offizielle Presets ein:
- `compact` – 1–2 Absätze pro Szene, harte Verdichtung, ideal für Chat-Realität
- `standard` – aktueller Mittelweg
- `cinematic` – volle Wucht für Highlight-Sessions

Optional zusätzlich:
- 6-Szenen-Demo
- 8-Szenen-Standard-Mission
- 12-Szenen-Langform

**Aufgaben**

1. Ergänze `scene_density` und/oder `output_pace` um einen echten Kompaktmodus.
2. Passe Masterprompt, Handbuch und ggf. HUD-/Debrief-Regeln an.
3. Definiere, welche Blöcke in welchem Modus Pflicht sind.

**Akzeptanzkriterien**

- Der Runtime-Kanon unterstützt mindestens einen offiziell kompakten Spielmodus.
- Core-Missionen können ohne Stilbruch kürzer gefahren werden.
- Boss-, Debrief- und Save-Logik bleiben trotzdem lesbar.

**Betroffene Dateien**

- `meta/masterprompt_v6.md`
- `core/spieler-handbuch.md`
- `systems/toolkit-gpt-spielleiter.md`
- ggf. HUD-/Gameflow-Doku

---

## Priorität C – Politur, damit der Kanon sauber bleibt

### Issue 12 — Meta-/GPT-Leaks aus den Runtime-Modulen entfernen

**Titel**

`[P2] Terminologie-Sweep: GPT-/Director-Leaks aus geladenen WS-Dateien entfernen`

**Ziel**

In geladenen Runtime-Dateien soll nur die Spielsprache vorkommen: KI-SL, Spielleitung, Kodex – aber keine Modell- oder Meta-Leaks.

**Problem**

Einige geladene Texte sprechen noch von „GPT“ oder „Directors“, obwohl der Repo-eigene Agentenkanon genau das eigentlich vermeiden will.

**Aufgaben**

1. Suche alle geladenen WS-Dateien nach `GPT`, `LLM`, `Director`, ggf. ähnlichen Meta-Begriffen ab.
2. Ersetze sie durch `KI-SL`, `Spielleitung`, `Kodex`, `Spielrunde` oder passende Inworld-Formulierungen.
3. Lasse Meta-Begriffe nur in Dev-Dokumenten zu.

**Akzeptanzkriterien**

- In geladenen WS-Dateien taucht `GPT` nicht mehr als Runtime-Terminologie auf.
- Spielertexte bleiben vollständig immersiv.

**Betroffene Dateien**

- `gameplay/kampagnenuebersicht.md`
- `gameplay/kreative-generatoren-missionen.md`
- weitere WS-Dateien mit Meta-Begriffen

---

### Issue 13 — Katalog für Ausrüstung/Items/Implantate normalisieren

**Titel**

`[P2] Kanonischen Item-Registry-Layer für Gear, Rüstung, Implantate und Artefakte einführen`

**Ziel**

Equipment muss nicht nur cool klingen, sondern auch stabil serialisierbar, mergebar und agentenfreundlich sein.

**Problem**

Der Kanon fordert bereits ein einheitliches Exportformat wie `{name, type, tier}`. Gleichzeitig sind viele Gear- und Implantatbeschreibungen noch stark prose-basiert, variieren in Feldern, Aliasen und Bezeichnungslogik und sind dadurch schwer sauber zu serialisieren.

**Empfehlung**

Lege eine kanonische Registry an:
- `id`
- `display_name`
- `type`
- `tier`
- `cost`
- optionale `tags`
- optionale `altSkin`/Alias-Felder

**Aufgaben**

1. Normiere Standard-Gear, Implantate, Rüstungen und typische Artefakte.
2. Definiere, was im Save steht und was nur Anzeige ist.
3. Halte Freitextnamen weiterhin lesbar, aber auf Basis einer kanonischen Registry.

**Akzeptanzkriterien**

- Standard-Items lassen sich eindeutig serialisieren.
- Shop, Save, Debrief und Loadout reden über dieselben Gegenstände.
- Alias-/Skin-Namen zerstören die Serialisierung nicht mehr.

**Betroffene Dateien**

- `characters/ausruestung-cyberware.md`
- `systems/currency/cu-waehrungssystem.md`
- `meta/masterprompt_v6.md`
- ggf. interne Tools/Testskripte

---

## Direkt übernehmbarer Content

### Snippet 1 — Ton-Kanon für README / Spieler-Handbuch / SL-Referenz

```md
## Ton-Kanon von ZEITRISS

**ZEITRISS** ist zuerst ein erwachsener historischer Agenten-Thriller mit Zeitverschwörungen, operativen Dilemmata und physisch greifbaren Einsätzen. **Core-Ops** bleiben grundsätzlich geerdet: bizarre Vorfälle wirken real, erhalten aber im Regelfall eine technische, psychologische, politische oder temporale Erklärung. Das Spiel lebt hier von Infiltration, Spurensuche, Cover, Verrat, Druck und Entscheidungen mit Preis.

**Rift-Ops** öffnen die Tür für echte Anomalien, aber kontrolliert: pro Fall gilt idealerweise **ein** klares Para-Element als Zentrum des Mysteriums. Der Rest bleibt investigativ lesbar. Rift steht für dunklere Stimmung, stärkere Resonanz, Artefakte und Grenzfälle – nicht für beliebiges Fantasy-Crossover.

Alles, was darüber hinausgeht – offenere Kosmologie, stärkere Alien-Spuren, extreme Paracreatures, metaphysische Deutung des Absolut oder deutlich mythic-lastige Kampagnen – ist eine **optionale Lore-Schicht**, nicht der stille Default. So bleibt ZEITRISS im Kern fokussiert, erwachsen und unverwechselbar.
```

---

### Snippet 2 — Chronopolis sauber definieren

```md
## Chronopolis – Kanonische Kurzdefinition

**Chronopolis** ist keine normale Stadt in der echten Zeitlinie, sondern eine von Kodex instanziierte Fehlspur der laufenden Episode: die Welt, wie sie unter gescheiterten Bedingungen aussehen könnte. Sie ist **real genug, um euch zu verletzen, zu töten und Beute zu geben**, aber **nicht** identisch mit dem sicheren ITI-HQ und **nicht** Teil der stabilen Primärzeitlinie.

Was in Chronopolis geschieht, ist zunächst **instanzlokal**. Dauerhaft kanonisch wird nur, was die Crew **physisch exfiltriert**, bewusst in HQ-Systeme überträgt oder als bestätigtes Protokoll in den Deepsave übernimmt. Händler, Gerüchte, Sichtungen und Stadtereignisse dürfen stark variieren; echte Persistenz entsteht erst beim Transfer in den HQ-Kanon.

Damit bleibt Chronopolis gefährlich, begehrenswert und geheimnisvoll – ohne die Logik des HQ als sicheren Hafen zu verwischen.
```

---

### Snippet 3 — Save-Kanon kurz und brutal klar

```md
## Save-Kanon

Für Runtime, Load, Merge, Split und Spielerexport gilt genau **ein** kanonisches Save-Schema. Dieses Schema ist das einzige öffentlich dokumentierte Format. Legacy-Saves werden weiterhin unterstützt, aber ausschließlich als **Importpfad** behandelt.

Alle geladenen Wissensspeicher-Module, Save-Beispiele, Debrief-Texte und Merge-Regeln müssen dieses Schema **wortgleich** respektieren. Sobald ein Feld nur noch aus Kompatibilitätsgründen existiert, gehört es in Migration/Dev-Doku – nicht in den aktiven Runtime-Kanon.
```

---

## Empfohlene Reihenfolge für Codex/Agenten

1. Issue 1 – Save-Schema
2. Issue 2 – Wallet/Ökonomie
3. Issue 3 – Würfelkanon
4. Issue 4 – Px/Cluster/Arena
5. Issue 5 – Version/Enums/Compliance
6. Issue 6 – Drift-Tests
7. Issue 7 – Runtime-Kanon vs Essay
8. Issue 8 – Ton-Kanon
9. Issue 9 – Psi-Gating
10. Issue 10 – Chronopolis
11. Issue 11 – Pacing
12. Issue 12 – Terminologie-Sweep
13. Issue 13 – Item-Registry

