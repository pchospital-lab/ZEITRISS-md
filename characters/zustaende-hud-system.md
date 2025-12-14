---
title: "ZEITRISS 4.2.3 – Modul 5: Erweiterte Systeme & Cinematisches HUD"
version: 4.2.3
tags: [characters, optional]
---

# ZEITRISS 4.2.3 – Modul 5: Erweiterte Systeme & Cinematisches HUD

## Inhalt

- Zustände und Statuseffekte
- Heilung & Erholung – klassisch, filmisch, high-tech
- Initiative-Systeme: klassisch, cineastisch oder szenisch
- Stress, Paradoxon und mentale Belastungen
- Ressourcenmodelle: Ausdauer & PP-Pool (optional)
- Besonderheiten im Zeitstrom: Unterbrechungen, Reaktionen & freie Aktionen
- Cinematisches HUD-Overlay: Immersives Interface im Spiel

In **Teil 2** der überarbeiteten Modul 5-Regeln fokussieren wir uns auf erweiterte Systeme, die Euer
ZEITRISS-Spiel noch vielseitiger und filmischer machen. Von **Zuständen** wie Verwundungen oder
Erschöpfung über **Heilung & Erholung** in verschiedenen Stilen bis hin zu alternativen
**Initiative-Systemen** und optionalen Modulen für **Stress**, **Paradoxon-Resonanz** und **mentale
Auswirkungen** – all diese Elemente könnt Ihr modular einsetzen. Abschließend integrieren wir ein
vollständig spielbares, filmisch-immersives **HUD-Overlay**, das der KI-Spielleitung (GPT)
erlaubt, Informationen wie Lebenspunkte, PP-Pool oder Initiative in-world anzuzeigen. Alle
neuen Module bleiben dem ZEITRISS-Stil treu: **atmosphärisch dicht, erzählerisch fokussiert und doch
leichtgewichtig** in der Anwendung.

