# ZEITRISS®-md Zeitreise RPG

[![LLM-Ready ✅][llm-ready-badge]][llm-ready-link]

> **Kurzfassung:** ZEITRISS® schickt euch als operative Chrononauten in ein
> Tech-Noir-Zeitreise-RPG mit KI-Spielleitung, explodierenden Würfeln und
> JSON-Charakterbögen.
> **Hinweis (18+):** Die Inhalte richten sich ausschließlich an Erwachsene.
> **Wichtig:** ZEITRISS ist für KI-Spielleitung gebaut; klassischer Start ist
> als empfohlener Modus die Referenz.

→ [Spieler-Handbuch (Regeln, Einleitung, Schnellstart)](core/spieler-handbuch.md)
→ [Setup-Guide (lokales Hosting)](docs/setup-guide.md)

## In 5 Minuten starten

### Nur kurz reinschauen (Schnellstart für Ungeduldige)

1. Öffnet das [Spieler-Handbuch](core/spieler-handbuch.md).
2. Nutzt den Schnellstart und erstellt eure Chrononauten.
3. Startet direkt mit `Spiel starten (solo schnell)`.
4. Für die volle Experience wechselt danach auf den klassischen Start.

### Empfohlener Weg: OpenWebUI + OpenRouter

1. Installiert OpenWebUI und richtet ein OpenRouter-Konto ein.
2. Folgt dem [Setup-Guide](docs/setup-guide.md) oder startet direkt mit
   `./scripts/setup-openwebui.sh`.
3. Hinterlegt im Setup eure Keys und wählt ein Modell.
4. Startet im Preset am besten mit `Spiel starten (solo klassisch)`.

