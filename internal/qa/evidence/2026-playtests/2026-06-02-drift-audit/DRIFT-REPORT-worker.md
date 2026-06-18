# ZEITRISS Drift-Report (Worker)

> Lese-Audit vom 2026-06-02, Worker-Sub-Agent. Messlatte: `zeitriss-audit/VISION-2026-06-02.md`.
> Reiner Soll-Abgleich, kein Kanon-Content angefasst. Alle Fundstellen mit grep/read verifiziert.

## Executive Summary

Die drei schlimmsten Drifts:

1. **Strang-Wahl im Briefing fehlt komplett (Soll 1).** Das Briefing-Output-Pflichtgate (`meta/masterprompt_v6.md` §C) erzwingt **„Hauptziel (genau eines)"**. Die Mission-Eröffnung serviert einen festen Marschbefehl, keine 2–3 wählbaren Stränge. Die Strang-Wahl existiert nur als HQ-*Mission*auswahl (`core/zeitriss-core.md:1247`), nicht *im* Briefing einer laufenden Mission.
2. **Kein harter konkreter Kern-Auftrag erzwungen (Soll 2).** Das Mission-Integrität-Pflichtgate (§C) schützt nur Länge/Phasen/Anti-Skip — es verlangt **nirgends** Ort + Ziel-Objekt/Person + klares Erfolgskriterium als Pflicht. Die Mission kann „läuft irgendwohin", solange sie im Szenen-Korridor bleibt.
3. **Pacing-Doku arbeitet aktiv gegen Dichte (Soll 3 + 4).** `kampagnenstruktur.md:1036-1039` (`Mehr Szenen bedeuten mehr Raum für Spannung`, `Länge flexibel erweitern`) und die Dauer-Tabelle `60-75 min` (`kampagnenstruktur.md:813`) widersprechen Flos Soll von **25–30 Min, dicht, zielgerichtet**.

---

## Pro Soll-Kriterium

### Soll 1 — Strang-Wahl im Briefing → **VERLETZT**

**Was Flo will:** Briefing serviert 2–3 Stränge/Angriffspunkte zur Wahl, der Spieler wählt selbst.

**Fundstellen:**

- `meta/masterprompt_v6.md` §C Briefing-Output-Pflichtgate, Regel 1:
  > „**Hauptziel (genau eines):** Klares Verb + Objekt + ggf. Bedingung."
  Das ist die direkte Drift-Quelle. Nebenziele sind ausdrücklich „optional" und „Opt./Bonus" — also Zusatz-Häkchen, **keine Alternativ-Stränge zur Wahl**.
- `meta/masterprompt_v6.md` §C Pflicht-Output-Format (ASCII-Box):
  > `Hauptziel: <Verb> <Objekt> … / Opt.: … / Bonus: …`
  Struktur kennt nur ein Hauptziel + Anhängsel, kein „Wähle Strang A/B/C".
- `gameplay/kreative-generatoren-missionen.md:145-170` Core-Briefing-Baukasten: zieht **einen** Anchor + **einen** Auftragstyp. Kein Mechanismus für parallele Angriffspunkte.
- **Wo die Wahl tatsächlich lebt:** `core/zeitriss-core.md:1242-1268` (§Kampagnenverlauf & Sandbox):
  > „Zwischen den Missionen im HQ können die Spieler oft wählen, welcher Spur sie als nächstes folgen wollen … mehrere **Einsatzmöglichkeiten** … drei Hinweise, die zu unterschiedlichen Folge-Missionen einladen (Pompeji / Lakehurst / Neo-Tokyo)."
  Das ist **Missions**-Wahl im HQ, nicht **Strang**-Wahl im Briefing einer Mission. Genau hier ist die Lücke: Das gute Wahl-Prinzip existiert, aber auf der falschen Skala — zwischen Missionen, nicht beim Briefing-Einstieg in *die eine* Mission.

**Drift-Diagnose:** Das #3182-Gate hat aus dem Briefing einen Single-Objective-Befehl gemacht. Innerhalb einer Mission gibt es keinen Punkt, an dem der Spieler zwischen 2–3 Wegen/Angriffspunkten wählt („Storm über das Dach ODER durch den Keller ODER Social-Engineering am Empfang"). Die Sandbox-Freiheit (zeitriss-core) ist Makro-Ebene; die Briefing-Wahl-Mikro-Ebene fehlt.

### Soll 2 — Konkreter Mission-Kern, kein Leerlauf → **TEILWEISE / Tendenz VERLETZT**

