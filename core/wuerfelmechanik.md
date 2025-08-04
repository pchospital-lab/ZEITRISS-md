---
title: "ZEITRISS 4.2.0 – Modul 2: Explodierende Würfel, HUD-Alerts & cineastische Schlachten"
version: 4.2.0
tags: [core, advanced]
---

# ZEITRISS 4.2.0 – Modul 2: Explodierende Würfel, HUD-Alerts & cineastische Schlachten

## Inhalt

- Würfelmechanik: Explodierende 6 & W10-Variante
- HUD-Management: Ereignis-Alerts & Info-Triage
- Attributs-Skalierung: Heldenwürfel & Endgame-Balance
- Speichersystem-Erweiterung: Versionskennzeichnung & Kompatibilität
- Cineastische Schlachten: Erfolgspools, Spotlight-Szenen & heroische Würfe

\*Mit letzter Kraft erhebt sich Chrononaut Leon aus dem Trümmerfeld, während um ihn eine epische
Schlacht tobt. Sein HUD überschlägt sich mit Warnmeldungen – **_Vitalstatus kritisch: 10%_**,
**_Paradoxon-Index +1_** –, doch er blendet die Alarme aus. Jetzt zählt nur noch dieser eine
verzweifelte Versuch. Leon schultert die Energie-Lanze eines gefallenen Mech-Piloten, legt an und
drückt ab. Ein gleißender Strahl zerfetzt die angreifende Zeitanomalie – ein schier unmöglicher
Treffer, zustande gekommen durch eine Prise Heldenmut und Würfelglück. Der Codex protokolliert
ungläubig: „Ziel eliminiert – Erfolgschance \< 5%“. Es sind genau solche filmreifen Momente, die
ZEITRISS zum Leben erwecken.\*

Willkommen zu einem weiteren Modul für **ZEITRISS 4.2.0**, das Feinschliff und neue cineastische
Optionen ins Spiel bringt. Dieses Regelmodul erweitert das System um spannende Verbesserungen in der
Würfelmechanik, ein dynamisches HUD-Warnsystem, feinere Attributs-Skalierung, ein robustes
Speichersystem und alternative Regeln für große **Schlachten** – ohne den erzählerischen Fokus zu
verlieren. Im Folgenden findet ihr neue Regeln und Inspirationen, um kritische Proben noch
nervenaufreibender, das HUD der Agenten informativer (aber nicht überwältigend) und Massengefechte
so filmisch wie im Kino zu gestalten. Kurzum: Mehr **Drama** und **Tiefe**, aber weiterhin
übersichtlich und spielbar am Spieltisch.

**Dieses Modul enthält im Überblick:**

- **Neue Würfelmechaniken:** Einführung der **„Exploding 6“**-Regel für W6-Proben, die bei einer
  gewürfelten 6 einen zusätzlichen Wurf gewährt – für unerwartete Spitzenresultate. Außerdem eine
  **optionale** Regelvariante, sämtliche Proben mit W10 statt W6 durchzuführen, um eine feinere
  Granularität und ein breiteres Erfolgsspektrum zu ermöglichen.
- **HUD-Management & Alerts:** Ein ereignisgesteuertes Hinweis-System für das HUD der Chrononauten, das
  bei definierten kritischen Zuständen (z. B. Lebenspunkte \< 25 % oder wenn der Paradoxon-Index steigt)
  automatisch Meldungen einblendet. Dazu kommen Vorschläge für **Info-Triage**, damit in brenzligen
  Situationen nur wirklich wichtige Daten angezeigt werden und die Agenten nicht von
  Informationsflut überwältigt werden.
  In jeder Kampagne kann der Resonanzhinweis über `modus paradox off`
  deaktiviert werden. Wer ihn aktiviert,
  nutzt das System identisch weiter.
- **Attributs-Skalierung & Heldenwürfel:** Attribute verleihen nun einen additiven Bonus.
  Ab **11** ersetzt ein W10 den W6 (Exploding 10). Erst bei **14** kommt ein Heldenwürfel
  für einen einmaligen Reroll hinzu. So bleibt jeder Punkt spürbar, ohne die Balance zu kippen.
 - **Erweitertes Speichersystem:** Spielstände (JSON-Daten) erhalten ab sofort ein
  **Versionskennzeichen**, um die Kompatibilität mit zukünftigen Regelupdates sicherzustellen. Wir
  zeigen Beispiele, wie **versionskompatible** Speicherstände aussehen und wie das Spiel mit
  unterschiedlichen Versionen umgeht, damit eure Kampagnen-Logs auch nach Updates nahtlos
  weiterverwendet werden können.
- **Cineastische Schlachten:** Eine alternative Regelabwicklung für große Konflikte, die
  **filmisch** statt kleinteilig funktioniert. Durch **Erfolgspools**, spannende **Spotlight- Szenen**
  für jede/n Chrononauten und **heroische Schlüsselwürfe** werden Massenkämpfe übersichtlich
  dargestellt, ohne an Dramatik einzubüßen – ganz im Stil eines mitreißenden Actionfilms, bei dem die
  Heldentaten den Ausschlag geben.

## Würfelmechanik: Explodierende 6 & W10-Variante

Nervenzerfetzende Würfelwürfe gehören zum Kern von ZEITRISS. Um die Spannung jeder Probe noch zu
steigern, führen wir die Regel **„Exploding 6“** ein – im Deutschen oft schlicht _explodierender
Würfel_ genannt. **Immer wenn bei einer W6-Probe eine 6 gewürfelt wird,** wird der W6 **erneut
geworfen** und das neue Ergebnis zur bisherigen Summe **addiert**. Sollte dabei wieder eine 6
fallen, wiederholt sich der Vorgang so lange, bis kein Maximum mehr erscheint. Damit die Werte nicht
übermäßig eskalieren, darf **nur der erste Würfel einer Probe** überhaupt explodieren; weitere 6er
werden normal gezählt. Auf diese Weise sind theoretisch **Ergebnisse über dem normalen Limit**
möglich, was besonders heroische Erfolge oder dramatische Wendungen darstellen kann. Spielerinnen
und Spieler erleben einen zusätzlichen Adrenalinstoß, wenn der Würfel „explodiert“ – denn aus einem
sicheren Misserfolg kann so doch noch ein triumphaler Erfolg werden.

**Kurzes Beispiel:** Zeigt der erste W6 eine **6**, wirfst du sofort einen zweiten.
Fällt dieser **4**, ergibt das **10** Punkte.
Würfelst du stattdessen noch einmal eine **6**, kommst du auf **12**.
Damit endet die Explosion – weitere Würfel sind nicht erlaubt, weil nur der erste W6 explodiert.
_(Beispiel: Nadia muss einen schwierigen Sprung über eine Schlucht meistern. Sie hat nur mäßige Werte,
bräuchte aber mindestens eine 10. Sie würfelt eine 6 – diese „explodiert“, sie darf erneut werfen.
Der zweite Wurf zeigt eine 4. Zusammen ergibt das 6+4=10 – gerade noch geschafft! Die Gruppe jubelt
ob dieses glücklichen Ausgangs.)_

