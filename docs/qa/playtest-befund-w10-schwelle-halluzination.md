# Playtest-Befund: W10-Schwelle fälschlich bei Attribut 6 ausgelöst

**Status:** Offen  
**Priorität:** Hoch — Würfelmechanik-Kernregel  
**Entdeckt:** 2026-04-19  
**Playtest:** `playtests/2026-04-19/episode1-mini-solo-sarah-v3/chat4-mission2.md`  
**Vorläufer-Evidence:** `internal/qa/evidence/playtest-2026-03-01/01-sonnet-46.md` (identisches Muster mit TEMP 8)  
**Modell:** `anthropic/claude-sonnet-4.6` (beide Playtests)  

---

## Zusammenfassung

Beim Level-Up von Wire (Lena Voss) von `INT 5 → 6` aktivierte die KI-SL
fälschlich den W10 mit halluzinierter Begründung *„Systemzugriff-Schwellenwert
erreicht"*. 9 Folge-Proben wurden mit W10 statt W6 geworfen — alle ERFOLG.

Das ist **kein reiner Halluzinationsfehler**. Die Masterprompt-Regel ist korrekt
formuliert, aber der **Level-Up-Prozess im SSOT enthält keinen Pflichtcheck
für Würfelschwellen-Änderungen**. Die KI interpoliert frei und interpoliert falsch.

Klassifikation: **LLM-Halluzination getriggert durch Doku-Lücke im
Level-Up-State-Transition.** Beides.

---

## SSOT-Regel

Die Schwelle ≥ 11 ist in vier Quellen identisch und eindeutig:

**`meta/masterprompt_v6.md` Zeile 127:**
```
W6 würfeln (Exploding: bei 6 nochmal würfeln und addieren). Ab Attribut ≥ 11:
W10 statt W6 (Exploding: bei 10 nochmal würfeln und addieren). Die ≥11-Schwelle
gilt einheitlich für alle Attribute - kein Sonderfall.
```

**`core/wuerfelmechanik.md` Zeilen 39–40:**
```
Proben nutzen standardmäßig W6, ab Attribut 11 automatisch W10 und ab
Attribut 14 zusätzlich den Heldenwürfel.
```

**`core/wuerfelmechanik.md` Zeile 80 (RULE-Anker):**
```
[[RULE]] Tooltip: "W10 ab 11, Heldenwürfel ab 14" [[/RULE]]
```

**`core/wuerfelmechanik.md` Zeilen 181–184 (Schwellen-Tabelle):**
```
|   Attribut | Würfelgröße   |
| ---------: | ------------- |
|       1-10 | W6            |
|        11+ | W10           |
```

**`core/zeitriss-core.md` Zeile 411:**
```
Ab Attribut 11: Der Würfel wechselt von W6 auf W10 (Exploding 10 mit Burst-Cap).
```

### Relevantes Talent (prüfend)

Talent **Systemzugriff** im Save-JSON:
```json
{ "name": "Systemzugriff", "tier": "Basis",
  "effect": "+2 auf INT-Proben bei Hacking und Technik-Analyse" }
```

**Das Talent hat keinen Schwellenwert.** Es gibt einen flachen +2-Bonus. Die von der SL
halluzinierte *„Systemzugriff-Schwellenwert erreicht"*-Meldung hat **keine
SSOT-Grundlage**. Auch keine andere Talent-Definition im Repo verweist auf eine
Würfeltyp-Änderung durch Talente.

### Level-Up-Prozedur im SSOT (Doku-Lücke!)

**`core/spieler-handbuch.md` Zeile 372:**
```
Pro Level-Up genau EINE Wahl: `+1 Attribut` ODER `Talent/Upgrade` ODER `+1 SYS`.
```

**`core/spieler-handbuch.md` Zeilen 638–641:**
```
1. Debrief / Score-Screen abschließen.
2. Level-Up jetzt abschließen (+1 Attribut oder Talent/Upgrade oder +1 SYS).
3. Danach HQ wählen.
4. Speichern.
```

