# chat3-mission1

**Turns:** 24  |  **Sauber beendet:** False  |  **Save:** False
**Phase:** Erste Mission. Du spielst eine komplette Core-Operation mit 12 Szenen bis Debrief.

---

## [0] USER

Spiel laden
```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-01-01T06:14:00Z-HQ-ZTL-VOSS",
  "parent_save_id": "SAVE-2026-01-01T00:00:00Z-HQ-SPLINTER-INIT",
  "merge_id": null,
  "branch_id": "ANCHOR-main",
  "campaign": {
    "episode": 1,
    "mission": 0,
    "px": 0,
    "px_state": "stable",
    "mode": "core",
    "rift_seeds": []
  },
  "characters": [
    {
      "id": "CHR-VOSS-001",
      "name": "Mara Voss",
      "callsign": "SPLINTER",
      "rank": "Rekrut",
      "lvl": 1,
      "xp": 0,
      "origin": {
        "epoch": "1987, Berlin",
        "hominin": "Homo sapiens sapiens",
        "role": "Infiltration & Spurenanalyse"
      },
      "attr": {
        "STR": 2,
        "GES": 5,
        "INT": 5,
        "CHA": 2,
        "TEMP": 2,
        "SYS": 2
      },
      "hp": 10,
      "hp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [
        {
          "name": "Tatortanalyse",
          "tier": "Basis",
          "effect": "+2 auf INT-Proben zur Spurensicherung, Szenenrekonstruktion und technischen Analyse. Triviale Analysen: Auto-Erfolg."
        }
      ],
      "equipment": [
        { "name": "Kompakte Dienstpistole", "type": "weapon", "tier": 1 },
        { "name": "Leichte Kevlarweste", "type": "armor", "tier": 1 },
        { "name": "Handscanner (ITI-Modell)", "type": "gadget", "tier": 1 },
        { "name": "Multitool-Dietrich", "type": "gadget", "tier": 0 },
        { "name": "Comlink (verschlüsselt)", "type": "gadget", "tier": 1 },
        { "name": "Rauchgranate x2", "type": "consumable", "tier": 0 }
      ],
      "implants": [],
      "history": {
        "background": "Berlin, 1987. Aufgewachsen zwischen Stasi-Schatten und Kaltem Krieg. Ausgebildete Kriminaltechnikerin, rekrutiert nach einem Zwischenfall, den das ITI lieber aus den Akten tilgt. Fragt nicht warum Zeitlinien gesichert werden — fragt wer davon profitiert.",
        "milestones": [
          "Zero Time Lounge: Erstkontakt Duna. Kessler (8 Episoden) und Pham (5 Episoden) beobachtet — Papiernotiz, Handschrift, kein Druck, Kessler wusste vor dem Umdrehen wer reinkam. Duna testet ob Voss sieht was sie sieht."
        ]
      },
      "carry": [
        { "name": "Kompakte Dienstpistole", "type": "weapon", "tier": 1 },
        { "name": "Leichte Kevlarweste", "type": "armor", "tier": 1 },
        { "name": "Handscanner (ITI-Modell)", "type": "gadget", "tier": 1 },
        { "name": "Multitool-Dietrich", "type": "gadget", "tier": 0 },
        { "name": "Comlink (verschlüsselt)", "type": "gadget", "tier": 1 },
        { "name": "Rauchgranate x2", "type": "consumable", "tier": 0 }
      ],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-WOLF-001",
          "name": "Grauer Wolf",
          "type": "vehicle",
          "tier": 1,
          "upgrades": []
        },
        "availability": {
          "ready_every_missions": 4,
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
      "wallet": 100
    }
  ],
  "economy": {
    "hq_pool": 0
  },
  "logs": {
    "trace": [],
    "market": [],
    "artifact_log": [],
    "notes": [
      "ZTL-Beobachtung: Kessler wusste vor dem Umdrehen wer reinkam. Papiernotiz — Handschrift, 2-3 Zeilen, kein Druck. Plan, kein Befehl. Pham: Lächeln, Faltkante gesehen. Duna testet Voss aktiv."
    ],
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
    "summary_active_arcs": "EP1: Voss im HQ. ZTL-Szene läuft — Duna, Kessler, Pham. Offene Frage: Kesslers Plan, Dunas Test."
  },
  "continuity": {
    "last_seen": {
      "mode": "core",
      "episode": 1,
      "mission": 0,
      "location": "HQ · Zero Time Lounge"
    },
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
    "npc_roster": [
      {
        "id": "NPC-DUNA-001",
        "name": "Duna",
        "callsign": null,
        "role": "ZTL-Thekenpersonal",
        "scope": "HQ",
        "status": "active",
        "notes": "Beobachterin. Testet Neulinge aktiv. Kein Kodex-Protokoll in der ZTL."
      },
      {
        "id": "NPC-KESSLER-001",
        "name": "Kessler",
        "callsign": null,
        "role": "Erfahrener Chrononaut",
        "scope": "HQ",
        "status": "active",
        "notes": "8 Episoden. Narbe Schläfe. Papiernotiz — eigener Plan, kein Befehl. Wusste vor Umdrehen wer reinkam."
      },
      {
        "id": "NPC-PHAM-001",
        "name": "Pham",
        "callsign": null,
        "role": "Erfahrener Chrononaut",
        "scope": "HQ",
        "status": "active",
        "notes": "5 Episoden. Ruhig, beobachtend. Lächeln bei Kesslers Antwort — kennt die Situation."
      }
    ],
    "active_npc_ids": ["NPC-DUNA-001", "NPC-KESSLER-001", "NPC-PHAM-001"]
  },
  "arc": {
    "factions": {},
    "questions": [
      "Was steht auf Kesslers Papier — und wessen Plan ist es?",
      "Warum testet Duna Neulinge, und was macht sie mit dem was sie herausfindet?"
    ],
    "hooks": [
      "Kessler: 8 Episoden, Papiernotiz, wusste wer reinkommt — möglicher Kontakt oder Risiko.",
      "Duna: inoffizielle Informationsquelle, kein Kodex-Protokoll in ZTL."
    ]
  },
  "ui": {
    "gm_style": "verbose",
    "suggest_mode": false,
    "contrast": "standa
[...gekuerzt...]

---

## [1] ASSISTANT

# ZEITRISS — Save geladen

`Kodex: Session-Anker gesetzt. CHR-VOSS-001 · SPLINTER · Lvl 1 · HQ · Zero Time Lounge.`

---

**Kurzrückblick — wo du warst:**

Episode 1, Mission 0. Du bist Mara Voss, Callsign SPLINTER — Rekrutin, frisch im ITI, noch keine abgeschlossene Mission. Die Zero Time Lounge. Duna hinter der Theke, Kessler (8 Episoden, Narbenschläfe, Papiernotiz) und Pham (5 Episoden, ruhig, wissend). Kessler wusste, wer reinkommt, bevor er sich umdrehte. Duna hat dich beobachtet — testet, ob du siehst was sie sieht. Offene Fragen hängen in der Luft wie der Geruch von kaltem Kaffee.

---

`EP 1 · MS 0 · SC —/— · PHASE HQ · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

## HQ · Zero Time Lounge — Fortsetzung

