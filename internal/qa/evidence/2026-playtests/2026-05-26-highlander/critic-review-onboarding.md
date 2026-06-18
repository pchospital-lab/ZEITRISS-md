# Critic-Review: feat/onboarding-tonfall

**Modell:** Sonnet 4.7
**Gelaufen:** 2026-05-27T20:55+02:00
**Hash:** 8481e749ec293f949e3a292d5b115908943db71c (main HEAD; Branch hat working-tree-Änderungen, **noch nicht committet**)
**Patch-Stat:** 3 files, +44/-3

## Verdict

**GO mit Mini-Fix.** Inhaltlich konsistent, Anti-Pattern aus realem Playtest belegt,
Pacing-Contract-Integration sauber als Sub-Bullet. Ein klarer **Grammatikfehler** in
`cinematic-start.md` muss vor Commit raus, plus ein **fehlender Querverweis** im
Mission-Generator. Keine echten Widerspruchs-Restbestände im Repo gefunden.

## Smoke

✓ Patch im Working Tree vorhanden (`git status` zeigt 3 modifizierte Files).
✗ **Branch noch nicht committet** — `git diff main..feat/onboarding-tonfall` ist leer,
  weil die Änderungen unstaged sind. Vor `~/bin/ghrepo push` muss `commit-msg-prepare.sh --commit` laufen.

## Befunde

### 1. Weitere Widerspruchs-Stellen?

Keine **echten** Konflikte gefunden. Geprüft:

