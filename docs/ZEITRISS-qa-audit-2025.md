# ZEITRISS QA-Audit 2025

## Kontext und Auftrag
Ihr habt den Systemtest zu **ZEITRISS 4.2.2** mit Fokus auf Systemkohärenz, Balance,
HQ-Abläufe und urbane Interaktionen eingespielt. Dieses Audit fasst die
Erkenntnisse zusammen, bewertet den aktuellen Umsetzungsstand und priorisiert die
nächsten Entwicklungsschritte. Grundlage sind die aufgeführten Testbeobachtungen
sowie der Repositorystand `c9a4da2`.

## Methodik
- Analyse der gelieferten Testnotizen (Solo bis Großgruppe, Level 3–100) mit
  Schwerpunkt auf PvP-Arena, HQ-Progression und urbanen Szenarien.
- Stichprobenhafte Abgleiche im Repository (z. B. Modul 6 Kampagnenstruktur,
  Toolkit-Flags für `debug_rolls`, Terminologie „Heat“).
- Priorisierung nach Auswirkung auf Spielbalance, UX und technische Konsistenz.

## Gesamtbewertung
Die Testreihe bestätigt, dass der aktuelle Build stabil läuft, jedoch mehrere
Kernsysteme inkonsistent benannt oder nur teilweise abgesichert sind. Besonders
kritisch sind widersprüchliche Modulnummern, farmbare Paradoxon-Belohnungen in
der Arena und das uneinheitliche „Heat“-Vokabular, das Spieler:innen wie Tools
verwirrt. Ohne Korrektur gefährden diese Punkte die Anschlussfähigkeit von
Regelreferenzen, die Progressionsökonomie und das Balancing in
Hochstufen-Spielrunden.

## Maßnahmenkatalog (Priorisiert)
1. **Modulnummern & Cross-References harmonisieren.** Modul 6 verweist weiterhin
   auf einen „ausgelassenen siebten Teil“, während Master-Index und Dateien
   Modul 7 führen. Status: *erledigt* – Modul 6, Modul 7, Kampagnenübersicht und
   README benennen die Sequenz nun konsistent.
2. **Paradoxon-Farm in der PvP-Arena unterbinden.** Arena-Belohnungssystem an
   Episoden- oder Rufmarker koppeln. Status: *erledigt* – Px-Bonus wird nur noch
   einmal pro Episode vergeben; `arena_episode_stamp` markiert den konsumierten
   Lauf.
3. **Heat-Terminologie trennen.** Psi-, Alarm-, Tech- und Stress-Anzeigen klar
   benennen; Save-Schema migrieren. Status: *erledigt* – Psi-Heat wird nun
   explizit geführt (`psi_heat`), Save-Version 5 migriert Altstände automatisch,
   HUD/Toolkits zeigen Psi-Heat getrennt von Stress & Tech-Heat.
4. **Exploding-DMG-Spitzen begrenzen.** Arena/Boss-Dämpfer als Pflicht setzen
   und Boss-DR automatisieren. Status: *erledigt* – Arena-HUD halbiert
   Exploding-Overflow automatisch, Boss-Spawn vergibt DR 2/3 inkl. HUD-Hinweis.
5. **High-Level-Progression auf Prestige-Perks umstellen.** Attribute nicht
   weiter erhöhen, stattdessen qualitative Boni verankern. Status: *erledigt* –
   Core-Regelwerk setzt ab Prestige-Level auf erzählerische Perks und ersetzt
   den Standard-Attributsbonus durch Legendenpfade.
6. **Psi vs. Non-Psi balancieren.** Phase-Strike-Kosten in PvP anheben,
   Anti-Psi-Grundschutz verbreitern. Status: *erledigt* – Arena setzt
   `phase_strike_tax = +1 SYS`, Kernanzüge tragen `psi_buffer` (+2 SG,
   neutralisiert Bonus-Schaden).
