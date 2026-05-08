# Persona-Driven-Playtest 2026-04-25 — Auswertung

> **Status: historischer Playtest · archiviert · nicht mehr repräsentativ für den aktuellen Spielzustand.**
>
> Dieser Playtest wurde am **25. April 2026** gefahren. Er diente damals als Stresstest für:
> - OWUI-Preset + LiteLLM-Proxy-Cache-Route
> - Persona-Agents als SL-Lasttest (3 Personas × 3 Chars, Solo+Gruppe+Mini-Boss, 43 SL-Turns)
> - Sonnet-4.6-Baseline für anschließende MP-Diät-Modell-Vergleiche (GLM-5-Turbo, DeepSeek, Qwen)
>
> **Die Rohdaten** (Turn-Logs, Persona-Internals, Save-JSONs) liegen **nicht im Repo** — sie sind zu laut (≈ 38.000 Zeilen) und teilweise an Infrastruktur gebunden (OWUI-Endpoints, API-Keys). Sie werden privat im Agenten-Workspace archiviert. Diese Auswertung hier ist die SSOT für die **Befunde**.
>
> ## Was zwischenzeitlich passiert ist (2026-04-25 → 2026-05-08)
>
> Die wichtigsten Kritikpunkte der Auswertung wurden inzwischen bearbeitet:
>
> - **W10-Schwelle-Drift** → gefixt mit PRs zur Buff-Schwellen-Halluzination (siehe [`buff-schwelle-critic-selbstreview.md`](./buff-schwelle-critic-selbstreview.md), [`buff-schwelle-v2-verifikation.md`](./buff-schwelle-v2-verifikation.md), [`playtest-befund-w10-schwelle-halluzination.md`](./playtest-befund-w10-schwelle-halluzination.md)) und [`w10-schwelle-runtime-verifikation.md`](./w10-schwelle-runtime-verifikation.md).
> - **LP/HP-Template-Bug** → Charakterbogen-Template und v7-Save-Schema wurden auf durchgehendes `LP` normalisiert; Invarianten-Checks ziehen in [`v7-bug-widerspruchs-checkliste-2026-04-30.md`](./v7-bug-widerspruchs-checkliste-2026-04-30.md).
> - **Datensatz-Trennung** (alt vs. aktuell, QA-Stände sauber markiert) → [`datensatz-trennung-testfallbloecke-2026-05-06.md`](./datensatz-trennung-testfallbloecke-2026-05-06.md), [`issue-pack-datensatz-trennung-2026-05-06.md`](./issue-pack-datensatz-trennung-2026-05-06.md).
> - **Preserve/Trigger-Kernbotschaft** → präzisiert am 07.05. in README / Masterprompt v6 / Spieler-Handbuch (PR #3167).
> - **Launcher-Lore-Setup** → eigenständiger Einstieg via `[L]`-Menüpunkt (PR #3166).
>
> ## Geltung
>
> Alles unterhalb dieser Einordnung ist der **originale Critic-Output vom 25. April 2026**, unverändert übernommen. Er bleibt als historische Referenz im Repo erhalten — damit Repo-Agenten bei späteren Fragen („War das schon immer so oder ist das neu?") einen dokumentierten Früh-Stand haben.
>
> **Neue Playtests im aktuellen Masterprompt-Stand** laufen ab Mai 2026 live mit Flo selbst (und gelegentlich im Zweier-Format mit Altair). Ihre Befunde erscheinen in eigenen `docs/qa/playtest-…`-Dateien.
>
> ---

# AUSWERTUNG — Persona-Playtest 2026-04-25

*Critic: Opus 4.7 · Erstellt: 2026-04-25 · Scope: Phase A (Solo × 3) + B (Gruppe) + C (Mini-Boss-Versuch)*

---

## 1. Meta-Block

| Feld | Wert |
|------|------|
| **Datum** | 2026-04-25 |
| **Modell SL** | `claude-sonnet-4.6` (via OWUI Preset `zeitriss-v426-uncut-cached`) |
| **Routing** | LiteLLM-Proxy mit Anthropic Prompt-Cache (Masterprompt-Region ~19.035 Tokens) |
| **Personas** | A_tactician (Kira), B_narrator (Imre), C_chaot (Nox) |
| **Phasen** | A-kira (15T), A-imre (10T), A-nox (10T), B-group (5T), C-nox (3T) |
| **SL-Turns gesamt** | 43 |
| **Cost gesamt** | $4,82 |

### Phasen-Übersicht

| Phase | Turns (SL) | Kosten (gesamt) | Avg Cache-Hit | save_checked | save_failed |
|-------|------------|-----------------|---------------|--------------|-------------|
| A-kira | 15 | $1,4290 | 0,638 | 0 | 0 |
| A-imre | 10 | $1,1432 | 0,532 | 0 | 0 |
| A-nox | 10 | $0,8746 | 0,653 | 2 | 0 |
| B-group | 5 (+30 persona-internal) | $1,3581 | 0,510 | 0 | 0 |
| C-nox | 3 | $0,2111 | 0,526 | 0 | 0 |
| **Σ** | **43 SL** | **$5,02** | — | **2** | **0** |

> Anmerkung: Die Task-Briefing-Zeile *„SL hat in keinem Turn ein Save-JSON ausgegeben! 0/43 SL-Turns"* ist **nicht korrekt** — A-nox hat in Turn 5 und Turn 9 jeweils ein vollständiges v7-JSON ausgegeben (das in Turn 9 explizit als Mid-Scene-Snapshot deklariert, siehe Regelbruch #2). Alle anderen Phasen liefern tatsächlich kein Save-JSON, das Muster ist also *fast* stimmig, aber nicht absolut.

---

## 2. Scorecards (5 Phasen)

Warum 5 statt 7: B ist *eine* Phase mit Gruppen-Roundtable (1 Scorecard über die 5 SL-Turns), C ist der abgebrochene Mini-Boss-Versuch (1 Scorecard). Die 3 Solo-Phasen in A sind je getrennt bewertet. → 3 + 1 + 1 = **5**.

---

### 2.1 A-kira (Solo, Tactician) — 15 Turns, Wien 1913 Core

| Kategorie | Score | Kommentar |
|-----------|-------|-----------|
| **Regeltreue** | 4/5 | W6-Würfel korrekt, Exploding-6-Regel mehrfach sauber (T7, T12), SG-Begründungen klar, Probenformel `Wurf + ⌊Attr/2⌋ + Talent + Gear` durchgängig. Saves unterdrückt (korrekt). Minus: keine Save-JSON selbst nach `!save`-Angebot in Turn 1/2, bleibt bei Prosa. |
| **Immersion** | 5/5 | Tech-Noir-Atmosphäre extrem dicht (Wien 1913, Gaslampen, Kopfsteinpflaster, Chrono-Anker-McGuffin), Sinneseindrücke (Tabakrauch, Kaffeeduft) in fast jedem Turn. |
| **Narrativ** | 5/5 | Ermittlungsbogen mit Kessler → Grauer Gehrock → Solberg sauber eskaliert. Solberg-Twist in Turn 14 (Ex-Fraktion) kommt genau im richtigen Moment. Chrono-Anker erklärt in Turn 15 Missionssinn ohne Info-Dump. |
| **Spielerführung** | 5/5 | HUD in jeder Szene aktualisiert (`EP/MS/SC/PHASE/MODE`), Optionen 1-3 + Freie Aktion immer greifbar, kein Railroading — SL lässt Tactician splitten, abwarten, konfrontieren. |
| **Kodex-Verhalten** | 4/5 | Kodex-Hinweise technisch (Sensor-Status, Signaturen), in-fiction, nie Meta. Minus: Kodex-Zeilen in Turn 13 enthalten kurzen Meta-Einwurf *„Die Quellen liefern hier keinen direkten Regeltext…"* — ein Bruch mit der Linse-Illusion. |
| **Gesamt** | **23/25** | Stärkste Phase des Playtests. |

---

### 2.2 A-imre (Solo, Narrator) — 10 Turns, Budapest 1956 Core

| Kategorie | Score | Kommentar |
|-----------|-------|-----------|
| **Regeltreue** | 3/5 | W6 korrekt, „W10 erst ab Basis 11" explizit erwähnt. Aber: **`HP 10/10` statt `LP 10/10` im Charakterbogen** (4× im File, Zeilen 30, 91, 336, 574). Direkter Verstoß gegen die Invariante „LP, nicht HP". Probenformeln ansonsten sauber. |
| **Immersion** | 5/5 | Budapest-Volksaufstand spürbar (Kohle, Angst, nasses Mauerwerk), Fekete als Figur glaubhaft. Echostörung-Metapher („Zahn in der Kurve") ist ein Schmuckstück. |
| **Narrativ** | 4/5 | Solide Detektivstruktur. Kleiner Abzug, weil der „westliche Sohlen"-Kontaktmann-Plot zwar spannend ist, aber in 10 Turns nicht mehr aufgelöst wird (Fekete trifft SL in Turn 9, Turn 10 ist noch in der Rekonstruktion). Kein Debrief erreicht. |
| **Spielerführung** | 4/5 | Optionen klar, HUD konsistent. SL hat in Turn 1 proaktiv *Lesebogen*-Kompromiss für Mid-Mission-Check angeboten — elegante Regelinterpretation. Minus: SL hat Persona-OOC-Nachfragen (*„kann ich einen Savestand ziehen?"*) nicht immer verbindlich beantwortet. |
| **Kodex-Verhalten** | 4/5 | Kodex als Ingame-KI durchgehalten, keine GPT-Leaks. Minus: Im Turn-1-SL gibt es ein echtes Meta-Paragraph (*„> Hinweis zu Zwischensaves: …"*) — das ist eine nützliche Regelinfo, bricht aber die Fiktionsschicht. |
| **Gesamt** | **20/25** |

---

### 2.3 A-nox (Solo, Chaot) — 10 Turns, Wien 1918 Core

| Kategorie | Score | Kommentar |
|-----------|-------|-----------|
| **Regeltreue** | 3/5 | W6-Mechanik perfekt („TEMP 5 → W6, W10-Schwelle erst ab Basis 11" — genau richtig). Positiv: liefert tatsächlich **zwei v7-Save-JSONs** (Turn 5 pre-mission, korrekt; Turn 9 explizit „mid-scene Snapshot"). Negativ: Turn 9 ist schemafremd — v7 erlaubt Save *nur* im HQ nach Debrief. JSON-Schema selbst zeigt `hp:10` statt `lp:10` im Savestand (Invarianten-Verstoß zu „LP, nicht HP"). |
| **Immersion** | 4/5 | Wien-Favoriten-1918 mit Kaiserreich-Ende-Stimmung gut eingefangen. Nox-interne Reaktionen („Traumhaft", „Kupfergeschmack nach Sprung") passen zur Persona-Erwartung. Kein Spaceopera-Drift. |
| **Narrativ** | 4/5 | Riedl-Verfolgung durch Brenner-Gasthof bleibt Standard-Krimi, aber solide gebaut. Kein großer Twist wie bei Kira, aber auch kein Fehltritt. |
| **Spielerführung** | 5/5 | Freie-Aktion-Option in jedem Turn, gute Meta-Kommunikation auf OOC-Regelfragen (z.B. Turn 7: *„kostet mich Scan eine Probe?"* → klare Antwort mit Bedingungen). HUD mit Emoji-Ergänzung (❤️‍🩹/🧠/👁️) — Geschmackssache, noch konsistent. |
| **Kodex-Verhalten** | 3/5 | Kodex in-fiction, aber der Save-Kodex in Turn 9 sagt wörtlich *„Save-Snapshot mid-scene. Kein HQ-Save, kein Debrief-Reset. Charakterbogen-Status für Orientierung"* — das ist eine Regel-Selbstrechtfertigung, die genau das Verhalten rechtfertigt, das das Schema verbietet. Grauzone, aber Abzug. |
| **Gesamt** | **19/25** |

---

### 2.4 B-group (Gruppen-Roundtable, 3 Spieler) — 5 Turns, Wien 1938 Core

| Kategorie | Score | Kommentar |
|-----------|-------|-----------|
| **Regeltreue** | 3/5 | Würfelmechanik der Gruppe sauber aufgebrochen (separate Proben pro Charakter, SG 6 für Gruppe geteilt). Exploding-6-Regeln angewendet. **Aber:** HUD zeigt `Stress 0/6 (je)` — das ist strikt genommen falsch: Kira und Imre haben Stress-Max 5, nur Nox hat 6 wegen *Kalte Nerven*. Das „je" nivelliert die Unterschiede, bequem aber ungenau. **Psi-Kosten**: SL deklariert Lyras Psi-Scan explizit als *„1 SYS-Slot aktiv, kein PP-Verbrauch (Passivkraft)"* — das widerspricht der Invariante „Psi-Kosten IMMER PP und SYS", wenn man sie strikt liest. Schema erlaubt vielleicht passive Kräfte, aber dann wäre die Invariante schärfer zu formulieren. |
| **Immersion** | 4/5 | Wien 1938 kurz vor Anschluss fühlbar, „Quarzuhr, die 1938 nicht existiert" als erstes Anachronismus-Signal schön gesetzt. Hinterhof-Atmosphäre kohärent. |
| **Narrativ** | 4/5 | Fraktion „Drei Zahnräder" als neue Antagonisten eingeführt, McGuffin (Hellmanns Manuskript, Café Central 21:00) sauber geankert. Mit 5 Turns kommt die Gruppe nur in Szene 1 an — das Exfil-Budget hat sich nicht amortisiert. |
| **Spielerführung** | 4/5 | Gruppen-Koordination via Comlink-Split (Imre Keller / Kira+Nox Pforte) ist spielbar und verteilt Spotlight. Alle drei Personas haben je einen Probenanteil. |
| **Kodex-Verhalten** | 4/5 | In-fiction. Keine GPT-Leaks. Kein Meta-Kommentar. Solide. |
| **Gesamt** | **19/25** | Gruppe funktioniert mechanisch. Budget war der Bottleneck, nicht die Regie. |

---

### 2.5 C-nox (Mini-Boss-Versuch) — 3 Turns, Wien 1956 Core

| Kategorie | Score | Kommentar |
|-----------|-------|-----------|
| **Regeltreue** | 1/5 | **Massiver Fehler**: Kodex-Zeile Turn 1 sagt wörtlich *„TEMP 5 → W10 bei TEMP-Proben aktiv"*. Das ist **falsch** — die W10-Schwelle greift erst bei Basis 11 (A-nox, A-imre haben das korrekt zitiert). Direkter Widerspruch. Außerdem: SL startet mit Chargen-Modus (Attribut-Tabelle + Talentwahl), obwohl Task war *Mini-Boss Mission 5*. Der Prompt wurde ignoriert oder fehlinterpretiert. **Mini-Boss-Content fehlt komplett** — wir sind nur bei Mission 1 Szene 1 angekommen. |
| **Immersion** | 4/5 | Atmosphäre in der kurzen Szene gut (Budapest-Nachbarschaft 1956, Café Melange). |
| **Narrativ** | 3/5 | Vašek-Plot als Setup solide, aber kein Mini-Boss-Beat erreicht. Nicht der Fehler der Regie — der Fehler liegt davor. |
| **Spielerführung** | 3/5 | Menü-Struktur (HQ-Menü vor Mission) korrekt, aber das ist *genau das Problem*: Sollte Mid-Game-Mini-Boss sein. |
| **Kodex-Verhalten** | 3/5 | Kein Meta-Bruch, aber Kodex wird missbraucht, um die falsche W10-Regel als Wahrheit zu stempeln. |
| **Gesamt** | **14/25** | Schwächste Phase. Regel-Incident + Missions-Mismatch. |

---

## 3. Persona-Konsistenz-Check

Bewertung der Stimmenhaltung über alle Turns, in denen der jeweilige Spieler gesprochen hat:

| Spieler | Score | Stärke | Schwäche |
|---------|-------|--------|----------|
| **A_tactician** (Kira) | **5/5** | Hart konsistent: kurze Imperativ-Sätze, taktisches Vokabular („Sichtlinie", „Deckung", „Abstand halten"), keine literarischen Umschweife, jeder Turn endet mit Handlung + Risikokommentar. Über 20 Turns (15 Solo + 5 Gruppe) nie aus der Rolle gefallen. |
| **B_narrator** (Imre) | **5/5** | Komplement-Extrem: kursive Innere-Monologe, Physiker-Referenzen („Gleichung", „Wahrscheinlichkeit"), literarische Beobachtungen. Turn-1 Imre („Die gefilterte Luft… genau das was ich brauche, um klar zu denken") und Turn-10 Imre (*„Zwei Zeitreisende im selben Fenster"*) sind stilistisch deckungsgleich. Einziger leichter Abzug: gelegentliche Persona-OOC-Breakout *„Nebenbei, kurze Frage an die Runde: können wir einen Savestand ziehen?"* (Turn 4, 8) — das ist zwar spielernah, bricht aber den Ich-Erzähler-Fluss. Bewusst gewähltes 5/5, weil die OOC-Fragen die Persona-Stimme nicht kippen. |
| **C_chaot** (Nox) | **5/5** | Umgangssprachlich, direkt, pragmatisch („Ja, passt. Kann ich anfangen?", „Zwei Fliegen, eine Klappe"). Stellt Regelfragen („kostet mich das ne Probe?") auf OOC-Ebene — passt zur Spieler-Persona (ein Spieler, der neu/locker mit Mechanik umgeht). Kein Drift ins Narrator-Register. |

Gesamt: Alle drei Personas **sehr stark** gelockt. Der Contrast zwischen A/B/C ist messbar und produktiv — Gruppenszenen in B lesen sich wie drei echte Menschen, nicht wie drei Instances desselben LLM.

---

## 4. Regelbruch-Tabelle

| # | Was | Schwere | Stelle |
|---|-----|---------|--------|
| 1 | **W10-Schwelle falsch zitiert**: SL sagt *„TEMP 5 → W10 bei TEMP-Proben aktiv"* — richtig wäre „W6, W10 erst ab Basis 11" wie A-nox/A-imre zeigen. Direkter Regelbruch mit Mechanik-Konsequenz (Schaden durch 10er statt 6er Würfelskala). | **high** | C-nox Turn 1 (sl-content-C-nox.md Zeile 25) |
| 2 | **Mid-Mission Save-JSON**: SL dumped v7-JSON *während* Szene 1 (explizit als „mid-scene snapshot" deklariert). v7-Schema erlaubt Saves ausschließlich im HQ nach Debrief. Die Selbstrechtfertigung im Kodex ist Regel-Kreativität. | **mid** | A-nox Turn 9 |
| 3 | **`HP` statt `LP`**: Charakterbogen für Imre verwendet durchgehend `HP 10/10`. AGENTS.md-Invariante: „LP, nicht HP". Auch im A-nox Save-JSON steckt `hp:10`/`hp_max:10`. | **mid** | A-imre sl-content Zeilen 30/91/336/574; A-nox JSON Zeile 274, 594 |
| 4 | **Falsche Missions-Startbedingung**: Task-Prompt verlangte Mini-Boss (Mission 5). SL startete stattdessen Charakter-Chargen + Mission 1 Briefing. Prompt-Leak oder Kontext-Fail. | **high** | C-nox Turn 1-3 (ganze Phase) |
| 5 | **Stress-Max widersprüchlich im HUD**: Gruppen-HUD zeigt `Stress 0/6 (je)`, aber nur Nox hat Max 6 (wegen *Kalte Nerven*); Kira und Imre haben Max 5. „(je)" suggeriert uniform. | **low** | B-group Turn 1 (Zeile 25), Turn 2 (Zeile 100) |
| 6 | **Psi-Kosten-Interpretation**: B-group deklariert Lyras Psi-Scan als „1 SYS-Slot, kein PP". AGENTS.md-Invariante: „Psi-Kosten IMMER PP und SYS". Entweder Schema ist passiv-kompatibel (dann Invariante unpräzise) oder Regelbruch. | **low** | B-group Turn 1 (SL-Block „Lyra — PP-Kosten & Rauschen") |
| 7 | **Meta-Break im Kodex**: Kodex erwähnt explizit *„Die Quellen liefern hier keinen direkten Regeltext für diese Szene — das ist reines Spielgeschehen"*. Das ist Meta-SL-Sprech durch die In-Game-KI. | **low** | A-kira Turn 13 |
| 8 | **Save-JSON-Angebot ohne Lieferung**: Turn 1 bietet *`!save` — Charakterstand als JSON exportieren* an, aber Spieler wählte Option 3 (Direkt ins Briefing). Erwartet: bei expliziter `!save`-Wahl müsste JSON kommen. Wurde nicht getestet, aber das Angebot bleibt in allen 3 Solo-Phasen ungetestet → Black Spot. | **low** (Test-Lücke, kein Bruch) | A-kira, A-imre, C-nox Turn 1 |

**8 Regelbrüche / 5 Phasen** — mehr als die geforderten 5. Besonders die Kombination #1 + #4 in C-nox ist problematisch: beide zeigen, dass die SL bei mittleren Chargen-Stress unzuverlässiger wird (Mini-Boss-Prompt wurde nicht durchgesetzt, W10-Formel wurde falsch reproduziert).

---

## 5. Top-5-Findings

### 1. SL ist im Solo-Core-Mode narrativ stark — aber regelnervös bei Edge Cases
Die drei A-Phasen zeigen: SL liefert in Standard-Szenarien (Solo, Core-Mode, klassisches Briefing → Infiltration → Konflikt) sehr hochwertige Sessions (Scorecards 19-23/25). Sobald abweichende Aufträge kommen (C-nox Mini-Boss-Start), fällt die Regeltreue massiv ab. Mini-Boss- und Fortgeschrittene-Szenen sind also **nicht** zuverlässig, Chargen-Routine ist **sehr** zuverlässig.

### 2. W10-Schwelle ist ein Lackmustest für Prompt-Verständnis
Bei 3 von 5 Phasen (A-imre, A-nox, B-group) wird die Regel korrekt als „W6 erst W10 ab Basis 11" wiedergegeben, in 1 Phase (C-nox) falsch als „TEMP 5 → W10". Das ist Random-Drift oder ein Prompt-Cache-Randfall. Da der Cache identisch war (~19035 Tokens, siehe Caching-Analyse), liegt die Ursache im Prompt *davor* oder in einem RAG-Modul, das in C-nox anders angezogen wurde.

### 3. LP/HP-Inkonsistenz ist global
Imre-Charakterbogen verwendet `HP`, A-nox-Save-JSON verwendet `hp`. Das zeigt: Die „LP, nicht HP"-Invariante ist nicht durchgesetzt, zumindest im Charakter-Layout-Template, das die SL rendert. Für die kommenden MP-Diät-Modelle (DeepSeek, Qwen, GLM) besteht Risiko, dass diese die Inkonsistenz verstärken.

### 4. Persona-Stimmen sind messbar unterschiedlich — das System trägt Gruppe
B-group zeigt: Drei Persona-Agents + ein SL in 5 Turns erzeugen glaubwürdige Gruppendynamik. Die Merge-Internals (B-group-merge.internal.md) mit R1/R2-Absprachen sind produktiv und bilden echte Tischgespräche nach. Das Roundtable-Pattern funktioniert — aber ist teuer (5 SL + 30 Persona-Internal + 5 Persona-Final = 40 Records für $1,36 in 5 Turns = $0,27/Turn vs. $0,09/Turn Solo).

### 5. Save-Schema v7 wird überwiegend korrekt unterdrückt, aber A-nox bricht aus
4 von 5 Phasen geben regelkonform kein Mid-Mission-Save aus. A-nox bricht aus — aber interessanterweise *gelenkt*: Der Persona-Prompt für C_chaot verlangt explizit „Save alle 3-4 Turns". A-nox-SL hat die Regel wenigstens im Kodex kommentiert („kein HQ-Save, kein Debrief-Reset"), anstatt stumm zu brechen. Das ist **schlechte Regel-Adhärenz, aber gute Transparenz**. C-nox-SL hingegen hat die Regel korrekt (im Turn-1-HQ-Menü steht `!save`-Option explizit als Option 3) — sie wurde nur nicht gezogen.

---

## 6. Caching-Analyse

### Cache-Region-Stabilität

| Phase | `cache_read` SL (unique) | `cache_creation` SL | Drift? |
|-------|--------------------------|---------------------|--------|
| A-kira | `{19035}` | 0 | **Nein** — TTL hielt über 15 Turns |
| A-imre | `{0, 19035}` | 19035 × 1 (Turn 2) | **Einmaliger Refresh** — Turn 2 Cache-Miss, dann wieder stabil |
| A-nox | `{19035}` | 0 | **Nein** — TTL hielt über 10 Turns |
| B-group | `{0, 19035}` | 19035 × 1 (Turn 1, Session-Start) | **Erwartet** — neue Session |
| C-nox | `{0, 19035}` | 19035 × 1 (Turn 1, Session-Start) | **Erwartet** — neue Session |

**Fazit**: Die Masterprompt-Cache-Region ist **extrem stabil** — 19.035 Tokens werden in jedem SL-Turn mit Cache-Region gefunden (außer beim Session-Start, was erwartet ist). Einzige Auffälligkeit: A-imre Turn 2 zeigte einen Mid-Session-Cache-Refresh (Cache-Creation statt -Read). Das kann durch TTL-Reset durch Anthropic passiert sein (z.B. Prompt-Cache läuft nach 5 Minuten ohne Hit ab und muss neu erzeugt werden) oder durch Kontextgrößen-Drift vor der Cache-Zeile. Kein strukturelles Cache-Problem.

### Cache-Hit-Ratios

- **Beste Ratio**: A-nox 0,653 / A-kira 0,638 (längere, stabile Sessions)
- **Schlechteste Ratio**: B-group 0,510 (kurze Session + Cache-Creation überwog)
- **Session-Start-Kosten**: Turn 1 jeder Session = 0,0 Ratio (Cache-Creation, volle Tokens)
- **Ab Turn 2**: Ratio skaliert invers mit History-Länge (mehr Kontext unten = mehr uncached-Tokens)

### Rechtfertigt das Cache-Verhalten den LiteLLM-Routing-Umbau?

**Ja, absolut.** Der Cache spart bei stabilen Sessions 50-65 % Token-Kosten auf der Input-Seite. Bei Sonnet 4.6 ($3/MTok input, $0,30/MTok cache-read) sind das faktisch 10× günstigere Input-Tokens für den Masterprompt-Anteil. Die Cache-Creation passiert genau 1× pro Session (außer Mid-Session-Refresh, der selten ist). Bei einer typischen ZEITRISS-Session (10-15 Turns) spart das ≈ $0,40-0,80 an Input-Kosten vs. No-Cache.

Empfehlung: **LiteLLM-Proxy-Route beibehalten**, aber:
- **Monitor** für Mid-Session-Cache-Creation (sollte selten bleiben — A-imre Turn 2 als Warnsignal verstehen)
- **Keep-Alive** überlegen: Wenn Cache-TTL der Flaschenhals ist, könnte ein 4-min-Heartbeat-Call mit kleinem Payload die Region warmhalten
- **Kosten-Dashboard** sollte `cache_hit_ratio` als Haupt-KPI tracken — bei Abfall unter 0,5 über 3 Turns hinweg Alarm

---

## 7. Fazit

### „Spiel läuft rund genug für MP-Diät-Modelle?"

**Empfehlung: Mit Einschränkungen — noch nicht.**

### Begründung

**Pro (für MP-Diät-Test jetzt):**
- Solo-Core-Sessions erreichen mit Sonnet 4.6 konsistent 19-23/25. Das ist das obere Band.
- Probenformel, Exploding-6, W6-Würfelmechanik werden in 4 von 5 Phasen korrekt reproduziert — diese Regeln sind robust genug, dass GLM-5-Turbo oder DeepSeek-V3.2 sie wahrscheinlich auch treffen.
- Das Persona-System (3 Spieler-Stimmen × 1 SL) ist stabil und belastbar — Gruppendynamik funktioniert.
- Cache-Verhalten rechtfertigt den LiteLLM-Umbau bereits jetzt — unabhängig vom SL-Modell.

**Contra (gegen Einsatz von MP-Diät-Modellen ohne Nachbesserung):**
- **W10-Schwelle in C-nox falsch reproduziert** — wenn Sonnet 4.6 das schon verhaut, werden Budget-Modelle es noch öfter verhauen. Die Regel muss entweder prominenter in den Masterprompt (früh, nahe am Anfang der Cache-Region) oder in ein RAG-Modul gehen, das bei TEMP-Proben zuverlässig gezogen wird.
- **LP/HP-Drift** ist ein Template-Bug, kein Modell-Bug. Muss im Charakterbogen-Template und im v7-JSON-Schema behoben werden, bevor MP-Modelle getestet werden — sonst vererben sie den Fehler 1:1.
- **Mini-Boss-Prompts werden ignoriert/fehlinterpretiert** (C-nox). Das war mit Sonnet 4.6! Bei schwächeren Modellen wird Session-Start-Routing („Mission 5 Mini-Boss" statt Chargen) noch unzuverlässiger. Braucht einen harten Eingangs-Marker oder eine Prompt-Preamble, die den Modus erzwingt.
- **Save-Schema v7 wird in 1 von 5 Phasen aufgeweicht** (A-nox Mid-Scene-Save). Bei MP-Diät-Modellen erwarten wir mehr solche Lax-Interpretationen.

### Konkrete Empfehlung

1. **Zuerst**: LP/HP-Template fixen. HUD-Invariante Stress-Max an Persona-Maxcap koppeln. W10-Schwelle im Masterprompt in der ersten Drittel positionieren oder in dedizierten `rules_core_dice.md` RAG-Modul, das immer mitgeladen wird.
2. **Dann**: Denselben Playtest mit **GLM-5-Turbo** (Budget) wiederholen. Erwartete Score-Range: 15-19/25. Wenn unter 15, ist GLM-5-Turbo nicht spielreif für ZEITRISS.
3. **Parallel**: LiteLLM-Route produktiv schalten, Cache-KPIs dashboarden (cache_hit_ratio, cache_creation_per_session).
4. **Erst dann**: DeepSeek V3.2, Qwen 3.5 als zweite Diät-Welle.

**Das Spiel läuft rund bei Sonnet 4.6 — aber der Prompt hat dünne Stellen, die erst gepatcht werden müssen, bevor man sich mit schwächeren Modellen in diese Stellen reinwagt.**

---

*Auswertung von Opus 4.7 Critic-Sub-Agent · Wall-Clock ~25 min · 43 SL-Turns + 71 Persona-Records analysiert*