[[RULE]] Exploding-6: Bei einer 6 wird erneut geworfen und addiert. [[/RULE]]
[[RULE]] Tooltip: "W10 ab 11, Heldenwürfel ab 14" [[/RULE]]
**Optionale W10-Regel:** Für Gruppen, die eine feinere Abstufung bei Würfelergebnissen bevorzugen,
bietet ZEITRISS alternativ den **Zehnseitigen Würfel (W10)** als Basis für Proben. Mit einem W10
erstreckt sich der mögliche Wertebereich von 1–10 (anstatt 1–6), wodurch **Granularität** und
Varianz zunehmen. Kleine Unterschiede in Attributen oder Fertigkeiten wirken sich damit etwas
weniger stark absolut aus, was Proben **ausgewogener** machen kann. Die SL sollte die
Schwierigkeitsgrade der Proben bei Verwendung von W10 im Blick behalten.
In der Regel kommen Aufgaben ohne Modifikator aus; die Zielzahlen bleiben gleich. Das
additive Modell lautet:

`Endwert = Würfel + ⌊Attribut / 2⌋ + Talent + Gear`.
Talentboni sind nach dem Attributsbonus auf **+5** begrenzt.

W6 explodiert bei 6, W10 bei 10.
Ein Heldenwürfel (ab 14) gewährt einen einmaligen Reroll.
Die **Exploding**-Regel lässt sich auf beide Würfel übertragen (_Exploding 6/10_).
### Transparenz-Log (optional)
Bei Remote-Runden können Würfe als JSON-Log geteilt werden.
```json
{"roll":"2d6","result":[5,6],"timestamp":"2024-01-01T12:00:00Z"}
```

Spannungsbreite; ob man zusätzlich explodierende Würfel bei 10 einsetzt, kann die Gruppe nach
gewünschter Dramaturgie entscheiden. In jedem Fall gilt: Beide Mechanismen – **Explodierende 6** und
der **W10-Ersatz** – sind **optional** und sollten nur eingesetzt werden, wenn sie zum Stil der
Runde passen. Sie bieten frischen Wind für erfahrene Runden, ohne das Grundsystem fundamental zu
verändern.

**Schwellen-Kalibrierung:** Standardproben nutzen einen W6. Ein SG von **5** gilt als
leichte Herausforderung, **8–9** als mittel, **12** als schwierig und **15+** als
extrem. Ein **Heldenwürfel** ermöglicht einmal pro Szene einen kostenlosen Reroll.

| Stufe  | Zielzahl |
| ------ | -------- |
| Leicht | 5        |
| Mittel | 8–9      |
| Schwer | 12       |
| Extrem | 15+      |

**Hinweis:** Durch explodierende Würfel können gerade unwahrscheinliche Aktionen spektakulär
gelingen. Die Spielleitung sollte dies erzählerisch hervorheben – z. B. durch cineastische
Beschreibungen, wie ein Charakter mit unglaublichem Glück das Blatt wendet. Gleichzeitig dürfen
solche Glückstreffer nicht zur Alltagskost werden: Explodierende Würfel sollten besondere Highlights
bleiben, die denkwürdige Szenen schaffen. Wenn Würfelpech umgekehrt dramatische Fehlschläge
produziert, kann dies ebenso interessant inszeniert werden (Stichwort **kritischer Patzer**), sofern
es zur Geschichte passt.

### Fail-Forward & Countdown {#fail-forward}

Bei anspruchsvollen Aufgaben kann die Spielleitung statt eines harten
Misserfolgs einen sanften _Fail-Forward_ anbieten. Die Szene geht weiter, doch
der Teilerfolg kostet Ressourcen oder erhöht den Paradoxon-Index. So bleibt der
Handlungsfluss erhalten, ohne Spannung zu verlieren. In Stressmomenten mit
weniger als 90 Sekunden Ingame-Zeit blendet das HUD automatisch einen
Countdown-Timer ein, um den Druck sichtbar zu machen.

**Option zur Mäßigung:** Einige Gruppen möchten den Würfelswing zähmen. Dafür kann die Explosion
erst ab der **zweiten gewürfelten 6** einsetzen. Der Durchschnitt pro W6 sinkt so von etwa 4,2 auf
3,9 Augen – Spannung bleibt erhalten, Ausreißer werden seltener.

**Feintuning-Varianten:** Wer Exploding-Würfel noch weiter zügeln will, hat zwei
Optionen:
- **Variante A:** Ein W6 explodiert nur, wenn eine natürliche 6 fällt **und** der
  zugrunde liegende Attributsbonus mindestens +1 beträgt. Das senkt den
  Mittelwert auf etwa 3,8 Augen.
- **Variante B:** Beim _Soft Explode_ liefern Zusatzwürfel höchstens 1–3 Punkte.
  So bleiben erzählerische Höhepunkte erhalten, ohne extreme Schadensspitzen.
- **Variante C: Burst-Cap** – Jeder Würfel darf nur **einmal** explodieren. Weitere 6er zählen normal.
  Diese Variante ist nun der **Standard** in ZEITRISS, um extreme Schadensspitzen zu bändigen.
- **Variante D:** Heldenwuerfel duerfen erst eingesetzt werden, wenn ein W6 explodiert ist.

### Sniper-Alpha-Strike eindämmen

Durch Exploding-Würfel können Fernkampfexperten gelegentlich extremen Schaden verursachen.
Um dieses "Alpha-Strike"-Phänomen auszugleichen, stehen zwei Optionen zur Wahl:

1. **Gegnerische Reaktion:** Erreicht ein einzelner Treffer **8+ Schaden**, darf die SL
   sofort eine Reaktionsprobe für das Ziel werfen – etwa "Deckung suchen".
   Gelingt die Probe, halbiert sich der erlittene Schaden, was filmisch zeigt, wie das Opfer
   in letzter Sekunde in Deckung springt.
2. **Limitierte Kill-Shots:** Pro Gefecht zählt nur ein voller Exploding-Bonus für den Scharfschützen.
   Weitere Explosionswürfe desselben Charakters erhalten **–1** Modifikator, bis die Szene endet.
   So bleiben spektakuläre Momente möglich, ohne die Balance zu kippen.

**Zielwerte je Missionsphase:** Um Proben konsistent zu halten, empfiehlt sich eine grobe Spanne:
`Aufklärung 8`, `Zugriff 12`, `Exfiltration 10`. Diese Richtwerte geben Spielern eine Vorstellung,
wie riskant ein Schritt ist und verhindern übermäßige Varianz.

## Schwierigkeits-Benchmark (Tabelle) {#schwierigkeits-benchmark-tabelle}

