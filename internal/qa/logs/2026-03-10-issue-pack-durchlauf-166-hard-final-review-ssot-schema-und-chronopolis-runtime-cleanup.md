# QA-Log – Durchlauf 166 (Hard-Final-Review SSOT-Schema + Chronopolis-Runtime-Cleanup)

## Ausgangslage

Der Hard-Final-Review war weitgehend abgeschlossen, es blieben jedoch drei
qualitative Restdrifts:

1. Save-v7-Textstellen mit Legacy-Anschein (`character`/`timeline` als aktiver Exportpfad).
2. SL-Referenz mit Altformulierung zu `character.quarters` und `arc.timeline`.
3. Chronopolis-Runtime-Abschnitt mit Implementierungsballast (API-/Pipeline-
   Denke statt reinem Spielleitungsfokus).

## Umsetzung

- `systems/gameflow/speicher-fortsetzung.md`
  - v7-Pflichtfeldblock auf `characters[]` als kanonischen Roster-Container
    geschärft.
  - Root-`character` eindeutig als Legacy-Importpfad markiert.
  - Arc-Hinweis auf v7-Pfade (`arc.factions/questions/hooks` + `summaries.*`)
    umgestellt; `arc.timeline` als Exportwahrheit entfernt.
- `core/sl-referenz.md`
  - Save-v7-Abschnitt bereinigt: HQ-/Profilinfos über
    `characters[].quarters_stash`; Weltkontinuität über
    `arc.factions/questions/hooks` + `summaries.*`.
- `gameplay/kampagnenstruktur.md`
  - Chronopolis-Teil von Implementierungsblöcken entlastet (keine Stub-/API-
    Signature, keine RAM/Cache/Spawn-Mechanik im Runtime-Wissensspeicher).
  - Durch kompakte Runtime-Leitplanken + Regie-Output ersetzt.
- Prozessspur synchronisiert:
  - Neuer Fahrplan für Durchlauf 166 angelegt.
  - `known-issues.md` + `hard-final-review-next-steps.md` auf Durchlauf-166-
    Stand ergänzt.

## Ergebnis

- Pflicht-Smoke erfolgreich: `bash scripts/smoke.sh` meldet
  „All smoke checks passed.“
- Die letzte SSOT-Drift zwischen Masterprompt-v7 und Runtime-Dokumenten ist in
  den drei priorisierten Zieldateien sichtbar reduziert.
- Anschlussfähigkeit bleibt erhalten: Restaufgaben sind in der
  Anschlussübersicht fortgeschrieben.
