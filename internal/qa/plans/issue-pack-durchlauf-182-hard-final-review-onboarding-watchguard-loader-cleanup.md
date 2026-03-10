# Fahrplan – Durchlauf 182 (Hard-Final-Review Onboarding-Watchguard Loader-Cleanup)

## Kontext

Der Onboarding-Watchguard nutzte zwar bereits `createDocTextLoader(...)`, hielt
aber noch lokale Wrapper/Direktlese-Helfer vor. Das ist funktional korrekt,
erhöht jedoch unnötig die Wartungsfläche im Vergleich zum inzwischen etablierten
Loader-Standard ohne lokale Duplikate.

## Ziel

- Letzte lokale Direktlese-/Wrapper-Reste im Onboarding-Watchguard entfernen.
- Den zentralen Loader-Standard (`readText`, `getDocText`) konsistent und direkt
  nutzen.
- Prozess- und QA-Spur auf Durchlauf-182-Stand fortführen.

## Arbeitspakete

1. `tools/test_onboarding_start_save_watchguard.js` auf direkte Nutzung von
   `createDocTextLoader(...).{readText,getDocText}` umstellen.
2. Pflicht-Smoke ausführen (`bash scripts/smoke.sh`).
3. QA-Log für Durchlauf 182 dokumentieren.
4. Prozessübersichten (`known-issues.md` + Anschlussübersicht) synchron
   aktualisieren.

## Abnahme

- Keine lokale `fs.readFileSync`-Direktlese und keine lokalen Loader-Wrapper mehr
  im Onboarding-Watchguard.
- `bash scripts/smoke.sh` läuft vollständig grün.
- Plan/Log/Prozessseiten sind auf Durchlauf-182-Stand anschlussfähig.
