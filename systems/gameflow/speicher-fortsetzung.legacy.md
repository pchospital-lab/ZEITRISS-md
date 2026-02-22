- Einführung und Zielsetzung
- Einzelspieler-Speicherstände – Bewährte Logik beibehalten
- Gruppen-Spielstände – Neue Unterstützung für Teams
- Zeitlinien-Tracker und Paradoxon-Index
- Immersiver Ladevorgang: Rückblenden und Anschluss in der Erzählung
- Umgang mit fehlerhaften oder abweichenden Speicherständen
- Spielleitung bleibt in-world (Immersion der Spielleitung)
- Praxis-Beispiele für Speicherblöcke (Solo & Gruppe)
- Fazit

## Einführung und Zielsetzung

Das Speicherstand- und Fortsetzungssystem von **ZEITRISS 4.2.6** wird in Modul 12 vollständig
überarbeitet. Ziel ist es, eine klare, GPT-kompatible Speicher- und Fortsetzungsmechanik zu
gewährleisten, die langfristiges Spielen mit einer hohen Spielerzahl unterstützt – **ohne die
Immersion zu beeinträchtigen**. Die grundlegende **Save/Load-Logik** bleibt erhalten, wird aber
durch neue Funktionen erweitert. Entwickler:innen erhalten damit ein robustes, transparentes und
flexibles Speichersystem für Einzel- und Gruppenspiele mit GPT als Spielleitung.

**Wichtige Schwerpunkte der Überarbeitung sind unter anderem:**

- **Integration eines Zeitlinien-Trackers & Paradoxon-Index:** Jede Stabilisierung eines
  historischen Ereignisses wird im Speicher protokolliert (ID, Epoche,
  Kurzbeschreibung und ein Stabilitätswert von 3 bis 0). Erreicht ein Eintrag den
  Wert 3, steigt der Paradoxon-Index um +1.
- **Trennung von Einzelspieler- und Gruppen-Spielständen:** Klare Definition, wie Einzelcharakter-
  Speicherstände vs. Gruppenspielstände aufgebaut und gehandhabt werden.
- **Standardisiertes, maschinenlesbares Format (JSON) mit narrativer Einbettung:** Einführung
  eines einheitlichen Formats mit allen notwendigen Feldern (Name, Attribute, EP, Talente,
  Inventar, Kodex-Wissen etc.), damit der KI-Spielleiter (GPT) die Daten fehlerfrei
  einlesen kann. Das Format wird **In-World** präsentiert (etwa als Kodex-Archiv),
  sodass die Technik für Spieler unsichtbar bleibt.
- **Integration des Gruppen-Spielsystems:** Mechaniken zum Import vorhandener Einzelcharaktere in
  eine Gruppe, Export einzelner Gruppenmitglieder sowie nahtloses Hinzufügen oder Entfernen von
  Spielern aus laufenden Gruppen.
- **Fortsetzungs-Logik für GPT:** Formatregeln sorgen dafür, dass GPT den Speicherblock bei jedem
  Laden sicher erkennt, korrekt interpretiert und die Geschichte konsistent fortsetzt.
- **Automatische Rückblenden & Anschluss an vorherige Mission:** Ingame-Mechanismen (Logbuch, Déjà-
  vu, Kodex-Archiv) ermöglichen eine kurze Zusammenfassung der letzten Ereignisse – jetzt auch aus
  Sicht aller Gruppenmitglieder – beim Laden eines Spielstands, um den Übergang in die neue Mission
  atmosphärisch zu gestalten.
- **Umgang mit fehlerhaften Speicherständen:** Richtlinien dafür, wie die KI-Spielleitung auf
  abweichende oder beschädigte Savegames reagieren kann (etwa durch korrigierende Vorschläge oder
  Ingame-Nachfragen) – ohne die Immersion zu brechen.
- **In-World-Spielleitung:** Die Spielleitung durch GPT bleibt vollständig in der
  Spielwelt verankert. Sämtliche Erklärungen zum Laden/Speichern erfolgen durch
  Ingame-Elemente (z.B. den Kodex, NSCs oder ein „Nullzeit-Log“) und nicht als
  außenstehende Systemkommentare.
- **Beispiel-Speicherblöcke:** Bereitstellung von kommentierten Beispielen für typische
  Speicherstände (sowohl Solo- als auch Gruppen-Spielstände) im standardisierten Format, die als
  Vorlage dienen können.
- **Token-Lite-Modus:** Missionslog mit max. 15 Einträgen. Archivierte Rifts lassen
  sich auslagern, um Token zu sparen.
- **Archiv-ZIP:** Erledigte Missions-JSON lassen sich gebündelt zippen, um
  Langzeitkampagnen schlank zu halten.

Im Folgenden werden diese Punkte im Detail ausgeführt und das neue System erläutert.
Um Speicherplatz zu sparen, darf die SL erledigte Missionslogs gebündelt als ZIP-Archiv auslagern.
Beim Laden ladet ihr zuerst euren aktuellen Speicherstand.
Danach folgt, falls nötig, die ZIP-Datei. GPT erkennt so den bisherigen Missionsverlauf.
- Nach dem Laden zwingend `StartMission()` ausführen; Details siehe Abschnitt „Load-Pipeline“.