| Schwierigkeit | Zielwert | Beschreibung | Beispiele |
|---------------|---------:|--------------|-----------|
| Routine       | **3** | Alltag, kaum Risiko | Tür öffnen, triviales Hacken |
| Standard      | **4** | Typische Einsatzprobe | Schloss knacken, Überwachung umgehen |
| Anspruchsvoll | **5** | Merkliches Risiko | High-Security Alarm umgehen |
| Legendär      | **6** | Nur für Profis | Laserfeld im Sprint passieren |
| Episch        | **7** | Held*innen-Stufe | In 5 Sek. Quantenkern neu kalibrieren |
| Unmöglich?    | **8+** | Nur mit Boosts | Freier Fall via Telekinese bremsen |

### Referenz-Bogen {#reference-sheet}

| SG  | Würfelgröße | Schwierigkeitsgrad |
|----:|-------------|-------------------|
| 5   | W6          | Leicht            |
| 8–9 | W6/W10      | Mittel            |
| 12  | W6/W10      | Schwer            |
| 15+ | W6/W10      | Extrem            |
| Attribut | Würfelgröße |
|---------:|-------------|
| 1–10     | W6 |
| 11+      | W10 |

Nutze diese Tabelle als One-Pager im HUD (`/help`), um Zielzahlen und Würfelgrößen schnell nachzuschlagen.

## HUD-Management: Ereignis-Alerts & Info-Triage

