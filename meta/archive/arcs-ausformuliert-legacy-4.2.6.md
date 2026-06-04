# Legacy: Ausformulierte Core-/Preserve-Arcs (4.2.6)

> **Archiviert am 2026-06-04.** Diese durchnummerierten Arc-Ketten (`arc_step 1..10`)
> wurden aus dem Runtime-Slot `gameplay/kreative-generatoren-missionen.md` entfernt.
>
> **Grund:** Ausformulierte Voll-Arcs verleiten die KI-SL dazu, eine feste
> Szenenkette *nachzuspielen*, statt aus Generatoren, Pools und dem
> Fremdfraktions-Generator jedes Mal eine **frische** Geschichte zu erzeugen.
> Das Antagonisten-Material (Rosters von ARGOS, CHRONOTECH, KAIROS) lebt jetzt
> als wiederverwendbarer **Fremdfraktions-Generator** weiter (siehe
> `gameplay/kreative-generatoren-missionen.md#fremdfraktions-generator`).
>
> Diese Datei ist **Dev-Referenz / Migrations-Beleg** — sie wird **nicht** in den
> KI-Wissensspeicher geladen und ist kein Spielinhalt mehr.

---

### Core-Arc Seeds {#core-arc-seeds}

```yaml
- arc_id: "Chicago1871"
  arc_step: 1
  pool: heist_pool
  title: "Brandstifter-Trupp"
  pitch: "Legt Nitrobeschleuniger unter Mrs O'Learys Scheune, ohne Zeugen."
  timeslot: "+0 h"

- arc_id: "Chicago1871"
  arc_step: 2
  pool: heist_pool
  title: "Pumpen-Manipulation"
  pitch: "Sabotiert die Dampfpumpen der Südseite, damit das Feuer sich ungehindert ausbreitet."
  timeslot: "+1 h"

- arc_id: "Chicago1871"
  arc_step: 3
  pool: heist_pool
  title: "Raubzug beim Juwelier"
  pitch: "Stehlt Diamanten im Wert von 200.000 $, während die ersten Unruhen toben."
  timeslot: "+3 h"

- arc_id: "Chicago1871"
  arc_step: 4
  pool: heist_pool
  title: "Weichen-Heist"
  pitch: "Leitet den einzigen Wasserzug um, indem ihr den Stellwerksturm übernehmt."
  timeslot: "+6 h"

- arc_id: "Chicago1871"
  arc_step: 5
  pool: heist_pool
  title: "Pinkerton-Tresorrettung"
  pitch: "Knackt einen brennenden Tresor voller Erpressungsakten."
  timeslot: "+9 h"

- arc_id: "Chicago1871"
  arc_step: 6
  pool: heist_pool
  title: "Nitro-Kähne am Fluss"
  pitch: "Sprengt die Waffenhändler-Kähne, bevor sie in der Nähe von Zivilisten explodieren."
  timeslot: "+12 h"

- arc_id: "Chicago1871"
  arc_step: 7
  pool: heist_pool
  title: "Schützenduell auf den Dächern"
  pitch: "Schaltet ein rivalisierendes Schatten-Team aus, das einen Fluchtkorridor deckt."
  timeslot: "+16 h"

- arc_id: "Chicago1871"
  arc_step: 8
  pool: heist_pool
  title: "Zeppelin-Start"
  pitch: "Verladet Kunstschätze auf einen geheimen Zeppelin bei Sturm."
  timeslot: "+20 h"

- arc_id: "Chicago1871"
  arc_step: 9
  pool: heist_pool
  title: "Versicherungsbetrugsfalle"
  pitch: "Deckt gefälschte Forderungen in einer halb eingestürzten Bank auf."
  timeslot: "+24 h"

- arc_id: "Chicago1871"
  arc_step: 10
  pool: heist_pool
  title: "Chrono-Safedrop"
  pitch: "Bergt den zeitcodierten Safe, bevor das Abrisskommando alle Spuren verwischt."
  timeslot: "+30 h"

- arc_id: "Peking1908"
  arc_step: 1
  pool: black_ops_pool
  title: "Kaiserlicher Goldzug"
  pitch: "Entert den gepanzerten Geldzug - Zukunftsagenten wollen Qing-Finanzen an Warlords umleiten."
  timeslot: "Day-1 Dawn"

- arc_id: "Peking1908"
  arc_step: 2
  pool: black_ops_pool
  title: "Tesla-Boxer-Labor"
  pitch: "Zerstört eine geheime Coilgun-Anlage - Chrono-Techniker rüsten Boxer-Rebellen auf."
  timeslot: "Day-1 Noon"

- arc_id: "Peking1908"
  arc_step: 3
  pool: black_ops_pool
  title: "Jade-Chronometer"
  pitch: "Stehlt ein codiertes Zeitrelikt aus dem Uhrenturm, das kaiserliche Zeitlinien berechnet."
  timeslot: "Day-1 Dusk"

- arc_id: "Peking1908"
  arc_step: 4
  pool: black_ops_pool
  title: "Attentat bei der Oper"
  pitch: "Verhindert das Attentat auf einen britischen Attaché - Gegner will internationalen Konflikt forcieren."
  timeslot: "Day-1 Night"

- arc_id: "Peking1908"
  arc_step: 5
  pool: black_ops_pool
  title: "Lotus-Drogenrazzia"
  pitch: "Brennt das Drogenlabor eines Warlords nieder; Schmuggelerlöse finanzieren Zeitoperationen."
  timeslot: "Day-2 Dawn"

- arc_id: "Peking1908"
  arc_step: 6
  pool: black_ops_pool
  title: "Fenghuang-Flugtest"
  pitch: "Testet ein Proto-Ornithopter - geplanter Technologietransfer aus der Zukunft."
  timeslot: "Day-2 Noon"

- arc_id: "Peking1908"
  arc_step: 7
  pool: black_ops_pool
  title: "Argus-Ballon-Abgriff"
  pitch: "Hackt das optische Telegraphenrelais, um falsche Aufstandsberichte zu senden."
  timeslot: "Day-2 Afternoon"

- arc_id: "Peking1908"
  arc_step: 8
  pool: black_ops_pool
  title: "Tunnelspektrenjagd"
  pitch: "Jagt einen Chronoschmuggler, der Rebellen mit Zukunftstechnik versorgt, durch Metro-Tunnel."
  timeslot: "Day-2 Dusk"

- arc_id: "Peking1908"
  arc_step: 9
  pool: black_ops_pool
  title: "Blutschriftrollen-Auktion"
  pitch: "Tauscht ein angeblich verfluchtes Dokument aus - tatsächlich ein zeitgeladenes Schriftstück."
  timeslot: "Day-2 Midnight"

- arc_id: "Peking1908"
  arc_step: 10
  pool: black_ops_pool
  title: "Drachentor-Abriegelung"
  pitch: "Versiegelt die kaiserliche Gruft, bevor ein rivalisierendes Zeitteam Qing-Relikte manipuliert."
  timeslot: "Day-3 Dawn"

- arc_id: "Orbital2220"
  arc_step: 1
  pool: future_pool
  title: "Mondaufzug-Raubzug"
  pitch: "Kapert eine Lastkabine am Aufzugskabel in 70 km Höhe."
  timeslot: "T-4 h"

- arc_id: "Orbital2220"
  arc_step: 2
  pool: future_pool
  title: "Massentreiber-Katastrophe"
  pitch: "Sabotiert die Asteroiden-Schienenkanone vor dem illegalen Abschuss."
  timeslot: "T-1 h"

- arc_id: "Orbital2220"
  arc_step: 3
  pool: future_pool
  title: "EVA-Luftkampf"
  pitch: "Besiegt Exoanzug-Söldner in einem schwerelosen Trümmerfeld."
  timeslot: "T + 2 h"

- arc_id: "Orbital2220"
  arc_step: 4
  pool: future_pool
  title: "Geisel im Grünen Ring"
  pitch: "Befreit ein Biotech-Gewächshaus, das bei 0,8 G rotiert."
  timeslot: "T + 5 h"

- arc_id: "Orbital2220"
  arc_step: 5
  pool: future_pool
  title: "Quanten-Börsenhack"
  pitch: "Schleust einen falschen Algorithmus in ein 0,25-s-Latenz-Fenster ein."
  timeslot: "T + 8 h"

- arc_id: "Orbital2220"
  arc_step: 6
  pool: future_pool
  title: "Frachtschleuder-Duell"
  pitch: "Fechtet in einer rotierenden Trommel, während die Gravitation schwankt."
  timeslot: "T + 12 h"

- arc_id: "Orbital2220"
  arc_step: 7
  pool: future_pool
  title: "Trümmer-Schrotflinte"
  pitch: "Manövriert durch die Kessler-Wolke, um einen Überläufer bei 800 m/s zu retten."
  timeslot: "T + 18 h"

- arc_id: "Orbital2220"
  arc_step: 8
  pool: future_pool
  title: "Fusionskern-Überlastung"
  pitch: "Haltet einen katastrophalen Ausbruch lange genug auf, um das Habitat zu evakuieren."
  timeslot: "T + 22 h"

- arc_id: "Orbital2220"
  arc_step: 9
  pool: future_pool
  title: "Geisterknoten-Verfolgung"
  pitch: "Verfolgt einen rivalen Chrononauten durch ein verlassenes Kommunikationsnetz."
  timeslot: "T + 26 h"

- arc_id: "Orbital2220"
  arc_step: 10
  pool: future_pool
  title: "Flucht in der Sturzkapsel"
  pitch: "Stürzt in einer Einsatztkapsel frei zum Pazifik hinab und stört dabei alle Tracker."
  timeslot: "T + 30 h"
# ─────────────────────────────────────────────────────────────
# CORE-ARC 4 - BERLIN 1961 "Mauerschatten"
# Pool: heist_pool  - Spionage-Heist im Kalten Krieg
# ─────────────────────────────────────────────────────────────
- arc_id: "Berlin1961"
  arc_step: 1
  pool: heist_pool
  title: "Stromausfall-Geister"
  pitch: "Sabotiere das Umspannwerk Treptow, um die Sektorgrenze in Dunkelheit zu legen."
  timeslot: "13.08.61 02:30"

- arc_id: "Berlin1961"
  arc_step: 2
  pool: heist_pool
  title: "Tunnel-Einbruch"
  pitch: "Sprenge verdeckt einen Abwasser-Blindschacht als Fluchttunnel-Zugang."
  timeslot: "+3 h"

- arc_id: "Berlin1961"
  arc_step: 3
  pool: heist_pool
  title: "Aktenzug 'Topas'"
  pitch: "Stehle STASI-Abschriften westlicher Informanten aus Bezirksamt Mitte."
  timeslot: "+6 h"

- arc_id: "Berlin1961"
  arc_step: 4
  pool: heist_pool
  title: "Mauer-Kran-Kidnapping"
  pitch: "Entführe einen Grenzkran samt Bauplan - 20 m über Niemandsland."
  timeslot: "+10 h"

- arc_id: "Berlin1961"
  arc_step: 5
  pool: heist_pool
  title: "Zementsprengung"
  pitch: "Unterlaufe Vopo-Patrouille und mische Schwell-Sprengstoff in Betonmischer."
  timeslot: "+14 h"

- arc_id: "Berlin1961"
  arc_step: 6
  pool: heist_pool
  title: "Radio-Funkpirat"
  pitch: "Kapere eine mobile RIAS-Antenne und sende Desinfo für 17 Minuten."
  timeslot: "+18 h"

- arc_id: "Berlin1961"
  arc_step: 7
  pool: heist_pool
  title: "Checkpoint Shadow-Swap"
  pitch: "Tausche gefälschte Pass-Sets unter Scheinwerferlicht von Checkpoint Charlie."
  timeslot: "+22 h"

- arc_id: "Berlin1961"
  arc_step: 8
  pool: heist_pool
  title: "Gleisbett-Himmelstürmer"
  pitch: "Nutze aufgegebene S-Bahn-Gleise als Flucht-Rampe auf britischen Hubschrauber."
  timeslot: "+26 h"

- arc_id: "Berlin1961"
  arc_step: 9
  pool: heist_pool
  title: "Zwischenlager NVA"
  pitch: "Befreie westliche Doppelagentin aus improvisierter Turnhallen-Zelle."
  timeslot: "+30 h"

- arc_id: "Berlin1961"
  arc_step: 10
  pool: heist_pool
  title: "Vorhang-Finale"
  pitch: "Zünde Ablenkungs-Feuerwerk entlang der Bernauer Straße, um Rückzug zu decken."
  timeslot: "+34 h"

# ─────────────────────────────────────────────────────────────
# CORE-ARC 5 - MARS 2287 "Red Horizon"
# Pool: future_pool - 10 forward-only Missionen (12 Szenen pro Job)
# ─────────────────────────────────────────────────────────────
- arc_id: "Mars2287"
  arc_step: 1
  pool: future_pool
  title: "Kuppel-Blackout"
  pitch: "Stelle Notstrom für Ares-7 wieder her, während Thrynn erste Wohnblöcke durchbrechen."
  timeslot: "T-0 h"          # Alarmminute

- arc_id: "Mars2287"
  arc_step: 2
  pool: future_pool
  title: "Evakuierungs-Himmelsschacht"
  pitch: "Eskortiere Forscher Dr. Selim zu Orbital-Ascender, unter Dauerfeuer von Chitin-Spitter."
  timeslot: "+2 h"

- arc_id: "Mars2287"
  arc_step: 3
  pool: future_pool
  title: "Datenkern-Heist"
  pitch: "Hacke Forschungs-Mainframe, sichere oder vernichte kontroverse Gen-Logs."
  timeslot: "+4 h"

- arc_id: "Mars2287"
  arc_step: 4
  pool: future_pool
  title: "Perimeter-Lockdown"
  pitch: "Aktiviere alte Verteidigungs-Sentinel-Bots, um Kuppel-Rand abzuriegeln."
  timeslot: "+6 h"

- arc_id: "Mars2287"
  arc_step: 5
  pool: future_pool
  title: "Lavatunnel-Abstieg"
  pitch: "Fahre Cargo-Lift 12 km tief in vergessene Terraformer-Stollen."
  timeslot: "+9 h"

- arc_id: "Mars2287"
  arc_step: 6
  pool: future_pool
  title: "Königin-Falle"
  pitch: "Setze Pheromon-Beacon, um Schwarm in Nebenkaverne zu locken - Sprengfalle vorbereiten."
  timeslot: "+12 h"

- arc_id: "Mars2287"
  arc_step: 7
  pool: future_pool
  title: "Schattentor Theta"
  pitch: "Entdecke uralten Megakomplex: Basalt-Portale, humanoide Glyphen, leere Wohnkuppeln."
  timeslot: "+15 h"

- arc_id: "Mars2287"
  arc_step: 8
  pool: future_pool
  title: "Labor Eos-Zero"
  pitch: "Enthülle, dass Thrynn Einheits-Genpool-Tests waren - Option: Datensätze stehlen oder löschen."
  timeslot: "+18 h"

- arc_id: "Mars2287"
  arc_step: 9
  pool: future_pool
  title: "Altar der Larven"
  pitch: "Boss-Fight gegen Leviathan-Brutbehälter; installiere Plasmabombe oder scanne Biokern."
  timeslot: "+21 h"

- arc_id: "Mars2287"
  arc_step: 10
  pool: future_pool
  title: "Roter Exodus"
  pitch: "Sprint zurück zur Oberfläche - Schwarmflut, fallende Drucktore, Start eines Sandorkan-Shuttles."
  timeslot: "+24 h"

# ─────────────────────────────────────────────────────────────
# CORE-ARC 6 - SEIDENSTRASSE 1280 "Wüsten-Caravan Noir"
# Pool: black_ops_pool  - Mittelalter-Heist mit Steampunk-Twist
# ─────────────────────────────────────────────────────────────
- arc_id: "Silk1280"
  arc_step: 1
  pool: black_ops_pool
  title: "Karakorum-Falschfracht"
  pitch: "Schmuggelt euch als Teppichhändler in einen mongolischen Steuerkonvoi."
  timeslot: "Tag 0 Morgengrauen"

- arc_id: "Silk1280"
  arc_step: 2
  pool: black_ops_pool
  title: "Falke-im-Wind"
  pitch: "Stiehl Code-Botschaft von Yam-Boten mittels trainiertem Jagdfalken."
  timeslot: "+6 h"

- arc_id: "Silk1280"
  arc_step: 3
  pool: black_ops_pool
  title: "Oasen-Signal"
  pitch: "Leg toxische Nebelkerzen in Händlerlager, um Wachen auszuschalten; defekter
    Funkmast sendet permanent Notrufe."
  timeslot: "+12 h"

- arc_id: "Silk1280"
  arc_step: 4
  pool: black_ops_pool
  title: "Kupfer-Automaton"
  pitch: "Repariere heimlich einen Uhrwerk-Golem, lasse ihn Tor aufbrechen."
  timeslot: "+18 h"

- arc_id: "Silk1280"
  arc_step: 5
  pool: black_ops_pool
  title: "Sandsturm-Abzweig"
  pitch: "Leite Karawane mittels gefälschtem Sternenkompass in Seitenschlucht."
  timeslot: "+22 h"

- arc_id: "Silk1280"
  arc_step: 6
  pool: black_ops_pool
  title: "Dschinn-Gerücht"
  pitch: "Nutze Holo-Illusion, um Gerüchte über Wüstengeist zu schüren - Moralbruch."
  meta_introspection: true
  timeslot: "+26 h"

- arc_id: "Silk1280"
  arc_step: 7
  pool: black_ops_pool
  title: "Sattel-Sprengfalle"
  pitch: "Platziere Pulverbeutel in Lastkamel-Sattel, zünde bei Stadttor."
  timeslot: "+30 h"

- arc_id: "Silk1280"
  arc_step: 8
  pool: black_ops_pool
  title: "Karawanserai-Schatten"
  pitch: "Entführe vergifteten Diplomaten zur Wüstenklinik - verdeckte Heilung."
  timeslot: "+34 h"

- arc_id: "Silk1280"
  arc_step: 9
  pool: black_ops_pool
  title: "Schmelzofen-Hehler"
  pitch: "Zwinge Waffenschmiede, geraubtes Gold sofort einzuschmelzen."
  timeslot: "+38 h"

- arc_id: "Silk1280"
  arc_step: 10
  pool: black_ops_pool
  title: "Kometen-Signal"
  pitch: "Projiziere künstlichen Kometen via Ballon-Spiegel als Zeichen zum Abzug."
  timeslot: "+42 h"
# -------------------------
# CORE-ARC 7 - TSCHERNOBYL 1986 "KAIROS Collapse"
# Pool: heist_pool - Reaktorunfall historisch korrekt eintreten lassen (Trigger)
# -------------------------
Dieser zehnteilige Trigger-Arc begleitet den Reaktor von frühen
Bauvorbereitungen über die fatale Nacht bis zur Vertuschung. Jede Mission
knüpft direkt an die vorherige an und lässt die Agenten mehrfach eingreifen.
- arc_id: "Chernobyl86"
  arc_step: 1
  pool: heist_pool
  title: "Foundation Crack"
  pitch: "Prüfbeton sabotieren; Kampf gegen KAIROS-Baupioniere in überfluteter Baugrube."
  timeslot: "1972-10-01"

- arc_id: "Chernobyl86"
  arc_step: 2
  pool: heist_pool
  title: "Control Logic"
  pitch: "Fehlerhaften Steuercode einspielen; NetSec-Trupp und Samurai (16. Jh.) mit Bioware greifen an."
  timeslot: "1975-07-14"

- arc_id: "Chernobyl86"
  arc_step: 3
  pool: heist_pool
  title: "False Green"
  pitch: "Dosimeterdaten fälschen; Med-Unit jagt verstrahlten Arbeiter durch Rohrlabyrinth."
  timeslot: "1982-09-09"

- arc_id: "Chernobyl86"
  arc_step: 4
  pool: heist_pool
  title: "Valve Ghost"
  pitch: "Ersatzdichtung entfernen; Micro-Bot-Attacke im dampfigen Tunnel abwehren."
  timeslot: "1984-04-27"

- arc_id: "Chernobyl86"
  arc_step: 5
  pool: heist_pool
  title: "Audit Silence"
  pitch: "Prüfdokumente vernichten; Feuergefecht mit KAIROS-Extraction-Team im Archiv."
  timeslot: "1985-01-05"

- arc_id: "Chernobyl86"
  arc_step: 6
  pool: heist_pool
  title: "Night-Shift"
  pitch: "Unerfahrene Crew einschleusen; HR-Spoofer löst Treppenhaus-Schusswechsel aus."
  timeslot: "1986-04-25 18:00"

- arc_id: "Chernobyl86"
  arc_step: 7
  pool: heist_pool
  title: "Procedure 200/45"
  pitch: "Checkliste kürzen; Nahkampf am Leitpult gegen KAIROS-Lead-Engineer."
  timeslot: "1986-04-25 23:10"

- arc_id: "Chernobyl86"
  arc_step: 8
  pool: heist_pool
  title: "Core Burst"
  pitch: "AZ-5 auslösen; Bioware-Samurai attackiert im rot flackernden Steuerstand."
  timeslot: "1986-04-26 01:23"

- arc_id: "Chernobyl86"
  arc_step: 9
  pool: heist_pool
  title: "Black Rain"
  pitch: "Feuerwehr fehlleiten; Sniper-Duo jagt Drohnen zwischen radioaktiven Trümmern."
  timeslot: "1986-04-26 02:04"

- arc_id: "Chernobyl86"
  arc_step: 10
  pool: heist_pool
  title: "Evidence Chain"
  pitch: "Bericht auf menschlichen Fehler lenken; Jagd auf Spin-Doctor durch Ministerialgänge."
  timeslot: "1986-05-02"
```

