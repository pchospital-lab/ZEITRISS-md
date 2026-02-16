---
title: "ZEITRISS Einführung, Verteilung & Hosting"
version: 0.1.0
tags: [meta]
---

# ZEITRISS – Einführung, Verteilung & Hosting (intern)

Hinweis: Strategiepapier für Maintainer:innen, Partner und interessierte
Endanwender:innen. Nicht in den Wissensspeicher laden.

## Ziel & Rahmen

ZEITRISS wird als privatsphärefreundliches KI-Rollenspiel vertrieben. Der
Schwerpunkt liegt auf lokalem Betrieb – sämtliche Spielinhalte und Regeln
laufen entweder auf der Hardware der Endnutzer:innen oder in Ende-zu-Ende-
verschlüsselten Umgebungen. Das System ist als Solo-Betrieb konzipiert: eine
zentrale Wissensbasis (Regelwerk + Module), ein KI-Spielleiter-Prompt und ein
einheitlicher Entwicklungsstand, der auf verschiedene Plattformen gespiegelt
werden kann.

Die perfekte Verbindung von Pen-&-Paper und Computerspiel: ZEITRISS vereint
kreative Freiheit klassischer Tischrollenspiele mit den Annehmlichkeiten
vollständig digitaler Systeme. Die Grenze „Spielbuch vs. Game Engine“ entfällt
– die KI generiert flexibel Geschichten, während sie zuverlässig Regeln
anwendet. Dieses Alleinstellungsmerkmal soll in Verteilung und Vermarktung
hervorgehoben werden.

## Einfacher Solo-Betrieb (One-Build-Strategie)

- **Ein Regelwerk, überall identisch:** Das Repository (insbesondere das
  Spieler-Handbuch und die Runtime-Module in `characters/`, `core/`, `gameplay/`,
  `systems/`) bildet die einzige Quellenbasis.
- **Einmal ändern, überall spiegeln:** Änderungen am Regelwerk oder an
  Mechaniken werden einmalig im Repo durchgeführt und anschließend auf allen
  Zielplattformen (ChatGPT-Instanz, Proton LUMO, lokale Runner)
  synchronisiert. Es gibt keine parallelen Varianten des Spiels.
- **Plattform-Overhead minimieren:** Anstatt eine eigene App oder Server-
  Infrastruktur zu entwickeln, nutzt ZEITRISS bestehende Tools. LM Studio oder
  ähnliche lokale LLM-Umgebungen dienen als „Game-Engine“, Proton LUMO oder
  Custom-GPT-Umgebungen als Alternativen. Updates werden durch das Teilen der
  Wissensbasis realisiert, nicht durch App-Patches.
- **Geschützter Betrieb:** Wo immer möglich, bleibt das Spiel offline oder
  Ende-zu-Ende-verschlüsselt. Die Spielerfahrung findet im privaten Rahmen
  statt – ähnlich wie eine Pen-&-Paper-Runde im Wohnzimmer, nur digital
  unterstützt. Online-Features (wie eine zentrale Lobby oder Cloud-Speicher)
  sind derzeit nicht vorgesehen, um Datenschutz und Unabhängigkeit zu
  gewährleisten.

## Wartung & Weiterentwicklung mit KI-Unterstützung

- **Codex-Workflow:** Entwicklungsänderungen werden konsequent mit
  KI-Unterstützung (GitHub Copilot, Codex Repo-Agent) umgesetzt. Nach jedem
  Commit laufen automatische Checks: Formatierung (`npm run fmt`), Link- und
  Konsistenzprüfungen (`npm run check`), ggf. Markdown-Linting und
  Schema-Validierung. Ergebnisse und Auffälligkeiten hält der Maintainer im
  QA-Journal fest (`internal/qa/logs/...`).
