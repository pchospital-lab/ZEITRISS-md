#!/usr/bin/env python3
"""
tests/mmo_sim/test_h02_vollreise_profiles_2026_09_28.py — H02-Vollreise
(Auftragspaket `zeitriss-p2-headless-h02-vollreise-auftrag-2026-09-28-r1`):
zwei vollstaendige kontrollierte Reisen (API mit echter getrenntprozessiger
Start-/Resumephase; Hybrid mit echter `PersonaClaudeCodeDriver`-Klasse +
selbst erzeugter ausfuehrbarer Fake-CLI) ueber echte Factories/CLI/Runtime/GM:
sechs bestaetigte KI-Personas (sniper/tech/cqb/face/medic/pyro) + eine reale
menschliche Teilnehmeridentitaet, nur sniper/tech ueber `--personas`
freigegeben, sniper nominiert (aus eigener Initiative) TECH statt sich selbst
als Leader, echter Consent, G0 Leaderimport, G1 Gastimport, dann drei echte
SL-Spielantworten G2-G4 ueber die echte HTTP-GM-Grenze, G4 mit gueltigem
individuellem v7-Endsave fuer beide Mitglieder, normale Freigabe, danach ein
neues freiwilliges Fenster mit neuen eigenen pause-Antworten (kein zweiter
Tisch aus altem Consent).

Plus Pflicht-Negativkontrollen (02_ABNAHME_UND_AUFRUFE.md §A, 04_HYBRID_API_SL.md
§6): Y-N1 (Hybrid-CLI-Fehler ohne API-Fallback), Y-N2 (API-Fehler 401 ohne
Providerwechsel), Y-N3 (fehlender GM-Outputbound blockiert unter hartem
Dollarbudget), Y-N4 (providerfreies Testprofil autorisiert keine externe
Route), N-HUMAN (echte menschliche waiting/hold-Probe an einem vorab ueber
bestehende Produktdienste gebundenen Tisch) und N-STOP (separater `lab
stop`-Prozess an einer kontrolliert in-flight befindlichen Personaantwort,
plus passives `status`/`attach` aus getrennten Prozessen).

Neuer permanenter Test (kein vorhandener Dateiname im Ausgangsbaum), von
`run_all.py` automatisch entdeckt. Helper/Fixtures in
`_h02_vollreise_support.py`. `H02_EVIDENCE_DIR` ist eine neue dokumentierte
Testausgabevariable (s. dortiger Docstring), kein Produktflag.

Nur `scripts/mmo_sim.py lab start/resume/status/stop/attach` als echte,
neue Python-Subprozesse mit `stdin=DEVNULL`; keine Tastenpumpe, keine zweite
Orchestrierung. Persona-/GM-Empfaenger sind ausschliesslich eigene, in
diesem Test gebundene `127.0.0.1:0`-Loopback-Server bzw. eine selbst erzeugte
ausfuehrbare Fake-CLI-Datei -- keine realen Anbieter/Keys, keine bestehende
OWUI-Instanz."""
from __future__ import annotations

import copy
import datetime
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import _h02_vollreise_support as sup  # noqa: E402
from mmo_sim.core import lobby_flow  # noqa: E402
from mmo_sim.core import lobby_service  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER, ZeitrissHarvestValidator, ZeitrissTableSizePolicy  # noqa: E402
from mmo_sim.lab import runner as lab_runner  # noqa: E402

_MMO_SIM = sup.MMO_SIM
SELECTED = ("sniper", "tech")  # nur diese zwei ueber --personas freigegeben.
NOT_SELECTED = ("cqb", "face", "medic", "pyro")


def _run_lab(args, env_extra=None, timeout=60, tmp_root=None, guard_dir=None, require_schema_dependency=False):
    """C1-Nachzug (01_REVIEW_H02.md §3 '11 von 12 Prozess-Invocations tragen
    PID=null', 02_AUFTRAG_RESTPFLICHTEN.md C1): vorher `subprocess.run(...)`
    -- `CompletedProcess` traegt KEINEN `pid`, der reale Kind-PID ging
    verloren. Jetzt `subprocess.Popen` mit explizitem `proc.pid`-Zugriff
    SOFORT nach dem Spawn (der echte Kind-PID, kein `os.getpid()` des
    Elternprozesses), danach `communicate(timeout=...)` -- Verhalten/
    Zeitverhalten bleibt sonst identisch zum vorherigen `subprocess.run`
    (`stdin=DEVNULL`, Text-Modus, dasselbe `timeout`, echter `TimeoutExpired`
    bei Ueberschreitung, kein stilles Verschlucken).

    C3-Nachzug r2 (01_REVIEW_H02.md §5 'alle drei realen Lab-Kinder ... hatten
    jsonschema is None ... trotzdem PASS', 02_AUFTRAG_RESTABSCHLUSS.md C3):
    `require_schema_dependency=True` (nur von den drei ECHTEN fachlichen
    Lab-Kind-Aufrufen der beiden Vollreisen gesetzt, s. test_a/test_b) macht
    `jsonschema` ueber eine exklusive Scratch-Sichtbarkeitskopie (Hashbeleg,
    keine Installation) im GLEICHEN `env` sichtbar, das gleich anschliessend
    fuer den fachlichen Subprozess verwendet wird, UND prueft VOR dessen
    Spawn per echtem Probe-Kindprozess (identisches `env`), dass die
    Dependency dort tatsaechlich ankommt -- fehlt sie, bricht diese Funktion
    kontrolliert mit AssertionError ab (BLOCKED, KEINE fachliche
    Positivreise), statt den optionalen Produktfallback unbemerkt laufen zu
    lassen."""
    root = tmp_root or Path(tempfile.mkdtemp(prefix="h02_kidtmp_"))
    schema_dependency_dir = None
    dependency_manifest = {}
    if require_schema_dependency:
        schema_dependency_dir, dependency_manifest = sup.copy_dependency_visibility(root / "schema-dependency-visibility")
    env = sup.minimal_lab_env(
        env_extra or {}, tmp_root=root, guard_dir=guard_dir, schema_dependency_dir=schema_dependency_dir,
    )
    schema_dependency_proof = None
    if require_schema_dependency:
        schema_dependency_proof = sup.probe_schema_dependency(env)
        schema_dependency_proof["dependency_visibility_manifest"] = dependency_manifest
        schema_dependency_proof["scratch_dir"] = str(schema_dependency_dir) if schema_dependency_dir else None
        assert (
            schema_dependency_proof.get("available") is True
            and schema_dependency_proof.get("functional_validate_ok") is True
        ), (
            "C3: benoetigte Schema-Dependency (jsonschema) ist im ECHTEN, fuer den gleich anschliessenden "
            f"fachlichen Request verwendeten Lab-Kind-Env NICHT importierbar/funktional nutzbar -- BLOCKED vor "
            f"jeder fachlichen Positivreise (kein Produkt-PASS ohne nachgewiesene Dependency): {schema_dependency_proof}"
        )
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    popen = subprocess.Popen(
        [sys.executable, str(_MMO_SIM), "lab", *args],
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env,
        cwd=str(_REPO_ROOT),
    )
    real_pid = popen.pid  # echter Kind-PID, sofort nach Popen() verfuegbar.
    try:
        out, err = popen.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        popen.kill()
        popen.communicate(timeout=10)
        raise
    proc = subprocess.CompletedProcess(args=popen.args, returncode=popen.returncode, stdout=out, stderr=err)
    proc._h02_pid = real_pid  # type: ignore[attr-defined]
    proc._h02_started_utc = started  # type: ignore[attr-defined]
    proc._h02_ended_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()  # type: ignore[attr-defined]
    proc._h02_cwd = str(_REPO_ROOT)  # type: ignore[attr-defined]
    proc._h02_schema_dependency_proof = schema_dependency_proof  # type: ignore[attr-defined]
    return proc


def _log_invocation(
    case: Path, name: str, args: list[str], env_extra: dict, proc: subprocess.CompletedProcess,
    pid: int | None = None,
) -> None:
    """R4-Nachzug (Review H02 2026-09-28 §5, WORKER-AUFTRAG.md C): VOLLSTAENDIGE
    tatsaechlich ausgefuehrte argv (kein `["start", "..."]`-Platzhalter mehr),
    plus cwd/pid/Start-/Endzeitpunkt, wo bekannt (Review: 'Konkrete argv,
    CWD, Exitcodes, PIDs, Zeitpunkte ... erhalten. Keine ... in
    Lieferbelegen.'). `env_extra`-WERTE werden mitgeloggt (nur synthetische
    `SYNTH-...`-Platzhalter/Loopback-URLs in diesem Test, keine echten
    Secrets) -- reine Namensliste allein war zu wenig, um argv/Env wirklich
    zu reproduzieren.

    C1-Nachzug: `pid` wird -- falls der Aufrufer keinen expliziten Wert
    uebergibt (N-STOP uebergibt den `Popen.pid` des laenger lebenden
    Controllerprozesses explizit) -- automatisch von `proc._h02_pid`
    (real via `Popen.pid` in `_run_lab` gesetzt) uebernommen. Vorher blieb
    `pid` fuer 11 von 12 Aufrufstellen `None` (Review-Befund)."""
    resolved_pid = pid if pid is not None else getattr(proc, "_h02_pid", None)
    sup.append_jsonl(case / "invocations.json", {
        "name": name, "argv": [sys.executable, str(_MMO_SIM), "lab", *args],
        "cwd": getattr(proc, "_h02_cwd", None), "pid": resolved_pid,
        "started_utc": getattr(proc, "_h02_started_utc", None),
        "ended_utc": getattr(proc, "_h02_ended_utc", None),
        "env_extra": dict(env_extra), "returncode": proc.returncode,
    })
    (case / f"stdout.{name}.txt").write_text(proc.stdout, encoding="utf-8")
    (case / f"stderr.{name}.txt").write_text(proc.stderr, encoding="utf-8")
    # C3-Nachzug r2: Beleg, DASS die Schema-Dependency-Sichtbarkeitspruefung
    # fuer dieses ECHTE Lab-Kind tatsaechlich lief (nur gesetzt, wenn der
    # Aufrufer `_run_lab(..., require_schema_dependency=True)` verwendet hat).
    dep_proof = getattr(proc, "_h02_schema_dependency_proof", None)
    if dep_proof is not None:
        sup.write_json(case / f"schema-dependency-proof.{name}.json", dep_proof)


# ---------------------------------------------------------------------------
# Gemeinsamer positiver Ablauf (Persona-/GM-Antwortsequenzen) -- identisch in
# Bedeutung fuer API- und Hybridprofil (nur der Persona-Transport wechselt).
# ---------------------------------------------------------------------------

def _leader_nomination_proposal() -> str:
    return json.dumps({
        "action": "propose", "wants": ["tech"], "leader": "tech",
        "activity": "Gemeinsamer HQ-Debriefabschnitt (H02-Vollreise)",
    })


def _accept_as_nominated_leader(offer_id: str) -> str:
    return (
        f"ENTSCHEIDUNG offer_id={offer_id} participant_id=tech decision=accept "
        "explanation=Ich uebernehme die Fuehrung."
    )


def _final_saves(keys=SELECTED) -> dict[str, dict]:
    """Rohe, UNVERAENDERTE Start-Fixture -- nur noch fuer Vorher-Vergleiche
    (`before`-Snapshots) verwendet. Der tatsaechliche Abschlusstext (G4) geht
    ueber `_distinguishable_final_saves` (s.u.), NICHT mehr ueber diese
    Funktion (R2-Nachzug, s. dort)."""
    return {pk: sup.load_fixture_save(pk) for pk in keys}


def _distinguishable_final_saves(table_id: str, section_id: str, keys=SELECTED) -> dict[str, dict]:
    """R2-Nachzug (Review H02 2026-09-28 §3, WORKER-AUFTRAG.md B): G4 nutzte
    bisher `_final_saves()` -- BYTEGLEICH zur Start-Fixture, die `make_ready`
    bereits als `current` publiziert hatte (Review-Befund: '`_final_saves()`
    verwendet dieselben Start-Fixturewerte, sodass bloßes Wiederverwenden
    des alten Current nicht sicher unterscheidbar ist'). Jede Kopie bekommt
    hier einen NEUEN `save_id` und ein zusaetzliches `_h02_end_marker`-Feld
    -- beide Aenderungen stammen AUSSCHLIESSLICH aus dieser synthetischen
    GM-Antwort (kein Nachschreiben der Ergebnisdateien nach dem Lauf, s.
    Aufrufer). `v`/`characters[0].char_id` bleiben unveraendert (Schema-/
    Identitaetspflicht, `ZeitrissHarvestValidator.validate_block` prueft
    genau diese zwei Felder)."""
    out: dict[str, dict] = {}
    for pk in keys:
        save = copy.deepcopy(sup.load_fixture_save(pk))
        save["save_id"] = f"{save['save_id']}-h02end-{table_id}-{section_id}"
        save["_h02_end_marker"] = f"H02-VOLLREISE-ENDSAVE-{pk}-{table_id}-{section_id}"
        out[pk] = save
    return out


_G0_TEXT = "Ihr steht bereit im HQ. Was ist der erste Schritt? [G0-ENDMARKER-lobby-sniper-tech]"
_G1_TEXT = "Die Lage ist ruhig, ihr koennt in Ruhe planen. [G1-ENDMARKER-lobby-sniper-tech]"
_G2_TEXT = (
    "Ihr sondiert das Gebiet in einem weiten Bogen um das HQ. Zwischenstand: keine "
    "Feindkontakte, aber ein verdaechtiges periodisches Signal im Norden, das ihr beide "
    "unabhaengig voneinander auf euren Geraeten registriert und im Logbuch vermerkt. "
    "[G2-ENDMARKER-lobby-sniper-tech]"
)
_G3_TEXT = (
    "Rueckbezug auf das Signal aus dem Norden: eine verlassene Relaisstation mit intakter "
    "Notstromversorgung. Ihr sichert gemeinsam den Zugang und dokumentiert die Koordinaten "
    "fuer den Abschlussbericht, bevor ihr euch zum Rueckweg bereitmacht. "
    "[G3-ENDMARKER-lobby-sniper-tech]"
)


def _gm_response_texts(table_id: str, section_id: str) -> list[str]:
    saves = _distinguishable_final_saves(table_id, section_id)
    g4 = f"{sup.debrief_blocks(saves)}\n{COMPLETION_MARKER} table_id={table_id} section_id={section_id}"
    return [
        _G0_TEXT,  # G0: Leader-Anker-Antwort (Import)
        _G1_TEXT,  # G1: Gastimport-Antwort
        _G2_TEXT,  # G2: lang + unterscheidbarer Endmarker (R2)
        _G3_TEXT,  # G3: lang + unterscheidbarer Endmarker (R2)
        g4,  # G4: gueltiger Abschluss + zwei unterscheidbare v7-Endsaves (R2)
    ]


def _gm_response_tuples(table_id: str, section_id: str) -> list[tuple[int, dict]]:
    return [(200, {"choices": [{"message": {"content": t}}], "usage": {}}) for t in _gm_response_texts(table_id, section_id)]


def _persona_response_sequence_for_full_journey(offer_id: str) -> list[str]:
    """Exakte Aufrufreihenfolge, aus dem echten Produktweg abgeleitet
    (`core/lobby_flow.run_lobby_window` -> `play_bound_table` ->
    `core/runtime.py:run_full_section`): tech-Consent (wird zugleich Leader)
    -> tech-Anker(G0) -> sniper-Import(G1) -> tech-Turn(G2) ->
    sniper-guest_poll -> tech-Turn(G3) -> sniper-guest_poll -> tech-Turn(G4,
    Marker) -> zwei Reflexionen -> neues Fenster: sniper-pause, tech-pause."""
    return [
        _accept_as_nominated_leader(offer_id),  # 1: tech akzeptiert + wird Leader
        "Wir sichern das HQ und starten den Debrief.",  # 2: tech G0 Leader-Anker
        "Ich sichere die Flanke und importiere meinen aktuellen Stand.",  # 3: sniper G1 Gastimport
        "Wir sondieren die Lage gemeinsam. Was faellt euch auf?",  # 4: tech G2 Debriefturn
        "Ich schlage vor, zuerst den noerdlichen Zugang zu sichern.",  # 5: sniper guest_poll
        "Wir uebernehmen den Vorschlag teilweise und ruecken vorsichtig vor.",  # 6: tech G3 Debriefturn
        "Ich bleibe in Deckung und beobachte das Relais.",  # 7: sniper guest_poll
        "Wir schliessen den HQ-Debrief kontrolliert ab.",  # 8: tech G4 Debriefturn (Marker in GM-Antwort)
        "Ich nehme mit, dass wir das HQ sauber gesichert haben.",  # 9: Reflexion Mitglied A
        "Ich nehme mit, dass die Absprache am Tisch gut funktioniert hat.",  # 10: Reflexion Mitglied B
        '{"action": "pause"}',  # 11: neues Fenster -- sniper pausiert
        '{"action": "pause"}',  # 12: neues Fenster -- tech pausiert
    ]


def _persona_response_tuples_for_full_journey(offer_id: str) -> list[tuple[int, dict]]:
    return [
        (200, {"choices": [{"message": {"content": t}}], "usage": {}})
        for t in _persona_response_sequence_for_full_journey(offer_id)
    ]


# ---------------------------------------------------------------------------
# B2-Nacharbeit (H02-Belegschluss 2026-09-28, 02_AUFTRAG_BELEGSCHLUSS.md,
# 07_HYBRID_API_SL_VOLLSTAENDIG.md §3): echte Validatoren fuer BEIDE echten
# Empfaenger (Persona-HTTP UND GM-HTTP) -- vorher liess `recording_http_server`
# JEDEN Request unbesehen durchgehen (`validators` immer leer). Jetzt prueft
# jeder Aufruf VOR der gescripteten Antwort tatsaechlich Persona/Phase
# (Praefixlaenge) bzw. den entschiedenen Leadertext; falscher/unerwarteter
# Input wird als HTTP599 abgelehnt (s. `recording_http_server.do_POST`) statt
# stillschweigend die naechste Antwort zu poppen.
# ---------------------------------------------------------------------------

_SEQ_PK = (
    "tech", "tech", "sniper", "tech", "sniper", "tech", "sniper", "tech", "sniper", "tech", "sniper", "tech",
)  # _SEQ_PK[i] = tatsaechlich entscheidende Persona fuer seq[i] (i=0..11, s. Docstring oben).

_TABLE_DECISION_PREFIX_LENGTHS = (0, 1, 2, 3, 3, 4, 4, 5, 5)  # seq[1..9], 03_ABNAHME_UND_AUFRUFE.md §1


def _persona_validators_for_full_journey(offer_id: str, table_id: str, section_id: str) -> dict:
    """Persona-HTTP-Validatoren fuer ALLE 12 Calls von `seq` (Phase 2).
    Index 0 (Consent) und 10/11 (neues Fenster/Pause) laufen ueber
    `lobby_flow.py`s eigenes `table_view={"lobby_messages": [...]}` (KEIN
    `sl_log`-Feld, andere Struktur als die Tischsicht). Index 1..9 (die neun
    realen Tischentscheidungen) pruefen zusaetzlich die tatsaechliche
    SL-Praefixlaenge (dieselben Sollwerte wie
    `_assert_public_sl_prefix_and_reflections_exact`).

    C2-Nachzug (01_REVIEW_H02.md §4 Probe 1/2, 02_AUFTRAG_RESTPFLICHTEN.md
    C2): Index 0 (tech-Consent) prueft zusaetzlich die tatsaechlich woertlich
    transportierte `offer_id` (aus `decision_contract_instruction`, s.
    `make_persona_input_validator`-Docstring) -- schliesst die Review-Probe
    'HTTP-Zustimmung ohne Angebot/Current/Phase, nur "tech spielt": HTTP200
    Erfolg'. Index 1..9 pruefen zusaetzlich `table_view["table_id"]` --
    schliesst die Review-Probe 'HTTP-Leaderimport mit falschem Tisch,
    fehlendem Current und leerem Praefix: HTTP200 Erfolg'.

    C2-Nachzug r1 (01_REVIEW_H02.md §3 'Figur, vollstaendiger Current ...
    fehlen'): JEDER der 12 Calls prueft jetzt zusaetzlich die eigene Figur
    UND den vollstaendigen Current (`make_persona_input_validator`s neue
    Parameter). Fuer Index 0..9 (Initiative bis beide Reflexionen) ist der
    erwartete Current unveraendert die Start-Fixture (`_own_system_context`
    liest ihn ueber `_resolve_active_save`, der ERST NACH gueltigem
    Abschnittsabschluss einen neuen Wert liefert -- s.
    `ui/tui.py:_own_system_context`-Docstring/eigener Kontrolllauf). Fuer
    Index 10/11 (neues Fenster NACH Abschluss) ist der erwartete Current der
    NEU veroeffentlichte Endsave (`_distinguishable_final_saves`, dieselbe
    Funktion, die G4 bereits fuer den erwarteten Endstand verwendet)."""
    sl_log_len_by_idx = {0: None, 10: None, 11: None}
    for offset, length in enumerate(_TABLE_DECISION_PREFIX_LENGTHS):
        sl_log_len_by_idx[offset + 1] = length
    final_saves = _distinguishable_final_saves(table_id, section_id)
    out = {}
    for i in range(12):
        pk = _SEQ_PK[i]
        expected_current = final_saves[pk] if i in (10, 11) else sup.load_fixture_save(pk)
        out[i] = sup.make_persona_input_validator(
            pk, sl_log_len_by_idx[i],
            expected_table_id=table_id if 1 <= i <= 9 else None,
            expected_offer_id=offer_id if i == 0 else None,
            expected_current=expected_current,
        )
    return out


def _gm_leader_texts_for_full_journey(seq: list[str]) -> list[str]:
    """Der tatsaechlich an die SL uebermittelte Leadertext je GM-Turn
    (G0-G4) -- fuer G1 ist das der ROHE Gastimporttext (`seq[2]`), weil der
    Leader (`tech`) den Gastimport unveraendert weiterreicht (A08: nur der
    Leader SENDET, der Textinhalt stammt trotzdem vom Gast), s.
    `_assert_sl_log_leader_only_and_origin`-Docstring fuer dieselbe
    Zuordnung."""
    return [seq[1], seq[2], seq[3], seq[5], seq[7]]  # G0, G1, G2, G3, G4


def _gm_validators_for_full_journey(seq: list[str]) -> dict:
    """C2-Nachzug r1 (01_REVIEW_H02.md §3, 02_AUFTRAG_C_ABSCHLUSS.md C2):
    `make_gm_leader_text_validator` prueft jetzt EXAKTE Gleichheit gegen die
    aktuelle GM-Usernachricht -- deshalb muss der uebergebene `expected_text`
    der VOLLSTAENDIGE erwartete Text sein (bei G0/G1 inklusive des erlaubt
    angehaengten Save-JSON-Blocks, `_gm_wire_texts_with_embedded_saves`),
    nicht mehr nur der rohe Leadertext."""
    return {
        idx: sup.make_gm_leader_text_validator(text)
        for idx, text in enumerate(_gm_wire_texts_with_embedded_saves(_gm_leader_texts_for_full_journey(seq)))
    }


def _assert_full_journey_final_state(case: Path, run_dir: Path, table_id: str, seq: list[str]) -> dict:
    table = core_store.Table.load(run_dir, table_id)
    assert table.status == "closed", f"Tisch haette geschlossen sein muessen: {table.status}"
    assert set(table.members) == set(SELECTED), table.members
    assert table.leader == "tech", f"nominierter Leader (tech, NICHT sniper) erwartet: {table.leader}"
    locks = core_store._read_locks(run_dir)
    assert locks == {}, f"Locks nach Abschluss geloest erwartet: {locks}"
    _assert_sl_log_leader_only_and_origin(table, seq)
    summary = {
        "table_leader": table.leader, "table_members": sorted(table.members), "table_status": table.status,
        "sl_log": [dict(e) for e in table.sl_log],
    }
    sup.write_json(case / "final_table_state.json", summary)
    return summary


def _offer_id_for_first_window(community_participant_id: str) -> str:
    community_id = f"community-{community_participant_id}"
    window_id = f"lobby-{community_id}-0"
    return lobby_service.offer_id_for(window_id, "sniper", 0)


# ---------------------------------------------------------------------------
# R2/R4-Nachzug (Review H02 2026-09-28 §3/§5): gemeinsame, aus dem ECHTEN
# Produktverhalten (ground-truth-Laeufe mit Debug-Dump gegen `table.sl_log`
# und die reale `persona-receipts.jsonl`) abgeleitete Inhaltspruefungen --
# fuer API- UND Hybridprofil gleichermassen verwendet, da beide denselben
# `_own_system_context`/`render_public_wire_text`-Vertrag durchlaufen (nur
# der Transport wechselt).
# ---------------------------------------------------------------------------

def _own_marker(pk: str) -> str:
    """Woertliche Kopfzeile aus `persona_state.render_for_prompt` -- die
    einzige zuverlaessige Stelle, um im tatsaechlich gesendeten eigenen
    Kontext OHNE Rateannahme ueber Aufrufreihenfolge zu erkennen, welche
    Persona gerade entscheidet."""
    return f"{pk} spielt"


