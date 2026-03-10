# Fahrplan – Durchlauf 196 (Legacy-Save-Beispiele SSOT-Markierung)

## Kontext

Der v7-Exportvertrag ist bereits auf einen schlanken HQ-Export gehärtet. In
`systems/gameflow/speicher-fortsetzung.md` standen jedoch zwei große Beispielblöcke
weiterhin als v7-JSON im Dokument, obwohl sie bewusst Legacy-/Bridge-Inhalte
(`location`, `phase`, `zr_version`, `character`) zeigen.

## Ziel

- Restdrift zwischen Legacy-Beispielen und kanonischem v7-Neu-Export
  beseitigen.
- Lesesicherheit erhöhen: Altstandsbeispiele klar als Migration markieren,
  damit keine falschen neuen Save-Shapes nachgebaut werden.
- Anschlussfähigkeit über Plan/Log/Prozessseiten sichern.

## Arbeitspakete

1. `systems/gameflow/speicher-fortsetzung.md`
   - Zwei Legacy-Abschnitte explizit als `Legacy-Bridge` benennen.
   - Legacy-JSON-Beispiele auf `"v": 6` kennzeichnen.
   - Klarhinweis ergänzen, dass `location`/`phase` dort reine
     Migrationsfelder sind und im kanonischen v7-Export ausgeschlossen
     bleiben.
2. Prozessspiegel fortschreiben:
   - `internal/qa/process/hard-final-review-next-steps.md`
   - `internal/qa/process/known-issues.md`
3. Pflichtcheck:
   - `bash scripts/smoke.sh`

## Abnahme

- Legacy-Beispiele sind eindeutig als Altstands-Bridge lesbar und kollidieren
  nicht mehr sprachlich mit dem v7-Kanon.
- Der kanonische v7-Abschnitt bleibt unverändert SSOT für Neu-Exporte.
- Smoke ist grün; Durchlauf 196 ist dokumentiert.
