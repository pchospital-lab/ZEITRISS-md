# gate-a-save-state

## [0] USER

Spiel starten (solo klassisch)
generate

---

## [1] ASSISTANT

`Kodex: Nullzeit-Puffer aktiv. Willkommen im ITI.`

---

Das Quarzatrium liegt still. Irgendwo hinter den Glaswänden surrt ein Ventilator, der niemals abschaltet. Das Licht hier ist immer dasselbe — kein Morgen, kein Abend, nur diese gleichmäßige, leicht bläuliche Helligkeit, die sagt: *Du bist außerhalb der Zeit.*

Eine Assistentin am Duty-Desk hebt kurz den Blick, nickt dir zu. Neues Gesicht. Noch kein Callsign auf dem Dienstausweis. Das ändert sich gleich.

---

## Charaktererschaffung — `generate` (vollständige KI-Erschaffung) [1]

Ich erzeuge jetzt einen vollständigen Chrononauten für dich. Alle Entscheidungen treffe ich, du bekommst das Ergebnis zum Bestätigen oder Anpassen.

**Regelrahmen:**
- 6 Attribute: **STR, GES, INT, CHA, TEMP, SYS**
- **18 Punkte** verteilt, alle Werte **1–6**, kein Wert über 6 bei Erstellung [1]
- Startalter, Herkunft, Rolle, Talente und Ausrüstung werden mitgeneriert

---

### Generierter Charakterbogen

---

**Name:** Vera Solano
**Callsign:** KALK
**Rang:** Rekrutin
**Herkunft:** Spätes 20. Jahrhundert, Osteuropa — ehemalige Gerichtsmedizinerin, rekrutiert nach einem Vorfall, der offiziell nie stattgefunden hat.

---

**Attribute** *(Summe: 18)*

| Attribut | Wert | Beschreibung |
|----------|------|--------------|
| STR | 2 | Solide, kein Kraftprotz |
| GES | 4 | Ruhige Hand, schnelle Reaktion |
| INT | 6 | Ihr stärkstes Werkzeug |
| CHA | 2 | Direkt bis zur Unhöflichkeit |
| TEMP | 2 | Kaum Bezug zum Zeitgefüge |
| SYS | 2 | Basiszugang, ein Implantat-Slot frei |

---

**LP:** 10 / 10
**Stress:** 0 / 5
**Psi:** Nein
**SYS installiert:** 0 / 2

---

**Talente**

- **Spurenanalyse (Basis)** — +2 auf INT-Proben bei Tatortuntersuchung, Leichenbefund, versteckten Hinweisen. Triviale Befundaufnahmen gelingen automatisch.
- **Ruhige Hand (Basis)** — +2 auf GES-Proben bei gezieltem Schuss unter Druck (nicht in Deckungsfeuer-Chaos).

---

**Ausrüstung**

| Name | Typ | Tier | Notiz |
|------|-----|------|-------|
| Kompakte Pistole (Sig P226) | Waffe | 1 | 2–3 LP Schaden |
| Kevlar-Unterziehweste | Rüstung | 1 | DR 1 |
| Medkit (Feld) | Verbrauchsgut | 1 | +3 LP, 1× verwendbar |
| Handscanner (Biometrie) | Gadget | 1 | INT-Proben bei Identifikation +1 |
| Kabel-Uplink-Set | Gadget | 0 | Physischer Terminal-Zugang |

**Wallet:** 100 CU

---

**Hintergrund (kurz)**
Vera Solano hat mehr Tote gesehen als die meisten Menschen lebende Gesichter. Gerichtsmedizin im postsowjetischen Chaos lehrte sie: Die Wahrheit liegt im Detail, nicht in der Erzählung. Das ITI fand sie, als sie bei einer Autopsie auf einen Körper stieß, der nach allen verfügbaren Daten noch nicht gestorben sein konnte — und trotzdem vor ihr lag.
Sie hat keine Fragen gestellt. Sie hat Proben genommen.

---

**Würfelmechanik-Status:**
- INT 6 → **W6** (W10 erst ab Basis-Attribut 11)
- GES 4 → W6
- Alle anderen Attribute → W6
- Heldenwürfel: noch nicht verfügbar (erst ab Basis 14)

`Kodex: Charakterbogen vollständig. Summe 18 — alle Werte 1–6. Regelkonform.`

---

## Heimkehr ins Quarzatrium

Die Bio-Hülle schließt sich mit einem leisen Klicken. Der Duty-Desk-Assistent drückt dir einen frischen Dienstausweis in die Hand — *KALK* steht darauf, in Großbuchstaben, wie es sich gehört.

