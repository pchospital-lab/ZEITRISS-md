# QA-Log – Durchlauf 170 (Hard-Final-Review NPC-Watchguard Markdown-Resolver-Rollout)

## Ausgangslage

Der Resolver-Rollout war weitgehend abgeschlossen, aber
`test_npc_continuity_consistency.js` las die SSOT-Markdown-Dateien im
Slot-Durchlauf weiterhin direkt per Dateipfad. Damit blieb ein letzter
Fragilitätspunkt bei künftigen Markdown-Pfad-/Dateiumzügen.

## Umsetzung

- `tools/test_npc_continuity_consistency.js` erweitert:
  - `resolveUniqueMarkdownTarget` eingebunden.
  - Resolver-Helfer `readMarkdown()` ergänzt.
  - `markdownDocCache` + `getDocText()` eingeführt
    (Resolver + Caching für `.md`, Direktlese-Fallback für Nicht-Markdown).
- SSOT-Loop umgestellt:
  - Slot-/Pflichtanker-Prüfungen laufen jetzt über `getDocText()` statt über
    Direktzugriffe.

## Ergebnis

- Der NPC-Continuity-Watchguard nutzt in den SSOT-Markdown-Scans jetzt den
  gleichen Resolver-Standard wie die übrigen Hard-Final-Review-Guards.
- Pflicht-Smoke erfolgreich:
  - `bash scripts/smoke.sh` → „All smoke checks passed.“
