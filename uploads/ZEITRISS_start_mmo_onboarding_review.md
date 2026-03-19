# ZEITRISS – Start/MMO/Onboarding Review (aktueller Nachcheck)

## Kurzurteil

Der aktuelle Stand ist **deutlich stärker** als in den vorigen Runden. Die MMO-Illusion über Save/Load, Split/Merge, Session-Anker, persönliche Wahrheit und NPC-Kontinuität trägt inzwischen spürbar. Die letzten großen Bremsen sitzen **nicht** mehr im Weltdesign, sondern im **Einstiegsvertrag** und in ein paar verbleibenden **oldschooligen UI-/Menü-Mustern**.

Mein Urteil in einem Satz:

**Save/Load ist fast da, aber Start/Onboarding und HQ-Navigation denken an einigen Stellen noch zu sehr wie ein klassisches Menüspiel statt wie eine KI-geführte, zusammenhängende Dienstwelt.**

---

## Was jetzt schon gut sitzt

- **Session-Anker + persönliche Wahrheit + Kontinuität** fühlen sich konzeptionell richtig an.
- **Mehrfach-Load** und **NPC-Kontinuität** sind als Weltsynthese gedacht und nicht mehr nur als Host-Save-Hack.
- **HQ-only Save** bleibt als Stabilitätsanker sinnvoll.
- **README** erklärt inzwischen klar, dass der Save der Charakter ist und Multiplayer ohne Server läuft.
- **ITI-Hauskanon** und feste Kernorte/Kernfiguren stützen die MMO-Illusion.

---

## Die letzten Bremser

### 1) Der Startvertrag ist noch zu „command-first“

Intern sagt ZEITRISS bereits, dass der Dispatcher **natürliche Sprache** versteht. Gleichzeitig verlangen Spielertexte und SL-Referenz weiterhin strikte Startsyntax mit Klammern.

Das wirkt technisch, obwohl die KI es besser könnte.

### Problem

Aktuell muss sich der Spieler zu sehr an den Parser erinnern, statt einfach sein Anliegen auszusprechen.

### Zielbild

- **Spieler-facing:** natürliche Sprache reicht.
- **Intern:** die KI normalisiert auf den kanonischen Startpfad.
- **Syntaxhinweis nur**, wenn das Anliegen wirklich nicht eindeutig ist.

### Empfehlung

Akzeptiere zusätzlich stillschweigend Formulierungen wie:

- „Ich will allein neu anfangen.“
- „Wir sind zu dritt und wollen mit neuen Chars starten.“
- „Ich lade meinen Save und joine die Gruppe.“
- „Solo, klassisch, bitte generieren.“
- „Ich will mit zwei NPCs loslegen.“

Die KI soll intern daraus denselben Dispatcher-Aufruf bauen, aber **nicht** mit Startsyntax belehren, solange die Absicht klar ist.

---

### 2) `klassisch` vs. `schnell` ist noch als gleichwertige Gabel zu prominent

Momentan fragt der Startpfad bei fehlendem Modus noch nach **„klassisch oder schnell?“**. Das ist funktional okay, aber UX-seitig nicht der modernste Weg.

### Warum das bremst

Dein eigentlich smarter Pfad ist längst da:

- **klassisch + generate/custom generate**
- oder klassisch + manuell bauen

Das ist schon die KI-native Version von Charaktererschaffung.

### Empfehlung

Mache daraus den **kanonischen Standardpfad**:

1. **Neu oder Laden?**
2. Falls neu: **solo / npc-team / gruppe?**
3. Dann **automatisch klassisch** als Default.
4. Erste echte Frage:
   - `generate`
   - `custom generate`
   - `selbst bauen`
5. **Schnellstart** bleibt erhalten, aber nur als expliziter Wunsch oder als Alias für Demo-/Kurzrunden.

### Ergebnis

Der Spieler denkt nicht mehr in „Menümodus“, sondern in „wie will ich meinen Chrononauten erzeugen?“

---

### 3) `generate` lebt in der Charaktererschaffung, aber nicht stark genug im Start-SSOT

Die moderne Logik ist vorhanden, aber nicht an der Spitze des Startvertrags verankert.

### Problem

Der Masterprompt priorisiert weiter im Wesentlichen:

- klassisch
- schnell
- load

`generate/custom generate` ist eher im Charakterbau versteckt, nicht als **primäre Startentscheidung** verankert.

### Empfehlung

Im Start-SSOT explizit festziehen:

> **Klassischer Standardpfad:** Nach Wahl von solo / npc-team / gruppe fragt die KI zuerst, ob der Charakter **generiert**, **teil-generiert** (`custom generate`) oder **komplett manuell** gebaut werden soll.

So landet die modernste UX an der Startoberfläche statt nur im Regeltext.

---