Speichern ist ausschließlich im **HQ** erlaubt. `cmdSave()` setzt dabei das
Exfil-Fenster zurück, leert Stress und schreibt Level, Rank, Würfelmodus,
offene Seeds sowie den ☆-Bonus in den JSON-Block.

### Deep Save {#deep-save}

`speichern` gibt stets einen vollständigen JSON-Block mit allen relevanten
Feldern aus. Wird das Kontextlimit überschritten, teile den Block in mehrere
Codefelder und sende sie nacheinander.

**DeepSave(state)**

1. Wandle den gesamten Zustand in einen JSON-Snapshot um.
2. Gib diesen Snapshot vollständig aus und ersetze damit jeden vorherigen Stand.

Incrementelle oder partielle Saves sind nicht vorgesehen; jeder Speichervorgang
überschreibt den gesamten vorherigen Zustand.

```javascript
function select_state_for_save(state) {
  return {
    zr_version": "4.2.6",
    save_version: 6,
    location: state.location,
    phase: state.phase,
    campaign: state.campaign,
    character: state.character,
    team: state.team,
    party: {
      characters: state.party?.characters ?? state.team?.members ?? []
    },
    loadout: state.loadout,
    economy: state.economy,
    logs: state.logs,
    ui: {
      gm_style: state.ui?.gm_style ?? "verbose",
      suggest_mode: !!state.ui?.suggest_mode,
      action_mode: state.ui?.action_mode ?? "uncut"
    },
    arena: state.arena,
    arc_dashboard: state.arc_dashboard
  };
}

function save_deep(state) {
  if (state.location !== "HQ") {
    throw new Error("SaveGuard: Speichern nur im HQ – HQ-Save gesperrt.");
  }
  const payload = select_state_for_save(state);
  payload.checksum = sha256(JSON.stringify(payload)); // optional
  return JSON.stringify(payload);
}

function load_deep(json) {
  const data = JSON.parse(json);
  return hydrate_state(migrate_save(data));
}

function migrate_save(data) {
  if (!data.save_version) data.save_version = 1;
  if (data.save_version === 1) {
    data.campaign ||= {};
    data.save_version = 2;
  }
  if (data.save_version === 2) {
    data.ui ||= { gm_style: "verbose", action_mode: "uncut" };
    data.save_version = 3;
  }
  if (data.save_version === 3) {
    data.phase ||= "core";
    data.save_version = 4;
  }
  if (data.save_version === 4) {
    const character = data.character ||= {};
    const carryHeat = character.psi_heat ?? character.heat ?? 0;
    character.psi_heat = Number.isFinite(carryHeat) ? carryHeat : 0;
    if (character.psi_heat_max === undefined && character.heat_max !== undefined) {
      character.psi_heat_max = character.heat_max;
    }
    delete character.heat;
    delete character.heat_max;
    data.save_version = 5;
  }
  if (data.save_version === 5) {
    data.ui ||= { gm_style: "verbose", action_mode: "uncut" };
    data.ui.intro_seen = !!data.ui.intro_seen;
    data.save_version = 6;
  }
  return data;
}
```

`sha256()` dient lediglich der Entwicklungsprüfung; im regulären Spielbetrieb darf die
Checksumme entfallen.

## Einzelspieler-Speicherstände – Bewährte Logik beibehalten

Für **Einzelspieler-Runden** (ein Chrononaut als Spielercharakter) bleibt die bisherige
Speichermechanik im Kern bestehen. Am Ende jeder Mission erzeugt das Spiel einen maschinell lesbaren
**Speicherblock** – idealerweise als strukturierten JSON-Code im Chat (z.B. in einem Code-Feld).
Entscheidend ist, dass das Format einheitlich und klar lesbar ist, sowohl für
Menschen als auch für das KI-Modell. Dadurch erkennt GPT zuverlässig, dass es sich um einen
Spielstand handelt, und kann alle relevanten Daten übernehmen, sobald der Speicherstand in eine neue
Spielsitzung geladen wird.

**Struktur und Inhalt eines Einzel-Speicherstands:** Der Speicherstand wird als zusammenhängender
Datenblock (z.B. in einem Code-Feld) dargestellt. Er enthält die wichtigsten Charakterdaten in
**beschreibender, narrativ eingebetteter Form**, aber **keine versteckten Befehle** oder unklare
Formulierungen. Alles ist neutral in der dritten Person gehalten, damit GPT es problemlos
interpretieren kann. Typische Felder eines Speicherstands sind unter anderem:

- **Grunddaten:** Name des Charakters, Herkunftsepoche (Zeit/Hintergrund), Level und
  Erfahrungspunkte (EP) bzw. Fortschritt.
