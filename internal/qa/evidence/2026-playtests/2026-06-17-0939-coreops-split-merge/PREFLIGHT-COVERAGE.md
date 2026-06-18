# PREFLIGHT-COVERAGE: scope-aware `shared_echoes` (campaign-Lane mit Verdichtung)

> Erstellt: 2026-06-17 · Kritiker-Subagent (read-only, keine Änderungen vorgenommen)
> Repo: `/home/altair/.openclaw/workspace-cloud/zeitriss`
> Auftrag: lückenlose Coverage-Map für den geplanten Fix (NICHT Bewertung des Fixes).

## Geplante Änderung (Kontext, nicht zu bewerten)

`continuity.shared_echoes[]` wird **scope-aware**:
- flüchtige Scopes (`shared`/`rumor`/`personal`) behalten engen Cap (~6, dürfen verfallen = gewollt);
- `scope: "campaign"`-Echos bekommen eigene Lane: **kein Hard-Drop**, sondern **Verdichtung** (ältester campaign-Echos werden beim Save/Load zu dichterem Sammel-Anker komprimiert). Soft-Cap triggert Verdichtung, nicht Löschen.

---

## 1. ENFORCEMENT-POINTS (harte Caps) — [HARD-GATE]

Alle diese laufen in `scripts/smoke.sh` (verifiziert: Zeilen 117/127/131/143/194/202/215). Ein einziges scope-blindes `length <= 6` failt sonst CI.

| # | Datei:Zeile | Snippet | Status der Inventur |
|---|---|---|---|
| 1.1 | `systems/gameflow/saveGame.v7.schema.json:402` | `"maxItems": 6` im `shared_echoes`-Block (Block beginnt Z.399) | **KORREKT** (du sagtest ~Z.402). Items haben bereits `scope`-enum `[shared,rumor,campaign,personal]` (Z.413–420). Hier muss der scope-aware Soft/Hard-Cap rein — JSON-Schema kann das **nicht** bedingt-pro-scope ausdrücken (kein `if/then` auf Array-Item-Ebene gegen Gesamtlänge). → **Falle, siehe §5.1.** |
| 1.2 | `systems/gameflow/saveGame.v7.export.schema.json:508` | `"maxItems": 6` im `shared_echoes`-Block (Z.506) | **KORREKT, von dir nur als „auch prüfen" markiert — bestätigt: Treffer.** ACHTUNG: Export-Schema-Block ist **flach** (nur `type`+`maxItems`, KEINE `items`/`scope`-Definition). Wenn campaign-Lane den Gesamt-Cap anhebt, muss auch dieser Wert mitgezogen werden, sonst lehnt Export legitime Saves ab. |
| 1.3 | `tools/test_v7_schema_consistency.js:58` | `assert.ok(continuity.shared_echoes.length <= 6, ... überschreitet Budget (max 6).)` | **KORREKT** (du sagtest ~Z.58). Scope-blind. Muss scope-aware werden (z. B. nur flüchtige Scopes zählen, oder campaign separat gegen Soft-Cap). |
| 1.4 | `tools/test_save_budget_watchguard.js:22` | `assert.ok(/shared_echoes[\s\S]{0,40}max\s*6/i.test(text), ...)` | **KORREKT** (du sagtest ~Z.22). Das ist ein **Doku-Regex-Guard** gegen `speicher-fortsetzung.md` — er erzwingt, dass dort der String „shared_echoes … max 6" steht. Wenn die Doku auf scope-aware umformuliert wird (z. B. „flüchtig max 6, campaign verdichtet"), bricht dieser Regex. → **Falle, siehe §5.2.** |

---

## 2. DOKU / KANON-SSOT — [DOKU-SSOT]