→ [Paradoxon-Index](systems/gameflow/speicher-fortsetzung.md#paradoxon-index)
→ [Immersives Laden](systems/gameflow/speicher-fortsetzung.md#immersives-laden)
→ [Makros im Überblick](systems/gameflow/speicher-fortsetzung.md#makros-im-ueberblick)

## TL;DR - ZEITRISS in 6 Punkten

1. **Agenten.** Als Chrononauten deckt ihr Zeitverschwörungen auf.
2. **Missionsphasen.** Eine **Mission** läuft über Briefing → Infiltration →
   Intel/Konflikt → Exfiltration → Debrief und umfasst meist zwölf Szenen.
   Eine **Episode** bündelt rund zehn Missionen derselben Epoche; Rift-Ops
   sind Sondermissionen in drei Akten mit vierzehn Szenen.
3. **Explodierende Würfel.** W6, ab Attribut 11 W10; Heldenwürfel erst ab 14.
4. **Paradoxon-Index (Px)** misst eure temporale Resonanz - ein **Belohnungssystem**.
   Stilvolles, professionelles Vorgehen lässt den Index steigen. Bei Px 5 enthüllt
   `ClusterCreate()` 1-2 Rift-Seeds auf der Raumzeitkarte - Bonus-Missionen mit
   Paramonstern und Artefakten. Danach springt der Px für den nächsten Zyklus auf 0;
   weitere Px-5-Treffer stapeln zusätzliche Seeds im Pool. Chaos oder grobe Paradoxa
   halten den Index niedrig; in Extremfällen kostet das ausnahmsweise **-1 Px**.
5. **Klassik als Default.** Mischform aus filmischen und taktischen Regeln;
   Schnellstart dient nur dem schnellen Eindruck.
6. **Boss-Rhythmus.** In der **5. Mission einer Episode** erscheint ein
   Mini-Boss, in der **10. Mission** der Episoden-Boss. Rift-Operationen
   führen ihren Endgegner im finalen Akt ein (meist um Szene 10). Das Toolkit
   löst `generate_boss()` an diesen Punkten automatisch aus.

→ Das vollständige **[Spieler-Handbuch](core/spieler-handbuch.md)** enthält
Einleitung, Lore, Schnellstart-Spickzettel, Mini-Einsatzhandbuch, FAQ, Glossar
und die Runtime-Referenz.

## Lizenz & Nutzung (Kurzfassung)

- **Privatnutzung:** Kostenlos für private Einzelspiel- oder Gruppenrunden.
  Anpassungen sind erlaubt, solange die CC BY-NC 4.0 eingehalten und
  "ZEITRISS® - pchospital" genannt wird.
- **Kommerzielle Nutzung:** Jede Nutzung in kommerziellen Produkten,
  Plattformen oder Services erfordert eine schriftliche Lizenzvereinbarung.
  Details und Anfragen laufen über die im Repository genannten
  Maintainer-Kanäle (siehe [LICENSE](LICENSE)).
- **Creator-Nutzung:** Monetarisierte Gameplay-Videos/Streams sind über die
  Zusatzfreigabe in [`docs/creator-license.md`](docs/creator-license.md) erlaubt
  (inkl. Attribution und Markenleitplanken).
- **Marke & Altersfreigabe:** ZEITRISS® ist markenrechtlich geschützt, die
  Inhalte richten sich ausschließlich an Erwachsene (18+).

## Release- und Hosting-Modell (Public Repo)

- **Keine vorgefertigten gehosteten GPT-Builds:** Dieses Repository stellt
  Regeln, Runtime-Module und Werkzeuge bereit, aber keine dauerhaft
  betriebenen Fremdinstanzen.
- **Self-Hosting auf eigene Verantwortung:** Nutzung erfolgt lokal oder im
  eigenen Hosting-Stack (z. B. OpenWebUI/Ollama oder kompatible Setups).
  Sicherheitsdefaults für OpenWebUI stehen im
  [`docs/setup-guide.md`](docs/setup-guide.md#sicherheitsdefaults-für-openwebui).
- **KI-first Betrieb:** Das Spiel ist auf KI-Leitung im Chat ausgelegt
  (Text, optional Voice in kompatiblen UIs wie OpenWebUI).
- **Lokale Modelle:** Reiner Offline-Betrieb mit lokalem Modell ist derzeit
  meist zu fordernd; empfohlen sind starke Remote-Modelle.
- **Setup-Option:** Für lokale Installationen steht
  [`scripts/setup-openwebui.sh`](scripts/setup-openwebui.sh) als Hilfsskript bereit
  (provider-neutral mit expliziter Modellwahl; DeepSeek V3 als empfohlener Default,
  Sonnet 4 als Premium-Alternative).
- **Multiplayer-Hinweis:** Lokal oder online mit Gruppe möglich; Save-Stand und
  Chatlog können zwischen Sessions geteilt werden.
- **Betriebshinweis:** Es gibt keine zugesicherte Verfügbarkeit, keinen
  individuellen Endnutzer-Support und keine SLA für private Nutzung (Details in
  [LICENSE](LICENSE)).
- **GitHub-GUI-Feinschliff:** Eine kurze Maintainer-Checkliste für finale
  Public-Settings liegt unter
  [`docs/github-public-checkliste.md`](docs/github-public-checkliste.md).

## Markenhinweis / Inspiration

- Vergleiche mit bekannten Franchises dienen nur der stilistischen Einordnung.
- Es besteht keine Verbindung, Kooperation oder Empfehlung durch Drittmarken.
- Namen und Logos Dritter dürfen nicht als Produktkennzeichen für ZEITRISS
  verwendet werden.

## Recht & Marke (kurz)

- ZEITRISS® ist eine eingetragene Marke von Florian Michler.
- Das vollständige DPMA-Dossier (Aktenzeichen 30 2025 215 671.9) liegt
  repo-intern vor.

## Schnellzugriff auf ausgelagerte Regelteile

Ausführliche Laufzeitregeln liegen in [`core/sl-referenz.md`](core/sl-referenz.md).

_Wartungshinweis:_ Wenn Navigation oder Überschriften in `core/sl-referenz.md`
geändert werden, diese Linkliste direkt mitziehen.

- [Agenda für Session 0](core/sl-referenz.md#agenda-session-0)
- [Wahrscheinlichkeits-Übersicht](core/sl-referenz.md#wahrscheinlichkeits-uebersicht)
- [Chat-Kurzbefehle](core/sl-referenz.md#chat-kurzbefehle)
- [Exfil-Fenster & Sweeps](core/sl-referenz.md#exfil-fenster--sweeps)
- [Level & EP-Kurve](core/sl-referenz.md#level--ep-kurve)
- [Regelreferenz](core/sl-referenz.md#regelreferenz)
- [Spielstart](core/sl-referenz.md#spielstart)
- [Spielmodi](core/sl-referenz.md#spielmodi)
- [Generator-Utilities](core/sl-referenz.md#generator-utilities)

## Feedback & Beiträge

**Pull Requests werden nicht angenommen.** Das Projekt wird vom Maintainer
direkt gepflegt. Wenn dir etwas auffällt — Regelfehler, Balancing-Probleme,
Ideen, Tippfehler — erstelle bitte ein
[Issue](https://github.com/pchospital-lab/ZEITRISS-md/issues) mit einer kurzen
Beschreibung. Feedback wird gesammelt und gebündelt umgesetzt.

Die verbindliche Public-Policy (Issue-Kanal, kein SLA, Umsetzung nach
Maintainer-Ermessen) steht in [`docs/community-policy.md`](docs/community-policy.md).

Sicherheitsmeldungen bitte gemäß [`SECURITY.md`](SECURITY.md) einreichen.

Danke für dein Interesse an ZEITRISS. 🕐

[llm-ready-badge]: https://img.shields.io/badge/LLM--Ready-%E2%9C%85-success
[llm-ready-link]: systems/gameflow/speicher-fortsetzung.md#paradoxon-index

© 2025 pchospital – ZEITRISS® – private use only. See LICENSE.
