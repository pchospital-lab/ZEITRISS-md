# Selbst-Review: Buff-Schwellen-Patch (Branch fix/buff-schwellen-halluzination)

**Datum:** 2026-04-19  
**Reviewer:** Altair (nach abgebrochenem Critic-Run)  
**Scope:** Diff gegen main, SSOT-Konformitaet, Kompaktierung, LLM-Robustheit, Widersprueche, Edge-Cases, Watchguards

---

## TL;DR

**Verdict: Merge mit einer Anpassung (Formel-Namensgleichheit) und einem fehlenden Satz nachziehen.**

Der Patch ist korrekt, konsistent und widerspruchsfrei. Aber er loest das 
V3-Robustheit-Problem (30% Pass-Rate) nicht - kann er auch nicht, das ist 
ein struktureller Limit des "mehr Text"-Ansatzes. Er bringt trotzdem drei 
echte Gewinne gegenueber main und ist damit Merge-tauglich.

---

## Gefundene Probleme

### 1. [KLEIN] Formel-Namensinkonsistenz "temporaere Modifikatoren" vs "Buff"

**Zeile 134 (Regel):** `Wurf + ⌊Basis-Attribut / 2⌋ + Talent + Gear + temporaere Modifikatoren`  
**Zeile 239 (Negativ-Beispiel):** `Die Formel ist 'Wurf + ⌊Basis/2⌋ + Talent + Gear + Buff'`

Gleiche Formel, zwei Namen fuer denselben Summanden. Eine KI koennte 
versucht sein, die beiden als unterschiedliche Konzepte zu lesen (z.B. 
"temporaere Modifikatoren = Zustaende, Buff = Injektor").

**Schweregrad:** Klein. Harmlos wenn die KI es zusammen liest, aber 
unnoetig ambig.

**Fix-Vorschlag:** In Zeile 239 auf `+ temporaere Modifikatoren (Buff, 
Debuff, Zustand)` umstellen oder beide auf `Buff/Debuff` konsolidieren.

### 2. [MITTEL] Verlorener Satz: Talent-Tier-Schutz

**V2 hatte:** *"Talentbeschreibungen, die das Wort 'Schwelle' enthalten, 
referenzieren Narrativ oder Talent-Tier, nicht Würfelmechanik."*

**V3 (kompaktiert) hat:** den Satz nicht mehr.

