---
title: "ZEITRISS 4.2.6 - Modul 5A: Zustände & erweiterte Systeme"
version: 4.2.6
tags: [characters, optional]
---

# ZEITRISS 4.2.6 - Modul 5A: Zustände & erweiterte Systeme

## Inhalt

- - Zustände und Statuseffekte - Heilung & Erholung - klassisch, filmisch, high-tech - Initiative-
  Systeme: klassisch, cineastisch oder szenisch - Stress, Paradoxon und mentale Belastungen -
  Ressourcenmodelle: Ausdauer & PP-Pool (optional) - Besonderheiten im Zeitstrom: Unterbrechungen,
  Reaktionen & freie Aktionen

In **Teil 2** der überarbeiteten Modul 5-Regeln fokussieren wir uns auf erweiterte Systeme, die Euer
ZEITRISS-Spiel noch vielseitiger und filmischer machen. Von **Zuständen** wie Verwundungen oder
Erschöpfung über **Heilung & Erholung** in verschiedenen Stilen bis hin zu alternativen
**Initiative-Systemen** und optionalen Modulen für **Stress**, **Paradoxon-Resonanz** und **mentale
Auswirkungen** - all diese Elemente könnt Ihr modular einsetzen. Die HUD-Spezifikation und das
Interface-System sind im Modul [Cinematisches HUD & Interface-System](hud-system.md) gebündelt. Alle
neuen Module bleiben dem ZEITRISS-Stil treu: **atmosphärisch dicht, erzählerisch fokussiert und doch
leichtgewichtig** in der Anwendung.

## Zustände und Statuseffekte

Charaktere in ZEITRISS können von verschiedenen **Zuständen** betroffen sein - seien es physische
Verletzungen, Erschöpfung, temporale **Destabilisierung** oder psychische **Traumata**. Solche
Zustände wirken sich sowohl erzählerisch als auch regeltechnisch aus. Hier die wichtigsten Zustände
im Überblick:

- - **Verwundungsstufen:** ZEITRISS nutzt **10 LP (Lebenspunkte)** als Basis, die gleichzeitig die
  **Verletzungsstufe** bestimmen. Jede Stufe hat typische Symptome und **Mali**,
  die die Leistungsfähigkeit beeinträchtigen, sowie entsprechende Erholungszeiten:

  > | LP | Stufe | Malus |
  > |---:|-------|------:|
  > | 10 | Unverletzt | 0 |
  > | 7-9 | Leicht verletzt | -1 |
  > | 4-6 | Mittel verletzt | -2 |
  > | 1-3 | Schwer verletzt | -3 |
  > | 0 | Kritisch | - (keine Aktionen, Not-Rückholung) |

  - - **Unverletzt:** Keine nennenswerten Wunden - vielleicht ein Kratzer oder blauer Fleck, aber
    **nichts, was den Charakter einschränkt**. _System:_ **Keinerlei Abzüge**; alle Aktionen und
    Bewegung normal. _Heilung:_ Keine besondere Behandlung nötig - der Chrononaut ist **sofort
    wieder einsatzbereit** (höchstens ein kurzer Check im HQ-Medi-Lab). - **Leicht verletzt:**
    Oberflächliche Wunden (Schürfwunden, kleine Schnitte, Prellungen). **Leichter Schmerz** ist
    spürbar, Adrenalin hält einen aber auf den Beinen. _System:_ **-1 Malus** auf feine oder
    konzentrationsintensive Aktionen (es fällt etwas schwerer, sich 100%ig zu fokussieren),
    ansonsten **keine großen Einschränkungen**; Bewegung weiterhin normal. Das HUD ergänzt
    automatisch `Wundmalus -1` in eure nächsten Würfelbefehle. _Heilung:_ Solche Blessuren heilen
    oft **innerhalb einer Szene oder bis zur nächsten Mission** von selbst. Im HQ genügt ein
    Desinfektionsspray, Verband und eine Nacht Ruhe - zum Start der nächsten Mission sind leichte
    Wunden meist **automatisch verheilt**. - **Mittel verletzt:** Deutlichere Verletzungen oder
    starke Prellungen (z.B. tiefer Schnitt, klaffende Platzwunde, verstauchter Knöchel). **Schmerz
    und Ablenkung** nehmen zu. _System:_ **-2 Malus** auf die meisten Proben, besonders körperliche.
    Keine Vollleistung mehr: Sprinten ist z.B. nicht möglich, nur noch normales Tempo; auch die
    Konzentration ist merklich gestört. Das HUD fügt `Wundmalus -2` an jede Würfelabfrage an. Der
    Charakter bleibt **funktionsfähig, aber spürbar gehandicapt**. _Heilung:_ Mittlere Wunden
    brauchen **eine HQ-Phase Erholung** oder medizinische Hilfe. Im HQ werden Verletzungen genäht,
    geschient oder mit regenerativen Salben behandelt. Nach einer HQ-Phase intensiver Behandlung
    (oder im Medi-Tank) kann der Malus auf -1 gelindert werden; nach einer längeren HQ-Phase Ruhe
    ist der Charakter wieder voll hergestellt. Mit futuristischer Medizin (z.B. Nanodocs als
    Belohnung oder gegen Ressourcen/Kosten) lässt sich die Heilung beschleunigen - mittlere Wunden
    könnten dann sogar innerhalb einer Szene schließen. - **Schwer verletzt:** Lebensbedrohliche
    Wunden (tiefe Stich-/Schussverletzungen, starker Blutverlust, komplizierte Brüche). Der
    Charakter steht **kurz vor dem Zusammenbruch**, zittert vor Schmerz und Erschöpfung, kämpft ums
    Bewusstsein. _System:_ **-3 Malus** auf **alle** Aktionen; Fortbewegung nur noch sehr
    eingeschränkt möglich (max. halbes Tempo, oft nur mit Hilfe). Die **Konzentration bricht ein**,
    nur grundlegende Handlungen wie Abstützen, Kriechen oder reines Abwehren sind noch durchführbar
    - an gezielten Kampf oder komplexe Aktionen ist kaum zu denken. Das HUD hängt automatisch
    `Wundmalus -3` an jede Probe an. _Heilung:_ Schwere Verletzungen erfordern
    **intensivmedizinische Betreuung**. **Im Feld wäre ein Agent in diesem Zustand kaum
    überlebensfähig**, doch hier greift das ITI- Notfallprotokoll: **Sinkt ein Chrononaut im Einsatz
    auf 0 Lebenspunkte**, initiiert das System **automatisch einen Zeitriss zur Not-Rückholung**.
    Der Verwundete wird in Sekundenbruchteilen ins HQ gezogen, wo ein Ärzteteam bereitsteht, um sein
    Leben zu retten. Die Mission ist für diesen Agenten damit **beendet**, aber er überlebt
    stabilisiert. Im HQ folgen dennoch **mehrere HQ-Phasen Genesung** (ggf. im Medi-Tank oder
    künstlichen Koma). Selbst mit Zukunftsmedizin und Biotech bleibt es eine bedeutende Ausfallzeit
    - unter Umständen muss der Charakter eine kommende Mission aussetzen (in einer langen Kampagne
    könnte der Spieler in der Zwischenzeit einen Ersatzcharakter steuern). **Narben** bleiben fast
    immer zurück, ob physisch oder psychisch. - **Kritisch verletzt:** Zustand jenseits von "schwer"
    - der Charakter schwebt **in akuter Lebensgefahr**. Schwere innere Verletzungen, zertrümmerte
    Gliedmaßen oder **multiple Trauma** zeichnen dieses Bild. _System:_ **Keine regulären Aktionen
    mehr möglich.** Der Charakter driftet an der Bewusstlosigkeit entlang - Tunnelblick, Blut
    spucken, versagende Körperfunktionen. Er bricht schließlich **bewegungsunfähig** zusammen;
    **alle Proben scheitern automatisch**, solange dieser Zustand anhält. _Heilung:_ **Ohne
    sofortige Hilfe tritt der Tod ein.** Auch hier greift die ZEITRISS-Notfall-Mechanik: Das ITI
    initiiert umgehend eine **Not-Rückholung** per Zeitriss. Innerhalb von Augenblicken wird der
    Sterbende ins HQ gezogen, wo die Ärzte bereits auf ihn warten. In besonders brenzligen Fällen
    dreht das ITI die persönliche Zeit des Charakters sogar ein Stück zurück - die Extraktion
    erfolgt aus einem Moment **Sekunden vor der tödlichen Verwundung**, um bessere
    Stabilisierungschancen zu haben (natürlich nur, wenn dies kein Paradoxon auslöst). Für die
    Kampagne heißt das: Der Charakter **überlebt knapp**, ist aber **schwer gezeichnet**. Die
    Genesung dauert sehr lange, und bis zur völligen Einsatzfähigkeit vergehen mitunter **zahlreiche
    Missionen**. **Bleibende Schäden** sind wahrscheinlich (Narben, Verlust von Gliedmaßen etc., die
    evtl. durch **Cyberware** ersetzt werden). Solch ein Vorfall sollte als einschneidendes
    dramatisches Ereignis ausgespielt werden - etwa als Anlass für Charakterentwicklung (z.B. Angst
    vor dem nächsten Einsatz, posttraumatische Belastung) oder als Aufhänger für Upgrades (der Agent
    erhält z.B. einen Cyber-Arm, um den verlorenen Arm zu ersetzen).

