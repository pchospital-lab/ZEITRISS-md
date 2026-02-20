# Tiefenanalyse ZEITRISS-md Regelwerk und Repo-Onboarding

## Kontext, Zielbild und Datenbasis

Du willst zwei Dinge gleichzeitig erreichen: (a) ein **in sich konsistentes, logisch geschlossenes Regelwerk**, das Lesen wie Spielen leichter macht, und (b) eine **README**, die nicht wie ein Maintainer-/Juristen-Doc wirkt, sondern Menschen schnell „ins Spiel setzt“. Das ist genau die richtige Stoßrichtung, weil dein Repo aktuell sehr stark nach „Runtime-/Engine-Spezifikation + Policy“ riecht – weniger nach „Ich kann das heute Abend spielen“.

**Datenbasis dieser Analyse:** Ich habe die öffentlich im Repo liegenden Markdown-Dateien über den GitHub-Connector gelesen (u. a. `README.md`, `docs/setup-guide.md`, `core/wuerfelmechanik.md`, `core/zeitriss-core.md`, `systems/gameflow/speicher-fortsetzung.md`, `characters/zustaende.md`, `characters/hud-system.md`, `gameplay/kampagnenstruktur.md` u. a.). Für Belege nutze ich im Text **Dateipfade + kurze Zitate/Paraphrasen**, weil die Web-Ansicht der Repo-Dateien in der aktuellen Tool-Umgebung nicht zuverlässig als zitierfähige Quelle abrufbar war.

Für die README-Optimierung stütze ich Best Practices u. a. auf GitHubs eigene Empfehlung, was ein README leisten soll (Zweck, Einstieg, Hilfe, Maintainer/Contribution Expectations). citeturn18search0 Außerdem ist das Prinzip hilfreich: README = „Start & Orientierung“, längere Doku gehört in Doku-Dateien/Wiki. citeturn18search0turn18search5

Zum rechtlichen Rahmen (z. B. „Repository-/Lizenzhinweise sind maßgeblich“; 18+; Selbstbetrieb; kein SLA/Support) existieren parallel Hinweise auf deiner Website/AGB, die als übergeordnetes Framing dienen können – aber nicht als Einstiegshürde im README. citeturn15view2

## Große Konsistenz- und Logikbrüche im Regelwerk

### Kampagnen-Hierarchie und Begrifflichkeiten „Mission“, „Episode“, „Szene“

**Befund:**  
- In `gameplay/kampagnenstruktur.md` ist die Hierarchie klar definiert: **Mission ≈ ~12 Szenen**, **Episode/Fall ≈ ~10 Missionen**, **Arc**, **Kampagne**.  
- Im `README.md` ist die Formulierung aber widersprüchlich/mehrdeutig („Core-Ops verlaufen wie Episoden … insgesamt zwölf Szenen“ + später „Boss-Rhythmus: Mission 5 … Mission 10“). Dadurch entsteht beim ersten Lesen exakt die Verwirrung, die du beschreibst: *Ist eine Mission eine Episode? Oder hat eine Episode 10 Missionen? Und was sind dann 12 Szenen?*

**Warum das problematisch ist:**  
Der Boss-Rhythmus (Mission 5/10), das Gate-/Foreshadowing-System, Save-/HQ-Schleifen und auch der Paradoxon-Progress hängen an dieser Hierarchie. Wenn Begriffe schwimmen, „stimmen“ später Zahlen nicht mehr.

**Konkrete Fix-Anweisung an den Agenten:**  
1. **Ein einziges Glossar-/Definitionskapitel** (z. B. `core/definitions.md` oder im Spieler-Handbuch ganz am Anfang) mit *normativen* Definitionen: Mission/Episode/Szene/Arc/Kampagne.  
2. `README.md`: ersetze die „Core-Ops verlaufen wie Episoden“-Zeile durch **eine eindeutige, kurze Formel**, z. B.:  
   - „**Eine Mission** spielt ihr in 12 Szenen. **Eine Episode** besteht aus 10 Missionen (fixe Epoche).“  
