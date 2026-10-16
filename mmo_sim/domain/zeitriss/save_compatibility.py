#!/usr/bin/env python3
"""
mmo_sim/domain/zeitriss/save_compatibility.py — ZEITRISS-Domänenwissen für
den Save-/Load-Komfortvertrag (ZR-SAVECOMPAT-TERMINAL-20261016-R1,
02_SAVEVERTRAG.md §B/§C/§D).

Reine Domänenschicht (kein I/O, kein Modellaufruf, keine Zustandspersistenz
-- das bleibt `core/save_compatibility.py` vorbehalten, exakt dieselbe
Schichtentrennung wie `save_correction.py`/`core/save_correction.py`):

  1. Wertgleiche Wallet-Normalisierung (02.B): ein bekannter numerischer
     Walletbetrag wird wertgleich in `{"balance": N}` gewrappt; eine
     ZEITRISS-eigene `currency: "CU"`-Zusatzangabe wird aus dem
     GESCHLOSSENEN kanonischen Exportwallet entfernt, aber NIE verworfen
     -- sie bleibt in der separat zurückgegebenen Originalsicht
     (`retained_original`) UND als Annotation erhalten. KEINE arbiträren
     Fremdfelder werden gelöscht (nur die eine bekannte, source-gebundene
     "CU"-Ausnahme) und KEINE Fremdwährung wird konvertiert.
  2. Kompatibilitätsumschlag (02.D): ein versionierter, NICHT-kanonischer
     Behälter für Rohantworten/beste Sicht/letzten validen Stand/
     Fortschrittsbelege/Konflikte/Fehler/Herkunft -- strikt vom v7-
     Saveformat getrennt (02.F: "der neue Kompatibilitätsumschlag ist ein
     getrennter Vertrag", v7-Schemas bleiben UNVERÄNDERT).
  3. Deterministische Kandidatenauswahl + konfliktfreie Ergänzung (02.C):
     bevorzugt einen vollständig gültigen GANZEN Kandidaten; ergänzt NUR
     Eigenschaften, die im gewählten Kandidaten fehlen UND in genau einer
     Zusatzquelle eindeutig vorliegen -- kein `dict.update`, keine
     Maximalwert-Auswahl, keine Item-Duplikation, kein Vermischen
     verschiedener Figuren/Branches.
"""
from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field
from typing import Any, Callable

from . import save_validation as save_validation_lib

# ─────────────────────────── A: Wallet-Projektion ───────────────────────────

#: 02.B: Die ZEITRISS-eigene, source-gebundene Einheit -- NIE eine andere
#: Währungsangabe wird hier geraten/konvertiert (GENERALREVIEW.md Punkt 4:
#: "CU is the source-bound ZEITRISS unit, not a foreign-exchange guess").
_NATIVE_CURRENCY = "CU"


def _finite_number(value: Any) -> bool:
    """Bool ist in Python ein `int`-Subtyp -- `True`/`False` sind KEIN
    Geldbetrag (01_AUFTRAG_SAVEGATE.md-Muster, s. `qa/test_verifier.py`
    `bool_not_money`)."""
    if isinstance(value, bool):
        return False
    return isinstance(value, int) or (isinstance(value, float) and math.isfinite(value))


def _pointer(value: str) -> str:
    """RFC6901-JSON-Pointer-Escaping für einen einzelnen Segmentnamen
    (char_id kann theoretisch '/'/'~' enthalten) -- NUR für die
    Annotation-`path`-Anzeige, keine echte Pointer-Auflösung."""
    return value.replace("~", "~0").replace("/", "~1")


@dataclass(frozen=True)
class WalletProjection:
    """Ergebnis der Wallet-Projektion EINES ganzen Save-Blocks.
    `canonical_candidate` enthält AUSSCHLIESSLICH wertgleiche Wrap-/
    Entfernungsänderungen gegenüber dem Original (sonst identisch);
    `retained_original` ist der unveränderte Eingabeblock (verlustfrei,
    für die Rettungs-/Kompatibilitätssicht); `annotations` dokumentiert
    JEDE vorgenommene Änderung mit Pfad+Regel+Vorher/Nachher."""

    canonical_candidate: dict
    retained_original: dict
    annotations: tuple[dict, ...]
    changed: bool


