# QA-Log – Durchlauf 169 (Hard-Final-Review ITI-Watchguard Markdown-Resolver-Rollout)

## Ausgangslage

Der `iti-hardcanon-watchguard` war inhaltlich stabil, nutzte aber in Teilen noch
Direktzugriffe auf Markdown-Dateien. Damit war die Robustheit gegen
Pfad-/Dateiumzüge geringer als bei den bereits auf
`resolveUniqueMarkdownTarget` gehärteten Guards.

## Umsetzung

- `tools/test_iti_hardcanon_watchguard.js` erweitert:
  - `readMarkdown()` als Resolver-Helfer ergänzt.
  - `markdownDocCache` + `getDocText()` eingeführt (einheitliches Lesen mit
    Resolver + Caching für `.md`, Fallback auf Direktlesen für Nicht-Markdown).
- Slot-basierte Textprüfungen umgestellt:
  - Verbotene Driftbegriffe im Slot-Loop laufen jetzt über `getDocText()`.
  - Legacy-Alias-Check im Slot-Loop läuft jetzt ebenfalls über `getDocText()`.

## Ergebnis

- Resolver-Rollout ist für den ITI-Watchguard jetzt auch in den
  Slot-Scans konsistent umgesetzt.
- Pflicht-Smoke erfolgreich:
  - `bash scripts/smoke.sh` → „All smoke checks passed.“