7. **Tech-Dominanz-Check auf kleine Teams ausweiten.** `tech_heat` früher
   triggern und Gerätezwang durchsetzen. Status: *erledigt* – Solo- und
   Duo-Teams feuern `tech_solution()` nun bei niedrigeren Limits und die
   Toolkit-Makros sperren Tech-Ketten, bis `confirm_device_slot()` ein Field Kit
   bestätigt.
8. **Suspend-Snapshot als Komfortfunktion implementieren.** HQ-Save-Pflicht
   erhalten, aber Session-Pause erlauben. Status: *erledigt* – `!suspend` legt
   einen 24h-Snapshot an, `!resume` setzt ihn einmalig fort und respektiert den
   HQ-Deepsave.
9. **Exfil-Kommunikation im HUD verstärken.** Auto-Toasts für Arming/Alt-Anchor
   und RW-Ticks. Status: *erledigt* – `!exfil arm/alt/tick/status` triggern
   automatische HUD-Toasts, aktualisieren Anchor/ALT und spiegeln den Timer im
   Overlay.
10. **Arena-Matchmaking mit Tier-Loadouts absichern.** Artefakt-Spitzen kappen,
    Proc-Budget limitieren. Status: *erledigt* – Runtime-Stub erzwingt
    Tier-Gates, kappt Artefakt-Überhänge und bremst Proc-Ketten mit pro Tier
    gesetztem Budget.
11. **Boss-Foreshadow-Gate erzwingen.** Szene 10 blockieren, bis Hinweise
    geliefert sind. Status: *erledigt* – `NextScene()` hält Szene 9, bis vier
    (Core) bzw. zwei (Rift) Foreshadows über Makros registriert sind und meldet
    den Gate im HUD.
12. **Mission-Generator linten.** Gewichte und Duplicate-Seeds automatisch
    prüfen. Status: *erledigt* – `scripts/lint_mission_generator.py` prüft die
    Pools und stellt d24-Abdeckung sicher.
13. **Endgame-Ökonomie justieren.** Chronopolis-Angebote mit Rang/Research-Gates
    und Daily Stock versehen. Status: *erledigt* – Runtime koppelt das
    Tagesangebot an Dienstgrad und Research-Level, der Pool rotiert filmisch pro
    HQ-Zyklus.
14. **Signal-Space-Konsequenz in Texten verankern.** Remote-Hack-Formulierungen
    bereinigen, `comms_check()` erzwingen. Status: *erledigt* – Arena-Makro
    zwingt `must_comms`, Ausrüstungshinweis verankert Hardwarepflicht.
15. **Urban Quick-Card zentral anbieten.** Deckungs- und Verfolgungsreferenzen in
    `/help` bündeln. Status: *erledigt* – `/help urban` liefert Deckungsgrade,
    Distanzstufen und HUD-Tags; README verankert die Schnellhilfe.
16. **HQ-Moments mechanisch verankern.** Tabelle mit Buff-Icons einführen.
    Status: *erledigt* – Toolkit listet HQ-Buffs als HUD-Icons inkl.
    Makro-Snippet, Dopplungen werden per Kampagnenflag geblockt.
17. **Arena zwingt JSON-Würfellog.** `debug_rolls` standardmäßig aktivieren.
    Status: *erledigt* – Toolkit-Default wurde auf `true` gesetzt und README
    dokumentiert das neue Standardverhalten.
18. **Rift-Boss-Drops automatisieren.** Toolkit-Trigger `on_rift_boss_down()`
    für Loot-Erinnerung. Status: *erledigt* – neues Makro setzt den Boss-Flag,
    stößt das para-Loot an und markiert den Legendary-Wurf im Log.
19. **Attribut-Cap kommunizieren.** Charaktererschaffung um Prestige-Hinweis
    ergänzen. Status: *erledigt* – Charaktererschaffung betont das Cap bei 10
    und verweist auf Prestige-Aufstiege für höhere Werte.
20. **Arena-Großteams mit Timern steuern.** 30-Sekunden-Takt und Move-Limit im
    HUD. Status: *erledigt* – Arena initialisiert nun Großteam-Zyklen, trackt
    Moves und blendet Timer sowie Limit im HUD ein.
