# Produktplan — Figurenreise am Tisch

Stand: 2. November 2026. Diese Datei ist die **einzige** Planstelle für den
Produktpfad „Figurenreise am Tisch". Sie beschreibt einen zusammenhängenden,
rein terminalbasierten Weg: Ein Mensch bietet an seinem Gerät einen Tisch an
oder sucht einen, eine Anfrage wird vom Host entschieden, es wird gespielt, der
Abschnitt schließt, der Gast geht (oder der Host spielt allein weiter), und der
Gast kehrt später mit seiner **selbst** fortgeschrittenen Figur zurück. Die
Figur reist dabei real über Export/Import zwischen zwei getrennten Datenwurzeln
A → B → A. Ein paralleler Fahrplan wird hier bewusst nicht geführt; eine native
LAN-/Netz-Lobby bleibt getrennt und ist unter „Betreiber-, Misch- und Netzbetrieb"
abgegrenzt und ausdrücklich als noch nicht geliefert gekennzeichnet.

## Zwei-Wurzel-Modell (A → B → A)

- **Wurzel A — Gastgerät, ohne Hoststack.** Der Gast besitzt den Terminal-Client
  und seine eigenen JSON-Dateien, aber keinen eigenen Spielleitungs-/Persona-
  Stack. Ohne Spielleitungsanbindung kann A **keine Figur eigenständig
  erschaffen** — der Erschaffungsdialog läuft über denselben GM-Transport wie
  das Spiel und bleibt ohne ihn ein ehrlicher Teilstand. A nutzt eine bereits
  host-/stackgestützt angelegte Figur und exportiert bzw. importiert sie von
  dort nur noch. Die vom Betreiber freigegebene, hostgestützte Gast-Erschaffung
  ohne fertiges JSON ist mit R2 geliefert (siehe „Geliefert in R2 (Betreiber-
  Etappe)").
- **Wurzel B — Hostgerät, voller Stack.** Der Host betreibt Spielleitung und
  eigene Personas. Nur auf B wird ein Tisch tatsächlich gespielt.
- **Die Figur ist das Reisegut, nicht der Spieler.** Der admittierte Gast spielt
  **auf B** mit; seine Figur gelangt als exportierte Datei von A nach B und der
  fortgeschrittene Stand als Datei zurück nach A. Es wandert kein Hoststack, kein
  Persona-Gedächtnis und keine fremde Konfiguration mit.

## Geliefert (jetzt im Produkt)

Der Weg steht aus einem host-autoritativen Pre-Start-Dienst, einer expliziten
Fähigkeitsgrenze, dem toleranten Fremdimport und der Verdrahtung zum
unveränderten Spielpfad. Die bestehenden Spiel-, Speicher- und Importpfade
bleiben unverändert; der Nachzug ergänzt sie chirurgisch.

- **Host-autoritativer Pre-Start-Dienst** (`mmo_sim/core/table_admission.py`).
  Trennt die Hostautorität sauber von der bisherigen, erst im Spielpfad aus der
  ersten voll angenommenen Offer abgeleiteten Leiterrolle. Persistente, neustart-
  feste Zustandsübergänge laufen ausschließlich über diesen einen gemeinsamen
  Dienst: anbieten, suchen, anfragen, zurückziehen, annehmen, ablehnen,
  entfernen, verlassen, Roster lesen, starten, **einen gestarteten Abschnitt
  zurückbinden und nach echtem Abschluss schließen**. Host-only-Übergänge
  (annehmen/ablehnen/entfernen/anbieten/starten/binden/schließen) prüfen die
  Hostidentität gegen den **persistierten** Datensatz.
  - **Lokale Angebotssuche** (`list_open_tables`, Kommando `tisch-suchen`). Ein
    brandneuer Gast kann alle lokal offenen Angebote lesen, **ohne vorher einen
    `table_key` zu kennen** oder schon im Datensatz zu stehen. Reine Lesefunktion
    mit derselben lokalen Lesefreigabe wie der Rosterblick; keine Schreibzugriffe,
    kein Modellaufruf.
  - **Bindung der echten Abschnittskennung** (`bind_section`). Nach `tisch-start`
    wird die vom Spielpfad tatsächlich zurückgegebene Abschnittskennung
    (`table.table_id`) in den Admissionsdatensatz zurückgebunden. Ist der
    zugehörige Store-Tisch danach real `status="closed"`, schließt `close_table`
    auch den Admissionsdatensatz. Ein erneuter `tisch-start` auf denselben
    `table_key` trifft dann ehrlich auf „geschlossen — neues Angebot nötig",
    statt blind idempotent denselben `started`-Zustand weiterzutragen.
- **Explizite Fähigkeitsgrenze** (`host_capable`, Durchsetzung in
  `mmo_sim/ui/tui.py`). Der Gastmodus ist ein ausdrücklicher Einsatzentscheid des
  Starters, nicht aus der bloßen Anwesenheit einer (ohnehin trägen) Factory
  abgeleitet. Ein Gast kann lokale Angebote **suchen**, anfragen, zurückziehen,
  nach Hostannahme beitreten, mitspielen, verlassen und seine eigene Figur
  exportieren/importieren. Ein Gast kann **nicht** solo spielen, Tische anbieten,
  eigene Personas/Einladungen fahren oder annehmen/ablehnen/entfernen/starten.
  Das Gate greift am Methodeneintritt. Der Soloweg `_cmd_local_round` prüft die
  Hostfähigkeit jetzt als **allererste** Anweisung — vor jedem Laufumgebungscheck
  und vor `create_table_from_offer_log`, das Figuren sperrt und einen Tisch
  persistiert. Ein abgewiesener Gaststart hinterlässt dadurch **keinen** Lock und
  **keinen** Tischfortschritt. Kein Modell wird nur zur Tischsuche hochgefahren.
- **Hostpersona-Autorität** (`tisch-anfragen-persona`, Persona-Treiber in
  `tisch-start`). Eine eigene bestätigte Hostpersona kann als Teilnehmerin
  angefragt werden; die Hostentscheidung bleibt ein **getrennter** Vorgang. Beim
  Start wird ein Rostermitglied nur dann als menschliches Token behandelt, wenn
  es **nicht** zum eigenen bestätigten Personabestand gehört — eine eigene
  Persona wird tatsächlich als Persona getrieben, nicht pauschal zum Menschen
  erklärt. Eine fremde oder unbekannte Persona-ID wird vor jeder Admissions-
  mutation abgewiesen (kein Schreibzugriff, kein Modellaufruf).
- **Toleranter Fremdimport** (`mmo_sim/domain/zeitriss/import_export.py`,
  `preview_import_tolerant`). Eine regulär exportierte, legitim tolerierte
  Best-Effort-Figur passiert den Importweg mit **sichtbar** mitgeführter
  Restwarnung und erst nach ausdrücklicher, benannter Nutzerbestätigung. Es gibt
  **keine** pauschale Schema-Lockerung: Beide v7-Schemas bleiben bytegleich, ein
  unvollständiger SAVECOMPAT-Umschlag bleibt von einem abgeschlossenen tolerierten
  Stand unterschieden, und eine harte Identitäts-/Bindungs-/Konfliktverletzung
  wird **nicht** als harmlose Warnung durchgereicht.
- **Fremdzuordnungs-Konflikt am Import** (`catalog.find_registration` im
  Importweg). Eine Char-ID, die bereits bei einem **anderen** Teilnehmer
  registriert ist, wird vor jedem Zielwrite erkannt und der Import geparkt — auch
  **ohne** aktiven Tischlock. Die bereits vorhandene teilnehmerübergreifende
  Lesefunktion wird dafür einmalig, vor dem Schreiben, konsultiert; es entsteht
  keine zweite widersprechende Prüfung und keine neue Schreibsemantik. Eine
  wirklich neue, nirgends registrierte ID bleibt eine neue Figur.
- **Verdrahtung zum spielbaren Strang** (`mmo_sim/ui/tui.py`). Die Tisch-
  Lebenszyklus-Kommandos hängen am bestehenden Dispatch; `tisch-start` friert das
  Roster ein und übergibt es an den **unveränderten** Spielpfad
  (`create_table_from_offer_log` + `run_play_session`). Der Statuskopf zeigt
  Modus und Roster/Anfragen der eigenen Tische rein lesend.

### Rückreise und Konfliktverhalten

Der Re-Import nach A läuft über das unveränderte `resolve_import`. Die gleiche
Char-ID mit extern fortgeschrittenen Bytes ersetzt — nur bei ausdrücklicher Wahl
— genau die vorige aktive Gastkopie; der alte Stand darf Historie bleiben, gewinnt
aber nicht als `current`. Ein identischer Re-Import ist idempotent
(`noop_identical`), eine andere Char-ID ist eine andere Figur (`register_new`).
Bei aktiver Tischbindung oder offenem Abschluss wird der Eingang geparkt; ohne
ausdrückliche Konfliktwahl wird nicht automatisch hochgelevelt oder gemischt.
Unbeteiligte Host-/Heimatfiguren, inaktive Figuren, Persona-Erinnerungen und
fremde Konfiguration werden nicht überschrieben.

### Ehrliche Grenze beim Verlassen während eines offenen Abschnitts

Verlässt ein Gast den Tisch (oder entfernt der Host ihn), während der gebundene
Store-Tisch real **noch offen** ist, bucht der Admissionsdienst die Roster-
änderung wie bisher — und die Oberfläche zeigt zusätzlich **ehrlich** an, dass
diese Admissionsbuchung die Bindung am eigentlichen Spielkern **nicht** löst und
**keinen** Spielstand verwirft oder zurückrollt. Der sichere, kontrollierte Weg
bleibt der **bestehende** `/pause` am Spielzug-Prompt beziehungsweise ein
regulärer Debrief/Abschluss; zusätzlich steht seit R2 der **kontrollierte
Betreiber-Stop** und der **echte, nicht-destruktive Abbruch** vor der
Abschlussentscheidung (siehe „Geliefert in R2 (Betreiber-Etappe)"). Die bloße
Admissionsbuchung beim Verlassen/Entfernen rollt für sich genommen weiterhin
nichts zurück.

### Nachweislage (J1–J8, ursprüngliche Langnamen)

Die acht Akzeptanzpunkte tragen ihre **ursprünglichen** Bedeutungen aus dem
Figurenreise-Auftrag. Sie sind mit echten Ergebnis-Bytes über die realen
Produkt-/Terminalpfade des gemeinsamen Spielkerns belegt: deterministische Unit-
und Integrationstests am Modellrand sowie ein persistenter Evidenzlauf, dessen
prozessübergreifende Grenzen jeweils ein **echter neuer `python3`-Interpreter**
sind (`subprocess`, kein zweites Objekt im selben Prozess). Die gemessenen Hashes
und äußeren Läufe am finalen Produktanker liegen in der Rückgabe
(`EVIDENCE-MAP.md`, `REWORK.json`); boolesche Altzusammenfassungen gelten nicht
als neue Spielbeweise.

- **J1_TABLE_LIFECYCLE — Tisch-Lebenszyklus.** Anbieten, Suchen ohne
  `table_key`-Vorwissen, Anfragen, Hostannahme, Start, Spiel bis zum real
  geschlossenen Abschnitt, Rückbindung der echten Abschnittskennung und Schließen
  des Admissionsdatensatzes. Angebot/Anfrage/Annahme ergeben real Roster
  `[host, guest]`; die gestartete Abschnittskennung wird gebunden und nach
  `status="closed"` auch im Admissionsdatensatz als geschlossen geführt.
- **J2_SOLO_GROUP_SOLO — Solo, Gruppe, Solo.** Der Host kann solo starten, eine
  Gruppe bilden und nach dem Abschnitt wieder allein weiterspielen; `leave_table`
  entfernt nur den Gast. Der Gast erreicht den Soloweg nicht: die frühe
  Hostgrenze greift **vor** Lock und Tisch-Persistierung, ein abgewiesener
  Gaststart hinterlässt keinen Lock und keinen Fortschritt (mit Vorher/Nachher-
  Bytes belegt).
- **J3_HOST_PERSONA_AUTHORITY — Hostpersona-Autorität.** Eine eigene bestätigte
  Hostpersona wird als Persona getrieben, nicht als Mensch; die Hostentscheidung
  bleibt getrennt; eine fremde/unbekannte Persona-ID wird vor jeder Mutation
  abgewiesen, ohne Spielleitungs-/Persona-Factory aufzurufen.
- **J4_FOREIGN_JOURNEY_VALID_AND_TOLERATED — fremde Reise, gültig und
  toleriert.** Ein **regulär gültiger** A→B→A-Lauf (Export aus A, Annahme/Spiel/
  Abschluss/Export auf B, Wiederannahme in A durch einen frischen Prozess; Level
  real 2 → 3) und ein **tolerierter** Warnungsstand (unveränderter Cap-Überlauf-
  Stand aus dem Originalauftrag) als getrennter Fall: Letzterer wird über den
  **echten Produktweg** importiert — mit sichtbar mitgeführter Restwarnung und
  ausdrücklicher namentlicher Bestätigung — und dann an einer **tatsächlich
  bereitgestellten Spielleitung** (einem eigenen eingerichteten Hoststack, **nicht**
  als hoststack-loser Solo-Gast) real geladen, gespielt und über den normalen
  Spiel-/Speicherweg gespeichert (nicht nur die tolerante Vorschau) sowie von einem
  frischen Prozess zurückgelesen. Der tolerierte Cap-Überlauf-Rest besteht
  unmittelbar nach dem Import noch und wird erst mit diesem echten Speichern
  bereinigt — **keine** pauschale Zusage, dass jede Restwarnung automatisch
  verschwindet; die exportierte Ausgangsfassung bleibt byteidentisch erhalten.
- **J5_RETURNING_GUEST_REPLACES_ACTIVE_COPY — erneut anreisender Gast.** Dieselbe
  Figur reist ein zweites Mal; B zeigt die alte **und** die neue Kopie (Level 2
  bzw. 3), die extern fortgeschrittene Fassung ersetzt via `adopt_incoming` nur
  bei ausdrücklicher Wahl die aktive Kopie, der nächste Spielinput trägt den neu
  gewählten Stand; die Folgegeneration des Abschnitts wird korrekt aufgelöst.
- **J6_CONFLICTS_AND_NO_DOUBLE_EFFECTS — Konflikte gehalten, keine
  Doppeleffekte.** Eine bereits fremd registrierte Char-ID wird vor jedem
  Zielwrite geparkt (auch ohne aktiven Lock); aktive Bindung bzw. offener
  Abschluss bzw. abweichender Stand ohne Wahl → `parked`; identischer Re-Import →
  `noop_identical`; ausdrückliches Behalten → `keep_existing`; Unbeteiligte
  bleiben unverändert.
- **J7_CANONICAL_PLAN_AND_PLAYER_FLOW — kanonische Planstelle und Spielerfluss.**
  Diese Datei ist die einzige Planstelle (verlinkt aus `terminal-status.md`); der
  beschriebene Weg ist der real spielbare A→B→A-Terminalfluss, nicht eine
  gesonderte Beschreibung neben dem Code.
- **J8_DELIVERY_FINAL_BYTES — Lieferung echter finaler Bytes.** Die tatsächlich
  verwendeten Evidenztreiber mit gemessenen Hashes, ihre äußeren Läufe am eigenen
  finalen Produktanker, der nachvollziehbar gebundene Treiber `drive_j1_j8.py`
  sowie der reguläre reviewbare PR mit zugeordneter CI sind in der Rückgabe
  (`03_RUECKGABE.md`, `REWORK.json`, `EVIDENCE-MAP.md`) benannt.

## Geliefert in R2 (Betreiber-Etappe)

Die erste Betreiberetappe ist mit R2 **geliefert und gegen echte Ergebnis-Bytes
belegt**. Sie ergänzt den bestehenden Tisch-/Spielkern chirurgisch; die Spiel-,
Speicher- und Importpfade bleiben unverändert.

- **Betreiber als eigenständige Rolle am Normalweg** (`mmo_sim/ui/tui.py`,
  `mmo_sim/core/table_admission.py`). Ein Hostanbieter kann einen Abschnitt für
  angenommene menschliche Gäste bereitstellen, **ohne selbst mitzuspielen oder
  eine eigene Spielfigur mitzuführen** — über den **regulären** Tischweg, nicht
  nur über den Persona-Kurzweg. Die Leitung wird aus dem Roster aufgelöst; ein nur
  bedienender Betreiber zählt nicht als Mitspieler und erzeugt keinen Phantom-
  charakter. Die Eingaben von Betreiber-Steuerung und menschlichem Gast werden
  **eindeutig getrennt geroutet**; eine kollidierende Eingabequelle wird
  abgewiesen, statt Antworten zu vermischen.
- **Eine gemeinsame, dauerhafte Stop-/Abschlussentscheidung** (`mmo_sim/core/
  admission.py`, `mmo_sim/core/store.py`, `mmo_sim/core/table_admission.py`).
  Zwischen einem Betreiber-Stop und dem Abschnittsabschluss entscheidet **genau
  ein** neustart-fester atomarer Entscheid pro Tisch (Test-and-Set, Einzel-
  gewinner) — es gibt kein Zeitfenster, in dem Stop und Abschluss beide „gewinnen".
  Ein bereits gepinnter Plan bleibt committet (kein Rollback, idempotente
  Fertigstellung möglich); ein vor dem Pin gewonnener Stop verhindert Plan und
  Save.
- **Sauberer Abbruch und sichtbare Speichergrenze.** Vor der verbindlichen
  Abschlussentscheidung kann der offene Abschnitt **wirklich** abgebrochen werden:
  Der Gast erhält genau seine vor Spielbeginn gebundene, tatsächlich angenommene
  Anfangsfassung zurück (Originalbytes, nicht nachgebaut, nicht um ungespeicherte
  XP/Geld/Items ergänzt), betroffene Bindungen werden gelöst, und er kann erneut
  teilnehmen — Verwurf ist **nicht** bloß Pause. Ist der Plan bereits angenommen,
  bleibt der verbindliche Stand erhalten; späte Modellantworten oder Recovery
  speichern einen wirksam abgebrochenen Abschnitt nicht nachträglich.
- **Vom Betreiber eng freigegebene Gast-Erschaffung** (`mmo_sim/domain/zeitriss/
  creation_service.py` als Freigabeschicht + `mmo_sim/ui/tui.py`). Ein Gast ohne
  fertige Figur stellt eine konkrete Erschaffungsanfrage; der Betreiber bestätigt
  genau **einen** Erschaffungsvorgang. Erst dieser durable Grant — gegen den
  persistierten Datensatz geprüft (fehlend/abgelehnt/fremd/veraltet wird vor jedem
  GM-Aufruf abgewiesen), **ohne** Bezug auf eine Fähigkeitsflagge der aufrufenden
  Session — erlaubt den bedienten Dialog über **denselben** unveränderten
  Erschaffungs-/GM-Kern; es entsteht **keine** zweite Erschaffungslogik. Die
  angenommene Figur wird über den normalen Produktweg gespeichert und ist als
  persönliches JSON mitnehmbar; ein abgebrochener Entwurf erzeugt keinen
  erfundenen Save.

Belegt über echte Produkt-/Terminalpfade: deterministische Treiber am Modellrand
sowie ein persistenter Evidenzlauf, dessen prozessübergreifende Grenzen **echte
neue `python3`-Interpreter** sind (`subprocess`, inklusive eines harten
Prozessabbruchs nach dem Plan-Pin und anschließendem idempotentem Abschluss in
einem frischen Prozess). Gemessene Hashes und äußere Läufe liegen in der Rückgabe
(`R2-RESOLUTION.json` und das Ergebnis-Manifest).

## Geliefert in R3 (Betreiberetappe: erreichbar am Normalweg + prozessfest belegt)

R3 liefert **keine neue Fähigkeit über die Betreiberetappe hinaus**, sondern
schließt deren Erreichbarkeits- und Dauerhaftigkeitslücke am tatsächlichen
Terminalstart und belegt sie prozessübergreifend:

- **Erreichbare Betreiber-/Gaststeuerung am echten Launcher** (`scripts/mmo_sim.py`).
  Die Betriebssteuerung ist jetzt über den **regulären Terminalstart** erreichbar,
  nicht nur über eine im Test injizierte Kontrollquelle: explizite Kanalflaggen
  (`--operator-control-fifo`, `--guest-terminal <id>:<in>:<out>`, `--run-dir`,
  `--states-dir`) binden eine getrennte Kontroll- und eine getrennte Gasteingabe an
  denselben unveränderten Tisch-/Admissionskern. Ein normaler lokaler Betreiber
  erreicht damit Stop/Steuerung an einem laufenden Abschnitt; die Eingabetrennung
  aus R2 bleibt erhalten.
- **Stop-/Abschluss-/Wiederaufnahmegrenze über echte Prozessgrenzen belegt.** Der
  dauerhafte Entscheid (Abbruch vor Commit gegen committeten Plan nach Annahme)
  ist nun in **frischen `python3`-Interpretern** nachgewiesen — inklusive eines
  harten Prozessabbruchs nach dem Plan-Pin und anschließender idempotenter
  Fertigstellung in einem neuen Prozess (byteidentische Anfangs-/Primärfassung,
  kein Phantom-Save, keine Doppelveröffentlichung, kein nachträgliches Speichern
  eines wirksam abgebrochenen Abschnitts).
- **Hostlose, vom Betreiber freigegebene Gast-Erschaffung prozessfest belegt.** Der
  mehrschrittige bediente Erschaffungsdialog über denselben Erschaffungs-/GM-Kern,
  der durable Grant (fehlend/abgelehnt/fremd/veraltet wird abgewiesen) und der
  persönliche Save sind über echte neue Prozesse nachgewiesen; ein reiner Gastclient
  wird dadurch kein eigener GM-Host.

Belegt über vier Ergebnisfamilien (T1–T4) mit **echten privaten Ergebnisdateien**
und **echten äußeren OS-Läufen** (gemessene Hashes, `argv`/`cwd`/Exit/UTC je Lauf).
Messwerte und Läufe liegen in der Rückgabe (`R3-RESOLUTION.json` und das
Ergebnis-Manifest).

**Dieser in R3 offene Vorbefund ist mit R4 behoben** (siehe „Geliefert in R4").
Der **Tisch-Wiederaufnahme-Weg** (`tisch-start` auf einen gebundenen Abschnitt nach
Prozess-Neustart) stufte einen über die Admission aufgenommenen **menschlichen**
Gast-Leiter fälschlich als KI-Persona ein und brach die Fortsetzung ab. R4 erhält
beim Wiederaufnehmen die tatsächliche menschliche Mitgliedschaft aus den legitimen
Rollen-/Anschlussdaten; der normale Fortsetzen-Weg führt wieder bis zum Abschluss
und zur persönlichen Save-Rückgabe, ohne KI-Persona-Ersatz.

## Geliefert in R4 (Betreiberetappe: normale Bedienwege geschlossen)

R4 liefert **keine neue Fähigkeit über die Betreiberetappe hinaus**, sondern schließt
die zuletzt offenen normalen Nutzerwege und macht sie prozessfest bedienbar:

- **Gast-Erschaffung am echten Launcher durchgängig bedienbar.** Ein über
  `--guest-terminal` angeschlossener Gast bedient seine Erschaffungs-/Menübefehle
  jetzt tatsächlich über sein eigenes Terminal (eigener nebenläufiger Dispatch) auf
  der mit dem Anbieter verbundenen Autorität — ohne eigenen Hoststack. Pro
  Gast-Terminal liest zu jedem Zeitpunkt **nur ein** Leser (Menübefehl erreicht das
  Menü, Tischzug die Runde), keine konkurrierende Fehlzustellung.
- **Erreichbarer Betreiberstop der offenen Gast-Erschaffung.** Der berechtigte
  Betreiber kann eine bereits freigegebene Erschaffung während des offenen
  Anbieterrequests adressiert stoppen (`gast-erschaffung-stop <id>`); Stop und
  verbindliche Annahme ordnen sich an **einer** gemeinsamen dauerhaften Entscheidung
  (Operation/Generation). Ein gewonnener Stop macht den Entwurf terminal; eine späte
  Antwort wird verbucht, aber nicht veröffentlicht.
- **Einmalige Veröffentlichung auch beim identischen Retry.** Eine bereits
  vollständig publizierte Erschaffung erzeugt bei identischem Retry **keine** zweite
  Current-Version mehr; die bereits angenommene Figur bleibt idempotent fertigstellbar.
- **Normaler menschlicher Gast-Resume bis zum Abschluss** (behobener R3-Vorbefund
  oben): der menschliche Gast-Leiter überlebt den `tisch-start`-Resume mit richtiger
  Rolle und erreicht Final plus persönliche Save-Rückgabe.

Belegt über dieselben vier Ergebnisfamilien (T1–T4) am **echten Launcher/Dispatch**
mit **echten äußeren OS-Läufen** (literale `argv`, `cwd`, Exit, UTC je Lauf) und echten
privaten Ergebnisdateien; der Anbieter-Modellrand ist dabei eine klar gekennzeichnete
deterministische Grenzinjektion, kein Live-Modelllauf. Messwerte und Läufe liegen in
der Rückgabe (`R4-RESOLUTION.json` und das Ergebnis-Manifest).

## Geliefert in R5 (Betreiberetappe: die drei verbliebenen Grenzfälle geschlossen)

R5 liefert **keine neue Fähigkeit**, sondern schließt genau die drei vom R4-Generalreview belegten
Restbefunde an den benannten Grenzen und berichtigt die dafür zu weit gefassten R4-Erledigtaussagen
oben sachlich:

- **Terminaler Stop auch im laufenden inneren Dialog.** Die R4-Aussage „ein gewonnener Stop macht den
  Entwurf terminal" galt nur für die Publikation: der innere Erschaffungsdialog sandte nach gewonnenem
  Stop noch einen weiteren Anbieterrequest. R5 prüft die gemeinsame Stop-Entscheidung jetzt vor **jedem**
  weiteren Request für genau diese Operation/Generation (`mmo_sim/core/creation_service.py` Loop-Gate +
  `mmo_sim/domain/zeitriss/creation_service.py:creation_stop_committed`), einschließlich der internen
  Save-Korrekturschleife (`mmo_sim/core/save_correction.py:pursue_single_figure_correction`); nach gewonnenem Stop endet der
  Weg terminal ohne dritten Request, die bereits offene Antwort bleibt ehrlich verbucht.
- **Erwartete Generation am Abschluss gebunden.** Der Abschluss prüft jetzt, dass der aktuell gültige
  Grant dieselbe Generation trägt wie der laufende Vorgang; ein neuer Grant einer anderen Generation gibt
  einen alten laufenden Versuch nicht frei (`mmo_sim/ui/tui.py:_finish_granted_guest_creation`).
- **Exklusive Gast-Eingabeübergabe wirklich atomar.** Die R4-Aussage „zu jedem Zeitpunkt nur ein Leser"
  war quellseitig ein TOCTOU (Check und Konsum nicht atomar mit dem Host-Claim). R5 führt einen
  gemeinsamen Ausschluss-Lock ein: Claim-Setzen (Host) und Check+Konsum (Gast-Menü) laufen atomar unter
  demselben Lock, eine Zeile fällt deterministisch genau einem Leser zu (`mmo_sim/ui/tui.py`).
- **Unterbrochene persönliche Publikation übernimmt den erreichten Schritt.** Wird der Prozess zwischen
  Versionsdatei und State-Zeiger unterbrochen, übernimmt der normale Retry genau diese verwaiste,
  inhaltsgleiche Version statt eine zweite anzulegen (`mmo_sim/core/store.py:publish_current_save`); die
  bereits in R4 belegte vollständig publizierte Wiederholung bleibt unverändert.

Belegt über drei neue Ergebnisfamilien (r5a/r5b/r5c) am echten Launcher/Dispatch bzw. am echten
`TuiSession`-Leser, mit echten äußeren OS-Läufen (literale `argv`, `cwd`, Exit, UTC) bzw. einer
deterministischen In-Process-Barriere; der Anbieter-Modellrand bleibt eine gekennzeichnete
Grenzinjektion, kein Live-Modelllauf. Messwerte und Läufe liegen in der Rückgabe (`R5-RESOLUTION.json`
und das Ergebnis-Manifest). G2/G3 und der bereits vollständig publizierte identische Retry bleiben als
R4-Ergebnisse unverändert anerkannt.

**R5-Teilauftrag Tisch-/Gruppen-Save-Pfad (quellseitig bestätigt, kein neuer Patch).** Der im R5-Lauf
dokumentierte Fund — die Gruppen-Save-Korrektur `mmo_sim/core/save_correction.py:pursue_group_save_correction`
trägt keinen eigenen lokalen `stop_check` — wurde als enger Teilauftrag gegen die echte Quelle geprüft. Beide
Zweige (frische Runde und Wiederaufnahme) konvergieren auf **einen** Versand (`send_correction_turn`), der vor
jedem Transport den tisch-skopierten Betreiber-Stop über `read_admission_block(…, table_id=…)` →
`mmo_sim/core/admission.py:read_table_stop` liest; eine nachträgliche Publikation des abgebrochenen Vorgangs ist
ausgeschlossen, weil `mmo_sim/core/store.py:complete_section` die Plan-Fixierung über denselben atomaren
Entscheidungs-Slot (`try_commit_table_decision`) führt, um den auch der Stop (`request_table_stop`) konkurriert.
Der Fall ist damit **durch Bauart geschützt**, nicht durch einen fehlenden lokalen Check offen; der Schutz wird
durch einen gezielt ergänzten Beleg-Test
(`tests/mmo_sim/test_zr_betreiber_r5_group_save_tischstop_resume_2026_11_05.py`) am echten Code demonstriert.
Keine Produktcode-Änderung in diesem Teilauftrag; die offenen G5-Restpunkte (T1/T2) bleiben davon unberührt.

## Geliefert in R6 (zwei präzise Produktkanten geschlossen)

R6 liefert **keine neue Fähigkeit**, sondern schließt genau die zwei vom R5-Generalreview an den
benannten Grenzen belegten Restkanten und präzisiert die dafür zu weit gefasste R5-Aussage oben:

- **Terminal auch bei spät zurückkehrender gültiger Antwort nach gewonnenem Stop.** Die R5-Aussage
  „terminal ohne dritten Request" galt für das Unterbinden eines *weiteren* Anbieterrequests; sie deckte
  nicht den Fall, dass der **bereits offene** Request nach dem gewonnenen Stop noch eine *gültige* Antwort
  zurückliefert. R6 prüft die gemeinsame generationsgebundene Stop-Entscheidung jetzt auch **nach** der
  ehrlichen Verbuchung dieser spät zurückkehrenden Antwort und **vor** innerer Ergebnisannahme bzw.
  Folgefrage (`mmo_sim/core/creation_service.py`): die Antwort bleibt verbucht, der Weg ist terminal —
  keine weitere Gastfrage, keine Annahme/Publikation. Dieselbe Entscheidung greift in der inneren
  Save-Korrekturschleife für eine **spät gültige** Korrekturantwort (`mmo_sim/core/save_correction.py:
  pursue_single_figure_correction`): sie wird als `correction_received` verbucht, aber **nicht** mehr
  adoptiert. Ein gültiger Grant einer anderen Generation gibt einen alten laufenden Versuch weiterhin
  nicht frei (unveränderte R5-Generationsbindung).
- **Fehlende Hostaufnahme beim normalen Import vor erster Admission.** Importiert ein hostloser Gast
  seine vollständige, bereits identisch im gemeinsamen Spielstand liegende Figur **vor** der ersten
  Tisch-Aufnahme, blieb die Host-Projektion (Onboarding/Katalog) bisher aus, sodass der spätere Tischstart
  die Figur nicht auflösen konnte. R6 vervollständigt im `noop_identical`-Zweig der Tisch-Annahme genau
  diese fehlende Host-Projektion (`mmo_sim/ui/tui.py`) — **ohne** zweite Current-Version/Fortschritt und
  **ohne** Seed-Ersatzaufnahme als Vorbedingung. Die allgemeine Importentscheidung bleibt `noop_identical`
  (kein Umschlag auf „neu registrieren"); der echte identische Re-Import bleibt idempotent.

Belegt über fünf neue launcher-basierte Nachweisfamilien (`a_dialog`, `a_correction`, `b_import`,
`c_teilpub`, `d_t2`) am echten `scripts/mmo_sim.py`-Subprozess mit echten äußeren OS-Läufen (literale
`argv`, `cwd`, Exit, UTC je Lauf) und echten privaten Ergebnisdateien; der Anbieter-Modellrand bleibt
eine gekennzeichnete deterministische Grenzinjektion, kein Live-Modelllauf. `c_teilpub` und `d_t2` sind
reine Nachweisfamilien ohne neue Storearbeit: sie liefern die fehlenden Originalkörper der persönlichen
Teilpublikation bzw. die korrekte Stop-vor-Primärrest-Reihenfolge an der bereits gebauten T2-Grenze.
Messwerte und Läufe liegen in der Rückgabe (`R6-RESOLUTION.json` und das Ergebnis-Manifest). G1/G2/G3,
der Gruppen-Save-Schutz und die anerkannten T1/T1d/T2-Ergebnisse bleiben als frühere Ergebnisse
unverändert anerkannt.

## Jetzt (bewusste Grenzen dieser Etappe)

- Vollständig terminalbasiert, **kein Netz**. Die Figur reist auf Datenebene
  (Datei A → Datei B → Datei A), nicht über eine Verbindung.
- Die Tisch-Geschäftsvorgänge sind so geschnitten, dass sie später transportfähig
  bleiben: ein gemeinsamer, persistenter Admissionsdienst mit klaren Host-only-
  Übergängen, nicht in die Oberfläche eingestreute Sonderfälle.
- Die frühere Lücke an der Verlassens-/Pausengrenze ist mit der jetzt gelieferten
  Betreiberetappe adressiert: ein kontrollierter Stop und ein echter, nicht-
  destruktiver Abbruch vor der Abschlussentscheidung stehen (siehe „Geliefert in
  R2 (Betreiber-Etappe)"). Weiterhin **nicht** geliefert sind LAN/Netz und mehrere
  gleichzeitige Abschnitte auf einem Host.
- Kein Billing-, Lobby- oder Netz-Platzhalter wurde eingezogen.

## Betreiber-, Misch- und Netzbetrieb (verbindliche Fortschreibung)

Die **Betreiber-Etappe** dieses Plans — eigenständige Betreiberrolle, erreichbarer
Stop, sauberer Abbruch vor Commit mit sichtbarer Speichergrenze, vom Betreiber
freigegebene Gast-Erschaffung — ist mit R2 **geliefert und belegt** (siehe
„Geliefert in R2 (Betreiber-Etappe)"); die folgenden Absätze halten ihren
verbindlichen Vertrag fest, der jetzt im Produkt realisiert ist. **Noch nicht als
geliefert oder getestet abgenommen** bleiben der **Mischbetrieb/LAN** und
**mehrere gleichzeitige Abschnitte auf einem Host** (am Ende dieses Abschnitts).
Alles steht an **dieser** einen kanonischen Planstelle — es gibt keine zweite
dauerhaft gepflegte Repo-Roadmap. Die zugrunde liegende, rein lesende
Architekturstudie liegt als Leseanker im Auftragspaket des Nachzugs, **nicht** als
Datei im Repository.

**Betreiber ist eine eigenständige Rolle.** Ein Hostanbieter kann einen Abschnitt
für seine eigenen Personas oder angenommene menschliche Gäste bereitstellen,
**ohne selbst mitzuspielen oder eine eigene Spielfigur mitzuführen**. Er sieht den
öffentlichen Spielverlauf und behält seine Betriebssteuerung; Zuschauen erzeugt
keinen Spielerzug, keinen Phantomcharakter und keinen eigenen Fortschritt. Ein
Gerät/Terminal-Client ist ein Bedienplatz und nicht automatisch ein Spieler;
Teilnehmer, Figur und Betreiber sind getrennte Rollen. Die Größenpolicy zählt die
wirklichen Mitspieler, nicht einen nur zuschauenden Betreiber. Persona-Anfragen
gehen ausschließlich aus dem eigenen bestätigten Bestand an dessen Anbieter.

**Stop und sauberer Abbruch.** Die erste Betreiberetappe ist ausdrücklich keine
Verwaltung beliebig vieler eingefrorener Runden, sondern ein **sauberer
Abbruch**: Der Betreiber kann Stop anfordern — auch während eines GM-/
Personaaufrufs, nicht erst beim nächsten menschlichen Prompt. Ein bereits
versandter Providerrequest wird dadurch nicht nachweislich kostenlos rückgängig
gemacht; seine Abrechnung und empfangenen Rohantworten bleiben korrekt verbucht.
Nach wirksamem Stop werden weitere Requests und neue verbindliche
Speicherentscheidungen verhindert. Ein Stop gilt für den zugeordneten Tisch/
Abschnitt, nicht still für fremde Tätigkeiten im selben Datenroot.

**Sichtbare Speichergrenze.** „Noch offen" heißt **nicht** automatisch
„ungespeichert verwerfbar". Vor der verbindlichen Abschlussentscheidung kann der
offene Abschnitt kontrolliert abgebrochen werden; ein menschlicher Gast kann
ausdrücklich „Ungespeicherten Abschnitt verwerfen und Tisch suchen" wählen und
erhält genau die vor Spielbeginn gebundene **tatsächlich angenommene
Anfangsfassung** zurück (Originalbytes, nicht aus altem Onboarding nachgebaut,
nicht um ungespeicherte XP/Geld/Items ergänzt; eine legitim tolerierte
Anfangsfassung behält ihre Warnungskennzeichnung). Ist der Abschlussplan bereits
angenommen oder der Primärsave schon teilweise/vollständig publiziert, erhält
Stop die verbindliche Fassung („Spielstand übernommen; Abschluss noch offen") —
**kein Zurückrollen** auf den Anfangssave, idempotente Fertigstellung bleibt
möglich. Ein vollständig geschlossener Abschnitt gibt dem Gast den wirklich
aktuellen abgeschlossenen Save mit; Stop verhindert dann nur einen weiteren
Abschnitt, verwirft aber keine gespeicherte Karriere. Späte Modellantworten oder
Recovery dürfen einen wirksam abgebrochenen Abschnitt nicht nachträglich
speichern.

**Gast ohne JSON: vom Betreiber freigegebene Erschaffung.** Ein neuer Gast kann
ohne fertige Figur eine Erschaffung anfragen; der Betreiber bestätigt genau
diesen Erschaffungsabschnitt und stellt seine Spielleitung bereit. Der Gast
bedient seinen Dialog im Terminal, erhält aber **weder** pauschale Hostfähigkeit
**noch** Zugriff auf Host-Shell, allgemeine Dateiwurzeln, Einstellungen oder
Modellzugänge. Vor dem tatsächlichen Erschaffungsabschluss ist die Figur ein
Entwurf: Es gibt **noch kein** gültiges früheres Figuren-JSON, das ein Abbruch
zurückgeben könnte, und ein abgebrochener Entwurf erzeugt **keinen** erfundenen
Save. Eine angenommene Figur wird über den normalen Produktweg gespeichert und
als persönliches JSON mitnehmbar. Hostgestützte Erschaffung macht aus dem reinen
Gastclient keinen eigenen GM-Host; Solo, eigene Personas und selbst Anbieten
erfordern weiterhin einen eigenen eingerichteten Hoststack.

**Mischbetrieb: drei Menschen lokal, der vierte über LAN (verbindlicher LAN-
Zielfall).** Drei Menschen teilen einen Terminalplatz, der vierte kommt über LAN;
alle vier sind getrennte Teilnehmer mit ihren jeweiligen Figuren am selben Tisch.
Die Eingabeübergabe am gemeinsamen Gerät bleibt erkennbar; der LAN-Anschluss ist
ein weiterer Zugang zum **selben** fachlichen Tischdienst — kein „ein Client = ein
Spieler"-Zwang und keine zweite Spiellogik für LAN-Gäste. Nach dem gemeinsamen
Abschnittsabschluss können die drei **einen gemeinsamen** HQ-Abschnitt spielen
(nicht drei Soloabschnitte nacheinander); der vierte spielt währenddessen auf
einem eigenen eingerichteten Host seinen Solo-HQ-Abschnitt und reist danach mit
aktualisierter Figur wieder an, die der Zieltisch an einer passenden
Abschnittsgrenze in der ausdrücklich angenommenen neuen Fassung aufnimmt.
Unterschiedliche Abschnittszahlen und Level allein verhindern das Zusammenspiel
nicht. Eine Figur darf im vorgesehenen Spielweg nur an **einen** offenen Abschnitt
gebunden sein; die heutige lokale Sperre in einem `run_dir` beweist noch keine
geräteübergreifende Ausschließlichkeit, und der spätere LAN-/Übergabeweg muss
diese Autoritätsgrenze erhalten (allein kopierbare JSON-Dateien sind kein
globaler Eigentums- oder Sperrnachweis). Dafür wird **kein** globales Kontosystem
oder Signaturprojekt eingeführt. Ein eigener Host bleibt Komfort, keine
Mitspielpflicht; ein reiner Terminalgast mit JSON bleibt vollwertiger Mitspieler
und muss OpenWebUI/LiteLLM beziehungsweise den eigenen Modellstack nicht
installieren.

**Mehrere gleichzeitige Abschnitte auf einem Host** sind eine **zusätzliche,
noch nicht nachgewiesene** lokale Fähigkeit mit getrennten Eingaben,
Abschnittsbindungen, Veröffentlichungen und Stopkontrollen. Weder LAN noch zwei
Terminalfenster beweisen sie; sie wird separat konkretisiert und nachgewiesen und
ist hier ausdrücklich **nicht** als bereits vorhanden ausgegeben. Zwei
unabhängige Hosts können getrennte HQ-Gruppen parallel führen, ohne auf diese
Zusatzfähigkeit zu warten.

### Feste Reihenfolge

1. ✅ **Geliefert (R2):** der beauftragte lokale Tisch-/Figurenreiseweg ist
   geschlossen und die kanonische Produktprosa berichtigt; Betreiber-, Misch- und
   Netzbetriebsrichtung ist hier festgehalten.
2. Die Änderung durchläuft die reguläre Review- und Merge-Freigabe; sie wird
   nicht selbsttätig übernommen.
3. ✅ **Geliefert (R2), in R3 am Normalweg erreichbar gemacht und prozessfest
   belegt:** die eigene Betreiberetappe — Anbieter ohne Spielfigur, öffentliche
   Zuschaueransicht, erreichbarer Stop, sicherer Abbruch vor Commit, keine
   Rücksetzung danach, hostgestützte Gast-Erschaffung. R3 bindet die Steuerung an
   den echten Launcher und weist die Stop-/Abschluss-/Retry-Grenze über echte neue
   Prozesse nach (siehe „Geliefert in R3"); ein pre-existing, außerhalb des
   Gegenstands liegender Tisch-Wiederaufnahme-Befund bleibt offen
   (`R3-RESOLUTION.json`).
4. **Als Nächstes:** LAN verbindet Terminal-Clients mit demselben Dienst (drei
   lokale Menschen plus LAN-Gast, gemeinsame/getrennte HQ-Gruppen, erneut
   angenommene aktuelle Gastfigur, klare Eingabe-/Figurenbindung).
5. Mehrere parallele Abschnitte auf einem Host und eine mögliche Pause-/Wechsel-/
   Fortsetzungsverwaltung bleiben gesonderte Anschlussfähigkeiten, falls danach
   sinnvoll.

**Reihenfolge-Notiz (ZR-BETREIBER-GASTERSCHAFFUNG):** Betreiberetappe →
README/Doku/selbsterklärendes Terminal (optional Zeit-Gedanken in echten
Wartephasen) → LAN → optional parallel/Pause-Komfort. Spätere Etappen werden
hier jetzt nicht vorgezogen implementiert.

Keine Browseroberfläche, keine übergreifende Chatlobby und keine Abrechnung im
Spiel. Persönlicher Figurensave, Populationsbackup und optionales späteres
Persona-Reisepaket bleiben getrennt. Keine pauschale Stable- oder
Kostenkonstanzzusage.