_Hinweis:_ In einem erzählerisch fokussierten Spiel muss man nicht jede Verletzung tabellarisch
auswürfeln - die obigen Stufen reichen als Richtlinie. Wichtig ist, dass die **Konsequenzen
spürbar** werden, ohne den Spielfluss zu bremsen. Spielercharaktere sterben dank ITI-Protokoll **so
gut wie nie "off-screen"** durch Zufall - das Abenteuer wird eher mit dramatischer Rettung und ggf.
langfristigen Folgen fortgesetzt, anstatt mit einem abrupten Todeswurf.

- - **Erschöpfung:** Neben Wunden kann **Übermüdung oder Auszehrung** den Charakter beeinträchtigen.
  Lange Missionen ohne Pause, Schlafentzug, übermäßiger Einsatz von Kräften oder schlicht
  Erschöpfung nach Kampf können zu einem **Erschöpfungs-Zustand** führen. _System:_ Pro Stufe
  Erschöpfung (vom SL nach Lage vergeben) erhält der Charakter z.B. **-1 auf alle Aktionen**,
  vergleichbar einer leichten Verletzung. Mehrfache Erschöpfung stapelt sich bis zur völligen
  **Erschöpfung/Ausgebrannt**-Stufe, wo der Charakter eventuell handlungsunfähig wird. _Erholung:_
  Erschöpfung kann durch **Ruhe, Schlaf oder Erholungsphasen** im HQ abgebaut werden. Eine kurze
  Verschnaufpause im Einsatz (eine Runde ohne Aktionen, etwas Wasser, ggf. ein Aufputschmittel) kann
  1 Stufe mildern. Vollständige Erholung erfolgt in der Regel nach einer **ausgeschlafenen Nacht**
  oder durch medizinische Stimulanzien. Stimulanzien (z.B. Koffein-Injektionen oder futuristische
  Energie-Booster) können kurzfristig Erschöpfung negieren - oft um den Preis eines späteren
  "Zusammenbruchs", wenn die Wirkung nachlässt (optionale Regel).

- - **Temporale Destabilisierung:** ZEITRISS-Agenten arbeiten mit der Zeit - doch temporale
  Phänomene können auch ihnen zusetzen. **Destabilisierung** bezeichnet einen Zustand, in dem der
  **Zeitstrom um (oder in) einem Charakter ins Wanken gerät**. Ursachen können ungefilterte
  temporale Energien, Zeitreisen ohne ausreichende Schutzmaßnahmen oder temporale Waffen/Implantate
  sein. Destabilisierte Charaktere erleben **Desorientierung, Déjà-vus oder gar Sekundenbruchteile
  des "Aus-der-Zeit- Fallens"**. _Effekt:_ Je nach Schwere erhält der Charakter **Abzüge auf
  Aktionen** (z.B. -1 bis -3) und der SL kann beschreiben, wie die Person sporadisch **flimmert oder
  phasenversetzt** erscheint. In schweren Fällen könnte der Charakter **kurz aus der aktuellen
  Zeitlinie gerissen** werden (z.B. für ein paar Spielrunden "geistabwesend" oder an einem falschen
  Ort/anderen Zeitfragment auftauchend). _Stabilisierung:_ **Gegenmaßnahmen** umfassen spezielle
  **Temporalfelder oder Kalibrations-Module**, die das ITI im HQ oder per Gadget bereitstellen kann.
  Durch eine **Synchronisation im HQ** (ein kurzer Aufenthalt im Zeitlabor) lässt sich
  Destabilisierung meist beheben. Innerhalb des Spiels kann die KI-Spielleitung über das HUD warnen
  ("Temporale Instabilität detektiert!") und die Effektstärke anzeigen. Destabilisierung sollte als
  spannendes **zeitrelevantes Hindernis** eingesetzt werden - z.B. tickt die Zeit gegen das Team,
  bis alle wieder stabilisiert sind.