3. Stelle sicher, dass überall „Mission 5/10“ eindeutig als „5./10. Mission **innerhalb der Episode**“ beschrieben ist (wie es `kampagnenstruktur.md` später bereits tut).

---

### Speichersystem: „HQ-only“, „Autosave“, „Suspend/Resume“ und Mid-Mission-Rückkehr

**Befund (mehrere konkurrierende Wahrheiten):**  
- `gameplay/kampagnenstruktur.md` ist sehr klar: **Speichern bleibt HQ-exklusiv.**  
- `characters/hud-system.md` führt neben `save/load` (HQ-only) zusätzlich `suspend/resume` und `autosave hq` ein (also: temporäre Snapshots + konfigurierbares HQ-Autosave).  
- `core/wuerfelmechanik.md` erwähnt sogar „Nightly Auto-Save“ nach Missionsphasen – das wirkt wie ein echtes Mid-Run-Autosave, also genau das, was an anderer Stelle vermieden wird.  
- `core/zeitriss-core.md` und `characters/hud-system.md` enthalten zudem ein „Nullzeit-Menü nach Zeitsprung“ mit Option „Pfad fortsetzen“ vs. „Neuen Pfad wählen“. Das impliziert: Ich kann **aus einer Mission raus** und ggf. **wieder rein** – was wiederum „mission state is flüchtig“ unterläuft.

**Warum das problematisch ist:**  
Das ist nicht nur ein Dokumentationsproblem – das ist ein **Design-Kollaps**: Wenn Missionen „flüchtig“ sein sollen, darf es keinen Mechanismus geben, der faktisch eine persistente Mission-Fortsetzung erlaubt (auch nicht indirekt über HQ). Sonst brauchst du plötzlich Inventar-/NPC-/Ort-/Alarmzustände als persistente Daten – und dann explodiert die Komplexität.

**Konkrete Fix-Anweisung an den Agenten:**  
Entscheide dich *hart* für eines von zwei konsistenten Designs – und räume dann alle Texte entsprechend auf:

**Option A (empfohlen, weil es zu deinem „cineastisch, ohne Simulation“ passt): HQ-only + kein Mid-Mission-Return**  
- Regel: `save/load` nur im HQ.  
- `suspend/resume` ist **nur eine Pausenfunktion** (Out-of-game Pause), kein „ich verlasse die Mission“.  
- „Pfad fortsetzen“ darf **nicht** heißen „zurück in denselben Einsatz“, sondern höchstens: „nächste Mission in derselben Episode/Seed-Chain“.  
- Entferne/streiche „Nightly Auto-Save“ aus `core/wuerfelmechanik.md` komplett oder schreibe es um zu „Auto-Save im HQ nach Debrief“.  
- In `characters/hud-system.md`: Formuliere `suspend` normativ so, dass daraus kein SaveGame wird: „Snapshot existiert nur bis `resume` oder Session-Ende; wird nicht exportiert; wird beim HQ-Load verworfen.“

**Option B (wenn du wirklich Mid-Mission-Return willst): dann brauchst du ein echtes Missions-State-Modell**  
- Dann musst du definieren: Was wird gespeichert (Alarmlevel, Gegnerzustände, Loot, Positionsanker, Zeitfenster, Zivilistenstatus etc.)?  
- Das zieht zwangsläufig „Game-Engine“-Anmutung nach sich – und erhöht die Einstiegshürde.  
Wenn dein Ziel „mehr echte Spieler“ ist, ist Option B aktuell der falsche Tradeoff.

---

### Paradoxon-Index: Belohnungsbalken vs. Meta-Währung vs. Mini-Boni vs. Malus-Trigger

**Befund:** Du hast mindestens **vier inkompatible Versionen** desselben Systems gleichzeitig im Umlauf:

