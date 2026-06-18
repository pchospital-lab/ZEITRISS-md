# Critic-Review: feat/boss-mehrphasig

**Modell:** openrouter/anthropic/claude-opus-4.7 (thinking high)  |  **Gelaufen:** 2026-05-27T20:34+02:00  |  **Hash (base main):** 070526251a822d5452d45bab58adad4c9a23d587  |  **Patch:** working-tree (uncommitted), 4 files +157/-2

## Verdict

**GO mit Mini-Fix.** Patch adressiert Flo-Feedback aus Highlander-Playtest sauber, ist konsistent mit existierenden Pflichtgates (Kampfszenen-, Foreshadow-Gate, Signaturtell, Boss-DR-Tabelle) und bringt narrative Tiefe ohne Stat-Inflation. Drei kleinere Lücken bei Builder-Schema-Migration, Szenen-Korridor-Kompatibilität (Core 12-Szenen mit Episoden-Boss in Mission 10!), und einer toten Pfad-Referenz im wuerfelmechanik.md-Banner. Fix-Aufwand <30 Min.

## Smoke

- ✓ `git diff` parsed sauber, 4 Files +157/-2.
- ✓ Anchor `{#bossphasen-system}` existiert in kampagnenstruktur.md:545.
- ✓ Boss-Stat-Hint-Format in `kreative-generatoren-missionen.md` (Z.2276 ff.) ist `"LP 11 | Armor 1 | ..."` — Patch erweitert um `phase_1/phase_2/phase_3`-Felder, **bricht** das alte Inline-Format aber nicht (additive Erweiterung).
- ✓ Boss-DR-Tabelle (kampagnenstruktur.md:519) erwähnt im Patch konsistent, kein Wert-Override.
- ✗ `meta/masterprompt_v6.md` referenziert in §C die Spec `gameplay/kampagnenstruktur.md` §Bossphasen-System — sauber. Aber Rückreferenz im `core/wuerfelmechanik.md`-Banner zeigt auf "Masterprompt §C und kampagnenstruktur.md §Bossphasen-System" — funktioniert, ist aber redundant zur §Cineastische-Beats-Spec direkt darunter. Keine Inkonsistenz, nur stilistischer Hinweis.

## Befunde (5)

### 1. Boss-Mechanik-Konsistenz

