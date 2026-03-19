# ZEITRISS – Frischer Review-Durchlauf (Round 4)

## Gesamturteil

Der aktuelle Stand ist **deutlich stärker** als in den vorigen Durchläufen.
Der Mystery-/Alien-Kern funktioniert jetzt: UFO-/Grey-/Roswell-Vibes sind wieder da, aber die Texte lassen viel öfter die spätere Umdeutung „nicht Aliens, sondern Zukunft / Zeitversatz / posthumane Menschen“ zu.

Die größten verbleibenden Baustellen sind jetzt vor allem **SSOT-Drifts** und **Stil-Defaults**, nicht mehr die große Vision.

---

## Die fünf stärksten Restprobleme

### 1) Erzählperspektive / Voice-SSOT ist noch gespalten

**Problem:**

- Masterprompt fordert klar **Präsens + Du/Ihr**.
- `sl-referenz.md` setzt `gm_second_person` als Default.
- `speicher-fortsetzung.md` normalisiert Defaults aber auf `gm_third_person`.
- `toolkit-gpt-spielleiter.md` sperrt den Runtime-Stil sogar aktiv auf **dritte Person**.

**Warum das wichtig ist:**
Das ist kein Schönheitsfehler. Es verändert direkt, wie sich ZEITRISS anfühlt. Wenn die KI bei Save/Load oder je nach geladenem Modul zwischen 2nd und 3rd Person kippt, leidet der Kern deiner filmischen Immersion.

**Empfehlung:**
Eine einzige harte Wahrheit festziehen:

- Runtime-Default = `gm_second_person`
- Third Person nur als explizite Accessibility-/Style-Option
- `toolkit-gpt-spielleiter.md` auf dieselbe Linie heben
- `speicher-fortsetzung.md`-Defaults entsprechend korrigieren

**Copy-paste-Issue:**

**Titel:** `[P0] Voice-SSOT bereinigen: Runtime-Default überall auf gm_second_person / Du-Ihr festziehen`

**Beschreibung:**
Die Runtime ist stilistisch nicht SSOT-sauber. Aktuell konkurrieren vier Wahrheiten:

- Masterprompt: Präsens + Du/Ihr
- SL-Referenz: `gm_second_person` als Default
- Save-Doku: `gm_third_person` als Default
- Toolkit: Voice-Lock auf dritte Person

Das erzeugt echten Spielgefühl-Drift bei Save/Load und je nach Modulgewichtung.

**Aufgaben:**

1. In `systems/toolkit-gpt-spielleiter.md` den Voice-Lock auf **Second Person** umstellen:
   - Default `ui.voice_profile = gm_second_person`
   - `gm_third_person` nur optional / explizit gewählt
2. In `systems/gameflow/speicher-fortsetzung.md` Default-Migration für `voice_profile` auf `gm_second_person` setzen.
3. In `core/sl-referenz.md` bestätigen, dass nur `gm_second_person` Default ist und Third Person eine freiwillige Ausnahme bleibt.
4. Alle Save-Beispiele und UI-Preset-Beispiele auf dieselbe Voreinstellung ziehen.
5. Smoke-/Lint-Check ergänzen, der bei `gm_third_person` als unmarkiertem Default fehlschlägt.

**Akzeptanzkriterien:**

- Kein Runtime-Modul widerspricht mehr `Du/Ihr` als Standard.
- `gm_third_person` bleibt nutzbar, aber nie Default.
- Save/Load kippt die Erzählperspektive nicht mehr ungewollt.

---

### 2) v7-Save ist stark – aber die Doku hat noch Schattenstrukturen

**Problem:**
Der Masterprompt beschreibt ein klares v7-Modell (`v`, `zr`, `characters[]`, `attr`, `economy.hq_pool`, `arc.questions/hooks`).
In `speicher-fortsetzung.md` und teils `sl-referenz.md` tauchen aber noch kanonisch aussehende Beispiele/Helferschichten auf mit:

- `zr_version`
- Root-`character{}`
- `character.attributes`
- `characters[].attributes`
- `attr` vs. `attributes`
- `arc.open_seeds` / `open_questions` / `timeline`
- teils `loadout`-Strukturen außerhalb der SSOT-Beschreibung

Dazu kommt eine direkte Kollision in `sl-referenz.md`:

- einmal sind `character.attributes.SYS_runtime/SYS_used` und `cooldowns` Pflicht im HQ-Deepsave
- später heißt es, genau diese Laufzeitwerte würden **nicht** gespeichert.

**Warum das wichtig ist:**
Für Menschen ist das lesbar. Für Agenten/LLMs ist es Gift. Sobald ein Save-Modul zugleich SSOT und Hilfsschatten enthält, steigt das Risiko, dass die Spielleitung im falschen Format exportiert oder beim Load unnötig migriert.