#### KAIROS Dynamics Einsatzprofile

| Rolle       | Kern-Loadout                                 | Taktik                             |
| ----------- | -------------------------------------------- | ---------------------------------- |
| Baupionier  | Hydraulik-Hämmer, Ballistikmantel            | Nahkampf, Gelände-Kontrolle        |
| Hack-Rigger | Cyberdeck T2, Shock-Pistol                   | Netzangriffe, Drohnen-Steuerung    |
| Samurai     | Historischer Samurai mit Bioware-Verstärkung | Blitzschnelle Klingenstürme        |
| Sniper      | Gauss-Precision Rifle, Chamäleon-Cloak       | Fernfeuer, Drohnen-Barrage         |
| Spin-Doctor | Voice-Mod, Fake-Creds, Gel-Ruger             | Social-Manipulation, Rückfallebene |
| Humine      | Sensorimplantate, Chitinpanzer               | Gruppenunterstützung und Späher    |

# ─────────────────────────────────────────────────────────────

# PRESERVE-ARC - ABLE ARCHER '83

# Pool: heist_pool - nukleare Fehldeutung verhindern

# Gegnerfraktion: CHRONOTECH Genesis - biogenetischer Zeit-Megakon

# ─────────────────────────────────────────────────────────────

- arc_id: "AbleArcher83"
  arc_step: 1
  pool: heist_pool
  title: "Red Tape"
  pitch: >
  NATO-UDSSR Hotline stabilisieren; 3 Neandertaler-Bruiser und Urwolf-Tracker
  sabotieren Glasfaser - Nahkampf im Kabelschacht.
  timeslot: "1977-03-18"

