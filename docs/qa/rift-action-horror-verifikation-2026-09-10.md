# Rift-Action-Horror – synthetische Redaktionsprüfungen (2026-09-10)

## Datensatz-vs-Dev-Check

- **Datensatz-Relevanz:** Ja; geprüft wurden Regeln und Beispiele in geladenen Wissensmodulen und Masterprompt.
- **Nur Dev/QA:** Dieser Bericht ist QA-Evidenz, nicht selbst Spielwissen.
- **WS-Spiegelpflicht:** Erfüllt in Missions-/Begegnungsgenerator, Kampagnenstruktur, Toolkit und Masterprompt.
- **Invarianten betroffen:** Nein; Save v7, 14 Szenen, Boss-Einstieg Szene 10, Bossphasen, Belohnungen und HQ-Exfil bleiben unverändert.

Die folgenden Fälle sind **synthetische Redaktionsprüfungen**. Echte Modell- oder
Plattformtests wurden nicht durchgeführt; frühere Spieler-Rückmeldungen und historische
Juni-QA gelten nicht als Abnahme dieses Patchstands.

## Fall 1 – Raumfahrt: Station Nadir

- **Ausgangslage:** Eine abgeschottete Orbitalstation schweigt; der interne Fallkern sind körperliche Jagdwesen mit Nestboss, ohne aktiven Zeit-Skill.
- **Spieleraktion:** Das Team verfolgt Kratzspuren und beschädigte Filter, öffnet per Wartungszugang einen Rettungsweg und lockt den Boss mit Kühlmittel ins Druckschott.
- **Beispielreaktion:** Überlebende melden nur Geräusche und Wege, die sie kennen. Das Rudel reagiert auf die Falle statt auf verborgenes Spielerwissen; eine umgangene Patrouille wird nicht erzwungen nachgesetzt.
- **Regelabgleich:** Rettung, konkrete Wegführung, frühe Gefahr und physische Schwäche erfüllen den Rift-Fall. Der fehlende Zeit-Skill ändert weder Rift-Status noch drei Bossphasen; reguläre Exfil/HQ-Rückkehr bleibt offen.

## Fall 2 – Katakomben: Rabensteg

- **Ausgangslage:** Dorfbewohner nennen die Kreaturen unter dem Beinhaus Dämonen; Gefangene leben noch. Boss und Brut stammen aus demselben Fallkern.
- **Spieleraktion:** Die Crew deutet Kratzspuren und einen blutigen Fluchtweg, täuscht eine Brutgruppe mit Tierkadavern und nutzt Lampenöl sowie Einsturzstützen gegen die Bossflanke.
- **Beispielreaktion:** Die Täuschung öffnet den Rettungsweg; die KI-SL teleportiert keine Gegner hinterher. Weitere räumlich zusammenhängende Gefechte nutzen vorhandene Schwereklassen statt einer neuen Hordenregel.
- **Regelabgleich:** Mehrere Kreaturen erzeugen keine neue Anomalie pro Körper. Einwohnerwissen bleibt epochenplausibel, die Para-Bedrohung echt, körperlich und ohne wissenschaftlichen Lore-Dump.

## Fall 3 – Appalachen: Kestrel Hollow

- **Ausgangslage:** Nach einer Mordserie verbindet eine Zeugin reale Fundorte im Wald; der Nightcrawler besitzt einen einzelnen angekündigten Bewegungsslip.
- **Spieleraktion:** Das Team gleicht Doppelfährten, Harzfasern und Jagdzeiten ab, schützt die Zeugin und spannt an einer Kalkstein-Enge eine beleuchtete Fanglinie.
- **Beispielreaktion:** Der Boss setzt den begrenzten Slip sichtbar in einer Phase ein; Licht und Engstelle bleiben wirksam. Bio + Material klassifizieren den Fall ohne temporale Pflichtanalyse.
- **Regelabgleich:** Ermittlung geschieht während Schutz und Jagd. Der Zeittrick wickelt keinen Treffer oder Entschluss zurück; ein Nicht-Psi-Team kann Weakness, Bossphasen und Abschluss regulär bewältigen.

## Gegenfälle

- **Core-Raumfahrt:** Ein Core-Auftrag auf einem Schiff bleibt Core-Thriller; Ort und Epoche aktivieren keinen Rift-Horror.
- **Nicht-Psi-Team:** Terrain, normale Ausrüstung und bestehende Proben eröffnen einen vollständigen Lösungsweg; Psi ist höchstens Abkürzung.
- **Rift-Boss ohne Zeit-Skill:** Der zusammenhängende außergewöhnliche Ursprung genügt; körperlicher Boss und vorhandene Phasen bleiben vollwertig.
- **Gegnergruppe:** Brut, Rudel oder Befallene desselben Kerns werden nicht einzeln via `register_anomaly()` registriert; unverbundene Monster bleiben ausgeschlossen.
- **Täuschung/Umgehung:** Gelungene Aktionen verändern den Weg. Gegner erhalten ohne sichtbare Spur, Alarm oder nachvollziehbare Ursache kein Wissen; eine Kampfquote überschreibt den Erfolg nicht.