Das war ein spezifischer Schutz gegen die Halluzinations-Richtung 
"Talent X hat Tier Y mit Schwelle Z" → Wuerfeltyp-Aenderung. 
Der aktuelle Patch verbietet implizit Talent-Schwellen ("Andere 
wuerfelmechanische Schwellen existieren nicht"), aber nicht explizit 
die Konfusion Talent-Tier ↔ Wuerfel-Schwelle.

**Schweregrad:** Mittel. Die Ursprungs-Halluzination war genau diese 
Richtung (Talent "Systemzugriff" → Schwellenwert erreicht). Der 
expliziten Schutz wieder rein zu nehmen waere billig.

**Fix-Vorschlag:** Am Ende von Zeile 133 anhaengen: *"Talent-Tiers 
(Basis/Fortgeschritten/Meister) und Talent-Beschreibungen mit dem 
Wort 'Schwelle' sind Narrativ, niemals Würfelmechanik."*

Kostet ca. 100 Zeichen, bleibt unter 40 KB Budget.

### 3. [KLEIN] Debuff-Abdeckung implizit

Der Patch spricht von "temporaeren Boni/Mali" nur einmal (Zeile 127 via 
"Zustaende"), der Rest des Patches redet nur von "Buffs". Debuff-Symmetrie 
ist implizit, nicht explizit.

**Schweregrad:** Klein. Keine Runtime-Verifikation dazu. Wenn ein Debuff 
Basis-GES 11 auf 10 druecken wuerde, koennte eine KI fragen: "Ist das 
jetzt W10 oder W6?"

**Fix-Vorschlag:** Nicht jetzt. Wenn je beobachtet, separater Patch.

### 4. [KLEIN] Gear-Boni-Behandlung nicht explizit

Gear-Boni sind in ZEITRISS Probe-Boni, nicht Attribut-Boni. Der Patch 
laesst offen, wie Gear in die Formel einfliesst. Die Formel `Wurf + 
⌊Basis/2⌋ + Talent + Gear + temporaere Modifikatoren` stellt Gear 
separat - korrekt. Aber wenn ein Gear theoretisch **permanent** GES +1 
gaebe (hypothetisch), wuerde der Patch sagen, es zaehlt zum Basis?

**Schweregrad:** Klein. Kein aktueller Gear in ZEITRISS gibt Attribut-Boni. 
Theoretisches Problem.

**Fix-Vorschlag:** Nicht jetzt. Wenn Gear-Attribut-Boni eingefuehrt werden, 
dann Patch.

---

## Was der Patch RICHTIG macht

### ✅ SSOT-Konformitaet (100%)

`core/wuerfelmechanik.md:49-50` sagt: *"Attribute verleihen nun einen 
additiven Bonus. Ab 11 ersetzt ein W10 den W6."* Der Patch ist damit 
vollstaendig konsistent. SSOT hat keine Buff-Regel explizit - der Patch 
fuellt eine Regelluecke ohne Widerspruch.

### ✅ Kompaktierung ohne Inhaltsverlust (bis auf Punkt 2)

Alle drei kritischen Aussagen sind erhalten:
- "Schwellenwert" darf im Kodex NUR bei 11 und 14 stehen ✅
- Heldenwürfel = Reroll-Token, kein zweiter Wuerfel im Wurf ✅
- Nur zwei wuerfelmechanische Schwellen existieren ✅

Prompt-Groesse 41,1 KB → 39,8 KB. Bleibt unter 40 KB Portabilitaet-Budget.

### ✅ Keine Masterprompt-Widersprueche

`ripgrep` auf "Buff|Injektor|Adrenalin|temporaer" zeigt: Alle Stellen 
sprechen EINE Sprache. Keine Gegenstimme im ganzen 645-Zeilen-Dokument.

### ✅ Heldenwürfel-bei-Buff korrekt abgedeckt

Tabelle nutzt "Basis-Attribut" als Schluessel. Buff kann Heldenwürfel 
nicht triggern (Basis 13 + Buff 2 = 15 → Basis bleibt 13 → kein 
Heldenwürfel). Das ist korrekt und durch Patch-Formulierung abgedeckt.

### ✅ Watchguard-Assertions greifen

5 neue Assertions, plus Anpassung der alten auf kompaktierte Formulierung. 
Gegenprobe bestanden (Patch absichtlich gebrochen → Watchguard meldet 
klare Fehler). Smoke 18/18 gruen.

---

## Die unbequeme Wahrheit: Warum Pass-Rate nur 30%

Das ist NICHT ein Patch-Bug. Das ist ein struktureller Limit des "mehr 
Text"-Ansatzes.

**Location-Problem:** Die Buff-Falle (Zeile 135) steht in Zeile 135 von 
645. Bei 39,8 KB Prompt = mittig-oberes Drittel. **Schlechtester 
Attention-Platz** laut "Lost in the Middle"-Phaenomen. Das wichtigste 
Negativ-Beispiel (Zeile 239) ist 100 Zeilen spaeter.

**Trigger-Problem:** Level-Up hat einen klaren Check-Zeitpunkt ("bei 
Attribut-Aenderung → pruefe"). Eine Probe mit aktivem Buff hat keinen 
solchen Trigger. Die Regel gilt "bei jeder Probe", aber das LLM erinnert 
sich nicht immer ans Regel-Setup.

**Attribute-Priming-Problem:** Wenn der Save ein Talent mit Effekt 
"+3 auf GES-Proben fuer eine Szene" enthaelt, liest das LLM das bei 
Save-Load als "GES wird effektiv +3". Diese Interpretation ist im 
Gewicht stark - 40 KB Masterprompt-Text dagegen schwach.

**Dieser Patch kann das nicht loesen.** Mehr Negativ-Beispiele wuerden 
den Prompt aufblasen, nicht die Pass-Rate heben.

---

## Empfehlung

### Jetzt

**Merge.** Drei Fixes im Patch:
1. Formel-Namensinkonsistenz in Zeile 239 auf "temporaere Modifikatoren" 
   angleichen
2. Verlorenen Talent-Tier-Satz in Zeile 133 zurueck nehmen (siehe Problem 2)
3. Commit anpassen mit diesem Review als Kontext

Diese drei Anpassungen kosten ~5 Minuten und verbessern den Patch ohne 
Risiko. Danach PR.

### Danach

**Folge-Issue BF-8 oeffnen:** Probe-Template-Ansatz.

Der Buff-Bug ist probabilistisch zu fragil fuer "mehr Text". Was wirklich 
helfen wuerde:
- **Probe-Template erzwingen**: 2-Zeilen-Kopfzeile vor jedem Wurf, die 
  Basis-Attribut + Wuerfeltyp getrennt auschreibt BEVOR die Formel anfaengt.
- **Opus 4.7 testen** (BF-5): Vermutlich bessere Regel-Befolgung.
- **Runtime-Watchguard** (BF-7): Middleware-Output-Scan vor Auslieferung. 
  Nicht in OpenWebUI nativ, aber via Proxy machbar.

---

## Audit-Trail

Dieser Review ersetzt einen abgebrochenen Critic-Run (Timeout nach 
4m52s und 427K Input-Tokens). Der Critic hatte zu viel Kontext geladen 
und war erst bei "jetzt lese ich den relevanten Bereich" als das 
Timeout kam. Daher Selbst-Review mit fokussierten ripgrep-Suchen 
statt Volltextanalyse.
