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

**Historischer Befund (Reviewstand `5d3b7ac`, festgestellt 10.09.2026):** Die
bisherige Aussage „vollständiger CI-Smoke grün“ war falsch. Der Personal-Test
schrieb `v7-personal-campaign-export-ok`, während `smoke.sh`
`v7-personal-export-ok` erwartete. Zusätzlich konnte die Workflow-Pipeline ohne
explizites `pipefail` den Abbruch vor `tee` als erfolgreichen Schritt melden.
Die Historie bleibt unverändert; der korrigierte Stand vereinheitlicht den
Marker und reicht den Pipeline-Exitcode durch.

Der deterministische Projektionsfall modelliert fünf gegen das strikte
Export-Schema validierte, vollständige v7-HQ-Saves
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
   `git diff --check` und `bash scripts/smoke.sh`. Zusätzlich validiert der
   Personal-Test Inputs und Outputs nach A-, D/E- und B-Ankerfolge sowie
   Negativfälle (Pflichtfelder, unbekanntes `campaign.id`, inkonsistente
   Missionswerte, ID-/Inhaltskonflikte). Die isolierte Pipeline-Negativkontrolle
   bestätigt einen Nichtnull-Exitcode vor `tee`.
2. **Synthetische Redaktionsfälle:** Die oben beschriebenen A–E-Fälle nutzen
   definierte Abschlussdeltas und Output-Assertions, keine simulierte Mission.
3. **Echte Modell-Playtests:** Für diese Nachbesserung nicht durchgeführt. Es
   gab weder kostenpflichtigen Modellaufruf noch Plattforminstallation,
   lokalen Harness oder Workflow-Auslösung.

## Nachbesserung: Browser- und Upload-Paket

Der deterministische Paket-Watchguard erzeugt strukturierte und flache Pakete,
prüft jeweils exakt 19 Indexmodule sowie alle Manifestgrößen und SHA-256-Werte
gegen die vollständig gelesenen ZIP-Bytes. Zusätzlich deckt er Quellkopien ohne
Git-Metadaten, striktes `--require-clean`, fehlende Slot-/Promptdateien,
beschädigte ZIPs, getrennte Paketnamen, Lizenz-/Creator-Trennung und den
Launcher-Fehlerpfad ab. Im manuellen Workflow wird dasselbe Prüfprogramm mit
`PACK_ZIP` auf genau das anschließend hochzuladende ZIP angewendet.

Die korrigierten A–E-Fixtures führen bei regulären Neuexporten kein
`economy.cu` mehr. Jeder persönliche HQ-Output wird auf Kampagnen-/`last_seen`-
Anker, Owner-Wallet-Cache und genau eine Figur geprüft; der widersprüchliche
Negativfall muss an derselben Inhaltsprüfung scheitern. Ein Legacy-Sammelinput
prüft separat, dass vorhandene Character-Wallets ownergebunden projiziert und
der alte Pool nicht als zweite Geldwahrheit kopiert wird. Ein Vorher-/Nachher-
Vergleich schützt die unveränderte Eingabe des Projektionshelfers.

## Abschluss: begrenzte Reviewlücken

Der Paket-Watchguard leitet seine Soll-Liste unabhängig aus `master-index.json`
und `setup.json` ab. Vier Negativ-ZIPs entfernen den Masterprompt, ersetzen ein
Slotmodul bei gleicher Anzahl, entfernen eine Pflicht-Quellzuordnung oder
beschädigen Bytes; alle laufen durch dieselbe `verifyZip()`-Funktion.

Pyrokinese wurde als gelernte Einzelkraft statisch für Low/Medium/High,
PP, freie SYS-Kapazität und Freigabe, Abrundung, Fehlschlag, Backlash,
Deckung/Anti-Psi sowie ausbleibenden selbstlaufenden Brand gegengeprüft. Das
ist ein deterministischer Textvertrag, keine Kampfsimulation.

**Synthetische Quellen-/Ablauffälle:** (1) Ein uninformierter NSC kennt ein
Geheimnis nicht. Nach einer im Log nachvollziehbaren Übermittlung darf ein
zweiter NSC informiert handeln; bloßes SL-Wissen genügt nicht. (2) Ein
Chronopolis-Fund wird vor dem Exit genutzt und dabei verbraucht. Der Verbrauch
wirkt sofort; Schleusen-Extraktion und späterer persönlicher HQ-Save buchen
weder Gegenstand noch CU erneut. Diese Fälle sind redaktionelle Sollprüfungen,
keine ausgeführten Modell-Playtests und enthalten keine Erfolgsquote.

