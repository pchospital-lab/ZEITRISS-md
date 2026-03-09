---
title: "QA-Log 2026-03-09 – Durchlauf 131 (Start/MMO-Onboarding-Entschlackung)"
status: "abgeschlossen"
run_id: "zr-021-d131"
---

# Kontext

Der Upload-Review `uploads/ZEITRISS_start_mmo_onboarding_review.md` markiert
keine Kernmechanik-Lücken mehr, sondern vorrangig Produkt-/UX-Drift im
Einstieg: zu starke Startsyntax-Pflicht, überprominentes
`klassisch vs. schnell`, menühaftes HQ-Weiterleitungsgefühl und leichte
README/Setup-Inkonsistenz.

# Umgesetzte Änderungen

1. **Startvertrag auf natürliche Sprache + Klassik-Default gehärtet**
   - `meta/masterprompt_v6.md`: Dispatcher-Priorität akzeptiert jetzt auch
     klare natürliche Neustart-/Load-Wünsche; klassischer Pfad fragt zuerst
     `generate`/`custom generate`/manuell; Schnellstart als Fast-Lane markiert.
   - `core/sl-referenz.md`: Klammer-Syntax als kanonische Kurzform statt
     Pflichtbarriere; bei fehlendem Modus Default `klassisch` +
     Generate-Frage.
   - `systems/toolkit-gpt-spielleiter.md`: gleicher Dispatcher-Vertrag,
     Mehrdeutigkeits-Only-Syntaxhinweis, Schnellstart nur auf Wunsch.
   - `core/spieler-handbuch.md`: Mini-Einsatzhandbuch und Schnellstartfluss auf
     natürlichen Einstieg + Klassik-Default umgestellt.

2. **HQ-Flow mit Save-Contract synchronisiert**
   - `systems/toolkit-gpt-spielleiter.md`: HQ-Option „Auto-HQ & Save“ zu
     „Auto-HQ (mit Save-Angebot)“ umgebaut und explizit verankert, dass nach
     Save-Hinweis kein automatischer Sprung ins nächste Briefing erfolgt.

3. **Archetypen/Pregens als Fallback statt Standard markiert**
   - `characters/charaktererschaffung-optionen.md`: klarer Prioritätssatz für
     Kampagnenstarts (`klassisch + generate/custom/manuell`), Archetypen als
     Inspirations-/One-Shot-Material eingerahmt.

4. **README/Setup harmonisiert**
   - `README.md`: Topblock stärker auf Produktversprechen (MMO ohne Server,
     Save = Charakter, KI-first) und konsistenten Startpfad ausgerichtet.
   - `docs/setup-guide.md`: Erstlauf-Formulierungen konsistent auf
     `solo klassisch` oder natürliche Neustartformulierung; `solo schnell`
     als Fast-Lane gekennzeichnet.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
2. `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process README.md docs/setup-guide.md core/spieler-handbuch.md core/sl-referenz.md systems/toolkit-gpt-spielleiter.md meta/masterprompt_v6.md characters/charaktererschaffung-optionen.md`

# Bewertung

Der Start-/Onboarding-Vertrag ist jetzt deutlich näher am gewünschten
KI-SL-Spielgefühl: natürliche Sprache zuerst, klare Hierarchie
(`klassisch + generate`), stabiler HQ-Save-Rhythmus und synchronisierte
Einstiegsdokumente.
