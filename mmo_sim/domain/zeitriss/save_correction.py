#!/usr/bin/env python3
"""
mmo_sim/domain/zeitriss/save_correction.py — ZEITRISS-Domänenwissen für die
request-gebundene SL-Korrekturschleife (R12-Savegate, W44/W48-Slice,
01_AUFTRAG_SAVEGATE.md §A/§B/§C/§E).

Reine Domänenschicht (SCOPE.json semantic_constraints.domain: "v7 schema
loading/errors/repair prompt semantics only"): baut die technische
Korrekturnachricht (Schema-/Validatorauszug + unveränderter Entwurf), wertet
einen Kandidatenblock gegen `save_validation` aus und erkennt unerwünschte
inhaltliche Drift (Identität/Name/Callsign/Level/Attribute/Inventar/Wallet/
Fortschritt dürfen bei reiner Schemareparatur NICHT still umgeschrieben
werden — 01_AUFTRAG_SAVEGATE.md §A). Die eigentliche request-/ledger-
gebundene Versandorchestrierung (Admission-Gate, `request_ledger`,
Zustands-/Zählerpersistenz) lebt in `core/save_correction.py` — diese Datei
schreibt NIE auf Platte und ruft NIE einen Transport auf (reine Funktionen,
kein I/O, kein Modellaufruf)."""
from __future__ import annotations

import json

from . import save_validation as save_validation_lib

#: POLICY.json `save_correction.max_additional_sl_requests_per_persona_per_operation`.
MAX_ADDITIONAL_REQUESTS = 3

#: Dedizierte Operationsidentitäten (01_AUFTRAG_SAVEGATE.md §D: "Eine
#: dedizierte Korrekturrolle/-Operationsidentität verhindert Verwechslung
#: mit gm_turn/persona_decision") -- NIE "gm_turn"/"persona_decision"/
#: "creation_dialog" wiederverwenden.
ROLE_CREATION = "save_correction_creation"
ROLE_GROUP = "save_correction_group"

#: Felder, unter denen ein numerischer Betrag OHNE Wertänderung in ein
#: Objekt gewrappt werden darf (01_AUFTRAG_SAVEGATE.md §A Beispiel: "Wallet
#: Zahl 100 -> Objekt mit balance 100 erlaubt; 100 -> 1000 nicht").
_AMOUNT_WRAP_KEYS = frozenset({"balance", "amount", "credits", "value"})


def evaluate(block: dict | None, expected_chrononaut_id: str) -> save_validation_lib.AcceptanceResult:
    """Dünner Zugriff auf den vollen `save_validation`-Annahmepunkt (BEIDE
    v7-Schemas + Bindung) -- im Gegensatz zu `policy.ZeitrissHarvestValidator.
    validate_block` (liefert nur `bool`) braucht die Korrekturschleife den
    VOLLEN `AcceptanceResult` (Fehlerpfade für die Korrekturnachricht, s.
    `build_correction_message`)."""
    return save_validation_lib.validate_save_block(block, expected_chrononaut_id)


#: G02/SC06 (W54-Fix): Re-Export des bereits vorhandenen Detectors, damit
#: `core/save_correction.py` ihn verdrahten kann, OHNE einen zusaetzlichen
#: Cross-Domain-Import (`save_validation`) in der Core-Schicht zu brauchen
#: (SCOPE.json semantic_constraints.core: ZEITRISS-Wissen bleibt in dieser
#: Datei gebuendelt). Dieselbe Funktion, die bereits oben (`evaluate`) UND
#: in `extract_checked_single` unten genutzt wird -- kein Zweitdetector.
find_duplicate_save_ids = save_validation_lib.find_duplicate_save_ids


def extract_checked_single(text: str, expected_chrononaut_id: str) -> tuple[dict | None, list]:
    """Dünner Zugriff auf `save_validation.extract_checked_single` (s.
    dort) -- strikter, mehrdeutigkeitssicherer Extraktionspfad fuer GENAU
    EINE erwartete Figur, fuer `core/save_correction.py`s Erstantwort-/
    Korrekturantwort-Annahmepunkte (G02/SC06)."""
    return save_validation_lib.extract_checked_single(text, expected_chrononaut_id)


