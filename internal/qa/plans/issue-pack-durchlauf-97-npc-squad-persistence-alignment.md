---
title: "Issue-Pack Durchlauf 97 – NPC-Squad-Persistenzabgleich"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_npc_mmo_immersion_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-96-cinematic-physicality-restdrift.md"
---

# Ziel

Restdrift in `gameplay/kampagnenstruktur.md` nachziehen, damit das Modul nicht
mehr implizit auf ein reines Drohnen-Solo oder temporäre NPC-Verbündete
kollabiert, sondern den kanonischen Persistenzpfad (`npc-team`, Offscreen-
Kontinuität) mitträgt.

1. Solo-Abschnitt auf den gültigen Startpfad `npc-team 0-4` spiegeln.
2. NPC-Squad-Kodex sprachlich von „temporären Verbündeten" auf persistente
   wiederkehrende NPC-Kontinuität heben.
3. Pflicht-Smoke ausfuehren und den Anschlusslauf in QA-Prozessdokumenten
   verankern.

# Checkliste

- [x] `gameplay/kampagnenstruktur.md` an den NPC-Persistenzkanon angepasst.
- [x] `internal/qa/process/known-issues.md` um Durchlauf 97 erweitert.
- [x] Pflicht-Smoke ausgefuehrt.

# Abschluss

Durchlauf 97 beseitigt einen verbleibenden MMO-Immersionsbruch im
Kampagnenstruktur-Modul: Solo bleibt nicht auf Drohnenfallback verengt und
Begleit-NPCs werden nicht mehr als primär temporaer beschrieben.
