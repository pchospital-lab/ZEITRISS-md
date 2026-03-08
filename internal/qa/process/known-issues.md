---
title: "Known Issues & Triage-Prozess"
version: 1.0.0
tags: [meta, qa]
---

# Known Issues & Triage-Prozess

Diese Seite bündelt den Prozess für offene QA-Funde, die nicht direkt im
Runtime-Content gelöst werden (z. B. Tooling-, Workflow- oder Plattformfragen).

## Ziel

- Einheitlicher Ort für Triagestatus (`neu`, `geprüft`, `geplant`,
  `in Umsetzung`, `abgeschlossen`, `verworfen`).
- Klare Verlinkung zwischen Eingangsquelle, Fahrplan, Log und Umsetzung.
- Saubere Trennung zwischen Runtime-Änderungen und Meta-Prozessarbeit.

## Prozess (leichtgewichtig)

1. **Erfassen**
   - Issue im QA-Log benennen und mit Quelle verlinken (Upload, Playtest,
     Audit, Maintainer-Report).
2. **Triagieren**
   - Priorität (`P0`–`P3`), Scope (Runtime/Meta/Tooling) und Besitzer:in
     festlegen.
3. **Planen**
   - Falls umsetzungsrelevant: Ticket in den Fahrplan (`internal/qa/plans/`)
     aufnehmen.
4. **Umsetzen**
   - Änderungen im Repo durchführen, Pflichtprüfungen laufen lassen,
     Commit/PR mit Referenz auf den QA-Eintrag versehen.
5. **Abschließen**
   - Status in dieser Liste, im QA-Log und im Fahrplan synchron auf
     `abgeschlossen` oder `verworfen` setzen.

## Aktuelle Known Issues

| ID | Titel | Quelle | Priorität | Scope | Status | Notiz |
| --- | --- | --- | --- | --- | --- | --- |
| ZR-015 | Interne QA-Known-Issues in GitHub-Issue-Triage spiegeln | `uploads/deep-research-report(4).md` | P3 | Meta/Prozess | abgeschlossen | Diese Prozessseite ist der kanonische Startpunkt; operative Arbeit läuft weiterhin über Fahrplan + QA-Log. |
| ZR-016 | Externer Codex-Issue-Pack in iterative Fahrplan-Cluster überführen | `uploads/ZEITRISS_codex_issue_pack.md` | P0 | Runtime/QA | abgeschlossen | Primärindex für den Gesamtstand: `internal/qa/process/issue-pack-statusmatrix.md`. Abschluss dokumentiert bis Durchlauf 38 (`internal/qa/plans/issue-pack-durchlauf-01.md` bis `internal/qa/plans/issue-pack-durchlauf-38.md` plus zugehörige QA-Logs `internal/qa/logs/*issue-pack-durchlauf-*.md`). Folgearbeit wird als neue Known-Issue-ID angelegt. |
| ZR-017 | Save/Load v7 und OpenWebUI-Standardpfad aus dem neuen Issue-Pack nachziehen | `uploads/ZEITRISS_v7_save_load_issue_pack.md` | P0 | Runtime/QA | abgeschlossen | Durchläufe 39-47 umgesetzt (`internal/qa/plans/issue-pack-durchlauf-39.md` bis `internal/qa/plans/issue-pack-durchlauf-47.md` + Logs): Chat-Load-Standard (`!save` + JSON-Paste, `Spiel laden` optional), `!bogen`-Lesesicht, kanonische Split/Merge-Grenze, Mid-Episode-Klarfall 5er→3/2, OpenWebUI-Hopper/Leaver-Betrieb und Arena-Savegrenze (`idle|completed` bei inaktiver Arena) sind dokumentiert; obsolet gewordene Runtime-Komfortbefehle (`load/suspend/resume/autosave hq`) wurden aus dem Spielerpfad entfernt. Leseführung bleibt auf "Kanon pro aktivem Host-Chat" (Merge weiter host-priorisiert). Dedupe/Lineage-Standard wurde in Durchlauf 48 dokumentarisch verankert; Save-Größenbudget inkl. `summaries.*`-Prune-Standard wurde in Durchlauf 49 ergänzt; der Px-Zustandsautomat (`campaign.px_state` + Merge-Priorität `consumed > pending_reset > stable`) wurde in Durchlauf 50 vereinheitlicht; in Durchlauf 51 wurden die Economy-Bänder auf `120/512/900+` harmonisiert und eine v7-Fixture-/Smoke-Strecke für 5er-Highlevel, Split/Merge, Chronopolis, Abort und chat-nativen JSON-Load ergänzt; in Durchlauf 52 wurde das formale Mixed-Split-Präzedenzmodell (Rift/PvP/Chronopolis/Abort) inklusive Allowlist-Importregeln und Fixture-Checks abgeschlossen. Durchlauf 53 führte eine SSOT-Revalidierung nach: konkurrierender Alt-v7-Exportblock in `speicher-fortsetzung.md` auf den kanonischen `zr`/`campaign.mission`/`attr`/`arc.questions+hooks`-Pfad harmonisiert; Legacy-Feldnamen bleiben nur Import-Bridge. Durchlauf 54 ergänzt einen dauerhaften Driftguard (`tools/test_v7_schema_consistency.js`) plus kanonische v7-Schemareferenz (`systems/gameflow/saveGame.v7.schema.json`) im Pflicht-Smoke. Durchlauf 55 schärft die WS-/Repo-Trennung nach: Save-Kanon in WS-Texten explizit ohne Repo-Pfad-Abhängigkeit für KI-SL/OpenWebUI; externe Schemas bleiben reine Tooling-/Runtime-Hilfe. Durchlauf 56 ergänzt eine zentrale Statusmatrix über Upload-Issues 1–10 (`internal/qa/process/v7-save-load-statusmatrix.md`) inklusive Watchpoints für Anschluss-QA und revalidiert den Stand erneut via Pflicht-Smoke. |

| ZR-018 | Ruf/Tier-Progress und Alien/Mystery-Onboarding als SSOT nachziehen | `uploads/ZEITRISS_ruf_alien_review.md` | P0 | Runtime/QA | abgeschlossen | Durchlauf 57 abgeschlossen: Trennung `reputation.iti` vs. `reputation.factions.*`, bossbasierte ITI-Rufprogression (M1/M5/M10/M15/M20), Tier-V-Lizenz als kaufbarer Pfad, Rang-Mapping 0–5, Level-10-vs.-Lizenz-Klarstellung sowie Mystery-Contract/Graue-Deckname in Spieler-Onboarding und Kampagnenübersicht. Durchlauf 58 schließt den Restdrift im Spieler-Handbuch (Debrief-Label `ITI-Ruf`, Tier-V-Cheatsheet `5.000 CU`). Primärindex: `internal/qa/process/ruf-alien-statusmatrix.md`. |

## Pflegehinweis

Neue Meta-Issues werden zuerst hier erfasst und danach in Fahrplan/Log
verknüpft. Runtime-Issues bleiben primär im Fahrplan, werden aber bei
prozessualem Bedarf mit Referenz in dieser Datei gespiegelt.