def forced_conflict_acceptance(conflicts: list) -> save_validation_lib.AcceptanceResult:
    """G02/SC06 (W54-Fix): baut ein bewusst ABGELEHNTES `AcceptanceResult`
    AUS bereits erkannten Mehrdeutigkeitskonflikten
    (`find_duplicate_save_ids`/`extract_checked_single`) -- fuer den Fall,
    dass der Aufrufer VOR dem eigentlichen Annahmepunkt bereits weiss, dass
    KEINER der beteiligten rohen Kandidatenbloecke uebernommen werden darf
    (mehrere Rohbloecke derselben char_id/save_id mit ABWEICHENDEM Inhalt
    in derselben Antwort). `feedback_items` tragen dadurch die vorhandene,
    bereits SC17-sichere Konflikttextzeile (`BindingError.message`) an die
    SL weiter -- keine neue Fehlerklasse, keine Schemaaufweichung."""
    structure = save_validation_lib.StructureReport(valid=False, errors=[], total_error_count=0, truncated=False)
    return save_validation_lib.AcceptanceResult(accepted=False, structure=structure, binding_errors=list(conflicts))


#: G03/SC15/SC17 (W54-Fix): NUR diese festen, oeffentlichen Kategorien
#: duerfen eine Spieleranzeige/einen `print_fn`-/Terminal-Statusaufruf
#: erreichen -- NIE der rohe Text hinter einem Praefix (kann `str(exc)`
#: einer Fremdantwort/Transportausnahme sein, z.B. `core.save_correction.
#: send_correction_turn`s `transport_error:{exc}`). Der volle Rohgrund
#: bleibt NUR im geschuetzten Korrekturdatensatz (`core.save_correction.
#: mark_hold`s `last_reason`-Feld, `save_corrections/<repair_key>.json`)
#: erhalten -- fuer Diagnose, NICHT fuer die Spieleranzeige. Jede Kategorie
#: unten beschreibt einen tatsaechlich VERSUCHTEN oder kontrolliert
#: blockierten Vorgang -- ein ehrlicher Fehlversuch bleibt dadurch als
#: 'versucht/unklar/HOLD' erkennbar, NIE faelschlich als 'kein
#: Modellaufruf'.
_REASON_PREFIX_CATEGORY = (
    ("transport_error:", "transport_error_after_attempt"),
    ("unclear_sent_in_flight:", "unclear_prior_attempt_in_flight"),
    ("admission_blocked:", "budget_or_admission_hold"),
    ("altformat_unresolved_", "unresolved_prior_result_hold"),
)
_SAFE_REASONS = frozenset({
    "attempt_budget_exhausted", "unjustified_semantic_drift", "blocked",
    "adopted_without_durable_block", "adopted_durable_block_failed_revalidation",
})


def public_hold_reason(reason: str | None) -> str:
    """G03/SC15/SC17: liefert GENAU EINE klassifizierte, oeffentliche
    Kategorie fuer die Spieleranzeige -- NIE den rohen `reason`-Text selbst
    (s. Modulkonstante oben). Ein bereits bekannter, sicherer Grund
    (`_SAFE_REASONS`, enthaelt schon keine Fremddaten) wird unveraendert
    durchgereicht; ein bekanntes Praefix wird auf seine feste Kategorie
    abgebildet; alles andere (unbekannt/fehlend) wird NIE roh
    durchgelassen, sondern bekommt den neutralen Sammelbegriff
    'unclear_hold' bzw. 'unclear' (kein `reason` vorhanden)."""
    if not reason:
        return "unclear"
    if reason in _SAFE_REASONS:
        return reason
    for prefix, category in _REASON_PREFIX_CATEGORY:
        if reason.startswith(prefix):
            return category
    return "unclear_hold"


def creation_repair_key(participant_id: str, expected_chrononaut_id: str) -> str:
    """Stabiler, NEUSTART-fester Korrekturschlüssel für den menschlichen/
    Persona-Erschaffungsdialog -- bewusst NUR aus Identität+Operation
    abgeleitet, NIE aus einem Inhalts-/Kandidatenhash (01_AUFTRAG_SAVEGATE.md
    §C: "Zähler wird nicht aus neuem Kandidatenhash auf 0 gesetzt")."""
    return f"creation::{participant_id}::{expected_chrononaut_id}"


