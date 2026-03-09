# ZEITRISS – NPC-Chrononauten & MMO-Immersion (Review + Copy-Paste-Paket)

## Kurzfazit

Die neue **Kontinuitätslogik für echte Spielercharaktere** ist inzwischen stark genug, um das gewünschte MMO-Gefühl glaubhaft anzudeuten.

Der **größte verbleibende Bruch** liegt jetzt bei den **NPC-Chrononauten**:
- In der aktuellen Philosophie von ZEITRISS sollen Rückkehrer, Joiner, Splits, Rejoins und Kontinuitäts-Echos eine lebende Welt erzeugen.
- Im Toolkit existiert aber noch eine alte Logik, in der ein Solo-NPC-Team im Kern **temporär** ist und Gruppenstarts sogar **Px/Seeds resetten**.
- Gleichzeitig gibt es im v7-Schema **keinen kompakten, strukturierten NPC-Kontinuitätsblock**, obwohl `npc-team` als echter Startpfad vorhanden ist.

Die Folge: Bei Menschen ist Kontinuität inzwischen deutlich besser, bei NPC-Mitagenten aber noch nicht auf demselben Niveau.

---

## Was jetzt als Zielbild gelten sollte

**Leitidee:**
NPC-Chrononauten sind **keine Wegwerf-Füller**, sondern **persistente Offscreen-Agenten des ITI**, die den Spieler begleiten, sich von ihm lösen, wieder auftauchen, Spuren hinterlassen und sich in Solo wie Multiplayer gleich anfühlen.

Der Spieler soll **nichts verwalten müssen**. Er lädt nur seinen Save. Die KI-SL erledigt den Rest in-world.

---

## Design-Entscheidung (SSOT)

### Neue Goldregel

> **NPC-Chrononauten sind persistente Kontinuitätsakteure.**
> Sie verschwinden nicht, wenn sie die Szene verlassen. Wenn sie nicht im Bild sind, operieren sie anderswo im ITI-Einsatznetz.

### Drei Arten von NPC-Chrononauten

1. **personal**  
   Gehören zur persönlichen Kontinuität eines Spielercharakters.  
   Sie reisen mit dessen Save als bekannte Personen mit.

2. **session**  
   Gehören zur aktuell laufenden Gruppen-/Branch-Kontinuität.  
   Sie bleiben beim Session-Anker, wenn ein Spieler die Runde verlässt.

3. **iti**  
   Allgemeine ITI-Agenten.  
   Sie können situativ auftauchen, werden aber nur persistent gespeichert, wenn sie mehrfach wichtig wurden.

---

## Minimaler Schema-Zusatz (kompakt, MMO-tauglich)

### Vorschlag: Ergänzung in `continuity`

```json
"continuity": {
  "last_seen": { "mode": "core", "episode": 1, "mission": 0, "location": "HQ" },
  "split": {
    "family_id": null,
    "thread_id": null,
    "expected_threads": [],
    "resolved_threads": [],
    "convergence_ready": false
  },
  "roster_echoes": [],
  "shared_echoes": [],
  "convergence_tags": [],
  "npc_roster": [
    {
      "id": "NPC-0001",
      "name": "Mara Voss",
      "callsign": "Latch",
      "role": "tech",
      "trait": "trocken, präzise, ungeduldig",
      "scope": "personal",
      "owner_id": "CHR-XXXX",
      "bond": 2,
      "status": "attached",
      "last_seen": { "episode": 1, "mission": 3, "location": "HQ" },
      "offscreen": "War mit Team Orpheus in Alexandria; kam mit Brandnarbe und Zugangskarte zurück.",
      "hook": "Kennt Wartungsschacht C-12"
    }
  ],
  "active_npc_ids": ["NPC-0001"]
}
```

### Harte Caps

- `npc_roster[]` max **6**
- `active_npc_ids[]` max **4**
- `offscreen` max **1 Satz pro NPC**
- keine Wallets, keine Vollinventare, keine Extra-Subtrees für NPCs

### Warum das reicht