**Empfehlung:**
Die Save-Doku braucht jetzt einen letzten harten Sweep:

- ein einziges öffentliches v7-Zielmodell
- alles andere explizit als Legacy-/Helper-Bridge markieren oder aus dem Runtime-Kanon entfernen

**Copy-paste-Issue:**

**Titel:** `[P0] Save-SSOT final härten: Helper-/Legacy-Schatten aus Runtime-Doku entfernen oder klar abkapseln`

**Beschreibung:**
Obwohl das v7-Zielmodell inzwischen klar ist, enthalten geladene Runtime-Dokumente noch konkurrierende Formen (`zr_version`, `character{}`, `attributes`, alte Arc-Pfade, persistierte Runtime-Felder). Das ist für KI-Spielleitung und Save/Load-Export unnötig riskant.

**Aufgaben:**

1. `systems/gameflow/speicher-fortsetzung.md` in zwei sauber getrennte Bereiche teilen:
   - **Kanonisches v7-Zielmodell**
   - **Legacy-/Import-Bridges**
2. Alle kanonischen Beispiele ausschließlich im SSOT-Format zeigen:
   - `v`
   - `zr`
   - `characters[]`
   - `attr`
   - `economy.hq_pool`
   - `arc.questions` / `arc.hooks`
3. Root-`character{}` nur noch als klar markierte Laufzeit-/Bridge-Struktur aufführen oder komplett aus Runtime-Texten entfernen.
4. `sl-referenz.md` bereinigen: entscheiden, ob `SYS_runtime`, `SYS_used`, `cooldowns` persistieren oder Laufzeit-only bleiben.
5. Alle Save-Beispiele gegen dieselbe Feldliste validieren.

**Akzeptanzkriterien:**

- Ein Leser kann in 30 Sekunden erkennen, wie ein kanonischer v7-Save aussieht.
- Kein kanonisches Beispiel nutzt gleichzeitig `attr` und `attributes`.
- Kein kanonisches Beispiel mischt `zr` und `zr_version`.
- Persistenz von `cooldowns` / `SYS_runtime` / `SYS_used` ist eindeutig.

---

### 3) Paradoxon ist fast perfekt – aber `kampagnenstruktur.md` baut wieder Optionalschleier ein

**Problem:**
Im Spieler-Handbuch ist Px inzwischen genau richtig: ein **fester, deterministischer Progressionspfad**.
Aber `kampagnenstruktur.md` führt wieder Unschärfe ein:

- optionaler **Index-Merge-Schalter** bei Paralleltrupps
- optionaler **±1-Jitter** auf die Schwelle
- **Kurzmissionen zählen nur halb** / jeder zweite Einsatz = +1

**Warum das wichtig ist:**
Damit verlierst du genau die Eleganz, die ZEITRISS an dieser Stelle inzwischen hat. Gerade Px sollte sich wie ein verlässlicher Taktgeber anfühlen, nicht wie ein optional konfigurierbarer Nebel.

**Empfehlung:**
Px konsequent als SSOT-Loop behandeln. Hausregeln entweder ganz raus aus Runtime-Modulen oder klar in einen „Optional / Dev / Hausregel“-Kasten, der nicht als Live-Regel verstanden werden kann.

**Copy-paste-Issue:**

**Titel:** `[P0] Px-SSOT schließen: Jitter, Halbzählung und optionale Merge-Schalter aus Runtime-Kanon entfernen`

**Beschreibung:**
Der Paradoxon-Index ist in den Core-Texten bereits als fester, deterministischer Belohnungs-Loop verankert. `kampagnenstruktur.md` bringt aktuell wieder optionale Abweichungen rein (Jitter, halbierte Kurzmissionen, optionaler Index-Merge-Schalter). Das schwächt die Klarheit des Systems.

**Aufgaben:**

1. In `gameplay/kampagnenstruktur.md` die Passagen zu
   - `Index-Merge-Schalter`
   - `±1-Jitter`
   - `Kurzmissionen zählen erst nach zwei Einsätzen`
     aus dem Runtime-Kanon entfernen oder in einen explizit nicht-kanonischen Hausregelblock verschieben.
2. Überall klarstellen:
   - Px folgt ausschließlich der TEMP-Tabelle
   - kein Zufallsjitter
   - keine Sonderzählung für Kurzmissionen
   - Merge folgt dem fest definierten Präzedenzgraphen
3. Falls Paralleltrupps relevant bleiben: exakt eine Merge-Regel definieren, keine Schalterlogik.

**Akzeptanzkriterien:**