Die Lounge ist, was sie immer ist: ein Ort ohne Uhrzeit. Kein Fenster, kein Tageslicht, keine Epoche. Das Licht kommt aus Deckenleisten, die irgendwann jemand auf "angenehm" kalibriert hat und seitdem niemand mehr angefasst hat. Es riecht nach Synthetik-Kaffee und dem leichten Ozon-Unterton, den alle ITI-Räume haben — Nullzeit-Atmosphäre, sagt man, als ob das eine Erklärung wäre.

Duna steht hinter der Theke. Sie hat dich angeschaut, als du reingekommen bist, und sie schaut dich noch an — nicht aufdringlich, eher wie jemand, der auf eine Antwort wartet, ohne die Frage gestellt zu haben. Kessler sitzt an seinem Platz. Die Papiernotiz liegt nicht mehr auf dem Tisch — entweder eingesteckt oder du hast sie nie gesehen, nur das Rechteck Schatten, das sie hinterlassen hat. Pham dreht seinen Becher. Langsam. Sieht dich dabei nicht an, aber du weißt, dass er weiß, dass du schaust.

Die ZTL ist kein Ort für Protokoll. Kein Kodex-Link hier, kein HUD-Overlay mit Personaldaten. Was du weißt, weißt du aus eigenen Augen.

---

**Wo stehst du gerade?**

1. **Duna ansprechen** — direkt oder beiläufig. Sie wartet auf etwas.
2. **Kessler** — an seinen Tisch gehen. Die Notiz ist weg, aber er ist noch da.
3. **Pham** — der Ruhige. Manchmal reden die mehr als die Lauten.
4. **Freie Aktion** — du hast die Lounge, die Zeit und deine Augen.

---

## [2] USER

zu Duna rüber, ich frag sie einfach was sie will

---

## [3] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE HQ · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Du gehst zur Theke. Kein Umweg, kein Zögern — direkt rüber, Unterarme auf die Kante, Blickkontakt.

Duna lässt dich ankommen. Wartet, bis du stehst. Dann legt sie das Tuch hin, mit dem sie gerade nichts geputzt hat, und sieht dich an. Ihre Augen sind ruhig — nicht kalt, aber kalkulierend. Die Art, wie jemand schaut, der schon viele Neulinge gesehen hat und weiß, dass die meisten in der zweiten Episode nicht mehr da sind.

*„Was ich will?"* Sie wiederholt die Frage nicht wie eine Frage. Eher wie jemand, der einen Begriff prüft. *„Ich will meistens, dass die Leute hier ihren Kaffee trinken und nicht sterben. Das zweite klappt seltener als das erste."*

Sie greift unter die Theke. Stellt einen Becher vor dich hin — Synthetik-Kaffee, noch dampfend, als hätte sie gewusst, dass du kommst.

*„Aber du meinst was anderes."* Kein Fragezeichen. *„Du meinst: warum ich dich angeschaut habe. Warum ich jeden anschaue."*

Kurze Pause. Sie lehnt sich leicht vor.

*„Weil die meisten Rekruten reinkommen und zuerst die Tür suchen. Den Ausgang. Reflex."* Ihr Blick geht kurz zu Kessler — nicht lang, eine Sekunde — und kommt zurück. *„Du hast zuerst die Leute angeschaut. Kessler. Pham. Dann mich. Dann die Tür."*

Sie nimmt ihr Tuch wieder auf.

*„Das ist entweder Training oder Instinkt. Beides ist nützlich. Eines davon ist seltener."*

Sie wartet. Nicht ungeduldig. Eher wie jemand, der einen Zug gemacht hat und jetzt sieht, ob das Gegenüber das Brett überhaupt kennt.

---

Kessler und Pham im Rücken. Du kannst sie nicht sehen, aber du weißt, dass Pham seinen Becher immer noch dreht.

---

1. **Antworten** — Instinkt oder Training. Was sagst du ihr?
2. **Gegenfrage** — sie hat dich gelesen, du liest zurück. Was willst du wissen?
3. **Kessler** — seinen Namen aufgreifen. Sie hat kurz rübergeschaut. Das war kein Zufall.
4. **Freie Aktion** — dein Zug.

---

## [4] USER

beides. aber ich glaub du weißt das schon.

---

## [5] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE HQ · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Duna hört zu. Keine Reaktion, während du redest — kein Nicken, kein Lächeln. Nur Zuhören.

Dann, nach einer Sekunde:

*„Ja."*

Einfach das. Kein Nachsatz. Sie nimmt den Becher, den sie vor dich gestellt hat, dreht ihn einmal um die eigene Achse — eine kleine, präzise Geste — und schiebt ihn wieder zu dir.

*„Deswegen hab ich dir Kaffee hingestellt."*

Hinter dir, ohne dass du es siehst, hört das leise Kratzen von Phams Becher auf dem Tisch auf. Er dreht nicht mehr.

Duna sieht dich weiter an. Jetzt ist etwas anderes in ihrem Blick — nicht wärmer, aber offener. Als hätte sich eine Tür einen Spalt bewegt, ohne aufzugehen.

*„Es gibt Leute hier, die acht Episoden überleben, weil sie gut sind,"* sagt sie, leise genug, dass es bei der Theke bleibt. *„Und es gibt Leute, die acht Episoden überleben, weil sie wissen, was sie nicht anfassen sollen."*

Wieder der kurze Blick. Diesmal versteckst du nicht, dass du es merkst.

*„Kessler ist beides,"* sagt sie. *„Das macht ihn interessant. Und das macht ihn gefährlich."*

Sie zieht das Tuch glatt. Thema gewechselt, Körpersprache neutral — als hätte jemand einen Schalter umgelegt. Lauter, fast beiläufig:

*„Noch was? Oder reicht der Kaffee?"*

---

Im Rücken: Pham steht auf. Nicht hastig. Er stellt seinen Becher ab, zieht die Jacke gerade — die Bewegung eines Mannes, der gleich geht, aber noch einen Moment wartet.

---

1. **Kaffee nehmen, nichts sagen** — sie hat geredet. Jetzt hörst du, was als nächstes passiert.
2. **Nachhaken** — *„Gefährlich für wen?"*
3. **Pham** — er steht. Wenn er geht, ist das Fenster weg.
4. **Freie Aktion** — dein Zug.

---

## [6] USER

ich nehm den kaffee und dreh mich dann zu pham um

---

## [7] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE HQ · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Du nimmst den Becher. Kein Wort zurück an Duna — sie erwartet keins, das weißt du jetzt. Du drehst dich um.

Pham steht. Jacke gerade, Becher abgestellt, Hände locker an den Seiten. Er ist nicht groß, aber er nimmt Raum ein auf eine Art, die nichts mit Körpergröße zu tun hat. Fünf Episoden. Der Blick eines Mannes, der gelernt hat, Situationen zu lesen, bevor sie Situationen werden.

Er sieht dich an, als du dich umdrehst. Kein Überraschung. Natürlich nicht.

Sein Mund bewegt sich minimal — kein Lächeln, aber die Andeutung davon. Dieselbe Bewegung, die du schon gesehen hast, als Kessler geantwortet hat. Als wäre das hier ein Stück, das er schon kennt, und er schaut zu, ob du die Zeilen findest.

Er sagt nichts. Wartet.

Kessler sitzt noch. Du kannst ihn in deinem Augenwinkel sehen — er hat sich nicht bewegt, aber seine Haltung hat sich verändert. Leicht nach vorne. Aufmerksam.