- - **Trauma & mentale Nachwirkungen:** Nicht jede Wunde ist sichtbar - die Psyche der Charaktere
  kann durch Erlebnisse **Schaden nehmen**. Nach besonders **schockierenden Ereignissen** (etwa
  einer knapp überlebten kritischen Verletzung, Begegnungen mit grauenhaften Paradoxa oder dem
  Verlust eines Teammitglieds) kann ein Charakter ein **mentales Trauma** entwickeln. _Effekt:_ Das
  kann als anhaltender **Malus ("Traumatisiert") oder Nachteil** dargestellt werden - z.B.
  Schlafstörungen, Flashbacks oder Angst, die in bestimmten Situationen Abzüge verursacht. Im Spiel
  könnte ein traumatisierter Charakter etwa einen **Nervenflattern-Malus** erhalten: -1 auf
  Aktionen, wenn die Erinnerungen hochkochen (z.B. sobald wieder eine ähnliche Gefahr droht).
  _Verarbeitung:_ Traumata sollten im Rollenspiel **aufgearbeitet** werden können. Im HQ gibt es
  sicher **psychologische Betreuung** durch ITI-Therapeuten; auch kameradschaftliche Gespräche im
  Team können helfen. Schritt für Schritt kann der Malus so verringert oder ganz aufgehoben werden
  (eventuell pro HQ- Phase einen Malus-Punkt abbauen, wenn sinnvoll ausgespielt). Wichtig ist, diese
  **Charakterentwicklung** auszuspielen: Ein Agent, der z.B. in einer Epoche gefoltert wurde, könnte
  zunächst eine **Angst vor dieser Epoche** haben - was er in der nächsten Mission durch Mutproben
  und Unterstützung der Gruppe überwindet. Solche mentalen Auswirkungen machen die Charaktere
  facettenreicher, sollten aber **sparsam und einfühlsam** eingesetzt werden (das Spiel soll Spaß
  machen, keine Therapie erzwingen).

- - **Schock:** Kurzzeitige Lähmung durch Schmerz oder Trauma. _Effekt:_ -2 auf alle mentalen
  Proben, bis Ruhe oder Erste Hilfe den Zustand lindert.

- - **Vergiftung & Toxine:** Einige Waffen oder Fallen wirken über Giftstoffe. _Effekt:_ Pro Runde
  1W6 Schaden oder -1 bis -3 auf Aktionen, abhängig von Potenz. Ein erfolgreicher Medikit-Einsatz
  oder Antidot stoppt die Wirkung. - **Enttarnt:** Die Tarnung ist aufgeflogen. Stealth-Manöver sind
  tabu, bis ein Safehouse oder die nächste HQ-Phase erreicht wurde.

## Heilung & Erholung - klassisch, filmisch, high-tech

Verletzungen und Erschöpfung sind Teil des Abenteuers, doch wie man damit umgeht, kann tonal
variieren. ZEITRISS bietet mehrere **Heilungsstile**, von realistisch bis cineastisch. Die Gruppe
kann wählen, was am besten passt, oder die Stile kombinieren:

- - **Klassische Erholung:** Im **klassischen Modus** wird Heilung relativ **realistisch und
  zeitintensiv** behandelt. Charaktere erholen sich durch **Ruhe, medizinische Behandlung und
  Zeit**. Eine schwere Verletzung kann bedeuten, dass der Agent für den Rest der laufenden Mission
  ausfällt und erst nach wochenlanger HQ-Reha wieder voll einsatzfähig ist. Dieser Ansatz erhöht die
  Konsequenzen von Schaden - jede Wunde zählt, Ressourcen wie Verbandszeug oder Medikits sind
  wichtig. Spieler müssen Risiken gut abwägen, da **tödliche Konsequenzen** nicht immer durch Wunder
  abgewendet werden. _Spielfokus:_ Dieser Modus eignet sich, wenn Ihr **mehr Herausforderung und
  Survival-Feeling** wollt. Die Spielleitung kann offen kommunizieren, wie lange Heilung dauert
  (z.B. "Das wird mindestens eine HQ-Phase dauern"), und die HQ-Phase nutzen, um Genesungsszenen
  auszuspielen.

- - **Filmische Heilung:** Im **cineastischen Stil** steht die **Dramaturgie über der Realität**.
  Helden fallen nicht einfach sinnlos um - **dramatische Rettungen** und schnelle Erholungen sind
  möglich, wenn es der Story dient. ZEITRISS unterstützt dies durch das ITI-Notfallprotokoll
  (automatische Rettung via Zeitriss bei 0 LP) und durch cinematic Tricks: etwa ein **Adrenalin-
  Stoß** in letzter Sekunde, der dem Charakter erlaubt, trotz schwerer Wunde **noch eine finale
  Aktion** durchzuführen (vergleichbar einer Filmszene, wo der Held schwer verletzt den letzten
  Schlag führt). Heilung erfolgt hier oft "zwischen den Szenen": Nach dem Kampf schneidet man direkt
  zur Krankenstation, wo der Agent schon verbunden ist, oder man erklärt im nächsten Akt, dass ein
  **fortschrittliches Heilverfahren** ihn erstaunlich schnell wieder fit gemacht hat. _Spielfokus:_
  Dieser Modus sorgt für **hohe Immersion und Heldentum** - die Spannung entsteht durch filmreife
  Wendungen statt durch Simulation. Die SL sollte dennoch **Konsequenzen** darstellen (Narben, kurze
  Schwächephasen), aber der Erzählfluss bleibt rasant. Es kann sogar erlaubt sein, dass ein
  Charakter im Finale wieder mitmischt, obwohl er zuvor out war - sofern es **cool und glaubwürdig**
  begründet wird (z.B. mit einem High-Tech-Heilmittel). Wichtig: Alle Spieler sollten mit so einem
  **actionfilmartigen Handling** einverstanden sein, damit die Erwartungen passen.

