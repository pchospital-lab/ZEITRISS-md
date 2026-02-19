# ZEITRISS®-md Zeitreise RPG

[![LLM-Ready ✅][llm-ready-badge]][llm-ready-link]

> **Kurzfassung:** ZEITRISS® schickt euch als operative Chrononauten in ein
> Tech-Noir-Zeitreise-RPG mit KI-Spielleitung, explodierenden Würfeln und
> JSON-Charakterbögen.
> **Hinweis (18+):** Die Inhalte richten sich ausschließlich an Erwachsene.
> **Markenhinweis:** ZEITRISS® ist eine eingetragene Marke von Florian Michler.
> **DPMA-Dossier:** Der vollständige Registerauszug liegt repo-intern vor;
> haltet das Aktenzeichen 30 2025 215 671.9 bereit.

→ [Spieler-Handbuch (Regeln, Einleitung, Schnellstart)](core/spieler-handbuch.md)
→ [Paradoxon-Index](systems/gameflow/speicher-fortsetzung.md#paradoxon-index)
→ [Immersives Laden](systems/gameflow/speicher-fortsetzung.md#immersives-laden)
→ [Makros im Überblick](systems/gameflow/speicher-fortsetzung.md#makros-im-ueberblick)

## TL;DR - ZEITRISS in 6 Punkten

1. **Agents.** Chrononauten decken Zeitverschwörungen auf.
2. **Mission Phases.** Core-Ops verlaufen wie Episoden: Briefing → Infiltration →
   Intel/Konflikt → Exfiltration → Debrief - insgesamt zwölf Szenen. Rift-Ops sind
   eigenständige Filme in drei Akten mit vierzehn Szenen.
3. **Exploding Dice.** W6, ab Attribut 11 W10; Heldenwürfel erst ab 14.
4. **Paradoxon-Index (Px)** misst eure temporale Resonanz - ein **Belohnungssystem**.
   Stilvolles, professionelles Vorgehen lässt den Index steigen. Bei Px 5 enthüllt
   `ClusterCreate()` 1-2 Rift-Seeds auf der Raumzeitkarte - Bonus-Missionen mit
   Paramonstern und Artefakten. Danach springt der Px für den nächsten Zyklus auf 0;
   weitere Px-5-Treffer stapeln zusätzliche Seeds im Pool. Chaos oder grobe Paradoxa
   halten den Index niedrig; in Extremfällen kostet das ausnahmsweise **-1 Px**.
5. **Klassik als Default.** Mischform aus filmischen und taktischen Regeln; Film bleibt optional
   für cineastisches Tempo.
6. **Boss-Rhythmus.** In Mission 5 einer Episode erscheint ein Mini-Boss, in
   Mission 10 der Episoden-Boss. Rift-Operationen führen ihren Endgegner im
   finalen Akt ein (meist um Szene 10). Das Toolkit löst `generate_boss()` an
   diesen Punkten automatisch aus.

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
- **Setup-Option:** Für lokale Installationen steht
  [`scripts/setup-openwebui.sh`](scripts/setup-openwebui.sh) als Hilfsskript bereit
  (provider-neutral mit expliziter Modellwahl; Sonnet als empfohlener Default).
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
