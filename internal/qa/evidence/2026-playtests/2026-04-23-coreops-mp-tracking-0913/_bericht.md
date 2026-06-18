# CoreOps-Playtest: coreops-mp-tracking-0913

**Datum:** 2026-04-23 09:13
**Szenario:** CoreOps Tier-1, KI-generierte Mission (keine Vorgabe). MP-Nutzung pro Turn getrackt.
**Modell SL:** zeitriss-v426-uncut via KB `bb266c62...`
**Modell Spieler:** anthropic/claude-sonnet-4.6
**Ziel:** MP-Usage-Tracking für Straffungs-Entscheidung

---

## Turn 0 — Gruppenstart

**GRUPPE:** Spiel starten (gruppe klassisch). Wir sind 3 Spieler:
Sarah hat schon eine Mission gespielt und bringt Mara Voss
mit (Callsign SPLINTER, GES 5, INT 5, Talent Tatortanalyse).
Jonas und Kim haben letztens mitgespielt, bringen ihre
Charaktere wieder — du darfst sie neu aushandeln wenn nötig.

Briefing bitte. Core-Mission, Tier 1, Tempocom-Auftrag.

### Turn 1 — SL

# ZEITRISS — Einleitung

> *Das Institut für Temporale Integrität operiert aus der Nullzeit — einem konstanten Heimatraum außerhalb der messbaren Chronologie. Eure Aufgabe: die Zeitlinie wahren. Nicht verändern. Wahren. Manchmal bedeutet das, Katastrophen zu verhindern. Manchmal bedeutet das, sie geschehen zu lassen.*
>
> *Ihr seid Chrononauten. Werkzeuge mit Gewissen. Agenten mit Ablaufdatum.*
>
> *Willkommen beim ITI.*

---

## Gruppen-Chargen

Bevor wir ins Briefing gehen: Ich brauche kurz die Grundlagen für Jonas und Kim — dann baue ich alle drei sauber auf.

**Mara Voss (SPLINTER)** ist bereits bekannt. Ich vervollständige sie auf Basis der Angaben zu einem vollständigen Tier-1-Charakter.

Für Jonas und Kim:

---

### Jonas — was bringt er mit?

Bitte kurz: **Rolle / Vibe** (z. B. "Ex-Militär, Nahkämpfer", "Technikerin, lieber unsichtbar", "Journalist, redet sich überall rein") — dann generiere ich daraus einen ZEITRISS-konformen Startcharakter mit 18 Punkten, Werten 2–6, Tier-1-Ausrüstung.

Oder: Jonas sagt einfach **`generate`** — dann bekommt er einen zufälligen Vollcharakter.

---

### Kim — was bringt sie mit?

Gleiche Frage: **Rolle / Vibe** oder **`generate`**.

---

*Alternativ: Wenn ihr alle drei einfach mit `generate` starten wollt, sage ich Bescheid und baue die Crew direkt durch — dann geht es schneller ins Briefing.*

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Mein Char ist ja der Nahkämpfer von letzter Runde — Ex-Militär, eher der stille Typ, löst Probleme lieber mit den Fäusten als mit Worten. Die Stats passen so wie sie sind (STR 5, GES 4 usw.), wenn du die einfach übernehmen kannst, Sarah?

**Kim** [Kim]: generate, ich will einfach loslegen lol

**Mara Voss** [Sarah]: Ich warte kurz, ob Jonas und Kim noch was eingeben — aber wenn die beiden einfach `generate` nehmen wollen, bin ich dabei. Voss braucht keine Vorstellung mehr.

### Turn 2 — SL

Perfekt. Ich baue alle drei durch.

**Jonas:** Ich übernehme den Nahkämpfer-Vibe und die genannten Werte (STR 5, GES 4) und fülle den Rest plausibel auf 18 Punkte auf. **Kim:** Vollgeneriert. **Mara:** Vervollständigt auf Basis der bekannten Werte.

---

