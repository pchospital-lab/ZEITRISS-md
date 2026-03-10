# Fahrplan – Durchlauf 171 (Hard-Final-Review Watchguard-Doc-Loader-Standardisierung)

## Kontext

Die Resolver-Härtung ist funktional abgeschlossen, aber mehrere Watchguards
tragen weiterhin duplizierte Helferblöcke (`readText`/`readMarkdown`/Cache),
obwohl sie denselben Markdown-Resolver-Standard verwenden.

## Ziel

- Einen gemeinsamen Doc-Loader für Watchguards bereitstellen, damit
  Resolver-/Cache-Logik nicht pro Datei neu implementiert werden muss.
- Den neuen Loader in bereits resolver-basierten Guards produktiv nutzen,
  ohne fachliche Vertragsregeln zu verändern.
- Anschlussfähigkeit über Plan/Log/Prozessseiten für Folge-Durchläufe
  sicherstellen.

## Arbeitspakete

1. Gemeinsames Utility `tools/watchguard_doc_loader.js` ergänzen
   (`readText`, `readMarkdown`, `getDocText` mit Markdown-Cache).
2. `tools/test_iti_hardcanon_watchguard.js` und
   `tools/test_npc_continuity_consistency.js` auf das Utility umstellen.
3. Pflicht-Smoke (`bash scripts/smoke.sh`) vollständig ausführen.
4. Prozessseiten (`known-issues.md`, Anschlussübersicht) auf Durchlauf-171-Stand
   synchronisieren.

## Abnahme

- `bash scripts/smoke.sh` vollständig grün.
- Beide Guards nutzen das zentrale Loader-Utility statt lokaler
  Duplikat-Helfer.
