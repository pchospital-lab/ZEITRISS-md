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

## Das Besondere: Dein Save IST dein Charakter

ZEITRISS läuft im Chat, aber dein Fortschritt hängt nicht an einem
Server-Account. Dein Charakter liegt als JSON-Speicherstand vor — wie ein
Characterdatenblatt beim klassischen Pen & Paper.

- **Mitnehmbar:** Du kannst denselben Charakter bei jeder KI-Spielleitung laden.
- **Teilbar:** Gruppen splitten nach der Episode, spielen Rifts getrennt und
  mergen danach — mit transparentem Merge-Protokoll.
- **Besitz bei dir:** Dein Save, dein Charakter. Kein Account, kein Lock-in.

Kurz: ZEITRISS ist Drop-in/Drop-out-Multiplayer mit echtem Charakter-Besitz.

## In 5 Minuten starten

### Standardpfad (empfohlen): Script-Setup in OpenWebUI

1. **Einmalig vorbereiten:** OpenWebUI installieren und OpenRouter-Konto
   erstellen, Provider verbinden und in OpenWebUI einen API-Key anlegen.
2. **Aktuellen Repo-Stand holen:**
   - per Git: `git clone ...` (danach vor Sessions `git pull`), oder
   - per GitHub-Download (ZIP), entpacken und in den Projektordner wechseln.
3. **Setup-Script ausführen:** `./scripts/setup-openwebui.sh`
   (legt Preset + Wissensspeicher an und synchronisiert den aktuellen Stand).
4. **Vor dem Spiel kurz prüfen:**
   - Masterprompt ist im Systemfeld gesetzt,
   - Wissensspeicher ist sauber verknüpft (20 Slots),
   - dann mit `Spiel starten (solo klassisch)` starten.

**Falls die Plattform kein eigenes Systemfeld anbietet:**
`meta/masterprompt_v6.md` als **erste Chatnachricht** senden und erst danach
`Spiel starten (solo klassisch)` nutzen; Load startet auch direkt über eingefügten Save-JSON (optional mit `Spiel laden`).

**Session-Update-Standard:** Vor jeder Runde neuesten Repo-Stand laden und das
Setup-Script erneut starten. Bei laufendem OpenWebUI aktualisiert das den
ZEITRISS-Stand im üblichen Workflow.

### Manuelle Alternative (wenn ohne Script gearbeitet wird)