- - **Medizinische Versorgung (klassisch und im Feld):** Dieser Aspekt gilt in beiden obigen Stilen,
  verdient aber eigene Beachtung. **Medizinische Fertigkeiten und Ausrüstung** können im Spiel
  verwendet werden, um den Heilungsprozess zu unterstützen:

  - - Im **Feldeinsatz** ermöglichen **Erste-Hilfe-Maßnahmen** das Stabilisieren Verwundeter. Ein
    Charakter mit Medikit oder medizinischem Talent kann z.B. **Blutungen stillen**, Schock
    behandeln oder sogar einen bewusstlosen Kollegen reanimieren. Das Standard-Medikit stellt dabei
    außerhalb des Kampfes **1W6 LP** wieder her (maximal 1× pro Charakter und Mission), damit
    Heilung zur 10-LP-Skala passt. Gelingt eine entsprechende Probe
    (z.B. Medizinwissen), kann der SL entscheiden, dass die Verletzungsstufe **um 1 verbessert**
    wird (aus "schwer" wird "mittel" etc.) oder dass zumindest der Sterbende bis zur Rettung
    **stabil bleibt**. Dadurch gewinnen die anderen Zeit, den Verletzten zum nächsten Zeitfenster
    für die Rückholung zu bringen. - Im **HQ** steht eine komplette **Klinik** zur Verfügung:
    Operationssäle, Autodoc-Roboter, Genesungs-Scanner und sogar **Regenerationstanks**. Hier können
    selbst kritisch verletzte Agenten mit modernster Medizin behandelt werden. Das HQ-Personal kann
    Mali deutlich schneller abbauen, als reine Ruhe es erlauben würde. (Für genaue Werte kann die SL
    entscheiden, z.B.: pro HQ-Phase Behandlung im HQ eine Verletzungsstufe verbessern.) Klinik-
    Szenen eignen sich auch erzählerisch: Man kann das Team zeigen, wie es am Krankenbett plant,
    oder den Verwundeten im Fiebertraum-Szenen haben lassen - **dramatische Erholungsszenen**
    verstärken das filmische Flair. - **Medizinisches Personal & Talente:** Einige Chrononauten sind
    ausgebildete Ärzte oder Sanitäter. Solche Charaktere sollten ihre Fähigkeiten nutzen dürfen, um
    **Heilwürfe** durchzuführen. Im Regelkontext könnte man einen **Heilungs-Wurf** erlauben (etwa
    auf INT oder ein Medizin-Attribut), dessen Erfolg Heilzeiten verkürzt oder Mali verringert.
    Dadurch wird der "Heiler" im Team zu einer wichtigen Rolle - ähnlich wie in klassischen
    Rollenspielen, aber hier eingebettet in Sci-Fi (von Kräuterkunde bis Nano-Medizin).

