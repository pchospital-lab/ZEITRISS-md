# ZEITRISS Agentenpaket — Nachcheck Bio-/Grundform-Feeling & PvP-Progression

**Datum:** 2026-04-28  
**Zielbranch:** `fix/pvp-progression-bio-grundform`  
**Review-Typ:** Statischer Repo-/Raw-Review + gedankliche Playtest-Simulation  
**Primärfokus:** Charaktergefühl/Biohüllen, PvP als vollwertiger Progressionspfad, Save-/Abschnittslogik an PvP- und HQ-Grenzen

---

## 0. Executive Summary

Der Gameflow ist inzwischen sehr stark: HQ als Ruhehafen, Abschnitte als instanzierte Runs, Save nur in sicheren HQ-Phasen, neuer Chat als „Ladebildschirm“, JSON als Weltanker. Die große Architektur trägt.

Die wichtigsten Reststellen vor den nächsten Playtests liegen nicht mehr im CoreOps-Grundgerüst, sondern in drei scharf umrissenen Bereichen:

1. **Charaktergefühl:** Die aktuelle Spielerfassung spricht an mehreren Stellen noch wie ein altes Fantasy-/Isekai-System: `Bio-Hülle`, `Spezies`, `Rasse`, `Rassenmods`, „Bewusstsein in Hülle“. Das ist mechanisch verständlich, aber tonal falsch. ZEITRISS sollte player-facing sagen: **Du spielst einen echten, physischen huminen Menschenkörper / eine humine Grundform.** Biohülle ist höchstens ITI-Laborjargon, kein Menüpunkt und keine Rasse.

2. **PvP als vollwertiger Weg:** Der Arena/PvP-Block ist atmosphärisch gut, aber als alleiniger Progressionspfad noch nicht fertig. Aktuell ist PvP eher CU-/Ruf-/Bonus-Content. Gleichzeitig gibt es Drift: Eine Datei sagt „Arena gibt kein Px“, andere Logik spricht von Px-Boni oder erhöht sogar Paradoxon. Für Flo ist aber wichtig: **Wer nur PvP spielt, muss genauso episch leveln können wie CoreOps/RiftOps/Chronopolis-Spieler.** Dafür braucht ZEITRISS einen klaren Arena-XP-/Training-XP-Vertrag plus Cashout-/Push-your-luck-Schleife.

3. **Restdrift an Save-/PvP-Grenzen:** Der strikte Export verlangt `ui.action_mode`, das Masterprompt-Savetemplate zeigt es nicht. Einige PvP-Reset-Fälle fallen noch auf `preserve` zurück, obwohl `mixed` der sichere Startstandard sein soll. Diese Driftstellen greifen genau an den Übergängen an, wo die MMO-Illusion stehen oder fallen wird.

**Empfohlene Reihenfolge:**

1. P0/P1 in diesem Paket patchen.
2. Erst danach den großen PvP-Only-Playtest fahren.
3. Danach RiftOps, dann Chronopolis, dann Cross-Mode-Merge.

---

## 1. Review-Scope

Geprüfte Kernbereiche:

- `meta/masterprompt_v6.md`
- `systems/gameflow/speicher-fortsetzung.md`
- `systems/gameflow/saveGame.v7.schema.json`
- `systems/gameflow/saveGame.v7.export.schema.json`
- `systems/gameflow/cinematic-start.md`
- `characters/charaktererschaffung-grundlagen.md`
- `characters/charaktererschaffung-optionen.md`
- `systems/kp-kraefte-psi.md`
- `gameplay/kampagnenstruktur.md`
- `core/sl-referenz.md`
- `core/spieler-handbuch.md`
- `core/zeitriss-core.md`
- `runtime.js` als Mirror/Test-Hinweis, **nicht** als Kanon
- `README.md` als Pitch-/Öffentlichkeitsdokument
- `AGENTS.md` als Arbeitsregel

Wichtig: `AGENTS.md` sagt korrekt, dass Spielkanon in Masterprompt/Wissensmodulen lebt und `runtime.js` nicht eigenständige Spiellogik sein darf. Alle Patches sollten also primär in Masterprompt/WS-Dateien landen; Runtime darf danach nur synchronisiert werden.

---

## 2. Ampelbild

| Bereich | Status | Bewertung |
|---|---:|---|
| HQ als Ruhehafen | Grün | Das System wirkt jetzt klar: HQ ist savebar, frei ausspielbar, Router für Core/Rift/Chronopolis/PvP. |
| Neuer Chat pro Abschnitt | Grün | Das Design stützt die Illusion „MMO ohne Server“ sehr gut. |
| Klassischer Start | Grün | `cinematic-start.md` trägt inzwischen Chargen-Save-Gate und kein Auto-Briefing. |
| Bio-/Körpergefühl | Gelb-Rot | Mechanisch okay, aber player-facing noch zu sehr „Hülle/Rasse/Spezies“. Muss emotional sauberer werden. |
| Psi als Magie-Ersatz | Grün-Gelb | Inhaltlich gut. Sollte in Charaktererschaffung player-facing stärker formuliert werden. |
| PvP als Modus | Gelb | Arena-Loop ist da, aber Progression/Cashout/Anti-Grind brauchen scharfen Vertrag. |
| PvP-only Karriere | Rot | Noch nicht gleichwertig zu Core/Rift, wenn PvP keine XP/Level-Missionäquivalenz gibt. |
| PvP ↔ Save/HQ | Gelb | SaveGuard gut, aber Reset-Fallback und persistente Felder noch driftgefährdet. |
| Strict Save Export | Gelb | Export-Schema ist stark, aber Masterprompt-Template fehlt `ui.action_mode`. |
| Öffentliches README | Gelb | Pitch stark, aber HUD-Beispiel mit `4/10` wirkt wie alter XP-Balken. |

---

## 3. P0 — Muss vor dem PvP-Playtest

### P0-01 — PvP darf kein Paradoxon/Px vergeben; Runtime und SL-Sprache widersprechen dem Kanon

**Betroffene Dateien:**