**Was Flo will:** Jede Mission hat einen harten, abschließbaren Kern-Auftrag mit Ort + Ziel-Objekt/Person + klarem Erfolg. NICHT „beobachte die Lage, sammle Hinweise, läuft irgendwohin".

**Fundstellen:**

- `meta/masterprompt_v6.md` §C Briefing-Output-Pflichtgate Regel 3:
  > „**Erfolgskriterium pro Ziel (knapp):** Was zählt als erfüllt? Einfache Prädikate"
  → Das ist der **einzige** Hebel, der Richtung „konkret" zeigt — aber es prüft nur die *Formulierung* des Ziels, nicht ob die Mission einen **harten Action-Kern** hat. Ein „Hauptziel: Lage dokumentieren / Erfüllt, wenn 3 Hinweise gesichert" passt formal durchs Gate und ist trotzdem genau der Leerlauf, den Flo verachtet.
- `gameplay/kreative-generatoren-missionen.md:153` Briefing-Baukasten „People first":
  > „Mindestens 60 % der Core-Briefings drehen sich um Personen- oder Einflussziele (Schutz, Exfil, Umstimmen) statt reiner Objekt-Raids."
  → Gut für Varianz, aber gibt keinen **Action-Kern-Zwang**. „Beschatten" und „dokumentieren" stehen gleichberechtigt in der Verb-SSOT (§C Regel 1) neben „ausschalten/sichern" — das öffnet die Tür für die zähen Observier-Missionen.
- `meta/masterprompt_v6.md` §C Mission-Integrität-Pflichtgate: schützt **Länge, HQ-Sperre, Zeit/Stadt-Sprung** — aber **kein Wort** zu „muss harten konkreten Kern-Auftrag haben". `grep` bestätigt: kein „Kern-Auftrag"-Pflichtbegriff im gesamten Repo.

**Drift-Diagnose:** Es gibt keine Regel, die sagt „die Mission braucht ein greifbares Objekt/Person an einem konkreten Ort und ein hartes Abschluss-Event". Das Verb-Set erlaubt explizit Beilage-Verben (beschatten/dokumentieren) als Hauptziel. Genau Flos Anti-Beispiel.

### Soll 3 — Spielzeit 25–30 Min, ~12 Szenen, dicht → **VERLETZT (Doku arbeitet dagegen)**

**Fundstellen:**

- `gameplay/kampagnenstruktur.md:813` Dauer-Tabelle:
  > „**Mission (Core-Op)** | 60-75 min | **12 Szenen** | „Netflix-Folge""
  → Direkter Widerspruch zu Flos „25–30 Min". Selbe Szenenzahl (12), aber doppelte Soll-Dauer ⇒ jede Szene wird auf 5–6 Min gedehnt statt dicht gehalten.
- `gameplay/kampagnenstruktur.md:1036-1039` (sl-referenz spiegelt es bei `core/sl-referenz.md` ~1037):
  > „Plane zu Beginn **mindestens zwei Szenen für Ankunft, Beobachtung oder Planung** ein, bevor der erste große Konflikt losbricht. Die SL darf die **Länge flexibel erweitern** … **Mehr Szenen bedeuten mehr Raum für Spannung.**"
  → Das ist die schädlichste Einzelzeile gegen Soll 3+4: sie *belohnt* Dehnung und Vor-Action-Leerlauf explizit.
- `gameplay/kampagnenstruktur.md:101`:
  > „Handlungsbögen zu verlängern, falls die Spieler z. B. unerwartete Nebenwege einschlagen."
- **Gegengewicht (gut, nicht anfassen):** §C Mission-Integrität Regel 1 sagt bereits korrekt: „routinemäßige Verlängerung durch Beschreibungs-Dehnung, Reise-Beats oder Side-Talk ist **nicht** zulässig" und „Bei Szene 8+ ohne klaren Pfad zu Exfil aktiv auf Klimax zusteuern". Dieser Teil zieht in Flos Richtung — er wird aber von den Zeilen oben (1036-1039) konterkariert. **Cross-File-Widerspruch innerhalb desselben Files.**

**Drift-Diagnose:** Zwei Stimmen im selben File: Das neue Gate (§C) drückt auf Dichte, der alte Pacing-Text (1036-1039 + Tabelle 60-75min) drückt auf Länge. Letzterer gewinnt im Zweifel, weil er konkret „mehr Szenen = mehr Spannung" sagt.