- - **Implantate & Biotech-Heilung:** Im ZEITRISS-Universum verschwimmen Körper und Technik -
  **Cyberware, Biotech und Naniten** können Heilung beeinflussen. Dieses Modul erlaubt High-Tech-
  Lösungen:

  - - **Heil-Implantate:** Einige Agenten tragen eingebaute Module, die im Notfall _automatisch_
    eingreifen. Beispiel: ein subkutanes Notfall-Stimulanz, das bei lebensgefährlichen Verletzungen
    sofort **Adrenalin und Gerinnungsfaktoren** ausschüttet. Im Spiel kann ein solches Implantat
    bewirken, dass der Charakter bei 0 LP **nicht sofort ausfällt**, sondern noch für eine bestimmte
    Zeit weiterkämpfen kann (z.B. für **1 Runde** voller Adrenalin, danach Zusammenbruch). Das
    erhöht die Überlebenschance und passt zum cineastischen Stil. Andere Implantate könnten
    kontinuierliche Heilung bieten (etwa ein Nanobot-Schwarm, der Wundgewebe repariert - pro Runde 1
    LP Heilung) oder Schmerzunterdrückung (Wundabzüge werden um 1 reduziert, wie ein internes
    Schmerzmittel). - **Biotech & Nanotechnologie:** **Heil-Naniten** sind winzige Maschinen oder
    genmodifizierte Zellen, die Verletzungen ausbessern. Im Feld könnten spezielle **Nano-
    Injektoren** gegeben werden, die eine mittelschwere Wunde in wenigen Runden schließen.
    **Regenerationstanks** im HQ nutzen Biotech, um Gewebe nachwachsen zu lassen - ein Agent könnte
    z.B. innerhalb eines Missionsintervalls einen verlorenen Finger regenerieren. All dies
    unterliegt der SL-Entscheidung und sollte **sparsam** eingesetzt werden (die Zukunftstechnologie
    ist zwar weit, aber Wunderheilungen haben oft einen Preis oder sind rar). - **Stim-Packs und
    Drogen:** Neben langfristigen Lösungen gibt es **temporäre Heilmittel**: Injektionen, Pülverchen
    oder elektronische Stims, die **sofort Erschöpfung entfernen oder Schmerz dämpfen**. Ein **Medi-
    Stim** könnte z.B. für eine Szene alle Mali durch Verletzung ignorieren lassen, allerdings auf
    Kosten späterer doppelter Erschöpfung. Solche Resourcen kann man als **einmalige Ausrüstung**
    ins Spiel bringen - vielleicht als Missions-Bonus ("Ihr habt 2 Medi-Stims, setzt sie weise
    ein."). Sie unterstreichen den Sci-Fi-Aspekt der Heilung.

> **Tipp:** Besprecht in Eurer Gruppe, welcher Heilungsansatz bevorzugt wird. Ihr könnt auch >
mischen: z.B. grundsätzlich filmisch spielen, aber in einem Horror-Szenario temporär den >
klassischen härteren Stil nutzen, um die Gefahr zu erhöhen. Wichtig ist, dass alle wissen, worauf >
sie sich einlassen, damit das Drama um Verletzungen für alle **spaßig und spannend** bleibt.

## Initiative-Systeme: klassisch, cineastisch oder szenisch

Wer **handelt zuerst** in brenzligen Situationen? ZEITRISS erlaubt verschiedene Initiative-Regeln,
je nachdem ob Ihr es taktisch, schnell oder erzählerisch mögt. Drei Varianten stehen zur Auswahl:

- - **Klassische Initiative:** Diese orientiert sich an traditionellen RPG-Regeln. **Jeder
  Kampfteilnehmer würfelt seine Initiative** (modifiziert durch Reflexe/Attribute), und es wird eine
  **feste Reihenfolge** festgelegt - meist der höchste Wurf zuerst, dann absteigend. Runden
  verlaufen geordnet, jeder Charakter hat seine Aktion(en) pro Durchgang. Vorteil: klare Struktur,
  taktische Planbarkeit. Nachteil: kann sich etwas starr oder unfilmisch anfühlen, wenn immer
  dieselbe Reihenfolge abläuft. _Varianten:_ Man kann pro **Kampfrunde neu würfeln** (erhöht Chaos,
  aber auch Dynamik) oder einmal zu Beginn eines Kampfes (etwas planbarer). Diese Methode passt zu
  Gruppen, die ein **vertrautes, strukturiertes System** wünschen und gerne taktisch denken. -
  **Cineastische Initiative:** Hier steht das **Filmgefühl** im Vordergrund. Anstatt starr nach
  Zahlen zu handeln, bekommt z.B. **das ganze Spieler-Team zuerst eine gemeinsame Phase**, dann die
  Gegner. So wirken die Helden proaktiver - ähnlich wie in Actionfilmen, wo zuerst die Protagonisten
  agieren. Alternativ kann man einen **"Popcorn"-Ansatz** nutzen: Ein dramatisch passender Charakter
  beginnt (z.B. der Scharfschütze, der einen Überraschungsschuss abgibt), danach **bestimmt dieser,
  wer als Nächstes handelt** - vielleicht ein Gegner, wenn es spannend ist, oder direkt ein
  Mitstreiter, um Momentum aufzubauen. Jede Figur kommt genau einmal dran, bis alle in der Runde
  agiert haben; dann beginnt eine neue Runde, wieder mit dramatisch passender Reihenfolge. Diese
  Variante erzeugt einen **flüssigen, überraschenden Ablauf** wie in einem Film: Die Initiative
  wechselt je nach Situation. _Hinweis:_ Die SL behält dennoch im Blick, dass niemand übergangen
  wird - jede Partei soll pro Runde alle ihre Aktionen erhalten. Für zusätzliche Dynamik könnten
  Spieler **"Initiative-Booster"** einsetzen (z.B. ein Talent, um sich doch noch vorzudrängeln, wenn
  es brennt: "Ich nutze meine schnellen Reflexe, um jetzt sofort zu handeln!"). Cineastische
  Initiative belohnt spontane Ideen und fördert ein **gemeinsames Erzählen von Actionsequenzen**. -
  **Szenendramaturgische Initiative:** In dieser **freien Variante** gibt es **keine festen Regeln**
  für Reihenfolgen - die Handlung richtet sich ganz nach der **Dramaturgie der Szene**. Die
  Spielleitung entscheidet (gerne in Absprache mit den Spielern) aus dem Kontext heraus, **wer
  gerade am logischsten oder spannendsten handelt**. Beispiel: In einer Verfolgungsjagd könnte
  zuerst der Flüchtende dran sein (um die Fluchtbewegung zu beschreiben), dann der Verfolger (um die
  Reaktion zu schildern). Oder in einem Duell lässt man den Spielercharakter immer gerade _knapp_
  vor dem Antagonisten agieren, um die Spannung zu halten, es sei denn der Schurke überrascht
  unerwartet. Diese Methode erfordert viel **Vertrauen** zwischen SL und Spielern, da sie sehr
  **flexibel** ist. Wenn alle an einem cineastischen Flow interessiert sind, kann das großartig
  funktionieren - man verzichtet komplett auf Initiativwürfe und orientiert sich an Story-Logik.
  _Wichtig:_ Jeder Spieler sollte das Gefühl haben, **fair berücksichtigt** zu werden. Die SL kann
  zur Sicherheit eine mentale Reihenfolge mitführen oder in Zweifelsfällen doch würfeln, aber
  grundsätzlich gilt: **Was der Szene dient, geschieht zuerst.** Diese Option passt zu Gruppen, die
  **erzählerisches Spielen** bevorzugen und Regelballast minimieren wollen.

> **Hinweis:** Unabhängig vom System können **Unterbrechungen/Reaktionen** eingebaut werden (siehe
> weiter unten). Auch im klassischen System dürfen z.B. bestimmte Aktionen wie "Deckung hechten"
> als Abwehrreaktion eingeschoben werden. Im cineastischen System empfiehlt es sich, zumindest
> einen **protagonistischen Bonus** zu gewähren - Helden bekommen einen kleinen Vorteil in der
> Reihenfolge, damit es sich heldenhaft anfühlt. Das **HUD-Overlay** kann helfen, die Initiative
> darzustellen: Im klassischen Modus zeigt es die **Reihenfolge-Liste** im UI; im cineastischen
> Modus blendet es nur dezent ein, **wer gerade die Oberhand hat** (z.B. "Initiative: Team" oder
> ein Icon für den aktuellen Akteur).

## Stress, Paradoxon und mentale Belastungen

Neben physischen Bedrohungen können **Stress und Zeitparadoxa** an den Charakteren nagen. Diese
optionalen Module erlauben es, **mentale und temporale Belastungen** abzubilden, die über bloße
Lebenspunkte hinausgehen:

- **Stress-Reset:** Stress betrifft **alle Klassen** und steigt bei Druck oder Fehlschlägen. Im
  HQ oder der Medbay fällt der Zähler auf **0**; eine kurze Ruhephase senkt ihn um **1**.
- **PP = TEMP:** Der PP-Pool entspricht der **Temporalen Affinität**. Ruhephasen und Talente wie
  _Meditation_ oder _Verbesserte Meditation_ regenerieren **1-2 PP**; Gear oder Consumables können
  situativ **+1-2 PP** gewähren.
- **Stresspunkte & Druck:** In turbulenten Missionen sammeln sich mitunter **mentaler Druck und
  Anspannung** an - durch Gefahr, Zeitdruck oder Konflikte. Die SL kann ein
  **Stresspunktekonto** einführen, das pro Charakter (oder fürs Team) mitläuft.
  _Mechanik:_ Jedes belastende Ereignis (knapper Überlebenskampf, Grauen, Fehlentscheidung) gibt
  **einen oder mehrere Stresspunkte**. Klettert das Konto über Schwellen, treten **Effekte** ein:
    bei 5 Punkten etwa der Zustand **"Angespannt"** (-1 auf soziale oder präzise Proben). Bei 10
    Punkten droht ein **Kurzzeit-Zusammenbruch** - Panik, Flucht oder Starre. Stress sinkt in
    HQ-Phasen durch **Entspannung** (ruhige HQ-Phase setzt das Konto auf **0**) oder durch
  **rollenspielerische Maßnahmen**: Gespräch mit einem NSC, Meditationstraining oder ein Abend in
  der Bar. Das Modul verleiht Psyche Gewicht: Spieler achten auf LP **und** auf Pausen zum
  Durchatmen.
  Stress sollte **nicht überstrapaziert** werden - es ist ein Drama-Element, kein dauerhafter
  Malus-Hagel. Die SL kann Stresspunkte verdeckt führen und nur Effekte beschreiben
  ("Eure Hände zittern...") oder offen kommunizieren ("Stress 5/10 - deutliche Anspannung."). Das
  HUD besitzt den Toggle `/stress open|hidden`.
- **Stress-Momente:** Unter akutem Zeitdruck blendet das HUD einen Countdown ein. Scheitert eine
  Probe, kann die SL einen _Fail-Forward_ zulassen und dafür Paradoxon oder Ressourcen in die
  Waagschale werfen.
- **Stress-Regeneration:** Eine Kampfrunde ohne Aktionen senkt Stress um **1 Punkt**, sofern eine
  Willenskraftprobe (CHA) gegen einen Mindestwurf in Höhe des aktuellen Stresslevels gelingt. Eine
  kurze Meditation über zwei Runden reduziert **3 Punkte**. Stress bleibt nach dem Kampf bestehen
  und kann nur in Ruhe oder im HQ abgebaut werden.
- **Stress als Ressource:** 5 Punkte erlauben einen Reroll.

> **Stress vs. Psi-Heat — Abgrenzung:**
>
> | | Stress | Psi-Heat |
> |---|--------|----------|
> | **Was** | Mentale Belastung | Psi-Überanstrengung |
> | **Skala** | 0–10 | 0–6 |
> | **Steigt durch** | Kampf, Trauma, Zeitdruck | Aktive Psi-Nutzung |
> | **Malus ab** | Stress 5 | Psi-Heat 5 (SG +4) |
> | **Maximum** | 10 → Panik | 6 → Psi-Reboot |
> | **Reset** | HQ-Phase → 0; im Feld: CHA-Probe oder 1 Runde Pause (−1) | Nach jedem Konflikt → 0; im Feld: −1 pro Kampfrunde (Probe) |

### Paradoxon-Index - Das Belohnungssystem

> **Kernregel:** Der Paradoxon-Index ist **kein Strafmechanismus**. Er belohnt
> stilvolles Spielen mit Zugang zu Bonus-Content (Rift-Ops, Paramonster, Artefakte).

**Die einfache Wahrheit:**
- Spielt gut → Index steigt → bei 5 gibt's Bonus-Missionen.
- Spielt chaotisch → Index stagniert → keine Bonus-Missionen.
- Spielt katastrophal (selten) → der Index steigt **nicht**, Konsequenzen laufen
  über Stress, Heat, Ressourcen und Storydruck.

Das ist alles. Keine mystische Zeitinstabilität, keine existenzielle Bedrohung.
Einfach ein Fortschrittsbalken für cooles Gameplay.
- **Paradoxon-Resonanz & temporale Stabilität:** Der Index misst temporale Spuren und steigt
  situativ während einer Mission. Niedrige **Temporale Affinität** füllt ihn langsam, hohe TEMP
  beschleunigt. Scheitern oder massive Paradoxa halten den Wert; Konsequenzen laufen über
  Stress/Heat/Ressourcen statt über automatische Px-Abzüge. Bei **Px 5** enthüllt
  `ClusterCreate()` bis zu zwei Rifts und setzt den Zähler auf 0.
  Offene Rifts steigern Schwelle und Loot-Faktor erst nach der Episode. Das **HUD** zeigt die
  Resonanz über eine fünfstufige Skala.
  Seit Version 4.1.4 blendet ein Balken-Meter (1-5 Segmente) den Fortschritt zum nächsten Riss ein.
  GPT kann beschreiben: _"Euer HUD meldet: Paradoxon-Index 3 - Resonanzpegel steigt, erste
  Risskoordinaten rücken näher."_ Der Index baut **Spannung** auf: Das Team entscheidet, ob es
  kontrollierter vorgeht, damit Px 5 als **Belohnung** zum passenden Zeitpunkt eintritt.
    _Auswirkungen:_ Px 0–4 liefert **keine mechanischen Boni** — der Fortschritt
    ist über HUD-Farbe und Score-Screen sichtbar. Der Payoff kommt bei Px 5:
    `ClusterCreate()` enthüllt 1–2 Rift-Seeds.
  Anschließend springt der Index auf 0.
  **Scope:** In `solo` und `npc-team` gehört der Wert zum jeweiligen Run;
  im Modus `gruppe` verwaltet ihr **einen** gemeinsamen Kampagnen-Index
  (`campaign.px`, Host-Save führend).
  Zeitkreaturen können Teil dieser Risse sein - siehe
  [Kreaturen-Generator](../gameplay/kreative-generatoren-begegnungen.md#kreaturen-generator) für
  Stat- und Schadenswerte.
  Wer einen puristischen Thriller bevorzugt, kann
  [im **Covert-Ops-Modus**](../core/sl-referenz.md#spielmodi) spielen, bei dem Rifts nur als dezentes
  Sensorrauschen auftreten. Optional zeigt das HUD ab Px 4 einen sanften Resonanzpuls und blendet
  die Zahl offener Seeds ein: `Seeds 3 · 🌀 Paradoxon 4/5`. Ein Foreshadow-Pulse warnt dezent vor
  nahen Rissen. Die Paradoxon-Mechanik ist standardmäßig aktiv, lässt sich aber jederzeit mit
  `modus paradoxon off` abschalten - mit `modus paradoxon on` wieder aktivieren.

Modul Paradoxon-Resonanz gibt der Gruppe Feedback, **wie viel temporale Resonanz ihr Einsatz
erzeugt**. Clevere Chrononauten haben vielleicht Geräte oder Talente, um Paradoxa zu **erkennen oder
zu reduzieren** (z.B. einen tragbaren Paradoxon-Detektor, der früh Alarm schlägt, oder einen
Temporallogiker im Team, der durch kluge Entscheidungen Stabilität zurückgewinnt). Behutsames,
stilvolles Vorgehen steigert den Index zusätzlich, während grobe Aktionen keinerlei Auswirkungen
  haben. Setzt dieses Element mit Bedacht ein - es soll **Handlungsanreize** bieten ("Wir pushen Px,
  um Rift-Ops freizuschalten."), aber nicht jedes Abenteuer dominieren. Wenn es passt, kann eine ganze Mission
darauf ausgelegt sein, **eine temporale Anomalie zu beheben** (z.B. einen Fehler in der
Vergangenheit zu korrigieren).

_Resonanzpuffer:_ Der Index steigt nur noch, wenn bereits **zwei Resonanz-Marken** in der Szene
liegen - die erste setzt lediglich eine Warnung. Erreicht der Index Px 5, aktiviert
`ClusterCreate()` 1-2 Seeds und setzt den Wert zurück.

### Paradoxon-Subsystem {#paradox-subsystem}

Das vereinfachte Paradoxon-Subsystem orientiert sich an der Kampagnenstruktur und zeigt den
reinen Fortschrittsfluss ohne Heil- oder Gruppenboni.

| Stufe | In-Mission-Effekt                   | HQ-Effekt                                        |
| ----- | ----------------------------------- | ------------------------------------------------ |
| 0-4   | Stabil - keine mechanischen Effekte | Fortschritt über HUD-Farbe sichtbar              |
| **5** | Resonanzpeak erreicht               | **ClusterCreate()** enthüllt 1-2 Rifts; Index 0 |

Nach Px 5 setzt `ClusterCreate()` den Paradoxon-Index auf 0 und legt 1-2 neue Rift-Seeds auf der
Raumzeitkarte ab. Diese sind erst nach Episodenende vom HQ aus erreichbar.

### Raumzeitkarte {#raumzeitkarte}

Die **Raumzeitkarte** ist ein großflächiges Holodisplay im HQ. Sie zeigt alle bekannten Epochen als
interaktive Knotenpunkte. Neue Seeds erscheinen dort automatisch, sobald `ClusterCreate()` aktiv
wird. Aus dem HQ können die Chrononauten über ihr **ITI-Terminal** direkt ein Sprungziel auf der
Karte anwählen. Im Einsatz blendet die AR-Kontaktlinse verkleinerte Auszüge der Karte ein, um Risse
oder Missionsziele zu lokalisieren.

_Optional kann [eine Covert-Ops-Variante](../core/sl-referenz.md#spielmodi) gespielt werden,_ bei der keine
Risse oder Zeitkreaturen erscheinen.

**Mini-Beispiele**

Das Retina-HUD der Chrononauten bleibt über alle Epochen hinweg gleich und läuft
auch ohne Funk autonom (Kinetik + Körperwärme). In funklosen oder gejamten
Zonen fehlt nur der Kodex-Link; HUD/Logs funktionieren unverändert weiter.

- Einsatz läuft sauber: HUD zeigt **Px 2/5** (`Paradoxon 2/5 · Resonanz ↑`).
- Nächste Stabilisierung: HUD springt auf **Px 3/5**.
- Backlash nach Patzer: HUD meldet **Px unverändert**; Konsequenzen erscheinen über Stress/Heat/Storydruck.
- Team stabilisiert erneut: HUD zeigt **Px 4/5**.
- Resonanzpeak: **Px 5/5**, `ClusterCreate()` legt 1-2 neue Rift-Seeds an.

> **Reminder:** Paradoxon-Index nach jeder Zeitlinien-Änderung aktualisieren.

## Ressourcenmodelle: Ausdauer & PP-Pool (optional)

Standardmäßig verwaltet ZEITRISS keine kleinteiligen Ressourcen wie Mana oder Ausdauer - der Fokus
liegt auf Handlung. Wer aber gern **Ressourcenmanagement** betreibt oder spezielle Kräfte einführen
will, kann folgende **optionale Ressourcensysteme** modular hinzufügen. Diese Werte können im
**HUD** angezeigt werden, um den Überblick zu behalten.

- - **Ausdauer (Stamina):** Dieses Modell simuliert **körperliche Erschöpfbarkeit** im Detail. Jede
  anstrengende Aktion (Sprinten, schwere Angriffe, Tragen von Lasten) kostet Ausdauerpunkte. Ein
  typischer Wert könnte z.B. 100 Punkte pro Charakter sein. Laufen, Kämpfen, Klettern ziehen Punkte
  ab, **Rasten oder Stimulanzien** stellen Punkte wieder her. Sinkt die Ausdauer unter bestimmte
  Schwellen (50%, 25%), greift man auf die oben beschriebene **Erschöpfungs-Mechanik** zurück: der
  Charakter erhält Mali, als wäre er erschöpft. Bei 0 Ausdauer kann der Charakter nicht mehr
  vernünftig agieren (völlige Erschöpfung, Zusammenbruch). _Anwendung:_ Ausdauerpunkte machen
  Aktionen **bedeutsamer** - man kann nicht endlos rennen oder kämpfen, ohne zu verschnaufen. Im HUD
  ließe sich das als **Ausdauerbalken** darstellen. Dieses Modul passt, wenn eure Gruppe etwas
  **Survival-Feeling oder taktische Tiefe** möchte. In einem filmischeren Spiel hingegen ignoriert
  man Ausdauer bewusst, um Helden nicht künstlich zu bremsen. - **PP-Pool (Psi-Energie):** Power-
  Punkte (PP) sind fest an _Temporale Affinität (TEMP)_ gebunden; euer Pool entspricht also dem
  TEMP-Wert. Starke/mittlere/geringe Kräfte kosten 3/2/1 PP und lösen 3/2/1 Runden Cooldown aus.
  Nach jeder Kampfrunde könnt ihr pro **3 TEMP** 1 PP regenerieren, falls eine Willenskraftprobe
  (CHA) gegen doppelten Psi-Heat gelingt; nach jedem Kampf wird der Pool voll aufgefüllt. Große
  Effekte erhöhen die Psi-Heat. Im HUD zeigt ein Ω-Symbol die aktuelle PP-Zahl.

- - **Modulare Ressourcen allgemein:** Natürlich könnt ihr auch andere Ressourcen tracken, z.B.
  **Munition**, **Batterieladung von Geräten**, **Sauerstoffvorrat** in bestimmten Szenarien etc.
  Das HUD prädestiniert sich dafür, solche Infos übersichtlich anzuzeigen (etwa "Munition: 12/30"
  bei einer Feuerwaffe). Der Grundansatz von ZEITRISS ist aber: **Nur das Nötigste verwalten.**
  Führt also nur Ressourcensysteme ein, die euren Spielspaß **erhöhen**. Wenn ihr merkt, dass Punkte
  zählen euch aus der Immersion reißt, lasst es lieber weg und vertraut auf die narrative Logik (die
  KI-Spielleitung kann dann z.B. entscheiden, wann die Munition knapp wird, anstatt jede Kugel zu
  zählen).

## Besonderheiten im Zeitstrom: Unterbrechungen, Reaktionen & freie Aktionen

Zeitreisen und Hochrisiko-Missionen erfordern manchmal **schnelle Reflexe und spontane Aktionen**.
Unabhängig vom gewählten Initiative-System könnt ihr folgende Sonderaktionen erlauben, um den Kampf-
und Actionszenen mehr **Lebendigkeit** zu verleihen:

- - **Unterbrechungen:** Eine Unterbrechung ist eine **außerplanmäßige Zwischenaktion**, mit der ein
  Charakter _im selben Moment_ reagiert, in dem etwas passiert, und so den Ablauf "unterbricht".
  Beispiel: Ein Agent sieht, wie ein Feind den Finger krümmt, um zu schießen - der Agent ruft:
  _"Unterbrechung! Ich werfe sofort eine Blendgranate!"_ Wenn die SL die Unterbrechung zulässt (ggf.
  mit einer Bedingung wie "ihr verbraucht dafür eure nächste reguläre Aktion" oder einem
  erfolgreichen Reflex-Wurf), wird die granate **noch bevor** der Schuss fällt ausgelöst.
  Unterbrechungen sind als **dramatisches Mittel** zu verstehen: In Filmen sieht man oft, wie jemand
  im _letzten Augenblick_ noch etwas tut. Im Spiel sollten sie **restriktiv** gehandhabt werden -
  etwa **maximal eine Unterbrechung pro Runde pro Charakter**, nur wenn es **dramatisch passt**.
  Möglich ist auch, Unterbrechungen an **Ressourcen** zu knüpfen (z.B. verbraucht 1 PP oder einen
  besonderen "Reflexmarker"). Das ZEITRISS-Setting bietet sogar techische Rechtfertigungen:
  Vielleicht nutzen einige Agenten **Temporalsinn-Implantate**, die für Sekundenbruchteile in die
  Zukunft spüren lassen, um solche Unterbrechungen durchführen zu können. Wichtig ist, dass
  Unterbrechungen **klar kommuniziert** werden ("Ich will unterbrechen, sobald der Wächter den
  Alarmknopf drückt…") und dass die SL fair entscheidet, ob es gelingt. Richtig eingesetzt, können
  Unterbrechungen extrem **spannende Wendungen** erzeugen. - **Reaktionen:** Reaktionen sind
  **Antworten auf Aktionen anderer**, die sofort erfolgen, aber nicht unbedingt den gegnerischen
  Ablauf verhindern - eher _parallel_ dazu oder im direkten Anschluss. Klassisches Beispiel: der
  **Gelegenheitsangriff** - ein Gegner läuft an euch vorbei, und _als Reaktion_ dürft ihr einen
  schnellen Schlag ausführen. Oder der Feind schießt auf euch, und _als Reaktion_ werft ihr euch zu
  Boden (**Ausweichreaktion**), um schwerer getroffen zu werden. Anders als Unterbrechungen, die das
  Geschehen _unterbrechen_, laufen Reaktionen _mit_ dem auslösenden Ereignis. Viele Systeme erlauben
  z.B. **eine Reaktion pro Runde** außerhalb der eigenen Turnorder. In ZEITRISS könnt ihr das
  ähnlich handhaben: Jeder Charakter hat z.B. **1 Reaktion pro Zyklus**, die er einsetzen kann, wenn
  ein definierter **Trigger** eintritt (wie "ich werde angegriffen" oder "mein Verbündeter wird
  getroffen, ich will ihn auffangen"). Reaktionen sollten **einfach** gehalten werden (kein halber
  Roman an Aktionen - es geht um kurze Reflexhandlungen). Beispiele im Spiel: Parieren oder Blocken
  eines Nahkampfangriffs, Gegenfeuer geben wenn man beschossen wird, einen fallenden
  Artefaktbehälter noch auffangen, bevor er am Boden zerschellt, etc. Diese Mechanik gibt Spielern
  das Gefühl, auch _zwischen_ ihren Zügen **handlungsfähig** zu sein, was die Cinematic-Dichte
  erhöht. Das HUD könnte Reaktionsmöglichkeiten symbolisch andeuten (z.B. ein kleines Icon, wenn
  eine Reaktion jetzt verfügbar ist - etwa ein Schild-Icon für "Abwehr bereit"). - **Freie
  Aktionen:** Unter freie Aktionen fallen all jene Handlungen, die **keine nennenswerte Zeit im
  Zeitstrom kosten**. Im Prinzip können sie _jederzeit_ durchgeführt werden, sofern logisch - oft
  auch parallel zu Hauptaktionen. Typische freie Aktionen: **Etwas rufen oder schreien**, eine kurze
  Funknachricht absetzen, eine Waffe fallen lassen, einen Knopf drücken, ein Holster öffnen, das HUD
  kurz konsultieren, etc. Im Kampf kosten solche Kleinigkeiten _keine_ Aktion, solange sie wirklich
  kurz sind. Aber Achtung: Mehrere freie Aktionen hintereinander sind irgendwann nicht mehr "frei" -
  in der Summe kosten sie natürlich doch Aufmerksamkeit. Die Faustregel: **1-2 freie Aktionen pro
  Zug** (z.B. etwas zurufen _und_ sich umschauen) sind okay, alles darüber hinaus sollte die SL als
  normale Aktion werten. Der Begriff "im Zeitstrom" bedeutet hier, dass diese Handlungen **so fix
  ablaufen**, dass sie den Fluss der Zeit nicht spürbar verzögern - quasi wie ein Schnitt im Film,
  in dem der Held einen kurzen Satz sagt oder den Sicherheitshebel umlegt, während die Haupthandlung
  weitergeht. Freie Aktionen eignen sich auch für **stilistische Beschreibungen**: Ein Agent könnte
  während seines Angriffs noch einen one-liner raushauen (frei) oder mitten im Sprint dem Team etwas
  zurufen. Dadurch wirken die Szenen lebendig. In begrenzten Situationen kann die SL freie Aktionen
  auch _einschränken_ ("Unter Wasser könnt ihr leider nichts rufen") - meist regelt aber der gesunde
  Menschenverstand, was geht. Spieler sollten also nicht versuchen, eine "freie Aktion" zu dehnen,
  um doch noch etwas Großes umsonst zu erledigen. Solange alle ehrlich abschätzen, was in einer
  Sekunde machbar ist, bleiben freie Aktionen ein intuitives Werkzeug.

> **Zusammenspiel:** Unterbrechungen, Reaktionen und freie Aktionen sorgen gemeinsam dafür, dass >
sich Action-Sequenzen **weniger rundenbasiert, sondern organischer** anfühlen. Die KI-Spielleitung >
sollte diese Möglichkeiten präsent halten. Im Text kann GPT z.B. anregen: \*"Der Wachmann hebt die >
Pistole - möchtet ihr **_reagieren_** (z.B. in Deckung springen)?"_ oder _"Die Zeit scheint zu >
stocken - falls ihr jetzt **_unterbrecht_** und den Zeit-Stasis-Gadget aktiviert, könntet ihr dem >
Ereignis zuvorkommen…"\*. So werden Spieler ermutigt, kreativ mit dem Zeitstrom zu spielen.

**Fazit:** Mit den in Modul 5A vorgestellten erweiterten Systemen könnt ihr euer ZEITRISS-Spiel
feinjustieren. Ob ihr nun Verletzungen detailliert ausspielt, cineastische Heilungen nutzt,
Initiative dramaturgisch gestaltet oder mit Zeitstrom-Optionen experimentiert - all diese Module
stehen euch **modular zur Verfügung**. Wählt, was zu eurer Runde passt. Bleibt dem **Geist von
ZEITRISS** treu: Cinematic Gameplay, spannende Entscheidungen und eine dichte Atmosphäre. Die Regeln
sind da, um _euch_ zu unterstützen, nicht umgekehrt. In diesem Sinne: Viel Spaß beim Experimentieren
mit Zuständen, Zeit und Technologie - möge euer nächster Einsatz ebenso **packend** wie erfolgreich
sein!

© 2025 pchospital - ZEITRISS® - private use only. See LICENSE.
