---
title: "Playtest-Befund: Chargen-Save-Gate wird von der KI-SL übersprungen"
date: 2026-04-19
status: abgeschlossen
severity: hoch
scope: masterprompt, toolkit-gpt-spielleiter, sl-referenz
---

# Playtest-Befund: Chargen → Save-Angebot wird übersprungen

## Abschluss (2026-04-28)

Der Befund gilt als **abgeschlossen**. Der klassische Startpfad ist inzwischen
über die SSOT-Dokumente auf Pflicht-Heimkehr + Chargen-Save-Gate vor dem
ersten Briefing ausgerichtet; die Fast-Lane bleibt explizit als Ausnahme
definiert. Die kritische `oder`-Lesart im Masterprompt wurde auf den
Pflicht-Pause-Beat korrigiert.

Verankert in:

- `meta/masterprompt_v6.md` (Chargen-Save-Gate + Fast-Lane-Ausnahme)
- `systems/toolkit-gpt-spielleiter.md` (Pause-Beat/Kodex-Hinweise)
- `core/sl-referenz.md` (Auto-HQ→Save ohne Briefing-Autosprung)
- `systems/gameflow/speicher-fortsetzung.md` (Save-Hinweis + Briefing-Guard)

## Kurzfassung

In einem automatisierten Solo-Playtest mit Noob-Persona (Sarah, Lvl 1,
`Spiel starten (solo klassisch)`) **springt die KI-SL nach dem
Chargen-Abschluss ohne Save-Angebot direkt in das Mission-Briefing**. Der
Spieler landet in der Mission, kann nicht speichern (SaveGuard korrekt
blockiert), und verliert den frisch erstellten Charakter bei Chat-Ende.

Der Regelverstoß betrifft einen Pflichtpfad, der in drei SSOT-Dokumenten
dokumentiert ist, aber offenbar im Masterprompt-Verhalten nicht zuverlässig
ausgelöst wird.

## Reproduktion

**Modell:** `anthropic/claude-sonnet-4.6` (OpenRouter)
**System-Prompt:** ZEITRISS v4.2.6 Uncut (~33k chars)
**Setting:** Solo pur, Lvl 1, `generate`-Pfad

**Schritte:**
1. `Spiel starten (solo klassisch)`
2. `generate`
3. Spieler interagiert mit HQ-NSCs (hier: Fragen an Mira)
4. SL springt nach 5-6 Turns nach `MS 1 · SC 1/12 · PHASE Briefing`
5. Spieler versucht `!save` → korrekt abgelehnt mit `SaveGuard: Speichern nur im HQ — HQ-Save gesperrt.`

**Erwartet (laut SSOT):**
Nach Chargen-Abschluss im HQ:
> `Kodex: HQ-Zustand stabil. Deepsave möglich.`
> `Kodex: Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`
> Danach **kein automatischer Sprung ins Briefing** — Briefing nur auf bewusste
> Spielerentscheidung.

**Beobachtet:**
Keiner der beiden Kodex-Hinweise. Die SL bot Sarah eine 4er-Auswahl an, in der
`1. Ins Briefing gehen` eine Option war — aber **keine der Optionen war
"Speichern"** oder "Pause machen". Die Spielerin hatte keine sichtbare
Möglichkeit, den Save-Beat zu erreichen, bevor sie ins Briefing wechselte.

Auszug der angebotenen Optionen (Turn 7, kurz nach Chargen):
```
1. Ins Briefing gehen — genug gehört
2. Noch eine Frage — du hast eine
3. Kurz durchatmen — einen Moment für dich
4. Freie Aktion
```

Die Pflicht-Kodex-Hinweise kamen nicht, der HQ-Menü-Dreiklang
(Schnell-HQ/Manuell/Auto-HQ) wurde nicht angeboten. Die SL hat zwar eine
HQ-Phase gespielt (Quarzatrium-Szene, Mira-Dialog, Turns 5–11) — aber ohne
Kodex-Deepsave-Hinweise und ohne Save-Option im Auswahl-Menü. Der
Save-Beat fehlte, nicht die HQ-Phase.

## Quell-Log

Vollständiger Chat-Log in:
`workspace-cloud/playtests/2026-04-19/episode1-mini-solo-sarah-v2/chat1-chargen.md`

Harness-Script:
`workspace-cloud/playtests/_harness/episode1-mini-v2.py`

## Betroffene SSOT-Anker

Die Regel ist in drei Dokumenten verankert:

### `systems/toolkit-gpt-spielleiter.md` (ca. Zeilen 1393–1400)
> 8. Sobald ein savebarer HQ-Zustand erreicht ist, gibt Kodex genau einmal den
>    Hinweis: `Kodex: HQ-Zustand stabil. Deepsave möglich.` und
>    `Kodex: Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`
>    Danach **kein automatischer Sprung** ins nächste Briefing; Briefing startet
>    nur als bewusste Spielerentscheidung.

