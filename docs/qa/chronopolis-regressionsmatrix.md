# Chronopolis Regressionsmatrix

## Positivfälle

1. **Start mit Optionen:** `start_chronopolis()` zeigt HUD + Loop-Ready-Hinweis.
2. **Beat nach Aktion:** Nach `chrono_next_beat('kauf')` genau ein Beat-Toast.
3. **Exit-Druck:** `chrono_mark_big_win()` + Folgeaktion erhöht Druck und priorisiert Encounter/Twist.
4. **Sauberer Exit:** `exit_chronopolis()` deaktiviert Guards und setzt `campaign.loc='HQ'`.

## Negativfälle

1. **Stuck in Chargen:** Kein Eintritt ohne Schlüssel (`chrono_has_key() != true`).
2. **Run ohne Auswahloptionen:** Falls keine Spieleraktion, kein Beat; nach Aktion Beat-Pflicht.
3. **Persistenzfehler:** Beat-Historie bleibt runtime-transient und wird nicht als Save-Pflichtfeld geführt.

## Modellvergleich (mind. 2 LLMs)

- Sonnet: Prüfen, ob nach jeder relevanten Aktion ein Beat folgt.
- DeepSeek: Prüfen, ob Exit-Druck nach Big-Win konsistent triggert.

## Pflichtcheck

- `bash scripts/smoke.sh`

## Spielerfeedback-Patch 2026-09-10: Loot und Extraktion

| Fall | Prüfsoll |
| --- | --- |
| R1 | Loot wird vor dem Exit erlangt und bei erfüllten Regeln im Run benutzt. |
| R2 | Verbrauch oder Verlust fehlt danach korrekt im Extraktionsbesitz. |
| R3 | Höhere vorhandene Tier-/Wirkungsqualität erzeugt erkennbar höheren, plausibel verursachten Extraktionsdruck. |
| R4 | Heimlicher Fund ohne Alarm erzeugt kein Gegnerwissen. |
| R5 | Schleichen/Täuschung/Umweg kann ohne Pflichtboss erfolgreich extrahieren. |
| R6 | Exit vergibt keine XP; HQ-v7-Save enthält nur abgeglichenen Besitz. |
| R7 | Load/Join/Merge dupliziert weder einmaligen Fund noch CU-Buchung. |
| R8 | Gruppen-Reload rollt den verworfenen Run vollständig zurück. |

Diese Sollfälle sind Redaktionsfälle, kein Beleg für Modellverhalten. Die
statischen Anker und der erzeugte Paketinhalt laufen im Smoke-Watchguard;
echte Modell-Playtests werden separat protokolliert.