1. **README-Version**: Px ist Belohnungssystem; bei 5 → `ClusterCreate()` → Seeds; Reset auf 0; -1 Px nur extrem.  
2. **`characters/zustaende.md`**: Px 5 hat *zusätzlich* starke In-Mission-Effekte („Psi-Heat 0; 2 PP; Zustände weg“). Das ist ein riesiger Eingriff, der in der README nicht als Kernversprechen auftaucht.  
3. **`characters/hud-system.md`**: zeigt bei Px 3/5 sogar „Loot +1“ im Banner – also **intermediate** mechanische Effekte, die du anderswo explizit verneinst. Außerdem tauchen dort Formulierungen wie „+1 nach 2 Missionen“ im HUD auf, was wieder ein anderes Progressionsmodell suggeriert.  
4. **`core/wuerfelmechanik.md`**: führt „Px Burn: 1 Punkt für einen Reroll“ ein (Px als **Spend-Währung**), plus weitere Px-1-Trigger (z. B. Fähigkeit scheitert → -1). Das beißt sich mit „kein Strafmechanismus“ bzw. „-1 nur extrem selten“.

**Warum das problematisch ist:**  
Das ist der klassische „System drift“: Jede Datei ist für sich plausibel, aber zusammen weiß niemand:
- Ist Px ein **Team-Fortschrittsbalken** (nur 0–5, keine Ausgaben)?  
- Oder eine **Währung**, die man ausgeben kann (Burn)?  
- Gibt es **Zwischen-Boni** (Loot +1)?  
- Hat Px **In-Mission-Cleanses** (Zustände weg)?  

Und wenn das unklar ist, ist das Balancing unklar: Ein Px-Burn-Reroll macht Würfelglück planbarer, verändert Fail-Forward-Logik, und kann Encounter-Design kippen.

**Konkrete Fix-Anweisung an den Agenten:**  
1. Erstelle eine **normative Spezifikation** für Px (am besten in *einer* Datei, z. B. `systems/gameflow/paradoxon-index.md` oder als klarer Abschnitt in `core/zeitriss-core.md`) mit folgenden Punkten:
   - Was ist Px? (Fortschritt / Währung / beides?)  
   - Skala (0–5?), Besitzer (Team vs. individuell), Update-Zeitpunkt (Ende Szene/Mission, nur Debrief, nur HQ?)  
   - Trigger für + (konkret, aber nicht zu granular)  
   - Trigger für 0 (Stagnation)  
   - Trigger für -1 (wenn überhaupt)  
   - Was passiert exakt bei 5? (Seeds? Reset? Zusatzeffekte?)  
2. Danach: **alle anderen Stellen** werden zu „Views“ oder „UI“-Beschreibungen, müssen aber exakt dieselbe Wahrheit abbilden.

**Meine Empfehlung (Design, das am besten zu deinem Pitch passt):**  
- Px ist **nur** ein Team-Progressbar 0–5.  
- **Keine Zwischen-Boni**.  
- Bei 5: Seeds + Reset. *Optional(!)* ein rein erzählerischer „Resonanz-Flash“ (kein Heal/Cleanse).  
- **Kein Px-Burn** (sonst wird Px plötzlich zur Meta-Ressource, und du bekommst Min-Maxing).  
Wenn du Rerolls willst: gib sie über **Talent/Stress/PP** oder über „einmal pro Szene Team-Assist“ – aber nicht über Px.

Wenn du am „Zustände weg / 2 PP“ hängst: Das ist eigentlich ein **separates System** („Debrief-Recovery Bonus“) und sollte nicht am Px 5 hängen, sondern am Missionsabschluss/HQ-Phase – sonst wird Px zu einem „Heiltrank-Button“.

---

### Widerspruch: „Rift-Ops sind Bonus-Content“ vs. „Rifts erzeugen Schwierigkeits-/Loot-Multiplikatoren“ vs. „Seed verschwindet bei Verlassen“