| # | Datei:Zeile | Snippet | Anmerkung |
|---|---|---|---|
| 2.1 | `meta/masterprompt_v6.md:1170–1176` | „**`shared_echoes`-Pflichtformat (Split/Merge)** … `{ "tag", "scope": "shared\|rumor\|campaign\|personal", "text" }` … Merge: `scope`-Konflikte via Priorität `shared > campaign > rumor > personal`" | **Schema-SSOT** (AGENTS.md: Masterprompt = Schema-SSOT). Hier KEIN numerischer Cap genannt — der Cap lebt nur in Doku/Schema/Test. Hier muss die Lane-Trennung kanonisiert werden. **Verifiziert: Masterprompt nennt nirgends „shared_echoes max N"** (grep leer). |
| 2.2 | `meta/masterprompt_v6.md:311` | Split-Debrief schreibt verfehlte Ziele als `{tag: "folgespur-ms<n>-<thread_id>", scope: "campaign", text:…}` | **DAS ist der Produzent, der campaign-Echos in Massen erzeugt** (genau der Playtest-Befund: 8/9 = campaign). Hier muss klar werden, dass diese Lane verdichtet statt gedroppt wird. |
| 2.3 | `meta/masterprompt_v6.md:312` | Briefing-Pull „bevorzugt Echos mit `scope: shared` oder `scope: campaign`" | **Konsument.** Wenn campaign-Echos verdichtet werden, muss der Briefing-Pull auch den Sammel-Anker lesen können (nicht nur Einzel-Echos). |
| 2.4 | `meta/masterprompt_v6.md:293` | Continuity-Anker-Pflicht zieht u. a. aus `continuity.shared_echoes[]` | Konsument-Referenz, scope-neutral — vermutlich unverändert ok, aber prüfen ob verdichteter Anker dieselbe Form hat. |
| 2.5 | `meta/masterprompt_v6.md:604–605`, `:748` | shared_echoes als Quelle für Director-Relevanzsatz / Save-Felder-Liste | Reine Referenzen, kein Cap. Konsistenz-Check ob neue Lane/Format erwähnt werden muss. |
| 2.6 | `core/sl-referenz.md:1452` | „**Kontinuitäts-Budget:** `roster_echoes` max 5, `shared_echoes` max 6, `convergence_tags` max 4 …" | **KORREKT** (du sagtest ~Z.1452). Zweite Doku-Stelle mit hartem „max 6"-Wording. Muss mit 1.4/2.7 konsistent umformuliert werden. |
| 2.7 | `systems/gameflow/speicher-fortsetzung.md:1089` | „`roster_echoes[]` (max 5), `shared_echoes[]` (max 6), `convergence_tags[]` (max 4)." | **Dies ist die Datei, die `test_save_budget_watchguard.js` per Regex prüft** (Z.11–14 des Tests laden `speicher-fortsetzung.md`). KORREKT, du hattest „Save-Größenbudget" referenziert — der eigentliche Regex-Anker sitzt aber hier in Z.1089, nicht im Save-Größenbudget-Block Z.392ff (dort steht `shared_echoes` NICHT, daher Z.392 unkritisch für 1.4). |
| 2.8 | `systems/gameflow/speicher-fortsetzung.md:1090` | Pflichtformat `shared_echoes[]` mit scope-enum (inkl. `campaign`) | Format-SSOT, muss Lane-Regel spiegeln. |
| 2.9 | `systems/gameflow/speicher-fortsetzung.md:1105` | „Bei HQ-`!save` werden ältere Echos verdichtet (Prune), nicht unkontrolliert gestapelt." | **WICHTIG: Hier existiert das Verdichtungs-Prinzip für Echos schon als Einzeiler** — aber scope-blind und ohne campaign-Sonderlane. Das ist der natürliche Andock-Punkt; siehe §5.3 (Mirror). |
| 2.10 | `gameplay/kampagnenstruktur.md:1222` | „`scope: "campaign"` getragen (episodenübergreifend, **kein Cap**, reift über Epochenwechsel …)" | **KORREKT — DER WIDERSPRUCH.** ABER: Dieser Satz spricht laut Kontext (Z.1220) von **`research`-Projekten** mit scope:campaign, NICHT von `shared_echoes`. → **Präzisierung/Falle, siehe §5.4.** |
| 2.11 | `gameplay/kampagnenstruktur.md:1031` | „… `shared_echoes`-Merge-Regel `shared > campaign > rumor > personal`" | Merge-Prioritäts-Referenz (dedupe). Bei Lane-Trennung prüfen ob Priorität noch gilt. |
| 2.12 | `gameplay/kampagnenstruktur.md:847` | Continuity-Rückverweis zieht u. a. aus `continuity.shared_echoes[]` | Konsument-Referenz, scope-neutral. |
| 2.13 | `systems/gameflow/speicher-fortsetzung.md:392–398` | „Save-Größenbudget … Beim Pruning bleiben die neuesten Einträge erhalten; ältere Detailstände werden kompakt in `summaries.*` verdichtet, statt still verloren zu gehen." | **Mirror-Vorlage Nr. 2:** Es gibt bereits ein etabliertes „verdichten in summaries statt löschen"-Muster (für trace/notes/hooks). Echo-Verdichtung sollte sich daran anlehnen statt neu zu erfinden. |
| 2.14 | `systems/toolkit-gpt-spielleiter.md:119`, `:1136` | shared_echoes als Echo-Ablage (Named-Target-Echo) bzw. Briefing-Relevanzsatz-Quelle | Konsument. Format-Konsistenz prüfen. |