21. **Boss-Pressure-Variationen schützen.** Memory-Pool/Cooldown für
    Druck-Set-Auswahl. Status: *erledigt* – Toolkit setzt eine
    Zweifach-Cooldown-Liste ein, bevor Druck-Sets wieder freigegeben
    werden.
22. **Self-Reflection-Flag sichtbar machen.** HUD-Badge `SF-OFF` ergänzen.
    Status: *erledigt* – Runtime blendet das Badge ein, wenn `self_reflection:
    false` aktiv ist; `!sf on/off` steuern das Flag und loggen den Status.
23. **Intro-Guard beim Laden aktivieren.** Einleitung nur bei Erststart zeigen.
    Status: *erledigt* – Runtime speichert `intro_seen` im UI-State und spielt
    das HQ-Kurzintro nur beim Erststart aus.
24. **DelayConflict für Heist/Street justieren.** Mission-Tags reduzieren
    Verzögerung. Status: *erledigt* – `StartMission()` normalisiert Mission-Tags
    und `DelayConflict` senkt bei `heist`/`street` automatisch die Schwelle.
25. **Briefing mit ☆-Feedback ausliefern.** Overlay standardisieren. Status:
    *erledigt* – Toolkit zeigt das ☆-HUD beim Missionsstart automatisch,
    `briefing_with_stars()` zieht den SG-Zuschlag konsistent nach.
26. **TK-Nahkampf-Cooldown visualisieren.** HUD-Icon nach Einsatz. Status:
    *erledigt* – Runtime blendet `TK🌀` nach `!tk melee` ein und `!tk ready`
    entfernt die Sperre nach der Cooldown-Runde.
27. **Arena-Gebühr progressiv staffeln.** Vermögensabhängige Kosten definieren.
    Status: *erledigt* – Staffelung mit 1 %/2 %/3 %-Brackets koppelt Gebühren an
    das HQ-Vermögen.
28. **Chronopolis-Reset-Rhythmus fixieren.** City-Tick nach Episoden und optional
    nach drei Missionen. Status: *erledigt* – Episodenabschluss triggert
    sofortigen Reset; ein konfigurierbarer Drei-Missions-Takt hält die Stadt
    lebendig.
29. **Gefährdungs-Skala vereinheitlichen.** Einheitliche Risk-Level-Icons.
    Status: *offen*.
30. **Würfel-Benchmarks bündeln.** One-Pager für SG/Exploding-Optionen unter
    `/help sg`. Status: *erledigt* – `/help sg` fasst Würfelgrößen, Zielwerte und
    Exploding-Ansagen filmisch auf einer Zeile zusammen.

## Nächste Schritte
1. **Kurzfristig (Sprint 1):** Punkte 1–4 adressieren; sie beeinflussen
   Referenzierbarkeit, Progression und Balancing unmittelbar.
2. **Mittelfristig (Sprint 2):** Punkte 5–13 für High-Level-Spielbarkeit und
   UX-Stabilität umsetzen.
3. **Langfristig (Sprint 3+):** Punkte 14–30 in Toolkit- und UX-Roadmap
   einsortieren; mehrere lassen sich als zusammenhängende HUD-/Automation-Epics
   bündeln.

## Offene Fragen für das Team
- Bestätigt bitte, ob Master-Index `modul_7` künftig die kanonische Bezeichnung
  trägt oder ob eine alternative Nummerierung geplant ist.
- Wird die Px-Ökonomie generell überarbeitet (z. B. neue Ruf- oder
  Trainingsmarker), oder bleibt die Anpassung auf die Arena beschränkt?
- Welche Toolchain übernimmt das Save-Schema-Mapping (Backwards Compatibility)
  nach der `psi_heat`-Migration?

Bitte gebt Rückmeldung, welche Punkte Ihr bereits intern priorisiert habt, damit
das Audit in nachfolgenden Iterationen aktualisiert werden kann.
