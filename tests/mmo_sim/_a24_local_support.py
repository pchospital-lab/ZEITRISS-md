#!/usr/bin/env python3
"""
tests/mmo_sim/_a24_local_support.py — gemeinsame Helper/Fixtures fuer
`test_a24_local_two_humans_2026_10_01.py` (A24-Nachweisauftrag, 2026-10-01).

Neues Testartefakt, keine Produktdatei. Baut NUR Testinfrastruktur
(Loopback-Receiver fuer Persona-API UND GM/SL, reale ausfuehrbare Fake-CLI
fuer das Hybrid-Profil, Community-/Registry-/Onboarding-Bootstrap ueber
vorhandene Produktfunktionen, echter Subprozess-Dispatch von
`scripts/mmo_sim.py`). Kein Testhelper hier erzeugt Angebot/Tisch/Consent/
Save direkt in Produktdateien -- das macht ausschliesslich der echte
Produktweg (`scripts/mmo_sim.py --participant ... --data-dir ...` als echter
Subprozess, s. `run_process()`).

Reihenfolge-Hinweis (wichtig fuer Aufrufer dieser Datei): `core.store.
create_table_from_offer_log` bildet `table.members` als `sorted(leader-id
UNION angenommene Gaeste)` -- NICHT Token-Reihenfolge. Menschliche
Registry-IDs (`p<16 hex>`, `core.identity.new_participant_id`) sortieren
IMMER zwischen den sechs KI-Persona-Fixturenamen (`cqb`,`face`,`medic`,
`pyro`,`sniper`,`tech` -- alle ohne 'p' als Erstbuchstaben ausser keiner)
und den restlichen Namen alphabetisch ein. Aufrufer berechnen die
tatsaechliche Reihenfolge ueber `sorted_guest_order()` (unten), NIEMALS
hartkodiert."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import selectors
import stat
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

# G6-O: nur LESENDER Re-Use des bereits bestehenden, unveraenderten Guard-
# Bausteins (dieselbe Importweise wie `_a23_vorlauf_support.py: import
# _h02_vollreise_support as sup`) -- `_h02_vollreise_support.py` selbst
# bleibt bytegleich, hier NIE geschrieben.
import _h02_vollreise_support as _h02sup  # noqa: E402

from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.community_bootstrap import bootstrap_community  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, COMPLETION_MARKER  # noqa: E402
from mmo_sim.registry.participants import ApplicationRecordRef, ParticipantRegistry  # noqa: E402

MMO_SIM = _REPO_ROOT / "scripts" / "mmo_sim.py"
SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
FIX = _REPO_ROOT / "internal" / "qa" / "harness" / "lobby" / "fixtures" / "saves"
SIX_PERSONAS = ("sniper", "tech", "cqb", "face", "medic", "pyro")


# --------------------------------------------------------------------------
# Evidenz
# --------------------------------------------------------------------------

def evidence_root() -> Path:
    """`A24_EVIDENCE_DIR` (neue, dokumentierte Testausgabevariable, analog
    H02s `H02_EVIDENCE_DIR`) -- ohne Angabe ein eigener Temp-Ordner, damit
    `run_all.py` diesen Test ohne externe Vorbereitung findet/ausfuehrt."""
    raw = os.environ.get("A24_EVIDENCE_DIR")
    root = Path(raw) if raw else Path(tempfile.mkdtemp(prefix="a24_local_evidence_"))
    root.mkdir(parents=True, exist_ok=True)
    return root


def case_dir(name: str) -> Path:
    d = evidence_root() / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "before").mkdir(exist_ok=True)
    (d / "after").mkdir(exist_ok=True)
    return d


def sha256_of(path: Path) -> "str | None":
    if not path.exists() or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hash_tree(root: Path) -> dict:
    out: dict[str, str] = {}
    if not root.exists():
        return out
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out[str(p.relative_to(root))] = sha256_of(p)
    return out


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")


def read_jsonl(path: Path) -> list:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


# --------------------------------------------------------------------------
# Community-/Registry-/Onboarding-Bootstrap (nur vorhandene Produktfunktionen)
# --------------------------------------------------------------------------

_PERSONA_ARCHETYPES = {
    "sniper": "Praeziser Einzelgaenger", "tech": "Analytischer Planer", "cqb": "Aggro-Draufgaenger",
    "face": "Sozialer Vermittler", "medic": "Vorsichtiger Absicherer", "pyro": "Chaotischer Improvisierer",
}


def bootstrap_six_persona_community(root: Path, community_id: str, persona_keys=SIX_PERSONAS):
    """Große bestaetigte synthetische Community (02_AUFTRAG_A24.md
    'Gemeinsamer Aufbau'): mindestens sechs unterscheidbare KI-Personas ueber
    die vorhandene `bootstrap_community`-Produktfunktion. Reine Roster-
    Anlage -- die tatsaechliche Figur (v7-Save) je Persona kommt erst ueber
    `make_ready()`."""
    states_dir = root / "states"
    run_dir = root / "run"
    onboarding_dir = root / "onboarding"
    catalog_dir = root / "catalog"
    states_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    ps_store = PersonaStateStore(schema_path=SCHEMA)
    community_dir = run_dir / "community"
    drafts = {
        pk: {
            "real_name": pk, "archetype": _PERSONA_ARCHETYPES.get(pk, "SIMULIERT"),
            "play_style": "SIMULIERT/DEMO", "charwunsch": "SIMULIERT/DEMO (A24-Testfixture).",
            "plays_char": {
                "save_file": "NOCH_NICHT_ERSCHAFFEN", "character_id": "NOCH_NICHT_ERSCHAFFEN",
                "name": "NOCH_NICHT_ERSCHAFFEN", "callsign": "NOCH_NICHT_ERSCHAFFEN",
            },
        }
        for pk in persona_keys
    }
    result = bootstrap_community(community_dir, community_id, 1, drafts, ps_store, states_dir, today="2026-10-01")
    return {
        "schema": SCHEMA, "states_dir": states_dir, "run_dir": run_dir,
        "onboarding_dir": onboarding_dir, "catalog_dir": catalog_dir, "bootstrap": result,
    }


def make_ready(onboarding_dir: Path, states_dir: Path, run_dir: Path, persona_key: str) -> str:
    """AI-Persona erhaelt ihre volle, bereits abgeschlossene v7-Figur ueber
    den Produktweg (`onboarding` + `core.store.publish_current_save`) --
    identisches Muster wie die bestehenden permanenten H02-Tests."""
    save = load_fixture_save(persona_key)
    chrono_id = save["characters"][0]["char_id"]
    ps_store = PersonaStateStore(schema_path=SCHEMA)
    onboarding.start_or_resume(onboarding_dir, persona_key)
    onboarding.complete_with_save(onboarding_dir, persona_key, save, ZeitrissHarvestValidator(), chrono_id)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, persona_key, chrono_id, save)
    core_store.publish_current_save(run_dir, persona_key, save, ps_store, states_dir)
    return chrono_id


def load_fixture_save(persona_key: str) -> dict:
    return json.loads((FIX / f"{persona_key}.json").read_text(encoding="utf-8"))


def synthetic_human_save(char_id: str, name: str, callsign: str) -> dict:
    """A01/11 §8: eigene vollstaendige, von allen KI-Fixturen UND vom
    jeweils anderen Menschen unterschiedene v7-Save-Identitaet fuer einen
    menschlichen Community-Slot -- dasselbe v7-Schema wie die KI-Fixtures,
    nur eigener char_id/name/callsign."""
    return {
        "v": 7, "save_id": f"fixture-{char_id.lower()}-initial-001",
        "_fixture_note": "SIMULIERT/FIXTURE (A24-Nachweis, menschlicher Teilnehmer)",
        "characters": [{"char_id": char_id, "id": char_id, "name": name, "callsign": callsign}],
    }


def register_human(registry_dir: Path, display_name: str):
    """Echte registrierte menschliche Teilnehmeridentitaet (A01, 02_AUFTRAG_A24.md
    'zwei registrierte menschliche Identitaeten mit eigenen gueltigen Figuren/
    record_refs') -- die ID kommt aus der Registry, kein erfundener fester Wert."""
    registry = ParticipantRegistry(registry_dir)
    return registry.register_participant(kind="human", display_name=display_name)


def onboard_human_figure(
    registry_dir: Path, participant_id: str, onboarding_dir: Path, states_dir: Path, run_dir: Path,
    char_id: str, name: str, callsign: str,
) -> dict:
    """Stattet eine ueber `register_human()` registrierte menschliche
    Identitaet mit einer eigenen, abgeschlossenen v7-Figur aus (derselbe
    Onboarding-/Publish-Produktweg wie jede KI-Persona) UND verbindet
    Registry-Seite und Figur via `add_record_ref` (echter `record_ref`,
    nicht nur impliziter Chrononaut-Bezug)."""
    registry = ParticipantRegistry(registry_dir)
    save = synthetic_human_save(char_id, name, callsign)
    chrono_id = save["characters"][0]["char_id"]
    ps_store = PersonaStateStore(schema_path=SCHEMA)
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), chrono_id)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, participant_id, chrono_id, save)
    core_store.publish_current_save(run_dir, participant_id, save, ps_store, states_dir)
    registry.add_record_ref(participant_id, ApplicationRecordRef(
        record_id=chrono_id, schema="zeitriss-v7", version="7", owner_participant_id=participant_id,
    ))
    return {"participant": registry.load_participant(participant_id), "save": save, "char_id": chrono_id}


# A24 R3 (02_AUFTRAG_R2_R3.md §R3 "Fremde/Bystander/Registry/Katalog/
# Onboarding/uebrige Figuren ... vor/nach assertieren"): die drei
# SIX_PERSONAS, die KEIN Test hier `make_ready()` aufruft -- bleiben ohne
# Onboarding/Current, muessen also vor UND nach jeder Runde unberuehrt
# (keine states-Datei) bleiben.
BYSTANDER_PERSONAS = tuple(sorted(pk for pk in SIX_PERSONAS if pk not in ("sniper", "tech", "medic")))


def capture_protected_authorities(states_dir: Path, registry_dir: Path, onboarding_dir: Path, catalog_dir: Path) -> dict:
    """A24 R3: Registry/Onboarding/Katalog werden von einer tatsaechlichen
    Rundenausfuehrung (`_cmd_local_round`/`_cmd_local_round_setup`) NIE
    geschrieben (nur in der Testvorbereitung, s. `register_human`/
    `onboard_human_figure`/`make_ready` oben) -- ein voller Vorher/Nachher-
    Hashvergleich ist daher KEINE schwache Teilmengenpruefung, sondern die
    tatsaechliche Autoritaetserwartung. `bystanders` sichert zusaetzlich,
    dass die drei NICHT an der Runde beteiligten SIX_PERSONAS (`BYSTANDER_
    PERSONAS`) weiterhin keine eigene Current-/State-Datei besitzen."""
    return {
        "registry": hash_tree(registry_dir),
        "onboarding": hash_tree(onboarding_dir),
        "catalog": hash_tree(catalog_dir),
        "bystanders": {pk: sha256_of(states_dir / f"{pk}.json") for pk in BYSTANDER_PERSONAS},
    }


def sorted_guest_order(leader_id: str, guest_ids) -> list:
    """Repliziert `core.store.create_table_from_offer_log`s
    `members = sorted({leader} | wants)` MINUS Leader -- die tatsaechliche
    Reihenfolge der Gast-Import-/Poll-/Reflexionsturns. Niemals hartkodiert,
    da menschliche Registry-IDs zur Laufzeit zufaellig erzeugt werden."""
    members = sorted({leader_id, *guest_ids})
    return [m for m in members if m != leader_id]


def sorted_table_members(leader_id: str, guest_ids) -> list:
    return sorted({leader_id, *guest_ids})


def compute_table_id(leader_id: str, invited_ids_in_token_order) -> str:
    """Repliziert `TuiSession._cmd_local_round`s `table_id`-Formel
    (`mmo_sim/ui/tui.py`): `local-<leader>` + `-` + sortierte, mit `-`
    verbundene `invited_ids` (NICHT Tokenreihenfolge, s. Quelle)."""
    if not invited_ids_in_token_order:
        return f"local-{leader_id}"
    return f"local-{leader_id}-" + "-".join(sorted(invited_ids_in_token_order))


def invitation_offer_id(leader_id: str, token_targets) -> str:
    """Repliziert die `invitation_offer_id`-Formel aus `_cmd_local_round`:
    `invite-<leader>-` + sortierte Zielnamen (Personas ohne `persona:`-
    Praefix, Menschen roh)."""
    return "invite-" + leader_id + "-" + "-".join(sorted(token_targets))


def lead_invite_offer_id(leader_persona_id: str, calling_human_id: str) -> str:
    return f"lead-invite-{leader_persona_id}-{calling_human_id}"


def accept_text(offer_id: str, participant_id: str, explanation: str = "Ich bin dabei.") -> str:
    """Woertliche I1-Kontrollform (`adapters/base.py:decision_contract_instruction`),
    identisch zum bereits bestehenden Muster in `test_m3_tui.py`/
    `e2e_real_subprocess_dialog.py`."""
    return (
        f"ENTSCHEIDUNG offer_id={offer_id} participant_id={participant_id} "
        f"decision=accept explanation={explanation}"
    )


def reject_text(offer_id: str, participant_id: str, explanation: str = "Ich lehne ab.") -> str:
    return (
        f"ENTSCHEIDUNG offer_id={offer_id} participant_id={participant_id} "
        f"decision=reject explanation={explanation}"
    )


# --------------------------------------------------------------------------
# G6 (02_AUFTRAG_G6.md "unabhaengige Erwartungsbindung"): beide Testdoubles
# (HTTP UND die Fake-CLI weiter unten) validieren VOR jeder Erfolgsausgabe
# den tatsaechlichen oeffentlichen Tischkontext/eigenen Current/Angebotsbezug
# der eingehenden Anfrage GEGEN eine unabhaengig AM SETUP gebaute Erwartung
# (`expected_context_for_case`, unten) -- NICHT gegen eine aus demselben zu
# pruefenden Input zurueckabgeleitete Form. Die frueher hier verwendete
# reine SELBSTKONSISTENZPRUEFUNG (table_id aus leader+members DES ANFRAGE-
# WERTS selbst rekonstruiert, sl_log gegen zwei feste Fallback-Narrative-
# Templates) akzeptierte ein komplett erfundenes, aber intern konsistentes
# Tripel (dokumentierter Fund A, 01_REVIEW_A24.md) -- dasselbe formal
# "konsistente" Fremdtripel wird jetzt abgelehnt, weil `table_id`/`leader`/
# `members` direkt gegen die unabhaengig im Testsetup berechneten Werte
# verglichen werden, und `sl_log`-Inhalte gegen das tatsaechlich beobachtete
# GM-Ausgangsjournal (`gm_receipts`, von `SequencedHTTPServer`s GM-Seite
# NACH echtem Write/Flush gefuehrt), statt gegen statische Erzaehltexte.
# Gesunde, unveraenderte Anfragen (kein Marker vorhanden ODER alle
# gefundenen Bloecke/Currents/Angebotsbezuege konsistent zur unabhaengigen
# Erwartung) bleiben unveraendert bedient -- kein `expected is None -> True`.
# --------------------------------------------------------------------------