NPCs brauchen für die MMO-Illusion **Beziehung, Status, letzte Spur und Haken** – nicht denselben Vollbau wie Spielercharaktere.

---

## Feldlogik für NPCs

### Pflichtfelder und Bedeutung

- `id` → stabile Wiedererkennung beim Merge
- `role` → Einsatzfunktion (`tech|face|medic|breach|intel|psi`)
- `trait` → Stimme / Persönlichkeit
- `scope` → wem die Figur logisch folgt
- `owner_id` → bei `personal` der zugehörige Spielercharakter
- `bond` → Bindung 0–4
- `status` → aktueller Zustand
- `offscreen` → genau ein Satz: Was ist seit dem letzten Treffen passiert?
- `hook` → verwertbare Spur, die später relevant werden kann

### Status-Enum

```text
attached | hq | assigned | recovering | missing | rival
```

Bedeutung:
- `attached` = gerade als aktiver Begleiter vorgesehen
- `hq` = im HQ ansprechbar, aber nicht im Feld
- `assigned` = offscreen bei anderem Einsatz
- `recovering` = verletzt / instabil / Klinik / Refit
- `missing` = bewusst unklar, Hook für spätere Rückkehr
- `rival` = lebt weiter, aber gegenläufig

---

## Auswahlregel für gemischte Mensch/NPC-Gruppen

### SSOT-Regel

> **Menschen belegen Feldplätze zuerst. NPCs füllen nur freie Plätze bis Teamgröße 5 auf.**

### Konsequenz

- 5 Menschen = keine Feld-NPCs, aber bekannte NPCs dürfen im HQ, Funk oder Debrief präsent sein
- 3 Menschen = bis zu 2 NPC-Feldplätze
- 1 Mensch solo mit `npc-team 4` = 4 NPC-Feldplätze möglich

### Wer darf NPCs „mitbringen“?

**Nicht nur der Host.**
Jeder geladene Save darf **NPC-Kontinuität** mitbringen.

Aber:
- **Session-NPCs** hängen am Session-Anker
- **Personal-NPCs** hängen an ihrem `owner_id`
- **aktive Feldplätze** sind global begrenzt

### Auswahlalgorithmus (einfach, robust)

```pseudo
human_slots = count(human characters in current session)
free_npc_slots = max(0, 5 - human_slots)

candidates = dedupe(all loaded continuity.npc_roster by npc.id)

priority order:
1. session + status=attached
2. personal + status=attached
3. session + status=hq
4. personal + status=hq
5. iti + status=hq|assigned

then tie-break by:
A. role fit zur Mission
B. höherer bond
C. neueres last_seen

selected = top free_npc_slots
all others remain HQ/offscreen
```

### Wichtig

Die KI-SL soll **nicht technisch nachfragen**, sondern nur dann in-world fragen, wenn es dramaturgisch Sinn ergibt:
- „Für den Einsatz ist nur ein freier Platz im Shuttle. Wen nehmt ihr mit – Latch oder Solberg?“

Wenn keine Nachfrage nötig ist, wählt die KI automatisch.

---

## Was passiert, wenn sich der Spieler von NPCs löst?

### Solo → wieder solo ohne NPC-Team

Die NPCs verschwinden **nicht**.
Sie gehen in einen der Zustände `hq`, `assigned`, `recovering`, `missing` oder `rival`.

Beim nächsten relevanten Load liefert die KI-SL **eine kurze Offscreen-Fortschreibung**:
- wo sie waren
- was sich verändert hat
- was sie jetzt mitbringen

Beispiel:

> **Latch** war in Alexandria mit Team Orpheus. Sie kam mit einer Brandnarbe zurück, spricht seitdem knapper als sonst und hat einen Wartungsring aus einem gesperrten Depot mitgebracht.

### Multiplayer-Join mit bekannten NPCs

- bekannte Personal-NPCs tauchen beim Rejoin zuerst als **Kontinuitätspräsenz** auf
- nur freie Feldplätze erlauben tatsächliche Mitnahme
- sonst bleiben sie sichtbar in HQ/Funk/Debrief statt unsichtbar gelöscht zu werden