#: Namen der beiden sanktionierten Regeln -- s. `project_wallets_in_block`-
#: Docstring. `RULE_CU_RETAINED_ONLY` wird vom Produktweg (`core/
#: save_correction.py`s laufendem Korrekturzyklus) verwendet: dort ist der
#: wertgleiche Zahl->balance-Wrap BEREITS seit laengerem durch die
#: bestehende, unveraenderte `detect_unjustified_drift`/`_is_allowed_
#: amount_wrap`-Ausnahme abgedeckt (der tatsaechlich reparierte p01-Fehler,
#: GENERALREVIEW.md, betraf AUSSCHLIESSLICH das zusaetzliche CU-Feld).
#: Zahlreiche bestehende Regressionstests nutzen einen DURCHGAENGIG
#: bloss-zahligen Wallet-Fixturewert gezielt als 'die SL liefert NIE eine
#: gueltige Korrektur'-Fixture fuer Budget-Erschoepfungs-/HOLD-Pfade, die
#: mit nichts Wallet-Spezifischem zu tun haben -- eine automatische
#: Zahl-Wrap-Projektion GENAU in diesem laufenden Korrekturzyklus wuerde
#: deren Fixture canceln (empirisch belegt: ein frueherer, breiterer
#: Entwurf dieses Fixes liess 24 vorher gruene Testdateien fehlschlagen).
#: `RULE_NUMBER_TO_BALANCE` bleibt fuer den EIGENSTAENDIGEN Annahmepunkt
#: (`evaluate_with_wallet_projection`, z.B. fuer den Kompatibilitäts-
#: Ladeweg/Tests/Seed-Paritaet) weiterhin verfuegbar -- NUR der laufende
#: Korrekturzyklus bindet sich auf die engere `RULE_CU_RETAINED_ONLY`-Teilmenge.
RULE_NUMBER_TO_BALANCE = "number_to_balance_same_value"
RULE_CU_RETAINED_ONLY = "CU_retained_outside_closed_canonical_wallet"
ALL_WALLET_RULES = frozenset({RULE_NUMBER_TO_BALANCE, RULE_CU_RETAINED_ONLY})
CU_ONLY_RULES = frozenset({RULE_CU_RETAINED_ONLY})