- **QA-Fahrplan & Tests:** Ein priorisierter Maßnahmenplan (siehe
  `internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md`) definiert anstehende
  Verbesserungen und Bugfixes. KI-gestützte Playtests (Beta-GPT in MyGPT)
  prüfen neue Builds autonom – inklusive vollständiger Durchläufe mit Issue-
  und Lösungsvorschlag-Blöcken. Jede erkannte Schwachstelle wird vom Repo-
  Agenten in Code oder Regeltext übertragen und im Fahrplan abgehakt.
- **Automatisierte Reviews:** Vor einem Release laufen automatisierte
  Prüfungen, z. B. Abgleich der Save/Load-Funktion gegen das JSON-Schema,
  PII-Scans (stellen sicher, dass keine personenbezogenen Entwicklerdaten im
  Repo landen) und Markdown-Linkchecks.
- **Kontinuierliche Dokumentation:** Alle Entwicklungsfortschritte – ob
  Regeländerungen, neue Features (z. B. „Whisper-Voice-Input“) oder gefundene
  Bugs – werden in internen Dokumenten nachverfolgt. QA-Journal und Changelog
  geben nachvollziehbar Auskunft, welcher Stand auf welche Plattform
  ausgerollt wurde und welche Änderungen eingeflossen sind.

## Privatsphäre & Datenhandhabung

- **Lokal und verschlüsselt als Standard:** ZEITRISS benötigt keine
  Serververbindung. Spielrunden können vollständig offline stattfinden. Wenn
  Cloud-Dienste genutzt werden (z. B. Proton LUMO), ist die Verbindung
  Ende-zu-Ende-verschlüsselt, sodass keine Drittanbieter Einblick in die
  Kommunikation haben.
- **Keine Telemetrie, keine Datensammelei:** Weder die Spiel-Engine (LLM) noch
  das Regelwerk enthalten Telemetrie-Code. Es werden keine Spielerdaten heimlich
  erfasst. Alles, was das System „lernt“, geschieht offen im Chat (z. B.
  Charakterbögen in JSON-Form) und verbleibt bei den Nutzer:innen.
- **Datensparsamkeit bei Exporten:** Spieler:innen können ihren Spielstand
  (Memory JSON) exportieren. Empfohlen wird, Exporte lokal und sicher
  aufzubewahren (bei sensiblen Inhalten ggf. verschlüsselt). Chats auf
  geteilten Plattform-Accounts (z. B. Firmenkonten) sollten nach Abschluss
  einer Kampagne gelöscht oder archiviert und dann gelöscht werden.
- **Hinweise für Nutzer:innen:** In Benutzeranleitungen oder Hilfetexten wird
  klargestellt, dass öffentliche/ungeschützte Plattformen tabu sind, wenn reale
  persönliche Informationen ins Spiel kommen. ZEITRISS selbst benötigt keine
  echten persönlichen Daten der Spieler:innen – falls Nutzer:innen dennoch
  eigene Namen oder biografische Details einbringen, geschieht dies auf eigene
  Verantwortung innerhalb der privaten Session.

## Verteilung über GitHub (Self-Service)

- **GitHub als Primärkanal:** Das komplette ZEITRISS-Regelwerk wird öffentlich
  über GitHub bereitgestellt (Repository `ZEITRISS-md`). Interessierte können
  das Repository klonen oder ein Release-ZIP herunterladen. Damit stehen alle
  Dateien zur Verfügung, um ZEITRISS auf der Plattform ihrer Wahl auszuführen.
- **Trademarks & Sichtbarkeit:** Die Veröffentlichung erfolgt erst, nachdem der
  Markeneintrag bestätigt wurde (bereits erfolgt, Markenhinweis im README).
  Das Repo kann öffentlich bleiben, da die CC BY-NC-Lizenz die Inhalte schützt
  (kommerzielle Interessen wenden sich ohnehin direkt an uns wegen
  Lizenzierung).
