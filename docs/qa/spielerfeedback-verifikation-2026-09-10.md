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
