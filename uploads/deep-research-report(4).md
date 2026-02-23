# Deep-Research-Audit: pchospital-lab/ZEITRISS-md (Spielinhalte, Regelkonsistenz, Fix-Backlog)

## Archivhinweis (Status 2026-02-23, nachgezogen)

Dieses Upload-Artefakt ist als **Eingangsquelle abgeschlossen**. Die priorisierten
P0/P1-Startpunkte aus diesem Report wurden für den ersten Umsetzungsblock
bereits im Repo abgearbeitet und im operativen QA-Pfad dokumentiert.

- ZR-001 (Exploding/Burst-Cap): abgeschlossen.
- ZR-002 (Px-Semantik ohne Default-Strafabzug): abgeschlossen.
- ZR-003 (Px-Scope solo/npc-team vs. gruppe): abgeschlossen.
- ZR-004 (HQ-Loop-Invariante, kein Default-Skip): abgeschlossen.
- ZR-005 (Chronopolis/Tod ohne Free-Respawn): abgeschlossen.
- ZR-006 (Physicality-Gate: Armbänder-Regel): abgeschlossen (Armbänder nur als Tracker, kein Handgelenk-HUD).
- ZR-010 (Toolkit: Regeltext vs. Runtime-Makros entkoppeln): als **Mirror ohne Runtime-Auslagerung** weitergeführt (Toolkit bleibt Laufzeitquelle).
- ZR-007 (Heilung/Medkit, LP≠HP): abgeschlossen (LP-Terminologie vereinheitlicht; Medikit auf 1W6 LP mit Missionslimit harmonisiert).
- ZR-008 („Alien"-Wortwahl/Cover-Lore): abgeschlossen (Default-Lore auf Fremdfraktions-/Gerüchtestatus harmonisiert).
- ZR-009 (Level-Up-Regel Attribut/Talent/SYS): abgeschlossen (SSOT auf 1 Wahl pro Stufe konsolidiert).

Verbindliche Nachverfolgung liegt ab jetzt in:

- `internal/qa/plans/2026-02-23-regelupdate-followup.md`
- `internal/qa/logs/2025-beta-qa-log.md`

Hinweis: ZR-010 läuft nach Kurskorrektur als wartbarer Mirror-Pfad weiter: Runtime-Makros bleiben vollständig im Toolkit; `internal/runtime/` dient nur der QA-/Review-Spiegelung.

Nachtrag zur offenen Audit-Frage „Team-TEMP im Gruppenspiel":
entschieden als `TEMP_gruppe = ceil(sum(temp aller aktiven Charaktere) / anzahl)`
(GRP = Gruppe). „Forward-only mode“ wurde nicht beauftragt und daher nicht als
Runtime-Standard übernommen.

Nachtrag ZR-006 (2026-02-23): Hardware-Physicality konsolidiert; Armbänder sind als
Tracker zulässig, projizieren aber kein HUD. Externe Projektoren bleiben
ausgeschlossen.

Nachtrag ZR-007 (2026-02-23): LP/HP-Schreibweise in den priorisierten Heil-
und Zustandsmodulen wurde auf **LP** vereinheitlicht und der Medikit-Standard
auf **1W6 LP** (max. 1× pro Charakter/Mission) nachgezogen; der priorisierte
Upload-Punkt gilt damit als abgeschlossen.

Nachtrag ZR-008 (2026-02-23): Alien-Begriffe in den priorisierten
Gameplay-Modulen wurden auf Cover-Lore/Fremdfraktions-Logik zurückgeführt,
damit der Hard-Sci-Fi-Defaultton ohne verpflichtenden Alien-Kanon erhalten
bleibt.

Nachtrag ZR-009 (2026-02-23): Die Level-Up-Regel wurde in den priorisierten
Progressionsmodulen auf einen eindeutigen SSOT gezogen: pro Stufe genau eine
Wahl (`+1 Attribut` oder `Talent/Upgrade` oder `+1 SYS`). Frühere
Doppel-Upgrade-Lesarten wurden im Standard entfernt.

Aktivierte Connectoren: **github**.

## Executive Summary

Dieses Repository enthält ein umfangreiches, stark modularisiertes Regel- und Content-Set für **ZEITRISS 4.2.6** (Markdown-Module plus interne QA-/Fixture-Dateien). In der aktuellen Fassung ist der Kernnutzen hoch (klarer Loop aus Core‑Ops → Paradoxon‑/Rift‑Loop, starke Generatoren, konsistente Noir‑/Physicality‑Leitplanken), aber die **Regel- und Standardkonsistenz ist an mehreren Stellen gebrochen** – teils durch echte Widersprüche, teils durch doppelte „Standards“, die voneinander abweichen, und teils durch Vermischung von **Player-/SL-Text** mit **Runtime-/Template-Inhalten**. (Basis der Analyse: Stand des Repos auf Commit **bb7391575be33415051046d2890d584eff1558d2**, insbesondere README.md, core/*, characters/*, gameplay/*, systems/*.)

Die größten, spielrelevanten Bruchstellen (P0/P1) sind:

- **Würfel-/Exploding-Standard** ist widersprüchlich (Burst‑Cap/„nur erster W6 explodiert“ vs. „Exploding pro Würfel“). Das ist ein mathematischer Kernanker des Systems und beeinflusst Balance, Boss‑Dämpfer, Advantage/Disadvantage und „Debug-/Audit“-Fixtures.
- **Paradoxon-Index (Px) ist semantisch nicht stabil**: mal reines Belohnungssystem ohne „Strafe“, mal mit Px‑Verlusten für Failure/Psi‑Burn/„Risk>Reward“. Zusätzlich kollidieren Aussagen zu **Scope (pro Charakter vs. kampagnenweit/gruppe)** und **Progression (fixe Erfolgszähler/TEMP vs. „Stil“/„Risiko“)**.
- **HQ‑Only Save & HQ‑Loop** (Debrief/Freeplay/Save) ist zwar mehrfach als Invariante formuliert, aber andere Module erlauben „direkt weiterspringen“ oder behandeln **Chronopolis/Tod** inkonsistent.
- **Lore-/Setting-Standards** („keine Aliens/kein Magie‑Standard“ vs. Alienvolk/First Contact/para‑Fantastik) sind nicht sauber als *Option* markiert, sondern stehen gleichrangig neben „Hard‑Agenten‑Thriller“-Axiomen.

Wenn ihr nur eine Sache sofort fixt: **SSOT‑Pass einziehen** (ein einziges, kurzes „Kerninvarianten“-Dokument + konsequente Verweise) und dann **Px + Exploding** auf exakt eine, copy‑paste‑fähige Regeldefinition normalisieren. Das wird in einem Codex‑„vibe-coding“-Sprint die höchste Rendite bringen, weil es Folgefehler in sehr vielen Modulen beseitigt.

---

## Repository-Überblick und Methodik

### Inhaltstypen und beobachtetes Zielbild

Im Repo liegen drei Ebenen, die momentan zu stark „ineinander bluten“:

1. **Spieltext/Regeltext** (Spielerhandbuch, Würfelmechanik, Zustände, Ausrüstung, Kampagnenstruktur, Generatoren).
2. **SL-/KI‑Leitfäden** (SL‑Referenz, Toolkit, cineastischer Einstieg).
3. **Runtime-/Template-/QA-Inhalte** (Makros, Fixtures, Transkripte, Normalizer‑Regeln).

Das Problem ist weniger „zu viel“, sondern: **fehlende Trennschärfe**. Dadurch entstehen doppelte Standards („im Regeltext steht A, im Toolkit steht B“) und unklare Zielgruppe („Spieler liest plötzlich Macro‑Guards“).

### Arbeitsweise / Evidenz

- Primäranalyse direkt aus Repo-Dateien via GitHub‑Connector (Commit **bb739…**).
- Web‑Validierung war für Repo‑Text **nicht möglich** (Zugriff via Webtool scheitert), daher sind Belege in diesem Report als **Dateipfade + Abschnittsbezug** formuliert (statt Web‑Zitate).  
- Wo ich „SSOT“ empfehle, beziehe ich mich auf die Module, die sich selbst bereits als „SSOT‑Anker“ positionieren (z. B. Save-/Loop‑Invarianten und Toolkit‑Kernregeln) – und markiere Konflikte als Fix‑Ziel.

### Empfohlene SSOT-Hierarchie (Entscheidungsvorschlag)

Damit Codex nicht „gegen die Wand“ refaktoriert, braucht ihr eine Prioritätsleiter. Vorschlag:

- **SSOT‑Kerninvarianten**: `systems/gameflow/speicher-fortsetzung.md` + ein neu einzuführendes Mini‑Dokument `core/ssot-kerninvarianten.md` (10–20 Zeilen).
- **Würfel & SG**: `core/wuerfelmechanik.md` (und *nur* dort die mathematische Definition).
- **Loop & Seeds**: `gameplay/kampagnenstruktur.md` als „Ablauf“, aber ohne alternative/experimentelle Abzweigungen im gleichen Tonfall.
- **HUD/UX**: `characters/hud-system.md` als Darstellungsstandard – aber ohne Regeldefinitionen zu würfeln/px, die abweichen.

---

## Konsistenz- und Balance-Audit

### Konflikt- und Doppelstandard-Matrix

Die folgende Tabelle fasst die wichtigsten Widersprüche zusammen und gibt eine konkrete Normalisierungsrichtung („SSOT“) vor. (Alle genannten Dateien existieren im Repo auf Commit **bb739…**.)

| Thema | Standard/Behauptung A | Standard/Behauptung B | Risiko im Spiel | Empfohlene Entscheidung (SSOT) | Primäre Patch-Orte |
|---|---|---|---|---|---|
| Exploding / Burst‑Cap | Exploding ist Teil des Kernwurfs; Burst‑Cap = „einmal“ (implizit, weil System meist 1 Würfel nutzt) in `core/wuerfelmechanik.md` | Abweichende Regeln: „Burst‑Cap 3“ (Cheat‑Sheet) **und** „Nur der erste W6 explodiert, weitere 6en nicht“ in `systems/toolkit-gpt-spielleiter.md` | Mathe kippt: Advantage/Disadvantage, Boss‑Dämpfer, Loot-/SG‑Kurven, QA‑Fixtures werden unzuverlässig | **Einheitlich**: *Jeder geworfene Würfel* kann **genau einmal** explodieren (Burst‑Cap = 1 **pro Würfel**). Keine Sonderregel „nur erster Würfel“. | `core/wuerfelmechanik.md` (Cheat‑Sheet), `systems/toolkit-gpt-spielleiter.md` (Roll‑Abschnitt) |
| Px als Belohnung vs. Strafe | Px als Resonanz‑Belohnung, seltene Abzüge nur bei extremen Fällen (mehrfach im „Front‑Facing“-Text) | Px‑1 bei Patz/Failure/„Risk > Reward“, Psi‑Burn etc. (Toolkit/Psi‑Regeltextstellen) | Spielgefühl bricht: Spieler interpretieren Px als „Strafleiste“ → vorsichtiges, unheroisches Play | **Einheitlich**: Px ist *Belohnungs-/Progressionsindex*, kein „Fail‑Punisher“. Failure = kein Fortschritt + Konsequenzen (CU/Stress/Heat), **kein Px‑1** im Default. | `systems/toolkit-gpt-spielleiter.md`, `systems/kp-kraefte-psi.md`, ggf. `gameplay/kampagnenstruktur.md` |
| Px‑Scope (pro Charakter vs. Gruppe/Kampagne) | „Zähler läuft pro Charakter“ (Solo‑Lesart) | „Gruppenspiel verwaltet gemeinsamen Index“ / kampagnenweit (mehrere Module) | Merge/Host‑Regeln werden unklar, Co‑op fühlt sich unfair an | **Einheitlich**: *Solo & npc‑team* = Px gehört dem Run/Save (praktisch „pro Charakterlauf“). *gruppe* = Px ist **gemeinsam**, Host‑Save ist führend. | `core/spieler-handbuch.md`, `characters/zustaende.md`, `systems/gameflow/speicher-fortsetzung.md` (klarstellen) |
| Px‑Progression (TEMP‑Zähler vs. Stil/Risiko) | TEMP‑abhängige Mission‑Zählung bis Px+1 (deterministisch, ETA berechenbar) | „Stilvoll/risikoreich“ lässt Px steigen/sinken; Mikropunkte, Risikoformeln | Unspielbar: SL muss „gefühlt“ Px steuern; ETA‑Anzeige wird Lüge | **Einheitlich**: Default = TEMP‑Zähler (success‑counter). *Stil‑Einfluss* nur als optionale „Resonanz‑Variante“ (klar als KANN, ohne Px‑1). | `core/wuerfelmechanik.md`, `characters/hud-system.md`, `gameplay/kampagnenstruktur.md` |
| HQ‑Only Save | Save nur im HQ (mehrere Systemtexte; SaveGuard/Flags) | Andere Module erlauben „direkt weiterspringen“ oder „HQ freiwillig“ | Save-Flow und Loop brechen; Tisch/Agent verliert Anker | **Einheitlich**: Mission endet immer in HQ (zur Not als Quick‑Cut). „Weiterspringen“ höchstens als optionaler Spezialmodus, nicht Default. | `core/zeitriss-core.md`, `characters/charaktererschaffung-grundlagen.md`, `gameplay/kampagnenstruktur.md` |
| Chronopolis & Tod | „Tod ist endgültig“ + Gruppen‑Todesentscheid (Kanon vs Reload) | „Tod = Aufwachen im HQ“ (Chronopolis‑Abschnitte in Kampagnenübersicht/Struktur) | Stakes werden beliebig; Chronopolis wird entweder zu hart oder zu risikolos | **Einheitlich**: Tod ist → **immer** Gruppen‑Todesentscheid (oder Solo: Spielerentscheid). Chronopolis ist **nicht** „Free Respawn“. | `gameplay/kampagnenuebersicht.md`, `gameplay/kampagnenstruktur.md`, `systems/toolkit-gpt-spielleiter.md` |
| Physicality Gate (Geräte) | Keine losgelösten Digitalräume; Linse/Comlink/Terminal; keine Armband‑HUDs | Widerspruch, ob Armbänder „verboten“ oder „okay“ sind | Stilbruch & Spielerfragen („darf ich Smartwatch?“) | **Einheitlich**: Armbänder **dürfen existieren** (Tracker/ID), aber **kein HUD/keine Projektion**; Default bleibt Linse/Comlink. | `core/zeitriss-core.md`, `core/sl-referenz.md`, `characters/hud-system.md`, `systems/toolkit-gpt-spielleiter.md` |
| „Keine Aliens“ vs. Alien‑Vokabular | Hard‑Agenten‑Thriller; para ist begrenzt | Generatoren/Arcs nennen Alienvolk/First Contact/Relikte | Tonalitätsbruch & Kanonkonflikt | **Einheitlich**: „Alien“ nur als *Cover‑Begriff*; im Kanon sind es **Transhumane/Zeitfraktionen/Bio‑Konstrukte**. Optionale „Exo‑Variante“ separat auslagern. | `gameplay/kreative-generatoren-missionen.md`, `gameplay/kampagnenuebersicht.md` |
| Heilung/Medkit‑Zahlen | Basis‑LP ~10 (implizit), Heilung klein und teuer | Medkit‑Heilung (z. B. 2W6) kollidiert mit LP‑Skala | Balance kippt: Verbrauchsgüter trivialisiert Schaden | **Einheitlich**: Heilung als kleiner, kalkulierbarer Wert (z. B. 1W6 oder fix 3) und klare Limits pro Mission. | `characters/ausruestung-cyberware.md`, `characters/zustaende.md`, Cheat‑Sheets |

### Solo vs. Gruppe: konkrete Problemstellen

- **Gruppenstart/Mid‑Session‑Merge**: Im Toolkit steht ein Pseudocode‑Reset (`state.campaign.px = 0`, Seeds leeren). Wenn so umgesetzt/gelebt wird, zerstört ein Spielerbeitritt den Kampagnenfortschritt. Das kollidiert mit „Host‑Regel“ (Host‑Save ist führend). → Muss raus oder als *nur für „neue Gruppe“* markiert werden.
- **Tempo-/Hazard‑Pay**: Bonifikationen für <3 Agent:innen sind ein gutes Solo‑Patch‑Werkzeug – aber es muss eindeutig sein, ob das **nur CU** betrifft oder auch SG/Encounter‑Dichte. Derzeit wirkt es, als könnten mehrere Systeme gleichzeitig „Solo‑Buffs“ geben.

### Text, der entfernt/verschoben werden sollte

Hochwahrscheinliche Kandidaten, weil sie als „Regeltext“ im Frontbereich auftauchen, aber eigentlich **Runtime‑Interna** oder **QA‑Artefakte** sind:

- Makro‑Blöcke, Template‑Syntax (⟨% … %⟩ / ⟪ … ⟫), Normalizer‑Regeln, „Acceptance‑Smoke‑Checkliste“ und „Fixture“-Verweise im **gleichen Dokument** wie Spielleitungsstil. Das gehört in `internal/` oder in klar getrennte Dateien (z. B. `internal/runtime/*.jinja`, `docs/qa/*`).

---

## Priorisierte Codex-Issues

### Issue-Index (für Copy‑Paste in GitHub Issues)

Legende Severity: **P0 Blocker**, **P1 Hoch**, **P2 Mittel**, **P3 Niedrig**.  
Effort: **S** (≤1h), **M** (½–1 Tag), **L** (1–3 Tage), **XL** (>3 Tage).

| ID | Issue-Titel | Severity | Effort | Primärdateien (Vorschlag) | Kurz-Ziel |
|---|---|---:|---:|---|---|
| ZR-001 | Exploding/Burst‑Cap normalisieren (1 Regel, überall) | P0 | M | `core/wuerfelmechanik.md`, `systems/toolkit-gpt-spielleiter.md` | Mathe-SSOT wiederherstellen |
| ZR-002 | Px-Philosophie fixen: Belohnungssystem ohne Default‑Px‑1 | P0 | M | `systems/toolkit-gpt-spielleiter.md`, `systems/kp-kraefte-psi.md`, `core/spieler-handbuch.md` | „Px ≠ Strafe“ konsequent |
| ZR-003 | Px‑Scope klarziehen (solo/npc-team vs gruppe) | P0 | S | `core/spieler-handbuch.md`, `characters/zustaende.md`, `systems/gameflow/speicher-fortsetzung.md` | Streitfragen eliminieren |
| ZR-004 | HQ‑Loop-Invariante durchziehen: kein „Skip HQ“ im Default | P1 | M | `core/zeitriss-core.md`, `characters/charaktererschaffung-grundlagen.md`, `gameplay/kampagnenstruktur.md` | Save-/Flow‑Konsistenz |
| ZR-005 | Chronopolis/Tod vereinheitlichen (kein Free‑Respawn) | P1 | M | `gameplay/kampagnenuebersicht.md`, `gameplay/kampagnenstruktur.md`, Toolkit‑Abschnitte | Stakes konsistent |
| ZR-006 | Physicality Gate: Armbänder-Regel eindeutig (Tracker ja, HUD nein) | P1 | S | `core/zeitriss-core.md`, `core/sl-referenz.md`, `characters/hud-system.md` | Stilfragen schließen |
| ZR-007 | Heilung/Medkit balansieren & terminologisch vereinheitlichen (LP≠HP) | P1 | M | `characters/ausruestung-cyberware.md`, `characters/zustaende.md` | Verbrauchsgüter stabil |
| ZR-008 | „Alien“-Wortwahl als Cover deklarieren oder Lore‑Variante auslagern | P2 | M | `gameplay/kreative-generatoren-missionen.md`, `gameplay/kampagnenuebersicht.md` | Tonalitätsbruch vermeiden |
| ZR-009 | Level‑Up‑Regel konsolidieren (Attribut vs Talent vs SYS) | P2 | M | `core/zeitriss-core.md`, `characters/charaktererschaffung-grundlagen.md`, SL‑Referenz | Build‑Balance |
| ZR-010 | Toolkit entkoppeln: „Regeltext“ vs „Runtime‑Makros“ in getrennte Dateien | P1 | L | `systems/toolkit-gpt-spielleiter.md` + neue `internal/runtime/*` | Wartbarkeit + Qualität |
| ZR-011 | HUD-Modul entschlacken: nur UX-Standard, keine abweichenden Kernregeln | P2 | M | `characters/hud-system.md` | „Anzeige“ ≠ Regel |
| ZR-012 | Kampagnenstruktur: seed-status normalisieren (open/closed) | P2 | S | `gameplay/kampagnenstruktur.md`, ggf. Save‑Modul | Merge/Normalizer |
| ZR-013 | Glossar/Terminologie-Guide (SG, LP, SYS, PP, TEMP) als 1 Seite | P2 | M | neues `core/glossar-ssot.md` + Links | reduziert Drift |
| ZR-014 | Generatoren: Sensitivitäts-Schalter (harte Realereignisse) dokumentieren | P3 | S | `gameplay/kreative-generatoren-missionen.md` | Gruppenkomfort |
| ZR-015 | Interne QA-„Known Issues“ in GitHub Issues spiegeln (triage) | P3 | M | `internal/qa/process/known-issues.md` | Backlog sauber |

### Ausformulierte Issues (Codex-ready)

#### ZR-001 — Exploding/Burst‑Cap normalisieren (1 Regel, überall)
**Problem:** Es existieren widersprüchliche Exploding-Regeln: (a) implizit „Exploding als Kernregel“, (b) Cheat‑Sheet/Meta erwähnt Burst‑Cap ≠ 1, (c) Toolkit behauptet „nur der erste W6 explodiert“. Das führt zu inkonsistenten Erfolgswahrscheinlichkeiten und macht spätere Balance‑Aussagen (Boss‑Dämpfer, SG‑Kurven) unzuverlässig.

**Reproduktion:**
1. Öffne `core/wuerfelmechanik.md`, suche nach „Burst‑Cap“ / Exploding‑Cheat‑Sheet.
2. Öffne `systems/toolkit-gpt-spielleiter.md`, suche nach dem Roll-/Exploding‑Abschnitt („Nur der erste W6…“ o. ä.).
3. Vergleiche: Definition, Cap, Anwendung bei Advantage (2 Würfel) oder Mehrwürfen.

**Vorschlag (Lösung):**
- Definiere in *einem* Absatz (SSOT) die Exploding‑Regel:
  - *Jeder geworfene Würfel* kann **genau einmal** explodieren (Burst‑Cap = 1 pro Würfel).
  - Exploding passiert **vor** dem Vergleich (z. B. bei Vorteil/Nachteil).
- Entferne/ersetze abweichende Aussagen im Toolkit.

**Dateien / Orte:**
- `core/wuerfelmechanik.md` → Abschnitt Exploding + Cheat‑Sheet.
- `systems/toolkit-gpt-spielleiter.md` → Würfelbefehl/Audit‑Trail Abschnitt.

**Severity:** P0  
**Effort:** M  
**Suggested Commit Message:** `fix(rules): vereinheitliche exploding-wuerfel (burst-cap=1) in core + toolkit`

---

#### ZR-002 — Px-Philosophie fixen: Belohnungssystem ohne Default‑Px‑1
**Problem:** Mehrere Module nutzen Px‑Verlust als Standardkonsequenz (Failure/Psi‑Burn/Risk‑Resolution), während andere Module Px ausdrücklich als Belohnungssystem rahmen. Dadurch wird das System psychologisch zu einer „Fehlerstrafe“ – das kippt Spielerentscheidungen.

**Reproduktion:**
1. Öffne `systems/toolkit-gpt-spielleiter.md`, suche nach „Px-1“ / „Resonanzverlust“ / „Patzer“.
2. Öffne `systems/kp-kraefte-psi.md`, suche nach „Px“ in Zusammenhang mit Kosten/Overload/Burn.
3. Öffne `core/spieler-handbuch.md` und vergleiche die dortige Semantik.

**Vorschlag (Lösung):**
- Default: **Px steigt nur** durch stabilisierte Missionen (via TEMP‑Zähler).  
- Failure: **kein Zuwachs**, stattdessen Konsequenzen über CU/Stress/Heat/Story.  
- Px‑1 bleibt als **KANN‑Option** für „Hardcore Resonanz“ oder „extreme, absichtlich paradoxe Intervention“ mit explizitem SL‑Call.

**Dateien / Orte:** Toolkit + Psi‑Modul + Spielerhandbuch (Kurzabschnitt „Px ist keine Strafe“).  
**Severity:** P0  
**Effort:** M  
**Suggested Commit Message:** `refactor(px): entferne default px-penalties, ersetze durch stress/cu-konsequenzen`

---

#### ZR-003 — Px‑Scope klarziehen (solo/npc-team vs gruppe)
**Problem:** Spielertexte widersprechen sich, ob Px pro Charakter oder kampagnenweit geführt wird. In Co‑op ist das entscheidend für Fairness und Merge‑Regeln.

**Reproduktion:** Lies Px‑Abschnitte in `core/spieler-handbuch.md` und `characters/zustaende.md` und prüfe Gruppenspiel‑Passagen im Save‑Modul.

**Vorschlag (Lösung, präzise Formulierung):**
- **solo & npc-team:** Px gehört zum Run/Save (praktisch „dein Agentenlauf“).
- **gruppe:** Px gehört der gemeinsamen Kampagne (Host‑Save führend).

**Severity:** P0  
**Effort:** S  
**Commit Message:** `docs(px): präzisiere px-scope für solo vs gruppe`

---

#### ZR-004 — HQ‑Loop-Invariante durchziehen: kein „Skip HQ“ im Default
**Problem:** Einige Texte erlauben „direkt weiterspringen“ oder deklarieren HQ‑Rückkehr als freiwillig. Das kollidiert mit HQ‑Only Save und mit dem Debrief‑/Freeplay‑Loop.

**Fix:** Formuliert „HQ‑Rückkehr ist immer Teil des Endes einer Mission; sie kann nur *erzählerisch* abgekürzt werden“. Optionaler Modus „Forward‑Only Arc“ kann später kommen, aber muss als Erweiterung markiert werden.

**Severity:** P1  
**Effort:** M  
**Commit Message:** `docs(loop): hq-rueckkehr als pflicht (quick-cut erlaubt), entferne skip-hq wording`

---

#### ZR-005 — Chronopolis/Tod vereinheitlichen (kein Free‑Respawn)
**Problem:** Chronopolis‑Abschnitte schwanken zwischen „Tod final“ und „Tod → Aufwachen im HQ“. Das zerstört Stakes.

**Fix:** Ein einziger Standard:
- Tod triggert **Gruppen‑Todesentscheid** (Kanon vs Reload).
- Chronopolis zählt **nicht** als HQ; keine Saves, keine „kostenlose Wiederauferstehung“.

**Severity:** P1  
**Effort:** M  
**Commit Message:** `fix(chronopolis): stakes vereinheitlichen, remove free-respawn claims`

---

#### ZR-010 — Toolkit entkoppeln: „Regeltext“ vs „Runtime‑Makros“
**Problem:** `systems/toolkit-gpt-spielleiter.md` enthält zugleich Regel-/Stiltext und massiven Runtime‑Code/Template‑Fragmente. Das erzeugt Drift und erhöht das Risiko, dass „Makros im Chat erscheinen“ – was der Text selbst verbietet.

**Fix-Vorschlag:**
- Mirror-first statt Auslagerung:
  - `systems/toolkit-gpt-spielleiter.md` bleibt **Human-Readable + vollständige Runtime-Quelle** für die GPT-Spielleitung.
  - `internal/runtime/` führt Makros nur als Spiegel für QA/Review-Diffs.
  - Toolkit darf den Runtime-Block nicht auf externe Dateien verweisen oder davon abhängig machen.

**Severity:** P1  
**Effort:** L  
**Commit Message:** `fix(toolkit): keep runtime macros in toolkit, use internal mirror for QA only`

---

## Patch-Vorschläge und Ersatztexte

Die folgenden Texte sind so geschrieben, dass ihr sie 1:1 in die Module kopieren könnt. Wo möglich gebe ich diff‑artige Patches; wegen fehlender Web‑Line‑Anchors referenziere ich Abschnitte nach Überschrift.

### Patch für ZR-001: Exploding/Burst‑Cap (SSOT-Text)

**Ziel:** Der Spieler soll *eine* Regel lesen – ohne Sonderfälle und ohne widersprüchliche Caps.

**Datei:** `core/wuerfelmechanik.md`  
**Ort:** Abschnitt „Explodierende Würfel / Burst‑Cap“ + Cheat‑Sheet

```diff
--- a/core/wuerfelmechanik.md
+++ b/core/wuerfelmechanik.md
@@ Abschnitt: Explodierende Würfel (Exploding) / Burst-Cap
- (mehrdeutige oder widersprüchliche Formulierungen zu Burst-Cap)
+ ### Exploding (Burst) – SSOT
+ Wenn du würfelst, gilt:
+ **Jeder geworfene Würfel kann genau einmal explodieren.**
+ Zeigt ein Würfel sein Maximum (W6=6 oder W10=10), würfelst du **denselben Würfel einmal nach**
+ und addierst das Ergebnis. Danach ist Schluss – kein Kettenfeuer, kein mehrfaches Explodieren.
+
+ **Wichtig bei Vorteil/Nachteil:** Wenn du mehrere Würfel wirfst (z. B. Vorteil),
+ wird **jeder** dieser Würfel einzeln nach dieser Regel abgehandelt (inkl. möglichem Exploding),
+ **bevor** du den besten/schlechtesten Gesamtwurf wählst.
+
+ Kurzform: Exploding = „+1 Nachwurf bei Maximum“, Burst‑Cap = 1 pro geworfenem Würfel.
```

**Begleitfix im Toolkit** (`systems/toolkit-gpt-spielleiter.md`), Würfelbefehl‑Abschnitt:

```diff
--- a/systems/toolkit-gpt-spielleiter.md
+++ b/systems/toolkit-gpt-spielleiter.md
@@ Abschnitt: Würfelbefehl mit Audit-Trail
- Nur der **erste** W6 einer Probe darf erneut geworfen werden. Weitere 6er zählen ohne Explosion.
+ Exploding-SSOT: **Jeder geworfene Würfel** darf bei Maximum **genau einmal** nachwürfeln.
+ (Burst‑Cap = 1 pro Würfel; gilt auch bei Vorteil/Nachteil.)
```

**Suggested Commit Message:** `fix(rules): exploding-ssot + burst-cap=1, remove first-die-only rule`

---

### Patch für ZR-002/ZR-003: Px (Semantik + Scope) — Ersatztextblock

**Ziel:** Px ist eindeutig *Resonanzfortschritt*, nicht Strafe; Scope ist klar.

**Datei:** `core/spieler-handbuch.md`  
**Ort:** Abschnitt „Paradoxon‑Index (Px)“ (und ggf. Kurz‑Cheat‑Sheet)

**Ersatztext (copy‑paste):**

> ### Paradoxon‑Index (Px) – Resonanz, kein Strafkonto  
> Der **Paradoxon‑Index (Px)** misst, wie stark sich ein Chrononautenlauf „in die Zeit eingräbt“ – eine **Resonanz**, die das ITI auswertet.  
> **Wichtig:** Px ist **keine Strafe**. Wenn ein Einsatz scheitert, verliert ihr normalerweise **keinen** Px – ihr bekommt stattdessen echte Konsequenzen (weniger CU, mehr Stress, ein offenes Problem im Arc).  
>
> **Scope:**  
> - **Solo** und **npc‑team:** Px gehört **deinem Lauf** (deinem Save).  
> - **Gruppe:** Px gehört **eurer gemeinsamen Kampagne** (Host‑Save ist führend).  
>
> **Wie steigt Px?**  
> Nach einem **stabilisierten** Einsatz sammelt ihr Fortschritt Richtung Px+1. Wie schnell das geht, hängt an der **TEMP‑Resonanz** des Teams (Kodex zeigt eine ETA an).  
>
> **Px 5 – ClusterCreate():**  
> Erreicht ihr **Px 5**, erzeugt das ITI neue **Rift‑Seeds** (typisch 1–2). Diese Seeds werden auf der Raumzeitkarte vermerkt, sind aber erst **nach Episodenabschluss** als eigene Rift‑Ops spielbar. Danach wird der Px im Debrief sauber auf **0** zurückgesetzt.

**Zusatzfix:** Entfernt oder markiert als „Option“ jede Default‑Stelle, an der „Px‑1“ bei Patzer/Failure steht (Toolkit/Psi/Stress‑Varianten).

---

### Patch für ZR-004: HQ‑Rückkehr & „Skip HQ“ entgiften

**Ziel:** Eine klare Invariante, aber ohne Spieler zu „zwingen“: Quick‑Cut ist erlaubt, Loop bleibt.

**Dateien:**  
- `core/zeitriss-core.md` (Passagen zu „Direkt weiterspringen“)  
- `characters/charaktererschaffung-grundlagen.md` (HQ „freiwillig“)  
- `gameplay/kampagnenstruktur.md` (Loop‑Beschreibung)

**Ersatztext (kurz, universell einsetzbar):**

> **HQ‑Rückkehr ist Teil jeder Mission.**  
> Am Ende eines Einsatzes kehrt ihr immer in die Nullzeit zurück – notfalls als harter Schnitt, wenn niemand Freeplay ausspielen möchte.  
> **Warum?** Weil Debrief, Auszahlungen, Upgrades, Stress‑Reset und das **HQ‑Only Save** dort verankert sind.  
> Wer „schnell weitermachen“ will, nutzt *Auto‑HQ*: Debrief‑Screen → 1–2 Sätze Freeplay → Save → nächstes Briefing.

---

### Patch für ZR-005: Chronopolis/Tod – ein Satz, der alles klärt

**Datei:** überall, wo Chronopolis erklärt wird (`gameplay/kampagnenuebersicht.md`, `gameplay/kampagnenstruktur.md`, Toolkit‑Chronopolis‑Abschnitte)

**Ersatztext (copy‑paste):**

> **Chronopolis zählt nicht als HQ.**  
> In Chronopolis gibt es **keine Saves**. Wenn jemand dort stirbt, gilt derselbe **Todesentscheid** wie überall:  
> **(1) Tod bleibt Kanon** oder **(2) neu laden** (letzten HQ‑DeepSave) – einmal entschieden, wird weitergespielt.  
> Chronopolis ist Belohnung und Risiko zugleich. Kein kostenloses „Aufwachen im HQ“.

---

### Patch für ZR-006: Physicality Gate & Armbänder (Tracker ja, HUD nein)

**Ersatztext (in `characters/hud-system.md` oder Core‑Spec):**

> **Armbänder & Wearables:**  
> Armbänder, Marken oder Tracker **dürfen** existieren (ID, Zugangsmarke, Sensor‑Tag).  
> Das **HUD selbst** läuft jedoch **nicht** über das Handgelenk: Die Anzeige kommt aus der **AR‑Kontaktlinse**, Kommunikation über **Comlink/Ohrstöpsel** oder Terminal/Hardline.  
> Keine Handgelenk‑Projektionen, keine „Smartwatch‑HUDs“.

---

## Roadmap, Milestones und Commit-Nachrichten

### Priorisierte To‑Do‑Checkliste

**Sofort (Stabilisierung, 1 Sprint)**  
- Exploding/Burst‑Cap als **SSOT** vereinheitlichen (ZR‑001).  
- Px‑Semantik („Belohnung, nicht Strafe“) und Px‑Scope (solo vs gruppe) konsolidieren (ZR‑002 + ZR‑003).  
- HQ‑Loop‑Invariante überall sprachlich konsistent machen (ZR‑004).  

**Kurzfristig (Qualität & Balance, 2. Sprint)**  
- Chronopolis/Tod konsistent (ZR‑005).  
- Healing/Medkit‑Werte + LP/HP‑Begriffe normalisieren (ZR‑007).  
- Physicality‑Gate‑Wearables klarziehen (ZR‑006).  

**Mittelfristig (Wartbarkeit, 3.–4. Sprint)**  
- Toolkit splitten: human‑readable vs runtime‑makros (ZR‑010).  
- HUD‑Modul entkoppeln: Anzeigenstandard statt Regeldopplung (ZR‑011).  
- Glossar‑SSOT einführen und überall verlinken (ZR‑013).  

**Optional (Tonalität/Content-Comfort)**  
- „Alien“ nur als Cover oder als optionale Lore‑Variante auslagern (ZR‑008).  
- Generator‑Sensitivitäts‑Toggle dokumentieren (ZR‑014).  

### Milestone-Plan (GitHub Milestones)

#### Milestone „SSOT‑Stabilisierung“
Scope: ZR‑001, ZR‑002, ZR‑003, ZR‑004  
**Definition of Done:**  
- Es gibt **genau eine** Exploding‑Definition.  
- Px hat **eine** Definition (Semantik + Scope + Px‑5‑Flow).  
- Kein Modul behauptet Default‑„Skip HQ“ im Widerspruch zum Save‑System.

**Suggested commits (Reihenfolge):**
1. `fix(rules): exploding-ssot + burst-cap=1 across docs`
2. `docs(px): clarify px as reward + scope for solo vs gruppe`
3. `docs(loop): enforce hq-return invariant (auto-hq quick-cut wording)`

#### Milestone „Stakes & Balance“
Scope: ZR‑005, ZR‑006, ZR‑007, ZR‑009  
**Definition of Done:**  
- Chronopolis-Tod ist überall gleich geregelt.  
- Wearables-Regel beantwortet die Smartwatch‑Frage endgültig.  
- Heilung passt zu LP‑Skala und ist konsistent begrenzt.  
- Level‑Up‑Optionen sind in allen Modulen gleich.

**Suggested commits:**
- `fix(stakes): unify chronopolis death rules (no free respawn)`
- `balance(healing): standardize medkit values + LP terminology`
- `docs(physicality): wearable tracker allowed, wrist-hud forbidden`
- `docs(progress): consolidate level-up choice (attr vs talent vs sys)`

#### Milestone „Struktur & Wartbarkeit“
Scope: ZR‑010, ZR‑011, ZR‑012, ZR‑013  
**Definition of Done:**  
- Toolkit ist sauber getrennt; keine Makro‑Syntax in Player/SL‑Text.  
- HUD‑Modul enthält keine abweichenden Kernregeln.  
- Seed‑Status ist normalisiert (open/closed) und überall gleich.  
- Glossar‑SSOT existiert und wird verlinkt.

**Suggested commits:**
- `refactor(toolkit): split runtime macros into internal/runtime`
- `refactor(hud): remove rule duplication, link to ssot sections`
- `docs(glossar): add ssot glossary + link from modules`
- `docs(seeds): normalize seed status to open/closed`

---

### Hinweis zu „fehlenden Details“
Einige Implementationsdetails sind im Repo implizit, aber nicht als *ein einziger* Zielstandard formuliert (z. B. „Wie genau wird Team‑TEMP im Gruppenspiel berechnet?“ oder „Gibt es einen offiziellen Forward‑Only‑Modus?“). In diesem Audit behandle ich diese Punkte als **derzeit nicht eindeutig spezifiziert** und empfehle, sie im SSOT‑Dokument als klare Entscheidung festzunageln, bevor Codex größere Refactors automatisiert.

---

### Mermaid: empfohlener, konsistenter Loop (Core → Px → Rift)

```mermaid
flowchart TD
  A[Start: Spiel starten (solo/npc-team/gruppe)] --> B[HQ: Briefing]
  B --> C[Core-Mission (12 Szenen)]
  C --> D[Debrief im HQ: CU/XP/Stress-Reset]
  D --> E{Mission stabilisiert?}
  E -- nein --> F[Konsequenzen: weniger CU / mehr Stress / Arc-Folge]
  E -- ja --> G[missions_since_px +1 (TEMP-abhängig)]
  G --> H{Px +1 erreicht?}
  H -- nein --> I[Auto-HQ oder Freeplay]
  H -- ja --> J[Px steigt um 1]
  J --> K{Px == 5?}
  K -- nein --> I
  K -- ja --> L[ClusterCreate(): 1-2 Rift-Seeds erzeugen]
  L --> M[Seeds bis Episodenende gesperrt]
  M --> N{Episode beendet? (nach 10 Core-Missionen)}
  N -- nein --> I
  N -- ja --> O[Option: Rift-Op (14 Szenen) aus HQ starten]
  O --> P[Boss Szene 10 + ggf. Artefaktwurf]
  P --> D
```

--- 

Wenn ihr den Report direkt in GitHub umsetzen wollt: Erstellt **Milestone „SSOT‑Stabilisierung“** und legt die Issues **ZR‑001 bis ZR‑004** an – exakt so wie oben – und lasst Codex dann file‑by‑file die Ersatztexte patchen (Start: Würfelmechanik, dann Toolkit, dann Spielerhandbuch, dann Kampagnenstruktur).