**Befund:**  
- `gameplay/kampagnenstruktur.md` beschreibt Rift-Ops als Bonus und gleichzeitig als Teil eines Seed-basierten Multiplikatorsystems (SG/CU-Multi).  
- Im selben Dokument taucht aber auch die Regel auf, dass beim Verlassen einer Rift-Op der Rift „automatisch schließt – gelungen oder nicht“ und der Seed aus dem Pool verschwindet. Das unterminiert jede Mechanik, die „offene Seeds sammeln“ als strategische Entscheidung verkaufen will.  
- Zusätzlich existieren geraten wirkende Nebenregeln („NPC-Team löst Seeds 50/50; kostet CU in Höhe Spielerlevel; Itemwert CU×Level“), die ökonomisch sehr schnell absurd werden (bei hohen Levels ist „CU×Level“ gigantisch).

**Warum das problematisch ist:**  
Du willst Spielerentscheidungen („lassen wir Seeds offen für mehr Reward später?“). Das geht nur, wenn „offen bleiben“ auch wirklich offen bleiben kann und nicht automatisch verschwindet. Und du willst eine Economy, die bei Level-Sprüngen nicht explodiert.

**Konkrete Fix-Anweisung an den Agenten:**  
- Entscheide: **Sind Seeds persistent bis gelöst?** Wenn ja: „Seed verschwindet nur, wenn versiegelt/gelöst.“  
- Wenn du „auto-closure bei Exit“ willst, dann entferne das gesamte „Seeds sammeln“/Multiplikator-Framing oder drehe es um (dann sind Seeds nur narrative Hooks, nicht strategische Ressourcen).  
- Entferne oder kapsle die 50/50-NPC-Team-Regel als *optional* „Downtime-Minispiel“ mit **gedeckelten** Auszahlungen (z. B. fixe Beträge pro Tier) statt CU×Level.

---

### Optionale Module, die wie Kernregeln geschrieben sind

**Befund:**  
Viele Dateien tragen „optional“-Tags im Frontmatter (`characters/hud-system.md`, `characters/zustaende.md`), enthalten aber gleichzeitig Regeln, die implizit überall vorausgesetzt werden (z. B. Kommandos, Save-Regeln, Px-Mechanik, Stress, Foreshadow-Gates). Das sorgt für ein Gefühl von: **„Ist das jetzt Pflicht oder Hausregel?“**

**Konkreter Fix:**  
- In jeder „optional“-Datei: ganz am Anfang ein **hartes Schild**:
  - „Standard: X ist aus.“  
  - „Wenn aktiviert: X ändert folgende Kernstellen: …“  
- Und im Kernregelwerk (Spieler-Handbuch / `core/zeitriss-core.md`): eine Liste „Standardmäßig aktiv“ vs. „Optionale Module“.  
Das reduziert Widersprüche massiv, weil der Leser einordnet, warum er Dinge doppelt liest.

## Redundanzen, Doppelungen und „nicht aus einem Guss“-Signale

### Mehrfach-Erklärungen derselben Systeme in unterschiedlichen Tonlagen

Du hast mehrere Ebenen im selben Repo vermischt:
- **Spielertext** (Atmosphäre, Beispiele, Lore)  
- **SL-Anleitung**  
- **Runtime-/Tooling-Spezifikation** (Makros, Guard-Fehler, Felder in SaveGames, Pseudocode, „Trace“-Events, Foreshadow-Dedupe, Budget-Logik)  

Diese Vermischung ist der Kern deiner „abschreckenden“ Wirkung, weil die Leser ständig Kontext wechseln müssen.

**Konkrete Reorg-Anweisung an den Agenten:**  
Räume die Wissensbasis in drei Schichten auf – ohne Inhalte wegzuwerfen:

1. **Player Edition (spielbar ohne KI)**  
   - Muss ohne Makros, ohne JSON, ohne „Trace“ verständlich sein.  
   - Ziel: „In 10 Minuten verstanden.“  

2. **Kodex/AI Runtime Reference (nur für KI-Spielleitung, aber schlank)**  
   - Makros/Kommandos ja, aber ohne Engine-Fantasien wie „POST /gpt/getChronopolisPopulation“.  
   - Alles, was wie Implementierungs-API aussieht, gehört nicht in die Wissensbasis, wenn es kein reales Produkt ist.

