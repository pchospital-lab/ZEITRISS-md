# ZEITRISS – Hard Final Review

## Gesamturteil

ZEITRISS läuft jetzt rund. Nicht im Sinn von „jede KI macht nie einen Fehler“, sondern im entscheidenden Sinn: Das Repo verhält sich inzwischen wie ein eigenes Produkt mit klarem Betriebsmodell. README, Spieler-Handbuch, SL-Referenz, Save-System, Masterprompt und Toolkit erzählen weitgehend dieselbe Betriebswahrheit: **MMO ohne Server**, **Save = Charakter**, natürlicher Neustart oder Kurzform, `klassisch` als Default, `generate` / `custom generate` / manuell, HQ-DeepSave, Session-Anker, persönliche Wahrheit, Kontinuitätsrückblick, NPC-Kontinuität und kein automatischer Sprung ins nächste Briefing nach dem Save. ([GitHub][1])

Für deine Zielgruppe ist das jetzt nicht mehr bloß ein cooles KI-Experiment, sondern schon sehr nah an einem eigenständigen Format. Ich würde dir aber nicht schönreden, es sei schon unangreifbar oder objektiv „das beste Textspiel aller Zeiten“. Es hat jetzt etwas Wertvolleres: eine klar erkennbare Identität und echtes Ausnahme-Potenzial.

## Was bereits außergewöhnlich gut ist

Der Startpfad ist inzwischen deutlich sauberer als früher. README und Handbuch sagen klar: Man muss vor dem ersten Run nicht erst das Regelwerk lesen, OpenWebUI + Preset reichen, natürlicher Start ist erlaubt, `klassisch` ist Standard, und die eigentliche Charaktererstellung läuft über `generate`, `custom generate` oder manuell. Die SL-Referenz und das Toolkit ziehen das mit und behandeln `schnell` nur noch als explizite Fast-Lane. ([GitHub][1])

Auch der Chatbetrieb ist endlich fast genau dort, wo er hinmusste: Save ist HQ-only, `!save` ist die harte Exportkante, neuer Chat pro Mission ist klar empfohlen, nach savebarem HQ-Zustand gibt Kodex genau einmal den DeepSave-Hinweis, und danach folgt kein automatisches Briefing. Genau das macht das System stabil, ohne wieder wie ein altes Savegame-Menü zu wirken. ([GitHub][2])

Am stärksten ist der neue Kontinuitätskern. README, Save-Doku, SL-Referenz und Masterprompt tragen inzwischen denselben großen Trick: erster Save = Session-Anker, neuester Charakterstand pro `characters[].id` = persönliche Wahrheit, Mehrfach-Load erzeugt Kontinuitätsrückblick, Echo-Fortwirkung, kanonische Core-Splits per `family_id`, und NPC-Chrononauten bleiben als kompakter `npc_roster` erhalten. Das ist genau der Punkt, an dem ZEITRISS von „Chat-Kampagne“ zu „MMO-Illusion ohne Server“ kippt. ([GitHub][1])

## Was noch hakt

1. Der größte verbliebene Bruch ist immer noch ein SSOT-Widerspruch im Split-/Merge-Kanon. In `speicher-fortsetzung.md` steht erst, Split/Merge sei standardmäßig nur nach Episodenende für getrennte Rift-Ops kanonisch, später sagt dieselbe Datei aber, parallele Core-Branches innerhalb derselben Episode seien kanonisch, wenn sie dieselbe `continuity.split.family_id` tragen. README, Masterprompt und SL-Referenz sind an dieser Stelle schon weiter und behandeln Core-Parallelpfade klar als kanonischen Standard mit Konvergenz. Solange dieser Alttext in der Save-SSOT bleibt, bleibt genau der schönste Teil deines MMO-Versprechens noch interpretierbar statt hart definiert. ([GitHub][2])

