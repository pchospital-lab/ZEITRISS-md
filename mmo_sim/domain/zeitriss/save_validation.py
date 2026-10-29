#!/usr/bin/env python3
"""
mmo_sim/domain/zeitriss/save_validation.py — lokaler ZEITRISS-Domainvalidator
fuer den v7-Speicherstand (R12 Savegate, 01_AUFTRAG_SAVEGATE.md §A/§B).

Laedt die BEIDEN unveraenderten v7-Schemas aus der gebundenen Quelle --
`systems/gameflow/saveGame.v7.schema.json` (tolerantes Import-/Normalizer-
Schema) UND `saveGame.v7.export.schema.json` (strikter kanonischer Export)
-- und validiert JEDEN Kandidatenblock gegen BEIDE (POLICY.json
`validate_both_existing_v7_schemas`). Reine Pruef-/Klassifikationsschicht:
schreibt NIE in den Save, hebt KEINEN Betrag an, setzt KEINE lokale
Enumheuristik (z.B. campaign.mode='core' -> 'mixed') -- nur Fehlerpfade und
die dafuer notwendige Struktur/erwartete Enumwerte werden ausgegeben; die
eigentliche Korrektur bleibt SL-Sache (W44-Korrekturschleife).

Kein Netzfetch, keine still permissive Rueckfallpruefung bei fehlendem
Validator: `jsonschema`/`referencing` werden OHNE optionalen `try/except
ImportError`-Fallback importiert (anders als `core/persona_state.py`s
optionaler `jsonschema is None`-Zweig, der ausdruecklich NICHT wiederholt
wird) -- fehlt die Dependency, bricht dieses Modul beim Import hart ab.
Referenzen werden ausschliesslich aus den beiden hier registrierten lokalen
Schemaressourcen aufgeloest (`referencing.Registry` ohne `retrieve`-
Callback) -- ein nicht lokal aufloesbarer Verweis scheitert kontrolliert
(`referencing.exceptions.Unresolvable`), statt einen Netzabruf zu
versuchen. Beide Schemadateien werden zusaetzlich beim Modulimport mit
`check_schema()` gegen ihr eigenes Meta-Schema geprueft ("Schema selbst
pruefen").
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from jsonschema.validators import validator_for
from referencing import Registry, Resource

from . import saves as save_lib

#: 01_AUFTRAG_SAVEGATE.md §A / POLICY.json `max_schema_feedback_items`: Cap
#: fuer die an die SL zurueckgegebenen Feedbackpunkte. Betrifft NUR, wie
#: viele Punkte angezeigt werden -- die tatsaechliche Fehlerzahl
#: (`StructureReport.total_error_count`) wird davon unabhaengig immer
#: vollstaendig gezaehlt, und `valid` ist bereits bei EINEM Fehler `False`
#: (kein abgeschnittener Katalog wird je als vollstaendiges PASS gewertet).
MAX_FEEDBACK_ITEMS = 32

_SCHEMA_DIR = Path(__file__).resolve().parents[3] / "systems" / "gameflow"
TOLERANT_SCHEMA_PATH = _SCHEMA_DIR / "saveGame.v7.schema.json"
EXPORT_SCHEMA_PATH = _SCHEMA_DIR / "saveGame.v7.export.schema.json"


def _load_and_check_schema(path: Path) -> dict:
    """Laedt eine der beiden unveraenderten Schemadateien UND prueft das
    Schema selbst (`check_schema`, Meta-Schema-Konformitaet) -- ein
    fehlerhaftes/unerwartet veraendertes Schema bricht hier hart ab, statt
    stillschweigend als "kein Fehler" durchzugehen."""
    import json  # lokal, um den Modulkopf auf die Hart-Dependencies zu beschraenken

    raw = json.loads(path.read_text(encoding="utf-8"))
    cls = validator_for(raw)  # "richtigen Draft nach $schema wählen" -- kein hartkodiertes Draft7Validator
    cls.check_schema(raw)
    return raw


def _local_registry(schemas: list[dict]) -> Registry:
    """Registry NUR aus den hier uebergebenen lokal gebundenen Schemas --
    ohne `retrieve`-Callback bricht die Aufloesung eines nicht registrierten
    `$ref` kontrolliert ab (`referencing.exceptions.Unresolvable`), es wird
    NIE ein Netzabruf versucht."""
    resources = [(s["$id"], Resource.from_contents(s)) for s in schemas if "$id" in s]
    return Registry().with_resources(resources)


_TOLERANT_SCHEMA = _load_and_check_schema(TOLERANT_SCHEMA_PATH)
_EXPORT_SCHEMA = _load_and_check_schema(EXPORT_SCHEMA_PATH)
_REGISTRY = _local_registry([_TOLERANT_SCHEMA, _EXPORT_SCHEMA])
_TOLERANT_VALIDATOR = validator_for(_TOLERANT_SCHEMA)(_TOLERANT_SCHEMA, registry=_REGISTRY)
_EXPORT_VALIDATOR = validator_for(_EXPORT_SCHEMA)(_EXPORT_SCHEMA, registry=_REGISTRY)

_REQUIRED_PROPERTY_RE = re.compile(r"^'(.+)' is a required property$")
_EXPECTED_KEYWORDS = frozenset({
    "enum", "const", "type", "pattern", "maxLength", "minLength",
    "maxItems", "minItems", "minimum", "maximum", "additionalProperties",
})
_LENGTH_KEYWORDS = frozenset({"maxItems", "minItems", "maxLength", "minLength"})
_MAX_MESSAGE_LENGTH = 500


@dataclass(frozen=True)
class SchemaError:
    """Eine klassifizierte Strukturabweichung gegen EINES der beiden v7-
    Schemas. `path` ist der Fehlerpfad im Save-Block (z.B.
    '/economy/wallets/CHR-VASEK-A01'), `check` das Validator-Schluesselwort
    (z.B. 'type'/'enum'/'required'/'const'), `expected` -- falls sinnvoll --
    der erwartete Wert/die erwartete Enummenge/der fehlende Pflichtschluessel."""

    schema: str  # "tolerant" | "export"
    path: str
    check: str
    message: str
    expected: object = None
    actual: object = None  # bei Laengenregeln (maxItems/minItems/maxLength/minLength): tatsaechliche Laenge der Instanz


@dataclass(frozen=True)
class BindingError:
    """Figur-/Persona-/char_id-Bindungsfehler, unabhaengig von der reinen
    Schemapruefung (Schema-valide ist NICHT inhaltlich/identitaetsgleich,
    01_AUFTRAG_SAVEGATE.md §A)."""

    code: str
    message: str


@dataclass
class StructureReport:
    valid: bool
    errors: list = field(default_factory=list)  # list[SchemaError], hoechstens MAX_FEEDBACK_ITEMS
    total_error_count: int = 0
    truncated: bool = False


@dataclass
class AcceptanceResult:
    """Ergebnis des einheitlichen Annahmepunkts (01_AUFTRAG_SAVEGATE.md §B):
    `accepted` ist NUR dann wahr, wenn BEIDE Schemas UND die Figuren-/
    char_id-Bindung fehlerfrei sind -- ein milder Harvest-Check (nur
    v7/Ein-Figur/char_id) kann einen Vollschemafehler NICHT uebersteuern
    (SC01)."""

    accepted: bool
    structure: StructureReport
    binding_errors: list = field(default_factory=list)  # list[BindingError]

    @property
    def feedback_items(self) -> list:
        """Kopierbarer, NUR auf diesen EINEN Save-Block bezogener
        Fehlerkatalog (01_AUFTRAG_SAVEGATE.md §E: 'Korrekturhinweis samt
        Schemaauszug'). Enthaelt ausschliesslich Fehlerpfade/erwartete
        Werte dieses Blocks -- keine fremden Daten, kein roher Python-
        Traceback (SC17)."""
        items = [_format_schema_feedback(e) for e in self.structure.errors]
        items += [f"[binding:{e.code}] {e.message}" for e in self.binding_errors]
        return items


def _classify(error, schema_name: str) -> SchemaError:
    path = "/" + "/".join(str(p) for p in error.absolute_path)
    keyword = str(error.validator)
    expected = None
    if keyword == "required":
        m = _REQUIRED_PROPERTY_RE.match(error.message)
        expected = m.group(1) if m is not None else error.validator_value
    elif keyword in _EXPECTED_KEYWORDS:
        expected = error.validator_value
    actual = None
    if keyword in _LENGTH_KEYWORDS:
        try:
            actual = len(error.instance)
        except TypeError:
            actual = None
    message = error.message
    if len(message) > _MAX_MESSAGE_LENGTH:
        message = message[:_MAX_MESSAGE_LENGTH] + "…(gekuerzt)"
    return SchemaError(schema=schema_name, path=path or "/", check=keyword, message=message, expected=expected, actual=actual)


def _format_schema_feedback(e: SchemaError) -> str:
    """Stellt Pfad, Regel, erlaubte Grenze und tatsaechliche Laenge VOR den evtl.
    auf _MAX_MESSAGE_LENGTH gekuerzten Validator-Text, damit die entscheidende
    Regel-/Grenzangabe (z.B. 'regel=maxItems erlaubt=6 ist=7') die SL auch dann
    erreicht, wenn der rohe jsonschema-Text (grosse Instanz-Repr) abgeschnitten
    wurde. Lockert nichts: schneidet keinen Spielfakt ab, zaehlt keinen Fehler
    weg -- der vollstaendige (ggf. gekuerzte) Originaltext bleibt angehaengt."""
    facts = ["regel=" + e.check]
    if e.check == "required":
        if e.expected is not None:
            facts.append("fehlendes_pflichtfeld=" + repr(e.expected))
    elif e.expected is not None:
        facts.append("erlaubt=" + str(e.expected))
    if e.actual is not None:
        facts.append("ist=" + str(e.actual))
    return "[" + e.schema + "]" + e.path + ": " + " ".join(facts) + " -- " + e.message


def validate_structure(block: dict) -> StructureReport:
    """Validiert `block` gegen BEIDE unveraenderten v7-Schemas. Liefert bis
    zu `MAX_FEEDBACK_ITEMS` klassifizierte Fehler; `total_error_count`
    zaehlt IMMER alle tatsaechlich gefundenen Fehler, auch jenseits des
    Caps -- ein abgeschnittener Katalog wird NIE als vollstaendiges PASS
    gewertet, `valid` ist bereits bei EINEM gefundenen Fehler `False`,
    unabhaengig vom Cap."""
    if not isinstance(block, dict):
        error = SchemaError(
            schema="structure", path="/", check="type",
            message="Save-Block ist kein JSON-Objekt.", expected="object",
        )
        return StructureReport(valid=False, errors=[error], total_error_count=1, truncated=False)

    all_errors: list[SchemaError] = []
    for name, validator in (("tolerant", _TOLERANT_VALIDATOR), ("export", _EXPORT_VALIDATOR)):
        for error in validator.iter_errors(block):
            all_errors.append(_classify(error, name))

    total = len(all_errors)
    return StructureReport(
        valid=(total == 0),
        errors=all_errors[:MAX_FEEDBACK_ITEMS],
        total_error_count=total,
        truncated=total > MAX_FEEDBACK_ITEMS,
    )


def validate_binding(block: dict, expected_chrononaut_id: str) -> list:
    """Exakt-1-Figur/Persona/char_id-Bindung (zusaetzlich zur reinen
    Schemapruefung). Prueft NUR Struktur/Zuordnung, AENDERT NICHTS am
    Block, setzt KEINE Heuristik/Dedupe."""
    errors: list[BindingError] = []
    if block.get("v") != 7:
        errors.append(BindingError("wrong_version", f"Save-Block hat v={block.get('v')!r}, erwartet 7."))
    n = save_lib.single_character_count(block)
    if n != 1:
        errors.append(BindingError(
            "not_single_character",
            f"Save-Block enthaelt {n} Figuren in 'characters', erwartet genau 1 "
            "(Sammel-/Host-Save oder leerer Block statt Personal-Save).",
        ))
    cid = save_lib.block_char_id(block)
    if cid is None:
        errors.append(BindingError("missing_char_id", "Kein auswertbarer char_id/id im Save-Block."))
    elif cid != expected_chrononaut_id:
        errors.append(BindingError(
            "char_id_mismatch",
            f"Save-Block gehoert zu char_id={cid!r}, erwartet {expected_chrononaut_id!r} -- "
            "fremde Figur/Generation wird NICHT uebernommen.",
        ))
    return errors


def validate_save_block(block: dict | None, expected_chrononaut_id: str) -> AcceptanceResult:
    """Einheitlicher Annahmepunkt-Kern (01_AUFTRAG_SAVEGATE.md §B). Liefert
    IMMER einen vollstaendigen `AcceptanceResult`, auch bei `block is None`
    (dann `accepted=False`, Bindungsfehler 'missing_block', leere
    Strukturpruefung -- es gibt nichts zu schemavalidieren)."""
    if block is None:
        structure = StructureReport(valid=False, errors=[], total_error_count=0, truncated=False)
        binding = [BindingError("missing_block", "Kein Save-Block vorhanden.")]
        return AcceptanceResult(accepted=False, structure=structure, binding_errors=binding)
    structure = validate_structure(block)
    binding = validate_binding(block, expected_chrononaut_id)
    return AcceptanceResult(accepted=(structure.valid and not binding), structure=structure, binding_errors=binding)


def find_duplicate_save_ids(blocks: list) -> list:
    """Erkennt konkurrierende Doppelbloecke gleicher save_id/char_id in
    EINER Liste frisch extrahierter Bloecke (z.B. aus einem einzelnen
    SL-Text) -- liefert je echtem Konflikt (gleiche ID, ABWEICHENDER
    Inhalt) einen `BindingError`. Versteckt NICHTS durch 'erster
    gewinnt'/Dedupe (01_AUFTRAG_SAVEGATE.md §A) -- reine Erkennung, keine
    Auswahl/Entscheidung (die bleibt der Korrekturschleife, W44,
    vorbehalten)."""
    errors: list[BindingError] = []
    by_save_id: dict[str, list] = {}
    by_char_id: dict[str, list] = {}
    for blk in blocks:
        if not isinstance(blk, dict):
            continue
        sid = blk.get("save_id")
        if sid:
            by_save_id.setdefault(str(sid), []).append(blk)
        cid = save_lib.block_char_id(blk)
        if cid:
            by_char_id.setdefault(str(cid), []).append(blk)
    for sid, group in by_save_id.items():
        if len(group) > 1 and any(g != group[0] for g in group[1:]):
            errors.append(BindingError(
                "duplicate_save_id_conflict",
                f"save_id={sid!r} erscheint {len(group)}x mit ABWEICHENDEM Inhalt in derselben "
                "Antwort -- keine automatische Auswahl (kein 'erster gewinnt').",
            ))
    for cid, group in by_char_id.items():
        if len(group) > 1 and any(g != group[0] for g in group[1:]):
            errors.append(BindingError(
                "duplicate_char_id_conflict",
                f"char_id={cid!r} erscheint {len(group)}x mit ABWEICHENDEM Inhalt in derselben "
                "Antwort -- keine automatische Auswahl (kein 'erster gewinnt').",
            ))
    return errors


def extract_checked_single(text: str, expected_chrononaut_id: str) -> tuple[dict | None, list]:
    """G02/SC06 (01_AUFTRAG_SAVEGATE.md §A): strikter Annahmepfad fuer GENAU
    EINE erwartete Figur -- sieht ALLE rohen, noch UNDEDUPLIZIERTEN
    Kandidaten fuer `expected_chrononaut_id` in `text`
    (`save_lib.extract_all_saves_raw`, VOR jedem 'erster gewinnt'), bevor
    irgendeine Auswahl getroffen wird. `find_duplicate_save_ids` wird dabei
    REAL auf diese Rohkandidaten angewendet (nicht nur im Test aufgerufen).

    Liefert `(None, konflikte)`, wenn mindestens zwei rohe Bloecke fuer
    `expected_chrononaut_id` mit ABWEICHENDEM Inhalt vorliegen -- der
    Aufrufer darf dann KEINEN der beteiligten Bloecke uebernehmen (SC06:
    'darf NIE als einer der Bloecke erfolgreich uebernommen werden').
    Identische Wiederholungen (gleicher Inhalt mehrfach) sind KEIN Konflikt
    -- deterministisch der erste Treffer, `(block, [])`. Kein Treffer fuer
    `expected_chrononaut_id` -> `(None, [])` (nichts zu uebernehmen, aber
    auch kein Konflikt). Andere Figuren/char_ids im selben Text bleiben
    unberuehrt (Gruppen-Personen getrennt -- jede char_id wird fuer sich
    geprueft, s. Aufrufer in `core/save_correction.pursue_group_save_
    correction` fuer den analogen Mehrpersonenfall)."""
    matching = [
        blk for blk in save_lib.extract_all_saves_raw(text)
        if save_lib.block_char_id(blk) == expected_chrononaut_id
    ]
    if not matching:
        return None, []
    conflicts = find_duplicate_save_ids(matching)
    if conflicts:
        return None, conflicts
    return matching[0], []
