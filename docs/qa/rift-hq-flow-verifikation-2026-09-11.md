# Rift-HQ-Flow – Verifikation 2026-09-11

## Umfang

Deterministische Zustandsprüfung des persönlichen Leader-Rift-Flows sowie
gezielte statische Textprüfungen. Echte Modell-, Chat-Plattform- und manuelle
Playtests wurden nicht durchgeführt.

## Entscheidungsmatrix

| Spielentscheidung | Geladene Hauptstelle | Deterministischer Fall |
| --- | --- | --- |
| erster Save wählt Leader | `systems/gameflow/speicher-fortsetzung.md` §Persönlicher Gruppenwechsel | A/B/C/D/E-Roundtrip |
| persönliche Einzelvergabe | `systems/gameflow/speicher-fortsetzung.md` §Kleine v7-Ablage | DB-1 weist B und C zu |
| Neuerwerbslimit/ITI | `gameplay/kampagnenstruktur.md` §Rifts sammeln | alle voll / letzter Platz |
| Px-Reset und neuer Zyklus | `systems/gameflow/speicher-fortsetzung.md` §Paradoxon-Index | stabile Abschluss-IDs, Budget-Roundtrip, danach neuer Folgeabschluss |
| Startguard und konkrete ID | `core/spieler-handbuch.md` §Start-/Load-Regeln | unbekannt/geschlossen/Übergang/Arena |
| SG-/CU-Einsatz-Snapshot | `gameplay/kampagnenstruktur.md` §Offene Rifts | tatsächlicher `launch_rift('A-R1')`, n=2, legaler Debrief, Folgeeinsatz |
| persönliche Abgabe | `gameplay/kampagnenstruktur.md` §Rifts sammeln | Leader- und Gastbesitzer, aktiv/fremd geschützt |
| persönlicher Export | `systems/gameflow/speicher-fortsetzung.md` §Projektionsreihenfolge | fünf strikte v7-Exporte und JSON-Neuladen |
| Gruppenwechsel | `systems/gameflow/speicher-fortsetzung.md` §Persönlicher Gruppenwechsel | B/C sowie A/E ohne Pool-Union |
| schlanke Kontinuität | `systems/gameflow/speicher-fortsetzung.md` §Persönliche Saves | eigene Kampagne → zwei Gastmissionen → Save → andere Gruppe → Wiedersehen |
| Projektionsreihenfolge | `systems/gameflow/speicher-fortsetzung.md` §Persönlicher Leader-Rift-Vertrag | P1–P5 und Trace-Budget |

## Abgedeckte Fälle

- Mid-Episode-HQ-Start eines offenen Rifts und unveränderte Core-Zähler.
- Erster Save als Leader; Gastbestände beeinflussen weder Board noch SG/CU.
- Kontrollierte Einzelvergabe B/C mit erneuter Kapazitätsprüfung, Ausschluss
  voller Figuren und stabiler Leader-/Einsatz-Abschlussidentität.
- Voller Bestand: ITI-Übernahme ohne Löschen oder Ersatz, Px-Abschluss auf 0.
- Fünf persönliche Exporte statt Gruppencontainer; Gastkampagnen/Px bleiben
  erhalten und getrennte Folgegruppen vereinigen keine Rift-Bestände.
- Stabile Instanz-IDs, fester Einsatz-Snapshot und Wirkung einer Schließung erst
  auf den Folgeeinsatz.
- Kostenfreie idempotente Besitzer-Abgabe sowie Legacy-Öffnung und Erhalt eines
  Altbestands über zwölf.
- **Synthetischer Redaktionsfall:** Eine Figur wechselt aus ihrer eigenen Kampagne
  für zwei Gastmissionen in eine Gruppe, nimmt ihren persönlichen Save in eine
  andere Gruppe mit und trifft die frühere Gruppe später wieder. Eigene Kampagne
  und persönliche Fortschritte bleiben erhalten; ein verdichteter gemeinsamer
  Erinnerungsanker genügt für den Anschluss, ohne Branch-Abgleich. Dies ist kein
  Modelltest.
- Historischer Payoff vor neuem Leader-Fortschritt, Payoff nur beim Gast,
  aktuelle Rift-Schließung, aktuelle Notiz-/Markt-/Artefakt-/Flag-Daten,
  Log-Konsolidierung und Gast-Zuweisung gegen einen veralteten Abschlussblock
  (P1–P5). Das Trace-Budget wurde außerdem mit 200 alten plus 200 neueren
  Ereignissen und einem Payoff-Roundtrip an der Kürzungsgrenze ausgeführt.

Die synthetische Folge verwendet vollständige v7-Fixtures, definierte
Abschlussdaten, Projektion, JSON-Serialisierung, eine tatsächlich neu geöffnete
Session sowie den echten Runtime-Pfad `launch_rift()` mit anschließendem
`debrief()`. Sie simuliert weder Kampf noch Match. Eine Modell- oder
Plattformausführung wird daraus ausdrücklich nicht abgeleitet.

## Redaktioneller Nachtrag

Die aktiven Kurzregeln im Masterprompt und Kampagnenmodul wurden auf den
persönlichen Gruppenwechsel sowie die Rift-Freigabe nach vollständigem Debrief
im nächsten frischen freien HQ-Chat konsolidiert. Split-/Konvergenzdaten und der
zugehörige Präzedenzgraph sind ausdrücklich nur historische Importkompatibilität;
dieser Nachtrag dokumentiert eine statische Prüfung, keinen Modelltest.

## Prüfebenen

- **Deterministische Zustandsfälle:** persönliche Projektion, Runtime-Guards,
  Snapshot, Abgabe und erneuter Import.
- **Statische Checks:** Schema-/Inhaltsvalidatoren sowie Textanker in den laut
  `master-index.json` geladenen 19 Slots und im Masterprompt; `internal/` ist
  dafür keine Ersatzquelle.
- **Synthetische Redaktion:** die oben beschriebenen fest vorgegebenen
  Abschlussdaten; keine Aussage über Modellverhalten.
- **Echte Modell-/Plattformtests:** nicht durchgeführt.

## Ausführung

- `node tools/test_rift_hq_flow.js`: deterministische Zustandsfälle.
- `node tools/test_load.js`: Leader-Bestand bleibt beim Gastimport getrennt.
- `bash scripts/smoke.sh`: vollständiger statischer und deterministischer Stack.
- `git diff --check`: Whitespace-/Patchprüfung.