def project_wallets_in_block(block: dict, *, rules: frozenset[str] = ALL_WALLET_RULES) -> WalletProjection:
    """Wertgleiche Normalisierung ALLER `economy.wallets.*`-Einträge in
    `block` (02.B). Reine Funktion (deepcopy, kein Aliasing mit dem
    Aufrufer-Objekt). Zwei sanktionierte Regeln, NICHTS sonst:

      a) ein nackter endlicher Zahlenwert N -> `{"balance": N}` (derselbe
         Betrag, nur strukturell gewrappt).
      b) ein bereits objektförmiges Wallet mit GENAU `currency == "CU"`
         und endlichem `balance` -> `currency` wird entfernt (der Betrag
         bleibt unverändert); jedes andere Feld (auch unbekannte) bleibt
         unangetastet.

    Jede andere Form (Fremdwährung, fehlendes `balance`, unbekannte
    zusätzliche Struktur ohne `currency=="CU"`) bleibt UNVERÄNDERT -- kein
    arbiträres Löschen, um einen Validator künstlich grün zu machen
    (02.B: "Keine arbitrary Zusatzfelder löschen"). Idempotent: ein
    bereits kanonischer Block liefert `changed=False` und identische
    Bytes."""
    if not isinstance(block, dict):
        raise TypeError("Save-Block muss ein JSON-Objekt sein.")
    original = copy.deepcopy(block)
    candidate = copy.deepcopy(block)
    annotations: list[dict] = []

    economy = candidate.get("economy")
    wallets = economy.get("wallets") if isinstance(economy, dict) else None
    if isinstance(wallets, dict):
        for char_id, wallet in list(wallets.items()):
            if not isinstance(char_id, str):
                continue  # kein wohlgeformter Schlüssel -- Schema-/Bindungsprüfung behandelt das regulär.
            path = "/economy/wallets/" + _pointer(char_id)
            if RULE_NUMBER_TO_BALANCE in rules and _finite_number(wallet):
                wallets[char_id] = {"balance": wallet}
                annotations.append({
                    "path": path, "rule": RULE_NUMBER_TO_BALANCE,
                    "before": copy.deepcopy(wallet), "after": copy.deepcopy(wallets[char_id]),
                })
            elif (
                RULE_CU_RETAINED_ONLY in rules
                and isinstance(wallet, dict)
                and wallet.get("currency") == _NATIVE_CURRENCY
                and _finite_number(wallet.get("balance"))
                and "currency" in wallet
            ):
                retained_value = wallet["currency"]
                del wallets[char_id]["currency"]
                annotations.append({
                    "path": path + "/currency", "rule": RULE_CU_RETAINED_ONLY,
                    "retained_value": retained_value,
                })
    return WalletProjection(
        canonical_candidate=candidate, retained_original=original,
        annotations=tuple(annotations), changed=bool(annotations) and candidate != original,
    )


@dataclass
class WalletProjectionOutcome:
    """Ergebnis des Annahmepunkts MIT Projektionsfallback (für
    `core/save_correction.py`, s. Moduldocstring dort). `accepted` ist NUR
    wahr, wenn entweder der Rohblock selbst ODER seine wertgleiche
    Projektion BEIDE v7-Schemas + Bindung erfüllt. `used_projection`
    unterscheidet die beiden Fälle -- der Aufrufer muss bei `True`
    `canonical_block` (NICHT den rohen Eingabeblock) als Inhalt der
    angenommenen Fassung übernehmen, `retained_original` bleibt die
    unveränderte Rohfassung für die Rettungssicht."""

    accepted: bool
    acceptance: save_validation_lib.AcceptanceResult
    canonical_block: dict | None
    retained_original: dict | None
    annotations: tuple[dict, ...]
    used_projection: bool


