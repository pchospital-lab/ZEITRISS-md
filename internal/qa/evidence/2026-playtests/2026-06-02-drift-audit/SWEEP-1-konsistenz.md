# Sweep 1 — Konsistenz & Invarianten

Audit der fünf Spielgefühl-Patches **#3192–#3195** gegen das Gesamt-Repo und die
Pflicht-Invarianten. Reiner Lese-Audit (HEAD `5d6cd8ac`, Branch `main`).
Befunde mit `Datei:Zeile` + Zitat; sonst „NICHT GEFUNDEN".

---

## Invarianten-Check (jede einzeln)

### Save-Schema v7 (Template im Masterprompt ist SSOT) → **VERLETZT** (durch #3194)

Der `research`-Block aus #3194 ist **nur** im Prosa-Pfadbaum von
`speicher-fortsetzung.md` ergänzt, fehlt aber in **drei** SSOT-Stellen — und die
strenge Export-Schema-Datei würde einen Save **mit** `research` aktiv zurückweisen.

1. **Kanonisches v7-JSON-Template (SSOT laut Aufgaben-Vorgabe & laut Doku):**
   `meta/masterprompt_v6.md:1013` zeigt
   > `"economy": { "hq_pool": 0 },`

   direkt gefolgt von `"logs": { … }` (Zeile 1014 ff). **Kein `research`-Block.**
   `grep 'research'` im Template-Bereich (Zeilen 950–1086): **NICHT GEFUNDEN.**
   Gleichzeitig schreibt das neue Gate explizit, `research.projects[]` sei Teil
   des Save-Schemas (`meta/masterprompt_v6.md:107`):
   > „Jedes Projekt (`research.projects[]`, siehe Save-Schema in
   > `systems/gameflow/speicher-fortsetzung.md`) …"

   → Das deklarierte SSOT-Template enthält das Pflicht-Feld nicht. LLM-Saves, die
   das Template wörtlich reproduzieren (genau das prüft
   `test_v7_schema_consistency.js` Check 2), verlieren den Block.

2. **v7-Export-Pflichtfelder-Liste (watchguard-geprüfte SSOT):**
   `systems/gameflow/speicher-fortsetzung.md:217-238` listet die Export-Pflichtfelder.
   Zwischen
   > `economy { hq_pool },` (Zeile 226)

   und `logs { … }` / `arena { … }` steht **kein** `research`-Eintrag. Diese Liste
   wird von `tools/test_v7_export_fieldlist_watchguard.js` als Vertrag gelesen — der
   Vertrag kennt `research` nicht.

3. **JSON-Schema-Dateien:**
   - `systems/gameflow/saveGame.v7.export.schema.json` hat **`additionalProperties: false`**
     auf Root und Root-Properties `[v, zr, save_id, parent_save_id, merge_id,
     branch_id, campaign, characters, economy, logs, summaries, continuity, arc,
     ui, arena]` — **ohne `research`**. Ein `!save`-Export, der den von #3194
     vorgeschriebenen `research`-Block enthält, ist nach diesem Export-Schema
     **schema-invalide** (verbotenes Zusatz-Property).
   - `systems/gameflow/saveGame.v7.schema.json` hat `additionalProperties: true` —
     toleriert `research` zwar, listet es aber ebenfalls nicht als Property.

   `test_v7_schema_consistency.js:127` validiert Fixtures nur gegen die **tolerante**
   `saveGame.v7.schema.json`, nicht gegen die **strenge** Export-Schema-Datei —
   deshalb fällt die Lücke im aktuellen Testlauf nicht auf, ist aber im echten
   Export-Pfad ein harter Vertragsbruch.