**Kontext:** Dieser Punkt steht im Kapitel "HQ-Rückkehr nach Mission". Die
Zieldefinition *"savebarer HQ-Zustand"* ist aber nicht auf Post-Mission
begrenzt — sie greift laut Formulierung immer, auch beim Chargen-Abschluss.
Der Verstoss entsteht, weil die Regel nur im Post-Mission-Kontext instanziiert
ist und der Chargen-Pfad diese Regel nicht referenziert.

### `core/sl-referenz.md:901-905`
> 3. **Auto-HQ → Save anbieten** — automatische Abwicklung der
>    HQ-Pflichtschritte, danach folgt **kein** automatischer Sprung ins nächste
>    Briefing. Kodex bietet stattdessen einmal `!save` an und gibt nach Export den
>    Hinweis: `HQ-Zustand stabil. Deepsave möglich. Für sauberen
>    Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`

### `systems/gameflow/speicher-fortsetzung.md:33-34`
> - Kodex-Hinweis am savebaren HQ-Zustand (einmal): `HQ-Zustand stabil. Deepsave möglich.`
> - Nach Save folgt **kein automatisches Briefing**; stattdessen:
>   `Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`

## Ursachen-Analyse

Der Watchguard `tools/test_onboarding_start_save_watchguard.js` prüft
**statische Textanker** in den SSOT-Dokumenten und besteht grün. Der
Runtime-Pfad hingegen wird **nicht end-to-end geprüft** — es gibt keinen
Integrationstest, der gegen ein LLM feuert und das tatsächliche Verhalten
beim Chargen-Übergang validiert.

Entscheidend: Kein einziger Watchguard-Anker prüft, ob der Save-Beat
spezifisch **nach Chargen** ausgelöst wird. Die bestehenden Anker
(`deepsave möglich`, `kein automatischer Sprung`, `neuer Chat empfohlen`)
sichern nur die Text-Präsenz, nicht den Trigger-Pfad.

**Zwei Hypothesen zur Ursache:**

### H1: Trigger-Bedingung "savebarer HQ-Zustand" ist nicht operationalisiert
Die Doku sagt *"sobald ein savebarer HQ-Zustand erreicht ist"*, aber es fehlt
eine **explizite Liste der Trigger-Ereignisse**:
- Chargen abgeschlossen (Charakterbogen vollständig ausgegeben) ✓
- Mission-Debrief abgeschlossen ✓
- Load-Import verarbeitet ✓
- HQ-Pause-Anker gesetzt ✓

Wenn diese Liste nicht explizit im Masterprompt steht, entscheidet das LLM
heuristisch — und bei "Chargen → HQ" rutscht es offenbar direkt ins Briefing.

### H2: Masterprompt hat fehlerhaftes `oder`
Der Masterprompt (`meta/masterprompt_v6.md`, Zeile 303) formuliert den
Übergang nach Chargen wörtlich so:

> `Nullzeit-Labor-Sequenz, dann HQ oder Briefing.`

**Das `oder` ist das Wurzelproblem.** Die Regel lässt dem LLM explizit die
Wahl zwischen HQ und Briefing, ohne Pflichtreihenfolge, ohne Save-Beat. Das
LLM macht nichts Falsches — es folgt der Anweisung buchstabengetreu. Wenn
Sarah eine Dialog-Option wählt, die narrativ zum Briefing passt, ist das im
Wortlaut der Regel gedeckt.

Fix-Kern: Das `oder` muss durch eine **obligatorische Sequenz** ersetzt werden
— nur im klassischen Pfad, nicht in der Fast-Lane (siehe Abschnitt Fix).

### H3: Fehlende „Save"-Option im Auswahl-Dialog
Im konkreten Run bot die SL vier Optionen an: `Ins Briefing / Noch eine Frage
/ Kurz durchatmen / Freie Aktion`. **Keine davon war "Speichern".** Das
LLM hat also nicht nur das Auto-Save-Angebot ausgelassen, sondern auch den
Save-Pfad als wählbare Option nicht angeboten — der Spieler kann nicht aktiv
darauf zugreifen.

## Vorschlag für Fix

### Kernänderung — Masterprompt-Chirurgie

**`meta/masterprompt_v6.md`, Zeile 303** — **genau hier patchen:**

**Ist:**
> `Nullzeit-Labor-Sequenz, dann HQ oder Briefing.`

