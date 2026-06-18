# Sweep 2 — Spielgefühl-Vollständigkeit

> Reiner Lese-Audit. Datum 2026-06-02. Branch: fix/research-v7-schema-consistency (main-Stand).
> Kontext: Patches #3192–#3195 erledigt (Core-Ops Strang-Wahl/harter Kern-Auftrag/Dichte 25–30min/Action-Kern,
> Rift-Ops Horror-Tonalität/Para-Schwereklassen/Action-Frontloading, Zukunfts-IA/RW-Spots,
> Research-Fortschritt scope episode/campaign, Px-Resonanz-Beat, Arena-Sofort-Action). **NICHT erneut vorschlagen.**
> Frage: Haben wir ALLES erwischt? Übersehene Spielgefühl-Lücken in den Modi finden, die KEIN Patch abgedeckt hat.

## Pro Modus (Status + Lücke/Datei:Zeile)

### Core-Ops — **rund** (frisch gepatcht)
Tech-Noir-Spionage, dichter Kern-Auftrag, Cinematic Arc mit Kampfszenen-Pflichtgate
(`kampagnenstruktur.md:1034`, `:1052`). Continuity-Rückverweis ab MS2 Pflicht
(`:842`), Debrief-Spiegel hakt Ziele ✓/✗ ab und legt Verfehltes als `arc.hooks[]`
ab (`:852`). Schauplatz aus Epoche (Kalter Krieg, viktorianisch, Ägypten, Industrialisierung)
+ wiederverwendbare IA/RW-Spot-Sets pro Epoche (`:881`). **Keine echte Lücke.**

### Rift-Ops — **rund** (frisch gepatcht)
Mystery-Casefile/Monster-Hunt, Para-Schwereklassen-Tabelle (`:447`), Boss in SC 10,
Artefaktwurf nur am Rift-Boss (`:494`), Fix-Objectives + Forensik-Dreieck im Debrief (`:858`).
**Keine echte Lücke.**

### Chronopolis Ring-Raid — **rund, gut spezifiziert**
Beute/Risiko/Eskalation sind sauber definiert: Big-Win→Exit-Druck-Kipp (`:2434`),
Apex-Bedrohung optional auf Rückweg/Exit (`:2440`), Reaktionslogik ohne Counter mit
Beat-Prioritäten `encounter_pool→nsc_generator→twist_pool` (`:2415`), Quadranten-Gefühl
(Dockyard/Bazaar/Archive/Sanctuary, `:2470`), Items nur bei lebendem Exit (`:2364`),
Sonder-Debrief 6-Schritt (`:2330`). Beute-Spezifik liegt bewusst in
`docs/dev/chronopolis-map-blueprint.md` (Maintainer). **Keine Lücke** — eher ein
Vorzeige-Modus.

### Arena — **rund** (frisch gepatcht: Sofort-Action)
Szenario-Pick vor Match, direkt entscheidende Showdown-Szene (`:2520`). MR-Trainingsanlage
gut beschrieben. **Keine Lücke.**

