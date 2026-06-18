# Sweep — Progressions-Beats (Rang / ITI-Ruf / Lizenz-Tier / Prestige)

> ZEITRISS @ main · reiner Lese-Audit · Worker: sweep-progression
> Messlatte: Vorbild-Patches Px-Resonanz-Pflichtgate (§F, masterprompt:518-521) und
> Level-Up-Belohnungs-Pflichtgate (§F, masterprompt:649-654). Beide rahmen eine
> Progression als **spürbaren, diegetischen Beat** statt als stiller Score-Screen-Zeile,
> **ohne** Zahlen/Caps/Mechanik zu ändern. Frage: Haben Rang/Ruf/Lizenz/Prestige das auch?

---

## Pro Achse

### 1. ITI-Ruf — **STILL** (Patch lohnt)

**Mechanik vorhanden, sauber definiert:**
- `meta/masterprompt_v6.md:658-661` — ITI-Ruf-Standardprogression: Start 0; +1 nach erster
  Core-Mission; +1 pro Core-Boss (MS 5/10/15/20); nur Core zählt; Cap = 5.
- `meta/masterprompt_v6.md:655-657` — SSOT: `reputation.iti` = operativer Institutsruf
  (Rang/Lizenzpfad), `reputation.factions.*` = politisches Standing. Sauber getrennt.

**Inszenierung — NUR HUD-Zeile, kein Beat:**
- `meta/masterprompt_v6.md:98` — Debrief-Sequenz listet `… → ITI-Ruf-Update → Px-Resonanz-Beat → …`.
  Auffällig: direkt **neben** dem Ruf-Update steht der Px-Resonanz-Beat (inszeniert),
  während das Ruf-Update selbst **nur ein Update** ist.
- `meta/masterprompt_v6.md:584-585` — `Zeige immer: 'Rang [Name] · ITI-Ruf +X · Lizenz Tier [0-V]'.
  Bei Ruf-Änderung explizit melden: 'ITI-Ruf +2 → +3 · Lizenz Tier III freigeschaltet!'`
  → Das ist exakt der **nackte Zahlen-Tick**, den das Px-Gate (masterprompt:518) ausdrücklich
  vermeiden will (»Kein nackter Zahlen-Tick«).

**Urteil:** STILL. Der Ruf-Anstieg ist nicht diegetisch inszeniert — kein In-World-Moment
(ITI registriert deine Leistung, ein Sachbearbeiter/Direktor vermerkt deinen Aufstieg).
Genau das Px-Muster vor dem Resonanz-Fix.

---

### 2. Rang — **STILL** (Patch lohnt; mit Ruf koppelbar)

**Mechanik vorhanden:**
- `core/spieler-handbuch.md:558-567` — ITI-Rang-Mapping (SSOT), an ITI-Ruf gekoppelt:
  Ruf 0 = Rekrut, 1 = Operator I, 2 = Feldagent, 3 = Senior-Feldagent, 4 = Elitechrononaut,
  5 = Apex-Agent. Damit ist **jeder** Ruf-Anstieg zugleich ein **Rang-Wechsel** (1:1-Mapping).
- `core/spieler-handbuch.md:569` — Debrief-Format `Rang Feldagent · ITI-Ruf +2 · Lizenz Tier II`.

**Inszenierung — nur Label-Wechsel in der HUD-Zeile:**
- Das Rang-Label rotiert in der HUD-Zeile (masterprompt:584), aber es gibt **nirgends** einen
  Beförderungs-Beat. Eine **Beförderung** vom Feldagent zum Senior-Feldagent ist diegetisch
  ein fetter Moment (Urkunde, Direktor-Funkspruch, neuer Zugang im HQ) — wird aber als reiner
  String-Tausch behandelt.
- Rang taucht **nicht** als eigener Schritt in der Debrief-Sequenz auf (masterprompt:98, :579),
  er reitet still auf dem Ruf-Update mit.

**Urteil:** STILL. Da Rang 1:1 an Ruf hängt, ist der natürliche Ort ein **gemeinsamer
Ruf-+-Rang-Beat** (siehe Patch-Vorschlag 1): Wenn der Ruf eine Stufe steigt und damit der Rang
wechselt, ist das **ein** Beförderungs-Moment.

