---
title: "ZEITRISS 4.0 – Chronometer-HUD-UI"
version: 4.0
tags: [systems]
---
# 📡 ZEITRISS 4.0 – CHRONOMETER-HUD-UI (Interface-Spezifikation)

## Übersicht

Das HUD des ZEITRISS-Chronometers ist ein lokales Interface auf dem Handgelenk jedes Chrononauten.
Es stellt **taktische Menüs, Statusanzeigen und Systemfunktionen** unabhängig vom Codex bereit – auch
bei Paradoxon, EMP oder Isolation.

**Zugriff:** jederzeit über den Sprach- oder Gedankenbefehl `menü` oder `optionen`.

---

## 📟 Systemfenster: Taktisches HUD-Menü

```

╔══════════════════════════════════════════════════════╗
║                ∎  Taktisches HUD-Menü  ∎             ║
║            [Signalquelle: Chronometer lokal]         ║
╠══════════════════════════════════════════════════════╣
║ 📍 Position: Nullzeit / Mission / Gefecht             ║
║ 🧠 Codex-Verbindung: [optional / gestört / online]    ║
╠══════════════════════════════════════════════════════╣
║ 1️⃣ Optionen        – Aktive Handlungswahl anzeigen   ║
║ 2️⃣ HUD             – Vitalstatus, SYS, Filtereffekte ║
║ 3️⃣ Log             – Missionsverlauf (chronologisch) ║
║ 4️⃣ Save            – Speicherstand erzeugen          ║
║ 5️⃣ Modus           – Erzählstil wechseln             ║
║ 6️⃣ Hilfe           – Übersicht aller Befehle         ║
║                                                      ║
║ 🛰️ Codex-Zugriff: `codex [thema]`                     ║
║ Beispiel: `codex psi`, `codex cyberware`, `codex HQ`  ║
╠══════════════════════════════════════════════════════╣
║ 🔒 Hinweis: Dieses Interface bleibt auch bei Codex-   ║
║ Unterbrechung, Paradoxon oder EMP voll nutzbar.       ║
║ Es ist physisch mit deinem Chronometer gekoppelt.     ║
╚══════════════════════════════════════════════════════╝

```

---

## 🛠️ Systemfunktionen & Befehle

| Befehl       | Wirkung |
|--------------|---------|
| `optionen`   | Blendet das obige HUD-Menü kontextsensitiv ein |
| `hud`        | Zeigt aktuelle Werte: Lebenspunkte, SYS-Belastung, aktive Filter |
| `log`        | Gibt den Missionsverlauf wieder |
| `save`       | Speichert Spielzustand / Missionsfortschritt |
| `modus`      | Ändert Erzählstil (Filmisch, Regel+Film, Klassisch) |
| `hilfe`      | Listet alle Befehle und HUD-Kommandos auf |
| `codex [x]`  | Fragt Weltwissen oder Regeln ab – abhängig von Codex-Verfügbarkeit |

---

## 🔁 Erweiterbare Module (Platzhalter)

- 🟥 `warnung` – zeigt [Vitalstatus kritisch], [Paradox-Index +1], [Filter ausgefallen]
- 🟦 `modulinfo` – zeigt aktuelle Cyberware, Bioware, Drohne, Ausrüstung
- 🟨 `temporale Umgebung` – z. B. `[Schwerkraftanomalie erkannt]` oder `[Zeitschleife → 14s Delay]`
- 🟩 `drohnenstatus` – Statusanzeige von VARC oder anderer Begleiteinheit

---

## 🔒 Technischer Hinweis

> **Das HUD ist lokal. Es kann nicht gehackt oder gestört werden**, außer durch komplette
> Zerstörung des Chronometers. Es ist AR-basiert, reagiert auf Neuroimpulse und wird durch
> Codex-Backup synchronisiert – wenn verfügbar.

---

## 🎮 Anwendung in der Engine / Spielumgebung

- Befehl `menü` oder `optionen` ruft **immer dieses Interface** auf
- `?` als Alias ist optional aktivierbar
- In Spielszenen kann das HUD **halbtransparent überlegt** oder als **volles Overlay** eingeblendet
  werden
- Die Statuswerte können als HUD-Subfenster geführt werden (`hud`-Kommando)

---

## 📌 Implementierungshinweis

Dieses Markdown kann direkt als In-Game-Fenster verwendet werden (Textengine, Bot, ChatUI). Es lässt
sich leicht in HTML oder Terminal-UIs übertragen und dient als referenzierbare Hilfe bzw.
"Escape-Menü" für Spieler.
