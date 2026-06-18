# Befund — Variante B Schritt 2: Organischer 5er-Lauf (Wallet-SSOT im Fluss)

**Run:** `runs/2026-06-16-1809-phase3-5er-wallet`
**Harness:** `group-harness.py --phase 3` (NEU, organischer 5er aus HQ-Anker)
**Datum:** 2026-06-16 18:09–18:30 (24 Turns, Mission EP12/MS10 komplett bis Debrief + EP13/MS1-Start)
**SL-Modell:** `zeitriss-v426-uncut` (Preset = Repo-HEAD `2e9f5cdf`, MP byte-identisch verifiziert)

## ⚠️ Preflight-Nachtrag (18:40) — voller Launcher-Verify nachgeholt

**Methodenfehler beim Lauf:** Ich hatte VOR dem Lauf nur den MP-Byte-Diff manuell
verifiziert, NICHT den vollen Launcher-`[4] Aktualisieren`-Lauf (git pull + run_sync
+ Coverage-Check). Flo zu Recht moniert: der Launcher prüft zusätzlich hart, ob
ALLE 19 KB-Module wirklich als File-Entity in der KB liegen (`meta.collection_name
== kb_id`), nicht nur der Masterprompt.

**Nachgeholt (Launcher [4], LAUNCHER_GIT=ghrepo, OWUI_UPLOAD_TIMEOUT=300):**
- Repo war schon aktuell (kein Pull nötig).
- **Masterprompt synchron** (MD5 5053679b — identisch mit manuellem Diff). ✓
- **Alle 19 KB-Dateien laut Manifest synchron.** ✓
- **Coverage-Check: 19/19 Dateien nachweisbar in der KB.** ✓

**Konsequenz:** Der Lauf oben ist damit **100 % aussagekräftig** — Preset, MP UND
vollständige KB waren beim Lauf korrekt geladen. (Selbst ohne diese Bestätigung
hätte fast alles geklappt, was zeigt wie robust der Stand ist — aber jetzt ist es
bewiesen statt vermutet.)
**Spieler:** 5 Persona-Sub-Agents (Sonnet 4.6) auf den fixen Anker-Charakteren
**Peak-Prompt:** 101.236 Tokens = **39,5 %** von Sonnets 256k → unkritisch

## Verdict: **PASS** — Wallet-SSOT spielt sich im 5er organisch sauber.

Die heute gemergten Patches (#3230 Wallet-SSOT, #3232 research.status, #3233
tier-Elimination) sind damit erstmals im **echten organischen Mehrspieler-Lauf**
live bestätigt, nicht nur über gescriptete Canaries.

---

## Die vier Ziel-Beats (NEXT.md a/b/c/d)

### (a) Kauf aus eigenem Wallet — ✓ BESTÄTIGT, mehrfach
- Blitz kauft Sturmkarabiner Mk-9 (T3) + Verbundpanzer (T3) für **800 CU** aus
  seinem Wallet: `8.900 → 8.100 CU`. Sauber abgebucht, korrekt verbucht.
- Echo kauft Med-Patch + Rauchgranate (80 CU): `9.050 → 8.970`.
- Cipher kauft Kamera-Jammer + Override-Kit (400 CU) im Missionsverlauf.
- **Jeder zahlt aus SEINEM Wallet** — kein Sammeltopf, exakt Wallet-SSOT-konform.

### (a-fail) Unterdeckungs-Scheitern — ⚠️ NICHT GEZÜNDET (erklärbar, kein Mangel)
- Trat organisch nicht auf, weil die SL **proaktiv und korrekt** vorrechnete:
  Blitz' 6.900 CU reichen für T3-Gear (600–900 CU) locker. Es kam nie zu einem
  Kaufversuch über Wallet-Deckung. Das ist **richtiges SL-Verhalten** (warnt
  vorher), nicht ein ungetesteter Pfad.
- **Restpunkt:** Das harte Scheitern ("Nicht genug CU im Wallet") bleibt nur über
  den gescripteten `split_merge`-Canary belegt, nicht organisch. Optional gezielt
  provozierbar (Persona mit teurem Wunsch + sehr klammem Wallet), aber niedrige
  Prio — die Mechanik selbst ist im Modul + Canary bewiesen.

