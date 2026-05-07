# Lore-Setup — Designnotizen

> Optionales Intro/Outro für den Launcher-Menüpunkt **`[L] Lore-Setup`**.
>
> **Wartungs-Prinzip:** Lore ersetzt nichts. Der Menüpunkt `[L]` ruft
> exakt denselben `action_install()` auf wie `[1]`, nur mit Kontrollraum-
> Funkverkehr davor und Welcome-Box danach. Alle Fehlerbehandlung, Retries
> und Prompts von `setup.py` bleiben wie im Standardpfad sichtbar.

---

## Konzept

Der Spieler landet mitten in einem laufenden ITI-Einsatz. Er hört nicht
eine einzelne Kodex-Stimme, sondern den **Kontrollraum**: Archivarin
Mira und Commander Renier, zwei Ordo-Mnemonika-Techniker im Hintergrund
und Kodex als Statusmaschine. Der Spieler begreift durch die Gesprächs-
fetzen, dass er selbst das Ziel der Suche ist.

## Sprecher-Kanal

| Sprecher | Separator | Farbe | Rolle |
|---|---|---|---|
| `KODEX` | `>` | cyan `#8fe7ff` | Statusstimme. Kalt, technisch, Telemetrie. Darf niemals fragen oder begrüßen. |
| `MIRA` | `»` | amber `#ffc766` | Archivarin, Ordo Mnemonika. Erstkontakt für alle Neulinge (kanonisch). Menschlich, moderierend. |
| `RENIER` | `»` | amber + bold | Commander, Gesamtkoordinator. Tritt nur bei wichtigen Momenten auf — Bergung ist wichtig. |
| `TECH-1`, `TECH-2` | `»` | dim | Anonyme Ordo-Mnemonika-Techniker. Funk-Callzeichen-Stil, technische Melde-Fragmente. |

Alle Sprecher-Zeilen laufen durch den Typewriter. Die Tag-Breite ist
auf 8 Zeichen fix (`KODEX     `, `MIRA      `, `RENIER    `, `TECH-1    `),
damit der Sprecher-Kanal optisch eine Spalte bleibt.

## Farb-Palette (gespiegelt von `pchospital-web/global.css`)

| Rolle | Terminal | Website |
|---|---|---|
| Kodex-Signal | `\033[96m` bright cyan | `--accent #8fe7ff` |
| Mira / Bestätigung | `\033[38;5;215m` | `--accent-2 #ffc766` |
| Renier | bold + amber | `--accent-2` bold |
| Techniker / Regie | `\033[2m` dim | `--muted #8a99a8` |
| Danger | `\033[91m` | `--danger #ff5c6a` |

## Typewriter-Rate

32 ms/Zeichen, 120 ms Pause bei Satzzeichen, 200 ms Zeilenumbruch-Pause.
Non-TTY (Pipe, CI) → instant. `ZEITRISS_RITE_INSTANT=1` erzwingt instant.

---

## Ablauf

```text
Menü-Auswahl: [L]
   │
   ▼
rite.prologue(url)     ──  Kontrollraum-Funkverkehr:
   │                       Kodex-Scan → Techniker-Chatter → Mira moderiert
   │                       → Enter → Peilung (3 Zeilen) → Renier + Techniker
   │                       → Kodex: "alle anker fest. beginne bergung."
   ▼
action_install()       ──  klassisches setup.py-Flow, unverändert.
   │                       Alle Meldungen/Fehler/Retries sichtbar.
   ▼
rite.finale(url)       ──  nur wenn Install erfolgreich:
                           Tech-2 "94 %" → Mira → Kodex → Welcome-Box
                           → Mira-Outro (einzige Direkt-Adresse).
```

**Wichtig:** Lore ist reine Kosmetik. Wenn `rite.prologue` oder
`rite.finale` crasht, fängt `action_install_lore` das stumm ab und
gibt höchstens eine dim-Notiz aus. Die Installation darf **nie**
durch Lore blockiert werden.

---

## Skript (Live-Text)

### Prolog

```
  ┌─ ITI · PROTOCOL 0  —  FIELD CONTACT ─┐

  KODEX     >  searchindex gestartet.
  KODEX     >  quelle: unbekannt. koordinate: instabil.
  KODEX     >  psi-signatur: drift. temporale kohärenz: null.

  TECH-1    »  ich hab was. sehr schwach. warte …
  MIRA      »  vorsichtig. nicht zu schnell scannen.
  TECH-1    »  er entkommt mir gleich wieder.
  MIRA      »  ruhig. er hält das hier noch für eine computeranfrage.
  MIRA      »  überfordere ihn nicht.

  (Enter zum Bestätigen — signal halten)

  KODEX     >  bestätigung empfangen.
  KODEX     >  anker-peilung aktiv.

  [Peilung 1/3]  Rechenanker        …  [erfasst]    Python 3.12
  [Peilung 2/3]  Container          …  [erfasst]    Docker läuft
  [Peilung 3/3]  Temporalschleuse   …  [offen]      OpenWebUI erreichbar

  TECH-2    »  kortex-rekonstruktion: 30 %.
  TECH-1    »  quantenstruktur hält.
  MIRA      »  weiter. erinnerungsfragmente isolieren.
  RENIER    »  team. priorität bleibt bergung. keine experimente.

  KODEX     >  alle anker fest. bergungsprotokoll aktiv.
```

