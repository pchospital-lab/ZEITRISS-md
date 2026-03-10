---
title: "Hard-Final-Review – Durchlaufhistorie 157–179"
date: 2026-03-10
status: archiv
owner: codex
scope: Runtime/QA + Meta/Prozess
---

# Zweck

Archivierte Detailhistorie der Anschlussdurchläufe 157–179 nach dem Hard-Final-
Review. Die operative Kurzfassung bleibt in
`internal/qa/process/hard-final-review-next-steps.md`.

## Durchlaufhistorie 157–179

- Durchlauf 157: Historie 73–156 aus `known-issues.md` archiviert.
- Durchlauf 158: `known-issues.md` auf kompakte Triage-Notizen reduziert;
  Detailstände liegen in den jeweiligen Statusmatrizen/Archivdateien.
- Durchlauf 159: `chronopolis-gate-watchguard` auf robuste
  Zielpfad-Ermittlung gehärtet (weniger manuelle Pflege bei Makro-Umzügen).
- Durchlauf 160: gemeinsame Resolver-Utility für robuste
  Watchguard-Zielpfadauflösung in `tools/` eingeführt und im
  `chronopolis-gate-watchguard` produktiv genutzt.
- Durchlauf 161: Resolver-Rollout auf
  `default-slot-dependency-watchguard` und
  `hard-final-review-watchguard` erweitert.
- Durchlauf 162: Resolver-Rollout auf
  `director-layer-watchguard`,
  `onboarding-start-save-watchguard` und
  `iti-hardcanon-watchguard` erweitert.
- Durchlauf 163: Upload-Kontext (`uploads/hard-final-review.md`) per
  Pflicht-Watchguard abgesichert (`upload-snapshot-watchguard-ok`).
- Durchlauf 164: Resolver-Rollout auf
  `ruf-alien-watchguard`,
  `physicality-watchguard` und
  `kausalabfang-watchguard` erweitert.
- Durchlauf 165: Prozess-Kompaktheit per neuem Pflicht-Guard
  `process-compactness-watchguard-ok` automatisiert
  (known-issues/Anschlussübersicht bleiben smoke-validiert schlank).
- Durchlauf 166: SSOT-Restdrift in Save-/SL-Referenz bereinigt (`characters[]`
  als einziger v7-Roster-Exportpfad, keine `arc.timeline`-Persistenzwahrheit)
  und Chronopolis-Runtime-Abschnitt von Implementierungsballast auf
  Leitplanken reduziert.
- Durchlauf 167: Arc-Makrokontinuität als Pflicht-Regiebeat ergänzt
  (genau eine Weltstatus-Zeile pro Missionszyklus aus
  `arc.factions/questions/hooks`) und per `director-layer-watchguard`
  regressionssicher im Smoke verankert.
- Durchlauf 168: Chronopolis-Runtime weiter entdevifiziert
  (Static-Blueprint/Spawn-/Kamerafahrt-Ballast aus dem geladenen
  Wissensspeicher entfernt, ersetzt durch kompaktes Stadtbild-Pattern +
  Maintainer-Verweis).
- Durchlauf 169: `iti-hardcanon-watchguard` im Slot-Scan auf
  resolver-basierte Markdown-Zielauflösung gehärtet (weniger Drift bei
  Markdown-Pfad-/Dateiumzügen).
- Durchlauf 170: `npc-continuity-consistency` im SSOT-Slot-Scan auf
  resolver-basierte Markdown-Zielauflösung gehärtet (schließt den letzten
  Direktlese-Rest in diesem Guard).
- Durchlauf 171: gemeinsames Watchguard-Loader-Utility
  (`watchguard_doc_loader`) eingeführt und im `iti-hardcanon-watchguard`
  sowie `npc-continuity-consistency` produktiv ausgerollt
  (Resolver-/Cache-Standard ohne Helferduplikate).
- Durchlauf 172: `onboarding-start-save-watchguard` auf den zentralen
  `watchguard_doc_loader` umgestellt (weiterer Abbau lokaler
  Resolver-/Cache-Duplikate).
- Durchlauf 173: `director-layer-watchguard` auf den zentralen
  `watchguard_doc_loader` umgestellt (Resolver-Duplikatlogik entfernt,
  fachliche Regie-Checks unverändert).
- Durchlauf 174: `process-compactness-watchguard` auf den zentralen
  `watchguard_doc_loader` umgestellt (Resolver-Einstieg vereinheitlicht,
  fachliche Kompaktheits-Checks unverändert).
- Durchlauf 175: verbleibende Hard-Final-Review-Restguards
  (`chronopolis-gate`, `default-slot-dependency`, `hard-final-review`,
  `kausalabfang`, `physicality`, `ruf-alien`, `upload-snapshot`) auf den
  zentralen `watchguard_doc_loader` umgestellt (fachliche Assertions
  unverändert, Resolver-Duplikatlogik entfernt).
- Durchlauf 176: `iti-hardcanon-watchguard` vollständig auf den zentralen
  `watchguard_doc_loader` konsolidiert (lokaler Resolver-Resthelfer entfernt;
  fachliche Assertions unverändert).
- Durchlauf 177: neuer Meta-Guard
  `watchguard-loader-consistency-watchguard-ok` ergänzt und im Pflicht-Smoke
  verankert; erzwingt für alle `test_*watchguard.js` den zentralen
  Loader-Standard (kein direkter `watchguard_file_resolver`-/
  `resolveUniqueMarkdownTarget`-Zugriff, keine direkte `.md`-Direktlese per
  `readFileSync`).
- Durchlauf 178: `director-layer-watchguard` für den Weltstatus-Pflichtsatz
  gehärtet (zusätzlicher Check auf `gameplay/kampagnenstruktur.md` sowie
  verpflichtender Folgewirkungsanker für die Weltstatus-Zeile aus
  `arc.factions/questions/hooks`).
- Durchlauf 179: `watchguard-loader-consistency` gehärtet
  (multiline-sichere Erkennung direkter `.md`-Direktlese via `readFileSync`
  und Pflicht zur realen Loader-API-Nutzung über `readMarkdown` oder
  `getDocText`).
