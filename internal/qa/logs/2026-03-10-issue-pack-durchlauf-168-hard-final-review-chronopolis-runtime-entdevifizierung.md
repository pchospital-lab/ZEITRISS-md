# QA-Log – Durchlauf 168 (Hard-Final-Review Chronopolis Runtime-Entdevifizierung)

## Ausgangslage

Im Chronopolis-Abschnitt war die grobe SSOT-Bereinigung abgeschlossen, aber ein
umfangreicher „Static Map Blueprint“-Block enthielt weiterhin technische
Vermessungs-, Spawn- und Kamerafahrt-Details. Das ist für Maintainer sinnvoll,
aber als Runtime-Wissensspeicher für die KI-SL unnötiger Dev-Kontext.

## Umsetzung

- `gameplay/kampagnenstruktur.md` bereinigt:
  - Abschnittstitel auf Runtime-Fokus umgestellt.
  - Restlicher Verweis auf Implementierungsdetails sprachlich neutralisiert.
  - Umfangreichen `Chronopolis Static Map Blueprint` (technische Geometrie,
    Spawnkoordinaten, Kamerafahrt) entfernt.
  - Ersatz durch kompaktes **Stadtbild-Pattern (Runtime)** mit Silhouette,
    Quadranten-Gefühl, Farb-/Soundmix und Regie-Fokus.
  - Maintainer-Blueprint explizit außerhalb des Runtime-Wissensspeichers auf
    `docs/dev/chronopolis-map-blueprint.md` verortet.

## Ergebnis

- Chronopolis-Runtime ist jetzt konsistent auf spielleitungsrelevante Inworld-
  Leitplanken reduziert; Dev-/Blueprint-Ballast liegt außerhalb des geladenen
  Wissensspeichers.
- Pflicht-Smoke erfolgreich:
  - `bash scripts/smoke.sh` → „All smoke checks passed.“