def evaluate_with_wallet_projection(
    block: dict | None, expected_chrononaut_id: str, *, rules: frozenset[str] = ALL_WALLET_RULES,
) -> WalletProjectionOutcome:
    """Einheitlicher Annahmepunkt MIT 02.B-Vorstufe: prüft `block` zuerst
    UNVERÄNDERT (`save_validation.validate_save_block`); nur wenn das
    scheitert UND die reine Wallet-Projektion (s.o.) eine schema-/
    bindungsgültige kanonische Fassung liefert, wird DIESE als akzeptiert
    gemeldet. Die Projektion ist durch Konstruktion wertgleich (nur die
    oben genannten Wrap-/Entfernungsregeln, s. `rules`) -- keine
    zusätzliche Drift-Prüfung gegen eine ältere Baseline nötig, DIESE
    Funktion vergleicht nur `block` gegen seine EIGENE Projektion, nicht
    gegen einen Vorgängerstand (das bleibt Aufgabe des Aufrufers für
    echten Mehrrunden-Vergleich, s. `core/save_correction.py`).
    `rules` (Default: beide Regeln) grenzt ein, WELCHE Projektionsregeln
    angewendet werden -- `evaluate_with_cu_retention_projection` unten
    bindet sich bewusst auf die engere Teilmenge für den laufenden
    Produktkorrekturzyklus."""
    if block is None:
        structure = save_validation_lib.StructureReport(valid=False, errors=[], total_error_count=0, truncated=False)
        binding = [save_validation_lib.BindingError("missing_block", "Kein Save-Block vorhanden.")]
        acceptance = save_validation_lib.AcceptanceResult(accepted=False, structure=structure, binding_errors=binding)
        return WalletProjectionOutcome(
            accepted=False, acceptance=acceptance, canonical_block=None, retained_original=None,
            annotations=(), used_projection=False,
        )
    direct = save_validation_lib.validate_save_block(block, expected_chrononaut_id)
    if direct.accepted:
        return WalletProjectionOutcome(
            accepted=True, acceptance=direct, canonical_block=block, retained_original=block,
            annotations=(), used_projection=False,
        )
    try:
        projection = project_wallets_in_block(block, rules=rules)
    except TypeError:
        return WalletProjectionOutcome(
            accepted=False, acceptance=direct, canonical_block=None, retained_original=None,
            annotations=(), used_projection=False,
        )
    if not projection.changed:
        return WalletProjectionOutcome(
            accepted=False, acceptance=direct, canonical_block=None, retained_original=None,
            annotations=(), used_projection=False,
        )
    projected_acceptance = save_validation_lib.validate_save_block(
        projection.canonical_candidate, expected_chrononaut_id,
    )
    if not projected_acceptance.accepted:
        # Projektion hat nicht geholfen (anderer/zusätzlicher Fehler) --
        # der reguläre Korrekturpfad bleibt unverändert zuständig.
        return WalletProjectionOutcome(
            accepted=False, acceptance=direct, canonical_block=None, retained_original=None,
            annotations=(), used_projection=False,
        )
    return WalletProjectionOutcome(
        accepted=True, acceptance=projected_acceptance, canonical_block=projection.canonical_candidate,
        retained_original=projection.retained_original, annotations=projection.annotations, used_projection=True,
    )


def evaluate_with_cu_retention_projection(block: dict | None, expected_chrononaut_id: str) -> WalletProjectionOutcome:
    """Enger Produktweg-Annahmepunkt: wendet NUR `RULE_CU_RETAINED_ONLY`
    an (kein Zahl->balance-Wrap). `core/save_correction.py`s laufender
    Korrekturzyklus verwendet AUSSCHLIESSLICH diese Funktion -- s.
    Konstantenblock oben für die Begründung (Testfixture-Kollision mit dem
    breiteren `evaluate_with_wallet_projection`)."""
    return evaluate_with_wallet_projection(block, expected_chrononaut_id, rules=CU_ONLY_RULES)


# ───────────────────── B: Kompatibilitätsumschlag (02.D) ────────────────────

COMPAT_ENVELOPE_SCHEMA = "zeitriss-savecompat-envelope/1"

#: Pflichtschlüssel eines Kompatibilitätsumschlags -- 02.D: "Rohantworten,
#: beste verwertbare Sicht, letzten validen Stand (falls vorhanden),
#: verifizierte Fortschrittsbelege, alle Konflikte/Extensions, Fehler und
#: Herkunft". Bewusst EIGENES, flaches Schema -- KEIN v7-Feldname wird
#: hier wiederverwendet (02.F: "getrennter Vertrag").
_ENVELOPE_REQUIRED_KEYS = frozenset({
    "schema", "envelope_version", "repair_key", "char_id", "participant_id", "operation_key",
    "table_id", "section_id", "raw_responses", "best_view", "last_valid", "progress_evidence",
    "conflicts", "extensions", "errors", "provenance", "created_ts", "canonical_import_eligible",
})