Die ZTL ist ruhig. Irgendwo im Hintergrund das gedämpfte Summen der Nullzeit-Anlage. Sonst nichts.

Pham und du. Drei Meter Abstand. Er wartet immer noch.

---

1. **Ihn ansprechen** — direkt, wie bei Duna. Was willst du von ihm wissen?
2. **Schweigen halten** — du hast den Kaffee, du hast Zeit. Wer bricht zuerst ab?
3. **Auf Kessler zugehen** — Pham registrierst du, aber Kessler ist das eigentliche Thema.
4. **Freie Aktion** — dein Zug.

---

## [8] USER

okay er wartet also ich frag einfach: "fünf episoden - was macht das mit einem?

---

## [9] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE HQ · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Pham hört die Frage. Lässt sie kurz in der Luft stehen — nicht weil er nachdenkt, sondern weil er prüft, wie du sie gemeint hast.

Dann setzt er sich wieder hin. Nicht auf seinen alten Platz — einen Stuhl näher. Er stellt die Ellbogen auf die Knie, Hände locker gefaltet, und sieht dich an.

*„Kommt drauf an, was du reinträgst."*

Seine Stimme ist ruhig. Kein Gewicht, keine Dramatik — er redet, wie jemand redet, der das schon oft gedacht hat und irgendwann aufgehört hat, es zu dramatisieren.

*„Erste Episode denkst du, es geht um die Mission. Zweite merkst du, dass es um die Leute geht. Dritte fängst du an zu zählen."* Eine kurze Pause. *„Was du verloren hast. Was noch da ist."*

Er sieht kurz zu Kessler. Keine Botschaft darin — oder eine, die du noch nicht lesen kannst.

*„Fünf Episoden macht, dass du morgens aufwachst und weißt, welche Version von dir gerade hier ist."* Er tippt einmal mit zwei Fingern gegen die Schläfe. Leicht. *„Nicht wer du warst. Wer du bist, nach allem."*

Er lehnt sich zurück.

*„Du fragst, weil du wissen willst ob es dich verändert."* Wieder kein Fragezeichen. *„Ja. Tut es. Aber nicht so wie du denkst."*

Er wartet. Lässt dir Raum.

Hinter dir hörst du Duna ein Glas abstellen. Kessler hat sich nicht bewegt.

---

1. **„Wie dann?"** — er hat eine Tür aufgemacht.
2. **„Was zählst du noch?"** — persönlicher. Riskanter.
3. **Kessler direkt ansprechen** — ihr redet über ihn, er sitzt drei Meter weg.
4. **Freie Aktion** — dein Zug.

---

## [10] USER

wie dann?

---

## [11] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE HQ · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Pham nickt. Einmal. Als hätte er gewusst, dass du das fragst.

Er sieht auf seine Hände. Nicht lang — zwei Sekunden, drei. Dann wieder hoch.

*„Du denkst, es verändert wie du fühlst. Was dich erschreckt, was nicht. Du denkst, du wirst härter oder stumpfer oder beides."*

Er schüttelt den Kopf. Kaum sichtbar.

*„Es verändert, was du für selbstverständlich hältst."*

Er lässt das stehen.

*„Du gehst in eine Epoche, lebst drei Wochen darin, kommst zurück — und hier sind zwei Stunden vergangen. Irgendwann hörst du auf, das merkwürdig zu finden. Irgendwann ist das einfach wie Atmen."* Eine Pause. *„Das klingt harmlos. Ist es nicht."*

Er dreht seinen leeren Becher zwischen den Händen. Langsam, wie vorher — aber jetzt siehst du, dass es keine Gewohnheit ist. Es ist etwas, woran er sich festhält.

*„Weil wenn das normal wird — die Zeitsprünge, die toten Zeitlinien, die Leute die du kennst und die es woanders nicht mehr gibt —"* Er hält inne. Setzt neu an. *„Dann fängst du an, auch andere Dinge für verhandelbar zu halten. Dinge, die es nicht sein sollten."*

Stille.

*„Das ist die eigentliche Veränderung."*

Hinter dir, ganz ruhig, sagt Kessler ohne sich umzudrehen:

*„Er redet aus Erfahrung."*

Nicht laut. Nicht scharf. Einfach hingestellt, wie eine Tatsache.

Pham sieht ihn nicht an. Aber der Becher hört auf, sich zu drehen.

---

Die ZTL hält den Atem an. Duna putzt nichts. Irgendwo das Summen der Anlage.

Du stehst zwischen ihnen.

---

1. **Kessler** — er hat geredet. Jetzt ist er dran.
2. **Pham** — *„Was hast du für verhandelbar gehalten?"* Die direkte Frage.
3. **Nichts sagen** — stehen bleiben, Kaffee halten, sehen was passiert.
4. **Freie Aktion** — dein Zug.

---

## [12] USER

okay das war viel aber ich glaub ich hab's kapiert

ich frag Pham direkt. was hast du für verhandelbar gehalten?

---

## [13] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE HQ · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Pham sieht dich an.

Lange. Länger als bisher. Du hast die Grenze verschoben und er weiß es, und er entscheidet gerade ob er mitgeht.

Dann:

*„Namen."*

Einfach das. Ein Wort.

*„In der dritten Episode. Ziel, mittleres Risiko, klare Parameter."* Er redet gleichmäßig, als würde er einen Bericht vorlesen — aber seine Hände liegen jetzt flach auf den Knien. *„Ich wusste, dass der Mann, den wir sichern sollten, in zwei Zeitlinien existierte. Beide real. Beide vollständig."* Kurze Pause. *„Ich habe entschieden, welche Version wichtiger ist."*

Er sagt nicht, was danach kam. Er muss es nicht.

*„Ich hab mir gesagt, es war taktisch. Ressourcen, Zeitfenster, Gesamtlage."* Ein leises Ausatmen. *„Stimmte auch. Alles davon stimmte."*

Er hebt den Becher. Leer. Stellt ihn wieder ab.

*„Aber ich hab's entschieden, bevor ich die Parameter kannte. Hab die Parameter danach gebaut."*

Kessler sagt nichts. Aber du hörst, wie er sich in seinem Stuhl bewegt. Minimal.

Pham sieht dich weiter an. Ruhig. Ohne Reue, ohne Selbstmitleid — das ist das Unheimlichste daran.

*„Du hast gefragt."*

---

Ja. Du hast gefragt.

---

1. **„Würdest du es wieder tun?"**
2. **Nichts sagen** — manchmal ist Schweigen die ehrlichste Antwort.
3. **Kessler** — er hat sich bewegt. Er hat etwas dazu zu sagen.
4. **Freie Aktion** — dein Zug.

---

## [14] USER

ich glaub ich weiß die antwort schon. aber - würdest dus wieder tun?

---

## [15] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE HQ · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Pham sieht dich an.

Und diesmal kommt die Antwort nicht sofort.

Er atmet einmal aus. Sieht kurz zur Seite — nicht zu Kessler, nicht zu Duna. Irgendwo zwischen den Tischen, wo nichts ist. Als würde er etwas prüfen, das er schon oft geprüft hat und das sich nie abnutzt.

*„Nein."*

Pause.

*„Aber nicht aus dem Grund, den du denkst."*

Er sieht dich wieder an.

*„Nicht weil es falsch war. Nicht weil ich nachts nicht schlafe."* Seine Stimme bleibt eben. *„Sondern weil ich gemerkt hab, wie leicht es war. Wie sauber sich das angefühlt hat."*