---

## 3. DOWNSTREAM-KONSUMENTEN — [DOWNSTREAM]

| # | Datei:Zeile | Was liest/prüft es | Scope-Differenzierung? |
|---|---|---|---|
| 3.1 | `runtime.js` | **`grep "shared_echoes" runtime.js` = 0 Treffer.** runtime.js berührt `shared_echoes` NICHT (nur generisches `state.campaign`, das ist ein anderes Feld!). | **Kein runtime.js-Code-Change nötig.** AGENTS.md-Spiegelpflicht (runtime ↔ WS) greift hier nicht, weil runtime das Feld gar nicht kennt. Entwarnung. |
| 3.2 | `tools/test_continuity_output_contract.js:38–44` | liest `fixture.continuity.shared_echoes`, prüft per `echo_followup.imported_echo_ref` ob ein referenzierter `shared:<tag>` existiert | **Indirekt scope-relevant:** Test prüft Existenz eines Echos nach `tag`. Wenn Verdichtung campaign-Echos zu Sammel-Anker fusioniert, könnte ein referenzierter `tag` verschwinden → Test bricht, falls Fixture-Echo wegverdichtet wird. Fixture-Echo ist `scope:campaign` (§4.1) → **Falle, siehe §5.5.** |
| 3.3 | `tools/test_v7_smart_merge_3_2.js:11` | `assert ... shared_echoes.length >= 1` (Konvergenz-Echo muss existieren) | Untergrenze, scope-blind. Verdichtung darf nicht auf 0 fallen. Niedriges Risiko (Fixture hat genau 1 campaign-Echo). |
| 3.4 | `tools/test_v7_personal_export.js:9–11` | `shared_echoes.length >= 1` UND `<= 3` (Personal-Export-Cap) | **Eigener, separater Cap (max 3) im Personal-Export!** Du hattest diesen Pfad nicht in der Inventur. Frage: Gilt für Personal-Export weiterhin Hard-3 (auch für campaign-Echos), oder erbt er die Lane-Logik? Fixture-Echo ist campaign (§4.2). → **Falle, siehe §5.6.** |
| 3.5 | `tools/test_v7_schema_consistency.js:65–68` | Pflichtformat-Check: jedes Item Objekt mit non-leerem `tag` | Der **verdichtete Sammel-Anker muss selbst schema-konform** sein (`tag` non-empty, gültiger `scope`). Verdichtung darf kein `{echo:...}`-Fremdformat erzeugen. |
| 3.6 | `tools/test_kausalabfang_watchguard.js:45` | Regex `/continuity\.shared_echoes\[\]/i` muss in 4 SSOT-Docs vorkommen | Doku-Anker-Guard. Solange das Token `continuity.shared_echoes[]` in den Docs bleibt, unkritisch — aber beim Umschreiben nicht versehentlich entfernen. |
| 3.7 | `tools/test_npc_continuity_consistency.js` | prüft `npc_roster`/`active_npc_ids`, NICHT shared_echoes-Länge | Kein direkter Treffer auf shared_echoes-Cap. Entwarnung für dieses Test. |

**Merge-Priorität `shared > campaign > rumor > personal`:** Diese Regel löst **scope-Konflikte beim Dedupe gleicher `tag`** (zwei Saves, gleicher tag, verschiedene scopes → welcher gewinnt). Sie kollidiert **nicht** zwingend mit der Lane-Trennung — sie operiert auf einer anderen Achse (tag-Dedupe vs. Lane-Cap). ABER: Inkonsistenz-Gefahr — wenn campaign eine eigene „nie droppen"-Lane bekommt, aber in der Dedupe-Priorität **unter** `shared` steht, kann ein campaign-Echo bei tag-Kollision trotzdem von einem shared-Echo überschrieben werden. Konsistenz explizit klären (Doku 2.1/2.11).

