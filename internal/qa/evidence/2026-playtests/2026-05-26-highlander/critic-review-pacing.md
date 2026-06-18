# Critic-Review: feat/mission-pacing-anchor

**Modell:** claude-opus-4.7 (sub-agent), Synthese durch claude-opus-4.7 (main aus Reasoning-Chain rekonstruiert)
**Gelaufen:** 2026-05-27T17:46+02:00
**Diff-Hash:** ce9a0bca
**Hinweis:** Sub-Agent (`pacing_critic`, 3m46s) hat alle Greps und Reads durchgeführt, dann Output-Budget vor dem `write` aufgebraucht. Befunde aus der Reasoning-Chain (`.openclaw-cloud/agents/main/sessions/96105765-df61-40f0-8cab-3ca233e7eec8.jsonl`) extrahiert und hier verdichtet.

## Verdict

**NEEDS-WORK** vor Merge.

Drei substantielle Befunde — zwei davon Blocker, weil der Patch semantische Klammern setzt (`PHASE Infiltration` bis `PHASE Exfil`), die das kanonische Phasen-Modell nicht vollständig abdecken, und weil ein anderes Modul den Begriff „Mid-Mission" mit anderer Bedeutung verwendet (Fraktions-Briefing-Trigger, kein HQ-Wechsel). Die Kern-Idee (Szenen-Anker als SOLL, kein Mid-Mission-HQ, keine Mid-Mission-Sprünge) ist konsistent zu Pflicht-Invarianten und greift den Playtest-Befund sauber an. Nach Blocker-Fix mergebar.

## Konkrete Befunde

### 🔴 Blocker (must-fix vor Merge)

**B1 — Phase-Klammer „PHASE Infiltration … PHASE Exfil" ist lückenhaft.**

Mein Patch schreibt:
> *„Zwischen `PHASE Infiltration` und `PHASE Exfil` ist die HQ-Nullzeit gesperrt."* (meta/masterprompt_v6.md:125)

Das kanonische 12-Phasen-Modell (gameplay/kreative-generatoren-missionen.md, Mission-Template):

| SC | Phase |
|----|-------|
| 1 | Anreise |
| 2 | Auftakt |
| 3 | Infiltration |
| 4 | Kontakt |
| 5 | Konflikt I |
| 6 | Intel Twist |
| 7 | Konflikt II |
| 8 | Sicherung |
| 9 | Flucht |
| 10 | Showdown |
| 11 | Rücksprung |
| 12 | Nullzeit-Beat |

→ „Infiltration bis Exfil" deckt streng gelesen nur SC3 (Infiltration) und SC12 (Exfil/Nullzeit-Beat) ab. SC1 (Anreise) und SC2 (Auftakt) sind nicht durch das Verbot gedeckt — dort wäre HQ-Rückkehr semantisch erlaubt, weil keine `PHASE Infiltration` läuft.

Das Masterprompt-§C-Phasen-Modell (Zeile 92) wiederum nennt: *„Briefing → Infiltration → Kontakt/Intel → Konflikt → Exfiltration → Debrief"* — vereinfachtes 6-Phasen-Modell, das die Generator-Phasen zusammenfasst.

**Fix:** Klammer umformulieren auf „Zwischen `PHASE Briefing` (Ende) und `PHASE Debrief` (Anfang)" oder „ab Szenenstart SC 1/12 bis Exfil-Rücksprung (SC 12/12)". Das deckt alle Einsatz-Szenen ab und ist konsistent mit der bestehenden Definition *„Szene 1 beginnt ab IA-Transfer, Szene 12 endet mit dem Exfil-Rücksprung"* (Masterprompt §C Zeile 89).

Konkrete Änderung:
```diff
-  2. **Kein Mid-Mission-HQ-Rückkehr:** Zwischen `PHASE Infiltration` und `PHASE Exfil` ist die HQ-Nullzeit **gesperrt**.
+  2. **Kein Mid-Mission-HQ-Rückkehr:** Von `SC 01/12` (IA-Transfer) bis zum Exfil-Rücksprung in `SC 12/12` (bzw. `SC 14/14` für Rift-Ops) ist die HQ-Nullzeit **gesperrt**. Das umfasst alle Einsatz-Phasen — Anreise, Auftakt, Infiltration, Kontakt/Intel, Konflikt, Sicherung, Flucht, Showdown, Rücksprung.
```