In ZEITRISS verschmelzen HUD-Overlay und Codex.
Das HUD blendet Hinweise bei <25 % Vitalstatus ein und sobald der Paradoxon-Index wächst.
Setzt optional `alertCooldown` in eurer config.json, um Spam zu vermeiden.
Weitere Details stehen im Modul
[Cinematisches HUD-Overlay](../characters/zustaende-hud-system.md#cinematisches-hud-overlay).
```json
{
  "alertCooldown": 1
}
```
## Attributs-Skalierung: Heldenwürfel & Endgame-Balance

ZEITRISS 4.2.0 zeichnet sich durch ein schlankes Attributssystem (Werte meist im Bereich 1–10) aus.
Doch was passiert, wenn ein Held im Laufe der Kampagne über sich hinauswächst und einen Wert
jenseits der menschlichen Spitze erreicht? Hier kommt unsere neue Mechanik ins Spiel: der
**Heldenwürfel**. Dieser besondere Würfel stellt sicher, dass **Attributswerte über 10** spürbar
belohnt werden, ohne aber die Spielbalance zu sprengen.

Ein Wert oberhalb von 10 signalisiert echtes Endgame-Kaliber und schaltet auf Wunsch den W10 frei.

### Heldenwürfel (ab Attribut 14)

* Ein zusätzlicher W10 darf einmal pro Szene als Reroll verwendet werden.
* **Exploding 10er-Regel:** Zeigt der Reroll eine 10, wird erneut geworfen.
* **Beispiel:** Agent Nyx hat SCHLEICHEN 14.
  Erstwurf: 7 auf dem W10. Er nimmt den Heldenwürfel und erhält eine 10; diese
  explodiert zu einer 6 → Gesamtergebnis 16.


Diese Mechanik belohnt außergewöhnliche Werte, ohne die Balance zu sprengen. Zuvor ändern sich nur die Würfelgrößen:

| Attribut | Würfelgröße |
|---------:|-------------|
| 1–10     | W6 |
| 11+      | W10 |

Heldenwürfel gibt es ab Attribut 14. Er ermöglicht einen einmaligen Reroll pro Szene.
- **Px Burn:** 1 Punkt für einen weiteren Reroll (jeder Charakter oder NSC)

### Attribut → Ø-Erfolgsrate (SG 8)

| Attribut | Erfolg W6 | Hinweis |
|---------:|----------:| ------- |
| 1 | 0 % | Benötigt 7+ |
| 2 | 17 % | Benötigt 6 |
| 3 | 33 % | Benötigt 5+ |
| 4 | 50 % | Benötigt 4+ |
| 5 | 67 % | Benötigt 3+ |
| 6 | 83 % | Benötigt 2+ |
| 7+ | 100 % | Automatischer Erfolg |

Sobald ein Attribut den Wert 11 erreicht, blendet das HUD **„[W10 aktiv]“** ein.
Ab 14 weist es zusätzlich auf den Heldenwürfel hin. Dieser erlaubt einen
einmaligen Reroll und kann ebenfalls explodieren.

**Beispiel:** \*Chrononaut Carlos hat dank zahlreicher Abenteuer seine Geschicklichkeit auf 14
gesteigert – ein Wert jenseits normaler menschlicher Limits. Als er nun versucht, in letzter Sekunde
durch ein sich schließendes Portal zu hechten, würfelt er mit einem W10 **und** dem Heldenwürfel.
Er erzielt eine 5 und eine 7; dank des Heldenwürfels nimmt er die 7 – gerade genug, um hindurch zu
kommen. Hätte er nur den W10 geworfen, wäre vielleicht die 5 geblieben und Carlos gestrandet.
In einer späteren Szene
klettert er eine futuristische Festungsmauer hinauf. Wieder würfelt er zweimal: Eine 6 und eine 6 –
beide Würfel explodieren! Im zweiten Anlauf kommen noch eine 4 und eine 3 hinzu, also 6+4 vs. 6+3.
Carlos’ bester Wurf ist damit eine **_10_**, was ihm einen spektakulären Aufstieg über die
Festungsmauer ermöglicht, als würde ihm das Schicksal selbst einen Schub verleihen.\*

**Balance im Endgame:** So nützlich Heldenwürfel sind, so vorsichtig sollten Spielleiter mit **zu
hohen Attributwerten** am Ende einer Kampagne umgehen. Ein Wert ab 14 (mit Heldenwürfel)
macht viele normale Herausforderungen trivial – was einerseits verdienter Ausdruck des Heldentums
sein kann, andererseits aber die Spannung mindern könnte, wenn die Helden alles zu leicht schaffen.
Daher empfiehlt es sich, das **Fortschrittstempo** bei Attributen ab einem gewissen Niveau zu
drosseln. Die Spielleitung kann etwa festlegen, dass Steigerungen über 10 hinaus **besonders
selten** sind und nur durch bedeutsame Meilensteine oder aufwendiges Training erreicht werden.
Alternativ können statt reiner Zahlensteigerung mehr **qualitative Fortschritte** im Vordergrund
stehen: neue Talente, Spezialisierungen oder Ressourcen, die den Charakter verbessern, ohne bloß die
Attributszahl in die Höhe zu treiben. **Hinweis:** Denkt daran, dass selbst mit Heldenwürfel keine
Aufgabe absolut garantiert gelingt – der Würfel bleibt ein Risikofaktor. Erzählerisch können Gegner
im Endgame ebenfalls mit besonderen Vorteilen oder höheren Werten auftreten, sodass die Helden trotz
ihrer Macht gefordert bleiben. Kurz gesagt: Der _Heldenwürfel_-Mechanismus gibt den Spielern das
befriedigende Gefühl echten Heldentums, während durch umsichtiges Balancing die **dramatische
Spannung** bis zum Schluss erhalten bleibt.


#### W6 vs. W10 – Erfolgswahrscheinlichkeit {#w6-vs-w10}

| TN | Erfolg W6 | Erfolg W10 |
|----|---------:|----------:|
| 2  | 83% | 90% |
| 3  | 67% | 80% |
| 4  | 50% | 70% |
| 5  | 33% | 60% |
| 6  | 17% | 50% |
| 7  | 17% | 40% |
| 8  | 14% | 30% |
| 9  | 11% | 20% |
| 10 | 8% | 10% |

#### Wahrscheinlichkeiten (1–10 W6, Burst-Cap)

| W6 | Ø Summe | ≥ 10 | ≥ 15 | ≥ 20 |
| --:| ------: | ---:| ---:| ---:|
| 1 | 4.1 | 8 % | 0 % | 0 % |
| 2 | 8.2 | 31 % | 8 % | 1 % |
| 3 | 12.3 | 66 % | 30 % | 8 % |
| 4 | 16.3 | 91 % | 58 % | 27 % |
| 5 | 20.4 | 98 % | 82 % | 52 % |
| 6 | 24.5 | 100 % | 95 % | 74 % |
| 7 | 28.6 | 100 % | 99 % | 90 % |
| 8 | 32.7 | 100 % | 100 % | 97 % |
| 9 | 36.7 | 100 % | 100 % | 99 % |
| 10 | 40.8 | 100 % | 100 % | 100 % |
### Quick-Fight Walkthrough

1. **Initiative:** Jeder wirft `1W6 + GES` (Boni aus Talenten oder Cyberware addieren); der höchste Wert beginnt.
2. **Angriffswurf:** Beispiel: 6 auf dem W6 + STR 3 = 9 gegen SG 8.
3. **Treffer:** 9 übertrifft den SG, also gelingt der Schlag.
4. **Schaden:** Laut Tabelle zählt der Hieb als mittlere Verletzung (~3 LP).
   Kritische Treffer mit Nahkampf-Mods gewähren **+2 DMG** extra.
5. **HUD:** Das Ziel sieht `[Vitalstatus 70%]` aufblinken.


## Speichersystem-Erweiterung: Versionskennzeichnung & Kompatibilität

ZEITRISS setzt auf eine enge Verzahnung von Regelwerk und technischer Unterstützung durch den Codex
(die KI-Spielleitung). Damit eure Kampagnenstände auch über Updates hinweg reibungslos
funktionieren, führen wir ein Update im **Speichersystem** ein: **Versionstagging** für Spielstände.
Jeder gespeicherte Spielstand (im JSON-Format) erhält künftig einen
**Versionskennzeichner**, der angibt, mit welcher Regelwerks-Version er erstellt oder zuletzt
konvertiert wurde. Dies mag nach einem rein technischen Detail klingen, hat jedoch handfeste
Vorteile für die Spielpraxis – insbesondere, da ZEITRISS 4.x aktiv weiterentwickelt wird.

**Versionskennung im Spielstand:** Ab Version 4.1.4 wird bei jedem Speichervorgang automatisch ein
**"version"**-Feld in den JSON-Daten geschrieben, z. B. _"version": "4.1.4"_. Bei späteren Modulen
oder Regelupdates erhöht sich diese Nummer entsprechend (etwa auf _4.1.4_ für ein größeres Modul-
Update). Die Codex-Software prüft beim Laden eines Spielstands dieses Feld und kann so
**automatisch** erkennen, ob der Spielstand aus einer älteren Version stammt. Stimmen
Hauptversionsnummern überein (z. B. 4.1 zu 4.1.4), sind die meisten Änderungen **vorwärtskompatibel**
– d.h. der Codex lädt den Stand und **aktualisiert im Hintergrund** die nötigen Datenstrukturen.
Kleinere Versionssprünge innerhalb von 4.x sind in der Regel unproblematisch und erfordern höchstens
das Einfügen neuer Felder mit Standardwerten. Ergänzend speichert der Codex seit
_4.1.4_ optional einen kurzen **Versions-Hash** im Save-Header. Dieser sechsstellige
Hexwert wird beim Speichern aus den wichtigsten Daten berechnet und verhindert,
dass versehentlich ältere Spielstände überschrieben werden.

**Beispiel – versionskompatibler Spielstand:** \*Angenommen, in Version 4.1.4 wird ein neues Attribut
**_“Mentalstabilität”_** eingeführt, das in 4.1.3 noch nicht existiert. Ihr habt einen Kampagnen-
Spielstand aus Version 4.1.3. Ladet ihr diesen in der aktualisierten Anwendung, erkennt der Codex
anhand _"version": "4.1.3"_, dass **_Mentalstabilität_** fehlt. Beim Konvertieren des Standes auf
4.1.4 wird automatisch das Feld _"mentalstabilität": 100_ (als Start- oder Standardwert) ergänzt. Eure
Chrononauten erhalten also rückwirkend einen vollen Mentalstabilitätswert, den ihr im Spiel dann
weiter verwenden könnt. Andere 4.1.4-Regeländerungen – etwa geänderte Fertigkeitslisten oder neue
Inventargegenstände – werden ähnlich gehandhabt: Der Codex passt den Spielstand datenbankseitig an,
ohne dass eure gespeicherten Fortschritte verloren gehen.\* Auf diese Weise könnt ihr **nahtlos** mit
euren bestehenden Charakteren und Kampagnen weiterzuspielen, selbst wenn zwischendurch
Regeländerungen stattfinden.

Bei **größeren Versionssprüngen** (etwa einem Wechsel von 4.x auf 5.0 in ferner Zukunft) könnte es
Inkompatibilitäten geben, aber für diesen Fall ist vorgesorgt: Der Codex würde dann beim Laden eine
Warnung ausgeben und – sofern möglich – ein **Migrationsskript** anbieten, das die wichtigsten Daten
in die neue Edition überführt. Solche größeren Updates werden natürlich ausführlich dokumentiert.
Für den Alltag in ZEITRISS 4.2.0 aber gilt: Dank der Versionskennzeichnung könnt ihr unbesorgt updaten
und euch auf neue Module stürzen, ohne Angst um eure mühsam erspielten Speicherstände haben zu
müssen. Jede Mission, jede Entscheidung eurer Chrononauten bleibt erhalten und wird im Lichte neuer
Regeln konsistent weitergeführt.

**Nightly Auto-Save:** Nach jeder Missionsphase aktualisiert der Codex automatisch den gespeicherten
Spielzustand. So geht selbst bei Unterbrechungen oder spontanen Pausen kein Fortschritt verloren.

## Cineastische Schlachten: Erfolgspools, Spotlight-Szenen & heroische Würfe

Chrononauten erleben nicht nur Einzelkämpfe und kleine Scharmützel, sondern geraten mitunter mitten
in die großen Konflikte der Geschichte – offene Feldschlachten, städtische Aufstände oder sogar
temporale Kriege, in denen Armeen verschiedener Epochen aufeinanderprallen. Anstatt solche
Massengefechte umständlich **für jeden Gegner einzeln** auszuwürfeln, bietet ZEITRISS mit den
folgenden Regeln eine **cineastische Alternative** an, die große Schlachten abstrahiert und dennoch
den Held\*innen erlaubt, das Blatt entscheidend zu wenden. Die Devise lautet: **Filmreife Action**
mit klarem Fokus auf den Taten der Chrononauten.

**Grundprinzip – Waagschalen-System:** Stellt euch den Verlauf einer Schlacht wie eine Waage mit
zwei Seiten vor: **Seite A** repräsentiert die Verbündeten der Helden, **Seite B** die Gegenseite.
Beide Seiten beginnen in der Regel ausgeglichen oder gemäß der Story-Vorgabe leicht zugunsten einer
Seite. Durch ihre **Schlüsselaktionen** können die Spielercharaktere nun das Gewicht zu Gunsten von
A oder B verschieben. Jede erfolgreiche **Helden-Aktion** legt sprichwörtlich ein Gewicht auf die
Waagschale von Seite A (Erfolgspunkt für die Heldenseite). Gelingt den Gegnern ein bedeutender Coup
– oder versäumen die Helden eine wichtige Gelegenheit – erhält Seite B einen Erfolgspunkt (oder ein
bereits erzielter Punkt für A wird neutralisiert). Am Ende des Konflikts werden die
**Erfolgspunkte** beider Seiten verglichen:

- **A \> B:** Die Heldenseite überwiegt – die Schlacht wird **gewonnen**. Positive Konsequenzen
  treten ein (der Feind zieht sich zurück, die Mission der Helden gelingt, etc.).
- **A \< B:** Die Gegner haben mehr Punkte – die Schlacht geht **verloren**. Entsprechend treten
  negative Folgen ein (die Helden müssen sich zurückziehen, wichtige Ziele gehen verloren, die
  feindliche Agenda setzt sich durch).
- **A = B:** Ein **Patt** – keine Seite hat klar gewonnen. Dies kann einen zähen Stillstand bedeuten
  oder einen Pyrrhussieg, bei dem zwar der Gegner gestoppt wird, aber zu hohem Preis. Die SL
  entscheidet nach dramaturgischem Bedarf, wie ein Unentschieden interpretiert wird – evtl. bricht
  eine dritte Partei den Gleichstand, oder beide Seiten ziehen sich erschöpft zurück.

**Wichtig:** Die Spielercharaktere sind das **Zünglein an der Waage**. Auch wenn Hunderte um sie
herum kämpfen, bilden die Heldentaten der Chrononauten den entscheidenden Unterschied. Die große
Schlacht tobt lediglich als spektakuläre **Kulisse** im Hintergrund – beschreibt Kanonendonner,
Schlachtrufe, Chaos überall – doch das **Spielleiter-Narrativ** bleibt auf die Aktionen der Helden
fokussiert. So fühlen sich die Spieler nie als Statisten im Weltgeschehen, sondern immer als
zentrale Akteure, deren Entscheidungen den Verlauf der Geschichte prägen.

**Ablauf einer cineastischen Schlacht:** Um eine Massenschlacht nach diesem System abzuwickeln, geht
ihr in mehreren Phasen vor:

- **Szene vorbereiten:** Die SL definiert ein **Szenario** und überlegt sich ein paar
  **Schlüsselszenen**, in denen die Helden eingreifen können. Jede Schlüsselszene ist eine konkrete
  Aufgabe oder Herausforderung innerhalb der Schlacht, die das Blatt wenden könnte. _Beispiele:_ In
  der **Schlacht von Hastings** könnten die Helden (a) eine strategisch wichtige Brücke halten, (b)
  den feindlichen Anführer im Duell ausschalten oder (c) die Moral der erschöpften Verbündeten durch
  eine flammende Rede stärken. Jede dieser Aufgaben wird als eigene Szene im Spiel ausgespielt.
- **Einfluss der Aktionen:** Spielt nun jede dieser Schlüsselszenen mit den normalen Regeln aus –
  sei es im Kampf, durch Schleichen, taktisches Geschick oder Diplomatie, je nach Art der Aufgabe.
  Gelingt den Helden die jeweilige Aktion, erhalten sie **1 Erfolgspunkt** für Seite A. Misslingt
  etwas gravierend oder ignorieren die Helden eine Chance, bekommt Seite B einen Punkt (oder ein
  bereits erzielter A-Punkt wird wieder abgezogen, wenn das plausibler scheint). Wichtig ist hier ein
  bisschen Fingerspitzengefühl der SL: Nicht jeder kleine Misserfolg der Helden sollte direkt einen
  Punkt für B geben – es geht um _entscheidende_ Wendungen.
- **Zwischenergebnisse einflechten:** Nach jeder Schlüsselszene skizziert die SL kurz, **wie der
  Schlachtenverlauf sich entsprechend verändert**. So bleibt das Geschehen dynamisch und die Spieler
  sehen direkt die Auswirkungen ihrer Taten. _Beispiel:_ Haben die Helden die Brücke erfolgreich
  gehalten (+1 für A), gewinnen ihre Verbündeten Zeit und einen taktischen Vorteil – vielleicht ziehen
  sich die Feinde kurz zurück, oder ein geplanter Flankenangriff misslingt dem Gegner. Scheitern die
  Helden später dabei, den feindlichen Champion aufzuhalten (Punkt an B), kippt das Blatt wieder: Die
  gegnerischen Truppen schöpfen neue Moral, da ihr Champion wütet, und drücken die Verbündeten zurück.
  Solche eingestreuten Schilderungen machen deutlich, wie **flexibel** das Gefüge ist und dass die
  Helden wirklich etwas bewegen.
- **Finale & Vergleich:** Sobald alle geplanten Schlüsselszenen gespielt sind (oder die Helden aus
  Zeitmangel nicht mehr eingreifen können), kommt es zum **Finale**. Vergleicht die auf A und B
  angesammelten Erfolgspunkte und bestimmt das **Endergebnis** der Schlacht gemäß dem Waagschalen-
  Prinzip (Sieg/Niederlage/Patt). Die SL beschreibt nun **cineastisch**, was geschieht: Haben die
  Helden genug Impact erzielt, bricht vielleicht die feindliche Armee panisch auseinander, der
  gegnerische Kommandant ergibt sich oder die Allianz der Helden feiert einen hart erkämpften Triumph.
  Haben die Punkte nicht gereicht, tritt das düsterere Szenario ein – vielleicht werden die Helden zur
  Rückzugsordnung gezwungen, während der Feind sein grausames Werk vollendet. Wichtig ist, dass das
  Ende **logisch** aus den Erfolgspunkten und der Story hervorgeht, aber dennoch Raum für
  Überraschungen lässt.
- **Nachspiel:** Jede Schlacht, ob gewonnen oder verloren, hat Konsequenzen. Nehmt euch als SL Zeit,
  das **Nachspiel** auszuleuchten. Welche langfristigen Folgen hat der Ausgang für die Kampagne?
  Wurden wichtige Personen gerettet oder getötet? Hat ein Sieg vielleicht neue Probleme geschaffen
  (z. B. Machtvakuum, Racheakte der Verlierer) oder bedeutet eine Niederlage einen dramatischen
  Wendepunkt für die Helden? Indem ihr die Nachwirkungen beschreibt, verleiht ihr den zuvor abstrakten
  Erfolgspunkten echtes **Gewicht**. Die Spieler spüren, dass ihre Anstrengungen die Geschichte
  beeinflusst haben – im Guten wie im Schlechten.

**Heroische Schlüsselwürfe:** In cineastischen Schlachten kulminieren viele Schlüsselszenen in
**einem entscheidenden Wurf** – dem Schlag gegen den feindlichen Kriegsherrn, der Charisma-Probe bei
der Ansprache an die Truppen, der Hack des Schutzschilds zur rechten Zeit. Diese Würfe solltet ihr
besonders dramatisch inszenieren. Die _Heldenwürfel_-Regel und _Exploding Dice_ kommen hier voll zur
Geltung: Wenn je ein Zeitpunkt für explodierende Ergebnisse oder Vorteilwürfe gegeben ist, dann in
diesen **Schlüsselmomenten**. Ermutigt die Spieler, alle Register zu ziehen (Chrono-Energie,
Ausrüstung, Teamwork), um den Wurf zu beeinflussen – denn vom Gelingen hängt oft das Schicksal der
gesamten Schlacht ab. Gleichzeitig dürfen Fehlschläge nicht antiklimaktisch sein: Selbst wenn der
entscheidende Wurf misslingt, sollte die daraus entstehende Wendung erzählerisch spannend bleiben
(z. B. erscheint im letzten Moment doch noch Verstärkung der Gegner, oder der Held erzielt zwar
keinen perfekten Erfolg, rettet aber zumindest einige Verbündete vor dem Schlimmsten).
**Cineastisch** bedeutet nicht, dass immer alles gut ausgeht – sondern dass es immer spektakulär und
bedeutsam für die Story ist.

**Hinweis:** Dieses cineastische Schlachtensystem lässt sich nicht nur für militärische Konflikte
verwenden, sondern ebenso für **soziale Umwälzungen, Wettstreite oder Katastrophenszenarien**. Man
denke an Revolutionen, in denen nicht Armeen, sondern Ideen gegeneinanderstehen – auch dort können
Erfolgspools gesammelt werden (z. B. Einfluss gewinnen vs. verlieren). Oder an ein Hacker-Duell in
der Cyberzeit, wo zwei KI-Netzwerke ringen und die Helden durch ihre Eingriffe Erfolgspunkte für die
jeweilige Seite sammeln. Passt die Art der Schlüsselszenen einfach dem Thema an: In einer
politischen Krise könnten es Debatten, Enthüllungen oder Sabotageakte sein, die den Ausschlag geben.
Die Mechanik bleibt gleich – nur das _Flair_ ändert sich. Wichtig ist, die Grautöne zu beachten:
Gerade in sozialen Konflikten gibt es nicht immer strahlende Sieger. Die SL sollte die Ergebnisse
ggf. mit moralischer Vielschichtigkeit darstellen (z. B. bringt ein Sieg der Revolution zwar
Freiheit, aber auch Chaos; eine Niederlage der Helden bewahrt kurzfristig den Frieden, lässt aber
Unterdrückung bestehen usw.). So bleibt das Spiel tiefgründig und der **Zeitreise-Aspekt** – mit all
seinen Paradoxien – wird gekonnt in Szene gesetzt.

Mit diesen Erweiterungen – von explodierenden Würfeln über Heldenwürfel und HUD-Alerts bis hin zu
cineastischen Schlachten und versionierten Speicherständen – erhält ZEITRISS 4.2.0 einen weiteren
Feinschliff. Spielrunden können nun noch flexibler entscheiden, welchen **Ton** sie anschlagen
wollen: Knallhart taktisch, filmisch-überdreht oder eine balancierte Mischung. Alle neuen
Modulelemente fügen sich nahtlos ins existierende Regelwerk ein. Nutzt diejenigen, die eure Kampagne
bereichern, und passt sie an euren Stil an. Ob eine unwahrscheinliche Würfelkette den Tag rettet,
der Codex mit Warnmeldungen das Team vor dem Schlimmsten bewahrt oder die Chrononauten in einer
gewaltigen Schlacht Geschichte schreiben – das Wichtigste ist, dass eure ZEITRISS-Runde
unvergessliche gemeinsame Abenteuer erlebt. In diesem Sinne: _Würfel bereit, HUD kalibriert – und
Film ab!_

## Cheat-Cards: Kompakte Referenz

Diese Tabellen passen auf eine A6-Karte oder ins HUD.

### Erfolgsschwellen (W6)

| Schwierigkeit | Schwelle |
| ------------- | -------- |
| leicht        | 5        |
| mittel        | 8–9      |
| schwer        | 12       |
| extrem        | 15+      |

### Beispielsprünge

| Schwierigkeit | Beispiel                                 |
| ------------- | ---------------------------------------- |
| 5             | Sprung über eine kleine Lücke            |
| 8–9           | Hacken eines gesicherten Terminals       |
| 12            | Deaktivierung eines Zeitbomben-Prototyps |
| 15+           | Absprung von einem abstürzenden Zeppelin |

### Paradoxon-Index

*Siehe auch das*
*[Paradox-Subsystem](../characters/zustaende-hud-system.md#paradox-subsystem)*
*für eine ausführliche Beschreibung.*

| Stufe | Effekt                     |
| ----- | -------------------------- |
| 0–1   | Stabil                     |
| 2     | Resonanzimpuls (−1 Stress) |
| 3     | Zeitflimmern (Team heilt 1 HP) |
| 4     | Tempowelle (+2 Initiative auf nächste Aktion) |
| 5     | ClusterCreate() im HQ      |

Der Index steigt vor allem, wenn ihr Missionen voranbringt oder Anomalien stabilisiert.
Scheitert ein Auftrag oder wird abgebrochen, bleibt der Wert stehen.
Gravierende Fehlentscheidungen oder Paradoxa können den Index in Ausnahmefällen
um **–1** senken (Px–1).
Einfache Begegnungen mit Zeitzeugen zählen nur, falls sie Resonanz im Szenario erzeugen.

> **Paradoxon-Pro-Tip:**
> *Jeder gelöste Hauptauftrag erhöht den Index um +1 bei **TEMP 14+**, entsprechend langsamer bei weniger.*
> *Scheitert ein Auftrag oder wird abgebrochen, bleibt der Wert stehen.*
> Riskantere Nebenaufgaben können Rifts schneller freischalten – das Team entscheidet.

### Seed-Counter im HUD

Sobald Paradoxon-Index **5** erreicht ist, markiert das HQ nach Missionsende 1–2 Rift-Seeds auf der Raumzeitkarte.
Stat-Blöcke und Schadenswerte der dort auftauchenden Zeitkreaturen findest du im
[Kreaturen-Generator](../gameplay/kreative-generatoren-begegnungen.md#kreaturen-generator).
Der Counter zeigt die offenen Seeds an und beeinflusst Schwellen sowie CU-Multiplikator:

| Offene Seeds | Probe-Schwelle + | CU-Belohnung × |
| ------------ | ---------------- | -------------- |
| 0            | 0                | 1.0            |
| 1            | +1               | 1.2            |
| 2            | +2               | 1.4            |

_Im HUD erscheint z.B. `[Seeds 1 | Para 5]`._ Die Schwelle jeder Mission –
Die Schwelle jeder Mission nutzt diese Werte ab Episodenende und sinkt, sobald ein Seed verschwindet.
**Live-Formel:** `probe_sg = grund_sg + (rifts_open * sg_rift_bonus) + situational_mods`
Der Rift-Bonus greift erst nach der Episode, wenn ein neuer Riss entsteht.

### Standard-Ausrüstungsslots

- 1 Hauptwaffe
- 1 Zweitwaffe
- 2 Hilfsgeräte
- 1 Spezialobjekt

## Beispiel-Play: Duo-Infiltration in Ost-Berlin 1961 {#beispiel-play}

Dieses kurze Beispiel orientiert sich am offiziellen Testfeld **Szenario 1**.
Zwei Chrononauten – ein **Tech**- und ein **Face**-Agent – schleichen in einen
Keller, um eine Stasi-Abhörleitung zu kappen. Es zeigt Schritt für Schritt, wie
die Regeln ineinandergreifen.

### 1. Aufklärung

Die Agenten sondieren das Gebäude. Ein verdeckter Wurf auf **Wahrnehmung**
(blaues Attribut: Geschicklichkeit) gegen SG 8 entscheidet, ob sie versteckte
Mikrofone entdecken. Der Tech-Agent würfelt eine `6` und darf laut der
**Exploding 6**‑Regel einen Zusatzwurf ausführen. Dieser zeigt `3`, womit das
Ergebnis bei `9` liegt – die Wanzen werden entdeckt.

### 2. Zugriff

Mit einem improvisierten Störsender betritt das Duo den Keller. Die SL bittet um
je eine Probe auf **Technik** (grünes Attribut) und **Täuschen** (gelb). Der
Face-Agent würfelt eine natürliche `6`, der Zusatzwurf zeigt `3`. Die Summe `9`
übertrifft den SG von 7 – die Wachen merken nichts.

### 3. Dramatischer Konflikt

Als der Störsender einen Funkschlag auslöst, kommt Hektik auf. Es folgt eine
kurze Initiative-Runde. Dank der **Quick-Reference** sieht jeder Spieler auf
einen Blick, welche Werte und Talente gelten. Der Tech-Agent klemmt das Kabel
ab, während der Face-Agent die Tür versperrt. Sein Wurf auf
**Geschicklichkeit** zeigt eine `6` und darf deshalb explodieren. Der
Zusatzwurf ergibt `2`, insgesamt also `8` Punkte – gerade genug, um die
heranstürmende Sicherheitskraft abzuwehren.

### Farbcode der Würfeltabelle

| Farbe   | Attribut         |
| ------- | ---------------- |
| **Rot** | Stärke           |
| **Blau** | Geschicklichkeit |
| **Grün** | Intelligenz      |
| **Gelb** | Charisma         |
| **Grau** | TEMP             |
| **Lila** | SYS              |

Die Farben korrespondieren mit den Tabellen im
[Modul zur Charaktererschaffung](../characters/charaktererschaffung.md) und
helfen neuen Gruppen, die Proben den richtigen Werten zuzuordnen.

### 4. Exfiltration

Mit gekapptem Kabel ziehen sich beide Agenten zurück. Ein kurzer "Atemzug"
zwischen den Szenen reduziert den Stress um 1 Punkt, wie im Modul
[Zustände & HUD](../characters/zustaende-hud-system.md) beschrieben.

Dieses Beispiel zeigt, wie flüssig die Kernmechanik abläuft und wie
Exploding-Würfel filmische Spitzen erzeugen, ohne den Spielfluss zu bremsen.

**Exfiltration-Hürden:**
- Engpässe sichern und Alarme überwachen.
- Gegnerische Verstärkung trifft nach `1W6` Runden ein, falls ein Alarm
  ausgelöst wird.
- Kommunikationswege kappen oder stören.
- Spuren verwischen und Daten löschen.
- Rücksprungsignal setzen: Paradoxon-Index melden und Koordinaten
  bestätigen.

### Negativ-Beispiel: Risiko-Fail

Manchmal kippt ein Exploding 6 gegen die Agenten. Bei einem nächtlichen Einbruch
würfelt ein Wachposten eine `6` und darf erneut würfeln. Die Zusatz-
`5` hebt seinen Gesamtwert auf `11` – deutlich über dem SG der
Schleichprobe. Der Gegner erhält einen Vorteil, etwa einen freien
Angriff oder Alarmbereitschaft. So zeigt sich, dass Exploding-Würfel
beide Seiten begünstigen können.

### Quick-Sheet: Psi & Massenkonflikt {#quick-sheet}

Diese knappe Übersicht hilft beim schnellen Nachschlagen während des Spiels.
**Dieses Quick-Sheet dient als zentrale Kurzreferenz und lässt sich im HUD über `/help` aufrufen.**

| Ergebnis | SG-Richtwert | Exploding-Beispiel | PP-Regel |
|---------|-------------|-------------------|---------|
| **Fail** | < SG | 4 auf W6 → Misserfolg | – |
| **Success** | ≥ SG | 6 explodiert, dann 5 → 11 | pro 3 TEMP 1 PP (CHA als Willenskraft vs 2×Heat) |
| **Critical** | ≥ SG + 5 | 10 → 10 → 3 = 23 | PP-Pool voll nach Kampf |

### Quick Reference (2 Seiten)

| Situation   | Standard                                | High‑Attribut (≥ 11) |
|-----------|----------------------------------------|----------------------|
| Würfeltyp | W6 (Attribut 1–10)                     | W10 |
| Bonus     | –                                      | Heldenwürfel ab 14 |
| Exploding | Jede 6 bzw. 10 explodiert einmal        |                      |
| SG-Beispiele | Leicht 5 · Mittel 8–9 · Schwer 12 · Extrem 15+ | |
| HUD-Alerts | Kurz halten, max. 6 Wörter             | |
**Paradoxon‑Index (Px)** – 0–2 = rot ⏳, 3–4 = gelb ⏳, 5 = grün ⌛ → `ClusterCreate()`
und Reset auf 0. Offene Seeds steigern den SG um +1 pro Seed.
**Px +0,1–0,3:** Missionsfortschritt laut Tabelle (Stabilisierung nur gering) |
**Px Burn:** 1 Punkt für einen Reroll (auch NSC)
Siehe [ClusterCreate-Nebenwirkungen](../gameplay/kreative-generatoren-begegnungen.md#clustercreate-nebenwirkungen)
für mögliche Folgeszenarien.
**Psi-Heat-Track** – 0 Pristine, 1–2 Warm, 3–4 Hot (−1 Ini), 5 Overload (SG +4 auf alle Proben),
6 Reboot → Runde aussetzen & Heat 0


**Psi-Effekte auf einen Blick**

- **Telepathie (1 SYS)** – Gedanken lesen oder kurze Botschaften senden.
  TEMP-Probe gegen die Willenskraft (CHA) des Ziels.
- **Präkognition (2 SYS)** – einmalige Vorahnung; erlaubt einen Wurf zu wiederholen
  oder gewährt einen hilfreichen Hinweis.
- **Zeit verlangsamen (2 SYS)** – gewährt eine zusätzliche Aktion oder einen
  deutlichen Bonus auf eine Reaktion; kostet viel Konzentration.
- **Temporaler Waffenimpuls (3 SYS)** – Angriff nach kurzem Zeitstillstand
  verursacht erhöhten Schaden. Misslingt der Einsatz, verliert das Team
  **1 Px**. Bei gravierenden Eingriffen springt der Index ohne ClusterCreate
  auf **0**.
- **Zeitsinn (passiv)** – spürt Anomalien und Zeitreisende im Umfeld.

**Massenkonflikt-Rundendurchlauf**

1. **Lagecheck** – SL beschreibt Aufstellung und Ziele aller Trupps.
2. **Initiative** – jede Seite erhält einen Spotlight-Moment pro Runde.
3. **Aktionen** – Helden setzen Manöver, Psi oder Taktik ein; Gegner reagieren.
4. **Erfolgspool prüfen** – erzielte Schlüsselszenen zählen als Punkte, die den Ausgang beeinflussen.
5. **Folgen & Übergang** – nach jedem Durchlauf passen sich Moral, Ressourcen und Gelände an.

_Orientierung:_ Kleine Gefechte brauchen 1–2 Punkte, mittlere Schlachten 3–5, große Konflikte 5+.

### Quickref: Rift-Überblick

| Seeds offen | Probe-Schwelle + | CU-Multi |
|-------------|-----------------|---------|
| 0 | 0 | 1.0 |
| 1 | +1 | 1.2 |
| 2 | +2 | 1.4 |

Diese Tabelle fasst kompakt zusammen, wie offene Risse Schwierigkeitsgrad und Belohnungen beeinflussen.
*Boni gelten erst nach Abschluss der aktuellen Episode.*

### Timeline-Konfliktresistenz {#konfliktresistenz}

| Situation | Modifikator |
|-----------|-------------|
| Eigene Epoche, bekannte Abläufe | 0 |
| Leichte Abweichung in naher Vergangenheit | −1 auf Stabilitätswürfe |
| Massive Zeitmanipulation oder fremde Ära | −2 auf Stabilitätswürfe |

Nutzt diese Tabelle auf dem Quick-Reference-Sheet, um schnell abzuschätzen, wie anfällig eine Szene
für Paradox-Effekte ist.

### Rift-Kreaturen auf die Schnelle {#rift-quickbuild}

| Schritt | Vorgehen |
| ------- | -------- |
| 1 | Basistier oder NSC-Vorlage wählen |
| 2 | 1–3 Anomalien hinzufügen (z.B. Zeitsprung, Psi, Mutation) |
| 3 | **Threat** = 1 + Anzahl der Anomalien (max. 5 💀) |

Mit dieser Kurzformel kann die SL jederzeit eine improvisierte Rift-Kreatur bauen.
Weitere Details stehen im [Kreaturen-Generator](../gameplay/kreative-generatoren-begegnungen.md#kreaturen-generator).

### Blind-Ops Cheat Sheet {#blind-ops}

Kurzanleitung für Missionen ohne funktionierenden Codex oder HUD.

#### Grundlegende Aktionen

- **Angreifen:** `1W6 + Fertigkeit` gegen SG
- **Hacken:** `TEMP oder TECH` gegen Sicherheit
- **Heilung:** Verbandskasten = 1W6 HP in 10 Min

#### Wichtige Befehle

| Kommando | Wirkung |
| -------- | ------- |
| `scan` | Einfacher Umgebungsscan |
| `lock` | Schloss knacken/hacken |
| `status` | Eigenen Zustand prüfen |

Diese Liste kann ausgedruckt werden, um den Spielablauf bei Funkstille zu erleichtern.

### Dynamische Bedrohung – Heatmap-System

Wiederholte Tech-Lösungen erhöhen die Schwierigkeit späterer Tech-Proben. Die SL führt einen
Zähler `tech_heat` von 0 bis 3. Nach jeder rein technischen Lösung gilt:

1. `tech_heat` + 1.
2. Bei `tech_heat >= 3` steigt `tech_sg` um +1, `tech_heat` fällt auf 0 und einmal pro Szene löst
   `inject_complication()` eine soziale oder physische Hürde aus.

So zwingt das System zu vielfältigen Herangehensweisen und verhindert Terminal-Dominanz.

### Würfel‑Cheat‑Sheet

| Attribut | Würfel | Besonderheiten |
|---------:|-------|----------------|
| 1–10 | 1×W6 | Exploding 6, Burst‑Cap 3 |
| 11+  | 1×W10 | 10 explodiert einmal |

**Erfolgsschwelle**
Standardziel 5. Der W10 ändert die Schwelle nicht.

**Heldenwürfel**
Einmal pro Szene als Reroll. Nur bei Attribut 14+.

### Druckbare Kurzreferenz (2 Seiten) {#druckreferenz}

1. **Phasenablauf:** Briefing → Infiltration → Kontakt/Intel → Konflikt → Exfiltration → Debrief.
2. **Würfel:** 1W6, ab Attribut 11 ein W10 (Exploding 10). Heldenwürfel ab 14.
3. **Paradoxon-Index:** wächst mit Missionsfortschritt oder Stabilisierung; bei 5 löst `ClusterCreate()` aus.
   Er setzt den Zähler auf 0. Neue Rift-Seeds sind erst nach Episodenende zugänglich.
4. **Stress & Health:** reichen von 0 bis 10; Heilung erfolgt hauptsächlich in der
HQ-Phase.
5. **Kurzbefehle:** `/roll Xd6`, `launch_rift(id)`, `scan_artifact()`.

Diese Liste deckt die Kernmechaniken ab und passt auf zwei druckbare Seiten.
*© 2025 pchospital – private use only. See LICENSE.