def _identify_persona(system_text: str, user_text: str) -> str | None:
    haystack = f"{system_text}\n{user_text}"
    if _own_marker("sniper") in haystack:
        return "sniper"
    if _own_marker("tech") in haystack:
        return "tech"
    return None


def _assert_sl_log_leader_only_and_origin(table, seq: list[str]) -> None:
    """A08 (02_ABNAHME_UND_AUFRUFE.md §1): NUR der Leader sendet an die SL
    (`leader_message` in JEDEM Eintrag); `origin_persona_key` markiert
    zusaetzlich, WESSEN Entscheidung ein Eintrag inhaltlich ist (weicht fuer
    den G1-Gastimport vom technischen Absender 'tech' ab). Exakte Texte aus
    der ECHTEN `table.sl_log` gegen die tatsaechlich gescripteten Persona-
    Antworten (`seq`, dieselbe Liste wie an den Empfaenger gesendet) --
    Indizes empirisch aus einem eigenen Ground-Truth-Lauf (Debug-Dump gegen
    `table.sl_log`) abgeleitet, keine Annahme aus dem Docstring allein. Prueft
    zusaetzlich: die ROHEN Gastberatungstexte (`seq[4]`/`seq[6]`, guest_poll
    vor G3/G4) duerfen in KEINEM `leader_message` automatisch auftauchen --
    der Leader entscheidet nachweislich seinen EIGENEN Text (kein Auto-
    Anhaengen der Beratung)."""
    assert len(table.sl_log) == 5, f"G0-G4 = 5 sl_log-Eintraege erwartet, {len(table.sl_log)} gefunden"
    expected = [
        (seq[1], "tech"),    # G0: Leader-Anker (eigener Text + eigener Save)
        (seq[2], "sniper"),  # G1: Gastimport -- Text/Save vom Gast, Absender bleibt der Leader
        (seq[3], "tech"),    # G2
        (seq[5], "tech"),    # G3
        (seq[7], "tech"),    # G4 (Abschluss)
    ]
    guest_raw_suggestions = (seq[4], seq[6])
    for i, (entry, (expected_text, expected_origin)) in enumerate(zip(table.sl_log, expected)):
        assert entry["leader_message"].startswith(expected_text), (
            f"sl_log[{i}]: leader_message weicht vom tatsaechlich entschiedenen Text ab: "
            f"{entry['leader_message']!r} (erwartetes Praefix: {expected_text!r})"
        )
        assert entry["origin_persona_key"] == expected_origin, (
            f"sl_log[{i}]: origin_persona_key={entry['origin_persona_key']!r}, erwartet {expected_origin!r}"
        )
        for raw in guest_raw_suggestions:
            assert raw not in entry["leader_message"], (
                f"sl_log[{i}]: rohe Gastberatung {raw!r} automatisch in Leadertext uebernommen (A08-Verstoss)"
            )


def _decode_public_table_view_or_fail(wire_text: str, where: str) -> dict:
    table_view = sup.decode_public_table_view(wire_text)
    assert table_view is not None, f"{where}: [OEFFENTLICHE_TISCHSICHT]-Block fehlt im Wire"
    return table_view


def _assert_public_sl_prefix_and_reflections_exact(
    classified: list[dict], gm_texts: list[str], table_id: str,
) -> None:
    """B1-Nacharbeit (H02-Belegschluss 2026-09-28, 02_AUFTRAG_BELEGSCHLUSS.md,
    07_HYBRID_API_SL_VOLLSTAENDIG.md §4, 01_REVIEW_H02.md §3 M3/M4-Befund):
    ERSETZT die fruehere zu schwache `_assert_reflections_see_full_history`
    (pruefte NUR die beiden Reflexionen, G0-G3 als reinen Substring-Check,
    G4 NUR am Abschlussmarker statt Volltext -- ein an den NORMALEN
    Tischentscheidungen geleerter Spielpraefix [M3-Mutationsklasse] UND ein
    auf den Marker gekuerztes G4 im Persona-Wire [M4-Mutationsklasse]
    blieben dadurch beide unentdeckt, 8/8 rc0 trotz Verstoss).

    Dekodiert an JEDER der NEUN realen Tischentscheidungen (`classified[1..9]`
    == `seq[1..9]`, s. `_persona_response_sequence_for_full_journey`-
    Docstring: G0-Leaderimport, G1-Gastimport, G2, Gastberatung-vor-G3, G3,
    Gastberatung-vor-G4, G4, beide Reflexionen -- Praefixlaengen laut
    03_ABNAHME_UND_AUFRUFE.md §1 exakt `0,1,2,3,3,4,4,5,5`) den tatsaechlich
    gesendeten `[OEFFENTLICHE_TISCHSICHT]`-JSON-Block (`table_view["sl_log"]`,
    s. `core/store.py:persona_view`) und vergleicht JEDEN bereits
    vorhandenen Eintrag ZEICHEN FUER ZEICHEN (`entry["content"] ==
    gm_texts[j]`) gegen das tatsaechliche GM-Ausgabejournal (`gm_texts`,
    dieselbe Liste, die an den GM-Empfaenger gescriptet wurde) -- keine
    Marker-/Laengenersatzpruefung, kein Verlangen nach noch nicht erzeugten
    Antworten (nur Indizes < aktueller Praefixlaenge werden geprueft).

    Bei den beiden Reflexionen (Praefixlaenge 5, `classified[8]`/`[9]`)
    deckt DIESELBE Schleife automatisch G0-G4 VOLLSTAENDIG ab -- inklusive
    des kompletten G4-Debrief-/Saveblocks (`gm_texts[4]`), weil `content`
    dort der volle unveraenderte GM-Text ist (JSON korrekt dekodiert, kein
    Escaping-Vorwand fuer eine Markerersatzpruefung)."""
    assert len(classified) >= 10, f"zu wenige klassifizierte Wires fuer Praefixpruefung: {len(classified)}"
    for offset, expected_len in enumerate(_TABLE_DECISION_PREFIX_LENGTHS):
        i = offset + 1  # classified[1..9] == seq[1..9]
        entry = classified[i]
        assert entry["pk"] == _SEQ_PK[i], (
            f"classified[{i}]: unerwartete entscheidende Persona {entry['pk']!r}, erwartet {_SEQ_PK[i]!r}"
        )
        table_view = _decode_public_table_view_or_fail(entry["user"], f"classified[{i}] (pk={entry['pk']})")
        assert table_view.get("table_id") == table_id, (
            f"classified[{i}]: table_id im table_view weicht ab: {table_view.get('table_id')!r} != {table_id!r}"
        )
        sl_log = table_view.get("sl_log")
        assert isinstance(sl_log, list), f"classified[{i}]: sl_log fehlt/keine Liste: {sl_log!r}"
        assert len(sl_log) == expected_len, (
            f"classified[{i}] (pk={entry['pk']}): SL-Praefixlaenge {len(sl_log)} != erwartet {expected_len} "
            f"(G04: unvollstaendiger/veraenderter oeffentlicher Verlauf)"
        )
        for j in range(expected_len):
            actual = sl_log[j].get("content")
            assert actual == gm_texts[j], (
                f"classified[{i}] (pk={entry['pk']}) sl_log[{j}]: oeffentlicher GM-Text weicht exakt ab "
                f"(G04/G05: kein Zeichen-fuer-Zeichen-Match). erwartet={gm_texts[j]!r} ist={actual!r}"
            )


# ---------------------------------------------------------------------------
# B2-Nacharbeit (G10, 02_AUFTRAG_BELEGSCHLUSS.md, 07_HYBRID_API_SL_VOLLSTAENDIG.md
# §6): requestweise Ledger-/Verbrauchszuordnung fuer die 13 Persona- + 5
# GM-Entscheidungen -- vorher wurde nur `status.turns_used == 18` (eine reine
# Summe) geprueft. Rollen-/Teilnehmerreihenfolge stammen aus dem echten
# Produktweg (`lobby_flow.py` Zeile ~515/526: role="lobby_offer_response"/
# "lobby_initiative"; `runtime.py` Zeile ~170/467: role="persona_decision"/
# "guest_poll"/"reflection"/"gm_turn"), keine erfundenen Werte.
# ---------------------------------------------------------------------------

_EXPECTED_LEDGER_PERSONA_ROLES = (
    "lobby_initiative",      # Phase1: sniper-Initiative (propose)
    "lobby_offer_response",  # seq[0]: tech akzeptiert (wird Leader)
    "persona_decision",      # seq[1]: tech G0 Leader-Anker
    "persona_decision",      # seq[2]: sniper G1 Gastimport
    "persona_decision",      # seq[3]: tech G2
    "guest_poll",            # seq[4]: sniper guest_poll
    "persona_decision",      # seq[5]: tech G3
    "guest_poll",            # seq[6]: sniper guest_poll
    "persona_decision",      # seq[7]: tech G4
    "reflection",            # seq[8]: sniper Reflexion
    "reflection",            # seq[9]: tech Reflexion
    "lobby_initiative",      # seq[10]: sniper pausiert (neues Fenster)
    "lobby_initiative",      # seq[11]: tech pausiert (neues Fenster)
)
_EXPECTED_LEDGER_PARTICIPANTS = ("sniper",) + _SEQ_PK  # Initiative-Proposer + _SEQ_PK[0..11]


def _expected_ledger_operations(community_participant_id: str, table_id: str, section_id: str) -> tuple[list[dict], list[dict]]:
    """C1-Nachzug (02_AUFTRAG_C_ABSCHLUSS.md C1, 01_REVIEW_H02.md §2 'die
    erlaubte Alternative muss wirklich eindeutig sein ... table_id,
    section_id, turn_idx ... werden hier nicht geprueft'): die vollstaendige
    Operationsidentitaet (`table_id`, `section_id`, `role`, `turn_idx`,
    `participant` -- exakt `request_ledger._operation_identity`s Tupelfelder)
    fuer alle 13 Persona- + 5 GM-Records dieser FESTEN H02-Vollreise-Fixture.

    Sollwerte stammen NICHT aus einem zu pruefenden Record, sondern aus (a)
    der bereits bekannten Fenster-/Sectionadressierung (`lobby_service`:
    `section_id=f'lobby-community-{{...}}-{{fensterindex}}'`, Fenster 0 =
    Initiative bis Tischbindung, Fenster 1 = neues Fenster nach Abschluss,
    `table_id=None` fuer beide Lobbyfenster-Rollen) und (b) einem eigenen,
    isolierten Kontrolllauf ausserhalb dieser Testdatei (read-only gegen
    `request_ledger._all_records`, KEIN Produktschreibzugriff durch die
    Kontrolle selbst) gegen exakt dieselbe Fixture (`sniper`propose/`tech`
    Leader, `_persona_response_sequence_for_full_journey`) -- `turn_idx`
    erhoeht sich pro abgeschlossenem SL-Turn (G0..G4 = 0..4, geteilt von
    Persona- UND GM-Record desselben Turns); `guest_poll` traegt den
    turn_idx des JEWEILS NAECHSTEN persona_decision-Turns (kein eigener
    Zaehler); beide Reflexionen turn_idx=5 (nach G4); GM-`participant` ist
    die URSPRUENGLICHE entscheidende Persona des Turns (bei G1 `sniper`,
    obwohl technisch `tech` als Leader sendet -- s.
    `_gm_leader_texts_for_full_journey`-Docstring), nicht der HTTP-Absender."""
    community_id = f"community-{community_participant_id}"
    window0 = f"lobby-{community_id}-0"
    window1 = f"lobby-{community_id}-1"
    persona_ops = [
        {"table_id": None, "section_id": window0, "turn_idx": 0, "role": "lobby_initiative", "participant": "sniper"},
        {"table_id": None, "section_id": window0, "turn_idx": 0, "role": "lobby_offer_response", "participant": "tech"},
        {"table_id": table_id, "section_id": section_id, "turn_idx": 0, "role": "persona_decision", "participant": "tech"},
        {"table_id": table_id, "section_id": section_id, "turn_idx": 1, "role": "persona_decision", "participant": "sniper"},
        {"table_id": table_id, "section_id": section_id, "turn_idx": 2, "role": "persona_decision", "participant": "tech"},
        {"table_id": table_id, "section_id": section_id, "turn_idx": 3, "role": "guest_poll", "participant": "sniper"},
        {"table_id": table_id, "section_id": section_id, "turn_idx": 3, "role": "persona_decision", "participant": "tech"},
        {"table_id": table_id, "section_id": section_id, "turn_idx": 4, "role": "guest_poll", "participant": "sniper"},
        {"table_id": table_id, "section_id": section_id, "turn_idx": 4, "role": "persona_decision", "participant": "tech"},
        {"table_id": table_id, "section_id": section_id, "turn_idx": 5, "role": "reflection", "participant": "sniper"},
        {"table_id": table_id, "section_id": section_id, "turn_idx": 5, "role": "reflection", "participant": "tech"},
        {"table_id": None, "section_id": window1, "turn_idx": 0, "role": "lobby_initiative", "participant": "sniper"},
        {"table_id": None, "section_id": window1, "turn_idx": 0, "role": "lobby_initiative", "participant": "tech"},
    ]
    gm_ops = [
        {"table_id": table_id, "section_id": section_id, "turn_idx": 0, "role": "gm_turn", "participant": "tech"},
        {"table_id": table_id, "section_id": section_id, "turn_idx": 1, "role": "gm_turn", "participant": "sniper"},
        {"table_id": table_id, "section_id": section_id, "turn_idx": 2, "role": "gm_turn", "participant": "tech"},
        {"table_id": table_id, "section_id": section_id, "turn_idx": 3, "role": "gm_turn", "participant": "tech"},
        {"table_id": table_id, "section_id": section_id, "turn_idx": 4, "role": "gm_turn", "participant": "tech"},
    ]
    assert [o["role"] for o in persona_ops] == list(_EXPECTED_LEDGER_PERSONA_ROLES)
    assert [o["participant"] for o in persona_ops] == list(_EXPECTED_LEDGER_PARTICIPANTS)
    return persona_ops, gm_ops


def _identity_tuple(op_or_record: dict) -> tuple:
    return (op_or_record.get("table_id"), op_or_record.get("section_id"), op_or_record.get("role"),
            op_or_record.get("turn_idx"), op_or_record.get("participant"))


def _assert_request_ledger_reconciles(
    run_dir: Path, table_id: str, section_id: str, community_participant_id: str,
    *, persona_journal: "list[dict] | None" = None, gm_journal: "list[dict] | None" = None,
) -> dict:
    """Ordnet die 13 Persona- + 5 GM-Entscheidungen requestweise gegen das
    VORHANDENE `request_ledger` zu (kein `>=`, kein Summenlabel, keine neuen
    Produkt-Ledgerfelder erfunden -- `role`/`participant`/`table_id`/
    `section_id`/`turn_idx`/`state` sind bereits bestehende Vertragsfelder
    aus `core/request_ledger.py:begin`/`_operation_identity`).

    C1-Nachzug r1 (01_REVIEW_H02.md §2): zusaetzlich zur bisherigen Rollen-/
    Teilnehmerreihenfolge wird JEDER der 18 Records exakt gegen seine
    UNABHAENGIG hergeleitete Sollidentitaet (`_expected_ledger_operations`,
    NICHT aus dem Record selbst) auf `table_id`/`section_id`/`turn_idx`
    geprueft, UND die Eindeutigkeit aller 18 `_operation_identity`-Tupel
    wird erzwungen (keine zwei Records mit identischer Identitaet -- eine
    echte Mehrdeutigkeit waere sonst unentdeckt). Das schliesst die
    Review-Luecke 'Persona-table_id/section_id/turn_idx ... werden hier
    nicht geprueft' UND die Review-Gegenprobe (`turn_idx:0->999`/
    `section_id->FOREIGN-SECTION-C-REVIEW` wurden vom alten Reconciler
    akzeptiert, s. `test_c1_corrupted_ledger_evidence_rejected`).

    C1-Nachzug r2 (01_REVIEW_H02.md §2 '19-statt-18 ... akzeptiert und weiter
    total:18', 02_AUFTRAG_RESTABSCHLUSS.md C1): die BISHERIGE `total`-Zahl
    zaehlte nur die beiden BEREITS GEFILTERTEN Listen (`persona_records`:
    alle `role!=gm_turn`; `gm_records`: `role==gm_turn AND table_id==table_id`)
    -- ein zusaetzlicher, bereits verbuchter GM-Record fuer einen FREMDEN
    Tisch wird vom `table_id`-Filter stillschweigend verschluckt und taucht
    in keiner der beiden gefilterten Listen auf, obwohl `_all_records`
    tatsaechlich 19 Datensaetze liefert. Deshalb JETZT VOR jeder Filterung
    die UNGEFILTERTE Rohmenge selbst auf exakt 18 geprueft (kein `>=`, keine
    Toleranz) -- genau der in `test_c1_corrupted_ledger_evidence_rejected`
    (dritter Fall) reproduzierte Review-Befund.

    C1-Nachzug r2 (01_REVIEW_H02.md §3 'Zaehlzusammenfassung ... reicht
    nicht'): `persona_journal`/`gm_journal` (falls vom Aufrufer uebergeben)
    sind die BEREITS VORHANDENEN echten Empfangs-/Antwortjournale in EXAKT
    derselben chronologischen Reihenfolge wie `persona_records`/`gm_records`
    (API: `recording_http_server(...).received`-Eintraege inkl. `body`/
    `response_body`/Hashes/Zeiten; Hybrid: CLI-`argv`/`stdin` +
    Antwortjournal-`rc`/`stdout`-Eintrag je Position) -- KEINE zweite
    Buchhaltung, keine neuen Produktfelder, kein interner Persona-ctx-Hash.
    Der Rueckgabewert `assignments` verknuepft JEDEN der 18 Records einzeln
    mit Request-ID, gepruefter Operationsidentitaet, dem originalen
    Journaleintrag (tatsaechlicher Input UND Output) und den vorhandenen
    Abrechnungsfeldern DES LEDGERRECORDS SELBST (`reserved_usd`/
    `dollar_billed`/`usd_reconciled`/`usage`) -- ohne Journal bleibt
    `assignments[i]["journal"]` `None` (z.B. in der synthetischen
    Korruptionsgegenprobe, die kein reales Journal hat)."""
    from mmo_sim.core import request_ledger
    records = request_ledger._all_records(run_dir)
    assert len(records) == 18, (
        f"G10/C1: UNGEFILTERTE Gesamt-Requestmenge muss exakt 18 sein (ein synthetischer Lauf), "
        f"{len(records)} tatsaechliche Records gefunden VOR jeder Filterung "
        f"(ids={[r.get('id') for r in records]}, table_ids={sorted({r.get('table_id') for r in records}, key=str)})"
    )
    gm_records = sorted(
        [r for r in records if r.get("role") == "gm_turn" and r.get("table_id") == table_id],
        key=lambda r: r.get("reserved_ts", 0),
    )
    persona_records = sorted(
        [r for r in records if r.get("role") != "gm_turn"],
        key=lambda r: r.get("reserved_ts", 0),
    )
    assert len(persona_records) == 13, (
        f"G10: 13 Persona-Ledgerrecords erwartet, {len(persona_records)} gefunden "
        f"(roles={[r.get('role') for r in persona_records]})"
    )
    assert len(gm_records) == 5, f"G10: 5 GM-Ledgerrecords (role=gm_turn, table_id={table_id!r}) erwartet, {len(gm_records)} gefunden"
    actual_roles = tuple(r.get("role") for r in persona_records)
    assert actual_roles == _EXPECTED_LEDGER_PERSONA_ROLES, (
        f"G10: Persona-Rollenreihenfolge weicht vom echten Produktweg ab: {actual_roles} != {_EXPECTED_LEDGER_PERSONA_ROLES}"
    )
    actual_participants = tuple(r.get("participant") for r in persona_records)
    assert actual_participants == _EXPECTED_LEDGER_PARTICIPANTS, (
        f"G10: Teilnehmerreihenfolge weicht ab: {actual_participants} != {_EXPECTED_LEDGER_PARTICIPANTS}"
    )
    for r in persona_records + gm_records:
        assert r.get("state") == "accounted", (
            f"G10: Ledgerrecord nicht abschliessend verbucht: id={r.get('id')} role={r.get('role')} state={r.get('state')!r}"
        )
    # C1-Nachzug: exakte table_id/section_id/turn_idx-Zuordnung + Eindeutigkeit.
    expected_persona_ops, expected_gm_ops = _expected_ledger_operations(community_participant_id, table_id, section_id)
    for i, (rec, expected) in enumerate(zip(persona_records, expected_persona_ops)):
        for field in ("table_id", "section_id", "turn_idx"):
            assert rec.get(field) == expected[field], (
                f"G10/C1: Persona-Record[{i}] (role={rec.get('role')!r}, participant={rec.get('participant')!r}) "
                f"{field}={rec.get(field)!r} != unabhaengig erwartet {expected[field]!r}"
            )
    for i, (rec, expected) in enumerate(zip(gm_records, expected_gm_ops)):
        for field in ("table_id", "section_id", "turn_idx", "participant"):
            assert rec.get(field) == expected[field], (
                f"G10/C1: GM-Record[{i}] {field}={rec.get(field)!r} != unabhaengig erwartet {expected[field]!r}"
            )
    all_18 = persona_records + gm_records
    identities = [_identity_tuple(r) for r in all_18]
    assert len(set(identities)) == 18, (
        f"G10/C1: {len(all_18)} Records ergeben nur {len(set(identities))} eindeutige Operationsidentitaeten "
        f"(Mehrdeutigkeit/Doppelbindung) -- Identitaeten: {identities}"
    )

    # C1-Nachzug r2: 18 EINZELNE Zuordnungen (Request-ID, gepruefte
    # Operationsidentitaet, echter Journaleintrag als Input+Output-Referenz,
    # Abrechnung aus dem Ledgerrecord selbst) statt nur vier Zaehlwerte.
    if persona_journal is not None:
        assert len(persona_journal) == 13, (
            f"G10/C1: persona_journal muss genau 13 Eintraege haben (1:1 zu den 13 Persona-Records), "
            f"{len(persona_journal)} erhalten -- fehlende/zusaetzliche Journalzeilen werden abgelehnt"
        )
    if gm_journal is not None:
        assert len(gm_journal) == 5, (
            f"G10/C1: gm_journal muss genau 5 Eintraege haben (1:1 zu den 5 GM-Records), "
            f"{len(gm_journal)} erhalten -- fehlende/zusaetzliche Journalzeilen werden abgelehnt"
        )
    persona_journal_padded = persona_journal if persona_journal is not None else [None] * len(persona_records)
    gm_journal_padded = gm_journal if gm_journal is not None else [None] * len(gm_records)
    assignments = []
    for rec, journal_entry in zip(persona_records, persona_journal_padded):
        assignments.append({
            "request_id": rec.get("id"), "role": rec.get("role"), "participant": rec.get("participant"),
            "table_id": rec.get("table_id"), "section_id": rec.get("section_id"), "turn_idx": rec.get("turn_idx"),
            "state": rec.get("state"),
            "billing": {
                "reserved_usd": rec.get("reserved_usd"), "dollar_billed": rec.get("dollar_billed"),
                "usd_reconciled": rec.get("usd_reconciled"), "usage": rec.get("usage"),
            },
            "journal": journal_entry,
        })
    for rec, journal_entry in zip(gm_records, gm_journal_padded):
        assignments.append({
            "request_id": rec.get("id"), "role": rec.get("role"), "participant": rec.get("participant"),
            "table_id": rec.get("table_id"), "section_id": rec.get("section_id"), "turn_idx": rec.get("turn_idx"),
            "state": rec.get("state"),
            "billing": {
                "reserved_usd": rec.get("reserved_usd"), "dollar_billed": rec.get("dollar_billed"),
                "usd_reconciled": rec.get("usd_reconciled"), "usage": rec.get("usage"),
            },
            "journal": journal_entry,
        })
    assert len(assignments) == 18, f"G10/C1: {len(assignments)} Zuordnungen statt 18 aufgebaut"

    return {
        "persona_records": len(persona_records), "gm_records": len(gm_records), "total": len(all_18),
        "unique_operation_identities": len(set(identities)),
        "assignments": assignments,
        "journal_based": persona_journal is not None and gm_journal is not None,
    }


def _write_synthetic_ledger_copy(run_dir: Path, ops: list[dict]) -> None:
    """Schreibt EIGENE, rein synthetische `request_ledger`-Requestdatensaetze
    (ueber die vorhandene `request_ledger._write_request`-I/O-Hilfsfunktion,
    KEIN neues Schreibformat) fuer `test_c1_corrupted_ledger_evidence_rejected`
    -- kopierte Testevidenz, kein Produktlauf, kein Netzwerk."""
    from mmo_sim.core import request_ledger
    for i, op in enumerate(ops):
        data = {
            "id": f"synthetic-{i:02d}", "role": op["role"], "route": None,
            "content_chars": 0, "content_sha256": hashlib.sha256(b"").hexdigest(),
            "output_limit_tokens": None, "reserved_usd": 0.0,
            "table_id": op["table_id"], "section_id": op["section_id"], "turn_idx": op["turn_idx"],
            "participant": op["participant"], "state": "accounted",
            "reserved_ts": float(i), "sent_ts": float(i), "settled_ts": float(i),
            "usage": None, "error": None, "usd_reconciled": True, "result_text": "synthetic",
            "dollar_billed": op["role"] != "lobby_initiative",
        }
        request_ledger._write_request(run_dir, data["id"], data)