2. Das Entfernen der vorgefertigten Charaktere aus dem Default-Stack war richtig — aber die Grundlagen der Charaktererschaffung referenzieren das optionale Modul `charaktererschaffung-optionen.md` weiterhin mehrfach für zusätzliche Optionen, Hominin-/Abstufungsdetails, Teamrollen und Archetypen-Anregungen. README sagt gleichzeitig ausdrücklich, dass genau diese Datei nur noch optionales Inspirations-/Fallback-Material und nicht Teil des Default-Wissensspeichers ist. Das ist ein echter Runtime-Haken: Ein geladenes Kernmodul verlässt sich noch auf ein standardmäßig nicht geladenes Hilfsmodul. ([GitHub][1])

3. Die größte verbleibende „Oldschool-/Repo-Denke“ sitzt nicht mehr im Save-System, sondern im Runtime-Ballast. AGENTS sagt klar, die KI-SL sieht nur die Wissensmodule plus Masterprompt; trotzdem enthalten produktive WS-Dateien noch Dev-/QA-/Inspirationsteile: `speicher-fortsetzung.md` referenziert interne QA-Fixtures und Test-Saves, das Toolkit verweist auf `internal/qa`-Fixtures und Start-Transkripte, `kampagnenstruktur.md` bezeichnet sich selbst offen als Regel- und Inspirationsmodul, und `cinematic-start.md` enthält breite Meta- und Stilberatung samt Variantenkatalog. Das Material ist nicht schlecht — aber im aktiven Laufzeitkontext kostet es Fokus, Präzision und deterministisches Verhalten. ([GitHub][3])

4. Es gibt noch einen kleinen, aber echten Einstiegskanon-Drift. `charaktererschaffung-grundlagen.md` setzt inzwischen sauber: alle neuen Chrononauten starten neutral beim Ordo Mnemonika, und es gibt keinen Fraktionswahlzwang bei der Erstellung. `cinematic-start.md` formuliert aber noch „Sobald die Fraktionswahl steht …“, als wäre dieser alte Startgedanke weiter gültig. Das ist klein, aber genau solche halben Altspuren sind später die Quelle für „KI hat sich was ausgedacht“. ([GitHub][4])

5. Ein weiterer kleiner Drift steckt im Kampagnenmodul selbst. Ganz oben verkauft es noch die „Weiterentwicklung eines gemeinsamen Hauptquartiers“, später stellt dieselbe Datei korrekt klar: Das HQ ist eine feste Nullzeit-Anlage, kein Bauprojekt; Fortschritt läuft über Zugänge, Lizenzen, Freigaben und Beziehungen. Das bricht das Spiel nicht mehr, ist aber noch ein unnötiger Rest aus einer älteren Denke. ([GitHub][5])

6. Rein maintainer-seitig gibt es noch einen Doku-Drift beim Wissensspeicher: README spricht im Default von 19 Wissensmodulen, AGENTS von 20 Slots mit Spieler-Handbuch plus 19 Runtime-Modulen. Das stört die Spielwelt nicht, aber genau solche Setup-Zahlen sollten an dieser Stelle nicht auseinanderlaufen. ([GitHub][1])

## Was ich jetzt nicht mehr bauen würde

Ich würde jetzt bewusst keine große neue Mechanik mehr einführen. ZEITRISS ist an dem Punkt, an dem zusätzliche Systeme eher Schaden anrichten könnten als Nutzen. Der Kern ist stark genug. Der nächste Gewinn kommt nicht aus „noch einer cleveren Regel“, sondern aus Schärfung, Vereinheitlichung und besserer KI-Nutzung des schon vorhandenen Kontinuitätsmaterials.

## Was ich als nächsten echten KI-Vorteil bauen würde