def group_repair_key(table_id: str, section_id: str, char_id: str) -> str:
    """Wie `creation_repair_key`, für den Gruppenabschluss -- EIN Schlüssel
    je (Tisch, Abschnitt, Figur), unabhängig vom jeweils zuletzt versuchten
    Kandidatenblock."""
    return f"group::{table_id}::{section_id}::{char_id}"


def _flatten(obj: object, prefix: str = "") -> list[tuple[str, object]]:
    """Zerlegt ein JSON-Objekt in (Pfad, Blattwert)-Paare, Pfadformat
    identisch zu `save_validation.SchemaError.path` ('/a/b/0')."""
    out: list[tuple[str, object]] = []
    if isinstance(obj, dict):
        for key in obj:
            out.extend(_flatten(obj[key], f"{prefix}/{key}"))
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            out.extend(_flatten(value, f"{prefix}/{idx}"))
    else:
        out.append((prefix or "/", obj))
    return out


def _leaves(obj: object) -> dict[str, object]:
    return dict(_flatten(obj))


def _is_allowed_amount_wrap(
    old_path: str, old_value: object, new_leaves: dict[str, object], consumed_new: set[str],
) -> bool:
    """Erlaubt GENAU den wertgleichen Zahl->Objekt-Wrap an EINEM einzigen
    neuen Unterpfad (z.B. '/economy/wallets/X' (100) -> '/economy/wallets/X/
    balance' (100)) -- jede Wertänderung (100 -> 1000) oder jeder zusätzliche
    Unterschlüssel bleibt eine abzulehnende Drift."""
    if not isinstance(old_value, (int, float)) or isinstance(old_value, bool):
        return False
    prefix = old_path + "/"
    candidates = [p for p in new_leaves if p.startswith(prefix)]
    if len(candidates) != 1:
        return False
    candidate = candidates[0]
    key = candidate[len(prefix):]
    if "/" in key or key not in _AMOUNT_WRAP_KEYS:
        return False
    new_value = new_leaves[candidate]
    if isinstance(new_value, bool) or new_value != old_value:
        return False
    consumed_new.add(candidate)
    return True


def _is_allowed_required_key_rename(
    old_path: str, old_value: object, old_leaves: dict[str, object],
    new_leaves: dict[str, object], consumed_new: set[str], error_paths: set[str],
) -> bool:
    """F1/F2 (01_AUFTRAG.md §A "amount:100 -> balance:100"): erlaubt GENAU
    den engen wertgleichen GESCHWISTER-Key-Rename innerhalb EINES
    Elternobjekts, das laut `error_paths` (required/additionalProperties)
    schema-ungueltig war -- der alte Blattschluessel verschwindet, ein NEUER
    schema-naher Blattschluessel (`_AMOUNT_WRAP_KEYS`) erscheint am selben
    Elternpfad mit byte-identischem Wert. Anders als `_is_allowed_amount_wrap`
    (Zahl wird zu geschachteltem Objekt, alter Pfad bleibt Praefix des neuen)
    behandelt dies den Fall, dass beide Blattpfade GESCHWISTER desselben
    Elternknotens sind (alter Schluessel weg, neuer Schluessel da).

    KEIN Blanket "schema-gueltig -> annehmen": beide Schluesselnamen (alt
    UND neu) muessen aus der festen, engen `_AMOUNT_WRAP_KEYS`-Menge stammen
    (verhindert Namens-/Fortschritts-/Alias-Umbenennungen), der Elternpfad
    muss ein TATSAECHLICH gemeldeter Fehlerpfad sein, der Wert muss
    byte-identisch bleiben (boolesche Scheinzahlen ausgeschlossen), und es
    darf GENAU EIN neuer, noch nicht vorhandener Geschwisterschluessel
    auftauchen (ein zusaetzlicher unbegruendeter Zusatzschluessel neben dem
    Rename laesst `len(candidates) != 1` scheitern -- bleibt Drift)."""
    if not isinstance(old_value, (int, float)) or isinstance(old_value, bool):
        return False
    sep = old_path.rfind("/")
    if sep <= 0:
        return False
    parent = old_path[:sep]
    old_key = old_path[sep + 1:]
    if old_key not in _AMOUNT_WRAP_KEYS:
        return False
    if parent not in error_paths:
        return False
    prefix = parent + "/"
    candidates = [
        p for p in new_leaves
        if p.startswith(prefix) and "/" not in p[len(prefix):] and p not in old_leaves
    ]
    if len(candidates) != 1:
        return False
    candidate = candidates[0]
    new_key = candidate[len(prefix):]
    if new_key not in _AMOUNT_WRAP_KEYS:
        return False
    new_value = new_leaves[candidate]
    if isinstance(new_value, bool) or new_value != old_value:
        return False
    consumed_new.add(candidate)
    return True


