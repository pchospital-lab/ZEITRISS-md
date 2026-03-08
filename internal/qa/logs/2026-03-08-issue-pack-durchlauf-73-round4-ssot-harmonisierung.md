---
title: "QA-Log 2026-03-08 – Durchlauf 73 (Round4 SSOT-Harmonisierung)"
status: "abgeschlossen"
run_id: "zr-018-d73"
---

# Kontext

Umsetzung der im Round-4-Review benannten Restprobleme (Voice-SSOT,
v7-Schattenstrukturen, Px-Optionalität, Ruf/Tier-Tooling, Absolut-Framing)
inkl. Anschlussdokumentation für Folge-Durchläufe.

# Umgesetzte Änderungen (Kern)

1. **Voice-SSOT vereinheitlicht**
   - `meta/masterprompt_v6.md`: UI-Template-Default auf
     `voice_profile = gm_second_person` gesetzt.
   - `systems/toolkit-gpt-spielleiter.md`: Voice-Lock von Third-Person-Default
     auf Second-Person-Default umgestellt; Third/Observer als optionale
     Accessibility-/Style-Profile deklariert.
   - `systems/gameflow/speicher-fortsetzung.md`: UI-Defaults + Beispiele auf
     `gm_second_person` normalisiert.

2. **Save-v7-SSOT geschärft / Konflikt bereinigt**
   - `core/sl-referenz.md`: HQ-Deepsave-Pflichtliste bereinigt; Laufzeitfelder
     (`SYS_runtime`, `SYS_used`, `cooldowns`) als **nicht persistiert**
     festgezogen.
   - `systems/gameflow/speicher-fortsetzung.md`: SaveGuard-Pflichtliste
     entsprechend bereinigt und Legacy-Vollbeispiel explizit als
     **Legacy-/Bridge-Referenz** markiert.

3. **Px-Determinismus konsolidiert**
   - `gameplay/kampagnenstruktur.md`: optionale Merge-Schalter,
     Kurzmissions-Halbzählung und ±1-Jitter aus kanonischer Regelbeschreibung
     entfernt/auf deterministischen SSOT-Pfad zurückgeführt.

4. **Ruf/Tier-Drift geschlossen**
   - `systems/toolkit-gpt-spielleiter.md`: Tier-Zugang auf
     `reputation.iti` als alleinige formale Quelle korrigiert;
     Fraktionsruf auf Story-/Politikreaktionen begrenzt.

5. **Absolut-Framing nachgeschärft**
   - Rahmensatz „ITI-Arbeitsbegriff/Grenzphysik" in frühe Texte ergänzt:
     `core/spieler-handbuch.md`,
     `characters/charaktererschaffung-grundlagen.md`,
     `gameplay/kampagnenuebersicht.md`.

6. **Bonus-Mechaniken ergänzt**
   - `gameplay/kampagnenstruktur.md`: neue Abschnitte
     **Signaturtell (Boss-/Rift-Payoff)** und
     **Forensik-Dreieck (Rift-Casefiles)** ergänzt.

7. **Chronopolis UI-Kante geglättet**
   - `gameplay/kampagnenstruktur.md`: Warn-Popup/Button-Sprache in
     narrativen Einstieg-Flow ohne UI-Dialogpflicht überführt.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**

2. `python3 tools/lint_links.py core characters gameplay systems meta/masterprompt_v6.md README.md`
   - Ergebnis: **grün**

# Bewertung

- Die Round-4-Topbaustellen sind im geladenen Runtime-Kanon geschlossen.
- Verbleibende Altfelder in Save-Dokumenten sind als Legacy-/Import-Bridge
  erkennbar und widersprechen der kanonischen v7-Exportlinie nicht mehr.

# Nächster Schritt

Falls gewünscht: gezielte Redaktionsrunde, um verbleibende Legacy-Beispielblöcke
in `systems/gameflow/speicher-fortsetzung.md` kompakter in einen gebündelten
Appendix zu verschieben (rein dokumentarisch, ohne Regeländerung).
