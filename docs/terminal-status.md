# Terminalstatus und Prüfstand

Stand: 29. Oktober 2026. Die Gegenwartsübersicht beschreibt die unabhängig
abgenommene lokale Beta-Etappe. Frühere Zwischenstände stehen getrennt
unter „Historische Zwischenstände“.

## Gegenwartsübersicht (Stand 29. Oktober 2026)

**Anerkannter lokaler Referenzweg:** Der lokale Terminal-Client an einem
Gerät beziehungsweise geteilten Terminal (`python3 scripts/mmo_sim.py`,
solo oder mit mehreren Menschen/KI-Personas am selben Gerät) ist der aktuell
belegte Weg. Eine native LAN-/Remote-Lobby ist davon weiterhin getrennt und
nicht Teil dieser Übersicht.

Tatsächlich belegter Umfang aus dem jüngsten geprüften R4-Anschluss:

- Der vorhandene Referenzlauf umfasst **fünf Figuren in einem Duo und einem
  Trio mit je zwei geschlossenen Runden**. Die beiden Trio-Abschlüsse waren
  bereits vor dem abschließenden Duo-B-Nachtrag erreicht und bleiben als
  Teilfortschritt anerkannt.
- **Duo-B wurde mit `best_effort=true` gespeichert und geschlossen** — ein
  freigegebener, geeigneter Kandidat mit strukturellen Listenwarnungen wurde
  dafür übernommen. Das ist ein autorisierter Produktabschluss, **kein**
  Schema-PASS (Details unten unter „Best Effort und SAVECOMPAT").
- **Fünf Endsave-/Kaltload-Bindungen** sind belegt: Die fünf Figuren-Saves
  wurden in einem frischen Prozess über den Produktleser geladen. Ihre
  Hash- und Figurenbindungen stimmen.
- **Eine wirksame Duo-Folgeaktion** an einem regulären neuen Tisch nach der
  Wiederaufnahme ist belegt. Ein zweiter strukturell abgeschlossener
  Abschnitt an diesem Folgetisch wird damit **nicht** behauptet.
- Der gezielte, formal gebundene **A→B-Fortsetzungsnachweis** wurde am Duo
  geführt. Die zwei bereits geschlossenen Trio-Runden bleiben daneben
  erhalten; die abschließende neue Folgeaktion betrifft den Duo-Tisch.

**Best-Effort-Grenze:** Nach höchstens drei zusätzlichen Korrekturversuchen
übernimmt das System den besten zulässigen Kandidaten; ein früherer
brauchbarer Erfolg beendet die Reparatur sofort. Eine verbleibende
strukturelle Warnung bleibt eine Warnung und ist **kein** Schema-PASS; der
nächste Load bereinigt den Stand nicht garantiert vollständig. Ein
automatischer Crash-Recovery-Pfad ist dabei **nicht** live abgenommen —
belegt ist ausschließlich ein regulärer Kaltstart mit anschließender
Folgeaktion.

Der hier beschriebene lokale R4-Umfang ist am 29. Oktober 2026 unabhängig
abgenommen und bildet die lokale Beta-Etappe. Grundlage sind die geprüften
Produktkorrekturen und Originalbelege für Speicherung, Kaltladen und
wirksame Fortsetzung. Weitergehende Livewege bleiben gesondert zu prüfen.
Daraus folgt keine pauschale Zusage für Remote-/LAN-Mitspiel, alle
Modellanbieter, alle Betriebssysteme oder einen Stable-Release.

### Best Effort und SAVECOMPAT

Bis zu drei zusätzliche vollständige Korrekturen werden angefordert; bei
einem früheren brauchbaren Erfolg geht es sofort weiter. Eine ausdrücklich
freigegebene Übernahme eines geeigneten Kandidaten **mit** strukturellen
Listenwarnungen kann den Abschluss ermöglichen — die Warnung bleibt eine
Warnung, **kein** Schema-PASS; der nächste Load hat damit nicht garantiert
schon alles bereinigt.

Ein **SAVECOMPAT**-Stand bewahrt nicht direkt übernehmbare Daten samt
Herkunft; er ist selbst noch kein abgeschlossener Abschnitt — Details:
`systems/gameflow/speicher-fortsetzung.md#kompatibilitaetsstand`.
Die Prüfung kann gemischte Typfehler **und** Überlänge gemeinsam tolerieren;
die Aussage „Typfehler gehen immer ausschließlich nach SAVECOMPAT" ist
deshalb **falsch** und wird hier nicht behauptet. Welcher Stand beim
nächsten Start tatsächlich lädt, folgt dem final akzeptierten
Store-/Resume-Verhalten; es gibt keine pauschale Garantie für verlustfreie
oder vollständig schemagültige Exporte. Spielerseitige Kurzerklärung:
[Spielerstart § Best Effort und SAVECOMPAT](spielerstart.md#best-effort-und-savecompat).

<a id="was-vorhanden-ist"></a>

## Historische Zwischenstände (15.–23. Oktober 2026)

Die folgenden datierten Teilstände dokumentieren die damaligen Ergebnisse
und offenen Punkte. Für den heutigen lokalen R4-Umfang gilt die
Gegenwartsübersicht oben; alte Zwischenstände werden nicht rückwirkend
umgeschrieben.

Lokaler Einstieg, Figurenwahl und -erschaffung, Import und Export,
Rundenzusammenstellung, lokale Mehrpersonenführung und Wiederaufnahme sind
implementiert. In der dokumentierten LA1-Live-Erprobung wurden Start,
Menübedienung und die Budgetablehnung geprüft; drei von fünf vorgesehenen
Testfiguren wurden über den Produktweg abgeschlossen. Der gesamte Lauf
bleibt **LIVE_ASSISTED_PARTIAL**, nicht vollständige Endnutzerabnahme.

Die jüngste private Recoverylieferung wurde mit 49 beauftragten
Offlinefällen erneut geprüft. Normale Terminal-Wiederaufnahme über einen
Prozessneustart und die Originalantwortbindung beim Abschnittsabschluss
bestehen in den bezeichneten synthetischen Prüfungen. Die neue
CLI-Kontextkorrektur ist ein separat zu integrierender Kandidat.

Stand 22. Oktober 2026 (R4-Anschluss, neuer Livebeleg): Für einen
**einzelnen** Spieler ist der vollständige Abschnitts-Schluss jetzt live
gegen die gehostete Spielleitung belegt — `!save` im HQ erntet den
Save-Block strukturell in den Store (`__final.json`, Save-Versionszähler
steigt), über einen echten Prozessneustart hinweg und mit wirksamem
Folgezug (zweiter Abschluss). Die Abschluss-Erkennung ist an das
`!save`-Kommando plus den Save-Block gebunden und damit unabhängig von
der jeweiligen Formulierung der Spielleitung. Das ersetzt NICHT die unten
genannte vollständige Mehrfiguren-Live-Abnahme.

Stand 22. Oktober 2026 (R4-Mehrspieler-Anschluss, Endstand): Ein zusätzlicher
Erstharvest-Savekonflikt wurde behoben — zwei abweichende, jeweils gültige
Speicherstände derselben Figur in einer Spielleitungsantwort werden jetzt VOR
jeder Abschlussveröffentlichung erkannt und der Abschnitt gehalten, statt still
den ersten zu übernehmen (identische Wiederholungen bleiben zulässig). Für den
Mehrfiguren-Weg wurden zwei weitere Ursachen adressiert: die KI-Mitspieler laufen
jetzt standardmäßig ohne erweitertes Nachdenken (deutlich schnellere, kurze
Spielerzüge; in einem realen Livelauf lösten sich die zuvor beobachteten
Zeitüberschreitungen vollständig auf), und die Mitspieler-Personas erhalten eine
knappe Terminal-Bedienungsnotiz, damit sie das Speicherkommando am
Abschnittsende selbst absetzen (zuvor umschrieben sie es nur narrativ). In
realen, bezahlten Liveläufen wurden daraufhin alle fünf regulären
Bestandsfiguren tatsächlich erschaffen bzw. importiert und eine organische
Gruppe spielte eine vollständige Mission bis zur HQ-Rückkehr. Ein strukturell
abgeschlossener Mehrfiguren-Abschnitt (Abschnitts-Finalrecord live) wurde dabei
noch NICHT erreicht — die Ursache liegt NICHT im geprüften Produktcode, sondern
in einem eng umrissenen Verhalten des privaten Test-Treibers (ein gutartiges
Zeitfenster-Ende eines Einzelschritts wird derzeit als terminaler Halt
fehlklassifiziert) zusammen mit dem begrenzten Live-Budget dieses Zyklus. Der
kommandobasierte Abschnittsabschluss, der Savekonflikt-Fix und die
Save-Kommando-Erkennung bleiben durch den Einzelspieler-Livebeleg, die
synthetische Fünf-Figuren-A/B-Prüfung und gezielte Komponententests bestätigt.

Stand 23. Oktober 2026 (R4-Gruppenabschluss-Anschluss, beobachteter Stand): In
einem realen, bezahlten Mehrspieler-Lauf wurden alle fünf regulären
Bestandsfiguren tatsächlich bereitgestellt (zwei über den Importweg, drei
organisch erschaffen), eine organische Gruppe bildete einen Zweier- und einen
Dreiertisch, und der Dreiertisch spielte Abschnitt A bis in den Speicher- und
Abschlussablauf: das Leader-Speicherkommando wurde ausgelöst, die
Gruppen-Speicherstände der Mitglieder wurden geerntet und schema-korrigiert und
der Abschluss-Plan wurde geschrieben. Ein strukturell abgeschlossener Abschnitt
(Abschnitts-Finalrecord, danach Prozessneustart und zweiter Abschnitt) wurde in
diesem Lauf noch nicht erreicht: der Lauf endete an einer einzelnen
vorübergehenden Störung des isolierten Mitspieler-Prozesses (Exitcode ungleich
null ohne jede Fehlerausgabe), während der Abschnitt bereits finalisiert wurde.
Die Ursache liegt nicht im geprüften Produktcode, sondern war eine transiente
Infrastruktur-Störung; der private Test-Treiber behandelt eine solche
vorübergehende Störung in der Abschnittsphase jetzt wie eine Zeitpause (begrenzte
Wiederaufnahme im nächsten Schritt) statt als endgültigen Halt. Der vollständige
strukturelle Mehrfiguren-Abschluss über zwei Abschnitte bleibt damit der noch
offene Live-Nachweis und ist durch das verbleibende Live-Budget dieses Zyklus
begrenzt, nicht durch einen Produkt- oder Regelfehler.

Stand 23. Oktober 2026 (R4-Beta-Anschluss, beobachteter Stand): Der Generalreview der Rohbelege identifizierte vier konkrete Produktursachen (offener Abschlussplan wurde im Lobby-Resume nicht fortgesetzt; ein alleinstehendes Leader-Speicherkommando ohne nutzbaren Export lief in weitere Spielrunden; die A/B-Bindung erkannte den zweiten Abschnitt nicht an die beobachtete Gruppe; der Mitspieler-Adapter verwarf bei Fehlern den Standardausgabekanal). Diese vier Ursachen wurden am normalen Produktpfad behoben und sind durch gezielte Tests belegt. Zusätzlich fängt das Terminal ein Kontingent-/Budgetende mitten im Spiel (Abo- bzw. OpenRouter-Limit) jetzt als klaren, speichernden Pausenhinweis ab und ist danach nahtlos fortsetzbar, statt mit einem Fehler abzubrechen. In einem realen, bezahlten Lauf wurde Abschnitt A strukturell abgeschlossen, der Prozess regulär neu gestartet und Abschnitt B tatsächlich weitergespielt (fortgeschriebene Speicherstände über den Prozessneustart hinweg); ein Mitspieler-Prozess traf dabei real ein Kontingentende, das der neue Pausenhinweis sauber abfing. Ein strukturell abgeschlossener zweiter Abschnitt (Finalrecord für Abschnitt B) wurde in diesem Lauf noch nicht erreicht: im langen Abschnitts-B-Kontext wichen einzelne Mitspieler-Antworten in erklärende Meta-Kommentare aus, sodass das abschließende Speicherkommando am Abschnittsende ausblieb; dies ist der präzise benannte, noch offene Punkt für eine gezielte Folgeiteration und keine Aussage über vollständige Stable-Reife. Produktseitig sind die genannten Korrekturen und der Kontingent-Pausenhinweis in diesem Stand enthalten.

<a id="was-für-eine-vollständige-live-abnahme-noch-fehlt"></a>

## Historische Zielstrecke und weitergehende Nachweise

Die frühere Zielbeschreibung verband fünf reguläre Figuren, zwei
aufeinanderfolgende Abschnitte, gespeicherten A→B-Fortschritt,
Prozessneustart und gesonderte Abschlusswiederaufnahme. Im fortgesetzten
R4-Referenzlauf stehen jetzt vier geschlossene Gruppentische: Duo A/B und
Trio A/B. Hinzu kommen die fünf geladenen Endsaves und die belegte
wirksame Duo-Folgeaktion. Diese erreichten Teile bleiben anerkannt.

Die ursprüngliche formale A-Baseline band den Duo-Tisch; dessen gezielter
Fortsetzungsnachweis ergänzt die bereits erreichten Trio-Abschlüsse. Die
Belege stammen aus dem vorhandenen, fortgesetzten R4-Lauf. Der abschließende
Code-Nachtrag wurde mit gezielten geldfreien Regressionen geprüft.

Weitergehende Nachweise betreffen insbesondere zusätzliche automatische
Crash-Recovery-Pfade, andere Modellanbieter und Betriebssysteme,
vollständiges Community-Backup/Restore sowie native Remote-/LAN-Nutzung.
Sie erweitern den beschriebenen lokalen Beta-Umfang. Die konkrete
Modellroute und die Kostenhistorie bleiben dem jeweiligen Livebeleg
zugeordnet.

<a id="bestehender-la1-lauf-und-neue-testkampagne"></a>

## Historischer LA1-Lauf und getrennte spätere Kampagnen

Im eingefrorenen LA1-Bestand bleibt P3s Originalrequest gesendet mit
unbekanntem Ausgang. Ein additiver Audit löst diese Sperre nicht. P5 bleibt
im dokumentierten HOLD nach einem Korrekturversuch. Die ursprünglichen
Bestände werden weder ersetzt noch als nachträglich bestanden umbenannt.

Ein später ausdrücklich beauftragter, getrennter Qualifikationslauf mit
neuen regulären Figuren wäre eine **neue** Testkampagne. Er wäre kein
Nachweis, dass der alte P3-Request wiederhergestellt oder der frühere LA1-Lauf
abgeschlossen wurde. Eine solche Kampagne benötigt eine eigene endliche
Freigabe und darf keine alten Budgets erneuern.

Stand 16. Oktober 2026 (Belegpräzisierung, keine neue Reifeaussage): die
private offline Generalprobe (nicht Teil dieser öffentlichen Kopie) belegt
inzwischen fünf reguläre Figurenannahmen, zwei echte Abschnitte mit
organischer A→B-Savekontinuität über den Store, einen echten
Prozessneustart und einen getrennt ausgewiesenen Lobby-Wiederaufruf nach
Abschnittsabschluss (0 Spielleitungs-, 5 Personaanfragen) — weiterhin
ausschließlich mit skriptierten Antworten, kein Livebeleg. Ein ebenfalls
privater `--check`/`--dry-run`/`--execute`-Qualifikationstreiber orchestriert
denselben Produktweg über echte Adapterfactories; `--execute` bleibt ohne
eine gesondert gebundene, nach dem bedingten Feature-Push erteilte Freigabe
abgewiesen. Kein bezahlter Lauf, keine neue Kampagne wurde dadurch
eröffnet.

## Reifeaussagen

Der beschriebene lokale Beta-Umfang ist kein allgemeiner Stable-Release.
Eine bestandene Offlineprüfung belegt ihren jeweiligen Umfang, nicht
automatische Live-Reife, plattformweite Regeltreue, LAN-Spielbarkeit oder
vollständige Backup-/Restore-Fähigkeit. Maßgeblich für die aktuelle Etappe
sind die Gegenwartsübersicht und ihre geprüften Originalbelege; historische
Teilabnahmen erweitern diesen Umfang nicht automatisch.

Historische Details: [Betriebsdokumentation](mmo-sim.md), insbesondere der
[LA1-Abschnitt](mmo-sim.md#la1--live-alltagsabnahme-2026-10-13).

## Showcase-Szene — Herkunft

Die beiden Szenen in der
[README](../README.md#so-spielt-sich-das-ein-zugriff-im-terminal) sind keine
ausgedachten Beispiele, sondern **Replays unveränderter Originaltexte** aus
echten Playtest-Läufen. Herkunft und Prüfsummen zum Nachvollziehen:

**Szene 1 — Crew-Zugriff (Fünfer, PHASE Konflikt).** Automatisierter
Fünf-Personas-Playtest, Episode 12, Mission 11.

- Quelldatei:
  `internal/qa/evidence/2026-playtests/2026-06-17-0939-coreops-split-merge/_transkript.md`
- Datei-SHA256: `47dc2d47626dd2a1e4c34920436dc458ef298539a50a20d227ab4c2acde1981a`
- Lauf-Typ: SL-Engine `zeitriss-v426-uncut` über OWUI-RAG, Mitspieler
  `anthropic/claude-sonnet-4.6` (fünf Personas), Harness-Protokoll in
  `turns.jsonl`. **Kein Live-Mitschnitt des Terminal-Clients** (`scripts/mmo_sim.py`),
  sondern derselbe automatisierte Persona-Playtest-Zugang wie unter
  [`docs/testing.md`](testing.md) beschrieben.
- Ehrlicher Vorbehalt: Der Lauf startete auf einem High-Level-Fixture-Save; die
  Engine flaggte dessen Prestige-Werte (Lvl 901–933) selbst als über dem
  Regel-Cap (Lvl 100). Diese Zahlen stehen unverändert im gezeigten HUD. Das
  `_summary.json` des Gesamtlaufs endet auf `verdict: FAIL` — die Fehler
  betreffen spätere Split/Merge-Save-Phasen, nicht die hier gezeigte frühe
  Zugriffsszene (M1-5er).
- Gezeigter Ausschnitt: Zeilen 518–612 (Crew-Abstimmung, HUD aller fünf
  Charaktere, Hinterhof-Zugriff mit zwei Proben, Café-Festnahme mit explodierendem
  Würfel; zwei parallele Schauplätze, in der Quelle als „gleichzeitig" markiert).
  Jede Auslassung mit `[…]`.

**Szene 2 — Solo-Feuergefecht (PHASE Konflikt).** Manueller Solo-Chat-Playtest
(Sonnet-SL), Episode 1, Mission 2, Rostock 17.10.1973.

- Quelldatei:
  `internal/qa/evidence/2026-playtests/2026-04-19-episode1-mini-solo-sarah-v3/chat5-mission3.md`
- Datei-SHA256: `55f8eaaf4b4a1b23c6d1270121fbc1573b08867f5febd10354d914c570a6c46a`
- Gezeigter Ausschnitt: Zeilen 593–702 (HUD, Initiative aller drei Beteiligten,
  Fernkampf mit explodierendem Würfel, LP-Schaden, Wollpullovers Flucht mit dem
  Dokument, Magazin-Zählung, ein Sprint-MISS mit Konsequenz). Jede Auslassung
  mit `[…]`.

Beide Szenen sind über den unveränderten Produkt-Renderer
`mmo_sim.ui.rendering.render_for_terminal` dargestellt; die README zeigt den
Terminalausdruck in lesbarer Textform (ANSI-Attribute entfallen in Markdown).
Für die README wurden die Texte nur gekürzt (jede Auslassung mit `[…]` markiert),
nicht umformuliert. Ehrlich getrennt: Beide Szenen sind Playtests — Szene 1 ein
automatisierter Fünf-Personas-Lauf (OWUI-RAG), Szene 2 ein manueller
Solo-Chat-Playtest. Beide authentisch, beide über denselben Produkt-Renderer
dargestellt, aber keines ein Live-Mitschnitt des Terminal-Clients.

Technische Randnotiz: Der Renderer setzt `**fett**` und `_kursiv_` in
Terminalattribute um; einzelne `*…*` bleiben als Zeichen stehen. Für die README
wurden bewusst Textfenster ohne solche Stellen gewählt, damit der Ausschnitt den
tatsächlichen Terminalausdruck zeigt und keine Markup-Reste.
