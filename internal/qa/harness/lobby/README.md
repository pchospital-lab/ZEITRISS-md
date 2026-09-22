# internal/qa/harness/lobby/ — Lobby/Tisch-Protokoll-Durchstich (offline, P1)

Kleinster reviewbarer **Offline**-Durchstich der Lobby-/Tisch-Ebene ueber dem
bestehenden Abschnitts-Baustein (`faithful_section.py`, unangetastet). Kein
Dauerprozess, kein Netz, kein echter Modell-/KI-SL-/OWUI-/OpenRouter-Call. Baut
NICHT auf einem Aufruf-Roster (`--players ...`) auf, sondern leitet Gruppe/Leader
aus protokollierten Offer-/Consent-Logs ab.

Quellen: `PLAN-P1.md`, `PLAN-CRITIC.md`, `PLAN-NACHBESSERUNG.md`,
`PLAN-CRITIC-NB.md` (siehe `zeitriss-p1-2026-09-21/` bzw.
`zeitriss-p1-nachbesserung-2026-09-21/` im Worker-Workspace),
`COORDINATION-MODEL-FROZEN.md`.

**Stand:** P1-Restkorrektur (2026-09-22) nach einer VIERTEN unabhaengigen
Re-Review (`review_p_boundaries.py`, 6/6; `review_p_admission_matrix.py`,
`premature_admission_scenarios=0`/`premature_leader_sends=0`) — behebt vier
verbleibende Autoritaets-/Uebergangsgrenzen gegenueber dem vorherigen
Konsistenz-Nachzug-Stand: (P1) ein offener Abschluss-Auftrag bindet seine
Mitglieder jetzt auch GEGEN NEUE Tische, nicht nur gegen einen zweiten
Abschnitt auf demselben Tisch (`_member_bound_by_open_order`); (P2) strikte
Section-ID-Grammatik + `__final`-Identitaetspruefung gegen `table_id` UND
`section_id`; (P3) der Fence-Strip vor der Marker-Suche erfasst JEDEN
Fence-Block, nicht nur ```` ```json ````; (P4) der Current-Save-Ref ist an
eine pro `run_dir` stabile `run_id` gebunden. Diese Datei korrigiert dabei
auch zwei fruehere Falschaussagen zum Save-Publikationsvertrag (s. R1) — der
Code nutzte den Current-Save-Ref bereits vorher als alleinige Autoritaet,
NIE ein "hoechste Version"-Read. `review_k_publication.py` (5/5),
`review_k_fault_matrix.py` (0/0/0), `review_ak_invariants.py` (8/8),
`review_nb_edges.py` (9/9) und `review_countertests.py` (10/10) bleiben
weiterhin gruen. Diese Datei beschreibt NUR den tatsaechlich in diesem Slice
erreichten Stand; ein passender `.turn()`-Vertrag (s. u.) ist kein Nachweis
einer Live-Integration mit einem echten SL-Adapter oder echten Personas.

## Was ist gebaut, was ist Stub

| Datei | Real umgesetzt | Stub/Fixture |
|---|---|---|
| `rooms.py` | Lobby/Tisch-Membership, Nachrichtenkanaele (Lobby/Tisch/Leader-SL), Sichtfilter, Leader-only-Send, Chrononaut-Lock (inkl. `join_more`), Tisch-Status `closed`, Completion-Idempotenz + Abschluss-Journal, Save/State-Identitaetspruefung, persistente aktuelle Saves — echte Logik, dateibasiert | — |
| `sl_stub.py` | Contract (Rueckgabeform identisch zu `SLSession.turn()`) | **Kompletter Inhalt ist Fixture** — liest nur vorher abgelegte, deutlich als SIMULIERT markierte Texte, macht NIE einen echten Aufruf |
| `section.py` | Transport-/Ablauflogik (Anker/Gaeste/Ernte/Marker-Gate/Completion) | Ruft `sl_stub.SLStub`, nicht `agent_mp.sl_client.SLSession`; Leader-/Gast-/Debrief-Texte kommen aus `fixtures/leader_messages.json` (SIMULIERT, generisch), nicht aus zur Laufzeit vom Controller formulierten Persona-O-Toenen |
| `fixtures/*` | — | Alles hier ist **SIMULIERT/FIXTURE**, deutlich markiert (`_fixture_note`/`fixture_note`-Felder). Kein „natuerliches Verhalten" behauptet. |

Wiederverwendet (nicht veraendert): `agent_mp/saves.py` (`extract_all_saves`,
`single_character_count`, `block_char_id`), `persona_state.py` (`load_state`,
`update_state`, `save_state`, Anti-Stacking-Gate). Der SL-Contract von
`agent_mp/sl_client.SLSession.turn()` wurde als Fixture-Stub NACHGEBILDET, nicht
importiert/aufgerufen. Ein passender `.turn()`-Rueckgabevertrag beweist NICHT,
dass Persona-Entscheidungen, echte Abschnittsausfuehrung oder Abschlussfreigabe
bereits mit einem echten Adapter verbunden sind — das bleibt eine separate,
spaeter freizugebende Integration.

## Adapter-Naht zum spaeteren echten SL-Adapter

`section.py` kennt nur den Rueckgabevertrag `{content, usage, sources, latency_s,
chat_id}` und ruft `<irgendein Objekt>.turn(turn_idx, text)`. Aktuell wird dafuer
`sl_stub.SLStub(fixture_path)` konstruiert (Fixture-Text, kein Netz). Um spaeter
echt zu verbinden: in `section.run_section(...)`-Aufrufern die Konstruktion durch
`agent_mp.sl_client.new_sl_session(run_dir)` ersetzen — der Rest von `section.py`
(Turn-Reihenfolge, Save-Ernte via `agent_mp/saves.py`) bleibt unveraendert, weil
beide Seiten denselben Vertrag erfuellen. **Nichts in diesem Slice ist live
verbunden.**

**Korrektur einer frueheren Ueberzeichnung (NB-A/R7):** ein identischer
Rueckgabevertrag allein beweist NICHT, dass ein echter Adapter den AUSGEHENDEN
`user_text` (inkl. des von `section.run_section` eingebetteten Save-Blocks, s.
u.) unveraendert an die eigentliche SL weiterreicht — reale Transportgrenzen
(Kontext-Kappung, Nachrichtenumformung) sind eine SEPARATE, hier NICHT geprueft
Eigenschaft eines kuenftigen echten Adapters, nicht dieses Stubs. Der
"Stub-einfach-tauschen"-Vertrag gilt nur dann unveraendert, wenn der echte
Adapter denselben Text-Empfangsvertrag erfuellt (Save als Teil von `user_text`
ankommt); nutzt er stattdessen eine STRUKTURIERTE Payload-API, muss die
Empfangsassertion (s. `SLStub.calls[i]['user_text']`, von der externen
Re-Review als Test 01 geprueft) angepasst — NICHT einfach umgangen — werden.

## Bekannter Pfad-Fix am wiederverwendeten `persona_state.py` (kein Modul-Edit)

`persona_state.py` ist FROZEN und wird hier nicht editiert. Sein
Default-Schema-Pfad (`_SCHEMA_PATH`, modulintern fest verdrahtet) zeigt auf
`<harness>/../personas/persona-state.schema.json` — diese Datei existiert in
diesem Worktree nicht. Die Schema-Datei liegt tatsaechlich unter
`internal/qa/fixtures/persona-state.schema.json` (git-historisch bestaetigt: dort
wurde sie im Commit `25b6de5d` eingefuehrt, nicht unter `personas/`). Ohne Fix
wirft jeder `persona_state.save_state()`-Aufruf `FileNotFoundError`. `rooms.py`
korrigiert deshalb zur LAUFZEIT nur den vom Modul selbst nachgeschlagenen Pfad
(`ps._SCHEMA_PATH = <realer Pfad>`, Cache geleert) — der Modulcode bleibt
unangetastet. Das ist ein vorgefundener Repo-Zustand, kein Artefakt dieses Slices.

## R5 — Persona-Identitaet: Enum -> Pattern (begruendete Freeze-Ausnahme)

`internal/qa/fixtures/persona-state.schema.json` beschraenkte `persona_key`
urspruenglich per `enum` auf exakt die fuenf historischen Schluessel (`cqb`,
`sniper`, `face`, `pyro`, `tech`). Die Acht-Personen-Lobby (`fixtures/
personas.json`) enthaelt aber drei weitere Fixtures (`medic`, `scout`, `ghost`).
Die Fuenfer-Grenze gehoert auf AKTIVE TISCHPLAETZE (`TABLE_MAX_SIZE = 5`), nicht
auf Persona-IDENTITAET. Deshalb wurde `persona_key` von `enum` auf ein Pattern
(`^[a-z][a-z0-9_]*$`) umgestellt — Validierung bleibt vollstaendig aktiv (kein
`additionalProperties`-Bypass, kein Abschalten), die fuenf historischen Keys
bleiben unveraendert gueltig. `test_8_medic_extra_persona_full_lifecycle` fuehrt
`medic` (mit echten Fixtures: `fixtures/persona_states/medic.json`,
`fixtures/saves/medic.json`, `fixtures/sl_canned/medic_solo.json`) durch den
vollen Offline-Lifecycle (Lobby -> Solo-Tisch -> Abschluss -> Save/State ->
Lobby).

## R1 — Persoenliche Save-Rueckkehr + Identitaetspruefung

`rooms.complete_section()` legt jeden geernteten v7-Block nach erfolgreicher
Validierung VERBATIM (reines `json.dumps`, kein Wrapperfeld) unter
`run_dir/current_saves/<persona_key>.json` ab; `rooms.load_current_save(run_dir,
persona_key)` liest ihn zurueck.

**Teilschreibsichere Veroeffentlichung (C2/Auflage 2, Test 05):** zusaetzlich zur
Direktdatei wird JEDE Veroeffentlichung auch atomar (temp+rename) unter
`current_saves/<persona_key>__versions/<seq>.json` versioniert. Reihenfolge pro
Mitglied: ERST die Direktdatei schreiben (das ist der von Test 05 abgefangene
Riss-Punkt — reisst dieser Schreibvorgang ab, wird der Versions-Commit fuer
diesen Aufruf gar nicht erst versucht), DANACH der atomare Versions-Commit.
Die Completion-Guard-Datei referenziert `save_path` (die MASZGEBLICHE
Versionsdatei, relativ zu `run_dir`), `current_save_path` (die Direktdatei) und
`save_sha256` (Hash der Versionsdatei — konsistent mit `load_current_save`).

**Tatsaechlicher Vertrag — State ist die maszgebliche Veroeffentlichungsautoritaet
(Restkorrektur 2026-09-22, ersetzt zwei vorherige Falschaussagen dieser
Datei):** `load_current_save` liest **NICHT** die "hoechste gueltige Version"
und der Persona-State enthaelt **NICHT** "keinen Zeiger" — beide fruehere
Aussagen widersprachen dem tatsaechlichen Code bereits vor dieser Korrektur.
Der EINZIGE gueltige Pfad: `ps.save_state` (die Persona-State-Fortschreibung,
atomar) ist der EINZIGE Veroeffentlichungs-Flip; das State-Objekt traegt dabei
selbst den Current-Save-Ref (`current_save_version`, additives Feld) —
`load_current_save` liest GENAU die darin referenzierte Version, eine
verwaiste (nicht referenzierte) Versionsdatei wird NIE gelesen, auch wenn sie
numerisch hoeher waere. Reihenfolge pro Mitglied: Direktdatei -> atomarer
Versions-Commit -> ERST DANACH `ps.update_state`/`ps.save_state` (Konsistenzplan
Frage 3, Test 05) — reisst der Direkt-Save-Schreibvorgang ab, bleiben Save UND
State fuer dieses Mitglied BEIDE unveraendert (kein "alter Save + bereits
fortgeschriebener State").

**Speicherbereichsbindung — `run_id` (P4/K1-Nachzug, Restkorrektur
2026-09-22):** der Current-Save-Ref ist seit dieser Korrektur kein bloszes
`{seq}` mehr, sondern `{"run_id": <str>, "seq": <int>}`. Jedes `run_dir`
erhaelt bei `Lobby.__init__` eine stabile, einmalig erzeugte `run_id`
(`run_dir/run_id.json`, JSON-**Objekt**, niemals ein bare String/Liste — sonst
bricht der generische `rglob('*.json')`+`.get('v')`-Scan der Gegenprobe
`review_countertests.py::test_01` mit `AttributeError`). `load_current_save`
loest eine Referenz NUR auf, wenn `ref["run_id"]` mit der `run_id` des
uebergebenen `run_dir` uebereinstimmt — eine Referenz aus einem ANDEREN
`run_dir` (selbst bei rein lokal wiederverwendeter, identischer Sequenznummer)
deutet dort NIE einen fremden Save um, sondern loest zu `None` auf. Derselbe
`run_dir` erhaelt bei jeder erneuten `Lobby(run_dir)`-Instanziierung dieselbe
`run_id` zurueck (Kontrolle 06: nur `states_dir` wechselt, `run_dir` bleibt
gleich -> Referenz bleibt aufloesbar). Der Recovery-Guard-Vergleich
(`expected_prev_ref`/`actual_prev_ref` in `_resume_and_finalize`) vergleicht
konsistent dasselbe Objektformat (Dict-Gleichheit).

**Auftragsbindung ueber den physischen Lock hinaus (P1/K2-Nachzug,
Restkorrektur 2026-09-22):** ein noch OFFENER Abschluss-Auftrag
(`completion/<section>__plan.json` OHNE eigenes `__final`) bindet seine
Chrononaut-IDs exklusiv — `create_table_from_offer_log` (Aufnahme an einem
NEUEN Tisch) lehnt ab (`(None, derivation)`, keine Ausnahme; bestehende
Konvention), wenn ein angefragtes Mitglied so gebunden ist
(`_member_bound_by_open_order`), UNABHAENGIG davon, ob sein physischer
Chrononaut-Lock (`locks.json`) bereits freigegeben wurde — Locks werden pro
Mitglied bereits VOR `__final` freigegeben (s. R3/R4 unten), der Auftrag
selbst bindet laenger. Nach gueltigem `__final` ist der Auftrag geschlossen
und bindet nicht mehr — freie Neugruppierung ist dann wieder moeglich.

**Grenzen:** keine OS-Powerloss-Garantie (nur Python-Ausnahmen/gezielte
Schreibunterbrechungen werden geprueft, kein Kernel-Crash-Mid-`write()`), keine
Mehrprozess-/Nebenlaeufigkeitsgarantie (sequenzielle Python-Fehlerinjektion,
kein echter Parallelzugriff zweier Prozesse auf dieselbe `run_dir`).

**Identitaetspruefung** (VOR jedem Write, in derselben Vorab-Validierungsschleife
wie der bestehende `missing`-Check — nicht in der Schreibschleife, damit kein
Mitglied geschrieben wird, waehrend ein spaeteres im selben Aufruf noch als
Mismatch erkannt werden koennte): der fuer `pk` geladene `persona_state` muss
`persona_key == pk` UND `plays_char.character_id == table.chrononaut_ids[pk]`
erfuellen. Bei Mismatch: `pk` gilt als `missing`, kein Write fuer IRGENDEIN
Mitglied dieses Aufrufs, letzte gueltige Save-/State-Zuordnung bleibt erhalten.

## R2 — Abschluss-Marker (zugeordnetes Ereignis, kein Substring-/Heuristik-Check)

Das Abschluss-Gate lebt in `section.run_section` (NICHT im
`complete_section`-Core — `complete_section` bleibt eine interne, NACHGELAGERTE
Persistenz-/Finalisierungsstufe HINTER dem hier bereits validierten Ereignis;
`complete_section` wird auch direkt mit gueltigen Saves aufgerufen — von
Gegenproben UND von Test 09 — und muss dort ohne Marker-Konzept erfolgreich
sein).

**NB-B-Korrektur:** vor der Marker-Suche werden NUR die Zeilen des
Debrief-Texts betrachtet, die AUSSERHALB eines Fence-Blocks liegen
(`section._top_level_lines`) — ein Marker-Token, der nur als STRING-WERT
innerhalb eines importierten/geernteten Saves auftaucht, zaehlt NICHT.

**Kontrollform — Ereignisgrammatik + Fence-Zustandsmaschine (P3/K3-Nachzug,
Restkorrektur 2026-09-22):** der fruehere `section._JSON_BLOCK_RE`-Regex
(nicht-greedy ```` ```.*?``` ````, zeilenuebergreifend) wurde durch eine
zeilenbasierte Zustandsmaschine ersetzt (`section._top_level_lines`, mit
`section._fence_delimiter` als gemeinsamer Delimiter-Erkennung fuer Oeffnen
UND Schliessen). Grund: der Regex konnte sowohl Marker faelschlich
FREILEGEN (ein bis Textende offener Fence-Block wurde gar nicht erst
gepaart, ```` ~~~ ````-Fences wurden vom Regex gar nicht erkannt, ein
verschachtelter kuerzerer innerer Delimiter paarte faelschlich VOR dem
laengeren aeusseren) als auch einen echten Top-Level-Marker faelschlich
VERDECKEN (Inline-Backticks in einer Prosazeile vor dem Marker liessen den
Regex ueber die Zeilengrenze hinweg bis zu einem spaeteren Fence-Ende
paaren). Die neue Kontrollform (CommonMark-nah, minimal):
  - Delimiterzeile = Zeile, die nach optional <=3 fuehrenden Leerzeichen mit
    einem Lauf von >=3 GLEICHEN Fence-Zeichen (`` ` `` oder `~`) BEGINNT;
    Text vor dem Lauf (Inline-Backticks in Prosa) macht die Zeile KEINE
    Delimiterzeile.
  - Oeffnen (ausserhalb eines Blocks): die erste Delimiterzeile oeffnet;
    Zeichenart und Lauflaenge werden gemerkt.
  - Schliessen (innerhalb eines Blocks): nur eine Delimiterzeile mit
    GLEICHER Zeichenart, Laenge >= der Oeffnungslaenge UND leerem
    Info-String schliesst — ein kuerzerer, andersartiger oder
    Info-tragender Delimiter schliesst NICHT (laengerer aeusserer Block
    bleibt offen).
  - Bleibt ein Block bis Textende offen, werden alle seine Zeilen
    verworfen — kein Marker wird freigelegt.
Die Marker-Suche (`section._completion_marker_matches`) iteriert ueber die
von `_top_level_lines` gelieferte Zeilenliste, NIE ueber einen wieder
zusammengefuegten String. Die Save-Ernte (`save_lib.extract_all_saves`)
laeuft weiterhin UNVERAENDERT auf dem Originaltext (nicht auf den
Top-Level-Zeilen) und ist von dieser Erweiterung strukturell unberuehrt.

**Konsistenz-Nachzug (2026-09-21, Konsistenzplan Frage 1, Test 02/03):** der
gefundene Marker muss danach (ggf. nach fuehrendem Whitespace) eine EIGENE
Zeile BEGINNEN — unmittelbar davor auf derselben Zeile darf KEIN weiterer Text
stehen. Das schliesst Negation (`"NICHT " + Marker`) und Zitat (`"> " + Marker`)
aus, ohne natuerlichsprachliche Negationswoerter zu erraten (keine zweite
Spielengine/Heuristik). Traegt der zeilen-beginnende Marker
`table_id=`/`section_id=`-Qualifier (auf derselben Zeile), muessen sie zu
`table.table_id` bzw. der aktuell verarbeiteten `section_id` passen — sonst
kein Abschluss (Fremdtisch-/-abschnitt-Marker zaehlen nicht). Ein BLANKER
Marker (keine Qualifier, eigenstaendige Zeile) gilt fuer die AKTUELLE Session
(der Stub IST die SL genau dieses Tisches) — so verwenden ihn alle
bestehenden Erfolgs-Fixtures (`section._completion_marker_matches`). ALLE
Vorkommen des Markers in den Top-Level-Zeilen werden geprueft (nicht nur das
erste) — ein FRUEHERES ungueltiges Vorkommen (kein Zeilenbeginn oder falsche
Qualifier) bricht die Suche nicht ab, wenn ein SPAETERES gueltiges Vorkommen
folgt; das erste GUELTIGE Vorkommen zaehlt. KEINE Heuristik ueber
Save-Wert-Praesenz/-Aenderung (ein gueltiger, wertneutraler HQ-Abschnitt darf
keinen erfundenen Fortschritt brauchen, und ein taeuschend gueltig aussehendes
Save-Echo ohne echten neuen Abschluss darf nicht als Erfolg durchrutschen).
Alle 6 Erfolgs-Fixtures unter `fixtures/sl_canned/` (`table1_solo.json`,
`table2_pair.json`, `table5_full.json`, `medic_solo.json`) UND die 2
Negativ-Fixtures, die trotzdem bis zur Save-Zuordnungspruefung durchlaufen
sollen (`table2_missing_save.json`, `table2_wrong_char_id.json`), tragen den
(fuer die jeweils aktuelle Session gueltigen) Marker als eigenstaendige Zeile
im Debrief-Turn — sie scheitern dadurch am RICHTIGEN Grund (fehlender/falsch
zugeordneter Save), nicht am Marker-Gate
(`test_10_nb_b_marker_qualifiers_and_json_stripping` prueft alle 6+2
Fixtures explizit; `test_13_nb_b_negation_quote_marker_and_cross_table_final`
prueft Negation/Zitat + Mehrfachvorkommen).

Zusaetzlich prueft `complete_section` selbst je Block `v == 7` (deckt den
direkten API-Einstieg ab, der das Marker-Gate umgeht).

## R3 — Teilschreib-Idempotenz (Abschluss-Auftrag + resumierbare Finalisierung)

**Korrektur einer frueheren Falschaussage in dieser Datei:** Das
Completion-Guard-„Alles-oder-nichts"-Muster allein deckte den Teilschreibfall
NICHT ab — bricht der Prozess zwischen dem State-Write fuer Mitglied A und dem
fuer Mitglied B ab, erkannte ein erneuter Aufruf das NICHT als
`already_completed` und schrieb A beim Retry ein zweites Mal fort (doppelter
Rundenfortschritt). Das ist behoben: `complete_section` schreibt VOR der
Schreibschleife einmalig einen persistenten Abschluss-Auftrag
`completion/<section_id>__plan.json = {table_id, members: {persona_key:
{round_no, save}}}` (existiert er bereits fuer DIESEN Tisch, wird er
UNVERAENDERT wiederverwendet, nicht neu berechnet; gehoert er einem ANDEREN
`table_id`, ist das eine Kollision, s. NB-B/C-Korrektur unten). Die
Schreibschleife ueberspringt jedes Mitglied mit bereits vorhandener
Guard-Datei (kein zweiter Rundenschritt); die uebrigen erhalten
`members_plan[pk]["round_no"]`/`["save"]` (die GEPINNTE Ernte) statt eines
frisch berechneten `rounds_played + 1`/des Funktionsarguments.
`persona_state`s eigenes Anti-Stacking-Gate bleibt eine ZWEITE, unabhaengige
Sicherung.

**Konsistenz-Nachzug (2026-09-21, NB-C/Test 08 — Ernte-Pinning):** der
Abschluss-Auftrag bindet nicht mehr nur `round_no`, sondern je Mitglied den
VOLLEN geernteten v7-Block (nicht nur einen Hash). Ein Retry mit ABWEICHENDER
Ernte (anderes `save_id` o. ae.) nutzt fuer noch offene Mitglieder IMMER die
gepinnte Ernte aus dem Auftrag, NIE das (ggf. abweichende) Funktionsargument
`harvested_saves` — kein Mischen zweier Ernten unter demselben Abschluss-
Ereignis. Die Validierung (v==7/Identitaet/Missing) laeuft bei einem Retry
ebenfalls gegen die gepinnte Ernte, nicht gegen das Argument.

**NB-C-Korrektur (C1/Auflage 1+4):** `already_completed` gilt NICHT mehr schon
bei vollstaendigen Mitglieder-Guards, sondern EINZIG bei existierendem
`completion/<section_id>__final.json` MIT ZUM AUFRUFENDEN TISCH PASSENDER
`table_id` **UND** PASSENDER `section_id` (P2/K2-Nachzug, Restkorrektur
2026-09-22 — der `__final`-Inhalt fuehrt beides; ein table_id-Treffer allein
reicht nicht mehr, kein "Erben" einer fremden/aehnlich benannten Section
ueber eine kollidierende Dateinamen-Normalisierung). Grund: die
Schreibschleife kann vollstaendig durchlaufen (alle Guards geschrieben), aber
die NACHGELAGERTE Finalisierung (Lock-Freigabe + `__final` + `status=closed`)
danach abbrechen — ein Retry, der das an den vorhandenen Guards allein
festmacht, wuerde die Finalisierung nie nachholen (Test 04). Die
vollstaendige Reihenfolge in `complete_section`:
[0] P2/Auflage 3 (Restkorrektur 2026-09-22): `section_id` muss der strikten
Grammatik `[A-Za-z0-9_-]` genuegen — der Reject sitzt in `complete_section`
SELBST (nicht nur in `section.run_section`), damit auch ein DIREKTER
`complete_section`-Aufruf (der `run_section` umgeht) ein unzulaessiges
`section_id` frueh kontrolliert ablehnt (`success=False`, keine Datei). Unter
dieser Grammatik kann `_safe_component` (nur `/` -> `_`) keine zwei
zulaessigen `section_id`s mehr auf denselben Dateinamen abbilden.
[1] `__final`-basierte `already_completed`-/Kollisions-Pruefung (`table_id`
UND `section_id` im `__final`-Inhalt muessen zum aufrufenden Tisch/zur
angefragten Section passen — ein FREMDER Tisch mit gleicher `section_id`,
oder ein `__final` mit abweichender `section_id`, wird hart abgelehnt,
`success=False`, kein Write, s. NB-B/C-Korrektur unten), [2] existiert noch
kein `__final`, aber bereits ein Abschluss-Auftrag (`__plan.json`) fuer
(table, section) — Recovery: fremder `table_id` im Auftrag -> ebenfalls
Kollision; eigener `table_id` -> Schreibschleife/Finalisierung werden
nachgeholt, [3] weder `__final` noch `__plan` fuer diese section: reload-
basierte `closed`-/Lock-Pruefung auf dem PERSISTIERTEN Stand (NB-D/R4+R6,
s. u.) — ein per ANDERER section_id bereits geschlossener Tisch eroeffnet
keinen neuen Zweig, [4] beim ERSTEN Versuch: Missing-/Identitaets-/`v==7`-
Validierung GEGEN DAS ARGUMENT, danach Pinnen des Abschluss-Auftrags. Die
Schreibschleife (Pro-Mitglied-Guard-Skip, C2-Current-Save-Veroeffentlichung
s. R1) und die resumierbare Finalisierung laufen fuer den ersten Versuch UND
jeden Retry ueber denselben Code-Pfad (`_resume_and_finalize`): Locks ALLER
Mitglieder freigeben (`release_chrononaut` ist selbst idempotent, s. R4) ->
**`__final.json` schreiben** -> **DANACH** `status="closed"` auf dem NEU
GELADENEN, persistierten Tisch setzen (Konsistenzplan Frage 4 — NICHT mehr
closed-vor-final; verhindert Totalverlust von `sl_log`/`table_messages`, s.
R7-Abschnitt unten). Ein Retry mit vorhandenen Guards, aber fehlendem
`__final`, holt GENAU diesen letzten Schritt nach, ohne die Schreibschleife
erneut auszufuehren (kein doppelter Rundenfortschritt). `test_lobby_tables.py`s
Guard-Zaehlung schliesst `__final.json` (wie `__plan.json`) explizit von der
Pro-Mitglied-Zaehlung aus.

**Auftragsbindung gegen NEUE Tische (P1/K2-Nachzug, Restkorrektur
2026-09-22):** die obige Bindung galt bisher nur GEGEN EINEN ZWEITEN
Abschnitt AUF DEMSELBEN Tisch. Locks werden pro Mitglied aber bereits VOR
`__final` freigegeben (Schritt [5] oben) — ein Mitglied, dessen Lock im
Cleanup deshalb schon fehlt, konnte bislang trotz noch offenem
urspruenglichen Auftrag an einem KOMPLETT NEUEN Tisch aufgenommen werden.
Behoben: `create_table_from_offer_log` (Aufnahme) prueft zusaetzlich zum
Chrononaut-Lock `_member_bound_by_open_order(run_dir, chrononaut_id)` — ein
angefragtes Mitglied, das in IRGENDEINEM offenen Abschluss-Auftrag
(`__plan.json` ohne eigenes `__final`, beliebiger Tisch) gebunden ist, fuehrt
zur bestehenden Ablehnungs-Konvention `(None, derivation)` (keine Ausnahme).
Die Chrononaut-IDs eines offenen Plans werden ueber
`Table.load(run_dir, plan_data['table_id']).chrononaut_ids` abgeleitet — der
referenzierte Tisch bleibt bis zum Final-Write ladbar. Nach gueltigem
`__final` ist der Auftrag geschlossen und bindet nicht mehr — freie
Neugruppierung bleibt erhalten (bestehende Positivtests `test_11`/`test_12`).

**NB-C-Korrektur (Konsistenzplan Frage 3, Test 05 — Save-/State-Reihenfolge):**
pro Mitglied wird `ps.save_state` jetzt ERST NACH dem vollstaendigen
Save-Commit aufgerufen (Direktdatei -> atomarer Versions-Commit -> DANACH
`ps.update_state`/`ps.save_state`). Reisst der Direkt-Save-Schreibvorgang ab,
bleiben Save UND State fuer dieses Mitglied UNVERAENDERT (kein "alter Save +
bereits fortgeschriebener State" mehr, s. R1 unten).

## R4 — Chrononaut-Locks + Tischidentitaet

- `Table.status` wird nach einem erfolgreichen Abschluss auf `"closed"`
  gesetzt und persistiert. **NB-D-Korrektur (D1/R4+R6, Test 06):** `submit_to_sl`,
  `post_table_message` UND `complete_section` pruefen VOR jeder Mutation den
  PERSISTIERTEN Tischstatus (`Table.load(run_dir, table_id).status`, NICHT das
  ggf. veraltete in-memory `table.status`) sowie die Lock-Eigentuemerschaft
  aller Mitglieder gegen den aktuellen `locks.json`-Stand — ein vor Abschluss
  geladenes ("stale") Table-Handle darf einen inzwischen persistiert
  geschlossenen Tisch weder weiterbespielen noch erneut abschliessen. Der
  normale `run_section`-Ablauf (aktive Tische, mehrere `submit_to_sl`-Aufrufe)
  bleibt davon unberuehrt, weil ein aktiver Tisch waehrend seines eigenen Laufs
  denselben persistierten Status wie sein in-memory-Objekt hat.
  **Reihenfolge in `complete_section`:** die `__final`-basierte
  `already_completed`-Pruefung geht der `closed`-/Lock-Pruefung voraus — sonst
  koennte ein Tisch seinen eigenen (inzwischen geschlossenen) Doppelabschluss
  nicht mehr idempotent beantworten (s. R3). **Reihenfolge in `submit_to_sl`:**
  die Leader-Identitaetspruefung geht der `closed`-/Lock-Pruefung voraus, damit
  ein Nicht-Leader weiterhin `LeaderOnlySendError` erhaelt, unabhaengig vom
  Tisch-Status.
- **NB-D-Korrektur (D2+D3, Tests 07+08): `Table.join_more` ist in diesem
  Slice AUSDRUECKLICH NICHT unterstuetzt** — die Methode MUTIERT NIE
  (kein Ersatz-Tisch/-Spieler, kein Teil-Zustand) und liefert IMMER `False`
  (Signatur `join_more(persona_key, chrononaut_id) -> bool` unveraendert). Sie
  prueft weiterhin (nur zur Nachvollziehbarkeit des Ablehnungsgrunds, nie als
  Zulassungspfad) den persistierten Tischstatus, Tisch-Groesse, Duplikat und
  fremde Chrononaut-Locks — bleibt aber selbst dann bei `False`, wenn keiner
  dieser Gruende zutrifft, weil in diesem Slice KEIN legitimierender
  Konsens-/Offer-Beleg fuer einen ueber die urspruengliche Offer hinausgehenden
  Beitritt existiert. Bewusste, spaetere Erweiterung (nicht Teil dieses Slices).
- `Lobby.release_chrononaut(chrononaut_id, expected_table_id)` loescht die
  Sperre NUR, wenn sie tatsaechlich `expected_table_id` gehoert — ein alter/
  fremder Tisch kann die Sperre eines inzwischen aktiven anderen Tisches nicht
  mehr freigeben, UND ist dadurch selbst idempotent (mehrfacher Aufruf mit
  demselben `expected_table_id` nach bereits erfolgter Freigabe ist ein
  No-op) — das traegt die resumierbare Finalisierung aus R3 (Test 04).
  **Signaturaenderung:** vorher einargig; die beiden Original-Call-Sites in
  `test_lobby_tables.py` (Kapazitaetstest, kein Lock-Test) wurden entsprechend
  um das jeweilige `table_id` ergaenzt.
- `create_table_from_offer_log` lehnt eine bereits existierende `table_id` ab
  (kein Ueberschreiben von Datei/Verlauf).
- `post_table_message` lehnt Versand an einen geschlossenen Tisch ab
  (Plan-Critic-Auflage 3), analog zu `submit_to_sl` — eigener Repo-Test
  `test_12_nb_d_stale_handle_closed_paths_and_consent_join`. **Konsistenz-
  Nachzug (2026-09-21):** prueft zusaetzlich die Lock-Eigentuemerschaft aller
  Mitglieder (analog `submit_to_sl`, vorher fehlte dieser Check hier —
  Report/Code-Diskrepanz aus REVIEW-AK.md §4).
- **Konsistenz-Nachzug (2026-09-21, Auflage 1 — schmales Crash-Fenster):**
  `submit_to_sl` UND `post_table_message` gaten zusaetzlich auf
  `_table_has_final(run_dir, table_id)` — existiert bereits ein
  `__final`-Marker FUER DIESEN TISCH (auch wenn `status` im schmalen Fenster
  zwischen dem NEU vorgezogenen `__final`-Write und dem NACHFOLGENDEN
  `status=closed`-Persist, s. R3, noch `active` waere), gilt der Tisch als
  gesperrt. Schliesst die vom Plan-Critic benannte Luecke: ohne diesen
  zusaetzlichen Check koennte ein bereits inhaltlich abgeschlossener Tisch in
  genau diesem Fenster noch einmal senden.

## R7 — Nachrichtenkanaele (Lobby/Tisch/Leader-SL) + Herkunftsbeleg

Drei getrennte, persistente Kanaele:

- **Oeffentlicher Lobby-Kanal** (`Lobby.post_lobby_message`/`lobby_messages`):
  nur Lobby-Mitglieder duerfen senden/lesen (`VisibilityError` sonst).
- **Privater Tisch-Absprachekanal** (`rooms.post_table_message`, sichtbar via
  `persona_view(...)["table_messages"]`): nur Tisch-Mitglieder duerfen
  senden/lesen.
- **Leader/SL-Dialog** (`submit_to_sl`, sichtbar via
  `persona_view(...)["sl_log"]`): persistiert sowohl die gesendete
  Leader-Nachricht (`leader_message`) als auch die SL-Antwort (`content`).

**Konsistenz-Nachzug (2026-09-21, Konsistenzplan Frage 5, Test 06):**
`submit_to_sl` UND `post_table_message` mutieren nicht mehr das ggf.
veraltete in-memory `table`-Argument und persistieren es als Voll-Snapshot.
Stattdessen: reload -> append -> persist AUF DEM PERSISTIERTEN Tisch (der neue
`sl_log`-/`table_messages`-Eintrag wird an den frisch geladenen, authoritativen
Stand angehaengt und persistiert); die Aufrufer-Kopie (`table`) wird danach auf
den neuen Stand nachgezogen. Ein sequenziell aelteres ("stale"), aber noch
aktives Table-Handle kann so beim Posten einer eigenen Nachricht den bereits
persistierten Verlauf des JEWEILS ANDEREN Kanals nicht mehr loeschen
(`test_15_nb_d_stale_handle_preserves_sl_log_on_table_message`). `complete_section`s
Finalisierung folgt demselben Prinzip (Auflage 2, kritisch): sie persistiert
den in Schritt [3] NEU GELADENEN Tisch mit `status="closed"`, NIEMALS das
`table`-Funktionsargument selbst — sonst wuerde ein Aufrufer, der sein
in-memory-Objekt nicht synchron gehalten hat, beim Abschluss den gesamten
akkumulierten `sl_log`/`table_messages`-Verlauf mit einem veralteten Snapshot
ueberschreiben (explizit gegen `test_7_message_channels`s drei-Turn-`sl_log`-
Assertion nach vollstaendigem Abschluss verifiziert).

`operator_meta` (Offer-Log-Rohdaten, Dissenter-Gruende, Herleitung) sowie
`chrononaut_ids`/Locks bleiben ausschliesslich ueber `operator_view()`
zugaenglich, NIE ueber `persona_view()`.

**Herkunftsbelegte simulierte Leader-Nachrichten (Auflage 6):** `section.
run_section` formuliert Leader-/Gast-/Debrief-Texte NICHT mehr zur Laufzeit als
Controller-f-String mit eingebettetem Save-JSON. Stattdessen kommen die Texte
aus der vorab abgelegten, klar als SIMULIERT markierten Fixture
`fixtures/leader_messages.json` (generischer, fester Text pro Turn-Art) und
werden als `SimulatedLeaderMessage(persona_key, source, text, save_payload)` an
`rooms.submit_to_sl` uebergeben: `persona_key`+`source` sind der Herkunftsbeleg
(welche Persona-Entscheidung dies simuliert, aus welcher Fixture/welchem
Schluessel); der tatsaechliche, laufabhaengige Save-Inhalt (der nicht vorab in
einer statischen Fixture stehen kann, weil er von den echten `initial_saves`
des jeweiligen Testlaufs abhaengt) wird GETRENNT als `save_payload` transportiert
und im `sl_log`-Eintrag separat gespeichert (`origin_persona_key`,
`origin_source`, `save_payload`, `leader_message`, `content`) — nie in den
Nachrichtentext hineingerechnet. `test_7_message_channels` prueft sowohl die
Kanaltrennung als auch, dass der Nachrichtentext keinen eingebetteten
Save-JSON-Blob enthaelt. Echte Reflexions-Turns (private Persona-interne
Ueberlegung vor dem Senden) bleiben eine ausgewiesene spaetere Grenze — hier
nicht implementiert.

## Leader-Ableitungsregel (Plan-Critic-Auflage 2, R6-Korrektur)

Aus dem Offer-/Consent-Log, NICHT aus einer Controller-Wahl: Scanne alle
`{"type":"offer", ...}`-Events in Log-Reihenfolge. Eine Offer ist **vollstaendig
angenommen**, wenn jede in `wants` genannte Persona ein
`{"type":"consent","offer_id":<id>,"accept":true}` hat UND KEINE davon ein
`accept:false` fuer dieselbe `offer_id` hat (`wants: []` = Solo, trivial
vollstaendig). Die **erste** so vollstaendige Offer im Log bestimmt Anker/Leader
(= ihr `from`) und die Mitgliederliste (`{leader} ∪ wants` — R6: die
EINGELADENE Menge, nicht zusaetzliche, nicht eingeladene Zustimmer aus
`accepted`). Implementiert in `rooms.derive_group_and_leader()`.

**Dissens (Plan-Critic-Auflage 1):** Ein `accept:false` macht die betroffene
Offer insgesamt unvollstaendig — die widersprechende Persona wird NICHT still aus
`wants` herausgefiltert, um doch noch eine Gruppe zu bilden. Nur eine SPAETERE,
tatsaechlich neu konsentierte Offer (ohne die widersprechende Persona) kann eine
Gruppe bilden (siehe `fixtures/offers/dissent_log.json`: `off-1` scheitert an
ghosts Widerspruch, `off-2` gelingt ohne ghost). Ein zusaetzlicher, NICHT
eingeladener Zustimmer darf eine vollstaendig angenommene Offer ebenfalls nicht
um sich selbst erweitern, selbst wenn er zustimmt und danach widerspricht
(`review_countertests.py` Test 07). `Testfall 3` prueft beide Dissens-Faelle.

## Operator-Belegansicht vs. Persona-Sicht (Plan-Critic-Auflage 3)

Ein `Table`-Objekt haelt `sl_log` (Leader/SL-Dialog inkl. Herkunftsbeleg +
Save-Payload), `table_messages` (privater Tisch-Absprachekanal) UND
`operator_meta` (Offer-Log-Rohdaten, Dissenter-Gruende, Herleitungs-Begruendung)
in DERSELBEN JSON-Datei. Zwei getrennte Lesefunktionen erzwingen die Trennung:

- `rooms.persona_view(table, persona_key)` — `table_id`, `leader`, `members`,
  `status`, `sl_log`, `table_messages`. Wirft `VisibilityError`, wenn
  `persona_key` kein Mitglied ist (kein Fremd-Tisch-Einblick). Enthaelt NIE
  `operator_meta` oder `chrononaut_ids`.
- `rooms.operator_view(table)` — voller Beleg inkl. `operator_meta` (Offer-Log,
  Dissenter, Herleitung), fuer QA/End-Critic, NICHT an Personas ausliefern.

`test_lobby_tables.test_2_channels_and_visibility` und
`test_7_message_channels` pruefen die Trennung aktiv.

## Freeze-Ausnahmen ggue. `COORDINATION-MODEL-FROZEN.md` (siehe `PLAN-P1.md`)

1. Teilnehmer werden aus Offer-/Consent-Logs abgeleitet, nicht per `--players`-Roster.
2. Tisch **1–5 inkl. Leader** ist die Grenze (kein 5+Leader-Roster-Default); Lobby
   darf >5 sein. 6. Beitritt wird hart abgelehnt (`Table.join_more` gibt `False`
   zurueck, mutiert nichts, waehlt keinen Ersatz-Tisch/-Spieler). Nachbeitritt
   jeder Art (voll/geschlossen/kein-Konsens-Beleg) ist in diesem Slice
   AUSDRUECKLICH NICHT unterstuetzt — `join_more` liefert in JEDEM Fall `False`
   (D2+D3, s. R4).
3. Geteilte Tisch-Sicht = identischer voller SL-Text fuer alle Mitglieder
   (`persona_view()` liest denselben `sl_log`, kein heimlich gekuerzter Ausschnitt).
4. NICHT angefasst in diesem Slice (offener Rest, nicht nachgebaut): feste
   ZUG/NOTIZ-Schablone, SL-Textkappung als Modell-Input, echte
   Persona-Reflexions-Turns vor dem Senden.
5. **`internal/qa/fixtures/persona-state.schema.json`** (R5): `persona_key`-Enum
   auf Pattern umgestellt — begruendet, weil die Fuenfer-Grenze auf Tischplaetze
   gehoert, nicht auf Persona-Identitaet; Validierung bleibt aktiv.

**Nicht angetastet** (COORDINATION-MODEL-FROZEN, nicht verhandelbar): Punkt 3 „NUR
der Leader schreibt" — `rooms.submit_to_sl()` erzwingt das (`LeaderOnlySendError`
sonst), `section.py` ruft es fuer JEDEN Turn ausschliesslich mit `table.leader`
als Akteur.

## Abnahmefaelle → Tests

`test_lobby_tables.py`, 22 Funktionen: die urspruenglichen 6 (Kapazitaeten inkl.
0/6-Ablehnung und 6. Beitritt; Kanaltrennung/Sichtfilter/Leader-only-Send;
Dissens ohne kuenstlichen Konsens; Lifecycle inkl. Doppel-Abschluss/fehlendem/
falschem Save/Initial-Import-ist-kein-Abschluss; Chrononaut-Lock; kein echter
Provider via Quelltext-Scan + Socket-Sperre) PLUS R7-Nachrichtenkanaele
(`test_7_message_channels`, inkl. NB-A-Empfaenger-Assertion) und R5-Zusatzpersona
`medic` durch den vollen Offline-Lifecycle
(`test_8_medic_extra_persona_full_lifecycle`) PLUS vier NB-Regressionstests aus
der Abschlusskorrektur 2026-09-21 (`test_9`..`test_12`, semantisch zu den
damaligen externen Edge-Faellen aequivalent: NB-A-Empfangstext,
NB-B-Qualifier+json-Strip, NB-C-Finalize-Recovery+torn-Save,
NB-D-stale-Handle/closed/consent) PLUS drei Konsistenz-Nachzug-Tests
(2026-09-21, semantisch zu den 8 `review_ak_invariants.py`-Faellen +
Plan-Critic-Auflagen aequivalent): `test_13_nb_b_negation_quote_marker_and_cross_table_final`
(zeilen-beginnende Negations-/Zitat-Marker inkl. Mehrfachvorkommen +
fremder-Tisch-`__final`-Kollision), `test_14_nb_c_recovery_torn_state_pair_and_harvest_pinning`
(closed-vor-final-Recovery mit Crash exakt beim `__final`-Write, Save+State
bleiben bei einem Riss gemeinsam alt, Retry mit abweichender Ernte mischt
nicht) und `test_15_nb_d_stale_handle_preserves_sl_log_on_table_message`
(reload-append-persist: ein aelteres aktives Handle loescht beim Posten den
bereits persistierten `sl_log` nicht), PLUS drei K-Re-Review-Regressionstests
(2026-09-21, semantisch zu `review_k_publication.py`/`review_k_fault_matrix.py`
aequivalent): `test_16_k3_suffix_marker_is_rejected` (ein an das Markertoken
angehaengtes `=false`-Suffix OHNE trennenden Whitespace ist kein positives
Ereignis), `test_17_k1_new_save_old_state_stays_consistent_on_state_write_failure`
(ein fehlgeschlagener State-Publish NACH bereits committeter Save-Version darf
keinen Leser eine gemischte Generation sehen lassen) und
`test_18_k2_pending_completion_order_blocks_second_section` (ein offener
Abschluss-Auftrag bindet den Tisch exklusiv gegen einen ZWEITEN Abschnitt AUF
DEMSELBEN Tisch), PLUS VIER NEUE P1-Restkorrektur-Tests (2026-09-22, semantisch
zu den 6 `review_p_boundaries.py`-Faellen + der Admission-Matrix aequivalent —
je einer pro P-Korrektur): `test_19_p1_open_completion_order_blocks_new_table_admission`
(ein lock-freies, aber noch am offenen Auftrag gebundenes Mitglied darf keinen
NEUEN Tisch bilden; nach `__final` wieder frei),
`test_20_p2_section_id_grammar_and_final_identity` (`/` im `section_id` wird
direkt UND via `run_section` abgelehnt; ein table_id-Treffer allein macht
einen `__final` mit abweichender `section_id` nicht zu `already_completed`),
`test_21_p3_fenced_text_block_marker_is_not_an_event` (ein Marker als
Protokollbeispiel innerhalb eines ```` ```text ```` -Fence ist kein Ereignis)
und `test_22_p4_run_scoped_ref_does_not_alias_across_run_dirs` (eine Referenz
aus einem fremden `run_dir` loest in einem anderen `run_dir` nie einen Save
auf; dieselbe `run_dir` erhaelt bei erneuter `Lobby`-Instanziierung dieselbe
`run_id`).

Externe, unabhaengige Re-Reviews (nicht Teil dieses Verzeichnisses):
- `review_countertests.py --repo-root <worktree>`, 10 gezielt aus dem
  Zielvertrag abgeleitete Tests (R1/R2×2/R3/R4×2/R5/R6/keine direkte
  R7-Testnummer — R7 wird nur manuell/End-Critic geprueft).
- `review_nb_edges.py --repo-root <worktree>`, 9 gezielte Edge-Faelle fuer
  NB-A..D (R7/R2×2/R1+R3×2/R4+R6×3/positive Retry-Gegenprobe).
- `review_ak_invariants.py --repo-root <worktree>` (dritte, unabhaengige
  Re-Review, `zeitriss-p1-review-ak-2026-09-21/`), 8 auf dieselben
  Zustands-/Dateninvarianten gerichtete Tests fuer NB-B/C/D (zeilen-
  beginnender Marker, `__final`-table_id-Bindung, closed-vor-final-Recovery,
  torn-Save-/State-Paar, `__final`-Kollision, harvest-drift-Pinning,
  stale-Handle-Kanaltrennung) — alle 8/8 gruen.
- `review_k_publication.py --repo-root <worktree>`, 5 K-Re-Review-Tests
  (Positiv+Retry, `=false`-Suffix-Negativ, State-Schreibfehler haelt Save
  ALT, offener Auftrag blockiert zweiten Abschnitt, alte Recovery darf
  spaeteren Tisch nicht zurueckrollen) — 5/5 gruen.
- `review_k_fault_matrix.py --repo-root <worktree>`, sequenzielle
  Vor-/Nach-Fehlerinjektion an JEDEM `write_text`/`os.replace`-Schritt eines
  `complete_section`-Laufs (34 Szenarien) — `mixed_pairs=0`,
  `failed_recovery_pairs=0`, `status_not_closed=0`.
- `review_p_boundaries.py --repo-root <worktree>` (vierte, unabhaengige
  Re-Review, `zeitriss-p1-review-p-2026-09-22/`), 6 auf die P1-P4-Korrekturen
  gerichtete Grenzfaelle (offener Auftrag bindet Mitglieder gegen NEUE Tische
  UND deren Retry, Section-ID-Kollision, gefenchte Steuerzeile, run-scope-
  Save-Alias, explizite `states_dir`-Kontrolle) — 6/6 gruen.
- `review_p_admission_matrix.py --repo-root <worktree>`, sequenzielle
  Vor-/Nach-Fehlerinjektion (17 Schritte, 34 Szenarien) mit Aufnahme-/
  Leader-Send-Sonden NACH jedem Schritt — `premature_admission_scenarios=0`,
  `premature_leader_sends=0`.

## Nicht-Ziele (unveraendert ggue. `PLAN-P1.md`)

Kein Wuerfeln/Aufstieg/Belohnung/Missionswahl, keine zweite Regelengine, kein
Web-UI/DB/Discord/Dauerprozess, keine Spielregel-/Masterprompt-/19-Module-/
`faithful_section.py`-Aenderung, kein Commit/Push/Merge. Echte
Modell-/KI-SL-/OWUI-/OpenRouter-Laeufe sind eine separate, spaeter freizugebende
Erweiterung — nicht Teil dieses Offline-Durchstichs.
