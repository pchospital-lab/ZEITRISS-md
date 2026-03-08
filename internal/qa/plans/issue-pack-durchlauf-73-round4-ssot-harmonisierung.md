---
title: "Issue-Pack Durchlauf 73 – Round4 SSOT-Harmonisierung"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-08"
links:
  issue: "internal/qa/process/known-issues.md#zr-018-ruf-tier-progress-und-alienmystery-onboarding-als-ssot-nachziehen"
  statusmatrix: "internal/qa/process/ruf-alien-statusmatrix.md"
---

# Ziel

Restdrift aus `uploads/ZEITRISS_fresh_review_round4.md` strukturiert schließen,
mit Fokus auf SSOT-Konsistenz in geladenen Runtime-Modulen:

1. Voice-Default (`gm_second_person`) in Masterprompt/Toolkit/Save-Doku
   vereinheitlichen.
2. Save-v7-Kommunikation härten (Laufzeitfelder nicht persistiert,
   Legacy-Blöcke klar als Bridge markieren).
3. Px-Determinismus in `gameplay/kampagnenstruktur.md` gegen optionale
   Abweichungen absichern.
4. Ruf/Tier-Text im Toolkit auf `reputation.iti` korrigieren.
5. Absolut-Framing in frühen Spielertexten als ITI-Arbeitsbegriff ergänzen.
6. Bonus: Signaturtell + Forensik-Dreieck in Kampagnenstruktur ergänzen.

# Checkliste

- [x] Betroffene Module vollständig gelesen und Konflikte gegen SSOT abgeglichen.
- [x] Voice-Default in `meta/masterprompt_v6.md`,
      `systems/toolkit-gpt-spielleiter.md`,
      `systems/gameflow/speicher-fortsetzung.md` harmonisiert.
- [x] Save-Schattenstrukturen durch Klarlabels/Terminologie getrennt
      (kanonisch vs. Legacy/Bridge) und Persistenzkonflikt in
      `core/sl-referenz.md` bereinigt.
- [x] Optionalität bei Px (Merge-Schalter, Jitter, Halbzählung) in
      `gameplay/kampagnenstruktur.md` entfernt/neutralisiert.
- [x] Ruf/Tier-Drift im Toolkit korrigiert (`reputation.iti` als alleiniger
      Tierpfad).
- [x] Absolut-Rahmensatz in Onboarding-/Lore-Texten ergänzt.
- [x] Pflicht-Smoke + Linklint ausgeführt und dokumentiert.

# Abschluss

Round-4-P0/P1-Kernpunkte sind als Dokumentsynchronisierung umgesetzt; offene
Restpunkte verbleiben primär als zukünftige Redaktions-/Verdichtungsarbeit in
Legacy-Beispielen und nicht als Regelkonflikt im Runtime-Kanon.
