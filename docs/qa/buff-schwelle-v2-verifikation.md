# Runtime-Verifikation V3 (Statistisch): Buff-Schwellen-Patch

**Datum:** 2026-04-19  
**Modell:** `anthropic/claude-sonnet-4.6`  
**Masterprompt:** v4.2.6 nach PR #2955 + Buff-Patch (kompaktiert, 39,8 KB)  
**Harness:** `playtests/_harness/w10-schwelle-probe-v3.py`  
**Logs:** `playtests/2026-04-19/w10-schwelle-probe-v3/`  
**Methodik:** N=10 Runs pro Szenario (statistische Pass-Rate statt Einzellauf)

---

## Warum V3

V1 hatte 4/5 Pass, V2 nur 2/5 Pass - gleiche Szenarien, gleicher Patch-Zustand, 
unterschiedliche Ergebnisse. Das zeigt: **Sonnet 4.6 ist probabilistisch.** Ein 
einzelner Lauf taugt nicht als Signal. Daher V3 mit 10 Runs pro Szenario.

Fokus: A (Level-Up INT 5->6, Ursprungs-Bug) und D (Buff-Fall, neuer Bug).
B/C hatten in V1+V2 beide 100% Pass und brauchen keine statistische 
Absicherung.

---

## Ergebnis

| Szenario | Titel | Pass-Rate | Verdict |
|----------|-------|-----------|---------|
| A | Level-Up INT 5→6 (darf KEIN W10) | **10/10 (100%)** | **Perfekt** |
| D | Buff GES 9 + Injektor +3 (darf KEIN W10) | **3/10 (30%)** | **Nicht behoben** |

### A: Der Ursprungs-Bug ist robust behoben

PR #2955 (Level-Up-Pflichtcheck) wirkt zuverlässig. In 10 Runs null Rückfall
auf die ursprüngliche Halluzination. Die V2-Regression war statistisches
Rauschen, kein strukturelles Problem.

**Das ist der harte Win dieser Patch-Serie.** Ursprungs-Bug tot.

### D: Der Buff-Patch wirkt kaum

Die SL halluziniert bei aktivem Injektor-Buff in 7 von 10 Läufen:
- 5× "Halluzinierte GES-Schwelle" (`GES 9 → W10` direkt ausgesprochen)
- 2× "Falsche Formel" (`⌊12/2⌋` statt `⌊9/2⌋`)
- 1× W10-Wurf ohne vorangestellte falsche Begründung

**Verteilung der Verstöße (7 Fails):**

| Verstoß | Anzahl |
|---------|-------:|
| Halluzinierte GES-Schwelle (`GES 9 → W10`) | 5 |
| Falsche Formel (`⌊12/2⌋ = 6`) | 2 |
| W10-Wurf in Probe | 1 |

---

## Interpretation

**PR #2955 (Level-Up-Kontext) wirkt robust.** Der Masterprompt-Patch hat
den Level-Up-Zeitpunkt gut eingefangen - "bei Attribut-Änderung → 
Übergangsregeln" ist ein klar definierter Moment, die KI prüft und hält 
sich daran.

**Der Buff-Patch (diese Branch) wirkt nicht zuverlässig.** Die Buff-Situation
ist probabilistisch schwerer zu erwischen, weil:

1. **Kein klarer "Check-Zeitpunkt"**: Bei Level-Up löst "Attribut-Änderung" 
   den Check aus. Bei einer Probe mit aktivem Buff gibt es keinen ähnlich 
   sauberen Trigger - die Regel gilt "immer beim Würfeln", aber das LLM 
   erinnert sich nicht immer.

2. **Buff-Darstellung im Save**: Der Injektor wird als Talent mit Effekt 
   "+3 auf GES-Proben" geladen. Das LLM interpretiert das in der Hälfte 
   der Runs als "aktives Attribut +3", obwohl der Patch sagt "additiver 
   Modifikator ans Ergebnis".

3. **Regel-Ort**: Der Buff-Fallen-Block steht unter "Würfelmechanik". Bei 
   einer Probe mit Buff muss das LLM *rückwärts* aus dem Regelbuch lesen. 
   Im Level-Up-Moment greift der Pflichtcheck vorwärts aus dem Kontext.

---

## Was tun

**Branch trotzdem mergen?** Ja, mit Einschränkungen.

Begründung:
- Kompaktierung (41 KB → 39,8 KB) ist unbestritten gut
- Formel-Anker (`⌊Basis-Attribut/2⌋ + temporäre Modifikatoren`) ist korrekt
- Konkrete Buff-Beispiele erhöhen die Pass-Rate von vermutlich 0% auf 30%
  (V1 hatte 0/1 bei D, V2 hatte 0/1, V3 hat 3/10)
- Watchguard-Absicherung gegen Drift

**Aber:** Für Produktions-Spiel reicht 30% nicht. ZEITRISS braucht einen 
grundsätzlich anderen Ansatz für den Buff-Fall.

---

## Nächster Ansatz: BF-8 - Probe-Template

Hypothese: Die W10-Schwellen-Regel muss bei **jedem Würfelwurf** erzwungen 
werden, nicht nur als Hintergrund-Regel.

**Konzept:** Ein verpflichtender 2-Zeilen-Header vor jeder Probe:

```
Probe-Setup: [ATTR] Basis X, W[6|10], Buff/Debuff ±Y (separat), Talent ±Z
Probe: [NAME] → W[6|10]: [Wurf] + ⌊X/2⌋ + Talent + Gear + Buff ±Y = Gesamt vs SG
```

Der erste "Probe-Setup"-Satz zwingt die SL, den Basis-Attributwert UND den 
Würfeltyp getrennt auszusprechen - **bevor** die Formel überhaupt anfängt. 
Dadurch wird die Regel in Worten reproduziert, nicht nur im Kopf geprüft.

**Ob das funktioniert**: Unbekannt. Muss im nächsten Experiment getestet 
werden, mit 10-20 Runs Minimum.

**Out of Scope für diesen Branch** - eigenes Folge-Issue, eigene Patch-Runde.

---

## Out of Scope

- **BF-5**: Modell-Varianz. Opus 4.7 hat eventuell bessere Regel-Befolgung 
  als Sonnet 4.6 für den Buff-Fall. Vergleichstest noch offen.
- **BF-7**: Runtime-Watchguard (Middleware scannt Output vor Auslieferung). 
  Andere Baustelle, nicht in OpenWebUI nativ.
- **BF-8**: Probe-Template als Robustheits-Verstärker (siehe oben).

---

## Empfehlung zusammengefasst

**Branch mergen mit Erwartung: A ist gefixt, D nur teilweise.** 
Transparenz-Dokument (dieses File) wird mit gemerged, damit in 3 Monaten 
nachvollziehbar ist, warum der Buff-Bug nur halb tot ist.

**Folge-Issue öffnen** für BF-8 (Probe-Template). Das ist der echte 
Ansatz - mehr Text alleine reicht nicht mehr.