---

## Was passiert, wenn der Spieler die Gruppe wieder verlässt?

### Harte Regel

- **personal-NPCs** gehen mit dem Spieler zurück in dessen persönliche Kontinuität
- **session-NPCs** bleiben beim Session-Anker der laufenden Runde
- **iti-NPCs** fallen auf Hintergrundstatus zurück, sofern sie nicht aufgewertet wurden

### Transfer nur als Szene

Ein Wechsel eines NPC zwischen `session` und `personal` darf nur über einen **sichtbaren Inworld-Beat** passieren:
- „Mara kommt mit dir.“
- „Solberg bleibt bei Team A.“
- „Renier zieht Latch für einen internen Auftrag ab.“

So wirkt es wie Weltlogik und nicht wie Datenverschiebung.

---

## Offscreen-Simulation: wenig Daten, viel Gefühl

### Regel

Pro abwesendem NPC maximal **eine** kompakte Offscreen-Fortschreibung pro Rückkehrfenster.

### Satzbau-Schablone

```text
[Name] war [Auftrag/Ort], kam [verändert] zurück und bringt [Hook/Folge] mit.
```

### Mini-Generator (für KI-SL)

**Auftrag:**
- Überwachung
- Bergung
- Eskortierung
- Archiv-Zugriff
- Chronopolis-Aufklärung
- Fraktionskontakt
- medizinische Reha

**Veränderung:**
- Narbe
- Misstrauen
- neue Loyalität
- Schuldgefühl
- seltsame Ruhe
- technischer Defekt
- Beute / Zugangscode / Kontakt

**Folge:**
- Hook
- Boss-Tell
- Alt-Route
- Ruf-Impuls
- Fraktionsgerücht
- persönlicher Konflikt

### Wichtiger Guard

Offscreen-NPCs erzeugen **keine vollständigen Parallelkampagnen**.
Sie liefern **Zusammenfassung + Haken**, keine zweite unendliche Spielfläche.

---

## Pflichtbeats, die noch fehlen und ergänzt werden sollten

### 1. NPC-Rejoin-Beat

Wenn bekannte NPC-Chrononauten im Save oder Merge relevant sind, muss die KI-SL beim Load kurz zeigen:
- wer physisch da ist
- wer nur als Funk/HQ-Spur präsent ist
- wer fehlt
- was sich an ihnen geändert hat

### 2. NPC-Departure-Beat

Wenn ein NPC das Team verlässt, nie still. Immer 1–2 Sätze.

### 3. NPC-Recognition-Beat

Wenn ein NPC später wieder auftaucht, soll er sich an mindestens **eine** konkrete geteilte Sache erinnern.

Beispiel:

> „Berlin ’73. Du hast mir damals den dritten Zugang aufgemacht. Ich hab das nicht vergessen.“

### 4. NPC-Cross-Pollination

Wenn NPCs Offscreen waren, sollen sie gelegentlich etwas aus einer anderen Linie mitbringen:
- ein Gerücht
- eine Wunde
- einen Gegenstand
- einen Boss-Tell
- eine neue Haltung

So entsteht die MMO-Lüge: Die Welt lief weiter, auch wenn die Kamera weg war.

---

## Der größte aktuelle Problemblock, der weg muss

### Alte Toolkit-Logik ersetzen

Der Abschnitt **„Solo-Modus mit temporärem NPC-Team“** muss raus oder komplett umgeschrieben werden.

Insbesondere problematisch:
- „temporäres Team“
- „existiert nur für diese Mission“
- `StartGroupMode(...)` mit Reset von `campaign.px` und `rift_seeds`

Diese Logik stammt aus der alten Gruppenstart-Denkweise und widerspricht dem aktuellen Kontinuitätsmodell direkt.

---

## Copy-Paste-Issue 1 – Persistente NPC-Chrononauten statt temporärer Solo-Begleiter