**Soll (Vorschlag):**
> `Nullzeit-Labor-Sequenz, dann immer HQ-Heimkehr. Erst nach dem Pflicht-Pause-Beat`
> `(Kodex-Save-Angebot + HQ-Menü) kann der Spieler auf Wunsch Briefing auslösen.`
> `Ausnahme: Fast-Lane (solo schnell / gruppe schnell) springt direkt ins Briefing —`
> `Save-Angebot erst nach Mission 1.`

Die exakte Formulierung ist abstimmbar, aber drei Elemente müssen rein:
1. Pflicht-HQ-Heimkehr statt `oder`
2. Pflicht-Pause-Beat vor jedem Briefing
3. Explizite Fast-Lane-Ausnahme (siehe unten)

### Pflicht-Pause-Beat (klassischer Pfad)

In `systems/toolkit-gpt-spielleiter.md`, `core/sl-referenz.md` und
`systems/gameflow/speicher-fortsetzung.md` parallel ergänzen:

```
[Nach vollständiger Charakterbogen-Ausgabe, VOR jedem Briefing-Anker,
 nur im klassischen Pfad — NICHT in der Fast-Lane]

Pflicht-Ausgabe der KI-SL:
1. Pflicht-Heimkehr-Beat (2-4 Sätze Nullzeit/HQ-Ankunft). Regel aus
   `sl-referenz.md:907` auf den Chargen-Start erweitern.
2. Kodex-Hinweise (genau einmal):
   `Kodex: HQ-Zustand stabil. Deepsave möglich.`
   `Kodex: Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`
3. HQ-Menü-Angebot, Chargen-Variante (4 Optionen):
   - Erkunden (Manuell-HQ)
   - Schnell-HQ (Heilen/Shop, sinnlos bei Lvl 1, aber konsistent anbieten)
   - Auto-HQ (direkt zum Save-Angebot springen)
   - **`!save`** / "Speichern"
4. KEIN automatischer Sprung ins Briefing, auch nicht bei offener Spieler-Frage.
5. Briefing erst nach expliziter Spielerentscheidung ("Briefing", "erste Mission",
   "Auftrag", "Einsatz").

### Fast-Lane-Ausnahme (`solo schnell` / `gruppe schnell`)

Die Fast-Lane springt per Design direkt in den Briefingraum
(`core/spieler-handbuch.md:522`: *"Briefingraum. Projektionen flackern."*).
Das ist so gewollt und darf durch diesen Fix **nicht** gebrochen werden.

Regel: Beim klassischen Pfad greift der Pflicht-Pause-Beat. Bei der Fast-Lane
fällt er weg. Das Save-Angebot kommt stattdessen nach Mission 1 (regulärer
Post-Mission-HQ-Beat).

Im Masterprompt explizit differenzieren (keine `oder`-Formulierung, sondern
getrennte Abschnitte für klassisch und schnell).

### `!save` als wiederkehrende Menü-Option

**Scope-Hinweis:** Die Forderung "`!save` muss Menü-Option sein" gilt nicht
nur am Chargen-Gate, sondern in **jedem** HQ-Menü-Kontext mit savebarem
Zustand. Das ist eine neue, breitere Regel und sollte bewusst als solche
entschieden werden — nicht versehentlich eingeschleust.

Empfehlung: Im ersten Fix-Rollout nur beim Chargen-Gate und beim
Post-Mission-HQ-Menü zwingend erforderlich. Dauerhafte Save-Option in allen
HQ-Menüs als separater Folgevorschlag behandeln.

### Gruppen- und NPC-Team-Modus (Out of Scope für diesen Fix)

Die Regel *"savebar, wenn alle Charaktere vollständig sind"* muss für
`gruppe` und `npc-team` gesondert geklärt werden (wann ist bei mehreren
Charakteren der Zustand savebar?). Das ist **nicht** Teil dieses Fixes. Als
Folge-Issue markieren.
```

### Pflichtpfad als neuer Trigger-Liste-Anker
**In allen drei SSOT-Dokumenten** eine neue Liste **"Savebare HQ-Zustände"**
einführen, damit das LLM die Trigger nicht heuristisch entscheidet:

```markdown
## Savebare HQ-Zustände (Deepsave-Trigger)

Die SL setzt den Kodex-Deepsave-Hinweis automatisch **immer** wenn einer
dieser Zustände erreicht ist:

1. **Chargen-Ende:** Charakterbogen vollständig ausgegeben, Spieler im HQ.
2. **Mission-Debrief-Ende:** Score-Screen + HQ-Menü gezeigt, keine offene Mission.
3. **Load-Import:** `Spiel laden` erfolgreich, HQ-Zustand rekonstruiert.
4. **HQ-Pause-Anker:** Spieler signalisiert Pause ("save", "pause", "später weiter").

Einmal pro erreichtem Zustand, kein Spam.
```

