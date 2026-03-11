# Fahrplan – Durchlauf 202 (Legacy-Bridge Leseregel-Klarstellung)

## Kontext

Im Save-Modul existiert ein großer Legacy-Bridge-HQ-Beispielblock. Der Block
ist absichtlich als Import-/Migrationsreferenz markiert, trägt aber aus
Kompatibilitätsgründen weiterhin `v: 7`. Damit beim Überfliegen kein zweiter
kanonischer Exportpfad gelesen wird, braucht der Abschnitt eine noch klarere
Leseregel direkt am Beispiel.

## Ziel

- Lesesicherheit im Legacy-Bridge-Abschnitt erhöhen, ohne den bestehenden
  v7-Guard-Vertrag zu brechen.
- Eindeutig festhalten: `v: 7` im Legacy-Block ist kein Neu-Exportpfad,
  sondern Import-/Migrations-Bridge.
- Änderung in Fahrplan/QA-Log/Prozessspiegel dokumentieren.

## Arbeitspakete

1. Save-Doku präzisieren:
   - `systems/gameflow/speicher-fortsetzung.md` um explizite Leseregel am
     Legacy-Bridge-HQ-Beispiel ergänzen.
2. QA-Prozess spiegeln:
   - Neuen Log unter `internal/qa/logs/` anlegen.
   - `internal/qa/process/hard-final-review-next-steps.md` ergänzen.
   - `internal/qa/process/known-issues.md` (ZR-021) fortschreiben.
3. Pflichtchecks:
   - `bash scripts/smoke.sh`
   - `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`

## Abnahme

- Legacy-Bridge-Abschnitt enthält die explizite Leseregel (`v: 7` dort nur als
  Import-/Migrations-Bridge, nicht als Neu-Export).
- Pflicht-Smoke ist vollständig grün.
- Plan/Log/Prozessseiten bestehen den Link-Lint ohne Fehler.