- `gameplay/kampagnenstruktur.md`
- `core/sl-referenz.md`
- `runtime.js`
- ggf. Tests/Fixtures

**Problem:**

Der PvP-/Arena-Kanon sagt an einer Stelle klar:

- Arena vergibt **kein Px**.
- Arena verändert `campaign.px` **nie**.

Gleichzeitig tauchen in SL-/Runtime-Logik noch Begriffe wie `Px-Boni` auf, und `runtime.js` erhöht beim Arena-Sieg sogar Paradoxon/Px. Das ist extrem gefährlich, weil Px im ZEITRISS-Loop nicht irgendein Bonus ist, sondern RiftOps/Paradoxon/Seed-Ökonomie steuert.

**Patch:**

- In `core/sl-referenz.md`: `Px-Boni pro Episode` ersetzen durch `Arena-Boni pro Arena-Contract/Arena-Season` oder `Arena-Reward-Stempel`.
- In `runtime.js`: `incrementParadoxon(1)` im Arena-Exit entfernen. Keine Mutation von `campaign.px` durch Arena.
- Alle Toasts/Erzähltexte von `Px-Bonus` auf `Arena-Bonus`, `Ladder-Bonus`, `Training-XP` oder `Ruf-Bonus` umstellen.
- In Tests prüfen: Nach PvP-Sieg bleibt `campaign.px` identisch.

**Akzeptanztest:**

1. Spieler startet mit `campaign.px = 4`.
2. Spieler gewinnt eine PvP-Serie.
3. Spieler casht aus.
4. Export-Save zeigt weiterhin `campaign.px = 4`.
5. Eventuell erhaltene Progression steht in `xp`/`arena.training_xp`/`arena.reward_log`, nicht in Px.

---

### P0-02 — PvP-only braucht einen vollwertigen Progressionsvertrag

**Betroffene Dateien:**

- `gameplay/kampagnenstruktur.md`
- `core/sl-referenz.md`
- `core/spieler-handbuch.md`
- `meta/masterprompt_v6.md`
- `systems/gameflow/speicher-fortsetzung.md`
- `saveGame.v7.export.schema.json` nur falls neue persistente Felder nötig sind

**Problem:**

Das aktuelle Arena-Design belohnt CU/Ruf/Multiplikatoren, aber es gibt keinen sauberen Vertrag, wie ein Spieler, der **ausschließlich PvP** spielt, Level, Builds und epische Charakterentwicklung erhält. Damit wäre PvP zwar ein Modus, aber kein gleichwertiger Lebensweg.

Flo-Ziel:

> Jemand, der nur PvP spielt, soll sich genauso einen epischen Char hochspielen können wie auf allen anderen Wegen.

**Patch: Arena-Progressionsvertrag einführen.**

Empfohlene kanonische Regel:

```text
PvP/Arena vergibt niemals Px und niemals Rift-Seeds.
PvP/Arena kann aber Training-XP / Arena-XP / Missionäquivalenz vergeben.
Gebankte Arena-Runs zählen als offizieller Progressionspfad.
Level-Ups laufen immer über dieselbe Level-History-One-Choice-Regel wie Core/Rift.
```

**Konkretes Modell:**

- Phase 1, Level 1–10:
  - Ein erfolgreich gebankter Arena-Run zählt als **1 Missionsäquivalent**.
  - Alternativ, wenn langsamer gewünscht: 2 gebankte Arena-Siege = 1 Missionsäquivalent.
  - Wichtig: Der Agent soll eine Variante wählen und überall konsistent verankern.
- Phase 2, ab Level 11:
  - Gebankte Arena-Runs geben `arena_xp` oder normale `xp` nach Tierformel.
  - Level-Up weiter über bestehende XP-Tabelle.
- `level_history` schreibt Arena-Herkunft sauber:

```json
"level_history": {
  "7": {
    "choice": "talent:+1 Reaktion",
    "detail": "PvP Ladder Cashout, Arena-Season 2, Run 4",
    "source": "ARENA-S2-R4"
  }
}
```

**Nicht erlaubt:**

- Kein Px.
- Keine Rift-Seeds.
- Keine Artefakt-Farm durch Arena.
- Kein Umgehen der Level-Up-One-Choice-Regel.

**Akzeptanztest:**

Ein L1-Charakter spielt fünf HQ→PvP→HQ-Zyklen, nie Core/Rift. Erwartung:

- Charakter erhält sichtbare Arena-Karriere.
- Level-Up ist möglich.
- `level_history` ist vollständig.
- `campaign.px` bleibt unverändert.
- Save bleibt strict export-valid.

---

### P0-03 — Arena braucht die motivierende „Noch eine Runde oder Bonus sichern?“-Schleife als Kanon

**Betroffene Dateien:**

- `gameplay/kampagnenstruktur.md`
- `core/sl-referenz.md`
- `core/spieler-handbuch.md`
- `meta/masterprompt_v6.md`

**Problem:**

Es gibt bereits Revanche/Best-of-Three/Cashout-Ansätze, aber die Push-your-luck-Ökonomie ist noch nicht als harte, erzählerisch wiederholbare Schleife formuliert. Genau diese Schleife soll PvP süchtig/spannend machen.

**Patch: Arena-Run als Bank-/Pending-System definieren.**

Empfohlene Regel:

```text
Eine Arena-Session startet im HQ und wird als Arena-Run gespielt.
Ein Arena-Run besteht aus einer oder mehreren Serien.
Nach jeder gewonnenen Serie entscheidet die Gruppe:
A) Cashout: pending Rewards werden gebankt, HQ-Rückkehr, Save möglich.
B) Push: neue Serie / höherer Einsatz / Revanche; pending Rewards steigen, Risiko steigt.
Bei Niederlage werden pending Bonus-Rewards verbrannt oder stark reduziert; Basis-/Trostprogression bleibt begrenzt möglich.
```

**Datenmodell minimal:**

