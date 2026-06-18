# Critic-Review: feat/exfil-stress

**Modell:** Opus 4.7 (thinking high) | **Gelaufen:** 2026-05-27T19:52+02:00 | **Hash:** b1c826793e4bdcfd0e985c7879824db1b2164206 (main; Patch uncommitted auf `feat/exfil-stress`)
**Files:** `meta/masterprompt_v6.md` (+9 Zeilen, §C Bullet), `gameplay/kampagnenstruktur.md` (+70 Zeilen, neuer Unterabschnitt mit `{#exfil-stress-pflichtgate}`), `core/sl-referenz.md` (+14 Zeilen)

## Verdict

**GO mit Mini-Fix.** Die Mechanik sitzt sauber in §C der Mission-Pflichtgates, der Anchor `{#exfil-stress-pflichtgate}` ist definiert, Cross-Verweise auf Masterprompt §C IA/RW-Spot-Pflichtgate und Mission-Integrität-Pflichtgate existieren. Drei klar adressierbare Mini-Fixes vor Merge nötig (Px-Framing-Schärfe, Sweep/Warteszene-Abgrenzung, Multiplayer-Klarstellung). Px-Belohnungs-Invariante (§D Z.209–211) wird **gewahrt**, weil der Patch explizit „Belohnungssystem, keine Strafe“ markiert.

## Smoke

✓ Patch parsed sauber (3 Files, diff zählt +90/-0)
✓ Anchor `{#exfil-stress-pflichtgate}` syntaktisch korrekt definiert (`kampagnenstruktur.md` Z.748)
✓ Cross-Link aus `sl-referenz.md` (`../gameplay/kampagnenstruktur.md#exfil-stress-pflichtgate`) auflösbar
✓ Bullet in §C steht nach IA/RW-Spot-Pflichtgate, vor Briefing-Output-Pflichtgate — Reihenfolge stimmig
✓ Typo: `kampagnenstruktur.md` Z.770 *„nicht belieg weit weg“* → soll `beliebig` heißen. **Fix vor Commit.**

## Befunde

### 1. Px-Belohnungssystem-Konsistenz — **GRENZWERTIG, aber haltbar**

`masterprompt_v6.md` Z.209–211 ist eindeutig: *„Nie negativ framen. Keine Warnungen wie 'droht Rift' oder 'Vorsicht, Px steigt' — Px-Anstieg ist immer positiv für den Spieler.“*

Der Patch (`kampagnenstruktur.md` Z.795–798) markiert Drift-Beat klar als Belohnung („Px +1 (Belohnungssystem, kein Punktabzug — siehe §D Paradoxon & TEMP)“), und das Kodex-Beispiel Z.800 sagt sachlich *„Causality-Drift detektiert. Px +1.“* — keine Warnung, keine negative Tonalität. **Aber:** Die Drift-Beat-Beschreibungen Z.793–795 („Zeuge sieht etwas Ungewohntes“, „Comlink-Echo bleibt hängen“) und die Tröstung Z.802 *„nicht als technisches Failure, sondern als ‚verdammt, jetzt hat der Zeuge die Glock gesehen'-Beat“* lesen sich für die SL **wie ein Fehler-Frame**. Risiko: SL übersetzt das in Spielerausgabe als „Mist, ihr habt’s vermasselt — Px steigt zur Strafe.“ Genau das verbietet §D.

**Zusätzlich problematisch:** Heat +1 in derselben Stelle ist mechanisch echte Strafe (höhere Patrouille-Dichte etc.). Wenn Drift-Beat eine reine Belohnung sein soll, warum **gleichzeitig** Heat +1 als Konsequenz? Das ist innerhalb des Bullets selbst widersprüchlich.

**Fix:** Patch schärfen — explizite Anweisung an SL, **wie** der Drift-Beat dem Spieler präsentiert wird: nicht als „ihr habt was kaputtgemacht“, sondern als „ihr habt unbewusst eine Spur in die Geschichte gedrückt — Px steigt, Rift-Loot näher.“ Heat +1 separat begründen oder optional machen (z.B. nur ab 2. Drift-Beat, damit erster Drift reine Px-Belohnung bleibt).

