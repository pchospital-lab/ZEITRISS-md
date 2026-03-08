---
title: "Issue-Pack Durchlauf 79 – Round4 Anschluss: SSOT-Feldnamen Restdrift"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-08"
links:
  issue: "internal/qa/process/known-issues.md#zr-018-ruftier-progress-und-alienmystery-onboarding-als-ssot-nachziehen"
  statusmatrix: "internal/qa/process/ruf-alien-statusmatrix.md"
---

# Ziel

Kleiner Anschlusslauf, um verbleibende Feldnamen-Restdrifts in Runtime-Beispielen
auf den kanonischen v7-Pfad zu ziehen und damit die SSOT-Leseführung weiter zu
härten.

1. Nicht-kanonische Kurzform `open_seeds` in Runtime-Checklisten auf
   `campaign.rift_seeds` harmonisieren.
2. Toolkit-Pseudocode für Gruppenreset auf kanonische Seed-Felder umstellen
   (`campaign.rift_seeds` + Legacy-Spiegel `arc.open_seeds`).
3. Pflicht-Smoke und Linklint ausführen.
4. Prozessanker/Statusmatrix um Durchlauf 79 ergänzen.

# Checkliste

- [x] Feldnamen in Runtime-Beispielen auf `campaign.rift_seeds` harmonisiert.
- [x] Toolkit-Pseudocode beim Gruppenreset auf kanonische Seed-Felder gezogen.
- [x] Pflicht-Smoke ausgeführt.
- [x] Linklint ausgeführt.
- [x] Prozessanker aktualisiert.

# Abschluss

Der Lauf enthält keine Regeländerung, sondern reine SSOT-Konsolidierung bei
Feldnamen. Damit sinkt das Risiko, dass Pseudocode-/Dev-Checklisten als
abweichende Runtime-Quelle interpretiert werden.
