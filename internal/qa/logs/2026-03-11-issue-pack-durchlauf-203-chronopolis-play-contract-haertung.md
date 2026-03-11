# QA-Log – Durchlauf 203 (Chronopolis Play-Contract Härtung)

## Ausgangslage

Chronopolis war als Stimmung, Lore und Risiko bereits stark, aber der
spielpraktische Contract noch nicht scharf genug als eigener Spielmodus
markiert. Ziel war eine klare Lesbarkeit für Spielende und KI-SL: freier
Infiltrationslauf mit reaktiver Stadt, ohne neues Subsystem.

## Umsetzung

- `core/spieler-handbuch.md`
  - Zusätzlicher Merksatz ergänzt: Chronopolis als freier
    Infiltrationslauf (hinein, Chancen lesen, Loot/Intel/Kontakte sichern,
    lebend hinaus).
- `meta/masterprompt_v6.md`
  - Chronopolis-Regeln um zwei Runtime-Vertragsanker erweitert:
    - **Chronopolis-Spielmodus** (kein Freizeit-Hub, kein Missionsersatz)
    - **Chronopolis-Reaktionslogik** (nach bedeutsamer Aktion genau ein Beat
      aus vorhandenen Tools; nach starkem Gewinn Exit-Druck)
- `gameplay/kampagnenstruktur.md`
  - Unter den Runtime-Leitplanken drei präzisierende Untersektionen ergänzt:
    - **4A Spielmodus: Freier Infiltrationslauf**
    - **4B Reaktionslogik ohne Counter**
    - **4C Seltene Apex-Bedrohung**
- Prozessspiegel aktualisiert:
  - `internal/qa/process/hard-final-review-next-steps.md`
  - `internal/qa/process/known-issues.md` (ZR-021)

## Ergebnis

Chronopolis ist nun konsistent als eigener Spielmodus lesbar:
- frei wie ein Infiltrationslauf,
- reaktiv statt nur atmosphärisch,
- mit seltenem, glaubhaftem Apex-Peak vorzugsweise auf Rückweg/Exit.

Damit bleibt der Kontrast stabil: HQ sicher, Mission strikt,
Chronopolis frei aber räuberisch.

## Checks

- `bash scripts/smoke.sh` → bestanden.
- `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` → bestanden.
- `rg -n 'Chronopolis-Spielmodus|Chronopolis-Reaktionslogik|Spielmodus: Freier Infiltrationslauf|Seltene Apex-Bedrohung' core/spieler-handbuch.md meta/masterprompt_v6.md gameplay/kampagnenstruktur.md` → erwartete Treffer.
