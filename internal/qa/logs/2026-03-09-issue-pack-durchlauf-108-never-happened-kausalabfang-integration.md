---
title: "QA-Log 2026-03-09 – Durchlauf 108 (Kausalabfang/\"Never happened\" Integration)"
status: "abgeschlossen"
run_id: "zr-019-d108"
---

# Kontext

Das Upload-Paket `uploads/ZEITRISS_never_happened_gadget_pack.md` fordert eine
saubere Integration des "Never happened"-Konzepts ohne Retcon-Missbrauch.
Der Lauf verankert deshalb eine Minimalregel als ITI-Cleanup-Protokoll mit
harten Sperren und fixer Reihenfolge.

# Umgesetzte Änderungen

1. **Spieler-Handbuch ergänzt**
   - Datei: `core/spieler-handbuch.md`
   - Neuer Absatz im Abschnitt *Einsatzgewalt & Endzustände*:
     - Nur nach 0 LP,
     - nicht als Kampfaktion,
     - Reihenfolge `Loot sichern → optionaler Kausalabfang → Cleanup/Exfil`,
     - Verbotsmatrix (Chrononauten, Boss-Ziele, Zivilisten, Para, Arena/PvP,
       Chronopolis).

2. **SL-Referenz ergänzt**
   - Datei: `core/sl-referenz.md`
   - Standardausrüstung enthält jetzt den `Kausalabfang-Marker` als
     ITI-Standardmodul (nicht shopbar, kein Pflicht-Inventarobjekt).
   - Loot/Cleanup-Quickref um feste Reihenfolge und Spurenregel ergänzt.

3. **Toolkit-Guard ergänzt**
   - Datei: `systems/toolkit-gpt-spielleiter.md`
   - Neue Guard-Bullets definieren Nutzungsschranken,
     Pflichtvoraussetzungen (Nahdistanz/Identität/Uplink),
     Reihenfolge und Auto-vs.-Nachfrage-Logik (unbenannt vs. benannt).

4. **Masterprompt harmonisiert**
   - Datei: `meta/masterprompt_v6.md`
   - Cleanup-Sektion ergänzt um dieselbe Kausalabfang-Minimalregel inkl.
     Reihenfolge und Sperren, damit SSOT und Runtime-Leittexte identisch
     bleiben.

5. **Ausrüstungseintrag ergänzt**
   - Datei: `characters/ausruestung-cyberware.md`
   - Flavor-Eintrag als ITI-Standardmodul im Gadget-Block ergänzt; explizit
     nicht shopbar, kein Zeitzauber, keine freie Retcon-Logik.

6. **Prozessdoku fortgeschrieben**
   - Dateien:
     - `internal/qa/process/continuity-redesign-statusmatrix.md`
     - `internal/qa/process/known-issues.md`
   - Evidenzlauf 108 + Watchpoint für die neue Kausalabfang-Reihenfolge ergänzt.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**
2. `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`
   - Ergebnis: **grün**

# Bewertung

Die Integration bleibt klein, robust und konsistent: kein neues Subsystem,
kein Shop-/Save-Ballast, aber klare Leitplanken über alle relevanten
WS-Module hinweg. Damit ist der Mechanismus spielbar, moralisch sauber
framed und gegen Retcon-Drift abgesichert.