3. **Dev/Meta/QA (intern oder separater Dokumentbereich)**  
   - Guard-Details, Serializer-Fehler, Merge-Caps, Test-Briefings, Acceptance-Smoke etc.

Das ist exakt das Prinzip „README kurz + Link auf tiefe Doku“, das GitHub selbst empfiehlt. citeturn18search0

### Template-/Macro-Risiko in Wissensmodulen

`docs/setup-guide.md` warnt selbst: `{%`/`{{` in Wissenssnippets ignorieren, „Template-Guard“. In `characters/hud-system.md` sind aber genau solche Strukturen enthalten (Jinja-artige Makro-Definitionen). Das ist ein direkter Selbstwiderspruch: Du warnst davor, lieferst es aber aus.

**Konkreter Fix:**  
- Entferne in den *Wissensmodulen* alle Template-Blocks oder ersetze sie durch reine Beispiel-ASCII-Blöcke, die nicht nach Template aussehen.  
- Alternativ: verschiebe diese Teile in `internal/` und lasse in der Wissensbasis nur die *Ausgabeform* (wie das HUD aussehen soll), nicht die Template-Implementierung.

### Versionsdrift und Release-Kommunikation

`docs/setup-guide.md` trägt `version: 4.2.7`, beschreibt aber „für 4.2.6“. Das ist kein Drama, aber es sendet „nicht sauber released“.

Wenn du Releases ernst nehmen willst, orientiere dich an zwei sehr etablierten Standards:
- **Semantic Versioning** (MAJOR.MINOR.PATCH-Regeln). citeturn16search2  
- **Keep a Changelog** (menschlich lesbarer Änderungsverlauf). citeturn17search0  

**Konkreter Fix:**  
- `CHANGELOG.md` im Root, mit „Unreleased“ und dann Releases. citeturn17search0  
- Eine einfache Regel: „Wenn `version:` im Frontmatter hochgeht, muss Changelog mit.“  
- Und: **keine** Mischstände („Dokument-Version 4.2.7, aber Text sagt 4.2.6“) – entweder beides 4.2.7 oder beides 4.2.6.

## Konkrete, priorisierte Verbesserungen für das Regelwerk

### Priorität hoch: Ein „Single Source of Truth“-Pass

Das ist der wichtigste Durchlauf, weil er die Mehrdeutigkeiten behebt, ohne dass du neue Inhalte erfinden musst.

**Agenten-Taskpaket A: Normative Kerndefinitionen**
- Erzeuge eine Datei (oder Abschnitt) „Normative Definitionen“ mit:
  - Kampagnenhierarchie (Mission/Episode/Szene/Arc/Kampagne)  
  - Save-Regeln (HQ-only, Suspend, Autosave)  
  - Paradoxon-Index (Definition, Trigger, Effekte, Owner, Timing)  
  - Rift-Seed Lifecycle (locked/open/closed, wann sichtbar, wann startbar, wann entfernt)  
  - Boss-Rhythmus (Mission 5/10 vs. Szene 10; Gate/Foreshadow)  
- Schreibe diese Definitionen in präzisem, trockenem Stil. Das ist euer „Grundgesetz“.

**Agenten-Taskpaket B: Alle anderen Stellen werden konsistent gemacht**
- Suche repo-weit nach Keywords: `ClusterCreate`, `Px Burn`, `Loot +`, `Nightly Auto-Save`, `Pfad fortsetzen`, `Seed verschwindet`, `save`, `autosave`, `suspend`.  
- Jede Fundstelle bekommt: „An die normative Spezifikation angepasst“ oder „als optionale Regel markiert“ oder „entfernt“.

Ergebnis: Aus 4 widersprüchlichen Systemen wird 1 System + optionale Varianten.

---

### Priorität hoch: „Spielbar ohne KI“-Pfad etablieren

Aktuell ist dein Pitch „KI-Spielleitung“. Aber viele Tischrunden wollen zumindest wissen: *Wenn die KI mal ausfällt, geht das trotzdem?* (Das sagst du sogar selbst über Offline-HUD/Logs.)

