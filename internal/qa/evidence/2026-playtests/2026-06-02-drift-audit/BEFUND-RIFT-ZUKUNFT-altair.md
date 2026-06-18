# Befund: Rift-Horror-Action & Zukunft (Altair, selbst-verifiziert 2026-06-02)

> Worker-Run brach in der letzten Verifikationsphase ab (kein Report geschrieben),
> lieferte aber den Schlüssel-Datenpunkt (NSC-Schablone mit Armor existiert). Rest
> selbst per grep/read gegen die Quelle verifiziert. Messlatte:
> VISION-RIFT-ZUKUNFT-2026-06-02.md.

## Teil A — Rift-Ops Horror-Action

### A1 — Action-Frontloading → TEILWEISE/VERLETZT
- `kreative-generatoren-missionen.md:293-300`: Rift-14-Step = Tatort (1-4) +
  Leads (5-9) + Boss (10) + Resolution (11-14). **9 von 14 Szenen Ermittlung
  vor dem Boss.** "Entdeckung vor Eskalation", "Monster als Ahnung", "Leads-Phase:
  drei Würfel-Checks". → Zu ermittlungslastig vs. Flos "vor allem actionlastig".
- Patch: Action-Frontloading-Satz analog Core-Ops-Fix — physische Para-Begegnungen
  schon in Tatort/Leads-Phasen, Ermittlung läuft WÄHREND der Action.

### A2 — Handfeste Parawesen → VERLETZT (Glaskanonen bestätigt)
- `kreative-generatoren-begegnungen.md:461-572`: Alle Standard-Paramonster
  `LP-Pool: W6 × 2` (~7 LP) bzw. `W6 × 1` (~3,5 LP), **Defense-Schwelle 4-6,
  KEIN Armor-Feld**.
- `core/wuerfelmechanik.md:345`: mittlerer Treffer ~3 LP, krit +2.
- RECHNUNG: 7 LP / 3 LP pro Treffer = **2-3 Treffer bis tot**. Vollteam macht das
  in EINER Runde. = Glaskanone. Genau Flos "die sollen ein paar Kugeln vertragen".
- ABER: Das System KENNT bereits zähe Statblocks: Risikostufen S/M/L/XL
  (`begegnungen.md:89, 653`), und Casefile-Bosse nutzen `LP | Armor | STR...`
  (`begegnungen.md:688, 696`). Das Armor-Feld existiert — die Standard-Paramonster
  nutzen es nur nicht.
- Patch (chirurgisch, kein neues System): Eine **handfeste/Brute-Para-Klasse**
  einführen, die das bestehende Armor-Feld + höhere LP-Tranche nutzt (z.B. LP
  W6×3-4 + Armor 1-2), als Mittelklasse zwischen Glaskanone-Standard und Boss.
  Plus Satz: physische Rift-Kämpfe nutzen bevorzugt handfeste Parawesen, nicht
  nur Glaskanonen.

### A3 — Horror-Tonalität als Pflicht → FEHLT KOMPLETT
- grep horror/grusel/schauer/unheimlich/hölle: nur `sl-referenz.md:897` "Body
  Horror" im **Safety Sheet** (Line/Veil-Toggle, KEINE Tonalitäts-Pflicht), und
  ein Beispiel-Hook "Vollmond-Dorf-Horror" (`missionen.md:1010`).
- Es gibt KEIN Rift-Horror-Pflichtgate (analog zum Kampfszenen-Pflichtgate).
- Patch: Rift-Horror-Pflichtgate in masterprompt §C — horror-artige Tonalität als
  Pflicht für Rift-Ops (sensorischer Grusel, Bedrohungsaufbau, Dread). RISIKO:
  Safety Sheet respektieren (Body Horror default Veil/Off-Screen) → Horror über
  Atmosphäre/Dread/Bedrohung, nicht Gore-Pflicht.

### A4 — Rift-Boss als Horror-Höhepunkt → TEILWEISE
- Bosskampf-Pflichtgate (masterprompt §C:250-259) deckt Rift-Boss SC10 mechanisch
  ab (3 Phasen, LP-Tranchen, Phase-Resistance). Aber **rein mechanisch** — keine
  Horror-Rahmung ("soll das Schauern lehren").
