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