- Px verhält sich überall gleich.
- Kein geladenes Runtime-Modul schlägt zufällige oder alternative Px-Zählung vor.
- Merge-Verhalten von Px ist ohne Optionen beschrieben.

---

### 4) Ruf/Tier ist fast sauber – aber im Toolkit sitzt noch ein alter Fraktionssatz

**Problem:**
In `charaktererschaffung-grundlagen.md` ist die neue Ruflogik sauber: `reputation.iti` = operativer Institutsruf, Fraktionsruf = Politik / Story.
Im Toolkit steht aber noch sinngemäß: **Der Hauptfraktionsruf (ITI/Ordo) bestimmt den Tier-Zugang.**

**Warum das wichtig ist:**
Das ist genau der alte Drift, den du schon fast aus dem Repo rausgezogen hast. Und ausgerechnet im Toolkit ist so ein Satz gefährlich, weil dort Beispiele leicht als Live-Verhalten übernommen werden.

**Empfehlung:**
Diesen Satz sofort korrigieren. Tier/Lizenzzugang darf nur an `reputation.iti` hängen.

**Copy-paste-Issue:**

**Titel:** `[P1] Toolkit auf neue Ruflogik ziehen: Tier-Zugang nur über reputation.iti`

**Beschreibung:**
Die neue Ruf-/Tier-Logik ist an mehreren Stellen schon sauber umgesetzt, aber im Toolkit existiert noch eine Formulierung, die den Tier-Zugang am „Hauptfraktionsruf (ITI/Ordo)“ festmacht. Das widerspricht dem neuen SSOT.

**Aufgaben:**

1. In `systems/toolkit-gpt-spielleiter.md` alle Formulierungen ersetzen, die Tier-Zugang über Fraktionsruf oder „Hauptfraktionsruf“ erklären.
2. Überall die SSOT-Linie verwenden:
   - `reputation.iti` = Rang, Lizenz-Tier, formaler Zugriff
   - `reputation.factions.*` = Story, Rabatte, Misstrauen, Sonderpfade
3. Debrief-Beispiele prüfen und ggf. auf `ITI-Ruf` umschreiben.

**Akzeptanzkriterien:**

- Kein Runtime-Modul leitet Tier-Zugang mehr aus Fraktionsruf ab.
- Debrief/Toolkit/Handbuch benutzen dieselbe Rufsprache.

---

### 5) Der Mystery-Kern sitzt – aber das frühe „Absolut“ ist noch etwas zu nackig

**Problem:**
Der Alien-/Mystery-Kern ist inzwischen stark. Aber der frühe Einstieg benennt weiterhin sehr direkt:

- Bewusstsein aus dem Absolut
- Rekrutierung aus dem Absolut
- Kampagnenübersicht mit deutlicher Absolut-Erklärung

**Warum das wichtig ist:**
Das ist nicht falsch. Aber es nimmt dem Setting in der Frühphase ein bisschen von seiner bodenständigen Härte und verschiebt den Erstkontakt schnell in Richtung Metaphysik. Gerade wenn du willst, dass Spieler zuerst UFO-/Grey-/Roswell-/Zukunfts-Fremdheit erleben, sollte Deep Lore etwas stärker als **ITI-Arbeitshypothese** statt als offen präsentierte Weltwahrheit erscheinen.

**Empfehlung:**
Nicht streichen — nur rahmen. Ein einziger Satz reicht oft:

> **ITI-intern gilt „Absolut“ nicht als Glaube, sondern als Arbeitsbegriff für eine bis heute unvollständig verstandene Grenzphysik.**

Damit bleibt die Tiefe erhalten, aber der frühe Ton bleibt erwachsener und nüchterner.

**Copy-paste-Issue:**

**Titel:** `[P1] Deep-Lore rahmen: „Absolut“ in frühen Spielertexten als ITI-Arbeitshypothese markieren`

**Beschreibung:**
Die frühe Onboarding-Schicht benennt das „Absolut“ bereits recht direkt. Das ist lore-seitig interessant, kann aber die bodenständige Mystery-Wirkung unnötig früh metaphysisch färben.

**Aufgaben:**

1. In `core/spieler-handbuch.md`, `characters/charaktererschaffung-grundlagen.md` und ggf. `gameplay/kampagnenuebersicht.md` jeweils einen Rahmensatz ergänzen, dass „Absolut“ ein ITI-Arbeitsbegriff / Forschungsmodell ist.
2. Keine große Umformulierung nötig; kleine, präzise Klammer genügt.
3. Prüfen, ob frühe Spielertexte weniger wie geoffenbarte Kosmologie und mehr wie kontrollierte Instituts-Sprache klingen.

**Akzeptanzkriterien:**

- Deep Lore bleibt vorhanden.
- Onboarding klingt nüchterner.
- Mystery-/Alien-/Zeitversatz-Vibes bleiben im Vordergrund.

