---
title: "QA-Log Durchlauf 142 - Spielerhandbuch-Startpfad priorisieren + Watchguard"
version: 1.0.0
tags: [qa, log, onboarding, mmo]
---

# Kontext

Anschlusslauf zu ZR-021 (Onboarding-Hardening). Obwohl Startvertrag und
Entry-Layer bereits weitgehend harmonisiert sind, war das Mini-Einsatzhandbuch
im Spieler-Handbuch weiterhin in einer `klassisch|schnell`-Gleichstellung
formuliert. Ziel: Priorisierung im spielernahen Einstiegstext nachziehen und per
Watchguard absichern.

## Umgesetzte Änderungen

1. `core/spieler-handbuch.md`
   - Startpfad im Mini-Einsatzhandbuch neu strukturiert:
     - Standard (empfohlen): `Spiel starten (solo klassisch)` bzw. natürliche
       Sprache.
     - Primäre Erschaffungswahl: `generate` / `custom generate` / manuell.
     - `npc-team`/`gruppe` klassisch ebenfalls auf diese Priorität ausgerichtet.
     - `solo schnell` und `npc-team ... schnell` als optionale Fast-Lane
       ausgewiesen.
2. `tools/test_onboarding_start_save_watchguard.js`
   - Neue Assertions ergänzt:
     - `solo klassisch` muss im Spieler-Handbuch als `Standard (empfohlen)`
       verankert sein.
     - `solo schnell` muss als `Fast-Lane (optional)` markiert bleiben.
3. Prozessspur aktualisiert (`internal/qa/process/known-issues.md`) mit
   Durchlauf-142-Eintrag unter ZR-021.

## Verifikation

- Pflicht-Smoke erfolgreich.
- Link-Lint auf geänderten Doku-/QA-Dateien erfolgreich.

## Ergebnis

Der spieler-sichtige Startvertrag priorisiert jetzt konsistent den
kampagnenorientierten Pfad (`klassisch + generate/custom generate/manuell`),
während die Fast-Lane erhalten bleibt. Der neue Watchguard-Check stabilisiert
diese Priorisierung für Folge-Durchläufe.
