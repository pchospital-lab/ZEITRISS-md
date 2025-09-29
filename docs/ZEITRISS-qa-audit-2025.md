# ZEITRISS QA-Audit 2025

## Kontext und Auftrag
Ihr habt den Systemtest zu **ZEITRISS 4.2.2** mit Fokus auf Systemkohärenz, Balance, HQ-Abläufe und urbane Interaktionen eingespielt. Dieses Audit fasst die Erkenntnisse zusammen, bewertet den aktuellen Umsetzungsstand und priorisiert die nächsten Entwicklungsschritte. Grundlage sind die aufgeführten Testbeobachtungen sowie der Repositorystand `c9a4da2`.

## Methodik
- Analyse der gelieferten Testnotizen (Solo bis Großgruppe, Level 3–100) mit Schwerpunkt auf PvP-Arena, HQ-Progression und urbanen Szenarien.
- Stichprobenhafte Abgleiche im Repository (z. B. Modul 6 Kampagnenstruktur, Toolkit-Flags für `debug_rolls`, Terminologie „Heat“).
- Priorisierung nach Auswirkung auf Spielbalance, UX und technische Konsistenz.

## Gesamtbewertung
Die Testreihe bestätigt, dass der aktuelle Build stabil läuft, jedoch mehrere Kernsysteme inkonsistent benannt oder nur teilweise abgesichert sind. Besonders kritisch sind widersprüchliche Modulnummern, farmbare Paradoxon-Belohnungen in der Arena und das uneinheitliche „Heat“-Vokabular, das Spieler:innen wie Tools verwirrt. Ohne Korrektur gefährden diese Punkte die Anschlussfähigkeit von Regelreferenzen, die Progressionsökonomie und das Balancing in Hochstufen-Spielrunden.

## Maßnahmenkatalog (Priorisiert)
1. **Modulnummern & Cross-References harmonisieren.** Modul 6 verweist weiterhin auf einen „ausgelassenen siebten Teil“, während Master-Index und Dateien Modul 7 führen. Status: *erledigt* – Modul 6, Modul 7, Kampagnenübersicht und README benennen die Sequenz nun konsistent.
2. **Paradoxon-Farm in der PvP-Arena unterbinden.** Arena-Belohnungssystem an
   Episoden- oder Rufmarker koppeln. Status: *erledigt* – Px-Bonus wird nur noch
   einmal pro Episode vergeben; `arena_episode_stamp` markiert den konsumierten
   Lauf.