- arc_id: "AbleArcher83"
  arc_step: 2
  pool: heist_pool
  title: "NORAD 40/15"
  pitch: >
  Alarm-Bug patchen (darf nicht feuern); CT-NetSec-Team mit Cyber-Samurai-Bodyguard
  hackt NORAD-Mainframe - Feuergefecht & Netz-Duel.
  timeslot: "1979-11-09"

- arc_id: "AbleArcher83"
  arc_step: 3
  pool: heist_pool
  title: "SAMURAI Key"
  pitch: >
  Samurai Shimada Gorō rekrutieren; Extraction-Spezialisten und Urwolf zur Fährtensuche
  - Katana-Duel im Frachtlift.
    timeslot: "1980-06-12"

- arc_id: "AbleArcher83"
  arc_step: 4
  pool: heist_pool
  title: "Solar Flare"
  pitch: >
  Schutzcode in Satellit laden; CT-Rigger-Duo mit Spreng-Drohnen
  stört Panel-Zugriff - Roof-Gunfight.
  timeslot: "1981-01-21"

- arc_id: "AbleArcher83"
  arc_step: 5
  pool: heist_pool
  title: "Black Bear"
  pitch: >
  Ersatz-Kosmos-1382 hochbringen; Neandertaler-Saboteure überfallen Konvoi, Urwolf spürt Route auf
  - Truck-Ambush.
    timeslot: "1982-02-22"