---

### 3. Lizenz-Tier — **STILL** (Patch lohnt) + **Persistenz-Befund**

**Mechanik vorhanden:**
- `meta/masterprompt_v6.md:425-434` — Tier-Wirkungsrahmen-Tabelle: Tier 0 = frei,
  Tier 1 = Ruf +1, … Tier 5 = Ruf +5. Lizenz-Tier schaltet den **Zugang zu Gear-/Waffen-/
  Rüstungs-Tiers** frei (Schaden, DR, CU-Bereich). Tier ist also **aus Ruf abgeleitet**
  (keine eigene Achse, sondern eine Sicht auf den Ruf).
- `core/spieler-handbuch.md:554-556` — Ab Ruf +5 alle regulären Lizenzpfade kaufbar.

**Inszenierung — nur Meldung, kein Freischalt-Beat:**
- `meta/masterprompt_v6.md:585` — `Lizenz Tier III freigeschaltet!` ist eine **Ausrufezeichen-
  Meldung in der HUD-Zeile**, aber kein diegetischer Beat. Eine Tier-Freischaltung heißt konkret:
  »Du darfst jetzt Tier-III-Ausrüstung beziehen« — das ist ein **Loadout-/Quartiermeister-Moment**
  (das ITI gibt dir Zugriff auf schwereres Gerät), der spielmechanisch sofort relevant ist
  (neuer Shop-Zugang). Wird aber nicht ausgespielt.

**Persistenz-Befund:** `license_tier` ist **NICHT** im Save persistiert (grep über alle KBs +
masterprompt-JSON-Template + speicher-fortsetzung.md → 0 Treffer). Das ist **konsistent &
korrekt**, weil Lizenz-Tier deterministisch aus `reputation.iti` ableitbar ist (Tabelle :425-434).
Kein eigenes Feld nötig — aber siehe Konsistenz-Check: die Ableitungsregel sollte dort, wo
Tier angezeigt wird, explizit als »abgeleitet aus iti« markiert sein, damit kein Worker später
ein redundantes Feld erfindet.

**Urteil:** STILL (Beat fehlt). Persistenz korrekt-als-abgeleitet.

---

### 4. Prestige — **TEILWEISE** (Beat-Design existiert, aber nur im Lore-KB, nicht spielflächen-aktiv) + **Persistenz-Befund**

**Beat-Design VORHANDEN — und sogar gut — in der Lore-KB:**
- `core/zeitriss-core.md:434-446` — Prestige-Trigger: »Der Aufstieg wird im HQ als **feierlicher
  Akt** festgehalten — Ihr kehrt ins ITI zurück, absolviert einen **Rite-of-Passage** …«;
  und :445-447 »Prestige-Perks sind bewusst **filmisch inszeniert**: Ihr spürt in der Szene, wie
  das Zeitgefüge kurz zittert, während das ITI Euren Namen in die Annalen brennt.«
  → Das ist **Beat-Sprache par excellence** — besser als alles, was Ruf/Rang/Lizenz haben.
- `core/zeitriss-core.md:341-347` — Prestige-Meilensteine Lvl 25 (_Bewährter Agent_, HUD-Abzeichen),
  50 (_Veteran_, eigener Fraktionssektor im HQ), 75 (_Koryphäe_, Zugang zu Prestige-Perks).

**Aber: nicht auf der Spielfläche (Masterprompt) verankert:**
- `grep -ni prestige meta/masterprompt_v6.md` → **0 Treffer.** Prestige kommt im Masterprompt
  **gar nicht** vor. Die schöne Beat-Beschreibung lebt ausschließlich in `zeitriss-core.md`
  (Design-Lore) und `sl-referenz.md:555`. Damit ist der Beat **dokumentiert, aber nicht als
  Pflichtgate erzwungen** — die SL muss zufällig in die Lore-KB schauen, um ihn auszulösen.
- Prestige-Meilensteine stehen **nicht** in der Debrief-Sequenz (masterprompt:98, :579) und
  **nicht** in der Level-Up-Pflicht-Logik (masterprompt:649-654), obwohl Lvl 25/50/75
  Level-Schwellen sind, die ohnehin durch das Level-Up-Gate laufen.

