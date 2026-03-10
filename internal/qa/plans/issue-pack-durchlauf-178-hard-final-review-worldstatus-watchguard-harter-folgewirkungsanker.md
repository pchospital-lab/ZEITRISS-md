# Fahrplan – Durchlauf 178 (Hard-Final-Review Weltstatus-Watchguard Folgewirkungsanker)

## Kontext

Der Director-Layer-Watchguard prüfte bereits die Pflichtbeats
(Relevanzsatz/ITI-Bulletin/Weltstatus) in den Kernreferenzen. Die
Weltstatus-Rückkopplung sollte zusätzlich auf den Runtime-Kampagnenkanon
abgedeckt und explizit auf den Folgewirkungsanker gehärtet werden, damit
Drift in Form abgeschwächter Formulierungen sofort im Smoke auffällt.

## Ziel

- Weltstatus-Pflichtsatz regressionssicher auf alle Runtime-SSOT-Referenzen
  erweitern (inkl. `gameplay/kampagnenstruktur.md`).
- Für die Weltstatus-Prüfung den Zusatzanker „konkrete Folgewirkung“ als
  verpflichtenden Patternbestandteil erzwingen.
- QA-/Prozessspur auf Durchlauf-178-Stand fortschreiben.

## Arbeitspakete

1. `tools/test_director_layer_watchguard.js` erweitern:
   - separate Dokumentliste für Weltstatus-Checks,
   - Einbezug von `gameplay/kampagnenstruktur.md`,
   - Folgewirkungsanker (`Folge`/`Folgewirkung`) als Pflichtmuster.
2. Pflicht-Smoke ausführen (`bash scripts/smoke.sh`).
3. QA-Log für Durchlauf 178 ergänzen.
4. `known-issues.md` und `hard-final-review-next-steps.md` synchronisieren.

## Abnahme

- `node tools/test_director_layer_watchguard.js` meldet
  `director-layer-watchguard-ok`.
- `bash scripts/smoke.sh` vollständig grün.
- Prozessübersichten dokumentieren Durchlauf 178 mit dem neuen
  Folgewirkungs-Regressionanker.
