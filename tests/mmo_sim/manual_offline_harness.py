#!/usr/bin/env python3
"""
tests/mmo_sim/manual_offline_harness.py — G06 (ZEITRISS Terminal UX-1,
Wiederanlauf W9/W19-F03): offener, spielbarer Offlinezugang fuer T.

Startet den ECHTEN `scripts/mmo_sim.py`-Prozess interaktiv (geerbtes
stdin/stdout -- T tippt direkt in sein eigenes Terminal, kein Pipe/Capture),
mit ZWEI isolierten Fakes an den aeusseren HTTP-Transportgrenzen: der
GM-/SL-Grenze (`CreationCapableSmartGmServer`, `tests/mmo_sim/
_ux1_r5_synthetic_creation_support.py` -- derselbe inhaltsgebundene
Loopback-Mechanismus wie `e2e_real_subprocess_dialog.py:SmartGmServer`, um
GENAU EINEN zusaetzlichen, ebenfalls inhaltsgebundenen Zweig fuer eine
ENDLICHE Erschaffung erweitert) UND der Persona-Grenze (W25,
`tests/mmo_sim/_ux1_r6_persona_loopback_support.py:PersonaLoopbackServer` --
derselbe inhaltsgebundene Mechanismus, dient T, falls im Hauptmenue eine
namensbasierte Einladung einer bekannten KI versucht wird: deterministisch
accept, echte unterscheidbare Spielzuege). Kein Fake-Client, kein
Produkt-Offlinefallback -- der komplette Launcher-/TUI-/Runtime-/
Adaptercode laeuft real durch einen echten, eigenstaendigen Python-
Subprozess, exakt wie bei einem echten Spielversuch.

W19/F03-Aenderung gegenueber der vorherigen Fassung: T bekommt KEINE
vorregistrierte, vorab abgeschlossene Figur mehr (kein
`onboard_human_figure`-Save-Injektions-Shortcut) -- T erschafft die eigene
Figur ECHT ueber den normalen Produktweg ('[n]' im Hauptmenue -> realer
SL-Erschaffungsdialog gegen die Fake-SL). Die Fake-SL antwortet an der
Erschaffungsgrenze endlich (eine Frage, dann ein gueltiger v7-Save) --
kein Rezept, welche Antwort T geben muss; jede Antwort fuehrt zum selben
endlichen Ergebnis.

R7/W27 (Generalbefund R6P01, BRIEF-W27.md): T ist NICHT mehr auf Solo
beschraenkt -- T darf im Hauptmenue frei ueber 'l <id> ...' beliebige
bekannte KI (ueber die Persona-Grenze) UND/ODER eine zweite lokale Person
einladen (2+3 etc.), UND nach einem echten Abschluss eine zweite Runde
beginnen. Der GM-Double kennt dabei NIE einen fest vorgegebenen
`table_id`/`section_id` -- er leitet den tatsaechlichen eigenen Tisch bei
jedem Abschlussversuch frisch aus dem persistierten Zustand des eigenen
`run_dir` ab (`_ux1_r5_synthetic_creation_support.
resolve_own_open_table_id`, dynamischer Modus), genau wie es der echte
Client selbst tut -- vorher adressierte ein beim Start fest gesetzter
Solo-`table_id` nach einer Einladung/zweiten Runde den FALSCHEN Tisch
(Abschnitt erreichte nie `closed`).

R7/W30 (Reparatur R7P02, BRIEF-W30.md): der obige Freiheitsgrad lief in
der Praxis leer -- dieser Harness registrierte bislang NUR den einen
menschlichen Leader und machte KEINE KI-Persona ueber den echten
Produktweg tischbereit; 'l persona:medic' scheiterte deshalb immer mit
"keine abgeschlossene Figur vorhanden". Jetzt wird beim Setup eine
bekannte, klar SIMULIERT markierte KI-Spielgemeinschaft (`sniper`/`tech`/
`medic`, dieselben Fixtures wie die bestehenden A24-Produkttests unter
`internal/qa/harness/lobby/fixtures/saves/`) ueber exakt denselben
Produktweg wie `tests/mmo_sim/_a24_local_support.py:bootstrap_six_persona_
community` + `make_ready` (Community-Bootstrap + Onboarding +
`core.store.publish_current_save`) tischbereit gemacht -- kein Save-
Inject in eine laufende Runde, keine Markergrammar-/Runtime-/
Produktdefault-Aenderung. Dadurch sind sie sowohl ueber 'l persona:<id>'
ALS AUCH ueber das gefuehrte '[spielen] -> Meine KI-Spielgemeinschaft'-
Menue einladbar; T erschafft weiterhin die eigene Figur ECHT ueber
'[n]'/[charaktere], eine zweite lokale Person ECHT ueber 'registrieren'
bzw. 'neu:<Name>' in der Gruppenzusammenstellung (beides bestehende,
unveraenderte Produktwege) -- eine 2+3-Runde (2 Menschen + 3 KI) ist
dadurch tatsaechlich bildbar.

## Start

    python3 tests/mmo_sim/manual_offline_harness.py

Die Ausgabe nennt VOR dem Start NUR die eigene Teilnehmer-ID und den
`--data-dir`-Pfad -- KEIN Loesungsrezept (R06/UX23, REVIEW.md §R06: ein
vorab gedrucktes Tastenrezept ist kein unbeeinflusster Erstversuch mehr).
Ab dem Hauptmenue bedient sich der echte, unveraenderte `scripts/mmo_sim.py`-
Client normal; welche Wege zum Ziel fuehren (inkl. Figurerschaffung ueber
'[n]'/[charaktere]), ist Teil der zu beobachtenden Aufgabe, nicht vorab
verraten.

Entwickler-/Operator-Verifikationsrezept (NUR fuer Main-Pre-T-Nachweis,
NICHT im T-sichtbaren Pfad): falls dokumentiert, liegt es im
Reportverzeichnis des jeweiligen Workers (kein fester, uebergreifender
Dateiname) -- nicht in diesem Testmodul, nicht im Start-Banner, nicht in
stdout.

`--data-dir` (Default: frischer Temp-Ordner, Pfad wird ausgegeben) kann fuer
einen spaeteren "Fortsetzen"-Testlauf (ECHTER, SEPARATER Prozess) wieder-
verwendet werden (derselbe `--participant`/Marker-Mechanismus wie im echten
Produkt) -- Erschaffungsfortschritt UND ein bereits laufender Abschnitt
bleiben dabei ueber den normalen Produktweg erhalten/fortsetzbar.

R7/W32 (F01/F02, GENERALREVIEW-R7.md §3/§4, BRIEF-W32.md): zwei Reparaturen
NUR an diesem Testzugang selbst, kein Core-/Store-/Ledgerfix.

F01 -- bislang rief dieser Harness bei JEDEM Start (auch einem passiven
Neustart eines bereits bespielten `--data-dir`) unbedingt `sup.make_ready`
fuer sniper/tech/medic auf; `make_ready` laedt dabei IMMER die Anfangs-
fixtur und publiziert sie erneut (`core.store.publish_current_save`) --
ein fortgeschrittener KI-`Current` (z.B. Level 7, eigener Marker) wurde
dadurch beim naechsten Harness-Start wieder auf
`fixture-<key>-initial-001` zurueckgesetzt, obwohl der normale
`scripts/mmo_sim.py`-Start ihn erhaelt (R7P01, belegt in
`evidence/runs/probe_harness_restart/observation.json`). Fix: Erst-
vorbereitung (`is_fresh_setup`, noch kein `harness_participant.json`) und
passiver Neustart (Marker bereits vorhanden) werden jetzt getrennt. Bei
einem Neustart klassifiziert `_ai_persona_state()` (reine Lesefunktion,
nutzt ausschliesslich bestehende Produktlesefunktionen) jede KI-Persona
als "absent" (noch nie beruehrt -- `make_ready` darf sicher einmalig
laufen), "complete" (vollstaendiger, konsistenter Bestand -- bleibt
UNBERUEHRT, `make_ready`/`publish_current_save` laufen NICHT erneut
darueber) oder "inconsistent" (teilweiser/widersprechender Bestand --
klarer Setup-HOLD, `return 3` VOR jedem weiteren Zugriff, kein stilles
Neuanlegen/Auffuellen/Reparieren). Frische Erstvorbereitung bleibt
unveraendert moeglich.

F02 -- die vier `logs/*.jsonl` wurden am Prozessende per `write_text` NEU
geschrieben; ein Folgeprozess (auch ein Null-Call-Neustart) vernichtete so
die vorigen Callbelege. Fix: jeder Harness-Prozess bekommt ueber
`_next_exclusive_run_logs_dir()` eine eigene, bisher nicht existierende
`logs/run-NNNN/`-Unterablage und schreibt seine vier `.jsonl`-Dateien
ausschliesslich dort -- auch bei null Calls (eigene, aber leere Dateien =
explizit belegter Null-Call-Lauf). Frueher geschriebene `run-NNNN/`-Ordner
werden nie wieder geoeffnet, bleiben bytegleich erhalten. Die
Abschlussausgabe nennt den konkreten Logordner dieses Laufs.

R9/W34 (F03, BRIEF-W34.md): `is_fresh_setup` war bislang WOERTLICH
"Markerdatei fehlt" -- fehlte der Marker aus IRGENDEINEM Grund (geloescht,
nie geschrieben, unlesbar), wertete Zeile 277 (alt) jede KI-Persona
unbedingt als `"absent"`, OHNE `_ai_persona_state()` ueberhaupt zu
befragen. War zu diesem Zeitpunkt aber bereits ein fortgeschriebener
Produktbestand vorhanden (Registry/Onboarding/States/Current aus einem
frueheren Lauf, nur die Markerdatei selbst manuell entfernt), republizierte
`sup.make_ready()` trotzdem die Anfangsfixtur ueber den fortgeschrittenen
Stand (belegt in `evidence/missing-marker-observation.json`:
`missing_marker_preserves_progress=false`, `new_testleader_created=true`).
`write_test_profile()` UND die Markerneuanlage liefen dabei zusaetzlich
VOR jeder Bestandspruefung.

Fix: eine vollstaendige, AUSSCHLIESSLICH lesende Bestandsentscheidung
(`_classify_harness_root()`) laeuft jetzt VOR jedem Write (vor
`write_test_profile`, `register_human`/Markerschreiben,
`bootstrap_six_persona_community`, `make_ready`) und unterscheidet drei
Klassen: `FRESH_EMPTY` (wirklich leerer Root -- kein Marker UND kein
begonnener Produktbestand, Erstvorbereitung bleibt unveraendert erlaubt),
`EXISTING_CONSISTENT` (gueltiger Marker + aufloesbarer Leader + keine
widersprechende KI-Persona -- passiver Start, `make_ready` nur fuer
tatsaechlich noch nie beruehrte Personas) und `SETUP_HOLD` (Marker fehlt/
unlesbar/falsches Schema/staler Leader BEI einem bereits begonnenen
Bestand, ODER irgendeine KI-Persona widerspruechlich -- `return 3` VOR
jedem weiteren Zugriff, keine neue Person, kein Ersatzmarker, kein
Teilwrite). Ein reiner `logs/`-Ordner zaehlt dabei NICHT als begonnener
Bestand (Logreste sind keine Spielberechtigung). Zusaetzlich behebt dies
einen bisher unbelegten Teilwrite-Pfad: die alte Schleife prueft
Inkonsistenz ERST pro Persona waehrend des Schreibens -- bei z.B.
sniper=absent/medic=inconsistent waere sniper bereits per `make_ready`
beschrieben worden, bevor der Abbruch bei medic ausgeloest wird.
`_classify_harness_root()` berechnet ALLE drei Personas-Zustaende VORHER,
also vor jedem Write."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from mmo_sim.core.admission import write_test_profile, read_admission_block  # noqa: E402
from mmo_sim.domain.zeitriss import community_bootstrap  # noqa: E402
from _ux1_r5_synthetic_creation_support import CreationCapableSmartGmServer  # noqa: E402
from _ux1_r6_persona_loopback_support import PersonaLoopbackServer  # noqa: E402
import _a24_local_support as sup  # noqa: E402


def _ai_persona_state(sup, persona_key, onboarding_dir, states_dir, run_dir) -> str:
    """R7/W32 (F01): rein LESENDE Einstufung eines bestehenden KI-Persona-
    Bestands fuer einen passiven Harness-Neustart -- "absent" (noch nie
    beruehrt, `make_ready` darf sicher einmalig laufen), "complete"
    (vollstaendiger, konsistenter Bestand, `make_ready`/
    `publish_current_save` duerfen NICHT erneut darueber laufen) oder
    "inconsistent" (teilweiser/widersprechender Bestand -- klarer Setup-
    HOLD, kein stilles Auffuellen/Reparieren). Nutzt ausschliesslich
    bestehende, unveraenderte Produktlesefunktionen (`onboarding.peek`,
    `PersonaStateStore.load_state`, `core.store.
    load_current_save_or_raise`) -- keine neue Schreibautoritaet.

    R11/W38 (R10-F01/R10P03, BRIEF-W38.md): `_EXPECTED_READ_ERRORS` faengt
    zusaetzlich zu `FileNotFoundError`/`CurrentSaveUnavailableError`
    JEDE erwartete Datei-/Parse-/Struktur-/Zuordnungsstoerung dieser drei
    Leserwege gezielt ab und stuft sie als "inconsistent" ein (klarer
    SETUP_HOLD beim Aufrufer), statt sie ungefangen bis zum Top-Level
    propagieren zu lassen. Belegt an `states/tech.json` mit falschem
    JSON-Typ `[]` (gueltiges JSON, aber keine Persona-State-Abbildung):
    `PersonaStateStore.load_state()` selbst liefert dabei die Liste OHNE
    Fehler zurueck (reiner `json.load`) -- erst `core.store.
    load_current_save_or_raise()`s interne Referenzkette versucht
    `state.get(...)` auf dieser Liste und wirft dabei tatsaechlich
    `AttributeError` ('list' object has no attribute 'get'), NICHT
    `CurrentSaveUnavailableError` (empirisch reproduziert, kein Rateversuch).
    `TypeError`/`KeyError`/`ValueError`/`json.JSONDecodeError` (Teilmenge von
    `ValueError`) decken dieselbe Fehlerklasse fuer verwandte Strukturfehler
    an `onboarding.peek()` (z.B. `OnboardingState(**data)` bei einer Liste
    statt eines Objekts) bzw. an einer kuenftig anders defekten
    Referenz/Sequenz ab. Bewusst KEINE nackte `except Exception` -- nur
    diese belegten, strukturell erwartbaren Fehlklassen; jede andere
    Ausnahme propagiert weiterhin ungefangen."""
    _EXPECTED_READ_ERRORS = (AttributeError, KeyError, TypeError, ValueError, OSError)
    try:
        onboarding_state = sup.onboarding.peek(onboarding_dir, persona_key)
    except _EXPECTED_READ_ERRORS:
        return "inconsistent"
    ps_store = sup.PersonaStateStore(schema_path=sup.SCHEMA)
    try:
        persona_state = ps_store.load_state(persona_key, states_dir=states_dir)
    except FileNotFoundError:
        persona_state = None
    except _EXPECTED_READ_ERRORS:
        return "inconsistent"
    try:
        current_save = sup.core_store.load_current_save_or_raise(
            run_dir, persona_key, ps_store, states_dir=states_dir,
        )
    except sup.core_store.CurrentSaveUnavailableError:
        return "inconsistent"
    except _EXPECTED_READ_ERRORS:
        return "inconsistent"
    if onboarding_state is None and persona_state is None and current_save is None:
        return "absent"
    if (
        onboarding_state is not None and onboarding_state.status == "completed"
        and persona_state is not None and current_save is not None
        and persona_state.get("persona_key") == persona_key
    ):
        return "complete"
    return "inconsistent"


def _read_marker(marker_path: Path) -> tuple[str, "str | None"]:
    """R9/W34 (F03): rein LESENDE Markerklassifikation, OHNE jeden
    Schreibversuch. Liefert `("absent", None)` (Datei existiert nicht),
    `("unreadable", None)` (Datei existiert, aber nicht parsebares JSON /
    kein Objekt / `leader_id` fehlt oder ist kein nichtleerer String) oder
    `("valid", leader_id)`."""
    if not marker_path.is_file():
        return "absent", None
    try:
        payload = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return "unreadable", None
    if not isinstance(payload, dict):
        return "unreadable", None
    leader_id = payload.get("leader_id")
    if not isinstance(leader_id, str) or not leader_id:
        return "unreadable", None
    return "valid", leader_id


def _leader_is_bound(sup, registry_dir: Path, leader_id: str) -> bool:
    """R9/W34 (F03): rein LESENDE Pruefung, ob `leader_id` noch eine
    aufloesbare Teilnehmeridentitaet in der Registry ist -- nutzt
    ausschliesslich die bestehende `ParticipantRegistry.load_participant`-
    Lesefunktion (liefert `None` bei fehlender Datei, wirft `ValueError` bei
    strukturell ungueltigem Datensatz, beides = nicht gebunden). Der
    Konstruktor von `ParticipantRegistry` legt `registry_dir` an
    (`mkdir(exist_ok=True)`) -- wird deshalb NUR aufgerufen, wenn
    `registry_dir` bereits existiert, damit diese reine Leseentscheidung
    selbst kein neues Verzeichnis anlegt."""
    if not registry_dir.is_dir():
        return False
    registry = sup.ParticipantRegistry(registry_dir)
    try:
        participant = registry.load_participant(leader_id)
    except ValueError:
        return False
    return participant is not None


def _root_has_started_product_bestand(
    registry_dir: Path, onboarding_dir: Path, states_dir: Path, catalog_dir: Path, run_dir: Path,
) -> bool:
    """R9/W34 (F03): rein LESENDE Pruefung, ob dieses `--data-dir` bereits
    IRGENDEINEN Produktbestand begonnen hat (Registry-Teilnehmer,
    Onboarding-Auftraege, Persona-States, Katalogdateien, Current-Saves
    ODER Community-Roster) -- unabhaengig vom Harness-Marker. Ein reiner
    `logs/`-Ordner (eigene Harness-Bookkeeping-Ablage, s.
    `_next_exclusive_run_logs_dir`) zaehlt bewusst NICHT -- Logreste sind
    keine Spielberechtigung.

    R10/W37 (C17-F01, BRIEF-W37.md): zusaetzlich zaehlt ein bereits
    VORHANDENES Testprofil (`run/lab.status.json` ODER `run/lab.stop`,
    offen oder geschlossen) ebenfalls als begonnener Bestand -- ohne
    diesen Check wurde ein Root OHNE Marker, aber mit einem bereits
    existierenden Profil, bisher als `FRESH_EMPTY` eingestuft und
    `write_test_profile()` lief erneut, was eine zuvor bewusst
    GESCHLOSSENE Testfreigabe stillschweigend auf `provider_free=True`
    zurueckgesetzt haette. Mit diesem Check liefert der marker-absent-
    Zweig in `_classify_harness_root()` stattdessen `SETUP_HOLD` (kein
    `write_test_profile`-Aufruf mehr), sobald irgendein Profil bereits da
    ist.

    R11/W38 (R10-F01/R10P01, BRIEF-W38.md): die bisherige Pruefung zaehlte
    NUR die oben einzeln aufgezaehlten Unterpfade (Registry/Onboarding/
    States/Katalog/`run/current_saves`/`run/community`/`lab.status.json`/
    `lab.stop`) -- `run/requests/<id>.json` (echte Request-Reservierung,
    `core.request_ledger.begin()` schreibt `reserved`->`sent` VOR dem
    eigentlichen Transport, s. dortiges Modul) blieb dabei UNGEPRUEFT: ein
    Root mit genau einer solchen reservierten Requestdatei und sonst
    nichts galt bisher faelschlich als `FRESH_EMPTY`, obwohl bereits eine
    echte, nicht abgeschlossene Produktoperation existiert. Fix: GENERISCHE
    Pruefung ALLER Dateien unter `data_dir` (`run_dir.parent` -- derselbe
    Root, den `main()` als `--data-dir` fuehrt UND an `scripts/mmo_sim.py`
    weitergibt), NICHT mehr nur der einzeln benannten Unterpfade. Das
    erfasst `run/requests` automatisch mit, zusaetzlich jede Tisch-
    (`run/tables`), Abschnitts- (`run/completion`) oder sonstige
    vorhandene Produktdatei im `--data-dir` -- auch einen unbekannten/
    beschaedigten Dateirest, der sich keiner der bekannten Kategorien
    zuordnen laesst (FRESH_EMPTY ist eine POSITIVE Feststellung eines
    wirklich unbegonnenen Roots, kein Default fuer "nicht explizit
    erkannt"). Ausgenommen bleiben NUR der eigene `logs/`-Ordner (reines
    Harness-Bookkeeping, s. `_next_exclusive_run_logs_dir` -- `main()`
    legt dort bereits VOR dieser Pruefung einen neuen, noch leeren
    `logs/run-NNNN/`-Ordner an; Logreste sind keine Spielberechtigung) und
    -- naturgemaess, weil hier ausschliesslich tatsaechliche Dateien
    gezaehlt werden -- nachweislich leere Scaffold-Verzeichnisse (z.B.
    von `core.store.Lobby.__init__` vorab per `mkdir(exist_ok=True)`
    angelegte, aber noch nie beschriebene `tables/`/`completion/`/
    `current_saves/`-Ordner).

    `os.walk(..., followlinks=False)` statt `Path.rglob` -- KEINE
    Symlink-Verfolgung (ein symlinkter Unterordner wird nicht betreten,
    bleibt aber als Eintrag sichtbar) UND keine Suche ausserhalb von
    `data_dir`. Rein lesend, kein Schreibzugriff, kein Verzeichnis wird
    dabei angelegt. Die Parameter `registry_dir`/`onboarding_dir`/
    `states_dir`/`catalog_dir` bleiben Teil der Signatur (unveraenderter
    Aufruf aus `_classify_harness_root()`), werden fuer diese generische
    Pruefung aber nicht mehr einzeln gebraucht -- sie liegen alle
    nachweislich unter `data_dir` und werden von der generischen
    Dateisuche automatisch mit erfasst."""
    data_dir = run_dir.parent
    if not data_dir.is_dir():
        return False
    for dirpath, dirnames, filenames in os.walk(data_dir, followlinks=False):
        if Path(dirpath) == data_dir and "logs" in dirnames:
            dirnames.remove("logs")
        if filenames:
            return True
    return False


def _classify_harness_root(
    sup, marker_path: Path, registry_dir: Path, onboarding_dir: Path, states_dir: Path,
    catalog_dir: Path, run_dir: Path, ai_personas: tuple,
) -> tuple:
    """R9/W34 (F03, BRIEF-W34.md) + R10/W36 (BRIEF-W36.md, R9-F01):
    VOLLSTAENDIGE, rein LESENDE Bestandsentscheidung fuer den GESAMTEN
    eigenen Root -- VOR JEDEM Write (vor `write_test_profile`,
    `register_human`/Markerschreiben, `bootstrap_six_persona_community`,
    `make_ready`). Liefert `(klasse, leader_id_oder_None,
    hold_grund_oder_None, persona_states)`.

    Klassen:
      FRESH_EMPTY -- kein Marker UND kein begonnener Produktbestand:
        explizite Erstvorbereitung (inkl. `write_test_profile`,
        `register_human`+Marker, `bootstrap_six_persona_community`,
        `make_ready` fuer alle drei Personas) bleibt unveraendert ERLAUBT,
        AUSSCHLIESSLICH in diesem Zweig.
      EXISTING_CONSISTENT -- gueltiger Marker + aufloesbarer Leader + ALLE
        DREI KI-Personas "complete" (R10/W36-Verschaerfung: ein
        passiver Neustart darf keine einzige Persona mehr "nachtraeglich"
        ueber `make_ready` auffuellen, auch wenn sie bisher nur "absent"
        war -- s. R9-F01/R9P02) + (R11/W38, R10P02) eine tatsaechlich
        VOLLSTAENDIG abgeschlossene Community-Bootstrap-Transaktion
        (`community_bootstrap.peek(community_dir, f"community-{leader_id}")
        .already_completed is True` -- rein lesend, dieselbe unveraenderte
        Produktfunktion) + eine VORHANDENE, OFFENE Testfreigabe
        (`read_admission_block(run_dir)` rein lesend, nicht blockiert).
        Keine weiteren Writes: kein `write_test_profile` (keine
        Neu-Autorisierung einer evtl. bereits geschlossenen Freigabe, s.
        R9-F01/R9P01), kein `bootstrap_six_persona_community`, kein
        `make_ready`, kein neuer Marker/Leader -- nur der echte Client
        startet passiv.
      SETUP_HOLD -- Marker fehlt/unlesbar/falsches Schema/staler Leader BEI
        einem bereits begonnenen Bestand (R11/W38, R10P01: "begonnener
        Bestand" zaehlt jetzt JEDE Datei unter `--data-dir` ausserhalb des
        eigenen `logs/`-Ordners, inkl. `run/requests/<id>.json` -- s.
        `_root_has_started_product_bestand()`), ODER irgendeine KI-Persona
        "inconsistent" (R11/W38, R10P03: dazu zaehlt jetzt auch ein
        gezielt abgefangener Datei-/Parse-/Struktur-/Zuordnungsfehler
        eines der drei Leserwege, s. `_ai_persona_state()`), ODER (R10/W36)
        irgendeine KI-Persona noch NICHT "complete" (also "absent", einzeln
        oder fuer alle drei) BEI einem gueltigen Marker/Leader, ODER
        (R11/W38, R10P02) alle drei Personas "complete", aber die
        Community-Bootstrap-Transaktion selbst (noch) nicht
        `already_completed`, ODER (R10/W36) die Testfreigabe fuer einen
        sonst vollstaendigen Bestand ist geschlossen/fehlend/beschaedigt/
        gesperrt (`read_admission_block(run_dir)` meldet blockiert): klarer
        Abbruch VOR jedem weiteren Zugriff (der Aufrufer gibt `return 3`),
        KEINE neue Person, KEINE Ersatz-Marker-Reparatur, KEINE Teilwrites,
        KEINE automatische Neu-Autorisierung (kein stilles
        `provider_free=True`).

    "Marker fehlt" bedeutet nach dem R9-Fix NUR NOCH bei einem tatsaechlich
    leeren Bestand "frische Erstvorbereitung" -- nicht mehr pauschal "alle
    Personas absent". Alle drei Personas-Zustaende werden hier VOLLSTAENDIG
    berechnet, bevor der Aufrufer auch nur eine einzige davon beschreibt --
    kein Abbruch mitten in einer bereits teilweise ausgefuehrten Schleife.
    Die Testfreigabe-Pruefung (R10/W36) laeuft NUR noch, wenn bereits alle
    drei Personas als "complete" feststehen -- `read_admission_block` ist
    eine bestehende, unveraenderte, rein lesende Produktfunktion (liest
    `lab.stop`/`lab.status.json`, schreibt nichts) und liefert exakt dasselbe
    Blockiertbild, das der echte Client vor jedem Request sehen wuerde."""
    marker_status, marker_leader_id = _read_marker(marker_path)

    if marker_status == "absent":
        if _root_has_started_product_bestand(registry_dir, onboarding_dir, states_dir, catalog_dir, run_dir):
            return (
                "SETUP_HOLD", None,
                "Marker 'harness_participant.json' fehlt, aber dieses --data-dir hat bereits einen "
                "begonnenen Produktbestand (Registry/Onboarding/States/Current/Community/Profil) -- kein "
                "impliziter Erstvorbereitungs-Shortcut, kein automatisches 'alle Personas absent'.",
                {},
            )
        return "FRESH_EMPTY", None, None, {pk: "absent" for pk in ai_personas}

    if marker_status == "unreadable":
        return (
            "SETUP_HOLD", None,
            "Marker 'harness_participant.json' ist vorhanden, aber unlesbar oder hat ein falsches "
            "Schema -- kein automatischer Ersatzmarker, kein Rate-Leader.",
            {},
        )

    # marker_status == "valid"
    if not _leader_is_bound(sup, registry_dir, marker_leader_id):
        return (
            "SETUP_HOLD", None,
            f"Marker verweist auf leader_id {marker_leader_id!r}, aber diese Teilnehmeridentitaet "
            "ist in der Registry nicht (mehr) aufloesbar (staler Leader) -- kein automatisches "
            "Neuanlegen.",
            {},
        )

    persona_states = {
        pk: _ai_persona_state(sup, pk, onboarding_dir, states_dir, run_dir) for pk in ai_personas
    }
    inconsistent = sorted(pk for pk, st in persona_states.items() if st == "inconsistent")
    if inconsistent:
        return (
            "SETUP_HOLD", None,
            "KI-Bestand fuer " + ", ".join(repr(pk) for pk in inconsistent)
            + " ist unvollstaendig/widerspruechlich -- kein automatisches Neuanlegen/Auffuellen/"
            "Reparieren.",
            {},
        )

    # R10/W36 (R9-F01/R9P02): ein gueltiger Marker/Leader allein macht einen
    # Neustart noch nicht "EXISTING" -- bleibt IRGENDEINE KI-Persona "absent"
    # (noch nie beruehrt, einzeln ODER fuer alle drei), waere ein passiver
    # Neustart bisher stillschweigend ueber `make_ready()` nachgefuellt
    # worden (genau die zu schliessende Teststart-Luecke, belegt in
    # `evidence/probes/probe_absent_member`). Ein bereits begonnener Bestand
    # mit gueltigem Marker darf NICHT nachtraeglich aufgefuellt werden --
    # das ist jetzt ein klarer SETUP_HOLD, keine Teilwrites.
    not_complete = sorted(pk for pk, st in persona_states.items() if st != "complete")
    if not_complete:
        return (
            "SETUP_HOLD", None,
            "KI-Bestand fuer " + ", ".join(f"{pk}={persona_states[pk]}" for pk in not_complete)
            + " ist (noch) nicht vollstaendig tischbereit, obwohl bereits ein gueltiger "
            "Marker/Leader vorhanden ist -- ein passiver Neustart darf keine Persona "
            "nachtraeglich per make_ready/Bootstrap auffuellen, kein Teilwrite.",
            {},
        )

    # R11/W38 (R10-F01/R10P02, BRIEF-W38.md): ALLE DREI Personas "complete"
    # (jede einzeln: eigener Onboarding-Abschluss + eigener Persona-State +
    # eigener Current-Save, s. `_ai_persona_state()`) ist der Beweis einer
    # individuell tischbereiten Figur -- NICHT derselbe Beweis wie eine
    # tatsaechlich vollstaendig abgeschlossene Community-Bootstrap-
    # TRANSAKTION (`community_bootstrap.bootstrap_community()`s eigener
    # crash-sicherer Plan/Guard/Final-Marker, s. dortiger Modul-Docstring:
    # `bootstrap__plan.json` + `bootstrap__<pk>.guard.json` je Persona +
    # EIN `bootstrap__final.json` als EINZIGER vollstaendiger Abschluss-
    # nachweis). Wird nach einer echten FRESH-Vorbereitung NUR dieser
    # Abschlussmarker entfernt, lesen sich die drei Personas weiterhin als
    # "complete" (ihre eigenen States/Currents/Onboarding-Eintraege bleiben
    # unberuehrt) -- ohne diesen Check waere das bisher `EXISTING_
    # CONSISTENT` geworden und haette den echten Client gestartet, obwohl
    # die Bootstrap-Transaktion selbst laut ihrer eigenen, unveraenderten
    # `peek()`-Lesefunktion nicht abgeschlossen ist. `community_dir`/
    # `community_id` werden EXAKT so abgeleitet, wie `bootstrap_six_
    # persona_community()` (`_a24_local_support.py`) sie selbst baut
    # (`run_dir / "community"`, `f"community-{leader_id}"`) -- reiner
    # Lesezugriff auf dieselbe, unveraenderte Produktfunktion
    # (`community_bootstrap.peek`), kein Schema-/Reader-Write, kein
    # Auffuellen/Neubootstrap bei einem passiven Neustart.
    community_dir = run_dir / "community"
    community_id = f"community-{marker_leader_id}"
    bootstrap_state = community_bootstrap.peek(community_dir, community_id)
    if bootstrap_state is None or not bootstrap_state.already_completed:
        return (
            "SETUP_HOLD", None,
            f"Community-Bootstrap fuer {community_id!r} unter {community_dir} ist (noch) "
            "nicht vollstaendig abgeschlossen (bootstrap__final.json fehlt/unvollstaendig), "
            "obwohl alle drei KI-Personas bereits einzeln als 'complete' gelesen werden -- "
            "kein automatisches Auffuellen/Nachbootstrappen bei einem passiven Neustart.",
            {},
        )

    # R10/W36 (R9-F01/R9P01): ERST wenn alle drei Personas bereits "complete"
    # sind, lohnt die rein lesende Testfreigabe-Pruefung -- `read_admission_
    # block()` ist dieselbe, unveraenderte Produktfunktion, die der echte
    # Client vor jedem Request befragt (liest nur `lab.stop`/
    # `lab.status.json`, schreibt NICHTS). Eine bereits GESCHLOSSENE
    # (`provider_free=False` ohne Limitfelder), FEHLENDE, BESCHAEDIGTE oder
    # explizit GESPERRTE (`lab.stop`) Freigabe wird jetzt als SETUP_HOLD
    # behandelt statt -- wie bisher -- von `write_test_profile()` stumm
    # erneut auf `provider_free=True` gesetzt (belegt in
    # `evidence/probes/probe_profile_restart`: `provider_free_before=False`
    # -> `provider_free_after=True`).
    release_blocked, release_reason = read_admission_block(run_dir)
    if release_blocked:
        return (
            "SETUP_HOLD", None,
            f"Testfreigabe fuer diesen bereits begonnenen, vollstaendigen Bestand ist "
            f"geschlossen/fehlend/beschaedigt/gesperrt ({release_reason}) -- keine "
            "automatische Neu-Autorisierung (kein stilles provider_free=True) bei einem "
            "passiven Neustart.",
            {},
        )

    return "EXISTING_CONSISTENT", marker_leader_id, None, persona_states


def _next_exclusive_run_logs_dir(logs_dir: Path) -> Path:
    """R7/W32 (F02): liefert den ersten noch nicht existierenden
    `logs_dir/run-NNNN`-Pfad -- jeder Harness-Prozess bekommt dadurch eine
    eigene, exklusive Lauf-Unterablage; ein Folgeprozess (auch ein
    Null-Call-Neustart) oeffnet NIE den Ordner eines frueheren Laufs
    erneut, bisherige Callbelege bleiben bytegleich erhalten."""
    n = 1
    while True:
        candidate = logs_dir / f"run-{n:04d}"
        if not candidate.exists():
            return candidate
        n += 1


def main() -> int:
    parser = argparse.ArgumentParser(description="G06/F03: spielbarer Offlinezugang fuer T (Solo, echte Erschaffung).")
    parser.add_argument(
        "--data-dir", default=None,
        help="Datenverzeichnis (Default: frischer Temp-Ordner, fuer einen spaeteren Fortsetzen-Test wiederverwendbar).",
    )
    # R7/W27 (01_AUFTRAG.md §A "Operator darf VOR dem Blindlauf ein Szenario
    # der rein synthetischen Gegenstelle auswaehlen"): reine OPERATOR-Wahl,
    # kein an T verratenes Produkt-Tastenrezept -- 'pause' ist bewusst KEIN
    # drittes Szenario hier (die Produktgrammatik kennt an der
    # Entscheidungsgrenze nur `decision=accept|reject`, s. `adapters/
    # base.py:decision_contract_instruction`); T kann jederzeit selbst
    # '/pause' im Hauptmenue/laufenden Zug verwenden (bestehender, echter
    # Produktweg, keine Harness-Konfiguration noetig).
    parser.add_argument(
        "--scenario", choices=["normal", "reject"], default="normal",
        help=(
            "Operator-Szenario der SYNTHETISCHEN Gegenstelle (NICHT T "
            "gezeigt): 'normal' = jede eingeladene KI sagt echt per HTTP zu; "
            "'reject' = genau die mit --reject-persona-key benannte KI lehnt "
            "echt ab (alle anderen weiterhin accept). Ein '/pause' mitten in "
            "der Runde ist unabhaengig davon jederzeit T's eigene, echte "
            "Produktwahl."
        ),
    )
    parser.add_argument(
        "--reject-persona-key", default=None,
        help="Nur mit --scenario reject: persona_key der KI, die echt ablehnen soll.",
    )
    args = parser.parse_args()
    if args.scenario == "reject" and not args.reject_persona_key:
        parser.error("--scenario reject erfordert --reject-persona-key <persona_key>.")

    data_dir = Path(args.data_dir) if args.data_dir else Path(tempfile.mkdtemp(prefix="zeitriss-manual-offline-"))
    data_dir.mkdir(parents=True, exist_ok=True)
    run_dir = data_dir / "run"
    registry_dir = run_dir.parent / "registry"
    logs_dir = data_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    # R7/W32 (F02): exklusive Pro-Prozess-Logablage -- dieser Prozess
    # schreibt seine vier Callbelege NUR in diesen neuen, bisher nicht
    # existierenden Unterordner, nie in den Ordner eines frueheren Laufs.
    run_logs_dir = _next_exclusive_run_logs_dir(logs_dir)
    run_logs_dir.mkdir(parents=True)

    marker_path = data_dir / "harness_participant.json"
    AI_PERSONAS = ("sniper", "tech", "medic")
    onboarding_dir = data_dir / "onboarding"
    states_dir = data_dir / "states"
    catalog_dir = data_dir / "catalog"

    # R9/W34 (F03, BRIEF-W34.md): VOLLSTAENDIGE, rein lesende Bestands-
    # entscheidung fuer den GESAMTEN eigenen Root -- VOR jedem Write (vor
    # `write_test_profile`, `register_human`/Markerschreiben,
    # `bootstrap_six_persona_community`, `make_ready`). Ersetzt das alte
    # `is_fresh_setup = not marker_path.is_file()`, das einen fehlenden
    # Marker auf einem bereits begonnenen Produktbestand faelschlich als
    # "alle Personas absent" behandelte (s. Docstring oben, R8-F03).
    classification, leader_id, hold_reason, persona_states = _classify_harness_root(
        sup, marker_path, registry_dir, onboarding_dir, states_dir, catalog_dir, run_dir, AI_PERSONAS,
    )
    if classification == "SETUP_HOLD":
        print(f"SETUP-HOLD: {hold_reason} Testsetup wird ehrlich abgebrochen.", file=sys.stderr)
        return 3

    # R10/W36 (BRIEF-W36.md, R9-F01): `write_test_profile`/`register_human`+
    # Marker/`bootstrap_six_persona_community`/`make_ready` laufen jetzt
    # AUSSCHLIESSLICH im FRESH_EMPTY-Zweig -- ein passiver EXISTING_
    # CONSISTENT-Neustart (gueltiger Marker, alle drei Personas bereits
    # "complete", Testfreigabe bereits offen, s. `_classify_harness_root()`)
    # macht GAR KEINEN Write mehr und geht direkt zum echten Client-Start
    # weiter. Vorher reautorisierte `write_test_profile()` bei JEDEM Start
    # unbedingt die Testfreigabe (auch eine zuvor bewusst geschlossene,
    # belegt in `evidence/probes/probe_profile_restart`) -- genau die
    # passive Teststart-Luecke, die dieser Fix schliesst.
    if classification == "FRESH_EMPTY":
        # Dasselbe explizite, sichtbare providerfreie Testprofil wie JEDER
        # bestehende Offline-Test (03 §7) -- sonst blockiert das
        # Admission-Gate jede Entscheidung, auch die des menschlichen
        # Leaders. NUR hier, bei einer wirklich frischen Erstvorbereitung.
        write_test_profile(run_dir)

        # R7/W30 (BRIEF-W30.md Ziel 2): neutraler Testname statt der
        # vorherigen Rollenbezeichnung "Leader" -- 03_TESTDATEN_UND_
        # PRUEFUNG.md "Neue Spielerprofile 'Testspieler A', 'Testspieler B'".
        leader = sup.register_human(registry_dir, "Testspieler A")
        leader_id = leader.participant_id
        marker_path.write_text(json.dumps({"leader_id": leader_id}), encoding="utf-8")

        # R7/W30 (BRIEF-W30.md Ziel 1): bekannte, klar SIMULIERT markierte
        # KI-Spielgemeinschaft ueber denselben Produktweg wie die
        # bestehenden A24-Produkttests tischbereit machen -- `root=data_dir`
        # liefert exakt dieselben Pfade (`onboarding`/`states`/`run`/
        # `catalog` unter `data_dir`), die `scripts/mmo_sim.py` selbst aus
        # `--data-dir` ableitet, keine zweite Datenablage.
        ai_boot = sup.bootstrap_six_persona_community(
            data_dir, f"community-{leader_id}", persona_keys=AI_PERSONAS,
        )
        # `_classify_harness_root()` liefert fuer FRESH_EMPTY ausnahmslos
        # "absent" fuer alle drei Personas (s. dortiger Rueckgabewert) --
        # `make_ready` darf deshalb hier fuer jede der drei sicher einmalig
        # laufen, ohne erneute Bestandspruefung.
        for _pk in AI_PERSONAS:
            sup.make_ready(ai_boot["onboarding_dir"], ai_boot["states_dir"], ai_boot["run_dir"], _pk)

    persona_decisions = (
        {args.reject_persona_key: "reject"} if args.scenario == "reject" else {}
    )

    print("=" * 78)
    print("ZEITRISS -- Offline-Testzugang (isolierte deterministische Gegenstelle, kein Live-Call)")
    print("=" * 78)
    print(f"Datenverzeichnis : {data_dir}")
    print(f"Deine Teilnehmer-ID: {leader_id}  (du bist als dieser Teilnehmer eingeloggt)")
    print(f"Logordner dieses Laufs (eigene, exklusive Callbelege): {run_logs_dir}")
    print()
    print(
        "SIMULIERT: diese Umgebung verbindet statt eines echten Sprachmodells mit einer "
        "synthetischen, deterministischen Gegenstelle -- kein Netzwerk-/Livekontakt, keine echten Kosten. "
        "Die synthetische Gegenstelle ersetzt auch die Spielleitung an der Erschaffungsgrenze -- du hast "
        "noch keine eigene Figur, die Erschaffung ist ueber das Hauptmenue erreichbar."
    )
    print(
        "Bediene das Produkt wie gewohnt ueber sein eigenes Hauptmenue; Hilfe/Navigation/Abbruch sind "
        "innerhalb des Produkts selbst verfuegbar ('?', '/hilfe', '/zurueck', '/abbrechen')."
    )
    print("=" * 78)
    print()

    # R7/W27 (Generalbefund R6P01): KEIN fester table_id/section_id mehr --
    # der GM-Double leitet seinen tatsaechlichen eigenen Tisch bei jedem
    # Abschlussversuch frisch aus dem eigenen run_dir ab (dynamischer Modus,
    # `resolve_own_open_table_id`). Funktioniert dadurch automatisch fuer
    # Solo, eine beliebige spaetere 2+3-Einladung UND eine zweite Runde,
    # ohne dass dieser Harness irgendeine Gruppenformel selbst vorwegnehmen
    # muesste (die wuerde er gar nicht kennen -- T waehlt die Gaeste frei).
    #
    # R7/W30 (BRIEF-W30.md, R7P02): `complete_after` von 2 auf 8 angehoben
    # (derselbe Wert wie der bestehende, erfolgreiche A24-Fuenferrunden-Test
    # `test_a24_guided_setup_g_path_human_leader_with_handoff`). Grund:
    # jedes Mitglied (Mensch UND KI) sendet seinen Erstimport (Anker-Save)
    # als EIGENE Nachricht -- bei 2+3 (5 Mitglieder) braucht allein das
    # bereits 5 Nachrichten, BEVOR ueberhaupt ein regulaerer Beitrag NACH
    # Erstimport moeglich ist. Mit dem alten Wert 2 versuchte der GM-Double
    # den Abschluss bereits nach der zweiten Nachricht (meist Leader +
    # genau eine KI) -- die echte Vollstaendigkeitspruefung lehnte das dann
    # zu Recht ab ("fehlende Saves fuer [...]"), der Abschnitt wurde
    # unterbrochen, BEVOR die uebrigen Mitglieder ueberhaupt importieren
    # konnten. Fuer Solo (ein Mitglied) bleibt der Weg unveraendert
    # funktionsfaehig -- T braucht lediglich entsprechend mehr Spielzuege,
    # bevor der GM-Double den Abschluss anbietet (reine Testdoppel-Tuning,
    # keine Markergrammar-/Runtime-/Produktdefault-Aenderung).
    with CreationCapableSmartGmServer(
        leader_id=leader_id, run_dir=run_dir, complete_after=8,
    ) as srv, PersonaLoopbackServer(persona_decisions) as persona_srv:
        env = dict(os.environ)
        env["OPENWEBUI_URL"] = srv.base_url
        env["OPENWEBUI_API_KEY"] = "SYNTHETIC_MANUAL_OFFLINE_KEY"
        # W25 (BRIEF-W25.md): Persona-Grenze NEBEN der bestehenden GM-Grenze
        # verdrahtet (`mmo_sim/adapters/factories.py:default_persona_driver_
        # factory` liest diese drei Env-Variablen, sonst RuntimeError) --
        # rein test-/operator-seitige Env-Konfiguration, KEINE
        # Produktdefault-Aenderung.
        env["MMO_SIM_PERSONA_API_BASE_URL"] = persona_srv.base_url
        env["MMO_SIM_PERSONA_API_KEY"] = "SYNTHETIC_MANUAL_OFFLINE_KEY"
        env["MMO_SIM_PERSONA_API_MODEL"] = "synthetic-manual-offline"
        cmd = [
            sys.executable, str(_REPO_ROOT / "scripts" / "mmo_sim.py"),
            "--data-dir", str(data_dir), "--participant", leader_id,
        ]
        print(f"Starte echten Prozess: {' '.join(cmd)}\n")
        rc = subprocess.run(cmd, env=env, cwd=str(_REPO_ROOT)).returncode

        # R7/W27 (Brief-Pflicht "getrennte Logs GM/Persona/Reflexion"):
        # echte Payload-/Call-Belege, getrennt nach Grenze/Zweck, als
        # Rohdateien fuer die spaetere Main-Nachpruefung -- NICHT nur
        # In-Prozess-Listen, die mit dem Harness-Prozess verloren gehen.
        #
        # R7/W32 (F02): Ziel ist jetzt IMMER `run_logs_dir` (eigener,
        # exklusiver Ordner dieses Prozesses, s. oben) statt des
        # gemeinsamen `logs_dir` -- ein Folgeprozess (auch ein
        # Null-Call-Neustart) schreibt dadurch NIE in die Dateien eines
        # frueheren Laufs; auch ein Lauf ohne jeden Call bekommt eigene
        # (leere) Dateien und ist damit explizit belegt.
        (run_logs_dir / "gm_gameplay_calls.jsonl").write_text(
            "\n".join(json.dumps(c, ensure_ascii=False) for c in srv.calls) + ("\n" if srv.calls else ""),
            encoding="utf-8",
        )
        (run_logs_dir / "gm_creation_calls.jsonl").write_text(
            "\n".join(json.dumps(c, ensure_ascii=False) for c in srv.creation_calls) + ("\n" if srv.creation_calls else ""),
            encoding="utf-8",
        )
        (run_logs_dir / "persona_decision_calls.jsonl").write_text(
            "\n".join(json.dumps(c, ensure_ascii=False) for c in persona_srv.decision_calls)
            + ("\n" if persona_srv.decision_calls else ""),
            encoding="utf-8",
        )
        (run_logs_dir / "persona_reflection_calls.jsonl").write_text(
            "\n".join(json.dumps({"text": t}, ensure_ascii=False) for t in persona_srv.reflection_calls)
            + ("\n" if persona_srv.reflection_calls else ""),
            encoding="utf-8",
        )

    print()
    print(f"Prozess beendet (rc={rc}). Datenverzeichnis bleibt erhalten: {data_dir}")
    print(f"Getrennte GM-/Persona-/Reflexionslogs dieses Laufs (frueher Laeufe bleiben unangetastet): {run_logs_dir}")
    print(
        f"Fuer einen 'Fortsetzen'-Testlauf (ECHTER, SEPARATER Prozess): python3 "
        f"{Path(__file__).relative_to(_REPO_ROOT)} --data-dir {data_dir}"
    )
    return rc


if __name__ == "__main__":
    sys.exit(main())