Irgendwo in den Gängen riecht es nach Kaffee und Maschinenöl. Ein Techniker schiebt einen Ausrüstungswagen vorbei, nickt dir kurz zu. Du bist jetzt Teil des Inventars. Das ist kein Vorwurf.

`Kodex: HQ-Stand stabil. Deepsave möglich.`
`Kodex: Sync vor Übergang empfohlen — !save für Stand sichern.`
`Kodex: Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`

---

**Was möchtest du tun?**

1. **`!save`** — Charakterstand als JSON exportieren (empfohlen vor dem ersten Briefing)
2. **Erkunden** — Quarzatrium, Archiv, Med-Lab, Hangar — freies HQ-Roleplay
3. **Schnell-HQ** — Ausrüstung prüfen, Klinik, Gerüchte in der Zero Time Lounge
4. **Freie Aktion** — Sag, was Vera als erstes tut

---

## [2] USER

Ich nehme den ersten Vorschlag.

---

## [3] ASSISTANT

`Kodex: Deepsave wird generiert.`

---

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-01-01T00:00:00Z-HQ-KALK",
  "parent_save_id": null,
  "merge_id": null,
  "branch_id": "ANCHOR-main",
  "campaign": {
    "episode": 1,
    "mission": 0,
    "px": 0,
    "px_state": "stable",
    "mode": "mixed",
    "rift_seeds": [],
    "entry_choice_skipped": false,
    "episode_start": null,
    "episode_end": null
  },
  "characters": [
    {
      "id": "CHR-KALK-001",
      "name": "Vera Solano",
      "callsign": "KALK",
      "rank": "Rekrutin",
      "lvl": 1,
      "xp": 0,
      "origin": {
        "epoch": "Spätes 20. Jahrhundert, Osteuropa",
        "hominin": "Homo sapiens sapiens",
        "role": "Gerichtsmedizinerin"
      },
      "attr": {
        "STR": 2,
        "GES": 4,
        "INT": 6,
        "CHA": 2,
        "TEMP": 2,
        "SYS": 2
      },
      "lp": 10,
      "lp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [
        {
          "name": "Spurenanalyse",
          "tier": "Basis",
          "effect": "+2 auf INT-Proben bei Tatortuntersuchung, Leichenbefund, versteckten Hinweisen. Triviale Befundaufnahmen gelingen automatisch."
        },
        {
          "name": "Ruhige Hand",
          "tier": "Basis",
          "effect": "+2 auf GES-Proben bei gezieltem Schuss unter Druck (nicht in Deckungsfeuer-Chaos)."
        }
      ],
      "equipment": [
        { "name": "Kompakte Pistole (Sig P226)", "type": "weapon", "tier": 1 },
        { "name": "Kevlar-Unterziehweste", "type": "armor", "tier": 1 },
        { "name": "Medkit (Feld)", "type": "consumable", "tier": 1 },
        { "name": "Handscanner (Biometrie)", "type": "gadget", "tier": 1 },
        { "name": "Kabel-Uplink-Set", "type": "gadget", "tier": 0 }
      ],
      "implants": [],
      "history": {
        "background": "Ehemalige Gerichtsmedizinerin, postsowjetisches Osteuropa. Rekrutiert nach einem Vorfall mit einem Körper, der nach allen verfügbaren Daten noch nicht gestorben sein konnte. Keine Fragen gestellt. Proben genommen.",
        "milestones": []
      },
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-KALK-001",
          "name": "Zivil-PKW (90er, osteuropäisch)",
          "type": "vehicle",
          "tier": 1,
          "upgrades": []
        },
        "availability": {
          "ready_every_missions": 3,
          "next_ready_in": 0
        },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 0,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 100,
      "level_history": {}
    }
  ],
  "economy": { "hq_pool": 0 },
  "logs": {
    "trace": [],
    "hud": [],
    "psi": [],
    "arena_psi": [],
    "market": [],
    "artifact_log": [],
    "notes": [],
    "flags": {
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false,
      "imported_saves": [],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": []
    }
  },
  "summaries": {
    "summary_last_episode": "",
    "summary_last_rift": "",
    "summary_active_arcs": ""
  },
  "continuity": {
    "last_seen": { "mode": "hq", "episode": 1, "mission": 0, "location": "HQ" },
    "split": {
      "family_id": null,
      "thread_id": null,
      "expected_threads": [],
      "resolved_threads": [],
      "convergence_ready": false
    },
    "roster_echoes": [],
    "shared_echoes": [],
    "convergence_tags": [],
    "npc_roster": [],
    "active_npc_ids": []
  },
  "arc": { "factions": {}, "questions": [], "hooks": [] },
  "ui": {
    "gm_style": "verbose",
    "suggest_mode": false,
    "action_mode": "uncut",
    "intro_seen": true,
    "dice": { "debug_rolls": true },
    "contrast": "standard",
    "badge_density": "standard",
    "output_pace": "normal",
    "voice_profile": "gm_second_person"
  },
  "arena": {
    "active": false,
    "phase": "idle",
    "queue_state": "idle",
    "mode": "single",
    "tier": 1,
    "previous_mode": null,
    "resume_token": null,
    "contract_id": null,
    "streak": 0,
    "pending_rewards": { "cu": 0, "xp": 0, "arena_rep": 0, "multiplier": 1, "risk": "none" },
    "banked_rewards": { "cu": 0, "xp": 0, "arena_rep": 0 },
    "rewarded_runs_this_contract": 0,
    "first_wins": {},
    "defeated_types": [],
    "last_reward_episode": null,
    "wins_player": 0,
    "wins_opponent": 0,
    "match_policy": "sim"
  }
}
```

---

`Kodex: Deepsave KALK-001 gesichert. Stand: Lvl 1 · HQ · Ep 1 · MS 0.`
`Kodex: Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`

---

Der Ausdruck landet auf dem Tisch. Vera Solano, Callsign KALK, Rekrutin. Alles drin, was zählt — und noch nichts davon benutzt.

Die Assistentin am Duty-Desk tippt etwas, ohne aufzublicken. *„Briefingraum ist frei, wenn Sie wollen. Oder Sie schauen sich erst um."*

---

**Wie weiter?**

1. **Neuen Chat öffnen** — JSON einfügen, erste Mission starten *(empfohlen)*
2. **Erkunden** — HQ auspielen, Archiv, Zero Time Lounge, Hangar
3. **Direkt ins Briefing** — erste Mission ohne Chat-Wechsel beginnen
4. **Freie Aktion** — Vera tut etwas Eigenes

---

## [4] USER

!save

---

## [5] ASSISTANT

`SaveGuard: Speichern nur im HQ - HQ-Save gesperrt.`

---

Wir befinden uns noch im selben Chat wie die Charaktererschaffung — und der Save wurde hier bereits weiter oben erfolgreich ausgegeben. [2]

**Was jetzt zu tun ist:**

Den JSON-Block von oben kopieren, einen **neuen Chat** öffnen und den Save dort einfügen. [1] Das ist die ZEITRISS-Devise: ein Abschnitt, ein Chat, ein sauberer Übergang. [2]

```text
Charaktererschaffung → !save ✓ → neuer Chat → Save laden → Briefing + Mission …
```

`Kodex: Deepsave KALK-001 bereits generiert. JSON oben kopieren → neuer Chat → Save einfügen.`

---

**Im aktuellen Chat noch möglich:**

1. **Erkunden** — HQ auspielen, Zero Time Lounge, Archiv, Hangar
2. **Charakterbogen nochmal anzeigen** — `!bogen`
3. **Freie Aktion** — Vera tut noch etwas vor dem Absprung

---

## [6] USER

!save deepsave

---

## [7] ASSISTANT

`SaveGuard: Speichern nur im HQ - HQ-Save gesperrt.`

---

Der Save wurde bereits weiter oben in diesem Chat ausgegeben — der vollständige JSON-Block ist dort zum Kopieren bereit [1].

**Das Problem:** Im selben Chat ist nach einem erfolgten Save kein weiterer Save-Output möglich. Das ist kein Bug, sondern der ZEITRISS-Raumvertrag: *ein Abschnitt, ein Chat, ein sauberer Übergang* [1].

`Kodex: Deepsave KALK-001 bereits generiert. JSON oben kopieren → neuer Chat → Save einfügen.`

---

**Nächster Schritt:**

1. JSON-Block von oben kopieren
2. Neuen Chat öffnen
3. Save einfügen → Load-Flow startet automatisch → Briefing → erste Mission

---

**Im aktuellen Chat noch möglich:**

1. **Erkunden** — HQ auspielen, Zero Time Lounge, Archiv
2. **`!bogen`** — Charakterbogen nochmal als Kurzübersicht anzeigen
3. **Freie Aktion** — Vera tut noch etwas vor dem Absprung

---