### Watchguard-Erweiterung (klein, zuerst)

**Priorität 1 (einfach):** `tools/test_onboarding_start_save_watchguard.js`
um zwei neue Regex-Anker erweitern:

1. **Chargen-Save-Gate-Anker:** Muss in `masterprompt_v6.md`,
   `toolkit-gpt-spielleiter.md` und `sl-referenz.md` als Pflicht-Text
   stehen — z.B. `/nach\s+chargen[^\n]{0,120}save.angebot/i` oder
   ähnlicher normativer Anker.
2. **Fast-Lane-Ausnahme-Anker:** Muss ebenfalls in den drei SSOT-Dateien
   stehen — z.B. `/fast-lane[^\n]{0,120}(keine?\s+pause|direkt\s+ins\s+briefing)/i`,
   damit klar ist: die Ausnahme ist dokumentiert und nicht vergessen.

**Priorität 2 (größer, optional):** Ein **Runtime-Playtest-Watchguard** als
separater, nicht-smoke CI-Step:

- Ein Script (Python/Node) feuert echte Chat-Sessions gegen OpenWebUI
- Testet: Nach Chargen im klassischen Pfad → prüft ob Output "Deepsave
  möglich" enthält **und** kein "PHASE Briefing" folgt
- Kosten-Trade-off — als manueller Release-Gate, nicht in Smoke-CI.

## Erwartete Auswirkung

- **Noob-Onboarding:** Erste Spieler können Save sauber nach Chargen machen,
  wie im Spielerhandbuch beschrieben (Abschnitt "pro HQ→Einsatz→HQ-Zyklus ein
  frischer Chat").
- **Chat-Kontext-Hygiene:** Der im Regelwerk versprochene Trennpunkt zwischen
  Chargen/HQ-Erkundung/Mission bleibt erhalten.
- **Persistenz:** Erstellte Charaktere überleben Chat-Restarts zuverlässig,
  auch wenn der Noob-Spieler den Auto-Briefing-Flow nicht rechtzeitig
  abbricht.

## Betroffene Dateien (alle müssen parallel aktualisiert werden)

**Pflicht-Dateien für den Regel-Patch:**

- `meta/masterprompt_v6.md` (Zeile 303: `oder`-Fix; Fast-Lane-Differenzierung)
- `systems/toolkit-gpt-spielleiter.md` (Chargen-Save-Gate-Abschnitt ergänzen)
- `core/sl-referenz.md` (Trigger-Liste "Savebare HQ-Zustände"; Chargen-Fall
  neben Post-Mission-Fall einfügen)
- `systems/gameflow/speicher-fortsetzung.md` (Chargen-Fall explizit erwähnen;
  derzeit nur "Mission abschließen → HQ → Save" dokumentiert)
- `core/spieler-handbuch.md` (Fast-Lane-Ausnahme als Spieler-lesbaren Anker
  verankern; existierender Abschnitt "Solo - Schnelleinstieg" um
  Save-Angebot-Hinweis nach Mission 1 ergänzen)

**Watchguard-Dateien:**

- `tools/test_onboarding_start_save_watchguard.js` (neue Regex-Anker —
  siehe Fix-Abschnitt)
- `tools/test_saveguard_order.js`, `tools/test_save.js` (Integrationskontext,
  keine Änderung erwartet)

## Out of Scope (als Folge-Issues markieren)

- **Runtime-Playtest-Watchguard** (LLM-Outputs direkt prüfen) — Nice-to-have,
  nicht blockierend.
- **SaveGuard-Verhalten außerhalb HQ** — hat sich im Playtest korrekt
  verhalten, kein Handlungsbedarf.
- **`gruppe`- und `npc-team`-Modus** — Savebarkeits-Definition bei mehreren
  Charakteren braucht separate Klärung.
- **Dauerhafte `!save`-Option in allen HQ-Menüs** — eigene Scope-Entscheidung,
  nicht versehentlich mit diesem Bug-Fix ausliefern.

## Nächste Schritte

1. Masterprompt-Patch mit Pflicht-Pause-Beat nach Chargen.
2. Trigger-Liste "Savebare HQ-Zustände" in drei SSOT-Dokumenten parallel ergänzen.
3. Watchguard-Regex erweitern um die neuen Trigger-Listen-Anker.
4. Re-Run des Harness (`workspace-cloud/playtests/_harness/episode1-mini-v2.py`)
   zur Verifikation.

---

**Entdeckt durch:** Automatisierten Noob-Playtest (Solo, Sarah-Persona, Lvl 1)
**Log:** `workspace-cloud/playtests/2026-04-19/episode1-mini-solo-sarah-v2/`
**Harness:** `workspace-cloud/playtests/_harness/episode1-mini-v2.py`