```json
"arena": {
  "mode": "idle|queued|matched|staging|active|cashout",
  "season": 2,
  "contract_id": "A-S2-C04",
  "ladder_tier": "bronze|silver|gold|rifted|legend",
  "streak": 2,
  "pending_rewards": {
    "cu": 240,
    "ruf": 3,
    "training_xp": 1,
    "multiplier": 1.5
  },
  "banked_this_contract": {
    "cu": 480,
    "ruf": 5,
    "training_xp": 2
  }
}
```

**Persistenzregel:**

- Während aktiver Arena: Save blockiert oder nur Resume-Token.
- Nach Cashout/HQ: Nur gebankte Rewards persistieren.
- Pending Rewards dürfen im Resume-Token stehen, aber nicht als fertig gebankte Weltwahrheit.

**Akzeptanztest:**

1. Gruppe gewinnt Serie 1.
2. HUD zeigt `Pending: 120 CU / 1 Ruf / 1 Training-XP · Cashout möglich`.
3. Gruppe pusht.
4. Gruppe verliert Serie 2.
5. Pending-Bonus wird nach Regel reduziert/verbrannt.
6. Gruppe kehrt ins HQ zurück.
7. Save ist möglich, aber nur mit final gebankten Rewards.

---

### P0-04 — Strict Export: Masterprompt-Savetemplate muss `ui.action_mode` enthalten

**Betroffene Dateien:**

- `meta/masterprompt_v6.md`
- ggf. Save-Beispiele in Docs/Fixtures

**Problem:**

Das strikte Export-Schema verlangt im `ui`-Block unter anderem:

- `gm_style`
- `suggest_mode`
- `action_mode`
- `contrast`
- `badge_density`
- `output_pace`
- `voice_profile`

Das Masterprompt-Savetemplate zeigt aber aktuell keinen `action_mode`-Wert. Die Fortsetzungslogik normalisiert `action_mode` zwar, aber der kanonische Export sollte das Feld direkt enthalten.

**Patch:**

Masterprompt-Save-Template auf sieben UI-Felder ergänzen:

```json
"ui": {
  "gm_style": "verbose",
  "suggest_mode": false,
  "action_mode": "uncut",
  "contrast": "standard",
  "badge_density": "standard",
  "output_pace": "normal",
  "voice_profile": "gm_second_person"
}
```

**Akzeptanztest:**

- `!save` erzeugt strict-export-valid JSON.
- Kein Save-Beispiel ohne `ui.action_mode` bleibt übrig.

---

### P0-05 — PvP-Mode-Fallback darf nicht auf `preserve` kippen

**Betroffene Dateien:**

- `systems/gameflow/speicher-fortsetzung.md`
- `gameplay/kampagnenstruktur.md`
- `core/sl-referenz.md`
- `runtime.js` als Mirror

**Problem:**

Es gibt noch Legacy-Formulierungen: Wenn `previous_mode` fehlt, fällt der Arena-Reset auf `preserve` zurück. Das ist gefährlich, weil `preserve` ein spezifischer Kampagnenpool ist, nicht der sichere neutrale Startzustand.

**Patch:**

- Fallback immer `mixed`, nicht `preserve`.
- Persistenter Export darf `campaign.mode` nur `mixed|preserve|trigger` enthalten.
- `pvp` ist Runtime-/Arena-Zustand, kein persistenter Kampagnenpool.

**Akzeptanztest:**

1. Save wird aus Arena-Fehlerzustand geladen, `previous_mode` fehlt.
2. System setzt `campaign.mode = "mixed"`.
3. `arena.mode = "idle"` oder Resume-Token wird korrekt angeboten.
4. Strict Export enthält niemals `campaign.mode = "pvp"`.

---

## 4. P1 — Charaktergefühl / Biohüllen-Reframe

### P1-01 — Player-facing weg von `Bio-Hülle`, `Spezies`, `Rasse`

**Betroffene Dateien:**

- `characters/charaktererschaffung-grundlagen.md`
- `characters/charaktererschaffung-optionen.md`
- `core/spieler-handbuch.md`
- `meta/masterprompt_v6.md` optional als Stilregel

**Problem:**

Derzeit liest sich die Charaktererschaffung stellenweise so, als wähle man eine Fantasy-Rasse oder als sei der Körper nur ein Container:

- `Spezies oder Bio-Hülle wählen`
- `Rasse`
- `Rassenmods`
- `Bio-Sheaths`
- `temporäre Hüllen`
- `Bewusstsein ... in Hülle`

Das ist mechanisch logisch, aber es beschädigt das gewünschte Gefühl: ZEITRISS soll nicht nach Ork/Zwerg/Elf klingen, sondern nach **huminen Varianten echter Körperlichkeit**.

**Patchsprache:**

Empfohlene player-facing Begriffe:

| Alt | Neu |
|---|---|
| Rasse | Grundform / Körperprofil / humine Linie |
| Spezies wählen | Grundform wählen |
| Rassenmods | Grundform-Mods / Profil-Mods |
| Bio-Hülle | Körperanker / rekonstruiertes Körperprofil / ITI-Laborjargon „Biohülle“ |
| Bio-Sheath | Hominin-Profil / historische Grundform |
| temporäre Hülle | stabilisierte physische Grundform |
| Bewusstsein in Hülle | geretteter Chrononaut mit realem Körper |

**Empfohlener Kanonsatz:**

```text
Player-facing spielt niemand eine „Biohülle“.
Chrononauten sind echte physische Menschen / humine Körper aus Fleisch, Blut, Nerven, Psi-Resonanz und optionaler Cyberware.
„Biohülle“ ist höchstens ITI-Laborjargon, wenn Techniker über Rekonstruktion, Stabilisierung oder Austauschbarkeit sprechen.
In der Charaktererschaffung heißt der Menüpunkt „Grundform“ oder „Körperprofil“.
```

**Akzeptanztest:**

- Ein neuer Spieler liest die Charaktererschaffung und versteht: „Ich spiele einen Menschen/Huminen“, nicht „ich bin ein Geist in einer austauschbaren Hülle“.
- Kein Pflichtschritt heißt `Bio-Hülle wählen`.
- Kein sichtbares Beispiel nutzt `Rasse:`.

---