- **Import-Schritte (Kurzfassung):** Für gängige Umgebungen werden kurze
  Importanleitungen bereitgestellt:
  - **OpenAI GPT (MyGPT/Store):** Custom-GPT anlegen,
    `meta/masterprompt_v6.md` vollständig ins Systemprompt-Feld kopieren.
    Danach `core/spieler-handbuch.md` und alle 19 Runtime-Module in den
    Wissensspeicher hochladen (Details in `docs/maintainer-ops.md`).
  - **Proton LUMO:** Neuen verschlüsselten Chat starten,
    `meta/masterprompt_v6.md` als erste Nachricht einfügen. Anschließend
    Spieler-Handbuch und Module via Büroklammer hochladen und dem
    Wissensspeicher hinzufügen.
  - **Lokale Runner (LM Studio, Ollama, Oobabooga etc.):** Lokales Modell
    (mind. 20B Parameter empfohlen) laden. Inhalt von
    `meta/masterprompt_v6.md` als System-/Instruktionsprompt einsetzen.
    Alle Markdown-Module sowie `core/spieler-handbuch.md` in das Wissenssystem importieren
    (via UI oder Scripts). Danach kann die Sitzung im Chat starten.
  - **Sprach-Plugin (optional):** Für maximale Immersion kann ein
    Whisper-basiertes Speech-to-Text-Plugin eingesetzt werden. Ausgabe via
    Text-to-Speech ist ebenfalls denkbar. Plugins sind nicht Teil des Repos,
    können aber von der Community integriert werden.
- **Self-Service-Dokumentation:** Eine ausführlichere Schritt-für-Schritt-
  Anleitung (mit Screenshots ggf.) kann auf der Projekt-Website oder im Wiki
  verlinkt werden, damit auch nicht-technische Nutzer:innen ZEITRISS einrichten
  können. Wichtig ist, den Importpfad klar und einfach zu halten – idealerweise
  in weniger als 5 Minuten vom Download bis zum spielbereiten Setup.

## Hosting-Strategie

- **Dezentraler Betrieb:** ZEITRISS bleibt einem dezentralen Modell treu. Jede
  Spielrunde läuft in der Umgebung der Nutzer:innen (lokal oder im eigenen
  geschützten Account). Dies reduziert laufende Betriebskosten und vermeidet
  Haftungsfragen durch Serverbetrieb (insbesondere wegen der 18+-Inhalte).
- **Kein öffentlicher Zentral-Server:** Aktuell ist kein offizieller Online-
  Server oder Matchmaking-Dienst geplant. Hosting großer Sprachmodelle wäre
  kostenintensiv, zudem steht die DIY-Philosophie im Vordergrund.
- **Option bei Partner-Hosting:** Sollte in Zukunft große Nachfrage entstehen
  oder ein Partner (z. B. Cloud-Anbieter) einen ZEITRISS-Server anbieten,
  wird das sorgfältig geprüft. Backups, Ausfallsicherheit und Moderation
  müssen dann klar geregelt sein. Bis dahin gilt „Bring your own hardware“.
- **Skalierung durch Community:** Da das Projekt Open-Source-Komponenten nutzt,
  kann die Community eigene Server oder Bots erstellen. Dies geschieht jedoch
  außerhalb des offiziellen Angebots. Zentral gehostete inoffizielle Angebote
  bleiben im Blick, v. a. wegen Lizenz- und Markennutzung.

## Lizenz & Monetarisierung

Das Lizenzmodell für kommerzielle Nutzer (z. B. Firmen/Plattformen) ist in
`docs/zeitriss-lizenzmodell-notizen.md` beschrieben. Alle Preisangaben und
Lizenzdetails bleiben außerhalb des Wissensspeichers und der Endnutzer-
Dokumentation, um das Spielerlebnis nicht mit Geschäftsmodalitäten zu
vermischen.

In der öffentlichen Kommunikation wird lediglich erwähnt: „ZEITRISS® –
kostenlos für private Nutzung, Lizenz für kommerzielle Nutzung erforderlich“.
Interessenten erhalten auf Anfrage transparente Informationen (basierend auf
internen Notizen).

## Plattformabhängigkeiten & Alternativen ohne Telemetrie