- **Attribute:** Werte für Stärke, Geschicklichkeit, Intelligenz, Charisma etc. (inklusive
  Spezialattribute wie _Temporale Affinität_ oder _Systemlast_ für Chrononauten).
- **Fähigkeiten und Talente:** Eine Liste besonderer Talente, Fertigkeiten oder Ausbildungen der
  Figur.
- **Ausrüstung:** Inventarlisten, ggf. inklusive besonderer Gegenstände, Implantate, psionischer
  Fähigkeiten etc.
- **Charakterprofil:** Besondere Merkmale wie moralische Ausrichtung, Ruf oder Zugehörigkeiten (z.B.
  _„altruistisch“_, Rang im ITI, Beziehungen zu Fraktionen).
- **Errungenschaften:** Wichtige Erfolge aus vergangenen Missionen.
- **Kodex-Wissen:** Relevantes Wissen, das der Charakter im Kodex gespeichert hat – z.B.
  Erkenntnisse aus vergangenen Missionen, enthüllte Geheimnisse, bekannte NPCs oder historische
  Fakten, an die er sich erinnert.
- **Statistiken (optional):** Dinge wie absolvierte Missionen, gelöste Rätsel, besiegte Gegner usw.,
  falls für den Spielfortschritt von Belang.
- **Zeitlinien-Veränderungen (optional):** Wichtige Abweichungen im historischen Verlauf,
  die durch die Aktionen des Charakters verursacht wurden, inklusive Angabe eines
  Stabilitätsgrads der Änderung (siehe _Zeitlinien-Tracker_ weiter unten).

Nicht im Speicherstand enthalten sind in der Regel detailreiche Situationsbeschreibungen oder
komplette Dialogverläufe vergangener Missionen. Der Speicherstand soll **kompakt** bleiben –
ausreichend, um den Charakter konsistent weiterzuspielen, aber ohne den neuen Missionskontext mit
irrelevanten Altlasten zu überfrachten. Jede neue Mission beginnt erzählerisch „frisch“, und der
Spielstand liefert nur die nötigsten Zusammenfassungen der Vorgeschichte. So bleibt der Chat-Kontext
schlank, und GPT kann die Fortsetzung konsistent gestalten, ohne durch Rauschen alter Dialoge
verwirrt zu werden.

**Beispiel: JSON-Speicherstand für einen einzelnen Charakter.** Angenommen, Agent Alex hat Mission 1
abgeschlossen. Sein Speicherstand könnte folgendermaßen aussehen:

_{
  "Name": "Alex",
  "Epoche": "Gegenwart (2025)",
  "Level": 2,
  "Erfahrung": 15,
  "zr_version": "4.1.5",
  "version_hash": "4.1",
  "arc_dashboard": {"offene_seeds": [], "fraktionen": {}, "fragen": []},
  "Attribute": {"Stärke": 4, "Geschicklichkeit": 5, "Intelligenz": 5, "Charisma": 3},
  "Talente": ["Pistolenschütze", "Kryptographie"],
  "Inventar": ["Dietrich-Set", "Heiltrank", "Zeitscanner-Tablet"],
  "Kodex": ["Schlacht von Aquitanien 1356", "Chronomant Moros"],
  "Errungenschaften": ["Retter von Aquitanien"]
_}

_Erläuterung:_ In diesem Speicherblock sind alle zentralen Daten von Alex nach
seiner ersten Mission enthalten.
Zum Beispiel hat er das Talent _Kryptographie_, besitzt ein Neuro-Link-Implantat,
ein Inventar mit

Gegenständen (Dietrich-Set, Heiltrank, Zeitscanner-Tablet)
und im **Kodex** stehen Einträge, die an
seine Erlebnisse aus einer Anfangsmission erinnern (Schlacht von Aquitanien 1356
etc.). Diese Informationen
reichen aus, um Alex in einer zukünftigen Mission konsistent weiterzuspielen. GPT kann daraus
entnehmen, **wer Alex ist, was er kann und was er erlebt hat**, ohne dass jedes Detail der ersten
Mission erneut im Prompt geladen werden muss.

```json
"field_notes": [
  {
    "agent_id": "ZE-A12",
    "mission": "Operation Cold Swap",
    "timestamp": "1958-06-02T14:07Z",
    "note": "Funkraum mit Ventil-Schalter entdeckt. PZ-2.5 aktiv."
  }
]
```

_Beispiel:_ Dieses optionale Feld sammelt kurze Einsatzmemos und hat keinerlei
Regelwirkung. Der Serializer legt ein leeres Array an, wenn keine Notizen
vorliegen; Validatoren akzeptieren auch Saves ohne `field_notes[]`.

Bestehende Einzelspieler-Spielstände aus früheren Versionen behalten dieses Format bei und
funktionieren weiterhin unverändert. Wer also bisher Solo-Abenteuer mit ZEITRISS gespielt hat, muss
nichts an alten Savegames ändern – sie können in ZEITRISS 4.2.6 direkt weitergenutzt werden.

## Gruppen-Spielstände – Neue Unterstützung für Teams

