---
title: "QA-Log 2026-03-10 – Durchlauf 140 (Entry-Layer-Watchguard + Archetypen-Slot-Default-Off)"
version: 1.0.0
date: 2026-03-10
status: abgeschlossen
tags: [qa, onboarding, startvertrag, slots]
---

# Kontext

Nach Durchlauf 139 war der Startvertrag in Runtime-SSOT und Referenzflächen konsistent. Für den nächsten Qualitätszug blieben drei operative Punkte:

1. Archetypen/Pregens im Default-Wissensspeicher endgültig demotieren.
2. Drift-Schutz vom Runtime-Kern auf den Entry-Layer ausdehnen (README/Setup-Guide/Setup-Script).
3. Anschlussarbeit prozessual als neuen Known-Issue-Track statt als lose Restnotizen führen.

# Umgesetzte Änderungen

## 1) Archetypen aus dem Default-Ladepfad entfernt

- Datei: `master-index.json`
- Änderung: Modul `chars-options` (`characters/charaktererschaffung-optionen.md`) von `slot:true` auf `slot:false` gesetzt.
- Wirkung: Archetypen/Pregens bleiben verfügbar, sind aber kein standardmäßig geladener Runtime-Slot mehr.

## 2) Onboarding-Watchguard auf Entry-Layer erweitert

- Datei: `tools/test_onboarding_start_save_watchguard.js`
- Ergänzungen:
  - harter Check, dass `chars-options.slot === false` bleibt,
  - neue Regelgruppe über `README.md`, `docs/setup-guide.md`, `scripts/setup-openwebui.sh` für:
    - `Spiel starten (solo klassisch)` als Default-Anker,
    - natürliche Sprache als gültiger Einstieg,
    - `solo schnell` nur als optionale Fast-Lane.

## 3) README/Setup-Guide auf neuen Default harmonisiert

- Dateien: `README.md`, `docs/setup-guide.md`
- Änderungen:
  - Wissensspeicher-Default auf **19 Module** (Spieler-Handbuch + 18 Runtime-Module) aktualisiert,
  - `characters/charaktererschaffung-optionen.md` explizit als optionales Inspirations-/Fallback-Material markiert.

## 4) Prozessspur fortgeführt

- Datei: `internal/qa/process/known-issues.md`
- Änderungen:
  - Durchlauf 140 in der ZR-020-Chronik ergänzt,
  - neuen Track `ZR-021` (`geplant`) für Post-139-Onboarding-Hardening angelegt.

# Verifikation

1. `bash scripts/smoke.sh` → erfolgreich (`All smoke checks passed`, inkl. Onboarding-Watchguard).
2. `python3 tools/lint_links.py README.md docs/setup-guide.md internal/qa/plans/issue-pack-durchlauf-140-entry-layer-watchguard-und-archetypen-slot-default-off.md internal/qa/logs/2026-03-10-issue-pack-durchlauf-140-entry-layer-watchguard-und-archetypen-slot-default-off.md internal/qa/process/known-issues.md` → keine Broken Links.

# Ergebnis

Die Archetypen-/Pregens-Demotion ist jetzt nicht nur textlich, sondern auch im Default-Slot-Verhalten vollzogen. Zusätzlich ist der Onboarding-Contract durch einen Smoke-Watchguard auf den Entry-Layer abgesichert, und die Folgearbeit läuft mit `ZR-021` auf sauberer Prozessspur weiter.