- `core/spieler-handbuch.md` — Mission-1-Erwähnungen (Z.157, 170, 336, 706, 709, 731,
  1003) betreffen alle Save-Gate-Mechanik („Save-Angebot kommt nach Mission 1"), keine
  Stakes-Sprache. Z.916 nennt „Untergang" aber als **generische Metapher**
  („Sekunden über Erfolg oder Untergang") in einem Action-Klappentext, nicht als
  MS1-Briefing-Vokabular. **Kein Eingriff nötig**, aber ggf. später hübschen.
- `core/zeitriss-core.md` — Lore-Setup, keine MS1-Briefing-Texte. Wort „Zeitlinie"
  taucht 20+ mal auf, immer als World-Building-Vokabel, nie als MS1-Stakes.
- `gameplay/kampagnenstruktur.md` — Andere MS1-Erwähnungen (Mini-Boss MS5,
  Episoden-Boss MS10) sind Boss-Rhythmus, nicht Stakes-Sprache.
- `systems/toolkit-gpt-spielleiter.md` — Z.1027/1032 sind nur Trigger-Wörter
  („Briefing", „erste Mission") für Phase-Übergang, nicht Stakes-Vorlagen.
- `gameplay/kreative-generatoren-missionen.md` — siehe Befund 3.

### 2. Pacing-Contract-Konsistenz

Konsistent, **keine Lücke MS3–5**.

- Pflichtgate sagt: „Mega-Stakes erst ab Mission 6+ erlaubt (Klimax-Phase)".
- Pacing-Contract sagt: MS3–5 = „Entwicklung. Fäden verdichten sich, Stakes steigen
  **spürbar**. Mini-Boss bei Mission 5."
- MS6–9 = „Klimax. Crew steht im Zentrum der Bedrohung. **Jetzt darf es um alles
  gehen**."

→ Treppe ist sauber: MS1–2 klein/konkret, MS3–5 spürbar steigend (nicht Mega), MS6+
  Mega/Welt-Stakes erlaubt. **Kein Fix nötig.**

### 3. Generator-Konflikt

`gameplay/kreative-generatoren-missionen.md` hat bereits Z.177–184 eine **Briefing-
Eskalation**-Regel (Netflix-Effekt, MS1–2 kleiner Ausschnitt, MS6+ Zentrum der
Bedrohung). Inhaltlich deckungsgleich mit dem neuen Pflichtgate, aber:

- **Kein Querverweis** auf das neue MS1-2-Tonfall-Pflichtgate.
- Die **Mission-Templates T-0001..T-0010** (Z.604+) enthalten Antagonist-Goals wie
  *„Titanic-Untergang verhindern, Kurs ändern lassen und Zeitlinie destabilisieren"*
  (T-0003). Das sind **SL-interne Mission-Mechaniken** (Antagonist-Goal, nicht
  Briefing-Text). Risiko: Eine KI-SL ohne Pflichtgate-Verständnis könnte den
  Antagonist-Goal-Text 1:1 als Briefing-Stakes spiegeln. Das Pflichtgate
  fängt es jetzt ab, aber ein **expliziter Annotation-Hinweis** beim Generator
  würde die Hürde senken.

**Empfehlung:** Mini-Fix in `kreative-generatoren-missionen.md` Z.177–184:
Querverweis ergänzen (siehe Empfehlung unten).

### 4. Cross-Verweise

- ✓ „Masterprompt §C MS1-2-Tonfall-Pflichtgate" — existiert
  (`meta/masterprompt_v6.md` Z.114).
- ✓ „Masterprompt §C Pacing-Contract" — existiert (Z.106).
- ✓ Verweis aus `cinematic-start.md` → Masterprompt §C — formatiert wie andere
  Pflichtgate-Verweise (Boss, Kampf, Exfil) im Repo. Sauber.
- ✓ Verweis aus `kampagnenstruktur.md` → Masterprompt §C — sauber.
- ⚠ **Grammatikfehler** in `cinematic-start.md` Z.50–51:
  *„Der erste Auftrag ist mehr als ein Tutorial — aber **deutlich weniger** als
  **der** Konfrontation mit der Verschwörung."*
  → falscher Kasus. Korrekt: *„als **die** Konfrontation"* (Vergleich, Nominativ/
  Akkusativ-Parallele zu „ein Tutorial"). **Muss vor Commit raus.**

## Empfehlung

**Mini-Fixes vor Commit:**

1. **Grammatikfix** in `systems/gameflow/cinematic-start.md` Z.50–51:

   ```diff
   - Der erste Auftrag ist mehr als ein Tutorial — aber **deutlich weniger** als der
   - Konfrontation mit der Verschwörung.
   + Der erste Auftrag ist mehr als ein Tutorial — aber **deutlich weniger** als die
   + Konfrontation mit der Verschwörung.
   ```

2. **Querverweis** in `gameplay/kreative-generatoren-missionen.md` Z.177–184
   (Briefing-Eskalation):

   ```diff
   - **Briefing-Eskalation:** Der Briefing-Scope folgt der Arc-Phase der Episode.
     Mission 1–2 zeigt einen **kleinen Ausschnitt** des historischen Szenarios als
     konkretes Ziel (einen Zeugen befragen, eine Lieferung verfolgen, einen Zugang
     dokumentieren). Erst ab Mission 6+ rückt die Crew ins Zentrum der großen
     Bedrohung. So entsteht der Netflix-Effekt: Der Spieler **entdeckt** die
     Verschwörung Schicht für Schicht, statt sie im ersten Briefing erklärt zu
   - bekommen.
   + bekommen. Vollständige Sprach-/Tonfall-Pflichten und Anti-Patterns:
   + Masterprompt §C MS1-2-Tonfall-Pflichtgate. Wichtig: Antagonist-Goals im
   + Mission-Template-Catalogue (T-0001+) sind **SL-interne Mechanik**, nicht
   + Briefing-Text — Briefing-Stakes bleiben auch dann klein, wenn das
   + Template-Endspiel groß ist.
   ```

3. **Commit ausführen** mit `~/.openclaw/workspace-cloud/scripts/commit-msg-prepare.sh --commit`
   (Working Tree ist noch unstaged, der Branch hat aktuell keine Commits gegenüber main).

**Optional (nice-to-have, nicht blockend):**

- `core/spieler-handbuch.md` Z.916 („Sekunden über Erfolg oder Untergang") später
  entschärfen — kein MS1-Briefing-Kontext, aber Eschatologie-Vokabular schwingt mit.
