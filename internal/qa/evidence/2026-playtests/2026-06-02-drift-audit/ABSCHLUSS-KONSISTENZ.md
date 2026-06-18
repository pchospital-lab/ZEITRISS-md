# Abschluss-Konsistenz-Audit

> Worker-Run 2026-06-02. Finaler Lese-Audit über den Gesamtstand nach 8 Spielgefühl-PRs (#3192–#3200) + Schema-Fix.
> Status: ABGESCHLOSSEN.
> Audit-Stand: HEAD = `feat/verlust-beats-und-heat-lebenszyklus` (= main + 1 Commit: Verlust-Achse-PR #3200, der letzte der 8). Alle 8 Spielgefühl-PRs + Schema-Fix #3196 sind im geprüften Stand enthalten.

## Methode
- Reiner Lese-Audit. grep/read über masterprompt, Save-Schema, Handbuch, Cross-Refs.
- smoke.sh ausgeführt: JA → grün (Exit 0, alle Checks passed). JSON-Schemas zusätzlich per python3-Parse verifiziert.
- Befunde mit Datei:Zeile + Zitat. Klassen: KRITISCH / KOSMETISCH / KEIN-PROBLEM.

## Pro Punkt 1–7 Befund

### 1. Beat-Konsistenz quer
**Befund: WEITGEHEND KONSISTENT, eine kleine Lücke.**

**Beat-Dosierungs-Rang (§F Z474)** listet 11 Einträge:
`Prestige-Meilenstein > Beförderung > Lizenz-Tier > Level-Up > Px-5-Riss-Ortung > Heat-5-Fahndung > Scheitern > Px-Resonanz(Normal) > Heat-3 > Research-ready > Research-Tick`.

Abgleich gegen alle real existierenden **Debrief/Progression-Beat-Gates**:
- Level-Up-Belohnungs-Beat (§F 679) → im Rang ✓
- Beförderungs-Beat / Aufstieg (§F 676–678) → im Rang (Beförderung + Lizenz-Tier) ✓
- Prestige-Meilenstein (§F 666) → im Rang ✓
- Px-Resonanz + Px-5-Payoff (§F 524–525) → im Rang (beide Stufen) ✓
- Research-Tick/ready (§C 98) → im Rang ✓
- Heat 3/5 (§F 529–531) → im Rang ✓
- Scheitern (kampagnenstruktur:853) → im Rang ✓

**Querverweise stimmig:** §C-Debrief (Z98) verweist auf §F Beat-Dosierungs-Pflichtgate; Heat-Debrief-Beat (§F 532) und Scheiterns-Beat (kampagnenstruktur:861) verweisen beide explizit auf „unter dem Beat-Dosierungs-Budget (§F)“; Fail-Forward-Verdeckung (§F 533) gilt querschnittlich für ALLE Verlust-Beats und wird vom Scheiterns-Beat rückverwiesen. Das geteilte Budget (Verlust + Belohnung teilen sich 1 voller Beat) ist in Rang-Regel 2 sauber spezifiziert. **Keine Widersprüche zwischen zwei Gates gefunden.**

**Kleine Lücke (KOSMETISCH):** Der **Stress-Schwellen-Beat** (zustaende:332) und der **Fraktions-Beobachter-Beat** (kampagnenstruktur:200) stehen **nicht** im Beat-Dosierungs-Rang. Verteidigbar, weil beide **In-Mission-Beats** sind (Stress feuert im Feld bei Schwelle 5/10 und wird vor dem Debrief auf HQ-Basis=0 resettet; Fraktions-Wurf bei Missionsbeginn), während der Rang primär die **Debrief/HQ-Gleichzeitigkeit** ordnet. Da §F-Geltungsbereich aber „jede Phase mit potenziell mehreren Beats“ sagt, wäre ein Halbsatz („In-Mission-Beats — Stress, Fraktion, Spotlight — folgen demselben max-1-voller-Beat-Budget pro Szene“) sauberer. Die generische Budget-Regel greift ohnehin; kein Regelbruch.

### 2. Save-Schema-Vollständigkeit
**Befund: KONSISTENT.** Alle drei neuen persistenten Werte geprüft über 3 Orte (Masterprompt-JSON-Template, runtime `saveGame.v7.schema.json`, `saveGame.v7.export.schema.json`):

- **`research.projects[]`** (root): im Masterprompt-Template (Z1040), runtime-Schema **explizit als Property** (Z151, #3196-Fix), export-Schema explizit (Z301). Nicht in root-`required` → optional, Migrations-Default `{ projects: [] }`. ✓
- **`campaign.heat`** (0–5): im Masterprompt-Template (Z986), export-Schema **explizit als Property** mit `min 0 max 5` (Z76). Im runtime-Schema **nicht explizit deklariert, aber zulässig** über `campaign.additionalProperties: true`. Nicht in `campaign.required` → optional, Default 0. ✓
- **`characters[].prestige`**: im export-Schema **explizit** (Z207, `{level_titles[], perks[]}`). Im runtime-Schema nicht deklariert, aber via `characters.items.additionalProperties: true` zulässig. **NICHT** im Masterprompt-JSON-Save-Template (siehe Punkt 6 — kosmetische Doku-Lücke). Nicht in `characters.required` → optional. ✓

**Asymmetrie ist kein Bug, sondern by design:** runtime-Schema = `additionalProperties: true` (toleriert alles, deklariert nur was es validieren will) → heat/prestige müssen dort nicht stehen. export-Schema = `additionalProperties: false` (streng) → **muss** jedes Feld deklarieren, sonst export-invalide. Beide behandeln alle drei als **optional** (kein `required`, Default vorhanden, Alt-Saves valide). Verifiziert per `python3 json`-Parse aller drei Stellen. Smoke `v7-schema-consistency-ok` + `v7-character-schema-watchguard-ok` grün.

### 3. Debrief-Sequenz (lang §C vs. kurz §F)
**Befund: DECKUNGSGLEICH.**

- **§C (Z98):** Score-Screen → Loot-Recap → CU-Auszahlung → XP/Level-Up (Belohnungs-Beat) → ITI-Ruf-Update (Beförderungs-Beat) → Px-Resonanz-Beat → Research-Tick → Lizenz-Tier (Freischalt-Beat).
- **§F (Z592):** Bewertung → Loot-Recap → CU-Auszahlung → XP/Level-Up (Belohnungs-Beat) → ITI-Ruf-Update (Beförderungs-Beat) → Px-Resonanz-Beat → Research-Tick → Lizenz-Tier (Freischalt-Beat).

„Score-Screen“ (§C) = „Bewertung“ (§F, erster Schritt) — identische Reihenfolge, identische Beat-Marker. §F verweist als SSOT explizit auf §C („Vollständige Reihenfolge + Beat-Pflichten siehe Mission-Transition-Pflichtgate §C“). Scheiterns-Beat und Heat-Debrief-Beat tauchen in keiner der zwei Inline-Sequenzen auf — korrekt, da es **bedingte Konsequenz-Beats** sind (nur bei verfehltem Hauptziel / Heat ≥3), die auf den Bewertungs-/Ziel-Spiegel-Schritt aufsatteln, den beide Sequenzen referenzieren. Konsistent mit der Beat-Dosierung.

### 4. Cross-File-Referenzen
**Befund: ALLE GEPRÜFTEN REFERENZEN AUFLÖSBAR.** 12 zentrale neue/relevante `§`- und Pfad-Verweise gegen Zielexistenz geprüft — alle Treffer:
`§Para-Schwereklassen`→begegnungen.md ✓ | `§Beziehungen`→kampagnenstruktur.md ✓ | `§Stress-Reset`→zustaende.md:310 ✓ | `§Prestige`→zeitriss-core.md ✓ | `§Aufstieg`→zeitriss-core.md ✓ | `§ITI-Rang-Mapping`→spieler-handbuch.md ✓ | `§Rift-Loop`→kampagnenstruktur.md ✓ | `§Cineastische Kampf-Beats`→wuerfelmechanik.md ✓ | `§Exfil-Stress-Pflichtgate`→kampagnenstruktur.md ✓ | `§Forensik-Dreieck`→kampagnenstruktur.md ✓ | `§IA/RW-Spot-Generator`→generatoren-missionen.md ✓ | `§Rift-Seed`→generatoren-missionen.md ✓.

Der Doc-Link-Linter (`scripts/lint_doc_links.py`) läuft **grün** (Exit 0, alle Markdown-`#anchor`-Links validiert). Hinweis: `§<Label>`-Verweise (z. B. `§Stress-Reset` → Bold-Label `**Stress-Reset:**` statt H-Heading) sind Repo-Konvention (Sektions-Label, kein Anchor-Link) — vom Linter korrekt nicht als Dead-Link gewertet. **Keine stale Regel-Nummern, keine Dead-Links.**

### 5. Spieler-Handbuch-Sync
**Befund: TEILWEISE SYNCHRON — zwei bereits gefixt, einige bewusste/offene Doku-Lücken.**

**Bereits synchronisiert (in #3197):**
- **Missions-Dauer/Dichte:** Handbuch sagt jetzt „rund 25-30 Min“ (Z1312), „~2-3 Min pro Szene“ (Z1310) — konsistent mit Dichte-Patch (#3192). ✓
- **Rift-Ton:** Handbuch sagt jetzt „Mystery-Casefile, die in **Horror-Action** kippt … handfeste Parawesen, die ein paar Kugeln vertragen“ (Z68–70) — konsistent mit Rift-Horror-Pflichtgate (#3193). ✓

**Konsistent (keine Drift):**
- **ITI-Rang-Mapping** (Z558) + **Tier-Lizenzen** (Z543): Tabellen vorhanden, decken sich mit den `§ITI-Rang-Mapping`/`§Tier-Wirkungsrahmen`-Verweisen der Aufstiegs-Beats (#3198). Der Aufstiegs-Beat ist reine SL-Inszenierung — keine Mapping-Änderung. ✓
- **Px-Mechanik** (Z488ff): ClusterCreate→Rift-Seeds, TEMP-Staffel, „Resonanz“ als Konzept (Z35/877/1165/1292) korrekt beschrieben — deckt die unveränderte Mechanik ab. ✓

**Doku-Lücken (Spieler-Features im Masterprompt geregelt, im Handbuch fehlend/dünn):**
1. **Heat-Lebenszyklus (#3200, frisch):** Handbuch erwähnt `Heat` nur als vage Konsequenz-Währung (Z41 „Konsequenzen über CU, Stress, Heat“; Z261 „Heat +1“), beschreibt **nicht** das neue System: 0–5-Skala, Fahndung bei 5, persistentes `campaign.heat`, HQ-Abbau −1/Episode, „nächste Mission startet unter erhöhtem Druck“. Das ist spieler-relevant (Persistenz + Ausweg). → **Sinnvollster Folge-Schritt** (der PR führt selbst Playtest-first als Post-Merge-TODO — Handbuch-Sync danach).
2. **Research-Fortschritt (#3194):** Handbuch nennt „Forschung“ nur als HQ-Ressource-Turn-Stichwort (Z232). Das `research.projects[]`-System (Tier=Missionen-Dauer, scope episode/campaign, „~3 Einsätze bis Ergebnis“-Ansage an den Spieler) ist größtenteils SL-Buchhaltung, aber die Spieler-Ansage-Mechanik („Analyse läuft — ~3 Einsätze“) könnte einen Satz im Handbuch vertragen. Modest.
3. **Prestige-Meilenstein-Rite (#3198):** Handbuch nennt nur „Prestige-Cap 14“ (Z411) als Attributs-Grenze — die Titel-Verleihung (Lvl 25/50/75/100: Bewährter Agent/Veteran/Koryphäe/Legende) ist nicht beschrieben. Vertretbar als Meilenstein-Überraschung; optional.

Kein **falscher** (widersprechender) Handbuch-Stand gefunden — die Lücken sind Auslassungen, keine Fehlinformationen.

### 6. Vergessenes / nicht-mitgezogene Stellen
**Befund: zwei genannte Sorgen ENTKRÄFTET, eine echte kleine Lücke (Masterprompt-Template), ein Housekeeping-Punkt.**

1. **Stress-Cap-Widerspruch (0/10 fix vs HUD 0/5-6) — NICHT (mehr) in den Live-Regeln.** `git grep` über alle getrackten `*.md`: die `0/5`- und `0/6`-Stress-Notationen erscheinen **ausschließlich in QA-/Playtest-Evidenz** (`docs/qa/playtest-2026-04-25-...`, `internal/qa/evidence/...`) — das sind **Transkripte von Modell-Verhalten**, die den Bug *dokumentieren* (2026-04-25 als „low“ geflaggt: „Stress-Max widersprüchlich im HUD“). Die **Live-Regel-SSOTs** sind konsistent 0–10: `zustaende.md:330` zeigt `Stress 5/10`, `hud-system.md` nutzt `Stress {cur}` + Skala bis 10. → Der Post-Merge-TODO des Verlust-PRs bezieht sich auf jene alten Logs, **nicht** auf einen aktuellen Regelkonflikt. KEIN-PROBLEM (auf Regel-Ebene).
2. **`research_level` (Chronopolis-Integer) vs. `research.projects` — KEINE Verwechslung im Repo.** Die einzige `research_level`-Erwähnung lebt in `systems/toolkit-gpt-spielleiter.md.bak` — und diese `.bak`-Datei ist **nicht getrackt** (`git ls-files | grep .bak` = leer). Das **live** `toolkit-gpt-spielleiter.md` enthält **kein** `research_level` mehr. → Keine Begriffs-Doppelbelegung im ausgelieferten Stand. (Housekeeping: das verwaiste `.bak` auf der Platte könnte man bei Gelegenheit löschen — reines Aufräumen, kein Inhalt.)
3. **`characters[].prestige` fehlt im Masterprompt-JSON-Save-Template (KOSMETISCH).** Der Masterprompt (Z666) nennt `characters[].prestige` als Persistenz-Ziel des Prestige-Akts; das **Export-Schema** deklariert `prestige` explizit (Z207). Aber das **JSON-Save-Vorlage-Objekt im Masterprompt** (Z993–1038, das characters-Beispiel) listet `prestige` **nicht** — anders als `research`/`heat`, die in ihren Vorlage-Blöcken stehen. Da `prestige` optional ist (`additionalProperties:true` runtime, nicht in `required`), bricht nichts; aber die Vorlage ist damit **nicht ganz vollständig** ggü. dem, was der Prompt verspricht. Ein leerer `"prestige": { "level_titles": [], "perks": [] }`-Eintrag im Template wäre sauberer (Parallelität zu `research`). Smoke unberührt davon (grün).
4. **`Heat-Wort`-Tippfehler (KOSMETISCH).** `systems/gameflow/speicher-fortsetzung.md:1479`: „Beim Merge wird der **höhere** Heat-**Wort** beider Threads übernommen (max)“ — soll **Heat-Wert** heißen. Reiner Typo aus dem Verlust-PR, inhaltlich klar.

### 7. Invarianten + Smoke
**Befund: GRÜN.** `bash scripts/smoke.sh` → `All smoke checks passed.` (Exit 0). ~45 Watchguards laufen durch, u. a. `v7-schema-consistency-ok`, `v7-issue-pack-ok`, `v7-character-schema-watchguard-ok`, `save-budget-watchguard-ok`, `px-language-watchguard-ok`, `continuity-output-contract-ok`. Keine Pflicht-Invariante (AGENTS.md) verletzt. Stress-HQ-Reset-Invariante (sl-referenz:280) wurde im Verlust-PR auf **0** festgenagelt (SSOT zustaende.md) — sauber.

## Kritische Befunde (gehört gefixt)

**KEINE.** Kein Befund auf KRITISCH-Stufe. Smoke grün, alle Schemas valide & konsistent (research/prestige/heat sauber optional), keine Dead-Links, keine widersprüchlichen Gates, Debrief-Sequenzen deckungsgleich, keine Mechanik-Zahl versehentlich geändert. Die zwei vorab befürchteten Risiken (Stress-Cap-Widerspruch, research_level-Kollision) sind auf Live-Regel-Ebene **entkräftet**.

## Kosmetisch / später

1. **Tippfehler `Heat-Wort` → `Heat-Wert`** (speicher-fortsetzung.md:1479). 1-Zeichen-Fix.
2. **`prestige` im Masterprompt-JSON-Save-Template ergänzen** (Z~1038, parallel zu `research`): `"prestige": { "level_titles": [], "perks": [] }`. Vollständigkeit der Vorlage, keine Funktionsänderung.
3. **Beat-Dosierungs-Rang um In-Mission-Beats-Halbsatz ergänzen** (Stress/Fraktion/Spotlight teilen sich pro Szene dasselbe max-1-voller-Beat-Budget). Präzisierung, kein Regelbruch.
4. **Verwaistes `systems/toolkit-gpt-spielleiter.md.bak`** auf der Platte aufräumen (nicht getrackt, reines Housekeeping).
5. **Handbuch-Sync nach Playtest:** Heat-Lebenszyklus, Research-Ansage, Prestige-Titel ins Spieler-Handbuch nachziehen (siehe Punkt 5). Die jeweiligen PRs sehen Playtest-first vor — daher bewusst nach der Verifikation.

## Vergessenes-das-reingehört

Nichts **funktional** Vergessenes (kein fehlendes Save-Feld, kein nicht-verankerter Beat, keine tote Mechanik). Die einzigen „hätte-man-mitziehen-können“-Stellen sind **Doku-/Vollständigkeits-Lücken**, alle nicht-blockierend:

- **Größte:** Spieler-Handbuch beschreibt den neuen **Heat-Lebenszyklus** (#3200) noch nicht — ein Spieler erfährt aus dem Handbuch nicht, dass Heat persistent ist und einen Abbau-Ausweg hat. Das ist ein spieler-relevantes Feature; der natürliche nächste Schritt ist ein Handbuch-Sync (nach dem im PR vorgesehenen Playtest).
- **Kleiner:** `prestige` im Masterprompt-Save-Template (Vollständigkeits-Parallelität zu `research`/`heat`).
- **Kleiner:** Research-Spieler-Ansage + Prestige-Titel im Handbuch.

## Gesamturteil

**Der Gesamtstand nach den 8 Spielgefühl-PRs + Schema-Fix ist konsistent und abschlussreif.** Smoke grün (Exit 0, ~45 Watchguards), beide v7-Schemas + Masterprompt-JSON valide, alle drei neuen persistenten Werte (research/prestige/heat) sauber als optional verankert, Debrief-Sequenzen deckungsgleich, alle geprüften Cross-Refs auflösbar, keine widersprüchlichen Gates. **Kein kritischer Befund.** Die Patches haben sich gegenseitig nicht zerschossen — das geteilte Beat-Dosierungs-Budget fängt die Stapel-Gefahr der vielen neuen Beats sauber ab.

**Was übrig bleibt, ist klein:** 1 Tippfehler, 1 unvollständiger Save-Template-Eintrag (kosmetisch), eine Präzisierung im Beat-Rang, und — inhaltlich am wichtigsten — ein noch ausstehender **Handbuch-Sync für den Heat-Lebenszyklus** (sinnvoll nach dem ohnehin geplanten Playtest). Die zwei eingangs befürchteten Risiken (Stress-Cap-Widerspruch, research_level-Kollision) sind auf Regel-Ebene entkräftet — sie spuken nur in alten QA-Logs bzw. einer ungetrackten `.bak`.
