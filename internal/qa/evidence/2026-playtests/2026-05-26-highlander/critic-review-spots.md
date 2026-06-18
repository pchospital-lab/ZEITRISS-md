# Critic-Review: feat/mystische-ia-rw-spots

**Modell:** openrouter/anthropic/claude-opus-4.7 (subagent, depth 1)
**Gelaufen:** 2026-05-27T16:52Z
**Base-Hash:** 372c15b1 (main = feat/mission-pacing-anchor merged)
**Patch-Status:** uncommitted im Arbeitsbaum auf Branch `feat/mystische-ia-rw-spots`
**Diff-Umfang:** 3 Files, +82/-2 Zeilen (masterprompt_v6.md, kampagnenstruktur.md, kreative-generatoren-missionen.md)

## Verdict

**GO mit Mini-Fix.**

Pflichtgate ist konsistent mit Mission-Integrität (≤30 min ⊂ ≤50 km, beide Regeln pushen Spatial-Proximity, kein Konflikt). Generator-Konflikt: keiner — der Begriff „Anchor" hat im Repo bereits drei distinkte Bedeutungen (IA, Briefing-Anchor, Fallanker), die in `kampagnenstruktur.md` §364 explizit getrennt sind; der neue Generator stört das nicht. Rift-Ops: Pflichtgate greift grundsätzlich auch dort (IA/RW existieren in Rift-Mode, siehe §377), aber der **Spot-Profil-Katalog deckt extraterrestrische/Far-Future-Settings nicht ab** (Luna 2266, Raumschiff-Rifts). Eine kurze Klarstellung im Generator löst das ohne neue Regel.

## Befunde

### 1. Konsistenz Pflichtgate — OK, kein Konflikt

`meta/masterprompt_v6.md` §C enthält jetzt zwei Pflichtgates dicht hintereinander:

- **Mission-Integrität-Pflichtgate** (Z.123, Regel 3): „keine narrativen Sprünge über `>50 km` Distanz" **innerhalb** einer Mission (Mid-Mission-Stadtwechsel = neue Mission).
- **IA/RW-Spot-Pflichtgate** (Z.129, Regel 2): „nächstmöglicher" Spot zum Operationsgebiet, „keine 2-Stunden-Anreise vom Land-IA zum Stadt-Ziel".

Beide Regeln zielen in dieselbe Richtung (Spatial-Proximity, keine erzählerische Reise-Streckung). Die 30-min-Schwelle aus dem neuen Pflichtgate ist **strenger** als das 50-km-Verbot — eine Mission kann gar nicht erst in einen `>50 km`-Sprung laufen, wenn der IA bereits ≤30 min am Ziel sitzt. Mutual reinforcement, kein Widerspruch. Mission-Integrität-Regel 3 bleibt notwendig für narrative Sprünge **nach** dem IA (Wien→Belgrad-Skip), die nicht durch die IA-Wahl abgedeckt sind.

**Empfehlung:** Keine Änderung nötig. Optional ein 1-Zeilen-Querverweis im IA/RW-Pflichtgate: *„Konsistent mit Mission-Integrität-Pflichtgate Regel 3 — IA ≤30 min macht den `>50 km`-Verbot mechanisch leichter durchsetzbar."*

### 2. Generator-Konflikt — Terminologie-Risiko, kein Inhalts-Konflikt

`gameplay/kreative-generatoren-missionen.md` enthält **drei** unterschiedliche „Anchor"-Begriffe, die durch den Patch nicht neu kollidieren, aber durch die Anchor-/IA-Pflege weiter belastet werden:

- **Z.145 „Core-Briefing-Baukasten (Anchor + Auftragstyp)"** → Anchor = Person/Ort/Objekt als **Kernkonflikt** der Mission (Informant, Relais-Knoten, Archivkiste).
- **Z.163 (neu) „IA/RW-Spot-Generator"** → Anchor = **Sprungort** (Insertion Anchor).
- **Z.2228+ Rift-Casefiles** → `Anchor-Uhr`, `Anchor-Knochen`, `Fahrgast-Anker`, Objective `Secure Anchor` → **Fallanker** (das gebundene Objekt der Anomalie).