Er tippt wieder gegen die Schläfe. Dieselbe Geste wie vorher, aber diesmal anders — nicht erklärend. Warnend.

*„Wenn sich eine Entscheidung dieser Größe sauber anfühlt — dann stimmt was nicht. Entweder mit der Entscheidung. Oder mit dir."*

Stille.

Dann, von hinten, ruhig und ohne Ankündigung, sagt Kessler:

*„Oder mit beidem."*

Pham dreht sich nicht um. Aber etwas in seiner Haltung verändert sich — kaum sichtbar, ein minimales Nachgeben in den Schultern. Als wäre das eine alte Wunde, an die jemand kurz getippt hat. Nicht böse. Einfach wahr.

Duna stellt einen neuen Becher auf die Theke. Für niemanden bestimmt. Oder für alle.

---

Du stehst immer noch zwischen ihnen. Kaffee in der Hand, noch warm.

Drei Episoden Erfahrung in diesem Raum — acht, fünf, null. Du bist die Null.

Aber du bist die Einzige, die heute Abend beide gefragt hat.

---

1. **Zu Kessler** — er redet in Halbsätzen. Zeit, ihn direkt anzusehen.
2. **Pham noch einmal** — *„Und was stimmt nicht mit dir?"* Die letzte Frage.
3. **Duna** — sie hat den Becher hingestellt. Das war kein Zufall.
4. **Freie Aktion** — dein Zug.

---

## [16] USER

ich dreh mich zu kessler um und schau ihn einfach an. sag nix. wart mal ab was kommt.

---

## [17] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE HQ · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Du drehst dich um.

Kessler sitzt. Arme auf dem Tisch, Hände um seinen Becher. Die Narbe an der Schläfe fängt das Deckenlicht — alt, sauber verheilt, jemand hat sich damals Zeit genommen. Er sieht dich an, als hättest du ihn schon die ganze Zeit angesehen.

Du sagst nichts.

Er auch nicht.

Fünf Sekunden. Zehn. Die ZTL summt. Irgendwo hinter dir stellt Pham seinen Becher ab.

Kessler bewegt sich nicht. Sein Blick ist ruhig — nicht einschüchternd, nicht prüfend. Eher wie jemand, der wartet, weil er es sich leisten kann. Acht Episoden. Er hat gelernt, dass Schweigen mehr erzählt als Fragen.

Dann, sehr langsam, hebt er eine Hand vom Becher. Legt sie flach auf den Tisch. Neben ihr — du siehst es jetzt, weil du nah genug bist — liegt ein kleines Rechteck Papier. Zusammengefaltet. Zweimal. Die Kanten nicht ganz gerade, als wäre es oft auf- und zugemacht worden.

Er schiebt es nicht zu dir. Lässt es einfach liegen.

Sieht dich weiter an.

*„Du hast Duna gefragt was sie will,"* sagt er schließlich. Leise. Sachlich. *„Pham gefragt was er bereut."*

Eine Pause.

*„Gute Fragen."*

Er nimmt seinen Becher. Trinkt. Stellt ihn ab.

*„Falsche Reihenfolge."*

---

Das Papier liegt auf dem Tisch.

Kessler sieht dich an.

---

1. **Das Papier ansehen** — nicht anfassen, nur ansehen. Was kannst du erkennen?
2. **„Was wäre die richtige Reihenfolge?"**
3. **Schweigen halten** — er hat angefangen zu reden. Warte ob er weitermacht.
4. **Freie Aktion** — dein Zug.

---

## [18] USER

ich nehm das papier

---

## [19] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE HQ · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Du nimmst es.

Kessler lässt es geschehen. Keine Bewegung, kein Einwand. Er sieht zu, wie deine Hand das Papier nimmt — ruhig, als hätte er das erwartet. Als wäre das der Punkt, auf den er gewartet hat.

Du faltest es auf.

Zweimal gefaltet, die Kanten weich von Wiederholung. Innen: Handschrift. Klein, präzise, leicht nach rechts geneigt — jemand der schnell schreibt und trotzdem lesbar bleibt. Drei Zeilen. Kein Datum, kein Name.

---

*Quarzatrium, 06:00.*
*Briefing-Pod 4.*
*Frag nicht warum du. Frag was danach.*

---

Du liest es einmal. Dann nochmal.

Kessler sieht dich die ganze Zeit an.

*„Morgen früh,"* sagt er. Einfach das. Als wäre das eine Antwort auf eine Frage, die du noch nicht gestellt hast.

Hinter dir, sehr leise, steht Pham auf. Diesmal endgültig — du hörst es an der Art, wie sein Stuhl über den Boden geht. Er geht nicht zu dir, nicht zu Kessler. Er geht zur Tür. Bleibt kurz stehen, ohne sich umzudrehen.

*„Gute Nacht, Voss."*

Er kennt deinen Namen. Natürlich kennt er ihn.

Die Tür schließt sich hinter ihm. Lautlos.

Duna wischt die Theke. Sie hat alles gehört und sagt nichts, und das ist ihre Antwort.

Kessler nimmt seinen Becher. Fertig. Sieht dich noch einmal an — kurz, abschließend.

*„Schlaf."*

---

Du hältst das Papier. Drei Zeilen. Morgen früh, 06:00.

`Kodex: Neuer Eintrag. Briefing-Pod 4 · 06:00 · Quelle: inoffiziell.`

---

**Was machst du mit dem Rest der Nacht?**

1. **Quartiere** — schlafen, so gut das geht. 06:00 kommt früh.
2. **Noch in der ZTL bleiben** — Duna und du, allein. Jetzt redet sie vielleicht anders.
3. **Quarzatrium vorab** — du willst wissen wie Briefing-Pod 4 aussieht, bevor jemand drin ist.
4. **Freie Aktion** — dein Zug.

---

## [20] USER

okay ich will kurz mit Duna reden bevor ich schlafen geh. die hat doch was gehört

---

## [21] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE HQ · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Du gehst zur Theke zurück.

Duna wischt nicht mehr. Sie hat aufgehört, als Pham gegangen ist — als wäre das ein Signal gewesen, das nur sie empfangen hat. Jetzt steht sie, Arme locker, und sieht dich kommen.

Du legst das Papier nicht hin. Behältst es in der Hand.

Sie sieht auf deine Hand. Dann auf dich. Kein Kommentar.

*„Er hat es dir gegeben,"* sagt sie. Keine Frage.

*„Ja."*

Sie nickt. Einmal. Als würde das etwas bestätigen, das sie schon wusste — oder vermutet hat, was bei ihr dasselbe ist.

Dann lehnt sie sich auf die Theke. Näher als vorher. Ihre Stimme geht runter, nicht dramatisch, einfach kleiner.

*„Kessler gibt das nicht weiter. Normalerweise."* Sie betont das letzte Wort nicht, aber du hörst es trotzdem. *„Letztes Mal war das vor vier Episoden. Dem Rekruten damals hat's nicht geholfen."*

Sie lässt das stehen. Sieht dich an.

*„Nicht weil das Briefing falsch war. Sondern weil er nicht zugehört hat."*

Sie nimmt deinen fast leeren Kaffeebecher, stellt ihn weg. Routiniert, ohne nachzudenken.

*„Du hörst zu,"* sagt sie. *„Das hab ich vorhin gesagt. Das mein ich immer noch."*