def test_c1_corrupted_ledger_evidence_rejected():
    """C1-Nachzug (01_REVIEW_H02.md §2 'Eigene Gegenprobe, nur an kopierter
    synthetischer Ledger-Evidenz, keine Produktmutante: Derselbe unveraenderte
    Reconciler akzeptiert sowohl turn_idx:0->999 als auch section_id->FOREIGN-
    SECTION-C-REVIEW an einem tatsaechlichen tech-Record und meldet weiter
    13+5=18. Der gesunde Originaldatensatz besteht vorher.'): schreibt DIESE
    Gegenprobe als REALE Requestdatensatzdateien in getrennten frischen
    Test-`run_dir`s (kein Produktschreiben ausserhalb dieser Testdateien,
    kein realer Lauf/Netzwerk) und ruft den TATSAECHLICHEN, jetzt gefixten
    `_assert_request_ledger_reconciles` GENAU SO auf, wie es die beiden
    Vollreise-Tests tun -- beweist, dass der reale Code (nicht nur eine
    Nachbildung) beide Korruptionen ablehnt, waehrend das gesunde Original
    weiter besteht.

    C1-Nachzug r2 (01_REVIEW_H02.md §2 'ein zusaetzlicher bereits verbuchter
    GM-Record fuer einen fremden Tisch -- tatsaechlich 19 Records, trotzdem
    akzeptiert und weiter total:18', 02_AUFTRAG_RESTABSCHLUSS.md C1 '19-statt-
    18-Evidenzprobe MUSS scheitern'): vierter Fall unten -- 18 gesunde
    Records PLUS ein zusaetzlicher, bereits verbuchter `gm_turn`-Record fuer
    einen FREMDEN Tisch (`table_id` != der hier geprueften). Der `table_id`-
    Filter auf `gm_records` UND die reine `role!=gm_turn`-Filterung auf
    `persona_records` verschlucken diesen 19. Record stillschweigend --
    NUR die neue Pruefung der UNGEFILTERTEN Rohmenge (`len(records)==18`,
    VOR jeder Filterung) kann ihn ueberhaupt entdecken."""
    table_id, section_id = "lobby-sniper-tech", "lobby-sniper-tech-section"
    persona_ops, gm_ops = _expected_ledger_operations("h02api", table_id, section_id)
    healthy_ops = persona_ops + gm_ops

    with tempfile.TemporaryDirectory() as td_healthy:
        run_dir = Path(td_healthy)
        _write_synthetic_ledger_copy(run_dir, healthy_ops)
        summary = _assert_request_ledger_reconciles(run_dir, table_id, section_id, "h02api")
        assert summary["total"] == 18, "gesundes Original haette bestehen muessen"

    corrupted_turn_idx = [dict(o) for o in healthy_ops]
    corrupted_turn_idx[2] = dict(corrupted_turn_idx[2], turn_idx=999)  # echter tech-persona_decision-Record (G0).
    with tempfile.TemporaryDirectory() as td_turn:
        run_dir = Path(td_turn)
        _write_synthetic_ledger_copy(run_dir, corrupted_turn_idx)
        try:
            _assert_request_ledger_reconciles(run_dir, table_id, section_id, "h02api")
            raised = False
        except AssertionError as exc:
            raised = True
            assert "turn_idx" in str(exc)
        assert raised, "C1: turn_idx:0->999-Korruption haette abgelehnt werden muessen (Review-Befund: akzeptiert)"

    corrupted_section_id = [dict(o) for o in healthy_ops]
    corrupted_section_id[2] = dict(corrupted_section_id[2], section_id="FOREIGN-SECTION-C-REVIEW")
    with tempfile.TemporaryDirectory() as td_section:
        run_dir = Path(td_section)
        _write_synthetic_ledger_copy(run_dir, corrupted_section_id)
        try:
            _assert_request_ledger_reconciles(run_dir, table_id, section_id, "h02api")
            raised = False
        except AssertionError as exc:
            raised = True
            assert "section_id" in str(exc)
        assert raised, "C1: section_id->FOREIGN-SECTION-C-REVIEW-Korruption haette abgelehnt werden muessen (Review-Befund: akzeptiert)"

    # C1-Nachzug r2 (19-statt-18-Evidenzprobe, s. Docstring oben): 18 gesunde
    # Records + 1 zusaetzlicher bereits verbuchter GM-Record fuer einen
    # FREMDEN Tisch -- der table_id-Filter auf gm_records liesse diesen
    # Record unentdeckt (er landet in KEINER der beiden gefilterten Listen),
    # deshalb MUSS die neue Rohmengenpruefung (len(records)==18) ihn fangen.
    extra_foreign_table_gm_op = dict(
        gm_ops[0], table_id="FOREIGN-TABLE-C-REVIEW", section_id="FOREIGN-TABLE-C-REVIEW-section", turn_idx=0,
    )
    nineteen_ops = healthy_ops + [extra_foreign_table_gm_op]
    with tempfile.TemporaryDirectory() as td_extra:
        run_dir = Path(td_extra)
        _write_synthetic_ledger_copy(run_dir, nineteen_ops)
        from mmo_sim.core import request_ledger
        assert len(request_ledger._all_records(run_dir)) == 19, (
            "C1-Testaufbau: die Gegenprobe muss tatsaechlich 19 rohe Records auf der Platte erzeugen"
        )
        try:
            summary = _assert_request_ledger_reconciles(run_dir, table_id, section_id, "h02api")
            raised = False
        except AssertionError as exc:
            raised = True
            assert "18" in str(exc), f"C1: Fehlermeldung sollte die Ungefiltert-18-Erwartung nennen: {exc}"
        assert raised, (
            "C1: 19-statt-18-Evidenzprobe (zusaetzlicher GM-Record fuer fremden Tisch) haette abgelehnt "
            "werden muessen (Review-Befund: weiterhin total:18 trotz 19 realer Records)"
        )


def _gm_wire_texts_with_embedded_saves(gm_leader_texts: list[str]) -> list[str]:
    """C1-Nachzug: `core/runtime.py:act()` haengt bei G0 (Leader-Anker,
    `attach_import_save=True`) und G1 (Gastimport, `attach_import_save=True`)
    den jeweils eigenen Start-v7-Save als sichtbaren Fenced-JSON-Block an
    den Wire-Text an (`_embed_json_block(text, save_payload)`, Zeile ~643-
    654), BEVOR dieser Text an `submit()`/`request_ledger.begin(content=...)`
    geht -- G2/G3/G4 (keine Importturns) bleiben unveraendert. Empirisch
    gegen einen eigenen Kontrolllauf verifiziert (echter `content_sha256`
    des ersten GM-Ledgerrecords == `sha256(_embed_json_block(seq[1],
    fixture_save('tech')))`). `leader`/`guest` sind in dieser H02-Vollreise
    IMMER `tech`/`sniper` (s. `_leader_nomination_proposal`)."""
    from mmo_sim.core.runtime import _embed_json_block
    g0, g1, g2, g3, g4 = gm_leader_texts
    return [
        _embed_json_block(g0, sup.load_fixture_save("tech")),
        _embed_json_block(g1, sup.load_fixture_save("sniper")),
        g2, g3, g4,
    ]


def _assert_gm_ledger_content_matches_observed(
    run_dir: Path, table_id: str, gm_leader_texts: list[str], gm_received: "list[dict] | None" = None,
) -> dict:
    """C1-Nachzug (01_REVIEW_H02.md §3 'requestweise nachvollziehbare
    Zuordnung ... Content-Hash nach dessen echtem Normalisierungsvertrag',
    02_AUFTRAG_RESTPFLICHTEN.md C1): `request_ledger.begin(role='gm_turn',
    content=text, ...)` hasht/laengt GENAU den an die SL gesendeten
    Wire-Text (`core/runtime.py:submit`, `content=text` woertlich). Dieser
    `text` ist bei G0/G1 NICHT der rohe Persona-Entscheidungstext, sondern
    inklusive eines angehaengten Save-JSON-Blocks (s. `_gm_wire_texts_with_
    embedded_saves`-Docstring) -- bei G2/G3/G4 unveraendert. Fuer alle 5
    GM-Records ist dieser vollstaendige Text damit AUSSERHALB des Produkts
    exakt rekonstruierbar (kein erfundenes Feld): `content_sha256 ==
    sha256(text)`, `content_chars == len(text)`. Fuer die 13 Persona-Records
    ist `content = json.dumps(ctx, ...)` -- der interne `ctx`-Dict (inkl.
    `own_context`/`decision_contract`) ist AUSSERHALB des Produkts nicht
    bytegleich rekonstruierbar; deren Identitaet wird stattdessen -- wie vom
    Produkt selbst als massgeblich behandelt, s. `request_ledger.begin`-
    Docstring '`_operation_identity` (table_id, section_id, role, turn_idx,
    participant)' -- bereits vollstaendig durch `_assert_request_ledger_
    reconciles` geprueft (Rollen-/Teilnehmerreihenfolge exakt); das ist keine
    Luecke dieser Funktion, sondern eine bewusste Scope-Trennung, die diese
    Funktion NICHT als erledigt unterschlaegt (s. WORKER-REPORT).

    C1-Nachzug r1 (01_REVIEW_H02.md §2 'GM-content_sha256/content_chars
    gegen die TATSAECHLICHE aktuelle User-Nachricht des echten GM-HTTP-
    Receipts ..., nicht bloss Fixtureberechnung'): ist `gm_received`
    (`recording_http_server`s `.received`-Liste, die TATSAECHLICH am GM-
    Empfaenger eingetroffenen Bodies) uebergeben, wird ZUSAETZLICH jeder
    GM-Ledgerrecord gegen `gm_received[i]["body"]["messages"][-1]["content"]`
    geprueft -- die echten Receiptbytes, kein rekonstruierter Fixturewert.
    Beide Pruefungen (Fixture-Rekonstruktion UND echter Receipt) muessen
    uebereinstimmen; ohne `gm_received` bleibt nur die Fixture-Pruefung
    (Rueckwaertskompatibilitaet fuer Aufrufer, die den Receipt nicht mehr im
    Scope halten)."""
    from mmo_sim.core import request_ledger
    records = request_ledger._all_records(run_dir)
    gm_records = sorted(
        [r for r in records if r.get("role") == "gm_turn" and r.get("table_id") == table_id],
        key=lambda r: r.get("reserved_ts", 0),
    )
    full_texts = _gm_wire_texts_with_embedded_saves(gm_leader_texts)
    assert len(gm_records) == len(full_texts), (
        f"C1: {len(gm_records)} GM-Ledgerrecords, {len(full_texts)} bekannte Wire-Texte -- nicht 1:1 zuordenbar"
    )
    if gm_received is not None:
        assert len(gm_received) == len(full_texts), (
            f"C1: {len(gm_received)} echte GM-Receipts, {len(full_texts)} bekannte Wire-Texte -- nicht 1:1 zuordenbar"
        )
    matched = []
    for i, (rec, text) in enumerate(zip(gm_records, full_texts)):
        expected_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        assert rec.get("content_sha256") == expected_sha, (
            f"C1: GM-Ledgerrecord id={rec.get('id')} content_sha256={rec.get('content_sha256')!r} "
            f"!= sha256(realer Wire-Text)={expected_sha!r} -- Record und tatsaechlich gesendeter Text nicht deckungsgleich"
        )
        assert rec.get("content_chars") == len(text), (
            f"C1: GM-Ledgerrecord id={rec.get('id')} content_chars={rec.get('content_chars')} != len(realer Wire-Text)={len(text)}"
        )
        receipt_check = None
        if gm_received is not None:
            body = gm_received[i].get("body") or {}
            messages = body.get("messages") or []
            actual_current_message = messages[-1].get("content", "") if messages else ""
            receipt_sha = hashlib.sha256(actual_current_message.encode("utf-8")).hexdigest()
            assert rec.get("content_sha256") == receipt_sha, (
                f"C1: GM-Ledgerrecord id={rec.get('id')} content_sha256={rec.get('content_sha256')!r} "
                f"!= sha256(TATSAECHLICHE aktuelle GM-Receipt-Usernachricht)={receipt_sha!r}"
            )
            assert rec.get("content_chars") == len(actual_current_message), (
                f"C1: GM-Ledgerrecord id={rec.get('id')} content_chars={rec.get('content_chars')} "
                f"!= len(TATSAECHLICHE aktuelle GM-Receipt-Usernachricht)={len(actual_current_message)}"
            )
            assert actual_current_message == text, (
                f"C1: echte GM-Receipt-Usernachricht weicht von der Fixture-Rekonstruktion ab (i={i}): "
                f"receipt={actual_current_message!r} fixture={text!r}"
            )
            receipt_check = {"receipt_sha256": receipt_sha, "receipt_chars": len(actual_current_message)}
        matched.append({
            "request_id": rec.get("id"), "content_sha256": rec.get("content_sha256"),
            "content_chars": rec.get("content_chars"), "receipt_check": receipt_check,
        })
    return {"gm_ledger_content_matches": matched, "receipt_based": gm_received is not None}


def _observed_gm_texts_from_receipts(gm_received: list[dict], planned_gm_texts: list[str]) -> list[str]:
    """C1-Nachzug (01_REVIEW_H02.md §3 'gm_texts ... stammen aus der
    geplanten Fixtureliste, nicht einem beobachteten Responsejournal'):
    liest die TATSAECHLICH ueber `recording_http_server` ausgegebenen
    Response-Bodies (`sup.observed_choice_content`, seit dem C1-Nachzug im
    Receipt real erfasst -- nicht mehr nur das, was gescriptet WERDEN
    sollte) und verwendet DIESE Liste als Eingabe fuer
    `_assert_public_sl_prefix_and_reflections_exact`. `planned_gm_texts`
    (`_gm_response_texts`) dient hier NUR noch als Kontrollwert -- die
    Funktion beweist zusaetzlich explizit, dass beobachtet==geplant war
    (kein stiller Drift), ersetzt aber NICHT die Beobachtung als
    Primaerquelle fuer den nachfolgenden B1-Wirevergleich."""
    observed = [sup.observed_choice_content(r) for r in gm_received]
    assert None not in observed, f"C1: mindestens ein GM-Receipt ohne auswertbaren choices[0].message.content: {observed}"
    assert observed == planned_gm_texts, (
        "C1: beobachtete tatsaechlich ausgegebene GM-Antworten weichen von der geplanten Scriptliste ab "
        f"(kein stiller Drift erwartet): observed={observed!r} != planned={planned_gm_texts!r}"
    )
    return observed


# ---------------------------------------------------------------------------
# A) API-Profil -- echte getrennte Start-/Resumeprozesse
# ---------------------------------------------------------------------------