**Konsistenz-Riss bei den Meilenstein-Stufen:**
- `core/zeitriss-core.md:341-347` listet 25/50/75 (drei Titel).
- `core/sl-referenz.md:555-556` listet 25/50/75 **+ 100 (_Legende_)** — vier Stufen.
  → Die beiden KBs sind bei der Meilenstein-Liste **nicht deckungsgleich** (100/_Legende_
  fehlt in zeitriss-core). Befund für Konsistenz-Patch (kein Mechanik-Eingriff, nur Liste angleichen).

**Persistenz-Befund:** `prestige` / `prestige_level` ist **NICHT** im Save persistiert
(grep über masterprompt-JSON + speicher-fortsetzung.md → 0 Treffer; einziger prestige-Treffer in
systems/ ist `kp-kraefte-psi.md:665`, ein Psi-Übernahme-Begriff, **nicht** das Progressions-Prestige).
Das ist ein **echter Befund**: Prestige-Cap 14 (spieler-handbuch:407) und die Prestige-Perks
(zeitriss-core:441) verändern dauerhaft Attributs-Caps und Fähigkeiten — wenn der Prestige-Status
**nicht** im Save steht, kann er einen Chat-Restart / JSON-Reload **nicht überleben**. Allerdings:
relevant erst ab Lvl 25/100 — bei der typischen Kampagnenlänge (20 Core-Missionen → Lvl ~20)
praktisch noch nicht erreicht. **Niedrige Dringlichkeit, aber notieren** (gleiche Klasse wie der
research-Persistenz-Befund: Mechanik dokumentiert, Save-Feld fehlt).

**Urteil:** TEILWEISE. Beat-**Beschreibung** existiert (gut), aber nicht spielflächen-erzwungen +
Persistenz-Lücke + Meilenstein-Liste inkonsistent.

---

## Save-Persistenz-Check

| Achse        | Save-Feld                         | Persistiert? | Bewertung |
|--------------|-----------------------------------|--------------|-----------|
| ITI-Ruf      | `characters[].reputation.iti`     | ✅ ja (masterprompt:1005-1007, speicher:347) | korrekt |
| Rang         | `characters[].rank`               | ✅ ja (masterprompt:978; speicher:632, :926) | korrekt (string) |
| Lizenz-Tier  | — (aus `reputation.iti` abgeleitet) | ⚪ bewusst nicht | korrekt-als-abgeleitet, sollte als »derived« markiert sein |
| Prestige     | — (kein Feld)                     | ❌ **fehlt** | **Befund**: Cap-14/Perks überleben Restart nicht; niedrige Dringlichkeit |

Detail: `rank` ist als String persistiert (z. B. `"rank": "Operator I"`), nicht als abgeleiteter
Wert — d. h. Rang **und** Ruf werden beide gespeichert. Da Rang 1:1 aus Ruf folgt (Mapping
spieler-handbuch:558), ist `rank` technisch redundant, aber unschädlich (kein Patch nötig;
nur erwähnt für Vollständigkeit).

---

## Konsistenz-Check

1. **Debrief-Sequenz-Asymmetrie (masterprompt:98 vs :579):** Die Sequenz nennt
   `XP/Level-Up (mit Belohnungs-Beat) → ITI-Ruf-Update → Px-Resonanz-Beat → Research-Tick →
   Lizenz-Tier`. Zwei Schritte sind explizit als **Beat** markiert (Level-Up, Px-Resonanz),
   die anderen beiden Progressions-Schritte (ITI-Ruf-Update, Lizenz-Tier) **nicht** — obwohl
   sie in derselben Sequenz, direkt daneben stehen. Das ist die sichtbarste Inkonsistenz:
   die Sequenz mischt »Beat«-Schritte und »stille Update«-Schritte.
   `meta/masterprompt_v6.md:579` (Kurzform) nennt zudem **keinen** Px-Resonanz-Beat und
   **keinen** Research-Tick — die Lang- (:98) und Kurzfassung (:579) der Debrief-Sequenz sind
   nicht deckungsgleich (Befund unabhängig vom Beat-Thema, aber hier sichtbar geworden).
