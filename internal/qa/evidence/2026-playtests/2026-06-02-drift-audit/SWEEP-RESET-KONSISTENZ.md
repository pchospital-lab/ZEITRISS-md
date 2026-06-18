# Sweep — Reset & Konsistenz (negative Werte)

> Audit-Typ: reiner LESE-Audit. Fokus: Reset-/Persistenz-Logik der negativen/Verlust-Achse
> (Stress, Heat, Psi-Heat, Fraktionen, Tod). Jeder Befund mit Datei:Zeile + Zitat.
> Quellen: `meta/masterprompt_v6.md`, `core/sl-referenz.md`,
> `systems/gameflow/speicher-fortsetzung.md`, `characters/zustaende.md`.

---

## Stress-HQ-Reset (Flos Verdacht)

**Flos Verdacht: „Stress sollte sich ja im HQ nullen."** → Im Kern **bestätigt**, aber mit
einer Formulierungs-Spannung, **ob auf `0` oder auf „HQ-Basis/Grundwerte"** genullt wird.

Befunde (alle sagen: HQ/Debrief setzt Stress zurück — die Mechanik ist da):

- `characters/zustaende.md:311-312` — **klarste Aussage, Ziel = 0**:
  > „nutzt eine feste Skala von **0–10** (`stress_max = 10`, nicht variabel) … Im
  > **HQ oder der Medbay fällt der Zähler auf 0**; eine kurze Ruhephase senkt ihn um 1."
- `characters/zustaende.md:350` (Reset-Tabelle) — **Ziel = 0**:
  > „**Reset** | HQ-Phase → 0; im Feld: CHA-Probe oder 1 Runde Pause (−1)"
- `core/sl-referenz.md:280` — **„HQ-Basis"** (nicht wörtlich „0"):
  > „**Invariante:** Speichern nur im HQ; Debrief setzt `stress`/`psi_heat`/`SYS`
  >  vorher auf **HQ-Basis** zurück."
- `core/sl-referenz.md:114-115` — **„gespeicherte Grundwerte"** (nicht wörtlich „0"):
  > „Transfers zurück ins HQ setzen zusätzlich SYS-Auslastung, **Stress** und
  >  Psi-Heat auf die **gespeicherten Grundwerte** zurück."
- `core/sl-referenz.md:495-496` — HQ-Serializer normalisiert vor Export:
  > „HQ-Serializer transiente Werte vor dem Export auf **HQ-Basis**
  >  (`stress`, `psi_heat`, `sys_runtime/sys_used`, `cooldowns`, Timer-Reste)"
- `meta/masterprompt_v6.md:552` (Kodex-Beispiel) — **erzählerisch „reset"**:
  > „`` `Kodex: Stress reset. Sprung-Ready.` ``"
- `meta/masterprompt_v6.md:1207-1208` — Debrief-Reset vor HQ-`!save`:
  > „Vor dem HQ-`!save` läuft der **Debrief-Reset** (`stress`/`psi_heat`/`SYS` auf
  >  HQ-Basis). `stress` und optional `psi_heat` bleiben dennoch Teil des Schemas…"
- `systems/gameflow/speicher-fortsetzung.md:165` (SSOT-Helper):
  > „`normalize_hq_transients()  # stress/psi_heat/sys_runtime/sys_used/cooldowns/timer`"
- `systems/gameflow/speicher-fortsetzung.md:248-249` — HQ-Save normalisiert „auf HQ-Basis".

**Urteil: ÜBERWIEGEND SAUBER — eine LÜCKE in der Begriffsdefinition.**
Alle Stellen sind sich einig, *dass* Stress im HQ/Debrief zurückgesetzt wird, und es gibt
einen SSOT-Helper (`normalize_hq_transients`). **Aber:** zustaende sagt explizit „→ **0**",
während sl-referenz (3×) und masterprompt von **„HQ-Basis"/„gespeicherte Grundwerte"**
sprechen. **Nirgends ist definiert, dass „HQ-Basis" für Stress immer `0` ist.** Wenn ein Char
einen Nicht-Null-„Grundwert" haben könnte (Trauma-Malus, Dauerbelastung?), widersprechen sich
zustaende (`→0`) und sl-referenz (`→Grundwert`). → **Klarstellung nötig:** „HQ-Basis für
Stress = 0" einmal verbindlich festschreiben, sonst ist Flos „sollte sich nullen" nur
implizit gedeckt. Beat-Patch sollte sich auf **0** als kanonisches Reset-Ziel verlassen können
— aktuell muss er das aus zwei Quellen zusammenreimen.

---

## Transient vs. Persistent