**Was FEHLT:** Ein expliziter Pflichtcheck beim Level-Up, der klarstellt:
- Bei welchem Attributswert wechselt der Würfeltyp? (Nur bei 11, Heldenwürfel bei 14)
- Bei welchen Werten passiert **nichts**? (Bei 2–10, 12, 13, 15+ — alle ohne Würfeltyp-Änderung)
- Was soll NICHT gemeldet werden? (Keine „Schwellenwert"-Meldungen außerhalb 11 und 14)

Diese Lücke im State-Transition-Flow ist der Trigger für die Halluzination.

---

## Repro

**Datei:** `playtests/2026-04-19/episode1-mini-solo-sarah-v3/chat4-mission2.md`

**Vor Level-Up (Zeilen 478, 560, 699, 944 — korrekt W6):**
```
W6: [4] + INT 5/2 (2) + Talent Systemzugriff (nicht anwendbar) = 6 vs SG 6 → ERFOLG
W6: [5] + INT 5/2 (2) = 7 vs SG 5 → ERFOLG
W6: [5] + INT 5/2 (2) + Talent Systemzugriff +2 = 9 vs SG 7 → ERFOLG
W6: [3] + INT 5/2 (2) + Talent Systemzugriff +2 = 7 vs SG 6 → ERFOLG
```

**Level-Up-Moment (Zeile 1228 — Halluzination):**
```
Kodex: Attribut INT 5 → 6 bestätigt. Systemzugriff-Schwellenwert erreicht —
Würfeltyp W10 bei INT-Proben ab sofort aktiv.
```

**Nach Level-Up (Zeilen 1571, 1602, 2180, 2268, 2351, 2437, 2462, 2663, 2696 — falsch W10):**
```
W10: [7] + INT 6/2 (3) + Talent Systemzugriff +2 = 12 vs SG 9 → ERFOLG
W10: [9] + INT 6/2 (3) = 12 vs SG 10 → ERFOLG
W10: [6] + INT 6/2 (3) = 9 vs SG 8 → ERFOLG
W10: [8] + INT 6/2 (3) = 11 vs SG 9 → ERFOLG
W10: [7] + INT 6/2 (3) = 10 vs SG 8 → ERFOLG
W10: [5] + INT 6/2 (3) = 8 vs SG 7 → ERFOLG
W10: [9] + INT 6/2 (3) = 12 vs SG 9 → ERFOLG
W10: [8] + INT 6/2 (3) + Talent Systemzugriff +2 = 13 vs SG 9 → ERFOLG
W10: [6] + INT 6/2 (3) = 9 vs SG 8 → ERFOLG
```

**Quantifizierung (verifiziert durch `grep -c "W10:"` und `grep -c "W6:"`):**
- Chat 4 **vor** Level-Up: 0 W10-Proben, 16 W6-Proben (korrekt)
- Chat 4 **nach** Level-Up (Zeile 1228): 9 W10-Proben, 0 W6-Proben bei INT-Proben (falsch)
- Chat 5 **mit INT 6 aus Save geladen, kein Level-Up-Event**: 0 W10-Proben, 18 W6-Proben (korrekt)

**Sample-Größe:** Dieser Fall N=1, plus ein älterer dokumentierter Fall
(TEMP 8, `01-sonnet-46.md`). **Reproduktions-Versuch mit frischem Chat + absichtlich
forciertem Level-Up-Event steht aus** (Out of Scope für diesen Befund).

---

## Ursachenanalyse

### Halluzination + Doku-Lücke kombiniert

Die SL hat beim Level-Up eine sinnhaft klingende aber falsche Begründung
konstruiert (Talent-Name × Attributs-Schritt = nicht-existenter „Schwellenwert").
Das ist klassische LLM-Confabulation.

Aber: **Der Level-Up-Prozess im SSOT bietet der KI keinen deterministischen
Ablaufplan.** Er sagt nur *„Pro Level-Up genau EINE Wahl"* — und überlässt der
KI die Semantik des State-Transition komplett selbst. Das ist die Doku-Lücke,
die den Halluzinations-Trigger bereitet.

### Nicht persistent, aber nicht durch Save-Reload beweisbar

Chat 5 hat 18 W6-Proben mit INT 6 aus dem Save — korrekt. **Aber Chat 5 hatte
kein Level-Up-Event.** Der Bug ist eine **State-Transition-Halluzination**,
kein stationärer Zustandsfehler. Chat 5 beweist nicht, dass die Doku vollständig
ist — nur, dass die geladene Regel bei nicht-transitorischem Spiel greift.

### Bekanntes, systematisches Muster

`internal/qa/evidence/playtest-2026-03-01/01-sonnet-46.md` Zeile 37:
> *„NPC-Squad-Lauf (Midgame) verwendete ein simulierter Mitspieler TEMP 8 mit
> W10-Annahme — Fehler im Lauf erkannt und korrigiert."*

Zwei identische Fehler (TEMP 8 und INT 6), beide bei Sonnet 4.6, beide bei
Schwellen-Interpolation. Das ist **systematisch**, nicht stochastisch.

---

## Auswirkung

### Probabilistik

| Probe | W6 + INT 6/2 | W10 + INT 6/2 |
|-------|--------------|---------------|
| Würfelbereich | 1–6 + 3 = 4–9 | 1–10 + 3 = 4–13 |
| Burst-Cap triggert bei | 6 (16.7%) | 10 (10%) |
| Erfolgsrate gegen SG 9 (ohne Talent) | ≈ 16% (6 explodiert) | ≈ 40% |
| Erfolgsrate gegen SG 9 (mit Talent +2) | ≈ 33% | ≈ 70% |

Sarah spielte auf Lvl 2 mit Würfelmechanik, die erst bei ~Lvl 11 vorgesehen ist.
Alle 9 W10-Proben ERFOLG — plausibel kein Zufall.

### Retroaktive Datenintegrität (Policy-Frage)

Die 9 falschen Proben führten zu 9 Erfolgen. Einige hätten mit W6 gescheitert.
Narrativ hat Wire dadurch Informationen/Vorteile erhalten, die regelkonform
nicht hätten kommen dürfen. **Der Save ist betroffen.**

Zusätzlich: W10-Explosions-Events (bei Wurf 10) sind in W6-Regelwelt unmöglich.
Falls in Chat 4 solche Explosionen vorkamen, enthält das Narrativ Ereignisse,
die mit korrekter Würfelbasis nicht reproduzierbar sind.

Diese Frage ist **out of scope** für diesen Befund, aber im Folge-Issue zu klären.

---

## Fix-Optionen (priorisiert)

### P1 — C: Masterprompt-Verstärkung im Level-Up-Kontext

**Aufwand:** Niedrig. **Reichweite:** Hoch. **Greift den Root-Cause**
(Doku-Lücke im State-Transition).

In `meta/masterprompt_v6.md` nach Zeile 127 ergänzen:

```
Level-Up-Würfelschwelle: Beim Erhöhen eines Attributs prüfe den neuen Wert
gegen exakt zwei Schwellen:
- Neuer Wert = 11: W10 aktivieren, Kodex-Meldung "Würfel-Schwelle erreicht: W10"
- Neuer Wert = 14: Heldenwürfel aktivieren, Kodex-Meldung "Heldenwürfel-Schwelle erreicht"
- Jeder andere neue Wert (2-10, 12, 13, 15+): KEINE Würfeltyp-Änderung, KEINE
  "Schwellenwert"-Meldung. Talente haben KEINE Würfeltyp-Schwellen.
```

### P2 — E: Schwellen-Tabelle prominenter im Masterprompt

**Aufwand:** Niedrig. **Reichweite:** Hoch. **Ergänzt P1.**

Die existierende Tabelle aus `core/wuerfelmechanik.md:181-184`:
```
| Attribut | Würfelgröße |
| 1-10     | W6          |
| 11-13    | W10         |
| 14+      | W10 + Heldenwürfel |
```

sollte **als vollständige Tabelle** (nicht nur als Tooltip-Satz) im Masterprompt
stehen. Tabellen überleben Kontext-Drift robuster als Prosa.

### P3 — D: Negativ-Beispiel im Masterprompt

**Aufwand:** Sehr niedrig. **Reichweite:** LLMs lernen aus Beispielen stärker
als aus Regeln.

Im Masterprompt-Level-Up-Block:
```
Beispiel FALSCH: "Kodex: INT 5→6 bestätigt. Systemzugriff-Schwellenwert
erreicht — W10 aktiv." → Dies ist ein Regelverstoß. Attributswert 6 hat
keine Würfelschwelle.

Beispiel RICHTIG: "Kodex: INT 5→6 bestätigt. Würfeltyp bleibt W6 (W10 erst ab 11)."
```

### P4 — A: Toolkit Level-Up-Block um Pflichtcheck erweitern

**Aufwand:** Mittel. **Reichweite:** Nur wenn Toolkit aktiv im Kontext ist.

In `systems/toolkit-gpt-spielleiter.md` im Level-Up-Block einen expliziten
Pflichtcheck ergänzen:

```
LEVEL-UP-ABSCHLUSS — Pflichtcheck:
1. Attributswert ≥ 11? → W10 aktivieren, einmaliger Kodex-Hinweis
2. Attributswert ≥ 14? → Heldenwürfel aktivieren, einmaliger Kodex-Hinweis
3. Attributswert 10 → 11? → W10-Aktivierung ist Pflicht
4. Attributswert bleibt < 11? → Keine Würfeltyp-Änderung, keine Schwellen-Meldung
5. Attribut sinkt von 11+ auf 10 oder tiefer? → W10 deaktivieren, zurück auf W6
```

### P5 — B: Watchguard-Regression mit konkretem Szenario

**Aufwand:** Hoch. **Reichweite:** Statischer Doku-Anker, kein LLM-Runtime-Schutz.

Neue Watchguard-Assertions in `tools/test_onboarding_start_save_watchguard.js`:
- Prüft Präsenz der Schwellen-Tabelle in `meta/masterprompt_v6.md`
- Prüft Präsenz des Negativ-Beispiels
- Prüft Level-Up-Pflichtcheck-Anker im Toolkit

Ein runtime-LLM-Regressionstest (konkretes Szenario: „Chargen INT 5 + Level-Up
auf INT 6, prüfe ob W10 fälschlich genannt wird") wäre wertvoll, erfordert
aber separate Infrastruktur (siehe Out of Scope).

### P6 — F: Retroaktive Korrektur-Policy

**Aufwand:** Policy-Entscheidung (Flo).

**Option F1:** Gespielte Proben bleiben, narrativ beibehalten. „Canon" wird
vom Spieler so akzeptiert.

**Option F2:** Kodex-Meldung „Regelkorrektur" beim Entdecken eines Fehlers,
retroaktive W6-Auswürfe durch SL. Brechen den Flow.

**Option F3:** Ignorieren (Spielbalance-Einzelfall, kein Scope für Regel-Patch).

Empfehlung: F1 (Canon wahren). Aber diese Policy explizit dokumentieren.

### Empfehlung

**P1 + P2 + P3 zusammen** — alle drei wirken im selben Dokument (`masterprompt_v6.md`),
ergänzen sich, geringer Aufwand, maximale Robustheit.

**P4 zusätzlich**, wenn Toolkit-Pfad genutzt wird.

**P5** als Absicherung, aber nicht der Root-Cause-Fix.

Fast-Lane-Ausnahme: Nicht relevant — Fast-Lane startet Lvl 1 ohne Level-Up-Event.

---

## Blinde Flecken & Folge-Fragen (Out of Scope hier)

Diese wurden durch den Critic-Review identifiziert und gehören in separate Issues:

**BF-1 — Echte Schwelle 10→11:** Verhält sich die SL beim *echten* Schwellen-Event
korrekt (aktiviert sie W10, wenn sie soll)? Nicht getestet.

**BF-2 — Attribut-Senkung:** Was wenn Attribut von 11 auf 10 fällt (Verletzung,
Zustand, Fluch)? Fix-Formulierungen müssen den Rück-Übergang abdecken
(P4 tut das, P1/P2/P3 nicht explizit).

**BF-3 — Temporäre Boni:** Item/Zauber hebt INT temporär auf 11+. Gilt W10
nur für die Dauer des Effekts? SSOT ist ambivalent.

**BF-4 — Andere Schwellen-Systeme:** Der gleiche Bug-Mechanismus (Schwellen-
Halluzination im State-Transition) kann bei Heldenwürfel (14), Burst-Cap und
Talent-Rang-Schwellen greifen. Struktureller Fix wäre besser als W10-spezifisch.

**BF-5 — Modell-Varianz:** Fix gilt für Sonnet 4.6. Verhalten von Opus, GLM-5,
Qwen ungeprüft. Separater Playtest-Zyklus nötig.

**BF-6 — Context-Window-Erosion:** Bug trat in Chat 4 auf, nicht in Chat 5 (frisch).
Möglicherweise Kontext-Degradation bei langer Session. Fixes im Masterprompt
helfen nur, solange Masterprompt im Kontext vollständig bleibt.

**BF-7 — LLM-Runtime-Watchguard:** Statische Anker-Prüfung (Option P5) fängt
nicht, wenn die SL zur Laufzeit halluziniert. Ein Watchguard-Subprozess, der
live SL-Outputs gegen die Regel prüft, wäre technisch möglich (siehe
`systems/toolkit-gpt-spielleiter.md`-Kodex-Check-Pattern), aber separater Scope.

---

## Betroffene Dateien (Fix-Branch)

- `meta/masterprompt_v6.md` — P1, P2, P3 (Hauptfix)
- `systems/toolkit-gpt-spielleiter.md` — P4 (ergänzend)
- `tools/test_onboarding_start_save_watchguard.js` — P5 (Absicherung)
- Keine Änderungen an `core/wuerfelmechanik.md` nötig (Regel dort bereits korrekt)