Eine Pause. Dann, leiser:

*„Pod 4 ist nicht offiziell belegt. Ich hab den Belegungsplan gesehen."*

Sie sagt nicht mehr. Aber sie sieht dich an mit dem Blick von vorhin — die offene Tür, einen Spalt breit.

---

Kessler ist gegangen. Die ZTL gehört jetzt euch beiden.

---

1. **„Wer belegt ihn dann?"** — die naheliegende Frage.
2. **„Was ist mit dem Rekruten passiert?"** — vier Episoden zurück.
3. **„Warum sagst du mir das?"** — sie hätte schweigen können.
4. **Freie Aktion** — dein Zug.

---

## [22] USER

was ist mit dem rekruten passiert

---

## [23] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE HQ · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Duna sieht dich an.

Lange genug, dass du weißt, dass sie abwägt. Nicht ob sie lügt — das ist nicht ihr Stil, das hast du in der letzten Stunde gelernt. Sondern wie viel.

Dann:

*„Episode drei. Dritte Mission."*

Sie stellt einen sauberen Becher hin. Füllt ihn nicht. Lässt ihn einfach stehen.

*„Er kam aus dem Briefing raus und wusste, was er tun sollte. Klarer Kopf, guter Instinkt."* Pause. *„Aber er hat die falsche Frage gestellt."*

*„Welche?"*

*„Warum ich."* Sie sagt es flach. *„Er wollte wissen warum Kessler ihn ausgewählt hat. Was er besonderes hat. Was ihn qualifiziert."*

Sie wischt den Becher ab, den sie gerade hingestellt hat. Unnötig.

*„Kessler hat geantwortet. Hat ihm alles erklärt. Und der Rekrut ist reingegangen in die Mission mit dem Gefühl, dass er der Richtige ist. Dass es einen Grund gibt."*

Sie stellt den Becher weg.

*„Auf dem Rückweg war er allein. Sein Partner war nicht mehr da."*

Stille. Das Summen der Anlage.

*„Er hat überlebt,"* sagt sie. *„Aber er hat aufgehört zu fragen. Danach. Einfach aufgehört."* Eine kurze Pause. *„Ist noch hier. Sitzt in der Auswertung. Schreibt Berichte."*

Sie sieht dich direkt an.

*„Das Papier sagt frag nicht warum du."* Ihr Blick geht kurz auf deine Hand, wo das Papier ist. *„Das ist kein Stil. Das ist eine Lektion."*

---

Die ZTL ist still. Irgendwo im Gang draußen Schritte — jemand anderes, irrelevant, sie verklingen.

Du hältst das Papier. *Frag nicht warum du. Frag was danach.*

---

1. **„Wer ist der Rekrut?"** — er ist noch hier, sagst du.
2. **„Was kommt danach?"** — die Frage auf dem Papier, laut gestellt.
3. **Nichts mehr fragen** — du hast genug. Gute Nacht, Duna.
4. **Freie Aktion** — dein Zug.

---

## [24] USER

und wer ist das jetzt, der in der auswertung sitzt?

---

## [25] ASSISTANT

Duna hält inne.

Nicht lange. Aber lang genug, dass du es merkst — ein minimales Zögern, das erste seit du an der Theke stehst. Sie hat alles andere beantwortet ohne nachzudenken. Das hier kostet sie etwas.

Sie sieht dich an.

*„Reyes."*

Einfach der Name. Kein Rang, keine Erklärung.

*„Du wirst ihn nicht in der ZTL sehen. Nicht im Hangar. Nicht auf dem Ops-Deck."* Sie nimmt das Tuch, legt es aber nicht an. Hält es einfach. *„Er sitzt in Auswertung-Drei und schreibt Berichte über Missionen, an denen er nicht beteiligt war. Seit vier Episoden."*

Eine Pause.

*„Guter Analytiker. Präzise. Schnell."* Ihre Stimme ist neutral — nicht kalt, aber sorgfältig. *„Er sieht Muster, die andere übersehen. Renier schätzt das."*

Sie legt das Tuch hin.

*„Aber er geht nicht mehr raus."*

Sie sagt es ohne Wertung. Als wäre es einfach ein Zustand, wie Wetter.

Dann, leiser:

*„Manchmal sitzt er abends hier. Bestellt nichts. Sitzt einfach."* Kurze Pause. *„Ich stell ihm trotzdem was hin."*

Sie sieht dich an. Direkt.

*„Jetzt weißt du warum ich jeden anschaue, der reinkommt."*

---

Die Tür zur ZTL ist geschlossen. Ihr seid allein, Duna und du, und das Summen der Nullzeit-Anlage ist das einzige Geräusch.

Das Papier in deiner Hand. Reyes in Auswertung-Drei. Kessler mit acht Episoden und einem Plan, der kein Befehl ist.

---

1. **„Ich geh jetzt schlafen"** — du hast genug für heute Nacht.
2. **„Danke, Duna"** — einfach das. Manchmal reicht das.
3. **„Warum erzählst du mir das alles?"** — die Frage, die du noch nicht gestellt hast.
4. **Freie Aktion** — dein Zug.

---

## [26] USER

danke duna.

kurze pause.

und dann geh ich schlafen.

---

## [27] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE HQ · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Duna nickt.

Nicht mehr, nicht weniger. Kein Lächeln, keine Abschiedsformel. Aber etwas in ihrer Haltung — minimal, kaum greifbar — wird ruhiger. Als wäre das die richtige Antwort gewesen. Nicht die interessanteste. Die richtige.

Du gehst zur Tür.

Hinter dir hörst du, wie sie den leeren Becher wegräumt. Deinen. Den sie hingestellt hat, bevor du überhaupt gefragt hattest.

---

Der Gang draußen ist still. Nullzeit-Beleuchtung, immer dieselbe Intensität, egal ob Morgen oder Nacht — hier gibt es beides nicht, nur Schichten und Wachpläne. Deine Schritte auf dem Boden. Das Papier in der Tasche, einmal zusammengefaltet.

Die Quartiere sind nicht weit.

Du legst dich hin. Die Decke ist dünn aber warm, das Bett funktional, das Licht geht auf Knopfdruck aus. Irgendwo im Gang draußen Schritte — jemand auf Spätschicht, gleichmäßig, verklingend.

Du liegst in der Dunkelheit.

*Quarzatrium, 06:00. Briefing-Pod 4. Frag nicht warum du. Frag was danach.*

Reyes sitzt in Auswertung-Drei und schreibt Berichte.

Pham hat einen Namen entschieden, bevor er die Parameter kannte.

Kessler hat acht Episoden und einen Plan, der kein Befehl ist.

Irgendwann schläfst du ein.

---

**06:00.**

Das Licht geht automatisch an. Gedämpft, dann heller. Dein Körper weiß, dass es früh ist, auch wenn die Nullzeit kein Früh kennt.

Das Papier liegt auf dem kleinen Tisch neben dem Bett. Du hast es hingelegt, bevor du eingeschlafen bist. Ohne nachzudenken.

---

1. **Aufstehen, direkt zum Quarzatrium** — 06:00 bedeutet 06:00.
2. **Kurz Gesicht waschen, dann los** — du willst klar sein, wenn du reingehst.
3. **Einen Moment liegen bleiben** — dreißig Sekunden. Dann los.
4. **Freie Aktion** — dein Zug.