### Soll 4 — Action ist Kern, Aufklärung ist Beilage → **TEILWEISE**

**Fundstellen:**

- **Pro Action (gut):** Es gibt starke, neue Action-Gates — Kampfszenen-Pflichtgate und Bosskampf-Pflichtgate (§C, mehrphasig, cineastisch). Das *Kampfgefühl* ist exzellent abgesichert.
- **Gegen Action-als-Kern:** Das Mission-Skelett `gameplay/kreative-generatoren-missionen.md:95-113` (Core 12-Step) verteilt: Anreise (1), Auftakt/Lage sondieren (2), Infiltration (3), Kontakt/Info (4), erst SC5 erster Konflikt. → **Vier Szenen Vorlauf vor der ersten Action.** Bei 25-30-Min-Soll ist das zu viel Aufklärungs-Beilage vorne.
- `gameplay/kampagnenstruktur.md:1036-1037`: „mindestens zwei Szenen für Ankunft, Beobachtung oder Planung, **bevor der erste große Konflikt losbricht**" — zementiert den Action-späten Aufbau.
- Die Verb-SSOT (§C) stellt „dokumentieren/beschatten" gleichrangig neben Kampf-Verben → Aufklärung kann legitimes Hauptziel sein (siehe Soll 2).

**Drift-Diagnose:** Action ist mechanisch top abgesichert, aber **dramaturgisch nach hinten geschoben**. Es fehlt die Klarstellung „Action ist der Kern, Verschwörung läuft nebenbei während der Action mit". Das 12-Step-Skelett ist gut (Flo will es behalten), braucht nur einen Fokus-Satz, dass Aufklärung *in* die Action eingewoben wird statt ihr vorgelagert.

### Soll 5 — Kein Echtzeit-Warten → **ERFÜLLT**

**Fundstellen:**

- `grep` über alle Files: **kein** „warte 48h", „in Echtzeit", „Stunden/Tage warten" als Spielmechanik gefunden. Die Treffer auf „rechtzeitig" sind antagonist_goals (z. B. `kreative-generatoren-missionen.md:660`), keine Echtzeit-Warte-Aufforderungen.
- `meta/masterprompt_v6.md` §F HUD-Präsenz-Policy + §C Mission-Integrität Regel 3:
  > „weitere Übergänge innerhalb des Operationsgebiets … sind **HUD-Pause** statt eigene Szene"
  → Das ist genau Flos „Zeitsprünge = HUD-Pause, nicht Spiel-Leerlauf". Sauber abgedeckt.

**Drift-Diagnose:** Keine Drift. Kein Patch nötig. (Restrisiko: Exfil-Warteszenen mit W6-Spotlight, `kampagnenstruktur.md:945-983` — aber die sind *aktiv* (Spannungs-Eskalation), kein Leerlauf-Warten. Bleibt konform.)

### Soll 6 — HQ-Loop + Save-Sichtbarkeit → **ERFÜLLT / TEILWEISE**

**Fundstellen:**

- HQ-Loop voll abgedeckt: `core/spieler-handbuch.md:96-106, 213, 261-275` (HQ als eigener Spielabschnitt: skillen, equipen, Klinik, Werkstatt, Roleplay, Forschungen/Gerüchte). Debrief→HQ→Briefing-Kette in §C Mission-Transition-Pflichtgate verbindlich.
- Save-Sichtbarkeit: §C Save-State-Pflichtgate (Briefing-Greeting) erzwingt, dass der Save-Stand wortwörtlich zitiert wird; §F Regie-Layer-Pflichtbeats (Weltstatus-Pflichtsatz aus `arc.factions/questions/hooks`) zeigen Welt-Entwicklung beim Wiedereinstieg.
- **Kleine Lücke:** Flos „beim Speichern/Laden sieht der Spieler, was sich in der Zwischenzeit getan hat (**Forschungsfortschritt**, Welt-Entwicklung)" — Welt-Entwicklung ist via Weltstatus-Pflichtsatz da, expliziter **Forschungsfortschritt** als sichtbares Delta ist nicht hart verankert. Niedrige Priorität, nicht Teil des akuten Drifts.

**Drift-Diagnose:** Im Kern erfüllt. Kein chirurgischer Patch im Rahmen dieses Audits nötig.

---

## Konkrete Patch-Kandidaten

> Chirurgisch, im Geist von Flos „nur ein paar feine Sätze, die den Fokus auf den Kern setzen". Reihenfolge = Priorität.