_OEFFENTLICHE_TISCHSICHT_MARKER = "[OEFFENTLICHE_TISCHSICHT]\n"
_OWN_CURRENT_MARKER = "Eigener aktueller Spielstand (Current, vollstaendig): "
_OFFER_ID_RE = re.compile(r'offer_id[=:]\s*"?([^\s",}]+)')


def _extract_table_view(text: str):
    """Liefert den geparsten `[OEFFENTLICHE_TISCHSICHT]`-Block aus einem
    beliebigen Anfrage-/Stdin-Text, `None` ohne Marker (z.B. reine
    GM-Anfragen ohne table_view -- kein Fehlalarm), `False` bei vorhandenem
    Marker mit nicht mehr gueltigem JSON danach (bereits verdaechtig)."""
    idx = text.find(_OEFFENTLICHE_TISCHSICHT_MARKER)
    if idx == -1:
        return None
    payload = text[idx + len(_OEFFENTLICHE_TISCHSICHT_MARKER):]
    try:
        return json.loads(payload)
    except (json.JSONDecodeError, ValueError):
        return False


_ACTOR_HEADER_INFIX = "— "  # "[BISHERIGER STAND — " (persona_state.render_for_prompt)
_ACTOR_HEADER_SUFFIX = " spielt "
# G6-E-Nacharbeit (Operationsbindung, 02_AUFTRAG_G6_REST.md #1, End-Critic-
# Fund `expected-tech-operation-relabelled-medic`): `persona_state.
# render_for_prompt` schreibt GENAU `"<actor> spielt <name> \"<callsign>\",
# <N> Runde(n) gespielt]"` -- bisher wurde aus dieser Zeile NUR der
# Akteurschluessel (`<actor>`) gelesen. Ein umbenannter Akteurheader
# ("— medic spielt ") VOR einem dazu self-konsistenten fremden Current
# (medic-Current, Name "Noor"/Callsign "MEDIC") wurde dadurch akzeptiert,
# OBWOHL derselbe Headertext dahinter weiterhin den ALTEN Namen/Callsign
# ("Kaede"/"TECH") des echten Aufrufers trug -- ein intern widerspruechliches
# Tripel, das die reine Actor-Key-Pruefung nicht sah. `_HEADER_TAIL_RE`
# liest Name+Callsign direkt aus derselben Kopfzeile; `_extract_own_currents`
# vergleicht sie gegen die unabhaengig bekannte Identitaet des per Header
# gewaehlten Akteurs (`own_current_by_actor[actor]["characters"][0]`).
_HEADER_TAIL_RE = re.compile(r'(?P<name>.*?) "(?P<callsign>[^"]*)", \d+ Runde\(n\) gespielt\]')


def _actor_header_positions(text: str, candidate_actors) -> list:
    """Liefert `(position, persona_key, header_name, header_callsign)` fuer
    JEDES tatsaechliche Vorkommen der unveraenderlichen `persona_state.
    render_for_prompt`-Kopfzeile ('... — <persona_key> spielt <name>
    "<callsign>", N Runde(n) gespielt]') im Text -- NUR fuer die unabhaengig
    im Testsetup bekannten `candidate_actors` (`expected["own_current_by_
    actor"]`-Schluessel), kein Teilstringraten auf einen beliebigen
    Fremdnamen. `header_name`/`header_callsign` sind `None`, wenn der
    Zeilenrest nach dem Aktormarker nicht dem festen `render_for_prompt`-
    Format entspricht (dann validiert `_extract_own_currents` sie ohnehin
    nie erfolgreich gegen eine bekannte Identitaet)."""
    out: list = []
    for pk in candidate_actors:
        marker = f"{_ACTOR_HEADER_INFIX}{pk}{_ACTOR_HEADER_SUFFIX}"
        start = 0
        while True:
            idx = text.find(marker, start)
            if idx == -1:
                break
            tail = _HEADER_TAIL_RE.match(text, idx + len(marker))
            header_name = tail.group("name") if tail else None
            header_callsign = tail.group("callsign") if tail else None
            out.append((idx, pk, header_name, header_callsign))
            start = idx + 1
    return out


def _extract_own_currents(text: str, own_current_by_actor: dict, allow_char_id_fallback: bool = False) -> list:
    """Liefert `("actor"|"char_id", key, parsed_current_dict)` fuer JEDEN
    `_OWN_CURRENT_MARKER`-Beleg in `text` (echter Marker aus `mmo_sim/ui/
    tui.py:_own_system_context`, hier nur gelesen). `own_current_by_actor`
    ist jetzt das VOLLE `expected["own_current_by_actor"]`-Dict (nicht mehr
    nur dessen Schluessel) -- s. G6-E-Nacharbeit unten, die seine Werte fuer
    die Header-Identitaetspruefung braucht.

    01_REVIEW_G6.md 'own_current_by_char_id erlaubt den Inhalt jeder dort
    enthaltenen Figur. Die zu pruefende char_id waehlt selbst den
    Erwartungsdatensatz': sobald IRGENDWO im Text mindestens EIN bekannter
    Akteurmarker (unveraenderliche `persona_state.render_for_prompt`-
    Kopfzeile '... — <persona_key> spielt ...') vorkommt, wird `key`
    GEBUNDEN aus dieser Kopfzeile bestimmt (NAECHSTE davor liegende
    Fundstelle) -- NICHT mehr aus dem eingebetteten `characters[0].char_id`
    DES GEPRUEFTEN Current-JSON selbst (frei waehlbar durch den Input,
    genau der dokumentierte Fehlkontext 'anderer Current mit erlaubter
    char_id').

    G6-Nacharbeit (End-Critic-Fund, `actor-header-strip-probe`): die fruehere
    Fassung koppelte den char_id-Fallback an "kein Akteurmarker IRGENDWO im
    Text" -- das liess sich durch das blosse ENTFERNEN der einen
    Headerzeile aus einer sonst korrekt abgelehnten `other-members-current`-
    Anfrage wieder in den schwaecheren Pfad zurueckdraengen (empirisch an
    beiden echten Doubles reproduziert). Der Fallback ist jetzt an ein
    EXPLIZITES, von `request_text_is_valid_for_double`/der CLI-Vorlage aus
    `expected["allow_legacy_charid_fallback"]` durchgereichtes Signal
    gebunden (`allow_char_id_fallback`), NICHT mehr an die blosse Abwesenheit
    einer Kopfzeile im zu pruefenden Text selbst. Nur das archivierte
    `reproduce_fund_a_g6_derivative.py`-Gesundfixture (ein blosser
    `_OWN_CURRENT_MARKER`-Block ohne vorausgehende `render_for_prompt`-
    Kopfzeile, strukturell verschieden vom echten Produktwire, das die
    Kopfzeile IMMER mitsendet) setzt dieses Signal explizit via
    `expected_context_for_case(..., allow_legacy_charid_fallback=True)`.
    Ohne dieses Signal ist ein Current-Beleg OHNE vorausgehenden Akteurmarker
    schlicht ungueltig (`mode=False`) -- ein Angreifer kann die Bindung also
    nicht mehr durch Entfernen der Kopfzeile abschalten. `(False, False,
    None)` bei ungueltigem JSON ODER fehlendem Akteurmarker ohne erlaubten
    Fallback (NIE stillschweigend uebersprungen). `json.JSONDecoder.
    raw_decode` liest GENAU den JSON-Wert ab der Markerposition, unabhaengig
    davon, ob er in einer HTTP-`system`-Nachricht (bis zum Ende) oder
    eingebettet in einem laengeren CLI-Stdin-Text (gefolgt von weiterem
    Text) steht.

    G6-E-Nacharbeit (Operationsbindung, End-Critic-Fund `expected-tech-
    operation-relabelled-medic`): der per Kopfzeile gewaehlte `actor`
    wird jetzt ZUSAETZLICH gegen die unabhaengig bekannte Identitaet
    (`own_current_by_actor[actor]["characters"][0]["name"]`/`["callsign"]`)
    geprueft, die GENAU DIESELBE Kopfzeile (`persona_state.render_for_
    prompt`) direkt danach mitfuehrt. Ein umbenannter Akteurschluessel VOR
    einem dazu self-konsistenten FREMDEN Current (z.B. "— medic spielt "
    + medic-Current) traegt in derselben Zeile weiterhin den ALTEN Namen/
    Callsign des echten Aufrufers -- `mode=False` bei diesem Widerspruch,
    NICHT erst beim (hier gar nicht vorhandenen) Current-Wertevergleich."""
    actor_positions = _actor_header_positions(text, own_current_by_actor.keys())
    out: list = []
    search_from = 0
    decoder = json.JSONDecoder()
    while True:
        idx = text.find(_OWN_CURRENT_MARKER, search_from)
        if idx == -1:
            break
        json_start = idx + len(_OWN_CURRENT_MARKER)
        try:
            obj, end = decoder.raw_decode(text, json_start)
        except (json.JSONDecodeError, ValueError):
            out.append((False, False, None))
            break
        if actor_positions:
            preceding = [
                (pos, pk, name, callsign) for pos, pk, name, callsign in actor_positions if pos <= idx
            ]
            if not preceding:
                actor = None
            else:
                _, actor, header_name, header_callsign = max(preceding, key=lambda t: t[0])
                known_chars = (own_current_by_actor.get(actor) or {}).get("characters") or [{}]
                known_name = known_chars[0].get("name") if known_chars else None
                known_callsign = known_chars[0].get("callsign") if known_chars else None
                if header_name != known_name or header_callsign != known_callsign:
                    actor = False
            out.append(("actor", actor, obj))
        elif allow_char_id_fallback:
            chars = obj.get("characters") if isinstance(obj, dict) else None
            char_id = (
                chars[0].get("char_id")
                if isinstance(chars, list) and chars and isinstance(chars[0], dict)
                else None
            )
            out.append(("char_id", char_id, obj))
        else:
            out.append((False, False, None))
        search_from = end
    return out


def expected_context_for_case(*, leader: str, members, table_id: str, section_id: str, final_saves: dict, offer_ids=(), allow_legacy_charid_fallback: bool = False) -> dict:
    """Baut die unabhaengige G6-Erwartung AUSSCHLIESSLICH aus bereits am
    Testsetup bekannten Werten (Fixture-Teilnehmer, gewollte Einladungen,
    `compute_table_id`/`sorted_table_members`, die VOR dem Rundenaufruf
    publizierten v7-Saves) -- NIEMALS aus einem spaeter zu pruefenden
    Anfrage-/Antworttext zurueckabgeleitet. `own_current_by_char_id` bindet
    den vollstaendigen, zu diesem Zeitpunkt gueltigen eigenen Spielstand an
    den tatsaechlichen Routingschluessel (`zeitriss_saves.block_char_id`) --
    derselbe Current bleibt in JEDER Anfragephase gueltig (Einladung/Import/
    Polls/Reflexion), weil `_own_system_context`/die Reflexion ihn erst NACH
    Abschnittsabschluss aktualisieren (02_AUFTRAG_G6.md 'Aktuell bleibt der
    Current im Reflexionsinput der vorher gueltige Stand').

    `allow_legacy_charid_fallback` (G6-Nacharbeit, End-Critic-Fund): Default
    `False` -- fuer JEDEN realen G6-E-Testfall in dieser Datei (Produktwire
    traegt die Akteurkopfzeile IMMER). Nur das archivierte, strukturell
    headerlose `reproduce_fund_a_g6_derivative.py`-Gesundfixture setzt dies
    explizit auf `True`, um ohne Zweitpflege gruen zu bleiben, s.
    `_extract_own_currents`."""
    own_current_by_char_id = {}
    for save in final_saves.values():
        char_id = zeitriss_saves.block_char_id(save)
        if char_id:
            own_current_by_char_id[char_id] = save
    # G6-E (01_REVIEW_G6.md, siehe `_extract_own_currents`): zusaetzlich
    # ZU `own_current_by_char_id` -- NICHT ersetzend, `own_current_by_char_id`
    # bleibt fuer die eigenstaendige Fake-CLI-Kopie der Pruefung erhalten --
    # eine vom eingebetteten `char_id` UNABHAENGIGE Bindung je `persona_key`
    # (dieselben Schluessel, mit denen `final_saves` von JEDEM Aufrufer
    # bereits befuellt wird, identisch zu `ui/tui.py:_own_system_context
    # (persona_key)`s eigenem Routingschluessel).
    own_current_by_actor = dict(final_saves)
    return {
        "table_id": table_id, "leader": leader, "members": sorted(members),
        "section_id": section_id, "own_current_by_char_id": own_current_by_char_id,
        "own_current_by_actor": own_current_by_actor,
        "offer_ids": sorted(set(offer_ids)),
        "allow_legacy_charid_fallback": bool(allow_legacy_charid_fallback),
    }


def table_view_is_consistent(view: dict, expected: dict, gm_receipts: list) -> bool:
    """G6-E: `table_id`/`leader`/`members` muessen EXAKT der unabhaengig im
    Testsetup berechneten Erwartung entsprechen (NICHT einer aus `view`s
    eigenem `leader`/`members` rekonstruierten Formel -- genau das liess das
    dokumentierte Fund-A-Tripel, komplett anders aber intern konsistent,
    zuvor durch).

    01_REVIEW_G6.md ('die EMPFANGENE Liste' + '`content in gm_receipts`' ist
    keine Vollstaendigkeitspruefung -- eine leere Liste, Umordnung und
    Wiederholung bekannter Texte blieben zulaessig; der Abschlussmarker
    erlaubte eine gekuerzte Endantwort): `sl_log` muss jetzt (a) GENAU so
    lang sein wie das unabhaengig gefuehrte `gm_receipts`-Journal (die
    EMPFANGENE Laenge bestimmt NICHT mehr die Solllaenge -- `len(gm_
    receipts)` ist die zum Zeitpunkt dieser Anfrage tatsaechlich bereits
    beobachtete, unabhaengige Praefixlaenge) und (b) an JEDER Position
    WORTGLEICH dem tatsaechlich beobachteten GM-Ausgangsjournaleintrag an
    GENAU dieser Position entsprechen -- keine Mengen-/Teilstringpruefung
    mehr. Der echte Abschlussmarker mit `table_id=`/`section_id=` bleibt
    eine ZUSAETZLICHE Pruefung (nicht mehr ein Ersatz/`continue`, der die
    Wortgleichheitspruefung fuer genau diesen Eintrag umgeht -- G6-E
    'COMPLETION_MARKER-continue darf vollstaendige Endantworten nicht
    umgehen')."""
    if view.get("table_id") != expected["table_id"] or view.get("leader") != expected["leader"]:
        return False
    members = view.get("members")
    if isinstance(members, list) and sorted(members) != expected["members"]:
        return False
    sl_log = view.get("sl_log")
    if not isinstance(sl_log, list) or len(sl_log) != len(gm_receipts):
        return False
    for idx, entry in enumerate(sl_log):
        if not isinstance(entry, dict):
            return False
        content = entry.get("content")
        if not isinstance(content, str) or content != gm_receipts[idx]:
            return False
        if COMPLETION_MARKER in content and (
            f"table_id={expected['table_id']}" not in content
            or f"section_id={expected['section_id']}" not in content
        ):
            return False
    return True