Wenn du noch einen echten KI-nativen Schritt willst, dann keinen neuen Subsystem-Block, sondern einen kleinen **Director-Layer**: Vor jedem Briefing genau **ein** personalisierter Relevanzsatz, der aus `history.milestones`, `reputation`, `roster_echoes`, `shared_echoes`, `npc_roster` oder dem letzten Debrief zieht, warum genau diese Crew diesen Auftrag bekommt oder warum genau diese Lage jetzt für sie brennt. Die Daten dafür sind im v7-System längst da — Charaktergeschichte, Echos, NPC-Roster und Kontinuitätskapsel sind bereits angelegt. Ich würde nur noch die harte Regel ergänzen, daraus vor jedem Auftrag sichtbar genau einen Autorenmoment zu machen. Das wäre billig, maximal KI-native und würde die lebende Dienstwelt noch einmal deutlich verstärken. ([GitHub][6])

## Harte Priorität, in genau dieser Reihenfolge

1. `speicher-fortsetzung.md` auf einen einzigen Split-/Merge-Kanon kürzen: Core-Splits mit `family_id` sind kanonisch, der alte „nur nach Episodenende Rift“-Satz muss raus oder explizit zum Legacy-/Fallback-Fall umgeschrieben werden. ([GitHub][2])

2. `charaktererschaffung-grundlagen.md` von Default-unloaded Abhängigkeiten befreien: Entweder die wirklich benötigten Teile aus `charaktererschaffung-optionen.md` in die Grundlagen spiegeln oder alle Verweise auf optionales Material klar als Zusatzlektüre markieren. ([GitHub][1])

3. Dev-/QA-/Inspirationsmaterial aus dem aktiven Runtime-Kanon ziehen oder hart als nicht-runtime markieren: interne Fixtures, Start-Transkripte, Meta-Hinweise, Session-0-Beratung und zu breite Einstiegskataloge gehören nicht in dieselbe Schicht wie Save-SSOT und Dispatcher-Verhalten. ([GitHub][3])

4. Den Einstieg endgültig auf einen einzigen Produktpfad zuschneiden: natürlicher Neustart oder Kurzform, `klassisch` als Default, `generate/custom generate/manuell`, dann HQ oder Briefing. Alles andere darf als optionale Fast-Lane oder Inspirationsmaterial existieren, sollte aber nicht mehr wie ein gleichrangiger Startmodus im Kern herumstehen. ([GitHub][1])

5. Danach den kleinen Director-Layer einziehen. Nicht früher. Erst wenn SSOT und Runtime-Schärfe sitzen, wirkt der zusätzliche Personalisierungsbeat wie Magie und nicht wie weiterer Rausch. ([GitHub][6])

## Schlussurteil

Ja: ZEITRISS läuft jetzt rund.
Nein: Es ist noch nicht „fertig“ im absoluten Sinn.
Aber: Es ist jetzt an einem Punkt, an dem die Welt nicht mehr auseinanderfällt, sobald man Save, Gruppensplit, NPC-Kontinuität und neuen Chat zusammendenkt. Das ist der eigentliche Durchbruch.

Wenn du die fünf Punkte oben noch sauber ziehst, bleibt am Ende nicht mehr nur ein cooles KI-Projekt, sondern etwas, das für deine Zielgruppe sehr schwer zu toppen sein wird.

[1]: https://raw.githubusercontent.com/pchospital-lab/ZEITRISS-md/main/README.md "raw.githubusercontent.com"
[2]: https://raw.githubusercontent.com/pchospital-lab/ZEITRISS-md/main/systems/gameflow/speicher-fortsetzung.md "raw.githubusercontent.com"
[3]: https://raw.githubusercontent.com/pchospital-lab/ZEITRISS-md/main/AGENTS.md "raw.githubusercontent.com"
[4]: https://raw.githubusercontent.com/pchospital-lab/ZEITRISS-md/main/characters/charaktererschaffung-grundlagen.md "raw.githubusercontent.com"
[5]: https://raw.githubusercontent.com/pchospital-lab/ZEITRISS-md/main/gameplay/kampagnenstruktur.md "raw.githubusercontent.com"
[6]: https://raw.githubusercontent.com/pchospital-lab/ZEITRISS-md/main/meta/masterprompt_v6.md "raw.githubusercontent.com"
