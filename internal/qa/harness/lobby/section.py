#!/usr/bin/env python3
"""
lobby/section.py — duenne Abschnitts-Ausfuehrung ueber dem SL-Stub.

Ablauf (spiegelt COORDINATION-MODEL-FROZEN Punkte 2/3/7, minimal):
  1. Leader-Anker zuerst: der Leader postet seinen eigenen Save als ersten Turn.
  2. Gaeste einzeln: fuer jedes weitere Mitglied EIN eigener Turn (eigener
     Save-JSON), aber IMMER ueber `rooms.submit_to_sl` mit dem Leader als Akteur
     (nur der Leader schreibt — COORDINATION-MODEL-FROZEN Punkt 3, nicht
     verhandelbar in diesem Slice).
  3. R2/Auflage 2: der Debrief-Turn muss den exakten, maschinenlesbaren
     `COMPLETION_MARKER`-Token in der SL-Antwort enthalten — sonst gilt der
     Abschnitt NICHT als abgeschlossen (kein Heuristik-Check ueber Save-Wert/
     -Aenderung, s. u.).
  4. Save-Ernte: die SL-Antwort wird via `saves.extract_all_saves`/
     `single_character_count`/`block_char_id` in N getrennte v7-Bloecke zerlegt
     und ueber `chrononaut_id` den Mitgliedern zugeordnet.
  5. `rooms.complete_section(...)` wertet die Ernte aus (Idempotenz, s. rooms.py).
  6. Bei echtem Erstabschluss: Rueckkehr in die Lobby.

R7/Auflage 6 — Herkunftsbelegte, simulierte Leader-Nachrichten:
  Die Leader-/Gast-/Debrief-Texte, die der Leader an die SL schickt, sind KEINE
  zur Laufzeit vom Controller formulierten Persona-Entscheidungen. Sie kommen aus
  der vorab abgelegten Fixture `fixtures/leader_messages.json` (generischer,
  fester Text pro Turn-Art) und werden als `SimulatedLeaderMessage` mit
  Herkunftsbeleg (welche Persona, welche Fixture/Schluessel) an
  `rooms.submit_to_sl` uebergeben. Der tatsaechliche, laufabhaengige Save-Inhalt
  (der nicht vorab in einer statischen Fixture stehen kann, weil er von den
  echten `initial_saves` des jeweiligen Testlaufs abhaengt) wird NICHT in den
  Nachrichtentext hineingerechnet, sondern als GETRENNTE strukturierte
  `save_payload` neben der Nachricht transportiert und von `rooms.submit_to_sl`
  im `sl_log`-Eintrag mitgespeichert. So bleibt sichtbar, was "persona-
  entschiedener (simulierter) Inhalt" ist und was "angehaengtes Save-Datum" ist,
  statt beides in einem einzigen f-String zu verschmelzen.

AUSDRUECKLICH NICHT enthalten: Wuerfeln, Aufstieg/Level-Up, Belohnung,
Missionswahl (reine Datei-/Transport-Logik, kein zweites Regelwerk). Echte
Reflexions-Turns bleiben eine ausgewiesene spaetere Grenze.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

_HARNESS_DIR = Path(__file__).resolve().parents[1]
_AGENT_MP_DIR = _HARNESS_DIR / "agent_mp"
_LOBBY_DIR = Path(__file__).resolve().parent
for _p in (str(_HARNESS_DIR), str(_AGENT_MP_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import saves as save_lib  # noqa: E402

import rooms

# R2/Auflage 2: exakter, maschinenlesbarer Abschluss-Marker-Token. Substring-
# Vergleich, KEINE Heuristik ueber Save-Wert-Praesenz/-Aenderung — der
# Abnahme-Test "Setup-Echo" liefert sonst taeuschend gueltig aussehende v7-
# Bloecke ohne echten neuen Abschluss und muesste faelschlich als Erfolg
# gewertet werden. Alle `fixtures/sl_canned/*.json`, die durch `run_section`
# laufen und Erfolg ODER eine ueber den Marker hinausgehende Ablehnung (fehlender/
# falscher Save) erreichen sollen, tragen diesen Token im Debrief-Turn.
COMPLETION_MARKER = "SECTION-ABSCHLUSS-BESTAETIGT"

_LEADER_MESSAGES_PATH = _LOBBY_DIR / "fixtures" / "leader_messages.json"

# P3/K3-Nachzug: zeilenbasierte Fence-Zustandsmaschine (ersetzt den
# frueheren nicht-greedy ```.*?```-Regex, der ueber Zeilengrenzen hinweg
# paarte und damit sowohl Falsch-Akzeptanzen — offener Block bis Textende,
# ```~~~```-Fences, verschachtelte Bloecke mit kuerzerem innerem Delimiter —
# als auch eine Falsch-Ablehnung — Inline-Backticks in einer Prosazeile vor
# einem echten Top-Level-Marker — erzeugen konnte. Die Marker-Suche
# (`_completion_marker_matches`) laeuft ausschliesslich ueber die Zeilenliste,
# die `_top_level_lines` liefert (nie ueber einen wieder zusammengefuegten
# String) — das Entfernen/Zusammenfuegen von Beispielinhalt kann so kein
# neues Ereignis erzeugen.
#
# Kontrollform (CommonMark-nah, bewusst minimal):
#   - Delimiterzeile = Zeile, die nach optional <=3 fuehrenden Leerzeichen mit
#     einem Lauf von >=3 GLEICHEN Fence-Zeichen (` oder ~) BEGINNT. Text vor
#     dem Lauf (z. B. "Prosa mit ```inline") macht die Zeile KEINE
#     Delimiterzeile — sie bleibt Top-Level.
#   - Oeffnen (ausserhalb eines Blocks): die erste Delimiterzeile oeffnet
#     einen Block; Zeichenart `c` und Lauflaenge `n` werden gemerkt. Die
#     Oeffnungszeile selbst ist nicht Top-Level.
#   - Schliessen (innerhalb eines Blocks): nur eine Delimiterzeile mit
#     GLEICHER Zeichenart `c`, Laenge >= `n` UND leerem Info-String (nur
#     Whitespace nach dem Lauf) schliesst. Ein kuerzerer, andersartiger oder
#     mit Info-String versehener Delimiter schliesst NICHT — ein laengerer
#     aeusserer Block bleibt offen, selbst wenn ein kuerzerer innerer
#     Delimiter vorbeizieht.
#   - Bleibt ein Block bis Textende offen, werden alle seine Zeilen
#     verworfen — kein Marker wird freigelegt (kontrollierte Ablehnung ohne
#     Abschluss).
#   - In-Block-Zeilen werden uebersprungen (nicht geloescht/zusammengefuegt).
#
# `save_lib.extract_all_saves` (Save-Ernte) laeuft UNVERAENDERT auf dem
# Originaltext, NICHT auf den Top-Level-Zeilen — von dieser Erweiterung
# strukturell unberuehrt (s. `run_section` [4] unten).
_FENCE_DELIMITER_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def _load_leader_messages() -> dict:
    return json.loads(_LEADER_MESSAGES_PATH.read_text(encoding="utf-8"))


def _with_save_block(text: str, save: dict) -> str:
    """NB-A/R7 (Test 01): haengt den v7-Save als eigenen ```json```-Block an
    den WIRE-Text an, der tatsaechlich an `sl_stub.turn()` geht — die Abnahme
    prueft `extract_all_saves` auf dem protokollierten `user_text`
    (`SLStub.calls[i]['user_text']`), nicht nur auf dem getrennt gefuehrten
    `sl_log`-Eintrag. Das ist reine technische Serialisierung der bereits
    freigegebenen Nachricht + Save — KEINE neu erfundene Persona-Entscheidung;
    Herkunft/Entscheidung bleiben ueber `origin_persona_key`/`origin_source`/
    `save_payload` im `sl_log` weiterhin GETRENNT nachvollziehbar
    (`rooms.submit_to_sl` speichert beides zusaetzlich)."""
    return text + "\n```json\n" + json.dumps(save, ensure_ascii=False) + "\n```"


def _fence_delimiter(line: str) -> tuple[str, int, str] | None:
    """Gemeinsame Hilfsfunktion fuer Oeffnen UND Schliessen (Plan-Critic-
    Auflage A2) — die Delimiter-Regel lebt an genau dieser einen Stelle,
    statt in zwei auseinanderlaufenden Pfaden.

    Liefert `(char, length, info)`, wenn `line` eine Fence-Delimiterzeile ist
    (s. Kontrollform im Kommentar oberhalb von `_FENCE_DELIMITER_RE`), sonst
    `None`. `info` ist der Rest der Zeile nach dem Zeichenlauf (Info-String);
    beim Schliessen gilt ein NUR-Whitespace-Info als "leer"."""
    m = _FENCE_DELIMITER_RE.match(line)
    if not m:
        return None
    run = m.group(1)
    return run[0], len(run), m.group(2)


def _top_level_lines(text: str) -> list[str]:
    """NB-B/Auflage 5 + P3/K3-Nachzug: liefert genau die Zeilen von `text`,
    die NICHT innerhalb eines Fence-Blocks liegen — ein Marker-Token, der
    zufaellig als STRING-WERT innerhalb eines importierten/geernteten Saves
    auftaucht (Test 02), oder als Protokollbeispiel innerhalb eines
    NICHT-json-Fence zitiert wird (K3), darf nicht als echtes
    Abschluss-Ereignis zaehlen.

    Nutzt `_fence_delimiter` fuer BEIDE Entscheidungen (Oeffnen und
    Schliessen); die Zeilenliste wird geliefert statt eines wieder
    zusammengefuegten Strings, damit spaetere Konsumenten (s.
    `_completion_marker_matches`) niemals ueber eine Zeilengrenze hinweg
    matchen koennen."""
    top_level: list[str] = []
    in_block = False
    fence_char = ""
    fence_len = 0
    for line in text.splitlines():
        delim = _fence_delimiter(line)
        if not in_block:
            if delim is not None:
                fence_char, fence_len, _info = delim
                in_block = True
                continue
            top_level.append(line)
            continue
        if delim is not None:
            char, length, info = delim
            if char == fence_char and length >= fence_len and info.strip() == "":
                in_block = False
        # In-Block-Zeilen (inkl. eines nicht schliessenden Delimiters) werden
        # uebersprungen, nicht geloescht/zusammengefuegt.
    return top_level


_QUALIFIER_RE = re.compile(r"^(table_id|section_id)=(.*)$")


def _completion_marker_matches(text: str, table_id: str, section_id: str) -> bool:
    """K3/NB-B: vollstaendige POSITIVE Ereignisgrammatik, kein Praefix-/
    Substring-Treffer irgendwo im Text.

    Ueber `_top_level_lines(text)` (Fence-Zustandsmaschine, s. o.) wird JEDE
    Zeile AUSSERHALB eines Fence-Blocks fuer sich tokenisiert: `s =
    line.strip()`, dann per Whitespace gesplittet. `tokens[0]` muss EXAKT
    `COMPLETION_MARKER` sein — ein an das Markertoken angehaengtes Suffix
    OHNE trennenden Whitespace (z. B. `MARKER=false` als EIN einziges Token)
    ist damit ebenso ausgeschlossen wie ein vorangestelltes Praefix-Token
    ("NICHT "/"> " + Marker, je eigenes Token vor dem Marker). JEDES weitere
    Token muss ein gueltiger `table_id=`/`section_id=`-Qualifier mit
    PASSENDEM Wert sein — ein unbekanntes Token (falscher Schluessel,
    fehlendes '=' oder freier Text) macht die gesamte Zeile ungueltig, auch
    wenn andere Qualifier auf derselben Zeile bereits passten. Ein BLANKER
    Marker (`tokens == [COMPLETION_MARKER]`, keine weiteren Token) gilt fuer
    die AKTUELLE Session (der Stub IST die SL genau dieses Tisches) — so
    verwenden ihn alle bestehenden Erfolgs-Fixtures unter
    `fixtures/sl_canned/` (eigenstaendige Zeile ohne Qualifier).

    ALLE Top-Level-Zeilen werden geprueft (nicht nur die erste): eine
    FRUEHERE ungueltige Zeile darf eine SPAETERE gueltige nicht verdecken
    (Plan-Critic-Auflage 5)."""
    for line in _top_level_lines(text):
        tokens = line.strip().split()
        if not tokens or tokens[0] != COMPLETION_MARKER:
            continue
        valid = True
        for tok in tokens[1:]:
            m = _QUALIFIER_RE.match(tok)
            if not m:
                valid = False
                break
            key, value = m.group(1), m.group(2)
            expected = table_id if key == "table_id" else section_id
            if value != expected:
                valid = False
                break
        if valid:
            return True
    return False


@dataclass
class SimulatedLeaderMessage:
    """R7/Auflage 6: klar als simuliert markierter Fixture-Input mit Herkunftsbeleg.

    `text` ist vorab in `fixtures/leader_messages.json` formulierter, generischer
    Entscheidungstext (KEIN zur Laufzeit vom Controller erfundener Persona-O-Ton).
    `persona_key`/`source` sind der Herkunftsbeleg (wessen Entscheidung dies
    simuliert, aus welcher Fixture/welchem Schluessel). `save_payload` traegt den
    tatsaechlichen, laufabhaengigen Save-Inhalt GETRENNT vom Text.
    """

    persona_key: str
    source: str
    text: str
    save_payload: dict | None = None


@dataclass
class SectionResult:
    completion: rooms.CompletionResult
    harvested: dict = field(default_factory=dict)
    debrief_text: str = ""


def run_section(
    lobby: rooms.Lobby, table: rooms.Table, sl_stub, section_id: str,
    initial_saves: dict[str, dict], states_dir: str | Path,
) -> SectionResult:
    turn_idx = 0
    msgs = _load_leader_messages()
    fixture_rel = str(_LEADER_MESSAGES_PATH.relative_to(_LOBBY_DIR))

    # 1. Leader-Anker zuerst — simulierte Fixture-Nachricht + getrennte Save-Payload.
    # NB-A/R7 (Test 01): der tatsaechliche WIRE-Text (an submit_to_sl->sl_stub.turn)
    # traegt den v7-Save als eigenen ```json```-Block, damit der Empfaenger ihn
    # wirklich erhaelt; Herkunft/Entscheidung bleiben ZUSAETZLICH getrennt ueber
    # origin_persona_key/origin_source/save_payload im sl_log nachvollziehbar.
    anchor = SimulatedLeaderMessage(
        persona_key=table.leader, source=f"{fixture_rel}#anchor_text",
        text=msgs["anchor_text"], save_payload=initial_saves[table.leader],
    )
    rooms.submit_to_sl(
        table, table.leader, sl_stub, turn_idx,
        _with_save_block(anchor.text, anchor.save_payload),
        origin_persona_key=anchor.persona_key, origin_source=anchor.source,
        save_payload=anchor.save_payload,
    )
    turn_idx += 1

    # 2. Gaeste einzeln (leader-relayed, ein Turn je Gast)
    for pk in [m for m in table.members if m != table.leader]:
        guest = SimulatedLeaderMessage(
            persona_key=pk, source=f"{fixture_rel}#guest_text",
            text=msgs["guest_text"], save_payload=initial_saves[pk],
        )
        rooms.submit_to_sl(
            table, table.leader, sl_stub, turn_idx,
            _with_save_block(guest.text, guest.save_payload),
            origin_persona_key=guest.persona_key, origin_source=guest.source,
            save_payload=guest.save_payload,
        )
        turn_idx += 1

    # 3. Save-Ernte: expliziter Debrief-/!save-Turn
    debrief_msg = SimulatedLeaderMessage(
        persona_key=table.leader, source=f"{fixture_rel}#debrief_text",
        text=msgs["debrief_text"],
    )
    debrief = rooms.submit_to_sl(
        table, table.leader, sl_stub, turn_idx, debrief_msg.text,
        origin_persona_key=debrief_msg.persona_key, origin_source=debrief_msg.source,
    )
    debrief_text = debrief["content"]

    # R2/NB-B (Auflage 2/5): ohne einen DIESEM Tisch+Abschnitt zugeordneten
    # Marker (ausserhalb jedes Fence-Blocks der Zustandsmaschine,
    # Qualifier-Abgleich, s. `_completion_marker_matches`/`_top_level_lines`)
    # KEIN Abschluss — dieser Check lebt bewusst hier (run_section), NICHT im
    # complete_section-Core. `complete_section` bleibt dadurch eine interne,
    # nachgelagerte Persistenz-/Finalisierungsstufe HINTER dem hier bereits
    # validierten Ereignis (Test 09/complete_section-Direktaufrufe der
    # Gegenproben muessen weiterhin ohne Marker-Konzept funktionieren, s.
    # `rooms.complete_section`-Docstring).
    if not _completion_marker_matches(debrief_text, table.table_id, section_id):
        completion = rooms.CompletionResult(
            success=False, already_completed=False, written=False,
            members_completed=[], missing=[],
            reason="Kein maschinenlesbarer Abschluss-Marker im Debrief-Turn — kein Abschnittsabschluss.",
        )
        return SectionResult(completion=completion, harvested={}, debrief_text=debrief_text)

    cid_to_pk = table.chrononaut_id_to_persona()
    harvested: dict[str, dict] = {}
    for blk in save_lib.extract_all_saves(debrief_text):
        cid = save_lib.block_char_id(blk)
        pk = cid_to_pk.get(cid) if cid else None
        if pk is not None and save_lib.single_character_count(blk) == 1 and pk not in harvested:
            harvested[pk] = blk

    # 5. Completion-Idempotenz
    completion = rooms.complete_section(lobby, table, section_id, harvested, states_dir)

    # 6. Rueckkehr in Lobby nur bei echtem (Erst-)Abschluss
    if completion.success:
        rooms.return_to_lobby(lobby, table)

    return SectionResult(completion=completion, harvested=harvested, debrief_text=debrief_text)