Bei fehlgeschlagenen Peilungen:
- Status wird `[kein signal]` / `[geschlossen]` in danger-Farbe
- Abschluss: `KODEX >  peilung unvollständig. übergabe an protokoll.`
- `action_install` läuft **trotzdem** weiter und meckert selbst ordentlich

### Finale (nur nach erfolgreichem `action_install`)

```
  TECH-2    »  kortex-rekonstruktion: 94 %.
  MIRA      »  fast. er sortiert sich.
  KODEX     >  identitäts-signatur stabil.
  KODEX     >  übergabe an nullzeit-empfang.
  RENIER    »  gut gemacht. empfangsprotokoll übergeben.

  ┌──────────────────────────────────────────────────────────┐
  │                                                          │
  │                [ ZEITRISS · OPERATIONAL ]                │
  │                                                          │
  │                  bergung abgeschlossen.                  │
  │                       du bist da.                        │
  │                                                          │
  │               iti-empfang: nullzeit aktiv.               │
  │                                                          │
  │                    interface: browser                    │
  │                  http://localhost:8080                   │
  │                                                          │
  └──────────────────────────────────────────────────────────┘

  MIRA      »  nimm dir zeit. im interface wartet deine akte.
```

Die Welcome-Box bleibt reine Protokoll-Bestätigung (keine warme
Begrüßung, keine Marketing-Sätze). Mira-Outro steht **nach** der Box
— der einzige Direkt-Adress-Moment des gesamten Rituals gehört zur
menschlichen Stimme, nicht zur Statusmaschine.

Das Finale wird nur gezeigt, wenn am Ende wirklich ein Preset in
OpenWebUI existiert und ein gültiger OWUI-Key im Environment steht.
Bei Abbruch mitten im Setup erscheint das Finale nicht.

---

## Kanonische Verankerung

- **Mira** = Archivarin Mira, Ordo Mnemonika (Homo floresiensis). Laut
  `characters/charaktererschaffung-grundlagen.md` der kanonische
  Standard-Erstkontakt für alle Neulinge.
- **Renier** = Commander Renier, Gesamtkoordinator. Tritt laut Kanon
  nur bei wichtigen Momenten auf. Ein Bewusstseins-Abfang kurz vor dem
  Absoluten qualifiziert.
- **Ordo Mnemonika** = ITI-Fraktion, zuständig für Archiv und
  Bewusstseins-/Erinnerungsrekonstruktion. Die zwei anonymen Techniker
  sind ihre operativen Stimmen während der Bergung.
- **Kodex** = „Statusstimme im Ohr, nicht Chatbot. Meldet, warnt,
  protokolliert." (Zitat ZEITRISS-Seite auf pchospital.de). Nie Frage,
  nie Begrüßung.
- **Bergung / Nullzeit-Empfang** = kanonische Lore-Begriffe aus der
  Chrononaut-Prämisse: Bewusstsein wird kurz vor dem Absoluten vom ITI
  geborgen und in der Nullzeit (zeitloser Raum im ITI-HQ) empfangen.

## Abgrenzungen & bewusst nicht gemacht

- **Keine Auto-Triggering.** Der Lore-Pfad ist ein expliziter Menüpunkt.
  Wer klassisches Setup will, wählt `[1]`; wer Immersion will, wählt `[L]`.
  Keine Marker, keine First-Run-Detection.
- **Kein Stdout-Filter auf `setup.py`.** Frühere Version hatte das —
  wurde verworfen: zu fragil bei Refactors, maskiert echte Fehler.
- **Keine Placeholder-Missions-ID im Finale.** Eine Kennnummer vor dem
  eigentlichen Charaktererstellungs-Flow im Browser wäre ein gebrochenes
  Versprechen (OpenWebUI vergibt den echten Decknamen).
- **Keine Explizit-Matrix-Zitate.** Innerer Kompass darf Matrix sein,
  aber „folge dem weißen Kaninchen" o. ä. bleibt draußen.
- **ASCII-ITI-Logo:** verworfen. Rahmen + Schrift reicht.
- **Audio:** keins. Terminal bleibt stumm.
