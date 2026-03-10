# QA-Log – Durchlauf 196 (Legacy-Save-Beispiele SSOT-Markierung)

## Ausgangslage

Der v7-Kanon (ohne Root-`location`/`phase`) war bereits gehärtet. In der
Save-Doku standen aber weiterhin zwei große Beispiele mit `"v": 7` und
Legacy-Feldern (`location`, `phase`, `zr_version`, `character`), was beim
Überfliegen wie ein zweiter v7-Exportstandard wirken konnte.

## Umsetzung

- `systems/gameflow/speicher-fortsetzung.md` bereinigt:
  - Abschnittstitel auf `Legacy-Bridge` umgestellt,
  - beide betroffenen Beispielblöcke von `"v": 7` auf `"v": 6` gesetzt,
  - expliziten Legacy-Feldhinweis ergänzt: `location`/`phase` dort nur für
    Migration, im kanonischen v7-Neu-Export ausgeschlossen.
- Prozessspiegel ergänzt:
  - `internal/qa/process/hard-final-review-next-steps.md`
  - `internal/qa/process/known-issues.md` (ZR-021-Nachtrag)

## Ergebnis

- Dokumentleseweg ist klarer: Bridge-Beispiele sind als Altstandsreferenz
  erkennbar und nicht mehr als konkurrierender v7-Export interpretierbar.
- v7 bleibt als einziges Neu-Exportformat semantisch stabil.

## Checks

- `bash scripts/smoke.sh` → `All smoke checks passed.`
- `rg -n "Legacy-Bridge|Legacy-Feldhinweis|\"v\": 6|Kanonisches Save-Exportformat" systems/gameflow/speicher-fortsetzung.md` → erwartete Treffer vorhanden.