### 4) Archetypen/Pregens sind noch zu präsent für ein KI-first-Spiel

Die Archetypen sind gut geschrieben und nützlich – aber im aktuellen Slot-System bleiben sie ein aktives Runtime-Modul.

### Problem

Dadurch konkurrieren sie im Wissensspeicher mit dem viel eleganteren `generate`-Pfad.

### Empfehlung A (klein, sicher)

Modul behalten, aber im Kopf klar markieren:

> **Archetypen sind Inspiration und One-Shot-Hilfe, nicht der bevorzugte Startpfad.**

### Empfehlung B (besser)

Pregens und Start-Archetypen in eine **nicht geladene Beispiel-/Appendix-Datei** auslagern oder `slot:false` machen.

### Ziel

Die KI soll bei frischen Starts zuerst an **individuelle Generierung** denken, nicht an vorgefertigte Heldenblöcke.

---

### 5) Die HQ-Navigation nach Mission ist noch zu menühaft und an einer Stelle sogar kontraproduktiv

Der kritischste Restblock aus UX-Sicht ist das **HQ-Menü nach Missionen**.

Aktuell steht sinngemäß:

- Schnell-HQ
- HQ manuell erkunden
- Auto-HQ & Save

und danach folgt direkt das nächste Briefing.

### Problem

Das beißt sich mit dem ansonsten guten Save-Contract:

- Neuer Chat pro Mission wird empfohlen.
- Der Save ist die Quelle der Wahrheit.
- Die KI soll den Zeitpunkt für Save/Load sauber vorschlagen.

Wenn **Auto-HQ & Save direkt ins nächste Briefing springt**, animiert das zu langen Chats und verwässert den stabilen Rhythmus.

### Empfehlung

Dritte Option umbauen zu:

- **Auto-HQ → Save anbieten**
- nach `!save` **nicht automatisch** ins nächste Briefing springen
- stattdessen klarer Kodex-Satz:

> `Kodex: HQ-Zustand stabil. Deepsave möglich. Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`

Optional danach zwei Klartextoptionen:

1. **Jetzt speichern**
2. **Ohne Speichern im HQ bleiben**

Nicht direkt:

3. nächstes Briefing starten

Das Briefing soll als **bewusster nächster Schritt** passieren, nicht als Autoband.

---

### 6) README, Setup-Guide und Script sind noch nicht vollständig auf denselben Onboarding-Satz harmonisiert

Hier sitzt aktuell ein echter Produkt-UX-Drift:

- README führt auf **OpenWebUI + Script + `solo klassisch`**.
- Das Script ist inzwischen ebenfalls auf **Sonnet 4.6** als Standard ausgerichtet.
- Der Setup-Guide endet aber noch bei **`solo schnell`** und trägt in seiner Erzählung noch Altlasten aus dem älteren Default-Denken.

### Empfehlung

Ein einziger kanonischer Satz in allen drei Einstiegspunkten:

> **Für den ersten echten Run: Setup in OpenWebUI, Preset wählen, dann `Spiel starten (solo klassisch)` oder einfach natürlich sagen, dass du neu beginnen willst. Die KI-SL übernimmt den Rest.**

Und direkt darunter:

> **Für erfahrene Spieler:** `solo schnell` bleibt als Fast-Lane/Demo-Modus verfügbar.

---

### 7) README ist als Landingpage gut, aber noch nicht scharf genug auf „MMO ohne Server“ und „du musst nichts lesen“

README ist sachlich gut – aber oben steht noch viel Setup-/Modell-/Lizenzlogik, bevor der eigentliche Zauber maximal klar sitzt.

### Mein Urteil

Ja: **README ist aktuell noch etwas zu ops-lastig für die eigentliche Produktmagie.**

### Ziel der ersten 10 Sekunden auf GitHub

Der Besucher sollte sofort verstehen:

1. **Das ist ein KI-geführtes Zeitreise-RPG.**
2. **Das fühlt sich wie ein MMO an, braucht aber keinen Server.**
3. **Der Save ist dein Charakter.**
4. **Ich muss keine Bücher lesen – ich richte OpenWebUI ein und spreche dann direkt mit der KI-SL.**

### Empfehlung

Modellpreise, längere TL;DR-Abschnitte und Teile des Betriebsmodells eine Ebene tiefer schieben.

README-Topblock stärker so:

- 1 Satz Fantasy/Promise
- 1 Satz MMO-ohne-Server
- 1 Satz „Save = Charakter“
- 3-4 Setup-Schritte
- 1 Satz „ab jetzt einfach mit der KI-SL sprechen“

---

## Meine konkrete Produktempfehlung

## **Behalte vier sichtbare Dinge, aber ändere ihre Hierarchie**

### Sichtbar für Spieler

1. **Neu starten**
2. **Save laden**
3. **solo / npc-team / gruppe**
4. **generate / custom generate / selbst bauen**

