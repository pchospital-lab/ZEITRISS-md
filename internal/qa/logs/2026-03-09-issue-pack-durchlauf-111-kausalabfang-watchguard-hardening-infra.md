---
title: "QA-Log 2026-03-09 – Durchlauf 111 (Kausalabfang Watchguard Hardening / Infra)"
status: "abgeschlossen"
run_id: "zr-019-d111"
---

# Kontext

Durchlauf 110 hat Named-Target-Echo und Kodex-Satzbau abgesichert.
Der Upload-Pack betont zusätzlich, dass der Marker **kein Kampfwerkzeug**
und **kein Shop-/Inventar-Gadget** sein darf, sondern ITI-Standardinfra.

# Umgesetzte Änderungen

1. **Watchguard-Hardening (Pflichtanker) erweitert**
   - Datei: `tools/test_kausalabfang_watchguard.js`
   - Neu als Pflichtanker über alle Kausalabfang-SSOT-Dateien:
     - Anti-Kampfanker (`kein Kampfwerkzeug` / `kein Kampf-Gadget`),
     - Distanzanker (`Nahdistanz`/`Nahbereich`),
     - Identitätsanker (`Identitätsfassung`/`Identitätslock`),
     - Uplinkanker (`Kodex-Uplink`/`Uplink`).

2. **Infra-Checks ergänzt**
   - Datei: `tools/test_kausalabfang_watchguard.js`
   - Für `core/sl-referenz.md` und `characters/ausruestung-cyberware.md`
     werden jetzt explizit geprüft:
     - Marker bleibt **nicht shopbar/kein Kaufgegenstand**,
     - Marker ist **kein Pflicht-Inventarstück**.

3. **Prozessdoku synchronisiert**
   - Dateien:
     - `internal/qa/process/known-issues.md`
     - `internal/qa/process/continuity-redesign-statusmatrix.md`
   - Evidenzlauf 111 + zusätzlicher Watchpoint für Infra-Setzung ergänzt.

4. **Fahrplanlauf dokumentiert**
   - Datei:
     `internal/qa/plans/issue-pack-durchlauf-111-kausalabfang-watchguard-hardening-infra.md`

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün** (inkl. `kausalabfang-watchguard-ok`)
2. `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`
   - Ergebnis: **grün**

# Bewertung

Kausalabfang ist jetzt nicht nur in Ablauf/Sperren/Echo-Kodex abgesichert,
sondern auch in seiner Infrastruktur-Rolle: kein Rückfall in aktiv-kämpferisches
Gadget-Design und keine Aufweichung zu Shop-/Inventar-Mechanik.