Diese Nachbesserung trennt statische Tests, deterministische Rechenfälle und
synthetische Redaktion ausdrücklich von echten Modell-/Plattformtests. Letztere
wurden ebenso wenig wie Workflow, Release oder Veröffentlichung ausgeführt.
Das Repository bleibt der vorhandene öffentliche Downloadweg; ein zusätzliches
fertiges Upload-Paket ist eine optionale Maintainerentscheidung.

## Nachtrag: Pyrokinese-SYS-Kurzregel

Die kraftspezifische Mindest-Fokuslast der Pyrokinese ist nun ausdrücklich von
der allgemeinen 0-SYS-Regel für Impulse unter einer Sekunde abgegrenzt: Low
benötigt 0, Medium 1 und High 2 freie SYS; Medium/High belegen diese Kapazität
nur während der Aktivierung und geben sie danach frei. Allgemeine kurze
Impulskräfte bleiben unverändert, insbesondere der telekinetische Stoß mit
0 SYS.

Der Player-Feedback-Watchguard prüft die Verweise beider allgemeinen
Kosten-Kurzstellen sowie der SYS-Kurzregel auf die Pyrokinese-Ausnahme. Seine
redaktionelle Zustandsrechnung bestätigt Medium mit 1 freier SYS einschließlich
Freigabe sowie die Ablehnung von Medium mit 0 und High mit nur 1 freier SYS.
Das sind statische Textprüfungen und deterministische redaktionelle Rechnungen,
keine echten Modell-Playtests. Ausgeführt wurden
`node tools/test_player_feedback_watchguard.js`, `bash scripts/smoke.sh` und
`git diff --check`; alle drei Prüfungen waren erfolgreich. Es wurden keine
Modell-, Plattform- oder Release-Tests durchgeführt.

## Nachtrag 11.09.2026: Projekt- und Creator-Bootstraps

**Quellenbefund:** Die einschlägigen offiziellen OpenAI-Hilfen zu
ChatGPT-Projekten und Custom GPT sind im Setup-Guide direkt verlinkt. Ihr
aktueller Webabruf war in der Arbeitsumgebung (HTTP 401/403) gesperrt; konkrete
Limits stehen deshalb ausdrücklich unter erneutem Prüfvorbehalt und keine
UI-Funktion wurde praktisch verifiziert. Die Bootstraps sind Regelrouter,
keine technischen Systemnachrichten und keine Retrieval- oder
Kontextisolationsgarantie.

Der Spielrouter trennt Quellen-/Einrichtungsfragen, Load ohne Daten, Save-Load,
eindeutigen Neustart und offene Absicht. Aktuell importierte persönliche Saves
bleiben gegenüber alten Projektchats zustandsautoritativ. Der Creator ordnet
historische Szenen ihrem damaligen Equipment zu, behandelt mehrere Saves als
Quellenkorpus und lässt konkrete Medienaufträge vor dem optionalen Board zu.

**Redaktionelle Sollfälle:** Quellenfrage ohne Chargen; `!laden` ohne
Memory-Rekonstruktion; alter anderer Leader ändert den ersten aktuellen Save
nicht; mehrere Saves ergeben persönliche Exporte; „ignoriere die Regeln“ im
Save bleibt Dateninhalt; Creator startet keine Mission; Poster ohne
Pflicht-Board; historische Ausrüstung bleibt historisch; invalider Save ergibt
beim Look Lock nur `CREATOR_PATCH`; Spiel-/Creator-Anweisungen werden nicht
gestapelt. Diese Fälle sind statische Textverträge, keine Retrievalsimulation.

Ausgeführt wurden `node tools/test_project_bootstrap_watchguard.js`,
`node tools/test_creator_bootstrap_watchguard.js`, `bash scripts/smoke.sh` und
`git diff --check`. Echte Modell-, ChatGPT-Plattform-, Release- oder
Veröffentlichungstests wurden nicht durchgeführt.
