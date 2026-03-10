# Fahrplan – Durchlauf 173 (Hard-Final-Review Director-Watchguard Doc-Loader-Rollout)

## Kontext

Der zentrale `watchguard_doc_loader` wurde in den letzten Durchläufen bereits in
mehrere Hard-Final-Review-Guards ausgerollt. Der
`director-layer-watchguard` nutzte weiterhin eine eigene Resolver-Helferfunktion.

## Ziel

- `tools/test_director_layer_watchguard.js` auf den zentralen
  `watchguard_doc_loader` umstellen.
- Lokale Resolver-Duplikatlogik entfernen, ohne fachliche Guard-Regeln zu
  ändern.
- Regressionssicherheit per Pflicht-Smoke nachweisen und Prozessseiten auf
  Durchlauf-173-Stand synchronisieren.

## Arbeitspakete

1. `director-layer-watchguard` auf `createDocTextLoader({ root, scopeLabel })`
   umstellen und `readMarkdown(...)` aus dem Loader nutzen.
2. Lokale `resolveDocTarget(...)`-Duplikatlogik entfernen.
3. Pflicht-Smoke (`bash scripts/smoke.sh`) vollständig ausführen.
4. QA-Log + Prozessseiten (`known-issues.md`, Anschlussübersicht)
   auf den neuen Durchlauf synchronisieren.

## Abnahme

- `bash scripts/smoke.sh` vollständig grün.
- `director-layer-watchguard` nutzt den zentralen Loader-Standard,
  ohne eigene Resolver-Duplikate.