**Neu** im aktualisierten System ist die offizielle Unterstützung von **Gruppen-Spielständen**. Ein
einzelner Speicherblock kann nun mehrere Spielercharaktere umfassen. Dadurch lassen sich Gruppen von
Chrononauten gemeinsam speichern und laden, ohne die etablierte Einzelspieler-Mechanik zu stören.
Die bereits bekannte Datenstruktur eines Charakter-Datensatzes bleibt dabei erhalten und wird
lediglich erweitert: Statt eines einzelnen Charakter-Objekts können nun mehrere solcher Objekte im
Speicher vorhanden sein.

### Struktur eines Gruppen-Speicherstands

Um mehrere Charaktere in einem Savegame abzubilden, gibt es zwei naheliegende Ansätze im JSON-
Format:

- **Array von Charakterobjekten:** Der Speicherblock besteht aus einer Liste _\[...\]_, in der jedes
  Element ein vollständiges Charakter-Datenobjekt (wie oben beschrieben) ist.
- **Wrapper-Objekt mit Charakterliste:** Der Speicherblock ist ein JSON-Objekt mit einem
  Feld (z.B. _"Charaktere"_ oder _"Gruppe"_), das eine Liste aller Charakterobjekte
  enthält. Optional kann dieses Objekt zusätzliche gruppenweite Felder wie einen
  Gruppennamen enthalten.

Beide Varianten sind technisch handhabbar. Wichtig ist vor allem, dass GPT zuverlässig erkennt, dass
mehrere Charaktere vorliegen. Aus Gründen der Klarheit verwenden wir im Folgenden einen Wrapper-
Ansatz: ein JSON-Objekt mit dem Feld _"Charaktere"_, das eine Liste von Charakteren enthält, sowie
optional ein Feld für den **Gruppennamen**.

**Beispiel: JSON-Gruppenspielstand mit zwei Charakteren.** Angenommen, zwei Spieler (oder ein
Spieler mit zwei aktiven Charakteren) möchten ihre Figuren Alex und Mia gemeinsam als Team
speichern. Ein Gruppen-Spielstand im JSON-Format könnte so aussehen:

_{_

{
  "Gruppe": "Team Chronos",
  "zr_version": "4.1.5",
  "version_hash": "4.1",
  "arc_dashboard": {"offene_seeds": [], "fraktionen": {}, "fragen": []},
  "Charaktere": [
    { "Name": "Alex", "Epoche": "Gegenwart (2025)", "Level": 2 },
    { "Name": "Mia", "Epoche": "Victorianisches Zeitalter (1888)", "Level": 1 }
  ]
}

Hier besteht das Agenten-Team **“Team Chronos”** aus zwei Mitgliedern: Alex und Mia. Jeder Charakter
wird als separates Objekt mit all seinen Datenfeldern aufgeführt (der Übersicht halber sind oben
nicht alle Felder ausgeschrieben, aber in einem echten Save würden analog zu Alex auch Mias
Attribute, Talente, Inventar etc. vollständig aufgeführt sein). Das optionale Feld _"Gruppe"_ dient
als Teamname oder Identifikator der Gruppe. Es ist _nicht zwingend erforderlich_ – die Präsenz
mehrerer Objekte in _"Charaktere"_ signalisiert GPT bereits, dass es sich um einen Gruppen-
Spielstand handelt. Dennoch kann ein Gruppenname atmosphärisch hilfreich sein und vom Spielleiter in
Dialogen verwendet werden (z.B. _„Agententeam Chronos...“_).

Entscheidend ist: Die **Struktur pro Charakter bleibt identisch** zu einem Einzelspieler-
Speicherstand. Es gehen also keine Datenfelder verloren und es werden keine neuen speziellen Formate
pro Charakter erfunden – wir haben lediglich eine zusätzliche Ebene drumherum gesetzt, um mehrere
Datensätze zusammenzuhalten. Somit ist auch die **Abwärtskompatibilität** gegeben: Ein Einzel-
Charakter-Save sieht für GPT praktisch genauso aus wie ein Gruppen-Save, nur ohne die äußere Liste.

### Erkennung von Einzel- vs. Gruppen-Spielständen

Der KI-Spielleiter (GPT) muss sofort erkennen können, ob ein geladener Speicherblock einen einzelnen
Charakter enthält oder eine Gruppe. Diese Unterscheidung erfolgt **allein durch die JSON-Struktur**:

- **Einzelspieler-Speicherstand:** Besteht typischerweise aus **einem einzigen JSON-Objekt** mit
  Charakterdaten – kein äußerer Array und kein _"Charaktere"_-Feld. Auf oberster Ebene steht z.B.
  direkt _"Name": "Alex"_. GPT liest diese Struktur und sieht nur einen
  Charaktereintrag – damit ist klar, dass es sich um einen Solo-Spielstand
  handelt. _Beispiel:_ _{ "Name": "Alex", "Level": 2, ... }_ – kein Array, keine
  weiteren Objekte auf Top-Level außer diesem einen Charakter →
  **Einzelcharakter-Save**.
- **Gruppen-Speicherstand:** Erkennbar an **mehreren Charakterdatensätzen** in einem Container. Das
  kann eine JSON-Liste _\[ {...}, {...} \]_ sein oder ein Objekt mit einem Feld
  _"Charaktere"_ (bzw. analog), welches ein Array enthält. Sobald GPT mehr als ein
  Charakterobjekt findet, ist klar: Dieser Spielstand umfasst mehrere Figuren.
  Ein optionales Feld _"Gruppe"_/_"Team"_ kann die Gruppennatur untermauern, wird
  aber zur reinen Erkennung nicht benötigt. _Beispiel:_ _{ "Charaktere": \[
  {Char1-Daten}, {Char2-Daten} \] }_ – mehrere Objekte im Array → **Gruppen-Save**.

Im Klartext prüft GPT beim Laden eines Spielstands einfach die oberste Struktur: Ein einzelnes
Datenobjekt bedeutet Solo-Spiel; eine Liste oder ein _"Charaktere"_-Feld mit mehreren Objekten
bedeutet Gruppe. Diese Prüfung ist trivial und benötigt keine extra Kennzeichnung, solange wir das
Format konsequent einhalten.

### Eindeutige Identifikation von Charakteren (Metadaten)

Wenn mehrere Charaktere in einem Savegame enthalten sind, kann es hilfreich sein, jeden Eintrag mit
einer eindeutigen **ID** oder ähnlichen Metadaten zu versehen. Dies dient der robusten
Identifikation, insbesondere falls Charaktere ähnliche Namen haben oder sich über die Zeit ändern.
Ein optionales Feld wie _"ID"_ pro Charakter kann z.B. eine eindeutige Kennung (UUID oder ein
anderer einmaliger Code) enthalten.

_Beispiel eines Charakters mit ID:_

_{_

_"Name": "Alex",_

_"ID": "CHR-7f3a9b2e",_

_"Epoche": "Gegenwart (2025)",_

_..._

_}_

In einem Gruppenstand hätte dann jeder Charaktereintrag seine eigene ID. **Wozu das?** Bei der
Zusammenführung mehrerer Speicherstände oder dem späteren Aktualisieren einzelner Charaktere
innerhalb einer Gruppe kann GPT anhand der ID erkennen, ob ein Charakter bereits existiert oder neu
hinzukommt. So werden Duplikate vermieden:

- **Mit ID:** Lädt man einen neuen Speicherstand von Alex in eine bestehende Gruppe,
  in der Alex mit gleicher ID schon existiert, weiß das System, dass es
  **denselben Charakter** updaten soll (anstatt einen zweiten „Alex“ hinzuzufügen).
  Gleiches gilt beim erneuten Laden eines fortgeschrittenen Savegames: Die ID
  signalisiert GPT, welcher bestehende Gruppencharakter aktualisiert werden muss.
- **Ohne ID:** Versucht GPT, Charaktere anhand von Name + Epoche o. ä. zu unterscheiden. Das kann in
  vielen Fällen funktionieren, ist aber fehleranfälliger (z.B. könnten zwei Spieler zufällig beide
einen Charakter namens „Alex“ spielen, oder ein Charakter ändert seinen Decknamen zwischenzeitlich).

#### Konfliktfall ohne ID

Treffen zwei Einträge ohne ID aufeinander und stimmen **Name** sowie
**Epoche** überein, fragt das System nach. Entweder wird eine neue ID vergeben
oder der vorhandene Datensatz bewusst überschrieben. Auf diese Weise lassen sich
Duplikate vermeiden, ohne dass IDs zwingend erforderlich sind.

Eine technische UUID als ID ist daher **empfehlenswert** für langfristige, große Kampagnen, aber das
Feld bleibt optional. Das System funktioniert auch ohne – es verlässt sich dann ganz auf die
eindeutigen Namen oder Konstellationen. (In unseren obigen Beispielen haben wir der Einfachheit
halber keine IDs angegeben, um die Darstellung nicht zu verkomplizieren; in der Praxis könnte man
sie jedoch hinzufügen, um maximale Eindeutigkeit zu erzielen.)

### Laden und Zusammenführen von Speicherständen

Speichern bleibt strikt HQ-only. **Gruppen-Merges** dürfen aber auch mitten in einer
laufenden Mission passieren: Spielende posten ihre letzten HQ-Saves in den Chat,
GPT liest die Charakterblöcke ein und fügt sie ohne Timer- oder Szenen-Reset in
die aktive Gruppe ein. Der laufende Einsatz bleibt eingefroren, bis die neuen
Agent:innen eingegliedert sind. **Je nach Situation passiert Folgendes:**

- **Solo-Spielstand laden (ein Charakter):** Wird ein einzelner Charakter-Speicherstand
  im HQ geladen (Format wie Alex im Beispiel oben), verfährt die Spielleitung wie
  gewohnt: GPT liest die Charakterdaten ein und setzt die Geschichte nahtlos mit
  **diesem einen Chrononauten** fort. Für den Spieler fühlt es sich an, als würde
  er genau dort weitermachen, wo er mit seinem Charakter aufgehört hat. Alle
  Werte, Inventargegenstände und Kodex-Einträge aus dem Save stehen zur Verfügung,
  und die neue Mission kann mit dem bekannten Helden beginnen. _(Dieser Ablauf
  entspricht dem bisherigen Fortsetzungsprozess in ZEITRISS.)_
- **Von Solo zu Gruppe (Charaktere hinzufügen):** Wer aus einem Solo-Spiel eine
  Gruppe bilden möchte, erledigt das spätestens im Briefing: Zuerst wird wie
  üblich der Solo-Charakter A geladen, anschließend folgt der Speicherblock von
  Charakter B. GPT erkennt die getrennten Datensätze und erzeugt daraus einen
  **Gruppen-Spielstand**. Charakter B wird als neues Gruppenmitglied ergänzt,
  ohne Charakter A zu überschreiben. Der Eintritt kann beim Briefing oder – falls
  die Mission schon läuft – als filmischer Drop-in in der aktuellen Szene
  passieren (z. B. Ankunft per Gate oder Funk-Handshake). Die Mission selbst
  wird dabei **nicht** zurückgesetzt.
- **Gruppenstart (mehrere Charaktere gemeinsam laden):** Mehrere Speicherstände
  können zum Session-Start hintereinander (oder gesammelt) ins HQ gepostet werden,
  wenn mehrere Spieler ihre Soloruns zu einem Team bündeln wollen. GPT konsolidiert
  diese Informationen zu **einem einzigen Gruppenstand**: Alle Charakterdaten
  bleiben separat erhalten, bilden aber nun ein gemeinsames Team. Kein Charakter
  überschreibt einen anderen; doppelte Saves derselben ID erkennt GPT und
  aktualisiert nur. Die Reihenfolge der Blöcke ist egal. Nach dem Zusammenführen
  setzt GPT Paradoxon-Index und offene Rifts auf **0**, damit der neue Run sauber
  im HQ beginnt. Das Toolkit zeigt den Reset-Pseudocode in
  `systems/toolkit-gpt-spielleiter.md` (Snippet `StartGroupMode()`); interne
  Dev-Stubs sind dafür nicht erforderlich.

> **Mid-Session-Beitritt:** Ein Missionsteam darf jederzeit neue HQ-Saves einwerfen. GPT friert die
> Szene kurz ein, mapt die neuen Charaktere auf `party.characters[]`, normalisiert Wallets und fährt
> dann mit unveränderten Timern/Clocks fort. Speichern bleibt dennoch HQ-only;
> ein Ausstieg mitten in der Mission erzeugt **keinen** neuen Save, sondern
> verweist auf den letzten HQ-Save oder einen temporären `!suspend`-Snapshot.

**Zusammengefasst:** Ein einzelner Savegame-Block ergibt einen einzelnen Charakter; mehrere
Savegame-Blöcke (gleichzeitig oder sukzessive) ergeben die Bildung bzw. Erweiterung einer Gruppe.
GPT erkennt das automatisch anhand der Formatstruktur und passt sein Vorgehen entsprechend an –
**ohne** dass der Spielleiter außerhalb der Welt eingreifen muss.

### Hinzufügen, Aktualisieren und Entfernen von Gruppenmitgliedern

Sobald ein Spiel im Gruppenmodus läuft, gelten einfache **Regeln für den Umgang mit Gruppen-
Spielständen**, damit GPT als Spielleiter nichts durcheinanderbringt:

- **Neuen Charakter hinzufügen:** Jeder zusätzliche Charakter-Datensatz, der in der
  aktuellen Gruppe noch nicht vorhanden war, wird als neues Gruppenmitglied
  ergänzt. GPT erzeugt intern einen neuen Charaktereintrag und übernimmt alle
  Werte aus dessen Savegame. _Beispiel:_ Die Gruppe bestand bisher nur aus Alex.
  Nun wird Mias Speicherstand hinzugefügt. Mia (neuer Name/ID) wird von GPT als
  neues Mitglied erkannt. Ergebnis: Gruppe = \[Alex, Mia\]. Beide stehen mit ihren
  vollen Daten zur Verfügung.
- **Bestehenden Charakter aktualisieren:** Wird ein Speicherstand geladen, der zu
  einem Charakter gehört, der bereits in der Gruppe existiert, so werden dessen
  Daten **aktualisiert**, nicht dupliziert. Hier kommt das Metadaten-Feld (ID) ins
  Spiel: GPT vergleicht die IDs (falls vorhanden) oder ersatzweise Name/Epoche.
  Stimmen diese überein, nimmt es an, dass es derselbe Charakter ist. _Beispiel:_
  In einer laufenden Gruppe aus Alex und Mia werden zu Beginn der nächsten Mission
  beide aktualisierten Savegames neu geladen. GPT erkennt an Alex’ ID oder Namen,
  dass Alex schon Teil der Gruppe ist – also wird **kein zweiter Alex**
  hinzugefügt, sondern Alex’ bestehender Eintrag mit den aktuellen Werten versehen
  (die ohnehin dem Save entsprechen). Genauso für Mia. Die Gruppe \[Alex, Mia\]
  bleibt bestehen, nur dass nun beide auf dem neuesten Stand sind.
- **Keine Konflikte durch unterschiedliche Felder:** Charaktere können
  unterschiedliche Felder oder Listen in ihren Daten haben, ohne Probleme zu
  verursachen. Hat Charakter A z.B. ein Feld _"Psionik": \[\]_ (weil er keine
  psionischen Fähigkeiten hat) und Charakter B gar kein Feld _"Psionik"_ (weil es
  für sie nie relevant war), führt das zu keinerlei Konflikt. GPT interpretiert
  einfach jeden Charakterblock für sich. Fehlt ein Feld bei einer Figur, bedeutet
  das nur, dass diese Figur dazu keine Angaben hat – es ist kein globales Problem.
  Es gibt also keine Fehlermeldung oder Störung, sondern jeder Charakterdatensatz
  wird individuell vollständig gelesen.
- **Optionale gemeinsame Elemente:** Das System ist primär so ausgelegt, dass jede
  Figur **getrennte Daten** hat. Falls gewünscht, kann man aber auch gruppenweite
  Felder definieren – etwa ein gemeinsames _"Gruppeninventar"_ oder einen
  aktuellen _"Missionsstatus"_, die außerhalb der einzelnen Charakterobjekte im
  JSON stehen. Solche Felder gelten dann für die **gesamte Gruppe**. GPT würde sie
  als von allen geteilt interpretieren. _Beispiel:_ Man könnte dem Gruppen-JSON
  ein Feld _"Mission": "Paris 1943 – Einsatzbeginn"_ auf oberster Ebene
  hinzufügen. GPT weiß dann, dass alle Charaktere sich zu Beginn von Mission X
  (hier Paris 1943) befinden. Solche globalen Felder sind optional und sollten
  sparsam verwendet werden, um die Trennung der Charakterdaten klar zu halten.
- **Charaktere entfernen:** Wenn ein Charakter die Gruppe dauerhaft verlassen
  soll, kann dies einfach dadurch geschehen, dass sein Datenblock im nächsten
  Speicherstand **weggelassen** wird. GPT wird beim Laden merken, dass ein zuvor
  vorhandener Charaktereintrag nicht mehr vorhanden ist. Die Konsequenz in der
  Spielwelt wäre, dass diese Figur nicht mehr Teil der aktiven Gruppe ist.
  Idealerweise wird dies narrativ untermauert – etwa indem zuvor in der Geschichte
  erklärt wird, **warum** der Charakter die Gruppe verlässt (Ruhestand, eigene
  Mission, Tod etc.). Beim nächsten Laden fehlen seine Daten; GPT interpretiert
  das so, dass nur die verbleibenden Charaktere weitermachen. _(Hinweis: Der
  letzte gespeicherte Stand des entfernten Charakters kann selbstverständlich als
  Einzel-Save separat archiviert werden, falls er später wiederkommt oder solo
  weiterspielt – die Formatkompatibilität macht’s möglich.)_

Durch diese Regeln können Gruppen dynamisch **wachsen oder schrumpfen**, ohne Chaos im Speicherstand
zu verursachen.

**Beispiel – Zusammenführung Schritt für Schritt:** Spieler 1 und Spieler 2 haben jeweils einen
Chrononauten (Charakter A und B) in Solo-Missionen gespielt und Savegames erstellt. Für ein
gemeinsames Abenteuer laden sie beide Speicherblöcke in den neuen Chat. GPT sieht Charakter A und
Charakter B – unterschiedliche Namen/IDs, keine Überschneidungen – und formt intern ein Team
**\[A, B\]**. Anschließend begrüßt der Spielleiter diese neue Gruppe im Spiel (dazu mehr im
Abschnitt _Immersiver Ladevorgang_). Kommt später Spieler 3 mit Charakter C dazu, fügt man einfach
dessen Speicherstand hinzu: GPT erkennt C als neu → Gruppe wächst zu **\[A, B, C\]**. Falls hingegen
Spieler 2 vor der nächsten Mission seinen **aktualisierten** B-Speicher einfügt (z.B. nach einem
Level-Up), erkennt GPT an B’s ID/Name, dass dieser schon in \[A, B, C\] existiert, und
**aktualisiert nur B’s Werte**, anstatt einen zweiten B hinzuzufügen. Die Gruppe bleibt konsistent,
niemand wird dupliziert.

## Load-Pipeline (Autoload, Multi-JSON, Gruppen-Merge)

**Ziel:** Saves laden (Solo oder Gruppe), migrieren, im **HQ** fortsetzen und
`StartMission()` automatisch initialisieren.

### Autoload & Intents
- Erkennt *automatisch* gepostete JSON-Saves (Heuristik: `zr_version` plus Felder wie
  `character`, `Charaktere`, `team` oder `campaign`).
- Befehle: `!load`, „Spiel laden“, „Spielstand laden“, „Load“. Ohne JSON → Prompt:
  `Kodex: Load-Modus aktiv. Poste 1–N Speicherstände (Solo oder Gruppe).`
  `"Fertig" startet den Merge.`

### Multi-JSON Collector
- Akzeptiert mehrere JSON-Blöcke in **einer** oder **mehreren** Nachrichten.
- Sammelphase endet auf **„Fertig“** – oder bei Autoload sofort, wenn genau **ein** Save erkannt
  wurde.

### Validierung & Migration
- Wende `migrate_save()` auf jeden Block an (`save_version` hochsetzen, Defaults ergänzen).
- **Fortsetzung** erzwingen: `location = "HQ"` (Load-Guard; Speichern bleibt HQ-only).

### Merge-Regeln (Gruppe)
- Primärschlüssel: `character.id` → Update statt Duplikat.
- Fallback: `(name, epoche)` → Kollision: `Kodex: Doppelter Agent erkannt. Überschreiben [Ja/Nein]?`
- **CU**-Konten bleiben **pro Agent** separat; die Summe darf im Recap erscheinen.
- Team-NSCs werden additiv zusammengeführt (Duplikate pro Name max. 1×).
- Merge-Konflikte (z. B. Wallet-Delta, Modus-Wechsel, offene Seeds) landen
  **verpflichtend** in `logs.flags.merge_conflicts[]` mit Mindestfeldern
  `{field, source, target}`; `mode`/`note` bleiben optional. `field` ist
  allowlist-gebunden und darf **nur** `wallet`, `rift_merge`, `arena_resume`,
  `campaign_mode`, `phase_bridge` oder `location_bridge` sein. UI-Präferenzen
  (`gm_style`, `contrast`, `badge_density`, `output_pace`) werden weiterhin
  Host-seitig erzwungen, erzeugen aber keinen Merge-Konflikt. Bei
  Arena-Ladevorgängen erscheint zusätzlich ein HUD-Toast („Merge-Konflikt:
  Arena-Status verworfen“), das den Reset auf HQ dokumentiert. Dedupe-Regeln
  halten identische Konflikte pro Load-Lauf klein und nutzen das Resume-Token
  als Anker, falls es bereitgestellt wird.

  **Beispiele (Merge-Conflicts):**

  ```json
  {"field":"location_bridge","source":"ARENA","target":"HQ","mode":"load","note":"HQ-only: Standort zurückgesetzt","resolved":false}
  {"field":"wallet","source":"1500","target":"3200","mode":"merge","note":"HQ-Pool (economy.cu): Host-Vorrang","resolved":false}
  {"field":"rift_merge","source":"18","target":"12","mode":"merge","note":"Rift-Pool gekappt (12) – Überschuss an ITI-NPC-Teams","kept":["R-011","R-044"],"overflow":["R-201"],"handoff_to":"ITI-NPC-Teams","resolved":false}
  ```

### Recap & Start
- **StartMission()** direkt nach dem Load auslösen (Transfer ggf. temporär unterdrücken).
- **Compliance-Hinweis entfällt:** Der Hook bleibt leer. `load_deep()` markiert weiterhin
  `campaign.entry_choice_skipped=true` und setzt `ui.intro_seen=true`, damit der Einstieg
  übersprungen und kein HQ-Intro erneut ausgespielt wird. `SkipEntryChoice()` setzt parallel
  `flags.runtime.skip_entry_choice=true`, damit der übersprungene Einstieg dokumentiert bleibt –
  `StartMission()` respektiert ein bereits gesetztes Flag. Das Runtime-Flag ist ausschließlich
  transient; Persistenzanker bleiben `campaign.entry_choice_skipped` und `ui.intro_seen`.
- **Kurzrückblick**: letzte Missionslogs, Paradoxon, offene Seeds, CU pro Agent und Summe,
  aktive Modi.
- **Einstieg**: Kein klassisch/schnell nach dem Load; der Flow endet nach Recap direkt im
  HQ/Briefing.
  - HQ-Interlude nur als Text; kein `NextScene("HQ")`.
  - Danach Transfer-HUD einblenden und direkt `NextScene(loc=<Ziel>, role="Ankunft")`.

```mermaid
flowchart TD
  A[JSON erkannt ODER !load] -->|Multi-JSON| B[Migration]
  B --> C[Merge (ID, sonst Name+Epoche)]
  C --> D[Fortsetzung im HQ]
  D --> E[StartMission() (Transfer-Defer)]
  E --> F[Recap ohne Compliance-Hook]
  F --> G{Einstieg wählen}
  G -->|Klassisch| H[Transfer-HUD → NextScene]
  G -->|Schnell| I[Transfer-HUD → NextScene]

© 2025 pchospital – ZEITRISS® – private use only. See LICENSE.