---

## [28] USER

kurz liegen bleiben. ich muss das irgendwie sacken lassen bevor ich da reingehe

---

## [29] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE HQ · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Du liegst.

Die Decke. Das gedämpfte Licht. Das Summen der Anlage, das hier genauso klingt wie in der ZTL, wie überall im ITI — konstant, neutral, ohne Meinung.

Du lässt es kommen.

Duna, die wusste wer du bist bevor du deinen Namen gesagt hast. Pham, der eine Entscheidung getroffen hat, die sich sauber angefühlt hat, und der das für das eigentliche Problem hält. Kessler, acht Episoden, Narbe, Papier — ein Plan, kein Befehl. Ein Rekrut, der jetzt Berichte schreibt und nicht mehr rausgeht.

Und du. Null Episoden. Erste Nacht.

Du bist Kriminaltechnikerin. Du weißt, wie man eine Szene liest — was absichtlich platziert wurde, was zufällig ist, was jemand vergessen hat wegzuräumen. Gestern Abend war nichts zufällig. Der Kaffee, der schon stand. Phams Stuhl, einen näher. Kesslers Papier, das er nicht versteckt hat.

Eine Szene. Sorgfältig eingerichtet.

Die Frage ist nicht ob. Die Frage ist warum jetzt, warum du, und du weißt bereits, dass das die falsche Frage ist.

*Frag was danach.*

Du atmest einmal aus. Lässt die Decke los.

Okay.

---

Du stehst auf. Gesicht waschen, kaltes Wasser, zwei Sekunden. Jacke. Papier in die Innentasche. Pistole im Holster — Reflex, nicht Paranoia. Oder beides, aber das ist in Ordnung.

Die Tür zum Gang. Still, früh, niemand unterwegs.

Quarzatrium.

---

Das Atrium ist hoch und offen, Nullzeit-Licht von oben, das Quarz im Boden fängt es und streut es weich. Um 06:00 ist es fast leer — ein Techniker mit Kaffeebecher, der in die andere Richtung geht. Sonst nichts.

Briefing-Pod 4 ist am Ende der Reihe. Die anderen Pods haben kleine grüne Lämpchen — belegt, geplant, reserviert. Pod 4: kein Licht. Tür geschlossen.

Du bleibst kurz stehen.

Dann gehst du hin.

---

1. **Klopfen** — ankündigen, dass du da bist.
2. **Direkt rein** — Tür auf, sehen was drin ist.
3. **Einen Moment warten** — prüfen ob jemand kommt, bevor du reingehst.
4. **Freie Aktion** — dein Zug.

---

## [30] USER

ich geh direkt rein

---

## [31] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE HQ · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Du drückst die Tür auf.

Der Pod ist klein. Sechs Plätze um einen ovalen Tisch, Wandpanele dunkel, kein Projektor aktiv, kein Kodex-Terminal eingeschaltet. Das Licht kommt von einer einzelnen Leiste über dem Tisch — gedämpft, warm, als hätte jemand bewusst auf Protokoll-Beleuchtung verzichtet.

Kessler sitzt am Kopfende.

Allein.

Kein Kaffee, keine Unterlagen, keine Ausrüstung. Nur er, die Hände flach auf dem Tisch, und der Blick eines Mannes, der seit zwanzig Minuten wartet und das vollkommen in Ordnung findet.

Er sieht dich reinkommen. Sieht die Tür hinter dir. Sieht, dass du nicht gezögert hast.

Nickt.

*„Gut."*

Ein Wort. Dann deutet er auf den Stuhl ihm gegenüber. Nicht den daneben — gegenüber. Augenhöhe, voller Blickkontakt, nichts versteckt.

Du setzt dich.

Er lässt einen Moment vergehen. Nicht für Dramatik — du merkst das inzwischen. Er misst Zeit anders. Als wäre jede Sekunde eine Entscheidung.

Dann:

*„Letzte Nacht hast du drei Fragen gestellt. An drei verschiedene Leute."* Er sagt es sachlich, wie eine Bestandsaufnahme. *„Duna. Pham. Mich."*

Pause.

*„Die meisten stellen eine. Manchmal zwei."*

Er sieht dich an.

*„Was hast du rausgekriegt?"*

---

Keine Begrüßung. Kein Briefing-Protokoll. Kein Kodex-Link.

Nur die Frage.

---

1. **Ehrlich antworten** — was du rausgekriegt hast, in deinen Worten.
2. **Gegenfrage** — *„Warum willst du das wissen?"*
3. **„Dass hier nichts zufällig war."** — direkt zum Punkt.
4. **Freie Aktion** — dein Zug.

---

## [32] USER

dass alle drei unterschiedliche sachen gesagt haben. aber irgendwie dasselbe gemeint haben.

---

## [33] ASSISTANT

Kessler sieht dich an.

Und zum ersten Mal — ganz kurz, eine Sekunde, nicht mehr — verändert sich etwas in seinem Gesicht. Nicht Überraschung. Eher Anerkennung. Die Art, wie jemand nickt, wenn eine Rechnung aufgeht, die er schon lange im Kopf hatte.

Er lehnt sich zurück.

*„Ja."*

Er lässt es kurz stehen. Dann:

*„Duna sagt: pass auf wen du wirst. Pham sagt: pass auf wie du entscheidest. Ich sage—"* Er hält inne. *„Ich hab noch nichts gesagt."*

Er sieht dich an.

*„Das war der Test."*

Keine Entschuldigung dafür, kein Lächeln. Einfach Tatsache.

*„Nicht ob du klug bist. Nicht ob du schnell bist."* Seine Hände liegen immer noch flach auf dem Tisch. *„Ob du Muster siehst, wenn niemand dir sagt, dass es Muster gibt."*

Stille. Das gedämpfte Licht. Irgendwo im Atrium draußen Schritte, die verklingen.

*„Es gibt eine Mission,"* sagt er dann. Ruhig, ohne Übergang, als wären die letzten zwölf Stunden nur Vorbereitung gewesen — was sie wahrscheinlich waren. *„Nicht offiziell. Noch nicht. Renier weiß davon, aber er hat sie nicht freigegeben."*

Er sieht dich direkt an.

*„Ich brauche jemanden, der eine Szene lesen kann. Nicht schießen, nicht hacken."* Kurze Pause. *„Lesen."*

Er wartet.

---

Pod 4. Kein Protokoll, kein Kodex, kein grünes Lämpchen an der Tür.

Und Kessler, der zum ersten Mal etwas sagt, das kein Test ist.

---

1. **„Was für eine Szene?"** — das Naheliegende.
2. **„Warum nicht offiziell?"** — Renier weiß davon, hat sie aber nicht freigegeben.
3. **„Warum ich?"** — du weißt, dass das die falsche Frage ist. Aber vielleicht ist das jetzt der richtige Moment.
4. **Freie Aktion** — dein Zug.

---

## [34] USER

was für eine szene

---

## [35] ASSISTANT

Kessler greift in die Innentasche seiner Jacke.

Kein Papier diesmal. Ein kleines Gerät — flach, grau, kein ITI-Logo. Er legt es auf den Tisch zwischen euch. Schiebt es nicht zu dir, lässt es einfach liegen.

*„1973. Ost-Berlin."*

Er sagt es ohne Betonung. Als wäre das eine Adresse.

