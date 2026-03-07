---
title: "QA-Log – Issue-Pack Durchlauf 37"
date: 2026-03-07
scope: "ZR-016 Übersichtshärtung (Statusmatrix + Known-Issues-Refactoring)"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- ZR-016 (externer Codex-Issue-Pack), Maintainer-Wunsch nach sauberem
  Anschlusszustand und klarer Gesamtübersicht vor den nächsten inhaltlichen
  Schritten.

## Umsetzung in diesem Durchlauf

1. **Statusmatrix eingeführt (`internal/qa/process/issue-pack-statusmatrix.md`)**
   - Kompakte 1–13-Übersicht mit Status, letzten Evidenz-Durchläufen und
     Primärpfaden je Issue ergänzt.
   - „in Nachpflege" bewusst nur für die verbleibenden Meta-Closure-Themen
     (Issue 1/6 im Kontext ZR-016-Gesamtabschluss) gesetzt.

2. **Known-Issues-Eintrag entschlackt (`internal/qa/process/known-issues.md`)**
   - Die überlange Aufzählung einzelner Plan-/Log-Dateien im ZR-016-Notizfeld
     auf einen stabilen Einstiegspfad reduziert:
     `issue-pack-statusmatrix.md` als Primärindex.
   - Durchlaufbereich auf den aktuellen Stand (01–37) aktualisiert.

3. **Prozessnachführung**
   - Plan + Log für Durchlauf 37 ergänzt, damit Folgearbeit direkt anknüpfen
     kann.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
