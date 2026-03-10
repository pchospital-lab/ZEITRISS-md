# Fahrplan – Durchlauf 170 (Hard-Final-Review NPC-Watchguard Markdown-Resolver-Rollout)

## Kontext

Die Resolver-Härtung wurde über mehrere Hard-Final-Review-Guards ausgerollt.
`test_npc_continuity_consistency.js` nutzte für SSOT-Slotprüfungen bislang noch
Direktlese-Zugriffe auf Markdown-Dateien, wodurch diese Stelle bei
Dateiumzügen weniger robust war als der übrige Guard-Stack.

## Ziel

- `test_npc_continuity_consistency.js` auf denselben Markdown-Resolver-Standard
  wie die übrigen Watchguards bringen.
- Slot-Prüfungen gegen stille Pfad-Drift absichern, ohne den fachlichen
  Vertragsinhalt zu verändern.
- Anschlussfähigkeit über Plan/Log/Prozessseiten für den nächsten Durchlauf
  sichern.

## Arbeitspakete

1. In `tools/test_npc_continuity_consistency.js` eine Resolver-basierte
   `getDocText()`-Logik mit Cache ergänzen.
2. SSOT-Dokumentprüfungen von Direktlesen auf `getDocText()` umstellen.
3. Pflicht-Smoke (`bash scripts/smoke.sh`) vollständig ausführen.
4. `known-issues.md` und Anschlussübersicht auf Durchlauf-170-Stand
   synchronisieren.

## Abnahme

- `bash scripts/smoke.sh` vollständig grün.
- NPC-Continuity-Watchguard liest Markdown-SSOT-Dateien resolver-basiert statt
  per Direktpfad.