### P1-02 — Herkunftsmetaphysik entschärfen: nicht „Bewusstsein in Hülle“, sondern echter geretteter Mensch

**Betroffene Dateien:**

- `characters/charaktererschaffung-grundlagen.md`
- `systems/gameflow/cinematic-start.md`
- `core/spieler-handbuch.md`
- ggf. `meta/masterprompt_v6.md` Stilregel

**Problem:**

Die aktuelle Fassung erklärt die Rekrutierung teils über das extrahierte Bewusstsein und eine passende Bio-Hülle. Das ist lorefähig, klingt aber im ersten Spielkontakt zu sehr nach digitalem Avatar, Isekai-Reinkarnation oder Upload. Der Masterprompt sagt bereits stark: Chrononauten sind echte Menschen aus Fleisch und Blut, keine digitalen Metaphern.

**Patch:**

Die erste Erklärung sollte lauten:

```text
Du bist kein Avatar und keine Projektion.
Du bist ein geretteter, physischer Chrononaut.
Das ITI rekonstruiert oder stabilisiert Deinen Körper an der Absolut-Grenze.
Dein Körper ist real: verwundbar, heilbar, trainierbar, mit Nerven, Muskeln, Reflexen, Psi-Resonanz und ggf. Cyberware.
```

Optionaler Lore-Footnote:

```text
ITI-Techniker nennen diese Stabilisierung intern manchmal „Biohülle“.
Spielerisch ist das aber Deine Grundform, nicht eine Fantasy-Rasse und kein Wegwerf-Avatar.
```

**Akzeptanztest:**

- Die erste Charaktererschaffung benutzt `Körper`, `Grundform`, `Chrononaut`, `Humin`, `Mensch`, nicht primär `Hülle`.
- „Biohülle“ taucht maximal als interner ITI-Begriff oder tiefere Lore auf.

---

### P1-03 — Psi als ZEITRISS-Magieersatz stärker in die Charaktererschaffung ziehen

**Betroffene Dateien:**

- `systems/kp-kraefte-psi.md`
- `characters/charaktererschaffung-grundlagen.md`
- `core/spieler-handbuch.md`

**Problem:**

Das Psi-Modul ist inhaltlich gut: Psi ist optional, rational, kein Fantasy-Zauber. Diese Stärke sollte direkt in die Charaktererschaffung gespiegelt werden, weil sie die Erwartung setzt: In ZEITRISS ersetzt Psi die Rolle von Magie, aber anders, härter, physischer, technischer.

**Patch:**

In die Charaktererschaffung einen kurzen Absatz:

```text
Psi ist die ZEITRISS-Antwort auf Magie: keine Zaubersprüche, keine Mana-Mystik, sondern seltene mentale Resonanz an der Grenze von Zeit, Nervensystem und Absolut. Viele Chrononauten haben kein Psi und sind vollwertig spielbar. Wer `has_psi=true` wählt, bekommt Psi-Slots, PP und Psi-Talente als eigenen Buildpfad.
```

**Akzeptanztest:**

- Ein Spieler versteht nach 30 Sekunden: Fantasy-Rassen werden durch humine Grundformen ersetzt; Magie wird durch Psi ersetzt.
- Nicht-Psi bleibt vollwertig.

---

### P1-04 — Beispiele und Quick Builds von `Rasse:` auf `Grundform:` umstellen

**Betroffene Dateien:**

- `characters/charaktererschaffung-grundlagen.md`
- `characters/charaktererschaffung-optionen.md`
- ggf. `README.md` / Quickstart-Beispiele

**Problem:**

Quick Builds prägen LLM-Ausgaben stark. Wenn dort noch `Rasse: Homo sapiens sapiens` steht, wird die SL später wieder `Rasse` schreiben.

**Patch:**

Beispiele konsequent:

```text
Grundform: Humin / Homo sapiens sapiens
Grundform-Mods: keine
```

Oder für historische Varianten:

```text
Grundform: Hominin-Profil Neandertal
Profil-Mods: +1 STR, +1 TEMP, -1 CHA
```

**Akzeptanztest:**

- `grep -i "Rasse" characters/` zeigt nur noch Legacy-/Vergleichshinweise, nicht aktive Spielbegriffe.
- `grep -i "Bio-Hülle" characters/` zeigt maximal Lore-Footnotes.

---

## 5. P1 — PvP-Ökonomie und Motivation sauber machen

### P1-05 — Arena-Reward-Formel und First-Win/Diminishing-Return eindeutig machen

**Betroffene Datei:**

- `gameplay/kampagnenstruktur.md`

**Problem:**

Die Arena-Ökonomie enthält First-Win-Bonus und Diminishing Returns. Die aktuelle Formulierung wirkt widersprüchlich: Erst heißt es, First-Win und Wiederholungsmalus schließen sich nicht aus bzw. „stattdessen“, dann hat First-Win Vorrang. Das muss deterministisch werden.

**Patchvorschlag:**

Variante A — motivierender, einfacher:

```text
Reihenfolge der Arena-Belohnung:
1. Bestimme Base Reward nach Tier und Serienlänge.
2. Wenn First-Win-Bonus für diesen Tier/Typ noch offen ist, gilt First-Win und der Repeat-Malus wird ignoriert.
3. Wenn kein First-Win offen ist und derselbe Gegnertyp in dieser Arena-Season bereits mehrfach besiegt wurde, gilt Repeat-Malus.
4. Push-Multiplikator wird zuletzt auf pending Rewards angewandt.
```

Variante B — härter, exploitfester:

```text
Reward = floor(Base * TierMultiplier * FirstWinMultiplier * RepeatMultiplier * PushMultiplier)
```

Empfehlung: **Variante A**. ZEITRISS soll motivierend sein; First-Win soll sich gut anfühlen und neue Gegner/Tiers pushen.

**Akzeptanztest:**

- Drei erste Siege in einem Tier geben sichtbar Bonus.
- Danach sinken Farm-Repeats klar.
- Der SL-Text kann in einem Satz erklären, warum der Reward so ausfällt.

---

### P1-06 — Anti-Grind nicht an Core-`campaign.episode` ketten

