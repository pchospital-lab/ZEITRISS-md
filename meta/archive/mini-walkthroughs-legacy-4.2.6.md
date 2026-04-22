---
title: "Mini-Walkthroughs (Legacy) — Archiviert in 4.2.6"
version: 4.2.6
archived: 2026-04-22
reason: >
  Mini-Walkthroughs waren 10-Szenen-Kurzformate aus ZEITRISS' Tabletop-Vergangenheit,
  entstanden bevor der Core-Briefing-Baukasten und die Missions-Generatoren
  (`generate_core_beat`, `generate_rift_beat`) die Mission-Composition übernommen
  haben. Sie waren nie kanonisch playgetestet, zählten 10 statt 12 Einsatz-Szenen
  und setzten Szene 10 nicht als Boss-Gate. In 4.2.6 ist der aktive Korpus
  fokussiert auf Prinzipien und Generatoren — die KI-SL erzählt frei aus den
  Bausteinen, statt vorgefertigten Drehbüchern zu folgen. Die Walkthroughs
  bleiben hier als historische Referenz erhalten.
status: inactive
source: gameplay/kampagnenstruktur.md (pre-4.2.6 Regelstand)
replaced_by:
  - gameplay/kreative-generatoren-missionen.md (Core 12-Step + Rift 14-Step Templates, Core-Briefing-Baukasten)
  - Masterprompt-Tool `generate_core_beat()` / `generate_rift_beat()`
  - gameplay/kampagnenstruktur.md §Aktaufteilung (SSOT für Szenen-Rhythmus)
---

# Mini-Walkthroughs — Legacy-Archiv

> **Nicht mehr aktiv.** Diese Walkthroughs sind historische Beispielskripte aus
> der Tabletop-Ära von ZEITRISS. Sie sind **kein kanonisches Missions-Material**
> und sollten nicht als Referenz für die KI-SL oder den Missions-Generator
> genutzt werden. Für neue Missionen siehe `gameplay/kreative-generatoren-missionen.md`
> (Core-Briefing-Baukasten + Step-Templates) und die SSOT-Regel
> `gameplay/kampagnenstruktur.md#briefing-debrief-szenen-count`.
>
> **Bekannte Abweichungen von 4.2.6-Regeln:**
> - Nur 10 Einsatz-Szenen statt 12 (Core) / 14 (Rift)
> - Szene 10 häufig Exfiltration statt Boss-Gate
> - Nie vollständig durch Gameflow-Smoke verifiziert

---

## Trigger-Beispiel Titanic 1912 {#trigger-beispiel-titanic-1912}

```yaml
# Legacy - pre-4.2.6
title: "Trigger-Mission Titanic 1912"
id: EX-TRIG-1912-TIT
trigger_only: true
version: 4.2.6
```

**Ereignis:** Untergang der Titanic.
**Hintergrund:** Ein Zeitverbrecher will das Schiff retten, um ein
Prototyp-Funkgerät zu bergen. Würde die Katastrophe ausbleiben,
gerät die Technik in militaristische Hände und verschärft kommende
Kriege.

HQ. Briefing - Auftrag: Titanic muss wie bekannt untergehen (HUD: SC 00/--).
 1. Anreise - Sprung nach Southampton, 10. April 1912.
 2. Infiltration - Undercover an Bord in Southampton.
 3. Kontakt - Verdächtigen Offizier im Rauchsalon belauschen.
 4. Intel - Merkwürdige Funkbauteile in seinem Gepäck sichern.
 5. Konflikt - Eiswarnungen im Funkraum abfangen.
 6. Konflikt - Störsender installieren, um Hilfe zu verzögern.
 7. Infiltration - Pumpensteuerung sabotieren.
 8. Twist - Saboteur deckt die Agenten auf, kurzer Nahkampf.
 9. Exfiltration - Rettungsboote beobachten, Chaos zulassen.
10. Konflikt - Gegner versucht weiterhin, Passagiere zu retten.
11. Exfiltration - Via Zeitriss oder Rettungsboot entkommen.
12. Nullzeit-Beat - Rücksprung aus der Einsatzzeit.
HQ. Debrief - Titanic sinkt, Zeitlinie stabil (HUD: SC --/--).