- arc_id: "AbleArcher83"
  arc_step: 6
  pool: heist_pool
  title: "Able Brief"
  pitch: >
  Leak echter Manöverdaten sichern; CT-Face plus Assault-Mercs
  stehlen Diskette - Archiv-Shootout.
  timeslot: "1983-11-07 08:00"

- arc_id: "AbleArcher83"
  arc_step: 7
  pool: heist_pool
  title: "Ghost Silos"
  pitch: >
  Autorisierung gegen Hack schützen; CT-Combat-Team bohrt Datenleitung, Urwolf bewacht Perimeter
  - Nahkampf am Silo-Tor.
    timeslot: "1983-11-07 19:00"

- arc_id: "AbleArcher83"
  arc_step: 8
  pool: heist_pool
  title: "Signal Down"
  pitch: >
  Untersee-Kabel reparieren; Rigger mit Mini-U-Boot und Tauch-Mercs
  zünden Sprengsatz - Sturm-Taucher-Gefechte.
  timeslot: "1983-11-08 02:00"

- arc_id: "AbleArcher83"
  arc_step: 9
  pool: heist_pool
  title: "Petrov Guard"
  pitch: >
  Oberst Petrov beschützen; Kill-Cell mit Bruiser, Urwolf und Sniper
  stürmt Wohnung - CQB-Fight.
  timeslot: "1983-11-09 16:00"