**Konsistente Teil-Aspekte von #3194** (zur Abgrenzung): Migrations-Default
(`speicher-fortsetzung.md:349` + `:1213-1215`: fehlender Block → `research:{projects:[]}`,
fehlendes `scope` → `campaign`) ist sauber definiert; Off-by-one-Anlege-Regel und
Cap-Formel `min(tier, 9−mission)` sind in sich konsistent und brechen **keine**
andere Invariante. Der Defekt liegt **ausschließlich** in der fehlenden
Aufnahme von `research` in Template + Export-Fieldlist + Export-Schema.

→ **NACHBESSERN (kritisch):** `research`-Block in (a) Masterprompt-§F-JSON-Template,
(b) Export-Pflichtfelder-Liste `speicher-fortsetzung.md:217ff`, (c)
`saveGame.v7.export.schema.json` (+ ggf. `.schema.json`) ergänzen. Sonst ist jeder
Save mit aktiver Forschung entweder schema-invalide oder verliert den Block beim
Template-getriebenen Re-Export.

### Boss-Timing (Core-Mission 5 Mini, Mission 10 Boss; Rift-Szene 10) → **OK**

`meta/masterprompt_v6.md:268`:
> „Mini-Boss MS5, Episoden-Boss MS10, Rift-Boss SC10, Para-Tier-3+."