# CREW-CHARGENBÖGEN

---

## MARA VOSS · Callsign: SPLINTER

*Forensikerin. Liest Räume wie andere Menschen Gesichter lesen. Wurde vom ITI rekrutiert, weil sie einen Tatort in der Vergangenheit rekonstruiert hatte — buchstäblich.*

| Attribut | Wert | Würfel | Mod |
|----------|------|--------|-----|
| STR | 2 | W6 | +1 |
| **GES** | **5** | **W6** | **+2** |
| **INT** | **5** | **W6** | **+2** |
| CHA | 3 | W6 | +1 |
| TEMP | 2 | W6 | +1 |
| SYS | 1 | — | — |

**Summe: 18 ✓**

**LP:** 10 · **Stress:** 0/8 · **SYS-Slots:** 1

**Talente:**
- `Tatortanalyse` (Basis) — +2 auf INT-Proben bei Spurensicherung, Szenenrekonstruktion, Beweiswertung. Triviale Analysen gelingen automatisch.

**Ausrüstung (Tier 1):**
- Kompaktpistole Mk.II *(Tier 1, 2–3 LP, verdeckt tragbar)*
- Leichte Einsatzjacke *(Tier 1, DR 1)*
- Forensik-Scanner *(Handgerät, INT +1 bei Tatortproben)*
- Comlink Standard
- Handscanner / Dietrich-Set

**Wallet:** 120 CU · **ITI-Ruf:** 1 *(eine Mission abgeschlossen)*
**Fraktion:** Ordo Mnemonika

---

## JONAS BRANDT · Callsign: ANVIL

*Ex-Militär. Irgendwo zwischen zwei Kriegen hat er aufgehört zu reden und angefangen zu handeln. Das ITI schätzt Männer, die keine Fragen stellen — solange die Fäuste die richtigen Antworten liefern.*

| Attribut | Wert | Würfel | Mod |
|----------|------|--------|-----|
| **STR** | **5** | **W6** | **+2** |
| **GES** | **4** | **W6** | **+2** |
| INT | 3 | W6 | +1 |
| CHA | 2 | W6 | +1 |
| TEMP | 2 | W6 | +1 |
| SYS | 2 | — | — |

**Summe: 18 ✓**

**LP:** 12 *(STR-Bonus: ⌊5/2⌋ = +2)* · **Stress:** 0/8 · **SYS-Slots:** 2

**Talente:**
- `Nahkampf: Militärisch` (Basis) — +2 auf STR-Proben im Nahkampf. Unbewaffnete Angriffe gelten als Tier-1-Waffe.

**Ausrüstung (Tier 1):**
- Kam

## Zusammenfassung

**Ende-Grund:** Stop-Hint: Mission abgeschlossen
**Turns:** 2
**Tokens gesamt:** 36476
**Peak Prompt:** 17375 tokens
**Ø Latenz pro Turn:** 30.4s

### MP-Sektion-Nutzung

- **sys-mechanik**: 7 hits ✅
- **lp-verletzung**: 7 hits ✅
- **nullzeit-hub**: 4 hits ✅
- **probe-formel**: 0 hits 💤 (nie getriggert!)
- **w10-schwelle**: 0 hits 💤 (nie getriggert!)
- **heldenwuerfel**: 0 hits 💤 (nie getriggert!)
- **psi-pp**: 0 hits 💤 (nie getriggert!)
- **hud-format**: 0 hits 💤 (nie getriggert!)
- **save-template**: 0 hits 💤 (nie getriggert!)
- **px-progression**: 0 hits 💤 (nie getriggert!)
- **kampfrunde**: 0 hits 💤 (nie getriggert!)
- **fraktionen**: 0 hits 💤 (nie getriggert!)
- **kb-retrieval**: 0 hits 💤 (nie getriggert!)

**CSV-Files:**
- Tokens: `_tokens.csv`
- MP-Sections pro Turn: `_mp-sections.csv`

### Findings (0)
- keine

