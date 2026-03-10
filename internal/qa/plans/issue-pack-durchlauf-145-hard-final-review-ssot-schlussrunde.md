---
title: "Issue-Pack Durchlauf 145 - Hard-Final-Review SSOT-Schlussrunde"
version: 1.0.0
tags: [qa, plan, runtime, ssot]
---

# Ziel

Die offenen Restpunkte aus `uploads/hard-final-review.md` in einem
qualitätsgesicherten Anschlusslauf schließen: Split-Kanon vereinheitlichen,
Default-Startpfad entkoppeln, Runtime-Ballast reduzieren und den kleinen
Director-Layer als Pflichtbeat verankern.

## Scope

- `systems/gameflow/speicher-fortsetzung.md`
- `characters/charaktererschaffung-grundlagen.md`
- `systems/gameflow/cinematic-start.md`
- `gameplay/kampagnenstruktur.md`
- `systems/toolkit-gpt-spielleiter.md`
- `internal/qa/process/known-issues.md`
- QA-Log für Durchlauf 145

## Checkliste

1. Split-/Merge-Canon im Speichermodul auf Core+Rift harmonisieren und den
   alten Rift-only-Standard entfernen.
2. Grundlagen der Charaktererschaffung so schärfen, dass der
   Default-Wissensspeicher ohne Pflichtabhängigkeit zu Modul 3B funktioniert.
3. Einstiegstexte in `cinematic-start.md` auf den Default-Produktpfad
   (natürlich/klassisch/generate) zuspitzen und alte Fraktionswahl-Formulierung
   aus dem Startkontext entfernen.
4. Kampagnenmodul sprachlich vom alten "Regel- und Inspirationsmodul"-Ton auf
   Runtime-Kanon umstellen (fester HQ-Kern statt HQ-Ausbau-Drift).
5. Toolkit um den Director-Layer ergänzen (ein Relevanzsatz vor Briefing,
   ein ITI-Bulletin im Heimkehr-Beat) und interne QA-Pfadreferenzen aus dem
   Laufzeittext entfernen.
6. Pflicht-Smoke ausführen (`bash scripts/smoke.sh`).
7. Geänderte Markdown-Dateien per Link-Lint prüfen.

## Abschlusskriterien

- Kein Widerspruch mehr zwischen Save-SSOT und Masterprompt beim Split-Kanon.
- Onboarding-/Charakterstart bleibt ohne optionales Modul vollständig spielbar.
- Runtime-Module enthalten weniger Dev-/QA-Ballast.
- Director-Layer ist in der SL-Referenz klar als Pflichtbeat formuliert.
- Pflicht-Smoke bleibt grün.
