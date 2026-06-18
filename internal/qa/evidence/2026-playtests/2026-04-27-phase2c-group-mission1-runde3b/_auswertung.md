# Auswertung — phase2c-group-mission1-runde3b

**Datum:** 2026-04-27
**Gruppe:** Jonas (ANVIL, Ex-Soldat), Kim (GHOST/Yuna, Newbie), Sarah (SPLINTER/Mara Voss)
**Status bei Auswertung:** Harness **läuft noch** (PID 798637, Snapshot: 18 Turns vollständig, Turn 19 SL geschrieben, Spieler mitten drin). Task-Brief ging von 16 Turns + Abbruch aus — **das Run ist nicht abgebrochen**.

---

## 1. Token-Statistik & Cache-Diagnose

**Stand Turn 18** (letzter vollständiger Turn inkl. Spieler):

| Metrik | Wert |
|---|---|
| Prompt-Tokens T1 | 29.258 |
| Prompt-Tokens T18 | 56.627 |
| Prompt-Wachstum gesamt | +27.369 |
| Linearer Slope | **~1.698 Tokens/Turn** |
| Completion-Tokens ⌀ | 1.315 (Peak T7: 4.574 — Save-JSON) |
| Latenz ⌀ | **38,4 s** (Peak T7: 80,3 s; Min T1: 16,9 s) |
| cum_tokens T18 | 818.645 |

**Cache-Diagnose:** Prompt-Tokens wachsen sauber linear (~1,7k pro Turn, entspricht genau der Summe aus SL-Completion + drei Spieler-Replies). **Kein Abflachen erkennbar** — OpenRouter meldet Prompt-Tokens weiterhin unredigiert, d. h. entweder greift Prompt-Cache nicht oder der Provider billt die Token trotzdem in der Zählung. Nur auffällig: Turn 8 (Delta +20 gegenüber T7) — das ist der Moment direkt nach dem Save-Gate, wo der Save-JSON im Kontext schon drin war.

Peak T7 (5.325 Prompt-Delta zu T8, 4.574 Completion, 11.7k Zeichen SL-Output) = **Deepsave-Gate mit voll-ausgeschriebenem JSON** (`SAVE-2026-EP1-MS0-HQ-CHARGEN`). Erwarteter Ausreißer.

## 2. SL-Qualität (Stichproben T1/T5/T10/T16/T18)

**Ihr-Ansprache:** Durchgängig korrekt. Gruppenansprache wird am Turn-Ende explizit als *„Was tut ihr?"* gestellt, Einzelansprachen werden per Name adressiert (*„Jonas —"*, *„Kim — ja, 13 ist sehr gut"*). **Keine Du-Regressionen gefunden** in den Samples.

**Stop-Hint-Tags:** `Kodex:`-Zeilen erscheinen ab Turn 5 (Talente-Bestätigung), dann konstant (T10: Szene 2, T12: Mira-Briefing, T14 Entscheidungspunkt, T15 Reniers Büro, T16 Abdeckung, T18 Sprungfenster T-90). Szenenmarkierungen sauber mit `---`-Trennern. **System läuft stabil.**

**Regelkorrektheit:**
- T9: explizite **CHA-Probe** mit SG 8, 13 gewürfelt, Überschreitung um 5 → *„Er mochte dich"* (Qualitäts-Eskalation je nach Erfolgsgrad).
- T11: *Einschätzen-*Probe angeboten, *Tatortanalyse*-Scope korrekt abgegrenzt (soziale vs. physische Szene).
- T13: Regelfrage Jonas → SL klärt *Tatortanalyse nur bei physischen Szenen, INT ohne Talent für Soziales*. Sauber.
- T16: **Tarnungs-Regel erklärt** (GES vs. CHA), ANVIL-Profil korrekt bewertet. Keine Regel-Inflation.

**Narrative Qualität:** Deutlich besser als postfix-2973-2974. Miras Szene (T5, T11) hat echte Präsenz — Details wie *„Stift, Kugelschreiber, billig"* und *„aufgehört zu rechnen"* tragen. Reniers Büro (T15–T18) liefert Legende (Weinhändler Lyon), Fahrzeug (Sarlat, Rue des Tanneurs 7), LERCHE-Kontakt und saubere Rollen-Verteilung (Voss führt, Park notiert, Hartner schweigt). Spannungsbögen werden gehalten, keine Railroading-Drift.

## 3. Missions-Fortschritt