### (b) CU-Übergabe (Wallet→Wallet) — ✓ BESTÄTIGT, Kern-Highlight
- Astra (reich, 60.400) gleicht die Crew organisch aus:
  - `Astra → Blitz: 2.000 CU` (60.400 → 58.400 / Blitz 6.900 → 8.900)
  - `Astra → Cipher: 2.000`, `Astra → Dusk: 2.000`, `Astra → Echo: 2.000`
    (Astra 58.400 → 52.400; alle Empfänger korrekt +2.000)
- Ausgelöst aus **natürlicher Sprache** (Astra bot von sich aus an, SL setzte um) —
  exakt der Modul-15-Pfad "Nova gibt Ghost 400 CU". `!uebergabe`-Befehlsform wurde
  nicht explizit getippt, aber der natürlichsprachige Weg (der häufigere) ist
  live bestätigt.
- **Geld-Konservierung exakt:** Σ Start 90.050 → Σ final 89.170 = 90.050 − 880
  (Sinks: Blitz 800 + Echo 80). Transfers verschieben nur, Käufe sind die einzigen
  Abflüsse. **Kein Leck, keine Inflation** — der ganze Sinn der hq_pool-Abschaffung
  hält im organischen Fluss.

### (c) Gruppenkasse-Σ-View — ⚠️ SOFT-BEFUND (echte Lücke)
- Die SL zeigt die Wallets **immer einzeln aufgelistet**
  (`Astra — 52.400 · Blitz — 8.100 · Cipher — 10.100 · …`), aber **nie die
  berechnete Summe als "Gruppenkasse: X CU"**.
- Modul 15 (`cu-waehrungssystem.md` Z55-56, Beispiel Z116) UND `sl-referenz.md`
  (Z1003, Z1265-1266) sehen die **Gruppenkasse als expliziten Σ-View** vor
  ("Wallet Nova: 1250 CU | Wallet Ghost: 1900 CU | **Gruppenkasse: 3150 CU**").
- Cipher (Buchhalter-Persona) fragte 2× aktiv nach dem Gesamtüberblick — die SL
  antwortete jedes Mal mit der Einzelliste statt der Summe. Funktional nicht
  falsch (die Zahlen sind alle da), aber der vorgesehene Σ-Komfort fehlt.
- **Kandidat für kleinen Masterprompt-/Modul-Patch:** Wallet-Auflistung soll die
  Summenzeile "Gruppenkasse: Σ CU" mitführen, wenn >1 Charakter. Niedrige Prio,
  reine UX. (Vor Patch: kurz prüfen, ob der MP die Summen-Anzeige schon irgendwo
  vorschreibt und die SL sie nur überging, oder ob die Regel fehlt.)

### (d) Split/Merge im Fluss — ⊘ NICHT TEIL DIESES LAUFS
- Die Crew blieb als 5er zusammen (eine Mission, kein Split). Split/Merge-Mechanik
  ist über die P1-Matrix (gescriptet) bereits bewiesen; ein organischer Split-Lauf
  wäre ein eigenes Szenario. Kein Blocker.

---

## Nebenbefunde (positiv, live bestätigt)

- **research.status = `in_progress`** (Patch #3232): SL schrieb beim neuen
  Research-Projekt "Anker-Null / Omega-Stempel" korrekt `status: in_progress`,
  später `status: ready`. Kein ungültiges "active" mehr. ✓
- **research OHNE tier** (Patch #3233): Research-Projekt nutzt `missions_done: 0/1`
  bzw. `missions_total`, **kein tier-Feld**. ✓
- **Px-5-Loop:** Mission → Px 5/5 → ClusterCreate → 2 Rift-Seeds → Px-Reset 0. ✓
- **Debrief-Wallet-Split:** Basis 800 CU/Agent korrekt auf alle 5 characters[].wallet
  gebucht. ✓
- **Concealment/Spielgefühl:** Boss-Mission MS10 lief filmisch, Crew koordinierte
  organisch (Override-Kit, Jammer, Tarnung), kein Café-Vorlauf. ✓

## Token/Performance
- Peak 101k Prompt (39,5 % von 256k), Ø 36,6 s/Turn. 5er-Vollmission gut im grünen
  Bereich — bestätigt die G3-Probe (87k) mit realem History-Wachstum.

## Offene Folge-Punkte
1. **(c) Σ-View-Patch** (Gruppenkasse-Summenzeile) — kleiner MP/Modul-Fix, niedrige Prio.
2. **(a-fail)** organisches Unterdeckungs-Scheitern — optional, Mechanik bereits via Canary belegt.
3. **(b) `!uebergabe`-Befehlsform** (statt nur natürliche Sprache) — optional explizit nachfahren.
