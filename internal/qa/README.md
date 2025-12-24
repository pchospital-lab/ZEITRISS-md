---
title: "QA-Index"
version: 1.0.0
tags: [meta, qa]
---

# QA-Index

Diese Übersicht bündelt alle qualitätssichernden Artefakte. Sie dient als
Einstiegspunkt für Maintainer:innen und den Repo-Agenten, wenn neue
Playtests, Beta-GPT-Durchläufe oder Deepchecks anstehen.

## Verzeichnisstruktur

| Ordner         | Inhalt                                                                | Zweck                                                                         |
| -------------- | --------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `audits/`      | `ZEITRISS-qa-audit-2025.md`                                           | Bewertet abgeschlossene Testreihen und dokumentiert Maßnahmenstatus.          |
| `plans/`       | `ZEITRISS-qa-fahrplan-2025.md`                                        | Priorisierte Aufgabenliste inklusive Übergaben an Codex und Maintainer:innen. |
| `evidence/`    | `README.md`, `2025-beta-gpt-evidenz.md`                               | Ablage für HUD-/Save-/Dispatcher-Nachweise zu den Beta-GPT-Läufen.            |
| `transcripts/` | `start-transcripts.md`                                                | Referenztranskripte für Startszenarien (Solo, Gruppe, NPC-Team).              |
| `logs/`        | `2025-beta-qa-log.md`, `ZEITRISS-vereinheitlichungs-fahrplan-2025.md` | Vollständige Chatprotokolle und begleitende Vereinheitlichungs-Logs.          |
| `../docs/qa/`  | `tester-playtest-briefing.md`                                         | Copy-&-Paste-Auftrag inkl. Acceptance-Smoke-Checkliste für Beta-GPT/MyGPT.    |

## Workflow-Knoten

1. **Deepcheck oder manueller Review** → Erkenntnisse aus Live-Sessions mit
   Codex unmittelbar im Fahrplan (`plans/…`) unter "Deepcheck-Aufgaben"
   ergänzen und bei Bedarf als Nachtrag im Audit (`audits/…`) verlinken.
2. **Beta-GPT-Testlauf** → Auftrag aus `../docs/qa/tester-playtest-briefing.md`
   nutzen, Ergebnis unverändert in `logs/` ablegen und anschließend Fahrplan/Audit
   synchronisieren.
3. **Smoke- oder Regressionstest** → Acceptance-Smoke-Abschnitt im
   `docs/qa/tester-playtest-briefing.md` durchspielen, Abweichungen im Log
   verlinken und im Fahrplan priorisieren.
4. **Dokumentationsabgleich** → Sicherstellen, dass `README.md`,
   `CONTRIBUTING.md` und `docs/maintainer-ops.md` auf die aktualisierten
   Pfade verweisen.

So bleibt der QA-Strom aus Findings, Priorisierung und Umsetzung zentral
sichtbar, unabhängig davon, ob Ergebnisse aus automatisierten GPT-Läufen
oder manuellen Sessions stammen.