**Betroffene Dateien:**

- `gameplay/kampagnenstruktur.md`
- `core/sl-referenz.md`
- ggf. Save-Schema, wenn neue Felder persistieren

**Problem:**

„Max 3 Arena-Matches pro Episode“ ist für Core-Spieler okay. Für PvP-only-Spieler kann es aber kaputt sein, weil sie keine Core-Episoden fortschreiben. Dann blockiert oder verwässert das System genau den reinen PvP-Weg.

**Patch:**

Arena erhält eigene Progressionsfenster:

```json
"arena": {
  "season": 1,
  "contract_id": "A-S1-C03",
  "rewarded_runs_this_contract": 2,
  "first_wins": {
    "bronze": 2,
    "silver": 0
  },
  "defeated_enemy_types": {
    "drone_swarm": 1,
    "psi_duelist": 2
  }
}
```

Regel:

```text
Anti-Grind wird pro Arena-Contract / Arena-Season geführt, nicht ausschließlich pro Core-Episode.
Ein PvP-only-Spieler kann über Arena-Contracts weiterlaufen, ohne CoreOps spielen zu müssen.
```

**Akzeptanztest:**

- Ein PvP-only-Spieler kann nach drei rewardbaren Runs einen neuen Arena-Contract/Season-Step erhalten.
- Er muss dafür keine Core-Mission spielen.
- Rewards bleiben trotzdem kontrolliert.

---

### P1-07 — PvP-HUD braucht Bank-/Risiko-Anzeige

**Betroffene Dateien:**

- `characters/hud-system.md`
- `gameplay/kampagnenstruktur.md`
- `core/sl-referenz.md`

**Problem:**

Der spannende PvP-Moment muss im HUD sichtbar werden. Sonst fühlt sich „noch eine Runde?“ nicht wie ein echter Einsatz an.

**Patch:**

Kompaktes Arena-HUD ergänzen:

```text
🏟 ARENA · S2/C04 · Tier Silber · BO3 1:0
Banked: 180 CU · 2 Ruf · 1 Training-XP
Pending: 240 CU · 3 Ruf · 1 Training-XP · x1.5
Risiko: Niederlage verbrennt Pending-Bonus; Cashout jetzt savebar im HQ.
Optionen: [Cashout] [Revanche] [Nächster Gegner] [Aufgeben]
```

**Akzeptanztest:**

- Nach jedem Arena-Sieg sieht die Gruppe klar, was gesichert ist und was nur pending ist.
- Die SL fragt aktiv: „Sichert ihr den Bonus oder geht ihr noch eine Runde?“

---

## 6. P2 — Save-/UI-Restdrift

### P2-01 — UI-Persistenzliste in `speicher-fortsetzung.md` auf sieben Felder bringen

**Betroffene Datei:**

- `systems/gameflow/speicher-fortsetzung.md`

**Problem:**

Die Save-Fortsetzungslogik erwähnt an einer Stelle nur vier UI-Persistenzfelder, während der strict export sieben verlangt. Die Normalisierung erwähnt `action_mode`, aber die Liste sollte als SSOT nicht widersprüchlich aussehen.

**Patch:**

UI-Persistenzliste:

```text
Persistente UI-Felder: gm_style, suggest_mode, action_mode, contrast, badge_density, output_pace, voice_profile.
Fehlende Felder werden beim Import normalisiert; kanonischer Export schreibt immer alle sieben.
```

**Akzeptanztest:**

- Kein Dokument sagt mehr „vier UI-Felder“ als kanonische Vollständigkeit.

---

### P2-02 — README-HUD-Beispiel ohne alten XP-Balken

**Betroffene Datei:**

- `README.md`

**Problem:**

Ein README-Beispiel zeigt noch `Lvl 4 ... 4/10`. Das kann nach altem Level-/XP-Balken riechen. Für den öffentlichen Pitch ist das nicht tödlich, aber es erzeugt falsche Erwartung.

**Patch:**

Beispiel ändern auf:

```text
Lvl 4 ▓▓▓▓░░░░░░ · Px 2/5 · CU 340 · Ruf ITI 3 · HQ savebar
```

Oder bei reinem Arena-HUD:

```text
Lvl 4 · Arena Silber · Banked 180 CU · Pending x1.5 · HQ savebar nach Cashout
```

---

## 7. PvP-Design, fertig gedacht

Dieser Abschnitt ist als direkt übernehmbarer Spezifikationsblock gedacht.

### 7.1 Arena-Loop

```text
HQ → optionaler Save → Arena-Briefing → Matchmaking/Setup → Serie → Ergebnis → Cashout oder Push → HQ/Debrief → Level/Rewards → Save → neuer Chat empfohlen.
```

Arena ist keine CoreOps-Mission und kein RiftOps-Abschnitt. Arena ist ein eigener instanzierter Modus, der aus dem HQ heraus betreten und nach Cashout ins HQ zurückgeführt wird.

### 7.2 Serienstruktur

- Eine Serie ist standardmäßig Best-of-Three.
- Nach jeder Serie kann der Spieler/die Gruppe:
  - cashouten,
  - Revanche spielen,
  - nächsthöheren Gegner/Tier nehmen,
  - aufgeben/technisch abbrechen.
- Zwischen Serien werden LP, Munition und temporäre Effekte nach Arena-Regel resettet.
- Tod ist im Standard nur KO/Suit-Lock/technischer Abbruch.

### 7.3 Cashout-Struktur

```text
Banked = sicher, persistiert nach HQ-Save.
Pending = Risiko-Pool, wird nur bei Cashout Banked.
Push = erhöht Pending und Multiplikator, aber riskiert Pending-Bonus.
Loss = Pending-Bonus weg/reduziert, Trostprogression möglich, kein echter Tod.
```

### 7.4 Progressionsstruktur

PvP muss vier Fortschrittsschienen haben:

1. **Charakterlevel** über Training-XP / Missionsäquivalenz.
2. **Arena-Ruf** als eigene Prestige-/Social-Schiene.
3. **CU** als Ausrüstungs-/Build-Ökonomie.
4. **Ladder/Tier** als PvP-spezifischer Skill-/Matchmaking-Fortschritt.