---

## Mini-Walkthrough London-Arc - Endgültige Fassung {#mini-walkthrough-london-arc}

```yaml
# Legacy - pre-4.2.6
title: "Mini-Walkthrough London-Arc"
id: EX-PRES-1851-LON
type: core_op
preserve_only: true
version: 4.2.6
```

**Mission 1 - Chrono Heist**

HQ. Briefing - Auftrag: Brand im Crystal Palace verhindern. (HUD: SC 00/--).
 1. Infiltration - Lieferkutsche schmuggelt Team aufs Gelände.
 2. Kontakt - Bestechung eines Wachmanns öffnet Seitentor.
 3. Intel - Heizungspläne sichern, Lage der Gasrohre prüfen.
 4. Konflikt - ARGOS-Agent entdeckt Störsender.
 5. Kontakt - Palastarbeiter weist auf Lagertrakt.
 6. Intel - Gasflasche mit Zeitsiegel markieren.
 7. Konflikt - Saboteure legen Brandfalle.
 8. Konflikt - Wache löst Alarm aus, Feuerwerk entzündet sich fast.
 9. Exfiltration - Flucht über Dachrinne in den Park.
10. Exfiltration - Zeitriss im Kutschenschuppen erreichen.
HQ. Debrief - Index 2/5, ARGOS bleibt aktiv. (HUD: SC --/--).

**HQ-Phase 1** - Paradoxon < 5, kein ClusterCreate().

**Mission 2 - Gasleitung stoppen**

HQ. Briefing - Seed R-089 droht Explosion am Ausstellungstag. (HUD: SC 00/--).
 1. Infiltration - Abwasserkanal führt unter das Gelände.
 2. Kontakt - Arbeiter melden unregelmäßige Lieferung.
 3. Intel - Abhörgerät entdeckt verdächtige Funksprüche.
 4. Konflikt - Gearwrights bewachen Gasverteiler.
 5. Kontakt - Ingenieur bittet um Hilfe beim Abdrehen.
 6. Intel - Code für Ventile entschlüsseln.
 7. Konflikt - Scharfschütze auf Kran hält Team in Schach.
 8. Konflikt - Gasleitung schließen, Gegner stören.
 9. Exfiltration - Rauch zieht auf, Besucherpanik.
10. Exfiltration - Team springt durch den offenen Zeitriss.
HQ. Debrief - ClusterCreate() löst Seed R-089, Index 0/5. (HUD: SC --/--).

**HQ-Phase 2** - Seed bleibt offen; Schwelle +1, CU ×1.2.

**Mission 3 - ARGOS-Venture zerschlagen**

HQ. Briefing - Letzte Hinweise auf ARGOS-Führer. (HUD: SC 00/--).
 1. Infiltration - Nachtmarkt um den Palast.
 2. Kontakt - Informant liefert Standortcode.
 3. Intel - Überwachungskarten sichern.
 4. Konflikt - ARGOS-Techniker stört Energieversorgung.
 5. Kontakt - Zivilisten warnen vor Patrouillen.
 6. Intel - Identität des Anführers bestätigt.
 7. Konflikt - Feuergefecht im Maschinenraum.
 8. Konflikt - Saboteur versucht Brand erneut.
 9. Exfiltration - Gefangene sichern, per Kutsche raus.
10. Exfiltration - Zeitriss aktiviert, Seed bleibt offen.
HQ. Debrief - Crystal Palace intakt, Arc abgeschlossen. (HUD: SC --/--).

**Epilog** - Seed R-089 weiter offen für spätere Rift-Op.

---

## Mini-Walkthrough Mauerbau 1961 {#mini-walkthrough-mauerbau-1961}

```yaml
# Legacy - pre-4.2.6
title: "Mini-Walkthrough Mauerbau 1961"
id: EX-TRIG-1961-BER
trigger_only: true
version: 4.2.6
```

**Mission 1 - Erste Kontakte**