**Titel:** Persistente NPC-Chrononauten als Kontinuitätsakteure definieren

**Ziel:**
Ersetze die alte Solo-„temporäres NPC-Team“-Logik durch ein persistentes NPC-Kontinuitätsmodell, das Solo und Multiplayer gleich behandelt.

**Umsetzen:**
- Toolkit-Abschnitt „Solo-Modus mit temporärem NPC-Team“ vollständig überarbeiten
- Begriffe „temporär“, „nur für diese Mission“ und Reset-Logik entfernen
- neue SSOT-Regel einführen: NPC-Chrononauten sind persistente Offscreen-Agenten
- Statusmodell ergänzen: `attached|hq|assigned|recovering|missing|rival`
- Scope-Modell ergänzen: `personal|session|iti`
- keine Vollcharaktere daraus machen, sondern kompakte Kontinuitätsobjekte

**Akzeptanzkriterien:**
- Solo-NPCs verschwinden nach Missionende nicht mehr implizit
- NPCs können in späteren Sessions wieder auftauchen
- Solo- und Multiplayer-Join nutzen dieselbe Logik
- kein Px-/Seed-Reset mehr beim Gruppieren

---

## Copy-Paste-Issue 2 – v7 um kompakten `npc_roster` ergänzen

**Titel:** Save v7 um kompakten NPC-Kontinuitätsblock erweitern

**Ziel:**
Persistente NPC-Chrononauten mit minimalem JSON-Budget speicherbar machen.

**Umsetzen:**
- in `continuity` ergänzen:
  - `npc_roster[]` max 6
  - `active_npc_ids[]` max 4
- pro NPC nur kompakte Felder speichern:
  - `id,name,callsign,role,trait,scope,owner_id,bond,status,last_seen,offscreen,hook`
- keine Wallets, keine Vollausrüstung, keine XP-Subtrees für NPCs

**Akzeptanzkriterien:**
- bestehende Saves bleiben per Default kompatibel (`npc_roster=[]`)
- Mehrfach-Load kann NPCs deduplizieren
- NPCs sind bei Rejoin/Leave später wieder referenzierbar

---

## Copy-Paste-Issue 3 – Seat-Algorithmus für Mensch/NPC-Mischgruppen

**Titel:** Einheitliche Slot-Regel für gemischte Menschen- und NPC-Gruppen

**Ziel:**
Festlegen, wer NPCs mitbringen darf und wie aktive Feldplätze fair und stabil besetzt werden.

**Umsetzen:**
- Menschen zählen immer zuerst gegen Teamcap 5
- NPCs füllen nur freie Plätze
- jeder geladene Save darf NPC-Kontinuität mitbringen
- Session-NPCs hängen am Session-Anker
- Personal-NPCs hängen am `owner_id`
- Auswahlreihenfolge definieren:
  1. `session+attached`
  2. `personal+attached`
  3. `session+hq`
  4. `personal+hq`
  5. `iti`
- Tie-Break: Rollenfit → Bond → Recency

**Akzeptanzkriterien:**
- 5 Menschen = keine Feld-NPCs
- 3 Menschen = max 2 Feld-NPCs
- kein stilles Verschwinden bekannter NPCs; nicht gewählte NPCs bleiben HQ/Funk/offscreen präsent

---

## Copy-Paste-Issue 4 – Offscreen-Fortschreibung für NPCs

**Titel:** Kompakte Offscreen-Simulation für abwesende NPC-Chrononauten

**Ziel:**
NPCs sollen auch außerhalb der aktiven Kamera glaubhaft weiterleben, ohne Save-Budget zu sprengen.

**Umsetzen:**
- pro NPC max 1 Offscreen-Satz pro Rückkehrfenster
- Format:
  - Auftrag/Ort
  - Veränderung
  - Hook/Folge
- KI-SL generiert die Fortschreibung nur bei Relevanz
- Offscreen-NPCs erzeugen keine vollständigen Nebenkampagnen, nur Echos/Hooks