def gm_history_is_valid(messages: list, gm_receipts: list, own_current_by_char_id: dict | None = None) -> bool:
    """G6-E ('GM-Requestrolle separat pruefen. Frueheres user/assistant-
    Transcript an die tatsaechlichen vorherigen GM-Ein-/Ausgaenge binden'):
    GM-Request-Bodies tragen KEINE Persona-Kopfzeile/kein `[OEFFENTLICHE_
    TISCHSICHT]`-Feld -- `request_text_is_valid_for_double`s Markerscan lief
    fuer sie bisher komplett LEER durch (01_REVIEW_G6.md 'GM-Bodies tragen
    diese Marker nicht; deren historische Nachrichten und exakte
    Leadernachricht werden dadurch nicht vollstaendig validiert'), eine
    ausgetauschte historische GM-Antwort wurde deshalb NIE abgelehnt.

    Diese eigene, separate GM-Rollenpruefung bindet jede im Request
    mitgefuehrte VERGANGENE `assistant`-Nachricht (GMs eigene vorherige
    Ausgabe) wortgleich an das tatsaechlich beobachtete GM-Ausgangsjournal
    (`gm_receipts`, von der GM-Seite NACH echtem Write/Flush gefuehrt) AN
    GENAU IHRER POSITION -- dieselbe unabhaengige, positionsgebundene
    Wortgleichheitspruefung wie `table_view_is_consistent`s `sl_log`, hier
    auf die GM-eigene `user`/`assistant`-Transcriptstruktur angewendet
    (`messages = [user_0, assistant_0, user_1, assistant_1, ..., user_i]`,
    `assistant_k` ist GMs tatsaechliche Ausgabe von Aufruf `k`). Die ZULETZT
    eingereichte `user`-Nachricht ist der NEUE, gerade erst vorgelegte
    Leaderinput -- fuer ihn existiert noch kein Journaleintrag, er wird
    NICHT gegen `gm_receipts` geprueft (das waere ein zirkulaerer Vergleich
    mit sich selbst).

    G6-E-Nacharbeit (02_AUFTRAG_G6_REST.md #2, End-Critic-Fund `gm-past-
    user-changed`): die obige Pruefung band bisher NUR die historischen
    `assistant`-Texte, NIE die historischen `user`-Texte (echte GM-Request-
    Bodies betten dort -- empirisch an allen vier A24-Faellen verifiziert --
    bei Importen/Erstkontakt eines Akteurs GENAU EINEN rohen v7-Save-Block
    ein, s. `zeitriss_saves.extract_all_saves`; spaetere reine Fortsetzungs-
    turns KEINEN). Ein ausgetauschter ALTER `user`-Text ohne jeden Save-Block
    (wie die synthetische Ersatz-Nachricht der Probe) wurde deshalb nie
    erkannt, obwohl die allererste `user`-Nachricht des gesamten GM-
    Verlaufs (Index 0 in `messages`, das Abschnitts-Eroeffnungsimport)
    IMMER genau einen gueltigen Block trug. Jeder irgendwo in `messages`
    gefundene Save-Block (gleich an welcher Position, historisch ODER
    aktuell) muss jetzt exakt dem unter seiner `char_id` unabhaengig
    bekannten Current entsprechen (`own_current_by_char_id`, KEIN Vergleich
    gegen `gm_receipts`/sich selbst); Position 0 muss mindestens einen
    solchen Block tragen."""
    if not isinstance(messages, list) or not messages:
        return False
    history = messages[:-1]
    if len(history) % 2 != 0 or len(history) // 2 != len(gm_receipts):
        return False
    for k in range(len(history) // 2):
        user_entry, assistant_entry = history[2 * k], history[2 * k + 1]
        if not isinstance(user_entry, dict) or not isinstance(assistant_entry, dict):
            return False
        if user_entry.get("role") != "user" or assistant_entry.get("role") != "assistant":
            return False
        if assistant_entry.get("content") != gm_receipts[k]:
            return False
    own_current_by_char_id = own_current_by_char_id or {}
    for idx, entry in enumerate(messages):
        if not isinstance(entry, dict) or entry.get("role") != "user":
            continue
        content = entry.get("content")
        if not isinstance(content, str):
            return False
        blocks = zeitriss_saves.extract_all_saves(content)
        if idx == 0 and not blocks:
            return False
        for blk in blocks:
            cid = zeitriss_saves.block_char_id(blk)
            if cid not in own_current_by_char_id or blk != own_current_by_char_id[cid]:
                return False
    return True


def request_text_is_valid_for_double(*texts: str, expected: dict, gm_receipts: list) -> bool:
    """`True` nur, wenn JEDER uebergebene Text (a) entweder keinen
    `[OEFFENTLICHE_TISCHSICHT]`-Block enthaelt oder einen, der
    `table_view_is_consistent` gegen die unabhaengige `expected`-Erwartung
    erfuellt, (b) jeder eingebettete eigene Current exakt dem unter seinem
    `char_id` unabhaengig erwarteten Save entspricht, und (c) jeder im Text
    referenzierte `offer_id`-Bezug (falls die Erwartung ueberhaupt Angebote
    kennt) zu einem tatsaechlich erwarteten Angebot gehoert. `False` bei
    jedem erkannten Fremd-/Korruptions-/Mehrdeutigkeitsfall -- kein
    `expected`-loser Default-Accept."""
    own_current_by_actor = expected.get("own_current_by_actor") or {}
    own_current_by_char_id = expected.get("own_current_by_char_id") or {}
    allow_char_id_fallback = bool(expected.get("allow_legacy_charid_fallback"))
    for text in texts:
        view = _extract_table_view(text)
        if view is False:
            return False
        if view is not None and not table_view_is_consistent(view, expected, gm_receipts):
            return False
        for mode, key, current_obj in _extract_own_currents(text, own_current_by_actor, allow_char_id_fallback):
            if mode is False or key is False or key is None:
                return False
            if mode == "actor":
                if key not in own_current_by_actor or current_obj != own_current_by_actor[key]:
                    return False
            else:  # mode == "char_id": kein Akteurmarker irgendwo im Text, s. `_extract_own_currents`.
                if key not in own_current_by_char_id or current_obj != own_current_by_char_id[key]:
                    return False
        if expected["offer_ids"]:
            for offer_match in _OFFER_ID_RE.findall(text):
                if offer_match not in expected["offer_ids"]:
                    return False
    return True


_DOUBLE_REJECTION_CONTENT = (
    "[A24_DOUBLE_REJECTED] inconsistent table_view/public GM-reply in "
    "request -- not treated as a successful turn (G6)."
)


# --------------------------------------------------------------------------
# Loopback-HTTP-Server: Persona-API (OpenAI-kompatibel) UND GM/SL (OWUI-
# kompatibel) erfuellen denselben {choices:[{message:{content}}]}-Vertrag.
# --------------------------------------------------------------------------

def _read_gm_receipts(path: Path) -> list:
    """Liest das tatsaechlich beobachtete GM-Ausgangsjournal (s.
    `_append_gm_receipt`) -- leer, wenn noch kein echter GM-Turn
    geschrieben/geflusht wurde (kein Fehlalarm, kein erfundener Eintrag)."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []
    return [json.loads(ln) for ln in lines if ln.strip()]


def _append_gm_receipt(path: Path, content: str) -> None:
    """G6-O: haengt EINEN tatsaechlich geschriebenen/geflushten GM-Antwort-
    text an das gemeinsame Journal an -- wird ausschliesslich NACH einem
    erfolgreichen `wfile.write`+`flush` der GM-Seite aufgerufen (s.
    `_SequencedHandler.do_POST`), NIE vorher/bei Ablehnung. Eigener
    `fsync`, damit ein paralleler Leser (Persona-HTTP-Handler ODER die
    Fake-CLI als eigenstaendiger Subprozess) den Eintrag danach sicher
    sieht -- kein unbegrenztes Retry, nur ein echter Flush-Beleg."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(content, ensure_ascii=False) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


class SequencedHTTPServer(HTTPServer):
    """Echter Loopback-HTTP-Server (127.0.0.1, zufaelliger freier Port).
    `scripted` liefert die ersten `len(scripted)` Antworten der Reihe nach
    (fuer deterministisch geordnete Aufrufe wie Einladungen); danach liefert
    `fallback_fn(call_index, body)` jede weitere Antwort (fuer normale Spiel-/
    Absprache-/Reflexionsturns, deren exakte Gesamtzahl nicht vorab gezaehlt
    werden muss). Jeder vollstaendige Request-Body wird in `.received`
    gesammelt (Rohbeleg, s. `02_AUFTRAG_A24.md` 'Belege und Schluss').

    G6: `expected_context` (s. `expected_context_for_case`) ist PFLICHT --
    kein `None`-Default, der jede Anfrage ungeprueft durchliesse.
    `gm_receipts_path` ist das gemeinsame, dateibasierte GM-Ausgangsjournal
    (von der GM-Seite, `is_gm_server=True`, NACH echtem Write/Flush
    gefuehrt; von der Persona-Seite UND der Fake-CLI nur gelesen)."""

    def __init__(self, scripted: "list[str]", fallback_fn, *, expected_context: dict, gm_receipts_path: "Path", is_gm_server: bool = False):
        super().__init__(("127.0.0.1", 0), _SequencedHandler)
        self.scripted = list(scripted)
        self.fallback_fn = fallback_fn
        self.received: list[dict] = []
        self.calls = 0
        self.expected_context = expected_context
        self.gm_receipts_path = Path(gm_receipts_path)
        self.is_gm_server = is_gm_server
        self._thread = threading.Thread(target=self.serve_forever, daemon=True)

    def next_content(self, body: dict) -> str:
        idx = self.calls
        self.calls += 1
        if idx < len(self.scripted):
            return self.scripted[idx]
        return self.fallback_fn(idx, body)

    @property
    def base_url(self) -> str:
        host, port = self.server_address
        return f"http://{host}:{port}"

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self.shutdown()
        self.server_close()


class _SequencedHandler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        return

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b""
        received_wall_ts = time.time()
        try:
            body = json.loads(raw.decode("utf-8")) if raw else {}
        except json.JSONDecodeError:
            body = {"_raw_undecoded": raw.decode("utf-8", errors="replace")}
        # G6-E: vor JEDER Erfolgsausgabe den tatsaechlichen oeffentlichen
        # Tischkontext/eigenen Current/Angebotsbezug gegen die unabhaengige
        # Erwartung validieren -- bei Ablehnung wird die gescriptete/
        # Fallback-Queue NICHT konsumiert (kein Indexversatz fuer
        # nachfolgende gesunde Aufrufe).
        message_texts = [
            m.get("content") for m in (body.get("messages") or [])
            if isinstance(body, dict) and isinstance(m, dict) and isinstance(m.get("content"), str)
        ]
        gate_lock, gate_state, gate_ok, gate_reason = _g6_gate_open(
            self.server.gm_receipts_path, "gm" if self.server.is_gm_server else "persona",
            message_texts, body.get("messages") or [],
        )
        gm_receipts = _read_gm_receipts(self.server.gm_receipts_path)  # type: ignore[attr-defined]
        valid = request_text_is_valid_for_double(
            *message_texts, expected=self.server.expected_context, gm_receipts=gm_receipts,  # type: ignore[attr-defined]
        )
        # G6-E: die GM-Seite traegt keine Persona-Kopfzeile/kein table_view
        # (der obige Markerscan laeuft fuer sie leer durch) -- eine EIGENE,
        # separate Rollenpruefung bindet ihr user/assistant-Transcript an
        # das tatsaechlich beobachtete GM-Ausgangsjournal (s. `gm_history_
        # is_valid`), statt unueberprueft durchzulaufen.
        if valid and self.server.is_gm_server:  # type: ignore[attr-defined]
            own_current_by_char_id = (self.server.expected_context or {}).get("own_current_by_char_id")  # type: ignore[attr-defined]
            valid = (
                gm_history_is_valid(body.get("messages") or [], gm_receipts, own_current_by_char_id)
                if isinstance(body, dict) else False
            )
        valid = valid and gate_ok
        rejected = not valid
        if rejected:
            content = _DOUBLE_REJECTION_CONTENT
        else:
            content = self.server.next_content(body)  # type: ignore[attr-defined]
        payload = {"choices": [{"message": {"content": content}}], "usage": {}, "sources": []}
        data = json.dumps(payload).encode("utf-8")
        # G6-O (01_REVIEW_A24.md Fund: "`.received` haengt response_content
        # an, BEVOR `wfile.write` aufgerufen wird" -- das belegte nur die
        # Schreibabsicht, keinen tatsaechlichen Ausgang): Status/Header
        # gehen unveraendert vor dem Body, aber die ERFOLGSAUFZEICHNUNG
        # (inkl. GM-Journaleintrag) erfolgt jetzt ausschliesslich NACH
        # einem tatsaechlich beobachteten `write`+`flush`.
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        write_ok = False
        write_error = None
        try:
            self.wfile.write(data)
            self.wfile.flush()
            write_ok = True
        except Exception as exc:  # pragma: no cover - defensiv, nur echte Socketfehler
            write_error = repr(exc)
        responded_wall_ts = time.time()
        self.server.received.append({  # type: ignore[attr-defined]
            "seq": len(self.server.received), "path": self.path,  # type: ignore[attr-defined]
            "authorization_present": bool(self.headers.get("Authorization")),
            "body": body,
            "request_raw_b64": base64.b64encode(raw).decode("ascii"),
            "request_raw_sha256": hashlib.sha256(raw).hexdigest(), "request_raw_len": len(raw),
            "response_content": content,
            "response_raw_b64": base64.b64encode(data).decode("ascii"),
            "response_raw_sha256": hashlib.sha256(data).hexdigest(), "response_raw_len": len(data),
            "rejected": rejected, "operation_reason": gate_reason, "write_ok": write_ok, "write_error": write_error,
            "received_wall_ts": received_wall_ts, "responded_wall_ts": responded_wall_ts,
        })
        # G6-O/G6-correspondence: der gemeinsame GM-Ausgangsjournaleintrag
        # entsteht NUR auf der tatsaechlichen GM-Seite, NUR nach echtem
        # Write/Flush, UND NIE fuer eine bereits abgelehnte Anfrage (sonst
        # koennte ein abgelehnter Request ein Fremdnarrativ ins Journal
        # schmuggeln, das spaetere gesunde Anfragen faelschlich akzeptieren
        # wuerden).
        if write_ok and not rejected and self.server.is_gm_server:  # type: ignore[attr-defined]
            _append_gm_receipt(self.server.gm_receipts_path, content)  # type: ignore[attr-defined]
        try:
            if write_ok and not rejected:
                _g6_gate_commit(gate_state, content, wire_sha256=hashlib.sha256(data).hexdigest(),
                                written_ts=responded_wall_ts)
        finally:
            _g6_gate_close(gate_lock)


def narrative_fallback(prefix: str):
    def _fn(idx: int, body: dict) -> str:
        return f"{prefix} Szene {idx}: ruhige Lage, was tut ihr als Naechstes?"
    return _fn


def smart_gm_fallback(expected_char_ids: set, final_saves: dict, table_id: str, section_id: str, complete_after: int, received_ids: set):
    """GM-Server-Fallback nach den gescripteten Eintraegen: liefert normalen
    Szenentext, SOBALD aber (a) mindestens `complete_after` Aufrufe insgesamt
    erfolgt sind UND (b) alle erwarteten v7-Char-IDs bereits in irgendeinem
    bisherigen `user`-Feld gesehen wurden, liefert er den Abschlussmarker mit
    allen finalen Saves -- positionsunabhaengig, kein geraten gezaehlter Slot
    (Muster aus `e2e_real_subprocess_dialog.py:_SmartGmHandler`)."""
    def _fn(idx: int, body: dict) -> str:
        messages = body.get("messages") or []
        last_user = messages[-1]["content"] if messages else ""
        for blk in zeitriss_saves.extract_all_saves(last_user):
            cid = zeitriss_saves.block_char_id(blk)
            if cid:
                received_ids.add(cid)
        if idx + 1 >= complete_after and expected_char_ids.issubset(received_ids):
            debrief = "\n".join(f"```json\n{json.dumps(b, ensure_ascii=False)}\n```" for b in final_saves.values())
            return f"{debrief}\n{COMPLETION_MARKER} table_id={table_id} section_id={section_id}"
        return f"Szene {idx}: Ihr beobachtet die Lage weiter. Was tut ihr?"
    return _fn


# --------------------------------------------------------------------------
# Reale ausfuehrbare Fake-CLI (Hybrid-Profil, echter `_RealProcessRunner`)
# --------------------------------------------------------------------------

_QUEUED_FAKE_CLI_TEMPLATE = '''{shebang}
__G6_SHARED_CODE__
import hashlib
import base64
import json
import os
import re
import sys
import time

CAPTURE_PATH = {capture_path!r}
QUEUE_PATH = {queue_path!r}
# G6-O (01_REVIEW_G6.md "Unveraendert besitzen die tatsaechlichen Hybrid-
# spiel-Captures nur argv, pid, stdin, wall_ts... Keine individuellen
# stdout-/stderr-/LF-, PPID-/cwd-/Exit-/Timeout- oder Elternempfangsbelege
# darin"): kuratierte kindseitige Env-Allowlist, identisch zu
# `mmo_sim/adapters/persona_claude_code.py:_CHILD_ENV_ALLOWLIST` (hier nur
# gelesen/gespiegelt, keine Produktaenderung).
_CHILD_ENV_ALLOWLIST = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "TERM", "SHELL")

if "--help" in sys.argv or "--version" in sys.argv:
    if "--version" in sys.argv:
        print("fake-claude 0.0.0-a24-test")
        sys.exit(0)
    print(
        "Usage: fake-claude [options]\\n"
        "  --permission-mode <mode>  restrict tool execution (plan|manual|acceptEdits|auto|bypassPermissions|dontAsk)\\n"
        "  --safe-mode  skip hooks, MCP servers, settings, plugins\\n"
        "  --tools <list>  restrict available tools\\n"
        "  --allowed-tools <list> / --disallowed-tools <list>\\n"
        "  --strict-mcp-config / --mcp-config <path> / --setting-sources <list>"
    )
    sys.exit(0)

# G6-O: beide Haelften dieses einen Aufrufs ("input" JETZT, "own_output"
# unmittelbar vor jedem Exit, s. `_a24_finish` unten) tragen denselben
# `pid` -- der gemeinsame Joinschluessel fuer `read_cli_captures()` (fake-
# eigene Seite) GEGEN die vom tatsaechlichen Elternprozess (TUI-Kind, s.
# `write_a24_cli_observer_guard`) unabhaengig beobachteten `spawns.jsonl`/
# `process-results.jsonl`-Eintraege (`join_cli_parent_observations`).
# G6-O-Nacharbeit (02_AUFTRAG_G6_REST.md #3, IMPLEMENTIERUNGSWEG Punkt 3):
# eindeutiger Rohbytevertrag -- die gewuenschte Ausgabe wird EXPLIZIT als
# UTF-8-Bytes codiert und GENAU diese Bytes werden via `stdout.buffer.write`/
# `flush` (nicht mehr die Text-`write`) geschrieben; Hash/Laenge/Encoding
# derselben Bytefolge werden direkt im `own_output`-Record mitgesichert,
# damit ein Test den Vertrag ohne erneute Encodierung nachrechnen kann.
def _a24_finish(rc, stdout_text, stderr_text):
    stdout_bytes = (stdout_text or "").encode("utf-8")
    stderr_bytes = (stderr_text or "").encode("utf-8")
    sys.stdout.buffer.write(stdout_bytes)
    sys.stdout.buffer.flush()
    sys.stderr.buffer.write(stderr_bytes)
    sys.stderr.buffer.flush()
    with open(CAPTURE_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(
            {{"kind": "own_output", "pid": os.getpid(), "planned_returncode": rc,
              "stdout": stdout_text, "stderr": stderr_text,
              "stdout_b64": base64.b64encode(stdout_bytes).decode("ascii"),
              "stderr_b64": base64.b64encode(stderr_bytes).decode("ascii"),
              "write_flush_succeeded": True,
              "stdout_sha256": hashlib.sha256(stdout_bytes).hexdigest(), "stdout_len": len(stdout_bytes),
              "stderr_sha256": hashlib.sha256(stderr_bytes).hexdigest(), "stderr_len": len(stderr_bytes),
              "encoding": "utf-8", "wall_ts": time.time()}},
            ensure_ascii=False,
        ) + "\\n")
        fh.flush()
        os.fsync(fh.fileno())
    try:
        if rc == 0 and _G6_OK:
            _g6_gate_commit(_G6_STATE, json.loads(stdout_text)["result"],
                            wire_sha256=hashlib.sha256(stdout_bytes).hexdigest(), written_ts=time.time())
    finally:
        _g6_gate_close(_G6_LOCK)
    sys.exit(rc)


_CALL_STARTED_TS = time.time()
stdin_bytes = sys.stdin.buffer.read()
stdin_text = stdin_bytes.decode("utf-8")
with open(CAPTURE_PATH, "a", encoding="utf-8") as fh:
    fh.write(json.dumps(
        {{"kind": "input", "argv": sys.argv[1:], "stdin": stdin_text, "stdin_b64": base64.b64encode(stdin_bytes).decode("ascii"), "stdin_len": len(stdin_bytes), "stdin_sha256": hashlib.sha256(stdin_bytes).hexdigest(), "pid": os.getpid(), "ppid": os.getppid(),
          "cwd": os.getcwd(), "env_curated": {{k: os.environ.get(k) for k in _CHILD_ENV_ALLOWLIST}},
          "wall_ts": _CALL_STARTED_TS}}, ensure_ascii=False,
    ) + "\\n")
    fh.flush()
    os.fsync(fh.fileno())

# G6-E (02_AUFTRAG_G6.md "unabhaengige Erwartungsbindung"): dieselbe
# unabhaengige Pruefung wie `_a24_local_support.request_text_is_valid_for_
# double`/`table_view_is_consistent` (eigenstaendiger Subprozess, kein
# Import aus `_a24_local_support.py` moeglich -- daher hier bewusst
# dupliziert, eng begrenzt auf genau diese Pruefung). Die Erwartung kommt
# AUSSCHLIESSLICH aus der vorab (VOR diesem Aufruf) vom Testfall
# geschriebenen `EXPECTED_CONTEXT_PATH` -- NIE aus `stdin_text` selbst
# zurueckabgeleitet. Damit faellt dasselbe komplett erfundene, aber intern
# konsistente Tripel (dokumentierter Fund A) hier genauso durch wie am
# HTTP-Double, weil `table_id`/`leader`/`members` gegen die unabhaengige
# Erwartung verglichen werden, statt aus dem Anfragewert selbst rekon-
# struiert zu werden; `sl_log`-Inhalte muessen im tatsaechlich beobachteten
# GM-Ausgangsjournal (`GM_RECEIPTS_PATH`, von der GM-Seite NACH echtem
# Write/Flush gefuehrt) vorkommen statt gegen statische Erzaehltexte.
EXPECTED_CONTEXT_PATH = {expected_context_path!r}
GM_RECEIPTS_PATH = {gm_receipts_path!r}

with open(EXPECTED_CONTEXT_PATH, "r", encoding="utf-8") as _ectx_fh:
    _expected = json.load(_ectx_fh)
_expected_members = sorted(_expected.get("members") or [])
_expected_own_current_actor = _expected.get("own_current_by_actor") or {{}}
_expected_own_current_charid = _expected.get("own_current_by_char_id") or {{}}
_expected_offer_ids = set(_expected.get("offer_ids") or [])
# G6-Nacharbeit (End-Critic-Fund, `actor-header-strip-probe`): derselbe
# explizite Fallback-Schalter wie in `_extract_own_currents` (Python-Seite)
# -- NICHT mehr blosse Abwesenheit einer Kopfzeile im zu pruefenden Text.
_allow_charid_fallback = bool(_expected.get("allow_legacy_charid_fallback"))


def _read_gm_receipts():
    try:
        with open(GM_RECEIPTS_PATH, "r", encoding="utf-8") as _gh:
            _lines = _gh.read().splitlines()
    except FileNotFoundError:
        return []
    return [json.loads(_ln) for _ln in _lines if _ln.strip()]


_G6_LOCK, _G6_STATE, _G6_OK, _G6_REASON = _g6_gate_open(
    GM_RECEIPTS_PATH, "persona", [stdin_text], None)
_gm_receipts = _read_gm_receipts()
_ok = _G6_OK

_marker = "[OEFFENTLICHE_TISCHSICHT]\\n"
_idx = stdin_text.find(_marker)
if _idx != -1:
    try:
        _view = json.loads(stdin_text[_idx + len(_marker):])
    except ValueError:
        _view = None
        _ok = False
    if _ok and isinstance(_view, dict):
        if _view.get("table_id") != _expected.get("table_id") or _view.get("leader") != _expected.get("leader"):
            _ok = False
        _members = _view.get("members")
        if _ok and isinstance(_members, list) and sorted(_members) != _expected_members:
            _ok = False
        # G6-E: dieselbe unabhaengige, positionsgebundene Wortgleichheits-
        # pruefung wie `table_view_is_consistent` in `_a24_local_support.py`
        # -- die EMPFANGENE Laenge bestimmt NICHT mehr die Solllaenge
        # (`len(_gm_receipts)` ist unabhaengig), und JEDE Position muss
        # wortgleich dem tatsaechlich beobachteten GM-Ausgangsjournaleintrag
        # entsprechen (keine Mengen-/Teilstringpruefung mehr). Der echte
        # Abschlussmarker bleibt eine ZUSAETZLICHE Pruefung, kein `continue`-
        # Ersatz dafuer.
        if _ok:
            _sl_log = _view.get("sl_log")
            if not isinstance(_sl_log, list) or len(_sl_log) != len(_gm_receipts):
                _ok = False
            else:
                for _sidx, _entry in enumerate(_sl_log):
                    if not isinstance(_entry, dict):
                        _ok = False
                        break
                    _content = _entry.get("content")
                    if not isinstance(_content, str) or _content != _gm_receipts[_sidx]:
                        _ok = False
                        break
                    if "SECTION-ABSCHLUSS-BESTAETIGT" in _content and not (
                        ("table_id=" + str(_expected.get("table_id"))) in _content
                        and ("section_id=" + str(_expected.get("section_id"))) in _content
                    ):
                        _ok = False
                        break
    elif _view is None:
        _ok = False

# G6-E (01_REVIEW_G6.md "own_current_by_char_id erlaubt den Inhalt jeder
# dort enthaltenen Figur. Die zu pruefende char_id waehlt selbst den
# Erwartungsdatensatz"): eigener Current gegen die unabhaengig gespeicherte
# Erwartung, gebunden ueber den GEPLANTEN ACTOR (unveraenderliche
# `persona_state.render_for_prompt`-Kopfzeile "... <actor> spielt ..." VOR
# dem Current) -- NICHT ueber das eingebettete `characters[0].char_id` DES
# GEPRUEFTEN Current-JSON selbst (das waehlte bisher frei seinen eigenen
# Erwartungsdatensatz). Derselbe Markertext wie `mmo_sim/ui/tui.py:
# _own_system_context` ("Eigener aktueller Spielstand (Current,
# vollstaendig): <json>"), hier nur gelesen/verglichen.
# G6-E-Nacharbeit (Operationsbindung, End-Critic-Fund `expected-tech-
# operation-relabelled-medic`, dieselbe Pruefung wie `_a24_local_support.
# _extract_own_currents` am Python-Double): die Kopfzeile traegt GENAU
# `"<actor> spielt <name> \"<callsign>\", N Runde(n) gespielt]"` -- ein
# umbenannter Akteurschluessel VOR einem dazu self-konsistenten FREMDEN
# Current (z.B. "— medic spielt " + medic-Current) traegt in derselben
# Zeile weiterhin den ALTEN Namen/Callsign des echten Aufrufers. Bisher
# wurde nur der Akteurschluessel gelesen -- `_HEADER_TAIL_RE` liest
# Name+Callsign direkt mit und bindet sie an die unabhaengig bekannte
# Identitaet des gewaehlten Akteurs.
_HEADER_TAIL_RE = re.compile(r'(?P<name>.*?) "(?P<callsign>[^"]*)", \\d+ Runde\\(n\\) gespielt\\]')
if _ok:
    _actor_positions = []
    for _pk in _expected_own_current_actor.keys():
        _actor_marker = "— " + _pk + " spielt "
        _astart = 0
        while True:
            _aidx = stdin_text.find(_actor_marker, _astart)
            if _aidx == -1:
                break
            _tail = _HEADER_TAIL_RE.match(stdin_text, _aidx + len(_actor_marker))
            _hname = _tail.group("name") if _tail else None
            _hcallsign = _tail.group("callsign") if _tail else None
            _actor_positions.append((_aidx, _pk, _hname, _hcallsign))
            _astart = _aidx + 1
    _cur_marker = "Eigener aktueller Spielstand (Current, vollstaendig): "
    _search_from = 0
    _decoder = json.JSONDecoder()
    while True:
        _cidx = stdin_text.find(_cur_marker, _search_from)
        if _cidx == -1:
            break
        _jstart = _cidx + len(_cur_marker)
        try:
            _cur_obj, _jend = _decoder.raw_decode(stdin_text, _jstart)
        except ValueError:
            _ok = False
            break
        if _actor_positions:
            _preceding = [(_p, _pk, _hn, _hc) for _p, _pk, _hn, _hc in _actor_positions if _p <= _cidx]
            if not _preceding:
                _ok = False
            else:
                _, _actor, _hname2, _hcallsign2 = max(_preceding, key=lambda _t: _t[0])
                _known_chars = (_expected_own_current_actor.get(_actor) or {{}}).get("characters") or [{{}}]
                _known_name = _known_chars[0].get("name") if _known_chars else None
                _known_callsign = _known_chars[0].get("callsign") if _known_chars else None
                if _hname2 != _known_name or _hcallsign2 != _known_callsign:
                    _ok = False
                elif _cur_obj != _expected_own_current_actor.get(_actor):
                    _ok = False
        elif _allow_charid_fallback:
            # G6-E Erhalt (reproduce_fund_a_g6_derivative.py-Gesundfixture ohne
            # jeden Akteurmarker, strukturell verschieden vom echten Produktwire,
            # setzt `allow_legacy_charid_fallback=True` explizit): Fallback auf
            # die char_id-gebundene Legacy-Pruefung.
            _chars = _cur_obj.get("characters") if isinstance(_cur_obj, dict) else None
            _cid = _chars[0].get("char_id") if isinstance(_chars, list) and _chars and isinstance(_chars[0], dict) else None
            if _cid not in _expected_own_current_charid or _cur_obj != _expected_own_current_charid.get(_cid):
                _ok = False
        else:
            # G6-Nacharbeit: kein Akteurmarker UND Fallback nicht explizit
            # erlaubt -- ein Angreifer kann die Bindung nicht mehr durch
            # blosses Entfernen der Kopfzeile abschalten (End-Critic-Fund).
            _ok = False
        if not _ok:
            break
        _search_from = _jend

# G6-E: Offer-Bindung -- jeder im Text referenzierte `offer_id=...`/
# `"offer_id": "..."`-Bezug muss zu einem in dieser Runde tatsaechlich
# erwarteten Angebot gehoeren (sofern die Erwartung ueberhaupt Angebote kennt).
if _ok and _expected_offer_ids:
    for _m in re.findall(r'offer_id[=:]\\s*"?([^\\s",}}]+)', stdin_text):
        if _m not in _expected_offer_ids:
            _ok = False
            break

if not _ok:
    _a24_finish(3, "", "fake-claude: A24_DOUBLE_REJECTED -- inconsistent table_view/Current/offer binding in stdin (G6)\\n")

with open(QUEUE_PATH, "r", encoding="utf-8") as fh:
    queue = json.load(fh)
if not queue:
    _a24_finish(2, "", "fake-claude: Antwortqueue erschoepft\\n")
item = queue.pop(0)
with open(QUEUE_PATH, "w", encoding="utf-8") as fh:
    json.dump(queue, fh)
result_text = item.get("result", "")
rc = int(item.get("rc", 0))
if rc != 0:
    _a24_finish(rc, "", item.get("stderr", "simulated CLI failure") + "\\n")
_a24_finish(0, json.dumps({{"type": "result", "subtype": "success", "is_error": False, "result": result_text, "usage": {{}}}}) + "\\n", "")
'''


def write_queued_fake_cli(root: Path, *, name: str, queue: list, expected_context: dict, gm_receipts_path: Path) -> Path:
    """Baut eine EIGENE, ausfuehrbare Fake-CLI-Datei, die -- fuer den
    laufenden `_RealProcessRunner` (kein injiziertes Testdouble) --
    `--help` mit den TATSAECHLICH bekannten Isolationsschaltern
    (`mmo_sim/adapters/persona_claude_code.py:_KNOWN_ISOLATION_FLAG_NAMES`)
    beantwortet und Entscheidungsaufrufe sequenziell aus einer Datei-Queue
    bedient. Ein globales, ueber ALLE drei Personas geteiltes Environment
    (`MMO_SIM_PERSONA_CLI`) ruft dieselbe Datei auf -- die Reihenfolge der
    Queue entspricht der deterministischen Gesamtreihenfolge aller
    Entscheidungsaufrufe (Invite -> Anker/Import -> Polls -> Reflexion),
    wie vom Testfall vorher berechnet (nicht geraten).

    G6: `expected_context` (s. `expected_context_for_case`, PFLICHT, kein
    `None`-Default) wird als eigene JSON-Datei neben Capture/Queue
    abgelegt -- die generierte Fake-CLI liest sie bei JEDEM Aufruf frisch,
    NIE aus dem eigenen stdin zurueckabgeleitet. `gm_receipts_path` ist das
    gemeinsame, dateibasierte GM-Ausgangsjournal (von der GM-HTTP-Seite
    gefuehrt, hier nur gelesen)."""
    capture_path = root / f"{name}.capture.jsonl"
    queue_path = root / f"{name}.queue.json"
    expected_context_path = root / f"{name}.expected_context.json"
    write_json(queue_path, queue)
    write_json(expected_context_path, expected_context)
    path = root / f"fake_claude_{name}.py"
    path.write_text(
        _QUEUED_FAKE_CLI_TEMPLATE.format(
            shebang=f"#!{sys.executable}", capture_path=str(capture_path), queue_path=str(queue_path),
            expected_context_path=str(expected_context_path), gm_receipts_path=str(Path(gm_receipts_path)),
        ).replace("__G6_SHARED_CODE__", _g6_shared_source()),
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return path


def read_cli_captures(root: Path, name: str) -> list:
    """Nur die `kind=="input"`-Eintraege (bestehende Erhalt-Vertrag: jeder
    Eintrag hat `argv`/`stdin`/`pid`) -- `_a24_finish`s neue, zusaetzliche
    `kind=="own_output"`-Eintraege im selben Capture-File werden hier NICHT
    mitgezaehlt/durchgereicht (keine Veraenderung der bestehenden `len(...)`-
    /`c["stdin"]`-Erhaltassertions). S. `read_cli_output_captures` fuer die
    neuen eigenen Fake-Ausgangsbelege."""
    return [r for r in read_jsonl(root / f"{name}.capture.jsonl") if r.get("kind", "input") == "input"]


def read_cli_output_captures(root: Path, name: str) -> list:
    """G6-O: die vom Fake-Prozess SELBST unmittelbar vor seinem Exit
    geschriebenen/geflushten rohen Ausgangsbytes (`_a24_finish`) -- die
    EIGENE, geplante Seite (`kind=="own_output"`, `pid`+`planned_returncode`
    +`stdout`+`stderr`), AUSDRUECKLICH getrennt von der vom tatsaechlichen
    Elternprozess beobachteten Seite (`read_cli_parent_observations`unten)."""
    return [r for r in read_jsonl(root / f"{name}.capture.jsonl") if r.get("kind") == "own_output"]


def cli_queue_remaining(root: Path, name: str) -> list:
    qp = root / f"{name}.queue.json"
    if not qp.exists():
        return []
    return json.loads(qp.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# G6-O: echte Elternseite der Hybrid-CLI-Aufrufe (passives Popen-Observer-
# Muster, s. `_a23_vorlauf_support._OBSERVER`/`_a23_popen_init`/
# `_a23_popen_communicate` -- hier testlokal fuer A24 integriert, KEINE
# Aenderung an `_a23_vorlauf_support.py` oder `persona_claude_code.py:
# _RealProcessRunner` selbst). `_RealProcessRunner.run()` ruft innerhalb des
# echten TUI-Kindprozesses unveraendert `subprocess.run(argv, input=stdin,
# capture_output=True, text=True, env=env, cwd=cwd, timeout=120)` auf --
# `subprocess.run` baut daraus intern GENAU EIN `Popen(...)` +
# `.communicate(...)`. Ein `sitecustomize.py`, das NUR in diesem TUI-
# Kindprozess (nicht im Testprozess selbst) geladen wird, patcht beide
# Methoden rein beobachtend (kein injiziertes Testdouble, keine veraenderte
# Rueckgabe) und schreibt NACH jedem tatsaechlich abgeschlossenen Aufruf
# PID/PPID/argv/cwd + den vom ECHTEN Elternprozess beobachteten
# Returncode/stdout/stderr (inkl. Timeout-/Fehlerfall) in ein eigenes
# Audit-Journal -- "geplanter Exit im Fake ist noch kein vom Elternprozess
# beobachteter Exit" (02_AUFTRAG_G6_REST.md §3).
# --------------------------------------------------------------------------

_A24_CLI_OBSERVER = r'''
import base64 as _a24o_b64, hashlib as _a24o_hashlib, json as _a24o_json, os as _a24o_os
import pathlib as _a24o_pathlib, subprocess as _a24o_subprocess, time as _a24o_time
_a24o_dir = _a24o_pathlib.Path(__A24_CLI_AUDIT_DIR__)
_a24o_dir.mkdir(parents=True, exist_ok=True)


def _a24o_write(name, rec):
    with (_a24o_dir / name).open("a", encoding="utf-8") as _a24o_fh:
        _a24o_fh.write(_a24o_json.dumps(rec, ensure_ascii=False) + "\n")
        _a24o_fh.flush()
        _a24o_os.fsync(_a24o_fh.fileno())


_a24o_init = _a24o_subprocess.Popen.__init__
_a24o_communicate = _a24o_subprocess.Popen.communicate


def _a24o_popen_init(self, *args, **kw):
    self._a24o_start = _a24o_time.time()
    _a24o_init(self, *args, **kw)
    _a24o_env = kw.get("env") or {}
    self._a24o_curated_env = {
        k: v for k, v in _a24o_env.items()
        if k in ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "TERM", "SHELL")
    }
    _a24o_write("spawns.jsonl", {
        "pid": self.pid, "ppid": _a24o_os.getpid(), "argv": list(self.args),
        "cwd": kw.get("cwd"), "curated_env": self._a24o_curated_env, "started_utc": self._a24o_start,
    })


def _a24o_popen_communicate(self, *args, **kw):
    try:
        result = _a24o_communicate(self, *args, **kw)
    except BaseException as exc:
        if not getattr(self, "_a24o_recorded", False):
            self._a24o_recorded = True
            _a24o_write("process-results.jsonl", {
                "pid": self.pid, "ppid": _a24o_os.getpid(), "argv": list(self.args),
                "returncode": self.returncode, "started_utc": self._a24o_start, "ended_utc": _a24o_time.time(),
                "stdout": None, "stderr": None, "communicate_error": repr(exc),
            })
        raise
    if not getattr(self, "_a24o_recorded", False):
        self._a24o_recorded = True

        def _a24o_enc(value):
            if value is None:
                return None
            data = value.encode("utf-8") if isinstance(value, str) else value
            return {
                "b64": _a24o_b64.b64encode(data).decode(), "sha256": _a24o_hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
                "capture": "text-mode UTF-8 re-encoding" if isinstance(value, str) else "raw pipe bytes",
            }
        _a24o_write("process-results.jsonl", {
            "pid": self.pid, "ppid": _a24o_os.getpid(), "argv": list(self.args),
            "returncode": self.returncode, "started_utc": self._a24o_start, "ended_utc": _a24o_time.time(),
            "stdout": _a24o_enc(result[0]), "stderr": _a24o_enc(result[1]), "communicate_error": None,
        })
    return result


_a24o_subprocess.Popen.__init__ = _a24o_popen_init
_a24o_subprocess.Popen.communicate = _a24o_popen_communicate
'''


def write_a24_cli_observer_guard(dest_dir: Path, audit_dir: Path) -> Path:
    """Baut einen EIGENEN Guard-Ordner fuer die Umgebung des echten Hybrid-
    TUI-Kindprozesses: derselbe unveraenderte Loopback-Socket-Guard wie
    `_h02_vollreise_support.write_loopback_guard` (bytegleicher Inhalt,
    NUR gelesen/kopiert -- diese Quelldatei bleibt unveraendert), ERGAENZT
    um `_A24_CLI_OBSERVER` (analog `_a23_vorlauf_support.run_tui`s eigenem
    Anhaengemuster an eine KOPIE des Guards, NIE am Original). Rueckgabe:
    Verzeichnis, das der Aufrufer VORNE in `PYTHONPATH` einreiht."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)
    guard_source = _h02sup._LOOPBACK_GUARD_SOURCE + _A24_CLI_OBSERVER.replace(
        "__A24_CLI_AUDIT_DIR__", repr(str(audit_dir)),
    )
    (dest_dir / "sitecustomize.py").write_text(guard_source, encoding="utf-8")
    return dest_dir


def read_cli_parent_observations(audit_dir: Path) -> dict:
    """Liest die vom ECHTEN TUI-Elternprozess (nicht vom Fake-CLI selbst)
    beobachteten `spawns`/`process-results`-Journale (s. `_A24_CLI_
    OBSERVER`) -- leer, wenn der Guard nie geladen wurde (kein Fehlalarm,
    kein erfundener Eintrag)."""
    audit_dir = Path(audit_dir)
    return {
        "spawns": read_jsonl(audit_dir / "spawns.jsonl"),
        "process_results": read_jsonl(audit_dir / "process-results.jsonl"),
    }


def join_cli_parent_observations(fake_inputs: list, parent_observations: dict) -> dict:
    """G6-O ('Pro realer Modelloperation eindeutigen Join ... Mehrdeutigkeit
    ist ein Befund, keine Zuordnung durch bloße Listenposition'): bindet
    JEDEN eigenen Fake-CLI-Eingangsbeleg (`fake_inputs`, `read_cli_captures`,
    `kind=="input"`, eigener `pid`) an GENAU den vom echten Elternprozess
    beobachteten Spawn-/Ergebniseintrag MIT DEMSELBEN `pid` -- der `pid` ist
    das einzige tatsaechlich auf beiden Seiten vorhandene gemeinsame Feld
    (die Fake-CLI meldet ihre EIGENE `os.getpid()`, der Observer beobachtet
    denselben Wert als `Popen.pid` des von ihm gestarteten Kindes). Liefert
    `{"joined": [...], "unmatched_inputs": [...], "ambiguous_pids": [...]}`
    -- ein `pid`, der mehrfach unter `spawns`/`process_results` auftritt
    (OS-PID-Wiederverwendung innerhalb desselben kurzen Testlaufs), wird als
    `ambiguous_pids`-Befund gemeldet, NIE stillschweigend per Listenposition
    aufgeloest."""
    spawns_by_pid: dict = {}
    ambiguous: set = set()
    for rec in parent_observations.get("spawns", []):
        pid = rec.get("pid")
        if pid in spawns_by_pid:
            ambiguous.add(pid)
        spawns_by_pid.setdefault(pid, rec)
    results_by_pid: dict = {}
    for rec in parent_observations.get("process_results", []):
        pid = rec.get("pid")
        if pid in results_by_pid:
            ambiguous.add(pid)
        results_by_pid.setdefault(pid, rec)
    joined: list = []
    unmatched: list = []
    for cap in fake_inputs:
        pid = cap.get("pid")
        spawn = spawns_by_pid.get(pid)
        result = results_by_pid.get(pid)
        if pid in ambiguous or spawn is None or result is None:
            unmatched.append(cap)
            continue
        joined.append({
            "pid": pid, "fake_input": cap, "parent_spawn": spawn, "parent_result": result,
        })
    return {"joined": joined, "unmatched_inputs": unmatched, "ambiguous_pids": sorted(ambiguous)}


# --------------------------------------------------------------------------
# G6-O-Nacharbeit (02_AUFTRAG_G6_REST.md #5, IMPLEMENTIERUNGSWEG Punkt 5):
# DAUERHAFTE, testlokal integrierte Fassung derselben Ledger-/Rollen-/
# Akteur-/Turn-/Tisch-/Consent-/Reflexions-Zuordnung wie das externe, rein
# lesende `audit_g6_chain.py` (P/tools) -- hier als harte Assertion in der
# PERMANENTEN A24-Suite, nicht nur als separat zitierte Audit-Summe aus
# einem eigenstaendigen Tool-Lauf. Mechanisch 1:1 aus `audit_g6_chain.py`s
# Pro-Fall-Schleife uebernommen (jedes `ck(name, ok, detail)` wird hier zu
# einem sofortigen `assert`), NUR an bereits im Testprozess vorhandene
# Objekte (Table-Instanz statt reinem dict, in-memory HTTP-/CLI-Records
# statt erneut von Platte gelesener Capture-JSONs) angepasst.
# --------------------------------------------------------------------------

def audit_g6_chain_for_case(
    *, case_name: str, run_dir: Path, table, initial: dict,
    gm: list, persona: list | None = None,
    cli_input_captures: list | None = None, cli_output_captures: list | None = None,
    cli_parent_observations: dict | None = None,
    reflections: list, invitation_decisions: list,
) -> dict:
    """G6-O: siehe Modulkommentar oben. `persona` (Persona-HTTP-Pfad) ODER
    `cli_input_captures`+`cli_output_captures`+`cli_parent_observations`
    (Hybrid-CLI-Pfad) -- genau einer der beiden Quellensaetze je Aufruf,
    identisch zur Fallunterscheidung in `audit_g6_chain.py`. Jede fehlende/
    mehrdeutige/widerspruechliche Zuordnung ist ein sofortiger
    `AssertionError` (semantischer Testfehler, s. Auftrag), kein nur
    protokollierter Befund. Rueckgabe: `{"checks": [...], "satisfied": n,
    "total": n, ...}` -- fuer die eigene Lieferung/Beleglage, NICHT als
    Ersatz fuer die Assertions selbst (die bereits beim Aufruf greifen)."""
    checks: list = []
    sha = lambda b: hashlib.sha256(b).hexdigest()

    def ck(name, ok, detail=None):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})
        assert ok, f"audit_g6_chain_for_case[{case_name}] FAILED {name}: {detail}"

    ledgers = [
        (p, json.loads(p.read_text(encoding="utf-8")))
        for p in sorted((Path(run_dir) / "requests").glob("*.json"))
    ]

    def findledger(ts, gmrole):
        found = [
            (p, r) for p, r in ledgers
            if r.get("sent_ts", float("inf")) <= ts <= r.get("settled_ts", -1)
            and (r["role"] == "gm_turn") == gmrole
        ]
        ck(case_name + ":unique-time-role-join", len(found) == 1, {"timestamp": ts, "matches": len(found)})
        return found[0]

    used: list = []
    mappings: list = []
    for i, g in enumerate(gm):
        inp = json.loads(base64.b64decode(g["request_raw_b64"]))
        out = json.loads(base64.b64decode(g["response_raw_b64"]))
        ck(case_name + ":http-body", inp == g["body"] and out["choices"][0]["message"]["content"] == g["response_content"])
        ck(case_name + ":http-write", g["write_ok"] is True and not g["rejected"] and g["responded_wall_ts"] >= g["received_wall_ts"])
        p, r = findledger(g["received_wall_ts"], True)
        used.append(r["id"])
        last = g["body"]["messages"][-1]["content"]
        ck(case_name + ":gm-ledger-content", sha(last.encode()) == r["content_sha256"] and len(last) == r["content_chars"])
        ck(
            case_name + ":gm-durable-content",
            table.sl_log[i]["content"] == g["response_content"] and table.sl_log[i]["leader_message"] == last,
        )
        expected_history = []
        for previous in gm[:i]:
            expected_history.extend([
                {"role": "user", "content": previous["body"]["messages"][-1]["content"]},
                {"role": "assistant", "content": previous["response_content"]},
            ])
        ck(case_name + ":full-historical-gm-user-assistant", g["body"]["messages"][:-1] == expected_history)
        ck(
            case_name + ":gm-identity",
            r["turn_idx"] == i and r["table_id"] == table.table_id
            and r["participant"] == table.sl_log[i]["origin_persona_key"],
        )
        mappings.append({"case": case_name, "operation": "gm", "request_id": r["id"], "response_seq": i})

    hybrid = cli_input_captures is not None
    raw_origins: list = []
    sources: list = []
    if hybrid:
        owns = cli_output_captures or []
        parents = cli_parent_observations or {"spawns": [], "process_results": []}
        for x in cli_input_captures:
            own = [rec for rec in owns if rec.get("pid") == x.get("pid")]
            result = [rec for rec in parents.get("process_results", []) if rec.get("pid") == x.get("pid")]
            spawn = [rec for rec in parents.get("spawns", []) if rec.get("pid") == x.get("pid")]
            ck(
                case_name + ":cli-unique-three-sided-pid", len(own) == len(result) == len(spawn) == 1,
                {"pid": x.get("pid"), "own": len(own), "result": len(result), "spawn": len(spawn)},
            )
            o, z, sp = own[0], result[0], spawn[0]
            ck(
                case_name + ":cli-exit", z["returncode"] == o["planned_returncode"] == 0 and z["communicate_error"] is None,
                {"pid": x.get("pid")},
            )
            ck(
                case_name + ":cli-identity",
                x["ppid"] == z["ppid"] == sp["ppid"] and x["argv"] == sp["argv"][1:] and x["cwd"] == sp["cwd"],
                {"pid": x.get("pid")},
            )
            for channel in ("stdout", "stderr"):
                v = z[channel]
                b = base64.b64decode(v["b64"])
                ck(case_name + f":parent-{channel}-hash", sha(b) == v["sha256"] and len(b) == v["bytes"], {"pid": x.get("pid")})
                ck(case_name + f":own-parent-{channel}-text", b.decode("utf-8") == o[channel], {"pid": x.get("pid")})
                own_bytes = (o.get(channel) or "").encode("utf-8")
                saved_bytes = base64.b64decode(o[channel + "_b64"], validate=True)
                ck(case_name + f":own-{channel}-raw-bytes", saved_bytes == own_bytes and o["write_flush_succeeded"] is True)
                ck(
                    case_name + f":own-output-self-{channel}-hash",
                    sha(own_bytes) == o.get(channel + "_sha256") and len(own_bytes) == o.get(channel + "_len"),
                    {"pid": x.get("pid")},
                )
            ck(case_name + ":cli-time", x["wall_ts"] <= o["wall_ts"] <= z["ended_utc"], {"pid": x.get("pid")})
            ck(case_name + ":cli-full-LF", o["stdout"].endswith("\n"), {"pid": x.get("pid")})
            raw_origins.append({
                "pid": x.get("pid"), "own_format": "Unicode text captured after sys.stdout.buffer.write/flush",
                "parent_format": z["stdout"]["capture"], "independent_raw_pipe_capture": False,
            })
            sources.append({"ts": x["wall_ts"], "text": x["stdin"], "output": json.loads(o["stdout"])["result"], "pid": x.get("pid")})
    else:
        for x in (persona or []):
            ck(case_name + ":persona-http-write", x["write_ok"] and not x["rejected"])
            out = json.loads(base64.b64decode(x["response_raw_b64"]))
            sources.append({
                "ts": x["received_wall_ts"],
                "text": "\n\n".join(m["content"] for m in x["body"]["messages"]),
                "output": out["choices"][0]["message"]["content"], "http_seq": x["seq"],
            })

    for x in sources:
        p, r = findledger(x["ts"], False)
        used.append(r["id"])
        actor = r["participant"]
        text = x["text"]
        curmarker = "Eigener aktueller Spielstand (Current, vollstaendig): "
        ck(case_name + ":actor-from-ledger", f"— {actor} spielt " in text, {"actor": actor})
        pos = text.find(curmarker)
        ck(case_name + ":current-present", pos >= 0, {"actor": actor})
        if pos >= 0:
            current, _end = json.JSONDecoder().raw_decode(text, pos + len(curmarker))
            ck(case_name + ":own-current-full", current == initial[actor], {"actor": actor})
        marker = "[OEFFENTLICHE_TISCHSICHT]\n"
        if marker in text:
            view = json.loads(text.split(marker, 1)[1])
            n = r["turn_idx"]
            ck(
                case_name + ":full-public-prefix",
                [v["content"] for v in view["sl_log"]] == [v["response_content"] for v in gm[:n]],
            )
            ck(
                case_name + ":view-vs-ledger",
                view["table_id"] == r["table_id"] == table.table_id and view["leader"] == table.leader
                and sorted(view["members"]) == sorted(table.members),
            )
        dest = []
        if r["role"] in ("lead_invite", "guest_invite"):
            ids = re.findall(r"offer_id=([^\s]+)", x["output"])
            dec = re.findall(r"decision=([^\s]+)", x["output"])
            dest = [
                ("invitation_decisions.jsonl", i) for i, v in enumerate(invitation_decisions)
                if v.get("from") == actor and v.get("offer_id") in ids and v.get("decision") in dec
            ]
        elif r["role"] == "reflection":
            dest = [
                ("reflections.jsonl", i) for i, v in enumerate(reflections)
                if v.get("persona_key") == actor and v.get("section_id") == r["section_id"]
                and v.get("text") == x["output"] and v.get("kind") == "ai_required_reflection"
            ]
        elif r["role"] == "guest_poll":
            dest = [
                ("table_messages", i) for i, v in enumerate(table.table_messages)
                if v.get("from") == actor and v.get("text") == x["output"]
            ]
        elif r["role"] == "persona_decision":
            dest = [
                ("sl_log", i) for i, v in enumerate(table.sl_log)
                if v.get("origin_persona_key") == actor and v.get("turn_idx") == r["turn_idx"]
                and (
                    v["leader_message"] == x["output"]
                    or (v.get("save_payload") == initial[actor] and v["leader_message"].startswith(x["output"] + "\n\n```json\n"))
                )
            ]
        ck(case_name + ":unique-persisted-response", len(dest) == 1, {"actor": actor, "role": r["role"], "matches": dest})
        mappings.append({"case": case_name, "operation": r["role"], "actor": actor, "request_id": r["id"], "persisted_matches": dest})

    ck(
        case_name + ":all-records-once",
        len(used) == len(set(used)) == len(ledgers) and set(used) == {r["id"] for p, r in ledgers},
        {"used": len(used), "ledgers": len(ledgers)},
    )
    st = json.loads((Path(run_dir) / "lab.status.json").read_text(encoding="utf-8"))
    ck(
        case_name + ":accounting-set",
        st["turns_used"] == len(ledgers) and set(st["reconciled_seconds_request_ids"]) == set(used),
        {"turns_used": st.get("turns_used"), "ledgers": len(ledgers)},
    )

    return {
        "case": case_name, "gm_records": len(gm), "source_records": len(sources), "ledger_records": len(ledgers),
        "checks": checks, "satisfied": sum(c["ok"] for c in checks), "total": len(checks),
        "mappings": mappings, "cli_raw_boundary": raw_origins,
    }


# --------------------------------------------------------------------------
# Echter Subprozess-Dispatch (das eigentliche Testsubjekt)
# --------------------------------------------------------------------------

def run_process(data_dir: Path, participant: str, stdin_text: str, env_extra: dict, timeout: int = 60) -> subprocess.CompletedProcess:
    """Ein ECHTER, EIGENSTAENDIGER Python-Subprozess gegen den
    tatsaechlichen `scripts/mmo_sim.py`-Einstiegspunkt -- kein In-Prozess-
    `TuiSession`-Aufruf. `env_extra` wird an die GEERBTE Umgebung angehaengt
    (gleiches Muster wie `e2e_real_subprocess_dialog.py:run_process`) --
    dadurch erbt das TUI-Kind insbesondere den bereits vom kontrollierten
    Runner gesetzten `PYTHONPATH` (Loopback-Guard + jsonschema-Dependency-
    Sichtbarkeit), was fuer den Nachweis 'Guard/Schema im echten TUI-Kind
    sichtbar' noetig ist."""
    env = dict(os.environ)
    env.update(env_extra)
    cmd = [sys.executable, str(MMO_SIM), "--data-dir", str(data_dir), "--participant", participant]
    return subprocess.run(
        cmd, input=stdin_text, capture_output=True, text=True, env=env, cwd=str(data_dir), timeout=timeout,
    )


def run_process_paced(
    data_dir: Path, participant: str, steps: list, env_extra: dict, *,
    timeout: int = 90, checkpoints: dict | None = None,
) -> dict:
    """R3 (02_AUFTRAG_R2_R3.md §R3 'echte mittlere Eingabebarriere ...
    Skriptinput erst nach tatsaechlich ausgegebenem relevantem Prompt
    weitergeben'): im Unterschied zu `run_process()` (ganzer `stdin_text`
    auf einmal via `subprocess.run(input=...)`, Elternprozess liest
    stdout/stderr erst NACH Prozessende -- kein echter Zwischenzustand
    beobachtbar) wird hier JEDE Zeile aus `steps` -- `(erwarteter_prompt_
    teilstring, zu_sendende_zeile)` -- ERST geschrieben, NACHDEM der
    erwartete Teilstring TATSAECHLICH im bisher vom Kindprozess
    geschriebenen stdout erschienen ist (kein fester `sleep`, keine blosse
    Ruhephasen-Heuristik: ein Kind, das zwischen zwei Prompts intern
    rechnet/wartet, wuerde eine reine Stille-Erkennung zu frueh ausloesen
    -- selbst erprobt und verworfen). CPython `input()` flusht seinen
    Prompt immer VOR dem Blockieren auf stdin (generischer Pfad bei Pipe-
    stdin/stdout, kein TTY, s. `mmo_sim/ui/tui.py:_readline` -> eingebautes
    `input`): das tatsaechliche Erscheinen des Prompt-Teilstrings im
    bisherigen stdout ist daher ein echter Beleg, dass der Kindprozess an
    GENAU dieser Stelle an `input()` haengt -- kein geschaetzter Call-
    Zeitpunkt. `steps[i][0]` kann `None` sein, wenn (z.B. unmittelbar nach
    Prozessstart) noch kein spezifischer Prompt bekannt ist; dann wird nur
    auf irgendein erstes Byte gewartet.

    `checkpoints`: optionales `{zeilen_index: (erwarteter_teilstring,
    capture_fn_oder_None)}`. VOR dem Schreiben von `steps[zeilen_index][1]`
    wird zusaetzlich hart geprueft, dass der erwartete Teilstring
    TATSAECHLICH im bisherigen stdout erscheint (sonst AssertionError --
    kein stiller Weiterlauf ohne echten Beleg; redundant zu `steps[i][0]`,
    falls dort bereits derselbe Teilstring gesetzt ist, aber eigenstaendig
    verwendbar); `capture_fn(stdout_so_far)` wird GENAU in diesem Moment
    aufgerufen, um einen echten Zwischenschnappschuss (z.B. Dateisystem)
    VOR Cleanup zu sichern, waehrend der Kindprozess nachweislich noch an
    dieser Stelle blockiert.

    Gibt vollstaendige stdout/stderr-ROHBYTES (inkl. LF), PID, argv, cwd,
    returncode und ein Step-Journal (tatsaechliche Wartezeiten je Zeile)
    zurueck -- kein Erfolg aus dem Returncode allein."""
    env = dict(os.environ)
    env.update(env_extra)
    cmd = [sys.executable, str(MMO_SIM), "--data-dir", str(data_dir), "--participant", participant]
    proc = subprocess.Popen(
        cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=str(data_dir), env=env, bufsize=0,
    )
    checkpoints = checkpoints or {}
    out_buf = bytearray()
    err_buf = bytearray()
    step_journal: list = []
    sel = selectors.DefaultSelector()
    sel.register(proc.stdout, selectors.EVENT_READ, "out")
    sel.register(proc.stderr, selectors.EVENT_READ, "err")
    start = time.monotonic()

    def _drain_once(poll_timeout: float) -> bool:
        got = False
        for key, _ in sel.select(timeout=poll_timeout):
            try:
                data = os.read(key.fileobj.fileno(), 65536)  # type: ignore[union-attr]
            except OSError:
                data = b""
            if data:
                got = True
                (out_buf if key.data == "out" else err_buf).extend(data)
        return got

    def _wait_for(expect_substring: "str | None", search_from: int, deadline: float) -> None:
        """Blockiert NUR bis `expect_substring` tatsaechlich NEU seit
        `search_from` (Pufferlaenge nach dem vorherigen Versand) im stdout
        erscheint -- NICHT irgendwann frueher im kumulierten Puffer (sonst
        wuerde ein wiederholter Prompttext wie 'Deine Aktion:' ab seinem
        zweiten Auftreten sofort faelschlich als 'erreicht' gelten, ohne
        dass das Kind den NEUEN Prompt tatsaechlich schon ausgegeben hat).
        Faellt, falls `None`, auf 'irgendein neues Byte seit `search_from`'
        zurueck. Niemals aus blosser Stille -- ein rechnendes/wartendes
        Kind zwischen zwei Prompts loest so keinen verfruehten Versand aus."""
        while True:
            new_bytes = bytes(out_buf)[search_from:]
            if expect_substring is None:
                if len(new_bytes) > 0 or proc.poll() is not None:
                    return
            elif expect_substring.encode("utf-8", errors="replace") in new_bytes:
                return
            elif proc.poll() is not None:
                return
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"run_process_paced: Timeout -- erwarteter Prompt/Beleg {expect_substring!r} "
                    f"nicht NEU im stdout seit Position {search_from} erschienen (keine echte "
                    f"Barriere erreicht): ...{new_bytes.decode('utf-8', errors='replace')[-600:]}"
                )
            _drain_once(0.05)

    try:
        search_from = 0
        for i, (expect_prompt, line) in enumerate(steps):
            deadline = start + timeout
            _wait_for(expect_prompt, search_from, deadline)
            if i in checkpoints:
                expect_substring, capture_fn = checkpoints[i]
                text_so_far = bytes(out_buf).decode("utf-8", errors="replace")
                assert expect_substring in text_so_far, (
                    f"Checkpoint vor Zeile {i}: erwarteter Prompt/Beleg {expect_substring!r} "
                    f"NICHT im bisherigen stdout gefunden (kein echter Zwischenzustand): "
                    f"...{text_so_far[-600:]}"
                )
                if capture_fn is not None:
                    capture_fn(bytes(out_buf))
            if proc.poll() is not None:
                step_journal.append({"line_index": i, "sent": False, "reason": "process already exited"})
                break
            proc.stdin.write((line + "\n").encode("utf-8"))  # type: ignore[union-attr]
            proc.stdin.flush()  # type: ignore[union-attr]
            step_journal.append({
                "line_index": i, "sent": True, "expect_prompt": expect_prompt,
                "waited_seconds": round(time.monotonic() - start, 3),
                "stdout_len_at_send": len(out_buf),
            })
            search_from = len(out_buf)
        try:
            proc.stdin.close()  # type: ignore[union-attr]
        except Exception:
            pass
        proc.wait(timeout=max(1.0, timeout - (time.monotonic() - start)))
        _drain_once(0.2)
    finally:
        sel.close()
    return {
        "returncode": proc.returncode, "pid": proc.pid, "argv": cmd, "cwd": str(data_dir),
        "stdout": bytes(out_buf), "stderr": bytes(err_buf), "step_journal": step_journal,
        "timeout_seconds": timeout,
    }


def snapshot_run_tree(run_dir: Path, dest: Path) -> dict:
    """R3 ('vollstaendige Registry-/Katalog-/State-/Current-/Versions-/
    Consent-/Request-/Tisch-/Completion-/Lockdaten soweit in dieser Phase
    vorhanden ... Fehlende Datei als Nichtvorhandensein erfassen'): kopiert
    + hasht GENAU im Moment des Aufrufs die tatsaechlich vorhandenen,
    tischrelevanten Unterbaeume (`tables`, `current_saves`, `reflections.
    jsonl`, `community`) von `run_dir` nach `dest` -- ein echter
    Dateisystem-Beleg, kein aus dem Endzustand rekonstruierter Fokusevent.
    Ein fehlender Pfad wird als `None` erfasst, NIE als spaetere Kopie
    stillschweigend uebersprungen."""
    dest.mkdir(parents=True, exist_ok=True)
    manifest: dict = {}
    for rel in ("tables", "current_saves", "reflections.jsonl", "community"):
        src = run_dir / rel
        if not src.exists():
            manifest[rel] = None
            continue
        if src.is_file():
            data = src.read_bytes()
            (dest / rel).write_bytes(data)
            manifest[rel] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
            continue
        entries: dict = {}
        out_dir = dest / rel
        for p in sorted(src.rglob("*")):
            if not p.is_file():
                continue
            relp = p.relative_to(src).as_posix()
            data = p.read_bytes()
            target = out_dir / relp
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            entries[relp] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
        manifest[rel] = entries
    return manifest


def debrief_blocks(final_saves: dict) -> str:
    return "\n".join(f"```json\n{json.dumps(b, ensure_ascii=False)}\n```" for b in final_saves.values())


def end_save_for(base_save: dict, tag: str, run_tag: str) -> dict:
    """R3 (02_AUFTRAG_A24.md §R3 'genau FUENF volle individuelle Endsaves mit
    deutlich unterscheidbaren synthetischen End-Save-IDs, nicht Ausgangs-
    payload wiederholen'): eigene, vom Onboarding-/Fixture-Ausgangsstand
    UNTERSCHIEDENE Kopie desselben v7-Blocks (gleicher `char_id` -- der
    Routingschluessel `zeitriss_saves.block_char_id` darf sich nicht aendern
    -- aber eigener, eindeutiger `save_id`), die der GM-Debrief tatsaechlich
    sendet. Reiner Testfixture-Helfer, keine Produktaenderung."""
    end = json.loads(json.dumps(base_save, ensure_ascii=False))
    end["save_id"] = f"{base_save.get('save_id', 'save')}-END-{tag}-{run_tag}"
    end["_a24_end_save_note"] = "SIMULIERT/FIXTURE -- synthetischer Endstand nach A24-Testrunde, kein Ausgangspayload."
    return end


def end_saves_for(final_saves: dict, run_tag: str) -> dict:
    return {pk: end_save_for(block, pk, run_tag) for pk, block in final_saves.items()}


_GUARD_CHECK_SOURCE = (
    "import importlib.metadata, json, socket, sys\n"
    "out = {}\n"
    "try:\n"
    "    import sitecustomize\n"
    "    out['guard_module_file'] = getattr(sitecustomize, '__file__', None)\n"
    "    out['guard_patches_getaddrinfo'] = socket.getaddrinfo.__module__ == 'sitecustomize'\n"
    "except Exception as exc:\n"
    "    out['guard_error'] = repr(exc)\n"
    "try:\n"
    "    out['jsonschema_version'] = importlib.metadata.version('jsonschema')\n"
    "except Exception as exc:\n"
    "    out['jsonschema_error'] = repr(exc)\n"
    "print(json.dumps(out))\n"
)


def current_process_guard_state() -> dict:
    """Dieselbe Pruefung wie `_GUARD_CHECK_SOURCE`, aber IM LAUFENDEN
    Elternprozess selbst (kein Subprozess) -- Referenzwert fuer den
    Kontinuitaetsvergleich in `verify_child_guard_and_schema`. Laeuft dieser
    Testprozess selbst unter dem kontrollierten Reviewer (K-Paket-Guard im
    eigenen `PYTHONPATH`), ist `sitecustomize` hier bereits beim
    Interpreterstart automatisch geladen -- laeuft er standalone (normaler
    `run_all.py` OHNE Paket, 02_AUFTRAG_A24.md Pflicht), bleibt es die
    System-`sitecustomize`/keine Patch-Wirkung. Beide Faelle sind gueltig;
    der eigentliche Nachweis ist Kontinuitaet (Kind == Eltern), nicht eine
    absolute Guard-Pflicht fuer jeden Ausfuehrungskontext."""
    import importlib.metadata
    import socket
    out: dict = {}
    try:
        import sitecustomize
        out["guard_module_file"] = getattr(sitecustomize, "__file__", None)
        out["guard_patches_getaddrinfo"] = socket.getaddrinfo.__module__ == "sitecustomize"
    except Exception as exc:  # pragma: no cover - defensiv, kein Produktpfad
        out["guard_error"] = repr(exc)
    try:
        out["jsonschema_version"] = importlib.metadata.version("jsonschema")
    except Exception as exc:  # pragma: no cover
        out["jsonschema_error"] = repr(exc)
    return out


def verify_child_guard_and_schema(env: dict, cwd: Path, timeout: int = 20) -> dict:
    """Beweist Guardidentitaet + jsonschema-Sichtbarkeit NICHT nur im
    Elternprozess, sondern im ECHTEN Kind-Interpreter mit GENAU demselben
    Environment/Interpreter, das auch das reale TUI-Kind (`run_process()`)
    erhaelt (02_AUFTRAG_A24.md/07 §4: 'Guardidentitaet und Schema muessen im
    ECHTEN TUI-Kind mit dessen Interpreter/minimalem Environment sichtbar
    sein -- nachweisen, nicht nur im Elternprozess'). Eigener separater aber
    GLEICH-konfigurierter Subprozess (derselbe `sys.executable`, dasselbe
    `env`/`cwd`) -- die reale TUI selbst importiert kein Diagnoseschema, der
    Nachweis muss daher denselben Interpreterstart getrennt pruefen."""
    proc = subprocess.run(
        [sys.executable, "-c", _GUARD_CHECK_SOURCE], env=env, cwd=str(cwd),
        capture_output=True, text=True, timeout=timeout,
    )
    result = {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
    try:
        result["parsed"] = json.loads(proc.stdout.strip().splitlines()[-1]) if proc.stdout.strip() else {}
    except (json.JSONDecodeError, IndexError):
        result["parsed"] = {}
    return result


# Review proposal: a fixture-owned finite operation tape, never game authority.
# Shared verbatim with the executable Fake-CLI; stdlib only.
def _g6_gate_open(receipts_path, endpoint, texts, messages=None):
    import fcntl
    import time
    import json
    from pathlib import Path
    root = Path(str(receipts_path) + '.operations')
    lock = open(str(root) + '.lock', 'a+b')
    deadline = time.monotonic() + 5.0
    while True:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except BlockingIOError:
            if time.monotonic() >= deadline:
                lock.close()
                raise TimeoutError('G6 operation journal remained busy')
            time.sleep(0.002)  # bounded wait for the actual preceding journal writer
    try:
        plan = json.loads(Path(str(root) + '.plan.json').read_text(encoding='utf-8'))
        journal = Path(str(root) + '.journal.jsonl')
        history = [json.loads(s) for s in journal.read_text(encoding='utf-8').splitlines() if s] if journal.exists() else []
        offset = int(plan.get('event_offset', 0))
        current = len(history) - offset
        event = plan['events'][current] if 0 <= current < len(plan['events']) else None
        state = {'plan': plan, 'history': history, 'event': event, 'journal': journal,
                 'received_ts': time.time(), 'endpoint': endpoint, 'texts': texts, 'messages': messages}
        ok, reason = _g6_check_operation(endpoint, texts, messages, plan, history, event)
        return lock, state, ok, reason
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        return lock, None, False, 'missing/invalid independent operation plan: ' + repr(exc)
    except BaseException:
        _g6_gate_close(lock)
        raise


def _g6_gate_close(lock):
    import fcntl
    fcntl.flock(lock, fcntl.LOCK_UN)
    lock.close()


def _g6_gate_commit(state, output, *, wire_sha256, written_ts):
    import json
    import os
    record = {'sequence': len(state['history']), 'endpoint': state['endpoint'],
              'expected_event': state['event'], 'texts': state['texts'], 'messages': state['messages'],
              'output': output, 'wire_sha256': wire_sha256,
              'received_ts': state['received_ts'], 'written_ts': written_ts,
              'write_flush_succeeded': True}
    with state['journal'].open('a', encoding='utf-8') as fh:
        fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + '\n')
        fh.flush()
        os.fsync(fh.fileno())


def _g6_check_operation(endpoint, texts, messages, plan, history, event):
    """The expected event is selected only by the immutable tape + past successful outputs.
    No actor, role, turn or expectation is selected from the wire under examination.
    """
    import json
    import re
    if not event or event.get('endpoint') != endpoint:
        return False, 'unexpected endpoint or exhausted operation tape'
    expected = plan['context']
    actor = event['actor']
    gm = [row for row in history if row['endpoint'] == 'gm']
    if len(gm) != event['prefix_count']:
        return False, 'independent phase/prefix count mismatch'
    if endpoint == 'gm':
        past = []
        for row in gm:
            past += [{'role': 'user', 'content': row['messages'][-1]['content']},
                     {'role': 'assistant', 'content': row['output']}]
        if not isinstance(messages, list) or messages[:-1] != past:
            return False, 'historical USER/ASSISTANT transcript differs from actual receipts'
        if not messages or messages[-1].get('role') != 'user':
            return False, 'current GM message must be user'
        if 'from_event' in event:
            idx = event['from_event']
            if not 0 <= idx < len(history):
                return False, 'missing actual chosen persona output'
            origin = history[idx]
            if origin['endpoint'] != 'persona' or origin['expected_event']['actor'] != actor:
                return False, 'chosen output belongs to another operation'
            chosen = origin['output']
        else:
            chosen = event['human_text']
        wire = messages[-1].get('content')
        if event['phase'] == 'load':
            pattern = re.escape(chosen) + r'\n\n```json\n(.*)\n```'
            match = re.fullmatch(pattern, wire or '', flags=re.S)
            if not match:
                return False, 'selected import text/framing mismatch'
            try:
                save = json.loads(match.group(1))
            except ValueError:
                return False, 'invalid selected import JSON'
            if save != expected['own_current_by_actor'][actor]:
                return False, 'import belongs to another selected figure'
        elif wire != chosen:
            return False, 'current GM text differs from actual chosen leader output/input'
        return True, 'exact expected GM operation'
    if endpoint != 'persona':
        return False, 'unsupported model endpoint'
    text = '\n\n'.join(texts)
    marker = 'Eigener aktueller Spielstand (Current, vollstaendig): '
    if text.count(marker) != 1:
        return False, 'exactly one own Current is required'
    before, after = text.split(marker, 1)
    headers = re.findall(r'\[BISHERIGER STAND — (.*?) spielt (.*?) "([^"]*)", (\d+) Runde\(n\) gespielt\]', before)
    if len(headers) != 1:
        return False, 'missing/ambiguous own header'
    own = expected['own_current_by_actor'][actor]
    char = own['characters'][0]
    if headers[0][:3] != (actor, char['name'], char['callsign']):
        return False, 'wire actor differs from independently selected operation'
    try:
        current, _ = json.JSONDecoder().raw_decode(after)
    except ValueError:
        return False, 'invalid current JSON'
    if current != own:
        return False, 'current differs from expected operation actor'
    view_marker = '[OEFFENTLICHE_TISCHSICHT]\n'
    is_reflection = 'PRIVATE_REFLECTION_SENTINEL' in text
    if event['role'] in ('guest_invite', 'lead_invite'):
        if view_marker in text or is_reflection:
            return False, 'invitation must not impersonate play/reflection'
        offers = re.findall(r'offer_id["\s]*[=:]\s*"?([^\s",}]+)', text)
        participants = re.findall(r'participant_id["\s]*[=:]\s*"?([^\s",}]+)', text)
        if not offers or set(offers) != {event['offer_id']} or not participants or set(participants) != {actor}:
            return False, 'invitation target/offer mismatch'
        if ('als Leader' in text) != (event['role'] == 'lead_invite'):
            return False, 'invitation role mismatch'
        return True, 'exact expected invitation'
    if is_reflection != (event['role'] == 'reflection'):
        return False, 'operation phase/reflection mismatch'
    if text.count(view_marker) != 1:
        return False, 'missing/ambiguous table view'
    try:
        view = json.loads(text.split(view_marker, 1)[1])
    except ValueError:
        return False, 'invalid table view'
    if (view.get('table_id') != expected['table_id'] or view.get('leader') != expected['leader']
            or sorted(view.get('members', [])) != expected['members']):
        return False, 'independently expected table/leader/members mismatch'
    entries = view.get('sl_log')
    if not isinstance(entries, list) or len(entries) != len(gm):
        return False, 'incomplete public prefix'
    for i, (entry, previous) in enumerate(zip(entries, gm)):
        if (entry.get('content') != previous['output']
                or entry.get('leader_message') != previous['messages'][-1]['content']
                or entry.get('turn_idx') != i):
            return False, 'public prefix differs from actual complete GM input/output'
    if 'consultations' in event:
        wanted = []
        for advice in event['consultations']:
            if 'from_event' in advice:
                j = advice['from_event']
                if not 0 <= j < len(history):
                    return False, 'missing actual guest consultation'
                output = history[j]['output']
            else:
                output = advice['human_text']
            wanted.append({'from': advice['actor'], 'text': output})
        if view.get('table_messages') != wanted:
            return False, 'guest consultation differs from actual output/planned human input'
    return True, 'exact expected persona operation'


def write_g6_operation_plan(receipts_path, expected_context, *, invite_actors, human_messages,
                            human_polls=None, play=True):
    """Create only test-oracle files BEFORE dispatch. Uses fixture choices, never received fields.
    The five imports and three ordinary GM turns are the existing fixed A24 journey.
    """
    import copy
    events = []
    ai = set(SIX_PERSONAS) & set(expected_context['members'])
    leader = expected_context['leader']
    guests = sorted(set(expected_context['members']) - {leader})
    human_polls = human_polls or {}
    guest_offer = next(x for x in expected_context['offer_ids'] if x.startswith('invite-'))
    for actor in invite_actors:
        lead = actor == leader and actor in ai
        offer = next(x for x in expected_context['offer_ids'] if x.startswith('lead-invite-')) if lead else guest_offer
        events.append({'endpoint': 'persona', 'actor': actor, 'role': 'lead_invite' if lead else 'guest_invite',
                       'phase': 'invite', 'prefix_count': 0, 'offer_id': offer})
    prefix = 0
    human_indexes = {k: 0 for k in human_messages}
    advice = []
    def person(actor, role, phase):
        idx = len(events)
        events.append({'endpoint': 'persona', 'actor': actor, 'role': role, 'phase': phase,
                       'prefix_count': prefix, 'consultations': copy.deepcopy(advice)})
        return idx
    def gm_turn(actor, phase):
        nonlocal prefix
        event = {'endpoint': 'gm', 'actor': actor, 'role': 'gm_turn', 'phase': phase, 'prefix_count': prefix}
        if actor in ai:
            event['from_event'] = person(actor, 'persona_decision', phase)
        else:
            index = human_indexes[actor]
            event['human_text'] = human_messages[actor][index]
            human_indexes[actor] += 1
        events.append(event)
        prefix += 1
    if play:
        for actor in [leader] + guests:
            gm_turn(actor, 'load')
        gm_turn(leader, 'play')
        for turn in (6, 7):
            for actor in guests:
                if actor in ai:
                    idx = person(actor, 'guest_poll', 'consult')
                    advice.append({'actor': actor, 'from_event': idx})
                else:
                    advice.append({'actor': actor, 'human_text': human_polls[actor][turn - 6]})
            gm_turn(leader, 'play')
        for actor in sorted(expected_context['members']):
            if actor in ai:
                person(actor, 'reflection', 'reflection')
    plan = {'schema': 'a24-independent-operation-tape-v1', 'context': copy.deepcopy(expected_context),
            'events': events, 'event_offset': 0, 'authority': 'synthetic fixture choices before dispatch; not game authority'}
    path = Path(str(receipts_path) + '.operations.plan.json')
    assert not path.exists(), 'Do not overwrite a previously used operation plan'
    write_json(path, plan)
    return plan


def assert_g6_operation_tape(receipts_path, *, require_complete=True):
    path = Path(str(receipts_path) + '.operations')
    plan = json.loads(Path(str(path) + '.plan.json').read_text())
    history = read_jsonl(Path(str(path) + '.journal.jsonl'))
    assert len(history) <= len(plan['events'])
    if require_complete:
        assert len(history) == len(plan['events']), 'G6: missing actual operations'
    for i, row in enumerate(history):
        assert row['sequence'] == i and row['expected_event'] == plan['events'][i]
        ok, reason = _g6_check_operation(row['endpoint'], row['texts'], row['messages'], plan, history[:i], plan['events'][i])
        assert ok, (i, reason)
        assert row['write_flush_succeeded'] is True and row['written_ts'] >= row['received_ts']
    return {'actual': len(history), 'planned': len(plan['events']), 'all_verified': True}


def _g6_shared_source():
    import inspect
    return '\n\n'.join(inspect.getsource(f) for f in
                       (_g6_gate_open, _g6_gate_close, _g6_gate_commit, _g6_check_operation))


def run_g6_exact_replays(sup, plan_file, history_file, output_dir, *, require_closed=True):
    """Existing G6 controls at actual HTTP/Fake-CLI, with one unchanged external operation.
    A rejected wire is followed by the original healthy wire at the SAME tape position.
    Original tape and receipts come from a completed independently planned healthy fixture.
    """
    import base64
    import copy
    import hashlib
    import json
    import os
    import subprocess
    import time
    import urllib.request
    from pathlib import Path
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    plan = json.loads(Path(plan_file).read_text())
    history = [json.loads(line) for line in Path(history_file).read_text().splitlines() if line]
    assert len(history) == len(plan['events'])
    assert plan['context'].get('allow_legacy_charid_fallback') is False
    def select(endpoint, actor, role, prefix):
        indexes = [i for i, event in enumerate(plan['events']) if event['endpoint'] == endpoint
                   and event['actor'] == actor and event['role'] == role and event['prefix_count'] == prefix]
        assert len(indexes) == 1, indexes
        return indexes[0]
    normal_index = select('persona', 'tech', 'guest_poll', 7)
    reflection_index = select('persona', 'tech', 'reflection', 8)
    gm_index = select('gm', plan['context']['leader'], 'gm_turn', 7)
    # This standard replay seed is deliberately the API/Human-Leader positive fixture.
    normal = copy.deepcopy(history[normal_index]['messages'])
    reflection = copy.deepcopy(history[reflection_index]['messages'])
    gm = copy.deepcopy(history[gm_index]['messages'])
    cases = []
    def add(name, index, messages, wanted):
        cases.append((name, index, messages, wanted))
    add('healthy-normal', normal_index, normal, True)
    add('healthy-reflection', reflection_index, reflection, True)
    def viewchange(messages, update):
        changed = copy.deepcopy(messages)
        head, tail = changed[-1]['content'].split('[OEFFENTLICHE_TISCHSICHT]\n', 1)
        view = json.loads(tail)
        update(view)
        changed[-1]['content'] = head + '[OEFFENTLICHE_TISCHSICHT]\n' + json.dumps(view, ensure_ascii=False, sort_keys=True)
        return changed
    add('known-fund-a', normal_index, viewchange(normal, lambda v: v.update(table_id='local-FORGED-LEADER-a-b', leader='FORGED-LEADER', members=['FORGED-LEADER','a','b'])), False)
    add('empty-public-prefix', normal_index, viewchange(normal, lambda v: v.update(sl_log=[])), False)
    add('reversed-public-prefix', normal_index, viewchange(normal, lambda v: v.update(sl_log=list(reversed(v['sl_log'])))), False)
    def trim(v):
        text = v['sl_log'][-1]['content']
        v['sl_log'][-1]['content'] = text[text.index('SECTION-ABSCHLUSS-BESTAETIGT'):]
    add('final-saveblocks-removed', reflection_index, viewchange(reflection, trim), False)
    foreign = copy.deepcopy(normal)
    marker = 'Eigener aktueller Spielstand (Current, vollstaendig): '
    head, _ = foreign[0]['content'].split(marker, 1)
    foreign[0]['content'] = head + marker + json.dumps(plan['context']['own_current_by_actor']['medic'], ensure_ascii=False, sort_keys=True)
    add('other-members-current', normal_index, foreign, False)
    incomplete_header = copy.deepcopy(foreign)
    incomplete_header[0]['content'] = incomplete_header[0]['content'].replace('— tech spielt ', '— medic spielt ')
    add('expected-tech-operation-relabelled-medic', normal_index, incomplete_header, False)
    full_header = copy.deepcopy(incomplete_header)
    tech = plan['context']['own_current_by_actor']['tech']['characters'][0]
    medic = plan['context']['own_current_by_actor']['medic']['characters'][0]
    full_header[0]['content'] = full_header[0]['content'].replace(
        '— medic spielt ' + tech['name'] + ' "' + tech['callsign'] + '"',
        '— medic spielt ' + medic['name'] + ' "' + medic['callsign'] + '"')
    assert '— medic spielt '+medic['name'] in full_header[0]['content']
    add('expected-tech-operation-complete-medic-header', normal_index, full_header, False)
    for name, messages in [('known-header-strip-foreign-current', foreign), ('headerless-healthy-not-production', normal)]:
        change = copy.deepcopy(messages)
        change[0]['content'] = ''.join(s for s in change[0]['content'].splitlines(keepends=True) if '[BISHERIGER STAND — ' not in s)
        add(name, normal_index, change, False)
    add('healthy-gm-history', gm_index, gm, True)
    for name, index, text in [
        ('gm-history-changed', 1, 'G6_CHANGED_ASSISTANT_REPLY'),
        ('gm-past-user-changed', 0, 'G6_CHANGED_OLD_USER_WITHOUT_SAVE'),
        ('gm-past-user-text-with-original-save', 0, 'G6_CHANGED_OLD_WORDS\n\n```json'+gm[0]['content'].split('```json',1)[1]),
        ('gm-current-leader-text-changed', -1, 'G6_CHANGED_CURRENT_LEADER_WORDS'),
    ]:
        change = copy.deepcopy(gm)
        change[index]['content'] = text
        add(name, gm_index, change, False)
    rows = []
    def write(path, data):
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    def seed(directory, index):
        directory.mkdir(parents=True, exist_ok=False)
        receipts = directory/'gm-receipts.jsonl'
        receipts.write_text(''.join(json.dumps(r['output'], ensure_ascii=False)+'\n' for r in history[:index] if r['endpoint']=='gm'))
        root = Path(str(receipts)+'.operations')
        write(Path(str(root)+'.plan.json'), {'schema':plan['schema'], 'context':plan['context'],
              'events':[plan['events'][index]], 'event_offset':index,
              'authority':'explicit isolated replay of original independent operation; not inferred from corrupted wire'})
        Path(str(root)+'.journal.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in history[:index]))
        return receipts
    for name, index, messages, wanted in cases:
        case = output_dir/name
        case.mkdir()
        event = plan['events'][index]
        original_messages = history[index]['messages']
        write(case/'source-binding.json', {'original_event_index':index,'expected_event':event,
              'expected_context_sha256':hashlib.sha256(json.dumps(plan['context'],sort_keys=True).encode()).hexdigest(),
              'original_request':original_messages, 'source_plan_sha256':hashlib.sha256(Path(plan_file).read_bytes()).hexdigest(),
              'same_expectation_for_healthy_and_corrupt':True})
        write(case/'changed-request.json', messages)
        receipts = seed(case/'http', index)
        server = sup.SequencedHTTPServer([], lambda i,b:'G6_REPLAY_ACCEPTED', expected_context=plan['context'],
                                        gm_receipts_path=receipts, is_gm_server=event['endpoint']=='gm')
        http = []
        requests = [messages] if wanted else [messages, original_messages]
        with server:
            for n, msg in enumerate(requests):
                raw = json.dumps({'messages':msg},ensure_ascii=False).encode()
                req = urllib.request.Request(server.base_url,data=raw,headers={'Content-Type':'application/json'},method='POST')
                with urllib.request.urlopen(req,timeout=10) as response:
                    out=response.read();status=response.status
                (case/f'http-request-{n}.bin').write_bytes(raw)
                (case/f'http-response-{n}.bin').write_bytes(out)
                result=json.loads(out)['choices'][0]['message']['content']
                http.append({'accepted':result=='G6_REPLAY_ACCEPTED','semantic_rejection':'A24_DOUBLE_REJECTED' in result,
                             'status':status, 'response_sha256':hashlib.sha256(out).hexdigest()})
        write(case/'http-records.json', server.received)
        cli = []
        if event['endpoint']=='persona':
            cli_receipts=seed(case/'cli', index)
            fake=sup.write_queued_fake_cli(case/'cli',name='exact',queue=[{'result':'G6_REPLAY_ACCEPTED'}],
                                            expected_context=plan['context'],gm_receipts_path=cli_receipts)
            for n,msg in enumerate(requests):
                raw=('[SYSTEM]\n'+msg[0]['content']+'\n\n[USER]\n'+msg[-1]['content']).encode()
                p=subprocess.Popen([str(fake)],cwd=case/'cli',env={'PATH':os.environ['PATH'],'HOME':str(case/'cli'),
                   'LANG':'C.UTF-8','LC_ALL':'C.UTF-8','PYTHONDONTWRITEBYTECODE':'1'},stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                out,err=p.communicate(raw,timeout=15)
                (case/f'cli-stdin-{n}.bin').write_bytes(raw)
                (case/f'cli-stdout-{n}.bin').write_bytes(out)
                (case/f'cli-stderr-{n}.bin').write_bytes(err)
                cli.append({'pid':p.pid,'returncode':p.returncode,'capture':'raw pipe bytes',
                   'accepted':p.returncode==0 and b'G6_REPLAY_ACCEPTED' in out,
                   'semantic_rejection':p.returncode==3 and b'A24_DOUBLE_REJECTED' in err})
        required = http[0]['accepted'] if wanted else http[0]['semantic_rejection'] and http[1]['accepted']
        if cli:
            required = required and (cli[0]['accepted'] if wanted else cli[0]['semantic_rejection'] and cli[1]['accepted'])
        row={'case':name,'expected_operation':event, 'wanted_acceptance':wanted, 'http':http, 'cli':cli,
             'healthy_after_rejection_same_position': None if wanted else http[1]['accepted'] and (not cli or cli[1]['accepted']),
             'requirement_satisfied':bool(required)}
        write(case/'result.json',row);rows.append(row)
    result={'cases':rows,'satisfied':sum(r['requirement_satisfied'] for r in rows),'total':len(rows),
            'legacy_flag':False,'strict_independent_operation':True,
            'method':'actual HTTP/Fake-CLI, original immutable tape event + previously successful output journal; no game replay/mutation'}
    write(output_dir/'result.json',result)
    if require_closed:
        assert all(row['requirement_satisfied'] for row in rows), json.dumps([(r['case'],r['requirement_satisfied']) for r in rows])
    return result
