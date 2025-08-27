---
title: "ZEITRISS 4.2.2 – Modul 4B: Cyberware & Bioware"
version: 4.2.2
tags: [characters, cyber]
---

# ZEITRISS 4.2.2 – Modul 4B: Cyberware & Bioware

## Cyberware-Implantate

Die Zukunft hinterlässt Spuren am Körper: **Cyberware** bezeichnet technische Implantate, die direkt
im Körper des Chrononauten integriert werden, um seine Fähigkeiten zu verbessern. Dies können
kybernetische Gliedmaßen, Sinnesverstärker, neuronale Chips u.v.m. sein. Cyberware unterliegt
strengen Regeln im ITI: Operationen finden _nur im HQ_ statt, in hochsterilen High-Tech-Kliniken –
**niemals im Feld**. Jedes Implantat hat einen **Preis in CU** und belegt einen Teil der
**Systemlast-Kapazität** (Attribut **SYS**) des Charakters. Faustregel: _1 SYS-Punkt ≈ 1 Standard-
Implantat_. Hat ein Chrononaut z.B. SYS 3, kann er drei größere Implantate tragen (oder mehrere
kleinere entsprechend verteilen). Zu viele Modifikationen überfordern Körper und Geist –
Überschreitung der SYS-Kapazität lässt Implantate Fehlfunktionen zeigen oder zwingt den Körper in
die Knie. Items und Implantate ab **Tier 3** tragen den Tag _heavy_ und belasten das System um +1 SYS,
solange sie aktiv sind. Das ITI-Medical-Team wird Überschreitungen gar nicht erst zulassen. Dennoch können
Charaktere mit mehreren Implantaten entscheiden, einige Systeme vorübergehend **herunterzuregeln**,
um Kapazität für andere frei zu machen (z.B. die Tarnoptik drosseln, um einen Psi-Boost zu
nutzen – siehe Psi später).

Implantate können sowohl bestehende Attribute verbessern als auch völlig neue Fähigkeiten
ermöglichen. Die Bandbreite reicht von **kybernetischen Armen** (mehr Kraft) über **optische
Implantate** (Verbesserte Wahrnehmung durch Zoom, Infrarot oder Nachtsicht) bis zu **internen
Computersystemen** (für Datenspeicherung oder Kommunikation). Die **Spielmechanik** von Cyberware
ist flexibel: Kleinere Boni (~+1 auf Attribute oder +2 auf spezialisierte Proben) sind üblich,
während mächtigere Effekte entsprechend teurer sind und evtl. höhere SYS-Kosten haben. Installation
und Upgrade von Cyberware bieten tolle Erzählchancen: Beschreibt, wie der Charakter im Med-Tank
schwebt, robotische Arme an ihm arbeiten und anschließend die Anpassung an das „Upgrade“ Zeit
braucht. Möglicherweise ist eine **STR- oder TEMP-Probe** fällig, um zu sehen, wie gut der
Körper das Implantat annimmt – ein guter Erfolg bedeutet schnelle Genesung, ein Patzer könnte
temporäre Malusse (z.B. –1 auf körperliche Proben bis zur Eingewöhnung) oder initiales Versagen des
Implantats bedeuten. Auch narrativ kann man spüren, wie der neue _Cyberarm_ zunächst fremd wirkt
oder das Auge überempfindlich auf Licht reagiert. Mit etwas Rollenspiel wird Cyberware so mehr als
nur ein Wert auf dem Bogen.

## Legalitäts- & Wartungs-Stufen {#legalitäts--wartungs-stufen}