### Nur bei ausdrücklichem Wunsch sichtbar

- `schnell`
- Archetypen/Pregens
- streng technische Startsyntax
- Menüdenken wie „Auto-HQ & Save → nächstes Briefing“

---

## Copy-paste-Issues für Codex / Agenten

### Issue 1 — Startsyntax player-facing von „Pflichtkommando“ auf natürliche Sprache umstellen

**Titel:** Accept natural-language starts; strict command syntax becomes fallback only

**Ziel:**
Spieler dürfen ZEITRISS natürlichsprachlich starten. Kanonische Kommandos bleiben erhalten, aber sind nicht mehr der einzige player-facing Pfad.

**Umsetzen in:**

- `core/sl-referenz.md`
- `systems/toolkit-gpt-spielleiter.md`
- `core/spieler-handbuch.md`
- `meta/masterprompt_v6.md`

**Regel:**

- Wenn die Absicht klar ist, akzeptiere natürliche Sprache.
- Nutze den Syntax-Hinweis nur bei echter Mehrdeutigkeit.
- Intern weiter auf denselben Dispatcher mappen.

**Beispiele, die funktionieren sollen:**

- „Ich will alleine neu anfangen.“
- „Wir sind zu zweit und laden unsere Saves.“
- „Ich will solo klassisch, aber bitte generieren.“
- „Mit zwei NPCs starten.“

**Wichtig:**
Die kanonischen Kommandos bleiben dokumentiert, aber nicht mehr als harter Immersionsstopper.

---

### Issue 2 — `klassisch + generate` als Standardpfad verankern, `schnell` zur Fast-Lane herabstufen

**Titel:** Make classic+generate the canonical onboarding path

**Ziel:**
Der Standard-Neustart soll nicht mehr primär „klassisch oder schnell?“ fragen, sondern auf KI-native Charaktererschaffung zielen.

**Neue Startlogik:**

1. Neu oder Laden?
2. solo / npc-team / gruppe?
3. Default = klassisch
4. Dann: `generate` / `custom generate` / `selbst bauen`
5. `schnell` nur bei explizitem Wunsch

**Umsetzen in:**

- `meta/masterprompt_v6.md`
- `core/sl-referenz.md`
- `core/spieler-handbuch.md`
- `docs/setup-guide.md`

---

### Issue 3 — `generate/custom generate` in den Masterprompt-Dispatcher holen

**Titel:** Promote generate/custom generate into the top-level start contract

**Ziel:**
Die modernste Charaktererschaffung darf nicht nur im Regeltext leben, sondern muss im eigentlichen Runtime-Dispatcher sichtbar werden.

**Änderung:**
Im Abschnitt `I) Start, Charaktere, Save/Load` des Masterprompts ergänzen:

> Nach Wahl des Startmodus (`solo`/`npc-team`/`gruppe`) fragt die KI im klassischen Standardpfad zuerst, ob der Charakter **generiert**, **teil-generiert** (`custom generate`) oder **komplett manuell** gebaut werden soll.

---

### Issue 4 — Archetypen/Pregens aus dem Default-Runtime-Druck nehmen

**Titel:** Demote archetypes/pregens from default runtime priority

**Ziel:**
Archetypen bleiben als Inspiration erhalten, sollen aber die KI beim Standardstart nicht dominieren.

**Empfohlene Varianten:**

- Entweder `characters/charaktererschaffung-optionen.md` in einen stärkeren Inspirations-/Appendix-Rahmen setzen,
- oder Pregens/Start-Archetypen in eine eigene nicht-geladene Datei auslagern,
- oder klar markieren: **nicht bevorzugter Startpfad**.

**SSOT-Satz:**

> Archetypen sind Inspirations- und One-Shot-Material. Der empfohlene Standardstart erfolgt über klassisch + `generate` / `custom generate` oder manuelle Erschaffung.

---

### Issue 5 — HQ-Menü mit Save-Contract harmonisieren

**Titel:** Remove same-chat pressure from HQ menu after mission

**Ziel:**
Das HQ-Menü darf den empfohlenen Save→neuer Chat-Rhythmus nicht unterlaufen.

**Aktuelle Problemstelle:**
`Auto-HQ & Save` führt zu stark Richtung „gleich weiter zum nächsten Briefing im selben Chat“.

**Neue Regel:**

- Nach jedem savebaren HQ-Zustand bietet Kodex genau einmal kurz `!save` an.
- Nach erfolgreichem `!save` folgt ein klarer Hinweis auf den empfohlenen neuen Chat.
- Kein automatischer Sprung ins nächste Briefing nach Auto-HQ.

**Neuer Kodex-Satz:**

> `Kodex: HQ-Zustand stabil. Deepsave möglich. Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`

---

