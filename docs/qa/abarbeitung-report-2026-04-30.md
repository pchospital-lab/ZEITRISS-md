# Abarbeitung Report (30.04.2026) — Save/Merge/Dispatcher

## Ziel

Dieses Dokument übersetzt den Nachcheck in eine anschlussfähige Arbeitsliste.
Fokus: **Masterprompt + Wissensdateien** als einziges Laufzeitsystem in der
Chatoberfläche (inkl. Split/Merge über mehrere parallele Chats).


## In diesem Schritt erledigt

- **Persistenzvertrag geschärft (P0-1):** `core/sl-referenz.md` präzisiert,
  dass `campaign.mode` ausschließlich Persistenzstrategie (`mixed|preserve|trigger`)
  ist und Arena-Status über Runtime (`runtime_phase`) läuft.
- **`campaign.mode`-Härtung dokumentiert (P0-3):** PvP-/Arena-Passagen
  stellen jetzt explizit klar, dass kein `campaign.mode='pvp'` persistiert
  wird; Fallback bleibt `mixed` bei fehlendem `arena.previous_mode`.
- **Arena-Resume entschärft:** `arena.resume_token` ist als runtime-only markiert;
  HQ-Load erfolgt über den regulären Arena-Router statt Auto-Rejoin via Save.

## Offen (nächste Steps)

### P0 — Muss vor breitem Playtest

1. **Chargen-Save-Gate regressionssicher**  
   Klassisch immer:
   Chargenabschluss → HQ-Heimkehrbeat → Save-Angebot → erst danach Briefing.

2. **Persistenzvertrag repo-weit spiegeln**  
   Nach der Referenz-Härtung müssen die übrigen WS-Module denselben Vertrag
   (persistent vs. runtime-only) wortgleich tragen.

### P1 — Unmittelbar danach

3. **5er-Split/Merge-Matrix als QA-Standard**  
   Fälle 4/1, 3/2, Resplit, Konfliktfälle, deterministische Thread-IDs.

4. **Seed-Cap/Overflow beweisen**  
   Merge >12 Seeds mit erwartetem Overflow-Logging (Trace + Flags).

5. **Arena-/Rift-Transferhygiene**  
   Kein persistenter Auto-Rejoin-Drift; HQ-only Savepfad und Wallet-Trennung
   in Negativtests sichern.

### P2 — Nach Stabilisierung

6. **Chronopolis-Qualitätspass**  
   Spawn-Prioritäten, shared/roster echoes, Beat-Loop-Varianz dokumentiert
   testen.

## Übergabeformat für den nächsten Step

Der nächste Bearbeitungsschritt sollte immer:

1. diese Datei aktualisieren (Was erledigt / Was offen),
2. die betroffenen Wissensmodule synchron ändern,
3. `bash scripts/smoke.sh` laufen lassen,
4. bei QA-relevanten Änderungen die betroffenen Fixture-Dateien benennen.