---

## 4. FIXTURES — [FIXTURE]

Drei Fixtures enthalten `shared_echoes` mit `scope:"campaign"` (alle anderen haben leeres `shared_echoes: []`):

| # | Datei:Zeile | Inhalt | Risiko bei scope-aware Cap |
|---|---|---|---|
| 4.1 | `internal/qa/fixtures/continuity_output_contract_multi_load.json:39` | 1× campaign-Echo; referenziert von `echo_followup.imported_echo_ref` (Test 3.2) | Verdichtung darf diesen tag nicht eliminieren, sonst bricht Contract-Test. |
| 4.2 | `internal/qa/fixtures/savegame_v7_personal_export_from_group.json:95` | 1× `{tag:"echo:morgenrot", scope:"campaign"}`; Test prüft `<= 3` (3.4) | Lane-Frage Personal-Export (§5.6). |
| 4.3 | `internal/qa/fixtures/savegame_v7_split_3_2_merge.json:109` | 1× `{tag:"morgenrot", scope:"campaign"}`; Test prüft `>= 1` (3.3) | Niedrig. |

**Coverage-Lücke bei Fixtures:** Es gibt **keine** Fixture mit >6 campaign-Echos oder einem Mix flüchtig+campaign jenseits des Caps. Wenn der Fix scope-aware Verdichtung einführt, **fehlt eine Test-Fixture, die genau diesen Fall abdeckt** (z. B. 8 campaign + 2 shared → flüchtige bei 6 gekappt, campaign verdichtet auf Sammel-Anker). Ohne neue Fixture ist die neue Lane untested. → empfohlene Ergänzung, nicht nur Touch.

---

## 5. WIDERSPRÜCHE / FALLEN — [WIDERSPRUCH]

### 5.1 JSON-Schema kann scope-bedingten Cap nicht ausdrücken
`maxItems` ist eine flache Array-Länge. Ein „flüchtig ≤6, campaign unbegrenzt/soft" lässt sich in JSON-Schema **nicht** als `maxItems` formulieren (kein bedingter Count auf Item-Property-Basis ohne `contains`/`minContains`-Verrenkungen, die hier nicht greifen). → Entweder Gesamt-`maxItems` anheben (z. B. auf realistischen Deckel inkl. campaign) **und** die scope-Logik in den **JS-Test** + **Masterprompt-SL-Regel** verlagern, oder Schema lässt Cap ganz weg und Test/Doku tragen ihn. **Beide Schemas (1.1 + 1.2) müssen denselben Wert tragen.**

### 5.2 `test_save_budget_watchguard.js:22` Regex bricht bei Umformulierung
Der Guard erzwingt das wörtliche Muster `shared_echoes … max 6` in `speicher-fortsetzung.md`. Jede scope-aware Neuformulierung der Doku-Zeile (2.7, Z.1089) **failt diesen Test**, wenn der Regex nicht parallel angepasst wird. Test UND Doku müssen im selben Commit geändert werden.

### 5.3 Zwei bereits existierende Verdichtungs-Muster — nicht neu erfinden
- `speicher-fortsetzung.md:1105`: „Bei HQ-`!save` werden ältere Echos verdichtet (Prune), nicht unkontrolliert gestapelt." (scope-blind, aber das Prinzip steht da schon)
- `speicher-fortsetzung.md:392–398` + `masterprompt:1198`: „ältere Einträge verdichten, nicht löschen" → kompakt in `summaries.*` für trace/notes/hooks.

Der Fix sollte sich an diesem etablierten „verdichten-statt-löschen + Sammel-Anker in summaries"-Muster **anlehnen**, nicht eine fünfte Mechanik erfinden. Frage, die der Fix beantworten muss: Landet der campaign-Sammel-Anker **innerhalb `shared_echoes[]`** (als verdichtetes Echo-Objekt) oder in `summaries.summary_active_arcs`? Das entscheidet, welche Tests/Schemas betroffen sind.