---

## Zwei kleine, starke Ideen mit wenig Aufwand

### Idee 1 – **Signaturtell** für Boss- und Rift-Showdowns

**Warum:**
Ihr habt schon Foreshadow-Gates. Was noch fehlt, ist ein **greifbarer taktischer Payoff** für gutes Vorarbeiten.

**Regel in einem Satz:**
Wenn das Team vor Szene 10 den **Signaturtell** des Gegners korrekt identifiziert, darf es in der Boss-Szene **einmal** eine Signaturfähigkeit des Bosses abschwächen, verzögern oder den Eröffnungszug an sich ziehen.

**Mini-Regeltext (direkt übernehmbar):**

### Signaturtell (Boss-/Rift-Payoff)

Vor jedem Mini-, Episoden- oder Rift-Boss existiert genau **ein verwertbarer Signaturtell**: eine körperliche Schwäche, ein wiederkehrendes Bewegungsmuster, ein technischer Taktfehler, eine Reaktion auf Material, Licht, Lärm, Temperatur oder Zeitmarker.

Wird dieser Tell **vor Szene 10** durch Foreshadow, Intel oder Forensik korrekt erkannt und im Spiel benannt, erhält das Team in der Boss-Szene **einmalig einen taktischen Vorteil**. Beispiele:

- Boss-Signaturfähigkeit startet **eine Runde später**,
- erstes Defensivfenster des Bosses fällt weg,
- Team erhält **+1 auf den Eröffnungszug** oder
- ein Boss-DR-/Overflow-Effekt wird **für genau einen Treffer** ignoriert.

Der Signaturtell ersetzt keine Boss-Mechanik, sondern macht Vorbereitung spürbar. ZEITRISS belohnt damit gutes Lesen eines Falls, nicht nur reinen Schadensoutput.

---

### Idee 2 – **Forensik-Dreieck** für Rift-Casefiles

**Warum:**
Das passt perfekt zu deinem Kern „erst Aliens/Mystery denken, dann plausibel umdeuten“.

**Regel in einem Satz:**
Jede Rift-Op hat drei Beweisachsen: **Bio**, **Material**, **Temporal**. Wenn das Team zwei davon sauber sichert, bekommt es den echten Read des Falls plus einen mechanischen Bonus im Finale oder Debrief.

**Mini-Regeltext (direkt übernehmbar):**

### Forensik-Dreieck (Rift-Casefiles)

Jede Rift-Op besitzt drei mögliche Beweisachsen:

- **Bio** – Gewebe, DNA, Sekrete, Knochen, Spuren am Opfer oder Tatort
- **Material** – Legierungen, Werkstoffe, Rückstände, Gerätefragmente, Schnittbilder
- **Temporal** – Driftmarker, Echoverzögerungen, Ankerfehler, Zeitversatzmuster

Sichert das Team **mindestens 2 von 3** Achsen sauber, gilt der Fall als **sauber klassifiziert**. Die Spielleitung gibt dann den eigentlichen Kern des Phänomens klar frei (z. B. „keine Alien-Biologie, sondern posthumane Hülle“, „keine dämonische Manifestation, sondern Zeitversatz + Bio-Adaptionsprojekt“).

**Payoff bei 2/3 oder 3/3:**

- ein **Boss-Signaturtell** wird offengelegt,
- oder **+1 Schritt** auf Debrief-/Research-Qualität,
- oder **sauberer Exfil-Bonus** / reduzierter Heat,
- oder ein zusätzlicher **Kodex-Hinweis**, der den Aha-Moment vorbereitet.

So bleibt Mystery erhalten, aber gute Ermittlungsarbeit kippt den Fall sichtbar von Mythos zu belastbarer Wahrheit.

---

## Ein einzelner Satz mit viel Wirkung

Wenn du nur **einen** Satz nachschärfen willst, würde ich diesen setzen:

> **Was im ersten Zugriff wie Fremdheit wirkt, entpuppt sich in ZEITRISS oft nicht als das Andere, sondern als etwas Verstörenderes: eine zu weit entfernte, aber immer noch menschliche Zukunft.**

Der Satz bündelt genau deine Stärke.

---

## Kurzfazit

ZEITRISS ist jetzt an einem Punkt, an dem die letzten Verbesserungen weniger „Welt retten“ und mehr **Klinge schärfen** sind.

Meine Reihenfolge wäre:

1. Voice-SSOT fixen
2. Save-SSOT final härten
3. Px-Optionalität aus Runtime ziehen
4. Toolkit-Rufsatz korrigieren
5. Absolut weich rahmen
6. Danach Signaturtell + Forensik-Dreieck ergänzen