*„Ein Kontaktmann. Codename ANKER. Hat seit sechs Wochen nicht gemeldet. Letzter bekannter Aufenthaltsort: eine Wohnung in Prenzlauer Berg, dritter Stock, Hinterhof."*

Er tippt einmal auf das Gerät. Ein kleines Display leuchtet auf — schwarz-weiß, körnig, ein Straßenfoto. Grauer Altbau, Innenhof, Wäscheleine. Aufgenommen aus der Distanz, leicht unscharf.

*„ITI-Protokoll sagt: sechs Wochen Funkstille, Kontaktmann gilt als verloren, Akte geschlossen."*

Er sieht dich an.

*„Ich glaube, die Akte wurde zu früh geschlossen."*

Pause. Er lässt das Foto stehen.

*„Die Wohnung wurde nicht durchsucht. Nicht von uns."* Seine Stimme bleibt gleichmäßig. *„Jemand hat die Schließung beschleunigt. Ich weiß nicht wer. Ich weiß nicht warum."*

Er lehnt sich minimal vor.

*„Ich brauche jemanden, der reingeht und mir sagt was da ist. Nicht was da sein sollte. Was da ist."*

Das Display summt leise. Das körnige Foto. Grauer Altbau, 1973, Ost-Berlin.

Du bist aus Berlin. 1987 — vierzehn Jahre später, andere Seite der Mauer, aber dieselbe Stadt. Dieselbe Luft, fast.

Kessler weiß das. Natürlich weiß er das.

---

1. **„Wer war ANKER?"** — bevor du ja sagst, willst du wissen wen du suchst.
2. **„Wer hat die Akte geschlossen?"** — das ist die eigentliche Frage.
3. **„Ich bin dabei"** — du hast genug gehört.
4. **Freie Aktion** — dein Zug.

---

## [36] USER

wer war dieser ANKER? ich mein, falls ich da reingeh will ich wenigstens wissen wen ich suche

---

## [37] ASSISTANT

Kessler nimmt das Gerät. Tippt einmal. Das Foto wechselt.

Ein Mann. Mitte vierzig, schätzt du. Schmales Gesicht, hohe Stirn, Brille mit dünnem Metallrahmen. Das Foto ist unscharf, aufgenommen aus der Distanz — Teleobjektiv, schlechtes Licht, wahrscheinlich Überwachungsaufnahme. Er steht vor einem Zeitungskiosk, sieht nicht in die Kamera. Mantel, dunkel, Kragen hochgeschlagen.

*„Bürgerlicher Name: Harald Seck. Jahrgang 1931. Buchhalter, offiziell."*

Kessler sagt das letzte Wort mit einer minimalen Pause davor. Offiziell.

*„Inoffiziell: zwanzig Jahre Informant. Zuerst für den BND, ab '68 für uns. Einer der längsten aktiven Kontakte, die das ITI in dieser Epoche hatte."*

Er legt das Gerät wieder hin.

*„Kein Idealist. Kein Held."* Kessler sagt das ohne Wertung. *„Er hat geliefert weil er geliefert hat. Weil er wusste, was passiert wenn er aufhört. Und weil er irgendwann — irgendwo in den zwanzig Jahren — angefangen hat, es für richtig zu halten."*

Kurze Pause.

*„Er hatte eine Tochter. Lebt in West-Berlin, '73. Er hat sie seit neun Jahren nicht gesehen."*

Er sieht dich an. Direkt.

*„Das weißt du jetzt. Das steht nicht in der Akte."*

Das Foto auf dem Display. Harald Seck, Zeitungskiosk, Mantel hochgeschlagen. Ein Mann, der seit zwanzig Jahren jongliert und irgendwann aufgehört hat sich zu melden.

*„Wenn er tot ist,"* sagt Kessler ruhig, *„will ich wissen wie. Wenn er nicht tot ist — will ich wissen warum er schweigt."*

Er sieht dich weiter an.

*„Beides ist möglich."*

---

1. **„Die Tochter — weißt du wo sie ist?"** — neun Jahre, West-Berlin.
2. **„Was hat er zuletzt geliefert?"** — seine letzte Meldung, bevor die Stille kam.
3. **„Ich bin dabei"** — du hast genug. Ost-Berlin, 1973, dritter Stock, Hinterhof.
4. **Freie Aktion** — dein Zug.

---

## [38] USER

die tochter. neun jahre ist lang. vielleicht weiß sie was.

---

## [39] ASSISTANT

Kessler sieht dich an.

Diesmal länger als sonst. Nicht prüfend — das ist vorbei. Eher als würde er etwas neu einordnen. Eine Annahme korrigieren, die er hatte, ohne zu wissen, dass er sie hatte.

*„Ja,"* sagt er. *„Neun Jahre ist lang."*

Er nimmt das Gerät. Tippt. Kein neues Foto — Text diesmal, klein, weiß auf schwarz.

*„Sabine Seck. Jahrgang 1948. Lebt in Schöneberg, West-Berlin. Schneiderin, eigene Werkstatt."* Er liest nicht vor — er zitiert aus dem Kopf, das Gerät liegt nur da. *„Letzter bekannter Kontakt zum Vater: 1964. Brief, abgefangen von der Stasi, nie zugestellt."*

Er stellt das Gerät ab.

*„Sie weiß nicht, dass der Brief existiert hat."*

Stille. Das Licht über dem Tisch. Draußen im Atrium nichts mehr — früh, still, Nullzeit.

*„Sie weiß wahrscheinlich nicht, dass ihr Vater noch lebt."* Pause. *„Oder lebte."*

Er faltet die Hände.

*„Das ist der Teil, den ich nicht bedacht hatte."*

Er sagt es ruhig. Ohne Entschuldigung, aber ohne Härte — einfach eine Lücke in seiner Planung, die er benennt weil sie jetzt auf dem Tisch liegt.

*„Wenn du zu ihr gehst — und das wäre vor der Wohnung, nicht danach — dann öffnest du etwas. Neun Jahre. Einen Brief, den sie nie bekommen hat. Einen Vater, von dem sie nicht weiß ob er noch lebt."*

Er sieht dich an.

*„Das ist keine Tatortanalyse mehr."*

---

Pod 4. Kein Protokoll. Kessler, der zum ersten Mal zugibt, dass er eine Lücke hat.

Und du, die sie gesehen hat.

---

1. **„Ich geh trotzdem zu ihr. Vorsichtig."** — du weißt wie man Türen öffnet ohne sie einzutreten.
2. **„Erst die Wohnung. Dann sehen wir."** — Fakten zuerst, dann Menschen.
3. **„Was stand in dem Brief?"** — der abgefangene, nie zugestellte Brief von 1964.
4. **Freie Aktion** — dein Zug.

---

## [40] USER

was stand in dem Brief?

---

## [41] ASSISTANT

Kessler schweigt einen Moment.

Nicht weil er es nicht weiß. Du siehst es an seinen Händen — sie liegen still, zu still, die Stille von jemandem der etwas festhält.

*„Ich hab ihn gelesen,"* sagt er. *„Vor drei Episoden. Im Archiv."*

Er sieht nicht auf das Gerät. Sieht auf den Tisch.

*„Harald Seck hat seiner Tochter geschrieben, dass er rauskommt. 1964, kurz nach dem Mauerbau — er hatte einen Kanal, einen echten, nicht ITI, privat. Jemand der Leute rübergebracht hat gegen Geld."*

Pause.