### 2. Sweep vs. Warteszene-Mechanik — **KLARSTELLUNG NÖTIG**

`kampagnenstruktur.md` Z.737–738 (bestehend): *„Jede Sweep-Szene kostet TTL - 2 Min und Stress +1 (Ausführender).“* Z.784–785 (Patch): *„W6 pro Warteszene (zusätzlich zum bestehenden Sweep-Risiko, gewichtet ab der 2. Szene nach Exfil-Fenster-Öffnung)“*.

„Zusätzlich“ ist da, aber **Definition unklar**: Ist eine Sweep-Szene auch eine Warteszene? Konsequenz hat zwei Lesarten:

- **Lesart A** (Sweep = Warteszene): Sweep zählt mit. Ein Sweep ab 2. Szene → TTL -2 Min **plus** Stress +1 **plus** W6 Drift-Wurf. Das macht 2 Sweeps stat. sehr teuer und trifft die Empfehlung *„0–2 Sweeps“* (Z.745) hart.
- **Lesart B** (Sweep ≠ Warteszene): „Warteszene“ = passives Verharren, „Sweep“ = aktives Suchen. Dann müsste der Spieler aktiv „sweepen“ um zwei Würfe (Sweep-Stress + Drift) zu vermeiden. Auch nicht trivial.

**Fix:** Eine Zeile Definition. Empfehlung Lesart A, weil Patch-Begründung Z.810 explizit sagt *„oder Sweeps macht, desto wahrscheinlicher reagiert die Welt“* — Sweeps **sollen** Drift triggern. Also explizit: *„Sweep-Szenen zählen als Warteszenen für die Causality-Drift-Wurf-Mechanik.“*

### 3. Fremdfraktions-Intervention-Trigger — **MAKRO FEHLT**

`kampagnenstruktur.md` §Fraktionsinterventionen (Z.195–207) etabliert die kanonische Mechanik: 1W6 zu Missionsbeginn, `5-6 = aktiver Eingriff`, danach `log_intervention({'result': status, 'faction': fraktion, 'impact': konsequenz})`.

Der Patch (Z.803–805) sagt nur *„Fremdfraktions-Intervention wird im nächsten Beat ausgespielt“* — kein Verweis auf das Makro, keine Spezifikation **welche** Fraktion eingreift (die etablierte aus der Missions-Eröffnung? Eine neue?), keine Beat-Pflicht (eine volle Szene Gegenwehr, wie §Fraktionsinterventionen vorschreibt). Wenn die Mission bei `1-2` (ruhig) startete, gibt es noch gar keine etablierte aktive Fraktion — wird sie jetzt nachträglich aktiviert?

**Fix:** Patch ergänzen um *„Eskalation triggert die in der Missions-Eröffnung gewählte Fremdfraktion auf `aktiver Eingriff`-Status (mindestens eine volle Szene Gegenwehr, siehe §Fraktionsinterventionen). Pflicht: `log_intervention({'result': 'escalated', 'faction': fraktion, 'impact': 'causality_drift_cascade', 'escalated': true})` nach der Szene.“*

### 4. Multiplayer-Lücke — **KONKRETE FÜLLUNG NÖTIG**

`masterprompt_v6.md` Z.161–165 etabliert drei Multiplayer-Modi: Squad-Manöver (kein Split), Core-Split mit `family_id`, Solo. Der Patch behandelt Squad nur halb (Z.776 *„Stress +1 für alle Squad-Mitglieder“* beim Alt-Anchor — gut), sagt aber **nichts** zu Drift-Würfel bei mehreren Threads:

- Squad-Manöver in einer Szene (mehrere Chars, eine Crew, ein Raum): **Ein Wurf für die Crew** oder **ein Wurf pro Char**?
- Core-Split mit `family_id` (parallele Threads in derselben Mission): Wirft jeder Thread separat? Beeinflusst ein Drift-Beat in Thread A das Px-Konto, das ja Mission-übergreifend ist?

Lücke ist real, weil Save-Schema v7 Px pro Mission tracked und Splits in `continuity.shared_echoes[]` konsolidieren. Ohne Klarstellung bekommt die SL bei Core-Split-Sessions inkonsistente Antworten.

