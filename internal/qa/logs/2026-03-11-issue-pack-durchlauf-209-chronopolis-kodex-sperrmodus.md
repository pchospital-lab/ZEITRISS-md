# QA-Log – Durchlauf 209 (Chronopolis Kodex-Sperrmodus)

## Ausgangslage

Nach Durchlauf 208 (Playtest-Gate-Pretest-Enforcement) bestand weiterhin eine
kleine, aber spielrelevante SSOT-Drift: Chronopolis war als Modus geschärft,
Kodex/HUD-Formulierungen klangen jedoch teils noch wie globaler Vollzugriff.

## Umsetzung

- Chronopolis-Sperrmodus (_Kodex dunkel, HUD lebendig_) in den Runtime-SSOT
  nachgezogen:
  - `core/spieler-handbuch.md`
  - `core/sl-referenz.md`
  - `characters/hud-system.md`
  - `meta/masterprompt_v6.md`
  - `gameplay/kampagnenstruktur.md`
  - `systems/toolkit-gpt-spielleiter.md`
- `!offline` differenziert jetzt ausdrücklich:
  - Standard: Re-Sync-Schritte bei Linkverlust
  - Chronopolis (`CITY`): bewusster Sperrmodus mit lokal weiterlaufendem HUD

## Ergebnis

Chronopolis ist jetzt als eigener dritter Betriebszustand klar formuliert:
HQ-Kern mit Vollzugriff, Feld/Offline mit Re-Sync-Logik, Chronopolis mit
gezielt blockiertem Live-Kanal bei aktivem HUD. Damit ist der gewünschte
Kontrast für den nächsten Playtest stabil im SSOT verankert.

## Checks

- `bash scripts/smoke.sh` → bestanden.
- `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` → bestanden.
- `rg -n 'Kodex dunkel, HUD lebendig|Sperrmodus|nicht in `CITY`|Chronopolis \(`CITY`\): eigene Sperrmodus-Antwort' core/spieler-handbuch.md core/sl-referenz.md characters/hud-system.md meta/masterprompt_v6.md gameplay/kampagnenstruktur.md systems/toolkit-gpt-spielleiter.md` → erwartete Treffer.
