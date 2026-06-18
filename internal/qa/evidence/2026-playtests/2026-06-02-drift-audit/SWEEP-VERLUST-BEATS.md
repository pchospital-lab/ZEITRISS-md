# Sweep — Verlust-/Risiko-Beats

> Audit-Worker: sweep-verlust-beats · Datum: 2026-06-02 · Repo @ main
> Reiner LESE-Audit. Keine Mechanik-Änderung, nur Erlebnis-Rahmung als Vorschlag.
> Messlatte: Belohnungs-Achse hat 6 Beat-Gates (Px-Resonanz, Level-Up, Aufstieg,
> Lizenz, Prestige + Research) → die negative Achse soll dasselbe Erlebnis-Niveau bekommen.
> Anti-Litanei: Jeder neue Beat-Vorschlag gehorcht dem Beat-Dosierungs-Pflichtgate
> (masterprompt §F, Z. 472–477: max 1 voller Beat + Rest Kodex-Zeilen pro Phase).

---

## Pro Achse (Status + Fundstelle + Beat-Bewertung)

### 1. Heat — **STILL** (größte Lücke)

**Mechanisch:** Heat ist ein Epochen-Zähler, der an vielen Stellen `+1` tickt:
- `meta/masterprompt_v6.md:239` (Spotlight-Beat → Heat +1)
- `meta/masterprompt_v6.md:323` (Anachronismus-Sichtung → Heat +1 für Crew)
- `gameplay/kampagnenstruktur.md:975` („**Heat +1** in der Epoche")
- `gameplay/kampagnenstruktur.md:1864` („erzeugt Heat +1 und eine Fraktionsnotiz")
- HUD zeigt ihn als `Heat 0/5` (`masterprompt_v6.md:695`)

**Was bewirkt Heat?** — Hier ist das Problem: **fast nichts Sichtbares, und nirgends ein Beat.**
Die einzige dokumentierte mechanische Heat-Konsequenz im Spiel ist eine *Generator-Zeile*:
`gameplay/kreative-generatoren-begegnungen.md:203` — *„Osmanische Geheimpolizei: … **Verstärkung ab Heat 3**. +1 Gegner je sichtbare Psi-Nutzung"*. Das ist ein lokaler Encounter-Tag, **keine globale Heat-Schwelle**.

Es gibt **keine zentrale Heat-Eskalations-Spezifikation** (anders als Psi-Heat, das in `systems/kp-kraefte-psi.md:1019–1025` eine volle Schwellentabelle mit SG-Mali/Reboot hat). Welt-Heat hat:
- keine dokumentierte Schwellenwirkung (kein „ab Heat X passiert Y"),
- **keinen Eskalations-Beat** („die Welt wird wachsamer, Fahndung läuft an"),
- **keine Debrief-/HQ-Thematisierung** — Negativ-Test bestätigt: kein einziger Treffer für Heat im Debrief- oder HQ-Kontext (außer dem trockenen Spotlight-Tick).

**Beat-Bewertung:** **STILL.** Heat ist ein stiller Zähler, der hochläuft und im Spielgefühl folgenlos bleibt — der Spieler sieht `Heat 3/5` im HUD und es bedeutet nichts Erlebbares. Das ist die **deutlichste Asymmetrie** zur Belohnungs-Achse: Px hatte exakt dasselbe Problem („spielt eigentlich gar keine Rolle mehr"), wurde aber durch das Px-Resonanz-Pflichtgate behoben. Heat hat denselben Fix noch nicht bekommen.

---

### 2. Fraktionsinterventionen — **TEILWEISE** (Eingriff = Beat, Übergang = still)

**Fundstelle:** `gameplay/kampagnenstruktur.md:196–210` (§Fraktionsinterventionen), `:995–1009` (Spotlight-Kaskade triggert `aktiver Eingriff`), `:1385` (`logs.fr_interventions[]`).

**Zitat (Mission-Start-Wurf):** *„Zu Missionsbeginn auf Intervention würfeln (`1-2` ruhig, `3-4` Beobachter, `5-6` aktiver Eingriff)."* (`:199`)

**Zitat (aktiver Eingriff IST ein Beat):** *„Bei aktivem Eingriff zwingt die Fraktion mindestens **eine volle Szene Gegenwehr** (Hinterhalt, Sperrfeuer, Blockade). Ergebnis `5-6` ist kein Flavor-Tag, sondern löst einen echten Angriff aus, bevor die Spielenden freie Aktionen haben."* (`:200–202`)

**Beat-Bewertung:** **TEILWEISE.**
- `aktiver Eingriff` (5-6) ist **bereits ein erlebbarer Beat** — volle Szene Gegenwehr, das ist gut. ✅
- **Aber:** Der Wurf ist ein **einmaliger Mission-Start-Würfel** (`:199`), und der `Beobachter`-Status (3-4) ist **still**: er wird als `observer: true` ins Save geloggt (`:207`), aber es gibt **keinen Übergangs-Beat** „die Gegenseite beobachtet euch — und entscheidet jetzt, einzugreifen". Flos Kern-Frage — *ist der Übergang ruhig→Beobachter→aktiver Eingriff als spürbarer Beat inszeniert, dass die Gegenseite **sichtbar auf Spielerfolg reagiert**?* — lautet: **Nein.** Der Übergang ist ein verdeckter Würfel + Log-Eintrag. Eine Fraktion auf `Beobachter` eskaliert nur über die Spotlight-Kaskade (`:995`) zu `aktiver Eingriff`, **nicht** als Reaktion auf Spielererfolg/Lautstärke während der Mission.
- Es fehlt: das MMO-Gefühl „je besser ihr seid, desto nervöser wird die Gegenseite". Aktuell ist die Fraktions-Haltung zu Missionsbeginn gewürfelt und danach statisch (außer Spotlight-Trigger).

---

### 3. Stress — **TEILWEISE → eher STILL** (Anstieg gut beschrieben, Schwellen still)

**Fundstelle:** `characters/zustaende.md:305–345` (§Stress, Skala 0–10).

**Zitat (Schwellen existieren):** *„Klettert das Konto über Schwellen, treten **Effekte** ein: bei 5 Punkten etwa der Zustand **„Angespannt"** (-1 auf soziale oder präzise Proben). Bei 10 Punkten droht ein **Kurzzeit-Zusammenbruch** — Panik, Flucht oder Starre."* (`zustaende.md:319–321`)

**Zitat (Anstieg als Erlebnis ist vorgesehen):** *„Die SL kann Stresspunkte verdeckt führen und nur Effekte beschreiben („Eure Hände zittern…") oder offen kommunizieren („Stress 5/10 — deutliche Anspannung.")."* (`zustaende.md:325–327`)

**Beat-Bewertung:** **TEILWEISE.**
- Stress hat **Schwellen-Konsequenzen** (5 = Angespannt/-1, 10 = Panik) — das ist mechanisch da. ✅
- Die *„Hände zittern"*-Erlebnis-Rahmung ist als **Möglichkeit** beschrieben („Die SL **kann**…"), aber **nicht als Pflicht-Beat**. Es gibt kein Stress-Pflichtgate, das den Schwellen-Übergang (besonders 4→5 „Angespannt" und 9→10 „Zusammenbruch") als spürbaren Moment erzwingt. Im dichten Action-Loop fällt die optionale Rahmung leicht weg → Stress wird zur stillen HUD-Zahl, die irgendwann einen -1-Malus auswirft, ohne dass der Spieler den Kipp-Moment *erlebt*.
- Stress-Anstieg `+1` in den Spotlight-/Anachronismus-Beats ist bereits Teil eines Beats (gut), aber der **eigenständige Schwellen-Übergang** (Crew-Mitglied kippt in „Angespannt"/Panik) ist nicht inszeniert.

---

### 4. Tod / 0 LP — **HAT-BEAT** ✅

**Fundstelle:** `meta/masterprompt_v6.md:941–946`.

**Zitat:** *„Bei 0 LP → Szene stoppen. Spieler wählt: (1) **Respawn:** Letzten Save laden… (2) **Heroischer Tod:** Filmisches Ende inszenieren, Final-Save (`"status":"deceased"`), Abschlussbericht…"* (`:941–945`); ergänzt durch *„das filmische Ende ist die Lore-Verankerung"* (`:890`, `core/sl-referenz.md:591–593`).

**Beat-Bewertung:** **HAT-BEAT.** Tod ist dramaturgisch inszeniert — „filmisches Ende", Abschlussbericht, explizit als Lore-Verankerung gerahmt. Das ist das stärkste Stück der negativen Achse. Kein Patch-Bedarf. (Anmerkung: Es ist kein *Pflicht*gate im selben Format wie die Reward-Gates, aber die Inszenierung ist klar vorgeschrieben.)

---

### 5. Mission-Scheitern — **TEILWEISE → STILL im Debrief**

**Fundstelle:** `meta/masterprompt_v6.md:224` (ITI-Notfall-Exfil = Mission gescheitert, Debrief-Score reduziert), `gameplay/kampagnenstruktur.md:851–859` (Debrief-Spiegel-Pflicht), `:903` (Hot-Exfil-Misslingen → Stress/Heat/CU/Story statt Px).

**Zitat (Score-Screen hakt ab):** *„Score-Screen hakt die im Core-Briefing gesetzten Ziele pro Ziel ab (✓/✗). Verfehlte Ziele werden in `arc.hooks[]` als Folgespur abgelegt…"* (`kampagnenstruktur.md:851–854`).

**Zitat (Briefing-Gate-Spiegel):** *„Verfehlte Ziele werden nicht still geschluckt — sie tauchen als Folgespur in `arc.hooks[]` wieder auf…"* (`masterprompt_v6.md`, Briefing-Output-Pflichtgate §Debrief-Spiegel).

**Beat-Bewertung:** **TEILWEISE — und hier ist die Asymmetrie scharf.**
- Verfehlte Ziele werden **abgehakt** (✓/✗) und als Folgespur geloggt — das ist Buchhaltung, nicht Erlebnis. ✅ für Continuity, ❌ für Beat.
- **Spiegelt der Debrief Misserfolg so erlebbar wie Erfolg?** **Nein.** Die Belohnungs-Seite des Debrief ist beat-reich (Px-Resonanz-Beat, Level-Up-Beat, Aufstiegs-Beat — alle Pflicht, alle „2–4 Sätze diegetisch"). Die Misserfolgs-Seite ist ein **rotes ✗ + Log-Eintrag**. Es gibt **keinen Scheiterns-Beat**, der spürbar macht *„das ITI ist unzufrieden / die Zeitlinie hat Schaden genommen / das hätte schiefgehen können und ist es"*. Der ITI-Notfall-Exfil (`:224`) reduziert nur den Score-Wert.
- Das ist genau Flos „ein MMO lebt auch vom *das hätte schiefgehen können*" — und genau das fehlt im Debrief als Erlebnis.

---

### 6. Anachronismus-Sichtung — **HAT-BEAT** ✅ (bewusst gedeckelt)

**Fundstelle:** `meta/masterprompt_v6.md:323` (Sichtbarkeits-Reibung im Feld).

**Zitat:** *„spielt die KI-SL **einmalig pro Vorfall** eine narrative Reibung aus dem Exfil-Stress-Vokabular: **Stress +1**…, **Heat +1**…, ein `logs.notes[]`-Eintrag… **Keine Eskalation** über mehrere Beats… das ist ein Beat, kein Status-Effekt. Im Debrief taucht das als Mini-Echo auf…"* (`:323`).

**Beat-Bewertung:** **HAT-BEAT.** Bereits sauber als einmaliger Beat formuliert, mit Feld-Reibung + Debrief-Mini-Echo + bewusster Anti-Eskalations-Deckelung. Gehorcht schon der Dosierungs-Logik. Kein Patch-Bedarf — Vorbild, wie ein kleiner Verlust-Beat aussehen soll.

---

### 7. Px bei Eskalation — **DESIGN BESTÄTIGT, konsistent** ✅

**Fundstelle:** `meta/masterprompt_v6.md:521`, plus Querschnitt.

**Zitat:** *„Kein Px-Abzug bei Eskalation: Fehler erzeugen Drucksignale (Heat/Noise/Timeline-Echo/Fraktionsreaktionen), nicht negative Px-Mechanik."* (`:521`).

**Konsistenz-Prüfung — durchgehalten:**
- Spotlight-Beat: *„Keine Px-Veränderung"* (`:239`, `kampagnenstruktur.md:973–978`).
- Anachronismus: *„Keine Px-Änderung (Px ist Belohnung, nicht Strafe)"* (`:323`).
- Hot-Exfil-Misslingen: *„keinen automatischen Px-Abzug… sondern eskaliert Stress/Heat/CU- und Storyfolgen"* (`kampagnenstruktur.md:903`).
- Spieler-Handbuch: *„im Default **keinen Px** — Konsequenzen laufen über CU, Stress, Heat"* (`core/spieler-handbuch.md:41`).

**Bewertung:** **BESTÄTIGT.** Die negative Achse läuft konsequent über Heat/Stress/Fraktion/CU/Story, **nicht** über Px-Strafe. Konsistent über alle Dateien. Px bleibt reines Belohnungssystem. ✅ (Optionale Px-Verlust-Hausregel an zwei Stellen erwähnt — bricht die Konsistenz nicht, weil explizit als Opt-in markiert.)

---

## Asymmetrie-Analyse (Belohnung vs. Verlust)

**Belohnungs-Achse: 6 Beat-Gates** (alle Pflicht, alle diegetisch inszeniert):
1. Px-Resonanz-Pflichtgate (`masterprompt:521`)
2. Level-Up-Belohnungs-Pflichtgate (`:655`)
3. Aufstiegs-Beat-Pflichtgate / Ruf+Rang (`:669`)
4. Lizenz-Tier-Freischalt-Beat (Teil von §F / `:98`)
5. Prestige-Meilenstein-Beat (`:659`)
6. Research-Tick/-ready (Teil von §F)

**Verlust-Achse: ~2 echte Beat-Gates**
- Tod/0 LP (HAT-BEAT, aber kein „Pflichtgate"-Format) ✅
- Anachronismus-Sichtung (HAT-BEAT, klein) ✅
- *(Spotlight/Exfil-Stress ist streng genommen ein Risiko-Beat-Gate — gehört aber zur Exfil-Phase, nicht zur generellen Verlust-Achse. Wenn man es mitzählt: ~3.)*

**Gefälle = 6 : ~2.** Die negative Achse ist erlebnis-ärmer um den Faktor 3.

**Wo die Asymmetrie am größten ist (priorisiert):**

1. **Heat** — größte Lücke. Voll stiller Zähler, kein Sinn, keine Schwelle, kein Beat, keine Debrief-Thematisierung. Exakt das Px-Problem vor dem Px-Resonanz-Patch. **Der Px-Fix ist die Blaupause.**
2. **Mission-Scheitern im Debrief** — zweitgrößte Lücke. Erfolgs-Debrief = 6 Beat-Gates, Misserfolgs-Debrief = ein rotes ✗. Genau die „das hätte schiefgehen können"-Achse, die Flo meint.
3. **Fraktions-Übergang ruhig→Beobachter→aktiv** — die Gegenseite reagiert nicht *sichtbar* auf Spielerfolg; der `Beobachter`-Status ist ein stiller Würfel/Log.
4. **Stress-Schwellen-Übergang** — Schwellen da, aber Kipp-Moment (→Angespannt, →Panik) nur optional gerahmt, kein Pflicht-Beat.

---

## Patch-Vorschläge priorisiert

> Leitsatz Flo: chirurgische Fokus-Sätze, kein Umbau, **keine Zahlen/Caps ändern**.
> Alle Vorschläge: nur Erlebnis-Rahmung, jeder gehorcht dem Beat-Dosierungs-Pflichtgate (§F).
> Wichtig: Bei Gleichzeitigkeit im Debrief muss die Rang-Liste in §F um die negativen Beats
> ergänzt werden (sonst kollidieren Verlust- und Belohnungs-Beats undokumentiert).

### P1 — Heat-Eskalations-Pflichtgate (höchste Priorität, Px-Blaupause)
Neuer §F-Beat analog Px-Resonanz: **Heat ist mechanisch ein Druckzähler, war aber im Spiel zu unsichtbar.** In-World-Logik: *Je höher Heat in einer Epoche, desto wachsamer wird die Welt — Fahndung, Patrouillendichte, misstrauische Blicke.* Drei Pflicht-Beats, **ohne neue Zahlen**:
- **Heat-Anstiegs-Rahmung:** Wenn Heat in einer Szene steigt, **nicht** nur `Heat +1` ticken, sondern *einmal* die wachsamere Welt zeigen (ein Aushang mit Phantombild, zwei Gendarmen mehr an der Ecke, ein Funkspruch im Hintergrund). Gehorcht Dosierung: max. 1 voller Heat-Beat pro Szene, sonst Kodex-Zeile.
- **Heat-Debrief-Thematisierung:** Steht die Crew mit hohem Heat aus der Mission, **thematisiert der Debrief das** („In dieser Epoche hängt jetzt euer Schatten — die nächste Operation hier wird heißer"). Spiegelbild zum Px-Resonanz-Debrief-Beat.
- **Schwellen-Konsequenz nur narrativ rahmen:** Die bereits existierende Generator-Konsequenz (Verstärkung ab Heat 3, `begegnungen.md:203`) wird als spürbarer Welt-Zustand gerahmt, nicht als stiller +1-Gegner. **Keine** neue globale Heat-Tabelle erfinden — nur das Vorhandene erlebbar machen.

### P2 — Scheiterns-Spiegel-Beat im Debrief
Ergänzung zur Debrief-Spiegel-Pflicht (`kampagnenstruktur.md:851`): Wenn Hauptziel = ✗ (oder ITI-Notfall-Exfil), spielt der Debrief **einen** Misserfolgs-Beat aus, der so erlebbar ist wie der Px-Resonanz-Beat bei Erfolg — *„das ITI ist unzufrieden / die Zeitlinie trägt einen Riss davon / die Folgespur ist diesmal eine Wunde, kein Bonus"*. **Keine** neue Strafmechanik, **kein** Px-Abzug (Konsistenz §521) — nur Rahmung des bereits geloggten ✗. Gehorcht Dosierung: ersetzt im Misserfolgs-Fall den vollen Beat-Slot, der bei Erfolg an Px/Level ginge.

### P3 — Fraktions-Reaktions-Beat (Beobachter wird sichtbar)
Erweiterung §Fraktionsinterventionen (`:196`): Bei Status `Beobachter` (3-4) **einen** stillen-Beobachtung-Beat erlauben, der bei deutlichem Spielerfolg/Lautstärke sichtbar wird (*„der Mann mit dem grauen Mantel notiert etwas und verschwindet"*) — die Gegenseite reagiert **spürbar**. Übergang Beobachter→aktiv bleibt mechanisch wie ist (Spotlight-Kaskade/Würfel), bekommt aber einen Ankündigungs-Beat statt stillem Log. Chirurgisch: ein Satz Reaktions-Inszenierung, keine neue Würfeltabelle.

### P4 — Stress-Kipp-Beat (Schwellen-Übergang als Pflicht statt Option)
Härtung der bestehenden „Hände zittern"-Rahmung (`zustaende.md:325`) von *kann* zu *Pflicht beim Schwellen-Übergang*: Wenn ein Charakter 4→5 („Angespannt") oder →10 (Panik) kippt, **einmal** den Moment ausspielen statt nur den HUD-Wert zu erhöhen. **Keine** Skala-/Malus-Änderung (5=-1, 10=Panik bleiben). Gehorcht Dosierung.

---

## Was schon HAT-BEAT ist (nicht anfassen)

- **Tod / 0 LP** (`masterprompt:941`) — filmisches Ende, Lore-Verankerung. ✅
- **Anachronismus-Sichtung** (`masterprompt:323`) — einmaliger Feld-Beat + Debrief-Echo, bewusst gedeckelt. ✅ Vorbild für kleine Verlust-Beats.
- **Aktiver Fraktions-Eingriff (5-6)** (`kampagnenstruktur:200`) — volle Szene Gegenwehr. ✅ (nur der *Übergang* dahin ist still.)
- **Exfil-Stress / Spotlight-Eskalation** (`masterprompt:239`, `kampagnenstruktur:968–1012`) — bereits ein voll inszeniertes Risiko-Beat-Gate mit SL-Framing-Pflicht. ✅ Das ist der Beweis, dass die negative Achse beat-fähig ist — nur ungleich verteilt.
- **Px-als-nur-Belohnung-Konsistenz** (`masterprompt:521`) — durchgehend gehalten. ✅

---

## Gesamturteil

Flos Vermutung stimmt **teilweise**: Vieles *läuft*, aber die negative Achse ist **erlebnis-ungleich verteilt**. Es gibt zwei Pole:
- **Gut beat-isiert:** Tod, Anachronismus, Exfil-Spotlight, aktiver Fraktions-Eingriff.
- **Still / nur Mechanik:** Heat (am stärksten), Mission-Scheitern im Debrief, Fraktions-Übergang, Stress-Schwellen-Kipp.

**Asymmetrie: ~6 Belohnungs-Beat-Gates vs. ~2 echte Verlust-Beat-Gates.** Das größte Gefälle ist **Heat** — ein stiller Zähler ohne Sinn, ohne Schwelle, ohne Beat, ohne Debrief-Thematisierung. Das ist exakt das Problem, das Px vor dem Px-Resonanz-Pflichtgate hatte (*„spielt eigentlich gar keine Rolle mehr"*). **Der Px-Fix ist die fertige Blaupause für den Heat-Fix.** Zweitgrößtes Gefälle: der Debrief feiert Erfolg sechsfach, quittiert Misserfolg mit einem roten ✗ — genau Flos *„das hätte schiefgehen können"* fehlt als Erlebnis.

**STILL (Patch lohnt), nach Priorität:**
1. **Heat** — größte Lücke, Px-Blaupause anwenden.
2. **Mission-Scheitern im Debrief** — Scheiterns-Spiegel-Beat.
3. **Fraktions-Übergang ruhig→Beobachter→aktiv** — sichtbare Gegenseiten-Reaktion.
4. **Stress-Schwellen-Kipp** — von optional zu Pflicht-Beat.

Alle vier rein chirurgisch rahmbar — keine Zahl, kein Cap, keine neue Würfeltabelle. Pflicht-Nebenbedingung für jeden Patch: die negativen Beats in die §F-Wichtigkeits-Rang-Liste aufnehmen, sonst stapeln sich Verlust- und Belohnungs-Beats im Debrief undokumentiert (das Dosierungs-Gate nennt Verlust-Beats bereits als „künftig", regelt ihren Rang aber noch nicht).
