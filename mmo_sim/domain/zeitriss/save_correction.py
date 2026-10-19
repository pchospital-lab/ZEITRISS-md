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
import re

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

#: F-WALLET-LOSS (ZR-N2-LIVEBUNDLE-FRESH-20261018-R1): jeder Blattpfad
#: unterhalb von `/economy/wallets/<char_id>` (der Betrag selbst ODER ein
#: Unterfeld wie `/balance`) gilt als bekannter, besonders geschuetzter
#: Geldbetrag (01_AUFTRAG_SAVEGATE.md §A: "Wallet ... duerfen bei reiner
#: Schemareparatur NICHT still umgeschrieben werden"). `[^/]+` bindet an
#: GENAU EINE Figur (kein Praefixtreffer auf eine andere char_id).
_WALLET_AMOUNT_PATH_RE = re.compile(r"^/economy/wallets/[^/]+(/.*)?$")


def _is_wallet_amount_path(path: str) -> bool:
    """F-WALLET-LOSS: True fuer jeden Pfad unter einem Figuren-Wallet.
    Wird NUR benutzt, um die generelle 'Pfad liegt in error_paths'-Ausnahme
    unten (`detect_unjustified_drift`) fuer Wallet-Pfade zu VERENGEN -- ein
    bekannter Geldbetrag, der ersatzlos verschwindet (kein wertgleicher
    Wrap/Rename nach `_is_allowed_amount_wrap`/`_is_allowed_required_key_
    rename`), bleibt Drift, AUCH wenn der Elternpfad schema-ungueltig war.
    Jede andere (nicht-monetaere) Strukturkorrektur an einem gemeldeten
    Fehlerpfad bleibt von dieser Verengung unberuehrt (01_AUFTRAG_SAVEGATE.
    md §A gilt wortgleich fuer Identitaet/Name/Callsign/Level/Attribute/
    Inventar/Fortschritt, aber diese Pruefung ist bewusst auf den hier
    konkret belegten Wallet-Fund begrenzt, kein Blanket-Umbau)."""
    return bool(_WALLET_AMOUNT_PATH_RE.match(path))


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
    identisch zu `save_validation.SchemaError.path` ('/a/b/0'). Ein LEERES
    Objekt/Array erzeugt bewusst KEINEN eigenen Blattpfad (unveraendert --
    ein globales Umstellen hierauf traf frueher ÜBERALL im Dokument
    unveraendert gebliebene leere Container, z.B. `economy:{}` in einem
    komplett neu generierten, inhaltlich unverwandten Korrekturversuch, als
    falsch-positive Drift). Die S3-Pruefung gegen ÜBERSEHENE leere
    Zusatzfelder lebt deshalb gezielt in `_sibling_keys_match` (raue
    Original-Objektschluessel am betroffenen Elternknoten, NICHT global)."""
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


def _node_at(obj: object, path: str) -> object | None:
    """Navigiert `path` (Format wie `_flatten`, z.B. '/a/b/0') im
    ROHEN (nicht geflatteten) `obj` und liefert den dort stehenden
    (Teil-)Knoten -- `None`, wenn der Pfad darin nicht existiert/navigierbar
    ist. S3-Hilfsfunktion: macht auch leere Geschwisterobjekte/-arrays
    sichtbar, die `_flatten` bewusst NICHT als eigenen Blattpfad fuehrt."""
    if path in ("", "/"):
        return obj
    node = obj
    for part in path.strip("/").split("/"):
        if isinstance(node, dict):
            if part not in node:
                return None
            node = node[part]
        elif isinstance(node, list):
            try:
                idx = int(part)
            except ValueError:
                return None
            if not (0 <= idx < len(node)):
                return None
            node = node[idx]
        else:
            return None
    return node


def _sibling_keys_match(
    original: object, corrected: object, parent: str, removed_key: str, added_key: str,
) -> bool:
    """S3-Fix (ZR-N2-STABILISIERUNG-WEITERLAUF-2026-10-17-R1): verifiziert
    am ROHEN Elternobjekt (nicht an den geflatteten Blattpfaden), dass sich
    an `parent` AUSSER dem einen Rename (`removed_key` weg, `added_key` neu)
    KEIN weiterer Schluessel geaendert hat -- INSBESONDERE kein zusaetzlicher
    leeres Objekt/Array-Zusatzfeld, das `_flatten` unsichtbar liesse (01_
    AUFTRAG.md §S3: "Leere Zusatzobjekte/-listen duerfen den Driftvertrag
    nicht passieren"). Erwartete neue Schluesselmenge = (alte Schluessel ohne
    `removed_key`) + `added_key`; jede Abweichung (fehlender Geschwister-
    schluessel, z.B. durch einen KONKURRIERENDEN zweiten Alias-Rename auf
    denselben `added_key` verbraucht, ODER ein unbegruendeter zusaetzlicher
    Schluessel jeder Art) scheitert hier."""
    old_parent = _node_at(original, parent)
    new_parent = _node_at(corrected, parent)
    if not isinstance(old_parent, dict) or not isinstance(new_parent, dict):
        return False
    expected = (set(old_parent.keys()) - {removed_key}) | {added_key}
    return set(new_parent.keys()) == expected


def _is_allowed_amount_wrap(
    old_path: str, old_value: object, new_leaves: dict[str, object], consumed_new: set[str],
    original: object, corrected: object,
) -> bool:
    """Erlaubt GENAU den wertgleichen Zahl->Objekt-Wrap an EINEM einzigen
    neuen Unterpfad (z.B. '/economy/wallets/X' (100) -> '/economy/wallets/X/
    balance' (100)) -- jede Wertänderung (100 -> 1000) oder jeder zusätzliche
    Unterschlüssel (S3: AUCH ein leeres Objekt/Array, s. `_sibling_keys_
    match`) bleibt eine abzulehnende Drift."""
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
    new_parent = _node_at(corrected, old_path)
    if not isinstance(new_parent, dict) or set(new_parent.keys()) != {key}:
        return False
    consumed_new.add(candidate)
    return True


def _is_allowed_required_key_rename(
    old_path: str, old_value: object, old_leaves: dict[str, object],
    new_leaves: dict[str, object], consumed_new: set[str], error_paths: set[str],
    original: object, corrected: object,
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
    Rename laesst `len(candidates) != 1` scheitern -- bleibt Drift).

    S3-Fix (ZR-N2-STABILISIERUNG-WEITERLAUF-2026-10-17-R1), ZWEI Luecken:
    (a) eine bereits VERBRAUCHTE neue Blattbindung (`consumed_new`) darf
    NICHT nochmal als Kandidat fuer einen ANDEREN alten Geschwister-
    schluessel gelten -- sonst mappen zwei alte Aliasse (z.B. `amount:100`
    UND `credits:100`) unabhaengig voneinander beide "eindeutig" auf
    DENSELBEN neuen `balance:100`-Schluessel (jeweils `len(candidates)==1`
    fuer sich betrachtet) und werden faelschlich BEIDE als wertgleicher
    1:1-Rename durchgelassen, obwohl die Zuordnung alt->neu nicht mehr
    eindeutig ist; (b) `candidates` beruht auf den GEFLATTETEN Blattpfaden
    -- ein zusaetzliches LEERES Geschwisterobjekt/-array (`{}`/`[]`) hat
    dort gar keinen eigenen Blattpfad und bleibt so unsichtbar. Die
    zusaetzliche rohe `_sibling_keys_match`-Pruefung unten schliesst BEIDE
    Luecken strukturell (exakter Rohschluessel-Mengenvergleich am
    tatsaechlichen Elternobjekt, nicht nur an den geflatteten Blaettern)."""
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
        if p.startswith(prefix) and "/" not in p[len(prefix):]
        and p not in old_leaves and p not in consumed_new
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
    if not _sibling_keys_match(original, corrected, parent, old_key, new_key):
        return False
    consumed_new.add(candidate)
    return True


def _wallet_amount_values_equal(old_value: object, new_value: object) -> bool:
    """N2L-A-R (F-WALLET-LOSS-RESIDUAL-SAME-LEAF-SUBSTITUTION): True fuer
    einen wertgleichen Typ-/Formwechsel am SELBEN Wallet-Blattpfad (z.B.
    `"500"` (String) -> `500` (Zahl), identischer Betrag) -- NICHT fuer
    einen echten, zahlenmaessig ANDEREN Betrag (`500` -> `300`, `"500"` ->
    `300`, `500` -> `500.01`; der Critic-Fund spricht ausdruecklich von
    'ANY DIFFERENT NUMERIC value', s. N2L-C-VERDICT.json). Beide Seiten
    werden dazu auf eine Zahl normalisiert (`bool` zaehlt bewusst NICHT als
    Zahl, ein Geldbetrag ist nie ein Wahrheitswert). Laesst sich eine der
    beiden Seiten UEBERHAUPT NICHT auf eine Zahl normalisieren (kein
    numerischer Betragsersatz im engeren Sinn des Critic-Funds), bleibt die
    bisherige allgemeine `error_paths`-Ausnahme unveraendert anwendbar --
    ein solcher Ersatzwert ist ohnehin niemals `type: number`-schema-gueltig
    und kann dadurch nie stillschweigend adoptiert werden (das Annahme-Gate
    in `core/save_correction.py` laeuft NACH dieser Pruefung); NUR ein
    tatsaechlich zahlenmaessig abweichender Betrag gilt hier als NICHT
    wertgleich (= Drift)."""
    def _to_number(value: object) -> int | float | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return None
        return None

    old_num = _to_number(old_value)
    new_num = _to_number(new_value)
    if old_num is None or new_num is None:
        return True
    return old_num == new_num


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
    bleiben Drift (s. Docstring dort).

    F-WALLET-LOSS (ZR-N2-LIVEBUNDLE-FRESH-20261018-R1): die generelle
    'Pfad liegt in error_paths' Ausnahme (unten) erlaubte bisher auch, dass
    ein bekannter Walletbetrag ERSATZLOS verschwindet (z.B. ein komplett neu
    generierter Block mit `economy={}`), SOLANGE der alte Walletpfad
    irgendeinen gemeldeten Schemafehler trug -- unabhaengig davon, ob der
    Betrag irgendwo wertgleich erhalten blieb. Fuer Pfade unter
    `/economy/wallets/<char_id>` (s. `_is_wallet_amount_path`) greift diese
    Ausnahme jetzt NICHT mehr pauschal -- nur noch die beiden oben bereits
    gepruefeten wertgleichen Ausnahmen (Wrap/Rename) duerfen einen
    Walletbetrag ueberhaupt verschwinden lassen. Jede andere Pfadkategorie
    bleibt von dieser Verengung unberuehrt.

    N2L-A-R (F-WALLET-LOSS-RESIDUAL-SAME-LEAF-SUBSTITUTION): dieselbe
    Verengung gilt jetzt auch in der ZWEITEN Schleife unten (Pfad existiert
    in BEIDEN Blaettern, mit unterschiedlichem ODER neu hinzugekommenem
    Wert) -- sonst konnte der Wallet-Blattpfad selbst der gemeldete
    Schemafehler sein (z.B. `balance:"500"` gegen `type:number`) und die
    Korrektur am selben Pfad einen ANDEREN Betrag einschmuggeln (`500 ->
    300`), OHNE dass die erste Schleife (die nur ersatzlos VERSCHWUNDENE
    Blaetter sieht) das je zu Gesicht bekommt. Ein wertgleicher Typwechsel
    am selben Wallet-Blatt (`"500" -> 500`, s. `_wallet_amount_values_equal`)
    bleibt weiterhin driftfrei; nur ein zahlenmaessig ANDERER Wert wird
    Drift."""
    if not isinstance(original, dict) or not isinstance(corrected, dict):
        return [] if original == corrected else [("/", original, corrected)]

    old_leaves = _leaves(original)
    new_leaves = _leaves(corrected)
    consumed_new: set[str] = set()
    drift: list[tuple[str, object, object]] = []

    for path, old_value in old_leaves.items():
        if path in new_leaves:
            continue  # im zweiten Durchgang behandelt (gleicher Pfad in beiden)
        if _is_allowed_amount_wrap(path, old_value, new_leaves, consumed_new, original, corrected):
            continue
        if _is_allowed_required_key_rename(
            path, old_value, old_leaves, new_leaves, consumed_new, error_paths, original, corrected,
        ):
            continue
        if path in error_paths and not _is_wallet_amount_path(path):
            continue  # Struktur wurde an genau dieser gemeldeten Stelle korrigiert (kein Geldbetrag).
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
                if not _is_wallet_amount_path(path) or _wallet_amount_values_equal(
                    old_leaves[path], new_leaves[path],
                ):
                    continue
            drift.append((path, old_leaves[path], new_leaves[path]))
        else:
            if path in error_paths and not _is_wallet_amount_path(path):
                continue
            drift.append((path, "<nicht vorhanden>", new_leaves[path]))
    return drift


def _deref(schema: dict, node: object) -> object:
    """Löst lokale (`#/...`) `$ref` im selben Schemadokument auf -- rein
    lesend, kein Netzabruf (genau wie `save_validation._local_registry`
    garantiert). Ein unauflösbarer/fremder `$ref` wird unverändert
    zurückgegeben; eine Zyklenbremse verhindert Endlosschleifen."""
    seen = 0
    while isinstance(node, dict) and isinstance(node.get("$ref"), str) and node["$ref"].startswith("#/"):
        target: object = schema
        for part in node["$ref"][2:].split("/"):
            if not isinstance(target, dict) or part not in target:
                return node
            target = target[part]
        node = target
        seen += 1
        if seen > 16:
            break
    return node


def _resolve_schema_path(schema: dict, path: str) -> dict | None:
    """Navigiert `path` (Instanzpfadformat wie `save_validation.SchemaError.
    path`, z.B. '/economy/wallets/<id>' oder '/characters/0/callsign') im
    übergebenen Schemabaum und liefert den dort geltenden Schemaknoten.
    Nur `properties`/`items`/`additionalProperties`-Navigation plus
    `$ref`-Deref -- es wird NICHTS am Schema geändert. `None`, wenn der Pfad
    im Schema nicht navigierbar ist."""
    node = _deref(schema, schema)
    for seg in [s for s in path.strip("/").split("/") if s != ""]:
        if not isinstance(node, dict):
            return None
        props = node.get("properties")
        if isinstance(props, dict) and seg in props:
            node = _deref(schema, props[seg])
        elif seg.isdigit() and isinstance(node.get("items"), dict):
            node = _deref(schema, node["items"])
        elif isinstance(node.get("additionalProperties"), dict):
            node = _deref(schema, node["additionalProperties"])
        else:
            return None
    return node if isinstance(node, dict) else None


def _schema_node_for_path(path: str) -> dict | None:
    """Liefert den Schemaknoten für `path` aus den bereits in
    `save_validation` geladenen, meta-geprüften und UNVERÄNDERTEN v7-Schemas
    (zuerst Export, dann tolerant als Rückfall). Reiner Lesezugriff auf das
    bestehende Schemaobjekt -- keine zweite Schemaquelle, kein `cu`-/Alias-
    Whitelisting, keine Lockerung des Driftwächters."""
    for schema in (save_validation_lib._EXPORT_SCHEMA, save_validation_lib._TOLERANT_SCHEMA):
        node = _resolve_schema_path(schema, path)
        if node is not None:
            return node
    return None


def _describe_expected_shape(node: dict | None) -> str | None:
    """Fasst EINEN Schemaknoten in einen knappen, schema-abgeleiteten
    deutschen Zielhinweis (Typ, Pflichtfelder + deren Typen, Verbot
    zusätzlicher Felder, enum/const). Rein beschreibend -- erfindet keine
    Felder, nennt keinen konkreten Wert über das Schema hinaus und lockert
    nichts. `None`, wenn der Knoten keine verwertbare Typ-/Strukturangabe
    trägt."""
    if not isinstance(node, dict):
        return None
    if "const" in node:
        return f"fester Wert {json.dumps(node['const'], ensure_ascii=False)}"
    if isinstance(node.get("enum"), list) and node["enum"]:
        allowed = ", ".join(json.dumps(v, ensure_ascii=False) for v in node["enum"])
        return f"einer der erlaubten Werte: {allowed}"
    typ = node.get("type")
    if typ == "object":
        required = node.get("required") or []
        props = node.get("properties") or {}
        fields = []
        for key in required:
            sub = props.get(key) if isinstance(props, dict) else None
            sub_t = sub.get("type") if isinstance(sub, dict) else None
            fields.append(f"`{key}`" + (f" ({sub_t})" if isinstance(sub_t, str) else ""))
        parts = ["Objekt"]
        if fields:
            parts.append("mit Pflichtfeld(ern) " + ", ".join(fields))
        if node.get("additionalProperties") is False:
            parts.append("ohne zusätzliche Felder")
        return " ".join(parts)
    if typ == "array":
        items = node.get("items") if isinstance(node.get("items"), dict) else {}
        it = items.get("type") if isinstance(items, dict) else None
        return "Liste" + (f" von {it}-Einträgen" if isinstance(it, str) else "")
    if isinstance(typ, list):
        return "einer der Typen: " + ", ".join(str(t) for t in typ)
    if typ == "string":
        return ("Zeichenkette (ein nicht gesetzter Wert ist die leere Zeichenkette "
                "\"\", keine erfundene/neue Angabe)")
    if isinstance(typ, str):
        return {"integer": "Ganzzahl", "number": "Zahl", "boolean": "Wahrheitswert",
                "null": "null"}.get(typ, typ)
    return None


def _schema_target_hints(acceptance: save_validation_lib.AcceptanceResult | None) -> list[str]:
    """Baut je gemeldetem STRUKTUR-Fehlerpfad genau einen schema-abgeleiteten
    Zielhinweis (de-dupliziert über den Pfad, Reihenfolge erhalten). Reine
    Bindungsfehler (`binding_errors`) bekommen bewusst keinen Formhinweis --
    sie sind keine Schemaform, sondern eine Identitäts-/char_id-Frage. Nur
    tatsächlich gemeldete Pfade erscheinen; es wird nichts frei erfunden."""
    hints: list[str] = []
    seen: set[str] = set()
    errors = acceptance.structure.errors if acceptance is not None else []
    for err in errors:
        path = getattr(err, "path", None)
        if not path or path in seen:
            continue
        shape = _describe_expected_shape(_schema_node_for_path(path))
        if shape is None:
            continue
        seen.add(path)
        hints.append(f"- {path}: erwartet {shape}")
    return hints


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
    target_hints = _schema_target_hints(acceptance)
    target_text = (
        "Erwartete Zielstruktur (aus dem unveränderten v7-Exportschema abgeleitet -- genau diese "
        "gemeldeten Stellen minimal schema-gültig machen, sonst nichts):\n"
        + "\n".join(target_hints) + "\n"
        if target_hints else ""
    )
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
        "Ändere AUSSCHLIESSLICH die unten beanstandeten Strukturen/Felder und bringe sie auf genau "
        "die unten genannte schema-gültige Minimalform. Identität, Name, Fortschritt, Werte, "
        "Inventar und Geldbeträge bleiben unverändert; ein gemeldeter nicht gesetzter Callsign wird "
        "die leere Zeichenkette \"\", keine neue Identität. Keine andere Figur, keine weitere "
        "Geschichte, keine Story-/Würfel-/Belohnungsaktion. Ist die beabsichtigte Bedeutung aus dem "
        "bisherigen Verlauf nicht eindeutig, benenne die Unklarheit statt neue Fakten zu erfinden.\n"
        f"Fehler aus lokalem Validator:\n{feedback_text}\n"
        f"{target_text}"
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