- Patch: Im Rift-Horror-Pflichtgate den Boss als Horror-Höhepunkt rahmen (Dread-
  Peak, das Jenseitige am stärksten spürbar).

### A5 — "Hölle leicht angedeutet" → FEHLT
- Kein Hinweis auf angedeutetes Jenseitiges/Höllisches. Das One-Weird-Thing-Budget
  (`missionen.md:305`) erlaubt genau 1 Anomalie — gut, das stützt "leicht
  angedeutet" sogar.
- Patch: Im Horror-Pflichtgate die "nur andeuten, nie ausbuchstabieren"-Linie
  verankern (Event-Horizon-Prinzip: der Grusel ist im Ungesagten).

## Teil B — Allzeitlichkeit/Zukunft

### B1 — Tragen Core-Ops-Patches in der Zukunft? → JA (Patches sind setting-agnostisch)
- Kern-Auftrag, Strang-Wahl, Action-Kern sind alle epochenneutral formuliert
  ("Ort + Ziel-Objekt/Person + Abschluss"). Flos Raumschiff-Beispiel passt 1:1
  (Schiff = Ort, Crew/Planet-Besiedlung = Ziel, Raptoren beseitigen = Abschluss).
- Kein Patch nötig — evtl. ein Zukunfts-Beispiel zur Illustration.

### B2 — IA/RW-Spots + Epochen für Zukunft → TEILWEISE
- IA/RW-Spot-Pflichtgate (masterprompt §C:219-225) nennt Spot-Profile: historisch/
  mystisch/technisch-verborgen/liminal. "technisch-verborgen" deckt Zukunft
  teilweise (Wartungsschacht, Tunnel), aber die Beispiele sind vergangenheits-/
  gegenwartslastig. Raumschiff/Orbital/Kolonie als Spot-Typen nicht explizit.
- ABER Zukunft ist breit da: `begegnungen.md:232` "Postorbitales Zeitalter",
  `:308` "Orbitalstation 2030+", Orbital-Encounters, Sat-Strikes, Zukunfts-Doubles.
- Patch (klein): IA/RW-Spot-Beispiele um Zukunfts-Spots ergänzen (Frachtschleuse,
  Kälteschlaf-Deck, Orbital-Dockingring, Kolonie-Reaktorkern) — ein Satz.

### B3 — Multi-Zeit-Episode (Erde→Schiff→Planet) → vermutlich ERFÜLLT
- Sandbox/Arc-System (`zeitriss-core.md:1242+`) + Multi-Zeit-Sicht-Split
  (`kampagnenstruktur.md:1230+`) erlauben verschiedene Zeit-Schauplätze. Flos
  Episode (drei Zeitpunkte, eine durchgehende Bedrohung) passt strukturell.
- Kein dringender Patch; ggf. als Zukunfts-Episode-Beispiel illustrieren.

## Priorisierte Patch-Liste
1. **PK-R1 (hoch):** Rift-Horror-Pflichtgate (A3+A4+A5) in masterprompt §C —
   Horror-Tonalität Pflicht, Boss als Dread-Peak, Hölle nur angedeutet, Safety-
   Sheet-konform.
2. **PK-R2 (hoch):** Handfeste Para-Klasse (A2) in begegnungen.md — Armor + höhere
   LP, Mittelklasse für physische Kämpfe. Bestehendes Armor-Feld nutzen.
3. **PK-R3 (mittel):** Rift-Action-Frontloading (A1) — physische Begegnungen in
   Tatort/Leads, Ermittlung nebenbei.
4. **PK-R4 (klein):** Zukunfts-IA/RW-Spots (B2) — Beispiel-Ergänzung.

## Risiko-Hinweise (nicht kaputtmachen)
- One-Weird-Thing-Budget (1 Anomalie pro Rift) — Horror-Gate darf keine zweite
  Weirdness erzwingen. Horror über Atmosphäre, nicht über mehr Anomalien.
- In-sich-abgeschlossen (kein Continuity-Zwang) — bleibt.
- Bosskampf-Pflichtgate-Phasen — Horror-Rahmung ergänzt, ersetzt nicht.
- Safety Sheet (Body Horror = Veil) — Horror-Pflicht muss Veil/Line respektieren.
- Forensik-Dreieck + Rift-Fix-Objectives — bleiben.
- Difficulty-💀-Skala — neue Para-Klasse muss da sauber andocken.
