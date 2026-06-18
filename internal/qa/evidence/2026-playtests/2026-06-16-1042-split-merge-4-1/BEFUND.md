# Befund — 5er-Split/Merge Case 4/1 (Mechanik-Canary, Variante A)

**Datum:** 2026-06-16 10:42–10:50
**Harness:** `playtests/zeitriss/harness/split_merge.py --case 4-1`
**SL:** `zeitriss-v426-uncut` (OWUI, #3228-Stand), Anker-Fixture `savegame_v7_5er_hq_highlevel.json`
**Kosten:** $0.63 (echt, OWUI `usage.cost`), 90% Ø Cache-Hit, Peak 64990 Prompt-Tokens (6,5% von 1M)
**Verdict (nach Quellenprüfung):** ✅ **PASS** — 0 harte Fehler, 3 SOFT-Befunde

---

## Was getestet wurde

Kanonischer 4/1-Split an Sync-Punkten (kein organisches Spiel):
5er-HQ-Save laden → Split (4er Squad / 1er Solo) → beide Branches in eigenen
Chats kurz spielen + `!save` → beide Ergebnis-Saves im Merge-Chat zusammenführen.
Gescriptete Spieler-Eingaben (deterministisch, isoliert die SL-Merge-Mechanik).

## Was die SL RICHTIG gemacht hat (verifiziert gegen Save-Output)

- **Split-Beat mustergültig:** Sync-Station-Lore, Mira als NPC, `family_id=SPLIT-EP12-MS10-KAIROS`, zwei Threads `SQUAD-ABCD`/`SOLO-E` sauber benannt, Save-Angebot + Chat-Wechsel-Hinweis.
- **Proaktive Fragment-Erkennung:** SL meldete selbst, dass der Anker-Save keine `attr/talents/equipment/level_history`-Blöcke trägt (Fixture ist Fragment) — transparent statt still halluziniert.
- **Konvergenz korrekt:** Merge-Save hat `resolved_threads=[SQUAD-ABCD, SOLO-E]`, `convergence_ready=true`, `family_id` durchgängig, `thread_id=MAIN`, `merge_id` gesetzt.
- **Persönliche Wahrheit getragen:** Alle 5 Wallets (7200/6900/8100/7600/7050) über Split+Merge intakt; alle 5 Charaktere im Merge.
- **Invarianten gehalten:** `px=3` stabil über ganzen Zyklus (keine Px-Reanimation), `px_state=stable`, `heat=0` korrekt als Default ergänzt, `shared_echoes` korrekt als Objekte mit `tag` (Konvergenz-Echo gesetzt).
- **Dedupe-Guards gesetzt:** `duplicate_branch_detected=false`, `duplicate_character_detected=false`.
- **Level-Diskrepanz quittiert:** SL erkannte „Lvl 901–933 aber level_history leer" und protokollierte es als `continuity_conflict` mit Spieler-Quittung statt still zu überschreiben.

## Datensatz-vs-Dev-Check

- **Datensatz-Relevanz:** ja — betrifft Masterprompt/Modul 12 (Save-Merge-Logik).
- **Nur Dev/QA:** nein. Echter Runtime-Pfad.
- **WS-Spiegelpflicht:** ja, falls Fix gewollt → `systems/gameflow/speicher-fortsetzung.md` (§Save-Sync-Handover / §Cross-Mode-Import) + ggf. Masterprompt §F.
- **Invarianten betroffen:** nein (Save v7 / Boss-Timing / Szenen-Count alle unberührt).

## SOFT-Befund 1 (echt, einziger Sach-Befund): HQ-Pool-Leck über Split/Merge

**Beobachtung:** `economy.hq_pool` 53200 (Anker) → Split halbiert auf 2× 26600
→ Merge bleibt 26600. Pro Split/Merge-Zyklus verliert die Crew **50% des
gemeinsamen Topfs**.

**Ursache (verifiziert im SL-Text):**
- Split: `Kodex: HQ-Pool 53200 CU hälftig aufgeteilt — je 26600` (sinnvoll).
- Merge: `Merge-Delta HQ-Pool: beide Branches 26600 CU — kein Konflikt, Wert übernommen`.

**Bewertung:** Die SL handelt **kanonisch korrekt** nach der Session-Anker-Regel
(„`economy.hq_pool` bleibt ankergeführt", Modul 12 §Cross-Mode-Import). Diese
Regel ist aber für **Lobby-Betrieb** gedacht (fremde Spieler stapeln Saves,
einer setzt den Anker), **nicht für Split/Merge derselben Crew**, wo der Topf
vorher bewusst geteilt wurde und beim Wiedervereinen additiv rekonstituiert
werden müsste (26600 + 26600 = 53200).

**Lücke:** Modul 12 hat **keine explizite Regel**, dass ein zuvor gesplitteter
`hq_pool` beim Merge wieder addiert wird. Die Anker-Regel greift fälschlich auch
hier. → Design-/Doku-Entscheidung für Flo: Soll der gemeinsame Topf beim
Crew-Merge additiv rekonstituiert werden (separat von der Lobby-Anker-Regel)?

**Fix-Vorschlag (wenn gewollt):** In §Save-Sync-Handover / §Cross-Mode-Import
eine Sonderregel für **Crew-Split-Merge** (gleiche `family_id`): `hq_pool` der
Branches **summieren** statt ankergeführt zu übernehmen — abgegrenzt vom
Lobby-Fall (fremde `family_id`/kein Split → Anker führt weiter).

## SOFT-Befund 2: imported_saves als String-Array

Merge-Save führt `logs.flags.imported_saves` als String-Array (`["SAVE-...",
...]`) statt der kanonischen Objektform `[{save_id, branch_id, status}]`
(Modul 12 §Lineage & Dedupe). Info ist da, Format nicht-kanonisch. Niedrige Prio.

## SOFT-Befund 3: Anker führt nicht (Folge von Befund 1)

`hq_pool 26600 != Anker 53200` — direkte Folge des Split-Halbierens; kein
eigenständiger Befund.

## Validator-Lernpunkte (Harness-Fixes, bereits umgesetzt)

- **CONVERGE-Match gegen `thread_id`, nicht `branch_id`:** Die SL führt
  `thread_id` als Thread-Identität (`SQUAD-ABCD`), `branch_id` als Lineage-Anker
  (`SPLIT-...-SQUAD`). Erste Validator-Version verglich falsch → 2 FALSCH-FAILs.
  Gefixt in `merge_assert.py` (assert_merge zieht jetzt Branch-`thread_id`).
- **Beat-Heuristik zu eng:** suchte „spaltet/teilt euch", SL schrieb
  „Split-Protokoll/Branch-Trennung/Sync-Station". Gefixt in `split_merge.py`.
- **imported_saves String-Array = SOFT, nicht FAIL.**

## Nächster Schritt

Variante B (organischer Persona-Lauf) erst nach erneutem Preflight inkl.
Token-Last-Test (G3: künstlich langes History-Array, nicht Turn 80 live).
Restliche P1-Matrix (3/2-Rejoin, Resplit 3→2/1, Konfliktfall, Seed-Cap) mit
demselben Harness erweiterbar.
