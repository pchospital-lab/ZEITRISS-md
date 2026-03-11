# Fahrplan – Durchlauf 216 (Weltstatus-Bruchwelten-Leitformel)

## Kontext

Die Runtime-SSOT hat die Weltstatus-Rückkopplung als Pflichtanker bereits
fest verankert (genau eine Zeile pro Missionszyklus mit Folgewirkung). Für
Langzeitspiel fehlte jedoch noch eine einprägsame Leitformel, die den
kosmologischen Einsatz dieser Zeile ausdrücklich auf Hauptlinie vs.
Bruchwelten spannt.

## Ziel

- In der SL-Referenz eine kompakte Leitformel ergänzen, die den
  Weltstatus-Pflichtsatz inhaltlich schärft.
- Prozessdoku für den Anschlusslauf synchronisieren.

## Arbeitspakete

1. `core/sl-referenz.md` ergänzen:
   - Leitformel bei der Weltstatus-Regel einfügen
     (`Hauptlinie stabilisieren` vs. `Bruchwelten-Dichte`).
2. Prozessanschluss fortschreiben:
   - `internal/qa/process/hard-final-review-next-steps.md`
   - `internal/qa/process/known-issues.md`
3. QA-Log für Durchlauf 216 anlegen.
4. Pflichtcheck ausführen: `bash scripts/smoke.sh`.

## Abnahme

- Weltstatus-Pflichtsatz und Bruchwelten-Leitformel stehen direkt zusammen
  in der SL-Referenz.
- Anschlussdokumente nennen Durchlauf 216 konsistent.
- Pflicht-Smoke ist grün.