Siehe [Ausrüstung & Cyberware](ausruestung-cyberware.md#legalitäts--wartungs-stufen) für die vollständige Tabelle.
> **Einbau-Reminder:** Wartung überfällig → nach jeder Mission +1 Risiko-Kategorie.

```pseudo
if item.license > char.licenses.max:
    deny_purchase(item.name, item.min_rank)
```

Implantate mit **SYS > 2** verursachen zusätzlich **5 % Wartungskosten pro Mission**.

**Beispiel-Cyberware-Implantate** _(mit `tier:`-Spalte)_:

id: implant_t1

| Implantat | Beschreibung | SYS | Kosten (CU) | Tier |
| --- | --- | --- | --- | --- |
| **Nachtsicht-Implantat** | Künstliches Auge mit Verstärker. _Effekt:_ Nachtsicht, +1 Wahrnehmung. | 1 | 300 | 0 |
| **Kybernetischer Arm** | Servomotorik-Prothese. _Effekt:_ Stärke +1, Schaden ohne Waffe schwer. | 1 | 400 | 1 |
| **Neuronales Interface** | Chip mit HUD. _Effekt:_ Datenzugriff, Funkverbindung; +2 Elektronik. | 1 | 250 | 1 |
| **Subdermale Panzerplatten** | Platten unter Haut. _Effekt:_ –1 Schaden; auffällig bei Verletzung. | 1 | 350 | 2 |
| **Notfall-Stimulat** _(Implantat)_ | Subkutanes Injektionssystem. Bei 0 LP hält es 1 Runde wach. | 1 | 200 | 0 |
| **Servomotoren in Beinen** | Bein-Servomotoren. _Effekt:_ +1 Athletik; mehr Traglast; Sprünge bis 2 m. | 1 | 300 | 2 |

_Hinweis:_ In Absprache kann die SL auch Implantate mit **höheren SYS-Kosten** zulassen, die dann
aber erhebliche Vorteile bieten (z.B. ein vollständiges Skelett-Verstärkungssystem mit SYS 2, das +2
Stärke **und** –1 erlittenen Schaden gewährt). Solche umfangreichen Mods sollten teuer und nur für
erfahrene Charaktere verfügbar sein. Zudem gilt: Mehr **Cyberware** bedeutet tendenziell weniger
Platz für **Bioware** oder **Psionik** – jede Richtung der Verbesserung hat ihren Preis.

## Bioware-Verbesserungen

Nicht alle Upgrades sind aus Stahl und Silizium – manche kommen aus Petrischale und Injektionsnadel.
**Bioware** umfasst genetische Optimierungen, biochemische Enhancer und organische Implantate, die
den Körper auf _natürliche_ Weise verbessern. Von verbesserten Organen bis hin zu Gen-Tweaks, die
Sinne oder Reflexe schärfen, bietet Bioware subtilere Alternativen zur Cyberware. Für Außenstehende
sind Bioware-Mods schwerer zu erkennen (kein mechanischer Glanz im Auge, keine Metallarme), was für
Undercover-Einsätze nützlich ist. Allerdings sind sie dauerhaft „an“ – man kann ein genetisch
verstärktes Muskelgewebe nicht einfach abschalten. Daher belegen Bioware-Verbesserungen ebenfalls
**SYS-Kapazität** (analog zu Cyberware). **Systemlast** repräsentiert ja die Belastung von
Körper/Geist durch Fremdsysteme _und_ Psionik. Bioware zählt dazu: Der Körper muss mit den
veränderten Organen leben, was auf Dauer ebenso an die Substanz geht. In der Regel zählt auch hier
eine größere Bioware-Mod als 1 SYS. Das ITI beschränkt Bioware-Experimente aus ethischen Gründen –
nur getestete Verbesserungen werden den Agenten angeboten, und meist erst nach einigen erfolgreichen
Missionen, wenn das Vertrauen besteht.

Spielmechanisch ähneln Bioware-Effekte oft Attributssteigerungen oder Resistenz-Boni. Manche Bioware
hebt physische Grenzen an, ohne die Nebenwirkungen mancher Cyberware (z.B. _Muskelverstärkung_
erhöht Stärke, ohne dass ein Metallarm nötig ist). Andere bieten Fähigkeiten, die ein normaler
Mensch nicht hätte, wie Infravision durch modifizierte Netzhaut oder ein extrem effizientes
Immunsystem als Schutz vor Krankheiten. Die _Kehrseite_: Bioware kann unvorhergesehene
**Nebeneffekte** haben – etwa überschießende Reaktionen des Immunsystems oder hormonelle
Schwankungen. Dies kann die SL ins Spiel bringen, muss aber nicht bei jeder Mod auftreten.

**Beispiel-Bioware-Modifikationen** _(Tabellenfeld `tier:` vorhanden)_:

id: implant_t2

| Modifikation | Beschreibung | SYS | Kosten (CU) | Tier |
| --- | --- | --- | --- | --- |
| **Immun-Booster-Genmod** | Resistenz gegen Gifte; mögliches Autoimmunrisiko | 1 | 250 | 1 |
| **Reflexverstärkung** | Nervensystem-Tuning. _Effekt:_ +1 Geschick; schnelle Reaktion; Muskelzucken. | 1 | 300 | 2 |
| **Muskelstärkung** | Genmod für mehr Kraft. _Effekt:_ +1 Stärke. Nebenwirkung: großer Appetit. | 1 | 300 | 2 |
| **Nachtsicht-Netzhaut** | Genetisch angepasste Augen. _Effekt:_ Nachtsicht. Augen leuchten rot/grün. | 1 | 200 | 1 |
| **Regenerations-Booster** | Heilrate x2; Nebenwirkung: hoher Stoffwechsel {heavy} | 1 | 400 | 3 |
| **Stoffwechselkontrolle** | Weniger Schlaf, toleriert Klima und Gifte besser; kann hyperaktiv wirken. | 1 | 250 | 1 |

_Balance-Hinweis:_ Cyberware und Bioware sind im Spiel gleichwertige Alternativen. Oft bevorzugen
Kämpfer vielleicht robuste Cyberware, während Infiltratoren lieber unauffällige Bioware nehmen.
Wichtig ist: **Alle Verbesserungen zehren an der SYS-Kapazität** – ein Agent voller Implantate hat
kaum Raum für Psi und umgekehrt. Die SL sollte zudem thematisch passende Nebenwirkungen einbauen,
wenn es dramatisch passt (z.B. ein _Reflex-Booster_-Charakter, der in einer ruhigen Wache-Szene
gegen eine Vase stößt, weil seine Nerven überreagieren).
_Psi-Abgleich:_ Kurzzeitig manifestierte Psi-Waffen (maximal eine Kampfrunde lang)
verursachen **1 SYS** und nutzen keine Exploding-Würfel.
Alles darüber hinaus zählt als dauerhafte Psi-Kraft und belegt SYS-Punkte wie andere Implantate.
Dauerhaft aktive Psi-Kräfte belegen hingegen SYS-Punkte wie andere Implantate.
Grundfähigkeiten sind leicht zu erlernen, doch hohe Meisterstufen verlangen intensives Training
und sorgfältiges SYS-Management.

### Bioware-Synergien (ab Bioware 3+)

_Hinweis:_ „Bioware 3+“ bedeutet, dass der Charakter Bioware im Wert von mindestens **3 SYS** installiert hat –
also drei belegte Slots.

#### Adaptive-Ligament (Bioware-Upgrade)
- **Slot-Typ:** Muskulatur
- **Voraussetzung:** Bioware 3+, Attribut Beweglichkeit ≥ 10
- **Effekt:** +1 Würfel auf Klettern & Sprünge; Fallschaden halbiert.

#### Neuromimetic-Coating
- **Slot-Typ:** Nervenverbund
- **Voraussetzung:** Bioware 3+, PSI-Fähigkeit verknüpft
- **Effekt:** Senkt PP-Kosten für [Mentale Maskierung](psi-talente.md#mentale-maskierung) um 1.

#### Metabo-Recycler
- **Slot-Typ:** Organe
- **Voraussetzung:** Bioware 3+
- **Effekt:** Erlaubt eine zweite Gratis-Erholung (Short Rest) pro Mission.
  Bei Übernutzung schläft der Charakter sofort ein oder kämpft mit extremer Müdigkeit.

#### Osteo-Capacitor
- **Slot-Typ:** Skelett
- **Voraussetzung:** Bioware 3+, Panzerungs-Mod aktiv
- **Effekt:** Beim Blocken wird Exploding-6 zweimal geprüft (stackt nicht).

#### Stealth-Skin
- **Slot-Typ:** Haut
- **Voraussetzung:** Bioware 3+
- **Effekt:** +1 Würfel auf Heimlichkeit-Proben.

<a id="optional-hominin-bio-sheaths"></a>
## Optional: Hominin-Bio-Sheaths

Die ITI-Forschung erlaubt es, ein Bewusstsein in eine **polyclonale Bio-Hülle** zu
implantieren. Diese Körper basieren auf fossiler DNA, ergänzt durch Nanografting.
Spieler können so statt eines modernen Menschen einen urzeitlichen Homininen
körpern. Der Ansatz bleibt reine Sci-Fi ohne Fantasy-Rassen.

### Vorteile & Herausforderungen

| Vorteil | Herausforderung |
| --- | --- |
| Frischer „Wow“-Effekt, ohne Magiewesen einzuführen. | Historische Limits bei Größe, Sprache und Feinmotorik. |
| Passt zur ZEITRISS-Prämisse. | Verkleidung erschwert; auffällige Proportionen. |
| Einfache Regel-Modifikatoren (+STR/–INT usw.). | Implantate benötigen angepasste Systemlast. |

### Mögliche Homininen

| Spezies | Zeitfenster | Key-Traits | Spielrelevanz |
| --- | --- | --- | --- |
| **Homo neanderthalensis** | bis ~40 000 v.Chr. | kräftiger Brustkorb | +2 STR, –1 INT, –1 CHA |
| **Denisova-Mensch** | bis ~50 000 v.Chr. | robuste Knochen, kälteresistent | +1 STR, +1 TEMP, –1 CHA, –1 INT |
| **Homo heidelbergensis** | bis ~200 000 v.Chr. | extreme Ausdauer | +1 STR, +1 SYS, –1 CHA, –1 INT |
| **Homo floresiensis** | bis ~50 000 v.Chr. | klein und wendig | +2 GES, –2 STR, Vorteil in engen Räumen |
| **Homo erectus (spät)** | bis ~110 000 v.Chr. | hohe Hitzeresistenz | +1 GES, +1 SYS, –1 CHA, –1 INT |

### Balancing-Regeln

- **Kosten:** zählt wie Bioware Stufe 2 (+1 SYS).
- **Talent:** Jede Spezies bringt ein exklusives Talent.
- **Limit:** Feinsensorische Cyberware ist teurer oder inkompatibel (+50 % Kosten).
- **Cover-Malus:** +2 SG auf soziale Infiltration bei auffälligen Körpern.

### Beispiel-Archetypen

| Archetyp | Attribut-Boni | Kern-Talent | Einsatzfeld |
| --- | --- | --- | --- |
| **„Neander-Bruiser“** | +2 STR, –1 INT, –1 CHA | Hammerschlag – Nahkampfschaden +1 | Sturm-Ops |
| **„Denisovan Scout“** | +1 STR, +1 TEMP, –1 CHA, –1 INT | Frostborn – ignoriert Kälte bis −20 °C | Arktis-Drops |
| **„Heidel-Endurer“** | +1 STR, +1 SYS, –1 CHA, –1 INT | Marathoner – doppelte Ausdauerlaufzeit | Aufklärung |
| **„Flores Shadow“** | +2 GES, –2 STR | Tunnelgeist – +2 Heimlichkeit in engen Räumen | Grabungsmissionen |
| **„Erectus Nomad“** | +1 GES, +1 SYS, –1 CHA, –1 INT | Heat-Runner – kein Erschöpfungsmalus bei Hitze | Wüsten-Ops |
© 2025 pchospital – ZEITRISS® – private use only. See LICENSE.