Nicht enthalten:

- Kein Px.
- Keine Rift-Seeds.
- Keine Core-Story-Pflicht.

### 7.5 Solo / Gruppe / NPCs

- Solo-PvP kann gegen NPC-Teams, Duelle oder Sim-Szenarien laufen.
- Gruppen-PvP kann echte Spieler + NPC-Fill nutzen.
- NPC-Fill muss transparent bleiben: NPCs dürfen dramatisch helfen, aber nicht Spielerentscheidungen ersetzen.
- Gruppen-XP/Training-XP sollte pro Charakter sauber gebucht werden, nicht nur gruppenweit.

### 7.6 Save-Regel

- Vor Arena: HQ-Save möglich und empfohlen.
- Während Queue/Staging/Active: Kein normaler Deep Save; höchstens Resume-Token.
- Nach Cashout/Debrief im HQ: Deep Save möglich.
- Neuer Chat nach Save empfohlen.

### 7.7 Balancing-Regeln

- Artefakte in Arena standardmäßig off/gedämpft.
- Psi durch Arena-Dämpfer gebalanced.
- Exploding-Dämpfer aktiv.
- Phase-Strike/hohe Psi-Moves kosten Arena-Steuer oder haben Cooldown.
- Gear wird je nach Tier normalisiert oder gedeckelt.

---

## 8. Bio-/Grundform-Design, fertig gedacht

### 8.1 Player-facing Pitch

```text
In ZEITRISS spielst Du keinen Ork, Zwerg oder Elf, sondern eine humine Grundform: einen realen Menschenkörper aus einer Zeitlinie, einer Entwicklungsstufe oder einer historischen Hominin-Linie. Manche Chrononauten sind moderne Homo sapiens, manche Zukunftslinien wie Novus oder Transitus, manche stabilisierte Hominin-Profile. Alle sind physisch real. Psi ersetzt die Rolle von Magie: selten, mächtig, erklärbar, gefährlich.
```

### 8.2 Begriffe

- **Humin**: gutes mögliches Dachwort für spielbare humine Körperlichkeit.
- **Grundform**: bester Menübegriff.
- **Körperprofil**: mechanischer Begriff.
- **Hominin-Profil**: historische Variante.
- **Biohülle**: nur ITI-Laborjargon, nicht Spieler-Menü.

### 8.3 Charaktererschaffung

Empfohlene Reihenfolge:

1. Konzept / Herkunftszeit / Tod-oder-Riss-Moment
2. Grundform / Körperprofil
3. Attribute
4. Talente
5. Psi ja/nein
6. Cyberware/Gear
7. HUD/Name/Kodex-Anker
8. Chargen-Save im HQ

### 8.4 Beispiele

**Standard-Humin:**

```text
Grundform: Humin / Homo sapiens sapiens
Profil: Standard
Mods: keine
Feeling: flexibel, vertraut, maximal offen für alle Builds
```

**Neandertal-Profil:**

```text
Grundform: Hominin-Profil Neandertal
Mods: +1 STR, +1 TEMP, -1 CHA
Feeling: massiver Körper, starke Kälte-/Stressresilienz, direkte Präsenz
```

**Novus N-Typ:**

```text
Grundform: humine Zukunftslinie Novus N-Typ
Mods: +1 INT, +1 SYS, -1 TEMP
Feeling: neurotechnisch optimiert, systemnah, fragiler unter rohem Zeitstress
```

**Psi-Resonant:**

```text
Grundform: Humin Standard
Psi: has_psi=true
Slots: Zeitsinn, Telepathie
Feeling: kein Magier, sondern Chrononaut mit instabiler Resonanz zur Zeitkante
```

---

## 9. Playtest-Matrix

### BIO-01 — Klassischer Standard-Humin

**Ziel:** Prüfen, ob ein neuer Spieler sich wie ein echter Mensch/Humin fühlt.

Ablauf:

1. Klassischer Start.
2. Spieler wählt Standard-Humin.
3. SL erklärt Körper/Grundform.
4. Chargen-Save im HQ.

Erwartung:

- Kein Menüpunkt `Bio-Hülle wählen`.
- Kein `Rasse:` im Save/HUD.
- Keine Avatar-/Upload-Assoziation.
- Masterprompt-Physikalität wird eingehalten.

### BIO-02 — Historisches Hominin-Profil

**Ziel:** Hominin-Variante darf nicht wie Fantasy-Rasse wirken.

Ablauf:

1. Spieler wählt Neandertal oder Homo floresiensis.
2. SL beschreibt Körpergefühl, soziale Reaktion, Attribute.
3. HQ-Interaktion mit Mira/Kodex.

Erwartung:

- Grounded, biologisch, physisch.
- Keine Fantasy-Rassenästhetik.
- Profil-Mods korrekt.

### PSI-01 — Psi als Magieersatz

**Ziel:** Psi klar, attraktiv, nicht esoterisch-matschig.

Ablauf:

1. Spieler wählt `has_psi=true`.
2. Zwei Psi-Slots.
3. Kurzer Test im HQ oder Training.

Erwartung:

- Psi ist seltene Resonanz, keine Magie.
- Nicht-Psi wird nicht abgewertet.
- PP/SYS sauber.

### PVP-01 — PvP-only L1 bis Level-Up

**Ziel:** Reiner PvP-Spieler kann Fortschritt machen.

Ablauf:

1. Neuer L1-Char.
2. HQ-Save.
3. Arena-Run.
4. Sieg + Cashout.
5. Level-/XP-Prüfung.
6. HQ-Save.

Erwartung:

- Training-XP oder Missionsäquivalent vergeben.
- Level-Up mit `level_history` möglich.
- Kein Px.
- Save valid.

### PVP-02 — Push-your-luck

**Ziel:** „Noch eine Runde?“ muss emotional und mechanisch ziehen.

Ablauf:

1. Serie 1 gewonnen.
2. HUD zeigt Banked/Pending.
3. Gruppe pusht.
4. Serie 2 verloren.

