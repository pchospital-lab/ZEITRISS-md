# Fahrplan – Durchlauf 174 (Hard-Final-Review Process-Compactness-Watchguard Doc-Loader-Rollout)

## Kontext

Der zentrale `watchguard_doc_loader` ist bereits in mehreren Hard-Final-Review-
Guards im Einsatz. Der `process-compactness-watchguard` nutzte noch direkte
Resolver-Aufrufe statt des einheitlichen Loader-Einstiegs.

## Ziel

- `tools/test_process_compactness_watchguard.js` auf den zentralen
  `watchguard_doc_loader` umstellen.
- Lokale Resolver-Aufrufe entfernen, ohne fachliche Guard-Regeln zu ändern.
- Regressionssicherheit per Pflicht-Smoke nachweisen und Prozessseiten auf
  Durchlauf-174-Stand synchronisieren.

## Arbeitspakete

1. `process-compactness-watchguard` auf
   `createDocTextLoader({ root, scopeLabel })` umstellen und
   `readMarkdown(...)` aus dem Loader nutzen.
2. Direkte `resolveUniqueMarkdownTarget(...)`-Nutzung im Guard entfernen.
3. Pflicht-Smoke (`bash scripts/smoke.sh`) vollständig ausführen.
4. QA-Log + Prozessseiten (`known-issues.md`, Anschlussübersicht)
   auf den neuen Durchlauf synchronisieren.

## Abnahme

- `bash scripts/smoke.sh` vollständig grün.
- `process-compactness-watchguard` nutzt den zentralen Loader-Standard,
  ohne lokale Resolver-Aufrufe.