def test_a_api_profile_full_journey_two_processes():
    case = sup.case_dir("A_api_profile_full_journey")
    result = {"profile": "api", "status": "RUNNING"}
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        guard_dir = sup.write_loopback_guard(root / "guard")
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = sup.bootstrap_six_persona_community(
            root, "community-h02api",
        )
        for pk in sup.SIX_PERSONAS:
            sup.make_ready(onboarding_dir, states_dir, run_dir, pk)
        human = sup.register_human_participant(root / "participants", "H02-Operator-Mensch-API")
        human = sup.onboard_human_figure(root / "participants", human.participant_id, onboarding_dir, states_dir, run_dir)
        sup.write_json(case / "human_participant.json", {
            "participant_id": human.participant_id, "kind": human.kind, "display_name": human.display_name,
            "record_refs": [r.__dict__ for r in human.record_refs],
        })
        sup.write_json(case / "before" / "state_hashes.json", sup.hash_tree(states_dir))

        # R3-Nachzug (Review H02 2026-09-28 §4, WORKER-AUFTRAG.md C): positive
        # kontrollierte Testautoritaet ausdruecklich VOR jedem Start setzen
        # (bisher fehlte dieser Aufruf komplett -- Review-Befund:
        # `lab.status.json` zeigte `provider_free: null`, nicht `true`).
        # `write_test_profile` schreibt `provider_free=True`, `_write_status`
        # (core/lab/runner.py) liest diesen Wert bei JEDEM Statuswrite
        # unveraendert vom Datentraeger zurueck -- die Autoritaet bleibt also
        # ueber Start UND Resume erhalten, s. Belege unten nach p1/p2.
        write_test_profile(run_dir, max_usd=5.0)
        status_before_start = lab_runner.read_status(run_dir)
        assert status_before_start is not None and status_before_start.provider_free is True, (
            f"provider_free muss VOR Start bereits True sein: {status_before_start}"
        )

        persona_receipts = case / "persona-receipts.jsonl"
        gm_receipts = case / "gm-receipts.jsonl"
        offer_id = _offer_id_for_first_window("h02api")
        table_id, section_id = "lobby-sniper-tech", "lobby-sniper-tech-section"

        # --- Prozess 1 ("lab start"): Initiativlimit=1 -- NUR sniper stellt
        # sein eigenes Angebot (Leadernominierung=tech). Fenster endet danach
        # kontrolliert (--max-idle-windows 1), KEIN zweiter Request.
        with sup.recording_http_server(
            [(200, {"choices": [{"message": {"content": _leader_nomination_proposal()}}]})],
            receipts_path=persona_receipts, label="persona-start",
            validators={0: sup.make_persona_input_validator("sniper", None, expected_current=sup.load_fixture_save("sniper"))},
        ) as persona_srv_1:
            env1 = {
                "MMO_SIM_PERSONA_API_BASE_URL": persona_srv_1.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTH-H02-NOT-A-REAL-KEY",
                "MMO_SIM_PERSONA_API_MODEL": "synthetic-h02-persona",
                "MMO_SIM_LOBBY_INITIATIVE_LIMIT": "1",
            }
            start_args = [
                "start", "--data-dir", str(root), "--community", "h02api", "--profile", "api",
                "--personas", "sniper,tech", "--max-requests", "64", "--max-seconds", "240",
                "--max-wall-seconds", "300", "--max-usd", "5", "--max-idle-windows", "1",
            ]
            p1 = _run_lab(
                start_args, env_extra=env1, tmp_root=root / "kidtmp1", guard_dir=guard_dir,
                require_schema_dependency=True,
            )
            _log_invocation(case, "start", start_args, env1, p1)
            assert p1.returncode == 0, p1.stdout + p1.stderr
            assert "schlaegt eine Runde vor" in p1.stdout, p1.stdout
            # A10: genau EIN Request (sniper) -- nicht ausgewaehlte Personas
            # wurden in Phase 1 nicht kontaktiert.
            assert len(persona_srv_1.calls) == 1, "genau EIN Request (sniper) in Phase 1 erwartet"

        status_after_start = lab_runner.read_status(run_dir)
        assert status_after_start is not None and status_after_start.provider_free is True, (
            f"R3: provider_free muss NACH 'lab start' weiterhin True sein: {status_after_start}"
        )
        offers_after_p1 = [r for r in lobby_service.read_offer_log(run_dir) if r.get("type") == "offer"]
        assert len(offers_after_p1) == 1
        assert offers_after_p1[0]["offer_id"] == offer_id, (offers_after_p1[0]["offer_id"], offer_id)
        assert offers_after_p1[0].get("leader") == "tech", "andere Leaderrolle (tech) muss im Angebot stehen"
        assert offers_after_p1[0].get("proposed_by") == "sniper"

        # --- Prozess 2 ("lab resume"): NEUER Prozess, uebernimmt Angebot/IDs.
        # G0/G1 Import, G2-G4 echte Spielantworten, Abschluss, Reflexionen,
        # danach im SELBEN Prozess ein neues freiwilliges Fenster mit neuen
        # pause-Antworten (kein zweiter Tisch aus altem Consent).
        seq = _persona_response_sequence_for_full_journey(offer_id)
        gm_texts = _gm_response_texts(table_id, section_id)
        # B2-Nacharbeit: echte Validatoren (statt leerem `validators={}`) --
        # unerwarteter Input (falsche Persona/Praefix bzw. fehlender
        # Leadertext) wird jetzt VOR der gescripteten Antwort mit HTTP599
        # abgelehnt, s. `_persona_validators_for_full_journey`/
        # `_gm_validators_for_full_journey`-Docstrings.
        with sup.recording_http_server(
            [(200, {"choices": [{"message": {"content": t}}], "usage": {}}) for t in seq],
            receipts_path=persona_receipts, label="persona-resume",
            validators=_persona_validators_for_full_journey(offer_id, table_id, section_id),
        ) as persona_srv_2, sup.recording_http_server(
            [(200, {"choices": [{"message": {"content": t}}], "usage": {}}) for t in gm_texts],
            receipts_path=gm_receipts, label="gm-resume",
            validators=_gm_validators_for_full_journey(seq),
        ) as gm_srv_2:
            env2 = {
                "MMO_SIM_PERSONA_API_BASE_URL": persona_srv_2.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTH-H02-NOT-A-REAL-KEY",
                "MMO_SIM_PERSONA_API_MODEL": "synthetic-h02-persona-b",
                "OPENWEBUI_URL": gm_srv_2.base_url, "OPENWEBUI_API_KEY": "SYNTH-H02-NOT-A-REAL-KEY",
                "MMO_SIM_GM_OUTPUT_LIMIT_TOKENS": "4096",
                "MMO_SIM_LOBBY_INITIATIVE_LIMIT": "8",
            }
            resume_args = [
                "resume", "--data-dir", str(root), "--community", "h02api", "--profile", "api",
                "--personas", "sniper,tech", "--max-requests", "64", "--max-seconds", "240",
                "--max-wall-seconds", "300", "--max-usd", "5", "--max-idle-windows", "1",
            ]
            p2 = _run_lab(
                resume_args, env_extra=env2, timeout=90, tmp_root=root / "kidtmp2", guard_dir=guard_dir,
                require_schema_dependency=True,
            )
            _log_invocation(case, "resume", resume_args, env2, p2)
            assert p2.returncode == 0, p2.stdout + p2.stderr
            assert "schlaegt eine Runde vor" not in p2.stdout, (
                f"sniper haette sein bereits offenes Angebot NICHT erneut stellen duerfen: {p2.stdout}"
            )
            assert "antwortet auf Angebot" in p2.stdout and "accept" in p2.stdout, p2.stdout
            assert "Lobby-Tisch abgeschlossen" in p2.stdout, p2.stdout
            assert len(persona_srv_2.calls) == 12, f"12 echte Persona-Requests erwartet, {len(persona_srv_2.calls)} erhalten"
            assert len(gm_srv_2.calls) == 5, f"G0-G4 = 5 echte GM-Requests erwartet, {len(gm_srv_2.calls)} erhalten"
            for rec in gm_srv_2.received:
                assert rec["body"].get("max_tokens") == 4096, f"GM-Body ohne validen max_tokens: {rec['body']}"
            assert persona_srv_2.validation_failures == [], (
                f"R3: Fake-Persona-Empfaenger meldet Inputvalidierungsfehler: {persona_srv_2.validation_failures}"
            )
            assert gm_srv_2.validation_failures == [], (
                f"R2: GM-Empfaenger meldet Inputvalidierungsfehler: {gm_srv_2.validation_failures}"
            )

            # R2-Nachzug (Review H02 2026-09-28 §3): echte Inhaltspruefung
            # statt Labelzaehlung -- jeder der 12 Calls wird ueber die
            # woertliche `render_for_prompt`-Kopfzeile einer Persona
            # zugeordnet (kein Raten aus der Aufrufreihenfolge).
            classified = []
            for rec in persona_srv_2.received:
                msgs = rec["body"].get("messages") or []
                system_text = msgs[0].get("content", "") if msgs else ""
                user_text = msgs[1].get("content", "") if len(msgs) > 1 else ""
                pk = _identify_persona(system_text, user_text)
                assert pk is not None, f"Persona im Wire nicht identifizierbar: {rec['body']}"
                classified.append({"pk": pk, "system": system_text, "user": user_text, "full": f"{system_text}\n{user_text}"})
            sup.write_json(case / "classified-persona-wires.json", classified)

            reflection_entries = [c for c in classified if c["system"].strip() == "PRIVATE_REFLECTION_SENTINEL"]
            assert len(reflection_entries) == 2, f"genau 2 Reflexionsaufrufe erwartet: {len(reflection_entries)}"
            reflections_full = {c["pk"]: c["full"] for c in reflection_entries}
            assert set(reflections_full) == {"sniper", "tech"}, reflections_full.keys()
            # C1-Nachzug: B1-Wirevergleich aus dem BEOBACHTETEN GM-Ausgangsjournal
            # (tatsaechlich ausgegebene Response-Bodies), nicht mehr direkt aus
            # der geplanten `_gm_response_texts`-Fixtureliste.
            observed_gm_texts = _observed_gm_texts_from_receipts(gm_srv_2.received, gm_texts)
            sup.write_json(case / "observed-gm-response-journal.json", observed_gm_texts)
            _assert_public_sl_prefix_and_reflections_exact(classified, observed_gm_texts, table_id)

            # R1-Regressionsnachweis (permanenter Test, ergaenzt den externen
            # `tools/review_reflection_roundtrip.py`-Befund): die letzten 2
            # Calls (neues Fenster) muessen die EIGENE gerade committete
            # Reflexion UND den neu veroeffentlichten eigenen Current
            # (unterscheidbarer Endmarker) im eigenen Kontext tragen --
            # fremde Reflexion NICHT (A07 Privattrennung).
            pause_entries = classified[-2:]
            assert {c["pk"] for c in pause_entries} == {"sniper", "tech"}, pause_entries
            own_reflection_text = {"sniper": seq[8], "tech": seq[9]}
            for c in pause_entries:
                pk, other_pk = c["pk"], ("tech" if c["pk"] == "sniper" else "sniper")
                assert own_reflection_text[pk] in c["system"], (
                    f"R1: eigene Reflexion von {pk} fehlt im neuen Fenster-Kontext: {c['system'][:200]!r}"
                )
                assert own_reflection_text[other_pk] not in c["system"], (
                    f"R1/A07: fremde Reflexion von {other_pk} leckte in {pk}s eigenen Kontext"
                )
                assert f"H02-VOLLREISE-ENDSAVE-{pk}-{table_id}-{section_id}" in c["system"], (
                    f"A09: neuer eigener Current (Endmarker) fehlt im neuen Fenster-Kontext von {pk}"
                )
                # A09/R2 (Review H02 2026-09-28 §3, M2-Mutationsprobe "+7
                # Runden"): die Kopfzeile aus `render_for_prompt` traegt
                # `rounds_played` woertlich -- GENAU eine verbuchte Runde,
                # keine `>=`-Naeherung.
                assert f"{pk} spielt" in c["system"] and "1 Runde(n) gespielt" in c["system"], (
                    f"A09: genau +1 Runde erwartet, Kopfzeile zeigt etwas anderes: {c['system'][:120]!r}"
                )

        status_after_resume = lab_runner.read_status(run_dir)
        assert status_after_resume is not None and status_after_resume.provider_free is True, (
            f"R3: provider_free muss NACH 'lab resume' weiterhin True sein: {status_after_resume}"
        )
        offers_after_p2 = [r for r in lobby_service.read_offer_log(run_dir) if r.get("type") == "offer"]
        assert len(offers_after_p2) == 1, "kein zweites/doppeltes Angebot durch 'lab resume' entstanden"
        summary = _assert_full_journey_final_state(case, run_dir, table_id, seq)

        # R2-Nachzug: unterscheidbare GM-End-Saves erreichen tatsaechlich den
        # veroeffentlichten eigenen Current (Aenderung stammt AUSSCHLIESSLICH
        # aus der synthetischen GM-Antwort, s. `_distinguishable_final_saves`).
        ps_store = PersonaStateStore(schema_path=schema_path)
        for pk in SELECTED:
            current = core_store.load_current_save_or_raise(run_dir, pk, ps_store, states_dir=states_dir)
            assert current.get("_h02_end_marker") == f"H02-VOLLREISE-ENDSAVE-{pk}-{table_id}-{section_id}", (
                f"unterscheidbarer Endmarker fehlt im veroeffentlichten Current von {pk}: {current}"
            )
            assert current.get("save_id") != sup.load_fixture_save(pk)["save_id"], (
                f"Current von {pk} ist bytegleich zur Start-Fixture geblieben (R2-Befund nicht behoben)"
            )

        status = lab_runner.read_status(run_dir)
        # R4-Nachzug (Review H02 2026-09-28 §5): EXAKTE Zaehlung (13
        # Persona-Entscheidungen [1 Initiative + 12] + 5 GM-Entscheidungen =
        # 18) statt der zu schwachen `>=`-Untergrenze -- fuer diese feste
        # 13-Persona-/5-GM-Fixture ist die Sollzahl bekannt und belegbar.
        assert status.turns_used == 18, f"R4: exakt 18 verbuchte Entscheidungen erwartet, {status.turns_used} erhalten"
        assert status.max_usd == 5

        # G10 (B2-Nacharbeit + C1-Nachzug r1/r2): requestweise Ledger-
        # Reconciliation inkl. table_id/section_id/turn_idx-Eindeutigkeit,
        # ungefilterter Gesamtmenge==18 UND 18 einzelnen Zuordnungen gegen
        # die bereits vorhandenen echten HTTP-Receipts (persona_srv_1 = die
        # eine Initiative aus Phase1, persona_srv_2 = die 12 Resume-Calls,
        # BEIDE schreiben in dieselbe `persona_receipts`-Datei in genau
        # dieser chronologischen Reihenfolge -- s. `_assert_request_ledger_
        # reconciles`-Docstring).
        persona_journal = persona_srv_1.received + persona_srv_2.received
        ledger_summary = _assert_request_ledger_reconciles(
            run_dir, table_id, section_id, "h02api",
            persona_journal=persona_journal, gm_journal=gm_srv_2.received,
        )
        sup.write_json(case / "request-ledger-reconciliation.json", ledger_summary)
        # C1-Nachzug r1: GM-Ledgerrecords per Content-Hash GEGEN DEN ECHTEN
        # GM-RECEIPT (gm_srv_2.received, TATSAECHLICH empfangene Bodies)
        # gejoint, zusaetzlich zur Fixture-Rekonstruktion (beide muessen
        # uebereinstimmen, s. Docstring).
        gm_content_join = _assert_gm_ledger_content_matches_observed(
            run_dir, table_id, _gm_leader_texts_for_full_journey(seq), gm_received=gm_srv_2.received,
        )
        sup.write_json(case / "gm-ledger-content-join.json", gm_content_join)

        # A10: private Zustaende der nicht ausgewaehlten Personas + des
        # Menschen bleiben bytegleich (0 Persona-/Reflexions-Receipts fuer sie).
        after_hashes = sup.hash_tree(states_dir)
        sup.write_json(case / "after" / "state_hashes.json", after_hashes)
        before_hashes = json.loads((case / "before" / "state_hashes.json").read_text(encoding="utf-8"))
        for pk in NOT_SELECTED + (human.participant_id,):
            for rel, h in before_hashes.items():
                if f"{pk}." in rel or f"/{pk}/" in rel or rel.startswith(pk):
                    assert after_hashes.get(rel) == h, f"unveraendert erwarteter Zustand von {pk} hat sich geaendert: {rel}"

        result.update({
            "status": "PASS", "table": summary, "offer_id": offer_id,
            "persona_requests": len(persona_srv_2.calls) + 1, "gm_requests": 5,
            "turns_used_final": status.turns_used, "max_usd": status.max_usd,
        })
    sup.write_json(case / "result.json", result)
    # R2-Nachzug (Review H02 2026-09-28 §3: "assertions.json zaehlt bzw.
    # behauptet Abnahmepunkte, ersetzt aber keine inhaltlichen Assertions"):
    # jeder Eintrag verweist auf die tatsaechlich oben ausgefuehrte(n)
    # Python-`assert`-Anweisung(en) UND die konkrete Rohdatei -- KEIN reines
    # Label mehr. Diese Datei wird erst NACH allen `assert`s dieser Funktion
    # geschrieben; ein Fehlschlag oben verhindert JEDEN dieser Eintraege
    # (kein Nachschreiben eines PASS trotz gescheitertem Lauf).
    sup.write_json(case / "assertions.json", {"claims": [
        {"id": "A02", "claim": "getrennte Start-/Resumeprozesse (2 echte Subprozesse)",
         "verified_by": "p1.returncode==0 UND p2.returncode==0, zwei getrennte _run_lab-Aufrufe", "evidence": "invocations.json"},
        {"id": "A03", "claim": "tech (nicht sniper) wird per sniper-Initiative nominierter Leader",
         "verified_by": "offers_after_p1[0]['leader']=='tech' UND table.leader=='tech'", "evidence": "final_table_state.json"},
        {"id": "A05/A06", "claim": "G0-G4 vollstaendig, lange unterscheidbare Endmarker, korrekter SL-Praefix pro Entscheidung",
         "verified_by": "_assert_public_sl_prefix_and_reflections_exact (dekodierter Zeichen-fuer-Zeichen-Vergleich an allen 9 Tischentscheidungen inkl. beider voller G4-Saveblöcke)",
         "evidence": "classified-persona-wires.json, gm-receipts.jsonl"},
        {"id": "A07", "claim": "eigene/fremde Privattrennung: fremde Reflexion leckt nicht in eigenen Kontext",
         "verified_by": "own_reflection_text[other_pk] not in c['system'] fuer beide Personas", "evidence": "classified-persona-wires.json"},
        {"id": "A08", "claim": "nur Leader sendet an SL; origin_persona_key korrekt; keine automatische Gastaggregation",
         "verified_by": "_assert_sl_log_leader_only_and_origin (exakter Textvergleich + Negativpruefung guest_raw_suggestions)",
         "evidence": "final_table_state.json#sl_log"},
        {"id": "A09", "claim": "unterscheidbare GM-End-Saves erreichen Current; eigene Reflexion (R1) UND neuer Current im naechsten Fenster",
         "verified_by": "current['_h02_end_marker']==erwartet UND save_id!=Start-Fixture; pause_entries own_reflection_text-Check",
         "evidence": "classified-persona-wires.json"},
        {"id": "A10", "claim": "nicht ausgewaehlte Personas + Mensch bytegleich",
         "verified_by": "after_hashes[rel]==before_hashes[rel] fuer alle NOT_SELECTED+human", "evidence": "before/after state_hashes.json"},
        {"id": "A11/A12", "claim": "max_usd=5, max_tokens=4096 in JEDEM GM-Body, provider_free vor/nach True",
         "verified_by": "status.max_usd==5, alle gm_srv_2.received[].body.max_tokens==4096, provider_free-Checks vor/nach/resume",
         "evidence": "gm-receipts.jsonl"},
        {"id": "R4-turns", "claim": "exakt 18 verbuchte Entscheidungen (13 Persona + 5 GM), nicht nur >=18",
         "verified_by": "status.turns_used==18", "evidence": "result.json"},
        {"id": "R3-authority", "claim": "keine Inputvalidierungsfehler am eigenen Empfaenger (Persona UND GM)",
         "verified_by": "persona_srv_2.validation_failures==[] UND gm_srv_2.validation_failures==[]", "evidence": "persona-receipts.jsonl, gm-receipts.jsonl"},
        {"id": "G09", "claim": "echte HTTP-Validatoren aktiv (Persona-Identitaet+Praefixlaenge, GM-Leadertext), kein Blind-Pop",
         "verified_by": "_persona_validators_for_full_journey/_gm_validators_for_full_journey verdrahtet, validation_failures==[]", "evidence": "persona-receipts.jsonl, gm-receipts.jsonl"},
        {"id": "G10", "claim": "13 Persona + 5 GM = 18 requestweise gegen vorhandenes request_ledger zugeordnet (Rollen+Teilnehmer+state=accounted)",
         "verified_by": "_assert_request_ledger_reconciles(run_dir, table_id)", "evidence": "request-ledger-reconciliation.json"},
    ]})


# ---------------------------------------------------------------------------
# B) Hybrid-Profil -- vollstaendig in EINEM neuen 'lab start' (04 §1: "Kein
# kuenstlicher Neustart erforderlich, um das neue Nachabschlussfenster
# sichtbar zu machen").
# ---------------------------------------------------------------------------

