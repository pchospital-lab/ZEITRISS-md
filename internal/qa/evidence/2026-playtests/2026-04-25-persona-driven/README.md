# 2026-04-25 Persona-Driven-Playtest (Rohdaten, workspace-lokal)

**Status: Archiv · historisch · 13 Tage alt (Stand 2026-05-08).**

Gerettet aus dem lokalen git-Branch `playtests/persona-driven-v1`, bevor der Branch gelöscht wurde (Remote war bereits weg, PR vermutlich closed-ohne-Merge).

Die **Zusammenfassung** dieses Playtests (AUSWERTUNG.md, Opus-Critic-Bewertung) ist als SSOT im ZEITRISS-Repo gelandet unter `docs/qa/playtest-2026-04-25-persona-auswertung.md` — damit andere Agenten (die nur über GitHub zugreifen) den Status und die Befunde sehen können. Diese Rohdaten hier sind der private Backup-Stand für Rückblick-Fragen („War das schon immer so oder ist das neu?").

## Inhalt

- `A-kira/` — Solo, Tactician-Persona, 15 Turns (Wien 1913)
- `A-imre/` — Solo, Narrator-Persona, 10 Turns (Budapest 1956)
- `A-nox/` — Solo, Chaot-Persona, 10 Turns (Wien 1918)
- `B-group/` — Gruppe, 3 Spieler + Merge-Internals, 5 Turns (Wien 1938)
- `C-nox/` — Mini-Boss-Versuch, 3 Turns, abgebrochen
- `dryrun/` — Vor-Check
- `AUSWERTUNG.md` — identisch mit der Version im Repo (gespiegelt)

## Wichtig für Einordnung

Dieser Playtest wurde mit dem Masterprompt-Stand **vor** den folgenden Arbeiten gefahren:

- Buff-Schwellen-Halluzinations-Fix (PR #~3100)
- Datensatz-Trennung (docs/qa/datensatz-trennung-*)
- LP/HP-Invarianten-Durchsetzung in Templates
- Preserve/Trigger-Kernbotschaft-Klärung (PR #3167, 2026-05-07)
- Launcher-Lore-Setup (PR #3166)

Die Kritikpunkte aus der Auswertung (W10-Schwelle-Drift, LP/HP-Template-Bug, Mini-Boss-Prompt-Ignore) sind **zum größten Teil seit dem 25.04. abgearbeitet**. Dieser Playtest ist also **nicht mehr repräsentativ für den aktuellen Spielzustand**. Neue Playtests im aktuellen Masterprompt-Stand laufen ab Mai 2026 mit Flo selbst.
