# Fahrplan – Durchlauf 172 (Hard-Final-Review Onboarding-Watchguard Doc-Loader-Rollout)

## Kontext

Mit Durchlauf 171 wurde der zentrale Watchguard-Doc-Loader eingeführt und bereits
für zwei Guards ausgerollt. Der Onboarding-Start-Save-Watchguard nutzte jedoch
noch lokale Duplikat-Helfer für Markdown-Resolver, Cache und Dateilese.

## Ziel

- `tools/test_onboarding_start_save_watchguard.js` auf den zentralen
  `watchguard_doc_loader` umstellen.
- Lokale Duplikat-Helfer für resolver-basiertes Markdown-Lesen entfernen,
  ohne fachliche Vertragslogik zu ändern.
- Regressionssicherheit über den Pflicht-Smoke nachweisen und
  Prozessseiten auf Durchlauf-172-Stand synchronisieren.

## Arbeitspakete

1. Guard auf `createDocTextLoader({ root, scopeLabel })` umstellen und
   `getDocText` aus dem Loader verwenden.
2. Redundante lokale Markdown-Helfer im Guard entfernen.
3. Pflicht-Smoke (`bash scripts/smoke.sh`) vollständig ausführen.
4. QA-Log + Prozessseiten (`known-issues.md`, Anschlussübersicht)
   mit dem neuen Durchlauf synchronisieren.

## Abnahme

- `bash scripts/smoke.sh` vollständig grün.
- `onboarding-start-save-watchguard` nutzt den zentralen Loader,
  ohne eigene Resolver-/Cache-Duplikate.