HQ. Briefing - Ost-Berlin wird abgeriegelt, Schleuserwege kartieren. (HUD: SC 00/--).
 1. Infiltration - Kontrollposten beobachten und Umwege testen.
 2. Kontakt - Schleusernetz ansprechen, Papiere besorgen.
 3. Intel - Baupläne des Schutzwalls auftreiben.
 4. Konflikt - Stasi-Patrouille wird misstrauisch.
 5. Kontakt - Überläufer warnt vor Plenum 89.
 6. Intel - Notfunk abhören, Materialtransporte verfolgen.
 7. Konflikt - Kneipenschlägerei lenkt Wachtrupp ab.
 8. Konflikt - Saboteure beschädigen Baufahrzeuge.
 9. Exfiltration - Rückzug über Kanalrohr.
10. Exfiltration - Zeitriss im Lagerhaus nutzen.
HQ. Debrief - Index 1/5, Lage weiter gespannt. (HUD: SC --/--).

**Mission 2 - Pläne sichern**

HQ. Briefing - Bauleitung überwacht Materialzugänge. (HUD: SC 00/--).
 1. Infiltration - Archiv im Verwaltungsbau infiltrieren.
 2. Kontakt - Stasi-Logistiker bietet Hilfe gegen Schutzgeld.
 3. Intel - Lieferlisten und Routen kopieren.
 4. Konflikt - Rivalen belauschen heimlich das Gespräch.
 5. Kontakt - Fälscherin liefert offizielle Stempel.
 6. Intel - Routenplan der Baufahrzeuge entschlüsseln.
 7. Konflikt - Zeitsoldaten greifen ein, Index steigt.
 8. Konflikt - Verfolgung über den Alexanderplatz.
 9. Exfiltration - Flussfähre Richtung Westen.
10. Exfiltration - Zeitriss im U-Bahn-Tunnel erreichen.
HQ. Debrief - Seed offen, Index 3/5. (HUD: SC --/--).

**Mission 3 - Aufruhr entfachen**

HQ. Briefing - Unruhen sollen Mauerbau erzwingen. (HUD: SC 00/--).
 1. Infiltration - Versammlungen koordinieren.
 2. Kontakt - Oppositionelle Gruppen zusammentrommeln.
 3. Intel - Zeitplan der SED abfangen.
 4. Konflikt - Volkspolizei räumt ersten Platz.
 5. Kontakt - Stasi spioniert Versammlungen aus.
 6. Intel - Funkspruch zum Baubefehl mitschneiden.
 7. Konflikt - Straßenkampf mit Loyalisten.
 8. Konflikt - Demonstration eskaliert vor dem Tor.
 9. Exfiltration - Untertauchen in der Menge.
10. Exfiltration - Zeitriss unter Bahnhof nutzen.
HQ. Debrief - Mauerbau beschleunigt, Zeitlinie stabil. (HUD: SC --/--).

**Epilog** - Grenzanlagen entstehen 12./13. August, Fluchtwege reißen ab.

---

## Preserve-Arc Salamis 480 v. Chr. — Missions-Tabelle

> Diese Tabelle ist der archivierte Walkthrough-Teil des Salamis-Arcs.
> Gegner-Roster, Stil-Notizen und Arc-Outcome bleiben im aktiven Modul
> `gameplay/kampagnenstruktur.md#preserve-arc-salamis-480` erhalten.