2. **Rang nicht eigenständig in der Sequenz:** Rang-Wechsel reitet implizit auf dem Ruf-Update,
   ist aber nirgends als Schritt benannt — er »passiert einfach« über das Mapping.
3. **Prestige fehlt komplett auf der Spielfläche** (siehe Achse 4): nicht im Masterprompt,
   nicht in der Debrief-Sequenz, nicht im Level-Up-Gate.
4. **Prestige-Meilenstein-Liste divergiert** zwischen zeitriss-core (:341-347, 3 Stufen) und
   sl-referenz (:555, 4 Stufen inkl. Lvl 100 _Legende_).

---

## Patch-Vorschläge (priorisiert, chirurgisch — KEINE Mechanik-Änderung)

> Leitprinzip wie bei Px/Level-Up: Beats **rahmen** die bestehende Mechanik, ändern **keine**
> Zahlen/Caps/Progression. Alle Vorschläge sind Fokus-Sätze in §F des Masterprompts.

**P1 — Ruf-+-Rang-Beförderungs-Pflichtgate (höchste Priorität).**
Ein **gemeinsames** Gate für die gekoppelten Achsen Ruf+Rang. Einfügen in §F, direkt nach dem
ITI-Ruf-SSOT/Standardprogression-Block (`meta/masterprompt_v6.md:655-661`). Inhalt:
- Bei Ruf-Anstieg, **der einen Rang-Wechsel auslöst** (jeder Anstieg tut das, Mapping 1:1):
  ein bis zwei diegetische Sätze — das ITI vermerkt deinen Aufstieg, Funkspruch/Urkunde/
  Direktor-Anerkennung, neuer Rang-Titel als In-World-Beförderung. Plus HUD-Ping
  `Kodex: ITI-Ruf +2 → +3 · Beförderung: Feldagent → Senior-Feldagent.`
- Geltungsbereich: Core-Debrief (dort entsteht Ruf). Ändert Mapping/Cap/Progression nicht.
- Begründung-Satz analog Px/Level-Up (»Aufstieg war korrekt, aber als Erlebnis ein String-Tausch«).
- **Wo:** Debrief-Sequenz :98 ergänzen — `… → ITI-Ruf-Update (mit Beförderungs-Beat) → …`.

**P2 — Lizenz-Tier-Freischalt-Beat (mittlere Priorität).**
Einfügen in §F nahe der Tier-Tabelle-Referenz bzw. als Zusatz zum P1-Gate. Inhalt:
- Wenn ein Ruf-Anstieg ein **neues Lizenz-Tier** freischaltet (Ruf +N → Tier N): kurzer
  Quartiermeister-/Loadout-Beat — »das ITI gibt deinen Zugriff auf Tier-N-Ausrüstung frei«,
  mit konkretem Hinweis, dass jetzt schwereres Gear im HQ-Shop verfügbar ist. Plus HUD-Ping
  statt bloßem `Lizenz Tier III freigeschaltet!`.
- Markiere in derselben Stelle Lizenz-Tier explizit als **abgeleitet aus `reputation.iti`**
  (Anti-Redundanz-Hinweis, verhindert künftiges Save-Feld-Erfinden).
- Geltungsbereich: Core-Debrief. Ändert die Tier-Tabelle (:425-434) nicht.
- **Wo:** Debrief-Sequenz :98 — `… → Lizenz-Tier (mit Freischalt-Beat bei neuem Tier) …`.

