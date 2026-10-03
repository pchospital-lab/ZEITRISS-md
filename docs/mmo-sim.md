# ZEITRISS MMO-Sim — Bedien-/Betriebsdoku (lokaler Entwicklungskandidat)

> **Status (2026-10-03):** Ausgewählte lokale Funktionsumfänge sind
> kontrolliert offline geprüft. IA-1 (Schutz von Current und inaktivem
> eigenen Figurenarchiv beim Resume) ist auf Quellstand `48ff6409`
> unabhängig im beschriebenen Offlineumfang abgenommen; die konkret
> geprüften Claim-/CC-1-/G1-Fälle bleiben erhalten.
> **H/P2/v2 insgesamt sind nicht abgenommen.** Das ist keine vollständige
> Endnutzer-, Live-, Installations- oder Abo-Kompatibilitätsfreigabe.
> Vollständiges Community-Backup/Restore und nativer LAN-/Remote-Join
> bleiben getrennte offene Nachweise. Die folgenden Bedienbeschreibungen
> ersetzen diese Freigaben nicht; historische Statusabschnitte behalten
> ihren jeweils angegebenen Zeitpunkt und Umfang.

## Architektur

```
mmo_sim/
  core/       neutraler Kern (Store, Persona-State-Engine, Controller, Runtime,
              Scheduler, Identity, Events, Completion-Marker) — kennt KEINE
              ZEITRISS-Regel (kein "v7", kein "5").
  adapters/   echte Produktionspfade: persona_api (LiteLLM/OpenRouter),
              persona_claude_code (lokale CLI, isoliert), gm_owui (nutzt
              agent_mp/sl_client), fakes (Prozess-/HTTP-Grenze für Tests).
  domain/zeitriss/  ZEITRISS-Domänenregeln als injizierte Policy-Objekte
              (policy.py), Save-Extraktion (saves.py, aus agent_mp/ verschoben),
              Onboarding, Import/Export, Katalog, Community-Bootstrap, Prelude.
  registry/   neutraler Teilnehmer-/Anwendungsdatensatz-Hook (11 §9).
  ui/tui.py   Terminaloberfläche (kein Browser fürs Spielen).
  lab/runner.py  headless Lab-Betrieb (Singleton, Budget, Stop/Status).
  reports/report.py  lokale Event-Reports + Issue-Entwürfe (kein Modellcall).
```

Die QA-Fassaden (`internal/qa/harness/lobby/rooms.py`, `agent_mp/saves.py`,
`persona_state.py`) sind Re-Export-Shims auf die extrahierte Implementierung
— sie enthalten selbst keine Logik mehr, nur Alt→Neu-Kompatibilitätsschicht
(Konstruktorsignaturen, Default-Datum für die eingefrorene P1-Testsuite).

## Starten (Terminal, kein Browser)

```bash
python3 scripts/mmo_sim.py --participant <teilnehmer-id> --data-dir internal/mmo_sim_data
```

Oder über den generischen Launcher: `python3 scripts/launcher.py` → Menüpunkt
`[M] ZEITRISS MMO-Sim`.

## Tests

```bash
# Neue mmo_sim-Regressionen (Gesamtrunner):
python3 tests/mmo_sim/run_all.py

# Eingefrorene P1-Regression (muss weiterhin grün sein):
python3 internal/qa/harness/lobby/test_lobby_tables.py

# Offizieller P1-Regressionsrunner (aus dem Auftragspaket, --repo-root auf
# diesen Worktree, --output-dir AUSSERHALB des Repos):
python3 <auftragspaket>/reference/p1-regressions/run_checks.py \
  --repo-root <dieser-worktree> --output-dir <externes-verzeichnis>
```

## Provider-Profile (03_PROVIDER_UND_BETRIEB.md)

| Profil | Spieler-Personas | KI-SL |
|---|---|---|
| Hybrid | `persona_claude_code` (lokale CLI, isoliert) | `gm_owui` |
| API | `persona_api` (LiteLLM/OpenRouter) | `gm_owui` |
| Offline-Prüfung | `adapters/fakes.FakeCLIProcess`/`FakeHTTPServer` | dito |

Kein stiller Fallback: 401/403 → `ProviderAuthError`, 429/Quota →
`ProviderQuotaError`, CLI/Isolation fehlt → `ProviderUnavailableError`. Alle
drei Fehlerklassen führen zu Pause/Fehlerstatus, nie zu einem automatischen
Providerwechsel.

**Betriebswarnung `persona_claude_code` ohne `extra_isolation_flags`
(End-Critic W1):** Ohne konfigurierte `extra_isolation_flags` prüft
`check_isolation()` NUR Binary-Erreichbarkeit + Arbeitsbereich; die von
03 §5 geforderte Tool-/MCP-/Hook-/Settings-Isolation bleibt unverifiziert.
Einzige verbleibende Schutzschicht ist dann der Billing-Var-Check (03 §4,
prüft nur 3 benannte Variablen). `decide()` gibt in diesem Fall genau eine
Log-Warnung pro `check_isolation()`-Aufruf aus (`persona_claude_code.py`,
`_LOG.warning`). **Für echten Spielbetrieb (nicht nur den in
`review_p2_integration.py` geprüften Kontext-/JSON-Vertrag) sind reale,
verifizierte `extra_isolation_flags` Pflicht** — der Default-Fall ohne
Flags ist nur für die Offline-/Vertragsprüfung freigegeben.

