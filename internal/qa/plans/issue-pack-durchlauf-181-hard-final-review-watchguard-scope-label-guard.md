# Fahrplan – Durchlauf 181 (Hard-Final-Review Watchguard Scope-Label Guard)

## Kontext

Der zentrale Meta-Guard `tools/test_watchguard_loader_consistency.js` erzwingt
bereits Loader-Nutzung, aber noch nicht explizit den `scopeLabel` am
`createDocTextLoader(...)`. Dadurch bleiben Fehlermeldungen bei künftigen
Guard-Regressionen potenziell weniger eindeutig.

## Ziel

- Nachvollziehbarkeit von Loader-Fehlern in allen Watchguards vereinheitlichen.
- `scopeLabel` als verpflichtenden Standard für alle `test_*watchguard.js`
  automatisch absichern.
- Prozessdokumente auf Durchlauf-181-Stand synchron halten.

## Arbeitspakete

1. `tools/test_watchguard_loader_consistency.js` um eine Pflichtprüfung auf
   `scopeLabel` im `createDocTextLoader(...)` erweitern.
2. Pflicht-Smoke ausführen (`bash scripts/smoke.sh`).
3. QA-Log für Durchlauf 181 dokumentieren.
4. Prozessübersichten (`known-issues.md` + Anschlussübersicht) synchron
   aktualisieren.

## Abnahme

- Meta-Guard meldet nur dann Erfolg, wenn alle Watchguards einen
  `scopeLabel`-konfigurierten Loader nutzen.
- `bash scripts/smoke.sh` läuft vollständig grün.
- Plan/Log/Prozessseiten sind auf Durchlauf-181-Stand anschlussfähig.
