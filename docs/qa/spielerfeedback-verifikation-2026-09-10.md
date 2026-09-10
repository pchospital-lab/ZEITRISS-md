# Spielerfeedback-Verifikation · 10.09.2026

## Umfang

Gezielter Redaktionspatch für Browser-Onboarding, individuelles NSC-Wissen,
Chronopolis-Loot/Extraktion, Charakterbogen-/v7-Kontinuität und den übernommenen
Designvorschlag Pyrokinese. Keine Website, neue Engine, Währung oder Save-Version.

## Evidenztrennung

1. **Statisch/deterministisch:** `git diff --check`, Paket-Watchguard und voller
   `bash scripts/smoke.sh`. Der Watchguard erzeugt echtes Verzeichnis und ZIP,
   prüft 19 Module, SHA-256-Dateien, Prompt-/Bootstrap-Paketpfade,
   Ausschluss unerwünschter Bäume und den Negativfall eines fehlenden Pflicht-
   Bootstraps. Ergebnis wird nach Ausführung in Commit/PR dokumentiert.
2. **Synthetische Redaktionsfälle (nicht ausgeführt als Modelltest):** N1–N6
   (Tarnname, Privatgespräch, belegte Nachricht, etablierter Verräter/Sensor,
   Epochenwissen, sichtbarer Verdacht), R1–R8 der Regressionsmatrix und P1–P4
   (Stufenwerte, Ressourcen, Reichweite/Abwehr, kein Folgebrand) wurden als
   Soll-/Gegenfälle gegen die Regeltexte geprüft. Das beweist kein LLM-Verhalten.
3. **Echte Modell-Playtests:** In diesem Patch nicht durchgeführt. Der erwähnte
   frühere ChatGPT-Projektlauf ist Nutzerfeedback ohne bestätigte Modell-ID,
   keine Abnahme. OpenWebUI, ChatGPT-Projekte, Lumo und weitere Plattformen
   wurden hier nicht mit einem Modell bespielt.

## Kontinuitäts-Soll

Figur/Stil → Chargen → HQ-`!save` → neuer Chat/Load → kurze Auto-HQ-Absegnung
und Einsatz im selben Chat → vollständiger Debrief → freie HQ-Phase →
spielerbefohlenes `!save` → neuer Chat → gleicher v7-Bogen und belegter
Anschluss derselben Episodenepoche. `!bogen` ist jederzeit Ansicht, kein Save.
Gruppen-Join/-Leave behält IDs und Wallets; Rollback mischt keinen verworfenen
Chronopolis-Besitz ein. Die bestehenden Save-/Load-/Merge-Tests bleiben die
rechenbare Evidenz; es wurde kein Mini-Spielinterpreter ergänzt.

## Nachbesserung: persönliche Kampagnen-Saves

Der deterministische Projektionsfall modelliert fünf vollständige v7-HQ-Saves
mit getrennten Kampagnen A–E auf Missionsständen 4/2/7/1/6, Geschichten,
Wallets, Forschungsständen, offenen Fäden und persönlichen Begleitern. Nach
einem definierten Einsatz mit A als erstem Save prüft er fünf persönliche
Exporte: A schreitet auf Mission 5 fort, B–E bleiben auf 2/7/1/6; individuelle
XP/CU-Deltas, ein eindeutig zugeordnetes Unikat und die gemeinsame Erinnerung
werden tatsächlich am Output geprüft.

Zusätzlich werden Allein-Loads, ein neuer A/B/C- und D/E-Chat, Fortschritt nur
der D-Ankerkampagne, späterer B-Anker, Import-Deduplizierung, ID-Konflikt,
persönliche Begleiter, Solo-/Duo-Anzahl, Legacy-Sammelimport und HQ-SaveGuard
als synthetische deterministische Fälle ausgeführt. Der kleine Helfer unter
`tools/lib/` projiziert ausschließlich vorgegebene Testdeltas; er ist keine
Runtime, kein Missionssimulator und kein Kampagnen-Verwaltungssystem.

**Evidenztrennung dieser Nachbesserung:**

1. **Statisch/deterministisch ausgeführt:**
   `node tools/test_v7_personal_export.js`,
   `node tools/test_npc_continuity_consistency.js`,
   `node tools/test_onboarding_start_save_watchguard.js`,
   `git diff --check` und `bash scripts/smoke.sh`.
2. **Synthetische Redaktionsfälle:** Die oben beschriebenen A–E-Fälle nutzen
   definierte Abschlussdeltas und Output-Assertions, keine simulierte Mission.
3. **Echte Modell-Playtests:** Für diese Nachbesserung nicht durchgeführt. Es
   gab weder kostenpflichtigen Modellaufruf noch Plattforminstallation,
   lokalen Harness oder Workflow-Auslösung.
