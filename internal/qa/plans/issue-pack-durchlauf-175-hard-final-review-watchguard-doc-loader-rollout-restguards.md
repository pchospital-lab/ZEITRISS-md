# Fahrplan – Durchlauf 175 (Hard-Final-Review Watchguard-Doc-Loader-Rollout Restguards)

## Kontext

Nach den Rollouts 171–174 nutzten mehrere Hard-Final-Review-Watchguards noch
Direktaufrufe auf `resolveUniqueMarkdownTarget(...)` statt den gemeinsamen
Loader-Einstieg über `watchguard_doc_loader`.

## Ziel

- Restliche betroffene Watchguards auf `createDocTextLoader(...)` umstellen.
- Lokale Resolver-Aufrufe entfernen, ohne fachliche Assertions zu ändern.
- Regressionssicherheit per Pflicht-Smoke nachweisen und Prozessseiten auf
  Durchlauf-175-Stand synchronisieren.

## Arbeitspakete

1. `tools/test_chronopolis_gate_watchguard.js` auf Loader-`readMarkdown(...)`
   umstellen.
2. `tools/test_default_slot_dependency_watchguard.js` auf Loader-`readMarkdown(...)`
   umstellen.
3. `tools/test_hard_final_review_watchguard.js` auf Loader-`readMarkdown(...)`
   umstellen.
4. `tools/test_kausalabfang_watchguard.js`,
   `tools/test_physicality_watchguard.js`,
   `tools/test_ruf_alien_watchguard.js` und
   `tools/test_upload_snapshot_watchguard.js` auf Loader-`readMarkdown(...)`
   umstellen.
5. Pflicht-Smoke (`bash scripts/smoke.sh`) vollständig ausführen.
6. QA-Log + Prozessseiten (`known-issues.md`, Anschlussübersicht)
   auf den neuen Durchlauf synchronisieren.

## Abnahme

- `bash scripts/smoke.sh` vollständig grün.
- Alle genannten Rest-Guards nutzen den zentralen Loader-Standard,
  ohne lokale `resolveUniqueMarkdownTarget(...)`-Direktaufrufe.
