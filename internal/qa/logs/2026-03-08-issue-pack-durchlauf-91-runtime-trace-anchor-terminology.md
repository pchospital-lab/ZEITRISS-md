---
title: "QA-Log 2026-03-08 – Durchlauf 91 (Runtime-Trace Anchor-Terminologie)"
status: "abgeschlossen"
run_id: "zr-018-d91"
---

# Kontext

Nach Durchlauf 90 blieb eine kleine, aber sichtbare Restdrift in der
Runtime-Schicht: Merge-Notizen und ein UI-Override-Trace trugen noch
Host-Wording (`Host-Vorrang`, `ui_host_override`), obwohl die
Kontinuitätsregeln auf Session-Anker umgestellt sind. Das erschwert
Trace-Auswertung und vergrößert das Risiko für semantische Rückdrift.

# Umgesetzte Änderungen

1. **Runtime-Terminologie harmonisiert**
   - `runtime.js`
   - Merge-Trace-Notizen auf `Session-Anker-Vorrang` umgestellt.
   - Wallet/HQ-Konfliktnotiz auf
     `HQ-Pool (economy.cu): Session-Anker-Vorrang` angepasst.
   - UI-Override-Trace auf `ui_session_anchor_override` umbenannt.
   - Economy-Audit-Bandgrund auf `session_anchor_level` harmonisiert.

2. **Referenz + Tests nachgezogen**
   - `core/sl-referenz.md`: Trace-Verweis auf `ui_session_anchor_override`.
   - `tools/test_economy_merge.js`: Assertion-Texte auf Session-Anker-Wording.

3. **QA-Prozess fortgeschrieben**
   - Fahrplan/Log für Durchlauf 91 angelegt.
   - Known-Issues um Durchlauf-91-Evidenz ergänzt.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**

2. `python3 tools/lint_links.py core systems meta/masterprompt_v6.md README.md internal/qa/plans internal/qa/logs internal/qa/process`
   - Ergebnis: **grün**

# Bewertung

Die Session-Anker-Semantik ist nun auch in Runtime-Trace-Labels und
Merge-Konfliktnotizen konsistent verankert. Das verbessert Lesbarkeit,
maschinelle Auswertung und minimiert Anschlussdrift zwischen Laufzeit,
Dokumentation und QA-Checks.