- arc_id: "AbleArcher83"
  arc_step: 10
  pool: heist_pool
  title: "Blue Silence"
  pitch: >
  Sim-Signal eines Trainingssenders als 'Übung' kennzeichnen; CT-Elite-Handler und
  Heavy-Merc-Squad greifen an
  - finale Mehr­ebenen-Schlacht (Gorō als Ally).
    timeslot: "1983-11-11 00:00"

---

#### Gegner-Einheiten (kompakt)

| Einheit                     | Kern-Rolle          | Stichworte\*                    |
| --------------------------- | ------------------- | ------------------------------- |
| **Neandertaler-Bruiser**    | Breacher            | STR 7, Keule W⁶+2, Resilienz    |
| **Urwolf-Bluthund**         | Spür- & Schock­hund | Geruch +3, Biss W⁶, Furcht-Aura |
| **Cyber-Samurai-Bodyguard** | Elite-Melee         | Katana T2, Reflex-Booster       |
| **CT-NetSec-Hacker**        | Netzkampf           | Cyberdeck T2, Shock-Pistol      |
| **Assault-Merc**            | Ranged DPS          | MP7-SD, Ballistik-Mantel        |
| **Rigger / Drone-Op**       | Support             | Mini-Drohnen (Recon/Spreng)     |
| **Elite-Handler** (Finale)  | Commander           | CHA 6, Tact-Link, Gel-Ruger     |

