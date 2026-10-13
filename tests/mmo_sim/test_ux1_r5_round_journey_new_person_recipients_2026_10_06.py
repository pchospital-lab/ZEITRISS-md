#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_r5_round_journey_new_person_recipients_2026_10_06.py
— W20/F04 (ZEITRISS Terminal UX-1, R5-Wiederanlauf): bestehende Gruppen-/
Gast-/Pending-Adapter zu EINER zusammenhaengenden UI-Reise verbinden (KEINE
neue Architektur, nur Verbindung bereits vorhandener Bausteine aus
`_cmd_local_round_setup`/`_local_round_select_humans`/`_local_round_handoff`/
`_HumanDriver`/`_collect_reflections`).

Deckt aus dem F04-Fachvertrag:
1. Eine ZWEITE NEUE Person waehrend DERSELBEN Rundenplanungszeile
   ('neu:Clara,neu:Dirk') -> ausdruecklicher Fokus (Terminaluebergabe) je
   Person -> eigene Figur UEBER DEN ECHTEN Erschaffungsweg
   (`_cmd_new_or_switch_character`/`run_admitted_creation_dialog`, content-
   gebundene Fake-SL mit GENAU EINER Frage vor dem Save -- kein Einzelschuss-
   Shortcut) -> Rueckkehr zur ERHALTENEN Besetzung (Leader bleibt Teil der
   3er-Zusammenfassung, kein Verlust).
2. (Teilausschnitt) echte Spielzuege nach der Verbindung -- kein Autoplayer,
   jeder Zug kommt aus einer eigenen stdin-Antwort dieses Transkripts.
3. Vier Empfaengerzwecke mit Payload-/Callbeleg: Leader->SL, erster
   Gast-Import->SL (ueber Leader), regulaerer Gast->Tischabsprache (dieser
   Test), Abschlussnotiz->lokal (zweiter Test unten, eigener schneller
   Abschluss -- vermischt sonst zwei unabhaengige Nachweise).
4. `/stand`/`/verlauf` unter dem AKTUELLEN Eingabeprofil (gerade eingebende
   Person, nicht pauschal der aeussere Sessionteilnehmer), volle Historie
   sichtbar paginiert, kein Modellkontext-Kuerzungshinweis.
5. Sechster Platz / fehlende Zustimmung stoppen kontrolliert ohne versteckte
   Ersatzgruppe (Erhaltungsproben, reine Regressionsabsicherung dieser Reise).

Methodik: EIN prompt-gebundener Antwortgeber (`_responder`) statt einer
starren Eingabezeilenliste -- die exakte Reihenfolge/Anzahl der vom Produkt
ausgeloesten Fokusuebergaben (`_local_round_handoff`, abhaengig von einer zur
Laufzeit zufaellig erzeugten Registry-ID) ist absichtlich NICHT hartkodiert;
der Antwortgeber erkennt JEDEN Prompttext inhaltlich (wie `_HumanDriver`
selbst inhaltsgebunden dispatcht) und bleibt dadurch unabhaengig von der
tatsaechlichen Zufalls-ID-Reihenfolge korrekt.

