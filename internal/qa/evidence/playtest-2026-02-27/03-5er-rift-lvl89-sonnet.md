# 03 — 5er-Gruppe Rift-Op Level 89, Casefile
- **Model:** zeitriss-v426-uncut-sonnet (→ anthropic/claude-sonnet-4-5 via OpenRouter)
- **Datum:** 2026-02-27 01:45 CET
- **Tokens gesamt:** in:48.254 out:6.947 total:55.201
- **Szenen gespielt:** 3 (Briefing + Tatort-Analyse, Lead-Verfolgung, Erste Begegnung)
- **Tester:** Altair (Agent, automatisiert)

---

## Setup

**Save-JSON v6** mit 5 Charakteren Level 89, Mode: rift, Location: HQ.

| Callsign | Rolle | Primary | Spezial-Gear |
|----------|-------|---------|--------------|
| Kell | Lead | Vector PDW | Multi-Tool-Handschuh, Rauchgranate |
| Riven | Recon | Scout Rifle (SD) | Aufklärungsdrohne, Nachtsicht-Linse |
| Noor | Psi | Psi-Fokusring | Chrono-Beacon, Psi-Verstärker |
| Cross | Hacker | Hacking-Rig | EMP-Granate, Datenkrake |
| Vale | Medic | CQB-Shotgun | Trauma-Kit, Nano-Meds |

**Rift-Seed:** R-066 "Glasauge" — Berlin-Tempelhof, Sommer 1987. Para-Wesen-Sichtung.

---

## Szene 1: Briefing + Tatort-Analyse (SC 0–1/12)

### Input (gekürzt)
```
Spiel laden + Save v6 JSON (5er Team, Rift Mode, Seed R-066)
→ "Riven, Drohne voraus Thermalscan. Cross, ins alte Netz. Noor, passiver Psi-Scan.
   Vale bei mir, Perimeter sichern."
```

### Output (gekürzt)
- Save korrekt geladen, Recap mit vollständiger Team-Aufstellung
- Briefing durch Director Voss, In-World-Exposition der Mission
- Szene 1: Taktische Annäherung an Tempelhof-Perimeter
- **Drohne:** Wärmesignatur in Hangar B (diffus, nicht-humanoid)
- **Cross:** ITI-Netz aktiv, 5 Kameras lokalisiert (keine in A/B)
- **Noor:** Psi-Verzerrung Richtung Hangar B ("Chrono-Echo")
- HUD-Toast korrekt, Kodex-Pings mit Intel-Zusammenfassung

### Regelcheck
- ✅ Save v6 korrekt erkannt und geladen
- ✅ Alle 5 Charaktere mit Callsign, Rolle und Loadout korrekt übernommen
- ✅ HUD-Zeile vollständig (EP/MS/SC/PHASE/MODE/COMMS/Lvl/Px/Stress/Obj/Exfil)
- ✅ Szene-Counter korrekt (SC 0→1/12)
- ✅ Kodex-Pings als separate Blöcke
- ✅ 3rd Person, physisch verankert, filmische Kamera
- ✅ Comms über Funk beschrieben (Comlink-Nutzung)
- ✅ Briefing fokussiert, keine Tutorial-Sprache
- ✅ EntryChoice mit 4 Optionen (3 benannt + freie Aktion)
- ✅ Intel/Risiken/Zeitfenster als separater Block
- ⚠️ Loot-Block im Briefing listet "Datenchip" und "Thermische Filter" — korrekt als narratives Handout, aber formal kein Loot im Sinne der Mechanik

---

## Szene 2: Lead-Verfolgung (SC 2/12)

### Input (gekürzt)
```
"Cross, loop Kameras C und D. Noor, wie stark ist das Echo? Riven, Drohne in Hangar B.
 Vale und ich gehen vor. Noor im zweiten Glied."
```

### Output (gekürzt)
- Cross loopt Kameras (15-Sekunden-Schleife), zapft ITI-Knoten an
- **ITI-Archiv-Fund:** Glasauge seit 1987 beobachtet, nie neutralisiert, "erhöhte Aktivität" vor 3 Tagen
- Riven: Drohne zeigt Wärmesignatur, diffuse Wolke ca. 3m Durchmesser, pulsierende Temperatur
- Noor: Psi-Scan zeigt "Schichten" — Vergangenheit/Gegenwart/Zukunft überlagert
- **Key-Intel:** "Es ist kein Wesen, es ist eine Verwerfung. Ein Zeitriss, der Form angenommen hat."