| #   | Datum/Phase 480 v. Chr.           | Codename              | Schauplatz           | Preserve                                                                                       |
| --- | --------------------------------- | --------------------- | -------------------- | ---------------------------------------------------------------------------------------------- |
| 1   | 26. Aug. - Morgengrauen           | **Dry Dock**          | Korinthische Werft   | Brandpfeile sabotieren, Schiffsrumpf beschädigen.                                              |
|     |                                   |                       |                      | 3 Bruiser + Urwolf eskortieren Waffen → Nachtkampf auf Triremen                                |
| 2   | 27. Aug. Mittag                   | **Copper Quill**      | Delphi-Amphiktyonie  | Orakelrolle fälschen: 'Seemauern retten Hellas.'                                               |
|     |                                   |                       |                      | Face + Hack-Monk säen Panik → Nahkampf im Adyton                                               |
| 3   | 31. Aug.                          | **Phalanx Key**       | Sparta, Gerusia      | Überzeuge Ephoren, 50 Triremen freizugeben (keine Landarmee).                                  |
|     |                                   |                       |                      | Silver-Tongue besticht Rat → Rededuell, dann Hoplit-Gunfight im Hof                            |
| 4   | 2. Sept.                          | **Aegis-Schaltpunkt** | Ägina-Signalfeuer    | Bewahre Feuerkette - falsches Signal ändert Flottenorden.                                      |
|     |                                   |                       |                      | Drohnen-Rigger zündet Kupfer-Ornithopter-Fackel → Felsenklippen-Duell                          |
| 5   | 10. Sept.                         | **Iron Marble**       | Piräus-Lager         | Persische Skorpion-Ballista-Vorräte zerstören.                                                 |
|     |                                   |                       |                      | Merc-Squad infiltriert als 'Bauern' → Lagerbrand, Kurzfeuergefechte                            |
| 6   | 18. Sept.                         | **Owl Cipher**        | Akropolis-Krypta     | Geheime Seekriegs-Kodexe von Themistokles sichern.                                             |
|     |                                   |                       |                      | Bruiser, Urwolf, Sniper stürmen Höhle → CQB in Karyatiden-Gängen                               |
| 7   | 20. Sept.                         | **Channel Ghost**     | Meerenge von Salamis | Seil-Boom stören, die Engpass blockieren soll.                                                 |
|     |                                   |                       |                      | Combat-Divers legen Minen → Unterwasser-Fight an Bronze-Ketten                                 |
| 8   | 21. Sept. Vor-Dämmerung           | **Red Keel**          | Vorhut-Reede         | ARGOS-Dronen von Xerxes' Flaggschiff entfernen.                                                |
|     |                                   |                       |                      | Samurai-Bodyguard + Rigger → Stealth-Katana vs. Smart-Kopis                                    |
| 9   | 22. Sept. Schlacht                | **Mist Spear**        | Deck der Athená Nicé | Admiralsflagge sichern - Signal fürs Gegenrammen.                                              |
|     |                                   |                       |                      | Sniper auf Nebelschiff, Urwolf an Kette → Mastkletter-Schusswechsel                            |
| 10  | 22. Sept. Ende                    | **Azure Break**       | Xerxes' Thron        | Xerxes nicht evakuieren - er muss Rückzug befehlen.                                            |
|     |                                   |                       |                      | Elite-Handler + Heavy-Merc-Schilde decken Xerxes → Finale Strand-Schlacht (Samurai Gorō hilft) |

---

## Quick-Mission Feuerkette 1410 {#quick-mission-feuerkette-1410}

_45-Minuten-Demo, Tannenberg/Grunwald - kompaktes 12-Szenen-Format zur Einführung_

> **ZEITPUNKT** 15. Juli 1410 - Vorabend der Schlacht von Tannenberg
> **ORT** Hügelkuppe "Witold-Höhe", 2 km südwestlich des Heerlagers der Ordensritter
> **AUFTRAG** Sabotiert einen hölzernen **Signal-Leuchtturm**, dessen Feuerkette Verstärkung anfordert.

```yaml
# Legacy - pre-4.2.6
preserve_only: true
objective: |
  Entferne Pulverrückstände, damit die Kette erst 1410/07/15 detoniert, wie überliefert.
antagonist: "Der Alte Orden"
antagonist_goal: "Signalkette auslösen und Verstärkung rufen"
```

### Szenenübersicht