def build_compat_envelope(
    *,
    envelope_version: int,
    repair_key: str,
    char_id: str,
    participant_id: str,
    operation_key: str,
    table_id: str | None,
    section_id: str | None,
    raw_responses: list[dict],
    best_view: dict | None,
    last_valid: dict | None,
    progress_evidence: list[dict] | None = None,
    conflicts: list[dict] | None = None,
    extensions: dict | None = None,
    errors: list[str] | None = None,
    provenance: dict | None = None,
    created_ts: float,
) -> dict:
    """Baut EINEN Kompatibilitätsumschlag -- reine Funktion, kein I/O
    (`core/save_compatibility.py` übernimmt Versionierung/Ablage).
    `canonical_import_eligible` ist IMMER `False` -- 02.D: "Das ist NICHT
    automatisch ein kanonisch valider v7-Save und darf nicht als solcher
    in SaveStatistiken, Exports oder completed-Flags gezählt werden." Das
    Feld macht diese Regel für JEDEN Leser (auch künftigen Code) explizit
    statt implizit aus der Abwesenheit eines v7-Feldes herzuleiten."""
    return {
        "schema": COMPAT_ENVELOPE_SCHEMA,
        "envelope_version": envelope_version,
        "repair_key": repair_key,
        "char_id": char_id,
        "participant_id": participant_id,
        "operation_key": operation_key,
        "table_id": table_id,
        "section_id": section_id,
        "raw_responses": list(raw_responses),
        "best_view": copy.deepcopy(best_view) if best_view is not None else None,
        "last_valid": copy.deepcopy(last_valid) if last_valid is not None else None,
        "progress_evidence": list(progress_evidence or []),
        "conflicts": list(conflicts or []),
        "extensions": dict(extensions or {}),
        "errors": list(errors or []),
        "provenance": dict(provenance or {}),
        "created_ts": created_ts,
        "canonical_import_eligible": False,
    }


def validate_compat_envelope(envelope: Any) -> list[str]:
    """Strukturprüfung EINES Kompatibilitätsumschlags -- KEIN v7-Schema
    (02.F: getrennter Vertrag). Liefert eine Liste menschenlesbarer
    Fehler; leere Liste == strukturell gültig. Reine Formprüfung, prüft
    NICHT den Inhalt von `best_view`/`last_valid` gegen v7 (das bleibt
    Aufgabe des Compat-Ladewegs, der sie VOR jeder Übernahme erneut durch
    `save_validation` schickt)."""
    errors: list[str] = []
    if not isinstance(envelope, dict):
        return ["envelope ist kein JSON-Objekt."]
    missing = _ENVELOPE_REQUIRED_KEYS - set(envelope)
    if missing:
        errors.append(f"fehlende Pflichtschlüssel: {sorted(missing)}")
    if envelope.get("schema") != COMPAT_ENVELOPE_SCHEMA:
        errors.append(f"unerwartetes schema={envelope.get('schema')!r}, erwartet {COMPAT_ENVELOPE_SCHEMA!r}.")
    if envelope.get("canonical_import_eligible") is not False:
        errors.append("canonical_import_eligible muss immer False sein (02.D: kein kanonisch valider v7-Save).")
    if not isinstance(envelope.get("raw_responses"), list):
        errors.append("raw_responses muss eine Liste sein.")
    if not isinstance(envelope.get("conflicts"), list):
        errors.append("conflicts muss eine Liste sein.")
    if not isinstance(envelope.get("errors"), list):
        errors.append("errors muss eine Liste sein.")
    best_view, last_valid = envelope.get("best_view"), envelope.get("last_valid")
    if best_view is None and last_valid is None:
        errors.append("weder best_view noch last_valid vorhanden -- nichts Verwertbares im Umschlag.")
    return errors


def is_compat_envelope(block: Any) -> bool:
    """Schnelle Unterscheidung Kompatibilitätsumschlag vs. kanonischer
    v7-Save -- der Compat-Ladeweg (`core/save_compatibility.py`) muss
    VOR jeder Behandlung wissen, mit welcher Form er es zu tun hat, ohne
    jedes Mal die volle Strukturprüfung zu bemühen."""
    return isinstance(block, dict) and block.get("schema") == COMPAT_ENVELOPE_SCHEMA


# ──────────────── C: Kandidatenauswahl + konfliktfreie Ergänzung (02.C) ────


