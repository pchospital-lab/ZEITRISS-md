---
title: "Maintainer-Ops"
version: 1.0.0
tags: [meta]
---

# Maintainer-Ops

Dieses Dossier hält euren Ablauf straff. Ihr sorgt dafür, dass alle Plattformen denselben Stand führen, QA-Protokolle lückenlos
bleiben und Releases ohne Drift live gehen. Der Wissensspeicher umfasst genau den Masterprompt, `README.md`, `master-index.json`
und 18 Runtime-Module; der Stub `systems/runtime-stub-routing-layer.md` bleibt ausschließlich für Dev-Zwecke lokal.

## Plattform-Workflows

### OpenAI MyGPT & GPT-Store
1. Legt einen Custom GPT **ZEITRISS [ver. 4.2.2]** an und kopiert `meta/masterprompt_v6.md` in das Masterprompt-Feld.
2. Ladet `README.md`, `master-index.json` und alle 18 Runtime-Module aus `core/`, `characters/`, `gameplay/` sowie `systems/`
   (ohne `systems/runtime-stub-routing-layer.md`) in den Wissensspeicher. Prüft, ob Titel und Version der YAML-Header sichtbar
   sind.
3. Klont den GPT direkt als **Beta**. Spieltests, Webtool-Prüfungen und Feature-Checks laufen ausschließlich dort, bis ihr QA
   freigebt.
4. Dokumentiert jede Session in `internal/qa/`. Vermerkt Datum, Plattform, Autoload-Pfade (`Spiel starten ...`), Save/Load-IDs
   und besondere Antworten.

### Proton LUMO
1. Öffnet einen verschlüsselten LUMO-Chat, ladet `README.md`, `master-index.json`, alle Module (ohne den Runtime-Stub) und
   `meta/masterprompt_v6.md` per Upload.
2. Sendet den Masterprompt zusätzlich als Chatnachricht, damit der Verlauf bei Rejoins vollständig bleibt.
3. Notiert im QA-Log, welche LUMO-Funktionen aktiv waren (Dateiupload, gespeicherte Nachrichten, Replay, Link-Vorschau).
4. Verifiziert, dass Tabellen, JSON-Blöcke und Makros unverändert angezeigt werden. Bei Formatverlust erneuter Upload.

### Ollama + OpenWebUI
1. Installiert das gewünschte Modell in Ollama und verbindet OpenWebUI mit `http://localhost`.
2. Importiert `meta/masterprompt_v6.md`, `README.md`, `master-index.json` und sämtliche Module außer dem Runtime-Stub manuell.
   Nutzt dafür entweder den Dokumenten-Upload oder fügt Inhalte direkt in die Wissensbibliothek.
3. Spielt den Acceptance-Smoke-Test offline durch. Webtools bleiben deaktiviert, bis eine geprüfte Integration zur Verfügung
   steht.
4. Haltet lokale Anpassungen im QA-Log fest. Spiegelt Änderungen zurück nach MyGPT und LUMO, sobald ihr sie verifiziert habt.

## QA-Loop & Save/Load
- Plant drei komplette Durchläufe im MyGPT-Beta, einen in LUMO und einen lokal. Jede Session endet mit einem Save/Load-Test.
- Speichert die `saveGame({...})`-Blöcke in sicheren Notizen. Beim Reimport postet ihr den JSON-Block unverändert in den Chat.
- Checkt Accessibility-Dialoge (HUD-Erklärungen, Sofa-Modus, Offline-Hinweise) und notiert Auffälligkeiten im QA-Log.
- Nutzt [docs/acceptance-smoke.md](docs/acceptance-smoke.md) als Checkliste, ergänzt aber Plattform-spezifische Beobachtungen.

## Release-Checkliste
- Versionierung folgt **MAJOR.MINOR.PATCH**. Aktualisiert `CHANGELOG.md`, `README.md` und `master-index.json` synchron.
- Prüft rechtliche Hinweise (`docs/trademark.md`, `LICENSE`) sowie Marken- und DPMA-Hinweise im README.
- Führt `make lint`, `make test` und `scripts/smoke.sh` aus. Ergebnisse wandern in den QA-Eintrag der jeweiligen Plattform.
- Gebt die Store- oder Listing-Updates erst frei, wenn alle Plattformen auf denselben Stand synchronisiert sind.
- Kontrolliert vor Freigabe, dass genau 18 Runtime-Module plus `master-index.json` auf jeder Plattform liegen – ohne den
  Runtime-Stub.

## Systemgrenzen
- Die KI-Spielleitung kann keine Dateien schreiben, Repos ändern oder externe APIs aufrufen. Alle Speicherstände entstehen durch
  Copy & Paste.
- Save-Funktionen sind auf das HQ beschränkt. Missionen lassen sich abbrechen, aber nicht zwischenspeichern.
- Webtools stehen nur im MyGPT-Beta zur Verfügung. LUMO arbeitet offline, Ollama bleibt lokal und verzichtet auf Webzugriffe.
- Achtet auf DSGVO-konforme Chats: keine echten personenbezogenen Daten posten, keine unverschlüsselten Log-Transkripte.

Bleibt wachsam: Jede Anomalie dokumentiert ihr im QA-Log, jede Freigabe folgt erst nach erfolgreichem Sync aller Plattformen.