| # | Ort | Konflikt | Ziel | Spur | SG |
|---|----|---------|-----|-----|----|
| 1 | Nullzeit-Bunker | Zeitdruck, Lauscher | Einsatzplan schmieden | Orden spioniert | 5 |
| 2 | Lagerpfad (Nacht) | Wache & Hund | In Lager eindringen | ferne Hammerschläge | 6 |
| 3 | Schmiedehütte | misstrauischer Schmied | Probenstück sichern | zweiter Wachposten naht | 7 |
| 4 | Schleusengraben | verschlammtes Tor | Geheimgang finden | Wasser steigt | 8 |
| 5 | Pulverkammer | Schloss + Giftgasfalle | Zugang zur Feuerkette | Ketten noch ungefährlich | 9 |
| 6 | Decision Room | Alarm droht | Pulverreste entfernen | Rufe von oben | 9 |
| 7 | Turmaufstieg | feindlicher Bogenschütze | Auf Wehrgang gelangen | Belagerer rücken an | 7 |
| 8 | Wehrgang Ost | Patrouille kreuzt | Zündvorrichtung sabotieren | Rauchwolke im Tal | 8 |
| 9 | Wehrgang West | Kreuzritter rufen Hilfe | Fluchtweg sichern | Kanister mit Öl | 7 |
| 10 | Hofpassage | Ritter greifen an | Zeitriss erreichen | Pferde scheuen | 8 |
| 11 | Waldrand | Verfolger abschütteln | Rücksprungpunkt erreichen | Turm brennt nicht | 6 |
| 12 | Nullzeit-Beat | Rücksprung armieren | Einsatzfenster schließen | Sprung-Signatur klar | 6 |

---

## Kurzabenteuer "Operation GLASLÄUFER" {#operation-glaslaeufer}

_10-Seiten-Outline, Berlin 1961_

| Position       | Ort                | Konflikt                  | Ziel                   | Spur                       | SG  |
| -------------- | ------------------ | ------------------------- | ---------------------- | -------------------------- | --- |
| _HQ (vor 1)_   | HQ-Briefing        | straffer Zeitplan         | Auftrag besprechen     | Funkmast-Foto              | -   |
| 1              | Checkpoint Charlie | misstrauische Grenzer     | Einreise sichern       | Baukolonne im Hintergrund  | 6   |
| 2              | Straßenmarkt       | neugieriger Informant     | Stasi-Ingenieur finden | Gerücht Funkstörung        | 6   |
| 3              | Baucontainer       | versteckte Mikrofone      | Pläne kopieren         | abgenutztes Siegel         | 7   |
| 4              | Funkmast-Basis     | Patrouille prüft Ausweise | Zugang zum Mast        | Aktentasche voller Skizzen | 8   |
| 5              | Wartungsgang       | Reparaturtrupp taucht auf | Abhörgerät platzieren  | Dröhnen setzt ein          | 8   |
| 6              | Versorgungsraum    | Zeitsoldaten erscheinen   | Kampf vermeiden        | Index steigt auf 1         | 9   |
| 7              | Container-Hack     | Alarm ausgelöst           | Steuerung sichern      | Peilsender piept           | 9   |
| 8              | Flucht zur Spree   | Scheinwerfer suchen       | Dampfer erreichen      | Hund bellt am Kai          | 7   |
| 9              | Dampferdeck        | Verfolger feuern          | Abfahrt erzwingen      | Funkspruch "Ziel flieht"   | 8   |
| 10             | Boss-Encounter     | Alt-Ingenieur stellt sich | Ziel-Objekt sichern    | Foreshadow-Gate 4/4        | 9   |
| 11             | Spree-Ufer         | Motorboot jagt            | Abstand gewinnen       | Wasserpegel steigt         | 7   |
| 12             | Nullzeit-Beat      | Rücksprung armieren       | Einsatzfenster schließen | Signatur rein            | 6   |
| _HQ (nach 12)_ | HQ-Debrief         | -                         | Einsatz bewerten       | Zeitsoldaten aktiv         | -   |

_Start in 60 Sek.:_ Pre-Gen-Operative wählen; ITI stellt Standard-Loadout kostenlos bereit
(Zusatzgear kostet CU, siehe Modul 15); SL würfelt Wetterprobe, nennt Sicht & Geräuschpegel.

---

## Beispiel-Episoden & Rift-Op

**Episode 1 - OKO FALSE-ALARM**