- **Phasen-LP vs. Single-LP-Hint:** Bestehende `boss_stat_hint`-Strings (z. B. `"LP 11 | Armor 1 | GES 8 | TEMP 6"` in `kreative-generatoren-missionen.md:2276`) sagen **eine** LP-Zahl. Patch deklariert in `meta/masterprompt_v6.md:163` und `kampagnenstruktur.md:557`: *„Die bestehende Boss-Stat-Tabelle (LP 8–11) gilt **pro Phase**, nicht als Gesamt."* — semantisch ein **Re-Mapping bestehender Strings**: ohne Schema-Update interpretieren Runtime/SL die alten 5 Rift-Boss-Stat-Hints (Z.2276/2296/2316/2336/2356) künftig als „LP-pro-Phase". Das ist die *gewollte* Änderung, sollte aber explizit benannt werden — sonst Risiko, dass alte Generator-Ausgaben (Single-Pool) und neue (Pro-Phase) nebeneinander existieren ohne diskriminierendes Feld. **Mini-Fix:** Eine Zeile im Patch ergänzen, dass `boss_stat_hint` ab sofort **pro Phase** zu lesen ist, plus optional in `kreative-generatoren-missionen.md` einen Satz an die 5 Rift-Seed-Beispiele („LP 11 = LP pro Phase ×3"). Auto-Migration trivial, weil Werte ohnehin im Patch-Korridor (LP 8–11 = Episoden-/Rift-Spec).

- **Boss-DR pro Phase:** Patch sagt explizit „Boss-DR aus der Teamgrößen-Tabelle … bleibt unverändert und wirkt in jeder Phase" (`meta/masterprompt_v6.md:163`). **Mathematisch:** Vollteam 5 → Arc/Rift-Boss DR 4. Beat-Schaden Crew ~6–10. Netto pro Treffer ~2–6. Bei 8–11 LP/Phase = 2–6 Treffer pro Phase. ×3 Phasen = 6–18 Treffer → ~15–24 Beats. Passt **exakt** zum Phasen-Beats-Korridor (Vollteam 5–8 Beats × 3 Phasen = 15–24). Konsistent. Kein Fix nötig.

- **Verzahnung mit Foreshadow-Gate:** Foreshadow-Gate (Core 4/4, Rift 2/2) öffnet das Boss-Gate vor Szene 10. Patch ändert daran nichts — Phasen-System greift **nach** dem Gate. Sauber.

- **Signaturtell-Erweiterung (kampagnenstruktur.md:686–689):** Neue Belohnungsoption „Phase 1 startet mit Spezialität inaktiv" konsistent mit Signaturtell-Logik (taktischer Vorteil, kein Hard-Skip). Sehr saubere Integration. ✓

### 2. Multiplayer/Szenen-Korridor

**Kritischer Befund.** Mission-Integrität-Pflichtgate (Masterprompt §C, `kampagnenstruktur.md:122`) hält Core auf 12 Szenen, Rift auf 14 Szenen. Akt C (Core 10–12, Rift 10–14) ist 3 Szenen (Core) bzw. 3–5 Szenen (Rift) für Boss-Showdown + Exfil + Nullzeit-Beat.

- **Rift, Szene 10 als Boss-Encounter:** 3 Phasen × 5–8 Beats Vollteam = 15–24 Beats. Bei 4–6 Beats pro Szene (Standard-Output VERBOSE) = **3–4 Szenen** für den Bosskampf allein. Bei Rift bleibt Szene 11 (Exfil-Anbahnung), 12 (Boss-Resolution), 13 (Nachspiel), 14 (Epilog) → der Bosskampf darf Szenen 10–12 belegen, dann Resolution ab 13. Mathematisch passt es, aber **es ist eng**.
- **Core, Mission 10 als Episoden-Boss:** Episoden-Boss ist eine **eigene Mission** (Mission 10 in der Episode), nicht eine Szene. Patch behauptet aber bei `meta/masterprompt_v6.md:160`: „Mini-Boss MS5, Episoden-Boss MS10" — bedeutet die ganze Mission 10 ist der Episoden-Boss-Encounter. Hier hat die Mission **12 Szenen**, also reichlich Platz für 15–24 Boss-Beats über 3–4 Szenen. **Passt.**
- **Rift-Casefile-Builder (`gameplay/kreative-generatoren-missionen.md:2384–2389`):** Patch sagt sauber „Drei Phasen Pflicht … LP pro Phase 8–11". Korrekt referenziert.
- **Mini-Boss MS5 (Core, 2 Phasen):** Mission 5 hat ebenfalls 12 Szenen. 2 Phasen × 5–8 Beats = 10–16 Beats = 2–3 Szenen. Passt.

**Mini-Fix:** In `gameplay/kampagnenstruktur.md` §Bossphasen-System einen kurzen Hinweis ergänzen: *„Ein Bosskampf umspannt typischerweise 2–4 aufeinanderfolgende Szenen — der Szenen-Zähler tickt jeweils weiter, der Encounter behält durchgängigen HUD-Tag `BOSS-Encounter Phase X/Y`. Damit bleibt das 12/14-Szenen-Pacing intakt."* — sonst Risiko, dass SL den ganzen Bosskampf in eine Szene 10 stopft (= 15–24 Beats in einem Szenen-Output, bricht VERBOSE-Format) oder umgekehrt das Szenen-Cap reißt.

### 3. Überraschung vs. Phasen-Plan-Ansage

Patch dokumentiert in `kampagnenstruktur.md:633–642` und `meta/masterprompt_v6.md:165`: **Phasen-Anzahl wird angesagt, Spezialitäten erst bei Phase-Start sichtbar.**

- **Spielerseitiges Metagaming:** Crew weiss „3 Phasen kommen", LP pro Phase 8–11. Bei Boss-LP nahe 0 in Phase 1 → Crew **erwartet** Switch. Das nimmt Überraschung in der **Timing**-Dimension. Aber: Switch-**Inhalt** (Hidden-Asset / Verstärkung / Schauplatzwechsel / Trumpf / …) bleibt unbekannt, und die **Phase-Spezialität** ist die eigentliche Mali-Quelle. Überraschung im narrativ-mechanischen Effekt bleibt erhalten.
- **Trade-off ist explizit:** Patch begründet die Wahl in `meta/masterprompt_v6.md:165`: *„damit der Spieler den Spannungsbogen einschätzen kann (»aha, das wird noch dauern«)"*. Das ist Pacing-Information, nicht Mechanik-Information. Vergleichbar mit „du siehst, dass der Boss schwer atmet" als Foreshadow für Phase-Switch in Tabletops.
- **Alternative (Phasen-Anzahl geheim):** Würde Überraschung erhöhen, aber Crew kann nicht taktieren („sollen wir Trumpf-Karten jetzt spielen oder für Phase 3 sparen?"). Wenn Crew nicht weiss, ob es 1, 2 oder 3 Phasen sind, sparen sie konservativ → Bosskampf wird zähhh statt cinematisch. Patch-Entscheidung („Anzahl bekannt, Inhalt geheim") ist **die richtige Balance**.
- **Kein Fix nötig.** Optional: Ein Satz „Crew darf taktisch wissen, dass Phasen kommen — das ist Pacing-Vertrag, kein Spoiler" zur Vorbeugung gegen Critic-Frage in 2 Wochen.

### 4. Generator-Builder-Schema

- **Schema-Erweiterung:** Patch fügt `phase_1`/`phase_2`/`phase_3` mit `name`/`speciality`/`trigger_next` zum Rift-Casefile-Builder hinzu (`kampagnenstruktur.md:649–668` als Beispiel, `kreative-generatoren-missionen.md:2374–2378` als Pflichtanweisung).
- **Backward-Compatibility:** Die 5 existierenden Rift-Seeds (Z.2276–2356) haben **kein** `phase_*`-Feld. Wenn Runtime/SL alte Seeds lädt → Phasen-Pflicht greift, aber kein Builder-Output vorliegt → SL muss zur Laufzeit Phasen-Specs improvisieren. Das ist machbar (Pool aus Switch-Typen und Spezialitäten ist explizit), aber **inkonsistent** zur Pflichtansage „Builder produziert das automatisch" (`kampagnenstruktur.md:670–671`).
- **Mini-Fix (empfohlen, nicht blockierend):** Entweder
  (a) die 5 alten Rift-Seeds in `kreative-generatoren-missionen.md` per **Folge-PR** um `phase_1/2/3` ergänzen, oder
  (b) im Patch einen Satz ergänzen: *„Alte Rift-Seeds ohne `phase_*`-Felder: SL produziert die Phasen-Specs zur Laufzeit aus Pool §Phase-Spezialitäten und §Phasen-Switch. Migration der 5 bestehenden Seeds in Folge-PR."* — Variante (b) reicht für GO, weil der Patch nicht behauptet, alle Bestands-Seeds seien migriert.
- **`generate_boss()`-Makro-Vertrag:** `kampagnenstruktur.md:149` und `:2409` referenzieren das Makro, ohne dass eine Spec im Repo existiert (Runtime-Implementierung). Patch erweitert das implizite Makro-Verhalten („produziert Phasen-Felder automatisch"). Falls das Makro in `core/sl-referenz.md` dokumentiert sein sollte (Stichprobe: `grep -n "generate_boss" core/sl-referenz.md` → 0 Treffer, nicht dokumentiert) → kein Konflikt. Wenn Makro außerhalb des Repos lebt (Runtime/Tool): Runtime-Adaption ist ein Folge-Ticket, **nicht** dieser Patch.

### 5. Cross-Verweise

| Verweis | Quelle | Ziel | Status |
| --- | --- | --- | --- |
| `core/wuerfelmechanik.md:411` → „Masterprompt §C" und „`gameplay/kampagnenstruktur.md` §Bossphasen-System" | wuerfelmechanik.md:411 | masterprompt §C / kampagnenstruktur.md:545 (`{#bossphasen-system}`) | ✓ |
| `meta/masterprompt_v6.md:160` → „Bosskampf-Pflichtgate" (Selbst-Referenz §C) | masterprompt §C | masterprompt §C | ✓ |
| `meta/masterprompt_v6.md:169` → „`gameplay/kampagnenstruktur.md` §Bossphasen-System" | masterprompt:169 | kampagnenstruktur.md:545 | ✓ |
| `gameplay/kampagnenstruktur.md:550` → „Masterprompt §C **Bosskampf-Pflichtgate**" | kampagnenstruktur.md:550 | masterprompt:160 | ✓ |
| `gameplay/kampagnenstruktur.md:573` → „Kampfszenen-Pflichtgate (Masterprompt §C)" | kampagnenstruktur.md:573 | masterprompt:143 | ✓ |
| `gameplay/kreative-generatoren-missionen.md:2378` → „`gameplay/kampagnenstruktur.md` §Bossphasen-System" | kreative-generatoren-missionen.md:2378 | kampagnenstruktur.md:545 | ✓ |
| `gameplay/kreative-generatoren-missionen.md:2388` → „`kampagnenstruktur.md` §Bossphasen-System" (relative Form) | kreative-generatoren-missionen.md:2388 | kampagnenstruktur.md:545 | ✓ (relativ vs. absolut zu 2378 inkonsistent — Mini-Fix) |
| Signaturtell-Update (kampagnenstruktur.md:687–689) → „siehe §Bossphasen-System" | kampagnenstruktur.md:689 | kampagnenstruktur.md:545 | ✓ (interner Abschnittsverweis ohne expliziten Anchor — funktioniert für Leser, kein Markdown-Link) |

- **Kein expliziter `{#signaturtell}`-Anchor** im bestehenden Markdown, daher kein toter Link, aber auch keine Rückreferenz vom Bossphasen-System zum Signaturtell-Abschnitt. **Optional-Fix:** `{#signaturtell}` an Z.674 ergänzen und im neuen §Bossphasen-System einen Hinweis „Belohnungs-Variante: §Signaturtell" — nicht-blockierend.
- **`{#kampfszenen-pflichtgate}`** existiert nicht als Anchor in Masterprompt (Masterprompt ist nicht heading-anchored, weil §-Notation). Konsistent mit anderen §C-Verweisen im Repo.
- **Pfad-Konsistenz:** Einmal absolut (`gameplay/kampagnenstruktur.md`), einmal relativ (`kampagnenstruktur.md`) in `kreative-generatoren-missionen.md`. Beide funktionieren in Markdown-Renderern, aber stilistisch uneinheitlich. **Mini-Fix:** beide auf absolut vereinheitlichen.

## Empfehlung

**GO mit drei Mini-Fixes** (alle in derselben Branch nachziehbar, kein Re-Review nötig):

1. **`kreative-generatoren-missionen.md:2388`:** Pfad-Form vereinheitlichen.
   ```diff
   - (siehe `kampagnenstruktur.md` §Bossphasen-System)
   + (siehe `gameplay/kampagnenstruktur.md` §Bossphasen-System)
   ```

2. **`gameplay/kampagnenstruktur.md` §Bossphasen-System (nach Z.558, vor „Crew-Sicht"):** Klarstellung Szenen-Span ergänzen.
   ```diff
   + **Szenen-Span:** Ein Bosskampf umspannt typischerweise **2–4 aufeinanderfolgende
   + Szenen** des 12/14-Szenen-Korridors (Mission-Integrität-Pflichtgate). Der
   + Szenen-Zähler tickt während des Bosskampfs weiter; der HUD-Tag
   + `BOSS-Encounter Phase X/Y` bleibt durchgängig. Damit bleibt das Akt-C-Pacing
   + (Showdown + Exfil + Nullzeit-Beat) intakt.
   ```

3. **`gameplay/kampagnenstruktur.md` §Bossphasen-System (am Ende des Abschnitts, nach Builder-Beispiel Z.671):** Migration alter Rift-Seeds klären.
   ```diff
   + **Backward-Compatibility:** Bestehende Rift-Seeds in
   + `gameplay/kreative-generatoren-missionen.md` (Z.2244–2360) ohne explizite
   + `phase_*`-Felder werden zur Laufzeit aus dem Switch-Typ- und Spezialitäten-Pool
   + improvisiert (`boss_stat_hint` „LP X" wird als **LP pro Phase** gelesen).
   + Schrittweise Migration der 5 Bestands-Seeds als Folge-PR.
   ```

4. **Optional (nicht-blockierend):** `{#signaturtell}`-Anchor an `kampagnenstruktur.md:674` ergänzen + Cross-Link aus §Bossphasen-System.

**Commit-Message-Hinweis:** Pflicht-Struktur (Was/Warum/Entscheidungen/Verifikation/Post-Merge-TODOs) bitte verwenden — diff ist groß genug, dass Squash-Merge ohne strukturierte Message Information verliert. Post-Merge-TODO „Migration der 5 Rift-Seeds um `phase_*`-Felder" explizit eintragen.

**Nach den 3 Mini-Fixes: green light für Squash-Merge auf `main`.**
