# Produktplan — Figurenreise am Tisch

Stand: 2. November 2026. Diese Datei ist die **einzige** Planstelle für den
Produktpfad „Figurenreise am Tisch". Sie beschreibt einen zusammenhängenden,
rein terminalbasierten Weg: Ein Mensch bietet an seinem Gerät einen Tisch an
oder sucht einen, eine Anfrage wird vom Host entschieden, es wird gespielt, der
Abschnitt schließt, der Gast geht (oder der Host spielt allein weiter), und der
Gast kehrt später mit seiner **selbst** fortgeschrittenen Figur zurück. Die
Figur reist dabei real über Export/Import zwischen zwei getrennten Datenwurzeln
A → B → A. Ein paralleler Fahrplan wird hier bewusst nicht geführt; eine native
LAN-/Netz-Lobby bleibt getrennt und ist unter „Betreiber- und Mischbetriebsplan"
abgegrenzt und ausdrücklich als noch nicht geliefert gekennzeichnet.

## Zwei-Wurzel-Modell (A → B → A)

- **Wurzel A — Gastgerät, ohne Hoststack.** Der Gast besitzt den Terminal-Client
  und seine eigenen JSON-Dateien, aber keinen eigenen Spielleitungs-/Persona-
  Stack. Ohne Spielleitungsanbindung kann A **keine Figur eigenständig
  erschaffen** — der Erschaffungsdialog läuft über denselben GM-Transport wie
  das Spiel und bleibt ohne ihn ein ehrlicher Teilstand. A nutzt eine bereits
  host-/stackgestützt angelegte Figur und exportiert bzw. importiert sie von
  dort nur noch. Die vom Betreiber freigegebene, hostgestützte Gast-Erschaffung
  ohne fertiges JSON ist unter „Betreiber- und Mischbetriebsplan" beschrieben
  und ausdrücklich noch nicht geliefert.
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
regulärer Debrief/Abschluss. Es gibt hier **keine** automatische
Bereinigungsgarantie und keinen neuen Abbruchmechanismus; die kontrollierte
Betreiber-Stop-/Abbruchsteuerung ist Teil der noch nicht gelieferten
Betreiberetappe (siehe unten).

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

## Jetzt (bewusste Grenzen dieser Etappe)

- Vollständig terminalbasiert, **kein Netz**. Die Figur reist auf Datenebene
  (Datei A → Datei B → Datei A), nicht über eine Verbindung.
- Die Tisch-Geschäftsvorgänge sind so geschnitten, dass sie später transportfähig
  bleiben: ein gemeinsamer, persistenter Admissionsdienst mit klaren Host-only-
  Übergängen, nicht in die Oberfläche eingestreute Sonderfälle.
- **Keine** automatische Bereinigungsgarantie an der Verlassens-/Pausengrenze
  (siehe oben). Die kontrollierte Betreiber-Stop-/Abbruchsteuerung ist noch nicht
  geliefert.
- Kein Billing-, Lobby- oder Netz-Platzhalter wurde eingezogen.

## Betreiber- und Mischbetriebsplan (verbindliche Fortschreibung, noch nicht geliefert)

Die folgenden Fähigkeiten sind **noch nicht als geliefert oder getestet
abgenommen**. Sie halten die neue Richtung (Betreiberkontrolle, gemischte
Terminalplätze) an **dieser** kanonischen Planstelle fest — es gibt keine zweite
dauerhaft gepflegte Repo-Roadmap. Die zugrunde liegende, rein lesende
Architekturstudie (Betreiberkontrolle und gemischte Clients mit
risikoorientierten Prüfvorschlägen) liegt als Leseanker im Auftragspaket des
Nachzugs, **nicht** als Datei im Repository; sie beschreibt geplante Fähigkeiten,
keine gelaufenen Produktbeweise.

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

1. R2 schließt den beauftragten lokalen Tisch-/Figurenreiseweg und berichtigt die
   kanonische Produktprosa; Betreiber- und Mischbetriebsrichtung ist hier jetzt
   festgehalten.
2. Die Änderung durchläuft die reguläre Review- und Merge-Freigabe; sie wird
   nicht selbsttätig übernommen.
3. Eigene Betreiberetappe: Anbieter ohne Spielfigur, öffentliche Zuschaueransicht,
   erreichbarer Stop, sicherer Abbruch vor Commit, keine Rücksetzung danach,
   hostgestützte Gast-Erschaffung.
4. LAN verbindet Terminal-Clients mit demselben Dienst (drei lokale Menschen plus
   LAN-Gast, gemeinsame/getrennte HQ-Gruppen, erneut angenommene aktuelle
   Gastfigur, klare Eingabe-/Figurenbindung).
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
