---
title: "Tester-Playtest-Briefing"
version: 2.0.0
tags: [meta]
---

# Tester-Playtest-Briefing

> Pflicht vor jedem externen Testlauf: den
> `internal/qa/process/playtest-readiness-gate.md` vollständig als
> Go/No-Go-Gate abarbeiten.

## Plattform

- **Nur Weg A testen:** OpenWebUI + OpenRouter
- Modell: `anthropic/claude-sonnet-4.6` (einziges Modell mit voller Regeltreue)
- Setup: `python scripts/setup.py` → Preset + 19 WS-Module + Masterprompt
- **Nicht Teil der QA-Basis:** Lumo (Plattform von Proton), ungetestete Plattformen (z. B. Claude Code), kleine lokale Modelle

## Testmatrix

### Solo-Tests

| Test                 | Eingabe                                     | Prüfpunkte                                       |
| -------------------- | ------------------------------------------- | ------------------------------------------------ |
| Quickstart           | `Spiel starten (solo schnell)`              | Summe 18, Cap 6, v7-Save, Ruf im Bogen           |
| Klassisch            | `Spiel starten (solo klassisch)`            | Chargen-Dialog, Attributverteilung, HQ-Intro     |
| Save/Load            | `!save` → neuer Chat → `Spiel laden` + JSON | Alle Werte erhalten, v7-Schema                   |
| Abschnittsrhythmus   | HQ-Runde + Mission in **getrennten Chats**  | Kein Mix, je Chat ein Abschnitt + Save dazwischen |
| Mission durchspielen | 12 Szenen, Debrief                          | Px-Staffel korrekt, Ruf + Lizenz-Tier im Debrief |
| Level-Up             | Nach Mission 1                              | Genau 1 Wahl: +1 Attr ODER Talent ODER +1 SYS    |

### Gruppen-Tests

| Test             | Eingabe                                      | Prüfpunkte                                       |
| ---------------- | -------------------------------------------- | ------------------------------------------------ |
| Gruppe erstellen | `Spiel starten (gruppe schnell)` + 2-5 Saves | characters[] Array, Host = Index 0               |
| Team-Split       | Nach Episode: Gruppe aufteilen               | Seeds korrekt zugewiesen, HQ-Pool aufgeteilt     |
| Separate Rifts   | Jedes Teilteam spielt Rift in eigenem Chat   | Unabhängige Saves, Artefakte, Level-Ups          |
| Team-Merge       | 2 Saves zusammenführen                       | Transparentes Merge-Protokoll, alle Chars intakt |

### Mechanik-Tests

| Test         | Prüfpunkte                                                           |
| ------------ | -------------------------------------------------------------------- |
| Würfelproben | `1W6 + ⌊Attr/2⌋ + Talent + Gear`, Exploding bei 6 (W6) / 10 (W10)    |
| Burst-Cap    | Max 1 Zusatzwurf pro Würfel, kein Ketten-Exploding                   |
| Heldenwürfel | Ab Attribut 14: W10 + Heldenwürfel (Reroll)                          |
| Px-Staffel   | TEMP 1-2: alle 2 Miss. +1 / 3-5: +1 / 6-8: +2 / 9-11: +2 / 12-14: +3 |
| Psi-Kosten   | Jede Kraft nennt PP UND SYS                                          |
| Artefakte    | Gate 1W6 (bei 6) → 1W14. TEMP ≥ 14: +2 → Mythic bei 15-16            |
| Ruf/Tier     | Debrief zeigt Ruf + Lizenz-Tier. Ruf +X = Tier X                     |

### Save-Schema v7

Prüfe bei jedem Save:

- `v: 7` (nicht `save_version: 6`)
- `characters[]` (nicht `character{}` + `party{}`)
- `attr` (nicht `attributes` mit SYS_max/runtime/used)
- `reputation` mit Fraktionswerten
- `economy.hq_pool` (nicht `economy.cu`)
- Keine Laufzeit-Daten (exfil, cooldowns, scene)
- Logs: 4 Arrays (trace, market, artifact_log, notes)

## Evidence dokumentieren

Playtest-Ergebnisse als Markdown unter `internal/qa/evidence/playtest-YYYY-MM-DD/`.
Pro Test eine Datei mit Modell, Szenario, Ergebnis und ggf. JSON-Save.

Vor dem ersten Testfall eines neuen Laufs immer zusätzlich den
Playtest-Readiness-Gate ausführen:

- `internal/qa/process/playtest-readiness-gate.md`

## CI-Smoke

```bash
bash scripts/smoke.sh
```

Muss vor jedem Push grün sein.

## Spielrhythmus (Pflicht-Check)