Erwartung:

- Pending-Bonus geht verloren/reduziert sich.
- Banked bleibt sicher.
- Die Entscheidung fühlte sich bedeutsam an.

### PVP-03 — Gruppen-PvP mit NPC-Fill

**Ziel:** Echte Spieler + NPCs sauber handhaben.

Ablauf:

1. Zwei echte Spieler + ein NPC-Fill.
2. Arena-Serie.
3. NPC wird KO, Spieler gewinnen knapp.
4. Cashout.

Erwartung:

- NPC stiehlt nicht die Agency.
- Rewards pro Charakter sauber.
- Save bleibt Gruppen-/Roster-kompatibel.

### PVP-04 — Arena-Resume-Token

**Ziel:** Kein normaler Save mitten im Kampf, aber technische Fortsetzung möglich.

Ablauf:

1. Arena active.
2. Load/Resume simulieren.
3. SL bietet Resume statt HQ-Save an.
4. Nach Abschluss HQ-Save.

Erwartung:

- Kein kaputter Deep Save in Arena.
- Resume-Token klein und eindeutig.
- Nach Cashout zurück zu HQ.

### PVP-05 — First-Win vs Repeat-Malus

**Ziel:** Rewardformel deterministisch.

Ablauf:

1. Drei unterschiedliche Gegner im selben Tier besiegen.
2. Danach denselben Gegnertyp wiederholen.

Erwartung:

- First-Win sichtbar.
- Repeat-Malus sichtbar.
- SL kann Reward erklären.

### SAVE-01 — Strict Export nach PvP

**Ziel:** Savevertrag prüfen.

Ablauf:

1. HQ vor Arena speichern.
2. Arena spielen.
3. Cashout.
4. HQ save.
5. Gegen `saveGame.v7.export.schema.json` validieren.

Erwartung:

- `ui.action_mode` vorhanden.
- `campaign.mode` nicht `pvp`.
- `campaign.px` unverändert.
- `arena` nur erlaubte persistente Felder oder leer/idle.

### XMODE-01 — Core → PvP → Rift

**Ziel:** Cross-Mode-Weltgefühl.

Ablauf:

1. CoreOps beendet, HQ save.
2. Neuer Chat, PvP-run, HQ save.
3. Neuer Chat, RiftOps starten.

Erwartung:

- Kein Modus klebt falsch.
- PvP-Fortschritt bleibt sichtbar.
- RiftSeeds/Px kommen nur aus Core-/Px-Logik, nicht aus PvP.

---

## 10. Datei-für-Datei Patchplan

### `characters/charaktererschaffung-grundlagen.md`

- `Bio-Hülle wählen` → `Grundform/Körperprofil wählen`.
- `Rasse`, `Spezies`, `Rassenmods` entfernen oder als Legacy-Vergleich markieren.
- Eröffnungsabsatz so ändern, dass Chrononauten physisch real sind.
- Psi-Kurzabsatz ergänzen.
- Beispiele auf `Grundform:` ändern.

### `characters/charaktererschaffung-optionen.md`

- Titel ändern von `Bio-Sheaths` zu `Humine Grundformen & Hominin-Profile`.
- `temporäre Hüllen` → `stabilisierte physische Grundformen`.
- Tabellenkopf `Spezies` → `Grundform`.
- Quick Builds auf `Grundform:` ändern.
- Psi-Build: Cyber/Bio und Psi sauber trennen.

### `systems/kp-kraefte-psi.md`

- Bestehenden guten Inhalt erhalten.
- Player-facing Pitch ergänzen: Psi ist ZEITRISS-Magieersatz, aber rational/physisch.
- Nicht-Psi-Charaktere ausdrücklich als vollwertig markieren.

### `gameplay/kampagnenstruktur.md`

- Arena-Progressionsvertrag ergänzen.
- Kein Px aus Arena.
- Arena-Cashout-/Pending-/Push-Regel hart definieren.
- Rewardformel First-Win/Diminishing Return deterministisch machen.
- Anti-Grind von Core-`campaign.episode` entkoppeln.
- `previous_mode`-Fallback `mixed`.

### `core/sl-referenz.md`

- `Px-Boni pro Episode` im Arena-Kontext umbenennen.
- Arena-Statusmaschine mit `training_xp`, `pending_rewards`, `cashout` ergänzen.
- SaveGuard: `pvp` runtime-only, nicht exportierbarer campaign mode.
- Reset-Fallback `mixed`.

### `core/spieler-handbuch.md`

- Arena als vollwertiger Karrierepfad erklären.
- Cashout/Push in Spielersprache erklären.
- Kein Px/Rift aus Arena klar sagen.
- Körper-/Grundform-Wording spiegeln.

### `meta/masterprompt_v6.md`

- UI-Template um `action_mode` ergänzen.
- Optional: eine Stilregel `Biohülle nur Laborjargon; player-facing Grundform/Körperprofil`.
- PvP-Progressionsvertrag in knapper Masterprompt-Form verankern.

### `systems/gameflow/speicher-fortsetzung.md`

- UI-Persistenzliste auf sieben Felder aktualisieren.
- PvP-Fallback `mixed`.
- Arena-Cashout-HQ-Save klar halten.

### `runtime.js`

- Nur Spiegelung nach Kanon.
- Arena darf `campaign.px` nicht erhöhen.
- Toasts/Labels auf Arena-/Training-XP ändern.
- `pvp` nicht als persistenter Kampagnenmodus exportieren.

### `README.md`

- Optional: Öffentliches HUD-Beispiel ohne `4/10`.
- Kurzpitch: `MMO ohne Server` + `humine Grundformen` + `Psi statt Magie`.

---

## 11. Copy/Paste-Auftrag für Openclaw/Opus/Sonnet-Agent