### PK-1 (höchste Prio) — Strang-Wahl ins Core-Briefing zurückholen

- **Datei/Sektion:** `meta/masterprompt_v6.md` §C Briefing-Output-Pflichtgate, Regel 1 „Hauptziel (genau eines)".
- **Was ändern:** Hauptziel bleibt genau eines (Score-Screen-Mechanik nicht brechen!), aber **ergänze einen Pflichtsatz**, dass das Briefing **2–3 wählbare Angriffspunkte/Vorgehenswege auf dasselbe Hauptziel** anbietet, die der Spieler wählt. Beispiel-Wording: *„Das Hauptziel ist genau eines, aber das Briefing serviert dem Spieler 2–3 erkennbar verschiedene Angriffspunkte/Wege dorthin (z. B. ‚über das Dach / durch den Keller / als Gast getarnt am Empfang'). Der Spieler wählt den Strang — der Marschbefehl ist das Ziel, nicht der Weg."*
- **Ergänzend** in der ASCII-Box (§C Pflicht-Output-Format) eine Zeile `Angriffspunkte: (1) … (2) … (3) …` **vor** den Spieler-Optionen.
- **Warum:** Stellt Soll 1 her, ohne die „genau ein Hauptziel"-Mechanik (Debrief-Spiegel ✓/✗, Continuity-Anker) zu zerstören. Wahl auf Weg-Ebene, nicht Ziel-Ebene.
- **Zweitstelle:** `gameplay/kreative-generatoren-missionen.md:145-170` Core-Briefing-Baukasten — denselben „2–3 Angriffspunkte"-Satz spiegeln, damit Generator sie produziert.

### PK-2 — Harten konkreten Kern-Auftrag erzwingen

- **Datei/Sektion:** `meta/masterprompt_v6.md` §C Mission-Integrität-Pflichtgate (als **neue Regel 4** oder als Satz in Regel 1).
- **Was ändern:** Pflichtsatz einfügen: *„Jede Core-Mission hat einen **harten, abschließbaren Kern-Auftrag**: konkreter Ort + greifbares Ziel-Objekt/Person + klares Abschluss-Event (gesichert / rausgeholt / ausgeschaltet / festgenommen). ‚Lage beobachten' oder ‚Hinweise sammeln' ist **nie** das Hauptziel, sondern höchstens Beilage während des Kern-Auftrags."*
- **Warum:** Schließt die Soll-2-Lücke direkt. Macht Flos Anti-Beispiel („läuft irgendwohin") zur Regelverletzung.
- **Ergänzend:** §C Briefing-Output-Pflichtgate Verb-SSOT — Hinweis, dass „dokumentieren/beschatten" als **alleiniges** Hauptziel in Core-Ops unzulässig ist (mind. ein Action-/Sicherungs-Verb muss das Hauptziel tragen). Nicht die Verb-Liste löschen — nur die Beilage-Verben als Solo-Hauptziel sperren.

### PK-3 — Pacing-Doku auf Dichte umstellen (Soll 3+4)

- **Datei/Zeile:** `gameplay/kampagnenstruktur.md:1036-1039`.
- **Was ändern:** Den Satz *„Die SL darf die Länge flexibel erweitern … Mehr Szenen bedeuten mehr Raum für Spannung."* **ersetzen** durch eine Dichte-Linie: *„Die Mission bleibt dicht und zielgerichtet — der 12-Szenen-Korridor ist die Soll-Länge, nicht die Untergrenze. Vorlauf-Szenen (Ankunft/Beobachtung) werden knapp gehalten; Aufklärung läuft **während** der Action mit, nicht ihr vorgelagert."*
- **Zweitstelle:** `gameplay/kampagnenstruktur.md:813` Dauer-Tabelle — `60-75 min` auf Flos Soll **`25-30 min`** korrigieren (Core-Op-Zeile). Achtung: prüfen, ob die Zahl woanders referenziert wird (grep `60-75` / `60–75` vor dem Patch).
- **Drittstelle:** `kampagnenstruktur.md:101` (Verlängerungs-Lizenz bei Nebenwegen) — auf „Nebenwege bleiben innerhalb des Korridors, keine Arc-Verlängerung als Default" eindampfen.
- **Warum:** Beseitigt den Cross-File-Widerspruch (Gate sagt „dicht", Pacing-Text sagt „dehnen").

### PK-4 (niedrige Prio) — Action-Kern-Fokussatz im 12-Step

- **Datei/Sektion:** `gameplay/kreative-generatoren-missionen.md:95` Core 12-Step Mission Template (Kopf-Notiz darüber).
- **Was ändern:** Ein Satz: *„Action ist der Kern jeder Core-Op; Aufklärung/Verschwörung wird **nebenbei während** der Infiltrations- und Konflikt-Szenen aufgedeckt, nicht als eigene Beobachtungs-Phase vorgeschaltet. SC1–2 bleiben knapp."*
- **Warum:** Setzt Soll 4 als Fokus, ohne das (gute) Skelett umzubauen. Rein additive Klarstellung.

---

## Cross-File-Widersprüche

1. **Dichte vs. Länge (innerhalb `kampagnenstruktur.md`):** §C Mission-Integrität Regel 1 (Zeilen ~117, „keine routinemäßige Verlängerung", „bei SC8+ auf Klimax zusteuern") **vs.** `kampagnenstruktur.md:1036-1039` („Länge flexibel erweitern, mehr Szenen = mehr Spannung") + Dauer-Tabelle `813` (`60-75 min`). Der neue Gate-Text und der alte Pacing-Text ziehen gegeneinander.
2. **Strang-Wahl: Skalen-Mismatch:** `core/zeitriss-core.md:1247` verspricht „echte Freiheit … Spieler steuern den Pfad" (HQ-Missionswahl) — der Spieler-erwartete „ich wähle meinen Weg"-Eindruck wird aber im Briefing (`masterprompt §C`, ein Hauptziel) nicht eingelöst. Spieler-Handbuch + zeitriss-core wecken Wahl-Erwartung, das Briefing-Gate verweigert sie auf Mikro-Ebene.
3. **Verb-SSOT vs. Action-Kern:** §C erlaubt „beschatten/dokumentieren" als Hauptziel-Verben, während Flos Vision (Soll 4) Aufklärung zur Beilage degradiert. Interner Zielkonflikt im selben Gate.

---

## Risiko-Hinweise (was beim Patchen NICHT kaputtgehen darf)

- **Score-Screen / Debrief-Spiegel-Mechanik:** Das „genau ein Hauptziel" ist Anker für den Debrief-✓/✗-Spiegel und die `arc.hooks[]`-Folgespur-Logik (§F Debrief, §C Debrief-Spiegel). PK-1 darf das Hauptziel **nicht** auf mehrere aufsplitten — nur Weg-/Angriffspunkt-Wahl ergänzen, Ziel bleibt singulär. Sonst bricht der Score-Screen.
- **Continuity-Anker-Pflicht (§C Regel 4):** Nicht antasten. Der Rückverweis auf Vor-Mission (`arc.hooks[]` etc.) ist gut und stützt Soll 6.
- **MS1-2-Tonfall-Pflichtgate (Anti-Onboarding-Hammer):** Beim Schärfen des „harten Kern-Auftrags" (PK-2) **nicht** versehentlich Welt-Stakes in MS1-2 zulassen. Der Kern-Auftrag in MS1-2 bleibt klein und konkret (Person beschatten/sichern), nicht „Atomkrieg verhindern". PK-2-Wording so halten, dass „konkret + hart" ≠ „große Stakes".
- **SaveGuard / HQ-only-Save / Mission-Transition-Pflichtgate:** Alle Phasen-/Save-Gates (§C, §I) sind orthogonal zu den Patches und müssen unberührt bleiben.
- **Kampfszenen- & Bosskampf-Pflichtgate:** Sind gut und stützen Soll 4 — nicht verwässern. PK-4 ist additiv.
- **Rift-Ops-Sonderweg:** PK-1/PK-2/PK-4 gelten **nur für Core-Ops**. Rift-Briefing (max. 5 Stichpunkte, Fix-Objectives `Secure Anchor`/`Trace Leads`/`Neutralize Weakness`/`Recover Sample`, kein Continuity-Zwang) nicht anfassen — beim Patchen explizit „Core-Ops"-Scope schreiben, sonst bricht der Rift-Pfad.
- **Dauer-Zahl `60-75 min` (PK-3):** Vor Änderung grep auf alle Vorkommen (`60-75`, `60–75`, evtl. Tests/Fixtures im Repo), damit kein referenzierender Schema-/Doku-Test rot wird.
- **`zeitriss-core.md:1247` Missionsauswahl (HQ):** NICHT entfernen — das ist die *gute* Makro-Wahl. PK-1 ergänzt die Mikro-Wahl im Briefing, ersetzt die HQ-Wahl nicht.