def detect_unjustified_drift(
    original: dict, corrected: dict, error_paths: set[str],
) -> list[tuple[str, object, object]]:
    """01_AUFTRAG_SAVEGATE.md §A: "Nur Fehlerpfade und nachweislich
    notwendige Strukturkorrekturen freigeben." Vergleicht `original` (der
    zuletzt abgelehnte Entwurf) gegen `corrected` (die neue SL-Antwort) Blatt
    für Blatt. Eine Abweichung an einem Pfad, der NICHT in `error_paths`
    (den tatsächlich gemeldeten `save_validation`-Fehlerpfaden) liegt, ist
    eine unerwünschte inhaltliche Änderung (Identität/Name/Callsign/Level/
    Attribute/Inventar/Wallet/Fortschritt) -- Aufrufer behandelt ein
    nicht-leeres Ergebnis als HOLD ("Unklarer Sinn -> HOLD statt raten"),
    NIEMALS als stille Übernahme.

    Ausnahme 1: ein reiner wertgleicher Zahl->Objekt-Wrap (s.
    `_is_allowed_amount_wrap`) ist auch AUSSERHALB von `error_paths` erlaubt
    (Beispiel 01_AUFTRAG_SAVEGATE.md §A), weil der tatsächliche Betrag
    nachweislich unverändert bleibt.

    Ausnahme 2 (F1/F2): ein enger wertgleicher Geschwister-Key-Rename (s.
    `_is_allowed_required_key_rename`), der einen laut `error_paths`
    schema-fehlerhaften Elternknoten gültig macht -- z.B.
    '/economy/wallets/X/amount' (100) -> '/economy/wallets/X/balance' (100).
    KEIN Blanket "schema-gültig ⇒ annehmen": Betragsänderung (100 -> 1000),
    Namens-/Fortschritts-/Alias-Umbenennung und unbegründete Zusatzschlüssel
    bleiben Drift (s. Docstring dort)."""
    if not isinstance(original, dict) or not isinstance(corrected, dict):
        return [] if original == corrected else [("/", original, corrected)]

    old_leaves = _leaves(original)
    new_leaves = _leaves(corrected)
    consumed_new: set[str] = set()
    drift: list[tuple[str, object, object]] = []

    for path, old_value in old_leaves.items():
        if path in new_leaves:
            continue  # im zweiten Durchgang behandelt (gleicher Pfad in beiden)
        if _is_allowed_amount_wrap(path, old_value, new_leaves, consumed_new):
            continue
        if _is_allowed_required_key_rename(path, old_value, old_leaves, new_leaves, consumed_new, error_paths):
            continue
        if path in error_paths:
            continue  # Struktur wurde an genau dieser gemeldeten Stelle korrigiert
        drift.append((path, old_value, "<entfernt/umstrukturiert>"))

    for path in sorted(set(old_leaves) | set(new_leaves)):
        if path in consumed_new:
            continue
        has_old = path in old_leaves
        has_new = path in new_leaves
        if has_old and not has_new:
            continue  # bereits im ersten Durchgang beurteilt
        if has_old and has_new:
            if old_leaves[path] == new_leaves[path]:
                continue
            if path in error_paths:
                continue
            drift.append((path, old_leaves[path], new_leaves[path]))
        else:
            if path in error_paths:
                continue
            drift.append((path, "<nicht vorhanden>", new_leaves[path]))
    return drift


_HEADER = (
    "TECHNISCHE SPEICHERKORREKTUR -- kein neuer Spielzug, keine neue Szene "
    "und keine Belohnung."
)


