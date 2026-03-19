# Playtest: 5er-Gruppe — Split/Merge v7 Schema-Test

**Datum:** 2026-03-05
**Modell:** zeitriss-v426-uncut (Sonnet 4.6)

---

## Phase 1: Erstellung ✅ PASS

- 5 Chars erstellt, alle Summe 18, alle ≤ 6, v7-Schema korrekt
- Reputation, has_psi, Equipment mit Tier — alles vorhanden

## Phase 2: Split ✅ PASS

- 5er-Gruppe nach Episode 1 gesplittet in 3er (Hammer/Phantom/Cipher → RS-001) und 2er (Silk/Drift → RS-002)
- HQ-Pool korrekt aufgeteilt (2500/2500)
- Seeds korrekt zugewiesen
- `team_split` Event im Trace
- Psi-Daten bei Drift korrekt mitgenommen
- Alle Character-Daten intakt in beiden Saves
- v7-Schema durchgehend korrekt

### Beobachtungen beim Split:

1. Die KI hat `campaign.mode` auf "rift" gesetzt — korrekt für Rift-Ops
2. `campaign.episode` auf 2 gesetzt — diskutabel (sind Rift-Ops eine eigene Episode?)
3. Seed-Status von "open" → "active" geändert — guter Touch, zeigt aktiven Einsatz
4. arc-Block identisch in beiden Saves — korrekt (geteiltes Wissen)

### Issue #1: campaign.episode bei Rift-Split

Die KI hat `episode: 2` gesetzt. Aber Rift-Ops sind ZWISCHEN Episoden, nicht Episode 2.
Sollte `episode: 1` bleiben mit einem Flag `"phase": "rift"` oder einfach `mode: "rift"` reicht.
→ **Nicht spielbrechend**, aber semantisch fragwürdig.

## Phase 3: Merge ✅ PASS

Beide Teams nach Rift-Abschluss wieder zusammengeführt. Ergebnis:

| Merge-Aspekt               | Ergebnis                                    | Bewertung |
| -------------------------- | ------------------------------------------- | --------- |
| Characters zusammengeführt | 5/5, Host = CHR-0001 (Index 0)              | ✅        |
| Px-Konsolidierung          | Max-Wert genommen (2)                       | ✅        |
| HQ-Pool                    | Summiert: 3500 + 3200 = 6700                | ✅        |
| Seeds Union                | RS-001 + RS-002 (beide closed)              | ✅        |
| Artefakte intakt           | Hammer: Skorpion-Stachel, Drift: Krakenherz | ✅        |
| Psi-Daten                  | Drift: pp=7, neue Fähigkeit (Psi-Schild)    | ✅        |
| Verwundung                 | Phantom: hp=8, stress=2 (aus Rift)          | ✅        |
| Arc-Daten                  | Factions, Questions, Hooks gemergt          | ✅        |
| Merge-Protokoll            | Transparente Tabelle mit Entscheidungen     | ✅        |
| v7-Schema                  | Vollständig konform                         | ✅        |

### Highlights:

- Die KI zeigt ein **transparentes Merge-Protokoll** als Tabelle — jede Entscheidung nachvollziehbar
- **Verwundungen werden korrekt transportiert** — Phantom hat hp=8 und stress=2 aus dem Rift mitgenommen
- **Psi-Progression funktioniert** — Drift hat im Rift eine neue Fähigkeit erlernt und TEMP gesteigert
- **HQ-Pool wird summiert**, nicht überschrieben — ökonomisch sauber

## Phase 4: Gesamtfazit

### v7-Schema Bewertung

| Test                   | Ergebnis |
| ---------------------- | -------- |
| Solo-Quickstart + Save | ✅ PASS  |
| 5er-Gruppen-Erstellung | ✅ PASS  |
| Team-Split (3er + 2er) | ✅ PASS  |
| Separate Rift-Ops      | ✅ PASS  |
| Team-Merge nach Rifts  | ✅ PASS  |
| Attribut-Cap 6         | ✅ PASS  |
| Summe 18               | ✅ PASS  |
| Reputation/Ruf         | ✅ PASS  |
| Psi-System (has_psi)   | ✅ PASS  |
| Artefakte (max 1)      | ✅ PASS  |
| Equipment mit Tier     | ✅ PASS  |

### Issues gefunden

| #   | Severity | Issue                                             | Status                                    |
| --- | -------- | ------------------------------------------------- | ----------------------------------------- |
| 1   | Info     | campaign.episode wird beim Split hochgezählt      | Akzeptabel — "bereit für nächste Episode" |
| 2   | Info     | Stress bei Split nicht auf 0 gesetzt (HQ = Reset) | Design-Frage: HQ-Reset bei Split?         |

**Gesamtbewertung: Das v7-Schema funktioniert.** Split/Merge mit 5er-Gruppe, separate Rift-Ops und anschließendem Merge — alles sauber. Die KI versteht das Schema intuitiv und produziert konsistente, nachvollziehbare Saves.