SSOT für transient: `normalize_hq_transients()` (`speicher-fortsetzung.md:165`) +
`transients`-Liste (`speicher-fortsetzung.md:170-174`). SSOT für persistent: Save-Pfadbaum
(`speicher-fortsetzung.md:222-367`) + JSON-Template (masterprompt:990ff).

| Wert | Reset wann | persistiert im Save? | SSOT-Stelle | Urteil |
|------|-----------|---------------------|-------------|--------|
| `stress` | HQ/Debrief → 0 (bzw. „HQ-Basis") | **Ja**, Feld bleibt im Schema (auf Basis-Wert) | zustaende:311; sl-ref:280; speicher:165,172; mp:997 | SAUBER (bis auf 0-vs-Basis, s.o.) |
| `psi_heat` | nach jedem Konflikt → 0; HQ → 0 | **Ja**, Feld im Schema (nur bei `has_psi`) | zustaende:350; sl-ref:113-114; speicher:173,624 | SAUBER |
| `SYS_runtime`/`SYS_used` | HQ → HQ-Basis | Schema-Feld, Runtime-Wert nicht | speicher:170,249; sl-ref:333 | SAUBER |
| `cooldowns` | HQ → leer/normalisiert | **Nein** (Laufzeit) | speicher:174,367 | SAUBER |
| Exfil (`stress`,`ttl`,`anchor`…) | Mission-Ende → verworfen | **Nein** (Laufzeit) | sl-ref:485-488; speicher:367,406 | SAUBER |
| **`heat` (Noise/Heat)** | **— kein Reset definiert —** | **NEIN — gar kein Save-Feld** | nur HUD mp:695, Beats mp:239/323 | **LÜCKE (kritisch)** |
| `reputation.iti` | nie (steigt/persistiert) | **Ja** | mp:1017; speicher:348 | SAUBER (persistent gewollt) |
| `reputation.factions.*` | nie | **Ja** | mp:1019-1022; speicher:348 | SAUBER (persistent gewollt) |
| `arc.factions` | nie | **Ja** | speicher:357,729,936; sl-ref impl. | SAUBER (persistent gewollt) |
| `logs.fr_interventions[]` | nie (Historie) | **Ja** | speicher:188,947,1251 | SAUBER (persistent gewollt) |
| `lp`/`lp_max` | HQ-Heilung (Stufen) | **Ja** | mp:996; zustaende:60ff | SAUBER |
| `status` (deceased) | terminal | **Ja**, Final-Save | mp:944; speicher:117 | SAUBER (s. Tod-Abschnitt) |

**Heat ist der Ausreißer:** Es ist weder als transient noch als persistent geführt — es
existiert *nur* als HUD-Anzeige und Beat-Konsequenz, hat aber **kein Save-Feld und keinen
Reset-Eintrag** in `normalize_hq_transients`. Damit fällt es durch beide SSOTs.

---

## Heat-Abbau (Ausweg vorhanden?)

**Befund: KEIN dokumentierter Heat-Abbau / kein Reset / kein Ausweg. Heat steigt nur.**

Heat wird ausschließlich **erhöht**:
- `core/sl-referenz.md:477` — „**Heat +1**, TTL -1 Min" (Exfil-Stress-Gate)
- `meta/masterprompt_v6.md:239` — Spotlight-Beat: „**Heat +1**"
- `meta/masterprompt_v6.md:323` — Anachronismus-Sichtung: „**Heat +1** für die Crew"
- `meta/masterprompt_v6.md:721` — „‚Heißes Loot' markieren (**erhöht Heat**)"
- HUD zeigt es als gekapptes Konto: `meta/masterprompt_v6.md:695` → „`… Heat 0/5 …`"

Grep nach `heat -1 / abbau / sinkt / reset / cool / abkühl` (ohne Psi-Heat): **0 Treffer.**
Es gibt **keine** HQ-Heat-Nullung, keinen Zeit-Abbau, keinen Mission-Ende-Reset.

**Urteil: LÜCKE / Balance-Problem (Befund).** Heat hat eine Skala (`/5` im HUD), mehrere
+1-Quellen, aber **keinen Ausweg**. Entweder (a) Heat ist *gewollt* nur ein Per-Mission-
Druckwert, der mit Mission-Ende verfällt — dann fehlt der explizite „Heat verfällt am
Exfil/Mission-Ende"-Satz und das HUD `0/5` suggeriert fälschlich Persistenz; oder (b) Heat
soll persistieren — dann fehlt sowohl das Save-Feld (s.u.) als auch jede Abbau-Mechanik, und
es steigt monoton bis zum Cap ohne Gegenmittel. **Beides ist undokumentiert → muss vor einem
Beat-Patch geklärt werden.** Empfehlung für Patch-Worker: erst Heat-Lebenszyklus definieren
(transient-pro-Mission **oder** persistent+abbaubar), bevor neue Heat-erzeugende Beats
gebaut werden.

---

## Save-Persistenz-Check (alle negativen Werte im Schema?)

Geprüft gegen JSON-Template (masterprompt:990-1050) **und** Pfadbaum (speicher:222-367).

- `stress` — ✅ vorhanden: `meta/masterprompt_v6.md:997` („`"stress": 0`"), speicher:172,623,928.
- `psi_heat` — ✅ vorhanden (bei `has_psi`): speicher:173,624,656,929; mp:1135.
- `reputation.iti` — ✅ vorhanden: `meta/masterprompt_v6.md:1017`; speicher:348.
- `reputation.factions.*` — ✅ vorhanden: `meta/masterprompt_v6.md:1019-1022`; speicher:348.
- `arc.factions` — ✅ vorhanden: speicher:357,729,936.
- `logs.fr_interventions[]` — ✅ vorhanden: speicher:188 (transients-Block? nein → persistent-Pfad),
  speicher:947 („`"fr_interventions": []`"), 1251.
- **`heat` (Noise/Heat) — ❌ FEHLT komplett.** Kein `"heat"`-Feld im JSON-Template, kein
  Pfad im Save-Baum, keine Erwähnung in `transients` oder `required`. Einzige Vorkommen sind
  HUD-Anzeige (mp:695) und Beat-Konsequenzen (mp:239,323; sl-ref:477). Grep
  `"heat"|heat":` liefert nur **`psi_heat`**-Treffer — das echte **Crew-Heat existiert nicht
  im Persistenzmodell.**

**Urteil: 1 PERSISTENZ-LÜCKE — Klasse `research`/`prestige`.**
**`heat` ist genau der Fall, den der Task als Referenz nennt:** ein im Spielfluss aktiv
manipulierter, im HUD gekappt angezeigter Wert (`Heat 0/5`), der **nirgends im Save-Schema
verankert** ist. Über einen `!save`/`!load`-Zyklus (oder Respawn) geht Heat **garantiert
verloren** bzw. ist undefiniert. Wenn Heat einen Lauf überdauern soll → Feld fehlt. Wenn Heat
*nicht* überdauern soll → dann ist die HUD-Kappung `0/5` irreführend und es müsste als reiner
Per-Mission-Beat-Zähler dokumentiert sein (kein `/5`-Konto). So oder so: **inkonsistent.**

---

## Tod-Persistenz

**Befund: SAUBER und zwischen beiden Dokumenten konsistent.**

- `meta/masterprompt_v6.md:941-945` — Tod-Handling, heroischer Tod erzeugt:
  > „Final-Save (`"status":"deceased"`), Abschlussbericht ausgeben. Bei Gruppen
  >  entscheidet die Gruppe."
- `systems/gameflow/speicher-fortsetzung.md:117` — identischer Wortlaut, Sonderausnahme:
  > „Heroischer Tod erzeugt einen Final-Save (`"status":"deceased"`) als
  >  **Sonderausnahme zur HQ-only-Regel**."
- speicher:113-122 stellt klar: Tod-Final-Save ist **kein** Sync-Punkt (kein Sync-Beat davor).

Beide Stellen nennen denselben Mechanismus (`"status":"deceased"`), denselben Trigger (0 LP →
heroischer Tod), und behandeln die HQ-only-Save-Invariante konsistent als Ausnahme.
**Urteil: SAUBER.** Einzige Mini-Anmerkung: Das `status`-Feld taucht im Standard-JSON-Template
(mp:990ff) nicht explizit als Default auf — es wird nur beim Final-Save gesetzt. Das ist
nachvollziehbar (lebende Chars haben implizit `alive`), aber ein expliziter Default
`"status": "active"` im Char-Template wäre robuster. Keine echte Lücke, nur Härtungs-Hinweis.

---

## Doku-Widersprüche

1. **Stress-Cap: `0/10` vs. `0/5` vs. `0/6` — WIDERSPRUCH.**
   - `characters/zustaende.md:310-311` + `:349` (Tabelle): **„feste Skala 0–10 (`stress_max = 10`,
     nicht variabel)"**, Maximum „10 → Panik".
   - `meta/masterprompt_v6.md:693-694`: **„Stress-Max (5 oder 6 je nach *Kalte Nerven*)"**,
     HUD-Beispiele `Stress 1/5`, `Stress 0/5`, `Stress 0/6`.
   - `meta/masterprompt_v6.md:658`: erneut „`stress_max = 10` bleibt fix, siehe zustaende.md".
   → **Direkter Widerspruch:** masterprompt:693 behauptet variablen Cap (5/6), zustaende +
     masterprompt:658 behaupten fixen Cap 10. Beat-Patch, der Stress-Schwellen anfasst (z. B.
     „Malus ab 5"), läuft hier auf widersprüchliche Maxima. **Klärung nötig.** (Plausible
     Auflösung: 10 ist die echte Skala, „5/6" in mp:693 ist veraltetes HUD-Beispiel — aber das
     muss bestätigt/korrigiert werden, nicht geraten.)

2. **Stress-Reset-Ziel: „→ 0" vs. „→ HQ-Basis / gespeicherte Grundwerte" — SPANNUNG/LÜCKE.**
   - `characters/zustaende.md:312`+`:350`: „fällt auf **0**".
   - `core/sl-referenz.md:114` „gespeicherte **Grundwerte**", `:280`/`:495` „**HQ-Basis**".
   → Funktional vermutlich identisch (HQ-Basis = 0), aber **nirgends festgeschrieben**.
     Begriff „HQ-Basis für Stress" ist undefiniert → Risiko, dass ein Patch einen Nicht-Null-
     Basiswert einführt und damit zustaende widerspricht.

3. **Heat: HUD-Konto (`0/5`) ohne Schema/Reset — WIDERSPRUCH HUD ↔ Persistenzmodell.**
   - `meta/masterprompt_v6.md:695` zeigt `Heat 0/5` (gekapptes, getracktes Konto).
   - Kein Save-Feld, kein Reset, kein Abbau (s. o.). → HUD impliziert Persistenz/Cap, das
     Datenmodell kennt Heat nicht. Inkonsistent.

Keine weiteren Widersprüche bei `psi_heat`, `reputation.factions`, `arc.factions`,
`fr_interventions`, Tod gefunden — diese sind über masterprompt ↔ speicher-fortsetzung
deckungsgleich.

---

## Gesamturteil + kritische Befunde

**Gesamturteil: Fundament für einen Beat-Patch ist GRÖSSTENTEILS solide, aber NICHT frei von
Lücken.** Stress-Reset und Persistenz der Fraktions-/Reputations-/Tod-Werte sind konsistent
und SSOT-gestützt. Es gibt jedoch **eine echte Persistenz-Lücke (Heat)** und **zwei
Doku-Widersprüche (Stress-Cap, Stress-Reset-Ziel)**, die der Patch-Worker kennen muss, bevor
er negative Beats anfasst.

**Flos Verdacht (Stress nullt im HQ): BESTÄTIGT** — die Reset-Mechanik existiert mehrfach und
hat einen SSOT-Helper (`normalize_hq_transients`). **Einschränkung:** Ob auf `0` oder auf eine
undefinierte „HQ-Basis" genullt wird, ist nicht eindeutig festgeschrieben (zustaende sagt 0,
sl-referenz/masterprompt sagen „HQ-Basis/Grundwerte"). Sauber genug zum Bauen, sollte aber
einmal verbindlich auf „0" festgenagelt werden.

**Hat ein negativer Wert eine Persistenz-Lücke? JA — `heat`.**

Kritische Befunde (Priorität):

1. 🔴 **`heat` hat KEIN Save-Feld** (Klasse `research`/`prestige`). Im HUD als `Heat 0/5`
   getrackt (mp:695), durch mind. 4 Beats erhöht (mp:239,323,721; sl-ref:477), aber **nicht im
   JSON-Template, nicht im Pfadbaum, nicht in `transients`/`required`**. → Über `!save`/`!load`
   verloren oder undefiniert. **Entscheidung erzwingen: persistent (Feld + Abbau-Regel) ODER
   per-Mission-transient (Reset-Regel + HUD-Wording fixen).**
2. 🔴 **Kein Heat-Abbau/Ausweg dokumentiert** — Heat steigt monoton, kein HQ-/Zeit-/Mission-
   Ende-Reset. Balance-Problem, falls Heat persistieren soll.
3. 🟠 **Stress-Cap-Widerspruch 10 vs. 5/6** (zustaende:310 + mp:658 = 10 fix; mp:693 = 5/6
   variabel). Vor jeder Stress-Schwellen-Änderung auflösen.
4. 🟡 **Stress-Reset-Ziel „0" vs. „HQ-Basis"** nicht verbindlich definiert — Klarstellung
   empfohlen (zustaende:312/350 vs. sl-ref:114/280/495).
5. 🟢 **Tod-Persistenz (`"status":"deceased"`) sauber & konsistent** (mp:944 ↔ speicher:117).
   Optionaler Härtungs-Hinweis: expliziter Default `"status":"active"` im Char-Template.
6. 🟢 **`psi_heat`, `reputation.factions`, `arc.factions`, `fr_interventions`** allesamt im
   Schema vorhanden und reset-/persistenz-konsistent.