def build_correction_message(
    *,
    persona_key: str,
    char_id: str,
    operation_label: str,
    acceptance: save_validation_lib.AcceptanceResult | None,
    original_block: dict | None,
    attempt_no: int,
    max_attempts: int = MAX_ADDITIONAL_REQUESTS,
) -> str:
    """Baut die an die SL (dieselbe Session/denselben historischen
    Chatkontext) zu sendende Korrekturnachricht -- inhaltlich an
    `templates/CORRECTION_MESSAGE.txt` des Auftragspakets angelehnt (Names/
    Details sind Implementierungssache, 01_AUFTRAG_SAVEGATE.md §C). Nutzt
    AUSSCHLIESSLICH `acceptance.feedback_items` (bereits SC17-sicher: kein
    roher Traceback, auf max. `save_validation.MAX_FEEDBACK_ITEMS` begrenzt,
    nur auf diesen EINEN Block bezogen) -- keine eigene Fehlerausgabe."""
    feedback_items = acceptance.feedback_items if acceptance is not None else []
    feedback_text = "\n".join(f"- {item}" for item in feedback_items) or "- (keine strukturierten Einzelpunkte)"
    original_json = (
        json.dumps(original_block, ensure_ascii=False, indent=2) if original_block is not None else "null"
    )
    return (
        f"{_HEADER}\n"
        f"Betroffene Persona/Figur: {persona_key} (char_id={char_id}); Operation: {operation_label}. "
        f"Korrekturversuch {attempt_no}/{max_attempts}.\n"
        "Die folgende ORIGINAL-Ausgabe wurde NICHT als neuer gültiger Spielstand übernommen. Bitte "
        "gib genau den vollständigen persönlichen v7-JSON-Save dieser EINEN Figur erneut aus, als "
        "EIN fenced ```json Block.\n"
        "Ändere AUSSCHLIESSLICH die unten beanstandeten Strukturen/Felder. Identität, Name, "
        "Callsign, Fortschritt, Werte, Inventar und Geldbeträge bleiben unverändert. Keine andere "
        "Figur, keine weitere Geschichte, keine Story-/Würfel-/Belohnungsaktion. Ist die "
        "beabsichtigte Bedeutung aus dem bisherigen Verlauf nicht eindeutig, benenne die "
        "Unklarheit statt neue Fakten zu erfinden.\n"
        f"Fehler aus lokalem Validator:\n{feedback_text}\n"
        f"Unveränderter betroffener Entwurf (DATEN, nicht editieren):\n```json\n{original_json}\n```\n"
        "Erwartet: EIN vollständiger persönlicher v7-JSON-Block. Dieser Text allein ist keine "
        "Schema-/Inhaltsprüfung; die App prüft danach erneut."
    )


def build_group_correction_message(
    *, table_id: str, section_id: str, requests: list[dict], max_attempts: int = MAX_ADDITIONAL_REQUESTS,
) -> str:
    """Wie `build_correction_message`, aber für den Gruppenabschluss: EINE
    an den Leader-Kanal gesendete Nachricht, die GENAU die fehlenden/
    ungültigen Figuren (je ein eigener Block aus `requests`) nachfordert --
    bereits gültige Mitglieder werden NICHT erneut angefragt
    (01_AUFTRAG_SAVEGATE.md §B: "nur fehlende/ungültige Figur(en)
    nachfordern"). `requests`: Liste von Dicts mit `persona_key`/`char_id`/
    `acceptance`/`original_block`/`attempt_no`."""
    parts = [
        "TECHNISCHE SPEICHERKORREKTUR (GRUPPENABSCHLUSS) -- kein neuer Spielzug, keine neue Szene, "
        "keine Belohnung, kein Fortschritt für andere Figuren.",
        f"Tisch/Abschnitt: {table_id}/{section_id}. Fehlende/ungültige Personal-Saves für "
        f"{len(requests)} Figur(en) -- bitte GENAU DIESE erneut vollständig ausgeben, je ein "
        "eigener fenced ```json Block pro Figur. Bereits gültige Figuren NICHT erneut ausgeben, "
        "keine fremde Figur/Generation.",
    ]
    for item in requests:
        parts.append(build_correction_message(
            persona_key=item["persona_key"], char_id=item["char_id"],
            operation_label=f"group:{section_id}", acceptance=item["acceptance"],
            original_block=item["original_block"], attempt_no=item["attempt_no"], max_attempts=max_attempts,
        ))
    return "\n\n".join(parts)