def test_b_hybrid_profile_full_journey_single_process():
    case = sup.case_dir("B_hybrid_profile_full_journey")
    result = {"profile": "hybrid", "status": "RUNNING"}
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        guard_dir = sup.write_loopback_guard(root / "guard")
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = sup.bootstrap_six_persona_community(
            root, "community-h02hybrid",
        )
        for pk in sup.SIX_PERSONAS:
            sup.make_ready(onboarding_dir, states_dir, run_dir, pk)
        human = sup.register_human_participant(root / "participants", "H02-Operator-Mensch-Hybrid")
        human = sup.onboard_human_figure(root / "participants", human.participant_id, onboarding_dir, states_dir, run_dir)
        sup.write_json(case / "human_participant.json", {
            "participant_id": human.participant_id, "kind": human.kind, "display_name": human.display_name,
            "record_refs": [r.__dict__ for r in human.record_refs],
        })
        sup.write_json(case / "before" / "state_hashes.json", sup.hash_tree(states_dir))

        # R3-Nachzug (wie Test A): positive Testautoritaet VOR Start setzen.
        write_test_profile(run_dir, max_usd=5.0)
        status_before_start = lab_runner.read_status(run_dir)
        assert status_before_start is not None and status_before_start.provider_free is True, (
            f"provider_free muss VOR Start bereits True sein: {status_before_start}"
        )

        offer_id = _offer_id_for_first_window("h02hybrid")
        table_id, section_id = "lobby-sniper-tech", "lobby-sniper-tech-section"
        seq = _persona_response_sequence_for_full_journey(offer_id)
        gm_texts = _gm_response_texts(table_id, section_id)
        cli_capture = case / "cli-receipts.jsonl"
        # R3-Nachzug (Review H02 2026-09-28 §4): jedes Queue-Item traegt jetzt
        # `expect_all` -- die Fake-CLI selbst prueft VOR dem Antworten den
        # eigenen Persona-Marker im tatsaechlich empfangenen STDIN (s.
        # `_QUEUED_FAKE_CLI_TEMPLATE`). Persona je Position aus der bereits
        # bekannten API-Ground-Truth abgeleitet (idx0=tech-Consent, idx1=tech
        # G0, idx2=sniper G1, idx3=tech G2, idx4=sniper guest_poll, idx5=tech
        # G3, idx6=sniper guest_poll, idx7=tech G4, idx8=sniper-Reflexion,
        # idx9=tech-Reflexion, idx10=sniper-Pause, idx11=tech-Pause); Position
        # 0 (sniper-Initiative) hat keinen eigenen Marker-Zwang, da die
        # Initiative-Textform sich vom regulaeren Entscheidungswire
        # unterscheidet (`Antworte AUSSCHLIESSLICH mit EINEM JSON-Objekt`).
        # queue[i] (i=1..12) transportiert seq[i-1]; Persona-Reihenfolge
        # empirisch aus der API-Ground-Truth (`checkpoint-a`-Lauf gegen
        # `persona_srv_2.received`, s. Kommentar oben) auf `seq`-Indizes
        # abgebildet: seq[0]=tech(Consent), [1]=tech(G0), [2]=sniper(G1),
        # [3]=tech(G2), [4]=sniper(poll), [5]=tech(G3), [6]=sniper(poll),
        # [7]=tech(G4), [8]=sniper(Reflexion), [9]=tech(Reflexion),
        # [10]=sniper(Pause), [11]=tech(Pause).
        # B2-Nacharbeit (02_AUFTRAG_BELEGSCHLUSS.md, 07_...md §3): zusaetzlich
        # zum bestehenden `expect_all`-Personamarker prueft die Fake-CLI JETZT
        # auch die tatsaechliche oeffentliche SL-Praefixlaenge VOR jeder
        # Antwort (`expect_sl_log_len`, s. `_QUEUED_FAKE_CLI_TEMPLATE`) --
        # dieselben Sollwerte wie `_assert_public_sl_prefix_and_reflections_exact`/
        # `_persona_validators_for_full_journey`, kein Antwort-Poppen mehr nach
        # reiner Position/Substring. Index 0 (Initiative) und 10/11 (neues
        # Fenster) haben KEIN `sl_log` (andere `table_view`-Struktur, s.
        # `lobby_flow.py`) -- dort bleibt es beim reinen Personamarker.
        #
        # C2-Nachzug (01_REVIEW_H02.md §4 Probe 4/5, 02_AUFTRAG_RESTPFLICHTEN.md
        # C2): VORHER hatte queue[0] (sniper-Initiative) UEBERHAUPT keinen
        # `expect_all`-Zwang (Review-Befund: 'Wirklich ausfuehrbare Fake-CLI
        # ohne jede Persona im Initiativeinput: rc0 Erfolg') -- `ctx["system"]
        # = own_ctx` wird aber laut `lobby_flow.py:520-524` AUCH fuer den
        # freien Initiativpfad gesetzt, der Marker ist also real transportiert
        # und kann/muss geprueft werden. Und queue[1] (tech-Consent) pruefte
        # NUR den Personamarker, nicht die tatsaechlich woertlich mitgesendete
        # `offer_id` (Review-Befund: 'Zustimmung mit blossem Persona-
        # Substring: rc0 Erfolg') -- `decision_contract_instruction` bettet
        # `offer_id=<id>`/`"offer_id": "<id>"` woertlich in denselben STDIN
        # ein (s. `make_persona_input_validator`-Docstring), jetzt zusaetzlich
        # in `expect_all` gefordert.
        # C2-Nachzug r1 (01_REVIEW_H02.md §3, 02_AUFTRAG_C_ABSCHLUSS.md C2):
        # `expect_all` prueft jetzt die VOLLE Figur-Kopfzeile
        # (`own_figure_marker`, Name+Callsign) statt nur `"{pk} spielt"`, UND
        # den vollstaendigen Current-JSON-Block (`own_current_full_marker`)
        # -- fuer queue[11]/queue[12] (seq[10]/seq[11], neues Fenster NACH
        # Abschluss) ist das der NEU veroeffentlichte Endsave, sonst die
        # Start-Fixture (analog `_persona_validators_for_full_journey`).
        final_saves_cli = _distinguishable_final_saves(table_id, section_id)

        def _expect_current_for_queue_idx(pk: str, queue_idx: int) -> str:
            current = final_saves_cli[pk] if queue_idx in (11, 12) else sup.load_fixture_save(pk)
            return sup.own_current_full_marker(current)

        expect_by_idx = {
            i: [sup.own_figure_marker(_SEQ_PK[i - 1]), _expect_current_for_queue_idx(_SEQ_PK[i - 1], i)]
            for i in range(1, 13)
        }
        expect_by_idx[1] = expect_by_idx[1] + [f"offer_id={offer_id}"]
        initiative_expect_all = [sup.own_figure_marker("sniper"), _expect_current_for_queue_idx("sniper", 0)]
        sl_log_len_by_queue_idx = {}
        for offset, length in enumerate(_TABLE_DECISION_PREFIX_LENGTHS):
            sl_log_len_by_queue_idx[offset + 2] = length  # queue[i] transportiert seq[i-1]; seq[1..9]->queue[2..10]
        queue = [{"result": _leader_nomination_proposal(), "expect_all": initiative_expect_all}]  # 0: sniper Initiative
        for i, t in enumerate(seq, start=1):
            queue.append({
                "result": t, "expect_all": expect_by_idx.get(i, []),
                "expect_sl_log_len": sl_log_len_by_queue_idx.get(i),
            })
        fake_cli = sup.write_queued_fake_cli(root, capture_path=cli_capture, queue=queue)
        isolated_workdir = root / "cli_workdir"
        isolated_workdir.mkdir(parents=True, exist_ok=True)

        gm_receipts = case / "gm-receipts.jsonl"
        with sup.recording_http_server(
            [(200, {"choices": [{"message": {"content": t}}], "usage": {}}) for t in gm_texts],
            receipts_path=gm_receipts, label="gm-hybrid",
            validators=_gm_validators_for_full_journey(seq),
        ) as gm_srv:
            env = {
                "OPENWEBUI_URL": gm_srv.base_url, "OPENWEBUI_API_KEY": "SYNTH-H02-NOT-A-REAL-KEY",
                "MMO_SIM_GM_OUTPUT_LIMIT_TOKENS": "4096",
                "MMO_SIM_LOBBY_INITIATIVE_LIMIT": "8",
                "MMO_SIM_PERSONA_CLI": str(fake_cli),
                "MMO_SIM_PERSONA_ISOLATED_WORKDIR": str(isolated_workdir),
                "MMO_SIM_PERSONA_ISOLATION_FLAGS": "--permission-mode=plan,--safe-mode",
            }
            start_args = [
                "start", "--data-dir", str(root), "--community", "h02hybrid", "--profile", "hybrid",
                "--personas", "sniper,tech", "--max-requests", "64", "--max-seconds", "240",
                "--max-wall-seconds", "300", "--max-usd", "5", "--max-idle-windows", "1",
            ]
            p = _run_lab(
                start_args, env_extra=env, timeout=120, tmp_root=root / "kidtmp", guard_dir=guard_dir,
                require_schema_dependency=True,
            )
            _log_invocation(case, "start", start_args, env, p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert "schlaegt eine Runde vor" in p.stdout, p.stdout
            assert "antwortet auf Angebot" in p.stdout and "accept" in p.stdout, p.stdout
            assert "Lobby-Tisch abgeschlossen" in p.stdout, p.stdout
            assert len(gm_srv.calls) == 5, f"G0-G4 = 5 echte GM-Requests erwartet, {len(gm_srv.calls)} erhalten"
            for rec in gm_srv.received:
                assert rec["body"].get("max_tokens") == 4096, f"GM-Body ohne validen max_tokens: {rec['body']}"
            assert gm_srv.validation_failures == [], f"R2: GM-Empfaenger meldet Inputvalidierungsfehler: {gm_srv.validation_failures}"

        status_after_start = lab_runner.read_status(run_dir)
        assert status_after_start is not None and status_after_start.provider_free is True, (
            f"R3: provider_free muss NACH Hybrid-Ende weiterhin True sein: {status_after_start}"
        )

        assert cli_capture.exists(), "Fake-CLI haette real (echter Subprozess) aufgerufen werden muessen"
        cli_calls = [json.loads(line) for line in cli_capture.read_text(encoding="utf-8").splitlines() if line.strip()]
        assert len(cli_calls) == 13, f"13 echte Fake-CLI-Entscheidungsaufrufe erwartet, {len(cli_calls)} erhalten"
        for rec in cli_calls:
            assert "--permission-mode=plan" in rec["argv"] and "--safe-mode" in rec["argv"]
            assert "[SYSTEM]" in rec["stdin"] and "[USER]" in rec["stdin"]
            assert rec.get("cwd") == str(isolated_workdir), f"R4: cwd im CLI-Receipt fehlt/weicht ab: {rec.get('cwd')!r}"
        remaining = sup.queue_remaining(root / f"fake_cli_queue_{cli_capture.stem}.json")
        assert remaining == [], f"Fake-CLI-Queue haette vollstaendig verbraucht sein muessen: {remaining}"
        fail_log = cli_capture.parent / f"{cli_capture.stem}.validation-failures.jsonl"
        assert not fail_log.exists() or fail_log.read_text(encoding="utf-8").strip() == "", (
            f"R3: Fake-CLI meldet Inputvalidierungsfehler: {fail_log.read_text(encoding='utf-8')}"
        )

        # C1-Nachzug r1 (01_REVIEW_H02.md §2 Bytebefund '224 tatsaechliche
        # Bytes, journalisiert/hasht aber 223 Bytes ohne LF'): das
        # Response-Journal der Fake-CLI muss den TATSAECHLICH per `print()`
        # geschriebenen Byte-Strom (inkl. LF) korrekt getrennt von der
        # normalisierten Textform benennen. Eigene Rekonstruktion aus dem
        # journalisierten `stdout`-Feld (`+ "\n"`, exakt das, was `print()`
        # anhaengt) muss mit dem journalisierten `stdout_raw_sha256`/
        # `stdout_raw_bytes_len` uebereinstimmen -- UND `stdout_raw_bytes_len`
        # muss um genau 1 (das LF) groesser sein als `stdout_chars`.
        response_log = sup.response_log_path_for(cli_capture)
        assert response_log.exists(), "C1: CLI-Antwortjournal (responses.jsonl) fehlt"
        response_entries = sup.read_jsonl(response_log)
        assert len(response_entries) == 13, f"C1: 13 CLI-Antwortjournaleintraege erwartet, {len(response_entries)} erhalten"
        for rec in response_entries:
            assert rec["rc"] == 0, f"C1: unerwarteter rc!=0 im Antwortjournal: {rec}"
            raw_bytes = (rec["stdout"] + "\n").encode("utf-8")
            assert rec["stdout_raw_bytes_len"] == len(raw_bytes), (
                f"C1: stdout_raw_bytes_len={rec['stdout_raw_bytes_len']} != tatsaechliche Byteslaenge {len(raw_bytes)} "
                f"(223->224-Byte-Fix nicht wirksam)"
            )
            assert rec["stdout_raw_bytes_len"] == rec["stdout_chars"] + 1, (
                f"C1: stdout_raw_bytes_len={rec['stdout_raw_bytes_len']} muss stdout_chars+1 (LF) sein, "
                f"stdout_chars={rec['stdout_chars']}"
            )
            assert rec["stdout_raw_sha256"] == hashlib.sha256(raw_bytes).hexdigest(), (
                f"C1: stdout_raw_sha256 stimmt nicht mit sha256(stdout+LF) ueberein: {rec}"
            )
            assert rec["stdout_sha256"] == hashlib.sha256(rec["stdout"].encode("utf-8")).hexdigest(), (
                f"C1: stdout_sha256 (normalisiert, ohne LF) stimmt nicht mit sha256(stdout) ueberein: {rec}"
            )
            assert rec["pid"] > 0, f"C1: kein echter Fake-CLI-PID im Antwortjournal: {rec}"
        sup.write_json(case / "cli-response-journal-lf-check.json", {
            "entries": len(response_entries), "all_raw_bytes_len_correct": True,
        })

        # R2-Nachzug: dieselbe Persona-/Reflexions-/Fenster-Inhaltspruefung
        # wie Test A, nur ueber CLI-STDIN statt HTTP-JSON-Body extrahiert.
        # cli_calls[0] ist die sniper-Initiative (Community-Vorschlag, kein
        # [SYSTEM]-Block, s. Fake-CLI-Template), cli_calls[1:] entsprechen
        # 1:1 der `seq`-Reihenfolge (Index 0..11 dort == cli_calls[1..12]).
        classified = []
        for rec in cli_calls[1:]:
            stdin_text = rec["stdin"]
            if stdin_text.startswith("[SYSTEM]\n"):
                rest = stdin_text[len("[SYSTEM]\n"):]
                system_text, _, user_text = rest.partition("\n\n[USER]\n")
            else:
                system_text, user_text = "", stdin_text
            pk = _identify_persona(system_text, user_text)
            assert pk is not None, f"Persona im CLI-STDIN nicht identifizierbar: {stdin_text[:200]!r}"
            classified.append({"pk": pk, "system": system_text, "user": user_text, "full": f"{system_text}\n{user_text}"})
        sup.write_json(case / "classified-persona-wires.json", classified)

        reflection_entries = [c for c in classified if c["system"].strip() == "PRIVATE_REFLECTION_SENTINEL"]
        assert len(reflection_entries) == 2, f"genau 2 Reflexionsaufrufe erwartet: {len(reflection_entries)}"
        reflections_full = {c["pk"]: c["full"] for c in reflection_entries}
        assert set(reflections_full) == {"sniper", "tech"}, reflections_full.keys()
        # C1-Nachzug (analog test_a): beobachtetes GM-Ausgangsjournal statt
        # geplanter Fixtureliste.
        observed_gm_texts = _observed_gm_texts_from_receipts(gm_srv.received, gm_texts)
        sup.write_json(case / "observed-gm-response-journal.json", observed_gm_texts)
        _assert_public_sl_prefix_and_reflections_exact(classified, observed_gm_texts, table_id)

        pause_entries = classified[-2:]
        assert {c["pk"] for c in pause_entries} == {"sniper", "tech"}, pause_entries
        own_reflection_text = {"sniper": seq[8], "tech": seq[9]}
        for c in pause_entries:
            pk, other_pk = c["pk"], ("tech" if c["pk"] == "sniper" else "sniper")
            assert own_reflection_text[pk] in c["system"], (
                f"R1: eigene Reflexion von {pk} fehlt im neuen Fenster-Kontext (Hybrid): {c['system'][:200]!r}"
            )
            assert own_reflection_text[other_pk] not in c["system"], (
                f"R1/A07: fremde Reflexion von {other_pk} leckte in {pk}s eigenen Kontext (Hybrid)"
            )
            assert f"H02-VOLLREISE-ENDSAVE-{pk}-{table_id}-{section_id}" in c["system"], (
                f"A09: neuer eigener Current (Endmarker) fehlt im neuen Fenster-Kontext von {pk} (Hybrid)"
            )
            # A09/R2 (End-Critic-Nacharbeit 2026-09-28, Befund 1: M2-Mutationsklasse
            # "+7 Runden" blieb im Hybrid-Profil unentdeckt, weil hier -- anders als
            # in test_a -- keine Rundenzahl aus der Kopfzeile geprueft wurde). Eigene
            # Sonde bestaetigte den gesunden Wert vorab als exakt "1 Runde(n) gespielt".
            assert f"{pk} spielt" in c["system"] and "1 Runde(n) gespielt" in c["system"], (
                f"A09: genau +1 Runde erwartet (Hybrid), Kopfzeile zeigt etwas anderes: {c['system'][:120]!r}"
            )

        offers = [r for r in lobby_service.read_offer_log(run_dir) if r.get("type") == "offer"]
        assert len(offers) == 1
        summary = _assert_full_journey_final_state(case, run_dir, table_id, seq)

        ps_store = PersonaStateStore(schema_path=schema_path)
        for pk in SELECTED:
            current = core_store.load_current_save_or_raise(run_dir, pk, ps_store, states_dir=states_dir)
            assert current.get("_h02_end_marker") == f"H02-VOLLREISE-ENDSAVE-{pk}-{table_id}-{section_id}", (
                f"unterscheidbarer Endmarker fehlt im veroeffentlichten Current von {pk} (Hybrid): {current}"
            )
            assert current.get("save_id") != sup.load_fixture_save(pk)["save_id"], (
                f"Current von {pk} ist bytegleich zur Start-Fixture geblieben (Hybrid, R2-Befund nicht behoben)"
            )

        status = lab_runner.read_status(run_dir)
        assert status.max_usd == 5, "Hybrid muss die explizite API-Dollargrenze (GM-Rolle) erhalten"
        # R4-Nachzug (End-Critic-Nacharbeit 2026-09-28, Befund 1): exakte Zaehlung
        # auch im Hybrid-Profil, analog test_a -- eigene Sonde bestaetigte den
        # gesunden Wert vorab als exakt 18 (identisch zum API-Profil).
        assert status.turns_used == 18, f"R4: exakt 18 verbuchte Entscheidungen erwartet (Hybrid), {status.turns_used} erhalten"

        # G10 (B2-Nacharbeit + C1-Nachzug r1/r2): requestweise Ledger-
        # Reconciliation inkl. table_id/section_id/turn_idx, analog test_a --
        # hier transportiert die Fake-CLI die 13 Persona-Entscheidungen, das
        # Journal kombiniert deshalb je Position den echten `cli_calls[i]`
        # (argv/stdin/cwd/pid) mit dem zugehoerigen echten Antwortjournal-
        # eintrag `response_entries[i]` (rc/stdout/stdout_raw_sha256) --
        # dieselben bereits oben (C1-LF-Check) verifizierten Rohbelege,
        # keine zweite Buchhaltung.
        persona_journal = [
            {**cli_calls[i], "response": response_entries[i]} for i in range(len(cli_calls))
        ]
        ledger_summary = _assert_request_ledger_reconciles(
            run_dir, table_id, section_id, "h02hybrid",
            persona_journal=persona_journal, gm_journal=gm_srv.received,
        )
        sup.write_json(case / "request-ledger-reconciliation.json", ledger_summary)
        # C1-Nachzug r1 (analog test_a): GM-Ledgerrecords per Content-Hash
        # GEGEN DEN ECHTEN GM-RECEIPT (gm_srv.received), zusaetzlich zur
        # Fixture-Rekonstruktion.
        gm_content_join = _assert_gm_ledger_content_matches_observed(
            run_dir, table_id, _gm_leader_texts_for_full_journey(seq), gm_received=gm_srv.received,
        )
        sup.write_json(case / "gm-ledger-content-join.json", gm_content_join)

        after_hashes = sup.hash_tree(states_dir)
        sup.write_json(case / "after" / "state_hashes.json", after_hashes)
        before_hashes = json.loads((case / "before" / "state_hashes.json").read_text(encoding="utf-8"))
        for pk in NOT_SELECTED + (human.participant_id,):
            for rel, h in before_hashes.items():
                if f"{pk}." in rel or f"/{pk}/" in rel or rel.startswith(pk):
                    assert after_hashes.get(rel) == h, f"unveraendert erwarteter Zustand von {pk} hat sich geaendert: {rel}"

        result.update({
            "status": "PASS", "table": summary, "offer_id": offer_id,
            "cli_requests": len(cli_calls), "gm_requests": len(gm_srv.calls), "max_usd": status.max_usd,
            "turns_used_final": status.turns_used,
        })
    sup.write_json(case / "result.json", result)
    sup.write_json(case / "assertions.json", {"claims": [
        {"id": "A02", "claim": "echter Subprozess, stdin=DEVNULL fuer 'lab start'", "verified_by": "p.returncode==0, _run_lab stdin=DEVNULL", "evidence": "invocations.json"},
        {"id": "A03", "claim": "tech (nicht sniper) wird per sniper-Initiative nominierter Leader", "verified_by": "table.leader=='tech'", "evidence": "final_table_state.json"},
        {"id": "A05/A06", "claim": "G0-G4 vollstaendig, lange unterscheidbare Endmarker, korrekter SL-Praefix an allen 9 Tischentscheidungen", "verified_by": "_assert_public_sl_prefix_and_reflections_exact", "evidence": "classified-persona-wires.json, gm-receipts.jsonl"},
        {"id": "A07", "claim": "eigene/fremde Privattrennung im CLI-STDIN", "verified_by": "own_reflection_text[other_pk] not in c['system']", "evidence": "classified-persona-wires.json"},
        {"id": "A08", "claim": "nur Leader sendet an SL, origin_persona_key korrekt", "verified_by": "_assert_sl_log_leader_only_and_origin", "evidence": "final_table_state.json#sl_log"},
        {"id": "A09", "claim": "unterscheidbare GM-End-Saves -> Current; eigene Reflexion+Current im neuen Fenster (Hybrid)", "verified_by": "current['_h02_end_marker'] + pause_entries-Check", "evidence": "classified-persona-wires.json"},
        {"id": "A10", "claim": "nicht ausgewaehlte Personas + Mensch bytegleich", "verified_by": "after_hashes==before_hashes fuer NOT_SELECTED+human", "evidence": "before/after state_hashes.json"},
        {"id": "A11", "claim": "echte Isolationsflags belegt, CLI-stdin [SYSTEM]/[USER], cwd korrekt", "verified_by": "argv/stdin/cwd-Check je cli_calls-Eintrag", "evidence": "cli-receipts.jsonl"},
        {"id": "A12", "claim": "max_usd=5 (GM-Rolle), CLI-Quota bleibt unbekannt, provider_free vor/nach True", "verified_by": "status.max_usd==5, provider_free-Checks", "evidence": "result.json"},
        {"id": "R3-authority", "claim": "Fake-CLI validiert Input (kein blindes Poppen), 0 Validierungsfehler", "verified_by": "fail_log leer/nicht vorhanden", "evidence": "cli-receipts.validation-failures.jsonl"},
        {"id": "R4-turns", "claim": "exakt 18 verbuchte Entscheidungen (13 Persona + 5 GM) auch im Hybrid-Profil, nicht nur >=18",
         "verified_by": "status.turns_used==18", "evidence": "result.json"},
        {"id": "G09", "claim": "Fake-CLI prueft zusaetzlich zur Persona-Identitaet die tatsaechliche SL-Praefixlaenge (expect_sl_log_len), GM-Validator prueft Leadertext",
         "verified_by": "expect_sl_log_len in queue-Items + _gm_validators_for_full_journey verdrahtet", "evidence": "cli-receipts.jsonl, gm-receipts.jsonl"},
        {"id": "G10", "claim": "13 Persona + 5 GM = 18 requestweise gegen vorhandenes request_ledger zugeordnet (Rollen+Teilnehmer+state=accounted)",
         "verified_by": "_assert_request_ledger_reconciles(run_dir, table_id)", "evidence": "request-ledger-reconciliation.json"},
    ]})


# ---------------------------------------------------------------------------
# Y-N1: Hybrid-CLI-Fehler beim Entscheidungsaufruf -- KEIN API-Fallback.
# ---------------------------------------------------------------------------

def _persona_rounds_played(states_dir: Path, schema_path: Path, personas=("sniper", "tech")) -> dict:
    """C3-Nachzug (02_AUFTRAG_C_ABSCHLUSS.md C3 'Persona-Runden/-Reflexionen
    ... sichern und fachliche Nullfolgen assertieren'): liest `rounds_played`
    UND `last_reflection` je Persona direkt aus dem realen Persona-State
    (nicht aus stdout/leeren Ordnern abgeleitet)."""
    ps_store = PersonaStateStore(schema_path=schema_path)
    out = {}
    for pk in personas:
        try:
            state = ps_store.load_state(pk, states_dir=states_dir)
            out[pk] = {"rounds_played": state.get("rounds_played", 0), "last_reflection": state.get("last_reflection")}
        except FileNotFoundError:
            out[pk] = None
    return out


def _assert_nullfolgen(before: dict, after: dict, *, allow_requests_change: bool, allow_status_change: bool, label: str) -> None:
    """C3-Nachzug (02_AUFTRAG_C_ABSCHLUSS.md C3): vergleicht zwei
    `_authority_hash_snapshot`-Aufnahmen und erzwingt, dass NUR die
    ausdruecklich erlaubten Bereiche (`requests/`, `lab.status.json` -- die
    legitimen Fehler-/Kostenrecords) sich aendern duerfen; `tables/`
    (kein Tischabschluss), `current_saves/` (keine neue Save-/
    Versionspublikation) und `locks.json` (keine haengende Sperre nach
    geordnetem Stop) MUESSEN bytegleich bleiben."""
    assert before["tables"] == after["tables"] == {}, f"{label}: unerlaubte Tischaenderung/-abschluss: before={before['tables']} after={after['tables']}"
    # `current_saves` ist bereits VOR jedem Y-N-Lauf durch `make_ready()`
    # (Bootstrap-Publikation der Start-Fixture) befuellt -- NICHT `{}`. Die
    # Nullfolge ist deshalb Gleichheit (kein DRIFT), nicht Leere.
    assert before["current_saves"] == after["current_saves"], (
        f"{label}: unerlaubte neue Save-/Versionspublikation: before={before['current_saves']} after={after['current_saves']}"
    )
    # `locks.json` wird PRODUKTSEITIG lazy angelegt (existiert vor dem ersten
    # Schreibzugriff gar nicht, `_authority_hash_snapshot` liefert dann
    # `None`; nach dem Anlegen mit leerem Inhalt `{}` traegt es
    # `sha256(b"{}")` -- BEIDES bedeutet "keine aktive Sperre", kein Drift.
    # Eine echte haengende Sperre haette einen ANDEREN (nicht-leeren) Hash.
    _empty_locks_sha = hashlib.sha256(b"{}").hexdigest()
    normalized_before_locks = None if before["locks.json"] in (None, _empty_locks_sha) else before["locks.json"]
    normalized_after_locks = None if after["locks.json"] in (None, _empty_locks_sha) else after["locks.json"]
    assert normalized_before_locks == normalized_after_locks, (
        f"{label}: haengende/veraenderte Sperre nach geordnetem Stop: before={before['locks.json']} after={after['locks.json']}"
    )
    if not allow_requests_change:
        assert before["requests"] == after["requests"], f"{label}: unerwartete Requestledger-Aenderung: {before['requests']} != {after['requests']}"
    if not allow_status_change:
        assert before["lab.status.json"] == after["lab.status.json"], f"{label}: unerwartete lab.status.json-Aenderung"


def test_y_n1_hybrid_cli_failure_no_api_fallback():
    case = sup.case_dir("Y_N1_hybrid_cli_failure")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        guard_dir = sup.write_loopback_guard(root / "guard")
        _schema, states_dir, run_dir, onboarding_dir, _catalog = sup.bootstrap_six_persona_community(
            root, "community-yn1", ("sniper", "tech"),
        )
        for pk in ("sniper", "tech"):
            sup.make_ready(onboarding_dir, states_dir, run_dir, pk)
        # C3-Nachzug: vorher/nachher-Autoritaetsbelege + Persona-Runden/
        # -Reflexionen aus den REALEN Stores (nicht aus ausbleibendem stdout
        # oder leerem Tischordner abgeleitet).
        rounds_before = _persona_rounds_played(states_dir, _schema)
        snapshot_before = _authority_hash_snapshot(run_dir)
        cli_capture = case / "cli-receipts.jsonl"
        fail_marker = root / "fake_cli_should_fail"
        fail_marker.write_text("1", encoding="utf-8")
        fake_cli = sup.write_queued_fake_cli(
            root, capture_path=cli_capture, queue=[{"result": _leader_nomination_proposal()}],
            fail_marker_path=fail_marker,
        )
        api_trap = sup.recording_http_server(
            [(200, {"choices": [{"message": {"content": '{"action": "pause"}'}}]})],
            receipts_path=case / "api-trap-receipts.jsonl", label="api-trap",
        )
        # R4-Nachzug (Review H02 2026-09-28 §5): Y-N1 hatte bisher NUR eine
        # Persona-API-Falle. Review-Befund: "Y-N1 muss neben der API-Falle
        # auch GM-/Publikationsfolgen ausschliessen" -- zusaetzliche eigene
        # GM-Falle, die bei einem (verbotenen) Fortschritt nach dem CLI-
        # Fehler angesprochen wuerde.
        gm_trap = sup.recording_http_server(
            [(200, {"choices": [{"message": {"content": "GM-Falle haette nie erreicht werden duerfen"}}]})],
            receipts_path=case / "gm-trap-receipts.jsonl", label="gm-trap",
        )
        with api_trap, gm_trap:
            env = {
                "MMO_SIM_PERSONA_CLI": str(fake_cli),
                "MMO_SIM_PERSONA_ISOLATED_WORKDIR": str((root / "cli_workdir")),
                "MMO_SIM_PERSONA_ISOLATION_FLAGS": "--permission-mode=plan,--safe-mode",
                # Falle: eine gueltig konfigurierte Persona-API DARF nicht
                # kontaktiert werden (kein automatischer Providerwechsel).
                "MMO_SIM_PERSONA_API_BASE_URL": api_trap.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTH-TRAP", "MMO_SIM_PERSONA_API_MODEL": "trap",
                # Falle: keine GM-/Publikationsfolge nach dem CLI-Fehler.
                "OPENWEBUI_URL": gm_trap.base_url, "OPENWEBUI_API_KEY": "SYNTH-TRAP",
                "MMO_SIM_GM_OUTPUT_LIMIT_TOKENS": "4096",
            }
            (root / "cli_workdir").mkdir(parents=True, exist_ok=True)
            start_args = [
                "start", "--data-dir", str(root), "--community", "yn1", "--profile", "hybrid",
                "--personas", "sniper,tech", "--max-requests", "10", "--max-seconds", "60",
                "--max-usd", "5", "--max-idle-windows", "1",
            ]
            p = _run_lab(start_args, env_extra=env, tmp_root=root / "kidtmp", guard_dir=guard_dir)
            _log_invocation(case, "start", start_args, env, p)
            assert p.returncode == 0, p.stdout + p.stderr  # geordneter Stop, kein Absturz.
            assert "fehlgeschlagen" in p.stdout, p.stdout
            assert api_trap.calls == [], f"API-Falle haette 0 Requests erhalten muessen: {len(api_trap.calls)}"
            assert gm_trap.calls == [], f"GM-Falle haette 0 Requests erhalten muessen (R4): {len(gm_trap.calls)}"
        cli_calls = [json.loads(line) for line in cli_capture.read_text(encoding="utf-8").splitlines() if line.strip()]
        assert len(cli_calls) == 1, "Fake-CLI muss real getroffen worden sein (echter Entscheidungsaufruf)"
        assert "Lobby-Tisch abgeschlossen" not in p.stdout
        table_path = run_dir / "tables"
        assert not table_path.exists() or list(table_path.glob("*.json")) == [], (
            "R4: kein Tisch/Save nach Y-N1-CLI-Fehler erwartet"
        )
        # C3-Nachzug: vollstaendige vorher/nachher-Nullfolgen -- der CLI-
        # Fehlerpfad darf `requests/`/`lab.status.json` aendern (legitimer
        # Fehler-/Kostenrecord), NICHT aber tables/current_saves/locks.json
        # oder Persona-Runden/-Reflexionen.
        snapshot_after = _authority_hash_snapshot(run_dir)
        rounds_after = _persona_rounds_played(states_dir, _schema)
        _assert_nullfolgen(snapshot_before, snapshot_after, allow_requests_change=True, allow_status_change=True, label="Y-N1")
        assert rounds_after == rounds_before, f"Y-N1: Persona-Runden/-Reflexionen haetten unveraendert bleiben muessen: {rounds_before} -> {rounds_after}"
        sup.write_json(case / "before-after-nullfolgen.json", {"before": snapshot_before, "after": snapshot_after, "rounds_before": rounds_before, "rounds_after": rounds_after})
        sup.write_json(case / "result.json", {
            "status": "PASS", "cli_hit": True, "api_trap_calls": len(api_trap.calls), "gm_trap_calls": len(gm_trap.calls),
            "returncode": p.returncode,
        })
        sup.write_json(case / "assertions.json", {"claims": [
            {"id": "Y-N1", "claim": "CLI rc=1 real getroffen, 0 API-Fallback-Calls, 0 GM-Folgeanfragen, keine Erfolgspublikation",
             "verified_by": "len(cli_calls)==1 (rc=1 via fail_marker), api_trap.calls==[], gm_trap.calls==[], kein Tisch/Save-File",
             "evidence": "cli-receipts.jsonl, api-trap-receipts.jsonl, gm-trap-receipts.jsonl"},
            {"id": "Y-N1-nullfolgen", "claim": "vollstaendige vorher/nachher-Nullfolgen: tables/current_saves/locks/Runden unveraendert",
             "verified_by": "_assert_nullfolgen(...), rounds_after==rounds_before", "evidence": "before-after-nullfolgen.json"},
        ]})


# ---------------------------------------------------------------------------
# Y-N2: API-Fehler (401) -- kein Switch auf Hybrid/anderen Provider.
# ---------------------------------------------------------------------------

def test_y_n2_api_error_401_no_fallback():
    case = sup.case_dir("Y_N2_api_error_401")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        guard_dir = sup.write_loopback_guard(root / "guard")
        _schema, states_dir, run_dir, onboarding_dir, _catalog = sup.bootstrap_six_persona_community(
            root, "community-yn2", ("sniper", "tech"),
        )
        for pk in ("sniper", "tech"):
            sup.make_ready(onboarding_dir, states_dir, run_dir, pk)
        rounds_before = _persona_rounds_played(states_dir, _schema)
        snapshot_before = _authority_hash_snapshot(run_dir)
        # R4-Nachzug (Review H02 2026-09-28 §5): "Y-N2 liefert zwar einen
        # echten API-401, stellt aber keine gleichzeitig nutzbare Fake-CLI-
        # Fallbackfalle bereit." -- eine unberuehrte, real funktionsfaehige
        # Fake-CLI wird jetzt zusaetzlich konfiguriert (auch wenn das
        # `api`-Profil sie produktseitig nicht anspricht); 0 Aufrufe belegen,
        # dass kein impliziter Providerwechsel stattfindet.
        cli_trap_capture = case / "cli-trap-receipts.jsonl"
        cli_trap = sup.write_queued_fake_cli(
            root, capture_path=cli_trap_capture, queue=[{"result": '{"action": "pause"}'}],
        )
        with sup.recording_http_server(
            [(401, {"error": "invalid_api_key (H02 Y-N2, markiert)"})],
            receipts_path=case / "persona-receipts.jsonl", label="persona-401",
        ) as persona_srv:
            env = {
                "MMO_SIM_PERSONA_API_BASE_URL": persona_srv.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTH-EXPIRED", "MMO_SIM_PERSONA_API_MODEL": "synthetic-yn2",
                "MMO_SIM_PERSONA_CLI": str(cli_trap),
                "MMO_SIM_PERSONA_ISOLATED_WORKDIR": str(root / "cli_workdir_trap"),
                "MMO_SIM_PERSONA_ISOLATION_FLAGS": "--permission-mode=plan,--safe-mode",
            }
            (root / "cli_workdir_trap").mkdir(parents=True, exist_ok=True)
            start_args = [
                "start", "--data-dir", str(root), "--community", "yn2", "--profile", "api",
                "--personas", "sniper,tech", "--max-requests", "10", "--max-seconds", "60",
                "--max-usd", "5", "--max-idle-windows", "1",
            ]
            p = _run_lab(start_args, env_extra=env, tmp_root=root / "kidtmp", guard_dir=guard_dir)
            _log_invocation(case, "start", start_args, env, p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert "fehlgeschlagen" in p.stdout, p.stdout
            assert len(persona_srv.calls) == 1, "genau EIN markierter 401-Request erwartet"
        assert not cli_trap_capture.exists() or cli_trap_capture.read_text(encoding="utf-8").strip() == "", (
            f"R4: Fake-CLI-Falle haette 0 Aufrufe erhalten muessen (kein Profilwechsel): {cli_trap_capture.read_text(encoding='utf-8') if cli_trap_capture.exists() else ''}"
        )
        assert "Lobby-Tisch abgeschlossen" not in p.stdout
        snapshot_after = _authority_hash_snapshot(run_dir)
        rounds_after = _persona_rounds_played(states_dir, _schema)
        _assert_nullfolgen(snapshot_before, snapshot_after, allow_requests_change=True, allow_status_change=True, label="Y-N2")
        assert rounds_after == rounds_before, f"Y-N2: Persona-Runden/-Reflexionen haetten unveraendert bleiben muessen: {rounds_before} -> {rounds_after}"
        sup.write_json(case / "before-after-nullfolgen.json", {"before": snapshot_before, "after": snapshot_after, "rounds_before": rounds_before, "rounds_after": rounds_after})
        sup.write_json(case / "result.json", {
            "status": "PASS", "http_status": 401, "persona_calls": len(persona_srv.calls),
            "cli_trap_hit": cli_trap_capture.exists() and cli_trap_capture.read_text(encoding="utf-8").strip() != "",
        })
        sup.write_json(case / "assertions.json", {"claims": [
            {"id": "Y-N2", "claim": "markierter 401 auf echten Request, kein Provider-Switch (CLI-Falle 0 Calls), kein erfundener Erfolg",
             "verified_by": "len(persona_srv.calls)==1, cli_trap_capture leer/nicht vorhanden, 'Lobby-Tisch abgeschlossen' not in stdout",
             "evidence": "persona-receipts.jsonl, cli-trap-receipts.jsonl"},
            {"id": "Y-N2-nullfolgen", "claim": "vollstaendige vorher/nachher-Nullfolgen: tables/current_saves/locks/Runden unveraendert",
             "verified_by": "_assert_nullfolgen(...), rounds_after==rounds_before", "evidence": "before-after-nullfolgen.json"},
        ]})


# ---------------------------------------------------------------------------
# Y-N3: fehlender GM-Outputbound blockiert unter hartem Dollarbudget --
# 0 GM-Receipts, kein neuer Save.
# ---------------------------------------------------------------------------

def test_y_n3_missing_gm_output_bound_blocks_under_hard_budget():
    case = sup.case_dir("Y_N3_missing_gm_output_bound")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        guard_dir = sup.write_loopback_guard(root / "guard")
        _schema, states_dir, run_dir, onboarding_dir, _catalog = sup.bootstrap_six_persona_community(
            root, "community-yn3", ("sniper", "tech"),
        )
        for pk in ("sniper", "tech"):
            sup.make_ready(onboarding_dir, states_dir, run_dir, pk)
        rounds_before = _persona_rounds_played(states_dir, _schema)
        snapshot_before = _authority_hash_snapshot(run_dir)
        offer_id = _offer_id_for_first_window("yn3")
        with sup.recording_http_server(
            [
                (200, {"choices": [{"message": {"content": _leader_nomination_proposal()}}]}),
                (200, {"choices": [{"message": {"content": _accept_as_nominated_leader(offer_id)}}]}),
                (200, {"choices": [{"message": {"content": "Wir starten den Debrief."}}]}),  # tech G0-Versuch
            ],
            receipts_path=case / "persona-receipts.jsonl", label="persona-yn3",
        ) as persona_srv, sup.recording_http_server(
            [], receipts_path=case / "gm-receipts.jsonl", label="gm-yn3-should-be-unused",
        ) as gm_srv:
            env = {
                "MMO_SIM_PERSONA_API_BASE_URL": persona_srv.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTH-H02-NOT-A-REAL-KEY", "MMO_SIM_PERSONA_API_MODEL": "synthetic-yn3",
                "OPENWEBUI_URL": gm_srv.base_url, "OPENWEBUI_API_KEY": "SYNTH-H02-NOT-A-REAL-KEY",
                # BEWUSST kein MMO_SIM_GM_OUTPUT_LIMIT_TOKENS -- Kontrollpunkt.
            }
            start_args = [
                "start", "--data-dir", str(root), "--community", "yn3", "--profile", "api",
                "--personas", "sniper,tech", "--max-requests", "10", "--max-seconds", "60",
                "--max-usd", "5", "--max-idle-windows", "1",
            ]
            p = _run_lab(start_args, env_extra=env, tmp_root=root / "kidtmp", guard_dir=guard_dir)
            _log_invocation(case, "start", start_args, env, p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert gm_srv.calls == [], f"0 GM-Receipts erwartet (Kontrollpunkt VOR Versand): {len(gm_srv.calls)}"
            assert "Lobby-Tisch abgeschlossen" not in p.stdout
            # R4-Nachzug (Review H02 2026-09-28 §5): "Y-N3 muss genau die
            # fehlende GM-Outputgrenze treffen, nicht eine vorgezogene
            # andere Ablehnung (z.B. fehlendes max_usd)." -- die exakte
            # Admission-Begruendung aus `core/admission.py:read_admission_
            # block` (empirisch aus einem eigenen Ground-Truth-Lauf
            # uebernommen) wird jetzt woertlich geprueft, nicht nur
            # abwesende Folgen.
            assert "Kein durchsetzbares Ausgabe-/Gesamtlimit fuer diesen Treiber ermittelbar" in p.stdout, (
                f"Y-N3: Blockgrund nicht die erwartete fehlende GM-Outputgrenze: {p.stdout}"
            )
            assert "max_usd" in p.stdout and "5.0" in p.stdout, (
                f"Y-N3: hartes max_usd nicht Teil der Ablehnungsbegruendung: {p.stdout}"
            )
        table_path = run_dir / "tables" / "lobby-sniper-tech.json"
        assert not table_path.exists() or json.loads(table_path.read_text(encoding="utf-8")).get("status") != "closed", (
            "kein neuer erfolgreicher Abschluss/Save erwartet"
        )
        # C3-Nachzug: vorher/nachher-Nullfolgen -- Y-N3 darf (anders als
        # Y-N1/Y-N2/Y-N4) legitim einen GEBUNDENEN (aber NICHT geschlossenen)
        # Tisch erzeugen, s. obige Pruefung; `current_saves`/Persona-Runden
        # muessen trotzdem unveraendert bleiben (kein Abschluss = keine
        # Publikation).
        snapshot_after = _authority_hash_snapshot(run_dir)
        rounds_after = _persona_rounds_played(states_dir, _schema)
        assert snapshot_before["current_saves"] == snapshot_after["current_saves"], (
            f"Y-N3: unerlaubte neue Save-/Versionspublikation: before={snapshot_before['current_saves']} after={snapshot_after['current_saves']}"
        )
        assert rounds_after == rounds_before, f"Y-N3: Persona-Runden/-Reflexionen haetten unveraendert bleiben muessen: {rounds_before} -> {rounds_after}"
        sup.write_json(case / "before-after-nullfolgen.json", {"before": snapshot_before, "after": snapshot_after, "rounds_before": rounds_before, "rounds_after": rounds_after})
        sup.write_json(case / "result.json", {"status": "PASS", "gm_calls": len(gm_srv.calls)})
        sup.write_json(case / "assertions.json", {"claims": [
            {"id": "Y-N3", "claim": "fehlender GM-Outputbound blockiert vor Versand unter hartem max_usd (exakter Blockgrund), 0 GM-Receipts, kein neuer Save",
             "verified_by": "exakte Admission-Begruendung 'Kein durchsetzbares Ausgabe-/Gesamtlimit...' im stdout, gm_srv.calls==[], kein table-Abschluss",
             "evidence": "gm-receipts.jsonl, invocations.json"},
            {"id": "Y-N3-nullfolgen", "claim": "keine neue Save-/Versionspublikation, Persona-Runden/-Reflexionen unveraendert (Tisch darf gebunden, aber nicht geschlossen sein)",
             "verified_by": "current_saves before==after (unveraendert), rounds_after==rounds_before", "evidence": "before-after-nullfolgen.json"},
        ]})


# ---------------------------------------------------------------------------
# Y-N4: providerfreies Testprofil autorisiert keine externe Route -- Ablehnung
# VOR DNS/Socket, kein realer externer Request.
# ---------------------------------------------------------------------------

def test_y_n4_test_authority_blocks_non_loopback_route():
    case = sup.case_dir("Y_N4_blocked_test_authority_host")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        guard_dir = sup.write_loopback_guard(root / "guard")
        _schema, states_dir, run_dir, onboarding_dir, _catalog = sup.bootstrap_six_persona_community(
            root, "community-yn4", ("sniper", "tech"),
        )
        for pk in ("sniper", "tech"):
            sup.make_ready(onboarding_dir, states_dir, run_dir, pk)
        write_test_profile(run_dir, max_usd=5.0)  # providerfreie Testautoritaet VOR dem Start.
        rounds_before = _persona_rounds_played(states_dir, _schema)
        snapshot_before = _authority_hash_snapshot(run_dir)
        blocked_url = sup.blocked_target_url()
        env = {
            "MMO_SIM_PERSONA_API_BASE_URL": blocked_url,
            "MMO_SIM_PERSONA_API_KEY": "SYNTH-H02-NOT-A-REAL-KEY", "MMO_SIM_PERSONA_API_MODEL": "synthetic-yn4",
        }
        start_args = [
            "start", "--data-dir", str(root), "--community", "yn4", "--profile", "api",
            "--personas", "sniper,tech", "--max-requests", "10", "--max-seconds", "15",
            "--max-usd", "5", "--max-idle-windows", "1",
        ]
        p = _run_lab(start_args, env_extra=env, timeout=30, tmp_root=root / "kidtmp", guard_dir=guard_dir)
        _log_invocation(case, "start", start_args, env, p)
        assert p.returncode == 0, p.stdout + p.stderr
        assert "gestoppt (Admission-Gate" in p.stdout, p.stdout
        assert "autorisiert keine externe Route" in p.stdout, p.stdout
        snapshot_after = _authority_hash_snapshot(run_dir)
        rounds_after = _persona_rounds_played(states_dir, _schema)
        _assert_nullfolgen(snapshot_before, snapshot_after, allow_requests_change=True, allow_status_change=True, label="Y-N4")
        assert rounds_after == rounds_before, f"Y-N4: Persona-Runden/-Reflexionen haetten unveraendert bleiben muessen: {rounds_before} -> {rounds_after}"
        sup.write_json(case / "before-after-nullfolgen.json", {"before": snapshot_before, "after": snapshot_after, "rounds_before": rounds_before, "rounds_after": rounds_after})
        sup.write_json(case / "result.json", {"status": "PASS", "blocked_url": blocked_url})
        sup.write_json(case / "assertions.json", {"claims": [
            {"id": "Y-N4", "claim": "providerfreies Testprofil blockiert nicht-loopback Route am Admissionpunkt vor DNS/Socket, kein externer Request",
             "verified_by": "'gestoppt (Admission-Gate' + 'autorisiert keine externe Route' im stdout, kein Netzwerkfehler (DNS/Timeout) im stdout/stderr",
             "evidence": "invocations.json"},
            {"id": "Y-N4-nullfolgen", "claim": "vollstaendige vorher/nachher-Nullfolgen: tables/current_saves/locks/Runden unveraendert",
             "verified_by": "_assert_nullfolgen(...), rounds_after==rounds_before", "evidence": "before-after-nullfolgen.json"},
        ]})


# ---------------------------------------------------------------------------
# N-HUMAN: echte menschliche waiting/hold-Probe an einem ueber bestehende
# Produktdienste vorab gebundenen Tisch (kein Ersatz fuer A03).
# ---------------------------------------------------------------------------

def test_n_human_waiting_hold_no_ai_takeover():
    case = sup.case_dir("N_HUMAN_waiting_hold")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        # A01: die registrierte ID wird selbst als persona_key fuer den
        # Community-/Onboarding-Weg verwendet -- kein erfundener fester
        # Produkt-ID-Wert (kein Literal wie "human_ops").
        human = sup.register_human_participant(root / "participants", "H02-Operator-Mensch-NHUMAN")
        human_pk = human.participant_id
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = sup.bootstrap_six_persona_community(
            root, "community-nhuman", ("sniper", human_pk),
        )
        sup.make_ready(onboarding_dir, states_dir, run_dir, "sniper")
        # Menschlicher Community-Slot: eigener v7-Save UEBER denselben
        # Onboarding-/Publish-Produktweg wie jede KI-Persona (A01: eigene
        # Figur, kein Wiederverwenden einer KI-Identitaet) -- KEIN
        # Erschaffungsdialog, nur die bestehende Fixture-Publish-Kette,
        # unter derselben Registry-ID (`human_pk`) und via `add_record_ref()`
        # sichtbar mit der Registry-Identitaet verbunden.
        ps_store = PersonaStateStore(schema_path=schema_path)
        human = sup.onboard_human_figure(root / "participants", human_pk, onboarding_dir, states_dir, run_dir)
        sup.write_json(case / "human_participant.json", {
            "participant_id": human.participant_id, "kind": human.kind, "display_name": human.display_name,
            "record_refs": [r.__dict__ for r in human.record_refs],
        })

        # Vorbestand: ein bereits gebundener Tisch mit sniper (KI) + Mensch
        # (registry-verbundene Figur) -- ueber bestehende Produktdienste
        # aufgebaut (02 §A ausdruecklich zulaessig fuer N-HUMAN), NICHT als
        # Ersatz fuer A03.
        lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        for pk in ("sniper", human_pk):
            lobby.join(pk)
        from mmo_sim.core.store import load_current_save_or_raise
        from mmo_sim.domain.zeitriss import saves as zeitriss_saves
        chrono_ids, active_saves = {}, {}
        for pk in ("sniper", human_pk):
            save = load_current_save_or_raise(run_dir, pk, ps_store, states_dir=states_dir)
            chrono_ids[pk] = zeitriss_saves.block_char_id(save)
            active_saves[pk] = save
        offer_events = [
            {"type": "offer", "id": "offer-nhuman", "from": "sniper", "wants": [human_pk], "window_id": "w0"},
            {"type": "consent", "offer_id": "offer-nhuman", "from": human_pk, "accept": True},
        ]
        table, derivation = core_store.create_table_from_offer_log(lobby, f"lobby-sniper-{human_pk}", offer_events, chrono_ids)
        assert table is not None, derivation.reason

        printed: list[str] = []

        class _Session:
            def __init__(self):
                self.run_dir = run_dir
                self.schema_path = schema_path
                self.states_dir = states_dir

            def _print(self, msg):
                printed.append(msg)

            def _own_system_context(self, pk):
                return f"[H02-N-HUMAN Testkontext fuer {pk}]"

            def gm_transport_factory(self, *_a, **_kw):
                raise AssertionError("kein GM-Call erwartet (H09/N-HUMAN)")

            def persona_driver_factory(self, pk):
                raise AssertionError(f"kein KI-Treiber fuer '{pk}' erwartet (H09/N-HUMAN)")

        outcome = lobby_flow.play_bound_table(
            _Session(), lobby, table, offer_events, "offer-nhuman", active_saves,
            ai_personas=frozenset({"sniper"}),  # human_pk ist NICHT ausgewaehlt -> echter Mensch.
        )
        assert outcome.kind == lobby_flow.LobbyOutcomeKind.WAITING_HUMAN, outcome
        assert human_pk in outcome.reason, outcome.reason
        assert table.status != "closed", "kein Spielstart erwartet"
        sup.write_json(case / "result.json", {
            "status": "PASS", "outcome_kind": outcome.kind.value, "reason": outcome.reason,
            "human_participant_id": human.participant_id,
        })
        # End-Critic-Nacharbeit 2026-09-28, Befund 3: strukturierte Form
        # (analog allen anderen Testfaellen) statt der alten flachen
        # String-Liste -- reine Formatvereinheitlichung, keine neue Pruefung.
        sup.write_json(case / "assertions.json", {"claims": [
            {"id": "N-HUMAN", "claim": "bestehender legal gebundener Tisch mit echtem menschlichem Mitglied -> WAITING_HUMAN",
             "verified_by": "outcome.kind==WAITING_HUMAN UND human_pk in outcome.reason", "evidence": "result.json"},
            {"id": "N-HUMAN-noai", "claim": "0 KI-Treiberkonstruktion fuer IRGENDEIN Mitglied dieses Tisches, 0 GM-Call",
             "verified_by": "AssertionError-Fallen in _Session.gm_transport_factory/persona_driver_factory nie ausgeloest", "evidence": "result.json"},
        ]})


# ---------------------------------------------------------------------------
# N-STOP: separater 'lab stop'-Prozess an einer kontrolliert in-flight
# befindlichen Personaantwort + passives status/attach aus separaten
# Prozessen, waehrend der Controller lebt.
# ---------------------------------------------------------------------------

def _authority_hash_snapshot(run_dir: Path) -> dict:
    """C3-Nachzug (01_REVIEW_H02.md §5 'status/attach pruefen bislang im
    Wesentlichen lab.status.json statt auch Requests/Stop/Tabellen/Locks/
    Currents/States', 02_AUFTRAG_RESTPFLICHTEN.md C3): VORHER verglich
    N-STOP nur `lab.status.json` vor/nach `status`/`attach`. Diese Funktion
    hasht ALLE tatsaechlich vorhandenen relevanten Autoritaetsbereiche unter
    `run_dir` (nicht erfundene Pfade -- nur Verzeichnisse, die laut
    `core/store.py`/`core/request_ledger.py` bereits real existieren):
    `lab.status.json`, `lab.stop`, `locks.json`, `requests/` (Request-
    Ledger-Records), `tables/` (Tischzustand), `current_saves/` (publizierte
    Currents). Fehlende Pfade werden als `None` gefuehrt (kein Erfinden),
    Verzeichnisse ueber `sup.hash_tree`."""
    def _file_hash(name):
        p = run_dir / name
        return sup.sha256_of(p) if p.exists() else None

    return {
        "lab.status.json": _file_hash("lab.status.json"),
        "lab.stop": _file_hash("lab.stop"),
        "locks.json": _file_hash("locks.json"),
        "requests": sup.hash_tree(run_dir / "requests") if (run_dir / "requests").exists() else {},
        "tables": sup.hash_tree(run_dir / "tables") if (run_dir / "tables").exists() else {},
        "current_saves": sup.hash_tree(run_dir / "current_saves") if (run_dir / "current_saves").exists() else {},
    }


def _authority_state_snapshot(run_dir: Path, states_dir: Path, schema_path, personas=("sniper", "tech")) -> dict:
    """Liest die echten Autoritaeten des bestehenden einzelnen N-STOP.

    Rundenzahl, Reflexionen und die publizierte Versionsreferenz gehoeren
    zum Persona-State, nicht zum ZEITRISS-v7-Save. ``v`` ist eine
    Schemanummer und ersetzt weder ``current_save_version`` noch das
    Versionsinventar. Vollstaendige Inhalte und Pfad/Byte-Inventare halten
    auch Aenderungen bei unveraenderter save_id oder Schemanummer fest.
    Status/Request-Abrechnung und lab.stop sind erlaubte Kontrollfolgen;
    sie stehen deshalb separat von den unveraendert erwarteten Daten.
    Kein Write, keine Publikation, kein weiterer Stop-/Signal-/Leasefall.
    """
    run_dir, states_dir = Path(run_dir), Path(states_dir)
    status = lab_runner.read_status(run_dir)
    ps_store = PersonaStateStore(schema_path=schema_path)
    currents = {}
    persona_states = {}
    for pk in personas:
        persona_states[pk] = ps_store.load_state(pk, states_dir=states_dir)
        currents[pk] = core_store.load_current_save_or_raise(
            run_dir, pk, ps_store, states_dir=states_dir,
        )
    protected_authority_hashes = {
        "persona_states": sup.hash_tree(states_dir),
        "current_saves_and_versions": sup.hash_tree(run_dir / "current_saves"),
        "completion": sup.hash_tree(run_dir / "completion"),
        "tables": sup.hash_tree(run_dir / "tables"),
        "locks.json": sup.sha256_of(run_dir / "locks.json"),
        "reflections.jsonl": sup.sha256_of(run_dir / "reflections.jsonl"),
    }
    reflections_path = run_dir / "reflections.jsonl"
    reflections = sup.read_jsonl(reflections_path) if reflections_path.exists() else []
    tables_state = {}
    tables_dir = run_dir / "tables"
    if tables_dir.exists():
        for p in sorted(tables_dir.glob("*.json")):
            data = json.loads(p.read_text(encoding="utf-8"))
            tables_state[p.name] = {"status": data.get("status"), "sl_log_len": len(data.get("sl_log") or [])}
    return {
        "turns_used": status.turns_used if status else None,
        "max_usd": status.max_usd if status else None,
        "usd_spent": status.usd_spent if status else None,
        "running": status.running if status else None,
        "lab_stop_file_exists": (run_dir / "lab.stop").exists(),
        "currents": currents,
        "persona_states": persona_states,
        "protected_authority_hashes": protected_authority_hashes,
        "reflections_count": len(reflections),
        "reflections": reflections,
        "tables": tables_state,
    }


def test_n_stop_separate_process_in_flight_barrier():
    case = sup.case_dir("N_STOP_separate_process")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        guard_dir = sup.write_loopback_guard(root / "guard")
        _schema, states_dir, run_dir, onboarding_dir, _catalog = sup.bootstrap_six_persona_community(
            root, "community-nstop", ("sniper", "tech"),
        )
        for pk in ("sniper", "tech"):
            sup.make_ready(onboarding_dir, states_dir, run_dir, pk)

        block_event = threading.Event()
        release_event = threading.Event()
        # B2-Nacharbeit (G11, 02_AUFTRAG_BELEGSCHLUSS.md, 07_HYBRID_API_SL_
        # VOLLSTAENDIG.md §7): EIGENER unabhaengiger Empfangszaehler/
        # Responsejournal -- bewusst GETRENNT vom Produkt-`request_ledger`
        # (das G10 an anderer Stelle real prueft). Dieser Handler zaehlt
        # tatsaechlich am Socket empfangene POSTs SOFORT beim Empfang, BEVOR
        # die kontrollierte Barriere freigegeben wird -- ein zweiter,
        # unabhaengig gefuehrter Beleg fuer "genau einmal empfangen", nicht
        # nur ein Produktledger-Blick von aussen.
        independent_receipts: list[dict] = []

        class _BlockingHandler(BaseHTTPRequestHandler):
            def log_message(self, *a):
                return

            def do_POST(self):
                length = int(self.headers.get("Content-Length", 0) or 0)
                raw = self.rfile.read(length) if length else b""
                # C3-Nachzug r2 (01_REVIEW_H02.md §5/02_AUFTRAG_RESTABSCHLUSS.md
                # C3 'auch die vollstaendigen tatsaechlichen Requestbytes/den
                # dekodierten Body mit Bezug auf den vorhandenen Hash
                # speichern'): VORHER nur `body_sha256`+`content_length`
                # (Hash+Laenge) -- jetzt ZUSAETZLICH der tatsaechlich
                # dekodierte Body selbst, unter Bezug auf denselben (bereits
                # vorhandenen, unveraenderten) Hash der Rohbytes.
                try:
                    decoded_body = json.loads(raw.decode("utf-8")) if raw else {}
                except (UnicodeDecodeError, json.JSONDecodeError):
                    decoded_body = {"_raw_undecoded_base64": __import__("base64").b64encode(raw).decode("ascii")}
                record = {
                    "seq": len(independent_receipts), "method": "POST", "path": self.path,
                    "content_length": length, "body_sha256": hashlib.sha256(raw).hexdigest(),
                    "body": decoded_body,
                    "received_monotonic": time.monotonic(),
                    # C3-Nachzug (02_AUFTRAG_C_ABSCHLUSS.md C3, 01_REVIEW_H02.md §5
                    # 'Sein eigener Handler journalisiert weiterhin KEINEN
                    # Ausgangsbody, nur Eingangsmetadaten'): Ausgangsfelder werden
                    # NACH dem tatsaechlichen `wfile.write` unten in DIESEN
                    # bereits journalisierten Eintrag ergaenzt (kein zweiter
                    # Schreiber) -- genau EIN Ein- UND Ausgangsbody.
                    "egress_body": None, "egress_sha256": None, "egress_sent_monotonic": None,
                }
                independent_receipts.append(record)
                block_event.set()  # Barriere: Persona-Request ist jetzt in-flight.
                release_event.wait(timeout=30)
                egress_body_dict = {"choices": [{"message": {"content": '{"action": "pause"}'}}]}
                payload = json.dumps(egress_body_dict).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                record["egress_body"] = egress_body_dict
                record["egress_sha256"] = hashlib.sha256(payload).hexdigest()
                record["egress_sent_monotonic"] = time.monotonic()

        srv = HTTPServer(("127.0.0.1", 0), _BlockingHandler)
        thread = threading.Thread(target=srv.serve_forever, daemon=True)
        thread.start()
        try:
            base_url = f"http://{srv.server_address[0]}:{srv.server_address[1]}"
            env = sup.minimal_lab_env({
                "MMO_SIM_PERSONA_API_BASE_URL": base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTH-H02-NOT-A-REAL-KEY", "MMO_SIM_PERSONA_API_MODEL": "synthetic-nstop",
            }, tmp_root=root / "kidtmp1", guard_dir=guard_dir)
            proc1 = subprocess.Popen(
                [sys.executable, str(_MMO_SIM), "lab", "start", "--data-dir", str(root),
                 "--community", "nstop", "--profile", "api", "--personas", "sniper,tech",
                 "--max-requests", "5", "--max-seconds", "60", "--max-usd", "5", "--max-idle-windows", "1"],
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env,
                cwd=str(_REPO_ROOT),
            )
            status_args = ["status", "--data-dir", str(root)]
            attach_args = ["attach", "--data-dir", str(root), "--max-updates", "1"]
            stop1_args = ["stop", "--data-dir", str(root), "--reason", "h02-n-stop-controlled"]
            stop2_args = ["stop", "--data-dir", str(root), "--reason", "h02-n-stop-repeat"]
            try:
                assert block_event.wait(timeout=20), "Prozess 1 haette real den Persona-Server erreichen muessen"

                # R4-Nachzug (Review H02 2026-09-28 §5): read-only-Beleg VOR
                # jedem status/attach-Aufruf per Byte-Hash -- 'ohne
                # Autoritaetsmutation' war bisher nur behauptet, nicht
                # geprueft. C3-Nachzug: NICHT mehr nur `lab.status.json`,
                # sondern die volle `_authority_hash_snapshot` (Requests/
                # Stop/Tabellen/Locks/Currents), s. dortiger Docstring.
                snapshot_before_status = _authority_hash_snapshot(run_dir)

                # Passive status/attach aus SEPARATEN Prozessen, waehrend der
                # Controller lebt -- keine Produktwrites, kein privater
                # Kontexttransfer.
                p_status = _run_lab(status_args, tmp_root=root / "kidtmp_status", guard_dir=guard_dir)
                _log_invocation(case, "status_while_inflight", status_args, {}, p_status)
                assert p_status.returncode == 0, p_status.stderr
                status_payload = json.loads(p_status.stdout)
                assert status_payload["run"] == "known"
                assert status_payload["running"] is True
                snapshot_after_status = _authority_hash_snapshot(run_dir)
                assert snapshot_after_status == snapshot_before_status, (
                    f"C3: 'lab status' hat relevante Autoritaetsbytes veraendert (erwartet read-only): "
                    f"before={snapshot_before_status} after={snapshot_after_status}"
                )

                snapshot_before_attach = _authority_hash_snapshot(run_dir)
                p_attach = _run_lab(attach_args, tmp_root=root / "kidtmp_attach", guard_dir=guard_dir)
                _log_invocation(case, "attach_while_inflight", attach_args, {}, p_attach)
                assert p_attach.returncode == 0, p_attach.stderr
                snapshot_after_attach = _authority_hash_snapshot(run_dir)
                assert snapshot_after_attach == snapshot_before_attach, (
                    f"C3: 'lab attach' hat relevante Autoritaetsbytes veraendert (erwartet read-only): "
                    f"before={snapshot_before_attach} after={snapshot_after_attach}"
                )
                sup.write_json(case / "authority-snapshots-read-only-proof.json", {
                    "before_status": snapshot_before_status, "after_status": snapshot_after_status,
                    "before_attach": snapshot_before_attach, "after_attach": snapshot_after_attach,
                })

                # C3-Nachzug r2 (02_AUFTRAG_RESTABSCHLUSS.md C3 'reale Current-/
                # Versions-/Persona-Runden-/Reflexions-/Tisch-/Completion-/
                # Budgetautoritaeten VOR Stop ... vergleichen'): Snapshot der
                # TATSAECHLICHEN Werte (nicht nur Byte-Hashes) unmittelbar VOR
                # dem ersten Stop-Aufruf.
                authority_state_before_stop = _authority_state_snapshot(run_dir, states_dir, _schema)
                for pk, cur in authority_state_before_stop["currents"].items():
                    assert cur is not None, (
                        f"C3: gesunder Fall -- Start-Current von {pk} darf VOR Stop nicht leer sein: {cur}"
                    )
                assert authority_state_before_stop["lab_stop_file_exists"] is False, (
                    f"C3: lab.stop existierte bereits VOR dem ersten Stop-Aufruf: {authority_state_before_stop}"
                )

                # Separater 'lab stop'-Prozess -- idempotente Stopanforderung.
                p_stop1 = _run_lab(stop1_args, tmp_root=root / "kidtmp_stop1", guard_dir=guard_dir)
                _log_invocation(case, "stop_1", stop1_args, {}, p_stop1)
                assert p_stop1.returncode == 0, p_stop1.stderr
                assert "Stop angefordert" in p_stop1.stdout, p_stop1.stdout
                turns_used_after_stop1 = lab_runner.read_status(run_dir).turns_used
                # C3-Nachzug (02_AUFTRAG_C_ABSCHLUSS.md C3 'finale einzelne
                # Abrechnung/turns_used1 ... verbindlich assertieren'): EXAKT
                # 1, nicht nur "unveraendert zwischen stop1/stop2" (das
                # bestaetigt Idempotenz, nicht die korrekte absolute Zahl).
                assert turns_used_after_stop1 == 1, (
                    f"C3: turns_used nach stop1 muss exakt 1 sein (die eine in-flight-Antwort), "
                    f"ist {turns_used_after_stop1}"
                )

                # Wiederholter Stop -- idempotent, keine zweite Fortschrittswirkung
                # (R4: explizit auf UNVERAENDERTES turns_used geprueft, nicht
                # nur auf rc0+Textmarker).
                p_stop2 = _run_lab(stop2_args, tmp_root=root / "kidtmp_stop2", guard_dir=guard_dir)
                _log_invocation(case, "stop_2", stop2_args, {}, p_stop2)
                assert p_stop2.returncode == 0, p_stop2.stderr
                turns_used_after_stop2 = lab_runner.read_status(run_dir).turns_used
                assert turns_used_after_stop2 == turns_used_after_stop1, (
                    f"R4: wiederholter Stop hat turns_used veraendert: {turns_used_after_stop1} -> {turns_used_after_stop2}"
                )
            finally:
                release_event.set()  # die konkrete in-flight-Antwort darf jetzt zugestellt werden.
                try:
                    out1, err1 = proc1.communicate(timeout=20)
                except subprocess.TimeoutExpired:
                    proc1.kill()
                    out1, err1 = proc1.communicate(timeout=10)
                # End-Critic-Nacharbeit 2026-09-28, Befund 2: `args` darf hier NICHT
                # bereits "lab" enthalten -- `_log_invocation` haengt "lab" selbst
                # voran (analog allen anderen Aufrufstellen), sonst zeigt das
                # geloggte argv "lab" doppelt. `_h02_cwd`/pid werden real belegt
                # (proc1 laeuft explizit mit cwd=_REPO_ROOT, s.o.), statt null zu
                # bleiben.
                _controller_proc = subprocess.CompletedProcess(args=[], returncode=proc1.returncode, stdout=out1, stderr=err1)
                _controller_proc._h02_cwd = str(_REPO_ROOT)  # type: ignore[attr-defined]
                _log_invocation(
                    case, "controller",
                    ["start", "--data-dir", str(root), "--community", "nstop", "--profile", "api",
                     "--personas", "sniper,tech", "--max-requests", "5", "--max-seconds", "60",
                     "--max-usd", "5", "--max-idle-windows", "1"],
                    {"MMO_SIM_PERSONA_API_BASE_URL": base_url},
                    _controller_proc, pid=proc1.pid,
                )
        finally:
            srv.shutdown()
            srv.server_close()
            thread.join(timeout=5)

        assert proc1.returncode == 0, out1 + err1
        # Die eine in-flight-Antwort durfte gespeichert/verbucht werden;
        # KEINE weitere Modellanfrage/erfundener Abschluss danach.
        assert "Lobby-Tisch abgeschlossen" not in out1
        status_after = lab_runner.read_status(run_dir)
        assert (run_dir / "lab.stop").exists()

        # C3-Nachzug r2 (02_AUFTRAG_RESTABSCHLUSS.md C3 '... UND nach
        # Antwortfreigabe vergleichen und Nullfolgen assertieren; erlaubte
        # Stop-/Request-/Budgetaenderungen von unerlaubten Save-/Runden-/
        # Abschlussfolgen trennen'): Snapshot NACH Barrierefreigabe UND
        # Prozessende. ERLAUBT: `lab.stop` entsteht, `turns_used` 0->1
        # (die eine tatsaechlich verbuchte Antwort). NULLFOLGE (muss
        # UNVERAENDERT bleiben): Budgetobergrenze, publizierte Currents
        # (kein Save/keine neue Runde durch eine blosse "pause"-Antwort auf
        # die allererste Initiative), Reflexionen, Tische/Completion.
        authority_state_after_release = _authority_state_snapshot(run_dir, states_dir, _schema)
        sup.write_json(case / "authority-state-before-stop.json", authority_state_before_stop)
        sup.write_json(case / "authority-state-after-release.json", authority_state_after_release)
        assert authority_state_after_release["lab_stop_file_exists"] is True, (
            f"C3: erlaubte Aenderung fehlt -- lab.stop haette NACH Stop/Antwortfreigabe existieren muessen: "
            f"{authority_state_after_release}"
        )
        assert authority_state_after_release["turns_used"] == 1, (
            f"C3: erlaubte Aenderung falsch -- turns_used muss NACH Antwortfreigabe exakt 1 sein: "
            f"{authority_state_after_release}"
        )
        assert authority_state_after_release["max_usd"] == authority_state_before_stop["max_usd"], (
            f"C3: Nullfolge verletzt -- Budgetobergrenze (max_usd) darf sich durch Stop/Antwortfreigabe nicht "
            f"aendern: vorher={authority_state_before_stop['max_usd']} nachher={authority_state_after_release['max_usd']}"
        )
        assert authority_state_after_release["currents"] == authority_state_before_stop["currents"], (
            f"C3: Nullfolge verletzt -- unerlaubte Current-/Rundenaenderung nach Stop/Antwortfreigabe: "
            f"vorher={authority_state_before_stop['currents']} nachher={authority_state_after_release['currents']}"
        )
        assert authority_state_after_release["persona_states"] == authority_state_before_stop["persona_states"], (
            "C3: Nullfolge verletzt -- Persona-State mit realer Rundenzahl, Reflexionen "
            "oder current_save_version wurde nach Stop/Antwortfreigabe veraendert"
        )
        assert authority_state_after_release["protected_authority_hashes"] == authority_state_before_stop["protected_authority_hashes"], (
            "C3: Nullfolge verletzt -- Inhalt oder Inventar von States, Currents/Versionen, "
            "Completion, Tischen, Locks oder Reflexionsdatei wurde veraendert"
        )
        assert authority_state_after_release["reflections_count"] == authority_state_before_stop["reflections_count"] == 0, (
            f"C3: Nullfolge verletzt -- keine Reflexion haette an dieser einen blockierten Initiative-Antwort "
            f"entstehen duerfen: vorher={authority_state_before_stop['reflections_count']} "
            f"nachher={authority_state_after_release['reflections_count']}"
        )
        assert authority_state_after_release["tables"] == authority_state_before_stop["tables"] == {}, (
            f"C3: Nullfolge verletzt -- kein Tisch/keine Completion haette an dieser einen blockierten "
            f"Initiative-Antwort entstehen duerfen: vorher={authority_state_before_stop['tables']} "
            f"nachher={authority_state_after_release['tables']}"
        )
        # C3-Nachzug: finale einmalige Abrechnung EXAKT 1, kein Folgecall,
        # kein Reset (nicht None/0/>1).
        assert status_after is not None and status_after.turns_used == 1, (
            f"C3: finaler turns_used muss exakt 1 sein, ist {status_after.turns_used if status_after else None}"
        )

        # R4-Nachzug: genau EIN abgeschlossen verbuchter Persona-Request
        # (state=='accounted') fuer die eine in-flight-Barriere, kein
        # Folgecall danach -- ueber den echten Request-Ledger, nicht nur
        # 'kein Erfolgstext im stdout'.
        from mmo_sim.core import request_ledger
        records = request_ledger._all_records(run_dir)
        accounted = [r for r in records if r.get("state") == "accounted"]
        assert len(records) == 1, f"R4: genau 1 Requestdatensatz erwartet (die eine in-flight-Anfrage): {len(records)}"
        assert len(accounted) == 1, f"R4: genau 1 empfangen/verbucht (state=accounted) erwartet: {[r.get('state') for r in records]}"
        sup.write_json(case / "request-ledger-records.json", records)

        # G11 (B2-Nacharbeit): der EIGENE, vom Produkt-Ledger unabhaengige
        # Empfangszaehler des Handlers bestaetigt DIESELBE genau-einmalige
        # Ankunft ein zweites Mal, ueber einen komplett getrennten Pfad
        # (Socket-Empfang im Testprozess, nicht Produkt-internes Buchen).
        assert len(independent_receipts) == 1, (
            f"G11: eigener unabhaengiger Empfangszaehler erwartet genau 1 real empfangenen POST, "
            f"{len(independent_receipts)} erhalten: {independent_receipts}"
        )
        # C3-Nachzug r2 (01_REVIEW_H02.md §5/02_AUFTRAG_RESTABSCHLUSS.md C3
        # 'auch die vollstaendigen tatsaechlichen Requestbytes/den dekodierten
        # Body mit Bezug auf den vorhandenen Hash speichern'): der EINE
        # journalisierte Eintrag muss den tatsaechlich EMPFANGENEN,
        # dekodierten Requestbody tragen (nicht nur `body_sha256`+Laenge).
        assert isinstance(independent_receipts[0].get("body"), dict) and independent_receipts[0]["body"], (
            f"C3: N-STOP-Journal ohne vollstaendigen dekodierten Requestbody: {independent_receipts[0]}"
        )
        assert independent_receipts[0].get("body_sha256"), (
            f"C3: der dekodierte Body muss weiterhin unter Bezug auf den vorhandenen Rohbyte-Hash stehen "
            f"(body_sha256 fehlt): {independent_receipts[0]}"
        )
        # C3-Nachzug (01_REVIEW_H02.md §5 'kein Ausgangsbody, nur
        # Eingangsmetadaten'): der EINE journalisierte Eintrag muss jetzt
        # auch den tatsaechlich AUSGEGEBENEN Antwortbody tragen.
        assert independent_receipts[0]["egress_body"] is not None, (
            f"C3: N-STOP-Journal ohne Ausgangsbody: {independent_receipts[0]}"
        )
        assert independent_receipts[0]["egress_sha256"] is not None
        assert independent_receipts[0]["egress_sent_monotonic"] > independent_receipts[0]["received_monotonic"], (
            "C3: Ausgang muss zeitlich NACH dem Eingang liegen (Barriere hielt die Antwort tatsaechlich zurueck)"
        )
        sup.write_json(case / "independent-receiver-journal.json", independent_receipts)

        sup.write_json(case / "result.json", {
            "status": "PASS", "controller_returncode": proc1.returncode,
            "turns_used_after": status_after.turns_used if status_after else None,
            "ledger_records": len(records), "ledger_accounted": len(accounted),
            "independent_receipts": len(independent_receipts),
        })
        sup.write_json(case / "assertions.json", {"claims": [
            {"id": "N-STOP-inflight", "claim": "separater lab-stop-Prozess trifft echte in-flight-Personaantwort",
             "verified_by": "block_event.wait(timeout=20)==True (echter HTTP-Request blockiert im Handler)", "evidence": "controller stdout in invocations.json"},
            {"id": "N-STOP-readonly", "claim": "status/attach aus separaten Prozessen ohne Autoritaetsmutation (lab.status.json, lab.stop, locks.json, requests/, tables/, current_saves/)",
             "verified_by": "_authority_hash_snapshot(run_dir) vor/nach beiden Aufrufen identisch", "evidence": "authority-snapshots-read-only-proof.json"},
            {"id": "N-STOP-exactly-one", "claim": "genau 1 empfangene/verbuchte Anfrage, kein Folgecall",
             "verified_by": "request_ledger._all_records(run_dir): len==1, state=='accounted'", "evidence": "request-ledger-records.json"},
            {"id": "G11-independent-journal", "claim": "eigener vom Produkt-Ledger unabhaengiger Empfangszaehler bestaetigt ebenfalls genau 1 reale Ankunft",
             "verified_by": "len(independent_receipts)==1 (im Handler selbst gezaehlt, VOR Barrierefreigabe)", "evidence": "independent-receiver-journal.json"},
            {"id": "N-STOP-idempotent", "claim": "wiederholter Stop idempotent, keine zweite Fortschrittswirkung",
             "verified_by": "turns_used nach stop1 == turns_used nach stop2", "evidence": "result.json"},
            {"id": "N-STOP-no-false-close", "claim": "kein falscher Tischabschluss nach Stop",
             "verified_by": "'Lobby-Tisch abgeschlossen' not in out1", "evidence": "invocations.json (controller)"},
            {"id": "N-STOP-egress-and-exact-one", "claim": "genau EIN Ein- UND Ausgangsbody journalisiert, turns_used exakt 1 (vor UND nach Stop)",
             "verified_by": "independent_receipts[0].egress_body/egress_sha256 gesetzt, egress_sent_monotonic>received_monotonic; turns_used_after_stop1==1; status_after.turns_used==1",
             "evidence": "independent-receiver-journal.json, result.json"},
            {"id": "N-STOP-decoded-body", "claim": "voller dekodierter Requestbody am unabhaengigen Empfaenger, mit Bezug auf den vorhandenen Hash",
             "verified_by": "independent_receipts[0]['body'] ist ein nichtleeres dict, body_sha256 weiterhin vorhanden",
             "evidence": "independent-receiver-journal.json"},
            {"id": "N-STOP-authority-nullfolgen", "claim": "reale Current-/Versions-/Runden-/Reflexions-/Tisch-/Completion-/Budgetautoritaeten vor Stop UND nach Antwortfreigabe verglichen; erlaubte Aenderungen (lab.stop, turns_used 0->1) von Nullfolgen (Currents/Reflexionen/Tische/Budget unveraendert) getrennt",
             "verified_by": "authority_state_before_stop/after_release: currents/reflections_count/tables/max_usd identisch, lab_stop_file_exists False->True, turns_used==1",
             "evidence": "authority-state-before-stop.json, authority-state-after-release.json"},
        ]})


# ---------------------------------------------------------------------------
# C2: schmale PERMANENTE Regressionen fuer die fuenf in 01_REVIEW_H02.md §4
# konkret reproduzierten Fehlkontexte -- jede Probe belegt: VOR dem C2-
# Nachzug war der jeweilige Fehlkontext ein Erfolg (HTTP200/rc0), die JETZT
# erweiterten Validatoren/Fake-CLI-Checks lehnen denselben Fehlkontext
# kontrolliert ab (HTTP599/validation_error bzw. rc9). Direkte Aufrufe der
# permanenten Helperfunktionen (kein neuer Produktmutant, keine zusaetzliche
# volle Reise) -- 02_AUFTRAG_RESTPFLICHTEN.md C2: 'schmale permanente
# Helper-Regressionen in erlaubten Tests'.
# ---------------------------------------------------------------------------

def test_c2_probe1_http_consent_without_offer_current_phase_rejected():
    """01_REVIEW_H02.md §4 Probe 1: 'HTTP-Zustimmung ohne Angebot/Current/
    Phase, nur "tech spielt": HTTP200 Erfolg'. Der Validator fuer den
    Consent-Call (Index 0 in `_persona_validators_for_full_journey`) prueft
    seit dem C2-Nachzug zusaetzlich die woertlich transportierte
    `offer_id`. Ein Body mit NUR dem Personamarker (kein `offer_id=...` im
    user-Feld) muss jetzt einen Fehlertext liefern statt `None`."""
    validator = sup.make_persona_input_validator("tech", None, expected_offer_id="lobby-offer-real-window-tech-0")
    bad_body = {"messages": [
        {"role": "system", "content": 'tech spielt Kaede "TECH"'},
        {"role": "user", "content": "Ich stimme zu, ohne jeden Angebots-/Phasenbezug im Text."},
    ]}
    error = validator(bad_body)
    assert error is not None, "C2: fehlender offer_id-Bezug haette abgelehnt werden muessen (Review-Probe 1 war HTTP200)"
    assert "offer_id" in error
    # Gegenprobe: derselbe Validator akzeptiert einen Body MIT korrektem Bezug.
    good_body = {"messages": [
        {"role": "system", "content": 'tech spielt Kaede "TECH"'},
        {"role": "user", "content": 'ENTSCHEIDUNG offer_id=lobby-offer-real-window-tech-0 participant_id=tech decision=accept'},
    ]}
    assert validator(good_body) is None, "C2: Positivfall mit korrektem offer_id-Bezug darf nicht abgelehnt werden"


def test_c2_probe2_http_leader_import_wrong_table_missing_current_empty_prefix_rejected():
    """01_REVIEW_H02.md §4 Probe 2: 'HTTP-Leaderimport mit falschem Tisch,
    fehlendem Current und leerem Praefix: HTTP200 Erfolg'. Der Validator
    prueft seit dem C2-Nachzug zusaetzlich `table_view['table_id']`. Ein
    Wire mit FALSCHER `table_id` (aber sonst korrektem Personamarker/
    Praefixlaenge) muss abgelehnt werden."""
    validator = sup.make_persona_input_validator("tech", 0, expected_table_id="lobby-sniper-tech")
    wrong_table_view = {"table_id": "lobby-FALSCHER-TISCH", "sl_log": []}
    bad_user = "Leaderimport.\n\n[OEFFENTLICHE_TISCHSICHT]\n" + json.dumps(wrong_table_view, sort_keys=True)
    bad_body = {"messages": [
        {"role": "system", "content": 'tech spielt Kaede "TECH"'},
        {"role": "user", "content": bad_user},
    ]}
    error = validator(bad_body)
    assert error is not None, "C2: falsche table_id haette abgelehnt werden muessen (Review-Probe 2 war HTTP200)"
    assert "table_id" in error
    good_table_view = {"table_id": "lobby-sniper-tech", "sl_log": []}
    good_user = "Leaderimport.\n\n[OEFFENTLICHE_TISCHSICHT]\n" + json.dumps(good_table_view, sort_keys=True)
    good_body = {"messages": [{"role": "system", "content": 'tech spielt Kaede "TECH"'}, {"role": "user", "content": good_user}]}
    assert validator(good_body) is None, "C2: Positivfall mit korrekter table_id/Praefixlaenge darf nicht abgelehnt werden"


def test_c2_probe3_gm_expectation_only_in_old_message_rejected():
    """01_REVIEW_H02.md §4 Probe 3: 'GM-Erwartungstext nur in alter
    Nachricht, aktuelle Usernachricht falsch: HTTP200 Erfolg'. Der GM-
    Validator prueft seit dem C2-Nachzug NUR `messages[-1]` statt des
    gesamten serialisierten Bodys."""
    validator = sup.make_gm_leader_text_validator("Wir schliessen den HQ-Debrief kontrolliert ab.")
    body_old_message_only = {"messages": [
        {"role": "user", "content": "Wir schliessen den HQ-Debrief kontrolliert ab."},  # aeltere Nachricht -- korrekt
        {"role": "assistant", "content": "Verstanden."},
        {"role": "user", "content": "Etwas VOELLIG anderes -- die aktuelle Nachricht ist falsch."},
    ]}
    error = validator(body_old_message_only)
    assert error is not None, "C2: Erwartungstext nur in alter Nachricht haette abgelehnt werden muessen (Review-Probe 3 war HTTP200)"
    body_current_correct = {"messages": [
        {"role": "user", "content": "irrelevante alte Nachricht"},
        {"role": "user", "content": "Wir schliessen den HQ-Debrief kontrolliert ab."},
    ]}
    assert validator(body_current_correct) is None, "C2: Positivfall mit korrekter AKTUELLER Nachricht darf nicht abgelehnt werden"


def test_c2_probe4_fake_cli_initiative_without_persona_marker_rejected():
    """01_REVIEW_H02.md §4 Probe 4: 'Wirklich ausfuehrbare Fake-CLI ohne
    jede Persona im Initiativeinput: rc0 Erfolg'. Die Fake-CLI prueft seit
    dem C2-Nachzug auch bei der Initiative (Queue-Position 0) `expect_all`
    (s. `test_b_hybrid_profile_full_journey_single_process` C2-Nachzug-
    Kommentar) -- ein echter Subprozessaufruf OHNE Personamarker im STDIN
    muss jetzt rc9 (kontrollierter Fehler) liefern, nicht rc0."""
    case = sup.case_dir("C2_probe4_fake_cli_initiative_no_marker")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        capture = case / "cli-receipts.jsonl"
        fake_cli = sup.write_queued_fake_cli(root, capture_path=capture, queue=[
            {"result": '{"action": "pause"}', "expect_all": [_own_marker("sniper")]},
        ])
        # Eingang OHNE Personamarker -- reproduziert exakt den Review-Fehlkontext.
        p_bad = subprocess.run(
            [str(fake_cli)], input="[SYSTEM]\n(kein Personamarker hier)\n\n[USER]\nirgendein Initiativetext",
            text=True, capture_output=True, timeout=15,
        )
        assert p_bad.returncode == 9, (
            f"C2: Fake-CLI-Initiative ohne Personamarker haette rc9 liefern muessen (Review-Probe 4 war rc0): "
            f"rc={p_bad.returncode} stderr={p_bad.stderr!r}"
        )
        # Gegenprobe: derselbe Aufruf MIT Personamarker (neue Queue, da die
        # erste Queue durch den Fehlversuch NICHT konsumiert wurde).
        p_good = subprocess.run(
            [str(fake_cli)], input="[SYSTEM]\nsniper spielt Beispielcharakter\n\n[USER]\nirgendein Initiativetext",
            text=True, capture_output=True, timeout=15,
        )
        assert p_good.returncode == 0, f"C2: Positivfall mit Personamarker darf nicht abgelehnt werden: {p_good.stderr}"
        sup.write_json(case / "result.json", {
            "status": "PASS", "bad_rc": p_bad.returncode, "good_rc": p_good.returncode,
        })
        sup.write_json(case / "assertions.json", {"claims": [
            {"id": "C2-probe4", "claim": "Fake-CLI-Initiative ohne Personamarker jetzt kontrolliert abgelehnt (rc9), vorher rc0",
             "verified_by": "p_bad.returncode==9, p_good.returncode==0 (Gegenprobe)", "evidence": "cli-receipts.jsonl"},
        ]})


def test_c2_probe5_fake_cli_consent_with_persona_substring_only_rejected():
    """01_REVIEW_H02.md §4 Probe 5: 'Zustimmung mit blossem Persona-
    Substring: rc0 Erfolg'. Die Fake-CLI prueft seit dem C2-Nachzug beim
    Consent-Call zusaetzlich zum Personamarker die woertliche `offer_id`
    (s. `expect_by_idx[1]`-Erweiterung in
    `test_b_hybrid_profile_full_journey_single_process`)."""
    case = sup.case_dir("C2_probe5_fake_cli_consent_substring_only")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        capture = case / "cli-receipts.jsonl"
        offer_id = "lobby-offer-real-window-tech-0"
        fake_cli = sup.write_queued_fake_cli(root, capture_path=capture, queue=[
            {"result": "ENTSCHEIDUNG offer_id=egal participant_id=tech decision=accept",
             "expect_all": ["tech spielt", f"offer_id={offer_id}"]},
        ])
        # Persona-Substring vorhanden, offer_id FEHLT -- reproduziert den
        # Review-Fehlkontext (nur Persona-Substring geprueft).
        p_bad = subprocess.run(
            [str(fake_cli)], input="[SYSTEM]\ntech spielt Beispielcharakter\n\n[USER]\nZustimmung ohne jeden offer_id-Bezug.",
            text=True, capture_output=True, timeout=15,
        )
        assert p_bad.returncode == 9, (
            f"C2: Zustimmung ohne offer_id-Bezug haette rc9 liefern muessen (Review-Probe 5 war rc0): "
            f"rc={p_bad.returncode} stderr={p_bad.stderr!r}"
        )
        p_good = subprocess.run(
            [str(fake_cli)],
            input=f"[SYSTEM]\ntech spielt Beispielcharakter\n\n[USER]\nENTSCHEIDUNG offer_id={offer_id} participant_id=tech decision=accept",
            text=True, capture_output=True, timeout=15,
        )
        assert p_good.returncode == 0, f"C2: Positivfall mit korrektem offer_id-Bezug darf nicht abgelehnt werden: {p_good.stderr}"
        sup.write_json(case / "result.json", {"status": "PASS", "bad_rc": p_bad.returncode, "good_rc": p_good.returncode})
        sup.write_json(case / "assertions.json", {"claims": [
            {"id": "C2-probe5", "claim": "Fake-CLI-Zustimmung mit blossem Personasubstring (ohne offer_id) jetzt kontrolliert abgelehnt (rc9), vorher rc0",
             "verified_by": "p_bad.returncode==9, p_good.returncode==0 (Gegenprobe)", "evidence": "cli-receipts.jsonl"},
        ]})


# ---------------------------------------------------------------------------
# C2-Nachzug r1 (02_AUFTRAG_C_ABSCHLUSS.md C2, 01_REVIEW_H02.md §3): FUENF
# NEUE isolierte C2-Abweichungen, getrennt von den fuenf AELTEREN
# `test_c2_probe1..5`-Regressionen oben (die bleiben unveraendert erhalten).
# Jede hier isolierte Abweichung veraendert GENAU EIN Feld gegenueber einem
# ansonsten gesunden/zulaessigen Eingang und muss kontrolliert (HTTP599 bzw.
# rc9) scheitern; die jeweilige Gegenprobe mit demselben, aber korrigierten
# Feld muss weiterhin akzeptiert werden.
# ---------------------------------------------------------------------------

def test_c2_deviation1_consent_current_removed_rejected():
    """Isolierte Abweichung 1 (02_AUFTRAG_C_ABSCHLUSS.md C2 'Current bei
    Consent entfernt'): sonst gesunder Zustimmungsinput (korrekte Figur,
    korrekte woertliche `offer_id`), aber OHNE den vollstaendigen
    Current-Block -- muss abgelehnt werden."""
    offer_id = "lobby-offer-real-window-tech-0"
    validator = sup.make_persona_input_validator(
        "tech", None, expected_offer_id=offer_id, expected_current=sup.load_fixture_save("tech"),
    )
    bad_body = {"messages": [
        {"role": "system", "content": 'tech spielt Kaede "TECH"'},  # Figur korrekt, Current FEHLT.
        {"role": "user", "content": f"ENTSCHEIDUNG offer_id={offer_id} participant_id=tech decision=accept"},
    ]}
    error = validator(bad_body)
    assert error is not None, "C2-Deviation1: Consent ohne Current haette abgelehnt werden muessen"
    assert "Current" in error
    good_body = {"messages": [
        {"role": "system", "content": 'tech spielt Kaede "TECH"' + "\n" + sup.own_current_full_marker(sup.load_fixture_save("tech"))},
        {"role": "user", "content": f"ENTSCHEIDUNG offer_id={offer_id} participant_id=tech decision=accept"},
    ]}
    assert validator(good_body) is None, "C2-Deviation1: Positivfall mit vollstaendigem Current darf nicht abgelehnt werden"


def test_c2_deviation2_leader_import_current_removed_rejected():
    """Isolierte Abweichung 2 (C2 'Current bei Import entfernt'): sonst
    gesunder Leaderimport-Input (korrekte Figur, korrekter `table_id`/
    Praefix), aber OHNE Current-Block -- muss abgelehnt werden."""
    table_id = "lobby-sniper-tech"
    validator = sup.make_persona_input_validator(
        "tech", 0, expected_table_id=table_id, expected_current=sup.load_fixture_save("tech"),
    )
    table_view = {"table_id": table_id, "sl_log": []}
    user_text = "Leaderimport.\n\n[OEFFENTLICHE_TISCHSICHT]\n" + json.dumps(table_view, sort_keys=True)
    bad_body = {"messages": [
        {"role": "system", "content": 'tech spielt Kaede "TECH"'},  # Figur korrekt, Current FEHLT.
        {"role": "user", "content": user_text},
    ]}
    error = validator(bad_body)
    assert error is not None, "C2-Deviation2: Leaderimport ohne Current haette abgelehnt werden muessen"
    assert "Current" in error
    good_body = {"messages": [
        {"role": "system", "content": 'tech spielt Kaede "TECH"' + "\n" + sup.own_current_full_marker(sup.load_fixture_save("tech"))},
        {"role": "user", "content": user_text},
    ]}
    assert validator(good_body) is None, "C2-Deviation2: Positivfall mit vollstaendigem Current darf nicht abgelehnt werden"


def test_c2_deviation3_foreign_figure_rejected():
    """Isolierte Abweichung 3 (C2 'fremde Figur'): der `"tech spielt"`-
    Marker bleibt woertlich erhalten, aber Name/Callsign sind die einer
    ANDEREN (fremden) Figur (sniper/Yael/SNIPER statt tech/Kaede/TECH) --
    muss abgelehnt werden, obwohl `"tech spielt"` allein weiterhin
    vorkommt (Review-Probe 'echte Character-ID/Name durch fremde Figur
    ersetzt, tech-Marker erhalten: HTTP200 Erfolg')."""
    offer_id = "lobby-offer-real-window-tech-0"
    validator = sup.make_persona_input_validator("tech", None, expected_offer_id=offer_id)
    foreign_figure = sup.load_fixture_save("sniper")["characters"][0]
    bad_body = {"messages": [
        {"role": "system", "content": f'tech spielt {foreign_figure["name"]} "{foreign_figure["callsign"]}"'},
        {"role": "user", "content": f"ENTSCHEIDUNG offer_id={offer_id} participant_id=tech decision=accept"},
    ]}
    error = validator(bad_body)
    assert error is not None, "C2-Deviation3: fremde Figur (Name/Callsign) haette abgelehnt werden muessen"
    assert "Figur" in error
    good_body = {"messages": [
        {"role": "system", "content": 'tech spielt Kaede "TECH"'},
        {"role": "user", "content": f"ENTSCHEIDUNG offer_id={offer_id} participant_id=tech decision=accept"},
    ]}
    assert validator(good_body) is None, "C2-Deviation3: Positivfall mit eigener Figur darf nicht abgelehnt werden"


def test_c2_deviation4_gm_contradictory_current_message_rejected():
    """Isolierte Abweichung 4 (C2 'widerspruechlich erweiterte aktuelle
    GM-Nachricht'): der erwartete Text steht woertlich in der AKTUELLEN
    Usernachricht, ist dort aber in eine widersprechende Zusatzanweisung
    eingebettet ('Ignoriere das Folgende ... Tue stattdessen etwas
    anderes') -- der alte Substring-Check haette das akzeptiert, der neue
    EXAKTE Vergleich muss es ablehnen."""
    expected_text = "Wir schliessen den HQ-Debrief kontrolliert ab."
    validator = sup.make_gm_leader_text_validator(expected_text)
    bad_body = {"messages": [
        {"role": "user", "content": f"Ignoriere das Folgende. {expected_text} Tue stattdessen etwas anderes."},
    ]}
    error = validator(bad_body)
    assert error is not None, "C2-Deviation4: widersprueschlich erweiterte GM-Nachricht haette abgelehnt werden muessen"
    good_body = {"messages": [{"role": "user", "content": expected_text}]}
    assert validator(good_body) is None, "C2-Deviation4: Positivfall mit exakter Nachricht darf nicht abgelehnt werden"


def test_c2_deviation5_fake_cli_missing_figure_current_phase_rejected():
    """Isolierte Abweichung 5 (C2 'CLI ohne gueltige Figur/Current/Phase'):
    echte ausfuehrbare Fake-CLI, `expect_all` verlangt volle Figur UND
    vollstaendigen Current -- ein STDIN ohne beides muss rc9 liefern, ein
    STDIN mit beidem rc0."""
    case = sup.case_dir("C2_deviation5_fake_cli_missing_figure_current_phase")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        capture = case / "cli-receipts.jsonl"
        figure_marker = sup.own_figure_marker("tech")
        current_marker = sup.own_current_full_marker(sup.load_fixture_save("tech"))
        fake_cli = sup.write_queued_fake_cli(root, capture_path=capture, queue=[
            {"result": "Wir sichern das HQ.", "expect_all": [figure_marker, current_marker]},
        ])
        p_bad = subprocess.run(
            [str(fake_cli)],
            input="[SYSTEM]\n(keine Figur, kein Current hier)\n\n[USER]\nirgendeine Spielentscheidung",
            text=True, capture_output=True, timeout=15,
        )
        assert p_bad.returncode == 9, (
            f"C2-Deviation5: Fake-CLI ohne Figur/Current haette rc9 liefern muessen: "
            f"rc={p_bad.returncode} stderr={p_bad.stderr!r}"
        )
        p_good = subprocess.run(
            [str(fake_cli)],
            input=f"[SYSTEM]\n{figure_marker}\n{current_marker}\n\n[USER]\nirgendeine Spielentscheidung",
            text=True, capture_output=True, timeout=15,
        )
        assert p_good.returncode == 0, f"C2-Deviation5: Positivfall mit Figur+Current darf nicht abgelehnt werden: {p_good.stderr}"
        sup.write_json(case / "result.json", {"status": "PASS", "bad_rc": p_bad.returncode, "good_rc": p_good.returncode})
        sup.write_json(case / "assertions.json", {"claims": [
            {"id": "C2-deviation5", "claim": "Fake-CLI ohne Figur/Current jetzt kontrolliert abgelehnt (rc9)",
             "verified_by": "p_bad.returncode==9, p_good.returncode==0 (Gegenprobe)", "evidence": "cli-receipts.jsonl"},
        ]})


# ---------------------------------------------------------------------------
# C3: exklusive Fallreservierung + echter Kind-Guard-/Dependency-Nachweis.
# ---------------------------------------------------------------------------

def test_c3_exclusive_case_dir_reservation_collision():
    """01_REVIEW_H02.md §5: 'ruft case_dir zweimal auf demselben frisch
    reservierten eigenen Ziel auf: zweiter Aufruf akzeptiert, statt
    Kollisionstop'. Seit dem C3-Nachzug (`case_dir`, `_h02_vollreise_
    support.py`) wirft eine zweite Reservierung `CaseDirCollisionError`,
    OHNE die Bytes der ersten Reservierung zu veraendern. Setzt
    `H02_EVIDENCE_DIR` fuer die Dauer der Probe explizit selbst (mit
    Restore im finally), damit BEIDE `case_dir()`-Aufrufe garantiert
    denselben `evidence_root()` treffen -- unabhaengig davon, ob die
    aeussere Testausfuehrung diese Variable gesetzt hat."""
    prior = os.environ.get("H02_EVIDENCE_DIR")
    with tempfile.TemporaryDirectory() as td:
        os.environ["H02_EVIDENCE_DIR"] = td
        try:
            first = sup.case_dir("C3_exclusive_probe_target")
            marker = first / "original.txt"
            marker.write_text("original-bytes", encoding="utf-8")
            original_hash = sup.sha256_of(marker)
            collided = False
            try:
                sup.case_dir("C3_exclusive_probe_target")
            except sup.CaseDirCollisionError:
                collided = True
            assert collided, "C3: zweite Reservierung desselben Fallnamens haette FAIL liefern muessen (Review-Befund: akzeptiert)"
            assert sup.sha256_of(marker) == original_hash, "C3: fehlgeschlagene zweite Reservierung darf Altbytes nicht veraendern"
            # Ergebnis- und Assertion-Belege liegen bewusst NEBEN dem
            # kollidierenden Zielverzeichnis (eigener Evidenzordner), nicht
            # darin -- eine dritte `case_dir`-Reservierung fuer den Beleg
            # selbst waere unnoetiger Scopezuwachs.
            report_dir = Path(td) / "_c3_probe_report"
            report_dir.mkdir(parents=True, exist_ok=True)
            sup.write_json(report_dir / "result.json", {
                "status": "PASS", "collision_raised": collided, "original_bytes_unchanged": True,
            })
        finally:
            if prior is None:
                os.environ.pop("H02_EVIDENCE_DIR", None)
            else:
                os.environ["H02_EVIDENCE_DIR"] = prior


def test_c3_real_child_guard_and_dependency_proof():
    """01_REVIEW_H02.md §5: 'Das minimale Kind-Environment existiert, aber
    die tatsaechliche Guard-/Dependencypruefung der realen Kinder/Fake-CLI
    ist nicht in den Dauertests belegt. Der aeussere Helper-Preflight ist
    dafuer kein Ersatz.' Spawnt ueber `sup.prove_child_guard_and_dependency`
    einen ECHTEN Kindprozess mit demselben `minimal_lab_env`/PYTHONPATH-
    Aufbau wie jeder reale `lab`-Subprozess und laesst IHN SELBST pruefen,
    ob der Loopback-Guard in seinem EIGENEN Prozess wirksam ist (nicht nur
    im Elternprozess/Helper-Preflight).

    C3-Nachzug r1 (01_REVIEW_H02.md §5 'Seine Probe wuerde bei fehlendem
    Hook sogar die externe Adresse mit socket.connect versuchen. Das muss
    vor einem solchen Aufruf rein lokal scheitern.'): zusaetzliche Pruefung
    `guard_hook_loaded_locally` -- MUSS in diesem gesunden Fall True sein
    (Guard tatsaechlich geladen), BEVOR der externe Verbindungsversuch
    ueberhaupt unternommen wird.

    C3-Nachzug r2 (01_REVIEW_H02.md §5 'prove_child_guard_and_dependency
    meldet bei fehlendem jsonschema weiterhin ok:true'): dieser Aufruf
    uebergibt bewusst KEIN `schema_dependency_dir` (derselbe Aufbau wie
    bisher) -- das Kind hat hier also tatsaechlich KEIN sichtbares
    `jsonschema` (frisches leeres HOME, keine Sichtbarkeitskopie im
    PYTHONPATH). Die Pruefung unten sperrt jetzt EXAKT diesen ehrlichen
    negativen Zustand fest (`ok is False`/`available is False`) statt nur
    die Schluesselpraesenz zu pruefen -- der alte Test haette den
    Review-Bug (beide Zweige meldeten `ok:True`) nicht gefangen."""
    case = sup.case_dir("C3_real_child_guard_dependency")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        guard_dir = sup.write_loopback_guard(root / "guard")
        result = sup.prove_child_guard_and_dependency(tmp_root=root / "kidtmp", guard_dir=guard_dir)
        sup.write_json(case / "child-guard-proof.json", result)
        assert result["returncode"] == 0, f"C3: echter Kindprozess (Guard-Probe) rc!=0: {result}"
        assert isinstance(result["pid"], int) and result["pid"] > 0, f"C3: kein echter Kind-PID erfasst: {result}"
        checks = result["report"].get("checks", {})
        assert checks.get("guard_hook_loaded_locally", {}).get("ok") is True, (
            f"C3: lokale Guard-Hook-Identitaetspruefung schlug fehl (VOR jedem externen Verbindungsversuch): {checks}"
        )
        assert checks.get("guard_blocks_nonloopback", {}).get("ok") is True, (
            f"C3: Guard im ECHTEN Kindprozess blockiert Nicht-Loopback-Ziel nicht: {checks}"
        )
        assert checks.get("guard_allows_loopback", {}).get("ok") is True, (
            f"C3: Guard im ECHTEN Kindprozess blockiert faelschlich Loopback: {checks}"
        )
        # jsonschema ist laut Produktcode optional (Fallback) -- hier wird
        # nur der EHRLICHE Ladezustand belegt, kein Hardblock erzwungen.
        # Diese informative Pruefung ersetzt NICHT den strengeren
        # fail-closed-Testvorbehalt, s. `test_c3_dependency_missing_fails_
        # closed_before_functional_test`. C3-Nachzug r2: OHNE
        # Sichtbarkeitskopie MUSS der ehrliche Ladezustand hier False sein
        # (Review-Bug-Regression: vorher `ok:True` in BEIDEN Faellen).
        dep_check = checks.get("jsonschema_dependency", {})
        assert dep_check.get("ok") is False and dep_check.get("available") is False, (
            f"C3: Kind ohne Dependency-Sichtbarkeitskopie haette jsonschema_dependency.ok/available==False "
            f"melden muessen (Review-Bug-Regression 'ok:true trotz fehlender Dependency'): {dep_check}"
        )
        sup.write_json(case / "result.json", {"status": "PASS", "child_pid": result["pid"], "checks": checks})
        sup.write_json(case / "assertions.json", {"claims": [
            {"id": "C3-child-guard", "claim": "echter Kindprozess (nicht Parent-Preflight) belegt Guard-Wirksamkeit + Dependency-Status mit realem PID; lokale Hook-Identitaet VOR externem Verbindungsversuch",
             "verified_by": "result['pid'] echter Popen.pid, checks.guard_hook_loaded_locally.ok==True, checks.guard_blocks_nonloopback.ok==True, checks.guard_allows_loopback.ok==True",
             "evidence": "child-guard-proof.json"},
        ]})


def test_c3_dependency_missing_fails_closed_before_functional_test():
    """C3-Nachzug (02_AUFTRAG_C_ABSCHLUSS.md C3, 01_REVIEW_H02.md §5): 'Der
    neue Guard-Test ... erklaert den ImportError von jsonschema ausdruecklich
    mit ok:True. ... Die optionale Produktfallback-Semantik hebt den
    strengeren Ausfuehrungsvorbehalt dieses Tests nicht auf.' Zwei echte
    Kindprozesse ueber `sup.prove_child_dependency_fail_closed`:

    1) `deny_dependency=True` (das UNVERAENDERTE reale `minimal_lab_env`-
       Muster -- frisches leeres `HOME`, wie es JEDER echte Lab-/Fake-CLI-
       Kindprozess bereits erhaelt; `jsonschema` liegt auf diesem Host nur
       im HOME-gebundenen User-Site-Verzeichnis und ist deshalb bereits
       ohne jede Praeparation unsichtbar, s. Docstring von
       `prove_child_dependency_fail_closed`): MUSS
       `BLOCKED_MISSING_DEPENDENCY`/`functional_test_executed=False`/
       `returncode=3` liefern -- KEIN `ok=True`, KEIN fachlicher
       `validate_state()`-Aufruf.
    2) `deny_dependency=False` (Gegenprobe: `_copy_dependency_visibility`
       macht das REAL vorhandene `jsonschema`-Package ueber eine exklusive
       Scratch-Kopie + `PYTHONPATH` sichtbar, mit Hashbeleg, keine
       Installation/kein HOME-/PATH-Eingriff): MUSS `status=OK`/
       `functional_test_executed=True` liefern -- beweist, dass GENAU
       diese Sichtbarkeitsaenderung (nicht ein zufaelliger Ambient-Zustand)
       die beobachtete Verfuegbarkeit steuert."""
    case = sup.case_dir("C3_dependency_missing_fails_closed")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        sample_state = {
            "v": 2, "persona_key": "tech", "real_name": "tech",
            "plays_char": {"save_file": "tech.json", "character_id": "CHR-TECH-001", "name": "Kaede", "callsign": "TECH"},
            "rounds_played": 0, "archetype": "SIMULIERT", "play_style": "SIMULIERT", "charwunsch": "SIMULIERT/DEMO",
        }
        missing = sup.prove_child_dependency_fail_closed(
            tmp_root=root / "kidtmp-missing", repo_root=_REPO_ROOT, schema_path=sup._SCHEMA,
            sample_state=sample_state, deny_dependency=True,
        )
        sup.write_json(case / "dependency-missing.json", missing)
        assert missing["report"].get("jsonschema_available") is False, (
            f"C3: -S-Kindprozess haette jsonschema NICHT importieren duerfen koennen: {missing}"
        )
        assert missing["report"].get("status") == "BLOCKED_MISSING_DEPENDENCY", (
            f"C3: fehlendes jsonschema haette BLOCKED_MISSING_DEPENDENCY liefern muessen, kein ok=True: {missing}"
        )
        assert missing["report"].get("functional_test_executed") is False, (
            f"C3: fachlicher validate_state()-Aufruf haette NICHT ausgefuehrt werden duerfen: {missing}"
        )
        assert missing["returncode"] == 3, f"C3: rc!=3 bei fehlender Dependency: {missing}"
        assert isinstance(missing["pid"], int) and missing["pid"] > 0, f"C3: kein echter Kind-PID: {missing}"

        available = sup.prove_child_dependency_fail_closed(
            tmp_root=root / "kidtmp-available", repo_root=_REPO_ROOT, schema_path=sup._SCHEMA,
            sample_state=sample_state, deny_dependency=False,
        )
        sup.write_json(case / "dependency-available.json", available)
        assert available["report"].get("jsonschema_available") is True, f"C3: Gegenprobe ohne -S sollte jsonschema sehen: {available}"
        assert available["report"].get("status") == "OK" and available["report"].get("functional_test_executed") is True, (
            f"C3: Gegenprobe mit verfuegbarer Dependency haette den fachlichen Test ausfuehren muessen: {available}"
        )
        assert available["returncode"] == 0, f"C3: Gegenprobe rc!=0: {available}"

        sup.write_json(case / "result.json", {
            "status": "PASS", "missing_status": missing["report"].get("status"),
            "available_status": available["report"].get("status"),
        })
        sup.write_json(case / "assertions.json", {"claims": [
            {"id": "C3-dependency-fail-closed",
             "claim": "fehlende jsonschema-Dependency im echten Kind-Env blockiert VOR dem fachlichen Test (BLOCKED_MISSING_DEPENDENCY, kein ok=True); Gegenprobe mit verfuegbarer Dependency fuehrt den Test aus",
             "verified_by": "missing.report.status==BLOCKED_MISSING_DEPENDENCY, functional_test_executed=False, rc=3; available.report.status==OK, functional_test_executed=True, rc=0",
             "evidence": "dependency-missing.json, dependency-available.json"},
        ]})


if __name__ == "__main__":
    import traceback

    tests = [
        test_a_api_profile_full_journey_two_processes,
        test_b_hybrid_profile_full_journey_single_process,
        test_y_n1_hybrid_cli_failure_no_api_fallback,
        test_y_n2_api_error_401_no_fallback,
        test_y_n3_missing_gm_output_bound_blocks_under_hard_budget,
        test_y_n4_test_authority_blocks_non_loopback_route,
        test_n_human_waiting_hold_no_ai_takeover,
        test_n_stop_separate_process_in_flight_barrier,
        test_c2_probe1_http_consent_without_offer_current_phase_rejected,
        test_c2_probe2_http_leader_import_wrong_table_missing_current_empty_prefix_rejected,
        test_c2_probe3_gm_expectation_only_in_old_message_rejected,
        test_c2_probe4_fake_cli_initiative_without_persona_marker_rejected,
        test_c2_probe5_fake_cli_consent_with_persona_substring_only_rejected,
        test_c1_corrupted_ledger_evidence_rejected,
        test_c2_deviation1_consent_current_removed_rejected,
        test_c2_deviation2_leader_import_current_removed_rejected,
        test_c2_deviation3_foreign_figure_rejected,
        test_c2_deviation4_gm_contradictory_current_message_rejected,
        test_c2_deviation5_fake_cli_missing_figure_current_phase_rejected,
        test_c3_exclusive_case_dir_reservation_collision,
        test_c3_real_child_guard_and_dependency_proof,
        test_c3_dependency_missing_fails_closed_before_functional_test,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
            passed += 1
        except Exception:
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed}/{len(tests)} Tests bestanden.")
    sys.exit(0 if failed == 0 else 1)
