---
title: "QA-Log 2026-03-09 – Durchlauf 134 (Masterprompt BEREIT-Startvertrag)"
status: "abgeschlossen"
run_id: "zr-021-d134"
---

# Kontext

Nach den Durchläufen 131–133 war der eigentliche Dispatcher-Vertrag bereits
auf natürliche Sprache + `klassisch`-Default harmonisiert. Im Masterprompt-
Abschlussblock `## BEREIT` standen aber weiterhin vor allem Startbeispiele mit
`solo/gruppe schnell`, was den alten Menüreiz unnötig sichtbar hielt.

# Umgesetzte Änderungen

1. **Masterprompt-Abschlussblock harmonisiert**
   - `meta/masterprompt_v6.md`: `Warte auf Spielerkommando` ersetzt durch
     `Warte auf klaren Start-/Load-Wunsch in natürlicher Sprache oder Kurzform`.

2. **Start-Hierarchie explizit nachgezogen**
   - `meta/masterprompt_v6.md`: Standard auf `Spiel starten (solo klassisch)`
     bzw. natürlichsprachlichen Neustart gesetzt; im klassischen Pfad
     `generate`/`custom generate`/`selbst bauen` als erste Frage verankert.

3. **Fast-Lane klar als optional markiert**
   - `meta/masterprompt_v6.md`: `Spiel starten (solo schnell)` nur bei
     ausdrücklichem Wunsch; Load weiter via JSON-Block (optional mit
     `Spiel laden`).

# Ausgeführte Checks

1. `bash scripts/smoke.sh`

# Bewertung

Der sichtbare Einstieg am Ende des Masterprompts entspricht nun vollständig dem
bereits implementierten MMO-/Onboarding-Vertrag: natürliche Sprache zuerst,
klassisch als Kampagnen-Default, Fast-Lane optional und JSON-first-Load.