HQ. Briefing in Nullzeit-Atrium - Petrow retten, Atomkrieg verhindern (HUD: SC 00/--).
 1. Moskau-Vorstadt: Schwarzmarkt-Kontakt für Uniform.
 2. LKW-Kontrolle: falsche Papiere überzeugen.
 3. Zaun bei Schneesturm - Laser-Kamera, Wachhund.
 4. Lüftungsschacht voller Frost - leise sägen.
 5. **Twist:** Legionär-Leibwache patrouilliert (anachron).
 6. Funkraum - Sat-Signal stören oder fälschen.
 7. Zentrale - Petrow zweifeln lassen, Raketen-Alarm blinkt.
 8. Alarm ertönt doch: Neandertaler-PMC stürmt Flur.
 9. Schacht-Escape zum Wald.
10. Verfolgung auf Ural-Truck.
HQ. Debrief - 300 CU + Lizenz-Shop (HUD: SC --/--).

**Episode 4 - FALKENSTEIN NACHTJAGD**

HQ. Briefing - Burggraf verkauft Zukunfts-Tech. (HUD: SC 00/--).
 1. Dorf-Schankstube: Gerücht, Geheimgang entdecken.
 2. Nacht-Wald, Armbrust-Patrouille.
 3. Steinschloss-MG-Nest (anachron) auf Zugbrücke.
 4. Innenhof - mittelalterliche Drohne auf Scheiterhaufen-Podest.
 5. **Twist:** Gladiator mit PKM bewacht Schatzkammer.
 6. Krypta-Tunnel - Kreuzrisse im Mauerwerk explodieren.
 7. Schatzkammer - Daten-Kristall sichern.
 8. Alarm: Burghorn + Scheinwerfer aus 1930.
 9. Dach-Rappelling bei Vollmond-Bluthunden.
10. Fluss-Flucht im Ruderboot, Verfolgung durch Sturmtruppler.
HQ. Debrief - 450 CU. (HUD: SC --/--).

**Episode 9 - TITAN DRIFT**

HQ. Briefing - Kolonisten 99 % tot, Anomalie stoppen. (HUD: SC 00/--).
 1. Dock-Schleuse: Vereiste Panels, Energie 3 %.
 2. Dunkel-Korridor, Leichensäcke treiben.
 3. Reaktor-Core, scheinbar "Alien"-Raptoren (zeitversetzte Fauna) nagen Kabel.
 4. Sensor-Array - Windung außerhalb Schiffshülle.
 5. **Twist:** Gegenspieler nutzt Zeit-Leuchtboje, Risse im Rumpf.
 6. Kolonisten-Cryo-Deck - Restcrew befreien.
 7. Reaktor neu starten (Schalter-Puzzle).
 8. Schwarm-Horde nähert sich Brücke, Zeitdruck 6 min.
 9. Not-Abkoppeln Brückensektion.
10. Evac via Shuttleröhre in Orbit-Pod.
HQ. Debrief - 700 CU, möglicher T3-Kauf. (HUD: SC --/--).

**Rift-Op Mothman Bridge**

HQ. Briefing - Sturzregen über Virginias Highway; flackernde Lichter und gesperrte Brücken beunruhigen die Polizei (HUD: SC 00/--).
 1. Anreise bei Sturm, Brückenbauwerk gesperrt.
 2. Local Witness - verängstigter Trucker berichtet von roten Augen.
 3. Drohnen-Scan zeigt Energiespitzen im Nebel.
 4. Spuren sichern am Brückenpfeiler.
 5. **Twist:** Phantom-Passanten tauchen zeitversetzt auf.
 6. Lagerhaus durchsuchen - alte Karten finden.
 7. Mutierte Tiere greifen aus Schatten an.
 8. Tunnel unter der Brücke entdecken.
 9. Seismische Stöße reißen Mauerstücke weg.
10. Mothman-Sichtung am Brückenbogen.
11. Kampf gegen Kultisten, die Zeitriss stabilisieren wollen.
12. Zeitriss schließen oder abstürzende Brücke riskieren.
13. Nachspiel - Aufräumen an der Brücke.
14. Epilog - Nullzeit-Beat / Flashback (kein Loot).
HQ. Debrief - 800 CU, Paradoxon sinkt auf 0 (HUD: SC --/--).