**P3 — Prestige auf die Spielfläche heben (niedrigere Priorität, da Lvl 25+ selten erreicht).**
- Den bereits vorhandenen, guten Beat aus `core/zeitriss-core.md:434-446` als **Kurz-Referenz/
  Pflicht-Hinweis** in den Masterprompt §F spiegeln (aktuell 0 Masterprompt-Treffer), damit die
  SL ihn an Lvl 25/50/75/100 zuverlässig auslöst — gekoppelt ans bestehende Level-Up-Gate
  (:649-654), nicht als neue Mechanik. Z. B. ein Satz: »Bei Prestige-Meilenstein-Leveln
  (25/50/75/100, siehe zeitriss-core.md#prestige) ist der Level-Up-Beat ein **Prestige-Akt**
  (Rite-of-Passage, Titel-Verleihung), kein normaler Werkstatt-Beat.«
- **Save-Persistenz prüfen/ergänzen:** optionales Feld `prestige` (oder `prestige_level`/Titel)
  im Character-Objekt + speicher-fortsetzung.md dokumentieren, **falls** Prestige-Status den
  Restart überleben soll. Niedrige Dringlichkeit (erst ab Lvl 25). Reiner Befund — Entscheidung Flo.
- **Konsistenz-Fix (trivial):** Meilenstein-Liste zwischen zeitriss-core:341-347 und
  sl-referenz:555 angleichen (Lvl 100/_Legende_ in zeitriss-core ergänzen oder in sl-referenz
  als »+100 optional« markieren).

**P4 — Debrief-Sequenz Lang/Kurz angleichen (Hygiene, beat-unabhängig).**
:98 (lang) und :579 (kurz) unterscheiden sich (Px-Resonanz-Beat + Research-Tick fehlen in :579).
Kurzfassung an Langfassung angleichen oder Kurzfassung entfernen. Kein Beat-Thema, aber beim
Audit aufgefallen.

---

## Was schon rund ist

- **ITI-Ruf-Mechanik** ist sauber definiert und persistiert (`reputation.iti`); SSOT-Trennung
  iti vs. factions ist klar (masterprompt:655-657). Nur der **Beat** fehlt.
- **Rang-Mapping** ist eine saubere SSOT (spieler-handbuch:558), 1:1 an Ruf — ideal für
  einen **gemeinsamen** Beförderungs-Beat (kein separates Tracking nötig).
- **Lizenz-Tier-Ableitung** aus Ruf (Tabelle :425-434) ist konsistent und braucht **kein**
  eigenes Save-Feld — die Nicht-Persistenz ist hier ein Feature, kein Bug.
- **Prestige-Beat-Sprache** in zeitriss-core.md:434-447 ist bereits exzellent (»feierlicher Akt«,
  »Rite-of-Passage«, »filmisch inszeniert«, »Namen in die Annalen brennt«) — das Material für
  den Beat existiert, es muss nur auf die Spielfläche gehoben werden, nicht erfunden.

---

## Gesamturteil

Von den vier geprüften Achsen laufen **drei noch ›still‹** durch (genau das Px-Muster vor dem
Resonanz-Fix), eine ist ›teilweise‹:

- **ITI-Ruf → STILL** (Patch lohnt, P1)
- **Rang → STILL** (Patch lohnt, mit Ruf koppeln → P1)
- **Lizenz-Tier → STILL** (Patch lohnt, P2; Persistenz korrekt-als-abgeleitet)
- **Prestige → TEILWEISE** (Beat-Design vorhanden & gut, aber nur im Lore-KB, nicht
  spielflächen-erzwungen; + Save-Persistenz-Lücke; + Meilenstein-Liste inkonsistent → P3)

**Kein HAT-BEAT** unter den vier (anders als Px und Level-Up). Die größte Hebelwirkung hat
**P1 (Ruf+Rang als gemeinsamer Beförderungs-Beat)**, weil beide Achsen 1:1 gekoppelt sind und
in **jedem** Core-Debrief mit Ruf-Anstieg greifen. P2 (Lizenz-Freischalt-Beat) ist der zweite
naheliegende Schritt, da er denselben Auslöser (Ruf-Anstieg) teilt — P1+P2 lassen sich zu **einem**
Debrief-Aufstiegs-Beat bündeln. P3 (Prestige) ist Design-mäßig fast fertig, braucht nur eine
Spielflächen-Verankerung + Persistenz-Entscheidung, ist aber wegen Lvl-25+-Seltenheit niedriger
priorisiert.

Zwei **Persistenz-/Konsistenz-Befunde** (kein Beat-Thema): Prestige nicht im Save (niedrige
Dringlichkeit) und Debrief-Sequenz lang≠kurz (:98 vs :579).