@dataclass(frozen=True)
class SelectionResult:
    """`selected` ist `None`, wenn KEIN Kandidat (auch nicht nach eigener
    Wallet-Projektion) vollständig schema-/bindungsgültig ist --
    `reason` benennt dann den letzten geprüften Fehlerkatalog bzw.
    'no_candidates'. Bei Erfolg trägt `source_tag` die vom Aufrufer
    übergebene Herkunftskennung (z.B. Requestid/Attemptno) GENAU DES
    gewählten Kandidaten -- NIE eine aus mehreren Quellen gemischte
    Kennung."""

    selected: dict | None
    source_tag: str | None
    used_projection: bool
    reason: str


def select_candidate(
    candidates: list[tuple[str, dict]], expected_chrononaut_id: str,
) -> SelectionResult:
    """02.C: "Deterministische Auswahl bevorzugt einen vollständig
    gültigen, identitäts- und inhaltstreuen GANZEN Kandidaten." Prüft
    `candidates` (Liste von `(source_tag, block)`, Reihenfolge = vom
    Aufrufer bereits priorisiert, z.B. neueste/vollständigste zuerst) IN
    GENAU DIESER REIHENFOLGE und liefert den ERSTEN, der (direkt ODER
    über die wertgleiche Wallet-Projektion, 02.B) vollständig gültig ist.
    KEINE Kombination mehrerer Kandidaten, KEIN Ranking nach Länge/
    Vollständigkeits-Heuristik -- reine deterministische Reihenfolgewahl
    EINES GANZEN Blocks (kein Vermischen verschiedener Branches/Figuren)."""
    last_reason = "no_candidates"
    for source_tag, block in candidates:
        outcome = evaluate_with_wallet_projection(block, expected_chrononaut_id)
        if outcome.accepted:
            return SelectionResult(
                selected=outcome.canonical_block, source_tag=source_tag,
                used_projection=outcome.used_projection, reason="selected",
            )
        last_reason = f"rejected:{source_tag}:{';'.join(outcome.acceptance.feedback_items) or 'unknown'}"
    return SelectionResult(selected=None, source_tag=None, used_projection=False, reason=last_reason)


def _flatten(obj: Any, prefix: str = "") -> list[tuple[str, Any]]:
    """R12-SAVECOMPAT-BUGFIX (gefunden beim Schreiben von
    `test_savecompat_conflict_no_silent_merge.py`): rekurriert NUR in
    `dict`-Knoten. Eine fruehere Fassung rekurrierte ZUSAETZLICH in Listen
    (Index als Pfadsegment) -- dadurch flachte ein Listenwert in mehrere
    EINZELNE `/.../<idx>`-Pfade auf, UND `_set_at_path` baute beim
    Zusammenfuehren eines solchen Index-Pfads den Zielknoten als neuen
    `dict` mit String-Schluesseln auf (`isinstance(nxt, dict)`-Zweig dort),
    was sowohl einen bereits in `primary` vorhandenen Listenwert BEIM
    MERGE STILL IN EIN DICT UMWANDELTE (Verstoss gegen 'ein in primary
    bereits vorhandener Pfad wird NIE ueberschrieben') als auch einen neu
    uebernommenen Listenwert elementweise in ein Dict statt den
    dokumentierten 'GANZEN Wert' zerlegte (Verstoss gegen 02.C: 'Listen
    werden NIE elementweise gemischt'). Eine Liste zaehlt hier -- wie
    jeder andere nicht-dict-Wert -- als EIN Blattwert auf ihrem eigenen
    Pfad."""
    out: list[tuple[str, Any]] = []
    if isinstance(obj, dict):
        for key in obj:
            out.extend(_flatten(obj[key], f"{prefix}/{key}"))
    else:
        out.append((prefix or "/", obj))
    return out


@dataclass(frozen=True)
class MergeConflict:
    path: str
    values_by_source: tuple[tuple[str, Any], ...]


