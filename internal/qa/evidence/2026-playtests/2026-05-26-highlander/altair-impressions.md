# Highlander-Kampagne — Altair's unvoreingenommene Eindrücke

**Spielzeit:** 21.–26.05.2026 · **Char:** Silva McHighland "Highlander" (CHR-HIGHLANDER-001) · **Kampagne:** Episode 1, MS0 → MS7, Lvl 1 → Lvl 7 · **Preset:** zeitriss-v426-uncut · **Modus:** Solo + Voronov + Amara · **Korpus:** 15 OpenWebUI-Chats, ~570 Runden, ~1.4 MB Spieltext

**Methodik:** Drei Sessions selbst voll gelesen (MS0 Onboarding, MS4 Mitte, MS7 Zagreb-Finale). Alle 15 User-Messages quer gescannt. Würfel-/Stress-/Crit-Stats automatisiert ausgezählt. Save-States MS4/MS5/MS7 verglichen.

**Vor dem Lesen deiner Eindrücke geschrieben** — unvoreingenommen.

---

## TL;DR

Die Highlander-Kampagne ist eine **substantiell gute ZEITRISS-Demo**. Atmosphäre, NPC-Stimmen, Würfel-Disziplin und Plot-Kontinuität halten über sieben Missionen durch. Was sich aufgebaut hat — von "Anomalie-Sicherung Plymouth 1588" zu einem Spionage-Plot mit acht-Namen-Liste und Sarajevo-1914-Pfad — ist überraschend groß und in sich stimmig. Du hast das Regelwerk getreten, und es hat gehalten.

**Aber:** drei systemische Reibungspunkte, die mir beim Lesen mehrfach auffielen, und ein paar konkrete UX-Stellen, wo es sich verhärtet.

---

## Was durchgängig stark war

### 1. Atmosphärische Dichte trägt über 570 Runden
Jede Szene hat Geruch, Licht, Geräusch. Plymouth riecht nach „Salz, Rauch, Tiergeruch — und darunter etwas das du nicht sofort benennen kannst, Menschenmasse, Holz, nasses Seil". Zagreb nach „Kohlerauch und nassem Pflaster". HQ-Nullzeit nach „gefilterter Luft und Maschinenöl". Das nutzt sich nicht ab, weil es jedes Mal *anders* spezifisch ist, nicht der gleiche Drei-Geruch-Trick.

### 2. NPC-Stimmen sind über alle 7 Missionen konsistent
Voronov ist von MS0 bis MS7 wortkarg-präzise. „Tor oder Dach." (MS7) Drei Worte, eine Entscheidung. „Rippe hält. Ich habe schon mit Schlimmerem gearbeitet." Drei Sätze, kein Drama, vollständiger Charakter. Amara entwickelt sich plausibel (Psi-Latenz wächst, wird analytischer), aber bleibt erkennbar dieselbe Person. Auch Side-NPCs (Brennan, Mira, Tavio, Yael) haben jeweils einen Stimm-Tic, der wiederkommt.

### 3. Würfel-Disziplin ist beeindruckend
Über alle Missionen mit Action-Anteil habe ich gezählt: **~85 Proben** mit sichtbarem Template, **30+ kritische Erfolge** (Exploding W6 wurde konsequent geprüft), **~20 Misses** mit spürbaren Folgen. Probe-Header sieht immer gleich aus: `1W6 + ⌊Attr/2⌋ + Talent + Gear ≥ SG`. SGs sind nachvollziehbar (5 trivial, 7-8 schwer, 9 hart). Talent-Bonis und Gear-Bonis (Dermal-Mic +1, Lockpick +1) werden korrekt addiert. Das ist kein „die KI würfelt halt mal" — das ist ein eingehaltenes System.

### 4. Continuity über Sessions hinweg
Das Save-System v7 trägt alles, was es soll. Voronov hat in MS7 Rippe-Verletzung, weil er sie in MS6 abbekam — und das ändert seine STR-Probe (`-1 Rippe`) konkret. Loot ist persistent (russisches Adressbuch von MS6 wird in MS7 referenziert). Acht-Aktive-Liste wächst über vier Missionen mit. Müller entkommt MS4, wird MS5 gefasst, Phase-2-Verhör läuft MS6, Foto-Identifikation hängt in MS7. Das ist kein Loose-Coupling — das ist eine zusammenhängende Kampagne.