`kampagnenstruktur.md` §Z.376–379 trennt die Begriffe für Rift-Ops explizit (`IA/RW-Anker` vs `Fallanker`). Im Core-Generator-Modul fehlt diese Trennung — der Briefing-Baukasten-Anchor (Z.145) und der neue IA-Spot-Generator (Z.163) verwenden beide das Wort „Anchor" ohne Crossref.

**Empfehlung (Mini-Fix, optional):** Im neuen Generator-Abschnitt einen 1-Satz-Disclaimer ergänzen, z. B. nach Z.171:

```diff
 Operationsgebiet — kein Abseits, keine 2-Stunden-Anreise zum Land-IA.
+
+> **Terminologie:** „IA-Anchor" (dieser Generator) ≠ Briefing-Baukasten-„Anchor"
+> (Z.145, Person/Ort/Objekt als Kernkonflikt) ≠ Rift-„Fallanker" (Z.2228,
+> gebundenes Objekt der Anomalie). Trennung wie in `kampagnenstruktur.md` §Rift-Op
+> Interface Contract.
```

Nicht blockierend, aber spart künftigen Sub-Agents einen Verwechslungs-Bug bei Mission-Generierung.

### 3. Rift-Ops-Skopus — Spot-Profile zu erd-/historisch-zentrisch

Rift-Ops haben IA/RW (`kampagnenstruktur.md` Z.377), das Pflichtgate greift dort grundsätzlich. Aber zwei der gecatalogten Rift-Seeds liegen **außerhalb** des Spot-Profil-Katalogs:

- **RIFT-LUNAR** (Luna Far-Side 2266) — kein „Steinkreis", keine „Kirche", keine „stillgelegte U-Bahn".
- **Raumschiff-Rift-Beispiel** (`kampagnenstruktur.md` Z.356, „Zukunfts-Rift führt in ein Raumschiff").

Das W4-Tabellen-Profil 3 (**Technisch-verborgen**) deckt „Wartungsschacht / Versorgungstunnel" ab — auf einer Mondbasis ist das natürlich anwendbar. Profile 1/2/4 (historisch/mystisch/liminal) sind dort nicht plausibel. Die Regel selbst ist OK (ein Wartungsschacht IST der nächstmögliche Zeit-taugliche Spot auf Luna), aber der **Beispiel-Pool** sollte das anerkennen, sonst riskiert ein literal-lesender Sub-Agent „kein passender Spot → Regel-Konflikt → IA aufs Mondfeld setzen".

**Empfehlung (Mini-Fix):** Im Generator unter „Anti-Patterns" oder als Fußnote ergänzen:

```diff
 - *„Ein Lagerschuppen außerhalb der Stadt.“* — zu weit weg und ohne Charakter.
+
+**Far-Future / extraterrestrische Rifts:** Bei Settings ohne historische
+Substanz (Mondbasis, Raumschiff, Tiefsee-Habitat) trägt Profil 3
+(technisch-verborgen) das Pflichtgate allein — Wartungsschacht, stillgelegte
+Druckschleuse, alter Reaktor-Kontrollraum sind dort die ZEITRISS-tauglichen
+Spots. Profile 1/2/4 sind dann nicht anwendbar, das ist OK.
```

Alternativ in `masterprompt_v6.md` IA/RW-Pflichtgate Regel 1 einen halben Satz: *„In Far-Future/extraterrestrischen Rifts trägt Profil 3 (technisch-verborgen) das Pflichtgate allein."* — eleganter, weil die Ausnahme direkt im Regel-Text steht.

## Empfehlung Gesamt

**GO mit zwei optionalen Mini-Fixes** (beide nicht-blockierend):

1. Terminologie-Disclaimer im Generator (Befund 2) — verhindert Anchor-Verwechslung.
2. Far-Future-Klausel für Rift-Ops auf nicht-historischen Settings (Befund 3) — schließt Edge-Case Luna/Raumschiff.

Beides zusammen ~6 Zeilen Diff. Wenn Flo squashen will: Beide Fixes in denselben Branch ziehen, kein neuer PR nötig.

Keine echten Konflikte mit Mission-Integrität-Pflichtgate (#3180), keine Generator-Kollision auf Inhaltsebene, kein Rift-Ops-Scope-Bruch — die Regel greift dort sinnvoll, der Beispiel-Pool ist nur lückenhaft für Sci-Fi-Settings.