- _Schaden & SG laut ZEITRISS-Core; Urwolf bleibt einziges Tier-Hybrid._

---

### Stil-Reminder

- **Urwolf** tritt nur 1-2× pro Mission als Spur- oder Schock­einheit auf -
  Aha-Effekt bleibt erhalten, kein Overload.
- Kämpfe bleiben chrompunk-artig: Chrom-Bodyguards, Netz-Support, schnelle,
  harte Feuer­gefechte.
- **Samurai Shimada Gorō** begleitet die Gruppe ab Mission 3 (Katana T2,
  einmal pro Szene Riposte-Konter).
- **Paradoxon** stagniert oder sinkt ausschließlich, wenn CT-Genesis kurz davor
  ist, den Atomkrieg auszulösen.

Damit habt ihr denselben Able-Archer-Preserve-Bogen, **nur mit dem Urwolf als ikonischem Hybrid**,
sonst reine Humanoiden-Gefechte - perfekt dosiert für euer gewünschtes ZEITRISS-Feeling.

# ─────────────────────────────────────────────────────────────

# PRESERVE-ARC - SALAMIS 480 v. Chr.

# Pool: heist_pool - Seesieg sichern

# Gegnerfraktion: ARGOS Venture - transtemporaler Megakon

# ─────────────────────────────────────────────────────────────

- arc_id: "Salamis480"
  arc_step: 1
  pool: heist_pool
  title: "Dry Dock"
  pitch: "Brandpfeil-Lieferung sabotieren; ARGOS-Bruiser und Urwolf eskortieren Waffen."
  timeslot: "480-08-26"
- arc_id: "Salamis480"
  arc_step: 2
  pool: heist_pool
  title: "Copper Quill"
  pitch: "Orakelrolle fälschen - Text muss 'Seemauern retten Hellas' lauten; Face und Hack-Monk säen Panik."
  timeslot: "480-08-27"