### Issue 6 — README / Setup-Guide / Script auf einen kanonischen Onboarding-Satz harmonisieren

**Titel:** Align README, setup guide and script around one canonical first-run path

**Ziel:**
Keine widersprüchlichen Erstempfehlungen mehr.

**Sollzustand:**

- erster echter Run = OpenWebUI-Setup + Preset + `solo klassisch`
- `solo schnell` = optionaler Fast-Lane-Modus
- Sonnet 4.6 = Referenzmodell in allen Einstiegstexten konsistent

---

### Issue 7 — README als Produkt-Landingpage schärfen

**Titel:** Rewrite README top section around the product promise, not around ops detail

**Ziel:**
Die erste Bildschirmhöhe auf GitHub soll die Produktfantasie verkaufen.

**Pflichtbotschaften ganz oben:**

- ZEITRISS ist ein KI-geführtes Zeitreise-RPG.
- Es fühlt sich wie ein MMO an, braucht aber keinen Server.
- Dein Save ist dein Charakter.
- Nach dem OpenWebUI-Setup sprichst du einfach direkt mit der KI-SL.

**Details verschieben:**

- Preistabelle
  n- längere Modellvergleiche
- Teile der Hosting-/Lizenztexte

---

## Direkt übernehmbare Textbausteine

### 1) README-Topblock (Ersatzvorschlag)

```md
> **ZEITRISS** ist ein KI-geführtes Zeitreise-RPG im Chat: Du spielst einen Chrononauten des ITI und erlebst eine persistente, zusammenhängende Einsatzwelt über Missionen, Rifts, Gruppenwechsel und neue Chats hinweg.
>
> **MMO ohne Server:** Dein JSON-Save ist dein Charakter. Du nimmst ihn zwischen Runden, Gruppen und KI-Spielleitungen mit – ohne Account, ohne Lock-in, ohne zentrale Datenbank.
>
> **Wichtig:** Du musst das Regelwerk nicht lesen, um zu spielen. Richte OpenWebUI ein, wähle das ZEITRISS-Preset und sprich ab dann direkt mit der KI-SL.
```

### 2) README-Quickstart (kompakter Zielpfad)

```md
## In 3-5 Minuten ins Spiel

1. OpenWebUI + Provider einrichten.
2. `./scripts/setup-openwebui.sh` ausführen.
3. Preset wählen.
4. Neuen Chat öffnen.
5. Entweder `Spiel starten (solo klassisch)` oder einfach natürlich sagen, dass du neu beginnen willst.

Ab dann übernimmt die KI-SL alles Weitere – inklusive Charaktererschaffung, Briefing, HQ-Flow und Save/Load-Hinweisen.
```

### 3) Masterprompt-Patch – neuer Default-Startpfad

```md
- **Fehlt beim Neustart der Modus**, nutze standardmäßig den klassischen Startpfad statt zuerst zwischen `klassisch` und `schnell` zu verzweigen.
- **Frage im klassischen Standardpfad zuerst:** `generate`, `custom generate` oder `selbst bauen`?
- **`schnell`** bleibt verfügbar, wird aber nur genutzt, wenn der Spieler es ausdrücklich wünscht oder eine sehr kurze Demo-Runde will.
- **Natürliche Sprache reicht:** Wenn die Startabsicht klar ist, normalisiere sie intern auf den kanonischen Dispatcher. Syntaxhinweise nur bei echter Mehrdeutigkeit.
```

### 4) Save/Load-Patch – sauberer KI-Hinweis im HQ

```md
Sobald ein savebarer HQ-Zustand erreicht ist, gibt Kodex genau einmal einen knappen Hinweis:

`Kodex: HQ-Zustand stabil. Deepsave möglich.`
`Kodex: Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`

Der Save selbst entsteht weiterhin nur auf explizites `!save`.
Nach erfolgreichem Save startet kein automatisches Briefing im selben Zug.
```

### 5) Handbuchsatz gegen Oldschool-Gefühl

```md
Die kanonischen Startbefehle bleiben als verlässliche Kurzform dokumentiert. Im Spielbetrieb versteht die KI-SL jedoch auch natürliche Sprache und normalisiert klare Startwünsche intern auf denselben Startpfad.
```

---

## Mein Schlussurteil

Wenn du nur **drei** Dinge anfasst, dann diese:

1. **Syntaxhärte raus aus der Spieleroberfläche**
2. **klassisch + generate zum echten Standard machen**
3. **HQ-Menü auf Save→neuer Chat trimmen statt Auto-Weiterleitung**

Wenn diese drei sitzen, wirkt ZEITRISS beim Start nicht mehr wie ein sehr gutes KI-Spiel mit klassischen Menüresten, sondern wie genau das, was du eigentlich willst:

**eine KI-simulierte Dienstwelt, in die man einfach hineinspricht.**
