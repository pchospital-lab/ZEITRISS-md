---
title: "Issue-Pack Durchlauf 111 – Kausalabfang Watchguard Hardening (Infra-Guards)"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_never_happened_gadget_pack.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-110-kausalabfang-echo-kodex-hardening.md"
---

# Ziel

Nachlauf zum Upload-Paket: die bereits verankerte Kausalabfang-Regel gegen
Drift im **Infra-/Einsatzrahmen** härten.

1. Watchguard um Pflichtanker erweitern (kein Kampfwerkzeug, Nahdistanz,
   Identitätsfassung, Kodex-Uplink).
2. Spezifische Guards für ITI-Infra-Setzung ergänzen (nicht shopbar,
   kein Pflicht-Inventar).
3. Prozessdoku + QA-Log für Anschlusslauf 111 aktualisieren.

# Checkliste

- [x] `tools/test_kausalabfang_watchguard.js` um zusätzliche Pflichtanker erweitert.
- [x] `tools/test_kausalabfang_watchguard.js` um Infra-Checks (`nicht shopbar`, `kein Pflicht-Inventar`) ergänzt.
- [x] `internal/qa/process/known-issues.md` um Evidenzlauf 111 ergänzt.
- [x] `internal/qa/process/continuity-redesign-statusmatrix.md` um Evidenzlauf 111 + Watchpoint ergänzt.
- [x] QA-Log für Durchlauf 111 angelegt.
- [x] `bash scripts/smoke.sh` erfolgreich ausgeführt.
- [x] `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` erfolgreich ausgeführt.

# Abschluss

Durchlauf 111 macht den Kausalabfang-Guard robuster gegen Rückfall in
Kampf-/Shop-/Inventar-Drift und sichert die ITI-Standardmodul-Setzung stärker
auf CI-Ebene.
