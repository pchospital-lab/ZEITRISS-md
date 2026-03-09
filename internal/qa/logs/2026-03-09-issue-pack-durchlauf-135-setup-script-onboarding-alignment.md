---
title: "QA-Log 2026-03-09 – Durchlauf 135 (Setup-Script/Guide Onboarding-Alignment)"
status: "abgeschlossen"
run_id: "zr-021-d135"
---

# Kontext

Nach Durchlauf 134 war der Runtime-Startvertrag harmonisiert, im
Operator-Einstieg gab es aber noch Restdrift: `docs/setup-guide.md`
führte beim Script-Default auf einen veralteten DeepSeek-Hinweis und
`scripts/setup-openwebui.sh` zeigte im Abschluss noch `solo schnell` als
primären Einstieg.

# Umgesetzte Änderungen

1. **Setup-Guide auf Script-Default harmonisiert**
   - `docs/setup-guide.md`: Standard-Base-Modell des Setup-Scripts auf
     `anthropic/claude-sonnet-4.6` korrigiert.
   - `docs/setup-guide.md`: Preset-Vorschläge auf
     `solo klassisch`/`Spiel laden`/natürlichsprachlichen Neustart angepasst.

2. **Setup-Script UX auf kanonischen Startpfad umgestellt**
   - `scripts/setup-openwebui.sh`: Suggestion-Prompts neu sortiert und
     `solo schnell` als dominanten Prompt entfernt.
   - `scripts/setup-openwebui.sh`: Abschlusshinweis von
     `Spiel starten (solo schnell)` auf `Spiel starten (solo klassisch)`
     plus natürlicher Neustart-Formulierung geändert.

3. **Prozessspur fortgeschrieben**
   - `internal/qa/process/known-issues.md`: Durchlauf 135 in der
     ZR-020-Kette dokumentiert.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
2. `python3 tools/lint_links.py docs/setup-guide.md scripts/setup-openwebui.sh internal/qa/plans/issue-pack-durchlauf-135-setup-script-onboarding-alignment.md internal/qa/logs/2026-03-09-issue-pack-durchlauf-135-setup-script-onboarding-alignment.md internal/qa/process/known-issues.md`

# Bewertung

Der Onboarding-Standard ist jetzt auch im Betreiberpfad konsistent:
klassischer Kampagnenstart als Primärweg, natürliche Sprache als
player-facing Oberfläche und Fast-Lane nur noch als optionaler Sonderfall.