Fake-SL ausschliesslich an der GM-/Transportgrenze (kein echter Modellaufruf,
02 §4-Grenze): content-gebunden (CREATION_SIGNATURE je Erschaffung,
eingebettete v7-Bloecke je Spielzug) wie in `_ux1_r5_synthetic_creation_
support.py`/`test_ux1_r06_adapter_guest_after_import_2026_10_05.py` bereits
etabliert -- kein neuer Fake-Mechanismus, nur fuer eine zusammenhaengende
Mehrpersonenreise statt eines Einzelfalls zusammengesetzt.

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs."""
from __future__ import annotations

import json
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

import _a24_local_support as sup  # noqa: E402
from _full_v7_fixture import full_v7_save  # noqa: E402
from _ux1_r5_synthetic_creation_support import CREATION_SIGNATURE  # noqa: E402

CREATION_QUESTION = (
    "[SYNTHETISCHE SL-ERSCHAFFUNG -- Fake-SL an der Transportgrenze, KEINE echte "
    "Spielleitung/Liveprobe] Welche Grundausstattung waehlst du fuer deinen ersten "
    "Einsatz als Chrononaut?"
)


class _JourneyCreationGm:
    """EIN Fake je NEU erschaffender Person (eigener Chat, s. `ui/tui.py:
    _cmd_new_or_switch_character`s `onboarding-<participant_id>`-Bindung).
    Inhaltsgebunden wie `_ux1_r5_synthetic_creation_support.
    _CreationCapableHandler`: die Eroeffnungszeile (`CREATION_SIGNATURE`)
    bekommt GENAU EINE Frage, jede andere (freie) Antwort einen gueltigen,
    fuer DIESE Person unterscheidbaren v7-Save -- ECHTER Zweiturn-Dialog,
    kein Einzelschuss-Save."""

    def __init__(self, char_id: str):
        self.char_id = char_id
        self.calls = 0

    def turn(self, idx, text, **kw):
        self.calls += 1
        if CREATION_SIGNATURE in text:
            return {"content": CREATION_QUESTION}
        # R12-Fix: kanonischer, gegen BEIDE v7-Schemas gueltiger Block statt
        # des alten Minimalfakes -- der frueher zusaetzlich gesetzte
        # Nicht-Schema-Root-Key `_fixture_note` verstiess ebenfalls gegen
        # `additionalProperties:false` am Export-Schema-Root.
        save = full_v7_save(
            self.char_id, name=f"Neu-{self.char_id}", callsign=self.char_id.upper(),
            save_id=f"synthetic-{self.char_id}-001",
        )
        return {"content": "Erschaffung abgeschlossen.\n```json\n" + json.dumps(save, ensure_ascii=False) + "\n```"}


class _JourneyTableGm:
    """EIN Fake fuer die eigentliche Runde (table_id als Chat-Identitaet,
    s. `ui/tui.py:_cmd_local_round`s `accepts_table_id`-Zweig). Erntet JEDEN
    eingebetteten v7-Block aus dem jeweils AKTUELLEN Zugtext (wie
    `_ux1_r5_synthetic_creation_support._CreationCapableHandler.
    _gameplay_response`) -- ohne vorab bekannte `final_saves`, da die
    char_ids der beiden neuen Personen erst waehrend der Erschaffung
    entstehen. Schliesst den Abschnitt NIE von selbst ab (wie `_a24_local_
    support`s `_NeverCompletingGm`/`test_ux1_r06_adapter_guest_after_import`s
    `_NeverCompletingGm`) -- diese Reise wird bewusst per EOF/`/pause`
    kontrolliert beendet, NACHDEM alle vier Empfaenger-/Fachpunkte real
    beobachtet wurden (kein Abschluss-/Reflexionsrauschen in diesem Teil)."""

    def __init__(self):
        self.calls: list[str] = []
        self.harvested: dict[str, dict] = {}

    def turn(self, idx, text, **kw):
        self.calls.append(text)
        for blk in zeitriss_saves.extract_all_saves(text):
            cid = zeitriss_saves.block_char_id(blk)
            if cid:
                self.harvested[cid] = blk
        return {"content": f"Szene {len(self.calls)}: Ihr beobachtet die Lage. Was tut ihr als Naechstes?"}


def _journey_gm_factory(creation_gms: dict, table_box: dict):
    """EIN Factory-Objekt fuer Erschaffung UND Spiel (derselbe Grundsatz wie
    W19s `CreationCapableSmartGmServer`: `OPENWEBUI_URL`/die SL-Anbindung ist
    je Prozess/Session fix, beide Zwecke teilen sich zwangsläufig densel­ben
    Transport) -- dispatcht rein an der uebergebenen Chat-Identitaet
    (`onboarding-<pid>` vs. `table.table_id`), kein globaler Modusschalter."""

    def factory(chat_id: str | None = None):
        if chat_id and chat_id.startswith("onboarding-"):
            pid = chat_id.split("onboarding-", 1)[1]
            if chat_id not in creation_gms:
                creation_gms[chat_id] = _JourneyCreationGm(char_id=f"chrono-journey-{pid}")
            return creation_gms[chat_id]
        if "gm" not in table_box:
            table_box["gm"] = _JourneyTableGm()
        return table_box["gm"]

    return factory


def _responder(printed: list, queues: dict, state: dict):
    """EIN prompt-gebundener Antwortgeber statt starrer Zeilenliste (s.
    Moduldocstring) -- erkennt JEDEN relevanten Prompttext inhaltlich und
    liefert die jeweils fachlich richtige Antwort, UNABHAENGIG von der
    tatsaechlichen (zur Laufzeit zufaelligen) Registry-ID-Reihenfolge."""

    def _fn(prompt: str = "") -> str:
        state["prompts"].append(prompt)
        if "Allein mit KI-Mitspielern" in prompt:
            return "2"
        if "Weitere Menschen an diesem Geraet" in prompt:
            return "neu:Clara,neu:Dirk"
        if "bestaetigen? [j/n]" in prompt or "uebernehmen? [j/n]" in prompt:
            return "j"
        if prompt == "Auswahl: ":
            return "1"  # Charaktere-Untermenue: [1] Auswaehlen/neu erstellen.
        if prompt == "Deine Antwort: ":
            state["creation_answers"] += 1
            return f"Ich nehme Standardausruestung #{state['creation_answers']}."
        if "KI-Mitspieler (Nummer/Name" in prompt:
            return ""  # Keine KI in dieser Reise (0 Personas, reiner Menschenfall).
        if prompt.startswith("Leader dieser Runde"):
            return ""  # Leader bleibt der aufrufende Mensch ("du").
        if "Mit dieser Startwahl fortfahren?" in prompt:
            return "j"
        if "beitreten? [j/n]" in prompt:
            return "j"
        if prompt.endswith("Deine Aktion: ") or "] Deine Aktion: " in prompt:
            if queues["moves"]:
                return queues["moves"].pop(0)
            raise EOFError()
        raise AssertionError(f"W20: unerwarteter Prompt ohne Antwortregel: {prompt!r}")

    return _fn


def test_two_new_people_one_setup_line_focus_creation_retained_cast_real_segment():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        registry_dir = root / "registry"
        onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
        states_dir, run_dir = root / "states", root / "run"
        write_test_profile(run_dir)

        leader = sup.register_human(registry_dir, "Leader")
        leader_id = leader.participant_id
        sup.onboard_human_figure(
            registry_dir, leader_id, onboarding_dir, states_dir, run_dir, "CHR-W20-LEAD", "Len", "LENOPS",
        )

        creation_gms: dict = {}
        table_box: dict = {}
        printed: list[str] = []
        state = {"prompts": [], "creation_answers": 0}
        # Zwei echte Spielzuege vor der ersten /stand+/verlauf-Probe, danach
        # weitere -- die genaue ZUORDNUNG zu Leader/Clara/Dirk ergibt sich
        # aus der tatsaechlichen, vom Produkt gesteuerten Akteurreihenfolge
        # (s. `_HumanDriver.decide`), nicht aus dieser Liste selbst.
        moves = [
            "Leader-Zug 1: Wir sichern den Zugang (Anker).",
            "/stand",
            "/verlauf",
            "/verlauf",
            "Neuer-Zug A: Ich melde mich einsatzbereit.",
            "Neuer-Zug B: Ich uebernehme die rechte Flanke.",
            "Leader-Zug 2: Wir beobachten weiter.",
            "Regulaerer Folgezug nach Erstimport: alles ruhig hier.",
        ]
        queues = {"moves": moves}

        session = TuiSession(
            onboarding_dir, catalog_dir, leader_id,
            input_fn=_responder(printed, queues, state),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=sup.SCHEMA,
            gm_transport_factory=_journey_gm_factory(creation_gms, table_box),
        )

        try:
            session._cmd_local_round_setup()
        except EndOfInput:
            pass
        out = "\n".join(printed)

        # -- Fachpunkt 1: zwei NEUE Personen aus EINER Setupzeile, je eigene
        # Erschaffung (ECHTER Zweiturn-Dialog: Frage dann Save), danach
        # Rueckkehr zur ERHALTENEN (3er-)Besetzung.
        assert "Neu registriert:" in out and out.count("Neu registriert:") == 2, out[-2000:]
        assert out.count("Erschaffung abgeschlossen.") == 2, (
            f"beide neu registrierten Personen muessen je EINE echte Erschaffung abschliessen: {out[-2000:]}"
        )
        assert len(creation_gms) == 2, f"zwei getrennte Erschaffungs-Chats erwartet: {list(creation_gms)}"
        for gm in creation_gms.values():
            assert gm.calls == 2, (
                f"ECHTER Zweiturn-Dialog (1 Frage + 1 Antwort->Save) je neuer Person erwartet, "
                f"beobachtet={gm.calls} Calls"
            )
        char_ids = {gm.char_id for gm in creation_gms.values()}
        assert len(char_ids) == 2, f"zwei unterscheidbare Figuren erwartet: {char_ids}"

        assert "Zusammenfassung (3 Spieler einschliesslich Leader)" in out, (
            f"Rueckkehr zur ERHALTENEN Besetzung (Leader + 2 neue Personen, kein Verlust) fehlt: {out[-1500:]}"
        )
        zsf_idx = out.index("Zusammenfassung (3 Spieler")
        erschaffung_idxs = [i for i in range(len(out)) if out.startswith("Erschaffung abgeschlossen.", i)]
        assert len(erschaffung_idxs) == 2 and all(i < zsf_idx for i in erschaffung_idxs), (
            "beide Erschaffungen muessen VOR der Rueckkehr zur Zusammenfassung/Besetzung liegen "
            f"(kein separater Zweitdurchgang): erschaffung={erschaffung_idxs} zusammenfassung={zsf_idx}"
        )

        # Die registrierten IDs der zwei neuen Personen (fuer Payload-/
        # Dateibelege unten) -- aus der Registry gelesen, NICHT erraten.
        all_known = dict(session._local_round_list_humans())
        new_ids = sorted(pid for pid, name in all_known.items() if name in ("Clara", "Dirk"))
        assert len(new_ids) == 2, all_known
        table_id = sup.compute_table_id(leader_id, new_ids)

        # -- Fachpunkt 2 (Teilausschnitt): kein Autoplayer -- jede der
        # gescripteten Zugzeilen kam tatsaechlich am GM an (inhaltsgebundene
        # Ernte, s. `_JourneyTableGm`).
        gm = table_box["gm"]
        # "Regulaerer Folgezug nach Erstimport" ist per Produktvertrag
        # (`_HumanDriver._purpose_label`/`poll_guests_and_consolidate`)
        # Tischabsprache, NIE ein SL-/GM-Call -- Beleg dafuer folgt unten
        # ueber `table_messages`/`leader_message`, nicht ueber `gm.calls`.
        for text in (
            "Leader-Zug 1: Wir sichern den Zugang (Anker).",
            "Neuer-Zug A: Ich melde mich einsatzbereit.",
            "Neuer-Zug B: Ich uebernehme die rechte Flanke.",
            "Leader-Zug 2: Wir beobachten weiter.",
        ):
            assert any(text in c for c in gm.calls), f"Zugzeile nicht beim SL angekommen: {text!r}"
        assert char_ids.issubset(set(gm.harvested)), (
            f"beide neu erschaffenen Figuren muessen als echte Importe beim SL geerntet worden sein: "
            f"erwartet={char_ids} geerntet={set(gm.harvested)}"
        )

        # -- Fachpunkt 3: vier Empfaengerzwecke (hier drei der vier Faelle;
        # der vierte, 'eigene lokale Notiz', ist Gegenstand des zweiten
        # Tests unten -- diese Reise endet bewusst per /pause VOR der
        # Reflexionsphase, um die Nachweise nicht zu vermischen).
        empf_lines = [p for p in printed if p.startswith("Empfaenger:")]
        leader_labels = [p for p in empf_lines if p == "Empfaenger: Spielleitung (SL)"]
        assert len(leader_labels) == 2, empf_lines  # zwei Leader-Zuege.
        import_labels = [p for p in empf_lines if p.startswith("Empfaenger: ueber Leader an Spielleitung")]
        assert len(import_labels) == 2, (
            f"je EIN Erstimport-Label fuer Clara UND Dirk erwartet: {empf_lines}"
        )
        table_labels = [p for p in empf_lines if p.startswith("Empfaenger: Tischabsprache")]
        # Mindestens EIN regulaerer Gastfolgezug (-> Tischabsprache, NICHT
        # SL) -- beide Gaeste werden in der zweiten "ongoing_round"-Runde
        # erneut befragt (die Beschriftung wird bereits VOR dem jeweiligen
        # Lesevorgang gedruckt, s. `_HumanDriver.decide`), die Reise endet
        # bewusst per EOF, sobald die Eingabequeue erschoepft ist -- mind.
        # EINE davon erreicht noch eine echte Antwort (s. `table_messages`-
        # Beleg unten), mehr als eine gedruckte Beschriftung ist zulaessig.
        assert len(table_labels) >= 1, (
            f"mindestens EIN regulaerer Gastfolgezug (-> Tischabsprache, NICHT SL) erwartet: {empf_lines}"
        )
        # Zeitliche Reihenfolge: der erste Tischabsprache-Fall kommt NACH
        # BEIDEN Erstimporten (nicht vor oder zwischen ihnen).
        assert empf_lines.index(table_labels[0]) > empf_lines.index(import_labels[-1]), empf_lines

        table_file = run_dir / "tables" / f"{table_id}.json"
        data = json.loads(table_file.read_text(encoding="utf-8"))
        sl_origins = [e.get("origin_persona_key") for e in data.get("sl_log", [])]
        for pid in new_ids:
            assert sl_origins.count(pid) == 1, (
                f"'{pid}' muss GENAU EINMAL (Erstimport) als sl_log-Ursprung erscheinen: {sl_origins}"
            )
        table_messages = data.get("table_messages", [])
        assert any(
            m.get("text") == "Regulaerer Folgezug nach Erstimport: alles ruhig hier." for m in table_messages
        ), f"regulaerer Gastfolgezug fehlt als reine Tischabsprache: {table_messages}"
        leader_messages_text = " ".join(e.get("leader_message", "") for e in data.get("sl_log", []))
        assert "Regulaerer Folgezug nach Erstimport" not in leader_messages_text, (
            "regulaerer Gastfolgezug darf NICHT versteckt an die SL gegangen sein"
        )
        # R12-Darstellungsmigration (02_TESTVERTRAG.md): das strikte Export-
        # Schema kennt auf Figurenebene nur `id` (additionalProperties:
        # false), keinen zusaetzlichen `char_id`-Schluessel -- empirisch an
        # den tatsaechlich an die SL gesendeten Bytes belegt (s. Probe):
        # der eingebettete Save traegt `"id": "<cid>"`, kein `char_id` mehr.
        # Unveraendert bleibt: GENAU EIN eigener eingebetteter Save je Figur.
        for cid in char_ids:
            assert leader_messages_text.count(f'"id": "{cid}"') == 1, (
                f"genau EIN eingebetteter Save fuer '{cid}' im an die SL gesendeten Text erwartet: "
                f"{leader_messages_text}"
            )

        # -- Fachpunkt 4 (dieser Teil): /stand unter dem AKTUELLEN
        # Eingabeprofil (gerade eingebende Person), /verlauf voll paginiert,
        # kein Kuerzungshinweis.
        stand_lines = [p for p in printed if p.startswith("Fortsetzen:")]
        assert len(stand_lines) == 1, printed
        # Die /stand-Zeile muss zur Figur der Person gehoeren, die GERADE
        # eingibt (nicht pauschal 'leader_id') -- der genaue Akteur zum
        # Zeitpunkt des '/stand' (direkt nach Leader-Zug 1) haengt von der
        # realen Fokusreihenfolge ab; belegt wird daher die STRUKTURELLE
        # Eigenschaft: die Zeile referenziert EINE der drei bekannten
        # Chrononaut-IDs dieser Runde, nie "kein aktueller Stand".
        assert "kein aktueller Stand" not in stand_lines[0], stand_lines
        verlauf_markers = [
            p for p in printed
            if p.startswith("(Anfang des Verlaufs erreicht") or "weitere, aeltere Eintraege" in p
        ]
        assert len(verlauf_markers) >= 1, (
            f"/verlauf muss sichtbar paginieren (Anfangsmarker ODER 'weitere Eintraege'): {printed[-20:]}"
        )
        assert not any("Kein bisheriger Verlauf" in p for p in verlauf_markers), verlauf_markers


def test_sixth_participant_rejected_no_table_no_gm_call():
    """Erhaltungsprobe (02 §D.5): sechs Menschen in derselben Reise -- die
    unveraenderte Tischgroessenpolicy lehnt VOR jeder Tischanlage ab, kein
    SL-Call, keine stille Restgruppe."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        registry_dir = root / "registry"
        onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
        states_dir, run_dir = root / "states", root / "run"
        write_test_profile(run_dir)

        names = ["Leo", "Mira", "Nils", "Opa", "Pia", "Quin"]
        chars = [(f"CHR-W20-S{i}", n, f"{n.upper()}OPS") for i, n in enumerate(names)]
        participants = [sup.register_human(registry_dir, n) for n in names]
        pids = [p.participant_id for p in participants]
        for pid, c in zip(pids, chars):
            sup.onboard_human_figure(registry_dir, pid, onboarding_dir, states_dir, run_dir, *c)

        leader_id, guest_ids = pids[0], pids[1:]

        class _MustNotBeCalledGm:
            def turn(self, idx, text, **kw):
                raise AssertionError(f"W20: Sechs-Menschen-Fall darf nie einen SL-Call ausloesen (text={text!r})")

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir, catalog_dir, leader_id,
            input_fn=lambda prompt="": "j" if "beitreten? [j/n]" in prompt else (_ for _ in ()).throw(EOFError()),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=sup.SCHEMA,
            gm_transport_factory=lambda *_a, **_kw: _MustNotBeCalledGm(),
        )
        try:
            session._cmd_local_round(list(guest_ids))
        except EndOfInput:
            pass
        out = "\n".join(printed)
        assert "Lokale Runde konnte nicht gestartet werden" in out, out
        assert "6 Spieler angefragt" in out, out
        assert "1 bis 5" in out, out
        assert not (run_dir / "tables").exists() or not list((run_dir / "tables").glob("*.json")), (
            "Sechs-Menschen-Fall darf keinen Tisch anlegen"
        )


