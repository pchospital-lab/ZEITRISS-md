#!/usr/bin/env python3
"""
mmo_sim/adapters/base.py — Protokolle fuer Persona-/GM-Adapter (03_PROVIDER,
PLAN.md §2/§3 Antwort 1+5).

`ParticipantDriver` liefert eine validierte Entscheidung — Human-Driver
(Terminal/geskriptet) und Persona-Driver (API/CLI/Fake) implementieren
DASSELBE Protokoll, damit `core/controller.py` beide gleich behandeln kann.

`GMTransport` ist der Vertrag, den `sl_stub.SLStub` UND
`agent_mp/sl_client.SLSession` bereits erfuellen: `{content, usage, sources,
latency_s, chat_id}` (Contract-Naht, s. P1 `sl_stub.py`-Docstring). Ein
Adapter, der diesen Vertrag nicht exakt erfuellt, ist nicht austauschbar.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Protocol


class ProviderAuthError(RuntimeError):
    """Fehlende Anmeldung / falscher API-Key — MUSS vor einem teuren Request
    sichtbar werden (03 §4, A02/A15). Kein stiller Fallback."""


class ProviderQuotaError(RuntimeError):
    """Abo-Limit/Kontingent-Ende erreicht — Pause statt Fallback (03 §4)."""


class ProviderUnavailableError(RuntimeError):
    """CLI/Client nicht vorhanden oder Isolation nicht herstellbar — Adapter
    liefert `unavailable`, kein unsicherer Betrieb (03 §5)."""


@dataclass
class ParticipantDecision:
    """Validierte Entscheidung eines Teilnehmers (Mensch ODER Persona) —
    identischer Vertrag fuer beide (PLAN.md §3 Antwort 1).

    A4/D2 (WEGKARTE §8, Plan-Critic A4, Test 03): `decision` ist ein
    STRUKTURELLES Feld -- "accept" | "reject" | "invalid" | `None` (nicht
    anwendbar, z.B. normale Spielzug-Entscheidungen statt einer Ja/Nein-
    Einladungsfrage). Der ADAPTER setzt es selbst (s. `interpret_yes_no_
    decision` unten); die Runtime/UI durchsucht NICHT selbststaendig den
    Fliesstext nach Zustimmung -- eine erfolgreich zugestellte Antwort
    (kein Exception, HTTP 200) ist NIE automatisch eine Zusage."""

    text: str
    save_payload: dict | None = None
    origin_source: str = ""  # z.B. "human:terminal" / "persona_api:gpt-x" / "fake:scripted"
    meta: dict = field(default_factory=dict)
    decision: str | None = None


_ACCEPT_LEAD_WORDS = ("ja", "jep", "jo", "yes", "yep", "j")
_REJECT_LEAD_WORDS = ("nein", "ne", "no", "nope", "n")


def interpret_yes_no_decision(text: str) -> str:
    """A4/D2 (WEGKARTE §7/§8, R02/R03-Restintegrationsfix, Test 02/03):
    wertet die Antwort auf eine ausdruecklich als Ja-/Nein-Frage gestellte
    Einladung aus. KEINE Liste deutscher Negationswoerter (kein Scan nach
    'nicht'/'kein'/'niemals'/... irgendwo im Fliesstext) -- geprueft wird
    ausschliesslich das FUEHRENDE Wort der Antwort gegen zwei kleine,
    geschlossene Woertermengen (ein Ja- und ein Nein-Protokollwort samt
    engster Kurzformen).

    R02-Restintegrationsfix (REVIEW-P2R.md R-B, bindend): der DEFAULT ist
    NICHT mehr 'accept'. 'Ein Text, der das vereinbarte positive
    Entscheidungsformat nicht erfuellt, darf nicht standardmaessig accept
    werden' -- eine Antwort, die weder mit einem Ja- noch mit einem
    Nein-Protokollwort beginnt (z.B. eine Ablehnung in freier Formulierung
    wie 'Ich lehne ab...', oder ein reiner Platzhaltertext), ist 'invalid'
    (keine Aufnahme, kein automatischer Beitritt bei Unklarheit) -- SYMMETRISCH
    zur bereits vorhandenen leeren-Antwort-Behandlung. Eine leere Antwort
    bleibt ebenfalls 'invalid'.

    Bewusste Grenze: eine reale Persona/ein Mensch, die/der trotz expliziter
    Protokollanweisung ('Antworte mit einem klaren Ja oder Nein am Anfang
    deiner Antwort') nicht mit diesem Wort beginnt, wird NICHT aufgenommen
    (invalid statt Rateversuch) -- das ist die im Auftrag geforderte
    Umkehr des Defaults, kein Bug. Fuer einen echten Live-Piloten bleibt ein
    vom Modell erzwungenes strukturiertes Antwortformat (z.B. JSON
    {'decision': 'accept'|'reject'}) ein moeglicher spaeterer Ausbau, kein
    Fix in diesem Restintegrations-Scope (WEGKARTE §5 'kein
    Store-/Protokollneubau').

    W1-Fix (F..., PLAN-CRITIC.md, Test 02 review_p2w_boundaries.py):
    'vollstaendig positiv/negativ' statt nur 'beginnt mit' -- eine Antwort
    wie 'Ja, ich habe die Einladung gelesen. Ich lehne dieses Angebot ab
    und bleibe draussen.' darf trotz fuehrendem Ja-Wort NICHT als Zusage
    gelten (das fuehrende Wort beantwortet hier nur "gelesen?", nicht die
    eigentliche Frage). Geprueft wird das STRUKTURELL, ohne jede
    Negationswortliste: eine Antwort bleibt nur dann vollstaendig positiv/
    negativ, wenn sie aus GENAU EINEM Satz besteht (hoechstens EIN
    Satzendezeichen '.'/'!'/'?', und dieses steht -- falls vorhanden -- am
    Ende, nicht mittendrin). Ein zweiter, eigenstaendiger Satz NACH dem
    ersten (weiteres Satzendezeichen mit folgendem Text, oder mehr als ein
    Satzendezeichen insgesamt) macht die Antwort unklar -- 'invalid', auch
    wenn das fuehrende Wort ein Protokollwort war. Einfache Antworten ohne
    oder mit nur einem abschliessenden Satzendezeichen ('Ja', 'Ja.',
    'Ja, ich nehme an.', 'Nein, ich lehne ab.') bleiben unveraendert
    accept/reject -- nur echte Mehrsatz-Antworten wechseln zu invalid."""
    stripped = (text or "").strip()
    if not stripped:
        return "invalid"
    first_word = stripped.split(None, 1)[0].strip(".,!?:;").lower()
    if first_word in _ACCEPT_LEAD_WORDS:
        decision = "accept"
    elif first_word in _REJECT_LEAD_WORDS:
        decision = "reject"
    else:
        return "invalid"
    # W1-B1-Fix (Main-Nacharbeit, End-Critic BLOCKER 1): Zeilenumbruch
    # zaehlt ebenfalls als Satzgrenze -- eine Antwort wie
    # 'Ja\nIch lehne ab und bleibe draussen' (zweiter, widersprechender
    # Satz nur per Newline abgetrennt) umging zuvor die Mehrsatz-Pruefung
    # und wurde faelschlich accept. Fuehrende/abschliessende Umbrueche
    # sind durch das obige .strip() entfernt und bleiben unschaedlich.
    sentence_enders = [i for i, ch in enumerate(stripped) if ch in ".!?\n\r"]
    if sentence_enders:
        trailing_after_last = stripped[sentence_enders[-1] + 1:].strip()
        if trailing_after_last or len(sentence_enders) > 1:
            return "invalid"
    return decision


_DECISION_CONTRACT_VALUES = ("accept", "reject")
_DECISION_CONTRACT_JSON_KEYS = frozenset({"offer_id", "participant_id", "decision", "explanation"})
_DECISION_CONTRACT_REQUIRED_KEYS = frozenset({"offer_id", "participant_id", "decision"})
_DECISION_LINE_RE = re.compile(
    r"^\s*ENTSCHEIDUNG\s+offer_id=(?P<offer_id>\S+)\s+participant_id=(?P<participant_id>\S+)\s+"
    r"decision=(?P<decision>accept|reject)(?:\s+explanation=(?P<explanation>.*))?\s*$",
    re.IGNORECASE,
)


def decision_contract_instruction(offer_id: str, participant_id: str) -> str:
    """I1 (WEGKARTE §"eindeutiges Entscheidungsereignis", MAIN-ENTSCHEIDUNG
    I1-Kontrollform): Protokolltext, der einer Persona VOR ihrer Entscheidung
    mitteilt, mit welcher vollstaendig validierbaren Kontrollform sie
    antworten muss -- IDs erreichen so tatsaechlich den Modellprompt (nicht
    nur nachtraeglich das Audit-Log, s. `mmo_sim/ui/tui.py` invite_ctx)."""
    offer_json = json.dumps(offer_id)
    participant_json = json.dumps(participant_id)
    return (
        "Antworte AUSSCHLIESSLICH mit einer der beiden folgenden Formen (kein "
        "Fliesstext, keine weitere Zeile davor/danach ausserhalb der Felder):\n"
        f'  1) JSON-Objekt: {{"offer_id": {offer_json}, "participant_id": {participant_json}, '
        '"decision": "accept"|"reject", "explanation": "<optional>"}\n'
        f"  2) Textzeile: ENTSCHEIDUNG offer_id={offer_id} participant_id={participant_id} "
        "decision=accept|reject [explanation=<optionaler Text ohne Zeilenumbruch>]\n"
        "offer_id und participant_id MUESSEN exakt den oben genannten Werten entsprechen -- "
        "jede andere/fehlende/zusaetzliche Form ist ungueltig und wird NICHT aufgenommen."
    )


def interpret_decision_contract(
    text: str, *, offer_id: str, participant_id: str,
) -> tuple[str, str | None]:
    """I1 (WEGKARTE, MAIN-ENTSCHEIDUNG I1-Kontrollform, PLAN-CRITIC F1/F2):
    vollstaendig validierbare Kontrollform fuer eine Einladungs-/
    Leaderentscheidung -- JSON ODER eine gleichwertige enge Textgrammatik,
    BEIDE mit geprueftem Bezug (offer_id/participant_id MUESSEN exakt zum
    tatsaechlichen Angebot/Entscheider passen, VOR jeder Aufnahme geprueft).
    Falscher Bezug, widersprechende/unbekannte Zusatzfelder, unvollstaendige
    oder sonstige Form -> ('invalid', None) -- keine Aufnahme.

    Ersetzt die alte 'fuehrendes Wort + Satzanzahl'-Heuristik fuer
    Einladungs-/Leaderentscheidungen: Case 02 ('Ja, ich habe die Einladung
    gelesen und lehne sie ab.') ist strukturell IMMER invalid, unabhaengig
    vom Wortlaut -- kein Rateversuch an natuerlicher Sprache mehr fuer genau
    diese Entscheidungsklasse. Normale Spiel-/Abspracheturns durchlaufen
    diese Funktion NICHT (WEGKARTE: 'Normale Spielturns bleiben frei')."""
    stripped = (text or "").strip()
    if not stripped:
        return "invalid", None
    decision: str | None = None
    got_offer: object = None
    got_participant: object = None
    explanation: object = None
    try:
        # PLAN-CRITIC F10/Auflage 7 (bindend): `json.loads` kollabiert
        # doppelte Objekt-Keys BEIM PARSEN SELBST auf den letzten Wert --
        # eine Pruefung auf dem fertigen `dict` (z.B. Feldanzahl) kann ein
        # Duplikat wie {"decision":"reject","decision":"accept"} STRUKTURELL
        # nicht mehr erkennen (Python hat den ersten Wert bereits verworfen).
        # `object_pairs_hook` sieht die ROHE (key, value)-Paarliste VOR dem
        # Kollabieren -- ein doppelter Key in dieser Liste macht das Objekt
        # sofort 'invalid', unabhaengig davon, welcher Wert "gewinnen" wuerde.
        def _reject_duplicate_keys(pairs):
            seen = set()
            for key, _value in pairs:
                if key in seen:
                    raise ValueError(f"doppelter JSON-Key: {key!r}")
                seen.add(key)
            return dict(pairs)

        parsed_json = json.loads(stripped, object_pairs_hook=_reject_duplicate_keys)
    except (json.JSONDecodeError, ValueError):
        parsed_json = None
    if isinstance(parsed_json, dict):
        if not set(parsed_json.keys()) <= _DECISION_CONTRACT_JSON_KEYS:
            return "invalid", None  # widerspruechliche/unbekannte Zusatzfelder
        if not _DECISION_CONTRACT_REQUIRED_KEYS <= set(parsed_json.keys()):
            return "invalid", None  # unvollstaendig
        got_offer = parsed_json.get("offer_id")
        got_participant = parsed_json.get("participant_id")
        raw_decision = parsed_json.get("decision")
        explanation = parsed_json.get("explanation")
        if not isinstance(raw_decision, str) or raw_decision.lower() not in _DECISION_CONTRACT_VALUES:
            return "invalid", None
        decision = raw_decision.lower()
    else:
        m = _DECISION_LINE_RE.match(stripped)
        if not m:
            return "invalid", None
        got_offer = m.group("offer_id")
        got_participant = m.group("participant_id")
        decision = m.group("decision").lower()
        explanation = m.group("explanation")
    if str(got_offer) != str(offer_id) or str(got_participant) != str(participant_id):
        return "invalid", None  # falscher Bezug -- kein Auto-Accept durch Namensgleichheit
    return decision, explanation


def human_menu_decision(raw_answer: str) -> tuple[str, str | None]:
    """I1 (MAIN-ENTSCHEIDUNG: 'Human-Ja/Nein im eindeutig bezeichneten Menue
    wird technisch in denselben Ereignisvertrag umgesetzt -- kein JSON fuer
    Menschen'). Die UI-Frage selbst stellt die Bindung an offer_id/
    participant_id her (genau EINE offene Frage an genau EINEN Entscheider);
    der Mensch tippt nur ein einfaches Ja/Nein. Liefert dieselbe (decision,
    explanation)-Form wie `interpret_decision_contract`, damit beide Pfade
    strukturell denselben Vertrag bedienen."""
    return interpret_yes_no_decision(raw_answer), None


class ParticipantDriver(Protocol):
    """Human- und Persona-Driver implementieren dasselbe Protokoll."""

    def decide(self, context: dict) -> ParticipantDecision: ...


class GMTransport(Protocol):
    """Identischer Vertrag zu `sl_stub.SLStub.turn()` / `agent_mp.sl_client.
    SLSession.turn()`: {content, usage, sources, latency_s, chat_id}."""

    def turn(self, turn_idx: int, user_text: str) -> dict: ...


def render_public_wire_text(context: dict) -> str:
    """F1 (K7): serialisiert die VOLLE erlaubte oeffentliche Sicht
    (`context["table_view"]`, s. `core/store.persona_view`) zusammen mit dem
    eigentlichen `user`-Prompt in den Text, der tatsaechlich an den Persona-
    Empfaenger (HTTP-Body/CLI-STDIN) geht. Ohne `table_view` (z.B. reine
    Preflight-/Isolationstests) bleibt das Verhalten unveraendert -- nur der
    rohe `user`-Text. Fremde private States/Operatorwissen gehen NIE in
    `table_view` ein (das filtert bereits `core/store.persona_view`) -- diese
    Funktion serialisiert nur, was der Aufrufer bereits als erlaubt
    markiert hat.

    R10-Restintegrationsfix (WEGKARTE §7, REVIEW-P2R.md R-D, Test 10):
    `context["own_context"]` (der eigene aktuelle Persona-/Chrononaut-State,
    von `core/runtime.py:_collect_reflections` gesetzt, WEIL `system` dort
    bewusst der generische Reflexions-Sentinel bleibt) wird -- falls vom
    Aufrufer gesetzt -- ZUSAETZLICH in denselben Wire-Text eingebettet, der
    tatsaechlich an den Empfaenger (HTTP-Body/CLI-STDIN) geht. Normale
    Spiel-/Absprache-Turns setzen `own_context` nicht (ihr eigener State
    steht bereits im `system`-Feld) -- fuer sie aendert sich nichts."""
    user = context.get("user", "")
    own_context = context.get("own_context")
    table_view = context.get("table_view")
    parts = [user]
    if own_context:
        parts.append(f"\n\n[EIGENER_KONTEXT]\n{own_context}")
    if table_view:
        parts.append(f"\n\n[OEFFENTLICHE_TISCHSICHT]\n{json.dumps(table_view, ensure_ascii=False, sort_keys=True)}")
    return "".join(parts)
