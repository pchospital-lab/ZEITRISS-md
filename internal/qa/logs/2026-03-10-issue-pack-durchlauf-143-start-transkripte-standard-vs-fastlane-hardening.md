---
title: "QA-Log Durchlauf 143 - Start-Transkripte Standard-vs-Fast-Lane-Hardening"
version: 1.0.0
tags: [qa, log, onboarding, mmo]
---

# Kontext

Anschlusslauf zu ZR-021. Nach der Harmonisierung des Startvertrags lag ein
sichtbarer Restdrift in den Beispiel-Transkripten des Spieler-Handbuchs:
Schnelleinstieg war präsent, aber der klassische Kampagnenstart als Primärpfad
wurde dort nicht gleich stark vorangestellt.

## Umgesetzte Änderungen

1. `core/spieler-handbuch.md`
   - Im Abschnitt `Start-Transkripte (Kurz)` einen neuen
     **Solo-Kampagnenstart (Standard: klassisch + generate)** ergänzt.
   - Bestehenden Solo-Schnelleinstieg explizit als
     **Fast-Lane (optional)** markiert.
   - Gruppen-Schnelleinstieg ebenfalls im Titel als Fast-Lane (optional)
     gekennzeichnet.
2. `tools/test_onboarding_start_save_watchguard.js`
   - Neue Assertions ergänzt:
     - Spieler-Handbuch muss den klassischen Kampagnenstart-Transcript als
       Standardanker ausweisen.
     - Solo-Schnelleinstieg muss explizit als optionale Fast-Lane markiert
       bleiben.
3. Prozessspur aktualisiert (`internal/qa/process/known-issues.md`) mit
   Durchlauf-143-Eintrag unter ZR-021.

## Verifikation

- Pflicht-Smoke erfolgreich.
- Link-Lint auf geänderten Doku-/QA-Dateien erfolgreich.

## Ergebnis

Die spieler-sichtigen Beispieltranskripte sind jetzt konsistent mit dem
Onboarding-Contract: klassischer Kampagnenstart mit `generate` steht vorne,
Schnellstart bleibt verfügbar, aber klar als optionaler Fast-Lane-Pfad.