- arc_id: "Salamis480"
  arc_step: 3
  pool: heist_pool
  title: "Phalanx Key"
  pitch: "Sparta zu 50 Triremen überreden; Silver-Tongue besticht den Rat - Rededuell."
  timeslot: "480-08-31"
- arc_id: "Salamis480"
  arc_step: 4
  pool: heist_pool
  title: "Aegis Node"
  pitch: "Feuerkette bewahren; Rigger mit Kupfer-Ornithopter zündet falsches Signal."
  timeslot: "480-09-02"
- arc_id: "Salamis480"
  arc_step: 5
  pool: heist_pool
  title: "Iron Marble"
  pitch: "Ballista-Vorräte vernichten; ARGOS-Söldner tarnen sich als Bauern - Lagerbrand."
  timeslot: "480-09-10"
- arc_id: "Salamis480"
  arc_step: 6
  pool: heist_pool
  title: "Owl Cipher"
  pitch: "Seekriegs-Kodexe schützen; Bruiser-Team mit Urwolf stürmt die Krypta."
  timeslot: "480-09-18"
- arc_id: "Salamis480"
  arc_step: 7
  pool: heist_pool
  title: "Channel Ghost"
  pitch: "Seil-Boom sabotieren; Combat-Divers legen Minen im Engpass."
  timeslot: "480-09-20"
- arc_id: "Salamis480"
  arc_step: 8
  pool: heist_pool
  title: "Red Keel"
  pitch: "Navigator-Dronen von Xerxes' Flaggschiff entfernen; Samurai Gorō hilft auf Deck."
  timeslot: "480-09-21"
- arc_id: "Salamis480"
  arc_step: 9
  pool: heist_pool
  title: "Mist Spear"
  pitch: "Admiralsflagge sichern; Sniper auf Nebelschiff und Urwolf an der Kette."
  timeslot: "480-09-22"
- arc_id: "Salamis480"
  arc_step: 10
  pool: heist_pool
  title: "Azure Break"
  pitch: "Xerxes' Evakuierung vereiteln; Elite-Handler und Heavy-Mercs decken den König."
  timeslot: "480-09-22"

---

## Aus gameplay/kampagnenstruktur.md entfernt (2026-06-04)

> Diese beiden Blöcke standen in der Kampagnenstruktur und wurden aus demselben
> Grund entfernt: vorformulierter Plot statt generativem Gerüst. Die generische
> Regel **Adaptive Opposition** wurde NICHT archiviert, sondern als
> wiederverwendbare Regel in `kampagnenstruktur.md#adaptive-opposition` behalten.
> Das ARGOS-Roster lebt im Fremdfraktions-Generator weiter.

### Preserve-Arc Salamis 480 v. Chr. (Voll-Block)

##### Preserve-Arc Salamis 480 v. Chr. {#preserve-arc-salamis-480}

```yaml
# gameplay/kampagnenstruktur.md - Abschnitt Preserve-Arc Salamis 480 v. Chr.
title: "Preserve-Arc Salamis 480 v. Chr."
id: EX-PRES-0480-SAL
type: core_op
preserve_only: true
version: 4.2.6
```

**Epoche:** Klassisches Griechenland & Perserkriege
**Beinahe-Katastrophe:** Die vereinte griechische Flotte siegt knapp bei Salamis.
Wäre Xerxes I. dort erfolgreich gewesen, hätte das Achämeniden-Reich die Ägäis dominiert -
Demokratie und Philosophie, wie wir sie kennen, wären nie entstanden.
**Auftrag:** Der griechische Sieg muss erhalten bleiben.

**Gegnerfraktion:** **ARGOS Venture** - ein transtemporaler Hochrisiko-Megakon.
Die Investoren setzen auf eine "Persische Weltordnung" und versuchen daher,
verdeckt einzugreifen. So wollen sie später an einer exklusiven
Bronze-Silk-Road-Zeitlinie verdienen.

> **Creature-Limit:** einziges Bio-Hybrid bleibt der **Urwolf-Bluthund**
> (zeitversetzter Riesenwolf). Keine weiteren Tiere.
> **Chrompunk-Flair:** Chrom-Söldner im Linothorax-Kevlar,
> Projektionshelme mit Hoplit-Kamm, "Bronze"-Smartguns und Wachstafel-Cyberdecks.

_Die SL generiert die Einsatz-Szenen dieses Arcs frei aus dem
Core-Briefing-Baukasten und dem Core-12-Step-Template
(`gameplay/kreative-generatoren-missionen.md`). Schauplatz-Kette,
Gegner-Roster, Stil-Notizen und Arc-Outcome bilden den kanonischen Rahmen._

### Gegner-Roster (kompakt)