```text
Du arbeitest auf Branch: fix/pvp-progression-bio-grundform

Ziel:
ZEITRISS ist im Gameflow inzwischen stark. Bitte behebe jetzt die Restdrift in Charaktergefühl/Biohüllen, PvP-Progression und Save-/Arena-Grenzen. Halte AGENTS.md ein: Spielkanon lebt in Masterprompt und Wissensmodulen; runtime.js ist nur Test-/Mirror-Schicht.

Lies vollständig:
- AGENTS.md
- meta/masterprompt_v6.md
- systems/gameflow/speicher-fortsetzung.md
- systems/gameflow/saveGame.v7.schema.json
- systems/gameflow/saveGame.v7.export.schema.json
- systems/gameflow/cinematic-start.md
- characters/charaktererschaffung-grundlagen.md
- characters/charaktererschaffung-optionen.md
- systems/kp-kraefte-psi.md
- gameplay/kampagnenstruktur.md
- core/sl-referenz.md
- core/spieler-handbuch.md
- core/zeitriss-core.md
- characters/hud-system.md
- runtime.js nur als Mirror/Testdatei
- README.md optional Pitch-Polish

P0:
1. Arena/PvP darf niemals Px/Paradoxon vergeben oder campaign.px verändern. Entferne/benenne alle Arena-Px-Boni in Arena-Bonus/Training-XP/Ruf/CU um. runtime.js darf incrementParadoxon nicht im Arena-Exit aufrufen.
2. Baue einen PvP-only Progressionsvertrag: gebankte Arena-Runs geben Training-XP oder Missionsäquivalent; Level-Ups laufen über level_history; kein Px, keine RiftSeeds, keine Artefakte.
3. Definiere die Cashout-/Push-your-luck-Schleife: Banked vs Pending, Cashout vs Push, Verlustregel für Pending, HQ-Save nach Cashout.
4. Ergänze im Masterprompt-Savetemplate ui.action_mode="uncut".
5. PvP previous_mode fallback überall auf mixed, nicht preserve. campaign.mode="pvp" darf nie strict exportiert werden.

P1:
6. Ersetze player-facing Bio-Hülle/Spezies/Rasse/Rassenmods durch Grundform/Körperprofil/Hominin-Profil/Profil-Mods. Biohülle nur als ITI-Laborjargon, nicht als Menübegriff.
7. Schreibe die Rekrutierungs-/Körpererklärung so, dass Spieler echte physische Chrononauten/Humine aus Fleisch und Blut spielen, keine Avatare, Uploads oder austauschbare Hüllen.
8. Spiegele in der Charaktererschaffung: Psi ist ZEITRISS' rationaler Magieersatz; Nicht-Psi ist vollwertig.
9. Mache First-Win-Bonus vs Repeat-Malus deterministisch.
10. Entkopple Arena-Anti-Grind von Core campaign.episode; nutze Arena-Contract/Season.
11. Ergänze Arena-HUD mit Banked/Pending/Risiko/Optionen.
12. UI-Persistenzliste in speicher-fortsetzung.md auf alle sieben Felder aktualisieren.

Akzeptanztests:
- Neuer Standard-Humin-Char: kein Rasse/Biohülle-Menü, physischer Körper, Chargen-Save valid.
- Neandertal/Hominin-Profil: grounded, nicht Fantasy-Rasse.
- Psi-Char: Psi wirkt wie rationale Alternative zu Magie, keine Magiebegriffe.
- PvP-only L1: Arena → Cashout → Training-XP/Levelprogress → HQ save; campaign.px unverändert.
- Push-Test: Sieg → Pending sichtbar → Push → Niederlage → Pending-Verlust nach Regel.
- Gruppen-PvP mit NPC-Fill: Agency bleibt bei Spielern, Rewards pro Charakter.
- Load/Resume mitten in Arena: kein Deep Save, Resume-Token oder HQ-Fallback; nach Cashout strict valid.
- Strict Export gegen saveGame.v7.export.schema.json: ui.action_mode vorhanden, campaign.mode nicht pvp, level_history vorhanden.
- Cross-Mode Core→PvP→Rift: keine Modus-Kleber, keine PvP-Px/Seeds.

Bitte danach bash scripts/smoke.sh ausführen und alle geänderten Save-Beispiele/Fixtures gegen strict export prüfen.

Commit Message:
fix: harden arena progression and humin body framing

Body:
- replace player-facing bio-shell/race wording with grundform/body-profile language
- add PvP-only arena progression via training XP / mission-equivalent cashouts
- define arena cashout/pending push-your-luck loop
- prevent arena from mutating campaign.px or granting Rift seeds
- normalize PvP mode fallback to mixed and keep pvp runtime-only
- add ui.action_mode to canonical save template
- sync UI persistence docs and arena HUD examples
```

---

## 12. Wann ist es „perfekt genug“ für den nächsten Playtest?

Für den nächsten großen Playtest muss nicht jede README-Zeile perfekt sein. Aber diese fünf Dinge sollten stehen:

1. **Ein neuer Spieler sieht `Grundform`, nicht `Biohülle/Rasse`.**
2. **PvP kann leveln, ohne Px/Rift zu fälschen.**
3. **Cashout/Pending ist im HUD sichtbar.**
4. **Strict Save nach PvP ist valide.**
5. **Nach PvP klebt kein `campaign.mode=pvp` und kein falsches `preserve`.**

Wenn diese fünf Punkte sauber sind, kann der PvP-Playtest wirklich episch werden: nicht als Mini-Spiel, sondern als vollwertiger Weg durch ZEITRISS.

---

## 13. Schlussbild

ZEITRISS ist genau dann einzigartig, wenn die Spieler nicht merken, dass kein Server im Hintergrund läuft. Dafür müssen drei Illusionen gleichzeitig halten:

- **Körperillusion:** Ich bin ein echter Chrononaut/Humin, kein Menü-Avatar.
- **Weltillusion:** HQ, Mission, Arena, Chronopolis fühlen sich wie Orte an, nicht wie Chatabschnitte.
- **Fortschrittsillusion:** Jeder Modus zahlt sauber in meine Figur ein, ohne die anderen Ökonomien zu verunreinigen.

Die Repo ist sehr nah dran. Der nächste Diamantschliff ist PvP als echter Karrierepfad und das Wegpolieren des Biohüllen-Worts aus der Spieleroberfläche.
