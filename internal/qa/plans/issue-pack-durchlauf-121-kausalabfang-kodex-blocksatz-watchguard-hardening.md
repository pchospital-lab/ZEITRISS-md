---
title: "Issue-Pack Durchlauf 121 – Kausalabfang Kodex-Blocksatz Watchguard-Hardening"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_never_happened_gadget_pack.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-120-kausalabfang-festnahme-statt-loeschung-hardening.md"
---

# Ziel

Den verbleibenden Kodex-Feinpunkt aus dem Upload (voller Blocksatz für
Zulässigkeits-Sperren) SSOT-parallel absichern, damit Toolkit und Masterprompt
bei Kausalabfang-Meldungen nicht auseinanderlaufen.

1. Kodex-Blocksatz in `meta/masterprompt_v6.md` auf den Toolkit-Stand heben.
2. `tools/test_kausalabfang_watchguard.js` um strikte Kodex-Pflichtregex ergänzen.
3. Prozessdoku (Plan/Log/known-issues/Statusmatrix) für Anschlussläufe nachziehen.

# Checkliste

- [x] `meta/masterprompt_v6.md` auf vollen Kodex-Blocksatz harmonisiert.
- [x] `tools/test_kausalabfang_watchguard.js` um Kodex-Pflichtregex erweitert.
- [x] QA-Log für Durchlauf 121 angelegt.
- [x] `bash scripts/smoke.sh` erfolgreich ausgeführt.
- [x] `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` erfolgreich ausgeführt.

# Abschluss

Durchlauf 121 stabilisiert den trockenen Kodex-Satzbau weiter und macht den
Upload-Anker „Ziel nicht zulässig / Uplink fehlt / Abfangfenster steht" als
CI-pflichtigen Hardening-Check explizit.
