# Fahrplan – Durchlauf 185 (Hard-Final-Review Scope-Label-Dateiname-Kohärenz)

## Kontext

Der Meta-Guard erzwingt bereits Loader-Standard, API-Bindung und
`scopeLabel`-Format. Eine verbleibende Driftlücke: ein formal gültiges Label
konnte semantisch vom Guard-Dateinamen abweichen und dadurch Diagnosepfade
unnötig unscharf machen.

## Ziel

- `scopeLabel` zusätzlich semantisch an den jeweiligen Guard-Dateinamen
  koppeln.
- Uneinheitliche Labelbezeichnungen frühzeitig im Meta-Guard blockieren.
- QA-/Prozessspur auf Durchlauf-185-Stand fortführen.

## Arbeitspakete

1. `tools/test_watchguard_loader_consistency.js` erweitern:
   - Normalisierung von Dateiname/Label auf vergleichbare Tokens,
   - neue Pflichtregel: `scopeLabel`-Token muss zum Dateinamen-Token passen.
2. Betroffene Guard-Datei nachziehen (falls Guard anschlägt).
3. Pflicht-Smoke ausführen (`bash scripts/smoke.sh`).
4. QA-Log + Prozessseiten (`known-issues.md`, Anschlussübersicht)
   synchronisieren.

## Abnahme

- Meta-Guard meldet bei Label-Dateiname-Drift einen klaren Verstoß.
- Betroffene Guards sind auf konsistente Labels angehoben.
- `bash scripts/smoke.sh` läuft vollständig grün.
- Plan/Log/Prozessseiten sind für Folge-Durchläufe anschlussfähig.