3. **Heat-Terminologie trennen.** Psi-, Alarm-, Tech- und Stress-Anzeigen klar benennen; Save-Schema migrieren. Status: *erledigt* – Psi-Heat wird nun explizit geführt (`psi_heat`), Save-Version 5 migriert Altstände automatisch, HUD/Toolkits zeigen Psi-Heat getrennt von Stress & Tech-Heat.
4. **Exploding-DMG-Spitzen begrenzen.** Arena/Boss-Dämpfer als Pflicht setzen und Boss-DR automatisieren. Status: *offen*.
5. **High-Level-Progression auf Prestige-Perks umstellen.** Attribute nicht weiter erhöhen, stattdessen qualitative Boni verankern. Status: *offen*.
6. **Psi vs. Non-Psi balancieren.** Phase-Strike-Kosten in PvP anheben, Anti-Psi-Grundschutz verbreitern. Status: *offen*.
7. **Tech-Dominanz-Check auf kleine Teams ausweiten.** `tech_heat` früher triggern und Gerätezwang durchsetzen. Status: *offen*.
8. **Suspend-Snapshot als Komfortfunktion implementieren.** HQ-Save-Pflicht erhalten, aber Session-Pause erlauben. Status: *offen*.
9. **Exfil-Kommunikation im HUD verstärken.** Auto-Toasts für Arming/Alt-Anchor und RW-Ticks. Status: *offen*.
10. **Arena-Matchmaking mit Tier-Loadouts absichern.** Artefakt-Spitzen kappen, Proc-Budget limitieren. Status: *offen*.
11. **Boss-Foreshadow-Gate erzwingen.** Szene 10 blockieren, bis Hinweise geliefert sind. Status: *offen*.
12. **Mission-Generator linten.** Gewichte und Duplicate-Seeds automatisch prüfen. Status: *offen*.
13. **Endgame-Ökonomie justieren.** Chronopolis-Angebote mit Rang/Research-Gates und Daily Stock versehen. Status: *offen*.
14. **Signal-Space-Konsequenz in Texten verankern.** Remote-Hack-Formulierungen bereinigen, `comms_check()` erzwingen. Status: *offen*.
15. **Urban Quick-Card zentral anbieten.** Deckungs- und Verfolgungsreferenzen in `/help` bündeln. Status: *offen*.
16. **HQ-Moments mechanisch verankern.** Tabelle mit Buff-Icons einführen. Status: *offen*.
17. **Arena zwingt JSON-Würfellog.** `debug_rolls` standardmäßig aktivieren. Status: *erledigt* – Toolkit-Default wurde auf `true` gesetzt und README dokumentiert das neue Standardverhalten.
18. **Rift-Boss-Drops automatisieren.** Toolkit-Trigger `on_rift_boss_down()` für Loot-Erinnerung. Status: *offen*.
19. **Attribut-Cap kommunizieren.** Charaktererschaffung um Prestige-Hinweis ergänzen. Status: *offen*.
20. **Arena-Großteams mit Timern steuern.** 30-Sekunden-Takt und Move-Limit im HUD. Status: *offen*.
21. **Boss-Pressure-Variationen schützen.** Memory-Pool/Cooldown für Druck-Set-Auswahl. Status: *offen*.
22. **Self-Reflection-Flag sichtbar machen.** HUD-Badge `SF-OFF` ergänzen. Status: *offen*.
23. **Intro-Guard beim Laden aktivieren.** Einleitung nur bei Erststart zeigen. Status: *offen*.
24. **DelayConflict für Heist/Street justieren.** Mission-Tags reduzieren Verzögerung. Status: *offen*.
25. **Briefing mit ☆-Feedback ausliefern.** Overlay standardisieren. Status: *offen*.
26. **TK-Nahkampf-Cooldown visualisieren.** HUD-Icon nach Einsatz. Status: *offen*.
27. **Arena-Gebühr progressiv staffeln.** Vermögensabhängige Kosten definieren. Status: *offen*.
28. **Chronopolis-Reset-Rhythmus fixieren.** City-Tick nach Episoden und optional nach drei Missionen. Status: *offen*.
29. **Gefährdungs-Skala vereinheitlichen.** Einheitliche Risk-Level-Icons. Status: *offen*.
30. **Würfel-Benchmarks bündeln.** One-Pager für SG/Exploding-Optionen unter `/help sg`. Status: *offen*.

## Nächste Schritte
1. **Kurzfristig (Sprint 1):** Punkte 1–4 adressieren; sie beeinflussen Referenzierbarkeit, Progression und Balancing unmittelbar.
2. **Mittelfristig (Sprint 2):** Punkte 5–13 für High-Level-Spielbarkeit und UX-Stabilität umsetzen.
3. **Langfristig (Sprint 3+):** Punkte 14–30 in Toolkit- und UX-Roadmap einsortieren; mehrere lassen sich als zusammenhängende HUD-/Automation-Epics bündeln.

## Offene Fragen für das Team
- Bestätigt bitte, ob Master-Index `modul_7` künftig die kanonische Bezeichnung trägt oder ob eine alternative Nummerierung geplant ist.
- Wird die Px-Ökonomie generell überarbeitet (z. B. neue Ruf- oder Trainingsmarker), oder bleibt die Anpassung auf die Arena beschränkt?
- Welche Toolchain übernimmt das Save-Schema-Mapping (Backwards Compatibility) nach der `psi_heat`-Migration?

Bitte gebt Rückmeldung, welche Punkte Ihr bereits intern priorisiert habt, damit das Audit in nachfolgenden Iterationen aktualisiert werden kann.