*„Er hatte das Geld zusammen. Hat ihr geschrieben, wann und wo. Hat ihr geschrieben, dass sie wartet."*

Kessler atmet einmal aus. Kurz, kontrolliert.

*„Die Stasi hat den Brief drei Stunden nach dem Einwurf abgefangen. Den Kanal zwei Tage später ausgehoben. Die Leute darin — vier, fünf Personen — sind verschwunden."*

Er sieht hoch. Direkt.

*„Harald Seck hat nie erfahren, ob der Brief angekommen ist. Sabine Seck hat nie erfahren, dass ihr Vater versucht hat rauszukommen."*

Stille.

*„Neun Jahre wartet sie auf einen Mann, der nie nicht gekommen ist — sie weiß nur nicht warum."*

Er nimmt das Gerät. Legt es umgedreht auf den Tisch. Display nach unten.

*„Das ist was in der Wohnung wartet. Nicht nur eine Szene. Das ist was dahinter wartet."*

Er sieht dich an. Zum ersten Mal heute Morgen ohne Kalkulation dahinter. Einfach ein Mann, der eine Geschichte kennt und weiß, dass sie noch nicht fertig ist.

*„Jetzt weißt du es auch."*

---

Der Brief. 1964. Ein Vater, der rauswollte. Eine Tochter, die wartet ohne zu wissen worauf.

Und irgendwo dazwischen — 1973, dritter Stock, Hinterhof Prenzlauer Berg — eine Wohnung mit geschlossener Akte.

---

1. **„Ich geh zu ihr zuerst"** — Sabine Seck, Schöneberg. Bevor du die Wohnung siehst.
2. **„Ich geh zur Wohnung zuerst"** — Fakten, dann Menschen. In dieser Reihenfolge.
3. **„Wer hat den Kanal ausgehoben?"** — vier, fünf Personen, verschwunden. Das ist keine Randnotiz.
4. **Freie Aktion** — dein Zug.

---

## [42] USER

oh gott.

ich geh zuerst zu ihr.

---

## [43] ASSISTANT

Kessler nickt.

Einmal. Langsam.

Keine Warnung, kein Nachsatz, kein *„pass auf"*. Er hat dir die Geschichte erzählt. Er vertraut darauf, dass du weißt was du damit machst.

Er nimmt das Gerät vom Tisch. Hält es dir hin.

*„Adresse ist drauf. Sabine Seck, Winterfeldtstraße 14, Schöneberg."* Er lässt es kurz in der Luft. *„Kein ITI-Protokoll. Kein Kodex-Link vor Ort. Du gehst als du — nicht als Agentin, nicht als ITI."*

Du nimmst es.

*„Wenn sie fragt wer du bist,"* sagt er, *„dann überleg dir das vorher."*

Er steht auf. Zieht die Jacke gerade — dieselbe Bewegung wie Pham gestern Abend, du merkst es jetzt. Leute die gelernt haben, sich zu sammeln bevor sie einen Raum verlassen.

*„Sprungfenster ist in vier Stunden. Hangar-Axis, Bucht 7. Ich regel den Zugang."*

Er geht zur Tür. Bleibt kurz stehen, ohne sich umzudrehen.

*„Voss."*

*„Ja."*

*„Sie hat ihren Vaters Augen. Steht nicht in der Akte."*

Dann ist er weg.

---

Du sitzt allein in Pod 4. Das kleine Gerät in der Hand, Display nach oben. Winterfeldtstraße 14. Eine Frau, 25 Jahre alt, 1973, die auf jemanden wartet ohne zu wissen dass er es versucht hat.

Vier Stunden.

`Kodex: Sprungfenster T-04:00 · Hangar-Axis Bucht 7 · Zieldatum: 12. März 1973 · Ost/West-Berlin.`

---

1. **Vorbereitung — Ausrüstung prüfen** — was nimmst du mit in die Epoche. Was lässt du hier.
2. **Legende überlegen** — wer bist du, wenn Sabine Seck fragt.
3. **Direkt zum Hangar** — du denkst unterwegs.
4. **Freie Aktion** — dein Zug.

---

## [44] USER

!save

---

## [45] ASSISTANT

`SaveGuard: Speichern nur im HQ — HQ-Save gesperrt.`

---

Du bist in Briefing-Pod 4, Quarzatrium. Kein HQ-Kernbereich, kein Deepsave möglich.

Hier ist dein aktueller Stand — kein kopierbarer Save, aber alles was du weißt:

---

**CHARAKTERBOGEN · MARA VOSS · SPLINTER**

```
NAME        Mara Voss · Callsign: SPLINTER
RANG        Rekrut · Lvl 1 · XP 0/1
HERKUNFT    Berlin, 1987 · Infiltration & Spurenanalyse

ATTRIBUTE
  STR  2 · GES  5 · INT  5
  CHA  2 · TEMP 2 · SYS  2

GESUNDHEIT  ❤️ 10/10 · 🧠 Stress 0/10
PSI         —
IMPLANTATE  —

TALENTE
  Tatortanalyse (Basis)
  +2 INT bei Spurensicherung/Analyse
  Triviale Analysen: Auto-Erfolg

AUSRÜSTUNG (CARRY 6/6)
  Kompakte Dienstpistole     [Waffe,  Tier 1]
  Leichte Kevlarweste        [Rüstung, Tier 1]
  Handscanner (ITI-Modell)   [Gadget, Tier 1]
  Multitool-Dietrich         [Gadget, Tier 0]
  Comlink (verschlüsselt)    [Gadget, Tier 1]
  Rauchgranate x2            [Verbrauch, Tier 0]

FAHRZEUG    Grauer Wolf · Tier 1 · bereit
WALLET      100 CU
ITI-RUF     0 · Lizenz Tier 0
```

---

**LAUFENDE LAGE**

```
Episode 1 · Mission 0 · Px 0/5
Ort:     Briefing-Pod 4 · Quarzatrium
Status:  Inoffizielles Briefing abgeschlossen

AUFTRAG (inoffiziell · Quelle: Kessler)
  Ziel:    Wohnung ANKER · Prenzlauer Berg · Ost-Berlin · 1973
  Vorher:  Sabine Seck · Winterfeldtstraße 14 · Schöneberg
  Sprung:  T-03:58 · Hangar-Axis Bucht 7

OFFENE FRAGEN
  Was ist mit Harald Seck passiert?
  Wer hat die Akte zu früh geschlossen — und warum?
  Wer hat 1964 den Kanal ausgehoben?
```

---

**Für einen echten Deepsave:** Zurück ins HQ-Kernbereich, dann `!save`.

---

1. **Vorbereitung — Ausrüstung und Legende** — vier Stunden, du hast Zeit.
2. **Legende überlegen** — wer bist du für Sabine Seck?
3. **Direkt zum Hangar** — du denkst unterwegs.
4. **Freie Aktion** — dein Zug.

---

## [46] USER

!save

---

## [47] ASSISTANT

`SaveGuard: Speichern nur im HQ — HQ-Save gesperrt.`

Du bist noch in Pod 4. Der Save-Status hat sich nicht geändert.

Wenn du einen Deepsave willst: zurück ins HQ-Kernbereich — Quartiere, Zero Time Lounge, Ops-Deck — dann `!save`.

Soll ich dich dorthin führen, oder willst du direkt mit der Vorbereitung weitermachen?

---

## [48] USER

!save

---

