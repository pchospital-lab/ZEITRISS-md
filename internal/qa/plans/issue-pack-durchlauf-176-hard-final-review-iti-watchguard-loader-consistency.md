# Fahrplan – Durchlauf 176 (Hard-Final-Review ITI-Watchguard Loader-Consistency)

## Kontext

Nach dem Rollout 171–175 nutzte der `iti-hardcanon-watchguard` bereits den
zentralen `watchguard_doc_loader`, enthielt aber noch einen lokalen
Resolver-Einstieg für Teile der SSOT-Scans.

## Ziel

- Den `iti-hardcanon-watchguard` vollständig auf den zentralen Loader-Einstieg
  (`readMarkdown`/`getDocText`) konsolidieren.
- Lokale Resolver-Duplikatlogik entfernen, ohne fachliche Assertions zu ändern.
- Regressionssicherheit per Pflicht-Smoke nachweisen und Prozessseiten auf
  Durchlauf-176-Stand synchronisieren.

## Arbeitspakete

1. `tools/test_iti_hardcanon_watchguard.js` auf konsistenten Loader-Einstieg
   (`readMarkdown`) umstellen.
2. Lokale Resolver-Helfer und ungenutzte Resolver-Imports aus dem Guard
   entfernen.
3. Pflicht-Smoke (`bash scripts/smoke.sh`) vollständig ausführen.
4. QA-Log + Prozessseiten (`known-issues.md`, Anschlussübersicht)
   auf den neuen Durchlauf synchronisieren.

## Abnahme

- `bash scripts/smoke.sh` vollständig grün.
- `tools/test_iti_hardcanon_watchguard.js` nutzt für Markdown-Zielauflösung
  keinen lokalen Resolver-Helfer mehr.
