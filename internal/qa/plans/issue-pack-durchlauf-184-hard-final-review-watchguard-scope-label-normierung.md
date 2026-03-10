# Fahrplan – Durchlauf 184 (Hard-Final-Review Scope-Label-Normierung)

## Kontext

Der Meta-Guard erzwingt bereits die Nutzung von `createDocTextLoader(...)`,
Loader-API-Bindung und einen gesetzten `scopeLabel`. Für einheitliche
Diagnostik über alle Guard-Logs fehlt noch eine klare Benennungsnorm für den
`scopeLabel` selbst.

## Ziel

- `scopeLabel` nicht nur als vorhanden, sondern auch als normiert absichern.
- Einheitliche Fehlersuche in Smoke-/CI-Logs über konsistente Labelnamen.
- Prozess- und QA-Spur auf Durchlauf-184-Stand fortführen.

## Arbeitspakete

1. `tools/test_watchguard_loader_consistency.js` erweitern:
   - `scopeLabel` extrahieren,
   - Regel ergänzen: Label endet auf `Watchguard`,
   - Regel ergänzen: Label enthält keine Slash-Zeichen.
2. Pflicht-Smoke ausführen (`bash scripts/smoke.sh`).
3. QA-Log für Durchlauf 184 dokumentieren.
4. Prozessübersichten (`known-issues.md` + Anschlussübersicht) synchron
   aktualisieren.

## Abnahme

- Meta-Guard schlägt fehl, wenn `scopeLabel` nicht auf `Watchguard` endet.
- Meta-Guard schlägt fehl, wenn `scopeLabel` Slash-Zeichen enthält.
- `bash scripts/smoke.sh` läuft vollständig grün.
- Plan/Log/Prozessseiten sind auf Durchlauf-184-Stand anschlussfähig.
