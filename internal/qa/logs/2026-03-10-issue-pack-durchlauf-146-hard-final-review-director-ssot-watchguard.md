---
title: "QA-Log Durchlauf 146 - Hard-Final-Review Regie-SSOT-Watchguard"
version: 1.0.0
tags: [qa, log, runtime, ssot, watchguard]
---

# Kontext

Nach Durchlauf 145 war der Regie-Layer als Pflichtbeat bereits im Toolkit
verankert, aber noch nicht als paralleler SSOT-Anker im Masterprompt und der
SL-Referenz abgesichert. Ziel des Anschlusslaufs: denselben Kernsatz in allen
zentralen Steuerdokumenten führen und per Smoke-Test regressionsfest machen.

## Umgesetzte Änderungen

1. `meta/masterprompt_v6.md`
   - Regie-Layer als Pflichtbeat ergänzt:
     - genau ein personalisierter Relevanzsatz vor dem Briefing,
     - genau eine ITI-Bulletin-Mikronachricht nach Heimkehr.

2. `core/sl-referenz.md`
   - Pflicht-Heimkehr-Block um denselben Regie-Layer ergänzt
     (Relevanzsatz + ITI-Bulletin).

3. `systems/gameflow/cinematic-start.md`
   - Einstiegskapitel um einen klaren Runtime-Default-Hinweis ergänzt
     (`klassisch` + `generate/custom generate/manuell`) und
     Abschnittslabel auf kanonischen Produktpfad geschärft.

4. `tools/test_director_layer_watchguard.js`
   - Neuer Watchguard prüft die Pflichtanker in Masterprompt, Toolkit
     und SL-Referenz.

5. `scripts/smoke.sh`
   - Neuen Regie-Layer-Watchguard in den Pflicht-Smoke aufgenommen.

6. `internal/qa/process/known-issues.md`
   - ZR-021-Eintrag um den Anschlusslauf 146 ergänzt.

## Verifikation

- Pflicht-Smoke erfolgreich (`bash scripts/smoke.sh`).

## Ergebnis

Der Regie-Layer ist jetzt SSOT-parallel in den zentralen
Spielleitungsdokumenten verankert und durch den Smoke automatisiert
abgesichert. Damit bleibt der personalisierte Missionsübergang auch in
künftigen Textpflege-Runden stabil.
