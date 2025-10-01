---
title: "Tester-Playtest-Briefing"
version: 1.0.0
tags: [meta]
---

# Tester-Playtest-Briefing

Dieser Leitfaden bündelt den standardisierten Playtest-Auftrag für ZEITRISS.
Nach dem Setup wird der Auftrag in den Chat kopiert, damit alle Plattformen
identische QA-Durchläufe liefern.

## Wissensspeicher vorbereiten

Vor dem Testlauf werden identische Datenquellen in jeder Plattform geladen:

- `meta/masterprompt_v6.md`
- `README.md`
- `master-index.json`
- Alle 18 Runtime-Module aus `core/`, `gameplay/`, `characters/` und `systems/`
  (ohne `systems/runtime-stub-routing-layer.md`).

Optional kann der Masterprompt zusätzlich im Wissensspeicher gesichert werden.

## Copy-&-Paste-Auftrag für den GPT

> (OOC: Spieleentwickler) Bitte lies den kompletten ZEITRISS-Datensatz aufmerksam
> und führe Solo-Missionen als Chrononaut durch. Simuliere Durchläufe in
> Frühphase, Midgame und Endgame, inklusive HQ-Briefing, Mission,
> Paradoxon-Index-Handling und Kodex-HUD. Prüfe Save/Load mit dem aktuellen
> `saveGame`-Schema (inkl. `zr_version`, `Charakter`-Blöcken, `Kodex`-Einträgen
> und optionalem `arc_dashboard`), kontrolliere HQ-Briefing-Schleifen,
> Accessibility-Dialoge, Offline-Hinweise sowie Ask→Suggest- und Kodex-Kommandos.
> Dokumentiere jede Unstimmigkeit, Balance-Frage oder Regelunklarheit. Liefere
> anschließend eine nummerierte Analyse mit Problem, möglicher Lösung für Codex
> (Programmier-KI) und Hinweisen aus Sicht von Spieler:innen sowie Spielleitung.

## Ablauf für Tester:innen

1. Masterprompt (`meta/masterprompt_v6.md`), `README.md`, `master-index.json`
   und alle Runtime-Module (ohne `systems/runtime-stub-routing-layer.md`) wie im
   Quickstart beschrieben laden. Optional Masterprompt zusätzlich in den
   Wissensspeicher übernehmen. Verifiziere, dass der GPT den Begriff **Kodex**
   korrekt nutzt und keine Legacy-Nennungen wie „Codex“ oder veraltete
   Save-Felder (`zr_version < 4.x`) ausgibt.
2. Den Auftrag oben senden und mindestens eine komplette Quest-Schleife je
   Progressionsphase (Frühphase, Midgame, Endgame) durchspielen. Der Durchlauf
   endet erst nach demonstriertem HQ-Loop, Mission, Save/Load und
   Paradoxon-Index-Anpassungen.
3. Manueller Save/Load-Test: `saveGame({...})` anfordern, lokal sichern, neuen
   Chat starten und den Reimport prüfen. Der GPT muss `zr_version`,
   Kodex-Archivdaten und alle Charakterwerte sauber rekonstruieren.
4. Zusätzlich dokumentieren, wie der GPT HUD-Presets, Sofa-Modus,
   Offline-Optionen, Paradoxon-Index-Hinweise und Ask→Suggest-Toggle erklärt.
   Notiere, ob Gear-Aliasse (z. B. Multi-Tool-Handschuh) und `Spiel starten`-
   Varianten laut Acceptance-Smoke funktionieren.
5. Analyse unverändert in den Report kopieren. Ergänzend können Plattform,
   Datum oder besondere Beobachtungen als Randnotizen ergänzt werden.
6. Report an die Maintainer:innen übergeben; daraus entsteht entweder eine neue
   QA-Notiz oder ein Update für bestehende Audits. Ergebnis wird in Codex
   übertragen, damit Aufgaben strukturiert abgearbeitet werden können.

## Template für den Report an die Maintainer:innen

```text
# Playtest-Report ZEITRISS
- Version: (z. B. 4.2.2 beta)
- Testplattform: (OpenAI / Proton LUMO / Ollama)
- Datum & Uhrzeit: (lokal)
- Tester:in: (Alias)

## GPT-Analyse
(Paste aus der GPT-Antwort)

## Save/Load-Beleg
saveGame({...})

## Eigene Anmerkungen
- (Optionale Ergänzung)
- (Weitere Beobachtungen)
```

## Hinweise zur Weiterverarbeitung

- Maintainer:innen übertragen die nummerierte Liste aus der GPT-Antwort in eine
  QA-Notiz (z. B. als Ergänzung zu `docs/ZEITRISS-qa-audit-2025.md` oder einen
  neuen Eintrag unter `docs/`). Der Save/Load-Block dient als Nachweis für den
  Kodex- und Charakterstand.
- Reports werden lokal oder in einer gesicherten Team-Ablage archiviert, damit
  der Ablauf offline nachvollziehbar bleibt.
- Weitere Durchläufe mit alternativen Solo-Builds oder Gruppen-Saves nutzen
  denselben Auftrag. Die Ansprache, Kodex-Hinweise und Offline-Optionen bleiben
  dadurch konsistent. Plattformen laufen online ohne Web-Tool; LUMO bietet
  Verschlüsselung, die lokale Instanz bleibt komplett offline.