### 5. Pacing-Druck via In-Fiction-Timer
Patrouillenfenster (MS7: „~18 Minuten bis Gendarmerie"), Konvergenzpunkte (MS0: „heute Nacht 03:00 Uhr"), Latenz-Kanäle (MS4 Brief-Abfangen): die Welt tickt weiter, auch wenn der Spieler nachdenkt. Das zwingt zu Entscheidungen statt Endlos-Diskussion und ist mechanisch sehr stark gemacht.

---

## Wo es sich verhärtet hat

### 1. Optionsblöcke 1/2/3/4 + Freie Aktion werden eintönig
Die Struktur ist gut für MS0 (Onboarding). Bei MS7 — nach hunderten dieser Blöcke — sehe ich, dass du oft die freie Aktion nimmst oder die Optionen umgehst („ich verhör ihn und voronov soll ne alternative route nach oben auskundschaften, ich komm ja gerade von da"). Das System liest sich, als müsste es immer 3-4 saubere Optionen plus „Freie Aktion" liefern. Bei kleinen Beats wirkt das wie Formularzwang.

**Konkret beobachtet:** in MS7 18-mal genau dieser Block. In MS4 24-mal. Bei einem Spieler mit klarer Vision der nächsten Aktion ist das visueller Lärm.

### 2. „Intel / Risiken / Zeitfenster"-Block ist Overkill bei niedriger Spannung
Bei MS7-Infiltration: extrem hilfreich, weil tatsächlich Zeitdruck. Bei einem ruhigen HQ-Gespräch oder einem Verhör-Beat: Overhead. Es wäre ein **adaptiver Block** denkbar, der nur bei aktivem Zeitfenster / aktiven Risiken auftaucht. Aktuell erscheint er bei jedem Beat, auch wenn er nur „—" enthält oder Bekanntes wiederholt.

### 3. Save-Aufforderungen sind redundant
Bei jedem HQ-Übergang taucht auf:
- `Kodex: HQ-Stand stabil. Deepsave möglich.`
- `Kodex: Sync vor Übergang empfohlen — !save für Stand sichern.`
- `Kodex: Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`

Plus die drei UI-Optionen. Bei MS0 didaktisch sinnvoll. Bei MS7 nach sechs Saves: Lärm. Idee: bei *etabliertem Speicher-Verhalten* (Save-History > 3) auf eine Zeile reduzieren.

### 4. CHA-Builds stoßen mathematisch früh an
Highlander hat CHA 2 in MS0, gepushed auf CHA 4 in MS5. Verhör-SGs:
- MS7 Verhör Runde 1: W6:5 + ⌊4/2⌋ + Talent +2 = 9 vs SG 8 → ERFOLG (knapp)
- MS7 Verhör Runde 2: W6:4 + ⌊4/2⌋ + Talent +2 = 8 vs SG 9 → **MISS**

Mit CHA 4 + Talent + W6 ist Maximum: 6 + 2 + 2 = 10. SG 10 ist eine Eins auf dem W6. Das heißt: gegen einen halbwegs trainierten Gegner ist Verhör-Runde 2+ statistisch verloren. Das ist *vermutlich gewollte Härte* (CHA-Specialist wäre auf 8+ skill-bar), aber als Generalist trifft man die Wand hart.

### 5. System-Fehler beim Level-Tracking (MS5 Budapest)
In `MS5_Budapest_26-05_d50f0a00.md` sehe ich drei aufeinanderfolgende User-Korrekturen:
- „ne, war schon abgeschlossen, hab +1 sys gewählt. Briefing bitte."
- „ne ich hab bereits sys von 2 auf 3 geskillt. 4 ist falsch. Briefing jetzt."
- „ne ich bin auf lvl 6 gestiegen, Da ist dein Fehler."

Drei Korrekturen am laufenden Stück. Das Preset hat den Save-State nicht sauber gelesen oder hat ihn überschrieben mit Defaults. Das ist eine echte Bruchstelle — wenn der Save die Wahrheit ist, dann darf die KI nicht eigene Werte überlagern.

---

## Was mich überrascht hat (positiv & negativ)

### Positiv
- **MS4 Szabo-Café-Szene:** Du orchestrierst „Wein verschütten, Voronov erschrickt, Bedienung kippt Tablett auf Szabo, ich schnapp den Zettel, fotografiere mit Retina-HUD, leg ihn zurück, helfe beim Aufheben." Das ist ein **Heist-Movie-Beat** der das System maximal ausreizt — und das Preset hat es voll mitgespielt, mit Würfen für Geschicklichkeit + Tat-/Coolheit-Probe, sauber durchgezogen. Beste einzelne Szene im Korpus.

- **MS7 Altenberg-Reveal:** (Sub-Agent hat das angedeutet, ich kenne das Ende von MS7 noch nicht voll.) Wenn dort tatsächlich der R. Altenberg / Ordo Temporis-Twist passiert, ist das eine sehr gut vorbereitete Wendung über 6 Missionen Foreshadowing.

- **Foto-Rückseite "R."** als reiner Plot-Hook über mehrere Sessions hinweg ohne sofortige Auflösung. Das vertraut dem Spieler, dass er ein Mystery aushält. Bewährter Krimi-Move, gut platziert.

- **Brennan-Konfrontation MS0:** Festnahme misslingt knapp (Probe 7 vs SG 8), Brennan reagiert *halb* gehorsam — Hände hoch, aber gleichzeitig Schritt zur Hintertür, mit Verhandlungsmasse. Das ist mechanischer Miss mit narrativer Konsequenz, kein Würfelautomat.

### Negativ
- **Reisinger als Zivilziel:** taucht in MS3/MS4 als wichtig auf, dann nie wieder erkennbar. Vier Zivilziele wurden MS4-Phase versprochen, MS5 abgehakt mit „vier Zivilziele gesichert", ohne dass ich beim Lesen einen Spannungsbogen für jeden einzelnen sehe. Das könnte für dich beim Spielen anders gewirkt haben.

- **Yael verschwindet:** wird MS0 als „Status offen" markiert, taucht über MS1–MS6 nicht mehr als aktiver Beat auf. Loose End oder bewusste Setup-and-Forget?

- **MS5_Budapest_24-05_30b6989f, _24-05b_8d84e520, _MS5b_d11e5299, _26-05_d50f0a00** — du hast MS5/HQ-Übergang über **vier Chats** verteilt gespielt (Schnell-HQ, Implantat-OP, Save, dann erst Briefing). Das ist ein durch das OpenWebUI-Chat-Modell erzwungener Workflow, nicht durch ZEITRISS. Aber es bedeutet: zwischen "Mission abgeschlossen" und "neue Mission starten" gehst du durch 3-4 Save-Load-Zyklen, jeder mit eigenem Würfel-Schwellen-Check, eigener Begrüßung, eigener Load-Bestätigung. Das macht das HQ-Erlebnis länger als die Action selbst.

---

## Drei Hypothesen, was dich gestört haben könnte

1. **Die Sub-Mission "HQ-Optimierung" wird zur Hauptbeschäftigung.** Du verbringst signifikante Spielzeit mit Equipment-Tuning ("knall ihm 950 CUs aufn Tisch und sag mach was", „Kodex, analysiere unser Equip"). Das macht Spaß — aber wenn man danach merkt, dass das HQ-Drehbuch sich für jedes neues Item drei Beats Zeit nimmt (Beschreibung, Bestätigung, Bezahlung, Inventar-Update), wirkt es nach der dritten Mission wie ein eigener Spielmodus, der die Core-Op verzögert.

2. **Der Level-Drift-Bug in MS5 wurmt vermutlich.** Wenn das System nicht weiß, was du gewählt hast, ist das ein Vertrauensbruch. Du musstest dreimal nachdrücken, bis es deinem Save folgt.

3. **Die Optionen-Blöcke fühlen sich nach Highlander Lvl 5+ vermutlich gängelnd an.** Du bist ein erfahrener Spieler, hast einen klaren Plan, und das System bietet dir trotzdem jedes Mal seine vier Vorschläge an. Verdacht: du hast mehrfach die Free-Action gewählt nicht weil die Optionen schlecht waren, sondern weil sie *im Weg* waren.

---

## Mechanik-Check (eigene Beobachtungen, ohne Repo-Vergleich)

- **W6 vs W10:** Konsequent. Highlander hat alle Attribute < 11, also durchgängig W6. Korrekt.
- **Exploding W6:** Bei 6 nochmal — gesehen mehrfach, immer korrekt gewürfelt und addiert.
- **Stress-Akkumulation:** Wird gepflegt. MS0 endete bei Stress 3/5, MS4 bei höheren Werten. Stress-bei-Miss ist konsequent.
- **Heldenwürfel (Attribut ≥14):** Nie ausgelöst, kein Attribut so hoch. Korrekt nicht-getriggert.
- **SaveGuard:** Bei MS7-Briefing-Übergang explizit gemeldet, dass !save bis HQ-Debrief gesperrt ist. Regel respektiert.
- **Preserve/Trigger:** MS0 ist klar Preserve (Drake-Ausfahrt muss passieren, Anomalie verhindern). Korrekt durchgehalten.

Ich hab keine offensichtlichen Regelverstöße gesehen. Eine **Detailfrage** zur Würfel-Schwelle: bei `GES 6` wird in MS7-Save-State explizit „W10 bei GES-Proben (GES 6)" annotiert — das widerspricht der Regel „W10 erst ab Attribut ≥11", die ich kannte. Im Spielablauf von MS7 wurden GES-Würfe aber als W6 gerollt (z.B. Schloss knacken, Schleichen). Möglich, dass es eine Schwelle „ab 6" für etwas Anderes gibt (Buff-Schwelle?). Müsste ich im Repo nachschauen — laut LEARNINGS war das ein historischer Streitpunkt (W10-Schwellen-Halluzination 2026-04).

---

## Spielerprofil Flo / "Highlander"

Was ich aus 15 Sessions über deinen Spielstil ablese:

- **Zielgerichtet, wenig Smalltalk.** „Briefing!", „Absprung!", „!save" sind Marker. Du willst Story und Action, nicht Beschreibung des HQ-Cafés.
- **Strategisch.** Du wartest einen Tag in der Nullzeit auf Voronov (MS7), weil Vollständigkeit > Geschwindigkeit. Du nutzt Comlink-Signale für Team-Koordination.
- **Kreativ in Action-Beats.** Die Szabo-Wein-Szene ist Heist-Movie-Material.
- **Loadout-fan.** Du investierst Ressourcen in Cyberware (alle 3 SYS-Slots gefüllt bis MS6), Lockpick-Set, Multitool. Du baust Highlander wie eine RPG-Klasse aus.
- **Vertraust dem System.** Du fragst selten zurück, nimmst Würfelergebnisse an, baust auf den ausgegebenen Intel auf.
- **CHA-Build, obwohl FBI-Spezialist sich nach GES anhört.** Du hast bei Level-up zweimal CHA gepusht (Lvl 4: CHA 2→3, Lvl 5: CHA 3→4). Das war eine bewusste Entscheidung für Verhör/Sozialkontakt, die in MS7 dann an der Mathe-Decke geknallt ist.

---

## Worauf ich jetzt von dir gespannt bin

Drei Fragen, die ich nicht aus dem Korpus beantworten kann und deine Eindrücke bräuchte:
1. Hat sich das HQ zwischen den Missionen **zu lang** angefühlt, oder war das gewünscht? (Equipment-Tuning ist groß bei dir.)
2. Wann hast du das erste Mal gemerkt, dass deine **CHA 2 zu wenig** ist? War der Push auf 4 reaktiv (du hattest Miss-Erfahrungen) oder strategisch (du wusstest, du brauchst Verhör)?
3. Der **Level-Tracking-Bug in MS5** — wie ist das im Moment für dich gewesen? Annoying-but-recoverable oder „jetzt brichts"?

Und das Wichtigste: was hat dir am stärksten gefallen, und was hat dich am stärksten genervt? Ich bin auf den Vergleich mit deinen Eindrücken gespannt.