Der Gameflow-Rhythmus ist die zentrale Spieler-Devise — bei jedem Testlauf
mitprüfen, weil Drift hier alles andere unzuverlässig macht.

**Erwarteter Ablauf in jedem Solo- oder Gruppen-Lauf:**

```text
Chargen → !save → neuer Chat → Save laden
       → HQ-Runde → !save → neuer Chat → Save laden
       → Briefing + Mission + Debrief → !save → neuer Chat → Save laden
       → HQ-Runde → !save → neuer Chat → Save laden
       → ...
```

**Acht Sync-Punkte (Pflicht-Check pro Punkt):**

| Sync-Punkt | Erwarteter In-Fiction-Beat | Erwartete Folge |
| --- | --- | --- |
| Charaktererschaffung → HQ-Hub | Heimkehr-Beat (Quarzatrium, Dienstpersonal) | Chargen-Save-Gate, kein Auto-Briefing |
| HQ → Briefing (Core) | Sprungvorbereitung an Sync-Station | `!save` → Chat-Wechsel-Verweis |
| HQ → Briefing (Rift) | Rift-Koordinate aktiviert + Sprungvorbereitung | `!save` → Chat-Wechsel-Verweis |
| HQ → Chronopolis-Schleuse | Schleuse verriegelt, rotes Statuslicht | `!save` → Chat-Wechsel-Verweis |
| HQ → Arena-Match | Arena-Lobby Match-Lock | `!save` → Chat-Wechsel-Verweis |
| Standard-Debrief → HQ | Nullzeit-Andocken | `!save` nach Score-Screen + Level-Up |
| Chronopolis-Debrief → HQ | Schleuse entriegelt | `!save` → Chat-Wechsel-Verweis |
| Arena-Debrief → HQ | Match-Recap eingehängt | `!save` nach `banked_rewards` |

**Generelle Prüfpunkte:**

- An jedem Sync-Punkt erscheint der Sync-Beat **bevor** der Übergang
  abgeschlossen wird. KI-SL darf **nicht** ohne Sync-Beat den Übergang
  durchführen.
- Tippt der Tester nach `!save` im selben Chat einen Übergangsbefehl
  („Briefing", „Arena", „Chronopolis betreten", „weiter ins HQ"), muss die
  KI-SL freundlich auf den nächsten Chat verweisen — **kein** Briefing,
  kein Match-Start, keine Schleuse, keine Mission im selben Chat nach Save.
- Im neuen Chat nach Save-Load erscheint **immer** der HQ-Hub-Router mit
  Wahl-Optionen (Briefing anfordern / HQ erkunden / Schnell-HQ /
  Chronopolis-Schleuse / Rift-Board / Arena-Router). Auch wenn der
  Spieler-Opener bereits einen Übergang nennt, wird der Router gezeigt
  (kann transparent durchspringen).
- Equipment-Änderungen, Implantate, Wallet-Bewegungen aus einer HQ-Runde
  müssen im danach erstellten Save sichtbar sein und beim nächsten
  Mission-Load korrekt geladen werden.
- Fast-Lane (`solo schnell` / `gruppe schnell`) ist Sonderfall: kein
  Chargen-Sync, erstes Save-Angebot erst nach Mission 1.

**Drift-Hinweise (alles unten ist ein Regress, in Findings festhalten):**

- KI-SL führt Übergang ohne Sync-Beat durch (z. B. springt direkt ins
  Briefing nach Debrief, ohne Heimkehr-Beat + Save-Angebot).
- KI-SL bietet im selben Chat nach `!save` einen weiteren Übergang an
  (z. B. „okay, jetzt das Briefing für die nächste Mission?").
- HQ-Hub-Router fehlt im neuen Chat nach Save-Load.
- Auto-Equip zwischen Mission und Mission im selben Chat angeboten
  (alter Pre-2026-05-Drift).
- KI-SL sagt „du kannst direkt weiter ins Briefing" ohne Sync-Beat
  (Verstoß gegen die
  [Save-Taktung](../../core/sl-referenz.md#save-taktung-verbindlich)).
- Sync-Beat ist nur ein nüchternes „!save?" ohne Lore-Verankerung
  (Sync-Station/Schleuse/Arena-Lobby/Heimkehr-Andocken). Das ist ein
  UX-Regress, kein harter Bug — aber reporten.

Spieler-Doku: [Der Gameflow][gameflow-spieler]. SL-/Toolkit-Pflichten:
[Save-Prompts im HQ-Flow][modul12].

[gameflow-spieler]: ../../core/spieler-handbuch.md#gameflow-chat-wechsel
[modul12]: ../../systems/gameflow/speicher-fortsetzung.md#save-sync-handover