@dataclass(frozen=True)
class MergeResult:
    """`merged` beginnt als exakte Kopie von `primary` -- NIEMALS wird ein
    in `primary` bereits vorhandener Pfad überschrieben (kein
    `dict.update`-Politik, 02.C). `provenance` trägt für JEDEN tatsächlich
    AUS EINER Zusatzquelle übernommenen neuen Pfad deren `source_tag`.
    `conflicts` listet jeden Pfad, der in `primary` fehlt UND in
    mindestens zwei Zusatzquellen MIT abweichendem Wert vorliegt -- dieser
    Pfad wird NICHT übernommen, bleibt im zurückgegebenen `merged` also
    abwesend (Aufrufer entscheidet, ob/wie das weiter behandelt wird)."""

    merged: dict
    provenance: dict[str, str]
    conflicts: tuple[MergeConflict, ...]


def merge_conflict_free(primary: dict, primary_tag: str, supplements: list[tuple[str, dict]]) -> MergeResult:
    """02.C: "Nur konfliktfreie Ergänzungen aus Antworten DERSELBEN
    Speicheroperation derselben Figur zusammenführen, jede übernommene
    Eigenschaft auf Quellkandidat/-pfad zurückführen." `primary` ist der
    bereits ausgewählte (s. `select_candidate`) Hauptkandidat;
    `supplements`: Liste `(source_tag, block)` weiterer Antworten
    DERSELBEN Operation/Figur (vom Aufrufer so eingegrenzt -- diese
    Funktion kennt keine Operations-/Figurbindung selbst).

    Regeln, bewusst eng (keine Heuristik):
      - EIN Pfad wird NUR übernommen, wenn er in `primary` GAR NICHT
        existiert (kein Überschreiben vorhandener Werte, keine
        Maximalwert-Auswahl zwischen primary und Zusatzquelle).
      - Liegt derselbe fehlende Pfad in MEHREREN Zusatzquellen MIT
        ABWEICHENDEM Wert vor, ist das ein Konflikt -- NICHT übernommen,
        in `conflicts` gelistet (kein 'erster gewinnt').
      - Liegt er in mehreren Zusatzquellen mit IDENTISCHEM Wert vor, ist
        das kein Konflikt -- übernommen, `provenance` trägt die erste
        liefernde Quelle.
      - Listen werden NIE konkateniert/dedupliziert (keine Item-
        Duplikation) -- ein Listenpfad wird wie jeder andere fehlende
        Pfad als GANZER Wert übernommen oder eben nicht, nie elementweise
        gemischt."""
    merged = copy.deepcopy(primary)
    primary_paths = {p for p, _ in _flatten(merged)}
    by_path: dict[str, list[tuple[str, Any]]] = {}
    for source_tag, block in supplements:
        for path, value in _flatten(block):
            if path in primary_paths:
                continue
            by_path.setdefault(path, []).append((source_tag, value))

    provenance: dict[str, str] = {}
    conflicts: list[MergeConflict] = []
    for path, entries in sorted(by_path.items()):
        distinct_values = []
        for _tag, value in entries:
            if value not in distinct_values:
                distinct_values.append(value)
        if len(distinct_values) > 1:
            conflicts.append(MergeConflict(path=path, values_by_source=tuple(entries)))
            continue
        source_tag, value = entries[0]
        _set_at_path(merged, path, value)
        provenance[path] = source_tag
    return MergeResult(merged=merged, provenance=provenance, conflicts=tuple(conflicts))


def _set_at_path(root: dict, path: str, value: Any) -> None:
    """Setzt `value` an einem '/'-getrennten Pfad (wie von `_flatten`
    erzeugt), legt fehlende Zwischenobjekte als `dict` an. NUR für Pfade
    verwendet, die im Ziel noch GAR NICHT existieren (s. Aufrufer) --
    überschreibt deshalb nie einen vorhandenen Zweig."""
    parts = [p for p in path.split("/") if p != ""]
    node = root
    for part in parts[:-1]:
        nxt = node.get(part) if isinstance(node, dict) else None
        if not isinstance(nxt, dict):
            nxt = {}
            node[part] = nxt
        node = nxt
    if parts:
        node[parts[-1]] = value