**Akzeptanzkriterien:**
- spätere Wiederbegegnungen haben sichtbare Veränderung
- Spieler bekommen das Gefühl, dass die Welt weiterlief
- JSON bleibt klein

---

## Copy-Paste-Issue 5 – Kontinuitätsrückblick um NPC-Lagebild erweitern

**Titel:** Mehrfach-Load um NPC-Lagebild ergänzen

**Ziel:**
Beim Rejoin soll sofort klar sein, wer da ist, wer fehlt und was sich bei bekannten NPCs geändert hat.

**Umsetzen:**
- Pflichtausgabe beim Mehrfach-Load erweitern:
  1. Session-Anker
  2. Rückkehrer/Joiner
  3. NPC-Lagebild
  4. gemeinsame Nachwirkungen
  5. Konvergenz-Folge (falls aktiv)
- NPC-Lagebild nennt:
  - anwesende NPCs
  - offscreen/zugewiesene NPCs
  - neue Spuren oder sichtbare Veränderungen

**Akzeptanzkriterien:**
- Rejoins lesen sich wie eine echte Fortsetzung
- bekannte NPCs fühlen sich nie „vergessen“ an

---

## Copy-Paste-Issue 6 – Alte Reset-Makros entfernen

**Titel:** Veraltete Gruppen-Reset-Pseudologik aus Toolkit entfernen

**Ziel:**
Alte Gruppenstartlogik, die Px und Seeds zurücksetzt, darf die neue Kontinuitätsphilosophie nicht mehr unterlaufen.

**Umsetzen:**
- `StartGroupMode(players=[], keep_scene=false)` entfernen oder komplett neu schreiben
- KEIN Reset mehr von:
  - `state.campaign.px`
  - `state.campaign.rift_seeds`
  - `state.arc.open_seeds`
- stattdessen nur:
  - Session-Anker übernehmen
  - Charaktere/NPCs mappen
  - Kontinuitätsrückblick triggern
  - ggf. Split-/Rejoin-Beat ausspielen

**Akzeptanzkriterien:**
- Join/Merge erzeugt keinen stillen Progress-Verlust mehr
- NPC- und Menschengruppen laufen auf derselben Philosophie

---

## Copy-Paste-Issue 7 – Physicality-Fix für Solo-Begleiter

**Titel:** Hologramm-/KI-Begleiter wording an Physicality Gate anpassen

**Ziel:**
Solo-Begleiter sollen nicht ungewollt nach externer Sci-Fi-Projektor-Ästhetik klingen.

**Umsetzen:**
- Formulierungen wie „Hologramm-Begleiter“ ersetzen durch:
  - Linsen-Lichtbild
  - Kodex-Assistenz im Sichtfeld
  - Comlink-Stimme
  - HQ-Leitfigur über physische Schnittstelle

**Akzeptanzkriterien:**
- Solo-Unterstützer bleiben möglich
- Physicality Gate bleibt unangetastet

---

## Drop-in-Text für `speicher-fortsetzung.md`

```md
### Persistente NPC-Chrononauten
NPC-Chrononauten sind keine Wegwerf-Begleiter, sondern persistente Kontinuitätsakteure des ITI.
Wenn sie die Szene verlassen, verschwinden sie nicht aus der Welt. Sie laufen als Offscreen-Agenten weiter und können später mit veränderter Lage, neuer Spur oder sichtbarer Folge wieder auftauchen.

Für v7 gilt ein kompaktes Modell:
- `continuity.npc_roster[]` hält bekannte NPC-Chrononauten fest.
- `continuity.active_npc_ids[]` markiert, welche davon aktuell als Feldbegleiter mitlaufen.
- NPCs speichern keine Vollökonomie und kein Vollinventar. Persistiert werden nur Identität, Rolle, Bindung, Status, letzte Sichtung, Offscreen-Fortschreibung und ein Hook.

Statuswerte: `attached|hq|assigned|recovering|missing|rival`
Scopes: `personal|session|iti`

Menschen belegen Feldplätze zuerst. NPCs füllen nur freie Plätze bis Teamgröße 5.
Jeder geladene Save darf NPC-Kontinuität mitbringen; aktive Feld-NPCs werden aber global nach Relevanz, Bindung und Rollenfit ausgewählt.
```