**Admission-Gate: „vor jedem Request", nicht atomar damit (End-Critic
W2):** `read_admission_block()` liest `lab.stop`/`lab.status.json` frisch
von der Platte vor jedem GM-Request, es gibt aber keinen Lock zwischen
diesem Read und dem darauffolgenden vollen Turn. Ein exakt in diesem
Fenster gesetzter Stop lässt den bereits begonnenen Turn noch zu Ende
laufen (max. 1 Turn „Overshoot"), bevor der Gate beim nächsten Request
sicher greift. Für den aktuellen Offline-/Einzelbenutzer-Betrieb
vertretbar, aber nicht als vollständig race-frei/atomar missverstehen.

## P2-Restintegration (2026-09-23, siehe WORKER-REPORT-REST.md für Details)

- `l lead:persona:<id> [<weitere-token>]` macht eine eingeladene Persona
  zum Leader statt des aufrufenden Menschen (A24, echte Zusage vor
  Tischaufnahme; der aufrufende Mensch wird selbst zum Gast).
- Nach Import eines Saves mit `level >= 2` bietet das Terminal die
  Direktspielen-/KI-Vorlauf-Wahl (11 §7, A23). `w`/`s`/leer/EOF/Abbruch
  bleiben Standard: kein Vorlauf, kein Lab-Autoritätswrite. `v` liest zuerst
  die bereits bestätigte Community unter diesem `run_dir` (deterministisch
  `community-<participant_id>`, kein neuer Bootstrap); fehlt sie, bricht der
  Dialog sofort kontrolliert ab. Sonst folgen Profil (`api`/`hybrid`),
  ausdrückliche freie KI-Personaauswahl aus der Community und die fünf
  endlichen Budgetfelder (`max-requests`/`max-seconds`/`max-usd`/
  `max-idle-windows`/`max-wall-seconds`, validiert über dieselben Typkonverter
  wie `lab.cli`), dann eine vollständige Zusammenfassung mit letzter
  ausdrücklicher Bestätigung (`ja`/sonst Abbruch). Erst danach startet
  `_cmd_bounded_ai_preflight` den bereits abgenommenen gemeinsamen
  Lab-Dispatcher (`scripts/mmo_sim.py lab resume ...`, derselbe Einstieg wie
  `mmo_sim.lab.cli.main`) als kontrollierten Kindprozess — kein zweiter
  `LabRunner`, keine kopierte Lobby-/Request-/Save-Schleife. Ohne separates
  Live-Go bleibt der Vorlauf providerfreie Konfiguration/Testautorität (01
  §M4); ein echter Modellaufruf setzt eine explizit konfigurierte, separat
  freigegebene Providerbindung voraus.
  R1-Nachzug (2026-09-30, A23-Restbefund): Community-Mitgliedschaft
  (`personas_written`) allein macht eine Persona NICHT frei/spielbereit —
  die Personaauswahl prüft zusätzlich über dieselbe bestehende Autorität wie
  jeder andere Spielstart (`_resolve_member`, `chrononaut_active_binding`/
  `chrononaut_open_completion_order`), ob die Figur fertig erschaffen, lesbar
  und nicht an einen Tisch/offenen Abschluss gebunden ist; unfertige/
  gebundene/nicht auflösbare Auswahl wird vor jedem Dispatcher-/
  Autoritätswrite konkret abgelehnt.
- `[n]`/`[i]` registrieren die betroffene Figur jetzt im Teilnehmer-Katalog
  (`domain/zeitriss/catalog.py`) — Resume-Karte/Mehrfiguren-Übersicht
  zeigen echte Einträge (A21, Teilausbau: der zugrunde liegende Save-Store
  bleibt weiterhin EIN aktueller Stand pro Teilnehmer, siehe Restrisiken
  im WORKER-REPORT-REST.md).
- `reports/report.py:extract_provenance_excerpts` liefert unveränderte
  Textausschnitte zu Ausrüstung/Boss/Kampf/Drift-Erwähnungen aus echten
  `sl_turn`-Events (A13, reine Stichwortsuche, keine Modellbewertung).

## A13 — lokaler Operator-Quellenbericht (2026-09-30, siehe WORKER-REPORT.md für Details)

Neuer, früher `report`-Zweig im bestehenden Terminal-Dispatcher
(`scripts/mmo_sim.py`, vor jeder Teilnehmer-/TUI-/Adapterkonstruktion) ruft
`mmo_sim.reports.report.main(argv, repo_root)` auf. Rein lesend, kein
Modellcall, keine neue Event-/Buchungs-/Publikationsschreiber — Quelle ist
`table.sl_log` (nicht `events.jsonl`, das in echten A23-Ablagen fehlt),
`completion/<section>__plan.json`/`__final.json`/Mitgliedsguards,
`current_saves/<persona>__versions/<seq>.json` und passende
`requests/*.json`. Genau EIN gewählter Tisch+Abschnitt pro Aufruf, kein
Mehrtabellen-/Playermenü.

```
python scripts/mmo_sim.py report --data-dir <vorhandene-synthetische-Kopie> \
  --table <tisch-id> --section <abschnitt-id> --output-dir <neuer-externer-ordner> \
  [--include-persona-feedback]
```

Erzeugt im NEUEN, noch nicht vorhandenen `--output-dir` (außerhalb Daten-
und Repoquellbaum): `report.json`, `report.md`, `issue-drafts.md`,
`source-index.json`, `SHA256SUMS`. Jeder Quellenausschnitt trägt relativen
Pfad, Quelldatei-SHA256, JSON-Pointer/Offsets und Texthash. Ohne
`--include-persona-feedback` werden keine privaten Reflexionstexte
exportiert; menschliche Privatnotizen bleiben in jedem Fall ausgeschlossen.
Issue-Entwürfe sind lokal/technisch (keine automatischen GitHub-Issues).

R1–R3-Nacharbeit (2026-09-30, siehe WORKER-REPORT.md unter
`tmp/a13-review-2026-09-30/worker/` für Details): widersprüchliche
Bindungen (publiziertes Endsave-Hash gegen Guard, Guard-eigenes
`persona_key`, Final-`section_id`, `expected_prev_ref`-Run-Bindung) sind
jetzt ein Hold (`A13SourceError`) statt eines stillen `COMPLETE`. Die
historische Vorversion wird tatsächlich aus `expected_prev_ref` (Plan) +
`run_id` geladen (nie aus dem aktuellen Current) und — wenn Vor- und
Nachsave vorliegen — mit passenden Szenenausschnitten als rein technisches
Quellenpaar verknüpft (ausdrücklich kein Kauf-/Erfolgsbeweis). Jeder
Quellenread (Tabelle, Completion, Requests, Reflexionen, `events.jsonl`)
läuft über denselben Rootcheck (auch Elternlink-Escape); alle gelesenen
Quellen werden vor der Ausgabe erneut gehasht (Snapshot-Hold bei
Änderung). Request-Routen werden vor jeder Ausgabe auf Schema+Host+Port+
Pfad reduziert (keine Userinfo/Passwörter/Querytoken/Fragmente). Exportierte
Reflexionen sind `private:true` mit auflösbarer Zeile/Offsets/Hash. Fehlen
GM-Modell-/Prompt-/Regelquellenmetadaten (aktuell immer, da nicht
aufgezeichnet), ist der Bericht `PARTIAL` statt pauschal `COMPLETE`.

## I4 — Figurenkontinuität (2026-09-24/25, siehe WORKER-REPORT-I4.md für Details)

- **Lücke 1 behoben:** `ui/tui.py:_sync_outgoing_active_figure` sichert vor
  JEDEM Aktivwechsel (Auswahl `_switch_active_figure`, Import-Aktivwechsel
  `_cmd_import`, Erschaffungs-Aktivierung `_cmd_new_or_switch_character`) den
  zuletzt real veröffentlichten Current-Save der BISHERIGEN aktiven Figur in
  ihre eigene Katalog-Persistenz (`catalog.store_figure_save`). Vorher hielt
  der Katalog je Figur nur ihren ursprünglichen Import-/Erschaffungsstand
  fest — ein Abschnittsabschluss aktualisierte diese Kopie nicht, ein
  A → B → A-Rückwechsel publizierte daher den veralteten Stand statt A_neu.
- **Lücke 2 behoben:** `_cmd_new_or_switch_character`s Erschaffungspfad prüft
  jetzt die REALE Bindung der bisherigen aktiven Figur
  (`store.chrononaut_active_binding`/`chrononaut_open_completion_order`) VOR
  jeder Current-/State-Publikation. Vorher publizierte der Pfad UNBEDINGT und
  rief `bind_for_section(..., has_open_section=False)` mit einem Literal auf,
  das nie `True` wurde — eine neue Figur konnte so eine tischgebundene aktive
  Figur als Current ersetzen, obwohl deren Abschnitt offen blieb.
- **Weg 3 ergänzt:** `_cmd_import`s Konfliktbasis (`existing_block_for_char_id`)
  berücksichtigt jetzt auch bereits registrierte INAKTIVE Figuren (Katalog-
  Fallback), nicht nur die aktuell aktive — ein Re-Import einer inaktiven
  Figur ist bei identischen Bytes idempotent (No-op) und verlangt bei
  abweichenden Bytes dieselbe ausdrückliche Konfliktwahl wie bei der aktiven
  Figur, statt stillschweigend für immer geparkt zu bleiben.
- Neue additive Tests: `tests/mmo_sim/test_i4_figure_continuity.py` (Weg 1
  zweite TuiSession im selben Prozess — Korrektur 2026-09-25: vorher
  irrefuehrend als "frischer Prozess" benannt/beschrieben, s.u. —, Weg 3
  inaktiver Importkonflikt, Weg 4 unterbrochene atomare Publikation, Weg 5
  zwei Teilnehmer mit getrennten Bindungen).
- **End-Critic-Befund BLOCKER 1 behoben (2026-09-25):** `_sync_outgoing_
  active_figure` ermittelte die "abfahrende" Figur ursprünglich über
  `catalog.active_chrononaut_id(...)`. Dieses Feld kann durch ein bereits
  VOR I4 bestehendes Absturzfenster zwischen `core_store.publish_current_
  save` und `catalog.bind_for_section` (an allen drei Aufrufstellen)
  veraltet sein, während Current selbst schon den neuen Stand trägt. Ein
  späterer Wechselversuch hätte dann die tatsächlichen (zu einer ANDEREN
  Figur gehörenden) Current-Daten unter der ID der veralteten "aktiven"
  Figur in deren Katalogpersistenz geschrieben — permanenter Verlust/
  Vermischung von Spielfortschritt (Vertrag §3 C/E). Fix: die "outgoing"-ID
  wird jetzt aus dem geladenen Current-Block selbst abgeleitet
  (`zeitriss_saves.block_char_id`), nicht aus dem instabilen Katalogfeld.
  Regressionstest: `tests/mmo_sim/test_i4_figure_continuity.py::
  test_weg4_stale_catalog_active_id_does_not_corrupt_outgoing_figure`.
- **I4-Nachzug (2026-09-25) — Korrektur:** die obige Einstufung des
  Absturzfensters zwischen `publish_current_save` und `bind_for_section`
  als "nur harmlose, selbstheilende Anzeige-Verzögerung" war ZU OPTIMISTISCH
  und wurde von einem externen Review (REVIEW-I4-AKTIVAUTORITAET.md)
  zurückgewiesen: der veraltete `catalog.active_chrononaut_id`-Zeiger diente
  bis dahin an DREI Stellen (`_switch_active_figure`, `_cmd_import`,
  `_cmd_new_or_switch_character`s Erschaffungspfad) weiterhin als Autorität
  für Rückgabe-/Sperrentscheidungen — kein reines Anzeigeproblem:
  - **T1a:** wählte man danach exakt die bereits real aktive (aber laut
    Katalog noch inaktive) Figur erneut an, wurde sie fälschlich aus ihrem
    veralteten Katalog-Importstand neu geladen und republiziert — realer
    Fortschritts-Rollback (nicht nur eine verzögerte Anzeige).
  - **T1b:** eine über den echten Current-Save bereits tischgebundene Figur
    ließ sich per Auswahl/Import/Erschaffung einer ANDEREN Figur ersetzen,
    weil die Sperrprüfung gegen die veraltete (ungebundene) Katalog-ID statt
    gegen die real gebundene Figur lief — Bindungsumgehung.
  - **T2:** ein bekannter, aber durch einen transienten Lesefehler gerade
    nicht ladbarer Current-Save wurde vom Ausgangs-Sync wie "kein Save
    vorhanden" behandelt (No-op) — der Wechsel lief trotzdem durch, und die
    ungesicherte Fassung ging beim nächsten Zugriff auf den alten
    Katalogstand verloren.

  **Fix:** `ui/tui.py:_resolve_real_active_chrononaut_id` ermittelt "wer ist
  wirklich aktiv" jetzt IMMER über die real veröffentlichte Current-Fassung
  (`store.load_current_save_or_raise` → `zeitriss_saves.block_char_id`),
  nicht über den Katalogzeiger — dieser wird bei Abweichung konsistent
  nachgezogen (Selbstheilung über denselben bestehenden `catalog.bind_for_
  section`-Persistenzpfad). Alle drei Aufrufstellen nutzen dieses Ergebnis
  sowohl für die "bereits aktiv"-Prüfung als auch für die Sperrprüfung
  (`chrononaut_active_binding`/`chrononaut_open_completion_order`). Ein neuer
  `store.load_current_save_or_raise` (mit `store.CurrentSaveUnavailableError`)
  unterscheidet zusätzlich "noch keine Fassung vorhanden" (weiterhin `None`,
  unveränderte Semantik für alle bestehenden Aufrufer von `load_current_
  save`) von "bekannte Fassung gerade nicht lesbar" — Letzteres bricht den
  Wechsel jetzt kontrolliert ab, statt ihn stillschweigend fortzusetzen.
  Regressionstests: `tests/mmo_sim/test_i4_figure_continuity.py::test_weg4_
  stale_catalog_active_id_does_not_corrupt_outgoing_figure` (bestehend) sowie
  neu `tests/mmo_sim/test_i4_active_authority_subprocess.py` (Wege 1-5,
  echte Interpreterprozesse, kleine Interruptions-Matrix an drei Nähten).

- **I4-Nachzug (2026-09-25) — Fehlertransparenz der Spurprüfung:**
  `core/store.py:_has_publication_trail` (belegt für strenge Verbraucher, ob
  für einen Teilnehmer bereits mindestens einmal veröffentlicht wurde) prüfte
  vorher über `Path.is_dir()` + `Path.glob("*.json")`. Beide Bausteine
  verschlucken I/O-Fehler an ihrer jeweiligen Naht: `is_dir()` fängt
  ENOENT/ENOTDIR/EBADF/ELOOP ab (→ `False`) und lässt andere Fehler (z. B.
  EIO) roh durch; `glob()` verschluckt `PermissionError`/`OSError` beim
  darunterliegenden Verzeichnis-Scan (→ leerer Iterator). Ein bloßer
  I/O-Fehler an der Prüfung konnte dadurch entweder wie ein sicherer
  Erstzustand aussehen (Export des alten Onboarding-Stands trotz
  vorhandener eigener Version) oder als roher `OSError` am vorgesehenen
  `CurrentSaveUnavailableError`-Handler vorbeigehen (Vertrag §3 A: "Fehler
  der Spurprüfung nicht wiederum als leere Menge behandeln").

  **Fix:** zwei unabhängige, fehlerbehandelte `os.scandir()`-Aufrufe statt
  `is_dir()+glob()`. Zuerst der Elternordner `current_saves/` (listet nur
  den Eintragsnamen `<persona_key>__versions`); nur `FileNotFoundError`/
  `NotADirectoryError` an DIESER Stelle gilt als echte Abwesenheit (Erst-
  zustand bleibt möglich, auch für neue Teilnehmer in einer bereits
  bestehenden Community). Existiert der Eintrag laut dieser unabhängigen
  Quelle, macht jeder Fehler beim Lesen seines Inhalts (EACCES, EIO, oder
  ein erneutes ENOENT als TOCTOU-Widerspruch) die Spur NICHT wieder zu einer
  leeren Menge — `CurrentSaveUnavailableError` statt `False`/rohem
  `OSError`, unabhängig von der genauen Errno-Klasse. Signatur bleibt
  `bool`, mit zusätzlichem `raise`-Pfad; `_persona_state_or_raise`/
  `_current_save_version_path_or_raise` (bereits angeschlossen) reichen den
  Fehler unverändert an `load_current_save_or_raise` → `ui/tui.py`s
  `_cmd_export`/`_resolve_active_save` weiter.

  Seam-Hinweis: die externe Abnahmeprobe `review_i4_publication_trail.py`
  injizierte ihre Fehlerfälle ursprünglich an `Path.stat` — dieser Seam wird
  vom Fixcode nicht mehr aufgerufen (nur noch `os.scandir`). Original bleibt
  unverändert; eine Kopie mit angepasstem Seam liegt im Ergebnispaket als
  `review_i4_publication_trail.ADAPTED.py`.

  Neue additive Tests:
  `tests/mmo_sim/test_i4_publication_trail_error_transparency.py` — echte
  Interpreterprozesse für Scan-Fehler an Kind- UND Elternebene (EACCES, EIO,
  TOCTOU-ENOENT nach bestätigter Elternexistenz), reale Verzeichniszustände
  für die Erstzustandsfälle (kein Elternordner, fremde Spur eines anderen
  Teilnehmers, leeres/nur-fremdartiges Versionsverzeichnis), sowie
  Nebenwrite-Freiheit sowie exakte Wiederherstellung nach einem geblockten
  Versuch.

## P2-Community-Erstgeneration (2026-09-25, siehe WORKER-REPORT.md für Details)

`c` (Neue Spielgemeinschaft) legte bisher NUR Profil-ENTWÜRFE an
(`bootstrap_community`, `plays_char={"...":"NOCH_NICHT_ERSCHAFFEN"}`) — kein
Current-Save, keine Chrononaut-ID, NICHT spielbereit. Jede geplante Persona
durchläuft jetzt ihren EIGENEN, fortsetzbaren SL-Erschaffungsdialog
(`mmo_sim/domain/zeitriss/community_creation.py`) — denselben Kern wie
`[n]` für einen Menschen (`mmo_sim/core/creation_service.py:
run_admitted_creation_dialog`), nur dass die Antworten von einem echten
Persona-Treiber kommen statt vom Terminal (`persona_driver_factory(persona_
key)`, eigene Chat-Identität `onboarding-<persona_key>`). SL-Fragen kommen
weiterhin von `gm_transport_factory`. Ohne beide konfigurierte Factories
ODER ohne Admission-Freigabe (keine `lab.status.json`) bleibt jede Persona
ein ehrlicher Entwurf (`no_driver`/`blocked`) — identisches Verhalten zur
bisherigen Baseline-Beobachtung ohne Live-Setup.

Jeder Modellschritt (Persona- UND GM-Turn) ist über Admission-Gate +
Reservierung + `request_ledger` gebunden an `(community_id, generation,
persona_key, phase, turn)` (`table_id=community_id`,
`section_id=f"gen{generation}"`, `role` trägt die Phase, `turn_idx`/
`participant=persona_key`) — ein Neustart löst keine zweite Reservierung/
keinen zweiten Request für denselben noch offenen Schritt aus (bestehende
`request_ledger._operation_identity`-Prüfung, kein neuer Mechanismus).
Eine bereits `completed` Persona (I4-Current-Autorität: gültiger
Current-Save vorhanden) wird bei Reentry NICHT neu erschaffen. Eine
blockierte/abgelehnte/fehlgeschlagene Persona hält die übrigen Mitglieder
nicht an (`advance_community_creation` iteriert alle geplanten Personas
einzeln).

Tischanschluss (bewusst KEIN neuer Code): eine spielbereite Persona nimmt
über den bereits vorhandenen `l persona:<key>`-Einladungsweg teil (Consent
über denselben `decision_contract`, ihr Current kommt als Gast/Leader an).

Tests: `tests/mmo_sim/test_p2_community_creation.py` (13 Fälle, Fake-GM/
Fake-Persona an der äußersten Grenze — neue Community >5 Personas,
mehrstufige Einzeldialoge, Fehler/Ablehnung/Budget-Stop ohne fingierte
Spielfähigkeit, Teilgeneration+Neustart ohne Doppelrequests, Reentry ohne
neuen Modellaufruf, echter Tischanschluss inkl. Ablehnung, unbeteiligte
Menschen/Communities unverändert, echter `c`-Weg via `TuiSession`) und
`tests/mmo_sim/test_p2_community_creation_real_subprocess.py` (echter
`scripts/mmo_sim.py`-Subprozess mit Terminaleingabe `c\nx\n`, echte
Loopback-HTTP-Doubles für GM+Persona, budgetbegrenzt auf eine Persona,
Reentry ohne neuen Request).

## Gate B — Persona-Zusatzfigur/gemeinsamer Level-1-Frischstart (2026-10-02)

> Status: kontrolliert offline geprüft (synthetische Fake-CLI-/loopback-
> HTTP-Doubles an den echten Adaptergrenzen), kein Livebetrieb, keine neue
> A24/G6-Abnahme. Terminal-Bestand/Neustart-Auftrag 2026-10-02.

Zielfall: eine bekannte, bereits spielende Persona (vorhandene aktive
Figur) erschafft auf ausdrückliche Einladung einen ZUSÄTZLICHEN eigenen
Chrononauten, damit Mensch und Persona gemeinsam auf Level 1 frisch
beginnen können — die alten Figuren, die Community/das Roster und fremde
Persona-Daten bleiben dabei unverändert erhalten. Bisher deckte der
vorhandene Persona-Erschaffungscode (`advance_one_persona_creation`/
`advance_community_creation`) ausschließlich die Community-ERSTgeneration
ab (`_cmd_community`, strukturelle Annahme „nie ein vorheriger
Current-Save") und der Einladungsweg (`_cmd_local_round`) ausschließlich
Personas mit BEREITS vorhandener fertiger Figur (kein Erschaffungsschritt).

Neue Domänenfunktionen in `mmo_sim/domain/zeitriss/community_creation.py`:

- **`advance_additional_persona_creation`**: GENAU EIN
  Erschaffungsversuch für eine ZUSÄTZLICHE Figur. Nutzt denselben
  `core/creation_service.run_admitted_creation_dialog`-Kern wie der
  menschliche Pfad und die Community-Erstgeneration — nur mit einer
  EIGENEN, von der realen Persona-Hauptkennung getrennten Onboarding-/
  Requestledger-Buchhaltungskennung (`_additional_onboarding_key`,
  `<persona_key>__additional_gen<N>`, `N` vom Aufrufer gewählt, z. B.
  `len(catalog.list_for_participant(...)) + 1`) — löst damit strukturell
  die „neue technische Auftragsidentität pro weiterer Erschaffung, getrennt
  von vorherigen abgeschlossenen Aufträgen"-Anforderung, ohne den
  bestehenden `force_new`-Mechanismus der Erstfigur zu überschreiben/zu
  gefährden. Der tatsächliche, an den Modellprompt gehende Persona-Kontext
  bleibt an die REALE `persona_key`-Identität gebunden (eigenes, bereits
  gepinntes Profil — „Die Persona bleibt dieselbe simulierte Person", kein
  altes Figurenwissen/Wallet/Inventar im Kontext).
- **`_publication_reconcile_additional`**: dieselbe Bindungssicherheit wie
  der menschliche Mehrfigurenweg (`ui/tui.py:_cmd_new_or_switch_character`/
  `_switch_active_figure`, I4 Lücke 1/2) — `chrononaut_id` wird IMMER aus
  dem neuen `final_save` selbst bestimmt (nie aus einem zufällig
  vorhandenen `current`, der hier die ALTE Figur trägt). Hat die bisherige
  aktive Figur einen offenen Abschnitt/Abschlussauftrag
  (`core.store.chrononaut_active_binding`/`chrononaut_open_completion_
  order`), bleibt die neue Figur registriert+mit eigenen Savebytes
  gesichert, aber INAKTIV — kein Umgehungswrite, kein KI-Ersatz. Vor jeder
  Aktivierung wird die ausgehende (bisherige) Figur mit ihrem zuletzt real
  veröffentlichten Stand gesichert (A → B → A bleibt dadurch erhalten).
  Idempotent wie `_publication_reconcile`: ein Reentry nach gesunder
  Fertigstellung schreibt nichts erneut, kein zweiter Modellaufruf.

TUI-Integration (`mmo_sim/ui/tui.py`): `_cmd_new_or_switch_character`
bietet direkt NACH einer bewusst gewählten eigenen Zusatzfigur (Menü `[n]`,
Eingabe `neu`) die neue Methode `_invite_persona_fresh_start` an — fragt
nach einer Persona-ID, holt über denselben Entscheidungsvertrag wie eine
Tischeinladung (`core.lobby_service.request_admitted_decision`,
`decision_contract`) eine echte, protokollierte Zusage ein (Annahme/
Ablehnung/Pause, kein erfundenes Accept, kein verdeckter Ersatz durch eine
andere Persona) und ruft bei Zustimmung `advance_additional_persona_
creation` auf. Reine Gelegenheit: nur die ausdrücklich benannte Persona
wird gefragt, keine automatische Vollgruppen-/Community-Nachfrage, kein
Gleichlevel-Zwang. UI-Aktion und headless Aufruf (z. B. aus einem Skript)
nutzen denselben Anwendungs-/Storeweg (direkter Aufruf der Domänenfunktion).

Tests: `tests/mmo_sim/test_n1_n7_persona_additional_figure_2026_10_02.py`
(N1–N7, lokale Auftragsfälle). N1 treibt den vollen Terminalweg (Mensch
erschafft eigene Zusatzfigur, lädt Persona ein, Persona stimmt zu und
erschafft ihre eigene Zusatzfigur, beide nehmen danach regulär an einem
Tisch teil) über BEIDE Persona-Providerprofile an ihrer echten
Adaptergrenze (`PersonaClaudeCodeDriver`+`adapters.fakes.FakeCLIProcess`
bzw. `PersonaApiDriver`+`adapters.fakes.FakeHTTPServer`). N2 deckt
Ablehnung und bewusste Pause mitten im Erschaffungsdialog (keine
Pflichtangleichung). N3 A→B→A plus Restart (Reentry auf eine bereits
fertige Zusatzfigur ohne zweiten Modellaufruf). N4 eine echte Tischbindung
der alten Figur (`core.store.Lobby.lock_chrononaut`), die eine Aktivierung
ohne Umgehungswrite verhindert. N5 ein simulierter Transportfehler sowie
Reentry nach vollständiger Fertigstellung ohne doppelten Request. N6 prüft
den tatsächlichen, an den Persona-Treiber gesendeten Wire-Kontext (kein
altes Wallet/Inventar/Figurengeheimnis, keine fremden Sentinels). N7 prüft
die Erreichbarkeit über den realen `[n]`-Menüdispatch (`TuiSession.run()`).

## Headless-/Lab-Betrieb (2026-09-27, `lab start|resume|status|stop|attach`)

> Status (Stand 2026-09-30): H02/H05 abgenommen im vereinbarten kontrollierten
> Offlineumfang; H10 im festen operativen T1–T10-Umfang abgenommen (T9-Fix
> bestätigt). H11/H12 ist geliefert: die zwei CLI-Hilfetexte und der
> H11-Bestandsbezug sind bestätigt. Die D1-/Bilanz-Statusberichtigung wird
> hier nachgezogen; die unabhängige H11/H12-Schlussentscheidung steht noch aus.
> H01/H03/H04/H06–H09 sind anhand vorhandener Tests/Quelllesungen mit ihren
> jeweiligen Beleggrenzen zugeordnet, nicht pauschal neu abgenommen.
> H/P2 bleibt offen. KEIN Livebetrieb, KEINE P2-/v2-Gesamtabnahme.
> Beispiele unten nutzen ausschließlich Testwerte/-endpunkte
> (`<markiert>`) — sie behaupten KEINE bereits erteilte Modellbetriebs-
> Freigabe.

Ein FÜHRENDES Subkommando `lab` vor allen anderen Argumenten schaltet auf den
headless Lab-Betrieb um; ein Aufruf OHNE `lab` bleibt exakt die bisherige TUI
(`--participant`/`--data-dir`), unverändert. `lab` selbst delegiert VOR jeder
Teilnehmer-/Community-Logik — `--help`, `status`, `attach` und eine
abgelehnte Fehlkonfiguration erzeugen 0 Modellcalls und keine Marker-/
Communitydateien.

```bash
python3 scripts/mmo_sim.py lab start  --data-dir <dir> --community <id> --profile <api|hybrid> \
  --max-requests <N> --max-seconds <S> --max-usd <U> --max-idle-windows <K> \
  [--max-wall-seconds <W>] [--personas <p1,p2,...>]
python3 scripts/mmo_sim.py lab resume --data-dir <dir> --community <id> --profile <api|hybrid> \
  --max-requests <N> --max-seconds <S> --max-usd <U> --max-idle-windows <K>
python3 scripts/mmo_sim.py lab status --data-dir <dir>   # nur lesend
python3 scripts/mmo_sim.py lab stop   --data-dir <dir> [--reason <text>]   # nur Stop-Flag, kein Reset
python3 scripts/mmo_sim.py lab attach --data-dir <dir> [--follow]   # nur lesend, passive Ansicht
```

### Voraussetzungen (VOR jedem Start geprüft, ohne Bestandsmutation bei Fehlern)

- **Bestehende bestätigte Community**: `--community <id>` ist die ROHE
  bestätigte ID, genau wie `--participant <id>` in der TUI — der Code
  ergänzt das Präfix selbst und legt unter
  `<dir>/run/community/community-<id>` ab (angelegt über den normalen
  `c`-TUI-Weg oder die Community-Erstgeneration, s. oben). Lab bootstrapt
  selbst KEINE neue Community; kein zusätzliches `community-`-Präfix in
  diesem Argument angeben.
- **`--max-usd` ist für BEIDE Profile (`api` UND `hybrid`) Pflicht** — die
  KI-SL/GM-Rolle wird in jedem Profil über ein echtes HTTP-API angesprochen
  (`adapters/gm_owui.py`) und bleibt deshalb immer dollarbegrenzt/
  outputbegrenzt. Zusätzlich sollte `MMO_SIM_GM_OUTPUT_LIMIT_TOKENS` gesetzt
  sein — ohne bekannte GM-Ausgabegrenze blockiert ein hartes `--max-usd`
  jeden GM-Request am Admission-Gate (Q07: "keine erfundene Grenze"), sobald
  ein Tisch tatsächlich spielt. CLI-/Abo-Personas unter `hybrid` haben KEINE
  eigene Dollarabrechnung (`--max-usd` begrenzt nur die tatsächlich
  API-abgerechneten Rollen) — ihre eigene Turn-/Zeit-/Kontingentgrenze
  bleibt getrennt und wird hier NICHT als 0 USD erfunden.
- **Profil `hybrid`** bindet Personas zusätzlich über `MMO_SIM_PERSONA_CLI`
  (+ `MMO_SIM_PERSONA_ISOLATION_FLAGS`, s. Provider-Profile oben — dieselbe
  Isolationsflag-Pflicht gilt auch headless).
- `--max-requests`/`--max-seconds`/`--max-idle-windows`/`--max-usd`/
  `--max-wall-seconds` sind endliche positive Zahlen (kein NaN/Inf/0/negativ/
  Bruch für Integerfelder) — ungültige Werte werden von `argparse` selbst vor
  jeder Anfrage abgelehnt.
- `--personas` (optional) schränkt auf eine ausdrücklich gewählte Teilmenge
  der Community ein (H-F: "Lab spielt nur ausdrücklich ausgewählte
  KI-Personas"). Ohne diese Option spielt Lab die GESAMTE bestätigte
  Community. Ein Tischmitglied AUSSERHALB dieser Menge (z. B. ein
  menschlicher Teilnehmer mit eigener Figur) lässt den betroffenen Tisch mit
  `waiting_human` anhalten, statt ihn automatisch zu übernehmen.

### `start` vs. `resume` vs. `status`/`stop`/`attach`

- `start`/`resume` sind derselbe Aufruf mit denselben Community-/Fenster-/
  Offer-/Request-/Tisch-/Section-Identitäten — jede Ausführung ist eine NEUE
  `LabRunner`-Instanz (eigener Prozess), die den vollen Verbrauchsstand
  (`turns_used`/`seconds_elapsed`/`usd_spent`) frisch von der Platte liest,
  NIEMALS zurücksetzt. `resume` ist die für Betreiber gedachte, ausdrückliche
  Fortsetzung nach einer Pause/einem Stop; ein neuer Budgetsatz bei `resume`
  gilt ab dann zusätzlich (kein Reset des bereits Verbrauchten).
- `status` und `attach` konstruieren KEINEN `LabRunner`, KEINE Community-/
  Personakonstruktoren, KEINE Adapter — reine Lesevorgänge (`lab.status.json`
  + Stop-Flag + offene Requestdatensätze + frisch berechneter Admission-Gate-
  Zustand). `attach --follow` zeigt periodisch (Default 1 s) denselben
  JSON-Zustand plus die letzten öffentlichen Angebots-/Antwort-Ereignisse;
  Ctrl-C/EOF beendet NUR diesen Beobachterprozess, nicht den Lab-Controller.
- `stop` schreibt AUSSCHLIESSLICH ein idempotentes Stop-Flag
  (`<dir>/run/lab.stop`) — kein Reset von Budget/Zählern/Locks. „Stop
  angefordert" (dieser Befehl kehrt sofort zurück) ist NICHT dasselbe wie
  „Controller bereits angehalten" (der laufende Prozess prüft das Flag vor
  dem nächsten Request und beendet sich dann geordnet).
- Ctrl-C/SIGTERM auf dem `start`/`resume`-Prozess selbst fordert ebenfalls
  nur eine geordnete Pause an (kein erfundener Abschnittsabschluss) — ein
  bereits versandter Request darf noch abgeschlossen/verbucht werden, danach
  folgt kein neuer Persona-/GM-/Reflexionsrequest ohne neue Freigabe.

### Offener Abschnitt vs. veröffentlichter Save

Ein Lab-Fenster liefert intern eines von fünf Ergebnissen
(`core/lobby_flow.py:LobbyOutcomeKind`): `section_completed` (Save/Reflexion
veröffentlicht, Locks gelöst), `no_consensus` (niemand frei/alle pausiert),
`waiting_human` (Tisch benötigt eine Nicht-KI-Entscheidung), `stopped`
(Admission-Gate/Transportfehler) oder `open_with_reason` (z. B. ein
begonnener, aber nicht abgeschlossener Tisch — bleibt über `lab resume` mit
DENSELBEN IDs fortsetzbar, kein neuer Tisch aus derselben Zustimmung). `lab
status`/`lab attach` zeigen den technischen Zustand (Requestledger, Stop-/
Budgetgrenzen), nicht diese interne Enum-Ausgabe selbst — Konsolentext auf
stdout des `start`/`resume`-Prozesses spiegelt sie zusätzlich menschlich
lesbar (identischer Text wie die TUI-Ausgabe an derselben Stelle).

### Statusautorität vs. Requestledger vs. Stop vs. Fensterdiagnose

Vier getrennte, nicht austauschbare Datenträger: `lab.status.json` ist die
Lauf-/Budget-/Testautorität (`turns_used`/`seconds_elapsed`/`usd_spent`,
Wall-Clock-Deadline); der `request_ledger` ist die Requestbuchungsautorität
je `(community_id, generation, persona_key, phase, turn)`; `<dir>/run/
lab.stop` ist AUSSCHLIESSLICH die Stopanforderung (idempotentes Flag, kein
Reset von Budget/Zählern/Locks); `lab.last_window.json` ist eine REINE
Diagnoseprojektion des zuletzt bekannten Fensters (`LobbyOutcomeKind`), NIE
Ersatz für die drei anderen. Kein Bedienbefehl in diesem Block repariert
einen dieser Träger automatisch oder verspricht ein universelles
Mid-Turn-Recovery — ein bereits versandter, durch `SIGKILL`/Prozessabbruch
unterbrochener Request bleibt nach einem späteren `lab resume` bewusst
unbekannt/offen, kein automatischer zweiter Versand, keine erfundene
Antwort.

### Ein Writer pro Datenablage (H-D)

`lab start`/`lab resume` sind der EINZIGE Schreiber für `<dir>/run`, solange
ihr PID-Lock lebt (`<dir>/run/lab.lock.json`) — ein zweiter gleichzeitiger
`lab start`/`lab resume`-Prozess für dieselbe Datenablage wird abgelehnt
(Exitcode 3). Eine gewöhnliche TUI (`l`/`b`-Kommando) gegen DIESELBE
Datenablage lehnt kontrolliert ab, statt heimlich zum zweiten Schreiber zu
werden, solange ein ANDERER Prozess den Lab-Lock hält — `lab status`/`lab
attach` bleiben davon unberührt (rein lesend, kein Lock-Konflikt).

### Beispiel (Testwerte, keine Livefreigabe)

`DATA` liegt bewusst AUSSERHALB dieses Repo-Quellbaums (kein Headless-
Schreiben in Software-Quellbäume); `demo-community` ist eine bereits
bestätigte, rein synthetische Community (z. B. über die TUI oder die
Community-Erstgeneration angelegt), keine von Lab selbst gebootstrappte.

```bash
export MMO_SIM_PERSONA_API_BASE_URL="http://127.0.0.1:<test-port>"   # <markiert>
export MMO_SIM_PERSONA_API_KEY="SYNTH-TEST-ONLY"                      # <markiert>
export OPENWEBUI_URL="http://127.0.0.1:<test-port-gm>"                # <markiert>
export OPENWEBUI_API_KEY="SYNTH-TEST-ONLY"                            # <markiert>
export MMO_SIM_GM_OUTPUT_LIMIT_TOKENS="2000"
DATA=<test-verzeichnis-ausserhalb-repo>                               # <markiert>

# Profil api: Persona- UND GM-Rolle laufen ueber eigene Loopback-HTTP-Doubles.
python3 scripts/mmo_sim.py lab start --data-dir "$DATA" \
  --community demo-community --profile api \
  --max-requests 20 --max-seconds 300 --max-usd 2.0 --max-idle-windows 2 \
  --max-wall-seconds 600

python3 scripts/mmo_sim.py lab status --data-dir "$DATA"
python3 scripts/mmo_sim.py lab attach --data-dir "$DATA" --follow
python3 scripts/mmo_sim.py lab stop   --data-dir "$DATA" --reason "Betreiber-Pause"
python3 scripts/mmo_sim.py lab resume --data-dir "$DATA" \
  --community demo-community --profile api \
  --max-requests 20 --max-seconds 300 --max-usd 2.0 --max-idle-windows 2 \
  --max-wall-seconds 600

# Profil hybrid: GM bleibt API-abgerechnet (--max-usd weiterhin Pflicht);
# Personas laufen ueber eine eigene, lokal erzeugte ausfuehrbare Fake-CLI
# (kein echtes `claude`, kein Login, kein bestehender Dienst als Testdouble).
export MMO_SIM_PERSONA_CLI=<eigene-fake-cli-ausfuehrbar>              # <markiert>
export MMO_SIM_PERSONA_ISOLATION_FLAGS=<verifizierte-isolationsflags> # <markiert>

python3 scripts/mmo_sim.py lab start --data-dir "$DATA" \
  --community demo-community --profile hybrid \
  --max-requests 20 --max-seconds 300 --max-usd 2.0 --max-idle-windows 2 \
  --max-wall-seconds 600
```

### Getestetes Betriebssystem und Grenzen

- Getestet unter Linux, VM-Interpreter Python 3.12.3 (dieses Repo/
  Auftragspaket); eine getrennte unabhängige Review lief zusätzlich unter
  Linux/Python 3.13.5 mit separat kopierten (nicht installierten)
  Abhängigkeiten — beide Umgebungen bleiben getrennt ausgewiesen und
  ersetzen sich nicht gegenseitig. Reale Subprozesse mit geschlossenem
  stdin, Loopback-HTTP-Doubles (`127.0.0.1`) für Persona/GM sowie eine
  ersetzte ausführbare Fake-CLI für das Hybrid-Profil (kein echtes `claude`,
  kein Login). Keine Windows-/macOS-/LAN-Abnahme in diesem Block.
- Kein Docker/Cron/Dauerdienst — ein Lab-Lauf ist ein normaler, vom Betreiber
  gestarteter Vordergrundprozess; ein beendeter Prozess rechnet NICHT weiter.
- `--max-wall-seconds` ist eine REALE Wall-Clock-Deadline, getrennt von
  `--max-seconds` (Summe der Requestlatenzen) — Leerlauf/Wartezeit zählt
  gegen `--max-wall-seconds`, nicht gegen `--max-seconds`. Die Deadline wird
  einmalig bei `lab start`/`lab resume` als absoluter Zeitpunkt persistiert
  (`lab.status.json:wall_deadline`) und von `core.admission.
  read_admission_block` vor JEDEM einzelnen Request geprüft (Initiative/
  Consent/Leader/Gast/GM/Reflexion) — nicht nur zwischen zwei Lobbyfenstern
  (Critic-Nacharbeit F2, s. unten).
- Bekannte Einschränkungen dieses Blocks: kein aktiver menschlicher
  Attach-Zugriff (nur passive Ansicht), keine mehreren entfernten Clients,
  keine Mehrprozess-Spielleitung, kein Level-/Vorlaufdialog über Lab.

## Bekannte Lücken (siehe WORKER-REPORT.md für Details)

- Kein echter Modellaufruf in diesem Bauauftrag (Auftragsgrenze) — alle
  Adapter sind an der Prozess-/HTTP-Grenze offline geprüft, nicht live.
- `scripts/launcher.py` weicht ab diesem Block bewusst von der
  repoübergreifenden Bytegleichheit ab (A4, siehe unten).
- Vollständige A01–A28-Testabdeckung mit allen Negativ-/Resume-Pfaden ist
  NICHT vollständig — reduzierter, aber real ausgeführter Kernsatz (siehe
  WORKER-REPORT.md Funktionsmatrix).
- Lokale Mehrmenschen-Runde (11 §8) ist auf Katalog-/Leader-Ebene geprüft,
  die volle TUI-Fokuswechsel-Bedienung ist nicht vollständig ausgebaut.

### Headless-/Lab-Block (2026-09-27) — Stand nach H02/H05/H10-Abnahme (2026-09-30)

- **H-D bewusster Verhaltenswechsel:** ein aktiver Lab-Lock lässt eine
  gewöhnliche TUI jetzt kontrolliert ablehnen (s. oben) — die ÄLTERE externe
  Erhaltprobe `reference/regressions/review_i2_finish.py::test_05_actual_
  cli_with_lab_budget_has_configured_limit_path` (Auftragspaket, NICHT Teil
  dieses Repos) geht noch von der VORHERIGEN Annahme aus, dass ein aktives
  `LabRunner`-Budget eine normale TUI-Runde NICHT vom Schreiben abhält, und
  schlägt deshalb jetzt erwartungsgemäß fehl (kein Regressionsfund, sondern
  die direkte, spezifikationsgemäße Folge von H-D/H06 — der in-Repo-Erhalt-
  test `tests/mmo_sim/test_i1_i2_i3_worker_matrix.py::test_i2_solo_play_
  blocked_when_lab_budget_exhausted`, der `LabRunner` und `TuiSession` im
  SELBEN Prozess konstruiert, bleibt bewusst unverändert grün, s. `lab.
  runner.active_lock_pid`s `exclude_pid`).
- **H05 (2026-09-29 nachgezogen, jetzt abgenommen):** die hier zum Stand
  2026-09-27 als offen benannten Fälle (Stop an der GM-/Reflexionsgrenze,
  `attach --follow`-EOF, echtes SIGTERM) sind durch
  `tests/mmo_sim/test_h05_stop_lifecycle_2026_09_29.py` (P0–P5/N1–N3)
  geschlossen, s. Abschnitt „H05 — `lab attach --follow`/SIGTERM-
  Stopgrenzen" unten. Dieser Absatz ist historisch überholt und bleibt nur
  zur Nachvollziehbarkeit stehen.
- **H10 (2026-09-29/30 nachgezogen, jetzt im festen kontrollierten
  T1–T10-Umfang abgenommen):** gezielte Schreib-/Diagnosefehlerinjektion an
  den neuen Lab-Persistenzstellen ist durch
  `tests/mmo_sim/test_h10_operating_persistence_2026_09_29.py` belegt.
  Insbesondere T7 (Profil `api`) und T8 (Profil `hybrid`) zeigen: ein
  Diagnoseschreibfehler an `lab.last_window.json` bewahrt bereits gültige
  veröffentlichte Saves/Runden/Reflexionen/Finalisierungen unverändert —
  eine danach gestellte neue freiwillige Pauseanfrage ist KEINE zweite
  Ernte/Runde/Saveversion. T9 (bekannter Lauf mit Request-/Tischbezügen,
  aber fehlendem `lab.status.json`) ist ein konkreter Hold VOR jeder
  Bestandsmutation, kein automatisches Neuinitialisieren/Zurücksetzen — der
  Betreiber muss den Zustand prüfen, bevor erneut resumed wird (s. `_run_
  controller`, H10-T9-Guard). T10 (beschädigte Autorität) bleibt bewusst
  UNKLAR statt automatisch repariert. H10 ist unabhängig im festen
  operativen T1–T10-Offlineumfang abgenommen; diese Abnahme hängt nicht vom
  noch offenen H11/H12-Schlussentscheid ab. Kein P2-/v2-/Live-PASS.
- **H02 (im vereinbarten kontrollierten Offlineumfang abgenommen):**
  `tests/mmo_sim/test_h02_vollreise_profiles_2026_09_28.py` belegt die große
  bestätigte Community mit mehr als fünf KI-Personas und geschützter
  menschlicher Identität, den freiwilligen Zweiertisch mit nominierter
  anderer Leaderpersona sowie vollständige API- und Hybrid-/API-SL-Reisen
  über echte CLI-/Subprozessgrenzen. Nach den Importantworten folgen drei
  weitere GM-Spielantworten (zusammen G0–G4), individuelle Saves/Reflexionen
  und eine neue freiwillige Gelegenheit. Der CLI-Nachweis ist damit nicht
  auf Self-Leader oder eine reine Zwei-Persona-Community beschränkt.
  Eine allgemeine 1:1-Wiederholung der vollständigen TUI-/A01–A28-Matrix
  bleibt davon getrennt ein P2-/v2-Restpunkt, keine neu geöffnete H02-Lücke
  und keine bereits erteilte P2-/v2-Gesamtabnahme.

### Critic-Nacharbeit (2026-09-27) — F1–F4 behoben

Der End-Critic dieses Bau-GO fand vier Befunde (CRITIC-REPORT.md), alle
selbst nachgearbeitet:

- **F1** (`lab status`/`lab attach` stürzten bei korruptem `lab.status.json`
  ab, H-C-Verstoß): `lab.cli._status_payload` fängt `OSError`/
  `JSONDecodeError`/`TypeError` jetzt ab und meldet `run: "unklar"` statt
  eines Tracebacks. `lab.runner.read_status` selbst bleibt für seine
  bestehenden Schreibpfad-Aufrufer (`LabRunner.__init__`/`record_turn`/
  `_write_status`) unverändert fail-closed (Ausnahme propagiert).
- **F2** (`--max-wall-seconds` nur zwischen Lobbyfenstern geprüft, nicht vor
  jedem Request): `LabBudget.max_wall_seconds` (neu, optional) wird von
  `LabRunner.start()` einmalig als absolute `wall_deadline` in
  `lab.status.json` persistiert; `core.admission.read_admission_block`
  prüft sie jetzt bei JEDEM Request frisch von der Platte (s. oben,
  „Getestetes Betriebssystem und Grenzen"). `lab.runner.compute_stop_state`
  bündelt Stop-Flag-/Budget-/Wall-Clock-Berechnung für `LabRunner.
  should_stop()` UND diesen Gate-Check gemeinsam.
- **F3** (`lab status` zeigte `stop_requested: false` trotz aktivem externen
  Stop, da `LabRunner.stop()`/`request_stop()` nur die Stop-Flag-Datei
  schreiben, nie `lab.status.json`): `_status_payload` berechnet
  `stop_requested`/`stop_reason` jetzt über `compute_stop_state` frisch von
  der Platte, statt das eingefrorene `LabStatus`-Feld vom letzten
  `_write_status()`-Aufruf zu zeigen.
- **F4** (inkonsistenter `exclude_pid`-Einsatz zwischen den beiden H-D-Guard-
  Aufrufstellen): `ui/tui.py:_cmd_lobby_initiative` übergibt jetzt wie
  `_cmd_local_round` `exclude_pid=os.getpid()` an `active_lock_pid`.

Vollständiger Befund-/Belegtext: `CRITIC-REPORT.md` (Worker-Austauschordner,
nicht Teil dieses Repos).

## A4 — `scripts/launcher.py`-Drift (bewusst, dokumentiert)

`scripts/launcher.py` ist repoübergreifend als byte-identisch gedacht
(`launcher-sync.sh`-Gate über 5 Bausätze). Dieser Block fügt einen optionalen
Projekt-Hook-Import (`mmo_sim_launcher_hook`, analog zum bestehenden
`rite_module`-Muster) und einen Menüpunkt `[M]` hinzu. Das erzeugt bewusst und
erwartungsgemäß Drift gegenüber den anderen 4 Bausätzen (ARXION, Privacy
Odyssey, Unfallhelfer, agent0) — KEIN Fehlalarm des Drift-Checks, KEINE
automatische Angleichung der anderen Repos in diesem Block (Auftragsgrenze).

## H05 — `lab attach --follow`/SIGTERM-Stopgrenzen (2026-09-29)

Zwei eng belegte Korrekturen in `mmo_sim/lab/cli.py:_cmd_attach`/
`_run_controller`, jeweils aus einem real reproduzierten roten Testfall in
`tests/mmo_sim/test_h05_stop_lifecycle_2026_09_29.py` (P3/P4):

- **`lab attach --follow`** beendet sich jetzt auch bei echtem stdin-EOF
  selbst (der bestehende Hilfetext "bis Ctrl-C/EOF" nannte das schon,
  implementiert war bislang nur Ctrl-C). Ein `--follow`-Aufruf mit
  `stdin=/dev/null` (z. B. in einem Hintergrundjob ohne angeschlossenes
  Terminal) beendet sich deshalb ab jetzt ebenfalls sofort nach der ersten
  Ausgabe — das ist die dokumentierte Absicht, kein Fehler; ein dauerhaft
  laufender Hintergrund-Observer braucht eine offene, nicht geschlossene
  stdin-Pipe (oder `--max-updates`/eigene Wiederholung von außen).
- **Ein reales `SIGTERM`** an den `lab start`/`resume`-Controllerprozess löst
  jetzt denselben kontrollierten Pausepfad wie Ctrl-C/SIGINT aus (`lab.stop`
  mit wahrheitsgemäßem Grund, Lock-/Statusfreigabe, `lab resume` später
  möglich) — vorher tötete SIGTERM den Prozess ohne jede Aufräumung
  (Python-Standardaktion), `lab status` zeigte danach fälschlich weiter
  `running: true`. Der Signalhandler ist ausschließlich für die aktive
  Controllerphase installiert und wird danach wieder auf den vorherigen
  Zustand zurückgesetzt.

Unverändert: `SIGKILL` bleibt nicht abfangbar (per Definition) — eine damit
unterbrochene Anfrage bleibt nach einem `lab resume` bewusst unbekannt/offen,
kein automatischer zweiter Versand, keine erfundene Antwort. Ein bereits
gebundener, mit offenem Reflexions-/Abschlussauftrag versehener Tisch wird
von `lab resume` aus demselben Grund NICHT automatisch weitergespielt
(`core/store.py:find_bound_active_unplayed_table` schließt das bewusst aus)
— das ist der bereits vorhandene sichere Hold, keine neue Funktion.

<!-- A24-LOCAL-ROUND-BEGIN -->
## A24 — Lokale-Runde-Anzeige und gefuehrter Einrichtungsweg (2026-10-01)

Zwei eng begrenzte Korrekturen in `mmo_sim/ui/tui.py`, beide ausschliesslich
innerhalb `_cmd_local_round`/`run`/`render_boot_menu` bzw. neuen
`_cmd_local_round_setup`/`_local_round_*`-Methoden (A24-SCOPE):

- **Sechser-Ablehnung nennt jetzt die tatsaechliche Policy-Spanne**: statt
  des wiederverwendeten Erfolgstexts ("erste vollstaendig angenommene Offer
  ...") zeigt eine Groessenueberschreitung die angefragte Spielerzahl und den
  tatsaechlichen `ZeitrissTableSizePolicy`-Bereich (`min_size`..`max_size`),
  z. B. "6 Spieler angefragt; zulaessig sind 1 bis 5 ...". Keine
  Policy-Abschwaechung, keine automatische Kuerzung.
- **Geteilter Anzeigecursor**: `_HumanDriver.decide` zeigt jetzt ALLE seit
  dem letzten Prompt empfangenen `sl_log`-Eintraege in Reihenfolge (nicht nur
  den letzten) — mehrere aufeinanderfolgende KI-Gastimporte fallen dadurch
  nicht mehr aus der gemeinsamen menschlichen Anzeige. Keine fremden
  Tische/privaten States.
- **Neuer gefuehrter Menuepunkt `[g]`** ruft `_cmd_local_round_setup()` auf:
  fragt "allein mit KI" oder "mehrere Menschen am Geraet", laesst vorhandene
  lokale Teilnehmer sichtbar auswaehlen bzw. ueber die vorhandene
  `ParticipantRegistry` bewusst neu registrieren, zeigt pro Mensch die eigene
  Figur aus vorhandenen Zuordnungen (`_resolve_member`) und laesst sie
  ausdruecklich bestaetigen (keine Dummyfigur, keine Autoauswahl aus fremdem
  Current — eine fehlende Figur fuehrt zu einem klaren Rueckweg ueber den
  eigenen `[n]`/`[i]`-Durchgang), zeigt die ausgewaehlten KIs, den
  angefragten Leader (der aufrufende Mensch ODER eine angefragte KI) und eine
  Zusammenfassung von 1–5 Gesamtspielern einschliesslich Leader zur letzten
  bewussten Startwahl. Diese Auswahl ist noch KEINE KI-Zustimmung und keine
  Tischaufnahme. Vor Uebergabe des geteilten Terminals an einen WEITEREN
  Menschen werden dessen Teilnehmer-ID und eigene Figur eindeutig angezeigt
  und eine bewusste Uebernahme verlangt; Abbrechen/EOF ist an jedem Schritt
  ein klarer Halt ohne KI-Ersatz und ohne Aenderung. Danach ruft die
  Einrichtung **unveraendert** `_cmd_local_round` mit der fertigen
  Tokenliste auf — Einladungs-/Consentweg, Tischanlage und Kernrunde bleiben
  strukturell exakt dieselben wie beim bestehenden `l`-Tokenweg (der
  weiterhin unveraendert kompatibel bleibt, inklusive bestehender
  Skripte/Tests). `[g]` fuehrt keine neue Spielengine/Fokuspersistenz ein;
  eine Fokusaktion aendert weder `table.leader` noch Mitgliedschaft/Figur.
- **Echte In-Runde-Uebergabe (2026-10-01, Nachzug; Fokuskontinuitaet
  2026-10-01 nachgezogen)**: die bisherige Uebergabebestaetigung griff nur
  EINMAL vor Rundenstart. Der gefuehrte Weg (`[g]`) fuehrt jetzt zusaetzlich
  einen FLUECHTIGEN, nur fuer den jeweiligen Rundenaufruf gueltigen
  Fokuszeiger (reine Methodenvariable, keine Datei, kein `self`-Attribut,
  kein `self.participant_id`-Umschreiben): dieser Zeiger startet NICHT bei
  `None`, sondern bei der zuletzt im Setup/Consent bestaetigten Person —
  eine einmalige Setup-Uebergabe bleibt dadurch auch ueber den ERSTEN
  Spielbeitrag hinweg gueltig, statt beim Rundeneintritt stillschweigend
  verworfen zu werden. Vor JEDER tatsaechlichen Eingabe eines ANDEREN
  Menschen als des zuletzt bestaetigten — inklusive der Ruecklaufergabe an
  den aufrufenden Menschen — zeigt `_local_round_handoff` erneut Name/
  Teilnehmer-ID/Figur und verlangt eine bewusste Uebernahme. Nur bei einem
  tatsaechlichen Akteurwechsel, nicht bei gleichbleibender Eingabe und
  nicht bei jedem Aufruf blind. Ablehnung/EOF WAEHREND eines bereits
  bestehenden Tisches beendet nur die geteilte Eingabe ("Tisch und
  bisherige Daten bleiben erhalten; kein KI-Ersatz") und behauptet KEINEN
  Nichtstart mehr; Ablehnung/EOF VOR Tischstart (Setup) bleibt "kein
  Spielstart". Gilt fuer beide gefuehrten Konstellationen (Human-Leader/API,
  KI-Leader/Hybrid+API-SL); der bestehende `l`-Tokenweg bleibt unveraendert
  OHNE neue Pflichtzeilen kompatibel (nur `guided=True`, von
  `_cmd_local_round_setup` gesetzt, aktiviert diesen Mechanismus).
- **Aktive Testdouble-Validierung (2026-10-01, testlokal; auf exakte
  Bindung verschaerft 2026-10-01)**: die beiden A24-Testdoubles
  (`SequencedHTTPServer`, Fake-CLI in `tests/mmo_sim/_a24_local_support.py`)
  pruefen vor jeder Erfolgsausgabe den mitgelieferten
  `[OEFFENTLICHE_TISCHSICHT]`-Block gegen den tatsaechlich erwarteten
  Kontext, nicht nur gegen dessen Form: der Tischname muss EXAKT (nicht nur
  als gemeinsamer Praefix) der echten Produktformel aus Leader + sortierten
  Mitgliedern entsprechen, und jeder `sl_log`-Eintrag muss VOLLSTAENDIG
  (nicht nur im `Szene N:`-Praefix) einem der tatsaechlich im Testcode
  verwendeten GM-Erzaehltexte fuer genau seinen `turn_idx` entsprechen oder
  den Abschlussmarker mit exakt gebundenem `table_id=`/`section_id=`
  tragen. Ein sonst gueltiger Tischname mit angehaengtem Fremd-Suffix und
  ein nach unveraendertem `Szene N:`-Praefix ausgetauschter Volltext werden
  dadurch jetzt erkannt und abgelehnt, nicht nur ein voellig fremder
  `table_id`. Reine Testinfrastruktur, kein Produktverhalten.
- **Echter R3-Mittelsnapshot (2026-10-01, testlokal)**: `run_process_paced`
  + `snapshot_run_tree` (`tests/mmo_sim/_a24_local_support.py`) treiben den
  echten `scripts/mmo_sim.py`-Subprozess zeilenweise, JEDE Eingabe erst
  NACH tatsaechlich beobachtetem zugehoerigem Prompt im stdout (keine feste
  Wartezeit, keine Ruhephasen-Heuristik). `test_a24_r3_midwait_active_table_
  snapshot` sichert damit einen echten Dateisystem-Zwischenschnappschuss
  genau am ersten In-Runde-Eingabepunkt des zweiten Menschen: Tisch bereits
  vollstaendig angelegt und `active` (NICHT `closed`), `sl_log` echt
  partiell. Reine Testinfrastruktur, kein Produktverhalten.
<!-- A24-LOCAL-ROUND-END -->