- **Primärplattform:** Empfohlen ist der lokale Betrieb mit LM Studio (oder
  vergleichbarer Frontend) in Verbindung mit einem leistungsfähigen KI-Modell.
  Für optimale Ergebnisse wird derzeit ein Modell der Größenordnung 20B
  Parameter genutzt (z. B. Llama-2-Chat-13B/70B je nach Hardware).
- **OpenAI API/Store:** Für Test- und QA-Zwecke läuft ZEITRISS in einer
  OpenAI-MyGPT-Instanz (GPT-4-basiert). Dies ist eher für Entwicklung gedacht,
  da die Inhalte dort nicht E2EE sind. Produktiv bleibt die Nutzung der
  OpenAI-Plattform optional und erfordert Vorsicht (keine echten persönlichen
  Daten im Spiel, Beachtung der OpenAI-Nutzungsbedingungen).
- **Self-Hosted Git:** Falls gewünscht, kann das Repository statt über GitHub
  auch über eine eigene Gitea/Forgejo-Instanz gespiegelt werden, um Telemetrie
  zu vermeiden. Unternehmen oder fortgeschrittene Nutzer können so
  sicherstellen, dass keine Metadaten an öffentliche Dienste gehen.
- **Dateiaustausch:** Neben GitHub sind alternative Bezugsquellen möglich,
  z. B. ein Download über Nextcloud, Tresorit oder Proton Drive. Diese können
  eingesetzt werden, um geschlossene Wissenspakete für Partner bereitzustellen
  (z. B. ZIP mit allen benötigten Dateien), falls direkte GitHub-Nutzung nicht
  erwünscht ist.
- **Lokale UIs:** Nutzer:innen, die kein LM Studio verwenden möchten, können
  andere UI-Frontends einsetzen. Erfolgreich getestet wurden z. B.
  Oobabooga Text UI oder OpenWebUI in Verbindung mit lokalem LLM-Backend.
- **Sprachein- und -ausgabe:** Für vollkommen telemetriefreie Immersion
  empfehlen sich lokale Sprach-Tools: Whisper offline zur Spracherkennung
  sowie Open-Source-TTS-Systeme (z. B. Coqui TTS) für Sprachausgabe. So bleibt
  auch die Audio-Ein-/Ausgabe des Spiels unter der Kontrolle der Nutzer:innen.
- **Hardware-Unabhängigkeit:** ZEITRISS ist an keine bestimmte Hardware
  gebunden. Es läuft auf gängigen PCs mit entsprechender GPU (für große
  Modelle) oder sogar CPU-only mit performance-schonenden Einstellungen.
  AMD- und NVIDIA-GPUs werden gleichermaßen unterstützt, insbesondere da
  keine proprietären Frameworks nötig sind – der Einsatz erfolgt über
  standardisierte KI-Modelle und Open-Source-Runtimes.

## Compliance-Hinweise

- **Kein echtes Zeitreise-Tool:** ZEITRISS ist fiktional. Ähnlichkeiten mit
  realen historischen Ereignissen dienen nur dem Spielspaß. Das System erhebt
  keinen Anspruch auf historische Genauigkeit und bietet keinerlei realen
  Beratungswert.
- **Altersfreigabe 18+:** Das Spiel richtet sich ausschließlich an Erwachsene.
  Gewalt, Entscheidungen über Leben und Tod und andere reife Themen sind Teil
  der Narrative. Dies wird in allen Nutzerinformationen deutlich
  kommuniziert (bereits im README und Lizenztext verankert).
- **Verantwortung bei Nutzung:** Weder der Entwickler noch eventuelle
  Lizenzpartner übernehmen Haftung für Handlungen der Nutzer:innen, die aus
  dem Spiel heraus inspiriert werden. Alle Anweisungen des KI-Spielleiters
  sind als Teil der Simulation zu verstehen.
- **Keine Notfallhilfe:** ZEITRISS ist nicht dafür vorgesehen, echte Probleme
  zu lösen oder Notfälle zu bewältigen. Es soll nicht zweckentfremdet werden,
  um Ratschläge in kritischen Lebenslagen, medizinische Auskünfte oder
  rechtliche Einschätzungen einzuholen.