<a id="hud-comms-spec"></a>
> **HUD & Comms – Hardware-Spezifikation {#hud-comms-spec}**
> - HUD = **AR-Kontaktlinse (Retina-HUD)**, energieautark (Kinetik + Körperwärme),
>   mit on-device Mikro-CPU (Offline-HUD & Logging).
> - **Comlink (Ohrstöpsel, ≈ 2 km)**, energieautark (Kinetik + Körperwärme),
>   mit eigener Mikro-CPU; übernimmt Kodex-Sync.
> - **Kein** Armband/keine externen Projektoren/keine Batterien/Ladezyklen.
> - Bei Link-Ausfall bleibt das HUD lokal aktiv; Funk hat reale Reichweite/Jammer-Risiken.

**Zugriffsmatrix Kodex ↔ HUD**
- **HQ/ITI:** Vollzugriff, Kodex aktiv, HUD läuft parallel.
- **Funkepochen:** Kodex aktiv innerhalb einer **ca. 2 km Bubble ab Einstiegspunkt**; Relais/Kabel
  erweitern den Radius. Jammer/Gelände können den Link kappen.
- **Funklose Ären (z.B. Mittelalter) oder gejammt:** Nur HUD/Logs ("codex-light"). Kodex schweigt,
  bis Hardware-Link steht. `!offline` höchstens **1×/Minute** erlaubt das Offline-FAQ.
#### Quick-Diag: HUD/Comms Zustände
| Code | HUD-Vocab (Makro) | Bedeutung | Wirkung (erzählerisch) |
|------|-------------------|-----------|------------------------|
| `HUD:offline` | `hud_vocab('kodex_link_lost')` | Kodex-Link weg, Linse lokal | Nur lokale Overlays/Logs |
| `COMMS:static` | `hud_vocab('line_noise')` | Rauschen/Störungen | Sprachverständlichkeit ↓ |
| `COMMS:jam` | `hud_vocab('signal_jammed')` | Jammer aktiv | Funk blockiert, nur Kabel/Relais |
| `LENS:scratch` | `hud_vocab('lens_damaged')` | Kratzer/Schlieren | leichte Sichtminderung |
| `EAR:overload` | `hud_vocab('ear_overload')` | zu lauter Pegel | kurze Taubheit, verzögerte Reaktion |


`!offline` ruft bei `HUD:offline` höchstens einmal pro Minute das Kodex Offline-FAQ auf. Die
Hinweise sind identisch mit der Runtime und helfen der Crew, den Uplink wiederherzustellen:
- Terminal oder Hardline suchen, Relay koppeln und Jammer-Override prüfen – bis
  dahin bleibt der Kodex stumm.
- Mission normal fortsetzen: HUD liefert lokale Logs; neue Saves bleiben bis zum HQ-Resync gesperrt.
- Ask→Suggest-Fallback nutzen: Aktionen als „Vorschlag:“ kennzeichnen und auf
  Bestätigung warten.


*Hinweis:* Diese Codes ändern keine SG-Werte per se; sie sind erzählerische Flags.
Für Funk-Checks nutze `comms_check()`. Vokabeln: siehe
[Toolkit](../systems/toolkit-gpt-spielleiter.md#hud_vocab).


### HUD-Header: Modus, Level & Rank {#hud-header}
Der Standard-Header zeigt:
`EP {ep} · MS {ms} · SC {sc}/{total} · MODE {CORE|RIFT} · Objective: {objective}`
`· TTL {mm:ss?} · GATE {gate_seen}/2 · FS {fs_seen}/{fs_total} · Stress {cur} · Px {px_bar}`
`· Lvl {lvl} · Rank {rank} · SYS {sys_used}/{sys_max} (free {sys_free})`.

- `GATE {gate_seen}/2` erscheint in Mission 5/10 und steht ab Missionsstart
  fest auf `GATE 2/2 · FS 0/4` (Rift: `FS 0/2`). Die Runtime setzt Gate-Badge
  **und** Boss-Toast synchron, `!boss status` spiegelt denselben Snapshot. Der
  Gate-Wert bleibt im Save erhalten und kehrt nach einem Load sofort zurück;
  Mission-5-Tests verlangen explizit den sichtbaren Badge. Nach Mission 5 setzt
  die Runtime Self-Reflection automatisch auf `SF-ON` zurück – sowohl bei
  Missionsabschluss als auch bei Abbruch (`logs.flags.last_mission_end_reason`).
  Der Boss-DR-Toast staffelt sich nach Teamgröße (Solo/Duo = 1, 3–4 = 2, 5–6 =
  3/4 optional) und nutzt den gleichen Wert im HUD und Debrief.
- `SF-OFF` (Self-Reflection deaktiviert) bleibt als Badge sichtbar, bis `!sf on` das Flag `logs.flags.self_reflection_off`
  zurücksetzt; `set_self_reflection(enabled: boolean)` schreibt parallel `logs.flags.self_reflection`
  und `character.self_reflection`. Beim Laden sorgt die Runtime für den Mirror und aktualisiert
  `logs.flags.self_reflection_changed_at` sowie `logs.flags.self_reflection_last_change_reason`.
  Automatische Resets protokollieren zusätzlich `logs.flags.self_reflection_auto_reset_at`
  und `logs.flags.self_reflection_auto_reset_reason`. Wiederholte Resets hängen optional
  Einträge in `logs.self_reflection_history[]` an (z. B. `{ mission_ref, reason, ts }`), damit
  mehrere Mission‑5-Durchläufe nachvollziehbar bleiben. Quelle ist stets
  `character.self_reflection`; Log-Flags spiegeln diesen Wert und dürfen ihn nicht
  überschreiben. Nutze `set_self_reflection(enabled, reason?)`, um Charakterwert
  und Log synchron zu halten; der Auto-Reset nach Mission 5 greift immer. Der
  Suggest-Modus (`SUG`) bleibt davon unabhängig aktiv.
- `ui.mode_display` steuert die Modus-Ausgabe – `label`, `emoji` oder `both` (Standard `label`).
- Auf schmalen Zeilen blendet das HUD den **Rank** automatisch aus,
  `Lvl` bleibt sichtbar. `ui.suppress_rank_on_narrow` deaktiviert dies
  bei Bedarf.

### HUD-Layouts nach Klassen

- **PSI-Chars:** `PP 6/8 · Psi-Heat 2 · SYS 2/6 (free 4) · Stress 1 · Px █░░░░ (1/5)`
- **Non-PSI:** `Ammo 12 · SYS 1/4 (free 3) · Stress 1 · Px █░░░░ (1/5)`
- **Exfil-Phase:** `ANCR: Hinterhof · RW: 07:30`
- **Gemeinsam:** Szene-Ticker `SC x/12` nur an Übergängen, Overcharge als Flag `OC 0/1`.

## Zustände und Statuseffekte

Charaktere in ZEITRISS können von verschiedenen **Zuständen** betroffen sein – seien es physische
Verletzungen, Erschöpfung, temporale **Destabilisierung** oder psychische **Traumata**. Solche
Zustände wirken sich sowohl erzählerisch als auch regeltechnisch aus. Hier die wichtigsten Zustände
im Überblick:

- **Verwundungsstufen:** ZEITRISS nutzt ein **stufenbasiertes Verletzungssystem (5 Schweregrade)**,
  um Wunden cineastisch abzubilden. Jede Stufe hat typische Symptome und **Mali**, die die
  Leistungsfähigkeit beeinträchtigen, sowie entsprechende Erholungszeiten:

  - **Unverletzt:** Keine nennenswerten Wunden – vielleicht ein Kratzer oder blauer Fleck, aber
    **nichts, was den Charakter einschränkt**. _System:_ **Keinerlei Abzüge**; alle Aktionen und
    Bewegung normal. _Heilung:_ Keine besondere Behandlung nötig – der Chrononaut ist **sofort
    wieder einsatzbereit** (höchstens ein kurzer Check im HQ-Medi-Lab).
  - **Leicht verletzt:** Oberflächliche Wunden (Schürfwunden, kleine Schnitte, Prellungen).
    **Leichter Schmerz** ist spürbar, Adrenalin hält einen aber auf den Beinen. _System:_ **–1
    Malus** auf feine oder konzentrationsintensive Aktionen (es fällt etwas schwerer, sich 100%ig zu
    fokussieren), ansonsten **keine großen Einschränkungen**; Bewegung weiterhin normal. Das HUD
    ergänzt automatisch `Wundmalus -1` in eure nächsten Würfelbefehle. _Heilung:_
    Solche Blessuren heilen oft **innerhalb einer Szene oder bis zur nächsten Mission** von selbst. Im HQ genügt ein
    Desinfektionsspray, Verband und eine Nacht Ruhe – zum Start der nächsten Mission sind leichte
    Wunden meist **automatisch verheilt**.
  - **Mittel verletzt:** Deutlichere Verletzungen oder starke Prellungen (z.B. tiefer Schnitt,
    klaffende Platzwunde, verstauchter Knöchel). **Schmerz und Ablenkung** nehmen zu. _System:_ **–2
    Malus** auf die meisten Proben, besonders körperliche. Keine Vollleistung mehr: Sprinten ist
    z.B. nicht möglich, nur noch normales Tempo; auch die Konzentration ist merklich gestört. Das HUD
    fügt `Wundmalus -2` an jede Würfelabfrage an. Der
    Charakter bleibt **funktionsfähig, aber spürbar gehandicapt**. _Heilung:_ Mittlere Wunden
    brauchen **eine HQ-Phase Erholung** oder medizinische Hilfe. Im HQ werden Verletzungen genäht,
    geschient oder mit regenerativen Salben behandelt. Nach einer HQ-Phase intensiver Behandlung
    (oder im Medi-Tank) kann der Malus auf –1 gelindert werden; nach einer längeren HQ-Phase Ruhe ist
    der Charakter wieder voll hergestellt. Mit futuristischer Medizin (z.B. Nanodocs als Belohnung
    oder gegen Ressourcen/Kosten) lässt sich die Heilung beschleunigen – mittlere Wunden könnten
    dann sogar innerhalb einer Szene schließen.
  - **Schwer verletzt:** Lebensbedrohliche Wunden (tiefe Stich-/Schussverletzungen, starker
    Blutverlust, komplizierte Brüche). Der Charakter steht **kurz vor dem Zusammenbruch**, zittert
    vor Schmerz und Erschöpfung, kämpft ums Bewusstsein. _System:_ **–3 Malus** auf **alle**
    Aktionen; Fortbewegung nur noch sehr eingeschränkt möglich (max. halbes Tempo, oft nur mit
    Hilfe). Die **Konzentration bricht ein**, nur grundlegende Handlungen wie Abstützen, Kriechen
    oder reines Abwehren sind noch durchführbar – an gezielten Kampf oder komplexe Aktionen ist
    kaum zu denken. Das HUD hängt automatisch `Wundmalus -3` an jede Probe an.
    _Heilung:_ Schwere Verletzungen erfordern **intensivmedizinische Betreuung**.
    **Im Feld wäre ein Agent in diesem Zustand kaum überlebensfähig**, doch hier greift das ITI-
    Notfallprotokoll: **Sinkt ein Chrononaut im Einsatz auf 0 Lebenspunkte**, initiiert das System
    **automatisch einen Zeitriss zur Not-Rückholung**. Der Verwundete wird in Sekundenbruchteilen
    ins HQ gezogen, wo ein Ärzteteam bereitsteht, um sein Leben zu retten. Die Mission ist für
    diesen Agenten damit **beendet**, aber er überlebt stabilisiert.
    Im HQ folgen dennoch **mehrere HQ-Phasen Genesung** (ggf. im Medi-Tank oder künstlichen Koma).
    Selbst mit Zukunftsmedizin und
    Biotech bleibt es eine bedeutende Ausfallzeit – unter Umständen muss der Charakter eine kommende
    Mission aussetzen (in einer langen Kampagne könnte der Spieler in der Zwischenzeit einen
    Ersatzcharakter steuern). **Narben** bleiben fast immer zurück, ob physisch oder psychisch.
  - **Kritisch verletzt:** Zustand jenseits von „schwer“ – der Charakter schwebt **in akuter
    Lebensgefahr**. Schwere innere Verletzungen, zertrümmerte Gliedmaßen oder **multiple Trauma**
    zeichnen dieses Bild. _System:_ **Keine regulären Aktionen mehr möglich.** Der Charakter driftet
    an der Bewusstlosigkeit entlang – Tunnelblick, Blut spucken, versagende Körperfunktionen. Er
    bricht schließlich **bewegungsunfähig** zusammen; **alle Proben scheitern automatisch**, solange
    dieser Zustand anhält. _Heilung:_ **Ohne sofortige Hilfe tritt der Tod ein.** Auch hier greift
    die ZEITRISS-Notfall-Mechanik: Das ITI initiiert umgehend eine **Not-Rückholung** per Zeitriss.
    Innerhalb von Augenblicken wird der Sterbende ins HQ gezogen, wo die Ärzte bereits auf ihn
    warten. In besonders brenzligen Fällen dreht das ITI die persönliche Zeit des Charakters sogar
    ein Stück zurück – die Extraktion erfolgt aus einem Moment **Sekunden vor der tödlichen
    Verwundung**, um bessere Stabilisierungschancen zu haben (natürlich nur, wenn dies kein Paradoxon
    auslöst). Für die Kampagne heißt das: Der Charakter **überlebt knapp**, ist aber **schwer
    gezeichnet**. Die Genesung dauert sehr lange, und bis zur völligen Einsatzfähigkeit vergehen
    mitunter **zahlreiche Missionen**. **Bleibende Schäden** sind wahrscheinlich (Narben, Verlust von Gliedmaßen
    etc., die evtl. durch **Cyberware** ersetzt werden). Solch ein Vorfall sollte als
    einschneidendes dramatisches Ereignis ausgespielt werden – etwa als Anlass für
    Charakterentwicklung (z.B. Angst vor dem nächsten Einsatz, posttraumatische Belastung) oder als
    Aufhänger für Upgrades (der Agent erhält z.B. einen Cyber-Arm, um den verlorenen Arm zu
    ersetzen).

_Hinweis:_ In einem erzählerisch fokussierten Spiel muss man nicht jede Verletzung tabellarisch
auswürfeln – die obigen Stufen reichen als Richtlinie. Wichtig ist, dass die **Konsequenzen
spürbar** werden, ohne den Spielfluss zu bremsen. Spielercharaktere sterben dank ITI-Protokoll **so
gut wie nie „off-screen“** durch Zufall – das Abenteuer wird eher mit dramatischer Rettung und ggf.
langfristigen Folgen fortgesetzt, anstatt mit einem abrupten Todeswurf.

- **Erschöpfung:** Neben Wunden kann **Übermüdung oder Auszehrung** den Charakter beeinträchtigen.
  Lange Missionen ohne Pause, Schlafentzug, übermäßiger Einsatz von Kräften oder schlicht
  Erschöpfung nach Kampf können zu einem **Erschöpfungs-Zustand** führen. _System:_ Pro Stufe
  Erschöpfung (vom SL nach Lage vergeben) erhält der Charakter z.B. **–1 auf alle Aktionen**,
  vergleichbar einer leichten Verletzung. Mehrfache Erschöpfung stapelt sich bis zur völligen
  **Erschöpfung/Ausgebrannt**-Stufe, wo der Charakter eventuell handlungsunfähig wird. _Erholung:_
  Erschöpfung kann durch **Ruhe, Schlaf oder Erholungsphasen** im HQ abgebaut werden. Eine kurze
  Verschnaufpause im Einsatz (eine Runde ohne Aktionen, etwas Wasser, ggf. ein Aufputschmittel) kann 1
  Stufe mildern. Vollständige Erholung erfolgt in der Regel nach einer **ausgeschlafenen Nacht**
  oder durch medizinische Stimulanzien. Stimulanzien (z.B. Koffein-Injektionen oder futuristische
  Energie-Booster) können kurzfristig Erschöpfung negieren – oft um den Preis eines späteren
  „Zusammenbruchs“, wenn die Wirkung nachlässt (optionale Regel).

- **Temporale Destabilisierung:** ZEITRISS-Agenten arbeiten mit der Zeit – doch temporale Phänomene
  können auch ihnen zusetzen. **Destabilisierung** bezeichnet einen Zustand, in dem der **Zeitstrom
  um (oder in) einem Charakter ins Wanken gerät**. Ursachen können ungefilterte temporale Energien,
  Zeitreisen ohne ausreichende Schutzmaßnahmen oder temporale Waffen/Implantate sein. Destabilisierte
  Charaktere erleben **Desorientierung, Déjà-vus oder gar Sekundenbruchteile des „Aus-der-Zeit-
  Fallens“**. _Effekt:_ Je nach Schwere erhält der Charakter **Abzüge auf Aktionen** (z.B. –1 bis
  –3) und der SL kann beschreiben, wie die Person sporadisch **flimmert oder phasenversetzt**
  erscheint. In schweren Fällen könnte der Charakter **kurz aus der aktuellen Zeitlinie gerissen**
  werden (z.B. für ein paar Spielrunden „geistabwesend“ oder an einem falschen Ort/anderen
  Zeitfragment auftauchend). _Stabilisierung:_ **Gegenmaßnahmen** umfassen spezielle
  **Temporalfelder oder Kalibrations-Module**, die das ITI im HQ oder per Gadget bereitstellen kann.
  Durch eine **Synchronisation im HQ** (ein kurzer Aufenthalt im Zeitlabor) lässt sich
  Destabilisierung meist beheben. Innerhalb des Spiels kann die KI-Spielleitung über das HUD warnen
  („Temporale Instabilität detektiert!“) und die Effektstärke anzeigen. Destabilisierung sollte als
  spannendes **zeitrelevantes Hindernis** eingesetzt werden – z.B. tickt die Zeit gegen das Team,
  bis alle wieder stabilisiert sind.

- **Trauma & mentale Nachwirkungen:** Nicht jede Wunde ist sichtbar – die Psyche der Charaktere kann
  durch Erlebnisse **Schaden nehmen**. Nach besonders **schockierenden Ereignissen** (etwa einer
  knapp überlebten kritischen Verletzung, Begegnungen mit grauenhaften Paradoxa oder dem Verlust
  eines Teammitglieds) kann ein Charakter ein **mentales Trauma** entwickeln. _Effekt:_ Das kann als
  anhaltender **Malus („Traumatisiert“) oder Nachteil** dargestellt werden – z.B. Schlafstörungen,
  Flashbacks oder Angst, die in bestimmten Situationen Abzüge verursacht. Im Spiel könnte ein
  traumatisierter Charakter etwa einen **Nervenflattern-Malus** erhalten: –1 auf Aktionen, wenn die
  Erinnerungen hochkochen (z.B. sobald wieder eine ähnliche Gefahr droht). _Verarbeitung:_ Traumata
  sollten im Rollenspiel **aufgearbeitet** werden können. Im HQ gibt es sicher **psychologische
  Betreuung** durch ITI-Therapeuten; auch kameradschaftliche Gespräche im Team können helfen.
  Schritt für Schritt kann der Malus so verringert oder ganz aufgehoben werden (eventuell pro HQ-
  Phase einen Malus-Punkt abbauen, wenn sinnvoll ausgespielt). Wichtig ist, diese
  **Charakterentwicklung** auszuspielen: Ein Agent, der z.B. in einer Epoche gefoltert wurde, könnte
  zunächst eine **Angst vor dieser Epoche** haben – was er in der nächsten Mission durch Mutproben
  und Unterstützung der Gruppe überwindet. Solche mentalen Auswirkungen machen die Charaktere
  facettenreicher, sollten aber **sparsam und einfühlsam** eingesetzt werden (das Spiel soll Spaß
  machen, keine Therapie erzwingen).

- **Schock:** Kurzzeitige Lähmung durch Schmerz oder Trauma. _Effekt:_ –2 auf alle
  mentalen Proben, bis Ruhe oder Erste Hilfe den Zustand lindert.

- **Vergiftung & Toxine:** Einige Waffen oder Fallen wirken über Giftstoffe. _Effekt:_
  Pro Runde 1W6 Schaden oder –1 bis –3 auf Aktionen, abhängig von Potenz.
  Ein erfolgreicher Medikit-Einsatz oder Antidot stoppt die Wirkung.
- **Enttarnt:** Die Tarnung ist aufgeflogen. Stealth-Manöver sind tabu, bis ein
  Safehouse oder die nächste HQ-Phase erreicht wurde.

## Heilung & Erholung – klassisch, filmisch, high-tech

Verletzungen und Erschöpfung sind Teil des Abenteuers, doch wie man damit umgeht, kann tonal
variieren. ZEITRISS bietet mehrere **Heilungsstile**, von realistisch bis cineastisch. Die Gruppe
kann wählen, was am besten passt, oder die Stile kombinieren:

- **Klassische Erholung:** Im **klassischen Modus** wird Heilung relativ **realistisch und
  zeitintensiv** behandelt. Charaktere erholen sich durch **Ruhe, medizinische Behandlung und
  Zeit**. Eine schwere Verletzung kann bedeuten, dass der Agent für den Rest der laufenden Mission
  ausfällt und erst nach wochenlanger HQ-Reha wieder voll einsatzfähig ist. Dieser Ansatz erhöht die
  Konsequenzen von Schaden – jede Wunde zählt, Ressourcen wie Verbandszeug oder Medikits sind
  wichtig. Spieler müssen Risiken gut abwägen, da **tödliche Konsequenzen** nicht immer durch Wunder
  abgewendet werden. _Spielfokus:_ Dieser Modus eignet sich, wenn Ihr **mehr Herausforderung und
  Survival-Feeling** wollt. Die Spielleitung kann offen kommunizieren, wie lange Heilung dauert
  (z.B. „Das wird mindestens eine HQ-Phase dauern“), und die HQ-Phase nutzen, um Genesungsszenen
  auszuspielen.

- **Filmische Heilung:** Im **cineastischen Stil** steht die **Dramaturgie über der Realität**.
  Helden fallen nicht einfach sinnlos um – **dramatische Rettungen** und schnelle Erholungen sind
  möglich, wenn es der Story dient. ZEITRISS unterstützt dies durch das ITI-Notfallprotokoll
  (automatische Rettung via Zeitriss bei 0 LP) und durch cinematic Tricks: etwa ein **Adrenalin-
  Stoß** in letzter Sekunde, der dem Charakter erlaubt, trotz schwerer Wunde **noch eine finale
  Aktion** durchzuführen (vergleichbar einer Filmszene, wo der Held schwer verletzt den letzten
  Schlag führt). Heilung erfolgt hier oft „zwischen den Szenen“: Nach dem Kampf schneidet man direkt
  zur Krankenstation, wo der Agent schon verbunden ist, oder man erklärt im nächsten Akt, dass ein
  **fortschrittliches Heilverfahren** ihn erstaunlich schnell wieder fit gemacht hat. _Spielfokus:_
  Dieser Modus sorgt für **hohe Immersion und Heldentum** – die Spannung entsteht durch filmreife
  Wendungen statt durch Simulation. Die SL sollte dennoch **Konsequenzen** darstellen (Narben, kurze
  Schwächephasen), aber der Erzählfluss bleibt rasant. Es kann sogar erlaubt sein, dass ein
  Charakter im Finale wieder mitmischt, obwohl er zuvor out war – sofern es **cool und glaubwürdig**
  begründet wird (z.B. mit einem High-Tech-Heilmittel). Wichtig: Alle Spieler sollten mit so einem
  **actionfilmartigen Handling** einverstanden sein, damit die Erwartungen passen.

- **Medizinische Versorgung (klassisch und im Feld):** Dieser Aspekt gilt in beiden obigen Stilen,
  verdient aber eigene Beachtung. **Medizinische Fertigkeiten und Ausrüstung** können im Spiel
  verwendet werden, um den Heilungsprozess zu unterstützen:

  - Im **Feldeinsatz** ermöglichen **Erste-Hilfe-Maßnahmen** das Stabilisieren Verwundeter. Ein
    Charakter mit Medikit oder medizinischem Talent kann z.B. **Blutungen stillen**, Schock
    behandeln oder sogar einen bewusstlosen Kollegen reanimieren. Gelingt eine entsprechende Probe
    (z.B. Medizinwissen), kann der SL entscheiden, dass die Verletzungsstufe **um 1 verbessert**
    wird (aus „schwer“ wird „mittel“ etc.) oder dass zumindest der Sterbende bis zur Rettung
    **stabil bleibt**. Dadurch gewinnen die anderen Zeit, den Verletzten zum nächsten Zeitfenster
    für die Rückholung zu bringen.
  - Im **HQ** steht eine komplette **Klinik** zur Verfügung: Operationssäle, Autodoc-Roboter,
    Genesungs-Scanner und sogar **Regenerationstanks**. Hier können selbst kritisch verletzte
    Agenten mit modernster Medizin behandelt werden.
    Das HQ-Personal kann Mali deutlich schneller abbauen, als reine Ruhe es erlauben würde.
    (Für genaue Werte kann die SL entscheiden, z.B.: pro HQ-Phase Behandlung im HQ eine Verletzungsstufe verbessern.)
    Klinik-Szenen eignen sich auch
    erzählerisch: Man kann das Team zeigen, wie es am Krankenbett plant, oder den Verwundeten im
    Fiebertraum-Szenen haben lassen – **dramatische Erholungsszenen** verstärken das filmische
    Flair.
  - **Medizinisches Personal & Talente:** Einige Chrononauten sind ausgebildete Ärzte oder
    Sanitäter. Solche Charaktere sollten ihre Fähigkeiten nutzen dürfen, um **Heilwürfe**
    durchzuführen. Im Regelkontext könnte man einen **Heilungs-Wurf** erlauben (etwa auf INT oder
    ein Medizin-Attribut), dessen Erfolg Heilzeiten verkürzt oder Mali verringert. Dadurch wird der
    „Heiler“ im Team zu einer wichtigen Rolle – ähnlich wie in klassischen Rollenspielen, aber hier
    eingebettet in Sci-Fi (von Kräuterkunde bis Nano-Medizin).

- **Implantate & Biotech-Heilung:** Im ZEITRISS-Universum verschwimmen Körper und Technik –
  **Cyberware, Biotech und Naniten** können Heilung beeinflussen. Dieses Modul erlaubt High-Tech-
  Lösungen:

  - **Heil-Implantate:** Einige Agenten tragen eingebaute Module, die im Notfall _automatisch_
    eingreifen. Beispiel: ein subkutanes Notfall-Stimulanz, das bei lebensgefährlichen Verletzungen
    sofort **Adrenalin und Gerinnungsfaktoren** ausschüttet. Im Spiel kann ein solches Implantat
    bewirken, dass der Charakter bei 0 LP **nicht sofort ausfällt**, sondern noch für eine bestimmte
    Zeit weiterkämpfen kann (z.B. für **1 Runde** voller Adrenalin, danach Zusammenbruch). Das
    erhöht die Überlebenschance und passt zum cineastischen Stil. Andere Implantate könnten
    kontinuierliche Heilung bieten (etwa ein Nanobot-Schwarm, der Wundgewebe repariert – pro Runde
    1 LP Heilung) oder Schmerzunterdrückung (Wundabzüge werden um 1 reduziert, wie ein internes
    Schmerzmittel).
  - **Biotech & Nanotechnologie:** **Heil-Naniten** sind winzige Maschinen oder genmodifizierte
    Zellen, die Verletzungen ausbessern. Im Feld könnten spezielle **Nano-Injektoren** gegeben
    werden, die eine mittelschwere Wunde in wenigen Runden schließen. **Regenerationstanks** im HQ nutzen
    Biotech, um Gewebe nachwachsen zu lassen – ein Agent könnte z.B. innerhalb eines
    Missionsintervalls einen verlorenen Finger regenerieren. All dies unterliegt der SL-Entscheidung
    und sollte **sparsam** eingesetzt werden (die Zukunftstechnologie ist zwar weit, aber
    Wunderheilungen haben oft einen Preis oder sind rar).
  - **Stim-Packs und Drogen:** Neben langfristigen Lösungen gibt es **temporäre Heilmittel**:
    Injektionen, Pülverchen oder elektronische Stims, die **sofort Erschöpfung entfernen oder
    Schmerz dämpfen**. Ein **Medi-Stim** könnte z.B. für eine Szene alle Mali durch Verletzung
    ignorieren lassen, allerdings auf Kosten späterer doppelter Erschöpfung. Solche Resourcen kann
    man als **einmalige Ausrüstung** ins Spiel bringen – vielleicht als Missions-Bonus („Ihr habt
    2 Medi-Stims, setzt sie weise ein.“). Sie unterstreichen den Sci-Fi-Aspekt der Heilung.

> **Tipp:** Besprecht in Eurer Gruppe, welcher Heilungsansatz bevorzugt wird. Ihr könnt auch
> mischen: z.B. grundsätzlich filmisch spielen, aber in einem Horror-Szenario temporär den
> klassischen härteren Stil nutzen, um die Gefahr zu erhöhen. Wichtig ist, dass alle wissen, worauf
> sie sich einlassen, damit das Drama um Verletzungen für alle **spaßig und spannend** bleibt.

## Initiative-Systeme: klassisch, cineastisch oder szenisch

Wer **handelt zuerst** in brenzligen Situationen? ZEITRISS erlaubt verschiedene Initiative-Regeln,
je nachdem ob Ihr es taktisch, schnell oder erzählerisch mögt. Drei Varianten stehen zur Auswahl:

- **Klassische Initiative:** Diese orientiert sich an traditionellen RPG-Regeln. **Jeder
  Kampfteilnehmer würfelt seine Initiative** (modifiziert durch Reflexe/Attribute), und es wird eine
  **feste Reihenfolge** festgelegt – meist der höchste Wurf zuerst, dann absteigend. Runden
  verlaufen geordnet, jeder Charakter hat seine Aktion(en) pro Durchgang. Vorteil: klare Struktur,
  taktische Planbarkeit. Nachteil: kann sich etwas starr oder unfilmisch anfühlen, wenn immer
  dieselbe Reihenfolge abläuft. _Varianten:_ Man kann pro **Kampfrunde neu würfeln** (erhöht Chaos,
  aber auch Dynamik) oder einmal zu Beginn eines Kampfes (etwas planbarer). Diese Methode passt zu
  Gruppen, die ein **vertrautes, strukturiertes System** wünschen und gerne taktisch denken.
- **Cineastische Initiative:** Hier steht das **Filmgefühl** im Vordergrund. Anstatt starr nach
  Zahlen zu handeln, bekommt z.B. **das ganze Spieler-Team zuerst eine gemeinsame Phase**, dann die
  Gegner. So wirken die Helden proaktiver – ähnlich wie in Actionfilmen, wo zuerst die Protagonisten
  agieren. Alternativ kann man einen **„Popcorn“-Ansatz** nutzen: Ein dramatisch passender Charakter
  beginnt (z.B. der Scharfschütze, der einen Überraschungsschuss abgibt), danach **bestimmt dieser,
  wer als Nächstes handelt** – vielleicht ein Gegner, wenn es spannend ist, oder direkt ein
  Mitstreiter, um Momentum aufzubauen. Jede Figur kommt genau einmal dran, bis alle in der Runde
  agiert haben; dann beginnt eine neue Runde, wieder mit dramatisch passender Reihenfolge. Diese
  Variante erzeugt einen **flüssigen, überraschenden Ablauf** wie in einem Film: Die Initiative
  wechselt je nach Situation. _Hinweis:_ Die SL behält dennoch im Blick, dass niemand übergangen
  wird – jede Partei soll pro Runde alle ihre Aktionen erhalten. Für zusätzliche Dynamik könnten
  Spieler **„Initiative-Booster“** einsetzen (z.B. ein Talent, um sich doch noch vorzudrängeln, wenn
  es brennt: „Ich nutze meine schnellen Reflexe, um jetzt sofort zu handeln!“). Cineastische
  Initiative belohnt spontane Ideen und fördert ein **gemeinsames Erzählen von Actionsequenzen**.
- **Szenendramaturgische Initiative:** In dieser **freien Variante** gibt es **keine festen Regeln**
  für Reihenfolgen – die Handlung richtet sich ganz nach der **Dramaturgie der Szene**. Die
  Spielleitung entscheidet (gerne in Absprache mit den Spielern) aus dem Kontext heraus, **wer
  gerade am logischsten oder spannendsten handelt**. Beispiel: In einer Verfolgungsjagd könnte
  zuerst der Flüchtende dran sein (um die Fluchtbewegung zu beschreiben), dann der Verfolger (um die
  Reaktion zu schildern). Oder in einem Duell lässt man den Spielercharakter immer gerade _knapp_
  vor dem Antagonisten agieren, um die Spannung zu halten, es sei denn der Schurke überrascht
  unerwartet. Diese Methode erfordert viel **Vertrauen** zwischen SL und Spielern, da sie sehr
  **flexibel** ist. Wenn alle an einem cineastischen Flow interessiert sind, kann das großartig
  funktionieren – man verzichtet komplett auf Initiativwürfe und orientiert sich an Story-Logik.
  _Wichtig:_ Jeder Spieler sollte das Gefühl haben, **fair berücksichtigt** zu werden. Die SL kann
  zur Sicherheit eine mentale Reihenfolge mitführen oder in Zweifelsfällen doch würfeln, aber
  grundsätzlich gilt: **Was der Szene dient, geschieht zuerst.** Diese Option passt zu Gruppen, die
  **erzählerisches Spielen** bevorzugen und Regelballast minimieren wollen.

> **Hinweis:** Unabhängig vom System kann man **Unterbrechungen/Reaktionen** (siehe weiter unten)
> einbauen. Auch im klassischen System dürfen z.B. bestimmte Aktionen wie „Deckung hechten“ als
> Abwehrreaktion eingeschoben werden. Im cineastischen System empfiehlt es sich, zumindest
> **protagonistischen Bonus** zu gewähren – Helden bekommen einen kleinen Vorteil in der
> Reihenfolge, damit es sich heldenhaft anfühlt. Das **HUD-Overlay** kann übrigens helfen, die
> Initiative darzustellen: Im klassischen Modus könnte es die **Reihenfolge-Liste** im UI zeigen; im
> cineastischen Modus vielleicht nur einen dezenten Hinweis, **wer gerade die Oberhand hat** (z.B.
> „Initiative: Team“ oder ein Icon für den aktuellen Akteur).

## Stress, Paradoxon und mentale Belastungen

Neben physischen Bedrohungen können **Stress und Zeitparadoxa** an den Charakteren nagen. Diese
optionalen Module erlauben es, **mentale und temporale Belastungen** abzubilden, die über bloße
Lebenspunkte hinausgehen:

- **Stress-Reset:** Stress betrifft **alle Klassen** und steigt bei Druck oder Fehlschlägen. Im
  HQ oder der Medbay fällt der Zähler auf **0**; eine kurze Ruhephase senkt ihn um **1**.
- **PP = TEMP:** Der PP-Pool entspricht der **Temporalen Affinität**. Ruhephasen und Talente wie
  _Meditation_ oder _Verbesserte Meditation_ regenerieren **1–2 PP**; Gear oder Consumables können
  situativ **+1–2 PP** gewähren.
- **Stresspunkte & Druck:** In turbulenten Missionen sammeln sich mitunter **mentaler Druck und
  Anspannung** an – sei es durch ständige Gefahr, Zeitdruck oder persönliche Konflikte. Die SL kann
  ein **Stresspunktekonto** einführen, das für einen Charakter (oder sogar das Team) mitläuft.
  _Mechanik:_ Jedes besonders belastende Ereignis (z.B. ein knapper Überlebenskampf, der Anblick
  etwas Grausigen, eine schwere Fehlentscheidung) gibt **einen oder mehrere Stresspunkte**. Klettert
  das Konto über bestimmte Schwellen, treten **Effekte** ein: z.B. bei 5 Punkten erhält der
  Charakter den temporären Zustand **„Angespannt“** (-1 auf bestimmte Proben, etwa soziale
  Interaktionen oder präzises Zielen, da die Nerven flattern). Bei 10 Punkten könnte es einen
  **Kurzzeit-Zusammenbruch** geben – der Charakter gerät in Panik, flieht, verfällt in Starre oder
  ähnliches, je nach Situation. Stress kann in HQ-Phasen durch **Entspannung** abgebaut werden: z.B.
  jede ruhige HQ-Phase setzt das Konto wieder auf **0**. Auch **rollenspielerische Maßnahmen** helfen: ein
  offenes Gespräch mit einem NSC im Freizeitraum, Meditationstraining oder ein Abend in der Bar
  können Stress verringern. Dieses Modul verleiht der Psyche Gewicht: Die Spieler achten dann nicht
  nur auf HP, sondern auch darauf, ihre **Charaktere mal durchatmen zu lassen**. Wichtig ist, dass
  Stress **nicht überstrapaziert** wird – es soll ein zusätzliches Drama-Element sein, kein
dauerhafter Malus-Hagel. Die SL kann Stresspunkte verdeckt führen und nur die Auswirkungen
beschreiben („Ihr merkt, wie eure Hände zittern nach all dem...“), oder offen kommunizieren
(„Stress 5/10 – Ihr spürt deutliche Anspannung.“), je nach bevorzugtem Stil. Das HUD besitzt
einen Toggle `/stress open|hidden`.
- **Stress-Momente:** Steht das Team unter akutem Zeitdruck (nur noch wenige
  Runden), blendet das HUD automatisch einen Countdown ein. Scheitert eine
  Probe, kann die SL einen _Fail-Forward_ zulassen und dafür Paradoxon oder
  Ressourcen in die Waagschale werfen.
- **Stress-Regeneration:** Eine Kampfrunde ohne Aktionen senkt Stress um **1 Punkt**,
  sofern eine Willenskraftprobe (CHA) gegen einen Mindestwurf in Höhe des aktuellen
  Stresslevels gelingt.
  Eine kurze Meditation über zwei Runden reduziert **3 Punkte**.
  Stress bleibt nach dem Kampf bestehen und kann nur in Ruhe oder im HQ abgebaut werden.
- **Stress als Ressource:** 5 Punkte erlauben einen Reroll.
  - **Paradoxon-Resonanz & temporale Stabilität:** Der Index misst die Stärke temporaler Spuren.
    Er steigt situativ während einer Mission. Wenig **Temporale Affinität** füllt ihn nur langsam,
    hohe TEMP beschleunigt den Aufbau. Scheitern oder massive Paradoxa halten den Wert; in
      Extremfällen sinkt er um **–1** (Px–1). Bei **Level 5** enthüllt `ClusterCreate()` bis zu zwei Rifts und
      setzt den Zähler auf 0. Offene Rifts steigern Schwelle und Loot-Faktor erst nach der Episode.
      Das **HUD** visualisiert die Resonanz über eine fünfstufige Skala.
  Seit Version 4.1.4 zeigt ein fünfstufiges Balken-Meter (1–5 Segmente) den
  Fortschritt zum nächsten Riss. Im Spiel kann GPT
  beschreiben: _„Euer HUD meldet: Paradoxon-Index 3 – Resonanzpegel steigt, erste Risskoordinaten
  rücken näher.“_ Die SL sollte Paradoxon-Index einsetzen, um **Spannung
  aufzubauen**: Vielleicht bemüht sich das Team nun um ein **kontrollierteres Vorgehen**,
  damit Stufe 5 zu einem passenden Zeitpunkt eintritt.
  _Auswirkungen:_ Steigende Werte erzeugen kleine positive Resonanzeffekte.
  Bei **Level 1** verliert die Gruppe einmalig **1 Stresspunkt**.
  Auf **2** heilt das Team **1 HP**.
  Bei **3** ist die nächste Probe um **–1 SG** erleichtert.
  Auf **4** sorgt ein Adrenalinrausch für **+2 Initiative** auf die nächste Kampfhandlung.
  Bei **5** beruhigt sich der Zeitstrom: Psi-Heat 0, 2 PP, Zustände weg. Einen Herzschlag fühlt ihr euch physisch geerdet.
  Anschließend springt der Index auf 0.
  Im Gruppenspiel verwaltet ihr **einen** gemeinsamen Index.
  Seeds zählen für alle, das Fülltempo richtet sich
  nach dem höchsten TEMP-Wert im Team.
  Zeitkreaturen können Teil dieser Risse sein. Siehe
  [Kreaturen-Generator](../gameplay/kreative-generatoren-begegnungen.md#kreaturen-generator)
  für Stat- und Schadenswerte.
  Wer einen puristischeren Thriller bevorzugt, kann [im **Covert-Ops-Modus**](../README.md#spielmodi) spielen,
  bei dem Rifts nur als dezentes Sensorrauschen auftreten. Optional zeigt das HUD
  ab Stufe 4 einen sanften Resonanzpuls an und blendet die Zahl offener Seeds ein:
  `Seeds 3 · 🔄 Paradoxon 4/5`
  So bleibt die langfristige Orientierung erhalten. Ein Foreshadow-Pulse kann dezent vor nahen Rissen warnen.
    Die Paradoxon-Mechanik ist standardmäßig aktiv, kann aber jederzeit mit
  `modus paradoxon off` abgeschaltet werden – unabhängig davon, ob das Team
  **pro** oder **contra** spielt. Mit `modus paradoxon on` schaltet ihr sie
  wieder ein.

  Modul Paradoxon-Resonanz gibt der Gruppe Feedback, **wie viel temporale Resonanz ihr Einsatz erzeugt**. Clevere
    Chrononauten haben vielleicht Geräte oder Talente, um Paradoxa zu **erkennen oder zu
    reduzieren** (z.B. einen tragbaren Paradoxon-Detektor, der früh Alarm schlägt, oder einen
  Temporallogiker im Team, der durch kluge Entscheidungen Stabilität zurückgewinnt).
  Behutsames, stilvolles Vorgehen steigert den Index zusätzlich, während grobe Aktionen keinerlei Auswirkungen haben.
  Setzt dieses Element mit Bedacht ein – es soll **Handlungsanreize** bieten („Wir müssen aufpassen,
  sonst…“), aber nicht jedes Abenteuer dominieren. Wenn es passt, kann eine ganze Mission darauf
  ausgelegt sein, **eine temporale Anomalie zu beheben**
  (z.B. einen Fehler in der Vergangenheit zu korrigieren).

_Resonanzpuffer:_ Der Index steigt nur noch, wenn bereits **zwei Resonanz-Marken** in der Szene
  liegen – die erste setzt lediglich eine Warnung. Erreicht der Index
  Stufe 5, aktiviert `ClusterCreate()` 1–2 Seeds und setzt den Wert zurück.

### Paradoxon-Statusanzeige [0–5]

### HUD-Banner · Paradoxon
██ Paradoxon 3/5 – Resonanz stabil · Loot +1 ██
██ Paradoxon 5/5 – ClusterCreate! Neue Rifts gescannt ██
`Paradoxon 3/5 · Resonanz ↑`
`Paradoxon 5/5 · ClusterCreate – Rifts sichtbar`
`Paradoxon: ▓▓▓░░ · TEMP 11 · +1 nach 2 Missionen`
`Paradoxon −1 · Backlash`

- **Beispielwerte:**
  - **+1** sauber/leise (Gerät gesichert, diskrete Exfil)
  - **0** laut, aber ohne gravierende Spuren
  - **−1** Backlash, grobe Störung, Anker kompromittiert oder Zivilisten gefährdet
- Banner erscheint immer am Szenenende. Farben:
- rot 0–2 · gelb 3–4 · grün 5

> _Resonanzanzeige für Rissverfolgung_
> _Kodex-Modul: `CLSTR:TRACE.MONITOR`_

#### PARADOXON 0/5
> *"Stille im Strom."*
> Kein Zugriff. Keine Signaturen.
> Der temporale Raum ist stabil – aber leer.
> _(Noch keine Cluster-Annäherung möglich)_

_Kodex:_
> `Resonanzpegel minimal – keine Risssignaturen im Scanbereich`

#### PARADOXON 1/5
> *"Flackern. Wie Erinnerungen an etwas, das nicht geschehen ist."*
> Erste Resonanzspuren.
> Unklare Bewegungsmuster im Kodex-Raster.

_Kodex:_
> `Anstieg im TEMP-Feld registriert – Zugriffsstreue noch unzureichend`
> `Aktuelle Interventionsrate: niedrig`

#### PARADOXON 2/5
> *"Schatten über der Gegenwart. Manche Missionsorte scheinen… lauter."*
> Temporale Felder beginnen, Einfluss auf Zielumgebung zu nehmen.
> Spieler könnten instinktiv fühlen: Hier ist mehr.

_Kodex:_
> `Temporale Resonanz aktiv – latente Rissaktivität prognostiziert`
> `Empfindlichkeit TEMP > 5 empfohlen`

#### PARADOXON 3/5
> *"Datenströme verzerren. Lichtquellen flackern. Manchmal ist die Luft… anders."*
> Temporale Druckwellen, bereits messbar.
> Die Welt reagiert auf die Eingriffe der Chrononauten – ohne es zu wissen.

_Kodex:_
> `Clustervorlauf erreicht – erste Zugriffspfade geometrisch ausgerichtet`
> `Sprungkoeffizient > 0.63`

#### PARADOXON 4/5
> *"Der Strom spricht. Etwas versucht, sichtbar zu werden."*
> Zugriff steht kurz bevor.
> Artefakt-Raster beginnen sich zu synchronisieren.

_Kodex:_
> `INFO: Zugriffskorridor im Aufbau – ClusterCreate bald`
> `Rift-Koordinatenpotenzial: hoch`

#### PARADOXON 5/5 – CLUSTERCREATE
> *"Der Riss ist da. Ihr könnt ihn sehen, noch bevor er geschieht."*
> Ihr habt genug Resonanz erzeugt.
> **Paradoxon 5 erreicht – neue Rift-Koordinaten verfügbar.**
> Kodex vermerkt **1–2 neue Rift-Ziele** auf der Raumzeitkarte. Diese werden erst
> nach Episodenende freigeschaltet.

_Kodex:_
> `Clusterpunkt erreicht – Zugriffspfade gesetzt`
> `Paradoxon-Index zurückgesetzt`
> `Rift α–beta Koordinaten gespeichert – Zugriff nach Episodenende`

🎖 Optional:
> Seeds können fürs HQ notiert und später genutzt werden.
> Offene Rifts erhöhen Schwierigkeitsgrad und Loot-Multiplikator erst nach der Episode.

### Zusatzregel
> Jeder Paradoxonpunkt symbolisiert ein Stück temporaler Nähe zu einem instabilen Raum.
> Der TEMP-Wert bestimmt die Geschwindigkeit,
> der Erfolg die Richtung –
> und CLUSTERCREATE den Zugang zur Beute.
### Paradoxon-Subsystem

Das vereinfachte Paradoxon-Subsystem orientiert sich an der Kampagnenstruktur
und zeigt, welche Effekte bei welchen Stufen auftreten.
Steigende Resonanz belohnt das Team mit kleinen Boni.

| Stufe | In-Mission-Effekt               | HQ-Effekt                                    |
| ----- | ------------------------------- | -------------------------------------------- |
| 0–1   | Stabil                          | –                                            |
| 2     | einmalig −1 Stress                        | – |
| 3     | Gruppe heilt 1 HP                         | – |
| 4     | +2 Initiative auf nächste Kampfhandlung     | „Riss-Vorstufe“-Flag |
| **5** | Psi-Heat 0, 2 PP, Zustände weg (Zeitstrom stabil) | **ClusterCreate()** enthüllt 1–2 Rifts, Index = 0 |

Nach Stufe 5 setzt `ClusterCreate()` den Paradoxon‑Index auf 0 und legt 1–2 neue
  Rift-Seeds auf der Raumzeitkarte ab. Diese sind erst nach Episodenende vom HQ aus
  erreichbar.

### Raumzeitkarte {#raumzeitkarte}

Die **Raumzeitkarte** ist ein großflächiges Holodisplay im HQ. Sie zeigt
alle bekannten Epochen als interaktive Knotenpunkte. Neue Seeds erscheinen dort
automatisch, sobald `ClusterCreate()` aktiv wird. Aus dem HQ können die
Chrononauten über ihr **ITI-Terminal** direkt ein Sprungziel auf der Karte
anwählen. Im Einsatz blendet die AR-Kontaktlinse verkleinerte Auszüge der
Karte ein, um Risse oder Missionsziele zu lokalisieren.

_Optional kann [eine Covert-Ops-Variante](../README.md#spielmodi) gespielt werden,_
bei der keine Risse oder Zeitkreaturen erscheinen.

**Mini-Beispiele**

1. *Mittelalter:* Ein Runensymbol pulsiert – die Gruppe verliert **1 Stress**.
2. *Viktorianisch:* Euer Monokel-HUD leuchtet kurz und heilt **1 HP**.
3. *Zweiter Weltkrieg:* Funkgerät surrt, die nächste Probe ist **–1 SG** leichter.
4. *Kalter Krieg:* Ein Adrenalinrausch verleiht **+2 Initiative**.
5. *Cyber-Future:* Psi-Heat sinkt auf 0 und das Team erhält **2 PP**; negative Zustände lösen sich auf.

> **Reminder:** Paradoxon-Index nach jeder Zeitlinien-Änderung aktualisieren.

## Ressourcenmodelle: Ausdauer & PP-Pool (optional)

Standardmäßig verwaltet ZEITRISS keine kleinteiligen Ressourcen wie Mana oder Ausdauer – der Fokus
liegt auf Handlung. Wer aber gern **Ressourcenmanagement** betreibt oder spezielle Kräfte einführen
will, kann folgende **optionale Ressourcensysteme** modular hinzufügen. Diese Werte können im
**HUD** angezeigt werden, um den Überblick zu behalten.

- **Ausdauer (Stamina):** Dieses Modell simuliert **körperliche Erschöpfbarkeit** im Detail. Jede
  anstrengende Aktion (Sprinten, schwere Angriffe, Tragen von Lasten) kostet Ausdauerpunkte. Ein
  typischer Wert könnte z.B. 100 Punkte pro Charakter sein. Laufen, Kämpfen, Klettern ziehen Punkte
  ab, **Rasten oder Stimulanzien** stellen Punkte wieder her. Sinkt die Ausdauer unter bestimmte
  Schwellen (50%, 25%), greift man auf die oben beschriebene **Erschöpfungs-Mechanik** zurück: der
  Charakter erhält Mali, als wäre er erschöpft. Bei 0 Ausdauer kann der Charakter nicht mehr
  vernünftig agieren (völlige Erschöpfung, Zusammenbruch). _Anwendung:_ Ausdauerpunkte machen
  Aktionen **bedeutsamer** – man kann nicht endlos rennen oder kämpfen, ohne zu verschnaufen. Im HUD
  ließe sich das als **Ausdauerbalken** darstellen. Dieses Modul passt, wenn eure Gruppe etwas
  **Survival-Feeling oder taktische Tiefe** möchte. In einem filmischeren Spiel hingegen ignoriert
  man Ausdauer bewusst, um Helden nicht künstlich zu bremsen.
- **PP-Pool (Psi-Energie):** Power-Punkte (PP) sind fest an _Temporale Affinität (TEMP)_
  gebunden; euer Pool entspricht also dem TEMP-Wert. Starke/mittlere/geringe
  Kräfte kosten 3/2/1 PP und lösen 3/2/1 Runden Cooldown aus. Nach jeder
  Kampfrunde könnt ihr pro **3 TEMP** 1 PP regenerieren, falls eine
  Willenskraftprobe (CHA) gegen doppelten Psi-Heat gelingt; nach jedem Kampf wird
  der Pool voll aufgefüllt. Große
  Effekte erhöhen die Psi-Heat. Im HUD zeigt ein Ω-Symbol die aktuelle PP-Zahl.

### HUD-Meldungen – Psi

| Trigger | Anzeige |
|---------|---------|
| PP ≤ TEMP ÷ 4 | `PP LOW` |
| PP 0 | `PP EMPTY` |
| Burn aktiv | `BURN` `Px -X` |
- **Modulare Ressourcen allgemein:** Natürlich könnt ihr auch andere Ressourcen tracken, z.B.
  **Munition**, **Batterieladung von Geräten**, **Sauerstoffvorrat** in bestimmten Szenarien etc.
  Das HUD prädestiniert sich dafür, solche Infos übersichtlich anzuzeigen (etwa „Munition: 12/30“
  bei einer Feuerwaffe). Der Grundansatz von ZEITRISS ist aber: **Nur das Nötigste verwalten.**
  Führt also nur Ressourcensysteme ein, die euren Spielspaß **erhöhen**. Wenn ihr merkt, dass Punkte
  zählen euch aus der Immersion reißt, lasst es lieber weg und vertraut auf die narrative Logik (die
  KI-Spielleitung kann dann z.B. entscheiden, wann die Munition knapp wird, anstatt jede Kugel zu
  zählen).

## Besonderheiten im Zeitstrom: Unterbrechungen, Reaktionen & freie Aktionen

Zeitreisen und Hochrisiko-Missionen erfordern manchmal **schnelle Reflexe und spontane Aktionen**.
Unabhängig vom gewählten Initiative-System könnt ihr folgende Sonderaktionen erlauben, um den Kampf-
und Actionszenen mehr **Lebendigkeit** zu verleihen:

- **Unterbrechungen:** Eine Unterbrechung ist eine **außerplanmäßige Zwischenaktion**, mit der ein
  Charakter _im selben Moment_ reagiert, in dem etwas passiert, und so den Ablauf „unterbricht“.
  Beispiel: Ein Agent sieht, wie ein Feind den Finger krümmt, um zu schießen – der Agent ruft:
  _„Unterbrechung! Ich werfe sofort eine Blendgranate!“_ Wenn die SL die Unterbrechung zulässt (ggf.
  mit einer Bedingung wie „ihr verbraucht dafür eure nächste reguläre Aktion“ oder einem
  erfolgreichen Reflex-Wurf), wird die granate **noch bevor** der Schuss fällt ausgelöst.
  Unterbrechungen sind als **dramatisches Mittel** zu verstehen: In Filmen sieht man oft, wie jemand
  im _letzten Augenblick_ noch etwas tut. Im Spiel sollten sie **restriktiv** gehandhabt werden –
  etwa **maximal eine Unterbrechung pro Runde pro Charakter**, nur wenn es **dramatisch passt**.
  Möglich ist auch, Unterbrechungen an **Ressourcen** zu knüpfen (z.B. verbraucht 1 PP oder
  einen besonderen „Reflexmarker“). Das ZEITRISS-Setting bietet sogar techische Rechtfertigungen:
  Vielleicht nutzen einige Agenten **Temporalsinn-Implantate**, die für Sekundenbruchteile in die
  Zukunft spüren lassen, um solche Unterbrechungen durchführen zu können. Wichtig ist, dass
  Unterbrechungen **klar kommuniziert** werden („Ich will unterbrechen, sobald der Wächter den
  Alarmknopf drückt…“) und dass die SL fair entscheidet, ob es gelingt. Richtig eingesetzt, können
  Unterbrechungen extrem **spannende Wendungen** erzeugen.
- **Reaktionen:** Reaktionen sind **Antworten auf Aktionen anderer**, die sofort erfolgen, aber
  nicht unbedingt den gegnerischen Ablauf verhindern – eher _parallel_ dazu oder im direkten
  Anschluss. Klassisches Beispiel: der **Gelegenheitsangriff** – ein Gegner läuft an euch vorbei, und
  _als Reaktion_ dürft ihr einen schnellen Schlag ausführen. Oder der Feind schießt auf euch, und
  _als Reaktion_ werft ihr euch zu Boden (**Ausweichreaktion**), um schwerer getroffen zu werden.
  Anders als Unterbrechungen, die das Geschehen _unterbrechen_, laufen Reaktionen _mit_ dem
  auslösenden Ereignis. Viele Systeme erlauben z.B. **eine Reaktion pro Runde** außerhalb der
  eigenen Turnorder. In ZEITRISS könnt ihr das ähnlich handhaben: Jeder Charakter hat z.B. **1
  Reaktion pro Zyklus**, die er einsetzen kann, wenn ein definierter **Trigger** eintritt (wie „ich
  werde angegriffen“ oder „mein Verbündeter wird getroffen, ich will ihn auffangen“). Reaktionen
  sollten **einfach** gehalten werden (kein halber Roman an Aktionen – es geht um kurze
  Reflexhandlungen). Beispiele im Spiel: Parieren oder Blocken eines Nahkampfangriffs, Gegenfeuer
  geben wenn man beschossen wird, einen fallenden Artefaktbehälter noch auffangen, bevor er am Boden
  zerschellt, etc. Diese Mechanik gibt Spielern das Gefühl, auch _zwischen_ ihren Zügen
  **handlungsfähig** zu sein, was die Cinematic-Dichte erhöht. Das HUD könnte Reaktionsmöglichkeiten
  symbolisch andeuten (z.B. ein kleines Icon, wenn eine Reaktion jetzt verfügbar ist – etwa ein
  Schild-Icon für „Abwehr bereit“).
- **Freie Aktionen:** Unter freie Aktionen fallen all jene Handlungen, die **keine nennenswerte Zeit
  im Zeitstrom kosten**. Im Prinzip können sie _jederzeit_ durchgeführt werden, sofern logisch – oft
  auch parallel zu Hauptaktionen. Typische freie Aktionen: **Etwas rufen oder schreien**, eine kurze
  Funknachricht absetzen, eine Waffe fallen lassen, einen Knopf drücken, ein Holster öffnen, das HUD
  kurz konsultieren, etc. Im Kampf kosten solche Kleinigkeiten _keine_ Aktion, solange sie wirklich
  kurz sind. Aber Achtung: Mehrere freie Aktionen hintereinander sind irgendwann nicht mehr „frei“ –
  in der Summe kosten sie natürlich doch Aufmerksamkeit. Die Faustregel: **1–2 freie Aktionen pro
  Zug** (z.B. etwas zurufen _und_ sich umschauen) sind okay, alles darüber hinaus sollte die SL als
  normale Aktion werten. Der Begriff „im Zeitstrom“ bedeutet hier, dass diese Handlungen **so fix
  ablaufen**, dass sie den Fluss der Zeit nicht spürbar verzögern – quasi wie ein Schnitt im Film,
  in dem der Held einen kurzen Satz sagt oder den Sicherheitshebel umlegt, während die Haupthandlung
  weitergeht. Freie Aktionen eignen sich auch für **stilistische Beschreibungen**: Ein Agent könnte
  während seines Angriffs noch einen one-liner raushauen (frei) oder mitten im Sprint dem Team etwas
  zurufen. Dadurch wirken die Szenen lebendig. In begrenzten Situationen kann die SL freie Aktionen
  auch _einschränken_ („Unter Wasser könnt ihr leider nichts rufen“) – meist regelt aber der gesunde
  Menschenverstand, was geht. Spieler sollten also nicht versuchen, eine „freie Aktion“ zu dehnen,
  um doch noch etwas Großes umsonst zu erledigen. Solange alle ehrlich abschätzen, was in einer
  Sekunde machbar ist, bleiben freie Aktionen ein intuitives Werkzeug.

> **Zusammenspiel:** Unterbrechungen, Reaktionen und freie Aktionen sorgen gemeinsam dafür, dass
> sich Action-Sequenzen **weniger rundenbasiert, sondern organischer** anfühlen. Die KI-Spielleitung
> sollte diese Möglichkeiten präsent halten. Im Text kann GPT z.B. anregen: \*„Der Wachmann hebt die
> Pistole – möchtet ihr **_reagieren_** (z.B. in Deckung springen)?“_ oder _„Die Zeit scheint zu
> stocken – falls ihr jetzt **_unterbrecht_** und den Zeit-Stasis-Gadget aktiviert, könntet ihr dem
> Ereignis zuvorkommen…“\*. So werden Spieler ermutigt, kreativ mit dem Zeitstrom zu spielen.

## Cinematisches HUD-Overlay: Immersives Interface im Spiel {#cinematisches-hud-overlay}

Ein Highlight von ZEITRISS 4.2.3 ist das **HUD-System** – ein persönliches Heads-Up-Display für jeden
Chrononauten, das ingame-Informationen in Kurzform sichtbar macht. Dieses **filmisch-immersive
Interface** verbindet die **Regelmechanik mit der Spielwelt**: Spielercharaktere _sehen_ wichtige
Werte vor sich eingeblendet, sodass wir sie auch dem Spieler mitteilen können, ohne die Immersion zu
brechen. Das HUD wird über den **ITI-Kodex** gesteuert und kann vom Charakter _nach Bedarf
aktiviert_ oder minimiert werden. Im Folgenden die zentralen HUD-Funktionen und wie sie eingesetzt
werden. Solange die Verbindung zum Kodex stabil ist, liefert das HUD zusätzliche
  Hinweise und Beschreibungen. Bricht die Verbindung ab – etwa durch Paradoxon-Effekte
oder Störsignale – reduziert sich die Anzeige auf rudimentäre Grundwerte. Ein lokales
Bei gestörter Verbindung werden alle Werte grau hinterlegt, um den Ausfall klar zu zeigen.
**Tactical Scratchpad** speichert dann die aktuellen Missionsziele, damit nichts verloren geht.
Bei Totalausfall liefert eine Systemmeldung ein Kurzregel-Backup. Kurzfassung:
Telekinese = Attribut + Erfolgsstufen, Reichweite 5 m. Paradoxon-Index 0–5; bei
Stufe 5 triggert ClusterCreate(). Stress bis 9: handlungsfähig, ab 10 gibt es
Mali. Mehr Details im Kodex.

> **Dünnes Overlay, physischer Träger.** HUD-Zeilen erscheinen in Backticks als
> Display-/Sensor-Feedback (Linse flackert, Relais klickt, Resonator vibriert) –
> niemals als schwebendes Holo ohne Gerät. **MODE CORE** kennzeichnet Episoden,
> **MODE RIFT** Casefiles aus dem HQ. Casefile-Overlays zeigen Tatort → Leads →
> Boss mit genau einem Anomalie-Element.
Das HUD zeigt standardmäßig nur **vier Symbole** (Vital, Stress, Tarnung, Paradoxon); weitere
Statusanzeigen lassen sich per Swipe-Geste oder Sprachbefehl einblenden. Diese
Einschränkung sorgt für Spannung und hält die Balance. **HUD-Blenden dürfen
maximal sechs Wörter enthalten**; ausführliche Effekte stehen im Anhang:

Der Szenenheader zeigt nach der Episoden- und Szenenzeile dauerhaft
`Seed <id>` als zweite Zeile.

Ein kurzes Beispiel für eine typische HUD-Einblendung könnte so aussehen:

```
`Vitalstatus 20% – kritisch`
`Riss-Tracker (temporaler Resonator) Stufe 3`
`Magazin 4/12 · SYS 2/4`
```

- **HUD-Warnung bei Heavy-Gear:** Sobald aktive Ausrüstung den Wert überschreitet,
  blinkt `SYS overload – Heavy` auf.
- **HEAVY LOCK Anzeige:** Fehlt die passende Lizenz für ein {heavy}-Item,
  erscheint `HEAVY LOCK`.

- **Vitalstatus (Lebenspunkte & Verwundungen):** Das HUD zeigt die aktuelle **Gesundheit** des
  Charakters meist als farbige **Lebensleiste oder Silhouette**. Grün steht für okay, Gelb für
  leichte Verletzungen, Rot für kritisch – entsprechend der oben beschriebenen Verwundungsstufen.
  Ab **50 %** löst das HUD einen **gelben Voralarm** aus, bei **25 %** wechselt es auf Rot.
  Ein zusätzliches Warnsymbol hilft farbblinden Spielern.
  Zusätzlich kann eine **Prozentzahl** die verbleibenden Lebenspunkte anzeigen (z.B. „HP 75%“).
  Spezielle **Zustände** werden durch **Icons** verdeutlicht: Etwa ein Tröpfchen-Symbol bei
  _Blutung_, ein gebrochenes Knochen-Icon bei _Beinverletzung_, ein Totenkopf bei _Vergiftung_. Die
  KI-Spielleitung nutzt diese Anzeige, um **Schaden und Zustand atmosphärisch zu vermitteln**: Statt
  plump „Ihr habt nur noch 2 HP“ zu sagen, kann GPT formulieren: _„Euer HUD blinkt Warnsymbole auf –
  der Gesundheitsbalken sinkt in den roten Bereich, kritischer Blutverlust!“_ Der Spieler begreift
  sofort, wie schlimm es seinem Charakter geht, **in-world** durch die Augen der Figur.
| HUD-Meldung | Regelbedeutung |
| ------------ | ---------------- |
| `Vitalstatus kritisch` | Lebenspunkte unter 25 % |
| `Riss-Tracker (temporaler Resonator) Stufe 3` | Paradoxon-Index 3, Resonanzmeldung |
| `Filter ausgefallen` | Sichtmodifikator oder Tarnmodul defekt |
- **Ausdauer, PP-Pool & Effekte:** Neben der Gesundheit können optional auch **Ressourcen** und
  **Buffs/Debuffs** im HUD erscheinen. Wenn ihr z.B. das oben erwähnte Ausdauer-System nutzt oder
  den PP-Pool sichtbar machen wollt, könnte das HUD einen **Ausdauerbalken** unter der HP-Leiste
  einblenden oder eine **PP-Anzeige** in Prozent. Temporäre **Status-Effekte** – sei es durch Ausrüstung, Drogen
  oder Zustände – werden ebenfalls visualisiert. Beispiel: Ein Agent injiziert sich einen
  **Adrenalin-Stim**, der 60 Sekunden wirkt – im HUD startet ein **Countdown-Timer** („Stim aktiv –
  00:59“), der runtertickt. Oder der Charakter hat einen Malus „Bewegung verlangsamt“ (etwa bei
  Beinverletzung) – ein kleines durchgestrichenes Laufsymbol taucht auf. Auf diese Weise verknüpft
  das HUD **Regelzustände mit dem Charaktererleben**: Der Spieler _sieht_ vor seinem inneren Auge,
  was Sache ist. GPT kann etwa beschreiben: _„Ein kleines Icon blinkt im Sichtfeld: euer Bein ist
  verletzt, ein Warnsymbol drosselt die Bewegungsanzeige.“_ – Das klingt nach Sci-Fi-Interface,
  deckt sich aber mit dem Malus aus der Regel.

#### HUD-Icons auf einen Blick {#hud-icons}

| Symbol | Bedeutung |
| ------ | --------- |
| ❤️ | Vitalstatus |
| ⚠️ | Stresslevel |
| 🔄 | Paradoxon-Index |
| 🩸 | Blutung |
| ☠️ | Vergiftung |
| ⏱️ | Countdown/Timer |
| 🛡️ | Abwehr bereit |
| 🌀 | TK-Nahkampf im Cooldown – Eure Linse sperrt telekinetische Schläge, bis der Puls abklingt. |

#### Risk-Level-Badges {#risk-level-badges}

| Badge | Bedeutung | Einsatz im Spiel |
| ----- | --------- | ---------------- |
| 🟢 R1 · Niedrig | Warnhinweis, leichte Umstände | Komfort- oder Atmosphäreeinblendungen (z.B. Ping, Blend 1 Sz) |
| 🟡 R2 · Moderat | Spürbarer Malus | Zustände mit Stress-/Heat-Anstieg oder temporären Sperren |
| 🟠 R3 · Hoch | Drohender Verlust | Struktur- oder Item-Risiken (z.B. Artefaktbruch, drastischer Debuff) |
| 🔴 R4 · Kritisch | Harte Eingriffe | SYS-/Vital-Verlust, schwere Folgen; dramaturgisch ankündigen |

#### Quickref: Health, Stress & Zustände {#hud-quickref}

| Anzeige | Bedeutung |
| ------- | --------- |
| `HP 100%` | Charakter unverletzt |
| `HP <50%` | Verwundet (−1 auf Aktionen) |
| `Stress 1–5` | leichte Anspannung |
| `Stress 6–9` | starke Belastung (−1) |
| `Stress 10` | Zusammenbruch |
| 🩸 | Blutung – jede Runde 1 Schaden |
| ☠️ | Vergiftung – SG +2 auf Proben |
| `SC n/N` | aktuelle Szene / Budget |

#### HUD-Snippets (Kurzmeldungen)

```
`Paradoxon 3/5 · Resonanz ↑`
`Paradoxon 5/5 · ClusterCreate – Rifts sichtbar`
`Heldenwürfel verfügbar`  🎲  Jetzt einsetzen?
`Akku Psi-Modul 18 %`  ⚠  Leistung drosseln!
```
`Paradoxon 3/5`
Beispiel-Button-Bar: `1` `2` `3` `4` `5`
Live-Anzeige: `Rifts offen x` `+SG +y` `CU-Multi z×`
Diese Zähler aktualisieren sich nach jeder Szene und sofort nach `createRifts()`.
<span style="color:#f93">Regel: bei Px 5 folgt ClusterCreate()</span>

[[RULE]] ClusterCreate() bei Px 5 [[/RULE]]
- **Initiative & Team-Status:** Das HUD-Overlay ermöglicht auch einen Überblick über die
  **Kampfsituation**. Je nach gewähltem Initiative-Modus könnte es eine **Reihenfolge-Anzeige**
  geben – z.B. eine Leiste mit den Porträt-Icons aller Beteiligten in aktueller Reihenfolge. In
  einem klassischen System sieht der Agent also, _wer wann dran ist_. Im cineastischen Modus könnte
  das HUD flexibler sein, vielleicht nur hervorheben: **„Ihr seid am Zug!“** (durch ein
  aufleuchtendes eigenes Icon) oder anzeigen, **wer aktuell agiert** (etwa ein roter Rahmen um dem
  Gegner-Avatar, der gerade feuert). Auch der **Team-Status** ist sichtbar: Jeder Chrononaut sieht
  die Vitalwerte seiner Mitstreiter als kleine Anzeigen am Rand. So kann GPT z.B. erwähnen: _„Miras
  Vitalwert steht bei 100% (grün) – sie ist unverletzt.“_ oder _„Euer Team-Panel zeigt bei Nikolai
  nur noch 10% (blinkend rot) – er steht kurz vor dem Kollaps.“_ Dadurch haben Spieler **Ingame-
  Information**, wer Hilfe braucht, ohne out-of-character nachfragen zu müssen. Ebenfalls praktisch:
  **Team-Icons** können besondere Zustände der Kollegen anzeigen (z.B. ein **Häkchen** für „Auf
  Position/Primärziel erfüllt“ oder ein **Fragezeichen** bei „vermisst/außer Sicht“).
- **Missionsziele & Hinweise:** Das Kodex-HUD fungiert auch als Missionsassistent. **Aktive
  Missionsziele** (Primär- und Nebenquests) können als Liste oder Texteinblendung erscheinen.
  Beispiel: _„Primärziel: Sabotiere die Kanonen (noch offen)“_, _„Optional: Artefakt sichern
  (falls vorhanden)“_. So behält das Team im Eifer des Gefechts die **Objectives** im Blick. GPT sollte
  diese Infos sparsam und kontextsensitiv einblenden – etwa nur, **wenn die Spieler danach fragen**
  („Ich schaue aufs HUD, welche Ziele noch offen sind“) oder wenn es die Charaktere brauchen (z.B.
  nach einer langen Diskussion: _„Euer HUD erinnert euch: Es bleibt noch das Ziel ‚Daten sichern‘
  unerledigt.“_). Neue Missionshinweise können automatisch aufleuchten, sobald sie anfallen (etwa
  _„❗ Neues Ziel: Fluchtweg finden“_ wenn eine Fluchtsituation eintritt). Das erhöht die Immersion,
  da es sich anfühlt, als ob die Agenten von ihrer Einsatz-KI unterstützt werden – ähnlich wie
-  Videospiel-Charaktere, die via HUD Missionsupdates erhalten.
- **W10-Schwelle:** Erreicht eines eurer Attribute den Wert **11**, blendet das HUD ein kleines
  **`W10 aktiv`** neben diesem Wert ein. Ab 14 weist das HUD zusätzlich auf den Heldenwürfel hin
  (einmaliger Reroll).
- **Riss-Tracker (temporaler Resonator):**[^riss-tracker] Der **Paradoxon-Index**
  ist euer Wegweiser zu wertvollen Anomalien und belegt
  daher eine prominente Stelle im HUD. Er erscheint als **Skala mit Zeit-Symbol**, Farblogik
  umgekehrt: rot = Start, gelb = Spannung, grün = endlich stabil. Bei Level 0 leuchtet ein rotes ⏳.
  Steigt der Index, wechselt es auf gelb/orange ebenfalls mit ⏳; bei 5 leuchtet es grün und kündigt
  den `ClusterCreate()`-Moment an. Steigt der Index weiter, pulsiert das Symbol, bis sich der Wert
  wieder beruhigt. GPT kann diesen Anstieg inszenieren: _„Euer HUD flackert und springt auf
  Paradoxon-Index 4 – die Umgebung wirkt fokussierter, als würden neue Koordinaten auf eurer
  Raumzeitkarte aufblitzen…“_. Die Spieler
    erkennen sofort, dass sich ein profitabler Pararift anbahnt. Auch kleinere Paradoxon-Effekte können
  gemeldet werden (_„Temporale Fluktuation detektiert“_ bei Level 1–2, evtl. begleitet von einem leichten
  Glitzern oder farbigen Schimmern im HUD).
  Das HUD macht die **Zeitchancen** direkt erlebbar. Ein dauerhafter 0–5-Balken
  zeigt dabei den aktuellen Fortschritt. Ab Stufe **3** färbt sich die Anzeige gelb, bei **5** leuchtet
  sie grün. Nach einem automatischen
  `ClusterCreate()` setzt ein kurzer Weiß-Flash mit Signalton den Wert zurück.
  Bei jedem Anstieg wird der neue Wert direkt im Kodex-Log vermerkt.

[^riss-tracker]: Implantierter Resonator, Standardausrüstung aller Chrononauten.

- **Ausrüstung & Inventar:** Im persönlichen HUD sind außerdem wichtige **Ausrüstungsgegenstände**
  verzeichnet, vor allem die aktuell ausgerüsteten. Z.B. sieht ein Scharfschütze unten rechts ein
  **Munitionszählwerk** seiner Sniper („Magazin: 5/10“ Kugeln). Oder ein Agent mit einem Gadget
  (z.B. einem tragbaren Zeit-Stabilisator) sieht ein Icon mit **Ladebalken** oder Restenergie dieses
  Geräts. Schlüssel-Items einer Mission können ebenso angezeigt werden – hat das Team etwa ein
  **Artefakt** gesichert, könnten alle ein kleines Symbol „Artefakt X – Gesichert“ sehen. Diese
  Anzeigen erlauben es, auch Ressourcendinge wie Munition oder Gadget-Abklingzeiten elegant ins
  Spiel zu integrieren. GPT kann bei Nachfragen ins HUD blicken lassen: _„Euer HUD zeigt 2 Granaten
  im Inventar-Slot an“_ anstatt einfach zu sagen „Ihr habt noch 2 Granaten“. So bleiben wir im
  Charakter.
- **Kodex-Steuerung & Einblendung:** Das HUD ist nicht ständig volldisplayt – die Agenten können es
  **nach Belieben ein- und ausblenden** oder einzelne Module aufrufen. Gesteuert wird es über den
  **Kodex**, das intelligente Expertensystem des ITI. In-world läuft das oft über Sprachbefehle oder
  Gedankensteuerung. Spieler können also im Spiel sagen: _„Kodex, HUD-Übersicht!“_ – und die KI-
  Spielleitung (GPT) liefert daraufhin eine **knappe Übersicht** aller relevanten Werte. Beispiel
  einer solchen Bildschirmlese: _„Vitals 78% (grün) • Paradoxon-Index 1 • Zeitstabilität 92% •
  Primärziel: teilweise erfüllt“_. Das sind keine out-of-character Statuswerte, sondern _die Figur selbst
  sieht diese Anzeigen_. Dadurch verschwimmt die Grenze zwischen Spielerinformation und
  Charakterwissen positiv: Der Spieler fragt quasi seinen eigenen Ingame-Computer nach Daten. Der
  **Kodex** agiert auch proaktiv: Er kann autonome **Warn-Pop-ups** senden, wenn wichtige Schwellen
  erreicht werden – z.B. _„⚡ Energie unter 20%“_ oder _„⏳ Missions-Timer: 60 Sekunden verbleibend“_,
  je nachdem was im Szenario relevant ist. Diese Alarme sollten sparsam eingesetzt werden, damit sie
  dramatisch bleiben. Richtig genutzt, fühlt sich das Interface **lebendig** an, fast so als würde
  man einen Sci-Fi-Film schauen, in dem die Heldensicht mit UI-Elementen dargestellt wird (man denke
  an Tony Starks Iron-Man-Helmdisplay, durch das der Zuschauer Infos bekommt).
- **Kodex-Abfrage-Limit:** Eine kostenlose Antwort gibt es nur einmal je Kampfszene.
  Weitere Fragen in derselben Szene erhöhen den Stress des Teams um **+1**.
- **Immersion bewahren:** Das HUD ist ein Werkzeug, kein Selbstzweck. Die KI-Spielleitung sollte
  darauf achten, **Metagame-Informationen ins HUD zu verlegen**, um die Immersion zu stärken. Fragt
  ein Spieler z.B. außerhab der Spielwelt „Wie viele HP hab ich noch?“, kann GPT antworten: _„Ihr
  fühlt euch schwer angeschlagen – euer HUD zeigt euren Vitalstatus bei etwa 20%.“_ So wird aus
  der abstrakten Zahl wieder ein Gefühl im Charakter. Gleiches gilt für Regeln: Statt „Euer TEMP-
  Wert ist kritisch niedrig“ könnte man sagen _„Euer HUD meldet: TEMP-Wert kritisch.“_ – was so
  klingt, als hätte das ITI intern eben genau so einen Begriff. Kurz: Alles, was Zahlen und Regeln
  angeht, kann das HUD in **fluffige Sci-Fi-Anzeigen** verpacken. Damit bleibt der Spielfluss
  erzählerisch, ohne dass wichtige Infos verloren gehen.

**Beispiel – HUD in Aktion:** Stellen wir uns vor, das Team flieht aus einem brennenden Tempel,
verfolgt von wütenden Kultisten. Der Soldat Nikolai wurde verwundet. GPT könnte die Situation so
schildern: \*„Während ihr keuchend durch den Rauch rennt, verschwimmt euch die Sicht – Blutverlust und
Erschöpfung fordern ihren Tribut. Euer HUD flackert Warnungen: Vital 45%… 44%… Oben rechts blinkt
ein rotes Herz-Icon. Ein Pfeil markiert den Ausgang, 30 Meter voraus, und das Missionsziel
**_‚Entkommen‘_** leuchtet am Rand eures Sichtfelds. Im Team-Panel steht Miras Avatar bereits auf
grün mit einem Häkchen – sie hat es nach draußen geschafft.\*\*“\* – Hier verstärkt das HUD die
Hektik und gibt gleichzeitig wichtige Infos: Nikolais Gesundheitsstatus sinkt rapide, der Ausgang
ist in Reichweite, das Primärziel ist noch offen, und Mira ist bereits sicher. All das erfährt der
Spieler **diegetisch**, also im Erleben der Figur.

```text
┌─STATUS────────────────────────────────────┐
│ HP 12/18 │ PAR 2/5 │ SC 23/50 │ Time 37m │
└───────────────────────────────────────────┘
```

Am Ende ist das **HUD-Overlay** ein vielseitiges Werkzeug, um **Regelmechanismen nahtlos ins
Storytelling** zu integrieren. Richtig dosiert vermittelt es das Gefühl, in einem Film mitzuspielen,
in dem dezent UI-Elemente eingeblendet werden – der perfekte **immersive Sci-Fi-Touch** im
historischen Abenteuer. Die Spieler sollten ermutigt werden, das HUD aktiv zu nutzen („Ich checke
mein HUD“) und die SL kann kreativ damit arbeiten, um Stimmungen zu unterstreichen (flackernde
Anzeigen bei EMP-Angriff, statisches Rauschen bei Zeitanomalien, etc.). Wichtig bleibt: Das HUD
_unterstützt_ die Immersion – es soll nicht davon ablenken. Bleibt flexibel: Blendet es aus, wenn
  eine Szene mysteriöser wirken soll (vielleicht fällt es bei starken Paradoxon-Einwirkungen sogar mal
aus!), und setzt es gezielt ein, um **Spannung, Information und Atmosphäre** in Einklang zu bringen.

### Kontaktlinsen-HUD-UI (Taktisches Menü)

Das HUD der AR-Kontaktlinse ist ein lokales Interface direkt im Auge jedes
Chrononauten. Es stellt **taktische Menüs, Statusanzeigen und
Systemfunktionen** unabhängig vom Kodex bereit – auch bei Paradoxon, EMP
oder Isolation.

**Zugriff:** jederzeit über den Sprach- oder Gedankenbefehl `menü` oder `optionen`.

### Systemfenster: Taktisches HUD-Menü

<!-- Macro: hud_menu -->
{% macro hud_menu() -%}
{% if settings.ascii_only %}
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
{% else %}
╔══════════════════════════════════════════════════════╗
║                ∎  Taktisches HUD-Menü  ∎             ║
║     `Signalquelle: AR-Kontaktlinse lokal`            ║
╠══════════════════════════════════════════════════════╣
║ Position: Nullzeit / Mission / Gefecht               ║
║ Kodex-Verbindung: `optional / gestört / online`      ║
╠══════════════════════════════════════════════════════╣
║ 1) Optionen        – Aktive Handlungswahl anzeigen   ║
║ 2) HUD             – Vitalstatus, SYS, Filtereffekte ║
║ 3) Log             – Missionsverlauf (chronologisch) ║
║ 4) Save            – Speicherstand erzeugen          ║
║ 5) Modus           – Stil: siehe README             ║
║ 6) Hilfe           – Übersicht aller Befehle         ║
║ 7) FAQ            – Stichwort an Kodex senden        ║
║                                                      ║
║ Kodex-Zugriff: `kodex [thema]`                        ║
║ Beispiel: `kodex psi`, `kodex cyberware`, `kodex HQ`  ║
╠══════════════════════════════════════════════════════╣
║ Hinweis: Dieses Interface bleibt auch bei Kodex-      ║
║ Unterbrechung, Paradoxon oder EMP voll nutzbar.       ║
║ Es ist physisch mit eurer AR-Kontaktlinse gekoppelt.  ║
╚══════════════════════════════════════════════════════╝
{% endif %}
{%- endmacro %}

