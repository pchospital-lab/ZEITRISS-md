---
title: "Wie öffne ich ein Terminal?"
tags: [meta, setup]
---

# Wie öffne ich ein Terminal?

Ein Terminal (auch "Eingabeaufforderung" oder "Konsole") ist ein Fenster, in dem du Befehle eintippen kannst. ZEITRISS ist ein Spiel für Linux Mint; so öffnest du das Terminal dort direkt im richtigen Ordner:

> Die Beispielbefehle unten (`python scripts/setup.py`) zeigen nur, wie ein Befehl in diesem Fenster aussieht — sie richten den Chat-/OpenWebUI-Weg ein und starten **kein** ZEITRISS-Terminalspiel. Der Terminal-Spielstart ist `python3 scripts/mmo_sim.py`, beschrieben unter [Spielerstart](spielerstart.md) (dort auch der normale Weg über `./zeitriss.sh` → Menü `[M]`).

## Linux (Mint)

1. Öffne den Dateimanager und navigiere zum Ordner
2. Drücke **F4** (funktioniert in den meisten Dateimanagern)
3. Alternativ: **Rechtsklick** im Ordner → „Terminal hier öffnen" o. ä.

```bash
# Beispiel: So sieht der Befehl aus
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