**Phasen-Verlauf:**
1. **Turns 1–4:** Gruppenstart, Charaktererstellung (ANVIL selbst-gebaut, GHOST/Yuna custom-generated, SPLINTER selbst-gebaut), HQ-Ankunft Quarzatrium.
2. **Turns 5–6:** Mira-Einführung, Retina-Overlay, Operations-Deck-Teaser.
3. **Turn 7:** **Save-Gate** ausgelöst durch Sarah (`!save`) — `SAVE-2026-EP1-MS0-HQ-CHARGEN` erzeugt, Deepsave-JSON voll ausgeschrieben.
4. **Turns 8–10:** Operations-Deck, Simultanaktion (Yuna CHA-Probe erfolgreich → Info über *„Alpha-Block, 3 Tage, Commander-Ebene, kein Team"*), Rückzug ins Atrium.
5. **Turns 11–13:** Mira-Briefing inoffiziell — das erste Team (Baur) wurde in 1943 Nordfrankreich vermisst, MERIDIAN-Verbindung.
6. **Turns 14–16:** Reniers Büro, Entscheidungspunkt, Legende gesetzt (Weinhändler Lyon, Fahrzeug Sarlat, Vane-Landgut).
7. **Turns 17–18:** Finale Briefing-Details, LERCHE-Kontakt (Apotheke Sarlat), Rollen-Festlegung, Sprungfenster T-90.

**Kodex-Stand bei T18:** `Sprungfenster T-90 Minuten. Ziel: Sarlat, Nordfrankreich, 13. November 1943.`

**Gates:** **1× Save-Gate bestanden (T7)**. Kein Level-Up-Gate (Mission 1 noch nicht gestartet).

**Abbruch-Grund T17/T19:** Kein echter Abbruch. Turn 17 hat SL-Output (2.339 Zeichen), Turn 18 ebenfalls (2.859 Zeichen). Turn 19 ist zum Zeitpunkt der Auswertung in der Verarbeitung (Live-Log: SL bereits gepostet um 15:04:15, Spieler antworten noch). Der Task-Brief hat auf einen veralteten Snapshot-Stand zugegriffen.

## 4. Vergleich mit postfix-2973-2974

| Metrik | postfix-2973-2974 | runde3b (T18) | Ratio |
|---|---|---|---|
| Turns | 54 | 18 (läuft weiter) | 0,33× |
| cum_tokens | 3.326.693 | 818.645 | 0,25× |
| Prompt T1 | 27.959 | 29.258 | +4,6 % |
| Prompt letzter | 96.902 (T54) | 56.627 (T18) | |
| Tokens/Turn (Slope) | ~1.300 | ~1.698 | +31 % |

**Warum kürzer:** runde3b ist schlicht **noch nicht fertig** — läuft weiter Richtung 80-Turn-Cap. Pro-Turn-Verbrauch ist sogar **~31 % höher** als postfix, getrieben durch (a) aktivere Spielerlogik (Kim stellt mehr Meta-Fragen), (b) ausführlichere SL-Regelerläuterungen in der frühen Phase, (c) Save-Gate-JSON T7. Extrapoliert auf 54 Turns wäre runde3b bei ~92k Prompt-Tokens und ~2,4 Mio cum — also kosteneffizienter als postfix *pro effektivem Story-Progress*, weil der Content dichter ist (Mira-Briefing + Renier-Briefing beide voll durchgespielt).

## 5. Empfehlungen

1. **Run weiterlaufen lassen bis Sprung.** Die Gruppe ist eine gute Minute vor dem Hangar-Axis-Sprung (T-75 laut T19). Es lohnt, Mission 1 auch narrativ zu starten — spätestens ab Turn 25 sollte der erste Sprung passieren, sonst zieht sich das HQ-Preamble zu weit in den Prompt-Budget.
2. **Cache-Strategie checken.** Prompt-Tokens wachsen linear ohne Cache-Hit-Erkennung. Falls OpenRouter/Sonnet Prompt-Cache unterstützt (ab 1024 Token), prüfen ob wir den Cache-Marker korrekt setzen — 18 Turns × ~1,7k gecached wäre deutliche Ersparnis.
3. **Turn-7-Muster festhalten.** Save-Gate mit vollem JSON-Echo ist der dominante Kosten-Spike (+4.574 Completion bei T7). Für zukünftige Runs prüfen, ob der JSON in einem Seitenkanal ausgegeben werden kann (Datei + kurze Bestätigung im Chat), statt voll inline — würde Folgeturns um ~5k Prompt-Tokens entlasten.
