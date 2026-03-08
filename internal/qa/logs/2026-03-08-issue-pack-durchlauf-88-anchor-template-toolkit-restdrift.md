---
title: "QA-Log 2026-03-08 – Durchlauf 88 (Anchor-Template + Toolkit-Restdrift)"
status: "abgeschlossen"
run_id: "zr-018-d88"
---

# Kontext

Nach den Durchläufen 81–87 war die Session-Anker-Semantik weitgehend konsistent,
aber in einzelnen Beispiel-/Spiegeltexten standen noch Host-Reste (`HOST-main`,
"Host-HQ-Pool", "Host-Save"), die beim Lesen unnötige Alt-Semantik vermitteln.

# Umgesetzte Änderungen

1. **Template-Wording in SSOT/Masterprompt harmonisiert**
   - `meta/masterprompt_v6.md`
   - `systems/gameflow/speicher-fortsetzung.md`
   - `branch_id` in den kanonischen v7-JSON-Beispielen von `HOST-main` auf
     `ANCHOR-main` umgestellt.

2. **Toolkit-Runtime-Spiegel auf Session-Anker nachgezogen**
   - `systems/toolkit-gpt-spielleiter.md`
   - Merge-/Economy-Abschnitt: "Host-HQ-Pool" / "Host-Wallets" auf
     "Session-Anker-HQ-Pool" / "Session-Anker-Wallets" harmonisiert.
   - Acceptance-Checkliste: Dispatcher-Eintrag zu Gruppenstart von
     "Host-Save + weitere" auf "Session-Anker-Save + weitere" angepasst.

3. **Prozessdoku erweitert**
   - `internal/qa/process/known-issues.md`
   - Durchlauf-88-Eintrag ergänzt, damit Anschlussläufe direkt an den
     Terminologie-Stand anknüpfen können.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**

2. `python3 tools/lint_links.py core systems meta/masterprompt_v6.md README.md internal/qa/plans internal/qa/logs`
   - Ergebnis: **grün**

# Bewertung

Die Kontinuitäts-/Session-Anker-Semantik ist jetzt auch in den letzten
kanonischen JSON-Beispielen und Runtime-Spiegeltexten einheitlich. Das reduziert
Review-Reibung und verhindert semantische Rückfälle bei Folgeänderungen.
