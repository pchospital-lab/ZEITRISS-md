---
title: "QA-Log 2026-03-08 – Durchlauf 75 (Round4 Restklarheit Save/Chronopolis)"
status: "abgeschlossen"
run_id: "zr-018-d75"
---

# Kontext

Anschlusslauf nach Durchlauf 74. Fokus auf verbleibende redaktionelle Drifts aus
Round 4: Save-Persistenzsprache (`character{}` vs. `characters[]`) und
Chronopolis-Wording (UI-Cutscene vs. In-World-Hinweis).

# Umgesetzte Änderungen (Kern)

1. **Save-Persistenzsprache auf v7-Container geschärft**
   - `core/sl-referenz.md`: Persistenz-Bullet von Legacy-`character.attributes`
     auf kanonische `characters[]`-Felder (`id`, `attr`, `sys_installed`,
     `stress`, `psi_heat`) umgestellt.
   - Legacy-Normalisierung (`character{}`/`character.attributes{}` →
     `characters[]` + `attr`) explizit ergänzt.

2. **Legacy-Bridge in Speicherdoku klar abgegrenzt**
   - `systems/gameflow/speicher-fortsetzung.md`: Hinweis vor dem großen
     Legacy-HQ-Referenzblock um den expliziten Satz ergänzt,
     dass der Block nicht als kanonischer Neu-Export zu verwenden ist.

3. **Chronopolis-Stilkante geglättet**
   - `gameplay/kampagnenstruktur.md`: Entry-Event-Formulierung von
     "Warn-Cutscene" auf "einmaligen In-World-Warnhinweis" umgestellt,
     konsistent mit Abschnitt "Einstieg-Flow ohne UI-Dialoge".

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**

2. `python3 tools/lint_links.py core characters gameplay systems meta/masterprompt_v6.md README.md`
   - Ergebnis: **grün**

# Bewertung

- Kein offener Restkonflikt mehr zwischen Persistenz-Beschreibung in der
  SL-Referenz und v7-Zielschema-Sprache.
- Legacy-Beispiel bleibt für Import/QA nutzbar, ist aber klar vom kanonischen
  Export getrennt.
- Chronopolis-Entry folgt jetzt auch im Event-Text der no-UI-Dialog-Linie.
