---
title: "Wie öffne ich ein Terminal?"
tags: [meta, setup]
---

# Wie öffne ich ein Terminal?

Ein Terminal (auch "Eingabeaufforderung" oder "Konsole") ist ein Fenster, in dem du Befehle eintippen kannst. ZEITRISS ist ein Spiel für Linux Mint; so öffnest du das Terminal dort direkt im richtigen Ordner:

> Normalerweise brauchst du das Terminal nur zum **Doppelklick auf
> `zeitriss.sh`** im entpackten Ordner (Nemo fragt dabei einmalig „Im
> Terminal ausführen") oder zum Starten über `./zeitriss.sh`, beschrieben
> unter [Spielerstart](spielerstart.md). Der Beispielbefehl unten
> (`python scripts/setup.py`) zeigt zusätzlich, wie ein Befehl in diesem
> Fenster aussieht: `setup.py` richtet die gemeinsame Backend-Einrichtung
> (OpenWebUI + LiteLLM) ein, die sowohl die KI-Spielleitung im
> Terminalspiel als auch der optionale Browser-Chat-Weg nutzen — der
> Terminal-Spielstart selbst ist `./zeitriss.sh` → Menü `[M]` bzw.
> `python3 scripts/mmo_sim.py`.

## Linux (Mint)

1. Öffne den Dateimanager und navigiere zum Ordner
2. Drücke **F4** (funktioniert in den meisten Dateimanagern)
3. Alternativ: **Rechtsklick** im Ordner → „Terminal hier öffnen" o. ä.

```bash
# Beispiel: So sieht der normale Spielstart aus
./zeitriss.sh
```

```bash
# Beispiel: So sieht die gemeinsame Backend-Einrichtung aus
python3 scripts/setup.py
```

## Andere Systeme (ungeprüfte Nebenkompatibilität)

ZEITRISS ist für Linux Mint gedacht; Windows ist kein Ziel, macOS ist eine
mögliche, ungeprüfte Nebenkompatibilität ohne Laufzusage. Die folgenden
Schritte sind keine gleichrangigen Produktwege, nur eine Referenz, falls
du es dort trotzdem versuchst.

### macOS

1. Öffne den Ordner im Finder
2. **Rechtsklick** auf den Ordner (oder Ctrl+Klick)
3. Wähle **„Neues Terminal beim Ordner"**
4. Ein Terminal-Fenster öffnet sich im richtigen Ordner

> Falls der Menüpunkt fehlt: Systemeinstellungen → Tastatur → Tastaturkurzbefehle → Dienste → „Neues Terminal beim Ordner" aktivieren.

```bash
# Beispiel: So sieht der Befehl aus
python3 scripts/setup.py
```

### Windows

1. Öffne den Ordner (z. B. den entpackten ZEITRISS-Ordner) im Explorer
2. Klicke in die **Adressleiste** oben (dort wo der Pfad steht, z. B. `C:\Users\Sarah\Downloads\ZEITRISS`)
3. Tippe `cmd` ein und drücke Enter
4. Ein schwarzes Fenster öffnet sich — du bist im richtigen Ordner

```
# Beispiel: So sieht der Befehl aus
python scripts/setup.py
```

---

**Tipp:** Befehle immer genau so eintippen wie angegeben (Groß-/Kleinschreibung beachten). Enter drücken zum Ausführen.