**Fix:** Eine Sektion *„Multiplayer-Verhalten“* mit drei Sätzen:
1. Squad-Manöver: **ein Wurf pro Warteszene** (Crew als Einheit gewertet, Drift trifft narrativ alle).
2. Core-Split: **ein Wurf pro Thread pro Warteszene**, jeder Drift erhöht das gemeinsame Px-Konto **getrennt** (kann zur Doppel-Eskalation führen wenn Thread A und B beide Drift treffen — bewusst so).
3. Eskalations-Schwelle „3 Drift-Beats pro Mission“ zählt **mission-weit**, auch über Threads aggregiert.

### 5. Cross-Verweise — **3/4 valide, 1 fehlt**

- ✓ `{#exfil-stress-pflichtgate}` sauber definiert (`kampagnenstruktur.md` Z.748), Backlink aus `sl-referenz.md` Z.470 auflösbar.
- ✓ *„Masterprompt §C IA/RW-Spot-Pflichtgate“* existiert (`masterprompt_v6.md` Z.129+), Alt-Anchor-Regel verweist korrekt.
- ✓ *„Masterprompt §C Mission-Integrität-Pflichtgate“* existiert (Z.123+), 12/14-Korridor-Verweis korrekt.
- ✗ *„§D Paradoxon & TEMP“* wird im Patch (`kampagnenstruktur.md` Z.795) referenziert, der **Verweis ist sinnvoll** (Belohnungs-Invariante absichern), aber ohne Datei-Pfad — Leser muss raten, dass §D in `meta/masterprompt_v6.md` Z.207+ steht. **Fix:** *„(Belohnungssystem, kein Punktabzug — siehe Masterprompt §D Paradoxon & TEMP, `meta/masterprompt_v6.md`)“*.

## Empfehlung

**Mini-Fix-Diff vor Commit** (alles in `gameplay/kampagnenstruktur.md`):

1. **Typo Z.770:** `belieg` → `beliebig`.
2. **Px-Framing schärfen** (nach Z.798 einfügen):
   > **SL-Framing-Pflicht:** Drift-Beat wird dem Spieler **niemals** als „ihr habt’s vermasselt“ präsentiert, sondern als *„ihr habt unbewusst eine Spur gedrückt — Px steigt, Rift näher.“* (Belohnungs-Invariante §D Paradoxon & TEMP, `meta/masterprompt_v6.md`).
3. **Sweep-Klarstellung** (Z.785 erweitern):
   > „W6 pro Warteszene (Sweep-Szenen zählen als Warteszenen; bestehende Sweep-Kosten TTL -2 / Stress +1 bleiben zusätzlich aktiv) …“
4. **Fraktions-Makro-Verweis** (Z.803–805 ergänzen):
   > „… Fremdfraktions-Intervention wird im nächsten Beat ausgespielt (siehe §Fraktionsinterventionen, mindestens eine volle Szene Gegenwehr). Pflicht: `log_intervention({'result': 'escalated', 'faction': <missions-fraktion>, 'impact': 'causality_drift_cascade', 'escalated': true})`.“
5. **Multiplayer-Sektion** (nach Z.806 einfügen):
   > **Multiplayer-Verhalten:** Squad-Manöver = **ein W6 pro Warteszene** für die Crew (Drift trifft narrativ alle, Px +1 einmal). Core-Splits mit `continuity.split.family_id` = **ein W6 pro Thread pro Warteszene** (Drift-Beats akkumulieren mission-weit über alle Threads; die 3-Beat-Eskalation zählt aggregiert). Stress +1 bei Alt-Anchor gilt pro betroffener Squad (nicht pro Thread).
6. **Heat +1 entschärfen** (Z.797): Optional — aktuelle Lesart „Px +1 (Belohnung) + Heat +1 (Strafe) gleichzeitig“ ist mechanisch inkohärent. Vorschlag: Heat +1 **erst ab 2. Drift-Beat**, damit erster Drift reine Belohnung ist und Eskalation erst danach Druck aufbaut.

Nach diesen 6 Mini-Fixes: **GO**, Squash-Merge-fähig. Branch ist Pflicht-Commit-Message-konform aufzubereiten (siehe TOOLS.md §PR-Flow — `commit-msg-prepare.sh --commit`).