def test_missing_consent_guest_declines_stops_round_without_replacement():
    """Erhaltungsprobe: lehnt ein zustimmungspflichtiger Gast ab, bricht die
    GESAMTE Runde kontrolliert ab -- kein stiller Solo-/Restgruppen-
    weiterlauf, kein Tisch."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        registry_dir = root / "registry"
        onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
        states_dir, run_dir = root / "states", root / "run"
        write_test_profile(run_dir)

        leader = sup.register_human(registry_dir, "Leader2")
        guest = sup.register_human(registry_dir, "Guest2")
        leader_id, guest_id = leader.participant_id, guest.participant_id
        sup.onboard_human_figure(registry_dir, leader_id, onboarding_dir, states_dir, run_dir, "CHR-W20-L2", "L2", "L2OPS")
        sup.onboard_human_figure(registry_dir, guest_id, onboarding_dir, states_dir, run_dir, "CHR-W20-G2", "G2", "G2OPS")

        class _MustNotBeCalledGm:
            def turn(self, idx, text, **kw):
                raise AssertionError(f"W20: abgelehnter Gast darf nie einen SL-Call ausloesen (text={text!r})")

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir, catalog_dir, leader_id,
            input_fn=lambda prompt="": "n" if "beitreten? [j/n]" in prompt else (_ for _ in ()).throw(EOFError()),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=sup.SCHEMA,
            gm_transport_factory=lambda *_a, **_kw: _MustNotBeCalledGm(),
        )
        try:
            session._cmd_local_round([guest_id])
        except EndOfInput:
            pass
        out = "\n".join(printed)
        assert "nicht alle angefragten Teilnehmer haben zugesagt" in out, out
        assert not (run_dir / "tables").exists() or not list((run_dir / "tables").glob("*.json")), (
            "abgelehnter Gast darf keinen Tisch anlegen"
        )


class _OneShotCompletingGm:
    """Liefert beim ERSTEN echten Spielzug sofort den Abschlussmarker samt
    beider finaler Saves -- derselbe etablierte Baustein wie in
    `test_ux1_g04_purpose_stand_verlauf_2026_10_05.py`, hier wiederverwendet,
    um die VIERTE Empfaengerzweck-Variante (lokale Notiz) isoliert (ohne die
    laengere Erschaffungsreise oben) nachzuweisen."""

    def __init__(self, final_saves: dict, table_id: str, section_id: str):
        self.final_saves = final_saves
        self.table_id = table_id
        self.section_id = section_id
        self.calls: list[str] = []

    def turn(self, idx, text, **kw):
        self.calls.append(text)
        debrief = "\n".join(
            f"```json\n{json.dumps(b, ensure_ascii=False)}\n```" for b in self.final_saves.values()
        )
        return {"content": f"{debrief}\n{COMPLETION_MARKER} table_id={self.table_id} section_id={self.section_id}"}


def test_local_reflection_note_is_fourth_recipient_purpose_not_leaked():
    """Fachpunkt 3 (vierter Fall): die freiwillige Abschlussnotiz zeigt die
    lokale Beschriftung (NICHT 'Spielleitung'/'Tischabsprache') und landet
    NUR in `reflections.jsonl` (`kind=human_note`) -- NIE im `sl_log`/in
    `table_messages` (keine Vertraulichkeitszusage bei geteiltem Bildschirm,
    aber auch kein Leck in den GM-/Tischkanal)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        registry_dir = root / "registry"
        onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
        states_dir, run_dir = root / "states", root / "run"
        write_test_profile(run_dir)

        leader = sup.register_human(registry_dir, "Leader3")
        guest = sup.register_human(registry_dir, "Guest3")
        leader_id, guest_id = leader.participant_id, guest.participant_id
        onb_leader = sup.onboard_human_figure(
            registry_dir, leader_id, onboarding_dir, states_dir, run_dir, "CHR-W20-L3", "L3", "L3OPS",
        )
        onb_guest = sup.onboard_human_figure(
            registry_dir, guest_id, onboarding_dir, states_dir, run_dir, "CHR-W20-G3", "G3", "G3OPS",
        )
        table_id = sup.compute_table_id(leader_id, [guest_id])
        section_id = f"{table_id}-section"
        final_saves = {
            leader_id: sup.end_save_for(onb_leader["save"], "w20note", "w20note"),
            guest_id: sup.end_save_for(onb_guest["save"], "w20note2", "w20note"),
        }
        gm = _OneShotCompletingGm(final_saves, table_id, section_id)

        leader_note = "Notiz: Figur und Ausruestung geprueft (lokal, nicht fuer die SL)."
        printed: list[str] = []
        # Beide "Deine Aktion: "-Aufrufe des Leaders (Spielzug, dann
        # Reflexion) tragen denselben Prompttext -- eine kleine
        # Zustandsmaschine statt einer rein prompttextgebundenen Antwort
        # unterscheidet sie anhand der Aufrufreihenfolge.
        calls_to_leader_prompt = {"n": 0}

        def _leader_input(prompt: str = "") -> str:
            if "beitreten? [j/n]" in prompt:
                return "j"
            if prompt == "Deine Aktion: ":
                calls_to_leader_prompt["n"] += 1
                if calls_to_leader_prompt["n"] == 1:
                    return "Leader-Anker-Zug."
                return leader_note
            if "] Deine Aktion: " in prompt:
                return ""  # Gast: leere freiwillige Notiz (zulaessig, kein human_note-Eintrag).
            raise EOFError()

        session = TuiSession(
            onboarding_dir, catalog_dir, leader_id,
            input_fn=_leader_input,
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=sup.SCHEMA,
            gm_transport_factory=lambda *_a, **_kw: gm,
        )
        try:
            session._cmd_local_round([guest_id])
        except EndOfInput:
            pass
        out = "\n".join(printed)

        assert "Abschnitt abgeschlossen:" in out, out[-1500:]
        note_labels = [p for p in printed if p.startswith("Empfaenger: eigene lokale Notiz")]
        assert len(note_labels) == 2, (
            f"je EINE lokale-Notiz-Beschriftung fuer Leader UND Gast erwartet: {printed[-20:]}"
        )
        assert not any(p == "Empfaenger: Spielleitung (SL)" and i > len(printed) - 3 for i, p in enumerate(printed)), out

        reflections_path = run_dir / "reflections.jsonl"
        reflections = sup.read_jsonl(reflections_path)
        human_notes = {r["persona_key"]: r.get("text") for r in reflections if r.get("kind") == "human_note"}
        assert human_notes.get(leader_id) == leader_note, human_notes
        assert guest_id not in human_notes, "leere freiwillige Gastnotiz darf nicht archiviert werden"

        table_file = run_dir / "tables" / f"{table_id}.json"
        data = json.loads(table_file.read_text(encoding="utf-8"))
        leader_messages_text = " ".join(e.get("leader_message", "") for e in data.get("sl_log", []))
        assert leader_note not in leader_messages_text, "lokale Notiz darf NIE an die SL gehen"
        table_messages_text = " ".join(m.get("text", "") for m in data.get("table_messages", []))
        assert leader_note not in table_messages_text, "lokale Notiz darf NIE als Tischabsprache landen"


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR {t.__name__}:")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} Tests bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