### 5.4 Der „kein Cap"-Satz (Z.1222) gilt `research`, NICHT `shared_echoes`
Genau gelesen (Kontext Z.1220–1224): „Der epochenübergreifende Strang wird **allein über `research`-Projekte** mit `scope: "campaign"` getragen … kein Cap, reift …". Das ist **research.projects[]**, nicht continuity.shared_echoes[]. → **Subtile Falle:** Der Playtest-Befund („8/9 Echos sind campaign, sollten kein Cap haben") stützt sich auf eine Doku-Zeile, die **strenggenommen vom research-Feld spricht**. Der Fix muss diesen Unterschied auflösen: Entweder (a) der rote Faden gehört wirklich in `research` (dann ist shared_echoes-Überfüllung ein SL-Fehlverhalten, kein Cap-Problem), oder (b) shared_echoes bekommt explizit dieselbe „campaign reift"-Semantik wie research — dann muss Z.1222 erweitert werden, dass auch shared_echoes:campaign so behandelt wird. **Diese Mehrdeutigkeit ist die gefährlichste, weil sie die ganze Fix-Prämisse berührt.**

### 5.5 Contract-Test referenziert per `tag` — Verdichtung kann Referenz brechen
`test_continuity_output_contract.js:42–44` sucht den exakten `tag` in `shared_echoes`. Wenn die Verdichtungs-Mechanik mehrere alte campaign-Echos zu einem Sammel-Anker mit **neuem** tag fusioniert, verschwindet der referenzierte tag → Test failt. Verdichtung braucht eine Regel: referenzierte/junge Echos nicht wegverdichten, oder Sammel-Anker behält die Original-tags als Sub-Liste.

### 5.6 Zweiter, unabhängiger Cap im Personal-Export (max 3) — in Inventur gefehlt
`test_v7_personal_export.js:11` erzwingt `shared_echoes.length <= 3` **zusätzlich** zum Haupt-6er-Cap. Dieser Pfad war in deiner Inventur nicht erfasst. Der Fix muss entscheiden: Erbt der Personal-Export die campaign-Lane (dann kann er >3 campaign-Echos tragen → Test anpassen), oder bleibt Personal-Export hart bei 3 (dann muss Verdichtung VOR dem Export laufen)? Fixture 4.2 hat genau 1 campaign-Echo, maskiert das Problem aktuell.

---

## Zusammenfassung Fundstellen

- **[HARD-GATE]** 4: schema (×2), `test_v7_schema_consistency.js:58`, `test_save_budget_watchguard.js:22`
- **[DOKU-SSOT]** 14 Referenzen über 5 Dateien (masterprompt, sl-referenz, speicher-fortsetzung, kampagnenstruktur, toolkit) — Kern: masterprompt §I/§D 1170, 311, 312; sl-referenz 1452; speicher 1089/1090/1105
- **[DOWNSTREAM]** 6 relevant; **runtime.js NICHT betroffen** (0 Treffer → AGENTS.md-Spiegelpflicht greift nicht)
- **[FIXTURE]** 3 mit campaign-Echos + 1 fehlende Test-Fixture für den >6-campaign-Fall
- **[WIDERSPRUCH]** 6 Fallen (§5.1–5.6)

## Die 3 kritischsten Fallen, die beim Fix garantiert übersehen werden

1. **§5.4 — „kein Cap" (kampagnenstruktur Z.1222) gilt `research`, nicht `shared_echoes`.** Die Fix-Prämisse stützt sich auf eine Doku-Zeile über ein anderes Feld. Vor dem Code: klären, ob der rote Faden überhaupt in shared_echoes gehört oder in research — sonst löst der Fix das falsche Problem.
2. **§5.2 + §5.6 — zwei versteckte Zweit-Caps:** (a) `test_save_budget_watchguard.js:22` ist ein **Regex-Doku-Guard**, der bei jeder Umformulierung der „max 6"-Zeile bricht; (b) `test_v7_personal_export.js:11` hat einen **separaten `<= 3`-Cap**, der in der Inventur fehlte. Beide failen lautlos im Smoke, wenn nur Schema+Hauptkonsistenz-Test angefasst werden.
3. **§5.1 + §5.5 — Schema kann scope-Cap nicht, und Verdichtung bricht tag-Referenzen:** JSON-Schema (beide Dateien!) trägt nur flaches `maxItems`; die scope-Logik muss in Test+Masterprompt wandern, beide Schema-Werte synchron. Und der Contract-Test referenziert Echos per exaktem `tag` — Verdichtung mit neuem Sammel-tag killt diese Referenz.
