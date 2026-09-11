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
| Px-Reset und neuer Zyklus | `systems/gameflow/speicher-fortsetzung.md` §Paradoxon-Index | DB-1-Roundtrip, danach DB-2 |
| Startguard und konkrete ID | `core/spieler-handbuch.md` §Start-/Load-Regeln | unbekannt/geschlossen/Übergang/Arena |
| SG-/CU-Einsatz-Snapshot | `gameplay/kampagnenstruktur.md` §Offene Rifts | n=2, Schließung, Folgeeinsatz |
| persönliche Abgabe | `gameplay/kampagnenstruktur.md` §Rifts sammeln | Leader- und Gastbesitzer, aktiv/fremd geschützt |
| persönlicher Export | `systems/gameflow/speicher-fortsetzung.md` §Projektionsreihenfolge | fünf strikte v7-Exporte und JSON-Neuladen |
| Gruppenwechsel | `systems/gameflow/speicher-fortsetzung.md` §Persönlicher Gruppenwechsel | B/C sowie A/E ohne Pool-Union |

## Abgedeckte Fälle

- Mid-Episode-HQ-Start eines offenen Rifts und unveränderte Core-Zähler.
- Erster Save als Leader; Gastbestände beeinflussen weder Board noch SG/CU.
- Kontrollierte Einzelvergabe B/C mit erneuter Kapazitätsprüfung, Ausschluss
  voller Figuren und stabilem Debrief-Schlüssel.
- Voller Bestand: ITI-Übernahme ohne Löschen oder Ersatz, Px-Abschluss auf 0.
- Fünf persönliche Exporte statt Gruppencontainer; Gastkampagnen/Px bleiben
  erhalten und getrennte Folgegruppen vereinigen keine Rift-Bestände.
- Stabile Instanz-IDs, fester Einsatz-Snapshot und Wirkung einer Schließung erst
  auf den Folgeeinsatz.
- Kostenfreie idempotente Besitzer-Abgabe sowie Legacy-Öffnung und Erhalt eines
  Altbestands über zwölf.

Die synthetische Folge verwendet vollständige v7-Fixtures, definierte
Abschlussdaten, Projektion, JSON-Serialisierung und eine tatsächlich neu
geöffnete Session. Sie simuliert weder Kampf noch Match.

## Prüfebenen

- **Deterministische Zustandsfälle:** persönliche Projektion, Runtime-Guards,
  Snapshot, Abgabe und erneuter Import.
- **Statische Checks:** Schema-/Inhaltsvalidatoren, geladene Textanker und
  verbotene aktive Gegengates.
- **Synthetische Redaktion:** die oben beschriebenen fest vorgegebenen
  Abschlussdaten; keine Aussage über Modellverhalten.

## Ausführung

- `node tools/test_rift_hq_flow.js`: deterministische Zustandsfälle.
- `node tools/test_load.js`: Leader-Bestand bleibt beim Gastimport getrennt.
- `bash scripts/smoke.sh`: vollständiger statischer und deterministischer Stack.
- `git diff --check`: Whitespace-/Patchprüfung.