---

## Drop-in-Text für `meta/masterprompt_v6.md`

```md
- **Persistente NPC-Chrononauten:** `npc-team` erzeugt keine reinen Wegwerf-Begleiter. Wiederkehrende NPC-Chrononauten leben als kompakte Kontinuitätsobjekte in `continuity.npc_roster[]` weiter.
- **NPC-Scope:** `personal` folgt dem Save eines Spielercharakters, `session` dem Session-Anker, `iti` bleibt institutioneller Hintergrundpool.
- **NPC-Slot-Regel:** Menschen zählen immer zuerst gegen Teamgröße 5. NPCs füllen nur freie Plätze. Nicht ausgewählte bekannte NPCs bleiben als HQ-/Funk-/Offscreen-Präsenz bestehen.
- **NPC-Offscreen-Fortwirkung:** Abwesende NPCs liefern bei Wiederkehr höchstens eine kompakte Fortschreibung (Auftrag + Veränderung + Hook), aber keine vollständige Parallelkampagne.
- **NPC-Rejoin-Pflicht:** Beim Mehrfach-Load nennt der Kontinuitätsrückblick auch bekannte NPC-Chrononauten: anwesend, offscreen, verändert, fehlend.
```

---

## Drop-in-Text für `systems/toolkit-gpt-spielleiter.md`

```md
## Solo- und Gruppenkontinuität mit NPC-Chrononauten
NPC-Chrononauten sind in ZEITRISS keine bloßen Füllfiguren. Sie sind persistente Offscreen-Agenten des ITI, die Solo- und Gruppenkontinuität miteinander verweben.

Wenn ein Spieler mit NPC-Begleitern unterwegs ist, merkt sich die KI-SL diese Figuren als bekannte Mitagenten mit Rolle, Stimme, Bindung und letzter Spur. Verlässt der Spieler sie oder wechselt in eine andere Gruppe, verschwinden sie nicht still, sondern wechseln in einen nachvollziehbaren Status: `hq`, `assigned`, `recovering`, `missing` oder `rival`.

Beim späteren Wiedersehen bringt jede dieser Figuren genau eine kompakte Offscreen-Fortschreibung mit: wo sie war, was sich verändert hat und welchen Hook sie jetzt in die Szene trägt.

In gemischten Menschen-/NPC-Runden gilt:
- Menschen belegen Feldplätze zuerst.
- NPCs füllen nur freie Plätze bis Teamgröße 5.
- Jeder geladene Save darf bekannte NPC-Kontinuität mitbringen.
- `session`-NPCs hängen am Session-Anker, `personal`-NPCs an ihrem Spielercharakter.
- Nicht ausgewählte NPCs bleiben sichtbar als HQ-Präsenz, Funkkontakt oder Offscreen-Spur.

Die KI-SL fragt nur dann aktiv nach einer Auswahl, wenn es in-world Sinn ergibt. Sonst entscheidet sie automatisch nach Rollenfit, Bindung und letzter gemeinsamer Relevanz.
```

---

## Ein Satz, der dem Ganzen sofort Magie gibt

> **Chrononauten verschwinden nicht aus der Welt, wenn die Kamera sie verlässt. Wenn sie nicht bei dir im Bild sind, operieren sie anderswo im Netz.**

---

## Gesamturteil

Wenn du diese NPC-Schicht sauber einziehst, bekommt ZEITRISS genau das, was dir noch fehlt:
- Solo fühlt sich nicht mehr nach „Ersatz-Team“ an,
- Multiplayer nicht mehr nach „Host mit Gastdaten“,
- und NPCs werden zu etwas, das sich fast wie andere echte Spieler anfühlt – nur eben von der KI simuliert.

Das ist genau der Punkt, an dem die MMO-Illusion nicht mehr nur technisch clever wirkt, sondern **emotional glaubhaft** wird.