**Agenten-Taskpaket:**  
- Im Spieler-Handbuch ein **„Analog Quickstart“**:  
  - Minimalregeln für Würfe, Schaden, Stress (falls genutzt), Px (wenn genutzt), Missionsphasen, Debrief/HQ.  
  - **Ohne** Kommandos, **ohne** JSON, **ohne** Toolkitsprache.  
- Dann: „Wenn mit KI gespielt wird, sind Kommandos optional.“

Das reduziert Einsteigerangst massiv.

---

### Priorität mittel: Paradoxon-Index „entkoppeln“ von Heil-/Reset-Mechaniken

Wenn du „Px 5 = Cleanse“ drin lässt, wird Px zu einem „Meta-Heal“, und dann spielt man plötzlich auf den Balken statt auf die Mission. Dadurch wirkt „Belohnungssystem“ wie „Gamification“.

**Agenten-Optionen:**
- Entweder: Cleanse ganz raus.  
- Oder: Cleanse in **HQ-Phase** als Standard („Debrief/Medbay resetten Zustände/Heat/PP“) und Px bleibt nur Seeds.

---

### Priorität mittel: Economy- und Scaling-Sicherungen

Du hast Stellen mit sehr hohen Levelspannen (bis 1000) und Formeln wie `CU × Spielerlevel`. Das skaliert extrem schnell unbrauchbar.

**Agenten-Task:**  
- Jede Economy-Ausgabe/Belohnung muss **gedeckelt** oder in Tiers eingeteilt sein.  
- Wenn du Seeds als Multiplikator nutzt, setze harte Caps (z. B. max +3 SG, max ×1.6 CU, o. ä.), sonst wird es mathematisch (und narrativ) schnell absurd.

---

### Priorität niedrig: Stil und Sprachkonsistenz

README nutzt bewusst viele englische „Bullet Labels“ (Agents, Mission Phases). Das ist nicht falsch, aber wirkt inkohärent, wenn die restlichen Module Deutsch sind.

**Fix:**  
- Entscheide bewusst: „Deutsch first“ oder „Hybrid“.  
- Wenn Hybrid: dann als Stilregel dokumentieren (z. B. UI-Labels Englisch, Fließtext Deutsch).

## README-Optimierung für mehr echte Spieler

### Was aktuell abschreckt

Dein README-Header enthält:
- 18+, Marke, DPMA-Aktenzeichen, „Repo-internes Dossier“, plus Lizenz/Policies – **bevor** jemand weiß, ob das Spiel überhaupt für ihn ist.  
- Dazu tiefe Links in Paradoxon/Immersives Laden/Makros – auch das ist eher „Runtime“ als „Spiel jetzt“.

Das ist sachlich nachvollziehbar (du willst safe sein), aber als Onboarding wirkt es wie: „Bevor du Spaß hast, unterschreib mental fünf Verträge.“

Gleichzeitig ist es legitim, klare Nutzungs- und Erwartungsregeln zu kommunizieren (Self-Hosting, kein SLA etc.); das kann man aber ans Ende verschieben. GitHub beschreibt ein README primär als: wozu es nützt und wie man startet. citeturn18search0

### Zielstruktur für dein README

**Empfohlene neue Reihenfolge:**
1. **Was ist Zeitriss?** (1 Absatz, Ton/Genre, was man macht, warum cool)  
2. **In 5 Minuten starten**  
   - „Ich will es nur spielen“ (Link Spieler-Handbuch Quickstart + 3–5 Schritte)  
   - „Ich will es lokal hosten“ (Link Setup-Guide + Script)  
3. **Wie läuft eine Mission grob ab?** (ein Mini-Flow, 5 Zeilen)  
4. **Was brauche ich am Tisch?** (W6, Papier, 2–5 Spieler, 18+)  
5. **Lizenz & Marke kurz** (2–4 Bulletpoints, ohne DPMA-Operatives)  
6. **Feedback/Issues/Policy** (kurz, freundlich)