`:261` (2 Phasen MS5 / 3 Phasen MS10/SC10), `:87-88`, `:214`, `:217` konsistent.
Das Rift-Horror-Gate (#3193) referenziert korrekt **SC10** als Boss
(`:273`: „Der Rift-Boss (SC10) ist der Dread-Peak"). Keine Verschiebung.

### 12 Szenen Core / 14 Szenen in 4 Stages Rift → **OK**

`meta/masterprompt_v6.md:84-85` (12/14), `:223` (Korridor 12/14).
Rift-Stages unverändert in `gameplay/kreative-generatoren-missionen.md`:
**Tatort (1-4) → Leads (5-9) → Boss-Encounter (10) → Boss-Resolution (11-14)**
(4 Stages). #3193 hat das Frontloading geändert (physische Begegnungen *innerhalb*
Tatort/Leads), die **Stage-Grenzen aber nicht angetastet** — die 14-Szenen-in-4-Stages-
Struktur bleibt. Konsistent.

### Px-Tabelle (1-2→+1/2Miss | 3-5→+1 | 6-8→+2 | 9-11→+2 | 12-14→+3) → **OK**

Kanonische Tabelle `meta/masterprompt_v6.md:514` **unverändert**:
> „TEMP 1-2 → +1 Px alle 2 Missionen | 3-5 → +1/Mission | 6-8 → +2 | 9-11 → +2 | 12-14 → +3."

Das Px-Resonanz-Gate (#3195) ändert **keine** Zahl (`:524`: „Mechanik … bleibt
**unverändert** … ändert keine Zahlen"). Der Resonanz-Zugewinn `:518` spiegelt die
Kadenz korrekt: „TEMP 3-5 = +1, TEMP 6-11 = +2, TEMP 12-14 = +3". Das Zusammenfassen
von 6-8 und 9-11 zu „6-11 = +2" ist **numerisch korrekt** (beide Bänder = +2), keine
Wertänderung — nur eine kompaktere Schreibweise derselben Tabelle. Kein Verstoß.

### Attribut-Cap max 6 / Summe 18 → **OK** (unberührt)

Von keinem der fünf Patches angefasst. Template `meta/masterprompt_v6.md:976`
(`attr {…:3…}` Summe 18) intakt, Check 3 in `test_v7_schema_consistency.js` schützt
weiter gegen Null-Attribute. NICHT GEFUNDEN: Verstoß.

### Equipment {name,type,tier} → **OK** (unberührt)

Von keinem Patch angefasst. NICHT GEFUNDEN: Verstoß.

### Psi-Kosten immer PP UND SYS → **OK** (unberührt)

Von keinem Patch angefasst. NICHT GEFUNDEN: Verstoß.

### LP (nicht HP) in spielersichtigen Texten → **OK**

Alle fünf Diffs verwenden in spielersichtigen Statblocks korrekt **LP**
(`begegnungen.md:579 ff`: „LP W6×3-4", „Armor 1-2"). NICHT GEFUNDEN: „HP" in den
Patches.

### „KI-SL"/„Spielleitung" (nicht „GPT") → **OK**

Alle Patches schreiben „SL" / „KI-SL" / „Spielleitung". NICHT GEFUNDEN: „GPT" in den
fünf Diffs. (Hinweis ohne Patch-Bezug: Dateiname `systems/toolkit-gpt-spielleiter.md`
trägt „gpt" historisch im Pfad — von diesen PRs nicht verursacht, daher kein
Sweep-1-Befund.)

---

## Stale Referenzen

### Briefing-Output-Pflichtgate „Regel <N>" → **OK, alle korrekt nachgezogen**

Durch Einfügen von **Regel 2 „Angriffspunkte"** verschoben sich Continuity-Anker
auf Regel 5 — alle Verweise zeigen korrekt:

- `meta/masterprompt_v6.md:315` (Rift-Sonderweg): „…Continuity-Anker-Pflicht ab MS2
  (§C Briefing-Output-Pflichtgate **Regel 5**)…" → korrekt (Continuity ist jetzt #5).
- `gameplay/kreative-generatoren-missionen.md:178`: „…Briefing-Output-Pflichtgate
  **Regel 2** (Angriffspunkte)." → korrekt.
- `gameplay/kreative-generatoren-missionen.md:183`: „…Briefing-Output-Pflichtgate
  **Regel 1** (Action-Kern-Pflicht)." → korrekt (Action-Kern ist Unter-Bullet von
  Regel 1 „Hauptziel").

Liste sauber 1–5 (`:280-296`: Hauptziel/Action-Kern → Angriffspunkte → Nebenziele →
Erfolgskriterium → Continuity).

### Mission-Integrität „drei/vier Regeln" → **OK, vollständig nachgezogen**

`grep 'drei Regeln'`: **NICHT GEFUNDEN**. Header `:222` „**Vier Regeln**", Trigger
`:227` „der **vier** Regeln", Anti-Skip `:228` „Die **vier** Regeln". Konsistent mit
neu eingefügter Regel 4 „Harter Kern-Auftrag" (`:226`).

### „Para-Schwereklassen"-Anchor → **OK**

Anchor existiert: `gameplay/kreative-generatoren-begegnungen.md:575`
`{#para-schwereklassen}`. Verweise zeigen darauf:
- `meta/masterprompt_v6.md` Rift-Horror-Gate Regel 4 (`:274`): „…§Para-Schwereklassen".
- `gameplay/kreative-generatoren-missionen.md` Rift-Pacing: „…§Para-Schwereklassen".
Kein Dead-Link.

### „Research-Fortschritt-Pflichtgate"-Verweise → **OK** (Verweis-seitig)

`meta/masterprompt_v6.md:98` (Debrief-Sequenz) und `:107/:109` verweisen konsistent
auf das Gate und auf `research.projects[]`. (Der Schema-Defekt oben ist **inhaltlich**,
nicht ein Verweis-Bruch.)

---

## Cross-File-Widersprüche

- **Strang-Wahl / Angriffspunkte:** Masterprompt §C (`:281`) und Generator
  (`missionen.md:172-178`) beschreiben dasselbe (Hauptziel singulär, Weg wählbar).
  Score-Screen-Anker bleibt singulär → kein Widerspruch zu Debrief/Continuity. **OK.**
- **Harter Kern-Auftrag / Action-Kern:** Masterprompt (`:226`, `:281` Action-Kern-
  Pflicht), Generator (`missionen.md:97-103` + `:179-183`) und MS1-2-Tonfall
  (`kampagnenstruktur.md:1045 ff`) konsistent — „konkret/hart ≠ große Stakes" wird in
  allen Stellen gleich getrennt. **OK.**
- **Dichte / 25-30 min:** siehe Dauer-Konsistenz unten — **OK in Produktion.**
- **Rift-Horror:** Masterprompt-Gate (`:269-275`), Generator-Frontloading
  (`missionen.md:291-308`), Para-Klassen (`begegnungen.md:575-606`) greifen sauber
  ineinander; Boss-DR vs. Para-Armor („stapeln nicht") explizit geklärt
  (`begegnungen.md:600`), kein Konflikt mit Bosskampf-Pflichtgate. Anomalie-Budget
  (One-Weird-Thing) ausdrücklich unangetastet (`:272`, `:275`). **OK.**
- **Research:** inhaltlich konsistent zwischen Masterprompt-Gate und
  `speicher-fortsetzung.md`-Pfadbaum (Cap-Formel, scope, Tick identisch
  formuliert) — der **einzige** Bruch ist die fehlende Schema-/Template-/Fieldlist-
  Aufnahme (siehe Invarianten-Check). **WIDERSPRUCH Doku↔Schema, siehe oben.**
- **Px-Resonanz:** Masterprompt §F (`:515-525`) Geltungsbereich „Core-only,
  Rift/Arena/Chronopolis kein Px" deckt sich mit `kampagnenstruktur.md` §Rift-Loop und
  `spieler-handbuch.md:450` („Arena … **nie Px** und **nie Rift-Seeds**"). **OK.**
- **Arena-Sofort:** Masterprompt (`:928`: Briefing-/Mission-Integrität-/Rift-Horror-
  Gates gelten nicht, Kampfszenen-Gate gilt) deckt sich mit
  `spieler-handbuch.md:448-450` (Arena = eigener Kampf-Sport-Pfad). **OK.**

---

## Dauer-Konsistenz

`grep -E '60[-–]75'` über alle Produktions-`*.md`/`*.json`
(exkl. `.git/ internal/ uploads/ meta/archive/ out/ .exports/ zeitriss-audit/`):
**NICHT GEFUNDEN.** Keine Reste der alten 60-75-min-Angabe in Produktion.

Alle Core-Op-Dauer-Angaben stehen konsistent auf **25-30 min**:
- `core/sl-referenz.md:177` „durchschnittlich **25-30 Minuten** … 12 Szenen".
- `gameplay/kampagnenstruktur.md:814` Tabelle „**25-30 min** | 12 Szenen".
- `gameplay/kampagnenstruktur.md:1043` „dichte **25–30 Min**".

Kein Widerspruch. (`core/spieler-handbuch.md:1303` „Szene ca. 5-10 Min" ist die
**Szenen**-Dauer, nicht Missions-Dauer — bei 12 Szenen × 5-10 Min entsteht zwar
rechnerisch 60-120 Min, das ist eine **bestehende Spannung im Handbuch** und wurde
von #3192 nicht angefasst; siehe Handbuch-Abgleich. Reine 60-75-Reste: keine.)
`systems/currency/cu-waehrungssystem.md:200` „25-30 k CU" ist Währung, kein Dauer-Bezug.

---

## Spieler-Handbuch-Abgleich

Das Handbuch ist von keinem der fünf PRs editiert worden. Drei Beobachtungen, keine
harten Brüche, aber zwei Drift-Kandidaten:

1. **Szenen-Dauer vs. neue Missions-Dichte (Drift-Kandidat, NIEDRIG):**
   `core/spieler-handbuch.md:1303`:
   > „**Szene** - ca. 5-10 Min. Spielzeit. Core-Ops nutzen 12 Einsatz-Szenen"

   12 × 5-10 Min = 60-120 Min — passt nicht mehr sauber zur neuen Soll-Dauer
   **25-30 min** (#3192). Dem Spieler wird implizit eine längere Mission versprochen,
   als die KI-SL jetzt liefern soll. Empfehlung: Szenen-Dauer-Angabe im Handbuch auf
   die Dichte (~2-3 Min/Szene) anpassen oder relativieren. **Kein Gate-Bruch**, aber
   stiller Erwartungs-Widerspruch.

2. **Rift-Op-Tonalität (Drift-Kandidat, NIEDRIG):**
   `core/spieler-handbuch.md:70`:
   > „Jede Rift-Op ist ein eigenständiger **Mystery-Casefile-Fallfilm**"

   Das neue Rift-Horror-Pflichtgate (#3193) rahmt Rift-Ops jetzt als **Horror-Action-
   Filme** („Event-Horizon-Vibe, mit mehr Kampf"). Das Handbuch verspricht weiter
   reine „Mystery-Casefile"-Atmosphäre (auch `:69`). **Kein harter Widerspruch** —
   `:89` sagt bereits „dürfen unberechenbarer wirken, bleiben … physisch und konkret",
   was zur handfesten Para-Klasse passt. Aber „mehr Kampf / Horror-Tonalität" ist im
   Handbuch nicht angekündigt. Empfehlung: einen Halbsatz Horror-Action ergänzen,
   damit Spieler-Erwartung und SL-Pflicht-Ton übereinstimmen.

3. **Px / Research / Angriffspunkte / Arena:** Handbuch beschreibt Px als
   Belohnungssystem (`:35-41`, `:486 ff`) — die neue Resonanz-Erlebbarkeit (#3195)
   widerspricht dem nicht (keine Mechanik-Änderung). Research und Angriffspunkte sind
   im Handbuch (noch) nicht beschrieben — das ist eine **Doku-Lücke**, kein
   Widerspruch (das Handbuch verspricht nichts Gegenteiliges). Arena-Sofort deckt sich
   mit `:448-450`. NICHT GEFUNDEN: aktiver Bruch eines Spieler-Versprechens.

---

## Gesamturteil

**NACHBESSERN** — eine kritische Invariantenverletzung, plus zwei Handbuch-Drifts.

**Kritisch (Pflicht-Invariante v7-Schema gebrochen):**

1. **`research`-Block fehlt in der v7-SSOT** (#3194). Konkret ergänzen:
   - `meta/masterprompt_v6.md` §F JSON-Template (nach `economy`, Zeile ~1013):
     `"research": { "projects": [] }`.
   - `systems/gameflow/speicher-fortsetzung.md:217-238` Export-Pflichtfelder-Liste:
     `research { projects[] { id, label, kind, scope, tier, missions_total,
     missions_done, status, source?, reward_hint? } }`.
   - `systems/gameflow/saveGame.v7.export.schema.json` (Root hat
     `additionalProperties:false` → **Pflicht**, sonst Export schema-invalide) und
     konsistent `saveGame.v7.schema.json`.
   - Empfehlung: einen `research`-Fixture + Export-Schema-Validierung in
     `test_v7_schema_consistency.js` nachziehen (aktuell wird nur gegen das tolerante
     Schema validiert, daher blieb die Lücke grün).

**Nicht kritisch (Spielgefühl-/Doku-Drift, niedrige Prio):**

2. `spieler-handbuch.md:1303` Szenen-Dauer (5-10 Min × 12 ≠ 25-30 min Missions-Soll)
   an die neue Dichte angleichen.
3. `spieler-handbuch.md:70` Rift-Op-Tonalität um Horror-Action-Hinweis ergänzen
   (Konsistenz mit Rift-Horror-Pflichtgate).

**Sauber bestätigt:** Boss-Timing, 12/14-Szenen/4-Stages, Px-Tabelle, Attribut-Cap,
Equipment, Psi-PP/SYS, LP-Nomenklatur, KI-SL-Nomenklatur, alle Regel-N-Querverweise,
„drei/vier Regeln", Para-Anchor, Dauer-Konsistenz (keine 60-75-Reste in Produktion).
