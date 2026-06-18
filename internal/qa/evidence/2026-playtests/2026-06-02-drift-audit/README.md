# Drift-Audit 2026-06-02

Worker-Audit nach Mission-6-Playtest (Spielstand nach 8-PR-Pflichtgate-Marathon
#3180–#3191). Festgehaltene SOLL-Vision (`VISION-2026-06-02.md`) + Sweeps, die
prüfen wo das Spiel von Flos Spielgefühl-Intent abdriftet ("XCom-Loop, nicht
Pen&Paper-Wandertag").

**Status:** Befunde abgearbeitet (flossen in PRs #3192–#3200 ein, Abschluss-Audit
sagte "MERGE OK"). Diese Vision war die direkte Vorgeschichte zu den Run-Pool-
und Fraktions-Generator-PRs (#3205/#3206) vom 2026-06-04.

**Lag ursprünglich** untracked im Repo-Root `ZEITRISS-md-git/zeitriss-audit/` —
am 2026-06-04 hierher verschoben (gehört zu den Playtest-Run-Artefakten, nicht
ins Repo).

Offene übergreifende Empfehlung (KEIN Blocker): Masterprompt-Token-Druck. Aber:
Redundanz (Save/Würfeltemplates im Masterprompt) ist ABSICHT — Stochastik braucht
Wiederholung an Ort und Stelle. Echte Grenze = <200k Token in der 5er-Gruppe,
nicht "schlank um jeden Preis". Komprimieren erst wenn das Spiel rund läuft.