### HQ-Loop — **lebendig, NICHT dürres Menü**
Zwei Ebenen sauber getrennt: (a) **HQ-Runde** als vollwertiger Spielabschnitt mit eigenem
Chat — Equip, Klinik/OP, Werkstatt-Upgrades, Bar/Archiv, RP, Gerüchte, Fraktionsbeats
(`spieler-handbuch.md:213`, `:260` „Du entscheidest, was du tust… niemand drängt dich"),
(b) **Ressource-Turn** als Mini-Loop (Stash/Stress/Forschung, `kampagnenstruktur.md:1980`).
Dazu reiche **Erzählpausen**-Prosa (Alltag, Hobbys, Training-Minispiele, soziale Events,
intime Charakterepisoden, HQ-Anomalien — `:1995ff`). **Narrativ ist das stark.**
→ Einzige Beobachtung: die mechanische Belohnungsschleife der HQ-Aktivitäten ist dünner
als die Prosa (siehe Lücke #2).

### Level-Up / Progression — **funktional, aber spürbar mager** ⚠️
`spieler-handbuch.md:580`: „Pro Level-Up genau EINE Wahl: `+1 Attribut` ODER
`Talent/Upgrade` ODER `+1 SYS`." Level 1–10 = jede Mission ein Level-Up (`:573`).
Das ist die einzige nennenswerte echte Lücke — siehe unten.

## Übersehene Lücken priorisiert (mit Patch-Vorschlag)

### 1) Level-Up fühlt sich nicht wie ein Belohnungs-Beat an ⚠️ (lohnendste Lücke)
**Datei:** `core/spieler-handbuch.md:580`, Debrief-Sequenz `kampagnenstruktur.md:850`,
Psi-Progression `systems/kp-kraefte-psi.md:1054ff`.
**Befund:** Level 1–10 liefert pro Mission genau **eine** kleine Wahl (+1 Attribut /
Talent / +1 SYS). Anders als Core-Ops (Kern-Auftrag-Patch), Rift (Para-Klassen) oder
Px (Resonanz-Beat) gibt es für den Aufstieg **keinen inszenierten Spielgefühl-Beat** —
er läuft als Zeile im Auto-Debrief-Score-Screen durch. Für Psi-Begabte sind 3-stufige
Kräfte (Basis/Fortgeschritten/Experte) definiert (`kp-kraefte-psi.md:1069`), aber für
Nicht-Psi-Charaktere gibt es **keine spürbaren Freischalt-Meilensteine** ("ab Lvl X
neue Mechanik/Slot"). Das ist genau das Px-Muster: mechanisch da, erlebnisarm.
**Patch-Vorschlag:** (a) Im Debrief einen kurzen **Level-Up-Inszenierungs-Beat** als
Pflicht-Mikro-Moment (1–2 Sätze diegetisch: was die neue Fähigkeit konkret kann, HUD
`Lvl ↑`-Ping). (b) **Tier-Meilensteine für ALLE** (nicht nur Psi): an markanten Levels
(z. B. 5/10/15…) ein fühlbarer Sprung statt nur +1 — analog zu den Para-Schwereklassen-
Tiers. (c) Klarstellen, dass Level-Up-Wahl ein **eigener kleiner HQ-Beat** sein darf
(Werkstatt/Training-Szene), nicht nur eine Score-Screen-Zeile.

### 2) HQ-Aktivitäten ohne mechanischen Pay-off (mittel)
**Datei:** `kampagnenstruktur.md:1995ff` (Erzählpausen) vs. Ressource-Turn `:1980`.
**Befund:** Die Erzählpausen-Prosa (Training, soziale Events, intime Episoden) ist reich,
aber bis auf „Stress −1" im Ressource-Turn hängt **kein greifbarer Mechanik-Effekt** dran.
Beziehungswerte existieren als Konzept (`:1619`), sind aber nicht an die HQ-Aktivitäten
gekoppelt. Risiko: Spieler überspringen Erzählpausen, weil sie sich „nur Flavor" anfühlen.
**Patch-Vorschlag:** Leichte, optionale Kopplung — z. B. Training-Minispiel gewinnen →
1× Reroll-Token für nächste Mission; soziales Event → +1 Beziehungsstufe zu einem NSC;
intime Episode → temporärer Stress-Cap-Bonus. Klein halten (kein Grind), aber „lohnt sich"-
Signal setzen. **Nicht zwingend ein eigener Patch** — kann Teil von #1 sein.

### 3) Verschwörungs-Drip nur an den Rändern, nicht in der Missionsmitte (klein)
**Datei:** `kampagnenstruktur.md:1041` (SOLL „Verschwörungs-Reveals laufen während der
Infiltration mit"), Continuity-Verweis `:842`, Weltstatus-Zeile `sl-referenz.md:1090`.
**Befund:** Der rote Faden ist an **Briefing** (Continuity-Rückverweis ab MS2), **Debrief**
(verfehlte Ziele → `arc.hooks[]`) und **einmal pro Zyklus** (Weltstatus-Zeile) verankert —
also gut an den Mission-Rändern. Für die **mittleren Szenen 3–9** gibt es nur den tonalen
SOLL-Satz, **kein Pflichtgate** wie beim Kampfszenen-Beat (`:1052`). Risiko: Verschwörung
wird im Briefing erwähnt und taucht erst im Debrief wieder auf — die Mitte fühlt sich
verschwörungsfrei an. Echte, aber kleine Lücke (der SOLL-Satz fängt das tonal teils ab).
**Patch-Vorschlag:** Optionaler **Mid-Mission-Thread-Beat**: in einer der mittleren Szenen
genau ein konkretes Verschwörungs-Detail (Dokument, NSC-Andeutung, beobachtetes Symbol),
das auf `arc.questions[]` einzahlt — als KANN-Empfehlung, nicht als hartes Gate (sonst
Padding-Risiko, das der Dichte-Patch gerade abgeschafft hat).

## Was schon rund ist
- **Chronopolis Ring-Raid:** vorbildlich (Big-Win/Exit-Druck, Apex-Platzierung, Beat-Pool).
- **Core-/Rift-Loop:** dicht, Kern-Auftrag-fokussiert, Continuity sauber verdrahtet.
- **HQ als Schauplatz (narrativ):** lebendig, klar als eigener Spielabschnitt etabliert.
- **Schauplatz-Vielfalt:** Epoche liefert Setting + IA/RW-Spot-Sets + Quadranten in Chronopolis
  + Field-Downtime-Pool (`:1791`). Über IA/RW-Spots hinaus ausreichend variabel — **keine Lücke**.
- **Verschwörung an den Rändern:** Briefing/Debrief/Weltstatus mechanisch verankert.

## Gesamturteil
**Das Wesentliche ist erwischt.** Die fünf Modi (Core, Rift, Chronopolis, Arena, HQ) sind nach
den Patches #3192–#3195 spielgefühl-solide; kein zweiter „Px-Fall" (mechanisch-da-aber-tot)
unter den Hauptmodi. **Die einzige klare, lohnende übersehene Lücke ist das Level-Up/
Progression-Spielgefühl** — derselbe Befund-Typ wie damals bei Px, nur eine Ebene tiefer:
der Aufstieg ist mechanisch korrekt, aber als Erlebnis ein Score-Screen-Eintrag statt eines
Beats, und Nicht-Psi-Charaktere haben keine fühlbaren Freischalt-Meilensteine.

**Die 2–3 lohnendsten übersehenen Lücken:**
1. **Level-Up als Belohnungs-Beat** (#1) — Inszenierungs-Mikro-Moment im Debrief + Tier-
   Meilensteine für alle Klassen, nicht nur Psi. **Klar patch-würdig.**
2. **HQ-Aktivitäten mit leichtem Mechanik-Pay-off** (#2) — kann an #1 angehängt werden.
3. **Mid-Mission-Verschwörungs-Beat** (#3) — kleinste Lücke, als KANN-Empfehlung, kein Gate.
