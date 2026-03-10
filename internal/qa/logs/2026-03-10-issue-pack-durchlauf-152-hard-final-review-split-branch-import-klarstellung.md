---
title: "QA-Log – Durchlauf 152 (Split-/Branch-Import-Klarstellung)"
date: 2026-03-10
result: bestanden
owner: codex
---

# Kontext

Im Hard-Final-Review-Strang war nach den Durchläufen 145–151 noch ein
Restwiderspruch im Wording erkennbar: Der Abschnittstitel
"Nicht-kanonische Branches ohne Protokoll" stand direkt unter dem zuvor bereits
kanonisch definierten Core-Split-Standard. Das konnte als SSOT-Bruch gelesen
werden, obwohl der Fließtext Core-Parallelpfade korrekt als kanonisch führt.

# Umgesetzt

1. `systems/gameflow/speicher-fortsetzung.md`
   - Abschnittstitel auf **"Branch-Importe ohne Split-Protokoll"** umgestellt.
   - Einleitung sprachlich geschärft:
     - Core-Parallelpfade mit gleicher `continuity.split.family_id` sind
       kanonisch.
     - Gemischte Pfade ohne gemeinsames Split-Protokoll laufen als
       Branch-Import mit Präzedenzgraph.

2. Prozessspur
   - Plan ergänzt:
     `internal/qa/plans/issue-pack-durchlauf-152-hard-final-review-split-branch-import-klarstellung.md`
   - `internal/qa/process/known-issues.md` um Durchlauf 152 erweitert.

# Validierung

- Pflicht-Smoke erfolgreich:
  - `bash scripts/smoke.sh`

# Ergebnis

Der Split-/Merge-Kanon bleibt inhaltlich unverändert, ist aber sprachlich
widerspruchsfrei zwischen Abschnittstitel und Regeltext ausgerichtet. Damit ist
für Anschlussläufe klarer trennbar: kanonischer Core-Split vs.
Import-Fallback für gemischte Pfade ohne Split-Protokoll.
