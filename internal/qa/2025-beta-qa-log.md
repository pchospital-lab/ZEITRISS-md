---
title: "ZEITRISS Beta-QA Log 2025"
version: 0.1.0
tags: [meta]
---

# ZEITRISS Beta-QA Log 2025

## Zweck
Dieses Log sammelt unveränderte Ergebnisse aus Beta-GPT- und MyGPT-Testläufen. Es
ist die Arbeitsgrundlage, um Copy-&-Paste-Protokolle aus den GPT-Chats in
konkrete Aufgaben im QA-Fahrplan zu überführen und deren Abarbeitung
nachzuvollziehen.

## Workflow
1. Maintainer:innen oder Tester:innen führen den Playtest gemäß
   [docs/tester-playtest-briefing.md](../../docs/tester-playtest-briefing.md)
   aus und kopieren das vollständige Chatprotokoll in einen neuen Abschnitt
   dieses Logs.
2. Kennzeichne zu Beginn jedes Abschnitts Datum, Plattform, Build und genutzte
   Wissensbasis.
3. Füge das Protokoll unverändert als Codeblock ein. Sensible Informationen
   werden vor dem Einfügen entfernt oder anonymisiert.
4. Ergänze unterhalb des Protokolls eine kurze Liste mit offenen Punkten.
5. Verlinke den Abschnitt im QA-Fahrplan und priorisiere die offenen Punkte.
6. Sobald Codex einen Punkt bearbeitet hat, aktualisiere das Log mit Verweis auf
   Commit, PR oder Ticket.

## Abschnittsvorlage
```
## 2025-03-17 – Beta GPT – Build 4.2.2
- Plattform: Proton LUMO (offline)
- Wissensstand: README v4.2.2, master-index.json, Runtime-Module (18)
- Copy-&-Paste-Auftrag: siehe docs/tester-playtest-briefing.md Abschnitt "Beta"

```chatlog
<ungefiltertes Protokoll>
```

**Offene Punkte**
- [ ] Zusammenfassung des QA-Befunds (z. B. "Arena belohnt Px doppelt")
- [ ] ...

**Nachverfolgung**
- Commit/PR: `docs:xxxx`
- QA-Fahrplan: Abschnitt 1.2
```

## Pflegehinweise
- Bewahre jeden Abschnitt in chronologischer Reihenfolge auf (neuste oben).
- Verweise in Commit- oder PR-Beschreibungen auf den entsprechenden Abschnitt.
- Entferne keinen historischen Eintrag; markiere Korrekturen mit einem kurzen
  Hinweis ("Korrigiert am …").
- Sobald alle offenen Punkte erledigt sind, markiere den Abschnitt als
  abgeschlossen und dokumentiere das Datum.