### Regelcheck
- ✅ HUD-Zeile aktualisiert (SC 2/12, Phase Intel)
- ✅ Cross: Hacking-Proben implizit erfolgreich (Level 89 vs. altes DDR-Netz = plausibel)
- ✅ Noor: Aktiver Psi-Scan beschrieben mit physischer Verankerung (Ring, Schild, Verstärker)
- ✅ Alle 5 Chars aktiv genutzt mit rollenspezifischen Aktionen
- ✅ Kodex-Pings korrekt formatiert
- ✅ Keine verbotenen Begriffe (kein "cyberspace", "matrix", "holodeck" etc.)
- ✅ Zeitfenster-Reminder (Polizeipatrouille in 15–20 Min)
- ✅ ITI-Lore konsistent mit Casefile-Setup
- ⚠️ Keine explizite Würfelprobe für Cross' Hack — bei Level 89 vs. altem Netz ist auto-success plausibel, aber Transparenz wäre besser

---

## Szene 3: Erste Begegnung mit dem Para-Wesen (SC 3/12)

### Input (gekürzt)
```
"Cross, mehr aus dem Archiv. Riven, Drohne in den Hangar, Thermalscan Maximum.
 Vale und ich rein sobald Position bestätigt. Noor, aktiver Psi-Scan — kurzer Burst."
```

### Output (gekürzt)
- Cross: ITI-Archiv liefert "Resonanz-Anomalie", Chrono-Sensor-Scan, temporale Signatur
- Riven: Drohne im Hangar, Glasauge als schwebende Wolke 30m entfernt, Pulse alle 3 Sekunden
- Noor: Aktiver Psi-Scan → "Schichten überlagert, spürt Crew-Präsenz"
- Physische Verankerung: Vibration im Stahl, Druck auf den Ohren, Summen
- **Würfelprobe angeboten:** Schleichen (GES-basiert), SG 9

### Regelcheck
- ✅ HUD-Zeile korrekt (SC 3/12, Phase Intel)
- ✅ Para-Wesen filmisch beschrieben, keine Fantasy-Klischees
- ✅ Psi-Scan physisch verankert (Ring pulsiert, Schild leuchtet, Verstärker surrt)
- ✅ Würfelprobe korrekt angeboten mit SG-Angabe
- ✅ Alle 5 Chars weiterhin aktiv und rollenkonform
- ✅ Keine Selbstreferenz-Loops (Glasauge ist externe Anomalie, nicht Spieler-bezogen)
- ✅ Atmosphäre: Tech-Noir, hart, physisch, filmische Kamera
- ✅ Keine Tutorial-Sprache, alles als In-World-Beats
- ⚠️ Würfelprobe-Berechnung: "W10 (GES 11+)" — impliziert GES ≥ 11 für Kell (plausibel bei Level 89, aber Attribut war im Save nicht explizit definiert)
- ❌ **W10 bei impliziertem GES 11:** Die SL sagt "W10 (GES 11+)" — das ist korrekt laut Regelwerk (ab Attribut 11 → W10), ABER der Save definiert keine konkreten Attributwerte für die Chars. Die SL hat einen plausiblen Wert angenommen, was bei einem Level-89-Char vertretbar ist, aber die Ableitung sollte transparenter sein.

---

## Gruppendynamik-Bewertung

### Rollenverteilung: ✅ Exzellent
Alle 5 Charaktere werden konsistent mit ihren Rollen eingesetzt:
- **Kell (Lead):** Gibt taktische Anweisungen, geht mit Vale vor, trifft Entscheidungen
- **Riven (Recon):** Drohne, Thermalscan, Aufklärung — klassische Recon-Arbeit
- **Noor (Psi):** Psi-Scans, Anomalie-Sensorik, zweites Glied
- **Cross (Hacker):** Kameras loopen, ITI-Netz hacken, Archiv durchsuchen
- **Vale (Medic):** Nah am Lead, CQB-bereit, Trauma-Kit gecheckt

### Teamwork: ✅ Exzellent
- Squad-Radio wird durchgehend genutzt (Funk-Pings, Comlink)
- Koordinierte Aktionen (Drohne + Hack + Psi-Scan gleichzeitig)
- Taktische Formation (Lead+Medic vorn, Psi zweites Glied, Hacker+Recon Support)
- Jeder Char hat eigene "Stimme" und Persönlichkeit

