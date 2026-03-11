# QA-Log – Durchlauf 210 (Chronopolis Sperrmodus Wording-Fix)

## Ausgangslage

Review-Feedback auf Durchlauf 209: Zwei Formulierungen wirkten nicht präzise
genug (HQ-Re-Sync-Lesart und technische Ursache des Chronopolis-Sperrmodus).

## Umsetzung

- `core/sl-referenz.md`: SaveGuard-Re-Sync-Satz auf reguläre Offline-Missionen
  außerhalb Chronopolis eingegrenzt; HQ-Kern als wieder online klargestellt.
- `characters/hud-system.md`: Sperrmodus-Begründung auf Echo-bedingtes
  Instanzkollapsrisiko (inkl. Crew im Run) präzisiert.
- `meta/masterprompt_v6.md`: dieselbe Begründung als SSOT-Regel gespiegelt.

## Ergebnis

Der Chronopolis-Sperrmodus ist jetzt in Ursache und Wirkung eindeutig:
Kodex blockiert den Live-Kanal in `CITY`, um Echo-Kollaps der instanzierten
Zeitlinie zu verhindern; HQ-Kern bleibt der reguläre Wiederzugriffspfad.

## Checks

- `bash scripts/smoke.sh` → bestanden.
