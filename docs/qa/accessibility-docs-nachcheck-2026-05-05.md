# QA-Nachtrag: Zugänglichkeit & Setup-Kommunikation (2026-05-05)

## Kontext

Dokumentations-Nachschärfung nach Nutzerfeedback zur zu hohen Einstiegshürde.
Ziel war eine klare Trennung zwischen:

1. **Standard-Setup (getestet, empfohlen)**
2. **Portabler Export (theoretisch nutzbar, ohne Gewähr)**

## Geänderte Dokumente

- `README.md`
- `docs/setup-guide.md`

## Prüfpunkte

- README kommuniziert zwei Wege explizit und priorisiert OpenWebUI als Referenzplattform.
- Nicht belastbare Aussagen zu Lumo/Proton wurden entfernt bzw. auf „nicht empfohlen“ gesetzt.
- Setup-Guide behandelt alternative Plattformen nur noch als portablen Exportpfad ohne Support-Zusage.
- Referenz-/Command-Abschnitte sind konsistent zur neuen Positionierung.

## Verifikation

- `bash scripts/smoke.sh` → OK
