# Fahrplan – Durchlauf 166 (Hard-Final-Review SSOT-Schema + Chronopolis-Runtime-Cleanup)

## Kontext

Aus dem Hard-Final-Review blieb ein fokussierter Restpunkt offen: letzte
Schema-Drift zwischen Masterprompt-v7 und Runtime-Dokumenten sowie ein
Chronopolis-Abschnitt mit zu viel Implementierungsballast im geladenen
Wissensspeicher.

## Ziel

- `systems/gameflow/speicher-fortsetzung.md` auf den v7-Exportpfad
  (`characters[]` als einziger Roster-Container) nachziehen.
- `core/sl-referenz.md` von Legacy-Formulierungen bereinigen, die Root-`character`
  oder `arc.timeline` als aktuelle Persistenzwahrheit erscheinen lassen.
- `gameplay/kampagnenstruktur.md` im Chronopolis-Abschnitt auf Runtime-Kanon
  verdichten und Dev-/API-/Pipeline-Ballast entfernen.
- Prozessspur (Known-Issues + Anschlussübersicht + QA-Log) für den nächsten
  Durchlauf anschlussfähig dokumentieren.

## Arbeitspakete

1. Schemaformulierungen in Save-Doku und SL-Referenz korrigieren.
2. Chronopolis-Abschnitt auf spielleitungsrelevante Leitplanken reduzieren.
3. Known-Issues/Anschlussübersicht auf Durchlauf-166-Stand synchronisieren.
4. Pflicht-Smoke ausführen und Ergebnis im QA-Log festhalten.

## Abnahme

- `bash scripts/smoke.sh` bleibt vollständig grün.
- Drei Zieldateien sind SSOT-konsistent (v7, Runtime-fokussiert,
  keine implementierungsnahen API-/RAM-/Cache-Pfade im Runtime-Text).