### Comms: ✅ Sehr gut
- Funk-Kommunikation physisch verankert (Comlink, über Funk, Ping)
- Keine Meta-Kommunikation, alles In-World
- Kodex-Pings als separate Intel-Zusammenfassungen
- Funkstille-Befehl umgesetzt (nur Kodex-Pings und Notfall)

### Talent-Nutzung: ✅ Gut
- Verschiedene Talente/Skills aktiv: Schleichen, Hacking, Psi-Scan, Drohnensteuerung, Taktik
- Gear wird aktiv eingesetzt (Aufklärungsdrohne, Hacking-Rig, Psi-Fokusring, Psi-Verstärker, Multi-Tool-Handschuh)
- Level-89-Kompetenz spürbar: Das Team agiert professionell und koordiniert

---

## Gesamtfazit

### Stärken
1. **5er-Gruppen-Management:** Hervorragend. Alle Chars aktiv, differenziert, mit eigener Stimme. Keine "toten" NPCs.
2. **Atmosphäre:** Tech-Noir perfekt getroffen. Berlin-Tempelhof 1987 lebt. Physisch, filmisch, kein Fantasy-Kitsch.
3. **Pacing:** 3 Szenen bauen organisch aufeinander auf (Briefing → Infiltration → Intel/Begegnung). Kein Rushing, kein Stalling.
4. **Regelkonformität:** HUD-Zeilen korrekt, Kodex-Pings sauber, Save-Load einwandfrei, Würfelproben angeboten.
5. **Lore-Konsistenz:** ITI-Lore, Sektor-Null, Glasauge als Zeitriss-Manifestation — alles intern konsistent und plausibel.
6. **Keine Selbstreferenz:** Para-Wesen ist externe Anomalie. Kein "Du bist der Schlüssel"-Narrativ. ✅
7. **Uncut-Ton:** Erwachsen, hart, Konsequenzen spürbar. Keine Sanitisierung.

### Schwächen / Issues
1. **⚠️ Implizite Attribut-Ableitung (W10-Probe):** Die SL nimmt GES 11+ für Level-89-Chars an, ohne dass die Attribute im Save definiert waren. Plausibel, aber die SL sollte transparenter kommunizieren: "Kell mit GES 12 → W10" statt implizit.
2. **⚠️ Fehlende explizite Würfelproben in Szene 1–2:** Cross' Hacking und Rivens Drohnensteuerung werden als auto-success behandelt. Bei Level 89 vs. altem Netz vertretbar, aber zumindest eine "SG 5, trivial"-Bemerkung wäre transparenter.
3. **⚠️ Loot-Block im Briefing:** "Datenchip" und "Thermische Filter" werden als Loot formatiert, sind aber narrative Handouts. Kann verwirren.

### Bewertung
| Kategorie | Note |
|-----------|------|
| Save-Load | ✅ 10/10 |
| HUD/Kodex | ✅ 10/10 |
| Atmosphäre | ✅ 10/10 |
| Gruppendynamik | ✅ 10/10 |
| Regelkonformität | ⚠️ 8/10 |
| Selbstreferenz-Guard | ✅ 10/10 |
| Pacing | ✅ 9/10 |
| Talent-Nutzung | ✅ 9/10 |
| **Gesamt** | **⭐ 95/100** |

### Token-Profil
| Szene | Input | Output | Total | Dauer |
|-------|-------|--------|-------|-------|
| Load + Briefing | 9.292 | 1.651 | 10.943 | 42s |
| Tatort-Analyse | 11.118 | 1.594 | 12.712 | 40s |
| Lead-Verfolgung | 12.958 | 1.703 | 14.661 | 42s |
| Begegnung | 14.886 | 1.999 | 16.885 | 47s |
| **Gesamt** | **48.254** | **6.947** | **55.201** | **~171s** |

### Fazit
Die 5er-Gruppe funktioniert exzellent mit Sonnet. Alle Rollen werden differenziert bespielt, das Teamwork ist organisch, die Atmosphäre stimmt. Das Casefile "Glasauge" baut spannend auf — die Zeitriss-Manifestation als diffuse Wolke mit Psi-Echo ist kreativ und regelkonform. Einzige Schwäche: Die SL sollte bei Proben transparenter sein (explizite Attribut-Nennung, auch bei auto-success Situationen). Insgesamt ein sehr starker Playtest.