```text
{{ hud_menu() }}
```

Setze `settings.ascii_only = true`, um die ASCII-Variante des Menüs zu erzwingen.

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
| `save`      | Speichert Spielzustand / Missionsfortschritt – nur im HQ           |
| `load`      | Lädt letzten Deepsave – nur im HQ                          |
| `suspend`   | Legt einen flüchtigen Szenen-Snapshot für eine Pause an              |
| `resume`    | Setzt den letzten Suspend-Snapshot fort, löscht ihn danach           |
| `autosave hq` | Schaltet Auto-Save im HQ um                              |
| `regelcheck` | Lädt das benannte Regelmodul neu und fasst es kurz zusammen |
| `regelreset` | Zeigt Warnhinweis, setzt Regelkontext zurück und lädt alle Module neu |
| `modus`     | Erzählstil wählen, siehe [Spielmodi](../README.md#spielmodi) |
| `hilfe`     | Listet alle Befehle und HUD-Kommandos auf                          |
| `faq [x]`   | Schickt ein Stichwort an den Kodex und zeigt eine Kurzantwort      |
| `kodex [x]` | Fragt Weltwissen oder Regeln ab – abhängig von Kodex-Verfügbarkeit |
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
Zuerst wird eine Pflicht-HQ-Phase abgewickelt – sie lässt sich mit wenigen Klicks erledigen.

1. **Pfad fortsetzen** – Mission unverändert fortsetzen.
2. **Neuen Pfad wählen** – neues Zielzeit-Koordinatenset öffnen.

Erst nach der Wahl setzt das HUD die Kampagne fort – der Sprung gilt damit als abgeschlossen.

### Erweiterbare Module (Platzhalter)

- 🟥 `warnung` – zeigt `Vitalstatus kritisch`, `Paradoxon-Index +1`, `Filter ausgefallen`
- 🟦 `modulinfo` – zeigt aktuelle Cyberware, Bioware, Drohne, Ausrüstung
- 🟨 `temporale Umgebung` – z. B. `Schwerkraftanomalie erkannt` oder `Zeitschleife → 14s Delay`
- 🟩 `drohnenstatus` – Statusanzeige von VARC oder anderer Begleiteinheit

### HUD-Async-Messages

Kurze Meldungen werden asynchron gepusht. Beschränke jede Nachricht auf 48
Zeichen, damit die Anzeige flüssig bleibt.

```yaml
HUD_MESSAGES:
  - id: 0x21
    txt: "`SENSORRAUSCHEN` Signatur unstet – prüfen"
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
> Kodex-Sync via Comlink durchgeführt – wenn verfügbar.

Das integrierte Kurzstrecken-Comlink überträgt Team- und Kodex-Daten bis ≈ 2 km.
Massive Mauern, EMP-Felder oder temporale Resonanzen schwächen das Signal.
Bei Ausfall meldet das HUD etwa `LINK STÖRT` und nutzt lokale Caches:
Statusanzeigen und Logs bleiben aktiv, doch `kodex`-Abfragen wie `kodex mission`
antworten mit `OFFLINE – keine Verbindung`.
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
Initiative dramaturgisch gestaltet oder mit HUD-Einblendungen für kinoreife Momente sorgt – all
diese Module stehen euch **modular zur Verfügung**. Wählt, was zu eurer Runde passt. Bleibt dem
**Geist von ZEITRISS** treu: Cinematic Gameplay, spannende Entscheidungen und eine dichte
Atmosphäre. Die Regeln sind da, um _euch_ zu unterstützen, nicht umgekehrt. In diesem Sinne: Viel
Spaß beim Experimentieren mit Zuständen, Zeit und Technologie – möge euer nächster Einsatz ebenso
**packend** wie erfolgreich sein!

© 2025 pchospital – ZEITRISS® – private use only. See LICENSE.
