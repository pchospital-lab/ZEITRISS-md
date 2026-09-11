# Rift-HQ-Flow – Verifikation 2026-09-11

## Umfang

Deterministische Zustandsprüfung des persönlichen Leader-Rift-Flows. Es wurden
keine kostenpflichtigen Modell- oder Plattformtests ausgeführt.

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

Die synthetische Folge lautet: Core MS3 → Debrief/Zuweisung → persönliche Saves
→ neuer HQ-Chat → zwei Leader-Rifts nacheinander oder Core MS4. Der Test arbeitet
mit definierten Abschlussdaten und echten Load-/Projektionshelfern, nicht mit
einer Kampfsimulation.

## Ausführung

- `node tools/test_rift_hq_flow.js`: deterministische Zustandsfälle.
- `node tools/test_load.js`: Leader-Bestand bleibt beim Gastimport getrennt.
- `bash scripts/smoke.sh`: vollständiger statischer und deterministischer Stack.
- `git diff --check`: Whitespace-/Patchprüfung.
