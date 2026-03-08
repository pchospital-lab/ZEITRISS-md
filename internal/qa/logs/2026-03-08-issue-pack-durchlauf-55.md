---
title: "QA-Log – Issue-Pack Durchlauf 55"
date: 2026-03-08
scope: "WS-/OpenWebUI-Grenze: Save-Kanon ohne Repo-Pfad-Abhängigkeit"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- Upload-Issue-Pack: `uploads/ZEITRISS_v7_save_load_issue_pack.md`.
- Fahrplan: `internal/qa/plans/issue-pack-durchlauf-55.md`.

## Umsetzung in diesem Durchlauf

1. **Save-SSOT in WS-Datei entkoppelt**
   - `systems/gameflow/speicher-fortsetzung.md` beschreibt den Save-Kanon nun
     als v7-Template im Masterprompt + Kompakt-Profil in derselben WS-Datei.
   - Repo-Pfadverweise auf konkrete Schema-Dateien wurden aus dem KI-SL-
     Leitabschnitt entfernt; externe Schemas bleiben nur Tooling-Hinweis.

2. **SL-Referenz auf sichtbaren Kanon fokussiert**
   - `core/sl-referenz.md` verweist im Save-Block jetzt primär auf das
     Kompakt-Profil im Wissensspeicher.
   - Externe Schema-Dateien sind explizit als Runtime-/Tooling-Hilfe außerhalb
     des Wissensspeichers markiert (inkl. Legacy-Importfehlerpfad-Hinweis).

3. **Known-Issues fortgeschrieben**
   - `internal/qa/process/known-issues.md` ergänzt Durchlauf 55 als
     Nachschärfung der WS-/Repo-Trennung ohne Regeländerung.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.

## Ergebnis / Anschluss

- Der spielrelevante Save-Kanon bleibt vollständig im sichtbaren
  Wissensspeicher (Masterprompt + WS-Module) beschrieben.
- Repo-Schemas bleiben für Integrations-/CI-Zwecke nutzbar, ohne als
  KI-SL-Laufzeitabhängigkeit missverstanden zu werden.
