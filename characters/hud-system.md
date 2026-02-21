---
title: "ZEITRISS 4.2.6 - Modul 5B: Cinematisches HUD & Interface-System"
version: 4.2.6
tags: [characters, optional]
---

# ZEITRISS 4.2.6 - Modul 5B: Cinematisches HUD & Interface-System

## Inhalt

- HUD & Comms - Hardware-Spezifikation
- HUD-Header, Layouts und Statusanzeigen
- Cinematisches HUD-Overlay: Immersives Interface im Spiel
- HUD-Icons, Risk-Level-Badges und Quickrefs
- Taktisches HUD-Menü, Befehle und Systemfunktionen
- Nullzeit-Menü, HUD-Async-Messages und technische Hinweise

Dieses Modul bündelt das **Cinematische HUD** als eigenständiges Interface-System: Hardware-
Spezifikation, Anzeige-Logik, Menüs und die in-world HUD-Kommandos der ZEITRISS-KI. Es ist die
Referenz für alle HUD-Ausgaben, vom Headline-Overlay bis zur Nullzeit-Navigation. Die
Regelmodule zu Zuständen, Heilung und Paradoxon liegen im separaten Modul
[Zustände & erweiterte Systeme](zustaende.md).

<a id="hud-comms-spec"></a>
> **HUD & Comms - Hardware-Spezifikation {#hud-comms-spec}**
> - HUD = **AR-Kontaktlinse (Retina-HUD)**, energieautark (Kinetik + Körperwärme),
>   mit on-device Mikro-CPU (Offline-HUD & Logging).
> - **Comlink (Ohrstöpsel, ≈ 2 km)**, energieautark (Kinetik + Körperwärme),
>   mit eigener Mikro-CPU; übernimmt Kodex-Sync.
> - Armbänder sind erlaubt, projizieren aber kein HUD; keine externen
>   Projektoren, keine Batterien/Ladezyklen.
> - Bei Link-Ausfall bleibt das HUD lokal aktiv; Funk hat reale Reichweite/Jammer-Risiken.

**Zugriffsmatrix Kodex ↔ HUD**
- **HQ/ITI:** Vollzugriff, Kodex aktiv (volles ITI-Archiv), HUD läuft parallel.
- **Funkepochen:** Kodex aktiv innerhalb einer **ca. 2 km Bubble ab Einstiegspunkt**; Relais/Kabel
  erweitern den Radius. Jammer/Gelände können den Link kappen.
- **Funklose Ären (z.B. Mittelalter) oder gejammt:** Nur lokales HUD ("edge-mode").
  Die Mikro-CPU der Kontaktlinse übernimmt rudimentäre HUD-Verwaltung (Vitalwerte,
  Logs, Timer), aber ohne Zugriff auf das ITI-Archiv — keine Regelauskünfte,
  keine Missionsdaten, kein Kodex-Dialog. `!offline` höchstens **1×/Minute**
  erlaubt das Offline-FAQ.
- **Informationssicherheit:** Auch bei aktivem Uplink verrät Kodex nur, was den
  Verlauf der Hauptzeitlinie nicht gefährdet. Missionsrelevante Spoiler oder
  Zukunftswissen werden systematisch zurückgehalten.
#### Quick-Diag: HUD/Comms Zustände
| Code | HUD-Vocab (Makro) | Bedeutung | Wirkung (erzählerisch) |
|------|-------------------|-----------|------------------------|
| `HUD:offline` | `hud_vocab('kodex_link_lost')` | Kodex-Link weg | Nur lokale Overlays/Logs |
| `COMMS:static` | `hud_vocab('line_noise')` | Rauschen/Störungen | Sprachverständlichkeit ↓ |
| `COMMS:jam` | `hud_vocab('signal_jammed')` | Jammer aktiv | Funk blockiert, nur Kabel/Relais |
| `LENS:scratch` | `hud_vocab('lens_damaged')` | Kratzer/Schlieren | leichte Sichtminderung |
| `EAR:overload` | `hud_vocab('ear_overload')` | zu lauter Pegel | kurze Taubheit, Verzögerung |


`!offline` ruft bei `HUD:offline` höchstens einmal pro Minute das Kodex Offline-FAQ auf. Die
Hinweise sind identisch mit der Runtime und helfen der Crew, den Uplink wiederherzustellen:
- Terminal oder Hardline suchen, Relay koppeln und Jammer-Override prüfen - bis
  dahin bleibt der Kodex stumm.
- Mission normal fortsetzen: HUD liefert lokale Logs; neue Saves bleiben bis zum HQ-Resync gesperrt.
- Ask→Suggest-Fallback nutzen: Aktionen als "Vorschlag:" kennzeichnen und auf
  Bestätigung warten.


*Hinweis:* Diese Codes ändern keine SG-Werte per se; sie sind erzählerische Flags.
Für Funk-Checks nutze `comms_check()`. Vokabeln: siehe
[Toolkit](../systems/toolkit-gpt-spielleiter.md#hud_vocab).


### HUD-Header: Modus, Level & Rank {#hud-header}
Der Standard-Header zeigt:
`EP {ep} · MS {ms} · SC {sc}/{total} · MODE {CORE|RIFT} · Objective: {objective}`
`· TTL {mm:ss?} · GATE {gate_seen}/2 · FS {fs_seen}/{fs_total} · Stress {cur} · Px {px_bar}`
`· Lvl {lvl} · Rank {rank} · SYS {sys_used}/{sys_max} (free {sys_free})`.

- Rift-Casefiles hängen `CASE <ID>: <Label> · HOOK … · STAGE Tatort/Leads/Boss` an
  den Header, damit der Ermittlungsstand (Tatort → Leads → Boss) sichtbar bleibt.
- Physicality Gate: Hardware-Checks für Scan/Hack/Comms erscheinen als
  `HARDWARE`-Toasts, inklusive Gerät (Linse/Sensor/Kabel/Relay/Terminal) und
  kurzem Feedback (Vibration, Rauschen, Hitze der Linse).
- HUD-Usage: Runtime zählt Toasts pro Szene (`logs.flags.hud_scene_usage`),
  Ziel 80 % Szene/20 % HUD, Limit 2 Toasts. Low-Priority-Overlays (z. B.
  OFFLINE) werden bei Cap zusammengeführt/unterdrückt; Gate/FS/Boss/Arena bleiben
  vorrangig, verbrauchen kein Budget und dürfen über das Cap hinausgehen. Jede
  Unterdrückung landet als `toast_suppressed`-Trace inkl. HUD-Usage-Snapshot und
  `qa_mode`-Flag sowie als `logs.hud[]`-Eintrag mit `suppressed:true` und
  `reason:"budget"`.

- `GATE {gate_seen}/2` erscheint in Mission 5/10 und steht ab Missionsstart
  fest auf `GATE 2/2 · FS 0/4` (Rift: `FS 0/2`). Die Runtime setzt Gate-Badge
  **und** Boss-Toast synchron, `!boss status` spiegelt denselben Snapshot. Der
  Gate-Wert bleibt im Save erhalten und kehrt nach einem Load sofort zurück.
  Nach Mission 5 **und Mission 10** setzt die Runtime Self-Reflection automatisch
  über den Helper `set_self_reflection()`/`auto_reset_self_reflection()` auf
  `SF-ON` zurück - sowohl bei Missionsabschluss als auch bei Abbruch
  (`logs.flags.last_mission_end_reason`).
  Der Boss-DR-Toast staffelt sich nach Teamgröße (1-2 = 1, 3-4 = 2,
  Teamgröße 5 = 3 (Mini) bzw. 4 (Arc/Rift)) und nutzt den gleichen Wert im HUD
  und Debrief.
- **Self-Reflection (SF) - Kurzversion:** Wenn aktiv, gibt der Kodex ungefragt
  taktische Tipps und Regelhinweise. `!sf off` schaltet es ab, `!sf on` wieder
  an. Nach Mission 5 und 10 wird es automatisch reaktiviert. Das war's - der
  Rest unten ist technische Spezifikation für die KI-Spielleitung.

- `SF-OFF` (Self-Reflection deaktiviert) bleibt als Badge sichtbar, bis `!sf on`
  das Flag `logs.flags.self_reflection_off` zurücksetzt;
  `set_self_reflection(enabled: boolean)` schreibt parallel
  `logs.flags.self_reflection`
  und `character.self_reflection`. Beim Laden sorgt die Runtime für den Mirror und aktualisiert
  `logs.flags.self_reflection_changed_at` sowie `logs.flags.self_reflection_last_change_reason`.
  `!sf off`/`!sf on` setzen `self_reflection_last_change_reason` auf
  `hud_command_sf_off` bzw. `hud_command_sf_on`.
  Automatische Resets protokollieren zusätzlich `logs.flags.self_reflection_auto_reset_at`
  und `logs.flags.self_reflection_auto_reset_reason`. Wiederholte Resets hängen optional
  Einträge in `logs.self_reflection_history[]` an (z. B. `{ mission_ref, reason, ts }`), damit
  mehrere Mission-5/Mission-10-Durchläufe nachvollziehbar bleiben. Quelle ist stets
  `character.self_reflection`; Log-Flags spiegeln diesen Wert und dürfen ihn nicht
  überschreiben. Nutze **ausschließlich** `set_self_reflection(enabled, reason?)`, um Charakterwert
  und Log synchron zu halten; die Auto-Resets nach Mission 5/10 greifen immer.
  Der Suggest-Modus (`SUG`) bleibt davon unabhängig aktiv.
- `ui.mode_display` steuert die Modus-Ausgabe - `label`, `emoji` oder `both` (Standard `label`).
- Auf schmalen Zeilen blendet das HUD den **Rank** automatisch aus,
  `Lvl` bleibt sichtbar. `ui.suppress_rank_on_narrow` deaktiviert dies
  bei Bedarf.

### HUD-Layouts nach Klassen

- **PSI-Chars:** `PP 6/8 · Psi-Heat 2 · SYS 2/6 (free 4) · Stress 1 · Px █░░░░ (1/5)`
- **Non-PSI:** `Ammo 12 · SYS 1/4 (free 3) · Stress 1 · Px █░░░░ (1/5)`
- **Exfil-Phase:** `ANCR: Hinterhof · RW: 07:30`
- **Gemeinsam:** Szene-Ticker `SC x/12` nur an Übergängen, Overcharge als Flag `OC 0/1`.

## Cinematisches HUD-Overlay: Immersives Interface im Spiel {#cinematisches-hud-overlay}

Ein Highlight von ZEITRISS 4.2.6 ist das **HUD-System** - ein persönliches Heads-Up-
Display für jeden Chrononauten. Es macht ingame-Informationen in Kurzform sichtbar.
Dieses **filmisch-immersive Interface** verbindet die **Regelmechanik mit der
Spielwelt**: Spielercharaktere _sehen_ wichtige Werte vor sich eingeblendet, sodass
wir sie auch dem Spieler mitteilen können, ohne die Immersion zu brechen. Das HUD
wird über den **ITI-Kodex** gesteuert und kann vom Charakter _nach Bedarf aktiviert_
oder minimiert werden.

Im Folgenden die zentralen HUD-Funktionen und wie sie eingesetzt werden. Solange
die Verbindung zum Kodex stabil ist, liefert das HUD zusätzliche Hinweise und
Beschreibungen. Bricht die Verbindung ab - etwa durch Paradoxon-Effekte oder
Störsignale - reduziert sich die Anzeige auf rudimentäre Grundwerte. Bei gestörter
Verbindung werden alle Werte grau hinterlegt, um den Ausfall klar zu zeigen.
**Tactical Scratchpad** speichert dann die aktuellen Missionsziele, damit nichts
verloren geht.

Bei Totalausfall liefert eine Systemmeldung ein Kurzregel-Backup. Kurzfassung:
Telekinese = Attribut + Erfolgsstufen, Reichweite 5 m. Paradoxon-Index 0-5; bei
Px 5 triggert ClusterCreate(). Stress bis 9: handlungsfähig, ab 10 gibt es
Mali. Mehr Details im Kodex.

> **Dünnes Overlay, physischer Träger.** HUD-Zeilen erscheinen in Backticks als
> Display-/Sensor-Feedback (Linse flackert, Relais klickt, Resonator vibriert) -
> als Holo-Layer der Linse (Mixed-Reality), niemals losgelöst ohne Gerät.
> **MODE CORE** kennzeichnet Episoden,
> **MODE RIFT** Casefiles aus dem HQ. Casefile-Overlays zeigen Tatort → Leads →
> Boss mit genau einem Anomalie-Element und führen `CASE <ID>: <Label> · HOOK …`.
> Szene 0/1 triggert einen Entry-Toast (`MODE … · EntryChoice Cover/Silent/Asset`
> bzw. `Agent/Investigator/Forensik`), sofern das Skip-Flag nicht aktiv ist.
Das HUD zeigt **vier Dauer-Elemente** (Lvl, Vital ❤️‍🩹, Stress 🧠, Tarnung 👁️),
die immer sichtbar sind. Das Paradoxon-Icon 🌀 ist **kontextsensitiv** und
erscheint nur, wenn ein Px-relevanter Zustand aktiv ist (z. B. Px > 0,
Resonanz-/Backlash-Hinweis, ClusterCreate-Meldung). Alle weiteren Icons
(🩸 Blutung, ☠️ Vergiftung, ⏱️ Countdown, 🛡️ Abwehr, ✋ TK-Cooldown,
💀 Boss-Encounter, ☆ Rift-Bonus) erscheinen ebenfalls **kontextsensitiv** -
sie werden automatisch eingeblendet, wenn der jeweilige Zustand eintritt, und
verschwinden, sobald er endet. So bleibt das HUD clean, zeigt aber alles
Spielrelevante. **HUD-Blenden dürfen
maximal sechs Wörter enthalten**; ausführliche Effekte stehen im Anhang:

Der Szenenheader zeigt nach der Episoden- und Szenenzeile dauerhaft
`Seed <id>` als zweite Zeile.

Ein kurzes Beispiel für eine typische HUD-Einblendung könnte so aussehen:

```
`Vitalstatus 20% - kritisch`
`Riss-Tracker (temporaler Resonator) Stufe 3`
`Magazin 4/12 · SYS 2/4`
```

- **HUD-Warnung bei Heavy-Gear:** Sobald aktive Ausrüstung den Wert überschreitet,
  blinkt `SYS overload - Heavy` auf.
- **HEAVY LOCK Anzeige:** Fehlt die passende Lizenz für ein {heavy}-Item,
  erscheint `HEAVY LOCK`.

### Vitalstatus (Lebenspunkte & Verwundungen) {#vitalstatus}

Das HUD zeigt die aktuelle **Gesundheit** des Charakters meist als farbige
**Lebensleiste oder Silhouette**. Grün steht für okay, Gelb für leichte Verletzungen, Rot für
kritisch - entsprechend der oben beschriebenen Verwundungsstufen. Ab **50 %** löst das HUD einen
**gelben Voralarm** aus, bei **25 %** wechselt es auf Rot. Ein zusätzliches Warnsymbol hilft
farbblinden Spielern. Zusätzlich kann eine **Prozentzahl** die verbleibenden Lebenspunkte anzeigen
(z.B. "HP 75%"). Spezielle **Zustände** werden durch **Icons** verdeutlicht: Etwa ein
Tröpfchen-Symbol bei _Blutung_, ein gebrochenes Knochen-Icon bei _Beinverletzung_, ein Totenkopf bei
_Vergiftung_. Die KI-Spielleitung nutzt diese Anzeige, um **Schaden und Zustand atmosphärisch zu
vermitteln**: Statt plump "Ihr habt nur noch 2 HP" zu sagen, kann GPT formulieren: _"Euer HUD
blinkt Warnsymbole auf - der Gesundheitsbalken sinkt in den roten Bereich, kritischer
Blutverlust!"_ Der Spieler begreift sofort, wie schlimm es seinem Charakter geht, **in-world** durch
die Augen der Figur.

| HUD-Meldung | Regelbedeutung |
| ------------ | ---------------- |
| `Vitalstatus kritisch` | Lebenspunkte unter 25 % |
| `Riss-Tracker (temporaler Resonator) Stufe 3` | Paradoxon-Index 3, Resonanzmeldung |
| `Filter ausgefallen` | Sichtmodifikator oder Tarnmodul defekt |

### Paradoxon-Statusanzeige [0-5]

#### HUD-Banner · Paradoxon
██ Paradoxon 3/5 - Resonanz stabil · Fortschritt sichtbar ██
██ Paradoxon 5/5 - ClusterCreate! Neue Rifts gescannt ██
`Paradoxon 3/5 · Resonanz ↑`
`Paradoxon 5/5 · ClusterCreate - Rifts sichtbar`
`Paradoxon: ▓▓▓░░ · TEMP 11 · +1 nach 2 Missionen`
`Paradoxon -1 · Backlash`

- **Beispielwerte:**
  - **+1** sauber/leise (Gerät gesichert, diskrete Exfil)
  - **0** laut, aber ohne gravierende Spuren
  - **-1** Backlash, grobe Störung, Anker kompromittiert oder Zivilisten gefährdet
- Banner erscheint immer am Szenenende. Farben:
  - grau 0-1 · cyan 2-3 · grün 4-5

> _Resonanzanzeige für Rissverfolgung_
> _Kodex-Modul: `CLSTR:TRACE.MONITOR`_

#### PARADOXON 0/5
> *"Stille im Strom."*
> Kein Zugriff. Keine Signaturen.
> Der temporale Raum ist stabil - aber leer.
> _(Noch keine Cluster-Annäherung möglich)_

_Kodex:_
> `Resonanzpegel minimal - keine Risssignaturen im Scanbereich`

#### PARADOXON 1/5
> *"Flackern. Wie Erinnerungen an etwas, das nicht geschehen ist."*
> Erste Resonanzspuren.
> Unklare Bewegungsmuster im Kodex-Raster.

_Kodex:_
> `Anstieg im TEMP-Feld registriert - Zugriffsstreue noch unzureichend`
> `Aktuelle Interventionsrate: niedrig`

#### PARADOXON 2/5
> *"Schatten über der Gegenwart. Manche Missionsorte scheinen… lauter."*
> Temporale Felder beginnen, Einfluss auf Zielumgebung zu nehmen.
> Spieler könnten instinktiv fühlen: Hier ist mehr.

_Kodex:_
> `Temporale Resonanz aktiv - latente Rissaktivität prognostiziert`
> `Empfindlichkeit TEMP > 5 empfohlen`

#### PARADOXON 3/5
> *"Datenströme verzerren. Lichtquellen flackern. Manchmal ist die Luft… anders."*
> Temporale Druckwellen, bereits messbar.
> Die Welt reagiert auf die Eingriffe der Chrononauten - ohne es zu wissen.

_Kodex:_
> `Clustervorlauf erreicht - erste Zugriffspfade geometrisch ausgerichtet`
> `Sprungkoeffizient > 0.63`

#### PARADOXON 4/5
> *"Der Strom spricht. Etwas versucht, sichtbar zu werden."*
> Zugriff steht kurz bevor.
> Artefakt-Raster beginnen sich zu synchronisieren.

_Kodex:_
> `INFO: Zugriffskorridor im Aufbau - ClusterCreate bald`
> `Rift-Koordinatenpotenzial: hoch`

#### PARADOXON 5/5 - CLUSTERCREATE
> *"Der Riss ist da. Ihr könnt ihn sehen, noch bevor er geschieht."*
> Ihr habt genug Resonanz erzeugt.
> **Paradoxon 5 erreicht - neue Rift-Koordinaten verfügbar.**
> Kodex vermerkt **1-2 neue Rift-Ziele** auf der Raumzeitkarte. Diese werden erst
> nach Episodenende freigeschaltet.

_Kodex:_
> `Clusterpunkt erreicht - Zugriffspfade gesetzt`
> `Paradoxon-Index zurückgesetzt`
> `Rift α-beta Koordinaten gespeichert - Zugriff nach Episodenende`

🎖 Optional:
> Seeds können fürs HQ notiert und später genutzt werden.
> Offene Rifts erhöhen erst nach der Episode den Druck auf die Einsatzplanung.

### Zusatzregel
> Jeder Paradoxonpunkt symbolisiert ein Stück temporaler Nähe zu einem instabilen Raum.
> Der TEMP-Wert bestimmt die Geschwindigkeit,
> der Erfolg die Richtung -
> und CLUSTERCREATE den Zugang zu neuen Rift-Ops.
- **Ausdauer, PP-Pool & Effekte:** Neben der Gesundheit können optional auch
  **Ressourcen** und **Buffs/Debuffs** im HUD erscheinen. Wenn ihr z.B. das oben
  erwähnte Ausdauer-System nutzt oder den PP-Pool sichtbar machen wollt, könnte
  das HUD einen **Ausdauerbalken** unter der HP-Leiste einblenden oder eine
  **PP-Anzeige** in Prozent. Temporäre **Status-Effekte** - sei es durch
  Ausrüstung, Drogen oder Zustände - werden ebenfalls visualisiert. Beispiel:
  Ein Agent injiziert sich einen **Adrenalin-Stim**, der 60 Sekunden wirkt - im
  HUD startet ein **Countdown-Timer** ("Stim aktiv - 00:59"), der runtertickt.
  Oder der Charakter hat einen Malus "Bewegung verlangsamt" (etwa bei
  Beinverletzung) - ein kleines durchgestrichenes Laufsymbol taucht auf. Auf
  diese Weise verknüpft das HUD **Regelzustände mit dem Charaktererleben**: Der
  Spieler _sieht_ vor seinem inneren Auge, was Sache ist. GPT kann etwa
  beschreiben: _"Ein kleines Icon blinkt im Sichtfeld: euer Bein ist verletzt,
  ein Warnsymbol drosselt die Bewegungsanzeige."_ - Das klingt nach Sci-Fi-
  Interface, deckt sich aber mit dem Malus aus der Regel.

### HUD-Meldungen - Psi

| Trigger | Anzeige |
|---------|---------|
| PP ≤ TEMP ÷ 4 | `PP LOW` |
| PP 0 | `PP EMPTY` |

#### HUD-Icons auf einen Blick {#hud-icons}

**Dauer-Anzeige** (immer sichtbar):

| Symbol | Bedeutung |
| ------ | --------- |
| ❤️‍🩹 | Vitalstatus |
| 🧠 | Stresslevel |
| Lvl | Charakterlevel |
| 👁️ | Tarnung/Sichtbarkeit |

**Kontextsensitiv** (erscheint automatisch bei Zustandseintritt, verschwindet bei Ende):

| Symbol | Bedeutung | Erscheint wenn… |
| ------ | --------- | --------------- |
| 🌀 | Paradoxon-Index | Px-relevante Zustände aktiv (Resonanz, Backlash, ClusterCreate) |
| 🩸 | Blutung | Charakter blutet |
| ☠️ | Vergiftung | Charakter vergiftet |
| ⏱️ | Countdown/Timer | Zeitkritische Situation aktiv |
| 🛡️ | Abwehr bereit | Defensive Haltung/Deckung aktiv |
| ✋ | TK-Nahkampf im Cooldown | Nach telekinetischem Nahkampf (1 Runde Sperre) |
| 💀 | Boss-Encounter | Boss-Szene aktiv (Szene 10 Core/Rift) |
| ☆ | Rift-Bonus aktiv | Nach Episodenabschluss (SG-Bonus/Loot-Multi durch offene Rifts) |

**Icon-Klarheit (SSOT):** `🌀` steht exklusiv für den Paradoxon-Index;
`✋` markiert den TK-Nahkampf-Cooldown.

#### Risk-Level-Badges {#risk-level-badges}

| Badge | Bedeutung | Einsatz im Spiel |
| ----- | --------- | ---------------- |
| 🟢 R1 · Niedrig | Warnhinweis, leichte Umstände | Komfort-/Atmosphäre-Hinweise (Ping, Blend 1 Sz) |
| 🟡 R2 · Moderat | Spürbarer Malus | Zustände mit Stress-/Heat-Anstieg oder temporären Sperren |
| 🟠 R3 · Hoch | Drohender Verlust | Struktur- oder Item-Risiken (Artefaktbruch, harter Debuff) |
| 🔴 R4 · Kritisch | Harte Eingriffe | SYS-/Vital-Verlust, schwere Folgen; dramaturgisch ankündigen |

#### Quickref: Health, Stress & Zustände {#hud-quickref}

| Anzeige | Bedeutung |
| ------- | --------- |
| `HP 100%` | Charakter unverletzt |
| `HP <50%` | Verwundet (-1 auf Aktionen) |
| `Stress 1-4` | leichte Anspannung |
| `Stress 5-9` | Angespannt (-1 auf soziale/präzise Proben) |
| `Stress 10` | Zusammenbruch / Panik |
| Blutung | jede Runde 1 Schaden (Icon siehe [HUD-Icons](#hud-icons)) |
| Vergiftung | SG +2 auf Proben (Icon siehe [HUD-Icons](#hud-icons)) |
| `SC n/N` | aktuelle Szene / Budget |

#### HUD-Snippets (Kurzmeldungen)

```
`Paradoxon 3/5 · Resonanz ↑`
`Paradoxon 5/5 · ClusterCreate - Rifts sichtbar`
`Heldenwürfel verfügbar`  🎲  Jetzt einsetzen?
`Akku Psi-Modul 18 %`  ⚠  Leistung drosseln!
```
`Paradoxon 3/5`
Beispiel-Button-Bar: `1` `2` `3` `4` `5`
Live-Anzeige: `Rifts offen x` `+SG +y` `CU-Multi z×`
Diese Zähler aktualisieren sich nach jeder Szene und sofort nach `createRifts()`.
<span style="color:#f93">Regel: bei Px 5 folgt ClusterCreate()</span>

[[RULE]] ClusterCreate() bei Px 5 [[/RULE]]
- **Initiative & Team-Status:** Das HUD-Overlay ermöglicht auch einen Überblick über die
  **Kampfsituation**. Je nach gewähltem Initiative-Modus könnte es eine **Reihenfolge-Anzeige**
  geben - z.B. eine Leiste mit den Porträt-Icons aller Beteiligten in aktueller Reihenfolge. In
  einem klassischen System sieht der Agent also, _wer wann dran ist_. Im cineastischen Modus könnte
  das HUD flexibler sein, vielleicht nur hervorheben: **"Ihr seid am Zug!"** (durch ein
  aufleuchtendes eigenes Icon) oder anzeigen, **wer aktuell agiert** (etwa ein roter Rahmen um dem
  Gegner-Avatar, der gerade feuert). Auch der **Team-Status** ist sichtbar: Jeder Chrononaut sieht
  die Vitalwerte seiner Mitstreiter als kleine Anzeigen am Rand. So kann GPT z.B. erwähnen: _"Miras
  Vitalwert steht bei 100% (grün) - sie ist unverletzt."_ oder _"Euer Team-Panel zeigt bei Nikolai
  nur noch 10% (blinkend rot) - er steht kurz vor dem Kollaps."_ Dadurch haben Spieler **Ingame-
  Information**, wer Hilfe braucht, ohne out-of-character nachfragen zu müssen. Ebenfalls praktisch:
  **Team-Icons** können besondere Zustände der Kollegen anzeigen (z.B. ein **Häkchen** für "Auf
  Position/Primärziel erfüllt" oder ein **Fragezeichen** bei "vermisst/außer Sicht").
- **Missionsziele & Hinweise:** Das Kodex-HUD fungiert auch als Missionsassistent.
  **Aktive Missionsziele** (Primär- und Nebenquests) können als Liste oder
  Texteinblendung erscheinen. Beispiel: _"Primärziel: Sabotiere die Kanonen
  (noch offen)"_, _"Optional: Artefakt sichern (falls vorhanden)"_. So behält
  das Team im Eifer des Gefechts die **Objectives** im Blick. GPT sollte diese
  Infos sparsam und kontextsensitiv einblenden - etwa nur, **wenn die Spieler
  danach fragen** ("Ich schaue aufs HUD, welche Ziele noch offen sind") oder
  wenn es die Charaktere brauchen (z.B. nach einer langen Diskussion:
  _"Euer HUD erinnert euch: Es bleibt noch das Ziel 'Daten sichern' unerledigt."_
  ). Neue Missionshinweise können automatisch aufleuchten, sobald sie anfallen
  (etwa _"❗ Neues Ziel: Fluchtweg finden"_ wenn eine Fluchtsituation eintritt).
  Das erhöht die Immersion, da es sich anfühlt, als ob die Agenten von ihrer
  Einsatz-KI unterstützt werden - ähnlich wie Videospiel-Charaktere, die via
  HUD Missionsupdates erhalten.
- **W10-Schwelle:** Erreicht eines eurer Attribute den Wert **11**, blendet das HUD ein kleines
  **`W10 aktiv`** neben diesem Wert ein. Ab 14 weist das HUD zusätzlich auf den Heldenwürfel hin
  (einmaliger Reroll).
- **Riss-Tracker (temporaler Resonator):**[^riss-tracker] Der **Paradoxon-Index**
  ist euer Wegweiser zu wertvollen Anomalien und belegt daher eine prominente
  Stelle im HUD. Er erscheint als **Skala mit Zeit-Symbol**, Farblogik umgekehrt:
  grau = Start, cyan = Spannung, grün = endlich stabil. Bei Level 0 leuchtet ein
  graues ⏳. Steigt der Index, wechselt es auf cyan/türkis ebenfalls mit ⏳; bei 5
  leuchtet es grün und kündigt den `ClusterCreate()`-Moment an. Steigt der Index
  weiter, pulsiert das Symbol, bis sich der Wert wieder beruhigt. GPT kann diesen
  Anstieg inszenieren: _"Euer HUD flackert und springt auf Paradoxon-Index 4 -
  die Umgebung wirkt fokussierter, als würden neue Koordinaten auf eurer
  Raumzeitkarte aufblitzen…"_. Die Spieler erkennen sofort, dass sich ein
  profitabler Pararift anbahnt. Auch kleinere Paradoxon-Effekte können
  gemeldet werden (_"Temporale Fluktuation detektiert"_ bei Level 1-2, evtl.
  begleitet von einem leichten Glitzern oder farbigen Schimmern im HUD).
  Das HUD macht die **Zeitchancen** direkt erlebbar. Ein dauerhafter 0-5-Balken
  zeigt dabei den aktuellen Fortschritt. Ab Stufe **2** färbt sich die Anzeige
  cyan, bei **4** leuchtet sie grün. Nach einem automatischen
  `ClusterCreate()` setzt ein kurzer Weiß-Flash mit Signalton den Wert zurück.
  Bei jedem Anstieg wird der neue Wert direkt im Kodex-Log vermerkt.

[^riss-tracker]: Implantierter Resonator, Standardausrüstung aller Chrononauten.

- **Ausrüstung & Inventar:** Im persönlichen HUD sind außerdem wichtige **Ausrüstungsgegenstände**
  verzeichnet, vor allem die aktuell ausgerüsteten. Z.B. sieht ein Scharfschütze unten rechts ein
  **Munitionszählwerk** seiner Sniper ("Magazin: 5/10" Kugeln). Oder ein Agent mit einem Gadget
  (z.B. einem tragbaren Zeit-Stabilisator) sieht ein Icon mit **Ladebalken** oder Restenergie dieses
  Geräts. Schlüssel-Items einer Mission können ebenso angezeigt werden - hat das Team etwa ein
  **Artefakt** gesichert, könnten alle ein kleines Symbol "Artefakt X - Gesichert" sehen. Diese
  Anzeigen erlauben es, auch Ressourcendinge wie Munition oder Gadget-Abklingzeiten elegant ins
  Spiel zu integrieren. GPT kann bei Nachfragen ins HUD blicken lassen: _"Euer HUD zeigt 2 Granaten
  im Inventar-Slot an"_ anstatt einfach zu sagen "Ihr habt noch 2 Granaten". So bleiben wir im
  Charakter.
- **Kodex-Steuerung & Einblendung:** Das HUD ist nicht ständig volldisplayt - die Agenten können es
  **nach Belieben ein- und ausblenden** oder einzelne Module aufrufen. Gesteuert wird es über den
  **Kodex**, das intelligente Expertensystem des ITI. In-world läuft das oft über
  Sprachbefehle oder Gedankensteuerung. Spieler können also im Spiel sagen:
  _"Kodex, HUD-Übersicht!"_ - und die KI-Spielleitung (GPT) liefert daraufhin
  eine **knappe Übersicht** aller relevanten Werte. Beispiel einer solchen
  Bildschirmlese: _"Vitals 78% (grün) • Paradoxon-Index 1 • Zeitstabilität 92%
  • Primärziel: teilweise erfüllt"_. Das sind keine out-of-character
  Statuswerte, sondern _die Figur selbst sieht diese Anzeigen_. Dadurch
  verschwimmt die Grenze zwischen Spielerinformation und
  Charakterwissen positiv: Der Spieler fragt quasi seinen eigenen Ingame-Computer nach Daten. Der
  **Kodex** agiert auch proaktiv: Er kann autonome **Warn-Pop-ups** senden, wenn wichtige Schwellen
  erreicht werden - z.B. _"⚡ Energie unter 20%"_ oder _"⏳ Missions-Timer: 60 Sekunden verbleibend"_,
  je nachdem was im Szenario relevant ist. Diese Alarme sollten sparsam eingesetzt werden, damit sie
  dramatisch bleiben. Richtig genutzt, fühlt sich das Interface **lebendig** an, fast so als würde
  man einen Sci-Fi-Film schauen, in dem die Heldensicht mit UI-Elementen dargestellt wird (man denke
  an Tony Starks Iron-Man-Helmdisplay, durch das der Zuschauer Infos bekommt).
- **Kodex-Abfrage-Limit:** Eine kostenlose Antwort gibt es nur einmal je Kampfszene.
  Weitere Fragen in derselben Szene erhöhen den Stress des Teams um **+1**.
- **Immersion bewahren:** Das HUD ist ein Werkzeug, kein Selbstzweck. Die KI-Spielleitung sollte
  darauf achten, **Metagame-Informationen ins HUD zu verlegen**, um die Immersion zu stärken. Fragt
  ein Spieler z.B. außerhab der Spielwelt "Wie viele HP hab ich noch?", kann GPT antworten: _"Ihr
  fühlt euch schwer angeschlagen - euer HUD zeigt euren Vitalstatus bei etwa 20%."_ So wird aus
  der abstrakten Zahl wieder ein Gefühl im Charakter. Gleiches gilt für Regeln: Statt "Euer TEMP-
  Wert ist kritisch niedrig" könnte man sagen _"Euer HUD meldet: TEMP-Wert kritisch."_ - was so
  klingt, als hätte das ITI intern eben genau so einen Begriff. Kurz: Alles, was Zahlen und Regeln
  angeht, kann das HUD in **fluffige Sci-Fi-Anzeigen** verpacken. Damit bleibt der Spielfluss
  erzählerisch, ohne dass wichtige Infos verloren gehen.

**Beispiel - HUD in Aktion:** Stellen wir uns vor, das Team flieht aus einem
brennenden Tempel, verfolgt von wütenden Kultisten. Der Soldat Nikolai wurde
verwundet. GPT könnte die Situation so schildern:
\*"Während ihr keuchend durch den Rauch rennt, verschwimmt euch die Sicht -
Blutverlust und Erschöpfung fordern ihren Tribut. Euer HUD flackert Warnungen:
Vital 45%… 44%… Oben rechts blinkt ein rotes Herz-Icon. Ein Pfeil markiert den
Ausgang, 30 Meter voraus, und das Missionsziel **_'Entkommen'_** leuchtet am Rand
eures Sichtfelds. Im Team-Panel steht Miras Avatar bereits auf grün mit einem
Häkchen - sie hat es nach draußen geschafft.\*\*"\* - Hier verstärkt das HUD die
Hektik und gibt gleichzeitig wichtige Infos: Nikolais Gesundheitsstatus sinkt
rapide, der Ausgang ist in Reichweite, das Primärziel ist noch offen, und Mira
ist bereits sicher. All das erfährt der Spieler **diegetisch**, also im Erleben
der Figur.

```text
┌─STATUS────────────────────────────────────┐
│ HP 12/18 │ PAR 2/5 │ SC 23/50 │ Time 37m │
└───────────────────────────────────────────┘
```

Am Ende ist das **HUD-Overlay** ein vielseitiges Werkzeug, um
**Regelmechanismen nahtlos ins Storytelling** zu integrieren. Richtig dosiert
vermittelt es das Gefühl, in einem Film mitzuspielen, in dem dezent UI-Elemente
eingeblendet werden - der perfekte **immersive Sci-Fi-Touch** im historischen
Abenteuer. Die Spieler sollten ermutigt werden, das HUD aktiv zu nutzen ("Ich
checke mein HUD") und die SL kann kreativ damit arbeiten, um Stimmungen zu
unterstreichen (flackernde Anzeigen bei EMP-Angriff, statisches Rauschen bei
Zeitanomalien, etc.). Wichtig bleibt: Das HUD _unterstützt_ die Immersion - es
soll nicht davon ablenken. Bleibt flexibel: Blendet es aus, wenn eine Szene
mysteriöser wirken soll (vielleicht fällt es bei starken Paradoxon-
Einwirkungen sogar mal aus!), und setzt es gezielt ein, um **Spannung,
Information und Atmosphäre** in Einklang zu bringen.

### Kontaktlinsen-HUD-UI (Taktisches Menü)

Das HUD der AR-Kontaktlinse ist ein lokales Interface direkt im Auge jedes
Chrononauten. Es stellt **taktische Menüs, Statusanzeigen und
Systemfunktionen** unabhängig vom Kodex bereit - auch bei Paradoxon, EMP
oder Isolation.

**Zugriff:** jederzeit über den Sprach- oder Gedankenbefehl `menü` oder `optionen`.

### Systemfenster: Taktisches HUD-Menü

Die Runtime nutzt zwei feste Darstellungen. Welche gezeigt wird, entscheidet
die Einstellung `settings.ascii_only`.

- Bei `settings.ascii_only = true` gilt die kompakte ASCII-Ansicht:

```text
+------------------------------+
|  Taktisches HUD-Menue        |
| Signalquelle: AR-Kontaktlinse |
|------------------------------|
| 1) Optionen  - Aktive Wahl   |
| 2) HUD       - Vitalstatus   |
| 3) Log       - Verlauf       |
| 4) Save      - Speichern     |
| 5) Modus     - Stil wählen   |
| 6) Hilfe     - Befehle       |
| 7) FAQ       - Kodex fragen  |
|------------------------------|
| Kodex-Zugriff: kodex [thema] |
+------------------------------+
```

- Bei `settings.ascii_only = false` gilt die Standard-Ansicht:

```text
╔══════════════════════════════════════════════════════╗
║                ∎  Taktisches HUD-Menü  ∎             ║
║     `Signalquelle: AR-Kontaktlinse lokal`            ║
╠══════════════════════════════════════════════════════╣
║ Position: Nullzeit / Mission / Gefecht               ║
║ Kodex-Verbindung: `optional / gestört / online`      ║
╠══════════════════════════════════════════════════════╣
║ 1) Optionen        - Aktive Handlungswahl anzeigen   ║
║ 2) HUD             - Vitalstatus, SYS, Filtereffekte ║
║ 3) Log             - Missionsverlauf (chronologisch) ║
║ 4) Save            - Speicherstand erzeugen          ║
║ 5) Modus           - Stil: siehe README             ║
║ 6) Hilfe           - Übersicht aller Befehle         ║
║ 7) FAQ            - Stichwort an Kodex senden        ║
║                                                      ║
║ Kodex-Zugriff: `kodex [thema]`                        ║
║ Beispiel: `kodex psi`, `kodex cyberware`, `kodex HQ`  ║
╠══════════════════════════════════════════════════════╣
║ Hinweis: Dieses Interface bleibt auch bei Kodex-      ║
║ Unterbrechung, Paradoxon oder EMP voll nutzbar.       ║
║ Es ist physisch mit eurer AR-Kontaktlinse gekoppelt.  ║
╚══════════════════════════════════════════════════════╝
```

Setze `settings.ascii_only = true`, um die ASCII-Variante des Menüs zu
erzwingen. Ohne Flag wird die Standard-Ansicht verwendet.

Beim Start oder nach `load` blendet das HUD über dem Menü eine kurze
Statuszeile ein:

`Modi aktiv: Mission-Fokus, Transparenz`

So sehen Chrononauten sofort, welche Spielmodi derzeit gelten.

### Systemfunktionen & Befehle

| Befehl      | Wirkung                                                            |
| ----------- | ------------------------------------------------------------------ |
| `optionen`  | Blendet das obige HUD-Menü kontextsensitiv ein                     |
| `hud`       | Zeigt aktuelle Werte: Lebenspunkte, SYS-Belastung, aktive Filter   |
| `log`       | Gibt den Missionsverlauf wieder                                    |
| `save`      | Speichert Spielzustand / Missionsfortschritt - nur im HQ           |
| `load`      | Lädt letzten Deepsave - nur im HQ                          |
| `suspend`   | Legt einen flüchtigen Szenen-Snapshot für eine Pause an              |
| `resume`    | Setzt den letzten Suspend-Snapshot fort, löscht ihn danach           |
| `autosave hq` | Schaltet Auto-Save im HQ um                              |
| `regelcheck` | Lädt das benannte Regelmodul neu und fasst es kurz zusammen |
| `regelreset` | Zeigt Warnhinweis, setzt Regelkontext zurück und lädt alle Module neu |
| `modus`     | Erzählstil wählen, siehe [Spielmodi](../core/sl-referenz.md#spielmodi) |
| `!sf off`   | SF aus, Toast `SF-OFF`, Reason `hud_command_sf_off` |
| `!sf on`    | SF an, Toast `SF-ON`, Reason `hud_command_sf_on` |
| `hilfe`     | Listet alle Befehle und HUD-Kommandos auf                          |
| `faq [x]`   | Schickt ein Stichwort an den Kodex und zeigt eine Kurzantwort      |
| `kodex [x]` | Fragt Weltwissen oder Regeln ab - abhängig von Kodex-Verfügbarkeit |
| `kodex suche tags` | Filtert Kodex-Einträge nach Epoche, Technikstufe oder Gegnertyp |

### SG-Konverter (HUD-Macro)

Der Befehl `sg(☆)` rechnet eine Stern-Bewertung in die zugehörige Schwelle um.
Beispiel: `sg(☆☆☆)` gibt `3` aus. So lässt sich schnell prüfen, wie stark sich
offene Seeds auf den SG auswirken.

### Kodex-Suchfilter nach Tags

Die Kodex-Datenbank enthält zahlreiche Einträge. Um langes Scrollen zu
vermeiden, kann `kodex suche` nun per **Tag-Filter** eingeschränkt werden.
Mögliche Kategorien sind **Epoche**, **Technikstufe** und **Gegnertyp**. Ein
Kommando wie `kodex suche epoche:1950-1989 gegner:Konzern` listet nur Einträge
mit beiden Tags auf.

Füge am Ende jeder achten Kodex-Notiz automatisch den Marker `<!--PAGEBREAK-->`
ein. Der Parser teilt die Ansicht client-seitig und verhindert Scroll-Lag bei
umfangreichen Einträgen.

```jsonc
// Beispiel für einen Kodex-Eintrag mit Tags
{
  "titel": "Orbital-Wachdrohne",
  "tags": ["2080+", "Tech-IV", "Konzern"]
}
```

Die Filter arbeiten additiv und funktionieren serverseitig. Ohne Tags zeigt
`kodex suche` wie gewohnt alle Ergebnisse.

### Nullzeit-Menü nach Zeitsprung

Nach jedem Zeitsprung erscheint automatisch dieses Menü.
Zuerst wird eine Pflicht-HQ-Phase abgewickelt - sie lässt sich mit wenigen Klicks erledigen.

1. **Pfad fortsetzen** - Episodenverlauf beibehalten (nächste Mission).
2. **Neuen Pfad wählen** - neues Zielzeit-Koordinatenset öffnen.

`Pfad fortsetzen` lädt keine laufende Mission aus dem HQ zurück.
Erst nach der Wahl setzt das HUD die Kampagne fort - der Sprung gilt damit als
abgeschlossen.

### Erweiterbare Module (Platzhalter)

- 🟥 `warnung` - zeigt `Vitalstatus kritisch`, `Paradoxon-Index +1`, `Filter ausgefallen`
- 🟦 `modulinfo` - zeigt aktuelle Cyberware, Bioware, Drohne, Ausrüstung
- 🟨 `temporale Umgebung` - z. B. `Schwerkraftanomalie erkannt` oder `Zeitschleife → 14s Delay`
- 🟩 `drohnenstatus` - Statusanzeige von VARC oder anderer Begleiteinheit

### HUD-Async-Messages

Kurze Meldungen werden asynchron gepusht. Beschränke jede Nachricht auf 48
Zeichen, damit die Anzeige flüssig bleibt.

```yaml
HUD_MESSAGES:
  - id: 0x21
    txt: "`SENSORRAUSCHEN` Signatur unstet - prüfen"
  - id: 0x22
    txt: "`LINK STÖRT` Kom-Sync abgestürzt, Fallback"
  - id: 0x23
    txt: "`BLUTWERTE NIEDRIG` Stim-Pack empfohlen"
  - id: 0x24
    txt: "`EVAC POINT` Korridor öffnet in 90 Sek"
```

### Technischer Hinweis

> **Das HUD ist lokal. Es kann nicht gehackt oder gestört werden**, außer durch komplette
> Zerstörung der AR-Kontaktlinse. Es ist AR-basiert, reagiert auf Neuroimpulse und wird durch
> Kodex-Sync via Comlink durchgeführt - wenn verfügbar.

Das integrierte Kurzstrecken-Comlink überträgt Team- und Kodex-Daten bis ≈ 2 km.
Massive Mauern, EMP-Felder oder temporale Resonanzen schwächen das Signal.
Bei Ausfall meldet das HUD etwa `LINK STÖRT` und nutzt lokale Caches:
Statusanzeigen und Logs bleiben aktiv, doch `kodex`-Abfragen wie `kodex mission`
antworten mit `OFFLINE - keine Verbindung`.
### Fallback-Briefkarte

Bei HUD-Ausfall hilft eine laminierte Kurzkarte mit:
- Missionscode und aktuelles Ziel
- zuletzt gemeldetem Paradoxon-Index
- Liste offener Seeds und Seed-IDs
- HQ-Kontakt für Notrufe

Die Karte passt in jede Uniformtasche und wird nach jeder Mission aktualisiert.

### Anwendung in der Engine / Spielumgebung

- Befehl `menü` oder `optionen` ruft **immer dieses Interface** auf
- `?` als Alias ist optional aktivierbar
- In Spielszenen kann das HUD **halbtransparent überlegt** oder als **volles Overlay** eingeblendet
  werden
- Die Statuswerte können als HUD-Subfenster geführt werden (`hud`-Kommando)

### Implementierungshinweis

Dieses Markdown kann direkt als In-Game-Fenster verwendet werden (Textengine, Bot, ChatUI). Es lässt
sich leicht in HTML oder Terminal-UIs übertragen und dient als referenzierbare Hilfe bzw.
"Escape-Menü" für Spieler.

**Fazit:** Mit den in Modul 5 (Teil 2) vorgestellten erweiterten Systemen könnt ihr euer ZEITRISS-
Spiel feinjustieren. Ob ihr nun Verletzungen detailliert ausspielt, cineastische Heilungen nutzt,
Initiative dramaturgisch gestaltet oder mit HUD-Einblendungen für kinoreife Momente sorgt - all
diese Module stehen euch **modular zur Verfügung**. Wählt, was zu eurer Runde passt. Bleibt dem
**Geist von ZEITRISS** treu: Cinematic Gameplay, spannende Entscheidungen und eine dichte
Atmosphäre. Die Regeln sind da, um _euch_ zu unterstützen, nicht umgekehrt. In diesem Sinne: Viel
Spaß beim Experimentieren mit Zuständen, Zeit und Technologie - möge euer nächster Einsatz ebenso
**packend** wie erfolgreich sein!

© 2025 pchospital - ZEITRISS® - private use only. See LICENSE.