- 20 Wissensmodule laden (`core/spieler-handbuch.md` + 19 Runtime-Module).
- `meta/masterprompt_v6.md` nur als Systemprompt setzen (nicht als Wissensdatei).
- **Parameter setzen:** Temperature `0.8` · Top-P `0.9` · Frequency Penalty `0.3` · Max Tokens `64000`.
- Verknüpfung nach jeder Änderung prüfen (Slots + Preset).
- Details: [Setup-Guide → Manuelles Setup](docs/setup-guide.md#wissensspeicher--plattform-setup).

_(Kurzmodus bleibt möglich: `Spiel starten (solo schnell)`.)_

### Modell-Empfehlung

> **Stand März 2026:** Derzeit ist `anthropic/claude-sonnet-4.6` das einzige Modell,
> das das ZEITRISS-Regelwerk zuverlässig umsetzt — korrekte Würfelmechanik
> (W6+Attr/2+Talent, Exploding), saubere HUD-Struktur, vollständige Score-Screens
> und regelgetreue Px/CU-Berechnung. Andere Modelle erzählen atmosphärisch gut,
> erfinden aber eigene Regelsysteme statt dem Spieler-Handbuch zu folgen.

- **Empfohlen:** `anthropic/claude-sonnet-4.6`
  (~$3/$15 pro 1M Token · 128K Output). Einziges Modell mit vollständiger
  Regeltreue — HUD, Würfelproben, Score-Screen, Px-Staffel, Interface-Contract.
  Stärkster Noir-Ton, flüssiges Deutsch, sauberste Spielerfahrung.
- **Budget-Alternative:** `deepseek/deepseek-v3.2`
  (~$0.25/$0.40 · 65K Output). Gute Noir-Atmosphäre, korrekte HUD-Formate,
  sehr günstig ($0.002 pro Turn). Würfelmechanik weicht teilweise ab —
  spielbar, aber nicht regelgetreu. Für wen die Atmosphäre wichtiger ist als
  exakte Proben.
- **Experimentell:** `z-ai/glm-4.6`
  (~$0.40/$1.71 · 131K Output). Starke Atmosphäre zum Niedrigpreis.
  Erfindet eigene Regeln — nur für Spieler geeignet, die den Noir-Ton
  genießen und über Regelabweichungen hinwegsehen.

→ [Paradoxon-Index](systems/gameflow/speicher-fortsetzung.md#paradoxon-index)
→ [Immersives Laden](systems/gameflow/speicher-fortsetzung.md#immersives-laden)
→ [Makros im Überblick](systems/gameflow/speicher-fortsetzung.md#makros-im-ueberblick)

## TL;DR - ZEITRISS in 6 Punkten

1. **Agenten.** Als Chrononauten deckt ihr Zeitverschwörungen auf.
2. **Missionsphasen.** Eine **Mission** läuft über Briefing → Infiltration →
   Intel/Konflikt → Exfiltration → Debrief und umfasst meist zwölf Szenen.
   Eine **Episode** bündelt rund zehn Missionen derselben Epoche; Rift-Ops
   sind Sondermissionen in vier Stages mit vierzehn Szenen.
3. **Explodierende Würfel.** W6, ab Attribut 11 W10; Heldenwürfel erst ab 14.
4. **Paradoxon-Index (Px)** misst eure temporale Resonanz — ein **Belohnungssystem**.
   Je nach TEMP steigt Px pro Mission (niedrig = langsam, hoch = schnell). Bei Px 5
   enthüllt `ClusterCreate()` 1-2 Rift-Seeds auf der Raumzeitkarte — Bonus-Missionen
   mit Paramonstern und Artefakten. Danach Reset auf 0. Rift-Ops werden zwischen
   Episoden gespielt — Seeds können akkumulieren für mehr Loot und höheren
   Schwierigkeitsgrad.
5. **Klassik als Default.** Mischform aus filmischen und taktischen Regeln;
   Schnellstart ist ein optionaler Zugriffspfad für den schnellen Eindruck,
   ändert aber keine Kernregeln.
6. **Boss-Rhythmus.** In der **5. Mission einer Episode** erscheint ein
   Mini-Boss, in der **10. Mission** der Episoden-Boss. Rift-Operationen
   führen ihren Endgegner im finalen Akt ein (meist um Szene 10). Das Toolkit
   löst `generate_boss()` an diesen Punkten automatisch aus.

→ Das vollständige **[Spieler-Handbuch](core/spieler-handbuch.md)** enthält
Einleitung, Lore, Schnellstart-Spickzettel, Mini-Einsatzhandbuch, FAQ, Glossar
und die Runtime-Referenz.

### Normsprache für Module (SSOT-Anker)

- **MUSS:** bindende Invarianten wie Boss-Timing, SaveGuard (HQ-only),
  Px-5-`ClusterCreate()` und die einheitliche CU-Formel.
- **SOLL:** empfohlener Standardpfad ohne harte Sperre (klassischer Start,
  neuer Chat pro Mission).
- **KANN:** optionale Komfort- oder Darstellungsvarianten ohne Regeländerung
  (z. B. Schnellstart/Film-Modus).

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
  (provider-neutral mit expliziter Modellwahl; DeepSeek V3 als empfohlener
  Preis-Leistungs-Default).
- **Multiplayer-Hinweis:** Lokal oder online mit Gruppe möglich; Save-Stand und
  Chatlog können zwischen Sessions geteilt werden.
- **Betriebshinweis:** Es gibt keine zugesicherte Verfügbarkeit, keinen
  individuellen Endnutzer-Support und keine SLA für private Nutzung (Details in
  [LICENSE](LICENSE)).
- **GitHub-GUI-Feinschliff:** Eine kurze Maintainer-Checkliste für finale
  Public-Settings liegt unter
  [`docs/github-public-checkliste.md`](docs/github-public-checkliste.md).

## Multiplayer ohne Server: Bring-Your-Character

- Eine Person hostet den Chat (lokal oder online per Stream/Screenshare).
- Im HQ speichert ihr mit `!save` — der JSON enthält alle Charaktere.
- `!bogen` zeigt den aktuellen Charakterbogen als lesbare Übersicht (kein JSON-Export).
- **Kanonischer Split:** Split/Merge ist standardmäßig nur **nach Episodenende**
  für getrennte Rift-Ops vorgesehen (z.B. 3er + 2er in separaten Chatfenstern).
- **Kanonischer Merge:** Nach abgeschlossenen Rifts werden die HQ-Saves wieder
  zusammengeführt — transparentes Protokoll zeigt, wie CU, Seeds und Px
  konsolidiert wurden.
- **Nicht-kanonisch ohne Branch-Protokoll:** Parallele Core-Missions-Branches
  innerhalb derselben Episode sowie Misch-Splits (Rift/PvP/Chronopolis)
  gelten als Hausregel und dürfen nicht stillschweigend als kanonischer
  Kampagnenfortschritt übernommen werden.
- **Klarfall 5er→3/2 mitten in der Episode:** Beide Gruppen können legitim
  weiterspielen. Für jede Runde ist immer der eigene aktuelle Host-Save der
  Hauptfortschritt. Erst wenn später gemerged wird, zählt fremder Verlauf als
  Import (Charakterdaten/Wallet/Loadout statt Kampagnenfortschritt).
- **Hopper-Betrieb (OpenWebUI-Realität):** Wer nach jeder Mission Hosts
  wechselt, spielt im Lobby-Modell. Einfachregel: Pro Chat gilt genau ein
  Host-Kanon; mitgebrachte Saves ergänzen Charakterdaten, nicht automatisch
  Episode/Mission/Px aus anderen Linien.
- **Leaver/Rejoin im HQ:** Leaver können nach jeder Mission im HQ einsteigen,
  wenn sie den aktuellen Host-Stand laden. Sie setzen keine neue Episode frei,
  sondern übernehmen den Missionsstand des Hosts.
- Danach kann jede Person den Gruppenstand weiter nutzen oder einen eigenen
  Solo-Stand daraus starten.

Damit bleibt der Koop-Loop einfach: spielen, speichern, splitten, Rifts
getrennt erleben, mergen, nächste Episode.

> **Wichtig für OpenWebUI / reinen Chatbetrieb:** Der harte Standard ist `!save` im HQ (JSON-Export) und Laden per JSON-Copy-Paste. `Spiel laden` ist optional; ein eingefügter Save-JSON reicht als Startsignal für den Load-Flow.

**Betriebsstandard (chat-only):** ZEITRISS läuft im Spielbetrieb über den HQ-DeepSave (`!save`) und JSON-Copy-Paste; `Spiel laden` bleibt optionales Startsignal. Zusätzliche Snapshot-/AutoSave-Befehle sind nicht Teil des kanonischen Spielpfads.

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
- [Level & XP-Kurve](core/sl-referenz.md#level--ep-kurve)
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

© 2025-2026 pchospital – ZEITRISS® – private use only. See LICENSE.
