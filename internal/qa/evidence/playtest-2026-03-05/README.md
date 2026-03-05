# Playtest-Evidence 2026-03-05: Save-Schema v7

**Modell:** Sonnet 4.6 via OpenWebUI + OpenRouter
**Kontext:** Vollständiges Regelwerk-Audit (53 Issues, 9 Spielbrecher) + Schema-Redesign v6→v7

## Tests durchgeführt

| # | Test | Ergebnis | Datei |
|---|------|----------|-------|
| 00 | Solo Quickstart + Save | ✅ PASS | `00-solo-quickstart-sonnet46.md` |
| 01 | 5er-Gruppe: Erstellung, Split, Merge | ✅ PASS | `01-5er-gruppe-split-merge.md` |
| 02 | Merge-Ergebnis (vollständiger JSON) | ✅ PASS | `02-merge-result-sonnet46.md` |

## Was getestet wurde

1. **Solo-Quickstart** — Chargen mit v7-Schema, `!save` gibt korrektes JSON
2. **5er-Gruppen-Erstellung** — 5 Chars, Summe 18, Cap 6, Reputation, Psi-Gate
3. **Team-Split** — 5er → 3er (Rift 1347) + 2er (Rift 2089), Seeds zugewiesen
4. **Separate Rift-Ops** — Beide Teams spielen unabhängig, Level-Ups, Artefakte
5. **Team-Merge** — 3er + 2er → 5er, transparentes Merge-Protokoll

## Kernergebnis

Das v7-Schema funktioniert durchgehend. Die KI-SL (Sonnet 4.6):
- Gibt konsistente v7-Saves aus
- Splittet sauber mit transparenter Dokumentation
- Mergt mit nachvollziehbarer Entscheidungstabelle
- Transportiert Verwundungen, Artefakte, Psi-Progression, Reputation korrekt

**Kein einziger Spielbrecher gefunden.**