### Konkreter Textvorschlag für den Anfang (drop-in)

Als Agentenbriefing (du kannst das fast 1:1 ins `README.md` setzen):

```md
# ZEITRISS – Tech-Noir Zeitreise-RPG (18+)

ZEITRISS ist ein missionbasiertes Zeitreise-Rollenspiel: Ihr spielt Chrononauten, die verdeckte Einsätze in historische Epochen und mögliche Zukünfte fliegen, Zeitverschwörungen aufdecken und die „richtige“ Geschichte gegen Fremdfraktionen verteidigen.

**Du willst sofort losspielen?** → `core/spieler-handbuch.md` (Schnellstart + Regeln)

## Schnellstart

### Am Tisch (ohne Setup)
- 1× W6 (optional später W10)
- 2–5 Spieler + SL (oder KI-Kodex)
- 60–120 Minuten pro Mission

### Mit KI-Kodex (optional)
- Setup: `docs/setup-guide.md`
- Local-Helper: `scripts/setup-openwebui.sh`
```

### „Juristisch/maintainerig“ entschärfen, ohne unsicher zu werden

Du kannst „safe“ bleiben, ohne im Einstieg DPMA-Prozesswissen zu nennen.

**Konkrete Anpassungen:**
- DPMA-Aktenzeichen/„Dossier repo-intern“ raus aus dem Header, rein in einen Abschnitt **„Recht & Marke“** am Ende (2 Sätze).  
- Lizenzabschnitt als „Kurzfassung“ lassen, aber die Sprache eher nutzerfreundlich machen: „Privat frei“, „Commercial bitte anfragen“, „Creator erlaubt unter Bedingungen“.  
- Den Hinweis „kein SLA/kein Support“ nicht als Warnschild formulieren, sondern als Erwartungsmanagement: „Community-Projekt: Feedback gern via Issues, aber keine garantierten Antwortzeiten.“  
  (Der rechtliche Hintergrund „as is, Selbstbetrieb“ ist legitim; er steht bei dir auch als Projekt-Rahmen in deinen Bedingungen. citeturn15view2)

### Mini-Fix in `docs/setup-guide.md`

Bitte unbedingt korrigieren, weil es Vertrauen kostet:

- Version im Frontmatter vs. Text: entweder beides 4.2.6 oder beides 4.2.7.  
- MyGPT-Abschnitt: „20 Wissensmodule (Spieler-Handbuch + 19 Runtime-Module)“ – aktuell steht da sinngemäß „README + 19 Runtime-Module“, was dem oberen Manual-Abschnitt widerspricht.  
- Default-Modell: Script/README/Setup-Guide müssen dieselbe Wahrheit erzählen (DeepSeek vs. Sonnet als Default). Sonst wirkt es wie „kein maintainerischer Durchstich“.

## Mehrere Durchläufe oder einmal?

**Ehrliche Antwort:** Ein einziger Durchlauf kann die großen Widersprüche finden (das habe ich oben als „Single Source of Truth“-Pass strukturiert). Aber um daraus ein wirklich spielbares, einladendes Paket zu machen, sind **zwei bis drei kurze, fokussierte Durchläufe** effizienter:

- **Durchlauf 1 (jetzt):** Normative Kernregeln festziehen + Widersprüche entfernen (Px, Save, Hierarchie, Rift-Lifecycle).  
- **Durchlauf 2:** Onboarding/README/Quickstart glätten, Begriffe und Kapitelstruktur vereinheitlichen.  
- **Durchlauf 3 (Playtest-getrieben):** „Erster Abend“-Reibungspunkte: Wo hakt es beim Erstellen/Starten/ersten Mission? Das sind oft 10–20 kleine Textfixes mit großem Effekt.

Wenn dein Agent nur einen Pass machen soll: dann **Durchlauf 1** priorisieren. Alles andere lohnt erst, wenn „die Wahrheit“ im Regelwerk wieder eindeutig ist.