| Einheit                   | Loadout                                  | Kern-Taktik                |
| ------------------------- | ---------------------------------------- | -------------------------- |
| **ARGOS-Bruiser**         | Linothorax-Kevlar, Smart-Gladius, Schild | Breach & Schildwall        |
| **Urwolf-Bluthund**       | Hybrid-Tracker                           | Spur, Biss W⁶, Furcht      |
| **Hack-Monk**             | Wachstafel-Deck, Shock-Stylus            | Matrix-Scrying, Propaganda |
| **Silver-Tongue Face**    | Vox-Mod, Chameleon-Himation              | Bestechung, Crowd-Control  |
| **Drohnen-Rigger**        | Kupfer-Ornithopter, Mini-Hydra-Bots      | Luft-Recon, Sprengungen    |
| **Samurai-Bodyguard**     | Katana T2, Reflex-Boost                  | Elite-Melee                |
| **Sniper (Gastraphetes)** | Repetier-Bolzenwerfer, Optik-Aug         | Fernfeuer                  |
| **Heavy-Merc**            | Hoplon-Drohnen, Pilum-Launcher           | Schildwall-Advance         |
| **Elite-Handler**         | Takt-Leitung, Gel-Stab                   | Kommando, Moral-Boost      |

### Stil- und Regel-Notizen

- **Urwolf** taucht maximal zweimal pro Mission auf (Spür- oder Angsteinheit).
- **Samurai Shimada Gorō** stößt in Mission 8 zum Team - sein Katana schneidet antike Bronze mühelos.
- **Chrom trifft Antike:** Bronze-Kupfer-Optik, aber Smart-Mechanik; der Repetier-Gastraphetes
  spielt sich wie eine Sturm-Armbrust.
- **Paradoxon-Trigger:** nur, wenn ARGOS entscheidend persische Siege erzwingt (flüchtige Persian-Win-Branch).

**Arc-Outcome**

- Erfolg → Griechischer Sieg bleibt, Demokratiepfad stabil, +2 Ruf bei Kodex, 600-800 CU Gesamtertrag.
- Scheitern → "Persische Weltordnung" → ClusterCreate(), Zeitlinie kollabiert, Kampagne-Reset empfohlen.

#### Dev-Check-Liste

- Paradoxon-Tracker 0-5 bleibt bestehen.
- Bei Px 5 `roll(1d2)` Seeds im aktuellen `epoch_id` anlegen.
- Rift-Pool als Array: `seed_id` und
  `status(locked_until_episode_end/open/closed)`.
- Schwierigkeit = `base_dc + len(campaign.rift_seeds)`.
- CU = `base_cu * (1 + len(campaign.rift_seeds)*0.2)`.
- High-Level-Ökonomie: Modul 15 listet Richtwerte für Level 100/400/1000
  (Belohnung vs. Kosten/Sinks); Hazard-Pay und Seed-Multiplikator bleiben
  identisch.
- Side-Op erzeugt ein Paramonster nach dem obigen Template im aktuellen `epoch_id`.
- Bei Rift-Ops die `campaign.scene` bis **14** verfolgen und erst dann abschließen.
- Rift-Operationen erhöhen den Paradoxon-Index nicht und schließen sich nach dem Verlassen automatisch.
  Artefaktkontakt kann dennoch Punkte auslösen.
- Artefakte handelbar wie Gear: Research-/Archivwerte dokumentieren Fortschritt;
  prozentuale Buff-Staffel (≈ 10 / 15 / 20-25 %) hält Endgame-Balancing stabil.

#### Adaptive Opposition

Steigt der Paradoxon-Index während einer Mission auf 3 oder höher, reagieren
Antagonisten aktiver. Jeder wichtige Gegner erhält einmalig einen kleinen
taktischen Vorteil - etwa einen Drohnen-Sweep oder einen vorbereiteten
Hinterhalt. Diese Routine verändert den Grund-Schwierigkeitsgrad nicht, sorgt
aber für glaubwürdig agierende Gegenspieler.


### Staffel-Skeleton "Glanzlicht"

| Ep  | Phase | Arbeitstitel             | Kernmechanik                                    |
| --- | ----- | ------------------------ | ----------------------------------------------- |
| 1   | Core  | Lieferung aus dem Nichts | Phantom-Stahllieferung (Logistik vs. Sabotage)  |
| 2   | Core  | Planer unter Zeitdruck   | Social-Heist im Baubüro                         |
| 3   | Core  | Kanal unter dem Palast   | Understreet-Einbruch                            |
| 4   | Core  | Der Schatten der Zukunft | Verfolgung / Gefecht mit Fremdfraktion          |
| 5   | Core  | Die Nacht der Bauprobe   | Sicherung oder Einbau letzter Zukunfts-Bauteile |
| 6   | Core  | Bauabnahme               | Staffel-Finale: Showdown Bewahren vs. Auslösen  |

Im Finale treffen beide Philosophien direkt aufeinander: Die Chrononauten wollen
das Ereignis bewahren, die gegnerische Fraktion versucht es auszulösen (oder
umgekehrt, je nach Kampagnenausrichtung).

Rifts spawnen separat zwischen diesen Episoden und werden einzeln gelistet.