---

**B2 — Begriffskollision „Mid-Mission" in toolkit-gpt-spielleiter.md.**

`systems/toolkit-gpt-spielleiter.md:183` definiert Briefing-Phasen:
> *„Briefing (HQ-Phase vor Szene 1, `SC 00/--`), Mid-Mission (ab Szenenhälfte) und [Debrief]..."*

Hier ist „Mid-Mission" ein **erlaubter Briefing-Trigger** für Fraktions-Intel oder Lage-Updates per Comlink — und meint **nicht** HQ-Rückkehr. Mein Patch schreibt aber:
> *„Auch indirekte HQ-Berührungen (Briefing-Auftrag mitten in Mission, neuer Loadout-Drop) sind verboten."* (meta/masterprompt_v6.md:125)

Direkter Wording-Konflikt: Eine bestehende, legitime Mechanik („Mid-Mission-Briefing per Comlink/Funk während laufender Mission") kollidiert mit meinem Verbot „Briefing-Auftrag mitten in Mission".

**Fix:** Mein Patch muss präzisieren, dass **Funk-/Intel-Einspielungen ohne HQ-Wechsel** erlaubt bleiben. Verboten ist nur die **erzählerische Rückkehr ins HQ** (Spieler ist physisch dort) oder ein **neuer Loadout-Drop** (Equipment-Lieferung über Sprung-Gate). Comlink-Briefings, Fraktions-Funk, Auftragserweiterung-per-Funk = OK.

Konkrete Änderung:
```diff
-  2. **Kein Mid-Mission-HQ-Rückkehr:** ... „Kurz verschnaufen", „im HQ nachfragen", „Equipment nachladen", „Klinik" sind als Erzählwendung **nicht** zulässig — nicht durch Comlink-Briefing, nicht durch Mini-Rücksprung, nicht durch Zwischenmontage. Auch indirekte HQ-Berührungen (Briefing-Auftrag mitten in Mission, neuer Loadout-Drop) sind verboten.
+  2. **Kein Mid-Mission-HQ-Rückkehr:** ... „Kurz verschnaufen", „im HQ nachfragen", „Equipment nachladen", „Klinik-Besuch" sind als Erzählwendung **nicht** zulässig — nicht durch Mini-Rücksprung, nicht durch Zwischenmontage. Auch ein neuer Loadout-Drop oder Sprung-Gate-Sendung mitten in der Mission ist verboten. **Erlaubt bleiben:** Comlink-/Funk-Kommunikation mit HQ-Operatoren, Fraktions-Briefings über Funk, Intel-Updates per Knochenleitung — alles, was den Operativen-Status nicht unterbricht und keine HQ-Szene erzwingt (siehe Mid-Mission-Briefing-Trigger in `systems/toolkit-gpt-spielleiter.md`).
```

---

### 🟡 Should-fix (empfohlen)

**S1 — „Anreise = SC1" im Generator-Template kollidiert mit Reise-Beats-Regel.**

`gameplay/kreative-generatoren-missionen.md`, Mission-Skelett-Tabelle:
> *„1 | Anreise | Sprung oder Reise"*

Mein Patch sagt:
> *„Reise-Beats innerhalb der Mission bleiben erlaubt (kurze Sprünge im selben Operationsgebiet, Stunden statt Tage), aber sind **HUD-Pause** statt eigene Szene und addieren keine Szenen-Zählung."* (meta/masterprompt_v6.md:126)

Wenn Anreise eine eigene Szene SC1 ist, dann sind Reise-Beats nicht „HUD-Pause statt Szene" — sie sind explizit Szene. Inkonsistenz im Wording.

**Fix-Vorschlag:** Im Patch klarstellen, dass die initiale Anreise (Sprung an IA, SC1) als Szene zählt, weitere Reise-Beats innerhalb der Mission (etwa von einem Tatort zum nächsten) HUD-Pause sind. Oder Generator-Tabelle anpassen, dass „Anreise" optional ist und nicht als Szene 1 reserviert werden muss.

Konkrete Änderung im Patch:
```diff
-Reise-Beats innerhalb der Mission bleiben erlaubt (kurze Sprünge im selben Operationsgebiet, Stunden statt Tage), aber sind **HUD-Pause** statt eigene Szene und addieren keine Szenen-Zählung.
+Reise-Beats innerhalb der Mission bleiben erlaubt — die initiale Anreise (Sprung an Insertion Anchor) ist SC1 (siehe Mission-Skelett in `gameplay/kreative-generatoren-missionen.md`); weitere Übergänge innerhalb des Operationsgebiets (zwischen Schauplätzen, Stunden statt Tage) sind **HUD-Pause** statt eigene Szene und addieren keine Szenen-Zählung.
```

---

**S2 — „aktiver Verfolgungsdruck" als Ausnahme ist Neukonzept ohne Anker.**

Mein Patch sagt:
> *„Innerhalb einer Mission keine narrativen Sprünge über >24 Stunden Spielzeit oder über >50 km Distanz (Stadtwechsel, Landwechsel) **ohne aktiven Verfolgungsdruck**."* (meta/masterprompt_v6.md:126)

Der Begriff „Verfolgungsdruck" taucht sonst nirgends im Regelwerk auf. Damit ist es Auslegungsspielraum für die KI-SL.

**Fix-Vorschlag:** Entweder Begriff streichen (Ausnahme entfällt → klarere Regel), oder konkretisieren als „aktive Verfolgung durch Gegnerfraktion mit eigenem HUD-Marker" (Anker schaffen).

Empfehlung: **Streichen.** Klare Regel > flexible Ausnahme. Wenn ein Wochen-Skip durch Verfolgung nötig ist, ist das eine eigene Mission („Verfolgungsjagd quer durch Europa"), nicht eine Strecke innerhalb einer Mission.

---

### 🟢 Nice-to-have / Beobachtung

**N1 — Kein Smoke-Watchguard für das neue Pflichtgate.**

Smoke-Lint-Liste (scripts/lint_*.py) deckt: arena, chronopolis, doc-links, hud-kodex, markdown, mission-generator, save-sync, signal-devices, umlauts. **Kein lint_pacing.py.** Das Pflichtgate ist also nur durch Prompt-Befolgung gesichert, nicht durch CI.

Vorschlag: später (eigener Branch) einen `lint_pacing.py` ergänzen, der prüft, ob im Masterprompt + kampagnenstruktur die SOLL-Sprache konsistent verwendet wird. Nicht jetzt mitnehmen.

---

**N2 — „Leitplanke"-Wording an anderen Stellen ist anderer Kontext.**

`core/zeitriss-core.md:903` (Austrittswinkel-Leitplanke), `characters/ausruestung-cyberware.md:51/63` (Item-Generierung-Leitplanken), `gameplay/kampagnenstruktur.md:1835/2026` (Psi-Balance, Chronopolis-Runtime), `systems/kp-kraefte-psi.md:170` (Hard-Sci-Fi-Leitplanke). Alles andere Kontexte — kein Pacing-Drift. **Nicht patchen.**

---

**N3 — Generator produziert noch Briefings mit Stadtwechseln.**

`gameplay/kreative-generatoren-missionen.md` Mission-Generatoren wurden nicht überprüft, ob sie aktuell Briefs produzieren, die innerhalb einer Mission Stadtwechsel verlangen (z.B. „Frankfurt → Berlin in derselben Mission"). Wenn ja, müsste der Generator nachgezogen werden, sonst gibt's Konflikt zwischen generierter Mission und Pflichtgate.

Vorschlag: nach diesem Patch im nächsten Playtest beobachten, ob Generator weiterhin „große Sprünge in einer Mission" produziert. Bei Bedarf: eigener Branch `chore/mission-generator-cleanup`.

---

## Module-by-Module-Check

(verdichtet aus den Greps des Sub-Agents)

| Modul | Greps | Befund | Verdict |
|---|---|---|---|
| meta/masterprompt_v6.md | Phasen, SC, HQ, SaveGuard, Pflichtgate | Patch-Hauptquelle. Phase-Klammer ist Blocker (B1). | **impact (B1+B2)** |
| gameplay/kampagnenstruktur.md | Leitplanke→SOLL, Phasen, Korridor, Briefing | Patch-Co-Quelle. Konsistent zum Masterprompt-Patch. | minor (B1-Referenz mitziehen) |
| gameplay/kreative-generatoren-missionen.md | Anreise, Reise, Mission-Template, Anomalie | „Anreise = SC1" kollidiert mit Reise-Beats-Regel (S1). Generator produziert evtl. noch Stadtwechsel (N3). | minor |
| systems/toolkit-gpt-spielleiter.md | Mid-Mission, Briefing, Pacing | „Mid-Mission (ab Szenenhälfte)"-Briefing-Trigger kollidiert mit Patch-Wording (B2). | **impact (B2)** |
| systems/gameflow/speicher-fortsetzung.md | Save, SaveGuard, !suspend/!resume | Konsistent. SaveGuard-Verstärkung durch Patch passt. | clean |
| core/spieler-handbuch.md | Leitplanke, Comlink, Mid-Mission, Briefing | „Comlink (Ohrstöpsel) - Standardausrüstung" — bestätigt, dass Funk-Briefings erlaubt bleiben müssen (B2-Fix). | minor |
| core/zeitriss-core.md | Leitplanke (Austrittswinkel-Kontext), Szenen | Anderer Kontext (N2). | clean |
| core/sl-referenz.md | HUD-Block, Phasen, Gate-HUD-Policy | HUD-Block-Regel konsistent. | clean |
| core/wuerfelmechanik.md | Anomalien, SG-Tabelle | Kein Pacing-Touch. | clean |
| characters/hud-system.md | HUD-Pause, Gate-HUD-Policy, Statusänderung | HUD-Pausen-Grenze im Patch konsistent zu §F. | clean |
| characters/zustaende.md | Stress, LP, Schwellen | Kein Pacing-Touch. | clean |
| characters/charaktererschaffung-grundlagen.md | Attribute, Talente | Kein Pacing-Touch. | clean |
| characters/ausruestung-cyberware.md | Leitplanke (Item-Gen), Generative Items | Anderer Kontext (N2). | clean |
| systems/kp-kraefte-psi.md | Psi-Heat, Reichweite, Leitplanke (Hard-SF) | Anderer Kontext (N2). | clean |
| systems/currency/cu-waehrungssystem.md | Honorar, Bonus-Strukturen | Kein Pacing-Touch. | clean |
| systems/gameflow/cinematic-start.md | Onboarding-Sequenz | Kein Pacing-Touch. | clean |
| gameplay/kampagnenuebersicht.md | Arc, Episoden | Konsistent. | clean |
| gameplay/kreative-generatoren-begegnungen.md | Encounter-Tabellen | Kein direkter Pacing-Touch. | clean |
| gameplay/fahrzeuge-konflikte.md | Verfolgungsjagden, Reisen | Konsistent (Verfolgungsjagden bleiben eigene Szenen). | clean |
| gameplay/massenkonflikte.md | Zeitsprung-Mech (eines Fahrzeugs) | Anderer Kontext (Fahrzeug-Manöver, nicht Mission-Sprung). | clean |

## Empfehlung

**Merge mit Nachzug.** Konkret:

1. **B1 fixen** (Phase-Klammer auf SC-Bereich umstellen) — Pflicht.
2. **B2 fixen** (Funk/Comlink-Briefings explizit erlauben) — Pflicht.
3. **S1 fixen** (Anreise-SC1-Klarstellung in Reise-Beats-Regel) — empfohlen, kostet 1 Zeile.
4. **S2 fixen** (Verfolgungsdruck-Ausnahme streichen oder ankern) — empfohlen, vereinfacht die Regel.
5. **N3 nicht in diesem Branch** — Generator-Cleanup ist eigener Branch.
6. **N1 nicht in diesem Branch** — Smoke-Watchguard ist eigener Branch.

Nach Fix: `bash scripts/smoke.sh` nochmal laufen lassen, `git commit --amend`, force-with-lease push, Flo PR-Review.

Patch-Qualität insgesamt: **gut bis sehr gut**. Die drei Kernregeln greifen den Playtest-Befund präzise an, sind konsistent zu Pflicht-Invarianten (Save-Schema, 12-Szenen-Mission, SaveGuard-Mechanik), und das Wording ist hinreichend hart („starkes SOLL", „**nicht** zulässig", konkrete Schwellen). Die zwei Blocker sind Wording-Glitches, keine Design-Probleme.
